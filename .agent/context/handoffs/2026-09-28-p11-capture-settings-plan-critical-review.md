---
date: "2026-09-28"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md"
round: 2
verdict: "approved"
findings_count: 6
template_version: "2.1"
requested_verbosity: "standard"
agent: "claude-fable-5-1-subagent"
---

# Critical Review: 2026-09-28-p11-capture-settings

> **Review Mode**: `plan`
> **Verdict**: `approved` (Round 2, with correction notes — 0 High/Critical, 1 Medium, 5 Low; Round 1 below was `changes_required`)

---

## Intent Anchor

Executing this plan is supposed to deliver Session 26 after Session 25: MEU-57 recomposes the Capture page (header with key cap and Settings disclosure, 200 px filmstrip, viewport toolbar with tool segment and per-shot actions, inline confirm strips) and MEU-58 recomposes the Settings page (960 px two-column grid, observer-tracked rail, 168 px form grid, save-mode captions, chip-list diagnostics), both under `COMPOSITION_LOCK` with every existing test ID preserved and only the human-approved `TEST_MIGRATIONS` touching pre-existing expectations. It must then pass one fresh full D6 Phase 11 exit gate, obtain independent execution approval, and reconcile SSOT/hub/grouping/focus to mark Phase 11 complete.

The verdict question is whether executing the plan as written would deliver that. It would not: the plan's own stop rules halt it at row 2 (Finding 3), then at the first pre-existing assertion that CP1/CP4/the moved IDs contradict that is not in `TEST_MIGRATIONS` (Finding 1), and if both were pushed through, the Phase 11 exit would be declared on a tree carrying a red Vitest contract that the fresh gate never saw (Finding 2).

## Scope

**Target**: `docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md`; `docs/execution/plans/2026-09-28-p11-capture-settings/task.md`; supporting `plan_checks.py`, `human-review-decision.md`
**Review Type**: plan review of an unstarted Session 26 plan (Round 1, user-directed Fable 5.1 subagent route per `human-review-decision.md`)
**Checklist Applied**: PR-1–PR-9 and DR-1–DR-8, with the workflow Intent Anchor and Materiality Gate

Expanded evidence scope: Phase 11 canon (`docs/build-plan/11-page-layout.md` CP1–CP6, ST1–ST7, §Capture, §Settings, Test-ID migration CP 1–24 / ST 1–35), both 2026-09-03 mockups (§02–§06 text extracted), the Phase 11 grouping, `meu-status.yaml` MEU-48–61 blocks, `current-focus.md`, `BUILD_PLAN.md:55,72`, harness profiles and the local override, `commands.md` §D6, AGENTS §Testing/§Dual-Agent/§Commits/§RTK, GUARDRAILS SIGN 1, `create-plan.md` §4/§4A/§5c, PROJECT-PROFILE B1/B4/D6/E5, live `CapturePage.tsx`/`CaptureViewport.tsx`/`CaptureFilmstrip.tsx`/`SettingsPage.tsx`/`useSettingsPage.ts`/`StartAtSignInControl.tsx`/`useCaptureSettings.ts`, the five MEU-51 primitives plus `Button`/`SelectInput`, `AppShell.tsx`, `capture-hotkey.ts`, `cookie-bar.ts`, `schemas/captures.py`, `services/capture.py`, `services/settings.py`, `06-gui.md:960–1016`, `09-screenshot-capture.md:554`, every unit and E2E suite the plan names plus `layout-canon.test.ts`, `test-ids.ts`, the Playwright wrapper and config, `ui/package.json` scripts, and the Session 24 plan/review/reflection.

Worktree state: HEAD `0f51036`, `git status --porcelain` shows only `?? docs/execution/plans/2026-09-28-p11-capture-settings/`. No MEU-57/58 handoff, no implementation review, no new source or test file exists. All 17 task rows are `[ ]`. Review mode `plan` is correct.

No project test, build, `npm install`, generator or repo-mutating command was run. The only executed tools were the plan-local read-only verifier (`plan_checks.py self-test`, `meu-state`) and `tools/lint_task_contract.py`, both with receipts under `${RECEIPTS_DIR}`.

