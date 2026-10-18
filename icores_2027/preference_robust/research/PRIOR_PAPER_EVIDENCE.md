# Prior-paper evidence audit for preference-robust screening

Audit date: 2026-10-18 UTC. Read-only examination of the prior work; no historical paper or experiment edited.

## 1. Materials read and version identity

Read the complete 18-page English PDF `prior-paper/anonymous_regular_submission.pdf` (all pages via text extraction), both complete Chinese manuscripts, the English LaTeX manuscript and included Top-10 material, the prior analysis script, selection protocol, evidence matrix and aggregate tables, recomputation manifest, final QA, author handoff and open items. Also read the new task, root start document, research configuration and historical weight-sensitivity CSV.

The supplied PDF SHA256 is `27f20bc85c92403d24c5567bc55fd3a126603f044c0a2b259af19e0584f5df0f`; the current downloaded `manuscript.tex` SHA256 is `fc4cd28bfac0d5f67e41a39d4c4623148168af3ec8d9440f002afd047286d680`. Both exactly match the archived final QA/handoff and the source hash in both Chinese manuscripts. The PDF title, sections, equations (1)-(11), Tables 1-5, Figures 1-3, eight references and numerical claims correspond to that manuscript. This establishes the supplied final artifact/source version identity through recorded hashes and content, not a fresh recompilation. Remote latest-HEAD verification belongs to the parent task; do not confuse the old reanalysis input commit `5dc805a2962f7f21836b4a4f64a5db3e483958e9` with the final branch HEAD.

The old root `ARCHITECT_DECISION_START_HERE.md` still says the task has not yet produced new experiments/paper; that is stale introductory status. Final handoff says complete for author review, not approved or submitted. Prior technical QA reports 18 pages, 40,926 extracted non-whitespace characters, all 14 fonts embedded and 55 automated assertions, but these do not transfer automatically to the new manuscript.

## 2. Immutable scientific case definition

- 45 canonical building groups; 36 eligible under source movable/protected flags with strict Boolean parsing and height >3 m. Research eligibility is not ownership, legal permission or structural feasibility.
- Choose exactly two distinct eligible groups, hence C(36,2)=630 unordered pairs. All 630 exist, with no duplicate pair identities.
- Selected height: h_rule=max(3, h-min(3,0.25h)); unselected heights and all footprints stay unchanged. This is a finite rule universe, not arbitrary shape optimization or 630 completed designs.
- Canonical footprints are unions of DXF-component bounding boxes. Shared components, overlapping footprints and disagreement with an archived OBJ representation limit fidelity. They are not surveyed/as-built boundaries.
- Receiving grid: 2,031 points, 3 m spacing, 0.1 m height, area weight 9 m². Receivers are outside and off boundaries of the canonical footprints. Actual case has no polygon holes; synthetic hole failures do not establish a defect in these scenes.
- Latitude 24.55 N, longitude 118.03 E, UTC+8, north assumed zero. Declared pvlib date 2026-12-21 is a near-solstice design-day scenario, not observed future weather or demonstrated global worst day.
- 16 half-hour samples centred 08:15 through 15:45, each weighted 0.5 h: total integration weight 8 h, although centre-to-centre span is 7.5 h.
- Direct-sun duration D_j=sum_t delta_t d_t(1-b_jt), with active-sun indicator d_t=1(alpha_t>0). Legacy below-horizon entries could be counted visible, but all frozen 16 samples are above horizon. Do not imply this latent defect invalidates frozen data.
- 2.5D primitive uses first positive projected horizontal ray-footprint distance, compares 0.1+l tan(alpha) to building height; ignores distances <=1e-7 m and uses 1e-9 m height tolerance.
- Direct-sun hours/threshold area are not indoor daylight, annual irradiation/energy, glare or regulatory compliance. Threshold tau=3 h is research-defined.

## 3. Metrics, normalization and exact legacy baseline

