# 2026-10-09 triage residuals · Session grouping

> **Source:** `.agent/context/triage-output.yaml` from `/issue-triage` on 2026-10-09 (26 ungrouped open issues, Mat's four unfiled 2026-09-30 items, Mat's 2026-10-09 local checks). The user accepted every triage recommendation ("All recommendations accpeted as proposed", 2026-10-09); rulings are in `known-issues.yaml` `enrichment.decision_log` D-40 to D-69.
> **Generated:** 2026-10-09
> **Method:** `/session-grouping` Stage A (issues → MEU-71–91, registered in `meu-status.yaml`, `render --check` green; build-plan homes in 03/04/07/09) + Stage B (MEUs → Sessions 32–39; MEU-71 extends Session 31 in the [2026-09-30 grouping](2026-09-30-gui-walkthrough-residuals-session-grouping.md)).
> **Origin:** The 2026-09-30 grouping (Sessions 27–31) covered only the walkthrough batch. Since then Sessions 27–30 and Mat's looks filed 26 more issues, two of them high severity (packaged TTS cannot synthesize; MCP TTS generate times out).
> **Status:** Active — reversible draft, not a gate. Nothing here approves a plan or authorizes execution.
> **Gated docs:** Session 30 is in review and its `GATED_PATHS` include `docs/build-plan/06-gui.md`, `11-page-layout.md`, `gui-actions-index.md` and `build-priority-matrix.md`. Their edits (matrix rows 3.6–3.10, 4.4, 7.3, 7.4, 9.13–9.24, 11.13 and the 11 §TTS voice panel alignment section for MEU-79) wait for Session 30's approval (§8 D-1).

---

## 1. MEU / scope summary

| MEU | Slug | Covers (known issues) | Layer | Depends on |
|-----|------|-----------------------|-------|------------|
| MEU-71 | `gui-mcp-setup-prompt` | `MCP-SETUP-PROMPT` → **Session 31** | ui main + Settings + 07 docs | MEU-23, MEU-25 |
| MEU-72 | `dist-tts-onnx-runtime` | `TTS-PACKAGED-RUNTIME-EXCLUDED` (+ records candidate `MCP-PACKAGED-ENTRY-UNREACHABLE`) | infra + packaging | MEU-24, MEU-62 |
| MEU-73 | `svc-tts-voice-assets` | `TTS-VOICE-PACK-LAZY-FETCH`, `SETTINGS-TTS-ASSET-ROW-STALE`, `TTS-SPACY-SYSPATH-PREPEND` | core + infra + Settings | MEU-62 |
| MEU-74 | `svc-tts-language-runtime` | `TTS-NON-ENGLISH-G2P-DEPS` | core + infra + api + TTS page | MEU-73, MEU-64 |
| MEU-75 | `svc-tts-device-fallback` | `TTS-MODEL-FLOW-GAPS` | infra + api + TTS page | MEU-62, MEU-63 |
| MEU-76 | `api-error-surface` | `API-UNHANDLED-ERROR-OPAQUE` | api + core (download) | MEU-14 |
| MEU-77 | `svc-tts-async-generate` | `MCP-TTS-GENERATE-SYNCHRONOUS` | core + api + mcp + TTS page | MEU-62, MEU-63, MEU-68, MEU-76 |
| MEU-78 | `svc-ffmpeg-resolver` | `FFMPEG-RESOLUTION-DIVERGENCE` | infra + api wiring | MEU-13, MEU-29 |
| MEU-79 | `gui-tts-voice-panel-layout` | `TTS-MODEL-ROW-LAYOUT` | ui (TTS page) | MEU-63, MEU-75 |
| MEU-80 | `gui-icon-button-hints` | `CAPTURE-TOOLTIPS-NOT-SHOWN` | ui (shared primitive) | MEU-65, MEU-67 |
| MEU-81 | `gui-capture-action-row` | `CAPTURE-ACTION-ROW-ICONS`, `CAPTURE-MARKS-ROW-SQUEEZED`, `CAPTURE-SAMPLE-ORIGINAL-UNLABELED`, `CAPTURE-HOTKEY-BANNER-GAP` | ui (Capture) | MEU-80, MEU-67 |
| MEU-82 | `capture-text-baseline` | `CAPTURE-TEXT-BG-PREVIEW-OFFSET` | ui (viewport) | MEU-59 |
| MEU-83 | `capture-arrow-geometry` | `CAPTURE-BAKE-ARROW-THIN` | infra bake + ui preview | MEU-59, MEU-67 |
| MEU-84 | `capture-file-variant-sync` | `CAPTURE-STALE-ANNOTATED-PATH`, `CAPTURE-OPEN-FILE-VARIANT` | core + ui | MEU-39, MEU-67 |
| MEU-85 | `gui-capture-size-scrub` | `CAPTURE-SIZE-MOUSE-CONTROL` | ui | MEU-65 |
| MEU-86 | `gui-capture-color-swatches` | `CAPTURE-NAMED-COLOR-SWATCHES` | ui | MEU-65 |
| MEU-87 | `gui-capture-tool-lock` | `CAPTURE-AUTO-SELECT-AFTER-DRAW` | ui | MEU-60, MEU-65 |
| MEU-88 | `gui-capture-filmstrip-menu` | `CAPTURE-FILMSTRIP-CONTEXT-MENU` | ui + main IPC | MEU-57 |
| MEU-89 | `gui-capture-filmstrip-multiselect` | `CAPTURE-FILMSTRIP-MULTISELECT` | ui | MEU-88 |
| MEU-90 | `capture-pixelate-mark` | `CAPTURE-PIXELATE-TOOL` | domain + infra + api + mcp + ui | MEU-59, MEU-67 |
| MEU-91 | `capture-eraser-mark` | `CAPTURE-ERASER-TOOL` | domain + infra + api + mcp + ui | MEU-90 |

