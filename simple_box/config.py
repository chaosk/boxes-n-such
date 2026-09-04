"""Parameters for the simple lidded box.

All dimensions are millimetres. Every tunable lives here so ``parts.py`` stays
declarative.
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent

# --------------------------------------------------------------------------- #
# Overall box outer envelope (lid stacks on top; overall stack = BOX_H + LID_T)
# --------------------------------------------------------------------------- #

BOX_W = 80.0          # outer width  (X)
BOX_D = 60.0          # outer depth  (Y)
BOX_H = 30.0          # outer height of the box body (excludes the lid plate)

WALL = 2.4            # side wall thickness
FLOOR = 2.0           # floor thickness of the box
LID_T = 2.0           # lid plate thickness (excludes the underside channel)

# --------------------------------------------------------------------------- #
# Lid / box mating: upstanding tongue on the box rim seats in an underside
# channel in the lid. Named clearances keep the fit tunable without touching
# ``parts.py``.
# --------------------------------------------------------------------------- #

LIP_CLEAR = 0.15      # channel over-width vs the box wall (per side)
TONGUE_CLEAR = 0.10   # tongue clearance inside the channel (per side)
TONGUE_H = 2.5        # tongue height above the box rim
LIP_DROP = TONGUE_H + 0.3   # underside channel depth — a hair deeper than the tongue

# --------------------------------------------------------------------------- #
# Cosmetics
# --------------------------------------------------------------------------- #

EDGE_FILLET = 0.4     # touch-round exposed top-face perimeter edges

COLOR = "#3B7DDD"     # single filament — the ticket asks for a "simple" box
