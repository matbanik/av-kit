---
date: "2026-11-20"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-20-help-quick-start/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "hq-plan-2026-11-20-help-quick-start"
round: 3
---

# Critical Review: 2026-11-20-help-quick-start

> **Review Mode:** plan
> **Verdict:** approved

## Scope

Reviewed the round 3 working implementation plan, task table and exact JSON draft, including the complete before/current diff, against the cited renderer and local review contract. Rechecked F6, the Settings step 1 correction and regressions from the round 3 edits. Applied the plan-review Materiality Gate. Claude Code (Anthropic) authored the plan and corrections; Codex is its independent reviewer. This is Session 99, MEU-162, matrix 6.23, ledger round 3 of 3. Rounds 1 and 2 are retained as history below; the current assessment is in Recheck (round 3).

All writes were under `C:/Temp/av-kit`. No repository edits, package manager, product suite, Electron launch, network request, commit or push occurred. The disclosed sandbox-only settings file and all forbidden secret paths were left unopened. Existing planning receipts were read as planning evidence, not execution proof. Main-process and transcript response code were inspected narrowly to resolve the launch-isolation and content questions.

## Intent Anchor

when a first-time user opens the How it works card on any of the six pages (Downloader, Transcript, Text to speech, Convert, Capture, Settings), the card shows one sentence about the page, a numbered quick start of 4 or 5 steps in ASD-STE100 Strict style, and one screenshot (two on Settings) of the page with the same numbers marked on the controls. The screenshot matches the light or dark theme. Below the steps, the reference topics are short, plain and closed until opened. A tracked script takes the screenshots from the running app with demo data. Tests prove these things: every step names a control that exists, every image loads in both themes, no image is out of date with its steps, no image shows a home folder path, and the steps pass the STE linter. There is no manual check.

Intent achieved: **yes**, at the plan-specification level. F1 to F6 are fixed; zero open blocking findings and no new findings. Execution remains unstarted and requires Mat. Historical assessments and evidence below retain their original round context; the round 3 section supersedes them.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | **The shipped instructions describe workflows the current app cannot follow.** `QUICK_START_DATA`: Transcript step 4 promises View compiled immediately at Done, but the API does not return `compiled_path`; the renderer supplies it only after the user invokes Compile. A seeded compiled path hides this missing action. Convert offers Cut or Extract, then requires the Compress-only preset; a new user who chooses either cannot follow step 3. `PLAIN_TOPICS` also mandates the false fact that each Settings card saves when its Save is clicked, although most cards autosave or apply immediately. These violate AC-162.1/AC-162.9's intended content correctness and the first-time guide intent. | `docs/execution/plans/2026-11-20-help-quick-start/quick-start-draft.json:21`, `:39`, `:41`; `implementation-plan.md:223`. Producers: `ui/src/renderer/src/features/transcript/TranscriptPage.tsx:184`, `:323`; `packages/api/src/avkit_api/routes/transcripts.py:43`; `ui/src/renderer/src/features/converter/ConvertPage.tsx:699`; `ui/src/renderer/src/features/settings/settings-sections.ts:34`. | Include the Transcript Compile prerequisite and where to find it; make Convert a coherent first example or state its task conditions; correct the Settings fact to distinguish automatic and explicit saves. Keep the guide to 4 or 5 steps and test the real transition/preconditions rather than supplying the missing result in demo data. | fixed |
| F2 | High | yes | behavior | **`DEMO_STAGE` does not isolate the actual launch and readiness side effects.** The plan says launchElectron runs no backend and that scratch AVKIT_APP_DATA keeps every run off the real models folder. The launch reaches `boot()` and unconditionally `spawnOwned()`, before the fetch seam. Settings additionally calls `window.api.getSetupReadiness()`, outside fetch: a fresh scratch profile without a database falls back to `<HOME>/.avkit/models`, and its writability probe writes/deletes a file in that folder or its nearest existing ancestor. Thus the proposed Settings run touches real home/model storage and its readiness cannot be prescribed by the named fetch seam. This defeats the safety premise of AC-162.14/DEMO_STAGE and S12. | `docs/execution/plans/2026-11-20-help-quick-start/implementation-plan.md:51`, `:154`, `:161`; `task.md:36`. Call chain: `ui/tests/e2e/electron-app.ts:135`; `ui/src/main/index.ts:267`, `:379`; `ui/src/renderer/src/features/settings/SettingsPage.tsx:371`; `ui/src/main/setup-readiness.ts:62`, `:109`, `:147`. | Specify a real test-side isolation mechanism before launch. Seed the scratch profile's models setting to a scratch directory and assert it; account explicitly for the spawned backend and main-process IPC. If a backend-free launch is mandatory, name a supported launch seam and prove it rather than relying on renderer fetch replacement. Keep product backend/API/MCP scope unchanged unless Mat authorizes otherwise. | fixed |
| F3 | High | yes | control-defeat | **`STE_GATE`'s severity model and negative examples do not match the vendored linter.** `mechanism: task-row-completion-predicate`. The plan describes finding levels as `hard` or advisory, and its planning probe filters `level == 'hard'`. Actual hard findings use `advisory-free`. An independent `Spin up the job.` probe returned `hard_count: 1`, level `advisory-free`, exit 1; the plan probe's filter would report zero. Moreover AC-162.2 requires the passive fixture and `Set up the folder.` to fail, but the former is advisory only and the latter has no finding; both satisfy all the specified extra length/sentence/semicolon checks. Implementing only STE_GATE's stated checks therefore misses required violations, while its required negative tests cannot pass. | `docs/execution/plans/2026-11-20-help-quick-start/implementation-plan.md:57`, `:171`, `:298`; `task.md:48`; `C:/Temp/av-kit/help-quick-start/hq99-ste-draft.py:11`. Actual producer: `P:/creative-writing/.agent/skills/asd-ste100/scripts/ste-lint.py:35`, `:480`. | Define the adapter against the actual `advisory-free` value, fail closed on unknown levels, and use a known hard finding as a negative oracle. Explicitly specify how Strict handles passive advisories and the undetected phrasal example; add project-owned checks if those examples must be rejected. Do not change the vendored bytes or weaken frozen expectations during Green. | fixed |
| F4 | High | yes | behavior | **The generator can crop required numbered controls out of a successful screenshot.** `HELP_SHOTS_GEN` clamps the union of target boxes to the window before its size check and never requires every target/marker to lie inside the final clip. The `settings-setup` image groups Download Browse near the start of Settings with Readiness after Transcript, TTS, Convert, Capture, Console, Appearance and Dependencies. Those are separate, always-rendered sections in a long scrolling column, beyond the default 1280×800 window. Waiting for DOM visibility does not bring both into the viewport. Clamping loses one control; rejecting the unclamped union instead reaches S9. AC-162.7 checks dimensions/hash and AC-162.11 checks DOM visibility and image loading, so neither proves that both numbers actually appear in this image. This violates AC-162.4/AC-162.14's marked-screenshot deliverable. | `docs/execution/plans/2026-11-20-help-quick-start/implementation-plan.md:149`, `:150`; `quick-start-draft.json:66`. Layout: `ui/src/renderer/src/features/settings/SettingsPage.tsx:632`, `:1253`; `ui/src/renderer/src/features/settings/settings-sections.ts:34`; default window: `ui/src/main/index.ts:145`. | Define a feasible capture composition for the two Settings images, such as deliberate multiple-region composition, while preserving the required numbers. Assert full containment of every target and badge after scrolling/composition and before writing; add a negative off-clip target case. Do not silently clamp away a target or rely on the image-read observation to prove the gate. | fixed |
| F5 | High | yes | behavior | **Row 7 cannot reach its required Green before row 8.** `CARD_QUICK_START` skips a shot whose URL is absent, and its image dimensions come from the manifest. Both WebP files and manifest are first created in row 8. Nevertheless row 7 requires AC-162.4, which asserts the figures, two real image URLs and manifest dimensions, to pass, allowing only AC-162.7 to fail. Row 8 depends on row 7. With the stated real asset lookup, AC-162.4 must also fail; a static missing manifest import can prevent typecheck as well. This blocks the deliverable before generation, rather than demonstrating an intended Red. | `docs/execution/plans/2026-11-20-help-quick-start/task.md:53`, `:54`; `implementation-plan.md:136`, `:300`, `:410`. | Remove the dependency contradiction before writing/fixing the tests. Either produce the required assets before the full card Green or explicitly leave all asset-dependent assertions pending through row 7 and require their unchanged tests to pass after row 8. Specify how the renderer builds safely during that intermediate state. | fixed |

