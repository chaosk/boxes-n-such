"""Generic CadQuery / shapely helpers, free of any model-specific parameters.

Parts that are built from flat closed outlines - offset, stepped, and extruded -
share this vocabulary. The helpers follow the BRep idiom of *building a profile
and extruding it once* rather than extruding a slab and cutting it away.
"""

import functools

import cadquery as cq
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MplPath
from matplotlib.textpath import TextPath
from shapely.geometry import Point, Polygon, box as sbox
from shapely.ops import unary_union

Pts = list  # a list of (x, y) tuples describing a closed outline


def face(pts, z=0.0):
    """A Workplane holding the closed outline ``pts`` at height ``z``."""
    return cq.Workplane(cq.Plane(origin=(0, 0, z))).polyline(pts).close()


def extrude(pts, height, z=0.0):
    """Solid prism of outline ``pts``, ``height`` tall, based at ``z``."""
    return face(pts, z).extrude(height)


def ring(outer, inner, height, z=0.0):
    """Solid ring/wall between ``outer`` and ``inner`` outlines, extruded once.

    Two nested closed wires on one workplane give a face with a hole (even-odd
    rule), so a single ``extrude`` yields the ring - no boolean subtraction.
    ``inner`` must lie wholly inside ``outer``.
    """
    return face(outer, z).polyline(inner).close().extrude(height)


def offset(pts, d):
    """Offset a closed outline by ``d`` (negative = inward), keeping the steps.

    A mitre join preserves the square pixel corners; if the inward offset splits
    the polygon, the largest piece is returned.
    """
    p = Polygon(pts).buffer(d, join_style=2)
    if p.geom_type == "MultiPolygon":
        p = max(p.geoms, key=lambda g: g.area)
    return list(p.exterior.coords)


def notched_rect(w, h, r, quad_segs=48):
    """A ``w`` x ``h`` rectangle with a circle of radius ``r`` subtracted from
    each corner, giving four concave quarter-circle "plaque" corners."""
    g = sbox(-w / 2, -h / 2, w / 2, h / 2)
    for sx in (1, -1):
        for sy in (1, -1):
            g = g.difference(Point(sx * w / 2, sy * h / 2).buffer(r, quad_segs=quad_segs))
    return list(g.exterior.coords)


def stepped_rect(w, h, step, n):
    """A ``w`` x ``h`` rectangle with ``n`` square steps cut from each corner."""
    a, b = w / 2, h / 2
    poly = sbox(-a, -b, a, b)
    cuts = []
    for sx in (1, -1):
        for sy in (1, -1):
            for i in range(n):
                x0, x1 = sx * a - sx * (n - i) * step, sx * a
                y0, y1 = sy * b - sy * (i + 1) * step, sy * b
                cuts.append(sbox(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
    return list(poly.difference(unary_union(cuts)).exterior.coords)


def _bezier(p0, p1, p2, p3, n):
    return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0]
             + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0],
             (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1]
             + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1])
            for t in (k / n for k in range(1, n + 1))]


def _quad(p0, p1, p2, n):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])
            for t in (k / n for k in range(1, n + 1))]


@functools.lru_cache(maxsize=32)
def _glyph_geom(txt, size, font_path, curve_steps):
    """Flatten the glyph run ``txt`` into a shapely (multi)polygon with holes.

    CadQuery's ``text()`` ignores ``fontPath`` on this platform and falls back to
    a default font, so glyph outlines are taken straight from the TTF via
    matplotlib and bezier segments are flattened by hand for a smooth contour.
    """
    tp = TextPath((0, 0), txt, size=size, prop=FontProperties(fname=font_path))
    verts, codes = tp.vertices, tp.codes
    contours, cur, last, i = [], [], (0.0, 0.0), 0
    while i < len(codes):
        code = codes[i]
        if code == MplPath.MOVETO:
            if cur:
                contours.append(cur)
            cur, last, i = [tuple(verts[i])], tuple(verts[i]), i + 1
        elif code == MplPath.LINETO:
            cur.append(tuple(verts[i])); last = tuple(verts[i]); i += 1
        elif code == MplPath.CURVE3:
            p1, p2 = tuple(verts[i]), tuple(verts[i + 1])
            cur += _quad(last, p1, p2, curve_steps); last = p2; i += 2
        elif code == MplPath.CURVE4:
            p1, p2, p3 = tuple(verts[i]), tuple(verts[i + 1]), tuple(verts[i + 2])
            cur += _bezier(last, p1, p2, p3, curve_steps); last = p3; i += 3
        else:  # CLOSEPOLY
            if cur:
                contours.append(cur); cur = []
            i += 1
    if cur:
        contours.append(cur)

    rings = sorted((Polygon(c).buffer(0) for c in contours if len(c) >= 3),
                   key=lambda p: p.area, reverse=True)
    geom = None
    for r in rings:
        if geom is None:
            geom = r
        elif geom.contains(r.representative_point()):
            geom = geom.difference(r)   # interior ring -> hole
        else:
            geom = geom.union(r)        # separate glyph
    return geom


def text_solid(txt, size, depth, font_path, origin=(0.0, 0.0, 0.0), curve_steps=16):
    """Embossed text as a standalone Shape, centred over ``origin`` and rising
    ``depth`` in +Z from ``origin``'s z."""
    geom = _glyph_geom(txt, size, font_path, curve_steps)
    minx, miny, maxx, maxy = geom.bounds
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2

    solid = None
    for g in (geom.geoms if geom.geom_type == "MultiPolygon" else [geom]):
        wp = cq.Workplane("XY").polyline(
            [(x - cx, y - cy) for x, y in g.exterior.coords[:-1]]).close()
        for hole in g.interiors:
            wp = wp.polyline([(x - cx, y - cy) for x, y in hole.coords[:-1]]).close()
        part = wp.extrude(depth)
        solid = part if solid is None else solid.union(part)
    return solid.translate(origin).val()
