# web / single-trust

- **Repo path:** `2026/web/single-trust`
- **Category:** web (crypto-flavored)
- **Difficulty (estimate):** Medium
- **Points:** not listed
- **FLAG:** `lactf{4pl3tc4tion_s3curi7y}`
  - Source: verbatim from `2026/web/single-trust/flag.txt`.
- **needs_docker:** yes. Service file: `2026/web/single-trust/Dockerfile`. Node app (`index.js`).

## Technique / attack name
AES-CTR / stream-cipher **malleability (bit-flipping)** on a homemade encrypted session cookie, with a short (1-byte) auth tag that is brute-forceable (256 tries). Rewrite the session's `tmpfile` path to `/flag.txt`.

## How the challenge works (`index.js`, per challenge description)
- Homemade JWT-ish auth: cookie `auth = base64(iv) . base64(auth_tag) . base64(ct)`.
- The library is the LA CTF 2023 "zero-trust" library with aplet's backdoor patched out; the remaining flaw is that decryption uses `cipher.update(ct)` output (a keystream XOR of plaintext) with no real integrity — the "auth tag" is effectively 1 byte, and the ciphertext is malleable because encryption is a stream cipher: flipping ciphertext byte i flips plaintext byte i.
- Server-side, the decrypted JSON has a `tmpfile` field pointing at the user's paste store; the app reads/returns that file. Change it to `/flag.txt` (flag location stated in the challenge: "the flag is in `/flag.txt`").

## Step-by-step solution (from committed `solve.py`)
1. `GET /` to obtain a fresh `auth` cookie; split into `[iv, auth_tag, ct] = base64decode(unquote(cookie).split("."))`.
2. Known current plaintext: `cur = {"tmpfile":"/tmp/pastestore/<32 a's>"}`. Desired plaintext: `des = {"tmpfile":"/flag.txt","x":"<32 a's>"}`. Pad so `len(cur) == len(des) == len(ct)`.
3. Stream-cipher bit-flip: `new_ct[i] = ct[i] XOR cur[i] XOR des[i]` for all i.
4. Brute-force the 1-byte auth tag: for `auth_tag in range(256)`, rebuild cookie `base64(iv).base64(bytes([auth_tag])).base64(new_ct)`, `GET /`, and check for `lactf` in the response.
5. The matching tag returns the flag from `/flag.txt`.

```python
cur = f'{{"tmpfile":"/tmp/pastestore/{"a"*32}"}}'.encode()
des = f'{{"tmpfile":"/flag.txt","x":"{"a"*32}"}}'.encode()
new_ct = bytes(a ^ b ^ c for a,b,c in zip(cur, des, ct))
# then loop auth_tag 0..255
```

## Source files handed out
- `2026/web/single-trust/single-trust.zip` (per challenge.yaml `provide`)
- In-repo: `2026/web/single-trust/{index.js,index.html,package.json,package-lock.json,Dockerfile}`, `static/`
- (`solve.py`, `flag.txt` in repo)
