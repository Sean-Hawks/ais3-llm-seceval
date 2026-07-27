#!/usr/bin/env python3
"""快照目前跑批狀態 → run_status.json（給 dashboard 的『即時跑批狀態』區塊）。
非真即時（artifact 是靜態）：每次重建 dashboard 時刷新這份，republish 即更新。"""
import os, json, glob, subprocess, datetime, collections
from inspect_ai.log import read_eval_log
ROOT = os.path.dirname(os.path.abspath(__file__))
INSPECT = os.path.abspath(os.path.join(ROOT, "../.."))

def procs(pat):
    try: return subprocess.run(["pgrep","-fl",pat],capture_output=True,text=True).stdout.strip()
    except Exception: return ""

# 目前在跑的 inspect eval（哪個模型/階段）
ps = subprocess.run(["ps","axo","command"],capture_output=True,text=True).stdout
running=[]
for line in ps.splitlines():
    if "inspect eval" in line and "grep" not in line:
        m = next((t.split("/")[-1] for t in line.split() if t.startswith("openai-api/ais3")), "?")
        stage = "deep_hard" if "deep_hard" in line else ("recent2026" if "recent2026" in line or "recent2026_eval" in line else ("contaminated" if "contaminated" in line else "?"))
        sid = "tic-tac-no,scrabasm" if "tic-tac-no" in line else None
        running.append({"model":m,"stage":stage,"pwn_rerun":bool(sid)})

# pwn 重跑：哪些模型的 pwn 已是有效資料
MODELS=["550b","26b","12b","30b","70b","8b"]
pwn_done=set()
for f in glob.glob(os.path.join(INSPECT,"logs/bench27/recent2026","*.eval")):
    try: l=read_eval_log(f)
    except Exception: continue
    if "pwn-rerun" not in (getattr(l.eval,"tags",[]) or []): continue
    mm=(l.eval.model or "").split("/")[-1]
    sh={"nemotron-3-ultra-550b":"550b","gemma-4-26b":"26b","gemma-4-12b":"12b","nemotron-cascade-2-30b":"30b","llama-3.3-70b":"70b","llama-3.1-8b":"8b"}.get(mm)
    if l.status=="success" and sh: pwn_done.add(sh)

# Opus 5ep 進度
op = os.path.join(ROOT,"opus_runs.json")
opus_done = len(json.load(open(op,encoding="utf-8"))) if os.path.exists(op) else 0

status={
  "stamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
  "pwn_rerun": {"done": sorted(pwn_done, key=lambda x: MODELS.index(x)), "total": 6,
                "alive": bool(procs("run_pwn_rerun"))},
  "opus5ep": {"done": opus_done, "total": 27, "alive": bool(procs("opus-arena") or procs("_opus_"))},
  "running": running,
}
json.dump(status, open(os.path.join(ROOT,"run_status.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(status, ensure_ascii=False))
