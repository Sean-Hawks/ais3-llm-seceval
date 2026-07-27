#!/usr/bin/env python3
"""每個受測模型『實際解題』的完整 wp：推理 + 下的指令 + 工具輸出 + 提交/flag。
與標準解答 wp_27/ 平行，命名一致。輸出 agent_wp/<清楚題名>/<model>.md（含所有 epoch）。
工具輸出過長會截斷（預設 1600 字/則）以保可讀。"""
import glob, os, json, collections
from inspect_ai.log import read_eval_log

ROOT = os.path.dirname(os.path.abspath(__file__))
INSPECT_ROOT = os.path.abspath(os.path.join(ROOT, "../.."))
OUT = os.path.join(ROOT, "agent_wp")
LOGDIRS = ["logs/bench27/contaminated", "logs/bench27/recent2026", "logs/bench27/deep_hard"]  # 27 題
TOOL_TRUNC = 1600

SH = {"nemotron-3-ultra-550b":"550b","gemma-4-26b":"26b","gemma-4-12b":"12b",
      "nemotron-cascade-2-30b":"30b","llama-3.3-70b":"70b","llama-3.1-8b":"8b"}
ALIAS = {"tic-tac-no":"pwn_tic-tac-no","scrabasm":"pwn_scrabasm","glotq":"web_glotq","single-trust":"web_single-trust"}
# tid -> (arm, 清楚題名)  對齊 wp_27
CLEAR = {
 "5":("contaminated","C01_crypto_ROT13"),"slcg":("contaminated","C02_crypto_sequential-LCG"),
 "missingbits":("contaminated","C03_crypto_RSA-missing-bits"),"44":("contaminated","C04_rev_VaultDoor-char-mapping"),
 "13":("contaminated","C05_rev_keygenme-sha256"),"94":("contaminated","C06_forensics_strings-in-image"),
 "8":("contaminated","C07_forensics_EXIF-metadata"),"37":("contaminated","C08_misc_hidden-file-unzip"),
 "34":("contaminated","C09_misc_zip-password-brute"),"back_to_the_past":("contaminated","C10_web_git-repo-leak"),
 "glacier_exchange":("contaminated","C11_web_float-balance-overflow"),"network_tools":("contaminated","C12_pwn_ROP-chain"),
 "crypto_six-seven":("recent2026","R01_crypto_digit-6-7-prime-factoring"),
 "crypto_six-seven-again":("recent2026","R02_crypto_coppersmith-partial-key"),
 "rev_ooo":("recent2026","R03_rev_unicode-homoglyph-flag"),"rev_flag-finder":("recent2026","R04_rev_nonogram-regex-z3"),
 "forensics_cake":("recent2026","R05_forensics_pcap-http-cookie"),"forensics_stillthere":("recent2026","R06_forensics_pcap-icmp-covert"),
 "misc_endians":("recent2026","R07_misc_utf16-endianness"),"misc_error-correction":("recent2026","R08_misc_QR-reed-solomon-rebuild"),
 "web_glotq":("recent2026","R09_web_go-parser-differential"),"web_single-trust":("recent2026","R10_web_AES-GCM-short-tag"),
 "pwn_tic-tac-no":("recent2026","R11_pwn_OOB-global-write"),"pwn_scrabasm":("recent2026","R12_pwn_shellcode-PRNG"),
 "permuted":("deep_hard","D01_crypto_permutation-group-DLP"),"delulu":("deep_hard","D02_pwn_format-string-overwrite"),
 "just_another_pickle_jail":("deep_hard","D03_misc_pickle-jail-escape"),
}

