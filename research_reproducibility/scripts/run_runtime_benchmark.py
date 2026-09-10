"""Measure 2.5D screening and summarize measured HB wall-clock costs."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ENUMERATOR = ROOT / "src" / "legacy_route_b"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    os.environ["LIGHT_EQUITY_RUN_ID"] = run_dir.name
    os.environ["LIGHT_EQUITY_RUN_DIR"] = str(run_dir)
    runtime = load_runtime()
    runtime_root = run_dir / "runtime_repeats"
    rows: list[dict[str, object]] = []
    for repeat in range(1, args.repeats + 1):
        repeat_dir = runtime_root / f"repeat_{repeat:02d}"
        if repeat_dir.exists():
            shutil.rmtree(repeat_dir)
        (repeat_dir / "results_csv").mkdir(parents=True, exist_ok=True)
        shutil.copytree(run_dir / "canonical_site_v2", repeat_dir / "canonical_site_v2")
        shutil.copy2(run_dir / "results_csv" / "100_HB_Radiance传感点.csv", repeat_dir / "results_csv" / "100_HB_Radiance传感点.csv")
        env = os.environ.copy()
        env.update(
            {
                "LIGHT_EQUITY_CONFIG": str(ROOT / "configs" / "research.yaml"),
                "LIGHT_EQUITY_RUN_ID": f"runtime_repeat_{repeat:02d}",
                "LIGHT_EQUITY_RUN_DIR": str(repeat_dir),
                "PYTHONPATH": str(ROOT / "src"),
            }
        )
        log = repeat_dir / "screening.log"
        started = time.perf_counter()
        with log.open("w", encoding="utf-8", errors="replace") as handle:
            completed = subprocess.run([sys.executable, str(ENUMERATOR / "route_b_enumerate_2p5d_candidates.py")], env=env, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT)
        elapsed = time.perf_counter() - started
        rows.append({"experiment": "2.5D_screening_630", "repeat": repeat, "wall_seconds": elapsed, "exit_code": completed.returncode, "status": "PASS" if completed.returncode == 0 else "FAIL", "scope": "measured"})
        if completed.returncode != 0:
            raise RuntimeError(f"2.5D repeat failed: {log}")

    hb_records = run_dir / "logs" / "runtime_records.csv"
    if hb_records.exists():
        hb = pd.read_csv(hb_records)
        for _, row in hb.iterrows():
            rows.append({"experiment": f"HB_{row['scope']}", "repeat": "", "wall_seconds": float(row["wall_seconds"]), "exit_code": int(row["exit_code"]), "status": row["status"], "scope": "measured"})
    benchmark = pd.DataFrame(rows)
    results_dir = run_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    benchmark.to_csv(results_dir / "runtime_benchmark.csv", index=False, encoding="utf-8-sig")

    screening = benchmark[(benchmark["experiment"] == "2.5D_screening_630") & (benchmark["status"] == "PASS")]["wall_seconds"].astype(float).tolist()
    hb_times = benchmark[benchmark["experiment"].str.startswith("HB_") & benchmark["status"].eq("PASS")]["wall_seconds"].astype(float).tolist()
    hb_median = statistics.median(hb_times) if hb_times else None
    summary = {
        "screening_repeats": screening,
        "screening_mean_seconds": statistics.mean(screening) if screening else None,
        "screening_median_seconds": statistics.median(screening) if screening else None,
        "screening_std_seconds": statistics.stdev(screening) if len(screening) > 1 else 0.0,
        "hb_measured_call_count": len(hb_times),
        "hb_median_seconds": hb_median,
        "estimated_full_hb_630_seconds": 630 * hb_median if hb_median is not None else None,
        "estimated_full_hb_630_label": "EXTRAPOLATED, not directly measured",
        "operational_workflow_hb_calls": int((benchmark["experiment"].isin(["HB_curated_initial", "HB_curated_extra", "HB_design_translation"])).sum()),
        "research_only_validation_hb_calls": int((benchmark["experiment"] == "HB_independent_validation").sum()),
        "high_fidelity_fraction_operational": int((benchmark["experiment"].isin(["HB_curated_initial", "HB_curated_extra", "HB_design_translation"])).sum()) / 630,
    }
    (results_dir / "runtime_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_run_metadata(runtime, stage="runtime_benchmark", inputs=[run_dir / "logs" / "runtime_records.csv"], extra=summary)

    labels = ["2.5D screening median", "HB median measured", "HB full-630 estimate"]
    values = [
        summary["screening_median_seconds"] or 0,
        summary["hb_median_seconds"] or 0,
        summary["estimated_full_hb_630_seconds"] or 0,
    ]
    fig, ax = plt.subplots(figsize=(7, 4), dpi=220)
    ax.bar(labels, values, color=["#2a9d8f", "#e9c46a", "#e76f51"])
    ax.set_ylabel("Wall time / seconds")
    ax.set_title("Measured and extrapolated computational cost")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(run_dir / "figures" / "runtime_comparison.png")
    plt.close(fig)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
