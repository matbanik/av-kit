# 2026-10-29 Capture annotation editor · Session grouping

> **Source:** `_inspiration/capture-annotation-tools/synthesis.md`, the synthesis of three deep-research reports (GPT, Gemini, Claude) on how open-source annotation tools handle the editor features users reported missing on the Capture page. On 2026-10-29 Mat accepted every recommendation (C-1 to C-14) and the three decisions (D-1 revise D-136, D-2 Lock on by default, D-3 "Smart eraser"): "all recommendations are accepted, continue with create-plan and execution upon review approval."
> **Generated:** 2026-10-29
> **Method:** Stage A (synthesis slices → MEU-99–107, registered in `meu-status.yaml`, `render --check` green; build-plan homes in 09 §Residuals registered 2026-10-29; matrix rows 9.25–9.33) + Stage B (MEUs → Sessions 43–48).
> **Origin:** Mat reported that box, pixelate, eraser and text marks cannot be resized once drawn. The cause is not a regression: MEU-60 deferred resize handles (09 :390, Human-approved 2026-09-20). The synthesis widened the question to the whole editor.
> **Status:** Active — reversible draft, not a gate. Nothing here approves a plan or authorizes execution. Session 43's plan is reviewed separately (plan-critical-review).
> **Parallel work:** none. The 2026-10-17 grouping (Sessions 40–42) is fully approved.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (synthesis) | Layer | Depends on |
|-----|------|--------------------|-------|------------|
| MEU-99 | `gui-capture-history-chords` | slice 1: M-1, A-3, D-1, G-2 | ui (CapturePage keydown, Undo/Redo hints, help) | MEU-60, MEU-97 |
| MEU-100 | `gui-capture-resize-handles` | slice 2: M-2, A-1, C-11 | ui (new `capture-transform.ts`, hit-test, CaptureViewport handles) | MEU-60, MEU-91 |
| MEU-101 | `gui-capture-text-reedit` | slice 3a: M-3, A-2, A-6, C-3 | ui (TextDraft, text plate handles) | MEU-82, MEU-100 |
| MEU-102 | `capture-text-multiline` | slice 3b: A-7, G-3 | domain + infra bake + ui metrics | MEU-101 |
| MEU-103 | `capture-redact-mark` | slice 4: M-5, A-5, A-11, A-16, C-1, C-2, C-10, D-3 | domain, bake, API/OpenAPI, MCP, ui | MEU-91, MEU-100 |
| MEU-104 | `capture-copy-image-actions` | slice 5: M-4, A-4, A-15, C-5, C-14, B-1, G-6(a) | API render endpoint, ui clipboard and labels | MEU-81, MEU-99 |
| MEU-105 | `gui-capture-style-tool-flow` | slice 6: A-8, A-9, A-10, A-12, A-13, B-12, C-4, C-6, C-12, D-2 | ui (toolbar, preferences, registry letters) | MEU-87, MEU-99, MEU-100 |
| MEU-106 | `capture-line-ellipse-shapes` | slice 7: A-14, B-7, C-13 | domain, bake, schemas, ui | MEU-100, MEU-105 |
| MEU-107 | `capture-step-mark` | slice 8: C-8 | domain, bake, schemas, ui | MEU-105 |

Synthesis → MEU traceability:

| Synthesis item | Disposition |
|----------------|-------------|
| Slices 1–8 (3 split into 3a and 3b) | MEU-99 … MEU-107 above |
| Band A "keep what already works" (A-17), non-goals (A-18) | no MEU; constraints on every slice |
| Parity risks (A-19) | ACs inside MEU-102, MEU-103, MEU-106, MEU-107 (preview/bake fixtures) |
| Later items (wrap width, bold, align, highlight blend, freehand `path`) | not registered; the synthesis names their triggers |
| G-2 (menu re-routing vs text fields) | answered in Session 43 planning: no menu change needed (§8 D-163) |
| G-3 (`\n` in preview and bake today) | MEU-102's plan settles it first |
| G-5 (pixelate block size after resize) | answered: the domain has no block ≤ area rule, so resize keeps `block_size` |
| G-6 (Copy image source) | option (a), a render endpoint, in MEU-104 |

