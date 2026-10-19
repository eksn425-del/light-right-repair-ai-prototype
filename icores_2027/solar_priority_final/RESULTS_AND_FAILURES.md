# Solar-priority decision analysis: results and failures

No context satisfies the prospectively declared supported-replacement criterion. Preserve the previous manuscript and evidence; do not relax the0.02 recovery requirement after seeing results. New findings support an optional transparent sensitivity revision, not a superior general algorithm claim.

A failed composite criterion is not absence of all value. Total-solar-weight supports admit H-oriented winning choices missed by Historical10; the new lists preserve them. Ordered priorities already retain the best choice. These are different priority definitions.

## Mathematical selection
For scenario Top10 set T(w), Q(S)=E[|S∩T(w)|/10]=sum(i in S)Pr(i in T(w))/10. Linearity makes Q modular. The ten highest training inclusion frequencies exactly maximize empirical Q. ProtectedCoverage10 mandates each distinct training winner before filling remaining slots; >10 mandated winners is explicitly infeasible. Both selectors have identical membership in all six observed contexts, so the protection constraint adds no observed selection advantage. Neither mechanism is new general optimization theory.

180000 sampled weights are divided into three supports and independent train/test/replication splits of20000. A-floor contexts reuse solar70 samples intentionally. Only training determines membership. Ten training blocks provide selection stability. Independent evaluation, grid and LP never reselect.

Ordered means wA>=wH>=wV but remains compensatory. Total-solar70/80 means wA+wH>=.70/.80, permits wA=0 and does not guarantee a physical A floor. A90/180/270 are hard prospective study scenarios, not laws or expert preferences. All normalization remains global and frozen.

## Threshold attrition
| context | A_min | eligible_count | excluded_count | feasible_k10 |
| --- | --- | --- | --- | --- |
| ordered | nan | 630 | 0 | True |
| solar70 | nan | 630 | 0 | True |
| solar80 | nan | 630 | 0 | True |
| A90_solar70 | 90.000000 | 166 | 464 | True |
| A180_solar70 | 180.000000 | 50 | 580 | True |
| A270_solar70 | 270.000000 | 12 | 618 | True |

Layered baseline lists are explicitly eligible adaptations. Original-list violations are separately archived; no list is silently relabeled. Ten slots are compared within the same universe.

