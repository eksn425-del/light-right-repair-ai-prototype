from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import MultiPoint, Polygon, box, mapping
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402

try:
    import ezdxf
except Exception:  # pragma: no cover
    ezdxf = None


RUNTIME = load_runtime()
ROOT = RUNTIME.project_root
WORK = RUNTIME.run_dir
SRC = RUNTIME.source_team_root

BUILDINGS_CSV = RUNTIME.source_dataset / "buildings.csv"
BUILDINGS_AUDIT_CSV = RUNTIME.source_dataset / "buildings_with_audit_columns.csv"
ORIGINAL_OBJ = SRC / "沿湖休闲片区场地.obj"
ORIGINAL_SKP = SRC / "沿湖休闲片区场地.skp"
ORIGINAL_DXF = SRC / "沿湖休闲片区标号(新）.dxf"
SITE_DXF = SRC / "沿湖休闲片区场地说明.dxf"
LADYBUG_READY_BASELINE = ROOT / "data" / "private_external" / "baseline_original_full_site_ladybug_ready.obj"
LADYBUG_READY_C6_C33 = ROOT / "data" / "private_external" / "algorithm_after_full_site_only_C6_C33_changed_ladybug_ready.obj"
LATEST_AUDIT = RUNTIME.source_audit


def ensure_dirs() -> None:
    for sub in [
        "data_raw",
        "data_processed",
        "canonical_site_v2",
        "results_csv",
        "figures",
        "docs",
        "logs",
    ]:
        (WORK / sub).mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"building_id": str})


def rect_from_row(row: pd.Series) -> Polygon:
    return box(float(row.x_min), float(row.y_min), float(row.x_max), float(row.y_max))


def source_file_stats(path: Path) -> dict:
    if not path.exists():
        return {"path": str(path), "exists": False}
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": path.stat().st_size,
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
    }


def obj_raw_extent(path: Path) -> dict:
    xs, ys, zs = [], [], []
    if not path.exists():
        return {"exists": False}
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.startswith("v "):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                xs.append(float(parts[1]))
                ys.append(float(parts[2]))
                zs.append(float(parts[3]))
            except ValueError:
                continue
    if not xs:
        return {"exists": True, "vertex_count": 0}
    return {
        "exists": True,
        "vertex_count": len(xs),
        "x_min": min(xs),
        "x_max": max(xs),
        "y_min": min(ys),
        "y_max": max(ys),
        "z_min": min(zs),
        "z_max": max(zs),
    }


