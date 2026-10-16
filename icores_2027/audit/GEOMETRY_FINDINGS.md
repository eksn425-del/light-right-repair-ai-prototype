# G2 geometry and monotonicity audit

Status: source/synthetic counterexamples executed; real-site adverse points UNRESOLVED.
No real footprint, original 2,031-row sensor ordering, historical model/binary visibility
or Raytrace replay has been inferred, reconstructed from images, or substituted.
`EVIDENCE_READY_FOR_WEB_REVIEW` must remain false.

## What was executed

`icores_2027/scripts/geometry_audit.py --synthetic` executes the unchanged AST bodies
of `building_shades`, `prism_shades`, `face` and the height helper from
`research_reproducibility/src/legacy_route_b/route_b_prepare_hb_batch.py`. Runtime
filesystem side effects are excluded; the exact emitted prism arguments and actual
Honeybee/Ladybug roof boundaries are inspected. Production source is unmodified.
The protocol is the committed `ae7483ca493768e23a19cf402446c54d6f6c95ef` version.
Source SHA256s, full synthetic fixture definitions and run/config/input identities
are in `runs/geometry_20261016/geometry_manifest.json`.

All geometry is in metres; protocol tolerances are retained: coordinate 1e-7 m,
height 1e-9 m, outside area 1e-8 m² absolute / 1e-10 relative, volume 1e-7 m³.
A section fails containment when outside area exceeds max(absolute tolerance,
relative tolerance × baseline section area). Both absolute and relative areas
are reported. Union volumes integrate Boolean-unioned polygon sections between
all z breakpoints, including overlapping components; summed part volume is not
used as a substitute. Invalid shapes are rejected, never silently buffer(0)-fixed.

## Findings and evidence classification

### GEOMETRY_BUG_CONFIRMED, synthetic/source scope: centroid scaling can add mass

At 12 m height, the actual production stepback on the fixed concave U fixture
has 5.2350903074 m² of upper footprint outside the original, or 7.27095876% of
original footprint area. The added outside volume is 47.1158127665 m³. Its net
removed volume is still 216 m³; matching net volume does not establish inclusion.
Rectangle and disjoint-multipart fixtures are contained at this height.

Seven synthetic rays that were visible in the baseline become blocked by this
production roof/wall envelope. These are deliberately targeted unit-test probes
at an added-geometry patch with 89° elevation, not estimates of site frequency or
rays from the registered winter-solstice analysis. Each adverse ray is recorded
with fixture sensor/sample IDs, blocking prism and ray height in
`ADVERSE_RAY_AUDIT.csv`. The geometric ray interval test is not a Radiance run.

### GEOMETRY_BUG_CONFIRMED, synthetic/source scope: holes are lost in HB faces

For an outer 10 × 10 m polygon with a 4 × 4 m courtyard, `prism_shades` emits a
100 m² roof and four exterior walls; the polygon area is 84 m². The courtyard roof
hole and its four inner walls are omitted. A hole-aware wrapper emits an 84 m²
roof, bottom and both wall rings (10 faces total).

The distinction between intended polygon layers and actual emitted faces matters:
centroid-scaling the polygon with its hole adds 5.3333333333 m² within the original
courtyard. But the actual production baseline already fills that courtyard, so
that intended-layer violation alone does NOT prove an adverse ray relative to the
emitted baseline. The audit therefore reports canonical layer sections and the
separate envelope inferred from actual production roof/wall faces. No historical
HB adverse point has been assigned to this bug.

For this fixture, the reported rule-based removed volume is 252 m³. The actual
emitted roof/wall prism envelope loses 300 m³, because its baseline and modified
courtyard footprints are filled. `emitted_envelope_*` columns are that explicit
prism-envelope calculation with ground closure implied, not a measured Radiance
mesh volume. Unprefixed volume columns describe polygon layers. This distinction
also applies to the rule-flat fixture.

### GEOMETRY_BUG_CONFIRMED, synthetic/source scope: face errors are swallowed

The actual `face` function returns None for a two-vertex invalid face. Callers
silently omit it. `safe_face` raises `GeometryAuditError` with building/face ID and
exception details, validates finite vertices, nonzero area, planarity and
self-intersection. `safe_prism_shades` preserves holes and constructs all rings.
It is an audit-only candidate wrapper, not a silent production replacement.

### GEOMETRY_BUG_CONFIRMED, synthetic/source scope: lower area-fraction clamp

A 100 m² rectangle of height 4.01 m has a recorded target removal of 100.25 m³,
but the legacy 0.05 minimum upper-area fraction yields actual layer removal
95.95 m³. This 4.30 m³ discrepancy occurs even without holes or concavity. None
of the available canonical building heights lie in the affected (4, 4.07142857) m
interval under the registered rule; this test does not establish contamination
of the current site.

### MAPPING_OR_NUMERIC_ISSUE, code-domain scope: nighttime aggregation

