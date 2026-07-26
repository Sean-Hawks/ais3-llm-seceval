# crypto / six seven again

- **Repo path:** `2026/crypto/six-seven-again`
- **Category:** crypto
- **Difficulty (estimate):** Medium (requires Coppersmith / SageMath `small_roots`)
- **Points:** not listed in challenge.yaml
- **FLAG:** `lactf{n_h4s_1337_b1ts_b3c4us3_667+670=1337}`
  - Source: verbatim from `2026/crypto/six-seven-again/flag.txt`.
- **needs_docker:** yes — service prints fresh `n,c` per connection. Service file: `2026/crypto/six-seven-again/Dockerfile`. Static plaintext flag.

## Technique / attack name
Coppersmith's method (partial known-bits factoring). One RSA prime is almost fully known (fixed high and low digit blocks, only a small middle unknown), recover the unknown middle with `small_roots`.

## How the challenge works (`chall.py`)
- `generate_super_67_prime()`: builds a 201-digit prime `p` whose decimal digits are: 67 leading `6`s, then 67 digits each freely chosen from `{6,7}`, then 67 trailing `7`s.
- `q = getPrime(670)` (a normal ~670-bit prime). `n = p*q`, `e = 65537`. Prints `n`, `c`.
- So `p = A + x*10^67` where `A = int("6"*67 + "0"*67 + "7"*67)` and `x` is a 67-digit unknown in `[0, 10^67)`. The unknown middle is small relative to `p`, making `p` a partially-known factor of `n`.

## Step-by-step solution (from committed `solve.sage`, SageMath)
1. Read `n`, `c`.
2. Set `A = Integer("6"*67 + "0"*67 + "7"*67)`.
3. In `Zmod(n)[x]`, define `f = A + x*10^67`; make monic: `f_monic = f / f.leading_coefficient()`.
4. `roots = f_monic.small_roots(X=10^68, beta=0.3)` — recovers the unknown middle block `x`.
5. `p = int(roots[0]*10^67 + A)`, `q = n / p`.
6. RSA decrypt: `d = inverse(65537, (p-1)*(q-1))`, `m = pow(c,d,n)`, `long_to_bytes(m)`.

## Key script (verbatim core)
```python
R.<x> = PolynomialRing(Zmod(n))
A = Integer("6" * 67 + "0"*67 + "7"*67)
f = A + x*10^67
f_monic = f / f.leading_coefficient()
roots = f_monic.small_roots(X=10^68, beta=0.3)
p = int(roots[0]*10^67 + A)
q = n / p
```

## Source files handed out
- `2026/crypto/six-seven-again/chall.py` (server source)
- Service over `nc` (challenge.yaml `expose.main tcp 31181`)
- (`Dockerfile`, `flag.txt`, `solve.sage` in repo)
