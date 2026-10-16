from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


REQUIRED_OUTPUTS = [
    "A_diagnosis/A_summary.json",
    "A_diagnosis/sunlight_hours.csv",
    "A_diagnosis/dark_zones.csv",
    "A_diagnosis/heatmap.png",
    "B_candidates/candidate_scores.csv",
    "B_candidates/interventions.csv",
    "C_validation/safety_report.csv",
    "C_validation/final_recommendation.json",
    "final_report/before_after_metrics.csv",
    "final_report/comparison_chart.png",
    "final_report/final_summary.json",
]


def _run(command: list[str], cwd: Path) -> None:
    print("[run]", " ".join(command))
    subprocess.run(command, cwd=str(cwd), check=True)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_outputs(output_dir: Path) -> list[str]:
    missing = [item for item in REQUIRED_OUTPUTS if not (output_dir / item).exists()]
    if missing:
        raise AssertionError(f"Missing outputs under {output_dir}: {missing}")
    zero = [item for item in REQUIRED_OUTPUTS if (output_dir / item).is_file() and (output_dir / item).stat().st_size == 0]
    if zero:
        raise AssertionError(f"Empty outputs under {output_dir}: {zero}")
    return missing


def _summarise(output_dir: Path) -> dict:
    a_summary = _read_json(output_dir / "A_diagnosis/A_summary.json")
    final = pd.read_csv(output_dir / "final_report/before_after_metrics.csv")
    safety = pd.read_csv(output_dir / "C_validation/safety_report.csv")
    selected = _read_json(output_dir / "C_validation/final_recommendation.json")
    algorithm = final[final["scheme_type"] == "algorithm_design"].iloc[0].to_dict()
    return {
        "output_dir_name": output_dir.name,
        "total_grid_count": int(a_summary["total_grid_count"]),
        "dark_grid_count": int(a_summary["dark_grid_count"]),
        "baseline_dark_zone_ratio": float(a_summary["dark_zone_ratio"]),
        "baseline_average_sunlight_hours": float(a_summary["average_sunlight_hours"]),
        "selected_candidate_id": selected["selected_candidate_id"],
        "algorithm_average_sunlight_hours": float(algorithm["average_sunlight_hours"]),
        "algorithm_dark_zone_ratio": float(algorithm["dark_zone_ratio"]),
        "algorithm_accessibility_coverage": float(algorithm["accessibility_coverage"]),
        "algorithm_safety_score": float(algorithm["safety_score"]),
        "passed_candidate_count": int(safety["passed"].astype(str).str.lower().isin({"true", "1"}).sum()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the Light Equity ABC pipeline.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dataset", default="sample_toy_street")
    parser.add_argument("--config-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--obj", type=Path)
    parser.add_argument("--verify-candidates", action="store_true")
    parser.add_argument("--regenerate-toy", action="store_true")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    config_dir = args.config_dir or project_root / "config"
    output_dir = args.output_dir.resolve()

    _run([sys.executable, "-m", "compileall", "-q", str(project_root)], project_root.parent)

    command = [
        sys.executable,
        str(project_root / "main.py"),
        "--dataset",
        args.dataset,
        "--config-dir",
        str(config_dir),
        "--output-dir",
        str(output_dir),
    ]
    if args.obj:
        command += ["--obj", str(args.obj), "--overwrite-obj-dataset"]
    if args.regenerate_toy:
        command.append("--regenerate-toy")
    if args.verify_candidates:
        command.append("--verify-candidates")
    _run(command, project_root.parent)

    _assert_outputs(output_dir)
    summary = _summarise(output_dir)
    report_path = output_dir / "validation_report.json"
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[ok] validation report:", report_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
