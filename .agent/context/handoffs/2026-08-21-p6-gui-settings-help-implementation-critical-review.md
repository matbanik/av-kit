---
date: "2026-08-21"
review_mode: "implementation"
target_plan: "docs/execution/plans/2026-08-21-p6-gui-settings-help/implementation-plan.md"
verdict: "approved"
findings_count: 0
round: 3
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
---

# Critical Review: p6-gui-settings-help (MEU-23)

> **Review Mode**: `implementation`
> **Verdict**: `approved`

## Intent Anchor

MEU-23 was intended to replace the settings stub with a complete, persisted Settings page; add safe setup-readiness and MCP-status IPC; mount reusable searchable help; and prove the settings/help flows with meaningful Wave 4/6 Electron tests without rewriting FastAPI/MCP or rewinding the Phase 6 chrome. The delivered UI mounts and the focused E2E suite runs, but several required controls and command/readiness/error paths do not implement the approved AC contract.

## Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| F1 | High | **AC-23.2, AC-23.6, and AC-23.7 are materially incomplete.** The approved named sets require all 11 downloader leaves, all 9 transcript leaves, and all 7 TTS leaves. The rendered cards omit downloader `yt_dlp_debug`; transcript `delay_between_requests`, `retry_delay`, `pause_between_batches`, `playlist_end`, and `max_words_per_document`; and TTS `voice`, `speed`, `output_format`, `output_path`, and `device`. The passing test finds these names in schemas/source aggregation rather than verifying editable controls, so the handoff's “all ACs met” claim is false. | `implementation-plan.md:95-97,267,271-272`; `SettingsPage.tsx:151-280,285-370`; `settings-page.test.ts:42-98` | Render every required leaf with the specified GET/PUT parity and add interaction tests that change each control and assert namespace, leaf payload, and persisted hydration. | open |
| F2 | High | **AC-23.11 setup readiness does not use the specified producers.** Descriptor readiness accepts any nonempty text lacking the literal `"tombstone"` instead of requiring parseable non-tombstone JSON. The models probe always targets `~/.avkit/models`, ignoring the current `tts.models_directory` and the required app-data default. The UI renders plain yes/no paragraphs and provides no failing-row deep-link/focus behavior. Invalid descriptors and a configured models path that is a regular file can therefore report the wrong state. | `implementation-plan.md:76,119-120,276`; `ui/src/main/index.ts:294-328`; `SettingsPage.tsx:451-458` | Parse and validate the descriptor, resolve the current TTS models setting or app-data default, test missing/invalid/tombstone descriptors and regular-file models paths, and implement/assert failing-row navigation/focus. | open |
| F3 | High | **AC-23.10 `settings:check_deps` command delivery recursively redispatches itself.** `SETTINGS_COMMANDS.checkDeps()` emits `av-kit:settings:check_deps`; the always-mounted listener for that same event calls `SETTINGS_COMMANDS.checkDeps()` again. A button or palette activation can recurse synchronously to stack exhaustion instead of being a single refetch action. W4-3 passes because it only checks that some dependency URL was observed and does not fail on renderer errors or assert exactly-once delivery. | `settings-commands.ts:1-3,15-18`; `AppShell.tsx:120-144`; `SettingsPage.tsx:127-133,445`; `settings.test.ts:142-179` | Separate registry intent events from page-local execution, or make AppShell the sole non-redispatching owner; add a behavioral test asserting one activation, one refetch, and no `pageerror`. | open |
| F4 | High | **AC-23.17 `help:toggle` does not toggle HelpCard.** AppShell handles the palette event by emitting `av-kit:help:toggle-local` and incrementing `data-help-toggle`, but `HelpCard` has no listener/prop for either signal and owns expansion only through its button state. Off-route navigation is also absent. The AC-23.17 test merely greps for names, while Wave 6 tests visibility/search without invoking the palette command. | `implementation-plan.md:133,282`; `settings-commands.ts:5-12`; `AppShell.tsx:116-118,197`; `HelpCard.tsx:43-103`; `help-card.test.ts:68-77`; `help-search.spec.ts:20-40` | Wire one authoritative toggle action into the active HelpCard, including off-route navigation, and exercise the actual palette command in Electron E2E. | open |
| F5 | High | **AC-23.14/G15 error surfacing is absent for immediate operations.** Only the debounced `schedulePut` path catches `SettingsValidationError`/`ApiError` and dispatches the banner event. `putNow`, apply-defaults, browse saves, theme saves, dependency actions, and MCP copy are launched with `void` and have no catch-to-banner path, so server 422/409/API/IPC failures become unhandled rejections rather than in-card errors. | `implementation-plan.md:126,250-251,279`; `useSettingsPage.ts:92-105,111-120`; `SettingsPage.tsx:88-137,145-148,161,200,263,280,301,352,416-426,470-473` | Route every user-triggered async action through a shared error-to-banner handler and add negative interaction tests for API and IPC failures. | open |
| F6 | Medium | **IR-5/IR-7 test rigor is insufficient and demonstrably false-passes broken behavior.** `settings-page.test.ts` is source-text inspection despite AC-23.1-13 being labeled integration; AC-23.17 is also source grep. W4-3 clicks many controls but asserts only apply-defaults and dependencies calls, not browse IPC, PUT namespace/body, MCP results, exactly-once dispatch, or renderer errors. Focused Vitest (20/20) and Wave 4/6 (5/5) therefore stay green with F1-F5 present. | `settings-page.test.ts:27-163`; `help-card.test.ts:68-77`; `settings.test.ts:142-179` | Replace source-presence assertions for integration ACs with component/IPC behavior tests and strengthen W4-3 outcome assertions. | open |

