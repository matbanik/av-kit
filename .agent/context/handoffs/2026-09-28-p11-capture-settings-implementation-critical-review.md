---
date: "2026-09-29"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md"
round: 2
verdict: "approved"
findings_count: 3
template_version: "2.2"
requested_verbosity: "detailed"
agent: "claude-fable-5-1-subagent"
loop_id: "p11cs-execution-review-2026-09-29"
---

# Critical Review: 2026-09-28-p11-capture-settings (Round 1)

> **Review Mode**: `execution`
> **Verdict**: `changes_required`

---

## Review binding

- **Intent anchor**: The plan's goal is to *"Deliver Session 26 as grouped"* — MEU-57 `gui-capture-layout` (header row with the hotkey key cap and a Settings disclosure, a 200 px filmstrip, a viewport toolbar with the tool segment and per-shot actions, inline confirm strips) and MEU-58 `gui-settings-layout` (960 px two-column grid, sticky IntersectionObserver rail, 168 px form grid, path+Browse rows, save-mode captions, chip-list diagnostics), both inside `COMPOSITION_LOCK`, followed by the Phase 11 exit gate. The verdict below answers whether the delivered code achieves that.
- **Intent achieved**: `partial` — both pages are composed as specified, every payload, mutation, enablement rule and test ID is preserved, the A8 typing fix is equivalence-proven, TM-1..TM-12 are the only expectation changes, and the authoritative Windows gate is clean on the code-identical commit; but moving the confirmation into the viewport and focusing its Cancel button puts the confirmation inside the annotation editor's keyboard scope, so Delete and arrow keys pressed on the open strip silently mutate the overlay under confirmation (reproduced; the pre-change portal was inert to the same keys).
- **Reviewed state**: HEAD `e514443` (branch `claude/quirky-gates-o1lql2`), clean tree. Code-identical under `ui/`, `packages/`, `mcp-server/`, `tests/` to the Windows-gated commit `7613beb` (`git diff 7613beb HEAD --stat -- ui packages mcp-server tests` is empty, exit 0). Session baseline for the diff is the merge `1f9b035` (Session 25 merged from `main`); planning baseline `0f51036`.
- **Reviewer**: independent Claude Code `Agent` subagent, Fable 5.1, high effort requested, per `human-review-decision.md` (`USER_EXPLICIT`, same-vendor exception recorded there). The reviewer did not author any of the work and wrote this file directly; no product, test, plan, task, walkthrough or work-handoff file was modified. Scratch probes ran only under `<scratchpad>/review-r1/`.
- **Verdict-rule conflict surfaced**: `.agent/workflows/execution-critical-review.md` §Verdict Rule says `changes_required` needs a `High`/`Critical`; the dispatch prompt for this round says "Approve only if no High or Critical finding remains, and no Medium finding that is a demonstrated runtime defect inside an AC's contract". Finding 1 is a demonstrated runtime defect with a reproducer on the surface AC-57.7 defines (the inline strip, its focus target, and `CONFIRM_EXCLUSIVITY`), so the stricter dispatch instruction is applied, exactly as Session 25 Round 1 did. If the orchestrator/user rules that the editor-key scope is outside AC-57.7's literal text, the same file state would be `approved` with Finding 1 open as `Blocking: no`.

---

## Scope

**Target**: MEU-57 and MEU-58 work handoffs (`.agent/context/handoffs/2026-09-28-p11-capture-settings-MEU-57-handoff.md`, `-MEU-58-handoff.md`); `implementation-plan.md` (FIC AC-57.1–57.10, AC-58.1–58.13, single-statement contracts, `TEST_MIGRATIONS` TM-1..TM-12, amendments A1–A11, A11-W, A10-R), `task.md`, `walkthrough.md`, `human-gate-decision.md`, `human-review-decision.md`, `validate-task.sh`/`.ps1`, `plan_checks.py`, `windows-gate-result.json`; `docs/build-plan/11-page-layout.md` (COMPOSITION_LOCK, CP1–CP6, ST1–ST7, §Test-ID migration); the full `git diff 1f9b035 HEAD` (33 files, +4066/−1030; 19 code/test files +2636/−987); `tests/tooling/test_framework_adoption.py` at `4047bfc`→`7613beb`; SSOT (`meu-status.yaml`, `meu-registry.md`, `current-focus.md`, Phase 11 grouping, `docs/BUILD_PLAN.md`).
**Review Type**: execution review (multi-MEU project; both handoffs loaded per the Project-Integrated Handoff rule; Session 25 code excluded except where Session 26 changed it — no Session 25 file was changed).
**Checklist Applied**: IR-1..IR-7 (IR-5 per-test grading), DR-1..DR-8.

---

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| 1 | Medium | yes | behavior | **Editor keystrokes act on the overlay while the confirm strip is open (violates AC-57.7; `COMPOSITION_LOCK` "same enablement").** The strip is rendered inside `capture-viewport` (`CaptureViewport.tsx:724`) and AC-57.7's focus rule moves focus to its Cancel button (`CapturePage.tsx:427-432`). The window key handler's guard `annotationOwnsFocus()` (`:91-102`) treats any focused element inside the viewport that is not in `COLOR_FOCUS_IDS` as "the editor owns focus", so with the strip open: `Delete` removes the selected mark (`:882-886`) and `ArrowLeft/Right/Up/Down` nudge it (`:887-906`) — while the prompt "Discard unsaved overlay marks on this shot?" / "Delete this capture…" is still showing. Reproduced (PROBE-A, unchanged HEAD page): open a dirty confirm after drawing one arrow → `activeElement = capture-dirty-confirm-cancel`; `ArrowRight` → `x1` 1→2; `Delete` → arrow count 1→0; strip still open; 0 `DELETE` requests. The same sequence on the pre-change page (`1f9b035`, portal in `document.body`, focus left on the filmstrip item) leaves `x1 = 1` and the arrow count at 1. On the delete-capture strip the shot may be clean but a saved mark can still be selected, so `Delete` there silently dirties the overlay behind the "Delete capture" prompt. The shipped tests (`capture-page.behavior.test.ts:1107,1123`; Electron `capture-inbox.test.ts:742`) exercise clicks only, so this path is untested. | `ui/src/renderer/src/features/capture/CapturePage.tsx:91-102` (guard), `:427-432` (focus), `:882-906` (keys); `ui/src/renderer/src/features/capture/CaptureViewport.tsx:724` (strip placement) | Make the confirmation inert to editor keys: in `annotationOwnsFocus()` return `false` when `active.closest('[data-testid="capture-confirm-strip"]')` is non-null (or short-circuit `handleEditorKey` while `confirm !== null`). Add a unit regression beside `:1123`: draw a mark, open the dirty strip, assert focus is on Cancel, dispatch `keydown Delete` and `ArrowRight` on the focused element, assert the mark count and `x1` are unchanged and the strip is still open; optionally add the same keystrokes to the AC-57.10 strip spec. Because this touches `ui/`, rerun `green57`, `gate57`, `pregate` and `WINDOWS_GATE` before Round 2 (task H1-7 rule). | open |
| 2 | Low | no | behavior | **Rail click lock drops observer updates and never reconciles them (AC-58.3 edge, non-blocking).** `activate()` sets `clickLockUntil = now + 800` (`SettingsRail.tsx:133`); observer callbacks inside the window record `visible` but return before `setActive` (`:86-88`), and nothing re-evaluates `visible` when the lock expires. Reproduced (PROBE-C, fake observer + mocked `Date.now`): click Download, then an observer report of MCP at +300 ms → current stays `settings-rail-download`; at +5300 ms with no new crossing → still `download`; only the next crossing corrects it. In the product this is a user who clicks an entry then wheels within 0.8 s and stops: the highlight stays on the clicked entry until a section next crosses the band. The Electron spec `settings.test.ts:221` (click MCP → `scrollTo(top)` → expect Download current) passes only because Playwright's `toBeInViewport` polling schedule lands the instant scroll after the lock; it passed 4/4 here (8.0–24.1 s each) and 110/0/0 on Windows, so no flake is claimed. | `ui/src/renderer/src/features/settings/SettingsRail.tsx:86-88`, `:133` | On lock expiry (a `setTimeout` armed in `activate`, cleared on unmount) recompute `chosen` from the retained `visible` map with the same bottom rule and `setActive` it. Outside this loop unless Round 2 is needed for Finding 1 anyway. | open |
| 3 | Low | no | behavior | **Cookie-mode group lost its readable accessible name.** The base page named the radio group with `<legend>Cookie mode</legend>` (`1f9b035:SettingsPage.tsx:252`); the recomposition renders `SegmentedControl`, whose fieldset takes `aria-label={name}` = `"cookie_mode"` (`SegmentedControl.tsx:29`), and the visible "Cookie mode" text is an unassociated `<span>` (`SettingsPage.tsx:492`). Screen readers now announce the group as "cookie_mode". Not an AC requirement (AC-58.6 covers radio semantics, IDs, one PUT and sub-field visibility), so non-blocking; recorded as a real a11y regression with a one-line fix. | `ui/src/renderer/src/features/settings/SettingsPage.tsx:491-507`; `ui/src/renderer/src/components/ui/SegmentedControl.tsx:29` | Give the primitive an additive `label`/`aria-label` prop (the `PathRow readOnly` precedent) and pass "Cookie mode", or wrap the segment in a `fieldset`/`legend` on the page. Unit-check `getByRole('group', { name: 'Cookie mode' })`. | open |
| 4 | Low | no | test-rigor | **AC-58.6 passes unchanged on the pre-change page.** Running HEAD's `settings-rail.test.tsx` against the `1f9b035` `SettingsPage.tsx` (with HEAD's `settings-sections.ts`/`SettingsRail.tsx` dropped in so the file collects) fails 14 of 18 cases as expected, but `AC-58.6 cookie mode is a native-radio segment…` passes: the old `<fieldset>` with native radios, the same IDs, one `{cookie_mode}` PUT and the same sub-field rule already satisfied every assertion. The ST1 *adoption* is pinned only by the TM-1 source check (`layout-primitives.test.ts:237-242`). 🟡 by IR-5 — it is an honest invariant test (it would catch a regression of ST1's "preserve radio semantics and IDs"), so `Low`, not `Medium`. The Red oracle's `--new-file` acceptance means this was not visible to the author (the whole file failed to collect). | `ui/tests/unit/settings-rail.test.tsx:351-368` | Add one assertion that discriminates the segment: each radio's `<label htmlFor>` equals the radio id (the primitive's contract) or the group has the segment container class; keep the existing invariants. | open |