## Independent test
| context | set | top10_recovery | winner_coverage | regret_mean | regret_max | list_A_mean | list_H_mean | list_V_mean | rule_HB_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ordered | historical10 | 0.894950 | 1.000000 | 0.000000 | 0.000000 | 309.600000 | 0.042491 | 4542.283978 | 10 |
| ordered | robust10 | 0.444360 | 1.000000 | 0.000000 | 0.000000 | 208.800000 | 0.041630 | 3312.565625 | 7 |
| ordered | AV10 | 0.290815 | 1.000000 | 0.000000 | 0.000000 | 225.900000 | 0.029099 | 2414.392784 | 10 |
| ordered | AHV10 | 0.741410 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 |
| ordered | coverage10 | 0.899380 | 1.000000 | 0.000000 | 0.000000 | 319.500000 | 0.038996 | 4378.828553 | 9 |
| ordered | protected_coverage10 | 0.899380 | 1.000000 | 0.000000 | 0.000000 | 319.500000 | 0.038996 | 4378.828553 | 9 |
| solar70 | historical10 | 0.649650 | 0.890800 | 0.000750 | 0.018651 | 309.600000 | 0.042491 | 4542.283978 | 10 |
| solar70 | robust10 | 0.456385 | 1.000000 | 0.000000 | 0.000000 | 208.800000 | 0.041630 | 3312.565625 | 7 |
| solar70 | AV10 | 0.211580 | 0.685050 | 0.030440 | 0.228607 | 225.900000 | 0.029099 | 2414.392784 | 10 |
| solar70 | AHV10 | 0.656835 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 |
| solar70 | coverage10 | 0.660935 | 1.000000 | 0.000000 | 0.000000 | 296.100000 | 0.044953 | 4427.400313 | 9 |
| solar70 | protected_coverage10 | 0.660935 | 1.000000 | 0.000000 | 0.000000 | 296.100000 | 0.044953 | 4427.400313 | 9 |
| solar80 | historical10 | 0.655725 | 0.844350 | 0.001073 | 0.019141 | 309.600000 | 0.042491 | 4542.283978 | 10 |
| solar80 | robust10 | 0.450710 | 1.000000 | 0.000000 | 0.000000 | 208.800000 | 0.041630 | 3312.565625 | 7 |
| solar80 | AV10 | 0.205810 | 0.689750 | 0.031419 | 0.231087 | 225.900000 | 0.029099 | 2414.392784 | 10 |
| solar80 | AHV10 | 0.649560 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 |
| solar80 | coverage10 | 0.669465 | 1.000000 | 0.000000 | 0.000000 | 272.700000 | 0.050197 | 5350.608195 | 7 |
| solar80 | protected_coverage10 | 0.669465 | 1.000000 | 0.000000 | 0.000000 | 272.700000 | 0.050197 | 5350.608195 | 7 |
| A90_solar70 | historical10 | 0.649650 | 0.890800 | 0.000750 | 0.018651 | 309.600000 | 0.042491 | 4542.283978 | 10 |
| A90_solar70 | robust10 | 0.529890 | 1.000000 | 0.000000 | 0.000000 | 236.700000 | 0.045790 | 3804.159358 | 7 |
| A90_solar70 | AV10 | 0.211580 | 0.685050 | 0.030440 | 0.228607 | 225.900000 | 0.029099 | 2414.392784 | 10 |
| A90_solar70 | AHV10 | 0.656835 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 |
| A90_solar70 | coverage10 | 0.660935 | 1.000000 | 0.000000 | 0.000000 | 296.100000 | 0.044953 | 4427.400313 | 9 |
| A90_solar70 | protected_coverage10 | 0.660935 | 1.000000 | 0.000000 | 0.000000 | 296.100000 | 0.044953 | 4427.400313 | 9 |
| A180_solar70 | historical10 | 0.693290 | 0.890800 | 0.000750 | 0.018651 | 309.600000 | 0.042491 | 4542.283978 | 10 |
| A180_solar70 | robust10 | 0.704565 | 1.000000 | 0.000000 | 0.000000 | 296.100000 | 0.044953 | 4427.400313 | 9 |
| A180_solar70 | AV10 | 0.601720 | 0.890800 | 0.000750 | 0.018651 | 297.900000 | 0.038405 | 3922.582216 | 10 |
| A180_solar70 | AHV10 | 0.706795 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 |
| A180_solar70 | coverage10 | 0.706795 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 |
| A180_solar70 | protected_coverage10 | 0.706795 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 |
| A270_solar70 | historical10 | 0.996625 | 1.000000 | 0.000000 | 0.000000 | 323.100000 | 0.036091 | 4288.020817 | 8 |
| A270_solar70 | robust10 | 0.996625 | 1.000000 | 0.000000 | 0.000000 | 323.100000 | 0.036091 | 4288.020817 | 8 |
| A270_solar70 | AV10 | 0.900000 | 1.000000 | 0.000000 | 0.000000 | 322.200000 | 0.035180 | 4232.208586 | 9 |
| A270_solar70 | AHV10 | 0.900000 | 1.000000 | 0.000000 | 0.000000 | 322.200000 | 0.035180 | 4232.208586 | 9 |
| A270_solar70 | coverage10 | 0.996625 | 1.000000 | 0.000000 | 0.000000 | 323.100000 | 0.036091 | 4288.020817 | 8 |
| A270_solar70 | protected_coverage10 | 0.996625 | 1.000000 | 0.000000 | 0.000000 | 323.100000 | 0.036091 | 4288.020817 | 8 |

