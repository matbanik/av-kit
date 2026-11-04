# Walkthrough — 2026-09-28-p11-capture-settings

**Authorization.** The user wrote "check if we can execute now since 25 has finished and I'm good with your recommendations" and then chose "Split like Session 25 (Recommended)" (Claude Code web session, 2026-09-29). Both are recorded in [human-gate-decision.md](human-gate-decision.md). OQ-1..OQ-5 follow the ✅ recommendations.

**Receipts.** `$RECEIPTS_DIR` is the session scratchpad `receipts/` directory: `/tmp/claude-0/-home-user-av-kit/732d64b0-ff02-55ac-8b7c-1f17da32a6cc/scratchpad/receipts`.

## Prerequisites (row 1)

- **Merge:** `origin/main` (Session 25 approved, `9c9557a`) was merged into `claude/quirky-gates-o1lql2` as `1f9b035`. The only conflict was `current-focus.md`, resolved by hand.
- **`SEQUENCING_GATE`:** `plan_checks.py meu-state --expect MEU-50..56=approved --expect MEU-57..58=pending` → `PASS MEU STATE: 9 MEU expectations hold`, exit 0 (`p11cs-seqgate-0929.txt`).
- **Context-tool gate (execution recheck):** `not_applicable`. The `validate-task.sh prereq` guard confirms `graphify-out/` and `graphify-out-research/` are absent, and there is no Headroom install.
- **Dependencies:** `npm --prefix ui ci` and `npm --prefix mcp-server ci` both exited 0 (`p11cs-npm-ci-ui.txt`, `p11cs-npm-ci-mcp.txt`). The Electron postinstall silently left no binary, the same as in Session 25.
- **`electron-setup`:** `PASS electron-setup`. Electron 42.9.3 was fetched with curl and matches `checksums.json` (sha256 `46fc1cd5d70de57c372fbc0f36870c4c4d80b127a0d452d80bd577c5a7d39b7d`). `--version` runs under `xvfb-run` with `ELECTRON_DISABLE_SANDBOX=1`.
- **`prereq`:** `PASS prereq`. It covers the helper self-test, `SEQUENCING_GATE`, Node v22.22.2, `electron@42.9.3`, and Electron launchability.

```json
{"schema_version":"evidence.v1","check_id":"s26-prereq","command":"bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh prereq","cwd":"/home/user/av-kit","scope":"helper self-test, SEQUENCING_GATE, node_modules, Electron launchability","phase":"static","exit_code":0,"result":"pass","tested_state":"HEAD 1f9b035","output":"PASS MEU STATE: 9 MEU expectations hold ... v22.22.2 ... electron@42.9.3 ... v42.9.3 PASS prereq","fresh":true}
```

## Baseline (untouched tree, before any product or test edit)

- **Vitest:** `PASS s26-baseline-vitest: 629 passed`. The 2 `ENV_BOUND_TESTS` (AC-51.6 CRLF hash, AC-41.3 `P:` path) failed with their proven signatures, so the total is 631, matching Session 25's authoritative count.
- **Builds:** ordinary build and primitive-harness build both PASS.
- **Electron:** recorded below when the run finishes (`s26-baseline-e2e.txt`).

## Migration census (row 2)

`validate-task.sh census` → 222 hit lines in `s26-census.txt` (rg exit 0). Every hit site has one of the dispositions below. **TM-11 and TM-12** are new-contradictions: the stop rule fired and the user approved them, as recorded in [human-gate-decision.md](human-gate-decision.md).

