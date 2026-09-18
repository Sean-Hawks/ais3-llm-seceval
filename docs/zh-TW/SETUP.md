# 安裝、驗證與重現

[English](../en/SETUP.md) · [文件導覽](../README.md)

## 1. 先選擇需要的層級

| 目的 | 需求 | 能重現什麼 |
|---|---|---|
| 閱讀／重建快照 | Python 3.10+，標準函式庫 | 本 repo 的成功率、分母、題目索引 |
| 匯出新的原始紀錄 | Inspect AI 套件、本機 `.eval` | 結果 JSON、排除紀錄、模型 authored 文字 |
| 重新跑模型 | Python 環境、Docker、自己的模型 endpoint／金鑰 | 新一輪 CTF 實驗，結果不保證相同 |
| 重建簡報步驟分析 | 隊友 repo、釘選資料版本、抽取／評分設定 | 見[串接指南](COMPANION.md)，不是單靠本 repo 即可 |

Linux、macOS 可使用以下指令；Windows 的 shell 腳本建議在 WSL2 中執行。Docker 容器使用 Linux。Python 3.12 適合作為評測環境起點；原實驗環境記錄為 Python 3.14。套件與容器建置仍需依平台驗證。

## 2. 離線檢視

```bash
git clone https://github.com/Sean-Hawks/ais3-llm-seceval.git
cd ais3-llm-seceval
python3 -m ais3_bench validate
python3 -m ais3_bench report --check
python3 -m unittest discover -s tests -v
python3 scripts/check_docs.py
```

`validate` 會檢查 27 題的 metadata、checkpoint 相依關係、本地附件、樣本唯一性、flag 對應及成本資料 join。它不會驗證每題在 Docker 裡一定可解，也不會把舊資料中的已知負時間偷偷修正。

`report --check` 不寫檔；移除 `--check` 即可重建 `results/`。歷史儀表板可直接在本機瀏覽器開啟 `ctf/bench27/dashboard.html`；GitHub 原始檔頁面不會執行 HTML。

## 3. 評測環境

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

在 `.env` 填自己的 `AIS3_BASE_URL` 與 `AIS3_API_KEY`。範例 endpoint 是佔位值，不是真實服務。Inspect 會從 repo 根目錄讀取 `.env`；請從根目錄執行。若已有 `.env`，直接編輯它，不要用範例覆寫。

`requirements.txt` 是評测所需的直接套件版本；`requirements-research.txt` 保存原實驗的完整 `pip freeze`，**不是跨平台 lockfile**。離線分析不需安裝任何套件。沒有把所有解題套件裝在 host：挑戰用工具應由 Docker 映像提供。

```bash
python -m ais3_bench doctor --evaluation
inspect eval smoke_test.py --model openai-api/ais3/ais3/llama-3.1-8b --limit 1
```

`doctor` 只讀套件版本與 Docker 狀態，不讀取或顯示金鑰、不聯絡模型。冒煙測試才會真的呼叫一次模型。模型 ID 由你的 gateway 決定；`openai-api/<provider>/<remote-model-id>` 中第一個 `ais3` 對應環境變數，第二個是原實驗 gateway 的模型前綴。如果遠端 ID 沒有前綴，可使用：

```bash
python -m ais3_bench run --arm recent2026 --model 8b --model-prefix openai-api/ais3/
```

## 4. Docker 與執行

先啟動 Docker Desktop、OrbStack 或 Docker Engine。映像建置可能需要網路；執行時，靜態題共用沙箱採 `network_mode: none`，六個自訂服務題採內部網路讓 agent 只連題目 victim。新隔離設定是本次改善，不能回推原始實驗已完全斷網。上游 InterCode/Cybench 的 compose 由其套件管理。已安裝 Cybench 的 Docker 警語明示允許上網；本次不修改上游套件，因此不能把六題的內部網路設定推廣成全題組斷網保證。

```bash
docker compose -f ctf/compose.yaml build
# 預覽單一模型的一個分區
python -m ais3_bench run --arm recent2026 --model 8b
# 實際執行；預設五次
python -m ais3_bench run --arm recent2026 --model 8b --execute
```

全部 27 題、6 模型的計畫：

```bash
python -m ais3_bench run --arm all --model all
```

Cybench 要求 `CYBENCH_ACKNOWLEDGE_RISKS=1`；閱讀上游執行要求並準備隔離環境後再自行設定。新入口不會暗自替你設定。`--execute` 會開始模型呼叫。`--epochs 1` 適合短程診斷，但不可與五次的歷史成績混為同一實驗。

新執行目錄自動命名為 `output/runs/<UTC時間>/`，內含實際指令 `commands.txt` 與各分區 `.eval`。也可 `--log-dir output/runs/my-experiment` 指定不存在的目錄；存在即拒絕，避免混跑。模型與批次按順序執行，但每個 Inspect 任務內的 `max_samples` 仍允許設定的樣本併行。

`run_contaminated.sh`、`run_recent2026.sh`、`run_deep_hard.sh` 現在是相容入口，預設僅預覽。舊 `run_recent2026.sh all` 參數已由 `--arm recent2026 --model all` 取代。`run_overnight_5ep.sh` 與重跑／Frontier 工具為歷史用途，不是新的正式入口。

## 5. 匯出新的實驗

```bash
python -m ais3_bench export --logs output/runs/my-experiment --output output/export/my-experiment
```

輸出 `runs.json`、`audit.json`、`authored.jsonl`。同一題／模型有多個 log 時，依 Inspect ISO 時間檔名先選**最新一整次 run**，再剔除 error、零生成或不支援評分的樣本，舊成功不會填回新 run 的失敗空洞。此規則是機械選擇規則，不能取代事先定義的實驗納入策略；正式發表請指定不可變的 log 清單。

空目錄、無有效樣本、未知題號、損毀 log 或既有輸出目錄都會拒絕寫入。不要用新的匯出直接覆蓋 `ctf/bench27/bench27_runs.json`。新的自訂模型別名須同步更新設定；這個匯出器只接受設定中的模型。

## 6. 常見問題

| 症狀 | 檢查 |
|---|---|
| Docker daemon unavailable | 啟動容器引擎後再跑 `doctor --evaluation` |
| 401／模型不存在 | 本地檢查 endpoint、API key 與 gateway 真正模型 ID；不要貼出金鑰 |
| 平行工具呼叫 400 | 保留 `--no-parallel-tool-calls` |
| 一直等／504 | 檢查重試與 gateway；區分 sample total time、working time 與零生成 |
| `ModuleNotFoundError` 在沙箱內 | 補 Docker 工具並建立**新條件的實驗**，不要假裝是純模型差異 |
| ARM 上 pwn 失敗 | 此兩題有 x86-64 socat 版本，需模擬支援；與上游 nsjail 不是完全相同 scaffold |
| 無法解 Coppersmith／QR | 目前映像不保證完整 SageMath、QR 工具；見方法限制，需驗證工具可得性 |

設定說明依本地 Inspect 安裝版本核對；CLI 定義可查[官方選項](https://inspect.aisi.org.uk/options.html)，內部網路語義可查 [Docker 官方文件](https://docs.docker.com/reference/compose-file/networks/#internal)。

## 原始紀錄回溯核對

主實驗 logs 已在本機核對；公開 clone 不包含原始 logs。若持有同一批檔案，可產生只含雜湊／識別碼的 audit：

```bash
python scripts/audit_snapshot.py --logs logs/bench27 --output output/snapshot_audit.json
```
