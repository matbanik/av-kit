# 2026-10-17 GUI shell and TTS sideload · Session grouping

> **Source:** `.agent/context/triage-output.yaml` from `/issue-triage` on 2026-10-17 (Mat's four GUI reports filed as five issues, the seven Session 32 candidates promoted and classified). Mat ruled the three human questions on 2026-10-17 (palette D-87, Appearance D-88, shortcuts D-89); the agent rulings are in `known-issues.yaml` `enrichment.decision_log` D-76 to D-86.
> **Generated:** 2026-10-17
> **Method:** `/session-grouping` Stage A (issues → MEU-93–98, registered in `meu-status.yaml`, `render --check` green; build-plan homes in 06 and 03; matrix rows 3.11 and 6.8–6.12) + Stage B (MEUs → Sessions 40–42).
> **Origin:** The 2026-10-09 grouping (Sessions 31–39) is planned or executed. The new batch is Mat's walkthrough of the app shell (path fields, Light theme, command palette, shortcuts) plus one TTS model defect found in Session 32.
> **Status:** Active — reversible draft, not a gate. Nothing here approves a plan or authorizes execution.
> **Parallel work:** Session 31b (approved; merged to `main` on 2026-10-24, so the §5 prerequisite is met) also edits `06-gui.md`, `gui-actions-index.md`, `build-priority-matrix.md` and `meu-status.yaml`, and owns MEU-92 (§5, §8 D-96).

---

## 1. MEU / scope summary

| MEU | Slug | Covers (known issues) | Layer | Depends on |
|-----|------|-----------------------|-------|------------|
| MEU-93 | `gui-path-fields` | `GUI-CONVERT-OUTPUT-NO-BROWSE` | ui (PathRow, Convert, TTS) | MEU-33, MEU-22 |
| MEU-94 | `gui-theme-reactive-selects` | `GUI-LIGHT-THEME-SELECT-STALE-DARK` | ui (SelectInput/G30, `lib/theme.ts`, boot) | MEU-19, MEU-23 |
| MEU-95 | `gui-shortcut-binding` | `GUI-SHORTCUTS-ADVERTISED-UNBOUND` | ui (AppShell, command registry) | MEU-19, MEU-69 |
| MEU-96 | `gui-command-palette-curation` | `GUI-COMMAND-PALETTE-CURATION` | ui (CommandPalette, `*-commands.ts`, gui-actions-index) | MEU-95, MEU-23 |
| MEU-97 | `gui-common-shortcuts` | `GUI-KEYBOARD-SHORTCUTS-COMMON` | ui (registry, pages, tooltips) | MEU-95, MEU-96 |
| MEU-98 | `svc-tts-sideload-load` | `MODEL-SIDELOAD-LOAD-500` | core + infra (models service, TTS adapter) | MEU-12, MEU-75 |

Findings → MEU traceability (every open, mitigated or dismissed row accounted for):

| Known issue | Category | MEU / disposition |
|-------------|----------|-------------------|
| MEU-93 … MEU-98 rows above | MEU-NEW | as listed |
| `GUI-AUDIT-CLIPBOARD-RESOLVER` | TECH-DEBT | rider in Session 41 (§8 D-99) |
| `TTS-SPACY-SYSPATH-STALE-DIR` | TECH-DEBT | rider in Session 42 (§8 D-99) |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | MEU-EXPAND (MEU-74) | local evidence stage in Session 42 (§8 D-100) |
| `MCP-SETUP-PROMPT` | MEU-NEW | MEU-71, Session 31b (2026-10-09 grouping D-55) |
| `MCP-PACKAGED-ENTRY-UNREACHABLE` | MEU-NEW | MEU-92 `dist-mcp-server-bundle`, Session 31b (2026-10-09 grouping D-56); resolves on the 31b merge |
| `QUEUE-PILL-TOKEN-DRIFT` | MEU-NEW | superseded by Session 31b amendment A-1; its `meu_links: MEU-92` on main is void (§8 D-96) |
| `FFMPEG-GPL-BUILD` | MEU-NEW | no MEU yet; needs Mat's licensing ruling (§8 D-101) |
| `FFMPEG-PIN-URL-404` | BLOCKED | waits on `FFMPEG-GPL-BUILD` |
| `INSTALLER-SHIPS-FFMPEG-ZIP`, `FETCH-FFMPEG-EXIT-CODES` | TECH-DEBT | FFmpeg fetch debt batch, with the re-pin once D-101 is ruled |
| `NOTICES-SPACY-TRANSITIVE` | DOCUMENTATION | not an MEU; rides with the D-101 licensing work |
| `TTS-JA-ZH-G2P-EXTRAS` | MEU-NEW (P4) | unplaced; next triage (§8 D-102) |
| `TOOLING-TRIAGE-CLI-CP1252`, `TOOLING-SHARED-REGISTRY-COUPLING`, `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE`, `UI-ELECTRON-LAZY-INSTALL-RACE`, `E2E-ELECTRON-LAUNCH-FLAG`, `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` | TECH-DEBT | not MEUs; the standing debt batch (2026-10-09 grouping D-3, plus the CP1252 row) |
| `DOWNLOAD-QUEUE-DRAG-OVER-MISS`, `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` | MONITORING | reopen with diagnostics on the next miss |
| `CAPTURE-JOURNAL-VOLATILE` | DEFER | stays deferred |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | UPSTREAM (mitigated) | not an MEU; track anthropics/claude-code #98978 |
| `TTS-VOICE-SELECT-LAYOUT-JUMP` | dismissed | not reproduced (Mat, 2026-10-09) |

Build-plan homes (Stage A3, source-labelled ACs): [06 §Path fields](../../../docs/build-plan/06-gui.md#path-fields-residual), [§Theme-reactive selects](../../../docs/build-plan/06-gui.md#theme-reactive-selects-residual), [§Shortcut binding](../../../docs/build-plan/06-gui.md#shortcut-binding-residual), [§Command palette curation](../../../docs/build-plan/06-gui.md#command-palette-curation-residual), [§Common shortcuts](../../../docs/build-plan/06-gui.md#common-shortcuts-residual); [03 §TTS sideload load](../../../docs/build-plan/03-service-layer.md#tts-sideload-load-residual). The matrix also gained the missing rows of five already registered MEUs (§8 D-97).

---

## 2. Dependency graph + critical path

```
MEU-19, MEU-23 ──► MEU-94 ─┐
MEU-33, MEU-22 ──► MEU-93 ─┴──────────────────────────── Session 40  gui-theme-path-fields

MEU-19, MEU-69 ──► MEU-95 ──► MEU-96 ──► MEU-97 ──────── Session 41  gui-keyboard-palette   (after Session 40: shared AppShell, lib/theme.ts, ConvertPage)
                     │      (MEU-23)         ▲
                     └───────────────────────┘

MEU-12, MEU-75 ──► MEU-98 ─────────────────────────────── Session 42  tts-sideload-load
```

All prerequisites outside the batch (MEU-12, 19, 22, 23, 33, 69, 75) are approved.

**Critical path:** MEU-95 → MEU-96 → MEU-97, the only hard chain. MEU-96's palette lists the registry chords that MEU-95 binds, and MEU-97's chords are registry entries bound by MEU-95's map that must not collide with MEU-96's Ctrl+Shift+D/L.

**Soft order (shared files, not dependencies):**
- MEU-94 before MEU-96. MEU-96's Appearance commands set `ui.theme` through the path MEU-94 makes reactive. Both edit `lib/theme.ts` and the AppShell theme listener.
- MEU-93 before MEU-97. Both edit `ConvertPage.tsx`, and MEU-97 adds the Ctrl+O hint to Convert's Browse files button.

**Parallel tiers:** Session 42 shares no files with Sessions 40–41 and could run in either slot. It goes last on priority (P3).

---

## 3. Recommended grouping — 3 sessions (40–42)

### Session 40 — `gui-theme-path-fields` (MEU-94, MEU-93) · P2

- **Layer / files:**
  - Theme: `components/ui/SelectInput.tsx` (`getG30Styles`), `lib/theme.ts` (a reactive hook on `THEME_CHANGED_EVENT`), `ConsolePanel.tsx` (duplicate removed), boot theme apply (`index.html` / `main.tsx`).
  - Paths: `components/ui/PathRow.tsx`, `features/converter/ConvertPage.tsx`, `TTSPage.tsx` output path.
  - Tests and index: Settings/TTS/Convert Electron specs, `gui-actions-index.md` (`convert-output-dir-browse`).
- **Why grouped:** both are shared-primitive fixes ("one control, one behaviour everywhere") with the same Electron wave across Settings, TTS and Convert. Neither touches the keyboard or palette.
- **Order:** MEU-94 (P2, visible on every page) → MEU-93.
- **Cloud/local:** the unit work can run in the container. The both-theme and cold-boot Electron checks are local (`ELECTRON_RUN_AS_NODE` cleared).
- **Token estimate:** calibrate against Session 31 `gui-polish-residuals` (MEU-69/70, shell polish over several pages) and Session 34 `capture-chrome` (a shared primitive plus its consumers). Expect smaller than either.
- **Split flag:** no.

### Session 41 — `gui-keyboard-palette` (MEU-95, MEU-96, MEU-97) · P2

- **Layer / files:**
  - Shell: `registry/commandRegistry.ts` (keydown map from `shortcut`), `AppShell.tsx` keydown, `CommandPalette.tsx` (context-aware list), `*-commands.ts` (labels, ConfirmModal on Clear/Cancel, Appearance commands).
  - Pages: `NavRail.tsx` and page buttons (tooltips, `aria-keyshortcuts`).
  - Index and spec: `gui-actions-index.md` (Palette column amendment), 06 §Command palette amendment.
  - Rider: `ui/tests/unit/gui-actions-audit.test.ts` resolver and two Settings index rows (`GUI-AUDIT-CLIPBOARD-RESOLVER`).
- **Why grouped:** a hard chain through one registry, one keydown map and one index file. Splitting it across sessions would amend `gui-actions-index.md` and the AC-23.20 audit three times.
- **Order:** MEU-95 → MEU-96 → MEU-97, with the rider alongside MEU-96 (the same audit and index edit).
- **Cloud/local:** unit in the container; the Electron chord and palette-confirm specs are local.
- **Token estimate:** calibrate against `p6-gui-shell` (MEU-19, AppShell and registry) and `p6-gui-settings-help` (MEU-23, palette and the AC-23.20 audit).
- **Split flag:** **yes, candidate.** MEU-96 is the largest (context model, ConfirmModal wiring, renames, spec amendment). If the MEU-96 handoff passes ~50% context, run MEU-97 as 41b.

### Session 42 — `tts-sideload-load` (MEU-98) · P3

- **Layer / files:**
  - Code: `packages/core` `services/models.py` (`list_available` marks the sideload downloaded, `load` resolves the path); `packages/infrastructure` `tts/adapter.py` (`tts.load_failed` around `_require_weight_path`).
  - Rider: `tts/assets.py` / `wiring.py` spaCy `sys.path` swap on a `models_directory` change (`TTS-SPACY-SYSPATH-STALE-DIR`).
  - Tests: the API contract `GET /models/downloaded` then `POST /models/load`.
  - Local evidence stage: live eSpeak NG generates (AC-74.11, `TTS-ESPEAK-LIVE-PATH-UNVERIFIED`).
- **Why grouped:** all three sit on the TTS model directory and readiness path. The eSpeak stage is evidence for the approved MEU-74, not new scope.
- **Cloud/local:** Python in the container. The eSpeak stage needs eSpeak NG installed on the Windows machine. If it is absent, the issue stays open and the session still closes.
- **Token estimate:** calibrate against the MEU-75 half of Session 35 `tts-voice-panel`. Expect smaller.
- **Split flag:** no.

---

## 4. Plan-creation pathway

Multi-session fan-out. Run `/create-plan` once per session, in order, each reading this proposal for scope:

1. `/create-plan gui-theme-path-fields` → MEU-94, MEU-93
2. `/create-plan gui-keyboard-palette` → MEU-95, MEU-96, MEU-97 (+ `GUI-AUDIT-CLIPBOARD-RESOLVER`)
3. `/create-plan tts-sideload-load` → MEU-98 (+ `TTS-SPACY-SYSPATH-STALE-DIR`, `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` local stage)

Each plan follows `.agent/docs/cloud-local-collaboration.md`: gate location and reviewer route at plan time, the `ENV_BOUND_*` census, and both gate scripts built from one stage list.

---

## 5. Prerequisite gate

- **Merge Session 31b to main first** for Sessions 40 and 41. 31b edits `06-gui.md`, `gui-actions-index.md`, `build-priority-matrix.md` (rows 7.3 and 7.5) and `meu-status.yaml` (MEU-92).
  - Expected conflicts are tail-only: keep both sides, with MEU-92 before MEU-93 in `meu-status.yaml` and rows 7.3/7.5 alongside this grouping's rows in the matrix. Then re-run `meu_status.py render --check`.
  - The merge also resolves `QUEUE-PILL-TOKEN-DRIFT` (§8 D-96).
- Session 42 touches none of those files, but one project per session still applies.
- The scoping review (§9) runs before the first `/create-plan`, subject to §8 D-103.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 40 | `gui-theme-path-fields` | MEU-94, MEU-93 | P2 | approved | `docs/execution/plans/2026-10-24-gui-theme-path-fields/` |
| 41 | `gui-keyboard-palette` | MEU-95, MEU-96, MEU-97 | P2 | approved | `docs/execution/plans/2026-10-26-gui-keyboard-palette/` |
| 42 | `tts-sideload-load` | MEU-98 | P3 | approved | `docs/execution/plans/2026-10-26-tts-sideload-load/` |

---

## 7. Token calibration sources

- Session 31 `gui-polish-residuals` (MEU-69/70) and Session 34 `capture-chrome` (MEU-80/81) — Session 40.
- `p6-gui-shell` (MEU-19) and `p6-gui-settings-help` (MEU-23) — Session 41.
- Session 35 `tts-voice-panel`, MEU-75 half — Session 42.
- Sessions 31–35 for the cloud/local gate overhead (one or two Windows round trips per session).

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-94 | Do MEU-93 to MEU-97 run as one GUI session, as triage D-80 to D-84 batched them? | autonomous | No: two sessions. Session 40 has the primitives (MEU-94, MEU-93) and Session 41 has the keyboard/palette chain (MEU-95–97). | Local Canon | Triage batched by component, and the batch is roughly 15 files plus three Electron waves, too large for one plan. The seam is clean: 93/94 are shared-primitive fixes with no keyboard work, and 95–97 is the only hard chain. Two-way: the plans can still merge if Session 40 turns out small. | — |
| D-95 | Session order | autonomous | 40 → 41 → 42 | Local Canon | Both GUI sessions are P2. Session 40 goes first because MEU-96's Appearance commands use the theme path MEU-94 rewrites, and MEU-97 edits the `ConvertPage.tsx` that MEU-93 changes. Running 41 first would land the most user-harmful item, the palette Clear without a confirm, a session sooner. It lost because it would then rework `lib/theme.ts` twice. Session 42 is P3 and independent. Two-way. | — |
| D-96 | What happens to `QUEUE-PILL-TOKEN-DRIFT` and its MEU-92 on main? | autonomous | Out of this grouping. It is superseded by Session 31b amendment A-1, and MEU-92 is 31b's `dist-mcp-server-bundle`. No edit on main; the 31b merge resolves it. | Human-approved (via 31b) | The 31b worktree records Mat's D-90 (keep the 61243baf palette) and D-91 A (decouple from the Zorivest checkout; AC-41.3 reads `_inspiration/zorivest/globals.css`). This overturns main's triage D-72/D-74 and leaves the queue-pill MEU nothing to do. Registering it here would collide with 31b's MEU-92. Surfaced to Mat in the report. | 31b plan D-90, D-91 (Mat) |
| D-97 | Backfill the matrix rows that registered MEUs were missing? | autonomous | Yes: 3.9 MEU-77, 3.10 MEU-78, 4.4 MEU-76, 9.21 MEU-88, 9.22 MEU-89. Row 7.3 (MEU-71) is left to the 31b merge. | Local Canon | `meu-status.yaml` already gave these MEUs matrix items (the 2026-10-09 D-1 deferral never landed). Without the rows, the new 3.11 row would sit after a gap. Two-way. | — |
| D-98 | Do D-86's matrix row and log level still hold? | autonomous | Row 3.9 → 3.11; "warning level" → the adapter's existing error-level `tts.load_failed`. Recorded in D-86's reasoning and in MEU-98's description. | Local Canon | 3.9 and 3.10 belong to MEU-77/78. The adapter already logs every other load failure as `tts.load_failed` (`adapter.py:123-124`), and a separate warning event for one cause would split the log query. Two-way. | — |
| D-99 | Which TECH-DEBT rows ride with an MEU session? | autonomous | `GUI-AUDIT-CLIPBOARD-RESOLVER` → Session 41; `TTS-SPACY-SYSPATH-STALE-DIR` → Session 42. Other debt stays in the debt batch. | Local Canon | Each rider edits a file its session already changes: the AC-23.20 audit and `gui-actions-index.md` (MEU-96), and the TTS models directory (MEU-98). Their triage notes already propose these homes. Two-way. | — |
| D-100 | Where does `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` (MEU-EXPAND of approved MEU-74) run? | autonomous | A local evidence stage in Session 42; MEU-74 scope reopens only if the live run fails | Local Canon | It needs only eSpeak NG installed and the AC-74.11 generates run, not new code. Session 42 is the next TTS session. A failure becomes a new issue against MEU-74 rather than widening MEU-98. Two-way. | — |
| D-101 | FFmpeg licence posture: an LGPL build with Convert's software encoders changed, or keep GPL with full source-offer compliance? | open | — | — | One-way for distribution: a released installer cannot be unshipped. It decides the build `FFMPEG-PIN-URL-404` re-pins to and Convert's H.264/H.265 fallback. Not an agent call. No MEU is registered until Mat rules. | — |
| D-102 | Register an MEU for `TTS-JA-ZH-G2P-EXTRAS` now? | autonomous | No; leave it for the next triage | Local Canon | P4, and the misaki ja/zh extras are hundreds of MB with a new licence review. That review should follow D-101's licensing ruling, not run ahead of it. Two-way. | — |
| D-103 | When does the independent MEU scoping review run, given that the workflow's exit criterion says "no review dispatched"? | human | A separate Codex dispatch after Mat confirms the grouping, before the first `/create-plan` (the recommendation) | Human-approved | Triage D-85 (accepted by Mat) and the 2026-10-09 D-6 put the Codex scoping review on this grouping draft for batches of 3+ MEUs (this one has 6). The session-grouping exit criterion forbids dispatching inside the workflow. Recommended: dispatch it as a separate step right after Mat confirms, before the first `/create-plan`. | USER_EXPLICIT 2026-10-24 'yes go ahead' |

Carry-forward: each row appears in its consuming session's reflection `### Decisions Log` with stage `grouping`.
- Sessions 40–42 carry D-94, D-95 and D-103.
- Session 41 also carries D-99.
- Session 42 also carries D-98, D-99 and D-100.
- D-96, D-97, D-101 and D-102 carry to the next `/issue-triage`.

---

## 9. Scoping review criteria (D-6, D-85)

The independent MEU scoping review checks this proposal against these criteria; a blocking finding cites one of them.

> **Status 2026-10-24: approved in round 2** (ledger loop `s40-42-grouping-scoping-2026-10-24`, dispatched after Mat confirmed the grouping, §8 D-103). Round 1 (changes_required): AC-1 to AC-4 and AC-6 passed; one blocking AC-5 finding (F1: MEU-95's "no binding exists outside the registry" widened D-78 to Capture's F2 and zoom keys). Corrected in `06-gui.md` §Shortcut binding (residual): the invariant is limited to the AppShell keydown map, and Capture's bindings stay as D-89 collision constraints. Mat continued the loop (+2.5M tokens, "continue the scoping review"); round 2 (Codex, closure check) approved with F1 fixed and no blocking finding.

- **AC-1** Every open, mitigated or dismissed known issue in `known-issues.yaml` maps to exactly one MEU or a named non-MEU disposition (§1 traceability), with no issue in two MEUs. `QUEUE-PILL-TOKEN-DRIFT` is the one deliberate exception, recorded in D-96.
- **AC-2** Each MEU is one coherent change with its own TDD cycle: not two unrelated changes, and not so large that one plan cannot carry it.
- **AC-3** Every MEU's dependencies are registered MEUs, no session schedules an MEU before its prerequisites, and the critical path in §2 matches `meu-status.yaml`.
- **AC-4** Sessions follow one-project-per-session and shared-file continuity; split candidates are flagged; nothing P2 waits behind P3/P4 work without a stated reason.
- **AC-5** Every build-plan row in the 06 and 03 homes has a source label (`Spec` / `Local Canon` / `Research-backed` / `Human-approved`) that matches the recorded decision (D-76 to D-89) and does not widen it.
- **AC-6** No Human-approved rule is reversed or amended without a recorded human ruling (D-85, D-87, D-88, D-89; 31b's D-90/D-91 for D-96).
