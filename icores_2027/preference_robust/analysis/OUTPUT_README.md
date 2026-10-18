# Output archive and index conventions

All new analysis is reproduced by run_analysis.py. Then run make_report.py and package_results.py.

The repository delivery uses results/weight_samples/*.npz and results/set_scenario_metrics/*.csv.gz as lossless shards. The two corresponding large monoliths may be omitted from GitHub upload; they are reproducibly regenerated locally by the script. SPLIT_ARCHIVE_MANIFEST.json certifies exact array/dataframe equality and records all shard hashes. Concatenate metric shards and sort by space,split,set,scenario to reconstruct the monolithic logical table. Each weight shard has key weights and columns wA,wH,wV. There are 9 weight shards and 54 metrics shards (all six sets, three spaces, three splits), with no omitted scenarios.

NPZ rank_memberships files contain zero-based candidate indices into all630_metrics_memberships.csv in its saved natural numeric pair-ID row order, with one row per weight sample in that space/split. Full per-candidate rank histograms (all ranks 1..630) are in rank_distribution_*.csv.gz. Histograms include all train, test, and replication samples. Every scenario Top10 is preserved in rank_memberships, while complete rank distributions are retained in histogram form.

SUMMARY.json is manuscript-ready structured data. RESULTS_AND_LIMITATIONS.md contains all same-k test/replication results, continuous fixed-set LP results, shortlist evidence, MC precision and caveats. Full fronts are separately labeled, never equal-size comparisons. LP raw candidate objectives may be negative because an individual candidate can be worse than the shortlist at every weight; only their maximum is the set's nonnegative worst-case regret.

Reporting corrections: the initial run was retained for HiGHS-version, rejection-rate and stratified-SE fixes. A subsequent run corrected uint16 cross-space worst-rank subtraction by casting to signed float before differencing. Neither correction changes sampling, candidate rankings, shortlist selection, regret or scientific conclusions. Prior affected files/logs/manifests are preserved in audit/. Do not cite superseded audit output as final results.

All performance data are archived; no physical simulator was run. Missing Honeybee results are explicitly MISSING, never treated as validation success. Rule-level HB evidence and translated-design status are separate.