## Independent replication
| context | set | top10_recovery | winner_coverage | regret_mean | regret_max |
| --- | --- | --- | --- | --- | --- |
| ordered | historical10 | 0.895955 | 1.000000 | 0.000000 | 0.000000 |
| ordered | robust10 | 0.443985 | 1.000000 | 0.000000 | 0.000000 |
| ordered | AV10 | 0.291390 | 1.000000 | 0.000000 | 0.000000 |
| ordered | AHV10 | 0.742035 | 1.000000 | 0.000000 | 0.000000 |
| ordered | coverage10 | 0.899770 | 1.000000 | 0.000000 | 0.000000 |
| ordered | protected_coverage10 | 0.899770 | 1.000000 | 0.000000 | 0.000000 |
| solar70 | historical10 | 0.653950 | 0.895800 | 0.000742 | 0.019075 |
| solar70 | robust10 | 0.456595 | 1.000000 | 0.000000 | 0.000000 |
| solar70 | AV10 | 0.213535 | 0.694550 | 0.029756 | 0.230492 |
| solar70 | AHV10 | 0.659660 | 1.000000 | 0.000000 | 0.000000 |
| solar70 | coverage10 | 0.664335 | 1.000000 | 0.000000 | 0.000000 |
| solar70 | protected_coverage10 | 0.664335 | 1.000000 | 0.000000 | 0.000000 |
| solar80 | historical10 | 0.653140 | 0.845800 | 0.001097 | 0.019029 |
| solar80 | robust10 | 0.449740 | 1.000000 | 0.000000 | 0.000000 |
| solar80 | AV10 | 0.204875 | 0.690200 | 0.031886 | 0.228626 |
| solar80 | AHV10 | 0.647300 | 1.000000 | 0.000000 | 0.000000 |
| solar80 | coverage10 | 0.667910 | 1.000000 | 0.000000 | 0.000000 |
| solar80 | protected_coverage10 | 0.667910 | 1.000000 | 0.000000 | 0.000000 |
| A90_solar70 | historical10 | 0.653950 | 0.895800 | 0.000742 | 0.019075 |
| A90_solar70 | robust10 | 0.530425 | 1.000000 | 0.000000 | 0.000000 |
| A90_solar70 | AV10 | 0.213535 | 0.694550 | 0.029756 | 0.230492 |
| A90_solar70 | AHV10 | 0.659660 | 1.000000 | 0.000000 | 0.000000 |
| A90_solar70 | coverage10 | 0.664335 | 1.000000 | 0.000000 | 0.000000 |
| A90_solar70 | protected_coverage10 | 0.664335 | 1.000000 | 0.000000 | 0.000000 |
| A180_solar70 | historical10 | 0.696835 | 0.895800 | 0.000742 | 0.019075 |
| A180_solar70 | robust10 | 0.707200 | 1.000000 | 0.000000 | 0.000000 |
| A180_solar70 | AV10 | 0.603525 | 0.895800 | 0.000742 | 0.019075 |
| A180_solar70 | AHV10 | 0.708475 | 1.000000 | 0.000000 | 0.000000 |
| A180_solar70 | coverage10 | 0.708475 | 1.000000 | 0.000000 | 0.000000 |
| A180_solar70 | protected_coverage10 | 0.708475 | 1.000000 | 0.000000 | 0.000000 |
| A270_solar70 | historical10 | 0.996820 | 1.000000 | 0.000000 | 0.000000 |
| A270_solar70 | robust10 | 0.996820 | 1.000000 | 0.000000 | 0.000000 |
| A270_solar70 | AV10 | 0.900000 | 1.000000 | 0.000000 | 0.000000 |
| A270_solar70 | AHV10 | 0.900000 | 1.000000 | 0.000000 | 0.000000 |
| A270_solar70 | coverage10 | 0.996820 | 1.000000 | 0.000000 | 0.000000 |
| A270_solar70 | protected_coverage10 | 0.996820 | 1.000000 | 0.000000 | 0.000000 |

