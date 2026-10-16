from pathlib import Path
import zipfile,re
p=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\光权修复论文_EI会议_中文学术定稿版.docx')
with zipfile.ZipFile(p) as zf: xml=zf.read('word/document.xml').decode('utf-8')
text=re.sub(r'<[^>]+>','',xml)
checks=['Route B','工作包','交付','导师审阅','最终版','投稿前','本轮','本次工作','文件名','代码目录','图表说明','本图用于证明','证明什么','132_HB','138_','140_','142_','144_','146_','导师阅读摘要','投稿前自检','正式收敛','高精度','唯一最优','自动生成最优','最佳','显著改善','28.125']
for c in checks:
    n=text.count(c)
    if n: print(c,n)
print('ref_count', len(re.findall(r'\[\d+\]', text)))
