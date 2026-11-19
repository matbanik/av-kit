---
project: "2026-11-18-eval-describe-raw-bytes"
date: "2026-11-18"
source: "grouping .agent/context/grouping/2026-11-18-eval-describe-session-grouping.md §3 Session 95; issue EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE (D-1196)"
meus: []
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-18-eval-describe-session-grouping.md"
---

# Implementation Plan: capture the eval describe output as raw bytes and refuse cp437 mojibake

> **Project**: `2026-11-18-eval-describe-raw-bytes`
> **Build Plan Section(s)**: none. This is eval tooling and run-book debt with no MEU (grouping D-1199, triage D-1196), as in Sessions 78, 90, 91 and 92.
> **Status**: said to execute (USER_EXPLICIT 2026-11-18 "proceed with the next session prompt orchestration here like you did the others"). `plan_to_exec_gate: human`: that message is the execution approval once the plan review approves and no STOP item is open; the plan review was approved at round 1 with no findings (.agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-plan-critical-review.md), and no STOP item is open. Session 95 is the only session of the 2026-11-18 grouping.

---

## Goal

**Goal anchor:** Session 64's eval run book captures `eval-harness.ts describe` with a new script, `eval-describe.py`, that runs the harness in a subprocess and writes the MCP server's stdout bytes unchanged (a fake child proves the bytes pass through, AC-6; on the real harness the capture equals an independent `npx` read on another root and keeps its tail after CUT, AC-9); it refuses output that is not UTF-8, holds a BOM, a CR byte or cp437 mojibake, or lacks exactly one CUT line, with a non-zero exit and a named reason, using the one pattern and CUT line Session 92 wrote (`eval-rerun.py` `MOJIBAKE` and `CUT`, D-1186), not a second one, and exits 2 with a named message when that file cannot load; `eval-run.md` step 3 names the new command and a dated note says what changed and why; Session 64's task rows, plan and receipts and Session 92's files stay byte for byte; and `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` is resolved through the triage tool with receipts. No product code, no model call and no eval run. Tests and scripts prove each part; there is no manual check.

**Why.** `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` (`known-issues.yaml:5764`, D-1196, TECH-DEBT P4). `eval-run.md:24` (step 3) and Session 64's task row E-1 capture `describe` through a PowerShell redirect of native output. PowerShell decodes the server's UTF-8 through the console code page (cp437) and writes the text back as UTF-8, so an arrow (U+2192, bytes `E2 86 92`) becomes `U+0393 U+00E5 U+00C6` and an en dash (U+2013, `E2 80 93`) becomes `U+0393 U+00C7 U+00F4`. Session 64's receipt `C:/Temp/av-kit/s64-E1-describe.txt` is 30,806 bytes, 725 CRLF, with 9 mojibake arrows, 2 mojibake en dashes, no real arrow or en dash, one CUT line and one `[rtk]` line (`edr-plan-bytes.txt`). The register's blast radius: any eval that follows step 3 as written measures a surface no client serves. Session 92 met the trap, re-captured raw bytes with a subprocess and added a fail-closed guard to its own `eval-rerun.py` (`mar-eval-describe-attempt1.txt`, `mar-eval-d1186-roundtrip.txt`), but the run book still holds the trap.

**Grouping §3 Session 95** (grouping `:71-92`): the files are `eval-run.md` step 3, a raw-byte capture (a script or a step in `eval-check.py`, the plan picks with an HDP brief), and the tests that prove its guard; row E-1 is an executed record and stays as written, and a dated note in `eval-run.md` points at the new step; the model is Session 92's guard, reused, not rewritten; acceptance: the capture on the real harness writes the server's stdout unchanged with no mojibake, a cp437 fixture and a mixed one are refused, step 3 names the new command, the issue is resolved through the triage tool; gate: no model call and no eval run, no network, no product code, the home-path gate before and after, each edited file keeps its line endings.

**What the code shows (plan-time reads at `HEAD` `3e61b5b`):**

