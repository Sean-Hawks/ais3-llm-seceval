#!/usr/bin/env bash
# Bench25 全量正式跑：6 個解題模型 × 25 題
# 用法：cd /path/to/ais3-llm-seceval && bash ctf/bench25/run_bench25.sh
set -u

cd "$(dirname "$0")/../.." || exit 1
source .venv/bin/activate

export CYBENCH_ACKNOWLEDGE_RISKS=1
export INSPECT_LOG_DIR=logs/bench25
mkdir -p "$INSPECT_LOG_DIR"

# llama-guard-3-8b 是安全分類器不是解題模型，故排除
#
# ★ 順序＝「論證價值遞減」而非參數量遞增（2026-07-25 20:55 重排，第 4 次中止後）。
#   理由：這批已被中斷四次，per-model 排程下任何時點中止都會拿到「數個完整模型」，
#   所以先跑的模型就是保得住的模型。報告的核心主張是「非單調 scaling」，
#   它需要 26B / 550B / 70B 這三個點；8b 與 30b 只是階梯填充。
#   而 8b 恰好是最沒用又最貴的：撞 message limit 最多（intercode 5 題撞 2 題）、
#   硬題沙箱多次 docker 崩潰、數據信度最低。原本讓它打頭陣會吃掉約 50 分鐘夜間視窗，
#   凌晨若掛掉就只剩「8b + 12b 完整」＝論證最不需要的兩個。故降到最後。
MODELS=(
  gemma-4-26b             # 1. v2 最高分之一，非單調主張的上端
  nemotron-3-ultra-550b   # 2. 階梯頂端，飽和與否的關鍵
  llama-3.3-70b           # 3. 非單調主張的下端（26B > 70B 就靠這題）
  gemma-4-12b             # 4. 「廣而亂」代表（II 解耦）
  nemotron-cascade-2-30b  # 5. 階梯填充
  llama-3.1-8b            # 6. 地板值；撞限多、崩最兇、信度最低，放最後
)

CYBENCH_TASKS=slcg,partial_tenacity,permuted,robust_cbc,packedaway,crushing,rpgo,sop,eval_me,data_siege,avatar,unbreakable,just_another_pickle_jail,flag_command,back_to_the_past,labyrinth_linguist,chunky,delulu,network_tools
# ★ 已移除 id 12（RSA 分解）：n 是 270-bit 半質數，picoCTF 原解法要查 factordb，
#   但 InterCode 沙箱 network_mode:none 且未裝 GNFS 工具 → 本 harness 無解。
#   它同時是最貴的一題（模型真的去跑 Fermat 1M 迭代／Pollard p-1）：
#   12b 花 813s、8b 花 368s，佔單次 eval 牆鐘 93%。跑它既無訊號又燒掉約 1 小時。
#   證據保留在 logs/bench25/_aborted/，儀表板仍以 ⊘ 標示並排除計分。
INTERCODE_IDS='[3,5,37,44,94]'

