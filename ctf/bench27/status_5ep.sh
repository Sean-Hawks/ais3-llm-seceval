#!/usr/bin/env bash
# 快照：目前跑到哪、各組完成的 top-level eval 數、當前 eval 的 working_time
cd "$(dirname "$0")/../.." || exit 1
echo "=== $(date '+%F %T') ==="
if pgrep -f overnight_5ep.sh >/dev/null; then echo "overnight_5ep.sh: ALIVE"; else echo "overnight_5ep.sh: NOT RUNNING"; fi
CUR=$(ps aux | grep "inspect eval" | grep -v grep | grep -oE 'ais3/[a-z0-9.-]+ ' | head -1)
echo "current model: ${CUR:-<none>}"
echo "current stage tags:"; ps aux | grep "inspect eval" | grep -v grep | grep -oE 'recent2026|deep_hard' | head -1
echo "recent2026 top-level .eval: $(ls logs/bench27/recent2026/*.eval 2>/dev/null | wc -l | tr -d ' ')"
echo "deep_hard  top-level .eval: $(ls logs/bench27/deep_hard/*.eval 2>/dev/null | wc -l | tr -d ' ')"
echo "--- last 6 stage markers ---"
grep -E '=====|##########' logs/bench27/overnight_5ep.out 2>/dev/null | tail -6
