from pathlib import Path
import zipfile,re
p=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\光权修复论文_EI会议_中文学术定稿版_投稿前小修.docx')
with zipfile.ZipFile(p) as zf: xml=zf.read('word/document.xml').decode('utf-8')
text=re.sub(r'<[^>]+>','',xml)
checks=['DOI: 不适用','DOI：不适用','唯一最优','显著改善','高精度模拟','自动生成最佳方案','3051 m²','11.5','10.9','13.0','7.4','0.3','lbt-recipes run direct-sun-hours','Direct Sun Hours[EB/OL]']
out=[]
for c in checks:
    out.append(f'{c}: {text.count(c)}')
body=text.split('参考文献')[0]
out.append('body_refs: '+','.join(re.findall(r'\[[0-9,\-\s]+\]', body)))
Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\logs\minor_final_scan.txt').write_text('\n'.join(out),encoding='utf-8')
