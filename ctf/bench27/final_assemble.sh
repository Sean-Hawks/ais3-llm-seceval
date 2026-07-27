#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 1
source .venv/bin/activate
export CYBENCH_ACKNOWLEDGE_RISKS=1
export INSPECT_LOG_DIR=logs/bench27/deep_hard
# 等當前 deep 跑批(2757)結束
while ps -p 2757 >/dev/null 2>&1; do sleep 120; done
echo "=== deep 主批結束，permuted@msg50 補跑 26b/550b $(date '+%F %T') ==="
for m in gemma-4-26b nemotron-3-ultra-550b; do
  inspect eval inspect_evals/cybench -T eval_names=permuted -T variant_names=hard \
    --model "openai-api/ais3/ais3/$m" \
    --epochs 1 --message-limit 50 --time-limit 1800 --max-tool-output 32768 \
    --no-parallel-tool-calls --no-fail-on-error --max-samples 1 \
    --tags bench27,deep_hard,permuted-rerun-msg50,"$m"
done
echo "=== 更新最終表 $(date '+%F %T') ==="
.venv/bin/python ctf/bench27/flag_table.py > ctf/bench27/FLAG_TABLE_FINAL.txt 2>&1
.venv/bin/python ctf/bench27/flag_table.py --md > ctf/bench27/FLAG_TABLE_FINAL.md 2>&1
.venv/bin/python ctf/bench27/extract_transcripts.py > logs/bench27/_final_transcripts.txt 2>&1
tar -czf ctf/bench27/bench27_transcripts.tar.gz -C ctf/bench27 transcripts
echo "=== ALL DONE $(date '+%F %T') ==="
