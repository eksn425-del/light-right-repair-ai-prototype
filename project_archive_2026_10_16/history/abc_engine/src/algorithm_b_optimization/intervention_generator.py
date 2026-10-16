from __future__ import annotations

import math

import pandas as pd

from src.geometry.mesh_utils import (
    box_conflicts_with_protected_zones,
    distance_point_to_rect,
    is_building_editable,
)
from src.io.load_tables import to_bool


def _light_gain_from_severity(severity: str) -> float:
    mapping = {"high": 5.0, "medium": 3.2, "low": 1.6}
    return mapping.get(str(severity).lower(), 2.0)


def _find_building(buildings: pd.DataFrame, building_id: str) -> pd.Series | None:
    match = buildings[buildings["building_id"].astype(str) == str(building_id)]
    if match.empty:
        return None
    return match.iloc[0]


def _nearest_editable_building(x: float, y: float, buildings: pd.DataFrame) -> pd.Series | None:
    editable = buildings[buildings.apply(is_building_editable, axis=1)]
    if editable.empty:
        return None
    distances = editable.apply(lambda row: distance_point_to_rect(x, y, row), axis=1)
    return editable.loc[distances.idxmin()]


def _intervention_box(row: dict) -> dict:
    sx = max(float(row["size_x"]), 0.2)
    sy = max(float(row["size_y"]), 0.2)
    sz = max(float(row["size_z"]), 0.2)
    return {
        "x_min": float(row["x"]) - sx / 2,
        "x_max": float(row["x"]) + sx / 2,
        "y_min": float(row["y"]) - sy / 2,
        "y_max": float(row["y"]) + sy / 2,
        "z_min": float(row["z"]),
        "z_max": float(row["z"]) + sz,
    }


def _make_subtract(
    intervention_id: str,
    dark_zone: pd.Series,
    buildings: pd.DataFrame,
    protected_zones: pd.DataFrame,
) -> dict | None:
    target = _find_building(buildings, str(dark_zone.get("nearest_building_id", "")))
    if target is None or not is_building_editable(target):
        target = _nearest_editable_building(float(dark_zone["x"]), float(dark_zone["y"]), buildings)
    if target is None:
        return None

    x = min(max(float(dark_zone["x"]), float(target["x_min"])), float(target["x_max"]))
    if float(dark_zone["y"]) >= (float(target["y_min"]) + float(target["y_max"])) / 2:
        y = float(target["y_max"])
    else:
        y = float(target["y_min"])
    height = float(target["height_m"])
    size_x = min(3.0, max(1.5, (float(target["x_max"]) - float(target["x_min"])) * 0.25))
    size_y = 2.5
    size_z = min(3.0, max(1.5, height * 0.25))
    row = {
        "intervention_id": intervention_id,
        "type": "subtract",
        "target_building_id": target["building_id"],
        "x": round(x, 3),
        "y": round(y, 3),
        "z": round(max(height - size_z, 0.0), 3),
        "size_x": round(size_x, 3),
        "size_y": round(size_y, 3),
        "size_z": round(size_z, 3),
        "volume_change": round(-size_x * size_y * size_z, 3),
        "expected_light_gain": _light_gain_from_severity(str(dark_zone.get("severity", ""))),
        "protected_conflict": bool(to_bool(target.get("protected", False))),
        "notes": "reference void box for local corner/overhang reduction",
    }
    row["protected_conflict"] = row["protected_conflict"] or box_conflicts_with_protected_zones(
        _intervention_box(row), protected_zones
    )
    return row


def _make_add(
    intervention_id: str,
    gap: pd.Series,
    protected_zones: pd.DataFrame,
) -> dict:
    potential = float(gap.get("estimated_potential", 1.0))
    size_x = 2.8
    size_y = 2.2
    size_z = 3.0
    row = {
        "intervention_id": intervention_id,
        "type": "add",
        "target_building_id": f"{gap.get('related_building_1', '')}|{gap.get('related_building_2', '')}",
        "x": round(float(gap["x"]), 3),
        "y": round(float(gap["y"]), 3),
        "z": 0.0,
        "size_x": size_x,
        "size_y": size_y,
        "size_z": size_z,
        "volume_change": round(size_x * size_y * size_z, 3),
        "expected_light_gain": round(max(1.0, potential * 1.2), 3),
        "protected_conflict": False,
        "notes": "small inserted light/gray-space block; geometry is a placeholder",
    }
    row["protected_conflict"] = box_conflicts_with_protected_zones(_intervention_box(row), protected_zones)
    return row


def _make_reorganize(
    intervention_id: str,
    gap: pd.Series,
    protected_zones: pd.DataFrame,
) -> dict:
    potential = float(gap.get("estimated_potential", 1.0))
    size_x = 5.0
    size_y = 1.6
    size_z = 2.8
    row = {
        "intervention_id": intervention_id,
        "type": "reorganize",
        "target_building_id": f"{gap.get('related_building_1', '')}|{gap.get('related_building_2', '')}",
        "x": round(float(gap["x"]), 3),
        "y": round(float(gap["y"]), 3),
        "z": 0.0,
        "size_x": size_x,
        "size_y": size_y,
        "size_z": size_z,
        "volume_change": round(-size_x * size_y * size_z * 0.3, 3),
        "expected_light_gain": round(max(0.8, potential * 0.9), 3),
        "protected_conflict": False,
        "notes": "open ground-level gray space or passage; no boolean geometry yet",
    }
    row["protected_conflict"] = box_conflicts_with_protected_zones(_intervention_box(row), protected_zones)
    return row


