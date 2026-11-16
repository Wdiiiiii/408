"""从人工逐题底稿、题型卡片、选项裁定重建手册；结构检查不替代原图阅读。"""
from pathlib import Path
import collections, json, re, runpy, sys, hashlib
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[1]; D=R/'工作底稿'
# 名称表保持旧稿编号稳定，空号不重新分配。
old=(R/'scripts/build_handbook.py').read_text(encoding='utf-8')
ns={};exec(old[old.index('names={}'):old.index('rows=[]')],ns);names=ns['names']
cards={}
for f in sorted(D.glob('catalogue_*.py')):
 for c in runpy.run_path(str(f))['CARDS']:
  assert c['id'] not in cards
  cards[c['id']]=c
oa=runpy.run_path(str(D/'option_audit.py'))
manifest=json.loads((D/'manifest.json').read_text(encoding='utf-8-sig'))
rows=[];errors=[]
for y in range(2009,2027):
 for line in (D/'annotations'/f'{y}.tsv').read_text(encoding='utf-8-sig').splitlines():
  q,pg,t,n=line.split('\t',3);key=f'{y}:{q}';tags=t.split(',');roles={x:'D' for x in tags}
  if key in oa['ADDITIONS']:
   more,explain=oa['ADDITIONS'][key];n+='；选项补充：'+explain
   for x in more.split(','):
    if x not in tags: tags.append(x);roles[x]='O'
  for role,field in [('O','OPTIONS'),('P','PREREQUISITES')]:
   for x in oa[field].get(key,'').split(','):
    if x in tags:roles[x]=role
  parent=int(q.split('.')[0]);r=dict(key=key,year=y,q=q,parent=parent,pages=pg,tags=tags,roles=roles,note=n,variants={})
  for t in tags:
   if roles[t]=='O' and t=='DS32':
    r['variants'][t]=['DS32-V03']
   elif roles[t]=='O' and t in oa['OPTION_RULES']:
    r['variants'][t]=[t+'-VO']
   else:
    r['variants'][t]=[f'{t}-V{i:02}' for i,v in enumerate(cards[t]['variants'],1) if re.search(v[1],n)]
   if not r['variants'][t]:errors.append(f'未归并变式 {key} {t} {n}')
  rows.append(r)
bytype={t:[r for r in rows if t in r['tags']] for t in cards}
variants={}
for t,c in cards.items():
 for i,(title,pattern,rule) in enumerate(c['variants'],1):variants[f'{t}-V{i:02}']={'type':t,'title':title,'rule':rule}
 if any(t+'-VO' in r['variants'][t] for r in bytype[t]):
  variants[t+'-VO']={'type':t,'title':'选项中的性能／概念边界','rule':oa['OPTION_RULES'][t]}
for v,data in variants.items():
 data['evidence']=[r['key'] for r in bytype[data['type']] if v in r['variants'][data['type']]]
 if not data['evidence']:errors.append('无证据变式 '+v)
scores={2009:[10,15,8,13,7,8,9],2010:[10,13,11,12,7,8,9],2011:[8,15,11,12,8,7,9],2012:[10,13,11,12,7,8,9],2013:[13,10,9,14,7,8,9],2014:[13,10,9,12,11,7,8],2015:[15,8,13,10,9,6,9],2016:[9,8,15,9,14,6,9],2017:[15,8,13,10,7,8,9],2018:[13,12,8,15,8,7,7],2019:[13,10,8,7,16,7,9],2020:[13,10,13,10,7,8,9],2021:[15,8,15,8,7,8,9],2022:[13,10,15,8,7,8,9],2023:[13,10,14,9,7,8,9],2024:[13,10,13,10,7,8,9],2025:[13,10,12,11,7,8,9],2026:[13,10,10,13,7,8,9]}
def a(r):return f"e{r['year']}-{r['q'].replace('.','-')}"
def label(r):return f"{r['year']}/{r['q']}（PDF {r['pages']}）"
def link(r):return f'[{label(r)}](#{a(r)})'
def stats(rs):
 p={(r['year'],r['parent']) for r in rs}
 return dict(years=len({y for y,q in p}),questions=len(p),choice=sum(q<=40 for y,q in p),comprehensive=sum(q>40 for y,q in p))
