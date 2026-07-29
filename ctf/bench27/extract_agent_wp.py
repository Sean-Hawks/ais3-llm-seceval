#!/usr/bin/env python3
"""每個受測模型『實際解題』的完整 wp：推理 + 下的指令 + 工具輸出 + 提交/flag。
與標準解答 wp_27/ 平行，命名一致。輸出 agent_wp/<清楚題名>/<model>.md（含所有 epoch）。
工具輸出過長會截斷（預設 1600 字/則）以保可讀。
⚠ 本腳本會 rmtree 整個 agent_wp/ 重建，**只產 6 個受測模型**；Opus-4.8.md 由 extract_opus_wp.py 產，
  故跑完本腳本後務必接著跑 `extract_opus_wp.py` 補回 Opus 欄（否則 27 個 Opus 檔會消失）。"""
import glob, os, json, collections
from inspect_ai.log import read_eval_log

def no_generation(s):
    """gateway 504 / 連線中斷導致該樣本 0 次生成（無任何 assistant 訊息）＝無效樣本。
    沒量到東西，不是模型答錯；一律從分母剔除，不做選擇性重跑。"""
    return not any(getattr(m, "role", "") == "assistant" for m in (s.messages or []))

def gateway_error(s):
    """從 model event 撈出真正的 gateway 錯誤（504 / Connection error）供標記顯示。"""
    for e in (s.events or []):
        if getattr(e, "event", "") == "model" and getattr(e, "error", None):
            t = " ".join(str(e.error).split())
            if "504" in t: return "504 Gateway Time-out（gateway 逾時掐斷）"
            return t[:120]
    return ""


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

# 收集 per (tid, model, epoch) 取「最佳」樣本：非錯誤優先；重跑(後出現)覆蓋舊錯誤。
# writeup 語料保留全部 27×6×5=810 格，錯誤格標記而非略過（與統計聚合器不同，統計才排除錯誤）。
picked={}   # (tid, model, epoch) -> (is_error:bool, solved:bool, markdown:str)
for ld in LOGDIRS:
    for f in sorted(glob.glob(os.path.join(INSPECT_ROOT, ld, "*.eval"))):  # sorted→新覆蓋舊
        try: l=read_eval_log(f)
        except Exception: continue
        mfull=(l.eval.model or "").split("/")[-1]
        if mfull not in SH: continue
        m=SH[mfull]
        for s in (l.samples or []):
            tid=ALIAS.get(str(s.id).split(" (")[0], str(s.id).split(" (")[0])
            if tid not in CLEAR: continue
            ep=getattr(s,"epoch",1); key=(tid,m,ep)
            iserr=bool(getattr(s,"error",None))
            prev=picked.get(key)
            if prev is not None and prev[0] is False and iserr:  # 已有有效的，別讓錯誤覆蓋
                continue
            sc=next(iter((s.scores or {}).values()),None)
            solved=bool(sc and str(sc.value).upper() in ("C","CORRECT","1"))
            tgt=(s.target if isinstance(s.target,str) else (s.target[0] if s.target else "")) or ""
            nogen=(not iserr) and no_generation(s)
            if iserr or nogen:
                if nogen:
                    short=gateway_error(s) or "（無 model event 錯誤紀錄）"
                    md=(f"### 第 {ep} 次 (EPOCH {ep}) — ⚠ 無效樣本：0 次生成，**不計入分母**\n\n"
                        f"> gateway 回錯／連線中斷，重試耗盡後撞 time-limit，模型一則回覆都沒產出。\n"
                        f"> **這不是模型答錯，是沒量到東西**；依「不做選擇性重跑」原則剔除而非補跑。\n>\n"
                        f"> 錯誤：`{short}`")
                else:
                    short=str(getattr(s,"error","")).replace("\n"," ")[:140]
                    md=(f"### 第 {ep} 次 (EPOCH {ep}) — ⚠ 此 epoch 因 harness/生成錯誤未產生解題內容\n\n"
                        f"> 錯誤：`{short}`")
                iserr=True                      # 一併排除於「有效 epoch」分母
            else:
                md=render_epoch(s,ep,solved,tgt)
            picked[key]=(iserr,solved,md)

if os.path.isdir(OUT): __import__("shutil").rmtree(OUT)
os.makedirs(OUT)
MODELS6=["550b","26b","12b","30b","70b","8b"]
EPOCHS=[1,2,3,4,5]
n_files=0; n_sections=0; idx=[]
for tid,(arm,clear) in CLEAR.items():
    d=os.path.join(OUT, clear); os.makedirs(d, exist_ok=True)
    per_model_solved={}
    for m in MODELS6:
        parts=[]; nsolv=0; nvalid=0
        for ep in EPOCHS:                          # ★ 保證每 (題×模型) 都有 5 段 → 27×6×5=810
            k=(tid,m,ep)
            if k in picked:
                iserr,solved,md=picked[k]
                if not iserr: nvalid+=1
                if solved: nsolv+=1
            else:
                md=f"### 第 {ep} 次 (EPOCH {ep}) — （log 無此 epoch 紀錄）"
            parts.append(md); n_sections+=1
        per_model_solved[m]=(nsolv,nvalid)
        head=(f"# {clear} — {m} 實際解題 wp\n\n"
              f"題目：{arm} / `{tid}`　·　此模型 {nsolv}/{nvalid} 有效 epoch 解出（共 5 次嘗試）　·　"
              f"標準解答見 `../../wp_27/{clear}.md`\n\n"
              f"> 內容＝模型自己的推理＋下的指令＋工具輸出（過長截斷）＋提交；錯誤格已標記。\n\n---\n\n")
        open(os.path.join(d, f"{m}.md"),"w",encoding="utf-8").write(head+"\n\n---\n\n".join(parts))
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

print(f"寫出 {n_files} 檔 × 5 epoch = {n_sections} 個 writeup 段（目標 27×6×5=810）→ {OUT}/  + INDEX.md")
