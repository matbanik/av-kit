---
project: "2026-11-11-capture-export-copy"
date: "2026-11-11"
source: ".agent/context/grouping/2026-11-09-video-stills-session-grouping.md#session-64--capture-export-copy-meu-136--p2"
grouping_source: ".agent/context/grouping/2026-11-09-video-stills-session-grouping.md"
meus: ["MEU-136"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Export copy (Session 64)

> **Project:** `2026-11-11-capture-export-copy`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §Residuals registered 2026-11-09 → §Export copy (`:1185-1199`, anchor `export-copy`, MEU-136).
>
> **Source request.** On 2026-11-09 Mat asked whether an agent can take stills from a video through av-kit, and accepted every recommendation of the video stills design (`_inspiration/video-stills/design.md`; grouping D-500). This is the last of the grouping's three sessions. Session 62 delivered probe and frames (MEU-133, MEU-134, commit `7403f18`) and Session 63 the sheet (MEU-135, commit `2832e3d`), all `approved`. Done comes from 09's contract, not from Mat's words: each rule holds with a behaviour test, and the design's three-task description eval (grouping D-505) runs under the method Mat rules (D-608), with its receipt cited.
> **Known issues:** `MCP-AUDIT-BASELINE-PENDING-CROP` stays open; `avkit_capture.export` joins the same pending list last (D-616) and `--update-baseline` is never run. `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` bears on the eval (D-608) and is not fixed here. `CAPTURE-EXIF-SCANNED-ORIENTATION`: export keeps the stored frame, as probe, bake and crop do, so a scanned JPEG or WebP tagged 5 to 8 exports sideways with its tag dropped; AC-136.7 records that by test, and the issue is not fixed here (D-613). `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST`: export never scans the inbox and writes only a file it has just encoded and probed, so it can neither cause nor meet that issue; not fixed here. `_run_with_progress` is left alone. Round 1 F1 found that a direct 8-bit conversion clips a 16-bit gray PNG; export maps the depth itself (D-619), and the two places that already clip it, `_encode_view` (the `image` view) and `bake`, are raised in the handoff, not fixed here (§Out of Scope).
> **Status:** `draft`, with the gate held on 2026-11-11 (Mat's words in §User Review Required, "The gate"). `plan_to_exec_gate: human`. One question is Mat's (§User Review Required): D-608, how the description eval runs. Mat also sets the execution budget at the gate.

## Goal

**Goal anchor:** Session 64 lets an agent make a small deliverable from a shot. `POST /captures/{id}/export` and `avkit_capture` `export` take the shot as it is shown (the annotated bake when it has saved marks, otherwise the original), shrink it so its long edge is at most `max_edge` (never enlarging), encode it as PNG, JPEG or WebP at `quality`, and write it into the capture inbox as a new shot with source `Export`. The source's file, sidecar and bake are only read. The response gives the new shot's id, path, size and byte count, so an agent can see when an export came out larger than it wanted and export again with a smaller edge or quality. The session also runs the design's three-task description eval on the finished video stills surface.

Four things are missing today:

1. **No resize or re-encode.** `CaptureAdapter.crop` (`packages/infrastructure/src/avkit_infra/capture/adapter.py:427`) cuts pixels into a PNG without resampling. `_encode_view` (`:271`) encodes a view in the source's own format at `LOSSY_QUALITY` (`:69`), in memory only. Nothing writes a resized or re-encoded copy.
2. **No export source member.** `CaptureSource` (`packages/core/src/avkit_core/domain/enums.py:209-223`) ends with `Video`.
3. **No copy name for a format other than PNG.** `_crop_dest` (`packages/core/src/avkit_core/services/capture.py:1659`) always returns `{stem}.png`.
4. **No export surface.** No route, schema or MCP action takes a format, an edge and a quality.

The session ends when 09's §Export copy holds with a behaviour test per rule, the eval has run under D-608 with its receipt cited (or Mat ruled C), the session gate's last line is `session-gate: all steps exit 0`, and MEU-136 is `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (2026-11-11). No payload is oversized: services/capture.py, capture/adapter.py, capture.ts and mcp-server/scripts/audit/plan.ts were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`plan_to_exec_gate: human`). Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s64-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s64\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
  - No row runs Electron (D-617), so `ELECTRON_RUN_AS_NODE` doesn't matter here; the scripts clear it anyway.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s64-plan-canonical-2026-11-11-capture-export-copy` and `s64-execution-2026-11-11-capture-export-copy`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290), and the `--review-state-only` receipt is rebuilt there.
  - Reviewer prompts name the ledger vocabulary up front: D-608 to D-621, AC-136.1 to AC-136.19, and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, anything under `.agent/fleet/hub` and `docs/proposals/2026-11-10-download-logic-divergence-report.md`, and write `<HOME>` for the home folder. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4). Each recheck carries a literal Prior Pass Summary with bare closure words (Session 52 RULE-1), names each prior finding by the review's own id (Session 53 RULE-3), and asks for a `### New Findings` table and bare words in its Recheck cells (`fixed`, `open`).
- **Never in these rows without Mat's words:** commit, push, a network request of any kind, a model, runtime, FFmpeg or Python package download, the live MCP audit, `--update-baseline`, a tag, release or upload, or an `approved` verdict authored by the implementer. Nothing touches the installed avkit MCP servers (no `mcp__avkit__*` tool is called), Mat's inbox, Mat's videos or YouTube. Every test image is made by Pillow in a temp folder. The eval's clips are made by the pinned FFmpeg under `C:/Temp/av-kit/s64/eval/`, and its server is this work tree's built `mcp-server/dist/index.js` against a fake REST backend inside `eval-harness.ts`, never a running av-kit.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-136 `capture-export-copy` | `.agent/context/handoffs/2026-11-11-capture-export-copy-MEU-136-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-11-capture-export-copy-plan-critical-review.md` and `.agent/context/handoffs/2026-11-11-capture-export-copy-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts, `s64-anchors.txt` |
| WP-2 | Type-only names (row 1) | WP-1 | shared | `CaptureSource.Export`, `ImageAnnotatePort.export`, the `export_*` stubs and `EXPORT_*` constants, `ExportResult`, the `CaptureSource` pins moved |
| WP-3 | MEU-136 Red, then Green (rows 2a, 2b, 3) | WP-2 | shared | `EXPORT_SIZE`, `EXPORT_NAME`, `EXPORT_CHECKS`, `EXPORT_SOURCE`, `EXPORT_ENCODE`, `EXPORT_WRITE`, `EXPORT_ROUTE`, `EXPORT_MCP`, `EXPORT_AUDIT`; the OpenAPI snapshot with the export route |
| WP-4 | Description eval (rows E-1 to E-4) | WP-3 | shared | `EVAL_RUN` receipts, or the D-608 C record |
| WP-5 | Records (row 6) | WP-4 | shared | The 09 note, MEU status, renders, grouping tracker |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | The handoff, review, reflection, Session 65's prompt |

**No UI (D-617).** The grouping's Session 64 entry names "service and agent layers" only and runs no Electron (grouping `:65`, `:75`). Session 63's D-593 reasoning said MEU-136 "adds a UI action and its own E2E"; that was wrong, and D-617 corrects it. An export is an ordinary shot on the Capture page, as a sheet is.

## User Review Required

