---
date: "2026-11-08"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s58-plan-canonical-2026-11-08-capture-region-import"
round: 3
---

# Critical Review: 2026-11-08-capture-region-import

> **Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial.

## Intent Anchor

Session 58 lets an agent look at any part of a capture at full resolution and bring any local image into the capture inbox. `GET /captures/{id}/image` and MCP `image` take an optional region in original pixels or in fractions rounded outward. The region is clamped to the image and fitted inside `max_edge` (default 1568, at most 4× up) with Lanczos resampling. No file is written. The frame is reported in five response headers and, through MCP, in a text item before the image. `POST /captures` with `mode: import`, and MCP `capture` with `mode: import`, copy a local png, jpg, jpeg or webp into the inbox root as a new shot with source `Import`. An EXIF-rotated image is written as an upright PNG. A file already in the inbox root registers in place, and the source file is never changed.

## Findings

All findings have High confidence. F1 is the only approval blocker. No Critical finding.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | `IMPORT_ACCEPT` can accept a truncated JPEG, then `IMPORT_COPY` publishes it before the real `probe()` discovers the decode failure. Its `InboxPathError` escapes the specified cleanup handler, returns the destination path, and leaves a corrupt copy that also breaks the next inbox scan. Violates AC-129.8, AC-129.9 and `NO_RAW_CONSOLE`/AC-129.11 (family AC-129). | `implementation-plan.md:259-261`; `packages/infrastructure/src/avkit_infra/capture/adapter.py:257-263`; `packages/core/src/avkit_core/services/capture.py:312-322` | Decode before publication; translate failures to fixed messages; enclose final probe/UoW completion in cleanup. Add the truncated-JPEG and subsequent-list regression. | fixed |
| F2 | Medium | no | behavior | Finite whole px operands can overflow when summed before the outside-origin check: `x=1e308`, `width=1e308` makes `int(x+width)` raise `OverflowError`, yielding an internal error instead of `REGION_ERRORS`' 422. | `implementation-plan.md:175-183` | Use integer operands or safe pre-clamp arithmetic and test this case. | fixed |
| F3 | Medium | no | behavior | D-425's 15 MiB input-cap option does not guarantee whole-image readback: an accepted rotated JPEG can become an upright PNG larger than 15 MiB. | `human-gate-decision.md:14` | Qualify the benefit as applying to byte copies; keep `max_edge`/region as the fallback for normalized PNGs. | fixed |

Plan-relative references above are under `docs/execution/plans/2026-11-08-capture-region-import/`. These are delivery findings, not review-scaffolding or control-defeat findings.

## Scope

Reviewed the working-tree implementation plan, task, human briefs, design and grouping, Stage A region/import spec, MEU records, production call chains and tests, all five plan-local scripts, the review template and latest Session 55 peer review. HEAD independently reads `f69ee08cb682a409486835b27e432201dac02edb`. All 26 task rows are unstarted; no implementation result is asserted.

The user's accepted facts and deferrals remain accepted. D-407–D-424 are judged as autonomous choices, not approval requests. D-425 and D-426 remain open for Mat. External links were not fetched: this review was explicitly offline. No repository file was edited.

## Q1 — Goal and three calls

**MCP fraction view:** `{action:"image", id, x:0.25, y:0.25, width:0.5, height:0.5, unit:"fraction"}` on 3840×2160 passes the extended strict union, GET-only `withQuery`, the six route arguments and `read_image_view`. `resolve_region` yields `(960,540,1920,1080,false)`; `view_scale` is `1568/1920`; `CaptureAdapter.view` crops the original-resolution variant and Lanczos-resizes to 1568×882 in memory. Headers are `3840,2160`, `960,540,1920,1080`, `1568,882`, `0.816667`, `false`. `apiBinary` collects the headers; the registry returns frame text, then image. This normal chain is sound.

**Outside EXIF JPEG:** strict `CaptureImportIn` → import branch → accept/read/inspect → lock/name → upright PNG temporary file → replace → probe → `_upsert_shot(Import)` → UoW commit → 201. The row uses the written upright dimensions, and the source is read only. Valid files work; F1 identifies the failure branch the current AC set misses.

**Inbox-root PNG:** resolve parent against resolved inbox; inspect, then under the lock return/refesh the existing row with source preserved, or register the existing file as `Import`. No copy or transpose is made. This respects the expressly stated in-place exception and source immutability.

**Answer:** passing the current rows would not establish the whole goal safely, because F1 can survive every declared test.

## Q2 — Region resolution, errors and scale

Accepted the named error order and fixed 422s for partial region, unit alone, bad max_edge, non-finite values, negative origins, zero sizes, fractional px, fractions above one, outside origins and post-clamp edges under eight. Invalid unit/max_edge syntax is separately rejected by FastAPI. F2 is the extreme finite px exception.

The supplied float cases and independent arithmetic agree: 0.29×100 snaps to 29; odd dimensions still round outward. Products 1e-7 px below/above an edge round outward as expected. Products within the 9-decimal snap tolerance intentionally collapse to the edge: the prose claim that *no exact product changes* is mathematically too broad, but this sub-nanopixel tolerance has no material image-use consequence.

864 independent width/height/max_edge cases produced no returned edge below one, above max_edge, or above 4× the corresponding region edge. With no requested transform the original can exceed max_edge, intentionally preserving today's response.

## Q3 — Formats, unchanged bytes and variants

Accepted palette conversion before Lanczos, RGBA preservation, JPEG RGB/quality 90, and WebP quality 90 with alpha retained. `RETURN_UNCHANGED` preserves stored bytes for the whole image at scale one; the no-new-field route deliberately continues using `read_image` and does not decode it. This preserves existing callers, including AC-37.10's fake service.

The real `bake()` converts/draws without changing canvas dimensions (`adapter.py:275-286`), so the same source frame is valid for original and annotated variants. A stale file dimension mismatch is correctly a path-free 409; an unreadable/undecodable transformed view should be the fixed `InboxPathError` 422. Scanned EXIF behavior is expressly deferred and filed; it is not a new finding.

## Q4 — Headers, compatibility and OpenAPI

Accepted the no-parameter body/media-type guard, five headers on every 200, the route's `responses={200:{"headers":...}}`, and 413 guidance naming both max_edge and a region. An in-memory FastAPI app confirmed that all five header definitions survive OpenAPI generation. A route sweep confirms existing `responses=` use for 409s and no existing response-header documentation in routes.

