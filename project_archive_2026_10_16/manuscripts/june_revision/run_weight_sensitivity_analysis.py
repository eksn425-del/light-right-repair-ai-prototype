from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "light_equity_project"
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from src.algorithm_b_optimization.run_optimization import run_optimization  # noqa: E402
from src.algorithm_a_diagnosis.run_diagnosis import BUILDING_COLUMNS, STREET_COLUMNS  # noqa: E402
from src.geometry.voxelizer import create_ground_grid, estimate_site_diagonal  # noqa: E402
from src.io.export_results import ensure_dir, write_csv, write_json  # noqa: E402
from src.io.load_tables import normalise_bool_columns, read_config, read_table  # noqa: E402
from src.solar.sun_path import sample_sun_path  # noqa: E402
from src.solar.sunlight_simulator import _apply_subtractive_height_changes  # noqa: E402


DATASET_DIR = PROJECT / "data" / "real_guankou" / "lakeside_leisure_ready"
DIAGNOSIS_DIR = PROJECT / "outputs" / "lakeside_leisure_final_6m" / "A_diagnosis"
BASE_CONFIG_DIR = PROJECT / "outputs" / "light_product_2026_06_02" / "strategy_comparison_postsim" / "_configs" / "conservative"
BASELINE_CSV = PROJECT / "outputs" / "lakeside_leisure_final_6m" / "A_diagnosis" / "sunlight_hours.csv"
OUTPUT_DIR = ROOT / "paper_revision_work_2026_06_14" / "weight_sensitivity"


BASE_WEIGHTS = {
    "light_gain": 1.0,
    "intervention_volume": 0.16,
    "new_shadow_penalty": 0.9,
    "protected_zone_penalty": 2.0,
}

VARIANTS = [
    ("base", "基准权重", BASE_WEIGHTS),
    ("light_minus_50", "光照收益 -50%", {**BASE_WEIGHTS, "light_gain": BASE_WEIGHTS["light_gain"] * 0.5}),
    ("light_plus_50", "光照收益 +50%", {**BASE_WEIGHTS, "light_gain": BASE_WEIGHTS["light_gain"] * 1.5}),
    (
        "volume_minus_50",
        "体量惩罚 -50%",
        {**BASE_WEIGHTS, "intervention_volume": BASE_WEIGHTS["intervention_volume"] * 0.5},
    ),
    (
        "volume_plus_50",
        "体量惩罚 +50%",
        {**BASE_WEIGHTS, "intervention_volume": BASE_WEIGHTS["intervention_volume"] * 1.5},
    ),
    (
        "shadow_minus_50",
        "新阴影惩罚 -50%",
        {**BASE_WEIGHTS, "new_shadow_penalty": BASE_WEIGHTS["new_shadow_penalty"] * 0.5},
    ),
    (
        "shadow_plus_50",
        "新阴影惩罚 +50%",
        {**BASE_WEIGHTS, "new_shadow_penalty": BASE_WEIGHTS["new_shadow_penalty"] * 1.5},
    ),
]


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def prepare_config(variant_id: str, weights: dict) -> Path:
    config_dir = ensure_dir(OUTPUT_DIR / "_configs" / variant_id)
    for name in ["solar_config.yaml", "accessibility_rules.yaml"]:
        shutil.copy2(BASE_CONFIG_DIR / name, config_dir / name)
    site = load_yaml(BASE_CONFIG_DIR / "site_config.yaml")
    site.update(
        {
            "candidate_count": 3,
            "search_iterations": 220,
            "max_interventions_per_candidate": 2,
            "random_seed": 42,
            "grid_size_m": 6.0,
            "score_weight_light_gain": float(weights["light_gain"]),
            "score_weight_intervention_volume": float(weights["intervention_volume"]),
            "score_weight_new_shadow_penalty": float(weights["new_shadow_penalty"]),
            "score_weight_protected_zone_penalty": float(weights["protected_zone_penalty"]),
            "sensitivity_case": f"weight_sensitivity_{variant_id}",
        }
    )
    write_yaml(config_dir / "site_config.yaml", site)
    return config_dir


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"true", "1", "yes", "y"})


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


