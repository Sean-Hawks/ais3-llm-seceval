#!/usr/bin/env python3
"""整理 24 題（污染12＋近代12）writeup → wp_24/，命名清晰易懂 + INDEX.md。
每題另附 checkpoints / Opus 手解，放進 _checkpoints/ 與 _frontier_opus/（同一清楚檔名）。"""
import os, json, shutil, collections
from inspect_ai.log import read_eval_log  # noqa (只為確保 venv)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, "wp_24")

# (source_dir, arm, tid, clear_filename, category, difficulty, official, source, technique)
MAP = [
 # ---- 污染 12（2022–23，有公開 writeup）----
 ("contaminated/crypto_picoctf5","contaminated","5","C01_crypto_ROT13","crypto","easy","ROT13","picoCTF","ROT13 位移密碼直接還原"),
 ("contaminated/crypto_slcg","contaminated","slcg","C02_crypto_sequential-LCG","crypto","medium","Sequential LCG","GlacierCTF 2023","序列 LCG 參數回推、還原亂數流"),
 ("contaminated/crypto_missingbits","contaminated","missingbits","C03_crypto_RSA-missing-bits","crypto","medium","Missing Bits","GlacierCTF 2023","RSA 私鑰缺位元、由已知位元重建 d"),
 ("contaminated/rev_picoctf44","contaminated","44","C04_rev_VaultDoor-char-mapping","rev","easy","VaultDoor Training","picoCTF","逐字元映射反推 flag"),
 ("contaminated/rev_picoctf13","contaminated","13","C05_rev_keygenme-sha256","rev","medium","keygenme","picoCTF","key＝sha256(名字) 取特定 index"),
 ("contaminated/forensics_picoctf94","contaminated","94","C06_forensics_strings-in-image","forensics","easy","Glory of the Garden","picoCTF","strings 掃圖檔尾找 flag"),
 ("contaminated/forensics_picoctf8","contaminated","8","C07_forensics_EXIF-metadata","forensics","medium","Modified Metadata","picoCTF","EXIF 中繼資料藏 flag"),
 ("contaminated/misc_picoctf37","contaminated","37","C08_misc_hidden-file-unzip","misc","easy","find the hidden file","picoCTF","層層解壓找隱藏檔"),
 ("contaminated/misc_picoctf34","contaminated","34","C09_misc_zip-password-brute","misc","medium","hash sling (level5)","picoCTF","字典/爆破 zip 密碼"),
 ("contaminated/web_back_to_the_past","contaminated","back_to_the_past","C10_web_git-repo-leak","web","medium","Back to the Past","HKCert 2022",".git 目錄外洩、還原原始碼"),
 ("contaminated/web_glacier_exchange","contaminated","glacier_exchange","C11_web_float-balance-overflow","web","medium","Glacier Exchange","GlacierCTF 2023","浮點精度誤差刷爆餘額"),
 ("contaminated/pwn_network_tools","contaminated","network_tools","C12_pwn_ROP-chain","pwn","hard","Network Tools","SekaiCTF 2023","ROP chain 串接 gadget getshell"),
 # ---- 近代 12（2026，post-cutoff）----
 ("recent2026/crypto_six-seven","recent2026","crypto_six-seven","R01_crypto_digit-6-7-prime-factoring","crypto","medium","six-seven","LACTF 2026","質數僅由數字6/7組成、可分解 n"),
 ("recent2026/crypto_six-seven-again","recent2026","crypto_six-seven-again","R02_crypto_coppersmith-partial-key","crypto","medium","six-seven-again","LACTF 2026","Coppersmith small_roots 補回高位"),
 ("recent2026/rev_ooo","recent2026","rev_ooo","R03_rev_unicode-homoglyph-flag","rev","easy","ooo","LACTF 2026","Unicode 同形字組成的 flag"),
 ("recent2026/rev_flag-finder","recent2026","rev_flag-finder","R04_rev_nonogram-regex-z3","rev","medium","flag-finder","LACTF 2026","nonogram/regex 約束、z3 求唯一解"),
 ("recent2026/forensics_cake","recent2026","forensics_cake","R05_forensics_pcap-http-cookie","forensics","easy","There will be cake","BYUCTF 2026","pcap 裡 HTTP cookie base64 解碼"),
 ("recent2026/forensics_stillthere","recent2026","forensics_stillthere","R06_forensics_pcap-icmp-covert","forensics","medium","Are You Still There?","BYUCTF 2026","pcap ICMP 隱蔽通道重組"),
 ("recent2026/misc_endians","recent2026","misc_endians","R07_misc_utf16-endianness","misc","easy","endians","LACTF 2026","UTF-16 端序轉換取 flag"),
 ("recent2026/misc_error-correction","recent2026","misc_error-correction","R08_misc_QR-reed-solomon-rebuild","misc","medium","error-correction","LACTF 2026","QR/Reed-Solomon 重建＋frame 指派"),
 ("recent2026/web_glotq","recent2026","web_glotq","R09_web_go-parser-differential","web","medium","glotq","LACTF 2026","Go parser 差異攻擊"),
 ("recent2026/web_single-trust","recent2026","web_single-trust","R10_web_AES-GCM-short-tag","web","medium","single-trust","LACTF 2026","AES-GCM 短 tag 爆破＋CTR 可鍛性"),
 ("recent2026/pwn_tic-tac-no","recent2026","pwn_tic-tac-no","R11_pwn_OOB-global-write","pwn","easy","tic-tac-no","LACTF 2026","越界寫全域變數改勝負"),
 ("recent2026/pwn_scrabasm","recent2026","pwn_scrabasm","R12_pwn_shellcode-PRNG","pwn","medium","ScrabASM","LACTF 2026","組 shellcode＋預測 PRNG"),
]
# frontier_manual basename
FM = {"5":"crypto_picoctf5","slcg":"crypto_slcg","missingbits":"crypto_missingbits","44":"rev_picoctf44",
 "13":"rev_picoctf13","94":"forensics_picoctf94","8":"forensics_picoctf8","37":"misc_picoctf37",
 "34":"misc_picoctf34","back_to_the_past":"web_back_to_the_past","glacier_exchange":"web_glacier_exchange",
 "network_tools":"pwn_network_tools","crypto_six-seven":"crypto_six-seven","crypto_six-seven-again":"crypto_six-seven-again",
 "rev_ooo":"rev_ooo","rev_flag-finder":"rev_flag-finder","forensics_cake":"forensics_cake",
 "forensics_stillthere":"forensics_stillthere","misc_endians":"misc_endians","misc_error-correction":"misc_error-correction",
 "web_glotq":"web_glotq","web_single-trust":"web_single-trust","pwn_tic-tac-no":"pwn_tic-tac-no","pwn_scrabasm":"pwn_scrabasm"}

