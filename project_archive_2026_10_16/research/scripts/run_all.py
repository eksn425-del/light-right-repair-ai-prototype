"""Run the reproducible Route B baseline pipeline in an isolated run folder."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "src" / "legacy_route_b"
PYTHON = sys.executable


def execute(script: Path, env: dict[str, str]) -> None:
    print(f"[stage] {script.name}")
    subprocess.run([PYTHON, str(script)], check=True, env=env, cwd=ROOT)


def execute_hb(manifest: Path, log_dir: Path, records: Path, scope: str, env: dict[str, str], workers: int) -> None:
    subprocess.run(
        [
            PYTHON,
            str(ROOT / "scripts" / "run_hb_batch.py"),
            "--manifest",
            str(manifest),
            "--log-dir",
            str(log_dir),
            "--records",
            str(records),
            "--scope",
            scope,
            "--workers",
            str(workers),
        ],
        check=True,
        env=env,
        cwd=ROOT,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="baseline_20260909_clean")
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "research.yaml")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--skip-hb", action="store_true")
    args = parser.parse_args()

    run_dir = (args.run_dir or ROOT / "experiments" / args.run_id).resolve()
    env = os.environ.copy()
    env.update(
        {
            "LIGHT_EQUITY_CONFIG": str(args.config.resolve()),
            "LIGHT_EQUITY_RUN_ID": args.run_id,
            "LIGHT_EQUITY_RUN_DIR": str(run_dir),
            "PYTHONPATH": str(ROOT / "src"),
        }
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    logs = run_dir / "logs"
    records = logs / "runtime_records.csv"
    stages = [
        CODE / "route_b_geometry_audit.py",
        CODE / "route_b_prepare_hb_batch.py",
        CODE / "route_b_enumerate_2p5d_candidates.py",
        CODE / "route_b_prepare_hb_extra_candidates.py",
    ]
    for script in stages:
        execute(script, env)

    if not args.skip_hb:
        execute_hb(run_dir / "hb_radiance_project_batch" / "run_manifest.csv", logs / "hb_initial", records, "curated_initial", env, args.workers)

    execute(CODE / "route_b_prepare_hb_final_design_candidates.py", env)
    if not args.skip_hb:
        execute_hb(run_dir / "hb_radiance_project_batch_extra" / "run_manifest.csv", logs / "hb_extra", records, "curated_extra", env, args.workers)
        execute_hb(run_dir / "hb_radiance_project_final_design" / "run_manifest.csv", logs / "hb_design", records, "design_translation", env, args.workers)

    if not args.skip_hb:
        execute(CODE / "route_b_collect_hb_merged_results.py", env)
        execute(CODE / "route_b_compare_2d_hb.py", env)
        execute(CODE / "route_b_compare_verified_2p5d_hb.py", env)
        execute(CODE / "route_b_final_candidate_judgement.py", env)
    print(f"[done] {run_dir}")


if __name__ == "__main__":
    main()
