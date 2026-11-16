from pathlib import Path
import json, collections, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'工作底稿'
names={}
groups={
'DS':'复杂度|顺序表|数组算法设计|链表算法|栈与递归|队列与双端队列|表达式与括号|数组和矩阵存储|保留|树的数量与形态|二叉树遍历重建与线索|森林转换|哈夫曼与前缀编码|二叉搜索树|AVL树|B树|B+树|图的性质与建模|图的存储与矩阵|图的遍历|最小生成树|最短路径|拓扑排序|关键路径|顺序分块与加权查找|折半查找|散列|排序综合辨析|插入排序|希尔排序|冒泡排序|快速排序与选择|简单选择排序|堆|归并排序|基数排序|外部排序|保留|KMP',
'CO':'体系结构与指令集|性能计算|整数表示与转换|整数运算与标志|浮点表示|浮点运算|存储器扩展与编址|存储芯片与刷新|交叉编址|Cache映射与容量|Cache命中置换与时间|Cache写策略|存储层次与局部性|指令格式|寻址方式|指令执行与汇编|数据通路与控制信号|控制器与微程序|流水线性能|流水线相关|异常|中断|DMA|程序查询|总线|I/O接口|磁盘与存储设备|并行结构|海明校验',
'OS':'操作系统概念与启动|特权与系统调用|进程状态与切换|线程|互斥机制|信号量与同步设计|调度|死锁与安全性|内存分配与重定位|分页与地址转换|页面置换|驻留集与工作集|目录与文件操作|文件分配与索引|空闲空间管理|链接|磁盘调度|I/O软件层次|缓冲与假脱机|进程通信|虚拟机监控器',
'NET':'分层与服务|时延吞吐与交换|信道容量与编码|物理介质与接口|差错检测|可靠传输与滑动窗口|介质访问与复用|以太网帧|交换桥接与VLAN|无线局域网|IPv4地址与子网|转发与路由表|IP首部与分片|ARP DHCP ICMP|路由协议|IPv6|NAT|TCP序号确认与连接|TCP流量控制|TCP拥塞控制|UDP与端口|DNS|HTTP|FTP|电子邮件|客户服务器与P2P|HDLC位填充|SDN'}
for prefix, values in groups.items():
    for i,name in enumerate(values.split('|'),1): names[f'{prefix}{i:02}']=name
rows=[]
for year in range(2009,2027):
    for line in (DATA/'annotations'/f'{year}.tsv').read_text(encoding='utf-8-sig').splitlines():
        if not line.strip(): continue
        q,p,t,n=line.split('\t',3)
        rows.append(dict(year=year,q=q,parent=int(q.split('.')[0]),pages=p,tags=t.split(','),note=n))
bytype=collections.defaultdict(list)
for r in rows:
    for t in r['tags']:
        assert t in names,t
        bytype[t].append(r)
manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8-sig'))
def ref(r): return f"{r['year']}年第{r['q']}题（PDF {r['pages']}页）"
def anchor(r): return f"e{r['year']}-{r['q'].replace('.','-')}"
def stats(rs):
    parents={(r['year'],r['parent']) for r in rs}
    return dict(years=len({y for y,q in parents}),questions=len(parents),choice=sum(q<=40 for y,q in parents),comprehensive=sum(q>40 for y,q in parents))
def fmt(s): return f"{s['years']}年／{s['questions']}题（选择{s['choice']}、综合{s['comprehensive']}）"
out=['# 408真题题型全覆盖与答疑规范','',
'> 版本：2026-10-28 工作稿。当前已建立18年逐题归类底稿和可重算索引，但题型变式归并、逐项选项辨析核验与最终验收尚未完成。**尚未达到“已完成全覆盖核验”标准，不得把本稿视为已核验的最终范围边界。**','',
'## 使用范围与证据等级','',
'范围来源为本项目2009—2026年18套试卷。正文按题型组织；逐题记录集中在文末，供追溯。讲义仅解释必要原理，不用于自行扩大历史已考范围。每条索引是人工阅读时记录的考查任务，不是原题完整文字或官方答案。后续引用原题必须打开对应原图。','',
'区分直接考查、选项辨析和必要前置知识：当前底稿尚未为每个标签分别登记这三种角色，因此下列频次暂称“关联覆盖频次”，不能冒充已经剔除前置知识后的纯直接考频。未给出可验证来源的结论不能作为排除某知识点的依据。','',
'## 学习方法','',
'按“必要原理 → 闭卷识别并作答 → 对照思路定位错因 → 间隔重做 → 变式训练 → 跨模块限时训练”推进。先写出题目条件、要求和适用公式，再独立作答；重做时遮住答案。错误记录只来自真实作答，区分识别、原理、条件、计算、表达和时间问题。','',
'能够独立做对且解释条件后逐渐延长复测间隔；做错或靠提示完成则缩短间隔。复习覆盖低频题、难题和一次性考法；高频用于安排熟练度训练，不据此删除低频内容。限时练习记录实际耗时，不把建议用时伪装成历史考生数据。闭卷提取与间隔练习的依据见[学习技术研究综述](https://www.psychologicalscience.org/publications/journals/pspi/learning-techniques.html)。','',
'## 后续答疑协议（立即执行）','',
'**出题规则：** 用户要求出题时，每道题后直接给出答案及对应解析，不等待用户作答后再公布，也不将答案统一延后或折叠隐藏；用户当次明确要求先不给答案时除外。','',
'1. 直接回答所问，标明相关题型编号；尚未核验的条目标明工作稿状态。',
'2. 解释原理与适用条件，深度限于解相关真题和变式所需。',
'3. 给一道明确标注“原创”的例题并完整示范；不能只改真题数字冒充原创。',
'4. 给最贴切的真题，注明年份、题号、PDF页码，保留全部作答条件，必要时展示原图；说明考什么和如何识别。',
'5. 给一道明确标注“原创”的变式，说明条件改变、思路调整、答案与关键推理。','',
'不默认扩展工程实践。引用讲义时注明文件及PDF页码。超出已核验历史范围时明确说明，先讲已有证据支持的部分。原创题不计历史频次。当前用户明确要求的回答形式优先于默认协议。本协议取代此前先出题后讲解的练习顺序。原卷证据推翻手册时先更正并留变更记录，不能机械沿用错误。其他聊天无法访问本文件时需用户提供文件，不能承诺自动继承。','',
'## 统计与难度口径','',
'同一题型在同一年同一道大题多次出现只计一题，小问证据保留。跨题型允许重复关联，故各题型频次不能相加充当试卷总题数。近五年指2022—2026年。频次不是未来概率。综合题未能明确拆分的分值不向每个题型分配；本稿不发布题型分值排名。','',
'难度采用基础、常规、综合、较难四级分析评级：分别对应单概念直接判断、标准流程、多知识联动、较长推理链或特殊边界设计。必须给具体题目和难点理由，不冒充官方难度或正确率。本稿尚未完成逐题型评级，因此不自动按题数推断难度。','',
'## 题型目录与关联证据','']
summary={}
for prefix,title in [('DS','数据结构'),('CO','计算机组成原理'),('OS','操作系统'),('NET','计算机网络')]:
    out += [f'### {title}','']
    for t in sorted(k for k in bytype if k.startswith(prefix)):
        rs=bytype[t]; a=stats(rs); b=stats([r for r in rs if r['year']>=2022]);summary[t]={'name':names[t],'all':a,'recent':b}
        out += [f'<a id="{t.lower()}"></a>',f'#### {t} {names[t]}','',f'- 全时期关联覆盖：{fmt(a)}。近五年：{fmt(b)}。',
        '- 已提取的考查任务与特殊条件：详见下列逐题证据。核心方法、条件分支、合并后的变式、难度理由和掌握标准仍需逐型整理；不能将本段误认为最终题型卡片。',
        '- 证据：'+'；'.join(f'[{ref(r)}](#{anchor(r)})' for r in rs)+'。','']
