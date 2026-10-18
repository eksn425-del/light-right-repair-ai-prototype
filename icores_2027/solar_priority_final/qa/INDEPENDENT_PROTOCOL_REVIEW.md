# Independent pre-outcome protocol review

Review date: 2026-10-18 UTC. Reviewed new protocol before any new sampled preferences, threshold counts, rankings or outcomes. No analysis runs were performed by this reviewer before freeze.

## Findings

No substantive methodological blocker was found. The comparison answers the author's solar-priority question without assuming a favorable outcome.

- Ordered weight restrictions and aggregate solar-weight bounds are explicitly distinguished from lexicographic priority and minimum physical improvement. The latter requires an explicit A floor.
- A floors of 90, 180 and 270 square metres are declared scenario parameters, not regulations or elicited expert preferences. All comparisons within a floor share the same eligible universe, unchanged global normalization, and ten slots. Adapted historical lists are labeled separately from immutable original lists; infeasible contexts are reported rather than padded with ineligible candidates.
- Expected Top-10 recovery is a modular function, because expectation distributes across candidate membership indicators. Therefore choosing the ten highest empirical inclusion probabilities is an exact empirical optimum for this specific objective. It is not a new general coverage or optimization algorithm.
- Conditioning on required observed training winners retains an exact constrained empirical optimum when their number is at most ten. It does not guarantee unseen or boundary-winner coverage. Infeasibility is explicitly reported.
- Training, test, replication and fixed-grid/continuous audits are separated; stability resampling uses training blocks only. Independent holdout evaluation avoids selecting and evaluating on the same preference scenarios.
- Continuous fixed-set regret LP formulation is valid. Each candidate LP's own objective must be checked against that candidate's utility minus best shortlist utility; full-universe regret is checked at the global maximizing witness. These are not interchangeable.
- Mean solar-performance guards and recovery-improvement threshold are explicit analyst choices. They do not establish user desirability, causal design improvements, physical accuracy, or statistical discovery across sites.
- Existing HB evidence is joined by candidate identity and distinguished from geometric translation and construction feasibility. No new physical simulation is claimed.

## Requested prefreeze clarifications

The designer was asked to state that coverage and mean-regret guards apply separately to both independent holdouts; to write the full-universe opportunity-loss decomposition explicitly for layered contexts; and to distinguish descriptive claim rules from familywise statistical discovery. These are clarifications before freeze, not changes informed by new outcomes.

This review concerns the planned analysis. Implementation and result validation must follow after the coordinator confirms the remote protocol-freeze commit.
