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
| 44 | `capture-redact` | MEU-103 | P2 | pending | — |
| 45 | `capture-copy-image` | MEU-104 | P2 | pending | — |
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