> **Historical round 1 observations:** Q1 to Q7 and the first Checklist Results below describe the prior submission. Their rejected points are superseded by the round 2 recheck. The Findings table retains the original finding text and historical line references, with current statuses.

## Q1. Goal and AC coverage

Accepted: AC-162.1–9 cover the data shape, intro, ordered steps, themes, topics, linter and manifest; AC-162.10–16 add real-app loading, targets, search, generator/negative run, provenance and repeat runs. Rows 6–9 implement these, with a tracked generator rather than a human app-check row. The five pinned topics, 14 committed WebPs and vendored MIT skill are accepted as instructed.

Not accepted: passing the proposed checks does not establish truthful procedures (F1), isolated demo capture (F2), effective STE enforcement (F3) or fully marked screenshots (F4). F5 also prevents reaching the asset Green in dependency order. Intent achieved: **partial**.

## Q2. Content and preserved facts

Accepted: Downloader's intake/Add/Start/Open file sequence maps to the page and shared queue controls. TTS's model picker/action IDs, text box, voice picker and Generate exist; the Get state can be seeded without actually downloading a model. Capture's region, filmstrip, Arrow and dirty Save sequence agrees with the renderer; drawing an arrow can expose Save without starting a capture. Topic IDs/order and the five exact pins are accounted for. The fact table generally preserves the existing subjects and useful distinctions.

Not accepted: F1's Transcript, Convert and Settings claims. The Transcript seam already includes a `compiled_path` that the real list response lacks (`transcript-queue.test.ts:47` versus `routes/transcripts.py:43`), so reusing that sample is not a proof of the user's sequence. Settings Download Browse writes only `downloader.path` (`SettingsPage.tsx:452`); qualify the draft's “other output” wording rather than implying it sets every feature's output folder. A word/keyword test cannot validate these workflow facts.

## Q3. Card, search, IDs and theme

