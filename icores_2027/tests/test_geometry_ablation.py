"""Executed synthetic/source regressions; none validate the withheld real scene."""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from geometry_audit import (GeometryAuditError, LEGACY_2P5D, Prism, contained_stepback_v2,
    containment_report, emitted_prism_layers, legacy_layers, load_legacy_functions,
    match_sensors, polygon_parts, protocol, ray_hit, safe_face, safe_prism_shades,
    synthetic_fixtures, union_volume, validate_polygon)


@pytest.mark.parametrize('name', ['rectangle','concave_u','courtyard_hole','multipart'])
def test_contained_v2_is_subset_for_all_fixture_topologies(name):
    geom=synthetic_fixtures()[name]
    base=[Prism(geom,0,12,'base')]
    fixed=contained_stepback_v2(geom,12,name)
    report=containment_report(base,fixed)
    assert report['solid_contained']
    assert report['outside_volume_m3'] == pytest.approx(0,abs=1e-8)
    assert report['actual_removed_volume_m3'] >= 0
    assert all(p.footprint.is_valid for p in fixed)


@pytest.mark.parametrize('name', ['concave_u','courtyard_hole'])
def test_actual_legacy_scaling_has_canonical_containment_counterexamples(name):
    geom=synthetic_fixtures()[name]
    layers,_=legacy_layers(geom,12)
    report=containment_report([Prism(geom,0,12,'base')],layers)
    assert not report['solid_contained']
    assert report['outside_area_max_m2'] > 5


def test_legacy_rectangle_target_volume_matches_prism_union():
    geom=synthetic_fixtures()['rectangle']
    layers,row=legacy_layers(geom,12)
    report=containment_report([Prism(geom,0,12,'base')],layers)
    assert report['solid_contained']
    assert report['actual_removed_volume_m3'] == pytest.approx(row['removed_volume_m3'])


def test_clipping_changes_volume_and_is_not_advertised_as_volume_match():
    geom=synthetic_fixtures()['concave_u']
    old,row=legacy_layers(geom,12)
    fixed=contained_stepback_v2(geom,12)
    report=containment_report([Prism(geom,0,12,'base')],fixed)
    assert report['actual_removed_volume_m3'] > row['removed_volume_m3']+40
    assert union_volume(fixed) < union_volume(old)


def test_actual_legacy_faces_drop_hole_but_safe_wrapper_preserves_it():
    geom=synthetic_fixtures()['courtyard_hole']
    ns=load_legacy_functions(['face','clean_id','prism_shades'])
    old=ns['prism_shades']('courtyard',geom,0,12)
    new=safe_prism_shades('courtyard_safe',geom,0,12)
    assert len(old)==5  # exterior roof + four outer walls, no courtyard walls
    assert old[0].geometry.area==pytest.approx(100)
    assert geom.area==84
    assert len(new)==10 # roof + bottom + both four-wall rings
    roof=next(f for f in new if f.identifier.endswith('_roof'))
    assert roof.geometry.area==pytest.approx(84)
    assert len(roof.geometry.holes)==1


def test_actual_emitted_hole_envelope_volume_differs_from_reported_target():
    geom=synthetic_fixtures()['courtyard_hole']
    old,row=legacy_layers(geom,12)
    base,_=legacy_layers(geom,12,'baseline')
    actual=union_volume(emitted_prism_layers(base))-union_volume(emitted_prism_layers(old))
    assert row['removed_volume_m3']==pytest.approx(252)
    assert actual==pytest.approx(300)


def test_face_errors_are_exposed_not_silently_dropped():
    ns=load_legacy_functions(['face','clean_id'])
    pts=[(0,0,0),(1,0,0)]
    assert ns['face']('legacy_bad',pts) is None
    with pytest.raises(GeometryAuditError,match='FACE_BUILD_FAILED B7_face2'):
        safe_face('B7_face2',pts)


def test_nonplanar_and_degenerate_faces_fail_fast():
    with pytest.raises(GeometryAuditError):
        safe_face('nonplanar',[(0,0,0),(1,0,0),(1,1,1),(0,1,0)])
    with pytest.raises(GeometryAuditError):
        safe_face('collinear',[(0,0,0),(1,0,0),(2,0,0)])


