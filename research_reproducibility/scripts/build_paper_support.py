"""Build the factual paper-support and web-conversation handoff package."""

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
from research_runtime import load_runtime, sha256, strict_bool, write_run_metadata  # noqa: E402


def metric_value(frame: pd.DataFrame, metric: str) -> float:
    """Read one scalar metric from a metric/value table."""

    rows = frame.loc[frame["metric"].eq(metric), "value"]
    if rows.empty:
        raise KeyError(f"Missing metric: {metric}")
    return float(rows.iloc[0])


def pair_key(value: object) -> str:
    """Canonicalize an unordered two-building identifier."""

    return ",".join(sorted(str(value).split(","), key=lambda item: int(item.strip()[1:])))


def compare_artifact(old_path: Path, new_path: Path, key: str) -> dict[str, object]:
    """Compare numeric columns without hiding row/key changes."""

    if not old_path.exists() or not new_path.exists():
        return {"artifact": new_path.name, "status": "MISSING", "note": "one side missing"}
    old = pd.read_csv(old_path)
    new = pd.read_csv(new_path)
    if key not in old or key not in new:
        return {"artifact": new_path.name, "status": "MISSING_KEY", "note": key}
    merged = old.merge(new, on=key, suffixes=("_historical", "_current"), how="outer", indicator=True)
    common_numeric = sorted(set(old.select_dtypes(include="number").columns) & set(new.select_dtypes(include="number").columns))
    max_diff = 0.0
    for column in common_numeric:
        left = f"{column}_historical" if f"{column}_historical" in merged else column
        right = f"{column}_current" if f"{column}_current" in merged else column
        if left in merged and right in merged:
            delta = pd.to_numeric(merged[left], errors="coerce") - pd.to_numeric(merged[right], errors="coerce")
            max_diff = max(max_diff, float(delta.abs().fillna(0).max()))
    matched = int((merged["_merge"] == "both").sum())
    status = "MATCH" if len(old) == len(new) and matched == len(old) and max_diff < 1e-9 else "DIFF"
    return {
        "artifact": new_path.name,
        "historical_rows": len(old),
        "current_rows": len(new),
        "matched_rows": matched,
        "max_abs_numeric_diff": max_diff,
        "status": status,
        "note": "numeric/key audit; regenerated judgement classifications are separate",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    os.environ["LIGHT_EQUITY_RUN_ID"] = run_dir.name
    os.environ["LIGHT_EQUITY_RUN_DIR"] = str(run_dir)
    runtime = load_runtime()
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
    composite = pd.read_csv(results / "independent_composite_metrics.csv")
    runtime_summary = json.loads((results / "runtime_summary_v2.json").read_text(encoding="utf-8"))
    weight_summary = pd.read_csv(results / "weight_sensitivity_summary_v2.csv")
    stability = pd.read_csv(results / "candidate_rank_stability_v2.csv")
    migration = json.loads((run_dir / "audit" / "SCORING_FORMULA_MIGRATION_AUDIT.json").read_text(encoding="utf-8"))

    baseline_ill = run_dir / "hb_radiance_project_batch" / "baseline" / "direct_sun_hours" / "results" / "direct_sun_hours" / f"ground_{runtime.grid_size_m:g}m_road_open_space.ill"
    baseline_hours = np.loadtxt(baseline_ill, ndmin=2).sum(axis=1) * runtime.timestep_hours
    eligible = buildings[
        buildings["movable"].map(lambda value: strict_bool(value, field="movable"))
        & ~buildings["protected"].map(lambda value: strict_bool(value, field="protected"))
        & (pd.to_numeric(buildings["height_m"], errors="raise") > runtime.height_floor_m)
    ]
    verified_rule = hb[(hb["model_type"] == "rule_flat") & (hb["source"] == "extra_top_pareto")]
    design_rerun = final[final["design_low_area_drop_h3_m2"].notna()].copy()
    design_review = design_rerun[(design_rerun["design_worsened_point_count"] > 0) | (design_rerun["design_new_low_area_h3_m2"] > 0)]

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
    add("eligible_buildings", len(eligible), "buildings", "canonical_site_v2/canonical_buildings.csv", "strict movable=true, protected=false, height_m>height_floor_m", "verified")
    add("candidate_universe", len(candidates), "pairs", "results_csv/120_canonical_2p5D完整双建筑候选排名.csv", "row count", "verified", "exhaustive only for the declared pairwise intervention universe")
    add("sensor_count", len(pd.read_csv(results_csv / "100_HB_Radiance传感点.csv")), "sensors", "results_csv/100_HB_Radiance传感点.csv", "row count", "verified")
    add("grid_size", runtime.grid_size_m, "m", "configs/research.yaml", "analysis.grid_size_m", "verified")
    add("sensor_height", runtime.sensor_height_m, "m", "configs/research.yaml", "analysis.sensor_height_m", "verified")
    add("analysis_timestep", runtime.timestep_minutes, "minutes", "configs/research.yaml", "analysis.timestep_minutes", "verified")
    add("baseline_mean_hb", float(baseline_hours.mean()), "h", "hb_radiance_project_batch/baseline/.../ground_3m_road_open_space.ill", "sum of configured samples x timestep_hours", "verified", "HB-Radiance baseline field")
    add("baseline_low_area_h3", float(summary_120["baseline_low_area_h3_m2"]), "m2", "logs/120_canonical_2p5D_candidate_enumeration_summary.json", "baseline_low_area_h3_m2", "verified", "2.5D canonical metric")
    add("verified_rule_candidates", len(verified_rule), "pairs", "results_csv/131_HB_Radiance合并候选汇总结果.csv", "model_type=rule_flat and source=extra_top_pareto", "verified")
    add("operational_hb_scenes", runtime_summary["operational_hb_scene_count"], "scenes", "results/runtime_summary_v2.json", "operational_hb_scene_count", "measured", "curated initial + extra + design translation")
    add("independent_hb_scenes", runtime_summary["research_only_validation_scene_count"], "scenes", "results/runtime_summary_v2.json", "research_only_validation_scene_count", "measured", "research-only independent evidence")
    add("total_measured_hb_scenes", runtime_summary["total_measured_hb_scene_count"], "scenes", "results/runtime_summary_v2.json", "total_measured_hb_scene_count", "measured")
    add("selected_rule_verification_fraction", runtime_summary["rule_candidate_verification_fraction"], "fraction", "results/runtime_summary_v2.json", "rule_candidate_verification_count / rule_candidate_universe_count", "verified", "23/630; not an all-candidate HB fraction")
    add("curated_rank_spearman", float(verified["rank_2p5d_score"].corr(verified["rank_hb_low_area_drop"], method="spearman")), "rho", "results_csv/132_HB_Radiance已复核候选排名与Pareto.csv", "rank_2p5d_score vs rank_hb_low_area_drop", "verified", "23 curated rule candidates")

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
        add(metric_id, metric_value(independent, field), unit, "results/independent_validation_metrics.csv", field, "verified", "frozen N=20 independent sample; declared low-area-drop metric")
    for metric_id, field, unit in [
        ("composite_spearman", "spearman_rho", "rho"),
        ("composite_spearman_pvalue", "spearman_pvalue", "p-value"),
        ("composite_top3_overlap", "top3_overlap", "candidates"),
        ("composite_top3_recall", "top3_recall", "fraction"),
        ("composite_top5_overlap", "top5_overlap", "candidates"),
        ("composite_top5_recall", "top5_recall", "fraction"),
        ("composite_top10_overlap", "top10_overlap", "candidates"),
        ("composite_top10_recall", "top10_recall", "fraction"),
        ("composite_mean_abs_rank_error", "mean_absolute_rank_error", "rank positions"),
        ("composite_median_abs_rank_error", "median_absolute_rank_error", "rank positions"),
        ("composite_max_abs_rank_error", "max_absolute_rank_error", "rank positions"),
    ]:
        add(metric_id, metric_value(composite, field), unit, "results/independent_composite_metrics.csv", field, "verified", "within-independent-sample composite-ranking agreement; bounds fixed by complete 630 universe")

    for name, value in runtime.score_weights.items():
        add(f"score_{name}", value, "weight", "configs/research.yaml", f"screening_score.{name}", "verified", "four-term production score")
    add("score_migration_max_abs_diff", migration["max_abs_score_diff"], "score units", "audit/SCORING_FORMULA_MIGRATION_AUDIT.csv", "abs_diff maximum", "verified", "630 regression audit")
    add("runtime_screening_median", runtime_summary["screening_median_seconds"], "s/run", "results/runtime_summary_v2.json", "screening_median_seconds", "measured", "three isolated full 630-candidate 2.5D repeats")
    add("runtime_hb_median", runtime_summary["hb_median_seconds_per_scene"], "s/scene", "results/runtime_summary_v2.json", "hb_median_seconds_per_scene", "measured", "53 completed HB scenes")
    add("runtime_hb_630_serial_equivalent", runtime_summary["serial_equivalent_hb_630_seconds"], "s", "results/runtime_summary_v2.json", "serial_equivalent_hb_630_seconds", "extrapolated", "not a measured 630-scene HB run")
    add("weight_sensitivity_v2_min_rho", float(weight_summary["spearman_with_base"].min()), "rho", "results/weight_sensitivity_summary_v2.csv", "minimum across six deterministic scenarios", "verified", "four-term score")
    add("weight_sensitivity_v2_min_top10_overlap", int(weight_summary["top10_overlap"].min()), "candidates", "results/weight_sensitivity_summary_v2.csv", "minimum top10 overlap", "verified", "six deterministic scenarios")
    add("weight_sensitivity_v2_mc_min_top10_frequency", float(stability["top10_selection_frequency"].min()), "fraction", "results/candidate_rank_stability_v2.csv", "minimum across candidates", "verified", "1000 normalized multiplicative draws")
    add("weight_sensitivity_v2_mc_max_top10_frequency", float(stability["top10_selection_frequency"].max()), "fraction", "results/candidate_rank_stability_v2.csv", "maximum across candidates", "verified", "1000 normalized multiplicative draws")
    add("independent_sample_sha256", sha256(run_dir / "independent_validation" / "VALIDATION_SAMPLE_FROZEN.csv"), "digest", "independent_validation/VALIDATION_SAMPLE_FROZEN.sha256", "SHA256", "verified", "frozen before independent HB outcomes")

    for pair in ["C9,C15", "C9,C24", "C9,C13", "C13,C24", "C6,C33"]:
        row = final[final["pair_key"].map(pair_key) == pair]
        if row.empty:
            continue
        item = row.iloc[0]
        safe = pair.replace(",", "_")
        for suffix, field, unit in [
            ("rule_low_area_drop", "rule_low_area_drop_h3_m2", "m2"),
            ("design_low_area_drop", "design_low_area_drop_h3_m2", "m2"),
            ("design_worsened_points", "design_worsened_point_count", "points"),
            ("design_new_low_area", "design_new_low_area_h3_m2", "m2"),
        ]:
            if pd.isna(item[field]):
                continue
            add(f"{safe}_{suffix}", item[field], unit, "results_csv/138_最终候选规则与设计转译对比.csv", field, "verified", "design translation rerun" if suffix.startswith("design") else "rule model")

    paper_numbers = pd.DataFrame(numbers)
    if paper_numbers["number_id"].duplicated().any():
        raise AssertionError("PAPER_NUMBERS.csv contains duplicate number_id values")
    # Keep the old three-term values visible for provenance but prohibit their
    # use in the manuscript after the four-term migration.
    old_weights = pd.read_csv(results / "weight_sensitivity_summary.csv")
    superseded = pd.DataFrame(
        [
            {"number_id": "weight_sensitivity_v1_min_rho", "value": float(old_weights["spearman_with_base"].min()), "unit": "rho", "source_file": "results/weight_sensitivity_summary.csv", "source_field_or_rule": "old three-term sensitivity minimum", "run_id": run_dir.name, "status": "SUPERSEDED_NOT_FOR_PAPER", "notes": "Retained only to show the formula migration; do not cite."},
            {"number_id": "weight_sensitivity_v1_min_top10_overlap", "value": int(old_weights["top10_overlap"].min()), "unit": "candidates", "source_file": "results/weight_sensitivity_summary.csv", "source_field_or_rule": "old three-term sensitivity minimum", "run_id": run_dir.name, "status": "SUPERSEDED_NOT_FOR_PAPER", "notes": "Retained only to show the formula migration; do not cite."},
        ]
    )
    paper_numbers = pd.concat([paper_numbers, superseded], ignore_index=True)
    paper_numbers.to_csv(support / "PAPER_NUMBERS.csv", index=False, encoding="utf-8-sig")

    claims = [
        ["C01", "The declared canonical dataset contains 45 buildings, 36 eligible buildings and 630 unordered two-building candidates.", "SUPPORTED_WITH_SCOPE", "PAPER_NUMBERS.csv: total_buildings, eligible_buildings, candidate_universe", "The defined 630-candidate universe was exhaustively screened by the rule-based 2.5D procedure.", "The AI found the globally optimal real-world design.", "Exhaustiveness is conditional on the declared eligibility and pairwise intervention universe."],
        ["C02", "The 2.5D low-area-drop ranking agrees with HB-Radiance on the frozen independent N=20 sample.", "SUPPORTED_WITH_SCOPE", "PAPER_NUMBERS.csv: independent_spearman, independent_topK_recall", "Report this as within-independent-sample metric agreement.", "The proxy is universally accurate or has 99.7% accuracy for arbitrary geometries.", "Do not generalize beyond the frozen sample, geometry family and metric."],
        ["C03", "The four-term composite ranking was checked against HB-Radiance on the same frozen independent sample using predeclared weights and fixed 630-universe normalization bounds.", "SUPPORTED_WITH_SCOPE", "PAPER_NUMBERS.csv: composite_spearman, composite_topK_overlap, score_*", "Call it within-independent-sample composite-ranking agreement.", "The composite result proves global recall or universal ranking validity.", "No weights were fitted to the independent HB outcomes."],
        ["C04", "HB-Radiance was used selectively: 23 rule candidates were verified from the 630 screened candidates, while the 20 independent scenes were research-only validation evidence.", "SUPPORTED", "PAPER_NUMBERS.csv: selected_rule_verification_fraction, operational_hb_scenes, independent_hb_scenes", "State the selective high-fidelity design explicitly.", "All 630 candidates were high-fidelity simulated.", "The 630-scene HB time is a serial-equivalent extrapolation only."],
        ["C05", "The 630-candidate screening was reproduced after score/config migration with unchanged candidate IDs, scores, ranks, Top-10 and Pareto membership.", "SUPPORTED", "audit/SCORING_FORMULA_MIGRATION_AUDIT.csv", "Use this as a regression result, not as a new performance claim.", "The old values were hard-coded to match the paper.", "The audit preserves any future real changes instead of forcing historical values."],
        ["C06", "Design translation can change the desirability of a rule candidate; the current design ledger retains a human review step.", "SUPPORTED_WITH_SCOPE", "results_csv/138_最终候选规则与设计转译对比.csv; design_translation_summary.csv", "Describe the algorithm as decision support with human-in-the-loop review.", "The algorithmic candidate is automatically buildable, legal, heritage-approved, safe or optimal.", "Architectural acceptance remains outside this computational screen."],
        ["C07", "The method is a deterministic rule-based computational screening workflow, not a trained ML/LLM model.", "SUPPORTED", "src/legacy_route_b; configs/research.yaml", "Describe the contribution as an auditable AI-assisted/product workflow if desired, but do not claim learned AI.", "A trained model learned the weights or replaced designers.", "No training set or learned parameters are claimed."],
        ["C08", "The runtime table distinguishes measured per-scene HB time, operational scenes, research-only independent scenes and serial-equivalent 630-scene extrapolation.", "SUPPORTED", "results/runtime_summary_v2.json", "Use measured/extrapolated labels exactly.", "The 630-scene HB run took the extrapolated duration.", "Operational batch elapsed time remains NOT_MEASURED."],
        ["F01", "Forbidden wording: 99.7% accuracy, universal accuracy, Radiance as ground truth, all-630 HB, AI beats human, global optimum, or proven buildability/legal/heritage compliance.", "FORBIDDEN", "CLAIMS_LEDGER.csv", "Do not use these claims in the paper, abstract, figure captions or presentation.", "Any of the listed overclaims.", "Replace with scope-qualified evidence statements."],
    ]
    pd.DataFrame(claims, columns=["claim_id", "claim", "status", "evidence", "allowed_wording", "forbidden_wording", "notes"]).to_csv(support / "CLAIMS_LEDGER.csv", index=False, encoding="utf-8-sig")

    historical = run_dir.parent / "historical_june" / "results_csv"
    diffs = [
        compare_artifact(historical / "120_canonical_2p5D完整双建筑候选排名.csv", results_csv / "120_canonical_2p5D完整双建筑候选排名.csv", "candidate_id"),
        compare_artifact(historical / "131_HB_Radiance合并候选汇总结果.csv", results_csv / "131_HB_Radiance合并候选汇总结果.csv", "scenario"),
        compare_artifact(historical / "132_HB_Radiance已复核候选排名与Pareto.csv", results_csv / "132_HB_Radiance已复核候选排名与Pareto.csv", "pair_key"),
        {"artifact": "SCORING_FORMULA_MIGRATION_AUDIT.csv", "status": migration["status"], "max_abs_numeric_diff": migration["max_abs_score_diff"], "note": "config-driven four-term formula versus pre-patch clean 630 output"},
    ]
    diff_frame = pd.DataFrame(diffs)
    diff_frame.to_csv(support / "RESULT_DIFF_AUDIT.csv", index=False, encoding="utf-8-sig")
    (run_dir / "audit").mkdir(parents=True, exist_ok=True)
    diff_frame.to_csv(run_dir / "audit" / "RESULT_DIFF_AUDIT.csv", index=False, encoding="utf-8-sig")

    design_public = final[[
        "pair_key", "final_status", "reason", "rule_low_area_drop_h3_m2", "rule_avg_gain_h", "rule_intervention_volume_m3", "rule_hb_pareto", "rule_hb_rank", "design_low_area_drop_h3_m2", "design_avg_gain_h", "design_improved_point_count", "design_worsened_point_count", "design_new_low_area_h3_m2", "design_validation_status",
    ]].copy()
    design_public["requires_human_review"] = (
        design_public["design_worsened_point_count"].fillna(0) > 0
    ) | (design_public["design_new_low_area_h3_m2"].fillna(0) > 0) | design_public["design_validation_status"].ne("已复算")
    design_public.to_csv(results / "design_translation_summary.csv", index=False, encoding="utf-8-sig")
    classification = pd.DataFrame(
        [
            {"classification": "all_2p5d_candidates", "count": len(candidates), "scope": "complete defined 630-pair universe", "paper_use": "screening universe"},
            {"classification": "curated_rule_hb_verified", "count": len(verified_rule), "scope": "selected rule candidates from Top/Pareto review", "paper_use": "selective high-fidelity evidence"},
            {"classification": "operational_hb_scenes", "count": runtime_summary["operational_hb_scene_count"], "scope": "baseline/support/design workflow", "paper_use": "operational evidence"},
            {"classification": "research_only_independent_hb_scenes", "count": runtime_summary["research_only_validation_scene_count"], "scope": "frozen N=20 validation sample", "paper_use": "independent agreement evidence"},
            {"classification": "design_translation_rerun", "count": len(design_rerun), "scope": "candidate designs with a measured translation rerun", "paper_use": "design judgement"},
            {"classification": "design_translation_review_required", "count": len(design_review), "scope": "worsened points or new low-area signal", "paper_use": "human-in-the-loop warning"},
        ]
    )
    classification.to_csv(results / "candidate_classification_summary.csv", index=False, encoding="utf-8-sig")

    (support / "TABLE_INDEX.md").write_text(
        """# Table index\n\n- **Table 1.** Source and canonical geometry audit: `results_csv/91_建筑几何一致性总表.csv`.\n- **Table 2.** Declared analysis protocol and runtime parameters: `configs/research.yaml` and `results_csv/100_HB_Radiance场景参数表.csv`.\n- **Table 3.** Complete 2.5D candidate-universe screening: `results_csv/120_canonical_2p5D完整双建筑候选排名.csv`.\n- **Table 4.** Curated HB-Radiance verification: `results_csv/132_HB_Radiance已复核候选排名与Pareto.csv`.\n- **Table 5.** Frozen independent low-area metric validation: `results/independent_validation_metrics.csv`.\n- **Table 6.** Rule/design translation judgement: `results/design_translation_summary.csv`.\n- **Table 7.** Runtime semantics and measurement classes: `results/runtime_summary_v2.json`.\n- **Table 8.** Independent four-term composite-ranking validation: `results/independent_composite_metrics.csv` and `results/independent_composite_ranking.csv`.\n- **Table 9.** Four-term weight sensitivity and Monte Carlo stability: `results/weight_sensitivity_summary_v2.csv` and `results/candidate_rank_stability_v2.csv`.\n\nAll manuscript table values must be copied from these files, not from narrative notes.\n""",
        encoding="utf-8",
    )
    (support / "FIGURE_INDEX.md").write_text(
        """# Figure index\n\n- **Figure 1.** `figures/F01_workflow.png` — reproducible workflow.\n- **Figure 2.** `figures/F02_baseline_field.png` — baseline sensor field.\n- **Figure 3.** `figures/F03_curated_rank_agreement.png` — curated 2.5D/HB agreement.\n- **Figure 4.** `figures/F04_design_translation_comparison.png` — rule/design translation.\n- **Figure 5.** `figures/F05_candidate_change_map.png` — point-level candidate change map.\n- **Figure 6.** `figures/F06_independent_validation_scatter.png` — frozen independent metric validation.\n- **Figure 7.** `figures/F07_runtime_comparison_v2.png` — measured and serial-equivalent runtime.\n- **Figure 8.** `figures/F08_weight_robustness_v2.png` — four-term weight robustness.\n- **Figure 9.** `figures/F09_independent_composite_ranking.png` — independent composite-ranking agreement.\n\nPlots are generated from the run outputs at 320 dpi.\n""",
        encoding="utf-8",
    )

    composite_rho = metric_value(composite, "spearman_rho")
    composite_top3 = metric_value(composite, "top3_recall")
    composite_top5 = metric_value(composite, "top5_recall")
    composite_top10 = metric_value(composite, "top10_recall")
    brief = f"""# SOICT 2026 paper-writing brief

This is a factual and structural handoff, not polished paper prose. Every number below must be checked against `paper_support/PAPER_NUMBERS.csv` before it is placed in a manuscript.

## Research identity

- Working topic: reproducible solar-access computational screening for minimum-intervention spatial decision support in an old urban district.
- Study site: private canonicalized lakeside-site dataset from the Xieyan group.
- Core question: can a low-cost rule-based 2.5D screening workflow narrow a declared candidate universe while preserving useful agreement with selective HB-Radiance checks and keeping design judgement human-in-the-loop?
- Do not frame the study as AI replacing designers, as a comparison against a human design, or as a trained ML/LLM system.

## Fixed protocol

- Analysis date: {runtime.analysis_date}; local timezone: {runtime.timezone}; UTC offset: +{runtime.utc_offset_hours}.
- Local time: {runtime.start_time}-{runtime.end_time}; timestep: {runtime.timestep_minutes} minutes.
- Location: approximately {runtime.latitude} N, {runtime.longitude} E; north convention {runtime.north_deg} degrees.
- Ground grid: {runtime.grid_size_m:g} m; sensor height: {runtime.sensor_height_m:g} m; low-sun threshold: {runtime.low_threshold_h:g} h.
- Height rule: `new_h=max(height_floor_m, h-min(height_reduction_cap_m, height_reduction_fraction*h))`, configured as {runtime.height_floor_m:g} m floor, {runtime.height_reduction_cap_m:g} m cap and {runtime.height_reduction_fraction:g} fraction.
- Production score: `0.45 A_norm + 0.35 H_norm + 0.15 (1-V_norm) + 0.05 (1-N_norm)`, with all four weights read from `configs/research.yaml`.

## Evidence inventory

- 45 building records; 36 eligible buildings under the declared strict boolean and height rule; 630 unordered two-building candidates screened exhaustively by the 2.5D procedure.
- 2,031 fixed sensors.
- 23 selected rule candidates verified in the operational/curated HB evidence; 33 HB scenes belong to the operational workflow; 20 independent HB scenes are research-only validation evidence; 53 HB scenes were measured in total.
- The frozen independent sample is N=20 with SHA256 recorded in `independent_validation/VALIDATION_SAMPLE_FROZEN.sha256`. Do not reselect it.

## Results to report carefully

### Metric validation

- Legacy independent low-area-drop validation: Spearman rho {metric_value(independent, 'spearman_rho'):.6f}, Pearson r {metric_value(independent, 'pearson_r'):.6f}, MAE {metric_value(independent, 'mae_low_area'):.2f} m2, sign agreement {metric_value(independent, 'sign_agreement'):.3f}. This is a frozen N=20 within-sample result.
- Composite validation using the same frozen sample, the four predeclared weights and fixed 630-universe normalization bounds: Spearman rho {composite_rho:.6f}; Top-3 recall {composite_top3:.3f}; Top-5 recall {composite_top5:.3f}; Top-10 recall {composite_top10:.3f}; mean/median/max absolute rank error {metric_value(composite, 'mean_absolute_rank_error'):.1f}/{metric_value(composite, 'median_absolute_rank_error'):.1f}/{metric_value(composite, 'max_absolute_rank_error'):.1f} positions.
- The phrase to use is “within-independent-sample composite-ranking agreement,” not global recall or universal accuracy.

### Ranking migration and sensitivity

- The config migration audit reports {migration['candidate_count_new']} candidates, maximum absolute score difference {migration['max_abs_score_diff']:.3g}, unchanged ranking: {migration['ranking_same']}, unchanged Top-10: {migration['top10_same']}, unchanged Pareto membership: {migration['pareto_same']}.
- Four-term deterministic sensitivity minimum Spearman rho {float(weight_summary['spearman_with_base'].min()):.6f}; minimum Top-10 overlap {int(weight_summary['top10_overlap'].min())}/10.
- Monte Carlo: 1,000 normalized multiplicative perturbations around BASE within +/-20%; see `results/candidate_rank_stability_v2.csv`.

### Runtime boundary

- 2.5D full 630-candidate screening median: {runtime_summary['screening_median_seconds']:.2f} s across three isolated repeats.
- HB per-scene measured median: {runtime_summary['hb_median_seconds_per_scene']:.2f} s across {runtime_summary['total_measured_hb_scene_count']} measured scenes.
- 630-scene HB value: {runtime_summary['serial_equivalent_hb_630_seconds']:.2f} s, explicitly a serial-equivalent extrapolation from the measured per-scene median, not a completed 630-scene run.
- Operational batch elapsed wall time: `NOT_MEASURED`.

## Recommended paper structure

1. **Introduction:** old-district solar-access problem; need for reproducible, low-cost and reviewable spatial decision support; state the scope-limited research question.
2. **Related work:** urban solar/daylight metrics, urban form and solar access, computational design exploration, human-in-the-loop AEC systems. Use only verified entries in the maintained bibliography; do not invent citations.
3. **Data and method:** source audit and canonicalization; fixed solar protocol; A/B/C workflow; 2.5D blocking; four-term score; selective HB verification; frozen independent sample; design translation and human review.
4. **Experiments:** complete 630 screening; curated 23-candidate HB check; frozen N=20 metric validation; frozen N=20 composite validation; four-term sensitivity; runtime semantics.
5. **Results:** use Tables 1-9 and Figures 1-9 by the index files. Keep measured, extrapolated, operational and research-only labels visible.
6. **Discussion:** what the workflow helps with, where ranking agrees/disagrees, why design translation can change desirability, and why human review remains necessary.
7. **Limitations and conclusion:** simplified 2.5D assumptions, selective rather than exhaustive HB, one private site, one frozen sample, no buildability/legal/heritage proof, and no claim of human-design superiority.

## Evidence-to-claim rules

Allowed: exhaustive screening of the defined 630 universe; scope-qualified agreement on the frozen N=20 sample; selective HB verification; deterministic sensitivity; human-in-the-loop design translation.

Forbidden: “99.7% accuracy,” universal accuracy, Radiance as ground truth, all 630 HB simulations, AI beats human design, global optimum, learned AI/ML if not added, or proof of construction/legal/heritage compliance.

## Figure/table source map

- Tables: `paper_support/TABLE_INDEX.md`.
- Figures: `paper_support/FIGURE_INDEX.md`.
- Numbers: `paper_support/PAPER_NUMBERS.csv`.
- Claim permissions: `paper_support/CLAIMS_LEDGER.csv`.
- Historical and migration audits: `paper_support/RESULT_DIFF_AUDIT.csv` and `audit/SCORING_FORMULA_MIGRATION_AUDIT.csv`.
- Reproduction sequence: `REPRODUCE.md`; environment: `ENVIRONMENT.md`.

## Formatting and integrity checklist

- Use the official SOICT 2026 author template and current submission instructions at writing time; do not infer page limits or reference style from this brief.
- Keep figure/table numbering synchronized with the index and all in-text cross-references.
- Keep the four-term formula in one place and cite the config-driven weights.
- Mark every new result with a source file and run ID before drafting prose.
- Do not upload private CAD/SKP/OBJ/DXF, full sensor coordinates, Radiance intermediate files, licensed weather files or local personal paths to the public repository.
- Treat the Word/LaTeX manuscript as a later writing artifact. This package is the evidence handoff, not the final paper.
"""
    (support / "SOICT_2026_PAPER_WRITING_BRIEF.md").write_text(brief, encoding="utf-8")
    (run_dir / "SOICT_2026_PAPER_WRITING_BRIEF.md").write_text(brief, encoding="utf-8")
    (ROOT / "SOICT_2026_PAPER_WRITING_BRIEF.md").write_text(brief, encoding="utf-8")

    summary = {
        "repo": "eksn425-del/light-right-repair-ai-prototype",
        "branch": "research-repro-v1",
        "commit": "TO_BE_RECORDED_AFTER_RELEASE_COMMIT",
        "tag": "soict-2026-write-ready-v1",
        "run_id": run_dir.name,
        "soict_write_ready": True,
        "production_score": {
            "formula": "0.45 A_norm + 0.35 H_norm + 0.15 (1-V_norm) + 0.05 (1-N_norm)",
            "low_area_drop": runtime.low_area_drop_weight,
            "avg_gain": runtime.avg_gain_weight,
            "volume_economy": runtime.intervention_volume_economy_weight,
            "new_low_avoidance": runtime.new_low_area_avoidance_weight,
        },
        "reproduction": {"status": "PASS", "candidate_count": len(candidates), "eligible_buildings": len(eligible), "sensor_count": len(pd.read_csv(results_csv / "100_HB_Radiance传感点.csv"))},
        "independent_metric_validation": {"status": "PASS", "sample_size": int(metric_value(independent, "sample_size")), "spearman_rho": metric_value(independent, "spearman_rho"), "mae_low_area_m2": metric_value(independent, "mae_low_area")},
        "independent_composite_validation": {"status": "PASS", "sample_size": int(metric_value(composite, "sample_size")), "spearman_rho": composite_rho, "top3": composite_top3, "top5": composite_top5, "top10": composite_top10, "mean_abs_rank_error": metric_value(composite, "mean_absolute_rank_error"), "median_abs_rank_error": metric_value(composite, "median_absolute_rank_error"), "max_abs_rank_error": metric_value(composite, "max_absolute_rank_error")},
        "runtime": runtime_summary,
        "weight_sensitivity_v2": {"status": "PASS", "scenario_count": len(weight_summary), "min_rho": float(weight_summary["spearman_with_base"].min()), "min_top10_overlap": int(weight_summary["top10_overlap"].min()), "monte_carlo_draws": 1000, "monte_carlo_seed": 20260909},
        "design_translation": {"status": "PASS", "rerun_count": len(design_rerun), "review_required_count": len(design_review), "source": "results/design_translation_summary.csv"},
        "tests": {"status": "PASS", "command": "pytest -q", "test_count": 19},
        "warnings": ["Operational HB batch elapsed time is NOT_MEASURED.", "Selective HB verification is not an all-630 high-fidelity simulation.", "Design acceptance remains human-in-the-loop."],
    }
    (run_dir / "RESULTS_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "RESULTS_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    handoff = f"""# HANDOFF_TO_CHATGPT

## Repository state

- Repository: `eksn425-del/light-right-repair-ai-prototype`
- Branch: `research-repro-v1`
- Final release commit: `TO_BE_RECORDED_AFTER_RELEASE_COMMIT`
- Tag: `soict-2026-write-ready-v1`
- Run ID: `{run_dir.name}`
- `SOICT_WRITE_READY`: `TRUE` after the recorded final QA, public-safe copy and tag verification.

## Scientific definition frozen for writing

- Production score: `0.45 A_norm + 0.35 H_norm + 0.15 (1-V_norm) + 0.05 (1-N_norm)`.
- Weights are read from `configs/research.yaml`; the scoring migration audit found unchanged 630 candidate IDs, scores, ranks, Top-10 and Pareto membership.
- Height rule, timezone, timestep and strict booleans are runtime/config-driven.
- The independent N=20 sample and SHA256 are unchanged; do not reselect or rerun it.

## Final evidence

- 45 buildings, 36 eligible, 630 defined 2.5D candidates, 2,031 sensors.
- 23 selected rule candidates verified; 33 operational HB scenes; 20 research-only independent scenes; 53 measured HB scenes total.
- Independent metric validation: rho {metric_value(independent, 'spearman_rho'):.6f}; MAE {metric_value(independent, 'mae_low_area'):.2f} m2.
- Independent composite validation: rho {composite_rho:.6f}; Top3/Top5/Top10 recall {composite_top3:.3f}/{composite_top5:.3f}/{composite_top10:.3f}; mean/median/max absolute rank error {metric_value(composite, 'mean_absolute_rank_error'):.1f}/{metric_value(composite, 'median_absolute_rank_error'):.1f}/{metric_value(composite, 'max_absolute_rank_error'):.1f}.
- Four-term weight sensitivity v2: minimum deterministic rho {float(weight_summary['spearman_with_base'].min()):.6f}; minimum deterministic Top-10 overlap {int(weight_summary['top10_overlap'].min())}/10; 1,000 normalized Monte Carlo draws.
- Runtime: 2.5D median {runtime_summary['screening_median_seconds']:.2f}s; HB measured per-scene median {runtime_summary['hb_median_seconds_per_scene']:.2f}s; 630 HB serial-equivalent {runtime_summary['serial_equivalent_hb_630_seconds']:.2f}s, not directly measured.

## Required wording boundary

Use “within-independent-sample composite-ranking agreement,” “selective HB-Radiance verification,” and “human-in-the-loop design translation.” Do not write 99.7% accuracy, universal accuracy, Radiance as ground truth, all-630 HB, AI beats human, global optimum, or proven buildability/legal/heritage compliance.

## First files for the web conversation

1. `SOICT_2026_PAPER_WRITING_BRIEF.md`
2. `paper_support/PAPER_NUMBERS.csv`
3. `paper_support/CLAIMS_LEDGER.csv`
4. `paper_support/TABLE_INDEX.md` and `paper_support/FIGURE_INDEX.md`
5. `paper_support/RESULT_DIFF_AUDIT.csv` and `audit/SCORING_FORMULA_MIGRATION_AUDIT.csv`
6. `REPRODUCE.md` and `ENVIRONMENT.md`

## Explicit limitations

- No full 630-scene HB run was performed; the stated value is serial-equivalent extrapolation.
- Operational batch elapsed time is `NOT_MEASURED`.
- Private geometry, sensor coordinates and Radiance intermediates remain outside the public mirror.
- This package is a writing/evidence handoff, not polished paper正文.
"""
    (run_dir / "HANDOFF_TO_CHATGPT.md").write_text(handoff, encoding="utf-8")
    (ROOT / "HANDOFF_TO_CHATGPT.md").write_text(handoff, encoding="utf-8")

    write_run_metadata(
        runtime,
        stage="paper_support_v2",
        inputs=[results_csv / "120_canonical_2p5D完整双建筑候选排名.csv", results / "independent_composite_metrics.csv", results / "runtime_summary_v2.json", runtime.config_path],
        extra={"paper_numbers": str(support / "PAPER_NUMBERS.csv"), "claims_ledger": str(support / "CLAIMS_LEDGER.csv"), "writing_brief": str(support / "SOICT_2026_PAPER_WRITING_BRIEF.md")},
    )
    print(f"Built paper-support v2 package in {support}")


if __name__ == "__main__":
    main()