| Site | Disposition |
|---|---|
| `e2e/capture-inbox.test.ts:217, :236, :321` (W9-3/W9-5 `capture-save` with no shot) | TM-2 |
| `e2e/capture-inbox.test.ts:229–233` (W9-3 no-force tool clicks with no shot) | TM-3 |
| `e2e/capture-inbox.test.ts:221–224, :237–238` (W9-3 inbox/hotkey/page-save) and `e2e/capture-picker.test.ts:185` (`toHaveValue`; no visibility needed) | TM-4 applies to W9-3. The picker `toHaveValue` is unaffected (value is readable while hidden). |
| `e2e/capture-inbox.test.ts:412, :455, :516` (clean-shot `toBeEnabled`) | TM-7 |
| `e2e/capture-inbox.test.ts:433, :601–602` | unaffected (the shot is dirty; Save is mounted) |
| `e2e/capture-inbox.test.ts` filmstrip, status, empty, banner and other tool hits (`:209–210, :225–228, :269–306, :292, :328, :410, :413, :427, :451, :454, :460, :514, :517, :552–560, :620–623`) | unaffected (IDs kept; tools clicked after a shot is selected; banner stays mounted per R2-3) |
| `e2e/capture-picker.test.ts:218` (`toContainText` full name) | unaffected (sr-only full name, `FILMSTRIP_LABEL_RULE`) |
| `unit/capture-page.behavior.test.ts:257–271` (`openSelectedSurface`) | TM-5 |
| `unit/capture-page.behavior.test.ts:455, :664, :682` | TM-6 |
| `unit/capture-page.behavior.test.ts:430–436` | TM-8 |
| `unit/capture-page.behavior.test.ts:650` | TM-9 |
| `unit/capture-page.behavior.test.ts:343` (tool `h-9`) | TM-10 |
| `unit/capture-page.behavior.test.ts:387–410` (AC-59.7, Save click on a clean shot) | **TM-11** (new, user-approved) |
| `unit/capture-page.behavior.test.ts:336–348` (AC-39.28, Box click) | **TM-12** (new, user-approved). Applied only if it fails: the page auto-selects the newest shot (`CapturePage.tsx:243–251`), so tools may be enabled. |
| `unit/capture-page.behavior.test.ts:406, :636, :698, :714, :853` | unaffected (shot is dirty at that point) |
| `unit/capture-page.behavior.test.ts:320–327, :785` (inbox/page-save interaction) | unaffected unless jsdom blocks the collapsed panel; the approved conditional TM-4 setup click covers that case |
| `unit/capture-page.behavior.test.ts` other tool, status and chrome hits (`:299–307, :370, :480–600, :658, :729, :819, :838, :854, :925–933`) | unaffected (after a selected surface; chrome classes kept) |
| `unit/capture-page.test.ts` source pins (`:67–100` ID list across capture sources; `:206, :217–219, :278, :296, :301–302, :311–312` page literals; `:240–247` filmstrip; `:262–265` viewport tools) | unaffected under `CAPTURE_SOURCE_LOCATION` (action group, empty state, inbox/hotkey controls rendered in `CapturePage.tsx`; tools stay in `CaptureViewport.tsx`; filmstrip keeps `bg-accent`) |
| `unit/layout-primitives.test.ts:218–224` | TM-1 |
| `unit/layout-primitives.test.ts:26, :157, :167, :205, :231–238` | unaffected (primitive harness, Downloader/Convert/Transcript/TTS adoption) |
| `unit/settings-page.test.ts` (`:212, :301, :327–330, :384–421, :472, :483`) | unaffected (same IDs and actions; `MCP_TOKEN_TEXT` keeps yes/no; readiness links keep their visibility rules) |
| `e2e/settings.test.ts` (`:100–165`), `e2e/help-search.spec.ts:60`, `e2e/console-chrome.test.ts:103` | unaffected (same IDs, visibility and clicks) |
| `unit/gui-actions-audit.test.ts`, `unit/chrome-zorivest.test.ts` | unaffected (ID strings stay in production sources; Button and SelectInput unchanged) |
| `unit/convert-page*.test.ts`, `unit/convert-controls.test.ts`, `e2e/convert-queue.test.ts`, `unit/queue-*.test.ts`, `unit/transcript-page.test.ts`, `unit/setup-readiness.test.ts` | unaffected (different surfaces; `display_name`/`createPortal`/`components/ui` matches belong to other pages) |
| `e2e/test-ids.ts` (20 hits) | unaffected. New IDs are appended after the MEU-56 block. |

## Baseline Electron (completed)

`PASS s26-baseline-e2e: 99 passed`. The 4 capture-picker specs were env-bound, since the Windows stub `.exe` is absent, so the total is 103, matching Session 25's authoritative count.

## MEU-57 (rows 3–5)