def fmt(x):return f"{x['years']}年／{x['questions']}题（选{x['choice']}、综{x['comprehensive']}）"
summary={}
for t,rs in bytype.items():
 summary[t]={'name':names[t]}
 for k,allowed in [('direct',{'D'}),('coverage',{'D','O'}),('prerequisite',{'P'})]:
  subset=[r for r in rs if r['roles'][t] in allowed]
  summary[t][k]={'all':stats(subset),'recent':stats([r for r in subset if r['year']>=2022])}
bykey={r['key']:r for r in rows}
for y in range(2009,2027):
 rs=[r for r in rows if r['year']==y]
 if {r['parent'] for r in rs}!=set(range(1,48)):errors.append(f'{y}题号不全')
 if len({r['q'] for r in rs})!=len(rs):errors.append(f'{y}重复题号')
 if sum(scores[y])!=70:errors.append(f'{y}分值不符')
 for q in range(41,48):
  qs=[r['q'] for r in rs if r['parent']==q]
  sub=sorted(int(x.split('.')[1]) for x in qs if '.' in x)
  if sub and (sub!=list(range(1,max(sub)+1)) or str(q) in qs):errors.append(f'{y}/{q}小问结构错误')
 for r in rs:
  bounds=[int(n) for n in r['pages'].split('-')]
  for p in range(bounds[0],bounds[-1]+1):
   if not (D/'pages'/str(y)/f'{p:02}.png').exists():errors.append(f'{r["key"]}页图不存在')
  if not any(v in ('D','O') for v in r['roles'].values()):errors.append(f'{r["key"]}只有前置')
for c in cards.values():
 for f in ['module','pre','scope','method','pitfall','mastery','difficulty','variants']:
  if not c[f]:errors.append(f'{c["id"]}缺字段{f}')
for m in manifest:
 if hashlib.sha256((R/m['file']).read_bytes()).hexdigest()!=m['sha256']:errors.append(f'{m["year"]}原卷指纹改变')
# 原图语义核验由人工形成单独记录；这里不通过脚本自行宣称已读图。
audit_path=D/'人工核验结论.json'
audit=json.loads(audit_path.read_text(encoding='utf-8')) if audit_path.exists() else {}
complete=not errors and audit.get('all_pages_reviewed') and audit.get('semantic_mapping_reviewed') and audit.get('unresolved')==[]
status='已完成全覆盖核验' if complete else '验收中：尚未完成全覆盖核验'
out=['# 408真题题型全覆盖与答疑规范','',f'> 版本：2026-10-28 v1.0。状态：**{status}**。范围限定本地2009—2026年18份原卷。覆盖核验指逐题、综合题小问、实质选项与题型边界已作人工检查，不是官方答案认证，也不保证未来不会发现需要更正的错误。','',
'## 使用方法与范围','',
'先查题型目录，再看对应变式和文末证据。D=直接任务或直接命题判断；O=为排除候选而辨析的跨题型知识；P=仅为完成任务所需的前置。一个题型内部的错误说法、数值、代码或图形候选，归入同一题型的条件与易错点，不为每个选项另造题型。题干中仅出现概念名称不构成历史考频。','',
'范围由原卷确定，不沿讲义目录扩张。没有历史证据的内容不能被说成已考；没有收录也不等于断言未来不考。正文是方法手册，不是原题逐题详解。引用某道原题时必须打开附录所链接的完整页图，保留全部条件及跨页内容。PDF页码含封面，印刷页码一般比PDF页码少1。','',
'## 学习方法：高分与全面覆盖','',
'采用“掌握必要原理 → 闭卷识别题型并作答 → 对照思路找错因 → 间隔重做 → 变式训练 → 跨模块限时训练”。闭卷提取和间隔练习是主线，阅读本手册不能代替做题。[学习方法研究综述](https://www.psychologicalscience.org/publications/journals/pspi/learning-techniques.html)。','',
'每次先写已知、所求、触发条件，再独立解答；对照后把错误归到识别、原理、条件、计算、表达或时间，并记录真实耗时。能独立做对且解释条件后延长复测间隔；靠提示、超时或做错则缩短。无需固定对所有人都相同的天数。复测遮住答案，更换条件后仍能说明方法为何适用才算掌握。','',
'全覆盖训练表应逐个包含基础、综合难题、低频题及关键变式。高频用于增加熟练度练习，低频用于检查边界，不能按考频删范围；先完成一遍覆盖，再以真实错题和耗时安排补练。算法题需写思想、实现和复杂度，计算题需写单位、边界和检查，概念题需解释错误候选错在哪里。','',
'## 后续答疑协议','',
'**出题规则：** 用户要求出题时，每道题后直接给出答案及对应解析，不等待用户作答后再公布，也不将答案统一延后或折叠隐藏；用户当次明确要求先不给答案时除外。','',
'1. 直接回答问题，标明本手册题型／变式编号。',
'2. 解释原理与适用条件，深度以完成相关真题和已考变式所需为限。',
'3. 给一道标明“原创”的例题并完整示范解答，不把仅改原题数字包装成原创。',
'4. 给最贴切的一道真题，注明年份、题号、PDF页码，保留全部作答条件，必要时展示原图；说明它考什么、如何识别。',
'5. 给一道标明“原创”的变式，说明改变什么条件、如何调整思路，并给答案和关键推理。','',
'本协议取代此前“先出题、后讲解”的顺序；用户当次明确指定格式时按当次要求。默认不扩展工程实践。引用参考讲义须记录文件名和PDF页码。超出本手册历史范围时说明边界，先回答已有证据支持的部分。原创例题不计历史频次，不虚构用户薄弱点。其他聊天无法访问这些文件时须提供文件，不能承诺自动继承。','',
'## 统计、分值与难度','',
'正文同时列直接考频D和含选项覆盖D∪O；P不进入两者。每一题型以（年份，大题号）去重，同一道综合题多个小问只计一题，年份数按实际出现年份去重。近五年为2022—2026。跨题型频次重叠，不能相加成试卷总题数；历史频次不是未来出题概率。','',
'选择每题2分；综合题只登记原卷整题共享分值，不自行拆给各小问或每个标签。每卷150分，18卷共2700分。题型难度为基础、常规、综合、较难四级分析评价；正文说明典型等级及较复杂情形的条件，不冒充官方难度或正确率。“较复杂证据”用于指明训练边界，不宣称已对全部历史题做客观难度排名。','',
'## 模块与题型目录','']
for pre,title in [('DS','数据结构'),('CO','计算机组成原理'),('OS','操作系统'),('NET','计算机网络')]:
 out+= [f'### {title}','']
 modules=list(dict.fromkeys(c['module'] for t,c in cards.items() if t.startswith(pre)))
 for module in modules:
  out += ['- '+module+'：'+'；'.join(f'[{t} {names[t]}](#{t.lower()})' for t,c in sorted(cards.items()) if t.startswith(pre) and c['module']==module)]
 out+=['']
