# Method specification for author and web review

Version: author-local evidence completion, 2026-10-17. This is a methods/evidence
specification, not a submission-ready manuscript. Frozen aggregate statistics
remain in `runs/statistics_20261016`. Completed local input, geometry, solver and
efficiency evidence is under `runs/local_*_20261016`; run IDs retain their start
date. No original20 sample was reselected or re-simulated.

## 1. Decision problem and scope

The case has 45 buildings and a research-defined eligible subset E of 36.
Eligibility uses the source movable/protected flags and height >3 m, with
strict Boolean parsing. It is a modeling constraint, not legal authority to
alter or demolish a building. Let z_i ∈ {0,1} for i in E and require
Σ(i∈E) z_i = 2. Other buildings are fixed. Exhaustively enumerate the complete
set of unordered pairs, |C|=C(36,2)=630, without claiming global optimality
outside this bounded decision universe.

For original height h_i, the selected rule height is

    h_i^r = max(3 m, h_i − min(3 m, 0.25 h_i))
    h_i(z) = (1 − z_i) h_i + z_i h_i^r

Footprints are fixed for the rule candidates. Stepback design translation is
a separate geometry-generation and re-evaluation step; its geometry and actual
removed volume cannot be assumed equivalent to uniform reduction.

## 2. Analysis domain and direct-sun-hours estimator

The frozen protocol uses a 3 m horizontal grid, 2,031 fixed receiving points
at z=0.1 m, north=0, latitude 24.55°N, longitude 118.03°E, local timezone
Asia/Shanghai (UTC+8), and date 2026-12-21. The 16 listed times are 08:15,
08:45, …, 15:45. With weights Δt=0.5 h, maximum accumulated exposure is 8 h.
The 7.5 h endpoint span is not the sum of the integration weights. Actual archived
WEA records, HOY labels, solar-source names and16-column binary visibility
matrices have now been checked across all six original scenes. Each cumulative
result exactly equals its visibility sum times0.5h. Treat these as half-hour
samples centered on08:15–15:45 with total weight8h, not continuous-time precision.

Let d_t indicate an above-horizon sun sample and b_jt(z) indicate occlusion at
receiver j by at least one building. A physically correct discrete estimator is

    D_j(z) = Σ_t Δt_t d_t [1 − b_jt(z)]                  [h]

The active-sun factor must be explicit. The legacy code skips below-horizon
ray construction but omits this factor in its final visible-sample count,
which is a reproduced latent defect. All 16 saved samples are above the
horizon, so this observation alone does not prove error in the frozen run.

The geometric primitive intersects a horizontal ray with a footprint and
uses the first positive projected distance l to test ray height
z_sensor + l tan(altitude) against the relevant building height. The baseline
source ignores distances <=1e-7 m and uses a 1e-9 m height tolerance. The
common coordinate system, footprint validity, holes, component unions,
receiving-point order, ray sign, time vectors and tolerance must be audited
before comparing physical outputs. A correct visibility routine must also
handle receiver/geometry boundary cases explicitly.

All six actual archived WEA files supply constant DNI1000 W/m² and DHI0 to
direct-sun-hours: an analysis carrier, not measured meteorology. Actual HB
effective rays are now mapped and shared across those scenes. They differ
slightly from saved pvlib rays; `historical_solar_mapping.csv` quantifies this.
WEA/HOY lack a calendar-year field: the declared pvlib2026 sequence is not an
identical year-specific astronomical input to the archived Ladybug reconstruction.
Timezone is UTC+8; north0 is a modeling assumption, not newly surveyed true north.
No annual-weather, indoor illuminance, glare or statutory-compliance validation
is established.

## 3. Four metrics, units, normalization and preference score

Let D_j^0 be baseline exposure, τ=3 h, P=2,031, and a=9 m² per grid point.

    A(z) = a Σ_j ([D_j^0 < τ] − [D_j(z) < τ])           [m²]
    H(z) = (1/P) Σ_j (D_j(z) − D_j^0)                  [h]
    V(z) = Σ_i area(F_i) (h_i − h_i(z))                 [m³]
    N(z) = a Σ_j [D_j^0 ≥ τ and D_j(z) < τ]             [m²]

The V formula applies to fixed-footprint uniform-height rule reductions with
correct nonoverlapping area. For translated, overlapping or multipart solids,
use audited union volumes or layered cross-sections and report target versus
actual removed volume separately. A rule formula is not a measurement of an
unverified translated solid.

