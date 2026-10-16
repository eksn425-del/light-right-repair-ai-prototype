from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "light_equity_project"
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from src.io.export_results import ensure_dir, write_csv, write_json  # noqa: E402
from src.visualization.plot_comparison import _simulate_selected_candidate  # noqa: E402


DATASET_DIR = PROJECT / "data" / "real_guankou" / "lakeside_leisure_ready"
GRID_3M_CONFIG = (
    PROJECT
    / "outputs"
    / "light_product_2026_06_03"
    / "grid_sensitivity"
    / "grid_3m"
    / "config_grid_3m"
)
GRID_3M_BASELINE = (
    PROJECT
    / "outputs"
    / "light_product_2026_06_03"
    / "grid_sensitivity"
    / "grid_3m"
    / "A_diagnosis"
)
CONSERVATIVE_6M_CANDIDATES = (
    PROJECT
    / "outputs"
    / "light_product_2026_06_02"
    / "strategy_comparison_postsim"
    / "conservative"
    / "B_candidates"
)
OUTPUT_DIR = ROOT / "paper_revision_work_2026_06_14" / "c6_c33_same_scheme_3m"


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"true", "1", "yes", "y"})


def main() -> None:
    ensure_dir(OUTPUT_DIR)
    start = time.time()

    # Keep a copy of the exact intervention input used for this same-scheme test.
    candidate_input_dir = ensure_dir(OUTPUT_DIR / "fixed_c6_c33_candidate_input")
    for name in ["candidate_scores.csv", "interventions.csv", "candidate_01.obj"]:
        src = CONSERVATIVE_6M_CANDIDATES / name
        if src.exists():
            shutil.copy2(src, candidate_input_dir / name)

    baseline_csv = GRID_3M_BASELINE / "sunlight_hours.csv"
    baseline_summary_path = GRID_3M_BASELINE / "A_summary.json"
    baseline = pd.read_csv(baseline_csv)
    baseline_summary = json.loads(baseline_summary_path.read_text(encoding="utf-8"))
    baseline_dark = float(_bool_series(baseline["is_dark_zone"]).mean())
    baseline_avg = float(baseline["sunlight_hours"].mean())

    post_dir = ensure_dir(OUTPUT_DIR / "post_simulation")
    post_sunlight, post_summary = _simulate_selected_candidate(
        dataset_dir=DATASET_DIR,
        candidates_dir=CONSERVATIVE_6M_CANDIDATES,
        output_dir=post_dir,
        config_dir=GRID_3M_CONFIG,
        selected_id="candidate_01",
    )
    interventions = pd.read_csv(CONSERVATIVE_6M_CANDIDATES / "interventions.csv")
    selected = interventions[interventions["candidate_id"].astype(str) == "candidate_01"].copy()
    changed_ids = ";".join(selected["target_building_id"].astype(str).tolist())
    volume = float(selected["volume_change"].abs().sum())

    post_dark = float(post_summary["dark_zone_ratio"])
    post_avg = float(post_summary["average_sunlight_hours"])
    dark_drop = baseline_dark - post_dark
    relative_improvement = dark_drop / baseline_dark if baseline_dark else 0.0
    avg_gain = post_avg - baseline_avg

    comparison = pd.DataFrame(
        [
            {
                "case_id": "baseline_3m",
                "grid_size_m": 3.0,
                "average_sunlight_hours": round(baseline_avg, 3),
                "dark_zone_ratio": round(baseline_dark, 4),
                "dark_zone_ratio_percent": round(baseline_dark * 100, 2),
                "dark_grid_count": int(_bool_series(baseline["is_dark_zone"]).sum()),
                "total_grid_count": int(len(baseline)),
                "changed_building_ids": "",
                "intervention_volume": 0.0,
                "notes": "3m baseline from prior grid-sensitivity diagnosis",
            },
            {
                "case_id": "c6_c33_same_scheme_3m",
                "grid_size_m": 3.0,
                "average_sunlight_hours": round(post_avg, 3),
                "dark_zone_ratio": round(post_dark, 4),
                "dark_zone_ratio_percent": round(post_dark * 100, 2),
                "dark_grid_count": int(post_summary["dark_grid_count"]),
                "total_grid_count": int(post_summary["total_grid_count"]),
                "changed_building_ids": changed_ids,
                "intervention_volume": round(volume, 3),
                "notes": "fixed 6m conservative candidate_01 interventions re-simulated on the 3m grid",
            },
        ]
    )
    comparison_path = write_csv(comparison, OUTPUT_DIR / "c6_c33_same_scheme_3m_metrics.csv")

    merged = baseline[["grid_id", "x", "y", "sunlight_hours", "is_dark_zone"]].merge(
        post_sunlight[["grid_id", "sunlight_hours", "is_dark_zone"]],
        on="grid_id",
        suffixes=("_baseline", "_post"),
    )
    merged["sunlight_diff_h"] = merged["sunlight_hours_post"] - merged["sunlight_hours_baseline"]
    merged["dark_to_light"] = _bool_series(merged["is_dark_zone_baseline"]) & ~_bool_series(
        merged["is_dark_zone_post"]
    )
    merged["light_to_dark"] = ~_bool_series(merged["is_dark_zone_baseline"]) & _bool_series(
        merged["is_dark_zone_post"]
    )
    diff_path = write_csv(merged, OUTPUT_DIR / "c6_c33_same_scheme_3m_grid_diff.csv")

    summary = {
        "grid_size_m": 3.0,
        "method": "Fixed C6/C33 conservative candidate_01 re-simulated on the existing 3m grid using the project simplified 2.5D sunlight simulator.",
        "baseline_average_sunlight_hours": round(baseline_avg, 3),
        "post_average_sunlight_hours": round(post_avg, 3),
        "average_sunlight_gain_h": round(avg_gain, 3),
        "baseline_dark_zone_ratio": round(baseline_dark, 4),
        "post_dark_zone_ratio": round(post_dark, 4),
        "baseline_dark_zone_percent": round(baseline_dark * 100, 2),
        "post_dark_zone_percent": round(post_dark * 100, 2),
        "dark_zone_drop_ratio_points": round(dark_drop * 100, 2),
        "relative_dark_zone_improvement": round(relative_improvement, 4),
        "baseline_dark_grid_count": int(_bool_series(baseline["is_dark_zone"]).sum()),
        "post_dark_grid_count": int(post_summary["dark_grid_count"]),
        "total_grid_count": int(post_summary["total_grid_count"]),
        "dark_to_light_grid_count": int(merged["dark_to_light"].sum()),
        "light_to_dark_grid_count": int(merged["light_to_dark"].sum()),
        "max_single_point_gain_h": round(float(merged["sunlight_diff_h"].max()), 3),
        "min_single_point_gain_h": round(float(merged["sunlight_diff_h"].min()), 3),
        "changed_building_ids": changed_ids,
        "intervention_volume": round(volume, 3),
        "candidate_source": str(CONSERVATIVE_6M_CANDIDATES),
        "config_source": str(GRID_3M_CONFIG),
        "comparison_csv": str(comparison_path),
        "grid_diff_csv": str(diff_path),
        "runtime_seconds": round(time.time() - start, 2),
        "interpretation": "This is not a new 3m optimization. It tests whether the same C6/C33 intervention remains directionally meaningful under a denser 3m ground grid.",
    }
    summary_path = write_json(summary, OUTPUT_DIR / "c6_c33_same_scheme_3m_summary.json")
    print(json.dumps({"summary": summary_path, "metrics": comparison_path, "data": summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