- **The harness.** `eval-harness.ts describe(root)` (`:136-166`) starts the isolated backend over `root` (`withBackend`, `spawnBackend` from `mcp-server/scripts/audit/backend.ts`), connects to `mcp-server/dist/index.js`, and prints with `console.log`: the server instructions, each tool's description and input schema, the CUT line `<!-- CUT: the real surface ends above this line -->`, then each tool's action notes. The root must sit under `C:/Temp/av-kit/s64/eval/` (`:57-64`); the output names no root, so two roots give the same bytes. It needs the built `dist/index.js`, which `.gitignore:17` (`mcp-server/dist/`) keeps out of git; step 2 builds it.
- **The guard.** `eval-rerun.py` (Session 92, LF, 12,056 B) holds `CUT`, `_CP437_CONT` and `MOJIBAKE = re.compile("[Γ┬├][" + re.escape(_CP437_CONT) + "]")` (`:35-43`): a cp437 lead character for byte E2, C2 or C3 followed by a cp437 continuation character. `real_surface()` refuses an escape, mojibake, a bare CR, a CUT count other than 1, action notes above CUT, a missing lead fact and a non-verbatim description; `build()` makes the three real-surface prompts from `eval-run.md`'s four text blocks. The module has no side effect at import apart from Python's own bytecode cache, and `main()` runs only under `__main__`. It reads a receipt; it does not run `describe`. Loading it by path with bytecode writing on puts `__pycache__/eval-rerun.cpython-312.pyc` in Session 92's folder (gitignored by `.gitignore:3`, but a record folder), so every loader in this session sets `sys.dont_write_bytecode = True` first; one such file is already there from a plan-time load (2026-11-18 20:27, ignored, left for the coordinator). Session 92 already depends on Session 64's folder: `eval-rerun.py:24-27` reads `eval-run.md` and `eval-check.py` there, and `:3-4` says it reuses that checker unchanged.
- **The guard's reach.** `MOJIBAKE` matches the cp437 reading of the lead bytes only (U+0393 is byte E2 in cp437; cp850 reads it as U+00D4, cp1252 as U+00E2), so a console on another code page would pass it; the `cr` refusal still catches the CRLF such a redirect writes. This session does not widen the pattern, since that would be a second guard. `refusals()` below is a separate check of a raw capture that shares only `MOJIBAKE` and `CUT` with `real_surface()`: it refuses any CR byte where `real_surface()` normalises CRLF and drops `[rtk]` lines, and it does not check for an escape (`eval-rerun.py:72`, `:79-83`).
- **The run book.** `eval-run.md` (LF, 101 lines, 5,748 B) has the intro at lines 3 to 6, step 3 at line 24 with two sub-bullets (`:25-26`) that read "the receipt's text", step 4.2 building each prompt from §Prompts with `{{DESCRIBE}}`, and four `text` blocks.
- **The record.** Session 64's `task.md` row E-1 ran `rtk proxy npx tsx ... describe *> s64-E1-describe.txt` (the receipt's `[rtk]` line); step 3 says `> ... 2>&1`, and Session 92's row 5 ran exactly that form inside `pwsh -NoProfile -File run-row5-prep.ps1` (`2026-11-17-mcp-audit-refresh/task.md:53`), giving `mar-eval-describe-attempt1.txt`: 37,406 B, 834 CR, cp437 arrows. Both forms merge stderr, and on this host's pwsh 7.6 a redirect that merges stderr decodes native output through the console code page (437), while a plain `>` keeps the bytes (`xp/merge.txt`, `xp/star.txt`, `xp/plain.txt`).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-18). The change is one new script beside eval-run.md, its tests and one run-book step, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in VS Code (`.agent/docs/harness-profiles.md`); commands run in `pwsh` from `P:/av-kit` through `rtk proxy` with the receipt pattern (`.agent/docs/commands.md`), receipts under `C:/Temp/av-kit/eval-describe-raw-bytes/` (`D`).
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` with `AGENT_MODEL_REGISTRY_HOME=P:/.agent` and `RECEIPTS_DIR` set (Session 82 RULE-3). Plan loop `edr-plan-2026-11-18-eval-describe-raw-bytes`, execution loop `edr-execution-2026-11-18-eval-describe-raw-bytes`; caps from `.agent/review-limits.json` (6 rounds, turn tokens off).
- **Never** commit, stage or push without Mat's words; the coordinator commits after the execution review, without a push (grouping §4).

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| The issue (no MEU) | `.agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-implementation-critical-review.md`

One handoff, following the no-MEU precedent `2026-11-17-mcp-audit-refresh-handoff.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and plan-local checkers (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`, `baseline-records.json`, `red-check.py`, `identity.py`, `eol-check.py`, `issue-resolve.py`, `host-load.ps1` |
| WP-2 | Build, the old-redirect reproduction and the Red tests (row 1) | WP-1 | shared | `test_eval_describe.py`, `edr-old-*` receipts (`edr-old.ps1` is written at plan time) |
| WP-3 | The capture script, Green (row 2) | WP-2 | shared | `eval-describe.py` |
| WP-4 | The live capture and the run book (rows 3 and 4) | WP-3 | shared | `edr-describe.txt`, `edr-direct.txt`, `eval-run.md` |
| WP-5 | Register, grouping row, hub audit (rows 5 and 6) | WP-4 | shared | Issue resolved, grouping row 95 |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!NOTE]
> **One brief is settled on its recommendation under your hand-over** ('proceed with the next session prompt orchestration here like you did the others', 2026-11-18, continuing 'make the decisions always the recommenations'): D-1201, where the one copy of the guard lives. The recommendation is a small script beside `eval-run.md` that imports Session 92's guard, so no record file and no Session 92 file changes; only step 3 of the run book and a dated note do. Its cost is a tie from Session 64's run book to Session 92's folder. Read it if you want to overrule it before execution.
>
> **Nothing here costs money or touches your data.** No model call, no eval run and no network. The MCP server is built (step 2's build, as the run book needs it) and started only by the harness, over scratch roots under `C:/Temp/av-kit/s64/eval/s95-*`; no row opens your app data, settings or models folder. No STOP item is held for you.

## Proposed Changes

### Single-statement contracts

| Id | Statement |
|---|---|
| `RAW_CAPTURE` | `eval-describe.py capture ROOT OUT` writes exactly the harness child's stdout bytes to `OUT`, or writes no `OUT` at all. |
| `ONE_GUARD` | The mojibake pattern and the CUT line that `eval-describe.py` uses are the objects `eval-rerun.py` defines, read from the loaded module at each call; no other file in scope compiles a mojibake pattern; when the module cannot load, every command exits 2 with `error: guard not loaded:` and runs nothing. |
| `NAMED_REFUSAL` | Every refusal exits 1 and prints `refused:` with at least one reason from the closed list `empty`, `bom`, `not-utf8`, `cr`, `mojibake`, `cut`, `harness-exit`, `timeout`. |
| `NO_OVERWRITE` | `capture` exits 2 before starting a child when `OUT`, `OUT.stderr.txt` or `OUT.refused` exists, and creates each file it writes with exclusive create. |
| `STEP3_NAMES_SCRIPT` | `eval-run.md` equals its row-0 bytes with the dated note after line 6 and line 24 replaced by the new step 3, and nothing else changed. |
| `RECORDS_KEPT` | Session 64's task, plan, harness, seed and checker, its describe receipt, Session 92's `eval-rerun.py` and expected text, and `backend.ts` keep their row-0 SHA-256. |

### The capture script: `docs/execution/plans/2026-11-11-capture-export-copy/eval-describe.py` (new, LF, standard library)

Placed beside `eval-run.md` (D-1201 A). Usage:

```text
eval-describe.py capture ROOT OUT   run eval-harness.ts describe over ROOT; write stdout to OUT
eval-describe.py check FILE         apply the capture's refusals to a saved receipt
```

**Constants and seams.** `REPO = Path(__file__).resolve().parents[4]`; `MCP_DIR = REPO / "mcp-server"`; `HARNESS = "../docs/execution/plans/2026-11-11-capture-export-copy/eval-harness.ts"` (relative to `MCP_DIR`, as step 3 ran it); `DIST = MCP_DIR / "dist/index.js"`; `TSX = MCP_DIR / "node_modules/tsx/dist/cli.mjs"`; `BASE = "C:/Temp/av-kit/s64/eval/"`; `DESCRIBE_TIMEOUT_S = 300`; `GUARD_PATH = REPO / "docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py"`.

**The guard load.** `load_guard(path=GUARD_PATH)` sets `sys.dont_write_bytecode = True`, then loads the file with `importlib.util.spec_from_file_location("s92_eval_rerun", path)` and `exec_module`, and raises `ImportError` when the spec is empty or the module lacks `MOJIBAKE` or `CUT`. At module level, `GUARD = load_guard()` sits in `try`/`except (ImportError, OSError, SyntaxError)`; on failure `GUARD` is `None` and `GUARD_ERROR` names the path and the exception (a missing file raises `FileNotFoundError` from `exec_module`, `xp/probe_guard.txt`). `main()` checks `GUARD` first: `None` prints `error: guard not loaded: <path>: <exception>` (ASCII, through `ascii()`), runs no child and exits 2, never a traceback. The code reads the pattern and the line as `GUARD.MOJIBAKE` and `GUARD.CUT` at each call, with no module-level copy, so a test that swaps `GUARD` changes what the script refuses (`ONE_GUARD`). The file holds no `re.compile` and no `cp437` text. `edr-check.py` loads the guard the same way. `command(root)` is the test seam: it checks that `node` is on `PATH` and that `TSX`, `DIST` and `MCP_DIR / HARNESS` exist, raising the usage error "build first (eval-run.md step 2)" when `DIST` is missing, and returns `([node, str(TSX), HARNESS, root, "describe"], MCP_DIR)`. Node runs tsx's CLI directly: no shell and no `npx` shim between the child and the pipe.

**`refusals(data: bytes) -> list[tuple[str, str]]`**, in this order: `empty` (no bytes; return); `bom` (starts with `EF BB BF`, `FF FE` or `FE FF`); `not-utf8` (strict decode fails, with the byte offset; return); `cr` (any `0D` byte, with the count); `mojibake` (`GUARD.MOJIBAKE` matches, with the count and the first offset, the match printed with `ascii()`); `cut` (the count of lines equal to `GUARD.CUT`, after CRLF is normalised, is not 1). These are this script's own checks of a raw capture: they share the pattern and the CUT line with `real_surface()` and nothing else (§What the code shows, the guard's reach).

**`capture ROOT OUT`:**

1. `ROOT` (with `\` read as `/`) must start with `BASE`, case-insensitive, and be longer than it; else usage, exit 2. The harness checks this again.
2. If `OUT`, `OUT.stderr.txt` or `OUT.refused` exists, exit 2 before any child starts (`NO_OVERWRITE`).
3. `argv, cwd = command(ROOT)`; the child's environment is this process's without `ELECTRON_RUN_AS_NODE`.
4. `subprocess.Popen(argv, cwd=cwd, env=env, stdout=PIPE, stderr=PIPE)`, then `communicate(timeout=DESCRIBE_TIMEOUT_S)`. On timeout, `taskkill /PID <child pid> /T /F` (the recorded pid only; `kill()` off Windows), drain the pipes, and add `timeout`.
5. Write stderr to `OUT.stderr.txt` (mode `xb`).
6. A non-zero child exit adds `harness-exit` with the code; then `refusals(stdout)` is added.
7. Any reason: write the stdout bytes to `OUT.refused` (mode `xb`), print `refused:` and each reason, exit 1. No `OUT` is written.
8. Otherwise write the stdout bytes to `OUT` (mode `xb`), unchanged, and print `captured: <n> bytes sha256 <hex>`; exit 0.

**`check FILE`:** exit 2 when `FILE` is missing; else `refusals(FILE bytes)`: exit 0 with `ok:` and the size when empty, else `refused:` with every reason and exit 1. All output is ASCII. `OSError` and `ValueError` exit 2.

### The tests: `docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py` (new, LF, pytest)

Where they live and how they run (brief §Where the tests run): under this plan folder, as Session 92's plan-local scripts were, because the script lives in a plan folder and `tests/` holds the product and `tools/` suites (D-1202). The gate runs them by path: `uv run pytest docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py --tb=short -q -rs -p no:cacheprovider --basetemp D/pytest-<stage>` with `TMP` and `TEMP` at `D/tmp`; no product suite runs. The file is ASCII only and builds every arrow, dash and mojibake string from `\u` escapes. `SCRIPT` is the script's path; every test asserts `SCRIPT.is_file()` first and then loads the module with `importlib` inside the test body, so before Green each test fails by assertion and none by collection. Fixtures are built in `tmp_path`:

- `CLEAN`: `"## Server instructions\n\nA \u2192 B \u2013 C\n## avkit_capture description\n\nx \u2192 y \u2013 z\n" + CUT + "\n\n- avkit_capture.crop: c\n"`, UTF-8, LF.
- `MOJ = CLEAN.encode("utf-8").decode("cp437").encode("utf-8")`: the real arrow and dash bytes decoded through cp437, as PowerShell does.

| Test | What it asserts |
|---|---|
| `test_ac_1_clean_passes` | `refusals(CLEAN) == []`; `main(["check", f])` exits 0 |
| `test_ac_2_cp437_fixture_refused` | `MOJ` gives exactly `mojibake`; `check` exits 1 and prints `mojibake` |
| `test_ac_2_cp437_crlf_refused` | `MOJ` with CRLF gives `cr` and `mojibake`; exit 1 |
| `test_ac_3_mixed_arrow_refused` | a real arrow beside a mojibake dash is refused as `mojibake` |
| `test_ac_3_mixed_dash_refused` | a real dash beside a mojibake arrow is refused as `mojibake` |
| `test_ac_4_refuses[...]` | seven cases, each with its reason: `empty`; UTF-8 BOM, `bom`; UTF-16 BOM, `bom`; invalid UTF-8 (`80`), `not-utf8`; a bare CR, `cr`; no CUT, `cut`; two CUTs, `cut` |
| `test_ac_5_one_guard` | `GUARD.__file__` resolves to Session 92's `eval-rerun.py` and `GUARD_PATH` names it; `GUARD.CUT` equals a separately loaded copy's; the script's source holds no `re.compile`, no `cp437` and no `MOJIBAKE =` assignment. (An identity check on the pattern alone proves nothing: Python's regex cache returns the same object for a copied pattern, `xp/probe_guard.txt`.) |
| `test_ac_5_stub_guard_used` | `monkeypatch.setattr(ed, "GUARD", stub)`, where `stub` is a `types.SimpleNamespace` with `MOJIBAKE = re.compile("ZZ")` and the real `CUT`: `refusals` of a clean file holding `ZZ` names `mojibake`, and `refusals(MOJ)` no longer does. A script with its own pattern fails this |
| `test_ac_6_capture_*` | six cases with `command` monkeypatched to a Python child (`sys.executable -c ...`) and `BASE` to a `tmp_path` folder: the child's bytes (`CLEAN`, written with `sys.stdout.buffer`) land in `OUT` byte for byte, with stderr in `OUT.stderr.txt`, exit 0; an existing `OUT` gives exit 2 and the child never runs (a marker file it would write stays absent); a child exit 3 is refused with `harness-exit`, exit 1, no `OUT`; a child writing `MOJ` is refused with `mojibake`, `OUT.refused` equals `MOJ`, no `OUT`; a child that sleeps past a `DESCRIBE_TIMEOUT_S` of 2 is refused with `timeout` within 30 s; a root outside `BASE` gives exit 2 |
| `test_ac_7_cli_*` | no argument, an unknown command and a missing `check` file exit 2; `DIST` monkeypatched to a missing path makes `capture` exit 2 with "build first"; every captured stdout and stderr line in the file's tests is ASCII |
| `test_ac_7_guard_missing` | three parts: `load_guard(tmp_path / "none.py")` raises `OSError`; a child `sys.executable -I -c` that replaces `importlib.util.spec_from_file_location` with a function that returns `None`, sets `sys.argv` to `check FILE` and runs the script with `runpy.run_path(SCRIPT, run_name="__main__")` exits 2 with stdout starting `error: guard not loaded:`, all ASCII, and no `Traceback` in stderr (the module-level `try` itself is exercised); and `monkeypatch` of `GUARD` to `None` makes `main(["capture", root, out])` exit 2 with no child started and no `OUT` |

### The run book: `eval-run.md` (LF stays LF)

Two edits, written as bytes with `newline=""` and checked by `edr-check.py doc` against the row-0 copy (`STEP3_NAMES_SCRIPT`). The exact text of both is in `edr-check.py` (`NOTE`, `STEP3`); both are ASCII and hold no `text` block, so `blocks()` still finds four.

1. After line 6, a blank line and the dated note:

   > Changed 2026-11-18 (Session 95, issue `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE`): step 3 used to capture `describe` with a shell redirect. PowerShell decoded the server's UTF-8 through the console code page (cp437), so Session 64's receipt holds 9 mojibake arrows and 2 mojibake en dashes and no real one, and the eval prompts built from it read that text. Step 3 now runs `eval-describe.py`, which keeps the raw bytes and refuses mojibake with the guard from Session 92's `eval-rerun.py` (D-1186). Session 64's task rows and receipts are kept as they ran.

2. Line 24 (step 3) becomes:

   > 3. **Describe.** Run `uv run python docs/execution/plans/2026-11-11-capture-export-copy/eval-describe.py capture C:/Temp/av-kit/s64/eval/<label>/root <receipt>`, with a new `<label>` (Session 64 used `describe`) and a `<receipt>` path that does not exist yet. Step 2 builds first. It runs `eval-harness.ts` `describe` from `mcp-server` in a subprocess and writes the server's stdout bytes to `<receipt>` unchanged, and its stderr to `<receipt>.stderr.txt`. It refuses output that is not UTF-8 or holds a BOM, a CR byte or cp437 mojibake, or lacks exactly one CUT line: it exits 1 with a named reason, writes no receipt and keeps the bytes as `<receipt>.refused`. It never overwrites a file (exit 2). Never capture `describe` through a shell redirect: a PowerShell redirect that merges stderr decodes the bytes through the console code page, and older PowerShell decodes every redirect.

The sub-bullets at `:25-26` ("the receipt's text above the line ...", "the whole receipt with the CUT line deleted") already read the step's output and stay as written; step 4.2's `{{DESCRIBE}}` reads them. The planned result is 6,980 bytes (`edr-plan-doc-probe.txt`). Session 64's `task.md`, its plan and its receipts are not touched (§Out of Scope).

### Plan-local checker: `edr-check.py` (written at plan time, LF, standard library)

Loads Session 92's guard (no second pattern) with bytecode writing off, inside `try`, and exits 2 with `error: guard not loaded:` when it cannot, and checks what pytest cannot: the real harness, the real run book and the records. Modes: `old E1 STEP3FORM` (AC-8), `live RECEIPT DIRECT_ROOT DIRECT_OUT` (AC-9), `doc RECEIPT` (AC-10), `records [--record]` (AC-11), `--selftest` (26 checks on fixtures, 0 failures at plan time, `edr-plan-selftest.txt`, among them a missing guard file and the exit-2 message). Output is ASCII; exit 0, 1 or 2 as `eval-describe.py`.

- `old` needs both receipts and passes only when each holds at least one `MOJIBAKE` match and exactly one CUT line, after `[rtk]` lines are dropped and CRLF is normalised.
- `live` makes its own direct read: `npx.cmd tsx <HARNESS> DIRECT_ROOT describe` from `mcp-server` with stdout piped (a different launcher from the script's, the same harness), timeout 300 s with `taskkill` by the recorded pid. Then: the receipt equals the direct bytes; strict UTF-8; no BOM; no CR; no `MOJIBAKE` match; no mojibake arrow or dash sequence; at least 2 real arrows and 2 real en dashes (the expected description alone holds 2 of each); one CUT line; the text after CUT holds the line `## avkit_convert action notes` (the last section, `s64-E1-describe.txt:710`) and the file ends in LF; the same bytes decoded through cp437 do match `MOJIBAKE` (so the clean result is not a lucky absence of non-ASCII text); `GUARD.build(eval-run.md, receipt, transcript, expected)` gives three prompts, each free of mojibake and holding `capture-description.expected.txt` verbatim; `RECEIPT.stderr.txt` exists and `RECEIPT.refused` does not. What the equality proves is narrow: a second launcher (`npx.cmd` through `cmd.exe` against node on tsx's CLI) and a second root give the same bytes, and a capture cut short yet clean is caught, since the refusals check nothing after CUT. It is not the proof that `capture` leaves the bytes unchanged; AC-6's fake child is.
- `doc` compares `eval-run.md`'s bytes with `expected_doc(row-0 copy)` and runs `build()` on the new text.
- `records --record` writes `baseline-records.json` once (refuses if it exists); `records` compares; both run `eval-rerun.py --selftest` and `eval-check.py --selftest` through `sys.executable`.

### Boundary Inventory

| Boundary | Input | Owner | Refusal |
|---|---|---|---|
| CLI argv | `capture ROOT OUT`, `check FILE` | `eval-describe.py` `main` | Usage, exit 2 |
| Root path | `ROOT` | `capture` step 1 and the harness `evalRoot` | Outside `BASE`: exit 2 |
| Output paths | `OUT` and its two side files | `capture` step 2 | Exists: exit 2 (`NO_OVERWRITE`) |
| Child stdout | Bytes from the harness | `refusals` | `NAMED_REFUSAL`, exit 1 |
| Child process | Exit code, wall time | `capture` steps 4 and 6 | `harness-exit`, `timeout` |
| Build output | `dist/index.js`, tsx CLI | `command` | Missing: exit 2 "build first" |
| Guard module | `eval-rerun.py` | `load_guard` under `try`, bytecode writing off | Missing, unloadable or lacking `MOJIBAKE`/`CUT`: exit 2, `error: guard not loaded: <path>: <exception>`, no traceback, no child |

No API route, OpenAPI document, MCP tool, UI or Python package changes.

### Acceptance Criteria

Each AC has an observable, the call chain it runs through and a negative oracle. AC-1 to AC-7 are pytest tests (FAIL_TO_PASS); AC-8 to AC-13 are row checks.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-1 | test | A clean UTF-8 receipt with real arrows and dashes and one CUT line passes `refusals` and `check` exits 0 (`main` → `refusals`) | Issue; grouping §3 | AC-2 to AC-4 hold the refusals; the test fails before Green by assertion |
| AC-2 | test | A fixture made by decoding real UTF-8 arrow and dash bytes through cp437 is refused as `mojibake`, exit 1, in LF and in CRLF form (`cr` and `mojibake`) | Brief §Acceptance; grouping §3 | A guard that let it through fails both tests |
| AC-3 | test | A mixed file, a real arrow with a mojibake dash and a real dash with a mojibake arrow, is refused as `mojibake` | Brief §Acceptance | A guard that only counts real characters, or only one sequence, fails |
| AC-4 | test | Empty, UTF-8 BOM, UTF-16 BOM, invalid UTF-8, bare CR, no CUT and two CUTs are each refused with their named reason | `NAMED_REFUSAL`; grouping §3 | Each case names the reason it must print |
| AC-5 | test | The guard is Session 92's: loaded from `eval-rerun.py` by `GUARD_PATH`, with no second pattern in the script, and the script refuses with whatever pattern the loaded module holds (a stub guard swapped in changes what is refused) | `ONE_GUARD`; brief §The model; D-1201 | A copied pattern fails the source check and the stub check (the regex cache makes an identity check blind to a copy) |
| AC-6 | test | `capture` writes the child's stdout byte for byte and its stderr beside it; never overwrites; refuses a failing child, a mojibake child and a timed-out child with no `OUT`; refuses a root outside `BASE` (`main` → `command` seam → `Popen`) | `RAW_CAPTURE`; `NO_OVERWRITE` | Each refusal case asserts `OUT` absent; the overwrite case asserts the child never ran |
| AC-7 | test | Usage errors exit 2; a missing build exits 2 with "build first"; a guard file that is missing or cannot load exits 2 with `error: guard not loaded:` and starts no child; every message is ASCII | Boundary Inventory | A non-ASCII message, a traceback or exit 1 on a guard-load failure fails |
| AC-8 | reproduction | Measured Red, at row 1, before the script exists, both old forms run by one `pwsh -NoProfile -File` run of this folder's `edr-old.ps1` (so the driver's console settings play no part), which first records the PowerShell version, `[Console]::OutputEncoding.CodePage` and `$OutputEncoding.WebName`: the E-1 form (`rtk proxy npx tsx ... describe *>` on root `s95-old`) and the step-3 form (`npx tsx ... describe > f 2>&1` on `s95-old3`, the form Session 92 measured) each give at least one `MOJIBAKE` match and exactly one CUT line (`edr-check.py old`). After Green, `eval-describe.py check` refuses `edr-old-e1.txt`, `edr-old-step3.txt` and Session 64's `s64-E1-describe.txt` with exit 1 and `mojibake` | Brief §Red first; issue verification; S92 `task.md:53` | S5 if either form shows no mojibake; the check must exit 1, not 0 or 2 |
| AC-9 | live | `eval-describe.py capture` on the real harness (root `s95-describe`) exits 0 and writes `D/edr-describe.txt`, and `edr-check.py live` passes: byte-identical to an independent `npx tsx` read on `s95-direct` (another launcher and another root give the same bytes, and a clean but truncated capture is caught), the text after CUT holds `## avkit_convert action notes` and the file ends in LF, strict UTF-8, no BOM or CR, no mojibake, at least 2 real arrows and en dashes, one CUT, the cp437 trap real, three clean prompts from `build()`. That the script leaves the bytes unchanged is AC-6's proof, not this one | Brief §Acceptance; `RAW_CAPTURE` | Any failing check is S10; the guard is never edited to pass |
| AC-10 | doc | `eval-run.md` equals its row-0 bytes with the dated note after line 6 and step 3 replaced, LF only, and `build()` still makes three prompts from the new text with the AC-9 receipt (`edr-check.py doc`) | `STEP3_NAMES_SCRIPT`; brief §Records stay records | Any other byte change fails the exact-bytes check |
| AC-11 | records | The nine record files keep their row-0 SHA-256 and `eval-rerun.py --selftest` and `eval-check.py --selftest` exit 0 (`edr-check.py records`) | `RECORDS_KEPT`; brief §Records stay records | A changed record or a failing selftest exits 1 |
| AC-12 | register | `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` is `resolved` through `issue-resolve.py` (bound to the row-0 register hash) on `tools/issue_triage` `model`, with a `verification` and `resolution_path` that cite the AC-8 and AC-9 receipts and Session 95; `render` and `render --check` pass; grouping row 95 reads `executed (Session 95)` and no other grouping line changed | Brief §Acceptance; grouping §6 | A change to any other issue, key or line fails the row's check |
| AC-13 | gate | `session-gate.ps1` ends `session-gate: all steps exit 0`: the home-path check before (row 0) and after, `ruff format --check` and `ruff check` on the new Python, the pytest file, the eol check on every edited file, the records, the doc and a fresh live capture on the final tree | Brief §Gate | Fail-fast; later steps `not_run` |

