"""Audit the config-driven scoring migration against the clean 630 baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_runtime import strict_bool  # noqa: E402


def pair_key(value: object) -> str:
    """Canonicalize an unordered two-building identifier."""

    return ",".join(sorted(str(value).split(","), key=lambda item: int(item.strip()[1:])))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--old", type=Path, default=None)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    new_path = run_dir / "results_csv" / "120_canonical_2p5D完整双建筑候选排名.csv"
    old_path = (args.old or (run_dir / "audit" / "SCORING_FORMULA_PRE_PATCH_120.csv")).resolve()
    if not old_path.exists() or not new_path.exists():
        raise FileNotFoundError(f"Both audit inputs are required: old={old_path}, new={new_path}")
    old = pd.read_csv(old_path)
    new = pd.read_csv(new_path)
    for frame in (old, new):
        frame["pair_key"] = frame["building_ids"].map(pair_key)
    if old["candidate_id"].duplicated().any() or new["candidate_id"].duplicated().any():
        raise AssertionError("Candidate IDs must be unique in both migration inputs")
    merged = old.merge(new, on="candidate_id", how="outer", suffixes=("_old", "_new"), indicator=True)
    if not (merged["_merge"] == "both").all():
        raise AssertionError("Candidate IDs changed during scoring migration")
    merged["pair_same"] = merged["pair_key_old"] == merged["pair_key_new"]
    merged["old_rank"] = pd.to_numeric(merged["rank_2p5d_score_old"], errors="raise")
    merged["new_rank"] = pd.to_numeric(merged["rank_2p5d_score_new"], errors="raise")
    merged["old_clean_score"] = pd.to_numeric(merged["score_old"], errors="raise")
    merged["config_driven_score"] = pd.to_numeric(merged["score_new"], errors="raise")
    merged["abs_diff"] = (merged["old_clean_score"] - merged["config_driven_score"]).abs()
    old_top10 = set(old.nsmallest(10, "rank_2p5d_score")["candidate_id"])
    new_top10 = set(new.nsmallest(10, "rank_2p5d_score")["candidate_id"])
    old_pareto = set(old.loc[old["is_pareto_front"].map(lambda value: strict_bool(value, field="old.is_pareto_front")), "candidate_id"])
    new_pareto = set(new.loc[new["is_pareto_front"].map(lambda value: strict_bool(value, field="new.is_pareto_front")), "candidate_id"])
    merged["rank_same"] = merged["old_rank"] == merged["new_rank"]
    merged["top10_same"] = merged["candidate_id"].isin(old_top10) == merged["candidate_id"].isin(new_top10)
    merged["pareto_same"] = merged["candidate_id"].isin(old_pareto) == merged["candidate_id"].isin(new_pareto)
    columns = [
        "candidate_id",
        "pair_key_old",
        "pair_key_new",
        "old_clean_score",
        "config_driven_score",
        "abs_diff",
        "old_rank",
        "new_rank",
        "rank_same",
        "top10_same",
        "pareto_same",
    ]
    out_dir = run_dir / "audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    audit = merged[columns].rename(columns={"pair_key_old": "pair_key"})
    audit.to_csv(out_dir / "SCORING_FORMULA_MIGRATION_AUDIT.csv", index=False, encoding="utf-8-sig")
    summary = {
        "old_file": str(old_path),
        "new_file": str(new_path),
        "candidate_count_old": len(old),
        "candidate_count_new": len(new),
        "pair_set_same": bool(merged["pair_same"].all()),
        "max_abs_score_diff": float(merged["abs_diff"].max()),
        "ranking_same": bool(merged["rank_same"].all()),
        "top10_same": old_top10 == new_top10,
        "pareto_same": old_pareto == new_pareto,
        "old_formula": "historical clean production score",
        "new_formula": "0.45 A_norm + 0.35 H_norm + 0.15 (1-V_norm) + 0.05 (1-N_norm), config-driven",
        "status": "PASS" if bool(merged["pair_same"].all() and merged["rank_same"].all() and old_top10 == new_top10 and old_pareto == new_pareto and merged["abs_diff"].max() < 1e-9) else "FAIL",
    }
    (out_dir / "SCORING_FORMULA_MIGRATION_AUDIT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
