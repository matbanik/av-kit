---
project: "2026-11-15-closeout-record-once"
date: "2026-11-15"
source: "P:/agentic-framework commits a73d6df (the closeout-validator part) and ec3857a"
grouping_source: ".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md"
meus: []
status: "draft"
template_version: "2.3"
---

# Implementation Plan: Closeout reads each decision once, in its stage log

> **Project**: `2026-11-15-closeout-record-once`
> **Build Plan Section(s)**: none (closeout tooling; no MEU, D-821)
> **Status**: `draft`
> **Session**: 84 of the HDP framework-sync grouping (Sessions 84 to 87, run in order on `main`)

---

## Goal

**Goal anchor:** The closeout validator reads every decision once, where it was made (the plan, the handoff, the grouping or the issue), refuses an entry that is not stated in full or is still pending, and no longer makes the reflection restate each decision; and its plan-root search stops at the repository boundary.

Two upstream commits in `P:/agentic-framework` are ported:

- **`a73d6df`** ("feat(hdp): port the decision protocol and the expert pass", 2026-11-14), the closeout-validator part only. Upstream dropped the reflection-versus-stage-log reconciliation ("record once"), added a field check and a pending check on stage-log entries, and added a check that the reflection's Decisions Log no longer holds the template example. The protocol, templates and expert-pass parts of that commit belong to Sessions 85 and 86.
- **`ec3857a`** ("fix(closeout): end the plan-root search at the repository boundary", 2026-11-10). `project_root` stops at an ancestor with a `.git` entry. This closes known issue `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR`: under the default temp folder the selftest finds the home folder's `.agent` and 5 of 219 arms fail (`C:/Temp/av-kit/cro/selftest-plan-time-default-tmp.txt`).

Today `tools/validate_closeout_artifacts.py:1840` (`check_decisions_log`) refuses a reflection unless every decision in every source has its own Decisions Log row with the same stage. That makes each decision live in two places. Session 85 moves the reflection template to a link list, and today's validator would refuse it (D-826). This session lands first so that Sessions 85 and 86 can close.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). Every payload here is source code, an upstream diff or a register entry that must be read verbatim, which is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`, with receipts under `C:/Temp/av-kit/cro/` named `cro-*`, `RECEIPTS_DIR=C:/Temp/av-kit`, `PYTHONIOENCODING=utf-8` and `ELECTRON_RUN_AS_NODE` cleared. Python runs through `uv run`; Vitest is not used.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub`, `P:/agentic-framework`, `P:/zorivest` and `P:/.agent` are read only, and the hub is never opened.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`, under ledger loops `cro-plan-2026-11-15-closeout-record-once` and `cro-execution-2026-11-15-closeout-record-once`. Claude wrote the plan, so the reviewer is a different vendor. Caps come from `.agent/review-limits.json` (plan 3, execution 6, token budgets off) and are printed by `review_ledger.py state`. The orchestrator dispatches; if Codex is unavailable or the ledger refuses a round, the fallback is Mat. Each round is metered, and the coordinator warns before dispatching.
- **Never in these rows without Mat's words:** commit, push, merge, release, a destructive data operation, external disclosure, credentials, or an `approved` verdict authored by the implementer.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| Closeout record-once (no MEU) | `.agent/context/handoffs/2026-11-15-closeout-record-once-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-15-closeout-record-once-plan-critical-review.md` and `.agent/context/handoffs/2026-11-15-closeout-record-once-implementation-critical-review.md`. The single non-MEU handoff follows `2026-11-14-review-limits-no-token-budget`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-content.txt`, `baseline-dirty-content.txt`, `selftest-arms-before.txt`, `cro-base-*.txt` |
| WP-2 | Tests Red, then the port Green (rows 1 to 5) | WP-1 | shared | `tests/tooling/test_closeout_record_once.py`, `tests/tooling/test_closeout_register_grammar.py`, `tools/validate_closeout_artifacts.py` |
| WP-3 | Selftest arms (row 6) | WP-2 | shared | `cro-selftest*.txt`, `cro-arms-check.txt` |
| WP-4 | Close the known issue (row 7) | WP-3 | shared | `.agent/context/known-issues.yaml`, `.agent/context/known-issues.md` |
| WP-5 | Old reflections and stage logs (row 8) | WP-4 | shared | `cro-reflections.txt`, `cro-survey.txt` |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | Handoff, review, reflection, Session 85 prompt |

## User Review Required

