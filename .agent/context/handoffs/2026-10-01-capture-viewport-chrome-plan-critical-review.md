---
date: "2026-10-01"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md"
round: 2
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "claude-fable-5-1-subagent"
---

# Critical Review: 2026-10-01-capture-viewport-chrome

> **Review Mode**: `plan`
> **Verdict**: `changes_required` (Round 1 of 3 — 1 High/blocking, 1 Medium, 3 Low; no Critical)
> **Reviewer**: Fable 5.1 subagent in a separate context, user-authorized route per `docs/execution/plans/2026-10-01-capture-viewport-chrome/human-review-decision.md` (same-vendor deviation disclosed there). The reviewer did not author the plan and wrote this verdict itself.

---

## Intent Anchor

Executing this plan is supposed to fix the three Capture-page problems Mat found on 2026-09-30: the viewport toolbar becomes nine icon buttons with tooltips and accessible names plus a contextual options row so that neither row scrolls horizontally at the default window (MEU-65, with the header "Settings" disclosure becoming an **Options** secondary button with icon and chevron), and the image gains wheel / + − Fit / `Ctrl+=` `Ctrl+-` `Ctrl+0` zoom about the cursor with Space-drag and middle-drag pan, where `FIT_MAP` grows a scale and offset so pointer → image mapping, handle radii and hit tests stay exact at every level and stored annotations never change (MEU-66) — under the Sessions 25–27 cloud/local split with one authoritative `WINDOWS_GATE` plus the human `CAPTURE_LOOK` L1–L6.

Would executing this plan as written deliver that? Almost. The architecture is sound and was verified against the live code: `VIEW_TRANSFORM` / `ZOOM_EXAMPLE` / `ZOOM_ABOUT_EXAMPLE` / AC-66.11 are arithmetically correct, `ZOOM_LADDER` matches Chromium `main`, every lucide name exists in the locked 0.400.0 typings, the keyboard design survives the surface `stopPropagation()` and the existing `CapturePage` / `AppShell` window handlers, `TEST_AMENDMENTS = ∅` holds against every existing assertion I could find, the AC-65.4 Red is achievable, and the `.sh` / `.ps1` / `plan_checks.py` mechanics are faithful to the Session 27 templates. One contract is wrong: AC-66.11's negative asserts that a sub-threshold **draw** creates no mark, but the live gesture reducer applies `DRAG_THRESHOLD_CSS` only to move/endpoint edits and `createDrawnMark` refuses only a zero-length arrow — and the plan itself declares `handleSurfacePointer` unchanged. That assertion would be frozen as an immutable Red that no planned production edit can turn Green (Finding 1). Everything else is Medium/Low.

---

## Scope

**Target**: `docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md`, `task.md`, and the plan-local files they invoke: `validate-task.sh`, `validate-task.ps1` (read against the `.sh` stage list per cloud-local §2), `plan_checks.py`, `local-requests.md`, `human-gate-decision.md`, `human-review-decision.md`.
**Review Type**: plan review of an unstarted Session 29 plan (Round 1; user-directed Fable 5.1 subagent route)
**Checklist Applied**: PR-1–PR-9 with the workflow Intent Anchor and Materiality Gate; DR-1–DR-8 where a docs claim is made; the v2.2 template IR/DR/PR tables.

Sources opened and compared line-by-line: `docs/build-plan/09-screenshot-capture.md:135-157,343-401,611-654,674-690`; `docs/build-plan/11-page-layout.md:35-50,80-95,255-290`; `docs/build-plan/gui-actions-index.md:70-85`; the grouping (`:60-110`, `:125-180`, §8 D-1–D-7 at `:164-176`); `known-issues.yaml` (`CAPTURE-TOOLBAR-ICONS`, `CAPTURE-SETTINGS-BUTTON-LABEL`, `CAPTURE-VIEWPORT-ZOOM` with their triage decision logs); `meu-status.yaml` MEU-57/59/60/65/66/67/68; `harness.local.md` (full), `harness-profiles.md:29,58,73-118`; `cloud-local-collaboration.md` §1–§10 headings and §3.3–3.4 text; `emerging-standards.md` G1/G11/G26/G30–G35/UX1/UX2 headings; reflections 2026-09-20 RULE-1, 2026-09-28 RULE-3 / ADD, 2026-09-30 RULE-3; AGENTS §Testing (`:57`), GUARDRAILS SIGN 1. Live code: `CaptureViewport.tsx` (all 951 lines), `CapturePage.tsx:5,41,60-135,128-178,574-720,860-930,970-1002,1125-1210,1249-1250`, `capture-fit-map.ts`, `capture-hit-test.ts`, `capture-help-content.ts`, `components/ui/{Button,Disclosure}.tsx`, `components/layout/{AppShell.tsx:40-90,255-273,NavRail.tsx:1}`, `ui/src/main/index.ts:130-145,450-470` (+ grep for `Menu`). Tests: `capture-page.behavior.test.ts:115-140,340-366,480-495,935-980,1040-1062,1240-1270`, `capture-page.test.ts:57,80-115,245-260,335-350`, `capture-inbox.test.ts:20-70,215-260,288-306,377-412,471,569,675-700`, `layout-primitives.test.ts:1-60,186-262`, `layout-canon.test.ts:1-50,85-150`, `gui-actions-audit.test.ts` (all), `e2e-wiring.test.ts:1-40`, `queue-canon.test.ts:1-20`, `tts-page.behavior.test.ts:240-256`, `tts-generate.test.ts:460-472`, `test-ids.ts:207-208,295-305,344`, `download-queue.test.ts:1105-1130`, `capture-fit-map.test.ts`, `capture-hit-test.test.ts`, `capture-help-content.test.ts` heads, `ui/playwright.config.ts:18`, `ui/package.json:31,51`, `ui/package-lock.json:7440-7443`, `.gitignore`. Peer plan: `2026-09-30-tts-repair/{validate-task.sh (diffed), implementation-plan.md:151-159, windows-gate-result.json, walkthrough.md}` and the MEU-64 handoff. Upstream: Chromium `third_party/blink/common/page/page_zoom.cc` (`main`, fetched 2026-10-01), `lucide-react@0.400.0/dist/lucide-react.d.ts` (unpkg), Electron `docs/api/web-contents.md` and `shell/browser/native_window_views.cc` (`main`), all under `/tmp/av-kit-review/`.

**Worktree state**: review started on `0e18fbd` with the plan folder untracked; during the review the author committed it as `4c62e18` (`docs(plan): Session 29 capture-viewport-chrome plan draft (MEU-65, MEU-66)`, 8 files, 1795 insertions). Line counts of every reviewed plan file are identical before and after the commit, `plan_checks.py static` still passes, `git diff --stat 0e18fbd 4c62e18 -- ui packages mcp-server tests tools docs/build-plan .agent/context` is empty, and `git status --porcelain` is now empty. No `2026-10-01-capture-viewport-chrome-MEU-6x-handoff.md`, no implementation review, no `walkthrough.md`, no `baseline.sha`, no `capture-toolbar.ts`, `capture-zoom.ts`, `capture-toolbar.test.ts` or `capture-zoom.test.ts` exists; all 20 task rows are `[ ]`. Review mode `plan` is correct.

**What was not run**: no product test, build, `uv sync`/`uv run`, `npm ci`, generator or CI gate (`ui/node_modules` is absent; no `rtk`, `pwsh` or Codex CLI here). Executed: `plan_checks.py static`, `bash -n validate-task.sh`, `tools/lint_task_contract.py` (stdlib, read-only), `rg`/`grep`/`sed`, `curl` into `/tmp/av-kit-review/`, and `.agent/skills/timestamp/scripts/stamp.py`.

