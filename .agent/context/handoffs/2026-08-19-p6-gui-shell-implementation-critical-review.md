---
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-19-p6-gui-shell/implementation-plan.md"
agent: gpt-5.6-sol
verdict: approved
findings_count: 0
round: 2
---

# Execution Critical Review: p6-gui-shell — Round 2

## Intent Anchor

Session 7 was intended to deliver MEU-19 only: a usable Electron/React shell that safely owns a newly spawned `python -m avkit_api` backend, refuses unsafe live identity, exposes only the approved IPC boundary, and wires the skeleton routes, console, startup metrics, and persistence without starting MEU-20–25. Round 2 asks whether the delivered current state, including the round-1 corrections, now achieves that intent.

## Findings

| Finding | Severity |
|---|---|
| None. No current High or Critical behavioral, contract, persistence, or false-implementation finding survived independent verification. | — |

The prior F7 test-rigor concern is not counted as a round-2 blocking finding: a temp-copy mutation removing the `boot()` → `resolveBootIdentity` wire survived all 29 Vitest tests. That is a Medium residual test-hardening gap under IR-5, while the unmodified production bundle independently passed the live unsupported-descriptor probe. The workflow's Verdict Rule requires a current High/Critical functionality-first finding for `changes_required`.

## Round-1 Finding Recheck

| Finding | Recheck result |
|---|---|
| F1 — live identity, readiness ownership, and quit wait | **Fixed.** A real rebuilt-Electron probe seeded schema 999 against a live PID: the descriptor stayed schema 999, the PID stayed alive, no port sibling appeared, and cleanup left no probe process. Production `boot()` calls `resolveBootIdentity`, `confirmReadyAndPublish`, `assertOwnedIdentity`, and `waitPidExit` (`ui/src/main/index.ts:178-213,233-256`; `ui/src/main/python-manager.ts:60-121`). |
| F2 — rail and palette navigation | **Fixed.** Fresh Electron actions reached `#/transcript` and `#/settings`; `AppShell` and the command registry invoke `navigateShell` (`ui/src/renderer/src/components/layout/AppShell.tsx:69`; `ui/src/renderer/src/registry/commandRegistry.ts:38-58`). |
| F3 — mounted console actions and snapshot | **Fixed.** The mounted `AppShell` test observed a clipboard write and settings request; production issues `PUT /settings/app`, consumes the snapshot/subscription/poll chain, and `get-log-snapshot` returns buffered state rather than a constant array (`ui/src/renderer/src/components/layout/AppShell.tsx:73-85`; `ui/src/main/ipc.ts:93-113,306-309`). |
| F4 — path and byte-limit boundary | **Fixed.** The direct handler oracle rejects `C:/outside/tool.exe` with zero FS side effects and returns exactly `A` for `maxBytes: 1` (`ui/src/main/ipc.ts:252-290`; `ui/tests/unit/secret-paths.test.ts:39-63`). |
| F5 — persisted UI/window state | **Fixed.** Persist helpers write storage; `AppShell` consumes `usePersistedState`; `BrowserWindow` consumes `createWindowOptions(uiStore)` and saves bounds (`ui/src/renderer/src/hooks/usePersistedState.ts:45-80`; `ui/src/main/index.ts:74-105,307-320`). |
| F6 — startup metric payload/readiness | **Fixed.** IPC waits for ready, forwards the validated key/value, and production posts `{key, value_ms}` to the port-bearing ready URL (`ui/src/main/ipc.ts:224-243`; `ui/src/main/index.ts:279-293`). The fresh test asserts the exact URL, GUI Bearer, key, and value. |
| F7 — production-path regression sensitivity | **Partially fixed / non-blocking residual.** Mounted AppShell and real-Electron route tests now catch F2/F3 removal, and direct production handlers catch F4/F6. However, the F1 temp-copy mutation survived the full 29-test suite, so the identity call-site still lacks a durable production-path regression test. |

## Scope

The exact correlated set is the approved plan and task at `docs/execution/plans/2026-08-19-p6-gui-shell/`, the sole MEU-19 handoff, `docs/build-plan/06-gui.md` plus the live-identity/spawn and named-set locks in `07-distribution.md`, current Python CLI files/tests, all files under `ui/src/main/`, `ui/src/renderer/`, `ui/tests/unit/`, and `ui/tests/e2e/`, plus MEU/phase/Hub SSOT. The workspace has no `.git` directory, so current file state and receipts—not a diff—are the evidence.

Scope stayed locked to Session 7 / MEU-19. No product, test, plan, MEU handoff, SSOT, FastAPI router, MCP tool, or MEU-20–25 file was edited by this review.

## IR-1–IR-7 Checklist

