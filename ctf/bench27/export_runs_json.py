#!/usr/bin/env python3
"""把所有跑完的 agent run 轉成單一權威 JSON（每 run＝一個 model×題×epoch 一筆）。
供跨方比對：判「解出」唯一依據＝scorer 的 value C/I；另附 flag 是否出現在提交/整段 transcript，
讓 retrieved(flag-grep) 與 solved(scorer) 的差異一眼可見。
輸出：ctf/bench27/bench27_runs.json（陣列）＋ stdout 印每模型小計。"""
import glob, os, json, collections
from inspect_ai.log import read_eval_log

ROOT = os.path.dirname(os.path.abspath(__file__))
INSPECT_ROOT = os.path.abspath(os.path.join(ROOT, "../.."))
LOGDIRS = ["logs/bench27/contaminated", "logs/bench27/recent2026", "logs/bench27/deep_hard"]
MODELS = {"nemotron-3-ultra-550b":"550b","gemma-4-26b":"26b","gemma-4-12b":"12b",
          "nemotron-cascade-2-30b":"30b","llama-3.3-70b":"70b","llama-3.1-8b":"8b"}
ALIAS = {"tic-tac-no":"pwn_tic-tac-no","scrabasm":"pwn_scrabasm","glotq":"web_glotq","single-trust":"web_single-trust"}
ARM = {ld.split("/")[-1] for ld in LOGDIRS}

def full_transcript(s):
    parts=[]
    for m in s.messages or []:
        t=getattr(m,"text","") or ""
        if t: parts.append(t)
        for tc in getattr(m,"tool_calls",None) or []:
            a=getattr(tc,"arguments",{}) or {}
            parts.append(" ".join(str(v) for v in a.values()))
    return "\n".join(parts)

rows=[]
for ld in LOGDIRS:
    arm=ld.split("/")[-1]
    for f in glob.glob(os.path.join(INSPECT_ROOT, ld, "*.eval")):
        try: l=read_eval_log(f)
        except Exception: continue
        mfull=(l.eval.model or "").split("/")[-1]
        if mfull not in MODELS: continue
        sh=MODELS[mfull]; scorer_name=None
        for s in (l.samples or []):
            tid=str(s.id).split(" (")[0]; tid=ALIAS.get(tid,tid)
            sc=next(iter((s.scores or {}).items()),(None,None))
            scorer_name, scobj = sc
            val = getattr(scobj,"value",None)
            solved = str(val).upper() in ("C","CORRECT","1")
            tgt=(s.target if isinstance(s.target,str) else (s.target[0] if s.target else "")) or ""
            submitted=(s.output.completion or "") if s.output else ""
            rows.append({
                "model": sh, "model_full": mfull, "arm": arm, "task": tid,
                "epoch": getattr(s,"epoch",1),
                "scorer": scorer_name, "score_value": val,
                "solved": solved,                              # ← 唯一權威「解出」判準
                "target_flag": tgt,
                "submitted": submitted[:400],
                "flag_in_submission": bool(tgt and tgt.lower() in submitted.lower()),
                "flag_in_transcript": bool(tgt and tgt.lower() in full_transcript(s).lower()),
                "log_file": os.path.basename(f),
            })

out=os.path.join(ROOT,"bench27_runs.json")
json.dump(rows, open(out,"w",encoding="utf-8"), ensure_ascii=False, indent=1)

# 小計
bym=collections.defaultdict(lambda:[0,0,0,0])  # runs, solved, flag_in_sub, flag_in_tr
tasks=collections.defaultdict(set)
for r in rows:
    a=bym[r["model"]]; a[0]+=1; a[1]+=r["solved"]; a[2]+=r["flag_in_submission"]; a[3]+=r["flag_in_transcript"]
    if r["solved"]: tasks[r["model"]].add((r["arm"],r["task"]))
print(f"寫出 {len(rows)} 筆 run → {out}\n")
print(f"{'model':6} {'runs':5} {'solved(C)':10} {'flag在提交':10} {'flag在transcript':16} {'解出題數':8}")
for sh in ["550b","26b","12b","30b","70b","8b"]:
    a=bym[sh]; print(f"{sh:6} {a[0]:<5} {a[1]:<10} {a[2]:<10} {a[3]:<16} {len(tasks[sh])}")
