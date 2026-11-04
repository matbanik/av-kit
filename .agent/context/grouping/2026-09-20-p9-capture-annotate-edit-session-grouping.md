# Phase 9 residual — Capture edit until Save · Session grouping

> **Source:** USER_EXPLICIT 2026-09-20 (`@.agent/workflows/create-plan.md all features as proposed`) accepting Astra’s enhanced approach in `docs/proposals/2026-09-19-p9-capture-annotate-edit-approach-review.md`.
> **Generated:** 2026-09-20
> **Method:** `/create-plan` after Astra peer review (not a second geometry repair)
> **Origin:** MEU-59 made arrow+text land on the aimed pixels. Placement is still fire-and-forget: Undo is the only correction. This residual adds Select-mode edit of the unsaved draft.
> **Status:** Complete — MEU-60 exec review r2 `approved`.

---

## 1. MEU / scope summary

| MEU | Slug | Covers | Layer | Depends on |
|-----|------|--------|-------|------------|
| MEU-60 | `gui-capture-annotate-edit-until-save` | Select mode; arrow body + two endpoints; move committed text / box / highlight; compact mark list; Apply/Cancel color; original-image sampler; rubber-band; guarded Save (button + palette); MEU-59 geometry unchanged | ui | MEU-59 |

Findings → MEU:

| Finding | MEU |
|---------|-----|
| Pointer-up appends; SVG `pointer-events-none`; Undo-only correction | MEU-60 |
| Color is a typed hex field, not a picker/sampler | MEU-60 |
| Hit-first drawing would trap under large highlights | MEU-60 (Select mode) |
| Palette `capture:save` bypasses the Save button `overlayReady` disable | MEU-60 |
| Box resize, text re-edit, OS EyeDropper | **out of scope** (Human-approved Astra deferrals 2026-09-20) |
| Circle / marker | **out of scope** (09 named deferrals + MEU-59 lock) |

---

## 2. Dependency graph + critical path

```
MEU-59 (approved) ─► MEU-60
```

Critical path: MEU-59 → MEU-60.

Parallel: MEU-50 (Phase 11) stays independently unblocked. This session does not steal MEU-50 or MEU-57.

---

## 3. Recommended grouping — 1 session

| # | Slug | MEUs | Why grouped | Token calibration | Split? |
|---|------|------|-------------|-------------------|--------|
| 1 | `p9-capture-annotate-edit` | MEU-60 | Single residual; same CaptureViewport/Page as MEU-59 | Calibrate vs `p9-capture-annotate-arrow-text` (one GUI MEU + Wave 9) | No |

---

## 4. Plan-creation pathway

`/create-plan` → `docs/execution/plans/2026-09-20-p9-capture-annotate-edit/`

---

## 5. Prerequisite gate

Can begin after plan review `approved`: MEU-59 is approved.

---

## 6. Session summary

| Session | Status | Plan folder |
|---------|--------|-------------|
| `p9-capture-annotate-edit` | complete | `docs/execution/plans/2026-09-20-p9-capture-annotate-edit/` |