---

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| 1 | High | yes | behavior | **`TEST_MIGRATIONS` is not "the complete list"; the plan's CP1/CP4/moved-ID changes contradict pre-existing assertions in five files that TM-1..TM-4 do not cover, and OQ-4 asks the human to approve an incomplete list.** Under AC-57.6 (`capture-save` mounted iff `CAPTURE_OVERLAY_DIRTY`), a clean or freshly loaded shot has no `capture-save` element. (a) The shared unit helper `openSelectedSurface()` waits for `getByTestId('capture-save').disabled === false` on a clean shot (`capture-page.behavior.test.ts:257–271`); roughly thirty AC-59/AC-60 tests call it and every one throws on the `getByTestId`. (b) `AC-59.8:455`, `AC-60.10:664` (empty text draft ⇒ not dirty) and `AC-60.10:682` (pointer-down only) assert `disabled === true` on a non-dirty overlay ⇒ element absent ⇒ throw. (c) E2E `AC-59.12:412,455` and `AC-60.12:516` assert `capture-save` `toBeEnabled()` on a clean shot before any mark is drawn / after reload with saved marks. (d) Source-string contracts require the literals `capture-save` (`AC-39.9:278`), `capture-delete` (`AC-39.11:296`), `capture-open-file`/`capture-open-folder` (`AC-39.12:301–302`) and `capture-empty` + `Press F2 or Capture region` (`AC-39.13:311–312`) to be **in `CapturePage.tsx`** (`pagePath`, line 10), while §Files Modified moves Save/actions into `CaptureViewport.tsx` and AC-57.9 moves `capture-empty` inside `capture-viewport`. (e) `capture-picker.test.ts` (region-picker confirm case) asserts `capture-filmstrip` `toContainText(<full timestamped filename>)`; `FILMSTRIP_LABEL_RULE` strips the date prefix from the visible text and keeps the full name only in `alt`/accessible name, which `toContainText` does not read. (f) `settings-page.test.ts:483` asserts `mcp-token-present` text matches `/yes\|no/`; AC-58.9 replaces it with "a token chip" whose label is unpinned. The plan states the list is complete (`implementation-plan.md:133`) and that "Existing W9/AC-59/AC-60 cases stay green, amended only per `TEST_MIGRATIONS`" (`:168`); both are false against file state. AGENTS §Testing requires human authorization per proven expectation change, and the plan's own rule stops execution at each unlisted one. Violates PR-1/PR-5 and the Verdict Rule (materially misstates scope). | `implementation-plan.md:133`, `:164`, `:168`, `:187–189`; `ui/tests/unit/capture-page.behavior.test.ts:257–271,455,664,682`; `ui/tests/e2e/capture-inbox.test.ts:412,455,516`; `ui/tests/unit/capture-page.test.ts:10,278,296,301–302,311–312`; `ui/tests/e2e/capture-picker.test.ts` ("renderer only learns…" `toContainText`); `ui/tests/unit/settings-page.test.ts:483` | Re-census every assertion on `capture-save`, the moved action IDs, `capture-empty`, filmstrip text and `mcp-token-present` across `ui/tests/unit` and `ui/tests/e2e` (`rg -n` receipts), then either (i) add each as a TM-n row with its canon source for OQ-4, or (ii) constrain the design so the assertion stays true (keep the ID literals in `CapturePage.tsx` by passing them as props/children; render the full filename in a visually-hidden text node so `toContainText` still holds; pin the token chip text to contain "yes"/"no"). Re-check `openSelectedSurface` explicitly: a helper change is one migration but it touches every consumer. | open |
| 2 | High | yes | control-defeat — `mechanism: post-gate-tree-mutation` | **H1-3's canon edit breaks a locked contract after the fresh gate, so `PHASE11_EXIT_PREDICATE`/H2-2 declare Phase 11 complete on a tree with a red Vitest test.** H1-3 "Fix[es] the canon '9 section ids' clerical count in ST 4" (`task.md:45`; `implementation-plan.md:122,270`). `ui/tests/unit/layout-canon.test.ts` AC-50.4 (`:130–145`) parses each mockup's §05 `table.inv` and asserts the canon inventory row label `toBe(source.label)` verbatim (`:141`); the settings mockup §05 cell reads "download-settings … mcp-access-card (9 section ids)". Editing the canon row therefore fails AC-50.4. H1-3 runs after H1-2 (the only full Vitest run); H2-2 runs only `meu_status.py render --check` and `plan_checks.py meu-state`; nothing re-runs `ui-tests`. The plan's own §Validation stage contract says "any later code change invalidates" the gate, but no row enforces it. This is a demonstrated false-passing completion gate (PR-4, PR-8, DR-8). | `task.md:45`, `:53`; `implementation-plan.md:122`, `:270`, `:392`; `ui/tests/unit/layout-canon.test.ts:130–145` | Drop the canon text edit from H1-3 (the discrepancy is already documented once under `SETTINGS_SECTION_SET`; record it in the reflection for MEU-50 follow-up), **or** make the edit before H1-2 together with the matching mockup §05 cell and a `layout-canon.test.ts` re-run, and add an explicit rule that any docs/test/source edit after H1-2 re-runs the affected D6 rows before H2-2. | open |
| 3 | High | yes | control-defeat — `mechanism: unreachable-red-oracle` | **Rows 2 and 5 cannot pass their own Red oracle as sequenced.** The plan requires all Vitest assertions "written before its production edit" and run to an assertion Red that `plan_checks.py red` verifies, which "refuses collection … failures" (`implementation-plan.md:140`). The MEU-57 Red file set includes the new `tests/unit/capture-filmstrip-label.test.ts` (`:294`), whose subject `capture-filmstrip-label.ts` is created only in row 3 (`:190`; `task.md:37` first bullet). The MEU-58 set includes the new `tests/unit/settings-rail.test.tsx` (`:294`) whose subject `SettingsRail.tsx`/`settings-sections.ts` are created in row 6. A Vitest file whose import fails is reported as `status: "failed"` with empty `assertionResults`; `_vitest_failures` classifies exactly that as `collection` and `check_red` raises `Refused` — the plan's own self-test fixture `vt_collect` (`plan_checks.py:214–220`) proves it. So row 2's and row 5's validation cells exit 1 on the planned inputs, the "Red is not an assertion Red" stop condition fires, and rows 3/6 are dependency-blocked. The sequence is impossible as written (Verdict Rule: "sequences work impossibly"). | `implementation-plan.md:140`, `:190`, `:243`, `:294`; `task.md:36–37`, `:39–40`; `plan_checks.py:54–70,105–111,214–220` | Choose one and state it once: (i) permit a named, minimal module scaffold (exports only, throwing or returning `undefined`) as part of the Red step, recorded as `Local Canon` (AGENTS: fixture repairs may fix setup), or (ii) run the new-module unit files to Red as a separate oracle invocation immediately after the scaffold and keep the page behavior files as the pre-edit Red, or (iii) drop the new unit files from the pre-edit Red set and require their Red before row 3/6's second bullet. Update rows 2/5 validation cells accordingly. | open |
| 4 | Medium | no | behavior | **The declared driver cannot run two gates the plan depends on, and only one of the two is disclosed.** (a) `capture-picker.test.ts` hard-requires `native/region-picker-stub/publish/avkit-region-picker-stub.exe` (`expect(existsSync(STUB_EXE)).toBe(true)`, no platform guard); the container has no `dotnet` and no `publish/` output, so row 4's targeted gate (`capture-picker.test.ts`) and H1-2's full `ui-electron` row fail deterministically on Linux, and the Electron ≥ 95 floor (a Windows-host count) cannot be met. (b) `rtk` is absent from PATH; the plan discloses this as a row-1 `[B]`, but every later validation cell also begins with `rtk proxy`, so a row-1 `[B]` cascades to every row and to the phase gate rather than being contained. A `[B]` on the Phase 11 exit gate is not a phase exit. | `implementation-plan.md:60–67`, `:297`, `:317`, `:321`; `task.md:38`, `:41`, `:44`; `ui/tests/e2e/capture-picker.test.ts` (`STUB_EXE`, `launch()`) | Add a row-1 decision with human options: run Session 26's gates on the Windows host (where the stub and RTK exist), or install RTK in the container and decide (Human-approved, G36-aware) how `capture-picker.test.ts` is treated on non-Windows. Do not leave it to surface at row 4. | open |
| 5 | Medium | no | behavior | **Closeout predicates are weaker than the prose they certify.** H2-2 promises grouping Session 26 `approved`, hub Phase 11 ✅ + Next line, `current-focus.md`, and a metrics row, but its validation cell asserts only `render --check` and `meu-state` (`task.md:53`); the hub "Next:" sentence at `BUILD_PLAN.md:72` is hand-maintained prose outside the AUTOGEN region, and the §BUILD_PLAN audit's `grep -n "Phase 11\|Next:"` cannot fail on content. H1-2's cell omits the D6 `task-contract` static row that §Verification Plan item 4 lists, omits the JSON `--outputFile` the same table specifies for `ui-electron`, and the "count check (Vitest ≥ 597, Electron ≥ 95)" has no command at all. Session 24's corrected H2-2 asserted grouping/hub/focus explicitly (`2026-09-26-p11-queue-pages` review Round 2); this plan regresses to prose. | `task.md:44`, `:53`; `implementation-plan.md:273`, `:309`, `:317`, `:321` | Add to H2-2 fail-closed predicates for the grouping row, the hub phase row and Next line, and `current-focus.md`; add the task-contract row and JSON output to H1-2; give the count floors an exact command over the JSON reports (or drop the floors). | open |
| 6 | Medium | no | behavior | **§05 reconciliation is incomplete for MEU-58.** Canon §Test-ID migration binds page MEUs to "reconcile each §05 keep/move/change entry before replacing a page", and the plan claims coverage of ST 1–35. Rows ST 14 (`apply-defaults-btn` ghost sm in a right-aligned footer), ST 29 (`log_to_file` + `settings-log-file-path` + `settings-copy-log-path` as one row with the fixed-path note as a hint), and ST 31 (`theme-dark-btn`/`theme-light-btn` as a two-button segment with `aria-pressed`) have no AC and no explicit disposition. They are presentation-only, so this is not a `COMPOSITION_LOCK` breach, but an untraced `change` row is exactly what the canon sentence forbids. | `implementation-plan.md:13`, `:213–224`; `docs/build-plan/11-page-layout.md:108,252,267,269` | Add a short §05 disposition table (row → AC or "presentation per mockup §04, no assertion") for CP 1–24 and ST 1–35, giving ST 14/29/31 an owner AC or an explicit "kept as today" note. | open |
| 7 | Low | no | clerical | Reference drift: (a) `schemas/capture.py:125` → the file is `packages/api/src/avkit_api/schemas/captures.py` (line 125 `created_at` is correct); (b) "immediate is `putNow('ui')` (`useSettingsPage.ts:74–79`)" — 74–79 is `flushPut`'s theme branch; `putNow` begins at `:126`; (c) H1-4 audits `packages/api mcp-server/src` while §Verification Plan item 4 and H1-2 say `packages/ mcp-server/` (PR-9 restated predicate; name one). All trivially inferable. | `implementation-plan.md:129`, `:123`, `:322`; `task.md:46` | Correct the two paths; make the scope-audit path set a single named literal. | open |

