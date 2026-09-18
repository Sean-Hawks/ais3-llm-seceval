# 資料字典與來源

[English](../en/DATA.md) · [文件導覽](../README.md)

所有相對路徑以下均以 repo 根目錄為基準。新的主要程式不需要讀取 `.env` 即可分析快照。

| 檔案 | 角色 | 可否重建 |
|---|---|---|
| `ctf/bench27/MANIFEST.json` | 27 題身份、來源、分區、flag、難度 | 題組定義，不由結果倒推 |
| `configs/bench27.json` | 模型別名與新的預設執行設定 | 人工維護，變動即不同條件 |
| `ctf/bench27/bench27_runs.json` | 已提交 803 筆 flag 評分結果 | 從對應 raw logs 才可重建原始證據 |
| `ctf/bench27/bench27_cost.json` | 同一批 803 筆 token／時間 | 需 raw logs；token 不等於金額 |
| `ctf/bench27/opus_runs.json` | 不同 scaffold 的 frontier 彙總 | 缺逐筆同格式原始證據與正式版本對應 |
| `ctf/bench27/*/*/checkpoints.json` | 27 題的階段參考與 anchors | 自有研究標註，不能由 flag 分數推算 |
| `ctf/bench27/agent_wp/` | 人可讀的模型軌跡匯出 | 可能截斷，不能取代完整 `.eval` |
| `ctf/bench27/wp_27/` | 人可讀的參考解打包 | 含研究衍生資料；與上游授權分開處理 |
| `ctf/bench27/snapshot_audit.json` | 本次對 30 份本機 raw logs 的去識別回溯稽核 | 需原始 logs；只公開 ID、排除原因與雜湊 |
| `results/` | 雙語結果、摘要與索引 | `python -m ais3_bench report`，標準函式庫即可 |
| `output/` | 新實驗、匯出與暫存 | 不進版控 |

## Run schema

主鍵 `(arm, task, model, epoch)`。題號以字串處理；例如 InterCode 的 `5` 不要轉成數值後丟失跨系統映射。

| 欄位 | 意義 |
|---|---|
| `model` / `model_full` | 本地別名與原始模型標籤；不是權重版本證明 |
| `arm` | contaminated / recent2026 / deep_hard |
| `task` | Inspect sample identity 的正規化形式，對照題目索引 |
| `epoch` | 該 run 的重複次序，歷史主實驗為 1–5 |
| `scorer` / `score_value` | 實際評分器與 C／I |
| `solved` | 等於 scorer 的 C，**不是**搜尋 transcript 找到 flag |
| `target_flag` | 評分端答案，不應做為模型輸入；CTF 答案不是 API 憑證 |
| `submitted` | 原匯出最多 400 字；不能只靠截斷欄位證明全體嚴格重算結果 |
| `flag_in_submission` / `flag_in_transcript` | 舊匯出採不分大小寫 substring，僅輔助診斷，非 scorer |
| `working_time` / `total_time` | 秒；前者有已知負值，後者不可直接當作整場牆鐘 |
| `log_file` | 原始 log 檔名；公開 clone 不附 `.eval` |

新的 `export` 保留完整 submission，flag 診斷採區分大小寫，另提供 audit／authored JSONL。這是新的匯出行為，不回寫歷史快照。

## Checkpoint schema

題目層有 `challenge`、`category`、`flag`、`n_checkpoints`、`checkpoints[]`。各步驟包含 `id`、`stage`、`depends_on`、`milestone`、`anchors`、`expert_action`、`keywords`。順序為參考，不能硬性否定替代解法。`source_of_truth` 部分是舊安裝路徑，非可攜下載 URL。

同一題有三種識別名稱：manifest 目錄、Inspect task ID、分析用 `C01_… / R01_… / D01_…`。完整 join 見 [TASK_CATALOG](../../results/TASK_CATALOG.md)，由 manifest 與 frontier ID 映射重建。

## 證據保留與已知異常

`summary.json` 記錄來源 SHA-256、缺少的七格與負時間異常。`snapshot_audit.json` 已用本機 logs 核對 803 筆結果與七筆排除；不包含原始訊息或 endpoint。這能偵測快照變更，不能證明過去執行環境未被改動。舊 exporter 有不同去重策略；新的結果入口固定以已提交 803 筆快照為準，不重跑舊 log 選樣。

[歷史來源說明](../../ctf/DATA_PROVENANCE.md) 最初為 Bench25，不是完整 Bench27 權威清單；以本次題目索引與每題原始來源交叉查核。第三方重新散布狀態見 [notices](../../THIRD_PARTY_NOTICES.md)。
