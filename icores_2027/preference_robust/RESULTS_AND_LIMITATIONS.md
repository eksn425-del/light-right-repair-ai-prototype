# Preference-robust screening: complete results and limitations

## Frozen design
Protocol was committed before new outcomes at cff3e81eebf93a16df6da8a21fe735c1554a5a8f. The analysis uses 20,000 independent samples for each of three spaces and each of train, test, replication (180,000 total), plus a resolution-100 grid and candidate-wise LP audit of each fixed set. Greedy selection uses only 60,000 equally pooled training samples. All 630 candidates remain in ranking analysis.

## Primary result
On full-simplex independent test weights, mean regret fell from 0.010759070 to 0.000053833; p95 fell from 0.080600885 to 0.000000000. Winner coverage rose from 77.69500% to 97.94000%.
The restricted ordered and local spaces yield zero regret for every same-k method, including the historical shortlist. Therefore the benefit is protection against broad preference uncertainty, especially extreme intervention-cost preferences, rather than universal improvement. The preregistered stable-improvement rule is met because full-space mean and p95 improve in both independent runs while restricted spaces are equal. This is not an empirical claim about architects.
A/H correlations: Pearson 0.640978217, Spearman 0.768359947. N is exactly zero for all 630. A measures area crossing the low-sun threshold, while H measures mean direct-sun duration gain; correlated but not equivalent outcomes.

## Independent test and replication, equal k=10
|Space|Split|Set|Mean regret|p95 regret|Observed max|Winner coverage|Any Top10 coverage|
|---|---|---|---:|---:|---:|---:|---:|
|full|test|historical10|0.010759070|0.080600885|0.241086995|0.77695|0.90045|
|full|test|AV10|0.022995530|0.138777541|0.231870908|0.66215|0.91990|
|full|test|AHV10|0.010378434|0.080600885|0.241086995|0.83170|0.90045|
|full|test|robust10|0.000053833|0.000000000|0.007539363|0.97940|1.00000|
|full|replication|historical10|0.011350705|0.082743342|0.240658083|0.76635|0.89560|
|full|replication|AV10|0.022741506|0.138120441|0.229999479|0.65895|0.91975|
|full|replication|AHV10|0.010944208|0.082743342|0.240658083|0.82280|0.89560|
|full|replication|robust10|0.000055063|0.000000000|0.007612873|0.97885|1.00000|
|ordered|test|historical10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|ordered|test|AV10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|ordered|test|AHV10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|ordered|test|robust10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|ordered|replication|historical10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|ordered|replication|AV10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|ordered|replication|AHV10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|ordered|replication|robust10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|local|test|historical10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|local|test|AV10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|local|test|AHV10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|local|test|robust10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|local|replication|historical10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|local|replication|AV10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|local|replication|AHV10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|
|local|replication|robust10|0.000000000|0.000000000|0.000000000|1.00000|1.00000|

## Continuous worst-case audit
All 630 candidate-wise LPs per fixed set/space passed. The maximum is global over the declared continuous polyhedral preference space, up to numerical solver tolerance; it is not a certificate that the selected set is optimal.
|Space|Set|Size|Continuous worst regret|Witness wA,wH,wV|
|---|---|---:|---:|---|
|full|historical10|10|0.246358582|0.000000, 0.000000, 1.000000|
|full|AV10|10|0.232558140|0.000000, 1.000000, 0.000000|
|full|AHV10|10|0.246358582|0.000000, 0.000000, 1.000000|
|full|robust10|10|0.007655659|0.211837, 0.000000, 0.788163|
|full|AV_full|12|0.232558140|0.000000, 1.000000, 0.000000|
|full|AHV_full|41|0.000000000|0.173664, 0.242534, 0.583801|
|ordered|historical10|10|0.000000000|1.000000, 0.000000, 0.000000|
|ordered|AV10|10|0.000000000|1.000000, 0.000000, 0.000000|
|ordered|AHV10|10|0.000000000|1.000000, 0.000000, 0.000000|
|ordered|robust10|10|0.000000000|1.000000, 0.000000, 0.000000|
|ordered|AV_full|12|0.000000000|1.000000, 0.000000, 0.000000|
|ordered|AHV_full|41|0.000000000|1.000000, 0.000000, 0.000000|
|local|historical10|10|0.000000000|0.373684, 0.368421, 0.257895|
|local|AV10|10|0.000000000|0.373684, 0.368421, 0.257895|
|local|AHV10|10|0.000000000|0.373684, 0.368421, 0.257895|
|local|robust10|10|0.000000000|0.373684, 0.368421, 0.257895|
|local|AV_full|12|0.000000000|0.373684, 0.368421, 0.257895|
|local|AHV_full|41|0.000000000|0.373684, 0.368421, 0.257895|

