#!/usr/bin/env bash
# Compatibility entry point. Preview by default; pass --execute to call models.
set -euo pipefail
cd "$(dirname "$0")/../.."
AIS3_PYTHON="${AIS3_PYTHON:-python3}"
if [[ -x .venv/bin/python ]]; then AIS3_PYTHON=.venv/bin/python; fi
exec "$AIS3_PYTHON" -m ais3_bench run --arm recent2026 --model all "$@"
