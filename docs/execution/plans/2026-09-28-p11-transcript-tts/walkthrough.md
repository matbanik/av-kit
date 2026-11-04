# Walkthrough — 2026-09-28-p11-transcript-tts

Execution was authorized by the user's direct message "execute" (Claude Code web session, 2026-09-28). That followed the plan-review Round 3 `approved` verdict (`.agent/context/handoffs/2026-09-28-p11-transcript-tts-plan-critical-review.md`, commit `1ed5c7b`). Receipts are written to `$RECEIPTS_DIR` = the session scratchpad `receipts/`.

## Prerequisites (row 1)

- **Context-tool gate (execution recheck)**: `not_applicable`. `graphify-out/` and `graphify-out-research/` are still absent (`ls` exit 2), and there is no Headroom install. The scope is unchanged from planning.
- **Dependencies**: `npm --prefix ui ci` exit 0; 676 packages. The Electron postinstall silently left no binary.
- **`ELECTRON_SETUP`**: `validate-task.sh electron-setup` → `PASS electron-setup`. Electron 42.9.3 is present, checksum-verified (`46fc1cd5…`, matching `checksums.json`), and `--version` runs under `xvfb-run` with `ELECTRON_DISABLE_SANDBOX=1`.
- **`prereq`**: `PASS prereq`. SSOT shows MEU-49/51/52 `approved` and MEU-55/56 `pending`; Node v22.22.2; `electron@42.9.3`.

```json
{"schema_version":"evidence.v1","check_id":"s25-prereq","command":"bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh prereq","cwd":"/home/user/av-kit","scope":"SSOT prerequisites, node_modules, Electron launchability","phase":"static","exit_code":0,"result":"pass","tested_state":"HEAD 1ed5c7b","output":"PASS SSOT prerequisites {'MEU-49': 'approved', 'MEU-51': 'approved', 'MEU-52': 'approved', 'MEU-55': 'pending', 'MEU-56': 'pending'} ... v42.9.3 PASS prereq","fresh":true}
```

## Amendment census (row 1)

The census grepped `ui/tests` for every moved Transcript/TTS test ID and for source-text pins on the files this plan modifies (`QueueCard.tsx`, `QueueCardMenu.tsx`, `QueueList.tsx`, `QueueHeaderRow.tsx`, `ProgressBar.tsx`, `status-tokens`, `TranscriptPage`, `TTSPage`, `test-ids.ts`).

| Suite / assertion | Class | Disposition |
|---|---|---|
| `e2e/transcript-queue.test.ts` W2-3 (`:239-260`) | A, B | TA-3 |
| `e2e/transcript-queue.test.ts` W2-4 (`:262-285`) | B | TA-4 |
| `e2e/transcript-queue.test.ts` W2-5 (`:287-452`) | A, B | TA-5 |
| `e2e/transcript-queue.test.ts` W2-1, W2-2, W2-6 | — | unaffected (navigation; palette focuses `channel-input`) |
| `e2e/tts-generate.test.ts` W2-3 (`:246-264`) | A, B | TA-6 |
| `e2e/tts-generate.test.ts` W2-4 (`:266-294`), W2-5 (`:296-359`) | A, B | TA-7 (the ledger at `:340-356` is byte-identical) |
| `e2e/tts-generate.test.ts` W2-1, W2-2, W2-6 | — | unaffected |
| `unit/layout-primitives.test.ts` AC-51.7 (`:218-224`) | D | TA-1 |
| `unit/queue-primitives.test.ts` STATUS_COLORS census (`:402-407`) | C | TA-2 |
| `unit/transcript-page.test.ts` (frozen) | — | Unaffected, provided the `transcriptSources()` scan (all of `features/transcript/`) keeps: `channel_name`/`video_count`/`transcripts_done`/`word_count`/`output_dir`; no `video_ids\|queue-table\|TanStack`; `stop-btn` present with no `cancel-btn`; `createPortal` + `document.body` + Escape; no `Batch `/`batch_index`; no `<select`; no hex classes; no TODO; the WAVE2 IDs literal in the page and `test-ids.ts`. |
| `unit/tts-page.test.ts` (frozen) | — | Unaffected, provided the `ttsSources()` scan keeps: no `stop-btn`/`tts:stop`; `segments_done`/`segments_total` present and **no `runtime\.fraction`**; `SelectInput` + `getG30Styles` with no raw `<select`; `openPath` + `showItemInFolder`; the WAVE2 IDs literal in `TTSPage.tsx` and `test-ids.ts`. |
| `unit/queue-header-row.test.tsx` (frozen) | — | Must pass unedited (AC-55.2). |
| `unit/bulk-action-bar.test.ts:304-308`, `convert-page.test.ts:751-754`, `downloader-page.test.ts:513-515,546-549` | — | `SOURCE_PINS`; in REG55. |
| `unit/queue-card.test.ts:483-488` | — | `SOURCE_PINS`; in REG55. |
| `unit/help-card.test.ts:104-105` | — | `SOURCE_PINS`; in REG55/REG56. |
| `unit/queue-canon.test.ts` AC-41.4 (`:184-206`) | — | **New for execution**: no line may pair selected state with `bg-bg-subtle`. The `VOICE_LISTBOX` selected fill uses the allowed `bg-accent/10`, and the suite is added to REG55/REG56. |
| `unit/queue-canon.test.ts` AC-41.3, `unit/layout-primitives.test.ts` AC-51.6 | — | `ENV_BOUND_TESTS` (container only). |
| `unit/convert-controls.test.ts` AC-45.12, `queue-primitives.test.ts:378-387` | — | Unaffected by the new `PROGRESS_FILL_CLASSES` export (verified by reviewer Round 2). |
| `unit/app-shell-wiring`, `e2e-wiring`, `shell-home`, `e2e/download-queue` W1-2/W1-6 | — | Navigation-only references; unaffected. |

