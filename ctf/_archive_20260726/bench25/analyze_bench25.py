#!/usr/bin/env python3
"""Bench25 結果分析：合併 cybench + intercode 兩段 log，輸出跨模型 × 領域 × 難度矩陣。

用法：cd /path/to/ais3-llm-seceval && python ctf/bench25/analyze_bench25.py
"""
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

# 用系統 python3 直接跑會找不到 inspect_ai（它裝在 .venv）。
# 自動改用 venv 的直譯器重新執行，省得每次都要先 activate。
try:
    from inspect_ai.log import list_eval_logs, read_eval_log
except ModuleNotFoundError:
    _venv_py = Path(__file__).resolve().parents[2] / ".venv" / "bin" / "python"
    if _venv_py.exists() and not os.environ.get("_BENCH25_REEXEC"):
        os.environ["_BENCH25_REEXEC"] = "1"
        os.execv(str(_venv_py), [str(_venv_py), *sys.argv])
    sys.exit(f"找不到 inspect_ai，且無法自動切換到 venv。請執行：\n"
             f"  {_venv_py} {Path(__file__).name}")

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "bench25"
MANIFEST = json.loads((Path(__file__).parent / "manifest.json").read_text())

MODELS = [
    "llama-3.1-8b", "gemma-4-12b", "gemma-4-26b",
    "nemotron-cascade-2-30b", "llama-3.3-70b", "nemotron-3-ultra-550b",
]
CATS = ["crypto", "rev", "forensics", "misc", "web", "pwn"]
DIFFS = ["easy", "medium", "hard"]

# manifest 的短名 -> (category, difficulty)
META = {}
for it in MANIFEST:
    src, short = it["id"].split("/", 1)
    META[(src, short)] = (it["category"], it["difficulty"], it["id"])


def wilson(k, n, z=1.96):
    """Wilson 95% CI，小樣本比 normal approx 可靠。"""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def load_logs():
    """只取正式跑批的 log；底線目錄（_aborted/_scratch）是中止或不同組態的批次。"""
    all_logs = list(list_eval_logs(str(LOG_DIR)))
    logs = [l for l in all_logs
            if not any(p.startswith("_") for p in Path(str(l.name)).parts)]
    return logs, len(all_logs) - len(logs)


def collect(logs):
    """擷取結果。回傳 (results, errors, steps, limits, thru)。

    results[model][(src,short)] = [0/1, ...]
    errors[model]  = [(題目 id, 原因)]
    steps[model]   = {題目 id: 訊息數}
    limits[model]  = {題目 id: 撞到的 limit 型別}   ← 用來區分「能力不足」與「預算耗盡」
    thru[model]    = {題目 id: (輸出 tok/s, working 秒數)}

    為什麼要記 tok/s：2026-07-25 實測到同一模型同一題（8b / intercode 3）兩次跑，
    訊息數同為 50、結論同為未解出，但 working_time 差 56 倍（9.9s vs 552.5s），
    輸出吞吐差 93 倍（140.4 vs 1.5 tok/s）。gateway 回應變慢的時間是花在 API call
    內部，會被 Inspect 全額計入 working_time（ratio 仍為 1.00），所以
    「看 working_time 而非 total_time」這條舊規則抓不到它——那條只抓得到重試退避。
    唯一穩的偵測量是輸出吞吐。
    """
    results = defaultdict(lambda: defaultdict(list))
    errors = defaultdict(list)
    steps = defaultdict(dict)
    limits = defaultdict(dict)
    thru = defaultdict(dict)

    for ref in logs:
        log = read_eval_log(ref)
        if log.status not in ("success", "error"):
            continue
        m = model_of(log)
        for s in (log.samples or []):
            key = sample_key(log, s)
            if key not in META:
                continue
            tid = META[key][2]
            if s.error is not None:
                errors[m].append((tid, str(s.error).split("\n")[0][:120]))
                continue
            val = 0
            if s.scores:
                sc = next(iter(s.scores.values()))
                v = sc.value
                val = 1 if (v == 1 or v == "C" or v is True) else 0
            results[m][key].append(val)
            steps[m][tid] = len(s.messages or [])
            lim = getattr(s, "limit", None)
            if lim is not None:
                limits[m][tid] = getattr(lim, "type", str(lim))
            w = getattr(s, "working_time", None) or 0
            out = sum(u.output_tokens for u in (s.model_usage or {}).values())
            if w > 0:
                thru[m][tid] = (out / w, w)
    return results, errors, steps, limits, thru