## Continuous fixed-set audit
| context | set | lp_count | all_success | continuous_worst_regret | wA | wH | wV |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ordered | historical10 | 630 | True | 0.000000 | 1.000000 | 0.000000 | 0.000000 |
| ordered | robust10 | 630 | True | 0.000000 | 1.000000 | 0.000000 | 0.000000 |
| ordered | AV10 | 630 | True | 0.000000 | 1.000000 | 0.000000 | 0.000000 |
| ordered | AHV10 | 630 | True | 0.000000 | 1.000000 | 0.000000 | 0.000000 |
| ordered | coverage10 | 630 | True | 0.000000 | 1.000000 | 0.000000 | 0.000000 |
| ordered | protected_coverage10 | 630 | True | 0.000000 | 1.000000 | 0.000000 | 0.000000 |
| solar70 | historical10 | 630 | True | 0.019380 | 0.000000 | 1.000000 | 0.000000 |
| solar70 | robust10 | 630 | True | 0.000000 | 0.307908 | 0.692092 | 0.000000 |
| solar70 | AV10 | 630 | True | 0.232558 | 0.000000 | 1.000000 | 0.000000 |
| solar70 | AHV10 | 630 | True | 0.000000 | 0.234551 | 0.465449 | 0.300000 |
| solar70 | coverage10 | 630 | True | 0.000000 | 0.700000 | 0.000000 | 0.300000 |
| solar70 | protected_coverage10 | 630 | True | 0.000000 | 0.700000 | 0.000000 | 0.300000 |
| solar80 | historical10 | 630 | True | 0.019380 | 0.000000 | 1.000000 | 0.000000 |
| solar80 | robust10 | 630 | True | 0.000000 | 0.307908 | 0.692092 | 0.000000 |
| solar80 | AV10 | 630 | True | 0.232558 | 0.000000 | 1.000000 | 0.000000 |
| solar80 | AHV10 | 630 | True | 0.000000 | 0.256005 | 0.543995 | 0.200000 |
| solar80 | coverage10 | 630 | True | 0.000000 | 0.256005 | 0.543995 | 0.200000 |
| solar80 | protected_coverage10 | 630 | True | 0.000000 | 0.256005 | 0.543995 | 0.200000 |
| A90_solar70 | historical10 | 166 | True | 0.019380 | 0.000000 | 1.000000 | 0.000000 |
| A90_solar70 | robust10 | 166 | True | 0.000000 | 0.307908 | 0.692092 | 0.000000 |
| A90_solar70 | AV10 | 166 | True | 0.232558 | 0.000000 | 1.000000 | 0.000000 |
| A90_solar70 | AHV10 | 166 | True | 0.000000 | 0.234551 | 0.465449 | 0.300000 |
| A90_solar70 | coverage10 | 166 | True | 0.000000 | 0.700000 | 0.000000 | 0.300000 |
| A90_solar70 | protected_coverage10 | 166 | True | 0.000000 | 0.700000 | 0.000000 | 0.300000 |
| A180_solar70 | historical10 | 50 | True | 0.019380 | 0.000000 | 1.000000 | 0.000000 |
| A180_solar70 | robust10 | 50 | True | 0.000000 | 0.700000 | 0.000000 | 0.300000 |
| A180_solar70 | AV10 | 50 | True | 0.019380 | 0.000000 | 1.000000 | 0.000000 |
| A180_solar70 | AHV10 | 50 | True | 0.000000 | 0.234551 | 0.465449 | 0.300000 |
| A180_solar70 | coverage10 | 50 | True | 0.000000 | 0.234551 | 0.465449 | 0.300000 |
| A180_solar70 | protected_coverage10 | 50 | True | 0.000000 | 0.234551 | 0.465449 | 0.300000 |
| A270_solar70 | historical10 | 12 | True | 0.000000 | 0.700000 | 0.000000 | 0.300000 |
| A270_solar70 | robust10 | 12 | True | 0.000000 | 0.700000 | 0.000000 | 0.300000 |
| A270_solar70 | AV10 | 12 | True | 0.000000 | 0.700000 | 0.000000 | 0.300000 |
| A270_solar70 | AHV10 | 12 | True | 0.000000 | 0.700000 | 0.000000 | 0.300000 |
| A270_solar70 | coverage10 | 12 | True | 0.000000 | 0.700000 | 0.000000 | 0.300000 |
| A270_solar70 | protected_coverage10 | 12 | True | 0.000000 | 0.700000 | 0.000000 | 0.300000 |