# 解出模型數（pass@any /6）從 bench27_runs.json
solved = collections.defaultdict(set)
runs_p = os.path.join(ROOT, "bench27_runs.json")
if os.path.exists(runs_p):
    for r in json.load(open(runs_p, encoding="utf-8")):
        if r["solved"]: solved[(r["arm"], r["task"])].add(r["model"])
MODELS6 = ["550b","26b","12b","30b","70b","8b"]

if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT); os.makedirs(os.path.join(OUT,"_checkpoints")); os.makedirs(os.path.join(OUT,"_frontier_opus"))

rows_idx=[]
for src, arm, tid, clear, cat, diff, official, source, tech in MAP:
    d = os.path.join(ROOT, src)
    shutil.copy(os.path.join(d,"writeup.md"), os.path.join(OUT, clear+".md"))
    cpf = os.path.join(d,"checkpoints.json")
    if os.path.exists(cpf): shutil.copy(cpf, os.path.join(OUT,"_checkpoints", clear+".checkpoints.json"))
    fm = os.path.join(ROOT,"frontier_manual", FM[tid]+".md")
    if os.path.exists(fm): shutil.copy(fm, os.path.join(OUT,"_frontier_opus", clear+".frontier_opus.md"))
    got = solved.get((arm,tid), set())
    who = "".join("✓" if m in got else "·" for m in MODELS6)
    rows_idx.append((clear, arm, cat, diff, official, source, tech, len(got), who))

# INDEX.md
with open(os.path.join(OUT,"INDEX.md"),"w",encoding="utf-8") as f:
    f.write("# Bench27 — 24 題 Writeup 索引（污染12 ＋ 近代12）\n\n")
    f.write("命名：`<C=污染|R=近代><編號>_<類別>_<技巧>.md`。解出欄＝6 受測模型 pass@any（")
    f.write("順序 550b·26b·12b·30b·70b·8b，✓=解出 ·=沒解出）。\n\n")
    f.write("每題另附 `_checkpoints/<同名>.checkpoints.json`（階段錨點）與 `_frontier_opus/<同名>.frontier_opus.md`（Opus 手解參考）。\n\n")
    f.write("| 檔名 | 類別 | 難度 | 原題 | 出處 | 技巧 | 解出/6 | 550·26·12·30·70·8 |\n")
    f.write("|---|---|---|---|---|---|:--:|:--:|\n")
    for clear,arm,cat,diff,official,source,tech,n,who in rows_idx:
        f.write(f"| `{clear}.md` | {cat} | {diff} | {official} | {source} | {tech} | {n} | `{who}` |\n")

print(f"寫出 {len(rows_idx)} 題 writeup → {OUT}/")
print(f"  + INDEX.md, _checkpoints/({len(os.listdir(os.path.join(OUT,'_checkpoints')))}), _frontier_opus/({len(os.listdir(os.path.join(OUT,'_frontier_opus')))})")
print("\n檔名一覽：")
for clear,*_ in rows_idx: print("  ", clear+".md")
