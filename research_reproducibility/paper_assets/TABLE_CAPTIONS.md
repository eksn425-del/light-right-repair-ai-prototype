# Table Captions

All table CSVs are derived from the frozen run ID `baseline_20260909_clean`, source commit `6b64fe43451e2e0330930a5677cbe3432307282b`, and tag `soict-2026-write-ready-v1`. Derived paper CSVs remove local absolute paths; they do not alter numerical values.

## Table 1
**Caption:** Source-to-canonical geometry audit for the study model, including centroid, height, footprint, and label/group consistency checks.

- Asset: `tables/table_01_geometry_audit.csv`
- Visibility: `PRIVATE ONLY (contains site geometry and identifiers)`
- Source CSV: `results_csv/91_建筑几何一致性总表.csv`
- Source script: `scripts/build_paper_support.py` and audit pipeline
- Run ID: `baseline_20260909_clean`

## Table 2
**Caption:** Declared solar-analysis protocol, grid and sensor parameters, time window, and simulation recipe. Local input paths are intentionally removed from the paper-facing CSV.

- Asset: `tables/table_02_analysis_protocol.csv`
- Visibility: `PUBLIC`
- Source CSV: `results_csv/100_HB_Radiance场景参数表.csv`; configuration `configs/research.yaml`
- Source script: `scripts/build_paper_assets.py`
- Run ID: `baseline_20260909_clean`

## Table 3
**Caption:** Complete 630-candidate 2.5D screening universe with the four-term production-score inputs and deterministic ranking fields.

- Asset: `tables/table_03_candidate_universe.csv`
- Visibility: `PRIVATE ONLY (site-specific candidate identifiers and geometry-derived values)`
- Source CSV: `results_csv/120_canonical_2p5D完整双建筑候选排名.csv`
- Source script: `src/legacy_route_b/route_b_enumerate_2p5d_candidates.py`
- Run ID: `baseline_20260909_clean`

## Table 4
**Caption:** Curated HB-Radiance verification results and Pareto/ranking fields for the selected rule candidates. Local project-folder paths are removed.

- Asset: `tables/table_04_curated_hb_verification.csv`
- Visibility: `PRIVATE ONLY (site-specific candidate identifiers)`
- Source CSV: `results_csv/132_HB_Radiance已复核候选排名与Pareto.csv`
- Source script: HB verification and ranking pipeline
- Run ID: `baseline_20260909_clean`

## Table 5
**Caption:** Frozen independent validation metrics for the low-area screening measure against HB-Radiance outcomes.

- Asset: `tables/table_05_independent_metric_validation.csv`
- Visibility: `PUBLIC`
- Source CSV: `results/independent_validation_metrics.csv`
- Source script: `scripts/analyze_independent_validation.py`
- Run ID: `baseline_20260909_clean`

## Table 6
**Caption:** Rule-selected candidate and human-readable design-translation summary, including reported improvements, new low-sun areas, and human-review flags.

- Asset: `tables/table_06_design_translation.csv`
- Visibility: `PUBLIC`
- Source CSV: `results/design_translation_summary.csv`; detailed source `results_csv/138_最终候选规则与设计转译对比.csv`
- Source script: design-translation validation pipeline
- Run ID: `baseline_20260909_clean`

## Table 7
**Caption:** Runtime measurements and semantic labels distinguishing measured, operational, research-only, and serial-equivalent quantities.

- Asset: `tables/table_07_runtime_semantics.csv`
- Visibility: `PUBLIC`
- Source JSON/CSV: `results/runtime_summary_v2.json`; `results/runtime_benchmark_v2.csv`
- Source script: `scripts/run_runtime_benchmark.py`
- Run ID: `baseline_20260909_clean`

## Table 8
**Caption:** Independent four-term composite-ranking validation metrics and row-level ranking results for the frozen N=20 sample.

- Assets: `tables/table_08_independent_composite_metrics.csv`; `tables/table_08_independent_composite_ranking.csv`
- Visibility: `PUBLIC`
- Source CSV: `results/independent_composite_metrics.csv`; `results/independent_composite_ranking.csv`
- Source script: `scripts/validate_independent_composite.py`
- Run ID: `baseline_20260909_clean`

## Table 9
**Caption:** Four-term weight sensitivity under named scenarios and Monte Carlo candidate-rank stability under the declared perturbation protocol.

- Assets: `tables/table_09_weight_sensitivity_summary.csv`; `tables/table_09_candidate_rank_stability.csv`
- Visibility: `PUBLIC`
- Source CSV: `results/weight_sensitivity_summary_v2.csv`; `results/candidate_rank_stability_v2.csv`
- Source script: `scripts/run_weight_sensitivity.py`
- Run ID: `baseline_20260909_clean`

## CSV note
CSV files are data tables for manuscript production. They should be imported into the target SOICT template and rechecked after typesetting for rounding, column width, and reference numbering.
