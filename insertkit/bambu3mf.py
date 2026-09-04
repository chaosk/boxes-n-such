"""Single multi-colour 3MF export in the Bambu Studio flavour.

Model-agnostic: callers pass *groups* of the form

    [(group_name, [(part_name, solid_or_workplane, filament_index), ...]), ...]

where each group becomes one Bambu object built from component parts, and each
part is assigned a filament (extruder). ``tile_layout`` / ``plate_layout``
arrange the groups; ``export_bambu_3mf`` writes the archive.

XML payloads are built with ``xml.etree.ElementTree`` (no string-built tags).
"""

from __future__ import annotations

import json
import math
import zipfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from typing import NamedTuple, Sequence

# 3MF / OPC namespaces
_NS_3MF = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
_NS_BAMBU = "http://schemas.bambulab.com/package/2021"
_NS_PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
_NS_RELS = "http://schemas.openxmlformats.org/package/2006/relationships"
_NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"
_NS_XML = "http://www.w3.org/XML/1998/namespace"

_IDENT = "1 0 0 0 1 0 0 0 1 0 0 0"
_PLATE_GAP = 0.2  # Bambu LOGICAL_PART_PLATE_GAP (bed stride = bed * 1.2)
_ZERO = (0.0, 0.0, 0.0)


class PlacedGroup(NamedTuple):
    """One printable object after layout, with plate-local and absolute origins.

    ``parts`` is ``[(part_name, solid, extruder), ...]``. ``local`` is the
    build-item transform within a plate; ``origin`` is the plate-slot offset
    used in the ``<assemble>`` block.
    """

    name: str
    parts: list
    local: tuple[float, float, float] = _ZERO
    origin: tuple[float, float, float] = _ZERO

    @property
    def world(self) -> tuple[float, float, float]:
        lx, ly, lz = self.local
        ox, oy, _ = self.origin
        return (ox + lx, oy + ly, lz)


class _PartRef(NamedTuple):
    obj_id: int
    name: str
    extruder: int


class _GroupObject(NamedTuple):
    obj_id: int
    name: str
    parts: list[_PartRef]
    world: tuple[float, float, float]
    local: tuple[float, float, float]
    origin: tuple[float, float, float]


class _LayoutItem(NamedTuple):
    name: str
    parts: list
    lx: float
    ly: float
    lz: float
    x: float
    y: float
    w: float
    h: float


def _build_transform(tx: float, ty: float, tz: float) -> str:
    """3×4 row-major affine matrix for a build-item placement."""
    return f"1 0 0 0 1 0 0 0 1 {tx} {ty} {tz}"


def _as_placed(entry) -> PlacedGroup:
    """Accept a ``PlacedGroup`` or a 2–4 tuple from older call sites."""
    if isinstance(entry, PlacedGroup):
        return entry
    name, parts, *rest = entry
    local = rest[0] if len(rest) >= 1 else _ZERO
    origin = rest[1] if len(rest) >= 2 else _ZERO
    return PlacedGroup(name, parts, local, origin)


def _project_settings(filament_colors, printer_model, printer_variant):
    """Bambu project JSON with filament colours and process overrides.

    Bambu Studio shows a one-time warning when opening the file because
    ``different_settings_to_system`` embeds customized process settings.
    """
    n = len(filament_colors)
    nozzle = f"{printer_model} {printer_variant} nozzle"
    # Bambu ignores overrides not listed in different_settings_to_system (slot 0
    # is the process profile; one slot per filament follows).
    process_keys = "enable_prime_tower;skirt_loops;sparse_infill_pattern"
    return {
        "version": "1.0.0.0",
        "printer_model": printer_model,
        "printer_variant": printer_variant,
        "printer_settings_id": nozzle,
        "enable_prime_tower": "1",
        "skirt_loops": "0",
        "sparse_infill_pattern": "gyroid",
        "filament_colour": list(filament_colors),
        "filament_type": ["PLA"] * n,
        "filament_settings_id": [""] * n,
        "different_settings_to_system": [process_keys] + [""] * n,
    }


def _plate_columns(plate_count):
    """Match Bambu PartPlateList::compute_colum_count (ceil(sqrt(n)))."""
    value = math.sqrt(plate_count)
    rounded = round(value)
    return int(rounded) + 1 if value > rounded else int(rounded)


def _plate_origin(plate_idx, plate_count, stride):
    """Top-left corner of a plate slot in Bambu's absolute plate grid."""
    cols = _plate_columns(plate_count)
    row, col = divmod(plate_idx, cols)
    return col * stride, -row * stride


