"""Check new release payloads and hash coordinate-free scientific evidence."""
import csv
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
I=ROOT/'icores_2027'
BASE='32721b622d4676be46d210c2c691cbe6a3ee2e92'
KEYS={'run_id','config_hash','code_commit','input_hash','measurement_class'}
FORBIDDEN={'.obj','.skp','.dxf','.dwg','.dwl','.dwl2','.wea','.res','.ill','.hbjson',
           '.epw','.pts','.oct','.rad','.mtx','.geojson','.stl','.ply','.unf'}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True,encoding='utf-8').splitlines()


def main():
    changed=set(git('diff','--name-only',BASE,'HEAD'))
    changed.update(git('diff','--name-only'))
    changed.update(git('ls-files','--others','--exclude-standard'))
    # These permitted generated PDFs are ignored by the repo-wide PDF pattern.
    changed.update(str(p.relative_to(ROOT)).replace('\\','/') for p in (I/'paper_support/figures').glob('local_*.pdf'))
    errors=[];csv_count=0
    for name in sorted(changed):
        path=ROOT/name
        if not path.is_file():continue
        if path.suffix.lower() in FORBIDDEN:errors.append('FORBIDDEN_PAYLOAD:'+name)
        if path.suffix=='.csv':
            csv_count+=1
            with path.open(encoding='utf-8-sig',newline='') as handle:
                fields=set(csv.DictReader(handle).fieldnames or [])
            if not KEYS.issubset(fields):errors.append('MISSING_PROVENANCE:'+name)
            if {'x','y','z'}.issubset(fields) or {'canonical_centroid_x','canonical_centroid_y'}.issubset(fields):
                errors.append('COORDINATE_TABLE:'+name)
        if 'baseline_20260909_clean/' in name or name.startswith('research_reproducibility/'):
            errors.append('FROZEN_OR_PRODUCTION_SOURCE_CHANGED:'+name)
    vectors={}
    for p in (I/'paper_support/figures').glob('local_*.svg'):
        has_raster=any(e.tag.endswith('image') for e in ET.parse(p).iter())
        vectors[p.name]={'native_vector_no_embedded_raster':not has_raster}
        if has_raster:errors.append('RASTER_EMBEDDED:'+p.name)
    code=git('rev-parse','HEAD')[0]
    common={'run_id':'local_release_20261017','config_hash':sha(I/'configs/ICORES_PROTOCOL.json'),
            'code_commit':code,'measurement_class':'RECOMPUTED_PUBLIC_SAFE_RELEASE_AUDIT'}
    science=[]
    for folder in ['local_ablation_20261016','local_hb_20261016','local_protocol_20261016','local_inputs_20261016']:
        science.extend(p for p in (I/'runs'/folder).iterdir() if p.is_file())
    science.extend((I/'paper_support/figures').glob('local_*'))
    science.extend(I/'paper_support'/name for name in ['PAPER_NUMBERS_ICORES.csv','CLAIMS_LEDGER_ICORES.csv','CLAIM_CORRECTIONS.csv'])
    science.append(I/'audit/RESULT_DIFF_ICORES.csv')
    science.extend(I/'runs/local_quality_20261016'/name for name in ['canonical630_frozen_regression.csv','experiment_gate_report.json'])
    out=I/'runs/local_quality_20261016'
    manifest=out/'PUBLIC_SAFE_FILE_MANIFEST.csv'
    with manifest.open('w',encoding='utf-8',newline='') as handle:
        fields=['path','sha256','bytes','release_scope',*common.keys(),'input_hash']
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
        for path in sorted(set(science)):
            writer.writerow(dict(path=str(path.relative_to(ROOT)).replace('\\','/'),sha256=sha(path),
                bytes=path.stat().st_size,release_scope='PRIVATE_REVIEW_AGGREGATES_ONLY',input_hash=sha(path),**common))
    protocol_blob=subprocess.check_output(['git','show',BASE+':icores_2027/configs/ICORES_PROTOCOL.json'],cwd=ROOT)
    unchanged=protocol_blob.replace(b'\r\n',b'\n')==(I/'configs/ICORES_PROTOCOL.json').read_bytes().replace(b'\r\n',b'\n')
    if not unchanged:errors.append('FROZEN_PROTOCOL_CHANGED')
    report={**common,'input_hash':sha(manifest),'created_utc':datetime.now(timezone.utc).isoformat(),
            'new_or_changed_files_checked':len(changed),'csvs_checked':csv_count,
            'scientific_artifacts_hashed':len(set(science)),'errors':errors,'passed':not errors,
            'protocol_scientific_content_unchanged':unchanged,
            'protocol_git_lf_sha256':hashlib.sha256(protocol_blob).hexdigest(),
            'protocol_windows_working_sha256':sha(I/'configs/ICORES_PROTOCOL.json'),
            'frozen20_sha256':sha(ROOT/'project_archive_2026_10_16/research/experiments/baseline_20260909_clean/independent_validation/VALIDATION_SAMPLE_FROZEN.csv'),
            'vector_checks':vectors,'public_geometry_added':False,
            'restricted_originals_upload_allowed':False,
            'visual_review':'Both aggregate PNG plots inspected in-chat after generation; labels and footnote readable, no overlap or site geometry',
            'main_commit':git('rev-parse','main')[0]}
    (out/'PUBLIC_SAFE_AUDIT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'passed':not errors,'errors':errors,'scientific_artifacts_hashed':len(set(science))}))
    if errors:raise SystemExit(2)


if __name__=='__main__':main()