S6 is feasible: row 3 adds only six query parameters and 200 header documentation; row 5 adds `CaptureImportIn` and its discriminated union references. No response-source enum component changes are needed because shot output source is already a string. Exporter `Path.write_text` produces CRLF on this Windows runtime, and rows 3/5 explicitly recheck it.

## Q5 — MCP shape and GET-only queries

Accepted `QUERY_GET_ONLY`: currently only capture image/list_requests schemas admit `variant`/`status`; neither belongs to a non-GET row. Other tool schemas do not depend on these query keys. Existing region POST coordinates remain in the JSON body through `httpBody`.

The schema's optional region fields and max_edge integer bounds agree with the API/domain split. Requiring all five parseable headers before emitting frame text preserves the fake/older API case. The audit client (`mcp-server/scripts/audit/client.ts:116`) and stdio test (`mcp-server/tests/image-over-stdio.test.ts:71`) find images by type. Adding a capture mode changes neither the 70-row index nor ten capture actions; `advertisedSchema` traverses all union branches and includes the added mode/fields.

## Q6 — Import acceptance, lock and upright copy

Accepted cheap checks before byte reads, following symlinks to regular files, rejecting directories, and translating read-sharing/permission failures to a fixed 422. Resolved direct-parent comparison separates an inbox-root file from a subfolder. UNC is an absolute Windows filesystem path under the stated acceptance rule; no UNC path was accessed in this review or prescribed as a test fixture.

No recursive lock acquisition was found: `probe`, `ensure_dir`, `_write_png` and `_upsert_shot` do not take `CAPTURE_FILE_LOCK`. Import uses `_upsert_shot`, not locked public scan methods. Holding the lock through publication/registration and UoW exit excludes the scanner; the temporary suffix is excluded too. The basic sequence avoids a scan race.

**Not accepted:** failure containment, F1. JPEG `verify()` does not guarantee a successful pixel decode; a reopened EXIF read does not fix that. The real probe's `InboxPathError` is outside the specified cleanup set. Database commit is on UoW exit (`unit_of_work.py:54-70`), so cleanup should enclose that boundary as well, not merely the temporary write. A 503 is appropriate for an actual write failure; corrupt source content should get the fixed 422 before publication.

Pillow's `exif_transpose` explicitly implements orientations 2–8 and loads before transpose; probing the final PNG yields its upright dimensions. This mechanism and the eight-orientation test design are accepted.

## Q7 — Names, in-place identity and Import readers

Accepted the bounded sanitized stem, reserved-name prefix and suffix search against both files and rows. On Windows, file existence checks catch case-only filesystem collisions; row-name comparisons must honor the same case-insensitive name contract, including stale rows. Resolved Windows Paths handle case, trailing separators and relative segments; a root-parent comparison excludes subfolders.

The persistence mapper writes `.name` and reconstructs the enum dynamically (`mappers.py:485-513`). API output source and renderer `CaptureListItem.source` are strings; no capture source label/filter whitelist was found. MCP forwards shot JSON. The plan explicitly updates all three member-list test tuples. No wire map or database migration is required.

## Q8 — Paths and Console

Accepted the existing `capture.registered` fields, and the production HealthService processor: it constructs its safe message from `CONSOLE_FIELDS`, then clears other event fields before downstream rendering (`health.py:207-235`). Thus `_write_png`'s `path` is discarded once HealthService is active. AC-129.11's actual stdout engine event and at least two registered ring events are meaningful positive controls; resetting `_active` and registering before scan addresses the existing lifecycle pitfalls.

**Not accepted:** the claim that every new refusal is path-free. F1 reaches the path-bearing existing probe error after publication, which the handler returns as a 422 detail (`errors.py:150-152`). This need not become a Console log to violate the plan's explicit error-message rule. Add that adversarial source to the AC-129.11/acceptance coverage.

## Q9 — Reds and guards

The region stubs make genuine assertion Reds possible; HTTP unknown queries and unsupported import mode reach assertions rather than collection errors. The `-k`, `-t` and required name boundaries match the listed titles. Non-required guards AC-128.9/.19 and AC-129.2 can pass during Red. Synthetic receipts exercised the actual parser: assertion accepted, AttributeError refused.

Two small construction notes should be made explicit before writing tests: AC-129.1 must assert membership/last-member before accessing `CaptureSource.Import.value`; and AC-129.4 must use Windows-legal source fixtures (`?` is not a legal ordinary filename, and `CON` needs a deliberate fixture strategy). Both can be repaired in Red setup without weakening the expectations; they are not approval blockers.

No demonstrated materially missing executable or gate that cannot fail was found. The final gate is fail-fast and compares input identities. F1 is a missing behavioral case, not a fabricated control-defeat mechanism. No product runner or plan selftest was executed here.

## Q10 — Endings, identity, scope and safety

Independent byte reads of 17 affected source/test/OpenAPI files match the declared CRLF/LF split. The scope allowlist matches Files Modified and project outputs, includes the new e2e module and spec/issue renders, and refuses test-id changes. Identity binds source/tests/config/locks, scripts, registers/renders, grouping and runtime inputs while excluding this session's later closeout documents. The full identity was inspected, not executed against the sandbox's differently ignored secret file.

The baseline parser reads the actual `id: MEU-125` entry and its `pending` status; strict execution is therefore refused now. The known Session 55 commit exists, and a waiver affects only the rc.2 status portion, consistent with the script's documented authority. Baseline/gate execution remains future authorized work.

Offline sync, fake MCP fetch, generated tmp_path images and targeted real Electron inbox checks are consistent with local-only implementation verification. No image-reading model probe is authorized or needed for this review. Existing test harnesses use temporary app data; no proposed feature requires writing a source file. This review wrote only under `C:/Temp/av-kit`, disabled Python bytecode, and blocked socket connections in its image probes.

## Human choices

D-425's options are implementable, but F3 corrects the 15 MiB option's claimed benefit: a 4,186,900-byte rotated JPEG produced an 18,750,276-byte upright PNG. Lowering the incoming cap does not itself cap normalized output. It remains Mat's choice whether to prefer 50 MB, 15 MiB or no incoming byte cap.