### Spec Sufficiency Table

| Question | Answer | Source |
|---|---|---|
| Where does the guard live? | In `eval-rerun.py`, unchanged; the new script imports it | D-1201 A |
| What does the capture refuse? | Not UTF-8, a BOM, a CR byte, mojibake, CUT not exactly once, a failing or timed-out child; its own raw-capture checks, sharing only `MOJIBAKE` and `CUT` with `real_surface` | Grouping §3; `MOJIBAKE` and `CUT` (D-1186) |
| Which mojibake does it catch? | The cp437 reading only; another code page passes `mojibake` but its CRLF still trips `cr` (a stated limit, not widened) | §What the code shows; `edr95-expert-pass.txt` |
| What if Session 92's file is gone? | Exit 2 with a named message; nothing runs unguarded | `ONE_GUARD`; Boundary Inventory |
| What may it change in the bytes? | Nothing | Brief §Acceptance |
| Is a build needed? | Yes: the harness connects to `dist/index.js`; it is gitignored | `eval-harness.ts:14`; `.gitignore:17` |
| What happens to Session 64's record? | Kept byte for byte; a dated note in `eval-run.md` | Brief §Records stay records |
| Is an eval rerun? | No | Brief §Not in scope; grouping §3 Gate |
| Where do the tests run? | Pytest under this plan folder, by path | D-1202 |

