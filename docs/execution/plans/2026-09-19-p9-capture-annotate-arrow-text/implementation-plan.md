---
project: "2026-09-19-p9-capture-annotate-arrow-text"
date: "2026-09-19"
source: "docs/build-plan/09-screenshot-capture.md#annotation-geometry-arrow-text"
meus: ["MEU-59"]
status: "approved"
template_version: "2.0"
---

# Implementation Plan: Capture arrow + text annotation repair

> **Project**: `2026-09-19-p9-capture-annotate-arrow-text`
> **Build Plan Section(s)**: [09 §Annotation geometry (arrow + text)](../../../build-plan/09-screenshot-capture.md#annotation-geometry-arrow-text)
> **Status**: `draft`
> **Grouping**: [2026-09-19-p9-capture-annotate-arrow-text-session-grouping.md](../../../../.agent/context/grouping/2026-09-19-p9-capture-annotate-arrow-text-session-grouping.md)

---

## Goal

The Capture page already has four overlay tools, but pointer coordinates are container pixels (`CaptureViewport` subtracts `getBoundingClientRect` origin only) while the PNG is `object-contain` letterboxed and the SVG has no `viewBox`. Arrow heads and text metrics also disagree between SVG preview and Pillow bake. Astra’s 2026-09-19 proposal (`ASTRA_PROPOSAL`) recommended repairing that path then adding `circle`/`marker`. **USER_EXPLICIT 2026-09-19:** implement **arrow pointer and text**, not circle/marker.

This MEU makes the human arrow+text path trustworthy (fit mapping, preview/bake agreement, honest Save, sidecar reload, inspect bake without stacking vectors on it) and keeps MCP on the **same DTO** with no new action or types.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "Glob 0 for graphify-out/graph.json and graphify-out-research/graph.json. GetDynamicTools catalog has no graphify/headroom namespaces. Work is CaptureViewport/CapturePage TSX internals plus existing Pillow bake — graphify.md would require direct file search anyway. Headroom has no approved disposition; receipts are exact-evidence bypass class."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-59 | `HANDOFF_59` |

Rolling implementation review: `EXEC_REVIEW_FILE`.
Rolling plan review: `PLAN_REVIEW_FILE`.

Product glob owner: `HANDOFF_FILTER`. Expected count: `HANDOFF_COUNT` = `1`. Filenames: `HANDOFFS`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`. `builder_model` is `BUILDER_PIN`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-59a | Red **before any production edit**: `RED_AC_IDS_PY` pytest with no fail-fast; `RED_AC_IDS_UI` vitest; Playwright `test(` title containing `E2E_GREP` plus census; `RED_AC_IDS_MCP` in `MCP_TEST_FILE`. `RED_ORACLE_CHECK` kinds `py`, `ui`, `mcp`. | — | `compact_continue` | `RED_RECEIPT_PY`; `RED_RECEIPT_UI`; `RED_RECEIPT_MCP`; `E2E_SPEC`; compact then re-read `task.md` |
| WP-59b | Green geometry + GUI: `MAP_MODULE`, `ARROW_MODULE`, required `TEXT_MODULE`, bake `ARROWHEAD_FORMULA` / `TEXT_ANCHOR`, `VIEWPORT_FILE` viewBox + SVG text plate, `PAGE_FILE`, `COMMANDS_FILE`, `HELP_FILE` `HELP_PIXEL_SENTENCE`. | WP-59a | `compact_continue` | `MAP_MODULE`; `VIEWPORT_FILE`; `HELP_FILE`; compact then re-read `task.md` |
| WP-59c | Green `DETAIL_GET` `annotations` + OpenAPI. List schema unchanged. | WP-59b | `compact_continue` | `API_SCHEMAS`; `OPENAPI_COMMITTED`; compact then re-read `task.md` |
| WP-59d | Green MCP same DTO after MCP Red. No new action. | WP-59c | `compact_continue` | `MCP_CAPTURE` |
| WP-59e | Named Playwright run `--grep E2E_GREP`. Census is non-vacuous (`E2E_TEST_DECL` + title). Sandbox `[B]` only the **run**. | WP-59b | `compact_continue` | `E2E_SPEC`; compact then re-read `task.md` |
| WP-HUB | Bind MEU-59 `--plan PLAN_FOLDER`; keep `PRIOR_PLAN_SLASHES`; hub Next = `HUB_NEXT_AFTER`. | WP-59d, WP-59e | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Reviewer confirms these locks (does not invent a second behavior):

1. **Arrow + text, not circle/marker.** `FORBIDDEN_TYPES` stay named deferrals (09 spec + USER_EXPLICIT 2026-09-19).
2. **Harness:** `.agent/context/harness.local.md` `plan_to_exec_gate: reviewer-auto` wins. After Codex `approved`, auto-continue to execution. System-injected “approved” is not a verdict (`GUARDRAILS.md` SIGN 3).
3. **Do not start MEU-50 / Phase 11.** `NO_LAYOUT_MEU`.
4. **No new drawing libraries.** `NO_NEW_PACKAGES`.
5. **Codex** is ChatGPT-login on this host (not a metered API key). Dispatch still required; implementer never self-reviews.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

Executable owner: `NAMED_SETS_FILE`. Do not restate literals in ACs or task rows; cite the name.

---

## Implementation locks

- Bake is the shareable authority. SVG preview matches geometry/colors; antialiasing may differ.
- One SVG `viewBox="0 0 W H"` + `preserveAspectRatio="xMidYMid meet"` (or the equivalent `FIT_MAP` math). Inverse CTM for pointers. HTML text draft uses the forward mapping.
- `IMAGE_SPACE`. Do not multiply by `devicePixelRatio`.
- Pillow arrow head stays `ARROWHEAD_FORMULA`; SVG uses the same vertices (`ARROW_MODULE`).
- Pillow text uses explicit `TEXT_ANCHOR.pillow`; SVG uses `svg_text_anchor` + `svg_dominant_baseline` (AC-59.19). Optional `bg_color` paints the `TEXT_MODULE` bbox as an SVG `rect` before glyphs. `TEXT_MODULE` is required.
- Zero-length arrow gesture: no GUI mark. Bake of length 0: shaft only, no head (existing adapter).
- Letterbox pointer-down: ignore. Drag that starts on-image: clamp to image bounds.
- Editor draws on `VARIANT_ORIGINAL` only. `VARIANT_ANNOTATED` view hides SVG marks.
- `DETAIL_GET` returns `annotations`; `LIST_GET` does not. Malformed sidecar / unknown type → 422, not `[]`.
- Save: `parseAnnotateBody` failure dispatches `av-kit:capture:error` and does not POST. Extra keys → POST count 0.
- Dirty = annotations ≠ saved **or** nonempty `textDraft`.
- Box/highlight keep current bake; they only gain `FIT_MAP`.
- MCP: no new `action`. `get` inherits detail annotations; `annotate` body unchanged.
- Do not edit the native picker. Do not restore Chromium overlays.

Research URLs:

- [CSS `object-fit`](https://developer.mozilla.org/en-US/docs/Web/CSS/object-fit)
- [SVG `preserveAspectRatio`](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/preserveAspectRatio)
- [SVG `getScreenCTM`](https://developer.mozilla.org/en-US/docs/Web/API/SVGGraphicsElement/getScreenCTM)
- [Pillow text anchors](https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html)
- [Pillow ImageDraw](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html)

---

## §4A GUI Element Compliance

**Triggered:** Capture viewport tools, text draft, Save, new font/bg/view controls.

`docs/gui-element-reference.md` and button/input indexes remain **absent** except `gui-actions-index.md`. Local fallback: G34 5×3, G31 `bg-accent`, G32 no hex in `className`, G33 no geometry animation, G35 T0–T2.

| Check | Result |
|-------|--------|
| E2E written+wired | `E2E_SPEC` + `E2E_REQUIRED_CASES` + `E2E_TESTIDS` |
| G30–G35 / E2 | No new `<select>`. Tools stay outline/primary. New view buttons outline/primary like tools. Duration tokens unused (no new motion). |
| G20 | Existing dirty-thumb confirm; dirty now includes `textDraft` |
| G11 | `capture:save` still `CAPTURE_COMMANDS.save` |
| G16 | CSP unchanged; blob thumbs stay |
| G23 | Settings Capture card untouched |
| G26 | HelpCard topics already include four tools; `HELP_FILE` must contain `HELP_PIXEL_SENTENCE` (AC-59.20) — do not invent a second HelpCard |
| G27 | No new IPC |
| 10-item enforcement doc | **Absent** — this table is the mapping |

| Element | Variant | Size | States | testid | Feedback |
|---------|---------|------|--------|--------|----------|
| Tool Arrow / Text (existing) | outline (active = primary) | md | default/hover/focus | `capture-tool-arrow`, `capture-tool-text` | T0 |
| Color / stroke (existing) | text | sm | default/focus | `capture-color`, `capture-stroke` | T0 |
| Font size (new, text tool) | text | sm | default/focus | `capture-font-size` | T0 |
| Text background (new, optional) | text | sm | default/focus/empty=none | `capture-text-bg` | T0 |
| Text draft (existing) | text | sm | default/focus | `capture-text-draft` | T0 |
| View original / annotated (new) | outline (active = primary) | sm | default/disabled if no bake | `capture-view-original`, `capture-view-annotated` | T1 GET image |
| Save (existing) | primary | md | default/disabled | `capture-save` | T1 POST annotate |
| Status (existing) | output | — | default/error | `capture-status` | T1 parse/sidecar errors |
| Draw surface (existing) | canvas | — | default | `capture-draw-surface` | T0 vectors |

---

## Proposed Changes

### MEU-59 — `gui-capture-annotate-arrow-text`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| Annotate Save | Zod `.strict()` `annotateInSchema` then Pydantic `AnnotateIn` | union `arrow\|rect\|highlight\|text`; colors `NAMED_COLORS` or `#RRGGBB`; text 1–500; ints | extra forbid | extra key / `FORBIDDEN_TYPES` → POST count 0; API 422 | full-list replace | Spec annotate; MEU-37 |
| GET detail | `CaptureShotDetailOut` (list stays `CaptureShotOut`) | `annotations` validated sidecar | write still forbid; extra top-level sidecar keys ignored on read | unknown type / malformed → 422, not `[]` | n/a (read) | Spec geometry section |
| MCP `annotate` | existing Zod `.strict()` | same union | extra forbid | extra key rejected before HTTP | same as REST | Spec MCP |
| MCP `get` | inherits detail JSON | may include `annotations` | ignore unknown out | 422 sidecar | n/a | Spec MCP `get` |
| Color input | renderer | `NAMED_COLORS` or `#RRGGBB` | n/a | invalid color → no mark / visible error | n/a | Domain `NAMED_COLORS` |

Python `assert` is not validation.

#### Acceptance Criteria

> Tag: `unit` or `integration`. Control ACs name observable + call chain + negative oracle.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-59.1 | unit | **Control `FIT_MAP`.** Observable: `MAP_MODULE` maps `FIT_MAP.example` container `(400,300)` on `1600×900` in `800×600` to image `(800,450)`. Letterbox point with `y < oy` returns `null`. Chain: `mapPointerToImage` used by `VIEWPORT_FILE`. Negative: identity map `(400,300)→(400,300)` on that example → fail. | Spec geometry; MDN object-fit | identity mapping |
| AC-59.2 | unit | **Control `ARROWHEAD_FORMULA`.** Observable: shared fixture vertices for `from [0,0] to [100,0] stroke 3` match Python `_apply_arrow` and `ARROW_MODULE` (head = 12, angle 0.4). Chain: bake `BAKE_ADAPTER`; preview `VIEWPORT_FILE`. Negative: SVG still uses fixed 10×4 → fail. | Spec geometry; Local Canon adapter constants | 10×4 head |
| AC-59.3 | unit | **Control `TEXT_ANCHOR`.** Observable: bake calls `text`/`textbbox` with `anchor="la"`; `bg_color` fills that bbox before glyphs. Chain: `_apply_text`. Negative: implicit baseline with no bg plate when `bg_color` set → fail. | Spec geometry; Pillow text-anchors | skip bg |
| AC-59.4 | integration | **Control viewport transform.** Observable: draw SVG has `viewBox="0 0 {W} {H}"` and `preserveAspectRatio` containing `xMidYMid meet`; pointer uses inverse CTM or `FIT_MAP`; no `devicePixelRatio` multiply in `VIEWPORT_FILE`. Chain: selected shot `width`/`height` → viewport. Negative: `clientX - box.left` as image x → fail. | Spec geometry; MDN getScreenCTM | container pixels as DTO |
| AC-59.5 | integration | **Control arrow gesture.** Observable: arrow tool drag tail→head commits one `type=arrow` in image pixels; hypot==0 creates **no** mark and does not push history. Chain: `onPointer` down/up → `applyHistory`. Negative: click-without-drag adds an arrow → fail. | Spec viewport tools | zero-length mark |
| AC-59.6 | integration | **Control text draft.** Observable: text tool click (on-image) opens `capture-text-draft` at mapped coords; Enter commits `type=text` with `font_size` from `capture-font-size` and optional `bg_color`; Esc cancels; `isComposing` Enter does not commit; dirty is true while draft nonempty even if annotations==saved. Chain: `PAGE_FILE`. Negative: dirty ignores draft; commit on composing Enter → fail. | Spec viewport tools + dirty | omit draft from dirty |
| AC-59.7 | integration | **Control Save fail-closed.** Observable: invalid body (extra key / bad color) → POST count 0 and `capture-status` nonempty; success POSTs full `ANNOTATE_POST` list; original PNG path unchanged. Chain: `saveAnnotations` → Zod → `apiFetch`. Negative: `parseAnnotateBody` null still `setSaved` → fail. | Spec annotate; Boundary Input Contract | silent return |
| AC-59.8 | integration | **Control `DETAIL_GET` annotations.** Observable: GET `/{id}` JSON includes `annotations`; selecting a shot with sidecar loads that list into draft **and** saved; no sidecar → `[]`; malformed/unknown type → 422 and status error, annotations not replaced with `[]`. Chain: `get_shot` + sidecar parse → `PAGE_FILE` chooseItem. Negative: chooseItem always `setAnnotations([])` → fail. | Spec geometry + sidecar | wipe on select |
| AC-59.9 | integration | **Control edit vs bake.** Observable: default view loads `VARIANT_ORIGINAL` with SVG marks; `capture-view-annotated` (enabled iff `annotated_path`) loads `VARIANT_ANNOTATED` and renders **zero** `capture-annotation` nodes. Chain: `IMAGE_LOADER` query `variant`. Negative: vectors drawn on baked PNG → fail. | Spec geometry | overlay on bake |
| AC-59.10 | unit | **Control color vocabulary.** Observable: renderer color schema accepts only `NAMED_COLORS` or `#RRGGBB` (no arbitrary `[A-Za-z]+`). Chain: `ANNOTATE_SCHEMA`. Negative: `color: "chartreuse"` parses → fail. | Domain `NAMED_COLORS`; Spec colors | alphabetic-any |
| AC-59.11 | integration | **Control no new types.** Observable: body `type: circle` or `marker` → Zod null / API 422; box/highlight still commit via `FIT_MAP` (non-zero rect after letterboxed drag). Chain: `AnnotateIn` discriminator. Negative: new union member `circle` → fail. | Spec named deferrals; Human-approved 2026-09-19 | add circle |
| AC-59.12 | integration | **Control E2E arrow+text.** Observable: `E2E_SPEC` case title contains `AC-59.12`; human-path: select shot, arrow drag, text commit, Save, reload/reselect, both marks still present in image space. Written+wired even if run is `[B]` `E2E_SANDBOX`. Chain: Playwright Electron. Negative: only unit tests, no E2E case → fail. | Spec Wave 9; testing-strategy E2E | unwired |
| AC-59.13 | integration | **Control tool-specific fields.** Observable: arrow tool shows stroke, hides font/bg; text tool shows `capture-font-size` + `capture-text-bg`, stroke may hide; buttons stay G34 variants. Chain: `VIEWPORT_FILE`. Negative: font hardcoded 16 with no control → fail. | Spec geometry `font_size`; G34 | hidden font |
| AC-59.14 | unit | **Control `NO_NEW_PACKAGES`.** Observable: none of `NO_NEW_PACKAGES` appear in `ui/package.json` dependencies or Python project deps added this MEU. Chain: package manifests. Negative: add `konva` → fail. | Human-approved 2026-09-19 | new engine |
| AC-59.15 | integration | **Control OpenAPI detail.** Observable: committed OpenAPI `GET /captures/{id}` response schema includes `annotations`; `GET /captures` item schema does **not**. Chain: `export_openapi.py --check` after regen. Negative: list items grow `annotations` → fail. | Spec `CaptureShotOut`; G8 | list bloat |
| AC-59.16 | integration | **Control MCP same DTO.** Observable: `avkit_capture.annotate` still posts `{annotations:[arrow,text,…]}` with no new action; `get` may return `annotations`; descriptions include one arrow+text example and still omit `FORBIDDEN_TYPES`. Chain: `MCP_CAPTURE`. Negative: new `suggest` action or circle example as live schema → fail. | Spec MCP; Astra GUI-first | new verb |
| AC-59.17 | integration | **Control font_size wire.** Observable: committed text annotation `font_size` equals `capture-font-size` integer (not 16 unless the control is 16). Chain: `onTextCommit`. Negative: ignore control → fail. | Spec text fields | hardcoded 16 |
| AC-59.18 | unit | **Control resize stability.** Observable: same image point maps from two container sizes using `FIT_MAP`; stored annotation `{from,to}` does not change when `Cw,Ch` change. Chain: `MAP_MODULE`. Negative: rewrite DTO on resize → fail. | Spec zoom/resize | mutate on resize |
| AC-59.19 | integration | **Control SVG text preview.** Observable: every `type=text` SVG node has `text-anchor="start"` and `dominant-baseline="hanging"`; when `bg_color` is set, a sibling `rect` exists whose box matches `TEXT_MODULE` bbox. Chain: `TEXT_MODULE` → `VIEWPORT_FILE`. Negative: SVG `<text>` without those attributes, or `bg_color` with no plate → fail. | Spec geometry; Pillow text-anchors | baseline-only SVG |
| AC-59.20 | unit | **Control HelpCard pixel sentence.** Observable: `HELP_FILE` contains `HELP_PIXEL_SENTENCE`. Chain: HelpCard four-tools topic. Negative: four-tools body omits that sentence → fail. | G26; Spec Save/reload | missing sentence |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Four tools exist; annotate is Capture page not picker | Spec | 09 viewport tools + named deferrals |
| Arrow + text this MEU; not circle/marker | Human-approved | USER_EXPLICIT 2026-09-19 |
| Fit mapping / viewBox | Research-backed | MDN object-fit + preserveAspectRatio; Astra formula accepted as that mapping |
| Arrowhead geometry | Local Canon | existing `ARROWHEAD_*` in adapter; SVG must match |
| Text `la` + bg plate | Research-backed | Pillow text-anchors; Spec optional `bg_color`; SVG preview is required (AC-59.19) |
| HelpCard pixel sentence | Local Canon | G26; `HELP_FILE` / `HELP_PIXEL_SENTENCE` |
| GET detail annotations | Spec | geometry section + `CaptureShotOut` detail vs list |
| Fail-closed Save | Local Canon | Boundary Input Contract; current silent return is a defect |
| MCP no new action | Spec | existing `annotate` / `get` |
| No Konva/Fabric | Human-approved | 2026-09-19 research lock |
| Box/highlight pixel-inset retune | out of scope | Human-approved arrow+text; they still use `FIT_MAP` |
| If-Match / Load proposal / mark list | out of scope | 09 omits them; Astra later slices |
| Phase 11 layout | deferred | MEU-50, MEU-57 already scheduled |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `MAP_MODULE` | new | `FIT_MAP` + letterbox null |
| `ARROW_MODULE` | new | shared head vertices |
| `TEXT_MODULE` | new | required preview bbox helper (`TEXT_ANCHOR` + bg plate) |
| `VIEWPORT_FILE` | modify | viewBox, CTM, tool-specific controls, view toggle |
| `PAGE_FILE` | modify | mapping, dirty draft, GET load, inspect bake |
| `ANNOTATE_SCHEMA` | modify | `NAMED_COLORS`; keep four types |
| `COMMANDS_FILE` | modify | fail-closed Save |
| `IMAGE_LOADER` | modify | `variant` query |
| `BAKE_ADAPTER` | modify | explicit `anchor="la"` (formula already present) |
| `CAPTURE_SERVICE` | modify | typed sidecar read for detail |
| `API_SCHEMAS` / `API_ROUTES` | modify | detail `annotations` |
| `MCP_CAPTURE` | modify | example only |
| `MCP_TEST_FILE` | modify | AC-59.16 Red/Green |
| `HELP_FILE` | modify | `HELP_PIXEL_SENTENCE` |
| `UI_TEST_FILES` / `PY_TEST_FILES` / `E2E_SPEC` / `ui/tests/e2e/test-ids.ts` | modify/new | AC tests |
| `openapi.committed.json` | modify | only if `--check` fails after API change |
| `docs/BUILD_PLAN.md` | modify | hub Next / Phase 9 residual note (non-AUTOGEN prose) |
| `.agent/context/meu-status.yaml` | modify | already registered pending; execution binds status |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Circle, marker, freehand, blur, curved arrows, spotlight, frames | out-of-scope | — | `docs/build-plan/09-screenshot-capture.md` Named deferrals (four tools only) + USER_EXPLICIT 2026-09-19 |
| In-picker ShapeManager / Chromium overlay | out-of-scope | — | 09 native picker: no annotation tools |
| If-Match / annotation revision concurrency | out-of-scope | — | 09 REST table omits If-Match; Astra called it a separate slice |
| Load-proposal paste / new MCP `suggest` | out-of-scope | — | 09 MCP workflow is `image` then `annotate`; no suggestion verb |
| Accessible mark list / resize handles | out-of-scope | — | 09 viewport tools list gestures only (drag/click), not a manager UI |
| Rect/highlight Pillow inset retune | out-of-scope | — | USER_EXPLICIT arrow+text; 09 already defines unfilled box vs translucent fill |
| Scroll zoom controls | out-of-scope | — | 09: optional, not a deferral blocker; fit is enough |
| macOS/Linux picker | out-of-scope | — | 09 named deferrals Windows-first |
| Phase 11 page composition | deferred | MEU-50, MEU-57 | grouping 2026-09-03; mockup “draw surface unchanged” is superseded only for the transform, not layout |
| Queue-card / Convert / Downloader work | out-of-scope | — | 09 forbids Downloader/Convert→Capture handoff |

---

## BUILD_PLAN.md Audit

This project **does** update hub prose: Phase 9 is no longer “complete at MEU-40” while MEU-59 is pending; after approval, Next remains `HUB_NEXT_AFTER` (MEU-50). Do not hand-edit AUTOGEN tables.

```powershell
rtk proxy pwsh -NoProfile -Command { $matches=@(Select-String -Path docs/BUILD_PLAN.md -Pattern 'p9-capture-annotate-arrow-text|MEU-59'); [pscustomobject]@{matches=$matches.Count; lines=@($matches.LineNumber)} | ConvertTo-Json -Depth 3 } *> C:/Temp/av-kit/build-plan-audit.json; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/build-plan-audit.json; exit $code
```

---

## Verification Plan

> Classify every command through `.agent/docs/output-evidence-policy.md`.

### 1. Red oracle (UI)

```powershell
rtk proxy npm --prefix ui run test -- --reporter=json --outputFile=C:/Temp/av-kit/fail-to-pass-meu-59-ui.json *> C:/Temp/av-kit/fail-to-pass-meu-59-ui.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'UI Red unexpectedly green'; exit 1 }; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/assert-red-oracle.ps1 -Kind ui -Receipt C:/Temp/av-kit/fail-to-pass-meu-59-ui.txt -JsonReceipt C:/Temp/av-kit/fail-to-pass-meu-59-ui.json; exit $LASTEXITCODE
```

### 2. Red oracle (Python) — no fail-fast

```powershell
rtk proxy uv run pytest tests/unit/test_capture_adapter.py tests/unit/test_capture_service.py tests/e2e/test_api_captures.py --tb=short -v *> C:/Temp/av-kit/fail-to-pass-meu-59-py.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'PY Red unexpectedly green'; exit 1 }; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/assert-red-oracle.ps1 -Kind py -Receipt C:/Temp/av-kit/fail-to-pass-meu-59-py.txt; exit $LASTEXITCODE
```

### 2b. Red oracle (MCP)

```powershell
rtk proxy npm --prefix mcp-server run test -- --reporter=json --outputFile=C:/Temp/av-kit/fail-to-pass-meu-59-mcp.json *> C:/Temp/av-kit/fail-to-pass-meu-59-mcp.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'MCP Red unexpectedly green'; exit 1 }; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/assert-red-oracle.ps1 -Kind mcp -Receipt C:/Temp/av-kit/fail-to-pass-meu-59-mcp.txt -JsonReceipt C:/Temp/av-kit/fail-to-pass-meu-59-mcp.json; exit $LASTEXITCODE
```

### 2c. E2E Red write (before production)

Write a Playwright `test(` whose title contains `E2E_GREP`, then:

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/assert-e2e-census.ps1 *> C:/Temp/av-kit/meu59-e2e-census.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu59-e2e-census.txt; exit $code
```

Attempt the named case for FAIL_TO_PASS. No-display sandbox `[B]` only the **run**.

```powershell
$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts --grep AC-59.12 *> C:/Temp/av-kit/fail-to-pass-meu-59-e2e.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/fail-to-pass-meu-59-e2e.txt | Select-Object -Last 40; exit $code
```

### 3. UI green

```powershell
rtk proxy npm --prefix ui run typecheck *> C:/Temp/av-kit/meu59-typecheck.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu59-typecheck.txt | Select-Object -Last 40; exit $code
```

Then `npm --prefix ui run test`, `npm --prefix ui run lint` (each own receipt).

### 4. Python green + OpenAPI

```powershell
rtk proxy uv run pytest tests/unit/test_capture_adapter.py tests/unit/test_capture_service.py tests/e2e/test_api_captures.py -q --tb=short *> C:/Temp/av-kit/meu59-pytest.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu59-pytest.txt | Select-Object -Last 40; exit $code
```

```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

Regenerate with `-o` **only** if Step 1 reported `[FAIL]`.

### 5. E2E named run (after Green)

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/assert-e2e-census.ps1 *> C:/Temp/av-kit/meu59-e2e-census.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/meu59-e2e-census.txt; exit $code }; $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts --grep AC-59.12 *> C:/Temp/av-kit/meu59-e2e.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu59-e2e.txt | Select-Object -Last 40; exit $code
```

Un-run E2E in a no-display sandbox is `[B]` with `E2E_SANDBOX` follow-up; the `test(` case must still exist.

### 6. No new packages / G36 / placeholders

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/assert-meu-scans.ps1 *> C:/Temp/av-kit/meu59-deps.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu59-deps.txt; exit $code
```

### 7. MEU_GATE (typecheck, lint, vitest, pytest, OpenAPI, MCP tests, E2E census, MEU_SCANS)

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/assert-meu-gate.ps1 *> C:/Temp/av-kit/meu59-gate.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu59-gate.txt | Select-Object -Last 40; exit $code
```

### 8. H2-4 closeout (`CLOSEOUT_H24_SCRIPT`)

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-09-19-p9-capture-annotate-arrow-text/assert-closeout-h24.ps1 *> C:/Temp/av-kit/closeout-check-p9-annotate.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/closeout-check-p9-annotate.txt; exit $code
```

---

## Open Questions

Research resolved the geometry forks (fit formula, `la` anchor, detail-vs-list GET). No remaining `Human-decision-required` item. Reviewer may still reject a lock; that is a finding, not a stop before dispatch.

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| Pointer mapping | A. Single SVG `viewBox` + inverse CTM | MDN preserveAspectRatio / getScreenCTM | One matrix | Needs image inside SVG or matched overlay | ✅ |
| | B. Keep HTML `img` + hand `FIT_MAP` | CSS object-fit | Less markup change | Two surfaces can drift | ⚠️ allowed equivalent if tests pin `FIT_MAP.example` |
| GET annotations | A. Detail only | REST list vs detail; Astra | Catalog stays small | Extra GET on select | ✅ |
| | B. Include on list | convenience | fewer round-trips | bloats filmstrip poll | ❌ |

---

## Research References

- `docs/proposals/2026-09-19-p9-annotation-adaptation-proposal.md` (advisory; circle/marker **not** adopted)
- [Pillow text anchors](https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html)
- [MDN object-fit](https://developer.mozilla.org/en-US/docs/Web/CSS/object-fit)
- [MDN preserveAspectRatio](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/preserveAspectRatio)
