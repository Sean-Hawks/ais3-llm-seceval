#!/usr/bin/env python3
"""bench27_cost.json → 每題×每模型的 5-epoch 平均成本大表（--md 出 markdown）。"""
import json, collections, os, re, sys, statistics as st

ROOT = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(ROOT, "bench27_cost.json")))
H = open(os.path.join(ROOT, "dashboard.html")).read()
TASKS = json.loads(re.search(r"const TASKS = (\[.*?\]);", H, re.S).group(1))
MO = ["8b", "12b", "26b", "30b", "70b", "550b"]
NAME = {"8b": "llama-3.1-8b", "12b": "gemma-4-12b", "26b": "gemma-4-26b",
        "30b": "nemotron-cascade-2-30b", "70b": "llama-3.3-70b", "550b": "nemotron-3-ultra-550b"}

agg = collections.defaultdict(list)
for r in R: agg[(r["task"], r["model"])].append(r)
mean = lambda v: sum(v) / len(v) if v else 0.0
order = sorted(TASKS, key=lambda t: t["code"])
md = "--md" in sys.argv
out = []
P = out.append

def cell(c):
    return dict(n=len(c),
                inp=mean([x["input_tokens"] for x in c]), o=mean([x["output_tokens"] for x in c]),
                tot=mean([x["total_tokens"] for x in c]), wt=mean([x["working_time"] for x in c]),
                tt=mean([x["total_time"] for x in c]), msg=mean([x["assistant_msgs"] for x in c]),
                solved=sum(x["solved"] for x in c))

if md:
    P("| 代碼 | 題目 | 分區 | 難度 | " + " | ".join(NAME[m] for m in MO) + " |")
    P("|---|---|---|---|" + "---|" * len(MO))
for t in order:
    cells = {m_: agg.get((t["tid"], m_), []) for m_ in MO}
    if md:
        row = [t["code"], t["name"], t["arm"], t["diff"]]
        for m_ in MO:
            c = cells[m_]
            if not c: row.append("—"); continue
            d = cell(c)
            row.append(f"{d['tot']/1000:.1f}k / {d['o']/1000:.1f}k<br>{d['wt']:.0f}s ({d['tt']:.0f}s)<br>{d['solved']}/{d['n']}")
        P("| " + " | ".join(row) + " |")
    else:
        P(f"{t['code']:5}{t['name']:20}{t['arm']:12}{t['diff']:7}" + "".join(
            (f"{'—':>27}" if not cells[m_] else
             "  %6.1fk/%5.1fk %5.0fs(%5.0f) %d/%d" % (
                 cell(cells[m_])["tot"] / 1000, cell(cells[m_])["o"] / 1000,
                 cell(cells[m_])["wt"], cell(cells[m_])["tt"],
                 cell(cells[m_])["solved"], cell(cells[m_])["n"]))
            for m_ in MO))
print("\n".join(out))

# ── 模型層彙總 ──
print("\n【模型彙總】每樣本平均（803 有效樣本）")
print(f"{'model':24}{'n':>5}{'in tok':>9}{'out tok':>9}{'總tok':>9}{'訊息':>6}{'out/訊息':>9}"
      f"{'working':>9}{'total':>9}{'排隊稅':>8}{'解出':>7}{'tok/解':>10}")
for m_ in MO:
    rs = [r for r in R if r["model"] == m_]
    solved = sum(r["solved"] for r in rs)
    o = mean([r["output_tokens"] for r in rs]); wt = mean([r["working_time"] for r in rs])
    tt = mean([r["total_time"] for r in rs]); msg = mean([r["assistant_msgs"] for r in rs])
    tot = mean([r["total_tokens"] for r in rs])
    print(f"{NAME[m_]:24}{len(rs):>5}{mean([r['input_tokens'] for r in rs]):>9.0f}{o:>9.0f}{tot:>9.0f}"
          f"{msg:>6.1f}{(o/msg if msg else 0):>9.0f}{wt:>9.0f}{tt:>9.0f}{(tt-wt)/tt*100:>7.0f}%"
          f"{solved:>7}{(sum(r['total_tokens'] for r in rs)/solved if solved else 0):>10.0f}")

# ── 分區 × 模型 ──
print("\n【分區平均 working_time 秒 / 平均 output tok / 解出率】")
for arm in ["contaminated", "recent2026", "deep_hard"]:
    print(f"\n{arm}")
    for m_ in MO:
        rs = [r for r in R if r["model"] == m_ and r["arm"] == arm]
        if not rs: continue
        print(f"  {NAME[m_]:24}{mean([r['working_time'] for r in rs]):7.0f}s "
              f"{mean([r['output_tokens'] for r in rs]):8.0f} "
              f"{sum(r['solved'] for r in rs)}/{len(rs)}")

# ── 解出 vs 未解出的成本 ──
print("\n【解出 vs 未解出：平均 working_time / output tok】")
for m_ in MO:
    a = [r for r in R if r["model"] == m_ and r["solved"]]
    b = [r for r in R if r["model"] == m_ and not r["solved"]]
    print(f"  {NAME[m_]:24} 解出 n={len(a):3} {mean([r['working_time'] for r in a]):6.0f}s "
          f"{mean([r['output_tokens'] for r in a]):7.0f}tok | 未解 n={len(b):3} "
          f"{mean([r['working_time'] for r in b]):6.0f}s {mean([r['output_tokens'] for r in b]):7.0f}tok")

# ── limit 分佈 ──
print("\n【樣本終止原因分佈】")
lim = collections.defaultdict(collections.Counter)
for r in R: lim[r["model"]][r["limit"] or "(正常結束)"] += 1
for m_ in MO: print(f"  {NAME[m_]:24}{dict(lim[m_])}")
