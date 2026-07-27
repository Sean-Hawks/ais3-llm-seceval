#!/usr/bin/env bash
# 把 27 題（污染12＋近代12＋深難3）的 writeup 整理成命名清晰易懂的一包：wp_27/
# 檔名＝ <C|R|D><NN>_<類別>_<技巧描述>.md ，另出 INDEX.md（出處/難度/解出模型數）
set -eu
cd "$(dirname "$0")/../.."
source .venv/bin/activate
.venv/bin/python ctf/bench27/build_wp27.py
