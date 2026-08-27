"""Shared toolkit for the parametric board-game insert projects.

Modules:
  * ``cqutil``   - generic CadQuery / shapely modelling helpers (profiles,
    rings, offsets, stepped rectangles, TTF text).
  * ``bambu3mf`` - single multi-colour 3MF export in the Bambu Studio flavour,
    with the colours also embedded as 3MF base materials.
"""

from . import bambu3mf, cqutil

__all__ = ["bambu3mf", "cqutil"]
