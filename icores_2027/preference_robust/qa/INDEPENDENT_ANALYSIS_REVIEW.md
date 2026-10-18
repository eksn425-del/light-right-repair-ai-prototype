# Independent methodological and implementation review

Reviewer: independent analysis QA worker. Review began 2026-10-18 after the coordinator confirmed protocol freeze commit `cff3e81eebf93a16df6da8a21fe735c1554a5a8f`. No protocol changes or outcome-driven selection changes are authorized by this review. Repository is a cloud file snapshot without local Git metadata; remote freeze confirmation is supplied by the coordinator.

## Initial frozen-protocol review

No mathematical blocker found in the frozen protocol.

- The three utility directions are correct: maximize area improvement and daylight-hour gain, minimize nominal volume loss through `1−V_norm`.
- IID Dirichlet(1,1,1) is uniform area measure on the simplex. Sorting these draws descending is uniform on the ordered sector by symmetry. Rejection from that distribution produces the declared uniform local intersection.
- Training selection, independent test, replication, and deterministic stress grid are separated in the specification. Grid outcomes must never reselect the shortlist.
- The greedy objective is sampled maximum absolute-utility regret, with mean regret then numeric pair ID as tie breakers. It is a heuristic; no global-optimality guarantee follows.
- Fixed-set continuous regret equals `max_i max_w min_s w·(x_i−x_s)` because candidate and weight maximization commute. The candidate-specific LP is valid with unrestricted t and correct weight constraints.
- A subtle LP validation pitfall was communicated to the analyst before implementation review: each candidate-specific LP objective should be checked against its own `min_s w·(x_i−x_s)`, not the full-universe regret at that witness. Full regret agreement is required at the globally maximizing witness.
- Rank ties, utility winner coverage, observed versus continuous maxima, and conditional Monte Carlo intervals are distinguished. None establish physical-model validity or the probability an architect actually likes a design.
- The frozen documents' pending-freeze status should remain unchanged. The run manifest must record the actual freeze commit.

## Independent input/reference checks

Executed directly against archived CSVs using a separate small Python calculation, not the analyst's functions:

- All six protocol input SHA256 values match.
- All 630 N values equal zero exactly.
- Frozen min–max normalization gives all four raw normalized components in [0,1]; N's zero range yields zero.
- Recomputed versus archived normalized values differ by at most 1.56e−15 (CSV floating-point parsing); historical scores differ by at most 5.56e−16, below the frozen 1e−12 check.
- Recomputed A>0 historical Top-10 is C9,C24; C9,C15; C9,C12; C15,C24; C9,C35; C9,C13; C12,C24; C9,C21; C9,C26; C9,C27, matching the archive's intended baseline.
- Independent synthetic LP sign check: alternatives (1,0,0), (0,1,0), shortlist {(0.4,0.4,0)} on the full simplex gives worst regret 0.6 at the first or second vertex, as analytically required. The selected candidate's own LP has value zero, illustrating the candidate-wise witness distinction above.

## Implementation/results review

Completed against the final reporting-and-signed-delta correction rerun on 2026-10-18. No unresolved scientific or implementation blocker was found within this review's scope. This is a computational and methodological audit, not independent verification of solar physics, geometry, or source measurements.

### Code review

The implementation uses frozen normalization bounds and the unchanged historical Top-10; sorts candidates by natural numeric pair IDs before stable descending utility sorting; implements strict Pareto domination in the correct directions; constructs all three sampling distributions with their frozen seeds; selects solely on the pooled training weights; and leaves test, replication, grid and LP outcomes out of selection. The greedy maximum-regret objective, mean-regret tie breaker and ten additions are implemented as specified. Every LP uses unrestricted t, correct inequality signs and applicable ordered/local constraints. Candidate-specific and global witness checks are separate and mathematically appropriate.

Minor reporting issues found and corrected transparently by the analyst: explicit HiGHS version; accepted rejection-sampling count before truncation; and stratified pooled mean standard errors. The initial affected reporting files/log/manifest are retained under the analysis audit directory. Pooled fixed-count stratified draws should not receive binomial Wilson intervals as though they were IID mixture draws; those intervals were removed. A third reporting correction casts worst-observed ranks to signed floating values before cross-space subtraction, preventing unsigned-integer wraparound. The previous affected cross-space file/log/manifest is retained under `audit/cross_space_signed_rank_correction`. All 5,670 final cross-space rows, including signed worst-rank changes, were independently verified. These fixes do not alter weights, selection, rankings, regret or the frozen protocol.