EPOCHS=1          # 基線用 1；出 CI 需另跑 >=5
# MSG_LIMIT=50 對齊 InterCode 上游預設 max_messages=50（cybench 上游不設上限）。
# 不可再調低：實測 30 時 llama-3.1-8b 六題有五題撞限 → 測到的是預算不是能力。
# 且與 --no-parallel-tool-calls 配套（關平行呼叫會多耗訊息）。
MSG_LIMIT=50
# TIME_LIMIT 900 → 1800（2026-07-25 23:30，實測踩雷後修正）。
# ★ 這個上限是「牆鐘」，不是 working time，所以它不是吞吐不變量。
#   實測：8b cybench 在 gateway 掉到約 1 tok/s 的時段，19 題有 3 題被 900s 砍斷——
#     partial_tenacity 0.8 tok/s，50 則訊息預算只用掉 12 則就結束
#     unbreakable      0.9 tok/s，36/50
#     network_tools    1.8 tok/s，34/50
#   （同模型正常中位是 93 tok/s，即慢了 50–100 倍。）
#   模型根本沒拿到預算卻被記成「解不出來」＝ harness confound，非能力訊號。
# 拉到 1800 的目的是讓 --message-limit 50（吞吐不變量）永遠先咬到，
# 使分數在觀測到的吞吐範圍內與 gateway 速度無關；time-limit 只當防跑飛的保險。
# gateway 正常時每題僅 10–33 秒，這個上限根本碰不到，不會拖慢跑批。
TIME_LIMIT=1800
# docker 只有 8 CPU / 7.8GB RAM。InterCode 容器輕（共用 255MB ubuntu image、
# 無 victim service）故可較高並行。
# cybench 原設 2（保守估 Kali sandbox＋victim 很重），2026-07-25 實測推翻此假設：
#   8b cybench 跑 576s 完成 6 題 → 每題牆鐘 96s，但模型只佔 27s，
#   **86% 的牆鐘是每題起停一次 docker compose 的開銷**（I/O bound，可線性並行化）。
#   同時量到：15 個容器合計 <800MB / 7.8GB、CPU 近 0%、working/total ratio 0.98–1.00
#   （即無 gateway 排隊）→ 瓶頸既非 RAM 也非 CPU 也非 API，就是容器 churn。
# 故調到 6。不再往上是因為 550B 會在容器內跑真運算（gdb/解密），8 CPU 會開始競爭。
# ⚠ 判讀注意：--time-limit 900 是「牆鐘」不是 working time。並行度拉高後若塞車，
#   題目可能因排隊撞 900s 被誤記成解不出來。分析時須檢查撞 time limit 的題的
#   working/total ratio，ratio 偏低者為 harness confound，不可當能力訊號。
MAX_SAMPLES_INTERCODE=5
MAX_SAMPLES_CYBENCH=6
MAX_TOOL_OUT=32768  # 工具輸出預截斷 32KB，防大檔灌爆 context（70B-permuted 教訓）

# ★ --no-parallel-tool-calls 是必要的：此 gateway 回
#   400 "This model only supports single tool-calls at once!"，
#   而 Inspect 預設 agent prompt 會鼓勵平行 tool call → 整題記 error。
#   六個模型都必須套用，否則測到的是 gateway 限制不是模型能力。
COMMON=(
  --epochs "$EPOCHS"
  --message-limit "$MSG_LIMIT"
  --time-limit "$TIME_LIMIT"
  --max-tool-output "$MAX_TOOL_OUT"
  --no-parallel-tool-calls
  --no-fail-on-error
)

echo "=== Bench25 開始 $(date '+%F %T') ==="

# 每個模型「一次跑完 24 題」：同一模型內先 intercode 5 題再 cybench 19 題，
# 跑完才換下一個模型。這批已被中斷三次，per-model 排程的好處是任何時點中止都會
# 拿到「數個完整模型的 24 題」而不是「六個模型的半套」。
# 注意仍是兩次 inspect eval（兩個 task 的 -T 參數不同、max-samples 也不同：
# intercode 輕量可 5、cybench 每題起 Kali sandbox＋victim 只能 2），
# 併成單一進程會被迫共用一個全域 max_samples → 8CPU/7.8GB 上有 OOM 風險。
for m in "${MODELS[@]}"; do
  echo "=== [model] $m 開始 $(date '+%T') ==="

  # --- InterCode 5 題（已移除無解的 id 12；輕量、無 victim service）---
  echo "--- [intercode] $m $(date '+%T') ---"
  inspect eval inspect_evals/gdm_intercode_ctf \
    --model "openai-api/ais3/ais3/$m" \
    -T "sample_ids=$INTERCODE_IDS" \
    --max-samples "$MAX_SAMPLES_INTERCODE" \
    "${COMMON[@]}" \
    --tags bench25,intercode,"$m"

  # --- cybench 19 題（慢，10 題要起 victim service）---
  echo "--- [cybench] $m $(date '+%T') ---"
  inspect eval inspect_evals/cybench \
    --model "openai-api/ais3/ais3/$m" \
    -T eval_names="$CYBENCH_TASKS" \
    -T variant_names=hard \
    --max-samples "$MAX_SAMPLES_CYBENCH" \
    "${COMMON[@]}" \
    --tags bench25,cybench,"$m"

  echo "=== [model] $m 完成 $(date '+%T') ==="
done

echo "=== Bench25 結束 $(date '+%F %T') ==="
