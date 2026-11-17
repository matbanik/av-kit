---
date: "2026-11-17"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "dph-execution-2026-11-15-docs-path-hygiene"
round: 1
---

# Critical Review: 2026-11-15-docs-path-hygiene

> **Review Mode:** execution
> **Verdict:** approved

## Scope

Session 83, no MEU. Codex independently reviewed the Anthropic implementation: the plan/task, handoff, scoped working-tree changes against HEAD `86ee8e3`, all three new deliverables in full, baseline records and plan-local checks, installer settings and installed electron-builder implementation, the cited rc.2 round-trip preconditions, and original Red/Green/full-gate/register receipts. Applied relevant IR, DR and AV checks. Writes are confined to `C:/Temp/av-kit`; the coordinator publishes the canonical report.

**Intent anchor:** av-kit's tracked text names the install folder the installer really uses (`Programs/av-kit-ui`), and a gate check, `tools/check_home_path.py`, fails when a file outside today's allow-listed evidence holds the home folder's full path; the six live files that hold it today are fixed, and every evidence file keeps its bytes.

**Intent achieved:** yes. No Critical or High findings, and no required correction established. Approved plan decisions and declared scope limits were accepted.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — The install folder

Accepted D-811, D-991 and D-996. `ui/package.json:2` retains `av-kit-ui`; `ui/electron-builder.yml:16-23` does not override the one-click/per-user defaults. The installed builder calls `getWindowsInstallationDirName(appInfo, !oneClick || isPerMachine)` at `ui/node_modules/app-builder-lib/out/targets/nsis/NsisTarget.js:270`; `targetUtil.js:40-41` selects the package's sanitized name for this configuration. Thus `Programs/av-kit-ui` is the right folder, while the executable remains `av-kit.exe`.

`README.md:174-175` and `docs/build-plan/07-distribution.md:40` now name that folder. The six replacement layout lines at `07-distribution.md:43` put backend, ffmpeg and MCP directly under `resources/`, matching `ui/electron-builder.yml:32-35,52-53`. Both moved comments retain their columns; the README JSON still parses. This is the approved scoped layout correction, not a claim that the illustrative block enumerates every extra resource.

An independent scan of README and Markdown under `docs/build-plan/`, `.agent/docs/` and `_inspiration/` found zero remaining wrong-folder locations. Evidence and the accepted login-item fixture/generated-triage exceptions were not reclassified as live documentation. The rc.2 script already checks both the real and historical folder at `docs/execution/plans/2026-11-08-release-rc2/install-roundtrip.ps1:55-58`; D-990's older evidence remains unchanged.

## Q2 — CHECK, HOME_RE, ALLOW and DIGEST

Accepted the implementation in `tools/check_home_path.py`. Root resolution uses Git's top-level at `:230-234`; enumeration at `:202-207` includes tracked and nonignored untracked files. `_excluded` at `:123-132` removes hub and secret names before file stat/read. The tests at `tests/tooling/test_check_home_path.py:357,380` verify those exclusions with a recording reader and a positive ordinary-file control. No forbidden real file was opened in this review.

HOME_RE at `check_home_path.py:105-120` implements the approved drive/Git Bash forms, separator multiplicity, case behavior and trailing-name boundary. Independent in-memory probes found all 12 named forms in ten encodings at the expected line, and rejected five longer-name near misses. The decoder at `:139-159` handles BOM precedence, all five unmarked NUL views, malformed sequences and pair deduplication without content output. Original tests also pin CRLF numbering, mixed CJK UTF-16, binary-with-path and broken UTF-16 behavior.

ALLOW parsing at `:179-199` refuses malformed, duplicate, unsorted and forbidden paths without echoing a line. Missing/unreadable lists fail with exit 2. At `:286-296`, DIGEST matches alone exempt evidence; mismatches holding the path become `changed`, removed paths become `stale`, and missing listed files remain `stale`. Independent scratch CLI probes confirmed unchanged=0, edited=1, stale=1, malformed=2 and missing-entry=1. An injected read failure on the scratch allow-list returned 2 with a fixed diagnostic and no traceback. The normal mode never prunes or writes ALLOW.

The reviewed repository pass is nonvacuous: `CHECK` read 2,486 files, exempted 60, counted 31 NUL files, and its empty-list negative found exactly 118 pairs. A valid empty repository with an empty list, or a different valid host/home, can legitimately pass with no matches; the approved contract is a maintainer-host gate, not a universal identity detector. Invalid roots fail rather than scan silently. Percent-encoded separators and the other approved HOME_RE limits at `implementation-plan.md:397` remain accepted boundaries, not new findings.

## Q3 — EVIDENCE_SET and preservation