- **Red:** `validate-task.sh red57` → `PASS RED vitest: 46 failing assertions cover ['AC-57']`. The new `capture-filmstrip-label.test.ts` failed only with a missing-module message, which `--new-file` accepts. Electron: `PASS AC-57 E2E RED: 4 failing AC-57 specs`.
- **Green:** `green57` → `164 passed` (AC-51.6 env-bound). TM-12 and the conditional unit TM-4 click were not needed.
- **Gate:** `gate57` → typecheck, lint, `vitest 164`, build, `e2e 13 passed` (4 picker specs env-bound). Commit `3b3de3e`.
- **Pre-review screenshot check:** real Electron, `xvfb`, seamed data. It found the per-shot actions off-screen in the first chrome row plus page-level horizontal overflow, and a far-offset Inbox label. Fixes: actions moved to the second chrome row, the viewport gets `min-w-0`, and the Capture PathRow gets a compact label column.
- **Gate re-run:** `gate57` → `vitest 165 passed`, `e2e 13 passed`, exit 0.

## MEU-58 (rows 6–8)

- **Red:** `red58` → `PASS RED vitest: 5 failing assertions cover ['AC-58']`. The new `settings-rail.test.tsx` failed only with a missing-module message. Electron: `PASS AC-58 E2E RED: 3 failing AC-58 specs`.
- **First Green run:** 3 real failures.
  - AC-39.15 and AC-33.16 pin leaf ID strings in `SettingsPage.tsx`. Fixed in production: the row helpers take literal `testId` props.
  - AC-58.6 read the cookie sub-field before the downloader query resolved. Fixed with a sync-only setup repair (`vi.waitFor`); no assertion changed.
- **Green:** `green58` → `176 passed` (AC-51.6 env-bound).
- **Gate:** `gate58` → typecheck, lint, `vitest 176`, build, harness build, `e2e 43 passed`, exit 0.
- **Pre-review screenshot check:** a rail click did not scroll `<main>` (scrollTop stayed 0). Probe: smooth `scrollIntoView` = 0 px, auto = 1809 px in headless Electron. Fix: `revealSection` focuses first, scrolls smoothly, and completes an unmoved scroller instantly after 450 ms. Re-probe: the "Console & logging" click → scrollTop 1809 with the entry current.
- **Gate re-run:** `gate58` → `vitest 176 passed`, `e2e 43 passed`, exit 0. Commit `4154da3`.

## H1

- **H1-1:** `validate-task.sh task-state` → `PASS implementation rows 1-8`.
- **H1-2, first attempt (preserved failure):** `validate-task.sh pregate` at `4154da3` → `FAIL: s26-gate-py-types exit 1`, with `67 errors` all `Import … could not be resolved (reportMissingImports)`.
  - Cause: this fresh container's workspace venv was not synced. The failure is environmental: `git diff --stat 0f51036 HEAD -- packages/ tests/` is empty, so no Python changed in this session.
  - Remedy: `uv sync --all-packages --locked` (exit 0; `uv.lock` unchanged). Then a fresh re-run of the whole pre-gate (`p11cs-pregate-r2.txt`).
- **H1-2, second attempt (preserved failure):** after the sync, `pregate` → `FAIL: s26-gate-py-types exit 1`, with `1 error`: `packages/api/src/avkit_api/routes/captures.py:78` passes a `list[dict[str, object]]` where `list[AnnotationIn]` is expected.
  - This is pre-existing: it comes from `6b40b4d` (MEU-60), `packages/` is unchanged since `0f51036`, and pyright is pinned in `uv.lock`, so Windows fails identically.
  - Remaining stages run individually for the full picture (`s26-rest-*.txt`): py-lint 0, ui-types 0, ui-lint 0, mcp-types 0, task-contract 0, openapi 0, render 0.
  - py-tests: 61 Windows-bound failures in this container.
  - mcp-tests: 2 failed only because `dist/` was not built yet; after `mcp-build`, `215 passed`.
- **Decision A8 (user):** "Fix it here (Recommended)". The one-line `model_validate` fix produced these results:
  - pyright: `0 errors`
  - ruff: 0
  - OpenAPI `--check`: 0
  - equivalence proof (`s26-fix-equivalence.txt`): `EQUIVALENT ['ArrowAnnotationIn', 'RectAnnotationIn', 'HighlightAnnotationIn', 'TextAnnotationIn']`, and both constructions reject an extra field
  - capture tests: the container failure set is identical before and after (23 = 23, `diff` empty)
