#!/usr/bin/env python3
"""Validate the hand-reviewed bibliography audit and stamp exact provenance.
This validates record integrity, not the truth of scholarly claims. Primary-source
findings were recorded during the source review described by the CSV and report.
"""
import csv,hashlib,json,pathlib,re,urllib.parse
ROOT=pathlib.Path(__file__).resolve().parent
REPO=ROOT.parent.parent
BIB=REPO/'research_reproducibility/paper_assets/BIBLIOGRAPHY.bib'
PROTOCOL=REPO/'icores_2027/configs/ICORES_PROTOCOL.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    path=ROOT/'BIBLIOGRAPHY_VERIFICATION.csv'
    with path.open() as f:
        reader=csv.DictReader(f); rows=list(reader); fields=list(reader.fieldnames)
    keys=re.findall(r'@\w+\{([^,]+),',BIB.read_text())
    assert len(rows)==13 and {r['citation_key'] for r in rows}==set(keys)
    base=json.loads(PROTOCOL.read_text())['base_code_commit']
    assert re.fullmatch('[0-9a-f]{40}',base)
    for k in ['code_commit_scope','code_script_path','code_script_sha256']:
        if k not in fields:fields.append(k)
    for row in rows:
        assert row['config_hash']==sha(PROTOCOL)
        assert row['input_hash']==sha(BIB)
        assert row['measurement_class']=='SOURCE_VERIFICATION'
        assert urllib.parse.urlsplit(row['source_url']).hostname in {'journals.library.columbia.edu','journals.sagepub.com','www.mdpi.com','www.sciencedirect.com','api.crossref.org','journal.hep.com.cn','publications.ibpsa.org','www.cambridge.org','ojs.aaai.org'}
        row.update(code_commit=base,code_commit_scope='BASE_COMMIT_PLUS_EXACT_SCRIPT_HASH',code_script_path='icores_2027/formatting/verify_bibliography_provenance.py',code_script_sha256=sha(pathlib.Path(__file__)))
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    print('PASS: 13 bibliography audit rows; source citation set, protocol/input SHA256, primary-source hostnames and code provenance verified.')
