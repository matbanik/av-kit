# Phase 9 residual — Capture arrow + text annotation · Session grouping

> **Source:** USER_EXPLICIT 2026-09-19 (“Instead of circle and marker, lets do arrow pointer and text”) plus Astra’s 2026-09-19 adaptation proposal (`docs/proposals/2026-09-19-p9-annotation-adaptation-proposal.md`) with that override.
> **Generated:** 2026-09-19
> **Method:** `/session-grouping` Stage A+B feeding `/create-plan`
> **Origin:** Phase 9 Capture shipped (MEU-34–40) with a fit-to-viewport coordinate defect and SVG/Pillow geometry mismatch. This is a residual quality MEU, not Phase 11 page layout.
> **Status:** Complete — MEU-59 exec review r2 `approved`.

---

## 1. MEU / scope summary

| MEU | Slug | Covers | Layer | Depends on |
|-----|------|--------|-------|------------|
| MEU-59 | `gui-capture-annotate-arrow-text` | Image-pixel `FIT_MAP`; arrow pointer preview/bake; text place/type/Enter/Esc + `bg_color`/`font_size`; fail-closed Save; GET detail sidecar reload; original vs annotated inspect; same DTO for MCP `get`/`annotate`; no new types | ui + bake + GET detail | MEU-39, MEU-40 |

Findings → MEU:

| Finding | MEU |
|---------|-----|
| Viewport subtracts container origin only; `object-contain` letterbox ignored; SVG has no `viewBox` | MEU-59 |
| SVG arrow head 10×4 vs Pillow `max(10, 4*stroke)` angle 0.4 | MEU-59 |
| SVG text has no `la` anchor / `bg_color` plate | MEU-59 |
| `font_size` hardcoded 16; dirty omits `textDraft`; Save silent-returns on Zod fail | MEU-59 |
| Selecting a shot clears vectors instead of loading sidecar | MEU-59 |
| Astra circle then marker | **out of scope** (09 named deferral + Human-approved 2026-09-19) |

---

## 2. Dependency graph + critical path

```
MEU-39 (approved) ─┐
                   ├─► MEU-59
MEU-40 (approved) ─┘
```

Critical path: MEU-39 → MEU-40 → MEU-59.

Parallel: MEU-50 (Phase 11) stays independently unblocked. This session does not steal MEU-50 or reopen page layout. MEU-57 (capture layout) still composes around the viewport after this repair.

---

## 3. Recommended grouping — 1 session

| # | Slug | MEUs | Why grouped | Token calibration | Split? |
|---|------|------|-------------|-------------------|--------|
| 1 | `p9-capture-annotate-arrow-text` | MEU-59 | Single residual; shared CaptureViewport/Page/bake/GET | Calibrate vs `p9-capture-gui` (MEU-39, one GUI MEU + Wave 9) — smaller than that session (no tray/picker) | No |

---

## 4. Plan-creation pathway

Default single-plan-per-phase exception: Phase 9 already completed three sessions. This is **one additional residual plan**:

`/create-plan` → `docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/`

---

## 5. Prerequisite gate

Can begin now: MEU-39 and MEU-40 are approved.

---

## 6. Session summary

| Session | Status | Plan folder |
|---------|--------|-------------|
| `p9-capture-annotate-arrow-text` | complete | `docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/` |
