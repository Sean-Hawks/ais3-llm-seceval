# ais3-llm-seceval

**語言模型資安能力評量的方法設計** — 一套以 [Inspect AI](https://inspect.aisi.org.uk/) 為骨幹、針對「污染」問題設計的 LLM 資安（CTF）能力評測 harness，附 27 題對照題組與 6 個模型 × 5 epoch 的完整實測。

> A methodology and harness for evaluating the cybersecurity capabilities of language models, built around an explicit **contamination-control** design. Ships a 27-task paired benchmark (contaminated vs. post-cutoff), full 6-model × 5-epoch results, and a frontier reference anchor. Developed as the AI-track capstone for Taiwan's **AIS3 2026** summer program.

---

## 這個專案在回答什麼問題

「一個語言模型在資安任務（CTF）上得高分，到底是**真的會**，還是**背過答案**？」

公開 CTF 題目幾乎必然帶有公開 writeup，極可能已進入模型訓練資料。單純跑一批公開題、報一個 accuracy，量到的可能只是**背誦（recall）**而非**能力（capability）**。

更麻煩的是第二個問題：「分數低，是**模型不會**，還是**我的 harness 壞了**？」本專案在實測中反覆撞到這件事，而它幾乎不會出現在 benchmark 論文的結果表裡。

本專案的貢獻是一套把上述兩件事都變成**可量測對照軸**的評測方法，並用一組實測資料驗證它會動。

## 主要結果：污染 gap 在六個模型上全數成立

同一模型、同一 harness、同一組態，跑污染組（2022–2023 公開題）與近代組（2026 post-cutoff 真題），差值即污染訊號：

| 模型 | contaminated | recent2026 | **gap** | deep_hard |
|---|---|---|---|---|
| llama-3.1-8b | 19% (11/58) | 0% (0/60) | **+19pp** | 0% |
| gemma-4-12b | 55% (33/60) | 25% (14/57) | **+30pp** | 21% |
| gemma-4-26b | 58% (35/60) | 40% (24/60) | **+18pp** | 33% |
| nemotron-cascade-2-30b | 53% (32/60) | 10% (6/60) | **+43pp** | 7% |
| llama-3.3-70b | 42% (25/60) | 2% (1/60) | **+40pp** | 0% |
| nemotron-3-ultra-550b | 62% (37/60) | 37% (22/60) | **+25pp** | 33% |

*每格為 per-epoch 樣本層級（27 題 × 6 模型 × 5 epoch，扣除 7 個無效樣本後 n=803）。*

三件值得注意的事：

1. **gap 不是評分器造成的**。污染組走上游 harness 的 `includes()` 子字串評分，近代組走本專案的 `exact_flag()`——這種混用本來會讓 gap 虛胖。用嚴格比對（提交內容須恰等於 flag）重算污染組後，**六個模型分數一格未變**，gap 完全保留。
2. **gap 大小與模型強弱不同調**。550b（最大）gap +25pp，比 30b 的 +43pp、70b 的 +40pp 小；而 26b 的 gap 最小（+18pp）且近代組表現最接近 550b。**排行榜名次在兩個分區之間會重排**——只跑污染題會得到不同的結論。
3. **弱模型的近代組直接歸零**。8b 在 12 題近代題上 0/60。污染組的 19% 幾乎全部是 recall。

> 完整逐題矩陣（含每格解題時間與 token 成本）見 [`ctf/bench27/COST_TABLE.md`](ctf/bench27/COST_TABLE.md)，或開 [`ctf/bench27/dashboard.html`](ctf/bench27/dashboard.html)（單檔、離線可看）。

### Frontier 參考錨點

另以 Opus 4.8 盲解同一組 27 題（題檔與 gold flag 相同，`solution/`、`writeup.md` 已排除）作為能力上緣參考：**27/27 題皆至少解出一次，23 題 5/5 全中，樣本層級 119/131**。

⚠️ 它跑在不同的 scaffold（agentic coding harness，非本專案的 Inspect + gateway 路徑），因此**不可與上表六個模型的分數並列排名**。它的用途是：確認題目本身在本專案的題檔形態下確實可解（排除「題目壞掉」），並提供 checkpoint 覆蓋與解題路徑的比對基準。模型實際解題過程存在 [`ctf/bench27/agent_wp/`](ctf/bench27/agent_wp/)。

## 方法主幹

- **抗污染三層**：① 有洞版 vs 修補版的**對照配對**（量假陽性率）② 沙箱可執行的 **pass/fail** ③ 時間污染 gap（本專案的主力對照軸，但不單押）。
- **統一 harness**：全部走 Inspect AI，組態固定並完整揭露（見下方「定案組態」——harness 設定會直接改變分數）。
- **統計效度**：每題 5 epoch；n=5 時 stderr≈0.2，故單格數字不宜當精確值讀，跨分區的聚合差值才是訊號。
- **嚴謹評分**：本專案自建的題目以 `exact_flag()`（提交的 flag-token 集合須**恰等於**正解）評分，取代上游常見的 `includes()` 子字串比對，阻擋「候選答案轟炸」這類 reward hacking。沿用上游 harness 的題目仍為 `includes()`，其分數是**上界**，本文已就此做過穩健性檢查（見上）。
- **事前的無效樣本判準**：凡樣本產生 0 次生成（無任何 assistant 訊息）一律剔除分母、**不補跑**。只重跑失敗的格子等於選擇性重擲，會系統性偏袒落後的模型。810 格中無效 7 格。
- **雙軸評估**：不只 accuracy，另計 **Intuition Index**（II = 100 / 解題中位步數），量「準」之外的「直覺強度」。實測發現 II 與 accuracy **解耦**（有模型「準但窄」、有模型「廣但亂」）。

> ⚠️ **科學限制（貫穿全專案的立場）**：單靠「訓練截止後的新 CVE / temporal holdout」不可靠——CVE ≠ 0-day（exploit 常先外流）、且時間訊號可被題目改寫抹除。因此污染訊號**必須**與各階段標準解 checkpoint 的語意命中並用；抗污染泛化的主張只由對照配對＋自製私有題支撐。

## Bench27 — 污染對照 × 深度標準解題組

主要評測題組，27 題分三區合看（詳見 [`ctf/bench27/README.md`](ctf/bench27/README.md)）：

| 分區 | 題數 | 年份／來源 | 測什麼 |
|---|---|---|---|
| **contaminated** | 12 | 2022–2023（picoCTF／Cybench）| writeup 幾乎必進訓練資料 → **recall** |
| **recent2026** | 12 | 真實 2026 CTF（LACTF／BYUCTF，post-cutoff）| 未污染 → **真實能力** |
| **deep_hard** | 3 | Cybench（HTB-2024／SekaiCTF）| 多階段硬題，checkpoint 有 headroom |

六大類（crypto／rev／forensics／misc／web／pwn）在兩個 12 題分區中對稱分布。每題附 `README.md`＋`writeup.md`＋`checkpoints.json`（各階段 milestone 語意 + 客觀錨點/中間值），供詞向量比對與部分分；服務型題目另附 `challenge.json` 與 Docker compose。

## 受測模型

主評測為官方 OpenAI-compatible gateway 提供的 6 個解題模型，構成 8B → 550B 的 scaling 階梯：

```
llama-3.1-8b · gemma-4-12b · gemma-4-26b
nemotron-cascade-2-30b · llama-3.3-70b · nemotron-3-ultra-550b
```

（同批另有 `llama-guard-3-8b`，是分類器不是解題模型，不進本評測。）

## 快速開始

完整設定（跨 OS、Docker、endpoint、疑難排解）見 **[`docs/SETUP.md`](docs/SETUP.md)**。最小路徑：

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # 填入你的 OpenAI-compatible endpoint 與 key
```

```bash
# MCQ 冒煙：確認能連上 endpoint 並跑完一次評測
inspect eval smoke_test.py --model openai-api/ais3/ais3/llama-3.1-8b --limit 6
```

```bash
# Bench27 污染組（需 Docker）
bash ctf/bench27/run_contaminated.sh
```

```bash
# 產出分析與儀表板
python ctf/bench27/analyze_bench27.py       # 污染 vs 近代 gap
python ctf/bench27/build_dashboard.py       # 重新產生 dashboard.html
```

> 所有評測都必須從本目錄執行（Inspect 會自動讀取同目錄的 `.env`）。CTF agentic 評測需要 Docker。

### 定案組態（缺一不可，皆為實測踩雷後修正）

| 旗標 | 為什麼 |
|---|---|
| `--no-parallel-tool-calls` | ★ gateway 對平行工具呼叫回 400，Inspect 預設 agent prompt 會鼓勵平行呼叫 → 整題記 error，會被誤讀成「難題解不動」 |
| `--message-limit 50` | 對齊 InterCode 上游預設；實測 30 時弱模型多題撞限＝量到預算不是能力 |
| `--max-tool-output 32768` | 大檔 dump 撐爆 context 會變成 `ModelGenerateError` |
| `--no-fail-on-error` | 單題失敗不中斷整批 |
| `--epochs 5` | 出 CI 的最低限度 |

## 實測到的方法論發現

皆有 log 佐證，是本專案認為比排行榜更值得寫的部分：

1. **Harness confound**：真 picoCTF forensics 題因沙箱缺 `steghide`/`xxd` 而**假性失敗**；補工具後同一模型分數上升。另一例是某 RSA 分解題在 `network_mode:none` 且未裝 GNFS 的沙箱中**根本無解**，六模型全滅看起來像「難題」，實際是設定造成——該題已排除計分。**分數會被 harness 左右，故組態必須固定並揭露。**
2. **基礎設施會系統性偏袒特定模型**：gateway 的 504 逾時只砸在 gemma 系（12b 22 次／26b 11／70b 5／8b 1／550b 0／30b 0），因為 gemma 單次生成又長又慢而撞上反向代理逾時。不翻 log 只看分數，會把「連話都沒說出口」誤讀成「能力較弱」。
3. **診斷速度要看 `working_time` 而非 `total_time`**：曾見 `total=307s` 但 `working=6.6s`——300 秒全在等 gateway 重試退避。共享 gateway 下多個 eval 併行取分會讓弱模型被吞吐餓死。
4. **「無解題」是最貴的題**：agentic 評測的牆鐘由「解不出來卻一直嘗試」的題主導，**越強的模型越慢**（會試更多攻擊法）。單一無解題可占整批牆鐘的 90%以上。時間成本不由題數決定。
5. **非確定性**：同題同模型不同次結果會變 → 每題 ≥5 次 + CI 是必要而非奢侈。
6. **解出 ≠ 走專家路徑**：實測到模型用等價異路（跳過 CRT 逐環運算）與非預期解（用 `file` 順手洩漏 comment 密碼，繞過預期的 `exiftool` 路徑）解題。**因此詞向量相似度不可當能力分**（會誤判有效的非預期解），只能用於解法路徑分群與 checkpoint 語意等價判定；客觀錨點（literal 中間值）才是穩的能力訊號，兩者並用。
7. **量測自身也會被污染**：模型 `cat` 出檔案會把原始碼字詞混進 transcript 造成假性 checkpoint 命中 → 抽取器只對模型 **authored**（自己寫的）內容計分。

## 誠實框定與限制

- **污染組屬已知且不可迴避的污染**：全部有公開 writeup，分數僅代表「已知污染下的領域覆蓋／工具使用／端到端成功率／粗略排名」，**不得**解讀為未見題泛化。
- **兩個分區的評分器不同**（`includes()` vs `exact_flag()`）。已做嚴格重算檢查、gap 完全保留（見上），但污染組的絕對數字仍應視為**上界**。
- **Frontier 錨點非同場競技**：Opus 4.8 走不同 scaffold，只作為「題目可解性」與路徑比對的上緣參考，不與 6 模型並列排名。
- **難度標籤為相對估計**、未跨來源校準；標籤來自題庫 metadata，**未驗證沙箱可解性**（發現 1 即此問題的後果）。
- **n=5 不足以支撐單格的精確主張**，只支撐聚合層級的方向性結論。

完整限制聲明見 [`ctf/DATA_PROVENANCE.md`](ctf/DATA_PROVENANCE.md) §5。

## 儲存庫結構

```
.
├── README.md                     ← 本檔（專案總覽）
├── docs/
│   ├── SETUP.md                  安裝與環境設定指南
│   └── REPORT_前置作業.md         前置作業技術報告（環境／踩雷全紀錄）
├── skills.md                     操作手冊 / 方法論參考（團隊可照跑）
├── smoke_test.py                 MCQ 冒煙測試（sec-smoke task）
├── requirements.txt              鎖定版本依賴
├── LICENSE                       MIT（僅涵蓋本專案自有創作）
├── THIRD_PARTY_NOTICES.md        第三方題目與工具的來源與授權標註
└── ctf/                          CTF agentic 評測主體
    ├── README.md                 迷你 CTF 評測（agentic + Docker 沙箱）說明
    ├── DATA_PROVENANCE.md        題目資料完整溯源（逐題出處／上游版本）
    ├── bench27/                  ★ 主題組
    │   ├── MANIFEST.json         27 題清單與 metadata
    │   ├── contaminated/         12 題（2022–2023）
    │   ├── recent2026/           12 題（2026 post-cutoff）
    │   ├── deep_hard/            3 題（多階段硬題）
    │   ├── bench27_runs.json     權威結果（803 有效樣本）
    │   ├── COST_TABLE.md         逐題 × 逐模型成本剖面（token／時間）
    │   ├── dashboard.html        單檔離線儀表板
    │   ├── agent_wp/             模型實際解題過程（27 題 × 各模型 × 5 epoch）
    │   ├── wp_27/                27 題標準解打包
    │   └── run_*.sh              各分區執行腳本
    ├── deep/                     深度題與 Cybench case study（推理路徑分析）
    └── _archive_20260726/        早期題組封存（Bench25 等，保留供溯源）
```

## 資料來源與第三方內容

本題組的 CTF 題檔與參考 writeup **多數並非本專案自製**，而是選自公開學術 benchmark（InterCode-CTF、Cybench）與公開 CTF 賽事歸檔（LACTF 2026、BYUCTF 2026 等）。所有第三方內容的出處、上游 repo 與授權條款見 **[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)** 與 **[`ctf/DATA_PROVENANCE.md`](ctf/DATA_PROVENANCE.md)**。各題原檔皆保留並標註來源。

## 授權

本專案**自有的**程式碼、評測設計、checkpoints 與文件以 **MIT** 授權（見 [`LICENSE`](LICENSE)）。
第三方 CTF 題檔與 writeup 各自受其上游授權／賽事條款約束，**不**在本專案的 MIT 授權範圍內——詳見 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

---

*AIS3 2026 AI 組專題 — 語言模型資安能力評量的方法設計。憑證（`.env`）永不進版控。*
