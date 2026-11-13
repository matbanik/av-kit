---
date: "2026-11-13"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-13-capture-copy-image/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s69-execution-2026-11-13-capture-copy-image"
round: 1
---

# Critical Review: 2026-11-13-capture-copy-image

> **Review Mode:** execution. **Verdict:** approved. **Intent achieved:** yes.

## Intent Anchor

Session 69 lets a user copy the image as they see it, with the current marks, saved or not, through a Copy image button and canvas Ctrl+C. Both go through a new `POST /captures/{id}/render` that bakes the posted marks exactly as Save would and writes no file. The filmstrip's Copy image follows the as-shown rule, and the per-shot actions take the names "Save annotations", "Flatten into image…" and "Restore backup…", with "Save and flatten" in the dirty-flatten confirm.

## Scope

Session 69, MEU-104 capture-copy-image-actions, ledger round 1. Reviewed the uncommitted delta from b3f393310d7a04fcdcde5092c1a5f238774493d8 on main, including the three untracked test files, the implementation plan/task/scripts, MEU-104 handoff, relevant unchanged callers and named receipts. Applied Intent Anchor, Materiality Gate, Verdict Rule, IR-1 to IR-7 and the reviewer role's adversarial checks. Claude Code / Anthropic authored the work; Codex / OpenAI is the independent reviewer and did not author it.

Accepted the supplied planning decisions and Mat's D-698 to D-700 rulings, previous sessions' delivered contracts, explicit exclusions and H1/H2 boundary. This review judges their implementation. No repository file was edited. All reviewer writes were under C:/Temp/av-kit. No suite, app/server, MCP server, network operation, package download, clipboard write, process termination or Git mutation was run. The permitted OpenAPI consistency command builds an in-process schema; it starts no server. Canonical adoption, ledger recording and H2 belong to the coordinator.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1 — Goal and end-to-end trace

Accepted. COPY_KEY and COPY_BUTTON call copyCurrentImage, which captures annotationsRef.current and invokes renderClipboardPng; parseAnnotateBody and postAuthorizedBlob carry that list to RENDER_ROUTE. AnnotateIn, _annotations_from_in, RENDER_SERVICE, the shared clamp and RENDER_BAKE produce PNG bytes for toClipboardPng and writeClipboardImage (CapturePage.tsx:1692, :1817, :2128; capture-clipboard.ts:90; capture-image.ts:20; routes/captures.py:462; services/capture.py:1493; adapter.py:546). AC-104.10 checks the real Python trace and response pixels; AC-104.11 and .13 check unsaved/saved UI payloads and exact returned bytes. Labels, filmstrip and dirty-flatten sentences have corresponding code and tests. No rejected goal behavior.

## Q2 — RENDER_BAKE and RENDER_PORT

Accepted. The extracted _bake_canvas preserves region-first ordering followed by _apply in annotation order (adapter.py:560). Independent probes compared the baseline bake method from HEAD with current bake: 27/27 byte-equal combinations over PNG RGBA, JPEG and WebP originals; PNG/JPEG/WebP outputs; empty, region-plus-drawn and all-seven-kind mark lists. Render equaled PNG bake in 9/9 cases, changed no file content/mtime and emitted no log. The unreadable-image exception is exactly the fixed path-free message at adapter.py:556. Real service probes also returned PNG with annotated_format=webp. The extraction leaves annotate/crop/flatten/revert/export/fixture callers on the same bake contract. No rejected behavior.

## Q3 — RENDER_SERVICE, RENDER_ROUTE and boundaries

Accepted. render_marks holds CAPTURE_FILE_LOCK through the read and adapter call, uses annotate's exact clamp, checks both missing-row and missing-original cases, and performs no save/unlink/sidecar operation (services/capture.py:1498). Independent real-SQLite probes started with saved marks and confirmed unchanged row, annotated file, sidecar and database/files after rendering different posted marks. Unknown/missing cases were refused and the lock was released.

