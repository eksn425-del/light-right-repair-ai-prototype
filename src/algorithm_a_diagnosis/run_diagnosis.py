from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.geometry.mesh_utils import footprint_gap, is_building_editable, nearest_building, point_in_rect
from src.geometry.voxelizer import create_ground_grid, estimate_site_diagonal
from src.io.export_results import ensure_dir, write_csv, write_json
from src.io.load_obj import load_obj_mesh
from src.io.load_tables import normalise_bool_columns, read_config, read_table
from src.solar.sun_path import sample_sun_path
from src.solar.sunlight_simulator import simulate_sunlight_hours
from src.visualization.plot_heatmap import plot_sunlight_heatmap


BUILDING_COLUMNS = [
    "building_id",
    "name",
    "x_min",
    "x_max",
    "y_min",
    "y_max",
    "height_m",
    "floors",
    "movable",
    "protected",
    "facade_type",
    "notes",
]
STREET_COLUMNS = [
    "street_id",
    "start_x",
    "start_y",
    "end_x",
    "end_y",
    "width_m",
    "main_direction",
    "pedestrian_priority",
    "notes",
]
SITE_ZONE_COLUMNS = [
    "zone_id",
    "name",
    "zone_type",
    "x_min",
    "x_max",
    "y_min",
    "y_max",
    "priority",
    "needs_light_improvement",
    "needs_accessibility_improvement",
    "protected",
    "notes",
]


def _severity(sunlight_hours: float, threshold: float) -> str:
    if sunlight_hours < threshold * 0.35:
        return "high"
    if sunlight_hours < threshold * 0.7:
        return "medium"
    return "low"


def _build_dark_zones(
    sunlight: pd.DataFrame, buildings: pd.DataFrame, site_config: dict
) -> pd.DataFrame:
    threshold = float(site_config.get("dark_sunlight_threshold_hours", 3.0))
    rows: list[dict] = []
    dark = sunlight[sunlight["is_dark_zone"]].copy()
    for index, point in enumerate(dark.itertuples(index=False), start=1):
        building_id, _ = nearest_building(float(point.x), float(point.y), buildings)
        rows.append(
            {
                "dark_zone_id": f"DZ{index:04d}",
                "x": point.x,
                "y": point.y,
                "sunlight_hours": point.sunlight_hours,
                "severity": _severity(float(point.sunlight_hours), threshold),
                "nearest_building_id": building_id,
                "notes": "simplified ground-grid dark point",
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "dark_zone_id",
            "x",
            "y",
            "sunlight_hours",
            "severity",
            "nearest_building_id",
            "notes",
        ],
    )


def _nearby_dark_count(x: float, y: float, dark_zones: pd.DataFrame, radius: float = 10.0) -> int:
    if dark_zones.empty:
        return 0
    dx = dark_zones["x"].astype(float) - x
    dy = dark_zones["y"].astype(float) - y
    return int(((dx * dx + dy * dy) ** 0.5 <= radius).sum())


