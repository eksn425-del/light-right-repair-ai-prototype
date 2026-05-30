from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.algorithm_a_diagnosis.run_diagnosis import BUILDING_COLUMNS, SITE_ZONE_COLUMNS
from src.algorithm_b_optimization.intervention_generator import generate_intervention_pool
from src.algorithm_b_optimization.scoring import DEFAULT_SCORE_WEIGHTS, score_interventions
from src.algorithm_b_optimization.simulated_annealing import search_candidate_sets
from src.geometry.intervention_mesh import write_candidate_obj
from src.io.export_results import ensure_dir, write_csv, write_json
from src.io.load_tables import normalise_bool_columns, read_config, read_table
from src.visualization.plot_candidates import plot_candidate_scores


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


def _score_weights(site_config: dict) -> dict:
    return {
        "light_gain": float(site_config.get("score_weight_light_gain", DEFAULT_SCORE_WEIGHTS["light_gain"])),
        "intervention_volume": float(
            site_config.get("score_weight_intervention_volume", DEFAULT_SCORE_WEIGHTS["intervention_volume"])
        ),
        "new_shadow_penalty": float(
            site_config.get("score_weight_new_shadow_penalty", DEFAULT_SCORE_WEIGHTS["new_shadow_penalty"])
        ),
        "protected_zone_penalty": float(
            site_config.get("score_weight_protected_zone_penalty", DEFAULT_SCORE_WEIGHTS["protected_zone_penalty"])
        ),
    }


def _read_optional_site_zones(dataset_dir: Path) -> pd.DataFrame:
    path = dataset_dir / "site_zones.csv"
    if not path.exists():
        return pd.DataFrame(columns=SITE_ZONE_COLUMNS)
    return normalise_bool_columns(
        read_table(path, SITE_ZONE_COLUMNS),
        ["needs_light_improvement", "needs_accessibility_improvement", "protected"],
    )


