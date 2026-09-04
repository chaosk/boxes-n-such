"""Part builders: the box body and its lid.

Both parts are built as flat closed outlines that are extruded once, following
the insertkit BRep idiom (see :func:`cqutil.ring`). Booleans are reserved for
the two genuine cavities — the box's well and the lid's underside channel.
"""

from shapely.geometry import box as sbox

from insertkit import cqutil as U

from simple_box import config as C

OUTER = list(sbox(-C.BOX_W / 2, -C.BOX_D / 2, C.BOX_W / 2, C.BOX_D / 2).exterior.coords)


def _touch_fillet(part, r):
    """Round the top-face perimeter edges for a softer grip."""
    if r <= 0:
        return part
    return part.faces(">Z").edges().fillet(r)


def make_box():
    """Return the single-solid open-topped box body with an upstanding rim
    tongue that seats in the lid's underside channel."""
    shell = U.extrude(OUTER, C.BOX_H)
    well = U.offset(OUTER, -C.WALL)
    body = shell.cut(U.extrude(well, C.BOX_H - C.FLOOR + 1, z=C.FLOOR))
    body = _touch_fillet(body, C.EDGE_FILLET)

    # Upstanding tongue on the top rim; two nested offsets set its walls in
    # from the outer edge by TONGUE_CLEAR so it slides into the lid channel
    # with a light press fit on each face.
    t_o = U.offset(OUTER, -0.05 - C.TONGUE_CLEAR)
    t_i = U.offset(OUTER, -(C.WALL + C.LIP_CLEAR) + C.TONGUE_CLEAR)
    tongue = _touch_fillet(U.ring(t_o, t_i, C.TONGUE_H, z=C.BOX_H), C.EDGE_FILLET)
    return body.union(tongue)


def make_lid():
    """Return the single-solid lid: a flat plate whose underside carries a
    channel that receives the box's rim tongue."""
    lid = _touch_fillet(U.extrude(OUTER, C.LID_T), C.EDGE_FILLET)

    # Underside channel matching the box wall footprint, LIP_CLEAR wider so the
    # tongue drops in with room for TONGUE_CLEAR play on each face.
    ch_o = U.offset(OUTER, -0.05)
    ch_i = U.offset(OUTER, -(C.WALL + C.LIP_CLEAR))
    return lid.cut(U.ring(ch_i, ch_o, C.LIP_DROP, z=0))