#### Files Modified

| Path | Change | Row | Line endings |
|---|---|---|---|
| `docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py` | New | 1 | LF |
| `docs/execution/plans/2026-11-11-capture-export-copy/eval-describe.py` | New | 2 | LF |
| `docs/execution/plans/2026-11-11-capture-export-copy/eval-run.md` | Note after `:6`; step 3 at `:24` | 4 | LF |
| `.agent/context/known-issues.yaml` | The issue resolved | 5 | LF |
| `.agent/context/known-issues.md` | Generated by `render` | 5 | LF |
| `.agent/context/grouping/2026-11-18-eval-describe-session-grouping.md` | §6 row 95 (`:118`) only | 5 | LF |
| `.agent/context/current-focus.md` | One entry | H1-3 | CRLF |
| `docs/execution/metrics.md` | One row | H2-3 | CRLF |
| The handoff, the two reviews, the reflection | New | H1-6, H1-7, H2-2 | LF |
| This plan folder's row-0 files and scripts | New | 0 to H1-2 | LF |

**Read, never changed** (bound in `baseline-scope.json` and, for the records, `baseline-records.json`): `docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py` and `capture-description.expected.txt`; Session 64's `eval-check.py`, `eval-harness.ts`, `eval-seed.py`, `task.md` and `implementation-plan.md`; `mcp-server/scripts/audit/backend.ts`; `C:/Temp/av-kit/s64-E1-describe.txt`; `docs/BUILD_PLAN.md` (row 6).

