# undo

- **Category:** General Skills / Misc
- **Difficulty:** Easy
- **Points:** 100
- **Author:** Imattas aka Zemi
- **Source:** https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/undo/index.mdx

## FLAG
FLAG: NOT FOUND IN WRITEUP (generic methodology template; no concrete flag value)

## Overview
Reverse a pipeline of Linux text transformations to recover a picoCTF{...} flag.

## Attack / Technique
Linux Text Transformation Reversal — apply inverse functions in reverse order.

## Step-by-Step Solution
1. Identify the transformation pipeline (from instructions or provided scripts).
2. Map each forward transform to its inverse:
   - base64 -> base64 -d
   - rev -> rev (self-inverse)
   - tr 'a-z' 'A-Z' -> tr 'A-Z' 'a-z'
   - rot13 -> rot13 (self-inverse)
3. Apply inverses in reverse order (e.g. forward `base64 | rev | tr_upper` undoes as `tr_lower | rev | base64 -d`).
4. Validate intermediate steps.
5. Verify final output matches picoCTF{...}.

## Exploit Script / Values
Python3 `solve.py`: accepts transformed file/stdin, `--transformations` spec, smart detection (base64/hex/case), bounded brute-force. Usage:
```
python3 solve.py transformed.txt -t "base64 rev tr_upper"
cat data.txt | python3 solve.py - --brute-force --max-depth 5
```
No concrete flag reproduced.

## Challenge Files
References a "transformed file" (e.g. transformed.txt); no download link. Provided by platform.

## needs_docker
NO — static file challenge, no network service.