For q∈{A,H,V,N}, bounds q_min/q_max are fixed from the complete 630 rule
candidates. Define n_q=(q−q_min)/(q_max−q_min), or n_q=0 when the range is
less than 1e-12. Do not refit ranges on HB outcomes or the selected review
subsets, and do not silently clip out-of-range values. The implemented score is

    S(z) = 0.45 n_A + 0.35 n_H + 0.15 (1 − n_V) + 0.05 (1 − n_N).

The coefficients express preferences, not probabilities or learned accuracy.
In all 630 frozen rule candidates N=0. Its normalized value is zero and its
score contribution is a constant 0.05. Changing only its weight preserves
the ranking. The historical NEW_LOW_SENSITIVE scenario also changes A/H
weights and therefore does not isolate N's discriminating power.

Pareto analysis in the existing implementation maximizes A and minimizes V,
with at least one strict improvement for domination. It is a two-objective
front, not a four-objective one. Preference-score rank, Pareto membership,
physical validity and professional acceptability answer different questions.
None replaces design or regulatory review.

## 4. Building-level blocker reuse

For each building i and receiver/time pair (j,t), precompute Boolean blockers
O_ijt at the original height and R_ijt at the rule-reduced height using the
same footprint and ray-intersection primitive. Let C_jt=Σ_i O_ijt. For selected
pair (a,b), update

    C_jt(a,b) = C_jt − O_ajt − O_bjt + R_ajt + R_bjt
    b_jt(a,b) = [C_jt(a,b) > 0].

Use an integer count type wide enough for the building count; do not subtract
in unsigned Boolean storage. Apply the same sun-active mask to every candidate.
The identity is exact when each building's contribution is independent,
unchanged footprints/heights of unselected buildings remain fixed, and all
inputs and tolerances are identical. It does not establish equivalence with
HB, translated geometry, reflections, materials or other solar phenomena.

Pseudocode:

    load and validate ordered sensors, footprints, heights and sun samples
    compute O and R using the common geometric primitive
    C = sum O in a safe integer type
    compute baseline DSH using C and the active-sun mask
    for every eligible unordered pair (a,b):
        updated = C − O[a] − O[b] + R[a] + R[b]
        DSH = weighted visible samples with active-sun mask
        derive A, H, V and N
    fit normalization bounds over the full declared candidate universe
    compute preference scores, deterministic ranks and A/V Pareto set
    save aggregate outputs and provenance

This is an application-specific exhaustive screening implementation with
precomputed occlusion reuse, not a newly established general OR algorithm.

## 5. Complexity, storage and fair efficiency evaluation

Let B be building count, P receiver count, T sun-sample count, M candidate
count and G the cost of one ray–footprint intersection (dependent on polygon
complexity and spatial indexing). Without cross-candidate blocker reuse,
the candidate intersection work is on the order of O(MBPTG). Building-level
reuse costs O(BPTG) for preparation and O(MPT) for candidate updates/metrics.
Baseline work and shared input/solar preparation must be handled consistently.
These expressions do not turn G into a constant independent of geometry.

Two uint8 blocker arrays require 2BPT bytes. For B=45, P=2,031 and T=16 this
is 2,924,640 bytes (about 2.79 MiB), excluding geometry, indexes, solar data,
safe integer count arrays, per-candidate temporaries and Python overhead.
Streaming candidate DSH avoids retaining a full M×P×T result cube. Score
ranking adds O(M log M); the present direct Pareto scan adds O(M²) comparisons.
These costs and I/O cannot be omitted from end-to-end reporting.

The G1 matched comparison specifies:

- A recomputes geometric intersections for each candidate without cross-candidate
  blocker reuse; ordinary input/solar preparation and legitimate optimizations
  remain available.
- B includes precompute plus updates; warm-cache evaluation alone is not its
  total time.
- Same geometry primitive, tolerances, hardware, threads, ordered candidates,
  metrics and phase accounting on both sides; compare pointwise DSH as well
  as A/H/V/N, scores and ranks before reporting speedup.
- Nested fixed prefixes m=5/20/60/630, at least three matched repeats, and the
  shared declared warm-up policy. The pilot chooses feasible runtime scale,
  not favorable outcomes. Full A at 630 is required if three repeats fit the
  declared 12-hour budget; otherwise only measured matched subsets support a
  speedup claim.

