# Independent solar-priority analysis review

Date: 2026-10-18 UTC. Coordinator confirmed remote protocol freeze `94ba70a567030b9736140b3c7ac69c6160e44d49` before new outcomes. Protocol and code review preceded execution. Reviewer did not import analyst functions.

## Verdict

PASS within computational/methodological scope. All six predeclared composite replacement criteria fail. This informative negative result must not be removed by adjusting thresholds after observing outcomes.

## Independent executable checks

`qa/independent_checks.py` reconstructs calculations directly from archived CSVs; `qa/independent_check_results.json` identifies the reviewed run.

- Eight frozen input hashes and all 159 manifest output hashes match, as does the analysis-script hash.
- Recreated every one of the 180,000 weights exactly using declared seeds/distributions.
- Verified N=0 in all 630 archived rows and unchanged global normalization.
- Reconstructed all Top-10 and winner memberships across 18 context/split combinations; sampled scalar Python rankings also match. All candidate inclusion/winner counts, mean ranks and worst observed ranks match.
- Reconstructed all twelve primary selections and all 120 training-block selections, including empirical modular objective and required training winners.
- Verified all comparator lists, filtered-universe Pareto sets and historical-order padding. All lists have ten unique eligible candidates. Original primary lists remain unchanged.
- Recomputed all 2,160,000 scenario/set rows for regret, recovery, winner coverage and all-universe regret; verified summary reductions and list A/H/V means.
- Independently evaluated all 12,708 LP witness objectives and weight constraints. Maximum discrepancy: 2.22e-16. Analyst code additionally verifies global maxima and dominance over sample/grid maxima. LP signs and unrestricted t were inspected; reviewer did not separately re-optimize every LP.
- Verified all 108 paired rows and Monte Carlo standard errors/lower bounds; independently applied every guard in all six adoption decisions.
- Verified all 360 shortlist evidence joins against archived HB values and separate design-translation status. Missing data remain missing.

## Corrections before execution

Chosen-candidate diagnostics initially used shortlist insertion order for exact utility ties; corrected to numeric ID order before execution. Grid weights/memberships, block membership frequencies and test/replication acceptability deltas were added before execution. No outcome-informed change occurred.

## Interpretation that must survive editing

1. No context reaches the predeclared 0.02 absolute Top-10-recovery improvement in both holdouts. This is an analyst-declared practical threshold, not expert knowledge or a regulatory standard.
2. Ordered weights: old and protected lists both have zero continuous regret and complete winner coverage. Test recovery rises only 0.894950 to 0.899380. Protected mean H falls about 0.042491 to 0.038996 hours, failing its 95% guard.
3. Solar70: test recovery improves 0.649650 to 0.660935; winner coverage rises 0.89080 to 1. Historical continuous worst regret is 0.019379845 at pure H preference; protected coverage has zero. Failure of the composite adoption rule does NOT mean no metric improves.
4. Solar80: test recovery improves 0.655725 to 0.669465 and winner coverage 0.84435 to 1. But mean A drops 309.6 to 272.7 square metres and nominal intervention increases about 4542.28 to 5350.61 cubic metres. This is not uniform superiority or lower intervention.
5. Floors 90/180/270 square metres retain 166/50/12 candidates. At the highest floor old and new selections coincide. Conditional regret must not be confused with full-universe opportunity loss.
6. Solar70 protected has nine existing rule-level HB reviews versus ten historical; solar80 has seven. Unreviewed candidates are not validated designs. Rule-level review, translated geometry, and construction feasibility remain separate.
7. Coverage10 is exact empirical modular optimization, not a new general algorithm. Required-winner protection only guarantees observed training identities; subsequent continuous audit is separate. Scenario weights are not measured human preferences.
8. Fixed-set continuous zero regret holds only for the specified archived utilities and linear preference model up to numerical tolerance; it does not certify global shortlist optimality, simulation accuracy or buildability.

## Recommendation

Retain historical10 as the evidence-backed default. Use preference sensitivity as an explanatory layer: ordered priority supports the existing list, while allowing H-dominant preferences reveals useful alternatives with modest recovery gains and explicit sunlight/evidence tradeoffs. Do not relax the frozen 2% and 95% guards or claim universal replacement.

## Scope and identity

This audit does not rerun Honeybee/Radiance, validate site geometry or actual preferences, establish causal benefits, or certify academic acceptance.

- Manifest SHA256: `dd8220699136078ec99bb2ac3432ca43ba24dc792ae46c5568a8678968fcb36e`
- Protocol SHA256: `f3b0c3657c9f39d2fc819994f5d8245fc0521c4c0544ccea57f07b4136679f29`
- Analysis script SHA256: `30865b77cbac781e179ff4e7035c4a6ce3a93bbaa62ffcdf3f282e285e0668dd`