No Critical finding. Findings 1–3 are each independently blocking under the Materiality Gate (evidence-backed High: scope misstatement, demonstrated false-passing gate, impossible sequence). Findings 4–7 do not contribute to the verdict.

### Human decisions vs. plan defects

- **OQ-1 (run order)** — human decision. The options table is adequate and the `SEQUENCING_GATE` predicate reproduces its planning-time refusal (`REFUSED: MEU-55 … MEU-56 …`). Not a defect.
- **OQ-2 (tools disabled with no shot)** — human decision. Note for the decider: CP5 is already a locked `DECISION_SET` entry ("visible but disabled"), so option A is `Spec`; the genuine human question is authorizing the TM-3 expectation change (AGENTS §Testing). The table's pros/cons are accurate. Not a defect.
- **OQ-3 (disclosure starts closed)** — human decision; table adequate. Not a defect. (Note: `Disclosure` renders its panel with `hidden`, so `capture-picker`'s `toHaveValue` wait still resolves; TM-4's toggle click is only needed before `fill`/`click`.)
- **OQ-4 (`TEST_MIGRATIONS`)** — the *decision* is human, but the *list* is a plan defect (Finding 1). The human cannot meaningfully approve it until the census is complete.

### Out-of-Contract Observations (non-blocking)

1. `capture-page.test.ts:248` requires `bg-accent` in `CaptureFilmstrip.tsx`; the mockup's new selected style ("50 % accent border + 8 % fill") should keep a `bg-accent/…` utility so the regex still matches.
2. The `SegmentedControl` primitive labels its `fieldset` with `aria-label={name}`; if the cookie segment's `name` stays `cookie_mode`, the accessible group name becomes "cookie_mode" — consider passing a human label.
3. `FormRow` uses `sm:grid-cols-[10.5rem_…]` (168 px) — consistent with `SETTINGS_CAP`'s form grid; no primitive change is needed there.
4. H1-1's row predicate (`re.search(r'[[][xB][]]', l)`) matches anywhere in the row, so task text containing `[x]` would false-pass; rows 1–7 contain none today. Simulated on the live file: it correctly reports rows 1–7 open.

---

## Checklist Results

### Plan Review (PR)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | fail | Scope and order agree (WP-1…WP-5, rows 1–7, H1, H2, Handoff Set), but the plan's statements that `TEST_MIGRATIONS` is complete and that W9/AC-59/AC-60 stay green are contradicted by file state (Finding 1); H1-3's canon edit is not reconciled with `layout-canon.test.ts` (Finding 2). |
| PR-2 Not-started confirmation | pass | `git status --porcelain` → only the untracked plan folder; HEAD `0f51036`; no `capture-filmstrip-label.ts`, `SettingsRail.tsx`, `settings-sections.ts`, new tests, MEU handoffs or implementation review exist; all 17 rows `[ ]`. |
| PR-3 Task contract completeness | pass | `lint_task_contract.py` → `OK: 17 row(s); 10-column table (with builder_model); … backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic` (exit 0). |
| PR-4 Validation realism | fail | Tools/scripts/specs all exist (`tools/*.py`, `openapi.committed.json`, reflection template/schema, every named unit/E2E file, `playwright-with-outputfile.mjs` consumes `--outputFile` and strips `--reporter=json`; `testMatch` includes `*.spec.ts` so `help-search.spec.ts` is valid). But rows 2/5 cannot exit 0 on their planned inputs (Finding 3), the completion gate false-passes after H1-3 (Finding 2), and H1-2/H2-2 cells are weaker than their prose (Finding 5). |
| PR-5 Source-backed planning | partial | ACs carry Spec/Local Canon/Research-backed/Human-decision labels; all cited canon rows (CP1–CP6, ST1–ST7), mockup §04 numbers (200 px / 56×36 / ~420 px / 176px+20 px / 960 / 168 px / ~760 px / 84 px), `06-gui.md:963,964,972,974,976,977,978,989,1004`, `09-screenshot-capture.md:554`, G30–G37/E2/UX1/UX2 headings, and reflection RULE-1..3 were verified to exist and say what the plan says. Gaps: Finding 1 (test contracts not sourced), Finding 6 (§05 rows unreconciled), Finding 7 (two path/line refs). |
| PR-6 Handoff/corrections readiness | pass | One canonical handoff per MEU and one rolling implementation review are named per `artifact-naming.md`; Round 1, so the census gate is n/a. Findings are resolvable via `/plan-corrections`. |
| PR-7 Scope discipline (C2) | pass | `deferred` → MEU-55/56 exist in `meu-status.yaml:1549–1599` and grouping Session 25. `out-of-scope` rows cite ST2/ST7/CP6/`COMPOSITION_LOCK`/grouping §not-do/AGENTS §Commits/PROFILE E5; each cited source was opened and genuinely omits the excluded item (e.g., ST 18 is "Full-width selects → 160 px selects" only; CP6 makes shot info optional; ST7 keeps readiness link IDs). No contract work is disguised as out-of-scope. |
| PR-8 Control reachability & totality | fail | Product-side chains are traceable and negative oracles are concrete (zero-PUT/zero-DELETE ledgers, `getHotkeyStatus` call count, `IntersectionObserver` fallback, `READINESS_LOADED` gating). Two controls are defeated by sequencing: the Red oracle is unreachable for the new-module tests (Finding 3), and the fresh-gate control is mutated after it fires with no re-run (Finding 2). |
| PR-9 Single-statement discipline | pass with Low note | Named contracts (`COMPOSITION_LOCK`, `SEQUENCING_GATE`, `SETTINGS_SECTION_SET`, `SAVE_MODE_CAPTIONS`, `READINESS_COUNT`, `CAPTURE_OVERLAY_DIRTY`, `FILMSTRIP_LABEL_RULE`, `CONFIRM_EXCLUSIVITY`, `NEW_TESTIDS`, `TEST_MIGRATIONS`, `PHASE11_EXIT_PREDICATE`, `POST_REVIEW_STATE`) are defined once. Census: `597`/`95` restated once each in plan and task as references; `MEU-50..56` appears three times but all as the same predicate. One competing literal: scope-audit path set (`packages/ mcp-server/` vs `packages/api mcp-server/src`) — Finding 7(c). |

