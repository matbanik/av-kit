---
date: "2026-08-20"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-19-p6-gui-shell/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
round: 3
review_round: 3
---

# Critical Review: p6-gui-shell

> **Review Mode**: `plan`
> **Verdict**: `changes_required`

---

## Scope

**Targets**: `docs/execution/plans/2026-08-19-p6-gui-shell/implementation-plan.md`; `docs/execution/plans/2026-08-19-p6-gui-shell/task.md`  
**Authority**: `06-gui.md`; live identity / CLI portions of `07-distribution.md`; `gui-actions-index.md`; grouping Session 7; MEU registry MEU-19; requested GUI emerging standards; p4/p5 carry-forward plans  
**Review Type**: unstarted risk-path plan review  
**Checklist Applied**: IR, DR-1–DR-8, PR-1–PR-9

## Intent Anchor

Executing this plan is supposed to deliver MEU-19 only: a secure Electron shell that owns a live-identity-verified Python backend, exposes strict allowlisted IPC, authenticates REST through `apiFetch`, and renders the shared AppShell/console without implementing later pages or packaging. As written, the plan cannot produce a valid Red phase and can pass while omitting material IPC, process-lifecycle, and console behavior.

---

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **The required Red phase is not runnable and Python production is sequenced before its tests.** Row 1 adds the CLI; row 2, which depends on row 1, claims to write AC-19.1–19.20 tests first but invokes Vitest inside `ui/`; row 3 creates the `ui/` package/config only afterward. Current state proves `ui/` and both CLI test files are absent (`C:/Temp/av-kit/p6-path-existence.txt`). The run therefore fails on the missing harness/config or occurs after CLI implementation, not on the intended behavioral oracle. This violates the mandatory tests-first/FAIL_TO_PASS contract and PR-4/PR-8. | `task.md:42-44`; `implementation-plan.md:58-60` | Schedule a behavior-free UI test-harness scaffold before Red; write and run the Python CLI tests and UI tests before their production code; require each receipt to fail on the intended missing behavior/assertion. | open |
| 2 | High | High | **IPC payload validation has no concrete strict schema owner or negative oracle.** The boundary inventory names “main handlers” rather than per-channel Zod schemas and says extra keys are ignored after “fail-closed,” while AC-19.7 proves only the channel registry and AC-19.8 proves selected path denial. The plan can pass with permissive or ill-typed payloads for startup metrics, file-dialog filters, clipboard writes, `maxBytes`, and MCP-copy options. That violates the mandatory Boundary Input Contract and PR-8 on this security boundary. | `implementation-plan.md:205-212`; `implementation-plan.md:224-226` | Define named `.strict()` schemas (or explicit no-payload validators) for every renderer-to-main channel, including type/range/size constraints, and add a parametrized oracle proving unknown/invalid payloads cause no side effect. | open |
| 3 | High | Medium-High | **The unpackaged owned-process identity is not total.** `DEV_BACKEND_BIN` is a command vector (`uv run python -m avkit_api`), while `OURS_EXE` is described as the resolved Python image; the plan never defines how Electron resolves and spawns that exact image or which PID is the owned child. Yet the authority requires `backend.json.pid` to equal the child just spawned, and live identity depends on an exact image/cmdline match. AC-19.2 tests the CLI descriptor, but no PythonManager oracle binds the descriptor PID/image to the actual dev child. This leaves the risk-path call chain ambiguous and able to accept a descriptor not proven to belong to its child. | `implementation-plan.md:92-93`; `implementation-plan.md:219-223`; `implementation-plan.md:230` | Define one dev spawn identity end to end (for example, resolve and directly spawn the environment Python), name the owned PID/image source, and test descriptor-PID mismatch and image mismatch before readiness is accepted. | open |
| 4 | High | High | **Owned-child shutdown and descriptor retirement are absent from the contract.** Canon requires Electron to terminate only its owned child on quit and delete/tombstone `backend.json` so MCP cannot target a dead port. The plan covers startup spawn/reap/refuse only; no AC observes owned-child exit, descriptor cleanup, or the negative case that a refused foreign PID survives quit. The gate can therefore pass with a stale discovery file or unsafe shutdown ownership. | `implementation-plan.md:110-112`; `implementation-plan.md:222-223`; authority `07-distribution.md:124,189-191` | Add a named shutdown control and integration/unit oracles for owned-child termination, descriptor/port-sibling retirement, foreign/refused PID survival, and backend lifespan completion. | open |
| 5 | High | High | **The planned ConsolePanel omits required shell-console actions.** Canon requires Copy-to-clipboard and log-to-file behavior, and the action index specifically requires `console:copy` through `writeClipboardText`. The plan exposes the IPC channel but has no `console:copy` producer/testid/feedback/E2E assertion and never mentions `app.log_to_file`; AC-19.19 covers polling, redaction, levels, and yt-dlp filtering only. The plan can pass with a materially incomplete MEU-19 console. | `implementation-plan.md:186-197`; `implementation-plan.md:236`; authority `06-gui.md:321-325,336,1224`; `gui-actions-index.md:67` | Add the missing console action/setting observables and E2E assertions (including action-index/testid/feedback mapping), or cite a real scheduled MEU basis for each deferral; MEU-19’s grouping currently owns the console. | open |
| 6 | Low | High | `task.md` frontmatter says `in_progress` although every task row is unchecked and all correlated implementation artifacts/handoffs are absent. This is clerical and does not defeat the independently verified not-started state. | `task.md:5`; `task.md:42-64` | Set the task frontmatter to the project’s not-started planning status. | open |
| 7 | Low | High | **PR-9 marker literals are re-spelled after being named.** `HANDOFF_BUNDLE_MARKERS` is defined once, but the marker sequence is repeated in multiple task validations, creating a stale-clause cluster. | `implementation-plan.md:148`; `task.md:46,55,63` | Make one executable owner for the marker set and reference it from the task rows; retain only deliberately narrower checks with an explicit name. | open |

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-19.1–19.20 each has a Spec, Local Canon/grouping, Research-backed, or emerging-standard source. |
| Validation cells are exact and runnable | fail | Commands are concrete, but the Red command is not runnable against the current absent `ui/` before row 3 (Finding 1). |
| BUILD_PLAN audit row present | pass | Plan lines 294–300 and task row 6 bind MEU-19 and the hub next step. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows are present. |

### Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | `ui/`, CLI files/tests, and correlated handoffs are absent; coding has not begun. |
| DR-2 Residual old terms | pass | p4/p5 deferral conflicts are disclosed and resolved against grouping/registry. |
| DR-3 Downstream references | pass | MEU-20–25 and next-plan references resolve to registered entries. |
| DR-4 Verification robustness | fail | Findings 1–5 identify behavioral failures or omissions that the gates do not catch. |
| DR-5 Evidence auditability | pass | Exact receipt commands and named paths are supplied; no project tests/scripts were run during review. |
| DR-6 Cross-reference integrity | fail | Dev identity, shutdown, and ConsolePanel coverage do not fully implement the cited 06/07/action-index contracts. |
| DR-7 Evidence freshness | pass | Current `Test-Path` and `rg` receipts were captured in round 1. |
| DR-8 Completion vs residual risk | pass | The artifacts remain draft/unstarted and make no implementation-complete claim. |

### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | fail | The plan and task share scope, but task rows 1–3 contradict the promised tests-first order (Finding 1). |
| PR-2 Not-started confirmation | pass | All rows are unchecked; `ui/`, CLI files/tests, and correlated implementation handoffs are absent. |
| PR-3 Task contract completeness | pass | Each actionable row has owner, deliverable, validation, dependencies/status, and durable outputs. |
| PR-4 Validation realism | fail | Red cannot reach the intended behavioral failure; lifecycle/console controls can false-pass. |
| PR-5 Source-backed planning | pass | Non-spec locks are labeled; no unsourced page or PyInstaller scope was added. |
| PR-6 Handoff/corrections readiness | pass | One MEU handoff and one rolling implementation-review path are explicit; this is round 1. |
| PR-7 Scope discipline | fail | MEU-20–25 deferrals are registered, but required MEU-19 console work is silently omitted rather than validly deferred (Finding 5). |
| PR-8 Control reachability/totality | fail | IPC validation, dev child identity, shutdown ownership, and console actions lack complete production chains and negative oracles (Findings 2–5). |
| PR-9 Single-statement discipline | fail | Repeated handoff-marker literals remain (Finding 7; non-blocking). |

---

## Commands Executed

- Read-only `Get-Content` receipts for the workflow, template, targets, authority files, roles, and harness/project context under `C:/Temp/av-kit/`.
- `C:/Temp/av-kit/p6-path-existence.txt` — current artifact existence / not-started proof.
- `C:/Temp/av-kit/p6-meu-census.txt` — MEU-19–25 registration and grouping proof.
- `C:/Temp/av-kit/console-contract-census.txt` — ConsolePanel/action omissions.
- `C:/Temp/av-kit/live-identity-census.txt` — live-identity and shutdown-contract comparison.
- `C:/Temp/av-kit/ipc-boundary-census.txt` — IPC schema/strictness comparison.
- `C:/Temp/av-kit/p6-review-pre-edit-guard.txt` — canonical write-target guard.

No project tests or `tools/` scripts were run because the plan is unapproved.

## Open Questions / Assumptions

- The dev-process finding concerns an unspecified ownership contract; no assumption is made that a particular local `uv` implementation was executed during this review.
- Session 7 and MEU-19 assign the shared ConsolePanel to this plan. Downloader, Transcript, TTS, Settings/Help pages, the full cross-page action audit, PyInstaller, and NSIS remain correctly deferred.

## Required Follow-Up

Use `/plan-corrections` to resolve Findings 1–5 and disposition the two Low notes. The correction pass should include an untruncated blast-radius census with a per-hit disposition, as required for round 2.

---

## Verdict

`changes_required` — five High findings demonstrate impossible Red sequencing and materially incomplete risk-path/user-visible controls. The plan should not enter execution until a corrected round passes independent review.

## Residual Risk

Even after documentary correction, Electron process identity and shutdown must be proven on real Windows process behavior, and Playwright may still require the evidence-gated no-display fallback. Those execution risks do not justify weakening the tests or IPC/lifecycle contract.

---

## Corrections Applied (2026-08-20)

**Workflow**: `/plan-corrections` inside `/create-plan` §5b (parent loop wins over `plan-corrections.md` HARD STOP). Plan/task only — no product code.
**Agent**: coordinator (implementer) — `corrections_applied`, never `approved`.
**Conflict flagged**: `plan-corrections.md` Step 7 / HARD STOP say timestamp-and-stop and do not chain into re-review; `create-plan.md` §5b requires blast-radius census then re-dispatch. Parent create-plan loop is followed.

Round-1 findings 1–7 addressed. F1–F7 are `fixed` (none refuted).

| # | Sev | Status | Fix |
|---|-----|--------|-----|
| 1 | High | fixed | WP-19a harness-only → WP-19b Red AC-19.1–19.23 (Python + UI FAIL_TO_PASS receipts; exit 0 is a Red failure) → WP-19c Green CLI + `ui/src`. Task rows 1–3 match. |
| 2 | High | fixed | `IPC_SCHEMAS` / `IPC_NO_PAYLOAD` / `IPC_PAYLOAD_SHAPES` / `IPC_STRICT_CENSUS`; AC-19.21 extra-key/type oracle; boundary extra-field policy is `.strict()`. |
| 3 | High | fixed | `PYTHON_IMAGE` + `DEV_SPAWN`; never own `uv.exe`; AC-19.22 pid/image mismatch oracle. |
| 4 | High | fixed | `SHUTDOWN_OWNED`; AC-19.23 foreign-pid / leftover-descriptor oracle. |
| 5 | High | fixed | `CONSOLE_SHELL_ACTIONS` + `WAVE5_TESTIDS` include `console-copy` / `console-log-to-file`; AC-19.19 is a control. |
| 6 | Low | fixed | `task.md` frontmatter `status: "draft"`. |
| 7 | Low | fixed | `HANDOFF_MARKER_CHECK` → `assert-handoff-markers.ps1` is the sole executable owner. Task rows 5 / H1-6 / H2-4 call the script; they do not restate the marker list. `HANDOFF_BUNDLE_MARKERS` remains the named definition only. |

This-session leftover F7 / sweep edits (after the first correction pass): `task.md:46` Task cell now names `HANDOFF_MARKER_CHECK`; `implementation-plan.md:161` `MEU_SCOPED_GATE` uses `HANDOFF_MARKER_CHECK`; `implementation-plan.md:61` WP-19d names `console-log-to-file`; `implementation-plan.md:287` unit-test AC range is `19.17–19.23`.

### Declared variants swept

