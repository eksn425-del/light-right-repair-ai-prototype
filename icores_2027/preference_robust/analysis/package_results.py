from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
B=Path(__file__).resolve().parents[1];R=B/'results'
mono=np.load(R/'weight_samples.npz');manifest=[]
for f in sorted((R/'weight_samples').glob('*.npz')):
 a=np.load(f)['weights'];assert np.array_equal(a,mono[f.stem]);assert f.stat().st_size<500000
 manifest.append({'path':str(f.relative_to(B)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'shape':list(a.shape)})
full=pd.read_csv(R/'set_scenario_metrics.csv.gz');parts=[]
for f in sorted((R/'set_scenario_metrics').glob('*.csv.gz')):
 g=pd.read_csv(f);parts.append(g);assert f.stat().st_size<1000000
 manifest.append({'path':str(f.relative_to(B)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'rows':len(g)})
cols=['space','split','set','scenario'];a=full.sort_values(cols).reset_index(drop=True);b=pd.concat(parts).sort_values(cols).reset_index(drop=True);pd.testing.assert_frame_equal(a,b,check_exact=True)
(R/'SPLIT_ARCHIVE_MANIFEST.json').write_text(json.dumps({'lossless_weight_verification':True,'lossless_scenario_verification':True,'scenario_rows':len(full),'excluded_redundant_monoliths':['results/weight_samples.npz','results/set_scenario_metrics.csv.gz'],'shards':manifest},indent=2)+'\n')
(B/'analysis/OUTPUT_README.md').write_text('''# Output archive and index conventions

All new analysis is reproduced by run_analysis.py. Then run make_report.py and package_results.py.

The repository delivery uses results/weight_samples/*.npz and results/set_scenario_metrics/*.csv.gz as lossless shards. The two corresponding large monoliths may be omitted from GitHub upload; they are reproducibly regenerated locally by the script. SPLIT_ARCHIVE_MANIFEST.json certifies exact array/dataframe equality and records all shard hashes. Concatenate metric shards and sort by space,split,set,scenario to reconstruct the monolithic logical table. Each weight shard has key weights and columns wA,wH,wV. There are 9 weight shards and 54 metrics shards (all six sets, three spaces, three splits), with no omitted scenarios.

NPZ rank_memberships files contain zero-based candidate indices into all630_metrics_memberships.csv in its saved natural numeric pair-ID row order, with one row per weight sample in that space/split. Full per-candidate rank histograms (all ranks 1..630) are in rank_distribution_*.csv.gz. Histograms include all train, test, and replication samples. Every scenario Top10 is preserved in rank_memberships, while complete rank distributions are retained in histogram form.

SUMMARY.json is manuscript-ready structured data. RESULTS_AND_LIMITATIONS.md contains all same-k test/replication results, continuous fixed-set LP results, shortlist evidence, MC precision and caveats. Full fronts are separately labeled, never equal-size comparisons. LP raw candidate objectives may be negative because an individual candidate can be worse than the shortlist at every weight; only their maximum is the set's nonnegative worst-case regret.

Reporting corrections: the initial run was retained for HiGHS-version, rejection-rate and stratified-SE fixes. A subsequent run corrected uint16 cross-space worst-rank subtraction by casting to signed float before differencing. Neither correction changes sampling, candidate rankings, shortlist selection, regret or scientific conclusions. Prior affected files/logs/manifests are preserved in audit/. Do not cite superseded audit output as final results.

All performance data are archived; no physical simulator was run. Missing Honeybee results are explicitly MISSING, never treated as validation success. Rule-level HB evidence and translated-design status are separate.
''')
print('Verified lossless delivery shards',len(manifest),'scenario rows',len(full))
