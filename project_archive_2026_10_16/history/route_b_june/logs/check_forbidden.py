from pathlib import Path
import zipfile,re
p=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\光权修复论文_EI会议_中文导师审阅定稿版_最终.docx')
with zipfile.ZipFile(p) as zf:
    xml=zf.read('word/document.xml').decode('utf-8')
text=re.sub(r'<[^>]+>','',xml)
for pat in ['唯一最优','最优方案','28.125','最佳方案','显著改善','高精度采光','自动生成最优']:
    print('PAT',pat, text.count(pat))
    for m in re.finditer(pat,text):
        print(text[max(0,m.start()-50):m.end()+50])