Accepted: `CARD_QUICK_START` preserves the existing storage key, first-visit closed state, route-scoped/held F1 delivery, header toggle and search IDs. Closed native details with summaries are consistent with the proposed topics; search must control their open state and reset it when cleared. Keeping `data-help-section` solely on topics preserves W6-2's count. Appending IDs after the existing registry preserves AC-51.6's prefix boundary/hash. The root `.dark` CSS switch works for either initial theme and while the card is open; AC-162.11 checks actual loading after the switch.

No independent blocker on those changes. Asset-dependent card proof remains subject to F5. Existing tests were inspected, not executed.

## Q4. Generator, stages and drift

Accepted: one-worker/no-retry generation, bounded WebP quality reduction and a hard size cap are coherent; renderer canvas encoding needs no new package. Demo Done/Pending rows can expose queue actions, and Capture can use the fixed fixture plus a real draw. Shared canonical hash input prevents differing Node/browser serialization from producing different step hashes. Changing a step without retaking its images is caught by AC-162.7. Removing or hiding a target is caught by AC-162.11 when the stage and target assertion remain unchanged.

Not accepted: screenshot completeness/Settings geometry (F4) and the assumed backend/main-process isolation (F2). Layout, colour or control-label changes that retain IDs can still pass the specified drift checks; they do not compare the saved pixels with current UI. This is a stated limit of D-1294's two guards, not a demand for host-sensitive pixel diffs. The source-level directive to retake after page changes should make that limit clear. Full containment/marker assertions are still necessary for the present images, regardless of later drift policy.

## Q5. Privacy and scratch data

Accepted: PRIVACY_GUARD includes input values as well as innerText, covering PathRow/textarea values. The planted Settings path, required `privacy: blocked settings-setup-light`, nonzero exit and before/after asset hashes are a genuine end-to-end negative for that surface if the stage override is loaded and the path is inside the capture. Comparing the whole asset set catches replacement and additions. A page screenshot excludes native window chrome, so its OS title is not automatically a leak.

The guard is not OCR: canvas/image pixels, placeholders and tooltip attributes are not covered merely by reading innerText/value. The fixed Capture fixture and deterministic neutral seeds can close those specific inputs; no actual personal pixel/placeholder leak was established from the inspected sources. Do not describe the text scan alone as a general pixel-privacy proof. F2 is a concrete isolation failure: the default model writability probe reaches outside the scratch profile even though no job control is clicked.

## Q6. Red before Green and immutable expectations

Accepted: missing new modules are reached through globs and asserted, avoiding import/setup failures masquerading as Reds. Missing JSON is an explicit pytest problem. The Electron test checks targets before the missing list/figures; refusing target failures at Red is sound because unavailable demo controls would not prove the guide change. Red-record/red-unchanged covers the new tests, gate tool, IDs and stage; pin hashes protect old assertions. The no-match and first-visit closed guards correctly stay out of FAIL_TO_PASS. Row-0 selftests and the pytest/Playwright modes are specified deliverables, not falsely claimed existing executables.

Not accepted: F3's negative fixtures and F5's Green order. A small source-scan correction is also needed: AC-162.1/row 0 look only inside a feature folder, but Convert's `queue-card-primary-action` is produced in `components/queue/QueueCard.tsx:619`; follow the mounted shared producer rather than stopping on this valid target. The intended target is unambiguous, so this is a nonblocking scope-reference correction, not an additional delivery finding.

## Q7. Gate, scope, safety and decisions

Accepted: H1-2 schedules tsc, ESLint, targeted/full Vitest, targeted/full tooling pytest, ruff, STE, line endings, home-path scan, pin/Red hashes, build, the four named Electron suites, cleared ELECTRON_RUN_AS_NODE, host load and before/after identity. H1-4's unchanged packages/MCP file-set hashes make skipping product Python types/full pytest/OpenAPI/MCP reasonable for this renderer/tooling scope. New Python tooling still gets pytest and ruff. No named row stops processes by image name or edits another worktree. Unrelated state is protected by S4.

Not accepted: the claim that those Electron launches use no backend; the F1 pin itself explicitly waits for the real backend (`help-f1-mount.test.ts:152`). The actual app boot and Settings IPC establish F2 independently of that comment. Screenshot/gate reachability needs F4/F5 corrected.

D-1289 and D-1290 are accepted as pending M-5 briefs: each gives recommendation A, meaningful alternatives, consequences, failure/undo cost, sources and a do-nothing option. The alternative test-assertion changes are disclosed as M-7. This review does not choose either for Mat. D-1291's in-card JSON and D-1293's portable licensed vendoring are sound directions, subject to F3. D-1292 needs F2/F4 corrected. D-1294 describes bounded hash/target coverage; its layout-only drift limit is recorded above. D-1295–D-1298 remain free. Execution remains unauthorized at the human gate.

## Checklist Results

