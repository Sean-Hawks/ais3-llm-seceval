#!/usr/bin/env python3
"""把 bench27_runs.json（單一真相源）注入 dashboard.html 的 RUNS 佔位符並更新時間戳。
題目靜態 spec（顯示名/類別/Opus）已烤在 dashboard.html 的 TASKS；此腳本只灌『每 run 結果』。
用法：.venv/bin/python ctf/bench27/build_dashboard.py [dashboard.html 路徑]"""
import json, os, re, sys, datetime
ROOT = os.path.dirname(os.path.abspath(__file__))
runs = json.load(open(os.path.join(ROOT, "bench27_runs.json"), encoding="utf-8"))
RUNS = [[r["task"], r["model"], 1 if r["solved"] else 0] for r in runs]
html_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dashboard.html")
h = open(html_path, encoding="utf-8").read()
h = h.replace("/*__RUNS__*/", json.dumps(RUNS, ensure_ascii=False, separators=(",", ":")))
h = re.sub(r"/\*__STAMP__\*/", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), h, count=1)
open(html_path, "w", encoding="utf-8").write(h)
print(f"注入 {len(RUNS)} 筆 run → {html_path}")
