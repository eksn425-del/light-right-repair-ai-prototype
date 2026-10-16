from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "light_equity_project"
sys.path.insert(0, str(PROJECT))

from src.algorithm_a_diagnosis.run_diagnosis import BUILDING_COLUMNS, STREET_COLUMNS  # noqa: E402
from src.geometry.voxelizer import create_ground_grid, estimate_site_diagonal  # noqa: E402
from src.io.export_results import ensure_dir, write_csv, write_json  # noqa: E402
from src.io.load_tables import normalise_bool_columns, read_config, read_table, to_bool  # noqa: E402
from src.solar.sun_path import sample_sun_path  # noqa: E402
from src.solar.sunlight_simulator import _apply_subtractive_height_changes  # noqa: E402


DATASET_DIR = PROJECT / "data" / "real_guankou" / "lakeside_leisure_ready"
CONFIG_DIR = PROJECT / "outputs" / "lakeside_leisure_final_6m_config"
DIAGNOSIS_DIR = PROJECT / "outputs" / "lakeside_leisure_final_6m" / "A_diagnosis"
AI_INTERVENTIONS = (
    PROJECT
    / "outputs"
    / "light_product_2026_06_02"
    / "strategy_comparison_postsim"
    / "conservative"
    / "B_candidates"
    / "interventions.csv"
)
AI_OFFICIAL_SUMMARY = (
    PROJECT
    / "outputs"
    / "light_product_2026_06_02"
    / "strategy_comparison_postsim"
    / "conservative"
    / "post_simulation"
    / "algorithm_post_simulation_summary.json"
)
OUTPUT_DIR = ROOT / "paper_revision_work_2026_06_14" / "non_ai_baseline_comparison"


def as_bool(value) -> bool:
    return bool(to_bool(value))


def editable_buildings(buildings: pd.DataFrame) -> pd.DataFrame:
    return buildings[
        buildings["movable"].map(as_bool) & ~buildings["protected"].map(as_bool)
    ].copy()


def make_subtract_rows(buildings: pd.DataFrame, building_ids: list[str], prefix: str) -> pd.DataFrame:
    rows = []
    for index, building_id in enumerate(building_ids, start=1):
        row = buildings[buildings["building_id"].astype(str) == str(building_id)].iloc[0]
        height = float(row["height_m"])
        size_x = min(3.0, max(1.5, (float(row["x_max"]) - float(row["x_min"])) * 0.25))
        size_y = 2.5
        size_z = min(3.0, max(1.5, height * 0.25))
        rows.append(
            {
                "candidate_id": prefix,
                "intervention_id": f"{prefix}_{index:02d}",
                "type": "subtract",
                "target_building_id": str(building_id),
                "x": round((float(row["x_min"]) + float(row["x_max"])) / 2, 3),
                "y": round(float(row["y_max"]), 3),
                "z": round(max(height - size_z, 0.0), 3),
                "size_x": round(size_x, 3),
                "size_y": round(size_y, 3),
                "size_z": round(size_z, 3),
                "volume_change": round(-size_x * size_y * size_z, 3),
                "expected_light_gain": 0.0,
                "protected_conflict": False,
                "notes": f"non-AI baseline subtract rule: {prefix}",
            }
        )
    return pd.DataFrame(rows)


def fast_simulate(
    ground_grid: pd.DataFrame,
    buildings: pd.DataFrame,
    sun_samples: list[dict],
    site_config: dict,
    solar_config: dict,
    max_ray_distance: float,
    interventions: pd.DataFrame,
) -> pd.DataFrame:
    scenario = _apply_subtractive_height_changes(buildings, interventions, site_config)
    x_min = scenario["x_min"].astype(float).to_numpy()
    x_max = scenario["x_max"].astype(float).to_numpy()
    y_min = scenario["y_min"].astype(float).to_numpy()
    y_max = scenario["y_max"].astype(float).to_numpy()
    heights = scenario["height_m"].astype(float).to_numpy()
    max_height = float(np.max(heights))
    ray_step = float(solar_config.get("shadow_ray_step_m", 2.0))
    dark_threshold = float(site_config.get("dark_sunlight_threshold_hours", 3.0))
    distances_all = np.arange(ray_step, max_ray_distance + ray_step, ray_step)
    active_hours = sum(float(sample["weight_hours"]) for sample in sun_samples if sample.get("is_active", True))

    rows = []
    for _, point in ground_grid.iterrows():
        px = float(point["x"])
        py = float(point["y"])
        pz = float(point["z"])
        sunlight_hours = 0.0
        for sample in sun_samples:
            if not sample.get("is_active", True):
                continue
            vx = float(sample["vector_x"])
            vy = float(sample["vector_y"])
            vz = float(sample["vector_z"])
            if vz <= 0:
                shadowed = True
            else:
                rz = pz + vz * distances_all
                active = rz <= max_height + 5.0
                if not np.any(active):
                    shadowed = False
                else:
                    d = distances_all[active]
                    rz = rz[active]
                    rx = px + vx * d
                    ry = py + vy * d
                    inside = (
                        (rx[:, None] >= x_min[None, :])
                        & (rx[:, None] <= x_max[None, :])
                        & (ry[:, None] >= y_min[None, :])
                        & (ry[:, None] <= y_max[None, :])
                        & (rz[:, None] <= heights[None, :])
                    )
                    shadowed = bool(np.any(inside))
            if not shadowed:
                sunlight_hours += float(sample["weight_hours"])
        rows.append(
            {
                "grid_id": point["grid_id"],
                "x": point["x"],
                "y": point["y"],
                "sunlight_hours": round(sunlight_hours, 3),
                "shadow_hours": round(max(active_hours - sunlight_hours, 0.0), 3),
                "is_dark_zone": sunlight_hours < dark_threshold,
            }
        )
    return pd.DataFrame(rows)


