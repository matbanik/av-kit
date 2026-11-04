---
date: "2026-10-02"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md"
round: 3
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "claude-fable-5-1-subagent"
---

# Critical Review: 2026-10-02-capture-flatten-backup

> **Review Mode**: `plan`
> **Verdict**: `changes_required` (Round 1 of 3 — 1 High/blocking, 4 Medium, 5 Low; no Critical)
> **Reviewer**: Fable 5.1 subagent in a separate context, user-authorized route per `docs/execution/plans/2026-10-02-capture-flatten-backup/human-review-decision.md` (same-vendor deviation disclosed there). The reviewer did not author the plan and wrote this verdict itself. Reasoning effort: `high`, as requested in the dispatch prompt.

---

## Intent Anchor

Executing this plan is supposed to deliver MEU-67 `capture-flatten-backup`: a permanent **Apply to image** that bakes the saved marks into the original PNG only after copying it to a backup folder (both governed by two new `capture` settings), a **Revert** from the newest backup, exposed on REST (`POST /captures/{id}/flatten|revert`, `backup_path` on the detail), on MCP as two destructive `confirm: true` actions with truthful server instructions and two audit steps, and on the Capture page behind the existing inline confirm strip — delivered under the Sessions 25–29 cloud/local split with one authoritative `LOCAL_SEQUENCE` (audit → baseline carry → `WINDOWS_GATE` → `FLATTEN_LOOK`). The verdict question is whether executing the plan as written reaches that without an unplanned human stop. It does not: one existing Python pin the design breaks is outside `TEST_AMENDMENTS` and invisible to the row-1 census, so execution halts at H1-2 with no authorized amendment (F1).

---

## Scope

**Target**: `docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md`, `task.md`, and the plan-local files they invoke: `validate-task.sh`, `validate-task.ps1` (read against the `.sh`; no `pwsh` here), `plan_checks.py`, `baseline_carry.py`, `local-requests.md`, `human-gate-decision.md`, `human-review-decision.md`.
**Review Type**: plan review (unstarted: no MEU-67 handoff, no `baseline.sha`, clean tree at `5168586`)
**Checklist Applied**: PR (PR-1 … PR-9) + DR-6 cross-reference integrity + the five focus areas of the dispatch (contracts, `TEST_AMENDMENTS` completeness, audit/baseline sequencing, script correctness, decision quality), then GUI/E2E, hub and docs.

Source canon read and line-checked: `docs/build-plan/09-screenshot-capture.md` (`:645-659`, `:562-582`, `:603`, `:487`, `:526`, `:155-157`), `05-mcp-server.md` (`:85-95`, `:270-305`), `11-page-layout.md` (`:87-89`, `:287-288`), the 2026-09-30 grouping (Session 30, §8), `known-issues.yaml` (both issues), `services/capture.py`, `services/settings.py`, `domain/errors.py`, `capture/adapter.py`, `routes/captures.py`, `schemas/captures.py`, `schemas/settings.py`, `api/errors.py`, `api/cli.py`, `mcp-server/src/{toolsets/capture,toolsets/registry,toolsets/settings,destructive,index}.ts`, `scripts/audit/{plan,run,classify,census,report,types}.ts`, every file under `mcp-server/tests`, the capture/settings renderer files, `ui/src/main/capture-inbox-watch.ts`, `ui/tests/e2e/{capture-inbox.test.ts,test-ids.ts}`, the UI unit suites named in `REGCAP`, `.agent/skills/mcp-tool-audit/SKILL.md` + `resources/baseline-snapshot.json`, and the Session 29 / Session 27 peer plans.