The table below records manual source review, not live product checks. Procedure: read the plan/task/draft, trace named controls and side effects through the current producer code, compare tests/canon/receipts and map each AC to its scheduled row. Observer: `codex-independent-reviewer`; exit code: null.

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | partial | Scope agrees; F5 makes the shared Green order unreachable. |
| PR-2 Not started | pass | All implementation rows are unchecked; new product/generator paths are absent as recorded in the planning probe and current reads. |
| PR-3 Task contracts | pass | Named owners, deliverables, commands, dependencies and statuses exist. |
| PR-4 Validation realism | fail | STE negative expectations conflict with the actual linter, and image assertions precede image generation (F3/F5). |
| PR-5 Source-backed planning | partial | Source labels and human briefs exist; F1/F2 contradict the actual application behavior. |
| PR-6 Corrections readiness | pass | Single target/MEU and rolling review paths are identified; no prior findings in round 1. |
| PR-7 Scope discipline | pass | Renderer/test/tooling scope and accepted exclusions are explicit; no unscheduled backend deliverable is hidden. |
| PR-8 Reachability and negatives | fail | Actual main-process side effects escape the fetch seam; screenshot clipping can lose a marked target (F2/F4). |
| PR-9 Named contracts | pass | Named single-statement contracts identify the governing rules; no materially ambiguous duplicate threshold established. |
| AV-1–AV-6, applicable planning aspects | partial | Assertion Reds and frozen files are planned, with no skip/only or product stubs; F1/F3/F5 prevent the proposed evidence from establishing every required behavior. |

### Independent executable probes

Each Python invocation set `PYTHONDONTWRITEBYTECODE=1`. Output was redirected under `C:/Temp/av-kit/help-quick-start/review`, its exit captured immediately and then propagated. No npm, pytest, Vitest, Playwright or Electron command ran.

| Check | Actual command | Exit | Decisive output |
|---|---|---|---|
| Draft mechanical lint | `rtk proxy python C:/Temp/av-kit/help-quick-start/hq99-ste-draft.py` | 0 | `total flagged: 0`. This proves the supplied draft satisfies that probe; its `hard` severity filter is not a valid general negative oracle. |
| Required negative examples | `rtk proxy python P:/creative-writing/.agent/skills/asd-ste100/scripts/ste-lint.py --json C:/Temp/av-kit/help-quick-start/review/ste-negative-passive.txt C:/Temp/av-kit/help-quick-start/review/ste-negative-phrasal.txt` | 0 | Passive example: one `passive-voice`, `level: advisory`; “Set up the folder.”: no finding. Overall `hard_count: 0`. |
| Actual hard finding | `rtk proxy python P:/creative-writing/.agent/skills/asd-ste100/scripts/ste-lint.py --json C:/Temp/av-kit/help-quick-start/review/ste-negative-hard.txt` | 1 | “Spin up the job.”: `phrasal-verb`, `level: advisory-free`, `hard_count: 1`. Expected linter rejection, not a product test failure. |
| Tracked tree unchanged | `rtk proxy git diff --exit-code` with `GIT_OPTIONAL_LOCKS=0` | 0 | Empty output: no tracked diff. This does not claim that untracked files are absent. |

```json
{"schema_version":"evidence.v1","check_id":"hq-r1-ste-hard-producer","command":"rtk proxy python P:/creative-writing/.agent/skills/asd-ste100/scripts/ste-lint.py --json C:/Temp/av-kit/help-quick-start/review/ste-negative-hard.txt","cwd":"P:/av-kit","scope":"vendored-source linter diagnostic contract","phase":"plan-review","exit_code":1,"result":"pass","tested_state":"working-plan-round-1; upstream skill 0.4.0; PYTHONDONTWRITEBYTECODE=1","output":"Expected rejection: phrasal-verb; level advisory-free; hard_count 1. The plan probe filters the different literal hard.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"hq-r1-ste-required-negatives","command":"rtk proxy python P:/creative-writing/.agent/skills/asd-ste100/scripts/ste-lint.py --json C:/Temp/av-kit/help-quick-start/review/ste-negative-passive.txt C:/Temp/av-kit/help-quick-start/review/ste-negative-phrasal.txt","cwd":"P:/av-kit","scope":"AC-162.2 passive and phrasal negative examples","phase":"plan-review","exit_code":0,"result":"fail","tested_state":"working-plan-round-1; upstream skill 0.4.0; PYTHONDONTWRITEBYTECODE=1","output":"hard_count 0; passive-voice advisory only for The file is downloaded by the app.; no finding for Set up the folder. The specified zero-hard gate accepts both required negatives.","fresh":true}
```

### Accepted limitations

This review does not certify UI runtime, image quality, WebP encoding or future plan-local scripts, which do not yet exist. Their specified behavior was reviewed; forbidden execution was not substituted with claimed passes. The known long pinned topics and image size budget are accepted. No finding concerns handoff formatting, section ordering, plan length, old squashed hashes or a different preference for the two human briefs.

## Recheck (round 2)

**Workflow:** `/plan-critical-review`, independent read-only recheck of Claude Code's corrections. **Observer:** `codex-independent-reviewer`. Current verdict: **changes_required**, one open High blocker. Execution remains unauthorized.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |
| F3 | open | fixed |
| F4 | open | fixed |
| F5 | open | fixed |