Findings → MEU traceability (every open or candidate row accounted for):

| Known issue | Category | MEU / disposition |
|-------------|----------|-------------------|
| MEU-71 … MEU-91 rows above | MEU-NEW | as listed |
| `CAPTURE-FLATTEN-WITH-BACKUP`, `MCP-INSTRUCTIONS-CAPTURE-REMOVE-FILES`, `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA` | MEU-NEW / BLOCKED | MEU-67 (Session 30); resolved at its H2-2 (third id added 2026-10-09) |
| `HEADER-CONSOLE-SETTINGS-BUTTON-STATE`, `SETTINGS-ACTIVE-SECTION-HIGHLIGHT` | MEU-NEW | MEU-69, MEU-70 (Session 31) |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | UPSTREAM (mitigated) | not an MEU; track anthropics/claude-code #98978 |
| `TOOLING-SHARED-REGISTRY-COUPLING`, `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE`, `UI-ELECTRON-LAZY-INSTALL-RACE`, `E2E-ELECTRON-LAUNCH-FLAG`, `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` | TECH-DEBT | not MEUs; a debt batch (§8 D-3) |
| `DOWNLOAD-QUEUE-DRAG-OVER-MISS` | MONITORING | reopen with A-4 diagnostics on the next miss |
| `CAPTURE-JOURNAL-VOLATILE` | DEFER | stays deferred |
| `MCP-PACKAGED-ENTRY-UNREACHABLE` | candidate | checked on MEU-72's installer build |
| `TTS-VOICE-SELECT-LAYOUT-JUMP` | dismissed | not reproduced (Mat, 2026-10-09) |