def _solid(part):
    return part.val() if hasattr(part, "val") else part


def bbox(parts):
    """Combined (xmin, ymin, xmax, ymax) of a group's parts."""
    bbs = [_solid(p).BoundingBox() for _, p, _ in parts]
    return (min(b.xmin for b in bbs), min(b.ymin for b in bbs),
            max(b.xmax for b in bbs), max(b.ymax for b in bbs))


def _zmin(parts):
    return min(_solid(p).BoundingBox().zmin for _, p, _ in parts)


def tile_layout(groups, max_w=250.0, gap=8.0):
    """Tile groups across a plate, wrapping rows. Parts within a group keep their
    relative offset so colour parts stay registered with their bodies."""
    placed, x, y, row_h = [], 0.0, 0.0, 0.0
    for gname, parts in groups:
        x0, y0, x1, y1 = bbox(parts)
        w, h = x1 - x0, y1 - y0
        if x > 0 and x + w > max_w:
            x, y, row_h = 0.0, y + row_h + gap, 0.0
        dx, dy = x - x0, y - y0
        # Keep the historical 2-tuple shape so ``for name, parts in …`` still works.
        placed.append((gname, [(pn, _solid(p).translate((dx, dy, 0)), e)
                               for pn, p, e in parts]))
        x += w + gap
        row_h = max(row_h, h)
    return placed


def plate_layout(plates, bed=(256.0, 256.0), gap=8.0):
    """Lay groups out onto separate Bambu plates.

    ``plates`` is ``[(plate_name, [group, ...]), ...]`` where a group is
    ``(group_name, [(part_name, solid, extruder), ...])``. Groups on each plate
    are tiled then the whole block is centred on the bed. Returned transforms
    are plate-local; the matching plate origin goes into the ``<assemble>`` block
    so Bambu can place objects on the correct bed slot.

    Returns ``(placed_groups, plate_members)`` where each placed group is a
    ``PlacedGroup`` and ``plate_members`` is
    ``[(plate_name, [group_name, ...]), ...]``.
    """
    bx = bed[0] if isinstance(bed, tuple) else bed
    by = bed[1] if isinstance(bed, tuple) else bx
    stride = bx * (1.0 + _PLATE_GAP)
    placed: list[PlacedGroup] = []
    plate_members = []
    n_plates = len(plates)
    for idx, (pname, groups) in enumerate(plates):
        ox, oy = _plate_origin(idx, n_plates, stride)
        layouts: list[_LayoutItem] = []
        x, y, row_h = 0.0, 0.0, 0.0
        for gname, parts in groups:
            x0, y0, x1, y1 = bbox(parts)
            w, h = x1 - x0, y1 - y0
            if x > 0 and x + w > bx:
                x, y, row_h = 0.0, y + row_h + gap, 0.0
            layouts.append(_LayoutItem(
                gname, parts, x - x0, y - y0, -_zmin(parts), x, y, w, h,
            ))
            x += w + gap
            row_h = max(row_h, h)
        if layouts:
            min_x = min(item.x for item in layouts)
            max_x = max(item.x + item.w for item in layouts)
            min_y = min(item.y for item in layouts)
            max_y = max(item.y + item.h for item in layouts)
            dx = (bx - (max_x - min_x)) / 2 - min_x
            dy = (by - (max_y - min_y)) / 2 - min_y
            for item in layouts:
                placed.append(PlacedGroup(
                    item.name,
                    [(pn, _solid(p), e) for pn, p, e in item.parts],
                    (item.lx + dx, item.ly + dy, item.lz),
                    (ox, oy, 0.0),
                ))
        plate_members.append((pname, [item.name for item in layouts]))
    return placed, plate_members


def _weld(verts, tris, ndigits=4):
    """Merge coincident vertices and drop degenerate triangles.

    OCC/CadQuery tessellation emits a separate vertex for every face that touches
    a shared edge, so adjacent triangles reference different (but identical) points
    and the mesh reads as non-watertight (Bambu reports thousands of "open edges").
    Snapping to a grid and reindexing welds those seams into a closed manifold.
    """
    index, uniq, remap = {}, [], []
    for v in verts:
        key = (round(v.x, ndigits), round(v.y, ndigits), round(v.z, ndigits))
        i = index.get(key)
        if i is None:
            i = len(uniq)
            index[key] = i
            uniq.append(key)
        remap.append(i)
    out = []
    for a, b, c in tris:
        a, b, c = remap[a], remap[b], remap[c]
        if a != b and b != c and a != c:
            out.append((a, b, c))
    return uniq, out


