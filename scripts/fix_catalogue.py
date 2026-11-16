from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'工作底稿'
replacements={
'catalogue_ds.py':{
'O\\(':'O[(]',
'WPL|weight|深度|表达式|BST|索引':'WPL|weight|深度|表达式|BST|索引|一元操作符',
'结点数|总结点|叶数':'结点数|总结点|总节点|叶与分支数|叶数',
'矩阵|邻接表|多重表|字段|存储|入度|出度|度数':'矩阵|邻接表|多重表|字段|存储|入度|出度|度数|奇度|K顶点',
},
'catalogue_co.py':{
'组号|字段|映射|标记|行号|块号|位数|地址|Cache行|组索引':'组号|字段|映射|标记|行号|块号|位数|地址|Cache行|组索引|Cache容量',
'LRU|命中|缺失|未命中|替换|访问|块数':'LRU|命中|缺失|未命中|替换|访问|块数|有效位',
'时钟|周期|最长路径|CPI':'时钟|周期|最长路径|CPI|PC加2',
'加|减|OF|CF|ZF|SF|标志|溢出|比较|补码|寄存器':'加|减|OF|CF|ZF|SF|标志|溢出|比较|补码|寄存器|下溢',
'字段|操作码|编码|格式|寄存器|位宽|定长|保留|指令数|指令条数':'字段|操作码|编码|格式|寄存器|位宽|定长|保留|指令数|指令条数|opcode',
},
'catalogue_os.py':{
'页号|页框|地址|字段|索引|页大小|虚实|PDBR|页目录|表项|页表基址':'页号|页框|地址|字段|索引|页大小|虚实|PDBR|页目录|表项|页表基址|代码同页',
'到达|周转|等待|次数|RR|时钟|SJF|FCFS|抢占|队尾|切换|调度时刻':'到达|周转|等待|次数|RR|时钟|SJF|FCFS|抢占|队尾|切换|调度时刻|时间片耗尽',
},
'catalogue_net.py':{
'2026初始cwnd为8MSS而rwnd仅2MSS，数据批次受接收窗口限制；不可机械从1MSS开始画慢启动。':'2026题给8MSS的是初始阈值ssthresh，不能误读为cwnd；按题目传统慢开始初始1MSS模型，并受rwnd=2MSS限制，批次为1／2／1。',
}}
for f,pairs in replacements.items():
 p=D/f;s=p.read_text(encoding='utf-8')
 for a,b in pairs.items():
  assert a in s,(f,a);s=s.replace(a,b)
 p.write_text(s,encoding='utf-8')
old='拥塞窗口初始8MSS，接收窗口2MSS限制每批2段；握手后2/2个MSS发送到末ACK共3RTT（15ms）'
new='8MSS为初始阈值而非cwnd；传统慢开始初始1MSS，rwnd=2MSS，握手后1/2/1个MSS发送到末ACK共4RTT（20ms）'
for p in [D/'annotations'/'2026.tsv',R/'scripts'/'prepare_catalogue.py']:
 s=p.read_text(encoding='utf-8');assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
