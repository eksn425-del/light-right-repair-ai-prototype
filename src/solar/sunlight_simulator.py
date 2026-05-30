from __future__ import annotations

import numpy as np
import pandas as pd

from src.geometry.mesh_utils import point_in_rect


def _box_from_intervention(row: pd.Series) -> dict:
    sx = max(float(row["size_x"]), 0.0)
    sy = max(float(row["size_y"]), 0.0)
    sz = max(float(row["size_z"]), 0.0)
    return {
        "x_min": float(row["x"]) - sx / 2,
        "x_max": float(row["x"]) + sx / 2,
        "y_min": float(row["y"]) - sy / 2,
        "y_max": float(row["y"]) + sy / 2,
        "z_min": float(row["z"]),
        "z_max": float(row["z"]) + sz,
    }


def _is_in_void(
    rx: float,
    ry: float,
    rz: float,
    building_id: str,
    voids: pd.DataFrame,
) -> bool:
    """Return True when a ray point passes through a proposed local subtraction/opening."""
    if voids.empty:
        return False
    building_id = str(building_id)
    for _, void in voids.iterrows():
        target = str(void.get("target_building_id", ""))
        targets = {part.strip() for part in target.split("|") if part.strip()}
        if target.startswith("zone:") or (targets and building_id not in targets):
            continue
        box = _box_from_intervention(void)
        if (
            box["x_min"] <= rx <= box["x_max"]
            and box["y_min"] <= ry <= box["y_max"]
            and box["z_min"] <= rz <= box["z_max"]
        ):
            return True
    return False


def _add_intervention_occluders(
    buildings: pd.DataFrame,
    interventions: pd.DataFrame | None,
) -> pd.DataFrame:
    """Add positive-volume intervention boxes as extra simplified occluders."""
    if interventions is None or interventions.empty:
        return buildings
    rows = []
    for _, row in interventions.iterrows():
        if str(row.get("type", "")) != "add":
            continue
        box = _box_from_intervention(row)
        rows.append(
            {
                "building_id": f"intervention:{row.get('intervention_id', '')}",
                "x_min": box["x_min"],
                "x_max": box["x_max"],
                "y_min": box["y_min"],
                "y_max": box["y_max"],
                "height_m": box["z_max"],
            }
        )
    if not rows:
        return buildings
    return pd.concat([buildings, pd.DataFrame(rows)], ignore_index=True, sort=False)


def _is_shadowed_by_buildings(
    x: float,
    y: float,
    z: float,
    sun_vector: tuple[float, float, float],
    buildings: pd.DataFrame,
    max_distance: float,
    step: float,
    voids: pd.DataFrame | None = None,
) -> bool:
    """Ray-march from a ground point toward the sun through 2.5D boxes."""
    vx, vy, vz = sun_vector
    if vz <= 0:
        return True
    voids = voids if voids is not None else pd.DataFrame()

    for distance in np.arange(step, max_distance + step, step):
        rx = x + vx * distance
        ry = y + vy * distance
        rz = z + vz * distance
        if rz > float(buildings["height_m"].max()) + 5.0:
            return False
        for _, building in buildings.iterrows():
            building_id = str(building.get("building_id", ""))
            if point_in_rect(float(rx), float(ry), building) and rz <= float(building["height_m"]):
                if _is_in_void(rx, ry, rz, building_id, voids):
                    continue
                return True
    return False


def simulate_sunlight_hours(
    ground_grid: pd.DataFrame,
    buildings: pd.DataFrame,
    sun_samples: list[dict],
    site_config: dict,
    solar_config: dict,
    max_ray_distance: float,
    interventions: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compute simplified sunlight hours for each ground grid point."""
    ray_step = float(solar_config.get("shadow_ray_step_m", 1.0))
    dark_threshold = float(site_config.get("dark_sunlight_threshold_hours", 3.0))
    active_hours = sum(float(sample["weight_hours"]) for sample in sun_samples if sample.get("is_active", True))
    interventions = interventions if interventions is not None else pd.DataFrame()
    voids = interventions[interventions.get("type", pd.Series(dtype=str)).astype(str).isin(["subtract", "reorganize"])]
    scenario_buildings = _add_intervention_occluders(buildings, interventions)

    rows: list[dict] = []
    for _, point in ground_grid.iterrows():
        sunlight_hours = 0.0
        for sample in sun_samples:
            if not sample.get("is_active", True):
                continue
            sun_vector = (
                float(sample["vector_x"]),
                float(sample["vector_y"]),
                float(sample["vector_z"]),
            )
            shadowed = _is_shadowed_by_buildings(
                float(point["x"]),
                float(point["y"]),
                float(point["z"]),
                sun_vector,
                scenario_buildings,
                max_ray_distance,
                ray_step,
                voids,
            )
            if not shadowed:
                sunlight_hours += float(sample["weight_hours"])

        shadow_hours = max(active_hours - sunlight_hours, 0.0)
        rows.append(
            {
                "grid_id": point["grid_id"],
                "x": point["x"],
                "y": point["y"],
                "sunlight_hours": round(sunlight_hours, 3),
                "shadow_hours": round(shadow_hours, 3),
                "is_dark_zone": sunlight_hours < dark_threshold,
            }
        )
    return pd.DataFrame(rows)
