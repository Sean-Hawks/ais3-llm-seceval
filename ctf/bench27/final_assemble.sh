#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 1
while ps -p 22917 >/dev/null 2>&1; do sleep 120; done
echo "=== 服務題結束，彙整 $(date '+%F %T') ==="
.venv/bin/python ctf/bench27/extract_transcripts.py > logs/bench27/_final_transcripts.txt 2>&1
tar -czf ctf/bench27/bench27_transcripts.tar.gz -C ctf/bench27 transcripts
.venv/bin/python ctf/bench27/flag_table.py > ctf/bench27/FLAG_TABLE_FINAL.txt 2>&1
.venv/bin/python ctf/bench27/flag_table.py --md > ctf/bench27/FLAG_TABLE_FINAL.md 2>&1
echo "=== final_assemble 完成 $(date '+%F %T') ==="