def _make_zone_add(intervention_id: str, zone: pd.Series, protected_zones: pd.DataFrame) -> dict:
    """Generate a small public-space insertion for a task-book zone."""
    size = 3.0
    x = (float(zone["x_min"]) + float(zone["x_max"])) / 2
    y = (float(zone["y_min"]) + float(zone["y_max"])) / 2
    priority = float(zone.get("priority", 3))
    row = {
        "intervention_id": intervention_id,
        "type": "add",
        "target_building_id": f"zone:{zone['zone_id']}",
        "x": round(x, 3),
        "y": round(y, 3),
        "z": 0.0,
        "size_x": size,
        "size_y": size,
        "size_z": size,
        "volume_change": round(size * size * size, 3),
        "expected_light_gain": round(max(1.0, priority * 0.8), 3),
        "protected_conflict": bool(to_bool(zone.get("protected", False))),
        "notes": f"3m public micro-device / memory container for {zone.get('zone_type', 'zone')}",
    }
    row["protected_conflict"] = row["protected_conflict"] or box_conflicts_with_protected_zones(
        _intervention_box(row), protected_zones
    )
    return row


def _make_zone_reorganize(intervention_id: str, zone: pd.Series, protected_zones: pd.DataFrame) -> dict:
    """Generate a ground-level reorganization action for a task-book zone."""
    x = (float(zone["x_min"]) + float(zone["x_max"])) / 2
    y = (float(zone["y_min"]) + float(zone["y_max"])) / 2
    size_x = min(12.0, max(4.0, (float(zone["x_max"]) - float(zone["x_min"])) * 0.5))
    size_y = min(4.0, max(1.8, (float(zone["y_max"]) - float(zone["y_min"])) * 0.25))
    size_z = 0.2
    priority = float(zone.get("priority", 3))
    row = {
        "intervention_id": intervention_id,
        "type": "reorganize",
        "target_building_id": f"zone:{zone['zone_id']}",
        "x": round(x, 3),
        "y": round(y, 3),
        "z": 0.0,
        "size_x": round(size_x, 3),
        "size_y": round(size_y, 3),
        "size_z": size_z,
        "volume_change": round(-size_x * size_y * max(size_z, 0.2), 3),
        "expected_light_gain": round(max(1.0, priority * 0.7), 3),
        "protected_conflict": bool(to_bool(zone.get("protected", False))),
        "notes": f"slow-path / parking / idle-space reorganization for {zone.get('zone_type', 'zone')}",
    }
    row["protected_conflict"] = row["protected_conflict"] or box_conflicts_with_protected_zones(
        _intervention_box(row), protected_zones
    )
    return row


def generate_intervention_pool(
    dark_zones: pd.DataFrame,
    gap_candidates: pd.DataFrame,
    buildings: pd.DataFrame,
    protected_zones: pd.DataFrame,
    site_zones: pd.DataFrame | None = None,
    max_dark_actions: int = 10,
    max_gap_actions: int = 8,
) -> pd.DataFrame:
    """Generate a pool of subtract/add/reorganize operations for Algorithm B."""
    rows: list[dict] = []
    counter = 1

    for _, dark_zone in dark_zones.head(max_dark_actions).iterrows():
        item = _make_subtract(f"INT{counter:04d}", dark_zone, buildings, protected_zones)
        if item is not None:
            rows.append(item)
            counter += 1

    for _, gap in gap_candidates.head(max_gap_actions).iterrows():
        rows.append(_make_add(f"INT{counter:04d}", gap, protected_zones))
        counter += 1
        rows.append(_make_reorganize(f"INT{counter:04d}", gap, protected_zones))
        counter += 1

    if site_zones is not None and not site_zones.empty:
        active_zone_types = {
            "ball_court",
            "community_node",
            "lakeside_leisure",
            "old_market",
            "parking",
            "road_edge",
            "street_corridor",
            "vacant_land",
            "vacant_public_building",
            "waterfront",
        }
        zone_candidates = site_zones[
            site_zones["zone_type"].astype(str).isin(active_zone_types)
            & ~site_zones["protected"].map(to_bool)
        ].copy()
        if "priority" in zone_candidates.columns:
            zone_candidates = zone_candidates.sort_values("priority", ascending=False)
        for _, zone in zone_candidates.head(8).iterrows():
            rows.append(_make_zone_reorganize(f"INT{counter:04d}", zone, protected_zones))
            counter += 1
            if str(zone.get("zone_type", "")) in {
                "community_node",
                "lakeside_leisure",
                "old_market",
                "vacant_land",
                "vacant_public_building",
                "waterfront",
            }:
                rows.append(_make_zone_add(f"INT{counter:04d}", zone, protected_zones))
                counter += 1

    if not rows:
        raise ValueError(
            "No intervention pool could be generated. "
            "Check that Algorithm A produced dark_zones/gap_candidates and buildings.csv has editable buildings."
        )

    pool = pd.DataFrame(rows)
    pool = pool.drop_duplicates(subset=["type", "target_building_id", "x", "y", "z"]).reset_index(drop=True)
    pool["intervention_id"] = [f"INT{index + 1:04d}" for index in range(len(pool))]
    return pool