for pre,title in [('DS','数据结构'),('CO','计算机组成原理'),('OS','操作系统'),('NET','计算机网络')]:
 out += [f'## {title}','']
 modules=list(dict.fromkeys(c['module'] for t,c in cards.items() if t.startswith(pre)))
 for module in modules:
  out += [f'### {module}','']
  for t,c in sorted(cards.items()):
   if not t.startswith(pre) or c['module']!=module:continue
   rs=bytype[t];s=summary[t];live=[r for r in rs if r['roles'][t]!='P']
   # 选择综合题/条件较丰富的记录作为复杂情形示例；并不按字数赋难度分。
   hard=max(live,key=lambda r:(r['parent']>40,len(r['note'])))
   levels=re.findall('基础|常规|综合|较难',c['difficulty']);typical=levels[0]
   out += [f'<a id="{t.lower()}"></a>',f'#### {t} {names[t]}','',
    f'**定位与前置：** {title}／{module}。{c["pre"]}。',
    f'**识别与实际范围：** {c["scope"]}',
    f'**核心解题路线与条件：** {c["method"]}',
    f'**易错点：** {c["pitfall"]}',
    f'**掌握标准与高分训练：** {c["mastery"]}',
    f'**难度：** 典型为{typical}。{c["difficulty"]} 较复杂已考情形示例：{link(hard)}——{hard["note"]}。','',
    '|口径|2009—2026|2022—2026|','|---|---|---|',
    f'|直接考频 D|{fmt(s["direct"]["all"])}|{fmt(s["direct"]["recent"])}|',
    f'|含选项覆盖 D∪O|{fmt(s["coverage"]["all"])}|{fmt(s["coverage"]["recent"])}|','',
    '**已考变式及边界**','']
   for v,data in variants.items():
    if data['type']!=t:continue
    ev=[bykey[k] for k in data['evidence']]
    roleonly='（仅前置支撑，不计考频）' if all(r['roles'][t]=='P' for r in ev) else ''
    out += [f'<a id="{v.lower()}"></a>',f'- **{v} {data["title"]}{roleonly}**：{data["rule"]}',
      '  证据：'+'；'.join(link(r)+f'[{r["roles"][t]}]' for r in ev)+'。','']