A=9 sum_j[1(D0_j<3)-1(D_j<3)] is NET low-sun-area reduction (m²). H=(1/2031)sum_j(D_j-D0_j) is mean duration change (hours), including improvements that do not cross the threshold. V=sum_i area(F_i)(h_i-h_i_rule) is a nominal additive volume proxy (m³); overlaps make it different from whole-scene union-volume change or actual demolition quantity. N=9 sum_j1(D0_j>=3,D_j<3) is newly low-sun area (m²).

Directly checked all 630 aggregate rows: N is exactly zero throughout; 210 rows have A=0. The bounds embedded in `normalization_bounds_json` are:

| Metric | Minimum | Maximum |
|---|---:|---:|
| A | 0 | 396 |
| H | 0 | 0.0635155096011816 |
| V | 387.3824354304028 | 10891.474417736685 |
| N | 0 | 0 |

Use these full-universe bounds, never rounded printed Table 1 bounds, cohort-specific bounds or outcome-adapted bounds. n_q=(q-min)/(max-min), unless range<1e-12, then zero. No silent clipping of out-of-range review outcomes.

Historical score S=0.45nA+0.35nH+0.15(1-nV)+0.05(1-nN). N contributes constant 0.05. The three-dimensional equivalent preference is w0=(9/19,7/19,3/19)=(0.4736842105,0.3684210526,0.1578947368), and S=0.95 U_w0+0.05. Preserve the published S values and order; use U for coherent new cross-preference utilities/regrets. Weights were declared by researchers; no architect elicitation, AHP, learning, optimality or probability calibration established them.

Production sorting: descending S, then descending A, then descending H; residual complete-key tie in the old reanalysis uses stable source-row order. No exact score ties occur in this universe. Top-10 selection filters A>0, then takes ten. Natural numeric pair sorting applies to old cohort exact-K comparisons, not a replacement historical production sort. For new rank distributions explicitly state the candidate domain, tie convention and handling of A=0; do not silently remove 210 rows from an analysis advertised as all 630.

Historical Top-10, in immutable order:

| Rank | Pair | A | H | Nominal V | S (rounded) | A/V front | Translation |
|---:|---|---:|---:|---:|---:|---|---|
| 1 | C9/C24 | 396 | 0.04874 | 5551.333 | .84486 | yes | corrected |
| 2 | C9/C15 | 351 | 0.03496 | 3127.755 | .75237 | yes | corrected |
| 3 | C9/C12 | 306 | 0.04357 | 4030.543 | .73582 | no | missing |
| 4 | C15/C24 | 243 | 0.05367 | 4016.480 | .72005 | no | missing |
| 5 | C9/C35 | 297 | 0.04481 | 5303.320 | .71420 | no | missing |
| 6 | C9/C13 | 333 | 0.03028 | 2975.156 | .70832 | yes | unchanged reused |
| 7 | C12/C24 | 198 | 0.06228 | 4919.268 | .70350 | no | missing |
| 8 | C9/C21 | 333 | 0.03250 | 4251.977 | .70229 | no | missing |
| 9 | C9/C26 | 315 | 0.03520 | 3906.127 | .70170 | no | missing |
| 10 | C9/C27 | 324 | 0.03890 | 7340.881 | .68323 | no | missing |

Use CSV precision for every regenerated numerical table; illustrative rounded fields above do not replace source CSV. All ten have archived RULE-level HB review. C9/C27 is the sole Top-10 A mismatch: screening 324 versus HB 333 m². C9/C24 heights 12,9 become 9,6.75 m.

Historical sensitivity CSV provides six isolated scenarios, not a weight-distribution analysis. Top-10 overlaps with baseline: AREA_HEAVY 9, GAIN_HEAVY 6, VOLUME_SENSITIVE 9, NEW_LOW_SENSITIVE 10, BALANCED 9. NEW_LOW_SENSITIVE changes A/H as well as N; its rank changes cannot be attributed to N. GAIN_HEAVY ranks C9/C15 tenth and C9/C13 fifteenth, while C9/C24 stays first in all six reported scenarios. Do not generalize that winner invariance to the full simplex before new analysis.

## 4. Pareto and set-comparison traps

