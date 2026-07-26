# misc_error-correction — frontier reference solve
- arm: recent2026 / category: misc / difficulty: medium / source: LACTF 2026 (Feb 2026, post-cutoff, contaminated: false)
- ground-truth flag (from checkpoints): `lactf{Th15_15_pr0b481y_n07_wh47_7h3y_m34n7_8y_3rr0r_c0rr3c710n_CVOD5Jp7IOq+XgR}`
- my derived flag: `lactf{Th15_15_pr0b481y_n07_wh47_7h3y_m34n7_8y_3rr0r_c0rr3c710n_CVOD5Jp7IOq+XgR}`
- SOLVED: yes

## Inputs examined (files/ only)
- `files/chall.py` — generator. `segno.make(flag, mode='byte', error='L', boost_error=False, version=7)` → 45×45 module QR. The module grid is diced into a 5×5 arrangement of 9×9-module blocks (25 blocks), indexed `code[405*y+45*ysub+9*x : 405*y+45*ysub+9*(x+1)]`; `random.shuffle(chunks)` permutes them (no seed saved → not recoverable from the script); result is upscaled 10×/NEAREST to 450×450 and saved as `chall.png`.
- `files/chall.png` — the 450×450 scrambled QR.

## Solution path (my independent reasoning, pre-checkpoint)
1. **Downsample**: sampled every 10 px (module centre) → 45×45 0/1 grid; sliced into 25 pieces of 9×9. The shuffle is unseeded, so the permutation must come from QR structure, not from `chall.py`.
2. **Pin the frame (function patterns)**: generated ~500 random *full-length* version-7-L QRs with segno and took the modules constant across all of them → the 432 mask-independent function modules (3 finders + separators, both timing lines, 6 alignment patterns, dark module, version-7 version-info blocks). (Using short random strings first gave false "constant" modules from shared padding — fixed by using near-capacity contents.) Scored each of the 25 pieces against each of the 25 grid slots over these anchors and solved the assignment (Hungarian / `linear_sum_assignment`). Result: **432/432 anchor agreement** — the frame (finders/timing/alignment/version info) is reconstructed exactly. This uniquely pins 11 of 25 blocks; the other **14 are near-pure-data blocks** (10 have zero function anchors) and remain ambiguous.
3. **Realise error-correction alone can't place them**: level-L RS on version 7 is 2 blocks of (98,78), i.e. corrects only ~10 codeword errors/block; a wrong arrangement of 14 blocks corrupts ~120 codewords → far beyond capacity. The blocks must be placed essentially exactly. Anchor scoring gives no gradient here, and hill-climbing on printable-ASCII count is all-or-nothing (no smooth fitness).
4. **Build a real QR reader as an oracle**: implemented the Nayuki zig-zag data path, the 8 mask functions, and — crucially — the **version-7-L 2-block interleave** (data codewords split block0=read even / block1=read odd, then reassembled). Validated end-to-end against a known segno QR (exact round-trip). Read the **mask from the reconstructed frame's format info → mask 0** (ecc bits = L, confirmed).
5. **Backtracking with ASCII pruning**: mapped every data-stream bit → exact module coordinate. DFS over the 14 free pieces, ordered by the first flag-byte each influences; after each placement, decode all now-complete flag bytes and prune unless printable ASCII, with `lactf{` as the known prefix, `count` (readable once block (3,4) is placed) bounding the flag region, and byte `count-1 == '}'`. Solved in **62 nodes**, count = 79.
6. **Independent check**: rendered the reconstructed matrix and decoded with zbar (pyzbar) → same flag.

## Derived answer
`lactf{Th15_15_pr0b481y_n07_wh47_7h3y_m34n7_8y_3rr0r_c0rr3c710n_CVOD5Jp7IOq+XgR}`
(confirmed twice: my hand-written v7-L decoder and independently zbar.)

## Checkpoint self-grade
| Checkpoint | Requirement | Grade |
|---|---|---|
| EC1 | Parse chall.py: v7 45×45 QR, 5×5 grid of 9×9 blocks, shuffle, 10px/module upscale | HIT — extracted exact geometry and generation params |
| EC2 | Downsample to 45×45, cut 25 blocks, reassemble via finder/timing/format structure (or brute+decoder w/ EC) | HIT — 432/432 anchor frame via function-pattern template + Hungarian, then decoder-guided backtracking for data blocks |
| EC3 | Decode reconstructed v7 byte-mode L QR to flag | HIT — decoded (my reader + zbar), exact flag |

Hits: 3 / 3

## Path vs standard writeup
The writeup describes two routes and leans on "brute force permutations + a QR decoder with level-L error correction, whose redundancy tolerates the reordering." In practice that framing understates the work: (a) a naive permutation brute force is infeasible (14! for the data blocks, and RS-L cannot correct a mis-arrangement — its capacity is ~10 codewords/block, not ~120), and (b) the finder/timing/format cues pin only the frame (11 blocks), leaving ~14 data blocks structurally unconstrained. My solve therefore did more than the writeup implies: I built the function-pattern anchor template empirically and solved the frame as an assignment problem, then implemented a full version-7-L decoder — including the non-obvious 2-block RS interleave and reading mask 0 from the recovered format info — to drive an ASCII/`count`-bounded backtracking search that places the remaining data blocks exactly. Same flag; more machinery than "let the error correction sort it out."
