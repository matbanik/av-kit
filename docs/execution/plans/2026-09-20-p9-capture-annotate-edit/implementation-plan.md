---
project: "2026-09-20-p9-capture-annotate-edit"
date: "2026-09-20"
source: "docs/build-plan/09-screenshot-capture.md#annotation-edit-until-save"
meus: ["MEU-60"]
status: "complete"
template_version: "2.0"
---

# Implementation Plan: Capture overlay edit until Save

> **Project**: `2026-09-20-p9-capture-annotate-edit`
> **Build Plan Section(s)**: [09 §Annotation edit until Save](../../../build-plan/09-screenshot-capture.md#annotation-edit-until-save)
> **Status**: `complete`
> **Grouping**: [2026-09-20-p9-capture-annotate-edit-session-grouping.md](../../../../.agent/context/grouping/2026-09-20-p9-capture-annotate-edit-session-grouping.md)

---

## Goal

MEU-59 made arrow and text land on the aimed pixels. Placement is still fire-and-forget: `onPointer` up appends a finished mark, the SVG overlay is `pointer-events-none`, and **Undo** is the only correction. Color is a typed hex field.

**USER_EXPLICIT 2026-09-20:** implement **all features as proposed** in `ASTRA_REVIEW` (keep-with-changes): Select mode, arrow body + two endpoints, move committed text / box / highlight, compact mark list, Apply/Cancel color, original-image sampler, rubber-band, guarded Save on button **and** palette.

This MEU does not add types, REST fields, or MCP actions. MEU-59 `FIT_MAP` / arrowhead / text-anchor stay.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "Re-evaluated before Step 6 execution 2026-09-20. Glob 0 for graphify-out/graph.json and graphify-out-research/graph.json. GetDynamicTools catalog has no graphify/headroom namespaces. Work is CaptureViewport/CapturePage TSX internals — graphify.md would require direct file search. Headroom has no approved disposition; receipts are exact-evidence bypass class."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-60 | `HANDOFF_60` |

Rolling implementation review: `EXEC_REVIEW_FILE`.
Rolling plan review: `PLAN_REVIEW_FILE`.

Product glob owner: `HANDOFF_FILTER`. Expected count: `HANDOFF_COUNT` = `1`. Filenames: `HANDOFFS`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`. `builder_model` is `BUILDER_PIN`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-60a | Red **before any production edit**: `RED_AC_IDS_UI` vitest titles (includes AC-60.19 keyboard); Playwright named block containing `E2E_BODY_TOKENS` plus census. `RED_ORACLE_CHECK` kind `ui`. `E2E_CLASSIFY` `-Mode red`. `AC-60.14` / `AC-60.18` are exact allowlists in `MEU_SCANS` — they are not Red titles. | — | `compact_continue` | `RED_RECEIPT_UI`; `E2E_SPEC`; compact then re-read `task.md` |
| WP-60b | Green `HIT_MODULE` + pointer machine in `PAGE_FILE`/`VIEWPORT_FILE`: `EDIT_MODES`, handles, mark list, rubber-band, keyboard inspector (`capture-nudge-body` / tail / head), Remove mark. | WP-60a | `compact_continue` | `HIT_MODULE`; `VIEWPORT_FILE`; compact then re-read `task.md` |
| WP-60c | Green `COLOR_MODULE` + `SAMPLE_MODULE`: well, hex, Apply/Cancel, original-image sampler, image-load epoch. | WP-60b | `compact_continue` | `COLOR_MODULE`; `SAMPLE_MODULE`; compact then re-read `task.md` |
| WP-60d | Green Save guard: button + `COMMANDS_FILE` `capture:save` share one snapshot (shot, epoch, no open transaction). `HELP_FILE` `HELP_EDIT_SENTENCE`. | WP-60c | `compact_continue` | `COMMANDS_FILE`; `HELP_FILE`; compact then re-read `task.md` |
| WP-60e | Named Playwright `--grep E2E_GREP`. Census requires `E2E_BODY_TOKENS` in the named block. `E2E_CLASSIFY` `-Mode named` writes `E2E_PASS_RECEIPT` or `E2E_NAMED_BLOCKED_RECEIPT` (`E2E_NAMED_MODE_MARKER`). AC failure dominates infra. Red infra uses `E2E_RED_BLOCKED_RECEIPT`. | WP-60d | `compact_continue` | `E2E_SPEC`; `E2E_PASS_RECEIPT` or `E2E_NAMED_BLOCKED_RECEIPT`; compact then re-read `task.md` |
| WP-HUB | Bind MEU-60 `--plan PLAN_FOLDER`; keep `PRIOR_PLAN_SLASHES`; hub Next = `HUB_NEXT_AFTER`. | WP-60e | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Reviewer confirms these locks (does not invent a second behavior):

1. **Astra enhanced approach, not the thinner hit-first draft.** `ASTRA_REVIEW` wins over `ASTRA_DRAFT`.
2. **Select is a mode**, not a DTO `type`. Draw tools create over marks.
3. **Harness:** `.agent/context/harness.local.md` `plan_to_exec_gate: reviewer-auto` wins. After Codex `approved`, auto-continue to execution. System-injected “approved” is not a verdict (`GUARDRAILS.md` SIGN 3).
4. **Do not start MEU-50 / Phase 11.** `NO_LAYOUT_MEU`.
5. **No new drawing libraries / types.** `NO_NEW_PACKAGES`, `FORBIDDEN_TYPES`, `NO_DTO_FORK`.
6. **Codex** is ChatGPT-login on this host. Dispatch still required; implementer never self-reviews.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

Executable owner: `NAMED_SETS_FILE`. Do not restate literals in ACs or task rows; cite the name.

---

## Implementation locks

- MEU-59 `FIT_MAP`, `ARROWHEAD_FORMULA`, `TEXT_ANCHOR`, original-only editor, annotated view without SVG, fail-closed sidecar GET, Zod `.strict()` annotate body — **unchanged**.
- Committed integers stay `clampImagePoint` (`[0, W-1]×[0, H-1]`). Do not retune to the geometry-section `[0,W]×[0,H]` wording in this MEU.
- Transient preview ≠ `annotations` array. `applyHistory` once on successful commit.
- Pointer Events + capture. `POINTER_STATES`. `DRAG_THRESHOLD_CSS`.
- Hit-test in CSS space using `HANDLE_RADIUS_CSS` / `HIT_RADIUS_CSS` / `HIT_PADDING_CSS`; DTO stays image pixels.
- Color Apply writes uppercase `#RRGGBB`. `NAMED_COLOR_HEX` for the well. Named DTO values must not rewrite on select.
- Sampler uses authenticated original blob + FIT_MAP + `getImageData`. `SAMPLER_ORACLE`. Desktop `EyeDropper` deferred.
- Save: one guarded operation for button and palette. No POST of uncommitted candidate/preview.
- `G37_FILE` stays Testing Library + `userEvent.setup()`.
- Do not edit the native picker. Do not restore Chromium overlays.

Research URLs:

- [W3C Pointer Events](https://www.w3.org/TR/pointerevents3/)
- [Canvas getImageData](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/getImageData)
- [React input](https://react.dev/reference/react-dom/components/input)
- [ShareX keybinds](https://getsharex.org/keybinds/)
- Astra `ASTRA_REVIEW`

---

## §4A GUI Element Compliance

**Triggered:** Select tool, mark list, Remove mark, color well/Apply/Cancel/Sample, arrow handles, Body/Tail/Head nudge inspector.

`docs/gui-element-reference.md`, button/input indexes, and the 10-item enforcement doc remain **absent**. Local fallback: G34 5×3, G31 `bg-accent`, G32 no hex in `className`, G33 no geometry animation, G35 T0–T2.

| Check | Result |
|-------|--------|
| E2E written+wired | `E2E_SPEC` + `E2E_REQUIRED_CASES` + `E2E_TESTIDS` |
| G30–G35 / E2 | No new `<select>`. Tools stay outline/primary. Duration tokens unused. |
| G20 | Existing dirty-thumb confirm; open text/color transaction is dirty |
| G11 | `capture:save` still `COMMANDS_FILE` — now shares the Save guard |
| G16 | CSP unchanged |
| G23 | Settings Capture card untouched |
| G26 | `HELP_FILE` must contain `HELP_EDIT_SENTENCE` (AC-60.15) |
| G27 | No new IPC |
| G37 | `G37_FILE` + `G37_RULE` |
| 10-item enforcement doc | **Absent** — this table is the mapping |

| Element | Variant | Size | States | testid | Feedback |
|---------|---------|------|--------|--------|----------|
| Tool Select (new) | outline (active = primary) | md | default/hover/focus | `capture-tool-select` | T0 |
| Tool Arrow / Text (existing) | outline (active = primary) | md | default | `capture-tool-arrow`, `capture-tool-text` | T0 |
| Mark list (new) | list of buttons | sm | default/selected | `capture-mark-list` | T0 |
| Remove mark (new) | ghost | sm | default/disabled | `capture-remove-mark` | T0 |
| Color well (new) | native `type=color` | sm | default | `capture-color-well` | T0 |
| Color hex (existing) | text | sm | default/focus | `capture-color` | T0 |
| Apply color (new) | primary | sm | default/disabled | `capture-color-apply` | T0 |
| Cancel color (new) | ghost | sm | default | `capture-color-cancel` | T0 |
| Sample original (new) | outline | sm | default/pressed-sampling | `capture-color-sample` | T1 canvas read |
| Handles (new) | SVG chrome | — | visible when selected arrow | `capture-handle-from`, `capture-handle-to` | T0 |
| Nudge Body / Tail / Head (new) | outline (active = primary) | sm | default/disabled (tail/head disabled unless selected arrow) | `capture-nudge-body`, `capture-nudge-tail`, `capture-nudge-head` | T0 |
| Save (existing) | primary | md | default/disabled | `capture-save` | T1 POST annotate |
| Status (existing) | output | — | default/error | `capture-status` | T1 |
| Draw surface (existing) | canvas | — | default | `capture-draw-surface` | T0 |

---

## Proposed Changes

### MEU-60 — `gui-capture-annotate-edit-until-save`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| Annotate Save | existing Zod `.strict()` `annotateInSchema` then Pydantic `AnnotateIn` | same four-type union; colors `NAMED_COLORS` or `#RRGGBB` | extra forbid | extra key / `FORBIDDEN_TYPES` → POST count 0; API 422 | full-list replace of **committed** draft | Spec annotate; MEU-59 |
| Color candidate (UI) | `COLOR_MODULE` | `#RRGGBB` or named; Apply normalizes hex | n/a | invalid hex → Apply disabled / visible error; no history | Apply vs next-draw default | Spec edit section |
| Sampler click | `SAMPLE_MODULE` | integer image pixel in `[0,W-1]×[0,H-1]` | n/a | letterbox / nonopaque / stale epoch → no candidate change | n/a | Spec sampler |
| MCP `annotate` | existing Zod `.strict()` | unchanged | extra forbid | extra key rejected | same as REST | Spec MCP; `NO_DTO_FORK` |

Python `assert` is not validation. No new write surfaces.

#### Acceptance Criteria

> Tag: `unit` or `integration`. Control ACs name observable + call chain + negative oracle.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-60.1 | unit | **Control CSS hit-test.** Observable: `HIT_MODULE` at two fit scales keeps `HIT_RADIUS_CSS` constant in CSS px; letterbox returns no hit; selected-arrow handles beat bodies; coincident `from`/`to` selects `to`. Chain: `HIT_MODULE` used by `VIEWPORT_FILE`. Negative: image-space radius that shrinks under fit → fail. | Spec edit hit-test | image-px radius |
| AC-60.2 | unit | **Control geometry transforms.** Observable: body translate preserves arrow `to-from` delta; endpoint edit preserves the other end; box/highlight `width`/`height` unchanged; collapsing nonzero arrow to zero cancels (returns pre-drag). Chain: `HIT_MODULE` helpers. Negative: independent clamp per endpoint that shears the shaft → fail. | Spec arrow/box edit | shear clamp |
| AC-60.3 | unit | **Control text hit plate.** Observable: `textBackgroundBox` plate is hittable when `bg_color` is empty; no extra painted plate required. Chain: `TEXT_MODULE` + `HIT_MODULE`. Negative: text without bg is unhittable → fail. | Spec text edit; Local Canon `TEXT_MODULE` | miss without bg |
| AC-60.4 | integration | **Control Select vs draw.** Observable: Arrow tool drag over an existing mark **creates** a new arrow then auto-Select; Select mode drag moves the targeted mark. Chain: `PAGE_FILE` pointer machine. Negative: hit-first intercepts drawing (large highlight traps) → fail. | Spec Select mode; Human-approved 2026-09-20 | hit-first |
| AC-60.5 | integration | **Control text move.** Observable: Enter commits; subsequent drag moves `x,y`; Save body has new coords; pointer on `capture-text-draft` does not start a second draft; composing Enter / Backspace / Delete do not Remove mark. Chain: `PAGE_FILE`. Negative: drag-while-typing moves caret field as a mark → fail. | Spec text edit | draft drag |
| AC-60.6 | integration | **Control history coalescing.** Observable: many move events → one undo step restoring exact start; Esc / lost capture / no-op preserve redo. Chain: `applyHistory` only on commit. Negative: `applyHistory` on mousemove → fail. | Spec history; Local Canon `applyHistory` | per-frame undo |
| AC-60.7 | integration | **Control mark list.** Observable: list shows all four types; click selects a covered mark; Remove mark drops that annotation only; `capture-delete` still means file delete. Chain: `VIEWPORT_FILE` list. Negative: Remove mark clicks Capture Delete → fail. | Spec mark list | file delete |
| AC-60.8 | integration | **Control color Apply.** Observable: well/hex update candidate only; Apply writes `#RRGGBB` to selected `color` and default; Cancel writes nothing; named green select shows `NAMED_COLOR_HEX.green` without dirtying. Chain: `COLOR_MODULE` + `PAGE_FILE`. Negative: React `onChange` from the well pushes history → fail. | Spec color; Research-backed React input | onChange commit |
| AC-60.9 | unit | **Control sampler.** Observable: `SAMPLER_ORACLE.rgb` → `SAMPLER_ORACLE.hex`; FIT_MAP integer pixel; overlay ignored; letterbox / stale epoch / nonopaque → no candidate change. Chain: `SAMPLE_MODULE` + `IMAGE_LOADER` blob. Negative: sample fitted canvas including SVG red → fail. | Spec sampler; Canvas getImageData | overlay sample |
| AC-60.10 | integration | **Control Save identity.** Observable: button **and** palette `capture:save` refuse when overlay/image epoch mismatch or a transaction is open; late pointer/sample cannot mutate the next shot. Chain: shared guard in `COMMANDS_FILE`/`PAGE_FILE`. Negative: palette Save posts while Save button is disabled → fail. | Spec Save; MEU-59 overlayReady | unguarded command |
| AC-60.11 | integration | **Control committed snapshot.** Observable: Save POSTs committed list (no preview, no unapplied candidate); annotated view has zero handles/`capture-annotation` SVG; failure keeps dirty draft. Chain: `saveAnnotations`. Negative: POST includes live rubber-band → fail. | Spec Save; MEU-59 edit vs bake | preview POST |
| AC-60.12 | integration | **Control E2E edit path.** Observable: named `test(` title contains `E2E_GREP` **and** that block contains every `E2E_BODY_TOKENS` token; fitted shot: create arrow+text, drag both ends and text, sample `SAMPLER_ORACLE`, Apply, Save body matches, reload, annotated view has no SVG marks. `E2E_TESTIDS` live in `test-ids.ts`. Named run classified by `E2E_CLASSIFY`; AC failure dominates infra. `[B]` only via `E2E_NAMED_BLOCKED_RECEIPT` with `E2E_NAMED_MODE_MARKER` plus `E2E_SANDBOX` and an infra token, bound to **both** `E2E_GREEN_RECEIPT` and parseable `E2E_GREEN_JSON` where Get-Outcome is not `failed`. Missing Green JSON is a gate fail, not `[B]`. Red infra cannot satisfy the gate (`E2E_RED_BLOCKED_RECEIPT` is a different path). Chain: Playwright Electron. Negative: title-only empty `test(` → census fail. | Spec Wave 9; testing-strategy E2E | empty title |
| AC-60.13 | integration | **Control new chrome.** Observable: `capture-tool-select` G34 outline/primary; color well/Apply/Cancel/Sample visible; handles visible only for selected arrow on original view. Chain: `VIEWPORT_FILE`. Negative: hex-only color field remains the sole control → fail. | Spec color + Select; G34 | text-only color |
| AC-60.14 | unit | **Control exact UI/Python dependency sets.** Observable: `ui/package.json` dependency names equal `UI_DEP_NAMES` and devDependency names equal `UI_DEVDEP_NAMES`; each `PY_DEP_ALLOWLIST` file equals that name set. `NO_NEW_PACKAGES` remain named examples. Chain: `MEU_SCANS`. Negative: add `roughjs` (or any name outside the allowlists) → fail. | Human-approved 2026-09-19 | extra package |
| AC-60.15 | unit | **Control HelpCard sentence.** Observable: `HELP_FILE` contains `HELP_EDIT_SENTENCE`. Chain: HelpCard four-tools topic. Negative: omit Select/sample sentence → fail. | G26; Spec edit | missing sentence |
| AC-60.16 | integration | **Control rubber-band.** Observable: Arrow down+move before up draws a preview with **no** `applyHistory`; valid up appends once. Chain: `drawing` state. Negative: each mousemove appends an arrow → fail. | Spec rubber-band | live append |
| AC-60.17 | unit | **Control `NAMED_COLOR_HEX`.** Observable: each `NAMED_COLORS` name maps to the named-sets hex table; unknown name is not silently coerced. Chain: `COLOR_MODULE`. Negative: orange → `#FFA500` mismatch → fail. | Spec color mapping | wrong orange |
| AC-60.18 | unit | **Control exact annotation DTO.** Observable: `ANNOTATE_SCHEMA`, `MCP_CAPTURE`, and `API_SCHEMA_FILE` discriminants equal `ANNOTATE_TYPES`; per-type keys equal `ANNOTATE_FIELDS`; MCP `action` literals equal `MCP_CAPTURE_ACTIONS`; `annotateInSchema` is `.strict()`. Chain: `MEU_SCANS`. Negative: add a fifth type, a new field, or a new MCP action → fail. | Spec MCP; Human-approved | schema fork |
| AC-60.19 | integration | **Control keyboard inspector.** Observable: selected inspector exposes `capture-nudge-body` and, for arrows, `capture-nudge-tail`/`capture-nudge-head`; Arrow keys nudge the focused target by `KEYBOARD_NUDGE_PX` image pixels (one history entry from keydown through keyup); Delete removes the selected mark only when annotation controls own focus; Esc cancels draft/color/sampling/in-progress geometry without pushing history; IME composition and unrelated page controls keep their keys; Backspace never removes marks. Chain: `PAGE_FILE` + `VIEWPORT_FILE` inspector. Negative: Delete with the text draft focused routes to Capture file Delete → fail. | Spec keyboard; Astra keyboard access | file-delete key |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Overlay stays vector until Save | Spec | 09 viewport tools + new edit section |
| Select mode, handles, mark list, sampler, Apply color | Human-approved | USER_EXPLICIT 2026-09-20 + `ASTRA_REVIEW` + spec section written this plan |
| Hit-first vs Select | Research-backed | Astra finding 1; ShareX distinguishes create vs select |
| History coalescing / pointer capture | Research-backed | W3C Pointer Events; Local Canon `applyHistory` |
| Color onChange is not commit | Research-backed | React input docs; Astra finding 4 |
| Sampler = original PNG pixel | Human-approved | USER_EXPLICIT sampler + Astra §6 |
| MEU-59 geometry/bake | Local Canon / Spec | do not retune |
| Box resize, text re-edit, OS EyeDropper | out of scope | Human-approved Astra deferral table 2026-09-20 |
| Circle / marker | out of scope | 09 named deferrals |
| Phase 11 layout | deferred | MEU-50, MEU-57 already scheduled |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `HIT_MODULE` | new | CSS hit-test + translate helpers |
| `COLOR_MODULE` | new | normalize + `NAMED_COLOR_HEX` |
| `SAMPLE_MODULE` | new | original-blob pixel read |
| `VIEWPORT_FILE` | modify | Select, handles, list, color chrome, pointer capture |
| `PAGE_FILE` | modify | `POINTER_STATES`, selection, epoch, Save snapshot |
| `COMMANDS_FILE` | modify | shared Save guard |
| `HELP_FILE` | modify | `HELP_EDIT_SENTENCE` |
| `E2E_SPEC` / `ui/tests/e2e/test-ids.ts` | modify | `E2E_GREP` + `E2E_TESTIDS` |
| `UI_TEST_FILES` | new/modify | Red then Green |
| `docs/build-plan/09-screenshot-capture.md` | modify | spec section (planning) |
| `.agent/context/meu-status.yaml` | modify | MEU-60 bind on H1-3 |

No `packages/api/` edits expected → OpenAPI `--check` only (H1-4 skip regen unless FAIL).

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Circle, marker, freehand, blur, curved arrows | out-of-scope | — | `docs/build-plan/09-screenshot-capture.md` Named deferrals; MEU-59 Human-approved 2026-09-19 |
| Box / highlight resize handles | out-of-scope | — | Human-approved 2026-09-20 (accepted `ASTRA_REVIEW` deferral table) |
| Drag text-entry field / re-edit committed text content | out-of-scope | — | Human-approved 2026-09-20 (`ASTRA_REVIEW`) |
| OS / `EyeDropper` desktop sampler | out-of-scope | — | Human-approved 2026-09-20 (`ASTRA_REVIEW`) |
| Selected stroke / font / `bg_color` rewriting | out-of-scope | — | Human-approved 2026-09-20 (`ASTRA_REVIEW`) |
| Phase 11 page layout | deferred | MEU-50, MEU-57 | scheduled in `meu-status.yaml`; `NO_LAYOUT_MEU` |
| In-picker ShapeManager ink | out-of-scope | — | 09 two-canvas lock; native picker has no annotation tools |
| New REST/MCP annotate fields or `suggest` action | out-of-scope | — | Spec MCP; `NO_DTO_FORK`; Astra GUI-first |
| Konva / Fabric / generative editors | out-of-scope | — | Human-approved 2026-09-19 research lock |
| Retune MEU-59 FIT_MAP / Pillow formulas | out-of-scope | — | Spec geometry section; Astra finding 12 keep code clamp |

---

## BUILD_PLAN.md Audit

This project **does** update hub/index: register MEU-60, keep Phase 11 as Next, note the residual. Validation (exact):

```powershell
rtk proxy pwsh -NoProfile -Command { $matches=@(Select-String -Path docs/BUILD_PLAN.md -Pattern @('MEU-60','p9-capture-annotate-edit')); [pscustomobject]@{matches=$matches.Count; lines=@($matches.LineNumber)} | ConvertTo-Json -Depth 3 } *> C:/Temp/av-kit/build-plan-audit.json; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/build-plan-audit.json; exit $code
```

Do not hand-edit AUTOGEN tables. `meu_status.py update` MEU-60 with `--plan PLAN_FOLDER`; rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`.

---

## Verification Plan

### 1. Red UI
```powershell
rtk proxy npm --prefix ui run test -- --reporter=json --outputFile=C:/Temp/av-kit/fail-to-pass-meu-60-ui.json *> C:/Temp/av-kit/fail-to-pass-meu-60-ui.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'UI Red unexpectedly green'; exit 1 }; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-20-p9-capture-annotate-edit/assert-red-oracle.ps1 -Kind ui -Receipt C:/Temp/av-kit/fail-to-pass-meu-60-ui.txt -JsonReceipt C:/Temp/av-kit/fail-to-pass-meu-60-ui.json; exit $LASTEXITCODE
```

### 2. E2E census + classify
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-20-p9-capture-annotate-edit/assert-e2e-census.ps1 *> C:/Temp/av-kit/meu60-e2e-census.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu60-e2e-census.txt; exit $code
```

Named run classification (Red / Green / gate) is `E2E_CLASSIFY` with `-Mode red|named|gate`. Red infra writes `E2E_RED_BLOCKED_RECEIPT` (`E2E_RED_MODE_MARKER`). Named infra writes `E2E_NAMED_BLOCKED_RECEIPT` (`E2E_NAMED_MODE_MARKER`). Gate pass requires `E2E_GREEN_RECEIPT`+`E2E_GREEN_JSON` Get-Outcome `passed` plus `E2E_PASS_RECEIPT`, or a MODE=named blocked file bound to **both** that Green raw and parseable Green JSON with Get-Outcome not `failed`. Absent `E2E_GREEN_JSON` is a gate fail.

### 3. MEU gate
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-20-p9-capture-annotate-edit/assert-meu-gate.ps1 *> C:/Temp/av-kit/meu60-gate.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu60-gate.txt | Select-Object -Last 40; exit $code
```

### N. OpenAPI Drift Check

No `packages/api/` edits planned. Still run `--check`. `-o` only on FAIL.

```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

`ABSENT_VALIDATOR_RULE`: do not call `tools/validate_closeout_artifacts.py`.

---

## Open Questions

None. USER_EXPLICIT 2026-09-20 accepted `ASTRA_REVIEW` including Select mode, Apply/Cancel color, mark list, and the listed deferrals. Remaining forks were resolved there with sources; the reviewer confirms those locks rather than re-opening product preference.

---

## Research References

- `docs/proposals/2026-09-19-p9-capture-annotate-edit-approach-review.md`
- `docs/proposals/2026-09-19-p9-annotation-adaptation-proposal.md` §3 item 2
- `docs/build-plan/09-screenshot-capture.md` §Annotation edit until Save
- [W3C Pointer Events](https://www.w3.org/TR/pointerevents3/)
- [Canvas getImageData](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/getImageData)
- [React `<input>`](https://react.dev/reference/react-dom/components/input)
- [ShareX keybinds](https://getsharex.org/keybinds/)
