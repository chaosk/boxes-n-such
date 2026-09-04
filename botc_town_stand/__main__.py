"""Assemble the Base Town tag board + storage box and write town_stand.3mf.

Run with ``uv run python -m botc_town_stand``. See README.md for the design,
the tag set, and the file layout.
"""

import sys
from pathlib import Path

# Allow running this file directly / in cq-editor by putting the repo root on the
# path; under `python -m botc_town_stand` it is already there.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import cadquery as cq

from insertkit import bambu3mf

from botc_town_stand import config as C
from botc_town_stand.parts import make_board, make_box, make_tag, seat_location

if "show_object" in globals():
    _CQ_EDITOR = True
else:
    _CQ_EDITOR = False
    def show_object(*args, **kwargs):
        return


# --------------------------------------------------------------------------- #
# Build (lazy — skip heavy CadQuery work on import unless preview/export runs)
# --------------------------------------------------------------------------- #

_board = _box = _tags = None


def _ensure_built():
    global _board, _box, _tags
    if _tags is None:
        _board = make_board()
        _box = make_box()
        _tags = [(cat, num, col, make_tag(num)) for cat, num, col in C.ALL_TAGS]
    return _board, _box, _tags


def describe():
    print(f"board (lid) : {C.BOARD_W:.1f} x {C.BOARD_H:.1f} mm plaque + {C.FOOT_EXT:.0f} mm "
          f"foot, face {C.FACE_T} + frame {C.FRAME_R1}/{C.FRAME_R2}, "
          f"{C.N_POCKET} pockets @ {C.POCKET_PITCH}")
    print(f"box         : {C.BOARD_W:.1f} x {C.BOARD_H:.1f} x {C.BOX_H:.1f} mm "
          f"(well {C.BOX_INNER_DEPTH}), stand lean {C.LEAN_DEG:.0f} deg")
    print(f"tags        : {len(C.ALL_TAGS)} @ {C.TAG_W} x {C.TAG_H} x {C.TAG_T}")


# --------------------------------------------------------------------------- #
# Colours / 3MF grouping
# --------------------------------------------------------------------------- #

# filament 1..6 -> colour; each part references one filament (extruder)
FILAMENTS = [C.BLACK, C.LAVENDER] + [col for _, _, col in C.CATEGORIES]


def _ext(hexcol):
    return FILAMENTS.index(hexcol) + 1


def _tag_groups(category):
    """The printable-object groups for every tag in one category."""
    out = []
    for cat, num, col, (body, colour) in _ensure_built()[2]:
        if cat != category:
            continue
        name = f"tag_{cat}_{num.replace('?', 'q')}"
        out.append((name, [(f"{name}_body", body, _ext(C.BLACK)),
                           (f"{name}_num", colour, _ext(col))]))
    return out


def plates():
    """One Bambu plate per tag category, plus a plate for the box and the lid."""
    board, box, _ = _ensure_built()
    return [
        ("demon", _tag_groups("DEMON")),
        ("minions", _tag_groups("MINIONS")),
        ("townsfolk", _tag_groups("TOWNSFOLK")),
        ("outsiders", _tag_groups("OUTSIDERS")),
        ("box and lid", [
            ("box", [("box", box, _ext(C.BLACK))]),
            ("board", [("board_body", board["body"], _ext(C.BLACK)),
                       ("board_frame", board["frame"], _ext(C.LAVENDER))]),
        ]),
    ]


# --------------------------------------------------------------------------- #
# Preview (cq-editor)
# --------------------------------------------------------------------------- #

def _rgb(hexcol):
    h = hexcol.lstrip("#")
    return cq.Color(*[int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def demo_assembly():
    """Playing mode: board standing upright in the box slot with a 7-player town
    shown; spares would live in the compartment behind it."""
    board, box, tags = _ensure_built()
    seat = seat_location()
    asm = cq.Assembly(name="botc")
    asm.add(box, name="box", color=_rgb(C.BLACK))
    asm.add(board["body"], name="board", color=_rgb(C.BLACK), loc=seat)
    asm.add(board["frame"], name="frame", color=_rgb(C.LAVENDER), loc=seat)

    shown = {"TOWNSFOLK": "7", "OUTSIDERS": "0", "MINIONS": "2", "DEMON": "1"}
    tag_by_num = {num: (body, colour) for _, num, _, (body, colour) in tags}
    for x, (cat, _, col) in zip(C.POCKET_XS, C.CATEGORIES):
        body, colour = tag_by_num[shown[cat]]
        loc = seat * cq.Location((x, 0, C.FACE_T - C.POCKET_DEPTH))
        asm.add(body, name=f"tag_{cat}", color=_rgb(C.BLACK), loc=loc)
        asm.add(colour, name=f"num_{cat}", color=_rgb(col), loc=loc)
    return asm


describe()
if _CQ_EDITOR:
    show_object(demo_assembly(), name="botc")


if __name__ == "__main__":
    out = C.HERE / "town_stand.3mf"
    print("laying out plates…", flush=True)
    placed, plate_members = bambu3mf.plate_layout(plates())
    print(f"tessellating {len(placed)} objects…", flush=True)
    bambu3mf.export_bambu_3mf(placed, FILAMENTS, out, plates=plate_members)
    print(f"exported {out.name} ({len(placed)} objects on {len(plate_members)} plates, "
          f"{len(FILAMENTS)} filaments)")
