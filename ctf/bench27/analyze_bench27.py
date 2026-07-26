#!/usr/bin/env python3
"""Bench27 結果分析：核心是「污染組 vs 近代組」的 accuracy gap（＝污染訊號）。

三分區（arm）：contaminated（2022/2023 公開 writeup）／recent2026（真 2026 CTF，post-cutoff）／deep_hard。
每個模型的 gap = acc(contaminated) − acc(recent2026)。gap 越大＝越依賴記憶而非能力。

用法（★ 從 inspect-test/ 跑）：
  python ctf/bench27/analyze_bench27.py
log 來源：logs/bench27/（遞迴；排除底線目錄 _aborted/_scratch —— 中止或不同組態批次）。
"""
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

try:
    from inspect_ai.log import list_eval_logs, read_eval_log
except ModuleNotFoundError:
    _venv_py = Path(__file__).resolve().parents[2] / ".venv" / "bin" / "python"
    if _venv_py.exists() and not os.environ.get("_BENCH27_REEXEC"):
        os.environ["_BENCH27_REEXEC"] = "1"
        os.execv(str(_venv_py), [str(_venv_py), *sys.argv])
    sys.exit(f"找不到 inspect_ai，請用 venv：{_venv_py} {Path(__file__).name}")

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "bench27"
MANIFEST = json.loads((Path(__file__).parent / "MANIFEST.json").read_text())

MODELS = [
    "llama-3.1-8b", "gemma-4-12b", "gemma-4-26b",
    "nemotron-cascade-2-30b", "llama-3.3-70b", "nemotron-3-ultra-550b",
]
CATS = ["crypto", "rev", "forensics", "misc", "web", "pwn"]
ARMS = ["contaminated", "recent2026", "deep_hard"]

# ---- 建 (source, key) -> manifest entry 的查表 ----
# contaminated intercode: key = src_id(task_id 字串)；cybench: key = src_id(eval_name)
# recent2026: key = dir basename（= inspect sample id）
# deep_hard: cybench eval_name
META = {}
for it in MANIFEST["problems"]:
    if it.get("status") == "pending_files_from_user":
        continue
    arm = it["arm"]
    base = it["dir"].split("/")[-1]
    if arm == "recent2026":
        META[("recent2026", base)] = it
    else:  # contaminated / deep_hard 都來自 intercode 或 cybench
        src = it.get("source", "")
        sid = it.get("src_id", "")
        if src == "intercode":
            META[("intercode", str(sid))] = it
        else:
            META[("cybench", str(sid))] = it


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def load_logs():
    all_logs = list(list_eval_logs(str(LOG_DIR)))
    logs = [l for l in all_logs
            if not any(p.startswith("_") for p in Path(str(l.name)).parts)]
    return logs, len(all_logs) - len(logs)


def model_of(log):
    return (log.eval.model or "").rsplit("/", 1)[-1]


def sample_key(log, sample):
    task = log.eval.task or ""
    if "intercode" in task:
        return ("intercode", str(sample.id))
    if "recent2026" in task:
        return ("recent2026", str(sample.id))
    # cybench
    meta = sample.metadata or {}
    name = meta.get("eval_name") or meta.get("challenge_name") \
        or str(sample.id).split(" (")[0].strip()
    return ("cybench", name)


def collect(logs):
    # results[model][arm] = [0/1,...] ; bycat[model][arm][cat]=[0/1]
    results = defaultdict(lambda: defaultdict(list))
    bycat = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    errors = defaultdict(int)
    thru = defaultdict(dict)
    for ref in logs:
        log = read_eval_log(ref)
        if log.status not in ("success", "error"):
            continue
        m = model_of(log)
        for s in (log.samples or []):
            key = sample_key(log, s)
            it = META.get(key)
            if it is None:
                continue
            arm, cat = it["arm"], it["category"]
            if s.error is not None:
                errors[m] += 1
                continue
            val = 0
            if s.scores:
                v = next(iter(s.scores.values())).value
                val = 1 if (v == 1 or v == "C" or v is True) else 0
            results[m][arm].append(val)
            bycat[m][arm][cat].append(val)
            w = getattr(s, "working_time", None) or 0
            out = sum(u.output_tokens for u in (s.model_usage or {}).values())
            if w > 0:
                thru[m][str(s.id)] = (out / w, w, getattr(getattr(s, "limit", None), "type", None))
    return results, bycat, errors, thru


