#!/usr/bin/env bash
# 近代組(recent2026) 交隊友分析包 —— 沿用既有格式：
#   1) transcripts 詞向量素材： recent2026__<題>/<solver>.txt（6 模型 + Opus-4.8）
#   2) wp bundle： recent2026__<題>__{writeup.md,checkpoints.json,frontier_opus.md}
#   3) 近代組 flag/epoch 結果表（ground truth 對照）
set -eu
cd "$(dirname "$0")/../.."                       # → inspect-test/
source .venv/bin/activate
B=ctf/bench27
OUT=$B/handoff_recent2026
rm -rf "$OUT"; mkdir -p "$OUT/transcripts" "$OUT/wp_bundle"

# --- 1) transcripts：只挑 recent2026__*，附 (model,epoch) 索引 ---
cp -R "$B"/transcripts/recent2026__* "$OUT/transcripts/"
{ head -1 "$B/transcripts/_INDEX.csv"; grep '^recent2026,' "$B/transcripts/_INDEX.csv"; } > "$OUT/transcripts/_INDEX.csv"

# --- 2) wp bundle：從各題原始資料夾重建、命名一致 ---
for d in "$B"/recent2026/*/; do
  name=$(basename "$d")
  [ "$name" = "_research" ] && continue
  [ -f "$d/challenge.json" ] || continue
  cp "$d/writeup.md"        "$OUT/wp_bundle/recent2026__${name}__writeup.md"
  cp "$d/checkpoints.json"  "$OUT/wp_bundle/recent2026__${name}__checkpoints.json"
  fm="$B/frontier_manual/${name}.md"
  [ -f "$fm" ] && cp "$fm" "$OUT/wp_bundle/recent2026__${name}__frontier_opus.md"
done

# --- 3) 近代組結果表（flag pass/fail + epoch n/5）---
python "$B/flag_table.py" --md 2>/dev/null > "$OUT/.ft_all.md" || true
{ sed -n '1,2p' "$OUT/.ft_all.md"; sed -n '/recent2026/,/deep_hard/p' "$OUT/.ft_all.md" | sed '$d'; } > "$OUT/RECENT2026_flag_table.md"
rm -f "$OUT/.ft_all.md"
python "$B/dashboard_data.py" 2>/dev/null > "$OUT/recent2026_epoch_data.json" || true

# --- README 說明格式 ---
cat > "$OUT/README.md" <<'EOF'
# Bench27 近代組(recent2026) 分析交付包

2026 賽事題（post-cutoff，LACTF 2026 + BYUCTF 2026 forensics）× 6 受測模型 + Opus 4.8 參考。
每題跑 5 epochs，評分 exact_flag，message-limit 50。**這是最終 5-epoch 資料**。

## 目錄
- `transcripts/recent2026__<題>/<solver>.txt`
  詞向量素材：每個 solver 對該題的 **authored 推理**（模型自己寫的 prose + 下的指令/程式），
  已排除 tool 輸出/檔案 dump。每段標頭都飆出**模型 + 第幾次**：
  `===== MODEL=<模型> · 第 k 次 (EPOCH k) · <題> · solved=C/I =====`（片段被單獨抽出也不失上下文）。
  檔首另有 `# solver=<模型> 題=... epochs=5`。solver = 6 模型（550b/26b/12b/30b/70b/8b）+ `Opus-4.8.txt`（手解參考，attempts=1）。
- `transcripts/_INDEX.csv`  總索引：每列 = (arm, task, **model**, **epoch**, solved, authored_chars)，可直接 key 在 (model,epoch) 上。
- `wp_bundle/recent2026__<題>__writeup.md`      標準解題 writeup
- `wp_bundle/recent2026__<題>__checkpoints.json` 階段 checkpoint（milestone 語意 + anchors 客觀中間值），供詞向量比對／部分分
- `wp_bundle/recent2026__<題>__frontier_opus.md` Opus 4.8 手解路徑（ground-truth-aware 參考，非盲測分）
- `RECENT2026_flag_table.md`     6 模型 + Opus × 12 題 flag 過/沒過
- `recent2026_epoch_data.json`   每 (題×模型) 的 n/總 epoch（解出/已跑）+ Opus 欄

## 誠實框定
Opus 欄＝我方授題、可自由用工具、多為單次的參考解，是「能力上緣／checkpoint 覆蓋」錨點，**非盲測能力分**。
詞向量請對「模型推理」比 checkpoints 語意，勿當能力分（解出≠與 writeup 相似，存在有效非預期解）。
EOF

# --- 打包 ---
tar -czf "$B/bench27_recent2026_transcripts.tar.gz" -C "$OUT" transcripts README.md RECENT2026_flag_table.md recent2026_epoch_data.json
tar -czf "$B/bench27_recent2026_wp_bundle.tar.gz"   -C "$OUT" wp_bundle README.md
# 一個合併全包（transcripts + wp + 表 + README），最省事交付
tar -czf "$B/bench27_recent2026_handoff.tar.gz"     -C "$B"   handoff_recent2026

echo "=== 交付包內容 ==="
echo "transcripts 題數: $(ls -d $OUT/transcripts/recent2026__*/ | wc -l | tr -d ' ')"
echo "wp_bundle 檔數:  $(ls $OUT/wp_bundle/ | wc -l | tr -d ' ') (應=12題×3=36)"
ls -lh "$B"/bench27_recent2026_*.tar.gz