def render_epoch(s, ep, solved, target):
    L=[f"### 第 {ep} 次 (EPOCH {ep}) — solved={'✅ C' if solved else '❌ I'}"]
    for m in s.messages or []:
        role=getattr(m,"role","")
        txt=(getattr(m,"text","") or "").strip()
        if role=="assistant":
            if txt: L.append(txt)
            for tc in getattr(m,"tool_calls",None) or []:
                a=getattr(tc,"arguments",{}) or {}
                code=a.get("code") or a.get("command") or a.get("answer") or json.dumps(a,ensure_ascii=False)
                tool=getattr(tc,"function","tool")
                L.append(f"```bash\n$ [{tool}] {code}\n```")
        elif role=="tool":
            out=txt
            if len(out)>TOOL_TRUNC: out=out[:TOOL_TRUNC]+f"\n…(截斷，共 {len(txt)} 字)"
            if out: L.append(f"```output\n{out}\n```")
    L.append(f"\n**提交**：`{(s.output.completion or '')[:200] if s.output else ''}`　**正解**：`{target}`")
    return "\n\n".join(L)

# 收集 per (tid, model) -> list[(ep, solved, markdown)]
bag=collections.defaultdict(lambda: collections.defaultdict(list))
for ld in LOGDIRS:
    for f in glob.glob(os.path.join(INSPECT_ROOT, ld, "*.eval")):
        try: l=read_eval_log(f)
        except Exception: continue
        mfull=(l.eval.model or "").split("/")[-1]
        if mfull not in SH: continue
        for s in (l.samples or []):
            tid=ALIAS.get(str(s.id).split(" (")[0], str(s.id).split(" (")[0])
            if tid not in CLEAR: continue
            sc=next(iter((s.scores or {}).values()),None)
            solved=bool(sc and str(sc.value).upper() in ("C","CORRECT","1"))
            tgt=(s.target if isinstance(s.target,str) else (s.target[0] if s.target else "")) or ""
            bag[tid][SH[mfull]].append((getattr(s,"epoch",1), solved, render_epoch(s,getattr(s,"epoch",1),solved,tgt)))

if os.path.isdir(OUT): __import__("shutil").rmtree(OUT)
os.makedirs(OUT)
MODELS6=["550b","26b","12b","30b","70b","8b"]
n_files=0; idx=[]
for tid,(arm,clear) in CLEAR.items():
    d=os.path.join(OUT, clear); os.makedirs(d, exist_ok=True)
    per_model_solved={}
    for m in MODELS6:
        runs=sorted(bag[tid].get(m, []))
        nsolv=sum(1 for _,sv,_ in runs if sv)
        per_model_solved[m]=(nsolv,len(runs))
        head=(f"# {clear} — {m} 實際解題 wp\n\n"
              f"題目：{arm} / `{tid}`　·　此模型 {nsolv}/{len(runs)} epoch 解出　·　"
              f"標準解答見 `../../wp_27/{clear}.md`\n\n"
              f"> 內容＝模型自己的推理＋下的指令＋工具輸出（過長截斷）＋提交。\n\n---\n\n")
        body="\n\n---\n\n".join(md for _,_,md in runs) or "（此模型無 run 紀錄）"
        open(os.path.join(d, f"{m}.md"),"w",encoding="utf-8").write(head+body)
        n_files+=1
    idx.append((clear, arm, tid, per_model_solved))

with open(os.path.join(OUT,"INDEX.md"),"w",encoding="utf-8") as f:
    f.write("# Bench27 — Agent 實際解題 wp（27 題 × 6 模型）\n\n")
    f.write("每題資料夾 `<清楚題名>/<model>.md`＝該模型**自己跑出來**的完整解題過程")
    f.write("（推理＋指令＋輸出＋提交）。標準解答對照見 `../wp_27/`。\n\n")
    f.write("格子＝該模型解出 epoch 數 / 5。\n\n")
    f.write("| 題 | "+" | ".join(MODELS6)+" |\n|---|"+"---|"*6+"\n")
    for clear,arm,tid,pms in idx:
        cells=" | ".join(f"{pms[m][0]}/{pms[m][1]}" for m in MODELS6)
        f.write(f"| `{clear}` | {cells} |\n")

print(f"寫出 {n_files} 篇 agent wp（27 題 × 6 模型）→ {OUT}/  + INDEX.md")
