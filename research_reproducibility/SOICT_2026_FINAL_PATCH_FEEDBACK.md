# SOICT 2026 Final Patch Feedback

Date: 2026-09-10  
Project: Light Equity / Solar-Access Computational Screening Research  
Branch: `research-repro-v1`  
Run ID: `baseline_20260909_clean`

## Status

The final patch is complete and the package is ready for a factual, evidence-bounded paper-writing handoff.

`SOICT_WRITE_READY = TRUE` means that the scoring definition, configuration source, frozen-sample checks, regression audits, tests, ledgers and public-safe release checks passed. It does not mean that a polished paper has been written or that all 630 candidates received high-fidelity HB-Radiance simulation.

## What changed

- Unified production scoring as `0.45 A_norm + 0.35 H_norm + 0.15 (1 - V_norm) + 0.05 (1 - N_norm)`.
- Made weights, height reduction, timezone, timestep and strict boolean parsing configuration-driven.
- Fixed the N=12 stratified fallback allocation to `3/3/2/2/2`; N=20 remains `4/4/4/4/4`.
- Added a 630-candidate score migration audit. Candidate IDs, pairs, scores, ranks, Top-10 and Pareto membership were unchanged; maximum absolute score difference was `0`.
- Added composite-ranking validation on the pre-frozen independent N=20 HB sample without reselecting or rerunning that sample.
- Rebuilt weight sensitivity with the four-term production formula, six declared scenarios and 1,000 normalized Monte Carlo draws.
- Separated measured screening time, measured per-scene HB time, operational scenes, research-only scenes and serial-equivalent extrapolation.
- Added public-safe aggregate outputs and refreshed the paper-number and claims ledgers.

## Key evidence

- 45 buildings, 36 eligible buildings, 630 defined 2.5D candidates and 2,031 sensors.
- 23 selected rule candidates, 33 operational HB scenes, 20 research-only independent scenes and 53 measured HB scenes total.
- Independent composite validation: Spearman rho `1.000000`; Top-3 `3/3`; Top-5 `5/5`; Top-10 `10/10`; mean/median/max absolute rank error `0/0/0`.
- Four-term weight sensitivity: minimum deterministic rho `0.975941`; minimum deterministic Top-10 overlap `6/10`; Monte Carlo seed `20260909`.
- 2.5D screening median `55.40 s`; measured HB per-scene median `51.11 s`.
- 630-scene HB value `32197.24 s` is serial-equivalent extrapolation, not a completed batch measurement.

## Verification

- Private research package: `19 passed`.
- Public-safe mirror: `17 passed, 2 skipped`; skipped tests require intentionally omitted private geometry tables.
- Python compile check and `git diff --check`: passed.
- `main` branch was not modified.
- Public mirror contains no private CAD, DXF, DWG, SKP, sensor-coordinate or Radiance intermediate files.

## Writing boundary

Use “within-independent-sample composite-ranking agreement”, “selective HB-Radiance verification” and “human-in-the-loop design translation”. Do not write universal accuracy, Radiance as ground truth, all-630 HB, AI superiority over human design, global optimum or proven buildability/legal/heritage compliance.

## Recommended handoff files

1. `SOICT_2026_PAPER_WRITING_BRIEF.md`
2. `paper_support/PAPER_NUMBERS.csv`
3. `paper_support/CLAIMS_LEDGER.csv`
4. `paper_support/TABLE_INDEX.md`
5. `paper_support/FIGURE_INDEX.md`
6. `paper_support/RESULT_DIFF_AUDIT.csv`
7. `audit/SCORING_FORMULA_MIGRATION_AUDIT.csv`
8. `HANDOFF_TO_CHATGPT.md`
9. `RESULTS_SUMMARY.json`

## Remaining limitations

- No full 630-scene HB run was performed.
- Operational HB batch elapsed time remains `NOT_MEASURED`.
- The evidence is from one private site and one frozen independent sample.
- Geometry, design translation, buildability, legal/heritage review and final acceptance remain human-in-the-loop.

This is an engineering and research handoff report, not polished paper正文.
