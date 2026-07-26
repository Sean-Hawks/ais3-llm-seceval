#!/usr/bin/env bash
# 修正後的近代靜態(7題×6模型) → deep_hard(3×6)，串接（gateway 序列化，勿併行）
set -u
cd "$(dirname "$0")/../.." || exit 1
echo "=== overnight2 開始 $(date '+%F %T') ==="
echo "### 近代組（修正版，7 靜態題）###"
bash ctf/bench27/run_recent2026.sh
echo "### deep_hard 3 題 ###"
bash ctf/bench27/run_deep_hard.sh
echo "=== overnight2 全部結束 $(date '+%F %T') ==="