| Check | Result | Evidence |
|---|---|---|
| IR-1 — Live runtime evidence | Pass | `tests/integration/test_backend_spawn.py` spawned a real backend (2 integration cases within 8/8 Python tests). Real Electron passed the F1 refusal probe and both F2 route probes; the post-correction 10/10 Playwright receipt was also re-read. |
| IR-2 — Stub behavioral compliance | N/A | MEU-19 owns no repository/UoW stub; the skeleton routes are the approved Session 7 state. |
| IR-3 — Error mapping completeness | N/A | FastAPI routers were outside write scope and unchanged; no route-error-mapping claim is introduced. |
| IR-4 — Fix generalization | Pass for delivered behavior | F1–F6 call-site census and direct/runtime probes now reach identity, navigation, console, path/size, persistence, and metrics production surfaces. The identity regression-test weakness is retained under IR-5 rather than escalated as a nearby F1 mutation. |
| IR-5 — Test rigor audit | Partial; Medium residual | All test files were audited below. Behavior coverage is materially stronger, but `C:/Temp/av-kit/p6-gui-exec-r2-f7-mutation.txt` proves the full Vitest suite misses removal of the `boot()` identity wire. |
| IR-6 — Boundary validation coverage | Pass | The strict 12-channel census passed; external `.exe` rejection and `maxBytes:1` passed with side-effect checks; unknown/wrong payloads fail before side effects. |
| IR-7 — Deferral and AC integrity | Pass | The sole handoff contains all 23 AC-19 IDs. MEU-20–25 exist as scheduled owners. MEU-19 is `ready_for_review` at the no-slash plan path, phase `"6"` has the slash path, and Hub Next is exactly `/create-plan p6-gui-downloader`. |

## IR-5 Per-File Test Ratings

| Test file(s) | Rating | Rationale |
|---|---|---|
| `tests/unit/test_backend_cli.py`; `tests/integration/test_backend_spawn.py` | 🟢 Strong | Exact negative parser behavior, atomic descriptor/secrets, real process/PID/port/HTTP and dual-token assertions. |
| `ui/tests/unit/api-fetch.test.ts`; `copy-mcp-config.test.ts`; `ipc-strict-census.test.ts`; `secret-paths.test.ts`; `startup-metrics.test.ts`; `app-shell-wiring.test.ts` | 🟢 Strong | Specific positive/negative values and side effects; the mounted shell now proves route/copy/settings wiring. |
| `ui/tests/unit/api-base-ipc.test.ts`; `web-prefs-ipc.test.ts`; `single-instance.test.ts`; `dev-spawn.test.ts`; `shutdown-owned.test.ts`; `backend-logs.test.ts`; `console-actions.test.ts`; `persist-ui.test.ts`; `shell-home.test.ts`; `command-palette.test.ts`; `g36-csp.test.ts` | 🟡 Adequate | Assertions are concrete, but some integration/call-site behavior is proven elsewhere or remains helper-level. |
| `ui/tests/unit/live-identity.test.ts` | 🟡 Adequate | Strong decision-table negatives, but it does not fail when production `boot()` stops calling the decision path. |
| `ui/tests/unit/e2e-wiring.test.ts` | 🔴 Weak | Proves files/test IDs exist, not semantic reachability. This contributes to the non-blocking F7 Medium residual. |
| `ui/tests/e2e/launch.test.ts`; `command-palette-nav.spec.ts` | 🟢 Strong | Real Electron asserts shell state and the corrected transcript/settings hash transitions. |
| `ui/tests/e2e/console-panel.test.ts` | 🔴 Weak | Visibility-only; mounted copy/log-to-file behavior is instead proven by `app-shell-wiring.test.ts`. |
| `ui/tests/unit/setup.ts`; `helpers/electron-stub.ts`; `ipc-channels.ts`; `ui/tests/e2e/global-setup.ts`; `global-teardown.ts`; `test-ids.ts` | Support | Fixtures/configuration/constants, not executable behavior suites. |

## Adversarial Verification Checklist

| Check | Result | Evidence |
|---|---|---|
| AV-1 — Failing-then-passing proof | Pass for recorded lifecycle; fresh Green independently rerun | The MEU handoff contains Red evidence; round 2 independently reran current Green and did not treat the implementer's correction prose as proof. |
| AV-2 — No bypass hacks | Pass | Fresh G36 scan found no skip/only/todo masking. |
| AV-3 — Changed paths asserted | Partial | F2–F6 production surfaces have direct or mounted assertions; the F1 call-site mutation survives. |
| AV-4 — No skipped/xfail masking | Pass | `p6-gui-exec-r2-hygiene.txt`. |
| AV-5 — No unresolved placeholders | Pass | `p6-gui-exec-r2-hygiene.txt`. |
| AV-6 — Source-backed criteria | Pass | Recheck uses only approved ACs, named sets, and the user-specified round-1 corrections. |

## Commands Executed — Round 2

All current commands used PowerShell all-stream redirects and isolated `C:/Temp/av-kit/p6-gui-exec-r2-*` receipts.