Old literals: `DEV_BACKEND_BIN`, `AC-19.1–19.20`, `AC-19.1-19.20`, `fail-to-pass-meu-19.txt`, `in_progress`, `uv run python -m avkit_api`, restated marker `foreach`, `19.17–19.20`, `AC-19.1-19.23`.
New / semantic: `DEV_SPAWN`, `PYTHON_IMAGE`, `SHUTDOWN_OWNED`, `owned.pid`, `uv.exe`, `IPC_SCHEMAS`, `IPC_NO_PAYLOAD`, `IPC_PAYLOAD_SHAPES`, `IPC_STRICT_CENSUS`, `CONSOLE_SHELL_ACTIONS`, `console-copy`, `console:copy`, `console-log-to-file`, `log_to_file`, `HANDOFF_MARKER_CHECK`, `HANDOFF_BUNDLE_MARKERS`, `assert-handoff-markers.ps1`, `AC-19.21`/`22`/`23`, `AC-19.1–19.23`, `19.17–19.23`, `fail-to-pass-meu-19-py.txt`, `fail-to-pass-meu-19-ui.txt`, `status: "draft"`, `ignore extra keys`.

Manifests: `C:/Temp/av-kit/census-p6-manifest.txt`, `C:/Temp/av-kit/census-p6-variants-manifest.txt`, `C:/Temp/av-kit/census-p6-ac-range-manifest.txt`. Runner: `C:/Temp/av-kit/census-p6-run.txt`. `assert-handoff-markers.ps1` exists (`script_exists=True`).

Blast-radius census: 27 primary values + 8 variants + 2 AC-range values = 37 sweeps. Zero-hit old receipts: 9. Nonzero raw `file:line` hits: 82 (1 leftover-old + 81 new/variant). Each hit is dispositioned below. No truncated `Select-Object -First` / `head`.

### Zero-hit old receipts (stale gone)

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `C:/Temp/av-kit/census-p6-dev-backend-bin-old.txt` | 0 | no stale `DEV_BACKEND_BIN` |
| `C:/Temp/av-kit/census-p6-ac-19-1-20-endash-old.txt` | 0 | no stale `AC-19.1–19.20` |
| `C:/Temp/av-kit/census-p6-ac-19-1-20-hyphen-old.txt` | 0 | no stale `AC-19.1-19.20` |
| `C:/Temp/av-kit/census-p6-fail-to-pass-single-old.txt` | 0 | no stale `fail-to-pass-meu-19.txt` |
| `C:/Temp/av-kit/census-p6-in-progress-old.txt` | 0 | no stale `in_progress` |
| `C:/Temp/av-kit/census-p6-uv-run-owned-old.txt` | 0 | no owned-child `uv run python -m avkit_api` |
| `C:/Temp/av-kit/census-p6-marker-foreach-old.txt` | 0 | no restated marker `foreach` |
| `C:/Temp/av-kit/census-p6-ac-19-1-23-hyphen-new.txt` | 0 | hyphen range unused (endash form is canonical) |
| `C:/Temp/av-kit/census-p6-ac-range-17-20-old.txt` | 0 | no stale `19.17–19.20` |

### Per-hit disposition — leftover-old (`ignore extra keys`)

Receipt: `C:/Temp/av-kit/census-p6-ignore-extra-keys-old.txt` (1 hit)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:250` | confirmed-consistent — AC-19.21 **Negative Test** column (the forbidden pass); not an extra-field policy |

### Per-hit disposition — `DEV_SPAWN`

Receipt: `C:/Temp/av-kit/census-p6-dev-spawn-new.txt` (6)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:44` | confirmed-consistent — Green row names `DEV_SPAWN` |
| 2 | `implementation-plan.md:60` | confirmed-consistent — WP-19c |
| 3 | `implementation-plan.md:99` | confirmed-consistent — named-set definition |
| 4 | `implementation-plan.md:251` | confirmed-consistent — AC-19.22 |
| 5 | `implementation-plan.md:260` | confirmed-consistent — sufficiency |
| 6 | `implementation-plan.md:367` | confirmed-consistent — open-question lock |

### Per-hit disposition — `PYTHON_IMAGE`

Receipt: `C:/Temp/av-kit/census-p6-python-image-new.txt` (6)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:98` | confirmed-consistent — named-set definition |
| 2 | `implementation-plan.md:99` | confirmed-consistent — `DEV_SPAWN` uses it |
| 3 | `implementation-plan.md:101` | confirmed-consistent — `OURS_EXE` |
| 4 | `implementation-plan.md:251` | confirmed-consistent — AC-19.22 |
| 5 | `implementation-plan.md:260` | confirmed-consistent — sufficiency |
| 6 | `implementation-plan.md:367` | confirmed-consistent — open-question lock |

### Per-hit disposition — `SHUTDOWN_OWNED`

Receipt: `C:/Temp/av-kit/census-p6-shutdown-owned-new.txt` (5)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:60` | confirmed-consistent — WP-19c |
| 2 | `implementation-plan.md:95` | confirmed-consistent — named-set definition |
| 3 | `implementation-plan.md:252` | confirmed-consistent — AC-19.23 |
| 4 | `implementation-plan.md:264` | confirmed-consistent — sufficiency |
| 5 | `task.md:44` | confirmed-consistent — Green row |

### Per-hit disposition — `IPC_SCHEMAS`

Receipt: `C:/Temp/av-kit/census-p6-ipc-schemas-new.txt` (7)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:44` | confirmed-consistent — Green row |
| 2 | `implementation-plan.md:60` | confirmed-consistent — WP-19c |
| 3 | `implementation-plan.md:89` | confirmed-consistent — named-set definition |
| 4 | `implementation-plan.md:221` | confirmed-consistent — boundary inventory |
| 5 | `implementation-plan.md:236` | confirmed-consistent — AC-19.7 |
| 6 | `implementation-plan.md:237` | confirmed-consistent — AC-19.8 after schemas |
| 7 | `implementation-plan.md:250` | confirmed-consistent — AC-19.21 |

### Per-hit disposition — `IPC_STRICT_CENSUS`

Receipt: `C:/Temp/av-kit/census-p6-ipc-strict-census-new.txt` (3)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:92` | confirmed-consistent — named-set definition |
| 2 | `implementation-plan.md:221` | confirmed-consistent — boundary inventory |
| 3 | `implementation-plan.md:250` | confirmed-consistent — AC-19.21 |

### Per-hit disposition — `CONSOLE_SHELL_ACTIONS`

Receipt: `C:/Temp/av-kit/census-p6-console-shell-actions-new.txt` (4)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:44` | confirmed-consistent — Green row |
| 2 | `implementation-plan.md:135` | confirmed-consistent — named-set definition |
| 3 | `implementation-plan.md:248` | confirmed-consistent — AC-19.19 |
| 4 | `implementation-plan.md:263` | confirmed-consistent — sufficiency |

### Per-hit disposition — `HANDOFF_MARKER_CHECK`

Receipt: `C:/Temp/av-kit/census-p6-handoff-marker-check-new.txt` (7)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:46` | updated — Task cell + validation call the script / name (F7 leftover) |
| 2 | `task.md:55` | confirmed-consistent — H1-6 validation is the script only |
| 3 | `task.md:63` | confirmed-consistent — H2-4 starts with the script |
| 4 | `implementation-plan.md:158` | confirmed-consistent — named-set definition |
| 5 | `implementation-plan.md:161` | updated — `MEU_SCOPED_GATE` now names `HANDOFF_MARKER_CHECK` |
| 6 | `implementation-plan.md:290` | confirmed-consistent — Files Modified |
| 7 | `implementation-plan.md:340` | confirmed-consistent — Verification §4 heading |