## Scope

**Targets**: `implementation-plan.md`, `task.md`, and `2026-08-21-p6-gui-settings-help-MEU-23-handoff.md`, correlated by the exact date/slug and sole MEU-23 handoff set.

**Claimed implementation inspected**: settings renderer sources; HelpCard/help modules and feature mounts; router, AppShell, command registry; main/preload/renderer IPC types; all three MEU-23 unit test files; both Wave 4/6 E2E files; and the E2E census script.

**Scope-boundary results**:

- `/settings` routes to `SettingsPage` (`router.tsx:45-49`), so no chrome rewind was observed in live file state.
- `getMcpAccessStatus()` returns `{ tokenPresent: boolean }` and the renderer displays only yes/no (`ipc.ts:366-368`; `env.d.ts:27-32`; `SettingsPage.tsx:462-474`). `copyMcpConfig()` returns `{ ok: true }`; no MCP token value is returned by the new status path.
- The snapshot has no `.git` directory, so historical proof that `packages/api/` and `mcp-server/` were untouched is unavailable. Direct inspection found the reviewed feature wiring under `ui/`; this limitation is not itself a finding.

## Commands Executed

| Command | Result | Receipt |
|---|---|---|
| `git status --short` | unavailable: snapshot is not a Git worktree | `C:/Temp/av-kit/review-git-status.txt` |
| Focused Vitest for the three MEU-23 unit files | 20 passed | `C:/Temp/av-kit/review-focused-vitest.txt` |
| `npm run typecheck` | pass | `C:/Temp/av-kit/review-typecheck.txt` |
| `npm run lint` | pass | `C:/Temp/av-kit/review-lint.txt` |
| `npm run build` | pass | `C:/Temp/av-kit/review-build.txt` |
| Wave 4/6 census | pass, 23 controls enforced | `C:/Temp/av-kit/review-e2e-census.txt` |
| Focused Wave 4/6 Playwright | 5 passed | `C:/Temp/av-kit/review-e2e-wave4-wave6.txt` |
| Full Vitest | 161 passed | `C:/Temp/av-kit/review-full-vitest.txt` |
| Full Playwright | incomplete: 39/41 passed before the 180-second command timeout; not counted as green | `C:/Temp/av-kit/review-full-playwright.txt`; `C:/Temp/av-kit/review-full-playwright-tail.txt` |

## Checklist Results

