#!/usr/bin/env bash
# Bench27 近代組跑批。用法：cd inspect-test && bash ctf/bench27/run_recent2026.sh [all]
# 預設只跑「已就緒」題（4 靜態 + 已 wire 的 crypto_six-seven）；帶 all 則跑全部
# （未 wire 的服務題會因連不到 victim 而失敗，需先照 recent2026/SERVICE_WIRING.md wire）。
set -u
cd "$(dirname "$0")/../.." || exit 1
source .venv/bin/activate
export CYBENCH_ACKNOWLEDGE_RISKS=1
export INSPECT_LOG_DIR=logs/bench27/recent2026
mkdir -p "$INSPECT_LOG_DIR"

MODELS=(gemma-4-26b nemotron-3-ultra-550b llama-3.3-70b gemma-4-12b nemotron-cascade-2-30b llama-3.1-8b)

# 已就緒（可直接跑）：6 靜態 + crypto_six-seven（已 wire victim）
# 2026-07-26 修：補回 forensics_cake/stillthere（純 pcap 靜態，原漏列）
READY_IDS="rev_ooo,rev_flag-finder,misc_endians,misc_error-correction,forensics_cake,forensics_stillthere,crypto_six-seven"

COMMON=(--epochs 1 --message-limit 50 --time-limit 1800 --max-tool-output 32768
        --no-parallel-tool-calls --no-fail-on-error)

SEL=()
if [ "${1:-ready}" != "all" ]; then
  # 修：inspect 對重複 --sample-id 只認最後一個 → 必須單一逗號分隔一次帶入
  SEL+=(--sample-id "$READY_IDS")
  echo "=== 只跑已就緒題：$READY_IDS ==="
else
  echo "=== 跑全部 recent2026（未 wire 服務題會失敗）==="
fi

for m in "${MODELS[@]}"; do
  echo "--- [recent2026] $m $(date '+%T') ---"
  inspect eval ctf/bench27/recent2026_eval.py@recent2026 \
    --model "openai-api/ais3/ais3/$m" \
    "${SEL[@]}" "${COMMON[@]}" \
    --tags bench27,recent2026,"$m"
done
echo "=== recent2026 結束 $(date '+%F %T') ==="
