# 2026-11-09 Video stills · Session grouping

> **Source:** `_inspiration/video-stills/design.md`, the video stills design written on 2026-11-09 from web research on how agents take frames from video and from the image work agents already do on this machine. Mat asked whether an agent can "grab screenshots from video" through av-kit, "for review of meeting vidoes or footage from security cameras", asked for a design that is "lighweight and with specific purpose in mind rather than going after all bells and wisels", and then ruled all five human decisions: "all recommendations accepted, proceed".
> **Generated:** 2026-11-09
> **Method:** Stage A (design slices S1–S4 → MEU-133–136, registered in `meu-status.yaml`, `render --check` green with 136 MEUs (`C:/Temp/av-kit/stills-render-check.txt`); build-plan homes in 08 §Media probe (residual) and 09 §Residuals registered 2026-11-09; matrix rows 8.10 and 9.40–9.42) + Stage B (MEUs → Sessions 62–64).
> **Origin:** av-kit bundles ffmpeg, but no tool takes a still from a video. Agents here run ffmpeg directly and build contact sheets by hand with Pillow (design §4, L-13, L-14), and an agent without a shell can't do it at all.
> **Status:** Active — reversible draft, not a gate. Nothing here approves a plan or authorizes execution. Each session's plan is reviewed separately (plan-critical-review).
> **Parallel work:** another session is writing the rc.3 release record in the same tree (`docs/releases/v0.1.0-rc.3.md`, `docs/releases/v0.1.0-rc.3-build-record.json`). Neither is touched here. Only the `main` worktree exists (`C:/Temp/av-kit/stills-worktrees.txt`). The highest decision id in use is D-499 (Session 59's plan), and no Session 62 or later, MEU-133 or later, or D-500 or later is claimed anywhere (`C:/Temp/av-kit/stills-claims-3.txt`).

---

## 1. MEU / scope summary

| MEU | Slug | Covers (design) | Layer | Depends on |
|-----|------|-----------------|-------|------------|
| MEU-133 | `convert-media-probe` | S1: probe (§6.2); D-6 | API/OpenAPI, MCP (`avkit_convert`) | MEU-31, MEU-32 |
| MEU-134 | `capture-video-frames` | S2: frames (§6.1, §6.3, §6.6); D-1, D-4, D-7 to D-12, D-15 to D-17, D-19 | port and adapter (`FramePort`), domain enum, service, API/OpenAPI, MCP | MEU-133, MEU-129, MEU-130 |
| MEU-135 | `capture-video-sheet` | S3: sheet (§6.4); D-4, D-13, D-14 | service (Pillow grid and labels), API/OpenAPI, MCP | MEU-134 |
| MEU-136 | `capture-export-copy` | S4: export (§6.5); D-3, D-20 | domain enum, service, API/OpenAPI, MCP | MEU-130 |

Design → MEU traceability:

| Design item | Disposition |
|-------------|-------------|
| Slices S1–S4 (§10) | MEU-133 … MEU-136 above |
| §6.1 times | MEU-134 builds the parser and the `time_ms`/`timecode` echo; MEU-135 reuses it |
| §6.6 descriptions | each MEU carries its own action description; MEU-134 adds the video Prerequisite markers that MEU-135 reuses |
| §7 GUI (D-5: none) | no MEU; the outputs are shots on the existing Capture page |
| §8 data contract | MEU-134 (`CaptureSource.Video`, frame names, write pattern, errors), MEU-135 (sheet name), MEU-136 (`CaptureSource.Export`, export name) |
| §9 deferred and rejected (D-2, D-5, D-18) | not registered; one new row in 09 §Named deferrals, and notes on the rows the design reopens in part (`:1091`, `:1092` by D-1; `:1097` by D-3) |
| §11 planning probes: seek accuracy, 20 frames of 4K HEVC, raw camera streams with no duration | MEU-134's plan (D-504) |
| §11 planning probe: a 5×5 sheet of 4K HEVC | MEU-135's plan (D-504) |
| §11 description eval (three tasks) | MEU-136's plan, the first point where probe, frames, sheet and export all exist (D-505) |

Build-plan homes: [08 §Media probe (residual)](../../../docs/build-plan/08-video-conversion.md#media-probe-residual) and [09 §Residuals registered 2026-11-09](../../../docs/build-plan/09-screenshot-capture.md#video-frames) — one anchored section per MEU with source-labelled rows, matrix rows 8.10 and 9.40–9.42, and the P2 band now `MEU-14–136`.

---

## 2. Dependency graph + critical path

```
MEU-31, MEU-32 ──► MEU-133 ──┐
                             ├─► MEU-134 ──► MEU-135 ──── Session 62 (133, 134) · Session 63 (135)
MEU-129 ─────────────────────┤
MEU-130 (Session 59) ────────┴─► MEU-136 ─────────────── Session 64 (136)
```

Every prerequisite outside the batch is approved except MEU-130, which is pending (Session 59 `capture-crop-copy`, planned; D-490 to D-499 are its plan's). MEU-31, MEU-32 and MEU-129 are approved.

**Critical path:** MEU-130 → MEU-134 → MEU-135. Frames must land after crop because AC-130.7 asserts `Crop` is the last `CaptureSource` member and both edit the same capture files (D-501).

**Parallel tier:** MEU-133 depends on nothing pending and could run before Session 59 closes. MEU-136 needs only MEU-130 and could run before Session 62.

**Soft order (shared files, not dependencies):** MEU-134, MEU-135 and MEU-136 all edit `services/capture.py`, `api/routes/captures.py`, `api/schemas/captures.py`, the MCP `capture.ts` and `registry.ts`, and the OpenAPI snapshot. MEU-134 and MEU-136 each add a `CaptureSource` member; whichever lands second moves the last-member assertion. MEU-133 edits the convert files instead (`routes/conversions.py`, `schemas/conversions.py`, `convert.ts`) and shares only the OpenAPI snapshot and `registry.ts`. None of the batch shares a file with Sessions 60 and 61, which are renderer and main-process work.

---

## 3. Recommended grouping — 3 sessions (62–64)

### Session 62 — `video-probe-frames` (MEU-133, MEU-134) · P2

- **Layer / files:** convert side: `api/routes/conversions.py` and `api/schemas/conversions.py` (`POST /conversions/probe`), the MCP `convert.ts` `probe` member. Capture side: a `FramePort` protocol in core (`probe`, `grab_frame`) implemented by the existing `FFmpegAdapter` instance in `media/adapter.py`; `domain/enums.py` (`CaptureSource.Video`); `services/capture.py` (time parsing, midpoint spacing, past-the-end checks, the `.avkit-tmp` → `os.replace` → register write under `CAPTURE_FILE_LOCK`, frame names); `api/routes/captures.py` and `api/schemas/captures.py` (`POST /captures/frames`, two request shapes); the MCP `capture.ts` `frames` member and `registry.ts`; the OpenAPI snapshot. Real-ffmpeg integration tests on generated clips (a `testsrc2` counter clip, a VFR clip, one with no duration), deselected on CI as Session 54's are.
- **Why grouped:** probe is small (one read-only route and one MCP member over the existing `MediaPort.probe`), and frames uses the same probe result for every time check. Agents call them in that order (design §6.6). One OpenAPI and registry regeneration covers both. Probe alone would pay a full plan and review cycle for one route.
- **Order:** MEU-133 → MEU-134.
- **Cloud/local:** local (real ffmpeg from `packaging/ffmpeg-win64/`; no Electron).
- **Token estimate:** calibrate against Session 54 `convert-extract-index` (convert route, real-ffmpeg tests) and Session 58 `capture-region-import` (two capture MEUs, a new `CaptureSource` member, the import write pattern).
- **Split flag:** yes, candidate. If Session 59 has not closed when this session is planned, MEU-133 runs alone as 62a and MEU-134 waits as 62b. If MEU-133's handoff passes ~50% context, MEU-134 runs as 62b.

### Session 63 — `capture-video-sheet` (MEU-135) · P2

- Service and agent layers: cell times from the frames spacing, ffmpeg grabs at cell size through `FramePort`, Pillow tiling, outlined labels in the annotate font (`_load_font`), the size and token budget, `POST /captures/sheet`, the MCP `sheet` member and registry row, OpenAPI. The plan runs the 5×5 4K HEVC timing probe first. Calibrate against Session 58 (the region view's Pillow render and size maths) and Session 38 `capture-new-marks` (Pillow drawing through every layer). If the plan comes out small, MEU-136 may ride with it; that is decided when Session 63 is planned.

### Session 64 — `capture-export-copy` (MEU-136) · P2

- Service and agent layers: `CaptureSource.Export`, the export through Session 59's copy pipeline (the bake when marks exist, `max_edge` that only shrinks, `png`/`jpeg`/`webp` with `LOSSY_QUALITY`, no metadata), `POST /captures/{id}/export`, the MCP `export` member and registry row, OpenAPI. The plan also runs the design's three-task description eval (D-505). Calibrate against Session 59 `capture-crop-copy` (the copy pipeline it reuses) and MEU-67 `capture-flatten-backup` (a new file beside the source).

---

## 4. Plan-creation pathway

Run `/create-plan` once per session, in order, on Mat's word. Nothing is planned now: Mat asked for the grouping ("After that we will aim to do session grouping from the design"), not a plan. Each plan re-reads the design sections its MEU covers (§6.x, §8, §11) and its 08 or 09 home.

1. `/create-plan video-probe-frames` → MEU-133, MEU-134
2. `/create-plan capture-video-sheet` → MEU-135
3. `/create-plan capture-export-copy` → MEU-136

---

## 5. Prerequisite gate

- **Queue:** Sessions 62–64 are new capability, so they execute after Session 59 and after the rc.3 release closes (D-503). Planning and plan review are not blocked, and execution of any session waits for Mat's explicit message (`plan_to_exec_gate: human`).
- **Session 62:** Session 59 has closed (MEU-130), unless MEU-133 runs alone as 62a. **Session 63:** Session 62 has closed. **Session 64:** Session 59 has closed; it does not wait for 62 or 63.
- **Caps:** if a planning probe shows 20 frames or a 5×5 sheet near the MCP request timeout, the plan lowers the cap (design D-4 allows it), records the measured time and names the change in its human gate. It does not add a queue.
- No open worktree; main only (no branches).

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 62 | `video-probe-frames` | MEU-133, MEU-134 | P2 | executed | `docs/execution/plans/2026-11-10-video-probe-frames/` |
| 63 | `capture-video-sheet` | MEU-135 | P2 | executed | `docs/execution/plans/2026-11-11-capture-video-sheet/` |
| 64 | `capture-export-copy` | MEU-136 | P2 | pending | — |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- Session 54 `convert-extract-index` (one convert service and API MEU with real-ffmpeg tests; plan review 8,541,302 tokens, execution review 7,859,970) and Session 58 `capture-region-import` (two capture MEUs, a new source member, the import write pattern) — Session 62.
- Session 58 (Pillow view render and size maths) and Session 38 `capture-new-marks` (Pillow drawing through every layer) — Session 63.
- Session 59 `capture-crop-copy` (the copy pipeline, once it executes) and MEU-67 `capture-flatten-backup` (a new file beside the source) — Session 64.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-500 | Adopt the video stills design's slices as registered MEUs and group them? | human | Yes: MEU-133 to MEU-136, Sessions 62–64; no plan created yet | Human-approved | Mat ruled design D-1 to D-5 as recommended and said "proceed" to the grouping step named in the design request. The design's other decisions keep their own tags: D-6 to D-20 are agent decisions (Research-backed or Local Canon) that a plan may revise with evidence. | USER_EXPLICIT 2026-11-09 "all recommendations accepted, proceed" |
| D-501 | Slice → MEU mapping and dependencies | autonomous | One MEU per slice. MEU-134 depends on MEU-130, though the design lists S2 with no MEU dependency; MEU-136 depends on MEU-130 for the copy pipeline | Local Canon | AC-130.7 asserts `Crop` is the last `CaptureSource` member, and MEU-130 edits the same capture service, route, schema and MCP files, so frames built before crop lands would collide in every one of them. MEU-136 reuses MEU-130's temporary-file, lock, unique-name and register pipeline (design §6.5). Making MEU-134 soft lost: Session 59 is already planned, and waiting for it costs nothing while the other order costs a rebase of a planned session. Two-way. | — |
| D-502 | Which slices share a session? | autonomous | S1 and S2 (MEU-133, MEU-134) in Session 62; S3 and S4 alone, with the option to merge S4 into Session 63 at plan time | Local Canon | Probe is one read-only route over `MediaPort.probe` and is too small to carry a plan and review cycle alone; frames reads the same probe result. S2 with S3 lost: frames is the largest slice (port, adapter, times, two request shapes, real-ffmpeg fixtures, two planning probes) and the sheet would push the session past half its context. One session for all four lost for the same reason. Split flag set for 62a/62b. Two-way. | — |
| D-503 | Build-plan homes, band and queue position | autonomous | MEU-133 in 08 §Media probe (residual), row 8.10; MEU-134–136 in 09 §Residuals registered 2026-11-09, rows 9.40–9.42; band P2; Sessions 62–64 executed after Session 59 and after the rc.3 release closes | Local Canon | Probe is a `/conversions` route and an `avkit_convert` member (design D-6), so it lives with the convert residuals; the rest are capture actions (design D-1) and follow the crop residuals in 09. P2 because it is Mat's direct ask, as crop was (crop grouping D-403). The queue follows crop grouping D-405: release candidates take fixes, not new capability. Running before Session 59 lost (D-501). Two-way: one message from Mat moves it, and planning proceeds either way. | — |
| D-504 | Where do the design's planning probes run? | autonomous | Session 62's plan runs seek accuracy, the 20-frame 4K HEVC timing and the raw-stream (no duration) check; Session 63's plan runs the 5×5 sheet timing. A plan may lower a cap from its measurement and names the change in its human gate | Local Canon | Each probe decides a constant or a description line in the MEU that owns it (design §11), so it must run before that MEU's code is written. Design D-4's reversibility note already allows lowering `FRAMES_MAX` from the probe; naming it at the human gate keeps a governance number from changing without Mat seeing it. Running all probes now lost: they need the `FramePort` code path and fixtures the plan writes. Two-way. | — |
| D-505 | Where does the design's description eval run? | autonomous | Session 64's plan, after probe, frames, sheet and export all exist | Local Canon | The eval's three tasks use every new action, and the third (shrink a 4K screenshot under 500 KB) needs export. Crop put its eval at the first point where all its actions existed (crop grouping §1); this follows that. If Session 64 is merged into 63 (D-502), the eval moves with it. Two-way. | — |

Carry-forward: each row appears in its consuming session's reflection `### Decisions Log` with stage `grouping`. The closeout validator reads every §8 row of the declared grouping, so a session's reflection lists them all; the lines below say which rows bear on that session.

- Session 62 carries D-500, D-501, D-502, D-503 and D-504.
- Session 63 carries D-502 and D-504.
- Session 64 carries D-501 and D-505.
