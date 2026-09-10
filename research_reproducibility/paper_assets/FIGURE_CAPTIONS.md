# Figure Captions

All figures below are tied to frozen run ID `baseline_20260909_clean`, source commit `6b64fe43451e2e0330930a5677cbe3432307282b`, and tag `soict-2026-write-ready-v1`. The labels `PUBLIC` and `PRIVATE ONLY` are release controls, not claims about scientific validity.

## Figure 1
**Caption:** Reproducible computational workflow for the proposed street-scale solar-access screening and minimum-intervention decision process. The workflow separates input normalization, low-cost 2.5D screening, selective HB-Radiance verification, composite ranking, and human review.

- Asset: `figures/png/F01_workflow.png`
- Visibility: `PUBLIC`
- Source CSV: `N/A (schematic figure)`
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 2
**Caption:** Baseline direct-sun-hours field on the 3 m analysis grid. The field is shown as a site-specific diagnostic for the frozen study area and should be interpreted within the stated winter-solstice time window and sensor definition.

- Asset: `figures/png/F02_baseline_field.png`
- Visibility: `PRIVATE ONLY (site geometry may be identifiable)`
- Source CSV: `results_csv/100_HB_Radiance传感点.csv`; baseline HB cumulative result file
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 3
**Caption:** Agreement between canonical 2.5D candidate ranking and curated HB-Radiance verification. The comparison is evidence for the frozen candidate set and selected verification scenes; it is not a claim of universal transferability.

- Asset: `figures/png/F03_curated_rank_agreement.png`
- Visibility: `PUBLIC`
- Source CSV: `results_csv/132_HB_Radiance已复核候选排名与Pareto.csv`; `results_csv/120_canonical_2p5D完整双建筑候选排名.csv`
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 4
**Caption:** Translation of a rule-selected massing intervention into architectural design language, including the distinction between the computational rule and the human-readable operations used for review.

- Asset: `figures/png/F04_design_translation_comparison.png`
- Visibility: `PUBLIC`
- Source CSV: `results_csv/138_最终候选规则与设计转译对比.csv`; `results/design_translation_summary.csv`
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 5
**Caption:** Point-level change map for the selected candidate relative to the baseline field. This figure is retained for the private manuscript package because the plotted point distribution can reveal the real study geometry.

- Asset: `figures/png/F05_candidate_change_map.png`
- Visibility: `PRIVATE ONLY (site geometry may be identifiable)`
- Source CSV: `results_csv/141_已复核候选Python与HB点位对齐结果.csv`
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 6
**Caption:** Frozen independent validation of the low-area screening metric against HB-Radiance outcomes. The points represent the predeclared independent sample and should be reported with its sample size and scope.

- Asset: `figures/png/F06_independent_validation_scatter.png`
- Visibility: `PUBLIC`
- Source CSV: `results/independent_validation_results.csv`; `results/independent_validation_metrics.csv`
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 7
**Caption:** Runtime evidence separated by measurement semantics: measured 2.5D screening repeats, measured single HB scenes, and the serial-equivalent extrapolation for 630 HB scenes. The extrapolated value is explicitly not a completed batch measurement.

- Asset: `figures/png/F07_runtime_comparison_v2.png`
- Visibility: `PUBLIC`
- Source CSV/JSON: `results/runtime_benchmark_v2.csv`; `results/runtime_summary_v2.json`
- Source script: `scripts/run_runtime_benchmark.py` (asset re-render at 320 dpi by `scripts/build_paper_assets.py`)
- Run ID: `baseline_20260909_clean`

## Figure 8
**Caption:** Robustness of the four-term production-score ranking under the preregistered scenario set and Monte Carlo weight perturbation. Frequencies describe selection within the frozen 630-candidate universe and do not establish robustness outside that universe.

- Asset: `figures/png/F08_weight_robustness_v2.png`
- Visibility: `PUBLIC`
- Source CSV: `results/weight_sensitivity_v2.csv`; `results/candidate_rank_stability_v2.csv`; `results/weight_sensitivity_summary_v2.csv`
- Source script: `scripts/run_weight_sensitivity.py` (asset re-render at 320 dpi by `scripts/build_paper_assets.py`)
- Run ID: `baseline_20260909_clean`

## Figure 9
**Caption:** Independent composite-ranking agreement between the 2.5D screening score and the HB-Radiance composite score on the frozen independent sample. Report the sample scope, fixed normalization universe, and four-term score definition with this figure.

- Asset: `figures/png/F09_independent_composite_ranking.png`
- Visibility: `PUBLIC`
- Source CSV: `results/independent_composite_metrics.csv`; `results/independent_composite_ranking.csv`
- Source script: `scripts/validate_independent_composite.py`
- Run ID: `baseline_20260909_clean`

## Asset-format note
Each figure has a high-resolution PNG plus PDF and SVG companions. The PDF/SVG companions embed the final raster pixels in publication containers; they should not be described as newly vectorized artwork.
