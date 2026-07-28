#!/usr/bin/env python3
"""把 Opus 4.8 盲解 5-epoch 的解題 transcript（走 Claude Code Workflow 子代理）抽成
第 7 個 solver → agent_wp/<clear>/Opus-4.8.md，湊成 27×7×5=945。
來源＝各 Opus workflow 的 agent-*.jsonl（用 prompt 裡的 opus_arena/<clear>/ 認題）。
去重：同題跨多次跑（quota 重跑）取『有 StructuredOutput 結果』的最後 5 次。工具輸出截斷 1600 字。"""
import glob, os, json, re, collections
ROOT = os.path.dirname(os.path.abspath(__file__))
GOLD = {t["clear"]: t["gold_flag"] for t in json.load(open(os.path.join(ROOT,"opus_tasks.json"),encoding="utf-8"))}
OUT = os.path.join(ROOT, "agent_wp")
TOOL_TRUNC = 1600
WF_BASES = glob.glob("/Users/hawks/.claude/projects/-Users-hawks-Documents-AIS3/*/subagents/workflows/wf_*")

def blocks(msg):
    c = msg.get("content")
    return c if isinstance(c, list) else ([{"type":"text","text":c}] if isinstance(c,str) else [])

def parse_agent(path):
    """回傳 (clear, markdown, final_flag) 或 None。"""
    lines = [json.loads(l) for l in open(path,encoding="utf-8",errors="replace") if l.strip()]
    if not lines: return None
    # 認題：第一個 user message 的文字含 opus_arena/<clear>/
    clear=None
    for o in lines:
        if o.get("type")=="user":
            txt=" ".join(b.get("text","") for b in blocks(o.get("message",{})) if b.get("type")=="text")
            m=re.search(r"opus_arena/([A-Za-z0-9_-]+)/", txt)
            if m: clear=m.group(1); break
    if not clear or clear not in GOLD: return None
    md=[]; final_flag=None
    for o in lines:
        if o.get("type")!="assistant": continue
        for b in blocks(o.get("message",{})):
            if b.get("type")=="text" and b.get("text","").strip():
                md.append(b["text"].strip())
            elif b.get("type")=="tool_use":
                nm=b.get("name",""); inp=b.get("input",{}) or {}
                if nm=="StructuredOutput":
                    final_flag=inp.get("flag"); continue
                cmd=inp.get("command") or inp.get("code") or inp.get("file_path") or json.dumps(inp,ensure_ascii=False)[:300]
                md.append(f"```bash\n$ [{nm}] {cmd}\n```")
        # tool 結果在下一個 user message
    # 工具輸出（tool_result 在 user messages）
    outs=[]
    for o in lines:
        if o.get("type")=="user":
            for b in blocks(o.get("message",{})):
                if b.get("type")=="tool_result":
                    c=b.get("content","")
                    if isinstance(c,list): c="".join(x.get("text","") for x in c if isinstance(x,dict))
                    c=str(c)
                    if c.strip(): outs.append(c[:TOOL_TRUNC]+("…截斷" if len(c)>TOOL_TRUNC else ""))
    body="\n\n".join(md)
    if outs: body+="\n\n<details>工具輸出摘錄</details>\n"  # 保持精簡；主要留 authored 推理+指令
    return clear, body, final_flag

# 收集 per clear → list[(mtime, solved, flag, md, path)]
bag=collections.defaultdict(list)
for wf in WF_BASES:
    for ap in glob.glob(os.path.join(wf,"agent-*.jsonl")):
        r=parse_agent(ap)
        if not r: continue
        clear,md,flag=r
        if not md.strip(): continue
        solved = bool(flag and GOLD[clear] and flag.strip()==GOLD[clear].strip())
        bag[clear].append((os.path.getmtime(ap), solved, flag, md))

written=0; sects=0; idx=[]
for clear, runs in bag.items():
    runs.sort(key=lambda x:-x[0])          # 新到舊
    picked=runs[:5]                        # 取最後 5 次有效嘗試
    picked=picked[::-1]                    # 回到時間序
    d=os.path.join(OUT, clear); os.makedirs(d,exist_ok=True)
    nsolv=sum(1 for _,s,_,_ in picked if s)
    parts=[f"# {clear} — Opus-4.8 盲解 5-epoch\n\n此模型 {nsolv}/{len(picked)} epoch 解出 · 與 6 受測模型看同一份題檔（不看解答）\n\n---\n"]
    for i,(_,s,flag,md) in enumerate(picked,1):
        parts.append(f"### 第 {i} 次 (EPOCH {i}) — solved={'✅ C' if s else '❌ I'}　提交:`{(flag or '')[:80]}`\n\n{md}")
    open(os.path.join(d,"Opus-4.8.md"),"w",encoding="utf-8").write("\n\n---\n\n".join(parts))
    written+=1; sects+=len(picked); idx.append((clear,nsolv,len(picked)))

print(f"寫出 {written} 題 Opus-4.8.md（共 {sects} 段）→ agent_wp/<clear>/Opus-4.8.md")
for c,n,t in sorted(idx): print(f"  {c:38} {n}/{t}")
