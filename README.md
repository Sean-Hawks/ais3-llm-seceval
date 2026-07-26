# Inspect AI 冒煙測試

目標：用最小的例子，確認 Inspect 能連上 AIS3 的 endpoint 並跑完一次評測。

## 0. 跨環境需求（Linux / macOS / Windows）

- **Python 3.12–3.14**（3.14 可用，但某些套件在 3.14 可能還沒 wheel；裝不起來就退 3.12）。
- **Docker**：CTF agentic 評測（cybench / intercode / 自製沙箱）**一定要 Docker**，且容器都是 Linux image。
  - Linux：原生最順，直接裝 docker engine。
  - macOS：Docker Desktop。
  - Windows：**必須用 WSL2**——`.sh` 腳本與 Linux 容器在原生 PowerShell 跑不了，請在 WSL2 (Ubuntu) 裡 clone、建 venv、跑 Docker Desktop 的 WSL2 backend。
- **連得到 AIS3 gateway**：受測模型走 `.env` 裡的 OpenAI-compatible endpoint，換環境後要先確認網路到得了（這才是真正的移植關卡，跟 OS 無關）。

## 1. 裝環境（建議用 venv，別汙染系統 Python）

```bash
git clone <this-repo-url> && cd ais3-llm-seceval
python3 -m venv .venv
source .venv/bin/activate          # Windows(WSL2) 一樣用這行；純 PowerShell 是 .venv\Scripts\Activate.ps1
pip install -r requirements.txt    # 完整鎖定版本；只想跑 MCQ 冒煙可改 pip install inspect-ai
```

> Python 3.14 太新，萬一某個相依套件沒有 wheel 裝不起來，改用 3.12：
> `python3.12 -m venv .venv`（或 `brew install python@3.12`）。
>
> 依賴清單由 `pip freeze` 產生於 `requirements.txt`。`.env` **不會**進版控（含真實憑證），請 `cp .env.example .env` 後自行填。

## 2. 設定 endpoint

把 `.env.example` 複製成 `.env`，填入你的網址與 key：

```bash
cp .env.example .env
# 然後編輯 .env
```

- `AIS3_BASE_URL`：OpenAI-compatible 根網址，**通常要以 `/v1` 結尾**。
- `AIS3_API_KEY`：沒有驗證的話填 `dummy` 之類的非空字串即可。

## 3. 跑第一次

```bash
inspect eval smoke_test.py --model openai-api/ais3/ais3/llama-3.1-8b --limit 6
```

模型字串規則：`openai-api/<provider>/<model>`

- `<provider>` = `ais3`（對應 `AIS3_BASE_URL` / `AIS3_API_KEY` 這組前綴，名字自取）。
- `<model>` = **gateway 真正的模型 ID**，已確認是帶前綴的 `ais3/llama-3.1-8b`。
- 所以完整字串 `ais3` 會出現兩次：`openai-api/ais3/ais3/llama-3.1-8b`（前者是本地 provider 名，後者是 gateway 模型前綴）。這不是筆誤。

## 4. 看結果

```bash
inspect view
```

會開一個本機網頁，逐題看「輸入 / 模型輸出 / 對錯 / 分數」。這就是 Inspect 最好用的地方——每一題都可追。

## 5. 一次比較多個模型（你的 scaling 階梯）

```bash
for m in ais3/llama-3.1-8b ais3/gemma-4-12b ais3/gemma-4-26b ais3/nemotron-cascade-2-30b ais3/llama-3.3-70b ais3/nemotron-3-ultra-550b; do
  inspect eval smoke_test.py --model openai-api/ais3/$m --limit 6
done
inspect view
```

> `llama-guard-3-8b` 是安全分類器、不是對話模型，別放進這個 MCQ 迴圈——它之後要當「安全評分員」用。

## 疑難排解

- **連不上 / 401**：檢查 `AIS3_BASE_URL` 有沒有 `/v1`、key 是否正確。先用 `curl` 確認 endpoint 本身會回：

  ```bash
  curl $AIS3_BASE_URL/models -H "Authorization: Bearer $AIS3_API_KEY"
  ```

- **model not found**：`<model>` 字串要跟 gateway 完全一致（見步驟 3）。
- **看不到分數**：確認跑完沒報錯，再 `inspect view`。

---

跑通這個之後，下一步就是把 `smoke_test.py` 換成**對照配對**的漏洞偵測（有洞版 vs 修補版 + paired-correct 評分），那才是你們 BR-B 的「尺」。要我接著寫那一版跟我說。

---

# 專案結構總覽

```
inspect-test/
├── .env / .env.example        endpoint 設定（AIS3_BASE_URL / AIS3_API_KEY）
├── README.md                  ← 本檔（設定指南 + 結構總覽）
├── smoke_test.py              MCQ 冒煙測試（sec-smoke task）
├── skills.md                  筆記
├── logs/                      ★ inspect 預設輸出目錄（新 eval 都寫這裡，平面結構）
│   └── _archive/                已歸檔的過時 log（sec-smoke 冒煙、被取代的 ctf-deep）
└── ctf/                       CTF agentic 評測主體
    ├── ctf_eval.py            task 定義：ctf() / ctf_pico() / ctf_deep()
    ├── compose.yaml + Dockerfile   共用 Docker 沙箱（自製工具：strings/steghide/pwntools…）
    ├── analyze_by_year.py     讀 ../logs 做 2023/2026 污染 gap 分析
    ├── intuition.py           讀 ../logs 算 Intuition Index（II=100/中位步數）
    ├── challenges/            自製題 01–33（含硬題 30-33）→ ctf()
    ├── picoctf/{2023,2026}/   年份對照組 → ctf_pico()
    ├── bench25/               25 題全領域藍圖（規劃文件：manifest/inventory/run）
    ├── deep/                  深度題（推理路徑分析）
    │   ├── A-rsa-wiener/ B-z3-crackme/ C-stego-chain/   舊自製深度題 → ctf_deep()
    │   ├── deep.zip           ↑ 這三題的舊備份（可刪）
    │   └── cybench/           ★ cybench 真題 case study（見其 README）
    └── logs 由頂層 ../logs 統一存放（ctf/ 內不另存）
```

## 各 task 怎麼跑（都從 `inspect-test/` 跑才讀得到 `.env`）
| 指令 | 內容 |
|---|---|
| `inspect eval smoke_test.py` | MCQ 冒煙 |
| `inspect eval ctf/ctf_eval.py@ctf` | 自製題 01–33 |
| `inspect eval ctf/ctf_eval.py@ctf_pico` | picoCTF 年份對照組 |
| `inspect eval ctf/ctf_eval.py@ctf_deep` | 舊自製深度題 A/B/C（checkpoint 部分分） |
| `ctf/deep/cybench/run_and_writeup.sh <model>` | cybench 深度 case study（一鍵跑+匯出 writeup） |

## logs 的原則
`logs/` 是 inspect 原生輸出，**新 eval 一定會寫回這裡的平面結構**，所以刻意不切子資料夾（會被下次跑打散、且 `analyze_by_year.py`/`intuition.py` 用非遞迴 glob 讀）。只把明顯過時的挪進 `logs/_archive/`。
例外：cybench case study 的 log 獨立存在 `ctf/deep/cybench/logs/`，由它自己的腳本管理。