| Verification | Result | Receipt |
|---|---|---|
| Correction-focused Vitest suites | 7 files / 15 tests passed | `C:/Temp/av-kit/p6-gui-exec-r2-correction-tests.txt` |
| Full UI type + Vitest + lint + build | 19 files / 29 tests passed; type/lint/build clean | `C:/Temp/av-kit/p6-gui-exec-r2-ui-gates.txt` |
| Real Electron transcript + palette settings routes | 2 passed | `C:/Temp/av-kit/p6-gui-exec-r2-e2e-nav.txt` |
| Post-correction full Playwright receipt re-read | 10 passed | `C:/Temp/av-kit/e2e-exec-r1-corrections.txt`; read receipt `p6-gui-exec-r2-e2e-prior-read.txt` |
| Live unsupported-schema descriptor probe | Refused: schema stayed 999, live PID unsignaled, no port sibling | `C:/Temp/av-kit/p6-gui-exec-r2-f1-live-descriptor.txt`; cleanup `p6-gui-exec-r2-f1-cleanup.txt` |
| F7 temp-copy mutation | Mutation survived all 29 tests | `C:/Temp/av-kit/p6-gui-exec-r2-f7-mutation.txt` |
| Python CLI unit + real spawn integration | 8 passed | `C:/Temp/av-kit/p6-gui-exec-r2-python-cli.txt` |
| Python type/lint | 0 errors/warnings; Ruff clean | `C:/Temp/av-kit/p6-gui-exec-r2-python-quality.txt` |
| SSOT, AC set, deferral owners, G36/placeholders | All pass | `p6-gui-exec-r2-ssot.txt`; `p6-gui-exec-r2-ac-coverage.txt`; `p6-gui-exec-r2-deferrals.txt`; `p6-gui-exec-r2-hygiene.txt` |
| Canonical path/write-scope pre-edit guard | Pass | `C:/Temp/av-kit/p6-gui-exec-r2-pre-edit-guard.txt` |

## Open Questions and Assumptions

- No product decision is needed. The approved plan already resolves the Session 7 scope and later-MEU ownership.
- The F7 mutation result is retained as test-hardening residual risk, not promoted into a new High variant of corrected F1.
- No live YouTube/model call was required or made.

## Verdict

`approved` — F1–F6 now satisfy the approved MEU-19 behavior under fresh source inspection, direct handler tests, a real spawned backend, and real Electron probes. No current High/Critical finding remains. The F7 mutation-survival gap is explicitly retained as non-blocking Medium residual risk under the workflow's materiality and verdict rules.

## Residual Risk

The current product behavior is approved, but regression protection is uneven: removing the production `boot()` live-identity call still leaves the full Vitest suite green, and the console Playwright file remains visibility-only. These are concrete follow-up test-hardening opportunities; they do not negate the independently exercised current behavior and do not authorize Session 8–12 work in this review.

---

## Prior Round Record — 2026-08-20 (Round 1 plus implementer corrections)

# Execution Critical Review: p6-gui-shell — Round 1

## Intent Anchor

Session 7 was intended to deliver MEU-19 only: a real Electron shell that safely owns and discovers its `python -m avkit_api` child, enforces the approved IPC boundary, and wires the skeleton home, nav, palette, console, and persistence without starting the later GUI pages or distribution work. The Python runtime CLI achieves its portion, but the integrated Electron delivery does not achieve that intent because ownership, shell actions, persistence, and boundary behavior fail direct probes while helper-level tests remain green.

## Findings

