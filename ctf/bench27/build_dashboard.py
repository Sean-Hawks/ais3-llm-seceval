#!/usr/bin/env python3
"""把 bench27_runs.json（單一真相源）注入 dashboard.html 的 RUNS 佔位符並更新時間戳。
題目靜態 spec（顯示名/類別/Opus）已烤在 dashboard.html 的 TASKS；此腳本只灌『每 run 結果』。
用法：.venv/bin/python ctf/bench27/build_dashboard.py [dashboard.html 路徑]"""
import json, os, re, sys, datetime
ROOT = os.path.dirname(os.path.abspath(__file__))
runs = json.load(open(os.path.join(ROOT, "bench27_runs.json"), encoding="utf-8"))
# [tid, model, solved01, working_time]
RUNS = [[r["task"], r["model"], 1 if r["solved"] else 0, r.get("working_time", 0)] for r in runs]
# Opus 5-epoch 盲解成績（頂端標準欄）；跑到哪灌到哪
op = os.path.join(ROOT, "opus_runs.json")
OPUS = json.load(open(op, encoding="utf-8")) if os.path.exists(op) else {}
# 即時跑批狀態快照
st = os.path.join(ROOT, "run_status.json")
STATUS = json.load(open(st, encoding="utf-8")) if os.path.exists(st) else {}
html_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dashboard.html")
h = open(html_path, encoding="utf-8").read()
# ★ 先把任何已烤入的 const 還原成 placeholder（讓本腳本對「模板或已烤檔」都可重複執行）
h = re.sub(r"const RUNS = .*?;", "const RUNS = /*__RUNS__*/;", h, count=1)
h = re.sub(r"const OPUS = .*?;", "const OPUS = /*__OPUS__*/;", h, count=1)
h = re.sub(r"const STATUS = .*?;", "const STATUS = /*__STATUS__*/;", h, count=1)
h = re.sub(r'const STAMP = "[^"]*";', 'const STAMP = "/*__STAMP__*/";', h, count=1)
h = h.replace("/*__RUNS__*/", json.dumps(RUNS, ensure_ascii=False, separators=(",", ":")))
h = h.replace("/*__OPUS__*/", json.dumps(OPUS, ensure_ascii=False, separators=(",", ":")))
h = h.replace("/*__STATUS__*/", json.dumps(STATUS, ensure_ascii=False, separators=(",", ":")))
h = re.sub(r"/\*__STAMP__\*/", STATUS.get("stamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), h, count=1)
open(html_path, "w", encoding="utf-8").write(h)
print(f"注入 {len(RUNS)} run(含時間) + Opus {len(OPUS)}/27 + status → {html_path}")