def _build_gap_candidates(buildings: pd.DataFrame, dark_zones: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    gap_index = 1
    for i, row_a in buildings.iterrows():
        for j, row_b in buildings.iterrows():
            if j <= i:
                continue
            same_side = (
                float(row_a["y_min"]) > 0
                and float(row_b["y_min"]) > 0
                or float(row_a["y_max"]) < 0
                and float(row_b["y_max"]) < 0
            )
            if not same_side:
                continue
            gap_distance, mid_x, _ = footprint_gap(row_a, row_b)
            y_overlap = min(float(row_a["y_max"]), float(row_b["y_max"])) - max(
                float(row_a["y_min"]), float(row_b["y_min"])
            )
            if not (1.0 <= gap_distance <= 7.0 and y_overlap > 3.0):
                continue

            street_edge_y = (
                min(float(row_a["y_min"]), float(row_b["y_min"])) - 1.0
                if float(row_a["y_min"]) > 0
                else max(float(row_a["y_max"]), float(row_b["y_max"])) + 1.0
            )
            dark_count = _nearby_dark_count(mid_x, street_edge_y, dark_zones)
            editable_bonus = 1.0 if is_building_editable(row_a) or is_building_editable(row_b) else 0.0
            raw_potential = dark_count * 0.25 + editable_bonus + gap_distance * 0.12
            potential = round(min(5.0, raw_potential), 3)
            rows.append(
                {
                    "gap_id": f"GAP{gap_index:03d}",
                    "x": round(mid_x, 3),
                    "y": round(street_edge_y, 3),
                    "related_building_1": row_a["building_id"],
                    "related_building_2": row_b["building_id"],
                    "estimated_potential": potential,
                    "notes": "between adjacent toy/white-model masses",
                }
            )
            gap_index += 1

    if not rows and not dark_zones.empty:
        for index, point in enumerate(dark_zones.head(5).itertuples(index=False), start=1):
            rows.append(
                {
                    "gap_id": f"GAP{index:03d}",
                    "x": point.x,
                    "y": point.y,
                    "related_building_1": point.nearest_building_id,
                    "related_building_2": "",
                    "estimated_potential": round(1.0 + index * 0.2, 3),
                    "notes": "fallback candidate around dark zone",
                }
            )

    return pd.DataFrame(
        rows,
        columns=[
            "gap_id",
            "x",
            "y",
            "related_building_1",
            "related_building_2",
            "estimated_potential",
            "notes",
        ],
    ).sort_values("estimated_potential", ascending=False)


def _read_optional_site_zones(dataset_dir: Path) -> pd.DataFrame:
    path = dataset_dir / "site_zones.csv"
    if not path.exists():
        return pd.DataFrame(columns=SITE_ZONE_COLUMNS)
    return normalise_bool_columns(
        read_table(path, SITE_ZONE_COLUMNS),
        ["needs_light_improvement", "needs_accessibility_improvement", "protected"],
    )


def _zone_diagnosis_label(zone_type: str, dark_ratio: float, priority: float, threshold: float) -> str:
    if dark_ratio >= threshold and priority >= 4:
        return "priority_light_and_public_space_repair"
    if "parking" in zone_type:
        return "parking_and_slow_path_reorganization"
    if zone_type in {"waterfront", "lakeside_leisure"}:
        return "waterfront_public_space_quality_check"
    if zone_type in {"vacant_land", "old_market", "vacant_public_building"}:
        return "idle_space_activation_candidate"
    return "general_context_zone"


def _build_zone_diagnosis(
    sunlight: pd.DataFrame, site_zones: pd.DataFrame, site_config: dict
) -> pd.DataFrame:
    """Summarise Algorithm A results by task-book zone."""
    columns = [
        "zone_id",
        "name",
        "zone_type",
        "grid_count",
        "average_sunlight_hours",
        "dark_zone_ratio",
        "priority",
        "diagnosis",
        "notes",
    ]
    if site_zones.empty:
        return pd.DataFrame(columns=columns)

    threshold = float(site_config.get("zone_dark_ratio_threshold", 0.35))
    rows: list[dict] = []
    for _, zone in site_zones.iterrows():
        mask = sunlight.apply(lambda point: point_in_rect(float(point["x"]), float(point["y"]), zone), axis=1)
        subset = sunlight[mask]
        if subset.empty:
            average = 0.0
            dark_ratio = 0.0
        else:
            average = float(subset["sunlight_hours"].mean())
            dark_ratio = float(subset["is_dark_zone"].mean())
        priority = float(zone.get("priority", 3))
        zone_type = str(zone.get("zone_type", "context"))
        rows.append(
            {
                "zone_id": zone["zone_id"],
                "name": zone["name"],
                "zone_type": zone_type,
                "grid_count": int(len(subset)),
                "average_sunlight_hours": round(average, 3),
                "dark_zone_ratio": round(dark_ratio, 4),
                "priority": priority,
                "diagnosis": _zone_diagnosis_label(zone_type, dark_ratio, priority, threshold),
                "notes": zone.get("notes", ""),
            }
        )
    return pd.DataFrame(rows, columns=columns).sort_values(
        ["priority", "dark_zone_ratio"], ascending=[False, False]
    )


def run_diagnosis(dataset_dir: Path, output_dir: Path, config_dir: Path) -> dict:
    """Run Algorithm A and export stable diagnosis outputs."""
    dataset_dir = Path(dataset_dir)
    output_dir = ensure_dir(Path(output_dir))
    config_dir = Path(config_dir)

    site_config = read_config(config_dir / "site_config.yaml")
    solar_config = read_config(config_dir / "solar_config.yaml")
    load_obj_mesh(dataset_dir / "site_model.obj")
    buildings = normalise_bool_columns(
        read_table(dataset_dir / "buildings.csv", BUILDING_COLUMNS),
        ["movable", "protected"],
    )
    streets = normalise_bool_columns(
        read_table(dataset_dir / "streets.csv", STREET_COLUMNS),
        ["pedestrian_priority"],
    )
    site_zones = _read_optional_site_zones(dataset_dir)

    ground_grid = create_ground_grid(buildings, streets, site_config)
    if ground_grid.empty:
        raise ValueError(
            f"No analysis grid points were generated for {dataset_dir}. "
            "Check building footprints, street width, and coordinate units."
        )

    sun_samples = sample_sun_path(site_config, solar_config)
    max_ray_distance = estimate_site_diagonal(buildings, streets, site_config)
    sunlight = simulate_sunlight_hours(
        ground_grid,
        buildings,
        sun_samples,
        site_config,
        solar_config,
        max_ray_distance,
    )
    dark_zones = _build_dark_zones(sunlight, buildings, site_config)
    gap_candidates = _build_gap_candidates(buildings, dark_zones)
    zone_diagnosis = _build_zone_diagnosis(sunlight, site_zones, site_config)

    sunlight_path = write_csv(sunlight, output_dir / "sunlight_hours.csv")
    dark_path = write_csv(dark_zones, output_dir / "dark_zones.csv")
    gap_path = write_csv(gap_candidates, output_dir / "gap_candidates.csv")
    zone_path = write_csv(zone_diagnosis, output_dir / "zone_diagnosis.csv")
    heatmap_path = plot_sunlight_heatmap(
        sunlight,
        output_dir / "heatmap.png",
        "Algorithm A sunlight-hours diagnosis",
    )

    worst = None
    if not dark_zones.empty:
        worst_row = dark_zones.sort_values("sunlight_hours").iloc[0]
        worst = {
            "x": float(worst_row["x"]),
            "y": float(worst_row["y"]),
            "sunlight_hours": float(worst_row["sunlight_hours"]),
        }

    summary = {
        "total_grid_count": int(len(sunlight)),
        "dark_grid_count": int(sunlight["is_dark_zone"].sum()),
        "dark_zone_ratio": round(float(sunlight["is_dark_zone"].mean()), 4),
        "average_sunlight_hours": round(float(sunlight["sunlight_hours"].mean()), 3),
        "worst_dark_zone_location": worst,
        "zone_count": int(len(site_zones)),
        "priority_zone_count": int((site_zones["priority"].astype(float) >= 4).sum()) if not site_zones.empty else 0,
        "config_used": {
            "site_config": site_config,
            "solar_config": solar_config,
            "dataset_dir": str(dataset_dir),
        },
    }
    summary_path = write_json(summary, output_dir / "A_summary.json")
    return {
        "sunlight_hours": sunlight_path,
        "dark_zones": dark_path,
        "gap_candidates": gap_path,
        "zone_diagnosis": zone_path,
        "heatmap": heatmap_path,
        "summary": summary_path,
        "summary_data": summary,
    }