### Implementation Review

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | partial | Real Electron Wave 4/6 ran 5/5, but uses a renderer fetch seam and does not assert the broken action outcomes. |
| IR-2 Stub behavioral compliance | n/a | No reviewed persistence stub contract. |
| IR-3 Error mapping completeness | fail | F5: immediate API/IPC errors do not reach the in-card surface. |
| IR-4 Fix generalization | n/a | Initial implementation review. |
| IR-5 Test rigor audit | fail | `settings-page.test.ts` 🔴 Weak; `help-card.test.ts` AC-23.15-16 🟡 Adequate and AC-23.17 🔴 Weak; `gui-actions-audit.test.ts` 🟢 Strong for its static contract; `settings.test.ts` W4-1/2 🟢 Strong and W4-3 🔴 Weak; `help-search.spec.ts` 🟢 Strong for AC-23.22. |
| IR-6 Boundary validation coverage | fail | Strict schemas exist, but renderer behavior and negative API/IPC outcomes are not exercised. |
| IR-7 Deferral and AC coverage integrity | fail | All AC IDs appear in the handoff, but integration ACs 23.2/6/7/10/11/17 are backed by source inspection or incomplete E2E and several are materially undelivered. |

## Out-of-Contract Observations

- The full 41-test Playwright run was inconclusive due the review command timeout after 39 passes; the focused contractual Wave 4/6 run completed 5/5.

## Verdict

`changes_required` — F1-F5 are evidence-backed High-severity failures of approved runtime/contract behavior. The clean typecheck/lint/build results and green focused suites confirm build health, but the tests currently permit these material defects to pass. Corrections must proceed through `/execution-corrections`; this review does not modify product code.

## Concrete Follow-up Actions

1. Implement every required downloader/transcript/TTS settings leaf and its persisted GET/PUT interaction coverage.
2. Correct descriptor/models readiness producers and add the required failing-row deep-link/focus behavior plus negative tests.
3. Repair settings/help command routing so each command has one non-recursive, behaviorally connected owner.
4. Centralize user-visible error handling for all immediate API/IPC actions.
5. Replace source-grep integration claims with behavioral unit/component tests and strengthen W4-3 to assert outcomes and renderer errors.

## Residual Risk

The focused Electron tests verify rendering and limited actuation through a seam, not live FastAPI behavior. The new MCP status channel appears secret-safe by direct code inspection, but no dedicated behavior test proves its false/true cases or guards the response shape against future token leakage.

---

## Corrections Applied (2026-08-21 / round after r1)

**Findings addressed**: F1–F6 (implementor + builder); additional boot fix `randomUUID` import restored in `ui/src/main/index.ts` after readiness extract (Electron firstWindow timeouts).

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F1 | Missing downloader/transcript/TTS leaves | All named leaves rendered with `settings-leaf-*` testids | Vitest leaf presence + Wave 4/6 |
| F2 | Readiness producers + deep-links | `setup-readiness.ts` JSON/tombstone parse; `tts.models_directory` from avkit.db / app-data default; readiness-*-link scroll/focus | `setup-readiness.test.ts` + UI links |
| F3 | check_deps recursion | AppShell no longer redispatches; SettingsPage owns refetch | AC-23.10 dispatch-count test |
| F4 | help:toggle | HelpCard listens `av-kit:help:toggle-local`; AppShell navigates off-route | help-card AC-23.17 |
| F5 | Immediate op ERROR_SURFACE | `runSettingsAction` / `putNow` catch → banner | unit + handlers wrapped |
| F6 | Weak tests | Behavioral Vitest + stronger W4-3 | 164 Vitest; Wave 4/6 5/5 (`C:/Temp/av-kit/e2e-wave4-wave6-r3.txt`) |
| boot | `randomUUID` undefined after extract | Re-import `randomUUID` in `index.ts` | Electron smoke + E2E green |

Awaiting re-review round 2.

---

## Round 2 Recheck (2026-08-21)

**Workflow**: `/execution-critical-review` Round 2  
**Agent**: `gpt-5.6-sol`  
**Intent recheck**: Re-verify the Round 1 corrections against live code and behavioral receipts, with particular attention to complete settings leaves, readiness producers, non-recursive command delivery, HelpCard palette behavior, immediate-operation error surfacing, Wave 4/6 rigor, main-process UUID wiring, and MCP-token containment.

