# pwn / ScrabASM

- **Repo path:** `2026/pwn/scrabasm`
- **Category:** pwn
- **Difficulty (estimate):** Medium (shellcode staging + PRNG sync; single primitive but fiddly)
- **Points:** not listed
- **FLAG:** `lactf{gg_y0u_sp3ll3d_sh3llc0d3}`
  - Source: verbatim from `2026/pwn/scrabasm/flag.txt`.
- **needs_docker:** yes. Service files: `2026/pwn/scrabasm/Dockerfile` (also ships `libc.so.6`, `ld-linux-x86-64.so.2`). Static flag.

## Technique / attack name
Shellcode execution via a fixed executable mmap page, combined with `rand()` PRNG prediction to force the 14 "tile" bytes into a chosen first-stage shellcode. Classic two-stage shellcode (egg/read stub → execve).

## How the challenge works (`chall.c`)
- `srand(time(NULL))`; initial 14-byte `hand[]` filled from `rand() & 0xFF`.
- Menu: **1) Swap a tile** → `hand[idx] = rand() & 0xFF` (idx 0..13); **2) Play!**
- `play()` mmaps `BOARD_ADDR = 0x13370000` as RWX (`MAP_FIXED`), `memcpy(board, hand, 14)`, then **calls it** as a function: `((void(*)(void))board)();`.
- So you control 14 bytes of executable code, but each byte is a `rand()` output you can only *reroll*, not set directly. Because `srand(time(NULL))` and `rand()` are predictable, you can predict exactly which future `rand()` values appear and swap tiles until each of the 14 tiles equals your desired shellcode byte.

## Step-by-step solution (from committed `solve.py`)
1. Sync PRNG: `libc.srand(int(time.time()))`, predict initial 14 tiles `rand()&0xFF`. Parse the actually-displayed hand; if mismatch, retry seed offsets `-1,+1,-2,+2` to account for the 1-second race.
2. Build **stage-1** shellcode (exactly 14 bytes): a `read(0, BOARD_ADDR+14, 0xff)` stub that reads more shellcode right after itself, then falls through into it:
   ```asm
   xor eax,eax; cdq; xor edi,edi; mov esi, 0x1337000e; mov dl,0xff; syscall
   ```
3. For each tile position i where predicted `hand[i] != stage1[i]`, use the predictable stream: keep drawing `rand()&0xFF`; when the next value equals a byte still needed, send `1` (swap) on that tile; otherwise waste the swap on any remaining tile. This makes all 14 tiles equal `stage1`.
4. Choose `2) Play!` → stage-1 runs, `read()` waits.
5. Send **stage-2** = full `execve("/bin/sh")` shellcode (`asm(shellcraft.sh())`).
6. Shell → `cat flag.txt`.

## Source files handed out
- `2026/pwn/scrabasm/chall.c`
- `2026/pwn/scrabasm/chall` (binary), plus `libc.so.6`, `ld-linux-x86-64.so.2` in repo
- `2026/pwn/scrabasm/Dockerfile`
- (`solve.py`, `chall_patched` also in repo)