### Per-hit disposition — `HANDOFF_BUNDLE_MARKERS`

Receipt: `C:/Temp/av-kit/census-p6-handoff-bundle-markers-new.txt` (2)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:157` | confirmed-consistent — single named definition of the marker list |
| 2 | `implementation-plan.md:158` | confirmed-consistent — owner sentence (not a restated task validation) |

### Per-hit disposition — `console-copy`

Receipt: `C:/Temp/av-kit/census-p6-console-copy-new.txt` (4)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:45` | confirmed-consistent — E2E row + testid assert |
| 2 | `implementation-plan.md:61` | updated — WP-19d also names `console-log-to-file` |
| 3 | `implementation-plan.md:136` | confirmed-consistent — `WAVE5_TESTIDS` |
| 4 | `implementation-plan.md:204` | confirmed-consistent — §4A table |

### Per-hit disposition — `console-log-to-file`

Receipt: `C:/Temp/av-kit/census-p6-console-log-to-file-new.txt` (5)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:45` | confirmed-consistent — E2E row + testid assert |
| 2 | `implementation-plan.md:61` | updated — WP-19d |
| 3 | `implementation-plan.md:136` | confirmed-consistent — `WAVE5_TESTIDS` |
| 4 | `implementation-plan.md:207` | confirmed-consistent — §4A table |
| 5 | `implementation-plan.md:248` | confirmed-consistent — AC-19.19 |

### Per-hit disposition — new ACs / Red receipts / draft / IPC shapes

| Receipt | # | file:line | Disposition |
|---------|---|-----------|-------------|
| `census-p6-ac-19-21-new.txt` | 1 | `implementation-plan.md:250` | confirmed-consistent — AC-19.21 row |
| `census-p6-ac-19-22-new.txt` | 1 | `implementation-plan.md:251` | confirmed-consistent — AC-19.22 row |
| `census-p6-ac-19-23-new.txt` | 1 | `implementation-plan.md:252` | confirmed-consistent — AC-19.23 row |
| `census-p6-fail-to-pass-py-new.txt` | 1 | `task.md:43` | confirmed-consistent — Red Python receipt |
| `census-p6-fail-to-pass-py-new.txt` | 2 | `implementation-plan.md:59` | confirmed-consistent — WP-19b |
| `census-p6-fail-to-pass-ui-new.txt` | 1 | `task.md:43` | confirmed-consistent — Red UI receipt |
| `census-p6-fail-to-pass-ui-new.txt` | 2 | `implementation-plan.md:59` | confirmed-consistent — WP-19b |
| `census-p6-status-draft-new.txt` | 1 | `implementation-plan.md:6` | confirmed-consistent — plan draft |
| `census-p6-status-draft-new.txt` | 2 | `task.md:5` | confirmed-consistent — F6 draft (not `in_progress`) |
| `census-p6-ipc-no-payload-new.txt` | 1 | `implementation-plan.md:90` | confirmed-consistent — named-set definition |
| `census-p6-ipc-no-payload-new.txt` | 2 | `implementation-plan.md:221` | confirmed-consistent — boundary inventory |
| `census-p6-ipc-payload-shapes-new.txt` | 1 | `implementation-plan.md:91` | confirmed-consistent — named-set definition |
| `census-p6-ipc-payload-shapes-new.txt` | 2 | `implementation-plan.md:221` | confirmed-consistent — boundary inventory |
| `census-p6-ac-range-17-23-new.txt` | 1 | `implementation-plan.md:287` | updated — unit-test AC range includes 19.21–19.23 |

### Per-hit disposition — `assert-handoff-markers.ps1`

Receipt: `C:/Temp/av-kit/census-p6-assert-handoff-markers-new.txt` (6)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:46` | updated — row 5 validation invokes the script |
| 2 | `task.md:55` | confirmed-consistent — H1-6 |
| 3 | `task.md:63` | confirmed-consistent — H2-4 |
| 4 | `implementation-plan.md:158` | confirmed-consistent — named-set command |
| 5 | `implementation-plan.md:290` | confirmed-consistent — Files Modified |
| 6 | `implementation-plan.md:343` | confirmed-consistent — Verification §4 command |

### Per-hit disposition — variants

| Receipt | # | file:line | Disposition |
|---------|---|-----------|-------------|
| `census-p6-console-colon-copy-var.txt` | 1 | `implementation-plan.md:135` | confirmed-consistent — action id in `CONSOLE_SHELL_ACTIONS` |
| `census-p6-console-colon-copy-var.txt` | 2 | `implementation-plan.md:248` | confirmed-consistent — AC-19.19 + negative column |
| `census-p6-log-to-file-leaf-var.txt` | 1 | `implementation-plan.md:135` | confirmed-consistent — `app.log_to_file` / leaf |
| `census-p6-log-to-file-leaf-var.txt` | 2 | `implementation-plan.md:207` | confirmed-consistent — §4A |
| `census-p6-log-to-file-leaf-var.txt` | 3 | `implementation-plan.md:248` | confirmed-consistent — AC-19.19 PUT body |
| `census-p6-ac-19-1-23-range-new.txt` | 1 | `task.md:43` | confirmed-consistent — Red row AC range |
| `census-p6-ac-19-1-23-range-new.txt` | 2 | `implementation-plan.md:59` | confirmed-consistent — WP-19b AC range |
| `census-p6-owned-pid-var.txt` | 1 | `implementation-plan.md:95` | confirmed-consistent — `SHUTDOWN_OWNED` |
| `census-p6-owned-pid-var.txt` | 2 | `implementation-plan.md:99` | confirmed-consistent — `DEV_SPAWN` |
| `census-p6-owned-pid-var.txt` | 3 | `implementation-plan.md:251` | confirmed-consistent — AC-19.22 |
| `census-p6-owned-pid-var.txt` | 4 | `implementation-plan.md:252` | confirmed-consistent — AC-19.23 |
| `census-p6-uv-wrapper-pid-var.txt` | 1 | `implementation-plan.md:251` | confirmed-consistent — AC-19.22 forbids owning `uv.exe` |

Ready for independent Round 2. Reviewer must write **new first frontmatter** `round: 2` / `review_round: 2` and adjudicate F1–F7 plus PR-6 census completeness. Do not treat this `corrections_applied` as `approved`.