def test_invalid_polygon_is_not_implicitly_buffer_repaired():
    invalid=Polygon([(0,0),(2,2),(0,2),(2,0),(0,0)])
    with pytest.raises(GeometryAuditError):
        validate_polygon(invalid)
    with pytest.raises(GeometryAuditError):
        safe_prism_shades('bowtie',invalid,0,3)


def test_union_volume_deduplicates_overlapping_components_and_z_slabs():
    layers=[Prism(box(0,0,2,2),0,4,'a'),Prism(box(1,0,3,2),2,6,'b')]
    assert sum(p.footprint.area*(p.z1-p.z0) for p in layers)==32
    assert union_volume(layers)==pytest.approx(28)
    assert union_volume(layers+layers)==pytest.approx(28)


def test_multipart_faces_and_union_volume():
    geom=MultiPolygon([box(0,0,2,2),box(5,0,7,2)])
    assert len(safe_prism_shades('multipart',geom,0,3))==12
    assert union_volume([Prism(geom,0,3,'multipart')])==24


def test_containment_detects_extra_z_volume():
    base=[Prism(box(0,0,2,2),0,3,'base')]
    modified=[Prism(box(0,0,2,2),0,4,'above')]
    report=containment_report(base,modified)
    assert not report['solid_contained']
    assert report['outside_volume_m3']==4


def sensor_fixture():
    return pd.DataFrame({'grid_id':['G1','G2'],'x':[0.,3.],'y':[0.,0.],'z':[.1,.1]})


def test_sensor_reorder_requires_ids_and_coordinates():
    ref=sensor_fixture()
    assert match_sensors(ref,ref.iloc[::-1]).tolist()==[1,0]
    wrong=ref.copy(); wrong.loc[:,'x']=list(reversed(wrong.x))
    with pytest.raises(GeometryAuditError,match='different coordinates'):
        match_sensors(ref,wrong)


@pytest.mark.parametrize('kind',['duplicate','missing','coordinate','nonfinite'])
def test_bad_sensor_mapping_fails(kind):
    ref=sensor_fixture(); c=ref.copy()
    if kind=='duplicate': c.loc[1,'grid_id']='G1'
    if kind=='missing': c.loc[1,'grid_id']='G3'
    if kind=='coordinate': c.loc[1,'x']+=1e-4
    if kind=='nonfinite': c.loc[1,'z']=np.nan
    with pytest.raises(GeometryAuditError): match_sensors(ref,c)


def test_legacy_nighttime_bug_reproduced_through_production_functions():
    names=['min_projected_distance','precompute_blockers','geoms_unary_bounds',
           'hours_from_blocked','reduced_height']
    ns=load_legacy_functions(names,source=LEGACY_2P5D)
    buildings=pd.DataFrame({'building_id':['C1'],'height_m':[12.]})
    grid=sensor_fixture().iloc[:1]
    solar=pd.DataFrame({'apparent_elevation_deg':[-10.], 'dx':[1.], 'dy':[0.], 'tan_altitude':[-.176]})
    orig,_=ns['precompute_blockers'](buildings,grid,{'C1':box(2,2,3,3)},solar)
    assert not orig.any()
    # The production generator skips the night ray, but aggregation calls it visible.
    assert ns['hours_from_blocked'](orig.sum(axis=0)>0,1,1,30)[0]==.5


def test_monotone_prism_reduction_and_no_night_hit():
    base=[Prism(box(2,-1,4,1),0,12,'base')]
    lower=[Prism(box(2,-1,4,1),0,3,'lower')]
    assert ray_hit([], (0,0,.1),(1,0),45) is None
    assert ray_hit(base,(0,0,.1),(1,0),45) is not None
    assert ray_hit(base,(0,0,.1),(1,0),-10) is None
    for altitude in [5,15,30,45,60,80]:
        if ray_hit(lower,(0,0,.1),(1,0),altitude):
            assert ray_hit(base,(0,0,.1),(1,0),altitude)


def test_production_concave_envelope_can_add_an_actual_ray_blocker():
    geom=synthetic_fixtures()['concave_u']
    old,_=legacy_layers(geom,12)
    b,_=legacy_layers(geom,12,'baseline')
    original=emitted_prism_layers(b); modified=emitted_prism_layers(old)
    found=False
    for layer in modified:
        added=layer.footprint.difference(geom)
        for part in polygon_parts(added):
            p=part.representative_point()
            for direction in [(1,0),(-1,0),(0,1),(0,-1)]:
                if not ray_hit(original,(p.x,p.y,.1),direction,89) and ray_hit(modified,(p.x,p.y,.1),direction,89):
                    found=True
    assert found