> [!IMPORTANT]
> **One question is Mat's.** Every other choice is recorded as autonomous in §Decision Log (D-609 to D-620), with its alternatives. The gate asks Mat to accept the plan, rule D-608, set the execution budget, and override any autonomous choice. Only Mat's words start execution.
>
> **D-608: how does the description eval run?** (`human-check`; grouping D-505.) The design's three tasks are: find the slide shown at a transcript time in a one-hour meeting (t1); find a car's arrival in a two-hour driveway clip with the sheet zoom loop (t2); shrink a 4K screenshot to a JPEG under 500 KB (t3). The plan built the tools and dry-ran the parts that need no model:
> - `eval-seed.py` makes `meeting.mp4` (1 h, 24 slides of 150 s each, with a transcript), `driveway.mp4` (2 h, a car arrives at a time only the answer key holds) and `dashboard-4k.png` with the pinned FFmpeg and Pillow, and writes the answer key outside every run's folder.
> - `eval-harness.ts` starts this work tree's built MCP server against a fake REST backend that serves the real capture and convert service over a per-run temp inbox, allows only `avkit_capture` list, get, image, frames, sheet, export and crop and `avkit_convert` probe, and records every call in a ledger. It refuses a root outside `C:/Temp/av-kit/s64/eval/` (`C:/Temp/av-kit/s64-plan-eval-harness-refuse.txt`, `…-refuse2.txt`). That is all it enforces: each run is kept away from the answer key, its sibling runs and the repository by its prompt's instructions, not by a sandbox, since the harness doesn't check where a `path` argument points (round 1 Q11). The key is written outside every run's folder.
> - `eval-harness.ts describe` prints what a model is shown. The plan-time run on `2832e3d` (`C:/Temp/av-kit/s64-plan-eval-describe.txt`) shows the gap: the **real** surface, what Claude Code gives a model (server instructions, each tool's description and flattened input schema), describes `avkit_capture` in one line, `Workflow: capture or list → get/image → annotate…`. The per-action texts, including sheet's "To zoom, call again with a narrower start and end", are only in `_meta.action_descriptions` (receipt lines 669-685), which Claude Code doesn't show (`MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL`).
> - `eval-check.py` scores the ledgers, reports and files against the key (`EVAL_RUN`). For t3 it decodes the exported file itself with Pillow, so a response can't vouch for a file that isn't a JPEG of the reported size in the run's inbox (round 1 F2). Its selftest passes with 0 wrong, with a real JPEG positive control beside a PNG, a 16×16 JPEG, a 12-byte non-image and a JPEG outside the inbox, each claiming 1280×720 (`C:/Temp/av-kit/s64-plan-eval-check-selftest-r1d.txt`). The first run after the change, `…-r1c.txt`, was 3 wrong: the selftest's own byte-count placeholder sat inside an escaped JSON string and was never replaced; that was fixed before r1d.
>
> Each run is one fresh subagent with `model: haiku`, given one prompt from `eval-run.md` and nothing else. A weaker model reads the text more literally, which is what an eval of descriptions wants, and it is the cheapest.
> - **A (Recommended): both surfaces, six runs.** `real-t1` to `real-t3` get the real surface; `meta-t1` to `meta-t3` get it plus each action's `_meta` text. Real shows what an agent gets today; meta shows whether the per-action text itself is right. A task that fails on real and passes on meta is evidence for the open known issue, not for a wrong text. About 1.5M tokens for the six runs.
> - **B: the real surface only, three runs.** Cheaper (about 0.75M). Leaves unproven: whether the per-action texts, including the new `EXPORT_TEXT`, would mislead a model that sees them.
> - **C, do nothing:** don't run the eval. Row E-1 to E-4 are skipped and the handoff records grouping D-505 as ruled out by Mat. Leaves unproven: any of the three tasks.
>
> Under A or B, a failed run is S13: the coordinator stops, and briefs Mat with the failing run's prompt, ledger and report, a recommendation, and a do-nothing option (record the result and keep the text). No description text changes without Mat's words.
>
> **What the words in the contracts mean here, and the limits they leave.**
> - **"`max_edge` only shrinks."** The long side becomes `max_edge` and the short side is scaled with it, rounded half up, at least 1 (`EXPORT_SIZE`). When `max_edge` is missing, or at least the long side, the size is unchanged and nothing is resampled. Probed over 3,060,000 cases with 0 mismatches against an exact-fraction reference, and 0 cases that grow (`C:/Temp/av-kit/s64-probe-export.txt`).
> - **"The shot as it is shown."** The bake when the shot's sidecar holds at least one mark, otherwise the original. A marked shot whose bake is missing is refused (404 `annotated image is missing`), never silently exported without its marks (D-611).
> - **"Saves no metadata."** EXIF, XMP and text chunks are dropped. The ICC colour profile is kept, as crop keeps it, so colours don't shift (D-613). For a CMYK, YCbCr or LAB source that `_to_srgb` converts, the profile kept is the sRGB profile it returns, never the source's (round 1 Q5). The stored frame is kept: no `exif_transpose` (D-613; `CAPTURE-EXIF-SCANNED-ORIENTATION`).
> - **"`quality` changes the size."** For JPEG and WebP only; with PNG it is refused, never ignored (D-609).
> - **Limits.** A WebP can't be more than 16,383 px on an edge and a JPEG more than 65,500 (`C:/Temp/av-kit/s64-probe-export.txt`); asking for either past its limit is a fixed 422 before any write (D-610). JPEG has no alpha: a transparent source's alpha, or its transparency key, is dropped before any resize, so its stored colour shows at every size (round 2 F1). A PNG or WebP export keeps the transparency, including a transparency key on a 1-, 2- or 4-bit gray PNG (round 3 F5); a resized one keeps each fully transparent pixel's alpha 0 but not its hidden colour, because Pillow resamples alpha premultiplied (`C:/Temp/av-kit/s64-plan-alpha-probe-r2.txt`).
> - **16-bit gray.** A 16-bit gray PNG opens as `I;16`, and JPEG and WebP hold 8 bits, so export maps each value to `v × 255 / 65535` rounded half up: 0, 257, 32768 and 65535 become 0, 1, 128 and 255, never the clip to 0, 255, 255 and 255 that a direct `convert("RGB")` gives (D-619; round 1 F1; `C:/Temp/av-kit/s64-plan-depth-probe.txt`). A PNG export keeps the 16 bits unless it is resized with a transparency key. A key becomes an exact alpha for WebP and for a resized PNG; a JPEG ignores it and shows the mapped value (round 2 F1). Pillow already opens a 16-bit gray-and-alpha or 16-bit RGB PNG as 8-bit `RGBA` or `RGB`, so those lose their low bits on open, before export sees them. A 16-bit RGB PNG's transparency key can't be matched once those low bits are gone, so export removes it and that colour exports opaque (round 3; §Out of Scope). A marked 16-bit shot exports its bake as it is, and `bake` clips 16-bit gray today (§Out of Scope).
>
> **The token estimate,** calibrated against Session 63 `capture-video-sheet` (plan 7,888,532 in 1 round; execution 13,275,057 in 1 round), Session 59 `capture-crop-copy` (plan 23,266,843 over 3 rounds; execution 12,812,411 over 2), Session 62 (plan 20,835,539 over 4 rounds; execution 13,244,126) and Session 58 (plan 19,334,552; execution 11,719,424). This session has one MEU across core, the capture adapter, the API and MCP, 19 ACs, no deadline machinery and no real-FFmpeg test, plus the eval. Expect 1 to 3 plan rounds (about 8M to 21M). The plan loop opens with the default 10.5M. At the plan gate Mat sets the execution loop's budget; the opening ask is round 1 ×2 plus one recheck at about half of round 1 (Session 60 RULE-5, Session 58 RULE-4): about 12M ×2 + 6M ≈ 30M over 3 rounds, plus about 1.5M for the eval under A. The citable AC family is fixed when the plan loop opens: AC-136.
>
> **The gate.** Held 2026-11-11: Mat said "accept the plan, D-608 A, execution budget 60M", which accepts the plan, rules D-608 A, and sets the execution loop's budget at 60M, above the ask of about 31.5M. The plan review approved in round 4 of 5 with no open finding (`.agent/context/handoffs/2026-11-11-capture-export-copy-plan-critical-review.md`; 25,009,271 tokens over 4 rounds, from the ledger lines in `C:/Temp/av-kit/dispatch/s64-plan-run-r1.txt` to `…-r4.txt`). No autonomous decision was overridden.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `EXPORT_SIZE` | `export_size(width: int, height: int, max_edge: int \| None) -> tuple[int, int]` in `services/capture.py`, pure, integers only. When `max_edge` is `None` or `max_edge >= max(width, height)`, it returns `(width, height)`. Otherwise `long` and `short` are the larger and smaller edges; the new long edge is `max_edge` and the new short edge is `max(1, (2 × max_edge × short + long) // (2 × long))`, which is `max_edge × short / long` rounded half up (Session 59 RULE-4); the pair is put back in the source's orientation (a square stays square). Named cases from the probe: 128×3 → 64×2 (1.5 up), 128×5 → 64×3 (2.5 up), 128×7 → 64×4 (3.5 up), 130×3 → 64×1 (1.48 down), 101×51 → 64×32, 51×101 → 32×64, 100000×1 → 64×1 (floor guard), 3840×2160 at 1920 → 1920×1080. |
| `EXPORT_NAME` | `export_stem(source_stem: str) -> str` in `services/capture.py` is `_IMPORT_STEM_DROP.sub("_", source_stem).strip(" _-")[:IMPORT_STEM_MAX]`, then `.strip(" _-")` again, plus `EXPORT_STEM_TAG = "-export"`; an empty result gives `EXPORT_STEM_FALLBACK = "export"`. `_IMPORT_STEM_DROP` keeps word characters, space and `-`, so a lone surrogate or control character becomes `_` and never reaches a name. The stem always ends in `-export`, so it is never a Windows reserved name. `_crop_dest(uow, inbox, stem, ext=FLATTEN_PNG_SUFFIX)` gains the keyword `ext` (D-615), and returns `inbox / f"{candidate}{ext}"`; its taken rule is unchanged, so `x-export.png` then a JPEG export gives `x-export_2.jpg`. `EXPORT_SUFFIXES = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}`. Crop's callers pass no `ext` and are unchanged. |
| `EXPORT_CHECKS` | `CaptureService.export_shot(shot_id: str, *, fmt: str, max_edge: int \| None = None, quality: int \| None = None) -> ExportResult` checks, in order, before taking the lock and before any I/O: `fmt` in `EXPORT_FORMATS = ("png", "jpeg", "webp")`, else `ValidationError("format must be png, jpeg or webp")`; `max_edge` `None` or an `int` that isn't a `bool`, `REGION_MAX_EDGE_MIN` (64) to `EXPORT_MAX_EDGE_MAX` (16,383), else `ValidationError("max_edge must be between 64 and 16383")`; `quality` `None` or an `int` that isn't a `bool`, 1 to 100, else `ValidationError("quality must be between 1 and 100")`; `quality` not `None` with `fmt == "png"` gives `ValidationError(EXPORT_QUALITY_PNG)`, `"quality applies to jpeg and webp only"` (D-609). Then, under the lock: the shot (`capture shot {id} not found`, 404, as crop); the source (`EXPORT_SOURCE`); `size = export_size(shot.width, shot.height, max_edge)`; and when `fmt` has an edge limit in `EXPORT_EDGE_LIMIT = {"jpeg": 65500, "webp": 16383}` and `max(size)` is above it, `ValidationError(EXPORT_TOO_LARGE)`, `"the export is too large for this format; lower max_edge"` (D-610). Every message is fixed; none echoes the input. A refused call writes nothing. |
| `EXPORT_SOURCE` | `marks = self._saved_marks(shot.original_path)` (a malformed sidecar is the existing 422 `sidecar is malformed`); the source is `self._variant_path(shot, "annotated")` when `marks` is not empty, else `self._variant_path(shot, "original")`, so a missing bake is 404 `annotated image is missing` and a missing original 404 `original image is missing` (D-611). The source size passed on is `(shot.width, shot.height)`, which the bake shares. |
| `EXPORT_ENCODE` | `ImageAnnotatePort.export(self, source: Path, source_size: tuple[int, int], out: Path, *, fmt: str, size: tuple[int, int], quality: int \| None) -> ImageProbe`, implemented by `CaptureAdapter.export` (D-614). It opens and loads `source` (any failure is the fixed `InboxPathError("the image could not be opened")`), refuses a size other than `source_size` with crop's fixed `ConflictError`, and keeps `icc_profile` and nothing else from `info`. Modes, in this order: (1) CMYK, YCbCr and LAB go through `_to_srgb`; when it returns a profile, that sRGB profile replaces the kept one, so the source's CMYK or LAB profile is never attached to RGB pixels (round 1 Q5). (1b) The PNG key (D-614; round 3 F5): export opens `source` once as a binary file, reads its first 26 bytes, seeks back to 0 and gives the same handle to `Image.open`, so a failure in any of that is the same fixed `InboxPathError`. `_png_key(image, header)` then corrects a `transparency` key that Pillow reports on a different scale from its samples. For a PNG whose IHDR colour type (byte 25) is 0 and bit depth (byte 24) is 2 or 4, the key becomes `key × (255 // (2 ** depth − 1))`, because Pillow scales those samples to 0 to 255 but not the key. For colour type 2 at depth 16 the key is removed, because Pillow keeps only each sample's high byte and no exact key exists. Any other image is unchanged (`C:/Temp/av-kit/s64-plan-key16-probe-r3.txt`, `C:/Temp/av-kit/s64-plan-keynorm-probe-r3.txt`; unresized WebP and PNG, `C:/Temp/av-kit/s64-plan-webp-unresized-probe-r3.txt`). (2) The depth map (D-619): a mode in `EXPORT_DEPTH_MODES = ("I;16", "I;16L", "I;16B", "I;16N", "I")` becomes `L` through `_depth_to_l`, which maps each value `v` to `(2 × v × 255 + 65535) // (2 × 65535)` clamped to 0 to 255 (`v × 255 / 65535` rounded half up), when `fmt` is jpeg or webp, when the mode isn't in `_CROP_KEPT_MODES` (`I`, `I;16L`, `I;16B` or `I;16N`), or when a PNG will be resized and the image has a `transparency` key. With a key `t` and `fmt` webp or png, an alpha band that is 0 exactly where `v == t` and 255 elsewhere is merged in, giving `LA`; for jpeg the key is ignored. Otherwise a PNG export keeps `I;16`, resized natively when asked. (3) JPEG: `convert("RGB")` now, before any resize, so an alpha band or a `transparency` key is dropped and the stored colour shows at every size. Pillow resamples an image with alpha premultiplied, so resizing first turns every fully transparent pixel black (round 2 F1; `C:/Temp/av-kit/s64-plan-alpha-probe-r2.txt`). (4) PNG and WebP, when the image will be resized: a `1`, `L`, `P` or `RGB` image with a `transparency` key becomes `LA` (from `1` or `L`) or `RGBA` through Pillow's own convert, which turns the key into alpha 0 and leaves no `transparency` in `info` (`C:/Temp/av-kit/s64-plan-key8-probe-r2.txt`; for `1`, `C:/Temp/av-kit/s64-plan-keynorm-probe-r3.txt`); a `P` without one becomes `RGB`, and a `1` without one becomes `L`. (5) It is resized with `LANCZOS` only when `size` differs from its size; a fully transparent pixel keeps alpha 0, not its hidden colour. (6) JPEG is saved with `quality=quality if quality is not None else LOSSY_QUALITY`. WebP: `RGBA` when the image has an alpha band or transparency, else `RGB`, saved with the same quality. PNG: a mode in `_CROP_KEPT_MODES` is kept, any other becomes `RGBA` or `RGB`; no quality. The `transparency` passed to a PNG save is read from the image being saved, never from the opened source as crop reads it (`adapter.py:458`), so no key is written beside an alpha band. Every save passes `icc_profile` only when there is one, and no `exif`, `xmp` or `pnginfo`. It writes `out` and returns `self.probe(out)`. A save failure raises `OSError("the export could not be saved")` from the cause, whose text holds no path. No `exif_transpose` (D-613). |
| `EXPORT_WRITE` | Crop's copy pipeline (`crop_shot`, `services/capture.py:1544-1644`), with one output and no sidecar. Under `with CAPTURE_FILE_LOCK:` and one unit of work: the shot, `EXPORT_SOURCE`, the size and edge checks, `inbox = self._inbox()` (read here, at use; Session 61 RULE-2), `self._annotate.ensure_dir(inbox)`, `dest = self._crop_dest(uow, inbox, export_stem(shot.original_path.stem), ext=EXPORT_SUFFIXES[fmt])`, the temp `dest + ".avkit-tmp"` opened `"xb"` and closed, `self._annotate.export(source, (shot.width, shot.height), tmp, fmt=fmt, size=size, quality=quality)`, `os.replace(tmp, dest)`, `probe = self._annotate.probe(dest)`, `size_bytes = dest.stat().st_size`, `new = self._upsert_shot(uow, dest, probe, now, CaptureSource.Export)`, then the commit. On any exception: the temp is discarded; once moved, `dest` is discarded; before the encode has run, an exception in `EXPORT_REFUSALS` (crop's `CROP_REFUSALS`) passes unchanged; anything else becomes `CaptureFailedError(EXPORT_NOT_WRITTEN)`, `"the export could not be written"` (503). The source's file, sidecar, bake and row are only read. No `confirm`. `ExportResult(shot: CaptureShot, source_id: str, bytes: int)`. |
| `EXPORT_ROUTE` | `POST /captures/{id}/export` in `routes/captures.py`, declared after `/{id}/crop` and before `DELETE /{id}`, status 201. `CaptureExportIn(ApiModel)` (`extra="forbid"`): `format: Literal["png", "jpeg", "webp"]`, `max_edge: Annotated[StrictInt, Field(ge=64, le=16383)] \| None = None`, `quality: Annotated[StrictInt, Field(ge=1, le=100)] \| None = None`, with a `field_validator("max_edge", "quality", mode="before")` that refuses an explicit `null`, as MCP refuses it (D-610). A schema refusal is the fixed 422 `validation_error` `Request validation failed`. `CaptureExportOut`: `shot: CaptureExportShotOut {id, path, width, height, bytes}` and `source_id`, with no image bytes (D-618). |
| `EXPORT_MCP` | `avkit_capture` `export`: `z.strictObject({action: z.literal("export"), id: captureId, format: z.enum(["png", "jpeg", "webp"]), max_edge: z.number().int().min(64).max(16383).optional(), quality: z.number().int().min(1).max(100).optional()}, {error: (issue) => (issue.code === "unrecognized_keys" ? EXPORT_UNKNOWN_KEY : undefined)})`, with `EXPORT_UNKNOWN_KEY = "export accepts only action, id, format, max_edge and quality"`: an unknown key's name never comes back in the refusal, and every other refusal keeps zod's own text (D-620; round 1 F4; `C:/Temp/av-kit/s64-plan-strict-probe.txt`). It is appended after `sheet` in `capture.ts`, with its row `{ tool: "avkit_capture", action: "export", method: "POST", path: "/captures/{id}/export" }` after `sheet`'s in `ACTION_INDEX` (`registry.ts:136`). `export` joins the capture actions in the `ADD_TIMEOUT_MS` selection (`registry.ts:391-401`, 120 s), as crop, frames and sheet are, under a comment line `// EXPORT_MCP under D-616 A: a full-size WebP at Pillow's pixel refusal edge encodes in about 83 s.` (D-616; round 1 Q7). Its description is `${desc("export", "POST", "/captures/{id}/export")} ${EXPORT_TEXT}`, crop's form, with `EXPORT_TEXT`: `Writes a resized or re-encoded copy as a NEW shot and returns its id, path, width, height and bytes; the source is never changed. format png, jpeg or webp. max_edge (64-16383) shrinks the long edge and never enlarges. quality (1-100, default 90) is for jpeg and webp only. Exports the shot as shown: the annotated image when it has saved marks, else the original. Keeps the colour profile and no other metadata. To get under a byte size, export again with a smaller max_edge or quality and check bytes.` The transports filter two inputs differently, both documented (transport parity, not identical filters): `quality` with `png` is refused by the API, not by the schema; and an integral JSON number such as `64.0` is refused by REST's `StrictInt` but reaches MCP as the JavaScript number 64, which `.int()` accepts and the call sends to REST as `64` (D-610; round 1 F3). |
| `EXPORT_AUDIT` | `BASELINE_PENDING` (`mcp-server/tests/audit/coverage.test.ts:23-27`) gains `"avkit_capture.export"` last, with a MEU-136 comment line. `AUDIT_PLAN` (`mcp-server/scripts/audit/plan.ts`) gains an offline `capture.export` step after `capture.sheet` (`:1670-1697`), `depends_on: ["capture.crop"]`, phase `lifecycle`, calling `{action: "export", id: <the crop step's shot id>, format: "jpeg", max_edge: 64}` and checking a 201, REST `source` `"Export"` on the new shot and the source's SHA-256 unchanged, in the form of the `capture.crop` step (`:1600`). |
| `EXPORT_SOURCE_MEMBER` | `CaptureSource.Export = "Export"`, after `Video`, with the comment `# EXPORT_SOURCE (MEU-136, D-618): a resized or re-encoded copy written by POST /captures/{id}/export.` `RegisterSourceWire` (`schemas/captures.py:29`) is unchanged, so `Export` has no register wire value. The shot `source` field is a plain `str` (`schemas/captures.py:176`), so the OpenAPI snapshot doesn't change for the member. A later inbox scan keeps `Export` (`_upsert_shot` keeps a known row's source). |
| `NO_RAW_OUTPUT` | No new log line, error message or response field carries a path or Pillow's exception text, except the 201 body's `shot.path`, which names the shot the caller now owns. `export_shot` logs `capture.export` with `shot_id` and `source_id` only. Pillow's text stays in `__cause__`, which no handler prints. On MCP an unknown key in an `export` call is refused with the fixed `EXPORT_UNKNOWN_KEY`, so a key holding a path never comes back (D-620); the other strict actions still name an unknown key in their refusal, to the calling client only and never in a log (§Out of Scope). |
| `EVAL_RUN` | The D-608 eval, by `eval-run.md`, `eval-seed.py`, `eval-harness.ts` and `eval-check.py` in this folder. Pass rules (`eval-check.py`): every run calls nothing outside the allowlist (a refused attempt is listed, not counted) and leaves the media's SHA-256 as the key holds it; t1 makes at least one successful frames or sheet call on `meeting.mp4` and one successful image call, and reports `slide: <title>` equal to the key's (case and spacing aside); t2 makes at least two successful sheet calls on `driveway.mp4` and reports `arrival: <seconds>` within 5 s of the key's; t3's last successful export asked for JPEG from the seeded shot and reports under 500,000 bytes and at least 1280 px on its long edge; its file exists with that size directly in the run's inbox and decodes with Pillow as a JPEG whose own size equals the reported width and height (round 1 F2); `dashboard-4k.png` is unchanged; and the report names the new shot. Exit 0 only when every line passes; under C it prints `not run under D-608 C` and exits 0. |

