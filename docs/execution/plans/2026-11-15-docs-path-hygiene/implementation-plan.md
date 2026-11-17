---
project: "2026-11-15-docs-path-hygiene"
date: "2026-11-15"
source: "grouping .agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md §3 Session 83; issues INSTALL-FOLDER-NAME-MISMATCH (triage D-811) and TRACKED-FILES-HOLD-HOME-PATH (grouping D-817, ruled A by Mat)"
meus: []
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
---

# Implementation Plan: The install folder's real name, and a check for the home folder's full path

> **Project**: `2026-11-15-docs-path-hygiene`
> **Build Plan Section(s)**: none (tooling and doc text; no MEU)
> **Status**: said to execute (USER_EXPLICIT 2026-11-15 'proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions.'). `plan_to_exec_gate: human`; the plan review was approved at round 3 (.agent/context/handoffs/2026-11-15-docs-path-hygiene-plan-critical-review.md).

---

## Goal

**Goal anchor:** av-kit's tracked text names the install folder the installer really uses (`Programs/av-kit-ui`), and a gate check, `tools/check_home_path.py`, fails when a file outside today's allow-listed evidence holds the home folder's full path; the six live files that hold it today are fixed, and every evidence file keeps its bytes.

This is Session 83 of the 2026-11-15 post-rc.3 grouping (§3, `:213-222`). It has two parts, in the grouping's order.

**Part 1: the install folder (`INSTALL-FOLDER-NAME-MISMATCH`, triage D-811).** electron-builder names a per-user one-click install folder after the package (`ui/package.json:2`, `av-kit-ui`), not the product. Three released candidates install to `%LOCALAPPDATA%/Programs/av-kit-ui`. D-811 chose to correct the docs and keep the package name. Two live lines still name `Programs/av-kit`:

- `docs/build-plan/07-distribution.md:40` (the on-disk layout);
- `README.md:174-175` (the hand-written MCP config, which a user copies; D-991).

The same layout, `07-distribution.md:43-49`, also puts the backend, ffmpeg and the MCP server under a `resources/extra/` folder. The installer makes no such folder: `ui/electron-builder.yml:32-35,52-53` copies them to `resources/avkit-backend`, `resources/ffmpeg` and `resources/mcp-server`, the packaged app reads `resources/mcp-server/index.mjs` (`ui/src/main/mcp-setup-prompt.ts:35`), and the same file says so itself (`07-distribution.md:194`, `:314`). This plan corrects that block too (D-996).

The newest round-trip script, `docs/execution/plans/2026-11-08-release-rc2/install-roundtrip.ps1`, already names and refuses the right folders (`:6`, `:55-58`). The two older scripts are finished sessions' evidence and stay as they are (D-990).

**Part 2: the home folder (`TRACKED-FILES-HOLD-HOME-PATH`, D-817 ruled A).** On 2026-11-15 the tracked tree held the home folder's full Windows path on 130 lines in 66 files. Sixty of those files are evidence (16 handoffs, 14 session digests, 30 plan-folder files), and six are live. Mat's ruling (grouping `:289-293`, brief `:297-323`) is:

- a check, run by the gate, that refuses new instances;
- today's evidence files allow-listed by name;
- the six live files fixed;
- evidence kept byte for byte.

Nothing in this plan writes the home folder's path into a tracked file. The check builds its pattern from `Path.home()` or `--home`, tests use the fake home `C:\Users\fixture`, and every replacement text uses `~`, `C:/Users/YOU` or `C:/Users/avkit`.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). The work is twelve known lines in six files, two doc lines, one short new tool and one register; every target was found by a byte-level scan and read verbatim, which is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host.
  - Validation goes through `rtk proxy`.
  - Receipts go under `C:/Temp/av-kit/dph/`, named `dph-*`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
  - Every pytest run sets `TMP` and `TEMP` to `C:\Temp\av-kit\dph\tmp`, to keep pytest's temp dirs away from the home folder.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` is never opened; the check drops that prefix before it reads anything.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` does not apply, because the driver OS is the target OS. The check itself is for the maintainer host: on another machine the home folder differs and the check finds nothing (D-988).
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `dph-plan-2026-11-15-docs-path-hygiene` and `dph-execution-2026-11-15-docs-path-hygiene`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, turn tokens off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor.
  - Every review prompt tells the reviewer to write `~` or "the home folder" and never the full path, because its review file is a tracked file that the check reads (S7).
  - The fallback is Mat.
- **Queue:** Session 87 (`framework-small-syncs`) is committed first; then Sessions 75 to 82 run, and this session runs last. Mat has not said whether each session is committed when it closes, so their changes may be uncommitted here. Every baseline and scope check is path-scoped and bound to content, not to `HEAD` (D-995).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| Docs path hygiene (no MEU) | `.agent/context/handoffs/2026-11-15-docs-path-hygiene-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-15-docs-path-hygiene-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-15-docs-path-hygiene-implementation-critical-review.md`

The single non-MEU handoff follows Session 49b (`2026-11-05-closeout-register-grammar`) and `2026-11-15-closeout-record-once`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `C:/Temp/av-kit/dph/base/`, `C:/Temp/av-kit/dph/inventory-0.json` |
| WP-2 | The check: Red, then Green (rows 1 and 2) | WP-1 | shared | `tests/tooling/test_check_home_path.py`, `tools/check_home_path.py` |
| WP-3 | The allow-list and the repo Red (rows 3 and 4) | WP-2 | shared | `tools/home_path_allowlist.txt`, `allowlist.sha256` |
| WP-4 | The live fixes: docs, tests, register, D6 row (rows 5 to 8) | WP-3 | shared | the seven edited files, `known-issues.yaml`, `known-issues.md`, `.agent/docs/commands.md` |
| WP-5 | The repo Green and the last issue (rows 9 and 10) | WP-4 | shared | `dph-repo-green.txt`, `dph-repo-green-2.txt` |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | Handoff, review, reflection |

## User Review Required

