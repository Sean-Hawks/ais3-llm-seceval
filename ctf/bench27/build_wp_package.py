#!/usr/bin/env python3
"""打包 Bench27 全部 wp（命名清晰）：
  wp_27/            標準解答（C/R/D 清楚命名 + checkpoints + Opus 手解）
  agent_wp/         27題 × 7 solver × 5 epoch = 945 模型/Opus 實際解題 transcript
產出 agent_wp/INDEX.md（7 solver 總表）+ 頂層 README，tar 成 bench27_wp_945.tar.gz。"""
import json, os, collections, subprocess
ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS = ["550b","26b","12b","30b","70b","8b"]
runs = json.load(open(os.path.join(ROOT,"bench27_runs.json"),encoding="utf-8"))
opus = json.load(open(os.path.join(ROOT,"opus_runs.json"),encoding="utf-8"))
TASKS = json.load(open(os.path.join(ROOT,"opus_tasks.json"),encoding="utf-8"))
tid2clear = {t["tid"]: t["clear"] for t in TASKS}
clear2tid = {t["clear"]: t["tid"] for t in TASKS}

# 模型 n/t per (tid,model)
cell = collections.defaultdict(lambda: [0,0])
for r in runs:
    if r["model"] in MODELS:
        cell[(r["task"], r["model"])][0] += r["solved"]; cell[(r["task"], r["model"])][1] += 1

clears = sorted(os.path.basename(d) for d in [p for p in __import__("glob").glob(os.path.join(ROOT,"agent_wp","*")) if os.path.isdir(p)])
lines = ["# Bench27 — Agent 實際解題 wp 總表（27 題 × 7 solver × 5 epoch = 945）\n",
         "每格 = 該 solver 解出 epoch 數 / 5。solver = 6 受測模型（550b→8b）+ **Opus-4.8 盲解**（頂端標準，同一份題檔）。\n",
         "檔案：`<清楚題名>/<solver>.md`（含 5 次嘗試的推理+指令）。標準解答見 `../wp_27/`。\n",
         "| 題 | 550b | 26b | 12b | 30b | 70b | 8b | **Opus** |",
         "|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|"]
for clear in clears:
    tid = clear2tid.get(clear, clear)
    row = [clear]
    for m in MODELS:
        s,t = cell.get((tid,m),[0,0]); row.append(f"{s}/{t}" if t else "·")
    o = opus.get(tid); row.append(f"**{o['n']}/{o['t']}**" if o else "·")
    lines.append("| "+" | ".join(row)+" |")
open(os.path.join(ROOT,"agent_wp","INDEX.md"),"w",encoding="utf-8").write("\n".join(lines)+"\n")

readme = """# Bench27 Writeup 包

27 題 CTF（污染12 + 近代12 + 深難3）× 語言模型資安評測。

## 內容
- **`wp_27/`** — 標準解答（人寫），命名 `<C=污染|R=近代|D=深難><NN>_<類別>_<技巧>.md`
  - `_checkpoints/` 階段錨點（客觀中間值，供部分分/詞向量）
  - `_frontier_opus/` Opus 手解參考路徑
  - `INDEX.md` 出處/難度/解出模型數
- **`agent_wp/`** — 每個 solver **實際跑出來**的解題過程（推理+指令+輸出）
  - `<清楚題名>/<solver>.md`，solver = 550b/26b/12b/30b/70b/8b + **Opus-4.8**
  - 27 題 × 7 solver × 5 epoch = **945** 段
  - `INDEX.md` 7-solver 總表（每格 n/5）

## 誠實框定
- 評分 exact_flag、pass@any；harness/生成錯誤樣本已排除（少數標 ⚠ = context 溢位等，非能力）。
- **Opus 欄 = 盲解 5-epoch**：與 6 受測模型看同一份題檔（不看 solution/writeup/checkpoints），公平能力上緣。
- Opus 成績：pass@any 25/27；未過＝ooo（異體字精確重現）、tic-tac-no（pwn jail）；部分＝nonogram 3/5、scrabasm/pickle 1/5。
"""
open(os.path.join(ROOT,"_WP_PACKAGE_README.md"),"w",encoding="utf-8").write(readme)

# 組裝 + tar
pkg = os.path.join(ROOT,"wp_package")
subprocess.run(["rm","-rf",pkg]); os.makedirs(pkg)
subprocess.run(["cp","-R",os.path.join(ROOT,"wp_27"),os.path.join(pkg,"wp_27")])
subprocess.run(["cp","-R",os.path.join(ROOT,"agent_wp"),os.path.join(pkg,"agent_wp")])
subprocess.run(["cp",os.path.join(ROOT,"_WP_PACKAGE_README.md"),os.path.join(pkg,"README.md")])
tar = os.path.join(ROOT,"bench27_wp_945.tar.gz")
subprocess.run(["tar","-czf",tar,"-C",ROOT,"wp_package"])
sz = os.path.getsize(tar)//1024
nfiles = sum(len(f) for _,_,f in os.walk(pkg))
print(f"打包完成 {tar}  ({sz}K, {nfiles} 檔)")
print(f"  wp_27: {len(os.listdir(os.path.join(pkg,'wp_27')))} 項  agent_wp: {len([d for d in os.listdir(os.path.join(pkg,'agent_wp')) if os.path.isdir(os.path.join(pkg,'agent_wp',d))])} 題")
