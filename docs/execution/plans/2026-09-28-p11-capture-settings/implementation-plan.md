---
project: "2026-09-28-p11-capture-settings"
date: "2026-09-28"
source: "docs/build-plan/11-page-layout.md"
meus: ["MEU-57", "MEU-58"]
status: "approved"
template_version: "2.2"
---

# Implementation Plan: Phase 11 Capture and Settings (Phase 11 exit)

> **Project:** `2026-09-28-p11-capture-settings`
> **Build plan:** `docs/build-plan/11-page-layout.md`: §Capture page layout, §Settings page layout, §Decision register CP1–CP6 and ST1–ST7, §Test-ID migration CP 1–24 and ST 1–35, §Shared layout primitives
> **Grouping:** `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md`, Session 26. This is the Phase 11 **exit** session and runs the phase gate.
> **Status:** `approved` by the independent plan review, Round 2 (user-directed Fable 5.1 subagent; see `.agent/context/handoffs/2026-09-28-p11-capture-settings-plan-critical-review.md`). Execution waits for a direct human message, the OQ-1..OQ-5 decisions and `SEQUENCING_GATE`.

## Goal

Deliver Session 26 as grouped:

- **MEU-57** recomposes the Capture page into a header row (Capture button with the hotkey key cap, plus a Settings disclosure), a 200 px filmstrip, a viewport toolbar with the tool segment and the per-shot actions, and inline confirm strips.
- **MEU-58** recomposes the Settings page into a 960 px two-column layout. It adds a sticky section rail (Pages / App / Setup) tracked by `IntersectionObserver`, a 168 px label/control grid, path+Browse rows, per-section save-mode captions, and Dependencies/Readiness/MCP shown as chip lists.
- After both MEUs are independently approved, the Phase 11 exit gate runs across the whole repository, and SSOT, hub, grouping and focus are updated to mark Phase 11 complete.

Both MEUs are bound by `COMPOSITION_LOCK`. That means the same IPC, API payloads, persisted mutations, enablement and save behavior, and every existing test ID. The only exceptions are the canon decisions that explicitly change presentation, plus the human decisions in §Open Questions.

The worktree baseline is the branch HEAD at execution time, which row 1 records. Planning started from `0f51036`. Treat the live files as the baseline and reset nothing.

## Sequencing gate: Session 25 comes first

`SEQUENCING_GATE` is the single authority for when this plan may execute. It uses this predicate:

```
plan_checks.py meu-state --expect MEU-50..56=approved
```

Today it **refuses**, because MEU-55 and MEU-56 are `pending`. The planning-time receipt shows `REFUSED: MEU-55: status 'pending' != 'approved'; MEU-56: status 'pending' != 'approved'`. Three sources order this session after Session 25:

- Grouping §Sessions: Session 26 is "Phase 11 **exit**".
- Grouping §Session 26: "Settings is last on purpose … section names and save-model captions are only stable once the five page MEUs have landed".
- `.agent/context/current-focus.md`: "Session 25 `p11-transcript-tts` (MEU-55–56) is next".

The formal dependency of MEU-57/58 is MEU-51 only, and that is approved. The *phase gate*, however, cannot pass while any Phase 11 MEU is unapproved. Task row 1 runs `SEQUENCING_GATE` and stops execution if it refuses. OQ-1 records the alternative (run Session 26 first and move the phase exit to Session 25), which needs a human decision and a grouping amendment.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json are absent (ls: No such file or directory); no headroom install on PATH. Scope is TSX page composition, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Re-evaluate before execution (task row 1).

## Harness, driver and reviewer route

- **Driver:** Claude Code. Planning ran in the web container (Linux, Bash tool); the execution host is decided by OQ-5 (`EXECUTION_HOST`).
  - `.agent/context/harness.local.md` §Claude Code sets `fresh_worker: Agent tool + .claude/agents/` and does **not** override `plan_to_exec_gate`. The Claude Code row in `.agent/docs/harness-profiles.md` therefore applies: `plan_to_exec_gate: human`.
  - Reviewer `approved` does not start execution. A direct user message does.
- **Shell and receipts:** `RECEIPTS_DIR` and `E2E_WRAP` must be **exported**, because several rows expand them inside single-quoted `bash -c`. Commands use POSIX form, `> "${RECEIPTS_DIR}/p11cs-<id>.txt" 2>&1; code=$?; …; exit $code`. `tools/lint_task_contract.py` accepts `${RECEIPTS_DIR}` and `code=$?`.
  - `RECEIPTS_DIR` is `C:/Temp/av-kit` on the Windows host, or an absolute directory in the session scratchpad on the web container.
  - Row 1 records the value.