> [!IMPORTANT]
> **Every session's gate gets a new step, `home-path`** (D-988, applying your D-817 ruling). It runs `uv run python tools/check_home_path.py`, which reads every tracked and untracked (not ignored) file and fails when one holds your home folder's full path, in any of its usual spellings (`\`, `/`, `\\`, any case, and the Git Bash form `/c/Users/...`).
>
> - It prints only `path:line`, never the line, so a receipt cannot leak the path.
> - The 60 evidence files of today are listed by name in `tools/home_path_allowlist.txt`, each with a digest of its content (D-997). A listed file whose content changes fails the check, so nothing can be added to an evidence file unseen. Adding a name, or a new digest for a name, loosens the check and needs a decision; a file that stops holding the path is dropped from the list by `check_home_path.py --prune` (a stale entry fails the check).
> - It reads UTF-8, UTF-16 and UTF-32 text. A file that holds a NUL byte and has no byte-order mark is read in every way it could be text, so no file is skipped, and a binary file that holds the path is reported too. It matches only your own folder name, not a longer one that starts with it.
> - It is not added to CI or to `agent-commit.ps1`: on the runner the home folder differs, so it would pass vacuously.
>
> **Files written by Sessions 75 to 82 that hold the path** (D-989, a brief handed to me by your 2026-11-15 ruling): if row 0 finds evidence files written after today's count (a handoff, review, digest, reflection or plan-folder file), they are allow-listed by name as well, and the handoff lists them. This session's own files are never allow-listed: a hit in this plan's folder or in a `2026-11-15-docs-path-hygiene-*` handoff or review stops the session (S7). A live file found then is fixed if it is a doc, and stops the session if it is a test, a source file or a script (D-993, S2).
>
> **The README's hand-written MCP config changes** (D-991, handed over): `Programs\\av-kit\\` becomes `Programs\\av-kit-ui\\` on its two lines, which matches what the installer does. The old folder never existed on any install, and one edit undoes the change, so it is not a one-way door. It is published only when you push.
>
> **The two older round-trip scripts stay as they are** (D-990, handed over): they are finished sessions' evidence, and the rc.2 script already uses the right folder.
>
> **The install layout in `07-distribution.md` loses its `resources/extra/` level** (D-996): the installer puts the backend, ffmpeg and the MCP server directly under `resources/`, as the same file's `extraResources` table already says.
>
> **What this plan leaves out:** renaming the package (D-811), rewriting any evidence file (D-817 B), scrubbing the history, and the short form `~` (Session 77 scrubs it from Console output).

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `CHECK` | `tools/check_home_path.py` |
| `ALLOW` | `tools/home_path_allowlist.txt`: one `<digest>  <path>` entry per `EVIDENCE_SET` file (D-997) |
| `HOME_RE(home)` | The text pattern `CHECK` builds from a home path and matches against each decoded line (§The check). Never written out in a tracked file. |
| `DIGEST(path)` | The SHA-256, lowercase hex, of the file's bytes with each CRLF read as LF. Row 0 records it in `inventory-0.json`; row 3 writes it into `ALLOW`, and the two must agree (D-997). |
| `LIVE_SET` | The `(path, line)` pairs that `CHECK` reports at row 4 with `ALLOW` in place. The plan expects the 12 pairs of §Live fixes; row 0's `inventory-0.json` holds the real set. |
| `EVIDENCE_SET` | The files that hold an instance at row 3 and are of an evidence kind: `.agent/context/handoffs/*.md`, `.agent/context/sessions/*/digest.md`, `docs/execution/plans/<date>-*/**`, `docs/execution/reflections/**`, minus this session's own files (`PLAN/**` and `.agent/context/handoffs/2026-11-15-docs-path-hygiene-*`). `ALLOW` lists exactly these. A hit in this session's own files is S7, never an entry. |
| `BASE(path)` | The bytes of a file this plan edits, copied by row 0 to `C:/Temp/av-kit/dph/base/`. These are the post-Session-82 bytes, not `HEAD`. |
| `PLAN` | `docs/execution/plans/2026-11-15-docs-path-hygiene` |

### The check (`CHECK`, D-988)

`CHECK` is new, LF, standard library only, in the style of `tools/check_commit_identity.py` (a `_Usage` exception, an argparse subclass whose `error` raises it without echoing the arguments, a `_git` helper that drops stderr, a `PREFIX`). It runs as `uv run python tools/check_home_path.py [--repo PATH] [--home PATH] [--allowlist PATH] [--prune]`.

1. **The repo.** `git -C <repo> rev-parse --show-toplevel` must succeed; otherwise exit 2. `--repo` defaults to the current directory, and `--allowlist` to `<repo>/tools/home_path_allowlist.txt`. A missing allow-list exits 2.
2. **The files.** `git ls-files -z --cached --others --exclude-standard` lists tracked and untracked files and leaves out ignored ones.
   - Any path under `.agent/fleet/hub/` is dropped from the list before anything is read.
   - A listed path that is missing (a deletion not yet staged) or is not a regular file (a submodule) is skipped.
   - Each file is read as bytes and decoded by step 2a. A file that cannot be read exits 2 with `check_home_path: cannot read <path>`.
   - **Decoding (step 2a, R1-F2).** Decoding never raises: bad sequences are replaced (UTF-16 and UTF-32) or kept as surrogate escapes (UTF-8).
     - **A byte-order mark** sets the encoding, and the mark is removed. UTF-32LE (`FF FE 00 00`) and UTF-32BE (`00 00 FE FF`) are tested first, then UTF-16LE (`FF FE`), UTF-16BE (`FE FF`) and UTF-8 (`EF BB BF`).
     - **No mark, and a NUL byte anywhere in the file (R2-F1).** The file is not classified, and it is never skipped. It is scanned in five views: its raw bytes as UTF-8 (surrogate escapes kept), and its bytes decoded as UTF-16LE, UTF-16BE, UTF-32LE and UTF-32BE (bad sequences replaced). An instance in any view is `found`, and a `(path, line)` pair found in two views is printed once. So unmarked UTF-16 or UTF-32 text is read as text whatever its language, and a binary file that holds the path in ASCII, UTF-16 or UTF-32 is reported as well: that is an exposure, not a false positive. Such a file is counted in `nul=<k>`.
     - **Otherwise** the file is UTF-8 (surrogate escapes kept). A file in another single-byte encoding (cp1252, Latin-1) is therefore scanned by its ASCII bytes; a home with a non-ASCII segment is matched only in UTF-8, UTF-16 and UTF-32 files.
     - Lines are numbered by `\n` in each decoded text, and each of the five views numbers its own lines, so a CRLF file numbers as git does and a UTF-16 or UTF-32 file numbers as an editor shows it.
     - Measured on 2026-11-15 (`C:/Temp/av-kit/docs-path-hygiene/r1-measure.txt`, `r1-binary.txt`, `r2-measure.txt`): 2,299 files with no NUL and no mark, 1 UTF-8 file with a mark, 31 files with a NUL and no mark, and no UTF-16 file. The five-view rule finds the same 130 lines in 66 files as the earlier byte rule, and none of the 31 files with a NUL holds the path in any view, so the repo Red (AC-9) and `EVIDENCE_SET` do not change.
3. **The pattern, `HOME_RE(home)`.** `home` is `--home` or `Path.home()`. A value with a drive letter is read as a Windows path (`PureWindowsPath`) on any OS, and otherwise as a POSIX path.
   - **Windows home** (`<D>:\<s1>\…\<sn>`): two alternatives, both case-insensitive.
     - The drive form: `(?<![A-Za-z])` + `D:` + `[\\/]+` + the escaped segments joined by `[\\/]+`.
     - The Git Bash form: `[\\/]` + `D` + `[\\/]+` + the same segments. It covers `/c/Users/<name>` and `/mnt/c/Users/<name>`.
     - Both end with the boundary `B`.
   - **POSIX home** (`/s1/…/sn`): `(?<![A-Za-z0-9_])` + the segments joined by `/+` + `B`, case-sensitive.
   - **The boundary `B` (R1-F3)** is a lookahead after the last segment. It accepts the end of the line; a `\` or `/`; a character Windows forbids in a name (`<>:"|?*` or a control character); whitespace; a `'` or a backtick; or a run of `.,;!)]}` followed by one of those or by the end of the line. So `…\fixture.` at the end of a sentence, `…\fixture,` and `(…\fixture)` match, and `…\fixture.other`, `…\fixture-other`, `…\fixture_x`, `…\fixtures` and `…\fixtureé` do not.
   - A home with fewer than two segments below the root exits 2: such a pattern would match too much.
4. **The allow-list (D-997).** `ALLOW` is LF text.
   - Lines that are blank or start with `#` are skipped. The header cites D-817 and D-997, says that a new entry or a new digest loosens the check and needs an HDP decision, and says that a file that no longer holds the path is removed with `--prune`.
   - Every other line is `<digest>  <path>`: 64 lowercase hex characters, two spaces, and a repository-relative POSIX path. The list is sorted by path, and each path appears once.
   - A digest that is not 64 lowercase hex characters, an absolute path, a backslash, a `..` segment, a duplicate, an out-of-order line or a path under `.agent/fleet/hub/` exits 2 with `check_home_path: usage error: allowlist line <n> is malformed`. The line's text is never echoed.
   - A listed file whose `DIGEST` equals its entry is exempt and not reported. A digest match exempts the file on any machine and under any home, so a clone with another user name passes.
   - A listed file that is missing prints `check_home_path: stale <path>`.
   - A listed file whose `DIGEST` differs is scanned. If it holds an instance, it prints `check_home_path: changed <path>` (no `found` line and no line text); if it holds none, it prints `check_home_path: stale <path>`. So a home path appended to an evidence file, and any other byte edit that keeps the old path, both fail while `ALLOW` stays unchanged.
   - **Editing an evidence file later.** Evidence is not edited. A session that must change one removes every instance from it in the same edit; the entry is then `stale`, and `CHECK --prune` deletes it. `--prune` rewrites `ALLOW` (LF, header kept) without its stale entries, never adds an entry and never writes a digest, and then runs the check as usual. A changed file that still holds the path cannot be pruned. Writing a new digest for an entry, by hand or by a tool, is a new entry, and the header says a new entry needs an HDP decision.
5. **Output and exit.**
   - Each instance outside the allow-list prints `check_home_path: found <path>:<line>`, sorted by path and then line. The line's text is never printed.
   - With any `found`, `changed` or `stale` line, a final `check_home_path: refused found=<n> changed=<c> stale=<m>` and exit 1.
   - Otherwise `check_home_path: ok files=<n> allowlisted=<m> nul=<k>` and exit 0.
   - A usage error, a path that is not a repo, a home that is too short, a missing or malformed allow-list, a file that cannot be read, or git that cannot run exits 2.
   - Nothing `CHECK` prints holds the home folder or any line of a scanned file.

### Live fixes (D-992)

Each edit replaces only the named text on the named line, binds to the line's content (the line number may have moved), and keeps the file's line endings. `edit-check.py` compares each file to `BASE(path)`.

| File | EOL | Line (plan time) | Old text (home shown as `<home>`) | New text |
|---|---|---|---|---|
| `.agent/skills/git-workflow/SKILL.md` | CRLF | 153 (after Session 87) | `` `<home>\.gemini\antigravity-ide\brain\…` `` | `` `~\.gemini\antigravity-ide\brain\…` `` (rest of the line unchanged) |
| `_inspiration/capture-crop/design.md` | LF | 205 | `"path": "<home>/Desktop/2026-11-07_13-16-09.png"` | `"path": "C:/Users/YOU/Desktop/2026-11-07_13-16-09.png"` |
| `docs/build-plan/06-gui.md` | CRLF | 960 | `[<home>\Downloads\av-kit` + spaces + `]` | `[~/Downloads/av-kit` + spaces + `]` |
| `docs/build-plan/06-gui.md` | CRLF | 975 | `[<home>\Documents\Transcripts` + spaces + `]` | `[~/Documents/Transcripts` + spaces + `]` |
| `docs/build-plan/07-distribution.md` | CRLF | 40 | `# e.g. %LOCALAPPDATA%/Programs/av-kit` | `# e.g. %LOCALAPPDATA%/Programs/av-kit-ui` |
| `docs/build-plan/07-distribution.md` | CRLF | 43-49 (D-996) | the `│   ├── extra/` line, then `avkit-backend/`, `ffmpeg/` and `mcp-server/` one level below it | §The layout block |
| `README.md` | LF | 174, 175 | `…\\Programs\\av-kit\\av-kit.exe` and `…\\Programs\\av-kit\\resources\\…` | `…\\Programs\\av-kit-ui\\av-kit.exe` and `…\\Programs\\av-kit-ui\\resources\\…` |
| `ui/tests/unit/capture-interactive.test.ts` | LF | 14 | `const INBOX_PATH = '<home>/Pictures/av-kit/2026-08-27_12-00-00.png'` | `const INBOX_PATH = 'C:/Users/avkit/Pictures/av-kit/2026-08-27_12-00-00.png'` |
| `ui/tests/unit/dev-spawn.test.ts` | LF | 8 | `const pythonImage = '<home>/.local/share/uv/python/cpython.exe'` | the same with `C:/Users/avkit` for `<home>` |
| `ui/tests/unit/dev-spawn.test.ts` | LF | 76, 77, 88, 89 | `liveImage:` and `oursExe:` values `'<home>/.local/share/uv/python/cpython.exe'` | the same with `C:/Users/avkit` for `<home>` |
| `.agent/context/known-issues.yaml` | LF | 3368 (`root_cause`), 3379 (`notes`) of `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` | `<home>/.agent` | `~/.agent` |

Notes:

- **06-gui.md.** The bracketed field keeps its width: the new path is padded with spaces to the old content's width, so the line keeps its code-point length (88 at plan time, without the CR). The siblings at `:989`, `:999` and `:1042` already write `~/`.
- **07-distribution.md.** The layout block is §The layout block. Line 40 and the block are the only changes.
- **README.md.** Only the folder segment changes. `av-kit.exe` stays, because the file name comes from `productName`. The JSON block must still parse after the edit (`edit-check.py`).
- **The two UI tests.** `C:/Users/avkit` follows `ui/tests/unit/login-item.test.ts:3`. Only the constants change; no assertion's text changes (§UI test assertions).
- **known-issues.yaml.** Edited through the register tooling only (§The register).
- **commands.md** (CRLF) gains one row (§The D6 row).

### The layout block (D-996)

In `docs/build-plan/07-distribution.md` (CRLF), the seven lines from `│   ├── extra/` through `│   │   └── mcp-server/` become these six, and nothing else in the block changes. The `extra/` line goes. Each line below it moves up one level, which removes one `│   ` prefix. `mcp-server/` becomes `├──`, because `app.asar` now follows it at the same level. Each `#` comment keeps its column: four spaces are added before it.

```text
│   ├── avkit-backend/             # PyInstaller onedir (preferred over onefile)
│   │   └── avkit-backend.exe
│   ├── ffmpeg/
│   │   ├── ffmpeg.exe
│   │   └── ffprobe.exe
│   ├── mcp-server/                # compiled JS (Phase 5 dist/)
```

The block's other `extraResources` entries (`deno/`, `region-picker/`, the icons and the licence files) stay unlisted, as they are today; the table at `07-distribution.md:194` names them.

### UI test assertions (named for §4a M-7)

These are the existing tests whose expected value changes because a constant they compare against changes. The assertion text is unchanged in each; only the value it now expects differs, from the home folder's path to the `C:/Users/avkit` path.

| File | Describe / test | Assertion (line at plan time) | New expected value |
|---|---|---|---|
| `capture-interactive.test.ts` | `MEU-40 AC-40.33 interactive request lifecycle` › `a published capture whose complete rejects is never cancelled` | `:82`, `:83` compare against `INBOX_PATH` | `C:/Users/avkit/Pictures/av-kit/2026-08-27_12-00-00.png` |
| `capture-interactive.test.ts` | same › `the next tick retries the journalled completion…` | `:127` | same |
| `capture-interactive.test.ts` | same › `an Expired row drops the entry…` | `:193` | same |
| `capture-interactive.test.ts` | same › `a Cancelled row is terminal…` | `:216` | same |
| `capture-interactive.test.ts` | same › `a backend restart keeps the journal…` | `:240` | same |
| `capture-interactive.test.ts` | same › `a listing that no longer contains the id…` | `:288` | same |
| `capture-interactive.test.ts` | same › `Expired on the reconciling read drops the entry WITH the terminal notice` | `:323` | same |
| `capture-interactive.test.ts` | same › `the picker only opens for a Pending row that is not already journalled` | `:389` | same |
| `dev-spawn.test.ts` | `AC-19.22 DEV_SPAWN` › `owns the resolved Python image, never uv.exe` | `:14` `expect(resolved).toBe(pythonImage)`, `:22` `expect(argv[0]).toBe(pythonImage)` | `C:/Users/avkit/.local/share/uv/python/cpython.exe` |
| `dev-spawn.test.ts` | `confirmReadyAndPublish publishes from AVKIT_READY on the owned child stdout` (the `withheld` and `portZero` cases) | inputs at `:76-77`, `:88-89`; their assertions expect `false` and `[]` | unchanged (`false`, `[]`) |

The mock at `capture-interactive.test.ts:49` returns `INBOX_PATH` and changes with it. Row 6 runs both files and both must pass with no test skipped.

### The register (D-994)

`known-issues.yaml` (LF) changes in three issues, all through the plan-local `issue-resolve.py`. It is a copy of `2026-11-15-closeout-record-once/issue-resolve.py` with `SCRATCH = C:/Temp/av-kit/dph`, plus one mode:

- **`--scrub ISSUE.FIELD`** (repeatable) replaces each `HOME_RE` match in that string field with `~`. It imports the pattern builder from `CHECK`, so there is one definition, and it refuses when a named field has no match. The same held-handle, staged-copy, parsed-difference and `--expect-sha256` checks apply, and the parsed difference must be exactly the named fields.

The three changes, in two calls:

1. **Row 7**, bound to row 0's register hash (`baseline-scope.json`):
   - `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR`: `--scrub` on `root_cause` and `notes`. Nothing else in it changes.
   - `INSTALL-FOLDER-NAME-MISMATCH`: `status: resolved`; `verification` (today's `last_checked`, a `method` naming `dph-docs-check.txt`, a `result` quoting its `ok` line); `resolution_path` saying that Session 83 corrected `07-distribution.md` and the README to `Programs/av-kit-ui`, that the rc.2 round-trip script already used it, and that the older scripts stay as evidence (D-990).
   - Row 7 then writes the register's new SHA-256 to `register-row7.sha256`.
2. **Row 10**, after the repo Green, bound to `register-row7.sha256`:
   - `TRACKED-FILES-HOLD-HOME-PATH`: `status: resolved`; `verification` naming `dph-repo-green.txt` and quoting its `ok` line; `resolution_path` naming `CHECK`, `ALLOW`, the D6 row and the six fixed files.
   - It waits for row 10 because its verification quotes row 9's receipt. `CHECK` runs once more after it.

Every value written uses forward slashes and names no home path. After each call `issue_triage.py render` and `render --check` run. `known-issues.md` is generated and never hand-edited.

### The D6 row (D-988)

`.agent/docs/commands.md` (CRLF) gains one row, directly after the `| task-contract |` row, which `tests/tooling/test_framework_adoption.py:896` reads by its prefix:

```text
| home-path | static | `uv run python tools/check_home_path.py` | Every session: tracked and untracked (not ignored) files outside .agent/fleet/hub; allow-list tools/home_path_allowlist.txt (D-817); exit 0 ok, 1 an instance or a stale entry, 2 usage; maintainer host only, CI's home differs |
```

No other line of the file changes.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `CHECK` argv | the argparse subclass in `CHECK` | `--repo` a git work tree; `--home` a path with at least two segments below the root; `--allowlist` an existing file | An unknown flag exits 2 without echoing it |
| `ALLOW` lines | `CHECK` | sorted, unique, repo-relative POSIX paths; `#` comments and blank lines | Any other form exits 2, naming the line number only |
| `issue-resolve.py --scrub` | `issue-resolve.py` | `ISSUE.FIELD` names an existing issue and a string field with at least one match | Refused otherwise; the register is not written |

### Acceptance Criteria

Tests are named `test_ac_<n>_…`.

- **AC-1 to AC-7, AC-22 and AC-23** are in `tests/tooling/test_check_home_path.py` (LF). Each test builds a temp repo with a hermetic git environment (`GIT_CONFIG_GLOBAL` at a temp file, `GIT_CONFIG_NOSYSTEM=1`) and runs `CHECK` with `--home C:\Users\fixture` (or `/home/fixture` for AC-7) and its own allow-list. Each test asserts `CHECK.is_file()` before loading or running it. No test reads the real home folder.
- **AC-8 to AC-21** are plan-local checks, because they read the live repository. AC-22 and AC-23 come from Codex plan review round 1 (R1-F2, R1-F1) and are numbered last so the earlier numbers stay stable.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-1 | integration | Each form is reported as `found`: `C:\Users\fixture\a`, `C:/Users/fixture/a`, `C:\\Users\\fixture\\a`, `c:\users\FIXTURE\a`, `file:///C:/Users/fixture/a`, `/c/Users/fixture/a`, `/mnt/c/Users/fixture/a`, the home with nothing after it, and the home followed by `.` at the end of a sentence, by `,` and a space, by `)`, and by a closing quote; and each is found in every encoding §The check step 2a reads, with or without a byte-order mark and whatever else the file holds (the encoding fixtures are AC-22's) | Human-approved (D-817); Local Canon (D-988, the boundary and the decoding) | Each form is its own parametrized case; a form not reported fails it |
| AC-2 | integration | None of these is reported: `C:\Users\fixtures\a`, `C:\Users\fixture.other\a`, `C:\Users\fixture-other\a`, `C:\Users\fixture_x\a`, `C:\Users\fixtureé\a` (UTF-8), `C:\Users\YOU\a`, `D:\Users\fixture\a`, `fixture` alone, `~/a`, `%USERPROFILE%\a` | Local Canon (D-988) | A file holding only these exits 0; any `found` line fails |
| AC-3 | integration | Output: one `check_home_path: found <path>:<line>` per instance, sorted, with the right line number in an LF and a CRLF file; then `refused found=<n> changed=0 stale=0` and exit 1. stdout and stderr hold neither `Users` nor `fixture` (the scanned files are named without either word) | Human-approved (D-817) | The line text is a distinctive marker; the test fails if the marker appears in the output |
| AC-4 | integration | A file named in the allow-list with its `DIGEST` is not reported. A listed file that is missing gives `stale <path>` and exit 1. A digest that is not 64 lowercase hex characters, an absolute path, a backslash, a `..` segment, a duplicate, an out-of-order line and a hub entry each exit 2 without echoing the line. Comment and blank lines are skipped. A missing allow-list exits 2 | Human-approved (D-817) | The malformed lines carry a marker that must not appear in the output |
| AC-5 | integration | An untracked file that is not ignored is scanned; an ignored one is not; a tracked file deleted from disk is skipped without error; a file under `.agent/fleet/hub/` holding an instance is never reported and never opened (in-process run with the file reader patched to fail on any hub path) | Local Canon (D-988; the hub rule) | The hub case fails if the patched reader is called |
| AC-6 | integration | An unknown flag, a `--repo` that is not a repo, and a `--home` with fewer than two segments (`C:\`, `/home`) each exit 2, with no traceback and no argument echoed | Local Canon (`check_commit_identity.py` convention) | `Traceback` and the bad argument's marker must not appear |
| AC-7 | integration | With `--home /home/fixture`: `/home/fixture/a` and `/home/fixture.` at the end of a sentence are found; `/home/fixtures/a`, `/home/fixture.other/a`, `/home/fixture-other/a`, `/home/Fixture/a` and `C:\Users\fixture\a` are not | Research-backed (POSIX paths are case-sensitive) | The two non-matches are the negatives |
| AC-8 | unit | `inventory.py --check-allowlist --cross-check`: `ALLOW` lists exactly `EVIDENCE_SET`, sorted, with the D-817 header, each entry carrying the `DIGEST` that `inventory-0.json` recorded at row 0, so every `EVIDENCE_SET` file is byte for byte (CRLF read as LF) what it was when execution started; and `CHECK` run with an empty allow-list reports exactly the `(path, line)` set that `inventory.py`'s own pattern finds | Human-approved (D-817); Local Canon (D-989) | `inventory.py --selftest`: an allow-list with a missing entry, with an extra entry, with an entry whose digest differs from row 0's, and a fake `CHECK` output that drops one line are each refused; a fixture instance in a file under `PLAN/` or in a `2026-11-15-docs-path-hygiene-*` handoff is reported as `own` and fails, and is not written to the allow-list |
| AC-9 | integration | Repo Red (row 4): `CHECK` with `ALLOW` in place exits 1, and its `found` set equals `LIVE_SET` from `inventory-0.json` exactly, with no `stale` or `changed` line | Human-approved (D-817) | `inventory.py --expect-live` fails on any extra or missing pair |
| AC-10 | unit | `SKILL.md`: only the transcript line changes, its old text matches `HOME_RE`, its new text is §Live fixes', and every line keeps CRLF | Local Canon (D-992) | `edit-check.py --selftest`: a second changed line, an LF line and a wrong new text are each refused |
| AC-11 | unit | `design.md`: only line 205 changes, to `C:/Users/YOU/Desktop/…`; LF kept | Local Canon (D-992) | as AC-10 |
| AC-12 | unit | `06-gui.md`: only the two path lines change, each to `~/…` padded to the old width, so each line's code-point length is unchanged; CRLF kept | Local Canon (D-992) | `--selftest`: a line one character shorter is refused |
| AC-13 | unit | `07-distribution.md`: line 40 changes from `Programs/av-kit` to `Programs/av-kit-ui`, and the seven lines from `│   ├── extra/` through `│   │   └── mcp-server/` become exactly §The layout block's six; no other line changes; each comment keeps its column; CRLF kept | Local Canon (D-811, applied; D-996) | as AC-10; `--selftest` also refuses a layout that keeps `extra/` and one whose comment column moved |
| AC-14 | unit | `README.md`: only lines 174 and 175 change, each from `Programs\\av-kit\\` to `Programs\\av-kit-ui\\`; `av-kit.exe` stays; the JSON block parses; LF kept | Local Canon (D-991) | `--selftest`: a README whose JSON no longer parses is refused |
| AC-15 | integration | `capture-interactive.test.ts`: only line 14 changes (§Live fixes); then `npm --prefix ui run test -- tests/unit/capture-interactive.test.ts` passes, with every test of §UI test assertions run and none skipped | Local Canon (D-992); the named assertions | The vitest receipt must show the file's test count passed and `0 skipped` (or no skip line) |
| AC-16 | integration | `dev-spawn.test.ts`: only lines 8, 76, 77, 88 and 89 change; then `npm --prefix ui run test -- tests/unit/dev-spawn.test.ts` passes, with no test skipped | Local Canon (D-992); the named assertions | as AC-15 |
| AC-17 | unit | Register scrub: in `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` only `root_cause` and `notes` change, each by `HOME_RE` → `~`; the parsed difference is exactly those two fields; LF kept | Human-approved (D-817) | `issue-resolve.py` refuses a `--scrub` field with no match, and any other difference |
| AC-18 | integration | `INSTALL-FOLDER-NAME-MISMATCH` (row 7) and `TRACKED-FILES-HOLD-HOME-PATH` (row 10) are `resolved` with `verification` and `resolution_path` filled, each call bound to the hash before it; after each, `issue_triage.py render` and `render --check` exit 0 | Local Canon (D-994) | `render --check` fails if `known-issues.md` was not regenerated; a stale `--expect-sha256` is refused |
| AC-19 | unit | `commands.md`: exactly one line is added, the D6 row of §The D6 row, directly after the `task-contract` row; every line keeps CRLF; `test_framework_adoption.py` and `test_hdp_expert_pass.py` pass | Local Canon (D-988) | `edit-check.py --selftest`: a removed line and an LF line are refused |
| AC-20 | integration | Repo Green (row 9): `CHECK` exits 0 with `ok files=<n> allowlisted=<m> nul=<k>`, `m` = the size of `EVIDENCE_SET`. Because `CHECK` exempts a listed file only on a digest match, this exit 0, and the gate's at H1-2 and H2-4, also proves every `EVIDENCE_SET` file unchanged since row 0; and `CHECK --allowlist <empty file>` exits 1 with a `found` set whose files equal `EVIDENCE_SET`, so the pass is not vacuous | Human-approved (D-817) | The empty-list run is the negative |
| AC-21 | integration | The session gate (H1-2): its `home-path` step exits 0, and its `inventory-check` step finds `ALLOW`'s SHA-256 equal to `allowlist.sha256` from row 3, so no entry was added after row 3. H2-4 repeats both after the review, reflection and metrics exist | Human-approved (D-817) | A changed `ALLOW` fails `inventory-check`; a review file holding the path fails H2-4 (S7) |
| AC-22 | integration | Encodings (R1-F2). A file outside the allow-list that holds `C:\Users\fixture\a` on line 3 is `found` at `:3` when it is UTF-8 with a mark, UTF-16LE with a mark, UTF-16BE with a mark, UTF-32LE with a mark, UTF-16LE without a mark, and UTF-32BE without a mark, each in an LF and a CRLF variant. Round 2's fixture, the three lines `日本語の記録`, `second` and `C:/Users/fixture/a`, written as unmarked UTF-16LE and as unmarked UTF-16BE, each in an LF and a CRLF variant, is `found` at `:3` and exits 1. A file that starts with the PNG signature and holds NUL bytes but no path exits 0, and the `ok` line shows `nul=1`; the same file with the path in ASCII after its fourth `\n` is `found` at `:4`. A UTF-16 file of odd length and one with an unpaired surrogate give no traceback. stdout and stderr hold neither `Users` nor `fixture` | Human-approved (D-817: fail when a file holds the path); Local Canon (D-988, the decoding); the encoding half of AC-1 | The UTF-16 and UTF-32 cases are the negative oracle: a byte-only reader passes each of them (round 1's probe), and a reader that calls a NUL file binary by a byte-lane threshold passes round 2's fixture (round 2's probe), so each must give `found`. The PNG file with no path is the guard against a false `found`. `red-check.py` requires `test_ac_22` to fail by assertion before `CHECK` exists |
| AC-23 | integration | Digest binding (R1-F1). With an allow-list naming an evidence fixture and its `DIGEST`: unchanged, the fixture is exempt (exit 0); with a second instance appended, it gives `changed <path>` and exit 1; with one byte changed elsewhere (the path kept), it gives `changed` and exit 1; with its CRLF endings changed to LF, it is still exempt; with every instance removed, it gives `stale` and exit 1. `--prune` then deletes exactly that entry, keeps the header and every other line byte for byte, and exits 0. `--prune` on the `changed` case leaves the allow-list byte-identical and exits 1. Each case compares the allow-list's bytes before and after; only `--prune` on a stale entry changes them | Human-approved (D-817: evidence kept byte for byte); Local Canon (D-997) | The appended and the byte-edit cases are the negatives: an exit 0, a `found` line for the listed file, or a line's text in the output fails the test |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| What is done about the home path | Human-approved | D-817, ruled A |
| Which install folder the docs name | Local Canon | D-811 (triage), applied |
| Where the check runs and what it scans | Local Canon | D-988 |
| Evidence files written after today's count | Local Canon | D-989 (brief, handed over) |
| Which round-trip script changes | Local Canon | D-990 (brief, handed over) |
| The README's MCP config | Local Canon | D-991 (brief, handed over) |
| The `resources/extra/` level in the layout | Local Canon | D-996 |
| How an allow-list entry binds its file, and how an entry leaves | Local Canon | D-997 |
| Which encodings are scanned, and where the user name ends | Local Canon | D-988 (§The check, steps 2a and 3) |
| The replacement text | Local Canon | D-992 |
| A live file beyond the six | Local Canon | D-993 |
| How the register changes | Local Canon | D-994 |
| Gate coverage, loops and receipts | Local Canon | D-995 |
| How a POSIX home is matched | Research-backed | POSIX paths are case-sensitive (AC-7) |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `tools/check_home_path.py` | new | The check (LF) |
| `tools/home_path_allowlist.txt` | new | `EVIDENCE_SET` by digest and name (LF) |
| `tests/tooling/test_check_home_path.py` | new | AC-1 to AC-7, AC-22 and AC-23 (LF) |
| `.agent/skills/git-workflow/SKILL.md` | modify | One path on one line; stays CRLF |
| `_inspiration/capture-crop/design.md` | modify | One path; stays LF |
| `docs/build-plan/06-gui.md` | modify | Two paths, widths kept; stays CRLF |
| `docs/build-plan/07-distribution.md` | modify | `Programs/av-kit-ui` on line 40; the layout block without `extra/` (lines 43-49); stays CRLF |
| `README.md` | modify | `Programs\\av-kit-ui\\` on lines 174-175; stays LF |
| `ui/tests/unit/capture-interactive.test.ts` | modify | One fixture constant; stays LF |
| `ui/tests/unit/dev-spawn.test.ts` | modify | Five fixture values; stays LF |
| `.agent/context/known-issues.yaml` | modify | Two scrubbed fields, two issues resolved; stays LF (through `issue-resolve.py`) |
| `.agent/context/known-issues.md` | regenerate | `issue_triage.py render` |
| `.agent/docs/commands.md` | modify | One D6 row; stays CRLF |

### Project files

- **Plan-local scripts**, all in this plan folder: `baseline.ps1`, `red-check.py`, `identity.py`, `scope-check.py`, `inventory.py`, `edit-check.py`, `issue-resolve.py`, `session-gate.ps1`.
  - `red-check.py`, `identity.py` and `scope-check.py` are copied from `2026-11-15-framework-small-syncs`, with this plan's `PLAN`, prefix and `PROJECT_ARTIFACTS`; `issue-resolve.py` from `2026-11-15-closeout-record-once` (§The register).
  - **Copy hazard.** Some peer scripts carry the home folder's full path in an ECN-2 comment (`2026-11-05-closeout-register-grammar` `baseline.ps1` and `session-gate.ps1`; `2026-11-14-review-limits-no-token-budget/baseline.ps1`; `2026-11-04-rc2-fetch-uninstall` `baseline.ps1` and `session-gate.ps1`). Copy only from the two peers named above, write the comment as "keep pytest's temp dirs away from the home folder", and never copy a line that names the home folder. The session gate's `home-path` step catches a slip.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`. Row 3 adds `allowlist.sha256`, and row 7 `register-row7.sha256`.
- **Scratch (never tracked):** `C:/Temp/av-kit/dph/base/`, `inventory-0.json` and `inventory.json`. They hold paths, line numbers and digests only, never line text.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the handoff, the rolling reviews and the reflection.

### `inventory.py`

`inventory.py` has its own pattern builder and decoder, written apart from `CHECK`'s with the same rules (§The check, steps 2a and 3), so the cross-check compares two implementations.

- With no flag it writes `C:/Temp/av-kit/dph/inventory.json`: every `(path, line)` instance in the files `git ls-files -z --cached --others --exclude-standard` lists outside the hub, each with its kind (`handoff`, `digest`, `plan-folder`, `reflection`, `own` or `live`) and its file's `DIGEST`. `own` is checked first: `PLAN/**` and `.agent/context/handoffs/2026-11-15-docs-path-hygiene-*`. An `own` instance makes every mode fail with S7, and an `own` file is never written to `ALLOW`. It prints counts by kind and the live pairs.
- `--baseline` writes the same to `inventory-0.json` (row 0), and fails (S2) if a `live` file is a test, source, config or script outside the six of §Live fixes, or holds a pair the table does not name. A live doc beyond them is printed for D-993.
- `--write-allowlist` writes `ALLOW`: the header, then one `<digest>  <path>` line per `EVIDENCE_SET` file, sorted by path, LF. Each digest is the one `inventory-0.json` recorded at row 0; a file whose current `DIGEST` differs fails the row (S4), and nothing is written.
- `--check-allowlist --cross-check` checks AC-8, including each entry's digest against `inventory-0.json`. Once `allowlist.sha256` exists, it also checks `ALLOW`'s SHA-256 against it (AC-21).
- `--expect-live <receipt>` checks AC-9, and `--expect-evidence <receipt>` checks AC-20's empty-list run.
- `--selftest` runs AC-8's negatives on fixtures.

### `edit-check.py`

`edit-check.py --group docs|tests|register|commands` compares each file of its group to `BASE(path)`. It checks that:

- only the named lines change, found by content;
- each old line matches `HOME_RE` (or the `Programs` text, for AC-13 and AC-14, or the `extra/` layout block, for AC-13);
- each new line equals §Live fixes' text;
- every line keeps its ending;
- the 06-gui widths and the README JSON hold;
- `commands.md` is add-only by one row.

The `register` group is different, because resolving an issue changes many lines. It checks that `known-issues.yaml` is still LF throughout, that no line of it matches `HOME_RE`, and that the parsed difference from `BASE` is exactly the fields of §The register that the rows so far have changed: `--stage 7` expects the scrub and `INSTALL-FOLDER-NAME-MISMATCH`, `--stage 10` adds `TRACKED-FILES-HOLD-HOME-PATH`; nothing else may differ. The groups are `docs` (AC-10 to AC-14), `tests` (AC-15, AC-16), `register` (AC-17, AC-18) and `commands` (AC-19).

`--selftest` runs the negatives of AC-10 to AC-14 and AC-19 on fixtures.

### Sibling overlap

The plan binds each shared file to its row-0 content (`baseline-scope.json`), not to `HEAD`, and changes only its own lines.

| File | Siblings | Rule |
|---|---|---|
| `.agent/skills/git-workflow/SKILL.md` | Session 87 adds lines (the transcript line moved from 150 to 153) | Bound by content; S5 if the line is absent |
| `ui/tests/unit/dev-spawn.test.ts` | Session 82 (`ready-handshake`) changes `confirmReadyAndPublish`, which this file tests | Bound by content. If Session 82 added a line holding the path, row 0 finds it and stops on S2 |
| `tests/tooling/` | Session 76 only (grouping `:124`) | This plan adds one new file there and edits none; Session 76 runs first |
| `.agent/context/known-issues.yaml`, `known-issues.md` | Sessions 75 to 82 close their own issues | Grouping `:125`: they run before this session. Row 7 changes only the fields of §The register, bound to the row-0 hash (S4) |
| `docs/build-plan/06-gui.md` | Sessions 80 and 81 may add notes | Grouping `:125`; bound by content |
| `tools/issue_triage*` | Session 79 changes the triage tool | This plan only runs `render`; a changed render shows in `render --check` (S8) |
| `.agent/docs/commands.md` | Session 86 (earlier) | One add-only row after `task-contract` |
| Evidence files of Sessions 75 to 82 | Each writes its own handoff, reviews, plan folder and reflection | They run before this session, in number order (grouping `:244`), so each file exists by row 0. Row 0 and row 3 put any that holds the path into `ALLOW` by name (D-989). A file that appears later is outside `baseline-dirty.txt` (S4) and fails the gate's `home-path` step |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Renaming the package to get `Programs/av-kit` | out-of-scope | — | D-811 |
| The two older round-trip scripts (`2026-11-03-release-rc1`, `2026-11-04-rc2-fetch-uninstall`) and every handoff that cites `Programs\av-kit` | out-of-scope | — | D-990; D-817 (evidence byte for byte) |
| Rewriting any evidence file, or scrubbing the history | out-of-scope | — | D-817 (B lost) |
| `triage-output.yaml:3102` | out-of-scope | — | Generated by `issue_triage.py triage`; it changes when triage next runs |
| `ui/tests/unit/login-item.test.ts:3` (`Programs\av-kit\av-kit.exe` with user `avkit`) | out-of-scope | — | A fixture for the login-item path logic, not a doc of the install folder; no assertion is about the folder name |
| Running `CHECK` in CI or in `agent-commit.ps1` | out-of-scope | — | D-988 |
| The limits of `HOME_RE` that round 2 listed without blocking: a percent-encoded separator (`%5C`, `%2F`) is not decoded; a user name that holds whitespace or an apostrophe ends there, so a longer name such as `fixture other` matches as the home; a non-ASCII home segment is missed in a cp1252 or Latin-1 file | out-of-scope | — | D-988 (how it can fail) |
| The short form `~` in Console output | out-of-scope | — | Session 77 (MEU-148) |

## BUILD_PLAN.md Audit

This project adds no build-plan section and changes no MEU, so `docs/BUILD_PLAN.md` and `meu-status.yaml` do not change. It edits two build-plan files (`06-gui.md`, two lines; `07-distribution.md`, line 40 and the layout block) that no generator reads. H1-3 proves the render is consistent:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/dph/dph-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/dph/dph-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. **Tree state.** It records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`.
2. **Path-scoped baseline.**
   - It writes `baseline-scope.json`: for each path in §Files Modified, its SHA-256, or `absent`. The three new files must be `absent`.
   - It writes `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope (or `deleted`), keyed by its repository-relative POSIX path. H1-4 reads it (R1-F4).
   - It copies every existing file of §Files Modified to `C:/Temp/av-kit/dph/base/`.
3. **Line endings.** It measures each edited file with Python bytes and fails if one differs from §Live fixes' EOL column (S5).
4. **Inventory.** It writes the plan-local scripts (§Project files), runs `inventory.py --baseline` (S2 on a live test, source, config or script beyond the six), and prints the counts by kind. A count that differs from the plan's 60 evidence files and 12 live lines is reported in the handoff, with each extra file's kind.
5. **Anchors.** Each line of §Live fixes is found by content, and the `| task-contract |` row exists (S5 otherwise).
6. **Base receipts.** `uv sync --frozen --all-packages`; the base Python suite (`dph-base-py.txt`) with `TMP` and `TEMP` at `C:\Temp\av-kit\dph\tmp`; and the two vitest files (`dph-base-ui.txt`), which must pass at base (S6).
7. **Selftests.** `red-check.py`, `inventory.py` and `edit-check.py` selftests.

If any step fails, the row fails and nothing else runs.

### 2. Red, then Green (rows 1 and 2)

- **The Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require test_ac_1 … --require test_ac_7 --require test_ac_22 --require test_ac_23` checks that.
- **New code fails by assertion.** Each test asserts `CHECK.is_file()` first.
- **Expectations stay immutable in Green.**

### 3. Repo checks (rows 3, 4, 9 and 10)

- Row 3 writes `ALLOW` and checks AC-8. It writes `allowlist.sha256`.
- Row 4 runs `CHECK` on the repo before any fix: exit 1, and the `found` set equals `LIVE_SET` (AC-9).
- Row 9 runs it after every fix: exit 0 (AC-20), then with an empty allow-list in `C:/Temp/av-kit/dph/empty-allowlist.txt`, whose `found` files must equal `EVIDENCE_SET`. Row 10 then resolves `TRACKED-FILES-HOLD-HOME-PATH` (§The register), renders, and runs `CHECK` once more.

### Session gate (H1-2)

`session-gate.ps1` follows the shape of `2026-11-15-framework-small-syncs/session-gate.ps1`:

- one receipt per step in `C:/Temp/av-kit/dph/`, named `dph-D6-<step>`;
- fail-fast, with later steps printed as `not_run`;
- the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `tools-lint` (`ruff check tools/check_home_path.py tests/tooling/test_check_home_path.py`); `py-lint` (`ruff check packages/ tests/`); `task-contract`; `scope-paths` (`scope-check.py`); `home-path` (`uv run python tools/check_home_path.py`, the new D6 row); `inventory-check` (`inventory.py --check-allowlist --cross-check`); `edit-check` (all four groups); `red-check-selftest`; `ui-types`; `ui-lint` |
| Targeted | `home-path-tests` (`pytest tests/tooling/test_check_home_path.py -rs`, no skip allowed); `ui-targeted` (`npm --prefix ui run test -- tests/unit/dev-spawn.test.ts tests/unit/capture-interactive.test.ts`); `adoption-tests` (`pytest tests/tooling/test_framework_adoption.py tests/tooling/test_hdp_expert_pass.py`) |
| Fresh full | `py-tests` (the full suite); `ui-tests` (the full Vitest suite); `state-render`; `issues-render` (`issue_triage.py render --check`); `closeout-selftest` |
| Skipped, with reason | `py-types`: nothing under `packages/` changes. `ui-build` and `ui-electron`: only two unit-test files change under `ui/`, no source. `mcp-*`: no MCP change. `openapi`: this session changes nothing under `packages/api` (H1-4: each path there that differs from `baseline.sha` still holds the content row 0 recorded, so an earlier session's uncommitted edit is not counted as this session's). `build-record`: no build |

`py-tests` and `ui-tests` excuse only ids that row 0's receipts show failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a live test, source, config or script file holding the path beyond §Live fixes (a live doc is fixed instead, D-993) | Stop; bring the file and the line number (not the text) to Mat |
| S3 | A Red receipt fails `red-check.py` | Fix the test setup; do not move to Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path changes content during the session | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | A named anchor is absent, or a file's line endings differ from §Live fixes | Stop; a sibling moved the text. Re-plan that line |
| S6 | Either vitest file fails at base | Stop; the failure predates this session |
| S7 | A review file, or any other artifact of this session (this plan's folder, a `2026-11-15-docs-path-hygiene-*` handoff or review, the reflection), holds the path; `inventory.py` reports such a hit as `own` | Never edit a reviewer's file. Stop and ask Mat; an artifact the agent wrote is rewritten with `~` before H1-6b |
| S8 | `issue_triage.py render --check` fails after row 7 | Stop; check Session 79's change to the render |
| S9 | Codex is unavailable or the ledger refuses a round | Mat |

## Decision Log

> [!NOTE]
> D-988 and D-992 to D-997 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. D-989, D-990 and D-991 failed §4 test 1 (convergence) and are written as Briefs below: D-989 and D-990 are source conflicts (M-6), and D-991 has no M hit. Mat handed this set to the agent on 2026-11-15, so each is recorded `resolution: autonomous` with the agent's own tag and its `mandatory:` list; none hits an item that stays Mat's. D-817 (Mat's ruling) and D-811 (triage) are applied here, not re-recorded. The grouping rows D-813, D-815, D-816 and D-817 stay in the grouping file's §8 and are not copied here; H2-2 reads them through `--decision-source` on the grouping file (this plan's `grouping_source`), and D-811 through `--decision-issue INSTALL-FOLDER-NAME-MISMATCH`. The grouping's old "Carry-forward" wording (`:325-329`, "each row appears in its consuming session's reflection") is ignored under the new HDP §6: the reflection's `### Decisions Log` lists only this session's reversible autonomous choices. D-997 was added after Codex plan review round 1 (R1-F1), and the same round refined D-988 (R1-F2, R1-F3); both passed the §4a list and the §4 test. D-998 is left free for execution.

```yaml
decision_log:
  - id: D-988
    stage: planning
    question: "Where does the home-path check run, and what does it scan?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A new standard-library tool, tools/check_home_path.py, run by a new D6 row (home-path) in every session's gate and by this session's gate; it scans tracked and untracked (not ignored) files outside .agent/fleet/hub, decodes each file (UTF-8 with or without a byte-order mark, UTF-16 and UTF-32 with a mark) and reads a file that holds a NUL byte and has no mark in five views (raw UTF-8, UTF-16LE, UTF-16BE, UTF-32LE, UTF-32BE), skipping no file, matches the home only where the user name ends (a separator, a character Windows forbids in a name, whitespace, a quote, the end of the line, or closing punctuation before one of those), exempts an allow-listed file only while its content digest matches (D-997), fails on a stale entry, and prints path:line only. It is not added to CI or to agent-commit.ps1."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:299 — D-817 A: a check, run by the gate, with evidence allow-listed by name"
      - "tools/check_commit_identity.py — the style of a gate tool that never echoes what it found"
      - ".agent/docs/commands.md:194-211 — the D6 table is where a gate step is defined"
      - "C:/Temp/av-kit/dph-plan-review-round-1.md — R1-F2 (UTF-16 missed) and R1-F3 (longer user names matched)"
      - "C:/Temp/av-kit/dph-plan-review-round-2.md — R2-F1 (a byte-lane threshold skips mixed-language UTF-16)"
    research: { engine: none, sources: [] }
    reasoning: "Mat's ruling names a check run by the gate; the D6 table is where every session's gate takes its steps, so one row there applies the ruling everywhere. Untracked files are scanned because a session's new files are untracked when its gate runs. A stale entry fails so the list cannot keep a name that no longer needs it. CI lost because the runner's home differs and the check would pass vacuously. agent-commit.ps1 lost because the gate runs before every commit already, and editing the commit script widens this session. Printing the text lost because a receipt would then hold the path. Codex plan review round 1 found that a byte pattern misses UTF-16 text and matches a longer user name; decoding and the name boundary fix both, and on 2026-11-15 the decoded rule found the same 130 lines in 66 files, with no UTF-16 file and no binary file holding the path. Round 2 found that calling a NUL file binary by a byte-lane threshold skipped valid mixed-language UTF-16. Reading every file that holds a NUL and has no mark in all five views cannot skip text, and a binary file that holds the path is an exposure too, so a hit there is not a false positive; on 2026-11-15 none of the 31 such files holds the path in any view. A threshold or a strict-decode test lost because each still lets some text file go unread; skipping binary files lost for the same reason. How it can fail: a percent-encoded separator is not decoded; a user name that holds whitespace or an apostrophe ends there, so a longer name such as 'fixture other' matches as the home; a non-ASCII home segment is missed in a cp1252 or Latin-1 file. Each is out of scope. Two-way: one row and one file."
  - id: D-989
    stage: planning
    question: "What happens to evidence files written after today's count that hold the path?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6]
    chosen: "A: allow-list them by name when their kind is evidence (handoff, review, digest, reflection, plan-folder file) and they are not this session's own files, and list them in the handoff. This plan's folder and the 2026-11-15-docs-path-hygiene-* handoff and review files are never allow-listed; a hit there is S7."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:299 — D-817 A: today's evidence files allow-listed, evidence byte for byte"
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:310,317 — Mat's 2026-11-07 ruling that Session 52's files are committed as they are"
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:244 — Sessions 75 to 83 run in number order"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this set, so the recommendation is chosen. The ruling's two parts pull apart for a file written between the count and this session: 'today's evidence files' could leave it out, but 'evidence stays byte-for-byte' forbids scrubbing it. All of Sessions 75 to 82 run on 2026-11-15, before this one and in number order (grouping :244), so their files are today's evidence and exist by row 0; a file that appeared after row 3 would be outside baseline-dirty.txt (S4) and would fail the gate's home-path step. This session's own plan folder, handoff and reviews are excluded: allow-listing them would let this session's own slip pass silently, and S7 already says what happens then (expert pass, 2026-11-15). Scrubbing lost because those files are bound by their own reviews and hashes. Stopping to ask lost because the answer follows from the byte-for-byte rule. Two-way: an entry is removed in one edit."
  - id: D-990
    stage: planning
    question: "Which install round-trip script changes for the install folder?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6]
    chosen: "A: none. The rc.2 script already names Programs/av-kit-ui and refuses both folders; the rc.1 and rc2-fetch-uninstall scripts are finished sessions' evidence and keep their bytes; the issue's resolution names the rc.2 script."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-08-release-rc2/install-roundtrip.ps1:6,55-58 — the newest script names av-kit-ui and refuses both folders"
      - ".agent/context/known-issues.yaml:4142 — D-811: the docs and the release round-trip script name Programs/av-kit-ui"
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:299 — D-817: evidence stays byte for byte"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this set, so the recommendation is chosen. D-811 (written by the 2026-11-15 triage, grouping :6 and :12, about an issue found on 2026-11-04, known-issues.yaml:4123) asks for the release round-trip script to name Programs/av-kit-ui; the rc.2 session's script, written on 2026-11-08, already names it and refuses both folders (install-roundtrip.ps1:6, :55-58). Editing the two older scripts lost because they are plan-folder evidence, which Mat's D-817 keeps byte for byte, and handoffs cite them as run. Leaving the issue open for the script lost because nothing is left to fix. Two-way."
  - id: D-991
    stage: planning
    question: "Does the README's hand-written MCP config get the real install folder too?"
    resolution: autonomous
    class: source-conflict
    mandatory: none
    chosen: "A: yes. README.md:174-175 change Programs/av-kit to Programs/av-kit-ui in both paths; av-kit.exe stays."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:4142 — D-811: correct the docs, keep the package name"
      - ".agent/context/known-issues.yaml:4125 — the release notes were corrected the same way (d287c55)"
      - "ui/package.json:2 — name av-kit-ui, which names the per-user install folder"
      - ".agent/docs/human-decision-protocol.md:155 — M-4 lists the public repo's docs as an example of a one-way door"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this set, so the recommendation is chosen. The README is the one place a user copies the folder name from, and today it points at a folder the installer never makes, so a hand-written config fails. It fails section 4 test 1: D-811's chosen text names 07-distribution.md and the release round-trip script, not the README, so no recorded decision has settled the README itself. M-4 is not hit. Its heading is one-way doors, and it lists 'the public repo's docs' as an example of one; this edit is not one-way, because the old folder never existed on any install (known-issues.yaml:4125, measured on rc.1), so no user's working setup depends on it, and one edit undoes it. M-6 is not hit either: local canon (D-811 and the rc.1 measurement) settles which folder is right. The edit reaches the public repository only on a push, which stays Mat's (M-1, M-12). Leaving it lost because it keeps a broken instruction in front of users; widening D-811 to every handoff lost under D-817."
  - id: D-992
    stage: planning
    question: "What text replaces the home folder on each live line?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "~ in prose and docs (SKILL.md, 06-gui.md, known-issues.yaml), C:/Users/YOU in the inspiration example (as README.md does), C:/Users/avkit in the two UI test fixtures (as login-item.test.ts does); 06-gui.md fields keep their width"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/06-gui.md:989 — the sibling field already writes ~/"
      - "README.md:165 — the user-facing example writes YOU"
      - "ui/tests/unit/login-item.test.ts:3 — a test fixture with user avkit"
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:323 — a later session writes ~ or the home folder"
    research: { engine: none, sources: [] }
    reasoning: "Each form follows the nearest sibling in the same kind of file. The tests need an absolute Windows-shaped path to keep their semantics, so ~ lost there. Removing the lines lost because each carries meaning for its reader."
  - id: D-993
    stage: planning
    question: "What happens if row 0 finds a live file holding the path beyond the six?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A doc or prose file is fixed by D-992's rules and added to the row-5 edits; a test, source, config or script file stops the session (S2)."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:299 — D-817 A: the live files are fixed"
      - ".agent/docs/human-decision-protocol.md §4a M-7 — a test's assertion changes only under a named row"
    research: { engine: none, sources: [] }
    reasoning: "Fixing a live doc applies D-817 directly. A new test or source line would change behaviour or an assertion that no row names, so it is Mat's under M-7. Allow-listing a live file lost because D-817 allow-lists evidence only."
  - id: D-994
    stage: planning
    question: "How does the register change?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Through a plan-local issue-resolve.py with a --scrub mode: scrub root_cause and notes of CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR, and resolve INSTALL-FOLDER-NAME-MISMATCH and TRACKED-FILES-HOLD-HOME-PATH; then render and render --check"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-closeout-record-once/issue-resolve.py — the register edit through the triage model, bound to a hash"
      - "docs/execution/plans/2026-11-15-closeout-record-once/task.md:57 — resolve, render, render --check"
    research: { engine: none, sources: [] }
    reasoning: "issue_triage.py has no resolve or edit command, and the brief forbids hand edits, so the peers' plan-local tool on the triage model is the repo path. The scrub needs its own mode because RESOLVE_KEYS does not include root_cause or notes; importing CHECK's pattern keeps one definition. Leaving the resolved issue's text lost because D-817 names known-issues.yaml as a live file."
  - id: D-995
    stage: planning
    question: "What does the session gate cover, and how are loops and receipts named?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "§Session gate's steps; receipts under C:/Temp/av-kit/dph named dph-*; loops dph-plan- and dph-execution-2026-11-15-docs-path-hygiene; baselines path-scoped and bound to content"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-framework-small-syncs/implementation-plan.md §Session gate — the shape for a tooling session"
      - ".agent/docs/commands.md:194-211 — the D6 stages"
    research: { engine: none, sources: [] }
    reasoning: "One Python tool, one test file and two UI test files change, so the Python and UI tests and lint run; types, build, Electron, MCP and OpenAPI have nothing to check. Content-bound baselines keep the earlier sessions' uncommitted work safe."
  - id: D-996
    stage: planning
    question: "Does the install layout in 07-distribution.md lose its resources/extra/ level?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Yes. Lines 43-49 lose the extra/ line, and avkit-backend/, ffmpeg/ and mcp-server/ move up one level under resources/, with their comments in the same column; the other extraResources entries stay unlisted."
    source_tag: Local Canon
    precedents:
      - "ui/electron-builder.yml:32-35,52-53 — to: avkit-backend, to: ffmpeg, to: mcp-server, with no extra/ folder"
      - "ui/src/main/mcp-setup-prompt.ts:35 — the packaged server path is resourcesPath/mcp-server/index.mjs"
      - "docs/build-plan/07-distribution.md:194,314 — the same file's extraResources table and packaging row name resources/mcp-server"
      - "tests/unit/test_packaging_installer.py:40 — the build config must not hold extra/avkit-backend"
    research: { engine: none, sources: [] }
    reasoning: "Found by the expert pass on 2026-11-15 and checked against the files. The layout serves the goal anchor (the docs name the folders the installer really uses), and the plan is not approved yet, so widening it is a planning choice, not an M-8 hit. Every source agrees there is no extra/ folder. Listing deno/, region-picker/ and the icons lost because the block was never complete and the table at :194 names them; leaving extra/ lost because a reader following the layout looks in a folder that does not exist. Two-way: one block in one doc."
  - id: D-997
    stage: planning
    question: "How does an allow-list entry bind the evidence file it exempts, and how does an entry leave the list?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Each entry is a content digest and a path: the SHA-256 of the file's bytes with CRLF read as LF, recorded at row 0 and written at row 3. CHECK exempts a listed file only while the digest matches; a changed file that still holds the path prints changed and fails, and one that no longer holds it is stale. CHECK --prune deletes missing and stale entries and nothing else. No tool or person writes a new digest for an entry: that is a new entry, which needs an HDP decision."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:299 — D-817 A: evidence kept byte for byte"
      - "C:/Temp/av-kit/dph-plan-review-round-1.md — R1-F1: a name-only entry exempts any later content at that path"
      - ".gitattributes:2 — text=auto, so a file's line endings in the working tree depend on the clone"
    research: { engine: none, sources: [] }
    reasoning: "Mat's ruling keeps evidence byte for byte, and a name-only entry would let a later session append the path to an evidence file unseen; a digest makes that fail in every later gate, not only in this session. Hashing the raw bytes lost because text=auto lets another clone check a file out with other line endings, which would fail a file that did not change; reading CRLF as LF keeps every other byte bound. A check that only this session runs (inventory.py) lost because the exposure would come from a later session. Letting CHECK or --prune write a new digest lost because that would admit an appended path silently; pruning only removes entries, so the list can only get tighter without a decision. Two-way: one file format in a new tool, undone by one edit."
```

Expert pass (fresh context): 3 briefs. Holds: none. Changed: D-989, D-990, D-991. Not adopted: none. Receipt: `C:/Temp/av-kit/docs-path-hygiene/dph-expert-pass.txt`.

### D-989: What happens to evidence files written after today's count that hold the home folder's path?

Expert pass: changed from "allow-list every evidence-kind file": that would have allow-listed this session's own plan folder and reviews without a word; they are now excluded, and a hit there is S7.

**I recommend A: list them by name in the allow-list, as today's evidence files are, and name them in the handoff.** Your ruling keeps evidence byte for byte. Every session before this one runs on the same day, and in number order, so their handoffs, reviews and plan files already exist when this session starts; they are today's evidence too. This session's own plan folder, handoff and reviews are never listed: if one of them holds the path, the session stops (S7). A can fail if a session wrote the path into a file that is not evidence; that file is fixed or stops the session instead (D-993). Undo: delete one line from the list.

- B: rewrite those files with `~`. The tree holds fewer instances, but it breaks the bytes their own reviews and hashes bind to.
- C: keep things as they are: stop at row 0 and ask you about each file. Nothing is decided without you, but the session waits on a question your ruling already answers.

Refs: D-817 (grouping `:299`, `:310`, `:317`), the queue order (grouping `:244`), D-993, S7, M-6.

### D-990: Which install round-trip script changes?

Expert pass: changed from the reasoning that D-811 was written on 2026-11-04: the 2026-11-15 triage wrote it, and only the issue dates from 2026-11-04. A holds.

**I recommend A: none.** The newest script (rc.2) already names `Programs\av-kit-ui` and refuses both folders. The two older scripts were run and reviewed by finished sessions, and your ruling keeps such files byte for byte. A can fail if someone reruns an old script; it would check the wrong folder, as it does today. Undo: edit two lines.

- B: change the default in the rc.1 script (`:33`) and the rc2-fetch-uninstall script (`:48`). The old scripts would be right, but their bytes would no longer match what their handoffs recorded.
- C: keep things as they are and leave the script part of the issue open. The issue stays open for a fix that already exists.

Refs: `docs/execution/plans/2026-11-08-release-rc2/install-roundtrip.ps1:6,55-58`, D-811 (`known-issues.yaml:4142`; written by the 2026-11-15 triage, grouping `:6`, `:12`), D-817, M-6.

### D-991: Does the README's hand-written MCP config get the real install folder?

Expert pass: changed from "M-4 is not hit because the installer's folder does not change": that did not answer M-4's own wording. The record now names the §4 test this brief fails (test 1). A holds.

**I recommend A: yes, change both paths to `Programs\av-kit-ui`.** Today a user who copies that config points their assistant at a folder the installer never makes, so the tools do not start. The fix makes the README match the installer, as the release notes already do. It needs a brief because your install-folder decision (D-811) names the build-plan doc and the script, not the README. The protocol lists "the public repo's docs" as an example of a one-way door, but this edit is not one: the old folder never existed on any install, so no working setup depends on it, and one edit undoes it. A can fail only if a later build renames the package; then the README changes back. It reaches the public repository only when you push.

- B: leave the README for a later session. Smaller scope, but the broken instruction stays on the page most users read first.
- C: keep things as they are. Same as B, with no follow-up.

Refs: `README.md:174-175`, `ui/package.json:2`, `known-issues.yaml:4125`, D-811, d287c55, M-4 (`human-decision-protocol.md:155`; not hit: not one-way), M-1, M-12.

## Research References

- electron-builder's install folder naming: `ui/node_modules/app-builder-lib/out/targets/nsis/NsisTarget.js:270` and `out/targets/targetUtil.js:40-42`, as cited in `INSTALL-FOLDER-NAME-MISMATCH` (`known-issues.yaml:4124`). Primary.
- Measured install folder on v0.1.0-rc.1, 2026-11-04 (`known-issues.yaml:4125`).
- git `ls-files --others --exclude-standard`: untracked files minus the ignore rules (git-ls-files docs).
- Python `pathlib.PureWindowsPath` and `PurePosixPath`: parse a path of either form on any OS.

## Planning receipts

All of these are under `C:/Temp/av-kit/docs-path-hygiene/`. Every probe was read-only with respect to the repository, and none of the receipts is tracked.

- **`plan-grep-wide.txt`, `plan-grep-wide-files.txt`, `plan-grep-lines.txt`, `plan-grep-files.txt`:** the byte-level scan of the tracked tree, outside the hub: 130 lines in 66 files.
- **`plan-classify.txt`:** 16 handoffs, 14 digests, 30 plan-folder files, 6 live files (12 lines).
- **`plan-live-lines.txt`:** the 12 live lines with the home folder masked, their lengths and line endings.
- **`plan-eol.txt`:** line endings by Python bytes for every file this plan edits.
- **`plan-programs-live.txt`:** the live lines that name `Programs/av-kit` without `-ui`.
- **`plan-triage-help.txt`:** `issue_triage.py --help`; there is no resolve or edit command.
- **Not run at plan time:** any test suite, any edit, `CHECK` (it does not exist yet).

## Validation stage contract

- **Static:** `tools-lint`, `py-lint`, `task-contract`, `scope-paths`, `home-path`, `inventory-check`, `edit-check`, `red-check-selftest`, `ui-types`, `ui-lint`.
- **Targeted:** the new test file (no skips), the two UI test files and the adoption tests.
- **Fresh full:** `py-tests`, `ui-tests`, `state-render`, `issues-render`, `closeout-selftest`.
- **Runtime:** none; `CHECK` on the live repository is a static step.
- **Identity:** `identity.py`, independent of the receipts. It hashes `HEAD`, plus the content of the tracked diff and the untracked files, minus this session's closeout artifacts. Other sessions' uncommitted files are therefore bound by content.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
