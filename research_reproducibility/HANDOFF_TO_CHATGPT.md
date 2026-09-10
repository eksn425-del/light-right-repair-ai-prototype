# Handoff to the web conversation

## Project status

- Project: Light Equity / Solar-Access Computational Screening Research
- Current run: `baseline_20260909_clean`
- Dataset: private Xieyan lakeside site, canonicalized from the Route B research package.
- Method: geometry audit -> 2.5D exhaustive candidate screening -> selective HB-Radiance verification -> independent validation -> design-translation judgement.

## Verified outputs

- 45 building records; 36 eligible buildings under the declared rule; 630 unordered two-building candidates.
- 2,031 fixed ground sensors at a 3 m grid and 0.1 m sensor height.
- 23 curated rule candidates and 31 HB scenes in the merged run output; 20 additional independent validation candidates were frozen and successfully run.
- Independent sample: Spearman rho 0.997668, MAE of low-area drop 0.45 m2, median absolute error 0 m2, sign agreement 1.0, Top-10 recall 1.0. These statistics apply only to the frozen 20-pair sample and declared metric.
- Curated verified ranking: Spearman rho 0.883399.
- Runtime: 2.5D median 52.33 s per full 630-candidate screening; HB median 51.11 s per measured scene; the 630-scene HB value is an extrapolation, not a completed run.

## Candidate judgement boundary

- C9,C15: positive design translation in the current metric and no observed new low-area signal or worsened points in the rerun. Still requires architectural review.
- C9,C24: higher gain but 4 worsened points and 9 m2 new low-area signal in the design translation; treat as a review-required trade-off candidate.
- C13,C24: design translation also retains adverse signals; do not present as an automatic recommendation.
- C6,C33 and C9,C13 are retained as evidence candidates, not universal answers.

## Files to use

- `paper_support/PAPER_NUMBERS.csv`: paper-number source of truth.
- `paper_support/CLAIMS_LEDGER.csv`: supported wording and forbidden overclaims.
- `paper_support/RESULT_DIFF_AUDIT.csv`: clean rerun versus copied June artifacts.
- `paper_support/TABLE_INDEX.md` and `paper_support/FIGURE_INDEX.md`: paper mapping.
- `REPRODUCE.md`: exact rerun sequence.
- `ENVIRONMENT.md`: Python, package and Radiance environment.

## Not done / must remain explicit

- No full 630-scene HB-Radiance run was performed.
- No claim of AI/ML training, human-design superiority, universal accuracy, structural feasibility, legal compliance or heritage approval.
- The source CAD/SKP/OBJ data remain private and require permission before any external upload.

## Git

- Local reproducibility commit: `319b0ec` (the code/results package commit before this handoff note).
- Final local tag: `soict-2026-repro-final`.
- Public GitHub mirror branch: [research-repro-v1](https://github.com/eksn425-del/light-right-repair-ai-prototype/tree/research-repro-v1/research_reproducibility).
- Public mirror commit: `3994be8`; this branch contains public-safe code and paper-support summaries only.
- Raw CAD/SKP/OBJ/DXF, sensor-coordinate tables and Radiance intermediates remain local/private.
