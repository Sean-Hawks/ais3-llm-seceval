# Contributing / 貢獻指南

## English

Start with [setup](docs/en/SETUP.md) and the [data dictionary](docs/en/DATA.md). Open an issue for a reproducibility failure, task/provenance correction or a proposed methodological change. Small documentation fixes can be submitted directly.

Before a pull request, run `make check`. With runtime dependencies installed, also run `python scripts/check_inspect.py` when changing loaders/scorers. CI performs offline checks; it does not call a paid model or prove container solvability.

- Update both language versions when changing reader-facing guidance.
- Preserve historical snapshots. New experiments go under `output/`; include settings, source hashes, raw-log selection and exclusions when proposing a new published snapshot.
- Distinguish scorer success, observed flag presence and process coverage. Never fill missing/failed attempts with selected successes.
- Add behavioral tests for scoring, identity/denominator changes or evidence extraction. Avoid asserting only implementation details.
- Keep third-party task sources, license text, changes and reference material distinguishable. Do not assume the root MIT license covers challenge assets.
- Do not commit `.env`, credentials, unrestricted raw logs or personal machine paths. See [security guidance](SECURITY.md).

A new task needs source/revision/redistribution status, a stable identity, metadata, evaluator-only target, permitted agent inputs, a tested sandbox, reference writeup and checkpoints. Updating only MANIFEST is insufficient: loaders, task mapping, experiment config, validation and reports must agree. Bench27 is intentionally a fixed 27-task snapshot; a larger suite should receive a distinct version.

## 繁體中文

先閱讀[操作指南](docs/zh-TW/SETUP.md)與[資料字典](docs/zh-TW/DATA.md)。重現失敗、題目來源修正或方法變更可先開 issue；小型文件修正可直接提交。

PR 前執行 `make check`。若變更 task loader／scorer，安裝 runtime 套件後再執行 `python scripts/check_inspect.py`。CI 不呼叫付費模型，也不能證明 Docker 題目可解。

- 主要說明變更需同步中英兩版。
- 保留歷史快照；新實驗放 `output/`。提議新的結果版本時附設定、來源雜湊、log 選擇與排除紀錄。
- 區分最終 scorer、軌跡 flag 與步驟覆蓋；不選擇性回填成功樣本。
- 評分、分母、ID 或抽取逻辑變更應補具體行為測試。
- 保留第三方來源、授權與改動說明；根目錄 MIT 不涵蓋所有題目。
- 不提交金鑰、`.env`、未清理 logs 或個人機器路徑。

新題須有來源／版本／散布依據、穩定 ID、metadata、僅評分端使用的答案、允許給 agent 的附件、已測試沙箱、參考解與 checkpoints。所有 loader／ID／設定／驗證／報告需同步；擴大固定 Bench27 應另立版本。
