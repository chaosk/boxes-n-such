# simple_box — a simple parametric lidded box

A no-frills rectangular box with a friction-fit lid. The box body prints
open-topped with an upstanding tongue running around its rim; the lid is a
flat plate whose underside carries a matching channel, so lid drops on and
seats with a light press-fit set by named clearances in `config.py`
(`LIP_CLEAR`, `TONGUE_CLEAR`).

All dimensions live in `config.py`, in millimetres. Both parts are built as
closed outlines extruded once via `insertkit.cqutil` (walls as an offset
outline, the tongue and channel as `ring`s) — the only booleans are the box
well and the lid channel. A single-filament Bambu 3MF is written next to the
package via `insertkit.bambu3mf`.

## Layout

| File          | Role                                             |
| ------------- | ------------------------------------------------ |
| `config.py`   | all parameters                                   |
| `parts.py`    | `make_box()` and `make_lid()` builders           |
| `__main__.py` | assembles the parts and writes `simple_box.3mf` |

## Run

```bash
uv run python -m simple_box
```

Writes `simple_box.3mf` (box + lid on one plate) next to the package
(gitignored; also available as a CI artifact).
