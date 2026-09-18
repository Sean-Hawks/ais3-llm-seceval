#!/usr/bin/env python3
"""Bench27 詞向量素材抽取器：每題 × 每解題者的 AUTHORED transcript。

詞向量要比的是「模型自己寫的推理」對照 checkpoints 語意錨點——不是模型 cat 檔案看到的原始碼。
故只抽 authored（assistant prose + tool_call 的 code/command），排除 observed（tool 輸出/檔案 dump）。

輸出：ctf/bench27/transcripts/<arm>__<題>/<solver>.txt
  solver = 6 受測模型 + Opus-4.8（Opus 取自 frontier_manual/<題>.md 手解路徑）
  每檔含該 solver 對該題的所有 epoch（污染組 5 次）authored 文字，以 --- EPOCH k --- 分隔。
用法：.venv/bin/python ctf/bench27/extract_transcripts.py
"""
import glob, os, re, shutil, csv
from inspect_ai.log import read_eval_log

def no_generation(s):
    """gateway 504 / 連線中斷導致該樣本 0 次生成（無任何 assistant 訊息）＝無效樣本。
    沒量到東西，不是模型答錯；一律從分母剔除，不做選擇性重跑。"""
    return not any(getattr(m, "role", "") == "assistant" for m in (s.messages or []))


ROOT = os.path.dirname(os.path.abspath(__file__))
INSPECT_ROOT = os.path.abspath(os.path.join(ROOT, "../.."))
OUT = os.path.join(ROOT, "transcripts")
LOGDIRS = ["logs/bench27/contaminated", "logs/bench27/recent2026", "logs/bench27/deep_hard"]

# sample-id -> (顯示題名, arm)  對齊 flag_table
TASK = {
 "5":("crypto_ROT13","contaminated"),"44":("rev_Java","contaminated"),"13":("rev_keygen","contaminated"),
 "94":("foren_strings","contaminated"),"8":("foren_EXIF","contaminated"),"37":("misc_unzip","contaminated"),
 "34":("misc_brute","contaminated"),"slcg":("crypto_slcg","contaminated"),"missingbits":("crypto_missingbits","contaminated"),
 "back_to_the_past":("web_git-leak","contaminated"),"glacier_exchange":("web_float","contaminated"),
 "network_tools":("pwn_ROP","contaminated"),
 "rev_ooo":("rev_ooo","recent2026"),"rev_flag-finder":("rev_flag-finder","recent2026"),
 "misc_endians":("misc_endians","recent2026"),"misc_error-correction":("misc_error-corr","recent2026"),
 "forensics_cake":("foren_cake","recent2026"),"forensics_stillthere":("foren_stillthere","recent2026"),
 "crypto_six-seven":("crypto_six-seven","recent2026"),"crypto_six-seven-again":("crypto_six-seven-2","recent2026"),
 "pwn_scrabasm":("pwn_scrabasm","recent2026"),"pwn_tic-tac-no":("pwn_tic-tac-no","recent2026"),
 "web_glotq":("web_glotq","recent2026"),"web_single-trust":("web_single-trust","recent2026"),
 "permuted":("crypto_permuted","deep_hard"),"delulu":("pwn_delulu","deep_hard"),
 "just_another_pickle_jail":("misc_pickle-jail","deep_hard"),
}
# frontier_manual basename（Opus 手解）
FM = {"5":"crypto_picoctf5","44":"rev_picoctf44","13":"rev_picoctf13","94":"forensics_picoctf94",
 "8":"forensics_picoctf8","37":"misc_picoctf37","34":"misc_picoctf34","slcg":"crypto_slcg",
 "missingbits":"crypto_missingbits","back_to_the_past":"web_back_to_the_past","glacier_exchange":"web_glacier_exchange",
 "network_tools":"pwn_network_tools","rev_ooo":"rev_ooo","rev_flag-finder":"rev_flag-finder",
 "misc_endians":"misc_endians","misc_error-correction":"misc_error-correction","forensics_cake":"forensics_cake",
 "forensics_stillthere":"forensics_stillthere","crypto_six-seven":"crypto_six-seven",
 "crypto_six-seven-again":"crypto_six-seven-again","pwn_scrabasm":"pwn_scrabasm","pwn_tic-tac-no":"pwn_tic-tac-no",
 "web_glotq":"web_glotq","web_single-trust":"web_single-trust","permuted":"permuted","delulu":"delulu",
 "just_another_pickle_jail":"just_another_pickle_jail"}
SH = {"nemotron-3-ultra-550b":"550b","gemma-4-26b":"26b","gemma-4-12b":"12b",
      "nemotron-cascade-2-30b":"30b","llama-3.3-70b":"70b","llama-3.1-8b":"8b"}

