# 與步驟分析 repo 串接

[English](../en/COMPANION.md) · [文件導覽](../README.md)

簡報第 46 頁同時列出本 repo 與 [YuCheng1122/ais-final](https://github.com/YuCheng1122/ais-final)。它們分別處理「跑題與保留軌跡」及「把軌跡結構化、比對步驟」，共同構成專題。建議先保留兩個 repo，以版本與明確介面串接。

本次唯讀檢查的 companion revision：`9a1a2af87c938a3e2d9ac4af7ba4fb318b26bc36`（2026-09-19 檢視）。這是檢視時版本，**尚未確認就是簡報用版本**。

## 哪些已經公開

| 內容 | 本 repo | companion |
|---|---|---|
| 題檔、Docker、Inspect 任務 | 有 | 不作為執行入口 |
| Flag 結果、成本、原始軌跡匯出 | 有 | 使用其匯出／抽取版本 |
| Checkpoint／參考解 | 有 | 有自己的 `ctf-step` reference JSON |
| 抽取 prompt 與 schema | 不執行模型抽取 | `Dataset/PROMPT.md` |
| Anchor 評分 | 舊 pilot 可供參考 | `src/anchor_match.py`、`src/score_steps.py` |
| 語意相似度 | 不含 embedding pipeline | Qwen3-Embedding-0.6B，探索性訊號 |
| 步驟互動報表 | 歷史 flag 儀表板 | `src/render_table.py` |

以上依[釘選版本 README](https://github.com/YuCheng1122/ais-final/blob/9a1a2af87c938a3e2d9ac4af7ba4fb318b26bc36/README.md)及其[方法文件](https://github.com/YuCheng1122/ais-final/blob/9a1a2af87c938a3e2d9ac4af7ba4fb318b26bc36/src/METHODOLOGY.md)核對；本次沒有重新執行 companion 的模型抽取或 embedding。

## 對接規則

1. 用 [TASK_CATALOG](../../results/TASK_CATALOG.md) 取得 `C/R/D` 分析 ID，join 時保留 `(task, model, epoch)`。
2. 參考解與模型軌跡須分開標註來源，模型只接觸題面及允許的附件。不可把 reference 或 gold flag 混入輸入。
3. 新實驗用 `python -m ais3_bench export` 產生 `authored.jsonl` 與 audit。這是證據格式，**不能直接當成 companion 的 ctf-step 格式**。
4. 如要重建既有圖，先在 companion 的既有 JSON 資料上重跑 anchor 評分，避免未經版本控制重新抽取而變更分母。依該 repo 自己的 requirements／指南操作。
5. 如要加入新軌跡，依原抽取 prompt 產生 `ctf-step`，保留來源雜湊、抽取模型版本、完整 prompt、參數、錯誤與人工覆核結果。
6. 對齊 `solved(C/I)`、`flag_status`、reference-step coverage 的定義後，才比較圖表。

## 已發現的口徑差異

本 repo 主樣本為 803，frontier 彙總是 131 次；companion 文件寫有 942 個有效 agent-run JSON、3 次錯誤未轉換。**不能直接把 803+131 與 942 認定為同一資料批次**。需雙方 input manifest、抽取紀錄及排除列表來對齊，尤其零生成樣本是否被排除。

Companion 說明以 literal anchor 決定 reached，embedding 只作語意參考；這比「語意相似就給能力分」更窄。Anchor 門檻、寬鬆比對與 generic token 仍可能造成假陽性，需要人工驗證。

本次僅引用及記錄分工，未複製 companion 原始碼／資料。若後續合併成單一 repo，先確認作者同意、授權、正式 revision 和資料口徑；不要用本 repo 的 MIT 自動覆蓋隊友材料。
