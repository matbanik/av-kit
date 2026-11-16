---
date: "2026-11-15"
project: "2026-11-15-e2e-harness-hardening"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-e2e-harness-hardening/implementation-plan.md"
build_plan_section: "none (test-harness debt; no MEU, D-815)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-15-triage-tool-fixes-handoff.md"
---

# Handoff: 2026-11-15-e2e-harness-hardening-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. This is Session 78 of the post-rc.3 triage residuals grouping (`.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` §3, `:164-172`). It works four test-harness issues: `E2E-MAIN-PROCESS-ERRORS-UNWATCHED`, `E2E-ELECTRON-LAUNCH-FLAG`, `UI-ELECTRON-LAZY-INSTALL-RACE` and `CAPTURE-HINT-TEST-PRESENCE-ONLY`.

**Goal anchor:** every Electron E2E launch goes through one helper that drops `ELECTRON_RUN_AS_NODE` from the environment it passes and fails the test when the main process throws an uncaught exception; Vitest installs the Electron binary once, before any worker starts; and Capture's AC-97.4 hint tests fail when the Save or Region chord is wrong.

**Execution gate.** `plan_to_exec_gate: human`. The plan review approved at round 3 (`.agent/context/handoffs/2026-11-15-e2e-harness-hardening-plan-critical-review.md`). Mat, 2026-11-15: "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions." After the plan review approved, the coordinator wrote those words into the plan's Status line (`implementation-plan.md:15`). That line is the only change made to the plan after its approval.

**Order and starting tree.** Row 0 first ran on `263f635` and stopped on the picker stub's NuGet restore (D-1033). While it waited, the coordinator ran Session 79 (`triage-tool-fixes`) and committed it as `cda7291`. Row 0's second run, on `cda7291`, stopped on C1-5 (D-1034), which Mat had fixed outside this session and the coordinator committed as `ebe68e4`. Every later row ran on `main` at `ebe68e4`, which `HEAD` still is. `origin/main` was `cda72910406eb5112a872b5ba9b3c4fb378dd94f` when last read; Mat pushes on his own. The untracked plans and plan reviews of Sessions 80 to 83 sit in the same tree, and this session left them alone. Every scope check binds to row 0's bytes (`baseline-scope.json`, `baseline-dirty-hashes.json`, `baseline-untouched.json` and the BASE copies), not to `HEAD`.