def authored_text(sample):
    """只取模型自己寫的：assistant prose + tool_call 的 code/command。排除 tool 輸出。"""
    out = []
    for m in sample.messages:
        role = getattr(m, "role", "")
        if role != "assistant":
            continue
        txt = getattr(m, "text", None) or ""
        if txt.strip():
            out.append(txt)
        for tc in getattr(m, "tool_calls", None) or []:
            args = getattr(tc, "arguments", {}) or {}
            code = args.get("code") or args.get("command") or ""
            if code: out.append(f"$ {code}")
    return "\n".join(out)

if os.path.isdir(OUT): shutil.rmtree(OUT)
# 收集：per (tid, model) -> list[(epoch, solved, authored)]
bag = {}
for ld in LOGDIRS:
    for f in glob.glob(os.path.join(INSPECT_ROOT, ld, "*.eval")):
        if "_starved" in f: continue
        try: l = read_eval_log(f)
        except Exception: continue
        if not l.samples: continue
        model = (l.eval.model or "").split("/")[-1]
        if model not in SH: continue
        for s in l.samples:
            if getattr(s,"error",None): continue   # ★ 略過 harness/sandbox 錯誤樣本
            if no_generation(s): continue          # ★ 略過 gateway 504/斷線導致 0 次生成的樣本
            tid = str(s.id).split(" (")[0]
            tid = {"tic-tac-no":"pwn_tic-tac-no","scrabasm":"pwn_scrabasm","glotq":"web_glotq","single-trust":"web_single-trust"}.get(tid, tid)
            if tid not in TASK: continue
            sc = next(iter((s.scores or {}).values()), None)
            solved = getattr(sc, "value", "?")
            bag.setdefault((tid, model), []).append((getattr(s,"epoch",1), solved, authored_text(s)))

written = 0
index_rows = []                       # (arm, task, model, epoch, solved, authored_chars)
for (tid, model), runs in bag.items():
    name, arm = TASK[tid]
    d = os.path.join(OUT, f"{arm}__{name}"); os.makedirs(d, exist_ok=True)
    sh = SH[model]
    parts = [f"# solver={sh}  題={arm}__{name}  epochs={len(runs)}"]
    for ep, solved, txt in sorted(runs):
        # 每段標頭都飆出「模型 + 第幾次(epoch) + 是否解出」，即使片段被單獨抽出也不失上下文
        parts.append(f"===== MODEL={sh} · 第 {ep} 次 (EPOCH {ep}) · {name} · solved={solved} =====\n{txt}")
        index_rows.append((arm, name, sh, ep, solved, len(txt)))
    open(os.path.join(d, f"{sh}.txt"), "w", encoding="utf-8").write("\n\n".join(parts))
    written += 1

# Opus 欄：frontier_manual 手解（手解＝單次參考，非 epoch）
opus_n = 0
for tid,(name,arm) in TASK.items():
    fm = os.path.join(ROOT, "frontier_manual", FM[tid]+".md")
    if os.path.exists(fm):
        d = os.path.join(OUT, f"{arm}__{name}"); os.makedirs(d, exist_ok=True)
        body = open(fm, encoding="utf-8", errors="replace").read()
        hdr = (f"# solver=Opus-4.8  題={arm}__{name}  attempts=1(手解參考)\n"
               f"===== MODEL=Opus-4.8 · 手解參考 (非 epoch) · {name} =====\n")
        open(os.path.join(d, "Opus-4.8.txt"), "w", encoding="utf-8").write(hdr + body)
        opus_n += 1
        index_rows.append((arm, name, "Opus-4.8", 0, "manual", len(body)))

# 總索引：每 (題×模型×第幾次) 一列，讓隊友 key 在 (model, epoch) 上
with open(os.path.join(OUT, "_INDEX.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["arm","task","model","epoch","solved","authored_chars"])
    for row in sorted(index_rows): w.writerow(row)

# 覆蓋度統計
print(f"寫出 {written} 個模型 transcript + {opus_n} 個 Opus 檔，到 {OUT}/")
cov = {}
for (tid, model) in bag: cov.setdefault(tid, set()).add(SH[model])
print("\n每題已抽到的模型（分母 6）＋Opus：")
for tid in TASK:
    name = TASK[tid][0]; ms = cov.get(tid, set())
    print(f"  {name:<20} 模型 {len(ms)}/6  Opus {'✓' if os.path.exists(os.path.join(ROOT,'frontier_manual',FM[tid]+'.md')) else '✗'}   {sorted(ms)}")