> `Blocking` is not `Severity`. Finding 1 is `Blocking: yes` under the dispatch instruction (see Review binding). Findings 2–4 never block.

### Out-of-Contract Observations (non-blocking, ≤ 5)

1. After Cancel or Confirm on the strip, focus lands on `body` (PROBE-A: `focusedAfterCancel = BODY` on HEAD **and** on the base portal). APG alert-dialog guidance returns focus to the invoker (the filmstrip item or `capture-delete`); AC-57.7 only requires the opening focus, so this is not a finding. Worth folding into the Finding 1 correction if the strip is touched.
2. Filmstrip item accessible name doubles the full name (`img alt={label.full}` plus the sr-only span, `CaptureFilmstrip.tsx:97-104`), and the dirty dot's `aria-label="Unsaved marks"` on a plain `<span>` is not announced by most readers. Cosmetic.
3. `validate-task.sh doc-tests` (A10-R) compares container failures of `test_framework_adoption.py` at HEAD against a `7613beb` worktree; while HEAD's file is byte-identical to `7613beb` the comparison is tautological. `WINDOWS_GATE` ran the file at 91/91 with zero tolerance, so nothing is hidden; noted per Materiality Gate #5.
4. The AC-57.10 header spec (`capture-inbox.test.ts:682-689`) branches on the live `getHotkeyStatus().registered`; in a gate environment where F2 is held by another app the keycap-present branch never executes. Both branches are asserted (no silent early return) and the unit tests cover both states explicitly, so 🟡 not 🔴.
5. Save overlay, Open file/folder and Delete now sit inside the viewport chrome and therefore inside the same editor key scope as the pre-existing toolbar buttons (`Delete` while `capture-delete` is focused removes the selected mark). This is consistent with the existing toolbar semantic and the mockup's placement; if Finding 1 is fixed by scoping, decide deliberately whether the action group should be excluded too.

---

## Verification record

### AC coverage (AC-57.1–57.10, AC-58.1–58.13)

| AC | Production entrypoint verified | Test that would fail on regression | Result |
|---|---|---|---|
| AC-57.1 | `CapturePage.tsx:1098-1101` (`w-full max-w-[var(--layout-page-max-width)]`, `styles.css:70`), `:1103-1199` header (Capture region primary md, "n shots · inbox {path}" `:1021,1124-1126`, `Disclosure` closed `:197,1127-1134`), `PathRow` `:1136-1155`, recorder unchanged `:1156-1182`, `capture-page-save` primary sm with `settings.saveClass` `:1183-1196`, same `settings.save()` | `capture-page.behavior.test.ts:957` (cap class, order, `aria-expanded`, hidden panel, zero PUT until Save then exactly one with the same body shape); Electron `capture-inbox.test.ts:675` (renderer fetch ledger) | pass |
| AC-57.2 | `:420-425` one `getHotkeyStatus` per hotkey value, `registered && accelerator` gate; `<kbd>` inside `capture-region` `:1115-1122` | `:989` (text, containment, name starts "Capture region", one call), `:1002` (`registered:false` → no keycap); Electron `:675` | pass |
| AC-57.3 | `:938` template byte-identical; `:1200-1207` `<p min-h-4>` with `StatusChip` warning + sentence only when `inUse` | `:1002` (chip text "Hotkey", sentence), `:1014` (empty mounted banner; Red-by-design, disclosed) | pass |
| AC-57.4 | `CaptureFilmstrip.tsx:21-40` (aside `w-[12.5rem]` at `CapturePage.tsx:1209`, `max-h-[26rem]`, `aria-label="Captures"`), rows `:80-104` (native button, 56×36 thumb, `aria-current`, `data-dirty`, sr-only full name, no listbox role); `capture-filmstrip-label.ts:26-34` | `capture-filmstrip-label.test.ts:12-35` (space/underscore prefixes, no-prefix, prefix-only fallback, local `HH:MM:SS`, invalid date); `capture-page.behavior.test.ts:1023`; Electron `:707` (190–210 px aside) | pass |
| AC-57.5 | `CaptureViewport.tsx:423-425` `shrink-0`/`flex-nowrap` kept; tool segment `:426-482` sm, `aria-pressed`, `disabled={!hasSelection}` + `title` (`hasSelection={selectedId !== null}` `CapturePage.tsx:1225`); labelled Color group `:508-561`, Stroke label `:606-619`; action slot `:720-721`; page-owned actions `CapturePage.tsx:1025-1095` with the unchanged enablement (`selected === null`, `selected === null && inbox_dir.length < 1`, `selectedId === null || confirm !== null`) | `:1044` (h-7 segment, aria-pressed swap, labels, actions inside chrome), `:1064` (no shot: disabled + hint, click cannot press, W9-5 table), `:342` (AC-39.28 under TM-10), `:939` chrome classes; Electron `:727`, W9-3/W9-5 | pass |
| AC-57.6 | `:228-241` `dirty`/`canSave` unchanged; `:1027-1056` mounted iff `dirty`, `disabled={!canSave}`, "Save overlay •", one `saveAnnotations()`; palette seam `:243-248` unchanged | `:1078` (absent → mounted → one POST → unmounted), `:1095` (non-empty draft mounts disabled); AC-60.10 `:668,690` palette refusal unchanged; Electron `:742` | pass |
| AC-57.7 | `:427-432` focus Cancel on open; `:942-1001` strip (same messages/IDs, `role="group" aria-labelledby`, "Delete capture" destructive), `createPortal` import removed; `CONFIRM_EXCLUSIVITY` via `locked={confirm !== null}` (`CaptureFilmstrip.tsx:90-91`) and `capture-delete` `:1087` | `:1107` (inline, above surface, Cancel focused, zero DELETE), `:1123` (filmstrip/Delete disabled, second click changes nothing, no fixed portal); Electron `:742` (`toBeFocused`, disabled item, zero DELETE) | **partial** — click paths proven; keyboard path fails (Finding 1) |
| AC-57.8 | `:1010-1018` error-first status rule unchanged; `:1237-1242` `capture-status h-5` + separate `capture-shot-info` (`:1022`) | `:1141` (error in status, never in shot info; status after surface); Electron `:742` | pass |
| AC-57.9 | `:1229-1236` `capture-empty` rendered in the page (`CAPTURE_SOURCE_LOCATION`), placed by `CaptureViewport.tsx:725-729` replacing the surface; "Select a shot from the filmstrip." kept `:728` | `:1154` (inside viewport, surface absent, empty shot info), `:1165` (absent with shots); Electron `:727`; source pins `capture-page.test.ts` AC-39.13 pass | pass |
| AC-57.10 | — | `capture-inbox.test.ts:675,707,727,742`; W9-1..W9-7, AC-59.12, AC-60.12 active; no `.skip/.only/.todo` under `ui/tests` | pass (Windows 110 expected / 0 unexpected / 0 flaky) |
| AC-58.1 | `SettingsPage.tsx:409-417` (`grid w-full max-w-[60rem] gap-5 min-[1000px]:grid-cols-[11rem_minmax(0,1fr)]`, rail first, content column h1 → HelpCard → `role=alert` → sections); all 11 `SETTINGS_SECTION_SET` IDs via `SettingsSectionFrame` `:89-95` | `settings-rail.test.tsx:191` (classes, no `max-w-3xl`, rail precedes h1, every section ID); `settings-page.test.ts:487`; Electron `settings.test.ts:221` (rail right edge ≤ heading x), `:275` (900 px window → rail above heading, < 120 px tall) | pass |
| AC-58.2 | `SettingsRail.tsx:134-185` (`<nav>`, three labelled groups, native buttons in set order), `activate` `:121-131` → `revealSection` `:44-67` (focus, smooth unless reduced motion, 450 ms unmoved fallback); startup entry via `onAvailabilityChange` (`StartAtSignInControl.tsx:29-31,55-57`; `SettingsPage.tsx:219,350,921`), no new IPC | `:205` (NAV, groups, no startup entry/panel unpackaged), `:218` (supported → entry + panel + caption), `:230` (click/Enter → scrollIntoView + focus, zero writes, one current); Electron `:221` | pass |
| AC-58.3 | `:78-118` observer rooted at the nearest scroller (`AppShell.tsx:272-273` `<main overflow-auto>`), `-60%` band, bottom rule, disconnect on cleanup; jsdom fallback `:80-82` | `:230` (fallback, no throw, first section current), `:257` (fake observer drives current, exactly one, disconnected on unmount); Electron `:221` (scroll → observer-driven current) | pass (Finding 2 edge is post-click only) |
| AC-58.4 | `settings-sections.ts:52-57` captions; `SettingsPage.tsx:86-102` one caption per section, none for `none`; persistence unchanged (`schedulePut`/`putNow`/hooks, see COMPOSITION_LOCK below) | `:156` (`SAVE_MODE_CAPTIONS` exact), `:289` (captions per key, none for deps/mcp, Convert zero PUT until Save then one, theme one immediate PUT); Electron `:250` | pass |
| AC-58.5 | `FormRow.tsx` 10.5 rem grid (unchanged); `GridSelect` `:111-145` (one label via `htmlFor`), `NumberRow` `:179-208` (84 px, hints only from `NUMBER_HINT_SOURCES`, no new min/max/step — identical `type="number"`/`Number()` pattern to base `:370-459`), `PathRow readOnly` for the five browse-only paths `:433-442,481-490,574-583,613-622,665-674`; Convert/Capture paths editable `:715-733,784-802`; `PathRow.tsx:14-15,41-46` | `:165` (one label per leaf via `getAllByLabelText`, browse in the same row, readOnly matrix, hint/no-hint, no min/max on numbers, speed 0.5/2/0.1), `:315`; `layout-primitives.test.ts:171` (readOnly ignores typing, Browse fires once); Electron `:250` (field/Browse y-overlap) | pass |
| AC-58.6 | `:491-507` `SegmentedControl` native radios with `settings-leaf-cookie_mode-{none,browser,file}`, group ID on the fieldset; `cookieBrowserVisible`/`cookieFileVisible` unchanged `:508-550` | `:351` (fieldset, radio type, label click → one `{cookie_mode}` PUT, sub-field visibility) — passes on the base page too (Finding 4); adoption pinned by TM-1 `layout-primitives.test.ts:237-242` | pass (see Finding 3 for the group name) |
| AC-58.7 | `CheckboxRow` `:147-177` hint from `CHECKBOX_COPY_SOURCES` only; `audio_format` never disabled `:462-479` | `:165`, `:370` (every listed copy via `aria-describedby`; none for skip_existing/close_to_tray/audio_only; audio_format enabled with audio_only off) | pass |
| AC-58.8 | `:697-713`, `:766-782` footers primary sm, "Save Changes •"/`btn-save-dirty`/`opacity-50`, same `converter.save()`/`capture.save()`; dots `:351-355` → `SettingsRail.tsx:170-177` | `:384` (h-7, label/class swap, dots appear per draft and clear after Save); Electron `:250` (dot, class, one PUT); AC-33.16/AC-39.15 source pins pass | pass |
| AC-58.9 | `checkChip` `:65-69` (undefined → "checking"), `readinessCount` `settings-sections.ts:81-91`, rows `:358-406` (Fix links keep their rules), count caption `:954-964`, dot `:354`, deps chips `:923-952`, MCP chip `:982-996` with `MCP_TOKEN_TEXT` | `:182` (null until both load, counts), `:404` (pre-load: no count/dot/warning chip, "checking"), `:415` (3 of 4, dot, chips, Fix only on failing rows, versions/paths, token text/tone, no token value), `:438` (4 of 4, no dot); Electron `:275`; AC-23.11/23.12 unchanged | pass |
| AC-58.10 | `StartAtSignInControl.tsx:77-115` panel/checkbox IDs, visibility and IPC unchanged; only the prop, `data-settings-section` and caption header added | `settings-page.test.ts` AC-61.12/13/14/16/20 untouched (diff is additive at `:486-513`); Electron AC-61.17 | pass |
| AC-58.11 | no subfolder under `features/settings`; Convert/Capture strings in `SettingsPage.tsx`; `test-ids.ts:343-377` additive after the MEU-56 block | `settings-page.test.ts:497`; AC-51.6 (Windows pass; container CRLF-hash env-bound with the replicated proof) | pass |
| AC-58.12 | — | `settings.test.ts:221,250,275`; W4-1..W4-3 and AC-61.17 unchanged (seam gained two additive GETs `:79-85`) | pass (Windows) |
| AC-58.13 | `:425-431` Apply defaults ghost sm footer, same POST; `:846-879` one `settings-log-row` with checkbox, mono path, Copy and the fixed-path hint; `:892-919` theme segment with `aria-pressed`, same `putNow('ui', …)` | `:449` (ghost/h-7, one POST, row containment, `logs/console.log`, exactly one `aria-pressed="true"`); AC-23.3/23.8/23.9 unchanged | pass |

