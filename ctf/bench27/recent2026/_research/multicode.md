# multicode

- **Category:** General Skills / Misc
- **Difficulty:** Medium
- **Points:** 200
- **Author:** Imattas aka Zemi
- **Source:** https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/multicode/index.mdx

## FLAG
FLAG: NOT FOUND IN WRITEUP (generic methodology template; no concrete flag value)

## Overview
Identify and remove successive layers of encoding applied to a hidden flag. Description: "No encryption, just multiple layers of obfuscation/encoding."

## Attack / Technique
Multi-Layer Encoding Peeling — iteratively identify and reverse reversible encodings (Base64, hex, ROT13, binary, octal, Morse, URL encoding, decimal ASCII, Atbash, Base32).

## Step-by-Step Solution
1. Obtain the encoded message.
2. Identify outermost layer by character patterns:
   - Base64: A-Za-z0-9+/ with = padding
   - Hex: 0-9a-fA-F pairs
   - Binary: groups of 8 bits
   - Octal: space-separated 3-digit octal
   - Morse: dots/dashes/spaces-slashes
   - URL: %XX sequences
   - Decimal ASCII: space-separated numbers 0-127
3. Apply the appropriate decoder.
4. Repeat steps 2-3 until picoCTF{...} revealed.

## Exploit Script / Values
Python3 `solve.py` provided with decoders: try_base64/hex/binary/octal/decimal/rot13/morse/atbash/base32/url_decode; main loop peel_layers() attempts decoders in specificity order, max 20 iterations, validates printability. Usage:
```bash
python3 solve.py            # interactive
python3 solve.py encoded.txt
echo "<data>" | python3 solve.py
```
No concrete flag reproduced.

## Challenge Files
Not specified; only the encoded message string is needed (provided by platform).

## needs_docker
NO — static challenge; decode the provided string, no network service.
