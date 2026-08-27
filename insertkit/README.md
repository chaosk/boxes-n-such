# insertkit

Shared toolkit for the parametric board-game insert projects in this repo.

| Module       | What it does                                                                                                                          |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `cqutil.py`  | Generic CadQuery / shapely modelling helpers: flat profiles, rings, outline offsets, stepped rectangles, and TTF text as solids.    |
| `bambu3mf.py`| Single multi-colour 3MF export in the Bambu Studio flavour, with the colours also embedded as 3MF base materials (visible on plain import in any 3MF viewer). |

These follow the BRep idiom of *building a profile and extruding it once* rather
than extruding a slab and cutting it away. Import from the repo root, e.g.:

```python
from insertkit import bambu3mf, cqutil
```
