# boxes-n-such — agent instructions

CadQuery (and legacy OpenSCAD) 3D models for board-game box inserts and related printables.

## Stack choice

- **Prefer CadQuery** for all new inserts and parts. Match `cosmic_encounter/`.
- **Do not expand OpenSCAD / Boardgame Insert Toolkit** (`frostpunk/`, `vendor/`) unless an issue explicitly says so. Treat Frostpunk as legacy reference only.

## Package layout (CadQuery)

One Python package per game, sibling to `cosmic_encounter/`:

```text
<game>/
  __init__.py          # optional
  kit.py               # shared Part / Project helpers (copy or import patterns from CE)
  main.py              # CQ-editor entry: builds Project, calls show_object
  player_box.py        # optional standalone scripts (lids, player boxes)
  parts/
    __init__.py        # export Part subclasses
    <component>.py     # one Part class per file
```

Reference implementation: `cosmic_encounter/` (`kit.py`, `parts/aliens.py`, `parts/cards.py`, `main.py`, `player_box.py`).

## Part / Project kit

Use the small kit in `cosmic_encounter/kit.py`:

- **`Part`** — subclass with `make()` returning `Workplane`s or named `Object`s. Named objects become assembly members.
- **`Project`** — holds parts + a `show_object` callable; builds a CadQuery `Assembly` and `.show()` for CQ-editor.
- **`Object`** — `name` + `workplane` pair for multi-solid parts.

Wire parts in `main.py` like Cosmic Encounter:

```python
from .kit import Project
from .parts import Aliens, Cards

def do():
    return Project((Aliens("aliens"), Cards("cards_1")), show_object=show_object)
```

`show_object` is provided by CQ-editor (or a stub in headless runs). Prefer named parts so exports stay identifiable.

## Modelling conventions

- **API**: fluent CadQuery `Workplane` API (`import cadquery as cq`). Do not mix free-function API in the same script unless converting explicitly.
- **Units**: millimetres everywhere.
- **Shells**: thin walls ~**1.5 mm** (`.faces("+Z").shell(1.5)`).
- **Outer edges**: light fillets on vertical edges (typically ~**1 mm**); small fillets (~0.4 mm) where faces meet.
- **Finger / side cutouts**: `cq.Sketch` (rect, trapezoid) + fillets on vertices, then `.cutThruAll()` / `.cutBlind("next")`. Side cutouts often offset slightly (e.g. `.center(0, 1)`) so the top opens without cutting the bottom rim.
- **Ergonomics**: finger wells and side openings so cards/tokens lift out without fighting the shell.
- **Dimensions**: measure components; leave slight clearance for print tolerance (see lid clearance in `player_box.py`: lid cut slightly oversized).

Load the workspace **cadquery-llm-skill** for idiomatic BRep / selector / shell patterns. Prefer selecting faces/edges and shelving over CSG piles of unions/cuts when possible; cuts for finger wells and component pockets are normal for inserts.

## Export / print workflow

- Iterate in **CQ-editor** with `show_object` / `Project.show()`.
- Export STL (or STEP/3MF) locally for slicing — **never commit `*.stl`** (gitignored).
- Headless export is fine when CadQuery/OCP is installed: build the `Workplane`/`Assembly`, then `cq.exporters.export(...)`. Do not rely on CQ-editor for CI.
- Validate fits with test prints before locking dimensions.

## Git / commits

- Sign every commit (`git commit -S` / `commit.gpgsign`). Never leave unsigned commits.
- Do not commit secrets, credentials, or generated meshes (`*.stl`).
- Keep PRs focused on one game package or shared kit change.

## Adding a new game insert

1. Create `<game>/` with `kit.py` (reuse CE patterns), `parts/`, and `main.py`.
2. Add `Part` subclasses for each printable (tray, card well, lid).
3. Register parts in `main.py` via `Project` + `show_object`.
4. Keep Frostpunk/OpenSCAD untouched unless the issue requires legacy work.
5. Smoke-check geometry in CQ-editor (or headless export if available); leave STLs untracked.
