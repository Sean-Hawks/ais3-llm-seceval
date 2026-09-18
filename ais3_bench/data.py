"""Validate and aggregate committed evidence without calling a model."""

from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "ctf" / "bench27"
ARMS = ("contaminated", "recent2026", "deep_hard")
TASK_ALIASES = {"tic-tac-no": "pwn_tic-tac-no", "scrabasm": "pwn_scrabasm",
                "glotq": "web_glotq", "single-trust": "web_single-trust"}

# Preserve this published telemetry anomaly; never use it for throughput metrics.
KNOWN_NEGATIVE_TIME = ("contaminated", "network_tools", "8b", 4)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def task_id(problem):
    return str(problem.get("src_id", Path(problem["dir"]).name))


def load_snapshot(root=ROOT):
    bench = root / "ctf" / "bench27"
    return (read_json(bench / "MANIFEST.json"),
            read_json(bench / "bench27_runs.json"),
            read_json(root / "configs" / "bench27.json"))


def row_key(row):
    return row["arm"], str(row["task"]), row["model"], row["epoch"]


def validate_rows(rows, manifest, config):
    """Reject ambiguous identities and malformed score values; allow missing runs."""
    problems = {(p["arm"], task_id(p)): p for p in manifest["problems"]}
    errors, seen = [], set()
    for index, row in enumerate(rows):
        prefix = f"run[{index}]"
        try:
            key = row_key(row)
            problem = problems[(row["arm"], str(row["task"]))]
            model = config["models"][row["model"]]
        except (KeyError, TypeError) as exc:
            errors.append(f"{prefix}: unknown or missing identity {exc}")
            continue
        if key in seen:
            errors.append(f"{prefix}: duplicate run {key}")
        seen.add(key)
        if type(row["epoch"]) is not int or not 1 <= row["epoch"] <= config["epochs"]:
            errors.append(f"{prefix}: epoch outside 1..{config['epochs']}")
        if type(row.get("solved")) is not bool:
            errors.append(f"{prefix}: solved must be a JSON boolean")
        if row.get("score_value") not in ("C", "I"):
            errors.append(f"{prefix}: unsupported score value")
        elif row["solved"] != (row["score_value"] == "C"):
            errors.append(f"{prefix}: solved disagrees with scorer value")
        if row.get("model_full") != model:
            errors.append(f"{prefix}: model alias mismatch")
        if row.get("target_flag") != problem["flag"]:
            errors.append(f"{prefix}: target differs from manifest")
        for field in ("working_time", "total_time"):
            value = row.get(field)
            known_anomaly = key == KNOWN_NEGATIVE_TIME and field == "working_time" and value == -1340.8
            if not known_anomaly and (type(value) not in (int, float) or not 0 <= value < float("inf")):
                errors.append(f"{prefix}: invalid {field}")
    return errors


