# Companion step-analysis integration

[繁體中文](../zh-TW/COMPANION.md) · [Documentation](../README.md)

Slide 46 references both this repository and [YuCheng1122/ais-final](https://github.com/YuCheng1122/ais-final). This repository runs challenges and preserves trajectories; the companion structures and compares solution steps. Together they support the capstone. Keep explicit interfaces and revisions when maintaining separate repositories.

Read-only inspection on 2026-09-19 used companion revision `9a1a2af87c938a3e2d9ac4af7ba4fb318b26bc36`. **It has not been confirmed as the slide-producing revision.**

## Available components

| Component | This repository | Companion |
|---|---|---|
| Tasks, Docker, Inspect harness | Provided | Not the execution entry point |
| Flag results, costs, trajectory exports | Provided | Uses its own imported/extracted versions |
| Checkpoints/references | Provided | Separate `ctf-step` reference JSON |
| Extraction prompt/schema | No model extraction pipeline | `Dataset/PROMPT.md` |
| Anchor scoring | Historical pilot only | `src/anchor_match.py`, `src/score_steps.py` |
| Semantic similarity | No embedding pipeline | Qwen3-Embedding-0.6B, exploratory |
| Interactive process report | Historical flag dashboard | `src/render_table.py` |

These roles were checked against the [pinned README](https://github.com/YuCheng1122/ais-final/blob/9a1a2af87c938a3e2d9ac4af7ba4fb318b26bc36/README.md) and [methodology](https://github.com/YuCheng1122/ais-final/blob/9a1a2af87c938a3e2d9ac4af7ba4fb318b26bc36/src/METHODOLOGY.md). Extraction/embedding were not rerun during this update.

## Interface contract

1. Use the generated [catalog](../../results/TASK_CATALOG.md) for `C/R/D` IDs; retain `(task, model, epoch)` throughout joins.
2. Label reference and agent material separately. Agents receive only prompts and permitted assets, never reference solutions or evaluator targets.
3. Export new attempts with `python -m ais3_bench export`. Its authored JSONL and audit preserve evidence; they are **not directly compatible with ctf-step JSON**.
4. To reproduce existing figures, first rescore the companion's existing JSON with its documented environment. Unversioned re-extraction can change denominators.
5. For new transcripts, apply the original extraction prompt and retain source hashes, extractor model revision, complete prompt, parameters, failures and human review.
6. Align scorer C/I, `flag_status`, and reference-step coverage before comparing figures.

## Reconciliation still required

This snapshot has 803 primary attempts and 131 frontier attempts. The companion documents 942 valid extracted agent-run JSON files and three excluded errors. **803+131 and 942 cannot be assumed to be the same batch.** Obtain input manifests and exclusion records, especially treatment of zero-generation attempts.

The companion uses literal anchors to decide reached-ness and embeddings only for semantic context. Anchor thresholds, loose matching and generic tokens still need false-positive validation against human annotations.

This update links to the companion without vendoring its code or data. A later merge should establish contributor permission, licensing, an agreed revision and compatible definitions; this repository's MIT license cannot automatically relicense companion material.
