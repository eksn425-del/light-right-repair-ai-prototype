# Frozen-table statistics and time semantics audit

**Local resolution, 2026-10-17:** the recomputation below remains a historical
aggregate audit, not new HB. Its then-unverified input/time statements are now
resolved by `LOCAL_PROTOCOL_FINDINGS.md` and `runs/local_hb_20261016/`.
Actual16-slot/WEA/HOY/solar-column mapping and UTC+8 are checked; constant
DNI1000/DHI0 is not measured weather. Actual HB and pvlib effective rays differ
slightly. Six legacy scenes were exactly replayed and four contained corrections
were separately simulated. The original20 sample and all old statistics remain
unchanged; no resampling or heldout HB rerun was performed. Canonical bbox/shared
footprint fidelity limits all physical interpretation, including agreement
statistics. Current efficiency is the separately measured local A/B comparison,
not any of the historical cross-solver or extrapolated costs below.

Run: `statistics_20261016`; executed 2026-10-16 UTC after protocol commit
`ae7483ca493768e23a19cf402446c54d6f6c95ef`. Historical scientific freeze:
`6b64fe43451e2e0330930a5677cbe3432307282b`, run `baseline_20260909_clean`.
Source retrieval was pinned to `ce4087f564a1169b500c0106f869158349c58c6e`.

Status: **frozen aggregate recomputation completed; physical replay and actual
HB time-vector equivalence remain blocked by absent private inputs**. These are
new calculations on old aggregate measurements, not new HB/2.5D simulations.
The audit script's own SHA256, all source hashes, protocol hash and dependency
versions are in `../runs/statistics_20261016/summary.json` and `input_manifest.csv`.

## 1. Immutable sample and sampling interpretation

The original frozen CSV was retrieved as base64 and decoded without text-mode
newline conversion. Its 6,830 bytes include a UTF-8 BOM and CRLF line endings.
Actual and declared SHA256 both equal:

`ad4abb9b89a263edaecc2cb3553f7832ce0ccb460521ba218e0083e05bcb46b2`

All 20 pair identities and sample orders match the archived composite table;
none overlaps the curated 23. Each of five score strata contains four pairs.
The sampler was not run. Selection used score strata, volume coverage and
building-ID diversity from the remaining 607 pairs, with a fixed tie-breaking
seed. This is an outcome-blind coverage sample held out from curated review,
not a probability sample, independent source dataset or cross-site validation.

The archived freeze metadata reports `2026-09-09T18:10:36+00:00`; the earliest
heldout HB runtime record reports `2026-09-09T18:12:39+00:00`. The ordering is
supported by these execution records, not by the hash itself. These are
archived local logs, without independent trusted timestamp attestation. Do not
describe this as an externally preregistered trial.

## 2. Complete universe, normalization and N=0

The 630 unique pairs are exactly C(36,2) for the 36 IDs appearing in the frozen
universe. This checks completeness of that table; it is not a fresh inspection
of the missing footprint/sensor source data or proof of legal eligibility.

Fixed 630-candidate bounds were recomputed:

| Term | Minimum | Maximum | Unit |
|---|---:|---:|---|
| A, low-sun-area reduction | 0 | 396 | m² |
| H, mean direct-sun-hours gain | 0 | 0.0635155096011816 | h |
| V, rule intervention volume | 387.3824354304028 | 10891.474417736685 | m³ |
| N, newly low-sun area | 0 | 0 | m² |

The zero-range transform returns 0. With weights 0.45/0.35/0.15/0.05, N adds
the same 0.05 to every score and has no discriminating effect. Recomputed
scores agree with stored values to a maximum absolute difference of
4.996003610813204e-16. Changing only N's weight to 0, 0.05, 0.25 or 1.0 preserves
all 630 pair ranks. This check leaves A/H/V weights fixed and does not renormalize
them; the mathematical result is simply an additive constant.

The legacy `NEW_LOW_SENSITIVE` setting changes A from .45 to .40, H from .35 to
.30, and N from .05 to .15. Its rank changes cannot show that the N penalty
itself is effective. The zero-range N transform also must not be carried
uncritically into a new design universe with positive N; that would need a
separately declared scale. No weight tuning or new simulations were performed.

## 3. Like-for-like comparisons, kept separate

All composite scores below use the same full-universe bounds and 45/35/15/5
formula on both sides. HB outcomes do not determine new normalization ranges.
Spearman uses average ranks for ties; these are descriptive sample comparisons.

| Cohort | Same-metric comparison | Spearman rho | MAE | Unit |
|---|---|---:|---:|---|
| curated23 | A versus A | 0.9992582518450251 | 0.391304347826087 | m² |
| curated23 | H versus H | 0.9915966386554622 | 0.0011774024361526744 | h |
| curated23 | score versus score | 0.9990118577075099 | 0.006932699083861882 | score |
| heldout20 | A versus A | 0.997668088547906 | 0.45 | m² |
| heldout20 | H versus H | 0.9996239894584121 | 0.00029542097488923 | h |
| heldout20 | score versus score | 1.0 | 0.0021392706131078978 | score |

The legacy curated rho `0.8833992094861661` is reproduced from the stored
2.5D-composite ranking versus HB-area ranking. It compares different targets.
It must not be contrasted with heldout A–A or score–score rho as a gain in model
accuracy. The new same-metric curated numbers correct the comparison's meaning;
the old number remains valid for its explicitly different target.