### Documentation Review (DR)

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | fail | The plan's "complete list" and "stay green" claims do not match test-file state (Finding 1). Draft/unstarted status claims are accurate. |
| DR-2 Residual old terms | pass | No stale Session 26 slug or alternate review-file name; handoff/review paths follow `artifact-naming.md`. |
| DR-3 Downstream references updated | partial | SSOT/grouping/hub/focus/metrics updates are named with owners, but H2-2 asserts only two of them (Finding 5); the hub Next line is hand-maintained prose. |
| DR-4 Verification robustness | fail | The fresh gate does not survive H1-3 (Finding 2); the Red gate refuses its own inputs (Finding 3). |
| DR-5 Evidence auditability | pass | Every cell is an exact POSIX command with `${RECEIPTS_DIR}` receipt, immediate `code=$?` capture and `exit $code`; the linter confirms all 17. |
| DR-6 Cross-reference integrity | partial | Canon, grouping, SSOT dependencies (`MEU-57/58 depends_on: [MEU-51]`), mockups and live pages agree on scope. `SETTINGS_SECTION_SET` (10 + conditional MEU-61 panel) matches `SettingsPage.tsx:192–895` and `StartAtSignInControl.tsx:62–63`. The canon/mockup "9 section ids" discrepancy is real, but the planned fix collides with AC-50.4 (Finding 2). |
| DR-7 Evidence freshness | pass | Live source, tests, SSOT, hub and current-focus were inspected at HEAD `0f51036`; Session 24's 597/95 counts are treated as predecessor evidence only. |
| DR-8 Completion vs residual risk | fail | H2-2/`PHASE11_EXIT_PREDICATE` can declare Phase 11 complete with a failing `layout-canon.test.ts` on the tree (Finding 2). |

---

## GUI, Boundary and Sequencing Assessment

- **SEQUENCING_GATE vs. phase exit** — sound in principle: the predicate `MEU-50..56=approved --expect MEU-57..58=pending` reproduces `REFUSED: MEU-55: status 'pending' != 'approved'; MEU-56: …` (exit 1) against the live SSOT; grouping, `current-focus.md` and the phase-gate requirement all order Session 26 after 25; `PHASE11_EXIT_PREDICATE` additionally checks the plan binding for MEU-57/58 and is re-run in H2-2 after `POST_REVIEW_STATE`. The gate is reachable and its post-approval producer exists (the Session 24 Round-1 defect is not repeated).
- **Control binding** — every AC names an observable, a production entrypoint and a negative oracle. Verified against live code: `CAPTURE_OVERLAY_DIRTY` = `CapturePage.tsx:221–223`; `canSave` = `:224–233`; portal = `:927–1008`; tool buttons carry no `disabled` (`CaptureViewport.tsx:406–450`); `getHotkeyStatus` returns `{accelerator, registered, inUse}` (`capture-hotkey.ts:3–19`) and the page reads only `inUse` today (`CapturePage.tsx:413–417`); `schedulePut` debounce/empty-string filter (`useSettingsPage.ts:85–124`); `StartAtSignInControl` null-renders when unsupported (`:62–63`); `<main class="flex-1 min-h-0 overflow-auto">` is the scroll root (`AppShell.tsx:272–273`); `cookieBrowserVisible`/`cookieFileVisible` (`cookie-bar.ts:78–84`); `CaptureShotOut.created_at` (`schemas/captures.py:125`); `TIMESTAMP_FORMAT` (`services/capture.py:44,476`). The `FormRow`/`PathRow` primitives forward the caller's `data-testid` to the native input/button, so the "caller ID on a wrapper fails" oracle is implementable. `PathRow` has no `readOnly` prop today, so the additive prop is genuinely needed for the five read-only path inputs.
- **Boundary inventory** — matches live builders: `useCaptureSettings.save()` → `parseSettingsPut('capture', form)` → `PUT /settings/capture`; converter mirrors it; `SelectInput` renders its own `<label htmlFor>`, so the "no double label" oracle is a real risk the plan correctly names. No new API/IPC surface is introduced; `onAvailabilityChange` is a prop, not a channel.
- **Single-statement contracts** — well formed; `SAVE_MODE_CAPTIONS`, `NUMBER_HINT_SOURCES` and `CHECKBOX_COPY_SOURCES` cite real lines. `NEW_TESTIDS` placement after the MEU-51 marker keeps the AC-51.6 SHA-256 prefix lock intact (`layout-primitives.test.ts:183–197`).
- **GUI compliance** — the five reference files are absent and correctly recorded as `gui-refs-not-shipped`; live `Button` exposes the five variants/three sizes the plan cites; G30–G37, E2, UX1/UX2 exist in `emerging-standards.md`.
- **Out of Scope basis cells** — all evidence-backed (PR-7 pass).

---

## Commands and Static Evidence

All receipts under `RECEIPTS_DIR=/tmp/claude-0/-home-user-av-kit/732d64b0-ff02-55ac-8b7c-1f17da32a6cc/scratchpad/receipts`. `rtk` is not on PATH in this container (confirmed `which rtk` empty, `~/.cargo/bin` has no `rtk`), so the reviewer ran the two allowed verifiers directly, unfiltered.

