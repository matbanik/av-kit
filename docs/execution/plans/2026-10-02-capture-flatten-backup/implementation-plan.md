---
project: "2026-10-02-capture-flatten-backup"
date: "2026-10-02"
source: "docs/build-plan/09-screenshot-capture.md#flatten-with-backup"
meus: ["MEU-67"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Capture flatten with backup (Session 30)

> **Project:** `2026-10-02-capture-flatten-backup`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md`:
> - §Flatten with backup (`:645-659`, matrix 9.12)
> - §MCP (`:562-582`), §Service layer and the annotate/remove contracts as Local Canon
> - `docs/build-plan/05-mcp-server.md` §Destructive gate (`:85-87`), server instructions (`:270-277`), §MCP live audit (`:289-305`)
> - `docs/build-plan/11-page-layout.md` §Capture page layout (`:87-89`) and the CP 23/24 confirm-strip rows (`:287-288`) as locked canon
>
> **Grouping:** `.agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md`, Session 30 (`:103-108`), decisions D-1 to D-7 (`:164-176`).
> **Known issues:** `CAPTURE-FLATTEN-WITH-BACKUP` (triage decisions D-14 Human-approved, D-15 autonomous); `MCP-INSTRUCTIONS-CAPTURE-REMOVE-FILES` (folded in by D-19).
> **User decisions:** [human-gate-decision.md](human-gate-decision.md) §Execution authorization and A-2 (2026-10-03).
> **Status:** `draft`, Round 2. Round 1 (`changes_required`, 1 High) is corrected below (§Round 1 Review Corrections), together with the user's 2026-10-03 decisions. Execution is authorized by a direct user message (`plan_to_exec_gate: human`), recorded in [human-gate-decision.md](human-gate-decision.md) §Execution authorization; the Round 2 verdict is collected before any code change.

## Goal

Mat's 2026-09-30 walkthrough asked for a way to make annotations permanent:

> "there needs to be option to permanently apply to image but also save the backup of the image in case user will want to revert, in a backup folder. This needs to be also a setting" (USER_EXPLICIT 2026-09-30, `known-issues.yaml` `CAPTURE-FLATTEN-WITH-BACKUP` D-14).

Today `annotate_and_save` (`packages/core/src/avkit_core/services/capture.py:371-419`) always writes `{stem}.annotated.png` plus a `{stem}.ann.json` sidecar and never touches the original. This session adds MEU-67 `capture-flatten-backup` across every layer, with the user's 2026-10-03 decisions ([human-gate-decision.md](human-gate-decision.md) §Execution authorization, A-2):

- **Service + REST:**
  - `POST /captures/{id}/flatten` copies the original to a backup folder, bakes the **saved** marks over the original, and removes the annotated sibling and sidecar.
  - A JPEG or WebP shot is never changed. Apply writes a new PNG copy, carries the marks over and flattens that PNG (`CONVERT_ON_APPLY`).
  - `POST /captures/{id}/revert` restores the newest backup. `GET /captures/{id}` reports the newest backup.
- **Settings:** `capture.flatten_backup` (default on), `capture.backup_dir` (default `BACKUP_DIR_DEFAULT_NAME` inside the inbox) and `capture.annotated_format` (PNG by default, or JPEG or WebP for the Save overlay copy, `ANNOTATED_FORMATS`).
- **MCP:**
  - `avkit_capture.flatten` and `avkit_capture.revert`, both destructive (`confirm: true`).
  - Capture remove, flatten and revert also ask the user through the IDE's MCP elicitation prompt and are refused unless the user accepts (`USER_CONFIRM`).
  - Truthful server instructions, audit steps with a declined-confirmation refusal, and the audit's isolation mapping.
- **GUI:**
  - **Apply to image** beside Save overlay, and **Revert** when a backup exists, each behind the existing inline confirm strip.
  - The status line reports the result; the viewport image and filmstrip thumbnail refresh; after a JPEG/WebP apply the selection moves to the new PNG.
  - Three new leaves on the Settings page Capture card.

Order (grouping `:106`): the service + REST + MCP half is the first TDD cycle, the GUI half the second. The worktree baseline is the branch HEAD when execution starts; row 0 records it in `baseline.sha`. Planning started from `477579d` (the Session 29 closeout). Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent (ls: No such file or directory, 2026-10-02); no headroom on PATH. Scope is capture service/route/MCP/renderer internals read directly, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). The `prereq` check refuses if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the claude.ai/code container:
  - `native_shell: bash`; no `rtk`, no `pwsh`, no Codex CLI (`which codex` empty, 2026-10-02);
  - `plan_to_exec_gate: human` (`.agent/context/harness.local.md` §Claude Code; `.agent/docs/harness-profiles.md`);
  - `fresh_worker` is the Agent tool with `.claude/agents/`; every row keeps `compact_continue` as the fallback.
- **Reviewer:** a Fable 5.1 subagent. It is the same vendor, and the user authorized it in [human-review-decision.md](human-review-decision.md). Caps: plan 3 rounds, execution 6.
- **Gate location:** the Sessions 25–29 split ([human-gate-decision.md](human-gate-decision.md) A-1).
  - The container pre-gate is non-authoritative.
  - One local request runs, in order: the authoritative `/mcp-audit` with `--update-baseline`, the baseline issue carry-over, `WINDOWS_GATE`, and the `FLATTEN_LOOK` checklist (`LOCAL_SEQUENCE` below). All are authoritative.
  - Container commands call tools raw, which is the unfiltered equivalent of `rtk proxy`. `validate-task.ps1` runs every stage through `rtk proxy`.
- **Receipts:** `$RECEIPTS_DIR` in the container (default `/tmp/av-kit`), `C:/Temp/av-kit/` on Windows.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-67` | `.agent/context/handoffs/2026-10-02-capture-flatten-backup-MEU-67-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-10-02-capture-flatten-backup-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-02-capture-flatten-backup-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, baseline, `TEST_AMENDMENTS` census (task rows 0–1) | — | `shared` | `walkthrough.md` §Baseline, §Census; `baseline.sha` |
| WP-1 | Service + REST + settings TDD (rows 2–3) | WP-0 | `shared` | Python tests and source; Red/Green receipts |
| WP-2 | MCP surface + audit steps TDD, OpenAPI, cycle-1 gate (rows 4–6) | WP-1 | `compact_continue` | `walkthrough.md` §Cycle 1 gate; compact, then re-read `task.md` and the walkthrough |
| WP-3 | GUI TDD and MEU-67 handoff (rows 7–9) | WP-2 | `compact_continue` | MEU-67 handoff; compact, then re-read |
| WP-4 | Hub reconciliation (row 10) | WP-3 | `shared` | `docs/build-plan/09…`, `05…`, `11…`, `gui-actions-index.md` |
| WP-5 | H1 closeout, `LOCAL_SEQUENCE`, execution review, H2 | WP-4 | `compact_continue` | handoff, audit + gate result files, walkthrough, rolling review, reflection |

---

## User Review Required

> [!IMPORTANT]
> The user has authorized execution (2026-10-03). These items record what that authorization covers and what the next report must tell the user. They are not a pause point.
>
> 1. **Decided by the user (A-2):**
>    - D-10: PNG-only processing, with JPEG/WebP converted on Apply to a new PNG while the original stays untouched (`CONVERT_ON_APPLY`).
>    - Save overlay output can be PNG, JPEG or WebP (`ANNOTATED_FORMATS`).
>    - Capture remove/flatten/revert ask the user through MCP elicitation (`USER_CONFIRM`).
> 2. **`TEST_AMENDMENTS` TA-1 to TA-7.** TA-1 to TA-5 were approved by "Count and changes approved". TA-6 (`ROUTE_COUNT_AFTER` 71 → 73) and TA-7 (`DOMAIN_ERROR_TYPE_NAMES` + `CaptureFlattenConflictError`) are the same count/name-list kind, found by Round 1 review F1. [human-gate-decision.md](human-gate-decision.md) records why they are read as covered. They are listed for the user in the next report. Any other contradiction stops execution (Stop condition S2).
> 3. **`BASELINE_PENDING`**, a declared container-only tolerance. `mcp-server/tests/audit/coverage.test.ts:74-80` requires the committed audit baseline to list exactly the served actions. Only an authoritative Windows audit may write it (`BASELINE_UPDATE_RULE`, `.agent/skills/mcp-tool-audit/SKILL.md:49`). The local request records the baseline **before** `WINDOWS_GATE`, so the authoritative gate tolerates nothing (D-20).
> 4. **Autonomous refinements of the user's answers, logged for veto:**
>    - D-22: the converted file is `{stem}-converted.png`, so it never shares the JPEG's sidecar.
>    - D-23: one annotated sibling at a time; `.jpg` extension; quality 90.
>    - D-24: an IDE without elicitation refuses the three actions. Amended by A-11 (2026-10-04): it falls back to a native Windows dialog (`DIALOG_FALLBACK`).
>    - D-24: the MCP audit's own client answers the elicitation on its disposable fixtures.
>    - D-11 to D-21 are as before.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once here. ACs, task rows and scripts refer to these names and never restate the values (PR-9).

| Name | Definition | Source |
|---|---|---|
| `PRODUCT_SCOPE` | The product files this plan may change are exactly the Files Modified rows below. `ui/src/main/` and `tools/` stay byte-identical to `baseline.sha`. In `packages/infrastructure/src/avkit_infra/capture/adapter.py` only `bake`'s output-format handling changes (`ANNOTATED_FORMATS`); the drawing (`_apply*`, `arrowhead_vertices`, `text_plate_box`, `_color_rgb`, `_load_font`) is unchanged, which `api-scope`'s AST comparison proves (AC-67.29) (`CAPTURE-BAKE-ARROW-THIN` stays out). `validate-task.sh api-scope` proves the frozen paths and that every changed product file is listed. | Spec 09:645-659; grouping `:105`; A-2 |
| `SAVED_MARKS` | The annotation list `CaptureService.load_shot_annotations(shot_id)` returns (`capture.py:264-274`): the parsed sidecar, `[]` when the sidecar is missing, `AnnotationValidationError` (422) when malformed. "Has saved marks" means `len(SAVED_MARKS) > 0`. | Spec 09:653 ("bake the **saved** annotations"); Local Canon |
| `FLATTEN_INPUTS` | By the original's lowercased suffix: `.png` → `FLATTEN_SEQUENCE` in place; `CONVERTIBLE` = `{.jpg, .jpeg, .webp}` → `CONVERT_ON_APPLY`; any other suffix → `FLATTEN_CONFLICTS` (b). | D-10 (Human-approved, A-2) |
| `BACKUP_DIR_DEFAULT_NAME` | `.avkit-backup` | Spec 09:655 |
| `TMP_SUFFIX` | `.avkit-tmp`, appended to a target file's full name for its temporary sibling. It is outside `SCAN_EXTENSIONS` and the watcher's `.png` filter, so a temporary file can never register as a shot. | D-8 |
| `BACKUP_DIR_RULE` | `resolve_backup_dir(raw, inbox)`: when `raw.strip() == ""` the result is `inbox / BACKUP_DIR_DEFAULT_NAME`; otherwise `Path(raw).expanduser()`, which must be absolute (else conflict). The result is `.resolve()`d and must not equal the resolved inbox (else conflict). It may be a subfolder of the inbox, because the inbox scan (`capture.py:201-208`) and the Electron watcher (`ui/src/main/capture-inbox-watch.ts:152`, non-recursive `fs.watch`) see only the inbox's own children. The folder is created (`mkdir(parents=True, exist_ok=True)`) only inside `FLATTEN_SEQUENCE` step 3. | Spec 09:655; D-11; precedent `downloader.ffmpeg_path` `""` = auto (`services/settings.py:47`) |
| `BACKUP_NAME` | `{stem}.{YYYYMMDD-HHMMSS}.png` from the service clock (`CaptureService._now()`, UTC), where `stem = original_path.stem`. If that name exists, `{stem}.{YYYYMMDD-HHMMSS}_{n}.png` for the smallest free `n ≥ 2` (the `_unique_png` pattern, `capture.py:475-485`). | Spec 09:653; D-9 |
| `BACKUP_PATTERN` | `^{re.escape(stem)}\.(\d{8}-\d{6})(?:_(\d+))?\.png$`, matched against file names (not directories) directly inside the resolved backup dir. | D-9 |
| `LATEST_BACKUP(shot)` | The `BACKUP_PATTERN` match in the resolved backup dir with the greatest `(timestamp, n)` (no `_n` = 1), or `None` when there is none, the backup dir does not exist, or `BACKUP_DIR_RULE` is violated. File modification times are never used. | D-9 |
| `FLATTEN_CONFLICTS` | The `CaptureFlattenConflictError` (409) set, checked before any file is written: (a) `SAVED_MARKS` empty; (b) the suffix is outside `FLATTEN_INPUTS`; (c) `capture.flatten_backup` on and `BACKUP_DIR_RULE` violated; (d) `capture.flatten_backup` on and the backup copy raised `OSError` (raised from step 3, after which `FLATTEN_ROLLBACK` runs); (e) replacing a file raised `OSError`. | Spec 09:653 (409 cases); D-16 |
| `FLATTEN_SEQUENCE` | Under `CAPTURE_FILE_LOCK`, in order: (1) load the row (404 if absent) and `SAVED_MARKS` (422 if malformed); (2) check `FLATTEN_CONFLICTS` (a)–(c); (3) if `flatten_backup` is on: resolve the backup dir, create it through `ImageAnnotatePort.ensure_dir` (A-5; services never call `mkdir`, AC-12.8), and `shutil.copyfile(original, backup_dir / BACKUP_NAME)`; (4) `annotate.bake(original, SAVED_MARKS, tmp, "png")` where `tmp` is the original's name plus `TMP_SUFFIX`; (5) `os.replace(tmp, original)`; (6) unlink every `ANNOTATED_SUFFIXES` sibling and the sidecar; (7) save the row with `annotated_path=None`, `sidecar_path=None`, width/height/file_size from the step-4 probe, `updated_at=now`; (8) log `capture.flattened` (shot id, backup path or `none`). Steps 3–8 are one private method that runs with the lock already held (`CAPTURE_FILE_LOCK` is not reentrant), so `CONVERT_ON_APPLY` reuses it. The response is the `DETAIL_OUT` shape with `annotations: []`. | Spec 09:653, 09:658; D-8 |
| `FLATTEN_ROLLBACK` | If step 3, 4 or 5 raises: delete `tmp` if present; delete the backup written in step 3 if any; leave the original, annotated sibling, sidecar and row exactly as they were; re-raise (`OSError` from 3 or 5 as `CaptureFlattenConflictError`; bake errors unchanged: `InboxPathError` 422, `CaptureFailedError` 503). Log `capture.flatten_failed` with the step number. | D-16 |
| `ATOMIC_REPLACE` | The read-then-write on a file is made safe by **ordering plus `os.replace`**: the backup exists before the original is touched, and the new bytes land by one `os.replace` of a fully written sibling. `os.replace` is atomic on POSIX; on Windows `MoveFileEx(MOVEFILE_REPLACE_EXISTING)` is usually but not guaranteed atomic, so the recovery guarantee is the backup, not the rename. With `flatten_backup` off there is no recovery copy, and the confirm text says so (`FLATTEN_CONFIRM_TEXT`). | Research-backed D-8 (Python docs `os.replace`; bugs.python.org issue 8828) |
| `CONVERT_NAME` | `{stem}-converted.png` in the original's folder; when that file exists or a row already holds that path, `{stem}-converted_{n}.png` for the smallest free `n ≥ 2`. | D-22 |
| `CONVERT_ON_APPLY` | Flatten on a `CONVERTIBLE` shot, under `CAPTURE_FILE_LOCK`: (1) load the row and `SAVED_MARKS`, and check `FLATTEN_CONFLICTS` (a) and (c); (2) `target = CONVERT_NAME`; `annotate.bake(original, [], target_tmp, "png")` (an unmarked RGB PNG decode of the original) then `os.replace(target_tmp, target)`; (3) register `target` through `_upsert_shot` with the original row's `source`, and write its sidecar (`SIDECAR_VERSION`, `SAVED_MARKS` on the wire); (4) run `FLATTEN_SEQUENCE` steps 3–8 on the new row, so the backup (when on) is the unmarked converted PNG and Revert works on it; (5) the JPEG/WebP file, its sidecar, its annotated sibling and its row are never touched. On any failure after step 2 began: delete `target_tmp`, `target`, its sidecar, its backup and its row, then re-raise as in `FLATTEN_ROLLBACK`. Log `capture.converted` (from, to). The response is the new PNG shot's `DETAIL_OUT`, so its `id` differs from the request's. | D-10 (Human-approved, A-2); D-22 |
| `REVERT_SEQUENCE` | Under `CAPTURE_FILE_LOCK`: (1) load the row (404 if absent); (2) `src = LATEST_BACKUP(shot)`; `None` is `NotFoundError` (404) "no backup for this capture"; (3) `shutil.copyfile(src, tmp)` then `os.replace(tmp, original)` (on `OSError`: delete `tmp`, raise `CaptureFlattenConflictError`); the backup file stays; (4) probe the restored original; (5) `ANNOTATED_CONSISTENCY`; (6) save the row (width/height/file_size from the probe, `annotated_path`/`sidecar_path` per step 5, `updated_at=now`); (7) log `capture.reverted`. The response is `DETAIL_OUT`. | Spec 09:654; D-14 |
| `ANNOTATED_FORMATS` | Setting `capture.annotated_format`, wires `png` \| `jpeg` \| `webp`, default `png`. The domain tuple `ANNOTATED_FORMATS = ("png", "jpeg", "webp")` lives in `domain/capture.py`, with `ANNOTATED_EXT = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}` and `ANNOTATED_SUFFIXES` = `.annotated` + each extension. The annotated sibling is `{stem}.annotated{ANNOTATED_EXT[format]}`. `annotate_and_save` bakes in the current format and unlinks the other two siblings, so at most one exists; an empty list unlinks all of them. The inbox scan skips every `ANNOTATED_SUFFIXES` name (today only `.annotated.png`, `capture.py:46,207`). `GET /captures/{id}/image?variant=annotated` already takes its media type from the file suffix (`routes/captures.py:45-50,235-241`), and MCP `image` sniffs it from the bytes (`mcp-server/src/client.ts:160-180`). | Human-approved A-2 Q2; D-23 |
| `LOSSY_QUALITY` | `90`, the Pillow `quality` for JPEG (`RGB`) and WebP (lossy) output of `bake`. PNG output is unchanged. | Human-approved A-2 Q2 ("JPEG/WebP use quality 90"); Pillow docs (≤ 95) |
| `BAKE_PORT` | `ImageAnnotatePort.bake(original_path, annotations, output_path, output_format: AnnotatedFormat = "png") -> ImageProbe` (`ports/capture.py:21-28`). An unknown format raises `ValidationError` before any file is written. Every existing call keeps its meaning through the default. | D-23 |
| `ANNOTATED_CONSISTENCY` | After a revert, if `SAVED_MARKS` is non-empty, the annotated sibling is re-baked from the restored original in the current `ANNOTATED_FORMATS` setting through a private helper (never the locked `annotate_and_save`), and the row keeps `annotated_path`/`sidecar_path`; if empty, every `ANNOTATED_SUFFIXES` sibling is unlinked and both paths are `None`. So an annotated sibling, when present, always equals `bake(original, sidecar)`. | D-14 |
| `CAPTURE_FILE_LOCK` | One module-level `threading.Lock` in `services/capture.py`, held for the whole body of `scan_inbox`, `flatten`, `revert`, `annotate_and_save` and `remove`. It is not reentrant: nothing inside a held section calls another locked public method. The API is one uvicorn process (`packages/api/src/avkit_api/cli.py:211-231`, no `workers`), and sync routes run on its thread pool, so a process lock serializes every capture file mutation and the scan's row pruning (`capture.py:239-241`). | D-15; Round 1 F6 |
| `DETAIL_OUT` | `CaptureShotDetailOut` (`schemas/captures.py:129`) gains `backup_path: str \| None` = `LATEST_BACKUP(shot)` as a string. `GET /captures/{id}`, flatten and revert return it. `CaptureShotOut` and the list envelope are unchanged. | Spec 09:653 ("plus `backup_path`"); D-13 |
| `NEW_SETTINGS` | `SETTINGS_KEY_TABLE` gains `("capture", "flatten_backup"): SettingSpec("boolean", True)`, `("capture", "backup_dir"): SettingSpec("string", "")` and `("capture", "annotated_format"): SettingSpec("string", "png", frozenset(ANNOTATED_FORMATS))`. `SettingsPutIn` gains `flatten_backup: bool \| None`, `backup_dir: str \| None` and `annotated_format: str \| None`. The MCP `SETTINGS_SCHEMA.namespaces.capture` and its strict Zod set schema (`mcp-server/src/toolsets/settings.ts:63-68,123-126`), and the renderer `capturePutSchema` (`ui/src/renderer/src/features/settings/settings-schemas.ts:75-90`), gain the same three keys with the same defaults (`annotated_format` as an enum). | Spec 09:655; A-2 Q2; D-11 |
| `MCP_ACTIONS` | `ACTION_INDEX` (`mcp-server/src/toolsets/registry.ts:111-118`) appends, after `avkit_capture.remove`, `{avkit_capture, flatten, POST, /captures/{id}/flatten}` and `{avkit_capture, revert, POST, /captures/{id}/revert}`. `captureSchema` gains, for each, a `z.object({action: z.literal(<action>), id: z.string().min(1), confirm: z.literal(true)}).strict()`. `DESTRUCTIVE_ACTIONS` gains both keys. `captureDescriptions` gains both via `desc(...)` plus one consequence sentence each. The request body is `{}` (`httpBody`, `registry.ts:197-221`, already drops `action`, `confirm`, `id`). | Spec 09:656; 05:85-87 |
| `USER_CONFIRM_ACTIONS` | `{avkit_capture.remove, avkit_capture.flatten, avkit_capture.revert}`: the MCP actions that delete or overwrite user files. Download/transcript/convert remove and clear keep files on disk (05:130,158) and are not members. | Human-approved A-2 Q3 |
| `USER_CONFIRM` | `ToolRuntime` (`registry.ts:167-170`) gains `confirmWithUser?: (request: {tool, action, id, message}) => Promise<UserConfirmOutcome>`, with `UserConfirmOutcome = "accept" \| "decline" \| "cancel" \| "unsupported"`. In `handleTool`, after the Zod parse and `confirmMissing`, a `USER_CONFIRM_ACTIONS` call awaits `confirmWithUser` (absent → `"unsupported"`). Only `"accept"` proceeds to fetch; every other outcome returns `TOOL_ERROR` code `user_confirmation_refused` naming the outcome, with zero fetches. The outcome switch is exhaustive (`assertNever`). `registerMcpSurface` builds `confirmWithUser` from the low-level `server.server`: no `elicitation.form` in `getClientCapabilities()` (the SDK normalizes a bare `elicitation: {}` to `{form: {}}`, `types.js:335-345`; a URL-only client has no form mode) → `"unsupported"`; otherwise `elicitInput({message, requestedSchema: {type: "object", properties: {confirm: {type: "boolean", title: "Allow"}}, required: ["confirm"]}}, {timeout: USER_CONFIRM_TIMEOUT_MS})`, mapping `action === "accept" && content.confirm === true` → `"accept"`, `"decline"` → `"decline"`, anything else or a thrown error/timeout → `"cancel"` (fail closed). `message` is `USER_CONFIRM_MESSAGE`. | Human-approved A-2 Q3; D-24; MCP spec 2025-06-18 §Elicitation |
| `DIALOG_FALLBACK` | (A-11) `registerMcpSurface(server, {nativeConfirm?})` (and `createServer`, which passes it through) times the elicitation. When the outcome is `"unsupported"`, or `decline`/`cancel` returned faster than `USER_CONFIRM_AUTODECLINE_MS`, the client answered, not the person, so the person is asked with `nativeConfirm(message)` (`mcp-server/src/native-confirm.ts`). That is a topmost Windows `MessageBox` (Yes/No, default No, title "av-kit") run by `powershell.exe -NoProfile -NonInteractive -STA -EncodedCommand`, with the message in `AVKIT_CONFIRM_MESSAGE`, never in the script, and `timeout: USER_CONFIRM_TIMEOUT_MS`. Exit 0 → `accept`, 1 → `decline` (only a `No` exits 1; with `$ErrorActionPreference = 'Stop'` and `trap { exit 2 }`, a script error exits 2), any other exit or the timeout → `cancel`. Off Windows, or when the process cannot start, it is `"unsupported"` and the elicitation outcome stands. An `accept` from elicitation, and a slower decline (the person's answer), never open the dialog. (A-11 review) The timing uses `options.now` (default `performance.now()`), and every confirmation writes one `options.log` line (default stderr): `avkit USER_CONFIRM <tool>.<action> <id>: elicitation <outcome> in <n> ms; dialog <outcome> in <n> ms` or `; dialog not asked`. | Human-approved A-11; `MCP-ELICITATION-VSCODE-AUTO-DECLINE`; may-I PR #1 |
| `USER_CONFIRM_AUTODECLINE_MS` | `250` (`destructive.ts`). No one reads and answers a prompt that fast; the VS Code extension auto-declines in about 1 ms (23 ms round trip in F8). Precedent: may-I PR #1 default. | Human-approved A-11 |
| `ADVERTISED_SCHEMA` | (A-9) `registerMcpSurface` keeps each tool's registered `inputSchema` as its strict per-action union, so server validation is unchanged. It rewrites only the `tools/list` result: each tool's `inputSchema` becomes the JSON schema of one object whose `action` is an `enum` of that tool's `ACTION_INDEX` actions, and whose other keys are the union of every branch's fields. Each such key is typed (one schema, or `anyOf` of the distinct branch schemas) and optional. `additionalProperties` is false. Every other `tools/list` field is unchanged. | Human-approved A-9; `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA` |
| `DISABLED_REASON_TIP` | (A-6, A-10) Apply and Revert sit in wrapper spans. While their button is disabled, the wrapper carries the reason as `title` and renders a visible `role="tooltip"` label (`capture-apply-image-reason` / `capture-revert-image-reason`) on hover or focus-within, so the reason shows without native tooltips. | Human-approved A-6, A-10 |
| `USER_CONFIRM_TIMEOUT_MS` | `120000` (two minutes for the person to answer the IDE prompt; the SDK request default is 60 s, `protocol.d.ts:57`). On expiry the call is refused as `cancel`. | D-24; Round 2 N3 |
| `USER_CONFIRM_MESSAGE` | remove: "An AI agent asks to delete capture {id} and its files (image, annotated copy, saved marks) from disk. Allow?"; flatten: "An AI agent asks to bake the saved marks into capture {id}'s image file (a backup is kept when backups are on; a JPEG/WebP shot gets a new PNG copy instead). Allow?"; revert: "An AI agent asks to overwrite capture {id}'s image with its newest backup. Allow?". Only the validated `id` is interpolated; no agent-supplied free text appears in the prompt. | D-24 |
| `INSTRUCTION_TEXT` | `SERVER_INSTRUCTIONS` line 5 (`mcp-server/src/index.ts:10`) and its mirror 05:274 become: "Destructive actions require confirm: true. Download, transcript and convert remove/clear keep files on disk. Capture remove deletes the shot's files; capture flatten overwrites the image file (after a backup when capture.flatten_backup is on; a JPEG/WebP shot gets a new PNG copy instead); capture revert overwrites it from its newest backup. These three capture actions also ask the user in the IDE and are refused unless the user accepts; call them only when the user explicitly asked." Every other line is unchanged. | D-19; A-2 Q3; 09:487,526 |
| `AUDIT_STEPS` | `mcp-server/scripts/audit/plan.ts` `CAPTURE_STEPS` gains two `destructiveStep`s, placed after `capture.image.annotated` and before `capture.capture_interactive`: `capture.flatten` (`depends_on: ["capture.annotate"]`, probe `{original_sha256, annotated_exists, backup_count}` read from the REST detail and the filesystem) and `capture.revert` (`depends_on: ["capture.flatten"]`, probe `{original_sha256}`). A confirmed flatten must change all three flatten probe fields (the sha differs, the annotated file is gone, one more backup exists); a confirmed revert must restore the sha recorded before `capture.flatten`. | Spec 05:300; grouping D-4 |
| `AUDIT_ELICITATION` | The audit client (`scripts/audit/client.ts:37`) declares `capabilities: {elicitation: {}}` and answers `elicitation/create` from a per-call policy the step sets (`accept` or `decline`; default `decline`, so an unplanned prompt never auto-accepts). `destructiveStep` takes `userConfirm: true` for the three `USER_CONFIRM_ACTIONS` steps and then adds a fourth call, `confirm: true` under a `decline` policy, recorded as `refusal_declined` in `RefusalRecord` (`scripts/audit/types.ts:46`), which also gains `user_confirm: boolean` (true exactly for those steps). `refusalVerdict` (`classify.ts:44-47`) fails a record with `user_confirm: true` whose `refusal_declined` is missing, not an error, or changed the probe; a record with `user_confirm: false` is judged exactly as today, so the existing `classify.test.ts:70-104` cases stay green (Round 2 N2). The confirmed call runs under `accept`: the operator who started the audit run is the user, and every target is a disposable fixture inside the isolated root. (A-11) The client answers after `AUDIT_ANSWER_DELAY_MS` = 2 × `USER_CONFIRM_AUTODECLINE_MS`, so its declines read as the operator's and never open `DIALOG_FALLBACK`. | D-24; Local Canon REFUSAL_ORACLE; A-11 |
| `AUDIT_ISOLATION` | `ISOLATION_SUBDIR` (`scripts/audit/run.ts:74-81`) gains `"capture.backup_dir": "capture_backups"`, and `OutSub` (`plan.ts:20`) gains `"capture_backups"`. Without it the audit refuses to start, because `backup_dir` matches `PATH_LIKE` (`classify.ts:269-281`) and an unmapped path-like key fails the isolation guard closed. | Local Canon AC-68.8 |
| `APPLY_ENABLED` | The **Apply to image** button (`capture-apply-image`) is enabled exactly when a shot is selected, `saved.length > 0`, the overlay is not dirty, no confirm strip is open, and the selected shot's lowercased suffix is in `FLATTEN_INPUTS`. When it is disabled with a shot selected, its `title` names the first unmet reason in that order: "Save marks first", "Save the overlay first", "This file type cannot be flattened". | Spec 09:657; D-18 |
| `REVERT_VISIBLE` | The **Revert** button (`capture-revert-image`) is rendered exactly when the selected shot's detail has `backup_path !== null`. It is disabled while the overlay is dirty (title "Save or discard overlay marks first") or a confirm strip is open. | Spec 09:657; D-18 |
| `FLATTEN_CONFIRM_TEXT` | PNG with backups on: "Bake the saved marks into {display_name}? The original is copied to {folder} first.", where `{folder}` is the `backup_dir` setting when non-empty, otherwise "the backup folder in the inbox". PNG with backups off: "Bake the saved marks into {display_name}? Backups are off, so this cannot be undone." `CONVERTIBLE`: "Bake the saved marks into a new PNG copy of {display_name}? {display_name} itself stays unchanged." Accept button `capture-flatten-confirm` "Apply to image", cancel `capture-flatten-confirm-cancel`. | Spec 09:657; D-18; A-2 Q1 |
| `REVERT_CONFIRM_TEXT` | "Replace {display_name} with its newest backup ({basename(backup_path)})? The current image is overwritten." Accept `capture-revert-confirm` "Revert image", cancel `capture-revert-confirm-cancel`. | Spec 09:657; D-18 |
| `CONFIRM_KINDS` | `CapturePage`'s `confirm` state (`CapturePage.tsx:197`) widens from `'dirty' \| 'delete' \| null` to `'dirty' \| 'delete' \| 'flatten' \| 'revert' \| null`. The strip's message and button wiring become an exhaustive `switch` over the union (`assertNever`), so a new kind breaks the build. `CONFIRM_EXCLUSIVITY` (filmstrip, Delete, Apply and Revert disabled while open) covers all four. Accept buttons are `variant="destructive"`, as CP 23/24 already are. | Local Canon 11:287-288; D-18 |
| `FLATTEN_STATUS` | `capture-status` text after the call: PNG flatten with a backup "Applied to image. Backup: {backup_path}"; without "Applied to image (no backup)."; convert "Applied to a new PNG copy: {new display_name}."; revert "Reverted from {basename(backup_path)}."; any failure the API envelope message (the existing error channel, `CapturePage.tsx:1015-1023`). A success notice clears on shot change and on the next edit. | Local Canon 11:89; D-18 |
| `IMAGE_REVISION` | After a 200 from flatten or revert, the page invalidates the captures list query (`QUERY_KEY`, as Save and Delete already do, `capture-commands.ts:91,97`) and reloads the selected detail. The viewport image effect (`CapturePage.tsx:287-311`) keys on `[selectedId, viewVariant, selected?.updated_at]` and the filmstrip thumbnail effect (`CaptureFilmstrip.tsx:58-78`) on `[item.id, item.updated_at]`. A flatten or revert bumps `updated_at`, so both refetch. When the response `id` differs from the selected id (`CONVERT_ON_APPLY`), the page selects the response id. | Spec 09:658; D-18; Round 1 F10 |
| `SETTINGS_LEAVES_UI` | The Settings page Capture card (`SettingsPage.tsx` around `:780-850`) gains: a checkbox `settings-leaf-flatten_backup` ("Back up the original before Apply to image"); a `PathRow` `settings-leaf-capture-backup_dir` with Browse `settings-capture-backup-browse`, placeholder "{inbox}/" + `BACKUP_DIR_DEFAULT_NAME`; and a select `settings-leaf-annotated_format` ("Save overlay format": PNG, JPEG, WebP). `useCaptureSettings` (`CaptureForm`, `CAPTURE_DEFAULTS`, `asForm`, `sameForm`) carries all three. The Capture page Options panel is unchanged. | Spec 09:603, 09:655; A-2 Q2; D-17 |
| `FLATTEN_HELP_SENTENCE` | "Apply to image bakes the saved marks into the original file after copying it to the backup folder (Settings → Capture); a JPEG or WebP shot gets a new PNG copy instead, and the original stays unchanged. Revert restores the newest backup. Save overlay can write PNG, JPEG or WebP (Settings → Capture)." It is appended to the `original-annotated` body (`capture-help-content.ts:20-23`); the existing sentence stays verbatim. | 09:155-157 HelpCard topics are a minimum |
| `NEW_TESTIDS` | One block appended after the MEU-66 block (`ui/tests/e2e/test-ids.ts:400-405`), `// MEU-67 Capture flatten and revert (additive IDs).`: `capture-apply-image`, `capture-revert-image`, `capture-flatten-confirm`, `capture-flatten-confirm-cancel`, `capture-revert-confirm`, `capture-revert-confirm-cancel`, `settings-leaf-flatten_backup`, `settings-leaf-capture-backup_dir`, `settings-capture-backup-browse`, `settings-leaf-annotated_format`. Appending after the `// MEU-51 primitive harness IDs.` marker keeps the AC-51.6 prefix hash valid. | Local Canon AC-51.6 |
| `TEST_AMENDMENTS` | TA-1 to TA-9 below: the only approved changes to existing test expectations. | AGENTS §Testing & TDD; human-gate-decision.md §Execution authorization |
| `FIXTURE_REPAIRS` | Setup-only edits that change no assertion: (a) `mcp-server/tests/fixtures.ts` per-action call and body maps (`:140-215`, `:255-300`) gain entries for the two actions; (b) `mcp-server/tests/audit/fake-backend.ts` serves `POST /captures/{id}/flatten` with an in-memory counter that `GET /captures/{id}` reports, for the test-local refusal step of AC-67.19 (Round 1 F3 option ii); (c) the Electron route mocks in `ui/tests/e2e/capture-inbox.test.ts:83-170` serve the two routes, `backup_path` on detail and a converted shot in the list; (d) jsdom fixtures that build a capture detail or settings object add the new fields only where a new test needs them; (e) the parity loop in `mcp-server/tests/action-index.test.ts:56-90` passes `confirmWithUser: async () => "accept"` in its runtime, so the three `USER_CONFIRM_ACTIONS` rows still reach their fetch assertions unchanged; (g) the route fake `FakeCapture` in `tests/e2e/test_api_captures.py` gains `latest_backup(shot_id) -> None` (A-3); (f) the Python fake port's `bake` (`tests/unit/test_capture_service.py:68`, three positional parameters) gains `output_format: str = "png"` so it matches `BAKE_PORT`, recording the format it was given (Round 2 N1). (h) the same fake port gains `ensure_dir(path)`, which creates the folder and records the call, matching the port method A-5 adds so the service never calls `mkdir` (AC-12.8). | AGENTS §Testing & TDD ("fixture repairs may fix setup") |
| `GATED_PATHS` | The executable copy is the `gated` list in `validate-task.sh` `windows-gate-check`, and `plan_checks.py static` asserts it equals this list: `ui packages mcp-server tests tools pyproject.toml uv.lock openapi.committed.json docs/build-plan/06-gui.md docs/build-plan/10-queue-card-ui.md docs/build-plan/11-page-layout.md docs/build-plan/build-priority-matrix.md docs/build-plan/gui-actions-index.md docs/proposals docs/execution/plans/2026-08-28-p10-queue-card-foundations docs/execution/plans/2026-09-02-p10-queue-card-migration docs/execution/plans/2026-09-03-p10-queue-card-dnd docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md .agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md .agent/model-registry.local.json .agent/model-registry.local.yaml .agent/skills/mcp-tool-audit .agent/workflows/mcp-audit.md .agent/workflows/README.md .agent/skills/README.md .agent/docs .agent/schemas .agent/roles .agent/templates docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.ps1`. That is Session 29's list (`2026-10-01-capture-viewport-chrome/implementation-plan.md:152`) plus what this plan's gate reads beyond it: the committed audit baseline and `SKILL.md` (`coverage.test.ts:10-13`, `docs.test.ts:8-9`), the two READMEs (`docs.test.ts:91-92`), and the `.agent/docs`, `.agent/schemas`, `.agent/roles`, `.agent/templates` inputs of the Python tooling tests (plan-time sweep, 2026-10-02). A framework-doc edit under those paths between the gate and review approval therefore reopens the gate; the `LOCAL_SEQUENCE` request says so. **Excluded, as a rule:** `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `docs/execution/metrics.md` and `.agent/context/MCP/mcp-tool-audit-report.md` are SSOT or closeout records that change only at H1-3/H2-2 (doc-only, cloud-local §3.4); `post-review-state` re-runs the doc-reading suites after its edits. | cloud-local §3.3 item 2, §3.4 |
| `COUNT_FLOORS` | Vitest total ≥ 748 and Electron expected ≥ 127, from the last authoritative gate: Session 29 attempt 4, `2026-10-01-capture-viewport-chrome/windows-gate-result.json` (Vitest 748/748, Playwright 127/0/0, pytest 629/0). In the runner's own vocabulary: Vitest `numTotalTests` ≥ 748 with `numFailedTests` 0; Playwright `stats.expected` ≥ 127 with `unexpected` 0 and `flaky` 0; pytest failed 0 and passed ≥ 629 (`pytest_floor` seeds at 629 and the `.ps1` carries it forward). The executable copies are the literals in `validate-task.sh` `windows-gate-check`; `plan_checks.py static` asserts they equal 748 / 127 / 629. | cloud-local §3.3 |
| `LOCAL_SEQUENCE` | One request ([local-requests.md](local-requests.md) §GATE), on the requested commit `C`, in this order: (1) `validate-task.ps1 -Check audit`: builds `mcp-server`, runs the authoritative audit with `--update-baseline --baseline … --report …`, then `baseline_carry.py` copies each prior `issue` onto identical non-pass entries and findings. If the carry refuses, the script restores the prior baseline and stops. It writes `mcp-audit-summary.json` into this plan folder. (2) Commit + push the baseline, report and summary as `A`. (3) `validate-task.ps1 -Check windows-gate` on `A`; commit + push `windows-gate-result.json`. (4) `FLATTEN_LOOK` F1–F8 on the same `A`. Code identity: `C..A` touches only the baseline, the report and this plan folder. | D-20; `BASELINE_UPDATE_RULE`, `BASELINE_ANNOTATION_RULE` (`SKILL.md:49-51`) |

**`TEST_AMENDMENTS`.** Each row changes only what its rule changes. Other assertions in the same test stay as they are.

| TA | Test (file:line) | Current expectation | Amended expectation | Rule |
|---|---|---|---|---|
| TA-1 | `mcp-server/tests/action-index.test.ts:40`; `capture.test.ts:89`; `convert.test.ts:55`; `m7-resource.test.ts:47` (title "exactly 67 keys"), `:52`, `:69`; `audit/coverage.test.ts:18-19`; `audit/runner-fake-backend.test.ts:75` | `ACTION_INDEX` / `ACTION_DESCRIPTIONS` / `ACTION_SET` / `discovery.actions` = 68 | 70 (+`avkit_capture.flatten`, +`avkit_capture.revert`), with a `// TA-1 (Session 30, MEU-67)` note beside each, as TA-9 did; the `m7-resource.test.ts:47` title says 70 | Spec 09:656; `MCP_ACTIONS` |
| TA-2 | `mcp-server/tests/capture.test.ts:106` (AC-38.2) and its expectation table `CAPTURE_ACTION_INDEX` (`mcp-server/tests/fixtures.ts:79-88`); `DESTRUCTIVE_KEYS` (`fixtures.ts:119-127`) | 8 capture rows; 7 destructive keys | 10 rows: the 8 unchanged plus the two `MCP_ACTIONS` rows in the same order; destructive keys + `avkit_capture.flatten`, `avkit_capture.revert` | Spec 09:656 |
| TA-3 | `mcp-server/tests/audit/coverage.test.ts:46-57` (destructive refusal list) | 7 destructive steps | The same 7 plus `avkit_capture.flatten`, `avkit_capture.revert`, sorted | Spec 05:300; `AUDIT_STEPS` |
| TA-4 | `tests/unit/test_capture_service.py:19` (asserted `:383`); `tests/e2e/test_api_captures.py:44` (asserted `:718`); `mcp-server/tests/capture.test.ts:33` (asserted `:165`) | capture key set = 4 keys | 7 keys: the 4 unchanged plus `flatten_backup`, `backup_dir`, `annotated_format`; old defaults unchanged; new defaults asserted (`True`, `""`, `"png"`) | Spec 09:655; A-2 Q2; `NEW_SETTINGS` |
| TA-5 | `mcp-server/tests/audit/isolation.test.ts:9-16` (`MAPPING`, "six output path keys", AC-68.8) | 6 isolation keys | 7: the 6 unchanged plus `capture.backup_dir` → `OUT("capture_backups")`; the test title says seven | Local Canon AC-68.8; `AUDIT_ISOLATION` |
| TA-6 | `tests/e2e/test_api_downloads.py:372` (`ROUTE_COUNT_AFTER`, asserted `:424` against `openapi.committed.json`) | 71 operations | 73 (+ the two flatten/revert POST operations), with a `# TA-6 (Session 30, MEU-67)` note | Spec 09:653-654; Round 1 F1 |
| TA-8 | `tests/e2e/test_api_openapi.py:14-87` (`ROUTE_INDEX`, asserted `:81` `paths == ROUTE_PATHS` and `:82` `len(ROUTE_INDEX) == 71`); `tests/e2e/test_api_downloads.py:374` (`ACTION_INDEX_AFTER`, asserted `:441`); `tests/e2e/test_api_captures.py:76` (`SHOT_DETAIL_OUT_FIELDS`, asserted `:824` `tuple(body) ==`) | 71 route rows; 68 registry rows; detail keys end `annotations` | `ROUTE_INDEX` + `("POST", "/api/v1/captures/{id}/flatten")`, `("POST", "/api/v1/captures/{id}/revert")` after the annotate row, `len == 73`; `ACTION_INDEX_AFTER = 70`; `SHOT_DETAIL_OUT_FIELDS` + `("backup_path",)` after `annotations`, matching `DETAIL_OUT`'s field order. Each has a `# TA-8 (Session 30, MEU-67)` note. | Human-approved A-3 (census, row 1) |
| TA-9 | `tests/unit/test_domain_capture.py:321` (AC-34.10, `list(inspect.signature(ImageAnnotatePort.bake).parameters)`) | `["self", "original_path", "annotations", "output_path"]` | the same list + `"output_format"` (`BAKE_PORT`); every other assertion in the test unchanged; a `# TA-9 (Session 30, MEU-67)` note | Human-approved A-4 (row 3 Green) |
| TA-7 | `tests/unit/test_domain.py:181-205` (`DOMAIN_ERROR_TYPE_NAMES`, asserted `:208-214` against `errors.DOMAIN_ERROR_TYPES`) | 24 ordered names ending `CaptureRequestConflictError` | The same 24 plus `CaptureFlattenConflictError` appended last; `DOMAIN_ERROR_TYPES` in `errors.py` appends it in the same position, so the tuple stays the full domain-error list | D-16; Round 1 F1 |