- **One launch path (rows 1 to 3, D-933, D-935, D-940).** `ui/tests/e2e/electron-env.ts` holds `electronEnv` (`ENV_DROP_FLAG`: the merge of the base and the spec's variables, `AVKIT_E2E=1`, then `ELECTRON_RUN_AS_NODE` and every `undefined` key deleted, the base never changed), `requireScratchAppData` (`SCRATCH_PROFILE`: `AVKIT_APP_DATA` must name a folder inside `tmpdir()` and not `tmpdir()` itself), `MAIN_ERROR_LOG_ENV`, `MAIN_ERROR_WATCH` and `mainErrorRecords`. `ui/tests/e2e/main-error-watch.cjs` is the `-r` preload: an `uncaughtException` listener that appends each full error record to the per-launch log and to `stderr` with `[avkit-e2e-main-error]`. `ui/tests/e2e/electron-app.ts` holds `launchElectron` (`ONE_LAUNCH_PATH`), the only `_electron.launch(` in `ui/tests/e2e/`; its `close()` closes the app, waits at most 5 s for the process to exit, then throws with every recorded stack (`CLOSE_CHECK`).
- **The 21 sites (rows 4 and 5, D-934, D-942).** The 21 `_electron.launch()` sites in 20 files moved to `launchElectron`, each keeping its own `env` keys, call order and line endings (`SITE_MIGRATION`); `site-check.py` derives every site from the row-0 BASE copies.
- **The whole suite under the watch (row 6, D-936).** The full Electron suite and the flag run pass with every spec under `MAIN_ERROR_WATCH`; no spec newly failed, so `NEW_FAILURE_RULE` had nothing to register.
- **The install race (rows 7 and 8, D-937).** `ui/tests/unit/global-setup.ts` requires `electron` once in Vitest's main process before any worker starts, throws with the install command if the binary is still missing, hands the path to the tests with `project.provide('electronBinary', path)` and returns nothing (`INSTALL_ONCE`); `ui/vitest.config.ts` gains one `globalSetup` line.
- **The hint tests (rows 9 to 11, D-938).** `capture-page.test.ts`'s AC-97.4 HINTS test now compares the Save and Region props with `chordOf('capture:save')` and `chordOf('page:primary')`, and `capture-page.behavior.test.ts` gains the rendered check with `expectBoundHint` (`HINT_VALUES`). `mutation.py` proved both: the old test passes on the `Ctrl+O` mutant and the new tests fail on it; `CapturePage.tsx` is back at its row-0 SHA-256 and mtime.
- **Registers (row 12).** The four issues were resolved through `issue-resolve.py --expect-sha256`, bound to row 0's register hash. `UI-DEV-ELECTRON-RUN-AS-NODE-SILENT` (D-939) and `E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED` (D-935) were added open. Grouping §6 row 78 says `executed (Session 78)`. After the gate's first attempt, D-1032 added `CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE` open. `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` is unchanged and stays MONITORING (D-940).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | unit | `electronEnv` drops `ELECTRON_RUN_AS_NODE` from the base and the extra, keeps `AVKIT_E2E` `'1'`, `KEEP` and `EXTRA`, drops the `undefined` key and leaves its base deep-equal to a copy | Local Canon (D-933, D-934) | `ui/tests/unit/e2e-harness.test.ts:47` | ✅ |
| AC-2 | unit (source) | Only `electron-app.ts` holds `_electron`, with exactly one `_electron.launch(`; `electron-env.ts` holds `...process.env` at most once | Local Canon (D-933) | `e2e-harness.test.ts:60` | ✅ |
| AC-3 | unit (subprocess) | The thrower dies without the watch; with `-r MAIN_ERROR_WATCH` it stays alive, prints `true` and `alive`, marks stderr, and logs exactly one record with the message and a stack frame | Research-backed (D-935) | `e2e-harness.test.ts:69` | ✅ |
| AC-4 | unit | `mainErrorRecords` keeps multi-line stacks, skips the blank line, returns `{ raw: 'not json' }` for the malformed one, and `[]` for `''` | Local Canon (D-935) | `e2e-harness.test.ts:112` | ✅ |
| AC-5 | E2E | With `ELECTRON_RUN_AS_NODE=1` in the worker, `launchElectron` starts the app and the main process sees no `ELECTRON_RUN_AS_NODE` | Local Canon (D-933) | `ui/tests/e2e/electron-harness.test.ts:31` | ✅ |
| AC-6 | E2E | `__avkitE2eMainErrorWatch` is `true` and `uncaughtException` has at least 2 listeners before any test action | Research-backed (D-935) | `electron-harness.test.ts:50` | ✅ |
| AC-7 | E2E (two tests) | An exception thrown after launch, and one thrown during startup by `fixtures/startup-throw-main.mjs`, each make `app.close()` reject with the message and its stack | Local Canon (D-935) | `electron-harness.test.ts:69` (after launch), `:97` (during startup) | ✅ |
| AC-8 | E2E | A launch with no main-process error closes cleanly within the test timeout | Local Canon (D-940) | `electron-harness.test.ts:117` | ✅ |
| AC-9 | site check | `site-check.py` rules 1 to 6 against the BASE copies exit 0; `--selftest` 13 of 13 | Local Canon (D-934) | `site-check.py` (row 5, gate `site-check`, `site-check-selftest`) | ✅ |
| AC-10 | E2E (suite) | The whole Electron suite with `ELECTRON_RUN_AS_NODE` unset passes at least base + 5, nothing failed; each run stops only its own processes; `owned-procs.ps1 -Selftest` 26 of 26 | Local Canon (D-936, D-941) | Row 6 and gate `ui-electron`; `owned-procs.ps1 -Selftest` (row 6, gate) | ✅ |
| AC-11 | unit (named change) | AC-51.7 checks `launchElectron(` in the E2E file and `_electron.launch` in `electron-app.ts`; its other assertions unchanged | Local Canon (D-933; M-7 named row 4) | `ui/tests/unit/layout-primitives.test.ts:216` (change at `:232`) | ✅ |
| AC-12 | unit | `ensureElectronBinary` returns a found path, throws the install command for a throwing `requireFn` or a missing path; the config holds the `globalSetup` line; the default export returns `undefined` and makes exactly one `provide('electronBinary', p)` | Research-backed (D-937) | `ui/tests/unit/vitest-global-setup.test.ts:34` | ✅ |
| AC-13 | unit | `inject('electronBinary')` is a string naming an existing path under `ui/node_modules/electron/dist/` | Research-backed (D-937) | `vitest-global-setup.test.ts:62` | ✅ |
| AC-14 | unit (named change) | The AC-97.4 HINTS source test compares Save and Region with `chordOf('capture:save')` and `chordOf('page:primary')` | Local Canon (D-938; M-7 named row 10) | `ui/tests/unit/capture-page.test.ts:630` | ✅ |
| AC-15 | unit (new) | The rendered `capture-save` and `capture-region` carry the registry chords (`expectBoundHint`) | Local Canon (D-938) | `ui/tests/unit/capture-page.behavior.test.ts:3449` | ✅ |
| AC-16 | mutation proof | On the mutant the old AC-97.4 test passes (row 9) and AC-14 and AC-15 fail by assertion (row 10); `restore` and `status` bring back `CapturePage.tsx`'s SHA-256 and mtime | Local Canon (D-938) | `mutation.py` (rows 9 and 10; gate `mutation-status`, `mutation-selftest`) | ✅ |
| AC-17 | register | The four issues resolved through `issue-resolve.py` bound to row 0's hash; the two issues added; `render` and `render --check` exit 0; LF kept; `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` unchanged; grouping row 78 executed | Local Canon (D-935, D-939, D-940) | Row 12 (`issue-resolve: 0 problem(s)`, the row-12 check); gate `issues-render` | ✅ |
| AC-18 | E2E (flag) | With `ELECTRON_RUN_AS_NODE=1` in the shell, `launch.test.ts` and `electron-harness.test.ts` pass and no receipt line holds `bad option` | Local Canon (D-933, D-1030) | Row 6 flag run and gate `ui-electron-flag`; the negative is row 0's `ehh-base-flag.txt` | ✅ |
| AC-19 | unit and E2E | `requireScratchAppData` accepts a folder inside `tmpdir()` and refuses `{}`, `''`, `tmpdir()` and a path outside it; `electron-app.ts` calls it before its launch; each harness test sees its own folder as `userData` and `sessionData` | Local Canon (D-933) | `e2e-harness.test.ts:121`; the five tests of `electron-harness.test.ts` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-1, AC-3, AC-19 | FAILED: `ui/tests/e2e/electron-env.ts exists: expected false to be true` and `ui/tests/e2e/main-error-watch.cjs exists: expected false to be true` | passed (row 3) | `ui/tests/unit/e2e-harness.test.ts:47`, `:69`, `:121` |
| AC-2 | FAILED: `files under ui/tests/e2e that name the Playwright Electron launcher: expected [ …(20) ] to deeply equal [ 'electron-app.ts' ]` (row 1); `[ …(21) ]` after row 3 added `electron-app.ts` (row 4, Red a) | passed (row 5) | `e2e-harness.test.ts:60` |
| AC-4 | FAILED by assertion: the module did not exist | passed (row 3) | `e2e-harness.test.ts:112` |
| AC-5 to AC-8 | FAILED: `expect(received).toBe(expected)`, `Expected: true`, `Received: false` (`electron-app.ts` absent), 5 failed | passed (row 3), `5 passed (2.8s)` | `ui/tests/e2e/electron-harness.test.ts:31`, `:50`, `:69`, `:97`, `:117` |
| AC-11 | FAILED: `expected 'import { _electron, expect, test } fr…' to contain 'launchElectron('` (Red b) | passed (row 5) | `ui/tests/unit/layout-primitives.test.ts:232` |
| AC-12 | FAILED: `ui/tests/unit/global-setup.ts exists: expected false to be true` | passed (row 8) | `ui/tests/unit/vitest-global-setup.test.ts:34` |
| AC-13 | FAILED: `expected 'undefined' to be 'string'` | passed (row 8) | `vitest-global-setup.test.ts:62` |
| AC-14 | FAILED on the mutant: `expected … to contain 'shortcut="Ctrl+S"'` | passed (row 11) | `ui/tests/unit/capture-page.test.ts:630` |
| AC-15 | FAILED on the mutant: `capture:save: expected 'Control+O' to be 'Control+S'` | passed (row 11) | `ui/tests/unit/capture-page.behavior.test.ts:3449` |

Red, helper unit (row 1): `5 tests | 5 failed` (child exit 1) and `red-check: 1 receipt(s), 5 required test(s), 0 problem(s)`. Red, harness E2E (row 2): `5 failed` and `red-check: 1 receipt(s), 4 required test(s), 0 problem(s)`; `0 leftover electron.exe launched by this run` (8 processes recorded). Green (row 3): unit `4 passed | 1 skipped` (`-t "AC-[134]"`), E2E `5 passed (2.8s)`, 0 leftover (13 recorded).

Red, sites (row 4): Red a (AC-2) and Red b (AC-51.7), `red-check: 2 receipt(s), 2 required test(s), 0 problem(s)` after D-1031. Green (row 5): `site-check: ok` (`BASE sites: 21 in 20 file(s)`), `20 passed`, line endings kept, `typecheck` and `lint` clean.

Red, install (row 7): `2 tests | 2 failed`, `red-check: 1 receipt(s), 2 required test(s), 0 problem(s)`. Green (row 8): `2 passed`; `vitest.config.ts` CRLF kept with one `globalSetup` line; the whole unit suite `132 passed (132)` files, `1539 passed`.

Mutation (rows 9 to 11): row 9 applied the mutant (SHA-256 `a0e7297c…`), the BASE AC-97.4 test gave `1 passed | 34 skipped`, and `restore` brought back `85a51cb7…` and mtime_ns `1794704785936682000`. Row 10: AC-14 and AC-15 failed by assertion on the mutant, `red-check: 1 receipt(s), 2 required test(s), 0 problem(s)`, restored. Row 11: `2 passed | 169 skipped`; `mutation.py status` equal to `baseline-scope.json`; CRLF kept.

Each Red ran the base code (or the mutant) under test, and each Green the changed code; every later row and the gate run the working tree.

Receipts, all under `C:/Temp/av-kit/e2e-harness-hardening/`:
- row 0: `ehh-baseline.txt` (`baseline: all steps exit 0`), `ehh-base-ui.txt`, `ehh-base-e2e.txt`, `ehh-base-flag.txt`, `ehh-base-lint.txt`; earlier runs `ehh-baseline-attempt1.txt` to `ehh-baseline-attempt4.txt`, `ehh-base-e2e-attempt2.txt` to `-attempt4.txt`, `ehh-base-flag-attempt4.txt`; `ehh-nuget-restore-probe.txt`, `ehh-diag-c15.txt`, `ehh-diag-flag-debug.txt`; the row-0 copies in `base/`;
- D-943, D-1030, D-1031: `ehh-d943-probe.txt`, `ehh-d943-edit.txt`, `ehh-d1030-edit.txt`, `ehh-d1030-parse.txt`, `ehh-d1030-guard-probe.txt`, `ehh-d1030-d943-diff.txt`, `ehh-d1031-edit.txt`, `ehh-d1031-diff.txt`, `ehh-d1031-selftest.txt`;
- rows 1 to 3: `ehh-helper-unit-red.txt` and its `.exit`, `ehh-helper-unit-red-check.txt`, `ehh-harness-e2e-red.txt` and its `.exit`, `ehh-harness-e2e-red-check.txt`, `ehh-helper-unit-green.txt`, `ehh-harness-e2e-green.txt`; the first Green `ehh-harness-e2e-green-attempt1.txt`, `row-3-out-attempt1.txt`;
- rows 4 and 5: `ehh-sites-red-a.txt`, `ehh-sites-red-b.txt` and their `.exit`, `ehh-sites-red-check.txt` (first check `ehh-sites-red-check-attempt1.txt`), `ehh-row5-migrate.txt`, `ehh-site-check.txt`, `ehh-sites-green.txt`, `ehh-sites-eol.txt`, `ehh-sites-types.txt`, `ehh-sites-lint.txt`;
- row 6: `ehh-owned-procs.txt`, `ehh-e2e-full.txt`, `ehh-e2e-flag.txt` and their `.exit` and `-run.txt`;
- rows 7 and 8: `ehh-install-red.txt` and its `.exit`, `ehh-install-red-check.txt`, `ehh-install-green.txt`, `ehh-install-eol.txt`, `ehh-ui-full.txt`;
- rows 9 to 11: `ehh-mutant-apply-r9.txt`, `ehh-mutant-old.txt`, `ehh-mutant-restore-r9.txt`, `ehh-mutant-apply-r10.txt`, `ehh-hints-red.txt` and its `.exit`, `ehh-hints-red-check.txt`, `ehh-mutant-restore-r10.txt`, `ehh-hints-green.txt`, `ehh-mutant-status.txt`, `ehh-hints-eol.txt`;
- row 12: `issue-resolve-set.json`, `ehh-issue-resolve.txt`, `ehh-issue-add-dev.txt`, `ehh-issue-add-rej.txt`, `ehh-issues-render.txt`, `ehh-issues-render-check.txt`, `ehh-row12-check.txt`, `ehh-scope-12.txt`, `ehh-scope-12-reconstruct.txt`;
- D-1032: `ehh-probe-ac977.txt`, `ehh-probe-ac977-base.txt` and their `.exit`, `ehh-issue-add-d1032.txt`, `ehh-issues-render-d1032.txt`, `ehh-issues-render-check-d1032.txt`;
- H1: `task-unchecked.txt` (H1-1); `ehh-gate-h1.txt` with `ehh-D6-<step>.txt` (H1-2), and the first attempt `ehh-gate-h1-attempt1.txt` with `ehh-D6-<step>-attempt1.txt`; `ehh-render-check.txt` and `ehh-h13-focus.txt` (H1-3); `openapi-check.txt` (H1-4); `ehh-h15-sources.txt` (H1-5); `handoff-check.txt` (H1-6), `handoff-ac-check.txt` (H1-6a) and `full-evidence-check.txt` (H1-6b);
- the scope check before each row: `ehh-scope-1.txt` to `ehh-scope-12.txt`.

Each row ran its task.md Validation cell verbatim from `C:/Temp/av-kit/e2e-harness-hardening/row-<n>-run.ps1` (row 0 from `run-row0.ps1`), as `pwsh -NoProfile -File`, after the row environment of `pre.ps1` (`Set-Location P:/av-kit`, `PYTHONIOENCODING=utf-8`, `RECEIPTS_DIR=C:/Temp/av-kit`, `ELECTRON_RUN_AS_NODE` cleared, `TMP` and `TEMP` at `C:\Temp\av-kit\e2e-harness-hardening\tmp`) and `scope-check.py --before-row <n>`. Every Electron run went through `e2e-run.ps1` or the plan's scripts and stopped only its own recorded processes through `owned-procs.ps1`; the older `electron.exe` processes under this checkout were never touched.

**Execution notes.** Each is a deviation from the plan, or a fact the plan did not foresee.

- **The Status line.** After the plan review approved, the coordinator wrote Mat's execute words into `implementation-plan.md:15`. It is the only change made to the plan after its approval; no row, AC or decision changed. The approved plan hash no longer matches for that reason alone.
- **The session order.** Session 79 ran and was committed (`cda7291`) before row 0's rerun, and Mat's C1-5 test fix was committed (`ebe68e4`) before the final row 0. Both commits changed files this plan reads (`known-issues.*`, the grouping, `current-focus.md`, `metrics.md`, `console-chrome.test.ts`); row 0 was recorded again from the start at `ebe68e4`, and every later row binds to that content.
- **Row 0 ran five times.**
  1. On `263f635`: `ui-picker-stub` exit 1, `NU1100` for the win-x64 runtime packs; this machine had no NuGet source (S1, D-1033). The coordinator added nuget.org; its `dotnet restore` rewrote the gitignored `native/region-picker-stub/obj/`.
  2. On `cda7291`: the base Electron suite `1 failed`, `202 passed (4.4m)`, C1-5 `Expected 1, Received 2` (S1, D-1034).
  3. On `ebe68e4`: `1 failed`, `202 passed (6.5m)`: AC-82.6 TEXT_PIXEL_ORACLE at `capture-inbox.test.ts:2278` with `Worker teardown timeout of 60000ms exceeded`, the `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` signature. D-941's one repeat applied.
  4. The repeat: `203 passed (4.5m)`, but the BASE flag run failed with `Process failed to launch!` and no `bad option` line (S1, D-1030).
  5. After D-1030: `baseline: all steps exit 0`; base unit `130 passed`, `1532 passed`; base Electron `203 passed (4.5m)`, 0 leftover (611 recorded); the BASE flag run exit 1 with 4 `bad option: --remote-debugging-port=0` lines.
- **`DEBUG=pw:browser` for the flag child (D-1030).** Playwright prints `electron.exe`'s stderr only under `DEBUG=pw:browser`, so without it neither side of AC-18 could see `bad option`. `baseline.ps1` step 7, `e2e-run.ps1 -Flag` and `session-gate.ps1`'s flag step set it in the child only and clear it in the parent before and after. The gate's flag step printed 187 `pw:browser` lines and 0 `bad option`.
- **`e2e-run.ps1` positional binding (D-943).** The task cells call `e2e-run.ps1 -Receipt R tests/e2e/electron-harness.test.ts`; without `[CmdletBinding(PositionalBinding = $false)]` PowerShell bound the spec path to `-MinPassed` and exited 1 (`Cannot convert value "tests/e2e/electron-harness.test.ts" to type "System.Int32"`). With it, the path lands in `-Files`.
- **`red-check.py`'s launch pattern (D-1031).** Row 4's Red b receipt quotes the BASE source `const app = await _electron.launch({` in Vitest's diff, and the setup-failure pattern `electron\.launch` refused it as a launch error. The pattern is now `(?<![\w$])electron\.launch`, with a positive and a negative fixture; the selftest went from 36 fixtures (11 positive, 25 negative) to 38 (12 positive, 26 negative), 0 wrong. Row 4 was run again from its Red; the first receipts are kept as `-attempt1`.
- **A helper defect found at row 3 (`NEW_FAILURE_RULE`).** The first Green gave `5 failed`, `TypeError: Cannot read properties of undefined (reading '_object')`: once `close()` has run, Playwright has disposed the app object and `app.process()` throws. `electron-app.ts` now takes the child process before it wraps `close()` (`electron-app.ts:84`). The stack was in the new helper, not product code, so S5 did not apply.
- **The row-12 order.** The grouping row-78 edit was applied before `scope-check.py --before-row 12` ran, so that check reported the grouping as moved (`8234daaf1b65 -> f1d8948b4d92`). `ehh-scope-12-reconstruct.txt` reverses the one row-78 edit and gets row 0's SHA-256 exactly (`reversed edit equals row 0: True`); nothing else in the file changed.
- **Gate attempt 1 and D-1032.** The first H1-2 gate failed `ui-electron`: `1 failed`, `207 passed (6.0m)`, AC-97.7 at `convert-queue.test.ts:1568`, `convert-staged-remove` count 0, expected 1 (`:1579`). `ui-electron-flag` and `identity-after` did not run. AC-97.7 alone under `--repeat-each=20` failed 2 of 20 on this tree and 3 of 20 with the row-0 BASE spec on the same build, so the flake predates this session. Cause: `ConvertPage` is a lazy route (`router.tsx:50`); `navigateAndDeliver` (`convert-commands.ts:102`) dispatches `CONVERT_BROWSE_EVENT` after two animation frames, and the listener is added only when `ConvertPage` mounts (`ConvertPage.tsx:497`). Mat ruled D-1032: one whole-gate repeat, and the flake registered as `CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE`. The repeat passed every step.
- **A third new issue.** AC-17 names two added issues; D-1032 adds a third, `CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE` (low, ui, open), through `issue_triage.py add`, then `render` and `render --check`. The register was edited before the repeat, so the repeat's `issues-render` step covers it.
- **The teardown hang stays MONITORING (D-940).** Row 0's third run hit its signature; neither gate run did.
- **Unit totals.** Row 8's whole suite gave `1539 passed` and the gate `1540 passed`: row 10 added AC-15 after row 8. Row 0 gave `1532`; the session adds 8 tests (5, 2 and 1).
- **Sizes since the plan.** Row 0 measured the same line endings as the plan everywhere. Sizes moved where committed sessions changed a file: `capture-inbox.test.ts` 177,626 bytes (plan 175,468), `console-chrome.test.ts` 10,737 (plan 10,587), `known-issues.yaml` 464,052 (plan 455,210), the grouping 31,642 (plan 31,451). All are bound by their row-0 hashes and BASE copies.
- **The date.** Every row ran on 2026-11-16, so the register entries and new issues carry that date; the plan and this handoff keep the project date 2026-11-15.
- **D-919 does not apply.** This plan's `red-check.py` reads only Vitest and Playwright receipts; no Red here is a pytest run.
- **Git's CRLF warnings.** `git diff` prints `LF will be replaced by CRLF` for the LF files. That comes from the system `core.autocrlf=true`, predates this session and changes no byte.
- **Other sessions' ACs that the plan names.** These ACs belong to other MEUs and sessions. The plan cites them only as siblings in the files it touches, and none is an acceptance criterion of this session.
  - AC-71.10 is at `ui/tests/unit/mcp-spawn-electron.test.ts:76`, where the plan's install-race trigger reads `path.txt`. It passed inside the gate's `ui-tests` (`1540 passed`).
  - AC-146.19 is at `ui/tests/e2e/capture-inbox.test.ts:3692` (Session 75), and AC-57.10 and AC-67.24 are at `capture-inbox.test.ts:675` and `:1572`. Their test bodies are unchanged, and they passed under the watch inside the gate's `ui-electron` (`208 passed`).
  - AC-108.7 is at `ui/tests/e2e/backend-output-after-close.test.ts:8` (Session 82). Its site moved to `launchElectron` with its `env` keys kept, and it passed inside `ui-electron`.
  - AC-151.7 is Session 81's, which has not run. Row 10 appended at the describe's closing line and touched none of its pins.
- **This handoff quotes no home-folder path.**

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/run-row0.ps1 (task.md row 0 Validation cell, verbatim: baseline.ps1 into C:/Temp/av-kit/e2e-harness-hardening/ehh-baseline.txt), the fifth run, after D-1030", "cwd": "P:/av-kit", "scope": "Row 0: baseline.sha, the dirty-path records, baseline-scope.json, baseline-sites.json, baseline-untouched.json, the BASE copies, the base unit and Electron suites, the BASE flag run, line endings and the plan-local selftests", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus the row-0 dirty tree", "output": "baseline.sha ebe68e4a3b934379622a8983debb47dec85e22dc; launch sites 21 in 20 files; base ui 130 files, 1532 passed; base e2e 203 passed (4.5m), 0 leftover (611 recorded), base-e2e-count.txt 203; BASE flag exit 1 with 4 lines 'electron.exe: bad option: --remote-debugging-port=0'; red-check selftest 36 fixtures (11 positive, 25 negative), 0 wrong; identity, mutation 0 failures; site-check selftest 13, 0 wrong; untouched 6 of 6; owned-procs 26 of 26; scope-check 6 of 6; CapturePage.tsx 85a51cb7...; baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row1-helper-unit-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-1-run.ps1 (task.md row 1 Validation cell, verbatim: npm --prefix ui run test -- tests/unit/e2e-harness.test.ts into ehh-helper-unit-red.txt with its .exit, then red-check.py --require for AC-1 to AC-4 and AC-19)", "cwd": "P:/av-kit", "scope": "Red for AC-1 to AC-4 and AC-19's unit test: the new tests before electron-env.ts, main-error-watch.cjs and electron-app.ts exist", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus row 1", "output": "5 tests, 5 failed (child exit 1): 'ui/tests/e2e/electron-env.ts exists: expected false to be true'; 'files under ui/tests/e2e that name the Playwright Electron launcher: expected [ ...(20) ] to deeply equal [ electron-app.ts ]'; 'ui/tests/e2e/main-error-watch.cjs exists: expected false to be true'. red-check: 1 receipt(s), 5 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row2-harness-e2e-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-2-run.ps1 (task.md row 2 Validation cell, verbatim: e2e-run.ps1 -Receipt ehh-harness-e2e-red.txt tests/e2e/electron-harness.test.ts, then red-check.py --require for AC-5 to AC-8)", "cwd": "P:/av-kit", "scope": "Red for AC-5 to AC-8 (and AC-19's E2E checks): the five harness tests before electron-app.ts exists", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 and 2", "output": "5 failed (child exit 1), each 'Error: expect(received).toBe(expected)', Expected: true, Received: false in loadLaunch. red-check: 1 receipt(s), 4 required test(s), 0 problem(s); e2e-run: 0 leftover electron.exe launched by this run, 0 stopped (8 processes recorded)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row3-harness-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-3-run.ps1 (task.md row 3 Validation cell, verbatim: the unit file with -t AC-[134], then e2e-run.ps1 -Receipt ehh-harness-e2e-green.txt -MinPassed 5 -Clean tests/e2e/electron-harness.test.ts), run again after the electron-app.ts fix", "cwd": "P:/av-kit", "scope": "Green for AC-1, AC-3, AC-4, AC-19 (unit) and AC-5 to AC-8 with AC-19's profile checks (E2E): ENV_DROP_FLAG, SCRATCH_PROFILE, MAIN_ERROR_WATCH, ONE_LAUNCH_PATH, CLOSE_CHECK", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 to 3", "output": "unit 4 passed, 1 skipped (5); e2e ok AC-5 :31, AC-6 :50, AC-7 after launch :69, AC-7 during startup :97, AC-8 :117; 5 passed (2.8s); 0 leftover electron.exe launched by this run, 0 stopped (13 processes recorded). The first Green gave 5 failed with TypeError: Cannot read properties of undefined (reading '_object'), fixed in electron-app.ts:84"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row4-sites-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-4-run.ps1 (task.md row 4 Validation cell, verbatim: Red a, AC-2, into ehh-sites-red-a.txt; Red b, AC-51.7 after the named change, into ehh-sites-red-b.txt; then red-check.py over both), run again after D-1031", "cwd": "P:/av-kit", "scope": "Red for AC-2 over the unmigrated sites and for AC-11, the named AC-51.7 change, against the BASE E2E file", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 to 4", "output": "Red a: 'files under ui/tests/e2e that name the Playwright Electron launcher: expected [ ...(21) ] to deeply equal [ electron-app.ts ]'; Red b: 'expected import { _electron, expect, test } fr... to contain launchElectron('. red-check: 2 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row5-sites-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-5-run.ps1 (task.md row 5 Validation cell, verbatim: site-check.py, the two unit files, the line-ending check, typecheck and lint)", "cwd": "P:/av-kit", "scope": "Green for AC-2, AC-9 and AC-11: the 21 sites in 20 files moved to launchElectron (SITE_MIGRATION, D-934, D-942)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 to 5", "output": "sites migrated: 21; BASE sites: 21 in 20 file(s); site-check: ok; 2 files, 20 passed; every file's line endings kept; typecheck and lint exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row6-e2e-suite", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-6-run.ps1 (task.md row 6 Validation cell, verbatim: owned-procs.ps1 -Selftest, e2e-run.ps1 full -BaseExtra 5 -Clean into ehh-e2e-full.txt, then e2e-run.ps1 -Flag for launch.test.ts and electron-harness.test.ts into ehh-e2e-flag.txt)", "cwd": "P:/av-kit", "scope": "AC-10 and AC-18: the whole Electron suite under MAIN_ERROR_WATCH, process ownership, and the flag run", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 to 6", "output": "owned-procs selftest: 26 of 26 passed; full suite 208 passed (7.4m), 0 leftover electron.exe launched by this run, 0 stopped (664 processes recorded); flag run 9 passed (6.7s), 0 'bad option' lines, 31 processes recorded"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row7-install-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-7-run.ps1 (task.md row 7 Validation cell, verbatim: vitest-global-setup.test.ts into ehh-install-red.txt with its .exit, then red-check.py --require AC-12 and AC-13)", "cwd": "P:/av-kit", "scope": "Red for AC-12 and AC-13 before global-setup.ts exists and before the config line", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 to 7", "output": "2 tests, 2 failed (child exit 1): 'ui/tests/unit/global-setup.ts exists: expected false to be true'; 'expected undefined to be string'. red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row8-install-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-8-run.ps1 (task.md row 8 Validation cell, verbatim: the test file, the vitest.config.ts line-ending check, then the whole unit suite into ehh-ui-full.txt)", "cwd": "P:/av-kit", "scope": "Green for AC-12 and AC-13 (INSTALL_ONCE) and the whole unit suite under the global setup", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 to 8", "output": "2 passed (2); vitest.config.ts CRLF kept, 1 globalSetup line; whole suite Test Files 132 passed (132), Tests 1539 passed (1539)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row9-mutant-old-test", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-9-run.ps1 (task.md row 9 Validation cell, verbatim: mutation.py apply, the BASE AC-97.4 HINTS test into ehh-mutant-old.txt, mutation.py restore in a finally)", "cwd": "P:/av-kit", "scope": "AC-16, the negative: the BASE AC-97.4 test passes on the Ctrl+O mutant", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 to 9", "output": "mutant applied, CapturePage.tsx sha256 a0e7297c...; BASE test 1 passed, 34 skipped (35); restored sha256 85a51cb7... and mtime_ns 1794704785936682000"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row10-hints-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-10-run.ps1 (task.md row 10 Validation cell, verbatim: mutation.py apply, AC-14 and AC-15 into ehh-hints-red.txt with its .exit, mutation.py restore, red-check.py --require AC-14 and AC-15)", "cwd": "P:/av-kit", "scope": "Red for AC-14 and AC-15 on the mutant (HINT_VALUES)", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 to 10", "output": "2 failed (child exit 1): behavior 'capture:save: expected Control+O to be Control+S'; source 'expected ... to contain shortcut=\"Ctrl+S\"'. restored to sha256 85a51cb7.... red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row11-hints-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-11-run.ps1 (task.md row 11 Validation cell, verbatim: AC-14 and AC-15 into ehh-hints-green.txt, mutation.py status, the line-ending check)", "cwd": "P:/av-kit", "scope": "Green for AC-14 and AC-15, and AC-16's restore", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 to 11", "output": "Test Files 2 passed (2), Tests 2 passed, 169 skipped (171); status CapturePage.tsx sha256 85a51cb73ed853163813f2695970622b3cfb47688a196bd092d719bc9a354446 equals baseline-scope; both files CRLF kept"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-row12-registers", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-12-run.ps1 (task.md row 12 Validation cell, verbatim: issue-resolve.py for the four issues with --set-file issue-resolve-set.json and --expect-sha256 from baseline-scope.json, the two issue_triage.py add calls, render, render --check, the grouping row 78 edit and the row-12 check)", "cwd": "P:/av-kit", "scope": "AC-17: the four issues resolved, the two issues added, the render, grouping section 6 row 78", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 to 12", "output": "decision logs read 95 of 95; register sha256 3144717371df89f2b8463f98810dd4bcabeab5b46786ce0606e1cc334cf1481f before, e842d899b028449b77b4094dfb9f66dbc48975ff62136ffab9de131e61fec600 after; 20 parsed fields; issue-resolve: 0 problem(s); OK: Added issue UI-DEV-ELECTRON-RUN-AS-NODE-SILENT; OK: Added issue E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED; Rendered known-issues.md, 56 lines; OK: known-issues.md is up-to-date; four resolved True, two added True, teardown unchanged True, row 78 True, register LF True, grouping LF True"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-h1-1-unchecked", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-H1-1-run.ps1 (task.md row H1-1 Validation cell, verbatim)", "cwd": "P:/av-kit", "scope": "H1-1: no implementation row of task.md is unchecked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD ebe68e4 plus rows 1 to 12", "output": "unchecked implementation rows: []"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-gate-h1-2-attempt1", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-H1-2-run.ps1 (task.md row H1-2 Validation cell, verbatim: $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-e2e-harness-hardening/session-gate.ps1 *> C:/Temp/av-kit/e2e-harness-hardening/ehh-gate-h1.txt), the first attempt, kept as ehh-gate-h1-attempt1.txt", "cwd": "P:/av-kit", "scope": "H1-2, first attempt: the registered D6 gate on the whole tree after rows 0 to 12", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "ebe68e4a3b934379622a8983debb47dec85e22dc+37871ced8e02b28db01091dc9e0f260c7f46ab93656b69f29502a8543f5ab8f8", "output": "every step through issues-render exit 0; ui-electron exit 1: 1 failed, 207 passed (6.0m), AC-97.7 Ctrl+O browses on Convert and is inert on Downloader (convert-queue.test.ts:1568), expect(locator).toHaveCount(expected) failed, Expected: 1, Received: 0 at :1579; ui-electron-flag and identity-after not run (fail-fast)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-probe-ac977-tree", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/probe-ac977.ps1 (e2e-run.ps1 --grep=AC-97.7 --repeat-each=20 on this tree)", "cwd": "P:/av-kit", "scope": "Diagnostic after gate attempt 1: AC-97.7 alone, 20 times, with the Session 78 spec", "phase": "runtime", "exit_code": 1, "result": "fail", "tested_state": "ebe68e4a3b934379622a8983debb47dec85e22dc+37871ced8e02b28db01091dc9e0f260c7f46ab93656b69f29502a8543f5ab8f8", "output": "2 failed, 18 passed (55.0s), both at convert-queue.test.ts:1568 AC-97.7; 0 leftover electron.exe launched by this run, 0 stopped (144 processes recorded)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-probe-ac977-base", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/probe-ac977-base.ps1 (e2e-run.ps1 with --config=C:/Temp/av-kit/e2e-harness-hardening/base-probe/ui/playwright.config.ts --grep=AC-97.7 --repeat-each=20)", "cwd": "P:/av-kit", "scope": "Diagnostic after gate attempt 1: the row-0 BASE convert-queue spec's AC-97.7, 20 times, against the same build", "phase": "runtime", "exit_code": 1, "result": "fail", "tested_state": "ebe68e4a3b934379622a8983debb47dec85e22dc+37871ced8e02b28db01091dc9e0f260c7f46ab93656b69f29502a8543f5ab8f8", "output": "3 failed, 17 passed (49.2s) with the BASE spec, so the flake predates this session; 0 leftover electron.exe launched by this run, 0 stopped (151 processes recorded)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-d1032-issue", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/d1032-issue.ps1 (issue_triage.py add --id CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE --severity low --component ui --add-status open --discovered 2026-11-16, then render and render --check)", "cwd": "P:/av-kit", "scope": "D-1032: register the AC-97.7 flake before the one allowed whole-gate repeat", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "ebe68e4a3b934379622a8983debb47dec85e22dc+454558a34705e83897c7ef7a5cb1a4a15d6fa329e1c9e57ab25be8175fac510e", "output": "OK: Added issue CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE to known-issues.yaml; Rendered known-issues.md: 57 lines; OK: known-issues.md is up-to-date; register sha256 fd3735e8d22021ac0a097b1504e0f036a87cec3ebe356e78ab62516e9b196dfc, LF"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-gate-h1-2", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-H1-2-run.ps1 (task.md row H1-2 Validation cell, verbatim: $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-e2e-harness-hardening/session-gate.ps1 *> C:/Temp/av-kit/e2e-harness-hardening/ehh-gate-h1.txt), the one repeat D-1032 allows", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 12 and D-1032: identity, types, lint, task contract, scope paths and every plan-local selftest and check, register grammar, the unit suite, the builds, the picker stub, state and issue renders, the whole Electron suite, the flag run, identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "ebe68e4a3b934379622a8983debb47dec85e22dc+454558a34705e83897c7ef7a5cb1a4a15d6fa329e1c9e57ab25be8175fac510e", "output": "ELECTRON_RUN_AS_NODE <unset>; task-contract 30 rows, 28 fully checked, 2 exempt; scope-check before row 13: 36 paths, 0 moved, ok; red-check selftest 38 fixtures (12 positive, 26 negative), 0 wrong; site-check BASE sites 21 in 20 files, ok; mutation-status sha equals baseline-scope; owned-procs 26 of 26; untouched-check ok; register grammar 35 passed in 0.58s; ui-tests 132 files, 1540 passed; state-render Drift check passed (153 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; ui-electron 208 passed (4.9m), passed=208 base=203 needed=208, 0 leftover (601 recorded); ui-electron-flag 9 passed (5.2s), 187 pw:browser lines, 0 bad option, 19 recorded; tested_state before equals after; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-h1-3-render", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-H1-3-run.ps1 (task.md row H1-3 Validation cell, verbatim: rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/e2e-harness-hardening/ehh-render-check.txt), after h13-focus.py put this session's entry on top of current-focus.md", "cwd": "P:/av-kit", "scope": "H1-3: the rendered state regions after this session's current-focus entry; no MEU status changes in this session", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "ebe68e4a3b934379622a8983debb47dec85e22dc+454558a34705e83897c7ef7a5cb1a4a15d6fa329e1c9e57ab25be8175fac510e", "output": "current-focus.md 69141 to 70768 bytes, CRLF kept: True; Drift check passed, SSOT loaded (153 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehh-h1-4-untouched", "command": "pwsh -NoProfile -File C:/Temp/av-kit/e2e-harness-hardening/row-H1-4-run.ps1 (task.md row H1-4 Validation cell, verbatim: untouched-check.py into openapi-check.txt)", "cwd": "P:/av-kit", "scope": "H1-4: the basis for skipping the OpenAPI, Python and MCP steps (nothing under packages/, tests/ or mcp-server/ changed since row 0)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "ebe68e4a3b934379622a8983debb47dec85e22dc+454558a34705e83897c7ef7a5cb1a4a15d6fa329e1c9e57ab25be8175fac510e", "output": "untouched-check: ok"}
```

### Quality Gate Results

`ehh-gate-h1-2` is the fresh full record (`ehh-gate-h1.txt`), the one repeat D-1032 allows. Its last line is:

> session-gate: all steps exit 0

| Step | Stage | Exit | Result |
|------|-------|------|--------|
| identity-before | identity | 0 | `tested_state` recorded; `ELECTRON_RUN_AS_NODE <unset>` |
| ui-types | static | 0 | `tsc --noEmit` clean |
| ui-lint | static | 0 | `eslint src/ tests/ --max-warnings 0` clean |
| task-contract | static | 0 | 30 rows, 28 fully checked, 2 exempt (`view_file`: H1-5, H2-1) |
| scope-paths | static | 0 | before row 13: 36 paths, 0 moved; `scope-check: ok` |
| scope-check-selftest | static | 0 | 6 of 6 |
| red-check-selftest | static | 0 | 38 fixtures (12 positive, 26 negative), 0 wrong |
| site-check-selftest | static | 0 | 13 fixtures, 0 wrong |
| site-check | static | 0 | `BASE sites: 21 in 20 file(s)`, `site-check: ok` |
| mutation-selftest | static | 0 | 0 failures |
| mutation-status | static | 0 | `CapturePage.tsx` SHA-256 equals `baseline-scope.json` |
| untouched-selftest | static | 0 | 6 of 6 |
| owned-procs-selftest | static | 0 | 26 of 26 |
| untouched | static | 0 | `untouched-check: ok` |
| register-grammar | targeted | 0 | `35 passed in 0.58s` |
| ui-tests | full | 0 | 132 files, `1540 passed` (row 0: 1532; +8 new tests); 0 baseline failures excused |
| ui-build | full | 0 | ok |
| ui-harness-build | full | 0 | ok |
| ui-picker-stub | full | 0 | ok (nuget.org source, D-1033) |
| state-render | full | 0 | Drift check passed (153 MEUs, 12 phases) |
| issues-render | full | 0 | `OK: known-issues.md is up-to-date` (after D-1032's add) |
| ui-electron | runtime | 0 | `208 passed (4.9m)`; `passed=208 base=203 needed=208`; 0 leftover (601 recorded) |
| ui-electron-flag | runtime | 0 | `9 passed (5.2s)`; 187 `pw:browser` lines, 0 `bad option`; 0 leftover (19 recorded) |
| identity-after | identity | 0 | `tested_state` equal before and after |

Skipped with their reasons in the receipt: `py-types`, `py-lint` and `py-tests` (nothing under `packages/` or `tests/` changed since row 0), the `mcp-*` steps (no MCP change), `openapi` (H1-4) and `build-record` (no release build).

The first attempt (`ehh-gate-h1-attempt1.txt`, record `ehh-gate-h1-2-attempt1`) failed only `ui-electron`, on AC-97.7; its `tested_state` was `ebe68e4a3b934379622a8983debb47dec85e22dc+37871ced8e02b28db01091dc9e0f260c7f46ab93656b69f29502a8543f5ab8f8`, before D-1032's register change.

`tested_state` `ebe68e4a3b934379622a8983debb47dec85e22dc+454558a34705e83897c7ef7a5cb1a4a15d6fa329e1c9e57ab25be8175fac510e`, the same before and after the gate. H1-3's current-focus entry, `task.md`'s row marks and this handoff are `PROJECT_ARTIFACTS` that `identity.py` excludes; H1-6b re-derives the state after them.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/tests/e2e/electron-env.ts` | new | `ENV_DROP_FLAG`, `SCRATCH_PROFILE`, `MAIN_ERROR_MARKER`, `MAIN_ERROR_LOG_ENV`, `MAIN_ERROR_WATCH`, `mainErrorRecords`; LF, 82 lines |
| `ui/tests/e2e/electron-app.ts` | new | `ONE_LAUNCH_PATH`, `CLOSE_CHECK`; LF, 96 lines |
| `ui/tests/e2e/main-error-watch.cjs` | new | `MAIN_ERROR_WATCH`; LF, 25 lines |
| `ui/tests/e2e/electron-harness.test.ts` | new | AC-5 to AC-8 (five tests) with AC-19's profile checks; LF, 129 lines |
| `ui/tests/e2e/fixtures/startup-throw-main.mjs` | new | AC-7's startup main; LF, 17 lines |
| `ui/tests/unit/e2e-harness.test.ts` | new | AC-1 to AC-4, AC-19; LF, 135 lines |
| `ui/tests/unit/global-setup.ts` | new | `INSTALL_ONCE`; LF, 44 lines |
| `ui/tests/unit/vitest-global-setup.test.ts` | new | AC-12, AC-13; LF, 68 lines |
| `ui/vitest.config.ts` | modified | One `globalSetup` line; CRLF kept, 481 to 533 bytes |
| `ui/tests/e2e/capture-filmstrip-actions.test.ts`, `console-chrome.test.ts`, `mcp-setup-prompt.test.ts`, `settings.test.ts`, `startup-reveal.test.ts`, `theme-probe.ts`, `tts-generate.test.ts` | modified | `SITE_MIGRATION`; CRLF kept |
| `ui/tests/e2e/backend-output-after-close.test.ts`, `capture-import.test.ts`, `capture-inbox.test.ts` (2 sites), `capture-picker.test.ts`, `command-palette-nav.spec.ts`, `console-panel.test.ts`, `convert-queue.test.ts`, `download-queue.test.ts` (with D-942), `help-search.spec.ts`, `keyboard-shortcuts.test.ts`, `launch.test.ts`, `layout-primitives.test.ts`, `transcript-queue.test.ts` | modified | `SITE_MIGRATION`; LF kept |
| `ui/tests/unit/layout-primitives.test.ts` | modified | AC-11; CRLF kept, 20,110 to 20,215 bytes |
| `ui/tests/unit/capture-page.test.ts` | modified | AC-14 and the `chordOf` import; CRLF kept, 29,260 to 29,440 bytes |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | AC-15 and the `expectBoundHint` import; CRLF kept, 195,766 to 196,279 bytes |
| `.agent/context/known-issues.yaml` | modified, by `issue-resolve.py` and `issue_triage.py add` only | The four issues resolved; three issues added (two in row 12, one by D-1032); LF kept, 464,052 to 470,456 bytes |
| `.agent/context/known-issues.md` | regenerated, by `issue_triage.py render` only | LF, 57 lines |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | modified | §6 row 78 only; LF kept |
| `.agent/context/current-focus.md` | modified | This session's entry on top (H1-3); CRLF kept |
| Plan folder: `baseline.ps1` (D-1030), `e2e-run.ps1` (D-943, D-1030), `session-gate.ps1` (D-1030), `red-check.py` (D-1031), `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-sites.json`, `baseline-untouched.json`, `base-e2e-count.txt`, `task.md` (rows marked) | new or modified | The plan's records, oracles and gate |

```diff
 export async function launchElectron({ main, env = {} }: LaunchOptions = {}): Promise<ElectronApplication> {
   requireScratchAppData(env)
 ...
+  // Taken now: once close() has run, Playwright has disposed the app object and process() throws.
+  const child = app.process()
+  const close = app.close.bind(app)
+  let closing: Promise<void> | undefined
+  app.close = () => {
+    closing ??= (async () => {
+      await close()
+      await waitForExit(child)
+      await checkMainErrors(dir, log)
+    })()
+    return closing
+  }
```

```diff
-  return _electron.launch({
-    args: [resolve(here, '../../out/main/index.js')],
+  return launchElectron({
     env: {
-      ...process.env,
-      AVKIT_E2E: '1',
       AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-')),
```

```diff
+    globalSetup: ['./tests/unit/global-setup.ts'],
```

```diff
-    expect(e2e).toContain('_electron.launch')
+    expect(e2e).toContain('launchElectron(')
+    expect(readFileSync(resolve(ui, 'tests/e2e/electron-app.ts'), 'utf8')).toContain('_electron.launch')
```

```diff
-    expect(save, 'capture-save shortcut prop').toContain('shortcut=')
+    expect(save, 'capture-save shortcut prop').toContain(`shortcut="${chordOf('capture:save')}"`)
-    const region = page.slice(regionAt, page.indexOf('Capture region', regionAt))
-    expect(region, 'capture-region aria-keyshortcuts').toContain('aria-keyshortcuts=')
-    expect(region, 'capture-region title').toContain('title=')
+    const region = page.slice(regionAt, page.indexOf('onClick=', regionAt))
+    expect(region, 'capture-region aria-keyshortcuts').toContain(`aria-keyshortcuts={ariaKeyshortcuts('${chordOf('page:primary')}')}`)
+    expect(region, 'capture-region title').toContain(`title="Capture region (${chordOf('page:primary')})"`)
```

```diff
-    // no page snapshot for `_electron` windows), so the failure carries it.
+    // no page snapshot for Electron windows), so the failure carries it.
```

```diff
+[CmdletBinding(PositionalBinding = $false)]
 param(
 ...
-    $line = "`$env:ELECTRON_RUN_AS_NODE='1'; " + ($npm -join ' ') + "; exit `$LASTEXITCODE"
+    $line = "`$env:ELECTRON_RUN_AS_NODE='1'; `$env:DEBUG='pw:browser'; " + ($npm -join ' ') + "; exit `$LASTEXITCODE"
```

```diff
-    r"Process failed to launch|electron\.launch|Test timeout of \d+ms exceeded|TimeoutError|"
+    r"Process failed to launch|(?<![\w$])electron\.launch|Test timeout of \d+ms exceeded|TimeoutError|"
```

Line endings, measured as Python bytes after the last edit: the seven CRLF E2E files, the three CRLF unit files, `vitest.config.ts` and `current-focus.md` CRLF on every line; the thirteen LF E2E files, the eight new files, `known-issues.yaml`, `known-issues.md` and the grouping 0 CR; the plan folder LF except `base-e2e-count.txt`, which `baseline.ps1` writes with PowerShell's CRLF (5 bytes). `CapturePage.tsx` is not in the diff: it is back at its row-0 SHA-256 and mtime.

---

## Codex Validation Report

Left for the reviewer. The H1-7 execution review writes the verdict to `.agent/context/handoffs/2026-11-15-e2e-harness-hardening-implementation-critical-review.md`; this section only records it.

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Verdict

Pending: the H1-7 execution review records it here.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE`: hold the browse request until the `ConvertPage` listener is mounted, and make AC-97.7 wait for the Convert page before Ctrl+O | new issue (open, low, ui) | its own session | D-1032: "The spec stays as it is; the flake is fixed later in its own session." |
| `UI-DEV-ELECTRON-RUN-AS-NODE-SILENT`, the `npm run dev` symptom | new issue (open, low, ui) | triage | D-939 |
| `E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED`, unhandled rejections in main | new issue (open, low, ui) | triage | D-935 |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | stays MONITORING | — | D-940 |
| Commit and push | out-of-scope | coordinator and Mat | The executor never commits; Mat pushes on his own |

---

## Decision Log

```yaml
decision_log:
  - id: D-942
    stage: execution
    question: "AC-2 allows the text _electron only in electron-app.ts, but a comment in download-queue.test.ts says Playwright keeps no page snapshot for _electron windows. How does that file pass AC-2?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Reword the comment to say Electron windows (ui/tests/e2e/download-queue.test.ts:1253); no code or assertion changes"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-e2e-harness-hardening/implementation-plan.md AC-2 — only electron-app.ts holds _electron", "ui/tests/e2e/download-queue.test.ts:1253 — the BASE comment"]
    research: { engine: none, sources: [] }
    reasoning: "The comment is prose about Playwright, and the reworded text says the same thing. Leaving it would fail AC-2 on a comment; narrowing AC-2 to code only lost because it would change an approved acceptance criterion. Two-way: one comment line."
  - id: D-943
    stage: execution
    question: "The task cells call e2e-run.ps1 -Receipt R tests/e2e/electron-harness.test.ts, and PowerShell bound the spec path to -MinPassed positionally and exited 1. How does the script take its spec paths?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "Add [CmdletBinding(PositionalBinding = $false)] before param( in e2e-run.ps1, so a bare path lands in -Files (ValueFromRemainingArguments) and the named parameters bind only by name"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-e2e-harness-hardening/e2e-run.ps1:16 — the change", "docs/execution/plans/2026-11-15-e2e-harness-hardening/task.md rows 2, 3 and 6 — the verbatim calls with a bare spec path"]
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The coordinator named this an M-8 change under the hand-over. The probe (ehh-d943-probe.txt) showed the plan-time block failing with Cannot convert value tests/e2e/electron-harness.test.ts to type System.Int32 and the changed block binding every task-cell form correctly. Rewriting the task cells lost because the cells are the approved commands; reordering the parameters lost because any positional binding can still steal a path. Two-way: one attribute line in a plan-local script."
  - id: D-1030
    stage: execution
    question: "Row 0's BASE flag run failed with Process failed to launch! and no bad option line, because Playwright prints electron.exe's stderr only under DEBUG=pw:browser, so AC-18 had no visible negative (S1). How do the flag runs show the real cause?"
    resolution: human
    class: two-way
    mandatory: [M-8]
    chosen: "Set DEBUG=pw:browser for the flag child in three plan-local scripts (baseline.ps1 step 7, e2e-run.ps1 -Flag and session-gate.ps1's flag step), cleared in the parent before and after, and rerun row 0 in full"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-11-15-e2e-harness-hardening/implementation-plan.md AC-18 and S1 — the BASE flag run must fail with bad option", "docs/execution/plans/2026-11-15-e2e-harness-hardening/baseline.ps1:212-217, e2e-run.ps1:45, session-gate.ps1:72 — the changes"]
    research: { engine: none, sources: [] }
    reasoning: "USER_EXPLICIT 2026-11-16, Mat's answer verbatim: 'Add DEBUG (Recommended)'. The option read: 'Set DEBUG=pw:browser for the flag child in three plan-local scripts: baseline.ps1 step 7, e2e-run.ps1 -Flag and session-gate.ps1's flag step. Record it as D-1030 (M-8) and rerun row 0 in full. Both sides of AC-18 can then see the real cause, and nothing else changes.' The rerun showed 4 bad option lines on the BASE side and 0 on the changed side (the gate's flag step printed 187 pw:browser lines)."
  - id: D-1031
    stage: execution
    question: "Row 4's Red b receipt quotes the BASE line const app = await _electron.launch({ in Vitest's diff, and red-check.py's setup-failure pattern electron\\.launch refused it as a launch error. How does red-check tell a quoted source line from a launch failure?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Change the pattern to (?<![\\w$])electron\\.launch, so _electron.launch in quoted source no longer matches while electron.launch: spawn ENOENT still does; add a positive and a negative fixture"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-e2e-harness-hardening/red-check.py:79 — the pattern", "docs/execution/plans/2026-11-15-e2e-harness-hardening/implementation-plan.md S3 — fix the test setup, never the expectation"]
    research: { engine: none, sources: [] }
    reasoning: "The refusal was a false positive of the oracle: the failure was the intended assertion and the matched text was the diff of the file under test. The narrowed pattern keeps every real Playwright launch error refused, which the new negative fixture proves; the selftest went from 36 to 38 fixtures with 0 wrong. Accepting the refusal and stopping lost because nothing was wrong with the Red. Two-way: one plan-local oracle."
  - id: D-1032
    stage: execution
    question: "The H1-2 gate failed ui-electron on AC-97.7 (convert-queue.test.ts:1568), which is not one of D-941's two repeat signatures; the flake also fails 3 of 20 with the BASE spec. Does the gate get a repeat, and what happens to the flake?"
    resolution: human
    class: two-way
    mandatory: [M-11]
    chosen: "Allow one whole-gate repeat for AC-97.7 and register the flake as CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE (Convert Ctrl+O delivery lost before the lazy page mounts), low, ui, open; disclose both gate runs; the spec stays as it is"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-11-15-e2e-harness-hardening/implementation-plan.md D-941 — one repeat only for the teardown-hang and AC-88.12 signatures", "ui/src/renderer/src/router.tsx:50, ui/src/renderer/src/features/converter/convert-commands.ts:102, ConvertPage.tsx:497 — the cause"]
    research: { engine: none, sources: [] }
    reasoning: "USER_EXPLICIT 2026-11-16, Mat's answer verbatim: 'Repeat + register (Recommended)'. The option read: 'Allow one whole-gate repeat for AC-97.7, recorded as D-1032 (your ruling). Register the flake as a new open issue, Convert Ctrl+O delivery lost before the lazy page mounts, low, ui. Disclose both gate runs in the handoff. The spec stays as it is; the flake is fixed later in its own session.' The repeat passed every step (session-gate: all steps exit 0)."
  - id: D-1033
    stage: execution
    question: "Row 0's ui-picker-stub step failed with NU1100: this machine had no NuGet package source, so the win-x64 runtime packs could not restore (S1). How does row 0 build the picker stub?"
    resolution: human
    class: two-way
    mandatory: [M-10, M-13]
    chosen: "Add nuget.org as a NuGet source on this machine; the coordinator ran dotnet nuget add source https://api.nuget.org/v3/index.json -n nuget.org, and baseline.ps1 and session-gate.ps1 keep their ui-picker-stub step unchanged"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-11-12-youtube-client-runtime/implementation-plan.md:684 — D-660, the same missing NuGet source, resolved by Mat", "docs/execution/plans/2026-11-15-e2e-harness-hardening/implementation-plan.md S1 — a row-0 failure goes to Mat"]
    research: { engine: none, sources: [] }
    reasoning: "USER_EXPLICIT 2026-11-16, Mat's answer verbatim: 'Add nuget.org (Recommended)'. A new trusted package source (M-13) and an action only Mat could authorize (M-10). The restore then exited 0 (ehh-nuget-restore-probe.txt); it rewrote the gitignored native/region-picker-stub/obj/, and the gate's ui-picker-stub step passed."
  - id: D-1034
    stage: execution
    question: "Row 0's second run failed the base Electron suite on C1-5 (console-chrome.test.ts: Expected 1, Received 2), outside D-941's signatures (S1). What happens to the failing test?"
    resolution: human
    class: two-way
    mandatory: [M-7]
    chosen: "A separate test-only fix outside Session 78, with this plan unchanged: C1-5's route records a body only for PUT requests and still fulfils the Console's start-level GET; the assertions are unchanged. The coordinator committed it as ebe68e4 with E2E-CONSOLE-C15-COUNTS-GET registered resolved, and row 0 ran again on that commit"
    source_tag: Human-approved
    precedents: ["ui/tests/e2e/console-chrome.test.ts:81 — C1-5", "docs/execution/plans/2026-11-15-e2e-harness-hardening/implementation-plan.md S1 — a base Electron failure beyond D-941 goes to Mat"]
    research: { engine: none, sources: [] }
    reasoning: "USER_EXPLICIT 2026-11-16, Mat's answer verbatim: 'Separate small fix (Recommended)'. A test change with no plan row (M-7), so it went outside this session and its own Codex review approved it at r1. The final row 0 at ebe68e4 passed the base suite (203 passed) and no later run failed C1-5."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-16 | claude-code-local (Claude Opus 5.5) | Initial handoff after H1-1 to H1-5; for the H1-7 execution review |
