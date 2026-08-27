# boxes-n-such — agent instructions

Parametric CadQuery models for 3D-printed board-game inserts and related printables.

## Canonical reference (newest first)

| Path | Role |
| --- | --- |
| **`botc_town_stand/`** | **Preferred pattern** for new CadQuery work (config / parts / `__main__`, multi-colour 3MF). |
| **`insertkit/`** | Shared helpers: `cqutil` (profiles, rings, offsets, text) and `bambu3mf` (Bambu multi-colour 3MF). |
| `cosmic_encounter/` | Older CadQuery (`Part` / `Project` kit, STL-oriented). Prefer BotC + insertkit for new packages. |
| `frostpunk/`, `vendor/` | Legacy OpenSCAD + Boardgame Insert Toolkit — do not expand unless an issue says so. |

## Tooling

- Python **≥ 3.11**, managed with **`uv`** (`pyproject.toml` + `uv.lock`).
- Dependencies: `cadquery`, `shapely`, `matplotlib`; optional `cq-editor` in the `dev` group.
- Repo is not an installable package (`tool.uv.package = false`). Run from the **repo root**:

```bash
uv run python -m botc_town_stand
```

- CQ-editor: open `__main__.py`; scripts stub `show_object` when it is not injected.
- Never commit `*.stl` (root `.gitignore`). Multi-colour **`.3mf`** exports may live beside the package when that is the deliverable (see `botc_town_stand/town_stand.3mf`).
- Sign every commit (`git commit -S`). Do not commit secrets.

## New package layout (match BotC)

```text
<game>/
  README.md       # design intent, how to run
  config.py       # all parameters (mm); builders stay declarative
  parts.py        # builders returning solids / colour-split parts
  __main__.py     # assemble, CQ-editor preview, export 3MF
  __init__.py
```

Import shared code as `from insertkit import cqutil, bambu3mf` (repo root on `sys.path`; `__main__.py` may insert the root when opened directly / in CQ-editor).

## Modelling conventions

- **Units:** millimetres. Put every tunable in `config.py` (sizes, clearances, colours, font paths).
- **API:** fluent CadQuery `Workplane`, plus shapely outlines in `cqutil`.
- **BRep idiom (insertkit):** build a closed **profile**, then **extrude once**. Prefer `cqutil.face` / `extrude` / `ring` / `offset` / `notched_rect` / `stepped_rect` / `text_solid` over “extrude a slab then carve everything away.”
- **Booleans:** reserve `.cut` / `.union` for genuine cavities (pockets, wells, slots) and for combining separate colour solids — not as the default construction style.
- **Multi-colour:** one solid (or Workplane) per filament colour; group parts for `bambu3mf.plate_layout` / `export_bambu_3mf` with filament hex colours and extruder indices.
- **Clearances:** name them in config (e.g. press-fit peg vs hole, lid channel / tongue, pocket oversize). Document intent in comments next to the constants.
- **Ergonomics:** finger notches, pegs, lead-ins, and print orientation (e.g. lid face-up with underside channel) belong in the design parameters, not as afterthoughts.

Load the workspace **cadquery-llm-skill** for general CadQuery / BRep patterns. Prefer selecting faces/edges and profile extrusion; avoid CSG reflex when `cqutil.ring` / offset profiles suffice.

## Export / print workflow

1. Iterate parameters in `config.py`; rebuild with `uv run python -m <package>` or CQ-editor `show_object`.
2. Export multi-colour Bambu 3MF via `insertkit.bambu3mf` (plates, filament colours, welded meshes).
3. Slice in Bambu Studio (or equivalent). Keep generated STLs untracked.

## Adding a new insert / printable

1. Add `<game>/` with `config.py`, `parts.py`, `__main__.py`, and a short README.
2. Reuse `insertkit.cqutil` for profiles/rings/text; use `insertkit.bambu3mf` if the print is multi-colour.
3. Do not copy `cosmic_encounter/kit.py` for new work unless an issue requires matching that older style.
4. Leave OpenSCAD / BIT alone unless asked.
5. Smoke-check with `uv run` (needs CadQuery/OCP via uv) or CQ-editor on a machine that has them.

## Older Cosmic Encounter notes (legacy CadQuery)

Still valid if editing CE only: per-game `kit.py` (`Part` / `Project` / `Object`), `parts/` modules, ~1.5 mm `.shell()`, Sketch finger cutouts, CQ-editor `show_object`. Prefer migrating new games to the BotC + insertkit layout above.
