---
project: "2026-11-05-closeout-register-grammar"
date: "2026-11-05"
source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md#session-49b--closeout-register-grammar-no-meu-closeout-check-refuses-register--p3"
grouping_source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md"
meus: []
status: "draft"
template_version: "2.2"
---

# Implementation Plan: The closeout check reads the issue register (Session 49b)

> **Project:** `2026-11-05-closeout-register-grammar`
> **Build plan:** none. This is a tooling session with no MEU (D-280). It is tracked by known issue `CLOSEOUT-CHECK-REFUSES-REGISTER` (P3), and its scope is grouping §3 Session 49b (`.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:145`).
>
> **Source requests,** Mat, 2026-11-05: "all recommendations are accpeted, proceed". That accepted D-274: a tooling session, 49b, after Session 49 and before Session 50. Mat's session brief, the same day, sets the scope used here:
> - `model.save` writes indented, unwrapped YAML.
> - The closeout check reads the register as `save` writes it.
> - `--decision-issue` becomes repeatable.
> - One reformat of the register, with every parsed value asserted equal by a script.
> - The six logs the placeholder check still refuses are reworded with the same meaning, each shown to Mat as before and after text.
>
> Done means a closing session passes `known-issues.yaml` with several `--decision-issue` flags and no extract.
> **Known issues:** `CLOSEOUT-CHECK-REFUSES-REGISTER`.
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review.
>
> Line anchors are from `main` `19001ca`. At plan time the tree holds only this plan folder, and the register's SHA-256 is `900b2cb0…` (`.agent/context/known-issues.yaml`, 328,365 B, LF, modified 2026-11-05 15:01). Only one worktree is open (`git worktree list`: `P:/av-kit 19001ca [main]`).

## Goal

**Goal anchor:** Session 49b makes the closeout check read `known-issues.yaml` exactly as `model.save` writes it, for every issue a session names, so Sessions 50 to 57 close without an extract.

Four things are wrong today:

1. **`model.save` writes a shape the closeout reader refuses** (`tools/issue_triage/model.py:345`). PyYAML's default dump writes each list at its key's indent and wraps values at 200 characters. The bounded grammar in `check_yaml_subset` (`tools/validate_closeout_artifacts.py:1039`) refuses both. Measured today: the reader refuses 66 of the register's 67 decision logs (`C:/Temp/av-kit/s49b/probe-old.txt`).
2. **`--decision-issue` keeps only its last value** (`tools/validate_closeout_artifacts.py:5555`). A session that names two issues checks one of them, and still exits 0.
3. **Fifteen fields in six decision logs hold text the placeholder test refuses.** These are braces, angle brackets and `${…}` in real decisions (`PLACEHOLDER`, `decision_entries`). They stay refused whatever the layout.
4. **Session 49 worked around all three** with an extract and one run per issue (D-272). Each of Sessions 50 to 57 would need the same workaround.

