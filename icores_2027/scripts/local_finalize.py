"""Validate completed local experiments, then derive coordinate-free ledgers.

This script never simulates, edits the protocol or fills absent measurements.
It refuses incomplete runs and preserves cloud ledgers before superseding them.
Readiness and final Git metadata remain a separate author-local integration step.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
I=ROOT/'icores_2027'
P=I/'paper_support'
KEYS=['run_id','config_hash','code_commit','input_hash','measurement_class']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def boolean(series):
    """Parse CSV booleans strictly; missing values are never successful gates."""
    values=series.astype(str).str.lower()
    if not values.isin(['true','false']).all():
        raise ValueError('Non-Boolean evidence value')
    return values.eq('true')


def provenance(row):
    return {key:row[key] for key in KEYS}


def check_experiments(ablation,hb):
    """Evaluate P0 evidence from completed files, independently of STATUS flags."""
    summary=pd.read_csv(ablation/'ablation_summary.csv')
    equality=pd.read_csv(ablation/'ablation_equivalence.csv')
    runtime=pd.read_csv(ablation/'ablation_runtime_records.csv')
    replay=pd.read_csv(hb/'design_translation_recheck.csv')
    mapping=pd.read_csv(hb/'historical_scene_mapping.csv')
    adverse=pd.read_csv(hb/'adverse_ray_explanation.csv')
    geometry=pd.read_csv(hb/'geometry_recheck.csv')
    checks={
        'all_registered_scales_measured':set(summary.subset_size)=={5,20,60,630},
        'three_matched_repeats_each':summary.completed_matched_repetitions.eq(3).all(),
        'every_comparison_equal':boolean(equality.equal).all() and boolean(summary.all_equal).all(),
        'twelve_measured_comparisons':len(equality[equality.stage.eq('measurement')])==12,
        'single_thread_A_B':runtime.threads.eq(1).all(),
        'measured_B_includes_precompute':runtime[runtime.method.eq('B')].precompute_seconds.gt(0).all(),
        'six_legacy_and_four_corrected':len(replay)==10 and replay.model_type.eq('legacy_replay').sum()==6 and replay.model_type.eq('contained_v2').sum()==4,
        'legacy_outputs_exactly_reproduced':boolean(replay[replay.model_type.eq('legacy_replay')].historical_matrix_exact_match).all(),
        'corrected_scenes_monotonic':boolean(replay[replay.model_type.eq('contained_v2')].contained_visibility_monotonic).all(),
        'all_replays_share_points_and_rays':all(boolean(replay[k]).all() for k in ['sensor_and_direction_exact_match','solar_sources_exact_match','time_columns_exact_match']),
        'six_original_models_faces_and_mapping_verified':len(mapping)==6 and all(boolean(mapping[k]).all() for k in ['sensor_id_and_xyz_match','regenerated_faces_match','sun_vectors_match_baseline','temporal_columns_match']),
        'all_recorded_adverse_rays_explained':len(adverse)>0 and adverse.cause.eq('LEGACY_ADDED_OUTSIDE_GEOMETRY_CONFIRMED').all(),
        'corrected_union_solids_contained':boolean(geometry[geometry.scenario.eq('contained_stepback_v2_UNVALIDATED')].solid_contained).all(),
        'frozen20_preserved':sha(ROOT/'project_archive_2026_10_16/research/experiments/baseline_20260909_clean/independent_validation/VALIDATION_SAMPLE_FROZEN.csv')=='ad4abb9b89a263edaecc2cb3553f7832ce0ccb460521ba218e0083e05bcb46b2'
    }
    return {key:bool(value) for key,value in checks.items()}


def frozen_regression(ablation,quality):
    """Audit all630 fresh metrics against frozen outputs, retaining tie drift.

    Floating-score tie order is not forced to match the archival row order.
    Every inversion outside the registered score tolerance is a hard failure.
    """
    fresh=pd.read_csv(ablation/'aggregate_B_m630_r1_run.csv').set_index('pair')
    frozen=pd.read_csv(ROOT/'paper_assets/tables/table_03_candidate_universe.csv').set_index('building_ids')
    if set(fresh.index)!=set(frozen.index) or len(fresh)!=630:
        raise ValueError('Fresh full630 pair universe differs from freeze')
    frozen=frozen.loc[fresh.index]
    columns={'A':'low_area_drop_h3_m2','H':'avg_gain_vs_baseline_h','V':'intervention_volume_m3',
             'N':'new_low_area_h3_m2','score':'score'}
    output=pd.DataFrame({'pair':fresh.index,'new_rank':fresh['rank'].to_numpy(),
                         'archived_rank':frozen.rank_2p5d_score.to_numpy()})
    valid=True
    for new,old in columns.items():
        diff=fresh[new].to_numpy()-frozen[old].to_numpy()
        output[new+'_difference']=diff
        valid=valid and bool(np.max(np.abs(diff))<=(1e-10 if new=='score' else 1e-8))
    oldscore=frozen.score.to_numpy();newrank=fresh['rank'].to_numpy()
    significant=oldscore[:,None]>oldscore[None,:]+1e-10
    inversions=int((significant & (newrank[:,None]>newrank[None,:])).sum())
    for key,value in provenance(fresh.iloc[0]).items():output[key]=value
    output['measurement_class']='RECOMPUTED_FROZEN_VS_NEW_RUN'
    output.to_csv(quality/'canonical630_frozen_regression.csv',index=False)
    return {'all630_metrics_match_frozen_tolerances':bool(valid),
            'no_rank_inversions_outside_score_tolerance':inversions==0}, {
                'rank_changed_count':int(output.new_rank.ne(output.archived_rank).sum()),
                'significant_rank_inversions':inversions,
                'max_absolute_errors':{k:float(output[k+'_difference'].abs().max()) for k in columns}}


def generate(ablation,hb,code_commit):
    """Create auditable new number/claim/difference tables from measured rows."""
    quality=I/'runs/local_quality_20261016';quality.mkdir(parents=True,exist_ok=True)
    checks=check_experiments(ablation,hb)
    regression_checks,regression_detail=frozen_regression(ablation,quality)
    checks.update(regression_checks)
    report={'run_id':'local_integration_20261016','config_hash':sha(I/'configs/ICORES_PROTOCOL.json'),
            'code_commit':code_commit,'measurement_class':'RECOMPUTED_LOCAL_EVIDENCE_GATES',
            'input_hash':sha(ablation/'ablation_summary.csv'),'checks':checks,
            'all_experiment_gates_passed':all(checks.values()),'canonical630_regression':regression_detail,
            'checked_utc':datetime.now(timezone.utc).isoformat()}
    (quality/'experiment_gate_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    if not all(checks.values()):
        raise ValueError('Incomplete/failed experiment gates: '+', '.join(k for k,v in checks.items() if not v))
    cloud=P/'cloud_checkpoint';cloud.mkdir(exist_ok=True)
    for filename in ['PAPER_NUMBERS_ICORES.csv','CLAIM_CORRECTIONS.csv','CLAIMS_LEDGER_ICORES.csv']:
        if not (cloud/filename).exists(): shutil.copy2(P/filename,cloud/filename)
    if not (cloud/'RESULT_DIFF_ICORES.csv').exists():
        shutil.copy2(I/'audit/RESULT_DIFF_ICORES.csv',cloud/'RESULT_DIFF_ICORES.csv')
    summary=pd.read_csv(ablation/'ablation_summary.csv',float_precision='round_trip')
    replay=pd.read_csv(hb/'design_translation_recheck.csv',float_precision='round_trip')
    geom=pd.read_csv(hb/'geometry_recheck.csv',float_precision='round_trip')
    solar=pd.read_csv(hb/'historical_solar_mapping.csv',float_precision='round_trip')
    comparisons=[]
    for _,g in geom[(geom.scope.eq('whole_scene_union')) & geom.scenario.eq('legacy_stepback')].iterrows():
        stem=g.case_id.replace(',','_')
        old_result=replay[replay.scenario.eq(stem+'_design_stepback')].iloc[0]
        fixed=replay[replay.scenario.eq(stem+'_contained_stepback_v2')]
        reused=fixed.empty
        new_result=old_result if reused else fixed.iloc[0]
        rule=geom[geom.case_id.eq(g.case_id) & geom.scope.eq('whole_scene_union') & geom.scenario.eq('rule_flat')].iloc[0]
        corrected=geom[geom.case_id.eq(g.case_id) & geom.scope.eq('whole_scene_union') & geom.scenario.eq('contained_stepback_v2_UNVALIDATED')].iloc[0]
        aggregate_provenance={**provenance(new_result),'code_commit':code_commit,
            'input_hash':hashlib.sha256((sha(hb/'geometry_recheck.csv')+sha(hb/'design_translation_recheck.csv')).encode()).hexdigest(),
            'measurement_class':'RECOMPUTED_REAL_EXPERIMENT_AGGREGATES'}
        comparisons.append(dict(**aggregate_provenance,case_id=g.case_id,
            hb_source_code_commit=new_result.code_commit,geometry_source_code_commit=g.code_commit,
            target_rule_volume_m3=g.target_removed_volume_m3,
            rule_union_removed_m3=rule.actual_removed_volume_m3,
            legacy_union_removed_m3=g.actual_removed_volume_m3,
            corrected_union_removed_m3=corrected.actual_removed_volume_m3,
            legacy_solid_contained=g.solid_contained,corrected_solid_contained=corrected.solid_contained,
            legacy_low_area_reduction_m2=old_result.low_area_drop_h3_m2,
            corrected_low_area_reduction_m2=new_result.low_area_drop_h3_m2,
            legacy_worsened_point_count=old_result.worsened_point_count,
            corrected_worsened_point_count=new_result.worsened_point_count,
            corrected_new_low_area_m2=new_result.new_low_area_h3_m2,
            corrected_result_reuses_unchanged_legacy=reused,
            status='LEGACY_REPRODUCED_AND_EXPLAINED_CORRECTION_VERIFIED',
            geometry_source_sha256=sha(hb/'geometry_recheck.csv'),
            daylight_source_sha256=sha(hb/'design_translation_recheck.csv')))
    pd.DataFrame(comparisons).to_csv(hb/'translation_outcome_comparison.csv',index=False)
    old=pd.read_csv(cloud/'PAPER_NUMBERS_ICORES.csv').fillna('')
    old.loc[old.metric.eq('weighted_day_duration'),'notes']='16*0.5h; actual archived HB/WEA/HOY columns now verified; HB/pvlib effective rays not identical.'
    rows=old[~old.metric.eq('real_matched_ablation_speedup')].to_dict('records')
    def number(metric,value,unit,path,row,notes=''):
        rows.append(dict(metric=metric,value=value,unit=unit,source=str(path.relative_to(I)).replace('\\','/'),
                         status='MEASURED' if 'MEASURED' in str(row['measurement_class']) else 'RECOMPUTED',
                         notes=notes,**provenance(row)))
    for _,r in summary.iterrows():
        m=int(r.subset_size)
        for key,unit in [('A_median_end_to_end_seconds','s'),('B_median_end_to_end_seconds','s'),('measured_speedup','ratio')]:
            number(f'local_ablation_m{m}_{key}',r[key],unit,ablation/'ablation_summary.csv',r,
                   'Same primitive and single thread; B includes precompute; three measured repeats; frozen canonical approximate geometry')
    full=summary[summary.subset_size.eq(630)].iloc[0]
    number('real_matched_ablation_speedup',full.measured_speedup,'ratio',ablation/'ablation_summary.csv',full,
           '630 vs630; measured, not extrapolated; only fresh-intersection vs blocker-reuse implementations')
    for _,r in replay.iterrows():
        for key,unit in [('mean_hours','h'),('mean_gain_h','h'),('low_area_h3_m2','m2'),
                         ('low_area_drop_h3_m2','m2'),('new_low_area_h3_m2','m2'),('worsened_point_count','count')]:
            number('local_HB_'+r.scenario+'_'+key,r[key],unit,hb/'design_translation_recheck.csv',r,
                   'New controlled solver replay on frozen canonical geometry, not surveyed as-built or weather validation')
    for _,r in geom[geom.scope.eq('whole_scene_union')].iterrows():
        for key in ['actual_removed_volume_m3','target_removed_volume_m3','outside_volume_m3']:
            number('local_geometry_'+r.case_id.replace(',','_')+'_'+r.scenario+'_'+key,r[key],'m3',hb/'geometry_recheck.csv',r,
                   'Union-integrated volume differs from nominal sum-of-building rule budget; no volume-matching claim')
    for key in ['elevation_difference_deg','azimuth_difference_deg']:
        number('local_actual_HB_pvlib_max_abs_'+key,float(solar[key].abs().max()),'deg',hb/'historical_solar_mapping.csv',solar.iloc[0],
               'Actual archived solar source columns mapped to local slots; the two engines do not have identical effective rays')
    overlap=pd.read_csv(hb/'footprint_overlap_audit.csv')
    adverse=pd.read_csv(hb/'adverse_ray_explanation.csv')
    for metric,value,source,row in [
        ('local_HB_replay_scene_count',len(replay),hb/'design_translation_recheck.csv',replay.iloc[0]),
        ('local_corrected_scene_count',int(replay.model_type.eq('contained_v2').sum()),hb/'design_translation_recheck.csv',replay.iloc[0]),
        ('local_explained_adverse_ray_events',len(adverse),hb/'adverse_ray_explanation.csv',adverse.iloc[0]),
        ('canonical_positive_overlap_pair_count',len(overlap),hb/'footprint_overlap_audit.csv',overlap.iloc[0]),
        ('canonical_identical_footprint_pair_count',int(boolean(overlap.identical_footprints).sum()),hb/'footprint_overlap_audit.csv',overlap.iloc[0])]:
        number(metric,value,'count',source,row,'Conditional on frozen canonical approximation; not surveyed geometry certification')
    pd.DataFrame(rows).to_csv(P/'PAPER_NUMBERS_ICORES.csv',index=False)
    corrections=pd.read_csv(cloud/'CLAIM_CORRECTIONS.csv').fillna('')
    replacements={
        'C06':('CORRECTED_ACTUAL_COLUMNS_VERIFIED','Actual16 ordered half-hour solar columns and WEA/HOY source IDs verified; integrated duration8h, endpoint span7.5h. HB/pvlib rays differ measurably; not identical-solar validation.'),
        'C08':('EXPLAINED_AND_CORRECTED_WITHIN_FROZEN_MODEL','Actual adverse rays hit C24 upper walls outside its original footprint; historical negative results retained. Controlled contained-v2 replays have no adverse visibility events. Not an unavoidable subtraction trade-off.'),
        'C09':('ACTUAL_UNION_VOLUME_AUDITED','Report nominal per-building rule volume separately from union-integrated removed solid volume. Canonical footprints overlap; neither translated volume matching nor a physically exact construction budget is established.'),
        'C10':('MEASURED_REAL_INPUT_MATCHED_ABLATION','Registered5/20/60/630 prefixes have three same-primitive single-thread matched repeats; pointwise DSH, A/H/V/N, score, rank and Pareto equivalent. B includes precompute. Speedup applies only to these implementations on this frozen approximate canonical model.'),
        'C14':('SYNTHETIC_AND_REAL_SCOPES_DISTINGUISHED','Synthetic holes/silent-face/height-clamp defects remain regressions. Actual45-footprint site has no holes and all six archived face dictionaries regenerate exactly; four of five legacy translations escape containment. Corrected versions tested separately.')}
    hbprov=provenance(replay.iloc[0]);abprov=provenance(full)
    for id,(status,claim) in replacements.items():
        mask=corrections.claim_id.eq(id)
        corrections.loc[mask,['status','corrected_claim']]=[status,claim]
        for k,v in (abprov if id=='C10' else hbprov).items(): corrections.loc[mask,k]=v
    extra=[
        ('C15','Canonical DXF-derived footprints are exact real building boundaries','Canonical source is DXF component-bbox union, with shared/overlapping footprints and archived OBJ disagreement. Case results are conditional on this approximation; do not claim as-built accuracy or verified site intervention feasibility.','LIMITATION_UNCHANGED_INPUTS','G2'),
        ('C16','Cloud normalization source hash exactly identifies the tracked file','An explicit pre-benchmark amendment pins actual committed bytes and an independent frozen reference with all630 pairs and metrics agreeing within existing tolerance. Original mismatched hash and failure are retained.','PROVENANCE_CORRECTION','G3')]
    more=[dict(claim_id=id,old_claim=old,corrected_claim=new,status=st,stage=stage,**(abprov if stage=='G3' else hbprov)) for id,old,new,st,stage in extra]
    corrections=pd.concat([corrections,pd.DataFrame(more)],ignore_index=True)
    corrections.to_csv(P/'CLAIM_CORRECTIONS.csv',index=False)
    pd.DataFrame([dict(claim_id=r.claim_id,claim=r.corrected_claim,status=r.status,
        evidence='paper_support/CLAIM_CORRECTIONS.csv',release_scope='PRIVATE_REVIEW_ONLY',**provenance(r))
        for _,r in corrections.iterrows()]).to_csv(P/'CLAIMS_LEDGER_ICORES.csv',index=False)
    pd.DataFrame([dict(item=r.claim_id,old=r.old_claim,new=r.corrected_claim,reason=r.status,
        affected_stage=r.stage,**provenance(r)) for _,r in corrections.iterrows()]).to_csv(I/'audit/RESULT_DIFF_ICORES.csv',index=False)
    make_figures(summary,replay,ablation,hb,code_commit)
    return report


def make_figures(summary,replay,ablation,hb,code_commit):
    """Native vector plots contain aggregate metrics only, never real geometry."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','pdf.fonttype':42})
    out=P/'figures';out.mkdir(exist_ok=True)
    fig,ax=plt.subplots(figsize=(7,4.2))
    for method,color in [('A','#28759c'),('B','#d27924')]:
        ax.plot(summary.subset_size,summary[f'{method}_median_end_to_end_seconds'],marker='o',color=color,
                label='A: fresh intersections' if method=='A' else 'B: reuse (including precompute)')
    ax.set(xscale='log',yscale='log',xlabel='Candidate count (matched prefixes)',ylabel='Median end-to-end seconds')
    ax.legend(frameon=False);ax.grid(alpha=.2);fig.tight_layout()
    save_figure(fig,'local_matched_ablation',out,ablation/'ablation_summary.csv',summary.iloc[0],code_commit)
    plt.close(fig)
    legacy=replay[replay.model_type.eq('legacy_replay') & ~replay.scenario.eq('baseline')].copy()
    corrected=replay[replay.model_type.eq('contained_v2')]
    fig,axes=plt.subplots(1,2,figsize=(9,4.2))
    xs=np.arange(len(legacy));width=.35
    for ax,key,ylabel in zip(axes,['low_area_drop_h3_m2','worsened_point_count'],['Low-sun area reduction (m²)','Net worsened receiving points']):
        values=[]
        for _,r in legacy.iterrows():
            name=r.scenario.replace('design_stepback','contained_stepback_v2')
            selected=corrected[corrected.scenario.eq(name)]
            values.append(r[key] if selected.empty else selected.iloc[0][key])
        ax.bar(xs-width/2,legacy[key],width,label='Legacy replay',color='#28759c')
        ax.bar(xs+width/2,values,width,label='Contained v2*',color='#d27924')
        ax.set(xticks=xs,xticklabels=[s.replace('_design_stepback','').replace('_','/') for s in legacy.scenario],ylabel=ylabel)
        ax.tick_params(axis='x',labelrotation=30);ax.grid(axis='y',alpha=.2)
    axes[0].legend(frameon=False,fontsize=8)
    fig.text(.5,.005,'*C9/C13 already contained: unchanged legacy result reused, not an extra solver run.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1))
    save_figure(fig,'local_translation_recheck',out,hb/'design_translation_recheck.csv',replay.iloc[0],code_commit)
    plt.close(fig)


def save_figure(fig,name,out,source,row,code_commit):
    files={}
    for suffix in ['svg','pdf','png']:
        path=out/f'{name}.{suffix}';fig.savefig(path,dpi=300)
        if suffix=='svg' and any(e.tag.endswith('image') for e in ET.parse(path).iter()):
            raise ValueError('Vector plot unexpectedly embeds a raster image')
        files[path.name]=sha(path)
    record={'figure':name,'source_table':str(source.relative_to(I)).replace('\\','/'),
        'source_sha256':sha(source),'script':'icores_2027/scripts/local_finalize.py',
        'script_sha256':sha(Path(__file__)),'artifact_build_commit':code_commit,
        'files':files,'geometry_exposed':False,
        'release_scope':'PRIVATE_REVIEW_ONLY','formats':{'svg':'native vector','pdf':'native vector','png':'300 dpi'},
        **provenance(row)}
    (out/f'{name}_manifest.json').write_text(json.dumps(record,indent=2),encoding='utf-8')


def run_tests(code_commit):
    """Capture an actual local integrated pytest run and reproducibility metadata."""
    out=I/'runs/local_quality_20261016';out.mkdir(exist_ok=True,parents=True)
    start=datetime.now(timezone.utc).isoformat()
    command=[sys.executable,'-m','pytest','-q','icores_2027/tests','icores_2027/formatting/test_anonymity.py']
    done=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
    (out/'integrated_final.log').write_text(done.stdout,encoding='utf-8')
    record={'run_id':'local_quality_20261016','config_hash':sha(I/'configs/ICORES_PROTOCOL.json'),
        'code_commit':code_commit,'input_hash':hashlib.sha256(''.join(sha(p) for p in sorted((I/'tests').glob('test*.py'))).encode()).hexdigest(),
        'working_status_sha256':sha(I/'STATUS.json'),
        'paper_numbers_sha256':sha(P/'PAPER_NUMBERS_ICORES.csv'),
        'measurement_class':'MEASURED_LOCAL_TEST_EXECUTION','command':command[1:],
        'started_utc':start,'ended_utc':datetime.now(timezone.utc).isoformat(),'exit_code':done.returncode,
        'stdout_sha256':sha(out/'integrated_final.log')}
    (out/'test_execution.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(done.stdout,flush=True)
    if done.returncode: raise RuntimeError('Actual local tests failed; log retained')
    return record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code-commit',required=True)
    parser.add_argument('--tests-only',action='store_true')
    args=parser.parse_args()
    if not args.tests_only:
        generate(I/'runs/local_ablation_20261016',I/'runs/local_hb_20261016',args.code_commit)
    run_tests(args.code_commit)


if __name__=='__main__': main()
