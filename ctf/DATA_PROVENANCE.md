> **Historical document / 歷史文件**：本檔主要描述 Bench25。現行 Bench27 請見 [task catalog](../results/TASK_CATALOG.md) 與 [data dictionary](../docs/en/DATA.md)。舊文的污染推論不代表已查證訓練資料。

# 題目資料來源溯源（24 + 3）

本文件說明本專案兩套受測題目——**廣度 benchmark（Bench25，計分 24 題）** 與
**深度 case study（3 題）**——的完整出處、上游版本與可重現資訊。所有欄位皆由
安裝環境內的實際檔案逐題核對，非依記憶或二手描述填寫。

> 一句話定位：**兩套題目都不是本專案自製，而是從兩個公開學術 benchmark 的安裝副本中選出。**
> 題目皆有公開題面／writeup，屬**已知污染**，僅用於領域覆蓋度、工具使用與粗略排名；
> 抗污染泛化不由此套題主張（另以自製私有題＋對照配對處理）。

---

## 1. 上游來源與版本（可重現性）

| 項目 | 值 |
|---|---|
| 評測框架 | Inspect AI（`inspect_ai`）`0.3.249` |
| 題庫套件 | `inspect_evals` `0.16.0` |
| 來源 A | **`gdm_intercode_ctf`**（InterCode-CTF，GDM 版） |
| 來源 A 上游 repo | `princeton-nlp/intercode` |
| 來源 A 釘選 commit | `c3e46d827cfc9d4c704ec078f7abf9f41e3191d8` |
| 來源 A 資料檔 | `ic_ctf.json`（100 題，過濾 22 題需連網者 → **78 題可用**） |
| 來源 A 論文 | Phuong et al., *Evaluating Frontier Models for Dangerous Capabilities*, arXiv:2403.13793 |
| 來源 B | **`cybench`**（Cybench） |
| 來源 B 題數 | 39 題，來自 4 個 CTF 賽事（見 §4） |
| 來源 B 每題 metadata | `challenges/<name>/eval.yaml` 內 `competition` / `category` / `first_solve_time` |

**InterCode 78 題的由來**：`ic_ctf.json` 原有 100 題，本實作排除 22 題需連網者
（id：1, 7, 9, 14, 16, 20, 28, 29, 35, 39, 41, 42, 43, 54, 57, 62, 66, 73, 87, 88, 89, 95），
餘 78 題。此排除清單與 GDM 論文略有差異（GDM 共排 26 題），差異已記錄於
`dataset.py` 註解。**全部 78 題皆為 picoCTF 題目。**

---

## 2. 廣度 benchmark：24 題逐題出處

Bench25 原選 25 題；`intercode/12` 因沙箱限制（`network_mode:none` 且未裝 GNFS
分解工具）導致六模型全滅，屬**設定造成非能力問題**，已自計分移除 →
**計分分母為 24**。下表仍列出該題並標記為「排除計分」以保完整。

### 2a. InterCode 來源（picoCTF，逐題 source URL 已核對）

| Bench ID | 領域 | 難度 | 上游來源 | 原始出處 URL |
|---|---|---|---|---|
| `intercode/5` | crypto | 易 | picoCTF 2019 | https://github.com/kevinjycui/picoCTF-2019-writeup/blob/master/Cryptography/13/README.md |
| `intercode/12` | crypto | 易 | picoCTF | https://play.picoctf.org/practice/challenge/162 ⚠️**排除計分** |
| `intercode/44` | rev | 易 | picoCTF | https://play.picoctf.org/practice/challenge/7 |
| `intercode/94` | forensics | 易 | picoCTF | https://play.picoctf.org/practice/challenge/44 |
| `intercode/3` | forensics | 中 | picoCTF | https://play.picoctf.org/practice/challenge/51 |
| `intercode/37` | misc | 易 | picoCTF | https://play.picoctf.org/practice/challenge/320 |

> URL 與 gold flag 取自 `ic_ctf.json` 每題的 `source` / `gold` 欄位。實際執行讀取
> 已安裝 dataset 的 artifact 與 `Sample.target`，**不依賴來源網站提供 flag**。

### 2b. cybench 來源（19 題，賽事與 first-solve-time 已核對）

`first_solve_time`（FST，單位：分鐘）為 Cybench 官方記錄之人類首解時間，本專案僅
將其作為難度**參考**，非官方校準難度。

| Bench ID | 領域 | 難度 | 賽事（competition） | FST(min) |
|---|---|---|---|---:|
| `cybench/slcg` | crypto | 中 | GlacierCTF | 29 |
| `cybench/partial_tenacity` | crypto | 難 | HackTheBox | 65 |
| `cybench/permuted` † | crypto | 難 | HackTheBox | 42 |
| `cybench/robust_cbc` | crypto | 難 | SEKAI CTF 2022 | 1494 |
| `cybench/packedaway` | rev | 易 | HackTheBox | 6 |
| `cybench/crushing` | rev | 中 | HackTheBox | 20 |
| `cybench/rpgo` | rev | 中 | GlacierCTF | 45 |
| `cybench/sop` | rev | 難 | GlacierCTF | 51 |
| `cybench/eval_me` | forensics | 中 | SEKAI CTF 2023 | 11 |
| `cybench/data_siege` | forensics | 難 | HackTheBox | 78 |
| `cybench/avatar` | misc | 中 | GlacierCTF | 84 |
| `cybench/unbreakable` | misc | 中 | HackTheBox | 123 |
| `cybench/just_another_pickle_jail` † | misc | 難 | SEKAI CTF 2023 | 244 |
| `cybench/flag_command` | web | 易 | HackTheBox | 6 |
| `cybench/back_to_the_past` | web | 中 | HKCERT CTF | 32 |
| `cybench/labyrinth_linguist` | web | 中 | HackTheBox | 43 |
| `cybench/chunky` | web | 難 | SEKAI CTF 2023 | 105 |
| `cybench/delulu` † | pwn | 中 | HackTheBox | 75 |
| `cybench/network_tools` | pwn | 難 | SEKAI CTF 2023 | 42 |

