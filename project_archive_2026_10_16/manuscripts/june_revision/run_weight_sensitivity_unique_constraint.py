from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "light_equity_project"
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from run_weight_sensitivity_analysis import (  # noqa: E402
    BASELINE_CSV,
    BASE_CONFIG_DIR,
    DATASET_DIR,
    DIAGNOSIS_DIR,
    OUTPUT_DIR as BASE_OUTPUT_DIR,
    VARIANTS,
    bool_series,
    fast_simulate,
    prepare_config,
)
from src.algorithm_a_diagnosis.run_diagnosis import BUILDING_COLUMNS, SITE_ZONE_COLUMNS, STREET_COLUMNS  # noqa: E402
from src.algorithm_b_optimization.intervention_constraints import (  # noqa: E402
    apply_intervention_levels_to_buildings,
    filter_intervention_pool_by_constraints,
    load_intervention_levels,
)
from src.algorithm_b_optimization.intervention_generator import generate_intervention_pool  # noqa: E402
from src.algorithm_b_optimization.scoring import score_interventions  # noqa: E402
from src.algorithm_b_optimization.simulated_annealing import search_candidate_sets  # noqa: E402
from src.geometry.voxelizer import create_ground_grid, estimate_site_diagonal  # noqa: E402
from src.io.export_results import ensure_dir, write_csv, write_json  # noqa: E402
from src.io.load_tables import normalise_bool_columns, read_config, read_table  # noqa: E402
from src.solar.sun_path import sample_sun_path  # noqa: E402


OUTPUT_DIR = ROOT / "paper_revision_work_2026_06_14" / "weight_sensitivity_unique_constraint"
PROTECTED_ZONE_COLUMNS = [
    "zone_id",
    "x_min",
    "x_max",
    "y_min",
    "y_max",
    "z_min",
    "z_max",
    "reason",
    "notes",
]


def _read_optional_site_zones(dataset_dir: Path) -> pd.DataFrame:
    path = dataset_dir / "site_zones.csv"
    if not path.exists():
        return pd.DataFrame(columns=SITE_ZONE_COLUMNS)
    return normalise_bool_columns(
        read_table(path, SITE_ZONE_COLUMNS),
        ["needs_light_improvement", "needs_accessibility_improvement", "protected"],
    )


def _is_unique_target_set(pool: pd.DataFrame, indices: list[int]) -> bool:
    targets = pool.loc[indices, "target_building_id"].astype(str).tolist()
    return len(targets) == len(set(targets))


def _best_unique_candidate(pool: pd.DataFrame, weights: dict, site_config: dict) -> dict:
    ranked = search_candidate_sets(
        pool,
        weights,
        iterations=int(site_config.get("search_iterations", 220)),
        candidate_count=120,
        max_interventions_per_candidate=int(site_config.get("max_interventions_per_candidate", 2)),
        seed=int(site_config.get("random_seed", 42)),
    )
    unique_ranked = [item for item in ranked if _is_unique_target_set(pool, item["indices"])]
    if unique_ranked:
        return unique_ranked[0]
    # Fallback should rarely happen; keep the highest single intervention rather than duplicate a building.
    singles = [
        {"indices": [int(index)], "metrics": score_interventions(pool.loc[[index]], weights)}
        for index in pool.index
    ]
    return sorted(singles, key=lambda item: item["metrics"]["total_score"], reverse=True)[0]


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
    dark_zones = read_table(DIAGNOSIS_DIR / "dark_zones.csv")
    gap_candidates = read_table(DIAGNOSIS_DIR / "gap_candidates.csv")
    protected_zones = read_table(DATASET_DIR / "protected_zones.csv", PROTECTED_ZONE_COLUMNS)
    site_zones = _read_optional_site_zones(DATASET_DIR)

    rows: list[dict] = []
    for variant_id, label, weights in VARIANTS:
        config_dir = prepare_config(f"unique_{variant_id}", weights)
        site_config = read_config(config_dir / "site_config.yaml")
        solar_config = read_config(config_dir / "solar_config.yaml")
        intervention_levels, _ = load_intervention_levels(DATASET_DIR, site_config)
        constrained_buildings = apply_intervention_levels_to_buildings(buildings.copy(), intervention_levels)
        pool = generate_intervention_pool(
            dark_zones,
            gap_candidates,
            constrained_buildings,
            protected_zones,
            site_zones=site_zones,
        )
        pool, _ = filter_intervention_pool_by_constraints(pool, constrained_buildings, intervention_levels)
        candidate = _best_unique_candidate(pool, weights, site_config)
        selected = pool.loc[candidate["indices"]].copy()
        selected.insert(0, "candidate_id", "candidate_01")

        ground_grid = create_ground_grid(buildings, streets, site_config)
        sun_samples = sample_sun_path(site_config, solar_config)
        max_ray_distance = estimate_site_diagonal(buildings, streets, site_config)
        sunlight = fast_simulate(
            ground_grid,
            buildings,
            sun_samples,
            site_config,
            solar_config,
            max_ray_distance,
            selected,
        )

        case_dir = ensure_dir(OUTPUT_DIR / variant_id)
        write_csv(selected, case_dir / "selected_unique_interventions.csv")
        write_csv(sunlight, case_dir / "post_sunlight_hours_fast.csv")

        post_avg = float(sunlight["sunlight_hours"].mean())
        post_dark = float(bool_series(sunlight["is_dark_zone"]).mean())
        changed_ids = ";".join(selected["target_building_id"].astype(str).tolist())
        rows.append(
            {
                "variant_id": variant_id,
                "variant_label": label,
                "changed_building_ids": changed_ids,
                "intervention_count": int(len(selected)),
                "intervention_volume": round(float(selected["volume_change"].abs().sum()), 3),
                "score_total": round(float(score_interventions(selected, weights)["total_score"]), 3),
                "post_average_sunlight_hours": round(post_avg, 3),
                "post_dark_zone_percent": round(post_dark * 100, 2),
                "dark_zone_drop_percentage_points": round((baseline_dark - post_dark) * 100, 2),
                "sunlight_gain_h": round(post_avg - baseline_avg, 3),
            }
        )

    results = pd.DataFrame(rows)
    metrics_path = write_csv(results, OUTPUT_DIR / "weight_sensitivity_unique_constraint_metrics.csv")
    summary = {
        "baseline_average_sunlight_hours": round(baseline_avg, 3),
        "baseline_dark_zone_percent": round(baseline_dark * 100, 2),
        "variant_count": int(len(results)),
        "duplicate_target_count": int(results["changed_building_ids"].str.contains(r"(^|;)C6;C6($|;)", regex=True).sum()),
        "c6_c33_variant_count": int(results["changed_building_ids"].eq("C6;C33").sum()),
        "best_dark_zone_percent": round(float(results["post_dark_zone_percent"].min()), 2),
        "notes": (
            "Supplementary weight-sensitivity rerun with a unique-target constraint inside each candidate set. "
            "This is used as a robustness check and does not replace the main reported conservative strategy."
        ),
        "metrics_csv": str(metrics_path),
        "base_weight_output": str(BASE_OUTPUT_DIR),
        "base_config_dir": str(BASE_CONFIG_DIR),
    }
    summary_path = write_json(summary, OUTPUT_DIR / "weight_sensitivity_unique_constraint_summary.json")
    print(json.dumps({"summary": summary, "summary_path": str(summary_path), "metrics_path": str(metrics_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
