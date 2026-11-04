---
agent: gpt-5.6-sol
review_mode: implementation
review_target: docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md
target_plan: docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md
round: 3
verdict: approved
findings_count: 0
dispatch_id: p6-gui-login-item-exec-r3
date: "2026-09-20"
---

# Execution Critical Review: MEU-61 GUI login item

**Intent anchor:** Deliver the OS-backed per-user Electron login item promised by MEU-61: default off, visible only on supported packaged platforms, with independently selectable “Start when I sign in” and “Start minimized” behavior, strict IPC, and deterministic Windows NSIS cleanup. The Windows path is implemented coherently, but the delivered macOS path cannot preserve or launch the minimized variant and therefore does not achieve the full approved platform contract.

## Findings

| # | Severity | Confidence | Finding | Evidence | Violated contract | Concrete failure scenario | Required action | Status |
|---|----------|------------|---------|----------|-------------------|---------------------------|-----------------|--------|
| 1 | High | High | Packaged macOS is classified as supported even though the implementation encodes the minimized variant exclusively through Electron's Windows-only `path`, `args`, and `name` fields. On macOS, both `getLoginItemSettings` probes observe the same app-level `openAtLogin` state, so the minimized-first read reports `minimized: true` whenever login launch is enabled; conversely, the OS launch receives no `--start-minimized` argument, so the window is shown. | `ui/src/main/login-item.ts:45-55`, `ui/src/main/login-item.ts:99-118`, `ui/src/main/login-item.ts:136-148`; installed Electron declarations mark get `path`/`args` Windows-only at `ui/node_modules/electron/electron.d.ts:22114-22124` and set `path`/`args`/`name` Windows-only at `ui/node_modules/electron/electron.d.ts:23530-23554`. Current Electron documentation likewise labels these fields Windows-only: https://www.electronjs.org/docs/latest/api/app#appsetloginitemsettingssettings-macos-windows | Spec promise and API at `docs/build-plan/06-gui.md:1084-1106`; AC-61.1, AC-61.4, AC-61.5, AC-61.6, and AC-61.15 in `docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md`. | On packaged macOS, select “Start when I sign in” with “Start minimized” off. The second set enables the app, but macOS ignores `args`; the fresh read probes minimized first and returns `minimized: true`. At the next sign-in the app starts without `--start-minimized`, `shouldShowWindowAfterLoad` returns true, and the window opens. Selecting “Start minimized” cannot change that launch behavior. | Resolve the macOS contract with a source-backed design and add platform-faithful tests. Either implement a macOS-native mechanism that can preserve the promised minimized choice while respecting the declared source of truth, or formally revise the spec/ACs and support classification so an unsupported macOS control is not shown. | fixed |
| 2 | Medium | High | AC-61.15's test can false-pass a broken main-process integration. It proves the pure helper and only checks that `index.ts` contains the helper's name; an unconditional `window.show()` can coexist with that token and still pass. It also does not assert that the tray “Show window” action calls `show()`. The present production lines are correct, but the material behavior is not protected against regression. | `ui/tests/unit/login-item-ipc.test.ts:75-81`; current guarded call at `ui/src/main/index.ts:494-501`; tray recovery at `ui/src/main/capture-tray.ts:14-20`. | AC-61.15 and IR-5 changed-path assertion strength. | Replace the guarded call with an unconditional `window.show()` while leaving the import/reference in `index.ts`; the test remains green although minimized login launch visibly opens the window. Remove the tray `show()` call; the same test also remains green. | Add a behavioral test around the post-load show decision and the tray Show action, using injected/testable window operations or an equivalent explicit assertion that fails under either mutation. | fixed |

## Scope Reviewed

- Seed and only project handoff: `.agent/context/handoffs/2026-09-20-p6-gui-login-item-MEU-61-handoff.md`.
- Correlated plan set: `docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md`, `task.md`, and `named-sets.json`.
- Canonical specs: `docs/build-plan/06-gui.md#startup-login-item` and `docs/build-plan/07-distribution.md#login-item-uninstall-meu-61`.
- Runtime/UI/installer surfaces claimed by the handoff, including `login-item.ts`, `startup-mode.ts`, IPC/preload/index wiring, `StartAtSignInControl.tsx`, Settings placement/help, `electron-builder.yml`, and `installer.nsh`.
- In-scope unit, RTL, audit, and named E2E tests. The dirty worktree contains unrelated MEU-50/60 and older changes; direct file reads and scoped searches were used instead of attributing the repository-wide diff to MEU-61.

