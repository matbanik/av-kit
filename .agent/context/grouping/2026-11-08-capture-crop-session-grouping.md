# 2026-11-08 Capture crop · Session grouping

> **Source:** `_inspiration/capture-crop/design.md`, the crop design for the Capture page, written on 2026-11-08 from web research on how agents and image tools crop. Mat asked for crop "in the GUI, MCP and API so it works on screenshots or any ohter images provided. Agentic utility goes first, GUI for human is second" (design D-2), and ruled D-1: "New shot (copy); source untouched". Mat then asked: "create new session grouping and start the first create plan from it".
> **Generated:** 2026-11-08
> **Method:** Stage A (design slices S1–S5 → MEU-128–132, registered in `meu-status.yaml`, `render --check` green with 132 MEUs; build-plan homes in 09 §Residuals registered 2026-11-08; matrix rows 9.35–9.39) + Stage B (MEUs → Sessions 58–61).
> **Origin:** Agents on this machine crop screenshots with ImageMagick, mostly to look closer at part of a shot and then throw the file away (design §4). av-kit's Capture surfaces have no region view, no crop and no way to bring in an image that isn't already in the inbox.
> **Status:** Active — reversible draft, not a gate. Nothing here approves a plan or authorizes execution. Session 58's plan is reviewed separately (plan-critical-review).
> **Parallel work:** one other session is planning Session 55 `download-received-quality` in the same tree: its plan folder, its plan review handoff, and its edits to `known-issues.*`, `triage-output.yaml` and the rc.2 grouping. None of them is touched here. No other worktree exists, and no Session 58 or later, MEU-128 or later, or D-393 or later is claimed anywhere (`C:/Temp/av-kit/crop-claims.txt`).

---

## 1. MEU / scope summary

| MEU | Slug | Covers (design) | Layer | Depends on |
|-----|------|-----------------|-------|------------|
| MEU-128 | `capture-region-view` | S1: region view (§6.1, §6.2, §6.6, §6.7); D-3 to D-6 | service, API/OpenAPI, MCP | MEU-37, MEU-38, MEU-111 |
| MEU-129 | `capture-image-import` | S3: import (§6.4); D-9 | domain enum and wire, service, API/OpenAPI, MCP | MEU-36, MEU-37, MEU-38 |
| MEU-130 | `capture-crop-copy` | S2: crop to a new shot (§6.3, §6.5); D-1, D-7, D-8 | domain enum and wire, service, bake, API/OpenAPI, MCP | MEU-128, MEU-67 |
| MEU-131 | `gui-capture-crop-tool` | S4: crop tool (§7.1); D-11 | ui | MEU-130, MEU-100 |
| MEU-132 | `gui-capture-image-import` | S5: GUI import (§7.2); D-12 | ui, main process | MEU-129, MEU-39 |

Design → MEU traceability:

| Design item | Disposition |
|-------------|-------------|
| Slices S1–S5 (§10) | MEU-128 … MEU-132 above |
| §6.6 ImageMagick mapping, §6.7 draft descriptions | MEU-128 carries the `image` description and the tool documentation's mapping; MEU-129 and MEU-130 carry their own action descriptions |
| D-10 (Pillow, named fields) | no MEU; a constraint on MEU-128 to MEU-130 (no ImageMagick dependency, no geometry strings) |
| §8 data contract | MEU-129 (`CaptureSource.Import`, `CaptureImportIn`), MEU-130 (`CaptureSource.Crop`, `CaptureCropIn`, `CaptureCropOut`) |
| §9 deferred and rejected (D-13) | not registered; one row in 09 §Named deferrals |
| §11 open check: scanned JPEGs with EXIF orientation other than 1 | MEU-129's plan probes it and files an issue if marks show in the wrong place |
| §11 description eval (R-8) | MEU-130's plan, the first point where region view, import and crop all exist |