- **A9:** the container pre-gate omits py-tests, which is authoritative on Windows; both scripts now build MCP before testing it.
- **H1-2, fourth attempt:** `validate-task.sh pregate` at `4c904ef`. The only change since is `task.md`; `ui/`, `packages/` and `mcp-server/` are identical to `16d859a`.
  - The third attempt failed at `task-contract`: brace set literals in the new H1-4 command were read as placeholders. Fixed.
  - Result: **PASS container pre-gate**:
    - py-types 0 errors, py-lint, ui typecheck, ui lint, mcp-types, task-contract
    - `vitest: 669 passed`, with AC-51.6 and AC-41.3 env-bound (671 total)
    - build, harness build, mcp-build, `mcp-tests 215`, openapi, render
    - `e2e: 106 passed`, with 4 capture-picker stub specs env-bound (110 total)

```json
{"schema_version":"evidence.v1","check_id":"s26-pregate","command":"bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh pregate","cwd":"/home/user/av-kit","scope":"container D6 pre-gate (non-authoritative): py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract, ui-tests, ui-build, harness build, mcp-build, mcp-tests, openapi, state-render, ui-electron, source audit; py-tests authoritative on Windows (A9)","phase":"full","exit_code":0,"result":"pass","tested_state":"HEAD 4c904ef + task.md-only edit (code identical to 16d859a)","output":"PASS s26-gate-vitest: 669 passed, env-bound tolerated: AC-51.6, AC-41.3 | PASS s26-gate-mcp-tests | PASS s26-gate-openapi | PASS s26-gate-e2e: 106 passed, env-bound tolerated: 4 capture-picker | PASS container pre-gate (authoritative gate: windows-gate)","fresh":true}
```

- **H1-3:** `validate-task.sh ssot-review` → MEU-57/58 `ready_for_review` via `meu_status.py update`, `render`, `render --check`; grouping Session 26 is "in review" and focus records `ready_for_review`.
  - Doc tests: Vitest `13 passed`, with AC-41.3 env-bound.
  - `s26-doc-pytest: no new failures (container-bound baseline 32, head 32)` (A10).
  - One earlier run stopped because the script invoked itself via a non-executable `"$0"`; fixed with `bash "$0"`.
- **H1-4:** `['packages/api/src/avkit_api/routes/captures.py']`, exit 0 (only the A8 file).
- **H1-5:** after both handoffs gained a "Referenced existing contracts" table: `OK: all 13 plan AC(s) present in the handoff` ×2, exit 0.

### B-H1-6

Reason: human-decision

Decision: [human-gate-decision.md — WINDOWS_GATE is run by Mat](human-gate-decision.md)

`WINDOWS_GATE` is the authoritative Phase 11 exit gate. It runs only on Mat's Windows host (RTK, the region-picker stub `.exe`, and the Windows-bound Python suite), so this row is a planned turn boundary. It becomes `[x]` when `validate-task.sh windows-gate-check` passes on the pushed result. Instructions for Mat:

```powershell
cd P:/av-kit
git pull origin claude/quirky-gates-o1lql2
pwsh -NoProfile -File docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.ps1 -Check windows-gate
git add docs/execution/plans/2026-09-28-p11-capture-settings/windows-gate-result.json
git commit -m "docs(execution): record Session 26 Windows gate"
git push origin claude/quirky-gates-o1lql2
```

#### WINDOWS_GATE attempt 1 — FAILED (preserved)

- Result: `windows-gate-result.json` at `47efbff` (tested commit `2a7eacc`, clean tree, Electron 42.9.3, Node v24.19.0).
- Stages `npm-ci` through `mcp-types` exited 0. `py-tests` (`uv run pytest tests/ -x --tb=short -q`) exited 1: 272 passed, 1 failed, then stopped because of `-x`. The stages after it (`ui-tests` … `source-audit`) did not run, so Vitest and Electron are unverified on Windows.
- Failing test: `tests/tooling/test_framework_adoption.py::test_verifier_bootstrap_accepts_captured_bytes`, which fails with `REFUSE: source revision drift`.
- Root cause: the test pins the live sibling repo `SOURCE = P:/agentic-framework` and `SHA = 003929c…` (lines 18–19). `verify_adoption.py` `source_state()` requires the source's `HEAD` to equal that SHA and its working tree to be clean. `P:/agentic-framework` is now at `fa7f8d4` (one commit ahead) and has one untracked file. Session 26 changes none of this, and the test was added by `d6cd5a3` (framework adoption).
- `validate-task.sh windows-gate-check` on this result: `FAIL: stages [... 'py-tests'] != [full stage list]`, a correct refusal.
- The local agent did not touch `P:/agentic-framework` because it is outside this task's scope. H1-6 stays `[B]` until a human decides how to handle the sibling-repo coupling, and `WINDOWS_GATE` is re-run on a new commit.