D-426 correctly discloses the missing reading probe and the judgement behind 4×; neither was treated as completed research. A 1024 default or explicit-only scaling can be implemented by changing the named constants/branch and corresponding AC/schema/docs before the authorized test cycle. The report does not choose either open decision or independently certify the external vendor/model research.

## Checklist Results

Manual observations below are by `codex-independent-reviewer`, exit code null. They derive from the line-numbered working-tree reads and call-chain comparison above.

| Check | Result | Procedure / decisive evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Compare rows 0–6 and H1/H2 with work packages and named contracts: scope/order agree. |
| PR-2 Not started | pass | All 26 task rows are `[ ]`; relevant production code remains pre-feature. |
| PR-3 Task contracts | pass | Rows specify owner, deliverable, exact validation and status; no process paperwork finding is raised. |
| PR-4 Validation realism | partial | Normal flows/guards have reachable checks; F1 lacks a source that verifies but cannot decode. Q9 records two small construction notes. |
| PR-5 Sources | pass | Inspect AC source labels and autonomous decision alternatives; no extra product scope imposed. |
| PR-6 Correction readiness | pass | Explicit two-MEU handoffs and rolling review; round-2 census is not applicable in round 1. |
| PR-7 Scope discipline | pass | GUI/crop MEUs exist; scanned EXIF defect is explicitly filed; no missing feature disguised as a deferral. |
| PR-8 Behavioral totality | fail | F1 traces a reachable import path to a path-bearing refusal and an orphan that poisons scans. F2 adds a non-blocking extreme numeric case. |
| PR-9 Single statement contracts | pass | Named contracts provide an operative canonical definition; no materially conflicting duplicate rule found. |
| DR / claim-to-state | pass | File anchors, exporter semantics, source consumers and supplied plan receipts compared against current files; future execution results not claimed. |
| Product suites / full gate | n/a | Explicitly prohibited for this review; not run. |
| Review write/egress boundary | pass | Issued-command audit: only temp writes, no app/suites/network/secrets/repository edits. |

### Decisive command evidence

```json
{"schema_version":"evidence.v1","check_id":"s58-independent-import-and-region","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s58_review_probe.py","cwd":"P:/av-kit","scope":"Plan inspection sequence applied in memory; real CaptureAdapter.probe; actual Red parser on synthetic receipts; temp-only files; PYTHONDONTWRITEBYTECODE=1; socket connections blocked","phase":"review","exit_code":0,"result":"pass","tested_state":"f69ee08cb682a409486835b27e432201dac02edb; working-tree Session 58 plan; Pillow 13.0.0; diagnostic reproduction only","output":"truncated_jpeg inspect_accepted=True orientation=1 probe_error=InboxPathError caught_by_planned_copy_handler=False raw_destination_in_detail=True copy_remains=True; px_overflow finite_inputs=True whole_inputs=True planned_resolver_error=OverflowError; Q1 region=[960,540,1920,1080] returned=[1568,882] scale=0.816667; Red AttributeError refused; AssertionError accepted. Exit 0 establishes reproduction, not a passing feature."}
```

```json
{"schema_version":"evidence.v1","check_id":"s58-independent-bounds-brief-and-bytes","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s58_review_more.py","cwd":"P:/av-kit","scope":"In-memory Pillow and FastAPI probes; byte/existence reads; baseline queue parser compared with actual YAML; no product runners or repository writes; PYTHONDONTWRITEBYTECODE=1; socket connections blocked","phase":"review","exit_code":0,"result":"pass","tested_state":"f69ee08cb682a409486835b27e432201dac02edb; working-tree Session 58 plan; installed Pillow/FastAPI; diagnostic reproduction only","output":"D425_input_jpeg_bytes=4186900 upright_png_bytes=18750276 input_under_15MiB=True output_over_15MiB=True; scale_cases=864 bound_failures=[]; FastAPI_response_headers=[X-Capture-Source,X-Capture-Region,X-Capture-Returned,X-Capture-Scale,X-Capture-Clamped]; affected file endings agree; five scripts exist; queue_ME125_detected_status=pending strict_accepts=False; task_rows=26 not_started=26."}
```

## Verdict

`changes_required` — one evidence-backed High delivery finding, F1. Correct through `/plan-corrections`, retain this loop and finding ids, then request round 2. F2 and F3 are non-blocking corrections. No repository change was made by this reviewer; the complete report is staged at the user-assigned temp path for the coordinator to preserve.

Residual limits: no live model reading probe, external research refresh, product-suite run or execution-gate certification. The disclosed legacy scanned-EXIF behavior remains the separately filed follow-up.

## Corrections Applied (2026-11-08)

Written by the plan's author acting as the corrections agent (`claude-opus-claude-code-coordinator`), not by a reviewer, for round 1 of loop `s58-plan-canonical-2026-11-08-capture-region-import`. The frontmatter verdict is now `corrections_applied`. Only the round-2 independent recheck can approve.

### Findings verified

3 confirmed, 0 refuted.

| # | Evidence | Result |
|---|---|---|
| F1 | `C:/Temp/av-kit/s58-corrections-verify.txt` | Confirmed. A 400×300 JPEG cut to 1,265 of its 2,530 B passes `verify()`, and `load()` raises `OSError: image file is truncated`. `CaptureAdapter.probe` (`adapter.py:253-263`) puts the path in both of its messages. The commit runs in `SqlAlchemyUnitOfWork.__exit__` (`packages/infrastructure/src/avkit_infra/database/unit_of_work.py:54-65`), outside the planned handler. |
| F2 | same receipt | Confirmed. `int(1e308 + 1e308)` raises `OverflowError`, and `int(x) + int(width)` gives a finite 1,025-bit `int` with `left >= 3840`. |
| F3 | the review's probe | Confirmed on its numbers: 18,750,276 B is over 15 MiB (15,728,640 B). |

Found while correcting F1 (same category, behavioral totality):

- `C:/Temp/av-kit/s58-corrections-verify2.txt`: a PNG with a damaged `IDAT` raises `SyntaxError`. That isn't an `OSError` and wasn't in the planned catch list, so it would have been an unhandled 500.
- `C:/Temp/av-kit/s58-corrections-verify3.txt`: under the error filter, `Image.open` itself raises `DecompressionBombWarning` (10000×10000) and `DecompressionBombError` (14000×14000). So the pixel-limit message has to come from those two exceptions, not from the later `w·h` check.

