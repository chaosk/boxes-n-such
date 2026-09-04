"""Geometry builders for the chip carrier: trays, the carrier plate + pole, and
the two-tone edge split. Parameters come from ``config``."""

import cadquery as cq

from netrunner_chips.config import *  # noqa: F401,F403  (model parameters)


def _pack_block(name: str, count: int) -> tuple[list[float], float]:
    """Pack one chip type from x=0 toward +X; return bump positions and length."""
    pitch = CHIP_THICKNESS
    x = 0.0
    bumps: list[float] = []
    is_credit = name.startswith("credit")
    for chip_index in range(count):
        x += pitch
        if is_credit and (chip_index + 1) % GROUP == 0:
            if (chip_index + 1) != count:
                bumps.append(x + BUMP_GAP / 2)
                x += BUMP_GAP
            x += CREDIT_BIN_EXTRA  # each 5-chip well (+ credit-5 single bin)
    return bumps, x


def _pack_blocks(blocks: list[tuple[str, int]]) -> tuple[list[float], list[float], int, float]:
    """Pack blocks sequentially from x=0; return bumps, dividers, chip count, length."""
    bumps: list[float] = []
    dividers: list[float] = []
    chips = 0
    x = 0.0
    for block_index, (name, count) in enumerate(blocks):
        block_bumps, block_len = _pack_block(name, count)
        bumps.extend(b + x for b in block_bumps)
        x += block_len
        chips += count
        if block_index != len(blocks) - 1:
            dividers.append(x + DIVIDER_GAP / 2)
            x += DIVIDER_GAP
    return bumps, dividers, chips, x


def row_features(row_spec: tuple) -> tuple[list[float], list[float], list[float], int, float]:
    """Return (bumps, dividers, end_walls, chip_count, used_length) for one lane.

    ``row_spec`` is ``(layout, mirror, blocks)`` where *layout* is:

    - ``"ends"`` — first block at one end, second at the opposite end
    - ``"neg"`` — all blocks packed from the −X end toward centre
    - ``"pos"`` — all blocks packed from the +X end toward centre

    *mirror* swaps ends (for the second lane of a tray).
    """
    layout, mirror, blocks = row_spec
    neg = -ROW_LENGTH / 2
    pos = ROW_LENGTH / 2
    end_walls: list[float] = []

    if layout == "ends":
        assert len(blocks) == 2, "ends layout expects exactly two blocks"
        b0_bumps, b0_len = _pack_block(*blocks[0])
        b1_bumps, b1_len = _pack_block(*blocks[1])
        used = b0_len + b1_len
        # Place groups at opposite ends; inner end-stops keep them from sliding
        # into the mid-lane gap (outer tray walls already hold the far ends).
        if not mirror:
            b0_origin, b1_origin = neg, pos - b1_len
            b0_side, b1_side = "left", "right"
        else:
            b0_origin, b1_origin = pos - b0_len, neg
            b0_side, b1_side = "right", "left"
        # Inner face of each group (toward mid-lane), by end — not by sign of
        # origin (a wide right-end block can still start left of centre).
        inners = []
        for origin, length, side in (
            (b0_origin, b0_len, b0_side),
            (b1_origin, b1_len, b1_side),
        ):
            if side == "left":
                inners.append(origin + length)  # right face of left-end group
            else:
                inners.append(origin)  # left face of right-end group
        left_inner, right_inner = sorted(inners)
        gap = right_inner - left_inner
        if gap >= 2 * DIVIDER_THICKNESS + 0.5:
            # Room for a stop on each group's inner face.
            end_walls = [
                left_inner + DIVIDER_THICKNESS / 2,
                right_inner - DIVIDER_THICKNESS / 2,
            ]
        elif gap >= DIVIDER_THICKNESS + 0.5:
            # Narrow gap — one shared mid stop.
            end_walls = [(left_inner + right_inner) / 2]
        # else: groups nearly meet; tray end walls alone are enough.
        bumps = [b + b0_origin for b in b0_bumps] + [b + b1_origin for b in b1_bumps]
        return bumps, [], end_walls, blocks[0][1] + blocks[1][1], used

    bumps, dividers, chips, used = _pack_blocks(blocks)
    assert used <= ROW_LENGTH + 1e-6, f"row overflows: {used:.1f}>{ROW_LENGTH}"

    if layout == "neg" and not mirror or layout == "pos" and mirror:
        origin = neg
        end_walls = [neg + used + DIVIDER_THICKNESS / 2]
    else:
        origin = pos - used
        end_walls = [pos - used - DIVIDER_THICKNESS / 2]

    return (
        [b + origin for b in bumps],
        [d + origin for d in dividers],
        end_walls,
        chips,
        used,
    )