## Commands and Evidence

| Check | Result | Receipt / evidence |
|-------|--------|--------------------|
| Pre-edit canonical-path guard | PASS | `C:/Temp/av-kit/reviewer-r1-pre-edit-guard.txt`; exact target is `.agent/context/handoffs/2026-09-20-p6-gui-login-item-implementation-critical-review.md` |
| Red oracle recheck | PASS | `C:/Temp/av-kit/reviewer-r1-red-oracle.txt`: `PASS: RED_ORACLE ui MEU-61 count=21` |
| Focused MEU-61 Vitest rerun | PASS | `C:/Temp/av-kit/reviewer-r1-focused-vitest.txt`: 6 files, 40 tests passed |
| UI TypeScript typecheck | PASS | `C:/Temp/av-kit/reviewer-r1-typecheck.txt`: `tsc --noEmit`, exit 0 |
| UI lint | PASS | `C:/Temp/av-kit/reviewer-r1-lint.txt`: ESLint with zero warnings, exit 0 |
| Full supplied Vitest receipt | PASS | `C:/Temp/av-kit/meu61-vitest.txt`: 68 files, 552 tests passed |
| Named Electron E2E AC-61.17 | PASS | `C:/Temp/av-kit/meu61-e2e.txt`, `meu61-e2e.json`, and `meu61-e2e-named-pass.txt`: 1 passed; named classifier PASS |
| MEU gate and H1 rerun | PASS | `C:/Temp/av-kit/meu61-gate.txt` and `C:/Temp/av-kit/full-verify-gate.txt`: `PASS: MEU-61 gate` |
| NSIS scan | PASS | `C:/Temp/av-kit/meu61-nsh-scan.txt`: `PASS: MEU-61 scans` |
| Hub audit | PASS | `C:/Temp/av-kit/build-plan-audit.txt`: hub Next and MEU-61 binding PASS |
| OpenAPI drift | PASS | `C:/Temp/av-kit/openapi-check.txt`: exit 0; no product output |

Electron/Playwright was not relaunched: the named AC-61.17 receipt is specific, fresh, and includes both the JSON result and named PASS classifier. The review independently reran the focused unit/RTL suite instead.

## Checklist Results

### Implementation Review (IR-1–IR-7)

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 Live runtime evidence | PASS | Real unpackaged Electron named E2E AC-61.17 ran and asserted the panel count is zero; no login-item dependency override supplies the result. |
| IR-2 Stub behavioral compliance | N/A | No repository/save-get domain stub is introduced. The absent-preload fallback deterministically returns unsupported state and is covered. |
| IR-3 Error mapping completeness | N/A | No REST route or HTTP write surface is added. |
| IR-4 Fix generalization | N/A | Round 1; no prior execution-review correction to generalize. |
| IR-5 Test rigor audit | FAIL | Finding 2 is a material false-pass. The suite also lacks a platform-faithful macOS state model, allowing Finding 1 through while all tests pass. |
| IR-6 Boundary validation coverage | PASS | `login-item-get` accepts only empty/strict `{}`; `login-item-set` requires two booleans and is `.strict()`. Invalid payloads reject before dispatch. No REST/MCP/settings write surface was added. |
| IR-7 Deferral and AC integrity | PASS | AC-61.1 through AC-61.22 all appear in the handoff; AC-61.17 has integration evidence; out-of-scope/deferred rows have concrete build-plan or scheduled-MEU bases. No orphan deferral found. |

### IR-5 Test Rigor Ratings