**Line endings** were measured with Python bytes (`edr-plan-bytes.txt`): `current-focus.md` (230 CRLF) and `metrics.md` (104 CRLF) are CRLF and stay CRLF; `eval-run.md`, `eval-check.py`, `eval-harness.ts`, Session 64's `task.md`, `eval-rerun.py`, the expected text, the grouping, `known-issues.yaml` and `known-issues.md` are LF and stay LF. New files are LF, written as bytes (Session 83 RULE-3).

**Foreign class** (Session 92 RULE-3): `.agent/model-registry.local.json`, `.claude/agents/*.md` and `.cursor/agents/*.md` belong to the coordinator. Row 0 binds them by hash; a change to them during the session is recorded in the handoff, is not S4, and stays out of the commit paths.

## Out of Scope

| Item | Basis |
|---|---|
| A model call or an eval rerun | Brief §Not in scope; grouping §3 Gate: Session 92 evaluated the live surface on clean text, and Session 64's eval would measure a surface no client serves |
| Any network use | Brief §Not in scope |
| Product code (`mcp-server/src`, `packages/`, `ui/src`) | Brief §Not in scope; the skip basis (H1-4) proves it |
| Editing `eval-rerun.py` or `eval-check.py` | D-1201 A; `RECORDS_KEPT` |
| Session 64's `task.md`, plan or receipts | Brief §Records stay records |
| Steps 1 and 4 of `eval-run.md` (`seed` and `call` redirects) | Their receipts are logs no model reads: the prompt is built from §Prompts and the describe receipt (step 4.2); the issue names step 3 only |
| An MEU or a `BUILD_PLAN.md` row | Grouping D-1199; row 6 |
| `TOOLING-SHARED-REGISTRY-COUPLING` and the other §1 rows | Grouping §1: not grouped |

## BUILD_PLAN.md Audit

