"""Build explicit, reviewable Inspect invocations from one shared configuration."""

from datetime import datetime, timezone
from pathlib import Path
import shlex
import shutil
import subprocess

from .data import ARMS, ROOT, load_snapshot, task_id


def commands(arm, model, prefix=None, epochs=None, log_dir=None, root=ROOT):
    manifest, _, config = load_snapshot(root)
    if epochs is not None and epochs < 1:
        raise ValueError("epochs must be positive")
    models = config["models"] if model == "all" else {model: config["models"][model]}
    arms = ARMS if arm == "all" else (arm,)
    common = ["--epochs", str(epochs or config["epochs"]), "--message-limit", str(config["message_limit"]),
              "--time-limit", str(config["time_limit"]), "--max-tool-output", str(config["max_tool_output"]),
              "--no-parallel-tool-calls", "--no-fail-on-error"]
    log_dir = Path(log_dir or root / "output/runs/preview")
    jobs = []
    for a in arms:
        for short, full in models.items():
            specs = []
            problems = [p for p in manifest["problems"] if p["arm"] == a]
            if a == "contaminated":
                ids = [int(task_id(p)) for p in problems if p["source"] == "intercode"]
                cybench = ",".join(task_id(p) for p in problems if p["source"] == "cybench")
                specs = [("inspect_evals/gdm_intercode_ctf", ["-T", f"sample_ids={ids}"], "intercode"),
                         ("inspect_evals/cybench", ["-T", f"eval_names={cybench}", "-T", "variant_names=hard"], "cybench")]
            elif a == "deep_hard":
                specs = [("inspect_evals/cybench", ["-T", "eval_names=" + ",".join(task_id(p) for p in problems),
                                                   "-T", "variant_names=hard"], "deep_hard")]
            else:
                specs = [("ctf/bench27/recent2026_eval.py@recent2026", [], "recent2026")]
            for target, selectors, concurrency in specs:
                jobs.append(["inspect", "eval", target, "--model", (prefix or config["model_prefix"]) + full,
                             *selectors, *common, "--max-samples", str(config["max_samples"][concurrency]),
                             "--log-dir", str(log_dir / a), "--tags", f"bench27,{a},{short}"])
    return jobs


def execute(jobs, log_dir):
    if not shutil.which("inspect"):
        raise ValueError("inspect is unavailable; activate the virtualenv and install requirements.txt")
    if not shutil.which("docker"):
        raise ValueError("Docker is unavailable")
    probe = subprocess.run(["docker", "info"], capture_output=True, timeout=20)
    if probe.returncode:
        raise ValueError("Docker daemon is not running; start Docker Desktop/OrbStack first")
    # User supplies CYBENCH_ACKNOWLEDGE_RISKS following upstream requirements.
    # Do not silently acknowledge upstream execution requirements for them.
    directory = Path(log_dir)
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "commands.txt").write_text("\n".join(shlex.join(j) for j in jobs) + "\n", encoding="utf-8")
    failures = []
    for job in jobs:
        print(shlex.join(job), flush=True)
        result = subprocess.run(job, cwd=ROOT, check=False)
        if result.returncode:
            failures.append((job[2], result.returncode))
    if failures:
        raise ValueError(f"Inspect reported failures: {failures}; retain logs and inspect before interpreting scores")


def fresh_log_dir():
    return ROOT / "output/runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
