# small-trouble

- **Category:** Cryptography
- **Difficulty:** Medium
- **Points:** 200
- **Author:** Imattas aka Zemi
- **Source:** https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/small-trouble/index.mdx

## FLAG
FLAG: NOT FOUND IN WRITEUP (generic methodology template; no concrete flag value)

## Attack / Technique
RSA Small Exponent Attack (Cube Root Attack).

Exploits scenarios where e=3 and plaintext m is small enough that m^3 barely exceeds n. Attack formula: m = iroot(c + k*n, 3) for incrementing k.
Writeup quote: "If e = 3 and m is small, then m^3 = c + k*n for some small integer k."

## Step-by-Step Solution
1. Extract RSA parameters (n, e, c) from challenge files.
2. Verify e is small (<= 17).
3. Iterate over k = 0, 1, 2, ... computing iroot(c + k*n, e).
4. When a perfect e-th root is found, convert result to bytes.
5. Decode to recover plaintext flag.

## Exploit Script / Values
Writeup provides a Python script combining three attack vectors: small-exponent cube-root iteration, trial division for small prime factors, and Wiener's attack (continued fractions) for small d. No concrete script text or specific n/e/c values reproduced.

## Challenge Files
RSA parameters and ciphertext provided; solver decrypts locally. No explicit file names or download URL given.

## needs_docker
NO — static file challenge, no network service.