> [!IMPORTANT]
> **What changes for every later closeout.** A reflection's Decisions Log no longer has to repeat each decision. `None.` and a link list both pass, whatever the stage logs record. The stage log becomes the one record, and the validator now refuses an entry there whose `question`, `chosen` or `reasoning` is blank or not text, or whose `chosen` starts with `pending`. A quoted value followed by a `# comment` is read as the text inside its quotes, so `chosen: "pending Mat" # awaiting reply` is refused as pending (D-831, amended after plan review R1, CRO-P1). A double-quoted value's YAML escapes are decoded first, so `reasoning: "\n"`, which `tools/issue_triage/model.py` writes for a reasoning that is only a newline, is refused as blank, and `chosen: "\u0070ending Mat"` as pending (D-831, amended after the R1 recheck, CRO-R1-1). A grouping's §8 row gets the same check: a ruled row (`autonomous` or `human`) needs its Question, Chosen and Reasoning cells, and a Chosen that does not start with `pending` (D-829, amended after R1, CRO-P2). A reflection that still holds the template's `_{…}_` example in its Decisions Log is refused.
>
> **Five checks go (D-826, ruled by default acceptance).** These are the refusals for:
> 1. `None.` while a source records decisions.
> 2. A decision missing from the reflection.
> 3. A reflection row whose stage differs from its source. The check that one decision has one stage across sources stays.
> 4. A blank reflection cell. This moves to the stage-log field check.
> 5. A duplicate or unknown Resolution, or a two-column table. These go with the table.
>
> Fourteen selftest arms that tested them are removed, and sixteen arms that refused only because a reflection row was missing now expect OK. Each is named in §Selftest arm changes.
>
> **What stays av-kit's own.** `refuse_repeated_ids` stays, with its message reworded (D-827). The repeatable `--decision-issue` stays too (D-828). §The av-kit-only checks lists each one.
>
> **Two things go stale until Session 85.** `human-decision-protocol.md` §6 still describes the reconciliation and the `.agent`-ancestor root, and `docs/execution/reflections/TEMPLATE.md` still shows the table (D-835). This session's own reflection uses the table form, which the ported validator accepts.
>
> **An `open` grouping row still closes (D-829, amended after R1).** It must state its Question and its Reasoning (why it stays open), but its Chosen is not read. Refusing it would block every session that consumes a grouping whose open question belongs to a later session: D-101 stayed `open` through Sessions 40 to 42, each of which closed. Upstream reads `open` rows too. The 10 groupings in the tree have 0 rows the check refuses (`C:/Temp/av-kit/cro/stage-log-survey-r1-1.txt`). This is ruled under the default acceptance; if Mat wants open rows refused at closeout, D-829 changes and AC-2's open-row negative flips.
>
> **One open plan with pending rulings.** `2026-11-04-rc2-ffmpeg-uninstall` records D-246 and D-251 with `chosen` pending. Its closeout will be refused until the rulings are recorded (D-838).
>
> **The token estimate.** The upstream validator diff is about 480 changed lines; av-kit's selftest changes are 14 removed, 16 flipped and 26 added arms (15 from upstream, 6 for the R1 corrections and 5 for the R1 recheck). Expect 1 or 2 plan rounds and 1 or 2 execution rounds.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `VALIDATOR` | `tools/validate_closeout_artifacts.py`. It is CRLF (5,671 lines, 0 bare LF, `C:/Temp/av-kit/cro/eol-plan-time.txt`), and it stays CRLF. |
| `UPSTREAM_A` | The validator part of `git -C P:/agentic-framework show a73d6df -- core/tools/validate_closeout_artifacts.py core/tools/tests/test_validate_closeout_stages.py`. A full copy at that commit is `C:/Temp/av-kit/cro/upstream-a73d6df.py`. |
| `UPSTREAM_E` | `git -C P:/agentic-framework show ec3857a -- core/tools/validate_closeout_artifacts.py`. It is an ancestor of `a73d6df`. |
| `FIELD_CHECK` | The refusal of a stage-log decision that is not stated in full or is still pending, in two forms (amended after plan review R1). **A `decision_log` entry** (plan, handoff, issue) is refused when its `question`, `chosen` or `reasoning` is missing, blank or non-text, which means `decision_field_text` returns `None`, or when its `chosen` matches `re.match(r"pending\b", chosen, re.IGNORECASE)`. A quoted value is read by `_quoted_scalar_text`: one whole quoted scalar and an optional `# comment` give the text inside the quotes, and a `#` inside the quotes is text (D-831, CRO-P1). A double-quoted body's YAML escapes are decoded before the blank and pending tests, so `"\n"`, `"\t"` and `"\x20\L"` are blank and `"\u0070ending Mat"` is pending; a single-quoted body has no escapes (D-831, CRO-R1-1). **A grouping §8 row** is refused by `grouping_row_problems` when its Question or Reasoning cell is blank, or, on a row whose Resolution is `autonomous` or `human`, when its Chosen cell is blank or matches the same pending test. A cell is blank when it holds only whitespace, `` ` ``, `*`, `_` and at most one `-`, `–` or `—`. An `open` row's Chosen is not read, and the YAML non-text rule does not apply to a cell, since a table has no types (D-829, CRO-P2). |
| `EXAMPLE_CHECK` | The refusal of a reflection whose `### Decisions Log` body (up to the next `##` heading) holds `_{`. |
| `PORT_SHAPE` | The static shape `port-check.py` checks (AC-15, AC-16). |
| `REFLECTION_SET` | Every `docs/execution/reflections/*.md` except `TEMPLATE.md`, each checked with that template and `.agent/schemas/reflection.v1.yaml` and no decision source: 82 files at plan time. |
| `STAGE_LOGS` | The decision logs read by `stage-log-survey.py`. These are every plan's fenced `decision_log`, every handoff's `## Decision Log` and every issue's `enrichment.decision_log` and every grouping's §8 rows (groupings added after R1, CRO-P2). At the R1 recheck correction that is 278 sources, 10 of them groupings, and 1,242 entries (`C:/Temp/av-kit/cro/stage-log-survey-r1-1.txt`; the 18 more are Session 87's plan, filled since R1); the first plan-time receipt, without groupings, read 264 and 1,101. |

### The validator port

`UPSTREAM_A` and `UPSTREAM_E` are ported function by function, not with `patch`, because upstream's validator has a stage framework (`_stage_*`) that av-kit doesn't carry and the line offsets differ by hundreds of lines. Rows 3 to 5 each own one part.

**Row 3: the field check and the removal.**

- **New:** `_NON_TEXT_SCALAR` and `decision_field_text`, copied from `UPSTREAM_A`. A plain `yes`, `no`, `on`, `off`, `true`, `false`, `null`, `~` or a number is not text.
- **The one deviation from `UPSTREAM_A` (D-831, amended after plan review R1, CRO-P1).** Upstream's quoted branch calls `_unquote(raw)` on the whole raw value. For `"pending Mat" # awaiting reply` that keeps the quotes, so the pending test misses; for `"" # not recorded` it returns the two quote characters as text. Both close with no ruling recorded.
  - A new `_quoted_scalar_text(raw)` matches one whole double- or single-quoted scalar, then optional blanks and an optional `# comment`: `^(?:"(?P<double>(?:[^"\\]|\\.)*)"|'(?P<single>(?:[^']|'')*)')[ \t]*(?:#.*)?$`. It returns the text inside the quotes. A single-quoted body is literal: `''` is read as `'` and a backslash is a backslash (YAML 1.2.2 §7.3.2). Anything else that starts with a quote, such as text after the closing quote or an unterminated quote, gives `None`.
  - A double-quoted body is decoded as YAML 1.2.2 §5.7 does, before the blank and pending tests (amended after the R1 recheck, CRO-R1-1). A new `DQ_ESCAPE_VALUES = dict(zip(DQ_ESCAPES, "\0\a\b\t\t\n\v\f\r\x1b \"/\\\x85\xa0" + chr(0x2028) + chr(0x2029)))` gives what each of the validator's existing `DQ_ESCAPES` (`:858`) stands for, and `\x`, `\u` and `\U` take the hex digits `DQ_HEX_ESCAPES` (`:859`) counts. An escape outside those tables, malformed hex digits or a code point above U+10FFFF gives `None`. `check_yaml_subset`'s `_scan_double_quoted` (`:862`) already refuses those spellings before any field is read, so this is a second line, not a new refusal.
  - This is the form `tools/issue_triage/model.py`'s `_represent_str` (`:336`) writes: a value that is `"\n"`, ends `"\n\n"` or holds U+0085, U+2028 or U+2029 is double-quoted, and PyYAML spells those characters `\n`, `\N`, `\L`, `\P`, a non-printable one as `\a`, `\e`, `\0`, `\xXX`, `\uXXXX` or `\UXXXXXXXX`, and `"` and `\` as `\"` and `\\`. Its width is `10**9`, so a double-quoted value never folds onto a second line. Every such value, saved by the real writer, decodes back to itself (`C:/Temp/av-kit/cro/escape-probe-r1-1.txt`).
  - `decision_field_text`'s quoted branch calls it instead of `_unquote`, and returns `None` when the result is `None` or blank. A `#` inside the quotes stays text: `chosen: "Keep # 3"` is read as `Keep # 3`.
  - `_unquote` itself is unchanged; its other callers (`:1159`, `:1307`, `:1729`) read keys, IDs and frontmatter.
  - The source is YAML 1.2.2 §6.6: a comment starts at a `#` that follows white space, outside a quoted scalar. `port-check.py` expects the deviation, so a later sync sees it.
- **`grouping_decisions`** (`:1509`) gains `grouping_row_problems(cells) -> list[str]`, an av-kit addition that upstream lacks (D-829, amended after R1, CRO-P2). After the Resolution check, it refuses the row's first problem with one of these messages:
  - `{label} row {id} has a blank {column} cell; each grouping row states the question and the reasoning, and a ruled row its choice (human-decision-protocol.md §6).`
  - `{label} row {id} is still pending; record the ruling in its Chosen cell before closeout, or set its Resolution to open (human-decision-protocol.md §6).`

  The fixture `_DECISION_GROUPING` already passes: D-7 is ruled and stated in full, and D-8 is `open` with Chosen `—`.
- **`decision_entries`** gains `FIELD_CHECK` with upstream's two messages, verbatim:
  - `{label} decision_log entry {id} has a blank or non-text {field}; each stage-log entry states the question, the choice and the reasoning (human-decision-protocol.md §6).`
  - `{label} decision_log entry {id} is still pending; record the ruling in \`chosen\` before closeout (human-decision-protocol.md §6).`
- **Removed:** `DECISION_RESOLUTIONS` (`:752`), `DECISIONS_LOG_HEADERS` (`:754`) and `reflection_decision_rows` (`:1778`).
- **`GROUPING_DECISION_HEADERS`** (`:766`) becomes upstream's literal list of seven columns (no `Stage`), with upstream's comment. `GROUPING_RESOLUTIONS` (`:767`) is unchanged.
- **`check_decisions_log(sources, issues)`** no longer takes the reflection text. It calls `decision_sources(sources, issues)`, which applies the field check and the stage check across sources, and returns `f"{len(expected)} stage-log decision(s) read, each stated in full"`. Its docstring follows upstream and cites §6 record-once. The repeatable `issues: Sequence[str]` stays (D-828). Its call site (`:1978`) passes no reflection text.
- **`refuse_repeated_ids`** (`:1310`) stays. Its docstring and message (`:1323`) drop "matched to a reflection row" (D-827). The message becomes `{label} repeats decision ID {decision_id}; each decision needs its own ID, so that its one record is the ruling and the stage check across sources reads it (human-decision-protocol.md §6).`
- **Fixtures:** in `_DECISION_KNOWN_ISSUES` and `_DECISION_KNOWN_ISSUES_INDENTED`, D-9 gains `question: "Other issue?"`, `chosen: "Keep"` and `reasoning: "two-way door"`, and D-3 gains `chosen: "New MEU"`. Every fixture the selftest reads as a source must now pass `FIELD_CHECK`. `_DECISIONS_LOG_ROWS` stays, as it does upstream, because the table form is still a valid reflection body.

**Row 4: the example check and the wording.**

- **`check_reflection`** ends with `EXAMPLE_CHECK`, upstream's code verbatim. Its message is `reflection {path} Decisions Log still holds the template example; list the reversible choices with links, or write None. (human-decision-protocol.md §6).`
- **`_GOOD_REFLECTION_TEMPLATE`**'s Decisions Log becomes the link-list example `- _{the choice in plain words}_ — [D-1](_{path to the stage log}_)` (D-839). `docs/execution/reflections/TEMPLATE.md` is not touched (Session 85).
- **Wording (D-833).** No line above the selftest fixtures (the first `_GOOD_REFLECTION_TEMPLATE =` line) may say `reconcil`, so each of the 14 such lines changes. At plan time they are `:385, 1170, 1210, 1313, 1366, 1384, 1425, 1462, 1505, 1573, 1596, 1792, 1870, 2046`. The phrase becomes "read", "checked" or "stage check", whichever is true at that line.
- **The module docstring** says `plus: every decision recorded in the plan, handoff or issue is stated in full, and the reflection's Decisions Log holds no template example`. **The usage text** (`:2046`) says `--decision-source/--decision-issue read the stage logs of a closeout and check the reflection's Decisions Log; pass --reflection PATH.`
- **The `--decision-source` help** (`:5620-5629`) no longer says the decisions `must each have a row in the reflection's Decisions Log`. Upstream left this line stale, which Zorivest's HD1 implementation review noted (`P:/zorivest/.agent/context/handoffs/2026-11-07-hd1-human-decision-protocol-implementation-critical-review.md:27`). It now says the file's `decision_log` entries are read and each must be stated in full and not pending.

**Row 5: the repository boundary (`UPSTREAM_E`).**

- **`project_root`** (`:1740`) gains `if (ancestor / ".git").exists(): return plan.parent` after the `.agent` test inside the loop, and upstream's docstring.
- **Selftest fixtures:** the four temp folders that upstream marks (`basename`, `declared-handoff`, `fenced-heading` and `tilde-heading`, wherever av-kit builds them) gain a `.git` folder.
- **New arms:** the three `grouping-declared-repo-boundary-*` arms, with the wants that `a73d6df` gives them (row 6's list).

**Line endings.** `VALIDATOR` is read and written as bytes with `newline=""`, and stays CRLF (AC-16).

### The av-kit-only checks

These are the decision checks av-kit has and `UPSTREAM_A` does not (function and arm diff, `C:/Temp/av-kit/cro/upstream-a73d6df.py` against `VALIDATOR`), and what happens to each (D-829).

| Check | Where | Disposition |
|---|---|---|
| A decision ID repeated in one source (`repeats decision ID`) | `refuse_repeated_ids` `:1310`; arms `grouping-repeated-id-refused`, `handoff-decision-log-repeated-id-refused` | **Kept.** The docstring and message are reworded (D-827). The arms are unchanged. |
| Repeatable `--decision-issue`; an absent issue refused beside a present one; a repeated ID is `USAGE` | `run`, `issue_decision_log` `:1480`; arm `decision-issue-absent-beside-present-refused`; `test_closeout_register_grammar.py` AC-5, AC-6 | **Kept** (D-828, Session 49b D-283). |
| Two issues each read | Arms `decision-issue-repeated-reconciled-ok` and `decision-issue-repeated-first-issue-read` | **Kept, rewritten.** Each keeps its label and want. The `must_say` of `…-reconciled-ok` changes from `3 recorded decision(s)` to `3 stage-log decision(s) read`. `…-first-issue-read` now reads a known-issues text whose OTHER-ISSUE D-9 `chosen` is `pending Mat's ruling`, and its `must_say` changes from `missing decision D-9 (triage, recorded in issue OTHER-ISSUE)` to `issue OTHER-ISSUE decision_log entry D-9 is still pending`. |
| The reflection table's grammar: eight headers, the Resolution set, a duplicate row, a two-column table | `reflection_decision_rows`, `DECISION_RESOLUTIONS`, `DECISIONS_LOG_HEADERS` | **Removed** with the table (D-826). |
| The known-issues bounded grammar | Session 49b; `test_closeout_register_grammar.py` AC-1 to AC-3 | **Kept.** The fixtures gain the fields `FIELD_CHECK` reads; the assertions are unchanged. |
| A quoted field followed by a `# comment` | `decision_field_text` through `_quoted_scalar_text` | **Added, av-kit only** (D-831, amended after R1, CRO-P1). Upstream copies the `_unquote` defect; `port-check.py` expects the deviation. |
| A double-quoted field's escapes, such as `reasoning: "\n"` from the register's writer | `_quoted_scalar_text` through `DQ_ESCAPE_VALUES` and `DQ_HEX_ESCAPES` | **Added, av-kit only** (D-831, amended after the R1 recheck, CRO-R1-1). `port-check.py` runs the function alone on `QUOTED_PROBES`. |
| The content of a grouping §8 row | `grouping_decisions` through `grouping_row_problems` | **Added, av-kit only** (D-829, amended after R1, CRO-P2). With the reflection rows gone, nothing else reads what a grouping row says. |

### Selftest arm changes

`selftest-arms-check.py` holds these lists as data. They replace the "a selftest must not shrink" rule for this one port (D-836). At plan time there are 219 arms, 67 of which want `0/OK`. After the port there are 231 arms, 96 of which want `0/OK`: 220 and 93 from `UPSTREAM_A` and `UPSTREAM_E`, plus the six av-kit arms added after plan review R1 and the five added after the R1 recheck.

- **Removed (14), with `UPSTREAM_A`:**
  - `decision-blank-reasoning-refused`
  - `decision-duplicate-id-refused`
  - `decision-indented-fence-reconciled`
  - `decision-indented-root-reconciled`
  - `decision-invalid-resolution-refused`
  - `decision-issue-indented-4-missing-refused`
  - `decision-issue-missing-from-reflection-refused`
  - `decision-missing-from-reflection-refused`
  - `decision-stage-before-id-refused`
  - `decision-stage-mismatch-refused`
  - `decision-two-column-table-refused`
  - `grouping-decision-missing-refused`
  - `grouping-fenced-heading-declared-unreconciled-refused`
  - `handoff-indented-root-reconciled`
- **Flipped to `0/OK` (16).** Each refused only because the reflection lacked a row:
  - `decision-log-inline-comment-read`
  - `decision-quoted-root-key-read`
  - `decision-tilde-yaml-fence-read`
  - `enrichment-inline-comment-read`
  - `issues-inline-comment-read`
  - `grouping-any-filename-read`
  - `grouping-declared-basename-beside-plan-read`
  - `grouping-declared-root-resolved-read`
  - `grouping-fenced-example-before-real-section-read`
  - `grouping-tilde-fenced-example-before-real-section-read`
  - `grouping-named-handoff-read-as-handoff`
  - `grouping-named-plan-read-as-plan`
  - `grouping-plan-source-null-read-as-grouping`
  - `plan-commented-heading-read-as-plan`
  - `plan-fenced-heading-read-as-plan`
  - `plan-tilde-fenced-heading-read-as-plan`

  Each one's own `must_say` is kept where it names the source read, and dropped where it named the missing row.
- **Added (26).**
  - From `UPSTREAM_A`:
    - `decision-blank-reasoning-in-log-refused` (1/REFUSE)
    - `decision-block-scalar-reasoning-ok` (0/OK)
    - `decision-indented-fence-read` (0/OK)
    - `decision-indented-root-read` (0/OK)
    - `decision-non-text-chosen-refused` (1/REFUSE)
    - `decision-pending-chosen-refused` (1/REFUSE, `must_say` `is still pending`)
    - `decision-stage-before-id-read` (0/OK)
    - `grouping-decisions-read` (0/OK)
    - `grouping-fenced-heading-declared-read` (0/OK)
    - `handoff-indented-root-read` (0/OK)
    - `reflection-decisions-log-example-refused` (1/REFUSE)
    - `reflection-decisions-log-link-list-ok` (0/OK)
  - From `UPSTREAM_E`, with `a73d6df`'s wants:
    - `grouping-declared-repo-boundary-read` (0/OK)
    - `grouping-declared-repo-boundary-gitfile-read` (0/OK)
    - `grouping-declared-repo-boundary-outer-decoy-refused` (1/REFUSE, `declares grouping_source`)
  - av-kit only, added after plan review R1 (D-831 and D-829, amended). Each writes its own plan, or the plan and `_DECISION_GROUPING` with one cell changed, and a reflection whose Decisions Log is `None.`:
    - `decision-commented-pending-chosen-refused` (1/REFUSE, `is still pending`): `chosen: "pending Mat" # awaiting reply`
    - `decision-commented-empty-chosen-refused` (1/REFUSE, `blank or non-text chosen`): `chosen: "" # not recorded`
    - `decision-quoted-hash-text-ok` (0/OK): `chosen: "Keep # 3"`
    - `grouping-blank-chosen-refused` (1/REFUSE, `has a blank Chosen cell`): D-7's Chosen is `—`
    - `grouping-pending-chosen-refused` (1/REFUSE, `is still pending`): D-7's Chosen is `pending Mat`
    - `grouping-open-row-read` (0/OK): `_DECISION_GROUPING` as it is, whose D-8 is `open` with Chosen `—`
  - av-kit only, added after the R1 recheck (D-831, amended; CRO-R1-1). Each writes its own plan with one double-quoted value, and a reflection whose Decisions Log is `None.`:
    - `decision-escaped-newline-reasoning-refused` (1/REFUSE, `blank or non-text reasoning`): `reasoning: "\n"`, the register writer's spelling
    - `decision-escaped-pending-chosen-refused` (1/REFUSE, `is still pending`): `chosen: "\u0070ending Mat"`
    - `decision-escaped-blank-question-refused` (1/REFUSE, `blank or non-text question`): `question: "\t"`
    - `decision-escaped-blank-chosen-refused` (1/REFUSE, `blank or non-text chosen`): `chosen: "\x20\L"`
    - `decision-escaped-text-ok` (0/OK): `chosen: "say \"x\" \\ \x7Bid\x7D"` and `reasoning: 'a \n stays as written'`
- **Rewritten (2):** `decision-issue-repeated-reconciled-ok` and `decision-issue-repeated-first-issue-read`, as in §The av-kit-only checks. Their labels sit below the fixture line, so the `reconcil` rule doesn't reach them.

### Test changes

- **New: `tests/tooling/test_closeout_record_once.py`** (LF). It holds AC-1 to AC-4 and AC-6 to AC-10, named `test_ac_<n>_…`.
  - CLI tests run `VALIDATOR` by subprocess with `cwd=ROOT`, the pattern of `test_closeout_register_grammar.py:208`. Each test writes its own plan, handoff, grouping and known-issues text under `tmp_path`.
  - Every CLI test whose plan declares `grouping_source` creates `tmp_path/.agent/` and `tmp_path/.git/`. The root is then `tmp_path` both before and after the port, under any temp folder.
  - AC-9 imports `VALIDATOR` and calls `project_root` on folders it builds.
  - AC-2 to AC-4 carry the R1 cases, each through the real CLI with a reflection that says `None.`:
    - CRO-P1: a quoted value followed by a `# comment`, as a pending `chosen` and as an empty `chosen`, `question` and `reasoning`; and `chosen: "Keep # 3"`, which passes.
    - CRO-P2: a grouping row whose Chosen is blank, and one whose Chosen is `pending Mat`, on a ruled row; a blank Question and a blank Reasoning; and an `open` row with Chosen `—`, which passes.
    - CRO-R1-1 (the R1 recheck): an issue whose `enrichment.decision_log` reasoning is `"\n"`, written by `model.save` itself (the `saved` pattern of `test_closeout_register_grammar.py:57`) and read through `--decision-issue`; a plan `chosen: "\u0070ending Mat"`; a plan `question: "\t"` and `chosen: "\x20\L"`; and `chosen: "say \"x\" \x7Bid\x7D"` with `reasoning: 'a \n stays as written'`, which passes.
    - In Red, today's validator refuses each closeout because the reflection lacks the row. The tests assert the new message (`is still pending`, `blank or non-text …`, `has a blank … cell`) or exit 0, so each Red fails by assertion.
  - No test touches `decision_field_text`, `_NON_TEXT_SCALAR`, `_quoted_scalar_text` or `grouping_row_problems`. A Red failure is then always an assertion (`red-check.py`).
- **Changed: `tests/tooling/test_closeout_register_grammar.py`** (CRLF, 267 lines). These changes make up AC-5.
  - `test_ac_1_nested_sequences_pass_the_grammar_and_read`: GRAMMAR-A D-1 gains `chosen` and `reasoning`; D-2 gains `question`, `chosen` and `reasoning`; GRAMMAR-B D-3 gains `question` and `reasoning`. The assertions are unchanged.
  - `test_ac_2_edge_string_passes_the_grammar`: the edge value moves from `reasoning` to an extra key `detail`, and plain `question`, `chosen` and `reasoning` are added. An edge string such as `"\n"` would otherwise be refused as blank, which is not what this test is about.
  - `run_check` gains a `known_issues` text parameter, which defaults to `v._DECISION_KNOWN_ISSUES`.
  - `test_ac_4_every_named_issue_is_read` replaces D-9's `chosen: "Keep"` with `chosen: "pending Mat's ruling"`. It asserts that the replace changed the text, then expects exit 1 with `OTHER-ISSUE` and `still pending` in stdout.
  - `test_ac_7_every_decision_present_passes` expects `3 stage-log decision(s) read` for the two issues. For one issue it expects `2 stage-log decision(s) read, each stated in full`.
  - `test_ac_5` and `test_ac_6` are unchanged.

### Closing the known issue

Row 7 resolves `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` (`.agent/context/known-issues.yaml:3362`, open, LF) with the tooling (D-834). Nothing is hand-edited, and `known-issues.md` is only rendered.

1. The coordinator writes `C:/Temp/av-kit/cro/issue-resolve-set.json`. It is keyed by the issue id and holds only these keys:
   - `status: "resolved"`
   - `verification`, with `last_checked` set to row 7's date, `method` naming row 6's receipts `cro-selftest-default-tmp.txt` and `cro-tooling.txt`, and `result` quoting their `0 failure(s)` and `passed` lines
   - `resolution_path`, which names this plan, Session 84 and `ec3857a`
2. `issue-resolve.py --issue CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR --set-file … --expect-sha256 <row 0's known-issues.yaml hash>` writes the register. It refuses any key outside `status`, `verification` and `resolution_path`, any other issue's change, and a register whose hash moved since row 0 (S4).
3. `tools/issue_triage.py render`, then `render --check`.

The issue's `root_cause` and `notes` are not touched. They hold a full home path that this plan never copies; the plan names that folder only as "the home folder". The two references at `:4298` and `:4317` are in other issues' fields and stay as written.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| A stage-log `decision_log` entry (plan, handoff, issue) | `decision_entries` in `VALIDATOR` | `id` and `stage` as today. `question`, `chosen` and `reasoning` are each non-blank text (`decision_field_text`), and `chosen` does not start with `pending` | Other keys (`resolution`, `class`, `precedents`, `research`, `human_message_reference`, `detail`) are read as today and not checked here |
| A grouping §8 row | `grouping_decisions` (`grouping_row_problems`) | The seven `GROUPING_DECISION_HEADERS` and Resolution in `GROUPING_RESOLUTIONS`, as today. Added after R1 (D-829): Question and Reasoning are non-blank; on an `autonomous` or `human` row, Chosen is non-blank and does not start with `pending` | Unchanged |
| The reflection's `### Decisions Log` | `check_reflection` | Any body without `_{`, including `None.`, a link list or the old table | No row-level check |
| `--decision-source`, `--decision-issue` | `run` | As today; `--decision-issue` repeatable, a repeated ID is `USAGE` | Unchanged |

### Acceptance Criteria

The new tests are in `tests/tooling/test_closeout_record_once.py`, named `test_ac_<n>_…`. AC-5 is the changed `test_closeout_register_grammar.py`. AC-11 to AC-18 are row and gate checks.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-1 | integration | A plan decision stated in full, with `reasoning` as a `\|` block scalar, is read. The CLI exits 0 with a reflection that lists it in the table form | Spec (`UPSTREAM_A` arm `decision-block-scalar-reasoning-ok`) | Guard: it passes in Red. AC-2 to AC-4 are its negatives |
| AC-2 | integration | A choice that starts with `pending` exits 1 with `is still pending`:<br>• a plan, handoff or issue entry whose `chosen` is `pending`, `Pending Mat` or `pending: yes` (`decision_log entry D-<n> is still pending`)<br>• a quoted `chosen` followed by a comment: `chosen: "pending Mat" # awaiting reply` (R1, CRO-P1)<br>• an escaped pending choice: `chosen: "\u0070ending Mat"` (R1 recheck, CRO-R1-1; arm `decision-escaped-pending-chosen-refused`)<br>• a grouping row with Resolution `human` or `autonomous` whose Chosen is `pending Mat` (`row D-<n> is still pending`; R1, CRO-P2) | Spec (`UPSTREAM_A` arm `decision-pending-chosen-refused`); Local Canon (D-829 and D-831, amended after R1; arms `decision-commented-pending-chosen-refused`, `grouping-pending-chosen-refused`) | `chosen: "Keep the pending queue"`, `chosen: "Pendingly"` and `chosen: "Keep # 3"` exit 0 (D-831). A grouping row with Resolution `open` and Chosen `—` exits 0 (D-829) |
| AC-3 | integration | A blank or non-text choice or question exits 1:<br>• a `chosen` or `question` that is `3`, `true`, `null`, `no`, `""`, `[a, b]` or missing (`has a blank or non-text chosen`, or `question`)<br>• `chosen: "" # not recorded` and `question: "" # not asked` (R1, CRO-P1)<br>• escaped blanks: `question: "\t"` and `chosen: "\x20\L"` (R1 recheck, CRO-R1-1; arms `decision-escaped-blank-question-refused`, `decision-escaped-blank-chosen-refused`)<br>• a ruled grouping row whose Chosen is empty or `—` (`has a blank Chosen cell`), and one whose Question is empty (`has a blank Question cell`; R1, CRO-P2) | Spec (`UPSTREAM_A` arm `decision-non-text-chosen-refused`; Zorivest AC-942.4); Local Canon (D-829 and D-831, amended after R1; arms `decision-commented-empty-chosen-refused`, `grouping-blank-chosen-refused`) | `chosen: "3 rounds"` exits 0. `chosen: "say \"x\" \x7Bid\x7D"` exits 0 (`decision-escaped-text-ok`). A grouping Chosen of `49` exits 0, since a cell has no type rule |
| AC-4 | integration | A blank reasoning exits 1:<br>• a `reasoning` that is `""`, an empty value, a `\|` block with only blank lines, or `"" # later` (`has a blank or non-text reasoning`; the last is R1, CRO-P1)<br>• an issue's `reasoning: "\n"` as `model.save` writes a reasoning that is only a newline, read through `--decision-issue` (R1 recheck, CRO-R1-1; arm `decision-escaped-newline-reasoning-refused`)<br>• a grouping row, ruled or `open`, whose Reasoning cell is empty (`has a blank Reasoning cell`; R1, CRO-P2) | Spec (`UPSTREAM_A` arm `decision-blank-reasoning-in-log-refused`); Local Canon (D-829 and D-831, amended after R1 and its recheck) | A one-word `reasoning` exits 0, and so does `reasoning: 'a \n stays as written'`, since a single-quoted body has no escapes |
| AC-5 | integration | The repeatable `--decision-issue` (`test_closeout_register_grammar.py` `test_ac_4` to `test_ac_7`):<br>• a pending D-9 is refused, naming `OTHER-ISSUE`<br>• two issues give `3 stage-log decision(s) read`<br>• one issue gives `2 stage-log decision(s) read, each stated in full`<br>• a repeated ID is `USAGE`, exit 2<br>• an absent issue is refused beside a present one | Local Canon (D-283, D-828) | `test_ac_4` (pending), `test_ac_5` (repeat) and `test_ac_6` (absent) |
| AC-6 | integration | `EXAMPLE_CHECK`, with no decision source:<br>• a reflection whose Decisions Log holds `- _{the choice in plain words}_ — [D-1](_{path to the stage log}_)` exits 1 with `still holds the template example`<br>• a link list (`- Kept the table — [D-1](docs/x.md)`) exits 0<br>• `None.` exits 0 | Spec (`UPSTREAM_A` arms `reflection-decisions-log-example-refused`, `reflection-decisions-log-link-list-ok`); the brief's link-list requirement | The example line is the negative |
| AC-7 | integration | A reflection whose Decisions Log is `None.`, and one with a link list, each exit 0 while all four sources record decisions:<br>• the plan<br>• the handoff<br>• the plan's declared grouping<br>• an issue named by `--decision-issue` | Human-approved (D-826) | With the same reflection, a pending `chosen` in the plan exits 1 |
| AC-8 | integration | The kept checks still refuse, exit 1:<br>• one ID with two stages across sources (`one decision has one stage`)<br>• one ID twice in a plan, a handoff, a grouping or an issue (`repeats decision ID`)<br>• a plan declaring `grouping_source` without that file among the sources (`declares grouping_source`)<br>• an `UNFILLED` marker<br>• a missing template section | Local Canon (D-827, D-829) | Guard: it passes in Red, and each case is itself a negative |
| AC-9 | unit | `project_root`, parametrized:<br>• an outer `.agent` above a folder with a `.git` folder gives `plan.parent`<br>• the same with a `.git` file (`gitdir: …`) gives `plan.parent`<br>• `.agent` and `.git` in one repo root with the plan two levels down gives that root<br>• `.agent` and `.git` in the plan's own folder give that folder | Spec (`UPSTREAM_E`) | The two outer cases return the outer folder today |
| AC-10 | integration | A plan inside a `.git` folder declares `grouping_source: "demo.md"`, and the outer `.agent` folder's `demo.md` is passed as a source. The CLI exits 1 with `declares grouping_source` | Spec (`UPSTREAM_E` arm `grouping-declared-repo-boundary-outer-decoy-refused`) | The repo's own `demo.md` exits 0 |
| AC-11 | unit | `VALIDATOR --selftest` with `TMP` and `TEMP` at `C:/Temp/av-kit/cro/tmp` exits 0 with 0 failures. `selftest-arms-check.py --before selftest-arms-before.txt` accepts the receipt: 231 arms, 96 wanting `0/OK`, and the §Selftest arm changes exactly | Human-approved (D-826); Local Canon (D-836) | `selftest-arms-check.py --selftest` refuses a removed arm still present, a missing prior arm, a changed want and an unlisted new arm |
| AC-12 | integration | Under the user's own temp folder, which has the home folder's `.agent` above it, the selftest exits 0 with `0 failure(s)`, and `pytest tests/tooling/test_framework_adoption.py -k test_evidence_contract_real_cli_selftests` passes | Local Canon (`CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR`; D-822, D-830) | Row 0's default-temp receipt shows 5 failures |
| AC-13 | integration | `reflections-check.py`: no reflection in `REFLECTION_SET` that the base validator accepts is refused by the ported one, and none is refused for the template example | Local Canon (the brief: old reflections still pass) | `reflections-check.py --selftest` flags an OK-to-REFUSE pair and an example refusal |
| AC-14 | integration | `stage-log-survey.py --compare` against row 0's receipt: the ported `decision_field_text` and `grouping_row_problems` refuse the same set of entries and grouping rows that row 0's simulation predicted. At the R1 recheck correction that is 29 problem entries, 2 of them open, and 0 grouping rows across 10 groupings (`C:/Temp/av-kit/cro/stage-log-survey-r1-1.txt`) | Local Canon (`FIELD_CHECK` predicted at plan time; D-829 and D-831, amended after R1) | `stage-log-survey.py --selftest` finds the planted commented-pending, commented-empty, escaped-pending, escaped-blank and grouping rows and the `model.save`-written `"\n"` reasoning, passes `Keep # 3`, the escaped text, the Chosen `49` and the `open` row, and flags an added and a missing problem line |
| AC-15 | unit | `port-check.py` accepts `PORT_SHAPE`:<br>• the three removed names are gone, and the five new names exist: `decision_field_text`, `_NON_TEXT_SCALAR`, `_quoted_scalar_text`, `DQ_ESCAPE_VALUES` and `grouping_row_problems`<br>• the av-kit deviation is expected, not flagged: `decision_field_text` calls `_quoted_scalar_text(` and never `_unquote(`, and `grouping_decisions` calls `grouping_row_problems(` (R1)<br>• `_quoted_scalar_text`, run alone with only the constants it reads, gives every `QUOTED_PROBES` answer: `"\n"` is a newline, `"\u0070ending Mat"` is `pending Mat`, `"\U0001F600"` one character, a single-quoted `\n` two characters, a quoted `#` text, and `"\q"`, `"\u00G0"` and `"a" b` `None` (R1 recheck, CRO-R1-1)<br>• `GROUPING_DECISION_HEADERS` is the literal list and `GROUPING_RESOLUTIONS` is unchanged<br>• `check_decisions_log` takes `(sources, issues)`<br>• `project_root` tests `.git`<br>• no `reconcil` above the fixtures; no `must each have a row` or `matched to a reflection row` anywhere<br>• the docstring holds both new phrases | Spec (`UPSTREAM_A`, `UPSTREAM_E`); Local Canon (D-827, D-828, D-833) | `port-check.py --selftest` refuses a pre-port source on each point, a `decision_field_text` that keeps `_unquote`, a `_quoted_scalar_text` that returns the raw escape spelling or skips the hex escapes, and a `grouping_decisions` that skips the row check. The R1 recheck run reports 18 problems (`C:/Temp/av-kit/cro/port-check-plan-time-r1-1.txt`) |
| AC-16 | unit | Line endings:<br>• `VALIDATOR` and `test_closeout_register_grammar.py` have only CRLF<br>• `test_closeout_record_once.py`, `known-issues.yaml` and `known-issues.md` have no CRLF | Local Canon (the brief: keep each file's line endings) | `port-check.py --selftest` fixtures |
| AC-17 | integration | `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is `resolved`, with `verification` and `resolution_path`. `issue-resolve.py` reports no other parsed difference. `issue_triage.py render --check` exits 0 after `render` | Local Canon (D-822, D-834) | `issue-resolve.py` refuses a key outside its three, another issue, and a wrong `--expect-sha256` |
| AC-18 | static | `ruff check tools/validate_closeout_artifacts.py tests/tooling/` is clean (clean at plan time: `C:/Temp/av-kit/cro/ruff-plan-time.txt`). The full Python suite fails no test that row 0's receipt shows passing | Local Canon (D-837) | — |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| What "stated in full" means, and the pending prefix | Spec | `UPSTREAM_A` `decision_field_text`, `decision_entries` |
| The template-example test | Spec | `UPSTREAM_A` `check_reflection` |
| Which checks are removed | Human-approved | D-826 (default acceptance of the brief) |
| The av-kit-only checks | Local Canon | D-827, D-828, D-829 |
| Where the root search stops | Spec | `UPSTREAM_E` |
| The `--decision-source` help wording upstream left stale | Local Canon | D-833 |
| A quoted value with a trailing `# comment` | Local Canon (a sourced deviation) | D-831, amended after R1: YAML 1.2.2 §6.6; upstream's `_unquote` call is the defect (CRO-P1) |
| A double-quoted value's escapes | Spec (YAML 1.2.2 §5.7, §7.3) and Local Canon | D-831, amended after the R1 recheck: the validator's own `DQ_ESCAPES` and `DQ_HEX_ESCAPES`; `model.py:336` writes `"\n"` (CRO-R1-1) |
| What a grouping row must state, and an `open` row | Local Canon | D-829, amended after R1: protocol §6's Grouping row; D-101 stayed `open` through Sessions 40 to 42; upstream reads `open` rows |
| Old reflections and stage logs | Local Canon | The plan-time receipts: 0 reflection regressions, 29 predicted stage-log problems, 0 grouping rows refused |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|---|---------|
| `tools/validate_closeout_artifacts.py` | modify | CRLF, kept | The port (§The validator port) and the selftest arm changes |
| `tests/tooling/test_closeout_record_once.py` | new | LF | AC-1 to AC-4, AC-6 to AC-10 |
| `tests/tooling/test_closeout_register_grammar.py` | modify | CRLF, kept | AC-5 (§Test changes) |
| `.agent/context/known-issues.yaml` | modify, by `issue-resolve.py` only | LF, kept | The one issue's `status`, `verification` and `resolution_path` |
| `.agent/context/known-issues.md` | regenerate, by `issue_triage.py render` only | LF, kept | The issue's row |

`known-issues.yaml`, `known-issues.md` and `current-focus.md` already carry uncommitted hunks from the triage workstream (`baseline-dirty.txt`). This session changes only the hunks named above.

### Project files

- **Plan-local scripts** (all in this plan folder):
  - `baseline.ps1`
  - `red-check.py`
  - `identity.py`
  - `selftest-arms-check.py`
  - `stage-log-survey.py`
  - `reflections-check.py`
  - `port-check.py`
  - `issue-resolve.py`
  - `session-gate.ps1`, written at H1-2
- **State:**
  - `docs/execution/metrics.md`
  - `.agent/context/current-focus.md`
  - the handoff
  - the rolling reviews
  - the reflection
  - `C:/Temp/av-kit/session-85-prompt.md`, outside the repository

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| `human-decision-protocol.md`, `docs/execution/reflections/TEMPLATE.md`, the plan and task templates, `AGENTS.md`, the workflows | deferred | — | Session 85 (`hdp-v2-protocol`) owns them (grouping D-821; D-835) |
| `a73d6df`'s expert pass and the hand-over parts | deferred | — | Session 86 (grouping D-821) |
| Upstream's `_stage_*` closeout framework and other upstream-only validator functions | out-of-scope | — | Not part of record-once; av-kit's validator has no stage framework (S2) |
| `core/tools/tests/test_validate_closeout_stages.py` | out-of-scope | — | Its cases are AC-1 to AC-4 and AC-6 here, in av-kit's `tests/tooling` (D-832) |
| D-246 and D-251 pending in `2026-11-04-rc2-ffmpeg-uninstall` | out-of-scope | — | D-838: that plan's own closeout records the rulings |
| The `MEU-72` and `MEU-74` handoffs' Decision Log shape refusal | out-of-scope | — | Closed sessions; the base validator refuses them the same way (survey `other-refusal`) |

## BUILD_PLAN.md Audit

This project adds no build-plan section and changes no MEU, so `docs/BUILD_PLAN.md` and `meu-status.yaml` don't change. `meu_status.py stats` on the work tree, which holds the triage workstream's uncommitted edits, reports 153 MEUs, 143 complete (`C:/Temp/av-kit/cro/meu-stats.txt`), and `render --check` passes (`C:/Temp/av-kit/cro/meu-render-check-plan-time.txt`). H1-3 proves the hub is a no-op:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/cro/cro-render-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/cro/cro-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following, fail-fast except where noted:

1. Records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`.
2. Writes `baseline-content.txt`: the SHA-256 and line-ending counts of the following files:
   - `VALIDATOR`
   - the two test files that exist
   - `known-issues.yaml` and `known-issues.md`

   `VALIDATOR`, `test_closeout_register_grammar.py` and `test_framework_adoption.py` must equal `HEAD` once CRLF is read as LF, or it exits 10 (S4). The two register files are dirty from the triage workstream, so only their hashes are recorded. Row 7 passes the `known-issues.yaml` hash to `issue-resolve.py --expect-sha256`. It also writes `baseline-dirty-content.txt`, the SHA-256 of every `baseline-dirty.txt` path (or `absent`), so the gate's `scope-paths` step can show that each one kept its content (S4; added after R1, Q8).
3. Copies `VALIDATOR` to `C:/Temp/av-kit/cro/base/validate_closeout_artifacts.py`.
4. Runs the selftest with `TMP` and `TEMP` at `C:/Temp/av-kit/cro/tmp` (`cro-base-selftest.txt`), and writes the sorted arm names to `selftest-arms-before.txt`. Anything but 219 arms exits 11.
5. Runs the selftest under the user's own temp (`cro-base-selftest-default-tmp.txt`). This is recorded, not fatal: 5 failures is the known issue.
6. Runs `uv sync --frozen --all-packages` and the base Python suite (`cro-base-py.txt`, `TMP` at `C:/Temp/av-kit/cro/tmp`). The suite's own failures are recorded, not fatal.
7. Runs `issue_triage.py render --check`. A failure is another session's drift (S8).
8. Runs the selftests of `red-check.py`, `identity.py`, `selftest-arms-check.py`, `stage-log-survey.py` and `reflections-check.py`, then the survey (`cro-base-survey.txt`) and the reflections check (`cro-base-reflections.txt`) on the base copy.

Its last line is `baseline: all steps exit 0`.

### 2. Red then Green (rows 1 to 5)

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require test_ac_<n>` matches exactly, and every failure block must be an assertion. Rows 1 and 2 have separate receipts, because both files have a `test_ac_4` and a `test_ac_7`.
- **AC-1 and AC-8 pass in Red by design.** They guard what Green could break. Row 1 requires AC-2, AC-3, AC-4, AC-6, AC-7, AC-9 and AC-10.
- **AC-5 fails in Red** in the two changed grammar tests:
  - `test_ac_4`'s replace finds no `chosen: "Keep"` in today's fixture.
  - `test_ac_7` expects the new summary line.

  Row 2 requires both.
- **Green is split by part:** row 3 (`FIELD_CHECK` and the removal), row 4 (`EXAMPLE_CHECK` and the wording), row 5 (`UPSTREAM_E`, then `port-check.py`). Each Green row runs the ACs its part makes pass.
- **Expectations stay immutable in Green.** `VALIDATOR` and the grammar test keep CRLF. Each is measured with Python bytes and written with `newline=""`.

### 3. Selftest arms (row 6)

Row 6 makes all of §Selftest arm changes in `VALIDATOR`'s selftest. Then it runs three checks:

- The selftest with `TMP` at `C:/Temp/av-kit/cro/tmp` and `selftest-arms-check.py` (AC-11).
- The selftest under the user's own temp, which must print `0 failure(s)` (AC-12).
- `pytest tests/tooling/` under the user's own temp. It runs the selftest again through `test_framework_adoption.py:167-171` (AC-12).

### 4. Closing the known issue (row 7)

This is §Closing the known issue, then `port-check.py` for the register's line endings (AC-16, AC-17).

### 5. Old reflections and stage logs (row 8)

- **`reflections-check.py`** runs `check_reflection` from the base copy and from `VALIDATOR` over `REFLECTION_SET` (AC-13). At plan time, with upstream's example check simulated, 48 reflections pass, 34 are refused by both copies for reasons the port doesn't touch, and 0 regress (`C:/Temp/av-kit/cro/reflections-check-run.txt`).
- **`stage-log-survey.py --compare cro-base-survey.txt`** runs the ported `decision_field_text` over `STAGE_LOGS`. It must list the same problems as row 0's prediction (AC-14). At the R1 recheck correction it finds 29 problem entries in 278 sources (1,242 entries), and 0 grouping rows refused in 10 groupings (`C:/Temp/av-kit/cro/stage-log-survey-r1-1.txt`):
  - 26 with a blank or non-text `chosen`
  - 26 with a blank or non-text `reasoning`
  - 3 still pending

  Only D-246 and D-251 of `2026-11-04-rc2-ffmpeg-uninstall` are in a plan without a reflection (D-838).

  No closed plan, handoff, issue or grouping gains a problem from the R1 corrections or from decoding escapes. The tree holds 17 double-quoted decision fields with an escape, such as `\"`, `\\` and `\x7B`, all in plans and handoffs; each decodes to text (`C:/Temp/av-kit/cro/escape-scan-r2.txt`). Compared with the first plan-time receipt, the R1 recheck survey has 0 differences (`C:/Temp/av-kit/cro/stage-log-survey-r1-1-compare.txt`); Session 87's plan has since been filled, so its `other-refusal` is gone. Compared with the first plan-time receipt, the R1 survey differs only by one `other-refusal`: a placeholder in Session 87's plan, which is still being written (`C:/Temp/av-kit/cro/stage-log-survey-r1-compare.txt`). Row 8 therefore compares with row 0's own `cro-base-survey.txt`, never with a plan-time receipt.

### Session gate (H1-2)

`session-gate.ps1` follows the peer's shape:

- It writes one receipt per step in `C:/Temp/av-kit/cro/`, named `cro-D6-<step>`.
- It is fail-fast, and prints later steps as `not_run`.
- Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `tools-lint` (`ruff check tools/validate_closeout_artifacts.py tests/tooling/`); `py-lint` (`ruff check packages/ tests/`); `task-contract`; `scope-paths`; `port-check`; `red-check-selftest`. `scope-paths` passes when every changed path is in §Files Modified, this plan folder, the closeout artifacts or `baseline-dirty.txt`, and every `baseline-dirty.txt` path outside this scope keeps the hash `baseline-dirty-content.txt` recorded for it at row 0 |
| Targeted | `record-once-tests` (`pytest tests/tooling/test_closeout_record_once.py tests/tooling/test_closeout_register_grammar.py`); `closeout-selftest` with `TMP` elsewhere, then `selftest-arms-check.py`; `closeout-selftest-default-tmp`, which must say `0 failure(s)`; `reflections-check`; `survey-compare`; `issues-render-check` |
| Fresh full | `py-tests` (the full suite, `TMP` at `C:/Temp/av-kit/cro/tmp` as in row 0); `state-render` |
| Skipped, with reason | `py-types`: `pyright packages/`, and nothing under `packages/` changes. `ui-*`: nothing under `ui/` changes. `mcp-*`: no MCP change. `openapi`: no `packages/api` change (H1-4). `build-record`: no build |

`py-tests` excuses only ids that row 0's receipt shows failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | An upstream hunk depends on code av-kit doesn't have (the `_stage_*` framework), and porting it would change behavior beyond record-once and the root search | Stop; bring the hunk and the options to Mat |
| S3 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S4 | Any of these happens:<br>• `HEAD` moves from `baseline.sha`<br>• a path outside `baseline-dirty.txt` and this plan's files changes<br>• a `baseline-dirty.txt` path changes content<br>• `known-issues.yaml`'s hash differs from row 0's at row 7 | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | A selftest arm outside §Selftest arm changes would have to be removed or have its want changed | Stop; that is a behavior change outside D-826. Bring it to Mat |
| S6 | `reflections-check.py` finds a regression, or `stage-log-survey.py --compare` finds a difference | Stop; the port refuses something the plan did not predict |
| S7 | Codex is unavailable or the ledger refuses | Mat |
| S8 | `issue_triage.py render --check` fails at row 0, or fails after row 7 for a reason outside this issue | Stop; it is another session's drift |
| S9 | The default-temp selftest still fails after row 6 | Stop; the known issue is not closed, so row 7 doesn't run |
| S10 | A step would commit, push, merge, release, run a destructive data operation, disclose anything externally or touch credentials | Stop and report; Mat's default acceptance doesn't cover it |

## Decision Log

> [!WARNING]
> **D-826 is the one human-gated decision**, below as a Decision Brief. Mat accepted the defaults in advance ("Run HDP on any decisions that come up and and I approving acceptance of the defaults.", 2026-11-15), so it is recorded with its recommendation as `chosen`. That acceptance does not cover commit, push, merge, release, destructive data operations, external disclosure or credentials (S10).
>
> **D-827 to D-839** passed the obviousness test as two-way choices. The grouping rows D-818, D-821, D-822 and D-824 are carried in this session's reflection, because this plan declares that grouping.

### D-826: Port record-once: the closeout reads each decision in its stage log and drops the reflection reconciliation   [governance-value] [planning]

**Recommendation:** A. Port `a73d6df`'s validator change. It removes the five reconciliation checks, adds the stage-log field and pending checks and the template-example check, and changes the selftest arms and the two grammar tests named in this plan. Each decision then has one record, the stage log, and that record is checked to be complete. This matches upstream and Zorivest, which ported the same change. Old reflections still pass (0 regressions), and the new check finds exactly the 29 stage-log entries the plan predicted.

**Why not the others**
| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ A. Port record-once with the field check | — | — | `P:/agentic-framework` `a73d6df`; `P:/zorivest/docs/execution/plans/2026-11-07-hd1-human-decision-protocol/implementation-plan.md:137-143, :391-399, :486-497`; `C:/Temp/av-kit/cro/reflections-check-run.txt`; `C:/Temp/av-kit/cro/stage-log-survey-plan-time.txt` |
| ⚠️ B. Remove the reconciliation without the field check | Smaller diff; no stage-log entry is refused | Nothing checks a decision's content any more, so a pending or empty ruling closes in silence. It also drifts from upstream and Zorivest, so every later sync re-diffs it | `a73d6df` `decision_entries` |
| ⚠️ C. Keep the reconciliation and also accept a link list | No check is removed | Each decision still lives in two places, and the reflection's rows still go stale against the stage log. It diverges from upstream on every sync | https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record |
| ❌ D. Do nothing | No change, no review cost | Session 85's link-list template fails today's validator, so Sessions 85 and 86 can't close. The duplication stays | `tools/validate_closeout_artifacts.py:1840` |

**Precedent:** Zorivest HD1-D2 made the same removal, with the same five-row table of checks and the same field check (AC-942.4), and kept the stage check across sources. In av-kit, Session 49b (D-283) made `--decision-issue` repeatable, which this port keeps.
**Research:** native web search, 2026-11-15:
- Microsoft's ADR guidance keeps each record standalone and links supporting material rather than copying it.
- Fandom engineering names knowledge duplicated across sources as a key risk of decision records.
- Fowler's ADR note keeps one record per decision in the repository, and replaces a decision with a new record rather than restating it elsewhere.

All three support one record per decision, with links to it.
**Reversibility / risk:** two-way in code: the old checks are in git and the base copy. It is governance because it removes blocking checks (M-3, M-11) and changes named test assertions (M-7). If it is wrong, a reflection could omit a decision the human never sees. The stage logs are still validated, and the reflection can still link them.
**If you do not answer:** Mat's default acceptance of 2026-11-15 applies, so A is carried as the plan's rows 1 to 6.

```yaml
decision_log:
  - id: D-826
    stage: planning
    question: "Does av-kit's closeout stop requiring each stage-log decision to be restated in the reflection, and check the stage-log entries instead?"
    resolution: human
    class: governance-value
    chosen: "Option A: port a73d6df's validator change. Remove the five reconciliation checks, add the field, pending and template-example checks, and change the selftest arms and grammar tests this plan names"
    source_tag: Human-approved
    precedents: ["P:/zorivest/docs/execution/plans/2026-11-07-hd1-human-decision-protocol/implementation-plan.md:137-143 — HD1-D2 removes the same five checks", "P:/agentic-framework a73d6df — record-once in the closeout validator", "tools/validate_closeout_artifacts.py:1840 — today's reconciliation"]
    research: { engine: native, sources: ["https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record — link supporting material, keep the record standalone", "https://medium.com/fandom-engineering/keep-programmers-decisions-documentation-up-to-date-and-simple-with-architecture-decision-records-8ef5f1761ba — duplicated knowledge across sources is a named risk", "https://www.martinfowler.com/bliki/ArchitectureDecisionRecord.html — one record per decision, kept in the repository"] }
    reasoning: "One record per decision, checked for completeness, matches upstream and Zorivest. B leaves content unchecked, C keeps the duplication, and D blocks Sessions 85 and 86. Plan-time receipts show 0 reflection regressions and 29 predicted stage-log problems, 2 of them in an open plan."
    human_message_reference: "USER_EXPLICIT 2026-11-15 \"Run HDP on any decisions that come up and and I approving acceptance of the defaults.\""
  - id: D-827
    stage: planning
    question: "Is av-kit's refuse_repeated_ids kept once the reflection table is gone?"
    resolution: autonomous
    class: two-way
    chosen: "Kept, with its docstring and message reworded to say that one ID per decision keeps its one record the ruling and lets the stage check across sources read it"
    source_tag: Local Canon
    precedents: ["tools/validate_closeout_artifacts.py:1310-1327 — today's check and its reflection-row wording", "tools/validate_closeout_artifacts.py:1636 — the stage check across sources keys by ID"]
    research: { engine: none, sources: [] }
    reasoning: "The check across sources compares one record per ID, so a repeated ID in one source would still hide a decision from it. Only the reason in the message was about the table. Removing it lost: two arms and a real guard would go for no gain."
  - id: D-828
    stage: planning
    question: "Does check_decisions_log keep the repeatable --decision-issue that upstream does not have?"
    resolution: autonomous
    class: two-way
    chosen: "Kept: check_decisions_log takes (sources, issues), and the absent-issue and repeat-is-USAGE refusals stay"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-05-closeout-register-grammar/implementation-plan.md:124 — D-283 made it repeatable", "tests/tooling/test_closeout_register_grammar.py:208-267 — AC-4 to AC-7"]
    research: { engine: none, sources: [] }
    reasoning: "A closeout can resolve several issues, and each issue's log must still be read. Upstream's single flag would drop that."
  - id: D-829
    stage: planning
    question: "What happens to each av-kit-only decision check, and is a grouping §8 row checked for what it says? (amended after plan review R1, CRO-P2)"
    resolution: autonomous
    class: two-way
    chosen: "Kept: repeated IDs (reworded), the repeatable --decision-issue, the known-issues bounded grammar. Rewritten: the two decision-issue-repeated arms. Removed with the table: its header, Resolution and duplicate-row checks. Added after plan review R1 (CRO-P2): grouping_row_problems in grouping_decisions refuses a blank Question or Reasoning cell, and on an autonomous or human row a blank or pending Chosen; an open row's Chosen is not read, and no type rule applies to a cell"
    source_tag: Local Canon
    precedents: ["C:/Temp/av-kit/cro/upstream-a73d6df.py — the function and arm diff against tools/validate_closeout_artifacts.py", "implementation-plan.md §The av-kit-only checks", "C:/Temp/av-kit/cro-plan-review-round-1.md CRO-P2 — a blank or pending grouping Chosen closed with exit 0 on the projected port", ".agent/docs/human-decision-protocol.md:200 — a grouping row's Resolution is autonomous, human or open", "docs/execution/reflections/2026-10-24-gui-theme-path-fields-reflection.md — D-101 carried while still open, left for its owner", "C:/Temp/av-kit/cro/stage-log-survey-r1.txt — 10 groupings, 0 rows refused; D-240's Chosen is 49"]
    research: { engine: none, sources: [] }
    reasoning: "Each check is kept unless its only purpose was the reflection table. The ones kept guard the stage logs, which are now the only record. With the reflection rows gone, a grouping row is the only record of its decision, so a ruled row gets the same field and pending check as a YAML entry. An open row is a declared open question, not a ruling. Refusing it lost: it would block every session that consumes a grouping whose open question belongs to a later session, as D-101 stayed open through Sessions 40 to 42, and upstream reads open rows. It must still say what the question is and why it stays open. The YAML non-text rule lost for cells because a table has no types."
  - id: D-830
    stage: planning
    question: "Is ec3857a ported here, closing CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR?"
    resolution: autonomous
    class: two-way
    chosen: "Ported in row 5, with its three arms and the four fixture .git folders, before a73d6df's arms in row 6"
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md D-822 — the issue moves to Session 84", ".agent/context/known-issues.yaml:3362 — the issue's cause is the ancestor walk"]
    research: { engine: none, sources: [] }
    reasoning: "Upstream's fix is the issue's root cause, and this session already edits project_root's file. ec3857a came first upstream, but porting it after the removal lets its two read arms land with a73d6df's final wants."
  - id: D-831
    stage: planning
    question: "Is upstream's pending test (re.match pending with a word boundary, any case) taken as written, and how is a quoted value with a trailing comment or an escape read? (amended after plan review R1, CRO-P1, and after its recheck, CRO-R1-1)"
    resolution: autonomous
    class: two-way
    chosen: "The pending test as written: a chosen that starts with the word pending is refused; a chosen that only contains it, or starts with a longer word, is read. Amended after plan review R1 (CRO-P1): decision_field_text reads a quoted value with a new _quoted_scalar_text, which drops a trailing # comment before the quotes are removed and keeps a # inside them. Amended after the R1 recheck (CRO-R1-1): a double-quoted body is decoded as YAML 1.2.2 §5.7 does, through a new DQ_ESCAPE_VALUES beside the existing DQ_ESCAPES and DQ_HEX_ESCAPES, before the blank and pending tests, so the register writer's reasoning \"\\n\" is blank and \"\\u0070ending Mat\" is pending; a single-quoted body stays literal. This is av-kit's one deviation from upstream's decision_field_text, and port-check.py expects it"
    source_tag: Local Canon
    precedents: ["C:/Temp/av-kit/cro/stage-log-survey-plan-time.txt — 3 entries start with pending, none is a real ruling", "P:/agentic-framework a73d6df decision_entries — the test", "C:/Temp/av-kit/cro-plan-review-round-1.md CRO-P1 — four commented quoted inputs closed with exit 0 on the projected port", "tools/validate_closeout_artifacts.py:1234 — _unquote strips a comment only from an unquoted value", "YAML 1.2.2 §6.6 Comments — a comment follows white space and is never inside a quoted scalar", "C:/Temp/av-kit/cro/stage-log-survey-r1-compare.txt — the corrected reading adds no problem in the tree", "C:/Temp/av-kit/cro-plan-review-round-1.md CRO-R1-1 — reasoning \"\\n\" from model.save and an escaped pending choice closed on the projected port", "tools/issue_triage/model.py:336 — _represent_str double-quotes a newline-only value", "tools/validate_closeout_artifacts.py:858 — DQ_ESCAPES and DQ_HEX_ESCAPES, the escapes the YAML subset admits", "YAML 1.2.2 §5.7 Escaped Characters", "C:/Temp/av-kit/cro/escape-probe-r1-1.txt — every writer-escaped value decodes back to itself", "C:/Temp/av-kit/cro/stage-log-survey-r1-1-compare.txt — decoding adds no problem in the tree"]
    research: { engine: none, sources: [] }
    reasoning: "The survey found no ruling that starts with the word pending, so the false-positive risk is measured and small. A wider match would refuse 'Keep the pending queue'. Upstream's quoted branch passes the whole raw value to _unquote, so a quoted pending value with a comment keeps its quotes and an empty quoted value with a comment reads as two characters of text; both would close with no ruling. Reading the scalar as YAML does fixes it in one helper. The R1 recheck showed the helper must decode a double-quoted body too: tools/issue_triage/model.py writes a reasoning that is only a newline as an escaped double-quoted scalar, which read raw is two characters of text. Decoding with the validator's own escape tables keeps one definition of what YAML admits; a full YAML parser lost because the validator is stdlib only. Copying upstream verbatim lost because it keeps the bypass; changing _unquote lost because its other callers read keys, IDs and frontmatter."
  - id: D-832
    stage: planning
    question: "Where do the tests for the port live?"
    resolution: autonomous
    class: two-way
    chosen: "A new tests/tooling/test_closeout_record_once.py (LF) for AC-1 to AC-4 and AC-6 to AC-10, and the changed grammar test file for AC-5; the selftest arms for AC-11"
    source_tag: Local Canon
    precedents: ["pyproject.toml:28 — testpaths is tests", "tests/tooling/test_closeout_register_grammar.py:208 — the CLI-by-subprocess pattern", "tests/tooling/test_review_limits.py — the newest tooling test is LF"]
    research: { engine: none, sources: [] }
    reasoning: "av-kit has no core/tools/tests; its tooling tests run in the full suite and the gate. A separate file keeps the Red receipts apart from the grammar file's own AC numbers."
  - id: D-833
    stage: planning
    question: "How much of the validator's wording about the reconciliation is changed?"
    resolution: autonomous
    class: two-way
    chosen: "Every line above the selftest fixtures that says reconcil (14 at plan time), the --decision-source help, the module docstring and the usage text"
    source_tag: Local Canon
    precedents: ["P:/zorivest/.agent/context/handoffs/2026-11-07-hd1-human-decision-protocol-implementation-critical-review.md:27 — the reviewer noted the stale help upstream kept", "docs/execution/plans/2026-11-15-closeout-record-once/port-check.py — the rule as a check"]
    research: { engine: none, sources: [] }
    reasoning: "Wording that describes a removed check misleads the next reader. Arm labels below the fixture line are names, not descriptions, so they stay."
  - id: D-834
    stage: planning
    question: "How is the known issue closed?"
    resolution: autonomous
    class: two-way
    chosen: "With this plan's issue-resolve.py (status, verification and resolution_path only, bound to row 0's hash), then issue_triage.py render and render --check"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-14-tts-fp16-phase-guard/issue-resolve.py — the tool this copies", "the brief — never hand-edit generated Markdown"]
    research: { engine: none, sources: [] }
    reasoning: "The register holds the triage workstream's uncommitted hunks. A bound, key-limited write can't overwrite them, and render keeps known-issues.md generated."
  - id: D-835
    stage: planning
    question: "What happens to the protocol and template text that describes the old checks?"
    resolution: autonomous
    class: two-way
    chosen: "Left for Session 85; human-decision-protocol.md §6 and the reflection TEMPLATE.md stay stale until then, and this session's reflection uses the table form"
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md D-821 — the validator first, then the protocol", ".agent/docs/human-decision-protocol.md:205-214 — the stale lines"]
    research: { engine: none, sources: [] }
    reasoning: "The ported validator accepts both the table and the link list, so the stale text breaks nothing between the sessions. Editing it here would collide with Session 85's rewrite."
  - id: D-836
    stage: planning
    question: "How is the selftest checked when D-826 removes arms?"
    resolution: autonomous
    class: two-way
    chosen: "An exact list in selftest-arms-check.py of 14 removed, 16 flipped and 26 added arms replaces the never-shrink rule for this port; every other arm and want must be unchanged. The 26 are 15 from upstream, 6 av-kit arms added after plan review R1 for D-829 and D-831, and 5 added after the R1 recheck for D-831 (CRO-R1-1), giving 231 arms, 96 wanting 0/OK"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-14-review-limits-no-token-budget/implementation-plan.md AC-12 — the never-shrink rule", "C:/Temp/av-kit/cro/arms-check-selftest.txt — the list check's selftest"]
    research: { engine: none, sources: [] }
    reasoning: "A shrink is the ruling here, so the check names each change rather than allowing any. An unlisted change still fails."
  - id: D-837
    stage: planning
    question: "What does the session gate cover?"
    resolution: autonomous
    class: two-way
    chosen: "Identity, lint, the task contract, scope paths, the port check, the Red check's selftest, the two test files, the selftest in both temp folders with the arm check, the reflections and survey checks, the issues render, the full Python suite and the state render; types, UI, MCP, OpenAPI and the build are skipped"
    source_tag: Local Canon
    precedents: [".agent/docs/commands.md:190-207 — the D6 stages", "docs/execution/plans/2026-11-14-review-limits-no-token-budget/implementation-plan.md §Session gate — the same shape"]
    research: { engine: none, sources: [] }
    reasoning: "Only one Python tool, its tests and the register change. The default-temp selftest is in the gate because it is the known issue's proof."
  - id: D-838
    stage: planning
    question: "Does this session record rulings for the pending D-246 and D-251 in 2026-11-04-rc2-ffmpeg-uninstall?"
    resolution: autonomous
    class: two-way
    chosen: "Left as they are; the handoff and the reflection flag that the plan's closeout will be refused until its rulings are recorded"
    source_tag: Local Canon
    precedents: ["C:/Temp/av-kit/cro/stage-log-survey-plan-time.txt — the two open problems", "AGENTS.md — no edits to another session's plan"]
    research: { engine: none, sources: [] }
    reasoning: "The rulings are that session's to record. The new check is what makes them visible; editing another plan here would act on decisions this session didn't make."
  - id: D-839
    stage: planning
    question: "Which Decisions Log example does the selftest's reflection template fixture hold?"
    resolution: autonomous
    class: two-way
    chosen: "The link-list example upstream uses; the real docs/execution/reflections/TEMPLATE.md is not touched"
    source_tag: Local Canon
    precedents: ["P:/agentic-framework a73d6df _GOOD_REFLECTION_TEMPLATE — the link-list example", "the brief — Session 85 owns the templates"]
    research: { engine: none, sources: [] }
    reasoning: "The example-check arms need a template fixture that holds the example, and the link list is the form Session 85 adopts. The fixture lives in the validator, so the real template is unchanged."
```

## Research References

- Upstream changes: `P:/agentic-framework` commits `a73d6df` and `ec3857a`. Primary.
- Zorivest's port: `P:/zorivest/docs/execution/plans/2026-11-07-hd1-human-decision-protocol/implementation-plan.md` (HD1-D2, AC-942.4) and its implementation review (`:27`).
- Web (D-826): https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record, https://medium.com/fandom-engineering/keep-programmers-decisions-documentation-up-to-date-and-simple-with-architecture-decision-records-8ef5f1761ba, https://www.martinfowler.com/bliki/ArchitectureDecisionRecord.html.

## Planning receipts

All are under `C:/Temp/av-kit/cro/`. Each probe was read-only with respect to the repository.

- **`eol-plan-time.txt`.** The line endings in §Files Modified, read as Python bytes.
- **`selftest-plan-time-tmp-elsewhere.txt`.** 219 arms, 0 failures, 67 must-OK.
- **`selftest-plan-time-default-tmp.txt`.** 219 arms, 5 failures (the known issue).
- **`arms-before-plan-time.txt`.** 219 arm names.
- **`arms-check-plan-time-against-base.txt`.** The base refused as expected: 32 problems.
- **`stage-log-survey-plan-time.txt`.** 264 sources and 1,101 entries; 29 problem entries, 2 of them open; 2 other refusals.
- **`survey-compare-probe.txt`.** 0 differences.
- **`reflections-check-run.txt`.** 82 reflections: 48 ok, 34 both-refuse, 0 regressions.
- **`port-check-plan-time.txt`.** Exit 1 with 13 problems, as expected before the port.
- **Selftests:** `red-check-selftest.txt` (36 fixtures, 0 wrong), `identity-selftest.txt`, `port-check-selftest.txt`, `arms-check-selftest.txt`, `survey-selftest.txt` and `reflections-check-selftest.txt`, all 0 failures.
- **Render and lint:**
  - `render-check-plan-time.txt`: `issue_triage.py render --check` exits 0.
  - `meu-render-check-plan-time.txt`: `meu_status.py render --check` exits 0.
  - `ruff-plan-time.txt`: `VALIDATOR` and `tests/tooling/` are clean.
  - `meu-stats.txt`.
- **`upstream-a73d6df.py`.** Upstream's validator at `a73d6df`.
- **After plan review R1** (CRO-P1, CRO-P2, Q5, Q8):
  - `stage-log-survey-r1.txt`: 278 sources, 10 of them groupings, and 1,224 entries; 29 problem entries, 2 of them open; 0 grouping rows refused; 3 other refusals.
  - `stage-log-survey-r1-compare.txt`: against `stage-log-survey-plan-time.txt`, 1 difference, the `other-refusal` of Session 87's unfinished plan.
  - `grouping-scan.txt`: the §8 rows of every grouping file. The only `open` row is D-101, with Question and Reasoning stated.
  - `port-check-plan-time-r1.txt`: exit 1 with 17 problems, as expected before the port.
  - `baseline-content-check-probe-r1.txt`: `baseline.ps1`'s content check run on the work tree, hashing every dirty path.
  - Selftests: `survey-selftest-r1.txt`, `port-check-selftest-r1.txt`, `arms-check-selftest-r1.txt`, all 0 failures.
  - `task-lint-r1.txt` and `decision-sources-r1.txt`.
- **After the R1 recheck** (CRO-R1-1):
  - `escape-scan-r2.txt`: 17 double-quoted decision fields with an escape in the tree, none blank or pending once decoded.
  - `escape-probe-r1-1.txt`: ten values saved by `model.save` decode back to themselves; the R1 reader fails the survey selftest with 6 failures.
  - `stage-log-survey-r1-1.txt`: 278 sources, 10 of them groupings, and 1,242 entries; 29 problem entries, 2 of them open; 0 grouping rows refused; 2 other refusals. `stage-log-survey-r1-1-compare.txt`: 0 differences from `stage-log-survey-plan-time.txt`.
  - `port-check-plan-time-r1-1.txt`: exit 1 with 18 problems, as expected before the port.
  - `stage-log-survey-r1-1-final.txt`, run after this plan gained its own escaped decision text: the same totals, and `stage-log-survey-r1-1-final-compare.txt` has 0 differences from `stage-log-survey-plan-time.txt`. `decision-sources-r1-1.txt`: the validator reads 22 decisions from this plan and its grouping, none in the survey's problem lines.
  - Selftests: `stage-log-survey-selftest-r1-1.txt`, `port-check-selftest-r1-1.txt`, `selftest-arms-check-selftest-r1-1.txt`, `red-check-selftest-r1-1.txt`, `identity-selftest-r1-1.txt`, `reflections-check-selftest-r1-1.txt`, all 0 failures; `task-lint-r1-1.txt`: OK, 26 rows.
- **Not run at plan time:** any change to `VALIDATOR`, the new tests or the register.

## Validation stage contract

- **Static:** `tools-lint`, `py-lint`, `task-contract`, `scope-paths`, `port-check`, `red-check-selftest`.
- **Targeted:** the two test files in rows 1 to 5; the selftest in both temp folders and the arm check in row 6; the render in row 7; the reflections and survey checks in row 8.
- **Fresh full:** `py-tests`, `state-render`.
- **Identity:** from `identity.py`, independent of the receipts.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
