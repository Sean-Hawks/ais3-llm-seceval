"""讀最新的 ctf_pico log，把準確率按 metadata['year'] 拆解 —— 這就是污染 gap。

用法：
  python ctf/analyze_by_year.py
"""
import glob
import json
import os
import zipfile
from collections import defaultdict

LOGDIR = os.path.join(os.path.dirname(__file__), "..", "logs")


def latest_pico_log():
    logs = glob.glob(os.path.join(LOGDIR, "*_ctf-pico_*.eval"))
    if not logs:
        logs = [f for f in glob.glob(os.path.join(LOGDIR, "*_ctf_*.eval"))]
    if not logs:
        raise SystemExit("找不到 ctf_pico log，先跑：inspect eval ctf/ctf_eval.py@ctf_pico --model ...")
    return max(logs, key=os.path.getmtime)


def main():
    f = latest_pico_log()
    z = zipfile.ZipFile(f)
    by_year = defaultdict(lambda: [0, 0])  # year -> [correct, total]
    rows = []
    for n in z.namelist():
        if n.startswith("samples/"):
            s = json.loads(z.read(n))
            md = s.get("metadata") or {}
            year = md.get("year", "unspecified")
            sc = s.get("scores") or {}
            v = next(iter(sc.values()), {}).get("value")
            ok = v in ("C", 1, 1.0, True)
            by_year[year][0] += int(ok)
            by_year[year][1] += 1
            rows.append((year, md.get("category", "?"), s.get("id"), "✔" if ok else "✘"))

    print(f"log: {os.path.basename(f)}\n")
    print(f"{'year':10} {'category':10} {'challenge':24} result")
    for year, cat, cid, r in sorted(rows):
        print(f"{year:10} {cat:10} {cid:24} {r}")

    print("\n=== 按年份（污染 gap）===")
    accs = {}
    for year in sorted(by_year):
        c, t = by_year[year]
        accs[year] = c / t if t else 0
        print(f"  {year}: {c}/{t} = {accs[year]:.2f}")
    if len(accs) >= 2:
        ys = sorted(accs)
        gap = accs[ys[0]] - accs[ys[-1]]
        print(f"\n  gap({ys[0]} - {ys[-1]}) = {gap:+.2f}  ← 舊題若明顯較高，即為污染訊號")
        print("  （示範用種子題差距接近 0 屬正常；換成真 picoCTF 題才會顯現）")


if __name__ == "__main__":
    main()
