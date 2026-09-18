# Setup, validation and reproduction

[繁體中文](../zh-TW/SETUP.md) · [Documentation](../README.md)

## Choose a reproduction level

| Goal | Requirements | What it reproduces |
|---|---|---|
| Read/rebuild snapshot | Python 3.10+, standard library | Success rates, denominators and catalog |
| Export new raw logs | Inspect AI, local `.eval` files | Result JSON, exclusion audit and authored text |
| Rerun models | Python environment, Docker, your endpoint/key | A new experiment; identical outcomes are not guaranteed |
| Rebuild slide process analysis | Companion repository, pinned data and extraction/scoring settings | See [integration](COMPANION.md); not provided by this repository alone |

Commands target Linux/macOS; use WSL2 for shell scripts on Windows. Containers are Linux. Python 3.12 is a practical starting point for evaluations; the historical environment recorded Python 3.14. Package installation and container builds still need platform validation.

## Offline review

```bash
git clone https://github.com/Sean-Hawks/ais3-llm-seceval.git
cd ais3-llm-seceval
python3 -m ais3_bench validate
python3 -m ais3_bench report --check
python3 -m unittest discover -s tests -v
python3 scripts/check_docs.py
```

Validation covers task metadata, checkpoint dependencies, local inputs, unique run identities, target consistency and cost joins. It does not prove sandbox solvability or silently repair known negative telemetry. `report --check` writes nothing; omit `--check` to rebuild `results/`.

Open the historical `ctf/bench27/dashboard.html` locally in a browser. GitHub's source viewer does not execute HTML.

## Evaluation environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Set your own `AIS3_BASE_URL` and `AIS3_API_KEY`. The example endpoint is a placeholder. Run from the repository root so Inspect reads `.env`. If `.env` already exists, edit it instead of copying over it.

`requirements.txt` pins direct runtime dependencies. `requirements-research.txt` preserves the original full `pip freeze`, **not a portable lockfile**. Offline analysis needs neither file. Challenge-solving libraries belong in the sandbox image rather than the host environment.

```bash
python -m ais3_bench doctor --evaluation
inspect eval smoke_test.py --model openai-api/ais3/ais3/llama-3.1-8b --limit 1
```

`doctor` checks package/Docker availability without reading keys or contacting a model. The smoke test makes a model call. In `openai-api/<provider>/<remote-model-id>`, the first `ais3` maps to environment variables and the second was the historical gateway's model prefix. To omit the remote prefix:

```bash
python -m ais3_bench run --arm recent2026 --model 8b --model-prefix openai-api/ais3/
```

## Docker and execution

Start Docker Desktop, OrbStack or Docker Engine. Image builds may require network access. At runtime, shared static sandboxes use `network_mode: none`; the six custom service tasks use internal networks between agent and victim. This is a new isolation improvement, not proof the historical experiment was fully offline. Upstream InterCode/Cybench configurations are managed by their packages. The installed Cybench Docker warning explicitly states internet access is allowed; this update does not modify upstream packages, so the six custom internal networks do not establish whole-benchmark offline execution.

```bash
docker compose -f ctf/compose.yaml build
python -m ais3_bench run --arm recent2026 --model 8b
python -m ais3_bench run --arm recent2026 --model 8b --execute
# Preview the full 27-task, six-model plan:
python -m ais3_bench run --arm all --model all
```

Cybench requires `CYBENCH_ACKNOWLEDGE_RISKS=1`. Read upstream execution requirements and prepare an isolated environment before setting it yourself. The new runner does not silently set it. `--execute` starts model calls. `--epochs 1` is useful for diagnostics but is a different experimental condition.

New runs use `output/runs/<UTC timestamp>/`, containing `commands.txt` and one log directory per arm. `--log-dir output/runs/my-experiment` selects a new directory; existing directories are rejected. Models and jobs run sequentially, while Inspect's configured `max_samples` still allows within-job sample concurrency.

The three `run_contaminated.sh`, `run_recent2026.sh`, and `run_deep_hard.sh` compatibility wrappers now preview by default. The obsolete positional `run_recent2026.sh all` becomes `--arm recent2026 --model all`. Overnight, selective-rerun and frontier scripts are historical utilities, not the maintained entry point.

## Export a new experiment

```bash
python -m ais3_bench export --logs output/runs/my-experiment --output output/export/my-experiment
```

Output: `runs.json`, `audit.json`, `authored.jsonl`. For repeated task/model logs, select the latest complete run by Inspect's ISO-prefixed filename **before** excluding errors, zero-generation samples or unsupported scores. Old successes cannot fill gaps in a newer failed run. This mechanical selection does not replace a preregistered inclusion policy; publish an immutable log list for formal experiments.

Empty inputs, no valid samples, unknown tasks, corrupt logs or existing output directories fail without overwriting results. Do not replace the historical `bench27_runs.json` with a new export. Additional model aliases require corresponding configuration changes.

## Troubleshooting

| Symptom | Check |
|---|---|
| Docker unavailable | Start the daemon and rerun `doctor --evaluation` |
| 401 / unknown model | Check endpoint, key and exact remote model ID locally; never post keys |
| Parallel-tool 400 | Retain `--no-parallel-tool-calls` |
| Slow / 504 | Inspect retries and gateway load; distinguish total time, working time and zero generation |
| Missing sandbox module | Update the image and label the result as a new experimental condition |
| ARM pwn failure | Two tasks use x86-64 socat adaptations and require emulation; these differ from upstream nsjail |
| Coppersmith / QR failure | Current images do not guarantee SageMath or complete QR tooling; validate tool availability |

CLI behavior is checked against the locally installed Inspect version. See [Inspect options](https://inspect.aisi.org.uk/options.html) and [Docker internal networks](https://docs.docker.com/reference/compose-file/networks/#internal).

## Retrospective raw-log audit

The main logs were audited locally; a public clone does not contain them. Holders of the same originals can generate an identity/hash-only audit:

```bash
python scripts/audit_snapshot.py --logs logs/bench27 --output output/snapshot_audit.json
```