def run_optimization(
    dataset_dir: Path,
    diagnosis_dir: Path,
    output_dir: Path,
    config_dir: Path,
) -> dict:
    """Run Algorithm B and export 2-3 intervention candidates."""
    dataset_dir = Path(dataset_dir)
    diagnosis_dir = Path(diagnosis_dir)
    output_dir = ensure_dir(Path(output_dir))
    config_dir = Path(config_dir)

    site_config = read_config(config_dir / "site_config.yaml")
    weights = _score_weights(site_config)
    iterations = int(site_config.get("search_iterations", 220))
    candidate_count = int(site_config.get("candidate_count", 3))

    dark_zones = read_table(diagnosis_dir / "dark_zones.csv")
    gap_candidates = read_table(diagnosis_dir / "gap_candidates.csv")
    buildings = normalise_bool_columns(
        read_table(dataset_dir / "buildings.csv", BUILDING_COLUMNS),
        ["movable", "protected"],
    )
    protected_zones = read_table(dataset_dir / "protected_zones.csv", PROTECTED_ZONE_COLUMNS)
    site_zones = _read_optional_site_zones(dataset_dir)

    pool = generate_intervention_pool(
        dark_zones,
        gap_candidates,
        buildings,
        protected_zones,
        site_zones=site_zones,
    )
    ranked_sets = search_candidate_sets(
        pool,
        weights,
        iterations=iterations,
        candidate_count=max(candidate_count * 8, candidate_count),
        max_interventions_per_candidate=int(site_config.get("max_interventions_per_candidate", 3)),
        seed=int(site_config.get("random_seed", 42)),
    )
    if not ranked_sets:
        raise ValueError("Algorithm B search produced no candidate sets.")

    selected_sets: list[dict] = []
    selected_keys: set[tuple[int, ...]] = set()

    def add_candidate(candidate: dict) -> None:
        key = tuple(candidate["indices"])
        if key not in selected_keys and len(selected_sets) < candidate_count:
            selected_sets.append(candidate)
            selected_keys.add(key)

    add_candidate(ranked_sets[0])
    if not site_zones.empty:
        found_zone_candidate = False
        for candidate in ranked_sets:
            targets = pool.loc[candidate["indices"], "target_building_id"].astype(str)
            if targets.str.startswith("zone:").any():
                add_candidate(candidate)
                found_zone_candidate = True
                break
        if not found_zone_candidate:
            zone_pool = pool[pool["target_building_id"].astype(str).str.startswith("zone:")]
            if not zone_pool.empty:
                scored = []
                for pool_index in zone_pool.index:
                    scored.append(
                        {
                            "indices": [int(pool_index)],
                            "metrics": score_interventions(pool.loc[[pool_index]], weights),
                        }
                    )
                add_candidate(
                    sorted(scored, key=lambda item: item["metrics"]["total_score"], reverse=True)[0]
                )
    for desired_type in ["subtract", "add", "reorganize"]:
        found_type_candidate = False
        for candidate in ranked_sets:
            types = set(pool.loc[candidate["indices"], "type"].astype(str))
            if desired_type in types:
                add_candidate(candidate)
                found_type_candidate = True
                break
        if not found_type_candidate:
            type_pool = pool[pool["type"].astype(str) == desired_type]
            if not type_pool.empty:
                scored = []
                for pool_index in type_pool.index:
                    scored.append(
                        {
                            "indices": [int(pool_index)],
                            "metrics": score_interventions(pool.loc[[pool_index]], weights),
                        }
                    )
                add_candidate(
                    sorted(scored, key=lambda item: item["metrics"]["total_score"], reverse=True)[0]
                )
    for candidate in ranked_sets:
        add_candidate(candidate)
        if len(selected_sets) >= candidate_count:
            break

    score_rows: list[dict] = []
    intervention_rows: list[pd.DataFrame] = []
    for index, candidate in enumerate(selected_sets, start=1):
        candidate_id = f"candidate_{index:02d}"
        candidate_interventions = pool.loc[candidate["indices"]].copy()
        candidate_interventions.insert(0, "candidate_id", candidate_id)
        metrics = score_interventions(candidate_interventions, weights)
        score_rows.append(
            {
                "candidate_id": candidate_id,
                **metrics,
                "notes": "simplified candidate generated from Algorithm A diagnosis",
            }
        )
        intervention_rows.append(candidate_interventions)
        write_candidate_obj(candidate_interventions, output_dir / f"{candidate_id}.obj")

    scores = pd.DataFrame(
        score_rows,
        columns=[
            "candidate_id",
            "total_score",
            "estimated_light_gain",
            "intervention_volume",
            "new_shadow_penalty",
            "protected_zone_penalty",
            "number_of_interventions",
            "notes",
        ],
    ).sort_values("total_score", ascending=False)
    interventions = pd.concat(intervention_rows, ignore_index=True)
    interventions = interventions[
        [
            "candidate_id",
            "intervention_id",
            "type",
            "target_building_id",
            "x",
            "y",
            "z",
            "size_x",
            "size_y",
            "size_z",
            "volume_change",
            "expected_light_gain",
            "protected_conflict",
            "notes",
        ]
    ]

    scores_path = write_csv(scores, output_dir / "candidate_scores.csv")
    interventions_path = write_csv(interventions, output_dir / "interventions.csv")
    plot_candidate_scores(scores, output_dir / "candidate_scores.png")

    summary = {
        "candidate_count": int(len(scores)),
        "best_candidate_id": str(scores.iloc[0]["candidate_id"]),
        "score_weights": weights,
        "search_iterations": iterations,
        "notes": "Framework version: boolean geometry is represented by reference boxes.",
    }
    summary_path = write_json(summary, output_dir / "B_summary.json")
    return {
        "candidate_scores": scores_path,
        "interventions": interventions_path,
        "summary": summary_path,
        "summary_data": summary,
        "candidate_objs": [output_dir / f"candidate_{index:02d}.obj" for index in range(1, len(scores) + 1)],
    }
