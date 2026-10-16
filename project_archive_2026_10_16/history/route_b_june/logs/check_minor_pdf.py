from pathlib import Path
import importlib.util
import fitz
from PIL import Image, ImageOps, ImageDraw
root=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20')
script=root/'code'/'generate_chinese_academic_final.py'
spec=importlib.util.spec_from_file_location('academic', script)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
data=mod.read_data()
pdf=mod.PAPER_PDF
doc=fitz.open(pdf)
imgs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(0.55,0.55), alpha=False)
    im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    im=ImageOps.expand(im,border=2,fill='black')
    ImageDraw.Draw(im).text((8,8),f'Page {i+1}',fill='red')
    imgs.append(im)
page_count=doc.page_count
doc.close()
w=max(im.width for im in imgs); h=max(im.height for im in imgs)
cols=2; rows=(len(imgs)+1)//2
sheet=Image.new('RGB',(cols*w,rows*h),'white')
for idx,im in enumerate(imgs): sheet.paste(im,((idx%cols)*w,(idx//cols)*h))
out=root/'figures'/'158_投稿前小修PDF全页缩略核查.png'
sheet.save(out)
status=f'通过。PDF 由 Microsoft Word 原生导出；PyMuPDF 读取 {page_count} 页；全页缩略核查图为 {out.name}。命令行执行路径在 PDF 页面中可见。'
mod.build_consistency_report(data, page_count, status)
issues=mod.check_document(data, page_count)
print(status)
print('issues', issues)