### Findings First

| # | Severity | Finding | File:Line / Receipt | Recommendation | Status |
|---|----------|---------|---------------------|----------------|--------|
| F4 | High | **AC-23.17 remains behaviorally broken for the required off-route case.** `AppShell` starts navigation to `/settings` and immediately emits `av-kit:help:toggle-local`; the destination `HelpCard` is not mounted in time to receive that synchronous event. A live Electron probe with Settings help pre-collapsed produced `{"hash":"#/settings","helpMounted":true,"expanded":"false"}`: navigation completed, but the card did not toggle. | `implementation-plan.md:282`; `ui/src/renderer/src/components/layout/AppShell.tsx:114-123`; `ui/src/renderer/src/components/help/HelpCard.tsx:40-58`; `C:/Temp/av-kit/review-r2-help-offroute-probe.txt` | Queue the toggle until after route mount, or carry explicit toggle intent into the destination; add a real AppShell/Electron test that starts off-route with collapsed Settings help and asserts navigation plus `aria-expanded="true"`. | open |
| F6 | Medium | **The corrected tests still false-pass F4.** The HelpCard unit test proves only that an already-mounted card responds to the local event, while the palette-delivery test remains source-text inspection. Wave 6 checks visibility/search only and never invokes `help:toggle`; therefore 164/164 Vitest and 5/5 Wave 4/6 remain green with the off-route contract failure present. The settings tests are materially stronger than Round 1, but AC-23.17 integration coverage is still weak. | `ui/tests/unit/help-card.test.ts:69-89,116-127`; `ui/tests/e2e/help-search.spec.ts:20-40`; `C:/Temp/av-kit/review-r2-full-vitest.txt`; `C:/Temp/av-kit/review-r2-e2e-wave4-wave6.txt` | Replace the AC-23.17 source-wiring assertion with behavioral AppShell delivery coverage and extend Wave 6 with the off-route palette scenario. | open |
| F7 | Medium | **The mandatory UI lint gate is not clean, contradicting the handoff's correction evidence.** Live `npm --prefix ui run lint` reports two `@typescript-eslint/no-require-imports` errors in the new readiness implementation and its test. Typecheck and build pass, so no runtime failure was demonstrated, but the P1 gate and the handoff's `eslint: 0 warnings` claim are false in current state. | `ui/src/main/setup-readiness.ts:59`; `ui/tests/unit/setup-readiness.test.ts:53`; `C:/Temp/av-kit/review-r2-lint.txt`; `2026-08-21-p6-gui-settings-help-MEU-23-handoff.md:170-181` | Replace the `require()` forms with lint-compliant Node SQLite imports while preserving Electron/Vitest compatibility, then rerun lint, build, readiness tests, and Wave 4/6. | open |

### F1-F6 Recheck Status

| Finding | Round 2 status | Recheck evidence |
|---------|----------------|------------------|
| F1 — missing downloader/transcript/TTS leaves | resolved | Live renderer census finds all 11 downloader, 9 transcript, and 7 TTS leaves with `settings-leaf-*` controls; `SettingsPage.tsx:185-553`. Component test renders the required controls (`settings-page.test.ts:192-259`). |
| F2 — readiness producers/deep-links | resolved | Descriptor JSON parse/tombstone rejection, app-data default, SQLite `tts.models_directory`, regular-file rejection, write probe, and ready-port parsing are implemented in `setup-readiness.ts:23-112`; focused negative/producer tests pass 5/5 (`setup-readiness.test.ts:15-83`). Readiness links render and target focusable cards (`SettingsPage.tsx:623-710`). |
| F3 — recursive `settings:check_deps` | resolved | AppShell no longer owns/redispatches the settings event. SettingsPage owns one event listener and refetches dependencies/readiness (`SettingsPage.tsx:72-87,164-166`); the behavioral dispatch-count test passes (`settings-page.test.ts:277-293`). |
| F4 — HelpCard palette toggle | **open** | Mounted-card local toggling works, but the required off-route navigate-then-toggle scenario fails in live Electron; see blocking finding F4 and `review-r2-help-offroute-probe.txt`. |
| F5 — immediate-operation `ERROR_SURFACE` | resolved | `putNow` maps validation/API failures to the banner and `runSettingsAction` maps API/IPC/Error rejections (`useSettingsPage.ts:117-153`). Browse, apply, and MCP handlers all execute inside that wrapper (`SettingsPage.tsx:97-171`); IPC registration throws failed envelopes before renderer resolution (`ui/src/main/index.ts:341-348`). |
| F6 — weak/misleading tests | **open** | Settings behavior coverage improved and Wave 4/6 passes, but AC-23.17 still has no route-transition behavior assertion and demonstrably false-passes F4. |