| Test file | Rating | Basis |
|-----------|--------|-------|
| `ui/tests/unit/login-item.test.ts` | 🟡 Adequate | Strong Windows set/read assertions, but the only macOS assertion is support classification; its fixtures model Windows `args` behavior and miss Finding 1. |
| `ui/tests/unit/login-item-ipc.test.ts` | 🔴 Weak | IPC census/preload assertions are useful, but AC-61.15 can false-pass the material main-window and tray mutations described in Finding 2. |
| `ui/tests/unit/login-item-nsh.test.ts` | 🟢 Strong | Parses executable non-comment lines, proves exactly two deletes, distinguishes Run from StartupApproved, and checks the scoped YAML mapping. |
| `ui/tests/unit/settings-page.test.ts` | 🟢 Strong | Exercises supported/unsupported rendering, parent-child visibility, a real checkbox click through `userEvent`, forbidden settings leaves, and missing-preload fallback. |
| `ui/tests/unit/ipc-strict-census.test.ts` | 🟢 Strong | Runs extra-field and type-invalid payloads across all 19 channels and checks rejection plus zero generic side effects. |
| `ui/tests/unit/gui-actions-audit.test.ts` | 🟡 Adequate | Verifies action IDs, test IDs, channel census, and preload tokens; mainly source/audit assertions by design. |
| `ui/tests/e2e/settings.test.ts` | 🟢 Strong | Named real-Electron assertion proves the unpackaged panel is absent. |

### Adversarial Verification

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 Failing-then-passing proof | PASS | Independent red oracle confirms 21 intended AC titles failed; current focused suite and full receipt are green. |
| AV-2 No bypass hacks | PASS | Gate/scans pass and no skip/only/todo or assertion-neutralizing construct was found in the MEU tests. |
| AV-3 Changed paths asserted | FAIL | AC-61.15 does not behaviorally assert the `index.ts` show branch or tray recovery; see Finding 2. |
| AV-4 No skipped/xfail masking | PASS | No MEU-61 test is skipped or focused. |
| AV-5 No unresolved placeholders | PASS | MEU scan passes for the declared production paths. |
| AV-6 Source-backed criteria | PASS | Criteria are tagged Spec, Local Canon, Research-backed, or Human-approved; no unsourced product behavior was introduced. |

### Documentation Review

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | FAIL | The handoff claims the AC set is complete, but the packaged-macOS behavior promised by the spec is not delivered; see Finding 1. |
| DR-2 Residual old terms | PASS | Scoped scans reject the forbidden service/autostart and Squirrel-path patterns. |
| DR-3 Downstream references | PASS | GUI action index, channel census, preload keys, MEU registry/status, and hub Next are updated consistently. |
| DR-4 Verification robustness | FAIL | AC-61.15 has the false-pass described in Finding 2. |
| DR-5 Evidence auditability | PASS | Receipts exist under `C:/Temp/av-kit/`, are readable, and key checks were independently rerun. |
| DR-6 Cross-reference integrity | FAIL | The implementation's macOS behavior conflicts with the platform promise and Electron's platform-specific option contract. |
| DR-7 Evidence freshness | PASS | Supplied receipts are dated 2026-09-20 and reproduced focused checks agree with them. |
| DR-8 Completion vs residual risk | FAIL | “All ACs met” is not supportable until Finding 1 is resolved. |

## Out-of-Contract Observations

None.

## Required Follow-up

1. Resolve Finding 1 through `/execution-corrections`, including a source-backed decision for macOS and tests whose fake Electron behavior matches platform semantics.
2. Add an assertion that fails if the loaded main window is shown under `--start-minimized`, plus an assertion that the tray Show action still invokes `show()`.
3. Re-run the focused suite, typecheck, lint, MEU gate, and the execution-critical review after corrections. Do not start MEU-50 as part of this correction.

## Verdict

`changes_required` — The Windows implementation, strict IPC boundary, unpackaged/Linux hiding, NSIS cleanup, and evidence bundle are sound, but the packaged-macOS path violates the approved user-visible contract. Finding 1 is an evidence-backed High behavioral defect, so the Materiality Gate requires a blocking verdict. Finding 2 independently requires stronger regression coverage under IR-5.

verdict: changes_required

---

## Round 2 Recheck (2026-09-20)

**Intent anchor:** MEU-61 must deliver the OS-backed per-user Electron login item on supported packaged Windows and macOS copies, including a separately selectable minimized launch, while keeping Linux/unpackaged copies hidden, IPC strict, Windows argv variants distinct, and NSIS cleanup deterministic. The Windows, IPC, UI, and NSIS surfaces remain coherent, but the proposed macOS correction relies on Electron fields that the installed Electron 42.9.3 contract says do not work on macOS 13 and newer, so the promised macOS minimized behavior is still not delivered.

### Findings