Old front maximizes A and minimizes V, requiring at least one strict improvement. It has 12 members, all A>0:
C9/C13, C9/C15, C9/C24, C9/C25, C9/C29, C13/C15, C13/C25, C13/C29, C15/C26, C15/C28, C15/C29, C25/C29.

Three overlap historical Top-10: C9/C24, C9/C15, C9/C13. A/H/V preference ranking must not be prefiltered to this A/V front: A/V-dominated options can be valuable for H. C12/C24 is an explicit example of high H but modest A. Build the three-objective front separately. Nonnegative linear utility can justify discarding three-objective dominated candidates for the best-in-set utility objective (subject to ties), but NOT discarding them before calculating complete 630-candidate rank acceptability; dominated options can still rank in the top ten.

Full fronts have different cardinalities from ten. Report unrestricted fronts descriptively, but compare ten-candidate sets at identical cardinality and evaluation scenarios; specify the selection/compression rule for each Pareto-restricted ten. Do not attribute the quality of an entire larger front to a ten-item shortlist. Do not optimize and evaluate on the same random weight draws. Freeze prior to seeing results: distributions, seeds, sample counts, domains, tie rules, local radius, optimization objective, scenario mixing, evaluation metrics and convergence checks.

Preference acceptability is a fraction under an assumed weight distribution, not the probability real architects favor a candidate. Preference robustness does not test uncertainty in geometry, weather, measurements or physical modeling. A/H correlation reflects related but distinct summaries: threshold transitions versus average exposure change. High correlation does not by itself justify deleting either objective, and weighting both entails an explicit modeling preference.

## 5. Forty-three rule HB records: provenance and join warning

Historical curated23 = Top10 union nonzero A/V front union C6/C33 and C13/C24 (historical) union C3/C19 and C26/C35 (reference interventions). Count 10+12+2+2-3=23. Reference interventions are not the no-intervention baseline. Curated selection is purposive, not random.

Frozen coverage20 is disjoint from curated23. It was selected for score strata, volume and identifier coverage without HB outcomes, on the same site; not a probability sample or independent external validation. Archived timestamps report freezing before HB execution; hashes alone do not prove that chronology. Preserve identities and results; do not reselect/rerun only convenient cases.

Directly checked evidence matrix status counts: 23 `ARCHIVED_RULE_HB_REVIEWED`, 20 `ARCHIVED_COVERAGE20_RULE_HB_REVIEWED`, 587 `2P5D_ONLY`. Hence 43 distinct rule-reviewed pairs, 6.8254% of the 630, but report curated and coverage agreement separately. Coverage pairs:
C9/C32, C7/C15, C24/C39, C12/C44, C21/C30, C35/C44, C5/C12, C26/C29, C27/C36, C20/C22, C4/C13, C28/C38, C18/C33, C32/C40, C16/C39, C10/C25, C8/C17, C11/C19, C6/C31, C3/C37.

**Join trap:** old `decision_evidence_matrix.csv` has a correct reviewed STATUS for all 20 coverage rows but NaN in `HB_rule_low_sun_area_reduction_m2` for all twenty. Its script fills this numeric field only from curated23. NaN in that convenience table is therefore not proof of no HB review. To obtain actual coverage numeric HB outcomes use `icores_2027/runs/statistics_20261016/comparison_values.csv`, joined by pair_key, not row position. If this source is absent from the downloaded subset, retrieve it or disclose unavailable numeric values; never impute them from screening. Preserve separate rule-HB and translated-geometry evidence fields.

Historical descriptive same-metric results:

| Cohort | Metric | Spearman | MAE | Exact |
|---|---|---:|---:|---:|
| curated23 | A | .999258 | .391304 m² | 22/23 |
| curated23 | H | .991597 | .001177 h | 3/23 |
| curated23 | S | .999012 | .006933 | 3/23 |
| coverage20 | A | .997668 | .450000 m² | 19/20 |
| coverage20 | H | .999624 | .000295 h | 9/20 |
| coverage20 | S | 1.000000 | .002139 | 9/20 |

