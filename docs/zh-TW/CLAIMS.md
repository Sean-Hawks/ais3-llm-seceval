# 研究主張與證據

[English](../en/CLAIMS.md) · [研究摘要](RESEARCH_BRIEF.md)

此表分開呈現獲獎紀錄、可重建觀察與尚未支持的推論。CI 通過表示已實作的檢查通過，不代表所有研究主張皆已驗證。

| 主張 | 狀態 | 證據 | 邊界／下一步 |
|---|---|---|---|
| 專題獲 AIS3 2026 AI 組最佳專題 | 團隊提供且有作者公開紀錄 | [獲獎來源](../../RECOGNITION.md) | 英文獎名為翻譯；後續可補官方公告／獎狀 |
| Bench27 有 27 題與對應 checkpoints | 已由 repo 定義驗證 | [題目索引](../../results/TASK_CATALOG.md)、`validate` | 精選公開題，難度與類別標籤未經校準 |
| 803 筆保留樣本與所檢視 raw logs 相符 | 已回溯驗證 | [稽核紀錄](../../ctf/bench27/snapshot_audit.json) | 原始 logs 留在本機，持有原檔者可核對雜湊；不宣稱事前登記 |
| 六個模型標籤至少一次解出 15/14/12/10/7/4 題 | 可重建觀察 | [結果表](../../results/README.zh-TW.md)、來源 JSON | 這是可用重複中的覆蓋率，不是單次成功率 |
| 六個模型在舊題的整體嘗試成功率均較高 | 可重建的描述性觀察 | [分區結果](../../results/README.zh-TW.md) | 不能歸因為已證明污染；分布、評分器、工具差異仍存在 |
| 過程分析可揭露失敗嘗試的中間進展 | 已實作方法與案例材料 | [參考階段](../../ctf/bench27/contaminated/web_back_to_the_past/checkpoints.json)、[隊友程式](COMPANION.md) | 與專家標註的一致性仍需量測 |
| 只靠本次發布就能重建簡報全部步驟熱圖 | 尚未建立 | [待補證據](EVIDENCE_GAPS.md) | 需確定抽取／評分版本與畫圖資料 |
| 語意相似就證明完成步驟 | 不支持，也不採此解讀 | [方法](METHODOLOGY.md) | 語意訊號僅供探索；literal matches 也須校準 |
| Frontier 可直接與六模型作同條件排名 | 不支持 | 不同 scaffold；[26/27 與 27/27 差異](../../results/README.zh-TW.md) | 相同 scaffold 重跑、統一 outcome 定義 |
| 所有歷史題目皆完全斷網 | 尚未建立 | 自訂與上游網路不同 | 新內部網路只涵蓋六個服務題，不能回推所有歷史環境 |
| Provider 模型版本／cutoff 已確認 | 尚未建立 | 快照記錄的是 gateway 標籤 | 需模型路由／revision 紀錄 |
| Repo 內所有檔案都屬 MIT | 不正確 | [授權範圍](../../THIRD_PARTY_NOTICES.md) | 原創部分用 MIT，第三方依各自條款並補散布依據 |
| 這是已通過同儕審查的論文或 SOTA 宣稱 | 不作此主張 | 研究軟體與獲獎專題 | 引用為軟體，不虛設論文 DOI／接受紀錄 |

## 從資料到結論

`MANIFEST.json + bench27_runs.json + bench27_cost.json + snapshot_audit.json` → 驗證 → 產生 `results/summary.json` 與表格 → 支持上列主張。新實驗 logs 分開存放，不靜默更改歷史快照。

若要提升結論強度，請先補上操作定義、精確輸入、可被反證的驗證方式與結果，再更新專案摘要。
