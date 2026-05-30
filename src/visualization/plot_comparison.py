from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.algorithm_a_diagnosis.run_diagnosis import BUILDING_COLUMNS, STREET_COLUMNS
from src.geometry.voxelizer import create_ground_grid, estimate_site_diagonal
from src.io.export_results import ensure_dir, write_csv, write_json
from src.io.load_tables import normalise_bool_columns, read_config, read_table
from src.solar.sun_path import sample_sun_path
from src.solar.sunlight_simulator import simulate_sunlight_hours
from src.visualization.plot_heatmap import plot_sunlight_heatmap


def _read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _improvement_from_dark_ratio(baseline: float, current: float) -> float:
    if baseline <= 0:
        return 0.0
    return round((baseline - current) / baseline, 3)


def _plot_metrics(metrics: pd.DataFrame, output_path: Path) -> Path:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    labels = metrics["scheme_type"].tolist()
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), dpi=160)
    chart_specs = [
        ("average_sunlight_hours", "Avg sunlight hours", "#3b6ea8"),
        ("dark_zone_ratio", "Dark zone ratio", "#8c4a3f"),
        ("intervention_volume", "Intervention volume", "#6b8f3f"),
        ("accessibility_coverage", "Accessibility coverage", "#9467bd"),
    ]
    for ax, (column, title, color) in zip(axes.ravel(), chart_specs):
        ax.bar(labels, metrics[column], color=color)
        ax.set_title(title)
        ax.grid(axis="y", linewidth=0.3, alpha=0.35)
        ax.tick_params(axis="x", rotation=15)
    fig.suptitle("Baseline / Manual / Algorithm comparison", y=0.98)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def _simulate_selected_candidate(
    dataset_dir: Path,
    candidates_dir: Path,
    output_dir: Path,
    config_dir: Path,
    selected_id: str,
) -> tuple[pd.DataFrame, dict]:
    """Re-run the simplified sunlight model with selected interventions applied."""
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
    interventions = pd.read_csv(candidates_dir / "interventions.csv")
    selected_interventions = interventions[interventions["candidate_id"].astype(str) == str(selected_id)].copy()

    ground_grid = create_ground_grid(buildings, streets, site_config)
    sun_samples = sample_sun_path(site_config, solar_config)
    max_ray_distance = estimate_site_diagonal(buildings, streets, site_config)
    sunlight = simulate_sunlight_hours(
        ground_grid,
        buildings,
        sun_samples,
        site_config,
        solar_config,
        max_ray_distance,
        interventions=selected_interventions,
    )
    write_csv(sunlight, output_dir / "algorithm_sunlight_hours.csv")
    plot_sunlight_heatmap(
        sunlight,
        output_dir / "algorithm_heatmap.png",
        f"{selected_id} post-intervention sunlight-hours estimate",
    )
    summary = {
        "average_sunlight_hours": round(float(sunlight["sunlight_hours"].mean()), 3),
        "dark_zone_ratio": round(float(sunlight["is_dark_zone"].mean()), 4),
        "dark_grid_count": int(sunlight["is_dark_zone"].sum()),
        "total_grid_count": int(len(sunlight)),
        "method": "same 2.5D sunlight model re-run with selected intervention boxes",
    }
    write_json(summary, output_dir / "algorithm_post_simulation_summary.json")
    return sunlight, summary