### Additional Focus Recheck

- `randomUUID` is restored in `ui/src/main/index.ts:1` and is used by main boot paths.
- MCP access status crosses into the renderer only as `{ tokenPresent: boolean }` (`ui/src/main/ipc.ts:366-368`; `ui/src/renderer/src/env.d.ts:26-32`). `copy-mcp-config` writes the token to the clipboard in main and returns only `{ ok: true }` (`ui/src/main/ipc.ts:343-355`; `copy-mcp-config.test.ts:4-27`). No MCP token value was found in Settings renderer state, props, or DOM.
- All DOWNLOADER/TRANSCRIPT/TTS named leaves are rendered; the Appearance theme uses `theme-dark-btn` / `theme-light-btn` rather than a `settings-leaf-theme` test ID, which is outside Round 1 F1's named scope and is behaviorally wired.

### Commands Executed

| Command / check | Result | Receipt |
|-----------------|--------|---------|
| `git status --short` | unavailable: snapshot is not a Git worktree | `C:/Temp/av-kit/review-r2-git-status.txt` |
| Live `settings-leaf-*` census and targeted code searches | all Round 1 F1 downloader/transcript/TTS leaves present; main UUID/help/error/security wiring located | `C:/Temp/av-kit/review-r2-leaf-census.txt`; `review-r2-leaves-search.txt`; `review-r2-routing-errors-secrets.txt` |
| Focused Vitest: settings, help, readiness, GUI audit, MCP-copy | 24 passed; React `act(...)` warnings present | `C:/Temp/av-kit/review-r2-focused-vitest.txt` |
| Full Vitest | 164 passed | `C:/Temp/av-kit/review-r2-full-vitest.txt` |
| `npm --prefix ui run typecheck` | pass | `C:/Temp/av-kit/review-r2-typecheck.txt` |
| `npm --prefix ui run lint` | **fail: 2 errors** | `C:/Temp/av-kit/review-r2-lint.txt` |
| `npm --prefix ui run build` | pass | `C:/Temp/av-kit/review-r2-build.txt` |
| Registered Wave 4/6 control census | pass, 23 enforced | `C:/Temp/av-kit/review-r2-e2e-census.txt` |
| Focused Electron Wave 4/6 | 5 passed | `C:/Temp/av-kit/review-r2-e2e-wave4-wave6.txt` |
| Off-route `help:toggle` Electron probe | **fail: navigated to Settings but remained collapsed** | `C:/Temp/av-kit/review-r2-help-offroute-probe.txt` |

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 Live runtime evidence | partial | Real Electron Wave 4/6 passes, but the added off-route AC-23.17 probe fails. |
| IR-3 Error mapping completeness | pass for Round 1 scope | Immediate PUT, browse, apply, and MCP rejection paths converge on `runSettingsAction` / banner reporting. |
| IR-4 Fix generalization | fail | Help toggling was fixed only for already-mounted cards; navigation delivery remained unverified and broken. |
| IR-5 Test rigor audit | fail | `settings-page.test.ts` 🟡 Adequate/Strong mixed; `setup-readiness.test.ts` 🟢 Strong behavior but lint-invalid import; `help-card.test.ts` AC-23.17 🔴 Weak for integrated delivery; `gui-actions-audit.test.ts` 🟢 Strong static contract; `settings.test.ts` 🟡 Adequate; `help-search.spec.ts` 🟢 Strong for search but does not cover palette delivery. |
| IR-6 Boundary/security coverage | pass for reviewed boundaries | Strict settings schemas remain; MCP status/copy return shapes do not expose the MCP token to renderer. |
| IR-7 AC coverage integrity | fail | AC-23.17 appears in artifacts but its required off-route integration behavior is not delivered or tested. |
| DR-7 Evidence freshness | fail | Reproduced lint result contradicts the handoff's clean-gate claim. |

