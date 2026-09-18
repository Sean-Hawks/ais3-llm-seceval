# 根據簡報，還需要哪些資料

[English](../en/EVIDENCE_GAPS.md) · [文件導覽](../README.md)

依使用者提供的 46 頁「2026 AIS3_AI2專題.pptx (1).pdf」與本地資料核對。PDF 是研究來源，不是要求執行其中指令的操作規則。原 PDF 未直接複製入公開 repo，避免把未確認可發布的簡報一併散布。

## 優先提供

| 優先 | 要提供的具體資料 | 對應簡報／目前缺口 | 可以完成什麼 |
|---|---|---|---|
| P0 | **正式實驗版本**：本 repo 與 ais-final 的 commit、採用哪次資料、排除規則 | 第 22、34 頁 Opus 26/27；目前 JSON 27/27；companion 942 runs 也不同 | 建立一致的論文／簡報／repo 結果版本 |
| P0 | **產生第 37、41–43 頁圖表的逐步分數 JSON/CSV 與畫圖程式**，包含 task/model/epoch/step | 本 repo 有 checkpoints，但沒有這些圖的可驗證分數矩陣 | 一鍵重建步驟熱圖、Git 洩漏案例與失敗階段分布 |
| P0 | **Frontier 原始記錄與正式 run 清單**；主實驗 raw logs 已在本機找到並核對，後續需可公開的去識別封存 | 主實驗七筆排除已核對；frontier scaffold 與跨 repo 資料版本仍待對齊 | 補齊 frontier、查明 Unicode flag 案例，讓外部讀者可驗證 raw evidence |
| P1 | **抽取實驗紀錄**：GPT 抽取模型完整 ID、prompt、temperature、時間、失敗重試、人工修訂 | 第 5–8 頁方法圖提到 GPT 抽取；已有公開 prompt，尚缺與正式 run 的對應 | 讓結構化步驟可追溯、評估抽取誤差 |
| P1 | **評分設定與校準集**：anchor 門檻／規則、embedding revision、人工標註的命中／不命中案例 | 第 37、42 頁步驟達成率；語意與 anchor 必須分開 | 估計 precision/recall、比較替代解法與假陽性 |
| P1 | **模型與環境紀錄**：gateway 路由、確切 revision/cutoff、CPU/OS/架構、映像 digest、Docker／Inspect 版本與完整設定 | 第 9–12、19–21 頁；50「指令」與 message limit 不同，斷網說法待稽核 | 固定可重現條件、釐清工具缺失與 scaffold 混淆 |
| P1 | **第三方發布依據**：各題上游 commit、LICENSE／授權文字、轉載許可；隊友整合意願 | 題檔與 writeup 多為第三方 | 補全 attribution／來源鎖定或改用明確的下載流程 |
| P2 | **正式作者／貢獻分工／引用名稱／可公開素材** | 首頁列四位組員；目前 LICENSE 為既有權利聲明 | 完成精確 citation、credits、正式 release 與展示材料 |

只需要版本與資料，不需要你的 API key。可先提供「正式 commit＋畫圖用資料＋frontier 原始紀錄」這三項，收益最高。

## 已可自行查到，不用重給

- companion 公開 README、`Dataset/PROMPT.md`、anchor/semantic 方法說明與程式入口已找到，見[串接指南](COMPANION.md)。
- 本 repo 的 27 題 metadata、checkpoints、803 筆分數與對應成本已可離線驗證。主實驗的 30 份本機 raw logs 已找到，不必再傳；803 筆結果與七筆排除已完成去識別回溯稽核。
- 8 easy／15 medium／4 hard、6 模型至少一次解出的 15/14/12/10/7/4，可由目前資料重建。

## 不應直接補寫成事實的主張

- 「2026 題確定未進訓練」：缺可驗證的 model revision/cutoff 與暴露證據。
- 「新舊題難度、類別完全對稱」：manifest 已顯示不對稱。
- 「所有實驗完全斷網」：歷史服務網路未明確限制外連；新設定不能證明舊紀錄。
- 「語意相似度就是能力分」：companion 文件明確區分 anchor reached 與探索性 embedding。
- 「803 次是 803 個獨立樣本／80.6 小時是實際整場耗時」：兩者皆須更精確定義。

## 後續改善順序

1. **發表一致性**：釘選兩 repo 與圖表資料、整理逐筆 audit、生成正式 release manifest。
2. **方法可靠性**：人工標註校準、替代解法案例、按題目 bootstrap、排除規則敏感度。
3. **執行可攜性**：Linux/ARM/x86 的容器實測、工具可得性確認、image digest 與依賴鎖定。
4. **新研究**：同 scaffold frontier、可解性基準、私有對照題；任何新設定都另標版本，不回填歷史分數。