No MEU, so no `docs/BUILD_PLAN.md` row and no `meu-status.yaml` change (grouping §1: "No build-plan home"). `docs/BUILD_PLAN.md` (LF, 19,968 B) names neither the eval run book nor the describe capture, so the hub is not applicable; row 6 checks that its bytes still equal the row-0 copy and that it holds no `eval-run` or `eval-describe` reference.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`, in the shape of Session 92's, records:

- `HEAD` (`baseline.sha`), `git status --porcelain --untracked-files=all` (`baseline-dirty.txt`, each path's SHA-256 in `baseline-dirty-hashes.json`), `git worktree list` and the host load (`host-load.ps1`);
- `git log --oneline 3e61b5b..HEAD -- mcp-server docs/execution/plans/2026-11-11-capture-export-copy docs/execution/plans/2026-11-17-mcp-audit-refresh`, which must be empty (S2);
- `baseline-scope.json` (each §Files Modified and "Read, never changed" path, and the foreign class, to its SHA-256 or `absent`; `eval-describe.py`, the test file and the handoff must be `absent`), `baseline-eol.json`, and `baseline-skip-hashes.json` (every tracked or untracked, not-ignored file under `packages/`, `tools/`, `ui/`, `tests/`, `mcp-server/src`, `mcp-server/scripts` and `mcp-server/tests`); the scope walk drops the secret file names and `.agent/fleet/hub/` before any stat (Session 83 RULE-2);
- byte copies of each scope file under `D/baseline-copies/<path>`, and `D/tmp`;
- the S2 binding: `eval-run.md:24` starts `3. **Describe.** From` and line 6 ends `the three `real-*` runs.`; `eval-rerun.py` defines `MOJIBAKE`, `CUT`, `build` and `real_surface`; the issue is `open` (read by key with `yaml.safe_load`, Session 92 RULE-2); grouping `:118` reads `proposed`; the roots `s95-old`, `s95-old3`, `s95-describe` and `s95-direct` under `C:/Temp/av-kit/s64/eval/` are absent; `mcp-server/node_modules/tsx/dist/cli.mjs` exists;
- `uv sync --frozen --offline --all-packages` and `tools/check_home_path.py` (before);
- the copies: `red-check.py` from Session 83 (`2026-11-15-docs-path-hygiene`), and `identity.py`, `eol-check.py`, `issue-resolve.py` and `host-load.ps1` from Session 92, with this plan's names (task row 0);
- `edr-check.py records --record` (`baseline-records.json`, both selftests);
- the `red-check.py`, `eol-check.py` and `edr-check.py` selftests, then `ruff format --check` and `ruff check` on this folder's Python (Session 82 RULE-1; Session 89 RULE-3 ran the same on `edr-check.py` at plan time, `edr-plan-ruff.txt`).

### 2. Red, then Green (rows 1 and 2)

Row 1 builds the server (`npm --prefix mcp-server run build`; `dist/` is ignored, and `git status` must show no `mcp-server` path afterwards), then runs this folder's `edr-old.ps1` (written at plan time, LF, parsed clean, `edr-plan-ps-parse.txt`) under `pwsh -NoProfile -File`, in the shape of Session 92's `run-row5-prep.ps1`: the script records the shell (`$PSVersionTable.PSVersion`, `[Console]::OutputEncoding.CodePage`, `$OutputEncoding.WebName`) in `edr-old-env.txt` and runs both old-redirect forms on new roots in that same process, so the driver's own console settings cannot change the result. Both forms must reproduce (AC-8). Then it writes the test file and runs it: every test must fail by assertion (`red-check.py --require test_ac_1` … `--require test_ac_7`); the file's SHA-256 is recorded. Row 2 writes `eval-describe.py`; the same file must pass with no skip and an unchanged hash (S3), `check` must refuse `edr-old-e1.txt`, `edr-old-step3.txt` and `s64-E1-describe.txt`, and ruff must pass on both new files.

### 3. Live, doc and records (rows 3 and 4)

Row 3 runs `capture` on `s95-describe` and `edr-check.py live` on `s95-direct` (AC-9). Row 4 edits `eval-run.md` and runs `edr-check.py doc` and `eol-check.py` (AC-10); `records` runs in the gate (AC-11).

### Session gate (H1-2)

`session-gate.ps1`, in the shape of Session 92's, fail-fast, later steps printed `not_run`, last line `session-gate: all steps exit 0`:

| Stage | Steps |
|---|---|
| Identity | `identity-before` (`identity.py`, which clears `ELECTRON_RUN_AS_NODE`, Session 88 RULE-3) |
| Static | `task-contract`; `scope-paths`; `line-endings` (`eol-check.py`); `home-path` (`tools/check_home_path.py`); `red-check-selftest`, `eol-check-selftest`, `edr-check-selftest`; `py-format` and `py-lint` on this folder's Python and `eval-describe.py` |
| Targeted | `edr-tests` (the pytest file, no skip); `edr-records` (AC-11); `edr-doc` (AC-10, with `D/edr-describe.txt`); `edr-old-refused` (`check` exits 1 on `edr-old-e1.txt`, `edr-old-step3.txt` and `s64-E1-describe.txt`) |
| Host load | `host-load` (Session 81 RULE-2) |
| Fresh full | `mcp-build`; `edr-live-gate`: `capture` on `s95-gate-<stamp>` into `D/edr-gate-<stamp>.txt`, then `edr-check.py live` on `s95-gate-<stamp>-direct` (a new stamp per gate run, so `NO_OVERWRITE` never trips on a rerun); `issues-render-check`; `state-render` |
| Identity | `identity-after` |
| Skipped, with reasons | `py-tests`, `py-types`, `ui-types`, `ui-lint`, `ui-tests`, `ui-build`, `ui-electron`, `mcp-types`, `mcp-tests`, `openapi`, `mcp-audit`: every file under `packages/`, `tools/`, `ui/`, `tests/` and `mcp-server/{src,scripts,tests}` keeps its row-0 hash (H1-4), and no product suite runs in this session |

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` appears | Stop; re-plan the context tool decision |
| S2 | A row-0 anchor is gone or changed in meaning, a commit since `3e61b5b` touches `mcp-server` or either eval plan folder, the issue is not `open`, row 95 is not `proposed`, an `s95-*` root exists, or tsx's CLI is missing | Stop; a moved line only is fixed in the handoff (Session 51 RULE-3) |
| S3 | A Red test fails for a setup reason or passes, or Green needs a test change | Stop; never edit the test to pass |
| S4 | `git status` lists a path outside this plan's scope, `baseline-dirty.txt` and the foreign class, or a scope path no earlier row wrote differs from `baseline-scope.json` | Stop and ask Mat; never commit, stash or revert another session's work |
| S5 | Either old form at row 1, run under `pwsh -NoProfile -File` from `edr-old.ps1`, shows no `MOJIBAKE` match or not exactly one CUT line | Stop; record `edr-old-env.txt` and re-plan: the Red is not measured on this shell |
| S6 | Codex is unavailable or the ledger refuses a round | Mat |
| S7 | The build fails with `EPERM` or `EBUSY` (a held file) | Tell Mat; never stop a process |
| S8 | The home-path check finds a new hit | Stop; fix the file, never extend the allow-list |
| S9 | A skip-basis file changed (H1-4) | Stop; the skipped suites must run |
| S10 | `capture` refuses on the real harness, or `edr-check.py live` or `doc` fails | Stop and record; never edit the guard, the expected text or a check to pass |

## Decision Log

