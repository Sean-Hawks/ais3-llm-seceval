#!/usr/bin/env bash
# Run the 3 deep cybench challenges across model-size ladder for reasoning-path case study.
# Must be run from inspect-test/ so .env (AIS3_BASE_URL / AIS3_API_KEY) is picked up.
set -u
cd "$(dirname "$0")/../../.." || exit 1   # -> inspect-test/
export CYBENCH_ACKNOWLEDGE_RISKS=1

CHALLENGES="permuted,delulu,just_another_pickle_jail"
VARIANT="hard"
LOGDIR="ctf/deep/cybench/logs"
mkdir -p "$LOGDIR"

# size ladder: 26B / 70B / 550B
MODELS=(
  "openai-api/ais3/ais3/gemma-4-26b"
  "openai-api/ais3/ais3/llama-3.3-70b"
  "openai-api/ais3/ais3/nemotron-3-ultra-550b"
)

for M in "${MODELS[@]}"; do
  echo "==================== $M ===================="
  .venv/bin/inspect eval inspect_evals/cybench \
    -T eval_names="$CHALLENGES" \
    -T variant_names="$VARIANT" \
    --model "$M" \
    --message-limit 30 \
    --max-connections 1 \
    --log-dir "$LOGDIR" \
    --log-format eval 2>&1
done
echo "ALL DONE"