def acc(lst):
    return (sum(lst) / len(lst)) if lst else None


def main():
    logs, skipped = load_logs()
    if skipped:
        print(f"（排除 {skipped} 個底線目錄 log：中止/不同組態）")
    if not logs:
        print(f"尚無 log：{LOG_DIR}\n（跑 run_contaminated.sh / recent2026 / deep 之後再分析）")
        return
    results, bycat, errors, thru = collect(logs)

    print("=" * 82)
    print("Bench27 核心：污染組 vs 近代組 accuracy gap（gap 大＝依賴記憶）")
    print("=" * 82)
    print(f"\n{'模型':<24}{'污染 acc':>12}{'近代 acc':>12}{'GAP':>8}{'深題 acc':>12}{'err':>6}")
    print("-" * 82)
    for m in MODELS:
        if m not in results:
            print(f"{m:<24}{'--- 尚未完成 ---':>44}")
            continue
        cont = results[m].get("contaminated", [])
        rec = results[m].get("recent2026", [])
        deep = results[m].get("deep_hard", [])
        ac, ar, ad = acc(cont), acc(rec), acc(deep)
        gap = (ac - ar) if (ac is not None and ar is not None) else None
        def fmt(a, lst):
            if a is None:
                return f"{'—':>12}"
            lo, hi = wilson(sum(lst), len(lst))
            return f"{a:>6.2f}({len(lst):>2})"
        print(f"{m:<24}{fmt(ac,cont)}{fmt(ar,rec)}"
              f"{(f'{gap:+.2f}' if gap is not None else '—'):>8}"
              f"{fmt(ad,deep)}{errors[m]:>6}")

    print("\n※ GAP=污染−近代。正且大 → 該模型在公開題上明顯較強，指向污染/記憶效應；")
    print("  近乎 0 或負 → 兩組表現相當，較可能反映真實能力（但仍受題目難度差異干擾，需配合 checkpoint 語意命中判讀）。")

    # ---- 領域 × arm ----
    print(f"\n{'=' * 82}\n領域 × arm accuracy（各模型平均）\n{'=' * 82}")
    print(f"{'領域':<12}{'污染':>10}{'近代':>10}{'領域 gap':>10}")
    print("-" * 82)
    for c in CATS:
        cont_all, rec_all = [], []
        for m in MODELS:
            cont_all += bycat[m].get("contaminated", {}).get(c, [])
            rec_all += bycat[m].get("recent2026", {}).get(c, [])
        acc_c, acc_r = acc(cont_all), acc(rec_all)
        gap = (acc_c - acc_r) if (acc_c is not None and acc_r is not None) else None
        print(f"{c:<12}"
              f"{(f'{acc_c:.2f}' if acc_c is not None else '—'):>10}"
              f"{(f'{acc_r:.2f}' if acc_r is not None else '—'):>10}"
              f"{(f'{gap:+.2f}' if gap is not None else '—'):>10}")

    # ---- 吞吐 confound（沿用 bench25 判讀：撞時間限+低吞吐＝harness confound）----
    print(f"\n{'=' * 82}\n吞吐 confound 檢查（撞【時間】限且吞吐 < 該模型中位 1/4 ＝ 非能力訊號）\n{'=' * 82}")
    any_c = False
    for m in MODELS:
        d = thru.get(m, {})
        rates = sorted(r for r, _, _ in d.values())
        if not rates:
            continue
        med = rates[len(rates) // 2]
        for tid, (r, w, lim) in sorted(d.items()):
            if lim == "time" and r < med * 0.25:
                print(f"  ⚠ {m} / {tid}: {r:.1f} tok/s (中位 {med:.1f}), working {w:.0f}s → 排除計分")
                any_c = True
    if not any_c:
        print("  （無）")


def _watch(interval):
    import time
    while True:
        os.system("clear")
        print(f"[analyze_bench27 --watch {interval}s]  (Ctrl-C 結束)\n")
        try:
            main()
        except Exception as e:
            print("分析出錯（可能正在寫 log）：", e)
        time.sleep(interval)


if __name__ == "__main__":
    if "--watch" in sys.argv:
        i = sys.argv.index("--watch")
        sec = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else 30
        _watch(sec)
    else:
        main()