out += ['## 精简逐题覆盖索引','', '这里保留每个已登记小问与条件，供题型反查；不是逐题解析汇编。页码均为PDF物理页码（含封面）。','']
for year in range(2009,2027):
    m=next(x for x in manifest if x['year']==year)
    path=(ROOT/m['file']).as_posix()
    out += [f'### {year}年', '',f'[原卷](<{path}>)','', '|题号|PDF页码／原图|题型|任务及条件记录|','|---|---|---|---|']
    for r in [x for x in rows if x['year']==year]:
        ps=[int(x) for x in r['pages'].split('-')]; page_links='、'.join(f'[{p}](<{(DATA/"pages"/str(year)/f"{p:02}.png").as_posix()}>)' for p in range(ps[0],ps[-1]+1))
        ts='、'.join(f'[{t}](#{t.lower()})' for t in r['tags'])
        out.append(f'|<a id="{anchor(r)}"></a>{r["q"]}|{page_links}|{ts}|{r["note"].replace("|","／")}|')
    out.append('')
out += ['## 资料来源与核验状态','', '|年份|PDF页数|文件SHA-256|','|---|---:|---|']
for m in manifest:out.append(f'|{m["year"]}|{len(m["pages"])}|`{m["sha256"]}`|')
out += ['', '参考讲义位于项目“参考资料”目录。本稿未按讲义目录补充未考知识，也没有声称已逐页审阅四本讲义。','',
'答疑格式和边界演示见[六组验收演示](<E:/codex_0_pro/408/工作底稿/答疑协议验收.md>)。已覆盖四科、Cache与分页综合、三叉哈夫曼低频考法；这是选定样例演示，尚非随机抽验。','',
'### 尚未完成的验收项目','',
'- 2023—2026年剩余原图复核及18年封面年份核对需形成逐页记录。',
'- 每个选项的实质性辨析与标签角色尚需单独核验；题号齐全不能证明内容齐全。',
'- 每个题型需完成模块细分、真正的变式归并、适用边界、检查方法、易错点、掌握标准与有证据的难度评级。',
'- 六组答疑演示已编写；仍需完成随机抽验与逐项独立核对。',
'- 需重新核对综合题小问数量、跨页条件与分值；完成语义层面的双向一致性检查。','',
'### 维护与重算','',
'人工逐题底稿：`工作底稿/annotations/*.tsv`；提取页图：`工作底稿/pages/`；OCR仅为辅助：`工作底稿/ocr/`。运行 `python scripts/build_handbook.py` 可重建本工作稿并重算 `工作底稿/频次统计.json` 和 `工作底稿/结构校验.json`。脚本的结构通过不代表语义覆盖通过。','',
'### 变更记录','',
'- 2026-10-28：恢复中断工作，生成18年逐题索引、题型关联频次和后续答疑协议；如实保留未完成验收项。']
(ROOT/'408真题题型全覆盖与答疑规范.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
(DATA/'频次统计.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
errors=[]
for year in range(2009,2027):
    qs={r['parent'] for r in rows if r['year']==year}
    if qs!=set(range(1,48)): errors.append({'year':year,'missing':sorted(set(range(1,48))-qs)})
    keys=[r['q'] for r in rows if r['year']==year]
    if len(keys)!=len(set(keys)):errors.append({'year':year,'duplicate':True})
report={'years':18,'parent_questions':len({(r['year'],r['parent']) for r in rows}),'evidence_rows':len(rows),'types':len(bytype),'structural_errors':errors,'semantic_full_coverage_verified':False}
(DATA/'结构校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