Build-plan homes (Stage A3, source-labelled ACs): [03 §TTS voice assets](../../../docs/build-plan/03-service-layer.md#tts-voice-assets-residual), [§TTS language runtime](../../../docs/build-plan/03-service-layer.md#tts-language-runtime-residual), [§TTS device resolution](../../../docs/build-plan/03-service-layer.md#tts-device-resolution-residual), [§TTS async generation](../../../docs/build-plan/03-service-layer.md#tts-async-generation-residual), [§FFmpeg resolution](../../../docs/build-plan/03-service-layer.md#ffmpeg-resolution-residual); [04 §Unhandled errors](../../../docs/build-plan/04-rest-api.md#unhandled-errors-residual); [07 §Packaged ONNX TTS runtime](../../../docs/build-plan/07-distribution.md#packaged-onnx-tts-runtime-residual), [§MCP setup prompt](../../../docs/build-plan/07-distribution.md#mcp-setup-prompt-residual); [09 §Residuals registered 2026-10-09](../../../docs/build-plan/09-screenshot-capture.md#icon-button-hints) (twelve sections). MEU-79's 11 section follows Session 30 approval.

---

## 2. Dependency graph + critical path

```
MEU-62 (approved) ──► MEU-73 ──► MEU-74 ─┐
MEU-24, MEU-62 ─────► MEU-72 ────────────┴── Session 32  tts-engine-runtime

MEU-14 ──► MEU-76 ──► MEU-77 ─┐   (MEU-77 also needs MEU-62/63/68)
MEU-13, MEU-29 ──► MEU-78 ────┴────────────── Session 33  backend-robustness

MEU-65, MEU-67 ──► MEU-80 ──► MEU-81 ──────── Session 34  capture-chrome

MEU-62, MEU-63 ──► MEU-75 ──► MEU-79 ──────── Session 35  tts-voice-panel   (after Session 33: shared TTSPage run bar)

MEU-59 ──► MEU-82 ─┐
MEU-59, MEU-67 ──► MEU-83 ─┼─────────────────── Session 36  capture-render-fidelity
MEU-39, MEU-67 ──► MEU-84 ─┘

MEU-65 ──► MEU-85, MEU-86;  MEU-60, MEU-65 ──► MEU-87 ── Session 37  capture-editor-options

MEU-57 ──► MEU-88 ──► MEU-89 ──────────────── Session 38  capture-filmstrip-actions

MEU-59, MEU-67 ──► MEU-90 ──► MEU-91 ──────── Session 39  capture-new-marks   (after Session 36: shared bake code)

MEU-23, MEU-25 ──► MEU-71 ─── Session 31b gui-mcp-setup-prompt (moved from Session 31, §8 D-55)
MEU-25, MEU-71 ──► MEU-92 ─── Session 31b (packaged MCP server bundle, §8 D-56)
```

**Critical path:** MEU-76 → MEU-77 (the P2 MCP/TTS timeout) and MEU-73 → MEU-74. Everything else hangs off approved MEUs, except MEU-67 (Session 30, in review), which MEU-80/81/83/84/90 build on.

**Parallel tiers:** Sessions 32, 33 and 34 have no mutual dependency; they are sequenced by priority and by the one-project-per-session rule. Session 35 follows 33 and Session 39 follows 36 for shared files, not hard dependencies.

---

## 3. Recommended grouping — 8 sessions (32–39) + Session 31 expansion

### Session 31 — `gui-polish-residuals` (MEU-69, MEU-70, **MEU-71**) · P3

Defined in the 2026-09-30 grouping; MEU-71 added there today (§8 D-2). Needs Session 30 approved first (06/11/gui-actions-index edits). Session 31 executed without MEU-71; it moved to Session 31b (§8 D-55).

### Session 31b — `gui-mcp-setup-prompt` (MEU-71, MEU-92) · P3

MEU-71 (§8 D-55): the Settings MCP setup prompt per 07 §MCP setup prompt (triage D-48–D-54 in `MCP-SETUP-PROMPT`). MEU-92 (§8 D-56): the self-contained MCP server bundle the packaged app ships, per 07 §MCP server bundle (`MCP-PACKAGED-ENTRY-UNREACHABLE`), with `MCP_ENTRY_PROBE` on a built `win-unpacked` tree as a pass condition.

### Session 32 — `tts-engine-runtime` (MEU-73, MEU-74, MEU-72) · P2

- **Layer / files:** `packages/infrastructure` `tts/adapter.py`, `tts/assets.py`, `model_manager/`; `packages/core` `services/models.py`, `services/health.py`, `services/tts.py`; `packages/api` wiring, voices/health schemas + OpenAPI; `packaging/avkit-backend.spec`; Settings Dependencies card; TTS voice combobox (disabled voices).
- **Why grouped:** all three change how TTS runtime pieces are provisioned and reported (managed assets, readiness rows, availability), in the same adapter/assets/health files. MEU-72 (no-torch ONNX path) is verified by the same generate regressions.
- **Order:** MEU-73 (asset plumbing) → MEU-74 (availability uses it) → MEU-72 (packaging and the local installer smoke).
- **Cloud/local:** Python work in the container; the packaged smoke and espeak-ng detection on Windows are local stages.
- **Token estimate:** calibrate vs Session 27 `tts-repair` (MEU-62 engine half) plus Session 24/p7 `p7-distribution` for the packaging row.
- **Split flag:** **yes, candidate** — if the MEU-74 handoff passes ~50% context, run MEU-72 as 32b.

### Session 33 — `backend-robustness` (MEU-76, MEU-78, MEU-77) · P2

- **Layer / files:** `packages/api` `errors.py`, `main.py`, `routes/tts.py`, `wiring.py`, OpenAPI; `packages/core` `services/download.py`, `services/tts.py`; `packages/infrastructure` `media/adapter.py`, `youtube/adapter.py`; `mcp-server/src/client.ts`, `toolsets/tts.ts`, audit baseline; TTS run bar polling.
- **Why grouped:** three backend contract fixes sharing the error envelope, wiring and OpenAPI diff; MEU-77's background failures need MEU-76's logging and CORS-safe 500 to be visible.
- **Order:** MEU-76 → MEU-78 → MEU-77.
- **Cloud/local:** container for Python/MCP; the MCP audit re-baseline (poll/cancel steps) and `WINDOWS_GATE` are local.
- **Token estimate:** calibrate vs `p9-capture-api-mcp` (MEU-37/38) for REST+MCP+OpenAPI and Session 28 `mcp-live-audit` for the baseline update.
- **Split flag:** **candidate** — MEU-77 is the largest (service + REST + MCP + GUI + audit); split to 33b if needed.

### Session 34 — `capture-chrome` (MEU-80, MEU-81) · P2

- **Layer / files:** a shared tooltip primitive under `ui/src/renderer/src/components/`, `ToolbarIconButton`, `CaptureViewport.tsx` chrome rows, `CapturePage.tsx` per-shot actions/header/hotkey status, `capture-sample.ts` (removed), capture Electron specs, test-ids, 09/11 text.
- **Why grouped:** icon-only buttons need the hint primitive; both live in the Capture chrome and the same Electron wave. Several Human-approved AC amendments (MEU-57/60/65) are decided already (D-49, D-51, D-64).
- **Token estimate:** calibrate vs Session 29 `capture-viewport-chrome` (MEU-65/66).
- **Split flag:** no.

### Session 35 — `tts-voice-panel` (MEU-75, MEU-79) · P3

- **Layer / files:** `tts/adapter.py` device resolution, device list endpoint/field, `TTSPage.tsx` model row and Format/Speed controls, TTS Electron geometry spec, 11 §TTS voice panel alignment.
- **Why grouped:** both change the Voice panel's model row; the device list feeds the row MEU-79 lays out. After Session 33 because MEU-77 also edits `TTSPage.tsx`.
- **Token estimate:** calibrate vs Session 27 MEU-63 (model row) — smaller.
- **Split flag:** no.

### Session 36 — `capture-render-fidelity` (MEU-82, MEU-83, MEU-84) · P3

- **Layer / files:** `CaptureViewport.tsx` text/arrow marks, `capture-text-metrics.ts`, `capture-arrow-head.ts`, `packages/infrastructure` capture bake, `services/capture.py` `scan_inbox`, `capture-commands.ts`.
- **Why grouped:** preview-vs-bake fidelity and file/variant truth on the same capture render path; one bake-fixture suite.
- **Token estimate:** calibrate vs `p9-capture-annotate-arrow-text` (MEU-59).
- **Split flag:** no.

### Session 37 — `capture-editor-options` (MEU-85, MEU-86, MEU-87) · P4

- **Layer / files:** `CaptureViewport.tsx` options row, a shared scrub number input, `capture-color.ts`, CapturePage gesture reducer and undo coalescing.
- **Why grouped:** three small editor-options changes in the same row and reducer.
- **Token estimate:** calibrate vs `p9-capture-annotate-edit` (MEU-60), smaller.
- **Split flag:** no.

### Session 38 — `capture-filmstrip-actions` (MEU-88, MEU-89) · P4

- **Layer / files:** `CaptureFilmstrip.tsx`, preload/main clipboard IPC, CapturePage selection model, delete confirm, gui-actions-index.
- **Why grouped:** MEU-89 depends on MEU-88's menu; same component and selection model.
- **Token estimate:** calibrate vs `p6-gui-login-item` (MEU-61, main + renderer IPC).
- **Split flag:** no.

### Session 39 — `capture-new-marks` (MEU-90, MEU-91) · P4

- **Layer / files:** domain Annotation union + sidecar, Pillow bake, SVG preview/toolbar/hit-test, OpenAPI + MCP annotate schema, 09 spec.
- **Why grouped:** both add a rectangle mark through every layer; MEU-91 reuses MEU-90's plumbing. After Session 36 (shared bake code).
- **Token estimate:** calibrate vs Session 30 `capture-flatten-backup` (domain + API + MCP + GUI).
- **Split flag:** no.

---

## 4. Plan-creation pathway

Multi-session fan-out. Run `/create-plan` once per session, in order, each reading this proposal for scope:

1. `/create-plan gui-polish-residuals` → MEU-69, MEU-70 (2026-09-30 grouping, Session 31; done). MEU-71 → `/create-plan gui-mcp-setup-prompt` (Session 31b, §8 D-55), with MEU-92 (§8 D-56, accepted)
2. `/create-plan tts-engine-runtime` → MEU-73, MEU-74, MEU-72
3. `/create-plan backend-robustness` → MEU-76, MEU-78, MEU-77
4. `/create-plan capture-chrome` → MEU-80, MEU-81
5. `/create-plan tts-voice-panel` → MEU-75, MEU-79
6. `/create-plan capture-render-fidelity` → MEU-82, MEU-83, MEU-84
7. `/create-plan capture-editor-options` → MEU-85, MEU-86, MEU-87
8. `/create-plan capture-filmstrip-actions` → MEU-88, MEU-89
9. `/create-plan capture-new-marks` → MEU-90, MEU-91

Each plan follows `.agent/docs/cloud-local-collaboration.md` (gate location and reviewer route at plan time, `ENV_BOUND_*` census, both gate scripts from one stage list).

---

## 5. Prerequisite gate

- **Session 30 approval first** for every session that edits `06-gui.md`, `11-page-layout.md`, `gui-actions-index.md` or `build-priority-matrix.md` (Sessions 31, 34, 35, 37, 38, 39 at least), and before the deferred matrix rows and the MEU-79 section are written (§8 D-1).
- Sessions 32 and 33 touch none of those files and could start while Session 30 is in review, but one project per session still applies.
- MEU-80/81/83/84/90 build on MEU-67's code; they plan against Session 30's approved state.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 31 | `gui-polish-residuals` | MEU-69, MEU-70 (MEU-71 moved to 31b, D-55) | P3 | approved | `docs/execution/plans/2026-10-10-gui-polish-residuals/` |
| 31b | `gui-mcp-setup-prompt` | MEU-71, MEU-92 (MEU-71 moved from 31, D-55; MEU-92 D-56) | P3 | approved | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/` |
| 32 | `tts-engine-runtime` | MEU-73, MEU-74, MEU-72 | P2 | approved | `docs/execution/plans/2026-10-14-tts-engine-runtime/` |
| 33 | `backend-robustness` | MEU-76, MEU-78, MEU-77 | P2 | approved | `docs/execution/plans/2026-10-14-backend-robustness/` |
| 34 | `capture-chrome` | MEU-80, MEU-81 | P2 | approved | `docs/execution/plans/2026-10-14-capture-chrome/` |
| 35 | `tts-voice-panel` | MEU-75, MEU-79 | P3 | approved | `docs/execution/plans/2026-10-16-tts-voice-panel/` |
| 36 | `capture-render-fidelity` | MEU-82, MEU-83, MEU-84 | P3 | approved | `docs/execution/plans/2026-10-14-capture-render-fidelity/` |
| 37 | `capture-editor-options` | MEU-85, MEU-86, MEU-87 | P4 | approved | `docs/execution/plans/2026-10-16-capture-editor-options/` |
| 38 | `capture-filmstrip-actions` | MEU-88, MEU-89 | P4 | approved | `docs/execution/plans/2026-10-14-capture-filmstrip-actions/` |
| 39 | `capture-new-marks` | MEU-90, MEU-91 | P4 | approved | `docs/execution/plans/2026-10-16-capture-new-marks/` |

---

## 7. Token calibration sources

- Session 27 `tts-repair` (MEU-62/63/64) — Sessions 32, 35.
- `p7-distribution` (MEU-24/25) — MEU-72 packaging.
- `p9-capture-api-mcp` (MEU-37/38) and Session 28 `mcp-live-audit` (MEU-68) — Session 33.
- Session 29 `capture-viewport-chrome` (MEU-65/66) — Session 34.
- `p9-capture-annotate-arrow-text` (MEU-59) and `p9-capture-annotate-edit` (MEU-60) — Sessions 36, 37.
- `p6-gui-login-item` (MEU-61) — Session 38.
- Session 30 `capture-flatten-backup` (MEU-67) — Session 39.
- Sessions 25–30 for the cloud/local gate overhead (several Windows round trips per session).

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1 | When are the gated build-plan edits (matrix rows, MEU-79's 11 section, 06/gui-actions-index) written? | autonomous | After Session 30's execution review approves; this grouping writes only ungated homes (03/04/07/09) and the SSOT | Local Canon | Session 30's `windows-gate-check` refuses any `GATED_PATHS` change after its gate (cloud-local §3.4), so editing them now would reopen its Windows gate. The cost of waiting is one dangling anchor (MEU-79) and missing matrix rows for a few days. Two-way. | — |
| D-2 | Does `MCP-SETUP-PROMPT` join Session 31? | human | Yes, as MEU-71; Session 31 becomes P3 | Human-approved | Recommended in the triage report: it shares `SettingsPage.tsx` and the Settings Electron wave with MEU-70, so one plan/review cycle instead of two. | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-3 | Are the tech-debt rows MEUs? | autonomous | No; a separate debt batch (`TOOLING-SHARED-REGISTRY-COUPLING`, `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE`, `UI-ELECTRON-LAZY-INSTALL-RACE`, `E2E-ELECTRON-LAUNCH-FLAG`, `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT`) | Local Canon | Same rule as the 2026-09-30 grouping D-5 and `issue-triage.md` (TECH-DEBT → debt batch). Two-way. | — |
| D-4 | Session order | autonomous | 31 (already queued, small) → P2 sessions 32, 33, 34 → P3 35, 36 → P4 37, 38, 39 | Local Canon | Priority bands from the triage matrix; Session 31 keeps its queued slot. Session 35 after 33 and 39 after 36 for shared files. Two-way. | — |
| D-5 | Keep TTS page work (MEU-75, MEU-79) out of the engine session? | autonomous | Yes, Session 35 after Session 33 | Local Canon | Session 32 is already a split candidate; MEU-77 (Session 33) edits the same `TTSPage.tsx`, so the page work lands once after both. Two-way. | — |
| D-6 | Where does the independent MEU scoping review run? | human | Codex scoping review on this grouping draft (batches with 3+ MEUs), not during triage | Human-approved | Recommended in the triage report: the review ledger needs an acceptance-criteria source, which exists only once MEUs and their build-plan homes exist. | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-7 | Repair the shared `status_labels` in `meu-status.yaml`? | autonomous | Yes: every row's labels rebuilt from its own status during registration | Local Canon | One YAML anchor was shared by many rows, so the registry showed MEU-63/68 (approved) and MEU-69/70 (pending) as `ready_for_review`. The SSOT status field was right; only the labels were wrong. `render --check` passes. Two-way. | — |
| D-55 | Where does MEU-71 run, now that Session 31 executed without it? | human | Its own Session 31b (MEU-71 alone), next | Human-approved | Session 31 closed without it (current-focus); folding it into a later session would tie a small UI MEU to unrelated work. Session 32, the other candidate home, already closed. | USER_EXPLICIT 2026-10-16 'accept all' |
| D-56 | Who makes the packaged `mcp-server` dependencies present (bundle or ship `node_modules`) and proves `MCP_ENTRY_PROBE` starts? | human | A new MEU-92 `dist-mcp-server-bundle` in Session 31b after MEU-71: an `esbuild` bundle the packaged app ships as `resources/mcp-server`, with `MCP_ENTRY_PROBE` on a built `win-unpacked` tree as a pass condition (plan Decision Brief option 1) | Human-approved | The accepted triage D-50 assumed MEU-72 kept this, but MEU-72 closed with it out of scope (2026-10-14-tts-engine-runtime `implementation-plan.md:418`), so it has no owner. Recommended: a new MEU in Session 31b next to MEU-71, with `MCP_ENTRY_PROBE` on a built `win-unpacked` tree as a pass condition (p7 RULE-1). Mat accepted the plan's Decision Brief recommendation. | USER_EXPLICIT 2026-10-16 'Accept' (item 2 of "1. increase budget to 20M 2. Accept 3. approved as proposed") |

Carry-forward: every row above appears in each consuming session's reflection `### Decisions Log` with stage `grouping` (Session 31 carries D-1, D-2, D-6, D-7; Session 31b carries D-1, D-2, D-6, D-7, D-55, D-56; Sessions 32–39 carry D-1, D-3, D-4, D-6; Session 35 also D-5).

---

## 9. Scoping review criteria (D-6)

The independent MEU scoping review checks this proposal against these criteria; a blocking finding cites one of them.

> **Status 2026-10-09: not yet run.** Ledger loop `s31-39-grouping-scoping-2026-10-09` is open (0 of 2 rounds used). The Codex dispatch stopped before any provider call with `overlay_not_validated`: the shared `P:/.agent/model-registry.json` changed again (overlay `ad9a09de…`, registry `a7c95972…`, `TOOLING-SHARED-REGISTRY-COUPLING`). Revalidating rewrites `.agent/model-registry.local.json`, a Session 30 `GATED_PATHS` file, so the review runs after Session 30's approval; the fallback reviewer is Mat (PROFILE B4).

- **AC-1** Every open or candidate known issue in `known-issues.yaml` maps to exactly one MEU or a named non-MEU disposition (§1 traceability), with no issue in two MEUs.
- **AC-2** Each MEU is one coherent change with its own TDD cycle: not two unrelated changes, and not so large that one plan cannot carry it.
- **AC-3** Every MEU's dependencies are registered MEUs, no session schedules an MEU before its prerequisites, and the critical path in §2 matches `meu-status.yaml`.
- **AC-4** Sessions follow one-project-per-session and shared-file continuity; split candidates are flagged; nothing P2 waits behind P4 work without a stated reason.
- **AC-5** Every build-plan row in the 03/04/07/09 homes has a source label (`Spec` / `Local Canon` / `Research-backed` / `Human-approved`) that matches the recorded decision (D-40 to D-69) and does not widen it.
- **AC-6** No Human-approved rule is reversed or amended without a recorded human ruling (D-49, D-51, D-61 to D-65, D-69).
