# Research brief

[繁體中文](../zh-TW/RESEARCH_BRIEF.md) · [Project](../../README.md) · [Claim–evidence ledger](CLAIMS.md)

**AIS3 LLM Security Evaluation: Writeup-based analysis of CTF solution trajectories**

AIS3 2026 AI2 project team · [Best Project Award, AI Track](../../RECOGNITION.md)

## Abstract

Final flag correctness is an objective outcome for capture-the-flag evaluations, but it does not explain the intermediate progress made by unsuccessful agents. This project studies a complementary view: align recorded solution trajectories with stages derived from reference writeups, while keeping literal evidence, semantic similarity and final outcomes separate. Bench27 comprises 27 public CTF challenges across six categories, including 12 older tasks, 12 tasks from 2026 and three difficult case studies. Six model labels were evaluated over five planned attempts per task. The released snapshot contains 803 valid attempts; a retrospective comparison with 30 local raw logs reproduced the retained identities, scores, timings and truncated submissions. A separate companion repository implements structured step extraction and matching. We provide a reproducible outcome snapshot and an inspectable interface for process analysis. Temporal comparisons remain descriptive because difficulty, scorer and execution conditions are not fully controlled. Reproducing the presentation's complete process-score figures still requires an agreed companion-data revision.

## Research questions

| Question | Operationalization | Current evidence |
|---|---|---|
| RQ1. What tasks and categories do the evaluated agents solve? | Per-attempt scorer accuracy; tasks solved at least once over available repetitions | Rebuildable from the 803-row snapshot |
| RQ2. How do outcomes differ between older and 2026 tasks? | Difference between cohort accuracies; difficult case studies excluded from this contrast | Rebuildable descriptive comparison, with composition/scorer confounds |
| RQ3. What progress is visible in attempts that fail to submit a correct flag? | Compare authored trajectory evidence with reference stages, separately from final success | Checkpoints, trajectories and companion code available; exact slide matrices require version reconciliation |

## Contribution in relation to prior work

This is a research software artifact and capstone study, not a claim to originate process evaluation.

- **InterCode** formalizes interactive coding with execution feedback and includes a CTF extension. We reuse its CTF ecosystem through Inspect rather than presenting a new interaction framework. [Yang et al., 2023](https://arxiv.org/abs/2306.14898).
- **Cybench** includes intermediary subtasks for detailed evaluation. Our emphasis is post-hoc comparison of recorded trajectories with writeup-derived reference stages. This is a difference in emphasis and implementation, not a demonstrated superiority result. [Zhang et al., 2024/2025](https://arxiv.org/abs/2408.08926).
- **NYU CTF Bench** contributes a scalable CTF dataset and automated agent framework. Bench27 is deliberately a smaller curated study; it does not replace broad coverage benchmarks. [Shao et al., 2024/2025](https://arxiv.org/abs/2406.05590).

Our concrete contributions are the task selection and reference annotations, the outcome/trajectory evidence, the integration between execution and step analysis, and tools for tracing scores back to their inputs. We do not claim that all prior work evaluates only final success, that this is a calibrated universal capability score, or that newer tasks are necessarily absent from model training.

## Experimental artifact

| Dimension | Released information |
|---|---|
| Tasks | 27 total; crypto 6, rev 4, forensics 4, misc 5, web 4, pwn 4 |
| Cohorts | 12 older public tasks; 12 tasks from 2026; 3 difficult case studies |
| Repetitions | 810 planned attempts; 803 retained; 3 sample errors and 4 zero-generation exclusions |
| Models | Six historical gateway model labels; provider revisions/cutoffs remain unresolved |
| Configuration | Inspect AI, Docker, documented limits; new-run defaults centralized in configuration |
| Outcome evidence | Flag scores, submissions, timings, log identities, source hashes and a retrospective audit |
| Process evidence | Reference checkpoints, exported trajectories, separate companion step extraction/scoring |
| Award | AIS3 2026 AI Track Best Project Award; source and translation recorded in recognition notes |

A “task solved” means at least one success among the available attempts, not an unbiased pass@5 estimate. The snapshot is not 803 independently sampled tasks. Exact outcome denominators and cohort rates are in [results](../../results/README.md); raw `.eval` files are not distributed, while their hashes and exclusion identities are.

## Worked example

The exposed-Git challenge `back_to_the_past` decomposes into discovering `.git/`, reconstructing the repository, locating a reset-away commit and recovering `flag.txt`. An agent can reconstruct the repository yet fail to recover the deleted secret. A final binary score treats that attempt as unsuccessful; process evidence can locate the bottleneck.

A command containing `git reflog` is not by itself proof that the repository was reconstructed or the command succeeded. Literal anchors provide evidence to inspect; model-authored quotations and failed commands can still produce false positives. Semantic similarity likewise does not prove completion. Valid alternative solutions may bypass reference stages, so dependencies are soft rather than mandatory. [Reference checkpoints](../../ctf/bench27/contaminated/web_back_to_the_past/checkpoints.json).

## Reproduce what is supported

```bash
python3 -m ais3_bench validate
python3 -m ais3_bench report --check
python3 -m unittest discover -s tests -v
```

These offline commands validate local assets, join result/cost identities and rebuild reported outcomes without a model API or raw logs. Holders of the original logs can additionally run `scripts/audit_snapshot.py`. New model runs use the [setup guide](SETUP.md). The [companion guide](COMPANION.md) describes the distinct `ctf-step` interface and records the inspected external revision.

## Interpretation and next experiments

The study's strongest supported statement is that its released outcome snapshot is internally consistent and traceable to the inspected local logs. Process analysis motivates a more informative view of failure, but its agreement with expert judgment still needs measurement.

The next experiments should (1) freeze both repositories and the figure-producing data, (2) assess anchor precision/recall against independently reviewed trajectories, including alternative solutions, (3) compare models under a common scaffold with verified tool availability, and (4) use task-level uncertainty estimates and exclusion sensitivity. Temporal differences should not be interpreted causally without controlling exposure and difficulty.

The frontier reference has a different scaffold and a 26/27-versus-27/27 presentation discrepancy. It is not included in a same-condition ranking. Updated custom networking does not certify the historical environment; upstream Cybench Docker execution permits internet access. [Full methodology](METHODOLOGY.md) · [Unresolved evidence](EVIDENCE_GAPS.md).
