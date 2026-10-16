from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from src.io.export_results import ensure_dir
from src.io.load_tables import to_bool


def buildings_to_boxes(buildings: pd.DataFrame) -> list[dict]:
    """Convert building rows into axis-aligned 3D boxes."""
    boxes: list[dict] = []
    for _, row in buildings.iterrows():
        boxes.append(
            {
                "name": str(row.get("building_id", "building")),
                "x_min": float(row["x_min"]),
                "x_max": float(row["x_max"]),
                "y_min": float(row["y_min"]),
                "y_max": float(row["y_max"]),
                "z_min": 0.0,
                "z_max": float(row["height_m"]),
            }
        )
    return boxes


def _box_vertices(box: dict) -> list[tuple[float, float, float]]:
    x0, x1 = float(box["x_min"]), float(box["x_max"])
    y0, y1 = float(box["y_min"]), float(box["y_max"])
    z0, z1 = float(box.get("z_min", 0.0)), float(box["z_max"])
    return [
        (x0, y0, z0),
        (x1, y0, z0),
        (x1, y1, z0),
        (x0, y1, z0),
        (x0, y0, z1),
        (x1, y0, z1),
        (x1, y1, z1),
        (x0, y1, z1),
    ]


def write_boxes_obj(boxes: Iterable[dict], output_path: Path, title: str) -> Path:
    """Write simple boxes as a Wavefront OBJ file."""
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    lines = [f"# {title}", "# Units: meters"]
    vertex_offset = 1
    faces = [
        (1, 2, 3, 4),
        (5, 8, 7, 6),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 8, 4),
        (4, 8, 5, 1),
    ]

    for box in boxes:
        name = str(box.get("name", "box")).replace(" ", "_")
        lines.append(f"g {name}")
        for vertex in _box_vertices(box):
            lines.append(f"v {vertex[0]:.3f} {vertex[1]:.3f} {vertex[2]:.3f}")
        for face in faces:
            shifted = [str(index + vertex_offset - 1) for index in face]
            lines.append("f " + " ".join(shifted))
        vertex_offset += 8

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def compute_site_bounds(
    buildings: pd.DataFrame, streets: pd.DataFrame | None = None, padding: float = 5.0
) -> tuple[float, float, float, float]:
    """Compute XY bounds from building footprints and optional street endpoints."""
    x_values = list(buildings["x_min"]) + list(buildings["x_max"])
    y_values = list(buildings["y_min"]) + list(buildings["y_max"])
    if streets is not None and not streets.empty:
        x_values += list(streets["start_x"]) + list(streets["end_x"])
        y_values += list(streets["start_y"]) + list(streets["end_y"])

    return (
        float(min(x_values) - padding),
        float(max(x_values) + padding),
        float(min(y_values) - padding),
        float(max(y_values) + padding),
    )


def point_in_rect(x: float, y: float, row: pd.Series, tolerance: float = 0.0) -> bool:
    """Return True when a point lies inside a building footprint rectangle."""
    return (
        float(row["x_min"]) - tolerance <= x <= float(row["x_max"]) + tolerance
        and float(row["y_min"]) - tolerance <= y <= float(row["y_max"]) + tolerance
    )


def point_in_any_building(x: float, y: float, buildings: pd.DataFrame) -> bool:
    """Return True if the point is inside any building footprint."""
    return any(point_in_rect(x, y, row) for _, row in buildings.iterrows())


def distance_point_to_rect(x: float, y: float, row: pd.Series) -> float:
    """Compute distance from a point to an axis-aligned rectangle."""
    dx = max(float(row["x_min"]) - x, 0.0, x - float(row["x_max"]))
    dy = max(float(row["y_min"]) - y, 0.0, y - float(row["y_max"]))
    return float((dx * dx + dy * dy) ** 0.5)


def nearest_building(x: float, y: float, buildings: pd.DataFrame) -> tuple[str, float]:
    """Find the closest building footprint to an XY point."""
    best_id = ""
    best_distance = float("inf")
    for _, row in buildings.iterrows():
        distance = distance_point_to_rect(x, y, row)
        if distance < best_distance:
            best_distance = distance
            best_id = str(row["building_id"])
    return best_id, best_distance


def footprint_gap(row_a: pd.Series, row_b: pd.Series) -> tuple[float, float, float]:
    """Return horizontal gap distance and midpoint between two building boxes."""
    if float(row_a["x_max"]) <= float(row_b["x_min"]):
        dx = float(row_b["x_min"]) - float(row_a["x_max"])
        mid_x = (float(row_a["x_max"]) + float(row_b["x_min"])) / 2
    elif float(row_b["x_max"]) <= float(row_a["x_min"]):
        dx = float(row_a["x_min"]) - float(row_b["x_max"])
        mid_x = (float(row_b["x_max"]) + float(row_a["x_min"])) / 2
    else:
        dx = 0.0
        mid_x = (
            max(float(row_a["x_min"]), float(row_b["x_min"]))
            + min(float(row_a["x_max"]), float(row_b["x_max"]))
        ) / 2

    if float(row_a["y_max"]) <= float(row_b["y_min"]):
        dy = float(row_b["y_min"]) - float(row_a["y_max"])
        mid_y = (float(row_a["y_max"]) + float(row_b["y_min"])) / 2
    elif float(row_b["y_max"]) <= float(row_a["y_min"]):
        dy = float(row_a["y_min"]) - float(row_b["y_max"])
        mid_y = (float(row_b["y_max"]) + float(row_a["y_min"])) / 2
    else:
        dy = 0.0
        mid_y = (
            max(float(row_a["y_min"]), float(row_b["y_min"]))
            + min(float(row_a["y_max"]), float(row_b["y_max"]))
        ) / 2

    return float((dx * dx + dy * dy) ** 0.5), mid_x, mid_y


def box_conflicts_with_protected_zones(box: dict, protected_zones: pd.DataFrame) -> bool:
    """Check whether a box overlaps any protected zone."""
    if protected_zones.empty:
        return False

    for _, zone in protected_zones.iterrows():
        intersects = not (
            float(box["x_max"]) < float(zone["x_min"])
            or float(box["x_min"]) > float(zone["x_max"])
            or float(box["y_max"]) < float(zone["y_min"])
            or float(box["y_min"]) > float(zone["y_max"])
            or float(box.get("z_max", 0.0)) < float(zone.get("z_min", 0.0))
            or float(box.get("z_min", 0.0)) > float(zone.get("z_max", 999.0))
        )
        if intersects:
            return True
    return False


def is_building_editable(row: pd.Series) -> bool:
    """Return True when a building can receive subtractive interventions."""
    return to_bool(row.get("movable", False)) and not to_bool(row.get("protected", False))

