# Reproduction

From repository root, install the pinned packages in requirements.txt and run:

SOLAR_PROTOCOL_FREEZE_COMMIT=94ba70a567030b9736140b3c7ac69c6160e44d49 python icores_2027/solar_priority_final/analysis/run_analysis.py

The script verifies frozen input SHA256s before generating weights. It writes only solar_priority_final outputs. Do not run the older preference_robust script for this experiment.

Weights are saved in nine individual NPZs. Context-specific train/test/replication and grid Top10 memberships are separate NPZs. Each scenario CSV.gz filename explicitly identifies context, split and method. No giant compressed result aggregate is needed. Same solar70 draws are intentionally reused across the three A-floor contexts; these contexts are paired, not independent samples. All other splits are separately seeded. Files retain all scenarios, not just summaries.

Coverage10 exactly maximizes empirical expected Top10 recovery by ordering marginal Top10 counts. ProtectedCoverage10 adds every observed training winner as a mandatory item before filling remaining slots. No heldout information changes a list. Required-winner feasibility is explicit. Conditional and all630 regret are separate in layered contexts.

The continuous LP audit evaluates each fixed list under its declared support and eligible universe; it does not solve global ten-item minimax selection. All physical inputs and HB results are historic archives, not new simulations.
