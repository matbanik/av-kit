---
project: "2026-11-15-capture-inbox-probe"
date: "2026-11-15"
source: "grouping .agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md §3 Session 75; issues CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST (triage D-802; filed by D-507) and CAPTURE-EXIF-SCANNED-ORIENTATION (triage D-803)"
meus: ["MEU-145", "MEU-146"]
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
---

# Implementation Plan: List past unreadable inbox files and honour EXIF orientation

> **Project**: `2026-11-15-capture-inbox-probe`
> **Build Plan Section(s)**: 09 [§Scan skips unreadable files](../../../build-plan/09-screenshot-capture.md#scan-skips-unreadable-files) (MEU-145, matrix 9.43) and 09 [§EXIF orientation on scan](../../../build-plan/09-screenshot-capture.md#exif-orientation-on-scan) (MEU-146, matrix 9.44)
> **Status:** said to execute (USER_EXPLICIT 2026-11-15 'proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions.'). `plan_to_exec_gate: human`; the plan review was approved at round 3 (.agent/context/handoffs/2026-11-15-capture-inbox-probe-plan-critical-review.md).

---

## Goal

**Goal anchor:** one inbox file that the probe cannot read never fails the capture list: every readable shot still lists through the API and MCP, the bad file is skipped with a fixed, path-free message and one count-only log line, and it is tried again on the next scan. A scanned or registered JPEG, MPO or PNG with an EXIF orientation tag is recorded, viewed, downloaded, copied, marked, cropped, baked and exported in the frame the GUI shows, an annotated copy baked in another frame is rebaked by the next scan, and the user's file is never rewritten.

This is Session 75 of the post-rc.3 grouping (§3: "both change how the inbox scan reads a file through `probe`, in the same function"). Order: MEU-145, then MEU-146 (grouping §3).

**MEU-145 (`CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST`).**

- `CaptureService.scan_inbox` (`services/capture.py:597`, not `:466` as 09's note says) holds `CAPTURE_FILE_LOCK` and calls `self._annotate.probe(resolved)` (`:610`) with nothing caught. So one bad file fails `GET /captures` and MCP `list` (`mcp-server/tests/capture.test.ts:24`, `GET /captures`).
- `CaptureAdapter.probe` (`capture/adapter.py:461`) raises `InboxPathError(f"{path} is not a file")` (`:464`) and turns `UnidentifiedImageError` and `OSError` into `InboxPathError(f"{path} is not an image")` (`:469-470`). Both messages hold the path, and a 422 carries it to the Console. A PNG with a damaged IDAT makes Pillow raise `SyntaxError`, which is neither, so the list answers 500 (plan probe `s75-plan-probe-pillow.txt`).
- `bake` (`:603`, message `f"{original_path} is not an image"` at `:616-617`) and `render` (`:623`, misses `SyntaxError`) have the same gaps. `view` (`:473`) and `crop` (`:549`) already catch `Exception` into the fixed `"the image could not be opened"` (D-421).
- AC-130.21 (`tests/e2e/test_api_capture_crop.py:763`) restores the source before its follow-up list for exactly this reason (`:779-781`).

**MEU-146 (`CAPTURE-EXIF-SCANNED-ORIENTATION`).**

- `probe` records `image.size`, the stored frame. Chromium (Electron 42.11.18, Chrome 148) shows a tagged JPEG and PNG turned, and never turns a WebP (plan probe `s75-plan-probe-electron.txt`). So a JPEG or PNG tagged 5 to 8 lists 400x300 while the GUI shows 300x400, and every mark, region and crop given in the shown frame lands in the wrong place or is refused by the size check (409).
- `view`, `crop`, `bake`, `render` and `export` (`:679`) open the stored pixels, and `_encode_view` (`:368-382`) drops the colour profile. Pillow's `getexif()` also reads a tag from XMP and from a PNG text chunk, which Chromium ignores (`s75-plan-probe-extra-electron.txt`). Only `write_upright_png` (`:539`, imports, D-417) applies `exif_transpose`. AC-136.7 (`tests/unit/test_capture_export_adapter.py:672`) records the stored-frame export as a characterisation of this issue (D-613).
- A row already scanned keeps its stored width and height: the scan (`:629`), `_upsert_shot` (`:2119`) and `_import_in_place` (`:754`) update a row only when the file size changes, and turning the frame does not change the size.
- The no-parameter `GET /captures/{id}/image` (`routes/captures.py:429-431`) returns the file's bytes while its `X-Capture-*` headers give the row's frame. The MCP image call with no region (`mcp-server/src/toolsets/registry.ts:410-439`) and GUI Copy of a shot with no marks (`capture-clipboard.ts:85`, then `nativeImage.createFromBuffer` at `ui/src/main/clipboard-image.ts:11`) both use it. So once the row reports the shown frame, an MCP client that ignores EXIF gets the stored frame under shown-frame headers, and Copy of a tagged PNG pastes sideways (inference: `nativeImage` and Windows clipboard readers ignore `eXIf`; a tagged JPEG pastes right because `createImageBitmap` turns it). Expert pass finding 1.
- Export, and Copy of a marked shot, use the annotated copy (`services/capture.py:1801-1803`, `:1816`). A copy baked before this change is in the stored frame. For tags 5 to 8 it is 400x300 while the row becomes 300x400, so export answers 409 "list them again and retry", which listing never clears. For tags 2 to 4 the sizes match, so export, Copy and the filmstrip silently show the old mirrored or 180-degree bake. GUI marks saved before this change were clamped to the stored size (`:1500-1502`), so some are already cut and cannot be recovered. Expert pass finding 2.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). The change touches one adapter module, one service module and their tests, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern.
  - Receipts go under `C:/Temp/av-kit/capture-inbox-probe/`, named `s75-*`. Pytest runs with `TMP` and `TEMP` at `C:\Temp\av-kit\capture-inbox-probe\tmp`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
  - Playwright runs from pwsh at `P:/av-kit` through `npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts`.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone; a process is stopped only by its executable path under `P:\av-kit\ui\`, never by name.
- **Cloud-local contract:** not applicable; the driver OS is the target OS (grouping §3 "Cloud/local: local"). No row needs Mat at the PC: AC-146.19 pins the Chromium premise in the Electron suite.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s75-plan-2026-11-15-capture-inbox-probe` and `s75-execution-2026-11-15-capture-inbox-probe`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
- **Queue:** Session 87 runs and is committed first. This is the first session of the grouping; Sessions 76 to 83 follow and may run with nothing committed in between. Every baseline, scope and closeout check binds to the content recorded at row 0 (hashes in `s75-anchors.txt`, byte copies under `C:/Temp/av-kit/capture-inbox-probe/row0/`), never to `HEAD` (§Verification Plan 1). Execution waits for Mat's message (`plan_to_exec_gate: human`).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-145 scan skips unreadable files | `.agent/context/handoffs/2026-11-15-capture-inbox-probe-MEU-145-handoff.md` |
| MEU-146 EXIF orientation on scan | `.agent/context/handoffs/2026-11-15-capture-inbox-probe-MEU-146-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-15-capture-inbox-probe-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-15-capture-inbox-probe-implementation-critical-review.md`

One handoff per MEU follows `2026-11-08-capture-region-import` (MEU-128, MEU-129). Session 58 `capture-region-import` and Session 59 `capture-crop-copy` (plans, handoffs, reflections) are the capture precedents.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `s75-anchors.txt`, `row0/`, `s75-base-*.txt` |
| WP-2 | Stubs, then Red for both MEUs (rows 1 and 2) | WP-1 | shared | The stub names and the two fakes' methods; `tests/orientation_fixtures.py`; the four new test files; the AC-146.19 Electron test |
| WP-3 | MEU-145 Green (row 3) | WP-2 | shared | `adapter.py` (`probe`, `bake`, `render`), `services/capture.py` (`scan_inbox`), the AC-130.21 move |
| WP-4 | MEU-146 Green (row 4) | WP-3 | `compact_continue` at the MEU boundary | `adapter.py` (`_open_shown` and its callers, `shown_tag`, `read_shown`, the colour profile), the port's two methods, `services/capture.py` (DIMS_REFRESH, `read_image`, the bake marker, STALE_BAKE), the route comment, the AC-136.7 flip |
| WP-5 | Notes, registers and status (rows 5 and 6) | WP-4 | shared | 09 Delivered notes, `known-issues.yaml` and `.md`, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, grouping §6 row 75 |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | Two handoffs, the review, the reflection |

## User Review Required

> [!IMPORTANT]
> **Three choices were briefs, and all three are handed to the agent.** How the app applies an orientation tag (D-903), which formats it applies it to (D-904) and what a whole-image view and the plain download return (D-905) are written as briefs (§Decision Log) and settled by your hand-over for this grouping ("like we did here. But use the new HDP process."). One line from you overturns any of them. Rewriting your inbox file was never offered as a choice: it would change your own file (M-2), so D-903 lists it and does not recommend it. Every other decision is autonomous and hits nothing on the §4a list. A fresh-context expert pass read the three briefs: D-903 and D-904 hold, and D-905 changed (the plain download is now turned too), which also added D-909 for old annotated copies.
>
> **No step needs you at the PC.** The Electron suite checks the one premise that matters (Chromium turns a tagged JPEG, MPO and PNG and never a WebP, and reads the tag only from the EXIF block, AC-146.19).
>
> **What changes for you:**
>
> - A file in the inbox that is not really an image, or is damaged or half-written, no longer breaks the capture list in the GUI or through MCP. It is left out of the list, and the next refresh tries it again, so a screenshot still being written shows up once it is complete. The log gets one line with a count when the set of skipped files changes, never a name or path.
> - A phone photo or other JPEG or PNG with an orientation tag lists with the width and height you see, and marks, regions, Copy, Crop, Save, Export and the plain image download all use that frame. Your file stays as it is.
> - **Plain download of a tagged file (D-905, changed by the expert pass).** For a tagged JPEG, MPO or PNG, the image with no region (the filmstrip, Copy of an unmarked shot, the MCP image call) is now the picture turned upright, untagged, in the file's own format, with its colour profile. This fixes Copy of a tagged PNG, which today pastes sideways, and the MCP image call. The costs: each such load decodes and re-encodes the file (lossy for JPEG, quality 90); an MPO keeps only its first frame; the other EXIF fields (camera, GPS) are dropped, as crop and export already drop them; and a re-encoded PNG can pass the 413 size limit. Any untagged file, and every WebP, still gets its own bytes, byte for byte.
> - **Old annotated copies (D-909).** A tagged shot annotated before this change has a baked copy in the stored frame. Three effects follow, and the next scan fixes the first two:
>   - tags 5 to 8: export answers 409 "list them again and retry", and listing again never clears it;
>   - tags 2 to 4: the sizes match, so export, Copy and the filmstrip silently show the old mirrored or 180-degree bake;
>   - marks you saved in the GUI before this change were clamped to the stored size when saved, so a mark cut there is already lost; the rebake cannot recover it.
>
>   The guard: when a shot's shown frame differs from the frame its annotated copy was baked in, the next scan rebakes that copy from the saved marks. The copy is a file av-kit wrote, not your original, which is never touched. It also catches tags 2 to 4, where the size did not change.
> - **Other side effects:** marks an MCP client placed earlier on a tag 5 to 8 shot were placed in the stored frame and now land turned. Flatten of a tagged PNG writes upright pixels with no tag; a backup is kept only when `capture.flatten_backup` is on, as today. Today's flatten already writes the stored pixels with no tag, so the picture turns when you flatten; this change stops that.
>
> **What this plan leaves out:** WebP orientation (Chromium does not turn it, so the shown frame is the stored one), the video contact sheet, the inbox resolver's own message at `services/capture.py:2089`, and an annotated copy with no sidecar (§Out of Scope).

## Proposed Changes

### Single-statement contracts

- **`SCAN_SKIP` (MEU-145, D-900):** `scan_inbox` wraps each child's `child.resolve()` (`:609`) and probe (`:610`) in one `try`/`except (InboxPathError, OSError)`, so an `OSError` from either is a skip (expert pass, neighbours). A file that raises is skipped: no row is added, its existing row (if any) is not changed or deleted, and the loop goes on to the next child. Every readable file is upserted as today.
- **`KEEP_ROW` (MEU-145, D-901):** a skipped file's existing row keeps its `id`, `width`, `height`, `file_size` and `updated_at`; the delete pass still removes only rows whose original is not a file.
- **`PROBE_FIXED` (MEU-145, D-902):** `probe` raises `InboxPathError("no file at that path")` for a path that is not a file and `InboxPathError("the image could not be opened")` for any other failure (it catches `Exception`, so `SyntaxError` and `ValueError` are included). `bake` and `render` give the same fixed message for any open or load failure and write no output. `UnidentifiedImageError` is no longer imported.
- **`SKIP_LOG` (MEU-145, D-902):** `services/capture.py` exports `SCAN_SKIPPED_EVENT = "capture.scan_skipped"`. When a scan's skipped set is non-empty and differs from the previous scan's (`self._scan_skipped`, per service instance), it logs `log.warning(SCAN_SKIPPED_EVENT, count=n)` once, with no other key; an empty set resets `self._scan_skipped`, so a later recurrence logs again.
- **`SHOWN_FORMATS` (MEU-146, D-904):** `adapter.py` exports `SHOWN_ORIENTATION_FORMATS = frozenset({"JPEG", "MPO", "PNG"})` and `shown_orientation(image) -> int`. It reads only the EXIF block, `image.info.get("exif")`, as it stands right after open and before `load()`, never `getexif()`: Pillow 13's `getexif()` falls back to XMP `tiff:Orientation` and to a PNG `Raw profile type exif` text chunk (`.venv/Lib/site-packages/PIL/Image.py:1644-1665`), and it reads an `eXIf` chunk after `IDAT` once loaded; Chromium reads none of these (`s75-plan-probe-extra-electron.txt`, expert finding 3). It strips one leading `Exif\0\0`, requires the rest to start `II*\0` or `MM\0*` (a doubled prefix fails), parses it with `Image.Exif().load(body)` and reads `0x0112`. It returns that value when `image.format` is in the set and the value is an `int` from 2 to 8, and 1 otherwise (WebP, untagged, XMP-only, raw-profile text, `eXIf` after `IDAT`, junk EXIF, 0, 9). It never raises.
- **`SHOWN_OPEN` (MEU-146, D-903):** `_open_shown(source: Path | IO[bytes]) -> tuple[Image.Image, int]` opens the image, reads `shown_orientation` before `load()`, loads, and when the tag is not 1 applies the fixed map (2 `FLIP_LEFT_RIGHT`, 3 `ROTATE_180`, 4 `FLIP_TOP_BOTTOM`, 5 `TRANSPOSE`, 6 `ROTATE_270`, 7 `TRANSVERSE`, 8 `ROTATE_90`) with `Image.transpose`, not `ImageOps.exif_transpose` (which uses the `getexif()` reader, `ImageOps.py:758-759`). The result carries no orientation. It returns the shown image and the tag applied. Any failure is `InboxPathError("the image could not be opened")`. `view`, `crop`, `bake`, `render` and `export` read pixels only through it; flatten and revert follow through `bake` and `probe`.
- **`PROBE_SWAP` (MEU-146, D-903):** `probe` opens the file, reads `shown_orientation` before `load()`, loads to detect damage as today (PROBE_FIXED), and for tags 5 to 8 swaps width and height. It makes no pixel transpose (the scan probes every file on every list under `CAPTURE_FILE_LOCK`, `services/capture.py:600`; expert finding 6).
- **`SHOWN_TAG` (MEU-146, D-909):** the adapter and `ImageAnnotatePort` (`ports/capture.py:19`) gain `shown_tag(path: Path) -> int`: open the header only and return `shown_orientation`; 1 on any failure; never raises.
- **`READ_SHOWN` (MEU-146, D-905):** the adapter and the port gain `read_shown(path: Path) -> bytes`: read `data = path.read_bytes()` (an `OSError` propagates as today); open the header from `BytesIO(data)`, and on any exception return `data`; when the tag is 1 return `data`; otherwise load, transpose by the map and return `_encode_view(image, suffix, icc=...)` in the file's own format with no orientation tag; a load failure returns `data`. The service's `read_image(shot_id, variant)` (`services/capture.py:1541-1543`) calls it for `"original"`; `"annotated"` stays `read_bytes()`, since a bake is untagged PNG, JPEG or WebP output.
- **`VIEW_SHOWN` (MEU-146, D-905):** `view` compares the frame's source size with the shown size and returns the file's bytes unchanged (D-410 RETURN_UNCHANGED) only when the request is the whole image at scale 1 and the tag applied is 1. A whole view of a tagged JPEG, MPO or PNG is encoded upright in the file's own format with no orientation tag. The no-parameter `GET /captures/{id}/image` (`routes/captures.py:429-431`) answers `read_image`, so an untagged file gets its own bytes byte for byte and a tagged JPEG, MPO or PNG gets READ_SHOWN's upright bytes at the whole frame; its `X-Capture-*` headers give the shown frame (D-411 FRAME_HEADERS). The route's code and docstring do not change; only its comment at `:424-426`, which today credits the byte-exact answer to D-411, is rewritten to name D-410 and D-905.
- **`ICC_KEEP` (MEU-146, D-905):** `_encode_view` (`adapter.py:368-382`) gains `icc: bytes | None = None` and passes it as `icc_profile` when set. The turned whole view and READ_SHOWN pass the source's `info.get("icc_profile")`, as crop and export already do (`:579`, `:593-594`; expert finding 5). Untagged region views keep today's behaviour (a residual, §Out of Scope).
- **`BAKE_MARKER` (MEU-146, D-909):** `annotate_and_save` (`services/capture.py:1470-1530`) calls `shown_tag(original)` before the bake and writes the sidecar through one helper, `_write_sidecar(path, marks, orientation)`, which adds `"baked_orientation": n` only when n is not 1. For an untagged shot the sidecar keys stay exactly `version` and `annotations`, and `SIDECAR_VERSION` stays 1; `parse_sidecar_document` already ignores unknown top-level keys (`:331-332`).
- **`STALE_BAKE` (MEU-146, D-909):** in the scan's reconcile loop, under the same lock and unit of work, for each shot whose `annotated_path` and `sidecar_path` both exist, whose original was not skipped this scan and whose recovery restored every file (`STAGED_REBAKE` Recovery): read `baked_orientation` from the sidecar (absent means 1; a malformed sidecar is left alone, silently); take `shown = shown_tag(original)`; when they differ, clamp the saved marks to the row's width and height and call `_restage_annotated` (`STAGED_REBAKE`), which publishes the new copy and sidecar at the same two paths; then save the row with the same paths and a new `updated_at`. It does not call `_rebake_annotated` (`:2009-2026`), which bakes straight onto the live path and deletes siblings first (review R1-F1). On any failure the copy, the sidecar and the row stay as they were and the next scan retries; the service logs `log.warning(STALE_BAKE_FAILED_EVENT, count=n)` with `STALE_BAKE_FAILED_EVENT = "capture.stale_bake_failed"`, deduplicated through `self._stale_bake_failed: frozenset[str]` as SKIP_LOG is, with no path. That set holds each shot whose restage or recovery hit an I/O failure this scan. Revert (`:1625-1657`) leaves the sidecar as it is; its own `_rebake_annotated` already bakes in the shown frame, so at worst the next scan rebakes once more and sets the key. Crop and convert sidecars (`:1729`, `:1962`) describe untagged PNG output and get no key. It does not key on size alone, so tags 2 to 4 are caught. Cost: one header parse per annotated shot per list.
- **`STAGED_REBAKE` (MEU-146, D-910):** `_restage_annotated(original, annotated, sidecar, marks, payload, shown)` is a new, scan-only service helper; `_rebake_annotated`, `annotate_and_save` and revert do not change. Every name it writes sits in the shot's own folder: for a live file `p`, the new file is `p.with_name(f".{p.name}.rebake-new")` and the kept old file is `p.with_name(f".{p.name}.rebake-prior")`. These names end in neither a scan extension nor an annotated suffix, so the scan never lists them (`:604-607`).
  - **Format kept.** The format comes from the copy's own name, the inverse of `ANNOTATED_EXT` (`domain/capture.py:48`) applied to its `.annotated<ext>` ending, never from `capture.annotated_format`. So a format setting changed since the save, or an invalid one, neither renames the copy nor fails the scan, and no sibling is ever deleted. A name with no known ending is left alone and counted as a failure.
  - **Order.** (1) `bake(original, marks, new_img, fmt)`; (2) write the sidecar text to `new_side`: the saved payload with its `annotations` list untouched and only `baked_orientation` set to `shown`, or removed when `shown` is 1; (3) `os.replace(annotated, prior_img)`; (4) `os.replace(new_img, annotated)`; (5) `os.replace(sidecar, prior_side)`; (6) `os.replace(new_side, sidecar)`; (7) discard both prior files. The service calls `os.replace` and `os.unlink` through its module's `os` (`services/capture.py:8`), so a test can patch `avkit_core.services.capture.os.replace` and `.os.unlink`. Every discard of a `.rebake-` name goes through one helper, `_discard_rebake(path) -> bool`, which unlinks it if present, catches `OSError` and returns False on a failure; it never raises. A failed discard in step 7 leaves the prior file for recovery and does not undo a publish.
  - **Rollback.** If any of steps 1 to 6 raises, the helper undoes the steps that ran, in reverse: a published new file is moved back to its `.rebake-new` name and the prior file is moved back to the live name. It then discards both `.rebake-new` names and raises, so STALE_BAKE counts the shot. The old copy, its marks and the row are what they were before the scan. If an undo step itself fails, the helper leaves that file under its `.rebake-` name for recovery and still raises the first error. A step 3 that meets a leftover prior it cannot replace fails here like any other step.
  - **Recovery.** If the process stops mid-step, or a discard failed, the next scan repairs the folder. For each row whose original is still a file, after the delete pass and before the RECONCILE checks (`:637-647`), `_recover_restage(shot) -> RecoverResult` runs on each of the row's two paths that is set, catches every `OSError` and never raises. `RecoverResult` has two fields, `restored_all: bool` and `io_failed: bool`.
    - **Restore.** When the live file is missing and its `.rebake-prior` exists, `os.replace(prior, live)`. If that raises (a prior opened without delete sharing, WinError 32), the prior stays, `restored_all` is False and `io_failed` is True.
    - **Cleanup.** Any leftover `.rebake-new`, and a `.rebake-prior` beside a live file, goes through `_discard_rebake`. A False return (a read-only prior, WinError 5) sets `io_failed` only; the live files are valid, so the shot goes on as usual.
    - **Outcome.** When `restored_all` is False the shot skips RECONCILE's path clearing and STALE_BAKE for this scan, so the row keeps both links and the prior keeps the old copy for the next scan. When `io_failed` is True the shot's resolved original path joins the same failure set as a failed restage, so one `STALE_BAKE_FAILED_EVENT` with `count` only covers both, deduplicated as SKIP_LOG is. The other shots are listed and reconciled as usual. A copy republished before the stop with an old sidecar key simply rebakes once more.
- **`DIMS_REFRESH` (MEU-146, D-906):** the scan (`:629`), `_upsert_shot` (`:2119`) and `_import_in_place` (`:754`) update a row when its width or height differs from the probe as well as when its file size does, so a row recorded before this change gets the shown size on the next scan.
- **`CROP_EXPORT_FRAME` (MEU-146, D-907):** `crop` and `export` cut and write the shown frame: the box and `source_size` are in that frame, and the output carries no orientation tag. The "no `exif_transpose`" docstrings of `crop` (`:549`) and `export` (`:679`) are rewritten to name D-907.
- **`WEBP_PIN` (MEU-146, D-904):** AC-146.19 pins in the Electron suite that Chromium turns a tag-6 JPEG, MPO and PNG (`eXIf` before `IDAT`) and does not turn a tag-6 WebP, an `eXIf` after `IDAT`, a prefixed `eXIf`, a raw-profile PNG or an XMP-only JPEG. Its fixtures come from one Pillow builder, `tests/orientation_fixtures.py`, which also reports what each fixture holds, so a broken fixture fails the test instead of passing it (expert finding 4). If it ever fails, `SHOWN_ORIENTATION_FORMATS` or the EXIF-block rule is wrong (S14).

### MEU-145: the scan survives an unreadable file

1. **`packages/infrastructure/src/avkit_infra/capture/adapter.py` (CRLF).** `probe` (`:461-470`), `bake` (`:603-617`) and `render` (`:623-631`) per `PROBE_FIXED`; remove the `UnidentifiedImageError` import (`:23`) once no use is left. A short comment names D-902 and D-421.
2. **`packages/core/src/avkit_core/services/capture.py` (CRLF).** Add `SCAN_SKIPPED_EVENT` beside `log` (`:94`), `self._scan_skipped: frozenset[str]` in `__init__`, and the per-child `try` and the one log call in `scan_inbox` (`SCAN_SKIP`, `KEEP_ROW`, `SKIP_LOG`). The set holds resolved paths in memory only; nothing logs or returns it.
3. **`tests/e2e/test_api_capture_crop.py` (LF), AC-145.15.** In `test_ac_130_21_damaged_source_is_422` remove `intact = source.read_bytes()` (`:771`), the two comment lines (`:779-780`) and `source.write_bytes(intact)` (`:781`). The follow-up list must still answer 200 with the same ids, now with the damaged file in the inbox.

### MEU-146: one frame for a tagged file

1. **`adapter.py` (CRLF).** Add `SHOWN_ORIENTATION_FORMATS`, `shown_orientation` and `_open_shown` after `_UPRIGHT_MODES` (`SHOWN_FORMATS`, `SHOWN_OPEN`). `probe` reports the shown size by a swap (`PROBE_SWAP`). `view` (`:473-497`), `crop`, `bake`, `render` and `export` open through `_open_shown` (`VIEW_SHOWN`, `CROP_EXPORT_FRAME`). Add `shown_tag` and `read_shown` (`SHOWN_TAG`, `READ_SHOWN`) and the `icc` parameter of `_encode_view` (`ICC_KEEP`). `write_upright_png` (D-417), `inspect_import` and `sheet` are unchanged.
2. **`packages/core/src/avkit_core/ports/capture.py` (CRLF).** `ImageAnnotatePort` (`:19`) gains `shown_tag` and `read_shown`, each with a one-line docstring naming D-909 or D-905.
3. **`services/capture.py` (CRLF).** The three update tests per `DIMS_REFRESH`; `read_image` per `READ_SHOWN`; `_write_sidecar`, the call in `annotate_and_save` and the reconcile step per `BAKE_MARKER` and `STALE_BAKE`; `_restage_annotated` and its recovery step per `STAGED_REBAKE`, calling `os.replace` through the module's `os`, with `_rebake_annotated` left as it is; and `STALE_BAKE_FAILED_EVENT` beside `SCAN_SKIPPED_EVENT` and `self._stale_bake_failed` in `__init__`. Flatten and revert reach the new frame through the adapter.
4. **`packages/api/src/avkit_api/routes/captures.py` (CRLF), comment only.** The three `#` lines at `:424-426` become: with none of x, y, width, height, unit and max_edge, an untagged file's bytes are returned unchanged (D-410) and a tagged JPEG, MPO or PNG is returned upright (D-905); the five `X-Capture-*` headers give the shown frame either way (D-411); the region fields line stays. No code, docstring or OpenAPI text changes (S6).
5. **Test fakes, no assertion change.** `FakeCapturePort` (`tests/unit/test_capture_service.py:67-132`, CRLF) and `FakeAnnotate` (`tests/unit/test_capture_export_service.py:92-138`, LF) each gain `read_shown` (returns `path.read_bytes()`) and `shown_tag` (returns 1), so every existing service test sees today's bytes and an untagged frame (§Existing test assertions).
6. **`tests/orientation_fixtures.py` (new, LF).** One builder, `build(out_dir) -> dict[str, dict]`, writes the 40x30 fixtures `o6.jpg`, `o6.png`, `o6.mpo.jpg`, `o6.webp`, `o6-after-idat.png`, `o6-prefixed.png`, `o6-raw-profile.png` and `o6-xmp.jpg` (blue with a red top-left block, orientation 6 written by Pillow or by a spliced chunk with its CRC32) and returns, per fixture, the format, the EXIF-block tag, the `getexif()` tag and, for the WebP, the `VP8X` flag byte and whether an `EXIF` chunk is present. `python -m tests.orientation_fixtures <out_dir>` prints that as JSON. AC-146.1 and AC-146.19 use it; `tests/` has no `__init__.py`, so it runs from the repo root as a namespace module.
7. **`tests/unit/test_capture_export_adapter.py` (LF), AC-146.11.** `test_ac_136_7_exif_orientation_is_not_applied` becomes `test_ac_136_7_exif_orientation_is_applied`, its docstring names D-907 in place of "records the behaviour; it fixes nothing", `_export` gets `source_size=(300, 400)`, and the asserts become: size `(300, 400)`, red at `(290, 10)`, blue at `(10, 390)`, no `0x0112` in the output and no `exif` in its info. It stays parametrized over `FORMATS`.
8. **`ui/tests/e2e/capture-inbox.test.ts` (LF), AC-146.19.** Append one test after the last describe, and add `spawnSync` to the file's `node:child_process` import, which today reads `import { spawn, type ChildProcess } from 'node:child_process'` (`:2`; review R1, non-blocking). The test runs `uv run --no-sync python -m tests.orientation_fixtures <outDir>` through `spawnSync` from `node:child_process` with `cwd` at the repo root and `outDir` under the test's temp folder, and first asserts the builder's report: the `getexif()` tag is 6 for every fixture, and the WebP has `VP8X` flag `0x08` and an `EXIF` chunk. It then calls `launchApp()` (`:65`), loads each fixture as an `<img>` from a data URL in the renderer and reads `naturalWidth` and `naturalHeight`: 30x40 for `o6.jpg`, `o6.png` and `o6.mpo.jpg`, 40x30 for the other five. It adds no launch helper of its own (grouping §2: "unless their plans say so"; this plan says so).

### Closing the known issues

Row 6 resolves both issues through `issue-resolve.py` (a copy of Session 84's, `SCRATCH` at `C:/Temp/av-kit/capture-inbox-probe`), bound to the register's row-0 SHA-256 from `s75-anchors.txt`. Each gets `status: "resolved"`, a `verification` naming the row 3 or row 4 receipts, and a `resolution_path` that starts `Fixed in Session 75 on <date> (plan docs/execution/plans/2026-11-15-capture-inbox-probe):`. The recorded cause stands. Then `issue_triage.py render` and `render --check`.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `GET /captures` and MCP `list` | `routes/captures.py` `CaptureShotOut`; `mcp-server/src/toolsets/capture.ts` | Unchanged shape. A skipped file is absent from `items`; a tagged file's `width` and `height` are the shown frame | Unchanged |
| `GET /captures/{id}/image` | `routes/captures.py:411` | Unchanged parameters, headers, media types and docstring. A tagged JPEG, MPO or PNG, with or without a region, answers upright, untagged bytes of the same media type; an untagged file's no-parameter answer stays its bytes | Unchanged |
| MCP image call | `mcp-server/src/toolsets/registry.ts:410-439` | Unchanged; it calls the no-parameter route, so it gets the upright bytes | Unchanged |
| `ImageAnnotatePort` | `packages/core/src/avkit_core/ports/capture.py:19` | Two new methods, `shown_tag` and `read_shown`; an in-process Protocol, not a wire | The two repo fakes gain both |
| Annotation sidecar | `services/capture.py` (`_write_sidecar`, `parse_sidecar_document` `:331-332`) | Optional `baked_orientation` int 2 to 8, written only for a tagged bake; `version` stays 1 | The parser already ignores unknown top-level keys |
| `InboxPathError` messages (422) | `adapter.py`, `errors.py` | Fixed strings: `no file at that path`, `the image could not be opened` | Not a schema change; the error class and code are unchanged |
| `capture.scan_skipped` and `capture.stale_bake_failed` log events | `services/capture.py` | Keys `event`, `log_level`, `module`, `count` only | New events, no path |

No API route, OpenAPI document, MCP tool shape or database schema changes, so there is no M-4 hit (D-900, D-905, D-909). The bytes of a tagged file's plain download change, but not its shape: the same media type, the same headers and the frame those headers already give. The session gate's `openapi` step proves the app still matches `openapi.committed.json`, and that file's row-0 hash is checked again (S6).

### Acceptance Criteria

Test names start with `test_ac_145_<n>_` or `test_ac_146_<n>_`, each with `@pytest.mark.unit` and `@pytest.mark.parametrize("ac_id", [label], ids=[label])`, at most 71 characters (`id-length.py`), so `red-check.py --require` matches each exactly. The Electron test title starts with `AC-146.19`.

- **AC-145.1 to AC-145.11** are in `tests/unit/test_capture_scan_unreadable.py` (new, LF). The adapter cases use the real `CaptureAdapter` on files written in the test. The service cases import `FakeCapturePort`, `_stack` and `_write_inbox_file` from `tests.unit.test_capture_service` (`:67`, `:135`, `:159`) and give the fake a `probe` that raises for named files, as `probe_failing_after_flatten` does (`:1009`). The log cases use `structlog.testing.capture_logs`.
- **AC-145.12 and AC-145.13** are in `tests/e2e/test_api_capture_scan_unreadable.py` (new, LF), and **AC-146.15 to AC-146.18, AC-146.27 and AC-146.28** in `tests/e2e/test_api_capture_orientation.py` (new, LF). Both follow the `_stack(app_data, inbox)` pattern of `test_api_capture_crop.py:55` with `TestClient(app, raise_server_exceptions=False)` (`test_api_error_surface.py:56`), so a 500 is an answer, not a raise.
- **AC-146.1 to AC-146.10, AC-146.12 to AC-146.14 and AC-146.20 to AC-146.26** are in `tests/unit/test_capture_orientation.py` (new, LF). Fixtures are generated in the test: a 400x300 RGB image, blue `(20, 20, 200)` with a red `(230, 20, 20)` block at `(0, 0, 40, 40)`, saved as JPEG (quality 95), PNG and WebP with `exif` holding orientation 1 to 8, plus an MPO (two 40x30 frames, tag 6), a JPEG with junk EXIF bytes, and tags 0 and 9. The fixtures whose tag Pillow reads but Chromium does not (XMP-only, raw-profile, `eXIf` after `IDAT`, prefixed `eXIf`) and the Pillow-written tag-6 PNG come from `tests/orientation_fixtures.py`, the same builder AC-146.19 uses. The ICC cases attach a small sRGB profile from `ImageCms.createProfile("sRGB")`.
- **The service cases of AC-146.23 to AC-146.26** use the real `CaptureService` with a subclass of `FakeCapturePort` whose `shown_tag` returns a set tag and whose `read_shown` returns a sentinel, so each case sees exactly which port method the service called. AC-146.25 and AC-146.26 use real files in a `tmp_path` inbox; their failure cases give the subclass a `bake` that writes `b"part"` to its output and then raises `OSError`, or patch `avkit_core.services.capture.os.replace` with a wrapper that raises `OSError` on its Nth call, or for one named source path, and passes the others to the real function; the recovery cases (f) and (g) also patch `.os.unlink` in the same way or set a real read-only attribute, and clear it in a `finally`. Each case records the bytes of the original, the copy and the sidecar and the row's paths before the scan, and lists the inbox folder after it.
- **Catch-then-assert.** Each Red test catches the exception a call raises and asserts on it (type, message), so a raise is an assertion failure, never a setup error. New names are imported inside the test body.
- **Negative cases have a positive control** (coordinator note, 2026-11-15). Every "absent" assertion sits beside one that today's code would fail or that proves the check can see its target:
  - the path checks (AC-145.1 to AC-145.6, AC-145.10, AC-145.12) use an inbox folder whose name holds the marker `s75mark`, so any path in a message, log line or body would match; each also asserts the message, the event or the listed shots it expects;
  - AC-145.8 records the row before the damage and asserts it is still there, unchanged, after the scan (not only that no row was added);
  - AC-145.11 starts from a state where the event fired once, and ends with a recurrence after a clean scan, so stale skip state fails it;
  - the guards (AC-146.5, AC-146.21, AC-146.28) run beside a tagged JPEG case in the same file whose bytes do change (AC-146.4, AC-146.20, AC-146.17);
  - every "gives 1" case of AC-146.1 uses a fixture whose `getexif()` reads 6, which the builder's report asserts, so a reader that falls back to `getexif()` fails it;
  - AC-146.25's "no second rebake" case first proves the first scan rebaked (the copy's size or pixels changed);
  - AC-146.26's path check uses the `s75mark` folder and also asserts the event it expects;
  - every test writes into its own `tmp_path`, and `_scan_skipped` and `_stale_bake_failed` live on the service instance, so a re-run starts empty.
- **AC-145.14, AC-145.15 and AC-146.11** run existing tests: the MCP list pin unchanged, and the two moved pins (§Pins that move).

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-145.1 | unit | `probe` on a non-image file named `.png` raises `InboxPathError` whose message is exactly `the image could not be opened`. | Local Canon (09 §Scan skips: No path; D-421; D-902) | In Red the message holds the path |
| AC-145.2 | unit | The same for a PNG whose IDAT is damaged in place (same length). | Local Canon (09 Tests; D-902) | In Red it raises `SyntaxError` |
| AC-145.3 | unit | The same for a PNG cut to half its length. | Local Canon (09 Retry: a half-written screenshot; D-902) | In Red the message holds the path |
| AC-145.4 | unit | `probe` on a missing path raises `InboxPathError` with exactly `no file at that path`. | Local Canon (`services/capture.py:727`; D-902) | In Red the message holds the path |
| AC-145.5 | unit | `bake` on the non-image, damaged and truncated files raises `InboxPathError` with the fixed message and writes no output file. | Local Canon (09 No path; D-902) | In Red the non-image message holds the path and the damaged file raises `SyntaxError` |
| AC-145.6 | unit | `render` on the same three files raises `InboxPathError` with the fixed message. | Local Canon (D-902) | In Red the damaged file raises `SyntaxError` |
| AC-145.7 | unit | A service scan whose fake probe raises `InboxPathError` for one file and `OSError` for another, and where `Path.resolve` is patched to raise `OSError` for a third, lists exactly the readable shots and adds no row for any of the three. | Local Canon (09 List; D-507; D-900) | In Red the scan raises |
| AC-145.8 | unit | A file listed once, then made unreadable, keeps its row: same `id`, `width`, `height`, `file_size` and `updated_at`. | Local Canon (09 Retry; D-901) | In Red the scan raises |
| AC-145.9 | unit | After the file is readable again, the next scan lists it (new file: a new row; kept row: updated as today). | Local Canon (09 Retry) | In Red the first scan raises |
| AC-145.10 | unit | Two unreadable files give one `capture.scan_skipped` warning whose keys are exactly `event`, `log_level`, `module` and `count`, with `count` 2 and no path, name, marker or exception text in any value. | Local Canon (09 No path; Session 50 rule; D-902) | In Red no event is logged and the scan raises |
| AC-145.11 | unit | A second scan with the same set logs nothing; a third bad file logs `count` 3; a scan with all files readable logs nothing; a later bad file logs `count` 1. | Local Canon (D-902) | A stale or missing reset fails the last case |
| AC-145.12 | e2e | API: an inbox with `a.png`, `b.png`, a non-image `fake.png` and a damaged `broken.png` answers `GET /captures` 200 with exactly the names `a.png` and `b.png`; no bad name, marker or path is in the body. | Local Canon (09 List and Tests; D-900) | In Red the answer is 422 or 500 |
| AC-145.13 | e2e | API retry: a non-image `late.png` is not listed; after it is overwritten with a valid PNG, the next list includes it. | Local Canon (09 Retry) | In Red the first list fails |
| AC-145.14 | unit | MCP `list` is `GET /captures` through the same service: the pin at `mcp-server/tests/capture.test.ts:24` passes unchanged in the gate's `mcp-tests`. | Local Canon (09 List: "through the API and MCP") | A changed MCP shape fails the pin |
| AC-145.15 | e2e | AC-130.21 with its restore removed: the follow-up list answers 200 with the same ids while the damaged file stays in the inbox (Green only). | Local Canon (09 Tests: "AC-130.21 no longer needs to restore") | Before Green the list fails |
| AC-146.1 | unit | `shown_orientation`: JPEG, MPO and PNG tagged 2 to 8 give that tag, and so does the builder's Pillow-written `o6.png` (6); tag 1 or no tag give 1; WebP tagged 2 to 8 gives 1; the builder's XMP-only JPEG, raw-profile PNG, `eXIf`-after-`IDAT` PNG (freshly opened) and prefixed-`eXIf` PNG give 1, though `getexif()` reads 6 for each; junk EXIF, 0 and 9 give 1, with no raise. | Local Canon (`SHOWN_FORMATS`; `s75-plan-probe-extra-electron.txt`; D-904, handed to the agent) | In Red the stub returns 1 for a tagged JPEG; a `getexif()` reader fails the XMP-only and raw-profile cases |
| AC-146.2 | unit | `probe` on the 400x300 JPEG and PNG tagged 1 to 8: tags 1 to 4 give `(400, 300)`, tags 5 to 8 give `(300, 400)`; with `Image.Image.transpose` patched to raise, `probe` of the tag-6 JPEG still gives `(300, 400)` (`PROBE_SWAP`). | Local Canon (09 Tests; D-903, handed to the agent) | In Red tags 5 to 8 give `(400, 300)` |
| AC-146.3 | unit | `probe` on the WebP tagged 1 to 8 gives `(400, 300)`; the MPO tagged 6 gives `(30, 40)`; the junk-EXIF JPEG gives its stored size; the builder's XMP-only, raw-profile and `eXIf`-after-`IDAT` files give `(40, 30)`. | Local Canon (D-904, handed to the agent) | In Red the MPO gives `(40, 30)` |
| AC-146.4 | unit | A whole view at scale 1 of the JPEG and PNG tagged 2 to 8 has the shown size, red (r > 200, g < 60, b < 60) at the Electron probe's position for that tag, no orientation tag, and the file's own format. | Local Canon (`VIEW_SHOWN`; `s75-plan-probe-electron.txt`; D-905, handed to the agent) | In Red tags 5 to 8 give 409 and tags 2 to 4 return the tagged bytes |
| AC-146.5 | unit | Guard: a whole view of an untagged file, a tag-1 file and a tagged WebP returns the file's bytes. | Local Canon (D-410 RETURN_UNCHANGED; D-905) | Run beside AC-146.4's tagged JPEG, whose bytes change |
| AC-146.6 | unit | A region `(260, 0, 40, 40)` of the tag-6 JPEG and PNG, with source size `(300, 400)`, is 160x160 (the D-409 4x upscale of the 40x40 region) with a red centre. | Local Canon (09 Tests: a region in the shown frame; D-903) | In Red the size check gives 409 |
| AC-146.7 | unit | A view of the tag-6 file given with the stored source size `(400, 300)` raises `ConflictError`. | Local Canon (D-903; MEU-129 size check) | In Red it returns bytes |
| AC-146.8 | unit | `crop` of the tag-6 JPEG, box `(260, 0, 40, 40)`, source size `(300, 400)`, writes a 40x40 PNG with a red centre and no EXIF. | Local Canon (`CROP_EXPORT_FRAME`; D-907) | In Red the size check refuses |
| AC-146.9 | unit | `bake` of the tag-6 JPEG with a `RedactAnnotation` `#00FF00` at shown `(100, 330, 40, 40)` writes a 300x400 PNG with green at `(120, 350)`. | Local Canon (09 Tests: a mark bakes in the same place; D-903) | In Red the output is 400x300 |
| AC-146.10 | unit | `render` with the same mark returns the same pixels as AC-146.9's bake. | Local Canon (D-903) | In Red the output is 400x300 |
| AC-146.11 | unit | The flipped AC-136.7 (`test_ac_136_7_exif_orientation_is_applied`) passes for PNG, JPEG and WebP output (Green only). | Local Canon (`CROP_EXPORT_FRAME`; D-907 over D-613) | Before Green the export is 400x300 |
| AC-146.12 | unit | A row recorded as 400x300 for a file whose probe now gives 300x400 with the same file size is updated to 300x400 by the next scan. | Local Canon (`DIMS_REFRESH`; D-906) | In Red the row keeps 400x300 |
| AC-146.13 | unit | The same through `register_shot`. | Local Canon (D-906) | In Red the row is returned unchanged |
| AC-146.14 | unit | The same through `import_image` of a file already in the inbox. | Local Canon (D-906) | In Red the row is returned unchanged |
| AC-146.15 | e2e | API: `GET /captures` over the JPEG and PNG tagged 1 to 8 and the WebP tagged 6 lists 400x300 for tags 1 to 4 and the WebP, and 300x400 for tags 5 to 8. | Local Canon (09 One frame; D-903, D-904) | In Red tags 5 to 8 list 400x300 |
| AC-146.16 | e2e | API: `GET /captures/{id}/image?x=260&y=0&width=40&height=40` on the tag-6 JPEG answers 200 with a 160x160 image (the D-409 4x upscale of the 40x40 region), a red centre and `X-Capture-Source: 300,400`. | Local Canon (09 Tests; D-903) | In Red it answers 409 |
| AC-146.17 | e2e | The no-parameter `GET /captures/{id}/image` on the tag-6 JPEG answers 200 with an upright 300x400 JPEG, red at `(290, 10)`, no `0x0112`, and `X-Capture-Source: 300,400`. | Local Canon (`READ_SHOWN`; D-905, handed to the agent) | In Red it returns the tagged 400x300 bytes |
| AC-146.18 | e2e | API flatten of the tag-6 PNG with one mark: the file becomes an upright 300x400 PNG with no orientation tag, the shot keeps its id, and the backup equals the tagged bytes. | Local Canon (D-903; flatten through `bake`) | In Red the file is 400x300 |
| AC-146.19 | e2e | Electron: the builder reports `getexif()` tag 6 for all eight fixtures and, for the WebP, `VP8X` flag `0x08` with an `EXIF` chunk; in the app's renderer `o6.jpg`, `o6.png` and `o6.mpo.jpg` load at `naturalWidth` 30 and `naturalHeight` 40, and `o6.webp`, `o6-after-idat.png`, `o6-prefixed.png`, `o6-raw-profile.png` and `o6-xmp.jpg` at 40 and 30. A guard. | Research-backed (`s75-plan-probe-electron.txt`, `s75-plan-probe-extra-electron.txt`; `WEBP_PIN`; D-904, handed to the agent) | A fixture that lost its tag fails the report; a Chromium change fails the sizes (S14) |
| AC-146.20 | unit | `read_shown` on the tag-6 JPEG, PNG and MPO returns bytes in the format the suffix names (`_encode_view`; JPEG for the `.jpg` MPO), 300x400 (MPO 30x40), red at the shown corner, no `0x0112` in the result. | Local Canon (`READ_SHOWN`; D-905, handed to the agent) | In Red the stub returns the tagged bytes |
| AC-146.21 | unit | Guard: `read_shown` returns the file's bytes unchanged for an untagged PNG, a tag-1 JPEG, the tag-6 WebP, the builder's XMP-only, raw-profile and `eXIf`-after-`IDAT` files, a tag-6 JPEG cut to half its length (its header still reads as tag 6), and a non-image file. | Local Canon (D-410 RETURN_UNCHANGED; D-905) | Run beside AC-146.20, whose bytes change |
| AC-146.22 | unit | A tag-6 JPEG and PNG carrying an sRGB ICC profile: the whole view at scale 1 and `read_shown` are each 300x400 and carry the same `icc_profile` bytes. | Local Canon (`ICC_KEEP`; crop and export keep it, `adapter.py:579`, `:593-594`; D-905) | In Red the view answers 409 and `read_shown` returns the tagged 400x300 bytes |
| AC-146.23 | unit | The service's `read_image(id, "original")` returns the port's `read_shown` sentinel; `read_image(id, "annotated")` returns the annotated file's bytes. | Local Canon (`READ_SHOWN`; D-905) | In Red `"original"` returns the file's bytes |
| AC-146.24 | unit | `annotate_and_save` with a port whose `shown_tag` is 6 writes a sidecar with `"baked_orientation": 6`; with `shown_tag` 1 the sidecar keys are exactly `version` and `annotations`. | Local Canon (`BAKE_MARKER`; D-909) | In Red the tag-6 sidecar has no key |
| AC-146.25 | unit | A scan rebakes the annotated copy once, calls `bake` once with the saved marks, an output path in the shot's folder other than the live copy, and the copy's own format, and rewrites the key, for: no key with `shown_tag` 6; no key with `shown_tag` 3; key 6 with `shown_tag` 1 (the key is removed). After it the copy holds the new bake at the same path, the sidecar's `annotations` list equals the saved one, the row's `annotated_path` and `sidecar_path` are unchanged, and no `.rebake-` file is in the folder. A second scan makes no `bake` call. A shot whose key matches makes none. | Local Canon (`STALE_BAKE`, `STAGED_REBAKE`; 09 One frame; D-909, D-910) | In Red the scan makes no `bake` call |
| AC-146.26 | unit | When that rebake fails, the list still answers and nothing the user had is lost. Cases: (a) `bake` writes `b"part"` to its output and raises; (b) `os.replace` raises while the copy is published (call 2) and (c) while the sidecar is published (call 4); (d) `capture.annotated_format` is `jpeg` while the copy is `.annotated.png`, with `bake` raising; (e) an interrupted rebake: the live copy is missing and its `.rebake-prior` holds the old copy. In (a) to (d) the original, copy and sidecar bytes and the row's paths equal those recorded before the scan; in (e) the copy is restored to its prior bytes and the row keeps its path. In (a) to (e) no `.rebake-` file is left, and one `capture.stale_bake_failed` warning has keys exactly `event`, `log_level`, `module` and `count`, `count` 1, no path or marker ((e) logs one once its rebake is made to raise); a second failing scan logs nothing. Then, with a working port and `os.replace`, the next scan rebakes once and the scan after it makes no `bake` call; in (d) the copy is still `.annotated.png`, the format the adapter is given is `png`, and no `.annotated.jpg` exists. Two recovery cases (review R2-F1), each with a second shot whose stale copy the same scans must rebake: (f) a read-only `.rebake-prior` beside a published copy and sidecar whose key matches, once with a real read-only attribute (`os.chmod(prior, stat.S_IREAD)`, WinError 5 on Windows) and once with `os.unlink` patched to raise `PermissionError` for that prior only, so the path runs on every platform: the list answers with both shots, the row keeps both links, the copy and the sidecar's marks are unchanged, no `bake` call is made for it, one warning with `count` 1 is logged and a second scan logs nothing; once the attribute is cleared or the patch removed, the next scan discards the prior and makes no `bake` call; (g) a live copy missing with its `.rebake-prior` locked, faked by an `os.replace` patched to raise `PermissionError` for that prior only, as the test's docstring says: the list answers with both shots, the row still has both links, the prior and the sidecar's marks are unchanged, no `bake` call is made for it, one warning with `count` 1 is logged and a second locked scan logs nothing; once unlocked, the next scan restores the copy and rebakes it exactly once, and the scan after makes no `bake` call. In both, the other shot is rebaked on the first scan, the warning's keys are exactly `event`, `log_level`, `module` and `count` with no path or marker, and the only `.rebake-` file left while locked is that prior. | Local Canon (`STALE_BAKE`, `STAGED_REBAKE`; D-902 log rule; D-909, D-910; reviews R1-F1 and R2-F1) | In Red no event is logged and no rebake happens; a rebake through `_rebake_annotated` would fail (a), (b) and (d) by leaving partial or `.jpg` files; a recovery that raises would fail (f) and (g) by a failed list, and one that goes on to RECONCILE would fail (g) by clearing the link |
| AC-146.27 | e2e | API: a tag-6 JPEG is annotated through the API with one `#00FF00` redact mark, then put in the state today's code leaves (the copy overwritten with a 400x300 bake of the stored frame, the sidecar rewritten with the same marks and no key). After `GET /captures` the copy is 300x400 with green at the mark's shown centre, the sidecar has `"baked_orientation": 6`, and a whole-frame export answers 200 with a 300x400 image. | Local Canon (`STALE_BAKE`; expert finding 2; D-909) | In Red the copy stays 400x300 |
| AC-146.28 | e2e | Guard: the no-parameter `GET /captures/{id}/image` returns the file's bytes byte for byte for an untagged PNG, a tag-1 JPEG and the tag-6 WebP. | Local Canon (D-410 RETURN_UNCHANGED; route comment `routes/captures.py:424-426`; D-905) | Run beside AC-146.17, whose answer changes |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Skip or flag an unreadable file | Local Canon | Skip (D-900); a flag would add a field to the REST and MCP list (M-4) |
| What happens to a skipped file's row | Local Canon | Kept as it is (D-901) |
| The messages and the log line | Local Canon | Fixed strings; one count-only event (D-902) |
| How the tag is applied | Ambiguous local canon (tag `Local Canon`), handed to the agent | D-903 (brief, M-5, M-6) |
| Which formats are turned | Source conflict with 09's "JPEG or WebP", handed to the agent | D-904 (brief, M-6) |
| What a whole view and the plain download return | Source conflict with D-410 and the route comment, handed to the agent | D-905 (brief, M-6; changed by the expert pass) |
| Which tag reader sets the frame | Research-backed (`s75-plan-probe-extra-electron.txt`) | The EXIF block only, as Chromium reads it (D-904, `SHOWN_FORMATS`) |
| Annotated copies baked in the old frame | Local Canon (09 One frame, `09-screenshot-capture.md:1277`) | Rebaked by the next scan (D-909) |
| How that rebake writes | Local Canon (review R1-F1) | Staged in the same folder and published by `os.replace`, keeping the copy's format; rolled back on failure; the next scan's recovery returns a result and never raises (D-910) |
| Rows recorded before the change | Local Canon | DIMS_REFRESH (D-906) |
| Crop and export frame | Local Canon | The shown frame (D-907) |
| Test layout, gate and split | Local Canon | D-908 |

#### Pins that move

These existing tests change, are named here and are approved scope, not M-7:

- **AC-130.21** (`tests/e2e/test_api_capture_crop.py:763`, LF): the three restore lines go (MEU-145 item 3). It runs at Green only: its `_stack` uses `TestClient(app)`, which raises on a 500, so before Green it would fail by setup.
- **AC-136.7** (`tests/unit/test_capture_export_adapter.py:672`, LF): renamed and flipped (MEU-146 item 7). It runs at Green only: before Green `source_size=(300, 400)` raises `ConflictError`.

#### Existing test assertions

No existing assertion changes beyond the two pins above, so D-905 and D-909 make no M-7 hit. Checked at plan time against every test of the byte-exact route, the sidecar and the fakes (expert pass, M-7 line):

- **The two fakes gain methods, not assertions.** `FakeCapturePort.read_shown` returns `path.read_bytes()` and `shown_tag` returns 1, so AC-36.10 (`tests/unit/test_capture_service.py:381-399`, which asserts `b"orig-bytes"` from `read_image`) and AC-36.9 (`:366-370`, which asserts the sidecar keys are exactly `{"version", "annotations"}`) see what they see today. The same two methods on `FakeAnnotate` (`tests/unit/test_capture_export_service.py:92-138`) keep its `annotate_and_save` cases (`:170`) as they are. `_RenderingPort` (`tests/unit/test_capture_render.py`) reaches `FakeCapturePort` through `__getattr__`, so it needs no change. The frames and sheet fakes (`test_capture_frames_service.py:110`, `test_capture_sheet_service.py:180`) never list annotated shots or call `read_image`.
- **Real-adapter route tests use untagged files.** No existing test sends a no-parameter `GET /captures/{id}/image` for a tagged file, so every byte-exact assertion on that route stays byte-exact under READ_SHOWN. AC-136.4 uses tag 1. AC-129.5 (a tagged region import) goes through `inspect_import` and `write_upright_png`, which do not change. `tests/unit/test_capture_adapter.py:465-470` raises bare errors; AC-104.3 already expects the fixed message.
- **Real-adapter sidecar tests use untagged files**, so BAKE_MARKER writes no key and their exact-key checks hold.
- **`_rebake_annotated` does not change** (D-910). Its one caller is revert (`services/capture.py:1642`), and its pin is the ANNOTATED_CONSISTENCY case in `tests/e2e/test_api_capture_flatten.py:360`; both see today's code. STAGED_REBAKE is a new helper that only the scan calls, so no existing test reaches it: every existing scan test lists untagged shots whose sidecar has no key, which `shown_tag` 1 matches.

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modify | CRLF, kept | `PROBE_FIXED`; `SHOWN_FORMATS`, `SHOWN_OPEN`, `PROBE_SWAP`, `SHOWN_TAG`, `READ_SHOWN`, `VIEW_SHOWN`, `ICC_KEEP`, `CROP_EXPORT_FRAME` |
| `packages/core/src/avkit_core/ports/capture.py` | modify | CRLF, kept | `ImageAnnotatePort.shown_tag` and `read_shown` |
| `packages/core/src/avkit_core/services/capture.py` | modify | CRLF, kept | `SCAN_SKIP`, `KEEP_ROW`, `SKIP_LOG`, `DIMS_REFRESH`, `READ_SHOWN` (`read_image`), `BAKE_MARKER`, `STALE_BAKE`, `STAGED_REBAKE` |
| `packages/api/src/avkit_api/routes/captures.py` | modify, comment only | CRLF, kept | The three `#` lines at `:424-426` (MEU-146 item 4) |
| `tests/unit/test_capture_service.py` | modify, fake only | CRLF, kept | `FakeCapturePort.read_shown` and `shown_tag` (§Existing test assertions) |
| `tests/unit/test_capture_export_service.py` | modify, fake only | LF, kept | `FakeAnnotate.read_shown` and `shown_tag` |
| `tests/orientation_fixtures.py` | new | LF | The Pillow fixture builder (MEU-146 item 6) |
| `tests/unit/test_capture_scan_unreadable.py` | new | LF | AC-145.1 to AC-145.11 |
| `tests/unit/test_capture_orientation.py` | new | LF | AC-146.1 to AC-146.10, AC-146.12 to AC-146.14, AC-146.20 to AC-146.26 |
| `tests/e2e/test_api_capture_scan_unreadable.py` | new | LF | AC-145.12, AC-145.13 |
| `tests/e2e/test_api_capture_orientation.py` | new | LF | AC-146.15 to AC-146.18, AC-146.27, AC-146.28 |
| `tests/e2e/test_api_capture_crop.py` | modify | LF, kept | AC-145.15 (the AC-130.21 move) |
| `tests/unit/test_capture_export_adapter.py` | modify | LF, kept | AC-146.11 (the AC-136.7 flip) |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | LF, kept | AC-146.19 appended |
| `docs/build-plan/09-screenshot-capture.md` | modify | CRLF, kept | One `Delivered (Session 75)` note under each of the two anchors |
| `.agent/context/known-issues.yaml` | modify (tool) | LF, kept | The two issues resolved through `issue-resolve.py` |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/meu-status.yaml` | modify (tool) | LF, kept | MEU-145 and MEU-146: `ready_for_review`, then `approved` (H2-2) |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | regenerate | LF | `meu_status.py render` |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | modify | LF, kept | §6 row 75 only: `executed (Session 75)` and this plan folder |

Line endings were measured with Python bytes at plan time (`C:/Temp/av-kit/capture-inbox-probe/s75-plan-eol.txt`); row 0 records them again with each file's SHA-256 in `s75-anchors.txt`. A CRLF file is read and written with `newline=""` from CRLF text. The session gate checks the line endings of every file in this table again.

### Project files

- **Plan-local scripts**, all in this plan folder: `baseline.ps1`, `red-check.py`, `identity.py`, `id-length.py`, `issue-resolve.py`, `session-gate.ps1`. They were written at plan time and are inputs the review reads; row 0 runs their selftests.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt` (each porcelain line with the path's SHA-256), and in the scratch folder `s75-anchors.txt` and `row0/`.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the two handoffs, the rolling reviews and the reflection.
- **Read, never changed:** `mcp-server/src/toolsets/capture.ts`, `mcp-server/src/toolsets/registry.ts`, `mcp-server/tests/capture.test.ts`, `tests/unit/test_capture_adapter.py`, `CaptureViewport.tsx`, `CaptureFilmstrip.tsx`, `capture-clipboard.ts`, `ui/src/main/clipboard-image.ts` (all CRLF), `tests/unit/test_capture_render.py` (LF), `docs/build-plan/build-priority-matrix.md` and `openapi.committed.json`. Copy and the MCP image call are fixed from the server (READ_SHOWN), so their code stays as it is. `s75-anchors.txt` records their hashes and the gate's `scope-paths` refuses a change since row 0.

### Sibling overlap

The plan binds each shared file to its content at row 0, not to `HEAD`, and changes only its own entries or lines in it (D-908). Where a sibling may already have changed a file this plan relies on, the row-0 `shapes` step checks that every section this plan reads is still there by name, rather than that the file equals `HEAD`.

| File | Siblings | Rule |
|---|---|---|
| `ui/tests/e2e/capture-inbox.test.ts` | Session 78 changes every E2E launch site (grouping §2) | This plan appends one test that calls the existing `launchApp()` and adds no launch site. If Session 78 runs first and changes `launchApp`, the `shapes` step still finds it by name and the test uses it as it stands |
| `.agent/context/known-issues.yaml`, `known-issues.md` | Session 79 changes `tools/issue_triage*`, which row 6 runs but never edits; Session 83 rewrites lines that name the home folder (grouping §2) | Row 6 changes only the two issues' `status`, `verification` and `resolution_path`, names no home path, and binds to the row-0 hash (S3) |
| `meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md` | Sessions 77, 80, 81, 82 | Only MEU-145's and MEU-146's rows change, through `meu_status.py` (S11) |
| Grouping §6 table | Every session of the grouping | Only row 75 changes |
| `docs/build-plan/09-screenshot-capture.md` | None in this grouping | Only the two Delivered notes are added; row 5 counts them |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

No sibling session edits a product or test file of this plan other than `capture-inbox.test.ts` (grouping §3).

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Turning a tagged WebP | out-of-scope | — | Chromium does not turn it, so its shown frame is the stored one (D-904). An imported WebP is still turned by `write_upright_png` (D-417); the handoff names that difference as a residual for triage |
| Rewriting or copying the user's inbox file | out-of-scope | — | M-2; D-903 B and C lost |
| `sheet` and `sheet_from_video` (`adapter.py:644`, `services/capture.py:790`, `services/capture.py:1030`) | out-of-scope | — | Video frames only, never an inbox photo |
| The inbox resolver's `InboxPathError(f"{resolved} is not a file")` (`services/capture.py:2089`) | out-of-scope | — | Not the scan path, and neither issue names it; the MEU-145 handoff names it as a residual for triage |
| An annotated copy with no sidecar | out-of-scope | — | STALE_BAKE needs the saved marks to rebake; with no sidecar it leaves the copy, and the reconcile step already clears a path whose file is gone. The handoff names it as a residual |
| Marks clamped by an earlier GUI save (`services/capture.py:1500-1502`) | out-of-scope | — | The cut part was never stored, so nothing can restore it (§User Review Required) |
| An untagged region view drops the colour profile | out-of-scope | — | Today's behaviour (`_encode_view`, `adapter.py:368-382`); ICC_KEEP covers only the turned paths. Residual for triage |
| `inspect_import` and `write_upright_png` read the tag through `getexif()` | out-of-scope | — | An imported XMP-only or raw-profile file is turned on import, though Chromium does not turn it. Import writes a new upright PNG (D-417), so it never disagrees with the GUI after import; residual for triage |
| The other frames of an MPO | out-of-scope | — | READ_SHOWN and the views keep only the first frame, which is the one Chromium shows (`s75-plan-probe-extra-electron.txt`) |
| A flag field for skipped files in the list | out-of-scope | — | M-4 (D-900) |
| `annotate_and_save` and revert still bake onto the live copy and write the sidecar in place (`services/capture.py:1503-1515`, `:2009-2026`) | out-of-scope | — | Both run when the user asks, and the user sees an error at once; STAGED_REBAKE covers only the unattended scan (D-910). The handoff names them as a residual for triage |
| A `.rebake-prior` or `.rebake-new` file that cannot be deleted (read-only or locked) | out-of-scope | — | Recovery retries it on each scan, counts it once in the warning and never fails the list; removing the shot (`remove`, `:1587-1598`) does not delete it, as it deletes only known names, and av-kit does not clear a read-only attribute. Residual for triage |

## BUILD_PLAN.md Audit

MEU-145 and MEU-146 are registered (`meu-status.yaml:3780` and `:3806`, `pending`, matrix 9.43 and 9.44; dependencies MEU-36, MEU-84, MEU-130 and MEU-35, MEU-36, MEU-128, MEU-129, all `approved`). Row 6 sets both to `ready_for_review` with this plan's `execution_plan` through `tools/meu_status.py update`, and H2-2 sets both to `approved`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/capture-inbox-probe/s75-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/capture-inbox-probe/s75-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` (written at plan time; a copy of Session 72's with this plan's checks) runs fail-fast, in this order:

1. **Rulings (S9).** Exactly one `> **Status:**` line, holding `said to execute (USER_EXPLICIT <date> '<words>')`.
2. **Queue (S8).** MEU-35, MEU-36, MEU-84, MEU-128, MEU-129, MEU-130 and MEU-136 `approved`; MEU-145 and MEU-146 `pending`; `6aaf9b0` an ancestor of `HEAD`.
3. **Shapes (S7).** Every shape this plan calls is present by name (the adapter methods, the scan's uncaught probe and its update test, the reconcile comment, `_upsert_shot`'s and `_import_in_place`'s early returns, `read_image`, `parse_sidecar_document`'s unknown-key rule, `ImageAnnotatePort`, the two fakes, the image route and its D-411 comment, the MCP list pin, AC-136.7, AC-130.21 and its restore lines, `launchApp`, the two 09 anchors), and every name, label and file this plan adds is absent (`read_shown`, `shown_tag`, `baked_orientation`, `STALE_BAKE_FAILED_EVENT`, `tests/orientation_fixtures.py` among them). This is the compatibility check for files a sibling may also have changed. Because the new names are absent only before row 1, a re-run of row 0 after any row has started stops here; re-baselining is Mat's call.
4. **Row-0 copies (S2, content-bound).** Each product, test and read-only file this plan touches or relies on, plus 09 and `openapi.committed.json`, is copied byte for byte to `C:/Temp/av-kit/capture-inbox-probe/row0/<path>`. A file that differs from `HEAD` is reported, never fatal: an earlier session may have left it changed, and the copy is then the base for every later check and for the execution review's delta. The copies are written only after the shapes step passes, so a re-run after row 1 can never overwrite them with edited content; a re-run before row 1 rewrites each copy from the same bytes.
5. **Tree state.** `baseline.sha` holds `HEAD`; `baseline-dirty.txt` holds `git status --porcelain --untracked-files=all` with each path's SHA-256.
6. **Anchors.** `s75-anchors.txt` holds the line endings, size and SHA-256 of every §Files Modified and read-only file; the four new test files and `tests/orientation_fixtures.py` must be `absent`. Row 6 reads the register's hash from it.
7. **Environment (S4).** `uv sync --frozen --offline --all-packages`; `ui` and `mcp-server` `node_modules` match their locks (not reinstalled: the running avkit MCP servers use them); the pinned FFmpeg pair answers `-version`.
8. **Base receipts.** The Python suite (`s75-base-py.txt`), Vitest (`s75-base-ui.txt`), the MCP build and suite (`s75-base-mcp-build.txt`, `s75-base-mcp.txt`), the UI build and the capture Electron file (`s75-base-ui-build.txt`, `s75-base-e2e.txt`), and ruff (`s75-base-ruff.txt`). Their failures are recorded, not fatal.
9. **Selftests.** `red-check.py`, `identity.py` and `id-length.py` `--selftest`, and `issue-resolve.py --help`.

### 2. Stubs, Red, then Green

- **Row 1 adds type-only stubs and the fixture builder** (Session 53 RULE-2): `shown_orientation` returns 1, `_open_shown` opens and loads without turning and returns `(image, 1)`, `shown_tag` returns 1 and `read_shown` returns `path.read_bytes()` on the adapter and the port, `SHOWN_ORIENTATION_FORMATS`, `SCAN_SKIPPED_EVENT` and `STALE_BAKE_FAILED_EVENT` exist, the two fakes gain `read_shown` and `shown_tag`, and `tests/orientation_fixtures.py` is written in full (it is test input, not product code). Nothing in the product calls the stubs, so the existing capture tests pass unchanged (the row's sweep, which includes `test_capture_export_service.py` and `test_capture_render.py`).
- **Each Red receipt holds an assertion failure, never a setup failure.** Row 2 runs the four new files, writes each receipt's `.exit` file, and `red-check.py --require test_ac_<meu>_<n>` checks AC-145.1 to AC-145.13 and AC-146.1 to AC-146.4, AC-146.6 to AC-146.10, AC-146.12 to AC-146.18, AC-146.20 and AC-146.22 to AC-146.27.
- **Guards pass in Red.** AC-146.5, AC-146.21 and AC-146.28 pin behaviour that already holds and must survive Green. AC-146.19 runs in row 2 against row 0's UI build (this plan changes no UI source) and must pass; a fail is S14.
- **Moved pins run at Green only** (§Pins that move): AC-145.15 in row 3, AC-146.11 in row 4.
- **Expectations stay immutable in Green.** A Green row that needs a changed expectation stops on S12.
- **Line endings.** Each Green row ends with a Python-bytes check of the files it wrote.

### Session gate (H1-2)

`session-gate.ps1` (written at plan time) follows Session 72's shape: one receipt per step in `C:/Temp/av-kit/capture-inbox-probe/`, named `s75-D6-<step>.txt`; fail-fast, with later steps printed as `not_run`; the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two `tested_state` values must match |
| Static | `py-types` (`pyright packages/`); `py-lint` (`ruff check packages/ tests/`); `ui-types`; `ui-lint`; `mcp-types`; `task-contract`; `scope-paths` (every path changed since `baseline.sha` is in §Files Modified, this plan folder, the closeout artifacts or `baseline-dirty.txt`; every `baseline-dirty.txt` path outside this scope, `openapi.committed.json` included, keeps its row-0 hash; another session's plan folder is reported only; `HEAD` moving is reported only); `route-comment-only` (every line that differs between `routes/captures.py` and its row-0 copy is, on both sides, blank or starts with `#` once stripped); `red-check-selftest`; `id-length` on the four new files |
| Fresh full | `py-tests` (`pytest tests/ --tb=short -q -rfE`; exit 1 passes only when every FAILED id also failed in `s75-base-py.txt`); `openapi` (`tools/export_openapi.py --check openapi.committed.json`; the route's docstring feeds it, so a docstring change fails here); `ui-tests`; `ui-build`; `mcp-build`; `mcp-tests` (AC-145.14); `state-render`; `issues-render` |
| Runtime | `ui-electron` (`npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts`, AC-146.19 and the existing capture specs) |
| Skipped, with reason | `mcp-audit` (live network and the installed avkit servers); `build-record` (no build) |

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A required Red passes early, or a Red receipt fails `red-check.py` | Fix the test setup; do not move to Green |
| S2 | A scoped file differs from `HEAD` at row 0 | Reported only; its row-0 copy is the base. It stops only through S7 (a shape this plan relies on is missing) |
| S3 | A path outside scope changes, a `baseline-dirty.txt` path changes its SHA-256, or `known-issues.yaml` no longer has its row-0 hash at row 6 | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S4 | `uv sync`, a lock-sync check or the FFmpeg pair fails | Stop; bring the receipt to Mat |
| S5 | A test reaches the network or the clipboard, or reads user data (the real inbox, the app database, the settings file) | Stop; rewrite the test on `tmp_path` |
| S6 | A REST or MCP shape change appears (`openapi --check` fails, `openapi.committed.json` changes, a line of `routes/captures.py` other than a `#` comment changes, or a flag field is needed) | Stop: M-4, Mat's call |
| S7 | A shape this plan calls is missing, or a name it adds already exists | Stop; re-read the anchors with Mat |
| S8 | The queue is wrong | Stop |
| S9 | The Status line lacks the execute words | Stop; the rows do not run |
| S10 | Codex is unavailable or the ledger refuses | Mat |
| S11 | `meu-status.yaml` has been changed by another session since row 0 | Copy the status files to `C:/Temp/av-kit/capture-inbox-probe/pre-status/` first, change only MEU-145's and MEU-146's fields through `meu_status.py`, and prove it with `render --check` and a diff against the copy (Session 61 RULE-5) |
| S12 | A contract or AC needs to change, or Green needs a changed expectation | Stop for Mat (M-8); never edit an expectation in Green |
| S13 | An existing test outside AC-145.14, AC-145.15 and AC-146.11 fails after Green | Stop: that is an M-7 question (§4a), not a fix |
| S14 | AC-146.19 fails: Chromium turns a WebP or one of the four Pillow-only PNG and JPEG fixtures, or does not turn a JPEG, MPO or PNG | Stop; the D-904 premise is wrong; brief Mat |
| S15 | A raw path, a file name or Pillow's text reaches a log line or a response | Fix it inside the row; the AC is not met until it is gone |

## Decision Log

> [!NOTE]
> D-900, D-901, D-902 and D-906 to D-910 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. D-903 hit M-5 and M-6, and D-904 and D-905 hit M-6, so they are briefs (below); they are settled by Mat's hand-over for this grouping and recorded `autonomous` with their `mandatory:` lists kept. The §5a expert pass changed D-905 (narrowed option C, still M-6 only) and added D-909 (old annotated copies); neither hits M-2 (D-905 reads the user's file and never writes it; D-909 rebakes only av-kit's own annotated copy and sidecar), M-4 (no route, header, media type, OpenAPI or MCP shape changes; the sidecar is not a wire and its parser ignores unknown keys), M-7 (§Existing test assertions) or M-8 (09's One frame rule, `09-screenshot-capture.md:1277`, already covers the bake). No item hit M-2: rewriting the user's file is option C of D-903, which is not recommended and was not handed over. There are no STOP items, so `open_decisions` is empty. Under the new HDP §6 a decision that applies an existing ruling gets no new record: D-417, D-421, D-411, D-507, D-613 and the triage rows D-802 and D-803 are applied, not re-recorded. The reflection does not restate the grouping rows (D-813 to D-817); the closeout reads them in the grouping's §8 through `grouping_source` and `--decision-source`, and the issues' rows through `--decision-issue`. The grouping's old "Carry-forward" wording (§9, `:325-327`) is ignored under the new §6. Plan review round 1 (R1-F1) added D-910, which stages STALE_BAKE's writes, and round 2 (R2-F1) gave its recovery a result that never raises; it hits nothing on the list either: the files are av-kit's own copy and sidecar, and `_rebake_annotated` and every existing assertion stay as they are (§Existing test assertions).

```yaml
decision_log:
  - id: D-900
    stage: planning
    question: "Does the scan skip a file the probe can't read, or list it with a flag?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Skip it: no row is added, the list holds every readable shot, and the file is tried again on the next scan."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1264 — List: a file the probe can't read never fails the list; skip or flag chosen at plan time"
      - "docs/build-plan/09-screenshot-capture.md:1266 — Retry: a failed file is tried again on the next scan"
      - "packages/api/src/avkit_api/routes/captures.py — CaptureShotOut has no field for an unreadable file"
      - "mcp-server/tests/capture.test.ts:24 — MCP list is GET /captures"
    research: { engine: none, sources: [] }
    reasoning: "09 leaves the choice open and asks for every readable shot to list and a retry on the next scan; skipping meets both with no new field. A flag would need a field in CaptureShotOut and the MCP list, which is an API shape change (M-4) that 09 does not specify, and a row for a file with no size to record. Two-way: one loop."
  - id: D-901
    stage: planning
    question: "What happens to the existing row of a file that becomes unreadable?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "KEEP_ROW: the row stays exactly as it was; the delete pass still removes only rows whose original is not a file. AC-130.21's restore lines are removed."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1266 — Retry: a half-written screenshot lists once it is complete"
      - "docs/build-plan/09-screenshot-capture.md:1267 — Tests: AC-130.21 no longer needs to restore the source"
      - "tests/e2e/test_api_capture_crop.py:771-781 — the restore and the list that expects the same ids"
    research: { engine: none, sources: [] }
    reasoning: "A file being rewritten in place is briefly unreadable; deleting its row would drop its marks and sidecar link, and AC-130.21's follow-up expects the same ids. Hiding the row from the list lost: the list reads rows, not files, so it would need a new filter for a state that heals on its own. Two-way."
  - id: D-902
    stage: planning
    question: "What do the probe, bake and render say about an unreadable file, and what does the scan log?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Fixed, path-free messages: 'no file at that path' for a path that is not a file, 'the image could not be opened' for any other failure (catch Exception). The scan catches InboxPathError and OSError per file and logs one capture.scan_skipped warning with only a count when the skipped set changes and is not empty."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1265 — No path: no message, log line or Console field carries the path or Pillow's text"
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:765 — D-421, the fixed refusal"
      - "packages/core/src/avkit_core/services/capture.py:727 — the existing 'no file at that path'"
      - "C:/Temp/av-kit/capture-inbox-probe/s75-plan-probe-pillow.txt — a damaged IDAT raises SyntaxError"
    research: { engine: none, sources: [] }
    reasoning: "Reusing the two messages the service and the view already give keeps the Console wording one set. Catching Exception is how view and crop already catch SyntaxError and ValueError. A count-only event tells the user something was skipped without a name; logging on every scan lost because the GUI lists often and the line would repeat. Two-way."
  - id: D-903
    stage: planning
    question: "How does the app honour the orientation tag of a scanned or registered file?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-5, M-6]
    chosen: "A: keep the user's file as it is and apply the tag wherever pixels or sizes are read: one helper (_open_shown) for view, crop, bake, render and export, a width and height swap in probe, and the same tag reader for the plain download (D-905)."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1277-1278 — One frame and Route: a plan-time brief because the inbox holds the user's own files"
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:703 — D-417: imports write an upright PNG; leaving orientation to the reader lost there"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:539 — write_upright_png"
      - "C:/Temp/av-kit/capture-inbox-probe/s75-plan-probe-electron.txt — Chromium turns a tagged JPEG and PNG"
      - "C:/Temp/av-kit/capture-inbox-probe/cip-expert-pass.txt — the expert pass: D-903 holds, with the undo, flatten, probe and gap corrections"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this brief set. M-5 because the route is a product fork 09 leaves open, and M-6 because D-417 rejected leaving orientation to the reader for imports. That reason was that every view, mark and crop would have to rotate; one helper used by every pixel read makes it one place, and an import owns its copy while a scanned file is the user's own. B, an upright copy, touches the scan, register, remove and delete, puts a second file in the user's inbox, and turns a JPEG into a larger PNG. C, rewriting the file, changes the user's own data (M-2) and is not offered. D, keeping things as they are, leaves the filed defect. Two-way in code: the helper can be removed and DIMS_REFRESH puts the stored sizes back on the next scan. Not two-way in recorded data: marks placed under A change meaning on undo, and flatten, crop, convert and export outputs stay upright."
  - id: D-904
    stage: planning
    question: "Which formats does the app turn by their tag?"
    resolution: autonomous
    class: two-way
    mandatory: [M-6]
    chosen: "JPEG, MPO and PNG, not WebP, because that is what Chromium turns; AC-146.19 pins it in the Electron suite."
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1273 — the residual says a JPEG or WebP tagged 5 to 8"
      - "C:/Temp/av-kit/capture-inbox-probe/s75-plan-probe-electron.txt — Electron 42.11.18, Chrome 148: JPEG and PNG turned, WebP never"
      - "C:/Temp/av-kit/capture-inbox-probe/s75-plan-probe-pillow.txt — Pillow 13.0.0 reads an MPO as format MPO with tag 6"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this brief set. M-6 because 09's note names WebP and the probe of the shipped Chromium shows it never turns a WebP; 09's own rule is the frame the GUI shows, so the probe decides. Turning WebP too lost: the app would size and mark a WebP turned while the GUI shows it upright. JPEG only lost: Chromium turns a tagged PNG and an MPO is a JPEG camera file. Two-way: one frozenset."
  - id: D-905
    stage: planning
    question: "What do a whole-image view and the plain image download of a tagged file return?"
    resolution: autonomous
    class: two-way
    mandatory: [M-6]
    chosen: "Narrowed C (changed by the expert pass): for a JPEG, MPO or PNG with a tag other than 1, the whole view at scale 1 and the no-parameter image GET both return upright, untagged bytes in the file's own format at the whole frame, with its colour profile kept; an untagged or tag-1 file and every WebP still get their own bytes, byte for byte (D-410 RETURN_UNCHANGED)."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:596-601 — D-410 RETURN_UNCHANGED: the file's bytes for a whole-image frame at scale 1"
      - "packages/api/src/avkit_api/routes/captures.py:425 — the route comment that credits the byte-exact answer to D-411"
      - "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:611-616 — D-411 FRAME_HEADERS: the five X-Capture headers, for the headers only"
      - "mcp-server/src/toolsets/registry.ts:410-439 — the MCP image call sends no region and reads the no-parameter route"
      - "ui/src/renderer/src/features/capture/capture-clipboard.ts:85 — Copy of an unmarked shot fetches the no-parameter route"
      - "ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx:208 — the GUI reads the no-parameter GET and Chromium turns it"
      - "C:/Temp/av-kit/capture-inbox-probe/cip-expert-pass.txt — finding 1, the widening; finding 5, the colour profile"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this brief set. M-6 because D-410 and the route comment say the whole view and the plain download are the file itself, and for a tagged file that is not the shown frame the X-Capture headers describe. D-410 and D-411 were autonomous, not USER_EXPLICIT, so the conflict is handable. The expert pass showed the plain download feeds Copy (a tagged PNG pastes sideways) and the MCP image call (stored pixels under shown headers), so turning only the scaled whole view left both wrong. Re-encoding only the tagged case keeps the byte-exact answer for every other file. Costs: a header parse per plain download, a decode and re-encode per load of a tagged file (lossy JPEG at quality 90), an MPO's other frames and the non-orientation EXIF dropped, and a re-encoded PNG can pass the size cap. The GUI display does not change, since Chromium turned the file anyway. No M-4: same media type, headers and docstring. Two-way: one condition in read_shown and view."
  - id: D-906
    stage: planning
    question: "How do rows recorded before this change get the shown size?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "DIMS_REFRESH: the scan, _upsert_shot and _import_in_place update a row when its width or height differs from the probe, as well as when its file size does."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:629 — the scan updates only on a size change"
      - "packages/core/src/avkit_core/services/capture.py:2119 — _upsert_shot's early return"
      - "packages/core/src/avkit_core/services/capture.py:754 — _import_in_place's early return"
    research: { engine: none, sources: [] }
    reasoning: "Turning the frame does not change the file size, so without this a tagged shot listed before the change would keep its stored size forever. A one-off migration lost: it rewrites the database for a value the next scan can compute. Two-way."
  - id: D-907
    stage: planning
    question: "What frame do crop and export cut?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The shown frame, with no orientation tag in the output; AC-136.7 is flipped from a characterisation to the fixed behaviour."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md:460 — D-613: AC-136.7 records this issue's effect without fixing it"
      - "docs/execution/plans/2026-11-08-capture-crop-copy/implementation-plan.md:118 — CROP_PIXELS never calls exif_transpose"
      - "docs/build-plan/09-screenshot-capture.md:1277 — One frame"
    research: { engine: none, sources: [] }
    reasoning: "Crop and export take a box and source size in the frame the list reports, so once probe reports the shown frame they must cut it or the size check refuses every tagged shot. D-613 said in its own words it fixes nothing, so flipping its pin applies the fix it left open. Two-way."
  - id: D-908
    stage: planning
    question: "Where do the tests live, what does the gate run, how does the session bind to other sessions' work, and is a 75b needed?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Four new LF test files, one LF fixture builder, the two moved pins, two fakes extended and one appended Electron test; the gate of §Session gate; every baseline, scope and closeout check bound to row-0 content, not HEAD; no 75b, with compact_continue at the MEU boundary; if a split is ever needed it falls at that boundary, MEU-145 in 75 and all of MEU-146 in 75b."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:141 — Split flag: 75b if MEU-145's handoff passes about 50% of context"
      - "docs/execution/plans/2026-11-14-capture-shapes-steps/session-gate.ps1 — the capture gate shape"
      - "tests/unit/test_capture_service.py:67 — FakeCapturePort, imported by the new service tests"
    research: { engine: none, sources: [] }
    reasoning: "Route A touches one helper and six adapter methods plus three service tests, which Session 58 and 59 sized as one session each with more files. The expert pass adds READ_SHOWN, SHOWN_TAG, ICC_KEEP, BAKE_MARKER and STALE_BAKE (two port methods, one service step, a comment-only route edit, two fakes and nine ACs), which makes the session medium-large but still one MEU's worth of related work: MEU-145 is small, so the 50% trigger is still unlikely, and compact_continue at the MEU boundary keeps the option without splitting the registers. The split point, if needed, is the MEU boundary, because READ_SHOWN and STALE_BAKE cannot ship apart from the frame change they follow. Splitting now lost: both MEUs change probe, and a 75b would run the same baseline and gate twice. Binding to row-0 content follows the sibling reviews: an earlier session may leave a scoped file changed and uncommitted. Two-way."
  - id: D-909
    stage: planning
    question: "What happens to an annotated copy of a tagged shot that was baked in the stored frame before this change?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "STALE_BAKE: the bake records the frame it used as baked_orientation in the sidecar (only when not 1), and when a shot's shown tag differs from that value the next scan rebakes the annotated copy from the saved marks and rewrites the key; the rebake is staged and published as STAGED_REBAKE (D-910) describes, so a failure leaves the copy, the sidecar and the row as they were and logs one count-only capture.stale_bake_failed warning."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1277 — One frame: the bake uses the frame the GUI shows"
      - "packages/core/src/avkit_core/services/capture.py:1801-1803 — export uses the annotated copy when marks exist, sized by the row"
      - "packages/core/src/avkit_core/services/capture.py:2009-2026 — _rebake_annotated, the revert's rebake"
      - "packages/core/src/avkit_core/services/capture.py:331-332 — parse_sidecar_document ignores unknown top-level keys"
      - "C:/Temp/av-kit/capture-inbox-probe/cip-expert-pass.txt — finding 2: the 409 for tags 5 to 8, the silent bake for tags 2 to 4, the clamped marks"
    research: { engine: none, sources: [] }
    reasoning: "Without it a tag 5 to 8 shot annotated before the change answers export with a 409 that listing never clears, and a tag 2 to 4 shot keeps a mirrored or 180-degree bake with no error. Keying on size lost: it misses tags 2 to 4, where the size does not change. Clearing the copy lost: the marks stay saved, so a clear leaves a shot whose marks are not shown until the user saves again; a rebake uses the same marks and the same code revert already runs. Not M-2: the copy and the sidecar are files av-kit wrote, never the user's original. Not M-4: the sidecar is a local file, not a wire, and its parser already ignores unknown keys. Not M-7: every existing sidecar test is untagged, so no key is written. Not M-8: 09's One frame rule already names the bake. Marks clamped by an earlier save cannot be recovered and are named in User Review. Two-way: remove the step and the key is ignored."
  - id: D-910
    stage: planning
    question: "How does the scan's rebake of an old annotated copy write its files so that a failure loses nothing?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "STAGED_REBAKE: a new scan-only helper, _restage_annotated, bakes to a .rebake-new file and writes the sidecar to a .rebake-new file in the same folder, keeps the copy's own path and format, then moves the old copy and sidecar to .rebake-prior names and the new files into place with os.replace, deleting the prior files only after both are published; any failure moves everything back. The next scan's recovery never raises: a failed delete of a leftover is counted and ignored, and a failed restore keeps the prior file and both row links and skips that shot's RECONCILE clearing and rebake for the scan; both are counted in the same count-only warning. _rebake_annotated, annotate_and_save and revert do not change."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/cip-plan-review-round-1.md — R1-F1: the rebake overwrote the live copy, could delete siblings first and wrote the sidecar in place"
      - "packages/core/src/avkit_core/services/capture.py:2009-2026 — _rebake_annotated bakes onto the target and unlinks every other sibling"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:838-866 — the PNG and lossy writers save to the output path and unlink it on OSError"
      - "packages/core/src/avkit_core/services/capture.py:600-607 — the scan lists only scan extensions that are not annotated names"
      - "C:/Temp/av-kit/cip-plan-review-round-2.md — R2-F1: recovery's delete and restore fail on Windows for a read-only or locked prior"
    research: { engine: none, sources: [] }
    reasoning: "The scan runs unattended on every list, so its rebake must never leave a shot worse than it found it. Baking to the live path lost: the adapter unlinks that path on a write error, so the old copy goes. Changing _rebake_annotated lost: revert uses it and its flatten pin would need a look, for a path the user starts and sees fail at once. Using the format setting lost: a setting changed since the save would rename the copy and delete the old one, and an invalid setting would fail every scan. Temp names in the same folder keep each os.replace on one volume, so each publish is one rename, and the scan never lists those names. Not M-2: only av-kit's own copy and sidecar are written, never the original. Not M-4 or M-7: no shape and no existing assertion changes. Recovery returns a result and never raises (review R2-F1): on Windows a read-only or share-locked prior makes its delete or restore fail, and a raise would fail every list while going on to RECONCILE would clear the link the restore needs. Two-way: remove the helper and STALE_BAKE goes with it."
open_decisions: []
```

Expert pass (fresh context): 3 briefs. Holds: D-903, D-904. Changed: D-905. Not adopted: none (receipt `C:/Temp/av-kit/capture-inbox-probe/cip-expert-pass.txt`). The pass's other findings are adopted as D-909 (old annotated copies), SHOWN_FORMATS's EXIF-block rule, AC-146.19's checked fixtures and MPO case, PROBE_SWAP, ICC_KEEP, the D-903 undo and flatten wording, the `child.resolve()` fix in SCAN_SKIP, and the file names in §Out of Scope.

### D-903: How does the app honour the orientation tag of a scanned or registered file?

**I recommend A: keep your file exactly as it is, and turn the picture by its tag wherever the app reads pixels or sizes.** One helper does it, and every place that reads pixels uses it: the region view, Copy and Crop, Save (bake), the preview render and Export; the size the list reports comes from the same tag reader. Flatten and revert follow through Save and the size check. The GUI's thumbnails and main view need no change: they load the file itself and Chromium already turns it. A changes nothing in your inbox. Two paths of the app's own read the plain download, which returned your stored pixels: Copy of an unmarked shot (a tagged PNG pastes sideways) and the MCP image call (stored pixels under shown-frame headers). D-905 now turns that download too, so both get the shown frame. Annotated copies baked before the change are rebaked by the next scan (D-909). Flatten of a tagged PNG writes upright pixels with no tag, and keeps a backup only when `capture.flatten_backup` is on; today's flatten already writes the stored pixels with no tag, so the picture turns when you flatten, and A stops that. Undoing it is two-way in code (remove the helper, and the next scan puts the stored sizes back) but not in recorded data: marks placed under A change meaning on undo, and flatten, crop, convert and export outputs stay upright.

- B: write an upright copy next to each tagged file. Touches the scan, register, remove and delete (two files per shot), and a JPEG becomes a larger PNG in your inbox.
- C: rewrite your file upright. Changes your own data (M-2), so it is not offered for hand-over.
- D: keep things as they are: a tagged photo lists and marks in its stored frame while the GUI shows it turned.

Refs: `docs/build-plan/09-screenshot-capture.md:1269-1279`, `adapter.py:461,473,539,549,603,623,679`, `CaptureFilmstrip.tsx:208`, `capture-clipboard.ts:85`, `registry.ts:410-439`, D-417, `s75-plan-probe-electron.txt`, `cip-expert-pass.txt`, `CAPTURE-EXIF-SCANNED-ORIENTATION`, MEU-146, AC-146.2 to AC-146.18, M-5, M-6.

### D-904: Which formats does the app turn by their tag?

**I recommend A: JPEG (and MPO, the multi-frame JPEG cameras write) and PNG, not WebP.** That is exactly what the app's own Chromium turns when it shows a file (checked on this PC: a tagged WebP stays as stored), and 09's rule is the frame the GUI shows. The app reads the tag only where Chromium does, the EXIF block: a tag kept only in XMP, in a PNG text chunk, or in a PNG `eXIf` chunk after the image data is not turned, because Chromium does not turn those either. 09's note says "JPEG or WebP", so A corrects the note against the probe, and an Electron test pins the premise so a Chromium change is caught. It can fail if a later Electron starts turning WebP; that test then fails and the set is one line.

- B: JPEG, PNG and WebP, as 09's note reads. A WebP would be sized and marked turned while the GUI shows it upright.
- C: JPEG only. A tagged PNG would stay wrong.
- D: keep things as they are: no format is turned.

Refs: `docs/build-plan/09-screenshot-capture.md:1273`, `s75-plan-probe-electron.txt`, `s75-plan-probe-extra-electron.txt`, `s75-plan-probe-exif-block.txt`, `s75-plan-probe-pillow.txt`, AC-146.1, AC-146.3, AC-146.19, M-6.

### D-905: What do a whole-image view and the plain image download of a tagged file return?

**I recommend A: for a tagged JPEG, MPO or PNG, both the whole-image view and the plain download (no region) return the picture turned upright, in the same format, with no tag and with its colour profile; every untagged file and every WebP still gets its own bytes back, byte for byte.** This changed after the expert pass: the plain download is what Copy of an unmarked shot and the MCP image call read, so leaving it raw left a tagged PNG pasting sideways and the MCP call getting stored pixels under headers that give the shown frame. The GUI's own display does not change, since Chromium turned the file anyway. The costs: each load of a tagged file decodes and re-encodes it (lossy for JPEG, quality 90); an MPO keeps only its first frame; the camera and GPS fields are dropped, as crop and export already drop them; and a re-encoded PNG can pass the 15 MB image cap. Your file is never written. Undoing it is one condition.

- B: turn only the scaled whole view, and keep the plain download as your file's bytes for every file. Copy of a tagged PNG stays sideways and the MCP call gets the stored frame under shown-frame headers.
- C: decode every plain download, untagged files too. Loses D-410's byte-exact answer and re-encodes every file the filmstrip loads.
- D: keep things as they are. Under D-903 A the list reports the shown frame, so a whole view of a tag 5 to 8 file answers 409, and the plain download stays the stored frame.

Refs: `adapter.py:473-497` (D-410 RETURN_UNCHANGED), `routes/captures.py:411-446` and its comment at `:424-426`, `registry.ts:410-439`, `capture-clipboard.ts:85`, `clipboard-image.ts:11`, D-410, D-411 (headers only), `cip-expert-pass.txt`, AC-146.4, AC-146.5, AC-146.17, AC-146.20 to AC-146.23, AC-146.28, M-6.

## Research References

- Local only, all read-only and written under `C:/Temp/av-kit/capture-inbox-probe/`:
  - `s75-plan-probe-electron.txt`: Electron 42.11.18 (Chrome 148.0.7778.280) turns a JPEG and PNG tagged 2 to 8 and never a WebP; the red-corner positions per tag (tag 6: shown 300x400, red at `(290, 10)`).
  - `s75-plan-probe-pillow.txt`: Pillow 13.0.0 gives `UnidentifiedImageError` for a non-image, `OSError` for a truncated PNG and `SyntaxError` for a damaged IDAT; junk EXIF reads as no tag and `exif_transpose` still succeeds; an MPO reads as format `MPO`, tag 6, 40x30, and turns to 30x40.
  - `s75-plan-probe-encode.txt`: re-encoding after `exif_transpose` drops the orientation tag for JPEG, PNG and WebP.
  - `s75-plan-probe-extra-pillow.txt` and `s75-plan-probe-extra-electron.txt`: nine tag-6 fixtures. Chromium turns the `eXIf`-before-`IDAT` PNG, the Pillow-written JPEG and PNG and the MPO (300x400), and leaves the `eXIf`-after-`IDAT` PNG, the prefixed `eXIf`, the raw-profile text PNG, the XMP-only JPEG and the Pillow WebP (VP8X flag `0x08`, `EXIF` chunk present) at 400x300. Pillow's `getexif()` reads 6 for all nine.
  - `s75-plan-probe-exif-block.txt`: what `info["exif"]` holds at open: none for the after-`IDAT`, raw-profile and XMP-only files (after-`IDAT` appears only after `load()`), a doubled `Exif\0\0` for the prefixed PNG, `Exif\0\0MM\0*` for the PNG, JPEG and MPO, and `MM\0*` for the WebP.
  - `cip-expert-pass.txt`: the §5a expert pass on D-903, D-904 and D-905.
- No web source was needed.

## Planning receipts

All under `C:/Temp/av-kit/capture-inbox-probe/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `s75-plan-eol.txt` | Line endings and sizes of every file in §Files Modified and §Project files; the four new test files absent |
| `s75-plan-probe-electron.txt`, `s75-plan-probe-pillow.txt`, `s75-plan-probe-encode.txt`, `s75-plan-probe-extra-pillow.txt`, `s75-plan-probe-extra-electron.txt`, `s75-plan-probe-exif-block.txt` | §Research References |
| `cip-expert-pass.txt` | The §5a expert pass, saved by the coordinator |
| `s75-plan-shapes-dryrun.txt` | `baseline.ps1`'s rulings, queue, row-0 copies, shapes and anchors blocks run against today's tree: rulings fails on the missing execute words (expected until the gate), the rest pass |
| `s75-plan-parse.txt` | Both `.ps1` files parse with no error |
| `s75-plan-task-lint.txt` | `lint_task_contract.py` on `task.md` |
| `s75-plan-decision-probe.txt` | `decision_sources` on this plan, the grouping and `known-issues.yaml` with the two issues: D-900 to D-910 at stage `planning`, and no stage conflict |

No suite or build ran at plan time.

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the two 09 home sections and the two issues | `s75-plan-2026-11-15-capture-inbox-probe` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from the row-0 content (`row0/` and `s75-anchors.txt`) in the §Files Modified paths, against AC-145.1 to AC-146.28 | `s75-execution-2026-11-15-capture-inbox-probe` |
