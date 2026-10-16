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

from src.algorithm_b_optimization.run_optimization import run_optimization  # noqa: E402
from src.algorithm_c_validation.run_validation import run_validation  # noqa: E402
from src.io.export_results import ensure_dir, write_json  # noqa: E402
from src.visualization.plot_comparison import _simulate_selected_candidate  # noqa: E402


STRATEGIES = {
    "conservative": {
        "scheme_type": "AI_conservative",
        "label": "保守型 AI",
        "overrides": {
            "search_iterations": 220,
            "max_interventions_per_candidate": 2,
            "score_weight_light_gain": 1.0,
            "score_weight_intervention_volume": 0.16,
            "score_weight_new_shadow_penalty": 0.9,
            "score_weight_protected_zone_penalty": 2.0,
        },
    },
    "balanced": {
        "scheme_type": "AI_balanced",
        "label": "均衡型 AI",
        "overrides": {
            "search_iterations": 260,
            "max_interventions_per_candidate": 3,
            "score_weight_light_gain": 1.0,
            "score_weight_intervention_volume": 0.08,
            "score_weight_new_shadow_penalty": 0.6,
            "score_weight_protected_zone_penalty": 1.0,
        },
    },
    "light_first": {
        "scheme_type": "AI_light_first",
        "label": "采光优先型 AI",
        "overrides": {
            "search_iterations": 320,
            "max_interventions_per_candidate": 4,
            "score_weight_light_gain": 1.35,
            "score_weight_intervention_volume": 0.045,
            "score_weight_new_shadow_penalty": 0.5,
            "score_weight_protected_zone_penalty": 1.2,
        },
    },
}


def _read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _write_yaml(path: Path, data: dict) -> None:
    with Path(path).open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)


def _prepare_config(base_config_dir: Path, output_root: Path, strategy_key: str) -> Path:
    config_dir = output_root / "_configs" / strategy_key
    config_dir.mkdir(parents=True, exist_ok=True)
    for name in ["solar_config.yaml", "accessibility_rules.yaml"]:
        shutil.copy2(base_config_dir / name, config_dir / name)

    site_config = _load_yaml(base_config_dir / "site_config.yaml")
    site_config.update(STRATEGIES[strategy_key]["overrides"])
    site_config["candidate_count"] = 3
    site_config["product_strategy"] = strategy_key
    site_config["product_strategy_label"] = STRATEGIES[strategy_key]["label"]
    _write_yaml(config_dir / "site_config.yaml", site_config)
    return config_dir


def _changed_buildings(interventions: pd.DataFrame, candidate_id: str) -> list[str]:
    selected = interventions[interventions["candidate_id"].astype(str) == str(candidate_id)]
    ids: set[str] = set()
    for value in selected["target_building_id"].astype(str):
        for item in value.split("|"):
            item = item.strip()
            if item and not item.startswith("zone:"):
                ids.add(item)
    return sorted(ids)


