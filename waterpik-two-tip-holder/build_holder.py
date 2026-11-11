"""Two-tip adhesive-mounted holder. Units: millimetres.

Requires CadQuery 2.7. Edit PARAMETERS and run this file to regenerate.
The rear tape face is already on the print bed (Z=0).
Mounted orientation: X left/right, Y upward, Z away from the tile.
Fit is deliberately tapered, not a model-specific snap fit.
"""
from pathlib import Path
import json
import struct
from collections import Counter, defaultdict

import cadquery as cq
import numpy as np

OUT = Path(__file__).resolve().parent
PARAMETERS = {
    "width": 44.0,
    "back_height": 24.0,
    "back_thickness": 2.4,
    "back_corner_radius": 2.0,
    "projection": 23.0,
    "shelf_top": 22.0,
    "shelf_thickness": 3.0,
    "shelf_rear": 2.0,
    "shelf_corner_radius": 2.0,
    "tip_spacing": 20.0,
    "slot_root_center": 9.0,
    "slot_root_width": 5.0,
    "slot_mouth_width": 9.5,
    "gusset_thickness": 2.4,
    "gusset_bottom": 5.0,
    "gusset_end": 17.0,
}
P = PARAMETERS


def slot_plan(center=0.0, plane="XZ"):
    """Open-ended taper plus round end. Extend beyond mouth before cutting."""
    r = P["slot_root_width"] / 2
    root = P["slot_root_center"]
    front = P["projection"]
    slope = (P["slot_mouth_width"] / 2 - r) / (front - root)
    beyond = front + 3
    half = r + slope * (beyond - root)
    trap = (cq.Workplane(plane)
            .polyline([(center-r, root), (center+r, root),
                       (center+half, beyond), (center-half, beyond)])
            .close().extrude(50, both=True))
    end = (cq.Workplane(plane).center(center, root)
           .circle(r).extrude(50, both=True))
    return trap.union(end)


def build_holder():
    back = (cq.Workplane("XY")
            .center(0, P["back_height"] / 2)
            .rect(P["width"], P["back_height"])
            .extrude(P["back_thickness"])
            .edges("|Z").fillet(P["back_corner_radius"]))
    rear, front = P["shelf_rear"], P["projection"]
    shelf = (cq.Workplane("XZ")
             .center(0, (rear + front) / 2)
             .rect(P["width"], front - rear)
             .extrude(P["shelf_thickness"])
             .edges("|Y").fillet(P["shelf_corner_radius"])
             .translate((0, P["shelf_top"], 0)))
    for x in (-P["tip_spacing"]/2, P["tip_spacing"]/2):
        shelf = shelf.cut(slot_plan(x))
    part = back.union(shelf)
    gusset_top = P["shelf_top"] - P["shelf_thickness"] + 0.2
    for x in (-P["width"]/2+3, 0, P["width"]/2-3):
        gusset = (cq.Workplane("YZ")
                  .polyline([(P["gusset_bottom"], P["shelf_rear"]),
                             (gusset_top, P["shelf_rear"]),
                             (gusset_top, P["gusset_end"])])
                  .close().extrude(P["gusset_thickness"])
                  .translate((x-P["gusset_thickness"]/2, 0, 0)))
        part = part.union(gusset)
    return part.clean()


def build_gauge():
    rear, front = P["shelf_rear"], P["projection"]
    gauge = (cq.Workplane("XY").center(0, (rear+front)/2)
             .rect(16, front-rear).extrude(P["shelf_thickness"])
             .edges("|Z").fillet(2.0))
    return gauge.cut(slot_plan(0, "XY")).translate((0, -rear, 0)).clean()


def inspect_stl(path):
    data = Path(path).read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    assert len(data) == 84 + n*50, "Unexpected STL encoding"
    dtype = np.dtype([("normal", "<f4", (3,)),
                      ("vertices", "<f4", (3, 3)),
                      ("attribute", "<u2")])
    raw = np.frombuffer(data, dtype=dtype, offset=84)
    triangles = raw["vertices"].astype(np.float64)
    vertices, inverse = np.unique(
        np.round(triangles.reshape(-1, 3), 5), axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    edges = Counter()
    direction = Counter()
    adjacency = defaultdict(set)
    for a, b, c in faces.tolist():
        for u, v in ((a, b), (b, c), (c, a)):
            edges[tuple(sorted((u, v)))] += 1
            direction[(u, v)] += 1
            adjacency[u].add(v)
            adjacency[v].add(u)
    unseen = set(range(len(vertices)))
    components = 0
    while unseen:
        components += 1
        todo = [unseen.pop()]
        while todo:
            for v in adjacency[todo.pop()]:
                if v in unseen:
                    unseen.remove(v)
                    todo.append(v)
    volume = np.einsum("ij,ij->i", triangles[:, 0],
                       np.cross(triangles[:, 1], triangles[:, 2])).sum()/6
    areas = np.linalg.norm(np.cross(triangles[:, 1]-triangles[:, 0],
                                  triangles[:, 2]-triangles[:, 0]), axis=1)/2
    report = {
        "triangles": n,
        "vertices_after_welding": len(vertices),
        "dimensions_mm": (vertices.max(0)-vertices.min(0)).round(5).tolist(),
        "min_xyz_mm": vertices.min(0).tolist(),
        "watertight": all(count == 2 for count in edges.values()),
        "consistently_oriented": all(direction[(v,u)] == count
                                    for (u,v), count in direction.items()),
        "connected_components": components,
        "euler_characteristic": int(len(vertices)-len(edges)+n),
        "degenerate_triangles": int(np.count_nonzero(areas < 1e-10)),
        "signed_volume_mm3": round(float(volume), 3),
    }
    assert report["watertight"]
    assert report["consistently_oriented"]
    assert components == 1
    assert report["degenerate_triangles"] == 0
    assert volume > 0
    return report


if __name__ == "__main__":
    holder = build_holder()
    gauge = build_gauge()
    report = {"parameters": P, "parts": {}}
    for name, model in (("Waterpik_dual_holder", holder),
                        ("Optional_fit_gauge", gauge)):
        shape = model.val()
        assert shape.isValid()
        assert len(model.solids().vals()) == 1
        cq.exporters.export(model, str(OUT / f"{name}.stl"),
                            tolerance=0.025, angularTolerance=0.08)
        cq.exporters.export(model, str(OUT / f"{name}.step"))
        cq.exporters.export(model, str(OUT / f"{name}.3mf"),
                            tolerance=0.025, angularTolerance=0.08)
        part_report = inspect_stl(OUT / f"{name}.stl")
        part_report["cad_valid"] = shape.isValid()
        part_report["cad_solids"] = len(model.solids().vals())
        part_report["cad_volume_mm3"] = round(shape.Volume(), 3)
        report["parts"][name] = part_report
    (OUT / "validation.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))