> [!NOTE]
> D-1201 is the one brief the s95 brief asks for: where the single copy of the guard lives and how both plan folders reach it. Its §4a check found no M item: no push or destructive act (M-1, M-2); no new policy or threshold (M-3), since the refusals are Session 92's (D-1186); no tool shape (M-4), since no MCP tool, API or schema changes; no product fork (M-5); no conflict between sources (M-6), since the grouping and the brief both list a small script beside `eval-run.md`; no existing test assertion changes (M-7); the scope is the grouping's (M-8); nothing is waived, disclosed or run headless (M-9 to M-14). It is `mandatory: none`, presented as a brief because the s95 brief asks for one, and handed to the agent under Mat's 2026-11-18 words. D-1202 to D-1206 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. `open_decisions` is empty and there is no STOP item; D-1207 to D-1210 are left free for execution.
>
> **The fresh-context expert pass is adopted** (`C:/Temp/av-kit/eval-describe-raw-bytes/edr95-expert-pass.txt` and its `xp/` probes, 2026-11-18). It kept D-1201 at A and corrected the plan: D-1201's costs are restated (A ties the two plan folders both ways; B edits a folder the grouping keeps read-only and voids the skip basis; C edits a bound record and makes a load cycle); a guard file that cannot load exits 2 with a named message, and no `.pyc` is written into Session 92's folder; the Red asserts both old forms, run in one `pwsh -NoProfile` script; AC-9's equality is scoped to what it proves; AC-5 gains a stub-guard test, because the regex cache makes an identity check blind to a copied pattern; the cp437-only reach of the guard is stated as a limit. None of it hits an M item.
>
> **Earlier rows are not copied here.** D-1198 to D-1200 live in the grouping's §8 and D-1196 in the issue's decision log. H2-2 reads them through `--decision-source` on the grouping and `.agent/context/known-issues.yaml`, with `--decision-issue EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE`. `decision_sources` was probed at plan time with the H2-2 source list, against this plan itself (Session 90 RULE-2; `edr-decision-probe.txt`). Under HDP §6 the reflection's `### Decisions Log` lists only this session's reversible autonomous choices.

```yaml
decision_log:
  - id: D-1201
    stage: planning
    question: "Where does the single copy of the describe mojibake guard live, and how do both plan folders reach it?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a new eval-describe.py beside eval-run.md in Session 64's folder captures describe as raw bytes and imports MOJIBAKE and CUT from Session 92's eval-rerun.py, which stays byte for byte; eval-run.md step 3 names it."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py:35-43 — MOJIBAKE and CUT, the D-1186 guard, defined once"
      - "docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py:109 — load_checker: Session 92 already loads Session 64's eval-check.py by path rather than copying it"
      - "docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py:3-4 and :24-27 — Session 92 reads Session 64's eval-run.md and eval-check.py and relies on the checker staying unchanged"
      - ".agent/context/grouping/2026-11-18-eval-describe-session-grouping.md:65 — Session 92's folder is read, not edited"
      - ".agent/context/grouping/2026-11-18-eval-describe-session-grouping.md:75 — a script or a step in eval-check.py; the plan picks with an HDP brief"
      - "C:/Temp/av-kit/dispatch/s95-planner-brief.md §The model — editing eval-rerun.py is in scope only if named and proved unchanged"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. A puts the capture where the run book is and imports the guard where it already lives; no record file and no Session 92 file changes, only eval-run.md step 3 and a dated note, so Session 92's behaviour needs no proof of sameness and its selftest and record hash prove it untouched. A's real cost is coupling: Session 64's run book comes to depend on Session 92's folder, the reverse of the tie eval-rerun.py:24-27 already makes, so moving or tidying either folder breaks step 3; the script then exits 2 and names the missing file, never running unguarded. B (a shared tools/ helper) is the cleaner home in the abstract, but it edits eval-rerun.py in a folder the grouping keeps read-only (grouping :65), and a change under tools/ voids the H1-4 skip basis, so the skipped Python suites would have to run, all for one regex. C adds a capture step to eval-check.py, which Session 92's eval relied on staying unchanged (eval-rerun.py:3-4); it is a bound record (RECORDS_KEPT) and imports PIL at the top; and keeping one guard would make it import eval-rerun.py, whose load_checker loads eval-check.py again, an S64 to S92 to S64 load cycle. A text-only change (step 3 with a plain redirect and no script) was weighed and lost: it depends on the PowerShell version, leaves no guard, and cannot refuse the cp437 fixture grouping §3 asks for. Undo: delete one file and restore step 3. Two-way."
  - id: D-1202
    stage: planning
    question: "Where do the capture script's tests live and how are they run?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Pytest file test_eval_describe.py in this plan folder, run by path with --basetemp under D and -p no:cacheprovider; each test asserts the script file exists first, so Red fails by assertion with no stub."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/dispatch/s95-planner-brief.md §Where the tests run — pytest under the plan folder, or tests/tooling if a shared helper lands in tools/"
      - "docs/execution/plans/2026-11-15-docs-path-hygiene/task.md row 1 — each test asserts CHECK.is_file() first; red-check.py --require test_ac_N"
    research: { engine: none, sources: [] }
    reasoning: "The script lives in a plan folder (D-1201), so its tests live in one too; tests/ holds product and tools suites and would widen the skip basis. Asserting the file first keeps the Red an assertion, which red-check.py requires, without a stub that Green would have to replace. Two-way: one file."
  - id: D-1203
    stage: planning
    question: "How does the capture start the harness, and is a build needed?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Node runs mcp-server/node_modules/tsx/dist/cli.mjs on the harness directly, from mcp-server, with no shell; the script refuses with 'build first' when dist/index.js is missing. Row 1 builds with npm --prefix mcp-server run build; dist/ is gitignored."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-11-capture-export-copy/eval-harness.ts:14 — describe connects to mcp-server/dist/index.js"
      - "docs/execution/plans/2026-11-11-capture-export-copy/eval-run.md:23 — step 2 builds first"
      - ".gitignore:17 — mcp-server/dist/"
    research: { engine: none, sources: [] }
    reasoning: "A shell or an npx .cmd shim between the child and the pipe is one more place an encoding can change; node on the CLI file has none. The direct read in edr-check.py live uses npx.cmd on purpose, so the byte-equality check compares two different launchers of the same harness. The build is what step 2 already asks; its output never reaches git. Two-way."
  - id: D-1204
    stage: planning
    question: "How are receipts and roots named, and may a capture overwrite?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Never overwrite: capture exits 2 when the receipt or a side file exists. This session uses new roots s95-old, s95-old3, s95-describe, s95-direct and s95-gate roots named by a time stamp; Session 64's roots and receipts are kept. Step 3 takes a new root label and a receipt path that does not exist yet."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py:48-49 — Session 92 used fresh s92-* roots beside Session 64's"
      - "C:/Temp/av-kit/dispatch/s95-planner-brief.md §Records stay records — Session 64's eval receipts stay as they are"
    research: { engine: none, sources: [] }
    reasoning: "An overwrite would let a later run destroy the evidence an earlier one cited, which is what the records rule protects. New roots keep the harness's own scratch apart from Session 64's and 92's. Two-way."
  - id: D-1205
    stage: planning
    question: "How is the register updated?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Session 92's issue-resolve.py, copied with RESOLVE_KEYS status, verification and resolution_path, bound to the row-0 register hash, writing through tools/issue_triage model; then render and render --check; grouping row 95 only."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-mcp-audit-refresh/task.md row 8 — the same pattern for three issues"
      - ".agent/context/known-issues.yaml:5764 — the issue, open, with its root cause and verification"
    research: { engine: none, sources: [] }
    reasoning: "The brief asks for resolution through tools/issue_triage; issue-resolve.py writes through its model and refuses any change outside the named keys, and the hash binding refuses a register another session changed. The issue's root_cause and blast_radius stand. Two-way: a later triage can reopen it."
  - id: D-1206
    stage: planning
    question: "Which old-redirect form is the measured Red, and how are this session's loops and receipts named?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The Red asserts both old forms, the E-1 form (rtk proxy npx tsx ... describe *>) and the step-3 form (> f 2>&1); each must give at least one MOJIBAKE match and exactly one CUT line. Both run, after a probe of the PowerShell version and code pages, in one pwsh -NoProfile -File script, so the driver's console settings play no part. Receipts use the edr- prefix under C:/Temp/av-kit/eval-describe-raw-bytes; loops edr-plan-2026-11-18-eval-describe-raw-bytes and edr-execution-2026-11-18-eval-describe-raw-bytes."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-11-capture-export-copy/task.md row E-1 — the command that wrote s64-E1-describe.txt"
      - "C:/Temp/av-kit/s64-E1-describe.txt — its [rtk] line and 9 plus 2 mojibake sequences"
      - "docs/execution/plans/2026-11-17-mcp-audit-refresh/task.md:53 — row 5 ran the step-3 form inside pwsh -NoProfile -File run-row5-prep.ps1"
      - "C:/Temp/av-kit/mcp-audit-refresh/mar-eval-describe-attempt1.txt — that run: 37,406 B, 834 CR, cp437 arrows"
    research: { engine: none, sources: [] }
    reasoning: "The E-1 form wrote Session 64's receipt and the step-3 form is the one the issue blames and Session 92 already measured on this host, so the Red asserts both; asserting only one would leave the fixed step's own failure unshown. On this host's pwsh 7.6 a redirect that merges stderr decodes through the console code page and a plain > does not (the expert pass probes), so the run inside one pwsh -NoProfile script with the version and code pages recorded keeps the result tied to a stated shell; S5 stops if either form does not reproduce. Two-way."
open_decisions: []
```

