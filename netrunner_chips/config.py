"""Parameters for the Academic 133+ XL Netrunner chip carrier.

All dimensions are millimetres. The geometry builders in ``parts.py`` consume
these via ``from netrunner_chips.config import *``.
"""

import math

# Gamegenic "The Academic 133+ XL" main compartment (W x D x H), in mm.
COMPARTMENT_X = 113.0
COMPARTMENT_Y = 86.0
COMPARTMENT_DEPTH = 109.0

# Ceramic chip stock.
CHIP_DIAMETER = 39.0
CHIP_THICKNESS = 3.4

# Lane / cradle parameters. Chips sit on edge in a cradle whose sides are arcs
# of (just larger than) the chip so they self-centre; the shallow *curved* bottom
# of the circle is replaced by a flat bottom (a flat patch prints as a clean top
# surface; it was the curvature that printed wavy, not the horizontality). The
# chip rests on both the two arc flanks and the flat bottom. The tray bottom
# stays solid, so it prints on the bed.
CRADLE_RADIAL_CLEAR = 0.5  # radial play between chip and cradle arc (lane = 2*radius)
CRADLE_RELIEF_W = 28.6  # width of the flat bottom under the chip
RELIEF_GAP = 0.1  # drop of the flat bottom below the chip (easier retrieval)
FLOOR_T = 2.0  # solid floor kept under the relief
INNER_WALL = 1.0  # wall between a lane and the central pole slot
OUTER_WALL = 1.0  # outer long wall
END_WALL = 2.0  # short end walls
WALL_RISE = 1.0  # how far the low walls reach above the chip's mid-height

# Central blade ("pole") + carrier parameters. The pole is a separate print from
# the base plate: a plain flat sheet that prints on its big face (no supports;
# lift load in-plane, not across layer lines). It drops into a straight slot in
# the base plate and a horizontal cross-pin through plate and pole locks it, so
# the whole carrier lifts the chip stack as one unit.
BLADE_THICKNESS = 1.4
BLADE_SLOT_CLEARANCE = 0.4  # extra width of a tray slot over the blade
BASE_PLATE_H = 3.5  # base plate; thick enough to house the cross-pin
POLE_SLOT_CLEAR = 0.2  # per-side clearance of the base slot over the pole
SLOT_FLOOR = 0.4  # solid plate kept under the pole slot (keeps the plate one piece)
PIN_DIAMETER = 1.75  # cross-pin: a snip of 1.75 mm filament (or a 2 mm rod)
PIN_CLEAR = 0.15  # clearance of the pin holes over the pin
PIN_Z = 1.95  # height of the cross-pin axis above the bed
# Grip: hole sits in the upper part of the dice cap; pole ends flush with the cap
# rim. Total height matches the Academic compartment (~109 mm).
GRIP_MARGIN_BELOW = 1.5  # grip-hole bottom → cap rim (or feature above)
GRIP_HOLE_LENGTH = 52.0  # was 45
GRIP_HOLE_HEIGHT = 14.0  # was 12
GRIP_HOLE_FILLET = 5.0
BLADE_END_CLEAR = 0.4  # per-end clearance of the blade vs the tray slot

# Type bins + "every 5 chips" separators.
GROUP = 5
DIVIDER_THICKNESS = 1.5
DIVIDER_HEIGHT = 14.0  # low dividers, well under the chip tops
DIVIDER_GAP = 2.0
BUMP_THICKNESS = 1.1  # thickness (along the row) of a counting bump
BUMP_GAP = 1.1  # extra spacing opened at every-5 for the bump to sit in
BUMP_RISE = 12.0  # height of the counting bump above the relief floor
CREDIT_BIN_EXTRA = 0.6  # extra along-row space per 5-chip credit well (mm)

# Dice cap (tier 3): sits on top chips; rim flush with pole top.
COVER_CLEARANCE = 2.0  # gap below deck-box lid (109 mm compartment)
COVER_FLOOR_T = FLOOR_T  # match chip-tray floor
DICE_SIZE = 16.0  # standard d6 edge length (measure yours if tight)
DICE_WELL_CLEAR = 0.6  # play around each die in its well

OUTER_FILLET = 2.0

# Two-tone colours: a mint body with a pink trim along the top edges, matching
# the Gamegenic Academic box. Parts are split into a mint solid and a pink edge
# solid, and both colours are written into the 3MF.
EDGE_BAND = 1.2  # thickness of the pink trim taken off the top edges
MINT_HEX = "#46C2C2"
PINK_HEX = "#F25C9C"
MINT_RGB = (0.27, 0.76, 0.76)
PINK_RGB = (0.95, 0.36, 0.61)

# --------------------------------------------------------------------------- #
# Derived dimensions
# --------------------------------------------------------------------------- #

