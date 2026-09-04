# Blood on the Clocktower — "Base Town" tag stand

Inspired by https://makerworld.com/en/models/2388995-blood-on-the-clocktower-base-town-stand?from=search#profileId-2616888

## Design

The board face is black with a two-tier stepped lavender frame and four plain
tag-shaped pockets. You push the numbered tags for the current player count into
the pockets (the tags carry their own category-coloured border); the spares live
in the box underneath.

## Print notes

Print the board part with supports enabled.

## Tag set (Trouble Brewing)

| Category  | Numbers | Colour |
| --------- | ------- | ------ |
| Townsfolk | 3/5/7/9 | blue   |
| Outsiders | 0/1/2   | cyan   |
| Minions   | 1/2/3   | orange |
| Demon     | 1       | red    |

## Layout

| File          | Role                                            |
| ------------- | ----------------------------------------------- |
| `config.py`   | all parameters                                  |
| `parts.py`    | tag / board / box builders                      |
| `__main__.py` | assembles the parts and writes `town_stand.3mf` |

Shared helpers live in the `insertkit` package (`cqutil` for the modelling
vocabulary, `bambu3mf` for the multi-colour 3MF export).

## Run

```bash
uv run python -m botc_town_stand
```

Writes `town_stand.3mf` (box + board + tags) next to the package (gitignored; also available as a CI artifact).
