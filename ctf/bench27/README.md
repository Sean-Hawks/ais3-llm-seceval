# Bench27 — tasks, trajectories and research evidence

[繁體中文專案總覽](../../README.zh-TW.md) · [English overview](../../README.en.md) · [Task catalog / 題目索引](../../results/TASK_CATALOG.md)

27 tasks: 12 older public tasks (`contaminated`, a historical exposure-risk label), 12 tasks from 2026 (`recent2026`), and 3 difficult case studies (`deep_hard`). 年份分組不代表已查證訓練資料污染；2026 題也不能保證未見過。每題附參考 writeup 與 checkpoint 定義；12 題 recent2026 均有本地 task metadata，六個服務題已附 compose。

## Start / 開始

```bash
# From repository root / 從 repo 根目錄
python3 -m ais3_bench validate
python3 -m ais3_bench report
python3 -m ais3_bench run --arm all --model all
```

The last command previews 24 Inspect jobs; `--execute` starts model calls. 最後一行預覽設定，不呼叫 API；加 `--execute` 才會啟動實驗。[中文操作指南](../../docs/zh-TW/SETUP.md) / [English setup](../../docs/en/SETUP.md).

## File roles / 檔案用途

| Files | Role / 用途 |
|---|---|
| `MANIFEST.json` | Task definitions; preserved IDs and flags / 題組定義 |
| `contaminated/`, `recent2026/`, `deep_hard/` | Tasks, reference writeups, checkpoints; upstream loader for old/deep arms / 題目與參考證據 |
| `bench27_runs.json` | Historical 803 valid attempts; do not overwrite with a new run / 既有結果快照 |
| `bench27_cost.json`, `bench27_cost_cells.csv` | Historical timing and token evidence; one negative working-time anomaly / 成本資料 |
| `opus_runs*.json` | Different-scaffold frontier aggregates; not directly comparable / Frontier 參考 |
| `agent_wp/` | Actual model transcripts exported as Markdown, possibly truncated / 模型解題軌跡 |
| `wp_27/` | Packaged reference material / 參考解包 |
| `frontier_manual/` | Manual/reference solver notes; not interchangeable with repeated scored attempts / 手解參考 |
| `recent2026_eval.py` | Maintained custom task loader / 自訂 task |
| `run_contaminated.sh`, `run_recent2026.sh`, `run_deep_hard.sh` | Compatibility wrappers around the maintained CLI, preview by default / 相容入口 |
| Other `run_*.sh`, `build_*.py`, `extract_*.py`, `export_*.py`, tables, `dashboard.html`, `run_status.json` | Research-era tooling/artifacts; requires original local inputs and may use older selection rules / 歷史工具與產物 |

The maintained reports live in [`results/`](../../results/README.md), not in historical dashboard status. 新的分析入口為 `results/`；不要把歷史 dashboard 狀態當成即時進度，也不要混用舊工具的不同去重規則。

## Scoring and process analysis / 評分與步驟分析

Historical InterCode/Cybench use `includes`; recent2026 uses flag-token-set matching. A reference checkpoint is not automatically a scored completion. 本 repo 提供步驟參考資料；簡報的完整抽取／anchor／語意分析在[隊友 repo](https://github.com/YuCheng1122/ais-final)。

[Methodology / 方法與限制](../../docs/en/METHODOLOGY.md) · [中文方法](../../docs/zh-TW/METHODOLOGY.md) · [Data dictionary / 資料字典](../../docs/en/DATA.md) · [Evidence gaps / 待補資料](../../docs/zh-TW/EVIDENCE_GAPS.md)