def ablation_fixture():
    buildings=pd.DataFrame({'building_id':['C1','C2','C3'], 'height_m':[12.,9.,6.],
                           'canonical_area_m2':[4.,4.,4.], 'movable':[True]*3,'protected':[False]*3})
    geoms={'C1':box(2,-1,4,1),'C2':box(5,2,7,4),'C3':box(-4,-1,-2,1)}
    grid=pd.DataFrame({'sensor_id':['S1','S2','S3'],'x':[0.,0.,0.], 'y':[0.,2.,5.], 'z':[.1]*3})
    solar=pd.DataFrame({'apparent_elevation_deg':[30.,60.,-5.], 'dx':[1.,-1.,1.], 'dy':[0.,0.,0.],
                        'tan_altitude':np.tan(np.radians([30.,60.,-5.]))})
    return buildings,grid,geoms,solar,[('C1','C2'),('C1','C3'),('C2','C3')]


def test_matched_ablation_pointwise_metrics_scores_and_ranking_equal():
    from matched_ablation import evaluate_method,compare_results
    buildings,grid,geoms,solar,pairs=ablation_fixture()
    analysis=protocol()['analysis']
    a=evaluate_method('A',buildings,grid,geoms,solar,pairs,analysis)
    b=evaluate_method('B',buildings,grid,geoms,solar,pairs,analysis)
    assert np.array_equal(a.candidate_hours,b.candidate_hours)
    assert np.all(a.candidate_hours>=a.baseline_hours-1e-9)
    for field in ['A','H','V','N','score','rank','is_pareto_front']:
        assert np.array_equal(a.metrics[field],b.metrics[field])
    assert a.primitive_calls>b.primitive_calls
    result=compare_results(a,b,protocol()['tolerances'])
    assert result['equal']
    assert np.all(a.metrics.N==0)


def test_safe_ablation_hours_mask_nighttime():
    from matched_ablation import hours_from_blocked
    _,grid,_,solar,_=ablation_fixture()
    hours=hours_from_blocked(np.zeros(len(grid)*len(solar),dtype=bool),len(grid),solar,30)
    assert np.array_equal(hours,np.ones(len(grid)))


def test_real_cli_loader_rejects_missing_manifest(tmp_path):
    from matched_ablation import load_real_inputs,ReadinessError
    with pytest.raises((ReadinessError,FileNotFoundError)):
        load_real_inputs(tmp_path/'absent.json',protocol())


def test_production_minimum_area_fraction_can_break_target_volume_match():
    geom=box(0,0,10,10)
    layers,reported=legacy_layers(geom,4.01)
    actual=union_volume([Prism(geom,0,4.01,'base')])-union_volume(layers)
    assert reported['removed_volume_m3']==pytest.approx(100.25)
    assert actual==pytest.approx(95.95)
    assert actual!=pytest.approx(reported['removed_volume_m3'])


def production_runtime(tmp_path):
    root=Path(__file__).resolve().parents[2]
    sys.path.insert(0,str(root/'research_reproducibility/src'))
    from research_runtime import load_runtime
    return load_runtime(root/'research_reproducibility/configs/research.yaml',run_dir=tmp_path/'runtime')


def test_real_canonical_attributes_yield_exact_36_and_630_frozen_pairs(tmp_path):
    import itertools
    runtime=production_runtime(tmp_path)
    from research_runtime import strict_bool
    root=Path(__file__).resolve().parents[2]
    b=pd.read_csv(root/'project_archive_2026_10_16/research/data/derived/canonical_site_v2/canonical_buildings.csv')
    assert len(b)==45
    eligible=b[b.movable.map(strict_bool)&~b.protected.map(strict_bool)&(b.height_m>runtime.height_floor_m)]
    assert len(eligible)==36
    pairs=list(itertools.combinations(eligible.building_id,2))
    assert len(pairs)==len(set(pairs))==630
    assert all(a!=b for a,b in pairs)
    assert pairs==[tuple(p) for p in protocol()['benchmark']['candidate_order']]


@pytest.mark.parametrize('value,expected',[('False',False),('false',False),('0',False),('true',True),('1',True),(False,False),(True,True)])
def test_production_strict_bool_does_not_use_string_truthiness(value,expected,tmp_path):
    production_runtime(tmp_path)
    from research_runtime import strict_bool
    assert strict_bool(value) is expected


