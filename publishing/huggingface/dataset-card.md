---
pretty_name: AIS3 Bench27 — LLM CTF Evaluation Outcomes
language:
- en
- zh
license: mit
size_categories:
- n<1K
task_categories:
- other
tags:
- ais3
- cybersecurity
- ctf
- llm-evaluation
- reproducibility
- tabular
configs:
- config_name: attempts
  default: true
  data_files:
  - split: observations
    path: data/attempts.jsonl
- config_name: tasks
  data_files:
  - split: catalog
    path: data/tasks.jsonl
- config_name: exclusions
  data_files:
  - split: audit
    path: data/exclusions.jsonl
---

# AIS3 Bench27

### Auditable outcomes of language-model agents solving CTF challenges

**AIS3 2026 AI Track Best Project Award · AI 組最佳專題**

[GitHub project](https://github.com/Sean-Hawks/ais3-llm-seceval) · [Research brief](https://github.com/Sean-Hawks/ais3-llm-seceval/blob/v0.1.0/docs/en/RESEARCH_BRIEF.md) · [Recognition](https://github.com/Sean-Hawks/ais3-llm-seceval/blob/v0.1.0/RECOGNITION.md) · [繁體中文](#繁體中文)

**27 tasks · 6 historical model labels · 803 retained attempts · 7 documented exclusions**

What can a failed CTF attempt tell us about an agent's capabilities? The broader project studies final flag correctness alongside reference steps in recorded solution trajectories. This dataset releases the **final-outcome measurements and task index** for its main experiment. Reference checkpoints and the companion process-analysis pipeline are linked from GitHub; process-score matrices are not included in this dataset.

The July 2026 experiment covers cryptography, reverse engineering, forensics, miscellaneous, web and binary exploitation tasks. Its three cohorts contain 12 older public tasks, 12 tasks from 2026, and three difficult case studies. Five attempts per task/model were planned: 810 slots, of which 803 appear in the validated result snapshot.

The source is the GitHub [v0.1.0 release](https://github.com/Sean-Hawks/ais3-llm-seceval/releases/tag/v0.1.0), commit `4ed7dc917012de50f0aa0f07c1de1838175b811c`. This is a field-limited projection of that release, preserving the retained scores and times. All 803 rows were retrospectively checked against 30 local raw logs; the seven exclusions comprise three sample errors and four zero-generation samples. Sixty attempts from superseded batches are outside this snapshot.

## Explore and load

Select a configuration in the viewer: **attempts**, **tasks** or **exclusions**. They have different schemas and are joined using `(arm, task)`; attempt identity is `(arm, task, model, epoch)`.

```python
from datasets import load_dataset

attempts = load_dataset("__DATASET_ID__", "attempts", split="observations")
tasks = load_dataset("__DATASET_ID__", "tasks", split="catalog")
exclusions = load_dataset("__DATASET_ID__", "exclusions", split="audit")

print(len(attempts), len(tasks), len(exclusions))  # 803, 27, 7
```

For an exact replication, pass the same published Hub commit as `revision=` to all three calls. This dataset is an archive of evaluation observations, not a randomized training/test split or a standalone executable challenge environment.

## Outcome snapshot

![Bench27 outcome comparison](figures/outcomes.png)

Left: tasks solved at least once over the available repetitions. Right: successful/valid attempts in each temporal cohort. Model labels are historical experiment labels; provider routing and exact model revisions remain unresolved. Frontier results from a different scaffold are excluded.

| Historical model label | Tasks solved at least once / 27 |
|---|---:|
| nemotron-3-ultra-550b | 15 |
| gemma-4-26b | 14 |
| gemma-4-12b | 12 |
| nemotron-cascade-2-30b | 10 |
| llama-3.3-70b | 7 |
| llama-3.1-8b | 4 |

This is observed task coverage, not single-attempt accuracy or an unbiased pass@5 estimate. Repeated attempts share tasks and are not independent benchmark items.

## Fields

| Configuration | Fields and interpretation |
|---|---|
| `attempts` | `arm`, `task`, `model`, `epoch`: identity; `model_full`: historical label; `scorer`, `score_value`, `solved`: original flag outcome (`C`/`I`, boolean); `working_time`, `total_time`: seconds; `input_tokens`, `output_tokens`, `total_tokens`, `assistant_msgs`: recorded usage; `analysis_id`, `category`, `difficulty`: task join; `working_time_anomaly`: flags known negative telemetry |
| `tasks` | `arm`, `task`, `analysis_id`, `category`, `difficulty`, `source`, `historical_year_label`, `reference_url`; links are pinned to the source commit |
| `exclusions` | `arm`, `task`, `model`, `epoch`, `status`; excluded slots are not included in the valid-attempt denominator |

Task IDs are strings, including numeric-looking InterCode IDs. Historical arm `contaminated` means the older-public-task cohort; it is **not verified training contamination**. Difficulty labels are historical annotations, not calibrated difficulty measurements. The negative `working_time=-1340.8` observation remains present and flagged; exclude it from working-time/throughput analyses. Summing `total_time` yields overlapping sample time, not experiment wall-clock time or monetary cost.

`provenance.json` contains source hashes, counts and the export policy. `SHA256SUMS` fingerprints this package. Raw logs, submissions, target flags, challenge binaries, service code and complete writeups are not part of the Hub export.

## Intended use and limitations

- Suitable for descriptive outcome analysis, teaching evaluation methodology and reproducing the project's reported task coverage.
- Cohorts differ in category composition and scorers. Older/2026 differences cannot establish causal effects of training contamination.
- Historical `includes` and custom `exact_flag` scorers are preserved. These rows have not been uniformly rescored with a new strict scorer.
- Missing attempts are explicit; smaller denominators must remain visible. Do not silently count exclusions as ordinary failures or replace them with older successful attempts.
- Task size is small, model revisions are not independently established, and the same scaffold was not used for the separate frontier reference.
- Process heatmaps, extraction reliability, alternative solutions and human-calibrated step scores require additional evidence. See the [claim–evidence ledger](https://github.com/Sean-Hawks/ais3-llm-seceval/blob/v0.1.0/docs/en/CLAIMS.md).
- JSONL rows are passive records. Executing the original CTF tasks requires the GitHub environment and its sandbox setup.

## Provenance, license and citation

Sources include InterCode/picoCTF, Cybench and its upstream events, LACTF 2026 and BYUCTF 2026. Each task retains a source label and a pinned reference link. The Hub package contains project measurements, factual metadata and documentation under the project's MIT scope; this does not relicense the referenced third-party challenges. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Authors, in presentation order: **陳威翰、林禹丞、洪軾洋、張宸瀚**. Cite the source software with [CITATION.cff](CITATION.cff) or [CITATION.bib](CITATION.bib), and add this dataset ID and the exact Hub revision used. The award record follows the team's report and linked participant account. This artifact makes no claim of peer-reviewed publication.

Questions and corrections can be filed in the [source repository](https://github.com/Sean-Hawks/ais3-llm-seceval/issues). This snapshot is versioned; corrections should preserve the original evidence and explain their effect on denominators and conclusions.

## 繁體中文

本資料集來自 **AIS3 2026 AI 組最佳專題**，專題研究語言模型解 CTF 時的最終結果與中間步驟。本次 Hugging Face 發布範圍為**主實驗的結果與題目索引**；參考 checkpoints、writeup 及隊友的步驟分析流程由 GitHub 連結提供，未將步驟分數或熱圖補寫成已驗證資料。

資料包含 27 題、6 個歷史模型標籤、803 筆有效嘗試，以及 7 筆排除紀錄。來源固定為 GitHub v0.1.0；803 筆分數與時間已與本機 30 份 raw logs 回溯核對，3 筆 sample error 與 4 筆零生成另外列出，60 筆較舊批次不屬於這個快照。

### 使用方式

上方檢視器可切換 `attempts`（803 筆）、`tasks`（27 筆）與 `exclusions`（7 筆）。前面的 `load_dataset` 範例可直接使用；要固定研究版本，三次讀取皆加入相同的 Hub commit 作為 `revision=`。`observations`／`catalog`／`audit` 表示資料角色，不代表隨機切分的訓練與測試集合。

以 `(arm, task)` 連接題目表；以 `(arm, task, model, epoch)` 識別嘗試。`C`／`I` 和 `solved` 保留原始 flag 評分，token 與訊息數是歷史用量紀錄。時間單位為秒；已知負 working time 保留並標記，不能直接用來比較速度。

### 研究解讀

圖表區分「最多五次有效嘗試中至少解出一次的題數」與「有效嘗試成功率」。兩者分母不同。`contaminated` 是舊題組的歷史名稱，不代表已證明訓練污染；兩個年份組的題型組成與評分器也不同。803 筆嘗試不是 803 個獨立題目，模型標籤也不代表已確認供應商 revision。

這份資料適合驗算描述性結果及研究評測方法，尚不能單獨支持因果污染結論或能力總排名。Frontier 使用不同 scaffold，沒有混入此資料集。缺少的正式步驟圖表、模型版本與人工校準資訊，見[待補資料](https://github.com/Sean-Hawks/ais3-llm-seceval/blob/v0.1.0/docs/zh-TW/EVIDENCE_GAPS.md)。

### 發布範圍與引用

此包未包含原始對話、模型提交、目標 flag、第三方題檔或服務程式。`provenance.json` 與 `SHA256SUMS` 提供來源及檔案雜湊；MIT 僅適用本專題原創部分，不替上游題目重新授權。

作者依簡報順序為陳威翰、林禹丞、洪軾洋、張宸瀚。請使用附帶的 CFF／BibTeX 引用原始專題，並另外註明這份資料集的 ID 與版本。完整方法、環境與貢獻方式見[繁體中文首頁](https://github.com/Sean-Hawks/ais3-llm-seceval/blob/v0.1.0/README.zh-TW.md)。