These LPs audit fixed sets under declared supports, not global set optimality or physical accuracy.

## Frozen success/failure guards

### ordered
Supported replacement: False

Failed guards: test_recovery_gain_ge_002, test_mean_H_guard, replication_recovery_gain_ge_002, replication_mean_H_guard

### solar70
Supported replacement: False

Failed guards: test_recovery_gain_ge_002, replication_recovery_gain_ge_002

### solar80
Supported replacement: False

Failed guards: test_recovery_gain_ge_002, test_mean_A_guard, replication_recovery_gain_ge_002, replication_mean_A_guard

### A90_solar70
Supported replacement: False

Failed guards: test_recovery_gain_ge_002, replication_recovery_gain_ge_002

### A180_solar70
Supported replacement: False

Failed guards: test_recovery_gain_ge_002, test_mean_A_guard, replication_recovery_gain_ge_002, replication_mean_A_guard

### A270_solar70
Supported replacement: False

Failed guards: test_recovery_gain_ge_002, test_recovery_MC_lower_positive, replication_recovery_gain_ge_002, replication_recovery_MC_lower_positive

## Negative findings and boundaries
All recovery gains are below the prospectively declared two-percentage-point criterion. Positive paired Monte Carlo intervals do not override this practical threshold. Ordered selection gains mean A but loses enough mean H to fail its95%guard. Solar80 shifts toward H, loses mean A and increases nominal intervention; do not claim more sunlight and less intervention in every sense. A180 also fails its mean-Aguard. At A270 historical, robust-adapted and both new lists coincide; AV/AHV differ. The A270 filter loses all630 opportunities despite zero conditional regret: conditional regret + filter loss = total regret, all separately saved.

Prior full-simplex Robust10 retains winners but recovers fewer preferred Top10 entries and contains low-A/low-volume options. Its original objective differs; it is not retrained in primary contexts. No geometric diversity, actual architect satisfaction or construction readiness has been measured.

N is exactlyzero and excluded from active rank discrimination but retained for geometry-risk interpretation. Rule-level HB review and translated-design checks are separate; missing entries remain missing. Frozen23/20cohorts are unchanged. This is new decision analysis on archived data, not new physical simulation.

## Recommended architect workflow
Clarify whether priority means orderedA/H/V, high total solar importance, or a hard minimumA. Inspect A and H separately, then nominalV without claiming real cost. Keep Historical10 as a defensible initial list under ordered priorities. Offer contextual total-solar lists as alternatives showing H-rich winning opportunities, with the small recovery gains and missingHBexplicit. Request professional simulation and geometric/structural/rights review before design development. Architect makes the final choice.

## Six requested answers
1. Consider the new mechanism to reveal dependence on one unelicited weight vector and preserve several high-ranked alternatives. The data do not justify automatic replacement.
2.45/35/15/5 ranks once. New selection aggregates Top10 membership across declared weight scenarios, optionally protects trainingwinners, and removes constantNfrom discrimination.
3. Actual benefit: total-solar supports restore missed H-oriented best options and modestly improve Top10 recovery; ordered baseline already has zero regret.
4. Failures: gains<2points, some meanA/H reductions, and no new-list advantage after A270; all six replacementgates fail.
5. Methods are established MCDA/SMAA-related acceptability and modular selection. Contribution is the controlled architectural comparison and transparent limits, not invented optimization theory.
6. Retain the supported baseline and offer sensitivity alternatives; architects choose priority interpretation and final designs.
