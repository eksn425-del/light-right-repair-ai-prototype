"""Validate the production four-term composite ranking on the frozen sample."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_runtime import load_runtime, production_score, sha256, write_run_metadata  # noqa: E402


NORMALIZATION_COLUMNS = {
    "low_area_drop_h3_m2": "low_area_drop_h3_m2_norm",
    "avg_gain_vs_baseline_h": "avg_gain_vs_baseline_h_norm",
    "intervention_volume_m3": "intervention_volume_m3_norm",
    "new_low_area_h3_m2": "new_low_area_h3_m2_norm",
}
SCORE_COLUMNS = (
    "low_area_drop_h3_m2",
    "avg_gain_vs_baseline_h",
    "intervention_volume_m3",
    "new_low_area_h3_m2",
)


def read_values(path: Path) -> np.ndarray:
    """Read numeric Radiance result values from a whitespace-delimited file."""

    return np.array(
        [float(value) for value in path.read_text(encoding="utf-8", errors="ignore").split() if value.strip()],
        dtype=float,
    )


def normalize(value: float, lower: float, upper: float) -> float:
    """Normalize with fixed full-universe bounds and no outcome-based refit."""

    if abs(upper - lower) < 1e-12:
        return 0.0
    return (float(value) - lower) / (upper - lower)


def deterministic_rank(frame: pd.DataFrame, score_column: str) -> pd.Series:
    """Return one-based ranks with a stable pair-key tie break."""

    ordered = frame.sort_values([score_column, "pair_key"], ascending=[False, True])
    ranks = pd.Series(index=ordered.index, data=np.arange(1, len(ordered) + 1), dtype=int)
    return ranks.reindex(frame.index)


def result_path(run_dir: Path, scenario: str, grid_name: str) -> Path:
    """Resolve one measured HB cumulative result file."""

    return run_dir / "independent_validation" / "hb_batch" / scenario / "direct_sun_hours" / "results" / "cumulative" / f"{grid_name}.res"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    sys.path.insert(0, str(ROOT / "src" / "legacy_route_b"))
    runtime = load_runtime(run_dir=run_dir)
    validation = run_dir / "independent_validation"
    results_dir = run_dir / "results"
    figures_dir = run_dir / "figures"
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    sample_path = validation / "VALIDATION_SAMPLE_FROZEN.csv"
    frozen_digest = sha256(sample_path)
    declared_digest = (validation / "VALIDATION_SAMPLE_FROZEN.sha256").read_text(encoding="ascii").strip()
    if frozen_digest != declared_digest:
        raise AssertionError("Frozen independent sample SHA256 does not match its declaration")
    sample = pd.read_csv(sample_path)
    if len(sample) != 20 or sample["pair_key"].duplicated().any():
        raise AssertionError("The declared N=20 independent sample must remain unchanged and unique")

    candidates = pd.read_csv(runtime.results_dir / "120_canonical_2p5D完整双建筑候选排名.csv")
    candidates["pair_key"] = candidates["building_ids"].map(
        lambda value: ",".join(sorted(str(value).split(","), key=lambda item: int(item.strip()[1:])))
    )
    if len(candidates) != 630 or candidates["pair_key"].duplicated().any():
        raise AssertionError("Composite normalization requires the complete unique 630-candidate universe")
    candidate_view = candidates[
        ["pair_key", "candidate_id", "score", *SCORE_COLUMNS]
    ].rename(
        columns={
            "candidate_id": "candidate_id_2p5d",
            "score": "score_2p5d",
            "intervention_volume_m3": "intervention_volume_m3_2p5d",
        }
    )
    sample_keys = sample[["sample_order", "pair_key", "stratum"]].copy()
    selected = sample_keys.merge(candidate_view, on="pair_key", how="left", validate="one_to_one")
    if selected["candidate_id_2p5d"].isna().any():
        raise AssertionError("Every frozen pair must exist in the current 630-candidate universe")

    bounds = {
        column: {
            "min": float(candidates[column].min()),
            "max": float(candidates[column].max()),
        }
        for column in SCORE_COLUMNS
    }
    grid_name = f"ground_{runtime.grid_size_m:g}m_road_open_space"
    baseline_path = run_dir / "hb_radiance_project_batch" / "baseline" / "direct_sun_hours" / "results" / "cumulative" / f"{grid_name}.res"
    baseline_hb = read_values(baseline_path)
    sensor_count = len(pd.read_csv(validation / "sensor_points.csv"))
    if len(baseline_hb) != sensor_count:
        raise ValueError("Baseline HB sensor count does not match the frozen validation grid")

    rows: list[dict[str, object]] = []
    for row in selected.sort_values("sample_order").itertuples(index=False):
        pair = str(row.pair_key)
        a, b = [part.strip() for part in pair.split(",")]
        scenario = f"independent_{int(row.sample_order):02d}_{a}_{b}_rule_flat"
        path = result_path(run_dir, scenario, grid_name)
        if not path.exists():
            raise FileNotFoundError(f"Missing measured independent HB result for {pair}: {path}")
        hb_hours = read_values(path)
        if len(hb_hours) != sensor_count:
            raise ValueError(f"{pair}: HB sensor count does not match the frozen validation grid")
        hb_low_area = float((hb_hours < runtime.low_threshold_h).sum() * runtime.grid_size_m**2)
        baseline_low_area = float((baseline_hb < runtime.low_threshold_h).sum() * runtime.grid_size_m**2)
        hb_drop = baseline_low_area - hb_low_area
        hb_gain = float((hb_hours - baseline_hb).mean())
        hb_new_low = float(((baseline_hb >= runtime.low_threshold_h) & (hb_hours < runtime.low_threshold_h)).sum() * runtime.grid_size_m**2)
        rows.append(
            {
                "sample_order": int(row.sample_order),
                "candidate_id": row.candidate_id_2p5d,
                "pair_key": pair,
                "stratum": row.stratum,
                "intervention_volume_m3": float(row.intervention_volume_m3_2p5d),
                "two_d_low_area_drop_h3_m2": float(row.low_area_drop_h3_m2),
                "hb_low_area_drop_h3_m2": hb_drop,
                "two_d_avg_gain_h": float(row.avg_gain_vs_baseline_h),
                "hb_avg_gain_h": hb_gain,
                "two_d_new_low_area_h3_m2": float(row.new_low_area_h3_m2),
                "hb_new_low_area_h3_m2": hb_new_low,
                "two_d_score": float(row.score_2p5d),
            }
        )
    result = pd.DataFrame(rows)

    for prefix in ("two_d", "hb"):
        raw_columns = {
            "two_d": {
                "low_area_drop_h3_m2": "two_d_low_area_drop_h3_m2",
                "avg_gain_vs_baseline_h": "two_d_avg_gain_h",
                "intervention_volume_m3": "intervention_volume_m3",
                "new_low_area_h3_m2": "two_d_new_low_area_h3_m2",
            },
            "hb": {
                "low_area_drop_h3_m2": "hb_low_area_drop_h3_m2",
                "avg_gain_vs_baseline_h": "hb_avg_gain_h",
                "intervention_volume_m3": "intervention_volume_m3",
                "new_low_area_h3_m2": "hb_new_low_area_h3_m2",
            },
        }[prefix]
        for raw, output_norm in NORMALIZATION_COLUMNS.items():
            result[f"{prefix}_{output_norm}"] = result[raw_columns[raw]].map(
                lambda value, raw=raw: normalize(value, bounds[raw]["min"], bounds[raw]["max"])
            )
        result[f"{prefix}_score"] = production_score(
            result[f"{prefix}_low_area_drop_h3_m2_norm"],
            result[f"{prefix}_avg_gain_vs_baseline_h_norm"],
            result[f"{prefix}_intervention_volume_m3_norm"],
            result[f"{prefix}_new_low_area_h3_m2_norm"],
            runtime.score_weights,
        )
    result["rank_2p5d"] = deterministic_rank(result, "two_d_score")
    result["rank_hb"] = deterministic_rank(result, "hb_score")
    result["abs_rank_error"] = (result["rank_2p5d"] - result["rank_hb"]).abs()
    result = result.sort_values("sample_order").reset_index(drop=True)
    result.to_csv(results_dir / "independent_composite_ranking.csv", index=False, encoding="utf-8-sig")

    x = result["two_d_score"].to_numpy(float)
    y = result["hb_score"].to_numpy(float)
    rho_result = spearmanr(x, y)
    pearson_result = pearsonr(x, y)
    metrics: list[dict[str, object]] = [
        {"metric": "sample_size", "value": len(result), "unit": "candidates", "notes": "frozen independent sample only"},
        {"metric": "normalization_universe_size", "value": len(candidates), "unit": "candidates", "notes": "fixed before reading HB outcomes"},
        {"metric": "spearman_rho", "value": float(rho_result.statistic), "unit": "rank correlation", "notes": "2.5D composite versus HB composite"},
        {"metric": "spearman_pvalue", "value": float(rho_result.pvalue), "unit": "p-value", "notes": "within-independent-sample test"},
        {"metric": "pearson_r", "value": float(pearson_result.statistic), "unit": "linear correlation", "notes": "composite score values"},
        {"metric": "top3_overlap", "value": int(len(set(result.nsmallest(3, "rank_2p5d")["pair_key"]) & set(result.nsmallest(3, "rank_hb")["pair_key"]))), "unit": "candidates", "notes": "HB composite as reference"},
        {"metric": "top3_recall", "value": float(len(set(result.nsmallest(3, "rank_2p5d")["pair_key"]) & set(result.nsmallest(3, "rank_hb")["pair_key"])) / 3), "unit": "fraction", "notes": "within-independent-sample only"},
        {"metric": "top5_overlap", "value": int(len(set(result.nsmallest(5, "rank_2p5d")["pair_key"]) & set(result.nsmallest(5, "rank_hb")["pair_key"]))), "unit": "candidates", "notes": "HB composite as reference"},
        {"metric": "top5_recall", "value": float(len(set(result.nsmallest(5, "rank_2p5d")["pair_key"]) & set(result.nsmallest(5, "rank_hb")["pair_key"])) / 5), "unit": "fraction", "notes": "within-independent-sample only"},
        {"metric": "top10_overlap", "value": int(len(set(result.nsmallest(10, "rank_2p5d")["pair_key"]) & set(result.nsmallest(10, "rank_hb")["pair_key"]))), "unit": "candidates", "notes": "HB composite as reference"},
        {"metric": "top10_recall", "value": float(len(set(result.nsmallest(10, "rank_2p5d")["pair_key"]) & set(result.nsmallest(10, "rank_hb")["pair_key"])) / 10), "unit": "fraction", "notes": "within-independent-sample only"},
        {"metric": "mean_absolute_rank_error", "value": float(result["abs_rank_error"].mean()), "unit": "rank positions", "notes": "absolute 2.5D versus HB composite rank error"},
        {"metric": "median_absolute_rank_error", "value": float(result["abs_rank_error"].median()), "unit": "rank positions", "notes": "absolute 2.5D versus HB composite rank error"},
        {"metric": "max_absolute_rank_error", "value": float(result["abs_rank_error"].max()), "unit": "rank positions", "notes": "absolute 2.5D versus HB composite rank error"},
    ]
    metric_df = pd.DataFrame(metrics)
    metric_df.to_csv(results_dir / "independent_composite_metrics.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(6.5, 5.5), dpi=320)
    ax.scatter(x, y, c=pd.Categorical(result["stratum"]).codes, cmap="viridis", s=48, edgecolors="white", linewidths=0.4)
    lim = [min(x.min(), y.min()) - 0.01, max(x.max(), y.max()) + 0.01]
    ax.plot(lim, lim, color="#555555", linewidth=1, linestyle="--")
    ax.set_xlabel("2.5D four-term composite score")
    ax.set_ylabel("HB-Radiance four-term composite score")
    ax.set_title(f"Independent composite-ranking agreement (rho={rho_result.statistic:.3f})")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(figures_dir / "F09_independent_composite_ranking.png")
    plt.close(fig)

    metadata = {
        "sample_size": len(result),
        "frozen_sample_sha256": frozen_digest,
        "normalization_bounds_from_630_2p5d_universe": bounds,
        "score_weights": runtime.score_weights,
        "threshold_h": runtime.low_threshold_h,
        "grid_size_m": runtime.grid_size_m,
        "timezone": runtime.timezone,
        "timestep_minutes": runtime.timestep_minutes,
        "status": "within-independent-sample_composite-ranking_agreement",
    }
    (results_dir / "independent_composite_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    write_run_metadata(
        runtime,
        stage="independent_composite_validation",
        inputs=[sample_path, runtime.results_dir / "120_canonical_2p5D完整双建筑候选排名.csv", baseline_path],
        extra={"sample_size": len(result), "spearman_rho": float(rho_result.statistic), "frozen_sample_sha256": frozen_digest},
    )
    print(metric_df.to_string(index=False))


if __name__ == "__main__":
    main()
