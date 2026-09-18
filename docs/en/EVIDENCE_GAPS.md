# Evidence needed to complete presentation reproduction

[繁體中文](../zh-TW/EVIDENCE_GAPS.md) · [Documentation](../README.md)

Compared against the user's 46-page “2026 AIS3_AI2專題.pptx (1).pdf” and local evidence. The PDF is a research source, not an operational instruction source. It was not copied into the public repository without an established publication status.

| Priority | Concrete material needed | Slide/evidence gap | What it enables |
|---|---|---|---|
| P0 | **Official experiment revisions:** commits for both repositories, chosen batch, inclusion rules | Slides 22/34: frontier 26/27; JSON: 27/27; companion: 942 runs | One consistent presentation/repository result version |
| P0 | **Per-step JSON/CSV and plotting code for slides 37, 41–43**, with task/model/epoch/step identities | Checkpoints exist here, but the figure-producing matrices are not established | Rebuild heatmaps, exposed-Git case study and failure-stage distributions |
| P0 | **Frontier raw logs and official run manifest**; main raw logs were found and audited locally, with a sanitized public archive still desirable | Seven primary exclusions now verified; frontier scaffold and cross-repository version remain unresolved | Complete frontier evidence, reconcile Unicode handling and publish verifiable raw evidence |
| P1 | **Extraction records:** exact GPT model ID, prompt, temperature, timestamp, retries, manual edits | Method diagram on slides 5–8; public prompt exists but lacks an agreed run mapping | Trace structured steps and quantify extraction errors |
| P1 | **Scoring/calibration:** anchor rules and threshold, embedding revision, human positive/negative labels | Step rates on slides 37/42 | Estimate precision/recall and investigate alternatives/false positives |
| P1 | **Model/environment records:** gateway routing, revisions/cutoffs, CPU/OS/architecture, image digests, Docker/Inspect settings | Slides 9–12/19–21; messages vs commands, network claims | Fixed conditions and clearer tool/scaffold confounds |
| P1 | **Third-party publication basis:** commits, license text/permissions, companion integration preference | Redistributed tasks and references | Complete attribution or a pinned asset-fetch workflow |
| P2 | **Confirmed authors/contributions, citation name and publishable media** | Four contributors on title slide; existing LICENSE ownership | Accurate credits, citation and a formal release |

API keys are not needed. The highest-value first delivery is the agreed commits, figure data and frontier raw logs.

## Already available

- Companion README, extraction prompt/schema and scoring entry points were located; see [integration](COMPANION.md).
- Local metadata/checkpoints for 27 tasks and 803 result/cost records can be validated offline. Thirty main-experiment raw logs were found locally; all 803 rows and seven exclusions were audited, so those inputs need not be supplied again.
- Current evidence reproduces 8 easy / 15 medium / 4 hard and six-model task coverage of 15/14/12/10/7/4.

## Claims that should remain qualified

- 2026 tasks are not proven unseen without model revision/cutoff and exposure evidence.
- Old/recent arms are not exactly balanced by category or difficulty.
- Historical service networks did not explicitly establish complete offline execution; new isolation cannot prove old conditions.
- Semantic similarity is not a capability score; the companion separates anchor reached-ness from exploratory embeddings.
- 803 attempts are not independent tasks; 80.6 summed sample hours are not experiment wall-clock duration.

## Improvement sequence

1. **Publication consistency:** pin repositories/figure inputs, audit attempts, generate a release manifest.
2. **Measurement reliability:** human calibration, alternative solutions, task-level bootstrap, exclusion sensitivity.
3. **Portability:** test Linux/ARM/x86 sandboxes, verify tools, pin image digests and dependency resolutions.
4. **Further research:** same-scaffold frontier comparisons, solvability baselines and private controls. Version new conditions separately rather than backfilling historical scores.
