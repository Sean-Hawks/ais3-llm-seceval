# Bench27 task catalog / 題目索引

Generated from MANIFEST.json and opus_runs.json; IDs join the harness and companion analysis.

`needs_docker` in historical metadata means a victim service, not whether an agent sandbox is required.

| Analysis ID | Harness ID | Arm | Category | Difficulty | Source & checkpoint |
|---|---|---|---|---|---|
| C01_crypto_ROT13 | `5` | contaminated | crypto | easy | [intercode](../ctf/bench27/contaminated/crypto_picoctf5/README.md) · [steps](../ctf/bench27/contaminated/crypto_picoctf5/checkpoints.json) |
| C02_crypto_sequential-LCG | `slcg` | contaminated | crypto | medium | [cybench](../ctf/bench27/contaminated/crypto_slcg/README.md) · [steps](../ctf/bench27/contaminated/crypto_slcg/checkpoints.json) |
| C03_crypto_RSA-missing-bits | `missingbits` | contaminated | crypto | medium | [cybench](../ctf/bench27/contaminated/crypto_missingbits/README.md) · [steps](../ctf/bench27/contaminated/crypto_missingbits/checkpoints.json) |
| C04_rev_VaultDoor-char-mapping | `44` | contaminated | rev | easy | [intercode](../ctf/bench27/contaminated/rev_picoctf44/README.md) · [steps](../ctf/bench27/contaminated/rev_picoctf44/checkpoints.json) |
| C05_rev_keygenme-sha256 | `13` | contaminated | rev | medium | [intercode](../ctf/bench27/contaminated/rev_picoctf13/README.md) · [steps](../ctf/bench27/contaminated/rev_picoctf13/checkpoints.json) |
| C06_forensics_strings-in-image | `94` | contaminated | forensics | easy | [intercode](../ctf/bench27/contaminated/forensics_picoctf94/README.md) · [steps](../ctf/bench27/contaminated/forensics_picoctf94/checkpoints.json) |
| C07_forensics_EXIF-metadata | `8` | contaminated | forensics | medium | [intercode](../ctf/bench27/contaminated/forensics_picoctf8/README.md) · [steps](../ctf/bench27/contaminated/forensics_picoctf8/checkpoints.json) |
| C08_misc_hidden-file-unzip | `37` | contaminated | misc | easy | [intercode](../ctf/bench27/contaminated/misc_picoctf37/README.md) · [steps](../ctf/bench27/contaminated/misc_picoctf37/checkpoints.json) |
| C09_misc_zip-password-brute | `34` | contaminated | misc | medium | [intercode](../ctf/bench27/contaminated/misc_picoctf34/README.md) · [steps](../ctf/bench27/contaminated/misc_picoctf34/checkpoints.json) |
| C10_web_git-repo-leak | `back_to_the_past` | contaminated | web | medium | [cybench](../ctf/bench27/contaminated/web_back_to_the_past/README.md) · [steps](../ctf/bench27/contaminated/web_back_to_the_past/checkpoints.json) |
| C11_web_float-balance-overflow | `glacier_exchange` | contaminated | web | medium | [cybench](../ctf/bench27/contaminated/web_glacier_exchange/README.md) · [steps](../ctf/bench27/contaminated/web_glacier_exchange/checkpoints.json) |
| C12_pwn_ROP-chain | `network_tools` | contaminated | pwn | hard | [cybench](../ctf/bench27/contaminated/pwn_network_tools/README.md) · [steps](../ctf/bench27/contaminated/pwn_network_tools/checkpoints.json) |
| D01_crypto_permutation-group-DLP | `permuted` | deep_hard | crypto | hard | [cybench](../ctf/bench27/deep_hard/permuted/README.md) · [steps](../ctf/bench27/deep_hard/permuted/checkpoints.json) |
| D02_pwn_format-string-overwrite | `delulu` | deep_hard | pwn | hard | [cybench](../ctf/bench27/deep_hard/delulu/README.md) · [steps](../ctf/bench27/deep_hard/delulu/checkpoints.json) |
| D03_misc_pickle-jail-escape | `just_another_pickle_jail` | deep_hard | misc | hard | [cybench](../ctf/bench27/deep_hard/just_another_pickle_jail/README.md) · [steps](../ctf/bench27/deep_hard/just_another_pickle_jail/checkpoints.json) |
| R01_crypto_digit-6-7-prime-factoring | `crypto_six-seven` | recent2026 | crypto | medium | [LACTF-2026](../ctf/bench27/recent2026/crypto_six-seven/README.md) · [steps](../ctf/bench27/recent2026/crypto_six-seven/checkpoints.json) |
| R02_crypto_coppersmith-partial-key | `crypto_six-seven-again` | recent2026 | crypto | medium | [LACTF-2026](../ctf/bench27/recent2026/crypto_six-seven-again/README.md) · [steps](../ctf/bench27/recent2026/crypto_six-seven-again/checkpoints.json) |
| R05_forensics_pcap-http-cookie | `forensics_cake` | recent2026 | forensics | easy | [BYUCTF-2026](../ctf/bench27/recent2026/forensics_cake/README.md) · [steps](../ctf/bench27/recent2026/forensics_cake/checkpoints.json) |
| R06_forensics_pcap-icmp-covert | `forensics_stillthere` | recent2026 | forensics | medium | [BYUCTF-2026](../ctf/bench27/recent2026/forensics_stillthere/README.md) · [steps](../ctf/bench27/recent2026/forensics_stillthere/checkpoints.json) |
| R07_misc_utf16-endianness | `misc_endians` | recent2026 | misc | easy | [LACTF-2026](../ctf/bench27/recent2026/misc_endians/README.md) · [steps](../ctf/bench27/recent2026/misc_endians/checkpoints.json) |
| R08_misc_QR-reed-solomon-rebuild | `misc_error-correction` | recent2026 | misc | medium | [LACTF-2026](../ctf/bench27/recent2026/misc_error-correction/README.md) · [steps](../ctf/bench27/recent2026/misc_error-correction/checkpoints.json) |
| R12_pwn_shellcode-PRNG | `pwn_scrabasm` | recent2026 | pwn | medium | [LACTF-2026](../ctf/bench27/recent2026/pwn_scrabasm/README.md) · [steps](../ctf/bench27/recent2026/pwn_scrabasm/checkpoints.json) |
| R11_pwn_OOB-global-write | `pwn_tic-tac-no` | recent2026 | pwn | easy | [LACTF-2026](../ctf/bench27/recent2026/pwn_tic-tac-no/README.md) · [steps](../ctf/bench27/recent2026/pwn_tic-tac-no/checkpoints.json) |
| R04_rev_nonogram-regex-z3 | `rev_flag-finder` | recent2026 | rev | medium | [LACTF-2026](../ctf/bench27/recent2026/rev_flag-finder/README.md) · [steps](../ctf/bench27/recent2026/rev_flag-finder/checkpoints.json) |
| R03_rev_unicode-homoglyph-flag | `rev_ooo` | recent2026 | rev | easy | [LACTF-2026](../ctf/bench27/recent2026/rev_ooo/README.md) · [steps](../ctf/bench27/recent2026/rev_ooo/checkpoints.json) |
| R09_web_go-parser-differential | `web_glotq` | recent2026 | web | medium | [LACTF-2026](../ctf/bench27/recent2026/web_glotq/README.md) · [steps](../ctf/bench27/recent2026/web_glotq/checkpoints.json) |
| R10_web_AES-GCM-short-tag | `web_single-trust` | recent2026 | web | medium | [LACTF-2026](../ctf/bench27/recent2026/web_single-trust/README.md) · [steps](../ctf/bench27/recent2026/web_single-trust/checkpoints.json) |
