"""Run deterministic weight scenarios and an optional Monte Carlo rank check."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402


SCENARIOS = {
    "BASE": (0.45, 0.35, 0.10),
    "AREA_HEAVY": (0.55, 0.25, 0.10),
    "GAIN_HEAVY": (0.30, 0.50, 0.10),
    "BALANCED": (0.40, 0.40, 0.10),
    "VOLUME_SENSITIVE": (0.40, 0.30, 0.20),
}


def main() -> None:
    runtime = load_runtime()
    source = pd.read_csv(runtime.results_dir / "120_canonical_2p5D完整双建筑候选排名.csv")
    results_dir = runtime.run_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    ranked: dict[str, pd.DataFrame] = {}
    for name, (wa, wh, wv) in SCENARIOS.items():
        table = source[["candidate_id", "building_ids", "low_area_drop_h3_m2_norm", "avg_gain_vs_baseline_h_norm", "intervention_volume_m3_norm", "is_pareto_front"]].copy()
        table["scenario"] = name
        table["weight_area"] = wa
        table["weight_gain"] = wh
        table["weight_volume_penalty"] = wv
        table["scenario_score"] = wa * table["low_area_drop_h3_m2_norm"] + wh * table["avg_gain_vs_baseline_h_norm"] - wv * table["intervention_volume_m3_norm"]
        table = table.sort_values(["scenario_score", "candidate_id"], ascending=[False, True]).reset_index(drop=True)
        table["rank"] = np.arange(1, len(table) + 1)
        ranked[name] = table
        rows.extend(table.to_dict(orient="records"))
    sensitivity = pd.DataFrame(rows)
    base_top = {k: set(ranked["BASE"].nsmallest(k, "rank")["candidate_id"]) for k in (5, 10, 20)}
    summary_rows = []
    for name, table in ranked.items():
        aligned = table[["candidate_id", "rank"]].merge(
            ranked["BASE"][["candidate_id", "rank"]].rename(columns={"rank": "base_rank"}),
            on="candidate_id",
            how="inner",
        )
        summary_rows.append(
            {
                "scenario": name,
                "spearman_with_base": float(aligned["rank"].corr(aligned["base_rank"], method="spearman")),
                "top5_overlap": len(set(table.nsmallest(5, "rank")["candidate_id"]) & base_top[5]),
                "top10_overlap": len(set(table.nsmallest(10, "rank")["candidate_id"]) & base_top[10]),
                "top20_overlap": len(set(table.nsmallest(20, "rank")["candidate_id"]) & base_top[20]),
            }
        )
    sensitivity.to_csv(results_dir / "weight_sensitivity.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(summary_rows).to_csv(results_dir / "weight_sensitivity_summary.csv", index=False, encoding="utf-8-sig")

    rng = np.random.default_rng(runtime.seed)
    monte_carlo_rows: list[dict[str, object]] = []
    for draw in range(1000):
        wa = max(1e-9, 0.45 * rng.uniform(0.8, 1.2))
        wh = max(1e-9, 0.35 * rng.uniform(0.8, 1.2))
        wv = max(1e-9, 0.10 * rng.uniform(0.8, 1.2))
        score = wa * source["low_area_drop_h3_m2_norm"] + wh * source["avg_gain_vs_baseline_h_norm"] - wv * source["intervention_volume_m3_norm"]
        rank = score.rank(ascending=False, method="first").astype(int)
        for idx, value in enumerate(rank):
            monte_carlo_rows.append({"draw": draw, "candidate_id": source.iloc[idx]["candidate_id"], "rank": int(value), "top10": int(value <= 10)})
    mc = pd.DataFrame(monte_carlo_rows)
    stability = mc.groupby("candidate_id").agg(
        rank_mean=("rank", "mean"),
        rank_median=("rank", "median"),
        rank_std=("rank", "std"),
        top10_frequency=("top10", "mean"),
    ).reset_index().sort_values(["top10_frequency", "rank_mean"], ascending=[False, True])
    stability.to_csv(results_dir / "candidate_rank_stability.csv", index=False, encoding="utf-8-sig")

    top = stability.head(20).sort_values("top10_frequency")
    fig, ax = plt.subplots(figsize=(8, 6), dpi=220)
    ax.barh(top["candidate_id"], top["top10_frequency"], color="#457b9d")
    ax.set_xlabel("Top-10 selection frequency under weight perturbation")
    ax.set_title("Weight robustness of 2.5D candidate ranking")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(runtime.run_dir / "figures" / "weight_sensitivity_heatmap.png")
    plt.close(fig)

    write_run_metadata(
        runtime,
        stage="weight_sensitivity",
        inputs=[runtime.results_dir / "120_canonical_2p5D完整双建筑候选排名.csv"],
        extra={"scenario_count": len(SCENARIOS), "monte_carlo_draws": 1000},
    )
    print(pd.DataFrame(summary_rows).to_string(index=False))


if __name__ == "__main__":
    main()