| Finding | Severity |
|---|---|
| **F1 — `boot()` bypasses `LIVE_IDENTITY_PROOF` and publishes readiness without the `DEV_SPAWN` ownership checks (AC-19.6, AC-19.22, `SHUTDOWN_OWNED`).** The production path hard-codes `pidRunning: false`, `query: { ok: false }`, and `descriptor: null`, so it never reads or OS-queries a live descriptor and can never choose `reap_then_spawn` or refuse a foreign/unsupported live process (`ui/src/main/index.ts:150-173`). It then publishes from a matching stdout fragment alone; `readDescriptorPid()` and `assertOwnedIdentity()` are never called by production (`ui/src/main/backend-descriptor.ts:27-34`; `ui/src/main/python-manager.ts:60-66`). A fresh real-Electron probe seeded an unsupported-schema descriptor pointing at a live PID; the app opened and replaced it with schema 1 instead of refusing (`C:/Temp/av-kit/p6-gui-exec-r1-electron-identity-probe.txt`). Quit also injects a no-op `waitPid`, so it exits without proving the owned PID stopped (`ui/src/main/index.ts:187-207`). This violates the approved no-attach/refuse/reap/readiness contract and can overwrite discovery state while another backend is live. | High |
| **F2 — Shell navigation and palette actions are rendered but do nothing (AC-19.11, AC-19.17).** `AppShell` mounts `<NavRail>` without `onNavigate` (`ui/src/renderer/src/components/layout/AppShell.tsx:56-60`), while every registered palette action returns `undefined` (`ui/src/renderer/src/registry/commandRegistry.ts:18-59`). A fresh compiled-Electron probe settled on `#/`, clicked Transcript, then selected Settings in the palette; both URLs remained `#/` (`C:/Temp/av-kit/p6-gui-exec-r1-electron-nav-probe.txt`). The current E2E tests assert visibility/query entry only and therefore pass despite the broken user flow (`ui/tests/e2e/launch.test.ts:22-45`; `ui/tests/e2e/command-palette-nav.spec.ts:16-31`). | High |
| **F3 — The mounted console is a static facade; copy, log-to-file, polling/stdout, clear/filter/search/collapse, and seq/ipc integration are not wired (AC-19.12, AC-19.19).** `AppShell` mounts `<ConsolePanel />` without `lines`, `onCopy`, or `onLogToFile` (`ui/src/renderer/src/components/layout/AppShell.tsx:60`), even though the component makes both behaviors optional (`ui/src/renderer/src/components/layout/ConsolePanel.tsx:22-65`). `useBackendLogs` contains only detached key/list helpers (`ui/src/renderer/src/hooks/useBackendLogs.ts:1-22`); child stdout handles only `READY_LINE` (`ui/src/main/index.ts:163-173`); and `get-log-snapshot` always returns an empty array (`ui/src/main/ipc.ts:274-275`). A fresh Electron probe toggled `console-log-to-file` and observed zero renderer fetch calls (`C:/Temp/av-kit/p6-gui-exec-r1-electron-wiring-probe.txt`). Helper tests at `ui/tests/unit/console-actions.test.ts:25-41` and `backend-logs.test.ts:3-23` do not mount or traverse the production chain. | High |
| **F4 — The IPC file/path boundary permits an arbitrary external `.exe` and does not enforce `maxBytes` (AC-19.8, IR-6).** `open-path`/`show-item-in-folder` reject URLs, token names, and app-data files but apply no allowed-output/dialog-choice or extension rule (`ui/src/main/ipc.ts:158-178,221-237`). `read-text-file` validates `maxBytes` in Zod but never consumes it when reading (`ui/src/main/ipc.ts:247-258`). A direct runtime probe opened `C:/outside/tool.exe` with `{ok:true}` and side-effect count 1, then returned 4096 bytes for `maxBytes:1` (`C:/Temp/av-kit/p6-gui-exec-r1-ipc-runtime-probe.txt`). The existing negative test uses an `.exe` inside app-data, which is rejected by the broad app-data rule and does not cover this case (`ui/tests/unit/secret-paths.test.ts:6-36`). | High |
| **F5 — The promised UI and window persistence is not implemented (AC-19.18).** `usePersistedState()` always returns its fallback and never reads or writes a store (`ui/src/renderer/src/hooks/usePersistedState.ts:16-18`); `AppShell` keeps collapse state only in local `useState` (`ui/src/renderer/src/components/layout/AppShell.tsx:20-23,57`); and `restoreWindowBounds()` is never consumed when constructing the `BrowserWindow`, whose dimensions are hard-coded (`ui/src/main/index.ts:61-79,248-258`). The test round-trips an independent `Map` helper rather than the hook or mounted shell (`ui/tests/unit/persist-ui.test.ts:8-22`), so restart persistence can be absent while AC-19.18 stays green. | High |
| **F6 — Startup metric payloads are discarded and replaced with a constant event (AC-19.14 and the approved `STARTUP_METRIC_KEYS` chain).** IPC validates `{key,value,timestamp}` but passes only URL and authorization to its dependency (`ui/src/main/ipc.ts:206-213`). The production dependency then posts every event as `{key:'startup.python_spawn_ms', value_ms:0}` (`ui/src/main/index.ts:229-235`), and before readiness the handler fabricates `http://127.0.0.1/api/v1` rather than waiting (`ui/src/main/ipc.ts:207-210`). Thus renderer/window/data/lazy metrics and their measured values are never recorded correctly. The test asserts only GUI-nonce authorization and URL text, not the request body or readiness wait (`ui/tests/unit/startup-metrics.test.ts:4-25`). | High |
| **F7 — IR-5 has multiple false-pass suites around the broken production seams.** `live-identity`, `dev-spawn`, `shutdown-owned`, `backend-logs`, `console-actions`, `persist-ui`, and `startup-metrics` test detached helpers or injected mocks without proving `boot()`/`AppShell` uses them; `e2e-wiring` and the Playwright console/nav suites largely assert files/testids/visibility. These tests remain green under F1-F6, so the handoff's claim that AC-19.5-19.23 are complete is not supported by integration-strength assertions. Per-file grades are below. | Medium |

