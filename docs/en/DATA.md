# Data dictionary and provenance

[繁體中文](../zh-TW/DATA.md) · [Documentation](../README.md)

Paths below are relative to the repository root. Offline snapshot analysis does not read `.env`.

| File | Role | Reproduction |
|---|---|---|
| `ctf/bench27/MANIFEST.json` | Task identity, source, arm, target and difficulty | Benchmark definition, not inferred from results |
| `configs/bench27.json` | Model aliases and new-run defaults | Maintained configuration; changes define new conditions |
| `ctf/bench27/bench27_runs.json` | 803 committed flag-scored attempts | Original evidence requires corresponding raw logs |
| `ctf/bench27/bench27_cost.json` | Matching 803 token/time records | Requires raw logs; tokens are not currency |
| `ctf/bench27/opus_runs.json` | Frontier aggregate from a different scaffold | Requires per-run evidence and an agreed version |
| `ctf/bench27/*/*/checkpoints.json` | Reference stages and anchors | Research annotations, not derivable from flag scores |
| `ctf/bench27/agent_wp/` | Human-readable exported trajectories | May be truncated; not a substitute for full `.eval` |
| `ctf/bench27/wp_27/` | Packaged reference writeups | Derived research material with distinct upstream terms |
| `ctf/bench27/snapshot_audit.json` | Sanitized retrospective audit of 30 local raw logs | Requires originals; publishes only IDs, statuses and hashes |
| `results/` | Bilingual reports, summary and catalog | Rebuild with `python -m ais3_bench report` |
| `output/` | New runs, exports and scratch | Ignored by Git |

## Run schema

Primary key: `(arm, task, model, epoch)`. Preserve task IDs as strings, including numeric-looking InterCode IDs.

| Field | Meaning |
|---|---|
| `model` / `model_full` | Local alias and historical label, not proof of weight revision |
| `arm` | contaminated / recent2026 / deep_hard |
| `task` | Normalized Inspect sample identity; join through the catalog |
| `epoch` | Repetition within a run, historically 1–5 |
| `scorer` / `score_value` | Actual scorer and C/I result |
| `solved` | Scorer success, not flag occurrence in a transcript |
| `target_flag` | Evaluator answer; must not be supplied to the model. CTF flags are not API credentials |
| `submitted` | Historical export truncated at 400 characters; insufficient alone to establish a full strict-rescoring audit |
| `flag_in_submission` / `flag_in_transcript` | Historical case-insensitive substring diagnostics, not the scorer |
| `working_time` / `total_time` | Seconds; one negative working-time anomaly; total time is not experiment wall-clock |
| `log_file` | Original filename; `.eval` files are not distributed in a public clone |

New exports retain full submissions, use case-sensitive flag diagnostics, and include an audit plus authored JSONL. These improvements do not rewrite the historical snapshot.

## Checkpoint schema

Task fields: `challenge`, `category`, `flag`, `n_checkpoints`, `checkpoints[]`. Stage fields: `id`, `stage`, `depends_on`, `milestone`, `anchors`, `expert_action`, `keywords`. Ordering is a reference, not a hard constraint on valid alternatives. Some `source_of_truth` values are historical installation paths rather than portable URLs.

A task can have three identities: manifest directory, Inspect sample ID, and analysis ID (`C01_…`, `R01_…`, `D01_…`). The generated [catalog](../../results/TASK_CATALOG.md) joins them using manifest and frontier ID mappings.

## Evidence preservation

`summary.json` records source SHA-256 values, seven missing identities and the negative-time anomaly. The raw-log audit verifies all 803 rows and seven exclusions without publishing messages or endpoint details. Hashes detect snapshot changes but cannot establish historical environment integrity. Historical exporters used varying deduplication policies; maintained reporting uses the committed 803 rows instead of reselecting old logs.

The original [provenance document](../../ctf/DATA_PROVENANCE.md) primarily covers Bench25; it is not a complete authoritative Bench27 catalog. Cross-check the new catalog against task sources and [third-party notices](../../THIRD_PARTY_NOTICES.md).