**Environment-bound census** (cloud-local §4). The container pre-gate tolerates only these failures. `WINDOWS_GATE` tolerates none. Session 29's set (`2026-10-01-capture-viewport-chrome/implementation-plan.md:157-163`) plus one sequencing-bound MCP member:

| Tier | Member | Signature / handling |
|---|---|---|
| Vitest | AC-51.6 `ui/tests/unit/layout-primitives.test.ts` | The CRLF prefix hash recomputes to `819760B9…` and new ids are unique (`vitest_env_ok` `crlf_proof`). `NEW_TESTIDS` lands after the marker. |
| Vitest | AC-41.3 `ui/tests/unit/queue-canon.test.ts` | `P:/zorivest` is absent and `styles.css` is unchanged since `f7d3134`. |
| Electron | capture-picker specs in `ui/tests/e2e/capture-picker.test.ts` | Not on Windows, the stub `.exe` is absent, and the failure is exactly the stub-missing error (`electron_env_ok`). |
| pytest | the Windows-bound tooling tests (`tests/tooling/*`) | `pytest_env_ok`: the container's failed set must be a subset of the failed set at `baseline.sha`. |
| MCP Vitest | `BASELINE_PENDING`: "AC-68.5 the committed baseline's entries equal AUDIT_ACTION_SET and every non-pass carries an issue" (`coverage.test.ts:74-80`) | `mcp_env_ok` tolerates only that test, and only when it re-proves from the sources that the committed baseline is byte-identical to `baseline.sha` and that the registry's served set minus the baseline entries is exactly `{avkit_capture.flatten, avkit_capture.revert}` with nothing extra. Any other failure is real. Closed by `LOCAL_SEQUENCE` step 1 before `WINDOWS_GATE` (D-20). |
| External inputs | `P:/agentic-framework` HEAD; `P:/.agent/model-registry.json` hash | `validate-task.ps1` records both before stage 1; on attempt ≥ 2 a mismatch stops before stage 1 (cloud-local §3.2). |