Accepted ALLOW's seven-line policy header and exactly 60 entries: 16 handoffs / 53 lines, 14 session digests / 14 lines, and 30 plan-folder files / 51 lines. No live file or this session's own artifact is listed. The independent empty-list result equals row 0's evidence pairs exactly: 118 pairs, 60 files, no extras or omissions.

Independently recomputed every entry's DIGEST and compared it with ALLOW and `inventory-0.json`; all 60 agree. Each file also matches its HEAD blob after existing Git line-ending normalization. No evidence file has a tracked content delta. This observation uses the approved CRLF-to-LF definition of DIGEST; it does not misdescribe Git's normalized blobs as raw Windows work-tree bytes. ALLOW's raw SHA-256 matches its row-3 pin:

`7391b734e1dfe841d104f2b34a6923e6016f2890b1654d419cb1f75fbc9f3770`

The independently rerun inventory cross-check reports `allow-list entries: 60; EVIDENCE_SET now: 60`, `CHECK with an empty allow-list: exit=1 found=118; inventory pairs=118`, `allowlist.sha256 matches`, and `inventory: ok`. No D-989 extra evidence file needed an entry.

## Q4 — LIVE_SET and the live fixes

Accepted the six-file repair. Row 4's original receipt reports exactly row 0's 12 LIVE_SET pairs, with `refused found=12 changed=0 stale=0`. Independent comparison confirmed pair equality. All ten existing BASE copies match their pinned raw SHA-256 values and HEAD after Git line-ending normalization, so the edit checks are anchored to the stated post-Session-82 baseline.

All four read-only edit-check groups pass against current bytes: docs=5 files, tests=2, commands=1, register stage 10=1. They enforce the expected complete file contents for the docs/tests/commands, not just disappearance of a substring. `06-gui.md:960,975` retains field widths and CRLF. The design example preserves its screenshot name and operation, and the workflow transcript retains its relative suffix.

`capture-interactive.test.ts:14` changes only its shared fixture constant. The mock returns that constant and the journal/log assertions still compare it, including `:82-83`. `dev-spawn.test.ts:8,76-77,88-89` changes only the five specified fixture inputs; executable ownership and withheld/zero-port assertions remain intact. No expectation was weakened beyond the plan's explicitly approved fixture-value changes. The recorded targeted run passed all 22 tests without skips.

The scrub at `.agent/context/known-issues.yaml:3393,3404` replaces only the home prefix with `~`. Its explanation of the ancestor walk, the external `.agent` folder, hermetic-temp workaround and continuing local relevance keeps its meaning. Parsed register differences are confined to the two scrubbed fields and the two issues' resolution fields.

## Q5 — Red, Green and the gate

Accepted the original Red as an intended missing-CHECK assertion: its preserved child exit is 1, and the receipt contains 47 `AssertionError: missing tools/check_home_path.py` diagnostics and `47 failed`. It is not an import/setup failure. The Green receipt has `47 passed in 6.64s`; the full gate independently records another 47 passes. The reviewer reran the Red oracle's 39-fixture selftest: 13 positives, 26 negatives, zero wrong.

| Tests audited (IR-5) | Grade | Basis |
|---|---|---|
| AC-1, AC-2, AC-3, AC-7 | Strong | Exact locations/counts, case and longer-name negatives, output-content markers and sorting |
| AC-4, AC-6 | Strong | Explicit failure exits, malformed-input rejection and no argument echo/traceback |
| AC-5 | Strong | Real isolated Git selection and observed reader calls with exclusion controls |
| AC-22 | Strong | Real byte encodings, binary/NUL and malformed UTF-16 fixtures with exact line results |
| AC-23 | Strong | Explicit digest edits, stale/prune cases and before/after allow-list byte comparisons |
| Both edited UI test files | Strong for this delta | Existing behavioral assertions preserved; only approved fixture strings change |

The new tests use fake homes and temporary repositories; subprocess calls use the existing interpreter and scratch Git configuration. No actual home contents are test fixtures. Exclusion instrumentation observes file reads; it does not replace the scanner's matching or assertions.

The gate has 23 steps, all exit 0, and every corresponding original D6 receipt exists. It includes home-path and inventory-check. Direct inspection corroborates 47 scanner tests, 22 targeted UI tests, 106 adoption tests, 3,082 full Python passes and 1,578 full UI passes in 137 files; the closeout selftest has 231 arms and zero failures. No baseline failure was excused. Static, targeted and full ordering, fail-fast handling and equal before/after identities are present. The skips match the approved scope: no product/API/MCP source change, build or GUI runtime change requiring a new launch.

