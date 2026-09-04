"""Part builders: the numbered tags, the board (lid) and the storage box.

Each colour ends up as its own solid so the multi-colour 3MF export can assign a
filament per part. Rings and walls are built as profiles-with-holes and extruded
once (see :func:`cqutil.ring`); booleans are reserved for genuine cavities
(pockets, the box well, the foot slot) and for combining separate solids.
"""

import functools

import cadquery as cq

from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

from insertkit import cqutil as U

from botc_town_stand import config as C

OUTER = U.notched_rect(C.BOARD_W, C.BOARD_H, C.BOARD_CORNER_R)
_front_y = -C.BOARD_H / 2
_front_xs = [x for x, y in OUTER if abs(y - _front_y) < 0.5]
FOOT_W = max(_front_xs) - min(_front_xs)
_foot = sbox(min(_front_xs), -C.BOARD_H / 2 - C.FOOT_EXT,
             max(_front_xs), -C.BOARD_H / 2)
BODY_FOOTPRINT = list(unary_union([Polygon(OUTER), _foot]).exterior.coords)
TAG_OUTLINE = U.notched_rect(C.TAG_W, C.TAG_H, C.TAG_CORNER_R)


def _touch_fillet(part, r):
    """Round the top-face perimeter edges for a softer grip."""
    if r <= 0:
        return part
    return part.faces(">Z").edges().fillet(r)


@functools.lru_cache(maxsize=1)
def _pocket_cutter_template():
    """Pocket void at x=0; top edge filleted to match the tag rim."""
    pts = U.offset(TAG_OUTLINE, C.POCKET_CLEAR)
    cutter = (
        cq.Workplane(cq.Plane(origin=(0, 0, C.FACE_T - C.POCKET_DEPTH)))
        .polyline(pts).close()
        .extrude(C.POCKET_DEPTH + 1)
    )
    if C.EDGE_FILLET > 0:
        cutter = cutter.faces(">Z").edges().fillet(C.EDGE_FILLET)
    return cutter.val()


def _pocket_cutter(x):
    return _pocket_cutter_template().located(cq.Location((x, 0, 0)))


@functools.lru_cache(maxsize=1)
def _notch_cutter_template():
    return (
        cq.Workplane(cq.Plane(origin=(0, C.NOTCH_Y, C.FACE_T - C.NOTCH_DEPTH)))
        .box(C.NOTCH_WX, C.NOTCH_WY, C.NOTCH_DEPTH + 1, centered=(True, True, False))
        .edges("|Z").fillet(C.NOTCH_FILLET).val()
    )


def _notch_cutter(x):
    return _notch_cutter_template().located(cq.Location((x, 0, 0)))


def seat_location():
    """Location that stands a board-local solid up in the box slot."""
    return cq.Location((0, C.SEAT_TY, C.SEAT_TZ), (1, 0, 0), C.SEAT_ALPHA)


@functools.lru_cache(maxsize=None)
def _tag_body():
    body = (U.extrude(TAG_OUTLINE, C.TAG_T)
            .faces(">Z").workplane()
            .pushPoints([(0, C.HOLE_Y)]).hole(C.HOLE_D))
    return _touch_fillet(body, C.EDGE_FILLET)


@functools.lru_cache(maxsize=None)
def _tag_ring():
    ring_o = U.offset(TAG_OUTLINE, -C.RING_GAP)
    ring_i = U.offset(TAG_OUTLINE, -(C.RING_GAP + C.RING_W))
    ring = U.ring(ring_o, ring_i, C.RING_RELIEF, z=C.TAG_T)
    hole_clear = (cq.Workplane(cq.Plane(origin=(0, C.HOLE_Y, C.TAG_T - 0.5)))
                  .cylinder(C.RING_RELIEF + 2, C.HOLE_D / 2 + 1.2,
                            centered=(True, True, False)))
    ring = ring.cut(hole_clear)
    return _touch_fillet(ring, C.RING_TOP_FILLET)


@functools.lru_cache(maxsize=None)
def make_tag(num):
    """Return ``(black_body, colour_part)`` for a numbered tag."""
    numeral = U.text_solid(num, C.NUM_SIZE, C.NUM_RELIEF, C.font_path(),
                           origin=(0, C.NUM_Y, C.TAG_T))
    colour = _tag_ring().union(cq.Workplane("XY").add(numeral))
    return _tag_body(), colour


