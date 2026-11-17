---
date: "2026-11-17"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-15-ready-handshake/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "rh-execution-2026-11-15-ready-handshake"
round: 1
---

# Critical Review: 2026-11-15-ready-handshake

> **Review Mode:** execution
> **Verdict:** approved

## Scope

Session 82, MEU-153 and MEU-154. Reviewed the plan/task, both handoffs, plan-local verifier/baseline/gate/measurement scripts and row-0 records, the scoped changes against baseline HEAD `5e5b4ba18b293d9215f79be878b0fa7b815f83b5`, both new tests in full, relevant unchanged runtime code and AC-108 pins, and the recorded Red/Green/full-gate/packaged evidence. Applied relevant IR/DR and AV-1–AV-6 checks. Codex is independent of the Anthropic author. Session 83 remains outside the substantive review; its three baseline hashes were checked for preservation.

**Intent anchor:** a request sent the moment `AVKIT_READY` appears is queued by a listening socket, never refused, and the desktop app's main process reads the backend's stdout as whole lines, so a ready line split across chunks, repeated, or sent beside other lines publishes the API exactly once with the right port; the ready line's text and the descriptor stay as they are.

**Intent achieved:** yes. No Critical or High findings, and no required correction established.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Listen first

Accepted LISTEN_FIRST and READY_TEXT_KEPT. `cli.py:218-220` binds and immediately calls `sock.listen(config.backlog)`, before the descriptor at `:222` and the sole ready print at `:233`. The print's format, bound port and `flush=True` are unchanged; `write_descriptor`, its fields, names, atomic `os.replace` and port sibling are unchanged in the diff.

The installed uvicorn `Config.bind_socket` binds without listening. `Server.startup` passes this same socket to `loop.create_server` after lifespan startup. No normal handoff step closes or rebinds it. An independent loopback probe used the installed Config, observed SO_ACCEPTCONN change from 0 to 1, connected and sent bytes before asyncio started serving, called `listen` again, and received those same bytes after asyncio's handoff. Exit 0.

AC-153.1 observes the real bound socket at both publication steps; the Red receipt reads `(0, 0)` versus `(1, 1)`. AC-153.2 is deliberately a passing text/port/flush pin. AC-153.3's five real backend spawns failed their early-connect assertion before the change and passed afterwards. These test actual ordering rather than a source substring.

Limit: a fatal configuration/lifespan failure can still terminate the backend after the line. The current lifespan runs stale-job recovery before yielding; uvicorn exits on startup failure. This change removes the bind-to-listen refusal window during successful startup; it does not establish health through arbitrary fatal startup errors. No new failure path or contract regression was demonstrated.

## Q2 — The line reader

Accepted READY_LINES, READY_ONCE and READY_BOUND at `python-manager.ts:183-223`. The reader retains the unterminated suffix, strips one trailing CR, skips empty lines, processes completed lines in order, and latches on the first successful synchronous publication. Subsequent pushes neither query nor publish and retain no carry. `index.ts:268-281` constructs a reader for the newly spawned child inside `boot`; it is not a global latch reused across children.

The poison flag discards an overlong line's remaining tail before accepting the next line. The independent copied-logic probe covered a complete overlong line, repeated overflow across chunks, a ready-like poisoned tail, and a following good line. It also replayed every one of 158 byte split positions in a stream containing adjacent multibyte text, blank lines, a CRLF ready line and a repeat, plus one byte per chunk. Every case published port 13988 exactly once. Zero-port and unterminated inputs did not publish; a fresh reader could publish again.

Decoding qualification: `index.ts:296` uses per-chunk `Buffer.toString('utf8')`, with no stateful decoder or `setEncoding`. A split non-ASCII character can become replacement characters. The probe confirmed this limitation and also confirmed that it does not corrupt the actual all-ASCII ready protocol (prefix, digits and UUID), its CR/LF boundaries, or publication beside Unicode log lines. Lossless arbitrary Unicode stdout is not claimed here; LOG_PER_CHUNK was expressly retained by D-980. No finding is raised against the approved ASCII handshake.

## Q3 — Wiring

