#!/usr/bin/env bash
# Bench27 污染組（12 題）全量跑：6 個解題模型 × (7 picoCTF + 5 cybench)
# 用法：cd /path/to/ais3-llm-seceval && bash ctf/bench27/run_contaminated.sh
# 組態全部沿用 bench25 已踩雷驗證的定案值（見 _archive_20260726/bench25/run_bench25.sh 註解）。
set -u

cd "$(dirname "$0")/../.." || exit 1
source .venv/bin/activate

export CYBENCH_ACKNOWLEDGE_RISKS=1
export INSPECT_LOG_DIR=logs/bench27/contaminated
mkdir -p "$INSPECT_LOG_DIR"

# 排除 llama-guard-3-8b（安全分類器非解題模型）。順序＝論證價值遞減（26B/550B/70B 先保）。
MODELS=(
  gemma-4-26b
  nemotron-3-ultra-550b
  llama-3.3-70b
  gemma-4-12b
  nemotron-cascade-2-30b
  llama-3.1-8b
)

# 污染組 picoCTF 7 題（intercode sample id = task_id）：
#   5 crypto/ROT13, 44 rev/Java, 13 rev/keygen, 37 misc/unzip, 34 misc/字典爆破,
#   94 forensics/strings, 8 forensics/EXIF
INTERCODE_IDS='[5,8,13,34,37,44,94]'
# 污染組 cybench 5 題：slcg(crypto) missingbits(crypto) back_to_the_past(web)
#   glacier_exchange(web) network_tools(pwn)
CYBENCH_TASKS=slcg,missingbits,back_to_the_past,glacier_exchange,network_tools

EPOCHS=5            # 過夜跑（2026-07-26 夜）：5 epochs 出 95% CI
MSG_LIMIT=50        # 對齊 InterCode 上游 max_messages；配 --no-parallel-tool-calls，勿調低
TIME_LIMIT=1800     # 牆鐘保險（非吞吐不變量）；正常每題僅數十秒碰不到
MAX_TOOL_OUT=32768  # 預截斷大檔輸出，防灌爆 context
MAX_SAMPLES_INTERCODE=5
MAX_SAMPLES_CYBENCH=6

# --no-parallel-tool-calls 必要：gateway 回 400 "single tool-calls at once"，否則整題記 error
COMMON=(
  --epochs "$EPOCHS"
  --message-limit "$MSG_LIMIT"
  --time-limit "$TIME_LIMIT"
  --max-tool-output "$MAX_TOOL_OUT"
  --no-parallel-tool-calls
  --no-fail-on-error
)

echo "=== Bench27 contaminated 開始 $(date '+%F %T') ==="
for m in "${MODELS[@]}"; do
  echo "=== [model] $m 開始 $(date '+%T') ==="

  echo "--- [intercode] $m $(date '+%T') ---"
  inspect eval inspect_evals/gdm_intercode_ctf \
    --model "openai-api/ais3/ais3/$m" \
    -T "sample_ids=$INTERCODE_IDS" \
    --max-samples "$MAX_SAMPLES_INTERCODE" \
    "${COMMON[@]}" \
    --tags bench27,contaminated,intercode,"$m"

  echo "--- [cybench] $m $(date '+%T') ---"
  inspect eval inspect_evals/cybench \
    --model "openai-api/ais3/ais3/$m" \
    -T eval_names="$CYBENCH_TASKS" \
    -T variant_names=hard \
    --max-samples "$MAX_SAMPLES_CYBENCH" \
    "${COMMON[@]}" \
    --tags bench27,contaminated,cybench,"$m"

  echo "=== [model] $m 完成 $(date '+%T') ==="
done
echo "=== Bench27 contaminated 結束 $(date '+%F %T') ==="

# recent2026 12 題＝自訂 task（picoCTF2026/LACTF2026），尚未接入 → 見 run_recent2026.sh（待建）。
# deep_hard 3 題＝沿用 ../deep/cybench/run_cybench_deep.sh。