@pytest.mark.parametrize('value',[None,np.nan,'unknown','',2])
def test_production_strict_bool_rejects_ambiguous_values(value,tmp_path):
    production_runtime(tmp_path)
    from research_runtime import strict_bool
    with pytest.raises(ValueError): strict_bool(value,field='movable')


def test_registered_parameters_match_resolved_production_source(tmp_path):
    runtime=production_runtime(tmp_path); a=protocol()['analysis']
    correspondence={'grid_size_m':'grid_m','sensor_height_m':'sensor_height_m',
                    'low_threshold_h':'threshold_h','latitude':'latitude','longitude':'longitude',
                    'north_deg':'north_deg','height_floor_m':'height_floor_m',
                    'height_reduction_cap_m':'height_cap_m','height_reduction_fraction':'height_fraction',
                    'timestep_minutes':'step_minutes','timezone':'timezone','utc_offset_hours':'utc_offset'}
    for production_name,registered_name in correspondence.items():
        assert getattr(runtime,production_name)==a[registered_name]
    assert runtime.analysis_date==a['date']
    assert [runtime.start_time,runtime.end_time]==a['times_local']
    assert list(runtime.score_weights.values())==protocol()['scoring_weights']
    assert len(runtime.analysis_datetimes())==16
    from geometry_audit import reduced_height
    for h in [3.,4.,4.01,6.,12.,30.]:
        assert runtime.reduced_height(h)==reduced_height(h,a)


@pytest.mark.parametrize('kind',['blank_id','duplicate_xyz'])
def test_sensor_mapping_rejects_ambiguous_identity(kind):
    ref=sensor_fixture(); candidate=ref.copy()
    if kind=='blank_id': candidate.loc[0,'grid_id']=''
    else: candidate.loc[1,['x','y','z']]=candidate.loc[0,['x','y','z']]
    with pytest.raises(GeometryAuditError): match_sensors(ref,candidate)


def test_real_loader_refuses_explicit_toy_measurement_class(tmp_path):
    import json
    from matched_ablation import load_real_inputs,ReadinessError
    path=tmp_path/'toy_manifest.json'
    path.write_text(json.dumps({'measurement_class':'SYNTHETIC_TEST'}))
    with pytest.raises(ReadinessError,match='Synthetic/toy'):
        load_real_inputs(path,protocol())


def test_synthetic_speedup_cannot_be_reported():
    from matched_ablation import speedup_if_equal
    with pytest.raises(ValueError,match='forbidden'):
        speedup_if_equal(2,1,{'equal':True},'SYNTHETIC_UNIT_TEST_ONLY')
    with pytest.raises(ValueError,match='equality'):
        speedup_if_equal(2,1,{'equal':False},'MEASURED_REAL_SITE')


def test_ablation_equivalence_rejects_corrupted_pointwise_result():
    from matched_ablation import evaluate_method,compare_results
    buildings,grid,geoms,solar,pairs=ablation_fixture()
    a=evaluate_method('A',buildings,grid,geoms,solar,pairs,protocol()['analysis'])
    b=evaluate_method('B',buildings,grid,geoms,solar,pairs,protocol()['analysis'])
    b.candidate_hours[0,0]+=.5
    assert not compare_results(a,b,protocol()['tolerances'])['equal']


def test_real_form_manifest_cannot_skip_private_provenance(tmp_path):
    import json
    from matched_ablation import load_real_inputs,ReadinessError
    manifest=tmp_path/'missing_provenance.json'
    manifest.write_text(json.dumps({'measurement_class':'REAL_SITE','site':protocol()['site']}))
    with pytest.raises(ReadinessError,match='provenance'):
        load_real_inputs(manifest,protocol())


def test_real_form_manifest_checks_file_hash_before_using_coordinates(tmp_path):
    import json
    from matched_ablation import load_real_inputs,ReadinessError
    dummy=tmp_path/'hash_probe.txt'; dummy.write_text('Synthetic negative-test payload, not scene data')
    manifest=tmp_path/'bad_hash.json'
    manifest.write_text(json.dumps({'measurement_class':'REAL_SITE','site':protocol()['site'],
        'source_run':'baseline_20260909_clean','coordinate_frame':'synthetic negative-test schema only',
        'units':'m','north_deg':0,'private_runtime_authorized':True,'sensor_order_preserved':True,
        'solar_mode':'new_pvlib_protocol','solar_version':'test-rejected-before-generation',
        'inputs':{'building_csv':{'path':dummy.name,'sha256':'0'*64}}}))
    with pytest.raises(ReadinessError,match='SHA256 mismatch'):
        load_real_inputs(manifest,protocol())


