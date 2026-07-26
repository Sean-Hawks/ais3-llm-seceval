# rev / ooo

- **Repo path:** `2026/rev/ooo`
- **Category:** rev
- **Difficulty (estimate):** Easy
- **Points:** not listed
- **FLAG:** `lactf{gоοօỏơóὀόὸὁὃὄὂȯöd_j0b}`
  - Source: verbatim from `2026/rev/ooo/challenge.yaml` (`flag:` field). NOTE: the flag contains many non-ASCII homoglyph "o" characters (Cyrillic о, Greek ο/omicron, Armenian օ, various accented o, etc.) — this is intentional; copy exactly.
- **needs_docker:** no. Pure local Python checker.

## Technique / attack name
Unicode homoglyph obfuscation + reversing a chained arithmetic constraint. The function names are all visually-identical "o" glyphs; each maps to a simple binary op.

## How the challenge works (`ooo.py`)
Functions (by homoglyph): `о`=add, `ο`=sub(a-b), `օ`=mul, `ỏ`=floordiv, `ơ`=xor, `ó`=or, `ὀ`=and, `ὸ`=b-a, `ὄ`=return a, `ὂ`=return b, `ȯ`=mod.
Target array `ὁ` = `[205, 196, 215, 218, 225, 226, 1189, 2045, 2372, 9300, 8304, 660, 8243, 16057, 16113, 16057, 16004, 16007, 16006, 8561, 805, 346, 195, 201, 154, 146, 223]`.
For each `i` in `range(len-1)` with `a=ord(guess[i])`, `b=ord(guess[i+1])`:
`о(ὄ(a,b), ὂ(a,b))` = `a + b` must equal `ὁ[ơ(i, ȯ(օ(a,b), a))]` = `ὁ[ i XOR ((a*b) % a) ]` = `ὁ[ i XOR 0 ]` = `ὁ[i]` (since `(a*b) % a == 0`).
So the whole check reduces to: **`ord(guess[i]) + ord(guess[i+1]) == arr[i]` for all i**, i.e. consecutive character codes sum to the array entry.

## Step-by-step solution (from committed `solve.py`)
1. The flag starts with `l` (`ord('l')=108`). Set `prev = ord('l')`, output `'l'`.
2. For each `arr[i]`, next char code = `arr[i] - prev`; print `chr(next)`; set `prev = next`.
3. This telescopes out the full flag string (recovering the homoglyph "o" characters as their codepoints).

```python
arr = [205,196,215,218,225,226,1189,2045,2372,9300,8304,660,8243,16057,16113,16057,16004,16007,16006,8561,805,346,195,201,154,146,223]
prev = ord('l'); out='l'
for v in arr:
    prev = v - prev; out += chr(prev)
# out == the flag
```

## Source files handed out
- `2026/rev/ooo/ooo.py` (the checker, provided per challenge.yaml `provide: ./ooo.py`)
- (`solve.py` also in repo)