### Deadline inventory (Session 62 RULE-1)

Export has no deadline, as crop has none. Every blocking call, with its bound:

| # | Blocking call | Bound |
|---|---|---|
| 1 | `CAPTURE_FILE_LOCK` wait | the holder's own: crop, flatten, revert, annotate and remove are each one local file operation; sheet and frames hold it only to reserve and to publish (`SHEET_WRITE`, `FRAME_WRITE`); an export holds it through its own encode (row 4), so a second export can wait one export's encode. Not a numeric bound |
| 2 | Connection checkout and commit (SQLite `busy_timeout` 5,000 ms, `engine.py:68`) | as crop |
| 3 | Open and decode the source | `Image.MAX_IMAGE_PIXELS` 89,478,485 (baseline S4 check) is a warning: above it Pillow opens the image with a `DecompressionBombWarning`, whose text names no path. Above twice it, 178,956,970, Pillow raises `DecompressionBombError`, which is the fixed open refusal. On this machine a 16,383×10,922 PNG (178,935,126 px) opened and loaded in 0.36 s, and a 16,384×10,923 one (178,962,432 px) was refused (`C:/Temp/av-kit/s64-plan-cap-probe.txt`) |
| 4 | Resize and encode | on a 3840×2160 source: PNG 0.17 s, JPEG q90 0.02 s, WebP q90 0.85 s (`s64-probe-export.txt`). On the 178,935,126 px source of row 3: full-size WebP q90 82.53 s, JPEG 0.38 s, PNG 2.00 s; a LANCZOS shrink to 1920 0.78 s and its WebP 0.32 s (`C:/Temp/av-kit/s64-plan-cap-probe.txt`). The full-size WebP is the worst case, and it is past the 30 s MCP default |
| 5 | `probe` of the output and `stat` | one decode of the output |

So `export` joins `ADD_TIMEOUT_MS` (120 s), as crop, frames and sheet are (D-616; round 1 Q7). The 120 s is not a bound either: on a slower machine, or behind another export holding the lock, the client can give up first. The server still finishes the export whole or discards it whole (`EXPORT_WRITE`), so the agent's next `list` shows the new shot or nothing, never a half-written file. That is crop's behaviour today; no enforced server deadline is added.

### Pins that move

| Pin | Where | From → to | Row |
|---|---|---|---|
| Last `CaptureSource` members | `tests/unit/test_domain_capture.py:911-912` (AC-134.1) | `members[-1] == "Video"`, `members[-2] == "Crop"` → `members[-2] == "Video"`, `members[-3] == "Crop"` | 1 |
| `CaptureSource` tuple | `tests/unit/test_domain.py:298-308` | gains `"Export"` last | 1 |
| Response sources | `tests/e2e/test_api_captures.py:93-103` (`SOURCE_OUT`) | gains `"Export"` last | 1 |
| Crop then Video | `test_domain_capture.py:894` (AC-130.7, `members[members.index("Crop") + 1] == "Video"`) | unchanged | — |
| Route census | `tests/e2e/test_api_openapi.py` `ROUTE_INDEX` (after the crop row, about `:60`) and the count at `:120` | gains `("POST", "/api/v1/captures/{id}/export")`; 77 → 78 | 2a |
| Operation counts | `tests/e2e/test_api_openapi.py:206` (AC-134.17) and `:251` (AC-135.20) | 77 → 78 | 2a |
| Operation and action counts | `tests/e2e/test_api_downloads.py:372` (`ROUTE_COUNT_AFTER`) and `:378` (`ACTION_INDEX_AFTER`) | 77 → 78 and 74 → 75, with a MEU-136 comment line | 2a |
| Valid bodies | `tests/e2e/test_api_bodies.py` (`_valid_body`) | gains `{"format": "png"}` for export | 2a |
| MCP action counts | `mcp-server/tests/action-index.test.ts:45`; `capture.test.ts:116`, `:895`, `:1060`, `:1252`; `convert.test.ts:61`; `m7-resource.test.ts:47` (title), `:57`, `:69` (title), `:78`; `audit/coverage.test.ts:44-46` (comment and title) | 74 → 75 | 2b |
| Built-server action count | `mcp-server/tests/audit/runner-fake-backend.test.ts:65` (title), `:80` and `:193` | 74 → 75, with a MEU-136 comment line | 2b |
| Capture action count | `capture.test.ts:135`, `:907`, `:1267` | 13 → 14 | 2b |
| Capture actions | `capture.test.ts:23-41` (`CAPTURE_ACTIONS`) | gains `{ action: "export", method: "POST", path: "/captures/{id}/export" }` after `sheet`, with a comment | 2b |
| Expected rows | `mcp-server/tests/fixtures.ts:226` (`minimalInput`) and `:315` (expected body) | gain `"avkit_capture.export": { action: "export", id: …, format: "png" }` and `{ format: "png" }`, in the form of the crop rows | 2b |
| Pending baseline | `coverage.test.ts:23-27` (`BASELINE_PENDING`) and its last-key pin (`:297`, AC-135.19) | gains `"avkit_capture.export"` last; the last-key pin reads `avkit_capture.export` | 2b |
| Sheet row position | `capture.test.ts` (AC-135.19) | unchanged: `sheet` is still directly after `frames`; AC-136.18 adds `export` directly after `sheet` | — |