def validate_repository(root=ROOT):
    manifest, rows, config = load_snapshot(root)
    errors = validate_rows(rows, manifest, config)
    bench = root / "ctf" / "bench27"
    problems = manifest["problems"]
    if Counter(p["arm"] for p in problems) != dict(contaminated=12, recent2026=12, deep_hard=3):
        errors.append("manifest: expected 12/12/3 tasks")
    identities = [(p["arm"], task_id(p)) for p in problems]
    if len(set(identities)) != len(identities):
        errors.append("manifest: duplicate task identity")
    for p in problems:
        directory = bench / p["dir"]
        for name in ("README.md", "writeup.md", "checkpoints.json"):
            if not (directory / name).is_file():
                errors.append(f"{p['dir']}: missing {name}")
        if not (directory / "checkpoints.json").is_file():
            continue
        cp = read_json(directory / "checkpoints.json")
        stages = cp.get("checkpoints", [])
        ids = [s["id"] for s in stages]
        if not stages or len(stages) != cp.get("n_checkpoints") or len(set(ids)) != len(ids):
            errors.append(f"{p['dir']}: invalid checkpoint count or identity")
        if cp.get("flag") != p["flag"]:
            errors.append(f"{p['dir']}: checkpoint target differs from manifest")
        for stage in stages:
            if not stage.get("milestone") or not isinstance(stage.get("anchors"), list):
                errors.append(f"{p['dir']}: missing checkpoint evidence definition")
            if any(dep not in ids or ids.index(dep) >= ids.index(stage['id'])
                   for dep in stage.get("depends_on", [])):
                errors.append(f"{p['dir']}: invalid checkpoint dependency")
        if p["arm"] == "recent2026":
            path = directory / "challenge.json"
            if not path.is_file():
                errors.append(f"{p['dir']}: missing challenge.json")
                continue
            challenge = read_json(path)
            if TASK_ALIASES.get(challenge["id"], challenge["id"]) != task_id(p) or challenge["flag"] != p["flag"]:
                errors.append(f"{p['dir']}: challenge identity/target mismatch")
            for dest, src in challenge.get("files", {}).items():
                resolved = (directory / src).resolve()
                if not resolved.is_relative_to(directory.resolve()) or not resolved.is_file():
                    errors.append(f"{p['dir']}: missing/escaping task asset {src}")
                if Path(dest).is_absolute() or ".." in Path(dest).parts:
                    errors.append(f"{p['dir']}: unsafe sandbox destination {dest}")
                if Path(src).name in {"flag.txt", "writeup.md", "checkpoints.json"}:
                    errors.append(f"{p['dir']}: evaluator-only file in agent inputs")
            compose = directory / challenge["compose"] if challenge.get("compose") else root / "ctf/compose.yaml"
            if not compose.is_file():
                errors.append(f"{p['dir']}: missing compose")
    costs = read_json(bench / "bench27_cost.json")
    if len({row_key(r) for r in costs}) != len(costs):
        errors.append("cost: duplicate run")
    if {row_key(r) for r in costs} != {row_key(r) for r in rows}:
        errors.append("cost: run identities differ from result snapshot")
    by_key = {row_key(r): r for r in rows}
    for r in costs:
        if row_key(r) in by_key and r["solved"] != by_key[row_key(r)]["solved"]:
            errors.append(f"cost: score mismatch for {row_key(r)}")
    audit = read_json(bench / "snapshot_audit.json")
    if audit["snapshot_sha256"] != hashlib.sha256((bench / "bench27_runs.json").read_bytes()).hexdigest():
        errors.append("audit: result snapshot hash changed; re-audit against raw logs")
    missing = aggregate(manifest, rows, config)["missing_attempts"]
    if {row_key(r) for r in audit["excluded_samples"]} != {row_key(r) for r in missing}:
        errors.append("audit: excluded identities differ from missing attempts")
    if audit["sample_status_counts"]["valid"] != len(rows) or audit["value_differences"] != 0:
        errors.append("audit: raw-log comparison does not match snapshot")
    return errors


def aggregate(manifest, rows, config):
    """Task coverage and per-attempt accuracy have deliberately separate denominators."""
    expected = {(p["arm"], task_id(p), model, epoch)
                for p in manifest["problems"] for model in config["models"]
                for epoch in range(1, config["epochs"] + 1)}
    missing = sorted(expected - {row_key(r) for r in rows})
    models = []
    for short, full in config["models"].items():
        selected = [r for r in rows if r["model"] == short]
        arms = {}
        for arm in ARMS:
            group = [r for r in selected if r["arm"] == arm]
            wins = sum(r["solved"] for r in group)
            arms[arm] = {"solved": wins, "valid_attempts": len(group),
                         "accuracy": wins / len(group) if group else None}
        cats = {}
        for cat in manifest["categories"]:
            tasks = {(p["arm"], task_id(p)) for p in manifest["problems"] if p["category"] == cat}
            cats[cat] = {"solved_tasks": len({(r["arm"], r["task"]) for r in selected
                                             if r["solved"] and (r["arm"], r["task"]) in tasks}),
                         "total_tasks": len(tasks)}
        old, recent = arms["contaminated"]["accuracy"], arms["recent2026"]["accuracy"]
        models.append({"model": short, "model_full": full,
                       "solved_tasks": len({(r["arm"], r["task"]) for r in selected if r["solved"]}),
                       "valid_attempts": len(selected), "solved_attempts": sum(r["solved"] for r in selected),
                       "arms": arms, "categories": cats,
                       "gap_percentage_points": 100 * (old - recent) if old is not None and recent is not None else None})
    return {"schema_version": 1, "expected_attempts": len(expected), "valid_attempts": len(rows),
            "missing_attempts": [dict(zip(("arm", "task", "model", "epoch"), k)) for k in missing],
            "summed_sample_hours": sum(r["total_time"] for r in rows) / 3600,
            "telemetry_anomalies": [{"arm": r["arm"], "task": r["task"], "model": r["model"],
                                     "epoch": r["epoch"], "field": "working_time", "value": r["working_time"],
                                     "treatment": "preserved; exclude from throughput/working-time analysis"}
                                    for r in rows if r["working_time"] < 0],
            "models": models}


def source_hashes(root=ROOT):
    bench = root / "ctf" / "bench27"
    paths = [root / "configs/bench27.json"] + [bench / name for name in
             ("MANIFEST.json", "bench27_runs.json", "bench27_cost.json", "opus_runs.json", "snapshot_audit.json")]
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
