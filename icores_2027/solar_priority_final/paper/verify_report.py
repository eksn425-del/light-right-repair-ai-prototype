from pathlib import Path
import hashlib,json,re,subprocess,zipfile
from pypdf import PdfReader
p=Path(__file__).resolve().parent
pdf=p/'solar_priority_experiment_report.pdf';r=PdfReader(pdf);text='\n'.join(x.extract_text() or '' for x in r.pages);log=(p/'manuscript.log').read_text()
assert len(r.pages)==15
for error in ['Overfull','undefined','Missing character']:assert error not in log,error
assert not r.metadata.get('/Author','')
for leak in ['eksn425','github.com','/workspace/','52aee8','94ba70']:assert leak not in text,leak
fonts=subprocess.check_output(['pdffonts',str(pdf)],text=True)
assert all(' yes ' in line for line in fonts.splitlines()[2:])
assert pdf.read_bytes()==(p/'qa/rebuild/solar_priority_experiment_report.pdf').read_bytes()
assert (p/'llncs.cls').read_bytes()==(p.parent.parent/'preference_robust/paper/llncs.cls').read_bytes()
assert (p/'splncs04.bst').read_bytes()==(p.parent.parent/'preference_robust/paper/splncs04.bst').read_bytes()
expanded=(p/'manuscript_expanded_for_translation.tex').read_text();assert expanded.count('\\begin{table}')==5 and '\\input{' not in expanded
assert expanded.count('\\section{')==7
report={'document_type':'Supplementary experiment report and revision options; NOT replacement submission manuscript','pages':15,'nonwhite_characters_pypdf':sum(not c.isspace() for c in text),'nonwhite_characters_poppler':sum(not c.isspace() for c in (p/'manuscript.txt').read_text()),'font_count':len(fonts.splitlines())-2,'all_fonts_embedded':True,'overfull_boxes':0,'undefined_refs':0,'missing_glyphs':0,'author_metadata':'empty','anonymous_content_scan_pass':True,'clean_build_byte_identical':True,'unchanged_official_class_style':True,'equations':15,'tables':5,'figures':2,'references':len(re.findall(r'\\bibitem', (p/'manuscript.bbl').read_text())),'visual_review':'All15pages reviewed in3 labeled montages; finalupdatedpage3 reviewedseparately. No clipping, overlaps, missingglyphs or tableoverflow. Actual vectorcharts inspected.','scientific_qa':'../qa/INDEPENDENT_ANALYSIS_REVIEW.md passed independently; all6predeclaredreplacementconditionsfailed, no methodclaimeduniversallysuperior','sha256':{f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in ['manuscript.tex','manuscript_expanded_for_translation.tex','solar_priority_experiment_report.pdf','references.bib']}}
(p/'qa/REPORT_QA.json').write_text(json.dumps(report,indent=2)+'\n')
files=['manuscript.tex','manuscript_expanded_for_translation.tex','manuscript.bbl','references.bib','llncs.cls','splncs04.bst','build_portable.sh','SOURCE_README.md','comparison1.tex','comparison2.tex','gate_table.tex','evidence_table.tex','shortlist_table.tex','generate_tables_figures.py','verify_report.py']
files += [str(f.relative_to(p)) for f in (p/'figures').glob('*.pdf')]
with zipfile.ZipFile(p/'report_latex_source_bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(p/f,f)
assert zipfile.ZipFile(p/'report_latex_source_bundle.zip').testzip() is None
print(json.dumps(report,indent=2))
