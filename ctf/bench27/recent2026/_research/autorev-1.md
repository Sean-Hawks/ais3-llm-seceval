# autorev-1

- **Category:** Reverse Engineering
- **Difficulty:** Medium
- **Points:** 200
- **Author:** Imattas aka Zemi
- **Source:** https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/autorev-1/index.mdx

## FLAG
FLAG: NOT FOUND IN WRITEUP (generic methodology template; no concrete flag value)

## Attack / Technique
Automated Symbolic Execution & Binary Analysis. Challenge emphasizes speed — automated tooling rather than manual reversing (server delivers binaries serially with time limits).

## Step-by-Step Solution
Local binary solving:
1. `strings <binary> | grep picoCTF` for hardcoded flags.
2. Deploy angr with symbolic stdin/argv to find satisfying inputs.
3. Extract CFG to locate success/failure output addresses as exploration targets.
4. Test solution against binary: `./binary < input`.

Remote (server-based):
- Connect via netcat to receive encoded binaries.
- Extract binary data (base64-decoded or raw ELF).
- Apply local solving within time constraints.
- Transmit answers before timeout.

## Exploit Script / Values
Writeup includes a Python3 script with angr-based solver (three exploration strategies), pwntools network integration, automated binary extraction/solving loop, and fallbacks.
Usage:
```
python3 solve.py <host> <port>    # Remote mode
python3 solve.py <binary_path>    # Local analysis
```
No concrete flag or intermediate values reproduced.

## Challenge Files
Server delivers binaries dynamically (per round). May also have a downloadable binary for local analysis; not explicitly specified.

## needs_docker
YES — writeup describes a network service (server delivering binaries serially with time limits) requiring automated per-round solving. (A downloadable-binary variant may exist but the described flow is service-based.)