No Critical finding was identified. F1-F6 are independently evidenced High behavioral/contract failures and satisfy the Materiality Gate for `changes_required`; F7 is non-blocking by itself.

## Scope

The correlated target is `docs/execution/plans/2026-08-19-p6-gui-shell/`, whose approved plan and task name exactly one execution handoff: `.agent/context/handoffs/2026-08-19-p6-gui-shell-MEU-19-handoff.md`. Review scope included that handoff, the plan/task, the cited `06-gui.md` and `07-distribution.md` contracts, named-set locks, Python CLI files/tests, all `ui/src/main/`, `ui/src/renderer/`, `ui/tests/unit/`, `ui/tests/e2e/`, the retained Python regression set, and the MEU/phase/Hub SSOT fields.

The workspace has no `.git` directory, so this verdict is based on current file state and fresh isolated receipts rather than a diff. Scope remained Session 7 / MEU-19 only. No Downloader, Transcript, TTS, or Settings page implementation; PyInstaller; FastAPI-router rewrite; MCP-tool rewrite; new MEU; or Session 8-12 work was reviewed as delivered scope.

## IR-1-IR-7 Checklist

| Check | Result | Evidence |
|---|---|---|
| IR-1 — Live runtime evidence | Fail (Electron); Pass (Python CLI) | `tests/integration/test_backend_spawn.py:79-130` is a real spawned-server integration and passed 2/2 within the fresh 8-test CLI gate. The Playwright files launch real Electron, but their assertions do not require backend readiness/owned identity; fresh real-Electron probes reproduced F1-F3. |
| IR-2 — Stub behavioral compliance | N/A | This MEU owns no repository/UoW save-get stub. The skeleton routes are the explicitly approved Session 7 product state, not missing page implementations. |
| IR-3 — Error mapping completeness | N/A / retained regression pass | No FastAPI router was changed or permitted in this scope. The retained API/E2E regression passed within 298 tests; no route rewrite finding is made. |
| IR-4 — Fix generalization | Fail | The intended helpers exist, but production integration does not consume them: identity/readiness, console/log actions, persistence, and startup-metric payloads all stop at detached helper seams. `C:/Temp/av-kit/p6-gui-exec-r1-callsite-probes.txt` records the call-site census. |
| IR-5 — Test rigor audit | Fail | Python CLI, `apiFetch`, strict IPC, and copy-MCP tests are strong. Seven UI suites are weak because they false-pass the concrete F1-F6 defects; grades are below. |
| IR-6 — Boundary validation coverage | Fail | The 12-channel `.strict()` extra-key/type census is strong and passed, but AC-19.8 field behavior fails the direct `.exe`/`maxBytes` runtime probe (F4). |
| IR-7 — Deferral and AC integrity | Pass | The plan and sole handoff each contain all 23 unique AC-19 IDs (`p6-gui-exec-r1-ac-coverage.txt`). MEU-20-25 are registered/scheduled; Downloader/Transcript/TTS/Settings/Help/openExternal/PyInstaller deferrals are source-backed, not disguised skips. SSOT paths/status and Hub Next are exact. |

### IR-5 Per-File Test Ratings