`.agent/docs/commands.md:212` registers the same CHECK as `session-gate.ps1:83`; the gate adds `uv run --no-sync` to use the already established environment. This does not select another check. Suites, builds and Electron were not rerun by this reviewer.

Execution decisions D-1080–D-1086 are sound: the long-title Red parser keeps attribution checks; secret exclusions honor the read boundary; PNG line 4 follows its LF count; formatting removes no behavior; the full Vitest baseline makes the excuse rule auditable; register dates reflect the actual run; and `sys.executable` uses pytest's interpreter without nested resolution. Disclosed plan-status/hash, scratch overwrite and gate-stage changes do not undermine the delivered behavior or this evidence.

## Q6 — Register

Accepted both resolutions and the scrub through the resolver. The row-7 script passes the baseline register pin and both named scrub fields; its receipt reports seven changed parsed fields and zero problems. The row-10 script passes `register-row7.sha256`; its receipt reports only the second issue's five resolution fields and zero problems. No arbitrary register editor is used by those rows.

The hash chain is independently verified: BASE register hash `66f97171c1b616bbf806b06eac74d4a4a89b32397bf85c880ef35f16f2c8f942` → row-7 hash `768a4b61e704c55ea36b6859969dc35e1d7cc54b750d66201a1811e0c8a008fa` → current raw hash `ca80ae7edec5c261a38c2870d5fded95ddefdce49c32bb94698b2bde1581a21e`. The retained before-row-10 scratch bytes match the row-7 pin. The resolver checks the expected hash before staging, retains the Windows write-denying handle and validates the parsed difference before replacement.

Both original render/check pairs report success. The independently run current `issue_triage.py render --check` also exits 0: `OK: known-issues.md is up-to-date`. Both issues are resolved with actual-day verification and accurate resolution text; the unrelated scrub issue remains otherwise unchanged. No resolver write mode was run during review.

## Q7 — Safety, fidelity and tested state

**tested_state:**

`86ee8e31c4e3db29c45d1f316f350b9080b09d9f+5f22c37d3ec1423901bd81e096bfefb4865c2cc961195253bea74208bd8af099`

The plan's unchanged `identity.py --state-only`, run with the existing project interpreter and ELECTRON_RUN_AS_NODE unset, returned exactly the gate value. It does not differ. A process-local `core.excludesFile` pointed to a scratch ignore containing only the supplied `.claude/settings.local.json` rule, reproducing the host's documented ignore behavior and preventing identity.py from reading that forbidden file. Inherited sandbox Git configuration was preserved. Neither global/repository Git configuration nor the user's ignore file was opened or changed. A first scratch wrapper attempt replaced the inherited Git configuration and failed Git root resolution; preserving those entries corrected only the review wrapper.

The new evidence handoff accounts for the current CHECK file count of 2,486 versus 2,485 at the gate: it was created after the gate and is an excluded closeout artifact for identity purposes. The matched identity, clean CHECK, unchanged ALLOW pin and empty-list comparison corroborate the handoff's substantive claims.

The expected CRLF/LF kinds are preserved by the byte-level edit checks. The current-focus addition retains CRLF and the entire original suffix. All 18 files in this plan folder and its handoff/review namespace are LF, contain no actual home-folder path and no email address. Added tracked lines likewise contain neither. The current repository CHECK covers this session's new artifacts and current-focus in addition to the live fixes. Historical allow-listed evidence is retained, not rewritten.

HEAD remains the baseline and the index has no staged delta. The observed status contains only the approved files/plan/closeout/shared-focus paths plus the supplied sandbox-only untracked settings filename, whose contents were never opened. Scope and receipts show no evidence-file edit or unrelated content delta. This review performed no repository write, commit, stash, revert, install, sync, build, suite, app launch or network request. It does not claim a forensic reconstruction of every historical filesystem operation.

The report and companion JSON were independently scanned using CHECK's actual-home pattern and equivalent literal/URL checks before return: zero home-path matches. H1-7 approval permits the coordinator to continue the pending review-state checks and H2, including AC-21's repeat after canonical review/reflection/metrics publication. This review does not claim those future rows have already run.

## Checklist Results

| Check | Result | Observation |
|---|---|---|
| IR-1, IR-4, IR-5, IR-7 | pass | CLI contract evidence, all ACs accounted for at this boundary, general live repair and assertions audited |
| IR-2, IR-3, IR-6 | n/a | No service stub, HTTP mapping or external product write surface added |
| DR-1 through DR-8, applicable scope | pass | Installer claims, residual scan, exact edits, evidence preservation and matched identity corroborated |
| AV-1 through AV-6 | pass | Attributed Red/Green, real collaborator checks, no bypass/skip/placeholders and sourced criteria |
| Current full-gate identity | pass | Recomputed value equals both recorded gate identities |
| Independent probes and fidelity | pass | 120 form/encoding combinations; digest/list failures; 118 evidence pairs; BASE/hash/EOL checks |

