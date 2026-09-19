"""Prepare the fixed v0.1.0 outcome dataset; no authentication or network access."""

import hashlib
import json
from pathlib import Path
import re

from .data import ROOT, load_snapshot, read_json, row_key, source_hashes, task_id, validate_repository

SOURCE_COMMIT = "4ed7dc917012de50f0aa0f07c1de1838175b811c"
SOURCE_URL = "https://github.com/Sean-Hawks/ais3-llm-seceval"
DEFAULT_REPO = "Sean-Hawks/ais3-bench27"
ATTEMPT_FIELDS = ("arm", "task", "model", "model_full", "epoch", "scorer", "score_value",
                  "solved", "working_time", "total_time")
COST_FIELDS = ("input_tokens", "output_tokens", "total_tokens", "assistant_msgs")
EXCLUSION_FIELDS = ("arm", "task", "model", "epoch", "status")


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def jsonl_bytes(rows):
    return "".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in rows).encode("utf-8")


def hub_artifacts(root=ROOT, repo_id=DEFAULT_REPO):
    if not re.fullmatch(r"[A-Za-z0-9][\w.-]*/[A-Za-z0-9][\w.-]*", repo_id):
        raise ValueError("Expected a Hub repository ID: owner/name")
    errors = validate_repository(root)
    if errors:
        raise ValueError("\n".join(errors))
    lock = read_json(root / "publishing/huggingface/source-lock.json")
    if lock["source_commit"] != SOURCE_COMMIT or source_hashes(root) != lock["source_sha256"]:
        raise ValueError("Source snapshot changed; define a new version and update its provenance before publishing")
    manifest, rows, config = load_snapshot(root)
    bench = root / "ctf/bench27"
    costs = {row_key(r): r for r in read_json(bench / "bench27_cost.json")}
    audit = read_json(bench / "snapshot_audit.json")
    frontier = read_json(bench / "opus_runs.json")
    catalog = []
    for p in manifest["problems"]:
        tid = task_id(p)
        catalog.append({
            "arm": p["arm"], "task": tid, "analysis_id": frontier[tid]["clear"],
            "category": p["category"], "difficulty": p["difficulty"], "source": p["source"],
            "historical_year_label": str(p["year"]),
            "reference_url": f"{SOURCE_URL}/blob/{SOURCE_COMMIT}/ctf/bench27/{p['dir']}/README.md",
        })
    tasks = {(r["arm"], r["task"]): r for r in catalog}
    attempts = []
    for r in sorted(rows, key=row_key):
        item = {key: r[key] for key in ATTEMPT_FIELDS}
        item.update({key: costs[row_key(r)][key] for key in COST_FIELDS})
        item.update({key: tasks[(r["arm"], r["task"])][key]
                     for key in ("analysis_id", "category", "difficulty")})
        item["working_time_anomaly"] = r["working_time"] < 0
        attempts.append(item)
    exclusions = [{key: r[key] for key in EXCLUSION_FIELDS}
                  for r in sorted(audit["excluded_samples"], key=row_key)]
    if (len(catalog), len(attempts), len(exclusions)) != (27, 803, 7):
        raise ValueError("Unexpected v0.1.0 dataset dimensions")
    provenance = {
        "dataset_id": repo_id, "dataset_version": "0.1.0", "source_release": "v0.1.0",
        "source_repository": SOURCE_URL, "source_commit": SOURCE_COMMIT,
        "source_sha256": lock["source_sha256"],
        "counts": {"tasks": len(catalog), "attempts": len(attempts), "exclusions": len(exclusions),
                   "models": len(config["models"]), "planned_attempts": 810},
        "selection": "All 803 retained primary attempts; seven exclusions kept separately; no frontier rows.",
        "raw_log_audit": {"identity_match": audit["identity_match"], "value_differences": audit["value_differences"],
                          "source_log_count": len(audit["raw_logs_sha256"]),
                          "sample_status_counts": audit["sample_status_counts"]},
        "projection": {"attempt_fields": list(ATTEMPT_FIELDS), "cost_fields": list(COST_FIELDS),
                       "excluded_content": ["target flags", "submissions", "transcripts", "raw logs", "log filenames",
                                            "challenge binaries and service code", "reference writeups", "credentials"]},
        "time_units": "seconds; negative working_time is retained and explicitly flagged",
        "source_of_truth": "Original flag scorer results, not substring diagnostics or process scores",
    }
    card = (root / "publishing/huggingface/dataset-card.md").read_text(encoding="utf-8")
    result = {
        "README.md": card.replace("__DATASET_ID__", repo_id).encode("utf-8"),
        "data/attempts.jsonl": jsonl_bytes(attempts),
        "data/tasks.jsonl": jsonl_bytes(catalog),
        "data/exclusions.jsonl": jsonl_bytes(exclusions),
        "provenance.json": json_bytes(provenance),
        "figures/outcomes.png": (root / "results/figures/outcomes.png").read_bytes(),
    }
    for name in ("CITATION.cff", "CITATION.bib", "LICENSE"):
        result[name] = (root / name).read_bytes()
    result["THIRD_PARTY_NOTICES.md"] = (
        "# Dataset scope\n\nThis Hub export contains project-authored measurements, factual task metadata and documentation. "
        "It does not redistribute challenge attachments, service code, flags, reference solutions or model conversations. "
        "MIT applies to original project work, not to the upstream challenges referenced by the catalog. "
        "Task names and sources are retained for attribution; links point to the fixed source release. "
        f"See the [source notices]({SOURCE_URL}/blob/{SOURCE_COMMIT}/THIRD_PARTY_NOTICES.md).\n\n"
        "此匯出僅含專題量測、題目索引及文件；上游題目的權利與授權不因資料集發布而改變。\n"
    ).encode("utf-8")
    result["SHA256SUMS"] = "".join(hashlib.sha256(content).hexdigest() + "  " + name + "\n"
                                      for name, content in sorted(result.items())).encode("utf-8")
    return result


def write_hub_export(directory, root=ROOT, repo_id=DEFAULT_REPO):
    outputs = hub_artifacts(root, repo_id)
    directory = Path(directory)
    if directory.exists():
        raise ValueError("Choose a new output directory; existing publication packages are never overwritten")
    directory.mkdir(parents=True)
    for name, content in outputs.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return list(outputs)