| # | Severity | Confidence | Finding | Evidence | Violated contract | Concrete failure scenario | Required action | Status |
|---|----------|------------|---------|----------|-------------------|---------------------------|-----------------|--------|
| 1 | High | High | Round 1 Finding 1 remains open. The correction replaced Windows-only argv behavior with `openAsHidden` / `wasOpenedAsHidden`, but Electron 42.9.3 explicitly marks both fields deprecated and unavailable on macOS 13 and newer. The new Darwin fakes implement behavior that current Electron does not provide on those OS versions, so their green and mutation-kill results do not establish the promised packaged-macOS behavior. This is verification of the original macOS failure, not a new nearby variant. | Installed Electron is 42.9.3 (`ui/node_modules/electron/package.json:3`). Its declarations say `openAsHidden` does not work on macOS 13+ (`ui/node_modules/electron/electron.d.ts:1248-1255`, `22047-22068`, `23505-23514`). Production depends on those fields at `ui/src/main/login-item.ts:114-126`, `153-169`, and `187-190`, with the show decision at `ui/src/main/index.ts:495-502`. The fake state model is at `ui/tests/unit/login-item.test.ts:244-296`. `C:/Temp/av-kit/reviewer-r2-darwin-mutation.txt` kills 4/4 source-logic mutants but necessarily exercises that fake model. | Spec promise and macOS support classification at `docs/build-plan/06-gui.md:1084-1096`, Start-minimized contract in the same section, and AC-61.5, AC-61.6, and AC-61.15 at `docs/execution/plans/2026-09-20-p6-gui-login-item/implementation-plan.md:155-166`. | On a normal packaged copy running macOS 13+, the user enables Start at sign-in and Start minimized. Electron cannot persist `openAsHidden` and does not expose `wasOpenedAsHidden`; the read-back cannot preserve the minimized selection and `loginLaunchShouldHideWindow` returns false, so the post-load branch shows the window. | Resolve the macOS 13+ contract with a source-backed design and platform-faithful tests. If the OS-backed minimized choice cannot be delivered within the OS-as-SoT constraint, revise support classification/spec/ACs so the UI does not promise it. | fixed |
| 2 | Medium | High | Round 1 Finding 2 remains open, although tray coverage is fixed. The AC-61.15 source oracle checks only token order and presence: it accepts a syntactically valid unguarded `window.show()` and also accepts removing the `loginLaunchShouldHideWindow` argument while its import remains. | `ui/tests/unit/login-item-ipc.test.ts:75-93`. `C:/Temp/av-kit/reviewer-r2-index-mutation.txt` records `UNGUARDED_MUTANT_SURVIVED=true`, `MACOS_HIDE_WIRING_REMOVAL_SURVIVED=true`, and `TRAY_SHOW_REMOVAL_SURVIVED=false`; both surviving mutants transpile cleanly. Current production is correctly guarded at `ui/src/main/index.ts:495-502`, and tray Show is present at `ui/src/main/capture-tray.ts:14-20`, but the regression oracle is still incomplete. | AC-61.15 and IR-5 changed-path assertion strength. | A future edit can leave the helper tokens/imports intact but invoke `shouldShowWindowAfterLoad` as a discarded expression before an unconditional block, or remove the second argument. The focused suite remains green while minimized login launches visibly open the window. | Add a behavioral test of the post-load show decision and its macOS hide wiring (or an equivalently structural assertion that fails under both demonstrated mutants) while retaining the tray Show assertion. | fixed |

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|--------------|----------------|
| 1 — packaged macOS minimized behavior | open | Still open: the corrected fields are unavailable on macOS 13+, so the original user-visible failure persists. |
| 2 — AC-61.15 false-pass | open | Still open: tray removal is now caught, but two material index/wiring mutants survive. |

### Commands and Evidence

