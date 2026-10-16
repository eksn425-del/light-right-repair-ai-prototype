from __future__ import annotations

import math

import numpy as np
import pandas as pd

from src.geometry.mesh_utils import compute_site_bounds, point_in_any_building


def _point_to_segment_distance(
    px: float, py: float, ax: float, ay: float, bx: float, by: float
) -> float:
    dx = bx - ax
    dy = by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    cx = ax + t * dx
    cy = ay + t * dy
    return math.hypot(px - cx, py - cy)


def _point_near_any_street(x: float, y: float, streets: pd.DataFrame, extra_margin: float) -> bool:
    if streets.empty:
        return True
    for _, street in streets.iterrows():
        distance = _point_to_segment_distance(
            x,
            y,
            float(street["start_x"]),
            float(street["start_y"]),
            float(street["end_x"]),
            float(street["end_y"]),
        )
        if distance <= float(street["width_m"]) / 2 + extra_margin:
            return True
    return False


def create_ground_grid(
    buildings: pd.DataFrame, streets: pd.DataFrame, site_config: dict
) -> pd.DataFrame:
    """Create analysis points on accessible ground/open street space.

    This is a 2.5D placeholder for future true voxelisation. It avoids building
    footprints and focuses the grid around street corridors.
    """
    grid_size = float(site_config.get("grid_size_m", 2.0))
    padding = float(site_config.get("bounds_padding_m", 5.0))
    ground_z = float(site_config.get("ground_z", 0.0))
    street_margin = float(site_config.get("street_analysis_margin_m", 4.0))
    x_min, x_max, y_min, y_max = compute_site_bounds(buildings, streets, padding)

    rows: list[dict] = []
    grid_id = 1
    for x in np.arange(x_min, x_max + grid_size, grid_size):
        for y in np.arange(y_min, y_max + grid_size, grid_size):
            if point_in_any_building(float(x), float(y), buildings):
                continue
            if not _point_near_any_street(float(x), float(y), streets, street_margin):
                continue
            rows.append(
                {
                    "grid_id": f"G{grid_id:05d}",
                    "x": round(float(x), 3),
                    "y": round(float(y), 3),
                    "z": ground_z,
                }
            )
            grid_id += 1
    return pd.DataFrame(rows)


def estimate_site_diagonal(buildings: pd.DataFrame, streets: pd.DataFrame, site_config: dict) -> float:
    """Estimate maximum ray length needed for simple shadow marching."""
    padding = float(site_config.get("bounds_padding_m", 5.0))
    x_min, x_max, y_min, y_max = compute_site_bounds(buildings, streets, padding)
    return float(((x_max - x_min) ** 2 + (y_max - y_min) ** 2) ** 0.5)