**F1 — fixed.** The draft now uses Open ZIP without inventing a compiled output, and AC-162.11 explicitly rejects `view-compiled-link` in the pre-Compile seed (`implementation-plan.md:170`, `:318`). The real worker writes the raw ZIP (`packages/core/src/avkit_core/services/transcript.py:562`), the route returns its path (`packages/api/src/avkit_api/routes/transcripts.py:43`), and the Done card offers the available link (`ui/src/renderer/src/features/transcript/transcript-card.ts:61`, `:117`). Convert's example consistently selects Compress, whose preset control is conditional (`ConvertPage.tsx:699`). The Settings fact now distinguishes save-as-you-type, explicit Save and immediate application (`implementation-plan.md:234`; `settings-sections.ts:35`, `:51`). These remove the original dead ends.

**F2 — fixed.** `launchIsolated()` supplies fresh scratch `AVKIT_APP_DATA`, `USERPROFILE` and `HOME` before launching, then asserts the child's environment and awaits backend readiness (`implementation-plan.md:168`; `task.md:50`). `launchElectron` actually passes those keys through `electronEnv` (`ui/tests/e2e/electron-app.ts:135`, `:137`; `electron-env.ts:32-40`), and `spawnOwned` inherits them (`ui/src/main/index.ts:267`). For the specified empty scratch home and database, the default models-folder probe reaches the existing scratch home rather than the real home (`setup-readiness.ts:54`, `:62`, `:102`, `:147`). `app.evaluate` here inspects the Electron main process, so it establishes the three child env values; it is not a filesystem trace, a renderer fetch assertion, or proof that no window was already created. The env is supplied before boot, which removes the actual original failure. The real backend and IPC are now acknowledged. No live launch was performed in this review.

**F3 — fixed.** `STE_GATE` uses the actual `advisory-free`/`advisory` levels, counts both in Strict steps, fails closed on missing/unknown levels and uses the detected `Spin up` oracle (`implementation-plan.md:185-189`, `:309`; `task.md:48`). The independent rerun of the permitted round-2 probe returned exit 0: 40 draft strings, 0 flagged; passive, phrasal, length, sentence-count and semicolon negatives each detected. `Set up` is explicitly a known linter limit. Unknown/missing-level adapter tests are specified; the future repository gate has not been executed.

**F4 — fixed.** The shots now group the top Download note/Browse separately from the adjacent Readiness/MCP area, rather than spanning most of Settings. After scrolling, `shotClip` must reject any target outside the viewport and may clamp only the empty margin; the overlay also checks badge containment (`implementation-plan.md:162-163`, `:315`, `:464`). The negative cases include partly/fully off-screen targets. Source layout supports the new `settings-setup` grouping: the four-row Readiness list is immediately followed by MCP, whose prompt has 12 rows (`SettingsPage.tsx:1253-1333`); the Console panel defaults closed (`components/layout/AppShell.tsx:64`), and the header is 40 px (`styles.css:167-173`). The resulting span is approximately 650 CSS px through Copy prompt, compatible with the stated 1280 x 800 window. This is a source-layout assessment, not a measured Electron viewport receipt; the scheduled generator must establish actual bounds and cannot silently crop away a number. F6 is a different failure in the capture's text collector.

**F5 — fixed.** `HELP_SHOTS` uses a manifest glob and returns null until assets exist (`implementation-plan.md:147`). `AC-162.4 css` can become Green at row 7 while `AC-162.4 figures` and AC-162.7 remain assertion failures until row 8 (`implementation-plan.md:311`, `:421`; `task.md:53-54`). `only-failing` is specified to require exactly the requested failing title groups, assertion failures only, and passes for every other AC-162 title (`task.md:44`); row 7 names both pending groups. The same test file must pass after generation at its row-4 hash. This removes the original dependency contradiction without changing an expectation or skipping a test. This is review of the scheduled tool's contract, not a claim that it exists or has passed.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F6 | High | yes | behavior | **Clean Settings screenshots are rejected by the expanded privacy scan.** PRIVACY_GUARD rejects clean Settings captures because ancestor innerText includes off-clip and masked paths. HELP_SHOTS_GEN now passes the scratch root and temp root to the guard, but PRIVACY_GUARD scans every intersecting element's innerText, skipping only the masked elements. Settings' outer page/column containers intersect either Settings clip and their innerText includes the Console card's Persist to <scratch>/appdata/logs/console.log, even when that card is scrolled outside the image. That value is produced by main-process readiness IPC, not the seeded fetch settings. Playwright screenshot masks do not remove DOM text; skipping settings-log-row does not remove the same text from its ancestors. The new roots therefore make the normal Settings run hit S10 and write no image. AC-162.14 cannot produce its required 14 files and clean lines. | `implementation-plan.md:164`, `:180`; `ui/src/renderer/src/features/settings/SettingsPage.tsx:622`, `:1108`, `:1116`; `ui/src/main/setup-readiness.ts:58`, `:153`. | Collect only text actually rendered in the clip, excluding masked subtrees without reintroducing their text through ancestor aggregates; check visible input values separately. Add generator/collector negatives showing that masked private text and off-clip private text do not block a clean clip, while an unmasked private path in the clip still blocks before any asset write. Keep the planted Download-path negative. | fixed |

F6 is a source-traced clean-run rejection, not a claimed pixel leak or a runtime result. The relevant chain is `getSetupReadiness` -> `probeSetupReadiness` -> `consoleLogFilePath(appData)` -> Settings `settings-log-file-path` span -> enclosing column/page `innerText` -> `findPrivatePath(..., roots)`. The enclosing column and page boxes intersect both Settings clips even while their Console child is off screen. Masking pixels does not alter those strings. This new root/mask combination prevents the positive generator run from completing. It is distinct from F2's corrected write outside scratch and F4's corrected target cropping. Subject: **committable-tooling**; kind: **behavior**; confidence: **High**; violated family: **AC-162**, specifically AC-162.14.

