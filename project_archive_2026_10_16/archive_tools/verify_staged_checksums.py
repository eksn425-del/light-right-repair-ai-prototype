"""Verify Git's staged blobs against the package checksum manifest."""

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
manifest = ROOT / 'project_archive_2026_10_16/indexes/PACKAGE_CHECKSUMS.csv'
with manifest.open(encoding='utf-8-sig', newline='') as handle:
    rows = list(csv.DictReader(handle))
process = subprocess.Popen(['git','cat-file','--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
errors = []
for row in rows:
    process.stdin.write((':' + row['repository_path'] + '\n').encode('utf-8'))
    process.stdin.flush()
    header = process.stdout.readline().decode('utf-8').strip().split()
    if len(header) != 3 or header[1] != 'blob':
        errors.append({'path': row['repository_path'], 'reason': 'missing_staged_blob'})
        continue
    data = process.stdout.read(int(header[2]))
    process.stdout.read(1)
    if len(data) != int(row['bytes']) or hashlib.sha256(data).hexdigest() != row['sha256']:
        errors.append({'path': row['repository_path'], 'reason': 'staged_byte_mismatch'})
process.stdin.close()
process.wait()
print(json.dumps({'status':'PASS' if not errors else 'FAIL', 'staged_assets_checked':len(rows),'errors':errors}, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
