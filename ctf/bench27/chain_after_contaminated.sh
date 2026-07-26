#!/usr/bin/env bash
# 夜間串接器：等污染組跑完 → 接力跑近代組(已就緒 5 題) → deep_hard 3 題。
# 刻意「串接」而非併行：污染組 cybench 階段會同時開多個 Docker sandbox，
# 本機僅 7.8GB RAM 且另有使用者 fuzzing 容器常駐，併行第二個 inspect eval 有 OOM 風險，
# 會拖垮最優先的污染組。串接可安全利用夜間、又不威脅 Task A。
# 用法：cd inspect-test && nohup bash ctf/bench27/chain_after_contaminated.sh <CONTAM_PID> > logs/bench27/chain.out 2>&1 &
set -u
cd "$(dirname "$0")/../.." || exit 1

CONTAM_PID="${1:?need contaminated run_contaminated.sh PID}"
echo "=== chain 啟動 $(date '+%F %T')，等待污染組 PID $CONTAM_PID 結束 ==="

# 輪詢等待污染組主腳本結束（每 60s 檢查一次；kill -0 探活不送訊號）
while kill -0 "$CONTAM_PID" 2>/dev/null; do
  sleep 60
done
echo "=== 污染組 PID $CONTAM_PID 已結束 $(date '+%F %T')，開始近代組 ==="

# 讓 Docker 沉澱、釋放 RAM
sleep 30

echo "=== [chain] 近代組(已就緒 5 題) $(date '+%T') ==="
bash ctf/bench27/run_recent2026.sh

echo "=== [chain] deep_hard 3 題 $(date '+%T') ==="
if [ -f ctf/deep/cybench/run_cybench_deep.sh ]; then
  bash ctf/deep/cybench/run_cybench_deep.sh
else
  echo "!! ctf/deep/cybench/run_cybench_deep.sh 不存在，跳過 deep_hard"
fi

echo "=== chain 全部結束 $(date '+%F %T') ==="
