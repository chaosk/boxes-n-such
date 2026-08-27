"""Single multi-colour 3MF export in the Bambu Studio flavour.

Model-agnostic: callers pass *groups* of the form

    [(group_name, [(part_name, solid_or_workplane, filament_index), ...]), ...]

where each group becomes one Bambu object built from component parts, and each
part is assigned a filament (extruder). ``tile_layout`` arranges the groups on
the plate; ``export_bambu_3mf`` writes the archive.
"""

import json
import math
import zipfile

_IDENT = "1 0 0 0 1 0 0 0 1 0 0 0"
_PLATE_GAP = 0.2  # Bambu LOGICAL_PART_PLATE_GAP (bed stride = bed * 1.2)


def _build_transform(tx, ty, tz):
    """3×4 row-major affine matrix for a build-item placement."""
    return f"1 0 0 0 1 0 0 0 1 {tx} {ty} {tz}"


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

    Returns ``(placed_groups, plate_members)`` where each placed group is
    ``(name, parts, (lx, ly, lz), (ox, oy, oz))`` and ``plate_members`` is
    ``[(plate_name, [group_name, ...]), ...]``.
    """
    bx = bed[0] if isinstance(bed, tuple) else bed
    by = bed[1] if isinstance(bed, tuple) else bx
    stride = bx * (1.0 + _PLATE_GAP)
    placed, plate_members = [], []
    n_plates = len(plates)
    for idx, (pname, groups) in enumerate(plates):
        ox, oy = _plate_origin(idx, n_plates, stride)
        layouts, x, y, row_h = [], 0.0, 0.0, 0.0
        for gname, parts in groups:
            x0, y0, x1, y1 = bbox(parts)
            w, h = x1 - x0, y1 - y0
            if x > 0 and x + w > bx:
                x, y, row_h = 0.0, y + row_h + gap, 0.0
            layouts.append((gname, parts, x - x0, y - y0, -_zmin(parts), x, y, w, h))
            x += w + gap
            row_h = max(row_h, h)
        if layouts:
            min_x = min(item[5] for item in layouts)
            max_x = max(item[5] + item[7] for item in layouts)
            min_y = min(item[6] for item in layouts)
            max_y = max(item[6] + item[8] for item in layouts)
            dx = (bx - (max_x - min_x)) / 2 - min_x
            dy = (by - (max_y - min_y)) / 2 - min_y
            for gname, parts, lx, ly, lz, *_ in layouts:
                placed.append((gname,
                               [(pn, _solid(p), e) for pn, p, e in parts],
                               (lx + dx, ly + dy, lz),
                               (ox, oy, 0.0)))
        plate_members.append((pname, [g for g, *_ in layouts]))
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


def _mesh_xml(solid, obj_id, tol=0.06):
    verts, tris = _weld(*solid.tessellate(tol))
    vtx = "".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in verts)
    tri = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tris)
    return (f'<object id="{obj_id}" type="model"><mesh>'
            f'<vertices>{vtx}</vertices><triangles>{tri}</triangles></mesh></object>')


def export_bambu_3mf(groups, filament_colors, path, plates=None,
                     printer_model="Bambu Lab P1S", printer_variant="0.4"):
    """Write ``groups`` to ``path`` as a Bambu multi-colour 3MF.

    Filament colours go into project_settings.config; per-part extruder
    assignments go into model_settings.config. If ``plates`` is given (as
    ``[(plate_name, [group_name, ...]), ...]``) the objects are split across that
    many Bambu plates; otherwise everything lands on a single plate.
    """
    meshes, group_objs, next_id = [], [], 1
    for entry in groups:
        if len(entry) >= 4:
            gname, parts, local, origin = entry[:4]
        elif len(entry) == 3:
            gname, parts, local = entry
            origin = (0.0, 0.0, 0.0)
        else:
            gname, parts = entry
            local = (0.0, 0.0, 0.0)
            origin = (0.0, 0.0, 0.0)
        lx, ly, lz = local
        ox, oy, oz = origin
        world = (ox + lx, oy + ly, lz)
        refs = []
        for pname, part, extruder in parts:
            print(f"  {gname}/{pname}…", flush=True)
            meshes.append(_mesh_xml(_solid(part), next_id))
            refs.append((next_id, pname, extruder))
            next_id += 1
        comps = "".join(f'<component objectid="{oid}" transform="{_IDENT}"/>'
                        for oid, _, _ in refs)
        group_objs.append((next_id, gname, refs, comps, world, local, origin))
        next_id += 1

    resources = "".join(meshes) + "".join(
        f'<object id="{goid}" type="model"><components>{comps}</components></object>'
        for goid, _, _, comps, _, _, _ in group_objs)
    build = "".join(
        f'<item objectid="{goid}" transform="{_build_transform(*world)}" printable="1"/>'
        for goid, _, _, _, world, _, _ in group_objs)
    # Bambu only runs its native loader (which reads model_settings.config for the
    # per-part filament assignments) when the file is recognised as a Bambu/Orca
    # project. These markers trigger that path; without them it imports as a plain
    # 3MF and drops the per-part colours (everything lands on filament 1).
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
        'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06">'
        '<metadata name="Application">BambuStudio-01.10.00.00</metadata>'
        '<metadata name="BambuStudio:3mfVersion">1</metadata>'
        '<metadata name="slic3rpe:Version3mf">1</metadata>'
        f'<resources>{resources}</resources><build>{build}</build></model>')

    cfg = ['<?xml version="1.0" encoding="UTF-8"?>', "<config>"]
    for goid, gname, refs, _, _, _, _ in group_objs:
        cfg.append(f'  <object id="{goid}">')
        cfg.append(f'    <metadata key="name" value="{gname}"/>')
        cfg.append(f'    <metadata key="extruder" value="{refs[0][2]}"/>')
        for oid, pname, extruder in refs:
            cfg.append(f'    <part id="{oid}" subtype="normal_part">')
            cfg.append(f'      <metadata key="name" value="{pname}"/>')
            cfg.append(f'      <metadata key="extruder" value="{extruder}"/>')
            cfg.append("    </part>")
        cfg.append("  </object>")
    # plate assignments: which objects live on which plate (1-based plater_id)
    name_to_goid = {gname: goid for goid, gname, _, _, _, _, _ in group_objs}
    identify_id = 1
    for pid, (pname, gnames) in enumerate(plates or [], start=1):
        cfg.append("  <plate>")
        cfg.append(f'    <metadata key="plater_id" value="{pid}"/>')
        cfg.append(f'    <metadata key="plater_name" value="{pname}"/>')
        cfg.append(f'    <metadata key="printer_model_id" value="{printer_model}"/>')
        cfg.append('    <metadata key="locked" value="false"/>')
        for gname in gnames:
            cfg.append("    <model_instance>")
            cfg.append(f'      <metadata key="object_id" value="{name_to_goid[gname]}"/>')
            cfg.append('      <metadata key="instance_id" value="0"/>')
            cfg.append(f'      <metadata key="identify_id" value="{identify_id}"/>')
            cfg.append("    </model_instance>")
            identify_id += 1
        cfg.append("  </plate>")
    if plates:
        cfg.append("  <assemble>")
        for goid, _, _, _, _, local, origin in group_objs:
            ox, oy, oz = origin
            cfg.append(
                f'   <assemble_item object_id="{goid}" instance_id="0" '
                f'transform="{_build_transform(*local)}" '
                f'offset="{ox:.4f} {oy:.4f} {oz:.4f}"/>')
        cfg.append("  </assemble>")
    cfg.append("</config>")
    model_settings = "\n".join(cfg)

    project = json.dumps(
        _project_settings(filament_colors, printer_model, printer_variant), indent=1)

    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel-1" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    ctypes = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
              "</Types>")

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ctypes)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)
        z.writestr("Metadata/model_settings.config", model_settings)
        z.writestr("Metadata/project_settings.config", project)
