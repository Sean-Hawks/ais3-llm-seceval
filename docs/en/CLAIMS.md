# Claim–evidence ledger

[繁體中文](../zh-TW/CLAIMS.md) · [Research brief](RESEARCH_BRIEF.md)

This ledger distinguishes project recognition, reproducible observations and unresolved inference. A green CI run verifies the checks implemented here; it is not an endorsement of every research claim.

| Statement | Status | Evidence | Boundary / next validation |
|---|---|---|---|
| The project received the AIS3 2026 AI Track Best Project Award | Team-reported recognition, linked participant record | [Recognition and sources](../../RECOGNITION.md) | English award title is a translation; add an organizer announcement/certificate when available |
| Bench27 has 27 tasks with reference checkpoints | Verified from repository definitions | [Catalog](../../results/TASK_CATALOG.md), `validate` | Curated public tasks; category/difficulty labels are not calibrated |
| 803 retained attempts match inspected raw logs | Retrospectively verified | [Audit](../../ctf/bench27/snapshot_audit.json) | Raw logs remain local; hashes enable comparison by holders of originals; no preregistration claim |
| Six model labels solve 15/14/12/10/7/4 tasks at least once | Reproducible observation | [Outcome tables](../../results/README.md), source JSON | Coverage over available repetitions, not single-run accuracy |
| Older tasks have higher aggregate attempt accuracy for all six labels | Reproducible descriptive observation | [Cohort tables](../../results/README.md) | Not causal evidence of contamination; composition/scorer/tool differences remain |
| Process analysis can expose intermediate progress in failed attempts | Implemented analysis approach with case-study material | [Reference stages](../../ctf/bench27/contaminated/web_back_to_the_past/checkpoints.json), [companion](COMPANION.md) | Quantitative agreement with expert annotations remains to be measured |
| The presentation's exact process-score heatmaps are reproducible from this release alone | Not established | [Evidence gaps](EVIDENCE_GAPS.md) | Need the agreed extraction/scoring revision and figure inputs |
| Semantic similarity proves a stage was completed | Not supported; not used as our interpretation | [Methodology](METHODOLOGY.md) | Similarity is exploratory; literal matches also require calibration |
| The frontier reference is directly comparable to the main six labels | Not supported | Different scaffold; [26/27 vs 27/27 discrepancy](../../results/README.md) | Same-scaffold rerun and reconciled outcome definitions |
| All historical tasks ran without internet access | Not established | Local/custom and upstream networking differ | New internal networks cover six custom services, not historical or upstream environments |
| Exact provider model revisions/cutoffs are established | Not established | Snapshot contains gateway labels | Provider routing/revision records required |
| Every redistributed file is MIT-licensed | False | [License scope](../../THIRD_PARTY_NOTICES.md) | Only original work uses project MIT; retain upstream terms and fill permission gaps |
| This is a peer-reviewed publication or a state-of-the-art benchmark claim | Not claimed | Research artifact, capstone recognition | Cite as software; no paper DOI or acceptance is asserted |

## Data-to-claim path

`MANIFEST.json + bench27_runs.json + bench27_cost.json + snapshot_audit.json` → validation → generated `results/summary.json` and tables → claims above. New evaluation logs go to separate output directories and do not silently change the historical snapshot.

When proposing a stronger conclusion, add its operational definition, exact inputs, a falsifiable test and the resulting evidence here before updating the project summary.
