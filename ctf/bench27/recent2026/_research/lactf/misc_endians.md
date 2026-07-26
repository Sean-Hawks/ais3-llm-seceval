# misc / endians

- **Repo path:** `2026/misc/endians`
- **Category:** misc
- **Difficulty (estimate):** Easy
- **Points:** not listed
- **FLAG:** `lactf{1_sur3_h0pe_th1s_d0es_n0t_g3t_l0st_1n_translati0n!}`
  - Source: verbatim from `2026/misc/endians/challenge.yaml` (`flag:` field). Cross-checked: applying the `solve.py` transform to `chall.txt` reproduces this.
- **needs_docker:** no. Pure local encoding puzzle.

## Technique / attack name
UTF-16 endianness confusion. The flag was encoded/decoded with mismatched UTF-16 byte order, turning ASCII into CJK-looking glyphs; reverse by swapping BE/LE.

## How the challenge works (`gen.py`)
```python
text = "lactf{REDACTED}"
endian = text.encode(encoding="???").decode(encoding="???")  # mismatched UTF-16 BE/LE
open("chall.txt","wb").write(endian.encode())
```
Effect: the ASCII flag's bytes get reinterpreted under the opposite endianness, so pairs of bytes (`00 6c`, etc.) become single wide characters. `chall.txt` shows CJK/fullwidth glyphs like `氀愀挀琀昀笀…`.

## Step-by-step solution (from committed `solve.py`)
1. Read `chall.txt` bytes and decode (UTF-8 works because the interspersed null bytes are dropped).
2. Re-encode as `UTF-16BE`, then decode as `UTF-16LE` (swap endianness back):
```python
chall = open("chall.txt","rb").read()
print(chall.decode().encode(encoding="UTF-16BE").decode(encoding="UTF-16LE"))
```
3. Output is the ASCII flag.

## Source files handed out
- `2026/misc/endians/chall.txt` (the mojibake ciphertext)
- `2026/misc/endians/gen.py` (generation script; per challenge.yaml `provide: ./chall.txt, ./gen.py`)
- (`solve.py`, `realgen.py` also in repo)
