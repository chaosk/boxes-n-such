"""Assemble the chip carrier and write chip_set.3mf.

Run with ``uv run python -m netrunner_chips``. See README.md for the design,
the chip set, and the file layout.
"""

import sys
from pathlib import Path

# Allow running this file directly / in cq-editor by putting the repo root on the
# path; under `python -m netrunner_chips` it is already there.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import cadquery as cq

from insertkit import bambu3mf

from netrunner_chips.config import *  # noqa: F401,F403  (model parameters)
from netrunner_chips.parts import (
    cover_edge_split, edge_split, make_carrier, make_cover, make_tray, row_features,
)

if "show_object" not in globals():
    def show_object(*args, **kwargs):
        return


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #

tray_a = make_tray(*TRAY_A_ROWS)
tray_b = make_tray(*TRAY_B_ROWS)
cover = make_cover()
plate, pole = make_carrier()  # base plate + slide-in pole, printed separately

# Filament 1 = mint, filament 2 = pink.
FILAMENTS = [MINT_HEX, PINK_HEX]
EXTRUDER_RGB = {1: MINT_RGB, 2: PINK_RGB}


def _tray_group(name, part, top_z=WALL_TOP):
    """Mint body + pink top-edge trim for a chip tray."""
    mint, pink = edge_split(part, top_z)
    slug = name.lower().replace(" ", "_")
    parts = [(slug, mint, 1)]
    if pink.val().Solids():
        parts.append((f"{slug}_edge", pink, 2))
    return (name, parts)


def _cover_group(name, part):
    """Mint body + pink rim for the dice cap (centre open at grip)."""
    mint, pink = cover_edge_split(part)
    slug = name.lower().replace(" ", "_")
    parts = [(slug, mint, 1)]
    if pink.val().Solids():
        parts.append((f"{slug}_edge", pink, 2))
    return (name, parts)


# Each group -> (name, [(part_name, solid, extruder)]) plus its Z in the stack.
GROUPS = [
    ("carrier base", [("carrier_base", plate, 2)]),
    ("carrier pole", [("carrier_pole", pole, 2)]),
    _tray_group("tray A", tray_a),
    _tray_group("tray B", tray_b),
    _cover_group("dice cover", cover),
]
GROUP_Z = {
    "carrier base": 0.0,
    "carrier pole": 0.0,
    "tray A": TRAY_Z[0],
    "tray B": TRAY_Z[1],
    "dice cover": COVER_BOTTOM_Z,
}


# --------------------------------------------------------------------------- #
# Preview (cq-editor)
# --------------------------------------------------------------------------- #

def preview_assembly():
    asm = cq.Assembly(name="academic_133_chip_carrier")
    for gname, parts in GROUPS:
        loc = cq.Location((0, 0, GROUP_Z[gname]))
        for pname, solid, extruder in parts:
            asm.add(solid, name=pname, color=cq.Color(*EXTRUDER_RGB[extruder]), loc=loc)
    return asm


# --------------------------------------------------------------------------- #
# Print layout — one object per Bambu plate, centred on the bed
# --------------------------------------------------------------------------- #

def _print_orient(gname, solid):
    """Orient a part as it should print. The pole lies on its big face; every
    other part already prints flat as modelled."""
    if gname != "carrier pole":
        return solid
    laid = solid.rotate((0, 0, 0), (1, 0, 0), -90)
    return laid.translate((0, 0, -laid.val().BoundingBox().zmin))


def plates():
    """One Bambu plate per printable object."""
    out = []
    for gname, parts in GROUPS:
        oriented = [(pname, _print_orient(gname, s), ext) for pname, s, ext in parts]
        out.append((gname, [(gname, oriented)]))
    return out


def describe():
    print(
        f"tray: {OUTER_X:.1f} x {OUTER_Y:.1f} mm, low walls {WALL_TOP:.1f} mm, "
        f"cradle (chip {CHIP_DIAMETER:.0f} mm on edge, lane {LANE_WIDTH:.1f} mm, "
        f"relief {CRADLE_RELIEF_W:.0f} mm, floor {FLOOR_T:.1f} mm)\n"
        f"tier pitch {TIER_PITCH:.1f} mm | blade {BLADE_THICKNESS} mm in "
        f"{SLOT_WIDTH} mm slot\n"
        f"pole drops into a {POLE_SLOT_W:.1f} mm slot, locked by a "
        f"{PIN_DIAMETER:g} mm cross-pin in a {BASE_PLATE_H:g} mm plate\n"
        f"blade {BLADE_LENGTH:.1f} mm long (tray slot {ROW_LENGTH:.1f}), "
        f"grip {GRIP_HOLE_LENGTH:.0f}×{GRIP_HOLE_HEIGHT:.0f} mm, "
        f"carrier height {CARRIER_TOP:.1f} mm (compartment {COMPARTMENT_DEPTH} mm)\n"
        f"dice cover {COVER_PART_H:.1f} mm tall, stack top {CARRIER_TOP:.1f}"
        f"/{COMPARTMENT_DEPTH:.0f} mm compartment"
    )
    total = 0
    for name, tray_rows in (("A", TRAY_A_ROWS), ("B", TRAY_B_ROWS)):
        for side, row_spec in zip(("+Y", "-Y"), tray_rows):
            _, _, blocks = row_spec
            _, _, _, chips, used = row_features(row_spec)
            bins = " | ".join(f"{t} x{c}" for t, c in blocks)
            total += chips
            print(f"  tray {name} {side}: {bins}  ({used:.1f}/{ROW_LENGTH:.1f} mm)")
    print(f"  total chips: {total}")


describe()
show_object(preview_assembly(), name="chip_carrier")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "chip_set.3mf"
    print("laying out plates…", flush=True)
    placed, plate_members = bambu3mf.plate_layout(plates())
    print(f"tessellating {len(placed)} objects…", flush=True)
    bambu3mf.export_bambu_3mf(placed, FILAMENTS, out, plates=plate_members)
    print(f"exported {out.name} ({len(placed)} objects on {len(plate_members)} plates) "
          f"to {out.parent}")
