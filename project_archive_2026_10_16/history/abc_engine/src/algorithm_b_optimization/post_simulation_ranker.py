from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.algorithm_a_diagnosis.run_diagnosis import BUILDING_COLUMNS, STREET_COLUMNS
from src.geometry.voxelizer import create_ground_grid, estimate_site_diagonal
from src.io.export_results import ensure_dir, write_csv, write_json
from src.io.load_tables import normalise_bool_columns, read_config, read_table
from src.solar.sun_path import sample_sun_path
from src.solar.sunlight_simulator import simulate_sunlight_hours
from src.visualization.plot_heatmap import plot_sunlight_heatmap


def verify_and_rerank_candidates(
    dataset_dir: Path,
    diagnosis_dir: Path,
    candidates_dir: Path,
    output_dir: Path,
    config_dir: Path,
    replace_candidate_scores: bool = False,
) -> dict:
    """Re-simulate every candidate and rank by verified light performance.

    Algorithm B first creates heuristic candidates. This function closes the
    loop by applying each candidate's intervention boxes to the simplified
    sunlight model and measuring actual changes on the same grid.
    """
    dataset_dir = Path(dataset_dir)
    diagnosis_dir = Path(diagnosis_dir)
    candidates_dir = Path(candidates_dir)
    output_dir = ensure_dir(Path(output_dir))
    config_dir = Path(config_dir)

    site_config = read_config(config_dir / "site_config.yaml")
    solar_config = read_config(config_dir / "solar_config.yaml")
    buildings = normalise_bool_columns(
        read_table(dataset_dir / "buildings.csv", BUILDING_COLUMNS),
        ["movable", "protected"],
    )
    streets = normalise_bool_columns(
        read_table(dataset_dir / "streets.csv", STREET_COLUMNS),
        ["pedestrian_priority"],
    )
    baseline = pd.read_csv(diagnosis_dir / "sunlight_hours.csv")
    candidate_scores = pd.read_csv(candidates_dir / "candidate_scores.csv")
    interventions = pd.read_csv(candidates_dir / "interventions.csv")

    baseline_avg = float(baseline["sunlight_hours"].mean())
    baseline_dark = float(
        baseline["is_dark_zone"].astype(str).str.lower().isin({"true", "1", "yes"}).mean()
    )
    ground_grid = create_ground_grid(buildings, streets, site_config)
    sun_samples = sample_sun_path(site_config, solar_config)
    max_ray_distance = estimate_site_diagonal(buildings, streets, site_config)

    rows: list[dict] = []
    for candidate_id in candidate_scores["candidate_id"].astype(str):
        selected = interventions[interventions["candidate_id"].astype(str) == candidate_id].copy()
        sunlight = simulate_sunlight_hours(
            ground_grid,
            buildings,
            sun_samples,
            site_config,
            solar_config,
            max_ray_distance,
            interventions=selected,
        )
        write_csv(sunlight, output_dir / f"{candidate_id}_sunlight_hours.csv")
        plot_sunlight_heatmap(
            sunlight,
            output_dir / f"{candidate_id}_heatmap.png",
            f"{candidate_id} verified post-intervention sunlight",
        )

        avg = float(sunlight["sunlight_hours"].mean())
        dark = float(sunlight["is_dark_zone"].mean())
        volume = float(selected["volume_change"].abs().sum()) if not selected.empty else 0.0
        protected_penalty = float(selected["protected_conflict"].astype(bool).sum() * 40.0)
        dark_drop = baseline_dark - dark
        sunlight_gain = avg - baseline_avg
        score = (
            dark_drop * float(site_config.get("verified_dark_drop_weight", 1000.0))
            + sunlight_gain * float(site_config.get("verified_sunlight_gain_weight", 20.0))
            - (volume / 1000.0) * float(site_config.get("verified_volume_penalty_per_1000m3", 1.2))
            - protected_penalty
        )
        rows.append(
            {
                "candidate_id": candidate_id,
                "verified_total_score": round(score, 3),
                "verified_average_sunlight_hours": round(avg, 3),
                "verified_dark_zone_ratio": round(dark, 4),
                "verified_dark_grid_count": int(sunlight["is_dark_zone"].sum()),
                "verified_sunlight_gain_hours": round(sunlight_gain, 3),
                "verified_dark_ratio_drop": round(dark_drop, 4),
                "intervention_volume": round(volume, 3),
                "protected_zone_penalty": protected_penalty,
                "notes": "post-simulation verified ranking on the same grid as Algorithm A",
            }
        )

    verified = pd.DataFrame(rows).sort_values(
        ["verified_total_score", "verified_dark_ratio_drop", "verified_sunlight_gain_hours"],
        ascending=[False, False, False],
    )
    verified_path = write_csv(verified, output_dir / "candidate_post_simulation_scores.csv")

    replaced_path = None
    if replace_candidate_scores:
        original_path = candidates_dir / "candidate_scores.csv"
        backup_path = candidates_dir / "candidate_scores_heuristic_backup.csv"
        if not backup_path.exists():
            candidate_scores.to_csv(backup_path, index=False, encoding="utf-8")
        merged = candidate_scores.merge(verified, on="candidate_id", how="left", suffixes=("", "_verified"))
        merged["total_score"] = merged["verified_total_score"]
        merged["estimated_light_gain"] = merged["verified_sunlight_gain_hours"]
        merged["intervention_volume"] = merged["intervention_volume_verified"]
        merged["protected_zone_penalty"] = merged["protected_zone_penalty_verified"]
        merged["notes"] = merged["notes_verified"]
        rewritten = merged[
            [
                "candidate_id",
                "total_score",
                "estimated_light_gain",
                "intervention_volume",
                "new_shadow_penalty",
                "protected_zone_penalty",
                "number_of_interventions",
                "notes",
            ]
        ].sort_values("total_score", ascending=False)
        replaced_path = write_csv(rewritten, original_path)

    summary = {
        "candidate_count": int(len(verified)),
        "selected_by_verified_score": str(verified.iloc[0]["candidate_id"]) if not verified.empty else "",
        "baseline_average_sunlight_hours": round(baseline_avg, 3),
        "baseline_dark_zone_ratio": round(baseline_dark, 4),
        "replace_candidate_scores": bool(replace_candidate_scores),
        "notes": "Use this when paper/report conclusions need post-simulation verified candidate ranking.",
    }
    summary_path = write_json(summary, output_dir / "candidate_post_simulation_summary.json")
    return {
        "verified_scores": verified_path,
        "summary": summary_path,
        "replaced_candidate_scores": replaced_path,
        "summary_data": summary,
    }
