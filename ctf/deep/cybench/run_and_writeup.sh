#!/usr/bin/env bash
# One shot: run the 3 deep challenges ONCE for a model, then export writeup + commands.
#
# Usage (from anywhere; script cd's to inspect-test/):
#   ctf/deep/cybench/run_and_writeup.sh                       # default model gemma-4-26b
#   ctf/deep/cybench/run_and_writeup.sh llama-3.3-70b         # any ais3 model short-name
#   ctf/deep/cybench/run_and_writeup.sh nemotron-3-ultra-550b permuted   # optional: subset of challenges
#
# Outputs:
#   ctf/deep/cybench/logs/            raw .eval log (viewable with `inspect view`)
#   ctf/deep/cybench/writeups/<chal>__<model>.md            human-readable writeup
#   ctf/deep/cybench/writeups/<chal>__<model>.commands.txt  ordered commands the model ran
#   ctf/deep/cybench/writeups/writeups.jsonl                one row/run: authored_text + commands (vectorize this)
set -u
cd "$(dirname "$0")/../../.." || exit 1   # -> inspect-test/
export CYBENCH_ACKNOWLEDGE_RISKS=1

MODEL_SHORT="${1:-gemma-4-26b}"
CHALLENGES="${2:-permuted,delulu,just_another_pickle_jail}"
MODEL="openai-api/ais3/ais3/${MODEL_SHORT}"
LOGDIR="ctf/deep/cybench/logs"
OUTDIR="ctf/deep/cybench/writeups"
mkdir -p "$LOGDIR" "$OUTDIR"

echo ">>> running [$CHALLENGES] once on $MODEL_SHORT ..."
.venv/bin/inspect eval inspect_evals/cybench \
  -T eval_names="$CHALLENGES" \
  -T variant_names=hard \
  --model "$MODEL" \
  --message-limit 30 \
  --max-connections 1 \
  --log-dir "$LOGDIR" \
  --log-format eval || { echo "eval failed"; exit 1; }

echo ">>> exporting writeups + commands ..."
.venv/bin/python ctf/deep/cybench/export_writeups.py "$LOGDIR" "$OUTDIR"

echo ">>> done. New writeups for $MODEL_SHORT:"
ls -1 "$OUTDIR" | grep -E "__${MODEL_SHORT}\.(md|commands\.txt)$" || true