### Q1 to Q7 updates

- **Q1:** F1 to F5 no longer defeat the intended coverage. Intent remains partial solely because F6 prevents the screenshot deliverable.
- **Q2:** Transcript's raw-ZIP action and the Compress example now match their real controls and preconditions. Settings Download Browse changes the downloads folder, each false Readiness row has its conditional Fix action (`SettingsPage.tsx:565-610`), and Client/Copy prompt are real controls (`:1290-1333`). Small wording note: step 1's “each card” should say each card **with settings to save**; Dependencies/MCP have no save caption and Readiness shows a count (`settings-sections.ts:43-45`; `SettingsPage.tsx:221-236`). This does not recreate the original false Save procedure and is not a blocker.
- **Q3:** Asset-dependent proof is no longer required before assets exist. The accepted card/search/theme contracts and unchanged test pins otherwise stand.
- **Q4:** The source-backed launch isolation, adjacent Settings groups, re-measurement and full target/badge containment resolve the earlier generator concerns. F6 now prevents its clean Settings run. D-1294's accepted layout/colour drift limit is unchanged.
- **Q5:** Masking the actual path elements is the right screenshot operation, and the launch env protects the original home-folder probe. The new roots are useful, but the element-level text collector re-reads the excluded data through ancestors (F6); it must collect the unmasked visible text rather than whole-subtree strings.
- **Q6:** The corrected levels/oracles and two pending row-7 failures remove the former Red/Green contradictions. The shared-control source scan now includes `components/`. `only-failing` is an exact failure-set check, not a permission to ignore any other test; its selftests and frozen row-4 test remain required.
- **Q7:** The real backend is now explicit. The `shared` exception is confined to S4 ownership/baseline detection (`implementation-plan.md:406`, `:459`); it does not excuse renderer changes, alter test pins or exempt `commands.md` and `known-issues.*` from the copied input-identity algorithm (Session 97 `identity.py:113-119`, `:160-173`). Metrics/focus remain intentional closeout-output exclusions. Re-reading and editing only this session's lines remains the stated rule. `shared` alone cannot prove that another session's prose survived an erroneous replacement, but no concrete missing help deliverable follows from that exception. Do not broaden it into a validation exclusion. D-1289/D-1290 still await Mat; no execution, commit or push is authorized.

### Current checklist results

All manual rows below use the procedure stated in the row, observer `codex-independent-reviewer`, and null exit code. They assess the plan specification, not implementation success.

| Check | Result | Procedure or actual command | Exit | Evidence |
|---|---|---|---|---|
| F1 content and Settings truth | pass | Trace corrected draft and fact table to Transcript worker/API/cards, Compress-only controls, Settings captions/Browse/Fix/Copy prompt | null | Original unavailable actions and false Save rule removed; minor editable-card qualifier noted above |
| F2 env and IPC isolation | pass | Trace launchIsolated contract through launchElectron, electronEnv, spawnOwned and setup-readiness fallback | null | Extra env wins; the default models probe uses the supplied scratch home |
| F3 STE producer and draft | pass | `rtk proxy python C:/Temp/av-kit/help-quick-start/hq99-ste-draft-r2.py` with `PYTHONDONTWRITEBYTECODE=1` | 0 | `draft: 40 strings, 0 flagged`; passive advisory and Spin up advisory-free negatives detected, plus length/sentence/semicolon negatives |
| F4 clipping and composition | pass | Read shot groups and current Settings frame/list/MCP geometry; compare shotClip and badge invariants with negative cases | null | Original cross-page span removed; targets cannot be clamped away; actual runtime bounds remain an execution check |
| F5 dependency and immutable tests | pass | Compare HELP_SHOTS null/glob behavior, AC-162.4 split, row-7 allowed failure set and row-8 unchanged-test requirement | null | The two asset-dependent groups stay Red until generation; all other groups must pass |
| PR-1 / PR-4 / PR-8 capture deliverability | fail | Trace path-producing readiness IPC, Settings ancestor boxes/text, expanded roots and masked-element exclusions | null | F6: off-clip Console text is present in intersecting ancestors; a clean Settings screenshot is rejected |
| PR-2 unstarted scope / PR-7 boundaries | pass | Read current task row states, plan scope and corrected files | null | All 28 work rows unchecked; renderer/test/tooling scope retained; no backend/API/OpenAPI/MCP deliverable added |
| Product suites and Electron runtime | n/a | Not run: explicitly prohibited for this read-only planning review | null | No pytest, Vitest, npm, Playwright, Electron or network execution; no runtime pass claimed |