#### A11 and WINDOWS_GATE attempt 2 — PASSED

- **A11 (`7613beb`, local agent on Windows, widened per A11-W):** only `tests/tooling/test_framework_adoption.py` changed (+63/−17). File-level pytest went from 91 tests (82 passed, 9 failed) before the change to 91 passed, 0 failed after it. `ruff check` and `ruff format --check` both exited 0.
- **Independent cloud check of A11:** `git diff --stat 4047bfc e05d484` shows only that file and `windows-gate-result.json`. The `def test_*` and `parametrize(...)` lists are identical, and every `assert` line is identical.
- **WINDOWS_GATE attempt 2 (`e05d484`):**
  - `tested_commit` is `7613beb`, with `clean_tree: true`.
  - All 17 stages exited 0 in the required order.
  - Vitest: 671 passed, 0 failed out of 671 (floor ≥ 631). E2E: 110 expected, 0 unexpected, 0 skipped, 0 flaky (floor ≥ 103).
  - Environment: Node v24.19.0, Electron 42.9.3, uv 0.12.5, pwsh 7.6.6, rtk 0.42.2, with `ELECTRON_RUN_AS_NODE` cleared before the run.
- **`validate-task.sh windows-gate-check`:** `PASS windows gate @ 7613beb…: vitest {'passed': 671, 'failed': 0, 'total': 671} e2e {'expected': 110, 'unexpected': 0, 'skipped': 0, 'flaky': 0}` (receipt `p11cs-windows-gate-check.txt`). H1-6 is now `[x]`.
- **Container `doc-tests` versus `1f9b035` (preserved failure):** `FAIL: new failures ['…rejects_path_escape[../outside.txt]', '…rejects_path_escape[P:/outside.txt]']`. At base these passed for the wrong reason, because the missing source produced `PosixPath('P:/agentic-framework')` in the refusal text. Now they reach `rtk`, which is absent here. A pass-through `rtk` shim still leaves 26 container-only failures. Resolution: amendment A10-R moves the container baseline to `7613beb`.

## H1-7 execution review

- **Round 1** (Fable 5.1 subagent): `changes_required`. Four findings: 1 Medium blocking (AC-57.7 editor keys act on marks while the confirm strip holds focus) and 3 Low.
- **Corrections:** all four findings were addressed test-first. See `Corrections Applied` in `.agent/context/handoffs/2026-09-28-p11-capture-settings-implementation-critical-review.md`.
  - The 4 new tests fail on the pre-fix source for the asserted reasons (receipt `p11cs-r1c-red-on-prefix.txt`).
  - Green on the corrected tree, with typecheck and lint at exit 0.
  - The container pre-gate passed (Vitest 673 + 2 tolerated; E2E 106 + 4 tolerated).
- **Next:** `ui/` changed, so `WINDOWS_GATE` attempt 3 is needed on the correction commit. After that comes Round 2.

#### WINDOWS_GATE attempt 3 — FAILED (preserved)

- Result: `windows-gate-result.json` at `fe86ac3`; tested commit `1356c59` (Round 1 corrections), clean tree, same environment as attempt 2.
- Stages: 15 exited 0, through `state-render`. `ui-electron` exited 1, and `source-audit` did not run. Vitest 675/675. E2E: 109 expected, 1 unexpected, 0 flaky.
- Failing test: `ui/tests/e2e/download-queue.test.ts:1155`, AC-49.26 (MEU-49). The live region was empty where the dragged title was expected. The local agent's diagnostic re-run, `--repeat-each=5` on Windows, gave 4 passed and 1 failed. That failure had a different symptom: the region said `"DL-1" was moved to position 2 of 4.` where position 3 was expected.
- Container reproduction: `--repeat-each=15` under xvfb gave 15/15 passed. The race does not reproduce on Linux.
- Session 26 did not cause this. Neither the queue code nor the test has changed since attempt 2 (`7613beb`), where the test passed. Round 1 changed only Capture, Settings and an additive `SegmentedControl` `label` prop; the downloader passes no `label`, so its `aria-label` is unchanged.
- Working hypothesis (not proven): the test's drag helpers race layout timing on Windows.
  - `grabRow` presses on the handle's bounding box without waiting for layout to settle, and never confirms the drag activated. dnd-kit sets `aria-pressed="true"` on the handle when it does. A missed activation leaves the region empty.
  - `dragOver` reads the target box once and moves there while sortable transforms may still be animating, so `closestCenter` can resolve the neighbouring row, giving position 2.
