#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 1
O2=34073
echo "=== chain_services 啟動 $(date '+%F %T')，等 overnight2 PID $O2 ==="
while kill -0 "$O2" 2>/dev/null; do sleep 60; done
echo "=== overnight2 結束 $(date '+%F %T')，開始 5 服務題（各 compose 首建映像會較久）==="
sleep 20
bash ctf/bench27/run_recent2026_services.sh
echo "=== chain_services 全部結束 $(date '+%F %T') ==="