def _cradle_cut(cy):
    """A chip cradle cut into the solid floor: circular side walls (arcs of
    CRADLE_RADIUS) cup the chip, an open top above the equator lets it drop in and
    stand proud, and a dropped flat relief replaces the shallow round bottom.
    Removing that near-horizontal bottom is what kills the wavy slicer top; the
    chip instead rests on the two arc flanks and clears the relief floor. Built at
    the lane centre via workplane origins (no translate).

    Cut = full cylinder (the arcs) + a straight box above the equator (open top,
    vertical walls so the chip drops in) + a narrow box down to the relief floor
    (the dropped flat middle)."""
    arcs = (
        cq.Workplane(cq.Plane(origin=(0, cy, CRADLE_AXIS_Z), normal=(1, 0, 0)))
        .circle(CRADLE_RADIUS)
        .extrude(ROW_LENGTH / 2, both=True)
    )
    top = cq.Workplane(cq.Plane(origin=(0, cy, CRADLE_AXIS_Z))).box(
        ROW_LENGTH, LANE_WIDTH, CHIP_TOP_Z + 2 - CRADLE_AXIS_Z,
        centered=(True, True, False),
    )
    relief = cq.Workplane(cq.Plane(origin=(0, cy, RELIEF_Z))).box(
        ROW_LENGTH, CRADLE_RELIEF_W, CRADLE_AXIS_Z - RELIEF_Z,
        centered=(True, True, False),
    )
    return arcs.union(top).union(relief)


def _feature_block(x, cy, thickness, height):
    """A divider block standing on the relief floor, placed via a workplane
    origin (no post-hoc translate)."""
    return (
        cq.Workplane(cq.Plane(origin=(x, cy, RELIEF_Z)))
        .box(thickness, LANE_WIDTH, height, centered=(True, True, False))
        .val()
    )


def _bump_fin(x, cy):
    """A counting bump shaped to match the cradle: a thin (along the row) slice
    that fills the cradle cross-section from the flat bottom up to BUMP_RISE. So
    it is a rectangular block at the bottom (the flat relief, with vertical notch
    walls) whose sides then follow the same arc as the cradle side walls. Built by
    intersecting the cradle channel with a thin, height-capped box."""
    cap = cq.Workplane(cq.Plane(origin=(x, cy, RELIEF_Z))).box(
        BUMP_THICKNESS, LANE_WIDTH, BUMP_RISE, centered=(True, True, False)
    )
    return _cradle_cut(cy).intersect(cap).val()


def make_tray(plus_row, minus_row) -> cq.Workplane:
    rows = [(ROW_OFFSET_Y, plus_row), (-ROW_OFFSET_Y, minus_row)]

    # Solid-bottomed pan: a solid slab from the bed up to the low walls, with the
    # chip cradles cut into the top. The whole bottom is solid, so it prints
    # directly on the bed with no support; chips stand proud of the low walls and
    # the tray above just rests its flat bottom on these chips.
    body = (
        cq.Workplane(cq.Plane(origin=(0, 0, FLOOR_BOTTOM)))
        .box(OUTER_X, OUTER_Y, WALL_TOP - FLOOR_BOTTOM, centered=(True, True, False))
        .edges("|Z")
        .fillet(OUTER_FILLET)
    )

    # Everything removed from the floor - both chip cradles plus the central
    # blade slot - collected into one compound and subtracted in a single
    # boolean (rather than cutting once per feature in a loop).
    blade_slot = cq.Workplane("XY").box(
        ROW_LENGTH, SLOT_WIDTH, CHIP_TOP_Z + 2, centered=(True, True, False)
    )
    cutters = [_cradle_cut(cy).val() for cy, _ in rows] + [blade_slot.val()]
    body = body.cut(cq.Compound.makeCompound(cutters))

    # Type dividers and counting bumps, likewise unioned in a single boolean.
    features = []
    for cy, row_spec in rows:
        bumps, dividers, end_walls, _, used = row_features(row_spec)
        walls = dividers + end_walls
        features += [_feature_block(dx, cy, DIVIDER_THICKNESS, DIVIDER_HEIGHT) for dx in walls]
        features += [_bump_fin(bx, cy) for bx in bumps]

    body = body.union(cq.Compound.makeCompound(features))

    return body


def _grip_opening_cutter():
    """Through opening — bottom corners rounded in, top left sharp for rim fillet."""
    lane_inner = ROW_OFFSET_Y - LANE_WIDTH / 2
    z0 = GRIP_BOTTOM_IN_COVER
    z1 = COVER_PART_H + 0.05
    y_span = 2 * lane_inner + SLOT_WIDTH + 0.2
    hw = GRIP_HOLE_LENGTH / 2
    r = min(GRIP_HOLE_FILLET, hw - 0.2, (z1 - z0) / 2 - 0.1)

    return (
        cq.Workplane("XZ")
        .moveTo(-hw, z1)
        .lineTo(hw, z1)
        .lineTo(hw, z0 + r)
        .radiusArc((hw - r, z0), r)
        .lineTo(-hw + r, z0)
        .radiusArc((-hw, z0 + r), r)
        .close()
        .extrude(y_span / 2, both=True)
        .val()
    )