---

## Recheck (2026-08-20) — Round 2

**Workflow**: `/plan-critical-review` recheck after `/plan-corrections`  
**Agent**: `gpt-5.6-sol`  
**Checklist Applied**: IR, DR-1–DR-8, PR-1–PR-9

### Intent Anchor

Executing this plan is supposed to deliver MEU-19 only: an Electron shell that owns a live-identity-verified `python -m avkit_api` child, exposes strict allowlisted IPC and Bearer-authenticated `apiFetch`, and renders AppShell/console without pulling in later pages or PyInstaller. The corrected scope is aligned, but the plan still permits invalid Red evidence and stale backend discovery after an unexpected owned-child exit, so execution would not yet satisfy the objective safely.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **R1 F1 remains open: the Red gate accepts any nonzero process failure as valid FAIL_TO_PASS evidence.** Row 2 says failures must be the intended missing module/assertion, but its command checks only `code == 0`; collection errors, syntax errors, broken imports, missing dependencies, or a bad Vitest harness all take the same nonzero branch and end in `PASS: FAIL_TO_PASS red; exit 0`. This is the concrete false-pass the r1 recommendation required the correction to exclude, violating the mandatory TDD/FAIL_TO_PASS contract and PR-4/PR-8. | `task.md:43`; `implementation-plan.md:59` | Make each Red receipt prove the expected failing test/assertion and reject collection/config/dependency failures before returning success; preserve and adjudicate the Python and UI exit states separately. | still-open |
| 2 | High | High | **R1 F4 remains open: descriptor retirement is reachable only from Electron quit, not every owned-child exit.** `SHUTDOWN_OWNED` begins “on Electron quit,” and AC-19.23 traces only `app.quit` / `before-quit` to SIGTERM and cleanup. Canon separately requires deleting/tombstoning discovery “on owned-child exit.” If the owned backend crashes while Electron stays open, the planned control has no producer that retires `backend.json` / `backend-port.txt`, so MCP may target a dead port. This violates the cited lifecycle contract and PR-8 reachability/totality. | `implementation-plan.md:95,252`; `docs/build-plan/07-distribution.md:124,189-191` | Bind descriptor/port-sibling retirement to the owned child process exit event independently of the quit path, and add a negative oracle for unexpected owned-child exit leaving live discovery behind. | still-open |
| 3 | High | High | **The G36 gate can pass while `.only` silently excludes most UI tests.** `SCAN_G36_ARGS` and the task-row scan cover disabled/todo forms but omit `it.only`, `test.only`, and `describe.only`; ESLint is scoped to `src/`, not `ui/tests/unit`. The task runs Vitest locally without `CI` or `allowOnly: false`; Vitest's documented default is `allowOnly: !process.env.CI`. A single focused test can therefore skip the remaining AC suite while the Green, MEU, and H1 gates return zero. This is a demonstrated materially false-passing gate under G36 and PR-4/PR-8. | `implementation-plan.md:143,161`; `task.md:44,46,51`; `.agent/docs/emerging-standards.md:1188-1194` | Set `test.allowOnly: false` in `vitest.config.ts` (or pass `--allowOnly=false`) and make the focused-test enforcement cover the test tree, including `.only` forms. | open |
| 4 | Low | High | **The corrections appendix's census total is stale by one.** The three manifests contain 69 primary + 12 variant + 1 AC-range hit = 82, and the appendix does disposition all 82; only the prose says 81. PR-6 therefore passes, but DR-7 freshness does not. | `2026-08-19-p6-gui-shell-plan-critical-review.md` Corrections Applied; `C:/Temp/av-kit/p6-r2-pr6-disposition-compare.txt` | Change the prose total from 81 to 82 during the next correction pass; no census rerun is required if the receipts remain unchanged. | open |

### Prior Pass Adjudication

| R1 Finding | Prior Status | Recheck Result | Evidence |
|------------|--------------|----------------|----------|
| F1 — runnable tests-first Red | open | ❌ Still open | Harness ordering is fixed, but `task.md:43` accepts any nonzero failure rather than the intended missing-behavior oracle. |
| F2 — strict IPC schemas / negative oracle | open | ✅ Fixed | `IPC_SCHEMAS`, `IPC_NO_PAYLOAD`, `IPC_PAYLOAD_SHAPES`, and `IPC_STRICT_CENSUS` cover every renderer→main channel with strict rejection and zero-side-effect oracles (`implementation-plan.md:89-92,221,236-237,250`). |
| F3 — unpackaged child identity | open | ✅ Fixed | `PYTHON_IMAGE` resolves the environment interpreter; `DEV_SPAWN` directly spawns it and binds readiness to `owned.pid` plus live image (`implementation-plan.md:98-101,251`). |
| F4 — shutdown / discovery retirement | open | ❌ Still open | Quit ownership and foreign-PID survival are covered, but unexpected owned-child exit still has no cleanup chain (`implementation-plan.md:95,252`; `07-distribution.md:124`). |
| F5 — console copy / log-to-file | open | ✅ Fixed | `CONSOLE_SHELL_ACTIONS`, §4A feedback/testids, AC-19.19, and Wave 5 wiring include clipboard copy and backend `log_to_file` persistence (`implementation-plan.md:135-136,196-207,248`; `task.md:45`). |
| F6 — not-started status | open | ✅ Fixed | Both target frontmatters are `draft`, all task rows are unchecked, and implementation paths/handoffs remain absent (`implementation-plan.md:6`; `task.md:5,42-64`; `C:/Temp/av-kit/p6-r2-path-existence.txt`). |
| F7 — handoff-marker restatement | open | ✅ Fixed | `HANDOFF_BUNDLE_MARKERS` is defined once and `HANDOFF_MARKER_CHECK` is the sole executable owner; task rows call the script (`implementation-plan.md:157-158,290,340-343`; `task.md:46,55,63`). |

### PR-6 Pre-Verdict Gate

`pass` — all three named manifests are present and untruncated. Every child receipt exists, its non-banner hit count matches its manifest row, and the raw/disposition multiset is 82/82 with no delta (`C:/Temp/av-kit/p6-r2-pr6-hit-index.txt`; `C:/Temp/av-kit/p6-r2-pr6-disposition-compare.txt`). The appendix's “81” total is the non-blocking clerical Finding 4, not a missing or undispositioned census hit.

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-19.1–19.23 each cite Spec, Local Canon/grouping, Research-backed, or the selected emerging standards. |
| Validation cells are exact commands | fail | Commands are concrete, but Red semantics and focused-test exclusion can false-pass materially incomplete evidence (Findings 1 and 3). |
| BUILD_PLAN audit row present | pass | Plan lines 311–316 and task row 6 bind MEU-19 and `HUB_NEXT_AFTER`. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows remain ordered. |

#### Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | fail | The correction log marks F1/F4 fixed, but current controls leave the two gaps above. |
| DR-2 Residual old terms | pass | Old-literal receipts are zero-hit; `ignore extra keys` is correctly confined to a negative-test column. |
| DR-3 Downstream references | pass | MEU-20–25 deferrals and p4/p5 carry-forward references resolve to registered work. |
| DR-4 Verification robustness | fail | Findings 1 and 3 demonstrate validation paths that return green without complete intended evidence. |
| DR-5 Evidence auditability | pass | PR-6 receipts, target reads, authority reads, existence checks, and exact command text are reproducible. |
| DR-6 Cross-reference integrity | fail | The quit-only cleanup chain is narrower than `07-distribution.md:124`'s any-owned-exit rule. |
| DR-7 Evidence freshness | fail | The appendix says 81 hits; the current manifests and dispositions prove 82 (Finding 4). |
| DR-8 Completion vs residual risk | pass | Targets remain draft/unstarted and make no implementation-complete claim. |

#### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | WP-19a→e and task rows 1→5 now share harness → Red → Green → E2E → gate ordering. |
| PR-2 Not-started confirmation | pass | `ui/`, CLI code/tests, MEU handoff, and implementation-review file are absent; every task row is unchecked. |
| PR-3 Task contract completeness | pass | Every actionable row has owner, deliverable, exact validation, dependency, context strategy, durable output, and status. |
| PR-4 Validation realism | fail | The Red and focused-test gates can false-pass (Findings 1 and 3). |
| PR-5 Source-backed planning | pass | Non-spec locks are labeled and traced; no unsourced page or packaging scope was added. |
| PR-6 Handoff/corrections readiness | pass | One MEU handoff is explicit, and all 82 raw census hits are dispositioned. |
| PR-7 Scope discipline | pass | MEU-20–25 deferrals resolve to grouping/registry; out-of-scope rows cite actual canon. |
| PR-8 Control reachability/totality | fail | Unexpected owned-child exit has no cleanup producer; Red/focused-test gates have concrete false-pass paths (Findings 1–3). |
| PR-9 Single-statement discipline | pass | R1 marker literals now have one executable owner; the rechecked named sets are referenced rather than behaviorally redefined. |

### Commands Executed

- Read-only, redirected reads of the workflow, review template, harness/profile, session context, roles, target plan/task, rolling review, and all named authority files.
- `C:/Temp/av-kit/p6-r2-pr6-counts.txt` — manifest/review existence and exact sizes.
- `C:/Temp/av-kit/p6-r2-pr6-all-raw-hits.txt` and `p6-r2-pr6-hit-index.txt` — every child receipt and 82-hit raw index, excluding RTK banners.
- `C:/Temp/av-kit/p6-r2-pr6-disposition-compare.txt` — raw/disposition multiset equality (`82/82`).
- `C:/Temp/av-kit/p6-r2-plan-numbered.txt` and `p6-r2-task-numbered.txt` — complete current targets with line numbers.
- `C:/Temp/av-kit/p6-r2-path-existence.txt` — unstarted state plus referenced-artifact existence.
- `C:/Temp/av-kit/p6-r2-repeated-literals.txt` — PR-9 recheck.
- `C:/Temp/av-kit/p6-r2-pre-edit-guard.txt` — canonical write-target guard.

No project tests or `tools/` scripts were run because the plan remains unapproved (SIGN 1). `P:/av-kit` has no `.git` directory, so a repository diff was unavailable; file state and exact receipts were used instead.

### Open Questions / Assumptions

- None requiring human product choice. The required corrections are deterministic from the existing TDD, lifecycle, G36, and PR-8 contracts.
- The focused-test false-pass assumes the task's local command environment as written (no `CI` assignment and no specified `allowOnly: false`); Vitest documents `allowOnly` defaulting to `!process.env.CI`.

### Required Follow-Up

Use `/plan-corrections` to resolve Findings 1–3 and update the clerical census total in Finding 4. The round-3 correction census must disposition the changed Red-gate, child-exit cleanup, and focused-test-control surfaces.

### Verdict

`changes_required` — PR-6 passes, and five of seven r1 findings are fixed, but two r1 High findings remain open and one new High finding demonstrates a separate G36 false-pass. The plan must not enter execution.

### Residual Risk

After correction, Windows process-query and termination behavior still require execution-time proof, and Playwright may validly use the evidence-gated no-display `[B]` path. Those execution risks do not justify weakening the Red, child-exit cleanup, or focused-test controls.

---

## Corrections Applied (2026-08-20) — after Round 2

**Workflow**: `/plan-corrections` inside `/create-plan` §5b. Plan/task + plan-folder helper script only. No product code.
**Agent**: coordinator (implementer) — `corrections_applied`, never `approved`.

| # | Sev | Status | Fix |
|---|-----|--------|-----|
| 1 | High | fixed | `RED_ORACLE` + `RED_ORACLE_CHECK` (`assert-red-oracle.ps1`). Row 2 adjudicates Python and UI separately: nonzero exit **and** allow-marker, deny collection/config/toolchain. |
| 2 | High | fixed | `SHUTDOWN_OWNED` now has two producers (quit **and** unexpected owned-child `exit`/`close`). AC-19.23 Chain B + negative: crash must not leave a live `api_base`. |
| 3 | High | fixed | `VITEST_ALLOW_ONLY` (`allowOnly: false` + `--allowOnly=false` on every vitest run). `SCAN_G36_ARGS` includes `.only` / `fit` / `fdescribe`. `UI_ESLINT` covers `tests/`. |
| 4 | Low | fixed | Prior appendix prose total corrected from 81 to 82. |

### r2 blast-radius census

Manifests: `C:/Temp/av-kit/census-p6-r2-manifest.txt`, `C:/Temp/av-kit/census-p6-r2-g36-manifest.txt`.
`assert-red-oracle.ps1` exists (`red_oracle_script=True`).
Sweeps: 12 primary + 1 G36 variant = 13. Zero-hit old: 2. Nonzero raw hits: 37. Each hit dispositioned below. No truncation.

### Zero-hit old receipts

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `C:/Temp/av-kit/census-p6-r2-vitest-run-bare-old.txt` | 0 | no bare `npx vitest run;` |
| `C:/Temp/av-kit/census-p6-r2-eslint-src-only-old.txt` | 0 | no `eslint src/` without `tests/` |

### Per-hit disposition — `RED_ORACLE`

