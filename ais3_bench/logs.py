"""Audit new Inspect logs without replacing the published experiment snapshot."""

from collections import defaultdict
import json
from pathlib import Path

from .data import ARMS, ROOT, TASK_ALIASES, load_snapshot, task_id

ALIASES = TASK_ALIASES


def authored_text(sample):
    """Assistant prose and tool-call arguments only; no prompt, target or tool output."""
    parts = []
    for message in sample.messages or []:
        if getattr(message, "role", "") != "assistant":
            continue
        text = getattr(message, "text", "") or ""
        if text:
            parts.append(text)
        for call in getattr(message, "tool_calls", None) or []:
            arguments = getattr(call, "arguments", {}) or {}
            for key in ("code", "command", "answer"):
                if isinstance(arguments.get(key), str):
                    parts.append(arguments[key])
    return "\n".join(parts)


def invalid_reason(sample):
    if getattr(sample, "error", None):
        return "sample_error"
    if not any(getattr(m, "role", "") == "assistant" for m in sample.messages or []):
        return "zero_generation"
    scores = getattr(sample, "scores", None) or {}
    if len(scores) != 1 or next(iter(scores.values())).value not in ("C", "I"):
        return "missing_or_unsupported_score"
    return None


def select_latest(groups):
    """Select a complete latest task/model run BEFORE excluding invalid samples.

    groups: (arm, task, model, filename, samples). Older successes must never fill
    holes in a newer failed run. ISO-prefixed Inspect filenames define ordering.
    """
    picked = {}
    for arm, task, model, filename, samples in sorted(groups, key=lambda g: g[3]):
        picked[(arm, task, model)] = (filename, samples)
    return picked


def export_logs(log_root, output):
    from inspect_ai.log import read_eval_log

    manifest, _, config = load_snapshot()
    aliases = {v: k for k, v in config["models"].items()}
    known = {(p["arm"], task_id(p)) for p in manifest["problems"]}
    log_root, output = Path(log_root), Path(output)
    files = [(arm, p) for arm in ARMS for p in sorted((log_root / arm).glob("*.eval"))]
    if not files:
        raise ValueError(f"No .eval files under arm directories in {log_root}; nothing was overwritten")
    if output.exists():
        raise ValueError(f"Output already exists: {output}; choose a new directory")
    groups, log_audit = [], []
    for arm, path in files:
        # Corrupt logs abort instead of silently changing the dataset.
        log = read_eval_log(str(path))
        full = (log.eval.model or "").split("/")[-1]
        if full not in aliases:
            log_audit.append({"log_file": path.name, "status": "unrecognized_model", "model": full})
            continue
        grouped = defaultdict(list)
        for sample in log.samples or []:
            tid = str(sample.id).split(" (")[0]
            tid = ALIASES.get(tid, tid)
            if (arm, tid) not in known:
                raise ValueError(f"Unknown task {arm}/{tid} in {path.name}")
            grouped[tid].append(sample)
        log_audit.append({"log_file": path.name, "arm": arm, "model": aliases[full],
                          "status": "read" if grouped else "no_samples",
                          "sample_count": sum(len(s) for s in grouped.values())})
        for tid, samples in grouped.items():
            epochs = [getattr(s, "epoch", 1) for s in samples]
            if len(set(epochs)) != len(epochs):
                raise ValueError(f"Duplicate epoch in {path.name}/{tid}")
            groups.append((arm, tid, aliases[full], path.name, samples))
    rows, authored, audit = [], [], []
    selected = select_latest(groups)
    for arm, tid, model, filename, samples in groups:
        if selected[(arm, tid, model)][0] != filename:
            audit.extend({"arm": arm, "task": tid, "model": model, "epoch": getattr(s, "epoch", 1),
                          "log_file": filename, "status": "superseded_run"} for s in samples)
    for (arm, tid, model), (filename, samples) in sorted(selected.items()):
        for sample in sorted(samples, key=lambda s: getattr(s, "epoch", 1)):
            identity = dict(arm=arm, task=tid, model=model, epoch=getattr(sample, "epoch", 1), log_file=filename)
            reason = invalid_reason(sample)
            audit.append({**identity, "status": reason or "valid"})
            if reason:
                continue
            scorer, score = next(iter(sample.scores.items()))
            target = sample.target if isinstance(sample.target, str) else (sample.target[0] if sample.target else "")
            submission = sample.output.completion or "" if sample.output else ""
            transcript = "\n".join(getattr(m, "text", "") or "" for m in sample.messages)
            rows.append({**identity, "model_full": config["models"][model], "scorer": scorer,
                         "score_value": score.value, "solved": score.value == "C", "target_flag": target,
                         "submitted": submission, "flag_in_submission": bool(target and target in submission),
                         "flag_in_transcript": bool(target and target in transcript),
                         "working_time": round(getattr(sample, "working_time", 0) or 0, 1),
                         "total_time": round(getattr(sample, "total_time", 0) or 0, 1)})
            authored.append({**identity, "solved": score.value == "C", "authored_text": authored_text(sample)})
    if not rows:
        raise ValueError("No valid scored attempts; nothing was written")
    # Store outside tracked evidence, even if a caller passes the snapshot path.
    protected = ROOT / "ctf/bench27"
    if output.resolve().is_relative_to(protected.resolve()):
        raise ValueError("Export destination must be outside the historical Bench27 directory")
    output.mkdir(parents=True, exist_ok=False)
    for name, data in (("runs.json", rows), ("audit.json", {"selection": "latest complete task/model group before filtering",
                                                            "logs": log_audit, "samples": audit})):
        (output / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "authored.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in authored), encoding="utf-8")
    return len(rows)
