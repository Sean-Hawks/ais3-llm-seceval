# Bench27 結果快照

[繁體中文](README.zh-TW.md) | [English](README.md)

由 `python -m ais3_bench report` 產生。來源是已提交的 JSON；不呼叫 API、不重跑模型。

27 tasks × 6 models × 5 epochs = 810 planned; 803 valid; 7 absent from snapshot.

缺少的 7 格不計入有效樣本分母。本次以本機原始 logs 核對：3 個 sample error、4 個零生成，803 筆身份、評分、時間與截斷提交皆與快照一致。另有 60 筆較舊 run 被整批取代。

[Retrospective audit / 回溯稽核](../ctf/bench27/snapshot_audit.json) · [Summary / 摘要](summary.json)

## 至少成功一次的題數

這是最多五次有效嘗試的觀察覆蓋率，不是單次成功率，也不是無偏 pass@5 估計。

| Model | Solved / 27 | crypto / 6 | rev / 4 | forensics / 4 | misc / 5 | web / 4 | pwn / 4 |
|---|---:|---:|---:|---:|---:|---:|---:|
| nemotron-3-ultra-550b | 15/27 | 4/6 | 3/4 | 4/4 | 3/5 | 1/4 | 0/4 |
| llama-3.3-70b | 7/27 | 1/6 | 2/4 | 1/4 | 3/5 | 0/4 | 0/4 |
| nemotron-cascade-2-30b | 10/27 | 2/6 | 2/4 | 3/4 | 3/5 | 0/4 | 0/4 |
| gemma-4-26b | 14/27 | 3/6 | 3/4 | 4/4 | 3/5 | 1/4 | 0/4 |
| gemma-4-12b | 12/27 | 3/6 | 2/4 | 4/4 | 3/5 | 0/4 | 0/4 |
| llama-3.1-8b | 4/27 | 1/6 | 1/4 | 1/4 | 1/5 | 0/4 | 0/4 |

## 有效嘗試成功率

| Model | contaminated | recent2026 | deep_hard | Old − recent (pp) |
|---|---:|---:|---:|---:|
| llama-3.1-8b | 11/58 (19.0%) | 0/60 (0.0%) | 0/14 (0.0%) | +19.0 |
| gemma-4-12b | 33/60 (55.0%) | 14/57 (24.6%) | 3/14 (21.4%) | +30.4 |
| gemma-4-26b | 35/60 (58.3%) | 24/60 (40.0%) | 5/15 (33.3%) | +18.3 |
| nemotron-cascade-2-30b | 32/60 (53.3%) | 6/60 (10.0%) | 1/15 (6.7%) | +43.3 |
| llama-3.3-70b | 25/60 (41.7%) | 1/60 (1.7%) | 0/15 (0.0%) | +40.0 |
| nemotron-3-ultra-550b | 37/60 (61.7%) | 22/60 (36.7%) | 5/15 (33.3%) | +25.0 |

年份差距是描述性結果，無法單獨歸因於訓練資料污染。兩組類別數量並非完全對稱，且使用不同評分器。重複 epoch 也不是 803 個獨立題目。

## Frontier 參考與簡報差異

目前 `opus_runs.json` 為 27/27 題、119/131 次成功；簡報第 22、34 頁為 26/27。兩者不可靜默合併，且使用不同 scaffold，不能和主表當成相同條件的排名。

樣本 `total_time` 加總為 80.56 小時；此值包含重疊執行時間，不是整場實驗的日曆耗時，也不是金額。

[Methodology / 方法](../docs/zh-TW/METHODOLOGY.md) · [Evidence gaps / 待補資料](../docs/zh-TW/EVIDENCE_GAPS.md)
