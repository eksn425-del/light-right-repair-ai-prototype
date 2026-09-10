"""Pre-register and freeze an independent stratified HB validation sample."""

from __future__ import annotations

import argparse
import hashlib
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402


def key(value: str) -> str:
    return ",".join(sorted((part.strip() for part in str(value).split(",") if part.strip()), key=lambda x: int(x[1:])))


def choose_stratum(pool: pd.DataFrame, selected_ids: set[str], count: int, seed: int) -> pd.DataFrame:
    """Select candidates with deterministic volume spread and building diversity."""

    rng = np.random.default_rng(seed)
    pool = pool.copy()
    pool["volume_quantile"] = pool["intervention_volume_m3"].rank(pct=True, method="first")
    targets = np.linspace(0.2, 0.8, count)
    chosen: list[int] = []
    remaining = set(pool.index)
    local_ids = set(selected_ids)
    for target in targets:
        candidates = pool.loc[list(remaining)].copy()
        candidate_scores = []
        for idx, row in candidates.iterrows():
            ids = set(str(row["building_ids"]).split(","))
            new_ids = len(ids - local_ids)
            repeated = len(ids & local_ids)
            distance = abs(float(row["volume_quantile"]) - float(target))
            candidate_scores.append((new_ids, -repeated, -distance, float(rng.random()), idx))
        candidate_scores.sort(reverse=True)
        chosen_idx = candidate_scores[0][-1]
        chosen.append(chosen_idx)
        remaining.remove(chosen_idx)
        local_ids.update(str(pool.loc[chosen_idx, "building_ids"]).split(","))
    return pool.loc[chosen].copy()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--n", type=int, default=20)
    args = parser.parse_args()
    runtime = load_runtime(run_dir=args.run_dir)
    results = runtime.results_dir
    out_dir = runtime.run_dir / "independent_validation"
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = pd.read_csv(results / "120_canonical_2p5D完整双建筑候选排名.csv")
    candidates["pair_key"] = candidates["building_ids"].map(key)
    merged = pd.read_csv(results / "131_HB_Radiance合并候选汇总结果.csv") if (results / "131_HB_Radiance合并候选汇总结果.csv").exists() else pd.DataFrame()
    curated = set(merged.loc[merged.get("model_type", pd.Series(dtype=str)).astype(str).eq("rule_flat"), "pair_key"].dropna().map(key)) if not merged.empty else set()
    universe = candidates[~candidates["pair_key"].isin(curated)].copy()
    if len(universe) != 630 - len(curated):
        raise ValueError(f"Unexpected independent universe size: {len(universe)}")
    if args.n not in {12, 20}:
        raise ValueError("Only preregistered N=20 or fallback N=12 is allowed.")

    universe["stratum"] = pd.qcut(universe["score"].rank(method="first"), q=5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"])
    per_stratum = args.n // 5
    selected_parts = []
    selected_ids: set[str] = set()
    for offset, stratum in enumerate(["Q1", "Q2", "Q3", "Q4", "Q5"]):
        part = choose_stratum(universe[universe["stratum"].eq(stratum)], selected_ids, per_stratum, runtime.seed + offset)
        selected_parts.append(part)
        selected_ids.update(",".join(part["building_ids"]).split(","))
    sample = pd.concat(selected_parts, ignore_index=True)
    sample["sample_order"] = np.arange(1, len(sample) + 1)
    sample["selection_seed"] = runtime.seed
    sample = sample.sort_values(["stratum", "sample_order"]).reset_index(drop=True)
    sample.to_csv(out_dir / "VALIDATION_SAMPLE_FROZEN.csv", index=False, encoding="utf-8-sig")
    digest = hashlib.sha256((out_dir / "VALIDATION_SAMPLE_FROZEN.csv").read_bytes()).hexdigest()
    (out_dir / "VALIDATION_SAMPLE_FROZEN.sha256").write_text(digest + "\n", encoding="ascii")

    plan = [
        "# Independent HB validation sampling plan",
        "",
        "This sample was frozen before any independent-validation HB output was read.",
        "",
        f"- Seed: {runtime.seed}",
        f"- Requested sample size: {args.n}",
        f"- Candidate universe: {len(universe)} after excluding {len(curated)} historical rule pairs",
        "- Stratification: five 2.5D-score quintiles, equal allocation",
        "- Within-stratum tie breaking: deterministic intervention-volume spread and building-ID diversity",
        f"- Frozen CSV SHA256: {digest}",
        "",
        "The sample is a within-independent-sample validation set. It must not be described as global 630-candidate recall.",
        "",
        sample[["sample_order", "sample_id" if "sample_id" in sample.columns else "candidate_id", "pair_key", "stratum", "score", "intervention_volume_m3"]].to_markdown(index=False),
    ]
    (out_dir / "VALIDATION_SAMPLING_PLAN.md").write_text("\n".join(plan) + "\n", encoding="utf-8")
    write_run_metadata(
        runtime,
        stage="freeze_independent_sample",
        inputs=[results / "120_canonical_2p5D完整双建筑候选排名.csv", results / "131_HB_Radiance合并候选汇总结果.csv"],
        extra={"sample_size": len(sample), "curated_pair_count": len(curated), "sample_sha256": digest},
    )
    print(sample[["sample_order", "pair_key", "stratum", "score", "intervention_volume_m3"]].to_string(index=False))
    print(digest)


if __name__ == "__main__":
    main()