The session ends when the check passes the register, as `save` wrote it, with several `--decision-issue` flags and no extract. The proof is Session 49's own reflection check rerun against the register (AC-11). The register's parsed content changes only in the 15 reworded fields and in the records row's resolution of this issue.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-05). A headroom binary is on PATH but no payload here is oversized: the scope is two tools, one test file, one register and one protocol paragraph, read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`, with receipts under `C:/Temp/av-kit` named `s49b-*`, `RECEIPTS_DIR=C:/Temp/av-kit`, `PYTHONIOENCODING=utf-8` and `ELECTRON_RUN_AS_NODE` cleared.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`, under ledger loops `s49b-plan-2026-11-05-closeout-register-grammar` and `s49b-execution-2026-11-05-closeout-register-grammar`. Claude wrote the plan, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable or the ledger refuses a round, the fallback is Mat. Each round is metered, and the coordinator warns before dispatching.
- **Never in these rows without Mat's words:** commit, push, or author an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `CLOSEOUT-CHECK-REFUSES-REGISTER` (no MEU) | `.agent/context/handoffs/2026-11-05-closeout-register-grammar-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-05-closeout-register-grammar-plan-critical-review.md` and `.agent/context/handoffs/2026-11-05-closeout-register-grammar-implementation-critical-review.md`. The single non-MEU handoff follows `2026-09-26-framework-update-adoption`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and the done-proof's Red (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipt, `s49b-done-proof-red.txt` |
| WP-2 | Tests, the writer and the reader (rows 1 to 3) | WP-1 | shared | Test file, `model.py`, the validator, the protocol paragraph |
| WP-3 | The register rewrite and the done-proof (rows 4 to 6) | WP-2 | shared | The register, rewrite receipts, done-proof receipt |
| WP-4 | Records (row 7) | WP-3 | shared | Register status, rendered issues, grouping tracker |
| WP-5 | Closeout (H1, H2) | WP-4 | `compact_continue` | Handoff, review, reflection |

## User Review Required

> [!IMPORTANT]
> **Read the 15 rewordings in §Rewording below.** Each one replaces only a brace, angle-bracket or `${…}` span, and the meaning should not change. If any after text reads wrong to you, say which one; row 5 writes exactly the table. These texts are decision records, so the rewording is the one part of this session that changes recorded words.
>
> **Every line of the register moves once (row 4).** The diff will be large, but the parsed content stays the same: the script fails unless every parsed value is equal. Row 5 then changes the 15 fields, and row 7 resolves this issue. Any other session that edits the register while rows 4 to 7 run is S4.
>
> **The token estimate.** The grouping says to calibrate against "Session 33 `capture-chrome`", but that session's ledger loops are named `s34-*` (`s34-plan-…`, `s34-execution-…`). The figures below are that session's, whatever its number is. One review round costs about 5M to 15M tokens:
> - capture-chrome's plan review took 3 rounds and about 33M tokens (8.77M, 12.68M and 11.52M). Its execution review took about 28.8M.
> - Session 49's plan review was one round of 5.0M, and its execution review one round of 7.7M.
>
> This delta is smaller than capture-chrome's. Expect 1 or 2 plan rounds and 1 or 2 execution rounds, about 10M to 50M tokens in all.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `REGISTER` | `.agent/context/known-issues.yaml`. |
| `REWRITE` | `docs/execution/plans/2026-11-05-closeout-register-grammar/register-rewrite.py`, written at plan time and run by rows 4, 5 and 7. |
| `DONE_PROOF` | Session 49's H2-2 reflection check, with the extract replaced by `REGISTER` and the two runs replaced by one with `--decision-issue UNINSTALL-LEAVES-INSTALLER-COPY --decision-issue FFMPEG-LIBDVDCSS-BUNDLED` (the exact command is task row 6). |

### `model.save` (D-281)

`save` keeps its header line, its `newline="\n"` and its `validate_strict` call. The dump changes in four ways:

- **A dumper subclass of `yaml.SafeDumper` indents every sequence under its key.** Its `increase_indent` always passes `indentless=False`.
  - Its `expect_block_sequence` starts a sequence that is itself a sequence item on a new line under its dash. PyYAML's compact `- - alpha` form is refused by the grammar as unexpected indentation. The noncompact form passes, to any depth (`C:/Temp/av-kit/s49b/r1-writer.txt`).
  - Its `ignore_aliases` returns `True`, so an object that appears twice in the data is written out twice. With the default, the dumper writes an `&id001` anchor, which the grammar refuses (`C:/Temp/av-kit/s49b/alias.txt`).
- **A string representer chooses the style.**
  - A string holding U+0085, U+2028 or U+2029 is written double-quoted, so those characters are escaped (`\N`, `\L`, `\P`) on one line. The reader splits lines on them, and PyYAML's own choice for them is refused or loads back different.
  - A string ending in two or more newlines is written double-quoted.
  - Any other string holding a newline is written as a literal block (`|`).
  - Every other string keeps PyYAML's choice.
- **A mapping representer refuses a string key that is empty or holds a line break.** PyYAML writes those keys with the `?` key notation, which the grammar refuses. No key in the register is like that, and `save` raises `IssueTriageError` instead of writing one.
  - Residual, recorded at plan review round 2: PyYAML also uses `?` for a string key longer than 128 characters, and `validate_strict` accepts one. `save` writes it, and the closeout check would refuse that file. No register key comes near that length. The schema's keys are short. A future need for such keys extends this refusal, not the reader.
- **`save` renders the text first, then writes.** It raises `IssueTriageError`, before opening the file, unless the text loads back equal to the data. A refusal therefore leaves the file as it was.

The dump also passes `width=10**9`, so nothing wraps, and keeps `default_flow_style=False`, `allow_unicode=True` and `sort_keys=False`.

The two-newline rule exists because a keep-chomped block (`|+`) as the last value makes PyYAML emit the `...` document-end marker, and `check_yaml_subset` refuses it. PyYAML already falls back to double quotes, on one line, when a literal block can't hold the string (trailing spaces, tabs, a `\r`). The grammar passes all of these (`C:/Temp/av-kit/s49b/edge.txt`). Integer, date, boolean and null keys and values pass (round-1 review). Over today's register, the four changes write bytes identical to the round-0 prototype. `model.load` is unchanged.

`save` doesn't import the validator. The grammar property is held by AC-1 and AC-2 over the edge set, not by a runtime check, because `tools/issue_triage` stays independent of the closeout tooling.

### `--decision-issue` repeatable (D-283)

- **argparse.** The flag gets `action="append"`. Help: "issue ID whose enrichment.decision_log to read from a known-issues --decision-source; repeat it once per issue". The usage docstring at `:12` becomes `[--decision-issue ID ...]`.
- **CLI checks.** The CLI refuses a repeated ID as `Usage` (exit 2), because naming one issue twice is a mistake in the command. The two existing checks at `:2040-2065` keep their meaning for a non-empty list.
- **`decision_sources`.** It takes `issues: Sequence[str]` instead of `issue: str | None`. For a known-issues source, it reads each named issue in the order given, each under its own label `issue <ID>`, through the unchanged `issue_decision_log`. That function already refuses an issue the file doesn't hold (`:1503`).
  - `refuse_repeated_ids` runs per issue.
  - The existing stage-agreement check runs across everything read, so one decision recorded with two stages is still refused.
  - "No known-issues source" is still refused when any issue is named.
- **Signatures.** `check_decisions_log` and `check_reflection` take the list in the same way. Every caller is inside the validator (`grep`, 2026-11-05).
- **Docs.** `.agent/docs/human-decision-protocol.md:201-203` says the flag is repeated once per issue. The two `TASK-TEMPLATE.md` H2-2 rows show one flag, which is still valid, so they don't change.

### The reader stays strict (D-282)

`check_yaml_subset`, `issue_decision_log` and `PLACEHOLDER` don't change. The writer conforms to the reader, and the six refused logs are reworded.

### Register rewrite (D-284)

`REWRITE` saves the register three times, each time through the new `model.save`, in rows 4, 5 and 7. Each run works the same way:

- **One exclusive handle for the whole run.** The script opens the register with a Windows handle that lets other processes read but not write, replace or delete it. It holds that handle from the first read to the last. Another process's write in that interval fails in that process with `PermissionError`, instead of being overwritten here. If another process already has the register open for writing, the script refuses (WinError 32) and writes nothing. Plan-time probe, `C:/Temp/av-kit/s49b/r1-rewrite-probe.txt`: a writer started between the read and the save was refused, and the register held exactly the staged bytes.
- **The hash is of the bytes read through that handle.** `--expect-sha256` is required. Row 4 passes the plan-time `900b2cb0…`, row 5 the hash row 4 printed, and row 7 the hash row 5 printed. The bytes read are kept as `C:/Temp/av-kit/s49b/register-before-<mode>.yaml`, and the original data are loaded from that copy.
- **Staged, then checked, then written.** `model.save` writes `C:/Temp/av-kit/s49b/stage/known-issues.yaml`. Every check below runs on the staged file. Only a stage with no problem replaces the register's contents, through the held handle, and the script then reads them back and compares the bytes. On any problem the register keeps its bytes, so S5's "last good save" is the file as it was.

The three modes:

- **`--mode reformat` (row 4)** saves the data unchanged. It exits 1 unless:
  - the parsed difference is empty;
  - the written file parses back to the data;
  - the whole file passes `check_yaml_subset`;
  - `issue_decision_log` returns, for every one of the 67 logs, the (id, stage) list the data hold. The only exception is the six planned issues, which may be refused only by the placeholder test.
- **`--mode reword` (row 5)** replaces the 15 fields in §Rewording. Each is replaced only if it still holds its before text exactly, and only if the after text doesn't match `PLACEHOLDER`. It exits 1 unless:
  - the parsed difference is exactly those 15 paths;
  - all 67 logs read equal;
  - no decision log matches the placeholder pattern.
- **`--mode resolve` (row 7)** sets `status`, `verification` and `resolution_path` on `CLOSEOUT-CHECK-REFUSES-REGISTER` from the JSON file `--set-file` names. It refuses a set file holding any other key. It exits 1 unless:
  - the data pass `validate_strict`;
  - every parsed difference is under those three keys of that issue;
  - all 67 logs read equal, and none matches the placeholder pattern.

Every mode prints the SHA-256 before and after, and the CRLF and LF counts. `--target` copies the stage to another file, and the register is never written. The handle check then confirms the register's bytes didn't change. Plan-time probes ran with `--target`, or with the script's `REGISTER` pointed at a copy.

### Rewording (D-285)

The convention: a brace or angle-bracket name becomes the same name in upper case, explained once in the sentence, and `${…}` is described in words. Only the quoted span changes in each field. The full strings are `REWORDS` in `REWRITE`, which refuses to write if any before text has changed.

1. **`CAPTURE-FLATTEN-WITH-BACKUP` D-15 `chosen`.**
   - Before: "copies original to `{inbox}/.avkit-backup/{stem}.{YYYYMMDD-HHMMSS}.png`, bakes over original_path" … "capture.backup_dir (default `{inbox}/.avkit-backup`)"; also "POST /captures/`{id}`/flatten".
   - After: "POST /captures/ID/flatten copies original to INBOX/.avkit-backup/STEM.YYYYMMDD-HHMMSS.png (ID is the capture id, INBOX the capture inbox, STEM the original's file stem), bakes over original_path" … "capture.backup_dir (default INBOX/.avkit-backup)".
2. **`TTS-VOICE-PACK-LAZY-FETCH` D-42 `chosen`.**
   - Before: "Yes: `voices/<id>.pt` is fetched".
   - After: "Yes: voices/ID.pt (ID is the voice id) is fetched".
3. **`MCP-TTS-GENERATE-SYNCHRONOUS` D-44 `chosen`.**
   - Before: "and `DELETE /tts/{id}` cancels a running job".
   - After: "and DELETE /tts/ID (ID is the job id) cancels a running job".
4. **`MCP-SETUP-PROMPT` D-47 `chosen`.**
   - Before: "using `${AVKIT_API_TOKEN}` expansion; the real token".
   - After: "using environment-variable expansion of AVKIT_API_TOKEN (a dollar sign and the name in braces); the real token".
5. **`MCP-SETUP-PROMPT` D-47 `precedents[1]`.**
   - Before: "mcpServers vs servers shapes, `${VAR}` expansion)".
   - After: "mcpServers vs servers shapes, dollar-brace environment-variable expansion)".
6. **`MCP-SETUP-PROMPT` D-47 `reasoning`.**
   - Before: "converges on project .mcp.json + `${VAR}`; keeping the token".
   - After: "converges on project .mcp.json + dollar-brace environment-variable expansion; keeping the token".
7. **`MCP-SETUP-PROMPT` D-49 `question`.**
   - Before: "Does any setup-prompt block carry the token or a `${AVKIT_API_TOKEN}` expansion?"
   - After: "Does any setup-prompt block carry the token or a dollar-brace expansion of AVKIT_API_TOKEN?"
8. **`MCP-SETUP-PROMPT` D-49 `chosen`.**
   - Before: "the server reads `{app_data}/mcp-token.txt` itself" … "Supersedes the `${VAR}`/inject-on-Copy part of D-47".
   - After: "the server reads mcp-token.txt in the app data folder itself" … "Supersedes the dollar-brace expansion and inject-on-Copy part of D-47".
9. **`MCP-SETUP-PROMPT` D-49 `reasoning`.**
   - Before: "beats both a literal token and `${VAR}` expansion (which still needs".
   - After: "beats both a literal token and dollar-brace expansion (which still needs".
10. **`MCP-SETUP-PROMPT` D-52 `chosen`.**
    - Before: "ends with exactly one 'RESULT: connected `<api_base>`' or 'RESULT: failed (`<step>`, `<error>`)' line; no new instance_id."
    - After: "ends with exactly one 'RESULT: connected API_BASE' or 'RESULT: failed (STEP, ERROR)' line, the upper-case names standing for the values; no new instance_id."
11. **`MCP-SETUP-PROMPT` D-53 `chosen`.**
    - Before: "Back up to `<file>.avkit-backup-<UTC>` and merge" … "quit and reopen `<client>`, then reply Ready')."
    - After: "Back up to FILE.avkit-backup-UTC and merge" … "quit and reopen CLIENT, then reply Ready'), FILE being the client's config file, UTC a UTC timestamp and CLIENT the client's name."
12. **`MCP-SETUP-PROMPT` D-57 `precedents[0]`.**
    - Before: "falls back to LOCALAPPDATA ?? `<home>/AppData/Local`, then av-kit".
    - After: "falls back to LOCALAPPDATA ?? the home folder's AppData/Local, then av-kit".
13. **`MCP-SETUP-PROMPT` D-58 `chosen`.**
    - Before: "'RESULT: failed (`<step>`, `<error>`)' line, where `<error>` is the server's error code (for example token_missing, app_not_running)."
    - After: "'RESULT: failed (STEP, ERROR)' line, where ERROR is the server's error code (for example token_missing, app_not_running) and STEP the step that failed."
14. **`QUEUE-PILL-TOKEN-DRIFT` D-72 `chosen`.**
    - Before: "(git show `<sha>`:ui/src/renderer/src/globals.css)".
    - After: "(git show SHA:ui/src/renderer/src/globals.css, SHA being that commit)".
15. **`CONVERT-EXTRACT-STREAM-INDEX-MISMATCH` D-227 `precedents[1]`.**
    - Before: "adapter.py:634-635 — `a:{stream_index}`".
    - After: "adapter.py:634-635 — the stream specifier a: followed by the stream index".

`.agent/context/known-issues.md` renders no decision log (`tools/issue_triage/render.py`), so the rewording doesn't change it. Row 5 checks with `render --check`.

### Closeout register grammar (`CLOSEOUT-CHECK-REFUSES-REGISTER`)

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `validate_closeout_artifacts.py --decision-issue ID` (repeatable) | The validator's argparse | Each ID non-empty, none repeated, and each one an issue the known-issues source holds | argparse refuses an unknown flag |
| `known-issues.yaml` as `model.save` writes it | `tools/issue_triage/model.py` `validate_strict` | `validate_strict` is unchanged. `save` also refuses an empty or multi-line string key, and any data whose text doesn't load back equal (D-281) | Unchanged |

No REST, MCP or UI surface changes, so `openapi`, `mcp-*` and `ui-*` don't apply.

#### Acceptance Criteria

The tests are in `tests/tooling/test_closeout_register_grammar.py`, named `test_ac_<n>_…`. The writer's tests import `issue_triage.model` and the validator's `check_yaml_subset` and `issue_decision_log`. The flag tests run the validator's CLI by subprocess, as `tests/tooling/test_framework_adoption.py` does, on fixtures built from the validator's own selftest constants (`_GOOD_REFLECTION`, `_GOOD_REFLECTION_TEMPLATE`, `_DECISIONS_LOG_ROWS`, `_DECISION_KNOWN_ISSUES`).

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-1 | unit | `model.save` writes every sequence indented under its key, and a sequence inside a sequence in the noncompact form, so the whole file passes `check_yaml_subset`. `issue_decision_log` reads nested lists inside a decision item (`precedents`, `research.sources`, and a list of lists three deep). | Local Canon (`CLOSEOUT-CHECK-REFUSES-REGISTER`; D-274) | Today the grammar refuses the fixture ("mixes a mapping and a sequence") |
| AC-2 | unit | `model.save` doesn't wrap: a 300-character value sits on one line. A multi-line value is a literal block. A string with trailing spaces, a tab, a `\r`, U+0085, U+2028 or U+2029, or ending in two newlines, is written so the whole file still passes `check_yaml_subset`. So is a list object shared by two fields: it is written twice, with no anchor. An empty or multi-line string key makes `save` raise `IssueTriageError`, and the file already at the path keeps its bytes. | Local Canon (same; D-281) | Today the 300-character value wraps and the grammar refuses it |
| AC-3 | unit | What `model.save` writes loads back through `model.load` equal to the data, for every edge string in AC-2 plus colon, `yes`, `#`, quote, unicode, leading-dash and empty strings. | Local Canon (D-281) | A guard for every case but one: today's writer loads `ab` back as `a b`, so the U+0085 case fails in Red too (plan review round 2). It fails later if the new representer changes a value |
| AC-4 | integration | With `--decision-issue` repeated, the check reads every named issue: a reflection missing a decision of the first-named issue is refused. | Local Canon (`CLOSEOUT-CHECK-REFUSES-REGISTER`; HDP §6) | Today only the last value is read, so the check exits 0 |
| AC-5 | integration | Repeating one ID among the flags is `Usage`, exit 2. | Local Canon (D-283) | Today exit 0 |
| AC-6 | integration | A named issue absent from the source is refused, even when another named issue is present. | Local Canon (`:1503`; D-283) | Today exit 0 when the absent issue is not last |
| AC-7 | integration | A reflection carrying every decision of every named issue passes with several flags, and a single flag behaves as before. | Local Canon (HDP §6) | A guard: it passes today, and fails if the change breaks a single flag |
| AC-8 | unit | The validator's `--selftest` gains arms for AC-4, AC-5 and AC-6, and reports 0 failures. | Local Canon (the selftest is the validator's own contract; `test_evidence_contract_real_cli_selftests`) | Each arm's expected exit is the AC's |
| AC-9 | integration | `REWRITE --mode reformat` saves the register with no parsed difference. The whole file passes the grammar, and all 61 logs outside the six planned issues read equal. | Human-approved (D-274; Mat's brief: "every parsed value asserted equal by a script") | Today, with the old `save`, it exits 1 with 66 problems (`s49b/probe-old.txt`) |
| AC-10 | integration | `REWRITE --mode reword` changes exactly the 15 planned fields, all 67 logs read equal, and no decision log matches the placeholder pattern. | Human-approved (D-274; D-285 at the human gate) | It refuses if a before text has changed or an after text matches `PLACEHOLDER` |
| AC-11 | integration | `DONE_PROOF` exits 0 against `REGISTER` as written. | Human-approved (Mat's brief: "Done means…") | Row 0's Red receipt: today it exits 1, refusing the second issue's log as invalid YAML |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| The grammar the writer must meet | Local Canon | `check_yaml_subset` (`:1039`), unchanged |
| PyYAML's indentless lists, wrapping, block and quote styles | Research-backed | PyYAML documentation, and the emitter measured at plan time (`s49b/edge.txt`, `s49b/proto.txt`) |
| What a repeated flag means | Local Canon | HDP §6's reconciliation: every named issue's log is reconciled |
| How argparse repeats a flag | Research-backed | Python docs: `action="append"` keeps every value, the default keeps the last |
| What "same meaning" requires in a reword | Human-approved | Mat reads §Rewording at the plan gate (D-285) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `tools/issue_triage/model.py` | modify | `save` per §`model.save`; CRLF kept |
| `tools/validate_closeout_artifacts.py` | modify | Repeatable flag, selftest arms; CRLF kept |
| `tests/tooling/test_closeout_register_grammar.py` | create | AC-1 to AC-7; CRLF, like its peer |
| `.agent/docs/human-decision-protocol.md` | modify | `:201-203`, the flag repeats once per issue; CRLF kept |
| `.agent/context/known-issues.yaml` | modify | Rows 4, 5 and 7 through `model.save`; LF |
| `.agent/context/known-issues.md` | modify | Rendered (row 7) |
| `.agent/context/triage-output.yaml` | modify | Regenerated (row 7) |
| `.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md` | modify | §6 tracker row 49b (`:239`) gets the plan folder and status; CRLF kept |
| `.agent/context/current-focus.md` | modify | H1-3 |

### Project files

Plan-local scripts, listed in §Verification Plan: `baseline.sha`, `baseline-dirty.txt`, `baseline.ps1`, `red-check.py`, `identity.py`, `register-rewrite.py`, `session-gate.ps1`. State: `docs/execution/metrics.md`, the handoff, the rolling reviews and the reflection.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| `tools/issue_triage/triage.py:65`, the triage-output dump | out-of-scope | — | No closeout check reads `triage-output.yaml`; the brief scopes `save` (D-287) |
| Loosening the reader to accept indentless lists or wrapped values | out-of-scope | — | D-282: the writer conforms to the strict reader |
| Changing `PLACEHOLDER` | out-of-scope | — | It guards against real template residue; the six logs are reworded instead (D-285) |
| The two `TASK-TEMPLATE.md` H2-2 rows | out-of-scope | — | One flag is still valid; the protocol paragraph documents the repeat |
| Carrying the change upstream to the framework the validator came from | out-of-scope | — | Not in the brief; a question for Mat |
| Session 50 `transcript-failure-reason` | deferred | MEU-115, MEU-116 | Grouping §3; D-247 already ruled |

## BUILD_PLAN.md Audit

This project adds no build-plan section and changes no MEU, so `docs/BUILD_PLAN.md` and `meu-status.yaml` don't change. Row 7 proves the hub is a no-op:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s49b-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s49b-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`.
2. Checks that the register's SHA-256 is still `900b2cb0…`. If it isn't, S4 applies, because another session wrote it after the plan's measurements.
3. Runs `uv sync --frozen --all-packages` and captures the base Python suite to `s49b-base-py.txt`, with `TMP` and `TEMP` at `C:\Temp\av-kit\s49b\tmp` (RC1 ECN-2).
4. Runs `DONE_PROOF` as it stands, records its exit in `s49b-done-proof-red.txt.exit`, and requires exit 1 with "is not valid YAML". This is AC-11's Red: the second issue's log is refused, and only the last flag is read.
5. Runs `red-check.py --selftest` and `identity.py --selftest`.

No UI or MCP install runs, because nothing here builds or tests them.

`red-check.py` and `identity.py` are copies of Session 49's, with this plan's values:

- **`red-check.py`.** `DECLARED_NEW` holds only the five names its selftest needs.
- **`identity.py`.** `PLAN` is this folder.
- **`PROJECT_ARTIFACTS`.** It holds this plan's `*.md`, this session's handoff, review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`, which are written after the gate. The register and its renders stay bound, because rows 4, 5 and 7 write them before H1-2.

### 2. Red then Green (rows 1 to 3)

- **Each Red receipt holds an assertion failure, never a setup failure.** The writer's tests catch the validator's `Refuse` and assert on it, so a refusal is an assertion failure, not an error. `--require test_ac_<n>` matches exactly, because `red-check.py:209` won't let `test_ac_1` match `test_ac_10`.
- **AC-7 passes in Red by design, and so does AC-3 except its U+0085 case.** They guard against what Green could break. Today's writer loads U+0085 back as a space, so that one AC-3 case fails in Red; row 1 doesn't require AC-3 either way, and its equality assertion stays.
- **AC-8 has no Red.** It is the selftest run in row 3, which `test_evidence_contract_real_cli_selftests` also runs in the full suite.
- **Expectations stay immutable in Green.** Rows 1 to 3 keep each file's CRLF line endings: they measure with Python bytes and write with `newline=""`.

### 3. The register (rows 4 to 6)

`REWRITE` was probed at plan time with a monkeypatched `save` against temporary targets (`C:/Temp/av-kit/s49b/probe-chain.txt`). The register stayed unchanged.

- **Reformat.** 0 parsed fields changed. The whole-file grammar passed. 61 of 67 logs read, and the 6 refusals were the planned placeholder ones. LF 4092.
- **Reword over that output.** Exactly 15 fields changed and 67 of 67 logs read.

Against today's `save`, reformat exits 1 with 66 problems (`probe-old.txt`). Rows 4 and 5 run `REWRITE` on the register itself after rows 2 and 3 are Green. `DONE_PROOF`, run one issue at a time against the reworded probe output, already reconciles 24 and 27 decisions (`s49b/predict-*.txt`). Row 6 runs it once, with both flags, against the register.

### Plan-local scripts

Written with their rows and kept in this plan folder:

- `register-rewrite.py` (plan time, run by rows 4, 5 and 7)
- `baseline.ps1`, `red-check.py`, `identity.py` (row 0)
- `session-gate.ps1` (H1-2)

### Session gate (H1-2)

`session-gate.ps1` is Session 49's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s49b-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-lint` (`ruff check packages/ tests/`), `tools-lint` (`ruff check tools/issue_triage/model.py tools/validate_closeout_artifacts.py`, clean at plan time), `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`), `red-check-selftest` |
| Fresh full | `py-tests` (which runs the validator's `--selftest`), `state-render`, `issues-render` (`issue_triage.py render --check`) |
| Skipped, with reason | `py-types`: `pyright packages/`, and nothing under `packages/` changes. `ui-types`, `ui-lint`, `ui-tests`, `ui-build`, `ui-electron`: nothing under `ui/` changes, and no UI test reads the files this session writes (`grep`, 2026-11-05: `layout-canon` reads only a 2026-09-03 grouping file). `mcp-*`: no MCP change. `openapi`: no `packages/api` change (H1-4). `build-record`: no build. |

`py-tests` excuses only ids that row 0's receipt shows failing, as Session 49 did.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | The new `save` can't make some register value pass the grammar while loading back equal | Stop; bring the value and the options to Mat. Don't loosen the reader |
| S3 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S4 | `HEAD` moves from `baseline.sha`; a path outside `baseline-dirty.txt` and this plan appears; or the register's SHA-256 or mtime changes other than by rows 4, 5 and 7 | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | `REWRITE` reports any problem, including a before text that no longer matches, a refused handle, or a write by another process failing while a row held the register | Stop; the register keeps the bytes it had before that row. Bring it to Mat |
| S6 | `DONE_PROOF` refuses for a reason other than this session's scope | Report it to Mat; don't change the Session 49 reflection |
| S7 | Codex is unavailable or the ledger refuses | Mat |

## Decision Log

> [!WARNING]
> No decision here needs Mat except D-285's wording, which Mat reads at the plan gate. Carried from the grouping and not relisted in the block, because the grouping's rows hold them: every §8 row, D-240 to D-250, D-267, D-277 and D-280. The closeout check reads all of them, and D-246 stays as a withdrawn row. D-274 and D-279 are in `.agent/context/known-issues.yaml` under `CLOSEOUT-CHECK-REFUSES-REGISTER`.

```yaml
decision_log:
  - id: D-281
    stage: planning
    question: "What does model.save write?"
    resolution: autonomous
    class: two-way
    chosen: "Every sequence indented under its key, no wrapping, multi-line strings as literal blocks, strings ending in two newlines or holding U+0085, U+2028 or U+2029 double-quoted, a sequence inside a sequence noncompact, no anchors or aliases, an empty or multi-line string key refused, and the text checked to load back equal before the file is opened; PyYAML's own double-quoted fallback stays for strings a literal block cannot hold"
    source_tag: Local Canon
    precedents: ["tools/validate_closeout_artifacts.py:1039 — check_yaml_subset, the grammar to meet", "tools/issue_triage/model.py:345 — the dump today"]
    research: { engine: "pomera_web_search (tavily)", sources: ["https://pyyaml.org/wiki/PyYAMLDocumentation — the emitter's width, indent and styles are configurable", "https://medium.com/@reorx/tips-that-may-save-you-from-the-hell-of-pyyaml-572cde7e1d6f — a Dumper whose increase_indent passes indentless False indents the lists", "https://til.simonwillison.net/python/style-yaml-dump — a str representer picks the block style"] }
    reasoning: "Measured at plan time: this format reads back equal for every value in the register and passes the grammar over the whole file, and the edge strings pass too. Always double-quoting would also pass but makes every multi-line decision unreadable in a diff. Teaching the reader indentless lists loosens a grammar that refuses on purpose (D-282)."
  - id: D-282
    stage: planning
    question: "Does the reader change, or the writer?"
    resolution: autonomous
    class: two-way
    chosen: "The writer conforms. check_yaml_subset, issue_decision_log and the placeholder pattern stay as they are"
    source_tag: Local Canon
    precedents: [".agent/context/known-issues.yaml — D-274's research names a restricted reader as an established pattern"]
    research: { engine: none, sources: ["https://github.com/crdoconnor/strictyaml — a restricted YAML reader is an established pattern"] }
    reasoning: "The grammar is the closeout check's own contract, and every other source it reads already meets it. One writer is easier to change than a reader that other sessions rely on refusing."
  - id: D-283
    stage: planning
    question: "What does a repeated --decision-issue mean?"
    resolution: autonomous
    class: two-way
    chosen: "Every named issue is read, in order, each under its own label; a repeated ID is Usage; a named issue the source does not hold is refused; one decision with two stages anywhere is refused. The protocol paragraph documents the repeat, and the task templates stay as they are"
    source_tag: Local Canon
    precedents: [".agent/docs/human-decision-protocol.md:201 — the reconciliation reads the closed issue's log", "tools/validate_closeout_artifacts.py:1503 — an absent issue is refused so the check never passes vacuously"]
    research: { engine: "pomera_web_search (tavily)", sources: ["https://docs.python.org/3/library/argparse.html#action — append keeps every value; the default keeps the last"] }
    reasoning: "A session closing several issues must reconcile all of them in one run. A comma-separated value would also work but needs its own parsing, and one run per issue is the workaround this removes."
  - id: D-284
    stage: planning
    question: "How is the register rewritten?"
    resolution: autonomous
    class: two-way
    chosen: "Three saves through a plan-local script, each holding an exclusive handle on the register from read to write, bound to the expected hash, staged and checked before the register is written: a reformat whose parsed difference must be empty, a reword whose parsed difference must be exactly the 15 planned fields, and the resolve of this issue, confined to three keys"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-11-04-rc2-fetch-uninstall/issue-decisions.py — Session 49's extract checked the reader against the register's ids"]
    research: { engine: none, sources: [] }
    reasoning: "Mat asked for a script that loads both and compares, not an eye check. Keeping the reformat and the reword in separate saves keeps each diff to one kind of change: the first is layout only, and the second is 15 values. Round 1 of the plan review showed a hash check before loading still let a concurrent save be overwritten; holding a deny-write handle across the run closes that interval, and staging keeps a refused save off the register."
    human_message_reference: "USER_EXPLICIT 2026-11-05 session brief 'with every parsed value asserted equal by a script that loads both and compares, not by eye'"
  - id: D-285
    stage: planning
    question: "How are the 15 refused fields reworded?"
    resolution: autonomous
    class: two-way
    chosen: "A brace or angle-bracket name becomes the same name in upper case, explained once in the sentence; dollar-brace expansion is described in words; nothing else in the field changes"
    source_tag: Local Canon
    precedents: [".agent/context/known-issues.yaml — UNINSTALL-LEAVES-INSTALLER-COPY D-228 was reworded the same way in Session 49"]
    research: { engine: none, sources: [] }
    reasoning: "The placeholder pattern refuses these spans because a real template leaves the same shapes behind. Upper-case names keep each field as short as it was and read as the same value. Mat reads every before and after text in the plan's Rewording section before row 5 runs."
  - id: D-286
    stage: planning
    question: "What does the session gate cover?"
    resolution: autonomous
    class: two-way
    chosen: "Identity, Python lint over packages and tests plus the two touched tools, the task contract, the scope paths, the red-check selftest, the full Python suite, and the state and issue renders; types, UI, MCP, OpenAPI and the build record are skipped for the reasons in the plan's Session gate"
    source_tag: Local Canon
    precedents: [".agent/docs/commands.md:190-207 — the D6 stages", "AGENTS.md:82 — one fresh full scoped gate before final review"]
    research: { engine: none, sources: [] }
    reasoning: "The session changes two Python tools, one Python test file, one register and docs. Nothing under packages, ui or mcp-server changes, and no UI test reads what changes. The full Python suite runs the validator's selftest."
  - id: D-287
    stage: planning
    question: "Does the triage-output dump change too?"
    resolution: autonomous
    class: two-way
    chosen: "No. Only model.save changes"
    source_tag: Local Canon
    precedents: ["tools/issue_triage/triage.py:65 — writes triage-output.yaml, which no closeout check reads"]
    research: { engine: none, sources: [] }
    reasoning: "The defect is the register the closeout check reads. Changing a second writer would grow the diff of a regenerated file for no reader."
  - id: D-288
    stage: planning
    question: "Where and how are the tests written?"
    resolution: autonomous
    class: two-way
    chosen: "tests/tooling/test_closeout_register_grammar.py, collected by the default pytest run; the writer through model.save and the validator's grammar functions, the flag through the CLI by subprocess on fixtures built from the validator's selftest constants"
    source_tag: Local Canon
    precedents: ["tests/tooling/test_framework_adoption.py — runs the validator's CLI by subprocess", "pyproject.toml — testpaths is tests, so tools/tests is not collected"]
    research: { engine: none, sources: [] }
    reasoning: "The CLI is the surface a closing session uses, so the flag is tested there. The selftest constants are the validator's own known-good reflection, which keeps the fixtures small."
```

## Research References

- PyYAML documentation: https://pyyaml.org/wiki/PyYAMLDocumentation. Official.
- PyYAML indented sequences: https://medium.com/@reorx/tips-that-may-save-you-from-the-hell-of-pyyaml-572cde7e1d6f. Blog; the recipe was measured here (`s49b/proto.txt`).
- PyYAML string styles: https://til.simonwillison.net/python/style-yaml-dump. Blog; measured here (`s49b/edge.txt`).
- ruamel.yaml on PyYAML's non-indented block sequences: https://yaml.dev/doc/ruamel.yaml/detail. Official for ruamel.
- argparse `action`: https://docs.python.org/3/library/argparse.html#action. Official.
- strictyaml: https://github.com/crdoconnor/strictyaml. Carried from D-274.

Searches: `C:/Temp/av-kit/s49b/research-pyyaml.txt`, `C:/Temp/av-kit/s49b/research-argparse.txt`.

## Planning receipts

All under `C:/Temp/av-kit/s49b/`. Each probe was read-only with respect to the repository, and the register's SHA-256 was unchanged after each one.

- **`scan.txt`, `entries.txt`.** The register's 67 decision logs, and the 15 fields the placeholder pattern matches.
- **`proto.txt`, `proto-dump.yaml`.** The prototype format over the whole register reads back equal and passes the whole-file grammar, with 16 literal blocks. 61 of 67 logs read, and the 6 refusals are the placeholder issues.
- **`edge.txt`.** Edge strings:
  - Trailing space, tab and CRLF fall back to one-line double quotes.
  - A leading space gives `|2-`, and a mid-document `|+` passes.
  - Long, colon, `yes`, hash, quote, unicode, leading-dash and empty strings pass and read back equal.
  - Only `|+` at the end of the document emits `...`, which the grammar refuses. That case is D-281's two-newline rule.
- **`r1-writer.txt`** (after round 1). The revised dumper over nested sequences to three deep, sequences of maps inside sequences, empty inner lists, U+0085, U+2028 and U+2029, int keys, long values, two trailing newlines and trailing spaces. Each reads back equal, passes the grammar, and `issue_decision_log` reads its log. Empty and multi-line keys are refused before writing. Over the register, its output is byte-identical to `proto-dump.yaml`.
- **`r1-probe.txt`, `r1-rewrite-probe.txt`** (after round 1). A deny-write handle refuses another process's `open('w')` and `os.replace`, and is itself refused while another process holds the file open for writing. `REWRITE` against a copy of the register refuses a wrong hash and a held file. With a writer started mid-run, that writer gets `PermissionError` and the register holds the staged bytes. The chain reformat, reword and resolve changes 0, 15 and 3 fields, reading 61, 67 and 67 logs. A set file with another key is refused. The real register's hash didn't change.
- **`alias.txt`.** A list shared by two fields makes the default dumper write `&id001` and `*id001`, which the grammar refuses. With `ignore_aliases` returning `True`, the list is written twice, reads back equal and passes.
- **`probe-old.txt`, `probe-chain.txt`.** `REWRITE` against today's `save` gives 66 problems. Against the prototype it gives 0 and then 0 (§Verification Plan 3).
- **`done-proof-plan-time.txt`.** `DONE_PROOF` today exits 1: "issue FFMPEG-LIBDVDCSS-BUNDLED decision_log item 1 is not valid YAML: line 9: … mixes a mapping and a sequence".
- **`predict-UNINSTALL-LEAVES-INSTALLER-COPY.txt`, `predict-FFMPEG-LIBDVDCSS-BUNDLED.txt`.** One run per issue against the reworded probe output exits 0, reconciling 24 and 27 decisions.
- **`ruff-plan-time.txt`.** The two tools and `tests/tooling/` are lint-clean. The 37 findings are all E501 in `register-rewrite.py`, which no D6 lint step covers. Its long lines are the exact before and after texts.
- **Not run at plan time:** any write to the register, and the new tests.

## Validation stage contract

- **Static:** `py-lint`, `tools-lint`, `task-contract`, `scope-paths`, `red-check-selftest`.
- **Targeted:** the test file in rows 1 to 3, the selftest in row 3, and `REWRITE` in rows 4, 5 and 7.
- **Fresh full:** `py-tests`, `state-render`, `issues-render`.
- **Runtime:** `DONE_PROOF` in row 6.
- **Identity:** from `identity.py`, independent of the receipts.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
