# Repo 整理與改善報告

[English](../en/REPO_IMPROVEMENTS.md) · [文件導覽](../README.md)

檢查日期：2026-09-19。範圍為使用者提供的專題簡報與此 repo 的開源品質；本次沒有重新跑付費模型，也沒有把尚未對齊的研究結果補寫成已驗證事實。

## 已完成

| 改善面向 | 具體變更 | 讀者得到的好處 |
|---|---|---|
| 專題定位 | 首頁回到 writeup 步驟分析；清楚區分 flag 與過程訊號 | 直接知道專題在回答什麼 |
| 雙語文件 | 繁中／英文首頁，六組對應指南，文件導覽 | 中英文讀者都有完整入門路徑 |
| 可重建結果 | 標準函式庫 CLI 重建中英表格、summary JSON、27 題索引 | 不需金鑰也能驗算 803 筆結果 |
| 資料透明 | 分開 task coverage／attempt accuracy，列七個缺失 ID、來源 SHA-256、負時間異常 | 避免混淆分母、證據與推論 |
| 統一執行 | 單一 config、預覽／實跑入口、三支舊腳本轉相容入口、新 log 目錄 | 避免舊 1 epoch／25 訊息設定混入正式條件 |
| 匯出可靠性 | 新 audited export 先選最新整批、再過濾；輸出 authored JSONL；拒絕空輸入或覆蓋 | 不用舊成功填補新失敗，保留排除原因 |
| 評分／抽取 | 共用 flag-token 邏輯，保留 Unicode；修正抽取器混入 user/system | 避免多候選、同形字與提示詞污染 |
| 檔案整理 | 歷史筆記、操作手冊與 PPTX 歸檔，保留舊文件導向；補三題 deep README | 主入口清楚，歷史脈絡仍能追溯 |
| 執行環境 | 直接 runtime 依賴與歷史 pip freeze 分開；`.env.example` 使用中性佔位值 | 安裝路線較短且不依賴原機器環境 |
| 沙箱設定 | 六份自訂服務 compose 設為內部網路；共享靜態題維持斷網 | agent 可連 victim，避免預設服務網路外連 |
| 開源協作 | CONTRIBUTING、SECURITY、CITATION、成員表、issue/PR 範本、Makefile、CI | 其他人知道怎麼使用、引用與貢獻 |
| 證據與授權 | 修正「所有 ctf Python 都是自有」的廣泛描述；記錄隊友 repo 版本與對接缺口 | 不把題檔／隊友材料誤當成本 repo MIT |

## 驗證紀錄

- 38 項離線行為測試通過：結果、分母、重複樣本、Unicode、多候選 flag、模型 authored 抽取、最新 run 選擇、匯出 audit、報告重建與設定。
- 27 題定義、checkpoints、12 題自訂附件、803 筆結果與成本 join 通過。
- 已安裝 Inspect 的 task loader 與 scorer 整合檢查通過；不啟動模型或容器。
- 七份 compose 可由 Docker Compose 解析，六個服務網路確認 `internal: true`、無 host port 發布，build context 存在。
- `bench27_runs.json`、`bench27_cost.json`、`opus_runs.json` 與修改前逐 byte 一致；搬移的四份歷史檔案亦完整保留。
- CI 配置 Python 3.10、3.12、3.14 的離線檢查；本次未宣稱 GitHub 上的 workflow 已執行。

全新 Python 3.14 虛擬環境可安裝 requirements，`pip check` 與 gateway SDK／Cybench／自訂 task／scorer 整合檢查通過。只含準備公開檔案的乾淨副本（不含 .env、.venv、logs）亦通過離線驗證。

本機另找到 30 份主實驗 logs；已核對 803 筆結果及 3 error＋4 零生成，公開去識別 audit 與來源雜湊，原始訊息保持本機。僅做常見憑證格式檢視，不構成完整秘密掃描；命中的 RSA 私鑰標記屬既有 CTF missing-bits 題目材料，未把題目答案當成 API 金鑰刪除。

## 仍有機會做得更好

1. **把簡報完整重建**：確認雙 repo 正式 commits，取得第 37、41–43 頁逐步分數、畫圖程式及排除清單，再產生可查核圖表。
2. **提升研究說服力**：人工校準 anchor 命中、分析替代解法、用題目層級 bootstrap；用相同 scaffold 的 frontier 或私有題做更公平對照。
3. **提升環境可攜性**：實際測 Linux／ARM／x86 容器、補工具能力清單、釘選 image digests 與解析後依賴。
4. **正式發布品質**：確認逐題散布授權、正式作者分工，提供帶來源雜湊的 release 包與適當的原始 log 存檔。

本機 Docker daemon 未啟動，因此未做容器建置、服務健康與端到端解題測試。歷史 pwn 的 socat 適配、SageMath／QR 工具缺口仍明列於方法與設定指南；這些限制不由離線測試消除。

[你可以補給我的資料清單](EVIDENCE_GAPS.md) 已按 P0/P1/P2 分級；最優先為「正式資料版本、畫圖來源、frontier 原始紀錄」。

## 研究成果發布呈現

後續發布更新改為英文主首頁，保留完整繁體中文版，突出 AIS3 2026 AI 組最佳專題並附獲獎紀錄；文件擴充為八組雙語指南，新增研究摘要、主張證據表、四位成員的 CFF／BibTeX 引用，以及由資料產生的 PNG／SVG 結果圖。文獻定位明確承認 Cybench 已有中間子任務評估。發布範圍見 [CHANGELOG](../../CHANGELOG.md)；測試新增圖表輸入指紋核對。