```json
{"schema_version":"evidence.v1","check_id":"hq-r2-ste-draft","command":"rtk proxy python C:/Temp/av-kit/help-quick-start/hq99-ste-draft-r2.py","cwd":"P:/av-kit","scope":"corrected quick-start draft and vendored-source linter negative oracles","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"round-2 working plan; source skill 0.4.0; PYTHONDONTWRITEBYTECODE=1","output":"draft: 40 strings, 0 flagged; passive (strict): advisory passive-voice; phrasal spin up (strict and flavored): advisory-free phrasal-verb; 21 words, three sentences and semicolon flagged; Set up remains the stated undetected case.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"hq-r2-settings-private-text-collection","procedure":"Read implementation-plan.md:163-180; trace SettingsPage.tsx:369-371, :622 and :1108-1116 to setup-readiness.ts:58-59 and :140-153. Compare outer page/column intersection with the collector's whole-subtree innerText and the masked-element skip.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"HELP_SHOTS_GEN and PRIVACY_GUARD positive Settings capture","phase":"plan-review","exit_code":null,"result":"fail","tested_state":"round-2 working plan and inspected producer source; no live app","output":"Console renders Persist to <scratch-root>/appdata/logs/console.log from main IPC. The intersecting page/column innerText includes this off-clip child. Skipping masked elements does not remove ancestor copies. roots includes scratch-root and tmpdir, so the clean positive run is blocked before writing the required Settings image.","fresh":true}
```

### Round 2 verdict (historical)

**changes_required** — F1 to F5 are fixed; F6 is one new evidence-backed High behavior failure in the tracked capture tooling. Correct the clip-text collection without weakening the unmasked-path negative, then submit ledger round 3. This report is saved only to `C:/Temp/av-kit/hq-plan-review-round-2.md`; the coordinator owns validation and copying to the canonical path. Mat still decides D-1289 and D-1290 and whether to execute. Nothing commits or pushes.

## Recheck (round 3)

**Workflow:** `/plan-critical-review`. **Observer:** `codex-independent-reviewer` (Codex, independent of Claude Code/Anthropic). **Current verdict:** **approved**. This is ledger round 3 of 3. There are zero open blocking findings. Approval assesses the plan; implementation and its runtime checks remain unstarted.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | fixed | fixed |
| F2 | fixed | fixed |
| F3 | fixed | fixed |
| F4 | fixed | fixed |
| F5 | fixed | fixed |
| F6 | open | fixed |

F1 to F5 retain their accepted fixes. The round 3 diff does not undo them. F6 is fixed by replacing ancestor text aggregation with individual text-node/control items, mask-subtree exclusion and clip filtering. The revised Settings sentence also resolves the round 2 Q2 wording note.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Confirmed fixes and adversarial checks

**F6 — fixed (`PRIVACY_GUARD`, AC-162.8 and AC-162.14).** `implementation-plan.md:180-187` now defines `gatherShotText(masks)` inside `page.evaluate`, without imported bindings or closures. It gathers each text node's own range rectangles, instead of an intersecting ancestor's entire subtree text. It separately gathers control values, including an empty control's placeholder. Membership in either masked subtree excludes its text and values. The pure, DOM-free `clipText` retains only unmasked items with a positive-area rectangle intersecting the screenshot clip.

This removes the original source-traced false block: the Console path is emitted in `settings-log-file-path` inside `settings-log-row` (`SettingsPage.tsx:1108-1116`). Its off-clip text can no longer arrive through the intersecting page/column containers (`:616-622`), and the mask excludes it if that row intersects a shot. The MCP prompt is a controlled textarea (`:1315-1322`) covered by the other named mask; the new control-value pass applies the same exclusion. Checking a masked element's descendants, rather than merely skipping its own aggregate string, is part of the corrected contract.

The negative still reaches the guard. Download path is an unmasked, read-only text input rendered through `PathRow` (`SettingsPage.tsx:641-650`; `components/ui/PathRow.tsx:42-48`). `gatherShotText` includes its value using the input's own rectangle. Row 8 still plants `C:\Users\alex\Videos` there and requires exit 1, `privacy: blocked settings-download-light`, and unchanged asset hashes (`task.md:54`; `implementation-plan.md:437`). `AC-162.8 text` also checks exclusion of masked, entirely off-clip and zero-area private items, followed by rejection of the same unmasked in-clip path (`implementation-plan.md:322`). These are prospective execution tests, not tests claimed to have run during this review.

**Visible-text edge cases.** The empty Backup folder field has a real path placeholder (`SettingsPage.tsx:1064-1070`); the new placeholder fallback covers it, and its source is the neutral staged inbox folder. MCP's closed Advanced details contains only action labels (`:1338-1349`), with no private path that could become a missed or false-positive value. The help card is closed before capture (`implementation-plan.md:161`). The inspected CSS and six feature/shared-control sources contain no CSS-generated private path. Queue output and eSpeak path titles do exist (`QueueCard.tsx:383`, `:621`; `SettingsPage.tsx:175`), but the prescribed stages supply neutral paths and do not request a native tooltip showing a personal path. The custom Tooltip portals actual text into `document.body`, where the walker can collect it. No concrete staged element was established that displays a private path omitted by the new collector, or carries an excluded scratch path back into the guard. This is a source assessment of these stages, not a general OCR or arbitrary-DOM privacy guarantee.

**Settings step 1 — true.** `quick-start-draft.json:187-188` now names the Download card and keeps `settings-mode-download`. The section registry labels that card Download and gives it autosave mode (`settings-sections.ts:35`). That mode's caption is `Saves as you type` (`:51-55`); `SettingsSectionFrame` places it beside the heading and gives it the exact target ID (`SettingsPage.tsx:219-236`). The revised instruction describes an existing visible note and no longer claims that every Settings card has a save note.

