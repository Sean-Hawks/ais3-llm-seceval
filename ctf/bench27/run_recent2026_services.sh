#!/usr/bin/env bash
# 近代 5 服務題 × 6 模型（crypto_six-seven-again, pwn_tic-tac-no, pwn_scrabasm, web_glotq, web_single-trust）
# 各題 compose 自帶 victim；epochs 1（先求覆蓋）。從 inspect-test/ 跑。
set -u
cd "$(dirname "$0")/../.." || exit 1
source .venv/bin/activate
export CYBENCH_ACKNOWLEDGE_RISKS=1
export INSPECT_LOG_DIR=logs/bench27/recent2026
mkdir -p "$INSPECT_LOG_DIR"
MODELS=(gemma-4-26b nemotron-3-ultra-550b llama-3.3-70b gemma-4-12b nemotron-cascade-2-30b llama-3.1-8b)
SERVICE_IDS="crypto_six-seven-again,pwn_tic-tac-no,pwn_scrabasm,web_glotq,web_single-trust"
COMMON=(--epochs 1 --message-limit 25 --time-limit 1800 --max-tool-output 32768
        --no-parallel-tool-calls --no-fail-on-error --max-samples 2)
echo "=== recent2026 服務題開始 $(date '+%F %T') ==="
for m in "${MODELS[@]}"; do
  echo "--- [services] $m $(date '+%T') ---"
  inspect eval ctf/bench27/recent2026_eval.py@recent2026 \
    --model "openai-api/ais3/ais3/$m" \
    --sample-id "$SERVICE_IDS" "${COMMON[@]}" \
    --tags bench27,recent2026,services,"$m"
done
echo "=== recent2026 服務題結束 $(date '+%F %T') ==="