| Command | Exit | Decisive output |
|---|---|---|
| `uv run python docs/execution/plans/2026-09-28-p11-capture-settings/plan_checks.py self-test > "$RECEIPTS_DIR/rev-selftest.txt" 2>&1` | 0 | `PASS SELF-TEST: 15 cases (positive and adversarial) behaved as specified` |
| `uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-09-28-p11-capture-settings/task.md > "$RECEIPTS_DIR/rev-lint.txt" 2>&1` | 0 | `OK: 17 row(s); 10-column table (with builder_model); 17 row(s) fully checked …` |
| `uv run python docs/execution/plans/2026-09-28-p11-capture-settings/plan_checks.py meu-state --expect MEU-50..56=approved --expect MEU-57..58=pending > "$RECEIPTS_DIR/rev-meustate.txt" 2>&1` | 1 | `REFUSED: MEU-55: status 'pending' != 'approved'; MEU-56: status 'pending' != 'approved'` (matches the plan's planning-time receipt) |
| `git status --porcelain`; `git log --oneline -5` | 0 | `?? docs/execution/plans/2026-09-28-p11-capture-settings/`; HEAD `0f51036 docs(execution): record queue pages approval` |
| Path-existence sweep over every file the plan cites (58 paths) | — | All tool/test/spec/doc paths exist; `useCaptureSettings.ts` lives under `features/capture/`, `useConverterSettings.ts` under `features/converter/`, `capture-hotkey.ts` under `ui/src/main/`, `AppShell.tsx` under `components/layout/`; `schemas/capture.py` does not exist (it is `captures.py`, Finding 7). `xvfb-run` present, `DISPLAY` unset, `dotnet` absent, `native/region-picker-stub/publish/` absent. |
| `python3` simulation of the H1-1 row predicate on the live `task.md` | — | reports rows `['1','2','3','4','5','6','7']` open (correct). |
| Repeated-literal census (`597`, `95`, `ready_for_review`, `MEU-50..56`, `MEU-50..58`, `packages/`, `mcp-server/`, `TM-1`, `168 px`, `176px`, `960`, `200 px`, `9 section`) | — | Only the scope-audit path set has two competing spellings (Finding 7c). |
| `rg`/`sed` reads of every cited line range in canon, mockups, live source and tests (see Scope) | — | Line references verified; deviations listed in Finding 7. |

No project test, build, generator, `npm install` or `tools/meu_status.py update` was executed. No file other than this review was written.

---

## Open Questions / Assumptions

- The review assumes the executor will honor the plan's stop conditions literally; Findings 1–3 are rated on that basis (each halts the run), not on an executor improvising a stub, a helper rewrite or a mockup edit.
- The review does not decide OQ-1..OQ-4; it assesses the option tables as adequate except that OQ-4's list must be completed first (Finding 1).
- `TASK-TEMPLATE.md` sets `status: "in_progress"`; the plan's `task.md` uses `"draft"`. Treated as a non-issue (the row legend governs execution state), consistent with the Session 24 Round-2 reading.

---

## Verdict

`changes_required` — executing the plan as written stalls at row 2 because the Red oracle refuses the new-module test files it is told to run (Finding 3); once past that, CP1/CP4 and the moved action IDs contradict at least five pre-existing assertion sites that `TEST_MIGRATIONS` omits while claiming completeness, so OQ-4 asks the human to approve an incomplete migration list (Finding 1); and H1-3's canon edit fails `layout-canon.test.ts` AC-50.4 after the only full Vitest run, so `PHASE11_EXIT_PREDICATE` would certify Phase 11 on a red tree (Finding 2). Each is an evidence-backed High under the Verdict Rule. The sequencing gate, control bindings, single-statement contracts, boundary inventory and Out-of-Scope basis cells are otherwise sound and were verified against sources, not the author's word.

## Follow-up Actions

1. Route corrections through `/plan-corrections`; do not implement product code.
2. Finding 1: run and attach an `rg` census over `ui/tests/**` for `capture-save`, `capture-delete`, `capture-open-file`, `capture-open-folder`, `capture-empty`, `Press F2`, `capture-filmstrip` text assertions and `mcp-token-present`; add each contradicted site to `TEST_MIGRATIONS` with its canon source, or constrain the design so it stays true. Re-present OQ-4 with the complete list.
3. Finding 2: remove the post-gate canon edit from H1-3 or move it (with the mockup cell and a `layout-canon.test.ts` re-run) before H1-2; add a rule that any edit after H1-2 re-runs the affected D6 rows before H2-2.
4. Finding 3: name once how new-module unit tests reach assertion Red (scaffold exception or split oracle) and fix rows 2/5.
5. Findings 4–6: decide the execution host / picker-stub treatment at row 1; strengthen H1-2/H2-2 predicates; add the §05 disposition table.
6. Re-submit this rolling file for Round 2 with the untruncated blast-radius census and per-hit dispositions (PR-6).

## Residual Risk

After Findings 1–3 are corrected, the main execution risk is breadth of UI regression across two large pages under a locked composition contract with no central GUI checklist; the plan's per-AC negative oracles and written-and-wired Electron waves are the available proof and must not be replaced by source-only checks. Environment risk (Finding 4) remains until the human names the host on which the Phase 11 exit gate runs.

---

# Round 2 — 2026-09-28 (resubmission after `/plan-corrections`)

> **Review Mode**: `plan` · **Reviewer**: Fable 5.1 subagent (separate context, user-directed route per `human-review-decision.md`; did not author the plan or the corrections)
> **Verdict**: `approved` with correction notes — no evidence-backed High/Critical finding survives; one Medium and five Low are recorded below.

## Intent Anchor (unchanged)

Executing this plan must deliver MEU-57 (Capture) and MEU-58 (Settings) recomposed under `COMPOSITION_LOCK` with every test ID kept and only human-approved `TEST_MIGRATIONS` touching pre-existing expectations, then one fresh full D6 Phase 11 exit gate, independent execution approval, and the SSOT/hub/grouping/focus reconciliation that marks Phase 11 complete. Round 2 asks whether the corrected plan would now deliver that. It would: the three Round 1 delivery blockers are closed on the live tree (the Red oracle accepts the new-module files, the post-gate canon edit is gone and the doc-reading tests are re-run after every later document edit, and the migration list now has a census-and-stop mechanism in front of any test edit). The residual defect (Finding R2-1) turns into a designed stop at task row 2, not a false pass.

## PR-6 gate: blast-radius census verification (checked before the corrected content)

| Check | Result | Evidence |
|---|---|---|
| Receipt named and present | pass | `implementation-plan.md:414` names `p11cs-census-r1.txt`; file exists at `${RECEIPTS_DIR}/p11cs-census-r1.txt` (63,432 bytes, 164 lines). |
| Receipt untruncated | pass | 37 `=== census:` headers, each closed by its own `rg_exit=` line (10 × `rg_exit=1`, 27 × `rg_exit=0`); 37 + 37 + 90 hit lines = 164 lines. No sweep is cut off; no head/tail truncation. |
| Every hit dispositioned | pass | All 90 `file:line` hits map to a row of `review-r2-census.md` (old-value table 12 rows, new-value table 16 rows). Per-cluster line lists reproduce exactly (e.g. `TM-*` → plan:105,140,177,201,203,387,406 + task:37; `DOC_READING_TESTS`/`post-review` → plan:142,144,145,280,281,338,407,410 + task:54; `EXECUTION_HOST`/`OQ-5` → plan:68,106,365,388,409 + task:35). Dispositions are `updated` / `confirmed-consistent` / `stale→fixed`, not bare counts. |
| Log ⊆ receipt | pass with note | The log lists `task:46` under `DOC_READING_TESTS` and claims three re-sweeps (`58.12`, `hub row`, `OQ-1..OQ-4`) that are not in the receipt. This review reproduced them live: `OQ-1..OQ-4` → 0 hits; `58.12` → plan:233,257,358; `hub row` → plan:145; `TM-1..TM-4` and `rows 1–7` → 0 hits. Over-inclusion in the log, not an undispositioned hit (Low, R2-6). |

Gate outcome: the census is present, untruncated and dispositioned, so the corrected content is reviewed this round.

## Round 1 finding status (re-verified against the live tree at HEAD `79079d0`)

| R1 # | Sev | Status | Evidence |
|---|---|---|---|
| F1 `TEST_MIGRATIONS` incomplete | High | **partially fixed** | TM-5 (`capture-page.behavior.test.ts:257–271` helper), TM-6 (`:455`, `:664`, `:682`), TM-7 (`capture-inbox.test.ts:412,455,516`) match the file. `CAPTURE_SOURCE_LOCATION` keeps the `capture-save`/`capture-delete`/`capture-open-*`/`capture-empty`/`Press F2 or Capture region` literals in `CapturePage.tsx`, which is exactly what `capture-page.test.ts:278,296,301–302,311–312` (`readRequired(pagePath)`) require; `AC-39.8:262–268` still finds the tool/undo/redo IDs in `CaptureViewport.tsx`. The sr-only full name keeps `capture-picker.test.ts:218–221` green (`toContainText` reads `textContent`, not `innerText`). `MCP_TOKEN_TEXT` is today's exact string (`SettingsPage.tsx:899–900`) so `settings-page.test.ts:483` stays green. `CAPTURE_READY_SIGNAL` is sound: `setOverlayReady(true)` fires only after the detail parse (`CapturePage.tsx:393–395`), so `overlayReady && imageEpoch > 0` implies both detail and image loaded — no weaker than the `canSave` wait it replaces. **Not fixed:** no fresh census was run; three more pre-existing sites contradict the plan's own ACs and are absent from TM-1..TM-7 (Finding R2-1). |
| F2 post-gate canon edit / no re-verify | High | **fixed** | Canon edit removed (`implementation-plan.md:124,280`; `task.md:46` "Do **not** edit the canon"). `DOC_READING_TESTS` = exactly the three files `rg -l "BUILD_PLAN|current-focus|session-grouping|meu-status|metrics\.md"` finds (`ui/tests/unit/layout-canon.test.ts`, `ui/tests/unit/queue-canon.test.ts`, `tests/tooling/test_framework_adoption.py`); H1-3 and H2-2 run them after their edits. Compatibility checked: AC-50.6 (`layout-canon.test.ts:169–174`) pins the quoted baseline sentence at `BUILD_PLAN.md:36`, which `POST_REVIEW_STATE` (phase row `:55`, Next line `:72`) does not touch; the grouping assertion (`:152–153`) is unrelated to Session 26 status. |
| F3 Red oracle unreachable for new-module files | High | **fixed** | `plan_checks.py red --new-file` (`:39`, `:59–89`) accepts a declared new file only when it fails with a missing-module message and still demands an assertion Red for the prefix from other files; self-test 26 cases exit 0 (reproduced, `rev2-selftest.txt`). Rows 3/6 pin exactly one `--new-file` each. Reporter shape: `vitest@3.2.7` is locked (`ui/package-lock.json`); its JSON reporter emits `testResults[].status: "failed"`, empty `assertionResults` and `message` = first file error for a file that fails to import, and Vite 7 reports `Failed to resolve import "…" … Does the file exist?`, which `MODULE_MISSING` matches. (`ui/node_modules` is absent in this container, so this is verified from the reporter source, not from disk.) Playwright `1.62.1`: `stats.expected/unexpected/flaky`, `suites[].specs[].tests[].results[].status/error/errors` and top-level `errors` are the documented JSON shape; the wrapper (`ui/scripts/playwright-with-outputfile.mjs`) strips `--reporter=json`, forwards `<spec> -g AC-5N`, and `playwright.config.ts` writes the JSON reporter to `PLAYWRIGHT_JSON_OUTPUT_NAME`. |
| F4 Linux cannot run the gates | Medium | **fixed (human decision)** | `EXECUTION_HOST`/OQ-5 (`:68`, `:106`, `:388–389`), row 1 tests the stub `.exe` and `rtk`, and a stop condition (`:365`) names it. Residual clerical: `§Harness:60` still states the web Linux driver unconditionally (R2-6). |
| F5 closeout predicates weaker than prose | Medium | **fixed** | `plan_checks.py counts` (`:221–236`) and `post-review` (`:239–276`). Reproduced the live negative: `post-review --plan …` → exit 1, `REFUSED: grouping Session 26 row lacks approved + plan folder; hub Phase 11 row not completed; metrics has no p11-capture-settings row`. Its anchors exist: grouping row `| 26 |` (`grouping:71`), hub row `| 11 — Page layout` (`BUILD_PLAN.md:55`), `Next:` line (`:72`), `execution_plan` field (`meu-status.yaml` MEU-54), `tools/meu_status.py next --limit 1` (returns `MEU-55` today). H1-2 now carries `task-contract`, `--outputFile.json=` (valid Vitest 3 dot-notation; `ui` `test` script is plain `vitest run --allowOnly=false`) and the `counts` floors. |
| F6 ST 14/29/31 unreconciled | Medium | **fixed** | AC-58.13 (`:234`); canon `11-page-layout.md:252,267,269` say what it cites. |
| F7 clerical references | Low | **fixed** | `schemas/captures.py`; `flushPut` at `useSettingsPage.ts:67–79`, `putNow` at `:126–144`; single `API_SCOPE_PATHS`, used by task H1-4. |

## Round 2 findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation |
|---|---|---|---|---|---|---|
| R2-1 | Medium | no | behavior (F1 residual) | **`TEST_MIGRATIONS` still calls itself "the complete set" while three further pre-existing sites contradict the plan's own ACs.** This review ran the plan's own `MIGRATION_CENSUS` sweep (`rev2-migration-census.txt`, 218 hits) and read every `capture-save`/`capture-tool-` site. (a) AC-59.8 "selecting a shot loads GET detail annotations and a 422 does not wipe them" (`capture-page.behavior.test.ts:415–439`): after the click on item 1 the page resets `annotations`/`saved` to `[]` (`CapturePage.tsx:351–353`), so the shot is clean and under CP1/AC-57.6 `capture-save` is unmounted — `:432` and `:436` (`getByTestId('capture-save')`) throw. (b) AC-60.8 "selecting a named-color mark … without … dirtying Save" (`:643–652`): a clean shot with saved marks; `:650` asserts `disabled === false` on an element that is absent by design. (c) AC-39.28 (`:336–349`): `:343` asserts `capture-tool-arrow` has `h-9`, but AC-57.5 makes the tool segment `sm`, which is `h-7` (`Button.tsx:23`); the page auto-selects the newest shot (`CapturePage.tsx:243–251`) so the `aria-pressed` half survives OQ-2 = A. None is in TM-5..TM-7. Because `MIGRATION_CENSUS` (task row 2) lists `capture-save` and `capture-tool-` and stops on any new-contradiction, execution halts for a human decision before any test edit rather than false-passing — so this is contained, and it is the same class as R1-F1, not a new failure mode (Materiality Gate #4). It remains a scope misstatement: OQ-4 asks the human to approve a list this review can already show is short, and the run will re-ask at row 2. | `implementation-plan.md:140` ("complete set"), `:387` (OQ-4); `ui/tests/unit/capture-page.behavior.test.ts:336–349, 415–439, 643–652`; `ui/src/renderer/src/components/ui/Button.tsx:23`; `ui/src/renderer/src/features/capture/CapturePage.tsx:243–251, 351–353` | Add TM-8 (AC-59.8 `:432/:436` → `capture-save` absent, then mounted-and-enabled only after a mark), TM-9 (AC-60.8 `:650` → absent on a clean shot), TM-10 (AC-39.28 `:343` → `h-7`, or keep the tool buttons `md` and say so in AC-57.5). Replace "complete set" with "complete as of the planning-time census receipt `<name>`" and attach that receipt; re-present OQ-4 with TM-1..TM-10. |
| R2-2 | Low | no | clerical / underspecified migration | TM-1 says "add [CapturePage/SettingsPage] to the positive-adoption loop", but that loop asserts all three of `Disclosure`, `SegmentedControl`, `StatusChip` per page (`layout-primitives.test.ts:222–230`). Per the ACs, `CapturePage` will not import `SegmentedControl` (the tool segment is buttons with `aria-pressed`, AC-57.5) and `SettingsPage` need not import `Disclosure`. Written literally, TM-1 fails Green and cannot be edited there. | `implementation-plan.md:140` (TM-1); `ui/tests/unit/layout-primitives.test.ts:222–230` | Name the per-page primitive set in TM-1 (Capture: `Disclosure`, `StatusChip`, `PathRow`; Settings: `SegmentedControl`, `StatusChip`, `FormRow`, `PathRow`) and let the loop take a per-page list. |
| R2-3 | Low | no | clerical | AC-57.3 says the hotkey banner is "shown only when `inUse`". W9-3 `capture-inbox.test.ts:227` asserts `capture-hotkey-banner` `toBeVisible()` with `inUse` false; today it passes only because the empty `<p>` keeps `min-h-4` (`CapturePage.tsx:1178`). One sentence is missing: the banner element stays mounted with reserved height when empty (else it is a TM). `MIGRATION_CENSUS` (`capture-hotkey`) would surface it at row 2. | `implementation-plan.md:170`; `ui/tests/e2e/capture-inbox.test.ts:227`; `ui/src/renderer/src/features/capture/CapturePage.tsx:1178` | Add "the banner element stays mounted with its reserved height; only its content is conditional" to AC-57.3. |
| R2-4 | Low | no | observable | AC-57.4's negative test ("a name starting `2026-09-03 ` renders without it") has no named observable: with the sr-only full name inside the item, the item's `textContent` still contains the prefix, and jsdom cannot tell sr-only from visible text. | `implementation-plan.md:131`, `:171`, `:133` (`NEW_TESTIDS`) | Add `capture-filmstrip-name` and `capture-filmstrip-time` to MEU-57 `NEW_TESTIDS` and assert the visible line on them. |
| R2-5 | Low | no | verification-quality | `$RECEIPTS_DIR` and `${E2E_WRAP}` are expanded inside single-quoted `bash -c '…'` in rows 5, 8, H1-2, H1-3, H2-2, H2-3, so they must be **exported**; the task preamble only says "set". An unexported variable makes `--outputFile.json=/p11cs-phase-vitest.json` and `counts --vitest-json /…`, which fails or fails closed — not a false pass — but it costs a gate re-run. | `task.md:31`, `:39`, `:42`, `:45`, `:46`, `:54`, `:55` | Row 1: `export RECEIPTS_DIR E2E_WRAP` and say so in the preamble. |
| R2-6 | Low | no | clerical | (a) `implementation-plan.md:27` baseline `0f51036` is stale — HEAD is `79079d0` (plan and R1 corrections committed, worktree clean). (b) `§Harness:60` states "Driver: Claude Code (web), Linux container" unconditionally while OQ-5 recommends the Windows host; say "planning driver; execution driver per OQ-5". (c) `review-r2-census.md` claims re-sweeps (`58.12`, `hub row`, `OQ-1..OQ-4`) and a `task:46` hit that are not in the receipt (reproduced live above). | `implementation-plan.md:27`, `:60`; `review-r2-census.md:4`, `:21`, `:36`, `:43` | One-line edits; append the re-sweep output to the receipt on the next correction. |

Materiality: R2-1 is the only non-clerical item and is contained by the plan's own row-2 stop; R2-2..R2-6 are clerical or observation-grade with the correction stated inline. No finding demonstrates a false-passing gate, an impossible sequence or an omitted deliverable, so the Verdict Rule yields `approved` with correction notes.

### Human decisions vs. plan defects

- **OQ-1, OQ-2, OQ-3** — unchanged human decisions; option tables still adequate (see Round 1 notes).
- **OQ-4** — human decision, but the list it presents is short by three sites (R2-1). The human can approve TM-1..TM-7 now on the understanding that row 2 will stop and re-ask, or the corrector can complete the list first.
- **OQ-5 `EXECUTION_HOST`** — genuine human decision, correctly framed: option B cannot exit Phase 11 (stub `.exe` at `capture-picker.test.ts:25`, no `rtk`), option A is coherent with the Claude Code profile row (`native_shell: … bash (Bash tool)`, `fresh_worker: Agent tool` under `harness.local.md` §Claude Code) and the same-vendor reviewer route still resolves there. Not a defect.

### Out-of-Contract Observations (non-blocking, ≤ 5)

1. New AC tests added to *existing* files must not import a not-yet-existing module, or that whole file becomes a collection failure the oracle refuses (only the declared `--new-file` may). Worth one sentence in §Verification Plan item 2.
2. A filmstrip item's accessible name will contain the full file name twice (`alt` + sr-only); consider `aria-hidden` on the visible stripped-name span or dropping the duplication.
3. `SegmentedControl` labels its fieldset `aria-label={name}` (carry-forward from Round 1).
4. `capture-page.test.ts:248` requires `bg-accent` in `CaptureFilmstrip.tsx` (carry-forward).
5. H1-1's `[x]`-anywhere predicate (carry-forward; rows 1–8 contain none today).

## Checklist Results (Round 2)

### Plan Review (PR)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass with note | WP-1..WP-5 ↔ rows 1–8/H1/H2 agree; `MIGRATION_CENSUS` is task row 2 and every later row renumbered; TM-1..TM-7, `CAPTURE_READY_SIGNAL`, `CAPTURE_SOURCE_LOCATION`, `DOC_READING_TESTS`, `COUNT_FLOORS`, `API_SCOPE_PATHS` are used consistently (census verified). The one remaining misstatement is "complete set" (R2-1). |
| PR-2 Not-started confirmation | pass | HEAD `79079d0`, `git status --porcelain` empty; no `capture-filmstrip-label.ts`, `SettingsRail.tsx`, `settings-sections.ts`, new test files, MEU handoffs or implementation review; all 18 rows `[ ]`. |
| PR-3 Task contract completeness | pass | `lint_task_contract.py` → `OK: 18 row(s); 10-column table (with builder_model); 18 row(s) fully checked … dependencies resolve and are acyclic` (exit 0, `rev2-lint.txt`). |
| PR-4 Validation realism | pass | Rows 3/6 now exit 0 on their planned inputs (F3 fixed); H1-2 is one chain ending in `counts`; H2-2 ends in `post-review` + `DOC_READING_TESTS` + `PHASE11_EXIT_PREDICATE`; every executable exists (`plan_checks.py`, `tools/lint_task_contract.py`, `tools/validate_closeout_artifacts.py`, `tools/meu_status.py`, `tools/export_openapi.py`, the wrapper, every named test file). Residual: export requirement (R2-5). |
| PR-5 Source-backed planning | pass | ACs keep Spec/Local Canon/Research-backed/Human-decision labels; AC-58.13 sources ST 14/29/31 verbatim; new line references (`capture-hotkey.ts:17–40`, `StartAtSignInControl.tsx:30–64/47–61`, `useSettingsPage.ts:67–79/126–144`, `captures.py:125`, `capture-picker.test.ts:25,218–221`, `settings-page.test.ts:483,489–494`, `layout-canon.test.ts:130–147`) were opened and say what the plan says. |
| PR-6 Handoff/corrections readiness | pass | Census receipt untruncated and dispositioned (table above); handoff set unchanged; findings resolvable via `/plan-corrections`. |
| PR-7 Scope discipline (C2) | pass | Out-of-Scope table unchanged from Round 1 (all rows evidence-backed; MEU-55/56 exist in `meu-status.yaml`). |
| PR-8 Control reachability & totality | pass | Both Round 1 control defeats are closed: the Red oracle reaches the new-module files (`--new-file`), and the fresh-gate control is re-asserted by `DOC_READING_TESTS` after every later doc edit. `CAPTURE_READY_SIGNAL` has a producer (`overlayReady` is set only after detail parse). `post-review` has an observable per document and refuses today. |
| PR-9 Single-statement discipline | pass | Old spellings gone (`TM-1..TM-4`, `hub-audit`, `schemas/capture.py`, `mcp-server/src`, `rows 1–7`, `Four items` all 0 hits). `597`/`95` appear as `COUNT_FLOORS` plus the two executable instances, which the plan names as such. |

### Documentation Review (DR)

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | pass with note | Corrections table (`:400–414`) claims match the tree for F2–F7; F1's "avoided further migrations by design" is true for the four R1 sites it names but the "complete" claim is not (R2-1). |
| DR-2 Residual old terms | pass | Old-value census rows all `rg_exit=1`; reproduced. |
| DR-3 Downstream references updated | pass | H2-2 now asserts grouping/hub/focus/metrics via `post-review`; task row numbering, WP table and H1-1 predicate updated to rows 1–8. |
| DR-4 Verification robustness | pass | Post-H1-2 doc edits are re-tested; `counts` fails closed on missing/unshaped JSON; `red` refuses syntax errors in new files (self-test v8). |
| DR-5 Evidence auditability | pass | Every cell remains an exact POSIX command with receipt, `code=$?`, `exit $code`; census receipt reproducible. |
| DR-6 Cross-reference integrity | pass | Canon, grouping, SSOT, mockups, live pages and tests agree; the "9 section ids" label is now explicitly left unedited. |
| DR-7 Evidence freshness | pass with note | Live tree at `79079d0`; plan baseline text still says `0f51036` (R2-6a). |
| DR-8 Completion vs residual risk | pass | `PHASE11_EXIT_PREDICATE` now includes the post-H2 `DOC_READING_TESTS` rerun; Phase 11 cannot be declared complete on a tree with a red doc-reading test. |

## Commands and Static Evidence (Round 2)

All receipts under `RECEIPTS_DIR=/tmp/claude-0/-home-user-av-kit/732d64b0-ff02-55ac-8b7c-1f17da32a6cc/scratchpad/receipts`. No project test, build, `npm install`, generator or repo-mutating command was run; no file other than this review was written.

| Command | Exit | Decisive output |
|---|---|---|
| Receipt audit of `p11cs-census-r1.txt` (`grep -n "^=== census\|^rg_exit"`, per-sweep hit extraction) | — | 37 sweeps, 37 `rg_exit`, 90 hits, 164 lines; every hit found in `review-r2-census.md`. |
| `rg -F -n` live re-sweeps: `OQ-1..OQ-4`, `58.12`, `hub row`, `TM-1..TM-4`, `rows 1–7` | 1/0/0/1/1 | 0 hits; plan:233,257,358; plan:145; 0; 0 (matches the log's claims). |
| `uv run python …/plan_checks.py self-test > rev2-selftest.txt` | 0 | `PASS SELF-TEST: 26 cases (positive and adversarial) behaved as specified` |
| `uv run python tools/lint_task_contract.py … --task …/task.md > rev2-lint.txt` | 0 | `OK: 18 row(s); …` |
| `uv run python …/plan_checks.py meu-state --expect MEU-50..56=approved --expect MEU-57..58=pending > rev2-meustate.txt` | 1 | `REFUSED: MEU-55: status 'pending' != 'approved'; MEU-56: …` (planning-time state, as the plan says) |
| `uv run python …/plan_checks.py post-review --plan docs/execution/plans/2026-09-28-p11-capture-settings > rev2-post-review.txt` | 1 | `REFUSED: grouping Session 26 row lacks approved + plan folder; hub Phase 11 row not completed; metrics has no p11-capture-settings row` (live negative reproduced) |
| `uv run python tools/meu_status.py next --limit 1` | 0 | `MEU-55 gui-transcript-layout` (the `_ssot_next` producer exists) |
| `rg -n -e capture-save … -e components/ui/ ui/tests > rev2-migration-census.txt` (the plan's own `MIGRATION_CENSUS` argv) | 0 | 218 hits across 20 files; every `capture-save`/`capture-tool-` site read (R2-1). |
| `rg -l "BUILD_PLAN\|current-focus\|session-grouping\|meu-status\|metrics\.md" ui/tests tests mcp-server/tests` | 0 | exactly `tests/tooling/test_framework_adoption.py`, `ui/tests/unit/layout-canon.test.ts`, `ui/tests/unit/queue-canon.test.ts` (= `DOC_READING_TESTS`) |
| `python3` read of `ui/package-lock.json` | — | `vitest 3.2.7`, `@playwright/test 1.62.1`, `vite 7.3.6`; `ui/node_modules` absent |
| `git log --oneline -2`; `git status --porcelain` | 0 | `79079d0 docs(plan): apply Session 26 plan review round 1 corrections`; clean |
| `sed`/`rg` reads of every cited line in canon, mockups, live source and tests (see tables) | — | Line references verified; deviations recorded in R2-1/R2-6. |

## Open Questions / Assumptions (Round 2)

- The Vitest JSON `message` field and Vite's missing-import wording were verified from the pinned versions' reporter/plugin sources, not from an installed `node_modules` (absent here). The plan's row-1 `npm ci` plus the first real Red run will confirm on the chosen host.
- This review assumes the executor honours `MIGRATION_CENSUS` literally at row 2; R2-1's severity rests on that stop existing.

## Verdict (Round 2)

`approved` — with correction notes. All three Round 1 High findings are closed on the live tree (F2, F3 fixed; F1 partially fixed and now contained by the row-2 census stop), and F4–F7 are fixed. The surviving items — one Medium (three unlisted CP1/`sm`-size contradictions in `capture-page.behavior.test.ts` while the plan still says "complete set") and five Low (TM-1 per-page primitive set, banner reserved height, filmstrip name/time observable, `export` of `RECEIPTS_DIR`/`E2E_WRAP`, stale baseline/driver/census-log lines) — do not demonstrate a false-passing gate, an impossible sequence or an omitted deliverable. Reviewer `approved` authorizes nothing further: Claude Code resolves `plan_to_exec_gate: human`, and OQ-1..OQ-5 still need the user's execution message.

## Follow-up Actions (Round 2)

1. Optional `/plan-corrections` pass for R2-1..R2-6 before the execution message, or accept them as correction notes and let row 2 stop for TM-8..TM-10; either way re-present OQ-4 with the full list.
2. Decide OQ-5 (host) first — it determines whether Phase 11 can exit in this session at all.
3. On the next correction, append any re-sweep output to the census receipt so log and receipt coincide.

## Residual Risk (Round 2)

Breadth of UI regression across two large pages under a locked composition contract remains the main execution risk; the per-AC negative oracles and the written-and-wired Electron waves are the proof and must not be replaced by source-only checks. The migration list will grow at row 2 (R2-1); that is a planned human stop, not a false pass. Environment risk closes only when the human picks OQ-5 = A.