### MEU-67 — `capture-flatten-backup`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| REST `POST /captures/{id}/flatten` body | `EmptyIn \| None = Body(default=None)` (the `create_capture_request` pattern, `routes/captures.py:186-193`) | no fields; missing body and `{}` both accepted | `extra="forbid"` (`ApiModel`) → 422 |
| REST `POST /captures/{id}/revert` body | same | same | same → 422 |
| REST path `{id}` (both routes) | route signature `id: str` | any string; unknown id → 404 from `NotFoundError` | n/a |
| REST `PUT /settings/capture` new leaves | `SettingsPutIn` (`schemas/settings.py:12`) + `SETTINGS_KEY_TABLE` `_encode` (`services/settings.py:116-140`) | `flatten_backup` bool; `backup_dir` string (empty allowed = derive); `annotated_format` ∈ `ANNOTATED_FORMATS` (other string → 422 "not a known wire value", `settings.py:139-140`) | `extra="forbid"` → 422 |
| MCP `avkit_capture` `flatten` / `revert` | `captureSchema` (`toolsets/capture.ts:110`) | `id` non-empty string; `confirm` literal `true` | Zod `.strict()`; a missing or false `confirm` fails the Zod parse (`validation_error`) before fetch |
| MCP `USER_CONFIRM_ACTIONS` user answer | `USER_CONFIRM` (elicitation result) | only `action: "accept"` with `content.confirm === true` proceeds | anything else, including errors and timeouts, is refused |
| MCP `avkit_settings set` capture leaves | strict Zod settings set schema (`toolsets/settings.ts:123-126`) | `flatten_backup` boolean; `backup_dir` string; `annotated_format` enum | `.strict()` |
| UI Settings Capture card form | `capturePutSchema` (`settings-schemas.ts:75-90`) via `parseSettingsPut('capture', form)` | same types | `.strict()` |
| File system: backup dir setting value | `BACKUP_DIR_RULE` | absolute after `expanduser`; not the inbox | violation → 409 at flatten (never a 500) |
| File system: original file type | `FLATTEN_INPUTS` | `.png` in place; `CONVERTIBLE` converted | other suffix → 409 |

