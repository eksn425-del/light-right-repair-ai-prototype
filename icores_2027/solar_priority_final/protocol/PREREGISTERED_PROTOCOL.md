# Solar-priority decision experiment: frozen protocol candidate

No new outcome has been computed. Commit JSON and this document before execution. JSON is the complete authoritative specification.

## Research question
Sunlight improvement comes first, nominal intervention second. Test whether ten options can retain more preference-specific highly ranked alternatives than historical weights while preserving best-option access. A null finding is valid.

## Fixed design
630 archived alternatives; frozen global normalization; N must be verified zero. Three weight supports: ordered wA>=wH>=wV; solar70 wV<=.30; solar80 wV<=.20. Three additional layered A>=90,180,270 m2 scenarios use solar70 and its exact same draws. Thresholds are study scenarios, not expert or regulatory limits.

20,000 train/test/replication draws per support, PCG64 seeds2026101901–03 /1911–13 /1921–23. Only training can select candidates. All methods use10slots. The four unchanged previous lists are primary baselines; layered adaptations are expressly labeled and compared in the same eligible universe.

## Two mathematically transparent selectors
Coverage10 maximizes mean Top10 intersection recovery by selecting the ten largest training Top10 probabilities, an exact solution of a modular objective. ProtectedCoverage10 imposes inclusion of every training rank-one identity before filling by that same objective. If more than ten winners exist the constrained method is infeasible, not silently relaxed. Neither is a new general algorithm.

## Evaluation and decision rule
Report held-out winner coverage, mean/worst regret, Top10 recovery, A/H/V distributions,10block training stability,HB/translation evidence gaps, boundary grid and continuous fixed-set LP audits. Layered analyses report lost opportunity relative to all630 as well as conditional performance.

Supported replacement in a named context requires >=.02 recovery improvement in both test and replication, positive paired95%MC lower bounds, no material winner/regret degradation, continuous worst regret no worse, and list mean A/H each>=95% of historical baseline. These cutoffs are declared study guards, not expert preferences. Any failed guard means tradeoff or null result. Universal claims require all feasible contexts to pass.

## Integrity
Protocol is frozen before new counts, selection or rankings. Preserve failures, original inputs and all previous outputs. New experiments are archived-performance decision analysis only; no new physical simulation or construction validation is asserted.

All holdout-dependent guards must hold separately in BOTH independent splits. The criteria are descriptive, not multiple-testing-adjusted discoveries. For layered scenarios total all630 regret equals filter opportunity loss plus within-eligible regret; all three are reported.