Accepted READY_STDOUT_ONLY, READY_NO_VETO and LOG_PER_CHUNK. `index.ts:301-303` hooks the ready reader only to stdout; stderr has only `onChildOutput`. That handler keeps the original per-chunk Console splitting and forwarding and contains no publication call. The reader callback uses the same owned pid, descriptor reader, live query, image, nonce and publisher as before.

`publishIfReady` checks usability before the query; `confirmReadyAndPublish` still publishes regardless of the returned ownership comparison. The reader's latch makes this one query and one publish per backend start. AC-154.4 meaningfully checks failed and foreign query results without reinstating a veto. Both MEU-108 pin files are byte-identical to their row-0 copies. Their source checks remain satisfied, and their recorded unit/Electron executions pass. No stderr publication or lost-log regression was found.

## Q4 — Measurement and packaged smoke

Accepted GAP_MEASURED. Independently reran the real `gap-tally.py` against all five execution JSONL receipts; every tally exited 0 and matched the handoff and 04's Delivered note:

| Backend / mode | Runs | First-request result | Refused | Errors |
|---|---|---|---|---|
| Before, dev fetch | 5 | 1 HTTP 200 | 4 | 0 |
| Before, dev CIM then fetch | 5 | 5 HTTP 200 | 0 | 0 |
| Before, existing packaged fetch | 5 | 0 HTTP 200 | 5 | 0 |
| After, dev fetch (`--all-ok`) | 10 | 10 HTTP 200 | 0 | 0 |
| After, scratch packaged fetch (`--all-ok`) | 5 | 5 HTTP 200 | 0 | 0 |

`accept_after_ready_ms` is measured after the first fetch (and, for CIM mode, after the query); it is not asserted to be an independent measurement of the exact listen instant. The handoff accurately explains this.

The row-4 command and build receipt use scratch `pack/build` and `pack/dist` under the receipts folder. The runtime JSON names that scratch executable, returns status 200 and `passed: true`; the text receipt reports `PASS: smoke-runtime source=bundled version=2.9.8 solver=True`. The forbidden-package check reports `[]`. Current `cli.py` still matches the build's recorded SHA-256. The packaged-unchanged receipt and my independent hash/size/mtime comparison match `baseline-packaged.json`. The tracked diff has no packaging change. Accepted D-983's disclosed local-smoke scope; no release-build claim is made.

## Q5 — Red, Green and gate

Accepted the Red/Green evidence. Preserved Red child exits are 1. Python Red contains two assertion failures and one passing pin; Green has 11 passes. UI Red contains eight assertions about the absent new function, rather than import/setup failures; Green has 17 passes including the unchanged ready-guard tests. Independently rerunning red-check on both receipts reports zero problems. Its selftest passes all 43 fixtures (14 positive, 29 negative), and gap-tally's selftest passes.

Execution decisions are sound: D-985 recognizes pytest's one-or-more-underscore long-title headers while retaining attributed assertion checks and negative fixtures; D-986 is the disclosed formatting-only amendment with its passing selftest; D-987 waits for `close`, allowing stdout to drain after process exit without weakening the exit-code, split-chunk, port or query-count assertions.

AC-154.8 invokes real `spawnOwned`, writes the ready text in two pieces 80 ms apart, consumes the pipe and asserts at least two data events, an incomplete first chunk, exit 0, one exact API address and one query. Its Green run and the full gate pass. It is a real transport test under the unit-runner directory, not a mocked emitter.

| Tests audited (IR-5) | Grade | Reason |
|---|---|---|
| AC-153.1, AC-153.2 | Strong | Real socket state, exact output/port/flush and descriptor comparison |
| AC-153.3 | Strong | Five real spawns, bounded early connects and exact health status |
| AC-154.1 through AC-154.6 | Strong | Exact publications/query counts, ordered lines, latch and negative cases |
| AC-154.7 | Adequate | Source wiring assertions, corroborated by direct wiring review |
| AC-154.8 | Strong | Real pipe, explicit split and exact one-publication result |
| AC-154.9 / AC-108 pins | Strong overall | Exact query/forwarding assertions and real Electron destroyed-window check |