| Check | Result | Receipt / evidence |
|-------|--------|--------------------|
| Pre-edit canonical-path guard | PASS | `C:/Temp/av-kit/reviewer-r2-pre-edit-guard.txt`; exact target is `.agent/context/handoffs/2026-09-20-p6-gui-login-item-implementation-critical-review.md` |
| Correction Red receipt | PASS as Red evidence | `C:/Temp/av-kit/meu61-corr-red.txt`: 4 failed / 14 passed before correction |
| Correction Green receipt | PASS | `C:/Temp/av-kit/meu61-corr-green.txt`: 6 files, 43 tests passed |
| Independent focused Vitest rerun | PASS | `C:/Temp/av-kit/reviewer-r2-focused-vitest.txt`: 2 files, 18 tests passed |
| Darwin behavior mutation check | PASS for implemented fake contract | `C:/Temp/av-kit/reviewer-r2-darwin-mutation.txt`: 4/4 mutants killed |
| AC-61.15 index/tray mutation check | FAIL | `C:/Temp/av-kit/reviewer-r2-index-mutation.txt`: unguarded-show and removed-hide-wiring mutants survived; tray removal was killed |
| Typecheck / lint / scans | PASS | `C:/Temp/av-kit/meu61-corr-typecheck.txt`, `meu61-corr-lint.txt`, and `meu61-corr-scans.txt` |
| MEU-61 correction gate | PASS | `C:/Temp/av-kit/meu61-corr-gate.txt` |
| Named Electron E2E AC-61.17 | PASS, not relaunched | `C:/Temp/av-kit/meu61-e2e.txt` and `meu61-e2e.json`: real unpackaged Electron, 1 passed; Darwin correction does not affect this absence case |
| Local Electron platform contract | FAIL for proposed macOS design | Electron 42.9.3 declarations at `ui/node_modules/electron/electron.d.ts:1248-1255`, `22047-22068`, and `23505-23514` |
| Closeout review validator | Expected blocking FAIL | `C:/Temp/av-kit/r2-review-validator.txt`: `verdict='changes_required' expected 'approved'`; H1-7 correctly remains open |

### Checklist Results

#### Implementation Review (IR-1–IR-7)

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 Live runtime evidence | PASS for AC-61.17 only | The named real-Electron test proves the unpackaged panel is absent. It does not establish packaged macOS login behavior, and no relaunch was needed for this correction recheck. |
| IR-2 Stub behavioral compliance | N/A | No repository persistence stub is introduced. |
| IR-3 Error mapping completeness | N/A | No REST route or HTTP write surface is introduced. |
| IR-4 Fix generalization | FAIL | The macOS fix was not checked against the installed Electron contract for macOS 13+, and the index-test correction does not generalize across the demonstrated unguarded and unwired mutations. |
| IR-5 Test rigor audit | FAIL | The Darwin tests strongly assert the implemented fake but model unavailable modern-macOS behavior; the AC-61.15 index oracle admits two material mutants. |
| IR-6 Boundary validation coverage | PASS | `login-item-get` remains empty/strict; `login-item-set` requires exactly two booleans; the 19-channel census and zero-side-effect negative cases remain covered. |
| IR-7 Deferral and AC integrity | PASS | AC-61.1–61.22 remain represented; AC-61.17 retains integration evidence; no MEU-50 or MEU-60 work was pulled into scope. |

#### IR-5 Test Rigor Ratings

| Test file | Rating | Basis |
|-----------|--------|-------|
| `ui/tests/unit/login-item.test.ts` | 🔴 Weak | Precise assertions and 4/4 mutation kills for the fake state model, but that model assumes deprecated fields work where Electron says they are unavailable; the material macOS contract false-passes. |
| `ui/tests/unit/login-item-ipc.test.ts` | 🔴 Weak | IPC/count/helper assertions are useful and tray removal is caught, but two syntactically valid material index/wiring mutations survive. |
| `ui/tests/unit/login-item-nsh.test.ts` | 🟢 Strong | Strips comments, proves exactly two executable deletes, distinguishes Run from StartupApproved, and checks the scoped YAML include. |
| `ui/tests/unit/settings-page.test.ts` | 🟢 Strong | Exercises support hiding, parent-child visibility, a real checkbox click, forbidden settings leaves, and absent-preload fallback. |
| `ui/tests/unit/ipc-strict-census.test.ts` | 🟢 Strong | Covers extra-field and type-invalid payloads across all 19 channels and asserts zero generic side effects. |
| `ui/tests/unit/gui-actions-audit.test.ts` | 🟡 Adequate | Verifies action IDs, test IDs, IPC census, and preload tokens; source-oriented by design. |
| `ui/tests/e2e/settings.test.ts` | 🟢 Strong for AC-61.17 | Real Electron asserts the unpackaged panel count is zero; it intentionally does not prove packaged login launch. |

