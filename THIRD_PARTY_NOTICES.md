# Third-Party Notices / 第三方來源與授權標註

本專案的評測 **harness、題目選擇、checkpoint 設計、分析腳本與文件** 為自有創作，以 MIT
授權（見 [`LICENSE`](LICENSE)）。但為了**可重現性**，本儲存庫也**重新散布**了一部分並非
本專案自製的內容——CTF 題檔、官方／參考 writeup、以及所依賴的評測資料集。這些內容各自
受其上游授權與 CTF 賽事條款約束，**不**在本專案 MIT 授權範圍內。

本文件逐一標註來源。逐題出處（含上游 commit、資料檔、gold flag 欄位）另見
[`ctf/DATA_PROVENANCE.md`](ctf/DATA_PROVENANCE.md)。

> ⚠️ 授權標示以「請以上游 repository 的實際條款為準」為原則。下列若標「見上游」表示本專案
> 未逕自認定其授權；散布前若有疑義，應回上游確認或改以「連結＋下載腳本」方式引用。

---

## 1. 評測框架與工具（Tooling）

| 元件 | 上游 | 授權 | 用途 |
|---|---|---|---|
| **Inspect AI** (`inspect_ai`) | UK AI Safety Institute — <https://github.com/UKGovernmentBEIS/inspect_ai> | MIT | 評測 harness 骨幹 |
| **inspect_evals** | UK AISI — <https://github.com/UKGovernmentBEIS/inspect_evals> | MIT | 提供 `gdm_intercode_ctf`、`cybench` loader |
| 其他 Python 依賴 | 見 [`requirements.txt`](requirements.txt) | 各自授權 | z3-solver、pwntools 等 |

## 2. 評測資料集來源（Benchmark datasets）

### 2a. InterCode-CTF（`gdm_intercode_ctf`）
- **上游**：`princeton-nlp/intercode` — <https://github.com/princeton-nlp/intercode>（釘選 commit `c3e46d8…`，見 DATA_PROVENANCE）
- **相關論文**：Yang et al., *InterCode*（NeurIPS 2023）；GDM 版評測見 Phuong et al., *Evaluating Frontier Models for Dangerous Capabilities*, arXiv:2403.13793
- **底層題目**：**picoCTF**（Carnegie Mellon University / picoCTF）— <https://picoctf.org>
- **授權**：InterCode 程式碼 MIT；底層 picoCTF 題目版權屬 CMU/picoCTF，適用其使用條款。

### 2b. Cybench
- **上游**：`andyzorigin/cybench` — <https://github.com/andyzorigin/cybench>（Stanford 等）
- **底層題目**來自下列公開 CTF 賽事，各自版權與條款屬原賽事：

  | 賽事 | 主辦 |
  |---|---|
  | HackTheBox CTF | Hack The Box |
  | Google CTF (GCTF) | Google |
  | GlacierCTF | GlacierCTF 團隊 |
  | HKCERT CTF | 香港電腦保安事故協調中心（HKCERT） |
  | SEKAI CTF (2022 / 2023) | Project SEKAI |
- **授權**：Cybench 框架見其 repo；各題目請以原賽事之發布條款為準。

## 3. 近代（post-cutoff）CTF 題目來源

### 3a. LACTF 2026
- **上游**：`uclaacm/lactf-archive`，路徑 `2026/<category>/<name>` — <https://github.com/uclaacm/lactf-archive>
- **主辦**：UCLA ACM Cyber
- **內容**：題檔、`solve.py`、Dockerfile、flag 皆 commit 於該 repo。授權**見上游 repo**。
- 本專案用途：recent2026 分區 10 題（crypto/rev/pwn/web/misc）。

### 3b. BYUCTF 2026
- **上游**：`BYU-CSA/BYUCTF-2026` — <https://github.com/BYU-CSA/BYUCTF-2026>
- **主辦**：BYU Cyber Security Association
- **內容**：forensics 2 題共用 `GLaDOS_Network.pcapng`，flag 公開。授權**見上游 repo**。
- 本專案用途：recent2026 分區 forensics 2 題。

## 4. 本專案的自有貢獻（MIT 範圍內）

以下為本專案原創、確實屬 MIT 授權：

- 全部評測 harness / task 定義 / loader（`smoke_test.py`、`ctf/**/*.py`、`ctf/bench27/*_eval.py` 等）
- Bench27 的**題目選擇、分區設計、污染對照方法**
- 每題的 `checkpoints.json`（各階段標準解的 milestone／anchors／keywords 標註）
- 各題自撰的 `writeup.md`（本專案為評測而重寫的參考解；與上游官方 writeup 為不同著作）
- frontier 手解參考（`ctf/bench27/frontier_manual/`）、分析與儀表板腳本、全部 README／文件
- `ctf/` 內標示「自製」之題目（如 `ctf/README.md` 表列的 01–05 自製沙箱題）

## 5. 若要對外散布的建議

若日後將本 repo 公開散布，對第 2、3 節的第三方原始題檔，建議二擇一：
1. **保留原檔 + 本文件之標註**（現行做法；風險由散布者評估），或
2. 改為**移除原檔、改附上游連結與下載腳本**，僅保留本專案自有的 checkpoints／分析／writeup。

無論何者，`.env`（憑證）永不進版控。

---

*本標註依安裝環境內實際檔案與上游 metadata 逐項核對產出。授權細節以各上游 repository 為準。*
