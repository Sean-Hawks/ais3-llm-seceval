#!/usr/bin/env python3
"""每題×每模型的『成本剖面』：5 epoch 平均 token 量與耗時。

判準與 export_runs_json.py 完全一致（同一去重、同一無效樣本排除規則），只是把量測欄位
從 solved 換成 tokens/time：
  - input/output/total tokens ← sample.model_usage（該樣本所有 model 呼叫加總）
  - working_time ← agent 實際工作秒數（不含 gateway 排隊/退避）
  - total_time   ← 牆鐘秒數（含排隊，兩者差距＝基礎設施稅）
輸出 bench27_cost.json（每 run 一筆）＋ bench27_cost_runs 聚合（每 model×題，n 個 epoch 平均）。
"""
import glob, os, json, collections
from inspect_ai.log import read_eval_log

ROOT = os.path.dirname(os.path.abspath(__file__))
INSPECT_ROOT = os.path.abspath(os.path.join(ROOT, "../.."))
LOGDIRS = ["logs/bench27/contaminated", "logs/bench27/recent2026", "logs/bench27/deep_hard"]
MODELS = {"nemotron-3-ultra-550b":"550b","gemma-4-26b":"26b","gemma-4-12b":"12b",
          "nemotron-cascade-2-30b":"30b","llama-3.3-70b":"70b","llama-3.1-8b":"8b"}
ALIAS = {"tic-tac-no":"pwn_tic-tac-no","scrabasm":"pwn_scrabasm","glotq":"web_glotq","single-trust":"web_single-trust"}


def no_generation(s):
    return not any(getattr(m, "role", "") == "assistant" for m in (s.messages or []))


if not any(glob.glob(os.path.join(INSPECT_ROOT, ld, "*.eval")) for ld in LOGDIRS):
    raise SystemExit("No raw logs found; historical snapshot was not overwritten. Use python -m ais3_bench export for new runs.")

bytm = {}
for ld in LOGDIRS:
    arm = ld.split("/")[-1]
    for f in sorted(glob.glob(os.path.join(INSPECT_ROOT, ld, "*.eval"))):
        try: l = read_eval_log(f)
        except Exception: continue
        mfull = (l.eval.model or "").split("/")[-1]
        if mfull not in MODELS: continue
        sh = MODELS[mfull]; fname = os.path.basename(f)
        for s in (l.samples or []):
            if getattr(s, "error", None): continue
            if no_generation(s): continue
            tid = str(s.id).split(" (")[0]; tid = ALIAS.get(tid, tid)
            mu = getattr(s, "model_usage", None) or {}
            it = sum(u.input_tokens or 0 for u in mu.values())
            ot = sum(u.output_tokens or 0 for u in mu.values())
            tt = sum(u.total_tokens or 0 for u in mu.values())
            n_msg = sum(1 for m in (s.messages or []) if getattr(m, "role", "") == "assistant")
            sc = next(iter((s.scores or {}).values()), None)
            solved = str(getattr(sc, "value", None)).upper() in ("C", "CORRECT", "1")
            rec = {"model": sh, "arm": arm, "task": tid, "epoch": getattr(s, "epoch", 1),
                   "solved": solved, "input_tokens": it, "output_tokens": ot, "total_tokens": tt,
                   "assistant_msgs": n_msg,
                   "working_time": round(getattr(s, "working_time", 0) or 0, 1),
                   "total_time": round(getattr(s, "total_time", 0) or 0, 1),
                   "limit": str(getattr(s, "limit", "") or ""), "log_file": fname}
            k = (arm, tid, sh); cur = bytm.get(k)
            if cur is None or fname > cur["file"]: bytm[k] = {"file": fname, "rows": [rec]}
            elif fname == cur["file"]: cur["rows"].append(rec)

rows = [r for v in bytm.values() for r in v["rows"]]
if not rows:
    raise SystemExit("No valid rows; historical snapshot was not overwritten.")

json.dump(rows, open(os.path.join(ROOT, "bench27_cost.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"寫出 {len(rows)} 筆 → bench27_cost.json")

agg = collections.defaultdict(list)
for r in rows: agg[(r["arm"], r["task"], r["model"])].append(r)
print(f"{len(agg)} 個 (題×模型) 格；每格 epoch 數分佈：",
      dict(collections.Counter(len(v) for v in agg.values())))