def main() -> None:
    ensure_dir(OUTPUT_DIR)
    baseline = pd.read_csv(BASELINE_CSV)
    baseline_avg = float(baseline["sunlight_hours"].mean())
    baseline_dark = float(bool_series(baseline["is_dark_zone"]).mean())
    buildings = normalise_bool_columns(
        read_table(DATASET_DIR / "buildings.csv", BUILDING_COLUMNS),
        ["movable", "protected"],
    )
    streets = normalise_bool_columns(
        read_table(DATASET_DIR / "streets.csv", STREET_COLUMNS),
        ["pedestrian_priority"],
    )

    rows = []
    for variant_id, label, weights in VARIANTS:
        config_dir = prepare_config(variant_id, weights)
        b_dir = ensure_dir(OUTPUT_DIR / variant_id / "B_candidates")
        run_optimization(DATASET_DIR, DIAGNOSIS_DIR, b_dir, config_dir)
        scores = pd.read_csv(b_dir / "candidate_scores.csv")
        interventions_all = pd.read_csv(b_dir / "interventions.csv")
        best_id = str(scores.iloc[0]["candidate_id"])
        selected = interventions_all[interventions_all["candidate_id"].astype(str) == best_id].copy()

        site_config = read_config(config_dir / "site_config.yaml")
        solar_config = read_config(config_dir / "solar_config.yaml")
        ground_grid = create_ground_grid(buildings, streets, site_config)
        sun_samples = sample_sun_path(site_config, solar_config)
        max_ray_distance = estimate_site_diagonal(buildings, streets, site_config)
        sunlight = fast_simulate(ground_grid, buildings, sun_samples, site_config, solar_config, max_ray_distance, selected)
        write_csv(sunlight, OUTPUT_DIR / variant_id / "post_sunlight_hours_fast.csv")

        post_avg = float(sunlight["sunlight_hours"].mean())
        post_dark = float(bool_series(sunlight["is_dark_zone"]).mean())
        changed_ids = ";".join(selected["target_building_id"].astype(str).tolist())
        rows.append(
            {
                "variant_id": variant_id,
                "variant_label": label,
                "weight_light_gain": round(float(weights["light_gain"]), 4),
                "weight_intervention_volume": round(float(weights["intervention_volume"]), 4),
                "weight_new_shadow_penalty": round(float(weights["new_shadow_penalty"]), 4),
                "weight_protected_zone_penalty": round(float(weights["protected_zone_penalty"]), 4),
                "best_candidate_id": best_id,
                "changed_building_ids": changed_ids,
                "intervention_count": int(len(selected)),
                "intervention_volume": round(float(selected["volume_change"].abs().sum()), 3),
                "score_total": round(float(scores.iloc[0]["total_score"]), 3),
                "estimated_light_gain": round(float(scores.iloc[0]["estimated_light_gain"]), 3),
                "post_average_sunlight_hours": round(post_avg, 3),
                "post_dark_zone_ratio": round(post_dark, 4),
                "post_dark_zone_percent": round(post_dark * 100, 2),
                "dark_zone_drop_percentage_points": round((baseline_dark - post_dark) * 100, 2),
                "relative_dark_zone_improvement": round((baseline_dark - post_dark) / baseline_dark, 4) if baseline_dark else 0,
                "sunlight_gain_h": round(post_avg - baseline_avg, 3),
            }
        )

    results = pd.DataFrame(rows)
    metrics_path = write_csv(results, OUTPUT_DIR / "weight_sensitivity_metrics.csv")
    c6c33_count = int(results["changed_building_ids"].eq("C6;C33").sum())
    summary = {
        "baseline_average_sunlight_hours": round(baseline_avg, 3),
        "baseline_dark_zone_percent": round(baseline_dark * 100, 2),
        "variant_count": int(len(results)),
        "c6_c33_variant_count": c6c33_count,
        "c6_c33_variant_ratio": round(c6c33_count / len(results), 3),
        "post_dark_zone_percent_min": round(float(results["post_dark_zone_percent"].min()), 2),
        "post_dark_zone_percent_max": round(float(results["post_dark_zone_percent"].max()), 2),
        "intervention_volume_min": round(float(results["intervention_volume"].min()), 3),
        "intervention_volume_max": round(float(results["intervention_volume"].max()), 3),
        "method": "Algorithm B re-run under ±50% single-factor weight perturbations; post metrics use vectorized reproduction of the same simplified 2.5D effective-height model.",
        "metrics_csv": str(metrics_path),
    }
    summary_path = write_json(summary, OUTPUT_DIR / "weight_sensitivity_summary.json")
    print(json.dumps({"summary": str(summary_path), "metrics": str(metrics_path), "data": summary, "rows": rows}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