### Changes made

30 exact edits, each matched once (`C:/Temp/av-kit/s58-plan-corrections-r1.txt`).

- **F1**, in `implementation-plan.md`:
  - `IMPORT_ACCEPT`: `inspect_import` decodes in full, and nothing is written until every check passes.
  - `inspect_import`: `verify()`, then a reopen and `load()`. The bomb exceptions give the pixel-limit message, and any other exception gives the generic refusal through `except Exception` (precedent `grab`, `adapter.py:318-321`). The refusal table row and the Boundary Inventory row match.
  - `IMPORT_COPY` and the copy-branch bullet: one `try` encloses the whole unit of work, so it covers the write, `os.replace`, `probe(dest)`, `_upsert_shot` and the commit. Its `except Exception` (precedent `convert`, `services/capture.py:715-717`) removes the temporary file and, once `os.replace` has run, the copy. No row commits, and a fixed 503 follows. It removes no file the import didn't write.
  - `IMPORT_IN_PLACE`: a `probe` failure becomes the fixed `InboxPathError("the image could not be opened")`, the view's existing text, and the user's file is never removed. `NO_RAW_CONSOLE` now says no `probe` message reaches a response.
  - AC-129.8 adds the damaged-`IDAT` PNG and the half JPEG. After the JPEG it checks that the inbox holds no new file or `.avkit-tmp` and that `GET /captures` returns 200.
  - AC-129.9 is parametrized over three faults: `os.replace` raising, `CaptureAdapter.probe` raising with the path, and `SqlAlchemyUnitOfWork.commit` raising `RuntimeError`. Each fault is keyed on the copy's expected path, so earlier commits in the request still pass, and is lifted with `monkeypatch.context()` before the follow-up list. Each import gives 503 with no path in the body and leaves nothing behind, and the list returns 200.
  - D-417 and D-418: the chosen text, the precedents and the rejected alternative are updated.
- **F2**: the resolver adds Python `int`s (`right = left + int(width)`). `REGION_RESOLVE` and the region prose say so, and AC-128.4 gains `px-huge` (`x` and `width` of `1e308`, the `outside` message).
- **F3**: the D-425 brief's 15 MiB row, the gate summary (`:91`) and D-425's reasoning now say a byte copy reads back whole, and an upright PNG from a rotated JPEG can still pass 15 MiB.
- **Q9 notes**: AC-129.1 asserts membership and last place before it reads `.value`. AC-129.4's sources are Windows-legal: `a.b c#!.jpg` gives `a_b c.jpg`, and `CON!.png` gives `import_CON.png`, because `CON!` becomes the reserved `CON` only after sanitizing.
- **Q7 note**: `IMPORT_NAME` compares names with `casefold()`, stale rows included, and AC-129.4 adds a `Shot.PNG` from another folder that gives `Shot_3.png`.
- **Q2 note**: the D-408 prose and reasoning now say the guard moves a product by at most 5e-10, so it changes a result only for a product that close to a whole number.
- `task.md`: row 4a carries the AC-129.1, .4, .8 and .9 test construction, and row 5 names the full decode and the enclosing `except Exception`.
- The plan's planning receipts list the three probe receipts.
- Write scope: `human-gate-decision.md` is a plan-folder file that `/plan-corrections` doesn't list. F3 cites it by line, so it was corrected, and that is disclosed here.

Bytes, all LF with 0 CRLF: plan 89,593 to 94,653 B (`b7beb86c…` to `7363310e…`), task 43,939 to 44,467 B (`fca6f49a…` to `dca3d72d…`), brief 7,985 to 8,147 B (`31b8aa7c…` to `ea0e7651…`).

### Blast-radius census

The receipts are `C:/Temp/av-kit/census-s58-*-old.txt`, `*-new.txt` and `*-variant.txt` (29), each read in full. Line numbers are the plan's unless a file is named.

