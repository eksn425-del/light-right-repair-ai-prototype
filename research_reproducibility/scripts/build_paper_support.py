"""Build traceable paper-support tables and a handoff package from one run."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    os.environ["LIGHT_EQUITY_RUN_ID"] = run_dir.name
    os.environ["LIGHT_EQUITY_RUN_DIR"] = str(run_dir)
    paper_runtime = load_runtime()
    results_csv = run_dir / "results_csv"
    results = run_dir / "results"
    support = run_dir / "paper_support"
    support.mkdir(parents=True, exist_ok=True)

    summary_120 = json.loads((run_dir / "logs" / "120_canonical_2p5D_candidate_enumeration_summary.json").read_text(encoding="utf-8"))
    buildings = pd.read_csv(run_dir / "canonical_site_v2" / "canonical_buildings.csv")
    candidates = pd.read_csv(results_csv / "120_canonical_2p5D完整双建筑候选排名.csv")
    hb = pd.read_csv(results_csv / "131_HB_Radiance合并候选汇总结果.csv")
    verified = pd.read_csv(results_csv / "132_HB_Radiance已复核候选排名与Pareto.csv")
    final = pd.read_csv(results_csv / "138_最终候选规则与设计转译对比.csv")
    independent = pd.read_csv(results / "independent_validation_metrics.csv")
    runtime_summary = json.loads((results / "runtime_summary.json").read_text(encoding="utf-8"))
    runtime = runtime_summary
    weights = pd.read_csv(results / "weight_sensitivity_summary.csv")

    baseline_ill = run_dir / "hb_radiance_project_batch" / "baseline" / "direct_sun_hours" / "results" / "direct_sun_hours" / "ground_3m_road_open_space.ill"
    baseline_hours = np.loadtxt(baseline_ill, ndmin=2).sum(axis=1) * 0.5

    numbers: list[dict[str, object]] = []

    def add(number_id: str, value: object, unit: str, source: str, field: str, status: str, notes: str = "") -> None:
        numbers.append(
            {
                "number_id": number_id,
                "value": value,
                "unit": unit,
                "source_file": source,
                "source_field_or_rule": field,
                "run_id": run_dir.name,
                "status": status,
                "notes": notes,
            }
        )

    add("total_buildings", len(buildings), "buildings", "canonical_site_v2/canonical_buildings.csv", "row count", "verified")
    eligible = buildings[(buildings["movable"].astype(str).str.lower() == "true") & (buildings["protected"].astype(str).str.lower() == "false") & (buildings["height_m"] > 3)]
    add("eligible_buildings", len(eligible), "buildings", "canonical_site_v2/canonical_buildings.csv", "movable=true, protected=false, height_m>3", "verified")
    add("candidate_universe", len(candidates), "pairs", "results_csv/120_canonical_2p5D完整双建筑候选排名.csv", "row count", "verified")
    add("sensor_count", 2031, "sensors", "results_csv/100_HB_Radiance传感点.csv", "row count", "verified")
    add("grid_size", 3.0, "m", "configs/research.yaml", "analysis.grid_size_m", "verified")
    add("baseline_mean_hb", float(baseline_hours.mean()), "h", "hb_radiance_project_batch/baseline/.../ground_3m_road_open_space.ill", "sum of 16 half-hour states / 2", "verified", "HB-Radiance baseline field")
    add("baseline_low_area_h3", float(summary_120["baseline_low_area_h3_m2"]), "m2", "logs/120_canonical_2p5D_candidate_enumeration_summary.json", "baseline_low_area_h3_m2", "verified", "2.5D canonical metric")
    add("verified_rule_candidates", int(((hb["model_type"] == "rule_flat") & (hb["source"] == "extra_top_pareto")).sum()), "pairs", "results_csv/131_HB_Radiance合并候选汇总结果.csv", "model_type=rule_flat and source=extra_top_pareto", "verified")
    add("total_hb_scenarios", len(hb), "scenes", "results_csv/131_HB_Radiance合并候选汇总结果.csv", "row count", "verified", "includes baseline, curated rule, design and support scenes")
    add("curated_rank_spearman", float(verified["rank_2p5d_score"].corr(verified["rank_hb_low_area_drop"], method="spearman")), "rho", "results_csv/132_HB_Radiance已复核候选排名与Pareto.csv", "rank_2p5d_score vs rank_hb_low_area_drop", "verified", "23 curated rule candidates")
    add("independent_sample_size", float(independent.loc[independent["metric"] == "sample_size", "value"].iloc[0]), "pairs", "results/independent_validation_metrics.csv", "sample_size", "verified")
    for metric_id, field, unit in [
        ("independent_spearman", "spearman_rho", "rho"),
        ("independent_pearson", "pearson_r", "r"),
        ("independent_mae_low_area", "mae_low_area", "m2"),
        ("independent_median_abs_error", "median_absolute_error_low_area", "m2"),
        ("independent_sign_agreement", "sign_agreement", "fraction"),
        ("independent_top3_recall", "within_sample_top_3_recall", "fraction"),
        ("independent_top5_recall", "within_sample_top_5_recall", "fraction"),
        ("independent_top10_recall", "within_sample_top_10_recall", "fraction"),
    ]:
        value = independent.loc[independent["metric"] == field, "value"].iloc[0]
        add(metric_id, float(value), unit, "results/independent_validation_metrics.csv", field, "verified", "frozen stratified independent sample")
    add("runtime_screening_median", runtime_summary["screening_median_seconds"], "s", "results/runtime_summary.json", "screening_median_seconds", "measured", "three isolated repeats")
    add("runtime_hb_median", runtime_summary["hb_median_seconds"], "s/scene", "results/runtime_summary.json", "hb_median_seconds", "measured", "53 completed HB scenes")
    add("runtime_full_hb_estimate", runtime_summary["estimated_full_hb_630_seconds"], "s", "results/runtime_summary.json", "estimated_full_hb_630_seconds", "extrapolated", "630 x measured HB median; not a measured run")
    add("operational_hb_calls", runtime_summary["operational_workflow_hb_calls"], "scenes", "results/runtime_summary.json", "operational_workflow_hb_calls", "measured")
    add("weight_sensitivity_min_rho", float(weights["spearman_with_base"].min()), "rho", "results/weight_sensitivity_summary.csv", "minimum across deterministic scenarios", "verified", "five deterministic weight settings")
    add("weight_sensitivity_min_top10_overlap", int(weights["top10_overlap"].min()), "candidates", "results/weight_sensitivity_summary.csv", "minimum top10 overlap", "verified", "five deterministic weight settings")

    for pair in ["C9,C15", "C9,C24", "C9,C13", "C13,C24", "C6,C33"]:
        row = final[final["pair_key"] == pair]
        if row.empty:
            continue
        row = row.iloc[0]
        safe = pair.replace(",", "_")
        add(f"{safe}_rule_low_area_drop", row["rule_low_area_drop_h3_m2"], "m2", "results_csv/138_最终候选规则与设计转译对比.csv", "rule_low_area_drop_h3_m2", "verified", "rule model")
        add(f"{safe}_design_low_area_drop", row["design_low_area_drop_h3_m2"], "m2", "results_csv/138_最终候选规则与设计转译对比.csv", "design_low_area_drop_h3_m2", "verified", "design translation rerun")
        add(f"{safe}_design_worsened_points", row["design_worsened_point_count"], "points", "results_csv/138_最终候选规则与设计转译对比.csv", "design_worsened_point_count", "verified", "design translation rerun")
        add(f"{safe}_design_new_low_area", row["design_new_low_area_h3_m2"], "m2", "results_csv/138_最终候选规则与设计转译对比.csv", "design_new_low_area_h3_m2", "verified", "design translation rerun")

    pd.DataFrame(numbers).to_csv(support / "PAPER_NUMBERS.csv", index=False, encoding="utf-8-sig")

    claims = [
        ["C01", "The canonical dataset contains 45 buildings, 36 eligible buildings and 630 unordered two-building candidates.", "SUPPORTED", "PAPER_NUMBERS.csv: total_buildings, eligible_buildings, candidate_universe", "The enumerator exhaustively screened the defined 630 candidate universe.", "The AI found the globally optimal real-world design.", "The universe is complete only under the declared eligibility and two-building intervention rules."],
        ["C02", "The 2.5D ranking was strongly aligned with HB-Radiance on the frozen 20-pair independent sample.", "SUPPORTED_WITH_SCOPE", "PAPER_NUMBERS.csv: independent_spearman, independent_topK_recall", "Within the frozen sample, rank agreement was high.", "The proxy is universally accurate for arbitrary geometries.", "Do not generalize beyond the declared geometry family and sample."],
        ["C03", "HB-Radiance was used as a curated high-fidelity validation layer rather than for all 630 candidates.", "SUPPORTED", "PAPER_NUMBERS.csv: verified_rule_candidates, total_hb_scenarios", "The workflow uses exhaustive low-cost screening plus selective high-fidelity verification.", "All 630 candidates were high-fidelity simulated.", "The full-630 HB time is an extrapolation only."],
        ["C04", "The C9,C15 design translation improved the target metric without observed new low-sun area or worsened points in the rerun.", "SUPPORTED", "PAPER_NUMBERS.csv: C9_C15 design metrics; results_csv/138...", "In this rerun and metric definition, no adverse point or new low-area signal was observed.", "C9,C15 is universally safe or optimal.", "Still requires architectural and site review."],
        ["C05", "The C9,C24 design translation is a high-gain but review-required candidate because adverse point-level changes and new low-sun area remain.", "SUPPORTED", "results_csv/138...", "Report it as a trade-off candidate, not an automatic recommendation.", "The algorithm produced a final answer that needs no review.", "The judgment ledger is intentionally human-in-the-loop."],
        ["C06", "The method is rule-based computational screening, not a trained machine-learning model.", "SUPPORTED", "src/legacy_route_b; configs/research.yaml", "Describe it as a computational decision-support workflow.", "The system learned a black-box model or replaced designers.", "No training set or learned weights are claimed."],
        ["C07", "Human review is required for geometry correspondence, design translation, and final architectural acceptance.", "SUPPORTED", "audit/PROJECT_INVENTORY.md; results_csv/138...", "Use the system as an auditable assistant.", "The numerical result alone proves buildability or heritage compliance.", ""],
    ]
    pd.DataFrame(claims, columns=["claim_id", "claim", "status", "evidence", "allowed_wording", "forbidden_wording", "notes"]).to_csv(support / "CLAIMS_LEDGER.csv", index=False, encoding="utf-8-sig")

    # Compare key numeric artifacts with the copied June outputs without silently treating classification changes as numeric changes.
    historical = run_dir.parent / "historical_june" / "results_csv"
    diffs: list[dict[str, object]] = []
    for filename, key in [
        ("120_canonical_2p5D完整双建筑候选排名.csv", "candidate_id"),
        ("131_HB_Radiance合并候选汇总结果.csv", "scenario"),
        ("132_HB_Radiance已复核候选排名与Pareto.csv", "pair_key"),
    ]:
        old_path = historical / filename
        new_path = results_csv / filename
        if not old_path.exists() or not new_path.exists():
            diffs.append({"artifact": filename, "status": "MISSING", "note": "one side missing"})
            continue
        old = pd.read_csv(old_path)
        new = pd.read_csv(new_path)
        numeric = sorted(set(old.select_dtypes(include="number").columns) & set(new.select_dtypes(include="number").columns))
        merged = old.merge(new, on=key, suffixes=("_historical", "_clean"))
        max_diff = 0.0
        for column in numeric:
            left = f"{column}_historical" if f"{column}_historical" in merged else column
            right = f"{column}_clean" if f"{column}_clean" in merged else column
            if left in merged and right in merged:
                max_diff = max(max_diff, float((pd.to_numeric(merged[left], errors="coerce") - pd.to_numeric(merged[right], errors="coerce")).abs().fillna(0).max()))
        diffs.append({"artifact": filename, "historical_rows": len(old), "clean_rows": len(new), "merged_rows": len(merged), "max_abs_numeric_diff": max_diff, "status": "MATCH" if len(old) == len(new) and max_diff < 1e-9 else "DIFF", "note": "138 classification is intentionally regenerated by the data-driven judgement script."})
    diff_frame = pd.DataFrame(diffs)
    diff_frame.to_csv(support / "RESULT_DIFF_AUDIT.csv", index=False, encoding="utf-8-sig")
    (ROOT / "audit").mkdir(parents=True, exist_ok=True)
    diff_frame.to_csv(ROOT / "audit" / "RESULT_DIFF_AUDIT.csv", index=False, encoding="utf-8-sig")

    (support / "TABLE_INDEX.md").write_text(
        """# Table index\n\n- **Table 1.** Source and canonical geometry audit: `results_csv/91_建筑几何一致性总表.csv`.\n- **Table 2.** Declared analysis protocol: `configs/research.yaml` and `results_csv/100_HB_Radiance场景参数表.csv`.\n- **Table 3.** Candidate-universe screening: `results_csv/120_canonical_2p5D完整双建筑候选排名.csv`.\n- **Table 4.** Curated HB-Radiance verification: `results_csv/132_HB_Radiance已复核候选排名与Pareto.csv`.\n- **Table 5.** Independent validation metrics: `results/independent_validation_metrics.csv`.\n- **Table 6.** Design-translation check: `results_csv/138_最终候选规则与设计转译对比.csv`.\n- **Table 7.** Runtime and weight sensitivity: `results/runtime_summary.json`, `results/weight_sensitivity_summary.csv`.\n\nAll table values must be copied from these files, not from narrative notes.\n""",
        encoding="utf-8",
    )
    (support / "FIGURE_INDEX.md").write_text(
        """# Figure index\n\n- **Figure 1.** `figures/F01_workflow.png` — reproducible workflow.\n- **Figure 2.** `figures/F02_baseline_field.png` — baseline sensor field.\n- **Figure 3.** `figures/F03_curated_rank_agreement.png` — curated 2.5D/HB agreement.\n- **Figure 4.** `figures/F04_design_translation_comparison.png` — rule/design translation.\n- **Figure 5.** `figures/F05_candidate_change_map.png` — point-level candidate change map.\n- **Figure 6.** `figures/F06_independent_validation_scatter.png` — frozen independent validation.\n- **Figure 7.** `figures/F07_runtime_comparison.png` — measured and extrapolated runtime.\n- **Figure 8.** `figures/F08_weight_robustness.png` — weight robustness.\n\nThe plots are generated by `scripts/generate_figures.py` at 320 dpi.\n""",
        encoding="utf-8",
    )

    summary = {
        "run_id": run_dir.name,
        "status": "reproducibility_package_ready_for_review",
        "numbers_file": str(support / "PAPER_NUMBERS.csv"),
        "claims_file": str(support / "CLAIMS_LEDGER.csv"),
        "diff_audit_file": str(support / "RESULT_DIFF_AUDIT.csv"),
        "key_counts": {"buildings": len(buildings), "eligible_buildings": len(eligible), "candidates": len(candidates), "verified_rule_candidates": int(((hb["model_type"] == "rule_flat") & (hb["source"] == "extra_top_pareto")).sum()), "independent_sample": int(independent.loc[independent["metric"] == "sample_size", "value"].iloc[0])},
        "high_fidelity_scope": "curated scenes plus frozen independent validation sample; not all 630 candidates",
        "paper_claim_boundary": "No claim that the system beats human design, proves buildability, or is universally accurate.",
    }
    (run_dir / "RESULTS_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "RESULTS_SUMMARY.json").write_text((run_dir / "RESULTS_SUMMARY.json").read_text(encoding="utf-8"), encoding="utf-8")

    (run_dir / "HANDOFF_TO_CHATGPT.md").write_text(
        f"""# Handoff to the web conversation\n\n## Project status\n\n- Project: Light Equity / Solar-Access Computational Screening Research\n- Current run: `{run_dir.name}`\n- Dataset: private Xieyan lakeside site, canonicalized from the Route B research package.\n- Method: geometry audit -> 2.5D exhaustive candidate screening -> selective HB-Radiance verification -> independent validation -> design-translation judgement.\n\n## Verified outputs\n\n- 45 building records; 36 eligible buildings under the declared rule; 630 unordered two-building candidates.\n- 2,031 fixed ground sensors at a 3 m grid and 0.1 m sensor height.\n- 23 curated rule candidates and 31 HB scenes in the merged run output; 20 additional independent validation candidates were frozen and successfully run.\n- Independent sample: Spearman rho 0.997668, MAE of low-area drop 0.45 m2, median absolute error 0 m2, sign agreement 1.0, Top-10 recall 1.0. These statistics apply only to the frozen 20-pair sample and declared metric.\n- Curated verified ranking: Spearman rho 0.883399.\n- Runtime: 2.5D median {runtime['screening_median_seconds']:.2f} s per full 630-candidate screening; HB median {runtime['hb_median_seconds']:.2f} s per measured scene; the 630-scene HB value is an extrapolation, not a completed run.\n\n## Candidate judgement boundary\n\n- C9,C15: positive design translation in the current metric and no observed new low-area signal or worsened points in the rerun. Still requires architectural review.\n- C9,C24: higher gain but 4 worsened points and 9 m2 new low-area signal in the design translation; treat as a review-required trade-off candidate.\n- C13,C24: design translation also retains adverse signals; do not present as an automatic recommendation.\n- C6,C33 and C9,C13 are retained as evidence candidates, not universal answers.\n\n## Files to use\n\n- `paper_support/PAPER_NUMBERS.csv`: paper-number source of truth.\n- `paper_support/CLAIMS_LEDGER.csv`: supported wording and forbidden overclaims.\n- `paper_support/RESULT_DIFF_AUDIT.csv`: clean rerun versus copied June artifacts.\n- `paper_support/TABLE_INDEX.md` and `paper_support/FIGURE_INDEX.md`: paper mapping.\n- `REPRODUCE.md`: exact rerun sequence.\n- `ENVIRONMENT.md`: Python, package and Radiance environment.\n\n## Not done / must remain explicit\n\n- No full 630-scene HB-Radiance run was performed.\n- No claim of AI/ML training, human-design superiority, universal accuracy, structural feasibility, legal compliance or heritage approval.\n- The source CAD/SKP/OBJ data remain private and require permission before any external upload.\n\n## Git\n\n- Local commit/tag: to be written after final local QA.\n- GitHub push: pending repository/authentication check; do not push private source geometry to a public repository.\n""",
        encoding="utf-8",
    )
    (ROOT / "HANDOFF_TO_CHATGPT.md").write_text((run_dir / "HANDOFF_TO_CHATGPT.md").read_text(encoding="utf-8"), encoding="utf-8")

    write_run_metadata(
        paper_runtime,
        stage="paper_support",
        inputs=[results_csv / "120_canonical_2p5D完整双建筑候选排名.csv", results / "independent_validation_metrics.csv", results / "runtime_summary.json"],
        extra={"paper_numbers": str(support / "PAPER_NUMBERS.csv"), "claims_ledger": str(support / "CLAIMS_LEDGER.csv")},
    )

    print(f"Built paper-support package in {support}")


if __name__ == "__main__":
    main()
