#!/usr/bin/env python3
"""每題一張小表（27 題 × 6 模型 ＝ 162 格），每格為該 (題,模型) 5 個 epoch 的平均。
輸出：COST_PER_TASK.md（27 張表）＋ bench27_cost_cells.csv（162 列長格式，供再分析）。"""
import json, collections, os, re, csv

ROOT = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(ROOT, "bench27_cost.json")))
H = open(os.path.join(ROOT, "dashboard.html")).read()
TASKS = json.loads(re.search(r"const TASKS = (\[.*?\]);", H, re.S).group(1))
MO = ["8b", "12b", "26b", "30b", "70b", "550b"]
NAME = {"8b": "llama-3.1-8b", "12b": "gemma-4-12b", "26b": "gemma-4-26b",
        "30b": "nemotron-cascade-2-30b", "70b": "llama-3.3-70b", "550b": "nemotron-3-ultra-550b"}
ARMZH = {"contaminated": "污染組", "recent2026": "近代組", "deep_hard": "深難層"}

agg = collections.defaultdict(list)
for r in R: agg[(r["task"], r["model"])].append(r)
mean = lambda v: sum(v) / len(v) if v else 0.0
order = sorted(TASKS, key=lambda t: t["code"])

md, rows = [], []
md.append("# Bench27 每題成本明細（27 題 × 6 模型 = 162 格，每格為 5 個 epoch 的平均）\n")
md.append("資料源 `bench27_cost.json`（803 有效樣本）。欄位說明：\n")
md.append("- **input / output / 總 tok**：該樣本所有 model 呼叫的 token 加總，取 epoch 平均\n"
          "- **訊息**：assistant 訊息數（＝ agent 實際走了幾步）；**out/訊息**：單次生成長度\n"
          "- **working**：agent 實際工作秒數；**total**：牆鐘（含 gateway 排隊/退避）；"
          "**排隊稅** ＝ (total−working)/total\n"
          "- **解出**：scorer 判 C 的 epoch 數 / 有效 epoch 數；**終止**：撞到的預算上限\n")

for t in order:
    md.append(f"\n## {t['code']} · {t['name']}　（{ARMZH[t['arm']]}／{t['cat']}／{t['diff']}）\n")
    md.append("| 模型 | n | input tok | output tok | 總 tok | 訊息 | out/訊息 | working | total | 排隊稅 | 解出 | 終止原因 |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for m_ in MO:
        c = agg.get((t["tid"], m_), [])
        if not c:
            md.append(f"| {NAME[m_]} | 0 | — | — | — | — | — | — | — | — | — | — |"); continue
        it, ot = mean([x["input_tokens"] for x in c]), mean([x["output_tokens"] for x in c])
        tt, msg = mean([x["total_tokens"] for x in c]), mean([x["assistant_msgs"] for x in c])
        wt, tl = mean([x["working_time"] for x in c]), mean([x["total_time"] for x in c])
        sv = sum(x["solved"] for x in c)
        tax = f"{(tl - wt) / tl * 100:.0f}%" if tl > 0 and wt >= 0 else "n/a"
        lim = collections.Counter("步數" if "message" in x["limit"] else "時間" if "time" in x["limit"]
                                  else "正常" for x in c)
        limtxt = "・".join(f"{k}{v}" for k, v in lim.most_common())
        md.append(f"| {NAME[m_]} | {len(c)} | {it:,.0f} | {ot:,.0f} | {tt:,.0f} | {msg:.1f} | {ot/msg:,.0f} | "
                  f"{wt:,.0f}s | {tl:,.0f}s | {tax} | {sv}/{len(c)} | {limtxt} |")
        rows.append(dict(code=t["code"], task=t["name"], tid=t["tid"], arm=t["arm"], cat=t["cat"],
                         diff=t["diff"], model=NAME[m_], short=m_, n=len(c),
                         input_tok=round(it), output_tok=round(ot), total_tok=round(tt),
                         msgs=round(msg, 1), out_per_msg=round(ot / msg) if msg else 0,
                         working_s=round(wt, 1), total_s=round(tl, 1),
                         queue_tax_pct=round((tl - wt) / tl * 100, 1) if tl > 0 and wt >= 0 else "",
                         solved=sv, solve_rate=round(sv / len(c), 2), stop=limtxt))

open(os.path.join(ROOT, "COST_PER_TASK.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
with open(os.path.join(ROOT, "bench27_cost_cells.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"COST_PER_TASK.md：{len(order)} 張表；bench27_cost_cells.csv：{len(rows)} 列")
