#!/usr/bin/env python3
"""
Extract multi-stage trajectories from cybench .eval logs for the 3 deep challenges.

For each (model, challenge) run it reports:
  - solved?  (scorer result)  + #assistant messages (trajectory depth)
  - a ROUGH per-stage anchor-hit scan: for each checkpoint, whether any of its
    literal anchors / keywords appears in the model's full transcript.
    This is NOT the final score (the user does word-vector scoring); it only
    demonstrates whether the checkpoints are discriminative and how far each
    model visibly got before stalling.

Usage:
  .venv/bin/python ctf/deep/cybench/extract_trajectories.py [LOGDIR]
"""
import json
import re
import sys
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log

HERE = Path(__file__).parent
CKPT_DIR = HERE / "checkpoints"
LOGDIR = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "logs"


def load_checkpoints():
    cps = {}
    for f in CKPT_DIR.glob("*.json"):
        d = json.load(open(f))
        cps[d["challenge"]] = d
    return cps


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower())


def transcript_text(sample) -> tuple[str, str, int, list[str]]:
    """Split the transcript into AUTHORED vs OBSERVED text.

    Returns (authored, observed, n_assistant_msgs, path_digest).

    authored  = what the MODEL WROTE: assistant prose + the code/commands it
                issued in tool_calls[].arguments ('code'/'command').
    observed  = what the model SAW: tool outputs (these contain `cat`-ed
                challenge source, so anchors matched here just mean the model
                READ the file, not that it reasoned to that stage).

    Anchor scoring runs on `authored` only, so reading chall.py/my_pickle.py
    can't inflate the stage-hit vector. (This mirrors why the user's word-vector
    scoring should target the model's own reasoning, not quoted source dumps.)
    """
    authored, observed, n_asst, digest = [], [], 0, []
    for m in sample.messages:
        role = getattr(m, "role", "")
        txt = getattr(m, "text", None) or ""
        if role == "tool":
            observed.append(txt)
            continue
        if role == "assistant":
            n_asst += 1
        authored.append(txt)
        for tc in getattr(m, "tool_calls", None) or []:
            fn = getattr(tc, "function", "")
            args = getattr(tc, "arguments", {}) or {}
            code = args.get("code") or args.get("command") or str(args)
            authored.append(code)
            first = code.strip().splitlines()[0][:70] if code.strip() else ""
            digest.append(f"{fn}: {first}")
    return norm("\n".join(authored)), norm("\n".join(observed)), n_asst, digest


def anchor_hits(text: str, cp: dict) -> list[dict]:
    """For each checkpoint, count how many anchors/keywords appear in transcript."""
    rows = []
    for c in cp["checkpoints"]:
        signals = []
        for a in c.get("anchors", []):
            # match on distinctive fragments: split anchor into salient tokens
            frag = norm(a)
            # try the whole anchor's most distinctive substring (drop generic words)
            if frag and frag in text:
                signals.append(("anchor", a))
        for k in c.get("keywords", []):
            if norm(k) in text:
                signals.append(("kw", k))
        rows.append(
            {
                "id": c["id"],
                "stage": c["stage"],
                "n_signals": len(signals),
                "hit": len(signals) > 0,
                "examples": [s[1] for s in signals[:4]],
            }
        )
    return rows


def main():
    cps = load_checkpoints()
    logs = list_eval_logs(str(LOGDIR))
    if not logs:
        print(f"No .eval logs found under {LOGDIR}")
        return
    print(f"# Deep cybench trajectory report  ({len(logs)} log file(s))\n")
    for lg in logs:
        log = read_eval_log(lg)
        model = log.eval.model
        if not log.samples:
            continue
        for sample in log.samples:
            chal = sample.metadata.get("eval_name") or sample.id
            cp = cps.get(chal)
            authored, observed, n_asst, digest = transcript_text(sample)
            solved = None
            if sample.scores:
                sc = next(iter(sample.scores.values()))
                solved = sc.value
            print("=" * 72)
            print(f"MODEL   : {model}")
            print(f"CHALLENGE: {chal}   solved={solved}   assistant_msgs={n_asst}")
            if cp is None:
                print("  (no checkpoint file)")
                continue
            rows = anchor_hits(authored, cp)          # authored-only = genuine reasoning
            obs_rows = anchor_hits(observed, cp)      # observed = just read the file
            hitvec = "".join("X" if r["hit"] else "." for r in rows)
            n_hit = sum(r["hit"] for r in rows)
            print(f"  authored anchor-hit vector (genuine, soft order): {hitvec}  ({n_hit}/{cp['n_checkpoints']} stages)")
            for r, o in zip(rows, obs_rows):
                mark = "X" if r["hit"] else "."
                read_only = " (read-in-file-only)" if (o["hit"] and not r["hit"]) else ""
                ex = ("  e.g. " + "; ".join(r["examples"])) if r["examples"] else ""
                print(f"    [{mark}] {r['id']} stage{r['stage']}  signals={r['n_signals']}{ex}{read_only}")
            print("  path digest (tool calls):")
            for d in digest:
                print(f"      - {d}")
    print("=" * 72)


if __name__ == "__main__":
    main()
