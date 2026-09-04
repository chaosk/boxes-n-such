"""Assemble the simple lidded box and write ``simple_box.3mf``.

Run with ``uv run python -m simple_box``. See README.md for the design.
"""

import sys
from pathlib import Path

# Allow running this file directly / in cq-editor by putting the repo root on the
# path; under ``python -m simple_box`` it is already there.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from insertkit import bambu3mf

from simple_box import config as C
from simple_box.parts import make_box, make_lid

if "show_object" in globals():
    _CQ_EDITOR = True
else:
    _CQ_EDITOR = False
    def show_object(*args, **kwargs):
        return


FILAMENTS = [C.COLOR]


_box = _lid = None


def _ensure_built():
    global _box, _lid
    if _box is None:
        _box = make_box()
        _lid = make_lid()
    return _box, _lid


def describe():
    print(f"box : {C.BOX_W:.1f} x {C.BOX_D:.1f} x {C.BOX_H:.1f} mm outer, "
          f"wall {C.WALL}, floor {C.FLOOR}")
    print(f"lid : {C.BOX_W:.1f} x {C.BOX_D:.1f} x {C.LID_T:.1f} mm, "
          f"tongue {C.TONGUE_H} / channel {C.LIP_DROP}")


def plates():
    """One plate carrying the box and the lid side-by-side."""
    box, lid = _ensure_built()
    return [
        ("box and lid", [
            ("box", [("box", box, 1)]),
            ("lid", [("lid", lid, 1)]),
        ]),
    ]


describe()
if _CQ_EDITOR:
    box, lid = _ensure_built()
    show_object(box, name="box")
    show_object(lid, name="lid")


if __name__ == "__main__":
    out = C.HERE / "simple_box.3mf"
    print("laying out plates…", flush=True)
    placed, plate_members = bambu3mf.plate_layout(plates())
    print(f"tessellating {len(placed)} objects…", flush=True)
    bambu3mf.export_bambu_3mf(placed, FILAMENTS, out, plates=plate_members)
    print(f"exported {out.name} ({len(placed)} objects on {len(plate_members)} plates, "
          f"{len(FILAMENTS)} filaments)")
