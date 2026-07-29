#!/usr/bin/env bash
# arm64 修復後重跑 4 個 pwn 服務題（原本 victim 在 arm64 起不來＝假失敗）：
#   recent2026: pwn_tic-tac-no / pwn_scrabasm（改 socat 版 victim，繞開 nsjail seccomp）
#   cybench:    network_tools（contaminated）/ delulu（deep_hard）（victim compose 加 platform: linux/amd64）
# 全部 6 模型串接、5 epochs。嚴禁與其他 inspect eval 併行（gateway starvation）。
# 新 log 進各自 arm 的 logdir；export_runs_json.py 會以最新 log 覆蓋舊壞資料（已加去重）。
set -u
cd "$(dirname "$0")/../.." || exit 1
source .venv/bin/activate
export CYBENCH_ACKNOWLEDGE_RISKS=1

MODELS="gemma-4-26b nemotron-3-ultra-550b llama-3.3-70b gemma-4-12b nemotron-cascade-2-30b llama-3.1-8b"
EPOCHS="${EPOCHS:-5}"   # 預設 5-epoch（出 CI）；隊友急用可 EPOCHS=1 bash ... 先跑一輪
COMMON="--epochs $EPOCHS --message-limit 50 --time-limit 1800 --max-tool-output 32768 --no-parallel-tool-calls --no-fail-on-error"

echo "########## ARM64 PWN FIX RERUN START $(date '+%F %T') · EPOCHS=$EPOCHS ##########"

# ---------- 預建 victim image（不計入樣本 time-limit）----------
echo "----- prebuild victims $(date '+%T') -----"
( cd ctf/bench27/recent2026/pwn_tic-tac-no && docker compose build victim ) 2>&1 | tail -1
( cd ctf/bench27/recent2026/pwn_scrabasm  && docker compose build victim ) 2>&1 | tail -1
docker pull --platform linux/amd64 aisiuk/evals-cybench-network_tools-victim 2>&1 | tail -1
docker pull --platform linux/amd64 aisiuk/evals-cybench-delulu-victim        2>&1 | tail -1

# ---------- 階段一：recent2026 pwn 2 題 ----------
export INSPECT_LOG_DIR=logs/bench27/recent2026
for m in $MODELS; do
  echo "===== RECENT pwn :: $m :: $(date '+%F %T') ====="
  inspect eval ctf/bench27/recent2026_eval.py@recent2026 \
    --model "openai-api/ais3/ais3/$m" --sample-id "tic-tac-no,scrabasm" \
    $COMMON --max-samples 2 --tags bench27,recent2026,arm64fix,"$m"
done

# ---------- 階段二：cybench network_tools（contaminated）----------
export INSPECT_LOG_DIR=logs/bench27/contaminated
for m in $MODELS; do
  echo "===== CYBENCH network_tools :: $m :: $(date '+%F %T') ====="
  inspect eval inspect_evals/cybench -T eval_names=network_tools -T variant_names=hard \
    --model "openai-api/ais3/ais3/$m" \
    $COMMON --max-samples 6 --tags bench27,contaminated,cybench,arm64fix,"$m"
done

# ---------- 階段三：cybench delulu（deep_hard）----------
export INSPECT_LOG_DIR=logs/bench27/deep_hard
for m in $MODELS; do
  echo "===== CYBENCH delulu :: $m :: $(date '+%F %T') ====="
  inspect eval inspect_evals/cybench -T eval_names=delulu -T variant_names=hard \
    --model "openai-api/ais3/ais3/$m" \
    $COMMON --max-samples 3 --tags bench27,deep_hard,cybench,arm64fix,"$m"
done

echo "########## ARM64 PWN FIX RERUN DONE $(date '+%F %T') ##########"