The full gate records 22 steps, all exit 0, with every corresponding rh-D6 receipt present: static checks; 11 Python and 17 UI targeted tests; packaged hash binding; 3,035 passing Python tests; 137 UI files / 1,578 passing UI tests; successful UI build; one passing Electron test; OpenAPI and both renders. The count checks are present and satisfied. MCP-specific work, unrelated Electron tests and a repeated packaged build are skipped on the approved stated grounds. The baseline tail-frame flake was allowed only if reproduced at baseline; the full gate had no failures to excuse.

S5 holds in the reviewed evidence: both existing Python files retain their entire baseline contents byte-for-byte as prefixes, and both AC-108 pins are byte-identical. No existing test was edited or failed in the passing gate. No suites, builds or apps were rerun by this reviewer.

## Q6 — Register, status and docs

Accepted the issue/status/doc changes. `rh-issue-resolve.txt` records the expected row-0 register hash and exactly ten changed parsed fields, confined to status, verification and resolution_path of the two named issues. The helper's exclusive-handle/hash/staging checks were inspected; it was not executed by this reviewer. The update/render receipts and current diff show both MEUs at `ready_for_review`, bound to this plan, with consistent generated surfaces. Independent `issue_triage.py render --check` passes; the OpenAPI check also exits 0.

Only grouping section 6 row 82 changes, independently confirmed against the hash-verified row-0 copy. 04 and 06 each add one Delivered note describing the shipped behavior and actual measurements. Both retain CRLF. Existing approved decisions D-977–D-984 are respected rather than reopened. No semantic documentation mismatch was found.

## Q7 — Safety, fidelity and current state

The independently recomputed identity equals the gate's before/after identity exactly:

`5e5b4ba18b293d9215f79be878b0fa7b815f83b5+8a1f1b0c2d5d366ce04112662dee50a7002181195c6366ff019c3ff80eb58594`

The successful run used the plan's unchanged `identity.py --state-only`, the existing project interpreter, and ELECTRON_RUN_AS_NODE unset. To avoid opening the explicitly forbidden `.claude/settings.local.json`, a process-local `core.excludesFile` pointed to a scratch file containing only that supplied host ignore entry. A process-local `safe.directory=P:/av-kit` allowed Git subprocesses to resolve HEAD in this sandbox. Neither repository nor global Git configuration was written. Thus the reported value does not differ from the gate; the known ignore and Electron environment differences were normalized explicitly. The forbidden settings file and the user's global ignore were never opened.

Independent byte checks found all 23 expected line-ending kinds preserved, all 13 existing scope baselines matching their row-0 copies, and all three unrelated baseline-dirty hashes unchanged. HEAD is unchanged at the baseline; the index has no staged delta. Added tracked lines and both new tests contain no full home paths or email addresses. Existing unrelated path-hygiene debt was not reclassified as this session's work.

Historical cleanup was checked through the implementation/tests and receipts: measurement uses each owned child's pid tree; backend spawn tests terminate/wait/kill their own child in finally; the pipe child exits itself; packaged smoke stops its owned Backend in finally; Electron checks close their own app. The gate's own recorded pids 45564 and 70076 had exited; the before/after comparison names only unrelated new Python processes, which were left alone. The measurement JSONL does not retain a per-run pid inventory, so this review does not claim to independently reconstruct every historical pid from it. No evidence of an orphaned session backend or an image-wide kill was found.

All reviewer writes are under `C:/Temp/av-kit`. The only new listening socket used 127.0.0.1 and port 0 and was closed along with its client/server. No backend, Electron app, build, suite, commit, stash or revert was started by this review. The handoffs' decisive results agree with the original receipts and current tested state.

## Checklist Results

