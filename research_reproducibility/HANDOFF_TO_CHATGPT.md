# HANDOFF_TO_CHATGPT

## Repository state

- Repository: `eksn425-del/light-right-repair-ai-prototype`
- Branch: `research-repro-v1`
- Final release commit: `6b64fe43451e2e0330930a5677cbe3432307282b`
- Tag: `soict-2026-write-ready-v1`
- Run ID: `baseline_20260909_clean`
- `SOICT_WRITE_READY`: `TRUE` after the recorded final QA, public-safe copy and tag verification.

## Scientific definition frozen for writing

- Production score: `0.45 A_norm + 0.35 H_norm + 0.15 (1-V_norm) + 0.05 (1-N_norm)`.
- Weights are read from `configs/research.yaml`; the scoring migration audit found unchanged 630 candidate IDs, scores, ranks, Top-10 and Pareto membership.
- Height rule, timezone, timestep and strict booleans are runtime/config-driven.
- The independent N=20 sample and SHA256 are unchanged; do not reselect or rerun it.

## Final evidence

- 45 buildings, 36 eligible, 630 defined 2.5D candidates, 2,031 sensors.
- 23 selected rule candidates verified; 33 operational HB scenes; 20 research-only independent scenes; 53 measured HB scenes total.
- Independent metric validation: rho 0.997668; MAE 0.45 m2.
- Independent composite validation: rho 1.000000; Top3/Top5/Top10 recall 1.000/1.000/1.000; mean/median/max absolute rank error 0.0/0.0/0.0.
- Four-term weight sensitivity v2: minimum deterministic rho 0.975941; minimum deterministic Top-10 overlap 6/10; 1,000 normalized Monte Carlo draws.
- Runtime: 2.5D median 55.40s; HB measured per-scene median 51.11s; 630 HB serial-equivalent 32197.24s, not directly measured.

## Required wording boundary

Use “within-independent-sample composite-ranking agreement,” “selective HB-Radiance verification,” and “human-in-the-loop design translation.” Do not write 99.7% accuracy, universal accuracy, Radiance as ground truth, all-630 HB, AI beats human, global optimum, or proven buildability/legal/heritage compliance.

## First files for the web conversation

1. `SOICT_2026_PAPER_WRITING_BRIEF.md`
2. `paper_support/PAPER_NUMBERS.csv`
3. `paper_support/CLAIMS_LEDGER.csv`
4. `paper_support/TABLE_INDEX.md` and `paper_support/FIGURE_INDEX.md`
5. `paper_support/RESULT_DIFF_AUDIT.csv` and `audit/SCORING_FORMULA_MIGRATION_AUDIT.csv`
6. `REPRODUCE.md` and `ENVIRONMENT.md`

## Paper asset package

- Complete private repository: `https://github.com/eksn425-del/soict-2026-paper-assets`
- Private branch: `paper-assets-v1`
- Private core-asset commit: `1f886551991d0e2a653de72981e084c6ecb89b6d`
- Private current branch tip (includes feedback): `189a5746bc75b593454ac1e9315a45b5bbdde637`
- Private tag: `soict-2026-paper-assets-v1`
- Complete package path: `paper_assets/`
- Public-safe subset path: `research_reproducibility/paper_assets/`
- Public mirror asset commit: `b3da4c58d1f86745bf16f6579a02a0f2edfb2650`

The private package contains Figures 1--9 and all numbered table CSVs. Figure
2, Figure 5, Table 1, Table 3 and Table 4 are private-only because they may
expose site-specific geometry or identifiers. No raw CAD/DXF/DWG/SKP/OBJ,
sensor coordinate tables, Radiance intermediate files, or unauthorized real
raw data is included.

The package feedback document is `paper_assets/FEEDBACK_REPORT.md` in the
private repository and `research_reproducibility/paper_assets/FEEDBACK_REPORT.md`
in this public mirror.

## Explicit limitations

- No full 630-scene HB run was performed; the stated value is serial-equivalent extrapolation.
- Operational batch elapsed time is `NOT_MEASURED`.
- Private geometry, sensor coordinates and Radiance intermediates remain outside the public mirror.
- This package is a writing/evidence handoff, not polished paper正文.