### Final Verdict

`changes_required` — F1, F2, F3, and F5 are resolved, and the corrected implementation passes 164 Vitest tests, build, typecheck, the 23-control census, and 5 focused Wave 4/6 Electron tests. Approval is still blocked by the evidence-backed High F4 failure of AC-23.17: off-route palette delivery navigates but does not toggle the destination HelpCard. F6 remains open because current tests false-pass that defect, and F7 records the independently reproduced lint-gate failure.

### Required Follow-up

1. Make off-route `help:toggle` delivery occur after the destination HelpCard mounts and add a behavioral AppShell/Electron regression test.
2. Replace the lint-invalid Node SQLite imports and rerun the exact lint/build/readiness/Wave 4/6 commands.
3. Return the rolling file to `corrections_applied` for Round 3 recheck; do not create a new review file.

### Residual Risk

The focused Electron tests continue to use the approved renderer fetch seam rather than live FastAPI dependencies. That declared boundary is accepted for this review. The remaining blocking risk is narrower and reproduced: global help delivery loses the toggle across navigation.

---

## Corrections Applied (2026-08-21 / after Round 2)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F4 | Off-route help:toggle lost across navigate | `HELP_COMMANDS.queueToggleAfterNavigate` + HelpCard mount consume of `HELP_PENDING_TOGGLE_KEY`; AppShell queues when path not in helpRoutes | Unit pending-toggle; W6-3 E2E |
| F6 | Tests false-passed F4 | W6-3 Electron + pending-mount Vitest | `help-search.spec.ts` W6-3; help-card unit |
| F7 | `require('node:sqlite')` lint | Static `import { DatabaseSync } from 'node:sqlite'` in readiness + test | eslint max-warnings 0 |
| boot | Missing `homedir` import after extract | Restored `import { homedir } from 'node:os'` | tsc clean |

Receipt: `C:/Temp/av-kit/meu23-r2-fix.txt` (tsc/eslint/vitest/build + Wave 4/6 6 passed). Awaiting Round 3.

---

## Round 3 Recheck (2026-08-21)

### Intent Anchor

This recheck verifies that the Round 2 corrections complete the required off-route `help:toggle` delivery, add a discriminating Electron regression test, restore the mandatory clean lint gate, and preserve the already-resolved MEU-23 settings/readiness/error/security behavior. The current implementation achieves that intent within the approved renderer-seam boundary.

### Findings First

No blocking findings. The reviewed corrections expose no evidence-backed High or Critical runtime, contract, persistence, security, or false-claim defect; `findings_count` is therefore `0`.

### Prior Finding Closure

| Finding | Recheck result | Evidence |
|---|---|---|
| F4 — off-route HelpCard toggle | ✅ Closed | `AppShell` detects routes without a mounted HelpCard, queues one pending toggle, and navigates to Settings (`ui/src/renderer/src/components/layout/AppShell.tsx:117-122`; `settings-commands.ts:10-22`). `HelpCard` consumes and removes that intent on mount before toggling its persisted state (`HelpCard.tsx:52-61`). W6-3 starts on an off-route hash with Settings Help collapsed and asserts navigation plus `aria-expanded="true"` (`ui/tests/e2e/help-search.spec.ts:42-63`); the live Electron recheck passed 1/1 and the complete Wave 4/6 run passed 6/6. |
| F6 — tests false-passed F4 | ✅ Closed | The pending-before-mount unit test asserts both the resulting ARIA state and removal of the queued intent (`ui/tests/unit/help-card.test.ts:116-130`). W6-3 exercises the full AppShell route transition in compiled Electron, so the Round 2 failure scenario is now behaviorally discriminated. |
| F7 — lint-invalid `require('node:sqlite')` | ✅ Closed | Both production and test use static `DatabaseSync` imports (`ui/src/main/setup-readiness.ts:14`; `ui/tests/unit/setup-readiness.test.ts:4`). Live `npm run lint` completed with exit 0 and no warnings/errors (`C:/Temp/av-kit/review-r3-lint.txt`). |
| Boot imports | ✅ Closed | Main boot statically imports both `randomUUID` and `homedir` (`ui/src/main/index.ts:1-3`); live TypeScript no-emit completed with exit 0 (`C:/Temp/av-kit/review-r3-typecheck.txt`). |