A pin in `tests/` moves in row 1 or 2a, and one in `mcp-server/tests/` in row 2b. Each Red row greps again, in every test file of `tests/`, `mcp-server/tests/` and `ui/tests/` (Session 62 RULE-4, Session 63 RULE-1): every literal `74`, `77` or `13` next to an action or route list, every test that walks `ACTION_INDEX`, `ROUTE_INDEX`, `CAPTURE_ACTIONS` or `CaptureSource`, each pin's order and adjacency (`members[-n]`, "directly after", "last"), and every signature-equality test over `ImageAnnotatePort` or `CaptureAdapter`. **Absence pins (Session 61 RULE-3):** the plan-time grep of the three test trees for `export`, `Export`, `capture.export` and the new names (`C:/Temp/av-kit/s64-plan-probes.txt`) is read again in row 2a; any test asserting an export name is absent moves in its Red row. `runner-fake-backend.test.ts` launches the built server, so row 2b builds the MCP server before its Red run and row 3 builds it before the whole MCP suite.

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **The shot id** comes from the path; it reaches the database lookup and the `not found` message (crop's existing message), the 201 body's `source_id` and the log line. Its writers: the caller, and the ids the service itself made.
- **The source's stem** goes through `export_stem` into the export's name, which reaches the inbox, the row, the 201 body's `shot.path` and the Capture page. A control character or lone surrogate becomes `_` (AC-136.3).
- **`format`** comes from a closed set; it picks the encoder and the suffix. It is not echoed in any message.
- **`max_edge` and `quality`** reach `export_size` and the encoder. A refused value's message echoes nothing.
- **The inbox path** is read from settings at use (`self._inbox()`), and reaches `dest`, the row and the 201 body only.
- **Pillow's exception text**, which can hold a path, stays in `__cause__`; the error body, the log and the console carry the fixed messages only (AC-136.15).
- **The exported pixels** come from the source's pixels only, with the ICC profile; no EXIF, XMP or text reaches the file (AC-136.4).

### Spec text (D3)

| File | Lines at `2832e3d` | Change |
|---|---|---|
| `docs/build-plan/09-screenshot-capture.md` | after the §Export copy Tests row (`:1199`) | A Delivered note naming the mechanism ids, AC-136.1 to .19, D-608 as ruled with the eval's result, the eval receipt and this plan folder, in the format of the Session 63 note (`:1172-1183`) |

Row 6 re-reads the anchor before it writes (Session 51 RULE-3) and cites the lines as they read then. `09` is CRLF.

### MEU-136 `capture-export-copy`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `POST /captures/{id}/export` body | `schemas/captures.py` `CaptureExportIn` | `EXPORT_ROUTE`; `quality` with `png` in `EXPORT_CHECKS` | `extra="forbid"`, fixed 422 |
| MCP `avkit_capture` `export` | `capture.ts` | `EXPORT_MCP` | `z.strictObject` with the fixed `EXPORT_UNKNOWN_KEY` (D-620), refused before fetch |
| 201 body | `CaptureExportOut` | `shot` and `source_id` only; `shot` `{id, path, width, height, bytes}` | — |
| `ImageAnnotatePort.export` | `ports/capture.py` | `EXPORT_ENCODE` | — |
| Inbox file and row | `CaptureService` | `EXPORT_NAME`, `EXPORT_WRITE`, `CaptureSource.Export` | — |

#### Acceptance Criteria

Test names start `test_ac_136_<n>_` (Python) and `AC-136.<n>` (Vitest). New Python files are LF.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-136.1 | Unit | Type characterisation of row 1's names: `ImageAnnotatePort.export` has positional `source`, `source_size`, `out` and keyword-only `fmt`, `size`, `quality`; `CaptureAdapter.export`'s signature equals the protocol's in name, kind, annotation and default; `CaptureSource` ends `Crop`, `Video`, `Export`; `CaptureSource.Export.value == "Export"`; neither `"Export"` nor `"export"` is in `get_args(RegisterSourceWire)`. In `test_domain_capture.py`. It passes from row 1 and runs as a guard. | 09 Source member | Signature drift fails |
| AC-136.2 | Unit | `EXPORT_SIZE`: the eight named cases of §Single-statement contracts; `None`, an equal edge and a larger edge return the size unchanged; an exhaustive loop over every `width` and `height` from 1 to 200 and every `max_edge` from 64 to 220 (Session 62 RULE-5) checks against `Fraction` half-up rounding, that the long edge is `min(max_edge, long)`, that neither edge grows, that both are at least 1 and that orientation is kept. In `test_capture_export_service.py`. | 09 Request | Half cases each way; never grows |
| AC-136.3 | Unit | `EXPORT_NAME`: `shot` → `shot-export`; `Łodz` keeps `Łodz-export`; a stem holding a lone surrogate, one holding `\x07` and `\x1b`, one of only `..`, and an empty stem each give a name with no surrogate, no control character and a non-empty stem, the empty ones `export` (Session 53 RULE-1); a 150-character stem is cut to 100 before `-export`; `CON` gives `CON-export`. `_crop_dest` with `ext=".jpg"`: an empty inbox gives `x-export.jpg`; `x-export.png` present gives `x-export_2.jpg`; `x-export.jpg.avkit-tmp` present gives `x-export_2.jpg`; with no `ext` it still gives `.png` (crop unchanged). In `test_capture_export_service.py`. | 09 Name | Surrogate, control-character and empty stems |
| AC-136.4 | Unit | `EXPORT_ENCODE` with the real `CaptureAdapter`: for each format, an RGB source with EXIF (orientation 1, a camera tag), XMP, a PNG text chunk and an sRGB ICC profile exports with no `exif` and no `xmp` in `info`, no text chunk, `getexif()` empty, and the same ICC bytes; the output opens as the format asked; `size` equal to the source writes the same size (no resample: a 1-px checkerboard keeps its exact pixels in PNG); a shrink gives exactly `size`; modes RGBA, LA, L, P with transparency, 1, I;16 and CMYK with a profile each export in all three formats, with PNG keeping L, LA, RGBA, P and I;16 when not resized, JPEG always RGB, and WebP RGBA exactly when the source has alpha. The depth map (D-619): `_depth_to_l` over all 65,536 `I;16` values equals `(2 × v × 255 + 65535) // (2 × 65535)` with 0 mismatches, and an `I` image holding -5 and 70000 gives 0 and 255; a 256×64 `I;16` source of four 64-px blocks at 0, 257, 32768 and 65535 exports at its own size and at `max_edge` 128 with block centres at 0, 1, 128 and 255 within 2 for JPEG and WebP; PNG keeps `I;16` with centres at exactly 0, 257, 32768 and 65535 unresized and within 1 resized without a key; the source is built from raw little-endian bytes and its four centres are asserted before any export, because `paste(32768)` into `I;16` writes 0 on Pillow 13.0.0 (`C:/Temp/av-kit/s64-plan-alpha-probe-r2.txt`). With a transparency key on the 32768 block, at its own size and at `max_edge` 128: JPEG is `RGB` with centres within 2 of 0, 1, 128 and 255 (the keyed-and-shrunk regression round 2 F1 asked for); WebP is `RGBA` with that block's alpha 0 and the other three blocks' alpha 255 and centres within 2 of 0, 1 and 255; PNG unresized keeps `I;16` with `transparency` 32768; PNG resized is `LA` with that block's alpha 0, the other three blocks' alpha 255 and luminance within 1 of 0, 1 and 255, and no `transparency` in `info`. A fully transparent block's colour is not asserted after a resize, because Pillow resamples alpha premultiplied. The 32768 block is never 255 in any output (the clip round 1 F1 found). Stored colour (round 2 F1): an RGBA source with a fully transparent region stored as (200, 40, 40), and a P source whose transparent index is (200, 40, 40), export to JPEG at their own size and at `max_edge` 128 with that region's centre within 3 of (200, 40, 40), never black; an `L` source keyed at 128 and an `RGB` source keyed at (200, 40, 40), shrunk to PNG, give `LA` and `RGBA` with alpha 0 on the keyed region and no `transparency` in `info`. Keys Pillow misreads (round 3 F5), from hand-written PNG bytes with a `tRNS` chunk as in `C:/Temp/av-kit/s64-plan-keynorm-probe-r3.txt`: a 256×64 1-bit gray PNG of alternating 1-px columns, black and keyed white, shrunk to `max_edge` 128, gives PNG `LA` and WebP `RGBA` with the centre's alpha within 10 of 127 and its colour within 10 of black, never the opaque grey (127, 127, 127, 255) the round 2 order gives; 1-bit (keys 0 and 1), 2-bit (keys 1 and 3) and 4-bit (keys 1 and 15) gray PNGs of 32-px stripes, keyed stripes alternating with unkeyed ones, give alpha 0 inside the keyed stripes and 255 inside the others, in PNG and WebP, unresized and shrunk, with no `transparency` in any alpha-bearing output's `info`, and JPEG shows each keyed stripe's stored value within 3; a 16-bit RGB PNG with a key exports with no `transparency` in `info` and every pixel's alpha 255. In the new `tests/unit/test_capture_export_adapter.py`. | 09 Writes, Tests | Metadata planted in each source; the midtone block, its centres asserted before export; the stored colour under alpha 0; F5's 1-px columns, which the round 2 order turns opaque grey |
| AC-136.5 | Unit | Quality: one noisy 512×512 RGB source exported at quality 20 and 95 gives strictly smaller bytes at 20, for JPEG and for WebP; a recording wrapper around `Image.Image.save` sees `quality=90` (`LOSSY_QUALITY`) when `quality` is `None`, `quality=37` when 37 is passed, and no `quality` key for PNG. In `test_capture_export_adapter.py`. | 09 Request, Tests | `None` passes 90 |
| AC-136.6 | Unit | Adapter failures: an undecodable source raises `InboxPathError` whose text is exactly `the image could not be opened`; a size other than `source_size` raises crop's `ConflictError`; a save that raises `OSError` holding a marker path raises `OSError` whose text is exactly `the export could not be saved` and doesn't hold the marker. In `test_capture_export_adapter.py`. | 09 Writes | Marker absent from the text |
| AC-136.7 | Unit | `CAPTURE-EXIF-SCANNED-ORIENTATION` characterisation (D-613): a 400×300 JPEG tagged orientation 6 exports at 400×300 in its stored frame (the pixel at a corner marked red is red at the same stored corner), and the output has no orientation tag. The test's docstring names the known issue; it records the behaviour and fixes nothing. In `test_capture_export_adapter.py`. | Known issue | The stored frame, not the turned one |
| AC-136.8 | Unit | `EXPORT_CHECKS` with a recording fake `ImageAnnotatePort` and a temp inbox: each refusal (`format` `"gif"`, `"JPEG"` and `""`; `max_edge` 63, 16384, `True`, `64.0`, 1e308, `-10**18` and `10**18`; `quality` 0, 101, `True`, `50.0`, 1e308, `-10**18` and `10**18`; `quality` 50 with `png`; an unknown id; a marked shot with no bake; a missing original; a malformed sidecar; a WebP export of a 20000×10 source with no `max_edge`, and a JPEG export of a 70000×1 source) makes no `export` call, leaves the inbox as it was and adds no row (Session 62 RULE-2); `max_edge` 64 and 16383 and `quality` 1 and 100 are accepted. Each error is checked by type and message first (Session 62 RULE-3), and each message is the fixed text. In the new `tests/unit/test_capture_export_service.py`. | 09 Request, D-609, D-610, D-611 | Every refusal records zero exports |
| AC-136.9 | Unit | `EXPORT_SOURCE` and the call trace (Session 55 RULE-3): with a recording fake, a shot with saved marks and a bake passes the bake's path, `(shot.width, shot.height)`, the temp path, `fmt`, `export_size(…)` and `quality` unchanged; a shot with no sidecar, and one whose sidecar holds no marks, pass the original. In `test_capture_export_service.py`. | 09 Source | Marked versus unmarked |
| AC-136.10 | Unit | `EXPORT_WRITE` with the real adapter: the temp is opened `"xb"` (a recording `Path.open`), an existing `x-export.png.avkit-tmp` from another writer makes the name taken and is left byte for byte (Session 58 RULE-1); two PNG exports of one shot give `x-export.png` then `x-export_2.png`; a PNG then a JPEG export give `x-export.png` then `x-export_2.jpg`; the source file, its sidecar and its bake keep their SHA-256 and the source row is unchanged; the new row has source `Export`, the probed size, no sidecar and no annotated path; `ExportResult.bytes` equals the file's size; no `.avkit-tmp` remains. In `test_capture_export_service.py`. | 09 Writes, Name, Source member | Never an overwrite |
| AC-136.11 | Unit | Failure cleanup: a fake `export` raising `OSError`, an output probe raising `InboxPathError`, an `os.replace` raising `OSError` and an `_upsert_shot` raising each give `CaptureFailedError` with exactly `the export could not be written`; afterwards no new file, no temp and no new row exist, and a pre-existing shot is unchanged; a refusal raised by the adapter before it writes (`InboxPathError`, `ConflictError`) passes unchanged with its own text. In `test_capture_export_service.py`. | 09 Writes | Partial failure leaves nothing |
| AC-136.12 | Unit | `NO_RAW_OUTPUT` in the service: with a source stem holding a marker, a successful export logs `capture.export` with exactly the keys `shot_id` and `source_id`, and no log record holds the marker; each refusal's message doesn't hold it. In `test_capture_export_service.py`. | NO_RAW_OUTPUT | Marker absence with a positive control |
| AC-136.13 | API | `POST /captures/{id}/export` on the real stack with the real `CaptureAdapter`: 201 with exactly `{shot, source_id}`, `shot` with exactly `{id, path, width, height, bytes}`; for each format the file at `shot.path` opens in that format with that size and `bytes` equals its size; `max_edge` 64 on a 300×200 source gives 64×43 and `max_edge` 1000 gives 300×200 (never grows); the output has no EXIF; a shot annotated through `POST /captures/{id}/annotate` exports the bake (a pixel under a mark has the mark's colour, and the same pixel of the original doesn't); the source bytes are unchanged; two exports give `-export` and `-export_2`; `GET /captures/{id}` shows `source` `"Export"`, and a scan after a new file is dropped in keeps it `"Export"`. In the new `tests/e2e/test_api_capture_export.py`. | 09 Response, Tests | Never grows; marked versus unmarked |
| AC-136.14 | API | Route validation: the fixed 422 for an extra key, a missing `format`, `format` `"gif"`, `max_edge` 63, 16384, `null`, `true`, `64.0`, `64.5` and `10**18`, `quality` 0, 101, `null`, `true`, `80.0` and `10**18`, and `max_edge` 1e308 (`64.0` and `80.0` are sent as raw JSON text, so they reach the API as JSON floats; round 1 F3); `quality` with `png` gives `quality applies to jpeg and webp only` (422); an unknown id gives 404. No file or row is added by any of them. In `test_api_capture_export.py`. | 09 Request | Each schema refusal |
| AC-136.15 | API | Errors are path-free on the real stack: a marked shot with its bake deleted gives 404 `annotated image is missing`; a source replaced by undecodable bytes gives 422 `the image could not be opened`; a forced write failure gives the masked 503. Under Session 54 RULE-2 the stack builds `HealthService` first, and a marker in the inbox path is absent from every error body, the log ring, captured stdout and stderr, with a positive control that logs the marker once and finds it. In `test_api_capture_export.py`. | 09 Writes | Marker absence with a positive control |
| AC-136.16 | API | OpenAPI: `POST /api/v1/captures/{id}/export` with `CaptureExportIn` and `CaptureExportOut` in the regenerated snapshot; 78 operations; `--check` passes; `/{id}/export` is declared after `/{id}/crop` and before `DELETE /{id}` in `routes/captures.py`. In `test_api_openapi.py`. | 09 Tests | The route-order check |
| AC-136.17 | MCP | `EXPORT_MCP`: the schema accepts `{action, id, format}` and every optional key and refuses before fetch: an extra key, a missing `format`, `format` `"gif"`, `max_edge` 63, 16384 and 64.5, `quality` 0, 101 and 50.5, and `max_edge: null`. An extra key named `C:/private-marker/source.png` gives `validation_error` with exactly `EXPORT_UNKNOWN_KEY`, and neither the tool result nor captured stderr holds the marker; the positive control sends the same key to `crop` and finds the marker in crop's refusal, so the test can see an echo (D-620). Arguments parsed with `JSON.parse` from the text `{"action":"export","id":"cap-1","format":"jpeg","max_edge":64.0,"quality":80.0}` are accepted, and the fetch body's text holds `"max_edge":64` and `"quality":80` with no `.0`: the documented transport difference (D-610). The call goes to `POST /captures/{id}/export` with the body minus `action` and `id`, with `ADD_TIMEOUT_MS`, as AC-135.18 checks for sheet (D-616). The description carries crop's shared markers and says `NEW shot`, `never enlarges`, `jpeg and webp only`, `annotated image when it has saved marks` and `bytes`. Title `AC-136.17 capture export schema, call and description`. In `capture.test.ts`. | 09 Request, Response | The refusals; the marker key |
| AC-136.18 | MCP | Parity and audit: `ACTION_INDEX` has 75 rows with `export` directly after `sheet`; the REST body keys (`CaptureExportIn.model_fields`, read from the committed OpenAPI) equal the zod object's keys minus `action` and `id`, and the fake backend's 201 body reaches the tool result with the same keys; `BASELINE_PENDING` ends with `avkit_capture.export`; `AUDIT_PLAN` has a `capture.export` step after `capture.sheet` that depends on `capture.crop`, and the coverage test sees every action covered. Title `AC-136.18 export parity and audit coverage`. In `capture.test.ts` and `audit/coverage.test.ts`. | 09 Tests | Coverage fails if the step is missing |
| AC-136.19 | Eval | `EVAL_RUN` under D-608 A, amended by D-621: `C:/Temp/av-kit/s64-E4-check.txt` is cited as it stands (exit 1, `eval-check: failed`). Every t3 line passes on both surfaces, every meta line passes, and every real run passes its allowlist, media and answer lines. The real-t1 `image` line and the real-t2 sheet-count line fail and are recorded as evidence for `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL`, as D-608 A reads that outcome (§User Review Required). Four video runs (real-t1, real-t2, meta-t1, meta-t2) opened inbox PNGs by the paths frames and sheet returned, which the prompts allowed and the checker can't see; the handoff records it. `C:/Temp/av-kit/s64-E4-amended.txt` checks that those two are the only FAIL lines. Cited in the handoff with the per-run lines. | Grouping D-505; D-608; D-621 | Any other FAIL line stops the row (S13) |

Guards (Session 54 RULE-1, Session 55 RULE-1): `test_domain_capture.py` and `test_domain.py` (core changes), `test_capture_service.py`, `test_capture_adapter.py` and `tests/e2e/test_api_capture_crop.py` (crop shares `_crop_dest` and the adapter), `test_api_captures.py`, `test_capture_sheet_service.py` and `test_capture_frames_service.py` (they share `CAPTURE_FILE_LOCK` and `_upsert_shot`), run in rows 1 and 3. Every caller of what is extended: `_crop_dest` is called by `crop_shot` (`services/capture.py:1592`) only, which passes no `ext`; `ImageAnnotatePort` is implemented by `CaptureAdapter` and the test fakes, each of which is named in the Red rows' signature sweep.

#### Spec Sufficiency

| Behavior | Classification | Resolution |
|---|---|---|
| Request and bounds | Human-approved (design D-3) | 09 Request; D-609, D-610 |
| Source choice | Local Canon | 09 Source; D-611 |
| Size rule | Local Canon, probed | 09 Request; `EXPORT_SIZE` probe |
| Encode and metadata | Local Canon, probed | 09 Writes; D-613, D-614 (mode probe), D-619 (depth probe) |
| Write and names | Local Canon | 09 Writes, Name; D-612, D-615 |
| Source member | Local Canon | 09 Source member; D-618 |
| Response | Research-backed | 09 Response; D-618 |
| MCP shape and description | Local Canon | D-616, D-620 |
| Description eval | Human | D-608; grouping D-505 |
| UI | Local Canon | D-617: none |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/enums.py` | Modify | `CaptureSource.Export` (`EXPORT_SOURCE_MEMBER`) |
| `packages/core/src/avkit_core/ports/capture.py` | Modify | `ImageAnnotatePort.export` |
| `packages/core/src/avkit_core/services/capture.py` | Modify | `export_size`, `export_stem`, `export_shot`, `ExportResult`, `_crop_dest`'s `ext`; `EXPORT_FORMATS`, `EXPORT_SUFFIXES`, `EXPORT_STEM_TAG`, `EXPORT_STEM_FALLBACK`, `EXPORT_MAX_EDGE_MAX`, `EXPORT_EDGE_LIMIT`, `EXPORT_QUALITY_PNG`, `EXPORT_TOO_LARGE`, `EXPORT_NOT_WRITTEN`, `EXPORT_REFUSALS` (`EXPORT_SIZE`, `EXPORT_NAME`, `EXPORT_CHECKS`, `EXPORT_SOURCE`, `EXPORT_WRITE`) |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | Modify | `EXPORT_ENCODE`: `CaptureAdapter.export`, `_png_key` (D-614), `_depth_to_l` and `EXPORT_DEPTH_MODES` (D-619) |
| `packages/api/src/avkit_api/routes/captures.py`, `schemas/captures.py` | Modify | `EXPORT_ROUTE`: the route, `CaptureExportIn`, `CaptureExportShotOut`, `CaptureExportOut` |
| `openapi.committed.json` | Regenerate | The export route |
| `mcp-server/src/toolsets/capture.ts`, `registry.ts` | Modify | `EXPORT_MCP`, `EXPORT_TEXT`, `EXPORT_UNKNOWN_KEY`, the `ACTION_INDEX` row, and `export` in the `ADD_TIMEOUT_MS` selection |
| `mcp-server/scripts/audit/plan.ts` | Modify | `EXPORT_AUDIT`: the `capture.export` step |
| `tests/unit/test_capture_export_adapter.py`, `test_capture_export_service.py` | New | AC-136.2 to .12 |
| `tests/e2e/test_api_capture_export.py` | New | AC-136.13 to .15 |
| `tests/unit/test_domain_capture.py`, `test_domain.py`, `tests/e2e/test_api_captures.py` | Modify | AC-136.1; the `CaptureSource` pins |
| `tests/e2e/test_api_openapi.py`, `test_api_downloads.py`, `test_api_bodies.py` | Modify | §Pins that move; AC-136.16 |
| `mcp-server/tests/capture.test.ts`, `convert.test.ts`, `action-index.test.ts`, `m7-resource.test.ts`, `fixtures.ts`, `audit/coverage.test.ts`, `audit/runner-fake-backend.test.ts` | Modify | AC-136.17, .18; §Pins that move |
| `docs/build-plan/09-screenshot-capture.md` | Modify | §Spec text |

Every function a mechanism names is in this table and in the gate's scope (Session 61 RULE-4). `wiring.py` doesn't change: `CaptureService` already gets `annotate`. Line endings at `2832e3d` (`C:/Temp/av-kit/s64-plan-probes.txt`): every target above is CRLF except `test_api_bodies.py`, `meu-status.yaml`, `meu-registry.md` and `docs/BUILD_PLAN.md`, which are LF. Row 0 measures every file again with Python bytes into `s64-anchors.txt`, and every row writes with `newline=""` or by byte replacement; a scratch script that edits a tracked file records the file's ending, writes in it, and fails on mixed endings (Session 63 RULE-3). New files are LF.

### Project files

- `docs/execution/plans/2026-11-11-capture-export-copy/`: `implementation-plan.md`, `task.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `red-check.py`, `identity.py`, `session-gate.ps1`, `eval-run.md`, `eval-seed.py`, `eval-harness.ts`, `eval-check.py`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, and the grouping tracker row (`:104`). If another session holds any of them dirty when row 6 runs, row 6 byte-edits only MEU-136's fields and proves them with `render --check` (Session 61 RULE-5).
- `.agent/context/handoffs/2026-11-11-capture-export-copy-*.md`, `docs/execution/reflections/2026-11-11-capture-export-copy-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.

Not this session's, and never opened: `docs/proposals/2026-11-10-download-logic-divergence-report.md` (hashed only). Anything another session leaves dirty is named to Mat before any commit.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| A GUI action for export | UI | None | D-617: an export is an ordinary shot on the Capture page |
| Turning EXIF-oriented scans upright | Bug | `CAPTURE-EXIF-SCANNED-ORIENTATION`'s own session | D-613 |
| `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` | Bug | Its own session | Export doesn't scan |
| Showing per-action text to models | MCP | `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL`'s own session | D-608 measures it; nothing fixes it here |
| `MCP-AUDIT-BASELINE-PENDING-CROP` and the pending actions | Audit | The next authoritative update | D-616; `--update-baseline` needs Mat's words |
| A target byte size (`max_bytes`) | Feature | None | 09 has none; the agent exports again with a smaller edge or quality (`EXPORT_TEXT`) |
| AVIF, GIF, TIFF or other formats | Feature | None | 09 Request: png, jpeg, webp |
| `_run_with_progress`'s decoding | Bug | Raised in Session 62's handoff | Left alone unless Mat rules |
| 16-bit gray clipped by `_encode_view` (the `image` view) and `bake` | Bug | None; raised in this session's handoff for Mat | Round 1 F1's sibling: both convert `I;16` straight to 8 bits; export maps the depth itself (D-619) |
| An unknown key named in the refusal of the other strict MCP actions | MCP | None; raised in this session's handoff for Mat | D-620 fixes export only; the others answer the calling client and log nothing |
| A PNG transparency key Pillow misreads (2- and 4-bit gray, 16-bit RGB) in crop and the resized `image` view | Bug | None; raised in this session's handoff for Mat | Round 3 F5's sibling: crop writes the unscaled key into an 8-bit PNG and the view resizes with it, so those regions lose their transparency. Export corrects the gray key and removes the 16-bit RGB one (`_png_key`, D-614), so a 16-bit RGB key colour exports opaque |
| Download reliability (MEU-137 to MEU-142) | Feature | Sessions 65 on | Their own grouping |

## BUILD_PLAN.md Audit

MEU-136 is in `.agent/context/meu-status.yaml` (phase 9, band P2, matrix item 9.42, anchor `export-copy`, `pending`). Row 6 sets it `ready_for_review` with `tools/meu_status.py update`, and H2-2 sets `approved`. The render check runs at row 6 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s64-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s64-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Checks that D-608 carries Mat's ruling in §Decision Log (S14). **The ruling format:** once Mat rules, the entry's `chosen` starts with the option letter, as `"A: …"`, `"B: …"` or `"C: …"`, and its `human_message_reference` becomes `"USER_EXPLICIT <date> '<Mat's words>'"`. A `chosen` that starts `Pending Mat's ruling`, or a `null` reference, is unruled. Checks the queue (S8): MEU-135 is `approved` in `meu-status.yaml`, MEU-136 is `pending`, and `2832e3d` (`feat(capture): write a labelled grid sheet of a local video span`) is an ancestor of `HEAD`. Grouping `:92` needs only Session 59 closed; Session 63 closing is a stricter check that keeps the capture files' order (D-501).
2. Checks the shapes this plan relies on, by name: `ImageAnnotatePort` with `crop` and `sheet`, `LOSSY_QUALITY = 90`, `_CROP_KEPT_MODES`, `_CROP_ICC_CONVERT_MODES`, `_to_srgb`, `CaptureAdapter.crop`, `crop_shot`, `_crop_dest` without `ext`, `_saved_marks`, `_variant_path`, `_discard`, `_upsert_shot`, `CAPTURE_FILE_LOCK`, `TMP_SUFFIX`, `FLATTEN_PNG_SUFFIX`, `_IMPORT_STEM_DROP`, `IMPORT_STEM_MAX = 100`, `CROP_TAKEN_SUFFIXES`, `CROP_REFUSALS`, `CaptureSource.Video`, `REGION_MAX_EDGE_MIN = 64`, the crop and delete routes, `CaptureCropOut`, `CaptureSheetOut`, `SHEET_TEXT` and its description row, the sheet `ACTION_INDEX` row, the `ADD_TIMEOUT_MS` selection, `BASELINE_PENDING` ending in `avkit_capture.sheet`, the built-server count `74`, the `capture.sheet` and `capture.capture_interactive` audit steps, and AC-134.1's `members[-1] == "Video"`; and that `Export = "Export"`, `ImageAnnotatePort.export`, the `export_*`, `EXPORT_*` and `ExportResult` names, `CaptureAdapter.export`, the `/export` route, the `CaptureExport*` schemas, `z.literal("export")`, `avkit_capture.export`, `EXPORT_TEXT`, `action: "export"` and `id: "capture.export"` are absent. Planning run: every present shape found and every absent one absent (`C:/Temp/av-kit/s64-plan-shapes-probe.txt`).
3. Creates `C:\Temp\av-kit\s64\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256; the other session's proposal, if dirty, is hashed and never opened.
4. Records the line endings and SHA-256 of every file in §Files Modified to `s64-anchors.txt`, which row 1 reads before it writes, and stops when a new file already exists. Planning run: `C:/Temp/av-kit/s64-plan-anchors-probe.txt`, 0 missing, 0 present.
5. Runs `uv sync --frozen --offline --all-packages`, and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason. It asserts the pinned FFmpeg pair is over 1024 B and runs `-version` offline, and that Pillow is 13.0.0 with `MAX_IMAGE_PIXELS` 89,478,485 and WebP support, and that `segoeui.ttf` loads (S4; the eval's clips and sheets need all of them).
6. Captures the base Python suite to `s64-base-py.txt`, builds the MCP server (`s64-base-mcp-build.txt`) and captures the base MCP suite to `s64-base-mcp.txt`, and runs `ruff check packages/ tests/` to `s64-base-ruff.txt`. The suites' own failures are recorded, not fatal.
7. Runs the `red-check.py`, `identity.py` and `eval-check.py` selftests, each on its own fixture copy (Session 56 RULE-4).

The scripts are copies of Session 63's, with this plan's values:

- **`red-check.py`.** Session 63's, with `DECLARED_NEW` holding `export_stem`, `export_size`, `EXPORT_STEM_TAG`, `EXPORT_STEM_FALLBACK`, `EXPORT_FORMATS`, `EXPORT_MAX_EDGE_MAX`, `EXPORT_EDGE_LIMIT`, `EXPORT_QUALITY_PNG`, `EXPORT_TOO_LARGE`, `EXPORT_NOT_WRITTEN`, `ExportResult`, `export_shot`, `CaptureExportIn`, `CaptureExportOut`, `CaptureExportShotOut`, and the selftest fixtures' names. These excuse a non-required block only. Its boundary fixtures are AC-136.1 against AC-136.10 (pytest) and against AC-136.17 and AC-136.18 (Vitest). A red-check failure names the failing test (Session 50). Planning selftest: 44 fixtures, 0 wrong (`C:/Temp/av-kit/s64-plan-redcheck-selftest.txt`).
- **`identity.py`.** `PLAN` is this folder. Its selftest binds `session-gate.ps1`, the eval scripts, the target sources and tests, `09`, the register's renders and the grouping. Planning selftest: 0 failures (`C:/Temp/av-kit/s64-plan-identity-selftest.txt`).
- **`PROJECT_ARTIFACTS`.** This plan's `*.md` (including `eval-run.md`), the handoff, review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`. The eval scripts are `.py` and `.ts`, so they stay bound.

### 2. Type-only first, then Red, then Green (rows 1 to 3)

- **Row 1 adds the shared names with no behaviour (Session 53 RULE-2).** `CaptureSource.Export`; `ImageAnnotatePort.export`; `CaptureAdapter.export` raising `NotImplementedError`; in `services/capture.py` every `EXPORT_*` constant at its value, `ExportResult`, `export_size` returning `(1, 1)`, `export_stem` returning `""`, `export_shot` raising `NotImplementedError`, and `_crop_dest`'s `ext` (used, since crop passes none and the default is today's `.png`). The three `CaptureSource` pins move. No route, schema or MCP change. Its check runs `test_domain_capture.py`, `test_domain.py`, `test_capture_service.py`, `test_capture_adapter.py`, `test_api_captures.py`, `tests/e2e/test_api_capture_crop.py`, `ruff` and `pyright` on the touched packages. AC-136.1 passes here.
- **Each Red receipt holds an assertion failure, never a setup failure (Session 62 RULE-3).** `red-check.py` refuses a collection error, an import error, a fixture error and a required test that fails on a missing name. The Reds reach the missing behaviour through an assertion: they call row 1's stubs inside `pytest.raises`-free assertions on returned values, or post to a route that answers 404 or 405 and assert 201, so each fails on a value or status assertion. A test that patches a new name asserts the name exists first (Session 52 RULE-4).
- **`--require` matches a test name up to a non-digit boundary.** Rows 2a and 2b: `AC-136.2` to `.18`, across the pytest and Vitest receipts. AC-136.1 is a characterisation of row 1 and must pass in row 2a. AC-136.19 is the eval, not a test.
- **Expectations stay immutable in Green.** No test file changes in row 3. The count pins move in the Red rows, so they fail in the Red receipt and pass in Green.

