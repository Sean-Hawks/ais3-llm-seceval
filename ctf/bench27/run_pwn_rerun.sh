#!/usr/bin/env bash
# 重跑 2 個 pwn 服務題（tic-tac-no / scrabasm）——原跑批因 jail 未 privileged 全錯。
# compose 已修（privileged:true + cgroup:host）。6 模型串接、5 epochs，寫進 recent2026 log。
set -u
cd "$(dirname "$0")/../.."
source .venv/bin/activate
export INSPECT_LOG_DIR=logs/bench27/recent2026
MODELS="gemma-4-26b nemotron-3-ultra-550b llama-3.3-70b gemma-4-12b nemotron-cascade-2-30b llama-3.1-8b"
echo "########## PWN RERUN START $(date '+%F %T') ##########"
for m in $MODELS; do
  echo "===== PWN rerun :: $m :: $(date '+%F %T') ====="
  .venv/bin/inspect eval ctf/bench27/recent2026_eval.py@recent2026 \
    --model "openai-api/ais3/ais3/$m" --sample-id "tic-tac-no,scrabasm" \
    --epochs 5 --message-limit 50 --time-limit 1800 --max-tool-output 32768 \
    --no-parallel-tool-calls --no-fail-on-error --max-samples 2 \
    --tags bench27,recent2026,pwn-rerun,"$m"
done
echo "########## PWN RERUN DONE $(date '+%F %T') ##########"