Curated A: 22 exact agreements and one C9/C27 difference (324 versus 333 m²).
Heldout A: 19 exact agreements and one C27/C36 difference (72 versus 81 m²).
Thus heldout MAE = 9/20 = 0.45 m² is an average across candidate totals. It is
not 0.45 m² spatial resolution; a 3 m grid cell represents 9 m². The cause of
either one-cell discrepancy cannot be determined from aggregate tables.

Perfect heldout score rank agreement does not mean identical score values
(MAE is nonzero), 100% accuracy, independent validation of all four terms, or
global recall over 630. V is shared and N is constant zero across the rule
candidates. A and H are the independently compared light-response quantities.

## 4. TopK and p-value reporting

The G1 primary TopK rule is descending metric then **natural numeric pair
order**, selecting exactly K from each stated cohort. Top3/5/10 overlaps under
this rule are 3/3, 5/5 and 10/10 for both A and score in both cohorts. These are
within-cohort sets, not recovery of the global best 630 candidates.

The heldout area Top5 result is sensitive to ties:

| Rule | 2.5D set size | HB set size | Intersection | HB-set recall |
|---|---:|---:|---:|---:|
| G1 natural numeric pair order | 5 | 5 | 5 | 1.0 |
| Lexicographic pair order | 5 | 5 | 5 | 1.0 |
| Legacy stable source/sample order | 5 | 5 | 4 | 0.8 |
| Include every tie at Kth threshold | 6 | 7 | 6 | 6/7 |

Retain and label the legacy 0.8. The new 1.0 reflects a declared tie rule, not a
changed model. Full set membership, K=3/5/10, and H comparisons are in
`topk_tie_audit.csv`. Tie-inclusive denominators use the actual HB set size.

SciPy's asymptotic Spearman routine returns floating 0 for perfect heldout
score ranks. The machine value is retained for audit but displayed as
`NUMERICAL_ZERO_NOT_EXACT_ZERO`, never mathematical p=0. As an optional exact
calibration under an explicitly hypothetical exchangeable rank-permutation
null, two perfectly ordered, untied lists of length 20 have two-sided
p=2/20!=8.22063524662433e-19. This conditional calculation is not a claim that
the coverage sample is random or supports population-level inference. Other
asymptotic p-values are preserved in `same_metric_agreement.csv`; small N and
ties make their asymptotic interpretation an additional limitation.

## 5. Time, solar algorithms and weather semantics

The archived solar table has 16 active half-hour samples, from 08:15 through
15:45 at UTC+8 on 2026-12-21. Each carries 0.5 h: total weight is 8 h, while
endpoint span is 7.5 h. Describing the samples as bin centers for 08:00–16:00
is plausible but is not yet confirmed against actual historical recipe/WEA
inputs. Do not silently substitute this as an established protocol.

All saved elevations are positive: minimum 16.374576590156014°, maximum
41.979258601574166°. Saved 3D directions have unit norm to 1.11e-16. A new
solar-only diagnostic using pvlib 0.16.1 reproduces the saved elevations to
7.11e-15°. Current Ladybug-core 0.44.62 reconstruction at the same month/day,
local time, latitude 24.55°, east longitude 118.03°, UTC+8 and north=0 differs
by at most 0.024220707274100306° elevation and 0.03797228897724381° azimuth.
This Ladybug month/day path uses internal non-leap year 2017; pvlib receives
2026 explicitly. These are current installed-algorithm reconstructions, not
observed historical HB effective rays. They do not establish the cause of
the area/mean-gain differences or the adverse stepback result.

Current source writes WEA using constant DNI=1000 W/m² and DHI=0, and constructs
Ladybug DateTime with month/day/hour/minute only. This is a geometry/DSH
calculation carrier, not measured weather or annual climatic validation.
The saved solar table and current function use different column schemas;
the successful pvlib numerical reconstruction is useful evidence but does
not replace matching the actual solver vectors, signs and time mapping.

The latent night integration defect is **reproduced**: skipping an elevation
<=0 leaves all blockers zero, and legacy `hours_from_blocked` counts that slot
as visible. A single 30-minute night slot returns 0.5 h; a masked reference
returns 0 h. The saved 16-slot table contains no such slot, so this defect
does not by itself establish contamination of these frozen results. The
audit does not silently modify production code or claim this defect fixed.

Needed for actual equivalence: frozen WEA/hours and recipe inputs, effective
HB sun vectors, per-point/per-time visibility outputs, baseline and candidate
sensor IDs/coordinates, and the corresponding solver/version provenance.
These remain private-run inputs and must not be uploaded as raw GitHub data.

## 6. Executed evidence and remaining gate

- `execution_01.log`: aggregate recomputation and latent-night diagnostic,
  exit 0; `pytest_01.log`: 15 newly executed tests passed.
- `execution_02.log`: same audit with recorded solar-algorithm reconstruction,
  exit 0; `pytest_02.log`: 15 newly executed tests passed in 0.85 s.
- Tests cover immutable sample bytes/order, disjoint cohorts, complete pairs,
  formula/zero-range/N-weight invariance, deterministic/tie-inclusive TopK,
  nonzero interpretation of floating-zero p, solar daytime/weight count, and
  explicit reproduction of the latent night defect.

Passing these tests establishes statistical/code checks at their stated scope.
It does not resolve the missing real geometry, adverse rays or matched runtime
experiment, and cannot turn `EVIDENCE_READY_FOR_WEB_REVIEW` true by itself.