No existing assertion needs an edit outside TA-1..TA-7.

## Execution amendments (from plan review Round 3 Low findings F7–F10)

These tighten checks without widening scope. They were applied before any product edit:

- **F7**: `vitest_env_ok` now tolerates AC-51.6 only if the rest of AC-51.6 also holds (uniqueness, disjointness, the five primitive IDs, replicated from `layout-primitives.test.ts:190-196`). It tolerates AC-41.3 only if `ui/src/renderer/src/styles.css` is unchanged since `f7d3134`. It fails on any "Unhandled Error/Rejection" in the text receipt. Synthetic JSON cases were re-run: env-only exit 0; env+real exit 1; wrong AC-51.6 signature exit 1; unhandled rejection exit 1.
- **F8**: `windows-gate-check` also requires no uncommitted or untracked changes under `ui/`, `packages/` and `mcp-server/`.
- **F9**: `validate-task.ps1` changes:
  - It sets `$PSNativeCommandUseErrorActionPreference = $false`.
  - It excludes a leftover `windows-gate-result.json` from `clean_tree`.
  - It records `lockfile_sha256` and the Electron version.
  - It fails when `ui-tests`/`ui-electron` ran without JSON.
- **F10**:
  - **H1-6 status handling**: at the H1-6 stop, H1-6 is `[B]` (human decision; durable link [human-gate-decision.md](human-gate-decision.md)). It becomes `[x]` only when `windows-gate-check` passes.
  - **`npm ci` exit status**: a nonzero `npm ci` in row 1 would be tolerated only for the Electron postinstall abort, and only when followed by a passing `electron-setup`. Here `npm ci` exited 0.
  - **Decision record**: the presented option (c) text is now quoted in `human-gate-decision.md`.
- **Census**: `queue-canon.test.ts` was added to REG55/REG56 (see the table above).

## Execution amendments (H1-2 pre-gate, first run)

The first container pre-gate passed typecheck, lint, the full Vitest suite (628 passed, with only the two `ENV_BOUND_TESTS` tolerated) and the build. Its full Electron stage then reported 98 passed and 5 failed. Both failure causes are environmental and existed before this change:

- **`e2e/layout-primitives.test.ts` AC-51.7** needs the isolated MEU-51 harness build in `ui/out-e2e` (Session 23 `E2E_HARNESS`: `AVKIT_PRIMITIVE_HARNESS_BUILD=1 npm --prefix ui run build -- --outDir <abs>/ui/out-e2e`). Neither this plan's pre-gate nor `validate-task.ps1` produced it. This is a gap in the gate procedure, not a product defect.
  - **Fix**: both gates now run a `harness_build` / `ui-harness-build` stage before Electron.
  - `windows-gate-check` now expects the stage order `npm-ci, ui-types, ui-lint, ui-tests, ui-build, ui-harness-build, ui-electron, source-audit, width-audit`.