| Value | Sweeps | Result |
|---|---|---|
| px sum | `int(x + width)`; `int(x) + int(width)`; `int(width)` | The old form appears only where the prose names it as the overflow avoided (`:204`, `:882`). `:118`, `:177` and `:882` updated |
| decode | `verify`; `load()`; `verify()`; `SyntaxError` | `:253`, `:263`, `:372`, `:390`, `:707`, `:712-714` and `:882` updated. 09's precedent (`:710`) is consistent: 09 asks for `verify()`, which still runs. `task.md:59` (`meu_status` `load`) and `task.md:76` (verify the metrics row) are unrelated |
| cleanup | `` OSError` or `CaptureFailedError` ``; `except Exception`; `_unlink_if_file` | Old 0. `:261`, `:263`, `:731` and `task.md:57` updated |
| path in messages | `InboxPathError`; `could not be opened` | `:131`, `:262`, `:391` and `:735` updated. The `IMPORT_ACCEPT` table (`:246-252`), D-416 (`:691`), the view's open failure (`:210`), AC-128.10 (`:331`) and `task.md:53` are consistent |
| Windows-legal stem | `a.b c?`; `a.b c#!` | Old 0. `:386` and `task.md:55` updated |
| reserved name | `CON.png`; `CON!.png` | The one old hit is the output name `import_CON.png` (`:386`), which is consistent. `:386` and `task.md:55` updated |
| case | `neither a file nor a row`; `casefold`; `Shot` | Old 0. `:132`, `:386` and `task.md:55` updated. `:240` (`CaptureShot`) is unrelated |
| read-back | `every imported original`; `byte-copied`; `15 MiB` | Old 0. Brief `:14`, `:91` and `:839` updated. `:126`, `:456`, `:831` and brief `:7` and `:20` are consistent: they state the outgoing caps |
| guard | `no exact product`; `5e-10` | Old 0. `:204` and `:577` updated |
| AC-129.9 faults | `` os.replace` patched ``; `three faults` | Old 0. `:391` updated |
| px-huge | `px-huge`; `1e308` | `:204`, `:325` and `:882` updated |

Blast-radius census: 10 values changed, 8 variants swept, 47 sites found, 27 updated, 17 confirmed consistent, 3 unrelated text matches.

Cross-doc sweep: 4 files checked (09, the design, the grouping and AGENTS.md), 0 updated. 09 `:1009` and design `:213` require `verify()` to pass. The full decode is stricter and still meets them, and both are Stage A files whose SHA-256 the plan pins.

### Verification

- `lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier`: OK, 26 rows (`C:/Temp/av-kit/s58-plan-task-lint-r1c.txt`).
- `red-check.py --selftest`: 36 fixtures, 0 wrong (`C:/Temp/av-kit/s58-plan-redcheck-selftest-r1c.txt`). `identity.py --selftest`: 0 failures (`C:/Temp/av-kit/s58-plan-identity-selftest-r1c.txt`).
- Decision probe: 27 decisions, no issues (`C:/Temp/av-kit/s58-decision-issue-probe-r1c.txt`).
- The `issue-file.py` dry run wasn't run again, because nothing it reads changed.
- No suite, build, app or network request was run.

### Round 2

The ledger refuses round 2 on the token reserve: 5,717,501 spent plus 5,717,501 reserved for the next round is more than the 10,500,000 budget. Mat's `continue` is needed before the recheck is dispatched.

### Human-gate briefs refreshed (Mat's 2026-11-08 request)

Mat wrote: "1. tripple the token budget and allow 2 extra rounds on top / For 2 3 4 run HDP and give me recommendations again". The plan's author did this after the corrections above, before round 2, so the recheck reads the briefs as they stand.

- **Ledger.** Mat's continue is recorded: a 31,500,000-token budget (5,717,501 spent) and 5 rounds (1 used), so round 2 is permitted. This replaces the Round 2 note above.
- **D-425.** A second precedent sweep and two searches. No av-kit cap on incoming files exists; the tree's three byte caps bound outgoing images and text reads. The class changes from `product-preference` to `governance-value` (HDP §4 test 4). The recommendation is unchanged (50 MB). New sources: the Claude Help Center, ChatGPT's 20 MB per image (otio.ai, quoting OpenAI), and ImageMagick's discussion 6068 and sample security policy.
- **D-426, a correction.** The brief said 1568 is the long edge a Claude model keeps, and D-426 said the default "wastes nothing". The vision page puts Claude 4.7 and later on the high-resolution tier (2,576 px, 4,784 visual tokens). The design's R-1 (`design.md:98`) already says so, and 09 states only the numbers, so neither changes. The brief, D-426, D-409's source and reasoning, and the plan's problem statement (`:28`) now say so. The recommendation is unchanged and is restated as a cost choice: at most 3,136 visual tokens per default view, and 2576 on request. The 1024-default row is replaced by two rows, a 2576 default and the limits arXiv 2610.09313 measured (1,024 px, at most 2×). The class changes to `governance-value`. The reading probe still hasn't run.
- **D-427, new.** It asks whether Stage A's seven files are committed before execution. Recommended: one exact-scope commit now, without the plan folder, this handoff or a push (precedent D-276, `83229ea`). If Mat doesn't answer, nothing is committed. The plan copes with either outcome (`:99`).
- **Edits** (`C:/Temp/av-kit/s58-hdp-refresh.txt`), all LF with 0 CRLF.
  - The brief was rewritten: 8,147 to 19,154 B (`ea0e7651…` to `c964045b…`).
  - The plan went from 94,653 to 101,056 B (`7363310e…` to `f79ca19a…`). Changed: the gate summary (`:90-95`), `:28`, `:62`, `:99`, the Decision Log intro (`:540`), D-409, D-425 and D-426, the new D-427 (`:868`), the Research References (`:896`) and the Planning receipts (`:913`).
  - The task went from 44,467 to 44,529 B (`dca3d72d…` to `dc82d2bb…`): H1-7's vocabulary and H2-2's decision list.
  - The seven Stage A files' SHA-256 were read again, and all match the values the D-427 brief lists.
- **Census** (`C:/Temp/av-kit/census-s58-hdp.txt`). Swept: "two questions", "D-407 to D-426", "wastes nothing", "throw away", "a 1024 default", "product-preference", "standard tier's", "model's own long edge", "rest on the vision documents alone" and "D-425 and D-426". One stale hit was found and fixed (task H1-7). Every other hit is the new text.
- **Verification.**
  - `lint_task_contract.py`: OK, 26 rows (`C:/Temp/av-kit/s58-plan-task-lint-hdp.txt`).
  - Decision probe: 28 decisions, with D-427 parsed (`C:/Temp/av-kit/s58-decision-issue-probe-hdp.txt`).
  - `identity.py --selftest`: 0 failures. `red-check.py --selftest`: 36 fixtures, 0 wrong (both `C:/Temp/av-kit/s58-plan-*-selftest-hdp.txt`).
  - No suite, build, app or model was run.
## Recheck (2026-11-08)

**Workflow**: `/planning-corrections` recheck
**Agent**: codex-independent-reviewer

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | open | ✅ Fixed |
| F2 | open | ✅ Fixed |
| F3 | open | ✅ Fixed |

### Confirmed Fixes

References to `implementation-plan.md`, `task.md` and `human-gate-decision.md` below are under `docs/execution/plans/2026-11-08-capture-region-import/`. This is an independent plan recheck; the author's corrections and refreshed briefs are evidence to check, not reviewer approval.

- **R1 / F1 — fixed (`IMPORT_ACCEPT`, `IMPORT_COPY`, `IMPORT_IN_PLACE`, `NO_RAW_CONSOLE`).** `implementation-plan.md:129-135` and `:254-264` now require verify, reopen and full load before any write. This decodes the same pixels that the real `probe` loads (`packages/infrastructure/src/avkit_infra/capture/adapter.py:253-263`); the byte-copy branch writes those inspected bytes. The half JPEG is refused by load, the damaged-IDAT PNG's `SyntaxError` is caught by the generic refusal, and the 10000×10000 warning and 14000×14000 error raised during open both select the pixel-limit refusal. The Pillow source agrees (`.venv/Lib/site-packages/PIL/Image.py:1005`, `:3577`, `:3608`). Independent diagnostic probes reproduced all four cases.
- **R1 / cleanup and exposure — accepted.** The try explicitly encloses the whole UoW, including its exit-time commit (`implementation-plan.md:262`; `packages/infrastructure/src/avkit_infra/database/unit_of_work.py:54-65`). It covers write, replace, final probe, upsert and commit. Removal is restricted to this import's temporary file and its copy after successful publication; it never removes the source or an in-place file. The fixed 503 is unlogged; in-place probe errors become the fixed 422 (`implementation-plan.md:263`; `packages/api/src/avkit_api/errors.py:138-152`). No raw probe message is passed onward. The existing Console processor drops `capture.wrote`'s path field before stdout, ring, disk or downstream rendering (`packages/core/src/avkit_core/services/health.py:207-235`). A diagnostic using real `SqlAlchemyUnitOfWork.__exit__` and in-memory SQLite left zero rows, no copy and no temporary file after injected write, replace, probe, upsert and commit failures; its success control left one row and one copy. This checks the proposed boundary, not a feature implementation.
- **R1 / Red-to-Green coverage — accepted.** AC-129.8 and .9 (`implementation-plan.md:391-392`; `task.md:55`) have genuine assertion Reds today: unsupported mode yields the wrong envelope/message, and .9 first asserts the missing callable. Green requires the listed refusals, 503s, cleanup, absence of a row and a successful follow-up list. The three faults are scoped to the expected copy path; the commit fault starts only once that copy exists, allowing earlier request commits. `monkeypatch.context()` is lifted before listing. None of these requirements needs weakening in row 5.
- **R2 / F2 — fixed (`REGION_RESOLVE`, `REGION_ERRORS`).** Integer conversion precedes addition (`implementation-plan.md:119`, `:175-205`). Python integer addition has no finite-float overflow; both coordinates remain exact integers for every accepted finite whole px input. AC-128.4's `px-huge` expects the outside-origin message (`:326`). A 30-case finite-whole operand probe, including the largest finite float, confirmed this reasoning.
- **R3 / F3 — fixed.** The brief, gate summary and D-425 reasoning consistently restrict whole-image readback to byte copies and disclose that upright PNGs may exceed 15 MiB (`human-gate-decision.md:16`; `implementation-plan.md:91`, `:846`). The recorded 4,186,900 B JPEG to 18,750,276 B PNG counterexample is stated accurately. This does not promise readback through MCP's smaller byte cap.
- **R4 — accepted.** D-408 now describes the 5e-10 guard tolerance (`implementation-plan.md:205`, `:578`). `IMPORT_NAME` uses casefold against files and all rows, including stale rows (`:133`); `Shot.PNG` therefore advances to `Shot_3.png` (`:387`). Membership/last-place assertions precede `.value` (`:384`). The Windows-legal fixtures sanitize as claimed: `a.b c#!.jpg` to `a_b c.jpg`, and `CON!.png` to `import_CON.png`. The Red row carries these requirements (`task.md:55`).

