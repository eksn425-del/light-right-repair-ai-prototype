from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.algorithm_a_diagnosis.run_diagnosis import run_diagnosis
from src.algorithm_b_optimization.post_simulation_ranker import verify_and_rerank_candidates
from src.algorithm_b_optimization.run_optimization import run_optimization
from src.algorithm_c_validation.run_validation import run_validation
from src.geometry.toy_street_generator import generate_toy_street
from src.io.export_results import ensure_dir
from src.io.obj_dataset_builder import build_dataset_from_obj, default_auto_dataset_dir
from src.visualization.plot_comparison import build_final_report


PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


def _required_dataset_files(dataset_dir: Path) -> list[Path]:
    return [
        dataset_dir / "site_model.obj",
        dataset_dir / "buildings.csv",
        dataset_dir / "streets.csv",
        dataset_dir / "nodes.csv",
        dataset_dir / "protected_zones.csv",
    ]


def _prepare_dataset(dataset_name: str, regenerate_toy: bool = False) -> Path:
    dataset_dir = DATA_DIR / dataset_name
    if dataset_name == "sample_toy_street":
        generate_toy_street(dataset_dir, overwrite=regenerate_toy)
    missing = [path for path in _required_dataset_files(dataset_dir) if not path.exists()]
    if missing:
        missing_text = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(
            f"Dataset '{dataset_name}' is incomplete. Missing files:\n{missing_text}"
        )
    return dataset_dir


def _prepare_obj_dataset(obj_path: Path, overwrite: bool = False) -> tuple[str, Path]:
    dataset_dir = default_auto_dataset_dir(DATA_DIR, obj_path)
    result = build_dataset_from_obj(obj_path, dataset_dir, overwrite=overwrite)
    print(f"Auto OBJ dataset: {result['dataset_dir']}")
    print(f"Auto OBJ summary: {result['summary']}")
    if result.get("warning") and result["warning"] != "ok":
        print(f"[OBJ WARNING] {result['warning']}")
    dataset_name = str(dataset_dir.relative_to(DATA_DIR)).replace("\\", "/")
    return dataset_name, dataset_dir


def _print_paths(step: str, outputs: dict) -> None:
    print(f"\n[{step}]")
    for key, value in outputs.items():
        if key.endswith("_data"):
            continue
        if isinstance(value, list):
            for item in value:
                print(f"- {key}: {item}")
        else:
            print(f"- {key}: {value}")


def run_pipeline(
    dataset_name: str,
    regenerate_toy: bool = False,
    output_root: Path | None = None,
    dataset_dir_override: Path | None = None,
    config_dir: Path = CONFIG_DIR,
    verify_candidates: bool = False,
    diagnosis_only: bool = False,
) -> dict:
    """Run the complete A/B/C and final-report workflow."""
    dataset_dir = dataset_dir_override or _prepare_dataset(dataset_name, regenerate_toy)
    config_dir = Path(config_dir)
    if output_root is None:
        diagnosis_dir = ensure_dir(OUTPUTS_DIR / "A_diagnosis")
        candidates_dir = ensure_dir(OUTPUTS_DIR / "B_candidates")
        validation_dir = ensure_dir(OUTPUTS_DIR / "C_validation")
        report_dir = ensure_dir(OUTPUTS_DIR / "final_report")
    else:
        output_root = ensure_dir(Path(output_root))
        diagnosis_dir = ensure_dir(output_root / "A_diagnosis")
        candidates_dir = ensure_dir(output_root / "B_candidates")
        validation_dir = ensure_dir(output_root / "C_validation")
        report_dir = ensure_dir(output_root / "final_report")

    print(f"Dataset: {dataset_name}")
    print(f"Dataset folder: {dataset_dir}")

    diagnosis_outputs = run_diagnosis(dataset_dir, diagnosis_dir, config_dir)
    _print_paths("Algorithm A diagnosis", diagnosis_outputs)

    if diagnosis_only:
        print("\nDiagnosis-only mode finished.")
        return {
            "dataset_dir": dataset_dir,
            "diagnosis": diagnosis_outputs,
            "optimization": None,
            "candidate_verification": None,
            "validation": None,
            "final_report": None,
        }

    optimization_outputs = run_optimization(dataset_dir, diagnosis_dir, candidates_dir, config_dir)
    _print_paths("Algorithm B candidates", optimization_outputs)

    verification_outputs = None
    if verify_candidates:
        verification_dir = ensure_dir(candidates_dir / "post_simulation_verification")
        verification_outputs = verify_and_rerank_candidates(
            dataset_dir,
            diagnosis_dir,
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
        diagnosis_dir,
        candidates_dir,
        validation_dir,
        report_dir,
        config_dir,
    )
    _print_paths("Final report", report_outputs)

    print("\nPipeline finished.")
    return {
        "dataset_dir": dataset_dir,
        "diagnosis": diagnosis_outputs,
        "optimization": optimization_outputs,
        "candidate_verification": verification_outputs,
        "validation": validation_outputs,
        "final_report": report_outputs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Light Equity Restoration ABC workflow.")
    parser.add_argument(
        "--dataset",
        default="sample_toy_street",
        help="Dataset folder under data/. The public demo includes sample_toy_street.",
    )
    parser.add_argument(
        "--obj",
        type=Path,
        help="Optional standalone OBJ. The pipeline will auto-generate a rough dataset under data/auto_obj/.",
    )
    parser.add_argument(
        "--overwrite-obj-dataset",
        action="store_true",
        help="Overwrite the auto-generated dataset for --obj.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional output folder. If omitted, legacy outputs/A_diagnosis etc. are used.",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=CONFIG_DIR,
        help="Config folder containing site_config.yaml, solar_config.yaml, and accessibility_rules.yaml.",
    )
    parser.add_argument(
        "--verify-candidates",
        action="store_true",
        help="Re-simulate each B candidate and replace candidate_scores.csv with verified ranking before C.",
    )
    parser.add_argument(
        "--diagnosis-only",
        action="store_true",
        help="Run only Algorithm A. Useful for standalone OBJ smoke tests or single-mass validation.",
    )
    parser.add_argument(
        "--regenerate-toy",
        action="store_true",
        help="Regenerate the toy street data before running.",
    )
    args = parser.parse_args()
    try:
        dataset_name = args.dataset
        dataset_dir_override = None
        if args.obj:
            dataset_name, dataset_dir_override = _prepare_obj_dataset(
                args.obj,
                overwrite=args.overwrite_obj_dataset,
            )
        run_pipeline(
            dataset_name,
            regenerate_toy=args.regenerate_toy,
            output_root=args.output_dir,
            dataset_dir_override=dataset_dir_override,
            config_dir=args.config_dir,
            verify_candidates=args.verify_candidates,
            diagnosis_only=args.diagnosis_only,
        )
    except Exception as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