def make_board():
    """Return ``{"body": black_solid, "frame": lavender_solid}``."""
    body = _touch_fillet(U.extrude(OUTER, C.FACE_T), C.EDGE_FILLET)
    foot = (cq.Workplane(cq.Plane(origin=(0, -C.BOARD_H / 2 - C.FOOT_EXT / 2, 0)))
            .box(FOOT_W, C.FOOT_EXT, C.FACE_T, centered=(True, True, False)))
    foot = _touch_fillet(foot, C.EDGE_FILLET)
    body = body.union(foot)

    t1_o = U.offset(OUTER, -C.FRAME_INSET)
    t1_i = U.offset(OUTER, -(C.FRAME_INSET + C.FRAME_T1_W))
    t2_i = U.offset(OUTER, -(C.FRAME_INSET + C.FRAME_T1_W + C.FRAME_T2_W))
    tier1 = _touch_fillet(U.ring(t1_o, t1_i, C.FRAME_R1, z=C.FACE_T), C.FRAME_T1_FILLET)
    tier2 = _touch_fillet(U.ring(t1_i, t2_i, C.FRAME_R2, z=C.FACE_T), C.FRAME_T2_FILLET)
    frame = tier1.union(tier2)

    pockets = [_pocket_cutter(x) for x in C.POCKET_XS]
    notches = [_notch_cutter(x) for x in C.POCKET_XS]
    body = (body.cut(cq.Compound.makeCompound(pockets))
                .cut(cq.Compound.makeCompound(notches)))

    pegs = [
        (cq.Workplane(cq.Plane(origin=(x, C.HOLE_Y, C.FACE_T - C.POCKET_DEPTH)))
         .circle(C.PEG_D / 2).extrude(C.PEG_H)
         .edges(">Z").chamfer(C.PEG_CHAMFER).val())
        for x in C.POCKET_XS
    ]
    body = body.union(cq.Compound.makeCompound(pegs))

    # Underside U-channel for the box tongue. Kept as a closed ring (both walls
    # rise from the bed; short bridge) rather than an open rabbet, which would
    # hang the whole outer flange in mid-air when printing face-up.
    ch_o = U.offset(OUTER, -0.05)
    ch_i = U.offset(OUTER, -(C.BOX_WALL + C.LIP_CLEAR))
    body = body.cut(U.ring(ch_i, ch_o, C.LIP_DROP, z=0))

    return {"body": body, "frame": frame}


def make_box():
    """Return the single-solid storage box / stand."""
    shell = U.extrude(OUTER, C.BOX_H)
    body = shell
    well = U.offset(OUTER, -C.BOX_WALL)
    body = body.cut(U.extrude(well, C.BOX_INNER_DEPTH + 1, z=C.BOX_FLOOR))

    inner_l = C.BOARD_W - 2 * C.BOX_WALL
    rail = (cq.Workplane(cq.Plane(origin=(0, C.Y_GROOVE, C.BOX_FLOOR)))
            .box(inner_l, C.RAIL_W, C.BOX_H - C.BOX_FLOOR, centered=(True, True, False)))
    body = body.union(rail).intersect(shell.val())
    body = _touch_fillet(body, C.EDGE_FILLET)

    # upstanding rim that seats in the lid's underside cap channel; added after the
    # shell clip so it isn't cut off at z = BOX_H.
    t_i = U.offset(OUTER, -(C.BOX_WALL + C.LIP_CLEAR) + C.TONGUE_CLEAR)
    t_o = U.offset(OUTER, -0.05 - C.TONGUE_CLEAR)
    tongue = _touch_fillet(U.ring(t_o, t_i, C.TONGUE_H, z=C.BOX_H), C.EDGE_FILLET)
    body = body.union(tongue)

    foot_cutter = (U.extrude(U.offset(BODY_FOOTPRINT, C.SLOT_CLEAR),
                             C.SLOT_W, z=-C.SLOT_CLEAR)
                   .val().located(seat_location()))
    body = body.cut(foot_cutter)

    zc = C.BOX_H - C.LEADIN_DEPTH
    lead = (cq.Workplane(cq.Plane(origin=(0, C.Y_GROOVE_SLOT, zc)))
            .rect(C.BOARD_W + 2, C.SLOT_W)
            .workplane(offset=C.LEADIN_DEPTH + 2)
            .rect(C.BOARD_W + 2, C.SLOT_W + 2 * C.LEADIN)
            .loft())
    body = body.cut(lead)

    return body