**R5 / D-425 — accepted with the disclosed scope.** The current source sweep confirms the API's 15,728,640 B and MCP's 7,800,000 B caps apply to returned images (`routes/captures.py:266`; `mcp-server/src/toolsets/registry.ts:351`), and `COMPILE_READ_MAX_BYTES` bounds transcript text reads (`packages/core/src/avkit_core/services/transcript.py:375`). They are not incoming media-file caps. The brief correctly separates these from the proposed local import cap (`human-gate-decision.md:19-43`). ImageMagick's saved snippets support resource-policy limits and the sample's 8192 px rule; they do not establish this machine's active ImageMagick configuration. The Claude Help and secondary ChatGPT upload claims match their saved snippets. No new byte cap, 15 MiB and 50 MB remain Mat's choices; changing/removing the import check leaves region readback available and requires the corresponding cap case to follow the ruling before Red.

**R5 / D-426 — accepted.** The saved official vision and coordinate snippets support the 4.7-and-later tier, 2576 px, 4784 tokens and ceil(w/28) × ceil(h/28). Independent arithmetic gives 3136 at 1568×1568, 1792 at 1568×882, 777 at 1024×576 and 4784 at 2576×1449. The saved arXiv 2610.09313 excerpt supports 1024/2× and the differing enlargement/native-pixel results; it does not establish a universal optimum. The 2576-default and measured-study options are honestly separated from the recommendation (`human-gate-decision.md:47-85`). D-409 and the problem statement agree (`implementation-plan.md:28`, `:592-595`, `:861-866`). The missing reading probe remains explicit. A different ruling changes the named default/cap or default-scaling branch and its dependent AC/schema/description values before Red; no additional feature or dependency is needed.

**R5 / D-427 — accepted.** All seven SHA-256 values match the working-tree bytes (`human-gate-decision.md:100-106`). A pre-row-0 commit changes HEAD, not those bytes; baseline records that new HEAD and the remaining dirty paths (`baseline.ps1:78-93`). Without that commit it records Stage A's dirty bytes instead. The S3 checks protect not-yet-written baseline files (`task.md:38`, `:59`, `:62`); the gate admits baseline paths and compares against baseline HEAD (`session-gate.ps1:70-91`), and identity binds the resulting diff/untracked inputs and HEAD (`identity.py:106-115`). Thus neither option invents a clean-tree requirement or makes the plan unable to run. The queue still applies independently, and an unanswered D-427 authorizes no commit. One wording qualification: the register diff also updates phase-9 date/note and P2 summary-range metadata for this registration, not literally just five appended records; it changes no unrelated MEU status. Read the brief's “nothing else” (`:101`, `:132`) in that registration scope.

**R6 — accepted.** I decoded all saved census receipts, matched their complete hits to current text, and read the current plan, task and brief in full. The superseded arithmetic and catch-list strings remain only in explanations of the rejected approaches. Full decode, failure messages, casefold naming, numeric defaults and task validation agree. I also checked refreshed text directly rather than relying on the clipped HDP hit previews. A non-blocking shorthand omission remains in `task.md:34`: its fixture-id list stops at the original eight refusal ids, while the complete AC-129.8 contract and row 4a explicitly add the damaged PNG and half JPEG. The same row's complete requirements govern; no required behavior is lost.

**R7 — accepted.** No newly introduced High or Critical delivery failure was found. The unchanged no-field image path, five headers, MCP frame-before-image shape, GET-only query forwarding, source enum readers, upright copy and source immutability remain consistent with the round-1 accepted call chains. No option in the three briefs requires a new dependency or omitted work package. Open decisions D-425 to D-427 remain with Mat; this approval does not rule them, authorize execution, waive the queue or authorize a commit.

