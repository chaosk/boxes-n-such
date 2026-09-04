"""Parameters for the Blood on the Clocktower tag board + storage box.

All dimensions are millimetres. Everything that controls the model lives here so
the part builders in ``parts.py`` stay declarative.
"""

import math
from pathlib import Path

from matplotlib import font_manager as _fm

HERE = Path(__file__).resolve().parent


def _find_font(*needles, fallback_family="serif"):
    """Path to the first installed font matching any of ``needles`` (matched
    against the family name or filename), else a sensible system fallback."""
    for f in _fm.fontManager.ttflist:
        hay = f"{f.name} {f.fname}".lower()
        if any(n.lower() in hay for n in needles):
            return f.fname
    return _fm.findfont(_fm.FontProperties(family=fallback_family))

# --------------------------------------------------------------------------- #
# Categories / colours
# --------------------------------------------------------------------------- #

CATEGORIES = [
    ("TOWNSFOLK", ["3", "5", "7", "9"], "#2E6BE6"),   # blue
    ("OUTSIDERS", ["0", "1", "2"], "#28B6D4"),   # cyan
    ("MINIONS", ["1", "2", "3"], "#E8602A"),     # orange
    ("DEMON", ["1"], "#D43028"),                 # red
]
ALL_TAGS = [(cat, num, col) for cat, nums, col in CATEGORIES for num in nums]

BLACK = "#1A1820"
LAVENDER = "#9E8FCB"

# --------------------------------------------------------------------------- #
# Tag ("plaque" shape: a rectangle with a circle cut from each corner)
# --------------------------------------------------------------------------- #

TAG_W, TAG_H = 37.8, 51.6
TAG_CORNER_R = 6.0    # radius of the circle bitten out of each corner
TAG_T = 2.0
HOLE_D = 5.0
HOLE_Y = 18.0         # lanyard hole, clear of the coloured border below the top

RING_GAP = 1.4        # colour border inset from the tag edge
RING_W = 1.9          # colour border width
RING_RELIEF = 0.7     # colour border / numeral height above the face

NUM_SIZE = 30.5
NUM_Y = -2.0
NUM_RELIEF = 0.7
_FONT_PATH: str | None = None


def font_path() -> str:
    """Lazily resolve the numeral font (matplotlib scans installed fonts once)."""
    global _FONT_PATH
    if _FONT_PATH is None:
        _FONT_PATH = _find_font("dumbledor", fallback_family="serif")
    return _FONT_PATH

# --------------------------------------------------------------------------- #
# Board (the lid)
# --------------------------------------------------------------------------- #

N_POCKET = len(CATEGORIES)
POCKET_PITCH = 43.0
POCKET_CLEAR = 0.5           # per-side gap of a pocket over a tag
POCKET_DEPTH = 2.2            # tag sinks in and is held
FACE_T = 3.5                 # black face plate thickness

NOTCH_WX = 30.0
NOTCH_WY = 18.0
NOTCH_Y = -21.0              # clear of underside lip channel at the front rim
NOTCH_DEPTH = FACE_T + 0.2   # cut fully through — no 1-layer floor
NOTCH_FILLET = 4.5

# Peg vs tag hole: ~0.1/side is a light press-fit on a 0.4 mm nozzle (was 0.3 → floppy).
PEG_CLEAR = 0.1
PEG_D = HOLE_D - 2 * PEG_CLEAR
PEG_H = POCKET_DEPTH
PEG_CHAMFER = 0.5
BOARD_SIDE = 13.0
BOARD_DEPTH = 70.0

FRAME_W = 6.0  # legacy total from outer edge; tiers sized below
# Sit the lavender frame fully inward of the underside lip channel so its first
# layer rests on solid face, not on the channel bridge.
FRAME_INSET = 2.8
FRAME_T1_W = 2.6
FRAME_T2_W = 1.9
FRAME_R1 = 1.1
FRAME_R2 = 2.4

BOARD_CORNER_R = 9.0

# Touch rounding — matched 0.35 mm top-rim on tags, pockets, box, and lid.
EDGE_FILLET = 0.35
RING_TOP_FILLET = EDGE_FILLET        # colour border only (numeral added after)
FRAME_T1_FILLET = 0.3                # outer lavender step (1.1 mm tall; 0.35 fails in OCC)
FRAME_T2_FILLET = EDGE_FILLET        # inner lavender step

# --------------------------------------------------------------------------- #
# Box
# --------------------------------------------------------------------------- #

BOX_WALL = 2.6
BOX_FLOOR = 2.2
BOX_INNER_DEPTH = 9.0

# Closure: shallow underside cap channel over the box wall; lid prints face-up.
LIP_T = 1.2
LIP_DROP = 2.0
LIP_CLEAR = 0.12
TONGUE_CLEAR = 0.08   # press-fit clearance inside the lid channel (per side)
TONGUE_H = LIP_DROP - 0.3   # box rim height; seats in the channel with headroom

LEAN_DEG = 0.0
RAIL_W = 13.0
FOOT_EXT = 6.0
GROOVE_DEPTH = 7.0
SLOT_CLEAR = 0.25
LEADIN = 1.2
LEADIN_DEPTH = 2.0

# --------------------------------------------------------------------------- #
# Derived geometry
# --------------------------------------------------------------------------- #

BOARD_W = (N_POCKET - 1) * POCKET_PITCH + TAG_W + 2 * BOARD_SIDE
BOARD_H = BOARD_DEPTH
POCKET_XS = [(-(N_POCKET - 1) / 2 + i) * POCKET_PITCH for i in range(N_POCKET)]
BOX_H = BOX_FLOOR + BOX_INNER_DEPTH
Y_GROOVE = -(BOARD_DEPTH / 2 - BOX_WALL) + RAIL_W / 2 - 1.0
SLOT_W = FACE_T + 2 * SLOT_CLEAR
Y_GROOVE_SLOT = Y_GROOVE

BODY_HALF = BOARD_H / 2 + FOOT_EXT

SEAT_ALPHA = 90.0 - LEAN_DEG
_a = math.radians(SEAT_ALPHA)
SEAT_TY = Y_GROOVE + (FACE_T / 2) * math.sin(_a) + (BOARD_H / 2) * math.cos(_a)
SEAT_TZ = (BOX_H - GROOVE_DEPTH) + BODY_HALF * math.sin(_a)
