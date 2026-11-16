from pathlib import Path
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
root = Path(__file__).resolve().parents[1]
for year in sys.argv[1:]:
    print('YEAR',year)
    for page in json.loads((root/'工作底稿'/'ocr'/f'{year}.json').read_text(encoding='utf-8')):
        if page['page'] == 1: continue
        text = page['text'].replace(' ', '')
        lines = [s for s in text.splitlines() if not any(x in s for x in ['扫码','回以','回“回'])]
        print('\n--- PDF PAGE',page['page'],'---\n'+'\n'.join(lines))