def throughput_report(thru, limits):
    """找出被 gateway 吞吐拖累的樣本，並區分它有沒有真的污染分數。

    分三類（判讀方式完全不同，不可混為一談）：
      A. 撞【時間】上限 + 低吞吐 → harness confound。--time-limit 是牆鐘，
         題目是因為 gateway 當下慢而被砍掉，不是模型能力不足。必須排除。
      B. 撞【時間】上限 + 吞吐正常 → 真的是預算耗盡（合法的預算訊號，非能力訊號）。
      C. 低吞吐但沒撞限 → 只影響牆鐘，不影響分數。純資訊。
    撞【訊息】上限不列入：--message-limit 是吞吐不變量，慢或快都走滿 50 則，
    結論不受影響（8b / intercode 3 兩次跑已實證：93 倍吞吐差、同樣 50 則、同樣未解出）。
    """
    out = {"confound": [], "budget": [], "slow_only": []}
    for m, d in thru.items():
        rates = sorted(r for r, _ in d.values())
        if not rates:
            continue
        med = rates[len(rates) // 2]
        floor = med * 0.25          # 低於該模型中位吞吐的 1/4 視為異常
        for tid, (r, w) in sorted(d.items()):
            lim = limits.get(m, {}).get(tid)
            slow = r < floor
            if lim == "time" and slow:
                out["confound"].append((m, tid, r, med, w))
            elif lim == "time":
                out["budget"].append((m, tid, r, med, w))
            elif slow:
                out["slow_only"].append((m, tid, r, med, w))
    return out


def model_of(log):
    m = log.eval.model or ""
    return m.rsplit("/", 1)[-1]


def sample_key(log, sample):
    """回傳 (source, short_name)，對應 manifest。"""
    task = log.eval.task or ""
    if "intercode" in task:
        return ("intercode", str(sample.id))
    # cybench：sample.id 形如 "<eval_name> (hard)" 或 metadata 帶 eval_name
    meta = sample.metadata or {}
    name = meta.get("eval_name") or meta.get("challenge_name")
    if not name:
        name = str(sample.id).split(" (")[0].strip()
    return ("cybench", name)


def main():
    # list_eval_logs 會遞迴掃子目錄。底線開頭的目錄（_aborted/_scratch）放的是
    # 中止或不同組態的跑批，混進來會讓同一模型的樣本數暴增、結果失真，必須排除。
    logs, skipped = load_logs()
    if skipped:
        print(f"（已排除 {skipped} 個位於底線目錄的 log：中止批次／不同組態）\n")
    if not logs:
        print(f"找不到 log：{LOG_DIR}")
        return

    results, errors, steps, limits, thru = collect(logs)

    # ---------- 總表 ----------
    print("=" * 78)
    print("Bench25 結果：6 模型 × 25 題")
    print("=" * 78)
    print(f"\n{'模型':<26} {'解出':>7} {'accuracy':>9} {'95% CI':>16} {'error':>6}")
    print("-" * 78)
    overall = {}
    for m in MODELS:
        if m not in results:
            print(f"{m:<26} {'--- 尚未完成 ---':>30}")
            continue
        k = sum(sum(v) for v in results[m].values())
        n = sum(len(v) for v in results[m].values())
        lo, hi = wilson(k, n)
        overall[m] = (k, n, k / n if n else 0)
        print(f"{m:<26} {k:>3}/{n:<3} {k/n if n else 0:>9.3f} "
              f"{f'[{lo:.2f}, {hi:.2f}]':>16} {len(errors[m]):>6}")

    # ---------- 領域矩陣 ----------
    print(f"\n{'=' * 78}\n領域 × 模型 accuracy\n{'=' * 78}")
    hdr = f"{'領域':<12}" + "".join(f"{m.split('-')[0][:6]+m.split('-')[-1]:>11}" for m in MODELS)
    print(hdr)
    print("-" * 78)
    for c in CATS:
        row = f"{c:<12}"
        for m in MODELS:
            if m not in results:
                row += f"{'--':>11}"
                continue
            ks = [(sum(v), len(v)) for kk, v in results[m].items() if META[kk][0] == c]
            k = sum(a for a, _ in ks); n = sum(b for _, b in ks)
            row += f"{f'{k}/{n}':>11}" if n else f"{'-':>11}"
        print(row)

    # ---------- 難度矩陣 ----------
    print(f"\n{'=' * 78}\n難度 × 模型 accuracy\n{'=' * 78}")
    print(hdr)
    print("-" * 78)
    for d in DIFFS:
        row = f"{d:<12}"
        for m in MODELS:
            if m not in results:
                row += f"{'--':>11}"
                continue
            ks = [(sum(v), len(v)) for kk, v in results[m].items() if META[kk][1] == d]
            k = sum(a for a, _ in ks); n = sum(b for _, b in ks)
            row += f"{f'{k}/{n}':>11}" if n else f"{'-':>11}"
        print(row)

    # ---------- 逐題 ----------
    print(f"\n{'=' * 78}\n逐題命中（. = 未解, X = 解出, ! = error）\n{'=' * 78}")
    print(f"{'題目':<38}" + "".join(f"{m.split('-')[-1]:>7}" for m in MODELS))
    print("-" * 78)
    for it in MANIFEST:
        src, short = it["id"].split("/", 1)
        key = (src, short)
        row = f"{it['id']:<30}{it['category'][:4]:<4}{it['difficulty'][:4]:<4}"
        for m in MODELS:
            if m not in results or key not in results[m]:
                errd = dict(errors[m]) if m in errors else {}
                row += f"{'!' if it['id'] in errd else '?':>7}"
            else:
                v = results[m][key]
                row += f"{('X' if sum(v) else '.'):>7}"
        print(row)

    # ---------- 直覺強度 II ----------
    print(f"\n{'=' * 78}\n直覺強度 II = 100 / 解題中位訊息數（只算解出的題）\n{'=' * 78}")
    for m in MODELS:
        if m not in results:
            continue
        solved = [steps[m][META[kk][2]] for kk, v in results[m].items()
                  if sum(v) and META[kk][2] in steps[m]]
        if not solved:
            print(f"{m:<26} 無解出題，II 未定義")
            continue
        solved.sort()
        med = solved[len(solved) // 2]
        print(f"{m:<26} 解出 {len(solved):>2} 題  中位訊息數 {med:>3}  II = {100/med:>5.1f}")

    # ---------- gateway 吞吐 ----------
    print(f"\n{'=' * 78}\ngateway 吞吐（輸出 tok/s，各模型中位數）\n{'=' * 78}")
    for m in MODELS:
        if m not in thru or not thru[m]:
            continue
        rates = sorted(r for r, _ in thru[m].values())
        med = rates[len(rates) // 2]
        print(f"{m:<26} 中位 {med:>6.1f} tok/s   最慢 {rates[0]:>6.1f}   最快 {rates[-1]:>6.1f}"
              f"   （n={len(rates)}）")

    tr = throughput_report(thru, limits)
    if tr["confound"]:
        print(f"\n【A】撞時間上限 + 吞吐異常低 → harness confound，不可當能力訊號：")
        for m, tid, r, med, w in tr["confound"]:
            print(f"  {m:<26} {tid:<34} {r:>6.1f} tok/s (該模型中位 {med:.1f}) work={w:.0f}s")
    else:
        print(f"\n【A】撞時間上限 + 吞吐異常低：無。")
    if tr["budget"]:
        print(f"\n【B】撞時間上限但吞吐正常 → 真的是預算耗盡（非能力訊號）：")
        for m, tid, r, med, w in tr["budget"]:
            print(f"  {m:<26} {tid:<34} {r:>6.1f} tok/s work={w:.0f}s")
    if tr["slow_only"]:
        print(f"\n【C】吞吐低但未撞限 → 只拖慢牆鐘，分數不受影響：")
        for m, tid, r, med, w in tr["slow_only"]:
            print(f"  {m:<26} {tid:<34} {r:>6.1f} tok/s (中位 {med:.1f}) work={w:.0f}s")

    # ---------- 錯誤 ----------
    if any(errors.values()):
        print(f"\n{'=' * 78}\nError（harness 問題，非能力）\n{'=' * 78}")
        for m in MODELS:
            for tid, reason in errors.get(m, []):
                print(f"  {m:<26} {tid:<34} {reason}")


def _progress_header():
    """跑批進度：完成的 (模型, 階段) 組合數，以及 runner 是否還活著。"""
    import subprocess
    done = alive = 0
    try:
        logs = [l for l in list_eval_logs(str(LOG_DIR))
                if not any(p.startswith("_") for p in Path(str(l.name)).parts)]
        for ref in logs:
            if read_eval_log(ref, header_only=True).status == "success":
                done += 1
    except Exception:
        pass
    try:
        alive = subprocess.run(["pgrep", "-f", "run_bench25.sh"],
                               capture_output=True).returncode == 0
    except Exception:
        alive = False
    state = "跑批進行中" if alive else "跑批已結束或未啟動"
    return f"進度：{done}/12 個 (模型 × 階段) 完成　|　{state}"


def _render():
    """把報告輸出成字串。"""
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    return buf.getvalue()


if __name__ == "__main__":
    import argparse
    import time
    from datetime import datetime

    ap = argparse.ArgumentParser(description="Bench25 結果分析")
    ap.add_argument("--out", metavar="FILE",
                    help="同時寫入檔案（markdown，含程式碼區塊）")
    ap.add_argument("--watch", type=int, metavar="SEC", default=0,
                    help="每 SEC 秒重新分析一次；跑批結束後再跑一輪就停")
    args = ap.parse_args()

    def once():
        stamp = datetime.now().strftime("%F %T")
        head = _progress_header()
        body = _render()
        if args.out:
            Path(args.out).write_text(
                f"# Bench25 即時結果\n\n"
                f"最後更新：{stamp}　|　{head}\n\n"
                f"> 本檔由 `analyze_bench25.py --watch` 自動覆寫，請勿手動編輯。\n\n"
                f"```\n{body}\n```\n"
            )
        return head, stamp, body

    if not args.watch:
        head, stamp, body = once()
        print(f"{head}\n")
        print(body)
        if args.out:
            print(f"已寫入 {args.out}")
    else:
        import subprocess
        while True:
            head, stamp, _ = once()
            print(f"[{stamp}] {head}" + (f" → {args.out}" if args.out else ""),
                  flush=True)
            running = subprocess.run(["pgrep", "-f", "run_bench25.sh"],
                                     capture_output=True).returncode == 0
            if not running:
                print("跑批已結束，最後一次分析完成，watcher 退出。", flush=True)
                break
            time.sleep(args.watch)
