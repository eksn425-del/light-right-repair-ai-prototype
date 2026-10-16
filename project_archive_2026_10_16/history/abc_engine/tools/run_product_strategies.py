from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required for strategy configs. Run: pip install -r requirements.txt") from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import _prepare_dataset, _print_paths  # noqa: E402
from src.algorithm_a_diagnosis.run_diagnosis import run_diagnosis  # noqa: E402
from src.algorithm_b_optimization.post_simulation_ranker import verify_and_rerank_candidates  # noqa: E402
from src.algorithm_b_optimization.run_optimization import run_optimization  # noqa: E402
from src.algorithm_c_validation.run_validation import run_validation  # noqa: E402
from src.io.export_results import ensure_dir  # noqa: E402
from src.visualization.plot_comparison import build_final_report  # noqa: E402


STRATEGIES = {
    "conservative": {
        "label": "保守型",
        "description": "优先控制改造体量和风险，只输出低扰动候选。",
        "overrides": {
            "candidate_count": 3,
            "search_iterations": 220,
            "max_interventions_per_candidate": 2,
            "score_weight_light_gain": 1.0,
            "score_weight_intervention_volume": 0.16,
            "score_weight_new_shadow_penalty": 0.9,
            "score_weight_protected_zone_penalty": 2.0,
        },
    },
    "balanced": {
        "label": "均衡型",
        "description": "在采光提升、最小干预和约束风险之间取平衡。",
        "overrides": {
            "candidate_count": 3,
            "search_iterations": 260,
            "max_interventions_per_candidate": 3,
            "score_weight_light_gain": 1.0,
            "score_weight_intervention_volume": 0.08,
            "score_weight_new_shadow_penalty": 0.6,
            "score_weight_protected_zone_penalty": 1.0,
        },
    },
    "light_first": {
        "label": "采光优先型",
        "description": "优先探索采光改善潜力，允许更高干预量，供人工复核。",
        "overrides": {
            "candidate_count": 3,
            "search_iterations": 320,
            "max_interventions_per_candidate": 4,
            "score_weight_light_gain": 1.35,
            "score_weight_intervention_volume": 0.045,
            "score_weight_new_shadow_penalty": 0.5,
            "score_weight_protected_zone_penalty": 1.2,
        },
    },
}


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _write_yaml(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)


def _prepare_strategy_config(base_config_dir: Path, output_root: Path, strategy_key: str) -> Path:
    """Create an isolated config folder for one product strategy."""
    strategy = STRATEGIES[strategy_key]
    config_dir = output_root / "_configs" / strategy_key
    config_dir.mkdir(parents=True, exist_ok=True)

    for name in ["solar_config.yaml", "accessibility_rules.yaml"]:
        shutil.copy2(base_config_dir / name, config_dir / name)

    site_config = _load_yaml(base_config_dir / "site_config.yaml")
    site_config.update(strategy["overrides"])
    site_config["product_strategy"] = strategy_key
    site_config["product_strategy_label"] = strategy["label"]
    site_config["product_strategy_description"] = strategy["description"]
    _write_yaml(config_dir / "site_config.yaml", site_config)
    return config_dir


def run_product_strategies(
    dataset: str,
    output_root: Path,
    base_config_dir: Path,
    verify_candidates: bool = False,
    rerun_diagnosis: bool = False,
) -> dict:
    """Run the ABC workflow for conservative/balanced/light-first strategies."""
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    results = {}
    dataset_dir = _prepare_dataset(dataset)

    shared_config_dir = _prepare_strategy_config(base_config_dir, output_root, "balanced")
    shared_diagnosis_dir = ensure_dir(output_root / "_shared_A_diagnosis")
    if rerun_diagnosis or not (shared_diagnosis_dir / "A_summary.json").exists():
        diagnosis_outputs = run_diagnosis(dataset_dir, shared_diagnosis_dir, shared_config_dir)
        _print_paths("Shared Algorithm A diagnosis", diagnosis_outputs)
    else:
        diagnosis_outputs = {"summary": shared_diagnosis_dir / "A_summary.json"}
        print(f"Reusing shared Algorithm A diagnosis: {shared_diagnosis_dir}")

    for strategy_key, strategy in STRATEGIES.items():
        print(f"\n=== Product strategy: {strategy_key} ({strategy['label']}) ===")
        config_dir = _prepare_strategy_config(base_config_dir, output_root, strategy_key)
        strategy_output = output_root / strategy_key
        candidates_dir = ensure_dir(strategy_output / "B_candidates")
        validation_dir = ensure_dir(strategy_output / "C_validation")
        report_dir = ensure_dir(strategy_output / "final_report")

        optimization_outputs = run_optimization(dataset_dir, shared_diagnosis_dir, candidates_dir, config_dir)
        _print_paths("Algorithm B candidates", optimization_outputs)

        verification_outputs = None
        if verify_candidates:
            verification_dir = ensure_dir(candidates_dir / "post_simulation_verification")
            verification_outputs = verify_and_rerank_candidates(
                dataset_dir,
                shared_diagnosis_dir,
                candidates_dir,
                verification_dir,
                config_dir,
                replace_candidate_scores=True,
            )
            _print_paths("Algorithm B post-simulation verification", verification_outputs)

        validation_outputs = run_validation(dataset_dir, candidates_dir, validation_dir, config_dir)
        _print_paths("Algorithm C validation", validation_outputs)

        report_outputs = build_final_report(
            dataset_dir,
            shared_diagnosis_dir,
            candidates_dir,
            validation_dir,
            report_dir,
            config_dir,
        )
        _print_paths("Final report", report_outputs)
        results[strategy_key] = {
            "dataset_dir": dataset_dir,
            "diagnosis": diagnosis_outputs,
            "optimization": optimization_outputs,
            "candidate_verification": verification_outputs,
            "validation": validation_outputs,
            "final_report": report_outputs,
        }
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run light-equity ABC workflow as product decision strategies.")
    parser.add_argument(
        "--dataset",
        default="real_guankou/lakeside_leisure_ready",
        help="Dataset folder under data/.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "product_strategy_runs",
        help="Folder for all strategy outputs.",
    )
    parser.add_argument(
        "--base-config-dir",
        type=Path,
        default=PROJECT_ROOT / "config",
        help="Base config folder to copy and override.",
    )
    parser.add_argument(
        "--verify-candidates",
        action="store_true",
        help="Re-simulate candidates before Algorithm C. Slower but better for paper-facing runs.",
    )
    parser.add_argument(
        "--rerun-diagnosis",
        action="store_true",
        help="Force re-running shared Algorithm A diagnosis even when outputs already exist.",
    )
    args = parser.parse_args()
    run_product_strategies(
        dataset=args.dataset,
        output_root=args.output_root,
        base_config_dir=args.base_config_dir,
        verify_candidates=args.verify_candidates,
        rerun_diagnosis=args.rerun_diagnosis,
    )


if __name__ == "__main__":
    main()