out += ['## 精简逐题覆盖索引','',
'这里每行对应一个选择题或原卷编号小问；未细分编号的综合题保留为整题并在任务中列出要求。点题型变式回正文，点页码打开原图。D、O、P含义见开头；一行多个标签不重复分配整题分值。','']
for y in range(2009,2027):
 m=next(m for m in manifest if m['year']==y)
 out += [f'### {y}年','',f'[原卷PDF](<{(R/m["file"]).as_posix()}>)。综合题41—47共享整题分值依次为：'+ '、'.join(map(str,scores[y]))+'分；选择题各2分。','',
 '|题／小问|PDF页／原图|题型变式及角色|任务、条件与实质辨析|','|---|---|---|---|']
 for r in [r for r in rows if r['year']==y]:
  ps=list(map(int,r['pages'].split('-')))
  pgs='、'.join(f'[{p}](<{(D/"pages"/str(y)/f"{p:02}.png").as_posix()}>)' for p in range(ps[0],ps[-1]+1))
  tags='；'.join('、'.join(f'[{v}](#{v.lower()})' for v in r['variants'][t])+f' [{r["roles"][t]}]' for t in r['tags'])
  out += [f'|<a id="{a(r)}"></a>{r["q"]}|{pgs}|{tags}|{r["note"].replace("|","／")}|']
 out += ['']
out += ['## 资料来源、验收与维护','',
 '|年份|含封面PDF页数|综合题分值核对|SHA-256|','|---|---:|---|---|']
for m in manifest:out += [f'|{m["year"]}|{len(m["pages"])}|70分，整卷150分|`{m["sha256"]}`|']
out += ['', '全部本地原卷均为图像PDF。OCR只辅助定位，公式、代码、图形、上下标和跨页题以原图为准。四科讲义未作逐页全面审读，也未用其目录扩大已考范围。可供后续解释原理时查阅：','']
for p in sorted((R/'参考资料').glob('*.pdf')):out += [f'- [{p.name}](<{p.as_posix()}>)']
out += ['',f'核验结果：{len(manifest)}年、{sum(len(m["pages"]) for m in manifest)}个PDF物理页面（含18封面）、846道大题（720选择、126综合）、{len(rows)}条题／小问记录、{len(cards)}个题型、{len(variants)}个变式条目（包含明确标注的前置支撑）。','',
 '[逐页核验与分值记录](<E:/codex_0_pro/408/工作底稿/逐页核验.md>)；[随机四科答疑抽验](<E:/codex_0_pro/408/工作底稿/随机抽验.md>)；[综合难题与低频边界演示](<E:/codex_0_pro/408/工作底稿/答疑协议验收.md>)；[疑点与更正记录](<E:/codex_0_pro/408/工作底稿/疑点与更正记录.md>)。','',
 '人工事实底稿为 `工作底稿/annotations/*.tsv`，题型方法为 `catalogue_*.py`，选项与角色裁定为 `option_audit.py`。最终证据账本 `工作底稿/evidence.json` 保存每条记录的角色与变式；`variants.json`保存反向证据；`频次统计.json`可从账本独立重算。','',
 '修改时先对照原图，更正事实底稿／卡片／角色裁定，登记原因，再运行 `python scripts/build_final_handbook.py` 和 `python scripts/validate_handbook.py`。结构通过只证明链接与统计一致，不能代替新增内容的人工语义复核。发现错误不得机械沿用旧结论。','',
 '### 版本记录','',
 '- 2026-10-28 v1.0：由中断工作稿补全四科方法、变式、选项角色、证据双向索引与重算统计；完成全卷图像复核及四科随机答疑演示。2026年第47题的8MSS明确为初始阈值，撤回把它误读成初始拥塞窗口的中间判断。']
(R/'408真题题型全覆盖与答疑规范.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
for filename,obj in [('evidence.json',rows),('variants.json',variants),('频次统计.json',summary)]:
 (D/filename).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=dict(years=18,pages=sum(len(m['pages']) for m in manifest),parent_questions=846,evidence_rows=len(rows),types=len(cards),variants=len(variants),structural_errors=errors,semantic_full_coverage_verified=bool(complete))
(D/'结构校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
if errors:sys.exit(1)
