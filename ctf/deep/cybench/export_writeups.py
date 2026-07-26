#!/usr/bin/env python3
"""
Export per-(model, challenge) "writeups" from inspect .eval logs for downstream
analysis (e.g. the user's word-vector path comparison).

For each sample it emits the model's OWN reasoning trace ("writeup"):
  - authored_text : assistant prose + every command/code the model issued
                    (this is what to vectorize; excludes cat-ed file dumps)
  - steps[]       : ordered [{i, role, text, tool, code}] for full fidelity
  - submitted[]   : answers the model submitted
  - solved / error / n_turns

Outputs (under OUTDIR, default ctf/deep/cybench/writeups/):
  - <challenge>__<model>.md    human-readable writeup
  - writeups.jsonl             one JSON row per run (authored_text for vectorizing)

Usage:
  .venv/bin/python ctf/deep/cybench/export_writeups.py [LOGDIR] [OUTDIR]
    LOGDIR default: ctf/deep/cybench/logs
"""
import json
import sys
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log

HERE = Path(__file__).parent
LOGDIR = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "logs"
OUTDIR = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "writeups"
OUTDIR.mkdir(parents=True, exist_ok=True)


def build_steps(sample):
    steps, authored, submitted, commands = [], [], [], []
    for i, m in enumerate(sample.messages):
        role = getattr(m, "role", "")
        text = getattr(m, "text", None) or ""
        tcs = getattr(m, "tool_calls", None) or []
        for tc in tcs:
            fn = getattr(tc, "function", "")
            args = getattr(tc, "arguments", {}) or {}
            code = args.get("code") or args.get("command") or json.dumps(args)
            steps.append({"i": i, "role": role, "tool": fn, "text": text, "code": code})
            if role == "assistant":
                authored.append(text)
                authored.append(code)
                if fn in ("bash", "python"):
                    commands.append({"tool": fn, "code": code})
            if fn == "submit":
                submitted.append(args.get("answer") or json.dumps(args))
        if not tcs:
            steps.append({"i": i, "role": role, "tool": None, "text": text, "code": None})
            if role == "assistant":
                authored.append(text)
    return steps, "\n".join(t for t in authored if t).strip(), submitted, commands


def main():
    logs = list_eval_logs(str(LOGDIR))
    if not logs:
        print(f"No logs under {LOGDIR}")
        return
    jsonl = open(OUTDIR / "writeups.jsonl", "w")
    n = 0
    for lg in logs:
        log = read_eval_log(lg)
        model = log.eval.model.split("/")[-1]
        for s in log.samples or []:
            chal = s.metadata.get("eval_name") or str(s.id)
            steps, authored, submitted, commands = build_steps(s)
            solved = bool(s.scores and next(iter(s.scores.values())).value == "C")
            err = str(s.error.message)[:120] if s.error else None
            n_turns = sum(1 for st in steps if st["role"] == "assistant")
            rec = {
                "model": model,
                "challenge": chal,
                "solved": solved,
                "error": err,
                "n_assistant_turns": n_turns,
                "n_commands": len(commands),
                "submitted": submitted,
                "commands": commands,          # ordered bash/python the model ran
                "authored_text": authored,     # reasoning + code (vectorize this)
            }
            jsonl.write(json.dumps(rec, ensure_ascii=False) + "\n")

            # commands-only export (cleanest "path" source for word-vectors)
            with open(OUTDIR / f"{chal}__{model}.commands.txt", "w") as cf:
                for k, c in enumerate(commands, 1):
                    cf.write(f"### [{k}] {c['tool']}\n{c['code']}\n\n")

            md = OUTDIR / f"{chal}__{model}.md"
            with open(md, "w") as f:
                f.write(f"# {chal} — {model}\n\n")
                f.write(f"- solved: **{solved}**  |  error: {err}  |  assistant turns: {n_turns}\n")
                if submitted:
                    f.write(f"- submitted: {submitted}\n")
                f.write("\n## Authored writeup (model reasoning + its own code)\n\n")
                for st in steps:
                    if st["role"] == "assistant" and st["text"]:
                        f.write(f"**[reason]** {st['text']}\n\n")
                    if st["code"]:
                        f.write(f"```{'python' if st['tool']=='python' else 'bash'}\n{st['code']}\n```\n\n")
                    if st["role"] == "tool" and st["text"]:
                        out = st["text"]
                        out = out[:600] + (" …[truncated]" if len(out) > 600 else "")
                        f.write(f"> _tool output:_ `{out.strip()[:600]}`\n\n")
            n += 1
    jsonl.close()
    print(f"Exported {n} writeups -> {OUTDIR}/ (per-run .md + writeups.jsonl)")


if __name__ == "__main__":
    main()
