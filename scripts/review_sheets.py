from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
root=Path(__file__).resolve().parents[1]/'工作底稿'
out=root/'review'
out.mkdir(exist_ok=True)
for year in range(2009,2027):
    pages=sorted((root/'pages'/str(year)).glob('*.png'))[1:]
    for k in range(0,len(pages),4):
        canvas=Image.new('RGB',(2300,3320),'#c0c0c0')
        draw=ImageDraw.Draw(canvas)
        for j,p in enumerate(pages[k:k+4]):
            im=Image.open(p)
            im.thumbnail((1140,1625))
            x=(j%2)*1150; y=(j//2)*1660
            canvas.paste(im,(x,y+30))
            draw.text((x+10,y+5),f'{year} PDF PAGE {p.stem}',fill='black')
        canvas.save(out/f'{year}-{k//4+1}.jpg',quality=90)
print('review sheets ready')