- Status: H1-6 is back to needing a passing gate. A fix needs human approval, because it is a test change outside Session 26's scope.
- **A12 (human-approved, "Harden helpers"):** only `grabRow` and `dragOver` in `ui/tests/e2e/download-queue.test.ts` changed. There are two new helpers:
  - `settledCenter` aims at the transform-agnostic centre once it has held still for two animation frames.
  - `rowTransitionsIdle` waits for row transitions to finish.

  `grabRow` now waits for the handle's `aria-pressed="true"`, so the drag is known to be active. `dragOver` re-aims after the sortable shift only if the layout moved. The diff touches no `expect(` or `test(` line. The helpers are shared by AC-49.25, AC-49.26, AC-49.28 and W1-14.
- Container evidence:
  - eslint and tsc both exit 0.
  - `-g "AC-49.2[5-8]" --repeat-each=5`: 20 passed (receipt `p11cs-a12-repeat-container.txt`).
  - Full `download-queue.test.ts`: 24 passed (`p11cs-a12-file-container.txt`).
  - The container never reproduced the race, so the Windows repeat run is the evidence that counts.

#### A12 repeat check on Windows — 1 failure in 100 (preserved)

- Local agent, `1442d73`, `-g "AC-49.2[5-8]|W1-14" --repeat-each=20` (5 specs × 20): 99 passed, 1 failed, 0 flaky, in 26.9 minutes.
  - AC-49.25, AC-49.26, AC-49.28 and W1-14 passed 20/20 each, so the A12 pointer fix held.
  - AC-49.27 (keyboard drag, unchanged by A12) failed on repetition 14 at `:1269`. It expected `/position 2 of 4/i` and got `Dragging "DL-1" was cancelled. It returned to position 1 of 4.`, stable for 5 s.
  - A targeted 20× re-run passed 20/20. The error-context folder of the failing run was lost: Playwright empties `ui/test-results/` at the start of every run.
  - The gate (attempt 4) was not run.
- Mechanism: dnd-kit 6.3.1 cancels on `resize` and `visibilitychange` (`KeyboardSensor.attach`). The main window is `show: false` until `loadFile` resolves (`src/main/index.ts:455-499`). A temporary container probe (5 launches, file deleted afterwards) recorded one `resize` after every launch, 1280×800 → 1280×773, within 2–22 ms of the page being reachable. A late resize on a loaded host after the Space pickup produces exactly this cancel text.
- **A13 (human-approved):** adds `windowSettled(page)` (visible, and 500 ms with no resize), called at the start of `grabRow` and in AC-49.27 before focus. The diff is +30 lines with no removals, and touches no `expect(` or `test(` line. eslint and tsc exit 0.
- Container evidence after A13: `-g "AC-49.2[5-8]|W1-14" --repeat-each=5` gave 25 passed (`p11cs-a13-repeat-container.txt`), and the full `download-queue.test.ts` gave 24 passed (`p11cs-a13-file-container.txt`). The Windows 20× repeat check is still the evidence that counts.

#### A13 repeat check PASSED; WINDOWS_GATE attempt 4 FAILED at py-tests (preserved)

- A13 repeat check (Windows, `52ec926`): 100 passed, 0 failed, 0 flaky. AC-49.25, AC-49.26, AC-49.27, AC-49.28 and W1-14 each passed 20/20.
- Attempt 4 (`706cdc7`, tested `52ec926`): 7 stages exited 0. `py-tests` exited 1 (605 passed, 1 failed, 158 s) at `tests/unit/test_services.py:2140` `test_ac_12_7…`, `assert 0 == 1`. Nothing after it ran.
  - The JSON's `vitest` and `e2e` fields are attempt 3's stale receipts and are **invalid** (A15).
