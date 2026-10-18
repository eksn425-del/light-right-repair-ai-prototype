#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,re,subprocess
import pandas as pd
from pypdf import PdfReader
P=Path(__file__).resolve().parent;A=P.parent/'analysis';q=P/'qa';checks=[]
def check(n,b):
 checks.append({'check':n,'passed':bool(b)})
 if not b:raise AssertionError(n)
d=pd.read_csv(A/'top10_rule_candidates.csv');f=pd.read_csv(A/'pareto_rule_candidates.csv');s=pd.read_csv(A/'selected_23_provenance.csv');e=pd.read_csv(A/'decision_evidence_matrix.csv')
check('630 unique candidate decisions',len(e)==630 and e.building_pair.nunique()==630)
check('Top10 ranks1to10',list(d['rank'])==list(range(1,11)))
check('12 AV-front identities',len(f)==12 and f.Pareto_membership.all())
check('23 curated selected identities',len(s)==23 and s.building_pair.nunique()==23)
check('allTop10ruleHB reviewed',d.HB_review_status.eq('ARCHIVED_RULE_HB_REVIEWED').all())
check('only3Top10translatedreview',sum(~d.design_translation_status.eq('NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION'))==3)
check('shortlisttableidentity',all(x.replace(',','/') in (P/'top10_table.tex').read_text() for x in d.building_pair))
for r in d.itertuples():
 line=next(x for x in (P/'top10_table.tex').read_text().splitlines() if re.match(str(r.rank)+r' & ',x))
 for v in [f'{r.low_sun_area_reduction_m2:.0f}',f'{r.mean_DSH_gain_h:.5f}',f'{r.nominal_volume_proxy_m3:,.0f}',f'{r.weighted_score:.5f}']:check('table_'+str(r.rank)+'_'+v,v in line)
pdf=P/'anonymous_regular_submission.pdf';reader=PdfReader(pdf);text=(q/'manuscript.txt').read_text();chars=len(''.join(text.split()))
check('official_character_range',10000<=chars<=50000)
check('anonymous_PDF_author',not reader.metadata.get('/Author'))
check('no_identifying_repo_paths',not re.search(r'eksn425|light-right-repair|/workspace|icores_2027|af486946|5dc805',text,re.I))
check('AI_disclosure_present','AI-Assistance Disclosure' in text and 'substantial assistance' in text)
log=(P/'manuscript.log').read_text();check('no_unresolved_refs_cites',not re.search(r'undefined|Label\(s\) may have changed',log,re.I));check('no_overfull_boxes','Overfull' not in log)
fontlog=(q/'pdffonts.txt').read_text().splitlines()[2:];check('all_fonts_embedded',all(re.search(r'\s+yes\s+yes\s+',l) for l in fontlog if l.strip()))
check('all_pages_rendered',len(list((q/'rendered').glob('page-*.png')))==len(reader.pages))
report={'status':'PASS','pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'tex_sha256':hashlib.sha256((P/'manuscript.tex').read_bytes()).hexdigest(),'pages':len(reader.pages),'pdf_nonwhitespace_characters_pdftotext_layout':chars,'checks':checks,'visual_review':'Recorded separately in QA_REPORT.md and independent final review','new_physical_simulation':False,'author_approval':False,'submitted':False}
(q/'AUTOMATED_QA.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2));print(len(checks),'checks passed')