def _fillet_grip_opening_top(part):
    """Round the rim lip above the opening (out into the wall, not into the hole)."""
    hw = GRIP_HOLE_LENGTH / 2
    y_half = (2 * (ROW_OFFSET_Y - LANE_WIDTH / 2) + SLOT_WIDTH + 0.2) / 2
    r = min(GRIP_HOLE_FILLET, hw - 0.2, GRIP_HOLE_HEIGHT / 2 - 0.1)
    edges = []
    for x in (hw, -hw):
        for y in (y_half, -y_half):
            edges.extend(
                part.edges(cq.NearestToPointSelector((x, y, COVER_PART_H))).vals()
            )
    if edges:
        part = part.newObject([part.val().fillet(r, edges)])
    return part


def _dice_well_cut(cy):
    """Rectangular lane pocket — same width/placement as a chip cradle lane."""
    return (
        cq.Workplane(cq.Plane(origin=(0, cy, COVER_FLOOR_T)))
        .box(ROW_LENGTH, LANE_WIDTH, DICE_WELL_DEPTH + 0.1, centered=(True, True, False))
    )


def make_cover() -> cq.Workplane:
    """Dice cap — same outer shell / lane layout as chip trays; open centre at grip."""
    # Same pan shell as make_tray (low outer walls, solid floor).
    body = (
        cq.Workplane(cq.Plane(origin=(0, 0, FLOOR_BOTTOM)))
        .box(OUTER_X, OUTER_Y, COVER_PART_H, centered=(True, True, False))
        .edges("|Z")
        .fillet(OUTER_FILLET)
    )
    blade_slot = cq.Workplane("XY").box(
        ROW_LENGTH, SLOT_WIDTH, COVER_PART_H + 2, centered=(True, True, False)
    )
    body = body.cut(cq.Compound.makeCompound(
        [_dice_well_cut(cy).val() for cy in (ROW_OFFSET_Y, -ROW_OFFSET_Y)] + [blade_slot.val()]
    ))
    body = body.cut(_grip_opening_cutter())
    body = _fillet_grip_opening_top(body)
    return body


def cover_edge_split(part):
    """Mint + pink rim (grip opening already clears the centre at the top)."""
    return edge_split(part, COVER_PART_H)


def _pin_hole(span):
    """The cross-pin hole: a cylinder on the Y axis at the pin height, extruded
    far enough each way to clear whatever it is cut from (the plate or the pole)."""
    return (
        cq.Workplane(cq.Plane(origin=(0, 0, PIN_Z), normal=(0, 1, 0)))
        .circle(PIN_HOLE_D / 2)
        .extrude(span, both=True)
    )


def make_carrier() -> cq.Workplane:
    # Flat base plate the stack sits on. The bottom tray rests on this plate and
    # is located by the pole through its blade slot (the trays nearly fill the
    # box in Y, so there's no room for a perimeter locating lip).
    plate = (
        cq.Workplane("XY")
        .box(OUTER_X, OUTER_Y, BASE_PLATE_H, centered=(True, True, False))
        .edges("|Z")
        .fillet(OUTER_FILLET)
    )

    # Straight slot the pole drops into, kept SLOT_FLOOR off the bottom so the
    # plate stays a single piece (not split into a fork), and a cross-pin hole
    # through the plate (and the seated pole) that locks the pole against lift.
    slot = cq.Workplane(cq.Plane(origin=(0, 0, SLOT_FLOOR))).box(
        BLADE_LENGTH + 1.0, POLE_SLOT_W, BASE_PLATE_H - SLOT_FLOOR + 1,
        centered=(True, True, False),
    )
    plate = plate.cut(slot).cut(_pin_hole(OUTER_Y))

    # Pole: a plain flat sheet (prints on its big face). The cross-pin hole near
    # its foot lines up with the plate's once it is dropped into the slot.
    blade = cq.Workplane(cq.Plane(origin=(0, 0, SLOT_FLOOR))).box(
        BLADE_LENGTH, BLADE_THICKNESS, CARRIER_TOP - SLOT_FLOOR,
        centered=(True, True, False),
    )
    blade = blade.cut(_pin_hole(BLADE_THICKNESS))

    # Rounded grip slot, built centred on the grip height (no translate) and cut
    # through the blade's thickness.
    hole = (
        cq.Workplane(cq.Plane(origin=(0, 0, GRIP_HOLE_Z)))
        .box(GRIP_HOLE_LENGTH, BLADE_THICKNESS + 2, GRIP_HOLE_HEIGHT)
        .edges("|Y")
        .fillet(GRIP_HOLE_FILLET)
    )
    blade = blade.cut(hole).edges(">Z").fillet(BLADE_THICKNESS / 2 - 0.01)

    return plate, blade


def _slab(z0, z1):
    """A big flat box spanning Z in [z0, z1], for slicing parts by height."""
    big = 2 * max(OUTER_X, OUTER_Y, CARRIER_TOP)
    return cq.Workplane(cq.Plane(origin=(0, 0, z0))).box(
        big, big, z1 - z0, centered=(True, True, False)
    )


def edge_split(part, top_z):
    """Split a part into (mint_body, pink_edge): the pink edge is the top
    EDGE_BAND of the part, the mint body is everything below it."""
    pink = part.intersect(_slab(top_z - EDGE_BAND, top_z + 1))
    mint = part.cut(_slab(top_z - EDGE_BAND, top_z + 1))
    return mint, pink