Area MAE .45 is one 9 m² discrepancy divided by 20, not sub-grid accuracy. Score rank correlation 1 is not exact scores or 100% accuracy. V is shared across routes; N is constant. Average ranks handle Spearman ties. Coverage exact-five A overlap changes .8 to 1.0 with natural-pair rather than source-row tie handling; retaining all boundary ties yields six and seven candidates. This is a set-definition effect, not a physical improvement. Older score-versus-area correlations are not comparable to current same-metric agreement as evidence of progress. Cohort top-K overlap is not full-universe recall.

Archived HB/Ladybug effective rays differ from saved pvlib rays. WEA uses constant DNI=1000 W/m² and DHI=0 as a direct-sun carrier, not measured meteorology; WEA/HOY records have no year field. All 16 visibility columns and 0.5 h integration were reconciled within the historical scenes. This actual-route agreement is distinct from matched-primitive equivalence.

## 6. Translation evidence is a separate intervention

Pure subtraction satisfies Omega_c subset Omega_0. With fixed rays/receivers an unobstructed baseline ray cannot become obstructed by a subset: sampled exposure is nondecreasing. An adverse event is a reason to investigate geometry/mapping/computation, not an automatic natural cost of subtraction.

Five historical translated pairs: C9/C24, C9/C15, C9/C13, C13/C24, C6/C33. Four fail containment; C9/C13 already passes. Six controlled scene replays (baseline plus five) reproduce old visibility exactly, then four corrected scenes are separately simulated: TEN scene runs, not eleven, not 630. C9/C13 unchanged result is reused, not rerun as a correction.

C9/C24 and C13/C24 each have four worsened receiving points and 9 m² newly low-sun area in legacy translations. Actual rays hit upper C24 walls outside the original footprint. Synthetic hole/silent-face bugs are not asserted as the cause: actual case has no holes and six archived face dictionaries regenerate exactly. All four contained corrections have no adverse sampled visibility, worsened points or new low-sun area on fixed model/rays/grid.

| Pair | Legacy translated A | Corrected/reused A | Nominal rule V | Rule union delta V | Legacy union delta V | Corrected/reused union delta V |
|---|---:|---:|---:|---:|---:|---:|
| C9/C24 | 342 | 351 | 5551.333 | 5470.406 | 5259.615 | 5474.582 |
| C9/C15 | 342 | 342 | 3127.755 | 3065.681 | 2927.693 | 2937.931 |
| C9/C13 | 333 | 333 | 2975.156 | 2918.246 | 2785.422 | 2785.422 |
| C13/C24 | 207 | 216 | 3863.880 | 3726.044 | 3534.257 | 3749.224 |
| C6/C33 | 18 | 18 | 5583.055 | 1909.864 | 2553.509 | 2554.767 |

Rule A=396 for C9/C24 is not corrected translated A=351. All top-ten rules have HB records, but only C9/C24 and C9/C15 have corrected-translation checks, C9/C13 has unchanged reused translation, seven lack translation evidence. Across the complete universe only these five historical pairs have these translation results. New robust shortlist status must be joined by pair and geometry level, never inferred from similar rank or membership.

Signed scene-union volume reduction |Omega0|-|Omegac| equals removed baseline volume minus outside-added volume for a noncontained scene. It is not gross material removed. Containment correction is not volume matching, and none of these proxies establish engineering costs or construction readiness.

## 7. Efficiency evidence to retain without recentering the paper

Reuse precomputes original/reduced blockers O,R; signed counts update C_ab=C-O_a-O_b+R_a+R_b and visibility is 1(C_ab>0). Algebraic equivalence assumes same primitive/vectors and unchanged other geometry. Boolean/unsigned subtraction is unsafe. It does not prove equivalence to another ray tracer or footprint-changing translation.

Repeated-primitive complexity O(MBPTG), reuse O(BPTG)+O(MPT); sort O(M log M), direct Pareto scan O(M²). Two byte blockers occupy 2BPT=2,924,640 bytes (~2.79 MiB) for 45x2031x16, excluding all other arrays/runtime overhead; not measured peak-memory reduction.