def build_final_report(
    dataset_dir: Path,
    diagnosis_dir: Path,
    candidates_dir: Path,
    validation_dir: Path,
    output_dir: Path,
    config_dir: Path,
) -> dict:
    """Build final comparison CSV, chart, and summary JSON."""
    dataset_dir = Path(dataset_dir)
    diagnosis_dir = Path(diagnosis_dir)
    candidates_dir = Path(candidates_dir)
    validation_dir = Path(validation_dir)
    output_dir = ensure_dir(Path(output_dir))
    config_dir = Path(config_dir)

    site_config = read_config(config_dir / "site_config.yaml")
    a_summary = _read_json(diagnosis_dir / "A_summary.json")
    final_recommendation = _read_json(validation_dir / "final_recommendation.json")
    candidate_scores = pd.read_csv(candidates_dir / "candidate_scores.csv")
    safety_report = pd.read_csv(validation_dir / "safety_report.csv")

    baseline_avg = float(a_summary["average_sunlight_hours"])
    baseline_dark = float(a_summary["dark_zone_ratio"])
    selected_id = final_recommendation["selected_candidate_id"]
    selected_score = candidate_scores[candidate_scores["candidate_id"] == selected_id].iloc[0]
    selected_safety = safety_report[safety_report["candidate_id"] == selected_id].iloc[0]
    _, algorithm_post = _simulate_selected_candidate(
        dataset_dir,
        candidates_dir,
        output_dir,
        config_dir,
        selected_id,
    )

    algorithm_avg = float(algorithm_post["average_sunlight_hours"])
    algorithm_dark = float(algorithm_post["dark_zone_ratio"])
    manual_avg = round(baseline_avg + float(site_config.get("manual_design_avg_sunlight_gain", 0.45)), 3)
    manual_dark = round(max(0.0, baseline_dark - float(site_config.get("manual_design_dark_ratio_drop", 0.06))), 4)
    manual_volume = round(float(selected_score["intervention_volume"]) * 1.25, 3)

    metrics = pd.DataFrame(
        [
            {
                "scheme_id": "baseline_01",
                "scheme_type": "baseline",
                "average_sunlight_hours": baseline_avg,
                "dark_zone_ratio": baseline_dark,
                "light_equity_improvement": 0.0,
                "intervention_volume": 0.0,
                "accessibility_coverage": float(site_config.get("baseline_accessibility_coverage", 0.68)),
                "safety_score": float(site_config.get("baseline_safety_score", 62)),
                "notes": "pre-intervention result from Algorithm A",
            },
            {
                "scheme_id": "manual_01",
                "scheme_type": "manual_design",
                "average_sunlight_hours": manual_avg,
                "dark_zone_ratio": manual_dark,
                "light_equity_improvement": _improvement_from_dark_ratio(baseline_dark, manual_dark),
                "intervention_volume": manual_volume,
                "accessibility_coverage": float(site_config.get("manual_design_accessibility_coverage", 0.76)),
                "safety_score": float(site_config.get("manual_design_safety_score", 74)),
                "notes": "placeholder; replace after architecture team submits manual scheme",
            },
            {
                "scheme_id": selected_id,
                "scheme_type": "algorithm_design",
                "average_sunlight_hours": algorithm_avg,
                "dark_zone_ratio": algorithm_dark,
                "light_equity_improvement": _improvement_from_dark_ratio(baseline_dark, algorithm_dark),
                "intervention_volume": float(selected_score["intervention_volume"]),
                "accessibility_coverage": float(selected_safety["accessible_route_ratio"]),
                "safety_score": float(selected_safety["safety_score"]),
                "notes": "selected by Algorithm C; sunlight metrics re-simulated with intervention boxes",
            },
        ]
    )

    metrics_path = write_csv(metrics, output_dir / "before_after_metrics.csv")
    chart_path = _plot_metrics(metrics, output_dir / "comparison_chart.png")
    summary = {
        "selected_candidate_id": selected_id,
        "baseline_dark_zone_ratio": baseline_dark,
        "algorithm_dark_zone_ratio": algorithm_dark,
        "algorithm_post_simulation": algorithm_post,
        "algorithm_light_equity_improvement": float(
            metrics[metrics["scheme_type"] == "algorithm_design"]["light_equity_improvement"].iloc[0]
        ),
        "outputs": {
            "before_after_metrics": "before_after_metrics.csv",
            "comparison_chart": "comparison_chart.png",
            "algorithm_sunlight_hours": "algorithm_sunlight_hours.csv",
            "algorithm_heatmap": "algorithm_heatmap.png",
            "algorithm_post_simulation_summary": "algorithm_post_simulation_summary.json",
        },
        "notes": "Manual design values are placeholders until the architecture team submits a real comparison scheme. Algorithm values are re-simulated with the current simplified 2.5D model.",
    }
    summary_path = write_json(summary, output_dir / "final_summary.json")
    return {
        "before_after_metrics": metrics_path,
        "comparison_chart": chart_path,
        "summary": summary_path,
        "summary_data": summary,
    }