| Test file | Rating | Rationale |
|---|---|---|
| `tests/unit/test_backend_cli.py` | 🟢 Strong | Exact parser values, missing/blank/unknown negatives, secret absence, atomic replace, and port sibling assertions. |
| `tests/integration/test_backend_spawn.py` | 🟢 Strong | Spawns a real server, asserts exact descriptor keys/PID/bind/port, and proves unauthenticated health plus dual-Bearer console access. |
| `ui/tests/unit/api-fetch.test.ts` | 🟢 Strong | All six 204 paths, concrete 422 envelope, `ApiError`, FormData header omission, and Authorization. |
| `ui/tests/unit/ipc-strict-census.test.ts` | 🟢 Strong | All 12 renderer-to-main channels reject extra keys and wrong types before recorded side effects. |
| `ui/tests/unit/copy-mcp-config.test.ts` | 🟢 Strong | Exact renderer-safe result, clipboard token content, app-data, and unpinned base omission. |
| `ui/tests/unit/api-base-ipc.test.ts` | 🟡 Adequate | Strong module-state port-zero/async checks, but no production descriptor PID/live-image readiness chain. |
| `ui/tests/unit/web-prefs-ipc.test.ts` | 🟡 Adequate | Exact web preferences/channel census/preload non-exposure; handler behavior lives in other tests. |
| `ui/tests/unit/ipc-channels.ts` and helpers/setup | Support | Shared expected channel set and Electron stubs; not executable suites themselves. |
| `ui/tests/unit/single-instance.test.ts` | 🟡 Adequate | Winner/loser lock behavior and loser no-spawn are direct; second-instance focus is not invoked. |
| `ui/tests/unit/live-identity.test.ts` | 🔴 Weak | Pure decision assertions are specific, but no test proves `boot()` performs the query or uses the result; F1 stays green. |
| `ui/tests/unit/dev-spawn.test.ts` | 🔴 Weak | Exact argv helper checks, but `assertOwnedIdentity()` is detached from readiness; F1 stays green. |
| `ui/tests/unit/shutdown-owned.test.ts` | 🔴 Weak | The helper receives a mocked working `waitPid`; production injects a no-op and is never exercised. |
| `ui/tests/unit/secret-paths.test.ts` | 🔴 Weak | Covers app-data secret denial and raw-key rejection, but not an external `.exe`, allowed-output provenance, or byte limits; F4 stays green. |
| `ui/tests/unit/startup-metrics.test.ts` | 🔴 Weak | Asserts GUI Bearer and URL only; request key/value body and wait-for-ready are unobserved. |
| `ui/tests/unit/backend-logs.test.ts` | 🔴 Weak | Exercises trivial detached key/list helpers, not child stdout, REST polling, dedup, or mounted state. |
| `ui/tests/unit/console-actions.test.ts` | 🔴 Weak | Calls copy/PUT helpers directly; never mounts `AppShell`/`ConsolePanel`, so missing callbacks pass. |
| `ui/tests/unit/persist-ui.test.ts` | 🔴 Weak | Round-trips a standalone `Map`; does not exercise `usePersistedState`, Electron store, AppShell, or window construction. |
| `ui/tests/unit/shell-home.test.ts` | 🟡 Adequate | Strong static lock against `DownloaderPage`/`url-input` and exact IDs, but no navigation behavior. |
| `ui/tests/unit/command-palette.test.ts` | 🟡 Adequate | Exact five-ID set and Ctrl+K event ownership; does not require any command action to navigate. |
| `ui/tests/unit/e2e-wiring.test.ts` | 🔴 Weak | File/testid existence only; no semantic reachability or action assertion. |
| `ui/tests/unit/g36-csp.test.ts` | 🟡 Adequate | CSP/navigation assertions are concrete; its internal deny scan covers only a subset, supplemented by the fresh full-scope G36 receipt. |
| `ui/tests/e2e/launch.test.ts` | 🟡 Adequate | Real Electron verifies shell home and absence of `url-input`, but nav buttons are never clicked. |
| `ui/tests/e2e/console-panel.test.ts` | 🔴 Weak | Visibility only; copy, persistence, clear/filter/search/collapse, and logging behavior are unasserted. |
| `ui/tests/e2e/command-palette-nav.spec.ts` | 🔴 Weak | Opens the palette and fills input, but never executes a command or asserts route change. |
| `ui/tests/e2e/global-setup.ts`, `global-teardown.ts`, `test-ids.ts` | Support | Build-existence check, empty teardown, and constants; they do not prove backend ownership or action wiring. |

## Adversarial Verification Checklist

| Check | Result | Evidence |
|---|---|---|
| AV-1 — Failing-then-passing proof | Pass as recorded lifecycle evidence | The MEU handoff records Python and UI Red oracles before Green at `.agent/context/handoffs/2026-08-19-p6-gui-shell-MEU-19-handoff.md:67-74`. This review did not treat those implementer receipts as current functional proof; it reran fresh Green gates and independent probes. |
| AV-2 — No bypass hacks | Pass on prohibited syntax; integration false-passes remain | No skip/only/todo or assertion-mocking bypass was found. Detached helper/static-presence tests are captured as F7 rather than misclassified as G36. |
| AV-3 — Changed paths asserted | Fail | The production `boot()` identity/readiness chain and mounted shell action/persistence chains are not asserted; F1-F3/F5/F6. |
| AV-4 — No skipped/xfail masking | Pass | `C:/Temp/av-kit/p6-gui-exec-r1-g36.txt` reports `PASS: G36 clean`; the assembled deny strings in `g36-csp.test.ts` were not treated as violations. |
| AV-5 — No unresolved placeholders | Pass | `C:/Temp/av-kit/p6-gui-exec-r1-anti-placeholder.txt` reports `PASS: anti-placeholder clean`. |
| AV-6 — Source-backed criteria | Pass | Every finding cites an approved AC/named-set/spec contract; no new product behavior or later-MEU requirement was introduced. |

## Documentation Review Checklist

