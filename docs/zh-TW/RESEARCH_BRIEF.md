# 研究摘要

[English](../en/RESEARCH_BRIEF.md) · [專案首頁](../../README.zh-TW.md) · [主張與證據](CLAIMS.md)

**AIS3 LLM Security Evaluation：基於 writeup 的 CTF 解題軌跡分析**

AIS3 2026 AI2 專題團隊 · [AI 組最佳專題](../../RECOGNITION.md)

## 摘要

CTF 的最終 flag 正確性提供客觀的結果指標，但無法說明未成功模型已完成哪些中間步驟。本專題探索互補的分析方式：以參考 writeup 拆解階段，再與模型實際解題軌跡比對，分別呈現文字證據、語意相似度與最終結果。Bench27 包含六類共 27 題公開 CTF，分為 12 題較早公開題、12 題 2026 題與三題困難案例。六個模型標籤各規劃每題五次嘗試；公開快照保留 803 筆有效樣本，已對本機 30 份原始 logs 完成身份、評分、時間與截斷 submission 的回溯核對。隊友 repo 實作結構化步驟抽取與比對。本專案提供可重建的結果快照及可檢視的過程分析介面；新舊題比較因難度、評分器與執行條件未完全控制，僅作描述性解讀。完整重建簡報步驟圖仍需對齊隊友的正式資料版本。

## 研究問題

| 問題 | 操作定義 | 目前證據 |
|---|---|---|
| RQ1：模型能解哪些題目與類別？ | 每次嘗試的 scorer 成功率、可用重複次數中至少成功一次的題數 | 可由 803 筆快照重建 |
| RQ2：較早公開題與 2026 題的結果有何差異？ | 兩分區成功率差距；困難案例不納入此對照 | 可重建描述性比較；類別分布及 scorer 仍有混淆 |
| RQ3：未提交正確 flag 的模型已完成什麼？ | 模型 authored 文字與參考階段的證據比對，獨立於最終成功率 | 已有 checkpoints、軌跡與隊友程式；簡報精確矩陣仍待版本對齊 |

## 與既有研究的關係

這是一份研究軟體成果與專題研究，不宣稱首創過程評估。

- **InterCode** 提供帶執行回饋的互動式程式框架，並可延伸至 CTF；本專題透過 Inspect 使用其生態系。[Yang et al., 2023](https://arxiv.org/abs/2306.14898)。
- **Cybench** 已包含中間子任務評估；本專題偏重事後將已記錄的解題軌跡與 writeup 階段對齊。這是分析重點與實作選擇，不是已證明的效果優越性。[Zhang et al., 2024/2025](https://arxiv.org/abs/2408.08926)。
- **NYU CTF Bench** 提供可擴充的 CTF 資料與自動化 agent 框架；Bench27 是較小型的精選研究，不能取代廣泛覆蓋的 benchmark。[Shao et al., 2024/2025](https://arxiv.org/abs/2406.05590)。

具體貢獻在於選題與參考標註、結果與軌跡證據、執行到步驟分析的介面，以及可追查分數來源的工具。不宣稱所有既有研究都只看最終成功、這是一把通用且校準完成的能力尺，或新題確定未進訓練資料。

## 實驗成果範圍

| 面向 | 已提供內容 |
|---|---|
| 題目 | 27 題；crypto 6、rev 4、forensics 4、misc 5、web 4、pwn 4 |
| 分區 | 12 題較早公開題、12 題 2026 題、3 題困難案例 |
| 重複 | 810 次規劃嘗試；保留 803；排除 3 sample error 與 4 零生成 |
| 模型 | 六個歷史 gateway 模型標籤；確切 provider revision/cutoff 尚待對齊 |
| 設定 | Inspect AI、Docker、已記錄的限制；新實驗預設集中管理 |
| 結果證據 | Flag 分數、提交、時間、log 身份、來源雜湊與回溯稽核 |
| 過程證據 | 參考 checkpoints、解題軌跡、獨立的隊友抽取／評分程式 |
| 獎項 | AIS3 2026 AI 組最佳專題；來源與英文翻譯另列於獲獎紀錄 |

「解出一題」是可用嘗試中至少一次成功，不是無偏 pass@5 估計。803 次也不是 803 題獨立任務。分母與成功率見[結果](../../results/README.zh-TW.md)；原始 `.eval` 未直接公開，已發布雜湊與排除身份。

## 具體案例

`back_to_the_past` 可拆為發現 `.git/`、重建 repository、找出被 reset 的 commit，以及取出 `flag.txt`。模型可能成功重建 repo，卻沒找到已刪除的秘密。最終二元分數仍是失敗；過程分析能指出卡住的位置。

命令中出現 `git reflog` 不代表 repo 已重建或命令成功。Anchor 是可供檢視的文字證據，引用題目或失敗命令仍可能假性命中；語意相似也不等於步驟完成。替代解法可能跳過標準路徑，因此相依順序僅作軟性參考。[原始 checkpoints](../../ctf/bench27/contaminated/web_back_to_the_past/checkpoints.json)。

## 重現已支持的結果

```bash
python3 -m ais3_bench validate
python3 -m ais3_bench report --check
python3 -m unittest discover -s tests -v
```

這些離線指令驗證本地附件、結果／成本身份與報告，不需 API 或 raw logs。持有原始 logs 者可另跑 `scripts/audit_snapshot.py`。新模型實驗見[操作指南](SETUP.md)；隊友的 `ctf-step` 格式與所檢查版本見[串接文件](COMPANION.md)。

## 解讀與後續實驗

目前最強的可支持主張是：公開結果內部一致，且與本次檢視的本機 logs 相符。過程分析提供更具解釋力的失敗觀點，但與專家判斷的一致性仍需量測。

下一步應固定兩 repo 及畫圖資料，抽樣人工覆核 anchor precision／recall，納入替代解法；在相同 scaffold 與已確認工具條件下比較模型；以題目為單位估計不確定性並做排除規則敏感度分析。未控制暴露與難度前，不把時間差距解讀成因果。

Frontier 使用不同 scaffold，且存在簡報 26/27 與當前 27/27 的差異，因此不列入同條件排名。新服務網路設定也不能回溯證明原始環境已完全斷網；上游 Cybench 的 Docker 設定允許上網。[完整方法](METHODOLOGY.md) · [待補證據](EVIDENCE_GAPS.md)。
