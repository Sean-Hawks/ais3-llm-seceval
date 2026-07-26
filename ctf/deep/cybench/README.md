# cybench 深度題 case study（推理路徑 vs 專家）

用 cybench 3 題真題分析「模型怎麼推理 vs 專家路徑」。模型跑出多階段 agentic 軌跡 →
抽成 checkpoint 命中 + writeup/指令序列 → 交給詞向量做路徑比對。詞向量評分由使用者自己做。

3 題：`permuted`(crypto/HTB2024)、`delulu`(pwn/HTB2024)、`just_another_pickle_jail`(misc/SekaiCTF2023)。

## 資料夾地圖
```
cybench/
  README.md                 ← 本檔
  RESULTS_pilot.md          ← pilot 結果與三個方法論發現
  trajectory_report.txt     ← 每 run 的 checkpoint 命中 + 指令 digest（extract 產生）
  checkpoints/              ← 專家路徑拆解（詞向量比對目標）
    permuted.json  delulu.json  just_another_pickle_jail.json  README.md
  logs/                     ← 原始 .eval（inspect view 可看）+ run_all.out
  writeups/                 ← 匯出結果（詞向量吃這裡）
    <題>__<模型>.md               人看的 writeup
    <題>__<模型>.commands.txt     模型跑過的指令序列（最乾淨的路徑來源）
    writeups.jsonl                每 run 一列：commands + authored_text
  run_and_writeup.sh        ← 一鍵：跑一次 → 匯出 writeup+指令
  run_cybench_deep.sh       ← 跑整個 26B/70B/550B 階梯
  export_writeups.py        ← .eval → writeups/（含 commands 與 authored_text）
  extract_trajectories.py   ← .eval → checkpoint 命中報告
```

## 一鍵跑（跑一次 → 出 writeup + 指令）
須從 `inspect-test/` 有 `.env`、Docker 開著、已 `pip install inspect_cyber`。
```bash
cd /Users/hawks/Documents/AIS3/inspect-test
ctf/deep/cybench/run_and_writeup.sh gemma-4-26b                 # 3 題一次
ctf/deep/cybench/run_and_writeup.sh nemotron-3-ultra-550b permuted,delulu   # 指定子集
```

## 只重匯出 / 重抽（不重跑模型）
```bash
.venv/bin/python ctf/deep/cybench/export_writeups.py      # logs/ → writeups/
.venv/bin/python ctf/deep/cybench/extract_trajectories.py # logs/ → checkpoint 命中
```

## 看原始軌跡
```bash
.venv/bin/inspect view --log-dir ctf/deep/cybench/logs
```

## 給詞向量的兩種用法
- **比解法路徑**：向量化 `writeups/*.commands.txt`（或 jsonl 的 `commands`）。
- **比推理 vs 專家 checkpoint**：向量化 jsonl 的 `authored_text`，對比 `checkpoints/*.json` 的 `milestone`。
- 兩者都只含模型自己寫的內容（不含 `cat` 出來的原始碼），避免假性相似。
- 每列的 `solved/submitted/challenge/model` 是現成的 key，可標好正解再丟回。

備註：`ctf/deep/` 根目錄的 `A-rsa-wiener/B-z3-crackme/C-stego-chain/` 是**舊的自製深度題**
（被 cybench 取代，仍接在 `ctf_eval.py@ctf_deep`），與本資料夾無關，勿混。
