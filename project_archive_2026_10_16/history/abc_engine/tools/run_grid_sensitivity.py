from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithm_a_diagnosis.run_diagnosis import run_diagnosis  # noqa: E402
from src.algorithm_b_optimization.run_optimization import run_optimization  # noqa: E402
from src.algorithm_c_validation.run_validation import run_validation  # noqa: E402
from src.io.export_results import ensure_dir, write_json  # noqa: E402
from src.visualization.plot_comparison import _simulate_selected_candidate  # noqa: E402


CONSERVATIVE_OVERRIDES = {
    "candidate_count": 3,
    "search_iterations": 220,
    "max_interventions_per_candidate": 2,
    "score_weight_light_gain": 1.0,
    "score_weight_intervention_volume": 0.16,
    "score_weight_new_shadow_penalty": 0.9,
    "score_weight_protected_zone_penalty": 2.0,
}


def _read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _write_yaml(path: Path, data: dict) -> None:
    with Path(path).open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)


def _prepare_config(base_config_dir: Path, output_root: Path, grid_size: float) -> Path:
    config_dir = output_root / f"config_grid_{grid_size:g}m"
    config_dir.mkdir(parents=True, exist_ok=True)
    for name in ["solar_config.yaml", "accessibility_rules.yaml"]:
        shutil.copy2(base_config_dir / name, config_dir / name)
    site_config = _load_yaml(base_config_dir / "site_config.yaml")
    site_config.update(CONSERVATIVE_OVERRIDES)
    site_config["grid_size_m"] = float(grid_size)
    site_config["sensitivity_case"] = f"grid_{grid_size:g}m_conservative"
    _write_yaml(config_dir / "site_config.yaml", site_config)
    return config_dir


def run_single_grid_case(
    dataset_dir: Path,
    base_config_dir: Path,
    output_root: Path,
    grid_size: float,
) -> dict:
    """Run baseline and conservative post-simulation for one grid size."""
    case_dir = ensure_dir(Path(output_root) / f"grid_{grid_size:g}m")
    config_dir = _prepare_config(Path(base_config_dir), case_dir, grid_size)
    diagnosis_dir = ensure_dir(case_dir / "A_diagnosis")
    candidates_dir = ensure_dir(case_dir / "B_conservative")
    validation_dir = ensure_dir(case_dir / "C_validation")
    post_dir = ensure_dir(case_dir / "post_simulation")

    run_diagnosis(dataset_dir, diagnosis_dir, config_dir)
    run_optimization(dataset_dir, diagnosis_dir, candidates_dir, config_dir)
    run_validation(dataset_dir, candidates_dir, validation_dir, config_dir)

    a_summary = _read_json(diagnosis_dir / "A_summary.json")
    recommendation = _read_json(validation_dir / "final_recommendation.json")
    selected_id = recommendation["selected_candidate_id"]
    _, post_summary = _simulate_selected_candidate(
        dataset_dir,
        candidates_dir,
        post_dir,
        config_dir,
        selected_id,
    )
    scores = pd.read_csv(candidates_dir / "candidate_scores.csv")
    selected_score = scores[scores["candidate_id"].astype(str) == str(selected_id)].iloc[0]
    interventions = pd.read_csv(candidates_dir / "interventions.csv")
    selected_interventions = interventions[interventions["candidate_id"].astype(str) == str(selected_id)]
    changed_ids = sorted(
        {
            item.strip()
            for value in selected_interventions["target_building_id"].astype(str)
            for item in value.split("|")
            if item.strip() and not item.startswith("zone:")
        }
    )

    baseline_dark = float(a_summary["dark_zone_ratio"])
    post_dark = float(post_summary["dark_zone_ratio"])
    improvement = (baseline_dark - post_dark) / baseline_dark if baseline_dark > 0 else 0.0
    result = {
        "grid_size_m": float(grid_size),
        "baseline_average_sunlight_hours": float(a_summary["average_sunlight_hours"]),
        "baseline_dark_zone_ratio": baseline_dark,
        "baseline_dark_grid_count": int(a_summary["dark_grid_count"]),
        "total_grid_count": int(a_summary["total_grid_count"]),
        "selected_candidate_id": selected_id,
        "post_average_sunlight_hours": float(post_summary["average_sunlight_hours"]),
        "post_dark_zone_ratio": post_dark,
        "post_dark_grid_count": int(post_summary["dark_grid_count"]),
        "dark_zone_improvement_ratio": round(improvement, 5),
        "estimated_light_gain": float(selected_score["estimated_light_gain"]),
        "intervention_volume": float(selected_score["intervention_volume"]),
        "changed_building_ids": ";".join(changed_ids),
        "output_dir": str(case_dir),
    }
    write_json(result, case_dir / "grid_sensitivity_case_summary.json")
    return result


def _plot_summary(summary: pd.DataFrame, output_path: Path) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), dpi=160)
    labels = summary["grid_size_m"].map(lambda value: f"{value:g}m")
    specs = [
        ("baseline_dark_zone_ratio", "Baseline dark zone ratio", "#9b2c2c"),
        ("post_dark_zone_ratio", "Post-sim dark zone ratio", "#c05621"),
        ("dark_zone_improvement_ratio", "Dark-zone improvement ratio", "#2f855a"),
        ("total_grid_count", "Grid sample count", "#4a5568"),
    ]
    for ax, (column, title, color) in zip(axes.ravel(), specs):
        ax.bar(labels, summary[column], color=color)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.25, linewidth=0.4)
    fig.suptitle("Grid Sensitivity: Conservative AI Strategy", y=0.98)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def run_grid_sensitivity(
    dataset_dir: Path,
    base_config_dir: Path,
    output_root: Path,
    grid_sizes: list[float],
) -> dict:
    """Run grid sensitivity cases and export a combined report."""
    output_root = ensure_dir(Path(output_root))
    rows = [
        run_single_grid_case(
            dataset_dir=Path(dataset_dir),
            base_config_dir=Path(base_config_dir),
            output_root=output_root,
            grid_size=float(grid_size),
        )
        for grid_size in grid_sizes
    ]
    summary = pd.DataFrame(rows).sort_values("grid_size_m", ascending=False)
    metrics_path = output_root / "grid_sensitivity_metrics.csv"
    summary.to_csv(metrics_path, index=False, encoding="utf-8-sig")
    chart_path = _plot_summary(summary, output_root / "grid_sensitivity_chart.png")
    report = {
        "metrics": str(metrics_path),
        "chart": str(chart_path),
        "grid_sizes_m": grid_sizes,
        "notes": "Conservative AI strategy re-tested under different ground-grid sizes using the simplified 2.5D model.",
    }
    summary_path = output_root / "grid_sensitivity_summary.json"
    write_json(report, summary_path)
    return {"metrics": metrics_path, "chart": chart_path, "summary": summary_path}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run 3m/2m grid sensitivity for conservative light strategy.")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "real_guankou" / "lakeside_leisure_ready",
    )
    parser.add_argument(
        "--base-config-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "lakeside_leisure_final_6m_config",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "light_product_2026_06_03" / "grid_sensitivity",
    )
    parser.add_argument("--grid-sizes", nargs="+", type=float, default=[3.0, 2.0])
    args = parser.parse_args()
    outputs = run_grid_sensitivity(args.dataset_dir, args.base_config_dir, args.output_root, args.grid_sizes)
    for key, value in outputs.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
