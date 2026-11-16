"""独立核验账本、双向引用、频次和本地链接；不认证语义完整性。"""
from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parents[1];D=R/'工作底稿'
rows=json.loads((D/'evidence.json').read_text(encoding='utf-8'))
variants=json.loads((D/'variants.json').read_text(encoding='utf-8'))
freq=json.loads((D/'频次统计.json').read_text(encoding='utf-8'))
md=(R/'408真题题型全覆盖与答疑规范.md').read_text(encoding='utf-8')
errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
keys={r['key']:r for r in rows}
check(len(keys)==len(rows),'重复证据键')
for r in rows:
 for t,vs in r['variants'].items():
  for v in vs:check(v in variants and r['key'] in variants[v]['evidence'],f'正向缺失 {r["key"]} {v}')
for v,data in variants.items():
 for k in data['evidence']:check(k in keys and v in keys[k]['variants'].get(data['type'],[]),f'反向缺失 {v} {k}')
for t,s in freq.items():
 for mode,roles in [('direct','D'),('coverage','DO'),('prerequisite','P')]:
  for period,start in [('all',2009),('recent',2022)]:
   pairs={(r['year'],r['parent']) for r in rows if r['year']>=start and r['roles'].get(t) in list(roles)}
   actual=dict(years=len({y for y,q in pairs}),questions=len(pairs),choice=sum(q<=40 for y,q in pairs),comprehensive=sum(q>40 for y,q in pairs))
   check(actual==s[mode][period],f'统计不符 {t} {mode} {period}')
anchors=re.findall(r'<a id="([^"]+)"',md)
check(len(anchors)==len(set(anchors)),'重复锚点')
for x in re.findall(r'\]\(#([^\)]+)\)',md):check(x in anchors,'锚点不存在 '+x)
for x in set(re.findall(r'\]\(<([^>]+)>\)',md)):check(Path(x).exists(),'文件不存在 '+x)
for y in range(2009,2027):check({r['parent'] for r in rows if r['year']==y}==set(range(1,48)),f'题号缺失 {y}')
result={'date':'2026-10-29','evidence_rows':len(rows),'types':len(freq),'variants':len(variants),'errors':errors,'scope':'只检查结构、双向链接与独立重算，不代替原图语义核验'}
(D/'独立校验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
sys.exit(bool(errors))