Using exact production `precompute_blockers` plus `hours_from_blocked`, one
below-horizon sample yields no blockers and then counts as 0.5 h visible daylight.
The new harness explicitly masks nonpositive-elevation samples. The available
archived solar table has 16 positive elevations (16.37457659° to 41.97925860°), so
this bug is not shown to contaminate that vector. Historical recipe/WEA/output
column correspondence is still unverified. Its archived columns differ from the
2.5D generator API; no silent vector-schema equivalence is assumed.

Sensor matching validates unique IDs, finite XYZ, identical ID sets and coordinate
agreement before returning a reorder map. Tests reject duplicated IDs, missing
IDs, coordinate reassignment and NaNs. Equal row counts alone never establish
mapping equivalence.

## Candidate repair, explicitly unvalidated

`contained_stepback_v2` intersects each production upper polygon with the original
footprint, retains valid polygon components, and uses hole-aware fail-fast faces.
All four synthetic topology fixtures satisfy containment. On the U fixture it
removes 263.1158127665 m³, versus the old 216 m³ target. On the courtyard fixture
it removes 300 m³ from the canonical hole-preserving baseline, versus target
252 m³. It is not volume-matched and does not silently redefine the original
design intent. A repaired baseline is also necessary if real baseline face
emission has lost holes. Same-config baseline/candidate HB recomputation and
author review remain mandatory before any real-site repair claim.

## Real-scene blockers and affected claims

The five registered pairs each have BLOCKED rows with blank numerical fields in
`GEOMETRY_MONOTONICITY.csv`, `ADVERSE_RAY_AUDIT.csv` and
`runs/geometry_20261016/design_translation_recheck.csv`. Blank means unavailable,
not zero. The original four worsened points / 9 m² newly low area remain
UNRESOLVED. Do not describe them as a genuine design trade-off until their exact
geometry, ID/XYZ alignment, time columns and blocking faces are checked.

Claims of contained translation and measured volume matching are not supported
by the legacy code in general. Whether each of the five real cases is affected
is unknown. If real holes or dropped faces altered the shared baseline, expand
the correction scope to all baseline-dependent HB comparisons, including the
curated 23 and held-out 20; do not selectively retain contaminated conclusions.
The current audit confirms a need to check that scope, not that all old results
are already proven wrong. `LEGACY_REPRODUCED_AND_EXPLAINED` is not assigned to
any real case.

## Reproduction and output meaning

- Python: use the isolated environment recorded in the parent capability audit.
- Run `python icores_2027/scripts/geometry_audit.py --synthetic`.
- Run `python -m pytest icores_2027/tests/test_geometry_ablation.py -q`.
- Initial pytest log is preserved; its three integration failures were missing
  in-development harness imports, not failed physical assertions.
- Real geometry-only entry point: `geometry_audit.py --real-manifest <private.json>
  --output-dir <authorized-private-output> --run-id <new-real-run-id>`. The shared strict loader verifies
  hash, building/sensor identities and registered input semantics first. This
  entry point does not claim to replay historical HB visibility.
- `code_commit` is the committed protocol/base tree; new wrapper source hashes
  disambiguate execution until the parent records the final evidence commit.

Matched A/B output is separately gated by real input availability. Synthetic
A/B equality is regression evidence only; it must not yield a site speedup claim.

## Executed final validation and G3 readiness

The timestamped final run at 2026-10-16 05:37:22–05:37:23 UTC completed **60 passed**
with exit code 0. `pytest_final.log` retains actual output; `test_execution.json`
records Python/package versions, platform, timestamps and exact test/wrapper
hashes. The initial three missing-module integration failures are retained in
`pytest_initial.log`, followed by passing integration/final logs.

Coverage includes actual canonical attributes yielding 36 eligible buildings and
the exact 630 unique registered pairs, production strict booleans and resolved
configuration, four footprint topologies, overlapping-volume union, face failure,
ID/XYZ matching, actual production nighttime counterexample, fixed safe night
masking, A/B equality and intentional corruption detection, real-input refusal,
and forbidden synthetic speedup. Four additional tests reproduce frozen scores
at registered 5/20/60/630 prefixes using one hash-verified full630 normalization.

`runs/geometry_20261016/ablation_synthetic_equivalence.csv` is the three-candidate,
three-sensor fixture from `tests/test_geometry_ablation.py::ablation_fixture`,
evaluated by the same public `evaluate_method` and `compare_results` APIs tested
there. All pointwise/metric/score errors are zero and ranks/Pareto flags agree.
It carries an independent synthetic input hash and deliberately blank speedup.
It is not a measurement of the real site's computational speedup.

The real G3 runner uses the exact production AST intersection primitive for both
methods, preserves A's ordinary first-blocker short-circuit, independently reloads
and precomputes for each repetition, includes B precompute and output I/O in total,
and applies fixed full630 score bounds without clipping or outcome-based refits.
All real 5/20/60/630 timing, equivalence and speedup records are BLOCKED and blank.
The harness has a portable optional Unix-memory import and labelled RSS fallback;
Windows execution has not been tested. Historical HB binary-to-ray orchestration
is not implemented by either harness and remains a separate local follow-up.
