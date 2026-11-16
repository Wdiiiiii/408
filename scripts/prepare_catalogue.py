from pathlib import Path
from PIL import Image,ImageDraw
import collections
R=Path(__file__).resolve().parents[1];D=R/'工作底稿'
fixes={
(2014,'1'):'外层k从1倍增至n、内层j从1递增至n，执行n(floor(log2 n)+1)次，Θ(n log n)',
(2019,'1'):'x从0递增且循环条件n≥(x+1)²，执行floor(sqrt(n))次，Θ(sqrt(n))',
(2025,'1'):'外层i²≤n、内层j≤i，求和至floor(sqrt(n))，总次数Θ(n)，不能直接写n²',
(2026,'47.4'):'8MSS为初始阈值而非cwnd；传统慢开始初始1MSS，rwnd=2MSS，握手后1/2/1个MSS发送到末ACK共4RTT（20ms）',
}
groups=collections.defaultdict(list)
for year in range(2009,2027):
 p=D/'annotations'/f'{year}.tsv';lines=[]
 for l in p.read_text(encoding='utf-8-sig').splitlines():
  q,pg,t,n=l.split('\t',3)
  n=fixes.get((year,q),n)
  if year==2022 and q.startswith('45.') and '硬链' in n and 'OS16' not in t:t+=',OS16'
  lines.append('\t'.join([q,pg,t,n]))
  for tag in t.split(','):groups[tag].append(f'{year}:{q} p{pg} {n}')
 p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
(D/'分题型证据.txt').write_text('\n\n'.join(t+'\n'+'\n'.join(v) for t,v in sorted(groups.items())),encoding='utf-8')
canvas=Image.new('RGB',(1800,1800),'white');draw=ImageDraw.Draw(canvas)
for i,y in enumerate(range(2009,2027)):
 im=Image.open(D/'pages'/str(y)/'01.png');im.thumbnail((295,570))
 x=(i%6)*300;ypos=(i//6)*600
 canvas.paste(im,(x,ypos+25));draw.text((x+10,ypos+5),str(y),fill='black')
canvas.save(D/'review'/'covers.jpg')