- **RTK:** AGENTS §RTK makes `rtk proxy` mandatory, and this web container has no `rtk` on PATH. Row 1 proves `rtk --version` before any other command. A missing RTK is a `missing-dependency` `[B]` with its exact diagnostic, not a silent drop of the prefix.
- **Electron on Linux:** `E2E_WRAP` is `xvfb-run -a` when `DISPLAY` is unset, and empty on Windows. `ELECTRON_RUN_AS_NODE` is removed with `env -u` before every launch (`.agent/docs/commands.md`).
- **`EXECUTION_HOST` (OQ-5):** the full Electron wave cannot pass on Linux. `ui/tests/e2e/capture-picker.test.ts:25` hard-requires `native/region-picker-stub/publish/avkit-region-picker-stub.exe`, a Windows build output that has no platform guard. RTK is also absent here. The recommended host is therefore the Windows host (Mat's `P:/av-kit`) for every row, using Git Bash for the POSIX commands, with `RECEIPTS_DIR=C:/Temp/av-kit`. That is where the Session 24 baseline of 95 Electron tests passed. Row 1 checks the host prerequisites (`rtk`, `node`, the stub `.exe`) and stops if any is missing. If the web container is chosen anyway, the capture-picker cases and every `rtk proxy` row would be `[B]` missing-dependency, and **Phase 11 could not be declared exited**. OQ-5 records this.
- **Reviewer (USER_EXPLICIT, same-vendor exception):** the user directed on 2026-09-28: "For reviewer instead of doing codex cli dispatch since we are in web Claude code platform use subagent to fable 5.1 high model".
  - The route is recorded in [human-review-decision.md](human-review-decision.md). The author is Anthropic (Claude Opus 5.5) and the reviewer is Anthropic (Fable 5.1, separate subagent context).
  - This departs from PROFILE B1 (Codex) and AGENTS §Dual-Agent vendor diversity. It is disclosed, not hidden. The author never writes a verdict.
  - The Agent tool cannot set reasoning effort per call. "high" is requested in the prompt and cannot be enforced; the decision file records this limit.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-57 | `.agent/context/handoffs/2026-09-28-p11-capture-settings-MEU-57-handoff.md` |
| MEU-58 | `.agent/context/handoffs/2026-09-28-p11-capture-settings-MEU-58-handoff.md` |
| Plan review | `.agent/context/handoffs/2026-09-28-p11-capture-settings-plan-critical-review.md` (rolling) |
| Project review | `.agent/context/handoffs/2026-09-28-p11-capture-settings-implementation-critical-review.md` (rolling) |

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Sequencing gate, prerequisites, context-tool recheck, source freeze | — | `shared` | `walkthrough.md` prerequisite section; `p11cs-prereq*.txt` |
| WP-2 | MEU-57 Capture: tests-first Red → Green → targeted gate → handoff | WP-1 | `compact_continue` | MEU-57 handoff and receipts; re-read `task.md` and the handoff before WP-3 |
| WP-3 | MEU-58 Settings: tests-first Red → Green → targeted gate → handoff | WP-2 | `compact_continue` | MEU-58 handoff and receipts; re-read `task.md` and the handoff before WP-4 |
| WP-4 | Phase 11 exit gate (full D6), H1 state, independent execution review | WP-3 | `shared` | Gate receipts, rolling review |
| WP-5 | H2: `POST_REVIEW_STATE`, reflection, metrics, commit-message draft | WP-4 | `shared` | Reflection, metrics row, SSOT/hub/grouping/focus |

WP-2 goes before WP-3 because MEU-58 renders the Capture settings section that MEU-57's disclosure duplicates (CP3). Doing Capture first means both copies are checked against a stable `useCaptureSettings` contract. The builder rows are pinned to classes, not models. Readonly validation rows may use `delegate_to: av-kit-verifier` because `fresh_worker` resolves for Claude Code.

---

## User Review Required

> [!IMPORTANT]
> Five items need a human decision. See §Open Questions for the options tables and recommendations.
>
> - **OQ-1:** run order (Session 25 first).
> - **OQ-2:** Capture tools are disabled when no shot is selected (CP5 vs. `COMPOSITION_LOCK`).
> - **OQ-3:** the Capture Settings disclosure starts closed.
> - **OQ-4:** the listed test-expectation migrations (`TEST_MIGRATIONS` TM-1..TM-10).
> - **OQ-5:** the execution host (Windows host recommended; the web container cannot run the full gate).
>
> The execution message must say which option was chosen for each. A plain "proceed" is read as accepting every ✅ recommendation, and that acceptance is recorded as `Human-approved` in `walkthrough.md`.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined here once. Everything else refers to it by name.

| Name | Single authority and definition |
|---|---|
| `COMPOSITION_LOCK`, `PRESERVED_TESTIDS` | `docs/build-plan/11-page-layout.md` §Scope and §Test-ID migration (CP 1–24, ST 1–35). |
| `SEQUENCING_GATE` | §Sequencing gate above. |
| `PAGE_CAP_CAPTURE` | `w-full max-w-[var(--layout-page-max-width)]` (72rem, `styles.css:70`). This is the Downloader/Convert pattern (`DownloaderPage.tsx:527`). |
| `SETTINGS_CAP` | A 960 px (`60rem`) grid: `176px minmax(0,1fr)` columns with a 20 px gap. Source: canon §Shared layout primitives and settings mockup §04. `max-w-3xl` goes away. |
| `SETTINGS_SECTION_SET` | The 11 sections in DOM order, as `key → section testid → rail group → save mode`:<br>• `download` → `download-settings` → Pages → autosave<br>• `transcript` → `transcript-settings` → Pages → autosave<br>• `tts` → `tts-settings` → Pages → autosave<br>• `convert` → `convert-settings` → Pages → explicit<br>• `capture` → `capture-settings` → Pages → explicit<br>• `console` → `console-settings` → App → autosave<br>• `appearance` → `appearance-settings` → App → immediate<br>• `startup` → `start-at-sign-in-panel` → App → immediate-os (**conditional**)<br>• `dependencies` → `dependencies-section` → Setup → none<br>• `readiness` → `readiness-card` → Setup → readiness-count<br>• `mcp` → `mcp-access-card` → Setup → none<br>The canon row ST 4 says "9 section ids". The live page has 10 always-rendered sections plus the conditional MEU-61 panel (`SettingsPage.tsx:192–895`). All 11 keep their IDs. The ST 4 label copies the mockup §05 cell word for word, and `layout-canon.test.ts:130–147` (AC-50.4) enforces that match. So the canon text is **not edited**: the discrepancy is recorded in the MEU-58 handoff only. |
| `SAVE_MODE_CAPTIONS` | Visible text for each mode:<br>• autosave → "Saves as you type"<br>• explicit → "Save required"<br>• immediate → "Applies immediately"<br>• immediate-os → "Applies immediately (OS)"<br>• readiness-count → `READINESS_COUNT`<br>• none → no caption<br>Code sources: autosave is `schedulePut` (`useSettingsPage.ts:85–124`); explicit is the drafts in `useConverterSettings`/`useCaptureSettings`; immediate is `putNow('ui', …)` (`useSettingsPage.ts:126–144`), which flushes through `flushPut`'s theme branch (`:67–79`); immediate-os is `loginItemSet` (`StartAtSignInControl.tsx:47–61`). Wording comes from mockup §02. |
| `READINESS_LOADED` | Both the `['setup','readiness']` query and the `/health/dependencies` query have `data !== undefined`. |
| `READINESS_COUNT` | "n of 4 ready", rendered **only** when `READINESS_LOADED`. `n` counts the true values among `descriptorPresent`, `portOk`, `modelsDirWritable` and `ffmpeg.available`. Before load there is no count (ST7). |
| `CHECKBOX_COPY_SOURCES` | The only explanation lines allowed (ST5). Checkboxes not listed get no line and keep the HelpCard (`skip_existing`, `close_to_tray`, `audio_only`):<br>• `archive_tracking`: "Skip previously downloaded videos" (`06-gui.md:963`)<br>• `yt_dlp_debug`: "Show yt-dlp debug messages in console" (`:964`)<br>• `console_visible`: "Show console panel on startup" (`:1004`)<br>• `copy_to_clipboard`: "After successful save" (`09-screenshot-capture.md:554`)<br>• `log_to_file`: keeps its existing "Persist to …" line and fixed-path note (`SettingsPage.tsx:746–749`) |
| `NUMBER_HINT_SOURCES` | The only hints allowed (ST4). No new `min`/`max`/`step` attribute is added. Only the existing `speed` range keeps `0.5/2.0/0.1`:<br>• `delay_between_requests`, `retry_delay`, `pause_between_batches`: "seconds" (`06-gui.md:972,974,976`)<br>• `playlist_end`: "0 = no limit" (`:977`)<br>• `max_words_per_document`: "Split compiled Markdown at this word count" (`:978`)<br>• `chunk_max_chars`: "Smart TTS chunking threshold" (`:989`)<br>Every other number gets no hint. |
| `CAPTURE_OVERLAY_DIRTY` | The existing predicate at `CapturePage.tsx:221–223`: annotations differ from `saved`, **or** the text draft is non-empty. |
| `FILMSTRIP_LABEL_RULE` | Three parts:<br>• **Visible name:** `display_name` with a leading `^\d{4}-\d{2}-\d{2}[ _]` prefix removed. If removing it would leave an empty string, show the full `display_name`.<br>• **Second line:** `created_at` rendered as local `HH:MM:SS`.<br>• **Accessible name:** the full `display_name` stays in the thumbnail `alt` and the item's accessible name.<br>The full `display_name` is also rendered as a visually hidden (`sr-only`) span inside the item, so the item's text content still contains the full file name (`capture-picker.test.ts:218–221` `toContainText` stays green, no migration). `created_at` is already carried by `CaptureShotOut` (`packages/api/src/avkit_api/schemas/captures.py:125`). Note that picker files are named `%Y-%m-%d_%H-%M-%S.png` (`services/capture.py:44,476`), so their visible name becomes `HH-MM-SS.png`. That is literal CP4 behavior. |
| `CONFIRM_EXCLUSIVITY` | While `confirm !== null`, filmstrip items and `capture-delete` are disabled, so a second confirmation cannot replace a pending one. The portal backdrop enforces this today (`CapturePage.tsx:927–1008`). |
| `NEW_TESTIDS` | Registered in `ui/tests/e2e/test-ids.ts` **after** the MEU-54 block, so the AC-51.6 pre-marker hash is unchanged:<br>• MEU-57: `capture-settings-toggle`, `capture-hotkey-keycap`, `capture-shot-info`, `capture-confirm-strip`, `capture-filmstrip-name`, `capture-filmstrip-time`<br>• MEU-58: `settings-rail`, `settings-rail-{key}` for each `SETTINGS_SECTION_SET` key, `settings-mode-{key}` for each key whose mode ≠ none, `settings-readiness-count`, `settings-rail-dot-{convert,capture,readiness}` |
| `SETTINGS_SOURCE_LOCATION` | All Settings section markup stays in `features/settings/SettingsPage.tsx`, or in new **top-level** `features/settings/*.tsx` files only. Section markup for Convert/Capture stays in `SettingsPage.tsx`. This keeps the source-string contracts green unchanged: AC-33.16 (`convert-page.test.ts:524–546`), AC-39.15 (`capture-page.test.ts:343–364`), AC-23.19/AC-61.21 (`gui-actions-audit.test.ts`, a non-recursive `readdirSync`) and the settings-page source contract (`settings-page.test.ts:489–494`). |
| `CAPTURE_SOURCE_LOCATION` | The per-shot action group (`capture-save`, `capture-open-file`, `capture-open-folder`, `capture-delete`) and the `capture-empty` block, with its text "Press F2 or Capture region", are **rendered in `CapturePage.tsx`**. They are passed into `CaptureViewport` as ReactNode slot props (`actions`, `emptyState`), and the viewport only places them. This keeps the source contracts `capture-page.test.ts:278,296,301–302,311–312` (`readRequired(pagePath)`) green unchanged. |
| `CAPTURE_READY_SIGNAL` | `capture-draw-surface` carries `data-overlay-ready="true"` iff the existing `overlayReady && imageEpoch > 0` state holds (`CapturePage.tsx:224–233`). This is an additive attribute and changes no behavior. It replaces "`capture-save` enabled on a clean shot" as the readiness wait, because CP1 unmounts Save on a clean shot. |
| `MCP_TOKEN_TEXT` | The token chip label is exactly "Token present: yes" or "Token present: no", on `mcp-token-present`. This keeps `settings-page.test.ts:483` (`/yes\|no/`) green unchanged. |
| `API_SCOPE_PATHS` | `packages/` and `mcp-server/`. This single path set is used by the H1-4 scope audit. |
| `MIGRATION_CENSUS` | Task row 2. Before any test is edited, run an unfiltered `rg` over `ui/tests` for every ID, literal and class this plan moves or changes: `capture-save`, `capture-tool-`, `capture-inbox-path`, `capture-hotkey`, `capture-page-save`, `capture-filmstrip`, `capture-empty`, `capture-status`, `capture-chrome`, `createPortal`, `display_name`, `mcp-token-present`, `settings-page`, `max-w-3xl`, `readiness-`, `settings-leaf-cookie_mode`, `apply-defaults-btn`, `theme-`, `settings-log-file-path`, `components/ui/`. Every hit gets a disposition in `walkthrough.md`: **unaffected**, **TM-n** (listed below), or **new-contradiction**. Any new-contradiction stops execution for a human decision. |
| `TEST_MIGRATIONS` | The known set of pre-existing assertions this plan changes (OQ-4). Completeness is enforced by `MIGRATION_CENSUS`, which stops on anything unlisted, each with its canon source. Each needs the human decision before its edit.<br>• **TM-1** `layout-primitives.test.ts:218–224` AC-51.7: remove `CapturePage` and `SettingsPage` from the "must not import primitives" loop, and add a per-page positive-adoption check: `CapturePage` imports `Disclosure`, `StatusChip` and `PathRow`; `SettingsPage` imports `SegmentedControl`, `StatusChip`, `FormRow` and `PathRow`. The existing Downloader/Convert loop (`:225–230`) is unchanged. Transcript and TTS **stay restricted** until Session 25. (Canon §Shared layout primitives.)<br>• **TM-2** `capture-inbox.test.ts` W9-3 and W9-5 (`:202–256`, `:315–330`): `capture-save` is expected to have count 0 with no shot, instead of visible and disabled. The force-click on Save in W9-3 is removed. (CP1.)<br>• **TM-3** W9-3: tools are expected disabled with no shot, and the no-force tool clicks are removed. (CP5; only if OQ-2 = A.)<br>• **TM-4** W9-3 and `capture-picker.test.ts`: click `capture-settings-toggle` before touching `capture-inbox-path` or the hotkey controls. Setup step only; no assertion change. (OQ-3 = A.)<br>• **TM-5** Unit helper `openSelectedSurface()` (`capture-page.behavior.test.ts:257–271`, used by the AC-59/60 cases): the readiness wait on "`capture-save` not disabled" becomes a wait on `CAPTURE_READY_SIGNAL` plus `queryByTestId('capture-save') === null` (the shot is clean). (CP1.)<br>• **TM-6** `capture-page.behavior.test.ts:455`, `:664`, `:682`: on a shot that is clean at that moment (failed detail load; text tool pointerup before any character; pointerdown mid-gesture), "`capture-save` disabled" becomes "`capture-save` absent". Each site keeps its other assertions. (CP1: not dirty, so not mounted.)<br>• **TM-7** `capture-inbox.test.ts:412`, `:455`, `:516` (AC-59.12 and AC-60.12, on a clean shot, before and after reload): "`capture-save` enabled" becomes `CAPTURE_READY_SIGNAL` plus `capture-save` count 0. After the first mark, the tests assert `capture-save` enabled before clicking it; their later Save steps are unchanged. (CP1.)<br>• **TM-8** `capture-page.behavior.test.ts:430–436` (AC-59.8, detail held on clean shot-2): "`capture-save` disabled" while held becomes "absent". "Enabled" after release becomes `CAPTURE_READY_SIGNAL` plus `capture-save` absent. The zero-POST assertion is unchanged. (CP1.)<br>• **TM-9** `capture-page.behavior.test.ts:650` (AC-60.8, re-selecting a saved named-color mark leaves the shot clean): "`capture-save` enabled" becomes `CAPTURE_READY_SIGNAL` plus `capture-save` absent. (CP1.)<br>• **TM-10** `capture-page.behavior.test.ts:343` (AC-39.28): the tool button size class `h-9` becomes `h-7`, because the tool segment is sm per capture mockup §05 ("One segment of four sm buttons") and `Button.tsx:23`. The Capture region `h-9` (`:339`) is unchanged. (Spec §05 CP 17.)<br>**New-contradiction rule:** any other contradicted assertion found by `MIGRATION_CENSUS`, or later during execution, is **not** edited. Execution stops, lists it individually with its canon source, and waits for the human, following the Session 24 precedent (`2026-09-26-p11-queue-pages/implementation-plan.md:252`). |
| `GUI_RULES` | `.agent/docs/emerging-standards.md` G30–G37, E2 and UX1/UX2; `Button.tsx` (five variants, three sizes); the MEU-51 primitives; mockups §04. |
| `PHASE11_EXIT_PREDICATE` | `plan_checks.py meu-state --expect MEU-50..58=approved --plan docs/execution/plans/2026-09-28-p11-capture-settings` exits 0, **and** every D6 row in §Verification Plan item 4 exits 0 on one fresh tree, **and** `plan_checks.py counts` passes `COUNT_FLOORS`, **and** the post-H2 doc-test rerun (`DOC_READING_TESTS`) passes on the final tree. |
| `COUNT_FLOORS` | Vitest executed ≥ 597 with 0 failed, and Electron `expected` ≥ 95 with 0 unexpected or flaky. These are the Session 24 final counts (`current-focus.md`). Checked by `plan_checks.py counts` against the H1-2 JSON reports. |
| `DOC_READING_TESTS` | The tests that read hub, grouping or SSOT documents: `ui/tests/unit/layout-canon.test.ts`, `ui/tests/unit/queue-canon.test.ts` and `tests/tooling/test_framework_adoption.py` (found by `grep -rl` for `BUILD_PLAN`, `current-focus`, `session-grouping`, `meu-status` and `metrics.md`). They are re-run after every H1-3 and H2-2 document edit, because those edits come after the H1-2 gate. |
| `POST_REVIEW_STATE` | Produced after independent execution `approved`, in this order:<br>1. MEU-57/58 set to `approved` with this plan binding via `tools/meu_status.py`, then render and check.<br>2. Grouping Session 26 set to `approved` with the real folder.<br>3. Phase 11 hub row set to ✅ Completed, and the hub Next line set to the first entry of `meu_status.py next`.<br>4. `current-focus.md` updated to that next item.<br>5. One metrics row added.<br>6. `plan_checks.py post-review` asserts items 2–5 against the tool-derived next MEU.<br>7. `DOC_READING_TESTS` and `meu-state --expect MEU-50..58=approved` re-run. |

Each control AC below names three things: a production entrypoint, the observable to assert, and a negative oracle. Test titles carry their AC IDs.

For each MEU, **all** Vitest behavior and Electron assertions are written before its production edit. They are then run to an assertion Red that `plan_checks.py red` verifies. The helper refuses collection, build or launch failures, and any prefix without its own failing assertion. Its self-test covers 15 positive and adversarial cases: `p11cs-plan-checks-selftest.txt`, exit 0 at planning time.

Tests cannot be weakened to reach Green. Interaction uses `userEvent` (G37). Electron uses the existing renderer seams and DOM geometry at the default window size.

### MEU-57 — `gui-capture-layout`

#### Boundary Inventory

| Surface | Schema owner | Field constraints | Extra-field policy |
|---|---|---|---|
| Inbox/hotkey form (page disclosure) | `useCaptureSettings` → `PUT /settings/capture`, zod `.strict()` in `settings-schemas.ts`, `SettingsPutIn` (`ApiModel`, `extra="forbid"`) | Existing path/accelerator strings; explicit Save only; the recorder keydown handler is unchanged | Malformed body → 422 at the API. Page and Settings copies share one hook (CP3). |
| Overlay save / delete / open | `capture-commands.ts`: `POST /captures/{id}/annotate` (`AnnotationIn`), `DELETE /captures/{id}`, IPC `openPath` / `showItemInFolder` | Existing `canSave` gate (`CapturePage.tsx:224–233`); delete only after confirm | Unchanged. The confirm strip cancel issues zero requests. |
| Region capture | IPC `captureRegion` | No payload change | n/a (no body) |
| Hotkey status read | IPC `getHotkeyStatus` → `{accelerator, registered, inUse}` (`capture-hotkey.ts:17–40`) | The same single call per hotkey change; `registered` is now read | No new IPC channel. |

#### Acceptance Criteria

| AC | Type | Description and chain | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-57.1 | integration | `CapturePage` renders `capture-page` with `PAGE_CAP_CAPTURE`, HelpCard first, then a **header row**: `capture-region` (primary md), a muted "n shots · inbox {path}" text from the existing catalog/settings data, and a `Disclosure` whose toggle is `capture-settings-toggle` (`aria-expanded`). The panel holds `PathRow` (`capture-inbox-path` / `capture-inbox-browse`), the hotkey field and Change button (`capture-hotkey` / `capture-hotkey-change`, recorder unchanged), and `capture-page-save` (primary sm, label "Save settings", with `settings.saveClass` and dirty label). Save calls the same `settings.save()`. | Spec §Capture; CP3; mockup §02/§04/§05 | Toggle issues zero requests. Editing inbox issues zero PUTs until Save, then exactly one `PUT /settings/capture` with the same body shape. A caller ID on a wrapper instead of the input/button fails. |
| AC-57.2 | integration | `getHotkeyStatus` → `registered === true` → a `capture-hotkey-keycap` `<kbd>` inside `capture-region` showing the accelerator. The button's accessible name still starts with "Capture region". | Spec CP2 | With `inUse:true`/`registered:false`, or with status not yet loaded, no key cap renders. Exactly one `getHotkeyStatus` call per hotkey value (no added IPC). |
| AC-57.3 | integration | `capture-hotkey-banner` becomes a warn status line directly under the header: a `StatusChip` (warning, "Hotkey") plus the same `HOTKEY_IN_USE_TEMPLATE` sentence, shown only when `inUse`. The element stays mounted with its reserved `min-h-4` height, so W9-3's `toBeVisible` (`capture-inbox.test.ts:227`) stays green. | Spec §Capture; mockup §05 | With `inUse:false` the banner contains no chip and no text. The sentence is byte-identical to the template. |
| AC-57.4 | integration | `capture-filmstrip` is a 200 px aside with its own scroll (max ~420 px) and `aria-label="Captures"`. Each `capture-filmstrip-item` is a native button: 56×36 thumbnail, `FILMSTRIP_LABEL_RULE` name and time lines, `aria-current="true"` on the selected item, and a dirty dot on the selected item when `CAPTURE_OVERLAY_DIRTY`. Selection still routes through `chooseItem` (dirty confirm unchanged). `role="listbox"` from the mockup is **not** used, because the APG listbox pattern requires an arrow-key model that `COMPOSITION_LOCK` does not add (Research-backed: https://www.w3.org/WAI/ARIA/apg/patterns/listbox/). | Spec CP4; mockup §04 | `capture-filmstrip-name` for a name starting `2026-09-03 ` has text without the prefix, `capture-filmstrip-time` shows `HH:MM:SS`, and the full name stays in `alt` and the sr-only span. A name made only of the prefix falls back to the full name. The dirty dot is absent on a clean selection. |
| AC-57.5 | integration | The viewport toolbar in `capture-chrome` keeps `shrink-0`/`flex-nowrap` (`capture-page.behavior.test.ts:923–937`).<br>• **Left:** a tool segment of the five existing tool buttons (`capture-tool-select`, `-arrow`, `-box`, `-highlight`, `-text`), sm, with `aria-pressed`; then `capture-undo` / `capture-redo`.<br>• **Middle:** `capture-color` and `capture-stroke` with **visible** labels "Color" / "Stroke". All other chrome IDs and their conditions are unchanged.<br>• **Right:** `capture-save` (AC-57.6), `capture-open-file`, `capture-open-folder`, `capture-delete` (destructive sm), each with its existing `disabled` rule.<br>Tools are disabled with a `title` hint when `selectedId === null` (OQ-2 = A; UX2). | Spec CP5; mockup §05; UX2; G34 | With no shot, tool clicks cannot change `aria-pressed`. With a shot, clicking Box sets `aria-pressed` on Box only. Open-file/delete enablement exactly matches the W9-5 table. |
| AC-57.6 | integration | `capture-save` (rendered in `CapturePage.tsx` per `CAPTURE_SOURCE_LOCATION`) is **mounted iff `CAPTURE_OVERLAY_DIRTY`** and, when mounted, `disabled = !canSave` (unchanged). The label is "Save overlay •". It still calls the same annotate command once. The palette seam `setCaptureSaveAllowed`/`canSaveRef` is unchanged, so `capture:save` behaves as before. | Spec CP1 | On a clean shot `capture-save` is absent. Adding a mark mounts it. While a text draft is open it is mounted but disabled. One click → exactly one `POST …/annotate`. |
| AC-57.7 | integration | Both confirmations render as one inline `capture-confirm-strip` above the draw surface, replacing the portal. The existing messages are unchanged. Buttons: `capture-dirty-confirm` ("Confirm") or `capture-delete-confirm` ("Delete capture", destructive), plus the matching `…-cancel`. Focus moves to the strip's Cancel button when it opens (Research-backed: APG alert dialog guidance to focus the least destructive action, https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/). `CONFIRM_EXCLUSIVITY` holds. Confirm and cancel reuse the existing handlers. | Spec §Capture ("inline confirm strips"); mockup §05 CP 23–24 | Cancel on delete → zero `DELETE`. While a dirty strip is open, a click on another filmstrip item changes neither selection nor pending target. No `createPortal` remains in `CapturePage.tsx`. |
| AC-57.8 | integration | `capture-status` sits under the draw surface, keeps `h-5` and its existing content rule (error first, then gate messages). A separate muted `capture-shot-info` shows `display_name · W×H` for the selected shot. | Spec CP6 | With both an error and a selected shot, `capture-status` shows the error and `capture-shot-info` never contains error text. With no selection, shot info is empty. |
| AC-57.9 | integration | `capture-empty` (rendered in `CapturePage.tsx` and passed as the `emptyState` slot, per `CAPTURE_SOURCE_LOCATION`) moves inside `capture-viewport`, replacing the draw surface when `items.length === 0`, with the existing text. "Select a shot from the filmstrip." stays for the shots-but-no-selection case. | Spec §05 CP 13 | With shots present, `capture-empty` is absent. The draw surface is absent while empty. |
| AC-57.10 | integration | A written, wired real-Electron wave in `capture-inbox.test.ts` covers:<br>• header, key cap and disclosure toggle/Save<br>• filmstrip label/time/`aria-current`/dirty dot<br>• the disabled tool segment with no shot<br>• the Save-overlay mount rule<br>• the confirm strip (both kinds, cancel with zero requests)<br>• shot info vs. status<br>• the empty state inside the viewport<br>• filmstrip width ≈200 px at the default window size<br>Existing W9/AC-59/AC-60 cases stay green, amended only per TM-2..TM-4 and TM-7. `capture-picker.test.ts` stays unchanged apart from the TM-4 setup click. | E2; `create-plan.md` §4A | A unit-only substitute, a conditional early return (G36) or a dead moved control fails. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Zones, sizing, ID dispositions | Spec | Canon §Capture, CP1–CP6, §Test-ID migration CP 1–24; mockup §04 |
| Save overlay mount rule | Spec | CP1; `CAPTURE_OVERLAY_DIRTY` is existing code |
| Key cap condition | Spec + Local Canon | CP2; `registered` field of the existing IPC |
| Tools disabled without shot | Human-decision-required | CP5 vs. `COMPOSITION_LOCK`; OQ-2 |
| Disclosure initial state | Human-decision-required | Not locked by the canon; OQ-3 |
| Filmstrip semantics (no listbox role) | Research-backed | APG listbox URL above; composition lock forbids new keyboard model |
| Confirm strip focus and exclusivity | Research-backed + Local Canon | APG alert dialog; current portal behavior |
| Filmstrip name/time | Spec + Local Canon | CP4; `created_at`, `TIMESTAMP_FORMAT` |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | Header, disclosure, banner, confirm strip, status/shot info, empty state placement |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | Toolbar grouping, tool segment disabled state, labels, Save/actions moved in |
| `ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx` | modify | 200 px rows, `FILMSTRIP_LABEL_RULE`, `aria-current`, dirty dot |
| `ui/src/renderer/src/features/capture/capture-filmstrip-label.ts` | new | Pure `FILMSTRIP_LABEL_RULE` function |
| `ui/tests/unit/capture-filmstrip-label.test.ts` | new | Unit tests for the rule |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-57 behavior (additive); TM-5, TM-6, TM-8..TM-10 |
| `ui/tests/unit/layout-primitives.test.ts` | modify | TM-1 (after human decision) |
| `ui/tests/e2e/capture-inbox.test.ts`, `ui/tests/e2e/capture-picker.test.ts` | modify | AC-57.10; TM-2..TM-4, TM-7 |
| `ui/tests/e2e/test-ids.ts` | modify | MEU-57 `NEW_TESTIDS` after the MEU-54 block |

### MEU-58 — `gui-settings-layout`

#### Boundary Inventory

| Surface | Schema owner | Field constraints | Extra-field policy |
|---|---|---|---|
| Autosave leaves (downloader, transcript, tts, console) | `schedulePut` → zod `.strict()` `parseSettingsPut` → `PUT /settings/{ns}` → `SettingsPutIn` `extra="forbid"`; core bounds in `SETTINGS_KEY_TABLE` (`services/settings.py:58–74`) | Existing 300 ms debounce, empty-string filter, core `min_number=0` and speed 0.5–2.0 | Invalid → 422 surfaced through `SETTINGS_ERROR_EVENT`. No new field or bound. |
| Convert/Capture drafts | `useConverterSettings`, `useCaptureSettings` → `PUT /settings/converter` / `capture` | Explicit Save only | Same schemas. Editing issues zero PUTs. |
| Theme | `putNow('ui', {theme})` | `dark` / `light` | Same. |
| Startup | IPC `loginItemGet` / `loginItemSet` (MEU-61) | Unchanged; the panel reports support through a new callback prop (no new IPC) | n/a |
| Diagnostics actions | `check-deps-btn` → `SETTINGS_COMMANDS.checkDeps`; readiness links → `focusSection`; `copyMcpConfig({pinEndpoint})` | Unchanged | n/a |

#### Acceptance Criteria

| AC | Type | Description and chain | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-58.1 | integration | `settings-page` becomes the `SETTINGS_CAP` two-column grid: rail, then a content column holding h1, HelpCard, the error `<p role=alert>`, then all `SETTINGS_SECTION_SET` sections with their existing IDs. Below ~760 px of content width the rail becomes a horizontally scrolling row above the content. | Spec §Settings; ST 1–4; mockup §04 | Any of the 11 section IDs missing, or `max-w-3xl` remaining, fails. The error `<p>` stays under the HelpCard. |
| AC-58.2 | integration | The `settings-rail` nav has three labelled groups (Pages / App / Setup) with `settings-rail-{key}` entries in `SETTINGS_SECTION_SET` order. Activating an entry by click or Enter/Space scrolls its section into view and gives it focus (guarded `scrollIntoView`; `smooth` unless `prefers-reduced-motion`). The `startup` entry renders only when `StartAtSignInControl` reports it is mounted, via `onAvailabilityChange`, a prop added with no new IPC call. | Spec ST3; mockup §02/§04 | When unpackaged (E2E) the startup entry and panel are both absent. Rail activation issues zero network/IPC writes. |
| AC-58.3 | integration | The active entry (`aria-current="location"`) follows scroll through an `IntersectionObserver` rooted at the nearest scrolling ancestor (the AppShell `<main>`). The observer disconnects on unmount. **No-observer fallback:** when `IntersectionObserver` is undefined (jsdom), the first section is active initially and activation sets it directly. | Spec ST3 | Exactly one entry is ever current. In jsdom, rendering without a polyfill does not throw. In Electron, scrolling to MCP makes `settings-rail-mcp` current without a click. |
| AC-58.4 | integration | Each section header shows its `SAVE_MODE_CAPTIONS` caption as `settings-mode-{key}`. Persistence is unchanged:<br>• A Download leaf edit → exactly one `PUT /settings/downloader` after the debounce.<br>• A Convert leaf edit → zero PUTs until `convert-settings-save`, then one.<br>• A theme click → one `PUT /settings/ui` immediately. | Spec ST2 | A Convert edit that autosaves, or an autosave section that needs a button, fails. Captions match `SAVE_MODE_CAPTIONS` exactly. |
| AC-58.5 | integration | Every leaf sits in a 168 px `FormRow`/`PathRow` grid with exactly one accessible label per control (no double label from `SelectInput`). Path rows are field + Browse on one line with the existing `browse-*-btn` IDs and handlers. `readOnly` path inputs stay read-only through a new optional `PathRow readOnly` prop (additive primitive change, unit-tested). Convert/Capture path inputs stay editable (`convert-page.behavior.test.ts:201–280`). Numbers use 84 px inputs in a two-column grid, with hints only from `NUMBER_HINT_SOURCES`. | Spec ST4; mockup §04; MEU-51 PathRow | `getByLabelText` finds each leaf exactly once. No number leaf gains a new `min`/`max`/`step`. Browse and field share a row (overlapping y-ranges in Electron). |
| AC-58.6 | integration | Cookie mode becomes a `SegmentedControl` of native radios carrying `settings-leaf-cookie_mode-{none,browser,file}`. The `settings-leaf-cookie_mode` ID stays on the group. Sub-fields are indented and follow the existing `cookieBrowserVisible`/`cookieFileVisible` rules (`cookie-bar.ts:78–84`). | Spec ST1; G30 | Clicking a styled label must change the radio and send exactly one PUT with `cookie_mode` only. Sub-field visibility is unchanged. |
| AC-58.7 | integration | Checkbox rows show explanation text only from `CHECKBOX_COPY_SOURCES`. `settings-leaf-audio_format` stays enabled whatever `audio_only` is (ST6). | Spec ST5, ST6 | `audio_format` is enabled with `audio_only=false`. Checkboxes outside the list have no explanation line. |
| AC-58.8 | integration | `convert-settings-save` and `capture-settings-save` sit in right-aligned section footers as primary sm. They keep their existing `saveLabel` ("Save Changes •") / `btn-save-dirty` and existing `disabled` rule, and are dimmed when clean. `settings-rail-dot-convert` / `-capture` render iff the matching hook `isDirty`. | Spec ST2; mockup §04 | A clean section shows no dot. After Save succeeds the dot clears. The label/class assertions of AC-33.16/AC-39.15 stay green unchanged. |
| AC-58.9 | integration | Diagnostics become chip lists:<br>• **Dependencies:** a `StatusChip` (success "available" / warning "missing") plus name plus the already-carried version/path, and `check-deps-btn` with the same command.<br>• **Readiness:** four checklist rows, each chip "ok" / "missing", or neutral "checking" before `READINESS_LOADED`. The `readiness-*-link` Fix buttons keep their existing visibility rules and focus targets. `settings-readiness-count` = `READINESS_COUNT`. `settings-rail-dot-readiness` iff `READINESS_LOADED` and n < 4.<br>• **MCP:** a token chip from `tokenPresent` with `MCP_TOKEN_TEXT`, then `copy-mcp-btn` / `pin-mcp-btn` with the same IPC.<br>The token value is never rendered. | Spec ST7; mockup §02/§05 | Before load there is no count, no rail dot, and no "missing" chip. After load with all ok: "4 of 4 ready" and no dot. The MCP card DOM never contains the token (AC-23.12 stays green). |
| AC-58.10 | integration | `start-at-sign-in-panel`, `start-at-sign-in-checkbox` and `start-minimized-checkbox` keep their IDs, visibility rules and IPC inside the App group. All AC-61.* tests pass unchanged. | Spec §Settings last sentence; grouping §not-do | Any AC-61 test edit fails. |
| AC-58.11 | unit | `SETTINGS_SOURCE_LOCATION` holds. `NEW_TESTIDS` are registered after the MEU-54 block. The AC-51.6 hash lock is unchanged. | Local Canon (test contracts cited) | Moving a section into a subfolder, or editing pre-marker `test-ids.ts`, fails the existing contracts. |
| AC-58.12 | integration | A written, wired real-Electron wave in `settings.test.ts` covers:<br>• rail visibility and groups<br>• click → section in viewport + `aria-current`<br>• scroll → observer-driven current entry<br>• caption texts<br>• one-line Browse geometry<br>• Convert dirty dot and Save clearing it<br>• readiness count after load<br>• narrow-window rail row<br>W4-1..W4-3 and AC-61.17 stay green unchanged. | E2; `create-plan.md` §4A | Unit-only proof, a G36 silent guard or a stale locator fails. |
| AC-58.13 | integration | The remaining §05 `change` rows:<br>• **ST 14:** `apply-defaults-btn` moves to the Download section footer as ghost sm, right-aligned, and still POSTs `/downloads/apply-defaults` with no body.<br>• **ST 29:** `settings-leaf-log_to_file`, `settings-log-file-path` (mono) and `settings-copy-log-path` sit in one row, with the fixed-path note as a hint line below; same text and handler.<br>• **ST 31:** `theme-dark-btn` / `theme-light-btn` become a two-button segment with `aria-pressed` reflecting the current theme; same IDs and the same `putNow('ui', …)`. | Spec §05 ST 14, ST 29, ST 31 | Apply defaults sends exactly one POST (AC-23.3 unchanged). Exactly one theme button is `aria-pressed="true"`. The log path text still contains `logs/console.log` (AC-23.8/9 unchanged). |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Rail, grid, cap, captions, chip lists | Spec | Canon §Settings, ST1–ST7; mockup §04 |
| Section count (11 vs. "9") | Local Canon | Live `SettingsPage.tsx`; canon label left unchanged (it copies the mockup, AC-50.4); discrepancy recorded in the MEU-58 handoff |
| Hints and explanation copy | Spec + Local Canon | ST4/ST5 limited to `NUMBER_HINT_SOURCES` / `CHECKBOX_COPY_SOURCES` |
| Observer root and fallback | Local Canon + Research-backed | `AppShell.tsx:272–273` scroll container; MDN IntersectionObserver `root` (https://developer.mozilla.org/en-US/docs/Web/API/IntersectionObserver/root); jsdom lacks the API |
| Startup rail entry visibility | Local Canon | `StartAtSignInControl.tsx:30–64` null-render rules; a callback prop avoids a second `loginItemGet` |
| Readiness pre-load | Spec | ST7 "no fabricated count" |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | Grid, rail, captions, FormRow/PathRow, chips, footers |
| `ui/src/renderer/src/features/settings/SettingsRail.tsx` | new (top-level) | Rail + observer/fallback, `SETTINGS_SECTION_SET` consumer |
| `ui/src/renderer/src/features/settings/settings-sections.ts` | new (top-level) | `SETTINGS_SECTION_SET`, `SAVE_MODE_CAPTIONS`, `CHECKBOX_COPY_SOURCES`, `NUMBER_HINT_SOURCES` as one exported table each |
| `ui/src/renderer/src/features/settings/StartAtSignInControl.tsx` | modify | Optional `onAvailabilityChange` prop only |
| `ui/src/renderer/src/components/ui/PathRow.tsx` | modify | Optional `readOnly` prop (additive) |
| `ui/tests/unit/settings-page.test.ts`, `ui/tests/unit/settings-rail.test.tsx` (new), `ui/tests/unit/layout-primitives.test.ts` | modify/new | AC-58 behavior; PathRow `readOnly`; TM-1 |
| `ui/tests/e2e/settings.test.ts`, `ui/tests/e2e/test-ids.ts` | modify | AC-58.12; MEU-58 `NEW_TESTIDS` |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Transcript/TTS page composition and the MEU-48 inherited ACs | deferred | MEU-55, MEU-56 | Grouping Session 25; `SEQUENCING_GATE` requires them approved first |
| New readiness Fix action, unified save model, autosave for Convert/Capture | out-of-scope | — | ST2 and `COMPOSITION_LOCK` (`11-page-layout.md` §Scope, ST2 row) |
| Voice/format select conversion in Settings TTS (the free-text `voice` stays) | out-of-scope | — | ST 18 row changes width only; `COMPOSITION_LOCK` forbids enablement/value changes |
| Filmstrip arrow-key listbox model | out-of-scope | — | `COMPOSITION_LOCK`; AC-57.4 research note |
| Capture mark-count "n marks unsaved" in shot info | out-of-scope | — | CP6 allows *optional* shot info. No carried field gives an unsaved-mark count, and deriving one would be new behavior (`COMPOSITION_LOCK`). |
| Pre-load "no" labels / FFmpeg Fix link rendered before deps load (`SettingsPage.tsx:41–43,96`) | out-of-scope | — | Existing visibility rules are kept by ST7 ("keep readiness links/status IDs"). Only the count/dot/chip are gated. The reflection records it as an observation for triage. |
| Backend, API, MCP change | out-of-scope | — | Canon §Scope; grouping §not-do "No backend work" |
| Commit, push, merge, release | out-of-scope | — | AGENTS §Commits; PROFILE E5 |

---

## BUILD_PLAN.md Audit

`docs/BUILD_PLAN.md:55` shows Phase 11 🟡 In Progress, and `:72` says "Next: Phase 11 page layout (MEU-55)".

- **H1 row H1-3** marks MEU-57/58 `ready_for_review` through the SSOT and render, and leaves the generated spans alone. It does **not** edit `11-page-layout.md`: the "9 section ids" label copies the mockup and is locked by AC-50.4 (see `SETTINGS_SECTION_SET`). After its edits it re-runs `DOC_READING_TESTS`.
- **After independent approval**, H2-2 produces `POST_REVIEW_STATE`: Phase 11 → ✅ Completed, and Next = the `meu_status.py next` head. It is asserted by `plan_checks.py post-review` and followed by a `DOC_READING_TESTS` rerun.

The hub check is `rtk proxy uv run python tools/meu_status.py render --check` plus `grep -n "Phase 11\|Next:" docs/BUILD_PLAN.md`, captured under `${RECEIPTS_DIR}`.

---

## Verification Plan

Every command runs after the human execution message, from the repo root, in the form `rtk proxy <argv> > "${RECEIPTS_DIR}/p11cs-<id>.txt" 2>&1; code=$?; tail -n 40 "${RECEIPTS_DIR}/p11cs-<id>.txt"; exit $code`. Distinct IDs per run; the first failure is preserved. `PC` = `docs/execution/plans/2026-09-28-p11-capture-settings/plan_checks.py`.

### 1. Prerequisites (row 1)
- `rtk --version`
- `node --version`
- `rtk proxy npm --prefix ui ci`
- `rtk proxy uv run python PC self-test`
- `rtk proxy uv run python PC meu-state --expect MEU-50..56=approved --expect MEU-57..58=pending` (`SEQUENCING_GATE`)

### 2. Red (per MEU)
1. Vitest run: `rtk proxy npm --prefix ui run test -- <MEU files> --reporter=json --outputFile="${RECEIPTS_DIR}/p11cs-5N-red-vitest.json"`. Nonzero is expected.
2. Vitest oracle: `rtk proxy uv run python PC red --kind vitest --json "${RECEIPTS_DIR}/p11cs-5N-red-vitest.json" --ac AC-5N --new-file <new test file>`. The new test files (`tests/unit/capture-filmstrip-label.test.ts` for MEU-57, `tests/unit/settings-rail.test.tsx` for MEU-58) import modules that do not exist until Green. `--new-file` requires each of them to fail with a missing-module message: that is the stronger Red fact, and a syntax error is still refused. The `AC-5N` prefix must additionally have at least one assertion failure from the existing files. Self-test cases 7–10 cover this.
3. Electron run: `rtk proxy npm --prefix ui run build`, then `env -u ELECTRON_RUN_AS_NODE ${E2E_WRAP} npm --prefix ui run test:e2e -- <spec> -g AC-5N --reporter=json --outputFile="${RECEIPTS_DIR}/p11cs-5N-red-e2e.json"`.
4. Electron oracle: `PC red --kind playwright … --ac AC-5N`.

MEU-57 files: `tests/unit/capture-page.behavior.test.ts tests/unit/capture-filmstrip-label.test.ts`, spec `tests/e2e/capture-inbox.test.ts`. MEU-58 files: `tests/unit/settings-page.test.ts tests/unit/settings-rail.test.tsx tests/unit/layout-primitives.test.ts`, spec `tests/e2e/settings.test.ts`.

### 3. Targeted Green (per MEU, after each production edit)
The same Vitest files without JSON; `npm --prefix ui run typecheck`; `npm --prefix ui run lint`; build; the MEU's Electron spec (plus `capture-picker.test.ts` for MEU-57).

### 4. Phase 11 exit gate: one fresh full D6 pass (H1-2)
Every row of `.agent/docs/commands.md` §D6, in stage order, stopping at the first blocking failure (later stages `not_run`):

| Stage | D6 IDs | argv |
|---|---|---|
| static | py-types | `uv run pyright packages/` |
| static | py-lint | `uv run ruff check packages/ tests/` |
| static | ui-types | `npm --prefix ui run typecheck` |
| static | ui-lint | `npm --prefix ui run lint` |
| static | mcp-types | `npm --prefix mcp-server run typecheck` |
| static | task-contract | `uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-09-28-p11-capture-settings/task.md` |
| full | py-tests | `uv run pytest tests/ -x --tb=short -q` |
| full | ui-tests | `npm --prefix ui run test` |
| full | ui-build | `npm --prefix ui run build` |
| full | mcp-tests | `npm --prefix mcp-server run test` |
| full | mcp-build | `npm --prefix mcp-server run build` |
| full | openapi | `uv run python tools/export_openapi.py --check openapi.committed.json` (expect no drift) |
| full | state-render | `uv run python tools/meu_status.py render --check` |
| runtime | ui-electron | `env -u ELECTRON_RUN_AS_NODE ${E2E_WRAP} npm --prefix ui run test:e2e -- --reporter=json --outputFile="${RECEIPTS_DIR}/p11cs-phase-e2e.json"` |

- `mcp-server` needs `npm --prefix mcp-server ci` first.
- **Pass:** every row exits 0.
- The `ui-tests` row runs with `--reporter=default --reporter=json --outputFile.json="${RECEIPTS_DIR}/p11cs-phase-vitest.json"`, and the `ui-electron` row writes `p11cs-phase-e2e.json`. `COUNT_FLOORS` is then checked by `PC counts --vitest-json … --playwright-json … --min-vitest 597 --min-e2e 95`.
- **Scope audit:** `git status --porcelain` over `API_SCOPE_PATHS` is empty (task row H1-4).
- **Placeholder audit:** `rg -n -e TODO -e FIXME -e transition-all -e 'bg-\[#'` over the changed UI files. `rg` exit 1 means clean; matches or codes >1 fail.

### 5. Closeout
- `PC rows --task …/task.md`
- `tools/validate_closeout_artifacts.py` (handoff, AC coverage, review state, reflection) per the task rows
- `PC post-review --plan docs/execution/plans/2026-09-28-p11-capture-settings`, then `DOC_READING_TESTS`, then `PHASE11_EXIT_PREDICATE`, all after H2-2

No `packages/api/` change is planned. If one appears, stop and re-plan (§Stop conditions).

## GUI Element Compliance Check

`create-plan.md` §4A applies. The five named GUI reference/index/checklist files are absent. A planning-time existence check printed `absent` for each, so they are recorded as `gui-refs-not-shipped` and not claimed as checked.

Mapping comes from the live `GUI_RULES`:

- **Buttons:**
  - Capture region: primary md
  - Settings toggle and Browse/Copy/Check again: ghost or the PathRow default secondary sm
  - Save overlay / Save settings / section Saves: primary sm
  - Delete: destructive sm
  - Fix and Copy config: secondary sm
- **Choices:** native radios (G30, UX1).
- **Status:** `StatusChip` tones.
- **Colors and motion:** tokens only (G32). Motion `duration-fast`/`ease-out` for the disclosure, confirm strip and rail state; no `transition-all` (G33).

Every moved or new interactive element has a written, wired Electron assertion in AC-57.10 or AC-58.12 (E2).

## Stop Conditions

Stop and wait for a human in any of these cases:

- `SEQUENCING_GATE` refuses.
- A row-1 host prerequisite (`rtk`, `node`, the region-picker stub `.exe`) is missing on the chosen `EXECUTION_HOST`.
- `MIGRATION_CENSUS` finds a new-contradiction.
- Any `TEST_MIGRATIONS` item or newly found contradicted assertion lacks a human decision.
- The work needs a new API field, IPC channel or persisted mutation.
- A §05 ID cannot be preserved.
- Red is not an assertion Red.
- A blocking gate fails and cannot be fixed within scope.
- The execution review reaches 6 rounds.
- The plan review reaches 3 rounds without approval.

Never commit, push, merge or release without direct human approval.

## Open Questions

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| **OQ-1** Run order | A. Execute only after Session 25 is approved (`SEQUENCING_GATE`) | Grouping §Sessions/§Session 26; `current-focus.md` | Keeps the phase exit meaningful; section names are stable | Waits for Session 25 | ✅ |
| | B. Execute now; move the Phase 11 exit gate to Session 25 | `meu-status.yaml` MEU-57/58 `depends_on: [MEU-51]` | Unblocks work immediately | Needs a grouping amendment and plan amendment; the Settings rail lands before the Transcript/TTS layouts | ⚠️ |
| **OQ-2** Tools with no shot (CP5) | A. Disabled with a `title` hint | CP5 "visible but disabled"; capture mockup §02 and §05; UX2 | Matches the locked choice; teaches the prerequisite | Changes the W9-3 no-force clicks (TM-3); the canon also says "matching existing enablement" | ✅ |
| | B. Keep enabled | `COMPOSITION_LOCK`; `CaptureViewport.tsx:409–445` has no `disabled` | No test change | Contradicts CP5's explicit "disabled" | ⚠️ |
| **OQ-3** Capture Settings disclosure initial state | A. Closed | Capture mockup §02 ("Settings ▾"), §03 ("keeps them reachable without spending a permanent row") | Matches the mockup's purpose | TM-4 adds a toggle click in two E2E specs | ✅ |
| | B. Open | W9-3 current flow | No test change | Defeats the disclosure; not supported by the mockup | ❌ |
| **OQ-4** `TEST_MIGRATIONS` TM-1..TM-10 | Approve as listed (TM-3/TM-4 follow OQ-2/OQ-3; TM-5..TM-9 follow CP1; TM-10 follows §05 CP 17) | AGENTS §Testing (a proven expectation change needs human authorization); Session 24 precedent | Canon-backed; per-site list; `MIGRATION_CENSUS` stops on anything unlisted | Human time | ✅ approve |
| **OQ-5** `EXECUTION_HOST` | A. Windows host (`P:/av-kit`, Git Bash, `RECEIPTS_DIR=C:/Temp/av-kit`) | `capture-picker.test.ts:25` stub `.exe`; PROFILE (Windows, RTK); Session 24 95-test baseline | Every gate is runnable, so Phase 11 can exit | Needs Mat's machine | ✅ |
| | B. This web container | Session driver | No hand-off | No RTK; capture-picker cannot launch, so the phase gate stays `[B]` and Phase 11 cannot exit | ❌ |

## Research References

- `docs/build-plan/11-page-layout.md` §§Scope, Decision register (CP1–CP6, ST1–ST7), Shared layout primitives, Capture, Settings, Test-ID migration.
- `docs/proposals/2026-09-03-capture-page-layout-mockup.html` and `…-settings-page-layout-mockup.html` §02–§06.
- `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md` §Sessions and §Session 26.
- `docs/execution/reflections/2026-09-26-p11-queue-pages-reflection.md` §Next Session Design Rules. RULE-1 (resolve by semantic data within the owning root) applies to the rail's section lookup. RULE-2 (async init yields to user ownership) applies to disclosure/readiness state. RULE-3 (prove the fallback precondition) applies to the observer fallback test.
- `docs/build-plan/06-gui.md:963–1016`; `09-screenshot-capture.md:554`.
- W3C APG listbox and alert dialog patterns; MDN `IntersectionObserver.root` (URLs inline above).

## Round 1 Review Corrections

Plan review Round 1 (Fable 5.1 subagent, `2026-09-28-p11-capture-settings-plan-critical-review.md`) returned `changes_required` with 7 findings (3 High, 3 Medium, 1 Low). Each was re-verified against the tree before correcting; none was accepted on the reviewer's word.

| # | Sev | Finding | Verification | Correction |
|---|---|---|---|---|
| F1 | High | `TEST_MIGRATIONS` incomplete | Confirmed at `capture-page.behavior.test.ts:257–271,455,664,682`; `capture-inbox.test.ts:412,455,516`; `capture-page.test.ts:278–312` (`pagePath` literals); `capture-picker.test.ts:218–221`; `settings-page.test.ts:483` | Added TM-5..TM-7 with per-site dispositions, `CAPTURE_READY_SIGNAL` and `MIGRATION_CENSUS` (task row 2). Avoided further migrations by design: `CAPTURE_SOURCE_LOCATION` (the source contracts stay green), the sr-only full name in `FILMSTRIP_LABEL_RULE` (capture-picker stays green) and `MCP_TOKEN_TEXT`. |
| F2 | High | Canon "9→11" edit breaks AC-50.4 after the gate; H2 does not re-verify | Confirmed at `layout-canon.test.ts:130–147` (verbatim mockup-cell compare) | Removed the canon edit. Added `DOC_READING_TESTS`, re-run after H1-3 and H2-2. `PHASE11_EXIT_PREDICATE` now includes that rerun. |
| F3 | High | Red oracle unreachable for new-module test files | Confirmed: the helper refused file-level failures | `plan_checks.py red --new-file`: declared new files must fail with a missing-module message, and assertion Red is still required for the prefix. Self-test is now 26 cases (`p11cs-plan-checks-selftest-r2.txt`, exit 0). |
| F4 | Medium | Linux cannot run the gates (stub `.exe`, no RTK) | Confirmed at `capture-picker.test.ts:25`; `rtk` absent | Added `EXECUTION_HOST` and OQ-5 (Windows recommended); row 1 checks the stub; new stop condition. |
| F5 | Medium | Closeout predicates weaker than the prose | Confirmed | `plan_checks.py counts` (`COUNT_FLOORS`) and `post-review` (grouping/hub/focus/metrics against the tool's next MEU). The live negative refuses today (`p11cs-post-review-live-neg.txt`). H1-2 adds `task-contract` and JSON outputs. |
| F6 | Medium | ST 14, 29, 31 not reconciled | Confirmed at canon `:252,267,269` | Added AC-58.13. |
| F7 | Low | Clerical references | Confirmed: `schemas/captures.py`; `flushPut` at `useSettingsPage.ts:67–79`, `putNow` at `:126–144`; scope paths stated two ways | Fixed; single `API_SCOPE_PATHS`. |

Blast-radius census: the census receipt is `p11cs-census-r1.txt` and the per-hit dispositions are in `review-r2-census.md`.

## Round 2 Correction Notes (post-approval, non-blocking)

Round 2 returned **`approved`** with 1 Medium and 5 Low notes. Each was verified on the tree and applied as the reviewer recommended. None changes an AC's intent.

- **R2-1 (Medium):** confirmed at `capture-page.behavior.test.ts:430–436`, `:650` and `:343`. Added TM-8..TM-10; `TEST_MIGRATIONS` is now "known set, census-enforced"; OQ-4 now covers TM-1..TM-10.
- **R2-2:** TM-1 names the per-page primitive set.
- **R2-3:** the AC-57.3 banner stays mounted with its reserved height.
- **R2-4:** added `capture-filmstrip-name` and `capture-filmstrip-time` as the AC-57.4 observable.
- **R2-5:** `RECEIPTS_DIR` and `E2E_WRAP` must be exported.
- **R2-6:** fixed the baseline and driver wording. The re-sweep receipt is `p11cs-census-r2-resweep.txt`.

## Execution amendments — 2026-09-29

These are recorded after the user's execution authorization and host choice ([human-gate-decision.md](human-gate-decision.md)). Session 25 (`2026-09-28-p11-transcript-tts`) landed on `main` after this plan was reviewed; it was merged in as `1f9b035`. The amendments follow Session 25's proven route and do not change any AC.

| # | Amendment | Source |
|---|---|---|
| A1 | **`EXECUTION_HOST` = split.** Rows 1–8 and H1-1 to H1-5 run in the web container. `WINDOWS_GATE` (`validate-task.ps1 -Check windows-gate`, run by Mat) is the authoritative Phase 11 exit gate. It covers the full D6 set: Python, UI, harness build, MCP, OpenAPI, state render, full real Electron and the source audit, with zero failures tolerated. It is checked by `validate-task.sh windows-gate-check` against the reviewed commit. New task row H1-6 holds this turn boundary. The review becomes H1-7 and runs after the gate result lands. | `Human-approved` (2026-09-29); Session 25 `human-gate-decision.md` precedent |
| A2 | **RTK.** `rtk` is absent in the container, so container checks invoke tools raw; a raw invocation is the unfiltered equivalent of `rtk proxy` exact evidence. `WINDOWS_GATE` runs every stage through `rtk proxy`. | Session 25 plan §Harness (`2026-09-28-p11-transcript-tts/implementation-plan.md:59–61`) |
| A3 | **`COUNT_FLOORS` raised** to Vitest total ≥ 631 with 0 failed, and Electron `expected` ≥ 103 with 0 unexpected or flaky. These are the Session 25 authoritative gate counts (`current-focus.md`; `2026-09-28-p11-transcript-tts/windows-gate-result.json`). Enforced in `windows-gate-check`. | Local Canon |
| A4 | **`ENV_BOUND_TESTS` in the container only.** These failures are tolerated only with their proof signatures, copied from Session 25:<br>• AC-51.6 (the CRLF hash of the `test-ids.ts` prefix, with the rest of AC-51.6 replicated)<br>• AC-41.3 (the absent `P:/zorivest` path, with `styles.css` unchanged since `f7d3134`)<br>• the capture-picker specs (the missing Windows stub `.exe`)<br>`WINDOWS_GATE` tolerates none. | Session 25 `validate-task.sh` `vitest_env_ok` / `electron_env_ok` |
| A5 | **TM-1 after Session 25.** Session 25 (TA-1) removed Transcript and TTS from the AC-51.7 restricted loop, so the loop now holds only Capture and Settings. TM-1 therefore deletes that loop and adds the per-page positive-adoption checks named in TM-1. | Live `layout-primitives.test.ts:218–224` |
| A6 | **`NEW_TESTIDS` placement.** The new IDs are registered after the MEU-56 block (`test-ids.ts:333+`). The pre-marker prefix hash is unchanged. | Live `test-ids.ts` |
| A7 | **Validation cells.** Each task row now calls an exact check in [validate-task.sh](validate-task.sh). Red for new-module files uses `plan_checks.py red --new-file`. Electron Red and Green use Session 25's `electron_red` / `electron_env_ok`, which include the primitive-harness build. | Session 25 precedent; lint passes |
| A8 | **Pre-existing `py-types` failure fixed (scoped `API_SCOPE_PATHS` exception).** `packages/api/src/avkit_api/routes/captures.py:78` (from `6b40b4d`, MEU-60) failed pinned pyright: a `list[dict[str, object]]` was passed as `list[AnnotationIn]`. The fix is one `CaptureShotDetailOut.model_validate({...})` call. `s26-fix-equivalence.txt` shows it produces payloads and types identical to the old constructor for all four annotation kinds, and both still reject an extra field. Pyright reports 0 errors, ruff is clean, OpenAPI `--check` exits 0, and the container capture-test failure set is identical before and after (23 Windows-path-bound). | `Human-approved` (2026-09-29) |
| A9 | **Container pre-gate scope and MCP stage order.** In this container, `py-tests` fails 61 Windows-bound tests (`C:/` fixtures, NSIS/PowerShell packaging, framework tooling) while `packages/` is unchanged. It is therefore authoritative only in `WINDOWS_GATE`, and the container pre-gate omits it. Both scripts now run `mcp-build` before `mcp-tests`, because AC-32.8 and AC-38.8 assert that `dist/` exists; after a build, 215/215 MCP tests pass. | Local Canon (split decision; receipts `s26-rest-*.txt`) |
| A10 | **Container doc-test leg.** `tests/tooling/test_framework_adoption.py` fails the same 32 tests in this container at the untouched pre-execution merge `1f9b035` and at HEAD (identical failure sets). In the container, `validate-task.sh doc-tests` therefore requires no *new* failure versus that base. `WINDOWS_GATE` runs the file inside py-tests with zero tolerance. | Local Canon (receipts `s26-fwadopt-base.txt`, `s26-fwadopt-head.txt`) |
| A11 | **Self-contained framework-adoption tests.** `WINDOWS_GATE` attempt 1 (`47efbff`) failed py-tests because `tests/tooling/test_framework_adoption.py` pins the live sibling repo `P:/agentic-framework` at `003929c` with a clean tree, and that repo has since moved on. Scoped exception: only in that one file, the `SOURCE`/`SHA` inputs that go to `verify_adoption.py` come from a fixture that builds a throwaway git repo (one commit) under pytest's temp dir. Test names, parametrize IDs and every assertion stay unchanged. No change to `verify_adoption.py`, and nothing touches `P:/agentic-framework`. Mat's local agent makes this change on Windows (it needs RTK) and commits it before `WINDOWS_GATE` attempt 2 runs on that commit. | Human-approved (`human-gate-decision.md` §WINDOWS_GATE attempt 1 follow-up) |
| A11-W | **A11 widened to `migrated_tree`.** The narrow A11 change was not enough. `verify_adoption.py` `source_state()` also hashes every manifest entry with a `source_path` inside the source repo. `migrated_tree` copies the real `adoption-manifest.json` (68 such entries, 67 of those files exist only in `P:/agentic-framework`), and the narrow prototype gave 87 passed, 4 failed. So in its manifest copy, `migrated_tree` also commits a file at each `source_path` (content = the path string) and rewrites that entry's `source_sha256` to match. The approval-mode manifest uses the placeholder `"f"*40`. Still one file only, with test names, parametrize IDs and assertions unchanged (checked independently against `4047bfc`). Side effect: several `static`-mode negative cases used to get their expected refusal from the source check. They now reach the rule each one targets. | Human-approved (`human-gate-decision.md` §A11 widening) |
| A10-R | **Doc-test baseline moved to `7613beb`.** At `1f9b035`, `test_verifier_bootstrap_rejects_path_escape[*]` passed in the container for the wrong reason: the missing `P:/` source produced `REFUSE: … PosixPath('P:/agentic-framework')`, which contains "path". With the A11 fixture repo, those tests reach `rtk`, which the container lacks, so the comparison against `1f9b035` flags them as new. Even with a pass-through `rtk` shim, 26 tests still fail in the container (pwsh, the `P:/.agent` registry). The container leg now requires no new failures versus `7613beb`, the commit `WINDOWS_GATE` ran at 91/91. `WINDOWS_GATE` stays authoritative, with zero tolerance. | Local Canon (receipts `p11cs-doc-tests-a11.txt`, `s26-doc-pytest*.txt`) |
| A12 | **Harden the MEU-49 drag helpers.** `WINDOWS_GATE` attempt 3 (`fe86ac3`, tested `1356c59`) failed `ui-electron` on AC-49.26. It fails about 1 run in 5 on Windows (the local agent's `--repeat-each=5` gave 4 passed, 1 failed) and passes 15/15 in the container. Neither the queue code nor the test changed since attempt 2 passed. Scoped exception: only the drag helpers `grabRow` and `dragOver` in `ui/tests/e2e/download-queue.test.ts` change. They wait until layout holds still, aim at the transform-agnostic (settled) position, and wait for dnd-kit's `aria-pressed="true"` so the drag is known to be active. No test body, assertion, test name or product file changes. Before attempt 4, the local agent runs AC-49.25–28 with `--repeat-each=20` on Windows, and that run must be clean. | Human-approved (`human-gate-decision.md` §A12) |
| A13 | **Wait for the window to settle before a drag.** The A12 repeat check on Windows (`1442d73`) passed every pointer drag, 80/80, but AC-49.27 (keyboard drag) failed once in 20, and was clean on a 20× re-run. The failure text was `Dragging "DL-1" was cancelled…`. dnd-kit 6.3.1's sensors cancel on a window `resize` or `visibilitychange`. The app window is created with `show: false` and shown only after `loadFile`. A container probe showed one resize after every launch (1280×800 → 1280×773). If that resize lands after the pickup, the drag is cancelled. Scoped exception in `ui/tests/e2e/download-queue.test.ts` only: a new helper `windowSettled(page)` waits for `visibilityState === 'visible'` and 500 ms with no resize. It is called at the start of `grabRow` and in one new setup line in AC-49.27 before the handle takes focus. No assertion, test name or product file changes. Before attempt 4, the repeat check (AC-49.25–28 and W1-14, `--repeat-each=20`) must be clean on Windows. | Human-approved (`human-gate-decision.md` §A13) |
| A14 | **Make `test_ac_12_7` contention deterministic.** `WINDOWS_GATE` attempt 4 (`706cdc7`, tested `52ec926`) failed py-tests at `tests/unit/test_services.py:2140`, `assert 0 == 1` conflicts. `models.download()` returns immediately and does the work on a background thread under `self._lock` (the service is correct). The test released the held download before the second contender had called `download()`, so a late-scheduled contender started a fresh download and both succeeded. A scratch probe delaying contender b by 0.5 s reproduced `['a-ok', 'b-ok']` / `0 == 1`. With the fix it gives `['a-ok', 'b-conflict']`. Scoped exception: in the contention half of `test_ac_12_7` only, join both contenders before `catalog.release.set()`. No assertion or product change. Before attempt 5, the test must pass a Windows repeat run. | Human-approved (`human-gate-decision.md` §A14) |
| A15 | **The gate never reports stale counts.** Attempt 4's JSON carried attempt 3's Vitest and E2E counts, read from leftover receipts even though neither stage ran. `validate-task.ps1` now deletes `s26-win-vitest.json` and `s26-win-e2e.json` before the stage loop, and reads each only when its stage ran. `windows-gate-check` already refuses a partial stage list, so no false pass was possible, but the recorded numbers were wrong. Attempt 4's `vitest` and `e2e` fields are invalid. | Local Canon (plan tooling) |
| A16 | **Drop only on a committed `over`.** `WINDOWS_GATE` attempt 5 (`7151fcb`, tested `eb3acc9`) passed py-tests (A14 held: 50/50 repeats, and the full suite with no `-x` gave 608/0). It failed `ui-electron` at AC-49.25, one row short: PUT `[dl-2, dl-1, dl-3, dl-4]`. Mechanism, from dnd-kit 6.3.1 source: each pointermove sets coordinates, a render computes `overId`, an effect sets `over`, and a layout effect copies it into `sensorContext.current`. The DragEnd handler reads `sensorContext.current.over`. A pointerup that arrives before those renders commit drops on the previous row. A container probe that released in the same task as the final move reproduced the exact body 3/3. Scoped exception: at the end of the `dragOver` helper only, wait until the live region announces `moved to position N of M` for the target. dnd-kit emits that only after `over` is committed. No assertion, test body or product change. With the fix, the same immediate-release probe lands `[dl-2, dl-3, dl-1, dl-4]` 3/3. | Human-approved (`human-gate-decision.md` §A16) |
| A17 | **Revalidate av-kit's registry overlay.** `WINDOWS_GATE` attempt 6 (`ded5af4`, tested `f680e75`) passed the checks before the gate (drag repeat 100/100; full Electron suite ×2, 220/220). It failed py-tests at `test_framework_adoption.py::test_review_pipeline_wrapper_refuses_before_provider[same-vendor]` with `overlay_not_validated`. `P:/.agent/model-registry.json` was edited on 2026-09-29 18:07 for zorivest (gpt-6-sol → gpt-6.1-sol), so its hash is now `b06d7cda…`, while the tracked `.agent/model-registry.local.json` still records `validated_against: 7e85d6f3…`. This is the resolver's intended freshness guard, not a code regression. Scoped exception: the local agent revalidates the overlay with the resolver's project-scoped validate/compile (no global sync, and nothing written to `P:/.agent`). Only `.agent/model-registry.local.json` may change, and only its `validated_against` value. Any binding or class change stops the step. Decoupling the tests from the shared registry is filed as `TOOLING-SHARED-REGISTRY-COUPLING`. | Human-approved (`human-gate-decision.md` §A17) |
| A18 | **An empty SSOT queue closes the build plan.** After MEU-57/58 were approved, `tools/meu_status.py next` printed `No pending+unblocked MEUs found`, and `stats` reported 61/61 complete (60 approved, MEU-48 closed). `POST_REVIEW_STATE` assumed a next MEU. `plan_checks.py` now accepts `next` = none only when the tool says so and `stats` shows `Pending: 0`. In that case the hub Next line and `current-focus.md` must each state `No pending MEU` explicitly. The check stays fail-closed, and the self-test grew from 26 to 28 cases, adding a positive and an adversarial empty-queue case. | Local Canon (plan tooling) |

## Validation stage contract

Each stage is bound to PROFILE D6 (§Verification Plan item 4).

- **Input identity:** the git HEAD plus `git diff --stat` and a SHA-256 manifest of the changed files, recorded before and after the fresh full gate in `walkthrough.md`. An unknown input disables reuse.
- **Freshness:** Red, targeted and Green receipts are working evidence. Only the single fresh full gate on the final tree certifies H1-2, and any later code change invalidates it.