Historical Windows 11, Python3.12.2, NumPy2.4.6, Shapely2.1.2/GEOS3.13.1, pvlib0.15.2; CPU recorded only as AMD64 Family25 Model80 Stepping0, 16 logical CPUs available. Matched timing uses one process/thread (do not inherit cpu_count:4 from the broader research YAML), no spatial index, three measured repeats at fixed nested prefixes, warmups excluded; B includes independent precomputation. Times are actual measured, including full 630 for A:

| M | A median s | B median s | ratio |
|---:|---:|---:|---:|
| 5 |109.706|23.359|4.697|
|20|373.812|23.418|15.963|
|60|1085.983|23.975|45.297|
|630|11608.183|24.037|482.927|

All 12 scale/repeat comparisons pass pointwise and aggregate equivalence. Ratio is only these implementations, not a Honeybee benchmark, indexed/compiled-solver benchmark, or measured human workflow saving. No verified commercial CPU model or RSS measurements; unknown is not zero. Six saved full630 A/B aggregates were byte-identical in the prior archive audit; reanalysis score discrepancy 5.5511e-16. Historical normalization-source hash mismatch was transparently amended before benchmark; numeric bounds/candidates were not outcome-retuned. 112 passing integrated software tests support regression coverage, not site ground truth.

## 8. Required interpretation in the new paper

New work may claim new aggregate preference analysis and auditable shortlist selection, with measured results determining its conclusions. SMAA, robust ordinal regression and minimax regret are existing theories. Greedy set construction is a heuristic unless a global certificate is actually supplied. Observed maximum sampled regret/rank is not worst case over a continuous domain unless separately proved/certified. An assumed distribution over weights is not elicited architect belief; ordered sunlight-priority weights are a study scenario.

Independent construction/evaluation draws address selection optimism but do not create independent physical/site validation. Missing HB on new selected candidates remains missing. Agreement of old review cohorts cannot certify all newly favored low-volume/high-H regions. High preference robustness cannot repair approximate geometry, resolve legal rights, prove construction feasibility, or guarantee physical accuracy. A negative result or no stable regret advantage should be reported, not hidden by tuning assumptions or changing baselines.

Raw CAD/DXF/SKP/OBJ, receiver coordinates, WEA, HB scenes and Radiance intermediates are restricted and unavailable for cloud physical reruns. The current task can faithfully reanalyse candidate aggregates and archived results; do not label it new HB simulation. Keep original 20 frozen candidates, historical failures and old manuscript intact. Restrict public paper figures to aggregate evidence without site geometry/coordinates.

Author decisions still outstanding: authorship/order/consent, data/text rights, prior publication and simultaneous submission, competing-interest/funding declarations, independent content review, AI disclosure/placement versus double-blind requirements. Prior AI disclosure is honest substantial assistance, exact old underlying model unrecorded, author approval not asserted. Technical readiness is not authorization to submit, pay, fill author identity, accept declarations, or make private repository public.

## 9. Sources within the downloaded repository

Primary scientific text: `icores_2027/architect_first_cloud/paper/manuscript.tex`, `top10_table.tex`, `top10_interpretation.tex`, both Chinese manuscripts; supplied final English PDF.

Primary aggregate input: `icores_2027/runs/local_ablation_20261016/aggregate_B_m630_r1_run.csv` (SHA256 `b07225c7f0bf43348a867934a7b71fb097d30975dcef8f571a5ccc0f0ff96387`).

Prior computed evidence: `analysis/selection_policy_frozen.md`, `recompute_candidates.py`, `RECOMPUTATION_CHECKS.json`, `decision_evidence_matrix.csv`, `selected_23_provenance.csv`, `top10_rule_candidates.csv`, `pareto_rule_candidates.csv`, `same_metric_recomputed.csv`, `historical_runtime_rechecked.csv`, `historical_translation_rechecked.csv`; paths relative to `icores_2027/architect_first_cloud/`.

Historical preferences: `research_reproducibility/configs/research.yaml`, `research_reproducibility/results_public/weight_sensitivity_summary_v2.csv`.

Version/readiness: prior `paper/QA_REPORT.md`, `handoff/FINAL_STATUS.json`, `handoff/WEB_AUTHOR_HANDOFF.md`, `handoff/OPEN_ITEMS.md`.
