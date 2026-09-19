"""Run with python -m ais3_bench; default operations never call a model."""

import argparse
from importlib import metadata
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

from .data import ARMS, ROOT, load_snapshot, validate_repository
from .report import write_reports
from .runner import commands, execute, fresh_log_dir


def doctor(evaluation=False):
    failures = []
    print(f"Python: {sys.version.split()[0]}")
    print("Offline report and validation: standard library only")
    for package in ("inspect_ai", "inspect_evals", "inspect_cyber", "openai"):
        try:
            print(f"{package}: {metadata.version(package)}")
        except metadata.PackageNotFoundError:
            print(f"{package}: not installed (only needed for evaluation/export)")
            failures.append(package)
    if shutil.which("docker"):
        try:
            result = subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"], capture_output=True, text=True, timeout=15)
            print("Docker: " + (result.stdout.strip() if result.returncode == 0 else "daemon unavailable"))
            if result.returncode:
                failures.append("Docker daemon")
        except subprocess.TimeoutExpired:
            print("Docker: timed out")
            failures.append("Docker daemon")
    else:
        print("Docker: not installed")
        failures.append("Docker")
    print("Credentials: values intentionally not read or displayed")
    return 1 if evaluation and failures else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="AIS3 Bench27: offline evidence, validation, and evaluation plans")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("validate", help="validate task assets, checkpoints, runs and costs offline")
    report = subs.add_parser("report", help="rebuild bilingual reports from committed JSON")
    report.add_argument("--output", type=Path, default=ROOT / "results")
    report.add_argument("--check", action="store_true", help="fail if committed reports differ; write nothing")
    diag = subs.add_parser("doctor", help="check local capabilities without reading credentials")
    diag.add_argument("--evaluation", action="store_true", help="fail if evaluation dependencies are unavailable")
    run = subs.add_parser("run", help="print an evaluation plan; --execute starts model calls")
    run.add_argument("--arm", choices=(*ARMS, "all"), default="recent2026")
    run.add_argument("--model", choices=(*load_snapshot()[2]["models"], "all"), default="8b")
    run.add_argument("--model-prefix", help="Inspect provider/model prefix; include trailing slash")
    run.add_argument("--epochs", type=int)
    run.add_argument("--log-dir", type=Path)
    run.add_argument("--execute", action="store_true")
    export = subs.add_parser("export", help="export new Inspect logs separately from the historical snapshot")
    export.add_argument("--logs", type=Path, required=True, help="directory containing one subdirectory per arm")
    export.add_argument("--output", type=Path, default=ROOT / "output/export")
    hub = subs.add_parser("hub-export", help="prepare the fixed v0.1.0 Hugging Face dataset locally; never upload")
    hub.add_argument("--output", type=Path, default=ROOT / "output/huggingface/bench27-v0.1.0")
    hub.add_argument("--repo-id", default="Sean-Hawks/ais3-bench27")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            errors = validate_repository()
            if errors:
                raise ValueError("\n".join(errors))
            print("PASS: 27 tasks, checkpoint references, local task assets, result identities and cost joins")
        elif args.command == "report":
            names = write_reports(args.output, args.check)
            print(("Verified" if args.check else "Wrote") + ": " + ", ".join(names))
        elif args.command == "doctor":
            return doctor(args.evaluation)
        elif args.command == "run":
            log_dir = args.log_dir or (fresh_log_dir() if args.execute else ROOT / "output/runs/preview")
            jobs = commands(args.arm, args.model, args.model_prefix, args.epochs, log_dir)
            if args.execute:
                execute(jobs, log_dir)
            else:
                print("Preview only. --execute starts evaluations and may incur provider charges.")
                for job in jobs:
                    print(shlex.join(job))
        elif args.command == "export":
            from .logs import export_logs
            count = export_logs(args.logs, args.output)
            print(f"Exported {count} valid attempts to {args.output}; audit and authored JSONL included")
        elif args.command == "hub-export":
            from .hub import write_hub_export
            names = write_hub_export(args.output, repo_id=args.repo_id)
            print(f"Prepared {len(names)} files in {args.output}; nothing uploaded")
    except (ValueError, OSError, KeyError, json.JSONDecodeError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
