"""Validate copied archive bytes, prohibited payloads, and frozen ledgers."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'project_archive_2026_10_16'
FORBIDDEN = {'.dwg', '.dxf', '.skp', '.skb', '.obj', '.ill', '.res', '.hbjson', '.oct', '.pts', '.rad', '.wea', '.epw'}


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024*1024), b''):
            result.update(chunk)
    return result.hexdigest()


def read_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def main():
    text_sources = ['PROJECT_OVERVIEW_CN.md','EXPERIMENTS_AND_EVIDENCE.md','MANUSCRIPTS_AND_SUBMISSION.md','ARCHIVE_REPORT.md']
    combined = '# 光权修复项目完整交接 / 2026-10-16\n\n仓库：eksn425-del/light-right-repair-ai-prototype（private）\n分支：project-handoff-2026-10-16\n冻结来源：soict-2026-write-ready-v1\n\n'
    for name in text_sources:
        combined += '\n\n' + '='*60 + '\n' + name + '\n' + '='*60 + '\n\n' + (ARCHIVE/name).read_text(encoding='utf-8')
    (ROOT/'WEB_HANDOFF_FULL.txt').write_text(combined, encoding='utf-8-sig')
    rows = read_rows(ARCHIVE / 'indexes/FILE_INVENTORY.csv')
    copied = [row for row in rows if row['action'] == 'copied']
    errors = []
    unique = {}
    for row in rows:
        if row['action'] == 'excluded':
            continue
        path = ARCHIVE / row['archive_path']
        actual = unique.setdefault(path, digest(path)) if path.exists() else ''
        if actual != row['sha256']:
            errors.append({'path': row['archive_path'], 'error': 'hash_mismatch_or_missing'})
    scanned = list(ARCHIVE.rglob('*')) + list((ROOT / 'paper_assets').rglob('*'))
    files = [path for path in scanned if path.is_file()]
    for path in files:
        if path.suffix.lower() in FORBIDDEN:
            errors.append({'path': path.relative_to(ROOT).as_posix(), 'error': 'prohibited_payload'})
    secret_hits = []
    patterns = {
        'github_token': re.compile(r'(?<![\w])(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})'),
        'openai_key': re.compile(r'(?<![\w])sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{35,}'),
        'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    }
    for path in files:
        if path.suffix.lower() not in {'.md','.txt','.json','.yaml','.yml','.py','.rb','.csv','.html','.ini'}:
            continue
        content = path.read_text(encoding='utf-8-sig', errors='replace')
        for name, pattern in patterns.items():
            if pattern.search(content):
                secret_hits.append({'path': path.relative_to(ROOT).as_posix(), 'kind': name})
    errors.extend(secret_hits)
    freeze = ARCHIVE / 'research/experiments/baseline_20260909_clean'
    sample = freeze / 'independent_validation/VALIDATION_SAMPLE_FROZEN.csv'
    declared = (freeze / 'independent_validation/VALIDATION_SAMPLE_FROZEN.sha256').read_text().strip()
    sample_sha_ok = digest(sample) == declared
    if not sample_sha_ok:
        errors.append({'error': 'frozen_sample_sha_mismatch'})
    frozen_csv = freeze / 'paper_support/PAPER_NUMBERS.csv'
    active_csv = ROOT / 'research_reproducibility/paper_support/PAPER_NUMBERS.csv'
    numbers_identical = digest(frozen_csv) == digest(active_csv)
    if not numbers_identical:
        errors.append({'error': 'paper_numbers_byte_mismatch'})
    frozen_claims = freeze / 'paper_support/CLAIMS_LEDGER.csv'
    claims_identical = digest(frozen_claims) == digest(ROOT / 'research_reproducibility/paper_support/CLAIMS_LEDGER.csv')
    if not claims_identical:
        errors.append({'error': 'claims_ledger_byte_mismatch'})
    summary_rows = []
    for row in copied:
        path = ARCHIVE / row['archive_path']
        if path.suffix.lower() != '.json' or not any(word in path.name.lower() for word in ('summary', 'metrics', 'report')):
            continue
        try:
            value = json.loads(path.read_text(encoding='utf-8-sig'))
        except (ValueError, OSError):
            continue
        def collect(obj, key=''):
            if isinstance(obj, dict):
                for name, item in obj.items():
                    collect(item, key + '.' + name if key else name)
            elif not isinstance(obj, list) and obj is not None:
                summary_rows.append({'source_file': row['source_relative_path'], 'archive_path': row['archive_path'],
                                     'evidence_role': row['status'], 'json_field': key,
                                     'recorded_value': obj, 'source_sha256': row['sha256']})
        collect(value)
    if summary_rows:
        with (ARCHIVE / 'indexes/SUMMARY_METRICS_CATALOG.csv').open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
            writer.writeheader()
            writer.writerows(summary_rows)
    result = {
        'checked_at': '2026-10-16', 'scope': 'archive packaging only; no simulation rerun',
        'status': 'PASS' if not errors else 'FAIL', 'source_inventory_rows': len(rows),
        'copied_unique_files': len(copied), 'hash_checked_source_references': sum(row['action']!='excluded' for row in rows),
        'word_readable_exports': len(list((ARCHIVE / 'readable_manuscripts').rglob('*.md'))),
        'run_or_stage_directories_registered': len(read_rows(ARCHIVE / 'indexes/EXPERIMENT_REGISTER.csv')),
        'summary_scalar_fields_indexed': len(summary_rows),
        'frozen_sample_sha256_valid': sample_sha_ok, 'paper_numbers_identical_to_frozen_run': numbers_identical,
        'claims_ledger_identical_to_frozen_run': claims_identical,
        'prohibited_payload_count': sum(item.get('error')=='prohibited_payload' for item in errors),
        'credential_pattern_findings': len(secret_hits), 'errors': errors,
        'exclusion_counts': dict(Counter(row['reason'] for row in rows if row['action']=='excluded')),
    }
    (ARCHIVE / 'indexes/ARCHIVE_VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    auxiliary = []
    for path in sorted((ARCHIVE / 'context/september_taskbook').glob('*')):
        if path.is_file():
            auxiliary.append({'source_location': 'E:/新建文件夹/' + path.name,
                              'archive_path': path.relative_to(ARCHIVE).as_posix(),
                              'bytes': path.stat().st_size, 'sha256': digest(path)})
    if auxiliary:
        with (ARCHIVE / 'indexes/ADDITIONAL_SOURCE_FILES.csv').open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(auxiliary[0]))
            writer.writeheader()
            writer.writerows(auxiliary)
    manifest_path = ARCHIVE / 'indexes/PACKAGE_CHECKSUMS.csv'
    manifest_files = [path for path in sorted(ARCHIVE.rglob('*')) if path.is_file() and path != manifest_path]
    manifest_files += [path for path in sorted((ROOT/'paper_assets').rglob('*')) if path.is_file()]
    manifest_files += [ROOT/name for name in ('START_HERE.md','HANDOFF_TO_CHATGPT.md','PROJECT_STATE.json','README.md','.gitattributes','WEB_HANDOFF_FULL.txt')]
    with manifest_path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['repository_path','bytes','sha256'])
        writer.writeheader()
        for path in manifest_files:
            writer.writerow({'repository_path': path.relative_to(ROOT).as_posix(),
                             'bytes': path.stat().st_size, 'sha256': digest(path)})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