† 同時為 §3 的深度題。
賽事名稱取自各題 `eval.yaml` 的 `metadata.competition`：SEKAI 題的年份直接編碼於
metadata（`Sekai-2022` / `Sekai-2023`）；HackTheBox / Glacier / HKCERT 在本地 metadata
**未編碼年份**（僅賽事名），故本表對這三者不標年份。

### 2c. 24 題來源分布小結（計分題，已排除 intercode/12）

- 依上游：InterCode/picoCTF **5 題**、cybench **19 題**。
- cybench 19 題依賽事：HackTheBox 9、GlacierCTF 4、SEKAI CTF 2023 4、SEKAI CTF 2022 1、HKCERT 1。

---

## 3. 深度 case study：3 題出處

3 題全取自 **cybench 真題**（附 writeup + `solve.py` + flag + 多階段 Docker 環境），
用於「推理路徑 vs 專家解法」的深度軌跡分析。

| 題目 | 賽事 | 領域 | FST(min) | 考點 |
|---|---|---|---:|---|
| `permuted` | HackTheBox | crypto | 42 | 置換群 Sₙ 上的 DLP：循環分解 + CRT 回復 DH 指數與 AES 金鑰 |
| `delulu` | HackTheBox | pwn | 75 | format string 位置參數 `%hn` 精準覆寫關鍵區域變數 |
| `just_another_pickle_jail` | SEKAI CTF 2023 | misc | 244 | 手工組 pickle opcode、劫持 Unpickler 狀態逃逸 jail 達成 RCE |

上游解答位於 `.venv/.../inspect_evals/cybench/challenges/<name>/solution/`。
checkpoint 設定於 `ctf/deep/cybench_checkpoints/<name>.json`（每題 6 階段：milestone
語意文字 + anchors 客觀錨點）。

> **重要重疊說明**：這 3 題**是 §2b 那 19 題 cybench 的子集**（`permuted`、`delulu`、
> `just_another_pickle_jail`），不是另外 3 個新來源。深度線是把它們**再拿去做多階段
> 軌跡分析**，因此「24 + 3」中的 3 與 24 有集合重疊，報告中須明確聲明避免誤讀成 27 個獨立來源。

---

## 4. Cybench 四個賽事來源（供背景引用）

本安裝的 cybench 39 題依 `competition` 欄位分屬：

| 賽事 | 說明 |
|---|---|
| HackTheBox | HTB 舉辦之 CTF 題目 |
| SEKAI CTF | 分 2022、2023 兩屆（metadata 有年份） |
| GlacierCTF | GlacierCTF 賽事題目 |
| HKCERT CTF | 香港 HKCERT 舉辦之 CTF |

---

## 5. 嚴謹性與限制聲明（寫入報告時務必保留）

1. **污染屬已知且不可迴避**：24 + 3 題全有公開題面／writeup，模型訓練資料極可能
   已見。分數僅代表「在已知污染下的領域覆蓋 / 工具使用 / 端到端成功率 / 粗略排名」，
   **不得**解讀為未見題泛化或抗污染推理能力。
2. **評分器為子字串比對（上界）**：cybench 與 gdm_intercode_ctf 皆使用 `includes()`
   子字串評分（`cybench.py` / `gdm_intercode_ctf.py`），此為本專案已於自製題淘汰的
   作弊面評分器。故 Bench25 分數是**能力上界**，且**不可與自製題的 `exact_flag`
   結果並列比較**。
3. **難度標籤非官方校準**：難度為依 `first_solve_time`、解題鏈長與工具需求所做的
   相對估計，兩來源間並未共同校準；且 inventory 難度標籤未驗證沙箱可解性
   （`intercode/12` 即為此類 harness confound）。
4. **pwn 僅 2 題為來源限制非疏漏**：兩來源合計僅 2 題真 pwn（InterCode ID 91 雖標
   Binary Exploitation，實為模 37 字元映射，未硬湊）。
5. **可重現前提**：結果綁定 `inspect_ai 0.3.249` / `inspect_evals 0.16.0` /
   InterCode commit `c3e46d8…`；升級套件或更換 commit 可能改變題目集合與行為。

---

*本文件由安裝環境檔案逐題核對產出（`ic_ctf.json` 的 `source`/`gold` 欄位、
cybench 各題 `eval.yaml` 的 `metadata`）。對應機器可讀清單見
[bench25/manifest.json](bench25/manifest.json)，完整 117 題盤點見
[bench25/inventory.md](bench25/inventory.md)。*
