"""Run the four-term production-score sensitivity analysis.

The historical three-term sensitivity files are intentionally left in place
for auditability. This script writes the superseding ``*_v2`` outputs and
reads the BASE weights from the single YAML configuration source.
"""

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
from research_runtime import load_runtime, production_score, write_run_metadata  # noqa: E402


MONTE_CARLO_SEED = 20260909
SCENARIO_ORDER = ["BASE", "AREA_HEAVY", "GAIN_HEAVY", "VOLUME_SENSITIVE", "NEW_LOW_SENSITIVE", "BALANCED"]
FOCUS_PAIRS = ["C9,C15", "C9,C13", "C9,C24"]
WEIGHT_KEYS = (
    "low_area_drop_weight",
    "avg_gain_weight",
    "intervention_volume_economy_weight",
    "new_low_area_avoidance_weight",
)


def scenario_weights(runtime) -> dict[str, dict[str, float]]:
    """Return preregistered four-term weight scenarios."""

    base = runtime.score_weights
    return {
        "BASE": base,
        "AREA_HEAVY": {
            "low_area_drop_weight": 0.55,
            "avg_gain_weight": 0.25,
            "intervention_volume_economy_weight": 0.15,
            "new_low_area_avoidance_weight": 0.05,
        },
        "GAIN_HEAVY": {
            "low_area_drop_weight": 0.30,
            "avg_gain_weight": 0.50,
            "intervention_volume_economy_weight": 0.15,
            "new_low_area_avoidance_weight": 0.05,
        },
        "VOLUME_SENSITIVE": {
            "low_area_drop_weight": 0.40,
            "avg_gain_weight": 0.30,
            "intervention_volume_economy_weight": 0.25,
            "new_low_area_avoidance_weight": 0.05,
        },
        "NEW_LOW_SENSITIVE": {
            "low_area_drop_weight": 0.40,
            "avg_gain_weight": 0.30,
            "intervention_volume_economy_weight": 0.15,
            "new_low_area_avoidance_weight": 0.15,
        },
        "BALANCED": {
            "low_area_drop_weight": 0.40,
            "avg_gain_weight": 0.35,
            "intervention_volume_economy_weight": 0.15,
            "new_low_area_avoidance_weight": 0.10,
        },
    }


def pair_key(value: object) -> str:
    """Canonicalize a two-building identifier for joins and reporting."""

    return ",".join(sorted(str(value).split(","), key=lambda item: int(item.strip()[1:])))


