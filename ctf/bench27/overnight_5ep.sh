#!/usr/bin/env bash
# Bench27 過夜跑批：近代 12 題 5ep → deep 3 題 5ep，6 模型串接（嚴禁併行＝gateway starvation）
set -u
cd "$(dirname "$0")/../.." || exit 1        # → inspect-test/
source .venv/bin/activate
export CYBENCH_ACKNOWLEDGE_RISKS=1

MODELS="gemma-4-26b nemotron-3-ultra-550b llama-3.3-70b gemma-4-12b nemotron-cascade-2-30b llama-3.1-8b"
COMMON="--epochs 5 --message-limit 50 --time-limit 1800 --max-tool-output 32768 --no-parallel-tool-calls --no-fail-on-error"

echo "########## OVERNIGHT 5ep START $(date '+%F %T') ##########"

# ---------- 階段一：近代 12 題（全部，不帶 --sample-id）----------
export INSPECT_LOG_DIR=logs/bench27/recent2026
for m in $MODELS; do
  echo "===== RECENT2026 5ep :: $m :: $(date '+%F %T') ====="
  inspect eval ctf/bench27/recent2026_eval.py@recent2026 \
    --model "openai-api/ais3/ais3/$m" \
    $COMMON --max-samples 2 \
    --tags bench27,recent2026,ep5,"$m"
  echo "===== RECENT2026 done :: $m :: $(date '+%F %T') ====="
done

# ---------- 階段二：deep 3 題（permuted/delulu/pickle, hard）----------
export INSPECT_LOG_DIR=logs/bench27/deep_hard
for m in $MODELS; do
  echo "===== DEEP_HARD 5ep :: $m :: $(date '+%F %T') ====="
  inspect eval inspect_evals/cybench \
    -T eval_names=permuted,delulu,just_another_pickle_jail -T variant_names=hard \
    --model "openai-api/ais3/ais3/$m" \
    $COMMON --max-samples 3 \
    --tags bench27,deep_hard,ep5,"$m"
  echo "===== DEEP_HARD done :: $m :: $(date '+%F %T') ====="
done

echo "########## OVERNIGHT 5ep ALL DONE $(date '+%F %T') ##########"
