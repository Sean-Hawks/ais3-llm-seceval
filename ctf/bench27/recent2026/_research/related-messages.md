# related-messages

- **Category:** Cryptography
- **Difficulty:** Medium
- **Points:** 200
- **Author:** Imattas aka Zemi
- **Source:** https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/related-messages/index.mdx

## FLAG
FLAG: NOT FOUND IN WRITEUP (writeup is a generic methodology template; no concrete flag value is given)

## Attack / Technique
Franklin-Reiter Related Message Attack on RSA.

Two mathematically related plaintexts encrypted under the same RSA public key allow recovery without factoring n. Sender encrypts m1, then corrects a typo and sends m2 where m2 = a*m1 + b (typically a=1).

## Mathematical Foundation
Construct two polynomials in Z_n[x]:
- g1(x) = x^e - c1  (root: m1)
- g2(x) = (a*x + b)^e - c2  (also has root m1)

Their GCD yields linear polynomial x - m1, exposing the plaintext.

## Step-by-Step Solution
1. Parse challenge data from `output.txt`: extract n, e, c1, c2, and relationship params a, b.
2. Construct polynomials using the formulas above.
3. Compute polynomial GCD in Z_n[x] via sympy.
4. Extract m1 from the linear GCD result as the negation of its constant term.
5. Convert integer to bytes using long_to_bytes(m1) to recover plaintext.
6. Search for picoCTF{...} pattern in decoded message or in m2 = a*m1 + b.

## Exploit Script / Values
Python script uses sympy (polynomial ops) and pycryptodome (number utilities). Attack complexity negligible for e <= 65537. No concrete script text or intermediate values (n, e, c1, c2) are reproduced in the writeup.

## Challenge Files
Writeup indicates typical provision of `output.txt` containing RSA parameters and ciphertexts. No explicit download URL given.

## needs_docker
NO — static file challenge (purely cryptographic analysis of provided data; no network service).