def dxf_raw_extent(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    if ezdxf is None:
        return {"exists": True, "error": "ezdxf is not available"}
    xs, ys, zs = [], [], []
    layer_counts: dict[str, int] = defaultdict(int)
    try:
        doc = ezdxf.readfile(path)
    except Exception as exc:  # pragma: no cover
        return {"exists": True, "error": repr(exc)}
    for ent in doc.modelspace():
        layer_counts[getattr(ent.dxf, "layer", "unknown")] += 1
        pts = []
        t = ent.dxftype()
        try:
            if t == "LINE":
                pts = [ent.dxf.start, ent.dxf.end]
            elif t in {"LWPOLYLINE", "POLYLINE"}:
                pts = list(ent.get_points()) if t == "LWPOLYLINE" else [v.dxf.location for v in ent.vertices]
            elif t in {"TEXT", "MTEXT", "INSERT", "POINT"}:
                pts = [ent.dxf.insert if hasattr(ent.dxf, "insert") else ent.dxf.location]
        except Exception:
            pts = []
        for p in pts:
            if len(p) >= 2:
                xs.append(float(p[0]))
                ys.append(float(p[1]))
                zs.append(float(p[2]) if len(p) >= 3 else 0.0)
    out = {"exists": True, "entity_count": sum(layer_counts.values()), "layer_counts": dict(layer_counts)}
    if xs:
        out.update({"x_min": min(xs), "x_max": max(xs), "y_min": min(ys), "y_max": max(ys), "z_min": min(zs), "z_max": max(zs)})
    return out


def parse_obj_building_points(path: Path) -> dict[str, list[tuple[float, float, float]]]:
    current_id = None
    points: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
    id_re = re.compile(r"\b(C\d+)_")
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith(("g ", "o ")):
                m = id_re.search(line)
                current_id = m.group(1) if m else None
            elif line.startswith("v ") and current_id:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        points[current_id].append((float(parts[1]), float(parts[2]), float(parts[3])))
                    except ValueError:
                        pass
    return points


def derive_dxf_transform(buildings: pd.DataFrame, dxf_components: pd.DataFrame) -> tuple[float, float, pd.DataFrame]:
    rows = []
    by_id: dict[str, list[pd.Series]] = defaultdict(list)
    for _, comp in dxf_components.iterrows():
        labels = [s.strip() for s in str(comp.label_ids).split(";") if s.strip()]
        for label in labels:
            by_id[label].append(comp)
    for _, b in buildings.iterrows():
        bid = b.building_id
        comps = by_id.get(bid, [])
        if not comps:
            continue
        x_min = min(float(c.x_min) for c in comps) / 1000.0
        x_max = max(float(c.x_max) for c in comps) / 1000.0
        y_min = min(float(c.y_min) for c in comps) / 1000.0
        y_max = max(float(c.y_max) for c in comps) / 1000.0
        rows += [
            {"building_id": bid, "axis": "x_min", "offset_m": x_min - float(b.x_min)},
            {"building_id": bid, "axis": "x_max", "offset_m": x_max - float(b.x_max)},
            {"building_id": bid, "axis": "y_min", "offset_m": y_min - float(b.y_min)},
            {"building_id": bid, "axis": "y_max", "offset_m": y_max - float(b.y_max)},
        ]
    offsets = pd.DataFrame(rows)
    x_offset = float(offsets[offsets.axis.str.startswith("x")].offset_m.median())
    y_offset = float(offsets[offsets.axis.str.startswith("y")].offset_m.median())
    return x_offset, y_offset, offsets


def derive_obj_transform(buildings: pd.DataFrame, obj_agg: pd.DataFrame) -> tuple[float, float, pd.DataFrame]:
    merged = buildings.merge(obj_agg, on="building_id", how="inner")
    rows = []
    for _, r in merged.iterrows():
        bid = r.building_id
        rows.append({"building_id": bid, "axis": "x_min", "offset_m": float(r.obj_x_min) / 1000.0 - float(r.x_min)})
        rows.append({"building_id": bid, "axis": "x_max", "offset_m": float(r.obj_x_max) / 1000.0 - float(r.x_max)})
        rows.append({"building_id": bid, "axis": "y_min", "offset_m": -float(r.obj_z_max) / 1000.0 - float(r.y_min)})
        rows.append({"building_id": bid, "axis": "y_max", "offset_m": -float(r.obj_z_min) / 1000.0 - float(r.y_max)})
    offsets = pd.DataFrame(rows)
    # Use the median and drop only visually documented gross outliers such as C1's distant extra group.
    x_offset = float(offsets[offsets.axis.str.startswith("x")].offset_m.median())
    y_offset = float(offsets[offsets.axis.str.startswith("y")].offset_m.median())
    return x_offset, y_offset, offsets


def transformed_obj_polygons(points_by_id: dict[str, list[tuple[float, float, float]]], x_offset: float, y_offset: float) -> dict[str, Polygon]:
    out = {}
    for bid, pts in points_by_id.items():
        xy = [(x / 1000.0 - x_offset, -z / 1000.0 - y_offset) for x, _vertical, z in pts]
        unique_xy = sorted(set((round(x, 6), round(y, 6)) for x, y in xy))
        if len(unique_xy) >= 3:
            out[bid] = MultiPoint(unique_xy).convex_hull
    return out


def dxf_component_polygons(dxf_components: pd.DataFrame, x_offset: float, y_offset: float) -> dict[str, list[Polygon]]:
    by_id: dict[str, list[Polygon]] = defaultdict(list)
    for _, comp in dxf_components.iterrows():
        labels = [s.strip() for s in str(comp.label_ids).split(";") if s.strip()]
        poly = box(
            float(comp.x_min) / 1000.0 - x_offset,
            float(comp.y_min) / 1000.0 - y_offset,
            float(comp.x_max) / 1000.0 - x_offset,
            float(comp.y_max) / 1000.0 - y_offset,
        )
        for label in labels:
            by_id[label].append(poly)
    return by_id


def polygon_to_obj_faces(poly: Polygon, height: float, vertex_start: int) -> tuple[list[tuple[float, float, float]], list[list[int]]]:
    # Canonical convention: X/Y are horizontal meters, Z is vertical meters.
    exterior = list(poly.exterior.coords)[:-1]
    if len(exterior) < 3:
        return [], []
    verts = [(x, y, 0.0) for x, y in exterior] + [(x, y, height) for x, y in exterior]
    n = len(exterior)
    bottom = list(range(vertex_start, vertex_start + n))[::-1]
    top = list(range(vertex_start + n, vertex_start + 2 * n))
    faces = [bottom, top]
    for i in range(n):
        j = (i + 1) % n
        faces.append([vertex_start + i, vertex_start + j, vertex_start + n + j, vertex_start + n + i])
    return verts, faces


def write_canonical_obj(buildings: pd.DataFrame, canonical_polys: dict[str, Polygon], path: Path) -> None:
    lines = [
        "# canonical_site_v2 generated by route_b_geometry_audit.py",
        "# Units: meters. Axes: X/Y horizontal, Z vertical.",
    ]
    vertex_index = 1
    for _, b in buildings.iterrows():
        bid = b.building_id
        geom = canonical_polys.get(bid)
        if geom is None or geom.is_empty:
            continue
        height = float(b.height_m)
        geoms = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
        for idx, poly in enumerate(geoms, start=1):
            lines.append(f"g {bid}_part{idx}_{height:g}m")
            verts, faces = polygon_to_obj_faces(poly, height, vertex_index)
            for v in verts:
                lines.append(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}")
            for face in faces:
                lines.append("f " + " ".join(str(i) for i in face))
            vertex_index += len(verts)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def iou(a: Polygon, b: Polygon) -> float:
    if a is None or b is None or a.is_empty or b.is_empty:
        return float("nan")
    inter = a.intersection(b).area
    union = a.union(b).area
    return float(inter / union) if union else float("nan")


def centroid_distance(a: Polygon, b: Polygon) -> float:
    if a is None or b is None or a.is_empty or b.is_empty:
        return float("nan")
    return float(a.centroid.distance(b.centroid))


def pass_status(row: pd.Series, key_ids: set[str]) -> tuple[str, str]:
    reasons = []
    bid = row.building_id
    if not bool(row.in_original_obj):
        reasons.append("原始OBJ缺失该编号")
    if not math.isnan(row.height_difference_m) and abs(row.height_difference_m) > 0.1:
        reasons.append("高度不一致")
    if bid in key_ids:
        if math.isnan(row.centroid_distance_m) or row.centroid_distance_m > 0.5:
            reasons.append("关键候选建筑质心偏差超过0.5m")
        if math.isnan(row.footprint_overlap_iou) or row.footprint_overlap_iou < 0.85:
            reasons.append("关键候选建筑footprint重叠不足")
    else:
        if not math.isnan(row.centroid_distance_m) and row.centroid_distance_m > 3.0:
            reasons.append("全场建筑质心偏差超过3m")
    if row.dxf_component_count == 0:
        reasons.append("DXF footprint组件缺失")
    if row.dxf_component_count > 1:
        reasons.append("DXF多组件/复合建筑")
    if row.obj_group_count > 1:
        reasons.append("OBJ多组聚合")
    if row.shared_dxf_labels:
        reasons.append("DXF组件存在多编号共享")
    if reasons:
        status = "未通过" if bid in key_ids and any("关键候选" in r or "缺失" in r for r in reasons) else "需解释"
        return status, "；".join(reasons)
    return "通过", ""


def make_figures(buildings: pd.DataFrame, csv_rects: dict[str, Polygon], obj_polys: dict[str, Polygon], canonical_polys: dict[str, Polygon]) -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    def plot_poly(ax, poly, color, label, linestyle="-", linewidth=1.2, alpha=1.0):
        if poly is None or poly.is_empty:
            return
        geoms = list(poly.geoms) if poly.geom_type == "MultiPolygon" else [poly]
        for geom in geoms:
            xs, ys = geom.exterior.xy
            ax.plot(xs, ys, color=color, linestyle=linestyle, linewidth=linewidth, alpha=alpha, label=label)
            label = None

    key_ids = ["C6", "C33", "C13", "C24"]
    fig, ax = plt.subplots(figsize=(10, 8), dpi=180)
    for bid in key_ids:
        plot_poly(ax, csv_rects.get(bid), "#2b6cb0", "CSV footprint" if bid == "C6" else None, "--", 1.6)
        plot_poly(ax, obj_polys.get(bid), "#c53030", "原始OBJ转换后footprint" if bid == "C6" else None, "-", 1.8)
        plot_poly(ax, canonical_polys.get(bid), "#2f855a", "canonical_site_v2 footprint" if bid == "C6" else None, ":", 2.0)
        c = csv_rects[bid].centroid
        ax.text(c.x, c.y, bid, fontsize=10, weight="bold")
    ax.arrow(0.06, 0.1, 0, 0.08, transform=ax.transAxes, width=0.004, head_width=0.02, color="black")
    ax.text(0.052, 0.19, "N", transform=ax.transAxes, fontsize=11, weight="bold")
    ax.plot([0.74, 0.94], [0.08, 0.08], transform=ax.transAxes, color="black", lw=2)
    ax.text(0.79, 0.045, "约50 m", transform=ax.transAxes, fontsize=9)
    ax.set_title("C6/C33/C13/C24 几何核对")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X / m")
    ax.set_ylabel("Y / m")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(WORK / "figures" / "92_C6_C33_C13_C24几何核对图.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 10), dpi=180)
    for _, b in buildings.iterrows():
        bid = b.building_id
        plot_poly(ax, csv_rects.get(bid), "#4a5568", "CSV" if bid == "C1" else None, "--", 0.7, 0.7)
        plot_poly(ax, canonical_polys.get(bid), "#2f855a", "canonical_site_v2" if bid == "C1" else None, "-", 0.9, 0.9)
        if bid in key_ids or bid in {"C42"}:
            c = csv_rects[bid].centroid
            ax.text(c.x, c.y, bid, fontsize=8, weight="bold")
    ax.arrow(0.05, 0.08, 0, 0.06, transform=ax.transAxes, width=0.003, head_width=0.015, color="black")
    ax.text(0.044, 0.145, "N", transform=ax.transAxes, fontsize=10, weight="bold")
    ax.set_title("全场 CSV 与 canonical_site_v2 建筑边界叠加")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X / m")
    ax.set_ylabel("Y / m")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(WORK / "figures" / "93_全场几何叠加核对图.png")
    plt.close(fig)


def write_geojson(canonical_polys: dict[str, Polygon], buildings: pd.DataFrame, path: Path) -> None:
    features = []
    by_id = buildings.set_index("building_id")
    for bid, geom in canonical_polys.items():
        if bid not in by_id.index or geom is None or geom.is_empty:
            continue
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "building_id": bid,
                    "height_m": float(by_id.loc[bid].height_m),
                    "movable": str(by_id.loc[bid].movable),
                    "protected": str(by_id.loc[bid].protected),
                },
                "geometry": mapping(geom),
            }
        )
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    buildings = read_csv(BUILDINGS_CSV)
    buildings_audit = read_csv(BUILDINGS_AUDIT_CSV)
    dxf_components = pd.read_csv(LATEST_AUDIT / "dxf_footprint_components.csv")
    obj_agg = read_csv(LATEST_AUDIT / "obj_building_aggregate.csv")
    consistency = read_csv(LATEST_AUDIT / "building_consistency_audit.csv")

    source_stats = {
        "original_skp": source_file_stats(ORIGINAL_SKP),
        "original_dxf_labels": source_file_stats(ORIGINAL_DXF) | {"raw_extent": dxf_raw_extent(ORIGINAL_DXF)},
        "site_dxf": source_file_stats(SITE_DXF) | {"raw_extent": dxf_raw_extent(SITE_DXF)},
        "original_obj": source_file_stats(ORIGINAL_OBJ) | {"raw_extent": obj_raw_extent(ORIGINAL_OBJ)},
        "ladybug_ready_baseline": source_file_stats(LADYBUG_READY_BASELINE) | {"raw_extent": obj_raw_extent(LADYBUG_READY_BASELINE)},
        "ladybug_ready_c6_c33": source_file_stats(LADYBUG_READY_C6_C33) | {"raw_extent": obj_raw_extent(LADYBUG_READY_C6_C33)},
        "buildings_csv": source_file_stats(BUILDINGS_CSV),
    }
    (WORK / "logs" / "90_source_file_stats.json").write_text(json.dumps(source_stats, ensure_ascii=False, indent=2), encoding="utf-8")

    dxf_x_offset, dxf_y_offset, dxf_offsets = derive_dxf_transform(buildings, dxf_components)
    obj_x_offset, obj_y_offset, obj_offsets = derive_obj_transform(buildings, obj_agg)
    dxf_offsets.to_csv(WORK / "results_csv" / "90_DXF到CSV偏移样本.csv", index=False, encoding="utf-8-sig")
    obj_offsets.to_csv(WORK / "results_csv" / "90_OBJ到CSV偏移样本.csv", index=False, encoding="utf-8-sig")

    obj_points = parse_obj_building_points(ORIGINAL_OBJ)
    obj_polys = transformed_obj_polygons(obj_points, obj_x_offset, obj_y_offset)
    dxf_poly_parts = dxf_component_polygons(dxf_components, dxf_x_offset, dxf_y_offset)
    csv_rects = {r.building_id: rect_from_row(r) for _, r in buildings.iterrows()}
    canonical_polys: dict[str, Polygon] = {}
    shared_dxf: dict[str, bool] = defaultdict(bool)
    for _, comp in dxf_components.iterrows():
        labels = [s.strip() for s in str(comp.label_ids).split(";") if s.strip()]
        if len(labels) > 1:
            for label in labels:
                shared_dxf[label] = True
    for _, b in buildings.iterrows():
        bid = b.building_id
        parts = dxf_poly_parts.get(bid)
        if parts:
            canonical_polys[bid] = unary_union(parts)
        else:
            canonical_polys[bid] = csv_rects[bid]

    # Write canonical data products.
    canonical_buildings = buildings.copy()
    canonical_buildings["canonical_geometry_source"] = [
        "dxf_component_bbox_union" if bid in dxf_poly_parts else "csv_bbox_fallback" for bid in canonical_buildings.building_id
    ]
    canonical_buildings["canonical_area_m2"] = [canonical_polys[bid].area for bid in canonical_buildings.building_id]
    canonical_buildings["canonical_centroid_x"] = [canonical_polys[bid].centroid.x for bid in canonical_buildings.building_id]
    canonical_buildings["canonical_centroid_y"] = [canonical_polys[bid].centroid.y for bid in canonical_buildings.building_id]
    canonical_buildings.to_csv(WORK / "canonical_site_v2" / "canonical_buildings.csv", index=False, encoding="utf-8-sig")
    write_canonical_obj(buildings, canonical_polys, WORK / "canonical_site_v2" / "canonical_site_v2.obj")
    write_geojson(canonical_polys, buildings, WORK / "canonical_site_v2" / "canonical_site_v2.geojson")

    consistency_by_id = consistency.set_index("building_id")
    obj_agg_by_id = obj_agg.set_index("building_id")
    rows = []
    for _, b in buildings.iterrows():
        bid = b.building_id
        csv_poly = csv_rects[bid]
        obj_poly = obj_polys.get(bid)
        canonical_poly = canonical_polys[bid]
        obj_height = float(obj_agg_by_id.loc[bid].height_m_from_obj) if bid in obj_agg_by_id.index else float("nan")
        audit_row = consistency_by_id.loc[bid] if bid in consistency_by_id.index else None
        rows.append(
            {
                "building_id": bid,
                "CSV centroid_x": csv_poly.centroid.x,
                "CSV centroid_y": csv_poly.centroid.y,
                "OBJ centroid_x": obj_poly.centroid.x if obj_poly is not None else np.nan,
                "OBJ centroid_y": obj_poly.centroid.y if obj_poly is not None else np.nan,
                "centroid_distance_m": centroid_distance(csv_poly, obj_poly) if obj_poly is not None else np.nan,
                "CSV height_m": float(b.height_m),
                "OBJ height_m": obj_height,
                "height_difference_m": obj_height - float(b.height_m) if not math.isnan(obj_height) else np.nan,
                "CSV footprint_area": csv_poly.area,
                "OBJ footprint_area": obj_poly.area if obj_poly is not None else np.nan,
                "canonical footprint_area": canonical_poly.area,
                "footprint_area_ratio": (obj_poly.area / csv_poly.area) if obj_poly is not None and csv_poly.area else np.nan,
                "footprint_overlap_iou": iou(csv_poly, obj_poly) if obj_poly is not None else np.nan,
                "in_original_obj": obj_poly is not None,
                "obj_group_count": int(audit_row.obj_group_count) if audit_row is not None and not pd.isna(audit_row.obj_group_count) else 0,
                "dxf_label_count": int(audit_row.dxf_label_count) if audit_row is not None and not pd.isna(audit_row.dxf_label_count) else 0,
                "dxf_component_count": int(audit_row.dxf_footprint_component_count) if audit_row is not None and not pd.isna(audit_row.dxf_footprint_component_count) else 0,
                "shared_dxf_labels": bool(shared_dxf[bid]),
                "修复方式": "canonical_site_v2采用DXF组件bbox并集+CSV高度；原始OBJ仅作核对" if bid in dxf_poly_parts else "CSV bbox fallback",
            }
        )
    audit_df = pd.DataFrame(rows)
    key_ids = {"C6", "C33", "C13", "C24"}
    statuses = audit_df.apply(lambda r: pass_status(r, key_ids), axis=1)
    audit_df["是否通过"] = [s[0] for s in statuses]
    audit_df["不通过原因"] = [s[1] for s in statuses]
    audit_df.to_csv(WORK / "results_csv" / "91_建筑几何一致性总表.csv", index=False, encoding="utf-8-sig")

    make_figures(buildings, csv_rects, obj_polys, canonical_polys)

    critical = audit_df[audit_df.building_id.isin(list(key_ids))][
        [
            "building_id",
            "centroid_distance_m",
            "CSV height_m",
            "OBJ height_m",
            "height_difference_m",
            "CSV footprint_area",
            "OBJ footprint_area",
            "canonical footprint_area",
            "footprint_overlap_iou",
            "是否通过",
            "不通过原因",
        ]
    ]
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "dxf_to_canonical_matrix": [
            [0.001, 0.0, -dxf_x_offset],
            [0.0, 0.001, -dxf_y_offset],
            [0.0, 0.0, 1.0],
        ],
        "obj_to_canonical_matrix_description": "x'=x_mm/1000-obj_x_offset; y'=-z_mm/1000-obj_y_offset; z'=y_mm/1000",
        "obj_x_offset_m": obj_x_offset,
        "obj_y_offset_m": obj_y_offset,
        "dxf_x_offset_m": dxf_x_offset,
        "dxf_y_offset_m": dxf_y_offset,
        "canonical_axes": "X/Y为水平米制坐标，Z为竖向高度米制坐标。",
        "critical_building_audit": critical.to_dict(orient="records"),
        "full_audit_status_counts": audit_df["是否通过"].value_counts(dropna=False).to_dict(),
    }
    (WORK / "logs" / "90_geometry_audit_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = []
    md.append("# 90_坐标尺度转换说明")
    md.append("")
    md.append(f"生成时间：{summary['generated_at']}")
    md.append("")
    md.append("## 采用的源文件优先级")
    md.append("")
    md.append("1. 原始 SKP 与 DXF 标号/边界；")
    md.append("2. `buildings.csv` 的建筑编号、高度、可动/保护属性；")
    md.append("3. 原始 `site_model.obj` / `沿湖休闲片区场地.obj`；")
    md.append("4. 旧 Ladybug-ready OBJ，仅作为历史对照，未直接作为规范输入。")
    md.append("")
    md.append("## 源文件原始坐标范围")
    md.append("")
    for name, stats in source_stats.items():
        md.append(f"### {name}")
        md.append("")
        md.append("```json")
        md.append(json.dumps(stats, ensure_ascii=False, indent=2))
        md.append("```")
        md.append("")
    md.append("## 单位、轴向与变换")
    md.append("")
    md.append("DXF 和原始 OBJ 坐标均表现为毫米量级；`buildings.csv` 已为米制局部坐标。规范模型统一采用米。")
    md.append("")
    md.append("DXF 到规范坐标的变换为：")
    md.append("")
    md.append("```text")
    md.append(f"x = dxf_x_mm / 1000 - {dxf_x_offset:.6f}")
    md.append(f"y = dxf_y_mm / 1000 - {dxf_y_offset:.6f}")
    md.append("z = height_m")
    md.append("```")
    md.append("")
    md.append("原始 OBJ 到规范坐标的核对变换为：")
    md.append("")
    md.append("```text")
    md.append(f"x = obj_x_mm / 1000 - {obj_x_offset:.6f}")
    md.append(f"y = -obj_z_mm / 1000 - {obj_y_offset:.6f}")
    md.append("z = obj_y_mm / 1000")
    md.append("```")
    md.append("")
    md.append("这说明原始 OBJ 的竖向轴为 Y，水平第二轴以负 Z 对应规范 Y；`canonical_site_v2` 改为 X/Y 水平、Z 竖向，以便后续 Python、trimesh 与 Radiance 统一使用。")
    md.append("")
    md.append("## 北向定义")
    md.append("")
    md.append("本轮暂以规范坐标 +Y 方向作为图面北向进行统一核对；后续 HB-Radiance 场景如需按真实北向旋转，必须在 `100_HB_Radiance场景参数表.csv` 中显式记录旋转角。")
    md.append("")
    md.append("## 规范模型构建口径")
    md.append("")
    md.append("由于 DXF footprint 为 LINE 组件而非闭合 PLINE，本轮 `canonical_site_v2` 采用 DXF footprint 组件 bbox 的并集作为建筑平面边界，并采用 `buildings.csv` 的高度和保护属性。原始 OBJ 用于坐标/高度/编号核对，不直接覆盖 DXF/CSV。")
    md.append("")
    md.append("## 关键建筑核对结论")
    md.append("")
    md.append(critical.to_markdown(index=False, floatfmt=".3f"))
    md.append("")
    md.append("## 最终规范模型坐标范围")
    md.append("")
    bounds = unary_union(list(canonical_polys.values())).bounds
    md.append(f"`canonical_site_v2` 平面范围：x={bounds[0]:.3f} 至 {bounds[2]:.3f} m；y={bounds[1]:.3f} 至 {bounds[3]:.3f} m。")
    md.append("")
    md.append("## 处理原则")
    md.append("")
    md.append("本文件废弃旧 2.5D/trimesh/Pareto 结论作为最终判断依据。后续所有新实验必须读取 `canonical_site_v2`，不得与旧 Ladybug-ready OBJ 混用。")
    (WORK / "docs" / "90_坐标尺度转换说明.md").write_text("\n".join(md), encoding="utf-8")

    write_run_metadata(
        RUNTIME,
        stage="geometry_audit",
        inputs=[BUILDINGS_CSV, ORIGINAL_OBJ, ORIGINAL_DXF, SITE_DXF, LATEST_AUDIT / "dxf_footprint_components.csv"],
        extra={"full_audit_status_counts": summary["full_audit_status_counts"]},
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
