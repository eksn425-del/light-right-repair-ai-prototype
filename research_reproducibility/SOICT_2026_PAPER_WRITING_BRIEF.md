# SOICT 2026 paper-writing brief

This is a factual and structural handoff, not polished paper prose. Every number below must be checked against `paper_support/PAPER_NUMBERS.csv` before it is placed in a manuscript.

## Research identity

- Working topic: reproducible solar-access computational screening for minimum-intervention spatial decision support in an old urban district.
- Study site: private canonicalized lakeside-site dataset from the Xieyan group.
- Core question: can a low-cost rule-based 2.5D screening workflow narrow a declared candidate universe while preserving useful agreement with selective HB-Radiance checks and keeping design judgement human-in-the-loop?
- Do not frame the study as AI replacing designers, as a comparison against a human design, or as a trained ML/LLM system.

## Fixed protocol

- Analysis date: 2026-12-21; local timezone: Asia/Shanghai; UTC offset: +8.
- Local time: 08:15-15:45; timestep: 30 minutes.
- Location: approximately 24.55 N, 118.03 E; north convention 0.0 degrees.
- Ground grid: 3 m; sensor height: 0.1 m; low-sun threshold: 3 h.
- Height rule: `new_h=max(height_floor_m, h-min(height_reduction_cap_m, height_reduction_fraction*h))`, configured as 3 m floor, 3 m cap and 0.25 fraction.
- Production score: `0.45 A_norm + 0.35 H_norm + 0.15 (1-V_norm) + 0.05 (1-N_norm)`, with all four weights read from `configs/research.yaml`.

## Evidence inventory

- 45 building records; 36 eligible buildings under the declared strict boolean and height rule; 630 unordered two-building candidates screened exhaustively by the 2.5D procedure.
- 2,031 fixed sensors.
- 23 selected rule candidates verified in the operational/curated HB evidence; 33 HB scenes belong to the operational workflow; 20 independent HB scenes are research-only validation evidence; 53 HB scenes were measured in total.
- The frozen independent sample is N=20 with SHA256 recorded in `independent_validation/VALIDATION_SAMPLE_FROZEN.sha256`. Do not reselect it.

## Results to report carefully

### Metric validation

- Legacy independent low-area-drop validation: Spearman rho 0.997668, Pearson r 0.999623, MAE 0.45 m2, sign agreement 1.000. This is a frozen N=20 within-sample result.
- Composite validation using the same frozen sample, the four predeclared weights and fixed 630-universe normalization bounds: Spearman rho 1.000000; Top-3 recall 1.000; Top-5 recall 1.000; Top-10 recall 1.000; mean/median/max absolute rank error 0.0/0.0/0.0 positions.
- The phrase to use is “within-independent-sample composite-ranking agreement,” not global recall or universal accuracy.

### Ranking migration and sensitivity

- The config migration audit reports 630 candidates, maximum absolute score difference 0, unchanged ranking: True, unchanged Top-10: True, unchanged Pareto membership: True.
- Four-term deterministic sensitivity minimum Spearman rho 0.975941; minimum Top-10 overlap 6/10.
- Monte Carlo: 1,000 normalized multiplicative perturbations around BASE within +/-20%; see `results/candidate_rank_stability_v2.csv`.

### Runtime boundary

- 2.5D full 630-candidate screening median: 55.40 s across three isolated repeats.
- HB per-scene measured median: 51.11 s across 53 measured scenes.
- 630-scene HB value: 32197.24 s, explicitly a serial-equivalent extrapolation from the measured per-scene median, not a completed 630-scene run.
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