### Description eval (rows E-1 to E-4)

After Green (row 3) and before row 6, under D-608 A or B, the coordinator follows `eval-run.md`: E-1 seeds the media and the key and records the describe output from this work tree's built server; E-2 seeds each run's root and writes each run's prompt; E-3 dispatches each run as a fresh `general-purpose` subagent with `model: haiku` and saves its final message unedited; E-4 runs `eval-check.py`. Under D-608 C the four rows are skipped and E-4 runs `eval-check.py` alone, which prints `not run under D-608 C`. Every eval file is under `C:/Temp/av-kit/s64/`, outside the repository. A failed run is S13.

### Plan-local scripts

- `baseline.ps1`, `red-check.py`, `identity.py`: §1.
- `session-gate.ps1` (H1-2): below.
- `eval-seed.py`, `eval-harness.ts`, `eval-check.py`, `eval-run.md` (rows E-1 to E-4): `EVAL_RUN`. `eval-harness.ts` runs from `mcp-server` with `npx tsx`; it reads only its root and the media, and its fake backend serves the real Python service through `uv run` in the work tree with the run's own temp inbox and database. It refuses any root outside `C:/Temp/av-kit/s64/eval/`. `identity.py` binds all three scripts.

### Session gate (H1-2)

`session-gate.ps1` is Session 63's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s64-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`. Before it runs, the coordinator lists every changed path against the gate's scope (Session 60 RULE-4).

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types` (`pyright`), `py-lint` (`ruff check packages/ tests/`), `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`), `red-check-selftest` |
| Fresh full | `py-tests`, `openapi` (`export_openapi.py --check openapi.committed.json`), `mcp-types`, `mcp-build`, `mcp-tests`, `state-render`, `issues-render`, `status-canon` (`ui/tests/unit/layout-canon.test.ts` and `queue-canon.test.ts`, which read `meu-status.yaml` and `docs/BUILD_PLAN.md` directly, and row 6 changes both) |
| Skipped with reason | `ui-types`, `ui-lint`, the rest of `ui-tests`, `ui-build` and `ui-electron` (no `ui/` file changes, D-617), `mcp-audit` (live network), `build-record` (no installer build), the package build and its smokes (no packaged surface changes), `real-ffmpeg` (no FFmpeg path changes; `py-tests` still runs the module) |

`py-tests` excuses only ids that row 0's receipt shows failing. A step that fails in a file this session didn't touch is rerun once unchanged, and both attempts' receipts are kept (Session 53 RULE-4).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`; a path outside `baseline-dirty.txt` and this plan appears; or, before rows 6 and H1-2, a `baseline-dirty.txt` path differs from its recorded SHA-256 | Stop and tell Mat; never commit, stash or revert another session's work |
| S4 | The pinned FFmpeg pair is missing or under 1024 B, `-version` fails, Pillow isn't 13.0.0, `MAX_IMAGE_PIXELS` differs, WebP is unsupported, or `segoeui.ttf` doesn't load | Stop: a fetch is a download and needs Mat's words |
| S5 | Any network request, download or upload, including the live audit | Stop and tell Mat |
| S6 | `eval-seed.py` exits 1 (one of its own checks failed), or an eval run touches a path outside its root | Stop and tell Mat with the receipt |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | At row 0, MEU-135 isn't `approved`, MEU-136 isn't `pending`, or `2832e3d` isn't an ancestor of `HEAD` | Stop; the queue is wrong |
| S9 | A count pin outside §Pins that move fails because of the new route, action or member | Add it to the row with its AC, grep its neighbours, and name it in the handoff |
| S10 | A path or Pillow's exception text reaches a log line, an error body or the console in a way it didn't before | Fix it in the row or raise it with Mat; never record it as a residual (Session 50 RULE-1) |
| S11 | A row 0 shape check fails, or a new name already exists | Stop; amend this plan through the plan review before row 1 |
| S12 | A row would change 09's rule text, an AC, or an existing route's behaviour (crop included, after `_crop_dest` gains `ext`) | Stop; brief Mat with a recommendation and a do-nothing option (Session 59 RULE-3) |
| S13 | `eval-check.py` exits 1 under D-608 A or B | Stop; brief Mat with the failing run's prompt, ledger and report, a recommendation, and the do-nothing option (record the result and keep the text); no description changes without Mat's words |
| S14 | At row 0, D-608 has no ruling from Mat in §Decision Log | Stop; ask Mat through the Human Decision Protocol |
| S15 | At row 6, `meu-status.yaml`, `meu-registry.md` or `BUILD_PLAN.md` changes any line outside MEU-136's entries and rows | Stop and tell Mat |