The route shares AnnotateIn and _annotations_from_in with annotate. Real-stack AC-104.6/.7 prove PNG byte parity, unchanged state, matching 422/404 envelopes and accepted control-character parity; the independent probe also covered embedded NUL without printing the text. RequestValidationError discards input details, and domain validation messages do not interpolate refused mark values (errors.py:121; domain/capture.py:76). The new route introduces no logging. Live adjacency, ROUTE_INDEX adjacency/count and committed-entry equality are tested under D-700; the read-only OpenAPI check passed and the structural snapshot delta is only render. Mark processing shares annotate's validation/bake work; always-PNG encoding and the absence of a size cap are accepted contracts. No new input or resource restriction is imposed by this review.

## Q4 — COPY_KEY ownership and guards

Accepted. The key branch requires Ctrl or Meta, C, no Shift/Alt/repeat, no confirm, historyOwnsFocus, a noneditable target, collapsed selection and copyEnabled (CapturePage.tsx:1679). Recording, composition, text draft and crop return earlier. historyOwnsFocus excludes focused form controls, modal dialogs and focus outside the viewport/body; annotationOwnsFocus excludes confirm/color controls. Filmstrip/settings/other-panel controls therefore retain their keys. AC-104.12 exercises the listed guard rows with both no POST and defaultPrevented=false, then a positive control; AC-104.23 preserves RESERVED_CHORDS and the absent registry entry. Input/select and other-panel exclusions were additionally inspected in source rather than newly executed as UI probes. No rejected behavior.

## Q5 — COPY_BUTTON, RENDER_CLIENT and errors

Accepted. The ghost Copy image button is after Save annotations when dirty and before Flatten when clean, with the specified Ctrl+C hint and enable rule (CapturePage.tsx:481, :2128; capture-toolbar.ts:75). AC-104.13 posts current marks and asserts no annotate request. Both blob helpers use backendBaseAndToken, preserving base/token and the existing seam (capture-image.ts:1).

Missing IPC, refused render and schema refusal stop before clipboard invocation; a throwing IPC reaches reportCopy/copyErrorMessage. Undecodable or invalid converted image data fails the shared PNG conversion checks; main also refuses an empty nativeImage before clipboard.writeImage (capture-clipboard.ts:37, :55; main/clipboard-image.ts:10). Valid non-PNG images retain MEU-88's explicit conversion semantics; they are not categorically rejected. The new AC-104.14 tests and unchanged AC-88.4/.5 tests cover these layers without the real clipboard. No newly introduced path/value disclosure was found.

## Q6 — FILMSTRIP_AS_SHOWN

Accepted. onCopyImage selects annotated exactly for a nonempty string annotated_path and original otherwise (CapturePage.tsx:1848). AC-104.15 checks nonempty, null and empty values and the exact requested URLs. The image route serves the selected variant and its corresponding media type (routes/captures.py:415). AC-88.3 path-copy behavior, AC-88.4 PNG/conversion behavior and AC-88.5 encoded-ID/error behavior remain intact and are included in the matching UI gate. No rejected behavior.

## Q7 — ACTION_LABELS and SAVE_AND_FLATTEN

Accepted. The action names, confirm accepts, titles, statuses and Settings labels match D-694; the independent ui/src sweep found no retired names outside comments. applyState checks the current count/canSave when dirty and saved count when clean, with the prescribed priority and file-type/confirm rules (capture-flatten.ts:49).

Dirty accept checks canSaveRef, awaits saveAnnotations, rejects false, and only then calls flattenCapture (CapturePage.tsx:1924). A thrown save exits through run without flatten; false/refused save uses Save annotations first. AC-104.18 records annotate-before-flatten and a failed save with no flatten; the separate false-return/canSave refusal branches are verified here from source, not claimed as independently executed behavior tests. The dirty confirm correctly says the current marks are saved first. No evidence of wrong marks or flatten-before-save was found within the declared operation contract. Restore backup's dirty title and both Settings labels agree with the implementation.

## Q8 — COPY_HELP