#### Documentation Review

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | FAIL | The correction handoff says Finding 1 is resolved, but the installed Electron contract disproves modern-macOS minimized support. |
| DR-2 Residual old terms | PASS | No forbidden service/Squirrel behavior was introduced; Windows still does not pass `openAsHidden`. |
| DR-3 Downstream references | PASS | IPC count 19, action IDs, preload keys, NSIS paths, and Hub Next remain consistent. |
| DR-4 Verification robustness | FAIL | Platform-unfaithful Darwin fakes and the two surviving AC-61.15 mutants can mask material regressions. |
| DR-5 Evidence auditability | PASS | Supplied receipts are readable, and focused tests plus both mutation checks were independently reproduced. |
| DR-6 Cross-reference integrity | FAIL | The updated spec/plan claim `openAsHidden` supplies macOS minimized behavior, contrary to the installed Electron contract on macOS 13+. |
| DR-7 Evidence freshness | PASS | Correction receipts and independent Round 2 receipts are dated 2026-09-20 and agree on the currently implemented logic. |
| DR-8 Completion vs residual risk | FAIL | A supported packaged-macOS path still violates the promised minimized behavior, so “2/2 resolved” is not supportable. |

### Out-of-Contract Observations

None.

### Required Follow-up

1. Resolve the original macOS High with a source-backed macOS 13+ design or narrow the macOS support/spec promise so the control cannot offer behavior Electron cannot deliver.
2. Replace the AC-61.15 token-order assertion with a behavioral or structurally exact oracle that kills both demonstrated index mutants while keeping the tray recovery assertion.
3. Re-run the focused suite, typecheck, lint, MEU-61 gate, and independent execution-critical recheck. Do not start MEU-50 or absorb MEU-60 work.

### Verdict

`changes_required` — Round 1 Finding 1 remains an evidence-backed High behavioral defect: the macOS correction depends on Electron fields that do not work on macOS 13 and newer, so the delivered behavior still fails the approved platform promise. Round 1 Finding 2 also remains open as a Medium IR-5 weakness because two material mutations false-pass. The Materiality Gate therefore requires a blocking verdict.

verdict: changes_required

---

## Round 3 Recheck (2026-09-20)

**Intent anchor:** MEU-61 must deliver an OS-backed, default-off, per-user Electron login item without introducing a service or settings-store shadow state. Packaged Windows supports the optional `--start-minimized` argv variant; packaged macOS supports Start at sign in through `openAtLogin` but does not advertise Start minimized because Electron 42 cannot persist that behavior on macOS 13+.

### Findings

No Critical, High, Medium, or Low findings survived verification against the updated spec and plan.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|--------------|----------------|
| 1 — packaged macOS minimized behavior | open | Fixed. The contract is now explicitly narrower: macOS remains supported for `openAtLogin`, always reports `minimized: false` and `startMinimizedSupported: false`, never writes `openAsHidden`, and the Settings UI omits Start minimized. Evidence: `docs/build-plan/06-gui.md:1104-1110`, `ui/src/main/login-item.ts:128-136`, `ui/src/main/login-item.ts:159-172`, `ui/tests/unit/login-item.test.ts:254-299`, and `ui/tests/unit/settings-page.test.ts:652-665`. |
| 2 — AC-61.15 false-pass | open | Fixed. `revealMainWindow` owns the post-load `show()` decision, `index.ts` has no `window.show(` and passes the login-launch hide result as the third argument, helper spies exercise both hidden inputs, and the source oracle kills both required mutants. Evidence: `ui/src/main/startup-mode.ts:11-25`, `ui/src/main/index.ts:495-499`, `ui/tests/unit/login-item-ipc.test.ts:75-98`, and `C:/Temp/av-kit/reviewer-r3-index-mutation.txt`. |

### Commands and Evidence