## Decision Log

> [!WARNING]
> Mat's request and the video stills design settle the scope, and the grouping (D-500 to D-505) placed this MEU. D-609 to D-620 didn't need Mat: each is autonomous, with its alternatives in `reasoning`. D-608 and D-621 (ruled in execution, at row E-4) are Mat's. D-600 to D-607 are claimed and D-608 up is free (`C:/Temp/av-kit/s64-plan-dids.txt`), so this block starts at D-608.
>
> Carried and not relisted in the block: every grouping §8 row, D-500 to D-505, with stage `grouping`. Of those, D-501 and D-505 bear on this session; the reflection carries all six, D-500 as human (`USER_EXPLICIT 2026-11-09 'all recommendations accepted, proceed'`) and D-501 to D-505 as autonomous, because the closeout validator reads every §8 row of the declared grouping. The design's own D-1 to D-20 are a separate namespace, cited as "design D-n" in prose only. The probe (`C:/Temp/av-kit/s64-plan-decision-probe.txt`), run with this plan and the grouping as sources (Session 54 RULE-5), shows what the closeout's decision flags pull in.

```yaml
decision_log:
  - id: D-608
    stage: planning
    question: "How does the design's three-task description eval run?"
    resolution: human
    class: two-way
    chosen: "A: six Haiku runs, the three tasks on the real surface and on the real surface plus each action's _meta text"
    source_tag: Human-approved
    precedents:
      - "grouping D-505 — the eval runs in Session 64's plan, once probe, frames, sheet and export exist"
      - "C:/Temp/av-kit/s64-plan-eval-describe.txt — the real surface describes avkit_capture in one line; per-action text is only in _meta (lines 669-685)"
      - "known issue MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL — Claude Code doesn't show _meta.action_descriptions"
      - "C:/Temp/av-kit/s64-plan-eval-check-selftest-r1d.txt — the checker's selftest, 0 wrong, with real image fixtures for t3"
    research:
      engine: none
      sources: []
    reasoning: "How an eval is run decides what its result means, and it costs model tokens outside the review loop, so it is Mat's. A tests what agents get today and, separately, whether the per-action text is right, so a failure can be put on the text or on the hidden-text issue. B halves the cost and can't tell those apart. C keeps the status quo and leaves the three tasks unproven. Haiku is the strictest cheap reader. Two-way: the rows are re-runnable."
    human_message_reference: "USER_EXPLICIT 2026-11-11 'accept the plan, D-608 A, execution budget 60M'"
  - id: D-609
    stage: planning
    question: "What happens to quality with format png?"
    resolution: autonomous
    class: two-way
    chosen: "A: refuse it with the fixed 422 'quality applies to jpeg and webp only', in the service, before the lock"
    source_tag: Local Canon
    precedents:
      - "09 :1191 — quality is 1 to 100 for jpeg and webp"
      - "crop's refusals — a request the service can't honour is refused, never silently ignored (D-476)"
    research:
      engine: none
      sources: []
    reasoning: "PNG is lossless; a quality that does nothing would let an agent think it shrank the file. Ignoring it lost because the response gives no way to say it was ignored. Mapping it to PNG compression level lost because 09 doesn't name it and level changes time, not quality. The check lives in the service so REST and MCP give the same message; zod can't see it without a refine that would differ from the API's. Two-way."
    human_message_reference: null
  - id: D-610
    stage: planning
    question: "What are the bounds and types of max_edge and quality?"
    resolution: autonomous
    class: two-way
    chosen: "A: max_edge StrictInt 64 to 16383 or absent; quality StrictInt 1 to 100 or absent; an explicit null refused; WebP past 16383 and JPEG past 65500 on the target size refused with a fixed 422; the service rechecks int-not-bool"
    source_tag: Research-backed
    precedents:
      - "09 :1191 — max_edge at least 64 and only shrinks; quality 1 to 100"
      - "C:/Temp/av-kit/s64-probe-export.txt — WebP refuses 16384 px, JPEG refuses past 65500 px on Pillow 13.0.0"
      - "Session 62 RULE-2 — magnitude bounds on every numeric input, tested at 1e308, a huge negative and just past the cap"
      - "Session 60 RULE-1 — one integer construction for max_edge"
      - "C:/Temp/av-kit/s64-plan-strict-probe.txt — zod accepts max_edge 64.0 parsed from JSON, as the number 64"
    research:
      engine: none
      sources: []
    reasoning: "64 is the region view's floor (REGION_MAX_EDGE_MIN) and 09's. A cap is needed so a huge number is a schema refusal, not arithmetic; 16383 is the smallest encoder limit, so one cap covers every format when it is used. A source larger than a format's limit with no max_edge is refused before any write, since the encoder would fail after the temp was made. Allowing up to 65500 for every format lost because a WebP request between the two would fail late. Refusing null matches MCP, where optional means absent. One difference is accepted and documented (round 1 F3): MCP arguments are JavaScript numbers, so the JSON number 64.0 is 64 before zod sees it and the call sends 64, while REST's StrictInt refuses the JSON float 64.0. Accepting 64.0 at REST lost because Pydantic's lax int would also take the string '64', and a float check of its own would differ from every other capture route. Two-way."
    human_message_reference: null
  - id: D-611
    stage: planning
    question: "What does export do with a marked shot whose bake is missing, or a malformed sidecar?"
    resolution: autonomous
    class: two-way
    chosen: "A: a shot with saved marks and no bake is the 404 'annotated image is missing' from _variant_path; a malformed sidecar is crop's 422 'sidecar is malformed'"
    source_tag: Local Canon
    precedents:
      - "09 :1192 — the source is the annotated bake when marks exist, otherwise the original"
      - "packages/core/src/avkit_core/services/capture.py:1461 — _variant_path's 404s"
      - "packages/core/src/avkit_core/services/capture.py:1647 — _saved_marks"
    research:
      engine: none
      sources: []
    reasoning: "Exporting the original when the marks exist but their bake doesn't would silently give the agent an image without the marks it asked to show. Re-baking lost because it writes the source's bake, which 09 says export doesn't change. Reusing the two existing helpers keeps one meaning for 'marked' and the same messages as image and crop. Two-way."
    human_message_reference: null
  - id: D-612
    stage: planning
    question: "How is the export's stem made?"
    resolution: autonomous
    class: two-way
    chosen: "A: the source stem through _IMPORT_STEM_DROP with '_', stripped of ' _-' and cut to 100, plus '-export'; an empty stem gives 'export'"
    source_tag: Local Canon
    precedents:
      - "09 :1194 — the stem plus -export, with the png, jpg or webp suffix, then _2 and on"
      - "packages/core/src/avkit_core/services/capture.py:229 — import_stem"
      - "Session 53 RULE-1 — lone-surrogate, control-character and empty regressions"
    research:
      engine: none
      sources: []
    reasoning: "Inbox stems come from capture, import, crop, frames, sheet and scans; a scanned file can hold any character Windows allows, including a lone surrogate from a bad decode. Replacing what import_stem would drop keeps the stem readable and safe. Reusing crop_default_stem lost because it keeps the stem's characters unfiltered. A reserved-name check isn't needed because the stem always ends in -export. Two-way."
    human_message_reference: null
  - id: D-613
    stage: planning
    question: "What metadata and orientation does an export keep?"
    resolution: autonomous
    class: two-way
    chosen: "A: keep the ICC profile; drop EXIF, XMP and text chunks; no exif_transpose, so the stored frame is kept; AC-136.7 records CAPTURE-EXIF-SCANNED-ORIENTATION's effect without fixing it"
    source_tag: Local Canon
    precedents:
      - "09 :1193 — saves no metadata"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:434-443 — crop keeps the ICC profile and drops EXIF, XMP and text (D-506 A)"
      - "known issue CAPTURE-EXIF-SCANNED-ORIENTATION — scanned files tagged 5 to 8 are sized and marked in their stored frame"
    research:
      engine: none
      sources: []
    reasoning: "A colour profile is not metadata about the shot; dropping it would shift colours on wide-gamut screenshots, and crop already keeps it. Turning the frame upright lost because the row's size, the marks and the bake are all in the stored frame, and changing that is the known issue's own plan. The test makes the effect visible to the next plan. Two-way."
    human_message_reference: null
  - id: D-614
    stage: planning
    question: "How does the adapter encode, and what are its failure texts?"
    resolution: autonomous
    class: two-way
    chosen: "A: ImageAnnotatePort.export takes source, source_size and out, then keyword-only fmt, size and quality, and returns an ImageProbe; CMYK, YCbCr and LAB through _to_srgb, keeping the sRGB profile it returns; 16-bit gray through the depth map (D-619); JPEG converted to RGB before any resize, dropping alpha and any key; for PNG and WebP, a keyed 1, L, P or RGB converted to LA or RGBA, a plain P to RGB and a plain 1 to L before a resize; a PNG key Pillow reports on another scale than its samples corrected from the IHDR by _png_key, 2- and 4-bit gray scaled and 16-bit RGB removed; LANCZOS only when shrinking; JPEG RGB, WebP RGBA when alpha else RGB, PNG keeps _CROP_KEPT_MODES with the saved image's own transparency key; quality None means LOSSY_QUALITY; fixed InboxPathError, ConflictError and OSError texts"
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:271 — _encode_view's per-format conversions"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:427 — crop's open, size check and mode handling"
      - "C:/Temp/av-kit/s64-plan-mode-probe.txt — on Pillow 13.0.0 every mode resizes and encodes to JPEG and WebP after conversion; CMYK, YCbCr, LAB, I and F can't be saved as PNG unconverted"
      - "C:/Temp/av-kit/s64-plan-depth-probe.txt — the 16-bit gray map, D-619"
      - "C:/Temp/av-kit/s64-plan-alpha-probe-r2.txt — round 2 F1: Pillow resamples LA and RGBA premultiplied, so a keyed or transparent region resized before the JPEG convert came out 0; converting first kept 128 and (200, 40, 40)"
      - "C:/Temp/av-kit/s64-plan-key8-probe-r2.txt — a keyed L or RGB converted to LA or RGBA has alpha 0 on the key and no transparency in info, and a PNG save of it holds no key"
      - "C:/Temp/av-kit/s64-plan-keynorm-probe-r3.txt — round 3 F5: a keyed 1-bit PNG of 1-px columns shrank to opaque grey (127, 127, 127, 255) by the round 2 order and to (0, 0, 0, 127) with the key converted first; with _png_key every gray depth's keyed stripes have alpha 0 and the others 255, unresized and shrunk, in PNG and WebP; a 16-bit RGB key is removed"
      - "C:/Temp/av-kit/s64-plan-key16-probe-r3.txt — Pillow 13.0.0 reports a 2- or 4-bit gray key unscaled (key 1 against samples 0, 85, 170, 255) and a 16-bit RGB key against 8-bit samples, so neither matches a pixel"
    research:
      engine: none
      sources: []
    reasoning: "One port method keeps Pillow out of core, as crop does. Resizing a palette or 1-bit image with LANCZOS resamples indices, not colours, so they are converted first. JPEG converts to RGB before resizing because Pillow resamples alpha premultiplied, and resizing first turned every fully transparent pixel black, against the rule that JPEG shows the stored colour (round 2 F1). The PNG key is read from the image being saved, not from the opened source as crop reads it, so no key is written beside an alpha band. A keyed 1 is converted like L, because converting it to L and resizing with the key attached blends keyed and unkeyed values until the key matches nothing (round 3 F5). The key is corrected from the file's IHDR because Pillow scales 2- and 4-bit gray samples but not their key, and keeps only the high byte of 16-bit RGB. Matching a 16-bit RGB key by its high bytes lost to removing it, because a high-byte match would hide opaque pixels that only share those bytes. Reading the header from the same handle keeps one open of the file. The adapter, not the service, defaults quality, so a recording test sees the exact 90 passed to save. Fixed texts keep paths out of every message (NO_RAW_OUTPUT). Encoding in memory and writing bytes lost because a large WebP would be held twice. Two-way."
    human_message_reference: null
  - id: D-615
    stage: planning
    question: "How does the copy name take a suffix other than .png?"
    resolution: autonomous
    class: two-way
    chosen: "A: _crop_dest gains a keyword ext defaulting to FLATTEN_PNG_SUFFIX; the taken rule is unchanged, so any existing x-export.* takes the stem"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:1659 — _crop_dest and CROP_TAKEN_SUFFIXES"
      - "09 :1193 — uses the crop copy pipeline (temporary file, lock, unique name, register)"
    research:
      engine: none
      sources: []
    reasoning: "The taken rule already covers .png, .jpg, .jpeg, .webp, sidecars, bakes and temps, so a JPEG never lands beside a PNG of the same stem, which would make the bake names collide. A second function lost because it would copy that rule and drift. Crop passes no ext and keeps its behaviour, which AC-136.3 checks. Two-way."
    human_message_reference: null
  - id: D-616
    stage: planning
    question: "How is export wired into MCP and the audit?"
    resolution: autonomous
    class: two-way
    chosen: "A: export after sheet in capture.ts, CAPTURE_ACTIONS and ACTION_INDEX; desc() plus EXPORT_TEXT as crop does; in the ADD_TIMEOUT_MS selection with crop, frames and sheet; avkit_capture.export joins BASELINE_PENDING last; an offline capture.export audit step after capture.sheet that depends on capture.crop"
    source_tag: Local Canon
    precedents:
      - "mcp-server/src/toolsets/capture.ts:100 — the sheet description row, crop's desc() form"
      - "mcp-server/src/toolsets/registry.ts:391-401 — the ADD_TIMEOUT_MS selection; capture, crop, frames and sheet are in it"
      - "C:/Temp/av-kit/s64-plan-cap-probe.txt — a full-size WebP at Pillow's pixel refusal edge took 82.53 s"
      - "mcp-server/tests/audit/coverage.test.ts:20-27 — BASELINE_PENDING under D-499 A terms"
      - "mcp-server/scripts/audit/plan.ts:1600 — the capture.crop step"
    research:
      engine: none
      sources: []
    reasoning: "Appending keeps every earlier adjacency pin true. A full-size WebP at Pillow's pixel refusal edge took 82.5 s on this machine (§Deadline inventory), past the 30 s default, so export takes the 120 s that crop, frames and sheet already have (round 1 Q7). Keeping 30 s lost because a large export would time out while the server still wrote it. An enforced server deadline lost because crop has none and the write is already whole or nothing. The pending list is the open known issue's mechanism; --update-baseline needs Mat's words. Using the crop step's shot keeps the audit offline and on a shot it made. Two-way."
    human_message_reference: null
  - id: D-617
    stage: planning
    question: "Does MEU-136 add a UI action or an Electron E2E?"
    resolution: autonomous
    class: two-way
    chosen: "A: no; an export is an ordinary shot on the Capture page; this corrects D-593's reasoning, which said MEU-136 adds a UI action"
    source_tag: Local Canon
    precedents:
      - "grouping :65 and :75 — Sessions 62 to 64 are service and agent layers, no Electron"
      - "09 :1185-1199 — no UI rule"
      - "D-593 (Session 63) — its reasoning named a UI action for MEU-136"
    research:
      engine: none
      sources: []
    reasoning: "Neither 09 nor the grouping asks for UI, and the design's slice S4 is an agent action. A button lost: it is new scope with its own E2E, and Mat hasn't asked for it. Recording the correction keeps D-593's text from misleading a later plan. Two-way."
    human_message_reference: null
  - id: D-618
    stage: planning
    question: "What are the source member, the response and the log line?"
    resolution: autonomous
    class: two-way
    chosen: "A: CaptureSource.Export after Video with no register wire value; 201 CaptureExportOut with shot (id, path, width, height, bytes) and source_id; log capture.export with shot_id and source_id only"
    source_tag: Research-backed
    precedents:
      - "09 :1196-1197 — the source member and the response"
      - "design §6.5 and §11 — bytes lets the agent see an export larger than its source"
      - "packages/api/src/avkit_api/schemas/captures.py:258 — CaptureCropOut's item and source_id"
    research:
      engine: none
      sources: []
    reasoning: "09 names the shape exactly. bytes comes from stat after the move, so it is the file's real size. Reusing CaptureShotOut lost because 09 asks for a small shape with bytes, which CaptureShotOut doesn't have. Logging no path keeps NO_RAW_OUTPUT. Two-way."
    human_message_reference: null
  - id: D-619
    stage: planning
    question: "How does export encode a 16-bit gray source?"
    resolution: autonomous
    class: two-way
    chosen: "A: I;16, I;16L, I;16B, I;16N and I map to L by v times 255 over 65535 rounded half up and clamped, for jpeg and webp, for I, I;16L, I;16B and I;16N, and for a PNG resized with a key; a key becomes an exact alpha for webp and a resized png and is ignored for jpeg; a PNG otherwise keeps I;16"
    source_tag: Research-backed
    precedents:
      - "round 1 F1 — a direct convert to RGB clips I;16 samples 0, 32768 and 65535 to 0, 255 and 255"
      - "round 2 F1 — building LA from the key before LANCZOS and then converting to JPEG gave 0, not 128, on the keyed block shrunk to 128 by 32; C:/Temp/av-kit/s64-plan-alpha-probe-r2.txt"
      - "C:/Temp/av-kit/s64-plan-depth-probe.txt — Pillow 13.0.0 opens 16-bit gray PNG as I;16 (and with tRNS keeps the key), 16-bit gray-and-alpha and 16-bit RGB as 8-bit; the map matches the integer formula on all 65,536 values with 0 mismatches; I;16 and LA resize; 0.012 s at 4K"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:78 — _CROP_KEPT_MODES keeps I;16 for PNG"
    research:
      engine: none
      sources: []
    reasoning: "09 says export takes the shot as it is shown and saves it in another format; clipping every midtone to white is not the shot. Scaling by 255 over 65535 keeps the full tonal range and puts 32768 at 128. Taking the high byte (v shifted right 8) lost because it rounds every value down, so 65535 and 65280 would differ from the half-up rule the plan uses for sizes. Mapping only for JPEG lost because WebP holds 8 bits too. A key is turned into an exact alpha before a resize because LANCZOS blends keyed and unkeyed values, so a key test after resizing would be wrong at every edge. JPEG has no alpha, so it ignores the key and shows the mapped value; an alpha band built for it would be resampled premultiplied and blacken the keyed block (round 2 F1). PNG keeps its 16 bits when it can, as crop does. The view and bake clip the same way; that is raised, not fixed here (Out of Scope). Two-way."
    human_message_reference: null
  - id: D-620
    stage: planning
    question: "What does export's MCP schema say about an unknown key?"
    resolution: autonomous
    class: two-way
    chosen: "A: z.strictObject with an error function that gives the fixed EXPORT_UNKNOWN_KEY for unrecognized_keys only; every other refusal keeps zod's text; the other strict actions are unchanged and raised"
    source_tag: Research-backed
    precedents:
      - "round 1 F4 — a bare .strict() names the unknown key, so a key holding a path comes back in the refusal"
      - "C:/Temp/av-kit/s64-plan-strict-probe.txt — zod 4.6.7 inside avkit_capture's union: crop and sheet echo the key today; the error function hides it and leaves the missing-format, range, fraction, enum and null refusals as they were"
      - "mcp-server/src/toolsets/registry.ts:360-365 — a validation error returns the issue messages in the tool result only"
    research:
      engine: none
      sources: []
    reasoning: "NO_RAW_OUTPUT says no new error message carries a path. A fixed text for the one issue that echoes caller text keeps that for export, and naming the allowed keys tells an agent what to send instead. Sanitizing every message in the registry lost because it changes the refusals of all 21 strict actions, which is outside this MEU and would move their tests. Leaving the echo lost because it breaks this plan's own contract for a new action. Two-way."
    human_message_reference: null
  - id: D-621
    stage: execution
    question: "Row E-4 eval-check exits 1 (S13): real-t1 makes no image call and real-t2 one sheet call where two are needed, while all six answers are right. What does AC-136.19 accept?"
    resolution: human
    class: two-way
    chosen: "A: amend AC-136.19 to cite the exit-1 receipt as it stands; every t3 and every meta line passes, every real run passes its allowlist, media and answer lines, and the two real-surface process lines are recorded as evidence for MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL; eval-check.py and the description text are unchanged"
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/s64-E4-check.txt — 43 PASS and 2 FAIL lines, eval-check: failed, exit 1"
      - "D-608 A in User Review Required — a task that fails on real and passes on meta is evidence for the open known issue, not for a wrong text"
      - "eval-check.py:387 — the checker prints eval-check: ok, so the former AC text eval-check: all runs PASS could not be met as written"
      - "an independent Opus subagent read at xhigh, consulted at Mat's request, recommended this option and the AC wording"
    research:
      engine: none
      sources: []
    reasoning: "B reruns only the two failures until they pass, one run per cell, and nothing that caused them changes. C changes description text and reaches into a known issue this plan leaves out of scope. D, the status quo, blocks MEU-136 on the frames and sheet surface of MEU-133 to MEU-135 although export (t3) passed every check on both surfaces. A keeps the failure on record where D-608 A said it belongs, and records that four video runs opened inbox PNGs by returned path, which the prompts allowed. Two-way: the eval rows can be re-run once the known issue is fixed."
    human_message_reference: "USER_EXPLICIT 2026-11-11 'A'"
```