## Robust10, greedy insertion order
Five entries overlap the historical10; Jaccard = 1/3. A/V front has 12 entries; A/H/V front has 41. Neither front required padding in its Top10 comparator. Full-front comparisons have different cardinalities and are diagnostics only.
|Step|Pair|Historical rank|A m2|H h|V m3|Full test Top10 acceptability|HB cohort|Translation|
|---:|---|---:|---:|---:|---:|---:|---|---|
|1|C9,C12|3|306.000|0.043574594|4030.543|0.63455|curated23|NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION|
|2|C12,C15|20|153.000|0.048498277|2495.690|0.33655|MISSING|NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION|
|3|C12,C24|7|198.000|0.062284589|4919.268|0.49645|curated23|NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION|
|4|C9,C24|1|396.000|0.048744461|5551.333|0.71125|curated23|CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED|
|5|C15,C25|125|99.000|0.022648941|964.857|0.12770|MISSING|NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION|
|6|C9,C15|2|351.000|0.034958149|3127.755|0.63955|curated23|CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED|
|7|C25,C29|397|18.000|0.003200394|387.382|0.05295|curated23|NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION|
|8|C13,C15|55|135.000|0.035204333|1440.303|0.20395|curated23|NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION|
|9|C24,C35|11|189.000|0.063515510|6192.045|0.36040|MISSING|NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION|
|10|C15,C24|4|243.000|0.053668144|4016.480|0.66145|curated23|NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION|

## Monte Carlo precision
All candidate-specific winner/Top10 Wilson intervals are retained in all630_rank_acceptability.csv; these are marginal conditional Monte Carlo intervals, not architect-preference probabilities or simultaneous uncertainty bounds. Test and replication are separate draws and never affect selection. Pooled mean standard errors use the stratified equal-space design; within-space coverage intervals use Wilson.
|Space|Metric|Median absolute test/replication difference|p95 difference|Maximum difference|
|---|---|---:|---:|---:|
|full|winner_acceptability|0.000000|0.000000|0.006500|
|full|top10_acceptability|0.000000|0.001550|0.010150|
|ordered|winner_acceptability|0.000000|0.000000|0.000000|
|ordered|top10_acceptability|0.000000|0.000000|0.007250|
|local|winner_acceptability|0.000000|0.000000|0.000000|
|local|top10_acceptability|0.000000|0.000000|0.009200|

## Interpretation and failure cases
- The full A/H/V front attains zero continuous regret because positive-weight linear winners have nondominated representatives; that requires 41 candidates here. The 10-item greedy set still has positive full-space regret.
- The A/V front can miss H-driven winners. Truncating either front by historical score is an explicit baseline, not a claim that Pareto filtering naturally supplies a unique best Top10.
- C12,C15; C15,C25; and C24,C35 lack archived rule-level HB results. Missing high-fidelity evidence must remain visible; do not describe all ten as validated. Existing HB evidence comes from the curated23 or frozen20 cohorts; no cohort was reselected.
- N=0 is a property of this archived pure-height-reduction universe, not a guarantee for later translated designs.
- Weights are declared scenarios. Uniform-simplex sampling is a modeling assumption, not preference-free or a population survey. The local half-width 0.10 and ordered constraints are assumptions.
- Normalization is frozen from this candidate universe. Correlation of A and H and redundancy deserve discussion; no learned or elicited weights were fitted.
- Worst observed rank differs from worst possible rank. Exact utility ties use stable natural numeric pair order; tie diagnostics are archived. Utility winner coverage is separately reported to avoid confusing rank-ID ties with utility loss.
- The run is archived-performance decision analysis only. No new Honeybee/Radiance, structural, rights, cost, or construction validation was run.
- Findings demonstrate one-site implementation and preference sensitivity. They do not establish novelty of SMAA, minimax regret, utility elicitation or Pareto theory.

## Reproduction
Run python icores_2027/preference_robust/analysis/run_analysis.py from the repository, then python icores_2027/preference_robust/analysis/make_report.py. See RUN_MANIFEST.json and requirements.txt for versions. The run verifies frozen input hashes before generating any weights. No network, GPU, or geometry simulator is required.
The initial run needed reporting-only corrections: stratified pooled MC SE, explicit HiGHS version, and local rejection acceptance count. Initial affected artifacts are retained under audit/initial_reporting_run. Rerun uses identical frozen seeds and rules; shortlist and outcomes are unchanged.
