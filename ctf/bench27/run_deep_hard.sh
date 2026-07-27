#!/usr/bin/env bash
# Bench27 deep_hard 3 題（permuted/delulu/just_another_pickle_jail）× 6 模型。
# 沿用污染組定案組態；log 進 logs/bench27/deep_hard 供 flag_table.py / analyze 讀。
# 用法：cd inspect-test && bash ctf/bench27/run_deep_hard.sh
set -u
cd "$(dirname "$0")/../.." || exit 1
source .venv/bin/activate
export CYBENCH_ACKNOWLEDGE_RISKS=1
export INSPECT_LOG_DIR=logs/bench27/deep_hard
mkdir -p "$INSPECT_LOG_DIR"

MODELS=(gemma-4-26b nemotron-3-ultra-550b llama-3.3-70b gemma-4-12b nemotron-cascade-2-30b llama-3.1-8b)
CHALLENGES=permuted,delulu,just_another_pickle_jail

COMMON=(--epochs 1 --message-limit 25 --time-limit 1800 --max-tool-output 32768
        --no-parallel-tool-calls --no-fail-on-error --max-samples 3)

echo "=== Bench27 deep_hard 開始 $(date '+%F %T') ==="
for m in "${MODELS[@]}"; do
  echo "--- [deep_hard] $m $(date '+%T') ---"
  inspect eval inspect_evals/cybench \
    -T eval_names="$CHALLENGES" -T variant_names=hard \
    --model "openai-api/ais3/ais3/$m" \
    "${COMMON[@]}" \
    --tags bench27,deep_hard,"$m"
done
echo "=== Bench27 deep_hard 結束 $(date '+%F %T') ==="