## Research References

- `docs/build-plan/09-screenshot-capture.md:1185-1199` (the contract), `:1152-1183` (§Video sheet and its Delivered note) and §Crop to a new shot.
- `_inspiration/video-stills/design.md`: §4, §6.5, §11 and design D-3, D-11, D-12, D-20.
- The grouping file: §3 (`:73-75`), §6 tracker (`:104`), §8 (`:118-133`).
- Session 63's plan and scripts (`docs/execution/plans/2026-11-11-capture-video-sheet/`), Session 59's (`2026-11-09-capture-crop-copy/`).

## Planning receipts

- `C:/Temp/av-kit/s64-plan-probes.txt` (`C:/Temp/av-kit/s64/plan_probes.py`): `HEAD` `2832e3d3eb61960c9359a4aabab2c6bea3ad71b0`, line endings and SHA-256 of the target files, and the export absence greps over the three test trees and the target sources.
- `C:/Temp/av-kit/s64-plan-dids.txt`: the D-id and AC sweep; D-608 to D-625 and AC-136 are free; the only worktree is `main`.
- `C:/Temp/av-kit/s64-probe-export.txt` (`C:/Temp/av-kit/s64/probe_export.py`): `EXPORT_SIZE` over 3,060,000 cases, 0 mismatches, 0 growing; the named cases; the WebP and JPEG edge limits; 4K encode times and sizes.
- `C:/Temp/av-kit/s64-plan-mode-probe.txt`: Pillow 13.0.0 resize and encode per mode.
- `C:/Temp/av-kit/s64-plan-shapes-probe.txt`, `C:/Temp/av-kit/s64-plan-anchors-probe.txt`: `baseline.ps1`'s shapes and anchors steps run alone at plan time; both exit 0.
- `C:/Temp/av-kit/s64-plan-eval-describe.txt`: `eval-harness.ts describe` on `2832e3d`.
- `C:/Temp/av-kit/s64-plan-eval-harness-refuse.txt`, `…-refuse2.txt`: the harness refusing roots outside `C:/Temp/av-kit/s64/eval/`.
- `C:/Temp/av-kit/s64-plan-eval-check-selftest.txt`, `s64-plan-redcheck-selftest.txt`, `s64-plan-identity-selftest.txt`: the scripts' selftests, each 0 wrong.
- `C:/Temp/av-kit/s64-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`.
- `C:/Temp/av-kit/s64-plan-decision-probe.txt`: the decision probe, with this plan and the grouping as sources.
- `C:/Temp/av-kit/s64-plan-ruled-probe.txt`: baseline's `d608-ruled` check reads this plan as unruled (exit 1), passes ruled copies for A, B and C, and refuses a copy with letter D.
- `C:/Temp/av-kit/s64-plan-eval-check-unruled.txt`: `eval-check.py` reads this plan's D-608 as unruled and exits 1.
- Round 1 corrections:
  - `C:/Temp/av-kit/s64-plan-depth-probe.txt` (`C:/Temp/av-kit/s64/probe_depth.py`, `probe_depth2.py`): how Pillow 13.0.0 opens 16-bit PNGs, and the depth map against the integer formula on all 65,536 values (D-619).
  - `C:/Temp/av-kit/s64-plan-cap-probe.txt` (`probe_cap.py`, `probe_cap2.py`): open, encode and shrink times at Pillow's pixel refusal edge, and where the refusal starts (§Deadline inventory, D-616).
  - `C:/Temp/av-kit/s64-plan-strict-probe.txt` (`C:/Temp/av-kit/s64/probe_strict.ts`): zod's unknown-key text today and with the error function, and `64.0` (D-610, D-620).
  - `C:/Temp/av-kit/s64-plan-eval-check-selftest-r1c.txt` (3 wrong, a selftest fixture bug) and `…-r1d.txt` (0 wrong): `eval-check.py` after the F2 change.