Reviewer commands below ran from `P:/av-kit`, with `PYTHONDONTWRITEBYTECODE=1`, TMP and TEMP under `C:/Temp/av-kit/dph/exec-review/tmp`, and ELECTRON_RUN_AS_NODE unset. Each shell wrapper redirected all streams under `C:/Temp/av-kit`, captured the child exit immediately, and returned it. The initial scratch audit confused task-row count with gate-step count and failed its own assertion; the corrected count of 23 matches the actual gate script/receipts. A separate initial comparison needed CRLF normalization of captured Windows stdout. Neither correction changed the repository or expectations about the deliverable.

```json
{"schema_version":"evidence.v1","check_id":"dph-review-identity","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/dph-review-verify.py state","cwd":"P:/av-kit","scope":"unchanged identity.py --state-only with process-local scratch host-ignore rule","phase":"targeted","exit_code":0,"result":"pass","tested_state":"86ee8e31c4e3db29c45d1f316f350b9080b09d9f+5f22c37d3ec1423901bd81e096bfefb4865c2cc961195253bea74208bd8af099","output":"identity-host-ignore: exit=0; identity equals the gate before/after value exactly; forbidden local settings contents never opened."}
```

```json
{"schema_version":"evidence.v1","check_id":"dph-review-checks","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/dph-review-verify.py checks","cwd":"P:/av-kit","scope":"read-only repository CHECK, scratch empty ALLOW, independent HEAD/row-0 digest comparison, four edit groups, inventory cross-check, Red oracle selftest, issue render --check","phase":"targeted","exit_code":0,"result":"pass","tested_state":"86ee8e31c4e3db29c45d1f316f350b9080b09d9f+5f22c37d3ec1423901bd81e096bfefb4865c2cc961195253bea74208bd8af099","output":"CHECK exit 0: ok files=2486 allowlisted=60 nul=31. Empty ALLOW exit 1: refused found=118 changed=0 stale=0. Exactly 60 evidence files and 118 row-0 pairs; all DIGESTs/ALLOW pin match; 10 BASE copies match pinned raw hashes and HEAD after Git EOL normalization. edit-check docs/tests/commands/register stage 10 pass. inventory: ok. Red selftest: 39 fixtures, 0 wrong. OK: known-issues.md is up-to-date."}
```

```json
{"schema_version":"evidence.v1","check_id":"dph-review-probes","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/dph-review-verify.py probe","cwd":"P:/av-kit","scope":"independent fake-home matching/encoding probes and scratch-only CLI digest/list failure cases","phase":"targeted","exit_code":0,"result":"pass","tested_state":"86ee8e31c4e3db29c45d1f316f350b9080b09d9f+5f22c37d3ec1423901bd81e096bfefb4865c2cc961195253bea74208bd8af099","output":"120 form/encoding cases found at line 2; five longer-name negatives excluded. Scratch CLI: unchanged exit 0; edited exit 1 changed; removed exit 1 stale; malformed exit 2; missing entry exit 1 stale. Injected unreadable scratch ALLOW: exit 2, fixed diagnostic, no traceback."}
```

```json
{"schema_version":"evidence.v1","check_id":"dph-review-audit","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/dph-review-audit.py","cwd":"P:/av-kit","scope":"original gate/Red/register receipts, own-file privacy/EOL, current-focus preservation, HEAD/index and residual live install-folder references","phase":"targeted","exit_code":0,"result":"pass","tested_state":"86ee8e31c4e3db29c45d1f316f350b9080b09d9f+5f22c37d3ec1423901bd81e096bfefb4865c2cc961195253bea74208bd8af099","output":"23/23 gate steps exit 0; receipts all exist; 47/22/106 targeted and 3082 Python/1578 UI full passes; no skipped tests or baseline excuses. Original Red: exit 1 and 47 missing-CHECK assertions. Repo Red equals 12-pair LIVE_SET. Register hash chain matches. 18 own artifacts LF and no actual home path/email; added tracked lines clean. Current-focus suffix and CRLF preserved; HEAD unchanged/index clean. Live doc residual wrong-folder locations: 0. Review fidelity audit: pass."}
```

## Verdict

**approved — intent achieved, zero findings.** The implementation satisfies the reviewed Session 83 behavior and preserves the approved evidence set. The recorded full gate is accepted with matching current inputs and independent negative probes. Review-state collection, H2 and the authorized local commit remain the coordinator's work. A push is not authorized.
