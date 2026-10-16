"""G2 geometry invariants and an explicitly unvalidated contained translation.

Production functions are executed from their unchanged AST, with filesystem/runtime
side effects excluded. Synthetic results are regression evidence, never site data.
Run --synthetic for auditable fixtures. Real input is accepted only through a
hash-verified private manifest; absent HB ray matrices remain UNRESOLVED.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable

import numpy as np
import pandas as pd
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely.validation import explain_validity

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = ROOT / 'icores_2027/configs/ICORES_PROTOCOL.json'
LEGACY_HB = ROOT / 'research_reproducibility/src/legacy_route_b/route_b_prepare_hb_batch.py'
LEGACY_2P5D = ROOT / 'research_reproducibility/src/legacy_route_b/route_b_enumerate_2p5d_candidates.py'
RUN_ID = 'geometry_20261016'
CODE_COMMIT = 'ae7483ca493768e23a19cf402446c54d6f6c95ef'
PROVENANCE_FIELDS = ['run_id', 'config_hash', 'code_commit', 'input_hash', 'measurement_class']


class GeometryAuditError(ValueError):
    """The scene is invalid; never silently drop a face or repair its footprint."""


@dataclass(frozen=True)
class Prism:
    footprint: object
    z0: float
    z1: float
    identifier: str


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def protocol():
    return json.loads(PROTOCOL_PATH.read_text())


def reduced_height(h, analysis=None):
    a = analysis or protocol()['analysis']
    return max(a['height_floor_m'], h - min(a['height_cap_m'], a['height_fraction'] * h))


def load_legacy_functions(names, source=LEGACY_HB, extra=None):
    """Execute exact selected production function ASTs, never module entrypoints."""
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.pointvector import Point3D
    from honeybee.shade import Shade
    a = protocol()['analysis']
    runtime = SimpleNamespace(height_floor_m=a['height_floor_m'], reduced_height=reduced_height,
                              timestep_minutes=a['step_minutes'])
    ns = dict(math=math, np=np, pd=pd, affinity=affinity, Point=Point,
              LineString=LineString, Face3D=Face3D, Point3D=Point3D, Shade=Shade,
              RUNTIME=runtime, LOW_THRESHOLD_H=a['threshold_h'], CELL_AREA_M2=a['grid_m']**2,
              SENSOR_HEIGHT_M=a['sensor_height_m'])
    ns.update(extra or {})
    tree = ast.parse(Path(source).read_text(encoding='utf-8'))
    selected = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in names]
    if {n.name for n in selected} != set(names):
        raise GeometryAuditError('Requested production function was not found')
    module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), *selected], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(source), 'exec'), ns)
    return ns


def polygon_parts(geom):
    if geom.is_empty:
        return []
    if geom.geom_type == 'Polygon':
        return [geom]
    if geom.geom_type == 'MultiPolygon':
        return list(geom.geoms)
    raise GeometryAuditError(f'Expected polygonal geometry, got {geom.geom_type}')


def validate_polygon(geom, identifier='footprint'):
    if geom.is_empty or not geom.is_valid or geom.area <= 0:
        raise GeometryAuditError(f'{identifier}: invalid/empty footprint: {explain_validity(geom)}')
    for part in polygon_parts(geom):
        for ring in [part.exterior, *part.interiors]:
            if not np.isfinite(np.asarray(ring.coords)).all():
                raise GeometryAuditError(f'{identifier}: nonfinite coordinate')
    return geom


def legacy_layers(geom, height, mode='design_stepback', building_id='fixture'):
    """Capture exact prism arguments emitted by the production building_shades."""
    layers = []
    def capture(prefix, poly, z0, z1):
        if not poly.is_empty and z1 > z0 + 1e-9:
            layers.append(Prism(poly, float(z0), float(z1), prefix))
        return []
    ns = load_legacy_functions(['building_shades', 'reduced_height'], extra={'prism_shades': capture})
    buildings = pd.DataFrame([{'building_id': building_id, 'height_m': height}])
    _, volumes = ns['building_shades'](buildings, {building_id: geom},
                                      {'pair': building_id, 'scenario': mode, 'model_type': mode})
    return layers, volumes[0]


def emitted_prism_layers(layers):
    """Read actual production roof boundaries to audit its hole-losing envelope.

    Production supplies roofs and vertical walls, with the ground closure implicit.
    This reports that prism envelope, not a Radiance or mesh-boolean measurement.
    """
    ns = load_legacy_functions(['face', 'clean_id', 'prism_shades'])
    result = []
    for p in layers:
        faces = ns['prism_shades'](p.identifier, p.footprint, p.z0, p.z1)
        roofs = [f for f in faces if '_roof_' in f.identifier]
        if len(roofs) != 1:
            raise GeometryAuditError(f'{p.identifier}: missing/ambiguous production roof')
        roof = roofs[0].geometry
        outer = [(v.x,v.y) for v in roof.boundary]
        holes = [[(v.x,v.y) for v in ring] for ring in (roof.holes or [])]
        g = Polygon(outer, holes=holes)
        validate_polygon(g, p.identifier)
        result.append(Prism(g,p.z0,p.z1,p.identifier+'_emitted'))
    return result


def contained_stepback_v2(geom, height, building_id='fixture'):
    """Explicitly intersect the legacy upper footprint with its baseline.

    This changes design volume when legacy scaling escapes a concavity or hole;
    it is not a volume-matched optimization. Controlled validation is limited to
    the frozen cases recorded under runs/local_hb_20261016; it is not a general
    guarantee of surveyed-geometry accuracy or professional design feasibility.
    """
    validate_polygon(geom, building_id)
    layers, _ = legacy_layers(geom, height, building_id=building_id)
    clipped = []
    for layer in layers:
        g = layer.footprint.intersection(geom)
        if g.is_empty:
            continue
        validate_polygon(g, layer.identifier)
        for i, part in enumerate(polygon_parts(g)):
            clipped.append(Prism(part, layer.z0, layer.z1, f'{layer.identifier}_contained_v2_{i}'))
    return clipped


def union_volume(layers: Iterable[Prism]):
    """Integrate union cross-sections between all z breakpoints (no double count)."""
    layers = list(layers)
    for layer in layers:
        validate_polygon(layer.footprint, layer.identifier)
        if not np.isfinite([layer.z0, layer.z1]).all() or layer.z1 <= layer.z0:
            raise GeometryAuditError(f'{layer.identifier}: invalid z interval')
    levels = sorted({v for layer in layers for v in [layer.z0, layer.z1]})
    volume = 0.0
    for lo, hi in zip(levels, levels[1:]):
        active = [p.footprint for p in layers if p.z0 < (lo+hi)/2 < p.z1]
        if active:
            volume += unary_union(active).area * (hi-lo)
    return float(volume)


def containment_report(baseline, modified, tolerances=None):
    baseline, modified = list(baseline), list(modified)
    t = tolerances or protocol()['tolerances']
    base_volume, modified_volume = union_volume(baseline), union_volume(modified)
    levels = sorted({v for p in baseline + modified for v in [p.z0, p.z1]})
    outside_volume, max_outside_area, max_relative = 0.0, 0.0, 0.0
    contained = True
    for lo, hi in zip(levels, levels[1:]):
        z = (lo+hi)/2
        b = unary_union([p.footprint for p in baseline if p.z0 < z < p.z1])
        m = unary_union([p.footprint for p in modified if p.z0 < z < p.z1])
        outside = m.difference(b).area
        relative = outside / b.area if b.area else (math.inf if outside else 0.0)
        max_outside_area = max(max_outside_area, outside)
        max_relative = max(max_relative, relative)
        outside_volume += outside * (hi-lo)
        if outside > max(t['outside_area_m2_abs'], b.area*t['outside_area_relative']):
            contained = False
    return dict(baseline_union_volume_m3=base_volume, modified_union_volume_m3=modified_volume,
                actual_removed_volume_m3=base_volume-modified_volume,
                outside_volume_m3=outside_volume, outside_area_max_m2=max_outside_area,
                outside_area_max_relative=max_relative, solid_contained=contained)


def safe_face(identifier, points, holes=None, tolerance=1e-7):
    """Construct an HB Shade with explicit holes; all errors name the face and stop."""
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.pointvector import Point3D
    from honeybee.shade import Shade
    try:
        if len(points) < 3 or not np.isfinite(np.asarray(points, dtype=float)).all():
            raise ValueError('fewer than three vertices or nonfinite coordinates')
        face = Face3D([Point3D(*p) for p in points],
                      holes=[[Point3D(*p) for p in ring] for ring in holes] if holes else None)
        if face.area <= tolerance**2:
            raise ValueError('zero/near-zero face area')
        if not face.check_planar(tolerance, raise_exception=False):
            raise ValueError('nonplanar face')
        if face.is_self_intersecting:
            raise ValueError('self-intersecting face')
        return Shade(identifier, face, is_detached=True)
    except Exception as exc:
        raise GeometryAuditError(f'FACE_BUILD_FAILED {identifier}: {type(exc).__name__}: {exc}') from exc


def safe_prism_shades(prefix, geom, z0, z1):
    validate_polygon(geom, prefix)
    if not np.isfinite([z0,z1]).all() or z1 <= z0:
        raise GeometryAuditError(f'{prefix}: invalid z interval')
    shades = []
    for part_i, poly in enumerate(polygon_parts(geom)):
        poly = orient(poly, sign=1.0)
        rings = [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]
        def horizontal(z, reverse=False):
            return [[(x,y,z) for x,y in (list(reversed(r)) if reverse else r)] for r in rings]
        roof, bottom = horizontal(z1), horizontal(z0, reverse=True)
        shades += [safe_face(f'{prefix}_p{part_i}_roof', roof[0], roof[1:]),
                   safe_face(f'{prefix}_p{part_i}_bottom', bottom[0], bottom[1:])]
        for ring_i, ring in enumerate(rings):
            for i, (x1,y1) in enumerate(ring):
                x2,y2 = ring[(i+1)%len(ring)]
                shades.append(safe_face(f'{prefix}_p{part_i}_ring{ring_i}_wall{i}',
                                        [(x1,y1,z0),(x2,y2,z0),(x2,y2,z1),(x1,y1,z1)]))
    return shades


def match_sensors(reference, candidate, tolerance=1e-7):
    """Return candidate row indices in reference order, checking unique IDs AND XYZ."""
    r, c = reference.copy(), candidate.copy()
    for frame in (r,c):
        if 'sensor_id' not in frame and 'grid_id' in frame:
            frame.rename(columns={'grid_id':'sensor_id'}, inplace=True)
        if not {'sensor_id','x','y','z'}.issubset(frame.columns):
            raise GeometryAuditError('Sensor table needs ID and x,y,z')
        if (frame.sensor_id.isna().any() or frame.sensor_id.astype(str).str.strip().eq('').any()
                or frame.sensor_id.astype(str).duplicated().any() or frame[['x','y','z']].duplicated().any()):
            raise GeometryAuditError('Sensor IDs must be unique and nonmissing')
        if not np.isfinite(frame[['x','y','z']].to_numpy(float)).all():
            raise GeometryAuditError('Sensor coordinates must be finite')
    if set(r.sensor_id) != set(c.sensor_id):
        raise GeometryAuditError('Sensor ID sets differ')
    lookup = {sid:i for i,sid in enumerate(c.sensor_id)}
    order = np.array([lookup[sid] for sid in r.sensor_id], dtype=int)
    if not np.allclose(r[['x','y','z']].to_numpy(float),c.iloc[order][['x','y','z']].to_numpy(float),rtol=0,atol=tolerance):
        raise GeometryAuditError('Same sensor ID has different coordinates')
    return order


def _line_parts(geom):
    if geom.is_empty:
        return []
    if geom.geom_type in ('LineString','Point'):
        return [geom]
    if hasattr(geom,'geoms'):
        return [part for g in geom.geoms for part in _line_parts(g)]
    return []


def ray_hit(layers, sensor, direction, altitude_deg, tolerance=1e-9):
    """Exact layered-prism intervals for synthetic diagnostics, not an HB replay."""
    if altitude_deg <= 0:
        return None
    x,y,z = map(float, sensor)
    dx,dy = map(float, direction)
    norm = math.hypot(dx,dy)
    if not math.isclose(norm,1,abs_tol=1e-9):
        raise GeometryAuditError('Sun horizontal direction must be unit length')
    if not layers:
        return None
    reach = max(math.hypot(xx-x,yy-y) for p in layers for xx,yy in
                [(p.footprint.bounds[0],p.footprint.bounds[1]),(p.footprint.bounds[2],p.footprint.bounds[3])])+1
    ray = LineString([(x,y),(x+dx*reach,y+dy*reach)])
    slope = math.tan(math.radians(altitude_deg))
    hits = []
    for layer in layers:
        for segment in _line_parts(ray.intersection(layer.footprint)):
            coords = [(segment.x,segment.y)] if segment.geom_type=='Point' else list(segment.coords)
            distances = [(xx-x)*dx+(yy-y)*dy for xx,yy in coords]
            lo = max(min(distances),(layer.z0-z)/slope,1e-7)
            hi = min(max(distances),(layer.z1-z)/slope)
            if lo <= hi+tolerance:
                hits.append((lo, layer.identifier, z+slope*lo))
    if not hits:
        return None
    d, face, height = min(hits)
    return {'blocking_prism':face,'distance_m':d,'ray_height_m':height}


def provenance(measurement_class, input_hash):
    return dict(run_id=RUN_ID, config_hash=sha256(PROTOCOL_PATH),code_commit=CODE_COMMIT,
                input_hash=input_hash,measurement_class=measurement_class)


def write_csv(path, rows, fields=None):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if fields is None:
        fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w', newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields); writer.writeheader(); writer.writerows(rows)


def synthetic_fixtures():
    return {
        'rectangle': box(0,0,10,8),
        'concave_u': Polygon([(0,0),(10,0),(10,10),(7,10),(7,3),(3,3),(3,10),(0,10)]),
        'courtyard_hole': Polygon([(0,0),(10,0),(10,10),(0,10)], holes=[[(3,3),(7,3),(7,7),(3,7)]]),
        'multipart': MultiPolygon([box(0,0,4,4),box(7,0,10,6)]),
    }


def run_synthetic():
    fixtures=synthetic_fixtures()
    synthetic_spec={'footprints':{k:{'wkt':g.wkt,'height_m':12} for k,g in fixtures.items()},
                    'short_rectangle':{'wkt':box(0,0,10,10).wkt,'height_m':4.01},
                    'ray_probe':{'sensor_height_m':.1,'grid_range':[-2,12,2],
                                 'added_patch_representative_points':True,'altitudes_deg':[15,30,45,89],
                                 'azimuths_deg':list(range(0,360,45))}}
    input_hash=hashlib.sha256(json.dumps(synthetic_spec,sort_keys=True).encode()).hexdigest()
    meta=provenance('SYNTHETIC_TEST',input_hash)
    rows=[]; ray_rows=[]
    for name, geom in fixtures.items():
        baseline=[Prism(geom,0,12,f'{name}_baseline')]
        old, reported=legacy_layers(geom,12,building_id=name)
        emitted_baseline=emitted_prism_layers(legacy_layers(geom,12,'baseline',name)[0])
        emitted_old=emitted_prism_layers(old)
        for mode,layers in [('rule_flat',legacy_layers(geom,12,'rule_flat',name)[0]),
                            ('legacy_stepback',old),('contained_stepback_v2_UNVALIDATED',contained_stepback_v2(geom,12,name))]:
            report=containment_report(baseline,layers)
            if mode=='contained_stepback_v2_UNVALIDATED':
                emitted_report=report
            else:
                emitted_report=containment_report(emitted_baseline,emitted_prism_layers(layers))
            emitted_report={f'emitted_envelope_{k}':v for k,v in emitted_report.items()}
            faces=[face for p in layers for face in safe_prism_shades(p.identifier,p.footprint,p.z0,p.z1)]
            rows.append(dict(**meta,case_id=name,scenario=mode,status='EXECUTED_SYNTHETIC',
                             finding='GEOMETRY_BUG_CONFIRMED' if not report['solid_contained'] else 'SYNTHETIC_INVARIANT_PASSED',
                             target_removed_volume_m3=reported['removed_volume_m3'],
                             calculation_basis='canonical_polygon_layers_and_production_surface_envelope_separate',
                             safe_wrapper_face_count=len(faces),holes=sum(len(p.interiors) for p in polygon_parts(geom)),
                             **report,**emitted_report,actual_minus_target_removed_m3=report['actual_removed_volume_m3']-reported['removed_volume_m3']))
        # Search rays outside the actual footprint; deterministic, synthetic only.
        fixed=contained_stepback_v2(geom,12,name)
        directions=[(math.sin(math.radians(az)),math.cos(math.radians(az))) for az in range(0,360,45)]
        adverse=0
        sample_xy=[(float(x),float(y)) for x in range(-2,13,2) for y in range(-2,13,2)]
        for p in emitted_old:
            extra=p.footprint.difference(unary_union([b.footprint for b in emitted_baseline]))
            if not extra.is_empty:
                sample_xy.extend((g.representative_point().x,g.representative_point().y) for g in polygon_parts(extra))
        for sensor_i,(xi,yi) in enumerate(sample_xy):
                if geom.covers(Point(xi,yi)):
                    continue
                for ai,alt in enumerate([15,30,45,89]):
                    for di,direction in enumerate(directions):
                        sensor=(xi,yi,.1)
                        basehit=ray_hit(emitted_baseline,sensor,direction,alt)
                        oldhit=ray_hit(emitted_old,sensor,direction,alt)
                        canonical_basehit=ray_hit(baseline,sensor,direction,alt)
                        fixedhit=ray_hit(fixed,sensor,direction,alt)
                        if not canonical_basehit and fixedhit:
                            raise AssertionError('Contained candidate reduced synthetic direct visibility')
                        if not basehit and oldhit:
                            adverse+=1
                            ray_rows.append(dict(**meta,case_id=name,scenario='legacy_stepback',
                                sensor_id=f'S{sensor_i:04d}',sample_id=f'alt{ai}_az{di}',status='EXECUTED_SYNTHETIC',
                                finding='PRODUCTION_ENVELOPE_ADDED_GEOMETRY_SYNTHETIC',baseline_visible=True,
                                modified_visible=False,blocking_prism=oldhit['blocking_prism'],
                                ray_height_m=oldhit['ray_height_m'],explanation='Actual production roof/wall envelope adds obstruction; deterministic prism-ray diagnostic, not HB replay'))
        for row in rows:
            if row['case_id']==name:
                row['sampled_adverse_rays']=adverse if row['scenario']=='legacy_stepback' else (0 if row['scenario']=='contained_stepback_v2_UNVALIDATED' else '')
    short=box(0,0,10,10)
    short_layers,short_reported=legacy_layers(short,4.01)
    short_report=containment_report([Prism(short,0,4.01,'short_baseline')],short_layers)
    rows.append(dict(**meta,case_id='rectangle_height_4_01',scenario='legacy_stepback',
                     status='EXECUTED_SYNTHETIC',finding='GEOMETRY_BUG_CONFIRMED',
                     calculation_basis='canonical_polygon_layers_equal_emitted_no_holes',
                     target_removed_volume_m3=short_reported['removed_volume_m3'],**short_report,
                     actual_minus_target_removed_m3=short_report['actual_removed_volume_m3']-short_reported['removed_volume_m3']))
    for pair in protocol()['audit_pairs']:
        for mode in ['baseline','rule_flat','legacy_stepback','contained_stepback_v2_UNVALIDATED']:
            rows.append(dict(**provenance('BLOCKED_REAL_INPUT',''),case_id=','.join(pair),scenario=mode,
                             status='BLOCKED_MISSING_PRIVATE_INPUTS',finding='UNRESOLVED'))
        ray_rows.append(dict(**provenance('BLOCKED_REAL_INPUT',''),case_id=','.join(pair),scenario='legacy_stepback',
                             status='BLOCKED_MISSING_HISTORICAL_RAY_OUTPUTS',finding='UNRESOLVED',
                             explanation='Cannot attribute historical adverse points without original geometry, mapping and ray outputs'))
    audit=ROOT/'icores_2027/audit'; out=ROOT/f'icores_2027/runs/{RUN_ID}'
    write_csv(audit/'GEOMETRY_MONOTONICITY.csv',rows)
    write_csv(audit/'ADVERSE_RAY_AUDIT.csv',ray_rows)
    write_csv(out/'design_translation_recheck.csv',rows)
    manifest=dict(created_at=datetime.now(timezone.utc).isoformat(),**meta,
                  source_hashes={str(p.relative_to(ROOT)):sha256(p) for p in [LEGACY_HB,LEGACY_2P5D,Path(__file__)]},
                  synthetic_input_spec=synthetic_spec,
                  real_site_status='UNRESOLVED',contained_stepback_v2='UNVALIDATED_CANDIDATE',
                  synthetic_adverse_ray_count=sum(r.get('finding')=='PRODUCTION_ENVELOPE_ADDED_GEOMETRY_SYNTHETIC' for r in ray_rows),
                  code_commit_note='Source commit supplied by CLI (default is initial protocol/base tree); exact executed wrapper hashes supplied separately. Final evidence commit recorded by handoff metadata.')
    (out/'geometry_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':'SYNTHETIC_EXECUTED_REAL_BLOCKED','rows':len(rows),
                      'synthetic_adverse_rays':manifest['synthetic_adverse_ray_count']}))


def main():
    global CODE_COMMIT
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--synthetic',action='store_true')
    group.add_argument('--real-manifest',type=Path)
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--code-commit',default=CODE_COMMIT,help='40-character source commit; exact wrapper source hashes are also recorded')
    parser.add_argument('--run-id',help='Required for a new real audit; never reuse the synthetic run identity')
    args=parser.parse_args()
    if not re.fullmatch(r'[0-9a-fA-F]{40}',args.code_commit):
        parser.error('--code-commit must be a 40-character commit SHA')
    CODE_COMMIT=args.code_commit
    if args.synthetic:
        run_synthetic(); return
    from matched_ablation import load_real_inputs, ReadinessError
    try:
        real=load_real_inputs(args.real_manifest,protocol())
    except ReadinessError as exc:
        print(json.dumps({'status':'BLOCKED','reason':str(exc),'real_geometry_executed':False}))
        return 2
    buildings,geoms,grid,solar,input_hash=real
    output=args.output_dir
    if output is None or not args.run_id:
        parser.error('--output-dir and --run-id are required for a new private real audit')
    # Geometry-only real audit is executable. HB historical per-ray explanation is
    # deliberately not inferred from this model; it remains an independent gate.
    meta=provenance('MEASURED_REAL_GEOMETRY',input_hash)
    meta['run_id']=args.run_id
    by_id=buildings.set_index('building_id'); rows=[]
    baseline_layers=[]
    for bid,g in geoms.items():
        validate_polygon(g,bid)
        baseline_layers.extend(legacy_layers(g,float(by_id.loc[bid,'height_m']),'baseline',bid)[0])
    safe_baseline_face_count=sum(len(safe_prism_shades(p.identifier,p.footprint,p.z0,p.z1)) for p in baseline_layers)
    emitted_baseline=emitted_prism_layers(baseline_layers)
    for pair in protocol()['audit_pairs']:
        scenes={mode:[] for mode in ['rule_flat','legacy_stepback','contained_stepback_v2_UNVALIDATED']}
        target=0.0
        for bid,g in geoms.items():
            h=float(by_id.loc[bid,'height_m'])
            if bid not in pair:
                for mode in scenes:
                    scenes[mode].extend(legacy_layers(g,h,'baseline',bid)[0])
                continue
            old,reported=legacy_layers(g,h,building_id=bid)
            target+=reported['removed_volume_m3']
            choices={'rule_flat':legacy_layers(g,h,'rule_flat',bid)[0],
                     'legacy_stepback':old,
                     'contained_stepback_v2_UNVALIDATED':contained_stepback_v2(g,h,bid)}
            for mode,layers in choices.items():
                scenes[mode].extend(layers)
                report=containment_report([Prism(g,0,h,bid)],layers)
                safe_faces=[f for p in layers for f in safe_prism_shades(p.identifier,p.footprint,p.z0,p.z1)]
                rows.append(dict(**meta,case_id=','.join(pair),building_id=bid,scope='building',scenario=mode,
                    status='REAL_GEOMETRY_ONLY_HB_REPLAY_PENDING',finding='GEOMETRY_BUG_CONFIRMED' if not report['solid_contained'] else 'UNRESOLVED',
                    target_removed_volume_m3=reported['removed_volume_m3'],safe_wrapper_face_count=len(safe_faces),**report))
        for mode,layers in scenes.items():
            report=containment_report(baseline_layers,layers)
            emitted_report=(report if mode=='contained_stepback_v2_UNVALIDATED' else
                            containment_report(emitted_baseline,emitted_prism_layers(layers)))
            rows.append(dict(**meta,case_id=','.join(pair),building_id='',scope='whole_scene_union',scenario=mode,
                status='REAL_GEOMETRY_ONLY_HB_REPLAY_PENDING',finding='GEOMETRY_BUG_CONFIRMED' if not report['solid_contained'] else 'UNRESOLVED',
                target_removed_volume_m3=target,**report,
                **{f'emitted_envelope_{k}':v for k,v in emitted_report.items()}))
    write_csv(output/'geometry_recheck_private.csv',rows)
    (output/'geometry_run_manifest.json').write_text(json.dumps({**meta,
        'created_at':datetime.now(timezone.utc).isoformat(),
        'source_hashes':{'geometry_audit.py':sha256(__file__),'legacy_hb':sha256(LEGACY_HB)},
        'historical_hb_replay':'NOT_EXECUTED','contained_stepback_v2':'UNVALIDATED_CANDIDATE',
        'safe_baseline_face_count':safe_baseline_face_count},indent=2)+'\n')
    print(json.dumps({'status':'GEOMETRY_ONLY_EXECUTED','historical_adverse_rays':'UNRESOLVED','rows':len(rows)}))


if __name__=='__main__':
    raise SystemExit(main())