- Root cause: a test race, proven with a scratch probe (`scratchpad/probe-ac127`, no repo change). With contender b delayed 0.5 s, the old ordering gives `['a-ok', 'b-ok']` (`0 == 1`). Joining before the release gives `['a-ok', 'b-conflict']`. The service check-and-set is under `self._lock` (`models.py:88-108`).
- **A14 (human-approved):** in `test_ac_12_7`, the contenders are joined before `catalog.release.set()`. `ruff check` passes. `ruff format --check` flags only drift already present at HEAD, not these lines; the gate runs `ruff check`. Container: 50× repeat, 0 failures (`p11cs-a14-repeat-container.txt`). Whole file: 65 passed.
- **A15 (plan tooling):** `validate-task.ps1` deletes the Vitest and E2E receipts before the run, and reads each only if its stage ran.

#### A14 checks PASSED; WINDOWS_GATE attempt 5 FAILED at ui-electron (preserved)

- A14 checks (Windows, `eb3acc9`):
  - `-k test_ac_12_7` ×50 (2 tests each): fails=0.
  - Full Python suite without `-x`: 608 passed, 0 failed.
- Attempt 5 (`7151fcb`, tested `eb3acc9`): all stages through `state-render` exited 0, including py-tests. Vitest 675/675, fresh (the A15 clearing ran). `ui-electron` exited 1: E2E 109 expected, 1 unexpected, 0 flaky. AC-49.25 at `:1236` sent exactly one PUT with body `[dl-2, dl-1, dl-3, dl-4]`, so dl-1 dropped over dl-2. `source-audit` did not run.
- Root cause, reproduced in a temporary container probe (removed afterwards): dnd-kit's DragEnd handler reads `sensorContext.current.over`, which is committed two renders after a pointermove. Moving to dl-3's centre and dispatching `pointerup` in the same task, while `over` was dl-2, gave `[dl-2, dl-1, dl-3, dl-4]` 3/3, which is attempt 5's body. CPU throttling (8× and 20×) did not reproduce it, as expected: throttling slows input and render equally.
- **A16 (human-approved):** `dragOver` now ends by waiting for the committed-over announcement `moved to position N of M`. The diff is +13 lines, with no `expect(` or `test(` line touched. eslint and tsc exit 0. The same immediate-release probe then gives `[dl-2, dl-3, dl-1, dl-4]` 3/3 (`p11cs-a16-probe.txt`).
- Container evidence after A16: `-g "AC-49.2[5-8]|W1-14" --repeat-each=5` gave 25 passed (`p11cs-a16-repeat-container.txt`), and the full `download-queue.test.ts` gave 24 passed (`p11cs-a16-file-container.txt`). The Windows repeat check is still the evidence that counts.

#### A16 checks PASSED; WINDOWS_GATE attempt 6 FAILED at py-tests on registry drift (preserved)

- A16 checks (Windows, `f680e75`):
  - Drag repeat: 100 passed, 0 failed, 0 flaky (AC-49.25 to AC-49.28 and W1-14, 20/20 each).
  - Full Electron suite `--repeat-each=2`: 220 passed, 0 failed, 0 flaky.
- Attempt 6 (`ded5af4`, tested `f680e75`): 7 stages exited 0, and `py-tests` exited 1 (333 passed, 1 failed, stopped by `-x`). Vitest and E2E were `null` because those stages did not run; A15 is confirmed.
  - Failing test: `tests/tooling/test_framework_adoption.py::test_review_pipeline_wrapper_refuses_before_provider[same-vendor]`. It expected `vendor_diversity_violation` and got `overlay_not_validated: … records registry 7e85d6f3… Run resolve_model.py sync to revalidate`.
- Root cause: environment drift outside av-kit. `P:/.agent/model-registry.json` was edited on 2026-09-29 at 18:07 (zorivest `independent_reviewer`/`translator_prose` on codex-cli, gpt-6-sol → gpt-6.1-sol; `P:/.agent/CHANGELOG.md`). Its sha256 is now `b06d7cda…`. av-kit's tracked overlay still records `7e85d6f3…`, and the resolver refuses a stale overlay by design. av-kit's own bindings (for example `avkit_independent_reviewer` codex-cli `gpt-5.6-sol`) do not reference the bumped entries.
- **A17 (human-approved):** the local agent revalidates only the overlay's `validated_against`. The coupling is filed as `TOOLING-SHARED-REGISTRY-COUPLING`.