Accepted. The help accurately describes current committed-to-editor marks, Ctrl+C focus/text-field ownership, the renamed actions, backup/format behavior and native text copy. The missing space before Right-click is fixed (capture-help-content.ts:22, :27); AC-104.20 checks the complete added sentence and names. No rejected behavior.

## Q9 — Tests, pins and Red evidence

Accepted. All 23 AC rows are present. Independently re-ran red-check against the three named Red receipts with all 19 task-row requirements: zero problems. Its 49 positive/negative fixtures also passed. The immutable-intent exceptions were checked: Departure 4 corrects the existing envelope's details=null field while keeping exact-envelope assertions; Departure 5 is Mat's D-700 ruling; Departure 6 repairs the Settings source path. No assertion was weakened by those data/path corrections.

The moved route counts/order, labels and action arrays match the approved delta. Departure 2's removeOnlyMark explicitly removes the sole saved mark and asserts an empty current list; TA-23/TA-24 still require a disabled button and a visible, correctly placed reason for an actual unmet rule (capture-inbox.test.ts:1464, :1603, :1634). TA-22 now expects the approved dirty-enabled behavior. No hidden skip or vacuous replacement was found.

| Test scope audited | IR-5 rating | Basis |
|---|---|---|
| Every test/parameter in test_capture_render.py | Strong | Exact signatures, format/byte comparisons, unchanged state, clamp equality, lock state, negative errors and real-stack pixels |
| Every test/parameter in test_api_capture_render.py | Strong | Real FastAPI/services/SQLite/Pillow, render-before-save oracle, exact validation envelope and schema adjacency/equality |
| New UI AC-104.11 to .16, .19 and .20 | Strong | Actual page events, exact current POST body/clipboard bytes, guard defaultPrevented checks, variant URLs and exact UI strings |
| New UI AC-104.1, .17, .18 and .23 | Adequate | Appropriate signature/state/registry guards; save success/failure behavior and source-confirmed false-return guard |
| New MCP AC-104.9 | Strong | REST_ONLY, ACTION_INDEX/path absence and rejected schema action |
| New Electron AC-104.22 and moved TA-22 to TA-24 | Strong | Real Electron labels/order, dirty confirm, disabled controls and real hover geometry; copy is never invoked |
| Changed capture-action-row, capture-flatten and capture-page.behavior assertions | Strong | Exact order/state/hint/status/behavior expectations retained or changed to D-693/D-694 |
| Changed API route-count, capture-page and help-content pins | Adequate | Static/count/content guards retain their purpose and are backed by behavior tests |

No test was graded Weak. Product runners were not re-executed during this read-only review; the matching fresh gate supplies their observed pass evidence.

## Q10 — Freshness, identity and records

Accepted. Independently recomputed exactly:

b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25

ELECTRON_RUN_AS_NODE was unset. A process-local core.excludesfile containing only the supplied .claude/settings.local.json exclusion reconciled the sandbox's unreadable user ignore; a process-local safe.directory handled sandbox ownership. Neither configuration file nor the excluded settings file was opened or changed.

Compared all eight evidence records with named baseline/row/Green/spec/status/D6 receipts and checked the full record against that state. Full step receipts confirm Python 2459 (2435 + 24), UI 1322 in 123 files, MCP 527 in 36 files and Electron 47. The 21 gate step records all have exit 0, no baseline failures were excused, and the gate ends with session-gate: all steps exit 0. AC-51.6's actual CRLF-sensitive prefix hash is unchanged: 6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454.

OpenAPI and MEU render read-only checks passed. The three spec/index files describe the delivered behavior; the old thumbnail IPC cell remains unchanged. Direct pre-status comparisons confine changes to MEU-104 fields/rendered status, the generated summary and grouping row 45. All 30 tracked modified files and three new tests match their declared CRLF/LF endings. Focus/handoff changes after the gate are excluded project artifacts by the approved identity contract. No rejected evidence or record claim.

## Q11 — Safety

Accepted for the new and changed paths. Python tests use generated media and isolated SQLite under tmp_path; UI fetch/clipboard functions are fakes; the new MCP check parses schemas/indexes; Electron uses its existing temporary app-data/fetch seam and never clicks Copy image or presses Ctrl+C. No new test reaches YouTube, the installed MCP servers or a download path. The unchanged AC-88.12 Electron clipboard test is excluded as directed.

