# ais3-llm-seceval

**語言模型資安能力評量的方法設計** — 一套以 [Inspect AI](https://inspect.aisi.org.uk/) 為骨幹、針對「污染」問題設計的 LLM 資安（CTF）能力評測 harness。

> A methodology and harness for evaluating the cybersecurity capabilities of language models, built around an explicit **contamination-control** design. Developed as the AI-track capstone project for Taiwan's **AIS3 2026** summer program.

---

## 這個專案在回答什麼問題

「一個語言模型在資安任務（CTF）上得高分，到底是**真的會**，還是**背過答案**？」

公開 CTF 題目幾乎必然帶有公開 writeup，極可能已進入模型訓練資料。單純跑一批公開題、報一個 accuracy，量到的可能只是**背誦（recall）**而非**能力（capability）**。本專案的核心貢獻是一套**把污染變成可量測對照軸**的評測方法，並以一組實測模型驗證。

## 方法主幹（不論題組如何變都成立）

- **抗污染三層**：① 有洞版 vs 修補版的**對照配對**（量假陽性率）② 沙箱可執行的 **pass/fail** ③ 時間污染 gap（僅輔助，不單押）。
- **統一 harness**：全部走 Inspect AI，組態固定並寫入報告（harness 設定會直接影響分數，見下方發現）。
- **統計效度**：每題 ≥5 次跑 + 95% CI；題數 ≥50 才有鑑別力（n=5 時 stderr≈0.2）。
- **嚴謹評分**：以 `exact_flag()`（提交的 flag-token 集合須**恰等於**正解）取代上游常見的 `includes()` 子字串比對，阻擋「候選答案轟炸」這類 reward hacking。
- **雙軸評估**：不只 accuracy，另計 **Intuition Index**（II = 100 / 解題中位步數），量「準」與「廣」之外的「直覺強度」。實測發現 II 與 accuracy **解耦**（例：某模型「準但窄」、某模型「廣但亂」）。

> ⚠️ **科學限制（貫穿全專案的立場）**：單靠「訓練截止後的新 CVE / temporal holdout」不可靠——CVE ≠ 0-day（exploit 常先外流）、且時間訊號可被題目改寫抹除。因此污染訊號**必須**與各階段標準解 checkpoint 的語意命中並用；抗污染泛化的主張只由對照配對＋自製私有題支撐。

## Bench27 — 污染對照 × 深度標準解題組

主要評測題組，27 題分三區合看（詳見 [`ctf/bench27/README.md`](ctf/bench27/README.md)）：

| 分區 | 題數 | 年份／來源 | 測什麼 |
|---|---|---|---|
| **contaminated** | 12 | 2022–2023（picoCTF／cybench）| writeup 幾乎必進訓練資料 → **recall** |
| **recent2026** | 12 | 真實 2026 CTF（post-cutoff）| 未污染 → **真實能力** |
| **deep_hard** | 3 | cybench（HTB-2024／Sekai）| 多階段硬題，checkpoint 有 headroom |

**核心對照**：同一模型在 contaminated 與 recent2026 的表現差（gap）＝污染訊號。每題附 `README.md`＋`writeup.md`＋`checkpoints.json`（各階段 milestone 語意 + 客觀錨點/中間值），供詞向量比對與部分分。

## 受測模型

官方提供的 7 個 OpenAI-compatible 模型，構成 8B → 550B 的 scaling 階梯：

```
llama-3.1-8b · gemma-4-12b · gemma-4-26b · nemotron-cascade-2-30b
llama-3.3-70b · nemotron-3-ultra-550b            （llama-guard-3-8b 作安全評分員，不進解題評測）
```

## 快速開始

完整設定（跨 OS、Docker、endpoint、疑難排解）見 **[`docs/SETUP.md`](docs/SETUP.md)**。最小路徑：

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # 填入你的 OpenAI-compatible endpoint 與 key

# MCQ 冒煙：確認能連上 endpoint 並跑完一次評測
inspect eval smoke_test.py --model openai-api/ais3/ais3/llama-3.1-8b --limit 6

# Bench27 污染組（需 Docker）
bash ctf/bench27/run_contaminated.sh
```

> 所有評測都必須從本目錄執行（Inspect 會自動讀取同目錄的 `.env`）。CTF agentic 評測需要 Docker。

## 儲存庫結構

```
.
├── README.md                  ← 本檔（專案總覽）
├── docs/SETUP.md              安裝與環境設定指南（原 quickstart）
├── skills.md                  操作手冊 / 方法論參考（團隊可照跑）
├── smoke_test.py              MCQ 冒煙測試（sec-smoke task）
├── requirements.txt           鎖定版本依賴
├── LICENSE                    MIT（程式碼）
├── THIRD_PARTY_NOTICES.md     第三方題目與工具的來源與授權標註
└── ctf/                       CTF agentic 評測主體
    ├── README.md              迷你 CTF 評測（agentic + Docker 沙箱）說明
    ├── DATA_PROVENANCE.md     題目資料完整溯源（逐題出處／上游版本）
    ├── bench27/               ★ 主題組：contaminated / recent2026 / deep_hard
    ├── deep/                  深度題與 cybench case study（推理路徑分析）
    └── _archive_20260726/     早期題組封存（Bench25 等，保留供溯源）
```

## 實測到的方法論發現（皆有 log 佐證，寫入報告用）

1. **Harness confound**：真 picoCTF forensics 題因沙箱缺 `steghide`/`xxd` 而**假性失敗**；補工具後同一模型分數上升——分數會被 harness 設定左右，故組態必須固定並揭露。
2. **非確定性**：同題同模型不同次結果會變 → 每題 ≥5 次 + CI 是必要而非奢侈。
3. **「無解題」是最貴的題**：agentic 評測的牆鐘由「解不出來卻一直嘗試」的題主導，越強的模型越會多試分解法而更慢——時間成本不由題數決定。
4. **Gateway 序列化 / 排隊偽裝成慢**：診斷速度要看 `working_time` 而非 `total_time`；共享 gateway 下多個 eval 不能併行取分（弱模型會被吞吐餓死）。
5. **子字串評分是上界**：cybench 與 gdm_intercode_ctf 上游皆用 `includes()`，其分數是能力上界，**不可**與本專案 `exact_flag` 的自製題結果並列比較。

## 誠實框定與限制

- **污染組屬已知且不可迴避的污染**：全部有公開 writeup，分數僅代表「已知污染下的領域覆蓋／工具使用／端到端成功率／粗略排名」，**不得**解讀為未見題泛化。
- **Frontier 手解參考點非盲測能力分**：以 frontier 模型（Opus）手解 27 題，作為 checkpoint 覆蓋與路徑比對的**上緣參考錨點**，出題方持 ground truth，非盲測分數。
- 難度標籤為相對估計、未跨來源校準；部分題的沙箱可解性需另行驗證。

完整限制聲明見 [`ctf/DATA_PROVENANCE.md`](ctf/DATA_PROVENANCE.md) §5。

## 資料來源與第三方內容

本題組的 CTF 題檔與參考 writeup **多數並非本專案自製**，而是選自公開學術 benchmark（InterCode-CTF、Cybench）與公開 CTF 賽事歸檔（LACTF 2026、BYUCTF 2026 等）。所有第三方內容的出處、上游 repo 與授權條款見 **[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)** 與 **[`ctf/DATA_PROVENANCE.md`](ctf/DATA_PROVENANCE.md)**。各題原檔皆保留並標註來源。

## 授權

本專案**自有的**程式碼、評測設計、checkpoints 與文件以 **MIT** 授權（見 [`LICENSE`](LICENSE)）。
第三方 CTF 題檔與 writeup 各自受其上游授權／賽事條款約束，**不**在本專案的 MIT 授權範圍內——詳見 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

---

*AIS3 2026 AI 組專題 — 語言模型資安能力評量的方法設計。憑證（`.env`）永不進版控。*
