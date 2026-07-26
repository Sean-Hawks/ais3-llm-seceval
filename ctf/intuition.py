"""AI 直覺強度 (Intuition Index)。

概念：兩個模型都解出同一題，但一個「一眼看出方法、三步解掉」，另一個「亂試二十步才矇到」——
前者直覺強。單看 accuracy 看不出這個差別，這支程式從『解題軌跡』把它量出來。

對每個「解出」的題：
  steps   = 到正確提交前的工具呼叫數（越少 = 越直接）
  flail   = 其中『出錯/無進展』的比例（command not found、traceback、錯誤提交…）
Intuition Index (II) = 100 / median(steps)  ，再看 flail 佐證。（II 越高 = 直覺越強）

用法：python ctf/intuition.py     # 讀每個模型最新的 ctf log，跨模型比較
"""
import glob
import json
import os
import re
import statistics
import zipfile

LOGDIR = os.path.join(os.path.dirname(__file__), "..", "logs")
ORDER = ["llama-3.1-8b", "gemma-4-12b", "gemma-4-26b",
         "nemotron-cascade-2-30b", "llama-3.3-70b", "nemotron-3-ultra-550b"]
SHORT = {"llama-3.1-8b": "8B", "gemma-4-12b": "12B", "gemma-4-26b": "26B",
         "nemotron-cascade-2-30b": "30B*", "llama-3.3-70b": "70B", "nemotron-3-ultra-550b": "550B"}
ERR = re.compile(r"command not found|Traceback|No such file|invalid|not found|nope|error", re.I)


def latest_per_model():
    logs = sorted(glob.glob(os.path.join(LOGDIR, "*_ctf_*.eval")), key=os.path.getmtime)
    bym = {}
    for f in logs:
        try:  # 跳過正在寫入/不完整的 log
            h = json.loads(zipfile.ZipFile(f).read("header.json"))
        except (KeyError, zipfile.BadZipFile, OSError):
            continue
        if h.get("status") == "error":
            continue
        m = h.get("eval", {}).get("model", "").split("/")[-1]
        if m in ORDER:
            bym[m] = f
    return bym


def analyze(f):
    z = zipfile.ZipFile(f)
    steps_solved, flails = [], []
    for n in z.namelist():
        if not n.startswith("samples/"):
            continue
        s = json.loads(z.read(n))
        sc = s.get("scores") or {}
        v = next(iter(sc.values()), {}).get("value")
        if v not in ("C", 1, 1.0, True):
            continue
        steps, errs = 0, 0
        for m in s.get("messages", []):
            if m.get("role") == "assistant" and (m.get("tool_calls")):
                steps += 1
            if m.get("role") == "tool":
                c = m.get("content")
                if isinstance(c, list):
                    c = " ".join(p.get("text", "") for p in c if isinstance(p, dict))
                if c and ERR.search(c):
                    errs += 1
        if steps:
            steps_solved.append(steps)
            flails.append(errs / steps)
    return steps_solved, flails


def main():
    bym = latest_per_model()
    print(f"{'model':7}{'solved':>8}{'med.steps':>11}{'flail':>8}{'II':>7}")
    print("-" * 41)
    for m in ORDER:
        if m not in bym:
            continue
        steps, flails = analyze(bym[m])
        if not steps:
            print(f"{SHORT[m]:7}{0:>8}{'-':>11}{'-':>8}{'-':>7}")
            continue
        med = statistics.median(steps)
        fl = statistics.mean(flails)
        ii = round(100 / med, 1)
        print(f"{SHORT[m]:7}{len(steps):>8}{med:>11.1f}{fl:>8.2f}{ii:>7}")
    print("\nsteps 越少、flail 越低、II 越高 = 直覺越強（一眼看出方法、少走冤枉路）。")
    print("註：II 只在『解出』的題上計算；與 accuracy 互補（會不會 vs 解得漂不漂亮）。")


if __name__ == "__main__":
    main()