---

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| 1 | High | yes | behavior | **AC-66.11's negative freezes an incorrect contract into an immutable Red that no planned production edit can turn Green.** The AC's Negative cell says "A 2 CSS px drag (below `DRAG_THRESHOLD_CSS`, which is 1 image px at `s = 2`) creates no mark" in the Arrow tool (`implementation-plan.md:254`). The live reducer does not do that: in `CapturePage.handleSurfacePointer` the `'up'` branch for `gesture.kind === 'drawing'` calls `createDrawnMark(...)` and commits the result **before** any distance check (`CapturePage.tsx:651-663`); the two `moved < DRAG_THRESHOLD_CSS` guards (`:671`, `:713`) are reached only for `moving` / `endpoint` edits; and `createDrawnMark` returns `null` only for a zero-length arrow or a zero-area rect/highlight (`:135-137`, `:149-151`). So at `ZOOM_EXAMPLE` (`s = 2`) a 2 CSS px Arrow drag maps to a 1 image px shaft and **creates an arrow**, exactly as 09:366 specifies ("Zero-length GUI gesture creates **no** mark" — anything longer does). The plan's own contracts agree with the code, not with the AC: `SURFACE_POINTER` says "`CapturePage.handleSurfacePointer` needs no change" (`:145`), MEU-66's Files Modified lists `CapturePage.tsx` as "passes `shotId={selectedId}` (the only change)" (`:295`), and Out-of-Scope keeps MEU-60's locks (`:316`). Under AGENTS §Testing (`AGENTS.md:57`: "Keep assertions/expected values immutable in Green … A proven wrong expectation needs a source-backed amendment and explicit human authorization") the row-5 Red for this assertion is immutable, so row 7 (`green66`) can finish only by editing a Red assertion or by adding a draw threshold to `CapturePage` — a MEU-60 behaviour change outside the plan — either of which is a human decision the plan does not schedule. Same class as Session 27 Finding 3 (incorrect contract cemented in Red); PR-5 source-backed planning, PR-8 (the negative oracle names a producer that does not exist and the plan does not create). The parenthetical is also wrong on its own terms: `DRAG_THRESHOLD_CSS` is 3 CSS px (`CapturePage.tsx:41`; 09:391), i.e. 1.5 image px at `s = 2`; it is the 2 CSS px drag that is 1 image px. | `implementation-plan.md:145,254,295`; `CapturePage.tsx:41,135-137,149-151,651-663,671,713`; `docs/build-plan/09-screenshot-capture.md:366,391`; `AGENTS.md:57` | Replace the negative with what MEU-59/60 actually guarantee at zoom: (i) a pointer-down and pointer-up at the **same** container point in the Arrow tool at `s = 2` creates no mark (zero length, AC-59.5 at zoom); and, if a threshold case is wanted, (ii) a 2 CSS px **body drag of a selected mark** at `s = 2` leaves the mark unchanged and pushes no history (`DRAG_THRESHOLD_CSS` is CSS-space, so it is zoom-invariant). State once in `SURFACE_POINTER` that the draw path has no threshold (09:366) so no later row reintroduces it. Fix the parenthetical. | open |
| 2 | Medium | no | behavior | **Red/Green mechanics are unstated for three MEU-66 unit cases, so their Red would be a setup error (S3) or no Red at all.** (a) AC-66.5 (`:248`) asserts `hitTestMarks` at `s = 4, ox = -300, oy = -120` — but `hitTestMarks` is already generic in `scale/ox/oy` (`capture-hit-test.ts:26-40,206-221`; the plan says so itself at `:145`), so every AC-66.5 assertion is **green on the baseline**; row 5's "Prove Vitest … assertion Red" cannot hold for it and `vitest_red` (`validate-task.sh:218-247`) only requires *some* decisive AC-66 failure, so a never-Red lock passes unremarked. (b) AC-66.7–66.10 run in the jsdom seam whose shot is 8×8 (`capture-page.behavior.test.ts:60-61`) on a 200×200 surface stub (`:122-135`) → `fitScale = 25`, above the 5.0 ladder top, so from `fit` `ZOOM_STEP in` is `null` and `capture-zoom-in` is disabled; only `out` (→ 500 %) is reachable. The plan names a ladder-reachable fixture (1600×900 in 800×600) only for AC-66.11 (`:254`). (c) AC-66.8's "resizing the stubbed surface … re-clamps the offsets" (`:251`) has no re-measure trigger in jsdom: the viewport measures in a `useLayoutEffect` keyed on `imageHeight, imageWidth, selectedIndex, showArrowHandles, showBodyHandle` and otherwise relies on `ResizeObserver`, which it skips when absent (`CaptureViewport.tsx:356-382`). Verification-quality, not a false pass of a missing deliverable (Materiality Gate #3), so non-blocking. | `implementation-plan.md:248,251,250-253`; `capture-hit-test.ts:26-40,206-221`; `CaptureViewport.tsx:356-382`; `capture-page.behavior.test.ts:60-61,122-135`; `validate-task.sh:218-247` | (a) Label AC-66.5 a regression lock expected green at Red (and have the MEU-66 handoff disposition it), or make it Red-capable by asserting the new `SURFACE_POINTER` → `hitTestMarks` chain at zoom. (b) Define the jsdom zoom fixture once (`ZOOM_SEAM_SHOT`: 1600×900 with the 800×600 stub, or any size whose fit lies inside the ladder) and reference it from AC-66.7–66.11. (c) State that AC-66.8's resize case installs a fake `ResizeObserver` whose callback the test invokes (test-side fixture), so the Red is the clamp assertion. | open |
| 3 | Low | no | control-defeat — `mechanism: gated-path-gap` | **`GATED_PATHS` says it lists "exactly the non-code files the gate stages read", but the `ui-tests` stage also reads files not in the list.** `capture-page.test.ts:57` reads `docs/build-plan/06-gui.md`; `queue-canon.test.ts:14-18` reads `10-queue-card-ui.md`, `06-gui.md` and `build-priority-matrix.md`; `queue-card` / `queue-list` tests read the three p10 plan folders and `2026-09-02-p10-queue-card-migration/named-sets.json` (`rg` census over `ui/tests/unit`). None is in the list (`implementation-plan.md:151`; `validate-task.sh:563-568`). No planned row edits any of them after the gate (row 9 touches 09/11/index before H1-6; H2-2's SSOT edits are re-proven by `post-review-state`), so nothing in this plan can exercise the gap — predicate-shape completeness, Low under Materiality Gate #3. Also predicate-shape: `look-check`'s regex `^\|?\s*L1\b.*?\b(pass|fail)\b` (`validate-task.sh:594`) takes the **first** of the two words on the line, so a row that keeps the template's `pass|fail:` token before the real result reads as `pass`. | `implementation-plan.md:151`; `validate-task.sh:563-568,594`; `capture-page.test.ts:57`; `queue-canon.test.ts:14-18` | Add `docs/build-plan/06-gui.md docs/build-plan/10-queue-card-ui.md docs/build-plan/build-priority-matrix.md docs/execution/plans/2026-08-28-p10-queue-card-foundations docs/execution/plans/2026-09-02-p10-queue-card-migration docs/execution/plans/2026-09-03-p10-queue-card-dnd` to `GATED_PATHS` (plan and `.sh`; `plan_checks.py` keeps them equal), or soften the "exactly" claim to the files this plan can touch. Anchor the look regex to the token that follows the item id (`^\|?\s*L1\b[^a-z]*(pass|fail)\b`). | open |
| 4 | Low | no | clerical | **Reference and wording drift** (all trivially inferable): (a) 09 row citations are off by a few lines — "FIT_MAP formulas from 09:369" → Fit model is `:363` (`:369` is Dirty); "letterbox … (09:371)" → `:364`; "both variants share the original pixel space (09:374)" → `:368` (Edit vs bake); D-12's "09:394 — Apply color with no selection" → `:393` (`:395` is Keyboard). (b) `gui-actions-audit.test.ts:12` → `indexPath` is `:11`. (c) `ZOOM_STEP`: "returns `null` when `fitScale` is not finite and > 0" should read "is not (finite and > 0)"; AC-66.1's `NaN`/`0` negatives already say which is meant. (d) Row 0's text lists `electron-setup` but its validation cell runs only `prereq && baseline`; `prereq` refuses without the binary (`validate-task.sh:322`), so this fails closed — say "run `electron-setup` by hand first" in the cell note. (e) `task.md` frontmatter `status: in_progress` while the plan says `draft` (same as Session 27; consistent with planning phase). | `implementation-plan.md:134-135,141-142,145,503`; `task.md:5,37` | Correct the five line refs, the `ZOOM_STEP` sentence and the row-0 note. | open |
| 5 | Low | no | clerical | **PR-9 restated clusters** (one finding; canonical site named): (a) the 15 icon names appear in `TOOLBAR_BUTTONS`/`OPTIONS_TOGGLE` (`:122,:129`), the `prereq` node check (`validate-task.sh:323`), §Planning receipts (`:619`) and §Research References (`:628`) — the `.sh` is the executable copy; say so and drop the two prose restatements. (b) `COUNT_FLOORS` 702/118 in the plan (`:152`), the `.sh` (`:552,:554`) and `local-requests.md:22-23` — `plan_checks.py` binds only the first two. (c) "17 stages" in plan §7 (`:402`) and `local-requests.md:21`; the `.sh` `order` list is canonical (`:542-543`). (d) `REPEAT_GREP` in plan §4 (`:377`) and `validate-task.sh:298`. (e) `WHEEL_STEP_PX = 100` is restated as the literal `wheel(0, -100)` in AC-66.12 (`:255`) and "one 100 px wheel event" in D-18 (`:565`). (f) `ZOOM_KEY_SCOPE` (`:140`) defines text-entry focus by tag name while the page already defines the same scope as `COLOR_FOCUS_IDS` + `annotationOwnsFocus` (`CapturePage.tsx:80-107`); the two differ only on `capture-text-bg-clear` / `capture-named-color`, which does not change zoom-key behaviour, but say which governs or reuse the set. (g) The `hub` check requires bare `D-9`/`D-12`/`D-14`/`D-15`/`D-17`/`D-18` in 09 (`validate-task.sh:422,428`); plan D-ids collide across plans (the plan notes this for triage ids at `:449`), so write them into the canon as "Session 29 plan D-14" — the substring predicate still passes. | as listed | Name the canonical site for each cluster and reference it elsewhere. | open |

No Critical finding. Finding 1 is independently blocking under the Materiality Gate: an evidence-backed incorrect contract (Severity guidance "incorrect contracts") that the plan would cement in an immutable Red assertion, so the row 5 → row 7 sequence cannot complete as written. Findings 2–5 do not contribute to the verdict.

### Autonomous decisions D-8 to D-21 vs. the obviousness test

All fourteen were checked against `human-decision-protocol.md` (convergence, two-way door, no product fork, no governance number) and the precedent sweep:

- **D-8** — `resolution: human`, `USER_EXPLICIT` reference present; grouping `:72` and `:135` say what the plan says.
- **D-9, D-11, D-13, D-16, D-19, D-20, D-21** — pass. `Button.tsx:22,58` (sm = `h-7`; `icon` = `p-0 aspect-square`), `NavRail.tsx:1` (lucide), `tts-page.behavior.test.ts:245,253` and `tts-generate.test.ts:464,469` (exact Cleanup text), `layout-primitives.test.ts:33-54` (AC-51.1 name 'Advanced') and AC-51.5's isolation regex (`:188-197` — forbids `features/`, `pages/`, `apiFetch`, `transition-all`, raw hex; a `lucide-react` import in `Disclosure.tsx` is allowed) all say what the plan says. `CaptureViewport.tsx:734` (`data-overlay-ready`) and `capture-inbox.test.ts:294-303` (inline FIT_MAP re-derivation) support D-20.
- **D-10** — pass: tools already sit in `role="group" aria-label="Annotation tool"` (`CaptureViewport.tsx:426`); 09:395 gives the arrow keys to nudging; no `role=toolbar`.
- **D-12** — pass as a decision; the only visible changes (Highlight, and Select-on-a-highlight, lose the Stroke field) contradict no existing assertion: the only Stroke reads are AC-59.13 (`capture-page.behavior.test.ts:490`, default tool `arrow` — `CapturePage.tsx:184`), AC-57.5 (`:1056`, after clicking Box) and W9-3 (`capture-inbox.test.ts:241`, no shot, tool `arrow`). The compaction lever's `Pipette` exists in 0.400.0.
- **D-14** — verified upstream: `page_zoom.cc:13-15` on `main` reads `{0.25, 1/3.0, 0.5, 2/3.0, 0.75, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0}`, min 0.25 / max 5.0 (`:25-26`); `plan_checks.py` binds the contract row to the D-14 quote.
- **D-15** — pass; `AppShell.tsx:273` (`main` is `overflow-auto`) is why a scroll container would break rect = container (see Observation 1 for the middle-button caveat).
- **D-17** — pass: `AppShell.tsx:49-75` binds only Ctrl+K / Ctrl+4 / Ctrl+5 / Escape; `CapturePage.handleEditorKey` (`:864-910`) prevents only Escape, Delete and the arrow keys and ignores `=`/`-`/`0`/Space; the surface `onKeyDown` (`CaptureViewport.tsx:736-739`) stops propagation **before** `window`, so the two-path design (`handleViewKey` from the surface handler and from a `window` listener) is necessary and sufficient. `capture-confirm-strip` exists (`CapturePage.tsx:978`), so the RULE-3 exclusion predicate is real.
- **D-18** — pass (MDN `deltaMode`; `page.mouse.wheel(0, -100)` yields `deltaMode 0`, `deltaY -100` → exactly one step at `WHEEL_STEP_PX = 100`).

No planning question needed a human; the plan is right not to ask one.

### Out-of-Contract Observations (non-blocking, ≤ 5)

1. **Middle-button pan vs Chromium autoscroll.** `PAN_GESTURES` (a) does not say the middle-button `pointerdown`/`mousedown` is `preventDefault()`ed. On Windows, Chromium starts middle-click autoscroll on an unprevented middle mousedown when a scrollable ancestor exists — `main` is `overflow-auto` (`AppShell.tsx:273`). `CAPTURE_LOOK` L5 would show it; one clause in `PAN_GESTURES` avoids the round trip.
2. **S5 is a macOS-class risk, not a Windows/Linux one.** Electron runs application-menu accelerators from `NativeWindowViews::HandleKeyboardEvent` (`shell/browser/native_window_views.cc:2060-2076`, `main`, read 2026-10-01), the `WebContentsDelegate` path for keyboard events the renderer did **not** handle, so a renderer `preventDefault()` on `keydown` suppresses View → Zoom In / Out / Actual Size on the gate target. The AC-66.12/66.13 `getZoomFactor()` oracle is still right to keep; D-22 is unlikely to fire.
3. **`NO_OVERFLOW` can be met by flex shrink rather than by fit.** Text inputs in a `flex-nowrap` row shrink below their width; today the Color group and the Stroke label carry `shrink-0` (`CaptureViewport.tsx:508,606`). State once that every `OPTIONS_ROW` group keeps `shrink-0`, so `scrollWidth <= clientWidth` measures fit, not clipping (L1 "nothing is clipped" is the human backstop).
4. **`capture-page.test.ts:254` forbids the literal `devicePixelRatio` anywhere in `CaptureViewport.tsx`** (comments included). A zoom comment mentioning it would trip AC-59.4; one line in `SURFACE_POINTER` prevents that.
5. **Playwright `getByRole('button', { name })` is substring, case-insensitive by default**, so `name: 'Text'` would also match "Clear text background" in Electron. The jsdom cases are safe (Testing Library is exact), but the Electron AC-65.x specs should use test ids or `exact: true`.

---

## Checklist Results

### Plan Review (PR)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Scope, order (rows 0–9, H1-1–H1-7, H2-1–H2-3), WP table, Handoff Set and Files Modified agree between `implementation-plan.md` and `task.md`; every `validate-task.sh <check>` in `task.md` is a case label; every D-id / AC-id in `task.md` is defined in the plan (`plan_checks.py static` PASS, 20 rows). |
| PR-2 Not-started confirmation | pass | HEAD `4c62e18` contains only the eight plan files; `git status --porcelain` empty; no MEU-65/66 handoff, implementation review, `walkthrough.md`, `baseline.sha`, `capture-toolbar.ts`, `capture-zoom.ts`, `capture-toolbar.test.ts` or `capture-zoom.test.ts` exists; all 20 rows `[ ]`. |
| PR-3 Task contract completeness | pass | `python3 tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-01-capture-viewport-chrome/task.md` → `OK: 20 row(s); 10-column table (with builder_model); 20 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic` (exit 0). |
| PR-4 Validation realism | partial | Every referenced executable exists (`tools/{lint_task_contract,meu_status,export_openapi,validate_closeout_artifacts,issue_triage}.py`, reflection template + schema, `metrics.md`, `current-focus.md`, `openapi.committed.json`, both registry overlays, the p11 plan and grouping; every existing test file in `UNIT65/UNIT66/REGCAP/E2ECAP/E2EDISC`; the four MISSING paths are the plan's new files). Flags verified: `--ac-coverage-only`, `--decision-source`, `update … --plan`, `issue_triage.py render --check`. `bash -n` exit 0. `electron_red`/`vitest_red`/`require_failed_title` read the Playwright/Vitest JSON shapes correctly (`-g AC-65` matches `AC-65.4`/`AC-65.5`; the needle `toBeLessThanOrEqual` is in Playwright's `expect(received).toBeLessThanOrEqual(expected)` message). The AC-65.4 Red is achievable: the pre-change row holds 9 text buttons plus the whole colour/stroke group (`CaptureViewport.tsx:425-620`, ≈1 250 px) against a ≈800 px viewport at 1280×773, and Session 27 proved an `innerHeight`-based geometry Red under the same `xvfb-run -a` helper (MEU-64 handoff `:71,:83`). Defects: AC-66.11's negative cannot reach Green (Finding 1); three MEU-66 unit cases have unstated Red mechanics (Finding 2); look-regex shape (Finding 3). |
| PR-5 Source-backed planning | partial | Every AC carries Spec / Local Canon / Research-backed / Human-approved. Verified against sources: 09:149, 09:155-157, 09:343-346, 09:363-375, 09:389-401, 09:619-623, 09:633-638, 09:642-654, 09:674-687; 11:41-46, 11:87-89, 11:263-286; gui-actions-index `:79`; grouping `:72,:95-101,:135,:164-176`; the three `known-issues.yaml` triage logs (D-10/D-11, D-12/D-13, D-16/D-17); `harness.local.md` §Claude Code (`plan_to_exec_gate` not overridden → `human`); `harness-profiles.md:29,58,75`; cloud-local §3.1–3.5, §4, §5.1, §7, §9, §10; G1/G11/G26/G30–G35/UX1/UX2; reflections 2026-09-20 RULE-1 (`:88`), 2026-09-28 RULE-3 (`:126`), 2026-09-30 RULE-3 (`:174`); Session 27 gate JSON (702/702 Vitest, 117 + 1 = 118 Electron). Upstream: Chromium ladder, 15 lucide names + `Pipette`, Electron `before-input-event` docs. Gap: AC-66.11's negative contradicts 09:366 and the Local Canon reducer (Finding 1); four 09 line refs drift (Finding 4). |
| PR-6 Handoff/corrections readiness | pass | One canonical handoff per MEU and one rolling implementation review named per `artifact-naming.md`; this file is the rolling plan review; Round 1, so the census gate is n/a. Every finding is resolvable via `/plan-corrections`. |
| PR-7 Scope-discipline (C2) | pass | `deferred` → MEU-67 and MEU-68 exist in `meu-status.yaml` (Sessions 30 / 28). `out-of-scope` rows cite 09:619-621 (icon rule scoped to "tool, history and view buttons"; overflow rule to "the tools row"; 09:389 "labeled buttons" for the mark list), 09:637 ("not a setting"; reset on shot change), 09:633 (wheel / buttons / keys only), 09:636 + 09:401 (MEU-59/60 locks), `PRODUCT_SCOPE` + S5 (app menu), `layout-canon.test.ts:91-103,130-145` (CP rows locked to `MEU-5[2-8]` and mockup text — verified, and the plan correctly routes the 11 edit to prose outside the parsed tables). Each cited source was opened and genuinely omits the item; no contract work is disguised as out-of-scope. |
| PR-8 Control reachability & totality | partial | Traced and sound: route `/capture` → `CapturePage` → `CaptureViewport` → `surfaceFromDom` → `SurfacePointer` → `handleSurfacePointer` → `hitTestMarks` / `createDrawnMark` → `POST …/annotate` with the E2E fetch ledger as the independent observable (AC-66.14, `capture-inbox.test.ts:382-409`); `ZOOM_OBSERVABLES` on the surface; `getZoomFactor()` and `scrollTop` negatives for the wheel/keys; `TOOLBAR_BUTTONS` closed over `CaptureTool` with `assertNever`; `wheelSteps` fails closed on unknown `deltaMode`/non-finite delta; `zoomKeyAction` closed key table → `null`; `VIEW_TRANSFORM` returns `null` on non-finite/≤ 0 input; zoom state is `useState` with no read-then-write pair across async boundaries. Arithmetic re-derived: `ZOOM_EXAMPLE` (400,300) ↔ (700,375), fit-only (800,450); `ZOOM_ABOUT_EXAMPLE` ox −133.33 within [−266.67, 0], oy 0 (content height 600 = container), cursor still (800,450); AC-66.11 ten centre-anchored `in` steps 0.5 → 2/3 → … → 2 keep the image centre under the container centre so (ox, oy) = (−1200, −600), then (+200, +150) → (−1000, −450); clamp ranges [−2400, 0] × [−1200, 0] hold. AC-66.1 steps (0.5 → 2/3 / 1/3; 1 → 1.1 / 0.9; 5 → null; fit 20 → null; fit 0.1 → null) and AC-66.5 (11 CSS px > `HIT_RADIUS_CSS` 10) hold. Defeated: AC-66.11's draw-threshold negative has no producer (Finding 1); AC-66.5 has no Red (Finding 2a); `GATED_PATHS` misses four `ui-tests` inputs (Finding 3). |
| PR-9 Single-statement discipline | pass with Low note | Named contracts (`PRODUCT_SCOPE`, `TOOLS`, `TOOLBAR_BUTTONS`, `ICON_BUTTON_RULE`, `OPTIONS_ROW`, `OPTIONS_BY_TOOL`, `NO_OVERFLOW`, `DEFAULT_WINDOW`, `WINDOW_SETTLED`, `OPTIONS_TOGGLE`, `DISCLOSURE_PROPS`, `ZOOM_LADDER`, `ZOOM_STATE`, `ZOOM_STEP`, `VIEW_TRANSFORM`, `VIEW_MAP`, `ZOOM_EXAMPLE`, `ZOOM_ABOUT`, `ZOOM_INPUTS`, `WHEEL_STEP`, `ZOOM_KEY_SCOPE`, `PAN_GESTURES`, `ZOOM_RESET`, `ZOOM_READOUT`, `ZOOM_OBSERVABLES`, `SURFACE_POINTER`, `CONTENT_BOX`, `ZOOM_SHOT`, `ZOOM_HELP_SENTENCE`, `TEST_AMENDMENTS`, `NEW_TESTIDS`, `GATED_PATHS`, `COUNT_FLOORS`) are each defined once; ACs and rows reference them by name; `plan_checks.py` binds `GATED_PATHS`, `COUNT_FLOORS`, `ZOOM_LADDER`, the stage order and the audit lists to their executable copies. Restated clusters recorded once as Finding 5. No two live spellings imply materially different behaviour. |

### Docs Review (DR)

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | partial | "`TEST_AMENDMENTS` is empty … keeps every existing assertion green" — verified against `h-7` (`capture-page.behavior.test.ts:350,1049`), visible Color/Stroke (`:1055-1056`), `flex-nowrap` (`:943-944`), `NO_SHOT_HINT` (title kept), AC-59.4 jsdom (`:361-363`, `querySelector('[data-testid="capture-draw-surface"] svg')` descends into `capture-zoom-content`) and source (`capture-page.test.ts:251-255`), AC-60.13 (`r = HANDLE_RADIUS_CSS / t.s` equals today's at fit), the rect stubs (`:122-135,1246-1268`), W9-3 (`capture-inbox.test.ts:241`, tool `arrow`), Cleanup exact text, AC-51.1/51.5/51.6/51.7, `gui-actions-audit` (Palette-`yes` rows and settings/help rows only — new `no` rows are inert), `e2e-wiring` (file + shell ids only); no `getByText`/`getByRole` query for a toolbar label exists in `ui/tests`. Holds. "`GATED_PATHS` … exactly the non-code files the gate stages read" — false for four inputs (Finding 3). "`CapturePage.handleSurfacePointer` needs no change" — true, and it is why AC-66.11's negative is wrong (Finding 1). |
| DR-2 Residual old terms | pass | `.ps1` stage ids, `AUDIT_SRC` and audit pattern match the `.sh` byte-for-byte (`plan_checks.py`); no `s27-` residue in the s29 scripts (diff against the Session 27 template shows only the plan slug, the receipt prefix, the removed `pytest_red` helper and the new test sets). |
| DR-3 Downstream references updated | pass | Row 9 names the 09 / 11 / index edits with `hub` predicates that match the live headings (`### Viewport tools` :135, `### Destructive Delete` :151, `### Viewport zoom`, `### Flatten with backup`, `## MEUs` :674, `## Exit criteria` :690, `## Capture page layout` 11:87, index row format `| \`capture:redo\` |`). |
| DR-4 Verification robustness | partial | Finding 1 (immutable wrong Red), Finding 2 (unstated Red mechanics), Finding 3 (gated-path gap, look regex). |
| DR-5 Evidence auditability | pass | Every task cell writes an exact receipt under `$RECEIPTS_DIR` and re-raises the exit; `.ps1` clears `s29-win-*` first, reads counts only for stages that ran, carries `pytest_floor` from the first counted attempt (`:49-50`, the Session 27 F9b fix), stops before stage 1 on preflight drift. |
| DR-6 Cross-reference integrity | partial | Line refs verified except the five in Finding 4. |
| DR-7 Evidence freshness | pass | `plan_checks.py static` re-run here on `4c62e18`: `PASS static: 20 task rows; scripts and plan cross-references agree` (exit 0), matching the planning receipt. |
| DR-8 Completion vs residual risk | n/a | Plan review; no completion claim. |

### Information Retrieval (IR) — template v2.2

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| All AC have source labels | pass | `grep -c "^| AC-6[56]\.[0-9]* |" implementation-plan.md` (24 rows) + manual read of the Source column | 0 | 7 + 17 ACs, each with Spec / Local Canon / Research-backed / Human-approved; D-ids resolve to the Decision Log |
| Validation cells are exact commands | pass | `python3 tools/lint_task_contract.py … --task …/task.md` | 0 | `OK: 20 row(s); … backticked, exit-code re-raised, receipt under RECEIPTS_DIR` |
| BUILD_PLAN audit row present | pass | `grep -n "## BUILD_PLAN.md Audit" implementation-plan.md`; `task.md` row 9 | 0 | §BUILD_PLAN.md Audit items 1–4; row 9 `hub` |
| Post-MEU rows present (handoff, reflection, metrics) | pass | `grep -n "^| H1-\|^| H2-" task.md` | 0 | H1-1…H1-7, H2-1 (reflection), H2-2 (metrics row, SSOT, issues), H2-3 (closeout) |

### Design Review (DR) — template v2.2

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| Naming convention followed | pass | `ls .agent/context/handoffs/ | grep capture-viewport-chrome`; plan §Handoff Set | 0 | `{date}-{slug}-MEU-6x-handoff.md`, one rolling plan review (this file), one rolling implementation review |
| Template version present | pass | `head -8 implementation-plan.md task.md` | 0 | `template_version: "2.2"` in both |
| YAML frontmatter well-formed | pass | `head -8` of both | 0 | keys `project/date/source/meus/status/template_version`; `task.md` `status: in_progress` vs plan `draft` (Finding 4e) |

### Post-Implementation Review (PR) — template v2.2

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| Evidence bundle complete | n/a | — | — | plan review |
| FAIL_TO_PASS table present | n/a | — | — | plan review; Red/Green per MEU (`red65`/`green65`, `red66`/`green66-unit`/`green66`) |
| Commands independently runnable | partial | `bash -n validate-task.sh`; `python3 plan_checks.py static` | 0 / 0 | Scripts parse and self-check; row 7's `green66` cannot reach Green for AC-66.11 as written (Finding 1) |
| Anti-placeholder scan clean | pass | `grep -nE '<PREFIX_AUDIT>' <5 existing AUDIT_SRC files>` | 1 (no hits) | The pattern now anchors `console\.log\(` (Session 27 F10 applied); no hit in the five existing audited sources; `capture-toolbar.ts`/`capture-zoom.ts` do not exist yet (`pregate` fails closed on a missing file, `:482`) |

---

## GUI, Boundary and Sequencing Assessment

- **Boundary Inventory (AGENTS §Planning Contract)**: complete and honest — no new external input surface in MEU-65 (handlers and `parsePositiveInt`/`normalizeHex`/annotate boundary unchanged); MEU-66's inputs are `WheelEvent` (closed `deltaMode` set, non-finite → 0 steps), `KeyboardEvent` (closed table → `null`), pointer buttons, and `ZOOM_STATE` that is never persisted or sent (`PRODUCT_SCOPE` proved by `api-scope`: frozen-path diff + Files-Modified allowlist over `ui/`, `.gitignore` covers `ui/out`, `ui/out-e2e`, `test-results/`).
- **Test-ID migration**: every registered Capture id is kept (`capture-settings-toggle` `:344`, `capture-color`/`capture-stroke` in `capture-page.test.ts:102-103` lists); `NEW_TESTIDS` land after the `// MEU-51 primitive harness IDs.` marker (`test-ids.ts:300`) so the AC-51.6 prefix hash (`layout-primitives.test.ts:200-207`) is untouched; `capture-chrome-tools` is used in source today and unregistered (grep), as stated. `DISCLOSURE_PROPS` with all three props omitted renders `[undefined, title, null]` → the same DOM, so TTS/Downloader/Convert/harness assertions hold.
- **Keyboard model**: verified end to end — React's synthetic `stopPropagation()` on the surface stops the native event at the root container, so a `window` listener never sees surface keys; with focus on `body` the window path is the only path; the `handled` flag is belt-and-braces. No conflict with `AppShell` (Ctrl+K/4/5, Escape) or `handleEditorKey` (Escape/Delete/arrows only). Electron on the gate target routes menu accelerators through the unhandled-key delegate (Observation 2), so S5 is a prepared exit that is unlikely to open.
- **Sequencing**: WP/row order is coherent; row 1's census precedes any test; `baseline` refuses on a dirty product tree; `prereq` refuses without the recorded execution message (good negative, matched against `human-gate-decision.md:7,28`); H1-3's SSOT edits precede the gate and H2-2's follow it with the doc-reading Vitest re-run, consistent with cloud-local §3.4. Defect: row 5 → row 7 for AC-66.11 (Finding 1).
- **Cloud/local split**: gate location recorded (`human-gate-decision.md` A-1, `USER_EXPLICIT`); reviewer route recorded with the same-vendor deviation disclosed; env-bound census equals Session 27's with proven signatures (`vitest_env_ok` `crlf_proof`, `electron_env_ok` stub-missing, `pytest_env_ok` subset-of-baseline); `COUNT_FLOORS` 702/118 reproduced from the Session 27 gate JSON (702/702; 117 expected + 1 unexpected under A-7). `.ps1` read against the `.sh`: 17 stage ids and argv identical to the `order` list; `rtk proxy` on every stage; `$PSNativeCommandUseErrorActionPreference = $false`; `rg` exit-1 → clean mapping; `pytest_floor` carried from the first counted attempt; preflight drift exits before stage 1; the result-file filter in `Get-CleanTree`. No Windows-side defect found.

---

## Commands and Static Evidence

```text
python3 docs/execution/plans/2026-10-01-capture-viewport-chrome/plan_checks.py static
  → PASS static: 20 task rows; scripts and plan cross-references agree   (exit 0; re-run on 4c62e18: same)
bash -n docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh        (exit 0)
python3 tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier \
  --task docs/execution/plans/2026-10-01-capture-viewport-chrome/task.md
  → OK: 20 row(s); 10-column table (with builder_model); 20 row(s) fully checked …   (exit 0)
curl … chromium.googlesource.com …/page_zoom.cc?format=TEXT | base64 -d → kPresetBrowserZoomFactorsArray lines 13-15 as quoted in D-14
curl … unpkg.com/lucide-react@0.400.0/dist/lucide-react.d.ts → 15/15 names `declare const …: LucideIcon`; Pipette present
curl … electron/docs/api/web-contents.md (before-input-event :517) ; shell/browser/native_window_views.cc (HandleKeyboardEvent :2060-2076)
python3 -c … 2026-09-30-tts-repair/windows-gate-result.json → vitest {702,0,702}; e2e {expected 117, unexpected 1, skipped 0, flaky 0}; pytest 629/0; pytest_floor 322
git rev-parse HEAD → 4c62e18aa9617287e1d2026a36593482399c0511 ; git status --porcelain → (empty)
git diff --stat 0e18fbd 4c62e18 -- ui packages mcp-server tests tools docs/build-plan .agent/context → (empty)
python3 .agent/skills/timestamp/scripts/stamp.py → 🕐 Completed: 2026-10-01 23:24 (UTC)
```

`rg`/`grep` sweeps (receipts in the transcript): toolbar-label text queries over `ui/tests` (none for Select/Arrow/Box/Highlight/Text/Undo/Redo/Original/Annotated; the only `hasText` hit is the mark list, `capture-inbox.test.ts:569`); `capture-stroke|Stroke|Color|h-7|flex-nowrap|overflow-x|object-contain|inset-0|viewBox|preserveAspectRatio|capture-chrome|capture-settings|'Settings'` over `ui/tests`; `addEventListener|DRAG_THRESHOLD|annotationOwnsFocus|confirm-strip|preventDefault|key ===` over `CapturePage.tsx`; `Menu|setApplicationMenu|before-input-event` over `ui/src/main/index.ts` (none); docs-path census over `ui/tests/unit` + `mcp-server/tests` + `tests/` (Finding 3); referenced-artifact existence (Sweep 8: 15 exist, 4 MISSING are the plan's new files).

---

## Open Questions / Assumptions

- Finding 1 assumes the plan intends no draw-threshold change in `CapturePage` (its own `SURFACE_POINTER` and Files Modified say so). If the author instead intends to add one, that is a MEU-60 behaviour change needing a Human-approved amendment to 09:366/09:391 and a row in Files Modified — say which.
- The container window geometry under `xvfb-run -a` is inferred from Session 27's proven `innerHeight`-based Red, not measured here (Electron was not launched). S4 remains the right guard.
- The plan folder was committed (`4c62e18`) while this review ran; the review binds to that SHA.

---

## Verdict

`changes_required` — executing the plan as written would freeze AC-66.11's "sub-threshold Arrow drag creates no mark" into an immutable Red assertion that contradicts the live gesture reducer (`CapturePage.tsx:651-663`, `createDrawnMark` `:135-137`) and 09:366, while the plan itself declares `handleSurfacePointer` unchanged — so row 7 cannot reach Green without either editing a Red assertion or changing MEU-60 outside the plan (Finding 1, evidence-backed High). The geometry contracts, the Chromium ladder, the icon set, the keyboard design, the empty `TEST_AMENDMENTS`, the AC-65.4 Red, the Out-of-Scope basis, the D-8–D-21 obviousness test, the env-bound census, the `.ps1`/`.sh` parity and the gate-check strictness were all verified against sources and hold, with the Medium/Low notes above.

---

## Follow-up Actions

1. Route corrections through `/plan-corrections`; do not implement product code.
2. Finding 1: rewrite AC-66.11's negative as the zero-length draw case (and, optionally, a sub-threshold **edit** case), fix the parenthetical, and state once in `SURFACE_POINTER` that the draw path has no distance threshold (09:366).
3. Finding 2: mark AC-66.5 as a green-at-Red regression lock (or make it Red-capable), define the jsdom zoom fixture once for AC-66.7–66.11, and state the fake-`ResizeObserver` mechanism for AC-66.8.
4. Finding 3: extend `GATED_PATHS` (plan + `.sh`) with the four `ui-tests` doc inputs or soften the "exactly" claim; anchor the `look-check` regex.
5. Findings 4–5: correct the five line refs, the `ZOOM_STEP` sentence and the row-0 note; collapse the restated clusters; tag the D-ids written into 09 with the plan.
6. Re-submit this rolling file for Round 2 with the untruncated blast-radius census and per-hit dispositions (PR-6).

## Residual Risk

After Finding 1 is corrected, the main execution risks are (i) the options-row width budget at `DEFAULT_WINDOW` on Mat's fonts — covered by D-12's pre-decided compaction lever and L1; (ii) middle-button autoscroll on Windows if `PAN_GESTURES` does not prevent the default (Observation 1), caught by L5; and (iii) the usual Session 26/27 gate round-trip overhead. S5 (whole-window zoom) is unlikely on the gate target (Observation 2). The non-English-voice and packaging items from Session 27 are untouched by this plan.

🕐 Completed: 2026-10-01 23:24 (UTC)

---

## Recheck (2026-10-01)

**Workflow**: `/plan-critical-review` Round 2 of 3 (recheck of the Round 1 corrections)
**Agent**: `claude-fable-5-1-subagent` (separate context, user-authorized route per `human-review-decision.md`; did not author the plan or the corrections)
**Reviewed state**: `1733777` (`docs(plan): Session 29 plan Round 1 review and corrections`) on top of the draft `4c62e18`; `git status --porcelain` empty; `git diff 4c62e18 1733777` touches only the plan folder (6 files, +462/−41) and this review file. Still unstarted: all 20 task rows `[ ]`, no MEU-65/66 handoff, `walkthrough.md`, `baseline.sha`, `capture-toolbar.ts`, `capture-zoom.ts` or their tests. Review mode `plan` is still correct.

### Intent Anchor (unchanged)

Executing this plan should deliver the icon toolbar + contextual options row + **Options** header button (MEU-65) and cursor-anchored wheel / button / `Ctrl` key zoom with Space- and middle-drag pan on a zoom-aware `FIT_MAP` that never rewrites stored annotations (MEU-66), gated by the Session 25–27 cloud/local split. With the Round 1 corrections, executing the plan as written would deliver that: the one contract that could not reach Green (AC-66.11's draw-threshold negative) is replaced by negatives the live reducer actually guarantees, and no correction introduced a defect that would stop a row from completing.

### PR-6 census gate (pre-verdict, round 2+)

| Requirement | Result | Evidence |
|---|---|---|
| Resubmission names a census receipt | pass | `implementation-plan.md:612-623` §Round 1 Review Corrections links `review-r1-census.md`; Step 5c summary line present (`review-r1-census.md:5-8`: 16 values, 45 + 3 sweeps, one stale site found and fixed) |
| Receipt is raw and untruncated | pass | `review-r1-census.md:31-189` holds the full `rg -F -n` output for Pass 1 (C1–C16, old and new values) and Pass 2 (the C4 re-fix), each with its `rg exit` code; no `head`/truncation. Re-running the sweeps here reproduces every hit (`DRAG_THRESHOLD_CSS` → plan:145,255; `ZOOM_SEAM_SHOT` → plan:148,251–255; `Session 29 plan D-` → plan:328–330, sh:422–423,429; `REPEAT_GREP` → plan:378, sh:298/390/412; old values `A 2 CSS px drag`, `exactly the non-code`, `17 stages`, `wheel(0, -100)`, `tagged with its D-id` → no match) |
| Every hit carries a per-hit disposition | pass | `review-r1-census.md:12-29` assigns each `file:line` from the receipt `consistent` / fixed; semantic variants were declared (C6 three spellings of "17", C10 both `.sh` tuple forms, C16 "the 17") |
| Delta since the receipt | noted, not a gate failure | The receipt predates the §Round 1 Review Corrections table, so three *current* hits are absent from it: plan:618 (`DRAG_THRESHOLD_CSS`), plan:619 (`ZOOM_SEAM_SHOT`) and plan:621 (`09:369` / `09:371` / `09:374` / `09:394`). All three are the correction log quoting the old and new values as history — I disposition them `confirmed-consistent`. No live plan statement still carries an old value. |

Gate passed; the corrected content is reviewed below.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 High — AC-66.11 draw-threshold negative cemented in Red | open | ✅ Fixed |
| F2 Medium — unstated Red/Green mechanics for AC-66.5 / AC-66.7–66.11 / AC-66.8 resize | open | ✅ Fixed |
| F3 Low — `GATED_PATHS` gap; `look-check` regex (`mechanism: gated-path-gap`) | open | ✅ Fixed (gated paths); regex residual recorded once below, non-blocking |
| F4 Low — reference and wording drift | open | ✅ Fixed |
| F5 Low — PR-9 restated clusters | open | ✅ Fixed |
| Observations 1, 3, 4, 5 | n/a | ✅ Folded into `PAN_GESTURES`, `OPTIONS_ROW`, `SURFACE_POINTER`, `ICON_BUTTON_RULE` |

### Confirmed Fixes

Each item was checked against the live sources, not the author's table.

- **F1** — `implementation-plan.md:255` AC-66.11 negatives are now (i) same-point down/up in the Arrow tool at `s = 2` creates no mark, (ii) a 2 CSS px body drag of a selected mark at `s = 2` leaves it unchanged and pushes no history, (iii) the fit-only mapping oracle. Verified against `CapturePage.tsx`: (i) a non-`select`, non-`text` down starts a `drawing` gesture (`:626-637`) and the `up` branch calls `createDrawnMark`, which returns `null` for a zero-length arrow (`:135-137`) → `return` before `applyHistory`/`commitSelection` (`:651-663`); (ii) in Select the down hit-tests through `hitTestMarks({cssX, cssY, scale, ox, oy, …})` (`:588-600`), the `moving` gesture records `startCssX/Y`, and both the `move` (`:713-715`) and `up` (`:671-673`) branches return when `Math.hypot` of the **CSS** deltas is `< DRAG_THRESHOLD_CSS` (= 3, `:41`) — no `applyHistory`, so the mark and history are untouched and the threshold is zoom-invariant in screen px, exactly as `SURFACE_POINTER` (`:145`) now states ("the draw path has no drag threshold … `DRAG_THRESHOLD_CSS` applies only to move and endpoint edits … No row adds or changes a threshold"). 09:366 (zero-length arrow) and 09:391 (3 CSS px drag threshold) say the same. The parenthetical is corrected (3 CSS px = 1.5 image px at `s = 2`). Negative (ii) is Red-capable, since its down must hit through the zoomed transform.
- **F2a** — `:249` AC-66.5 is labelled a regression lock expected green at Red with the handoff disposition `green-at-baseline (lock)` and names AC-66.11 as the Red-capable chain. `vitest_red` (`validate-task.sh:218-247`) needs only some decisive `AC-66` assertion failure, so the lock cannot fail the Red stage; `tools/validate_closeout_artifacts.py` enforces no Red-column vocabulary (`grep` for `FAIL_TO_PASS|Red` → none), so the free-text disposition is accepted.
- **F2b** — `:148` defines `ZOOM_SEAM_SHOT` once (1600×900 `SHOT` spread override, surface rect stubbed 800×600 via the `withSurfaceSize` pattern, `capture-page.behavior.test.ts:1246-1268`) and AC-66.7–66.11 (`:251-255`) all name it. Arithmetic re-derived by simulation with the plan's `ZOOM_STEP` / `ZOOM_ABOUT` / `VIEW_TRANSFORM` rules: fit `0.5` (`ox 0, oy 75`); ten `in` steps about `(400,300)` → `2/3, 0.75, 0.8, 0.9, 1, 1.1, 1.25, 1.5, 1.75, 2` with the image centre pinned under the container centre (each `ox = (Cw − W·z)/2`, the midpoint of the clamp range, so no clamp ever bites) → `(−1200, −600)`; pan `(+200, +150)` → `(−1000, −450)` inside `[−2400, 0] × [−1200, 0]`; `(400,300)` → image `(700, 375)`. `ZOOM_EXAMPLE` (`:136`) states the same numbers. Both directions are reachable from `0.5`, which fixes the fit-25 dead end.
- **F2c** — `:252` AC-66.8 installs a test-side fake `ResizeObserver`, changes the stubbed rect and invokes the callback. `CaptureViewport.tsx:356-382`: the `useLayoutEffect` measures via `host.getBoundingClientRect()` (`:362`), returns early when `typeof ResizeObserver !== 'function'` (`:374-376`) and otherwise subscribes `measure` (`:377-378`) — the cited `:374-381` is exact. The Red is therefore the clamp assertion.
- **F3 (gated paths)** — `GATED_PATHS` (`:152`) and the `.sh` `gated` list (`validate-task.sh:564-574`) now include `06-gui.md`, `10-queue-card-ui.md`, `build-priority-matrix.md`, `docs/proposals` and the three p10 plan folders; the "exactly" claim is replaced by the sweep it came from. `plan_checks.py static` → `PASS static: 20 task rows; scripts and plan cross-references agree` (exit 0), so the two lists are equal. A fresh path sweep over `ui/tests`, `mcp-server/tests`, `tests`, `packages` (`rg -o "docs/…|\.agent/…|openapi\.committed\.json"`) finds every `ui/tests/unit` input in the list or in the stated SSOT exclusion (`meu-status.yaml`, `BUILD_PLAN.md`); all paths exist on disk; the list is used only as a git pathspec (`git diff --quiet … -- *gated`, `git status --porcelain --untracked-files=all -- *gated`, `:575-582`), so directories are fine. `validate-task.ps1` holds no copy of the list (grep `gated|11-page-layout|gui-actions-index` → none), so nothing diverged.
- **F3 (look regex)** — `validate-task.sh:601` now `^\|?\s*L1\b[^a-z]*(pass|fail)\b`. Probed: `L1 pass: …` → pass; `L1 fail: pass button clipped` → fail; `| L1 | **fail** |` → fail; `L1 pending` / `L1 Pass` / `L10 pass` → no match (fails closed). It is strictly stricter than before. Residual below.
- **F4** — `:135` 09:363 (Fit model ✓), `:142` 09:368 (Edit vs bake ✓), `:146` Local Canon 09:363 ✓, `:254` 09:364 (Letterbox ✓), D-12 precedents 09:343-346 (DTO table ✓) and 09:393 (Color ✓), `gui-actions-audit.test.ts:11` ✓, `ZOOM_STEP` "not (finite and > 0)" ✓, `task.md:37` row 0 says to run `validate-task.sh electron-setup` by hand first and why ✓. `status: in_progress` kept with the stated TASK-TEMPLATE basis (`docs/execution/plans/TASK-TEMPLATE.md:5`) ✓.
- **F5** — `TOOLBAR_BUTTONS` (`:122`) is the canonical icon list and the two prose restatements are gone (`§Planning receipts`, `§Research References` now point at it); `local-requests.md:21-23` points at the `.sh` `order` list and `COUNT_FLOORS`; `:378` references `REPEAT_GREP` (defined once at `validate-task.sh:298`); AC-66.12 (`:256`) and D-18 (`:562,:566`) use `WHEEL_STEP_PX`; `ZOOM_KEY_SCOPE` (`:140`) says it governs only the zoom and Space keys while `COLOR_FOCUS_IDS` + `annotationOwnsFocus` keep the editor keys; the `hub` predicate (`validate-task.sh:422-423,429`) and the BUILD_PLAN Audit text (`:328-330`) both use "Session 29 plan D-n", and 09's heading order (§Viewport toolbar icons and Options `:613` → §Viewport zoom `:627` → §Flatten with backup `:642`) matches the predicate's section slicing.
- **Observations** — `PAN_GESTURES` (`:141`) prevents the middle-button down (autoscroll); `OPTIONS_ROW` (`:124`) keeps `shrink-0` on every group; `SURFACE_POINTER` (`:145`) bans the literal `devicePixelRatio`; `ICON_BUTTON_RULE` (`:123`) requires test ids or `exact: true` in Electron.
- **`plan_checks.py` definition-site check (new in the corrections)** — `plan_checks.py:134-152` now accepts a `D-n` only at `- id: D-n`, a `### D-n` heading, or a `| D-n |` grouping §8 row, and an `AC-6x.n` only at an AC table row; the grouping path resolves from the repo root or by `parents[4]` of the script. Negative cases on scratch copies: task referencing `D-99` → FAIL; `AC-65.42` → FAIL; `D-77` present **only as plan prose** → FAIL (the substring-check hole is closed); unmodified copy → PASS; live folder run from `/tmp` (fallback path) → PASS. Live `task.md` references D-1/D-7 (grouping rows), D-8/D-9/D-12/D-15/D-17/D-18/D-21 (`- id:`) and D-22 (`### D-22` draft heading) — all resolve.

### Remaining Findings

None blocking. No new High/Critical defect was introduced by the corrections. Non-blocking notes (clerical / residual, recorded once per Materiality Gate #3):

- **Low** / blocking: no — `mechanism: gated-path-gap` residual, `validate-task.sh:601`. The look regex still takes the first `pass|fail` after the item id, so a row that keeps the template token before the result (`L1 pass|fail: fail — clipped`) still reads `pass`; conversely any lowercase prose between the id and the result (`| L1 | Toolbar rows | pass |`) now refuses (fail-closed, so the coder must put the result first, as `local-requests.md:42` and the `.sh` comment say). If touched again: `(pass|fail)\b(?!\|)` or require the `:`. Recorded; not to be re-raised.
- **Low** / blocking: no — the Round 1 census receipt predates the §Round 1 Review Corrections table; plan:618/619/621 quote old values as history (dispositioned `confirmed-consistent` above). No action needed.
- **Low** / blocking: no — `ZOOM_SEAM_SHOT` (`:148`) cites `capture-page.behavior.test.ts:53-65,122-135`; live `SHOT` is `:54-66` and `bindSurface` `:125-138` (`withSurfaceSize` `:1246-1268` is exact). `withSurfaceSize(size)` stubs a square, so the 800×600 fixture is a width/height variant of that pattern, and the fake `ResizeObserver` must be installed before render because the effect's deps (`CaptureViewport.tsx:382`) do not re-run when the global appears.
- **Low** / blocking: no — `task.md:46` row 9 summarises the 09 rows as "the D-12/D-15/D-17/D-18 rows" (bare ids; D-9/D-14 unnamed) while the plan audit text and `hub` predicate require "Session 29 plan D-n". A summary, not a predicate; the `hub` check fails closed if the canon text omits the plan tag.
- **Low** / blocking: no — `plan_checks.py`'s AC check only sees AC ids written literally in `task.md` (the rows use ranges such as `AC-66.1–66.15`), so a renamed AC row is caught only via literal references — unchanged from Round 1, stated for the record.
- Residual, out of this plan's reach: `tests/tooling/test_framework_adoption.py` reads `.agent/docs/*.md`, `.agent/schemas/*`, `.agent/templates/TASK-TEMPLATE.md`, `docs/execution/plans/2026-09-26-framework-update-adoption` and one 2026-09-26 handoff that are not in `GATED_PATHS`; no row of this plan edits any of them (H1-3/H2-2 touch `meu-status.yaml`, the 2026-09-30 grouping, `current-focus.md`, `metrics.md`, `known-issues.yaml`; `metrics.md` is only a string in that test, `:918`), so nothing here can exercise the gap. Same class as F3; not escalated.

### Checklist (Round 2 deltas)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | `plan_checks.py static` PASS (20 rows); `lint_task_contract.py` → `OK: 20 row(s) … dependencies resolve and are acyclic` (exit 0); row 0 note now matches the `prereq` refusal (`validate-task.sh:322`) |
| PR-2 Not-started | pass | HEAD `1733777`, clean tree, only plan-folder and review-file changes since `4c62e18` |
| PR-3 Contract completeness | pass | lint exit 0 |
| PR-4 Validation realism | pass | `bash -n` exit 0; `vitest_red` tolerates the AC-66.5 lock; hub predicate matches the audit text and live 09 headings; look regex fails closed except the recorded template-token residual |
| PR-5 Source-backed planning | pass | AC-66.11 negatives now cite 09:366 / 09:391 / AC-59.5 and match `CapturePage.tsx`; the five line refs resolve to the quoted rows |
| PR-6 Census gate | pass | table above |
| PR-7 Scope-discipline | pass | Out of Scope table untouched by the corrections (`git diff` shows no change at `:314-320`); Round 1 verification stands |
| PR-8 Reachability & totality | pass | AC-66.11 (i)/(ii) have real producers (`createDrawnMark` null path; CSS-space threshold guards); `ZOOM_SEAM_SHOT` makes every AC-66.7–66.11 step reachable; the AC-66.8 resize trigger exists (`CaptureViewport.tsx:374-381`) |
| PR-9 Single-statement | pass | Restated clusters collapsed (F5); `WHEEL_STEP_PX`, `REPEAT_GREP`, `COUNT_FLOORS`, the `order` list and the icon list each have one canonical site plus named references |

### Commands and static evidence (Round 2)

```text
git log --oneline -2 → 1733777 docs(plan): Session 29 plan Round 1 review and corrections ; 4c62e18 … plan draft
git diff --stat 4c62e18 1733777 → 7 files, +462/−41 (plan folder + this review file only)
python3 docs/execution/plans/2026-10-01-capture-viewport-chrome/plan_checks.py static → PASS static: 20 task rows; scripts and plan cross-references agree (exit 0)
bash -n docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh → exit 0
python3 tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task …/task.md → OK: 20 row(s) … (exit 0)
plan_checks.py on scratch copies: D-99 → FAIL; AC-65.42 → FAIL; prose-only D-77 → FAIL; control → PASS; live from /tmp cwd → PASS
python3 ladder simulation (ZOOM_STEP/ZOOM_ABOUT/VIEW_TRANSFORM rules): fit 0.5 → ten steps → s 2 (−1200, −600); pan → (−1000, −450); (400,300) → (700, 375)
python3 regex probe of validate-task.sh:601 (nine cases, listed under F3)
rg re-runs of the census sweeps (C1, C2, C4, C6, C7, C8, C10, C16) → hits match review-r1-census.md plus the three correction-log lines
rg -o path sweep over ui/tests mcp-server/tests tests packages → GATED_PATHS covers every ui/tests/unit input
python3 .agent/skills/timestamp/scripts/stamp.py → 🕐 Completed: 2026-10-01 23:39 (UTC)
```

Not run: any product test, build, install, generator or CI gate (`ui/node_modules` absent; no `rtk`/`pwsh`/Codex here).

### Verdict

`approved` — every Round 1 finding is resolved in the live files: AC-66.11's negatives now assert what `CapturePage.tsx:135-137,651-663,671-673,713-715` and 09:366/09:391 actually guarantee, so row 5 → row 7 can complete without touching a Red assertion or MEU-60; `ZOOM_SEAM_SHOT` makes the jsdom zoom ACs reachable with arithmetic that reproduces `ZOOM_EXAMPLE`; the fake-`ResizeObserver` trigger matches `CaptureViewport.tsx:374-381`; `GATED_PATHS` covers every `ui/tests/unit` input and equals its executable copy; the hub predicate and audit text agree; the `plan_checks.py` definition-site check closes the substring hole and fails its negative cases. The PR-6 census is present, untruncated and dispositioned. Surviving items are clerical or recorded residuals (look-regex template-token case, three post-census log lines, two line-ref offsets, the row-9 summary wording) and do not block. Execution still needs the user's explicit authorization (`plan_to_exec_gate: human`); this verdict authorizes nothing further.

🕐 Completed: 2026-10-01 23:39 (UTC)
