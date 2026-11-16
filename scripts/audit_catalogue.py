from pathlib import Path
import importlib.util,re,json,sys,collections
sys.stdout.reconfigure(encoding='utf-8');R=Path(__file__).resolve().parents[1];D=R/'工作底稿'
cards={}
for p in sorted(D.glob('catalogue_*.py')):
 spec=importlib.util.spec_from_file_location(p.stem,p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 for c in mod.CARDS:
  assert c['id'] not in cards,c['id'];cards[c['id']]=c
rows=[];unmatched=[];used=collections.Counter()
for p in sorted((D/'annotations').glob('*.tsv')):
 for line in p.read_text(encoding='utf-8-sig').splitlines():
  q,pg,t,n=line.split('\t',3)
  for tag in t.split(','):
   if tag not in cards: unmatched.append(f'MISSING CARD {tag}');continue
   matches=[i for i,v in enumerate(cards[tag]['variants'],1) if re.search(v[1],n)]
   if not matches:unmatched.append(f'{tag} {p.stem}:{q} {n}')
   for i in matches:used[(tag,i)]+=1
empty=[f'{t}-V{i:02} {v[0]}' for t,c in cards.items() for i,v in enumerate(c['variants'],1) if not used[(t,i)]]
print('cards',len(cards),'unmatched',len(unmatched),'empty',len(empty))
print('\n'.join(unmatched));print('\n'.join(empty))
(D/'归并待核对.txt').write_text('\n'.join(unmatched+empty),encoding='utf-8')