Receipt: `C:/Temp/av-kit/census-p6-r2-red-oracle-new.txt` (6)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:59` | updated — WP-19b requires `RED_ORACLE_CHECK` |
| 2 | `implementation-plan.md:160` | updated — named-set definition |
| 3 | `implementation-plan.md:161` | updated — owner of `RED_ORACLE` |
| 4 | `implementation-plan.md:295` | updated — Files Modified |
| 5 | `task.md:43` | updated — Red row validation calls the script twice |
| 6 | `task.md:82` | updated — TDD note |

### Per-hit disposition — `RED_ORACLE_CHECK`

Receipt: `C:/Temp/av-kit/census-p6-r2-red-oracle-check-new.txt` (5)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:43` | updated — Red row |
| 2 | `task.md:82` | updated — TDD note |
| 3 | `implementation-plan.md:59` | updated — WP-19b |
| 4 | `implementation-plan.md:161` | updated — named-set definition |
| 5 | `implementation-plan.md:295` | updated — Files Modified |

### Per-hit disposition — `assert-red-oracle.ps1`

Receipt: `C:/Temp/av-kit/census-p6-r2-assert-red-oracle-new.txt` (3)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:43` | updated — executable calls |
| 2 | `implementation-plan.md:161` | updated — named-set command |
| 3 | `implementation-plan.md:295` | updated — Files Modified |

### Per-hit disposition — `VITEST_ALLOW_ONLY`

Receipt: `C:/Temp/av-kit/census-p6-r2-vitest-allow-only-new.txt` (3)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:158` | updated — named-set definition |
| 2 | `task.md:42` | updated — harness row + config assert |
| 3 | `task.md:82` | updated — TDD note |

### Per-hit disposition — `--allowOnly=false`