def test_real_geometry_cli_reports_blocker_without_running(tmp_path,monkeypatch,capsys):
    import geometry_audit
    monkeypatch.setattr(sys,'argv',['geometry_audit.py','--real-manifest',str(tmp_path/'missing.json'),
                                   '--output-dir',str(tmp_path/'out')])
    assert geometry_audit.main()==2
    assert '"real_geometry_executed": false' in capsys.readouterr().out
    assert not (tmp_path/'out').exists()


def test_blocked_benchmark_numeric_values_remain_blank():
    root=Path(__file__).resolve().parents[1]/'runs/geometry_20261016'
    df=pd.read_csv(root/'ablation_summary.csv')
    assert set(df.status)=={'BLOCKED_MISSING_REAL_INPUTS'}
    assert df.measured_speedup.isna().all()
    assert df.A_median_end_to_end_seconds.isna().all()
    assert df.B_median_end_to_end_seconds.isna().all()


@pytest.mark.parametrize('shape_name',['rectangle','concave_u','courtyard_hole','multipart'])
def test_ablation_equivalence_across_topology_fixtures(shape_name):
    from shapely import affinity
    from matched_ablation import evaluate_method,compare_results
    base=synthetic_fixtures()[shape_name]
    geoms={f'C{i+1}':affinity.translate(base,xoff=20*i) for i in range(3)}
    buildings=pd.DataFrame({'building_id':list(geoms),'height_m':[12.,9.,6.],
                           'canonical_area_m2':[base.area]*3,'movable':[True]*3,'protected':[False]*3})
    grid=pd.DataFrame({'sensor_id':['outside','north','east'],'x':[-2.,5.,60.],
                       'y':[5.,12.,5.],'z':[.1]*3})
    solar=pd.DataFrame({'apparent_elevation_deg':[15.,45.,80.,-5.],
                        'dx':[1.,0.,-1.,1.],'dy':[0.,-1.,0.,0.],
                        'tan_altitude':np.tan(np.radians([15.,45.,80.,-5.]))})
    pairs=[('C1','C2'),('C1','C3'),('C2','C3')]
    a=evaluate_method('A',buildings,grid,geoms,solar,pairs,protocol()['analysis'])
    b=evaluate_method('B',buildings,grid,geoms,solar,pairs,protocol()['analysis'])
    assert compare_results(a,b,protocol()['tolerances'])['equal']
    assert np.all(a.candidate_hours>=a.baseline_hours)
    assert a.candidate_hours.max()<=1.5


@pytest.mark.parametrize('size',[5,20,60,630])
def test_fixed_full630_normalization_reproduces_frozen_scores_on_nested_prefixes(size):
    from matched_ablation import load_normalization_reference,_rank_metrics,NORMALIZATION_COLUMNS
    bounds,provenance=load_normalization_reference(protocol())
    root=Path(__file__).resolve().parents[2]
    source=pd.read_csv(root/provenance['normalization_source']).set_index('building_ids')
    pair_keys=[','.join(p) for p in protocol()['benchmark']['candidate_order'][:size]]
    subset=source.loc[pair_keys]
    metric=pd.DataFrame({'pair':pair_keys,**{key:subset[column].to_numpy() for key,column in NORMALIZATION_COLUMNS.items()}})
    ranked=_rank_metrics(metric,protocol()['scoring_weights'],bounds)
    assert np.allclose(ranked.score.to_numpy(),subset.score.to_numpy(),atol=1e-10,rtol=0)
    assert bounds['N']==(0.,0.)
    assert provenance['normalization_basis']=='FROZEN_FULL630_REFERENCE'


def test_geometry_cli_rejects_invalid_code_commit(monkeypatch):
    import geometry_audit
    monkeypatch.setattr(sys,'argv',['geometry_audit.py','--synthetic','--code-commit','invalid'])
    with pytest.raises(SystemExit) as exc: geometry_audit.main()
    assert exc.value.code==2
