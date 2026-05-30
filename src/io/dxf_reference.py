from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

import pandas as pd

from src.io.export_results import ensure_dir, write_csv, write_json


def _entity_points(entity) -> list[tuple[float, float]]:
    """Extract approximate XY points from common DXF entities."""
    entity_type = entity.dxftype()
    try:
        if entity_type == "LINE":
            return [
                (float(entity.dxf.start.x), float(entity.dxf.start.y)),
                (float(entity.dxf.end.x), float(entity.dxf.end.y)),
            ]
        if entity_type == "LWPOLYLINE":
            return [(float(p[0]), float(p[1])) for p in entity.get_points("xy")]
        if entity_type == "POLYLINE":
            return [
                (float(vertex.dxf.location.x), float(vertex.dxf.location.y))
                for vertex in entity.vertices
            ]
        if entity_type in {"TEXT", "MTEXT", "INSERT"}:
            point = entity.dxf.insert
            return [(float(point.x), float(point.y))]
        if entity_type == "POINT":
            point = entity.dxf.location
            return [(float(point.x), float(point.y))]
        if entity_type in {"CIRCLE", "ARC"}:
            center = entity.dxf.center
            radius = float(entity.dxf.radius)
            return [
                (float(center.x) - radius, float(center.y) - radius),
                (float(center.x) + radius, float(center.y) + radius),
            ]
        if entity_type == "HATCH":
            points: list[tuple[float, float]] = []
            for path in entity.paths:
                if hasattr(path, "vertices"):
                    points.extend((float(v[0]), float(v[1])) for v in path.vertices)
            return points
    except Exception:
        return []
    return []


def _update_bounds(bounds: list[float], x: float, y: float) -> None:
    if not math.isfinite(x) or not math.isfinite(y):
        return
    bounds[0] = min(bounds[0], x)
    bounds[1] = max(bounds[1], x)
    bounds[2] = min(bounds[2], y)
    bounds[3] = max(bounds[3], y)


def _clean_bounds(bounds: list[float]) -> dict:
    if math.isinf(bounds[0]):
        return {
            "x_min": None,
            "x_max": None,
            "y_min": None,
            "y_max": None,
            "width_m": None,
            "height_m": None,
        }
    return {
        "x_min": round(bounds[0], 3),
        "x_max": round(bounds[1], 3),
        "y_min": round(bounds[2], 3),
        "y_max": round(bounds[3], 3),
        "width_m": round(bounds[1] - bounds[0], 3),
        "height_m": round(bounds[3] - bounds[2], 3),
    }


def _polygon_area(points: list[tuple[float, float]]) -> float:
    area = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
        area += x1 * y2 - x2 * y1
    return abs(area) / 2


def analyze_dxf_reference(dxf_path: Path, output_dir: Path) -> dict:
    """Summarise a CAD DXF file into stable CSV/JSON reference tables."""
    import ezdxf

    dxf_path = Path(dxf_path)
    output_dir = ensure_dir(Path(output_dir))
    doc = ezdxf.readfile(dxf_path)
    modelspace = doc.modelspace()

    entity_counts = Counter()
    layer_counts = Counter()
    layer_bounds: dict[str, list[float]] = {}
    overall_bounds = [float("inf"), -float("inf"), float("inf"), -float("inf")]
    text_rows: list[dict] = []
    closed_polyline_rows: list[dict] = []

    for entity in modelspace:
        entity_type = entity.dxftype()
        layer = str(getattr(entity.dxf, "layer", "0"))
        entity_counts[entity_type] += 1
        layer_counts[layer] += 1
        layer_bounds.setdefault(layer, [float("inf"), -float("inf"), float("inf"), -float("inf")])

        for x, y in _entity_points(entity):
            _update_bounds(overall_bounds, x, y)
            _update_bounds(layer_bounds[layer], x, y)

        if entity_type == "TEXT":
            text = str(entity.dxf.text).strip()
            if text:
                point = entity.dxf.insert
                text_rows.append(
                    {
                        "text": text,
                        "x": round(float(point.x), 3),
                        "y": round(float(point.y), 3),
                        "layer": layer,
                    }
                )
        elif entity_type == "MTEXT":
            text = str(entity.text).replace("\n", " ").strip()
            if text:
                point = entity.dxf.insert
                text_rows.append(
                    {
                        "text": text,
                        "x": round(float(point.x), 3),
                        "y": round(float(point.y), 3),
                        "layer": layer,
                    }
                )

        if entity_type == "LWPOLYLINE":
            try:
                if entity.closed:
                    points = [(float(p[0]), float(p[1])) for p in entity.get_points("xy")]
                    if len(points) >= 3:
                        xs = [point[0] for point in points]
                        ys = [point[1] for point in points]
                        area = _polygon_area(points)
                        closed_polyline_rows.append(
                            {
                                "area_m2": round(area, 3),
                                "x_min": round(min(xs), 3),
                                "x_max": round(max(xs), 3),
                                "y_min": round(min(ys), 3),
                                "y_max": round(max(ys), 3),
                                "width_m": round(max(xs) - min(xs), 3),
                                "height_m": round(max(ys) - min(ys), 3),
                                "vertex_count": len(points),
                                "layer": layer,
                                "candidate_note": "closed polyline; verify whether building/open-space/water edge",
                            }
                        )
            except Exception:
                pass

    layer_rows = []
    for layer, count in layer_counts.most_common():
        layer_rows.append({"layer": layer, "entity_count": int(count), **_clean_bounds(layer_bounds[layer])})

    entity_rows = [
        {"entity_type": entity_type, "count": int(count)}
        for entity_type, count in entity_counts.most_common()
    ]

    text_df = pd.DataFrame(text_rows)
    closed_df = pd.DataFrame(closed_polyline_rows).sort_values("area_m2") if closed_polyline_rows else pd.DataFrame()
    layer_df = pd.DataFrame(layer_rows)
    entity_df = pd.DataFrame(entity_rows)

    outputs = {
        "layers": write_csv(layer_df, output_dir / "dxf_layers.csv"),
        "entity_types": write_csv(entity_df, output_dir / "dxf_entity_types.csv"),
        "texts": write_csv(text_df, output_dir / "dxf_texts.csv"),
        "closed_polylines": write_csv(closed_df, output_dir / "dxf_closed_polylines.csv"),
    }

    summary = {
        "source_file": str(dxf_path),
        "dxf_version": doc.dxfversion,
        "modelspace_entity_count": int(len(modelspace)),
        "layer_count": int(len(layer_counts)),
        "text_count": int(len(text_rows)),
        "closed_lwpolyline_count": int(len(closed_polyline_rows)),
        "overall_bounds": _clean_bounds(overall_bounds),
        "important_note": (
            "Most entities are on one layer in this CAD file, so algorithm-ready "
            "buildings/streets/site_zones still need human verification."
        ),
    }
    outputs["summary"] = write_json(summary, output_dir / "dxf_summary.json")
    return {"summary_data": summary, **outputs}

