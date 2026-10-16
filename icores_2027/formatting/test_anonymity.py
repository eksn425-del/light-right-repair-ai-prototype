#!/usr/bin/env python3
"""Non-submission QA for the generated skeleton. Uses unittest and pypdf."""
from __future__ import annotations
import datetime as dt, hashlib, io, json, os, pathlib, re, unittest
from pypdf import PdfReader
from pypdf.generic import IndirectObject, StreamObject, DictionaryObject, ArrayObject, TextStringObject, ByteStringObject
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parent
PDF=ROOT/'anonymous/skeleton.pdf'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def strings_in_pdf(reader):
    seen=set(); out=[]
    def walk(value):
        if isinstance(value,IndirectObject):
            key=(value.idnum,value.generation)
            if key in seen:return
            seen.add(key);walk(value.get_object())
        elif isinstance(value,StreamObject):
            # Type 1 encrypted font programs are binary, not document text.
            # Scan their dictionary strings, but do not interpret eexec bytes as paths.
            if '/Length1' not in value and value.get('/Subtype') not in ['/Type1C','/CIDFontType0C','/OpenType']:
                try:out.append(value.get_data().decode('latin1',errors='replace'))
                except Exception:pass
            for k,v in value.items():walk(k);walk(v)
        elif isinstance(value,DictionaryObject):
            for k,v in value.items():walk(k);walk(v)
        elif isinstance(value,ArrayObject):
            for v in value:walk(v)
        elif isinstance(value,(str,bytes)):
            out.append(value.decode('latin1',errors='replace') if isinstance(value,bytes) else value)
    walk(reader.trailer)
    return '\n'.join(out)

class SkeletonQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader=PdfReader(PDF)
        cls.source=(ROOT/'anonymous/skeleton.tex').read_text()
        cls.record=json.loads((ROOT/'evidence/BUILD_RECORD.json').read_text())
        cls.manifest=json.loads((ROOT/'TEMPLATE_MANIFEST.json').read_text())
        cls.text='\n'.join(p.extract_text() for p in cls.reader.pages)
        cls.objects=strings_in_pdf(cls.reader)
        cls.log=(ROOT/'evidence/final-tex.log').read_text()

    def test_01_source_matches_actual_build(self):
        self.assertEqual(sha(ROOT/'anonymous/skeleton.tex'),self.record['source_sha256'])
        self.assertEqual(sha(PDF),self.record['pdf_sha256'])

    def test_02_current_official_class_unchanged(self):
        m=next(x for x in self.manifest['downloads'] if x['cache_name']=='latex.zip')
        self.assertEqual(next(x['sha256'] for x in m['members'] if x['name']=='llncs.cls'),self.record['template_class_sha256'])
        self.assertIn('v2.25',self.log)

    def test_03_executed_build_succeeded(self):
        self.assertGreaterEqual(len(self.record['commands']),10)
        self.assertTrue(all(x['exit_code']==0 for x in self.record['commands']))
        self.assertTrue(any(x['name']=='bibtex' for x in self.record['commands']))
        self.assertTrue(any(x['name']=='render' for x in self.record['commands']))

    def test_04_blank_author_affiliation_fields(self):
        self.assertIn(r'\author{}',self.source); self.assertIn(r'\institute{}',self.source)
        for macro in [r'\thanks{',r'\email{',r'\orcidID{',r'\authorrunning{']:
            self.assertNotIn(macro,self.source)

    def test_05_pdf_metadata_anonymous(self):
        m=self.reader.metadata
        self.assertEqual(m.get('/Author',''),'')
        self.assertEqual(m.get('/Title'),'Anonymous Formatting Skeleton')
        self.assertNotIn('/CreationDate',m);self.assertNotIn('/ModDate',m)
        self.assertIsNone(self.reader.xmp_metadata)

    def test_06_no_private_paths_or_accounts(self):
        data='\n'.join([self.text,self.objects,self.source])
        patterns=[r'/home/',r'/workspace/',r'/Users/',r'\b[A-Za-z]:[\\/]',r'github\.com/',r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',r'First Author',r'Princeton University']
        for pattern in patterns:self.assertIsNone(re.search(pattern,data,re.I),pattern)
        for value in os.environ.get('ICORES_ANON_FORBIDDEN','').split('|'):
            if value:self.assertNotIn(value.lower(),data.lower(),'Private deny-list match')

    def test_07_no_forms_attachments_comments_or_javascript(self):
        root=self.reader.trailer['/Root']
        self.assertNotIn('/AcroForm',root)
        names=root.get('/Names',{})
        self.assertNotIn('/EmbeddedFiles',names);self.assertNotIn('/JavaScript',names)
        for page in self.reader.pages:
            for ref in page.get('/Annots',[]):
                a=ref.get_object(); self.assertEqual(a.get('/Subtype'),'/Link')
                action=a.get('/A',{})
                if '/URI' in action:
                    self.assertRegex(action['/URI'],r'^https://(?:openai\.com/|doi\.org/)')
                self.assertNotEqual(action.get('/S'),'/JavaScript')

    def test_08_no_layout_or_citation_failures(self):
        for bad in ['Overfull','Underfull','undefined references','undefined on input','Fatal error','! LaTeX Error']:
            self.assertNotIn(bad,self.log)
        self.assertNotIn('??',self.text)

    def test_09_embedded_type_one_fonts(self):
        lines=(ROOT/'evidence/pdffonts.log').read_text().splitlines()[2:]
        self.assertTrue(lines)
        for line in lines:
            self.assertIn('Type 1',line);self.assertRegex(line,r'yes\s+yes\s+yes')

    def test_10_two_pages_rendered_and_no_raster_figures(self):
        self.assertEqual(len(self.reader.pages),2)
        for page in self.reader.pages:self.assertEqual(len(page.images),0)
        for i in [1,2]:
            with Image.open(ROOT/f'rendered/page-{i}.png') as image:
                self.assertGreater(image.width,1000);self.assertEqual(image.height,1800)
                for value in image.info.values():
                    if isinstance(value,str):self.assertNotRegex(value,r'/home/|/workspace/|/Users/')

    def test_11_editable_equation_table_figure(self):
        for token in [r'\begin{equation}',r'\begin{tabular}',r'\begin{picture}',r'\Description{']:
            self.assertIn(token,self.source)
        self.assertIn('Three boxes connected',(ROOT/'anonymous/DescriptionTexts.txt').read_text())

    def test_12_no_font_size_or_margin_compression(self):
        for token in [r'\geometry',r'\vspace',r'\textwidth}',r'\textheight}',r'\fontsize',r'\small',r'\tiny']:
            self.assertNotIn(token,self.source)
        self.assertIn(r'\usepackage{newtxtext}',self.source)
        self.assertIn(r'\usepackage[varvw]{newtxmath}',self.source)

    def test_13_proof_not_claimed_submission_ready(self):
        self.assertIn('mustnotbesubmitted',re.sub(r'\s','',self.text))
        self.assertLess(len(re.sub(r'\s','',self.text)),10000)
        self.assertIn('Provisional AI Use Disclosure',self.text)

    def test_14_no_vendor_fonts_or_word_macros_released(self):
        forbidden={'.pfb','.pfa','.ttf','.otf','.zip','.docm','.cls','.bst'}
        self.assertFalse([p.name for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in forbidden])

    def test_15_all_downloads_hash_checked(self):
        self.assertEqual(len(self.record['download_checks']),len(self.manifest['downloads']))
        self.assertTrue(all(x['status']=='PASS' for x in self.record['download_checks']))

if __name__=='__main__':
    stream=io.StringIO();started=dt.datetime.now(dt.timezone.utc).isoformat()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(SkeletonQA)
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    log=stream.getvalue().replace(str(ROOT),'<FORMATTING>'); print(log,end='')
    (ROOT/'evidence/anonymity-tests.log').write_text(log)
    report={'started_utc':started,'finished_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful(),'pdf_sha256':sha(PDF),'nonwhitespace_extracted_characters':len(re.sub(r'\s','',SkeletonQA.text)),'object_scan_scope':'Parsed PDF strings and decoded non-font streams; binary embedded font programs excluded from text-pattern matching.','count_scope':'PDF extracted text including vector labels; not an official final-manuscript count.','private_denylist_entries_checked':len([x for x in os.environ.get('ICORES_ANON_FORBIDDEN','').split('|') if x]),'docx_checks':'NOT_APPLICABLE: no manuscript DOCX produced; downloaded publisher DOCM templates remain private and unexecuted.','accessibility':'DescriptionTexts sidecar exists; PDF is not tagged. Full accessibility QA remains for final manuscript.'}
    (ROOT/'evidence/ANONYMITY_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