#### A17 and WINDOWS_GATE attempt 7 — PASSED

- **A17 (`cb864f3`, local agent):**
  - Command: `resolve_model.py validate --overlay P:/av-kit/.agent/model-registry.local.yaml --strict --write-compiled`. This is the resolver's project-scoped path; `--write-compiled` writes only the overlay's sibling `.local.json`. `sync` was not run.
  - Resolver output: `ok … added_classes=[avkit_builder, avkit_coordinator, avkit_independent_reviewer, avkit_router, avkit_verifier] tightened_classes=[]`.
  - Diff: exactly one line, `validated_against` `7e85d6f3…` → `b06d7cda…`, which equals `sha256(P:/.agent/model-registry.json)`.
  - The `P:/.agent` file-hash listings before and after are identical.
  - Full Python suite without `-x`: 608 passed, 0 failed.
- **WINDOWS_GATE attempt 7 (`f4c1a12`, tested `cb864f3`, clean tree):** all 17 stages exited 0. Vitest 675/675. E2E: 110 expected, 0 unexpected, 0 skipped, 0 flaky.
- **Cloud check:** `windows-gate-check` gives `PASS windows gate @ cb864f3…: vitest {'passed': 675, 'failed': 0, 'total': 675} e2e {'expected': 110, 'unexpected': 0, 'skipped': 0, 'flaky': 0}` (receipt `p11cs-windows-gate-check.txt`). Round 2 of the execution review follows.

## H1-7 and H2

- **H1-7:** execution review Round 2 `approved`, with 3 Low non-blocking findings. R2-3, the clerical H1-6 prose, was fixed. `review-check … execution 6` gives `PASS execution review approved round 2 by claude-fable-5-1-subagent` (receipt `p11cs-exec-review.txt`).
- **H2-1:** reflection `docs/execution/reflections/2026-09-28-p11-capture-settings-reflection.md`. The validator reports all 14 template sections, all 7 schema fields, and 3 sourced design rules (`p11cs-reflection.txt`).
- **H2-2:** MEU-57/58 are `approved`, and the render check passes. The grouping row for Session 26 is `approved`. The hub Phase 11 row is ✅ Completed (2026-09-30), and its Next line reads "No pending MEU". `current-focus.md` and the metrics row are updated. `meu_status.py next` is empty and `stats` reports 61/61 complete, which is why A18 was needed.
  - `validate-task.sh post-review-state` passes: `PASS MEU STATE: 9 MEU expectations hold`; `PASS POST-REVIEW: … agree on none`; `s26-doc-tests` 13 passed; `s26-doc-pytest` shows no new failures; `PASS POST_REVIEW_STATE, DOC_READING_TESTS and PHASE11_EXIT_PREDICATE` (`p11cs-post-review.txt`).
- **H2-3:** `lint_task_contract.py` and `plan_checks.py rows` both pass on the final `task.md` (receipt `p11cs-closeout.txt`). Commit-message draft for a squash of this branch, for the human to use; no merge was performed:

```text
feat(ui): Phase 11 Capture and Settings page layout (MEU-57, MEU-58)

Session 26 p11-capture-settings, the Phase 11 exit.

- Capture: filmstrip labels, inline confirm strip (editor keys inert while
  it holds focus), dirty-only "Save overlay", Settings disclosure, keycap.
- Settings: sticky section rail with scroll-spy and click-to-reveal,
  save-mode captions, chip lists, readiness count, native selects.
- Shared: additive PathRow readOnly and SegmentedControl label props.
- API: typing-only CaptureShotDetailOut construction fix (A8).
- Tests hardened under explicit approval: framework-adoption fixture
  repo (A11), MEU-49 drag helpers (A12, A13, A16), test_ac_12_7
  ordering (A14); overlay revalidated against P:/.agent (A17).

Independent review: plan r2 and execution r2 approved (Fable 5.1).
Authoritative Windows gate attempt 7 @ cb864f3: 675 Vitest, 110 Electron.
All 61 MEUs complete.
```
