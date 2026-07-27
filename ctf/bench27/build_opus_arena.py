#!/usr/bin/env python3
"""替 Opus 5-epoch 盲解準備乾淨場地：把每題的『真題檔』(排除 solution/writeup/checkpoints)
搬進 opus_arena/<clear>/challenge/，並記錄 gold flag / 是否需 Docker / prompt → opus_tasks.json。
真題來源＝6 受測模型跑批用的同一份上游檔（picoCTF 快取 + cybench challenges），確保可比。"""
import os, json, shutil, glob, re
ROOT = os.path.dirname(os.path.abspath(__file__))
INSPECT = os.path.abspath(os.path.join(ROOT, "../.."))
ARENA = os.path.join(ROOT, "opus_arena")
PICO = os.path.expanduser("~/Library/Caches/inspect_evals/gdm_intercode_ctf/data/task_assets")
CYB = glob.glob(os.path.join(INSPECT, ".venv/lib/*/site-packages/inspect_evals/cybench/challenges"))[0]
# 題目敘述來源（含 pico 的密文 query）＝與 6 受測模型跑批同一份
ICCTF = {str(t["task_id"]): t for t in json.load(open(
    os.path.expanduser("~/Library/Caches/inspect_evals/gdm_intercode_ctf/data/ic_ctf.json"), encoding="utf-8"))}
def cyb_hard_prompt(name):
    """從 cybench eval.yaml 抓 hard variant 的 prompt（受測模型跑的就是 hard）。"""
    p = os.path.join(CYB, name, "eval.yaml")
    if not os.path.exists(p): return None
    txt = open(p, encoding="utf-8").read()
    m = re.search(r"^  hard:\n    prompt: \|\n((?:      .*\n?)+)", txt, re.M)   # 區塊式 prompt: |
    if m: return re.sub(r"^      ", "", m.group(1), flags=re.M).strip()
    m = re.search(r"^  hard:\n    prompt: (?!\|)(.+)$", txt, re.M)               # 單行式 prompt: <text>
    return m.group(1).strip() if m else None

# (clear, arm, tid, kind, src_ref, bench_dir)  kind: pico=<id> / cyb=<name> / recent=<dir>
# bench_dir：含 gold flag 的 checkpoints.json 所在（contaminated/deep 用；recent 用 challenge.json）
TASKS = [
 ("C01_crypto_ROT13","contaminated","5","pico","5","contaminated/crypto_picoctf5"),
 ("C02_crypto_sequential-LCG","contaminated","slcg","cyb","slcg","contaminated/crypto_slcg"),
 ("C03_crypto_RSA-missing-bits","contaminated","missingbits","cyb","missingbits","contaminated/crypto_missingbits"),
 ("C04_rev_VaultDoor-char-mapping","contaminated","44","pico","44","contaminated/rev_picoctf44"),
 ("C05_rev_keygenme-sha256","contaminated","13","pico","13","contaminated/rev_picoctf13"),
 ("C06_forensics_strings-in-image","contaminated","94","pico","94","contaminated/forensics_picoctf94"),
 ("C07_forensics_EXIF-metadata","contaminated","8","pico","8","contaminated/forensics_picoctf8"),
 ("C08_misc_hidden-file-unzip","contaminated","37","pico","37","contaminated/misc_picoctf37"),
 ("C09_misc_zip-password-brute","contaminated","34","pico","34","contaminated/misc_picoctf34"),
 ("C10_web_git-repo-leak","contaminated","back_to_the_past","cyb","back_to_the_past","contaminated/web_back_to_the_past"),
 ("C11_web_float-balance-overflow","contaminated","glacier_exchange","cyb","glacier_exchange","contaminated/web_glacier_exchange"),
 ("C12_pwn_ROP-chain","contaminated","network_tools","cyb","network_tools","contaminated/pwn_network_tools"),
 ("R01_crypto_digit-6-7-prime-factoring","recent2026","crypto_six-seven","recent","crypto_six-seven",None),
 ("R02_crypto_coppersmith-partial-key","recent2026","crypto_six-seven-again","recent","crypto_six-seven-again",None),
 ("R03_rev_unicode-homoglyph-flag","recent2026","rev_ooo","recent","rev_ooo",None),
 ("R04_rev_nonogram-regex-z3","recent2026","rev_flag-finder","recent","rev_flag-finder",None),
 ("R05_forensics_pcap-http-cookie","recent2026","forensics_cake","recent","forensics_cake",None),
 ("R06_forensics_pcap-icmp-covert","recent2026","forensics_stillthere","recent","forensics_stillthere",None),
 ("R07_misc_utf16-endianness","recent2026","misc_endians","recent","misc_endians",None),
 ("R08_misc_QR-reed-solomon-rebuild","recent2026","misc_error-correction","recent","misc_error-correction",None),
 ("R09_web_go-parser-differential","recent2026","web_glotq","recent","web_glotq",None),
 ("R10_web_AES-GCM-short-tag","recent2026","web_single-trust","recent","web_single-trust",None),
 ("R11_pwn_OOB-global-write","recent2026","pwn_tic-tac-no","recent","pwn_tic-tac-no",None),
 ("R12_pwn_shellcode-PRNG","recent2026","pwn_scrabasm","recent","pwn_scrabasm",None),
 ("D01_crypto_permutation-group-DLP","deep_hard","permuted","cyb","permuted","deep_hard/permuted"),
 ("D02_pwn_format-string-overwrite","deep_hard","delulu","cyb","delulu","deep_hard/delulu"),
 ("D03_misc_pickle-jail-escape","deep_hard","just_another_pickle_jail","cyb","just_another_pickle_jail","deep_hard/just_another_pickle_jail"),
]
EXCLUDE = {"solution","writeup.md","checkpoints.json","README.md",".DS_Store","eval.yaml","flag","flag.txt"}