- **`e2e/capture-picker.test.ts`** (4 specs) needs `native/region-picker-stub/publish/avkit-region-picker-stub.exe`, built by `build:picker-stub` (`dotnet publish … -r win-x64`). That is Windows-only. The failure is `the deterministic sidecar stub is missing`.
  - **Fix**: the container pre-gate adds `ENV_BOUND_E2E` (`electron_env_ok`). It tolerates exactly these specs, and only when the platform is not Windows, the stub is absent, and the failure message is that stub assertion. Synthetic Playwright JSON checks: stub-missing only → exit 0; another capture failure → exit 1; stub-missing plus a Transcript failure → exit 1.
  - `WINDOWS_GATE` tolerates no failure; Mat's machine has run these specs before (Session 24: 95 Electron passed).

Neither amendment changes a product file or a test file. They change only this plan's gate scripts, under the user's (c) decision that the authoritative gate is the Windows one.

## H1-2 container pre-gate (passed)

The second run was on HEAD `548bc2a`; the code is identical at `7142719`, which changed only this plan's gate scripts.

- **Typecheck, lint**: pass.
- **Vitest**: 628 passed; only the two `ENV_BOUND_TESTS` tolerated, each with its proven signature.
- **Build and `out-e2e` harness build**: pass.
- **Electron**: 103 specs, 99 passed. The 4 capture-picker specs failed on the absent Windows-only stub.
  - Three failed with the stub-missing guard. The fourth ("the sidecar stub writes a real PNG") failed with `spawn …avkit-region-picker-stub.exe ENOENT`, the same absent executable.
  - The `ENV_BOUND_E2E` signature was widened to accept either message, and only with the stub's own path. It was re-applied to that run's Playwright JSON: `PASS s25-gate-e2e: 99 passed, env-bound tolerated: [4 capture-picker specs]`.
  - Negative synthetic cases still exit 1.
- **Source audit (10 files) and page width audit**: pass. These ran separately because the first attempt stopped at the Electron stage.

```json
{"schema_version":"evidence.v1","check_id":"s25-pregate","command":"bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh pregate (+ electron_env_ok re-evaluation of the same run's JSON; + audit lines)","cwd":"/home/user/av-kit","scope":"container pre-gate: typecheck, lint, full Vitest, build, harness build, full Electron (xvfb, ELECTRON_DISABLE_SANDBOX=1), source/width audit","phase":"full (non-authoritative; WINDOWS_GATE is authoritative)","exit_code":0,"result":"pass","tested_state":"548bc2a (code-identical to 7142719)","output":"PASS s25-gate-vitest: 628 passed … PASS s25-gate-harness-build … PASS s25-gate-e2e: 99 passed, env-bound tolerated: 4 capture-picker specs … PASS source audit (10 files) and page width audit","fresh":true}
```

## H1-6 first Windows attempt (premature; not recorded as the gate)

Mat's local agent started `WINDOWS_GATE` on `548bc2a` before the container pre-gate had finished. That was also before `7142719` added the `ui-harness-build` stage, so its result could not pass `windows-gate-check`. The agent did not push it and synced the branch to `7142719`.

**What that run showed**:
- `npm ci`, typecheck, lint, full Vitest (630/630, with AC-51.6 and AC-41.3 passing on Windows as expected) and the build all passed.
- Electron: 102 passed, 1 failed. The failure was **`download-queue.test.ts` AC-49.26**: the dnd-kit live region was empty when checked during a pointer drag.
- It passed 3/3 when rerun alone on Windows.
- The source and width audits did not run, because the script stops at the first failure.

**Assessment: not attributable to this change. It is still not proven to be a flake, so the gate must be rerun.**
- **Unchanged path**: the announcement comes from `DndContext accessibility.announcements = createQueueAnnouncements(items…)` in `QueueList.tsx:366-371`. That code, `queue-dnd.ts` and the drag handle are unchanged by this session.
- **The only `QueueList` edit** is `...cardSlots?.(job)` in the shell's per-row props (`:209`). Downloader passes no `cardSlots`, so it spreads nothing.
- **`QueueCard` without slots** renders byte-identical markup to the pre-change capture (AC-55.1 baseline test).
- **Container record**: AC-49.26 passed in every full Electron run here, on the MEU-55 regression run and on the second pre-gate (`ok: true`).
- **History**: the MEU-49 handoff and the reflections record no earlier flake of this test.

