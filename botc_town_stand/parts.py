"""Part builders: the numbered tags, the board (lid) and the storage box.

Each colour ends up as its own solid so the multi-colour 3MF export can assign a
filament per part. Rings and walls are built as profiles-with-holes and extruded
once (see :func:`cqutil.ring`); booleans are reserved for genuine cavities
(pockets, the box well, the foot slot) and for combining separate solids.
"""

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


def seat_location():
    """Location that stands a board-local solid up in the box slot."""
    return cq.Location((0, C.SEAT_TY, C.SEAT_TZ), (1, 0, 0), C.SEAT_ALPHA)


def make_tag(num):
    """Return ``(black_body, colour_part)`` for a numbered tag."""
    body = (U.extrude(TAG_OUTLINE, C.TAG_T)
            .faces(">Z").workplane()
            .pushPoints([(0, C.HOLE_Y)]).hole(C.HOLE_D))

    ring_o = U.offset(TAG_OUTLINE, -C.RING_GAP)
    ring_i = U.offset(TAG_OUTLINE, -(C.RING_GAP + C.RING_W))
    ring = U.ring(ring_o, ring_i, C.RING_RELIEF, z=C.TAG_T)
    hole_clear = (cq.Workplane(cq.Plane(origin=(0, C.HOLE_Y, C.TAG_T - 0.5)))
                  .cylinder(C.RING_RELIEF + 2, C.HOLE_D / 2 + 1.2,
                            centered=(True, True, False)))
    ring = ring.cut(hole_clear)

    numeral = U.text_solid(num, C.NUM_SIZE, C.NUM_RELIEF, C.FONT_PATH,
                           origin=(0, C.NUM_Y, C.TAG_T))
    colour = ring.union(cq.Workplane("XY").add(numeral))
    return body, colour


def make_board():
    """Return ``{"body": black_solid, "frame": lavender_solid}``."""
    body = U.extrude(OUTER, C.FACE_T)
    foot = (cq.Workplane(cq.Plane(origin=(0, -C.BOARD_H / 2 - C.FOOT_EXT / 2, 0)))
            .box(FOOT_W, C.FOOT_EXT, C.FACE_T, centered=(True, True, False)))
    body = body.union(foot)

    t1_o = U.offset(OUTER, -C.FRAME_INSET)
    t1_i = U.offset(OUTER, -(C.FRAME_INSET + C.FRAME_T1_W))
    t2_i = U.offset(OUTER, -(C.FRAME_INSET + C.FRAME_T1_W + C.FRAME_T2_W))
    frame = (U.ring(t1_o, t1_i, C.FRAME_R1, z=C.FACE_T)
             .union(U.ring(t1_i, t2_i, C.FRAME_R2, z=C.FACE_T)))

    pocket_pts = U.offset(TAG_OUTLINE, C.POCKET_CLEAR)
    pockets = [
        cq.Workplane(cq.Plane(origin=(x, 0, C.FACE_T - C.POCKET_DEPTH)))
        .polyline(pocket_pts).close()
        .extrude(C.POCKET_DEPTH + 1).val()
        for x in C.POCKET_XS
    ]
    notches = [
        cq.Workplane(cq.Plane(origin=(x, C.NOTCH_Y, C.FACE_T - C.NOTCH_DEPTH)))
        .box(C.NOTCH_WX, C.NOTCH_WY, C.NOTCH_DEPTH + 1, centered=(True, True, False))
        .edges("|Z").fillet(C.NOTCH_FILLET).val()
        for x in C.POCKET_XS
    ]
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

    # upstanding rim that seats in the lid's underside cap channel; added after the
    # shell clip so it isn't cut off at z = BOX_H.
    t_i = U.offset(OUTER, -(C.BOX_WALL + C.LIP_CLEAR) + C.TONGUE_CLEAR)
    t_o = U.offset(OUTER, -0.05 - C.TONGUE_CLEAR)
    tongue = U.ring(t_o, t_i, C.TONGUE_H, z=C.BOX_H)
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
