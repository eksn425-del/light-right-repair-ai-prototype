from pathlib import Path
import zipfile,re
p=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\光权修复论文_EI会议_中文学术定稿版_投稿前小修.docx')
with zipfile.ZipFile(p) as zf: xml=zf.read('word/document.xml').decode('utf-8')
text=re.sub(r'<[^>]+>','',xml)
checks=['DOI: 不适用','DOI：不适用','唯一最优','显著改善','高精度模拟','自动生成最佳方案','C9/C15','C9/C13','C9/C24','C13/C24','C6/C33','3051 m²','lbt-recipes run direct-sun-hours','Direct Sun Hours[EB/OL]']
for c in checks:
    print(c, text.count(c))
# citation sequence in body only
body=text.split('参考文献')[0]
print('body refs', re.findall(r'\[[0-9,\-\s]+\]', body))
