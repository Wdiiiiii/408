from pathlib import Path
import json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[1]
for y in sys.argv[1:]:
 print('YEAR',y)
 for p in json.loads((R/'工作底稿'/'ocr'/f'{y}.json').read_text(encoding='utf-8-sig')):
  if p['page']==1:continue
  s=p['text'].replace(' ','')
  cut=re.search(r'[一二]、综合|综合应用题',s)
  if cut:s=s[:cut.start()]
  print('PDF',p['page'],s)
  if cut:break