Reviewer probes generated media/database files only beneath the assigned exec-review-tmp folder, used no HTTP client/server, and suppressed bake's inherited path-bearing informational logs while comparing bytes. Render itself emitted no log. Input refusal/error handling was inspected and probed without exposing refused text or original paths. No prohibited location or secret was opened. No rejected safety behavior.

## Checklist Results

| Check | Result | Observation method | Exit | Evidence |
|---|---|---|---|---|
| IR-1 live runtime/integration evidence | pass | Manual real-stack/Electron test and matching receipt inspection; observer codex-independent-reviewer | null | Real SQLite/Pillow/FastAPI integration and real Electron coverage passed at the independently matched state |
| IR-2 collaborator/stub behavior | pass | Manual test-helper audit plus independent real-SQLite probe; observer codex-independent-reviewer | null | Exact posted marks/returned bytes and persisted-state oracles; new UI clipboard calls are recording fakes |
| IR-3 error mapping | pass | Manual shared schema/mapper/error-handler audit plus missing/unreadable probes; observer codex-independent-reviewer | null | Matching 422/404 envelopes, path-free unreadable/missing-original messages and no clipboard on refusal |
| IR-4 generalization | pass | Manual caller/pin/diff audit; observer codex-independent-reviewer | null | Shared bake extraction, shared base/token helper and complete affected GUI label changes |
| IR-5 test rigor / AV-1 to AV-5 | pass | Per-test/parameter/changed-assertion audit; observer codex-independent-reviewer | null | Strong/Adequate ratings above, no Weak tests, all 19 required Red identities independently checked |
| IR-6 boundary validation | pass | Manual API/Zod/domain comparison and independent body/render probes; observer codex-independent-reviewer | null | Existing annotate constraints shared; malformed-body tests assert exact refusal envelopes; control-character parity preserved |
| IR-7 / AV-6 AC and deferral integrity | pass | Manual plan/handoff/source reconciliation; observer codex-independent-reviewer | null | All 23 ACs mapped; accepted decisions/exclusions honored; no concealed missing feature |
| DR/PR evidence, identity and records | pass | Independent identity/OpenAPI/status/audit commands below | 0 | Exact gate state/counts, sole OpenAPI path addition, confined records and preserved line endings |
| H2, commit and push | n/a | Outside this review boundary | null | Remain coordinator/human work after this review; no session-completion or commit judgment is made |

### Independently executed evidence

All uv invocations used --no-sync, -B, PYTHONDONTWRITEBYTECODE=1, RECEIPTS_DIR=C:/Temp/av-kit, TMP=TEMP=C:/Temp/av-kit/s69/exec-review-tmp, UV_CACHE_DIR beneath that scratch folder and UV_OFFLINE=1. Commands used rtk proxy, redirected streams under C:/Temp/av-kit, captured the child exit immediately and propagated it.

Initial environment/inspection attempts were corrected locally: uv's default cache was inaccessible; the sandbox Git owner required a process-only safe.directory; the OpenAPI --check flag required its path argument. Two reviewer audit assumptions were also corrected before its passing run: Python text reads normalized the CRLF-sensitive test-ID prefix, and this gate has 21 steps rather than the peer session's 22. These were reviewer scaffolding corrections, not changes to the repository or its evidence.

```json
{"schema_version":"evidence.v1","check_id":"s69-review-runtime","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s69-review-probe.py","scope":"Baseline bake compatibility, render byte equality/no writes/no logs, real SQLite render service, clamping/lock/errors, control-character parity","output":"baseline/current bake byte equality: 27/27; render/PNG bake equality: 9/9; no file or log from render. Unreadable original: fixed InboxPathError message with no path. Real SQLite service: posted marks clamped (90,-4)->(40,0); lock held; PNG under png/webp settings; existing annotated file, sidecar and row unchanged; unknown/missing refused. Control-character parity: 2/2 accepted bodies retain their text and render byte-equal to bake. s69 independent runtime probes: pass","cwd":"P:/av-kit","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25"}
```

