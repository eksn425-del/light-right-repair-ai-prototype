"""Export searchable text and provenance for the local oversized planning PDF."""

import hashlib
import json
from pathlib import Path

import fitz

ARCHIVE = Path(__file__).resolve().parents[1]
SOURCE = Path('E:/AI项目/20250212灌口镇灌口一二社区“1314”焕新计划.pdf')
OUTPUT = ARCHIVE / 'context/large_planning_pdf'
OUTPUT.mkdir(parents=True, exist_ok=True)
source_hash = hashlib.sha256()
with SOURCE.open('rb') as handle:
    for chunk in iter(lambda: handle.read(1024*1024), b''):
        source_hash.update(chunk)
pages = []
text_parts = ['# 1314 焕新计划：可检索文字副本\n',
              'Source: ' + SOURCE.name + '\n',
              'The original PDF remains local because it exceeds the GitHub single-file limit.\n',
              'This text extraction preserves searchable text only; maps, figures and scanned text require the original PDF.\n']
with fitz.open(SOURCE) as document:
    for number, page in enumerate(document, 1):
        text = page.get_text('text')
        pages.append({'page': number, 'extracted_characters': len(text), 'requires_visual_reference': len(text.strip()) < 40})
        text_parts.append('\n\n## Source PDF Page ' + str(number) + '\n\n' + text)
text_path = OUTPUT / '1314_PLAN_SEARCHABLE_TEXT.md'
text_path.write_text(''.join(text_parts), encoding='utf-8')
metadata = {'source_file': SOURCE.name, 'source_bytes': SOURCE.stat().st_size, 'source_sha256': source_hash.hexdigest(),
            'raw_pdf_uploaded': False, 'extraction_date': '2026-10-16', 'page_count': len(pages),
            'extracted_characters': sum(page['extracted_characters'] for page in pages),
            'text_output': text_path.relative_to(ARCHIVE).as_posix(),
            'limitation': 'Text extraction does not preserve maps, drawings or scanned-image text. No OCR or scientific re-analysis was performed.',
            'pages': pages}
(OUTPUT / 'LARGE_PDF_EXTRACTION.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({key:value for key,value in metadata.items() if key!='pages'}, ensure_ascii=False, indent=2))
