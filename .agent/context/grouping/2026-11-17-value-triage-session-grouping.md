# 2026-11-17 Value triage · Session grouping

> **Source:** the second 2026-11-17 issue triage of `.agent/context/known-issues.yaml` (21 issues open or mitigated at the start; all in the §1 traceability table) and Mat's request "run triage and create new session grouping based on what is of most value to the application".
> **Generated:** 2026-11-17
> **Method:**
> - Triage (`.agent/workflows/issue-triage.md`): `discover` found 0 candidates and `verify --deep` no findings (`C:/Temp/av-kit/triage-1117b/discover-scan.txt`, `verify-deep.txt`). Every issue was rechecked against the evidence since the last triage: Session 90's seven full Electron runs (4 failed), Session 82's baseline Python receipt, a read-only caption probe through the library and the product adapter (`caption-probe.txt`, `adapter-probe.txt`), and the code each lead names. D-1125 to D-1130 are stage `triage` entries in their issues' `decision_log`. `bucket` proposed one P4 batch of the two MEU-NEW issues, which Session 94 keeps, and the FP16 issue, which stays with Session 74. `triage --output` rewrote `triage-output.yaml`, and `render --check` is OK.
> - Stage A: two MEUs, MEU-158 and MEU-159, registered in `meu-status.yaml`, band P2 and `pending`, with homes in 06 and 11 and matrix rows 6.22 and 11.14. `meu_status render --check` is green with 158 MEUs.
> - Stage B: the sessions are ordered by value to the application (D-1133): the one high-severity user defect first, then the gate flakes that slow every session, then the audit refresh the caption recovery unblocks, then the Python flake, then the small UI fixes.
> **Origin:** Sessions 89 and 90 closed the previous grouping (`79e3fa5`, `fc87056`) and filed `HELP-F1-BEFORE-LAZY-MOUNT-LOST` and `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT`; Session 90's handoff left its unnamed failing specs "for the next triage to file or fold in". Nothing here is a new capability.
> **Status:** Proposed. This is a reversible draft, not a gate. Mat asked for triage and grouping only, so no plan is created until Mat says which session to start.
> **Parallel work:** none seen. Only the `main` worktree exists, and HEAD is `fc87056`. The highest decision ID in use before this triage was D-1123 (D-1124 was left free by Session 90 and is unused). No Session 91 or later, MEU-158 or later, or D-1125 or later was claimed anywhere.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (issue) | Layer | Depends on |
|-----|------|----------------|-------|------------|
| MEU-158 | `gui-help-f1-after-mount` | `HELP-F1-BEFORE-LAZY-MOUNT-LOST` | renderer (`AppShell.tsx`, `settings-commands.ts`, `HelpCard.tsx`, possibly MEU-157's held delivery in `convert-commands.ts`), E2E | MEU-23, MEU-96, MEU-157 |
| MEU-159 | `gui-downloader-advanced-gap` | `DOWNLOADER-ADVANCED-PANEL-GAP` | renderer (`DownloaderPage.tsx` Advanced disclosure), E2E layout check | MEU-53 |

Build-plan homes, each an anchored section with source-labelled rows:
- [06 §F1 help waits for the page (residual)](../../../docs/build-plan/06-gui.md#help-f1-after-mount-residual)
- [11 §Downloader Advanced gap (residual)](../../../docs/build-plan/11-page-layout.md#downloader-advanced-gap-residual)

Issue → disposition traceability (every issue open or mitigated at the start, 21 in all):

| Issue | Status · category | Disposition |
|-------|-------------------|-------------|
| `TTS-ONNX-FP16-NONFINITE-AUDIO` | open · MEU-NEW P2 | Session 74 (D-797 ship amendment), outside the numbered sessions; MEU-144 held for it (D-801). Not run yet |
| `DOWNLOAD-QUEUE-DRAG-OVER-MISS` | open · TECH-DEBT P3 (was MONITORING P4) | Session 91, no MEU (D-1126). Folds in `convert-queue.test.ts:1182` and `download-queue.test.ts:1319` |
| `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` | open · TECH-DEBT P3 (was MONITORING P4) | Session 91, no MEU (D-1126). Folds in `capture-inbox.test.ts:1601`, `:1658`, `:2001`, `:3496` |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | open · TECH-DEBT P3 (was MONITORING P4) | Session 91, no MEU (D-1126). `capture-inbox.test.ts:1948` (AC-81.11) |
| `MCP-AUDIT-BASELINE-PENDING-CROP` | open · TECH-DEBT P3 | Session 92, no MEU: its blocker is gone (D-1125) |
| `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` | open · TECH-DEBT P3 | Session 92, no MEU: it changes the audit the session runs |
| `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE` | open · TECH-DEBT P3 (was MONITORING P4) | Session 93, no MEU unless the fix is in the product (D-1127) |
| `HELP-F1-BEFORE-LAZY-MOUNT-LOST` | open · MEU-NEW P4 (was unclassified) | MEU-158, Session 94 (D-1128) |
| `DOWNLOADER-ADVANCED-PANEL-GAP` | open · MEU-NEW P4 (was TECH-DEBT P4) | MEU-159, Session 94 (D-1129) |
| `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` | open · TECH-DEBT P4 (was unclassified) | Session 94, no MEU (D-1130) |
| `YOUTUBE-CAPTIONS-IP-BLOCK` | **resolved** (was open · UPSTREAM P2) | Closed by D-1125: captions fetch again from this network; reopen on a new 429 |
| `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` | open · UPSTREAM P3 | Not grouped: no fix planned (D-528). A change is open for Mat (§5); if Mat picks it, it joins Session 92 |
| `TOOLING-SHARED-REGISTRY-COUPLING` | mitigated · TECH-DEBT P2 | Not grouped: one test still reads the machine registry (D-912); it rides the next change to that file |
| `TRANSCRIPT-ADD-CHANNEL-422` | open · MONITORING | Not grouped: watch for a repeat. Its first lead is gone (b216681) |
| `E2E-CLIPBOARD-PRIMER-EMPTY` | open · MONITORING | Not grouped: not seen again |
| `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | open · MONITORING | Not grouped: not seen again |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | mitigated · UPSTREAM | Not grouped: anthropics/claude-code#98256 still open; DIALOG_FALLBACK stays |
| `CAPTURE-JOURNAL-VOLATILE` | open · DEFER | Not grouped: deferred by its own ruling |
| `TTS-JA-ZH-G2P-EXTRAS` | open · DEFER | Not grouped: deferred by its own ruling |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | open · BLOCKED | Not grouped: waits for eSpeak NG on a test machine (Mat's install) |
| `FFMPEG-LIBDVDCSS-BUNDLED` | open · CLOSE | Not grouped: accepted risk (D-266); stays open as the record |

---

## 2. Dependency graph + critical path

```
(D-797 ruling, MEU-144 held) ─────────────────► Session 74 (tts-fp16-guard-ship)
(E2E harness, no MEU) ────────────────────────► Session 91 (e2e-pointer-flakes)
YOUTUBE-CAPTIONS-IP-BLOCK resolved (D-1125) ──► Session 92 (mcp-audit-refresh)
(Python integration suite, no MEU) ───────────► Session 93 (video-tail-frame)
MEU-23, MEU-96, MEU-157 ──► MEU-158 ─┐
MEU-53 ───────────────────► MEU-159 ─┴────────► Session 94 (ui-small-fixes)
```

Every MEU prerequisite is approved (`meu_status next` lists MEU-158 and MEU-159 as unblocked), and neither depends on the other.

**Critical path:** none. The order in §5 is a value order, not a dependency chain.

**Soft order (shared files, not dependencies):**
- `ui/tests/e2e/`: Session 91 edits the drag and capture specs; Session 94 adds F1 and layout specs. Session 94 runs after Session 91's commit so its gate runs on the steadier suite.
- `mcp-server/`: Session 92 only, unless Mat picks the action-text change (§5), which then lands in Session 92 before its baseline.
- `tests/integration/`: Session 93 only.

---

## 3. Recommended grouping — Session 74 and 4 new sessions (91–94)

### Session 74 — `tts-fp16-guard-ship` (MEU-144 at its plan gate) · P2

- **Layer / files:** as its prompt says (`C:/Temp/av-kit/session-74-prompt.md`): how the guarded FP16 graph Session 73 measured reaches a user who picks ONNX FP16.
- **Covers:** `TTS-ONNX-FP16-NONFINITE-AUDIO`, the only high-severity defect a user can hit.
- **Why first:** Mat ruled to ship it (D-797), the measurement is done (149 of 149 guarded jobs pass), and it is the only open issue that loses a user's work.
- **Gate:** at its plan gate Mat confirms the MEU registration and picks the delivery route by Decision Brief. The prompt's HEAD (`6813232`) and queue facts are stale; the plan re-reads them.
- **Cloud/local:** local (packaged build, sentence smoke).
- **Token estimate:** calibrate against Session 73 `tts-fp16-phase-guard` and Session 52 `tts-load-fp16`.
- **Split flag:** no.

### Session 91 — `e2e-pointer-flakes` (no MEU) · P3

- **Layer / files:** `ui/tests/e2e/download-queue.test.ts`, `convert-queue.test.ts` (drag), `capture-inbox.test.ts` (real-pointer specs, AC-66.14, AC-81.11 launch and teardown), `electron-app.ts`, and any renderer code a found race lives in.
- **Covers:** `DOWNLOAD-QUEUE-DRAG-OVER-MISS`, `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE`, `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG`, and Session 90's unnamed failing specs folded into them (D-1126).
- **Why grouped:** one symptom: Electron specs that pass alone and fail under full-suite load. 4 of Session 90's 7 full runs failed on them, so every session's gate pays a rerun.
- **Order:** reproduce under load first (Session 90's `load-run.py` pattern), then the drag overshoot, then the pointer origin, then the launch hang.
- **Gate:** no retries and no raised timeouts; a fix waits on a real condition. Any assertion change is named in the plan (M-7). If a race is in the product, the plan registers an MEU for it.
- **Cloud/local:** local (Electron E2E under load).
- **Token estimate:** calibrate against Session 90 `test-run-reliability` and Session 78 `e2e-harness-hardening`.
- **Split flag:** yes, if reproduction shows the launch hang has a separate cause; it then becomes its own session.

### Session 92 — `mcp-audit-refresh` (no MEU) · P3

- **Layer / files:** `mcp-server/` audit runner (census network proofs), `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json`, `BASELINE_PENDING` and `.agent/context/MCP/mcp-tool-audit-report.md`.
- **Covers:** `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT`, then `MCP-AUDIT-BASELINE-PENDING-CROP`.
- **Why grouped:** the census fix changes the audit, and the authoritative run that follows records `avkit_capture.crop` and empties `BASELINE_PENDING` in the same change.
- **Why now:** the caption block that stopped a clean authoritative run has lifted (D-1125). If it returns before the session starts, the session waits.
- **Gate:** `--update-baseline` only from an authoritative Windows run with clean cleanup and no regression (BASELINE_UPDATE_RULE). The baseline is an MCP contract record; any tool-shape change in it is Mat's (M-4).
- **Cloud/local:** local (authoritative audit on the Windows host).
- **Token estimate:** calibrate against the 2026-10-01 `mcp-live-audit` session and Session 59 `capture-crop-copy`.
- **Split flag:** no.

### Session 93 — `video-tail-frame` (no MEU) · P3

- **Layer / files:** the real-ffmpeg frame-grab tests (`test_ac_134_10_*` under `tests/integration/`), and the media adapter's frame grab if the cause is there.
- **Covers:** `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE`.
- **Why alone:** a Python and ffmpeg cause with no file shared with the other sessions.
- **Order:** log the grab's ffmpeg stderr and the clip duration near the tail, reproduce, then fix.
- **Gate:** if the fix is in the product (a user grab near a clip's end can fail too), the plan registers an MEU (D-1127).
- **Cloud/local:** local (full Python suite under load).
- **Token estimate:** calibrate against Session 90 `test-run-reliability` (its Python waits).
- **Split flag:** no.

### Session 94 — `ui-small-fixes` (MEU-158, MEU-159) · P4

- **Layer / files:** `AppShell.tsx`, `settings-commands.ts`, `HelpCard.tsx` (F1), `DownloaderPage.tsx` (Advanced), `ui/scripts/electron-vite-dev.mjs` and `ui/package.json` (preview).
- **Covers:** `HELP-F1-BEFORE-LAZY-MOUNT-LOST` (MEU-158), `DOWNLOADER-ADVANCED-PANEL-GAP` (MEU-159), `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` (no MEU).
- **Why grouped:** three small renderer and dev-script fixes, each with its own Electron proof. The bucket tool proposed the two MEUs together.
- **Order:** MEU-158 (reuses MEU-157's held delivery while it is fresh) → MEU-159 → the preview script.
- **Gate:** MEU-159's cause is measured before any change. The README screenshot is retaken only if Mat asks.
- **Cloud/local:** local (Electron E2E).
- **Token estimate:** calibrate against Session 89 `queue-convert-fixes`.
- **Split flag:** no.

---

## 4. Plan-creation pathway

Mat asked for triage and grouping only, so no plan is made yet. When Mat names a session, `/create-plan` runs for it, followed by its Codex plan review. Each plan re-reads its MEU's build-plan home and the issues it closes. The no-MEU sessions plan as Sessions 78 and 90 did: the plan names the issues it closes, and no MEU status changes.

1. Session 74: its existing prompt (`C:/Temp/av-kit/session-74-prompt.md`), refreshed for HEAD
2. `/create-plan e2e-pointer-flakes` → no MEU
3. `/create-plan mcp-audit-refresh` → no MEU
4. `/create-plan video-tail-frame` → no MEU
5. `/create-plan ui-small-fixes` → MEU-158, MEU-159

---

## 5. Prerequisite gate

- **Queue (D-1133):** Session 74, then 91, 92, 93 and 94.
- **Session 74:** Mat confirms the MEU registration and picks the delivery route at its plan gate.
- **Session 92:** captions still fetch from this network at its start.
- **Open for Mat, no id yet:** whether to change what Claude Code agents see of each MCP action (`MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL`). This changes the MCP tool shape (M-4). Recommendation A: add one line per action to each tool's top-level description and keep the full text in `_meta`, landing in Session 92 before its baseline. B: move the full text into the description. C: leave it (D-528).
- **Not for a session:** `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` waits for Mat to install eSpeak NG on a test machine.
- No branch or worktree; main only. The coordinator commits each session after its execution review and does not push.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 74 | `tts-fp16-guard-ship` | MEU-144 (held) | P2 | proposed | — |
| 91 | `e2e-pointer-flakes` | — | P3 | proposed | — |
| 92 | `mcp-audit-refresh` | — | P3 | proposed | — |
| 93 | `video-tail-frame` | — | P3 | proposed | — |
| 94 | `ui-small-fixes` | MEU-158, MEU-159 | P4 | proposed | — |

The Band column is the session's queue priority. Both new MEUs are registered in band P2, as the earlier triage residuals were; a session band below P2 orders the queue and changes no register field.

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Session 74:** Session 73 `tts-fp16-phase-guard` and Session 52 `tts-load-fp16`.
- **Session 91:** Session 90 `test-run-reliability` and Session 78 `e2e-harness-hardening`.
- **Session 92:** the 2026-10-01 `mcp-live-audit` session and Session 59 `capture-crop-copy`.
- **Session 93:** Session 90 `test-run-reliability`.
- **Session 94:** Session 89 `queue-convert-fixes`.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1131 | Triage the register and group what it leaves by value to the application? | human | Yes. D-1125 to D-1130 written; MEU-158 and MEU-159 registered; Session 74 and Sessions 91 to 94 grouped and ordered by value. No plan is made until Mat names a session. | Human-approved | Mat asked for exactly this, and for no planning or execution. | USER_EXPLICIT 2026-11-17 "run triage and create new session grouping based on what is of most value to the application" |
| D-1132 | Which work shares a session, and does the debt with no MEU get one? | autonomous | Session 91: the three Electron load flakes. Session 92: the two audit issues. Session 93: the Python tail-frame flake alone. Session 94: MEU-158, MEU-159 and the preview script. The TTS FP16 issue stays with Session 74. No MEU for test or tooling debt; a plan registers one if a cause is in the product. | Local Canon | Test and tooling debt has run with no MEU since Sessions 78, 79 and 90 (D-815, D-1103). The Electron flakes share one symptom and one reproduction method; the audit fix and the baseline land in one change. One session for all P3 debt lost: Electron, MCP and ffmpeg share no file and would widen one review. The bucket tool proposed the two MEUs together. Two-way. | — |
| D-1133 | Queue order by value to the application? | autonomous | Session 74, then 91, 92, 93 and 94. | Local Canon | Session 74 fixes the only high-severity user defect and Mat has ruled to ship it (D-797). Session 91 next: the flakes failed 4 of 7 full runs and cost every later session a rerun, so they also speed Sessions 92 to 94. Session 92 then, while captions work (it closes two P3 issues and records the crop tool). Session 93 is a P3 test flake with a possible product cause. Session 94 is P4 polish. Putting 91 first lost: it is test speed, and 74 is a user's audio. Two-way: one message from Mat reorders it. | — |

Carry-forward: the closeout validator reads every §8 row of the declared grouping through `--decision-source` on this file, so a session's reflection does not restate them; its `### Decisions Log` lists only that session's own reversible autonomous choices (HDP §6).

- Session 74 carries D-1131 and D-1133, and its own D-797 and D-801.
- Sessions 91 to 94 carry D-1131, D-1132 and D-1133.