### F1-F5 Regression Status

| Prior finding | Round 3 status | Evidence |
|---|---|---|
| F1 — complete settings leaves | resolved | The full 165-test Vitest run includes the settings renderer assertions, and W4-1 through W4-3 passed in compiled Electron (`review-r3-full-vitest.txt`; `review-r3-e2e-wave4-wave6.txt`). No correction touched or removed the complete SettingsPage leaf surface. |
| F2 — setup-readiness producers/deep-links | resolved | The readiness implementation retains descriptor parsing, SQLite `tts.models_directory`, app-data fallback, regular-file rejection, and write/port probes (`ui/src/main/setup-readiness.ts:23-128`); all 5 focused readiness tests are included in the 165/165 green run. |
| F3 — non-recursive `settings:check_deps` | resolved | SettingsPage remains the action owner, and the full settings suite plus W4-3 passed without renderer failure or recursive redispatch (`ui/src/renderer/src/features/settings/SettingsPage.tsx:72-87,164-166`; `review-r3-e2e-wave4-wave6.txt`). |
| F4 — HelpCard palette delivery | resolved | Off-route queue/mount consumption and live W6-3 are closed as detailed above. |
| F5 — immediate-operation error surface | resolved | `runSettingsAction` remains the shared API/IPC rejection path and wraps browse/apply/MCP/theme operations (`ui/src/renderer/src/features/settings/useSettingsPage.ts:138-165`; `SettingsPage.tsx:98-171,605-615`). The full settings tests remain green. |

### Security and Import Recheck

- MCP access status crosses the preload boundary only as `{ tokenPresent: boolean }` (`ui/src/main/ipc.ts:368`; `ui/src/renderer/src/env.d.ts:32`), and Settings renders only `yes`/`no` (`SettingsPage.tsx:717-718`). The main-process `copy-mcp-config` channel retains the secret and returns only `{ ok: true }`; no MCP token value is present in renderer state, props, or DOM.
- `randomUUID` and `homedir` are both present in `ui/src/main/index.ts:1-3`. The readiness module and test contain no CommonJS `require()` use for `node:sqlite`.

### IR-5 Test Rigor Recheck

| Test file | Grade | Round 3 result |
|---|---|---|
| `ui/tests/unit/help-card.test.ts` | 🟢 Strong for F4/F6 | Asserts mounted local toggle behavior, pending-before-mount state transition, queue removal, ARIA state, and storage behavior. |
| `ui/tests/e2e/help-search.spec.ts` | 🟢 Strong | W6-3 reproduces the exact Round 2 off-route failure setup and asserts both destination navigation and expanded HelpCard state in real Electron. |
| `ui/tests/unit/setup-readiness.test.ts` | 🟢 Strong | Exercises descriptor negative cases, SQLite-configured models path, regular-file rejection, and producer outcomes; 5/5 passed inside the full run. |
| `ui/tests/unit/settings-page.test.ts` | 🟢 Strong for prior F1/F3/F5 paths | Behavioral controls, command-count, action, and MCP containment assertions remain green. React emitted `act(...)` warnings during the full run, but no false-pass of a material behavior was demonstrated. |
| `ui/tests/e2e/settings.test.ts` | 🟢 Strong | W4-1–W4-3 validate Settings routing/cards and actuate browse/apply/dependency flows in compiled Electron; 3/3 passed. |

### Commands Executed