def _plot_strategy_comparison(metrics: pd.DataFrame, output_path: Path) -> Path:
    labels = metrics["scheme_type"].tolist()
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), dpi=160)
    specs = [
        ("average_sunlight_hours", "Post-sim avg sunlight hours", "#2f80ed"),
        ("dark_zone_ratio", "Post-sim dark zone ratio", "#9b2c2c"),
        ("intervention_volume", "Intervention volume (m3)", "#b7791f"),
        ("changed_building_count", "Changed buildings", "#6b7280"),
    ]
    for ax, (column, title, color) in zip(axes.ravel(), specs):
        ax.bar(labels, metrics[column], color=color)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.25, linewidth=0.4)
        ax.tick_params(axis="x", rotation=12)
    fig.suptitle("Baseline and AI Strategy Comparison", y=0.98)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def run_strategy_comparison(
    dataset_dir: Path,
    diagnosis_dir: Path,
    base_config_dir: Path,
    output_root: Path,
    post_simulate: bool = True,
) -> dict:
    """Run B/C for three AI strategies and build a no-manual strategy report."""
    dataset_dir = Path(dataset_dir)
    diagnosis_dir = Path(diagnosis_dir)
    output_root = ensure_dir(Path(output_root))
    base_config_dir = Path(base_config_dir)
    a_summary = _read_json(diagnosis_dir / "A_summary.json")

    rows = [
        {
            "scheme_id": "baseline",
            "scheme_type": "baseline",
            "average_sunlight_hours": float(a_summary["average_sunlight_hours"]),
            "dark_zone_ratio": float(a_summary["dark_zone_ratio"]),
            "estimated_light_gain": 0.0,
            "intervention_volume": 0.0,
            "changed_building_count": 0,
            "changed_building_ids": "",
            "protected_conflict_count": 0,
            "accessible_route_ratio": "",
            "safety_score": "",
            "passed": "",
            "notes": "Existing condition from Algorithm A; no manual-design placeholder.",
        }
    ]

    for strategy_key, strategy in STRATEGIES.items():
        strategy_dir = ensure_dir(output_root / strategy_key)
        config_dir = _prepare_config(base_config_dir, output_root, strategy_key)
        candidates_dir = ensure_dir(strategy_dir / "B_candidates")
        validation_dir = ensure_dir(strategy_dir / "C_validation")

        run_optimization(dataset_dir, diagnosis_dir, candidates_dir, config_dir)
        run_validation(dataset_dir, candidates_dir, validation_dir, config_dir)

        scores = pd.read_csv(candidates_dir / "candidate_scores.csv").sort_values("total_score", ascending=False)
        interventions = pd.read_csv(candidates_dir / "interventions.csv")
        safety = pd.read_csv(validation_dir / "safety_report.csv")
        recommendation = _read_json(validation_dir / "final_recommendation.json")
        selected_id = recommendation["selected_candidate_id"]
        selected_score = scores[scores["candidate_id"].astype(str) == str(selected_id)].iloc[0]
        selected_safety = safety[safety["candidate_id"].astype(str) == str(selected_id)].iloc[0]
        changed = _changed_buildings(interventions, selected_id)
        selected_interventions = interventions[interventions["candidate_id"].astype(str) == str(selected_id)]
        if post_simulate:
            post_dir = ensure_dir(strategy_dir / "post_simulation")
            _, post_summary = _simulate_selected_candidate(
                dataset_dir,
                candidates_dir,
                post_dir,
                config_dir,
                selected_id,
            )
            average_sunlight_hours = float(post_summary["average_sunlight_hours"])
            dark_zone_ratio = float(post_summary["dark_zone_ratio"])
            light_equity_improvement = (
                (float(a_summary["dark_zone_ratio"]) - dark_zone_ratio) / float(a_summary["dark_zone_ratio"])
                if float(a_summary["dark_zone_ratio"]) > 0
                else 0.0
            )
            post_notes = "post-simulated with simplified 2.5D model"
        else:
            average_sunlight_hours = ""
            dark_zone_ratio = ""
            light_equity_improvement = ""
            post_notes = "post-simulation skipped"

        rows.append(
            {
                "scheme_id": selected_id,
                "scheme_type": strategy["scheme_type"],
                "average_sunlight_hours": average_sunlight_hours,
                "dark_zone_ratio": dark_zone_ratio,
                "light_equity_improvement": light_equity_improvement,
                "estimated_light_gain": float(selected_score["estimated_light_gain"]),
                "intervention_volume": float(selected_score["intervention_volume"]),
                "changed_building_count": len(changed),
                "changed_building_ids": ";".join(changed),
                "protected_conflict_count": int(selected_interventions["protected_conflict"].astype(bool).sum()),
                "accessible_route_ratio": float(selected_safety["accessible_route_ratio"]),
                "safety_score": float(selected_safety["safety_score"]),
                "passed": bool(selected_safety["passed"]),
                "notes": f"{strategy['label']} selected candidate; {post_notes}.",
            }
        )

    metrics = pd.DataFrame(rows)
    metrics_path = output_root / "strategy_comparison_metrics.csv"
    metrics.to_csv(metrics_path, index=False, encoding="utf-8-sig")
    chart_path = _plot_strategy_comparison(
        metrics[metrics["scheme_type"] != "baseline"].copy(),
        output_root / "strategy_comparison_chart.png",
    )
    summary = {
        "research_main_question": "AI-assisted sunlight diagnosis and minimum-intervention strategy comparison.",
        "comparison_set": ["baseline", "AI_conservative", "AI_balanced", "AI_light_first"],
        "manual_design_removed": True,
        "baseline": {
            "average_sunlight_hours": float(a_summary["average_sunlight_hours"]),
            "dark_zone_ratio": float(a_summary["dark_zone_ratio"]),
            "dark_grid_count": int(a_summary["dark_grid_count"]),
            "total_grid_count": int(a_summary["total_grid_count"]),
        },
        "outputs": {
            "strategy_comparison_metrics": str(metrics_path),
            "strategy_comparison_chart": str(chart_path),
        },
        "notes": (
            "This report compares AI strategy behavior rather than claiming AI beats a manual design. "
            "Strategy candidates are post-simulated by default with the simplified 2.5D sunlight model."
        ),
    }
    summary_path = output_root / "strategy_comparison_summary.json"
    write_json(summary, summary_path)
    return {"metrics": metrics_path, "chart": chart_path, "summary": summary_path}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run no-manual AI strategy comparison for light restoration.")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "real_guankou" / "lakeside_leisure_ready",
    )
    parser.add_argument(
        "--diagnosis-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "validation_lakeside_6m" / "A_diagnosis",
    )
    parser.add_argument(
        "--base-config-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "lakeside_leisure_final_6m_config",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "light_product_2026_06_02" / "strategy_comparison",
    )
    parser.add_argument(
        "--skip-post-simulation",
        action="store_true",
        help="Only report B/C estimated strategy scores; faster but less paper-ready.",
    )
    args = parser.parse_args()
    outputs = run_strategy_comparison(
        dataset_dir=args.dataset_dir,
        diagnosis_dir=args.diagnosis_dir,
        base_config_dir=args.base_config_dir,
        output_root=args.output_root,
        post_simulate=not args.skip_post_simulation,
    )
    for key, path in outputs.items():
        print(f"{key}: {path}")


if __name__ == "__main__":
    main()