def _mesh_data(solid, tol=0.06):
    return _weld(*solid.tessellate(tol))


def _qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def _serialize(root: ET.Element) -> str:
    """UTF-8 XML declaration + element tree as a Unicode string."""
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def _mesh_object(verts, tris, obj_id: int) -> ET.Element:
    obj = ET.Element(_qn(_NS_3MF, "object"), {"id": str(obj_id), "type": "model"})
    mesh = ET.SubElement(obj, _qn(_NS_3MF, "mesh"))
    vertices_el = ET.SubElement(mesh, _qn(_NS_3MF, "vertices"))
    for x, y, z in verts:
        ET.SubElement(vertices_el, _qn(_NS_3MF, "vertex"), {
            "x": f"{x:.4f}", "y": f"{y:.4f}", "z": f"{z:.4f}",
        })
    triangles_el = ET.SubElement(mesh, _qn(_NS_3MF, "triangles"))
    for a, b, c in tris:
        ET.SubElement(triangles_el, _qn(_NS_3MF, "triangle"), {
            "v1": str(a), "v2": str(b), "v3": str(c),
        })
    return obj


def _component_object(obj_id: int, parts: Sequence[_PartRef]) -> ET.Element:
    obj = ET.Element(_qn(_NS_3MF, "object"), {"id": str(obj_id), "type": "model"})
    comps = ET.SubElement(obj, _qn(_NS_3MF, "components"))
    for part in parts:
        ET.SubElement(comps, _qn(_NS_3MF, "component"), {
            "objectid": str(part.obj_id),
            "transform": _IDENT,
        })
    return obj


def _meta(parent: ET.Element, name: str, value: str) -> None:
    ET.SubElement(parent, _qn(_NS_3MF, "metadata"), {"name": name}).text = value


def _build_3dmodel(mesh_els: list[ET.Element], group_objs: list[_GroupObject]) -> str:
    """Serialize ``3D/3dmodel.model`` with Bambu recognition markers."""
    ET.register_namespace("", _NS_3MF)
    ET.register_namespace("BambuStudio", _NS_BAMBU)
    ET.register_namespace("p", _NS_PROD)

    model = ET.Element(_qn(_NS_3MF, "model"), {
        "unit": "millimeter",
        _qn(_NS_XML, "lang"): "en-US",
        # Prefix declarations so Bambu/Orca recognise the package flavour
        # (they are not used as element tags, so register_namespace alone
        # would omit them).
        "xmlns:BambuStudio": _NS_BAMBU,
        "xmlns:p": _NS_PROD,
    })
    # Bambu only runs its native loader (which reads model_settings.config for the
    # per-part filament assignments) when the file is recognised as a Bambu/Orca
    # project. These markers trigger that path; without them it imports as a plain
    # 3MF and drops the per-part colours (everything lands on filament 1).
    _meta(model, "Application", "BambuStudio-01.10.00.00")
    _meta(model, "BambuStudio:3mfVersion", "1")
    _meta(model, "slic3rpe:Version3mf", "1")

    resources = ET.SubElement(model, _qn(_NS_3MF, "resources"))
    for el in mesh_els:
        resources.append(el)
    for group in group_objs:
        resources.append(_component_object(group.obj_id, group.parts))

    build = ET.SubElement(model, _qn(_NS_3MF, "build"))
    for group in group_objs:
        ET.SubElement(build, _qn(_NS_3MF, "item"), {
            "objectid": str(group.obj_id),
            "transform": _build_transform(*group.world),
            "printable": "1",
        })
    return _serialize(model)


def _cfg_meta(parent: ET.Element, key: str, value: str) -> None:
    ET.SubElement(parent, "metadata", {"key": key, "value": value})