| Check | Result | Evidence |
|---|---|---|
| DR-1 — Claim-to-state match | Fail | The handoff marks AC-19.5-19.23 complete, but F1-F6 contradict those behavior claims. |
| DR-2 — Residual old terms/scope leak | Pass | `SHELL_HOME` is present; no `DownloaderPage`, `url-input`, or later page implementation was found in delivered source. |
| DR-3 — Downstream references | Pass | MEU-19 is `ready_for_review` with the no-slash plan path; phase 6 carries the slash path; Hub Next is exact. |
| DR-4 — Verification robustness | Fail | Helper/static/visibility checks do not catch the integrated defects; F7. |
| DR-5 — Evidence auditability | Pass | This round used isolated exact receipts and current-file line references; the workspace absence of Git is stated. |
| DR-6 — Cross-reference integrity | Pass | MEU-20-25 deferrals and Session 8-12 schedule are present and consistent with the approved plan. |
| DR-7 — Evidence freshness | Pass | Fresh reruns reproduce 23 Vitest tests, 8 CLI tests, and 298 retained Python tests. |
| DR-8 — Completion vs residual risk | Fail | The handoff concludes all ACs are complete despite the integrated behavior gaps. |

## Contract Surfaces Confirmed

- Python CLI: required/blank/unknown flag behavior, `127.0.0.1`, exact descriptor keys, `os.replace`, nonzero bound port, ready line, secret omission, unauthenticated health, and both bearer tokens pass real spawned-server tests.
- IPC schemas: all 12 renderer-to-main channels are strict and the extra-key/wrong-type census blocks recorded dialog/FS/clipboard/spawn side effects.
- `apiFetch`: every locked 204 row returns `undefined`; 422 produces `ApiError`; FormData omits JSON content-type; GUI Bearer is attached; no `sendSync` or port-zero publication is present.
- Copy MCP: renderer receives `{ok:true}` only; clipboard includes `AVKIT_API_TOKEN` and `AVKIT_APP_DATA`; `AVKIT_API_BASE` is omitted unless pinned.
- Shell scope: `/` is `ShellHome`/`ModuleSkeleton` with “Connecting to backend…”; no Downloader page or `url-input`; palette IDs are exactly the five approved nav IDs; no `download:add`.
- G36/CSP/scope: full deny scan is clean, assembled deny tokens are legitimate, CSP image sources and navigation denial are present, placeholder scan is clean, and no Session 8-12 page/package work was added.
- SSOT/IR-7: MEU-19 and phase/Hub paths are exact; all AC-19.1-19.23 IDs appear in the sole handoff; later GUI/distribution MEUs are registered.

## Commands Executed

All commands used PowerShell all-stream redirects and fresh `C:/Temp/av-kit/p6-gui-exec-r1-*` receipts.

| Command / probe | Exit | Receipt / result |
|---|---:|---|
| UI `npx tsc --noEmit` + `npx vitest run --allowOnly=false` + `npx eslint src/ tests/ --max-warnings 0` + `npm run build` | 0 | `p6-gui-exec-r1-ui-gates.txt`; 18 files / 23 tests passed; type/lint/build clean |
| Python CLI registered gate | 0 | `p6-gui-exec-r1-python-cli.txt`; 8 passed |
| H1-2 retained Python regression command | 0 | `p6-gui-exec-r1-python-regression.txt`; 298 passed, 1 deprecation warning |
| `uv run pyright packages/api` + `uv run ruff check packages/api` | 0 | `p6-gui-exec-r1-python-quality.txt`; 0 errors/warnings; lint clean |
| OpenAPI `--check` | 0 | `p6-gui-exec-r1-openapi.txt`; exact empty output, exit 0 |
| Identity/readiness + shell/path/metric call-site census | 0 | `p6-gui-exec-r1-callsite-probes.txt`; detached/unused production seams shown |
| Direct IPC `.exe` + `maxBytes` runtime probe | 0 (finding reproduced) | `p6-gui-exec-r1-ipc-runtime-probe.txt`; `.exe` `ok:true`, opened 1; 4096 bytes returned for limit 1 |
| Real Electron nav + palette probe | 0 (finding reproduced) | `p6-gui-exec-r1-electron-nav-probe.txt`; both route-change booleans false |
| Real Electron log-to-file wiring probe | 0 (finding reproduced) | `p6-gui-exec-r1-electron-wiring-probe.txt`; fetch calls 0 |
| Real Electron unsupported-live-descriptor probe | 0 (finding reproduced) | `p6-gui-exec-r1-electron-identity-probe.txt`; live schema 999 descriptor overwritten with schema 1 |
| SSOT/phase/Hub oracle | 0 | `p6-gui-exec-r1-ssot.txt`; exact status and paths pass |
| Plan-to-handoff AC coverage oracle | 0 | `p6-gui-exec-r1-ac-coverage.txt`; 23/23, missing 0 |
| Full-scope G36 scan | 0 wrapper / raw zero matches | `p6-gui-exec-r1-g36.txt`; clean |
| Anti-placeholder scan | 0 wrapper / raw zero matches | `p6-gui-exec-r1-anti-placeholder.txt`; clean |
| Canonical review path pre-edit guard | 0 | `p6-gui-exec-r1-pre-edit-guard.txt`; exact target matched and was absent |
| `uv run python tools/check_exec_review.py --self-test` | 0 | `p6-gui-exec-r1-review-self-test.txt`; checker self-test passed |
| Review frontmatter/marker/rolling-file oracle | 0 | `p6-gui-exec-r1-review-structure.txt`; exact six keys, Intent Anchor first, IR-1-IR-7 present, one rolling file |
| Completion-preflight canonical task read/gate | 0 | `p6-gui-exec-r1-completion-preflight.txt`; H1-7 and H2-1-H2-5 remain gated by this `changes_required` verdict |