| Check | Result | Receipt / evidence |
|-------|--------|--------------------|
| Pre-edit canonical-path guard | PASS | `C:/Temp/av-kit/reviewer-r3-pre-edit-guard.txt`; derived and requested targets both equal `.agent/context/handoffs/2026-09-20-p6-gui-login-item-implementation-critical-review.md`. |
| Correction Red receipt | PASS as Red evidence | `C:/Temp/av-kit/meu61-corr-r3-red.txt`: 3 files failed, 7 tests failed, 30 passed before the Round 3 correction. |
| Correction Green receipt | PASS | `C:/Temp/av-kit/meu61-corr-r3-green.txt`: 6 files, 43 tests passed. |
| Required independent focused Vitest | PASS | `C:/Temp/av-kit/reviewer-r3-focused-vitest.txt`: `login-item.test.ts`, `login-item-ipc.test.ts`, and `settings-page.test.ts`; 3 files, 37 tests passed. |
| Independent six-file Vitest | PASS | `C:/Temp/av-kit/reviewer-r3-six-file-vitest.txt`: 6 files, 43 tests passed. The pre-existing React `act(...)` warning is in an AC-23 settings test and does not affect the MEU-61 assertions. |
| Darwin narrowed-contract check | PASS | `C:/Temp/av-kit/reviewer-r3-darwin-contract.txt`: AC-61.6 Darwin write test passed; it asserts `startMinimizedSupported: false`, `minimized: false`, empty args, and no `openAsHidden`. |
| AC-61.15 mutation check | PASS | `C:/Temp/av-kit/reviewer-r3-index-mutation.txt`: baseline exact; inserted `window.show()` killed; dropped third `revealMainWindow` argument killed. Mutants were constructed in memory; no product file was edited. |
| Typecheck / lint / scans | PASS | `C:/Temp/av-kit/reviewer-r3-typecheck.txt`, `reviewer-r3-lint.txt`, and `reviewer-r3-scans.txt`; TypeScript and ESLint exit 0, scans report `PASS: MEU-61 scans`. |
| Named Electron E2E AC-61.17 | PASS, not relaunched | `C:/Temp/av-kit/meu61-e2e.txt`: real unpackaged Electron, 1 passed; this correction did not change the unpackaged-absence path. |
| Electron platform contract | PASS for narrowed design | Installed Electron 42.9.3 at `ui/node_modules/electron/package.json:3`; declarations state `openAsHidden` / `wasOpenedAsHidden` are unavailable on macOS 13+ at `ui/node_modules/electron/electron.d.ts:1248-1255`, `22047-22068`, and `23505-23514`. Current Electron docs remove `openAsHidden` and retain `openAtLogin`: https://www.electronjs.org/docs/latest/api/app#appsetloginitemsettingssettings-macos-windows |

The repository-wide UI suite was not rerun because the user identified four unrelated, dirty MEU-60 Capture failures. Those failures are outside MEU-61 and were not used to weaken any MEU-61 gate.

### Checklist Results

#### Implementation Review (IR-1–IR-7)

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 Live runtime evidence | PASS for the integration AC | The named real-Electron AC-61.17 receipt proves the unpackaged Settings panel is absent. Live HKCU or packaged-macOS mutation is explicitly outside this MEU's acceptance contract. |
| IR-2 Stub behavioral compliance | N/A | No repository persistence stub is introduced; the OS remains source of truth. |
| IR-3 Error mapping completeness | N/A | No REST route or HTTP write surface is introduced. |
| IR-4 Fix generalization | PASS | The macOS correction updates spec, plan, state shape, renderer visibility, read/write behavior, and tests. The show-path correction covers argv hiding, login-launch hiding, direct `index.ts` showing, third-argument wiring, and tray recovery. |
| IR-5 Test rigor audit | PASS | No weak test remains in the MEU-61 scope; the two previously demonstrated material mutants are now killed. Ratings are recorded below. |
| IR-6 Boundary validation coverage | PASS | `login-item-get` remains empty/strict and `login-item-set` requires exactly two booleans; extra/type-invalid payloads reject before side effects across the 19-channel census. |
| IR-7 Deferral and AC integrity | PASS | AC-61.1–61.22 remain represented in the handoff; AC-61.17 retains integration evidence; macOS Start minimized is explicitly not promised rather than silently deferred; MEU-50 and MEU-60 remain outside scope. |

#### IR-5 Test Rigor Ratings