Independent diagnostic command: `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s58_r2_probe.py`, with `PYTHONDONTWRITEBYTECODE=1`, exit 0. Decisive output: four corrupt/oversize cases refused as specified; five cleanup failures left zero rows/copies/temporary files; success control left one row/copy; 30 px arithmetic cases passed; all seven Stage A hashes matched; all 26 task rows remain unstarted. Product suites, baseline, session gate, app, model reading probe and network were not run. Only temp files were written.

External verification limit: refreshed claims were checked against saved search excerpts, not live pages or full fetched papers. The inherited Gemini/Hermes/typical-size and older ViCrop citations were not independently reread from full sources here. The ImageMagick policy discussion describes configurations, not a verified local policy. These limits do not conceal a demonstrated delivery defect.

Current checklist: PR-1 through PR-9 and the claim-to-state check pass for this plan recheck; product/full-gate execution is n/a. The two wording qualifications above are observations, not open findings.

Artifact verification: the complete prior handoff is byte-preserved except for the authorized frontmatter/status edits, and the output has CRLF throughout. `validate_closeout_artifacts.py --review-state-only` exits 0 and recognizes plan/round 2/approved, but records a synthetic open count of 1: `_latest_round_open` requires a separate Findings table (`tools/validate_closeout_artifacts.py:584-586`), which the user-prescribed Remaining Findings/None layout does not supply. I retained the requested layout. This is a coordinator tooling note, not a delivery finding or evidence of an open F1.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Remaining Findings

None.

### Verdict

`approved` — F1, F2 and F3 are fixed. Executing the corrected plan would deliver the registered intent, subject to Mat's existing execution gate and the stated queue. No open High or Critical finding remains.

## Corrections Applied (2026-11-08, after round 2)

Written by the plan's author acting as the corrections agent (`claude-opus-claude-code-coordinator`), not by a reviewer. Round 2 above is the reviewer's verdict, copied here byte for byte from `C:/Temp/av-kit/s58-plan-review-round-2.md`. Its review-state receipt is `C:/Temp/av-kit/s58-plan-review-state-r2-canonical.json`: verdict approved, round 2 of 5, open findings 1. The frontmatter verdict is now `corrections_applied`, because the plan's bytes changed after the approval. Only the round-3 independent recheck can approve again.

### Why a round 3

- **The approval can't pass the approved-state gate as written.** `_latest_round_open` (`tools/validate_closeout_artifacts.py:562-587`) needs each recheck section to hold its own `Findings` or `New Findings` table. A section without one counts as one open finding, and no later round is read. The round-2 prompt prescribed a layout without that table, so the omission is the coordinator's, not the reviewer's. The reviewer reported it under Artifact verification. An in-memory probe (`C:/Temp/av-kit/s58-r2-table-probe.txt`) reads open findings 1 as written and 0 once the section holds an empty `New Findings` table with the REVIEW-TEMPLATE header. The coordinator doesn't add that table, because it is the reviewer's text.
- **The two wording qualifications in R5 and R6 are corrected**, so that round 3 can check them.

### Changes made

Three exact edits, each matched once (`C:/Temp/av-kit/s58-plan-corrections-r2.txt`).

- **D-427, `meu-status.yaml`** (`human-gate-decision.md:101`, `:132`). Confirmed against `git diff -U0 .agent/context/meu-status.yaml`: besides the 133 added MEU-128 to MEU-132 lines, the diff changes phase 9's `last_updated` (`:113`) and note (`:118`) and the P2 summary band's range (`:3488`), and no other MEU. Read literally, the old step 1 ("adds only MEU-128 to MEU-132") would have stopped the commit Mat approved. The table row and step 1 now name those three fields.
- **AC-129.8's ids** (`task.md:34`). The list now ends `bomb-warn`, `bomb-error`, `bad-idat` and `half-jpeg`, matching the AC-129.8 contract (`implementation-plan.md:391`) and row 4a (`task.md:55`). No selector or `--require` name uses these ids.

Bytes, all LF with 0 CRLF: brief 19,154 to 19,357 B (`c964045b…` to `30872d7d…`), task 44,529 to 44,554 B (`dc82d2bb…` to `9f39924d…`). The plan is unchanged at 101,056 B (`f79ca19a…`).

### Blast-radius census

`C:/Temp/av-kit/census-s58-r2c.txt`. Swept the plan folder for "nothing else", "adds only MEU", "`bomb-warn` and" and "three fields". The old forms are gone, and the only hit is the new step 1 (`human-gate-decision.md:132`). `bomb-warn` and `bomb-error` appear only at `task.md:34`.

Blast-radius census: 2 values changed, 2 variants swept, 3 sites found, 3 updated, 0 confirmed consistent, 0 unrelated text matches.

### Verification

- `lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier`: OK, 26 rows (`C:/Temp/av-kit/s58-plan-task-lint-r2c.txt`).
- The seven Stage A files' SHA-256 were read again, and all match the D-427 table.
- The decision probe and the selftests weren't run again, because neither the plan nor the scripts changed.
- No suite, build, app or network request was run.

## Recheck (2026-11-08)

**Workflow**: `/planning-corrections` recheck
**Agent**: codex-independent-reviewer

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | fixed | ✅ Fixed |
| F2 | fixed | ✅ Fixed |
| F3 | fixed | ✅ Fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Confirmed Fixes

Plan-relative references in this section are under `docs/execution/plans/2026-11-08-capture-region-import/`. This round reviews only the three post-round-2 wording edits and their affected references. The round-2 delivery findings remain fixed; no unchanged accepted behavior was reopened.