def _build_model_settings(
    group_objs: list[_GroupObject],
    plates: list | None,
    printer_model: str,
) -> str:
    """Serialize ``Metadata/model_settings.config`` (no XML namespaces)."""
    cfg = ET.Element("config")
    for group in group_objs:
        obj = ET.SubElement(cfg, "object", {"id": str(group.obj_id)})
        _cfg_meta(obj, "name", group.name)
        _cfg_meta(obj, "extruder", str(group.parts[0].extruder))
        for part in group.parts:
            part_el = ET.SubElement(obj, "part", {
                "id": str(part.obj_id),
                "subtype": "normal_part",
            })
            _cfg_meta(part_el, "name", part.name)
            _cfg_meta(part_el, "extruder", str(part.extruder))

    name_to_goid = {g.name: g.obj_id for g in group_objs}
    identify_id = 1
    for pid, (pname, gnames) in enumerate(plates or [], start=1):
        plate = ET.SubElement(cfg, "plate")
        _cfg_meta(plate, "plater_id", str(pid))
        _cfg_meta(plate, "plater_name", pname)
        _cfg_meta(plate, "printer_model_id", printer_model)
        _cfg_meta(plate, "locked", "false")
        for gname in gnames:
            inst = ET.SubElement(plate, "model_instance")
            _cfg_meta(inst, "object_id", str(name_to_goid[gname]))
            _cfg_meta(inst, "instance_id", "0")
            _cfg_meta(inst, "identify_id", str(identify_id))
            identify_id += 1

    if plates:
        assemble = ET.SubElement(cfg, "assemble")
        for group in group_objs:
            ox, oy, oz = group.origin
            ET.SubElement(assemble, "assemble_item", {
                "object_id": str(group.obj_id),
                "instance_id": "0",
                "transform": _build_transform(*group.local),
                "offset": f"{ox:.4f} {oy:.4f} {oz:.4f}",
            })
    return _serialize(cfg)


def _content_types_xml() -> str:
    ET.register_namespace("", _NS_CT)
    types = ET.Element(_qn(_NS_CT, "Types"))
    ET.SubElement(types, _qn(_NS_CT, "Default"), {
        "Extension": "rels",
        "ContentType": "application/vnd.openxmlformats-package.relationships+xml",
    })
    ET.SubElement(types, _qn(_NS_CT, "Default"), {
        "Extension": "model",
        "ContentType": "application/vnd.ms-package.3dmanufacturing-3dmodel+xml",
    })
    return _serialize(types)


def _rels_xml() -> str:
    ET.register_namespace("", _NS_RELS)
    rels = ET.Element(_qn(_NS_RELS, "Relationships"))
    ET.SubElement(rels, _qn(_NS_RELS, "Relationship"), {
        "Target": "/3D/3dmodel.model",
        "Id": "rel-1",
        "Type": "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel",
    })
    return _serialize(rels)


def export_bambu_3mf(groups, filament_colors, path, plates=None,
                     printer_model="Bambu Lab P1S", printer_variant="0.4"):
    """Write ``groups`` to ``path`` as a Bambu multi-colour 3MF.

    Filament colours go into project_settings.config; per-part extruder
    assignments go into model_settings.config. If ``plates`` is given (as
    ``[(plate_name, [group_name, ...]), ...]``) the objects are split across that
    many Bambu plates; otherwise everything lands on a single plate.

    Each entry in ``groups`` may be a ``PlacedGroup`` or a 2–4 tuple
    ``(name, parts[, local[, origin]])``.
    """
    mesh_jobs: list[tuple[int, object]] = []
    group_objs: list[_GroupObject] = []
    next_id = 1
    for entry in groups:
        placed = _as_placed(entry)
        refs: list[_PartRef] = []
        for pname, part, extruder in placed.parts:
            print(f"  {placed.name}/{pname}…", flush=True)
            mesh_jobs.append((next_id, _solid(part)))
            refs.append(_PartRef(next_id, pname, extruder))
            next_id += 1
        group_objs.append(_GroupObject(
            next_id, placed.name, refs, placed.world, placed.local, placed.origin,
        ))
        next_id += 1

    unique_solids = list({id(s): s for _, s in mesh_jobs}.values())
    tess_cache: dict[int, tuple] = {}
    with ThreadPoolExecutor() as pool:
        for solid, data in zip(unique_solids, pool.map(_mesh_data, unique_solids)):
            tess_cache[id(solid)] = data
    mesh_els = [
        _mesh_object(*tess_cache[id(solid)], obj_id)
        for obj_id, solid in mesh_jobs
    ]

    model = _build_3dmodel(mesh_els, group_objs)
    model_settings = _build_model_settings(group_objs, plates, printer_model)
    project = json.dumps(
        _project_settings(filament_colors, printer_model, printer_variant), indent=1)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _content_types_xml())
        z.writestr("_rels/.rels", _rels_xml())
        z.writestr("3D/3dmodel.model", model)
        z.writestr("Metadata/model_settings.config", model_settings)
        z.writestr("Metadata/project_settings.config", project)
