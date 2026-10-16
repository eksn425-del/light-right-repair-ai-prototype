"""Measure low-cost screening and label existing HB runtime evidence safely."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ENUMERATOR = ROOT / "src" / "legacy_route_b"
HISTORICAL_WORKERS = {
    "curated_initial": 2,
    "curated_extra": 4,
    "design_translation": 4,
    "independent_validation": 4,
}


def iqr(values: list[float]) -> float | None:
    """Return the interquartile range for a non-empty numeric list."""

    if not values:
        return None
    return float(np.percentile(values, 75) - np.percentile(values, 25))


def command_version(command: list[str]) -> str:
    """Read a short external-tool version without making it a hard dependency."""

    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=10)
        lines = (completed.stdout or completed.stderr).strip().splitlines()
        return lines[0][:200] if lines else "NOT_AVAILABLE"
    except (OSError, subprocess.SubprocessError):
        return "NOT_AVAILABLE"


def resource_snapshot() -> dict[str, object]:
    """Capture host and solver metadata for the runtime table."""

    try:
        import psutil

        ram_gb = round(psutil.virtual_memory().total / 1024**3, 2)
    except (ImportError, AttributeError):
        ram_gb = "NOT_AVAILABLE"
    return {
        "host_os": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count() or "NOT_AVAILABLE",
        "ram_gb": ram_gb,
        "radiance_version": command_version(["rtrace", "-version"]),
        "lbt_recipes_version": command_version(["lbt-recipes", "--version"]),
    }


def read_hb_records(path: Path) -> pd.DataFrame:
    """Read historical/current HB records and attach explicit worker provenance."""

    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    if "workers" in frame.columns:
        frame["worker_count"] = pd.to_numeric(frame["workers"], errors="coerce")
        frame["worker_source"] = "recorded_by_run_hb_batch"
    else:
        frame["worker_count"] = frame["scope"].map(HISTORICAL_WORKERS)
        frame["worker_source"] = "inferred_from_historical_invocation_documentation"
    return frame


def run_screening_repeats(run_dir: Path, repeats: int) -> list[dict[str, object]]:
    """Run isolated 2.5D repeats; no HB scene is launched here."""

    runtime_root = run_dir / "runtime_repeats"
    rows: list[dict[str, object]] = []
    for repeat in range(1, repeats + 1):
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
            completed = subprocess.run(
                [sys.executable, str(ENUMERATOR / "route_b_enumerate_2p5d_candidates.py")],
                env=env,
                cwd=ROOT,
                stdout=handle,
                stderr=subprocess.STDOUT,
            )
        elapsed = time.perf_counter() - started
        rows.append(
            {
                "experiment": "2.5D_screening_630",
                "repeat": repeat,
                "wall_seconds": elapsed,
                "exit_code": completed.returncode,
                "status": "PASS" if completed.returncode == 0 else "FAIL",
                "measurement_class": "measured_screening_repeat",
                "scope": "screening",
                "worker_count": "",
                "worker_source": "not_applicable",
                **resources,
            }
        )
        if completed.returncode != 0:
            raise RuntimeError(f"2.5D repeat failed: {log}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--skip-screening", action="store_true", help="Use existing repeat records; never affects HB evidence.")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    os.environ["LIGHT_EQUITY_RUN_ID"] = run_dir.name
    os.environ["LIGHT_EQUITY_RUN_DIR"] = str(run_dir)
    runtime = load_runtime()
    resources = resource_snapshot()

    if args.skip_screening:
        prior = run_dir / "results" / "runtime_benchmark_v2.csv"
        if prior.exists():
            rows = pd.read_csv(prior).to_dict(orient="records")
            rows = [{**row, **resources} for row in rows if row.get("measurement_class") == "measured_screening_repeat"]
        else:
            rows = []
    else:
        rows = run_screening_repeats(run_dir, args.repeats)
    hb = read_hb_records(run_dir / "logs" / "runtime_records.csv")
    for _, record in hb.iterrows():
        rows.append(
            {
                "experiment": f"HB_{record['scope']}",
                "repeat": "",
                "wall_seconds": float(record["wall_seconds"]),
                "exit_code": int(record["exit_code"]),
                "status": record["status"],
                "measurement_class": "measured_hb_scene",
                "scope": record["scope"],
                "worker_count": record.get("worker_count", ""),
                "worker_source": record.get("worker_source", ""),
                **resources,
            }
        )
    benchmark = pd.DataFrame(rows)
    results_dir = run_dir / "results"
    figures_dir = run_dir / "figures"
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    benchmark.to_csv(results_dir / "runtime_benchmark_v2.csv", index=False, encoding="utf-8-sig")

    screening = benchmark[(benchmark["measurement_class"] == "measured_screening_repeat") & benchmark["status"].eq("PASS")]["wall_seconds"].astype(float).tolist()
    hb_pass = benchmark[(benchmark["measurement_class"] == "measured_hb_scene") & benchmark["status"].eq("PASS")]["wall_seconds"].astype(float).tolist()
    hb_scopes = benchmark[benchmark["measurement_class"] == "measured_hb_scene"]["scope"].astype(str)
    hb_median = statistics.median(hb_pass) if hb_pass else None
    operational_count = int(hb_scopes.isin(["curated_initial", "curated_extra", "design_translation"]).sum())
    independent_count = int((hb_scopes == "independent_validation").sum())
    curated_rule_count = int((hb_scopes == "curated_extra").sum())
    serial_equivalent = 630 * hb_median if hb_median is not None else None
    worker_counts = benchmark.loc[benchmark["measurement_class"] == "measured_hb_scene"].dropna(subset=["worker_count"])
    workers_by_scope = {
        scope: sorted({int(value) for value in worker_counts.loc[worker_counts["scope"] == scope, "worker_count"]})
        for scope in sorted(worker_counts["scope"].unique())
    }
    summary = {
        "screening_repeat_count": len(screening),
        "screening_repeat_seconds": screening,
        "screening_mean_seconds": statistics.mean(screening) if screening else None,
        "screening_median_seconds": statistics.median(screening) if screening else None,
        "screening_iqr_seconds": iqr(screening),
        "hb_measured_scene_count": len(hb_pass),
        "hb_median_seconds_per_scene": hb_median,
        "hb_iqr_seconds_per_scene": iqr(hb_pass),
        "hb_min_seconds_per_scene": min(hb_pass) if hb_pass else None,
        "hb_max_seconds_per_scene": max(hb_pass) if hb_pass else None,
        "rule_candidate_universe_count": 630,
        "rule_candidate_verification_count": curated_rule_count,
        "rule_candidate_verification_fraction": curated_rule_count / 630,
        "operational_hb_scene_count": operational_count,
        "research_only_validation_scene_count": independent_count,
        "total_measured_hb_scene_count": len(hb_pass),
        "serial_equivalent_hb_630_seconds": serial_equivalent,
        "serial_equivalent_hb_630_label": "serial-equivalent extrapolation from the measured per-scene median; not directly measured",
        "operational_batch_elapsed_status": "NOT_MEASURED",
        "workers_by_scope": workers_by_scope,
        "worker_record_status": "historical records inferred from invocation documentation" if "inferred_from_historical_invocation_documentation" in set(benchmark.get("worker_source", [])) else "recorded",
        **resources,
        "measurement_semantics": {
            "screening": "measured wall-clock time for one complete 630-candidate 2.5D screening run",
            "hb_scene": "measured wall-clock time for one sequentially launched HB scene; each scene used its recorded worker count",
            "serial_equivalent_hb_630": "not a completed batch; 630 multiplied by measured per-scene median",
            "operational_vs_research": "33 operational workflow HB scenes; 20 independent validation scenes counted as research-only evidence",
        },
    }
    (results_dir / "runtime_summary_v2.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    plot_rows = [
        ("2.5D screening\nmedian", summary["screening_median_seconds"], "measured"),
        ("HB scene\nmedian", summary["hb_median_seconds_per_scene"], "measured"),
        ("HB 630\nserial-equivalent", summary["serial_equivalent_hb_630_seconds"], "extrapolated"),
    ]
    fig, ax = plt.subplots(figsize=(7, 4), dpi=220)
    labels = [row[0] for row in plot_rows]
    values = [row[1] or 0 for row in plot_rows]
    ax.bar(labels, values, color=["#2a9d8f", "#e9c46a", "#e76f51"])
    ax.set_ylabel("Wall time / seconds")
    ax.set_title("Measured screening/HB scene time and serial-equivalent extrapolation")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(figures_dir / "F07_runtime_comparison_v2.png")
    plt.close(fig)
    write_run_metadata(runtime, stage="runtime_benchmark_v2", inputs=[run_dir / "logs" / "runtime_records.csv"], extra=summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