- Round 2 corrections:
  - `C:/Temp/av-kit/s64-plan-alpha-probe-r2.txt` (`C:/Temp/av-kit/s64/probe_alpha_r2.py`): the premultiplied resize, the JPEG-first order, and keyed PNG and WebP resizes (D-614, D-619).
  - `C:/Temp/av-kit/s64-plan-key8-probe-r2.txt` (`C:/Temp/av-kit/s64/probe_key8_r2.py`): keyed 8-bit `L` and `RGB` sources converted, shrunk and saved (D-614).
- Round 3 corrections:
  - `C:/Temp/av-kit/s64-plan-key16-probe-r3.txt` (`C:/Temp/av-kit/s64/probe_key16_r3.py`): how Pillow reports a `tRNS` key for 2- and 4-bit gray and 16-bit RGB PNGs (D-614).
  - `C:/Temp/av-kit/s64-plan-keynorm-probe-r3.txt` (`C:/Temp/av-kit/s64/probe_keynorm_r3.py`): F5 reproduced and fixed, and `_png_key` on every gray depth and 16-bit RGB (D-614).
  - `C:/Temp/av-kit/s64-plan-lowbit-probe-r3.txt` (`C:/Temp/av-kit/s64/probe_lowbit_r3.py`): the first low-bit probe, exit 1, which found the unscaled 2- and 4-bit keys; its F5 reproduction used 32-px stripes, whose interiors a 2x shrink leaves pure, so it did not reproduce F5.
  - `C:/Temp/av-kit/s64-plan-webp-unresized-probe-r3.txt` (`C:/Temp/av-kit/s64/probe_webp_unresized_r3.py`): keyed 1-, 2-, 4- and 8-bit gray PNGs after `_png_key`, saved unresized through step (6) as WebP `RGBA` and PNG in its kept mode, alpha 255 and 0 at the stripe interiors (D-614).
- Not run at plan time: any suite or build.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/`, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python and MCP suites, the OpenAPI check, the MCP build and the two render checks, in the session gate.
- **Runtime:** the description eval (rows E-1 to E-4) under D-608.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, the runtime and the FFmpeg pair. The gate records it before and after, and H1-6b checks each handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
