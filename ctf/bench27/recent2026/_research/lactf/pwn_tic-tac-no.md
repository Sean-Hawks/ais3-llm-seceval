# pwn / tic-tac-no

- **Repo path:** `2026/pwn/tic-tac-no`
- **Category:** pwn
- **Difficulty (estimate):** Easy (logic / out-of-bounds global write; no ROP)
- **Points:** not listed
- **FLAG:** `lactf{th3_0nly_w1nn1ng_m0ve_1s_t0_p1ay}`
  - Source: verbatim from `2026/pwn/tic-tac-no/challenge.yaml` (`flag:` field).
- **needs_docker:** yes (to actually receive flag.txt over the service). Service file: `2026/pwn/tic-tac-no/Dockerfile`. Flag also present inline in challenge.yaml.
- **NOTE:** No committed `solve.py` — technique below is derived from source `chall.c` (read-only). Vulnerability is unambiguous.

## Technique / attack name
Out-of-bounds array write via unchecked index into adjacent global variables. Beat the "perfect" minimax bot by corrupting the `computer` symbol.

## How the challenge works (`chall.c`)
Globals declared consecutively: `char board[9];` then `char player = 'X';` then `char computer = 'O';`.
`playerMove()` computes `index = (x-1)*3 + (y-1)` from two `scanf("%d")` values. The guard is:
```c
if(index >= 0 && index < 9 && board[index] != ' '){ printf("Invalid move.\n"); }
else { board[index] = player; break; }   // OOB write when index<0 or index>=9
```
So any index **outside [0,9)** is written unconditionally with `'X'` (`player`). The globals `player` (offset +9) and `computer` (offset +10) sit right after `board`.
Winner is checked by `checkWin()` on lines of three equal non-space cells; if `winner == player ('X')` the program prints `flag.txt`.

## Step-by-step solution
1. First move: pick row/col that yield **index 10** to overwrite the `computer` global with `'X'`:
   `(x-1)*3 + (y-1) = 10` → e.g. `x=4, y=2` (`3*3 + 1 = 10`). Now `computer == 'X'`.
2. With `computer == 'X' == player`, the "perfect bot" (`perfectComputerMove`) now places `'X'` too, and minimax maximizes for `'X'`. Every mark on the board is `'X'`.
3. Continue making any legal in-range moves; a line of three `'X'` quickly forms → `checkWin()` returns `'X'`, `winner == player`, and the program opens `flag.txt` and prints it.
   (Equivalently: overwriting `computer` means the bot can never place `'O'`, so you cannot lose and will complete a three-in-a-row.)

## Source files handed out
- `2026/pwn/tic-tac-no/chall.c`
- `2026/pwn/tic-tac-no/chall` (compiled binary)
- `2026/pwn/tic-tac-no/Dockerfile`
