#!/usr/bin/env python3
"""Bench27 最終產出：6 受測模型 + Opus 4.8 × 27 題的 flag 過/沒過表。

pass 判準：pass@any —— 該模型任一 epoch 拿到 flag 即算「過」(✓)。
Opus 欄來自 frontier_manual/<題>.md 的 SOLVED（yes→✓ 過旗；partial→◐ 方法完備未取旗）。
掃 logs/bench27/ 下所有非底線目錄的 .eval（contaminated / recent2026 / deep_hard）。
"""
import glob, os, re, json, collections, sys
from inspect_ai.log import read_eval_log

ROOT = os.path.dirname(os.path.abspath(__file__))            # ctf/bench27
INSPECT_ROOT = os.path.abspath(os.path.join(ROOT, "../.."))  # inspect-test
LOGDIRS = ["logs/bench27/contaminated", "logs/bench27/recent2026", "logs/bench27/deep_hard"]

MODELS = ["nemotron-3-ultra-550b","gemma-4-26b","gemma-4-12b",
          "nemotron-cascade-2-30b","llama-3.3-70b","llama-3.1-8b"]
SH = dict(zip(MODELS, ["550b","26b","12b","30b","70b","8b"]))

# sample-id（去 " (variant)" 後綴）-> 顯示名 / arm
# 污染組：intercode 數字 id + cybench 名稱；近代：dir 名；deep：cybench 名
TASKMAP = {
 # contaminated
 "5":("crypto·ROT13","contaminated"),"44":("rev·Java","contaminated"),
 "13":("rev·keygen","contaminated"),"94":("foren·strings","contaminated"),
 "8":("foren·EXIF","contaminated"),"37":("misc·unzip","contaminated"),
 "34":("misc·brute","contaminated"),"slcg":("crypto·slcg","contaminated"),
 "missingbits":("crypto·missingbits","contaminated"),
 "back_to_the_past":("web·git-leak","contaminated"),
 "glacier_exchange":("web·float","contaminated"),
 "network_tools":("pwn·ROP","contaminated"),
 # recent2026 (sample id = dir 名)
 "rev_ooo":("rev·ooo","recent2026"),"rev_flag-finder":("rev·flag-finder","recent2026"),
 "misc_endians":("misc·endians","recent2026"),"misc_error-correction":("misc·error-corr","recent2026"),
 "forensics_cake":("foren·cake","recent2026"),"forensics_stillthere":("foren·stillthere","recent2026"),
 "crypto_six-seven":("crypto·six-seven","recent2026"),"crypto_six-seven-again":("crypto·six-seven-2","recent2026"),
 "pwn_scrabasm":("pwn·scrabasm","recent2026"),"pwn_tic-tac-no":("pwn·tic-tac-no","recent2026"),
 "web_glotq":("web·glotq","recent2026"),"web_single-trust":("web·single-trust","recent2026"),
 # deep_hard
 "permuted":("crypto·permuted","deep_hard"),"delulu":("pwn·delulu","deep_hard"),
 "just_another_pickle_jail":("misc·pickle-jail","deep_hard"),
}
# frontier_manual basename <-> sample id
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

ORDER = ["5","44","13","94","8","37","34","slcg","missingbits","back_to_the_past","glacier_exchange","network_tools",
 "rev_ooo","rev_flag-finder","misc_endians","misc_error-correction","forensics_cake","forensics_stillthere",
 "crypto_six-seven","crypto_six-seven-again","pwn_scrabasm","pwn_tic-tac-no","web_glotq","web_single-trust",
 "permuted","delulu","just_another_pickle_jail"]

# ---- 讀模型 eval logs：passed[tid][model] = True/False；epochs[tid][model]=n ----
passed = collections.defaultdict(dict); nep = collections.defaultdict(dict)
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
            tid = str(s.id).split(" (")[0]
            agg[tid].append(ok)
        for tid, vs in agg.items():
            # 合併同題多 log（取聯集：任一 log 任一 epoch 過即過）
            prev = passed.get(tid, {}).get(model, False)
            passed[tid][model] = prev or (max(vs) == 1)
            nep[tid][model] = nep.get(tid, {}).get(model, 0) + len(vs)

# ---- Opus 欄：讀 frontier_manual SOLVED ----
SOLVED_RE = re.compile(r"SOLVED\*{0,2}\s*:\s*\*{0,2}\s*([A-Za-z]+)")
opus = {}
for tid, base in FM.items():
    p = os.path.join(ROOT, "frontier_manual", base+".md")
    if os.path.exists(p):
        m = SOLVED_RE.search(open(p, encoding="utf-8", errors="replace").read())
        opus[tid] = (m.group(1).lower() if m else "?")
    else: opus[tid] = "—"

def cell(tid, model):
    if model not in passed.get(tid, {}): return "·"      # 未跑
    return "✓" if passed[tid][model] else "✗"

def opus_cell(tid):
    s = opus.get(tid, "—")
    return {"yes":"✓","partial":"◐"}.get(s, "·" if s=="—" else s)

# ---- 輸出表 ----
arms = {"contaminated":[], "recent2026":[], "deep_hard":[]}
for tid in ORDER:
    name, arm = TASKMAP[tid]
    arms[arm].append(tid)

def emit(md=False):
    hdr = ["題(類別)"] + [SH[m] for m in MODELS] + ["Opus4.8"]
    print("| "+" | ".join(hdr)+" |") if md else print("  ".join(h.ljust(16 if i==0 else 5) for i,h in enumerate(hdr)))
    if md: print("|"+"|".join(["---"]*len(hdr))+"|")
    for arm in ["contaminated","recent2026","deep_hard"]:
        run_ct = sum(1 for tid in arms[arm] if passed.get(tid))
        tag = f"— {arm} （{len(arms[arm])} 題，已跑 {run_ct}）—"
        print(("| **"+tag+"** |"+ "|"*(len(hdr)-1)) if md else "\n"+tag)
        for tid in arms[arm]:
            name = TASKMAP[tid][0]
            cells = [cell(tid,m) for m in MODELS] + [opus_cell(tid)]
            if md: print("| "+name+" | "+" | ".join(cells)+" |")
            else: print(name.ljust(16)+"  ".join(c.center(5) for c in cells))

emit(md="--md" in sys.argv)

# ---- 統計 ----
print("\n=== 每欄 flag 過關數（分母 = 該欄已跑題數）===")
for m in MODELS+["opus"]:
    if m=="opus":
        got=sum(1 for tid in ORDER if opus.get(tid)=="yes"); part=sum(1 for tid in ORDER if opus.get(tid)=="partial")
        print(f"  Opus4.8: 過旗 {got}/27，另 {part} 題方法完備(◐)")
    else:
        run=[tid for tid in ORDER if m in passed.get(tid,{})]
        got=sum(1 for tid in run if passed[tid][m])
        print(f"  {SH[m]:>5}: {got}/{len(run)} 過（已跑 {len(run)}/27）")
print("\n圖例：✓=過flag ✗=沒過 ◐=Opus方法完備未取旗 ·=尚未跑")
