from pathlib import Path
import fitz
from PIL import Image, ImageOps, ImageDraw
root=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20')
pdf=root/'光权修复论文_EI会议_中文导师审阅定稿版_最终.pdf'
out=root/'figures'/'156_最终PDF全页缩略核查.png'
doc=fitz.open(pdf)
imgs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(0.55,0.55), alpha=False)
    im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    im=ImageOps.expand(im,border=2,fill='black')
    draw=ImageDraw.Draw(im)
    draw.text((8,8),f'Page {i+1}',fill='red')
    imgs.append(im)
w=max(im.width for im in imgs); h=max(im.height for im in imgs)
cols=2; rows=(len(imgs)+1)//2
sheet=Image.new('RGB',(cols*w,rows*h),'white')
for idx,im in enumerate(imgs): sheet.paste(im,((idx%cols)*w,(idx//cols)*h))
sheet.save(out)
print(len(imgs), out)
