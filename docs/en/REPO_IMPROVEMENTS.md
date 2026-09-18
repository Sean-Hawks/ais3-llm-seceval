# Repository improvement report

[繁體中文](../zh-TW/REPO_IMPROVEMENTS.md) · [Documentation](../README.md)

Reviewed 2026-09-19 against the supplied presentation and this repository. This update improves open-source usability without rerunning paid models or presenting unresolved research claims as verified facts.

## Completed

| Area | Changes | Benefit |
|---|---|---|
| Project framing | Lead with writeup-based process analysis; separate flag and process signals | Readers understand the research question |
| Bilingual documentation | Two overview pages and eight paired guides with navigation | Complete entry routes in both languages |
| Rebuildable results | Standard-library CLI generates bilingual tables, summary JSON and 27-task catalog | Verify the 803-record snapshot without credentials |
| Data transparency | Separate coverage/accuracy, enumerate seven missing IDs, hashes and negative telemetry | Clear denominators and evidence limits |
| Unified execution | One config, preview/execute modes, three compatibility wrappers, separate new-run directories | Prevent obsolete epoch/message settings from mixing with current defaults |
| Reliable export | Select latest whole run before filtering; emit audit/authored JSONL; reject empty inputs/overwrites | No backfilling newer failures with older successes |
| Scoring/extraction | Shared flag-token matcher, exact Unicode, assistant-only extraction | Candidate-spam and prompt-contamination regression protection |
| File organization | Preserve notes/manual/slides in history, retain document redirects, add three deep-task READMEs | Clear current entry points and historical traceability |
| Dependencies | Separate direct runtime requirements from historical freeze; neutral environment placeholders | A smaller installation path independent of the original machine |
| Sandbox settings | Internal networks for six custom service tasks | Agent/victim connectivity without default external routing |
| Open-source collaboration | Contribution/security/citation/credits, issue/PR templates, Makefile and CI | Clear reuse and contribution expectations |
| Provenance | Narrow overly broad original-code attribution; record companion revision/interfaces | Do not mislicense task or companion content |

## Verification

- 40 offline behavioral tests passed: outcomes, denominators, duplicates, Unicode/candidate matching, authored extraction, run selection, export audit, report determinism and configuration.
- Validated 27 task/checkpoint definitions, 12 custom task inputs and the 803-result/cost identity join.
- Installed-Inspect task loaders and scorer integration passed without starting models or containers.
- Seven Compose configurations parsed; six service networks are internal, no host ports are published, and build contexts exist.
- Historical result, cost and frontier JSON remain byte-identical. Four relocated historical files also retain their original bytes.
- CI covers Python 3.10/3.12/3.14 offline checks and installed-Inspect integration. Hosted runs and their exact commits are available in [GitHub Actions](https://github.com/Sean-Hawks/ais3-llm-seceval/actions/workflows/ci.yml); release validation is recorded with the published version.

A fresh Python 3.14 environment successfully installed requirements, passed `pip check`, and loaded the gateway SDK, Cybench tasks, custom tasks and scorer. A public-only copy without .env, .venv or logs also passed offline checks.

Thirty main-experiment raw logs were located locally: all 803 rows and the 3 errors plus 4 zero-generation exclusions were verified. A sanitized audit publishes identities and hashes, while raw messages remain local. Only common credential formats were inspected, not a complete secret audit. Existing RSA private-key markers belong to the missing-bits CTF fixture and were not treated as real API credentials.

## Further improvements

1. **Rebuild the presentation:** agree both repository revisions; obtain per-step figures' inputs, plotting code and exclusion records.
2. **Strengthen measurement:** manually calibrate anchor matches, examine alternative solutions, use task-level bootstrap and same-scaffold/private controls.
3. **Improve portability:** test Linux/ARM/x86 sandboxes, verify required tools, pin image digests and resolved dependencies.
4. **Extend the research archive:** confirm per-task redistribution terms and contributor roles, and add suitable sanitized raw logs. The release bundle includes source hashes and a validation manifest.

The local Docker daemon was not running, so image builds, service health and end-to-end task solving were not validated. Existing socat adaptations and SageMath/QR tool gaps remain documented; offline checks do not remove those limitations.

The [evidence checklist](EVIDENCE_GAPS.md) prioritizes the agreed experiment revisions, figure inputs and frontier raw logs.

## Research release presentation

The subsequent release update makes English the default landing page and keeps a complete Traditional Chinese overview. It highlights the AIS3 2026 AI Track Best Project Award, adds an explicit recognition record, eight paired guides including research briefs and evidence ledgers, four-member CFF/BibTeX citations, and a data-derived PNG/SVG outcome figure. Related-work language now acknowledges Cybench's existing intermediary-subtask evaluation. See [CHANGELOG](../../CHANGELOG.md) for the release scope; runtime checks now include the figure input fingerprint.