### COMPOSITION_LOCK (old vs. new via `git show 1f9b035:<path>`)

- **Capture**: `PUT /settings/capture` only through `settings.save()` (same hook, same body); `POST …/annotate` only through `saveAnnotations()` behind the unchanged `canSave` (`:231-241`) and the unchanged `canSaveRef`/`setCaptureSaveAllowed` seam; `DELETE` only from `acceptConfirm` (`:959-965`, the former portal handler verbatim); `getHotkeyStatus` still one call per hotkey value (`:420-425`, now also reads `registered`); `showDirectoryDialog`, `captureRegion`, `openPath`/`showItemInFolder` unchanged; Open file / Open folder / Delete enablement strings identical to base `:1063-1091`; tools' `disabled` is the approved OQ-2/CP5 change; every ID in `capture-page.test.ts` `WAVE9_TESTIDS`/`WAVE9_EXTRA_TESTIDS` still present (31/31 source-contract tests pass). Confirm-strip keyboard scope: **regressed** (Finding 1).
- **Settings**: autosave leaves still go through `schedulePut` (300 ms, strict schema, empty-string filter) and Browse through `putNow` (`:272-330`); Convert/Capture stay on their explicit-save drafts; theme through `putNow('ui', …)`; `apply-defaults` POST without body; `copyMcpConfig({pinEndpoint})`; `loginItemGet/Set` untouched; no new `min`/`max`/`step` (only the pre-existing speed range); number rows keep the base `type="number"` + `Number(event.target.value)` mutation. `packages/` diff is exactly A8 (`git diff 1f9b035 HEAD --name-only -- packages mcp-server` → `routes/captures.py` only); `openapi --check` exit 0 on Windows.
- **Test IDs**: `test-ids.ts` diff is purely additive after the MEU-56 block; AC-51.6 passed on Windows (671/671); every pre-existing ID string still appears in the sources (`grep` census in `capture-page.test.ts`/`settings-page.test.ts`/`gui-actions-audit.test.ts` all green).

### TEST_MIGRATIONS discipline (pre-existing tests changed since `1f9b035`)

`git diff 1f9b035 HEAD --name-only -- ui/tests` lists exactly: `capture-inbox.test.ts` (TM-2 `:217-218,322-323`, TM-3 `:232-235`, TM-4 `:223`, TM-7 `:414-416,459-461,522-524`, plus the additive AC-57.10 wave and ledger helpers), `capture-page.behavior.test.ts` (TM-5 `:271-276`, TM-6 `:466,678,697`, TM-8 `:441-448`, TM-9 `:662-664`, TM-10 `:349`, TM-11 `:395-397`, the disclosed `catalogItems` fixture seam `:149,176,233`, and the additive AC-57 block `:950-1168`), `layout-primitives.test.ts` (TM-1 `:237-246` + additive AC-58.5 `:171-186`), `settings-page.test.ts` (additive `:486-513`), `settings.test.ts` (additive seam GETs `:79-85` + AC-58.12 wave), `test-ids.ts` (additive), and the two new files. TM-12 was not applied (AC-39.28 passes unchanged, verified by the base-page probe: it fails there only for TM-10's `h-7`). `capture-picker.test.ts` is unchanged. No `.skip/.only/.todo` under `ui/tests` (0 hits). Every other diff hunk in a pre-existing test is additive or a setup step; no assertion outside TM-1..TM-11 was weakened.

**A11 / A11-W (`tests/tooling/test_framework_adoption.py`, `4047bfc`→`7613beb`)**: programmatic comparison — `def test_*` names identical (31), `parametrize(...)` lists identical (20), every `assert` line identical (59/59), marks unchanged (`parametrize` only), no `skip`/`xfail` added, the set of expected `REFUSE…` strings unchanged. The refusal assertions check specific reason substrings (`"drift"`, `"source"`, `"path"`, `"allow"`, `"stale"`, `"AC-2"`, …), so a case cannot pass on a generic non-zero exit; the fixture's throwaway repo plus per-`source_path` files means the static negatives now reach their own rule rather than the source check (A11-W's stated side effect), which is a strengthening. Windows ran the file at 91/91 inside `py-tests` with zero tolerance.

### Accessibility

- Capture: `capture-region` name "Capture region F2" (kbd inside the button); Disclosure `aria-expanded`/`aria-controls` with a `hidden` panel; PathRow label via `htmlFor`; hotkey input wrapped in `<label>`; banner chip + text; filmstrip buttons `aria-current="true"`, full name in `alt` + sr-only; tool segment `role="group"` with `aria-pressed`; Color `role="group"` (the `capture-color` text input itself still has no accessible name — pre-existing); Stroke wrapped in `<label>`; strip `role="group" aria-labelledby` and opening focus on Cancel (verified in jsdom and Electron). Post-close focus → `body` (observation 1). Keyboard scope leak → Finding 1.
- Settings: one label per control through `FormRow`; `aria-describedby` for hints; `aria-current="location"` exactly one; rail entries are native buttons (Enter/Space); sections `tabIndex={-1}` focus targets; theme `aria-pressed`; cookie group name regressed (Finding 3).

### Layout at narrow widths

