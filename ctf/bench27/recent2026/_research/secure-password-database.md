# secure-password-database

- **Category:** Reverse Engineering
- **Difficulty:** Medium
- **Points:** 200
- **Author:** Imattas aka Zemi
- **Source:** https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/secure-password-database/index.mdx

## FLAG
FLAG: NOT FOUND IN WRITEUP (generic methodology template; no concrete flag value)

## Overview
A password authentication binary that "shows you the password you entered saved in the database." Core task: reverse-engineer how the program transforms input and compares against a stored value.

## Attack / Technique
Six escalating techniques (cheap-to-expensive):
1. String extraction — `strings` for plaintext flag.
2. Library tracing — `ltrace -s 256` to capture strcmp/memcmp arguments during execution.
3. I/O transformation analysis — probe with known inputs (e.g. `AAAA`) to deduce encoding/XOR key/substitution.
4. Disassembly — `objdump` for hardcoded comparison values and .rodata; Ghidra for static analysis.
5. XOR brute-force — single-byte XOR keys against binary data.
6. Debugger automation — GDB breakpoints at comparison functions to extract register values.

The "database representation" display leaks transformation logic; testing repeated characters reveals invertible XOR/substitution patterns.

## Exploit Script / Values
Writeup includes a Python `solve.py` implementing all six approaches with exception handling. No concrete flag or values reproduced.

## Challenge Files
A binary is provided (implied by strings/ltrace/objdump/Ghidra/GDB workflow). No explicit file name or download URL given.

## needs_docker
NO — static file (binary) challenge; no network service required.
