#!/usr/bin/env bash
# 加速版 pipeline（msg-limit 25，跳過 deep）：
#  ① 70b 補跑近代唯一缺的 rev_flag-finder
#  ② 12b/30b/8b 跑全 7 近代靜態
#  ③ 5 服務題 × 6 模型
set -u
cd "$(dirname "$0")/../.." || exit 1
source .venv/bin/activate
export CYBENCH_ACKNOWLEDGE_RISKS=1
export INSPECT_LOG_DIR=logs/bench27/recent2026
mkdir -p "$INSPECT_LOG_DIR"
C=(--epochs 1 --message-limit 25 --time-limit 1800 --max-tool-output 32768 --no-parallel-tool-calls --no-fail-on-error)
echo "=== overnight3 開始 $(date '+%F %T') ==="
echo "### ① 70b 補 rev_flag-finder ###"
inspect eval ctf/bench27/recent2026_eval.py@recent2026 --model openai-api/ais3/ais3/llama-3.3-70b \
  --sample-id rev_flag-finder "${C[@]}" --tags bench27,recent2026,llama-3.3-70b
echo "### ② 12b/30b/8b 全 7 近代靜態 ###"
bash ctf/bench27/run_recent2026.sh
echo "### ③ 5 服務題 × 6 模型 ###"
bash ctf/bench27/run_recent2026_services.sh
echo "=== overnight3 全部結束 $(date '+%F %T') ==="
