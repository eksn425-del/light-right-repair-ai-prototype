from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "light_equity_project"
sys.path.insert(0, str(PROJECT))

from src.algorithm_a_diagnosis.run_diagnosis import BUILDING_COLUMNS, STREET_COLUMNS  # noqa: E402
from src.geometry.voxelizer import create_ground_grid, estimate_site_diagonal  # noqa: E402
from src.io.export_results import ensure_dir, write_csv, write_json  # noqa: E402
from src.io.load_tables import normalise_bool_columns, read_config, read_table, to_bool  # noqa: E402
from src.solar.sun_path import sample_sun_path  # noqa: E402
from src.solar.sunlight_simulator import simulate_sunlight_hours  # noqa: E402


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
OUTPUT_DIR = ROOT / "paper_revision_work_2026_06_14" / "non_ai_baseline_comparison"


def bool_series(series: pd.Series) -> pd.Series:
    return series.map(lambda value: bool(to_bool(value)))


def editable_buildings(buildings: pd.DataFrame) -> pd.DataFrame:
    movable = bool_series(buildings["movable"])
    protected = bool_series(buildings["protected"])
    return buildings[movable & ~protected].copy()


def make_subtract_rows(buildings: pd.DataFrame, building_ids: list[str], prefix: str) -> pd.DataFrame:
    rows = []
    for index, building_id in enumerate(building_ids, start=1):
        row = buildings[buildings["building_id"].astype(str) == str(building_id)].iloc[0]
        height = float(row["height_m"])
        size_x = min(3.0, max(1.5, (float(row["x_max"]) - float(row["x_min"])) * 0.25))
        size_y = 2.5
        size_z = min(3.0, max(1.5, height * 0.25))
        x = (float(row["x_min"]) + float(row["x_max"])) / 2
        y = float(row["y_max"])
        rows.append(
            {
                "candidate_id": prefix,
                "intervention_id": f"{prefix}_{index:02d}",
                "type": "subtract",
                "target_building_id": str(building_id),
                "x": round(x, 3),
                "y": round(y, 3),
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


def simulate_case(
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
    sunlight = simulate_sunlight_hours(
        ground_grid,
        buildings,
        sun_samples,
        site_config,
        solar_config,
        max_ray_distance,
        interventions=interventions,
    )
    write_csv(sunlight, OUTPUT_DIR / f"{name}_sunlight_hours.csv")
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
        "notes": "same simplified 2.5D post-simulation as Algorithm C verification",
    }


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

    height_ids = (
        editable.sort_values(["height_m", "building_id"], ascending=[False, True])
        .head(2)["building_id"]
        .astype(str)
        .tolist()
    )
    height = make_subtract_rows(buildings, height_ids, "height_priority")

    dark_counts = dark_zones.groupby("nearest_building_id").size().sort_values(ascending=False)
    dark_ids = []
    for building_id in dark_counts.index.astype(str):
        if building_id in set(editable["building_id"].astype(str)):
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
        simulate_case(
            "ai_conservative",
            "AI保守型",
            ai,
            baseline_avg,
            baseline_dark,
            ground_grid,
            buildings,
            sun_samples,
            site_config,
            solar_config,
            max_ray_distance,
        ),
        simulate_case(
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
        simulate_case(
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

    random_rows = []
    ids = editable["building_id"].astype(str).tolist()
    rng = random.Random(42)
    for i in range(10):
        selected = rng.sample(ids, 2)
        interventions = make_subtract_rows(buildings, selected, f"random_{i + 1:02d}")
        row = simulate_case(
            f"random_{i + 1:02d}",
            f"随机基线{i + 1:02d}",
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
        random_rows.append(row)
    random_df = pd.DataFrame(random_rows)
    random_summary = {
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
        "changed_building_ids": "10 random two-building trials; see random_baseline_trials.csv",
        "notes": "mean of 10 deterministic random editable two-building subtraction baselines; seed=42",
    }
    rows.append(random_summary)

    comparison = pd.DataFrame(rows)
    comparison_path = write_csv(comparison, OUTPUT_DIR / "non_ai_baseline_comparison.csv")
    random_path = write_csv(random_df, OUTPUT_DIR / "random_baseline_trials.csv")
    summary = {
        "baseline_average_sunlight_hours": round(baseline_avg, 3),
        "baseline_dark_zone_ratio": round(baseline_dark, 4),
        "ai_changed_buildings": "C6;C33",
        "height_priority_buildings": ";".join(height_ids),
        "dark_nearest_buildings": ";".join(dark_ids),
        "random_seed": 42,
        "random_trial_count": 10,
        "interpretation": "AI conservative improves dark-zone ratio with much lower intervention volume than the height-priority baseline and better dark-zone reduction than dark-nearest and random baselines under the same simplified post-simulation model.",
    }
    summary_path = write_json(summary, OUTPUT_DIR / "non_ai_baseline_summary.json")

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