---

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | **`TEST_AMENDMENTS` is incomplete: an existing Python pin the design breaks is outside TA-1..TA-5 and outside the census.** `tests/e2e/test_api_downloads.py:372` sets `ROUTE_COUNT_AFTER = 71` and `:424` asserts `len(operations) == ROUTE_COUNT_AFTER` over `openapi.committed.json` (reproduced: 71 operations today). AC-67.15 adds two POST operations → 73, so this assertion fails on every full pytest run after the OpenAPI regeneration. The targeted sets (`PYT`, `REGPY`) never run it; the first run that does is `pregate` → `pytest_env_ok` (H1-2), which refuses it as "new pytest failures versus baseline.sha", and `WINDOWS_GATE py-tests` (zero tolerance) would refuse it too. Row 1's census regex (`validate-task.sh:431-438`) has no pattern that reaches it (`ROUTE_COUNT`, `openapi.committed`, `operations`), so S2 does not fire at row 1 either; the plan reaches H1-2 with no authorized amendment and must stop for a human (AGENTS §Testing: a proven wrong expectation needs a source-backed amendment plus explicit authorization). Same surface, second pin: `tests/unit/test_domain.py:181-214` pins `DOMAIN_ERROR_TYPES` as an exact ordered name list; the plan adds `CaptureFlattenConflictError(ConflictError)` (Files Modified, `errors.py` row) without saying whether it joins the tuple, whose sibling `CaptureRequestConflictError` is a member (`errors.py:251`). If it joins, that pin breaks with no TA; if it does not, the tuple silently stops being the full subclass list. | `implementation-plan.md:143,151-157`; `task.md` rows 1, 2; `validate-task.sh:431-438`; `tests/e2e/test_api_downloads.py:372,424`; `tests/unit/test_domain.py:181-214` | Add **TA-6**: `test_api_downloads.py:372` `ROUTE_COUNT_AFTER` 71 → 73 with a `# TA-6 (Session 30, MEU-67)` note (Spec 09:653-654; the Session 27 TA-9 shape). Decide the tuple: either **TA-7** (`DOMAIN_ERROR_TYPE_NAMES` + the tuple gain `CaptureFlattenConflictError` after `CaptureRequestConflictError`) or an explicit sentence in the `errors.py` Files Modified row that `DOMAIN_ERROR_TYPES` is untouched. Add `ROUTE_COUNT`, `DOMAIN_ERROR_TYPE`, `openapi.committed` and `test_api_downloads` to the census `rg` patterns. Update User Review item 3, the `TEST_AMENDMENTS` row, task rows 2/4 ("Apply TA-…"), and `test_api_downloads.py` in Files Modified. | open |
| F2 | Medium | no | behavior | **AC-67.16 names an error code the prescribed schema cannot produce.** `MCP_ACTIONS` gives both actions `confirm: z.literal(true)` in `captureSchema`, mirroring `remove` (`capture.ts:147`) and download (`download.ts:86-87`). `handleTool` runs `schema.safeParse` before `confirmMissing` (`registry.ts:263-273`), so an omitted or `false` confirm is refused as `validation_error` and `confirm_required` is unreachable — already true for every existing destructive action, which is why `strict-confirm.test.ts:41-69` asserts only `isError` and zero fetch calls. A Red written to "`TOOL_ERROR confirm_required`" cannot go Green without editing the assertion in Green (forbidden) or switching the schema to `z.boolean().optional()` (a departure from the `remove` precedent the plan does not authorize). The fetch-count negative oracle is sound. | `implementation-plan.md:129` (`MCP_ACTIONS`), `:209` (AC-67.16); `mcp-server/src/toolsets/registry.ts:263-273`; `mcp-server/src/toolsets/capture.ts:147` | Restate AC-67.16's refusal oracle as "`isError` with zero `fetch` calls" (the strict-confirm shape) or name `validation_error`; keep "confirm: true → exactly one POST with body `{}`". | open |
| F3 | Medium | no | behavior | **AC-67.19's fake-backend clause is not deliverable with `FIXTURE_REPAIRS` (b).** The fake backend serves no capture lifecycle: `fake-backend.ts:130-132` answers only `GET /captures` → `{items: []}`; there is no register, detail, annotate, image or file on disk. `AUDIT_STEPS` obtains `shot_id` from `capture.capture` / the container's REST register seed (`plan.ts:1328-1358`) and the plan's flatten probe reads `original_sha256`, `annotated_exists`, `backup_count` from the filesystem. (b) adds only `POST …/flatten|revert` returning a `DETAIL_OUT` shape, so against the fake backend the probe can never change and the real steps cannot pass. The existing suite proves the refusal oracle with test-local specs (`runner-fake-backend.test.ts:39-62` `ADD`/`REMOVE`), not with `AUDIT_PLAN` steps. | `implementation-plan.md:144` (b), `:212` (AC-67.19); `mcp-server/tests/audit/fake-backend.ts:130-132`; `mcp-server/scripts/audit/plan.ts:1328-1358` | Either (i) widen (b) to a capture subset that registers a real PNG under the root, serves `GET /captures/{id}` with real paths, and makes flatten/revert rewrite the file and backup dir so the real `AUDIT_STEPS` probes move; or (ii) scope the fake-backend clause of AC-67.19 to test-local `destructiveStep` specs with a REST-only probe (as `REMOVE` does) and keep the real-step proof on `audit-container` and the authoritative run. State which. | open |
| F4 | Medium | no | behavior | **`green-mcp` (row 5's validation) cannot go Green as written.** `MCPT` includes `tests/audit/runner-fake-backend.test.ts`, which launches `dist/index.js` (`:12,66`) and, after TA-1, expects `discovery.actions` to be 70 (`:75`). `green-mcp` runs `mcp_env_ok` with no `npm --prefix mcp-server run build` (`validate-task.sh:451-453`), unlike `baseline` (`:422`) and `gate-cycle1` (`:459`). The dist on disk is the row-0 build, so the step false-fails until an undocumented build. Never a false-pass. | `validate-task.sh:451-453`; `task.md` row 5; `mcp-server/tests/audit/runner-fake-backend.test.ts:12,66,75` | Add `run s30-green-mcp-build npm --prefix mcp-server run build` before `mcp_env_ok` in `green-mcp` (and in `red-mcp` if the runner suite is to be a Red participant), or exclude the runner suite from `MCPT` for the targeted steps. | open |
| F5 | Medium | no | control-defeat | **`hub` tests the wrong paragraph for the extended Destructive sentence** — `mechanism: predicate-targets-wrong-paragraph`. `validate-task.sh:523` checks `"flatten" in mcp.split("\n\n", 2)[1]`; run against the current `09-screenshot-capture.md`, `[1]` is the "**Phase 5 exception (dated 2026-08-26)**" paragraph, while the sentence the plan edits ("Destructive `remove` requires `confirm: true` (M3)", `09:564`) is `[0]`. Demonstrated false-pass: add "flatten" to the Phase 5 paragraph and leave `:564` unchanged → PASS; the intended edit alone → FAIL. The 09 §MCP table rows, Settings sentence, 05 and 11 edits are checked correctly. | `validate-task.sh:519-524`; `docs/build-plan/09-screenshot-capture.md:564-566` | Test the paragraph that contains "Destructive `remove`" (i.e. `parts[0]`, or the matching line) for both `flatten` and `revert`. | open |
| F6 | Low | no | behavior | **`scan_inbox` prunes rows on a missing original and is outside `CAPTURE_FILE_LOCK`.** `capture.py:239-241` deletes every row whose `original_path.is_file()` is false; `list_shots` (`:244-247`) runs it on each `GET /captures`, which the renderer refetches on every `captures:inbox-changed` the watcher emits for exactly the fs activity flatten causes (tmp write, replace). D-15 says the lock "serializes every capture file mutation", but `scan_inbox` is not listed. On Windows, where `ATOMIC_REPLACE` concedes `os.replace` is not guaranteed atomic, a concurrent scan during step 5 can see the original absent and delete the row that step 7 then saves. Low because the window is tiny on NTFS and the GUI self-heals on the next scan. | `implementation-plan.md:123,126` (`ATOMIC_REPLACE`, `CAPTURE_FILE_LOCK`); `packages/core/src/avkit_core/services/capture.py:239-247` | Hold `CAPTURE_FILE_LOCK` across `scan_inbox` (or its prune loop) and name it in `CAPTURE_FILE_LOCK`/D-15; optionally one unit negative: a scan during a monkeypatched slow replace must not drop the row. | open |
| F7 | Low | no | clerical | Stale or contradictory statements: (a) `human-gate-decision.md:26` "approves no change to existing test expectations (`TEST_AMENDMENTS` is empty)" contradicts the plan's TA-1..TA-5 and User Review item 3, which routes their approval through the execution message; (b) spec-sufficiency row "Flatten with backups off — Spec + **Human-approved** — D-12" while D-12 is `autonomous` / `Local Canon`; (c) line refs: TA-2 `DESTRUCTIVE_KEYS` is `fixtures.ts:119-127` (not `:50-57`), TA-3 is `coverage.test.ts:46-57` (not `:44-55`), the Zod settings leaves are `settings.ts:123-126` (not `:122-125`); (d) the census row says `mcp_env_ok` tolerates on "its failure message shows `missing` …" while the script proves it from the sources (`validate-task.sh:211-217`, the stronger check) — align the prose to the script. | `human-gate-decision.md:26`; `implementation-plan.md:128,154,155,167,231` | One-line corrections each; for (a) say the execution message approves TA-1..TA-n (plus any added by F1). | open |
| F8 | Low | no | clerical | PR-9 restated literals: the default backup folder name `.avkit-backup` / `{inbox}/.avkit-backup` is spelled at seven sites (`BACKUP_DIR_RULE` is canonical; also `FLATTEN_CONFIRM_TEXT`, `SETTINGS_LEAVES_UI` placeholder, AC-67.12, D-11 chosen + reasoning, User Review item 5, `local-requests.md` F2) and the temp suffix `.avkit-tmp` at four (`FLATTEN_SEQUENCE` canonical; AC-67.3, AC-67.13, D-8). No two spellings disagree today. | `implementation-plan.md:98,116,121,122,135,140,196,205,206,452,459`; `local-requests.md:45` | Name them (`BACKUP_DIR_DEFAULT_NAME`, `TMP_SUFFIX`) in §Single-statement contracts and reference by name. | open |
| F9 | Low | no | behavior | **A `baseline_carry.py` refusal leaves a rewritten, issue-less baseline on disk.** The audit writes the baseline before it exits (`run.ts:584-603`), so when carry refuses (a new non-pass with no prior issue) the committed file has already been replaced; `baseline_carry.py:72` prints "baseline left unchanged" (true of the script, not of the file) and `-Check audit` exits 1. The next `-Check audit` then fails `Get-CleanTree` until the human restores the file by hand, and the plan forbids hand edits. | `validate-task.ps1:178-181`; `baseline_carry.py:72`; `mcp-server/scripts/audit/run.ts:584-603` | On carry refusal, `Copy-Item $prior $baseline -Force` before exiting and say so in the message; keep the summary and report for the Decision Brief. | open |
| F10 | Low | no | clerical | `IMAGE_REVISION` keys both fetches on `updated_at` but does not name how the new `updated_at` reaches them: the filmstrip's `item` comes from the list query (must be invalidated after flatten/revert, as Save/Delete already do) and the viewport effect is keyed on `[selectedId, viewVariant]` today (`CapturePage.tsx:287-311`). AC-67.22's ledger oracle ("one more GET …/image for each") depends on that invalidation. | `implementation-plan.md:139`, `:215`; `ui/src/renderer/src/features/capture/CapturePage.tsx:287-311` | Add one sentence: after a 200 from flatten/revert, invalidate the captures list query and set the viewport key from the returned `DETAIL_OUT.updated_at`. | open |

> **`Blocking` is not `Severity`** (`review-verdict.schema.v2.json`). Only F1 gates approval. F2–F5 are real defects that should be corrected in the same round because they are cheap and each would otherwise cost a Green or a gate attempt; F6–F10 are notes.

### Out-of-Contract Observations (not findings)

1. `APPLY_ENABLED` uses `endsWith('.png')` (case-sensitive) while `PNG_ONLY` lowercases the suffix; a `.PNG` shot is flattenable by REST/MCP but disabled in the GUI. Lowercase in the renderer.
2. `CAPTURE_FILE_LOCK` is a non-reentrant `threading.Lock`; `ANNOTATED_CONSISTENCY` inside `revert` must call `annotate.bake` directly (as written), never `annotate_and_save`, or it deadlocks — worth one sentence in the contract so a later refactor does not trip it.
3. `m7-resource.test.ts:47` still titles the test "exactly 67 keys"; since TA-1 edits `:52` anyway, fix the title.
4. `GATED_PATHS` now includes `.agent/docs`, `.agent/schemas`, `.agent/roles`, `.agent/templates`: any framework-doc edit between the gate and review approval reopens it. Intended, but say so in the `LOCAL_SEQUENCE` request so a doc tidy-up does not silently cost an attempt.
5. `look-check` (`validate-task.sh:747-753`) accepts a row only in the `F<n> … pass` shape; the request template in `local-requests.md` matches it, but a free-text reply ("F1 looks fine") will be refused — expected, just be ready to transcribe.

---

## What was verified and holds (so the corrector does not re-open it)

- **Spec and code citations.** Every `file:line` I checked resolves: 09 §Flatten rows `:653-659`, §MCP `:562-582`, Settings sentence `:603`, `:487`/`:526` (remove deletes files); 05 `:85-95`, `:270-277`, `:289-305`; 11 `:87-89`, `:287-288`; `capture.py` `:264-274`, `:371-419`, `:475-485`, `:201-208`, `:43,207`; `routes/captures.py` `:186-193`, `:217-221`, `:45-50,145-146`; `schemas/captures.py:129`; `errors.py:25-38`; `cli.py:211-231` (one `uvicorn.Server`, no workers); `registry.ts:111-118`, `:197-221`; `index.ts:10`; `settings.ts:63-67`; `classify.ts:269-281`; `run.ts:74-81`, `:584-594`; `coverage.test.ts:74-80`; `CapturePage.tsx:197`, `:287-311`, `:975-1006`; `CaptureFilmstrip.tsx:58-78`; `capture-help-content.ts:20-23`; `test-ids.ts:300` marker and `:400-405` MEU-66 block; `capture-inbox.test.ts:83-170` mocks; TA-9 precedent `2026-09-30-tts-repair/implementation-plan.md:147`; `COUNT_FLOORS` 748 / 127 / 629 equal Session 29 attempt 4's result JSON.
- **`DETAIL_OUT` vs spec.** 09:653 says "`CaptureShotOut` with `annotations: []` plus `backup_path`"; only `CaptureShotDetailOut` carries `annotations`, so the plan's choice is the only shape that satisfies the sentence. `CaptureShotOut`/list unchanged (AC-67.10 negative).
- **409/404/422 mapping.** `CaptureFlattenConflictError(ConflictError)` → 409 via `isinstance` in `DOMAIN_HTTP_MAP` (`errors.py:33,79-81`); `NotFoundError` 404; `AnnotationValidationError`/`InboxPathError` 422; `CaptureFailedError` 503; `EmptyIn | None = Body(default=None)` yields the `{"x":1}` → 422 case. Consistent.
- **Bake into `.avkit-tmp`.** `adapter.py:229-232` saves with `format="PNG"` explicitly, so the unknown suffix is safe and `packages/infrastructure` stays frozen (S6 not triggered).
- **Backup naming / newest.** `BACKUP_PATTERN` is anchored and `re.escape`d; the AC-67.8 decoys (`shot_2.…`, `shot.20261002-120000.20261002-120001.png`, a directory) all fail it; `(timestamp, n)` ordering never consults mtime.
- **Windows atomicity framing.** `ATOMIC_REPLACE` correctly makes backup-first ordering, not the rename, the recovery guarantee; `FLATTEN_ROLLBACK` deletes the step-3 backup so a failed flatten does not make Revert appear. F6 is the one gap.
- **Inbox invariants.** `.avkit-tmp` is outside `SCAN_EXTENSIONS` and the watcher's `.png` filter; `.avkit-backup` is a directory (skipped by `is_file()`); `shouldNotifyInboxChange` is on the production path (`computeInboxNotification` ← `onInboxListing` ← `rescan` ← `fs.watch`), so AC-67.13's control chain is real and `ui/src/main` can stay unchanged.
- **Registry insertion.** Appending after `avkit_capture.remove` (`:118`, before the MEU-62 `download_asset` row) keeps `capture.test.ts:100` (`slice(0,59)` has no capture rows) and `action-index.test.ts:42` / `convert.test.ts:66` (`slice(0,46)`) true; `models-assets.test.ts:22` finds `download_asset` by filter, not index.
- **TA-1..TA-5 line refs** are correct except the clerical ones in F7(c); `redact.test.ts:57` and `report.test.ts:35,86` use synthetic `actions: 67` summaries and are unaffected.
- **Audit sequencing (D-20).** `--baseline` + `--update-baseline` computes deltas (`NEW` for the two; `NEW` does not count toward `regressionCount`), `writeBaselineIfAllowed` needs authoritative + win32 + clean cleanup + no REGRESSION/REMOVED, and the known `tts.cancel` fail plus the eight issue-tagged findings keep the exit at 1, which the `.ps1` accepts. The written file drops `issue` ids (`run.ts:584-594`); `baseline_carry.py` restores them only on identical `(tool, action, status)` / `(code, tool)` keys and refuses anything new, so it cannot hide a regression. Container `BASELINE_PENDING` proof (`validate-task.sh:211-217`) is sound: with the baseline byte-identical to `baseline.sha` and `served − entries == {flatten, revert}`, the only assertion of that `it` that can fail is `coverage.test.ts:78`. After commit A the test passes outright and no tolerance is consulted, so `WINDOWS_GATE` runs with zero tolerance.
- **Container audit feasibility.** `capture.capture` is `skip_env` off Windows, but the step seeds a shot through REST register (`plan.ts:1346-1356`), so `capture.annotate` and the two new steps can run and pass in the container with the Pillow bake; `AUDIT_ISOLATION` is required because `backup_dir` matches `PATH_LIKE` and the guard fails closed on an unmapped key (`isolation.test.ts:57-66` already proves that mechanism).
- **`.sh` / `.ps1` parity.** Identical 17-stage order (also identical to Session 29's result JSON); identical `AUDIT_SRC`/pattern (`plan_checks.py static` PASS); the `.ps1` clears `s30-win-*` receipts first, records preflight, reports counts only for stages that ran, maps `rg` exit 1 → clean; `windows-gate-check` asserts schema, clean tree, preflight, order, exits, `COUNT_FLOORS`, carried `pytest_floor`, flaky and code identity over `GATED_PATHS`; `audit-check` binds the audit commit to the gate commit over the code paths only.
- **D-10.** Correctly human-gated: `SCAN_EXTENSIONS` admits `.jpg/.jpeg/.webp` shots, so JPEG/WebP flattening is a genuine product fork (lossy re-encode vs refuse vs new file); the brief leads with a recommendation, states reversibility and a default, and sources every option. D-8, D-9, D-11..D-21 pass the obviousness test and their precedents resolve.
- **Out of Scope (C2).** All nine rows evidence-backed; `deferred` rows name MEU-69/70, both in the grouping and `meu-status.yaml`; `CAPTURE-BAKE-ARROW-THIN` and `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA` exist in `known-issues.yaml`; the "Open file" row's basis (`current-focus.md` Next steps 2) is a real pointer and the item is outside 09 §Flatten.
- **GUI/E2E.** `NEW_TESTIDS` land after the MEU-51 marker (hash proof intact); every new interactive element has a registered id and an Electron assertion (E2); `gui-actions-audit` only requires Palette `yes` ids in the command registry and resolvable IPC on `settings:` rows, so the three new index rows (Palette `no`; `showDirectoryDialog`) are safe; `e2e-wiring.test.ts` reads wave 0/5/7 ids only; `capturePutSchema` is strict but `asForm` reads defensively, so existing four-key mocks keep working.
- **Hub reconciliation** items 1–5 are concrete and checked by `hub`, except the F5 predicate.
- **Referenced artifacts.** Every tool/script/fixture the validation cells invoke exists on disk or is in Files Modified (new: `tests/e2e/test_api_capture_flatten.py`, `ui/tests/unit/capture-flatten.test.ts`, `capture-flatten.ts`).

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| All AC have source labels | pass | `rg -n '^\| AC-67\.' …/implementation-plan.md` (manual read of the Source column) | 0 | 26 rows AC-67.1–67.26, each tagged Spec / Local Canon / D-n / Boundary / G8; D-10 tagged Human-decision-required |
| Validation cells are exact commands | pass | `python3 docs/execution/plans/2026-10-02-capture-flatten-backup/plan_checks.py static` | 0 | `PASS static: 21 task rows; scripts and plan cross-references agree` |
| BUILD_PLAN audit row present | pass | manual read | — | task row 10 + plan §BUILD_PLAN.md Audit items 1–5, `validate-task.sh hub` |
| Post-MEU rows present (handoff, reflection, metrics) | pass | manual read | — | rows 9 (handoff), H2-1 (reflection), H2-2 (metrics/POST_REVIEW_STATE), H2-3 |

### Design Review (DR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| Naming convention followed | pass | `ls .agent/context/handoffs \| grep flatten` (before this write: none) | 0 | one rolling plan review at the canonical path; handoff set names `…-MEU-67-handoff.md` |
| Template version present | pass | `head -8 …/implementation-plan.md …/task.md` | 0 | `template_version: "2.2"` in both |
| YAML frontmatter well-formed | pass | `head -8` | 0 | keys project/date/source/meus/status/template_version |

### Post-Implementation Review (PR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| Evidence bundle complete | n/a | — | — | plan review; no implementation evidence yet |
| FAIL_TO_PASS table present | n/a | — | — | plan review |
| Commands independently runnable | partial | `bash -n …/validate-task.sh` | 0 | syntax OK; F4 (`green-mcp` needs a build), F5 (hub predicate) |
| Anti-placeholder scan clean | pass | `rg -n 'TODO\|FIXME\|TBD' docs/execution/plans/2026-10-02-capture-flatten-backup/` | 1 | no hits (exit 1 = none) |

### Plan Review Checklist (PR-1 … PR-9)

| # | Result | Evidence |
|---|---|---|
| PR-1 plan/task alignment | pass | WP-0..WP-5 ↔ rows 0–10, H1-1..H1-7, H2-1..H2-3; `plan_checks.py static` cross-references agree |
| PR-2 not-started | pass | no MEU-67 handoff, no `baseline.sha`, `git status --porcelain` empty at `5168586` (the plan commit) |
| PR-3 task contract completeness | pass | 21 rows × 10 columns; plan receipt `lint_task_contract.py` OK; `plan_checks.py` structural checks pass |
| PR-4 validation realism | partial | F4, F5 |
| PR-5 source-backed | pass | every AC and single-statement row tagged; citations verified above |
| PR-6 handoff/corrections readiness | pass | handoff set + two rolling reviews named; round 1 (no census required yet) |
| PR-7 scope discipline (C2) | pass | nine rows evidence-backed; MEU-69/70 scheduled |
| PR-8 control reachability & totality | pass with notes | observables/chains/negatives real for AC-67.2/3/13/14/16/19/22; F2 (unreachable code name), F6 (one read-then-write outside the named lock) |
| PR-9 single-statement | partial | F8 (Low) |
| Sweep 2 — `TEST_AMENDMENTS` completeness | **fail** | F1 |
| Sweep 8 — referenced-artifact existence | pass | all `tools/*.py`, test suites, fixtures and templates named in validation cells exist |

### Commands executed (read-only; no product suite, build or audit was run)

```json
{"schema":"evidence.v1","command":"python3 docs/execution/plans/2026-10-02-capture-flatten-backup/plan_checks.py static","cwd":"/home/user/av-kit","exit":0,"scope":"plan-local static verifier","tested_state":"5168586 + working tree (clean)","decisive_output":"PASS static: 21 task rows; scripts and plan cross-references agree"}
```

```json
{"schema":"evidence.v1","command":"bash -n docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.sh","cwd":"/home/user/av-kit","exit":0,"scope":"shell syntax","tested_state":"5168586","decisive_output":""}
```

```json
{"schema":"evidence.v1","command":"python3 - (split 09-screenshot-capture.md §MCP exactly as validate-task.sh:519-523 does and print parts[0]/parts[1])","cwd":"/home/user/av-kit","exit":0,"scope":"F5 probe","tested_state":"5168586","decisive_output":"PART[0]: '\\nNew compound tool `avkit_capture` (M2 parity with REST). No second URL space. Zod `.strict()`. Destructive `remove` req…' PART[1]: '**Phase 5 exception (dated 2026-08-26):** …' 'Destructive' in parts[1]: False"}
```

```json
{"schema":"evidence.v1","command":"grep -rn ROUTE_COUNT tests --include=*.py; python3 -c \"count operations in openapi.committed.json\"","cwd":"/home/user/av-kit","exit":0,"scope":"F1 probe","tested_state":"5168586","decisive_output":"tests/e2e/test_api_downloads.py:372:ROUTE_COUNT_AFTER = 71 | tests/e2e/test_api_downloads.py:424: assert len(operations) == ROUTE_COUNT_AFTER | 71 operations"}
```

```json
{"schema":"evidence.v1","command":"grep -rn 'DOMAIN_ERROR_TYPES' packages tests tools --include=*.py","cwd":"/home/user/av-kit","exit":0,"scope":"F1 probe (second pin)","tested_state":"5168586","decisive_output":"packages/core/src/avkit_core/domain/errors.py:227 (definition) | tests/unit/test_domain.py:214 (names == list(DOMAIN_ERROR_TYPE_NAMES), exact ordered pin at :181-214)"}
```

```json
{"schema":"evidence.v1","command":"grep -rn '\\b68\\b' mcp-server/tests --include=*.ts; grep -n 'confirm' mcp-server/src/toolsets/download.ts mcp-server/src/toolsets/capture.ts","cwd":"/home/user/av-kit","exit":0,"scope":"TA-1 census + F2 probe","tested_state":"5168586","decisive_output":"68-pins at m7-resource:52,69; capture:89; convert:55; action-index:40; coverage:18-19; runner-fake-backend:75 (all in TA-1) | download.ts:86-87 and capture.ts:147 use confirm: z.literal(true)"}
```

```json
{"schema":"evidence.v1","command":"python3 -c \"load baseline-snapshot.json; print keys, entries count, non-pass entries\"","cwd":"/home/user/av-kit","exit":0,"scope":"D-20 inputs","tested_state":"5168586","decisive_output":"entries=68 findings=8 recorded_commit=65bfa42… mode=authoritative; non-pass: avkit_tts.cancel fail issue=MCP-TTS-GENERATE-SYNCHRONOUS"}
```

```json
{"schema":"evidence.v1","command":"python3 -c \"load 2026-10-01-capture-viewport-chrome/windows-gate-result.json; print schema, stage ids, counts\"","cwd":"/home/user/av-kit","exit":0,"scope":"COUNT_FLOORS / stage order check","tested_state":"5168586","decisive_output":"s29-windows-gate.v1; 17 stages identical to validate-task.sh order; pytest 629/0; vitest 748/748; e2e 127/0/0/0; pytest_floor 629"}
```

---

## Verdict

`changes_required` — F1 is an evidence-backed High: the plan declares `TEST_AMENDMENTS` TA-1..TA-5 as "the only approved changes to existing test expectations" and routes their approval through the execution message, yet the design provably breaks `tests/e2e/test_api_downloads.py:372,424` (`ROUTE_COUNT_AFTER = 71` vs 73 operations after AC-67.15), which is neither amended nor reachable by the row-1 census regex. Executing the plan as written therefore cannot pass its own container pre-gate or `WINDOWS_GATE` without an unplanned human stop at H1-2 — a required deliverable (the amendment and its authorization) is omitted. The second pin on the same surface (`DOMAIN_ERROR_TYPES`) needs a stated decision either way. F2–F5 are Medium and non-blocking but each would cost a Green or a gate attempt; please take them in the same correction round. The design itself (ordering, rollback, lock, backup naming, `LATEST_BACKUP`, 409/404/422 mapping, D-20 sequencing, D-10 gating) holds up against the spec and the code.

**Concrete follow-up for `/plan-corrections`:** (1) add TA-6 (`ROUTE_COUNT_AFTER` 71 → 73) and resolve the `DOMAIN_ERROR_TYPES` tuple (TA-7 or an explicit "untouched"), extend the census patterns, and update User Review item 3, task rows 2/4 and Files Modified; (2) restate AC-67.16's refusal oracle; (3) decide and write down how AC-67.19's fake-backend clause is delivered (widen (b) or scope to test-local steps); (4) add the build step to `green-mcp`; (5) fix the `hub` destructive-sentence predicate; (6) the Low items as one-liners. On resubmission include the blast-radius census receipt with per-hit dispositions (PR-6).

**Residual risk after corrections:** the authoritative audit on Mat's machine is the first run of `capture.flatten`/`capture.revert` with real screen capture; any Windows-only non-pass there is an S5 Decision Brief, not a plan defect. F6's race is Windows-only and self-healing; it is recorded, not required.

🕐 Completed: 2026-10-03 00:12 (UTC)

---

## Recheck (2026-10-03)

**Workflow**: `/plan-critical-review` Round 2 of 3 (recheck of commit `d061638`; HEAD is `544ffe6`, which adds only `walkthrough.md`)
**Agent**: claude-fable-5-1-subagent (separate context, user-authorized route per `human-review-decision.md`; same-vendor deviation disclosed there; effort `high`)
**Read-only**: `plan_checks.py static`, `bash -n`, `git diff/show`, `rg`/`grep`, a stdlib AST probe of `adapter.py`, and reads of `mcp-server/node_modules/@modelcontextprotocol/sdk` 1.30.0 (present in this container). No product suite, build or audit was run. Only this file was written.

### Intent anchor (updated)

The user authorized execution on 2026-10-03 and widened the objective (A-2): JPEG/WebP shots are converted on Apply to a new PNG copy with the original untouched; the Save overlay copy may be PNG/JPEG/WebP at quality 90; and `avkit_capture` remove/flatten/revert ask the user through MCP elicitation and fail closed. The question this round is whether the corrected plan would deliver that, and whether the Round 1 corrections and the new contracts hold against the code.

### PR-6 census gate (pre-verdict, round 2+)

| Check | Result | Evidence |
|---|---|---|
| Resubmission names a census receipt | **fail** | `implementation-plan.md:749-759` lists eight swept values and says "Receipts are in §Planning receipts (Round 2)", but `:794-803` holds only verifier/lint/negative-case/F5 rows — no `rg -F -n` output for any old or new value. No `review-r1-census.md` (the Session 29 shape, `2026-10-01-capture-viewport-chrome/review-r1-census.md`) exists in the plan folder (`ls`). |
| Receipt is raw and untruncated | n/a | no receipt |
| Each hit carries a disposition (`updated` / `confirmed-consistent`) | **fail** | the list names values, not `file:line` hits; a value name is not a disposition (`plan-corrections.md` Step 5c: "record each hit in the correction log marked updated or confirmed-consistent"; "A correction submitted without its census receipt is incomplete") |
| Reviewer re-sweep (what the receipt would have shown) | two stale sites survive | `rg -F` over the plan folder for the old spellings: `TA-1 to TA-5` (3), `TA-1..TA-5`, `PNG_ONLY`, `F1–F5` are all historical references (gate decision, census list, census regex) — fine. Surviving stale contract text: `implementation-plan.md:594` D-17 question still says "the two new settings" (there are three); `:360` cites the Destructive sentence at `09:564` (it is `:565`; the hub check itself reads the line by content, so this is clerical). |

Per `plan-critical-review.md` PR-6 and the Verdict Rule, a round-2 resubmission whose blast-radius census is missing or undispositioned is a pre-verdict procedural gate and the verdict is `changes_required` on that alone. The content assessment below is recorded so that Round 3 — the last round of the cap — needs only the receipt plus the non-blocking fixes listed; nothing in it is severity-blocking.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 High — `ROUTE_COUNT_AFTER` / `DOMAIN_ERROR_TYPE_NAMES` pins outside `TEST_AMENDMENTS` | open | ✅ Fixed — TA-6 (`plan:182`, 71 → 73) and TA-7 (`:183`, 24 names + `CaptureFlattenConflictError` appended; `errors.py` row `:284` appends it to the tuple; 24 verified against `test_domain.py:181-205`); census `rg` gains `ROUTE_COUNT`, `DOMAIN_ERROR_TYPE`, `openapi.committed`, `test_api_downloads` (`validate-task.sh:443`); both files in Files Modified (`:295,298`) and `REGPY` (`:333-334`); task rows 2 names TA-6/TA-7; approval basis recorded (`human-gate-decision.md:24`). |
| F2 Medium — `confirm_required` unreachable | open | ✅ Fixed — AC-67.16 (`plan:236`) asserts `isError` + zero fetches; Boundary row `:206` states the Zod refusal. |
| F3 Medium — fake-backend clause undeliverable | open | ✅ Fixed — option (ii): AC-67.19 (`:239`) uses a test-local `userConfirm` step over `FIXTURE_REPAIRS` (b) (`:168`), real-step proof on `audit-container` and the authoritative run. |
| F4 Medium — `green-mcp` without a build | open | ✅ Fixed — `validate-task.sh:457-459` (`red-mcp`) and `:461-463` (`green-mcp`) build first. |
| F5 Medium — `hub` read the wrong paragraph | open | ✅ Fixed — `validate-task.sh:535-538` reads the line containing "Destructive `remove`" (`09:565`, verified present) for `flatten`, `revert`, `elicitation`; the plan's receipt table records the false-pass proof and a positive control (`plan:802-803`). |
| F6 Low — `scan_inbox` outside the lock | open | ✅ Fixed — `CAPTURE_FILE_LOCK` (`:146`) covers `scan_inbox`; AC-67.14 (`:234`) adds the slow-replace scan negative; D-15 updated. |
| F7 Low — stale statements / line refs | open | ✅ Fixed — gate-decision A-1 sentence (`human-gate-decision.md:24`), D-12 row "Spec + Local Canon" (`:268`), TA-2/TA-3/settings.ts refs (`:178-179`, `:148`), census prose (`:193`). |
| F8 Low — restated literals | open | ✅ Fixed — `BACKUP_DIR_DEFAULT_NAME` (`:129`), `TMP_SUFFIX` (`:130`); every former site references the name; `local-requests.md` F2–F4 say "the backup folder". |
| F9 Low — carry refusal left a rewritten baseline | open | ✅ Fixed — `validate-task.ps1:183-188` restores `$prior` before exiting; `LOCAL_SEQUENCE` (`:171`) and the request (`local-requests.md:23-24`) say so. |
| F10 Low — `IMAGE_REVISION` delivery | open | ✅ Fixed — `:163` names the list-query invalidation, the detail reload and both effect keys (and the convert re-selection). |
| Observations 1–5 | — | ✅ Applied — `APPLY_ENABLED` lowercases (`:157`); non-reentrancy + private helper (`:136,145,146`); m7 title in TA-1 (`:177`); gated-path warning in the request (`local-requests.md:29-30`); look-check shape in the request (`:64`). |

### Confirmed Fixes

- All ten Round 1 findings and the five observations are closed on the evidence above; no fixed surface was reopened.
- `plan_checks.py static` → `PASS static: 21 task rows; scripts and plan cross-references agree` (exit 0); `bash -n validate-task.sh` exit 0.

### New contracts tested against the code

- **USER_CONFIRM / AUDIT_ELICITATION on the locked SDK 1.30.0 (verified in `mcp-server/node_modules/@modelcontextprotocol/sdk`, `package.json` version 1.30.0).** `Server.getClientCapabilities(): ClientCapabilities | undefined` (`dist/esm/server/index.d.ts:121`) and `Server.elicitInput(params: ElicitRequestFormParams | ElicitRequestURLParams, options?: RequestOptions): Promise<ElicitResult>` (`:158`) exist; `McpServer.server` is the low-level `Server` (`server/mcp.d.ts:18`). `elicitInput` form mode (`server/index.js:340-370`) requires `_clientCapabilities.elicitation.form`, and `ClientCapabilitiesSchema` preprocesses a bare `elicitation: {}` into `{ form: {} }` before `_oninitialize` stores it (`types.js:335-345`, `server/index.js:259-261`), so both the audit client's declared `{elicitation: {}}` and an IDE's bare declaration reach form mode. The server validates an accepted `content` against `requestedSchema` and throws `McpError` on mismatch (`:356-370`) — the plan's "thrown → cancel" mapping covers it. `ElicitResult.action` is the closed enum `accept | decline | cancel` (`types.d.ts:5381-5400`); `BooleanSchemaSchema` is a valid primitive (`:4687`); `InMemoryTransport` ships (`dist/esm/inMemory.js`) for AC-67.31. The audit runner's forbidden-import census (`run-cli.test.ts:93`) does not forbid SDK type imports in `client.ts`. **S4 cannot fire on this SDK**; `walkthrough.md:9` already records the same check.
- **CONVERT_ON_APPLY / CONVERT_NAME.** `bake(original, [], target_tmp, "png")` is a lossless RGB decode (`adapter.py:143-157`, `_write_png` `format="PNG"`); `_upsert_shot` takes the row's `source` (`capture.py:487-529`); a same-stem PNG would indeed share `{stem}.ann.json`/`.annotated.*` (`capture.py:382-387`), so D-22's distinct stem is necessary, not cosmetic; the rollback inventory (target_tmp, target, sidecar, backup, row) is complete; reusing `FLATTEN_SEQUENCE` steps 3–8 as a lock-held private method is consistent with the non-reentrant lock. Sound.
- **ANNOTATED_FORMATS / LOSSY_QUALITY / BAKE_PORT.** `routes/captures.py:45-50,235-241` already map `.jpg`/`.webp` by suffix; `client.ts:160-180` sniffs PNG/JPEG/WEBP from bytes; the watcher's `.png` filter (`capture-inbox-watch.ts:43-46`) ignores `.annotated.jpg/.webp`; the scan today skips only `.annotated.png` (`capture.py:46,205-208`) and the plan changes it to all `ANNOTATED_SUFFIXES`; `annotated_format` does not match `PATH_LIKE`, so it is not an isolation key. Existing `.annotated.png` pins (37 hits across `tests/`, `ui/tests`) all describe the unchanged default; `test_capture_adapter.py:354,376` call `bake` with three positional args and keep their meaning through the default (AC-67.29). Sound, with N1 below.
- **AUDIT_ELICITATION vs `scripts/audit/{client,plan,classify,types}.ts`.** `AuditClient` constructs `new Client({name, version})` (`client.ts:37`) — adding `{capabilities: {elicitation: {}}}` and a `setRequestHandler(ElicitRequestSchema, …)` is the standard SDK shape; `destructiveStep` (`plan.ts:191-251`) is where the fourth call slots after `asFalse`; `summary.schema.json:91` types `refusal` as a free object, so `refusal_declined` passes schema validation (`report.test.ts:53`); `RefusalRecord` (`types.ts:46-50`) gains the optional field. Sound, with N2 below.
- **TEST_AMENDMENTS / FIXTURE_REPAIRS for the new scope.** TA-4 now 4 → 7 keys (`flatten_backup`, `backup_dir`, `annotated_format`) matches `NEW_SETTINGS`; `ToolRuntime`'s new optional field breaks none of the 47 `{env, fetchImpl}` call sites; the only existing tests that drive `avkit_capture.remove` are `strict-confirm.test.ts:41-69` (refusal only, Zod refuses before `confirmWithUser`), `capture.test.ts:222-234` (no confirm, refusal) and the `action-index.test.ts:56-90` parity loop, which `FIXTURE_REPAIRS` (e) covers; `tools-parity.test.ts` drives no capture remove. Gap: N1.
- **Scripts.** `hub`: `05 §Destructive gate` split lands on the right section (`### Descriptions (M7)` is the next heading); the 09 Settings line exists at `:603`; `annotated_format` required. `api-scope`: the AST probe selects nine functions (`arrowhead_vertices`, `text_plate_box`, `_color_rgb`, `_load_font`, `_apply`, `_apply_highlight/arrow/rect/text`) and `ast.dump` omits line attributes, so a line shift does not false-fail; `packages/infrastructure` is unfrozen but every other infra file is still caught by "product changes outside Files Modified". `audit-check`/`audit_container`: require `refusal_declined` error-and-unchanged for all three `USER_CONFIRM_ACTIONS` steps; remove is not required `NEW`. `look-check`: F1–F8. `mcp_env_ok`: unchanged and still correct (`remove` is already baselined). `plan_checks.py`: singly-named ACs now count toward coverage (verified `AC-67.33` in row 7).
- **Decision fidelity.** D-10/D-22/D-23/D-24 quote the user's words verbatim and the AskUserQuestion option texts; D-22's one refinement is reasoned (sidecar collision) and flagged for veto; D-24 includes flatten/revert because the user chose the option that named "remove, flatten, revert". Execution authorization is recorded with the user's words (`human-gate-decision.md:30-36`). The TA-6/TA-7 "read as covered" interpretation is disclosed and queued for the user's next report; acceptable.
- **Not started (PR-2).** `544ffe6` adds only `walkthrough.md` (dependencies installed, the S4 SDK check, `electron-setup`); `git diff --name-only d061638..HEAD -- ui packages mcp-server tests openapi.committed.json` is empty, no `baseline.sha`, no MEU-67 handoff. Environment preparation only; `task.md:14` says the Round 2 findings are applied before row 0, which still holds.

### Remaining Findings (new this round; none blocking)

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| N1 | Medium | no | behavior | **`FIXTURE_REPAIRS` has no letter for the Python fake `bake`.** `tests/unit/test_capture_service.py:68` defines `bake(self, original_path, annotations, output_path)`; `BAKE_PORT` makes the service pass a fourth positional `output_format` (`FLATTEN_SEQUENCE` step 4 `annotate.bake(original, SAVED_MARKS, tmp, "png")`; `annotate_and_save` must pass the current format for `ANNOTATED_FORMATS`), so every existing `annotate_and_save` unit test raises `TypeError` until the fake gains the parameter. That is setup-only (AGENTS §Testing allows it), but row 1's disposition vocabulary admits `fixture` only "with a `FIXTURE_REPAIRS` letter", so the census hit on `bake(` (`validate-task.sh:444`) can only be filed as `new-contradiction` → Stop condition S2 — an avoidable human stop. | `implementation-plan.md:168`; `tests/unit/test_capture_service.py:68`; `validate-task.sh:444` | Add `FIXTURE_REPAIRS` (f): the `test_capture_service.py` fake `bake` gains `output_format: str = "png"` (recorded, not asserted) and any other Python fake the census finds; note that `test_capture_adapter.py` needs nothing (defaulted positional calls). | open |
| N2 | Low | no | behavior | **`refusalVerdict` cannot tell "missing `refusal_declined`" from "not a `userConfirm` step" from the record alone.** `AUDIT_ELICITATION` says `refusalVerdict` "fails such a step when `refusal_declined` is missing", but `RefusalRecord` gains only the optional field and the existing `classify.test.ts:70-104` cases (no such field) must keep passing. | `implementation-plan.md:155`; `mcp-server/scripts/audit/types.ts:46-50`; `mcp-server/tests/audit/classify.test.ts:70-104` | Add `user_confirm: boolean` to `RefusalRecord` (set by `destructiveStep` from its `userConfirm` option) and define the rule as: `user_confirm && (!refusal_declined \|\| !refusal_declined.isError \|\| refusal_declined.changed)` → `fail`, reason `user_confirm_missing` / `refusal_mutated`; name it in AC-67.32. | open |
| N3 | Low | no | behavior | **Capability test and timeout precision for `USER_CONFIRM`.** (a) The plan tests "no `elicitation` in `getClientCapabilities()` → unsupported"; after the SDK's normalization the decisive key is `elicitation.form` — a URL-only client (`{elicitation: {url: {}}}`) passes the plan's test and is then refused as `cancel` (thrown `Client does not support form elicitation.`) rather than `unsupported`. Still fail-closed, but the outcome label and the AC-67.31 "no-capability" case should be stated on `.form`. (b) `elicitInput` uses `DEFAULT_REQUEST_TIMEOUT_MSEC = 60000` unless `options.timeout` is passed (`shared/protocol.d.ts:57,77`); a user who takes longer than a minute gets `cancel`. F8 depends on this. | `implementation-plan.md:151`, `:251`; SDK `server/index.js:351-352`, `types.js:335-345`, `shared/protocol.d.ts:57` | Test `getClientCapabilities()?.elicitation?.form`; pass an explicit `{timeout}` (name the value in `USER_CONFIRM`, e.g. 5 min) and add one line that the IDE's own tools/call timeout still bounds it. S4 may additionally cite the walkthrough's verified check. | open |
| N4 | Low | no | clerical | Residual stale text the missing census would have caught: D-17 `question` still says "the two new settings" (`plan:594`, now three); `:360` cites the Destructive sentence at `09:564` (it is `:565`). | `implementation-plan.md:360,594` | One-line fixes. | open |

### Out-of-Contract Observations (not findings)

1. `elicitInput` is sent while the IDE's `tools/call` is in flight; Cursor and Claude Code support that (the plan's sources), Claude Desktop does not — the plan already fails closed there. Worth one sentence in the user-facing report so the F8 result is not misread as a product defect on an unsupported IDE.
2. `registerMcpSurface` must read `getClientCapabilities()` inside the per-call `confirmWithUser` (it is `undefined` until `initialize`), not at registration time; the plan's wording allows either reading.

### Verdict

`changes_required` — on the PR-6 procedural gate alone: the Round 2 resubmission carries no blast-radius census receipt and no per-hit dispositions (`plan-corrections.md` Step 5c; `plan-critical-review.md` PR-6 and Verdict Rule), and the reviewer's own re-sweep found two stale sites the receipt would have surfaced (N4). No severity-rated finding blocks: every Round 1 finding is closed on the evidence above, the new contracts are implementable on SDK 1.30.0 as verified in `node_modules`, and the new findings N1–N4 are non-blocking (N1 Medium, N2–N4 Low) with concrete fixes.

**Follow-up for `/plan-corrections` (Round 3 is the last of the cap):** (1) produce `review-r2-census.md` in the Session 29 shape — raw `rg -F -n` output per changed value (old and new spellings, both plan files and the plan-local scripts), each hit marked `updated` / `confirmed-consistent`, with the Step 5c summary line — and link it from §Round 1 Review Corrections; (2) add `FIXTURE_REPAIRS` (f) (N1); (3) N2–N4 one-liners. Nothing else needs to change.

**Residual risk:** unchanged from Round 1, plus: F8 is the first real-IDE elicitation check; an IDE without elicitation (Claude Desktop) or a slow answer beyond the request timeout reads as a refusal by design, and the walkthrough should say which IDE and version was used.

🕐 Completed: 2026-10-03 00:34 (UTC)

---

## Recheck (Round 3)

**Workflow**: `/plan-critical-review` Round 3 of 3 (recheck of commit `db6200d`; the cap's last round)
**Agent**: claude-fable-5-1-subagent (separate context, user-authorized route per `human-review-decision.md`; same-vendor deviation disclosed there; effort `high`)
**Read-only**: `plan_checks.py static`, `bash -n`, `git diff/log/status`, `rg`/`grep`. No product suite, build or audit was run. Only this file was written.

### PR-6 census gate (pre-verdict)

| Check | Result | Evidence |
|---|---|---|
| Resubmission names a census receipt | pass | `implementation-plan.md:760` links `review-r2-census.md`; the Step 5c summary line is present (`review-r2-census.md:26`: "15 values swept, 97 hits. 0 stale. 6 values updated in this round (N1–N4 and the F1–F8 / three-leaves sites); every other hit is confirmed consistent") |
| Receipt is raw and untruncated | pass | `review-r2-census.md:28-160` holds 29 `=== rg -F -n '<value>'` blocks (old and new spellings per value, scope: every file in the plan folder) with the full match lines and `(no hits)` markers; no `head`/truncation. Re-running three of them here reproduces the receipt: `:564` → no hits outside the receipt; `two new settings` → no hits; `user_confirm` → `implementation-plan.md:151,156,251,253,710,760` as listed. Note (clerical, non-blocking): the blocks print `(no hits)` instead of the captured `$rc`, so an `rg` I/O error (`rc > 1`) would be indistinguishable from "no match" in the receipt text; Session 29's receipt printed the exit code per block. |
| Each hit carries a disposition | pass | `review-r2-census.md:8-25`: fifteen rows, each listing its `file:line` hits and marked **updated** or **confirmed-consistent** with the reason (e.g. `TA-1 to TA-5` kept at `human-gate-decision.md:42` as the user's approved set; `.avkit-backup` kept only as the definition and two verbatim spec quotes) |

Gate passed; the corrected content is reviewed below.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| N1 Medium — no `FIXTURE_REPAIRS` letter for the Python fake `bake` | open | ✅ Fixed — (f) added (`implementation-plan.md:169`: `test_capture_service.py:68` fake gains `output_format: str = "png"`, recording the format); task row 2 applies it (`task.md:39`); the census's `output_format` sweep lists `BAKE_PORT` `:144`, (f) `:169`, `PY_SYMBOLS` and row 2. |
| N2 Low — `refusalVerdict` could not tell "missing" from "not a userConfirm step" | open | ✅ Fixed — `RefusalRecord` gains `user_confirm: boolean` (true exactly for the three steps); the rule is stated once in `AUDIT_ELICITATION` (`:156`) and asserted in AC-67.32 (`:253`), with `user_confirm: false` judged as today so `classify.test.ts:70-104` stays green. `mcp-server` `typecheck` includes only `src/**` and `scripts/**` (`tsconfig.json:14`, `tsconfig.scripts.json:8`) and Vitest does not type-check, so the existing test literals without the field cannot fail `mcp-types`. |
| N3 Low — capability test on `.form`; explicit elicitation timeout | open | ✅ Fixed — `USER_CONFIRM` (`:151`) tests `elicitation.form` with the SDK normalization cited (`types.js:335-345`; URL-only → `unsupported`) and passes `{timeout: USER_CONFIRM_TIMEOUT_MS}`; `USER_CONFIRM_TIMEOUT_MS` = 120000 defined once (`:152`, the only `120000` literal in the folder besides a timestamp in AC-67.8); AC-67.31 (`:252`) asserts the option. |
| N4 Low — D-17 "two new settings"; `09:564` | open | ✅ Fixed — D-17 question/chosen say three (`:595-598`); hub audit cites `:565` (`:361`), matching the file (`grep -n` here: line 565). |
| Round 1 F1–F10 and observations 1–5 | closed in Round 2 | ✅ Still closed — the Round 3 diff touches only `USER_CONFIRM`, `USER_CONFIRM_TIMEOUT_MS`, `AUDIT_ELICITATION`, `FIXTURE_REPAIRS`, AC-67.31/67.32, the hub `:565` cite, D-17 and the census pointer (`git diff 544ffe6..db6200d`); no fixed surface was reopened. |

### Confirmed Fixes

- `plan_checks.py static` → `PASS static: 21 task rows; scripts and plan cross-references agree` (exit 0) on `db6200d`; `bash -n validate-task.sh` exit 0.
- The Round 3 diff introduces no new restated literal (`USER_CONFIRM_TIMEOUT_MS` is referenced by name at `:151` and `:252`), no new script change (`validate-task.sh`, `.ps1`, `plan_checks.py`, `local-requests.md`, `human-gate-decision.md` are unchanged since Round 2), and no product or test file (`git diff --name-only 544ffe6..db6200d -- ui packages mcp-server tests openapi.committed.json` is empty).
- Spot-check of the amended contracts against the code: `USER_CONFIRM`'s `.form` test matches `server/index.js:351-352`; `elicitInput(params, options)` accepts `RequestOptions.timeout` (`shared/protocol.d.ts:77`); `RefusalRecord` is only consumed by `refusalVerdict` (`classify.ts:44-50`), `destructiveStep` (`plan.ts:191-251`) and the loosely typed `summary.schema.json:91`, so the new field is additive everywhere.

### Remaining Findings

None blocking. Non-blocking notes carried in this summary (the structured findings array is empty, as `approved` requires):

- **Note A (clerical):** the census receipt omits the per-block `rg` exit code; print `$rc` after each block next time (Step 5c's receipt shape).
- **Note B (observation):** since `user_confirm` is required on the type but the existing `classify.test.ts` literals omit it, write `refusalVerdict` so that an absent field is judged as `false` (or declare it `user_confirm?: true`); either keeps AC-67.32's "false is judged as today" true for hand-built records.
- **Note C (observation):** row 0's `baseline` has already run on `db6200d` (`baseline.sha` is present and untracked, written 00:37; no product file changed). That is within the user's execution authorization and `task.md:14`'s "Round 2 findings applied before row 0" holds; this approval does not reopen it. Commit `baseline.sha` with the walkthrough's §Baseline evidence as row 0 says.

### Out-of-Contract Observations

Unchanged from Round 2 (IDE support for mid-call elicitation; read client capabilities per call, not at registration).

### Verdict

`approved` — the PR-6 census gate is met (a raw, untruncated receipt with a disposition per hit, reproduced on re-run), every Round 1 and Round 2 finding is closed on file:line evidence, the Round 3 edits are confined to the four notes and introduce no new defect, and the plan's contracts were verified against the spec, the code and the locked SDK in Rounds 1–2. Executing this plan as now written would deliver MEU-67 with the user's A-2 decisions. Under `plan_to_exec_gate: human`, this approval authorizes nothing by itself; the user's 2026-10-03 message (recorded in `human-gate-decision.md` §Execution authorization) is the execution authorization, and commit/push remain on the designated branch only.

**Residual risk:** as recorded in Rounds 1–2 — the authoritative Windows audit is the first real run of `capture.flatten`/`capture.revert` with screen capture (an S5 Decision Brief if it fails, not a plan defect); F8 depends on an IDE with form elicitation and an answer within `USER_CONFIRM_TIMEOUT_MS`; F6's Windows replace race is now covered by the lock on `scan_inbox`.

🕐 Completed: 2026-10-03 00:38 (UTC)
