# boxes-n-such

Parametric CadQuery models for 3D-printed board-game inserts. Each project is an
importable package that builds its parts and writes a single multi-colour 3MF.

## Projects

| Package                                   | What it makes                                                |
| ----------------------------------------- | ----------------------------------------------------------- |
| [`netrunner_chips`](netrunner_chips/)     | Carrier + trays for a ceramic Netrunner chip set            |
| [`botc_town_stand`](botc_town_stand/)     | Blood on the Clocktower "Base Town" tag board + storage box |
| [`insertkit`](insertkit/)                 | Shared helpers (modelling vocabulary + 3MF export)          |

## Run

```bash
uv sync
uv run python -m netrunner_chips
uv run python -m botc_town_stand
```

Each writes its `.3mf` next to the package (gitignored). Download built files from CI workflow artifacts, or export locally. See each project's README for design notes, and [AGENTS.md](AGENTS.md) for package layout and how CI discovers **build packages**.

## Development

Dependencies are managed with [`uv`](https://docs.astral.sh/uv/). The packages
run in place from the repo root; nothing is pip-installed.