| Command / sweep | Result | Receipt |
|---|---|---|
| `npm run test` | 29 files, 165 tests passed | `C:/Temp/av-kit/review-r3-full-vitest.txt` |
| `npm run lint` | exit 0; zero warnings/errors | `C:/Temp/av-kit/review-r3-lint.txt` |
| `npm run typecheck` | exit 0 | `C:/Temp/av-kit/review-r3-typecheck.txt` |
| Focused W6-3 Playwright with output under `C:/Temp/av-kit/` | 1 passed | `C:/Temp/av-kit/review-r3-e2e-w6-3.txt` |
| Full Wave 4/6 Playwright with output under `C:/Temp/av-kit/` | 6 passed | `C:/Temp/av-kit/review-r3-e2e-wave4-wave6.txt` |
| Exact source/import/security searches | Pending-toggle path, static imports, and MCP status-only boundary confirmed | `C:/Temp/av-kit/review-r3-line-evidence.txt`; `review-r3-import-security-search.txt`; `review-r3-renderer-token-census.txt` |
| Compiled-output correction census | Existing Electron build contains pending-toggle delivery and static `DatabaseSync` wiring | `C:/Temp/av-kit/round3-out-correction-search.txt` |

`git diff` remains unavailable because `P:/av-kit` is not a Git repository. To honor the user's review-only write scope, this recheck did not run the repository-writing build command; instead it verified the correction in the existing compiled output before running Playwright against it.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass within approved boundary | Real Electron ran W6-3 and the complete Wave 4/6 set against compiled output; 1/1 and 6/6 passed. |
| IR-2 Stub behavioral compliance | N/A | No repository/UoW stub is introduced by this MEU; the approved E2E renderer fetch seam remains the declared boundary. |
| IR-3 Error mapping completeness | pass for reviewed UI actions | The shared immediate-operation error surface remains wired and covered by the green settings suite. |
| IR-4 Fix generalization | pass | Rechecked queued delivery, mount consumption, both relevant test layers, all UI lint targets, boot imports, prior F1-F5 paths, and MCP containment. |
| IR-5 Test rigor audit | pass | W6-3 now fails the exact Round 2 broken behavior; no scoped test remains 🔴 Weak. |
| IR-6 Boundary/security coverage | pass | Strict settings schemas remain; MCP renderer boundary exposes presence only, not the token value. |
| IR-7 AC coverage integrity | pass | AC-23.17 now has unit and compiled-Electron lifecycle proof; prior AC coverage remains green. |
| AV-1 Failing-then-passing proof | pass | Round 2 captured the live off-route failure; Round 3 W6-3 passes the same collapsed-destination scenario. |
| AV-2 No bypass hacks | pass | The E2E dispatches the real global event through AppShell and observes the destination HelpCard rather than inspecting source text. |
| AV-3 Changed paths exercised by assertions | pass | Queue production, mount consumption, queue removal, route transition, and final ARIA state are asserted across unit and E2E. |
| AV-4 No skipped/xfail masking | pass | Full Vitest and focused Playwright runs completed normally; no skip/only masking appeared. |
| AV-5 No unresolved placeholders | pass for correction scope | No placeholder was introduced on the reviewed correction paths. |
| AV-6 Source-backed criteria | pass | Corrections map directly to AC-23.17 and Round 2 findings F4/F6/F7. |

### Out-of-Contract Observations

- The full Vitest run emits React `act(...)` warnings in SettingsPage tests. This is non-blocking test hygiene: the reviewed behaviors have discriminating assertions and compiled-Electron coverage, and no material false-pass was demonstrated.

### Final Verdict

`approved` — F4, F6, and F7 are closed with direct source evidence and fresh behavioral receipts; F1-F5 remain resolved; lint and typecheck are clean; `randomUUID`/`homedir` boot imports are present; and the MCP token value does not cross into renderer. No evidence-backed High or Critical finding remains.

### Residual Risk

The Wave 4/6 tests continue to use the approved renderer fetch seam instead of live FastAPI dependencies. That declared boundary is accepted for MEU-23. The React `act(...)` warnings should be cleaned up in future test maintenance, but they do not block this verdict.
