"""Analyze the frozen independent 2.5D versus HB-Radiance sample."""

from __future__ import annotations

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
sys.path.insert(0, str(ROOT / "src" / "legacy_route_b"))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402
from route_b_enumerate_2p5d_candidates import hours_from_blocked, load_geometries, precompute_blockers, solar_samples  # noqa: E402


def read_values(path: Path) -> np.ndarray:
    return np.array([float(value) for value in path.read_text(encoding="utf-8", errors="ignore").splitlines() if value.strip()], dtype=float)


def main() -> None:
    runtime = load_runtime()
    validation = runtime.run_dir / "independent_validation"
    results_dir = runtime.run_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    sample = pd.read_csv(validation / "VALIDATION_SAMPLE_FROZEN.csv")
    buildings = pd.read_csv(runtime.run_dir / "canonical_site_v2" / "canonical_buildings.csv")
    grid = pd.read_csv(validation / "sensor_points.csv")
    geoms = load_geometries()
    solar = solar_samples()
    original_blockers, reduced_blockers = precompute_blockers(buildings, grid, geoms, solar)
    by_id = {bid: idx for idx, bid in enumerate(buildings["building_id"].tolist())}
    baseline_2d = hours_from_blocked(original_blockers.any(axis=0), len(grid), len(solar))
    cell_area = runtime.grid_size_m ** 2

    grid_name = f"ground_{runtime.grid_size_m:g}m_road_open_space"
    baseline_res = runtime.run_dir / "hb_radiance_project_batch" / "baseline" / "direct_sun_hours" / "results" / "cumulative" / f"{grid_name}.res"
    baseline_hb = read_values(baseline_res)
    if len(baseline_hb) != len(grid):
        raise ValueError("Baseline HB sensor count does not match the frozen sample grid.")

    rows: list[dict[str, object]] = []
    for _, candidate in sample.iterrows():
        pair = str(candidate["pair_key"])
        a, b = [part.strip() for part in pair.split(",")]
        ia, ib = by_id[a], by_id[b]
        blocked_count = original_blockers.sum(axis=0) - original_blockers[ia] - original_blockers[ib] + reduced_blockers[ia] + reduced_blockers[ib]
        two_d_hours = hours_from_blocked(blocked_count > 0, len(grid), len(solar))
        scenario = str(candidate["scenario"]) if "scenario" in candidate else f"independent_{int(candidate['sample_order']):02d}_{a}_{b}_rule_flat"
        hb_res = runtime.run_dir / "independent_validation" / "hb_batch" / scenario / "direct_sun_hours" / "results" / "cumulative" / f"{grid_name}.res"
        hb_hours = read_values(hb_res)
        if len(hb_hours) != len(grid):
            raise ValueError(f"{pair}: HB sensor count does not match the frozen sample grid.")
        two_d_drop = float(((baseline_2d < runtime.low_threshold_h).sum() - (two_d_hours < runtime.low_threshold_h).sum()) * cell_area)
        hb_drop = float(((baseline_hb < runtime.low_threshold_h).sum() - (hb_hours < runtime.low_threshold_h).sum()) * cell_area)
        rows.append(
            {
                "sample_order": int(candidate["sample_order"]),
                "pair_key": pair,
                "stratum": candidate["stratum"],
                "intervention_volume_m3": float(candidate["intervention_volume_m3"]),
                "two_d_low_area_drop_h3_m2": two_d_drop,
                "hb_low_area_drop_h3_m2": hb_drop,
                "two_d_avg_gain_h": float((two_d_hours - baseline_2d).mean()),
                "hb_avg_gain_h": float((hb_hours - baseline_hb).mean()),
                "two_d_improves": bool(two_d_drop > 0),
                "hb_improves": bool(hb_drop > 0),
            }
        )
    result = pd.DataFrame(rows)
    result["low_area_error_m2"] = result["two_d_low_area_drop_h3_m2"] - result["hb_low_area_drop_h3_m2"]
    result["absolute_error_m2"] = result["low_area_error_m2"].abs()
    result["rank_2p5d"] = result["two_d_low_area_drop_h3_m2"].rank(ascending=False, method="min").astype(int)
    result["rank_hb"] = result["hb_low_area_drop_h3_m2"].rank(ascending=False, method="min").astype(int)
    result.to_csv(results_dir / "independent_validation_results.csv", index=False, encoding="utf-8-sig")

    x = result["two_d_low_area_drop_h3_m2"].to_numpy(float)
    y = result["hb_low_area_drop_h3_m2"].to_numpy(float)
    rho = float(spearmanr(x, y).statistic)
    pearson = float(pearsonr(x, y).statistic) if np.std(x) > 0 and np.std(y) > 0 else float("nan")
    metrics = [
        {"metric": "sample_size", "value": len(result), "unit": "candidates"},
        {"metric": "seed", "value": runtime.seed, "unit": "fixed seed"},
        {"metric": "spearman_rho", "value": rho, "unit": "rank correlation"},
        {"metric": "pearson_r", "value": pearson, "unit": "linear correlation"},
        {"metric": "mae_low_area", "value": float(result["absolute_error_m2"].mean()), "unit": "m2"},
        {"metric": "median_absolute_error_low_area", "value": float(result["absolute_error_m2"].median()), "unit": "m2"},
        {"metric": "mean_bias_2p5d_minus_hb", "value": float(result["low_area_error_m2"].mean()), "unit": "m2"},
        {"metric": "sign_agreement", "value": float((result["two_d_improves"] == result["hb_improves"]).mean()), "unit": "fraction"},
        {"metric": "rank_direction_consistency", "value": float((np.sign(x - x.mean()) == np.sign(y - y.mean())).mean()), "unit": "fraction"},
    ]
    for k in (3, 5, 10):
        top_x = set(result.nsmallest(min(k, len(result)), "rank_2p5d")["pair_key"])
        top_y = set(result.nsmallest(min(k, len(result)), "rank_hb")["pair_key"])
        metrics.append({"metric": f"within_sample_top_{k}_overlap", "value": len(top_x & top_y), "unit": "candidates"})
        metrics.append({"metric": f"within_sample_top_{k}_recall", "value": len(top_x & top_y) / min(k, len(result)), "unit": "fraction"})
    metric_df = pd.DataFrame(metrics)
    metric_df.to_csv(results_dir / "independent_validation_metrics.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(6, 5), dpi=220)
    ax.scatter(x, y, c=pd.Categorical(result["stratum"]).codes, cmap="viridis", s=42)
    lim = [min(x.min(), y.min()) - 5, max(x.max(), y.max()) + 5]
    ax.plot(lim, lim, color="black", linewidth=1)
    ax.set_xlabel("2.5D low-area reduction / m2")
    ax.set_ylabel("HB-Radiance low-area reduction / m2")
    ax.set_title(f"Independent sample agreement (rho={rho:.3f})")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(runtime.run_dir / "figures" / "independent_validation_scatter.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5), dpi=220)
    ordered = result.sort_values("rank_hb")
    ax.plot(ordered["pair_key"], ordered["rank_2p5d"], marker="o", label="2.5D rank")
    ax.plot(ordered["pair_key"], ordered["rank_hb"], marker="o", label="HB-Radiance rank")
    ax.set_ylabel("Rank (lower is better)")
    ax.set_title("Independent-sample rank comparison")
    ax.tick_params(axis="x", rotation=60)
    ax.invert_yaxis()
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(runtime.run_dir / "figures" / "independent_validation_rank.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4), dpi=220)
    ax.bar(result["pair_key"], result["low_area_error_m2"], color=np.where(result["low_area_error_m2"] >= 0, "#2a9d8f", "#e76f51"))
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("2.5D minus HB low-area error / m2")
    ax.set_title("Independent-sample error")
    ax.tick_params(axis="x", rotation=60)
    fig.tight_layout()
    fig.savefig(runtime.run_dir / "figures" / "independent_validation_error.png")
    plt.close(fig)

    write_run_metadata(
        runtime,
        stage="analyze_independent_validation",
        inputs=[validation / "VALIDATION_SAMPLE_FROZEN.csv", results_dir / "independent_validation_results.csv"],
        extra={"sample_size": len(result), "spearman_rho": rho, "pearson_r": pearson},
    )
    print(json.dumps({"sample_size": len(result), "spearman_rho": rho, "pearson_r": pearson}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