| Check | Result | Observation |
|---|---|---|
| IR-1, IR-4, IR-5, IR-7 | pass | Real backend/pipe/Electron evidence; all 14 ACs accounted for; assertions audited above |
| IR-2, IR-3, IR-6 | n/a | No new service stub, HTTP error mapping or external write schema |
| DR claim accuracy | pass | Delivered notes, measurements and register deltas match code and receipts |
| AV-1 through AV-6 | pass | Attributed Red/Green, substantive assertions, no bypass/skip/placeholders, sourced contracts |
| Current identity / full gate | pass | Exact state equality; all 22 receipt-backed steps exit 0 |
| Independent adversarial probes | pass | 158 split positions, poisoned tails and loopback queued-byte handoff |

All commands below ran with PYTHONDONTWRITEBYTECODE=1 and TMP/TEMP at `C:/Temp/av-kit/ready-handshake/exec-review/tmp`. Each wrapper preserved the native child exit and stopped on failure. The initial audit's scratch-only UTF-8 decoding error was corrected before the passing audit; no product input changed.

```json
{"schema_version":"evidence.v1","check_id":"rh-review-readonly-checks","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/exec-review/run-readonly.ps1","cwd":"P:/av-kit","scope":"identity.py --state-only; red-check selftest and original Red receipt checks; gap-tally selftest and five execution JSONL checks; issue render --check; OpenAPI --check","phase":"targeted","exit_code":0,"result":"pass","tested_state":"5e5b4ba18b293d9215f79be878b0fa7b815f83b5+8a1f1b0c2d5d366ce04112662dee50a7002181195c6366ff019c3ff80eb58594","output":"Identity equals gate. red-check: 43 fixtures, 0 wrong; original Red checks: 2 and 8 required tests, 0 problems. Gap: before dev refused 4/5, CIM 0/5, packaged 5/5; after dev 10/10 and packaged 5/5 HTTP 200. OK: known-issues.md is up-to-date. OpenAPI exit 0."}
```

```json
{"schema_version":"evidence.v1","check_id":"rh-review-adversarial-probes","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/exec-review/run-probes.ps1","cwd":"P:/av-kit","scope":"scratch copied reader algorithm without repo imports; installed uvicorn Config with a loopback port-0 socket, repeated listen and asyncio handoff","phase":"targeted","exit_code":0,"result":"pass","tested_state":"5e5b4ba18b293d9215f79be878b0fa7b815f83b5+8a1f1b0c2d5d366ce04112662dee50a7002181195c6366ff019c3ff80eb58594","output":"ASCII ready handshake: 158 byte split positions pass, including CR/LF and adjacent UTF-8. One byte per chunk, overlong lines/poisoned tails, zero/unterminated/latch/fresh-reader checks pass. Per-chunk decoding can corrupt non-ASCII text without corrupting the ASCII ready line. SO_ACCEPTCONN: bind=0 listen=1; repeated listen and asyncio handoff preserve queued connection and bytes."}
```

```json
{"schema_version":"evidence.v1","check_id":"rh-review-fidelity-audit","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/ready-handshake/exec-review/run-audit.ps1","cwd":"P:/av-kit","scope":"baseline hashes, old test contents, AC-108 pins, EOLs, packaged hashes, added-line privacy, grouping scope, full-gate receipts, HEAD and index","phase":"targeted","exit_code":0,"result":"pass","tested_state":"5e5b4ba18b293d9215f79be878b0fa7b815f83b5+8a1f1b0c2d5d366ce04112662dee50a7002181195c6366ff019c3ff80eb58594","output":"13/13 existing row-0 copies match; existing backend tests unchanged prefixes; AC-108 pins byte-identical; 23 expected EOL kinds preserved; 3/3 Session 83 hashes unchanged; packaged executable hash/size/mtime unchanged and scratch cli.py hash matches; added tracked lines/new tests contain no home path/email; grouping only row 82; 22/22 gate steps exit 0, all step receipts present; Python 3035 passed, UI 1578 passed, targeted 11/17 passed, Electron 1 passed; HEAD unchanged, index clean."}
```

## Verdict

**approved — intent achieved, zero findings.** The scoped implementation satisfies AC-153.1–AC-153.5 and AC-154.1–AC-154.9 on the reviewed state. The recorded full gate is accepted with matching current inputs and corroborating independent probes. This approval closes the independent review step; H2 and any authorized commit remain the coordinator's work. No push is authorized by this report.
