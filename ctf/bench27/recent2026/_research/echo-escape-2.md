# echo-escape-2

- **Category:** Binary Exploitation (pwn)
- **Difficulty:** Easy
- **Points:** 100
- **Author:** Imattas aka Zemi
- **Source:** https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/echo-escape-2/index.mdx

## FLAG
FLAG: NOT FOUND IN WRITEUP (generic methodology template; no concrete flag value)

## Vulnerability
Format string vulnerability. Developer replaced gets() with fgets() (preventing buffer overflow) but still passes user input directly to printf() without a format specifier.

## Attack / Technique
Format String Exploitation — use %p/%x/%s/%n to read stack memory, leak addresses, and write to arbitrary memory.

## Step-by-Step Solution
Phase 1 — Locate format string offset: send `AAAAAAAA%p.%p.%p...` and find where 0x4141414141414141 (64-bit) appears; that position is the offset.
Phase 2 — Address leaking (PIE only): use `%19$p::%21$p` etc. to extract return/code pointers, compute binary base and target function addresses.
Phase 3 — Memory overwrite: use pwntools fmtstr_payload() for write-what-where targeting a saved return address or a GOT entry (e.g. exit@GOT).
Phase 4 — Trigger: on return or exit(), redirect execution to win() which outputs the flag.

## Exploit Script / Values
Python (pwntools) script with offset discovery, PIE/non-PIE handling, multiple overwrite strategies (GOT vs return address), stack-based flag extraction fallback. Key config:
```
FMT_OFFSET = 6            # empirically determined
WIN_OFFSET_FROM_MAIN = None  # set for PIE binaries
```
No concrete flag reproduced.

## Challenge Files
Not specified in writeup. A binary is implied (format-string pwn). Infrastructure/download details omitted.

## needs_docker
LIKELY YES — pwn challenges of this type run as a remote network service (nc host port); the writeup does not explicitly state it, but format-string-to-win exploitation is typically served over a socket. Treat as network service; a binary download is also typically provided for local analysis.