CHIP_RADIUS = CHIP_DIAMETER / 2
CRADLE_RADIUS = CHIP_RADIUS + CRADLE_RADIAL_CLEAR  # cradle arc radius
LANE_WIDTH = 2 * CRADLE_RADIUS  # lane width (keeps the tray width unchanged)
HALF_LANE = CRADLE_RADIUS
SLOT_WIDTH = BLADE_THICKNESS + BLADE_SLOT_CLEARANCE
POLE_SLOT_W = BLADE_THICKNESS + 2 * POLE_SLOT_CLEAR  # base-plate slot width
PIN_HOLE_D = PIN_DIAMETER + 2 * PIN_CLEAR  # pin hole diameter (plate + pole)
FLOOR_BOTTOM = 0.0  # tray bottom sits flat on the bed (no hanging rim)
RELIEF_Z = FLOOR_BOTTOM + FLOOR_T  # flat bottom floor (top of the solid base)
CHIP_BOTTOM_Z = RELIEF_Z + RELIEF_GAP  # chip's lowest point (rests on the flat bottom)
CHIP_CENTER_Z = CHIP_BOTTOM_Z + CHIP_RADIUS  # chip centre
CHIP_TOP_Z = CHIP_CENTER_Z + CHIP_RADIUS  # top of the chips
WALL_TOP = CHIP_CENTER_Z + WALL_RISE  # low walls; chips stand proud above them
# Cradle circle centre, set so the arc meets the chip exactly at the relief
# corners (+-CRADLE_RELIEF_W/2), which is where the chip comes to rest.
_HALF_RELIEF = CRADLE_RELIEF_W / 2
CRADLE_AXIS_Z = (
    CHIP_CENTER_Z
    - math.sqrt(CHIP_RADIUS ** 2 - _HALF_RELIEF ** 2)
    + math.sqrt(CRADLE_RADIUS ** 2 - _HALF_RELIEF ** 2)
)

OUTER_X = COMPARTMENT_X - 1.5
ROW_OFFSET_Y = SLOT_WIDTH / 2 + INNER_WALL + HALF_LANE  # lane center in Y
OUTER_Y = SLOT_WIDTH + 2 * INNER_WALL + 2 * LANE_WIDTH + 2 * OUTER_WALL
ROW_LENGTH = OUTER_X - 2 * END_WALL
# Blade spans almost the full tray slot (was ~6 mm short, leaving end gaps).
BLADE_LENGTH = ROW_LENGTH - 2 * BLADE_END_CLEAR

# Solid-bottomed trays stack by resting their flat bottom on the chips of the
# tray below; the central pole keeps the tiers square (locating each tray through
# its blade slot) and lifts the whole stack out in one grab.
TIER_PITCH = CHIP_TOP_Z  # full chip-top height per tier (solid bottom, no nesting)
BOTTOM_TRAY_Z = BASE_PLATE_H  # bottom tray rests on the carrier plate
TRAY_Z = (BOTTOM_TRAY_Z, BOTTOM_TRAY_Z + TIER_PITCH)  # bottom / top tray heights
TOP_OF_STACK = TRAY_Z[1] + CHIP_TOP_Z  # top of the upper tier's chips
# Cap sits on those chips; rim = pole top; height capped so the box still closes.
COVER_BOTTOM_Z = TOP_OF_STACK
COVER_PART_H = min(WALL_TOP, COMPARTMENT_DEPTH - COVER_CLEARANCE - TOP_OF_STACK)
CARRIER_TOP = COVER_BOTTOM_Z + COVER_PART_H
# Grip hole in assembly coords — bottom sits GRIP_MARGIN_BELOW below the shared top.
GRIP_HOLE_Z = CARRIER_TOP - GRIP_MARGIN_BELOW - GRIP_HOLE_HEIGHT / 2
# Same window in cover-local Z (0 = cap floor on the chips).
GRIP_BOTTOM_IN_COVER = COVER_PART_H - GRIP_MARGIN_BELOW - GRIP_HOLE_HEIGHT
GRIP_TOP_IN_COVER = COVER_PART_H - GRIP_MARGIN_BELOW
DICE_WELL_DEPTH = COVER_PART_H - COVER_FLOOR_T

# Tray A — each lane: 15× credit-1 (three 5-stacks with , bumps) at one end,
# 5× credit-5 at the other; second lane mirrored.
#   +Y: || 5×1 , 5×1 , 5×1 |     | 5×5 ||
#   −Y: || 5×5 |     | 5×1 , 5×1 , 5×1 ||
TRAY_A_ROWS = (
    ("ends", False, [("credit-1", 15), ("credit-5", 5)]),
    ("ends", True,  [("credit-1", 15), ("credit-5", 5)]),
)
TRAY_B_ROWS = (
    ("neg", False, [("virus/power", 10), ("click", 8)]),
    ("pos", False, [("bad-pub", 6), ("tag/core", 10)]),
)