Create/update parity: the two routes take no body, and the settings leaves go through the one PUT path used for every namespace, so there is no create/update split.

#### Acceptance Criteria

Python contract tests use a real `CaptureService` with the real Pillow `ImageAnnotatePort` on a `tmp_path` inbox (new `tests/e2e/test_api_capture_flatten.py`). Service unit tests use the existing fakes in `tests/unit/test_capture_service.py`. "No change" oracles compare SHA-256 of every file in the inbox and backup dir, and the row, before and after.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-67.1 | integration | Flatten a PNG shot with backups on: 200 `DETAIL_OUT` with `annotations: []`, `annotated_path` and `sidecar_path` null, and `backup_path` equal to the new `BACKUP_NAME` file. That file's SHA-256 equals the pre-flatten original. The original's bytes equal `bake(pre-flatten original, SAVED_MARKS)`, produced independently in the test. Width/height are unchanged; `file_size` is the new size; `updated_at` advanced; the annotated sibling and sidecar are gone. | Spec 09:653, 09:658 | With an older backup already present, `backup_path` must be the new one; an implementation that bakes anything but `SAVED_MARKS` fails the byte oracle |
| AC-67.2 | unit | `FLATTEN_SEQUENCE` order: a recording fake `bake` asserts, when called, that the backup file already exists with the original's SHA-256 and the original is unchanged; the original changes only after `bake` returns. | Spec 09:653 ("**after** saving a backup"); 09:659 | A bake-in-place implementation fails because the fake sees `output_path == original_path` |
| AC-67.3 | unit | `FLATTEN_ROLLBACK`: (a) `bake` raises `CaptureFailedError` → 503; (b) `os.replace` raises `OSError` (monkeypatched) → 409. In both, every inbox file and the row are unchanged, the backup dir listing equals its pre-call listing, and no `TMP_SUFFIX` file remains. | Spec 09:659; D-16 | Leaving the step-3 backup behind fails the listing oracle |
| AC-67.4 | integration | `FLATTEN_CONFLICTS` (a), (b), (c), (d) each → 409 with the standard error envelope, and the no-change oracle holds: (a) no sidecar, and an empty-list sidecar; (b) a registered `.bmp` shot with saved marks; (c) `backup_dir` relative (`"rel/dir"`) and `backup_dir` equal to the inbox; (d) `backup_dir` pointing at an existing **file**. Also a malformed sidecar → 422 and an unknown id → 404, both with no change. | Spec 09:653; D-10, D-11, D-16 | Each case also asserts zero files created anywhere under `tmp_path` |
| AC-67.5 | integration | Boundary: both routes accept a missing body and `{}`; `{"x": 1}` → 422 with no change; both routes without the bearer → 401. | Boundary Input Contract; Local Canon `routes/captures.py:186-193` | The 422 case asserts the original's SHA-256 is unchanged |
| AC-67.6 | integration | `flatten_backup = false`: 200, the original is baked, the annotated sibling and sidecar are gone, no new file is in the backup dir, and `backup_path` = `LATEST_BACKUP` (null with none; the older file's path when one exists). | Spec 09:653, 09:655; D-12 | A backup written while backups are off fails the listing oracle |
| AC-67.7 | integration | Revert after flatten: 200 `DETAIL_OUT`; the original's SHA-256 equals the backup's; the backup still exists; width/height/file_size match the restored file; `updated_at` advanced. `ANNOTATED_CONSISTENCY`: flatten, save new marks, then revert → the annotated sibling's bytes equal `bake(restored original, those marks)` in the current format, and the detail's annotations are those marks. With no marks, no annotated sibling exists and both paths are null. | Spec 09:654; D-14 | A revert that moves (not copies) the backup fails "backup still exists"; a stale annotated file fails the byte oracle |
| AC-67.8 | integration | Revert → 404 with no change when nothing matches `BACKUP_PATTERN`: an empty or absent backup dir; only backups of other stems (`shot_2.…png` for stem `shot`; `shot.20261002-120000.20261002-120001.png`, which belongs to stem `shot.20261002-120000`); a directory named like a backup. An unknown id → 404. | Spec 09:654 | Each decoy is present in the dir, so a prefix match fails |
| AC-67.9 | unit | `BACKUP_NAME` and `LATEST_BACKUP`: the clock gives the timestamp; two flattens in the same second give the base name, then the `_2` name; `LATEST_BACKUP` returns the greatest `(timestamp, n)` even with modification times set in reverse order; stems with regex metacharacters (`a+b`) and dots (`a.b`) match only their own backups. | D-9 | Reverse mtimes make an mtime-based choice fail |
| AC-67.10 | integration | `GET /captures/{id}` carries `backup_path` (`LATEST_BACKUP` or null); `GET /captures` items keep exactly the pre-change key set. | Spec 09:653, 09:657; D-13 | The list key-set equality fails if `backup_path` leaks into `CaptureShotOut` |
| AC-67.11 | integration | Settings: `GET /settings/capture` returns `flatten_backup: true`, `backup_dir: ""` and `annotated_format: "png"` by default, with the four old leaves unchanged; `PUT` round-trips all three. `flatten_backup: "yes"`, `backup_dir: 5` and `annotated_format: "gif"` → 422, each leaving the stored values unchanged. | Spec 09:655; A-2 Q2 | The 422 cases read back the old values |
| AC-67.12 | unit | `BACKUP_DIR_RULE`: `""` → `inbox / BACKUP_DIR_DEFAULT_NAME`; `"~/x"` expands; an absolute path is used as is; a relative path and the inbox itself (also with a trailing separator) raise `CaptureFlattenConflictError`; the dir is created only by a flatten with backups on. | Spec 09:655; D-11 | A flatten refused for (a) must not create the backup dir |
| AC-67.13 | integration | Inbox invariant: after a flatten with the default backup dir, `GET /captures` lists the same shot ids as before, and no backup, `TMP_SUFFIX` file or `ANNOTATED_SUFFIXES` file ever appears as a shot. Electron watcher: `shouldNotifyInboxChange` returns `false` for `BACKUP_DIR_DEFAULT_NAME`, for an `x.png` + `TMP_SUFFIX` name and for `x.annotated.jpg` (Vitest; `ui/src/main` unchanged). | Spec 09:658 | A backup dir equal to the inbox would add a shot; AC-67.4 (c) refuses that before any write |
| AC-67.14 | unit | `CAPTURE_FILE_LOCK`: two threads flatten the same shot while the fake `bake` sleeps 200 ms → exactly one success and one `CaptureFlattenConflictError` (no saved marks once the first finishes); exactly one backup file; the original equals one bake. A `scan_inbox` started during a monkeypatched slow replace waits and does not drop the row. | D-15; Round 1 F6 | Without the lock, two backups appear, or the scan prunes the row |
| AC-67.15 | integration | OpenAPI: `openapi.committed.json` gains exactly the two POST paths (200 → `CaptureShotDetailOut`) and the schema changes are limited to `CaptureShotDetailOut` (+ `backup_path`) and `SettingsPutIn` (+ three leaves). `export_openapi.py --check` passes after the two-step regeneration; no existing path object changes. | G8; Local Canon | The `--check` run before regeneration reports drift (proves the check sees the routes) |
| AC-67.16 | integration | MCP `flatten` / `revert`: without `confirm`, with `confirm: false`, and with an extra key → `isError` with zero `fetch` calls (the Zod parse refuses all three; `strict-confirm.test.ts:41-69` shape). With `confirm: true` and an accepting `confirmWithUser` → exactly one `POST /captures/{id}/flatten` (or `/revert`) with body exactly `{}`, and the JSON result is returned. | Spec 09:656; 05:85-87; Round 1 F2 | The fetch call count is 0 in every refused case |
| AC-67.17 | unit | MCP registry: the `MCP_ACTIONS` rows sit in order after `avkit_capture.remove`; `DESTRUCTIVE_ACTIONS` has both; each description carries ≥ 3 M7 markers; `SETTINGS_SCHEMA.namespaces.capture` has the three `NEW_SETTINGS` keys with their defaults; the strict settings set schema accepts them and rejects a non-boolean `flatten_backup` and an `annotated_format` outside the enum. | Spec 09:656; `NEW_SETTINGS` | Invalid values are refused before fetch |
| AC-67.18 | unit | `INSTRUCTION_TEXT`: `SERVER_INSTRUCTIONS` no longer contains "Files on disk are not deleted"; it contains the capture remove, flatten and revert consequence clauses and the user-confirmation clause, and still contains "Never upload or write to YouTube". | D-19; A-2 Q3 | The old sentence's presence fails |
| AC-67.19 | integration | Audit: `AUDIT_STEPS` and `AUDIT_ISOLATION` exist, and `coverage()` reports no missing action. Fake backend (Round 1 F3 option ii): a test-local `destructiveStep` with `userConfirm: true` over `FIXTURE_REPAIRS` (b) passes the refusal oracle: omitted confirm, `confirm: false` and declined elicitation are each refused with the REST probe unchanged, and the confirmed call changes it. The real-step proof is the container live audit (`audit-container`: `capture.flatten`, `capture.revert` and `capture.remove` all `pass`) and the authoritative Windows audit (`LOCAL_SEQUENCE` step 1: those steps `pass`, flatten/revert with delta `NEW`, no `REGRESSION` or `REMOVED`, cleanup ok, baseline written, every non-pass carrying an issue). | Spec 05:300-302; grouping D-4 | A flatten probe that ignores `backup_count` would let a no-backup flatten pass; the step requires all three fields to change |
| AC-67.20 | integration | GUI Apply: `capture-apply-image` sits in the per-shot actions beside Save overlay and is enabled exactly per `APPLY_ENABLED` (a PNG and a JPEG shot with saved marks are enabled; a `.bmp` shot is disabled with its title). Each disabled reason shows its title (jsdom). Electron: enabled for a PNG shot with saved marks, disabled after one unsaved edit. | Spec 09:657; A-2 Q1 | A dirty overlay keeps it disabled |
| AC-67.21 | integration | GUI flatten confirm: clicking Apply opens the strip with `FLATTEN_CONFIRM_TEXT` (all three variants, jsdom). Cancel sends nothing (Electron ledger `POST …/flatten` = 0). Confirm sends exactly one `POST /captures/{id}/flatten` with body `{}`. While the strip is open, filmstrip, Delete, Apply and Revert are disabled (`CONFIRM_KINDS`). | Spec 09:657; Local Canon 11:287-288 | Cancel path ledger count 0 |
| AC-67.22 | integration | GUI after flatten success: `capture-status` shows `FLATTEN_STATUS`; the mark list is empty, Annotated is disabled, and the view is Original. `IMAGE_REVISION` refetches the viewport image and the thumbnail (Electron ledger: one more `GET …/image` for each). After a 409, `capture-status` shows the API message, and the marks and saved state are unchanged (jsdom). | Spec 09:657-658 | The 409 case asserts no image refetch |
| AC-67.23 | integration | GUI Revert: rendered only when `backup_path !== null` (`REVERT_VISIBLE`); its strip shows `REVERT_CONFIRM_TEXT`; Confirm sends one `POST …/revert` with `{}`, then `FLATTEN_STATUS` and an image refetch; Cancel sends nothing; disabled while dirty. Electron: the flatten → revert round trip on one shot. | Spec 09:654, 09:657, 09:659 | With `backup_path: null` the button is absent |
| AC-67.24 | integration | GUI settings: the Settings page Capture card shows `SETTINGS_LEAVES_UI`; Save sends a `PUT /settings/capture` containing all three leaves. The renderer `capturePutSchema` rejects a non-boolean `flatten_backup`, a non-string `backup_dir` and an `annotated_format` outside the enum (unit). | Spec 09:603, 09:655; A-2 Q2; D-17 | The schema rejections are asserted |
| AC-67.25 | unit | `FLATTEN_HELP_SENTENCE` is appended to the `original-annotated` help body, and the existing sentence is unchanged. | 09:155-157 | The old sentence is asserted verbatim |
| AC-67.26 | unit | `NEW_TESTIDS` are registered after the MEU-66 block and are unique, and the AC-51.6 prefix proof still holds. | Local Canon AC-51.6 | A duplicate id fails |
| AC-67.27 | integration | `CONVERT_ON_APPLY` with backups on, for a real JPEG and a real WebP shot with saved marks. The response is 200 `DETAIL_OUT` for a **new** shot: its `id` differs from the request; its `original_path` is the `CONVERT_NAME` file with a PNG signature; its bytes equal `bake(bake(original, [], png), SAVED_MARKS)` computed independently; its `backup_path` file equals that unmarked PNG. The JPEG/WebP file, its sidecar, its annotated sibling and its row are unchanged (SHA-256 + row). `GET /captures` lists both shots. | D-10 (Human-approved, A-2 Q1); D-22 | A second Apply on the same JPEG creates the `_2` name, not an overwrite. A bake failure injected after the conversion leaves no `CONVERT_NAME` file, row, sidecar or backup, and the JPEG unchanged |
| AC-67.28 | integration | `ANNOTATED_FORMATS`: with `annotated_format` = `jpeg`, Save writes `{stem}.annotated.jpg` (JPEG signature) and no `.annotated.png`/`.webp`; `GET …/image?variant=annotated` returns `image/jpeg`. With `webp`, the sibling is `.annotated.webp` (RIFF/WEBP signature) and the `.jpg` is gone. Back to `png` restores today's file name. `GET /captures` never lists an annotated sibling as a shot. Flatten removes whichever sibling exists; revert re-bakes in the current format. | Human-approved A-2 Q2; D-23 | After a format switch, two annotated siblings must never coexist (the listing oracle) |
| AC-67.29 | unit | `BAKE_PORT` in the adapter: `bake(..., "jpeg")` and `bake(..., "webp")` write those formats at `LOSSY_QUALITY` (the bytes equal the same RGB canvas saved by Pillow with `quality=LOSSY_QUALITY` in the test). `bake(...)` with no format and with `"png"` writes byte-identical files, and every existing `test_capture_adapter.py` assertion stays green unchanged. `validate-task.sh api-scope` proves the drawing is untouched: the AST of `arrowhead_vertices`, `text_plate_box`, `_color_rgb`, `_load_font` and every `_apply*` method in `adapter.py` equals its AST at `baseline.sha`. | A-2 Q2; `PRODUCT_SCOPE` | `bake(..., "gif")` raises `ValidationError` and writes no file |
| AC-67.30 | unit | `USER_CONFIRM` in `handleTool`, for each `USER_CONFIRM_ACTIONS` key with `confirm: true`: `accept` → exactly one fetch with the registered method/path/body; `decline`, `cancel`, `unsupported` and an absent `confirmWithUser` → `isError` whose text contains `user_confirmation_refused` and the outcome, with zero fetches. `confirmWithUser` receives `USER_CONFIRM_MESSAGE` for the action with the id. It is never called for a refused Zod/confirm parse, nor for a non-member destructive action (`avkit_download.remove` with `confirm: true` fetches without asking). | Human-approved A-2 Q3; D-24 | Every refused outcome has fetch count 0 |
| AC-67.31 | integration | `USER_CONFIRM` wiring through the SDK, with a `Client` over an in-memory transport against `createServer()`: a client declaring `elicitation` with a handler returning `accept`/`confirm: true` → `avkit_capture.flatten` reaches the (stubbed) API once; a `decline` handler → refused, zero API calls; a client without the `elicitation` capability → refused as `unsupported`, zero API calls; a handler that throws → refused as `cancel`; `elicitInput` is called with `{timeout: USER_CONFIRM_TIMEOUT_MS}`. | Human-approved A-2 Q3; MCP spec §Elicitation | The no-capability client proves an agent cannot proceed alone |
| AC-67.32 | integration | `AUDIT_ELICITATION`: the audit client declares `elicitation`; its default policy is `decline`; `refusalVerdict` fails a record with `user_confirm: true` whose `refusal_declined` is missing, succeeded, or changed the probe, and judges a `user_confirm: false` record exactly as before (classify unit tests); the container live audit records `refusal_declined` (error, unchanged) for `capture.remove`, `capture.flatten` and `capture.revert`. | D-24; Local Canon REFUSAL_ORACLE | A declined call that mutates fails the step |
| AC-67.33 | integration | GUI convert: for a JPEG shot with saved marks, Apply shows the `CONVERTIBLE` confirm text; Confirm sends one `POST …/flatten`; the response's different `id` becomes the selection (its thumbnail is `aria-current`), `capture-status` shows the convert `FLATTEN_STATUS`, and the JPEG's thumbnail stays in the filmstrip (jsdom + Electron with the mocked list returning the new shot). | A-2 Q1; `IMAGE_REVISION` | The JPEG shot's marks list is unchanged when re-selected |
| AC-67.34 | integration | `ADVERTISED_SCHEMA` through a real SDK `Client` (in-memory) against `createServer()`: every tool's listed `inputSchema` has `properties.action.enum` equal to its `ACTION_INDEX` actions, so `extractSchemaActions` equals `_meta` and `classifyDiscovery` reports no `schema_not_advertised`. `avkit_capture` lists `confirm` as boolean `true` and `id` as a string. A flatten with `confirm: "true"` (string) or with an extra key is still refused, with zero API calls and no elicitation. | Human-approved A-9 | The empty schema (`{type: object, properties: {}}`) fails |
| AC-67.36 | integration | `DIALOG_FALLBACK` through a real SDK `Client` (in-memory) against `createServer({nativeConfirm})`, with a stub dialog: a decline handler answering at once → the dialog is asked once with `USER_CONFIRM_MESSAGE`; dialog `accept` → one API call, `decline`/`cancel` → refused naming that outcome, zero calls. A client without elicitation, or a throwing handler, → the dialog is asked and an accept runs. A decline after `USER_CONFIRM_AUTODECLINE_MS` + 100 ms → no dialog, refused as `decline`. An elicitation `accept` → no dialog. Unit: `nativeConfirm` maps exit 0/1/2/killed to accept/decline/cancel/cancel; the message is only in `AVKIT_CONFIRM_MESSAGE` (not in the args or the decoded script); the timeout is `USER_CONFIRM_TIMEOUT_MS`; off Windows or a spawn failure → `unsupported`. `AUDIT_ANSWER_DELAY_MS` > `USER_CONFIRM_AUTODECLINE_MS`. The default test dialog is `unsupported`, so no test opens a real one. (A-11 review) The tests inject a stepping clock, so there is no wall-time race, and exactly `USER_CONFIRM_AUTODECLINE_MS` counts as the person's answer. One log line per confirmation, with the elicitation and dialog outcome and ms, or `dialog not asked`. `dialogRunner(exec)` maps `execFile` results: null → 0, numeric code → that code, `killed` → null, string code → rejects; it sets `windowsHide`. | Human-approved A-11 | An instant decline that is refused without asking fails |
| AC-67.35 | integration | `DISABLED_REASON_TIP`: with Apply (and Revert) disabled, hovering the wrapper shows the visible `role="tooltip"` reason (jsdom: rendered with the reason text; Electron: `toBeVisible` after a real hover, hidden when enabled). | Human-approved A-10 | No visible label while disabled fails |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Flatten route, body, steps, response, 409 cases | Spec | 09:653 |
| Backup naming collision inside one second | Local Canon | `_unique_png` `_n` suffix (`capture.py:475-485`); D-9 |
| "Newest" backup ordering | Local Canon | name order, never mtime; D-9 |
| Non-PNG originals | Human-approved | D-10 / A-2 Q1: convert on Apply, original untouched |
| Converted file name and the JPEG's own marks | Local Canon | D-22 |
| Save overlay output formats and quality | Human-approved | A-2 Q2; D-23 |
| AI-agent deletes/overwrites through MCP | Human-approved | A-2 Q3; D-24 |
| Default `{inbox}/.avkit-backup` when the inbox changes | Local Canon | `""` = derive, as `ffmpeg_path`; D-11 |
| Backup dir equal to the inbox | Local Canon | would register backups as shots (`capture.py:201-208`); refused (D-11) |
| Flatten with backups off | Spec + Local Canon | 09:653's 409 applies only "when `capture.flatten_backup` is on"; D-12 |
| How the GUI knows a backup exists | Spec | 09:657; `DETAIL_OUT` (D-13) |
| Revert keeps or consumes the backup; marks saved after flatten | Local Canon | D-14 |
| Concurrent flattens and scans | Local Canon | `CAPTURE_FILE_LOCK`; single process (D-15) |
| Error mapping for I/O failures | Local Canon | `DOMAIN_HTTP_MAP` (`errors.py:25-38`); D-16 |
| Where the settings appear | Spec | 09:603 Settings Capture card; D-17 |
| Button variants, confirm text, status text | Local Canon | CP 23/24 (11:287-288); D-18 |
| MCP instructions wording | Spec conflict resolved | 09:487,526 vs 05:274; D-19 |
| Audit baseline sequencing | Local Canon | `BASELINE_UPDATE_RULE`; D-20 |
| Electron proof against mocked REST | Local Canon | `capture-inbox.test.ts:83-170`; the real backend is proven by contract tests and the authoritative audit; D-21 |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/capture.py` | modify | `ANNOTATED_FORMATS`, `ANNOTATED_EXT`, `ANNOTATED_SUFFIXES` |
| `packages/core/src/avkit_core/domain/errors.py` | modify | `CaptureFlattenConflictError(ConflictError)`, appended to `DOMAIN_ERROR_TYPES` (TA-7) |
| `packages/core/src/avkit_core/ports/capture.py` | modify | `BAKE_PORT` output format |
| `packages/core/src/avkit_core/services/capture.py` | modify | `flatten` (incl. `CONVERT_ON_APPLY`), `revert`, `latest_backup`, `resolve_backup_dir`, `BACKUP_NAME`/`BACKUP_PATTERN`/`CONVERT_NAME`, `ANNOTATED_FORMATS` in save/scan, `CAPTURE_FILE_LOCK` |
| `packages/core/src/avkit_core/services/settings.py` | modify | `NEW_SETTINGS` rows |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modify | `bake` output format and `LOSSY_QUALITY`; drawing unchanged |
| `packages/api/src/avkit_api/routes/captures.py` | modify | two POST routes; `_shot_detail_out` carries `backup_path` |
| `packages/api/src/avkit_api/schemas/captures.py` | modify | `CaptureShotDetailOut.backup_path` |
| `packages/api/src/avkit_api/schemas/settings.py` | modify | three `SettingsPutIn` leaves |
| `openapi.committed.json` | modify | regenerated (two-step G8) |
| `tests/unit/test_capture_service.py` | modify | AC-67.2/3/9/12/14 (append); TA-4 |
| `tests/unit/test_capture_adapter.py` | modify | AC-67.29 (append) |
| `tests/unit/test_domain.py` | modify | TA-7 only |
| `tests/unit/test_domain_capture.py` | modify | TA-9 only |
| `tests/e2e/test_api_capture_flatten.py` | new | AC-67.1/4–8/10/11/13/15/27/28 contract tests |
| `tests/e2e/test_api_captures.py` | modify | TA-4, TA-8; `FIXTURE_REPAIRS` (g) |
| `tests/e2e/test_api_downloads.py` | modify | TA-6, TA-8 |
| `tests/e2e/test_api_openapi.py` | modify | TA-8 only |
| `mcp-server/src/toolsets/capture.ts` | modify | two schemas and descriptions |
| `mcp-server/src/toolsets/registry.ts` | modify | `MCP_ACTIONS` rows; `USER_CONFIRM` in `handleTool` and `registerMcpSurface`; `DIALOG_FALLBACK` (A-11) |
| `mcp-server/src/native-confirm.ts` | new | `DIALOG_FALLBACK` dialog (A-11) |
| `mcp-server/src/destructive.ts` | modify | two destructive keys; `USER_CONFIRM_ACTIONS`; `USER_CONFIRM_AUTODECLINE_MS` (A-11) |
| `mcp-server/src/toolsets/settings.ts` | modify | `NEW_SETTINGS` in the schema and Zod |
| `mcp-server/src/index.ts` | modify | `INSTRUCTION_TEXT`; `createServer` options (A-11) |
| `mcp-server/scripts/audit/plan.ts` | modify | `AUDIT_STEPS`; `OutSub`; `destructiveStep` `userConfirm` |
| `mcp-server/scripts/audit/run.ts` | modify | `AUDIT_ISOLATION` |
| `mcp-server/scripts/audit/client.ts` | modify | `AUDIT_ELICITATION` capability and policy; answer delay (A-11) |
| `mcp-server/scripts/audit/classify.ts` | modify | `refusalVerdict` checks `refusal_declined` |
| `mcp-server/scripts/audit/types.ts` | modify | `RefusalRecord.refusal_declined?` |
| `mcp-server/tests/capture.test.ts` | modify | AC-67.16/17/18 (append); TA-1, TA-2, TA-4 |
| `mcp-server/tests/user-confirm.test.ts` | new | AC-67.30/31/34/36 |
| `mcp-server/tests/fixtures.ts` | modify | TA-2 tables; `FIXTURE_REPAIRS` (a) |
| `mcp-server/tests/action-index.test.ts` | modify | TA-1; `FIXTURE_REPAIRS` (e) |
| `mcp-server/tests/convert.test.ts` | modify | TA-1 |
| `mcp-server/tests/m7-resource.test.ts` | modify | TA-1 |
| `mcp-server/tests/audit/coverage.test.ts` | modify | TA-1, TA-3 |
| `mcp-server/tests/audit/classify.test.ts` | modify | AC-67.32 (append) |
| `mcp-server/tests/audit/runner-fake-backend.test.ts` | modify | TA-1; AC-67.19 test-local step (append) |
| `mcp-server/tests/audit/isolation.test.ts` | modify | TA-5 |
| `mcp-server/tests/audit/fake-backend.ts` | modify | `FIXTURE_REPAIRS` (b) |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | Apply/Revert, `CONFIRM_KINDS`, `FLATTEN_STATUS`, `IMAGE_REVISION`, detail `backup_path`, convert selection |
| `ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx` | modify | `IMAGE_REVISION` thumbnail key |
| `ui/src/renderer/src/features/capture/capture-commands.ts` | modify | `flattenCapture(id)`, `revertCapture(id)` beside `deleteCapture` |
| `ui/src/renderer/src/features/capture/capture-flatten.ts` | new | pure `applyEnabled`, `flattenConfirmText`, `revertConfirmText`, `flattenStatus` (the single renderer definitions of `APPLY_ENABLED` and the texts) |
| `ui/src/renderer/src/features/capture/useCaptureSettings.ts` | modify | three leaves |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modify | `FLATTEN_HELP_SENTENCE` |
| `ui/src/renderer/src/features/settings/settings-schemas.ts` | modify | three leaves in `capturePutSchema` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | `SETTINGS_LEAVES_UI` |
| `ui/tests/e2e/test-ids.ts` | modify | `NEW_TESTIDS` |
| `ui/tests/unit/capture-flatten.test.ts` | new | AC-67.20/21/23/33 pure-rule tests |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-67.20–23/33 jsdom (append) |
| `ui/tests/unit/capture-page.test.ts` | modify | AC-67.24 `parseSettingsPut('capture', …)` schema assertions (append) |
| `ui/tests/unit/capture-main.behavior.test.ts` | modify | AC-67.13 watcher assertions (append) |
| `ui/tests/unit/capture-help-content.test.ts` | modify | AC-67.25 (append) |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-67.20–24/33 Electron (append); `FIXTURE_REPAIRS` (c) |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Restoring the deleted sidecar/annotations on Revert | out-of-scope | — | 09:654 defines Revert as restoring the image ("restores the newest backup for that stem over `original_path`"); 09:653 deletes the sidecar on flatten. |
| A retention cap or automatic pruning of backups | out-of-scope | — | 09:655 "no retention cap (the user prunes) — no new governance number" |
| Converting JPEG/WebP on arrival in the inbox, or by a separate Convert button | out-of-scope | — | Human-approved A-2 Q1 ("On Apply to image") |
| A format choice for Apply to image's output | out-of-scope | — | Human-approved A-2 Q2 (the choice is for the Save overlay copy; "Apply to image keeps writing PNG") |
| User confirmation for download/transcript/convert remove and clear | out-of-scope | — | Those keep files on disk (05:130,158); A-2 Q3 scopes the rule to actions that delete or overwrite files |
| Fixing the thin/aliased baked arrow | out-of-scope | — | `CAPTURE-BAKE-ARROW-THIN` (filed 2026-10-02 under Session 29 A-5); `PRODUCT_SCOPE` keeps the drawing unchanged |
| Advertising action schemas in `tools/list` | out-of-scope | — | `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA` is open and not in the 2026-09-30 grouping's coverage (`grouping :17-26`, §1 traceability) |
| Command-palette entries for Apply/Revert | out-of-scope | — | 09:657 names buttons only; `gui-actions-index.md` rows are added with Palette `no` (as `capture:delete`, `:73`) |
| Apply/Revert controls in the Capture page Options panel | out-of-scope | — | 11:89 scopes that panel to inbox and hotkey; D-17 |
| Capture "Open file" opening the annotated copy | out-of-scope | — | Unfiled item from Mat's 2026-09-30 test, pending the user (`current-focus.md` Next steps 2) |
| Header and Settings polish | deferred | MEU-69, MEU-70 | Session 31 (grouping `:110-115`) |

## BUILD_PLAN.md Audit

The D3 hub is `docs/BUILD_PLAN.md` + `docs/build-plan/`. Task row 10 makes these edits, with exact validation (`validate-task.sh hub`):

1. `09-screenshot-capture.md`:
   - §Flatten with backup: add rows for `FLATTEN_INPUTS` + `CONVERT_ON_APPLY` ("Session 30 plan D-10", "… D-22"), the backup naming/collision/newest rule ("… D-9"), `BACKUP_DIR_RULE` ("… D-11"), the `backup_path` detail field ("… D-13"), Revert's keep-backup and re-bake rule ("… D-14"), `ANNOTATED_FORMATS` ("… D-23") and `USER_CONFIRM` ("… D-24").
   - §MCP: the Destructive sentence (`:565`, "Destructive `remove` requires `confirm: true` (M3)") names `flatten` and `revert` and the user confirmation; the action table (`:571-580`) appends `flatten` → `POST /captures/{id}/flatten` and `revert` → `POST /captures/{id}/revert`.
   - The Settings page sentence (`:603`) adds the three leaves.
2. `05-mcp-server.md`:
   - §Destructive gate (`:85-87`) gains one sentence on `USER_CONFIRM` (elicitation for `USER_CONFIRM_ACTIONS`).
   - `:95` adds `flatten`, `revert` to the capture destructive list.
   - The instruction line `:274` becomes `INSTRUCTION_TEXT`.
   - The audit lifecycle row (`:299`) adds `annotate→flatten→revert` to the capture sequence.
3. `11-page-layout.md` §Capture page layout: one prose sentence after `:89`: since MEU-67, the per-shot actions include Apply to image and Revert, behind the same inline confirm strip. The CP rows (`:287-288`) are **not** edited (the AC-50.1/50.4 lock).
4. `gui-actions-index.md`: append `capture:apply_image` and `capture:revert_image` after `capture:delete` (`:73`), with Palette `no`, REST `POST /captures/{id}/flatten` / `…/revert`, status `specified`, source `09`. Append `settings:browse_capture_backup_dir` after `settings:browse_capture_dir` (`:83`). Row 10 re-runs `gui-actions-audit.test.ts`.
5. `docs/BUILD_PLAN.md`: the AUTOGEN status regions are re-rendered by `tools/meu_status.py render` (H1-3 / H2-2) and checked with `render --check`.

## Verification Plan

Every command is registered in `validate-task.sh` (container) and `validate-task.ps1` (Windows), from one stage list. The stage ids match exactly (`windows-gate-check` asserts the order).

### 0. Plan-local static verifier (planning time; re-run in `pregate`)

`python3 docs/execution/plans/2026-10-02-capture-flatten-backup/plan_checks.py static` is stdlib-only and read-only and runs no product code (GUARDRAILS SIGN 1 carve-out). It checks:

- the task table's structure and its dependency graph;
- that every `validate-task.sh` check invoked from `task.md` exists, and every `validate-task.ps1 -Check` named in `local-requests.md` exists;
- that the `.sh` `windows-gate-check` order equals the `.ps1` stage ids;
- that `AUDIT_SRC` and the audit pattern are identical in both scripts;
- that `GATED_PATHS` and `COUNT_FLOORS` equal their executable copies;
- that every `D-n`, `TA-n` and `AC-67.n` named in `task.md` has a definition site;
- that every AC id in the AC table falls inside an `AC-67.a–67.b` range of a `task.md` test row.

Planning receipts are recorded in §Planning receipts.

### 1. Prerequisites and baseline (row 0)

`validate-task.sh prereq`, then `electron-setup` and `baseline`. `baseline` writes `baseline.sha` and collects the baseline pytest failed set and the Vitest, MCP and Electron receipts.

### 2. Red

- `red-py`: pytest assertion Red over the new and appended Python tests (`ac_67`). An import error is tolerated only for the declared new symbols (`PY_SYMBOLS`). Assertion failures in TA-amended tests are listed, and each is dispositioned in the census.
- `red-mcp`: an MCP build, then MCP Vitest assertion Red (`AC-67`; the new `user-confirm.test.ts` may fail only with a missing-module message).
- `red-ui`: UI Vitest assertion Red (`AC-67`; the new `capture-flatten.test.ts` may fail only with a missing-module message), then Electron Red after a fresh build.

### 3. Targeted Green (after each production edit)

`green-py`, `green-mcp` (which builds `mcp-server` first, Round 1 F4) and `green-ui` run the targeted suites plus the regression neighbours named in `validate-task.sh` (`REGPY`, `REGCAP`).

### 4. Targeted gates (rows 6 and 9)

- `gate-cycle1` (row 6): pyright, ruff, targeted pytest, MCP typecheck + build + full MCP Vitest (`mcp_env_ok`, tolerating only `BASELINE_PENDING`), the two-step OpenAPI check/regen with the path/schema diff, and the container audit (`audit-container`).
- `gate67` (row 9): UI typecheck, lint, Vitest (`REGCAP` + targeted), build, the whole `capture-inbox.test.ts` and `settings.test.ts` under Electron, and `--repeat-each=20` over `REPEAT_GREP` into `$RECEIPTS_DIR/s30-repeat-*`.

### 5. Product-scope proof (H1-4)

`validate-task.sh api-scope`:

- `ui/src/main` and `tools` are unchanged versus `baseline.sha` (committed and working tree);
- the drawing functions in `adapter.py` have the same AST as at `baseline.sha`;
- every other changed product file is in the Files Modified table;
- `export_openapi.py --check` passes.

### 6. Container pre-gate (H1-2, non-authoritative)

`validate-task.sh pregate`:

- input identity;
- `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `plan-static`, `task-contract`;
- `pytest_env_ok`, `vitest_env_ok`;
- `ui-build`, `ui-harness-build`, `mcp-build`, `mcp_env_ok`;
- `openapi`, `state-render`;
- `electron_env_ok`;
- `source-audit` over `AUDIT_SRC`.

### 7. `LOCAL_SEQUENCE` (H1-6, authoritative, local)

- **MCP audit.** `validate-task.ps1 -Check audit` (step 1), then `validate-task.sh audit-check` on the cloud side, which checks:
  - summary schema `mcp-audit-summary.v1` and `mode: authoritative`;
  - `capture.flatten`, `capture.revert` and `capture.remove` all `pass`, with deltas `NEW` for the two new actions;
  - no `REGRESSION`/`REMOVED`, cleanup `ok`, and every non-pass `KNOWN` with an issue;
  - the committed baseline covers exactly the served set.
- **Windows gate.** `validate-task.ps1 -Check windows-gate` (step 3) runs the D6 stages; the canonical order is the `order` list in `validate-task.sh windows-gate-check`. Schema `s30-windows-gate.v1`.
- **`FLATTEN_LOOK` F1–F8** (step 4, [local-requests.md](local-requests.md) §GATE). F8 is the real-IDE elicitation check. `validate-task.sh look-check` refuses unless all eight are recorded `pass` with provenance and the tested commit in `walkthrough.md` §FLATTEN_LOOK. Any `fail` is a Decision Brief (cloud-local §3.5).
- **`validate-task.sh windows-gate-check`:** schema, clean tree, stage order and exits, `COUNT_FLOORS`, flaky, and code identity over `GATED_PATHS`.

### 8. OpenAPI drift (G8)

```bash
uv run python tools/export_openapi.py --check openapi.committed.json   # must report drift once the routes exist (AC-67.15 negative)
uv run python tools/export_openapi.py -o openapi.committed.json        # only after the drift above
uv run python tools/export_openapi.py --check openapi.committed.json   # must pass
```

These run inside `gate-cycle1` with receipts `s30-openapi-*`.

### 9. Closeout (H1-5, H1-7, H2)

`validate_closeout_artifacts.py --ac-coverage-only`; `review-check`; the reflection validator with `--decision-source` for the plan, handoff and grouping; `lint_task_contract.py`.

## GUI Element Compliance Check

The §4A reference files are not shipped (`docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md`, `.agent/docs/gui-standards-enforcement.md` absent: `gui-refs-not-shipped`). The applicable canon:

| Element | Variant / size | States | Standard | E2E |
|---|---|---|---|---|
| Apply to image | `secondary`, `sm` | enabled / disabled + reason title | G34, UX2 | AC-67.20 |
| Revert | `secondary`, `sm` | absent / enabled / disabled + title | G34, UX2 | AC-67.23 |
| Confirm strip accept ×2 | `destructive`, `sm` | — | G34; CP 23/24 precedent | AC-67.21, AC-67.23 |
| Confirm strip cancel ×2 | `outline`, `sm` | — | G34 | AC-67.21, AC-67.23 |
| `capture-status` | existing text line | success / error | G26 | AC-67.22 |
| Settings backup checkbox | existing settings toggle component | on/off | G30 | AC-67.24 |
| Settings backup folder | `PathRow` + Browse | value / placeholder | G30, G32 | AC-67.24 |
| Settings Save overlay format | native `select` with `getG30Styles()` | PNG / JPEG / WebP | G30, G32 | AC-67.24 |

G32/G33 are enforced by `source-audit`. E2 is met: every new interactive element has a registered test id and an Electron assertion.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `prereq` refuses: a graph directory appeared, MEU-38 or MEU-60 is not `approved`, or MEU-67 is not `pending` | Stop. Re-run the context-tool gate with the human, or report. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS` | Stop for the human with a Decision Brief naming the test and the minimal amendment. No test edit. |
| S3 | A Red is not an assertion failure (collection or import error outside the declared new symbols/files) | Fix the test setup only, then re-prove Red. |
| S4 | The locked `@modelcontextprotocol/sdk` (1.30.0, `mcp-server/package-lock.json:482-484`) cannot send `elicitation/create` from a tool handler, or cannot report the client's `elicitation` capability | Stop MCP Green for `USER_CONFIRM`. Present a Decision Brief (for example an SDK upgrade, or the off-by-default setting from A-2 Q3's option 2). Never ship the three actions without a user-confirmation path. |
| S5 | `BASELINE_PENDING` fails with any other signature, or `audit-check` shows a `REGRESSION`/`REMOVED` or a non-pass without a prior issue | Stop. The baseline is never hand-edited; present a Decision Brief. |
| S6 | Making AC-67.1 or AC-67.29 pass would need a change to the adapter's drawing functions | Stop. That reopens `PRODUCT_SCOPE` (`CAPTURE-BAKE-ARROW-THIN`); Decision Brief. |
| S7 | A gate failure that is not a product defect | Handle per cloud-local §3.5: a Decision Brief and an A-n row in `human-gate-decision.md`. |
| S8 | Review cap (plan 3, execution 6), or the reviewer is unavailable | HARD STOP with TL;DR (create-plan §5d). |

## Decision Log

Research engine for this plan: `native` (Claude Code `WebSearch`, 2026-10-02). Grouping §8 rows D-1 to D-7 are carried forward unchanged; this plan's ids start at D-8.

```yaml
decision_log:
  - id: D-8
    stage: planning
    question: "What does flatten bake from, and how do the new bytes reach the original?"
    resolution: autonomous
    class: two-way
    chosen: "Bake SAVED_MARKS (the sidecar) with the existing ImageAnnotatePort into a TMP_SUFFIX sibling, then os.replace over the original (ATOMIC_REPLACE). The adapter's drawing is unchanged."
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:653 — bake the saved annotations over original_path"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:143-157 — bake writes an RGB PNG to output_path"
      - "packages/core/src/avkit_core/services/capture.py:43,207 — scan ignores non-image suffixes and .annotated.png"
    research:
      engine: native
      sources:
        - "https://docs.python.org/3/library/os.html#os.replace — rename is atomic when successful (POSIX requirement)"
        - "https://bugs.python.org/issue8828 — on Windows MoveFileEx is usually but not guaranteed atomic"
    reasoning: "Copying the existing .annotated.png would also work, but it can be missing or stale relative to the sidecar; baking SAVED_MARKS follows the spec literally. TMP_SUFFIX is outside SCAN_EXTENSIONS and the watcher's .png filter, so the temp file can never register as a shot. Because Windows replace is not guaranteed atomic, the backup-first ordering is the recovery guarantee (ATOMIC_REPLACE)."
  - id: D-9
    stage: planning
    question: "Backup naming within one second, and which backup is newest?"
    resolution: autonomous
    class: two-way
    chosen: "BACKUP_NAME with an _n suffix on collision; LATEST_BACKUP orders by (timestamp, n) parsed with BACKUP_PATTERN, never by mtime."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:475-485 — _unique_png appends _2, _3 on collision"
      - ".agent/context/known-issues.yaml CAPTURE-FLATTEN-WITH-BACKUP D-15 — [stem].[YYYYMMDD-HHMMSS].png"
    research: { engine: native, sources: [] }
    reasoning: "Two flattens in one second (flatten, revert, flatten) would otherwise overwrite the first backup. Name order is deterministic; mtimes are not (copy tools, sync and backup restores rewrite them). The anchored pattern stops 'shot' from matching 'shot_2' or a dotted longer stem."
  - id: D-11
    stage: planning
    question: "How is capture.backup_dir stored and validated?"
    resolution: autonomous
    class: two-way
    chosen: "BACKUP_DIR_RULE: '' derives inbox/BACKUP_DIR_DEFAULT_NAME at use time; otherwise absolute after expanduser; never the inbox itself; violations are 409 at flatten."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/settings.py:47 — downloader.ffmpeg_path '' means auto"
      - "docs/build-plan/09-screenshot-capture.md:655 — default [inbox]/.avkit-backup"
      - "packages/core/src/avkit_core/services/capture.py:201-208 — the scan reads only the inbox's own files"
    research: { engine: native, sources: [] }
    reasoning: "A literal default path would stop following the inbox when the user moves it. Storing '' keeps the spec's default (09:655) true for every inbox. The inbox itself is refused because every backup would then register as a shot; a subfolder is safe because neither the scan nor the watcher recurses. A relative path would resolve against the API's working directory, which the user cannot see, so it is refused."
  - id: D-12
    stage: planning
    question: "What does flatten do when capture.flatten_backup is off?"
    resolution: autonomous
    class: two-way
    chosen: "Flatten proceeds without a backup; backup_path reports LATEST_BACKUP; the confirm text says it cannot be undone."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:653 — 409 only when flatten_backup is on and the backup failed"
      - "known-issues.yaml CAPTURE-FLATTEN-WITH-BACKUP D-14 — the user asked for the backup to be a setting"
    research: { engine: native, sources: [] }
    reasoning: "The spec's 409 condition only makes sense if flatten runs with backups off. One definition of backup_path (LATEST_BACKUP) is used everywhere rather than a second 'backup just written' field."
  - id: D-13
    stage: planning
    question: "How does the GUI learn that a backup exists?"
    resolution: autonomous
    class: two-way
    chosen: "DETAIL_OUT: backup_path on GET /captures/[id], flatten and revert; the list item shape is unchanged."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:653,657 — flatten returns backup_path; Revert appears when a backup exists"
      - "packages/api/src/avkit_api/routes/captures.py:217-221 — the page already loads the detail per selected shot"
    research: { engine: native, sources: [] }
    reasoning: "Putting it on the list would scan the backup folder once per shot on every poll; the detail is already fetched for the selected shot. Flatten returns the detail shape because the spec puts annotations: [] in its response."
  - id: D-14
    stage: planning
    question: "Does Revert consume the backup, and what happens to marks saved after a flatten?"
    resolution: autonomous
    class: two-way
    chosen: "Revert copies (keeps) the backup and applies ANNOTATED_CONSISTENCY."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:655 — no retention cap, the user prunes"
      - "packages/core/src/avkit_core/services/capture.py:371-419 — the annotated sibling is always bake(original, sidecar)"
    research: { engine: native, sources: [] }
    reasoning: "Keeping the backup makes Revert repeatable and never destroys the only pre-flatten copy. Re-baking keeps the existing invariant that the .annotated.png matches the sidecar; leaving a sibling baked over the flattened image would show stale pixels in the Annotated view."
  - id: D-15
    stage: planning
    question: "What makes concurrent capture file mutations safe?"
    resolution: autonomous
    class: two-way
    chosen: "CAPTURE_FILE_LOCK, a process threading.Lock over scan_inbox, flatten, revert, annotate_and_save and remove (scan_inbox added by Round 1 F6)."
    source_tag: Local Canon
    precedents:
      - "packages/api/src/avkit_api/cli.py:211-231 — a single uvicorn.Server, no workers"
      - ".agent/workflows/create-plan.md:233-236 — every read-then-write names its atomicity mechanism"
    research: { engine: native, sources: [] }
    reasoning: "The API is one process with a thread pool, so a lock is the smallest mechanism that serializes the precondition check with the writes. A database transaction cannot cover file operations."
  - id: D-16
    stage: planning
    question: "How are I/O failures during flatten and revert reported?"
    resolution: autonomous
    class: two-way
    chosen: "FLATTEN_CONFLICTS and FLATTEN_ROLLBACK: OSError on backup or replace is 409 CaptureFlattenConflictError after rollback; bake errors keep their existing 422/503 mapping."
    source_tag: Local Canon
    precedents:
      - "packages/api/src/avkit_api/errors.py:25-38 — ConflictError 409, InboxPathError 422, CaptureFailedError 503"
      - "docs/build-plan/09-screenshot-capture.md:653 — backup failure is 409"
    research: { engine: native, sources: [] }
    reasoning: "The spec already classes an unwritable backup as 409; a locked original (another app holding it on Windows) is the same kind of state conflict. Rollback removes the step-3 backup so a failed flatten leaves the file system exactly as before and does not make Revert appear."
  - id: D-17
    stage: planning
    question: "Where do the three new settings appear in the GUI?"
    resolution: autonomous
    class: two-way
    chosen: "The Settings page Capture card only (SETTINGS_LEAVES_UI, all three leaves)."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:603 — Settings page Capture card holds the capture settings"
      - "docs/build-plan/11-page-layout.md:89 — the Capture page panel is inbox and hotkey"
    research: { engine: native, sources: [] }
    reasoning: "The backup choice is a set-once preference; the Capture page Options panel is the quick inbox/hotkey surface and would wrap at the default window (Session 29 A-5 #1)."
  - id: D-18
    stage: planning
    question: "Button variants, confirm and status text for Apply and Revert"
    resolution: autonomous
    class: two-way
    chosen: "APPLY_ENABLED, REVERT_VISIBLE, FLATTEN_CONFIRM_TEXT, REVERT_CONFIRM_TEXT, CONFIRM_KINDS, FLATTEN_STATUS, IMAGE_REVISION as defined; triggers secondary/sm, accept destructive/sm."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/11-page-layout.md:287-288 — CP 23/24 inline confirm strips with destructive accept"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:975-1006 — the strip pattern"
      - "ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx:58-78 — thumbnails keyed on id only"
    research:
      engine: native
      sources:
        - "https://www.peachpit.com/articles/article.aspx?p=3104542&seqNum=10 — flattening is destructive; keep a copy first"
    reasoning: "Both actions overwrite the original file, which is what the destructive accept variant marks in CP 23/24. The exact backup file name is chosen when flatten runs, so the strip names the folder. Without IMAGE_REVISION the viewport and thumbnail would keep showing the pre-flatten image."
  - id: D-19
    stage: planning
    question: "Fix the MCP instruction 'Files on disk are not deleted'?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: INSTRUCTION_TEXT, resolving MCP-INSTRUCTIONS-CAPTURE-REMOVE-FILES in this session."
    source_tag: Local Canon
    precedents:
      - "mcp-server/src/index.ts:10 and docs/build-plan/05-mcp-server.md:274 — the current sentence"
      - "docs/build-plan/09-screenshot-capture.md:487,526 — capture remove deletes files"
      - "known-issues.yaml MCP-INSTRUCTIONS-CAPTURE-REMOVE-FILES — reproduced 2026-10-01"
    research: { engine: native, sources: [] }
    reasoning: "This plan must edit that exact line to describe flatten and revert; keeping 'Files on disk are not deleted' next to 'flatten overwrites the original' would make the instruction self-contradictory and tell an IDE agent the wrong consequence of a confirm:true call. The fix is one sentence on a line already in scope."
  - id: D-20
    stage: planning
    question: "How is the audit baseline updated without hand-editing it or tolerating anything at the gate?"
    resolution: autonomous
    class: two-way
    chosen: "LOCAL_SEQUENCE: authoritative audit with --update-baseline, then baseline_carry.py restores prior issue ids, committed before WINDOWS_GATE; container-only BASELINE_PENDING tolerance with an exact signature."
    source_tag: Local Canon
    precedents:
      - ".agent/skills/mcp-tool-audit/SKILL.md:49-51 — BASELINE_UPDATE_RULE and BASELINE_ANNOTATION_RULE"
      - "mcp-server/tests/audit/coverage.test.ts:74-80 — committed baseline must equal the served set"
      - "mcp-server/scripts/audit/run.ts:584-594 — a written baseline carries no issue ids"
      - "grouping D-4 — Session 30's two actions are a baseline row, not a reopen"
    research: { engine: native, sources: [] }
    reasoning: "Only a win32 authoritative run may write the baseline, and the written file drops issue ids that coverage.test.ts requires, so the issues must be carried over mechanically. Running the audit first means the gate runs on a commit where the full MCP suite passes with zero tolerance. baseline_carry.py copies ids only for identical keys and refuses any new non-pass, so it cannot hide a regression."
  - id: D-21
    stage: planning
    question: "Is the Electron flatten → revert case against the real backend?"
    resolution: autonomous
    class: two-way
    chosen: "Against the existing mocked REST routes with a request ledger; the real backend is covered by the contract tests, the authoritative audit and FLATTEN_LOOK."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/capture-inbox.test.ts:83-170 — every capture Electron case uses page.route mocks"
      - "docs/build-plan/09-screenshot-capture.md:659 — one Electron case flatten → revert"
    research: { engine: native, sources: [] }
    reasoning: "The capture Electron wave has always mocked REST, and the GUI contract is what the request ledger proves. The file-level behaviour is proven by AC-67.1–67.8 with the real Pillow adapter and by the authoritative audit against a real backend."
  - id: D-10
    stage: planning
    question: "Should Apply to image work only on PNG originals?"
    resolution: human
    class: product-preference
    chosen: "Process PNG only; a JPEG/WebP shot is converted on Apply to a new PNG copy (marks carried over, then flattened with the usual backup) and the original file is left untouched (CONVERT_ON_APPLY)."
    source_tag: Human-approved
    precedents:
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:143-157 — the bake writes PNG"
      - "packages/core/src/avkit_core/services/capture.py:43 — the inbox admits .jpg/.jpeg/.webp"
    research:
      engine: native
      sources:
        - "https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html — lossy re-encode and quality limits"
        - "https://en.wikipedia.org/wiki/Generation_loss — every lossy re-encode adds loss"
    reasoning: "The planner recommended PNG only with a 409 for other formats. The user agreed with PNG-only processing but required that every format be accepted, by converting to PNG and leaving the original be; A-2 Q1 placed the conversion at Apply time."
    human_message_reference: "USER_EXPLICIT 2026-10-03 'D-10: create converter that will change JPEG and WEBP to PNG ... Agree with processing PNG only. But user experience has to be able accept all formats and auto covert them to PNG while leaving the original file be.' + AskUserQuestion 'On Apply to image (Recommended)'"
  - id: D-22
    stage: planning
    question: "What is the converted PNG called, and what happens to the JPEG's own marks?"
    resolution: autonomous
    class: two-way
    chosen: "CONVERT_NAME ([stem]-converted.png, then _n); the JPEG/WebP file, sidecar, annotated sibling and row are never touched; the new shot inherits the original's source."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:382-387 — sidecar and annotated names derive from the stem alone"
      - "packages/core/src/avkit_core/services/capture.py:475-485 — _n collision suffix"
    research: { engine: native, sources: [] }
    reasoning: "The option text said '[stem].png'. A same-stem PNG would share [stem].ann.json and [stem].annotated.* with the JPEG, so flattening it would delete the JPEG's saved marks and break 'leaving the original file be'. A distinct stem keeps both shots independent. Leaving the JPEG's marks in place means nothing about the original changes, which is what the user asked for."
  - id: D-23
    stage: planning
    question: "How do JPEG/WebP Save overlay copies coexist with today's .annotated.png?"
    resolution: autonomous
    class: two-way
    chosen: "ANNOTATED_FORMATS: one annotated sibling at a time ([stem].annotated.png|.jpg|.webp), the others unlinked on save; the scan skips all three; LOSSY_QUALITY 90 (from the approved option text); the format applies when Save overlay runs, not retroactively."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:46,207 — the scan skips .annotated.png only"
      - "packages/api/src/avkit_api/routes/captures.py:45-50 — media type by suffix, .jpg/.webp already mapped"
      - "mcp-server/src/client.ts:160-180 — MCP image sniffs the MIME type from the bytes"
    research:
      engine: native
      sources:
        - "https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html — JPEG quality ≤ 95; WebP quality"
    reasoning: "Two annotated siblings would make GET ?variant=annotated ambiguous and leave stale bakes behind. '.jpg' is the extension the inbox and IMAGE_MIME_MAP already use. Re-encoding existing annotated copies when the setting changes would be a silent bulk rewrite; the next Save applies the format instead."
  - id: D-24
    stage: planning
    question: "How exactly does the MCP user confirmation behave?"
    resolution: autonomous
    class: two-way
    chosen: "USER_CONFIRM via elicitation for USER_CONFIRM_ACTIONS (remove, flatten, revert); only accept+confirm=true proceeds; no capability, decline, cancel, error or timeout refuse with user_confirmation_refused; the prompt shows only USER_CONFIRM_MESSAGE with the validated id; the audit client answers its own disposable-fixture prompts (AUDIT_ELICITATION, default decline)."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/05-mcp-server.md:85-87 — the destructive gate this extends"
      - "mcp-server/src/toolsets/registry.ts:257-273 — Zod then confirm, before any fetch"
      - "mcp-server/scripts/audit/plan.ts:191-251 — the destructive refusal oracle"
    research:
      engine: native
      sources:
        - "https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation — servers request structured user input through the client"
        - "https://cursor.com/changelog/1-5 — Cursor supports MCP elicitation (v1.5)"
        - "https://claude-world.com/articles/claude-code-2176-release/ — Claude Code 2.1.76 added MCP elicitation"
        - "https://github.com/anthropics/claude-code/issues/41110 — Claude Desktop does not support elicitation"
    reasoning: "The user chose elicitation and said an agent must never do it alone, so every non-accept path fails closed, including clients without elicitation (Claude Desktop). Remove is included because it deletes files (09:487,526); download/transcript/convert remove keep files. Interpolating only the id stops an agent from writing a misleading prompt. The audit is a user-started run against fixtures in an isolated root, so its client answering is the operator's own answer; the declined-call refusal keeps the control observable there."
```

### D-10 — Should Apply to image work only on PNG originals? (resolved by the user, 2026-10-03)

**Outcome:** PNG-only processing, with conversion of JPEG/WebP on Apply to a new PNG copy, leaving the original file untouched (A-2 Q1; `decision_log` D-10). The planner's brief recommended a 409 for non-PNG files. Its options compared a 409 refusal (A), lossy re-encoding in place (B) and a new PNG beside the original (C). The user chose a variant of C, applied only at Apply time, and refined by D-22 (a distinct stem). Option B's generation-loss concern does not arise, because nothing is re-encoded lossily: the conversion decodes to a lossless PNG.

## Round 1 Review Corrections

The Round 1 verdict was `changes_required`: 1 High (blocking), 4 Medium, 5 Low (`.agent/context/handoffs/2026-10-02-capture-flatten-backup-plan-critical-review.md`). Each finding and how this revision closes it:

| Finding | Correction |
|---|---|
| F1 High: `ROUTE_COUNT_AFTER` and `DOMAIN_ERROR_TYPE_NAMES` pins outside `TEST_AMENDMENTS` | TA-6 and TA-7 added; `CaptureFlattenConflictError` joins `DOMAIN_ERROR_TYPES`; the census `rg` gains `ROUTE_COUNT`, `DOMAIN_ERROR_TYPE`, `openapi.committed`, `test_api_downloads`; both test files are in Files Modified and `REGPY`; task rows 2 and 4 name them; human-gate-decision.md records their approval basis. |
| F2 Medium: `confirm_required` unreachable | AC-67.16 asserts `isError` with zero fetches (the strict-confirm shape). |
| F3 Medium: fake-backend clause undeliverable | Option (ii): a test-local `userConfirm` step over `FIXTURE_REPAIRS` (b); the real-step proof stays on `audit-container` and the authoritative run (AC-67.19). |
| F4 Medium: `green-mcp` without a build | `red-mcp` and `green-mcp` build `mcp-server` first. |
| F5 Medium: `hub` read the wrong paragraph | `hub` now checks the line containing "Destructive `remove`" for `flatten`, `revert` and the user confirmation. |
| F6 Low: `scan_inbox` outside the lock | `CAPTURE_FILE_LOCK` covers `scan_inbox`; AC-67.14 adds the slow-replace scan negative. |
| F7 Low: stale statements and line refs | human-gate-decision.md A-1 sentence corrected; the D-12 spec-sufficiency row is now "Spec + Local Canon"; TA-2 (`fixtures.ts:79-88`, `:119-127`), TA-3 (`coverage.test.ts:46-57`) and settings.ts (`:63-68,123-126`) refs fixed; the census prose now describes the source re-proof the script performs. |
| F8 Low: restated literals | `BACKUP_DIR_DEFAULT_NAME` and `TMP_SUFFIX` are named once and referenced by name. |
| F9 Low: a carry refusal left a rewritten baseline | `validate-task.ps1 -Check audit` restores the prior baseline before exiting on a carry refusal. |
| F10 Low: `IMAGE_REVISION` delivery | It names the list-query invalidation, the detail reload, and both effect keys. |
| Observations 1–5 | 1: `APPLY_ENABLED` lowercases the suffix. 2: `CAPTURE_FILE_LOCK` states non-reentrancy and the private-helper rule. 3: the TA-1 `m7-resource.test.ts:47` title is fixed. 4: the `LOCAL_SEQUENCE` request warns that `.agent/docs` edits reopen the gate. 5: `look-check` shape noted in the request. |

**Also in this revision (user decisions of 2026-10-03, not review findings):** `CONVERT_ON_APPLY`/`CONVERT_NAME` (D-10, D-22), `ANNOTATED_FORMATS`/`LOSSY_QUALITY`/`BAKE_PORT` (D-23), `USER_CONFIRM`/`USER_CONFIRM_ACTIONS`/`USER_CONFIRM_MESSAGE`/`AUDIT_ELICITATION` (D-24), ACs AC-67.27–67.33, `FLATTEN_LOOK` F6–F8, and Stop condition S4 (SDK elicitation capability).

**Blast-radius census (plan-corrections Step 5c).** Every place that restated a value this revision changed was swept with `rg` over the plan folder:
- the TA count (TA-1..TA-5 → TA-1..TA-7);
- the capture settings key count (4 → 7);
- `PNG_ONLY` (removed; replaced by `FLATTEN_INPUTS`);
- the confirm-strip folder text;
- the frozen-path list (`packages/infrastructure` unfrozen, with the drawing guarded);
- the `look-check` item count (F1–F5 → F1–F8);
- the `MCPT`/`REGPY` membership;
- `AUDIT_SRC`.

The full receipt is [review-r2-census.md](review-r2-census.md): raw `rg -F -n` output per value, old and new spellings, and a per-hit disposition. Round 2 notes N1–N4 are applied: (f) in `FIXTURE_REPAIRS`, `RefusalRecord.user_confirm`, `elicitation.form` and `USER_CONFIRM_TIMEOUT_MS`, the D-17 wording and the `09:565` citation.

## Research References

- `docs/build-plan/09-screenshot-capture.md` §Flatten with backup, §MCP, Settings page sentence
- `docs/build-plan/05-mcp-server.md` §Destructive gate, server instructions, §MCP live audit
- `.agent/skills/mcp-tool-audit/SKILL.md` (`BASELINE_UPDATE_RULE`, `BASELINE_ANNOTATION_RULE`)
- `.agent/docs/cloud-local-collaboration.md`
- https://docs.python.org/3/library/os.html#os.replace
- https://bugs.python.org/issue8828
- https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
- https://en.wikipedia.org/wiki/Generation_loss
- https://www.peachpit.com/articles/article.aspx?p=3104542&seqNum=10
- https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation
- https://cursor.com/changelog/1-5
- https://claude-world.com/articles/claude-code-2176-release/
- https://github.com/anthropics/claude-code/issues/41110

## Planning receipts

All read-only, run 2026-10-02 in the container from `477579d` + the uncommitted plan folder; receipts under the scratchpad `receipts/` (non-durable; the decisive lines are copied here).

| Check | Command | Exit | Decisive output |
|---|---|---|---|
| Plan-local verifier | `python3 docs/execution/plans/2026-10-02-capture-flatten-backup/plan_checks.py static` | 0 | `PASS static: 21 task rows; scripts and plan cross-references agree` |
| Task contract lint | `uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task …/task.md` | 0 | `OK: 21 row(s); 10-column table (with builder_model); 21 row(s) fully checked` |
| `validate-task.sh` syntax | `bash -n …/validate-task.sh` | 0 | — |
| Verifier negative cases (V4), each on a scratch copy | COUNT_FLOORS 748→700 in the plan; AC range `67.20–67.26`→`67.25`; `docs/proposals` dropped from the `.sh` gated list; `validate-task.sh hub`→`hubx`; `-Check audit`→`auditx` in `local-requests.md`; `TA-4`→`TA-9` in `task.md`; `.ps1` floor 629→600 | 1 ×7 | `COUNT_FLOORS differ …`; `ACs not covered … [26]`; `GATED_PATHS differ …`; `invokes validate-task.sh 'hubx', not a case label`; `names -Check 'auditx' …`; `references TA-9, which has no definition site`; `COUNT_FLOORS differ … ps1_floor=600` |
| `baseline_carry.py` on synthetic copies of the committed baseline | issue ids stripped, `recorded_commit` changed, two `pass` entries added | 0 | `PASS baseline_carry: 9 issue ids carried; 70 entries`; carried ids equal the committed ones |
| `baseline_carry.py` negative cases | a new `fail` entry with no prior issue; an unchanged `recorded_commit` | 1 ×2 | `non-pass items with no prior issue … avkit_capture.revert (fail)`; `the baseline was not rewritten by this run` |
| `BASELINE_PENDING` re-proof input | registry regex vs committed baseline entries | 0 | `68 68 True` (the proof sees today's served set exactly) |

The `.ps1` is not executable here (no `pwsh`); the plan review reads it against the `.sh` (cloud-local §2).


**Round 2 (2026-10-03, after the Round 1 corrections and the user's A-2 decisions):**

| Check | Command | Exit | Decisive output |
|---|---|---|---|
| Plan-local verifier | `python3 …/plan_checks.py static` | 0 | `PASS static: 21 task rows; scripts and plan cross-references agree` |
| Task contract lint | `uv run python tools/lint_task_contract.py … --task …/task.md` | 0 | `OK: 21 row(s); 10-column table (with builder_model); 21 row(s) fully checked` |
| `validate-task.sh` syntax | `bash -n …/validate-task.sh` | 0 | — |
| Verifier negative cases, each on a scratch copy | COUNT_FLOORS 748→700; `AC-67.33` dropped from row 7; `docs/proposals` dropped from the `.sh` gated list; `hub`→`hubx`; `-Check audit`→`auditx`; `TA-7`→`TA-9` in row 2; `client.ts` dropped from the `.ps1` audit list | 1 ×7 | each refused by its check |
| F5 proof: the `hub` python on a scratch copy of `docs/build-plan` | flatten/revert/elicitation added only to the Phase 5 exception paragraph | 1 | `FAIL: 09 §MCP Destructive sentence does not name flatten, revert and the elicitation confirmation` |
| F5 positive control | the same copy with the Destructive line itself edited | 1, at the next check | `FAIL: 09 Settings page sentence lacks the three leaves` (the Destructive predicate passed) |

## Validation stage contract

Checks bind to PROFILE D6 through `validate-task.sh` (container) and `validate-task.ps1` (Windows): static (`py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `plan-static`, `task-contract`), targeted (`red-*`, `green-*`, `gate-cycle1`, `gate67`) and one fresh full scoped gate (`WINDOWS_GATE`) before the final review. Evidence is `evidence.v1` in the handoff and `walkthrough.md`; scratch receipts alone are not proof. Input identity is the tested commit plus the lockfile, `uv.lock` and preflight hashes in the result JSON, and `windows-gate-check` refuses any `GATED_PATHS` change after it. Any later gated-path commit reopens the gate (cloud-local §3.4).