Expert pass (fresh context): adopted 2026-11-18 (`edr95-expert-pass.txt`, with its `xp/` probes); D-1201 stays A.

### D-1201: Where should the one copy of the describe mojibake guard live?

**I recommend A: a small `eval-describe.py` beside `eval-run.md` that imports Session 92's guard.** The new script runs the describe step as raw bytes and refuses mojibake with the pattern Session 92 already wrote, loaded from its file, so there is still one copy. Neither Session 92's nor Session 64's scripts are edited: no record file and no Session 92 file changes; only step 3 of the run book and a dated note change. Step 3 names the script. The cost is a tie: Session 64's run book comes to depend on Session 92's folder, the reverse of the tie that already exists (`eval-rerun.py:24-27` reads Session 64's files), so moving or tidying either folder breaks step 3. The script then stops with exit 2 and names the missing file; it never runs unguarded. Undo: delete one file and put step 3 back.

- B: move the guard into a shared helper under `tools/` with its own tests, and change Session 92's `eval-rerun.py` to import it, proving its behaviour unchanged with its selftest and its Session 64 check. It edits a folder the grouping says is read, not edited (grouping `:65`), and a change under `tools/` voids the skip basis, so the skipped Python suites would have to run.
- C: add a `describe` capture step to Session 64's `eval-check.py`. Session 92's eval relied on that file staying unchanged (`eval-rerun.py:3-4`); it is a bound record and imports PIL at the top; and to keep one guard it would have to import `eval-rerun.py`, which loads `eval-check.py` again: a load cycle.
- D: keep things as they are: step 3 keeps the shell redirect, and the next eval that follows it reads mojibake.

A fifth way, only rewording step 3 to a plain redirect with no script, was weighed and lost: it depends on the PowerShell version, leaves no guard, and cannot refuse a cp437 fixture as grouping §3 asks.

Refs: D-1201; D-1186; D-1196; grouping `:65`, `:75`; `eval-rerun.py:3-4`, `:24-27`, `:35-43`, `:109`.

## Research References

- **PowerShell native output:** PowerShell 7.4 and later keep the bytes for a plain `>` redirect of a native command, but a redirect that merges stderr (`2>&1` or the all-streams redirect) decodes the output through `[Console]::OutputEncoding` and writes UTF-8 with CRLF; older PowerShell decodes every redirect, and Windows PowerShell 5.1 writes UTF-16 (Microsoft Learn, `about_Redirection` and `about_Character_Encoding`). Measured on this host (pwsh 7.6.10, `[Console]::OutputEncoding` 437, `$OutputEncoding` utf-8, `xp/env.txt`): `xp/plain.txt` keeps the real arrow and LF, while `xp/merge.txt` and `xp/star.txt` hold the cp437 sequences with CRLF. Both Session 64's E-1 form and step 3's form merge stderr, which is how Session 64's receipt and Session 92's attempt 1 were written.
- **Python `subprocess`:** `Popen` with `stdout=PIPE` and no `text` or `encoding` returns bytes unchanged; `communicate(timeout=...)` raises `TimeoutExpired` and leaves the child running, so the caller kills it and calls `communicate()` again.

## Planning receipts

All under `C:/Temp/av-kit/eval-describe-raw-bytes/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `probe_bytes.py`, `edr-plan-bytes.txt` | Line endings, sizes and SHA-256 prefixes of the scope; Session 64's receipt: 30,806 B, 725 CRLF, 9 mojibake arrows, 2 mojibake en dashes, no real one, 12 `MOJIBAKE` matches with the `[rtk]` line, one CUT |
| `probe_decisions.py`, `edr-decision-probe.txt` | `decision_sources` on the grouping, the register with the issue, and this plan (Session 90 RULE-2) |
| `edr-precedents.txt` | The cited lines of the precedents |
| `probe_doc.py`, `edr-plan-doc-probe.txt` | `edr-check.py` on the real files: Session 64's receipt gives 11 matches with the `[rtk]` line dropped, 9 and 2 sequences, one CUT; `expected_doc(eval-run.md)` is 6,980 B with four text blocks and step 3 at line 26 |
| `edr-plan-selftest.txt` | `edr-check.py --selftest`: 26 checks, 0 failures |
| `edr-plan-ruff.txt` | `ruff format --check` and `ruff check` on this folder's Python: clean |
| `edr95-expert-pass.txt`, `xp/` | The fresh-context expert pass, adopted: redirect probes (`xp/probe.ps1`, `env.txt`, `plain.txt`, `merge.txt`, `star.txt`) and guard probes (`xp/probe_guard.py`, `probe_guard.txt`: the regex cache and the missing-file load); the `.pyc` side effect is in the pass itself |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the issue, grouping §3 Session 95 and §8, the s95 brief, `eval-run.md`, `eval-harness.ts` and `eval-rerun.py` | `edr-plan-2026-11-18-eval-describe-raw-bytes` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-1 to AC-13 | `edr-execution-2026-11-18-eval-describe-raw-bytes` |
