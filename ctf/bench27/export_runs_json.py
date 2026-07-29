#!/usr/bin/env python3
"""把所有跑完的 agent run 轉成單一權威 JSON（每 run＝一個 model×題×epoch 一筆）。
供跨方比對：判「解出」唯一依據＝scorer 的 value C/I；另附 flag 是否出現在提交/整段 transcript，
讓 retrieved(flag-grep) 與 solved(scorer) 的差異一眼可見。
輸出：ctf/bench27/bench27_runs.json（陣列）＋ stdout 印每模型小計。"""
import glob, os, json, collections
from inspect_ai.log import read_eval_log

def no_generation(s):
    """gateway 504 / 連線中斷導致該樣本 0 次生成（無任何 assistant 訊息）＝無效樣本。
    沒量到東西，不是模型答錯；一律從分母剔除，不做選擇性重跑。"""
    return not any(getattr(m, "role", "") == "assistant" for m in (s.messages or []))


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

# ★ 去重（整次取代語意）：同一 (arm,題,模型) 可能被跑過多次（例：arm64 pwn 修好後重跑，
#   舊 5-epoch 壞檔與新 1-epoch 檔並存）。**每個 (arm,題,模型) 只保留「最新那一次跑」的全部 epoch**
#   ——用最新 log 檔（檔名 ISO 時間戳，字典序即時序）的樣本整組取代舊檔，1-epoch 重跑即可完整
#   洗掉舊 5-epoch（不會殘留舊 epoch 2–5）。cybench 一檔含多題故按 (題,模型) 而非整檔判斷。
bytm={}   # (arm,tid,sh) -> {"file": 最新log檔名, "rows": [該檔此key的所有樣本]}
for ld in LOGDIRS:
    arm=ld.split("/")[-1]
    for f in sorted(glob.glob(os.path.join(INSPECT_ROOT, ld, "*.eval"))):  # 舊→新
        try: l=read_eval_log(f)
        except Exception: continue
        mfull=(l.eval.model or "").split("/")[-1]
        if mfull not in MODELS: continue
        sh=MODELS[mfull]; scorer_name=None; fname=os.path.basename(f)
        for s in (l.samples or []):
            if getattr(s,"error",None): continue   # ★ 略過 harness/sandbox 錯誤樣本（非能力訊號，例：pwn jail 未privileged→容器exit1）
            if no_generation(s): continue          # ★ 略過 gateway 504/斷線導致 0 次生成的樣本（沒量到東西，非答錯）
            tid=str(s.id).split(" (")[0]; tid=ALIAS.get(tid,tid)
            sc=next(iter((s.scores or {}).items()),(None,None))
            scorer_name, scobj = sc
            val = getattr(scobj,"value",None)
            solved = str(val).upper() in ("C","CORRECT","1")
            tgt=(s.target if isinstance(s.target,str) else (s.target[0] if s.target else "")) or ""
            submitted=(s.output.completion or "") if s.output else ""
            rec={
                "model": sh, "model_full": mfull, "arm": arm, "task": tid,
                "epoch": getattr(s,"epoch",1),
                "scorer": scorer_name, "score_value": val,
                "solved": solved,                              # ← 唯一權威「解出」判準
                "working_time": round(getattr(s,"working_time",0) or 0, 1),  # agent 實際工作秒數（非排隊）
                "total_time": round(getattr(s,"total_time",0) or 0, 1),
                "target_flag": tgt,
                "submitted": submitted[:400],
                "flag_in_submission": bool(tgt and tgt.lower() in submitted.lower()),
                "flag_in_transcript": bool(tgt and tgt.lower() in full_transcript(s).lower()),
                "log_file": fname,
            }
            k=(arm,tid,sh); cur=bytm.get(k)
            if cur is None or fname>cur["file"]:      # 更新檔 → 整組換掉舊檔
                bytm[k]={"file":fname,"rows":[rec]}
            elif fname==cur["file"]:                  # 同一檔（多 epoch）→ 累加
                cur["rows"].append(rec)
            # fname<cur["file"] ＝更舊檔，整組略過

out=os.path.join(ROOT,"bench27_runs.json")
rows=[r for v in bytm.values() for r in v["rows"]]
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