def summarize_case(
    name: str,
    label: str,
    sunlight: pd.DataFrame,
    interventions: pd.DataFrame,
    baseline_avg: float,
    baseline_dark: float,
) -> dict:
    avg = float(sunlight["sunlight_hours"].mean())
    dark = float(sunlight["is_dark_zone"].mean())
    volume = float(interventions["volume_change"].abs().sum()) if not interventions.empty else 0.0
    ids = ";".join(interventions["target_building_id"].astype(str).tolist()) if not interventions.empty else ""
    return {
        "case_id": name,
        "case_label": label,
        "average_sunlight_hours": round(avg, 3),
        "dark_zone_ratio": round(dark, 4),
        "dark_zone_ratio_percent": round(dark * 100, 2),
        "dark_zone_drop": round(baseline_dark - dark, 4),
        "relative_dark_improvement": round((baseline_dark - dark) / baseline_dark, 4) if baseline_dark else 0.0,
        "sunlight_gain_hours": round(avg - baseline_avg, 3),
        "intervention_volume": round(volume, 3),
        "changed_building_count": int(len(interventions)),
        "changed_building_ids": ids,
        "notes": "fast vectorized reproduction of the same 2.5D height-reduction post-simulation logic",
    }


def run_case(
    name: str,
    label: str,
    interventions: pd.DataFrame,
    baseline_avg: float,
    baseline_dark: float,
    ground_grid: pd.DataFrame,
    buildings: pd.DataFrame,
    sun_samples: list[dict],
    site_config: dict,
    solar_config: dict,
    max_ray_distance: float,
) -> dict:
    sunlight = fast_simulate(
        ground_grid,
        buildings,
        sun_samples,
        site_config,
        solar_config,
        max_ray_distance,
        interventions,
    )
    write_csv(sunlight, OUTPUT_DIR / f"{name}_sunlight_hours_fast.csv")
    return summarize_case(name, label, sunlight, interventions, baseline_avg, baseline_dark)