def rank_candidates(source: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    """Score and rank every candidate with deterministic tie breaking."""

    table = source[
        [
            "candidate_id",
            "building_ids",
            "low_area_drop_h3_m2_norm",
            "avg_gain_vs_baseline_h_norm",
            "intervention_volume_m3_norm",
            "new_low_area_h3_m2_norm",
            "is_pareto_front",
        ]
    ].copy()
    table["pair_key"] = table["building_ids"].map(pair_key)
    table["scenario_score"] = production_score(
        table["low_area_drop_h3_m2_norm"],
        table["avg_gain_vs_baseline_h_norm"],
        table["intervention_volume_m3_norm"],
        table["new_low_area_h3_m2_norm"],
        weights,
    )
    for key, value in weights.items():
        table[key] = value
    table = table.sort_values(["scenario_score", "candidate_id"], ascending=[False, True]).reset_index(drop=True)
    table["rank"] = np.arange(1, len(table) + 1)
    return table


def overlap_metrics(table: pd.DataFrame, base: pd.DataFrame) -> dict[str, float | int]:
    """Calculate rank agreement against the config-driven BASE ranking."""

    aligned = table[["candidate_id", "rank"]].merge(
        base[["candidate_id", "rank"]].rename(columns={"rank": "base_rank"}),
        on="candidate_id",
        how="inner",
    )
    result: dict[str, float | int] = {
        "spearman_with_base": float(aligned["rank"].corr(aligned["base_rank"], method="spearman")),
    }
    for k in (5, 10, 20):
        current = set(table.nsmallest(k, "rank")["candidate_id"])
        reference = set(base.nsmallest(k, "rank")["candidate_id"])
        result[f"top{k}_overlap"] = len(current & reference)
        result[f"top{k}_jaccard"] = len(current & reference) / len(current | reference)
    focus = table.set_index("pair_key")["rank"]
    for pair in FOCUS_PAIRS:
        result[f"rank_{pair.replace(',', '_')}"] = int(focus.get(pair, -1))
    return result


def main() -> None:
    runtime = load_runtime()
    source = pd.read_csv(runtime.results_dir / "120_canonical_2p5D完整双建筑候选排名.csv")
    results_dir = runtime.run_dir / "results"
    figures_dir = runtime.run_dir / "figures"
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    weights_by_name = scenario_weights(runtime)
    ranked: dict[str, pd.DataFrame] = {}
    rows: list[dict[str, object]] = []
    for name in SCENARIO_ORDER:
        table = rank_candidates(source, weights_by_name[name])
        table["scenario"] = name
        ranked[name] = table
        rows.extend(table.to_dict(orient="records"))

    base = ranked["BASE"]
    summary_rows: list[dict[str, object]] = []
    for name in SCENARIO_ORDER:
        row: dict[str, object] = {"scenario": name, **overlap_metrics(ranked[name], base)}
        row.update(weights_by_name[name])
        summary_rows.append(row)

    # Multiplicative perturbations are normalized back to a simplex, so every
    # draw remains a valid four-term score rather than an unscaled proxy.
    rng = np.random.default_rng(MONTE_CARLO_SEED)
    base_vector = np.array([weights_by_name["BASE"][key] for key in WEIGHT_KEYS])
    mc_rows: list[dict[str, object]] = []
    for draw in range(1000):
        perturbed = base_vector * rng.uniform(0.8, 1.2, size=4)
        perturbed = perturbed / perturbed.sum()
        draw_weights = dict(zip(WEIGHT_KEYS, perturbed))
        table = rank_candidates(source, draw_weights)
        for row in table.itertuples(index=False):
            mc_rows.append(
                {
                    "draw": draw,
                    "candidate_id": row.candidate_id,
                    "pair_key": row.pair_key,
                    "rank": int(row.rank),
                    "top10": int(row.rank <= 10),
                    **draw_weights,
                }
            )
    mc = pd.DataFrame(mc_rows)
    stability = (
        mc.groupby(["candidate_id", "pair_key"], as_index=False)
        .agg(
            rank_mean=("rank", "mean"),
            rank_median=("rank", "median"),
            rank_std=("rank", "std"),
            top10_selection_count=("top10", "sum"),
            top10_selection_frequency=("top10", "mean"),
        )
        .sort_values(["top10_selection_frequency", "rank_mean", "candidate_id"], ascending=[False, True, True])
    )

    pd.DataFrame(rows).to_csv(results_dir / "weight_sensitivity_v2.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(summary_rows).to_csv(results_dir / "weight_sensitivity_summary_v2.csv", index=False, encoding="utf-8-sig")
    stability.to_csv(results_dir / "candidate_rank_stability_v2.csv", index=False, encoding="utf-8-sig")

    top = stability.head(20).sort_values("top10_selection_frequency")
    fig, ax = plt.subplots(figsize=(8, 6), dpi=220)
    ax.barh(top["candidate_id"], top["top10_selection_frequency"], color="#2878b5")
    ax.set_xlabel("Top-10 selection frequency under +/-20% weight perturbation")
    ax.set_title("Four-term production-score ranking robustness")
    ax.set_xlim(0, 1)
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(figures_dir / "F08_weight_robustness_v2.png")
    plt.close(fig)

    write_run_metadata(
        runtime,
        stage="weight_sensitivity_v2",
        inputs=[runtime.results_dir / "120_canonical_2p5D完整双建筑候选排名.csv", runtime.config_path],
        extra={
            "scenario_count": len(SCENARIO_ORDER),
            "monte_carlo_draws": 1000,
            "monte_carlo_seed": MONTE_CARLO_SEED,
            "score_formula": "four_term_config_driven_v1",
        },
    )
    print(pd.DataFrame(summary_rows).to_string(index=False))


if __name__ == "__main__":
    main()
