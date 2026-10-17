from pathlib import Path
import csv,json,re,hashlib,datetime
import fitz
ROOT=Path(__file__).resolve().parent
repo='https://github.com/eksn425-del/light-right-repair-ai-prototype/blob/af486946b210b12853b83f9dbdaf708255754d56/'
entries=[
('Abstract; 3.1','45 building groups; 36 eligible; choose two; 630 pairs','icores_2027/paper_support/METHOD_SPEC.md','Sections 1,8','C15','Eligibility is a research input; canonical bbox-union model, not as-built or legal permission.'),
('3.1 Eq.2','Uniform height-reduction rule with 3m floor and min(3m,25% height)','icores_2027/paper_support/METHOD_SPEC.md','Section 1','','Fixed-footprint rule; translated stepbacks are separate.'),
('3.2','2031 points, 3m grid, z0.1m,16 half-hour samples,8h integration','icores_2027/paper_support/METHOD_SPEC.md','Section 2','C06','Endpoint span7.5h is not sum of integration weights; discrete samples.'),
('3.2;5.3','Constant DNI1000/DHI0; north0 assumption; HB/pvlib rays differ','icores_2027/paper_support/METHOD_SPEC.md','Section 2','C06;C07','No measured-weather/annual/identical-year-specific validation.'),
('3.2','Latent below-horizon counting bug; saved16slots above horizon','icores_2027/paper_support/CLAIM_CORRECTIONS.csv','C12','C12','Not proof frozen run is affected; explicit mask required for extensions.'),
('3.3 Eqs.4–9','A/H/V/N definitions and fixed normalization/preferences','icores_2027/paper_support/METHOD_SPEC.md','Section 3','C02;C09','V additive nominal proxy with overlaps; weights preferences, not learned accuracy.'),
('Table1','Full630 normalization bounds','icores_2027/runs/statistics_20261016/normalization_bounds.csv','All rows','C02','No refitting on selected cohorts or clipping HB values.'),
('3.3','N=0 throughout; constant score contribution.05','icores_2027/paper_support/CLAIMS_LEDGER_ICORES.csv','C02','C02','N-only weight cannot discriminate; A/H-changing scenarios do not isolate N.'),
('3.3;4.2','A-max/V-min Pareto; sorting and direct scan costs','icores_2027/paper_support/METHOD_SPEC.md','Sections 3,5','','Two-objective front; no four-objective or novel-general-OR claim.'),
('4.1 Eqs.10–11','Exact signed-count blocker reuse identity','icores_2027/paper_support/METHOD_SPEC.md','Section 4','','Conditional on same primitive, independent contributions and fixed unselected geometry.'),
('4.2','2BPT=2924640 bytes≈2.79MiB','icores_2027/paper_support/METHOD_SPEC.md','Section 5','','Analytic two-array storage only, not measured process peak memory.'),
('4.3;6.3','Containment implies no new opaque-ray obstruction under fixed rays','icores_2027/paper_support/METHOD_SPEC.md','Section 7','C08','Set-subset argument; not a general imported-mesh guarantee.'),
('5.1;6.2','Curated23 and frozen coverage20 remain separate and unchanged','icores_2027/paper_support/CLAIMS_LEDGER_ICORES.csv','C04;C05','C04;C05','Same-site nonprobability coverage; hash proves bytes, not temporal ordering.'),
('5.1','Pre-benchmark source-identity amendment and retained failure','icores_2027/paper_support/CLAIMS_LEDGER_ICORES.csv','C16','C16','No outcome-adaptive normalization change.'),
('5.2','Hardware/software/thread/time accounting','icores_2027/runs/local_ablation_20261016/ablation_environment.json','Environment and source metadata','C10','CPU brand/model not guessed; RSS unknown.'),
('Abstract;6.1;Table2;Figure1;Conclusion','5/20/60/630 medians,three repeats,B includes precompute,ratio482.927','icores_2027/runs/local_ablation_20261016/ablation_summary.csv','All four rows','C10','Two single-thread no-index same-primitive implementations only; A630 measured.'),
('5.2;6.1','Pointwise DSH/metrics/score/rank/Pareto equivalence','icores_2027/audit/LOCAL_FINAL_REPORT.md','Section 3','C10','Matched implementation agreement, not external solver equivalence.'),
('6.1','630 ranking unchanged; zeroA/H/N,maxV9.09e-13,maxscore4.44e-16','icores_2027/paper_support/PAPER_NUMBERS_ICORES.csv','canonical630_regression_*','','Floating roundoff only; consistency with frozen model is not real-site accuracy.'),
('Abstract;6.2;Table3;Figure2;Conclusion','Same-metric Spearman,MAE,exact match counts bycohort','icores_2027/runs/statistics_20261016/same_metric_agreement.csv','Six cohort/metric rows','C01;C03;C04','Descriptive; no population inference;0.45m2 fromone9m2 discrepancy, not subgrid precision.'),
('Figure2','Candidate scatter values','icores_2027/runs/statistics_20261016/comparison_values.csv','curated23 and heldout20 rows','C03;C04','Frozen aggregate replot; coincident points retained without jitter.'),
('6.2','Coverage20 A exact-five overlap.8→1, boundary6vs7','icores_2027/runs/statistics_20261016/topk_tie_audit.csv','heldout20,A,k5:source_row_order,pair_key_natural_numeric,include_boundary_ties','C11','Tie-definition sensitivity; not model improvement or global630 recall.'),
('5.4;6.3','Six historical replays plus four corrections; C9/C13 reused unchanged','icores_2027/audit/LOCAL_FINAL_REPORT.md','Sections1,2','C08;C14','Ten actual scenes, not11; original20 not rerun.'),
('6.3;Figure3','Adverse walls and four worsenedpoints in each C24 case; correctedzero','icores_2027/runs/local_hb_20261016/translation_outcome_comparison.csv','C9,C24 and C13,C24 rows','C08','Actualray explanation in finalreport; conditional frozenmodel/grid/rays.'),
('6.3;Figure3','Five historical/corrected A values; reuse flag','icores_2027/runs/local_hb_20261016/translation_outcome_comparison.csv','All five rows','C08;C14','Only fournew corrections; preserved adversehistory; notvolumematched.'),
('6.3;Table4','NominalV versus rule/legacy/corrected netunionreduction','icores_2027/runs/local_hb_20261016/translation_outcome_comparison.csv','Four volume columns acrossfive rows','C09','Signed baseline−candidate unionvolume; noncontainedlegacy includesaddedvolume; notgrossremoval.'),
('3.1;7.2','Boundingboxunions,overlaps/sharedcomponents,OBJdisagreement','icores_2027/paper_support/CLAIMS_LEDGER_ICORES.csv','C15','C15','Conditional canonical fidelity; do notgeneralize asbuiltaccuracy.'),
('6.3;7.2','Actual noholes,facesregenerate,syntheticdefectsnotactualcause','icores_2027/paper_support/CLAIMS_LEDGER_ICORES.csv','C14','C14','Synthetic and actual evidence remain separated.'),
('7.3','112 passing integratedtests; raw restricted inputsnotreleased','icores_2027/audit/LOCAL_FINAL_REPORT.md','Section6','','Software regression coverage only; private package not anonymous supplement.')]
with (ROOT/'CLAIM_SOURCE_MAP.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['manuscript_location','claim','frozen_source_path','source_selector','ledger_ids','interpretation_boundary','verified_source_url'])
 for a in entries:w.writerow([*a,repo+a[2]])
# Independent values-to-LaTeX-table check, not a rerun of experiments.
def rows(p):return list(csv.DictReader((ROOT/'evidence/icores_2027'/p).open()))
s=(ROOT/'manuscript.tex').read_text();checks=[]
for r in rows('runs/local_ablation_20261016/ablation_summary.csv'):
 for k in ['A_median_end_to_end_seconds','B_median_end_to_end_seconds','measured_speedup']:
  v=f"{float(r[k]):,.3f}";checks.append({'source':k,'value':v,'present':v in s})
for r in rows('runs/local_hb_20261016/translation_outcome_comparison.csv'):
 for k in ['target_rule_volume_m3','rule_union_removed_m3','legacy_union_removed_m3','corrected_union_removed_m3']:
  v=f"{float(r[k]):,.3f}";checks.append({'source':r['case_id']+':'+k,'value':v,'present':v in s})
for r in rows('runs/statistics_20261016/same_metric_agreement.csv'):
 for k in ['spearman_rho','mae']:
  v=f"{float(r[k]):.6f}";checks.append({'source':r['comparison_set']+':'+r['comparison']+':'+k,'value':v,'present':v in s})
assert all(c['present'] for c in checks)
(ROOT/'qa/NUMERIC_TRANSCRIPTION_CHECK.json').write_text(json.dumps({'checks':checks,'passed':len(checks),'failed':0,'scope':'Displayed timing,cohortstatistics andvolumetable values matched source rounding. No new experiment.'},indent=2))
