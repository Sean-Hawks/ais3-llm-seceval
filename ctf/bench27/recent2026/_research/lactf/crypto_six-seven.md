# crypto / six seven

- **Repo path:** `2026/crypto/six-seven`
- **Category:** crypto
- **Difficulty (estimate):** Easy–Medium
- **Points:** not listed in challenge.yaml
- **FLAG:** `lactf{wh4t_67s_15_blud_f4ct0r1ng_15_blud_31nst31n}`
  - Source: verbatim from `2026/crypto/six-seven/flag.txt`.
- **needs_docker:** yes — service prints a fresh `n,c` each connection. Service file: `2026/crypto/six-seven/Dockerfile`. Static plaintext flag (same each instance).

## Technique / attack name
RSA factorization of "structured" primes (digit-constrained brute force / branch-and-prune on the last digits mod 10^k). Not Fermat; the primes are close-ish but the intended path is reconstructing digits.

## How the challenge works (`chall.py`)
- `generate_67_prime(256)`: builds a 256-digit prime whose decimal digits are all chosen from `{6,7}`, with the last digit forced to `7`. Two such primes `p`, `q` are produced.
- `n = p*q`, `e = 65537`. Flag is `bytes_to_long(flag)`, `c = pow(m,e,n)`. Server prints `n=...` and `c=...`.

## Step-by-step solution (from committed `solve.py`)
1. Read `n`, `c` from the service.
2. Reconstruct `p` digit-by-digit from the least-significant end. Maintain a stack of candidate suffixes (start with `7`). For a candidate suffix `test_p` of length `L`, form `test6 = int("6"+test_p)` and `test7 = int("7"+test_p)` (prepending a `6` or `7`).
3. For each, compute `result = n * inverse(testX, 10^(L+1)) mod 10^(L+1)`. This is the required matching digits of `q`. If every digit of `result` is `6` or `7` and it has the right length, the prefix is consistent — push it.
4. When a candidate reaches length 256, that is `p`. Then `q = n // p`.
5. Standard RSA decrypt: `t=(p-1)*(q-1)`, `d=inverse(65537,t)`, `m=pow(c,d,n)`, `long_to_bytes(m)`.

## Key intermediate values (committed in solve.py comments, for the committed n)
- `p=7677676767777667767767776766766676676676766767776676666676766667776766767667677666767777677776676676777767667767666766666676666666766777667666776667767766767766766667776677767667667766676667767667766767766667677677767766667666767666777767767676666776767767`
- `q=7676667766767776767777677766766676766666666677776767776767767667766767666776667667667766677777767677777767777677777677667766767777767666667676677776777766766767666776777667667666777766667766767667677666776776767677776766776777767667667666767777766776676677`

## Source files handed out
- `2026/crypto/six-seven/chall.py` (server source)
- Service exposed over `nc` (challenge.yaml `expose.main tcp 31180`)
- (`Dockerfile`, `flag.txt`, `solve.py` also in repo but flag.txt is the answer, not handed to solver)