### Independent executable checks

`qa/independent_checks.py` reads saved inputs and outputs directly, without importing the main analysis script. Its result record is `qa/independent_check_results.json`.

- Recreated every one of the 180,000 weights exactly, including rejection order and local-region center, using the frozen seeds.
- Independently reconstructed both Pareto fronts: 12 AV candidates and 41 AHV candidates. Consequently neither same-k comparator requires padding.
- Verified every full rank-histogram row and column total, every candidate's winner/Top-10 acceptability, average rank and worst observed rank, for all nine space/split combinations.
- Checked 549 sampled scenario Top-10 orders using a separate Python ordering with explicit numeric pair-ID tie breaking. Saved random-sample diagnostics show no exact or near ties at either rank-1 or rank-10 boundaries.
- Exhaustively recomputed all eligible candidate objective values at greedy additions 1 and 10 using all 60,000 training weights; both winning IDs and objective values agree. Other steps were inspected in code and monotonic trace, not independently exhaustively rerun.
- Independently recomputed 3,294 saved scenario/set metrics from weights and archived normalized utilities. Verified all saved set-summary regret/coverage reductions and all paired mean regret differences and standard errors.
- Independently evaluated all 11,340 LP witness objectives and applicable weight constraints. Maximum discrepancy from the candidate-specific LP objective was 4.58e−16. The global maximizing witness agrees with full-universe regret for every set/space.
- Verified every shortlist HB cohort/value and separate rule-level and translated-geometry evidence status against the archived evidence sources. Missing HB values remain missing with status `2P5D_ONLY`, never treated as passed.

### Interpretation findings that must survive manuscript editing

- The preregistered descriptive stable-improvement condition is met through an improvement in the full simplex and equality (zero regret for both historical and robust lists) in the ordered and local spaces. This is not uniform strict improvement across the three spaces.
- Full-space test mean regret is approximately 0.000054 for robust10 versus 0.010759 for historical10. Full-space continuous worst regret is approximately 0.007656 versus 0.246359. These concern fixed archived utilities and declared preference spaces only.
- Top-10 recovery deteriorates for robust10 in every test space: full 0.42248 versus 0.51560; ordered 0.44342 versus 0.89618; local 0.53373 versus 0.89953. This is distinct from winner coverage or regret. The robust set preserves a better best available option across weights while recovering fewer of each scenario's ten highest-ranked candidates. Do not call this general dominance, and do not turn this into an unmeasured geometric-diversity claim.
- Seven robust candidates have archived rule-level HB review; three lack it: C12,C15; C15,C25; C24,C35. Only two robust members carry archived corrected translated-geometry HB checks, C9,C24 and C9,C15. Rule-level review does not validate the remaining translated designs.
- The first ten additions never reach zero maximum training regret. The algorithm is a greedy sampled minimax heuristic; the LP audit certifies fixed-set worst regret up to numerical tolerance, not globally optimal ten-candidate selection.
- Rank acceptability and Wilson intervals are conditional numerical integration summaries under the declared weight distributions. They are neither empirical architect-choice probabilities nor uncertainty intervals for physical model correctness.

### Review limitations

This audit does not rerun all ten greedy searches independently, repeat Honeybee/Radiance, establish global shortlist optimality, verify final paper layout, or establish permission to build or alter any real building. It checks the requested computational logic and saved result consistency. The frozen protocol commit is confirmed by the coordinator; this cloud snapshot lacks local Git metadata.


## Final reviewed run identity

- manifest_sha256: `14e2c4d69a771010722f3d42abec33498c0982e16dcfc76f357bb2218d2df690`
- analysis_script_sha256: `bad6fc270e5f34d0de9b59bbbc6fc9917ba01689f2c8b5ea8fe182bde5571e3f`
- protocol_sha256: `e154588c9f3d22c98c9fb632c459c129d50a83ef5108aabd2319289b8b30ebc0`
- freeze_commit: `cff3e81eebf93a16df6da8a21fe735c1554a5a8f`
- manifest_output_hashes_verified: `114`

All 114 output SHA256 entries in the final run manifest were checked against saved files. The final analysis script SHA256 also matches the manifest. This identity distinguishes the reviewed final outputs from the retained earlier reporting versions.