def copy_filtered(src, dst):
    os.makedirs(dst, exist_ok=True)
    for item in os.listdir(src):
        if item in EXCLUDE: continue
        s=os.path.join(src,item); d=os.path.join(dst,item)
        if os.path.isdir(s): copy_filtered(s,d)
        else:
            try: shutil.copy2(s,d)
            except Exception: pass

if os.path.isdir(ARENA): shutil.rmtree(ARENA)
os.makedirs(ARENA)
manifest=[]
for clear, arm, tid, kind, ref, bench_dir in TASKS:
    wd=os.path.join(ARENA, clear); chdir=os.path.join(wd,"challenge"); os.makedirs(chdir, exist_ok=True)
    gold=prompt=compose=None
    if kind=="pico":
        copy_filtered(os.path.join(PICO, ref), chdir)
        prompt = (ICCTF.get(ref) or {}).get("query")   # ★ 含密文的題目敘述
    elif kind=="cyb":
        base=os.path.join(CYB, ref)
        # cybench 真題檔在 resources/（可下載檔）；pwn/web 的 victim 二進位/原始碼在 images/*/（排除 flag）
        for sub in ("resources","challenge"):
            p=os.path.join(base, sub)
            if os.path.isdir(p): copy_filtered(p, chdir)
        for img in glob.glob(os.path.join(base, "images", "*")):
            if os.path.isdir(img): copy_filtered(img, os.path.join(chdir, "server_"+os.path.basename(img)))
        comp=os.path.join(base, "compose.yaml")
        if os.path.exists(comp): compose=comp
        prompt = cyb_hard_prompt(ref)                  # ★ hard variant 敘述（受測模型同款）
    if kind in ("pico","cyb"):
        cp=json.load(open(os.path.join(ROOT, bench_dir, "checkpoints.json"),encoding="utf-8"))
        gold=cp.get("flag")
    if kind=="recent":
        rdir=os.path.join(ROOT,"recent2026",ref)
        meta=json.load(open(os.path.join(rdir,"challenge.json"),encoding="utf-8"))
        gold=meta["flag"]; prompt=meta.get("prompt")
        for dst,relsrc in (meta.get("files") or {}).items():
            s=os.path.join(rdir, relsrc)
            if os.path.exists(s):
                d=os.path.join(chdir, os.path.basename(dst)); shutil.copy2(s,d)
        if meta.get("compose"): compose=os.path.join(rdir, meta["compose"])
    nfiles=sum(len(f) for _,_,f in os.walk(chdir))
    manifest.append({"clear":clear,"arm":arm,"tid":tid,"needs_docker":bool(compose),
                     "compose":os.path.relpath(compose,INSPECT) if compose else None,
                     "gold_flag":gold,"prompt":prompt,
                     "challenge_dir":os.path.relpath(chdir, INSPECT),"n_files":nfiles})

json.dump(manifest, open(os.path.join(ROOT,"opus_tasks.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"場地就緒 {len(manifest)} 題 → opus_arena/")
print(f"  需 Docker: {sum(m['needs_docker'] for m in manifest)} 題")
print(f"  缺 gold flag: {[m['clear'] for m in manifest if not m['gold_flag']] or '無 ✓'}")
print(f"  challenge/ 空的: {[m['clear'] for m in manifest if m['n_files']==0] or '無 ✓'}")
for m in manifest: print(f"    {m['clear']:38} files={m['n_files']:2} docker={'Y' if m['needs_docker'] else '·'} flag={'✓' if m['gold_flag'] else '✗'}")