Receipt: `C:/Temp/av-kit/census-p6-r2-allowonly-false-new.txt` (8)

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:42` | updated — row 1 |
| 2 | `task.md:43` | updated — row 2 |
| 3 | `task.md:44` | updated — row 3 |
| 4 | `task.md:46` | updated — row 5 |
| 5 | `task.md:51` | updated — H1-2 |
| 6 | `implementation-plan.md:158` | updated — named-set text |
| 7 | `implementation-plan.md:165` | updated — `MEU_SCOPED_GATE` |
| 8 | `implementation-plan.md:332` | updated — Verification §1 |

### Per-hit disposition — `UI_ESLINT` / G36 `.only` / shutdown

| Receipt | # | file:line | Disposition |
|---------|---|-----------|-------------|
| `census-p6-r2-ui-eslint-new.txt` | 1 | `implementation-plan.md:159` | updated — named-set definition |
| `census-p6-r2-ui-eslint-new.txt` | 2 | `implementation-plan.md:165` | updated — `MEU_SCOPED_GATE` |
| `census-p6-r2-it-only-new.txt` | 1 | `implementation-plan.md:143` | updated — `SCAN_G36_ARGS` |
| `census-p6-r2-it-only-escaped.txt` | 1 | `task.md:46` | updated — row 5 G36 regex includes `it\.only` |
| `census-p6-r2-unexpected-owned-exit-new.txt` | 1 | `implementation-plan.md:256` | updated — AC-19.23 Chain B |
| `census-p6-r2-unexpected-owned-exit-new.txt` | 2 | `implementation-plan.md:268` | updated — sufficiency |
| `census-p6-r2-crash-leaves-new.txt` | 1 | `implementation-plan.md:256` | updated — AC-19.23 negative |
| `census-p6-r2-shutdown-owned-r2.txt` | 1 | `task.md:44` | confirmed-consistent — Green names the set |
| `census-p6-r2-shutdown-owned-r2.txt` | 2 | `implementation-plan.md:60` | confirmed-consistent — WP-19c |
| `census-p6-r2-shutdown-owned-r2.txt` | 3 | `implementation-plan.md:95` | updated — two-producer definition |
| `census-p6-r2-shutdown-owned-r2.txt` | 4 | `implementation-plan.md:256` | updated — AC-19.23 |
| `census-p6-r2-shutdown-owned-r2.txt` | 5 | `implementation-plan.md:268` | updated — sufficiency |

Ready for independent Round 3 (plan-review cap). Reviewer must write **new first frontmatter** `round: 3` / `review_round: 3` and adjudicate r2 F1–F4 plus PR-6 on the r2 census. Do not treat this `corrections_applied` as `approved`.

---

## Recheck (2026-08-20) — Round 3 (Plan-Review Cap)

**Workflow**: `/plan-critical-review` recheck after the second `/plan-corrections` pass  
**Agent**: `gpt-5.6-sol`  
**Checklist Applied**: IR, DR-1–DR-8, PR-1–PR-9

### Intent Anchor

Executing this plan is supposed to deliver Session 7 / MEU-19 only: an Electron shell that owns a live-identity-verified `python -m avkit_api` child, exposes strict allowlisted IPC and Bearer-authenticated `apiFetch`, and renders AppShell/console without starting later GUI pages or distribution packaging. The current plan would deliver that objective: the Round 2 Red-evidence, owned-child-exit retirement, and focused-test false-pass gaps are now bound to executable controls and negative oracles.

### Findings

No findings. PR-6 passed, all four Round 2 findings are fixed, and no new `High`/`Critical` delivery-level defect or non-blocking clerical note survived the full IR/DR/PR recheck.

### Prior Pass Adjudication

| Round 2 Finding | Prior Status | Round 3 Result | Evidence |
|-----------------|--------------|----------------|----------|
| F1 — Red gate accepts any nonzero failure | still-open | ✅ Fixed | `RED_ORACLE_CHECK` is required before Green and separately adjudicates the Python/UI receipts; the helper requires an allow-marker and rejects collection/config/toolchain markers (`implementation-plan.md:59,160-161`; `task.md:43`; `assert-red-oracle.ps1:12-58`). |
| F2 — discovery retirement only on Electron quit | still-open | ✅ Fixed | `SHUTDOWN_OWNED` now names two producers: quit signals only `owned.pid`, while owned-child `exit`/`close` retires `DESCRIPTOR_PATH` and `PORT_SIBLING` without signaling another process. AC-19.23 observes both paths and fails if crash leaves a live `api_base` (`implementation-plan.md:95,256,268`; authority `07-distribution.md:124,189-191`). |
| F3 — focused Vitest tests can false-pass G36 | open | ✅ Fixed | `VITEST_ALLOW_ONLY` requires config `allowOnly: false` and `--allowOnly=false` on every Vitest run; `SCAN_G36_ARGS` includes `.only`, `fit`, and `fdescribe`; `UI_ESLINT` covers `tests/` (`implementation-plan.md:143,158-159,165,332`; `task.md:42-46,51,82`). |
| F4 — prior correction census total says 81 rather than 82 | open (Low) | ✅ Fixed | The prior Corrections Applied appendix now states 82 total raw hits (`2026-08-19-p6-gui-shell-plan-critical-review.md:148`), matching its 82/82 disposition evidence. |

### PR-6 Pre-Verdict Gate

`pass` — both named Round 2 manifests are present and complete. All 13 child receipts exist and were read; excluding RTK banners, their declared counts total 37 raw `file:line` hits. The after-Round-2 corrections appendix contains 37 corresponding `updated` / `confirmed-consistent` dispositions with no multiset delta (`C:/Temp/av-kit/round3-r2-child-receipts.txt`; `C:/Temp/av-kit/round3-pr6-compare.txt`).

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-19.1–19.23 each cites Spec, Local Canon/grouping, Research-backed material, or a named emerging standard (`implementation-plan.md:234-256`). |
| Validation cells are exact commands | pass | All actionable rows provide concrete redirected commands; the Red row uses the plan-owned oracle helper and the Green/H1 Vitest commands explicitly disallow focused tests (`task.md:42-63`). |
| BUILD_PLAN audit row present | pass | The audit binds MEU-19 to `PLAN_FOLDER`, Phase 6, and `HUB_NEXT_AFTER` (`implementation-plan.md:316-322`; `task.md:47`). |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows remain explicit and ordered (`task.md:49-64`). |

#### Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | The after-Round-2 correction claims match current plan/task/helper state; the four findings above are fixed. |
| DR-2 Residual old terms | pass | The two old-form Round 2 receipts are zero-hit, and the current targets use the corrected controls (`census-p6-r2-vitest-run-bare-old.txt`; `census-p6-r2-eslint-src-only-old.txt`). |
| DR-3 Downstream references | pass | MEU-20–25 deferrals resolve to the registry/grouping, while MEU-19 retains startup, IPC, AppShell, and console ownership. |
| DR-4 Verification robustness | pass | Red receipts require semantic adjudication; owned-child crash cleanup and focused-test exclusion each have a concrete negative oracle. |
| DR-5 Evidence auditability | pass | Targets, authorities, both manifests, every child receipt, the 37/37 disposition comparison, existence checks, and status checks are reproducible named receipts. |
| DR-6 Cross-reference integrity | pass | `SHUTDOWN_OWNED` now matches both the any-owned-exit retirement rule and owned-child-only quit rule in `07-distribution.md:124,189-191`. |
| DR-7 Evidence freshness | pass | The current Round 2 manifests total 37 hits and match 37 dispositions; the earlier 82-hit appendix total is corrected. |
| DR-8 Completion vs residual risk | pass | Targets remain `draft`/unstarted and make no implementation-complete claim. |

#### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | WP-19a→e and task rows 1→5 retain harness → Red → Green → E2E → MEU gate ordering. |
| PR-2 Not-started confirmation | pass | All 19 actionable task statuses are `[ ]`; `ui/`, CLI code/tests, the MEU handoff, and the implementation-review file are absent (`C:/Temp/av-kit/round3-task-status-exact.txt`; `round3-readiness-and-existence.txt`). |
| PR-3 Task contract completeness | pass | All 19 actionable rows have task, owner, deliverable, validation, dependency/context, durable output, and status fields; the objective check found zero incomplete rows. |
| PR-4 Validation realism | pass | Current commands materially reject the three prior false-pass paths: wrong Red reason, focused Vitest execution, and incomplete child-exit retirement evidence. |
| PR-5 Source-backed planning | pass | Non-spec locks cite grouping, prior canon, research-backed sources, or named standards; no unsourced page or packaging behavior is added. |
| PR-6 Handoff/corrections readiness | pass | One MEU handoff and one rolling implementation-review path are explicit; the Round 2 blast-radius census is complete and fully dispositioned. |
| PR-7 Scope discipline | pass | MEU-20–25 deferrals are registered and Session 7 remains MEU-19 only; genuine out-of-scope rows cite grouping/build-plan omissions (`implementation-plan.md:299-312`). |
| PR-8 Control reachability/totality | pass | IPC, Bearer, dev child identity, unexpected owned-child exit, and G36 controls each name observables, production chains, and adversarial negative outcomes. No demonstrated vacuous control remains. |
| PR-9 Single-statement discipline | pass | Corrected risk-path semantics have named owners (`RED_ORACLE_CHECK`, `SHUTDOWN_OWNED`, `VITEST_ALLOW_ONLY`, `SCAN_G36_ARGS`, `UI_ESLINT`); repeated command invocations reference those semantics without a materially divergent live spelling. |

### Commands Executed

- Read-only redirected reads of the workflow, review template, terminal preflight, evidence policy, harness/project context, roles, all four targets, rolling review, and named authority files.
- `C:/Temp/av-kit/round3-review-and-manifests.txt` — current rolling review plus both Round 2 manifests.
- `C:/Temp/av-kit/round3-r2-child-receipts.txt` — all 13 manifest-named child receipts, read verbatim.
- `C:/Temp/av-kit/round3-pr6-compare.txt` — manifest count checks plus raw/disposition multiset equality (`37/37`).
- `C:/Temp/av-kit/round3-targets-numbered.txt`, `round3-target-ranges.txt`, and `round3-target-ranges-2.txt` — current targets with stable line numbers.
- `C:/Temp/av-kit/round3-authority-risk-paths.txt` and `round3-authority-scope-and-g36.txt` — IPC, Bearer, lifecycle, Session 7/MEU-19, action-index, M5, and G36 authority.
- `C:/Temp/av-kit/round3-readiness-and-existence.txt` and `round3-task-status-exact.txt` — referenced-helper existence and unstarted-state proof.
- `C:/Temp/av-kit/round3-r2-surface-sweep.txt` — Round 2 control/source/scope recheck.
- `C:/Temp/av-kit/round3-pre-edit-guard.txt` — canonical write-target guard.

No project tests or `tools/` scripts were run because this is an unapproved-plan review under SIGN 1.

### Open Questions / Assumptions

- None requiring a human product decision. The review assumes the metered Codex API-key profile supplied by `PROJECT-PROFILE.md`; no additional reviewer dispatch occurred inside this reviewer invocation.

### Required Follow-Up

None for plan correction. This review workflow stops after recording the Round 3 verdict; it does not begin execution or modify plan/product files.

### Verdict

`approved` — PR-6 passes, all four Round 2 findings are fixed, and the complete IR/DR/PR recheck found no remaining blocking or clerical finding. The plan-review cap is satisfied with an approval on Round 3.

### Residual Risk

Execution must still prove Windows process-query/SIGTERM behavior and real Electron E2E behavior. A no-display environment may support the plan's evidence-gated `[B]` path for the E2E run only; it cannot excuse missing tests or weaken the live-identity, Bearer, IPC, or G36 contracts.