- **S1 — confirmed.** D-427's description and step 1 now match the actual register diff (`human-gate-decision.md:101`, `:132`): five new MEU-128 to MEU-132 records, phase 9's `last_updated` and note, and the P2 summary band's range (`.agent/context/meu-status.yaml:113`, `:118`, `:3346`, `:3488`). The diff contains no other MEU change. All seven SHA-256 values still match the brief's table (`human-gate-decision.md:100-106`). Today's bytes therefore pass step 1. The wording still says "only" and "If anything differs, stop", and the unchanged hash checks also refuse an unrelated change. An in-memory probe accepted today's allowed delta and rejected both an unrelated MEU-127 status mutation and a phase-8 note mutation. This is a check of the stated guard, not an installed new gate or an authorization to commit.
- **S2 — confirmed.** The ten IDs at `task.md:34` now cover exactly the AC-129.8 refusal cases, including `bad-idat` and `half-jpeg` (`implementation-plan.md:391`), and agree with row 4a's damaged-PNG/cut-JPEG construction (`task.md:55`). The selectors use `-k ac_129` and `--require test_ac_129_8`, not individual parameter IDs (`task.md:55`). The Red checker matches base test titles and examines every matching failure block (`red-check.py:214-215`, `:264-272`); the four explicit IDs `bomb-warn`, `bomb-error`, `bad-idat` and `half-jpeg` occur only in the naming list. No selector or required-name update follows from this edit.
- **S3 — confirmed.** No contradiction was introduced. D-427 still names the same seven-file, hash-checked scope, leaves no-answer as no commit, and excludes execution and push (`human-gate-decision.md:129`, `:132-136`; `implementation-plan.md:93-99`, `:868-878`). The task's baseline/S3 protection remains compatible with either commit timing (`task.md:38`). The AC-129.8 edit supplies names for cases already required by the contract and row 4a; it adds no new behavior or changed expectation (`implementation-plan.md:391`; `task.md:55`). The unchanged implementation plan is 101,056 bytes, SHA-256 `f79ca19a193eb87d29e9ef46591a71eba6efe3846ade7b29788288feb709f478`.

Independent evidence: `rtk proxy git diff -U0 -- .agent/context/meu-status.yaml`, exit 0, yielded the five appended records and the three named metadata fields. `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s58_r3_probe.py`, with `PYTHONDONTWRITEBYTECODE=1`, exit 0, confirmed the allowed-delta positive case, two rejected in-memory negative cases, all seven matching hashes, the ten AC-129.8 IDs and the unchanged plan hash. Targeted `rtk proxy rg -n` censuses of the plan folder and selector-bearing plan/task/scripts each exited 0; their matching references were read directly for S3. These are read-only plan checks, not product implementation evidence. No product suite, baseline, session gate, app or network request ran. Only files under `C:/Temp/av-kit` were written.

The rolling report preserves every canonical section, including the author's post-round-2 Corrections Applied section. Apart from the requested frontmatter fields, the only prior-text edit is the authorized empty New Findings table immediately before round 2's Remaining Findings heading. The generated report uses CRLF throughout. The canonical repository handoff is unchanged and remains for the coordinator to replace after validating this report.

### Remaining Findings

None.

### Verdict

`approved` — The three edits are accurate and consistent with the accepted plan. F1, F2 and F3 remain fixed, and no new concrete delivery failure was found. Executing the plan would deliver the registered intent, subject to Mat's existing execution gate and the stated queue. D-425, D-426 and D-427 remain Mat's open decisions; this review does not decide them or authorize a commit, push or execution.

## Coordinator Record (2026-11-08, after round 3)

Written by the plan's author (`claude-opus-claude-code-coordinator`), not by a reviewer. Round 3 above is the reviewer's approval, and the frontmatter verdict stays `approved`. This section records Mat's rulings and the D-427 commit. It makes no plan correction.

### Mat's rulings

Mat's message on 2026-11-08, "all recommendations accepted", rules each of the three gate questions as recommended:

- D-425: `IMPORT_MAX_BYTES = 50_000_000` (50 MB).
- D-426: `max_edge` 1568 by default, 64 to 2576 allowed, and a region enlarged at most 4×.
- D-427: commit Stage A's seven files now, in one exact-scope docs commit, with no push.

Each ruling is recorded under its brief in `human-gate-decision.md` and in the plan's Decision Log. There, `chosen` is the ruled option, `source_tag` is `Human-approved`, and `human_message_reference` is `USER_EXPLICIT 2026-11-08 'all recommendations accepted'`. Each entry's reasoning is unchanged. The plan text that called the questions open, D-425 pending or the crop docs uncommitted now says they are ruled and committed (`:20`, `:90-95`, `:99`, `:241`, `:407`, `:540`). No AC, task row, script or command changed, because the plan already carried the recommended values.

- The plan went from 101,056 B (`f79ca19a…`), as round 3 approved it, to 101,152 B (`f2acb955…`). The brief went from 19,357 B (`30872d7d…`) to 20,132 B (`85737f29…`). Both are LF, with 0 CRLF. `task.md` is unchanged at 44,554 B (`9f39924d…`).
- Receipts: `C:/Temp/av-kit/s58-record-rulings.txt`, `s58-record-commit.txt` and `s58-record-push.txt` (the edits, each matched once). `lint_task_contract.py` passes on 26 rows (`s58-plan-task-lint-rulings.txt`). The decision probe reads all 28 decisions with no refusal (`s58-decision-issue-probe-rulings.txt`).

### The D-427 commit

- Step 1 passed just before the commit (`C:/Temp/av-kit/s58-d427-precheck.txt`). HEAD was `f69ee08`, and all seven SHA-256 values matched the brief's table. `meu-status.yaml`'s diff held only the MEU-128 to MEU-132 records and the three fields.
- The commit is `75617379f63c0885024b2c9f0dd9fc72de854b8b`, made in the exact-scope signed commit mode with `-NoPush` (`C:/Temp/av-kit/s58-d427-exact-scope-commit.txt`, `s58-d427-commit-state.json`). Its parent is `f69ee08` and its tree is `ed4af385…`. It holds seven files: 1,040 insertions and 9 deletions.
- The author and committer are both `MatBanik <219344396+matbanik@users.noreply.github.com>`. The signature is verified, and the message has no AI attribution trailer. Subject: `docs(capture): record the crop design, MEU-128 to MEU-132 and their session grouping`.
- Mat then directed the push separately: "push and wait we will complete 56 and 57 first than resume executino for 58 here". `git push origin main` sent `2963efe..7561737`, which carried Session 55's `f69ee08` and this commit (`C:/Temp/av-kit/s58-push.txt`). `main` now matches `origin/main`.
- As D-427 requires, three things stay untracked: this plan folder, this handoff, and `docs/execution/plans/2026-11-08-light-accent-contrast/`.

### Still not authorized

Execution has not started. Row 0 still refuses until Session 57 (MEU-125, rc.2) is `approved`, unless Mat waives the queue in words (`baseline.ps1 -QueueWaived`). Mat's order is that Sessions 56 (`light-accent-contrast`, MEU-126) and 57 complete first, and Session 58's execution resumes after them. Row 0 checks Session 57 but not Session 56, so the coordinator confirms that Session 56 has landed before running it.
