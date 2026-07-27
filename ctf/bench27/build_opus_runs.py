#!/usr/bin/env python3
"""彙整 Opus 5-epoch 盲解成績 → opus_runs.json（keyed by tid，供 dashboard 當頂端標準欄）。
來源：opus_runs_static.json（靜態 13 題）＋ opus_runs_docker.json（Docker 14 題，跑完才有）。
key 用 dashboard 的 tid（clear→tid 來自 opus_tasks.json）。"""
import os, json
ROOT = os.path.dirname(os.path.abspath(__file__))
clear2tid = {t["clear"]: t["tid"] for t in json.load(open(os.path.join(ROOT,"opus_tasks.json"),encoding="utf-8"))}
merged = {}
for fn in ("opus_runs_static.json","opus_runs_docker.json"):
    p = os.path.join(ROOT, fn)
    if not os.path.exists(p): continue
    for clear, v in json.load(open(p,encoding="utf-8")).items():
        tid = clear2tid.get(clear, clear)
        merged[tid] = {"n": v["n"], "t": v.get("t",5), "clear": clear}
json.dump(merged, open(os.path.join(ROOT,"opus_runs.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
done = len(merged); solved = sum(1 for v in merged.values() if v["n"]>0)
print(f"opus_runs.json: {done}/27 題有 5-epoch 資料；其中 pass@any {solved} 題")
print("  n/5:", " ".join(f"{v['clear'][:6]}={v['n']}" for v in merged.values()))