**Round 3 blast radius.** Compared all three current files with their supplied pre-round-3 copies. Changes are confined to the collector/filter contract, its new unit case and file/name inventories, corresponding task rows 4/7/8, and the one Settings sentence. The renderer-safe manifest glob, pending asset-dependent tests, screenshot containment rules, isolated launch, STE finding levels, Transcript Open ZIP and Compress example retain their fixes. `task.md:49`, `:53` and `:54` agree with the revised plan. D-1289/D-1290 remain human briefs using recommendation A; their choices and scope did not change.

### Current checklist results

Manual observations below use observer `codex-independent-reviewer` and null exit code. Pass means the reviewed plan specifies a coherent implementation and test; it does not certify an implementation that does not yet exist.

| Check | Result | Procedure or actual command | Exit | Evidence |
|---|---|---|---|---|
| F6 clean Settings capture | pass | Trace `implementation-plan.md:180-187` to Settings Console/MCP producers and mask membership | null | Individual node/control rectangles and subtree masks remove ancestor copies of excluded scratch paths |
| F6 unmasked in-clip negative | pass | Trace Download PathRow input through value collection, `clipText`, AC-162.8 text and row 8's planted negative | null | Visible value reaches `findPrivatePath`; negative still requires blocked line, nonzero exit and no asset write |
| Concrete visibility edge cases | pass | Inspect staged page/shared-control placeholders, closed details, path titles, Tooltip portal and generated CSS text | null | Backup placeholder covered; closed Advanced has labels only; no concrete staged private path missed |
| Settings step 1 | pass | Compare draft target/text with section mode, caption and heading render | null | Download has the named adjacent `Saves as you type` note at `settings-mode-download` |
| Round 3 regressions / F1 to F5 | pass | Compare three before/current files using `rtk proxy git diff --no-index -- <before-file> <current-file>`; inspect every changed contract/task clause | null | Diff exit 1 means differences, not a test failure; accepted fixes remain intact |
| Current draft STE and negative oracles | pass | `rtk proxy python C:/Temp/av-kit/help-quick-start/hq99-ste-draft-r2.py`, with `PYTHONDONTWRITEBYTECODE=1` | 0 | `draft: 40 strings, 0 flagged`; all expected negative diagnostics observed; documented Set up limit unchanged |
| Unstarted scope and human gate | pass | Re-read canonical task rows and plan gate; check correlated MEU handoff existence | null | All 28 work rows unchecked; correlated implementation handoff absent; `plan_to_exec_gate: human` retained |
| Product/runtime verification | n/a | Not run under the explicit read-only review restrictions | null | No pytest, Vitest, package manager, Playwright, Electron, network or repository mutation |

```json
{"schema_version":"evidence.v1","check_id":"hq-r3-privacy-source-trace","procedure":"Compare implementation-plan.md:163-187 and :322 with SettingsPage.tsx:616-650, :1064-1070, :1108-1116, :1315-1349 and PathRow.tsx:42-48; inspect task.md:49, :53-54 and the three before/current diffs.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"F6 correction, private-path positive/negative collection and round-3 regression check","phase":"plan-review","exit_code":null,"result":"pass","tested_state":"round-3 working plan, task, JSON draft and inspected renderer sources; no live app","output":"Ancestor innerText aggregation removed. Masked Console/MCP text excluded by subtree membership; off-clip and zero-area items filtered; unmasked in-clip input values and empty-control placeholders retained. AC-162.8 text specifies both exclusion and detection cases; row 8 retains blocked settings-download-light and unchanged-assets oracle. No new concrete failure established.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"hq-r3-ste-draft-independent","command":"rtk proxy python C:/Temp/av-kit/help-quick-start/hq99-ste-draft-r2.py","cwd":"P:/av-kit","scope":"current round-3 quick-start JSON and STE negative oracles","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"round-3 working draft; source linter loaded read-only with PYTHONDONTWRITEBYTECODE=1","output":"draft: 40 strings, 0 flagged; passive Strict advisory, Spin up advisory-free in both modes, 21-word sentence, three sentences and semicolon each flagged; Set up remains the documented undetected case. Includes revised Settings step 1.","fresh":true}
```

### Limits and authorization

The collector, images and renderer changes are planned deliverables. No browser/runtime pass, generated-image privacy result or future gate execution is claimed. The clean and planted-negative generator runs remain mandatory during execution. D-1294's accepted limitation on layout and colour drift remains unchanged. No Critical or High finding remains open.

The completion-preflight skill was consulted and applied to this review's output and task-state check. Its implementation-completion predicate cannot authorize execution in this read-only plan review: the unchecked task rows are expected. Mat still decides D-1289 and D-1290 and whether to execute. No repository file was edited; the coordinator owns copying this report and recording the verdict. Nothing commits or pushes.

## Verdict

**approved** — F1 to F6 are fixed at the plan-specification level. The plan achieves the registered onboarding intent under the stated decisions and accepted limits. There are no new findings and zero open blocking findings. Report: `C:/Temp/av-kit/hq-plan-review-round-3.md`. Execution remains subject to Mat's explicit authorization.