The rule is that a failing test is not written off as a flake, and the authoritative gate tolerates no failure. So H1-6 stays `[B]` until one clean `WINDOWS_GATE` run on the current HEAD passes. If AC-49.26 fails again in a full run, the next step is to root-cause it, most likely pointer-activation timing under a full-suite load, before any review dispatch.

## H1-6 Windows gate rerun (authoritative)

Mat's local agent reran `WINDOWS_GATE` on `7dab4d1` (08:06–08:20 EDT) and pushed `windows-gate-result.json` as `56bf0f7`. It left `task.md` H1-6 for the coordinator to mark after checking the result against the code.

- All nine stages exited 0: `npm-ci, ui-types, ui-lint, ui-tests, ui-build, ui-harness-build, ui-electron, source-audit, width-audit`.
- Vitest 630/630. Electron 103 expected, 0 unexpected, 0 flaky. **AC-49.26 passed in the full run.**
- Tree clean; lockfile `A86D9A42…2980`; electron@42.9.3; node v24.19.0.

**Concurrent-agent check.** While the gate was running, a Claude desktop-app thread ("Windows gate rerun for P11") opened a Remote Control session on `P:/av-kit` to run the same gate. A second thread ("Harden AC-49.26") was started to stress-test that spec.
- The local agent confirmed that neither thread touched this checkout. After the run, the tree was clean at `56bf0f7`, the `C:/Temp/av-kit/s25-win-*` receipts were all from the 08:06–08:20 run, and no av-kit Electron, Playwright or gate processes were running.
- Mat stopped the gate-rerun thread's Remote Control session. The Harden thread was to be stopped from its own thread.
- Project rule noted: only one local agent works in `P:/av-kit` at a time.
- **If a Harden AC-49.26 commit appears on this branch, it is not part of the reviewed state.** Its scope should be handled after H2.

## Execution review Round 1 corrections

The Round 1 verdict was `changes_required`: 1 Medium (blocking) and 1 Low. See `.agent/context/handoffs/2026-09-28-p11-transcript-tts-implementation-critical-review.md`.

- **Finding 1 (Medium, AC-55.5)**: the ▲ ▼ focus-restoration effect returned early when the order was unchanged. After a *rejected* reorder, focus therefore stayed on `body`.
  - **Red**: a new regression test, `AC-55.5 focus returns to the card after a rejected reorder too`. It holds the PUT, proves focus is lost, releases a 409, and expects focus on Bravo's ▲. It failed on the unchanged page with `expected <body> to be <button>`.
  - **Fix**: `TranscriptPage.tsx` no longer has the order-unchanged early return, and the unused `from` field is gone. Once the command settles, successful or not, the effect re-finds the card by `data-job-id` and focuses the same-direction button, or the other one if that is disabled. This matches the Session 24 `QueueList` fallback.
  - **Green**: `green-55` 171 passed, with only the two env-bound unit tests tolerated. `static` passed.
- **Finding 2 (Low, clerical)**: W2-5's `test.setTimeout(120_000 → 180_000)` is a setup-only *time budget* that goes with TA-5's added kebab clicks. It is not one of TA-5's declared interaction-path edits, and it is recorded here as an execution amendment. Evidence: under the Transcript seam every click settles in ~2.0 s (55 clicks, 1.93–2.05 s in a W2-5 trace), versus 0.05 s under the Downloader seam. The untouched W2-6 already takes 7 s for three clicks. No assertion changed.
- **Gate tooling fix**: the `amendments` guard compared against `HEAD`. Once this plan's own new test files were committed, a later edit to them read as a "pre-existing test outside TEST_AMENDMENTS". The guard now diffs against the pre-session baseline `0f51036` and checks existence there. Result: PASS; frozen suites untouched; pre-existing files changed only within TA-1..TA-7.

Because `ui/` changed, the container pre-gate and `WINDOWS_GATE` rerun before the Round 2 dispatch (task H1-7 rule).

### Round 1 corrections: container pre-gate rerun (passed)

```json
{"schema_version":"evidence.v1","check_id":"s25-pregate-r1","command":"bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh pregate","cwd":"/home/user/av-kit","scope":"container pre-gate after the Round 1 fix","phase":"full (non-authoritative)","exit_code":0,"result":"pass","tested_state":"d9ff880 + Round 1 working-tree fix (committed unchanged as 9fb0153)","output":"PASS s25-gate-vitest: 629 passed, env-bound tolerated: [AC-51.6, AC-41.3] … PASS s25-gate-harness-build … PASS s25-gate-e2e: 99 passed, env-bound tolerated: [4 capture-picker specs] … PASS container pre-gate (authoritative gate: windows-gate)","fresh":true}
```

