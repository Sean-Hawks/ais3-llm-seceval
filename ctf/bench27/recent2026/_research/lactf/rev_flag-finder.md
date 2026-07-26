# rev / flag-finder

- **Repo path:** `2026/rev/flag-finder`
- **Category:** rev
- **Difficulty (estimate):** Medium (single-technique but tedious constraint solve)
- **Points:** not listed
- **FLAG:** `lactf{Wh47_d0_y0u_637_wh3n_y0u_cr055_4_r363x_4nd_4_n0n06r4m?_4_r363x06r4m!}`
  - Source: verbatim from `2026/rev/flag-finder/challenge.yaml` (`flag:` field).
- **needs_docker:** technically the app is served via `Dockerfile` (challenge.yaml exposes http), but the entire logic is **client-side JavaScript** in `src/script.js`, so it is solvable fully offline from the handed-out source. Service file: `2026/rev/flag-finder/Dockerfile`.

## Technique / attack name
Regex-encoded **nonogram / picross** puzzle. A giant JS regex (`theFlag`) validates a 1919-character `#`/`.` string that represents a 19-row × 101-column bitmap grid. Solving the nonogram row/column constraints draws the flag text as pixels.

## How the challenge works (`src/script.js`)
- The page builds `len = 1919` checkboxes; each checked box → `#`, unchecked → `.`. Clicking "find" runs `theFlag.test(input)`.
- `theFlag` is a lookahead-stacked regex:
  - Grid is 19 rows × 101 chars per row (19*101 = 1919). Actually rows are 101 wide.
  - **Column constraints:** a first big lookahead block uses patterns like `(?:.{K}\..{100-K}...)` selecting one column `K` across all 19 rows and encoding that column's run-lengths (numbers of consecutive `#`).
  - **Row constraints:** trailing `(?<=.{101*r})(?<!.{101*r+1})(\.*#{a}\.+#{b}...\.*)` groups encode each row's run-lengths.
- Satisfying all row + column run-length constraints = solving a nonogram whose solution image spells the flag.

## Step-by-step solution
1. Extract the regex from `src/script.js` (single `const theFlag = /.../;`).
2. Parse it into nonogram row-clues and column-clues (grid 19×101).
3. Solve the nonogram (any nonogram solver, or feed clues to an ILP/constraint solver).
4. Render the resulting `#` bitmap → it visually spells the flag text `lactf{...regex0gram!}`.
5. Read off the flag.

(No committed `solve.py`; ground-truth flag is committed in challenge.yaml and is the intended output of the solved bitmap.)

## Source files handed out
- `2026/rev/flag-finder/src/index.html`
- `2026/rev/flag-finder/src/script.js` (contains the full regex — the whole challenge)
- (`Dockerfile` in repo to host the static page)