```json
{"schema_version":"evidence.v1","check_id":"s69-review-identity","command":"$env:ELECTRON_RUN_AS_NODE=$null; $env:GIT_CONFIG_COUNT='2'; $env:GIT_CONFIG_KEY_0='core.excludesfile'; $env:GIT_CONFIG_VALUE_0='C:/Temp/av-kit/s69-review-git-ignore'; $env:GIT_CONFIG_KEY_1='safe.directory'; $env:GIT_CONFIG_VALUE_1='P:/av-kit'; rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-13-capture-copy-image/identity.py --state-only","scope":"Independently recomputed D6 state, with process-only sandbox ownership and the supplied secret-path exclusion","output":"b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25; equals handoff and full gate before/after","cwd":"P:/av-kit","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25"}
```

```json
{"schema_version":"evidence.v1","check_id":"s69-review-red","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-13-capture-copy-image/red-check.py --require test_ac_104_2 --require test_ac_104_3 --require test_ac_104_4 --require test_ac_104_5 --require test_ac_104_6 --require test_ac_104_7 --require test_ac_104_8 --require test_ac_104_10 --require AC-104.11 --require AC-104.12 --require AC-104.13 --require AC-104.14 --require AC-104.15 --require AC-104.16 --require AC-104.17 --require AC-104.18 --require AC-104.19 --require AC-104.20 --require AC-104.22 C:/Temp/av-kit/s69-py-red.txt C:/Temp/av-kit/s69-ui-red.txt C:/Temp/av-kit/s69-e2e-red.txt","scope":"All 19 required Red test identities, assertion diagnostics and preserved nonzero child exits","output":"red-check: 3 receipt(s), 19 required test(s), 0 problem(s)","cwd":"P:/av-kit","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25"}
```

```json
{"schema_version":"evidence.v1","check_id":"s69-review-red-selftest","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-13-capture-copy-image/red-check.py --selftest","scope":"Positive and negative Red-receipt fixtures","output":"red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong: []","cwd":"P:/av-kit","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25"}
```

```json
{"schema_version":"evidence.v1","check_id":"s69-review-audit","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s69-review-audit.py","scope":"Named receipts, handoff records, AC coverage, OpenAPI structural delta, pre-status comparisons, action labels, line endings and prefix hash","output":"30 tracked modified files and 3 new tests match declared CRLF/LF. AC-51.6/AC-81.13 prefix hash: 6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454. OpenAPI structural delta: only render path. Four pre-status comparisons: only intended MEU-104 fields/rendered status, summary and grouping row 45. Baseline/Red/Green counts confirmed. Full Python 2459 (2435+24), UI 1322/123 files, MCP 527/36 files, Electron 47; 21 successful step records; no baseline excuses; final line session-gate: all steps exit 0. Eight handoff evidence records inspected; all 23 AC rows present; full record matches independently recomputed state. GUI action-label sweep clean. s69 independent evidence audit: pass","cwd":"P:/av-kit","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25"}
```

```json
{"schema_version":"evidence.v1","check_id":"s69-review-openapi","command":"rtk proxy uv run --no-sync python -B tools/export_openapi.py --check openapi.committed.json","scope":"Read-only live/committed OpenAPI consistency","output":"No output; process exit 0","cwd":"P:/av-kit","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25"}
```

```json
{"schema_version":"evidence.v1","check_id":"s69-review-status-render","command":"rtk proxy uv run --no-sync python -B tools/meu_status.py render --check","scope":"Read-only MEU SSOT/render consistency","output":"Drift check passed — SSOT loaded (142 MEUs, 12 phases), rendered regions match on-disk content","cwd":"P:/av-kit","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25"}
```

## Verdict

approved — the delivered work achieves the registered intent. No Critical, High or other actionable finding survived verification. No corrections are required for round 1. The report is ready for the coordinator's byte-for-byte canonical adoption and ledger validation; H2 remains outside this review.