| Test file | Rating | Basis |
|-----------|--------|-------|
| `ui/tests/unit/login-item.test.ts` | 🟢 Strong | Asserts Windows variants and approval fields, invalid types and zero writes, default off, and the narrowed Darwin read/write values including absence of `openAsHidden`. |
| `ui/tests/unit/login-item-ipc.test.ts` | 🟢 Strong | Asserts strict IPC/census/preload behavior, whole-token argv matching, behavioral `show()` spies, exact main-process wiring, forbidden token absence, and tray recovery. |
| `ui/tests/unit/login-item-nsh.test.ts` | 🟢 Strong | Strips comments, proves exactly two executable deletes, distinguishes Run from StartupApproved, and checks the scoped YAML include. |
| `ui/tests/unit/settings-page.test.ts` | 🟢 Strong | Exercises supported/unsupported rendering, parent-child visibility, the `startMinimizedSupported: false` branch, a real checkbox click, no settings PUT, and absent-preload fallback. |
| `ui/tests/unit/ipc-strict-census.test.ts` | 🟢 Strong | Covers extra-field and type-invalid payloads across all 19 channels and asserts zero generic side effects. |
| `ui/tests/unit/gui-actions-audit.test.ts` | 🟡 Adequate | Verifies action IDs, test IDs, IPC census, and preload tokens; it is intentionally source/audit-oriented. |
| `ui/tests/e2e/settings.test.ts` | 🟢 Strong for AC-61.17 | Real Electron asserts the unpackaged panel count is zero. |

#### Adversarial Verification

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 Failing-then-passing proof | PASS | Round 3 correction Red records 7 failures; both supplied and independent Green runs record 43 passes across 6 files. |
| AV-2 No bypass hacks | PASS | No assertion bypass, conditional early return, or mocked assertion function appears in the MEU-61 tests; scoped scans pass. |
| AV-3 Changed paths asserted | PASS | Darwin read/write and UI visibility are value-asserted; post-load showing is spy-asserted and source-wiring-asserted; both named regressions are killed. |
| AV-4 No skipped/xfail masking | PASS | The full focused six-file run has 43 passing tests and no skipped/focused MEU-61 test. |
| AV-5 No unresolved placeholders | PASS | `assert-meu-scans.ps1` passes over the declared production paths. |
| AV-6 Source-backed criteria | PASS | The narrowed macOS rule is grounded in the installed Electron 42 contract, Electron issue 37228 / PR 37244, and the updated canonical spec. |

#### Documentation Review

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | PASS | The correction claims match the live code, UI, tests, and independently reproduced receipts. |
| DR-2 Residual old terms | PASS | Scoped scans pass; `index.ts` contains neither `openAsHidden` nor `window.show(`. |
| DR-3 Downstream references | PASS | Spec, plan ACs, handoff AC table, IPC count, action IDs, preload keys, NSIS paths, and Hub Next remain aligned. |
| DR-4 Verification robustness | PASS | The specified Darwin contract and both AC-61.15 mutants are directly caught. |
| DR-5 Evidence auditability | PASS | Commands and receipts are explicit and reproducible under `C:/Temp/av-kit/`. |
| DR-6 Cross-reference integrity | PASS | The updated plan/spec no longer promise macOS Start minimized and retain Windows argv behavior. |
| DR-7 Evidence freshness | PASS | Round 3 receipts are dated 2026-09-20 and independently reproduce the supplied 43-test Green result. |
| DR-8 Completion vs residual risk | PASS | The remaining lack of live packaged OS mutation is identified as out of contract, not presented as completed evidence. |

### Out-of-Contract Observations

None.

### Required Follow-up

No implementation correction is required for MEU-61. The orchestrator may proceed with the plan's post-review closeout; this review does not authorize MEU-50, MEU-60, commit, push, merge, release, or deploy work.

### Residual Risk

No live packaged Windows HKCU mutation or packaged macOS login launch was performed. That clean-machine proof remains the separately declared Phase 7 path and is not an AC for MEU-61; the delivered unit/RTL contract, real unpackaged Electron absence case, strict IPC, and installer cleanup are verified.

### Verdict

`approved` — Both prior findings are independently verified fixed. The implementation now achieves the updated user intent: packaged Windows supports Start at sign in with an optional `--start-minimized` variant, packaged macOS supports Start at sign in without advertising unavailable minimized behavior, and the AC-61.15 regression oracle rejects both demonstrated material mutations. No evidence-backed High or Critical finding remains after the Materiality Gate.

verdict: approved
