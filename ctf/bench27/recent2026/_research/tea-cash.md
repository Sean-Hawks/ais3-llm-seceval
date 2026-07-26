# tea-cash

- **Category:** Binary Exploitation (pwn)
- **Difficulty:** Easy
- **Points:** 100
- **Author:** Imattas aka Zemi
- **Source:** https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/tea-cash/index.mdx

## FLAG
FLAG: NOT FOUND IN WRITEUP (generic methodology template; no concrete flag value)

## Overview
Exploiting glibc tcache (thread-local caching). Program stores a flag in an allocated chunk, then frees it; recover the flag from freed memory.

## Key Vulnerability
"free() does not zero out chunk data — a freed chunk still holds whatever the program wrote into it." Freed chunk data persists in the tcache free list.

## Attack / Technique
Tcache Chunk Reclamation / Use-After-Free. Tcache LIFO behavior: after the flag chunk is freed, allocating a new chunk of the same size returns the identical memory location with flag data intact.

## Step-by-Step Solution
1. Connect to the service and identify menu operations.
2. Determine the chunk size holding the flag.
3. Allocate a new chunk of matching size (tcache returns the freed chunk).
4. Read the newly allocated chunk to retrieve the flag.
5. Alternatively, exploit a "traverse free list" feature if provided.

## Exploit Script / Values
Python (pwntools) script implementing three strategies: menu-based interaction with flag-pattern extraction, tcache chunk reclamation via reallocation, exhaustive menu exploration + output dumping. No concrete flag or values reproduced.

## Challenge Files
References a local binary `./tea-cash` and remote service connection details. Explicit download instructions not provided.

## needs_docker
YES — requires a running network service (pwn/heap challenge). A binary (`tea-cash`) is also referenced for local analysis.