- Capture: header `flex-wrap`, viewport `min-w-0` (the handoff's overflow fix), both chrome rows `overflow-x-auto`, filmstrip `w-[12.5rem] shrink-0`; the disclosure's PathRow is a fixed `w-[24rem]` (fine at Electron's window sizes). The `sm:grid-cols-[3.25rem_minmax(0,1fr)]!` important-suffix is valid Tailwind v4.3.3 and is present in the built CSS (`ui/out/renderer/assets/index-*.css`: `3.25rem minmax(0, 1fr) !important`).
- Settings: single column below a 1000 px viewport with the rail as a horizontal scrolling row (Electron `:275` proves rail-above-heading and < 120 px height at 900 px); ≥ 1000 px the rail is `sticky top-4 self-start` in a grid whose row spans the content column, so it sticks inside `<main>` (Electron `:221` proves `rail toBeInViewport` after scrolling to MCP).

### IR-5 test-rigor grading

| Test | Rating |
|---|---|
| `capture-filmstrip-label.test.ts` ×5 | 🟢 (both separators, no-prefix, prefix-only fallback, invalid date) |
| `capture-page.behavior.test.ts` AC-57.1, 57.2 ×2, 57.4, 57.5 ×2, 57.6 ×2, 57.7 ×2, 57.8, 57.9 ×2 | 🟢 (exact IDs, request counts/bodies, focus target, disabled states, negative paths); all 14 fail on the base page except AC-57.3 `:1014` (Red-by-design, disclosed) |
| `capture-page.behavior.test.ts:1107,1123` strip | 🟡 — clicks proven; keyboard path unexercised (Finding 1) |
| TM-5..TM-11 edits | none weakened; each keeps its other assertions (verified hunk by hunk) |
| `settings-rail.test.tsx` table tests ×4 | 🟢 (exact tables; pure data) |
| `settings-rail.test.tsx` page tests ×14 | 🟢 for 13 (13/14 fail on the base page); `:351` AC-58.6 🟡 (Finding 4) |
| `settings-page.test.ts:487,497`, `layout-primitives.test.ts:171` | 🟢 (Red-verified in the receipts; `:497` pins the file layout and post-marker IDs) |
| Electron AC-57.10 ×4, AC-58.12 ×3 | 🟢 for 6; AC-57.10 header `:675` 🟡 (live-status branch, observation 4); AC-58.12 `:275` count/dot are data-driven but both branches asserted 🟡 |

No 🔴 test in scope.

### Correctness edge cases probed (scratchpad probes against the unchanged code)

| Probe | Result |
|---|---|
| PROBE-A (HEAD) dirty strip open, focus on Cancel, `ArrowRight` then `Delete` | `x1` 1→2, arrows 1→0, strip still open, 0 DELETE → **Finding 1** |
| PROBE-A (base `1f9b035`) same sequence | focus stays on the filmstrip item, `x1` 1, arrows 1 → old portal was inert |
| PROBE-A focus after Cancel | `BODY` on both HEAD and base (observation 1) |
| PROBE-B HEAD `settings-rail.test.tsx` on the base page | 14/18 fail, 4 table tests pass, `AC-58.6` passes → **Finding 4** |
| PROBE-B HEAD `capture-page.behavior.test.ts` on the base capture sources | every AC-57 case fails except `:1014`; TM-5..TM-11 sites and the CP1 cases fail as expected (Save was mounted on clean shots) |
| PROBE-C rail observer report inside the click lock, then lock expiry with no crossing | current stays on the clicked entry until the next crossing → **Finding 2** |
| Electron `settings.test.ts:221` ×4 (`--repeat-each 4`, xvfb) | 4 passed, 0 flaky (24.1 s, 8.1 s, 8.0 s, 8.1 s) |
| Tailwind `!` suffix on the Capture PathRow | present as `!important` in the built CSS |

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| IR-1 live runtime evidence | pass | `RECEIPTS_DIR=<scratch> bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh windows-gate-check` | 0 | `PASS windows gate @ 7613beb1…: vitest {'passed': 671, 'failed': 0, 'total': 671} e2e {'expected': 110, 'unexpected': 0, 'skipped': 0, 'flaky': 0}`; all 17 stages exit 0 in order, `clean_tree: true`, lockfile `A86D9A42…2980`, Electron 42.9.3, Node v24.19.0; `git diff 7613beb HEAD --stat -- ui packages mcp-server tests` empty |
| IR-2 stub behavioral compliance | pass | PROBE-A/C fetch and IPC stubs; the behavior/rail suites' seams | 0 | ledgers count exact PUT/POST/DELETE; `catalogItems` and the Electron seam GETs are additive setup |
| IR-3 error mapping | pass | `git diff 1f9b035 HEAD -- packages/api/src/avkit_api/routes/captures.py` | 0 | A8 is `model_validate` over the same dict, same discriminated-union validation; no route added; OpenAPI `--check` exit 0 (Windows stage `openapi`) |
| IR-4 fix generalization | partial | reading `annotationOwnsFocus()` vs the new in-viewport slots | — | the guard was not revisited when the strip and the action group moved into the viewport (Finding 1, observation 5) |
| IR-5 test rigor | pass | table above; PROBE-B | 1 | no 🔴; two 🟡 with reasons |
| IR-6 boundary validation | pass | `git show 1f9b035:…` vs HEAD for both pages and hooks | 0 | no new write surface; payloads, schemas and debounce unchanged; `git diff 1f9b035 HEAD --name-only -- packages mcp-server` → only the A8 file |
| IR-7 deferral & AC coverage | pass | handoff AC tables vs plan; `Deferred Items: None` in both | — | every AC-57.x/58.x present with file:line that resolves (spot-checked `:957,989,1002,1023,1044,1064,1078,1095,1107,1123,1141,1154,1165`; `:140,156,165,182,191,205,218,230,257,289,315,351,370,384,404,415,438,449`; Electron `:675,707,727,742`, `:221,250,275`); Out-of-Scope rows carry a Basis; every integration AC has an Electron case |

### Design Review (DR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| Naming convention followed | pass | `ls .agent/context/handoffs/ \| grep p11-capture-settings` | 0 | `-MEU-57-handoff.md`, `-MEU-58-handoff.md`, `-plan-critical-review.md`; this file is the canonical `-implementation-critical-review.md` |
| Template version present | pass | `grep -c 'template_version: "2.2"'` both handoffs | 0 | `1` each |
| DR-1 claim-to-state | pass | test line refs re-derived with `grep -n "^  it('AC-5[78]"` / `^test('AC-5[78]` | 0 | every cited line resolves to the named test; "TM-12 not applied" and "conditional TM-4 not needed" match the diff |
| DR-2 residual old terms | pass | `grep -rn createPortal ui/src/renderer/src/features/capture` | 1 | 0 hits; `max-w-3xl` absent from `SettingsPage.tsx` |
| DR-7 evidence freshness | pass | `npm --prefix ui run test -- --run <12 in-scope files>` | 1 | `Tests 1 failed \| 246 passed (247)`: the only failure is AC-51.6 (CRLF hash `DCABD0F9…` vs `819760B9…`), the tolerated `ENV_BOUND_TESTS` case |
| DR-8 completion vs residual risk | partial | handoff AC-57.7 rows say ✅ | — | the keyboard path is a residual gap the row does not disclose (Finding 1) |
| SSOT / task state | pass | `git diff 1f9b035 HEAD -- .agent/context/meu-status.yaml …`; `task.md` | 0 | MEU-57 (`:1612`) / MEU-58 (`:1637`) `ready_for_review`, `execution_plan` bound to this folder, registry/hub rendered (`render --check` exit 0 on Windows); grouping row 26 `in review`; focus records `ready_for_review`; rows 1–8 and H1-1..H1-6 `[x]` with the resolved B-H1-6 block; H1-7, H2-1..H2-3 `[ ]` by design |

### Post-Implementation Review (PR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| Evidence bundle complete | pass | `grep -c 'evidence.v1'` both handoffs + walkthrough | 0 | red/gate blocks in both handoffs; pregate and prereq blocks in the walkthrough; Windows result JSON committed |
| FAIL_TO_PASS table present | pass | `grep -c '### FAIL_TO_PASS'` | 0 | `1` each; Red-by-design rows disclosed |
| Commands independently runnable | pass | `windows-gate-check`, targeted Vitest, one Electron spec ×4 rerun by the reviewer | 0/1/0 | outputs above |
| Anti-placeholder scan clean | pass | Windows `source-audit` stage (rg exit 1 → 0 hits); `rg -n '\.(skip\|only\|todo)\(' ui/tests` | 1 | no hits |
| Harness integrity (A1–A11-W, A10-R) | pass | read `validate-task.sh` / `.ps1` / `plan_checks.py` | — | `windows-gate-check` binds stage order, exits, floors (631/103), tested commit identity and a clean code tree; `vitest_env_ok`/`electron_env_ok` tolerate only the three proof-signatured env cases and only off Windows; the Red oracle refuses collection errors except a declared new file with a missing-module message (self-test 26 cases). No amendment hides a defect: A9 moves `py-tests` to the authoritative host where it passed; A10-R is tautological today (observation 3) but Windows ran the file at zero tolerance |

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r1-windows-gate-check","command":"RECEIPTS_DIR=<scratchpad>/review-r1/receipts bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh windows-gate-check; git diff 7613beb HEAD --stat -- ui packages mcp-server tests","cwd":"/home/user/av-kit","scope":"authoritative D6 gate identity (WINDOWS_GATE attempt 2)","phase":"full-gate verification","exit_code":0,"result":"pass","tested_state":"HEAD e514443; code-identical to 7613beb","output":"PASS windows gate @ 7613beb1c7c5b3a48c07b8ace2fe189d9ff960e2: vitest {'passed': 671, 'failed': 0, 'total': 671} e2e {'expected': 110, 'unexpected': 0, 'skipped': 0, 'flaky': 0} | diff --stat empty","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r1-targeted-vitest","command":"npm --prefix ui run test -- --run tests/unit/capture-page.behavior.test.ts tests/unit/capture-filmstrip-label.test.ts tests/unit/capture-page.test.ts tests/unit/settings-page.test.ts tests/unit/settings-rail.test.tsx tests/unit/layout-primitives.test.ts tests/unit/gui-actions-audit.test.ts tests/unit/layout-canon.test.ts tests/unit/convert-page.test.ts tests/unit/capture-interactive.test.ts tests/unit/capture-lifecycle.test.ts tests/unit/chrome-zorivest.test.ts","cwd":"/home/user/av-kit","scope":"in-scope unit suites at HEAD","phase":"targeted","exit_code":1,"result":"pass (only ENV_BOUND_TESTS failed)","tested_state":"HEAD e514443","output":"Test Files 1 failed | 11 passed (12); Tests 1 failed | 246 passed (247): AC-51.6 CRLF hash DCABD0F9… vs 819760B9… (tolerated env-bound)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r1-probe-a-confirm-keys","command":"vitest run --config <scratchpad>/review-r1/probe/vitest.probe.config.ts confirm-keys-head.probe.test.ts confirm-keys-base.probe.test.ts (draw one arrow, click the other filmstrip item, then dispatch keydown ArrowRight/keyup and keydown Delete on document.activeElement)","cwd":"<scratchpad>/review-r1/probe (HEAD probe imports /home/user/av-kit/ui/src unchanged; base probe imports a git-archive of 1f9b035 ui/src)","scope":"AC-57.7 confirm strip under keyboard input","phase":"targeted","exit_code":0,"result":"fail (defect reproduced on HEAD; base inert)","tested_state":"HEAD e514443 vs base 1f9b035","output":"HEAD: focusedAtOpen=BUTTON[capture-dirty-confirm-cancel] x1Before=1 x1AfterArrow=2 arrowsAfterDelete=0 stripStillOpen=true focusedAfterCancel=BODY deletes=0 | BASE: focusedAtOpen=BUTTON[capture-filmstrip-item] x1Before=1 x1AfterArrow=1 arrowsAfterDelete=1 stripStillOpen=true focusedAfterCancel=BODY deletes=0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r1-probe-b-discrimination","command":"git archive 1f9b035 ui/src ui/tests ui/package.json ui/vitest.config.ts ui/tsconfig.json | tar -x -C <scratchpad>/review-r1/base; cp HEAD settings-sections.ts SettingsRail.tsx into the base settings folder; cp HEAD tests/unit/settings-rail.test.tsx and capture-page.behavior.test.ts (as .head.test.ts); vitest run --allowOnly=false <both files>","cwd":"<scratchpad>/review-r1/base/ui (node_modules symlinked)","scope":"do the new AC-57/AC-58 tests fail on the pre-change pages?","phase":"targeted","exit_code":1,"result":"pass (expected Red reproduced, one vacuous case found)","tested_state":"base pages 1f9b035; tests from HEAD e514443","output":"Tests 59 failed | 9 passed (68). settings-rail: 4 table tests pass, AC-58.6 passes (Finding 4), 13 page tests fail. capture behavior: every AC-57 case fails except AC-57.3 :1014 (Red-by-design); TM sites fail as expected","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r1-probe-c-rail-lock","command":"vitest run --config <scratchpad>/review-r1/probe/vitest.probe.config.ts rail-lock.probe.test.ts (fake IntersectionObserver; Date.now mocked; click Download, report MCP at +300 ms, advance to +5300 ms with no report, then report MCP again)","cwd":"<scratchpad>/review-r1/probe (imports /home/user/av-kit/ui/src unchanged)","scope":"AC-58.3 scroll-spy after a click","phase":"targeted","exit_code":0,"result":"observed (non-blocking)","tested_state":"HEAD e514443","output":"PROBE-C duringLock=settings-rail-download afterLockNoEvent=settings-rail-download afterNextEvent=settings-rail-mcp","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r1-e2e-rail-repeat","command":"ELECTRON_DISABLE_SANDBOX=1 xvfb-run -a npm --prefix ui run test:e2e -- tests/e2e/settings.test.ts -g 'AC-58.12 rail groups' --repeat-each 4 --reporter=json --outputFile=<scratchpad>/review-r1/receipts/r1-e2e-rail-repeat.json (env -u ELECTRON_RUN_AS_NODE AVKIT_E2E_OUT_DIR)","cwd":"/home/user/av-kit","scope":"timing sensitivity of the click-then-scroll rail spec (Finding 2)","phase":"runtime","exit_code":0,"result":"pass","tested_state":"HEAD e514443 (ui/out built 2026-09-29 04:14 from the code-identical 4c904ef)","output":"4 passed (51.6s): 24.1s, 8.1s, 8.0s, 8.1s; stats expected 4, unexpected 0, flaky 0","fresh":true}
```

---

## Commands run (reviewer)

- `git log --oneline 0f51036..HEAD`; `git diff 1f9b035 HEAD --stat`; `git diff 7613beb HEAD --stat -- ui packages mcp-server tests` (empty); `git diff 1f9b035 HEAD --name-only -- ui/tests packages mcp-server`
- `git diff 1f9b035 HEAD -- <capture sources> <settings sources> <tests>`; `git show 1f9b035:<SettingsPage.tsx|CapturePage.tsx|StartAtSignInControl.tsx>`
- `git diff 4047bfc 7613beb -- tests/tooling/test_framework_adoption.py` + a Python comparison of `def test_*`, `parametrize(...)`, `assert` lines, marks and `REFUSE` strings
- `bash …/validate-task.sh windows-gate-check` (RECEIPTS_DIR in the scratchpad); read `windows-gate-result.json`, `validate-task.sh`, `validate-task.ps1`, `plan_checks.py`
- `npm --prefix ui run test -- --run <12 in-scope files>`
- PROBE-A/B/C as recorded above; `xvfb-run -a npm --prefix ui run test:e2e -- tests/e2e/settings.test.ts -g "AC-58.12 rail groups" --repeat-each 4`
- `node -p require('tailwindcss/package.json').version` (4.3.3); grep of `ui/out/renderer/assets/index-*.css` for the important-suffix rule
- `rg`/`grep` sweeps: `createPortal`, `.skip/.only/.todo`, `<legend>`, `aria-label={name}`, `annotationOwnsFocus`, `--layout-page-max-width`, `format_iso`
- `python .agent/skills/timestamp/scripts/stamp.py` (timestamp below)

---

## Verdict

`changes_required` — Finding 1 is an evidence-backed runtime defect on the surface AC-57.7 defines: the inline confirm strip is rendered inside `capture-viewport` and AC-57.7's own focus rule parks focus on its Cancel button, which the page's window key handler reads as "the editor owns focus"; `Delete` removes the selected mark and the arrow keys nudge it while "Discard unsaved overlay marks…?" / "Delete this capture…?" is still open (reproduced on the unchanged page; the pre-change portal was inert to the same keys). Rated Medium and blocking under this round's dispatch instruction, with the workflow verdict-rule conflict recorded in the Review binding. Everything else reviewed holds: all 23 ACs have real production code and regression-sensitive tests (independently shown to fail on the pre-change pages, one honest invariant case aside), `COMPOSITION_LOCK` is intact (payloads, mutations, enablement, every existing test ID; `packages/` diff is exactly the human-approved A8 and OpenAPI has no drift), TM-1..TM-12 are the only expectation changes and A11/A11-W is input-only with every test name, parametrize ID and assertion identical, the validation harness and its amendments hide no defect, SSOT/task/handoff claims match file state and receipts, and the authoritative Windows gate is clean (671/671, 110/0/0) on a commit code-identical to HEAD.

**Follow-up (via `/execution-corrections`)**: fix Finding 1 in `CapturePage.tsx` (scope the editor keys away from the confirm strip) with a keyboard regression in `capture-page.behavior.test.ts` (and optionally in the AC-57.10 strip spec); rerun `green57`, `gate57`, `pregate` and `WINDOWS_GATE`; Findings 2–4 and observation 1 may be taken in the same correction or opened as follow-ups outside this loop; re-dispatch Round 2 (cap 6).

**Residual risk**: the rail's post-click staleness window (Finding 2) is a UX nit that self-corrects on the next crossing; the AC-58.12 rail spec is timing-tolerant rather than timing-proof; the pre-existing readiness Fix-link-before-load behaviour is out of scope by plan and unchanged.

🕐 Completed: 2026-09-29 14:57 (UTC)

---

## Corrections Applied — 2026-09-29 (after Round 1)

Author: the Claude Code orchestrator, acting as coder under `/execution-corrections`. The verdict is set to `corrections_applied`, not `approved`; approval needs the independent reviewer's Round 2. The Round 1 findings and verdict text above are unedited.

### Changes

| Finding | Test first (new tests; no existing assertion changed) | Fix |
|---|---|---|
| 1 (Medium, blocking) | `capture-page.behavior.test.ts`: `it.each` "AC-57.7 while the {dirty,delete} confirm strip owns focus, Delete and arrows leave the selected mark alone". Each case draws an arrow, opens the strip, waits for focus on its Cancel button, dispatches `ArrowRight` keydown/keyup and `Delete` on `window`, then asserts the arrow count stays 1, `x1` is unchanged, the strip is still open, and 0 `DELETE` requests were sent. | `CapturePage.tsx` `annotationOwnsFocus()` returns `false` when `document.activeElement.closest('[data-testid="capture-confirm-strip"]')` is non-null. The strip gets back the old portal's key scope; nothing else changes. |
| 2 (Low) | `settings-rail.test.tsx`: "AC-58.3 a crossing dropped during the click lock is reconciled when the lock expires". It uses a fake observer and fake `setTimeout`/`Date`. Click TTS, report MCP inside the lock (TTS stays current), advance 1000 ms, then expect MCP to be current and exactly one `aria-current`. | `SettingsRail.tsx`: `activate()` arms a timer (`CLICK_LOCK_MS` = 800, cleared on re-click and on unmount) that calls `reconcile(clicked)`. The observer effect installs `reconcile` and clears it on cleanup. If the clicked section's top is still inside the scroller, it keeps the clicked entry (RULE-2). Otherwise it applies the same `current()` rule (band, or bottom-of-scroll) to the retained `visible` map. The observer path now shares `current()`, with no behaviour change outside the lock. |
| 3 (Low) | `settings-rail.test.tsx`: "AC-58.6 the cookie mode group keeps its visible name as its accessible name". It asserts `getByRole('group', { name: 'Cookie mode' })` is `settings-leaf-cookie_mode`. | `SegmentedControl.tsx` gets an additive optional `label` prop: `aria-label={label ?? name}`, so existing callers are unchanged (the `PathRow readOnly` precedent). `SettingsPage.tsx` passes `label="Cookie mode"`. |
| 4 (Low) | The same new AC-58.6 test also asserts the segment contract for each mode: `radio.id === settings-cookie-mode-{mode}` and `radio.closest('label').htmlFor === radio.id`. The base page's radios had no `id` or `htmlFor` (`1f9b035:SettingsPage.tsx:251-266`), so this pins the ST1 adoption. The existing AC-58.6 test is untouched. | none (test-rigor only) |
| Obs. 5 | — | Kept deliberately. Save/Open/Delete stay in the viewport editor scope, like the existing toolbar buttons. Only the confirm strip is excluded, because it is the one surface AC-57.7 makes modal-like. |
| Obs. 1 | — | Not changed. It is outside AC-57.7's contract and pre-existing on the base portal, so it is left as a follow-up candidate. |

Diff: 6 files, +128/−15 under `ui/` (4 source files, 2 unit test files). The only removed test line is the `@testing-library/react` import, which gains `fireEvent`.

### Evidence

```json
{"schema_version":"evidence.v1","check_id":"p11cs-r1c-red-on-prefix","command":"git checkout 1663b0b -- CapturePage.tsx SettingsRail.tsx SettingsPage.tsx SegmentedControl.tsx; npx vitest run tests/unit/settings-rail.test.tsx tests/unit/capture-page.behavior.test.ts; restore fixed files","cwd":"/home/user/av-kit/ui","scope":"new correction tests against the pre-fix source","phase":"red","exit_code":1,"result":"pass (expected Red reproduced)","tested_state":"source 1663b0b, tests from the correction","output":"Tests 4 failed | 68 passed (72): AC-58.3 reconcile — expected null to be 'location'; AC-58.6 name — Unable to find role group name 'Cookie mode'; AC-57.7 dirty and delete strip — expected length 1 but got +0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"p11cs-r1c-green","command":"npx vitest run tests/unit/settings-rail.test.tsx tests/unit/capture-page.behavior.test.ts tests/unit/settings-page.test.ts tests/unit/layout-primitives.test.ts; npm run typecheck; npm run lint","cwd":"/home/user/av-kit/ui","scope":"targeted suites plus UI types and lint on the corrected tree","phase":"green","exit_code":0,"result":"pass (only ENV_BOUND AC-51.6 failed)","tested_state":"corrected working tree","output":"Tests 1 failed | 102 passed (103): AC-51.6 CRLF hash (tolerated env-bound); typecheck exit 0; lint exit 0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"p11cs-r1c-pregate","command":"bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh pregate","cwd":"/home/user/av-kit","scope":"container pre-gate: full Vitest, harness build, full Electron, types, lint, MCP, OpenAPI, render (a superset of green57/gate57/green58/gate58)","phase":"full-gate (non-authoritative)","exit_code":0,"result":"pass","tested_state":"corrected source (the later edit only added assertions to a new unit test, re-run green above)","output":"PASS s26-gate-vitest: 673 passed, env-bound tolerated AC-51.6, AC-41; PASS s26-gate-e2e: 106 passed, env-bound tolerated 4 capture-picker specs; PASS container pre-gate (authoritative gate: windows-gate)","fresh":true}
```

### Still required before Round 2

`WINDOWS_GATE` attempt 3 on the pushed correction commit. The code under `ui/` changed, so `windows-gate-check` against attempt 2 (`7613beb`) now correctly refuses. Round 2 is dispatched after the new result is pushed.

---

## Round 2

> **Review Mode**: `execution`
> **Verdict**: `approved`

### Review binding

- **Intent anchor**: The plan's goal is to *"Deliver Session 26 as grouped"* — MEU-57 `gui-capture-layout` and MEU-58 `gui-settings-layout` composed inside `COMPOSITION_LOCK`, followed by the Phase 11 exit gate. Round 2 answers whether the Round 1 corrections close the four findings without regression, whether the post-Round-1 test-only amendments (A12, A13, A14, A16) and the tooling/governance amendments (A15, A17) are what they claim, and whether the delivered work now achieves that intent.
- **Intent achieved**: `yes` — the AC-57.7 keyboard-scope defect is fixed and pinned by a discriminating test; the three Low findings are closed; every amendment since Round 1 is input/timing hardening, tooling or a single governance hash under quoted human approval, with no assertion, test name, expected outcome or product file changed; the authoritative Windows gate (attempt 7) is clean on a commit code-identical to HEAD.
- **Reviewed state**: HEAD `7b05c7a` (branch `claude/quirky-gates-o1lql2`), clean tree before and after the review (`git status --short` empty; the only files written are this review file and scratch under `<scratchpad>/review-r2/`). `git diff cb864f3 HEAD --stat -- ui packages mcp-server tests .agent/model-registry.local.json` is empty, so `WINDOWS_GATE` attempt 7 (`f4c1a12`, `tested_commit` `cb864f3`, `clean_tree: true`) binds to the reviewed code.
- **Reviewer**: the same independent Fable 5.1 subagent route as Round 1 (`human-review-decision.md`, `USER_EXPLICIT`); the reviewer authored none of the work, including none of the corrections. Verdict recorded by the reviewer.
- **Verdict rule applied**: the dispatch rule (no High/Critical; no Medium that is a demonstrated runtime defect inside an AC's contract). No finding of either kind remains.

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| R2-1 | Low | no | test-rigor | **The rail-reconcile unit test covers only the null-scroller branch.** `AC-58.3 a crossing dropped during the click lock is reconciled…` renders without a scrolling ancestor, so `scrollParent()` is `null`, `box` is `undefined`, and `reconcile()` skips its "clicked section still on screen → keep the click" guard (`SettingsRail.tsx:127-133`) and goes straight to `current()`. That guard — the part that protects a user's click from being overridden — has no unit coverage, and the Electron spec (`settings.test.ts:221`) asserts `aria-current` on MCP inside the 800 ms lock, so it does not exercise the expiry either. The reviewer's PROBE-R2-A/C/D (real Electron, below) show the guard holds: after clicking `capture`, `mcp`, `download`, `tts`, `appearance`, `dependencies`, `readiness` and waiting past the lock, the clicked entry stays current (one exception attributed to R2-2, pre-existing). 🟡 by IR-5: the test is discriminating (Red on `1663b0b`, `expected null to be 'location'`) but pins half of the correction. | `ui/tests/unit/settings-rail.test.tsx:289-323`; `ui/src/renderer/src/features/settings/SettingsRail.tsx:127-133` | Add one jsdom case with `getBoundingClientRect` stubbed on the scroller and the clicked section so `top` falls inside the box, click, report another section during the lock, advance 1000 ms, and assert the clicked entry is still current. Outside this loop. | open (non-blocking) |
| R2-2 | Low | no | behavior (residual, pre-existing) | **A crossing delivered after the lock still re-targets the bottom rule.** Under xvfb the IntersectionObserver delivers a scroll's crossing ~0.7–1.0 s after the scroll lands (PROBE-R2-D: scroll lands at ~480 ms, IO callback at 1000–1430 ms). After clicking `readiness` from `capture` the late crossing (`appearance=1` at ~1.28 s) arrives past `clickLockUntil`, the observer's bottom rule picks the last section whose top is on screen, and the highlight moves to `mcp` at ~1.3 s. **Identical on the pre-fix build `1663b0b`** (same sequence, same timings, 2/2 runs each), so the Round 1 correction neither caused nor changed it; the reconcile timer at 800 ms correctly kept the click (readiness top 514 px inside the 40–773 px box). On a desktop the crossing arrives within a frame of the scroll, inside the lock. Same surface as Round 1 Finding 2; recorded once as residual risk per Materiality Gate #4, not as a new failure. | `ui/src/renderer/src/features/settings/SettingsRail.tsx:100-103` (lock check), `:110-118` (bottom rule) | No action in this loop. If the rail is touched again: make the observer callback also honour "clicked section still on screen" for the first crossing after lock expiry, or extend the lock until the scroll has settled. | residual |
| R2-3 | Low | no | clerical | `task.md` row H1-6 still reads "`WINDOWS_GATE` attempt 2 passed at `7613beb`"; the authoritative gate is now attempt 7 at `cb864f3` (`windows-gate-result.json` at `f4c1a12`), as the walkthrough and plan A17 record. The row's `[x]` state and validation cell are correct; only the prose is stale. | `docs/execution/plans/2026-09-28-p11-capture-settings/task.md:50` | Replace "attempt 2 … `7613beb`" with "attempt 7 … `cb864f3`" at closeout. | open (clerical) |

> No finding is blocking. R2-2 is not a regression: it reproduces byte-for-byte on `1663b0b`, and its trigger (IO delivery lagging a landed scroll by ~1 s) is an artefact of the headless container, where the gate is not authoritative.

### Round 1 findings — closure check

| R1 # | Claimed fix | Verified | Red on `1663b0b` source (reviewer reproduction) | Regression check |
|---|---|---|---|---|
| 1 (Medium, blocking) | `annotationOwnsFocus()` returns `false` inside `capture-confirm-strip` | `CapturePage.tsx:97-101`: `active.closest('[data-testid="capture-confirm-strip"]') !== null → false`; the strip container carries that ID (`:978`); the `Delete` and arrow branches (`:887`, `:892`) both consult the guard; `Escape` (`:869-884`) was never gated and is unchanged. | Both `it.each` cases (`capture-page.behavior.test.ts:1141-1165`) fail on the pre-fix source with `expected to have a length of 1 but got +0` — the arrow is deleted behind the prompt, exactly Round 1's PROBE-A. Green at HEAD. | The guard only widens the "not editor-owned" set by one subtree; tools, color inputs and the action buttons keep their prior scope (observation 5, judged below). `capture-page.test.ts` source pins 31/31; Electron AC-57.10 ×4 passed in the container pre-gate and 110/0/0 on Windows. | **closed** |
| 2 (Low) | Reconcile on lock expiry | `SettingsRail.tsx:69,80-84,119-133,143-155`: `activate()` arms a `CLICK_LOCK_MS` timer (cleared on re-click and unmount) that calls `reconcile(clicked)`; the observer effect installs it and resets it on cleanup; the observer path now goes through the shared `current()` with the same band/bottom rule (moved verbatim, no behaviour change outside the lock). | `AC-58.3 … reconciled when the lock expires` fails on the pre-fix source with `expected null to be 'location'`. Green at HEAD. | PROBE-R2-A/B/C/D (real Electron, HEAD): a scroll-to-top inside the lock is corrected to `download` after the lock and a scroll-to-bottom to `mcp` (R2-B); clicks on mid, last and first sections stay current after expiry (R2-C, 5 sections; R2-D, 6 clicks). The only override observed is R2-2, which is pre-existing. Rail spec `settings.test.ts:221` ×3 in the container: 3 passed, 0 flaky. | **closed** (R2-1 notes the unit-coverage gap) |
| 3 (Low) | `SegmentedControl` `label` prop; `label="Cookie mode"` | `SegmentedControl.tsx:16-17,22,31`: optional `label`, `aria-label={label ?? name}`; the seven other callers (`ConvertPage.tsx:536,624,708,728`, `DownloaderPage.tsx:642`, `TTSPage.tsx:585`, `primitive-harness.tsx:25`) pass no `label`, so their accessible names are unchanged (`grep -rn "<SegmentedControl" ui/src`). | `AC-58.6 … keeps its visible name as its accessible name` fails on the pre-fix source with `Unable to find an accessible element with the role "group" and name "Cookie mode"`. Green at HEAD. | `convert-page.test.ts`, `gui-actions-audit.test.ts`, `layout-primitives.test.ts` pass at HEAD (only the env-bound AC-51.6 fails); Vitest 675/675 on Windows. | **closed** |
| 4 (Low) | Pin the segment contract (`id`/`htmlFor`) | Same new test asserts `radio.id === settings-cookie-mode-{mode}` and `radio.closest('label').htmlFor === radio.id`; the base page's radios had neither (`1f9b035:SettingsPage.tsx:251-266`). | Fails on `1663b0b` only for the name (the ids already existed there — that is expected: Finding 4 was about the *base* page `1f9b035`, and the discriminating assertion is the label/id pairing the base page lacked). | none (test only); the original AC-58.6 test is untouched. | **closed** |

**Observation 5 (Save/Open/Delete stay in the editor key scope) — judged.** Kept deliberately by the author. The action group sits in the viewport chrome next to the pre-existing tool buttons, which have always shared the editor key scope; only the confirm strip is modal-like under AC-57.7. The `Delete` key cannot activate a button (Enter/Space do), so there is no activation conflict, and a keyboard user who tabs to "Delete" and presses `Delete` removes the selected mark just as they would on "Arrow". Acceptable and consistent; if the strip's exclusion is ever generalised, exclude the whole `capture-actions` group, not individual buttons. Not a finding.

### Test-only amendments A12, A13, A14, A16 — hardening only

- **Scope.** `git diff 1663b0b HEAD -- ui/tests/e2e/download-queue.test.ts | grep -E "^[-+].*(expect\(|test\(|\.toBe|toHave)"` → no hits (exit 1). The diff adds `type Locator` to the import, four helpers (`settledCenter`, `rowTransitionsIdle`, `windowSettled`, and the committed-`over` wait inside `dragOver`), rewrites `grabRow`/`dragOver` bodies, and adds one `await windowSettled(page)` setup line in AC-49.27 (`:1298`). Commit stats match the walkthrough: A12 `1442d73` +86/−11 in the spec, A13 `52ec926` +30/−0, A16 `f680e75` +13/−0. `tests/unit/test_services.py` (A14) changes four lines: a two-line comment and the move of `catalog.release.set()` after both `join`s (`:2135-2139`).
- **Not vacuous.** Every added wait fails closed: `settledCenter` throws after 60 frames; `rowTransitionsIdle`, `windowSettled` and the `aria-pressed="true"` / live-region `waitFor`s time out into a test failure. None of them can produce a wrong-but-green drop, because the PUT bodies (`AC-49.25:1236`, `AC-49.27:1319`), the row order and the announcement texts are still asserted after `mouse.up()` / `Space`. `dragOver`'s wait for `"… moved to position N of M."` uses the target's **pre-drag DOM position** (`:1174-1178`), which is what `createQueueAnnouncements` announces (`queue-dnd.ts:118-137`, `over.position` from the pre-drag `items`), so it waits for exactly the intended `over` and cannot mask a drop on another row — if `over` never becomes the target the test fails on the wait, not on a false PUT. `windowSettled` cannot hide a product cancel: the cancel it avoids is dnd-kit's own `resize`/`visibilitychange` cancel (below), and a cancel from any other cause still fails the assertions.
- **Root causes checked against `@dnd-kit/core@6.3.1` (`ui/node_modules/@dnd-kit/core/dist/core.esm.js`).** Resize cancel: `this.windowListeners.add(EventName.Resize, this.handleCancel)` at `:1156` (pointer) and `:1444` (keyboard), `EventName.Resize = "resize"` `:1073`; the main window is created `show: false` (`src/main/index.ts:457`) and shown after `loadFile` (`:493`), consistent with the probed post-launch resize. Stale `over`: `overId` is derived in render; the `[overId]` effect (`:3241-3283`) calls `setOver(over)` and `onDragOver` (the announcement) in one `unstable_batchedUpdates`; the layout effect at `:3288` copies `over` into `sensorContext.current`, which `handleEnd` reads (`:2971`). The announcement therefore commits in the same React commit whose layout effect updates `sensorContext.current.over`, so a wait for the announcement is a wait for the committed `over` — A16's mechanism is sound. Droppables are measured with `getTransformAgnosticClientRect` (`defaultMeasuringConfiguration` `:2478-2490`), so `settledCenter`'s transform-stripped aim targets the same rect dnd-kit uses for `closestCenter` — A12's mechanism is sound.
- **A14 still proves the conflict.** `models.download()` (`packages/core/src/avkit_core/services/models.py:86-108`) checks and sets `Downloading` under `self._lock` and returns after starting the worker; the catalog hold lives in the worker. With both contenders joined before `catalog.release.set()`, the second caller necessarily meets `Downloading` and raises `ConflictError`; `max_in_flight == 1` still proves single entry. If `download()` ever blocked on the held catalog, both joins would time out, the later caller would find `Idle` after release and download again, and `0 == 1` would fail — so the reorder does not weaken the immediate-return proof either. Windows: 50× repeat clean, full suite 608/0 (attempt 5 and 7 receipts).
- **Container re-run at HEAD.** `download-queue.test.ts` (24 specs incl. AC-49.25–28, W1-14): 24 passed, 0 flaky, 3.9 min; `settings.test.ts -g "AC-58.12 rail groups" --repeat-each 3`: 3 passed. Both under `xvfb-run -a`, `ELECTRON_DISABLE_SANDBOX=1`, `ELECTRON_RUN_AS_NODE` unset, against the `ui/out` build of 2026-09-29 15:54 (newer than the last `ui/src` commit `1356c59`, so global-setup's staleness guard passed).

### A15 and A17

- **A15 (`validate-task.ps1:76-78,90-97`)** deletes `s26-win-vitest.json`/`s26-win-e2e.json` before the stage loop and reads each only when `$ran` contains its stage. Minimal and correct; the `$ran` computation moved above the reads, and the existing "ran but produced no JSON" checks still follow. Evidence that it works: attempt 4 (`706cdc7`, 8 stages, stopped at `py-tests`) carries attempt 3's `vitest 675` / `e2e 109+1` verbatim (the defect), attempt 6 (`ded5af4`, 8 stages) carries `vitest: null, e2e: null` (the fix), attempt 7 carries fresh `675/675` and `110/0/0`. `windows-gate-check` never accepted any partial list (attempts 1, 3, 4, 5, 6 all refused on the stage list), so no false pass was possible.
- **A17 (`.agent/model-registry.local.json`, `cb864f3`, author MatBanik)**: the diff is exactly one line, `validated_against` `7e85d6f3…` → `b06d7cda…`; `.agent/model-registry.local.yaml` and every `classes` binding are unchanged (`git diff 1663b0b HEAD --stat -- .agent/model-registry.local.*` → the JSON only); `tests/tooling/` is unchanged since `7613beb`. The approval is quoted verbatim in `human-gate-decision.md` §A17 (`USER_EXPLICIT`, "Revalidate overlay (Recommended)"), scoped to that one field with no `sync` and no write to `P:/.agent`. `TOOLING-SHARED-REGISTRY-COUPLING` is filed in `known-issues.yaml:29-39` (severity low, open, root cause and durable fix stated) and rendered in `known-issues.md:14`; a YAML-level comparison shows the two pre-existing entries are semantically identical (the diff is re-wrapping only). **Could not verify in the container**: that `b06d7cda…` equals `sha256(P:/.agent/model-registry.json)` (the sibling repo is not present); it is accepted on the Windows receipt chain (attempt 7 `py-tests` exit 0 includes `test_review_pipeline_wrapper_refuses_before_provider[same-vendor]`, the case that refused in attempt 6).

### Plan / evidence truthfulness

- Amendments A12–A17 in the plan, the seven `human-gate-decision.md` sections and the walkthrough's WINDOWS_GATE attempts 1–7 match the git history: attempt 3 `fe86ac3` (tested `1356c59`, 16 stages, `ui-electron` failed, e2e 109/1), attempt 4 `706cdc7` (`52ec926`, `py-tests`), attempt 5 `7151fcb` (`eb3acc9`, `ui-electron`, e2e 109/1), attempt 6 `ded5af4` (`f680e75`, `py-tests`, counts null), attempt 7 `f4c1a12` (`cb864f3`, 17 stages, all exit 0, 675/675, 110/0/0). Failures are preserved, not rewritten. The A13 implementation note (500 ms quiet window vs the 300 ms in the option text) is disclosed in the decision record and is a stricter wait of the same kind.
- SSOT (`meu-status.yaml`, `current-focus.md`), `task.md` and both MEU handoffs are unchanged since Round 1 (`git diff 1663b0b HEAD --stat` on those paths is empty); the handoff AC-57.7 rows that said ✅ are now true.
- `validate-task.sh windows-gate-check` at HEAD: `PASS windows gate @ cb864f3b…: vitest {'passed': 675, 'failed': 0, 'total': 675} e2e {'expected': 110, 'unexpected': 0, 'skipped': 0, 'flaky': 0}`, exit 0.

### Session 26 diff sweep (`0f51036..HEAD`, excluding Session 25 content at `1f9b035`)

Everything after `1663b0b` is covered above (17 files). Nothing else in the session diff was found that Round 1 missed: the Round 1 AC table, COMPOSITION_LOCK check, TM census and A11/A11-W comparison stand, and no file outside the 17 changed since.

### IR-5 grading (new/changed tests since Round 1)

| Test | Rating |
|---|---|
| `capture-page.behavior.test.ts:1141` AC-57.7 keyboard `it.each` ×2 | 🟢 (real window listener, exact count/`x1`/strip/DELETE assertions; Red on pre-fix source) |
| `settings-rail.test.tsx:289` AC-58.3 reconcile | 🟡 (discriminating, but null-scroller branch only — R2-1) |
| `settings-rail.test.tsx:407` AC-58.6 name + id/htmlFor | 🟢 |
| `download-queue.test.ts` helpers (A12/A13/A16) | not tests; every wait fails closed; assertions untouched |
| `test_services.py::test_ac_12_7` (A14) | 🟢 (conflict count, `max_in_flight`, immediate-return half unchanged) |

No 🔴 test in scope.

### Commands run (reviewer, Round 2)

- `git log --oneline 1663b0b..HEAD`; `git diff 1663b0b HEAD --stat`; `git diff cb864f3 HEAD --stat -- ui packages mcp-server tests .agent/model-registry.local.json` (empty); `git diff e514443 HEAD --stat`; `git diff 7613beb HEAD --stat -- tests/tooling` (empty)
- `git show 1356c59 -- ui/src ui/tests`; `git diff 1356c59 f680e75 -- ui/tests/e2e/download-queue.test.ts`; `git show eb3acc9`; `git show cb864f3`; `git show <attempt>:…/windows-gate-result.json` for `fe86ac3 706cdc7 7151fcb ded5af4 f4c1a12`
- `RECEIPTS_DIR=<scratch>/review-r2/receipts bash …/validate-task.sh windows-gate-check` → exit 0
- Red reproduction: `git archive HEAD ui` into `<scratch>/review-r2/prefix`, the four corrected sources replaced by `git show 1663b0b:<path>` (diff-verified), `node_modules` symlinked, `vitest run --config vitest.probe.config.ts` (base config + `server.fs.allow`) on `settings-rail.test.tsx` and `capture-page.behavior.test.ts`
- Green: `npx --prefix ui vitest run --root ui` on 7 in-scope unit files → 164 passed, 1 failed (AC-51.6 env-bound)
- Electron (xvfb, sandbox disabled): `download-queue.test.ts` full; `settings.test.ts -g "AC-58.12 rail groups" --repeat-each 3`; PROBE-R2-A/B/C/D via a scratch Playwright config (`testDir` in the scratchpad, repo `global-setup`), HEAD `ui/out` and a scratch `1663b0b` build (`git archive 1663b0b ui` + `npm run build`)
- `grep -rn "<SegmentedControl" ui/src`; dnd-kit source greps (`EventName.Resize`, `sensorContext.current`, `defaultMeasuringConfiguration`); YAML comparison of `known-issues.yaml` at `1663b0b` vs HEAD
- `python3 .agent/skills/timestamp/scripts/stamp.py`

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r2-windows-gate-check","command":"RECEIPTS_DIR=<scratchpad>/review-r2/receipts bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh windows-gate-check; git diff cb864f3 HEAD --stat -- ui packages mcp-server tests .agent/model-registry.local.json","cwd":"/home/user/av-kit","scope":"authoritative D6 gate identity (WINDOWS_GATE attempt 7)","phase":"full-gate verification","exit_code":0,"result":"pass","tested_state":"HEAD 7b05c7a; code-identical to cb864f3","output":"PASS windows gate @ cb864f3b3706e7fe5d2dc0f516e74297ee12f600: vitest {'passed': 675, 'failed': 0, 'total': 675} e2e {'expected': 110, 'unexpected': 0, 'skipped': 0, 'flaky': 0} | diff --stat empty","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r2-red-on-prefix","command":"git archive HEAD ui | tar -x -C <scratchpad>/review-r2/prefix; git show 1663b0b:<CapturePage.tsx|SettingsRail.tsx|SettingsPage.tsx|SegmentedControl.tsx> > <prefix copies>; npx vitest run --config vitest.probe.config.ts tests/unit/settings-rail.test.tsx tests/unit/capture-page.behavior.test.ts","cwd":"<scratchpad>/review-r2/prefix/ui (node_modules symlinked; fs.allow widened)","scope":"do the four correction tests fail on the pre-fix source for the asserted reasons?","phase":"red","exit_code":1,"result":"pass (expected Red reproduced)","tested_state":"source 1663b0b (diff-verified), tests from HEAD 7b05c7a","output":"settings-rail 20 tests | 2 failed: AC-58.3 reconcile → expected null to be 'location'; AC-58.6 name → Unable to find role group name 'Cookie mode'. capture-page.behavior 52 tests | 2 failed: AC-57.7 dirty and delete strip → expected to have a length of 1 but got +0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r2-green-head","command":"npx --prefix ui vitest run --root ui tests/unit/settings-rail.test.tsx tests/unit/capture-page.behavior.test.ts tests/unit/settings-page.test.ts tests/unit/layout-primitives.test.ts tests/unit/capture-page.test.ts tests/unit/convert-page.test.ts tests/unit/gui-actions-audit.test.ts","cwd":"/home/user/av-kit","scope":"corrected suites plus SegmentedControl callers at HEAD","phase":"targeted","exit_code":1,"result":"pass (only ENV_BOUND_TESTS failed)","tested_state":"HEAD 7b05c7a","output":"Test Files 1 failed | 6 passed (7); Tests 1 failed | 164 passed (165): AC-51.6 CRLF hash DCABD0F9… vs 819760B9… (tolerated env-bound)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r2-e2e-download-queue","command":"ELECTRON_DISABLE_SANDBOX=1 xvfb-run -a npm --prefix ui run test:e2e -- tests/e2e/download-queue.test.ts --reporter=json --outputFile=<scratchpad>/review-r2/receipts/r2-e2e-dlq.json (ELECTRON_RUN_AS_NODE, AVKIT_E2E_OUT_DIR unset)","cwd":"/home/user/av-kit","scope":"A12/A13/A16 helpers at HEAD, all 24 specs incl. AC-49.25-28 and W1-14","phase":"runtime","exit_code":0,"result":"pass","tested_state":"HEAD 7b05c7a (ui/out built 2026-09-29 15:54, newer than 1356c59)","output":"24 passed (3.9m); stats expected 24, unexpected 0, skipped 0, flaky 0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r2-e2e-rail-repeat","command":"ELECTRON_DISABLE_SANDBOX=1 xvfb-run -a npm --prefix ui run test:e2e -- tests/e2e/settings.test.ts -g 'AC-58.12 rail groups' --repeat-each 3 --reporter=json --outputFile=<scratchpad>/review-r2/receipts/r2-e2e-rail.json","cwd":"/home/user/av-kit","scope":"rail spec after the reconcile change","phase":"runtime","exit_code":0,"result":"pass","tested_state":"HEAD 7b05c7a","output":"3 passed (26.8s): 8.1s, 8.1s, 8.1s; expected 3, unexpected 0, flaky 0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s26-review-r2-probe-rail-lock","command":"xvfb-run -a npx playwright test --config <scratchpad>/review-r2/probe-e2e/playwright.probe.config.ts (PROBE-R2-A: click capture/mcp/download/tts/appearance, wait 1600 ms, read aria-current; PROBE-R2-B: click tts, scroll main to top at +500 ms, read at +1700 ms; click download, scroll to bottom at +300 ms, read at +1500 ms; PROBE-R2-C: per-section click from the top with samples at 100..2000 ms; PROBE-R2-D: 25 ms in-page recorder of aria-current/scrollTop/section top plus every IntersectionObserver callback, sequence tts→appearance→download→mcp→capture→readiness, run 2× on HEAD ui/out and 2× on a scratch 1663b0b build)","cwd":"/home/user/av-kit/ui","scope":"does the rail reconcile ever override a user's click wrongly?","phase":"targeted","exit_code":0,"result":"observed (no override caused by the correction)","tested_state":"HEAD 7b05c7a vs pre-fix 1663b0b","output":"R2-B duringLock=tts afterLock=download; duringLock2=download afterLock2=mcp (reconcile corrects a scroll made inside the lock). R2-C appearance/dependencies/readiness/console/mcp: clicked entry current at every sample to 2000 ms. R2-D HEAD and 1663b0b identical: scroll lands ~460-486 ms (450 ms fallback; smooth scroll never starts under xvfb); IO crossings arrive 1000-1438 ms after each click; only 'readiness' flips to 'mcp' at ~1.3 s, coincident with the late crossing appearance=1 at ~1.28 s, on both builds → pre-existing bottom-rule behaviour after lock expiry (R2-2), not the reconcile (readiness top 514 px inside box 40-773 → reconcile kept the click)","fresh":true}
```

### Verdict

`approved` — Round 1's blocking finding is fixed at the exact surface (`annotationOwnsFocus()` now excludes the confirm strip) and the new keyboard tests fail on the pre-fix source for the asserted reason; the three Low findings are closed with discriminating tests and no caller of `SegmentedControl` changes; the rail reconcile corrects dropped crossings and, in real Electron, never overrides a click on its own (the one post-lock flip reproduces identically on the pre-fix build and is a pre-existing environment-bound edge, recorded as residual). A12, A13, A14 and A16 change no assertion, test name, expected outcome or product file, fail closed, and rest on mechanisms verified in dnd-kit 6.3.1 source and the service lock; A15 is a minimal tooling fix proven by the attempt 4→6→7 JSONs; A17 is a single approved hash under quoted `USER_EXPLICIT` authority with the coupling filed as a known issue. The plan, decision records and walkthrough match the git history and the seven preserved gate attempts, and the authoritative Windows gate (17/17 stages, 675/675, 110/0/0) binds to code identical to HEAD.

**Follow-ups (outside this loop, non-blocking)**: R2-1 (one jsdom case for the "clicked still on screen" branch), R2-2 (only if the rail is touched again), R2-3 (one-line `task.md` prose fix at closeout), Round 1 observation 1 (return focus to the invoker after the strip closes).

**Residual risk**: the rail's lock is wall-clock and the observer's bottom rule is unconditional after it, so a crossing delivered late (throttled or occluded window) can move the highlight to the last section after a click near the bottom; on a desktop the crossing lands inside the lock. `TOOLING-SHARED-REGISTRY-COUPLING` remains open: the next shared-registry edit will fail `py-tests` on Windows until the overlay is revalidated again.

**Could not verify in the container**: the A17 hash against `P:/.agent/model-registry.json`; Windows-only stages (`py-tests` 608/0, the capture-picker stub specs) and the drag repeat runs (100/100, 220/220) are accepted on the receipt chain and the attempt 7 JSON.

🕐 Completed: 2026-09-30 01:42 (UTC)