def main() -> None:
    ensure_dir(OUTPUT_DIR)
    site_config = read_config(CONFIG_DIR / "site_config.yaml")
    solar_config = read_config(CONFIG_DIR / "solar_config.yaml")
    buildings = normalise_bool_columns(
        read_table(DATASET_DIR / "buildings.csv", BUILDING_COLUMNS),
        ["movable", "protected"],
    )
    streets = normalise_bool_columns(
        read_table(DATASET_DIR / "streets.csv", STREET_COLUMNS),
        ["pedestrian_priority"],
    )
    baseline = pd.read_csv(DIAGNOSIS_DIR / "sunlight_hours.csv")
    dark_zones = pd.read_csv(DIAGNOSIS_DIR / "dark_zones.csv")
    baseline_avg = float(baseline["sunlight_hours"].mean())
    baseline_dark = float(baseline["is_dark_zone"].astype(str).str.lower().isin({"true", "1", "yes"}).mean())
    ground_grid = create_ground_grid(buildings, streets, site_config)
    sun_samples = sample_sun_path(site_config, solar_config)
    max_ray_distance = estimate_site_diagonal(buildings, streets, site_config)
    editable = editable_buildings(buildings)

    ai_all = pd.read_csv(AI_INTERVENTIONS)
    ai = ai_all[ai_all["candidate_id"].astype(str) == "candidate_01"].copy()
    official_ai = json.loads(AI_OFFICIAL_SUMMARY.read_text(encoding="utf-8"))

    height_ids = (
        editable.sort_values(["height_m", "building_id"], ascending=[False, True])
        .head(2)["building_id"]
        .astype(str)
        .tolist()
    )
    height = make_subtract_rows(buildings, height_ids, "height_priority")

    dark_counts = dark_zones.groupby("nearest_building_id").size().sort_values(ascending=False)
    dark_ids = []
    editable_ids = set(editable["building_id"].astype(str))
    for building_id in dark_counts.index.astype(str):
        if building_id in editable_ids:
            dark_ids.append(building_id)
        if len(dark_ids) >= 2:
            break
    dark_nearest = make_subtract_rows(buildings, dark_ids, "dark_nearest")

    rows = [
        {
            "case_id": "baseline",
            "case_label": "现状",
            "average_sunlight_hours": round(baseline_avg, 3),
            "dark_zone_ratio": round(baseline_dark, 4),
            "dark_zone_ratio_percent": round(baseline_dark * 100, 2),
            "dark_zone_drop": 0.0,
            "relative_dark_improvement": 0.0,
            "sunlight_gain_hours": 0.0,
            "intervention_volume": 0.0,
            "changed_building_count": 0,
            "changed_building_ids": "",
            "notes": "baseline from Algorithm A",
        },
        {
            "case_id": "ai_conservative",
            "case_label": "AI保守型",
            "average_sunlight_hours": round(float(official_ai["average_sunlight_hours"]), 3),
            "dark_zone_ratio": round(float(official_ai["dark_zone_ratio"]), 4),
            "dark_zone_ratio_percent": round(float(official_ai["dark_zone_ratio"]) * 100, 2),
            "dark_zone_drop": round(baseline_dark - float(official_ai["dark_zone_ratio"]), 4),
            "relative_dark_improvement": round((baseline_dark - float(official_ai["dark_zone_ratio"])) / baseline_dark, 4),
            "sunlight_gain_hours": round(float(official_ai["average_sunlight_hours"]) - baseline_avg, 3),
            "intervention_volume": round(float(ai["volume_change"].abs().sum()), 3),
            "changed_building_count": int(len(ai)),
            "changed_building_ids": ";".join(ai["target_building_id"].astype(str).tolist()),
            "notes": "official slow post-simulation result from existing paper pipeline",
        },
        run_case(
            "height_priority",
            "高度优先基线",
            height,
            baseline_avg,
            baseline_dark,
            ground_grid,
            buildings,
            sun_samples,
            site_config,
            solar_config,
            max_ray_distance,
        ),
        run_case(
            "dark_nearest",
            "暗区邻近基线",
            dark_nearest,
            baseline_avg,
            baseline_dark,
            ground_grid,
            buildings,
            sun_samples,
            site_config,
            solar_config,
            max_ray_distance,
        ),
    ]

    rng = random.Random(42)
    random_rows = []
    ids = editable["building_id"].astype(str).tolist()
    for index in range(10):
        selected = rng.sample(ids, 2)
        interventions = make_subtract_rows(buildings, selected, f"random_{index + 1:02d}")
        random_rows.append(
            run_case(
                f"random_{index + 1:02d}",
                f"随机基线{index + 1:02d}",
                interventions,
                baseline_avg,
                baseline_dark,
                ground_grid,
                buildings,
                sun_samples,
                site_config,
                solar_config,
                max_ray_distance,
            )
        )
    random_df = pd.DataFrame(random_rows)
    rows.append(
        {
            "case_id": "random_10_mean",
            "case_label": "随机基线均值",
            "average_sunlight_hours": round(float(random_df["average_sunlight_hours"].mean()), 3),
            "dark_zone_ratio": round(float(random_df["dark_zone_ratio"].mean()), 4),
            "dark_zone_ratio_percent": round(float(random_df["dark_zone_ratio_percent"].mean()), 2),
            "dark_zone_drop": round(float(random_df["dark_zone_drop"].mean()), 4),
            "relative_dark_improvement": round(float(random_df["relative_dark_improvement"].mean()), 4),
            "sunlight_gain_hours": round(float(random_df["sunlight_gain_hours"].mean()), 3),
            "intervention_volume": round(float(random_df["intervention_volume"].mean()), 3),
            "changed_building_count": 2,
            "changed_building_ids": "10 deterministic random trials; see random_baseline_trials_fast.csv",
            "notes": "mean of 10 deterministic random editable two-building baselines; seed=42",
        }
    )

    comparison = pd.DataFrame(rows)
    comparison_path = write_csv(comparison, OUTPUT_DIR / "non_ai_baseline_comparison_fast.csv")
    random_path = write_csv(random_df, OUTPUT_DIR / "random_baseline_trials_fast.csv")
    summary = {
        "height_priority_buildings": ";".join(height_ids),
        "dark_nearest_buildings": ";".join(dark_ids),
        "random_seed": 42,
        "random_trial_count": 10,
        "important_caveat": "Non-AI baselines use a vectorized reproduction of the same simplified 2.5D height-reduction logic; the AI row uses the existing official slow post-simulation result.",
    }
    summary_path = write_json(summary, OUTPUT_DIR / "non_ai_baseline_summary_fast.json")
    print(
        json.dumps(
            {
                "comparison": str(comparison_path),
                "random_trials": str(random_path),
                "summary": str(summary_path),
                "rows": comparison.to_dict(orient="records"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