The real-input comparison is complete:5/20/60/630 candidates, three matched
repeats at each scale. All pointwise DSH, A/H/V/N, score, rank and A/V Pareto
checks pass. At630, median A=11608.1830554s and median B=24.0371276s, including
precompute; the measured ratio is482.9272136. These are two specific single-thread
Shapely implementations on the same frozen canonical input, not every spatially
indexed implementation, commercial CAD tool or HB. A retains first-blocker
short-circuiting; neither implementation uses a spatial index in this ablation.
Raw repeats, phase costs and environment are retained. Windows RSS is unavailable
and blank/UNKNOWN, not zero or a claimed peak-memory measurement.

The old55.3978s screening median and51.1067s HB scene
median are historical costs with different execution semantics. HB's 53
scenes combine 33 operational and 20 research-only scenes, with historical
worker settings initial=2 and later=4. The 8.94-hour full-630 HB estimate is
an extrapolation, not a completed 630-scene experiment or a fair same-solver
ablation.

## 6. Validation and reporting protocol

Keep curated23 and heldout20 separate. The latter is a frozen, outcome-blind
coverage sample held out from curated review, selected for score-stratum,
volume and ID coverage; it is not an independently sampled population or
different site. Its original byte hash and order are preserved. Archived
execution timestamps report freezing before heldout HB execution; the hash
alone proves no temporal ordering.

Compare A to A, H to H and S to S under the same fixed bounds. Do not compare
the older curated S-rank versus HB-A-rank rho with heldout same-metric rho as
if the model improved. Spearman assigns average ranks to ties. Primary exact-K
sets use descending metric then natural numeric pair order; disclose the
legacy row-order and all-boundary-ties sensitivity. Every TopK result names
its comparison cohort and is not global 630 recall.

Report candidate-level errors with grid scale. For heldout A, 19 pairs agree
exactly and one differs by one 9 m² cell, yielding mean error magnitude
0.45 m² across 20 candidates. This is not sub-grid spatial precision.
Shared V and constant N constrain interpretation of composite rank agreement.
Floating-zero p-values are numerical outputs, not exact probability zero;
the nonprobability sample does not support a population-generalization claim.

## 7. Translation audit and contribution boundary

Under fixed opaque geometry, rays and receivers, deleting a subset of a baseline
solid cannot decrease direct sunlight. Actual historical rtrace now explains the
old C9/C24 four worsened points and9m² newly low-sun area: clear baseline rays
hit C24 upper walls outside its original footprint in the translation. C13/C24
has the same four events. These are erroneous added obstructions, not unavoidable
effects of pure subtraction. Four of five legacy translations fail containment.
The actual canonical site has no polygon holes and every expected roof/wall
exists; synthetic hole/silent-face defects are not demonstrated causes here.

Six controlled legacy replays (baseline plus five translations) reproduce the
original visibility matrices exactly, with all new runs fixed to cpu-count1 and
workers1. Four contained-v2 corrections were then simulated, with unchanged
ordered grid, solar sources and time columns. They have no adverse visibility
events, worsened points or newly low-sun area on this model. C9/C24 low-area
reduction changes342→351m²; C13/C24 changes207→216m². C9/C15 and C6/C33 stay342
and18m². C9/C13 was already contained; its unchanged333m² result is reused, not
an eleventh run. Historical negative outputs are retained. See the paired
`translation_outcome_comparison.csv` and its source hashes.

Actual whole-scene union volumes differ from nominal per-building rule budgets
and across translations. Report both; clipping is not a volume-matched
optimization. No shared receiver/time/parser or missing-face defect was found
in the actual scenes, so this audit gives no basis for replacing or selectively
re-running the frozen20. A newly discovered shared defect would still require
explicit affected-scope review, not selective retention of favorable conclusions.

## 8. Canonical Fidelity and Release Boundary

The frozen canonical geometry is a DXF component-bbox union approximation.
Different IDs may share components and footprints overlap. The archived
OBJ/canonical audit reports discrepancies for important candidates. Experiments
therefore establish reproducible screening/translation behavior conditional on
this model, not as-built accuracy, legal modification permission, construction
feasibility or measured real-street improvement. If boundaries are corrected,
register a new input version and assess affected experiments explicitly; do not
reuse current cohort agreement as validation of different geometry.

Permissible contributions are bounded decision support, frozen same-model
aggregate agreement, actual geometry/ray error diagnosis with a tested correction,
and measured same-primitive reuse efficiency. Web evidence review can proceed
after final delivery gates. Manuscript completion, author approval, acceptance
and submission are separate. Raw geometry, coordinates, WEA and solver files stay
author-local; new figures are aggregate native-vector charts with manifests.

