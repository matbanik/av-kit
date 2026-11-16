---
date: "2026-11-15"
project: "2026-11-15-capture-inbox-probe"
meu: "MEU-146"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-capture-inbox-probe/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "MEU-145 (2026-11-15-capture-inbox-probe-MEU-145-handoff.md)"
---

# Handoff: 2026-11-15-capture-inbox-probe-MEU-146-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-146 `capture-exif-orientation` (issue `CAPTURE-EXIF-SCANNED-ORIENTATION`, triage D-803). A JPEG, MPO or PNG with an EXIF orientation tag has one frame, the one Chromium shows: the list size, views, the plain download, marks, the bake, crop and export all use it. The inbox file is never rewritten, a WebP is never turned, and an annotated copy baked in the old frame is rebaked by the next scan without loss.
**Build Plan Section**: [09 §EXIF orientation on scan](../../../docs/build-plan/09-screenshot-capture.md#exif-orientation-on-scan) (matrix 9.44), with the Delivered (Session 75) note above `## Named deferrals`.
**Predecessor**: MEU-145 (same session; `2026-11-15-capture-inbox-probe-MEU-145-handoff.md`).

- **SHOWN_FORMATS (D-904, handed to the agent).** `SHOWN_ORIENTATION_FORMATS` is JPEG, MPO and PNG (`capture/adapter.py:84`). `shown_orientation` (`:444`) reads the tag only from the EXIF block before load, never `getexif()`, so an XMP-only JPEG, a raw-profile PNG and an `eXIf` after `IDAT` give 1, as Chromium shows them. AC-146.19 pins Chromium's behaviour in this Electron.
- **SHOWN_OPEN (D-903, handed to the agent).** `_open_shown` (`:479`) opens, loads and turns the pixels by a fixed transpose map (`_turn`, `:472`). `view` (`:584`), `crop` (`:656`), `bake` (`:704`), `render` (`:725`) and `export` (`:780`) read pixels only through it (`CROP_EXPORT_FRAME`, D-907), so marks, the bake, regions, crop and export use the shown frame. The user's file is never rewritten (M-2).
- **PROBE_SWAP.** `probe` (`:534`) swaps width and height for tags 5 to 8 from the tag alone, with no pixel transpose (AC-146.2 patches `transpose` to raise).
- **SHOWN_TAG, READ_SHOWN, VIEW_SHOWN (D-905, handed to the agent).** The port gains `shown_tag` and `read_shown` (`ports/capture.py:101`, `:105`; adapter `:556`, `:564`). `read_image(id, "original")` answers `read_shown` (`services/capture.py:1747`), so the plain download of a tagged JPEG, MPO or PNG is upright, untagged and in its own format, and a palette PNG keeps its `tRNS` alpha (F1, D-1002: `_encode_view`'s PNG branch, `adapter.py:384-389`, converts a `P` image with `transparency` to RGBA, as `view` does at `:608-611`); any other file is returned byte for byte. A whole view at scale 1 returns the file's bytes only for tag 1.
- **ICC_KEEP (D-905; region views D-1000).** A turned view keeps the file's colour profile (`:614`), and `read_shown` keeps it (`:579`), through `_encode_view` (`:369`).
- **DIMS_REFRESH (D-906).** A recorded size that changed is refreshed by the scan (`services/capture.py:691-704`), `register_shot` and `import_image` (`_import_in_place`, `:943`; `_upsert_shot`, `:2309`).
- **BAKE_MARKER (D-909).** `_write_sidecar` (`:334`) records `baked_orientation` when it is not 1; `annotate_and_save` passes `shown_tag` (`:1708-1713`).
- **STALE_BAKE and STAGED_REBAKE (D-909, D-910).** The scan rebakes an annotated copy whose recorded frame differs from the shown one (`:734-743`, `_stale_rebake`, `:790`), through `_restage_annotated` (`:815`): the bake goes to a `.rebake-new` file in the shot's folder, the live copy and sidecar are moved aside to `.rebake-prior` names and published by `os.replace`, and a failure rolls back. `_recover_restage` (`:761`) repairs a stopped restage on the next scan, returns a `RecoverResult` (`:374`) and never raises. `capture.stale_bake_failed` (`STALE_BAKE_FAILED_EVENT`, `:97`) is logged once with only `count` when the failed set changes (`:754-758`).
- **Route comment (item 4).** `routes/captures.py:425-427` now says what the no-parameter image returns; only `#` lines changed (gate `route-comment-only`; H1-4).
- **Spec text and records (rows 5 and 6).** The Delivered note in 09; the issue resolved through `issue-resolve.py`; MEU-146 `ready_for_review` (`s75-status-146.txt`).

**Where values go (D-421, `NO_RAW_CONSOLE`).** The tag and the sizes are numbers. The stale-bake failure set holds paths only in memory and logs only a count; AC-146.26's path check uses the `s75mark` folder.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-15-capture-inbox-probe/implementation-plan.md) §MEU-146. **Execution authorization:** `USER_EXPLICIT`, 2026-11-15, "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions." The plan review approved at round 3 ([plan-critical-review.md](2026-11-15-capture-inbox-probe-plan-critical-review.md)); `plan_to_exec_gate: human`. The coordinator wrote these words into the plan's Status line (line 15) before row 0; that is a plan-text edit made after the plan was approved, disclosed here.

**Receipts.** A receipt named by its file name alone is in the session's receipts folder (`RECEIPTS_DIR`, the plan's `capture-inbox-probe` folder under it). Full paths appear only in the evidence records' `command` fields.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-146.1 | unit | `shown_orientation`: JPEG, MPO and PNG tagged 2 to 8 give that tag, and so does the builder's Pillow-written `o6.png` (6); tag 1 or no tag give 1; WebP tagged 2 to 8 gives 1; the builder's XMP-only JPEG, raw-profile PNG, `eXIf`-after-`IDAT` PNG (freshly opened) and prefixed-`eXIf` PNG give 1, though `getexif()` reads 6 for each; junk EXIF, 0 and 9 give 1, with no raise. | Local Canon (`SHOWN_FORMATS`; `s75-plan-probe-extra-electron.txt`; D-904, handed to the agent) | `tests/unit/test_capture_orientation.py:164` | ✅ |
| AC-146.2 | unit | `probe` on the 400x300 JPEG and PNG tagged 1 to 8: tags 1 to 4 give `(400, 300)`, tags 5 to 8 give `(300, 400)`; with `Image.Image.transpose` patched to raise, `probe` of the tag-6 JPEG still gives `(300, 400)` (`PROBE_SWAP`). | Local Canon (09 Tests; D-903, handed to the agent) | `tests/unit/test_capture_orientation.py:206` | ✅ |
| AC-146.3 | unit | `probe` on the WebP tagged 1 to 8 gives `(400, 300)`; the MPO tagged 6 gives `(30, 40)`; the junk-EXIF JPEG gives its stored size; the builder's XMP-only, raw-profile and `eXIf`-after-`IDAT` files give `(40, 30)`. | Local Canon (D-904, handed to the agent) | `tests/unit/test_capture_orientation.py:236` | ✅ |
| AC-146.4 | unit | A whole view at scale 1 of the JPEG and PNG tagged 2 to 8 has the shown size, red (r > 200, g < 60, b < 60) at the Electron probe's position for that tag, no orientation tag, and the file's own format. | Local Canon (`VIEW_SHOWN`; `s75-plan-probe-electron.txt`; D-905, handed to the agent) | `tests/unit/test_capture_orientation.py:260` | ✅ |
| AC-146.5 | unit | Guard: a whole view of an untagged file, a tag-1 file and a tagged WebP returns the file's bytes. | Local Canon (D-410 RETURN_UNCHANGED; D-905) | `tests/unit/test_capture_orientation.py:285` | ✅ |
| AC-146.6 | unit | A region `(260, 0, 40, 40)` of the tag-6 JPEG and PNG, with source size `(300, 400)`, is 160x160 (the D-409 4x upscale of the 40x40 region) with a red centre. | Local Canon (09 Tests: a region in the shown frame; D-903) | `tests/unit/test_capture_orientation.py:300` | ✅ |
| AC-146.7 | unit | A view of the tag-6 file given with the stored source size `(400, 300)` raises `ConflictError`. | Local Canon (D-903; MEU-129 size check) | `tests/unit/test_capture_orientation.py:318` | ✅ |
| AC-146.8 | unit | `crop` of the tag-6 JPEG, box `(260, 0, 40, 40)`, source size `(300, 400)`, writes a 40x40 PNG with a red centre and no EXIF. | Local Canon (`CROP_EXPORT_FRAME`; D-907) | `tests/unit/test_capture_orientation.py:333` | ✅ |
| AC-146.9 | unit | `bake` of the tag-6 JPEG with a `RedactAnnotation` `#00FF00` at shown `(100, 330, 40, 40)` writes a 300x400 PNG with green at `(120, 350)`. | Local Canon (09 Tests: a mark bakes in the same place; D-903) | `tests/unit/test_capture_orientation.py:353` | ✅ |
| AC-146.10 | unit | `render` with the same mark returns the same pixels as AC-146.9's bake. | Local Canon (D-903) | `tests/unit/test_capture_orientation.py:371` | ✅ |
| AC-146.11 | unit | The flipped AC-136.7 (`test_ac_136_7_exif_orientation_is_applied`) passes for PNG, JPEG and WebP output (Green only). | Local Canon (`CROP_EXPORT_FRAME`; D-907 over D-613) | `tests/unit/test_capture_export_adapter.py:672` (`test_ac_136_7_exif_orientation_is_applied`) | ✅ |
| AC-146.12 | unit | A row recorded as 400x300 for a file whose probe now gives 300x400 with the same file size is updated to 300x400 by the next scan. | Local Canon (`DIMS_REFRESH`; D-906) | `tests/unit/test_capture_orientation.py:403` | ✅ |
| AC-146.13 | unit | The same through `register_shot`. | Local Canon (D-906) | `tests/unit/test_capture_orientation.py:419` | ✅ |
| AC-146.14 | unit | The same through `import_image` of a file already in the inbox. | Local Canon (D-906) | `tests/unit/test_capture_orientation.py:439` | ✅ |
| AC-146.15 | e2e | API: `GET /captures` over the JPEG and PNG tagged 1 to 8 and the WebP tagged 6 lists 400x300 for tags 1 to 4 and the WebP, and 300x400 for tags 5 to 8. | Local Canon (09 One frame; D-903, D-904) | `tests/e2e/test_api_capture_orientation.py:108` | ✅ |
| AC-146.16 | e2e | API: `GET /captures/{id}/image?x=260&y=0&width=40&height=40` on the tag-6 JPEG answers 200 with a 160x160 image (the D-409 4x upscale of the 40x40 region), a red centre and `X-Capture-Source: 300,400`. | Local Canon (09 Tests; D-903) | `tests/e2e/test_api_capture_orientation.py:127` | ✅ |
| AC-146.17 | e2e | The no-parameter `GET /captures/{id}/image` on the tag-6 JPEG answers 200 with an upright 300x400 JPEG, red at `(290, 10)`, no `0x0112`, and `X-Capture-Source: 300,400`. | Local Canon (`READ_SHOWN`; D-905, handed to the agent) | `tests/e2e/test_api_capture_orientation.py:147` | ✅ |
| AC-146.18 | e2e | API flatten of the tag-6 PNG with one mark: the file becomes an upright 300x400 PNG with no orientation tag, the shot keeps its id, and the backup equals the tagged bytes. | Local Canon (D-903; flatten through `bake`) | `tests/e2e/test_api_capture_orientation.py:164` | ✅ |
| AC-146.19 | e2e | Electron: the builder reports `getexif()` tag 6 for all eight fixtures and, for the WebP, `VP8X` flag `0x08` with an `EXIF` chunk; in the app's renderer `o6.jpg`, `o6.png` and `o6.mpo.jpg` load at `naturalWidth` 30 and `naturalHeight` 40, and `o6.webp`, `o6-after-idat.png`, `o6-prefixed.png`, `o6-raw-profile.png` and `o6-xmp.jpg` at 40 and 30. A guard. | Research-backed (`s75-plan-probe-electron.txt`, `s75-plan-probe-extra-electron.txt`; `WEBP_PIN`; D-904, handed to the agent) | `ui/tests/e2e/capture-inbox.test.ts:3696` (gate `ui-electron`) | ✅ |
| AC-146.20 | unit | `read_shown` on the tag-6 JPEG, PNG and MPO returns bytes in the format the suffix names (`_encode_view`; JPEG for the `.jpg` MPO), 300x400 (MPO 30x40), red at the shown corner, no `0x0112` in the result. | Local Canon (`READ_SHOWN`; D-905, handed to the agent) | `tests/unit/test_capture_orientation.py:458`, `:478` (F1 palette alpha, D-1002) | ✅ |
| AC-146.21 | unit | Guard: `read_shown` returns the file's bytes unchanged for an untagged PNG, a tag-1 JPEG, the tag-6 WebP, the builder's XMP-only, raw-profile and `eXIf`-after-`IDAT` files, a tag-6 JPEG cut to half its length (its header still reads as tag 6), and a non-image file. | Local Canon (D-410 RETURN_UNCHANGED; D-905) | `tests/unit/test_capture_orientation.py:478` | ✅ |
| AC-146.22 | unit | A tag-6 JPEG and PNG carrying an sRGB ICC profile: the whole view at scale 1 and `read_shown` are each 300x400 and carry the same `icc_profile` bytes. | Local Canon (`ICC_KEEP`; crop and export keep it, `adapter.py:579`, `:593-594`; D-905) | `tests/unit/test_capture_orientation.py:508` | ✅ |
| AC-146.23 | unit | The service's `read_image(id, "original")` returns the port's `read_shown` sentinel; `read_image(id, "annotated")` returns the annotated file's bytes. | Local Canon (`READ_SHOWN`; D-905) | `tests/unit/test_capture_orientation.py:673` | ✅ |
| AC-146.24 | unit | `annotate_and_save` with a port whose `shown_tag` is 6 writes a sidecar with `"baked_orientation": 6`; with `shown_tag` 1 the sidecar keys are exactly `version` and `annotations`. | Local Canon (`BAKE_MARKER`; D-909) | `tests/unit/test_capture_orientation.py:690` | ✅ |
| AC-146.25 | unit | A scan rebakes the annotated copy once, calls `bake` once with the saved marks, an output path in the shot's folder other than the live copy, and the copy's own format, and rewrites the key, for: no key with `shown_tag` 6; no key with `shown_tag` 3; key 6 with `shown_tag` 1 (the key is removed). After it the copy holds the new bake at the same path, the sidecar's `annotations` list equals the saved one, the row's `annotated_path` and `sidecar_path` are unchanged, and no `.rebake-` file is in the folder. A second scan makes no `bake` call. A shot whose key matches makes none. | Local Canon (`STALE_BAKE`, `STAGED_REBAKE`; 09 One frame; D-909, D-910) | `tests/unit/test_capture_orientation.py:712` | ✅ |
| AC-146.26 | unit | When that rebake fails, the list still answers and nothing the user had is lost. Cases: (a) `bake` writes `b"part"` to its output and raises; (b) `os.replace` raises while the copy is published (call 2) and (c) while the sidecar is published (call 4); (d) `capture.annotated_format` is `jpeg` while the copy is `.annotated.png`, with `bake` raising; (e) an interrupted rebake: the live copy is missing and its `.rebake-prior` holds the old copy. In (a) to (d) the original, copy and sidecar bytes and the row's paths equal those recorded before the scan; in (e) the copy is restored to its prior bytes and the row keeps its path. In (a) to (e) no `.rebake-` file is left, and one `capture.stale_bake_failed` warning has keys exactly `event`, `log_level`, `module` and `count`, `count` 1, no path or marker ((e) logs one once its rebake is made to raise); a second failing scan logs nothing. Then, with a working port and `os.replace`, the next scan rebakes once and the scan after it makes no `bake` call; in (d) the copy is still `.annotated.png`, the format the adapter is given is `png`, and no `.annotated.jpg` exists. Two recovery cases (review R2-F1), each with a second shot whose stale copy the same scans must rebake: (f) a read-only `.rebake-prior` beside a published copy and sidecar whose key matches, once with a real read-only attribute (`os.chmod(prior, stat.S_IREAD)`, WinError 5 on Windows) and once with `os.unlink` patched to raise `PermissionError` for that prior only, so the path runs on every platform: the list answers with both shots, the row keeps both links, the copy and the sidecar's marks are unchanged, no `bake` call is made for it, one warning with `count` 1 is logged and a second scan logs nothing; once the attribute is cleared or the patch removed, the next scan discards the prior and makes no `bake` call; (g) a live copy missing with its `.rebake-prior` locked, faked by an `os.replace` patched to raise `PermissionError` for that prior only, as the test's docstring says: the list answers with both shots, the row still has both links, the prior and the sidecar's marks are unchanged, no `bake` call is made for it, one warning with `count` 1 is logged and a second locked scan logs nothing; once unlocked, the next scan restores the copy and rebakes it exactly once, and the scan after makes no `bake` call. In both, the other shot is rebaked on the first scan, the warning's keys are exactly `event`, `log_level`, `module` and `count` with no path or marker, and the only `.rebake-` file left while locked is that prior. | Local Canon (`STALE_BAKE`, `STAGED_REBAKE`; D-902 log rule; D-909, D-910; reviews R1-F1 and R2-F1) | `tests/unit/test_capture_orientation.py:898` | ✅ |
| AC-146.27 | e2e | API: a tag-6 JPEG is annotated through the API with one `#00FF00` redact mark, then put in the state today's code leaves (the copy overwritten with a 400x300 bake of the stored frame, the sidecar rewritten with the same marks and no key). After `GET /captures` the copy is 300x400 with green at the mark's shown centre, the sidecar has `"baked_orientation": 6`, and a whole-frame export answers 200 with a 300x400 image. | Local Canon (`STALE_BAKE`; expert finding 2; D-909) | `tests/e2e/test_api_capture_orientation.py:189` | ✅ |
| AC-146.28 | e2e | Guard: the no-parameter `GET /captures/{id}/image` returns the file's bytes byte for byte for an untagged PNG, a tag-1 JPEG and the tag-6 WebP. | Local Canon (D-410 RETURN_UNCHANGED; route comment `routes/captures.py:424-426`; D-905) | `tests/e2e/test_api_capture_orientation.py:228` | ✅ |
| AC-136.7 (cross-ref) | pin that moves | Renamed `test_ac_136_7_exif_orientation_is_applied` and flipped: export applies the tag (D-907 over D-613); it is AC-146.11 | MEU-136 | `tests/unit/test_capture_export_adapter.py:672` | ✅ |
| AC-128 (cross-ref) | guard | D-409 VIEW_SCALE and AC-128.5 set the region scale that D-1001 cites; D-410 RETURN_UNCHANGED still holds for tag 1, untagged files and every WebP (AC-146.5, AC-146.28) | MEU-128 | `tests/unit/test_capture_orientation.py:285`; `tests/e2e/test_api_capture_orientation.py:228` | ✅ |
| AC-129 (cross-ref) | guard | The size check refuses a frame at the stored size (AC-146.7); D-417's import path (`inspect_import`, `write_upright_png`) is unchanged and AC-129.5 still passes | MEU-129 | `tests/e2e/test_api_capture_region_import.py:384`; gate `py-tests` | ✅ |
| AC-36.9, AC-36.10 (cross-ref) | guard | The fakes gain `shown_tag` (1) and `read_shown` (the file's bytes), so the exact sidecar keys and `b"orig-bytes"` from `read_image` hold | MEU-36 | `tests/unit/test_capture_service.py:356`, `:389` | ✅ |
| AC-104.3 (cross-ref) | guard | The bare-error adapter test is unchanged and passes | MEU-104 | `tests/unit/test_capture_adapter.py:465-470` | ✅ |
| AC-130.21 (cross-ref) | pin that moves | Owned by MEU-145 (AC-145.15); crop now reads through `_open_shown`, and its damaged-source 422 still holds | MEU-130 | `tests/e2e/test_api_capture_crop.py:763` | ✅ |
| AC-145 (sibling) | sibling MEU | AC-145.1, AC-145.2, AC-145.3, AC-145.4, AC-145.5, AC-145.6, AC-145.7, AC-145.8, AC-145.9, AC-145.10, AC-145.11, AC-145.12, AC-145.13, AC-145.14, AC-145.15: the scan skip, evidenced in the MEU-145 handoff | MEU-145 | `2026-11-15-capture-inbox-probe-MEU-145-handoff.md` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-146.1 | `cases that did not give their shown tag` | Row 4: pass | `test_capture_orientation.py:164` |
| AC-146.2, AC-146.3 | `probe sizes off the shown frame`; `probe sizes: {'mpo 6': (40, 30)}` | Row 4: pass | `test_capture_orientation.py:206`, `:236` |
| AC-146.4 | `whole views not upright` | Row 4: pass | `test_capture_orientation.py:260` |
| AC-146.6, AC-146.22 | `jpg: the region raised ConflictError`; `jpg view: raised ConflictError` | Row 4: pass | `test_capture_orientation.py:300`, `:508` |
| AC-146.7 | `jpg: no conflict for the stored size` | Row 4: pass | `test_capture_orientation.py:318` |
| AC-146.8 | `the crop raised ConflictError` | Row 4: pass | `test_capture_orientation.py:333` |
| AC-146.9, AC-146.10 | `the bake is (400, 300)`; `the render is (400, 300)` | Row 4: pass | `test_capture_orientation.py:353`, `:371` |
| AC-146.12, AC-146.13, AC-146.14 | `the scan kept the old size`; `register returned the old size`; `import returned the old size` | Row 4: pass | `test_capture_orientation.py:403`, `:419`, `:439` |
| AC-146.15 | `{'t6.png': (400, 300)} != {'t6.png': (300, 400)}` | Row 4: pass | `test_api_capture_orientation.py:108` |
| AC-146.16 | `assert (160, 160) == (40, 40)` at Red, under the plan's old 40x40 text; under D-1001's corrected assert the row-0 code fails at `the region centre is not red` (`s75-red-146-16-corrected.txt`) | Row 4: pass | `test_api_capture_orientation.py:127` |
| AC-146.17 | `('JPEG', (400, 300)) == ('JPEG', (300, 400))` | Row 4: pass | `test_api_capture_orientation.py:147` |
| AC-146.18 | `the flattened file is ('PNG', (400, 300))` | Row 4: pass | `test_api_capture_orientation.py:164` |
| AC-146.20 | `jpg: ('JPEG', (400, 300))` | Row 4: pass | `test_capture_orientation.py:458` |
| AC-146.23 | `the original was not read through read_shown` | Row 4: pass | `test_capture_orientation.py:673` |
| AC-146.24 | `the tag-6 sidecar has no key` | Row 4: pass | `test_capture_orientation.py:690` |
| AC-146.25 | `no key, tag 6: 0 bake calls` | Row 4: pass | `test_capture_orientation.py:712` |
| AC-146.26 | `(a) first failing scan: 0 stale-bake warnings` | Row 4: pass | `test_capture_orientation.py:898` |
| AC-146.27 | `the copy is still (400, 300)` | Row 4: pass | `test_api_capture_orientation.py:189` |
| AC-146.20 (F1, D-1002) | `read_shown: the palette alpha was not kept: {(1, 0): 255, (1, 3): 255, (0, 0): 255}` (`s75-f1-red.txt`; the `view` case passed first) | F1 Green: pass (`s75-f1-green-one.txt`) | `test_capture_orientation.py:478` |

- **Guards, passing at Red by design:** AC-146.5, AC-146.21 and AC-146.28 (each runs beside a tagged case in the same file whose bytes do change: AC-146.4, AC-146.20, AC-146.17), and AC-146.19 (`s75-red-e2e.txt`: `1 passed (1.9s)`), which pins what Chromium already does.
- **Green only:** AC-146.11 (the flipped AC-136.7; before Green `source_size=(300, 400)` raises `ConflictError`).
- **Row 2 Red** (`s75-red-py.txt`): `36 failed, 3 passed in 19.97s` across both MEUs; MEU-146's 23 cases failed by assertion. `s75-red-check.txt`: `red-check: 1 receipt(s), 36 required test(s), 0 problem(s)`.
- **The S12 stop (D-1001).** At row 4 the first Green run read `2 failed, 78 passed, 5 warnings in 5.00s` (`scratch-green146.txt`): AC-146.6 and AC-146.16 asserted 40x40 and the code returned 160x160. The executor stopped and the coordinator ruled. After the correction, `s75-146-green.txt` reads `80 passed, 5 warnings in 5.18s` and `s75-146-sweep.txt` reads `1016 passed, 1923 deselected, 21 warnings`.
- **The Red record for AC-146.16, corrected.** The coordinator's ruling said the Red run failed on 409 before the size check. That holds for AC-146.6 (unit: `jpg: the region raised ConflictError`). AC-146.16 (API) answered 200 at Red and failed on the size, `assert (160, 160) == (40, 40)`, so the wrong expectation was visible at Red and that Red reason no longer holds under the corrected assert. A supplementary run of the corrected test against the row-0 product code (`s75-red-146-16-corrected.txt`) fails at the next assert, `the region centre is not red` (`getpixel((20, 20))` is `(20, 21, 200)`, the stored frame's blue corner), so the test still discriminates. A first attempt at that run was invalid, because pytest's `pythonpath` setting put the live packages ahead of the row-0 overlay and the test passed on the live code; the recorded run overrides that setting and prints the module paths pytest imported.
- **AC-146.26 (f).** The `chmod` variant (a read-only `.rebake-` file) runs only on win32; the patch variant runs everywhere (`test_capture_orientation.py:904`).
- **AC-146.27's status code.** The plan text says the export "answers 200"; the export route answers 201 Created, and the test asserts 201 (`test_api_capture_orientation.py:219-220`).

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-capture-inbox-probe/baseline.ps1 *> C:/Temp/av-kit/capture-inbox-probe/s75-baseline.txt (task.md row 0's Validation cell)", "scope": "Row 0: the rulings (S9) and queue (S8) checks, the shapes check (S7), the row-0 copies and their SHA-256 and line endings (s75-anchors.txt), baseline.sha and baseline-dirty.txt, the base Python, UI, MCP and Electron runs, ruff, the UI build and the red-check, identity and id-length selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 (baseline.sha), before row 1", "output": "s75-baseline.txt: execute words found; MEU-35, MEU-36, MEU-84, MEU-128, MEU-129, MEU-130 and MEU-136 approved, MEU-145 and MEU-146 pending; 6aaf9b0 is an ancestor of HEAD: True; shapes wrong (S7): []; the row-0 copies differ from HEAD: []; baseline-dirty.txt 61 paths; base py 2900 passed, 37 warnings in 250.26s; base ui Test Files 130 passed (130), Tests 1532 passed (1532); base mcp Tests 535 passed (535) in 36 files; base e2e 53 passed (1.5m); ruff All checks passed!; the base UI and MCP builds exit 0; red-check selftest 71 fixture(s) (21 positive, 50 negative), 0 wrong; identity selftest 0 failure(s); id-length selftest 4 case(s), 0 wrong; baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-1-stubs", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-1.ps1 (task.md row 1's Validation cell, extracted to a .ps1 and run from P:/av-kit with ELECTRON_RUN_AS_NODE unset); receipts s75-stub-types.txt, s75-stub-lint.txt, s75-stub-sweep.txt, s75-stub-check.txt, s75-stub-fixtures.txt", "scope": "Row 1 type-only names: SHOWN_ORIENTATION_FORMATS, shown_orientation and _open_shown stubs, the port's shown_tag and read_shown, FakeCapturePort and FakeAnnotate shown_tag and read_shown, the STALE_BAKE_FAILED_EVENT and scan-state names, and tests/orientation_fixtures.py, with no behaviour", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 and 1", "output": "s75-stub-types.txt: 0 errors, 0 warnings, 0 informations; s75-stub-lint.txt: All checks passed!; s75-stub-sweep.txt: 222 passed, 5 warnings in 17.70s; s75-stub-check.txt: stubs present: True line-ending drift: []; s75-stub-fixtures.txt: eight fixtures, each 40x30 with getexif_tag 6; exif_block_tag 6 for o6.jpg, o6.mpo.jpg, o6.png, o6-prefixed.png and o6.webp (EXIF chunk, vp8x_flags 8), and null for o6-xmp.jpg, o6-raw-profile.png and o6-after-idat.png"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-2-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-2.ps1 (task.md row 2's Validation cell, extracted to a .ps1 and run from P:/av-kit with ELECTRON_RUN_AS_NODE unset); receipts s75-red-idlen.txt, s75-red-py.txt, s75-red-check.txt (red-check.py with the 36 --require ids) and s75-red-e2e.txt (AC-146.19 through pwsh in P:/av-kit/ui)", "scope": "Red for both MEUs: AC-145.1 to AC-145.13 and AC-146.1 to AC-146.28 (less AC-146.11 and AC-146.19) against the row-1 stubs, with Pillow images under tmp_path and no network; the Electron pin AC-146.19", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 to 2", "output": "s75-red-idlen.txt: id-length: 39 test(s), 0 too long. s75-red-py.txt: 36 failed, 3 passed in 19.97s; the 3 passing are the guards AC-146.5, AC-146.21 and AC-146.28. Decisive: message is not the fixed one; damaged: raised SyntaxError; the scan raised InboxPathError; the scan raised OSError; list answered 500; list answered 422; probe sizes off the shown frame; whole views not upright; jpg: the region raised ConflictError; the bake is (400, 300); the scan kept the old size; assert (160, 160) == (40, 40); the original was not read through read_shown; the tag-6 sidecar has no key; no key, tag 6: 0 bake calls; the copy is still (400, 300). s75-red-check.txt: red-check: 1 receipt(s), 36 required test(s), 0 problem(s). s75-red-e2e.txt: AC-146.19 1 passed (1.9s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-4-green-146", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-4.ps1 (task.md row 4's Validation cell, extracted to a .ps1 and run from P:/av-kit with ELECTRON_RUN_AS_NODE unset); receipts s75-146-green.txt, s75-146-sweep.txt, s75-146-types.txt, s75-146-eol.txt", "scope": "MEU-146 Green: SHOWN_FORMATS, SHOWN_OPEN, PROBE_SWAP, SHOWN_TAG, READ_SHOWN, VIEW_SHOWN, ICC_KEEP, BAKE_MARKER, STALE_BAKE, STAGED_REBAKE, DIMS_REFRESH, CROP_EXPORT_FRAME and the AC-136.7 flip (AC-146.11), after the D-1001 assert correction", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 to 4", "output": "s75-146-green.txt: 80 passed, 5 warnings in 5.18s (test_capture_orientation.py, test_api_capture_orientation.py, test_capture_export_adapter.py); s75-146-sweep.txt: 1016 passed, 1923 deselected, 21 warnings in 89.38s (tests/ -k capture); s75-146-types.txt: 0 errors, 0 warnings, 0 informations; s75-146-eol.txt: line-ending drift: []. Before D-1001 the same run read 2 failed, 78 passed, 5 warnings in 5.00s (scratch-green146.txt): AC-146.6 and AC-146.16 failed on assert (160, 160) == (40, 40)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-red-146-16-corrected", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-red16.ps1 > C:/Temp/av-kit/capture-inbox-probe/s75-red-146-16-corrected.txt 2>&1 (copies packages/*/src to C:/Temp/av-kit/capture-inbox-probe/tmp/s75red16, overwrites the five row-0 product files from C:/Temp/av-kit/capture-inbox-probe/row0, sets PYTHONPATH to it, then uv run pytest -o pythonpath=. -p s75_where tests/e2e/test_api_capture_orientation.py -k test_ac_146_16)", "scope": "Supplementary Red for AC-146.16 after D-1001: the corrected test run against the row-0 product code (adapter, services, ports, domain and routes), so its Red reason under the 160x160 assert is on record", "phase": "red", "exit_code": 1, "result": "fail", "tested_state": "row-0 product code (s75-anchors.txt hashes) with the current test files", "output": "pytest modules from the row-0 overlay; pytest Red tree (no read_shown on the adapter): True. FAILED test_ac_146_16_region_view_is_cut_from_the_shown_frame[AC-146.16]: AssertionError: the region centre is not red; getpixel((20, 20)) is (20, 21, 200); 1 failed, 5 deselected in 2.39s. The size assert passed, so the region came back 160x160 from the stored frame's blue corner."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-f1-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-f1-red.ps1 (id-length.py on test_capture_orientation.py, then uv run pytest tests/unit/test_capture_orientation.py -k test_ac_146_20_read_shown_keeps_palette_alpha, then red-check.py --require test_ac_146_20_read_shown_keeps_palette_alpha); receipts s75-f1-idlen.txt, s75-f1-red.txt, s75-f1-red-check.txt", "scope": "F1 (D-1002) Red: a 4x2 tag-6 palette PNG with tRNS alpha 0, 128 and 255; view and read_shown must each keep alpha 0 and 128 at the turned positions, before the _encode_view fix", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "the round-1 tree plus the new AC-146.20 case, before the fix", "output": "s75-f1-idlen.txt: id-length: 21 test(s), 0 too long. s75-f1-red.txt: AssertionError: read_shown: the palette alpha was not kept: {(1, 0): 255, (1, 3): 255, (0, 0): 255}; 1 failed, 20 deselected in 10.82s (the view case passed before it). s75-f1-red-check.txt: red-check: 1 receipt(s), 1 required test(s), 0 problem(s). The row exits 0 because red-check confirms the decisive failure."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-f1-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-f1-green.ps1 (the new case, then row 4's Validation cell with s75-f1-* receipts, then ruff check on adapter.py and test_capture_orientation.py); receipts s75-f1-green-one.txt, s75-f1-green.txt, s75-f1-sweep.txt, s75-f1-types.txt, s75-f1-eol.txt, s75-f1-lint.txt", "scope": "F1 (D-1002) Green: _encode_view's PNG branch converts a P image with transparency to RGBA, as view does; the MEU-146 set, the capture sweep, pyright, line endings and ruff", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "the round-1 tree plus the F1 case and fix", "output": "s75-f1-green-one.txt: 1 passed, 20 deselected in 0.19s; s75-f1-green.txt: 81 passed, 5 warnings in 4.65s; s75-f1-sweep.txt: 1017 passed, 1923 deselected, 21 warnings in 81.60s; s75-f1-types.txt: 0 errors, 0 warnings, 0 informations; s75-f1-eol.txt: line-ending drift: []; s75-f1-lint.txt: All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-5-notes", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-5.ps1 (task.md row 5's Validation cell, extracted to a .ps1 and run from P:/av-kit with ELECTRON_RUN_AS_NODE unset); receipt s75-notes-check.txt", "scope": "Row 5: one Delivered (Session 75) note under each of the two 09 anchors, CRLF kept, insert-only against row 0", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 to 5", "output": "s75-notes-check.txt: CRLF: True notes: 1 1 opcodes against row 0: ['equal', 'insert']"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-6-records", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-6.ps1 (task.md row 6's Validation cell, extracted to a .ps1 and run from P:/av-kit with ELECTRON_RUN_AS_NODE unset); receipts s75-issue-resolve.txt, s75-issues-render.txt, s75-issues-render-check.txt, s75-status-145.txt, s75-status-146.txt, s75-status-render.txt, s75-row6-check.txt", "scope": "Row 6: both issues resolved through issue-resolve.py, known-issues.md rendered, MEU-145 and MEU-146 ready_for_review, the status render, and grouping row 75 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 to 6", "output": "s75-issue-resolve.txt: decision logs read: 95 of 95; parsed fields changed: 10 (issues[123] and issues[125]); issue-resolve: 0 problem(s). s75-issues-render.txt: Rendered known-issues.md: 64 lines; s75-issues-render-check.txt: OK: known-issues.md is up-to-date. s75-status-145.txt and s75-status-146.txt: Updated MEU-145 / MEU-146 → ready_for_review (updated: 2026-11-15). s75-status-render.txt: Loaded 153 MEUs across 12 phases; All regions rendered successfully. s75-row6-check.txt: other MEU rows changed: []; grouping LF: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-h1-1-rows", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-H1-1.ps1 (task.md row H1-1's Validation cell) ; receipt task-unchecked.txt", "scope": "H1-1: every implementation row of task.md is checked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 to 6", "output": "task-unchecked.txt: unchecked implementation rows: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-capture-inbox-probe/session-gate.ps1 *> C:/Temp/av-kit/capture-inbox-probe/s75-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/capture-inbox-probe/s75-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "scope": "H1-2, re-run after the F1 correction (D-1002): the registered D6 gate on the whole tree: identity, every static check, the full Python, UI and MCP suites, the UI build, OpenAPI, the MCP types, build and tests, both renders and the Electron capture-inbox spec, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8", "output": "identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); mcp-types exit=0; task-contract exit=0 (24 rows, 22 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (changed paths since 3397e78d7342: 86, outside scope (S3): [], head moved since row 0: False, baseline-dirty paths changed since row 0: []); route-comment-only exit=0 (route lines changed against row 0: 5, non-comment lines among them: []); red-check-selftest exit=0 (71 fixtures, 21 positive, 50 negative, 0 wrong); id-length exit=0 (40 tests, 0 too long); py-tests exit=0 (2940 passed, 37 warnings in 278.97s); openapi exit=0; ui-tests exit=0 (Test Files 130 passed (130), Tests 1532 passed (1532)); ui-build exit=0 (built in 5.53s); mcp-build exit=0; mcp-tests exit=0 (Test Files 36 passed (36), Tests 535 passed (535)); state-render exit=0 (153 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); ui-electron exit=0 (capture-inbox.test.ts, 54 passed (1.6m)); identity-after exit=0 (tested_state before = after); mcp-audit and build-record skipped with reasons; baseline failures excused: py [], ui [], mcp [], e2e []; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-h1-3-ssot", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-H1-3.ps1 (task.md row H1-3's Validation cell); receipts s75-render-check.txt, s75-h13-status-145.txt, s75-h13-status-146.txt, s75-h13-check.txt", "scope": "H1-3: MEU-145 and MEU-146 are ready_for_review and the status render matches, after the current-focus update (not a gated input)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8", "output": "s75-render-check.txt: Drift check passed, SSOT loaded (153 MEUs, 12 phases), rendered regions match on-disk content; s75-h13-check.txt: MEU-145 and MEU-146 ready_for_review: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-h1-4-shape", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-H1-4.ps1 (task.md row H1-4's Validation cell); receipts s75-openapi-check.txt, s75-api-hash-check.txt", "scope": "H1-4 (S6): the app matches openapi.committed.json; the OpenAPI document, capture.ts, registry.ts and capture.test.ts keep their row-0 SHA-256; routes/captures.py differs from row 0 only in blank or comment lines", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8", "output": "export_openapi --check exit 0, no output; s75-api-hash-check.txt: API and MCP files changed since row 0: [] route code lines changed: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-eol-final", "command": "uv run python C:/Temp/av-kit/capture-inbox-probe/eol-final.py > C:/Temp/av-kit/capture-inbox-probe/s75-eol-final.txt 2>&1", "scope": "Supplementary: the line endings of the 30 files measured at row 0, the five new test files, the plan and task.md, measured in bytes after H1-4", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8", "output": "s75-eol-final.txt: files checked: 37 line-ending drift: []"}
```

### Quality Gate Results

`s75-gate-h1-2` (H1-2) is the fresh full record for both MEUs. It is the gate re-run after the F1 correction (D-1002); round 1's gate (`3397e78…+7597a302…`, also `session-gate: all steps exit 0`) is kept in the receipts folder's `gate-round1` folder. Its last line is:

> session-gate: all steps exit 0

- **Identity:** the tested_state was the same before and after the gate (`s75-D6-identity-before.txt`, `s75-D6-identity-after.txt`): `3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8`. It is derived with `ELECTRON_RUN_AS_NODE` unset, as H1-6b's cell does. The plan's `*.md` files, this session's handoffs, the reflections, `metrics.md` and `current-focus.md` are artifacts the identity leaves out, so H1-3's current-focus edit and these handoffs do not change it.
- **Static:** pyright 0 errors; ruff passed; the UI typecheck and ESLint (`--max-warnings 0`) passed; the MCP typecheck passed; lint_task_contract passed on 24 rows (22 fully checked, 2 `view_file` exempt); scope-paths found 86 changed paths since `3397e78d7342`, none outside scope, HEAD did not move and no baseline-dirty path changed since row 0 (S3); route-comment-only found 5 changed route lines, none of them code; the red-check selftest read 71 fixtures with 0 wrong; id-length read 40 tests, none too long.
- **Suites:** pytest 2940 passed (`s75-D6-py-tests.txt`; the baseline's 2900 in `s75-baseline.txt` plus the 39 new cases that `s75-red-py.txt` ran at Red and F1's palette-alpha case, `s75-f1-red.txt`); Vitest Test Files 130 passed (130), Tests 1532 passed (1532), the baseline's counts, since no Vitest file changed; MCP Test Files 36 passed (36), Tests 535 passed (535), the baseline's counts, with the AC-145.14 `list` pin among them.
- **Build and state:** the UI build, the OpenAPI check and the MCP build exited 0; the state render (153 MEUs) and the issue render match the files on disk.
- **Runtime:** the Electron spec `ui/tests/e2e/capture-inbox.test.ts` passed 54 (`s75-D6-ui-electron.txt`; the baseline's 53 plus AC-146.19).
- **Skipped:** `mcp-audit` (live network, YouTube and the installed avkit servers, which the brief forbids) and `build-record` (no release and no package build in this session).
- **Baseline failures excused:** py [], ui [], mcp [], e2e []. Each gate run passed at its first attempt; the re-run is for F1's new tested_state, not a flake.
- **After the gate (both re-run after F1):** H1-3 (`s75-h13-check.txt`: `MEU-145 and MEU-146 ready_for_review: True`), H1-4 (`s75-api-hash-check.txt`: `API and MCP files changed since row 0: [] route code lines changed: []`) and the supplementary line-ending check (`s75-eol-final.txt`: `files checked: 37 line-ending drift: []`).

---

## Changed Files

Against `3397e78`, outside this plan folder and the handoffs, `git diff --numstat` reads 17 tracked files, 516 insertions and 105 deletions (it counts H1-3's `current-focus.md` paragraph too), plus five new test files.

| File | Line endings | Change |
|------|--------------|--------|
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | CRLF, kept | +152 −48: `PROBE_FIXED`, `SHOWN_FORMATS`, `SHOWN_OPEN`, `PROBE_SWAP`, `SHOWN_TAG`, `READ_SHOWN`, `VIEW_SHOWN`, `ICC_KEEP`, `CROP_EXPORT_FRAME`, and F1's palette alpha in `_encode_view` (D-1002) |
| `packages/core/src/avkit_core/services/capture.py` | CRLF, kept | +223 −16: `SCAN_SKIP`, `KEEP_ROW`, `SKIP_LOG`, `DIMS_REFRESH`, `READ_SHOWN`, `BAKE_MARKER`, `STALE_BAKE`, `STAGED_REBAKE` |
| `packages/core/src/avkit_core/ports/capture.py` | CRLF, kept | +8: `shown_tag`, `read_shown` |
| `packages/api/src/avkit_api/routes/captures.py` | CRLF, kept | +3 −2, comment lines only (`:425-427`) |
| `tests/unit/test_capture_service.py` | CRLF, kept | +8: `FakeCapturePort.shown_tag` and `read_shown` |
| `tests/unit/test_capture_export_service.py` | LF, kept | +8: `FakeAnnotate.shown_tag` and `read_shown` |
| `tests/unit/test_capture_export_adapter.py` | LF, kept | +8 −9: AC-136.7 renamed and flipped (AC-146.11) |
| `tests/e2e/test_api_capture_crop.py` | LF, kept | −4: AC-130.21's restore removed (AC-145.15) |
| `ui/tests/e2e/capture-inbox.test.ts` | LF, kept | +56 −1: AC-146.19 |
| `tests/orientation_fixtures.py` | LF, new | 202 lines: the Pillow fixture builder |
| `tests/unit/test_capture_scan_unreadable.py` | LF, new | 398 lines: AC-145.1 to AC-145.11 |
| `tests/e2e/test_api_capture_scan_unreadable.py` | LF, new | 122 lines: AC-145.12, AC-145.13 |
| `tests/unit/test_capture_orientation.py` | LF, new | 943 lines: AC-146.1 to AC-146.10, AC-146.12 to AC-146.14, AC-146.20 to AC-146.26, with F1's palette-alpha case under AC-146.20 (`:478`) |
| `tests/e2e/test_api_capture_orientation.py` | LF, new | 243 lines: AC-146.15 to AC-146.18, AC-146.27, AC-146.28 |
| `docs/build-plan/09-screenshot-capture.md` | CRLF, kept | +22: the two Delivered (Session 75) notes |
| `.agent/context/known-issues.yaml`, `known-issues.md` | LF, kept | the two issues resolved (tool) and the render |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md` | LF, kept | MEU-145 and MEU-146 `ready_for_review` (tool) and the render |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | LF, kept | row 75 executed |
| `.agent/context/current-focus.md` | CRLF, kept | +3: the Session 75 paragraph (H1-3) |
| `docs/execution/plans/2026-11-15-capture-inbox-probe/implementation-plan.md`, `task.md` | LF, kept | Status line (coordinator), lines 220 and 230 (D-1001), the row marks |

Line endings were measured in bytes against row 0's `s75-anchors.txt` at rows 1, 3, 4 and 5, at F1's Green (`s75-f1-eol.txt`) and again after H1-4 (`s75-eol-final.txt`: 37 files, no drift). No file outside the plan's §Files Modified, this plan folder and the closeout artifacts it names was edited. Nothing was staged or committed.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Finding | Fix | Status |
|---|----------|----------|---------|-----|--------|
| F1 | Medium | no | Round 1: `read_shown` turned a palette PNG with a `tRNS` chunk, and `_encode_view`'s PNG branch converted it to RGB, so the plain download made its transparent pixels opaque. | D-1002: `_encode_view` converts a palette PNG with `transparency` to RGBA (`packages/infrastructure/src/avkit_infra/capture/adapter.py:384-389`); regression `test_ac_146_20_read_shown_keeps_palette_alpha` at `tests/unit/test_capture_orientation.py:478`. | fixed |

Round 1 approved with F1 open and non-blocking. Round 2 rechecked the fix and recorded F1 `fixed`, with no new finding; its report wrote "None." under `### New Findings`, which the closeout parser reads as one open finding, so round 3 was a format-only recheck that rewrote that section as an empty table and confirmed the tested_state unchanged (`3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8`). The canonical rolling report is `.agent/context/handoffs/2026-11-15-capture-inbox-probe-implementation-critical-review.md`.

### Verdict

`approved` at round 3 of 6 (ledger loop `s75-execution-2026-11-15-capture-inbox-probe`), with 0 open blocking findings. The review grants no commit or push authorization.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| An imported WebP is turned by `write_upright_png` (D-417), while a scanned WebP is not turned | residual for triage | none | Chromium does not turn a WebP (D-904); import writes a new upright PNG |
| An annotated copy with no sidecar is not rebaked | residual for triage | none | STALE_BAKE needs the saved marks; the reconcile step already clears a path whose file is gone |
| Marks clamped by an earlier GUI save are lost (`services/capture.py:1704-1706` now; `:1500-1502` when the plan was written) | residual for triage | none | The cut part was never stored, so nothing can restore it |
| An untagged region view drops the colour profile (`_encode_view`, `adapter.py:369`) | residual for triage | none | Today's behaviour; ICC_KEEP covers the turned paths (D-1000) |
| `inspect_import` and `write_upright_png` read the tag through `getexif()` (`adapter.py:617`, `:646`) | residual for triage | none | An imported XMP-only or raw-profile file is turned on import, though Chromium does not turn it |
| `annotate_and_save` and revert still bake onto the live copy and write the sidecar in place (`services/capture.py:1709-1713`; revert's `_rebake_annotated`, `:2214`) | residual for triage | none | Both run when the user asks and show an error at once; STAGED_REBAKE covers only the unattended scan (D-910) |
| A `.rebake-prior` or `.rebake-new` file that cannot be deleted (read-only or locked) | residual for triage | none | Recovery retries it on each scan and counts it once; `remove` (`:1792`) deletes only known names |
| The other frames of an MPO | out-of-scope | none | READ_SHOWN and the views keep the first frame, the one Chromium shows |
| `sheet` and `sheet_from_video` | out-of-scope | none | Video frames only |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

**Side effects named in the plan's §User Review Required (D-905, D-909).**
- The plain download of a tagged JPEG, MPO or PNG is decoded and re-encoded: lossy for JPEG (quality 90), an MPO keeps only its first frame, the other EXIF fields are dropped, and a re-encoded PNG can pass the 413 size limit. Untagged files and every WebP keep their own bytes.
- Old annotated copies: for tags 5 to 8, export answered 409 and listing again never cleared it; for tags 2 to 4 the old mirrored or 180-degree bake showed silently. The next scan rebakes both from the saved marks (AC-146.25, AC-146.27). Marks clamped by an earlier GUI save stay lost.
- Marks an MCP client placed earlier on a tag 5 to 8 shot were placed in the stored frame and now land turned.
- Flatten of a tagged PNG writes upright pixels with no tag (AC-146.18).

### Departures and their basis

- **The Status line (plan line 15).** The coordinator wrote Mat's execute words into it before row 0. It is a plan-text edit made after the plan review approved, and it changes no AC or contract.
- **Decision ids.** Execution decisions use D-1000 to D-1009, not "the next free id after D-910" as H1-6's row says; the coordinator assigned the range so the parallel sessions of the grouping cannot collide. D-1000 to D-1002 are used.
- **Where the decisions are recorded.** H1-6's row says an execution decision goes in the plan's YAML and each handoff's Decision Log is `None.`. Under HDP v2 §6 and the coordinator's direction, D-1000 to D-1002 are recorded in the MEU-146 handoff's Decision Log, which the closeout reads; the plan's YAML is unchanged. The MEU-145 handoff's Decision Log is `None.` because no MEU-145 decision was made in execution.
- **Row commands.** Every row ran through a `.ps1` written from its task cell, because the cells' `*>` needs PowerShell; Vitest and Electron ran through pwsh in `P:/av-kit/ui`, and every pytest run set TMP and TEMP to the plan's `tmp` folder under the receipts folder.
- **The F1 correction came after round 1 approved.** The Codex execution review's round 1 approved Session 75 with one Medium, non-blocking finding, F1: `read_shown` turned a palette PNG with a `tRNS` chunk and `_encode_view`'s PNG branch converted it to RGB, so the plain download made its transparent pixels opaque. On the coordinator's call it was corrected in this session (D-1002): a Red case first (`s75-f1-red.txt`), a one-condition fix in `_encode_view`, Green, then H1-2, H1-3, H1-4, the line-ending check, H1-6, H1-6a and H1-6b again against the new tested_state.
- **No network, no real inbox.** No row and no gate step made a network request, and every test writes into its own `tmp_path` (S5).
- **Plan lines 220 and 230 (D-1001).** After the plan was approved, AC-146.6 and AC-146.16 were changed from 40x40 to 160x160 on the coordinator's S12 ruling, with the red centre and `X-Capture-Source: 300,400` kept; the two size asserts changed with them (`test_capture_orientation.py:312`, `test_api_capture_orientation.py:140`), and nothing else in either test.
- **ICC on a turned region view (D-1000).** The plan's ICC_KEEP text names the turned whole view and READ_SHOWN; the code keeps the profile on every turned view.
- **Moved cites (Session 51 RULE-3).** Against the plan's row-0 anchors: `probe` `adapter.py:534` (was `:461`), `scan_inbox` `services/capture.py:651` (was `:597`), the route comment `routes/captures.py:425-427`; the 09 note cites both.

---

## Decision Log

```yaml
decision_log:
  - id: D-1000
    stage: execution
    question: "ICC_KEEP names the turned whole view and READ_SHOWN. Does a turned region view keep the colour profile too?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Yes: view keeps the file's icc_profile on every turned view (tag != 1), whole or region; an untagged region view still drops it, as today"
    source_tag: Local Canon
    precedents: ["packages/infrastructure/src/avkit_infra/capture/adapter.py:614 — icc = image.info.get('icc_profile') if tag != 1 else None", "docs/execution/plans/2026-11-15-capture-inbox-probe/implementation-plan.md:236 — AC-146.22, crop and export keep the profile", "docs/execution/plans/2026-11-15-capture-inbox-probe/implementation-plan.md:336 — an untagged region view dropping the profile is today's behaviour and a residual"]
    research: { engine: none, sources: [] }
    reasoning: "Crop and export already keep the profile, and the turned whole view keeps it under ICC_KEEP. A turned region is the same pixels cut smaller, so dropping the profile there alone would make a tagged region view's colours differ from its whole view. Keying the profile on the tag keeps the untagged path exactly as today, which the plan leaves as a residual. No item on the HDP list is hit: no API shape, no user file and no assertion changes."
  - id: D-1001
    stage: execution
    question: "S12: AC-146.6 and AC-146.16 say a 40x40 region of the tag-6 file comes back 40x40, but the Green code returns 160x160. Which is right?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "160x160, the D-409 4x upscale of a 40x40 region at the default max_edge. Plan lines 220 and 230 and the two size asserts (tests/unit/test_capture_orientation.py:312, tests/e2e/test_api_capture_orientation.py:140) now say (160, 160); the red centre and X-Capture-Source: 300,400 stay"
    source_tag: Local Canon
    precedents: ["D-409 — VIEW_SCALE enlarges a region view up to REGION_UPSCALE_MAX = 4 at the default max_edge", "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:327 — AC-128.5, a 100x50 region gives 400x200 at scale 4"]
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The executor stopped on S12 with this recommendation and the coordinator ruled the stop. D-409 and AC-128.5 already fix the scale, so 160x160 is existing canon and the plan's 40x40 was a planning error. The expectations sit in new Session 75 tests, so no existing assertion changes (not M-7); a corrected acceptance input is M-8, which HDP section 6 lets the hand-over cover. Evidence: the S12 scratch probes test_s12_unit.py and test_s12_e2e.py and scratch-green146.txt (2 failed, 78 passed: assert (160, 160) == (40, 40)); s75-146-green.txt after the fix (80 passed); and s75-red-146-16-corrected.txt, where the corrected AC-146.16 fails on the row-0 code at the red-centre check."
  - id: D-1002
    stage: execution
    question: "F1 (round 1 execution review): read_shown turns a palette PNG with a tRNS chunk and _encode_view's PNG branch converts it to RGB, so the plain download is opaque. Where is it corrected?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "In _encode_view's PNG branch: a P image whose info has transparency converts to RGBA, as view already does; every other mode converts as before. A new AC-146.20 case pins it"
    source_tag: Local Canon
    precedents: ["packages/infrastructure/src/avkit_infra/capture/adapter.py:608-611 — view converts P or PA with transparency in info to RGBA before it encodes", "C:/Temp/av-kit/s75-exec-review-round-1.md:37 — F1, Medium, non-blocking: READ_SHOWN loses palette-PNG transparency"]
    research: { engine: none, sources: [] }
    reasoning: "The coordinator called it: a bug in READ_SHOWN against its own contract (the shown frame, in the file's own format), not a change to an existing assertion, so no item on the HDP list is hit. _encode_view has three callers: view converts P and PA itself first, and render passes RGB, so the one changed condition only alters what read_shown returns today, and it keeps any later caller from losing the alpha the same way. Fixing it in read_shown alone would leave that trap in the shared encoder. Evidence: s75-f1-red.txt (read_shown alpha 255 where 0 and 128 were stored; the view case passed) and s75-f1-green.txt (81 passed) with s75-f1-sweep.txt (1017 passed)."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-15 | claude-code-local (Claude Opus 5.5) | Initial MEU-146 handoff after the H1-2 gate, H1-3 and H1-4 |
| Updated | 2026-11-15 | claude-code-local (Claude Opus 5.5) | After the round 1 execution review: F1 corrected (D-1002), its Red and Green records added, the gate re-run with a new tested_state |
