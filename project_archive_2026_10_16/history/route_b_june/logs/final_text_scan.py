from pathlib import Path
import zipfile,re,sys
p=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\光权修复论文_EI会议_中文导师审阅定稿版_最终.docx')
with zipfile.ZipFile(p) as zf:
    xml=zf.read('word/document.xml').decode('utf-8')
text=re.sub(r'<[^>]+>','',xml)
checks=['唯一最优','自动生成最优','高精度采光','专业日照审查结论','显著改善','整体优于所有方案','最佳方案','最优方案','确定性结论','28.125','C9/C15','C9/C13','C9/C24','C6/C33']
out=[]
for c in checks:
    out.append(f'{c}: {text.count(c)}')
Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\logs\final_text_scan.txt').write_text('\n'.join(out),encoding='utf-8')
