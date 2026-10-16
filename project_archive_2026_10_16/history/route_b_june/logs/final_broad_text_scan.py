from pathlib import Path
import zipfile,re
p=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\光权修复论文_EI会议_中文导师审阅定稿版_最终.docx')
with zipfile.ZipFile(p) as zf: xml=zf.read('word/document.xml').decode('utf-8')
text=re.sub(r'<[^>]+>','',xml)
checks=['高精度','唯一最优','最优','最佳','显著','确定性','自动生成','28.125']
Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\logs\final_broad_text_scan.txt').write_text('\n'.join(f'{c}: {text.count(c)}' for c in checks),encoding='utf-8')