Build-plan homes: [09 §Residuals registered 2026-11-08](../../../docs/build-plan/09-screenshot-capture.md#region-view) — one anchored section per MEU with source-labelled rows, matrix rows 9.35–9.39, and the P2 band now `MEU-14–132`.

---

## 2. Dependency graph + critical path

```
MEU-37, MEU-38, MEU-111 ──► MEU-128 ──┬────────────────────── Session 58  capture-region-import
MEU-36, MEU-37, MEU-38  ──► MEU-129 ──┼────────────────────── Session 58
                                      │
        MEU-128 (+MEU-67)  ──► MEU-130 ────────────────────── Session 59  capture-crop-copy
        MEU-130 (+MEU-100) ──► MEU-131 (soft: MEU-105) ────── Session 60  gui-capture-crop-tool
        MEU-129 (+MEU-39)  ──► MEU-132 ────────────────────── Session 61  gui-capture-image-import
```

Every hard prerequisite outside the batch (MEU-36, 37, 38, 39, 67, 100, 111) is approved (`C:/Temp/av-kit/crop-dep-status.txt`). MEU-105 is pending and is a soft prerequisite of MEU-131 only (D-404).

**Critical path:** MEU-128 → MEU-130 → MEU-131. The crop reuses region view's coordinate, rounding and bounds resolver, so a crop and a region view of the same box cut the same pixels (D-401), and the GUI tool calls the crop endpoint.

**Parallel tier:** MEU-129 depends on nothing in the batch, and MEU-132 needs only MEU-129. Import and its GUI can move ahead of or behind the crop chain.

**Soft order (shared files, not dependencies):** MEU-128, MEU-129 and MEU-130 all edit `routes/captures.py`, `schemas/captures.py`, `services/capture.py`, the MCP `capture.ts` and `registry.ts`, and the OpenAPI snapshot. MEU-129 and MEU-130 both add a `CaptureSource` member and wire value.

---

## 3. Recommended grouping — 4 sessions (58–61)

### Session 58 — `capture-region-import` (MEU-128, MEU-129) · P2

- **Layer / files:** `services/capture.py` (a shared region resolver and the view render; the import copy, EXIF handling and naming), `domain/enums.py` and `domain/wire.py` (`Import`), `api/routes/captures.py` (GET image query and frame headers; POST `mode: import`), `api/schemas/captures.py` (`CaptureImportIn`), the OpenAPI snapshot, the MCP `capture.ts` (`image` region fields and the two-item content, the `import` member) and `registry.ts`; service, contract and MCP tests.
- **Why grouped:** both add agent surfaces with no GUI change, both edit the same route, schema, MCP tool and registry files and the OpenAPI snapshot, and the design runs them first and second (§10). Region view serves the most common use (design §4); import lets every later slice work on any image.
- **Order:** MEU-128 → MEU-129.
- **Cloud/local:** local (Python and MCP tests; no Electron).
- **Token estimate:** calibrate against Session 54 `convert-extract-index` (one service and API MEU) and the MEU-111 part of Session 44 `release-rc1` (the MCP image limit this MEU extends).
- **Split flag:** yes, candidate. If MEU-128's handoff passes ~50% context, run MEU-129 as 58b.

### Session 59 — `capture-crop-copy` (MEU-130) · P2

- Every agent layer: `CaptureSource.Crop`, the crop service with naming under `CAPTURE_FILE_LOCK`, the mark carry with intersection and Liang–Barsky clipping, the crop's own sidecar and bake, then the route, schema, MCP member and registry row. Reuses Session 58's resolver. Calibrate against Session 38 `capture-new-marks` and MEU-67 `capture-flatten-backup`. Split flag: candidate; the mark carry (design §6.5) can run as 59b.

### Session 60 — `gui-capture-crop-tool` (MEU-131) · P2

- Renderer only: the toolbar button, `CaptureTool` `'crop'`, the box with handles from `capture-transform.ts`, aspect presets, X/Y/W/H fields, modal keys and Save as copy through the crop endpoint. Local, with Electron proof (`ELECTRON_RUN_AS_NODE` cleared). Calibrate against Session 43 `capture-editor-repair`. The C key follows D-404. Split flag: candidate; aspect presets and the number fields can run as 60b.

### Session 61 — `gui-capture-image-import` (MEU-132) · P2

- Drop and the Import image button in the renderer; the file dialog and the Ctrl+V paste in the main process, writing to the inbox through the hotkey's publication path. Calibrate against Session 41 `gui-keyboard-palette` and MEU-39 `gui-capture`. If Session 60 is small, MEU-132 may ride with it; that is decided when Session 60 is planned.

---

## 4. Plan-creation pathway

Run `/create-plan` once per session, in order. Session 58 is planned now (Mat's instruction: "create new session grouping and start the first create plan from it"). Each plan re-reads the design sections its MEU covers (§6.x or §7.x, §8, §11) and its 09 home.

1. `/create-plan capture-region-import` → MEU-128, MEU-129
2. `/create-plan capture-crop-copy` → MEU-130
3. `/create-plan gui-capture-crop-tool` → MEU-131
4. `/create-plan gui-capture-image-import` → MEU-132

---

## 5. Prerequisite gate

- **Queue:** the crop sessions execute after rc.2 (Session 57) (D-405). Planning and plan review are not blocked, and execution of any session waits for Mat's explicit message (`plan_to_exec_gate: human`).
- **Session 59:** Session 58 has closed (MEU-128's resolver). **Session 60:** Session 59 has closed. **Session 61:** MEU-129 has closed.
- **Mark types:** MEU-130 clips every mark type on `main` when it executes. A mark type added after it (MEU-103 redact, MEU-106 line and ellipse, MEU-107 step) adds its crop rule and test in its own session (D-406).
- No open worktree; main only (no branches).

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 58 | `capture-region-import` | MEU-128, MEU-129 | P2 | executed | `docs/execution/plans/2026-11-08-capture-region-import/` |
| 59 | `capture-crop-copy` | MEU-130 | P2 | pending | `docs/execution/plans/2026-11-08-capture-crop-copy/` |
| 60 | `gui-capture-crop-tool` | MEU-131 | P2 | pending | — |
| 61 | `gui-capture-image-import` | MEU-132 | P2 | pending | — |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- Session 54 `convert-extract-index` (one service and API MEU; plan review 8,541,302 tokens, execution review 7,859,970) and the MEU-111 part of Session 44 `release-rc1` — Session 58.
- Session 38 `capture-new-marks` (mark types through every layer) and MEU-67 `capture-flatten-backup` (a new file beside the source) — Session 59.
- Session 43 `capture-editor-repair` (handles, gestures, Electron proof) — Session 60.
- Session 41 `gui-keyboard-palette` and MEU-39 `gui-capture` — Session 61.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-400 | Adopt the crop design's slices as registered MEUs and plan the first session? | human | Yes: MEU-128 to MEU-132, Session 58 planned now | Human-approved | Mat asked for the grouping and the first plan after ruling D-1. The design's other decisions keep their own tags: D-1 and D-2 are Human-approved, D-3 to D-13 are agent decisions (Research-backed or Local Canon) that a plan may revise with evidence. | USER_EXPLICIT 2026-11-08 "create new session grouping and start the first create plan from it" |
| D-401 | Slice → MEU mapping | autonomous | One MEU per slice; MEU-130 depends on MEU-128, though the design lists S2 with no dependency | Local Canon | The crop and the region view must resolve a box the same way (09 §Crop to a new shot, first row). Building the resolver once in MEU-128 and reusing it in MEU-130 avoids two copies that could drift. Two-way. | — |
| D-402 | Which slices share Session 58? | autonomous | S1 and S3 (MEU-128, MEU-129) | Local Canon | They edit the same route, schema, MCP tool, registry and OpenAPI files and are the design's first two slices. S1 with S2 lost: the mark carry is the largest piece of the batch and would push the session past half its context. Three single-MEU sessions lost: each would regenerate the same OpenAPI snapshot and registry rows. Split flag set for 58b. Two-way. | — |
| D-403 | Build-plan home and band | autonomous | 09 §Residuals registered 2026-11-08, matrix rows 9.35–9.39, band P2 | Local Canon | Earlier capture residuals live the same way in 09 (§Residuals registered 2026-10-29, rows 9.25–9.33). P2 because it is Mat's direct ask, like the must-have editor fixes of 2026-10-29 (Sessions 43 to 45 there). Two-way. | — |
| D-404 | Where does MEU-131's C key come from? | autonomous | A page-scoped shortcut registry entry; if the registry has no page-scoped letter entries yet, C arrives with MEU-105 and the button ships alone | Local Canon | Tool letters belong to MEU-105 (`gui-capture-style-tool-flow`, registry letters), which is pending. Adding one letter outside it would start the pattern MEU-105 owns. Two-way. | — |
| D-405 | Where do the crop sessions sit in the queue? | autonomous | Sessions 58–61, numbered and executed after rc.2's Session 57 | Local Canon; Research-backed | The rc.2 grouping already queued capture work behind the release sessions "because they fix no release problem and these do" (`2026-11-04-rc2-triage-residuals-session-grouping.md:242`); crop is new capability, not a fix. Release practice agrees: Zephyr allows no new features after RC1, only stabilization, bug and doc fixes (https://docs.zephyrproject.org/latest/project/release_process.html), and KiCad allows only regression fixes in its release candidate period (https://dev-docs.kicad.org/en/rules-guidelines/release-policy/index.html) (tavily, `C:/Temp/av-kit/crop-research-15-rc-freeze.md`). Crop in rc.2 lost: it delays a release whose fixes users are waiting for. Session 58 alone before rc.2 lost: it changes a public API and MCP shape late in a candidate. Two-way: one message from Mat moves it, and planning proceeds either way. | — |
| D-406 | How do crop and the mark types still pending (MEU-103, MEU-106, MEU-107) meet? | autonomous | MEU-130 clips every mark type on `main` when it executes; a mark type added later adds its own crop rule and test | Local Canon | The two groups share no renderer file before Session 60, so neither needs to wait for the other; the only coupling is that a crop must carry every mark type. Putting the rule on whichever lands second keeps both orders safe. Two-way. | — |

Carry-forward: each row appears in its consuming session's reflection `### Decisions Log` with stage `grouping`. The closeout validator reads every §8 row of the declared grouping, so a session's reflection lists them all; the lines below say which rows bear on that session.

- Session 58 carries D-400, D-401, D-402, D-403 and D-405.
- Session 59 carries D-401 and D-406.
- Session 60 carries D-404.
- Session 61 carries D-400.
