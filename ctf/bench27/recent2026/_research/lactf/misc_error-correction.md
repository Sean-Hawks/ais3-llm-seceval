# misc / error-correction

- **Repo path:** `2026/misc/error-correction`
- **Category:** misc
- **Difficulty (estimate):** Medium (image reconstruction; deterministic from source)
- **Points:** not listed
- **FLAG:** `lactf{Th15_15_pr0b481y_n07_wh47_7h3y_m34n7_8y_3rr0r_c0rr3c710n_CVOD5Jp7IOq+XgR}`
  - Source: verbatim from `2026/misc/error-correction/challenge.yaml` (`flag:` field). The trailing `CVOD5Jp7IOq+XgR` is part of the flag (padding to survive scrambling).
- **needs_docker:** no. Local image puzzle; `chall.py` fully specifies the (reversible) scramble.

## Technique / attack name
QR-code block scrambling + QR error correction. The QR of the flag is diced into a 5×5 grid of blocks which are then shuffled; recover by either (a) reversing the deterministic block permutation, or (b) leaning on QR error-correction to read the code despite the scramble.

## How the challenge works (`chall.py`)
- `qr = segno.make(flag, mode='byte', error='L', boost_error=False, version=7)`; rendered to a `0/1` module grid (version 7 = 45×45 modules).
- The 45×45 grid is split into a 5×5 arrangement of 9×9-module blocks: `chunks[...]` indexed as `code[405*y + 45*ysub + 9*x : ...+9*(x+1)]` for `x,y in range(5)`, `ysub in range(9)`.
- `random.shuffle(chunks)` permutes the 25 blocks; then reassembled and saved as `chall.png` (resized to 450×450, NEAREST).

## Step-by-step solution
1. Load `chall.png`, downsample back to the 45×45 module grid (each module = 10 px block). Recover the 25 blocks of 9×9 modules.
2. The 25 blocks are a permutation of the original QR's 5×5 block layout. Reassemble the correct QR: use the QR finder patterns (three corner squares), timing patterns, and format info to determine each block's correct position; OR try permutations / use a QR decoder with error correction to find the arrangement that decodes.
3. Decode the reconstructed QR (version 7, byte mode, EC level L) → yields the flag string.
   (`error='L'` + the padded suffix in the flag give enough redundancy for QR error correction to succeed once blocks are placed.)

## Source files handed out
- `2026/misc/error-correction/chall.png` (scrambled QR image)
- `2026/misc/error-correction/chall.py` (scramble generator — reveals exact block geometry; per challenge.yaml `provide: ./chall.png, ./chall.py`)
- (`flag.png` also in repo = the un-scrambled QR)
