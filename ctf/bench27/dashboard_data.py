#!/usr/bin/env python3
"""匯出儀表板 JSON：每 (題×模型) 的 n/總 epoch（解出 epoch 數 / 已跑 epoch 數）+ Opus 參考欄。
輸出到 stdout（JSON）。沿用 flag_table.py 的 TASKMAP/ALIAS/FM 邏輯。"""
import glob, os, re, json, collections
from inspect_ai.log import read_eval_log

ROOT = os.path.dirname(os.path.abspath(__file__))
INSPECT_ROOT = os.path.abspath(os.path.join(ROOT, "../.."))
LOGDIRS = ["logs/bench27/contaminated", "logs/bench27/recent2026", "logs/bench27/deep_hard"]

MODELS = ["nemotron-3-ultra-550b","gemma-4-26b","gemma-4-12b",
          "nemotron-cascade-2-30b","llama-3.3-70b","llama-3.1-8b"]
SH = dict(zip(MODELS, ["550b","26b","12b","30b","70b","8b"]))

TASKMAP = {
 "5":("crypto·ROT13","contaminated","crypto"),"44":("rev·Java","contaminated","rev"),
 "13":("rev·keygen","contaminated","rev"),"94":("foren·strings","contaminated","forensics"),
 "8":("foren·EXIF","contaminated","forensics"),"37":("misc·unzip","contaminated","misc"),
 "34":("misc·brute","contaminated","misc"),"slcg":("crypto·slcg","contaminated","crypto"),
 "missingbits":("crypto·missingbits","contaminated","crypto"),
 "back_to_the_past":("web·git-leak","contaminated","web"),
 "glacier_exchange":("web·float","contaminated","web"),
 "network_tools":("pwn·ROP","contaminated","pwn"),
 "rev_ooo":("rev·ooo","recent2026","rev"),"rev_flag-finder":("rev·flag-finder","recent2026","rev"),
 "misc_endians":("misc·endians","recent2026","misc"),"misc_error-correction":("misc·error-corr","recent2026","misc"),
 "forensics_cake":("foren·cake","recent2026","forensics"),"forensics_stillthere":("foren·stillthere","recent2026","forensics"),
 "crypto_six-seven":("crypto·six-seven","recent2026","crypto"),"crypto_six-seven-again":("crypto·six-seven-2","recent2026","crypto"),
 "pwn_scrabasm":("pwn·scrabasm","recent2026","pwn"),"pwn_tic-tac-no":("pwn·tic-tac-no","recent2026","pwn"),
 "web_glotq":("web·glotq","recent2026","web"),"web_single-trust":("web·single-trust","recent2026","web"),
 "permuted":("crypto·permuted","deep_hard","crypto"),"delulu":("pwn·delulu","deep_hard","pwn"),
 "just_another_pickle_jail":("misc·pickle-jail","deep_hard","misc"),
}
FM = {"5":"crypto_picoctf5","44":"rev_picoctf44","13":"rev_picoctf13","94":"forensics_picoctf94",
 "8":"forensics_picoctf8","37":"misc_picoctf37","34":"misc_picoctf34","slcg":"crypto_slcg",
 "missingbits":"crypto_missingbits","back_to_the_past":"web_back_to_the_past",
 "glacier_exchange":"web_glacier_exchange","network_tools":"pwn_network_tools",
 "rev_ooo":"rev_ooo","rev_flag-finder":"rev_flag-finder","misc_endians":"misc_endians",
 "misc_error-correction":"misc_error-correction","forensics_cake":"forensics_cake",
 "forensics_stillthere":"forensics_stillthere","crypto_six-seven":"crypto_six-seven",
 "crypto_six-seven-again":"crypto_six-seven-again","pwn_scrabasm":"pwn_scrabasm",
 "pwn_tic-tac-no":"pwn_tic-tac-no","web_glotq":"web_glotq","web_single-trust":"web_single-trust",
 "permuted":"permuted","delulu":"delulu","just_another_pickle_jail":"just_another_pickle_jail"}
ALIAS = {"tic-tac-no":"pwn_tic-tac-no","scrabasm":"pwn_scrabasm","glotq":"web_glotq","single-trust":"web_single-trust"}
ORDER = ["5","44","13","94","8","37","34","slcg","missingbits","back_to_the_past","glacier_exchange","network_tools",
 "rev_ooo","rev_flag-finder","misc_endians","misc_error-correction","forensics_cake","forensics_stillthere",
 "crypto_six-seven","crypto_six-seven-again","pwn_scrabasm","pwn_tic-tac-no","web_glotq","web_single-trust",
 "permuted","delulu","just_another_pickle_jail"]

# solved[tid][model] = 解出的 epoch 數；total[tid][model] = 已跑 epoch 數
solved = collections.defaultdict(dict); total = collections.defaultdict(dict)
for ld in LOGDIRS:
    for f in glob.glob(os.path.join(INSPECT_ROOT, ld, "*.eval")):
        try: l = read_eval_log(f)
        except Exception: continue
        if not l.samples: continue
        model = (l.eval.model or "").split("/")[-1]
        if model not in MODELS: continue
        agg = collections.defaultdict(list)
        for s in l.samples:
            v = None
            for k,vv in (s.scores or {}).items(): v = vv.value; break
            ok = 1 if (v==1 or str(v).upper() in ("C","CORRECT")) else 0
            tid = str(s.id).split(" (")[0]; tid = ALIAS.get(tid, tid)
            agg[tid].append(ok)
        for tid, vs in agg.items():
            solved[tid][model] = solved.get(tid, {}).get(model, 0) + sum(vs)
            total[tid][model]  = total.get(tid, {}).get(model, 0) + len(vs)

SOLVED_RE = re.compile(r"SOLVED\*{0,2}\s*:\s*\*{0,2}\s*([A-Za-z]+)")
opus = {}
for tid, base in FM.items():
    p = os.path.join(ROOT, "frontier_manual", base+".md")
    if os.path.exists(p):
        m = SOLVED_RE.search(open(p, encoding="utf-8", errors="replace").read())
        opus[tid] = (m.group(1).lower() if m else "?")
    else: opus[tid] = "—"

rows = []
for tid in ORDER:
    name, arm, cat = TASKMAP[tid]
    cells = {}
    for m in MODELS:
        if m in total.get(tid, {}):
            cells[SH[m]] = {"s": solved[tid][m], "t": total[tid][m]}
        else:
            cells[SH[m]] = None   # 尚未跑
    rows.append({"tid": tid, "name": name, "arm": arm, "cat": cat,
                 "cells": cells, "opus": opus.get(tid, "—")})

print(json.dumps({
    "models": [SH[m] for m in MODELS],
    "rows": rows,
    "generated_note": "n/總 = 解出 epoch 數 / 已跑 epoch 數；pass@any = s>0",
}, ensure_ascii=False, indent=1))