H1-6 has been reopened: `WINDOWS_GATE` must rerun on the corrected code before the Round 2 dispatch.

## H1-6 Windows gate on the Round 1 fix (`c315640`)

### Run 1: failed at `ui-electron` (not pushed)

Mat's local agent ran `WINDOWS_GATE` on `c315640`. The first six stages exited 0: `npm-ci`, `ui-types`, `ui-lint`, `ui-tests` (Vitest 631/631), `ui-build` and `ui-harness-build`. `ui-electron` exited 1 with 102 passed and 1 failed, so the audits did not run. Nothing was pushed.

- The failure was **`capture-inbox.test.ts` W9-3** (`capture controls visible interact tools fill inbox and settings`). It was the 3rd test in the run and failed after 1.0 m with `Test timeout of 60000ms exceeded`. The run also reported `Worker teardown timeout of 60000ms exceeded` and `1 error was not a part of any test`.
- Every Transcript and TTS spec passed, including AC-55.7, AC-56.6 and W2-5 (1.8 m).
- **Evidence caveat**: W9-3's `error-context.md` from this run is lost. Three single-spec reruns cleared `ui/test-results/` before the folder was copied. What remains shows only the test timeout and the worker-teardown timeout, with no step data. The run's receipts and Playwright JSON are saved on Mat's machine.

**Assessment: an environment hang, not attributable to this change.** It is not asserted to be a flake, and one rerun was allowed on that basis.
- **No code overlap.** W9-3 exercises Capture and Settings only. Neither imports any file this session changed (the queue components, `ProgressBar`, `status-tokens`, and the Transcript and TTS features). The local agent's `git diff main...HEAD` touches no capture, main, preload or e2e-helper file.
- **Passed before on this branch.** W9-3 passed in the `7dab4d1` Windows gate (22.5 s), in the Round 1 container pre-gate (25.1 s), and 3/3 when run alone on Windows (23–27 s). The Round 1 fix changed only Transcript focus handling.
- **Shape of the failure.** A launch or teardown hang (test timeout plus worker-teardown timeout plus an out-of-test error) on the 3rd test of the run, not a wrong assertion. The leading suspect was a concurrent local agent: earlier the same morning a desktop-app thread had opened a duplicate gate run on `P:/av-kit`, and a "Harden AC-49.26" thread was active.

### Run 2: passed (authoritative), result `692b483`

Before the rerun, the local agent confirmed that no Electron, Playwright or av-kit processes were running, and the Harden thread was to be paused. It then reran `WINDOWS_GATE` on `c315640` (11:20–11:35 EDT) and pushed `windows-gate-result.json` as `692b483`.

- All nine stages exited 0, source and width audits included.
- Vitest 631/631 (630 plus the Round 1 regression test). Electron 103 expected, 0 unexpected, 0 skipped, 0 flaky. W9-3 passed in 22.5 s.
- Tree clean; lockfile `A86D9A42…2980`; electron@42.9.3; node v24.19.0.
- `validate-task.sh windows-gate-check` passed in the container against HEAD `692b483`. `git diff c315640 692b483` changes only `windows-gate-result.json`, so the gated code is the code under review.

```json
{"schema_version":"evidence.v1","check_id":"s25-windows-gate-r1","command":"pwsh -NoProfile -File docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.ps1 -Check windows-gate; then bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh windows-gate-check","cwd":"P:/av-kit (Windows) / /home/user/av-kit (check)","scope":"PROFILE D6 UI fresh full gate after the Round 1 fix","phase":"full","exit_code":0,"result":"pass","tested_state":"c315640d05cc7ddf8293c8f0b64733c209bb0028 (code-identical to 692b483)","output":"PASS windows gate @ c315640d05cc7ddf8293c8f0b64733c209bb0028: vitest {'passed': 631, 'failed': 0, 'total': 631} e2e {'expected': 103, 'unexpected': 0, 'skipped': 0, 'flaky': 0}","fresh":true}
```

H1-6 is closed. Execution review Round 2 is dispatched against `692b483`.