Build-plan homes: [09 §Residuals registered 2026-10-29](../../../docs/build-plan/09-screenshot-capture.md#canvas-history-chords) — one anchored section per MEU with source-labelled rows. The MEU-60 row "No resize handles in this MEU" gains a pointer to MEU-100, and the named deferral of circles and numbered callouts now names MEU-106 and MEU-107.

---

## 2. Dependency graph + critical path

```
MEU-60, MEU-97 ──► MEU-99 ─────┬──────────────────────────── Session 43  capture-editor-repair
MEU-60, MEU-91 ──► MEU-100 ─┬──┼──► MEU-101 (+MEU-82) ─────── Session 43
                            │  │
                            │  └──► MEU-104 (+MEU-81) ─────── Session 45  capture-copy-image
                            ├─────► MEU-103 ───────────────── Session 44  capture-redact
                            │       MEU-101 ──► MEU-102 ───── Session 46  capture-text-multiline
                            └─────► MEU-105 (+MEU-87, 99) ─── Session 47  capture-style-tool-flow
                                    MEU-105 ──► MEU-106, MEU-107 ── Session 48  capture-shapes-steps
```

All prerequisites outside the batch (MEU-60, 81, 82, 87, 91, 97) are approved.

**Critical path:** MEU-100 → MEU-105 → MEU-106. The transform module is the base every bounded mark reuses; the style flow owns the per-tool defaults the new shapes inherit.

**Soft order (shared files, not dependencies):** MEU-99 before MEU-100 and MEU-101 inside Session 43, because all three edit `CapturePage.tsx`'s key handler and the help body.

---

## 3. Recommended grouping — 6 sessions (43–48)

### Session 43 — `capture-editor-repair` (MEU-99, MEU-100, MEU-101) · P2

- **Layer / files:** `CapturePage.tsx`, `CaptureViewport.tsx`, `capture-hit-test.ts`, new `capture-transform.ts`, `capture-help-content.ts`, a comment in `registry/shortcuts.ts`; unit, behaviour and Electron capture tests.
- **Why grouped:** the three MVP-must items users feel as "broken" (no Ctrl+Z, no resize, no text re-edit), all renderer-only with no model, API or MCP change. They share the key handler, the gesture state machine and the help text.
- **Order:** MEU-99 → MEU-100 → MEU-101.
- **Cloud/local:** local (Electron E2E, `ELECTRON_RUN_AS_NODE` cleared).
- **Token estimate:** calibrate against Session 41 `gui-keyboard-palette` (three GUI MEUs) and Session 38 `capture-new-marks`.
- **Split flag:** yes, candidate. If the MEU-100 handoff passes ~50% context, run MEU-101 as 43b.

### Session 44 — `capture-redact` (MEU-103) · P2

- Every layer: the `redact` type in domain, bake, OpenAPI and MCP schemas, then the GUI tool. MVP-must because a pixelated secret fails silently. Calibrate against Session 38 `capture-new-marks`.

### Session 45 — `capture-copy-image` (MEU-104) · P2

- A render endpoint plus the GUI clipboard and label changes. MVP-must. Calibrate against Session 34 `capture-chrome`.

### Session 46 — `capture-text-multiline` (MEU-102) · P3

- Domain text semantics, Segoe metrics and bake fixtures. G-3 first; if `\n` already bakes as lines, it is partly a parity fix and may move ahead of Session 45.

### Session 47 — `capture-style-tool-flow` (MEU-105) · P3

- Toolbar, preferences and registry letters. Split flag: candidate (six behaviours).

### Session 48 — `capture-shapes-steps` (MEU-106, MEU-107) · P3

- Two model additions through every layer. Split flag: yes, candidate; MEU-107 can run as 48b.

---

## 4. Plan-creation pathway

Run `/create-plan` once per session, in order. Session 43 is planned now (Mat's instruction: plan, review, and execute on approval).

1. `/create-plan capture-editor-repair` → MEU-99, MEU-100, MEU-101
2. `/create-plan capture-redact` → MEU-103
3. `/create-plan capture-copy-image` → MEU-104
4. `/create-plan capture-text-multiline` → MEU-102
5. `/create-plan capture-style-tool-flow` → MEU-105
6. `/create-plan capture-shapes-steps` → MEU-106, MEU-107

---

## 5. Prerequisite gate

- No open worktree or session touches the capture files. Main only (no branches).
- Each later session re-reads the synthesis band entries its MEU covers before planning.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 43 | `capture-editor-repair` | MEU-99, MEU-100, MEU-101 | P2 | approved | `docs/execution/plans/2026-10-29-capture-editor-repair/` |
| 44 | `capture-redact` | MEU-103 | P2 | executed | `docs/execution/plans/2026-11-13-capture-redact/` |
| 45 | `capture-copy-image` | MEU-104 | P2 | executed (Session 69) | `docs/execution/plans/2026-11-13-capture-copy-image/` |
| 46 | `capture-text-multiline` | MEU-102 | P3 | pending | — |
| 47 | `capture-style-tool-flow` | MEU-105 | P3 | pending | — |
| 48 | `capture-shapes-steps` | MEU-106, MEU-107 | P3 | pending | — |

---

## 7. Token calibration sources

- Session 41 `gui-keyboard-palette` (three GUI MEUs, registry chords) and Session 38 `capture-new-marks` (MEU-90/91) — Session 43.
- Session 38 — Sessions 44 and 48. Session 34 `capture-chrome` — Session 45.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-158 | Adopt the synthesis's slices and recommendations as registered MEUs? | human | Yes: every recommendation (C-1 to C-14) and D-1 to D-3 | Human-approved | Mat accepted them all. The slices are about one session each, with dependencies already stated. | USER_EXPLICIT 2026-10-29 "all recommendations are accepted" |
| D-159 | Slice → MEU mapping | autonomous | One MEU per slice, with slice 3 split into MEU-101 (3a) and MEU-102 (3b) as the synthesis already splits it | Local Canon | 3a has no model change and 3b needs G-3 settled first; joining them would hold the re-edit fix behind a parity investigation. Two-way. | — |
| D-160 | Run slices 1, 2 and 3a as one session? | autonomous | Yes, Session 43 | Local Canon | All three are renderer-only, share `CapturePage.tsx`'s key handler and gesture code, and are what users feel as broken. Three plans would rewrite the same handler and help body three times. Split flag set for 43b. Two-way. | — |

Carry-forward: Session 43's reflection `### Decisions Log` carries D-158 to D-160 with stage `grouping`. Later sessions carry D-158 and their own D-159 row.

---

## 9. Planning notes added 2026-11-12

Written after the crop sessions (58 to 61), the video-stills sessions (62 to 64) and the download sessions (65 to 67) landed on `main`. None of the five pending sessions has started and no capture file carries their features; the re-check of 2026-11-12 found no duplicated work and the conflicts below. Each plan re-reads this section, the synthesis entries its MEU covers (§5), and the crop grouping's D-404 and D-406 (`2026-11-08-capture-crop-session-grouping.md`).

### 9.1 Session numbers

The §6 table still names Sessions 44 to 48. Session 44 became `release-rc1` and 45 to 67 are taken (rc2 grouping D-240). The five sessions run as Sessions 68 to 72 in the §4 order: 68 `capture-redact`, 69 `capture-copy-image`, 70 `capture-text-multiline`, 71 `capture-style-tool-flow`, 72 `capture-shapes-steps` (D-674). The §6 rows keep their text so D-240's observation stays readable; the plan folders carry the slugs.

Row 44 (`capture-redact`, MEU-103) ran as Session 68 on 2026-11-13; its plan folder is `docs/execution/plans/2026-11-13-capture-redact/`.

### 9.2 Crop rules for new and changed marks (crop grouping D-406)

`clip_mark` in `packages/core/src/avkit_core/domain/capture.py` is an exhaustive `match` that ends in `assert_never`, so a new Annotation class fails the type check until it has a crop rule. MEU-106 adds fields to existing classes, so it compiles unchanged, but the rule it inherits must be the one wanted. The rules each plan carries (D-675, D-676):

| MEU | Mark | Crop rule | Test |
|-----|------|-----------|------|
| MEU-103 | `redact` | MARK_CLIP_BOX, the half-open rule pixelate uses (`_clip_half_open`; the `_HalfOpenMark` TypeVar gains the class) | straddling clipped, outside dropped, inside kept, zero-size kept while its origin is inside |
| MEU-106 | `arrow.head` | No new rule: `_clip_arrow` carries the field through `replace`. A clipped `both` arrow keeps a head at the crop edge, as every clipped `end` arrow does today (D-487) | the existing arrow cases run once per `head` value |
| MEU-106 | `rect.shape = "ellipse"` | MARK_CLIP_ELLIPSE (D-676 A): kept when its box lies inside the closed `[0, width] x [0, height]`, otherwise dropped, never clipped; `_clip_rect` is not inherited | inside kept, straddling dropped, outside dropped, with the box exactly on the edge kept |
| MEU-107 | `step` | MARK_CLIP_TEXT's anchor rule: kept when `(x, y)` is in `[0, width) x [0, height)`, else dropped, never clipped | mirrors the text cases |

### 9.3 Letters and chords

- MEU-105's Letters row gains **C Crop** (crop grouping D-404, D-508). The Crop button has shipped without its letter since Session 60; the plan registers C beside the other letters and the crop-tool hint shows it.
- X serves Redact (MEU-105) and the crop bar's aspect swap (MEU-131). This holds only because the page ignores tool letters while the crop is open (CROP_MODAL). The MEU-105 plan keeps the X case in `ui/tests/unit/capture-crop-tool.behavior.test.ts` green and adds its inverse: X with the crop closed arms Redact.
- Ctrl+D (Duplicate, MEU-106) is not in RESERVED_CHORDS (`ui/src/renderer/src/registry/shortcuts.ts`). The plan takes it as a page-scoped registry entry; if the registry refuses a Ctrl chord, it adds Ctrl+D to the reserved set and handles it on the page.
- Ctrl+C (MEU-104) stays in RESERVED_CHORDS and reaches the canvas the way Session 61's Ctrl+V does (D-678): the page key handler, with `isEditableTarget` (PASTE_KEY, `capture-import.ts`) leaving a text field its native copy, and no registry entry.
- Shift+arrow nudge and Shift aspect (MEU-105 Modifiers) reuse the crop tool's constants, `FIELD_STEP_SHIFT` in `CaptureCropBar.tsx` and `CROP_RATIO` in `capture-crop.ts`, not new numbers. The Pixelate block-size scrub is still owed: the control is a plain number input in `CaptureViewport.tsx`.

### 9.4 Copy image (MEU-104)

The filmstrip already has a "Copy image" item (MEU-88, Session 38): `loadClipboardPng` in `capture-clipboard.ts` fetches `GET /captures/{id}/image?variant=original` and `writeClipboardImage` puts it on the clipboard, so a shot with saved marks is copied without them. MEU-104's button and Ctrl+C copy the image with unsaved marks through `POST /captures/{id}/render`. By D-677 A the filmstrip item fetches `variant=annotated` when the shot has saved marks and `original` otherwise, MEU-136's as-shown rule, so every "Copy image" means the image as you see it. The render route encodes in memory as MEU-128's region view does and bakes through the path MEU-136's export uses; it adds no third encoder.

### 9.5 Every layer a mark type touches

A new type (`redact`, `step`) or field (`head`, `shape`) lands in one session across: the Annotation union and the sidecar, the bake and its parity fixtures (MEU-102 Parity row), MEU-130's crop (§9.2), MEU-136's export (it bakes saved marks), the OpenAPI document, the MCP annotate zod union in `mcp-server/src/toolsets/capture.ts` with `mcp-server/tests/audit/baseline.test.ts`, the hit test and handles, and the help body. An older server rejects the unknown type (MEU-103 Mark row), so the MCP schema and the service land together.

### 9.6 Renames

"Smart eraser" (MEU-103) and "Save annotations" / "Flatten into image…" / "Restore backup…" (MEU-104) change `capture-toolbar.ts`, `capture-help-content.ts`, the `docs/build-plan/gui-actions-index.md` rows (`capture:tool_eraser`, `capture:apply_image`, `capture:revert_image`, `capture:copy_image`), the Electron settings and capture tests, and possibly `test-ids.ts`, whose byte hash AC-51.6 guards: a plan that touches it runs `ui/tests/unit/capture-action-row.test.ts` as its own check and names the new hash in the row.

### 9.7 Ordering and housekeeping

- The rc2 grouping's hold (capture waits behind the release fixes) is satisfied: rc.2 shipped and MEU-113 and MEU-114 are approved; its Session 49 row reads `pending` only by staleness.
- MEU-105 unblocks the crop C key. Session 71 may run before Sessions 69 and 70 if Mat wants the key sooner; otherwise the §4 order stands. Session 72 depends on 68 only through the shared Redact tool letter, not through code.
- MEU-127 (`svc-tts-fp16-phase-guard`) sits in no grouping and is not part of this one.

### 9.8 Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-674 | Renumber Sessions 44 to 48? | autonomous | They run as Sessions 68 to 72 in the §4 order; the §6 rows keep their text and §9.1 says so | Local Canon | 44 is `release-rc1` and 45 to 67 are used (rc2 D-240). Rewriting §6 would erase what D-240 observed; a new section states the mapping once. Two-way. | — |
| D-675 | Which crop rules do redact, step, `head` and `shape` take? | autonomous | Redact takes `_clip_half_open`; step takes the text anchor rule; `head` rides `_clip_arrow`; `shape` waits on D-676 | Local Canon | Redact covers pixels the way pixelate does; a step badge is one point like a text label; an arrow head at a crop edge is already what D-487 ships. D-406 puts the rule on whichever lands second, and that is these sessions. Two-way. | — |
| D-676 | What does a crop do with an ellipse that straddles the crop edge? | human | A: kept when its box lies inside the closed `[0, width] x [0, height]`, otherwise dropped, never clipped (the text rule). Rejected do-nothing: inherit `_clip_rect`, which shrinks the box and draws a smaller ellipse that was never on the source | Human-approved | A clipped rectangle's outline is still a rectangle at the edge; a clipped ellipse's box is a new curve. Dropping is honest and the user redraws in one gesture. The do-nothing option costs no code and matches rect, at the price of a changed shape. | USER_EXPLICIT 2026-11-12 "both recommendations accpeted" |
| D-677 | After MEU-104, what does the filmstrip's "Copy image" copy? | human | A: the filmstrip item fetches `variant=annotated` when the shot has saved marks and `original` otherwise, the "as shown" rule MEU-136's export already uses, so every "Copy image" means the image as you see it; the editor button and Ctrl+C add unsaved marks through the render route. Rejected do-nothing: the filmstrip keeps `variant=original` and two labels copy different things | Human-approved | One label with two meanings is the ambiguity 09's design thesis rejects, and the as-shown rule is already canon for export. The original stays reachable through export. Do-nothing keeps MEU-88's behaviour unchanged for anyone who relies on a clean copy. | USER_EXPLICIT 2026-11-12 "both recommendations accpeted" |
| D-678 | How does Ctrl+C reach the canvas? | autonomous | Page key handler with `isEditableTarget` excluded, following Session 61's PASTE_KEY; Ctrl+C stays in RESERVED_CHORDS | Local Canon | Same chord class and the same text-field guard as Ctrl+V; a registry entry would need the reserved list to change for one key. Two-way. | — |

Carry-forward: Sessions 68 to 72 carry D-674 and D-675, and the row among D-676 to D-678 their MEU touches, with stage `grouping`.