The implementer's `C:/Temp/av-kit/e2e-wave0.txt` reports 8 passed and is consistent with the E2E files present, but it is not used as this round's proof of action correctness; the fresh targeted Electron probes above exercise the missing semantics.

## Open Questions and Assumptions

- No human/product decision is required to interpret F1-F7; each is measured against an explicit approved-plan contract.
- No live YouTube, Hugging Face, or Kokoro call was made, as required. The Python backend and local Electron bundle were exercised only against local temp app-data.
- Current-file verification cannot establish historical authorship because the workspace is not a Git repository; it establishes the present delivered behavior.
- H1-7 and H2 remain unchecked by design. A `changes_required` reviewer does not mark the independent-review row approved, update SSOT to approved, or start Session 8.

## Required Follow-up

1. Route corrections through `/execution-corrections`; do not patch during review.
2. Wire descriptor parsing, live OS query, refuse/reap behavior, normalized PID/image readiness, and a real quit wait into `boot()`, with an integration test that seeds live foreign/unsupported and owned-orphan descriptors.
3. Wire nav and palette commands to hash routing; mount console copy/settings/poll/stdout/clear/filter/search/collapse behavior; implement actual UI/window persistence; and test each through the compiled Electron surface.
4. Enforce allowed output/dialog provenance and extension rules for open/show paths, honor `maxBytes` during reads, and add the external `.exe` plus over-limit negative cases.
5. Forward validated startup key/value data after backend readiness and assert the exact API body/GUI Bearer.
6. Append round 2 to this same rolling review file after corrections; rerun the failing probes and all registered gates.

## Verdict

`changes_required` — F1-F6 are independently reproduced High behavioral/contract failures. Green type/lint/build, 23 Vitest, 8 CLI, 298 regression, OpenAPI, SSOT, AC-census, G36, and placeholder receipts do not override the demonstrated false-passes.

This workflow stops here. It does not authorize `/execution-corrections`, Session 8, product/test edits, SSOT changes, or H2 closeout.

## Residual Risk

Until corrected, Electron can spawn over a live/refused descriptor, expose an API base without proving child ownership, leave its core shell controls nonfunctional, permit path/size boundary violations, and lose all UI/window state across restart. The Python CLI itself has strong local evidence; no conclusion is drawn about prohibited live external media/model behavior.

---

## Corrections Applied (2026-08-20) — implementer, not a verdict

`verdict: corrections_applied` (implementer). Independent Codex must rewrite the first frontmatter. Findings resolved: 7/7 claimed; not approved.

| Finding | Change | Test / receipt |
|---|---|---|
| F1 | `boot()` now `resolveBootIdentity` (reads descriptor + live query), reaps then waits, and `confirmReadyAndPublish` requires `assertOwnedIdentity`. Quit uses `waitPidExit`. | `live-identity.test.ts` unsupported-schema refuse; `dev-spawn.test.ts` withheld publish; `shutdown-owned.test.ts` `waitPidExit` |
| F2 | `NavRail` `onNavigate={navigateShell}`; palette actions set hash / collapse event. | `app-shell-wiring.test.ts`; Playwright `#/transcript` and `#/settings` |
| F3 | `AppShell` mounts console with copy / log-to-file / clear; `useBackendLogs` snapshots + stdout + 500 ms poll; `get-log-snapshot` returns buffer. | `app-shell-wiring.test.ts` clipboard + `PUT /settings/app` |
| F4 | Deny `.exe` (and sibling binaries) outside app-data; `read-text-file` slices to `maxBytes`. | `secret-paths.test.ts` `C:/outside/tool.exe` + `maxBytes:1` → `A` |
| F5 | `usePersistedState` writes localStorage; `createWindowOptions` + electron-store restore/save bounds. | `persist-ui.test.ts` |
| F6 | `startup-metric` waits for ready; posts `{key, value_ms}` of the validated payload. | `startup-metrics.test.ts` exact URL + key/value |
| F7 | Added production-path tests above so F1–F6 cannot stay green if unwired. | Vitest 29; Playwright 10 |

Gates after correction: `C:/Temp/av-kit/ui-green-exec-r1.txt` (tsc/eslint/build + 29 passed); `C:/Temp/av-kit/e2e-exec-r1-corrections.txt` (10 passed); `C:/Temp/av-kit/pytest-backend-cli-r1.txt` (8 passed).

Do not treat this section as `approved`.
