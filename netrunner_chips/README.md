# Netrunner chip carrier

Carrier + shallow trays for the Neon Static / BR Pro Poker ceramic Netrunner
chip set, sized for the **main compartment** of the Gamegenic
["The Academic 133+ XL"](https://www.gamegenic.com/product/the-academic-133-xl/)
deck box (~113 × 86 mm, ~109 mm deep, opening at the top).

## Design

Each tray is a solid-bottomed pan: chips sit on edge in cradles cut into a solid
floor (circular side walls that cup the chip, with the shallow round bottom
replaced by a dropped flat relief so nothing prints as a wavy top), standing
proud of the low walls so they show and can be flipped through. The whole bottom
is solid, so a tray prints on the bed with no support.

A central "pole" (a thin blade spine) threads up through all the trays and the
dice cap: it carries the whole stack out of the deep box in one grab and keeps
the tiers square, locating each tray through its blade slot. The pole prints as
a separate part — a plain flat sheet lying on its big face — dropped into a
straight slot in the base plate and locked by a horizontal cross-pin through
plate and pole.

The dice cap sits on the top chip tray, presses the chips down, and fills the
remaining compartment height. Two dice wells flank the pole slot; the centre
walls are cut down at grip height so the pole handle stays reachable.

Chips are grouped by type with low dividers, and small molded bumps mark every 5
credits.

## Assembly notes

Place carrier pole on top of carrier base, push a strand of 1.75 mm filament
through the hole in the carrier base to lock them together.

Tray A goes on the bottom, tray B on top, dice cover on top of tray B (pole
through all three).

## Chips

Ceramic chips: 39 mm diameter, 3.4 mm thick (standard casino size).

Ceramic set (74): 30× credit-1, 10× credit-5, 6× bad-pub, 8× click,
10× tag/core, 10× virus/power.

## Layout

| File          | Role                                          |
| ------------- | --------------------------------------------- |
| `config.py`   | all parameters                                |
| `parts.py`    | tray / carrier builders + edge split          |
| `__main__.py` | assembles the parts and writes `chip_set.3mf` |

Shared helpers live in the `insertkit` package (`bambu3mf` for the multi-colour
3MF export).

## Run

```bash
uv run python -m netrunner_chips
```

Writes `chip_set.3mf` (carrier base + pole + tray A + tray B + dice cover) next to
the package.

## Sources

- https://neonstaticpod.com/poker_chips
- https://www.gamegenic.com/product/the-academic-133-xl/
