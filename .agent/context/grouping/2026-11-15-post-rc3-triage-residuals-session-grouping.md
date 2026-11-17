# 2026-11-15 Post-rc.3 triage residuals · Session grouping

> **Source:** the 2026-11-15 issue triage of `.agent/context/known-issues.yaml` (45 issues not resolved: 42 open, 1 mitigated, 2 dismissed; all in the §1 traceability table) and Mat's request "@.agent/skills/issue-triage/ and create new session grouping".
> **Generated:** 2026-11-15
> **Method:**
> - Triage (`.agent/workflows/issue-triage.md`) wrote D-801 to D-812 as stage `triage` entries in the register's `decision_log`, and added `meu_links` to the 17 issues now mapped. No category changed. `issue_triage render --check` is OK (`C:/Temp/av-kit/ki-check.txt`), and `triage --output` rewrote `triage-output.yaml` (`C:/Temp/av-kit/triage-out.txt`).
> - The `verify --deep` and `discover` scans gave 51 findings and 14 candidates, all noise of the kinds `TOOLING-TRIAGE-SCANNER-FALSE-FINDINGS` already records; the register was restored to its pre-scan bytes (D-812).
> - Stage A: ten MEUs, MEU-145 to MEU-154, registered in `meu-status.yaml`, all band P2 and `pending`. `meu_status render --check` is green with 153 MEUs (`C:/Temp/av-kit/meu-check.txt`). Homes are anchored sections in 03, 04, 06, 08 and 09, with matrix rows 3.22 to 3.24, 4.5, 6.18 to 6.20, 8.11, 9.43 and 9.44. MEU-144 and row 3.21 stay held for Session 74's ship MEU (D-801).
> - Stage B: the ten MEUs and the ten debt issues with no MEU are grouped into Sessions 75 to 83.
> **Origin:** rc.3 is released and Sessions 68 to 73 closed the capture editor and the TTS FP16 spike. What is left in the register is small debt filed by those sessions' reviews and closeouts, plus older tooling and E2E debt. Nothing here is a new capability.
> **Status:** Active. This is a reversible draft, not a gate. Nothing here approves a plan or authorizes execution. Mat ruled D-817 on 2026-11-15: option A.
> **Parallel work:** none seen. Only the `main` worktree exists, and HEAD is `6813232` (MEU-127). Session 74 (`tts-fp16-guard-ship`, the D-797 ship amendment) is prompted at `C:/Temp/av-kit/session-74-prompt.md` and sits outside this grouping. The highest decision ID in use before this triage was D-800. No Session 75 or later, MEU-145 or later, or D-801 or later was claimed anywhere.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (issue) | Layer | Depends on |
|-----|------|----------------|-------|------------|
| MEU-145 | `capture-scan-skip-unreadable` | `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` | service (`scan_inbox`), adapter (`probe`) | MEU-36, MEU-84, MEU-130 |
| MEU-146 | `capture-exif-orientation` | `CAPTURE-EXIF-SCANNED-ORIENTATION` | adapter (`probe`, bake, region view) | MEU-35, MEU-36, MEU-128, MEU-129 |
| MEU-147 | `svc-transcript-title-cleaning` | `TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS` | service (`services/transcript.py`), domain guard | MEU-122 |
| MEU-148 | `svc-console-home-short-form` | `CONSOLE-HOME-SCRUB-SHORT-FORM` | service (`services/health.py` `scrub_home`) | MEU-119 |
| MEU-149 | `gui-tts-status-pill-contrast` | `TTS-STATUS-PILL-BELOW-AA-CONTRAST` | renderer (`TTSPage.tsx`, `tts-controls.ts`) | MEU-22, MEU-126 |
| MEU-150 | `svc-tts-output-names-progress` | `TTS-AUDIO-RANDOM-FILE-NAMES`, `TTS-SEGMENTS-LABEL-IS-PROGRESS-SCALE` | service (`services/tts.py`), renderer (`TTSPage.tsx`) | MEU-12, MEU-22, MEU-77 |
| MEU-151 | `gui-settings-draft-baseline` | `SETTINGS-DRAFT-STALE-BASELINE`, `CONVERT-ADVANCED-EDIT-REPLACED` | renderer (`useCaptureSettings.ts`, `ConvertPage.tsx`) | MEU-33, MEU-39, MEU-112 |
| MEU-152 | `convert-queue-labels` | `CONVERT-CUT-TIME-RAW-MS`, `CONVERT-POSITIONS-NOT-RENUMBERED`, `CONVERT-CUT-ENCODER-LABEL` | service (`services/conversion.py`), renderer (`convert-controls.ts`, `ConvertPage.tsx`, `QueueCard.tsx`) | MEU-30, MEU-33, MEU-112, MEU-123 |
| MEU-153 | `api-ready-after-listen` | `BACKEND-READY-BEFORE-LISTEN` | API entry (`cli.py`) | MEU-24 |
| MEU-154 | `gui-ready-line-buffer` | `GUI-READY-CHUNK-BOUNDARY` | main process (`python-manager.ts`) | MEU-108 |

Build-plan homes, each an anchored section with source-labelled rows:
- [03 §Transcript title cleaning (residual)](../../../docs/build-plan/03-service-layer.md#transcript-title-cleaning-residual)
- [03 §Console home short form (residual)](../../../docs/build-plan/03-service-layer.md#console-home-short-form-residual)
- [03 §TTS output names and progress (residual)](../../../docs/build-plan/03-service-layer.md#tts-output-names-progress-residual)
- [04 §READY after listen (residual)](../../../docs/build-plan/04-rest-api.md#ready-after-listen-residual)
- [06 §TTS status pill contrast (residual)](../../../docs/build-plan/06-gui.md#tts-status-pill-contrast-residual)
- [06 §Settings drafts keep edits (residual)](../../../docs/build-plan/06-gui.md#settings-draft-baseline-residual)
- [06 §READY line buffering (residual)](../../../docs/build-plan/06-gui.md#ready-line-buffer-residual)
- [08 §Convert queue labels (residual)](../../../docs/build-plan/08-video-conversion.md#convert-queue-labels-residual)
- [09 §Scan skips unreadable files](../../../docs/build-plan/09-screenshot-capture.md#scan-skips-unreadable-files)
- [09 §EXIF orientation on scan](../../../docs/build-plan/09-screenshot-capture.md#exif-orientation-on-scan)

Issue → disposition traceability (every issue not resolved, 45 in all):

| Issue | Status · category | Disposition |
|-------|-------------------|-------------|
| `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` | open · MEU-NEW | MEU-145, Session 75 (D-802) |
| `CAPTURE-EXIF-SCANNED-ORIENTATION` | open · TECH-DEBT | MEU-146, Session 75 (D-803) |
| `TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS` | open · TECH-DEBT | MEU-147, Session 77 (D-804) |
| `CONSOLE-HOME-SCRUB-SHORT-FORM` | open · TECH-DEBT | MEU-148, Session 77 (D-805) |
| `TTS-STATUS-PILL-BELOW-AA-CONTRAST` | open · TECH-DEBT | MEU-149, Session 80 (D-806) |
| `TTS-AUDIO-RANDOM-FILE-NAMES` | open · TECH-DEBT | MEU-150, Session 80 (D-807) |
| `TTS-SEGMENTS-LABEL-IS-PROGRESS-SCALE` | open · TECH-DEBT | MEU-150, Session 80 (D-807) |
| `SETTINGS-DRAFT-STALE-BASELINE` | open · TECH-DEBT | MEU-151, Session 81 (D-808) |
| `CONVERT-ADVANCED-EDIT-REPLACED` | open · TECH-DEBT | MEU-151, Session 81 (D-808) |
| `CONVERT-CUT-TIME-RAW-MS` | open · TECH-DEBT | MEU-152, Session 81 (D-809) |
| `CONVERT-POSITIONS-NOT-RENUMBERED` | open · TECH-DEBT | MEU-152, Session 81 (D-809) |
| `CONVERT-CUT-ENCODER-LABEL` | open · TECH-DEBT | MEU-152, Session 81 (D-809) |
| `BACKEND-READY-BEFORE-LISTEN` | open · TECH-DEBT | MEU-153, Session 82 (D-810) |
| `GUI-READY-CHUNK-BOUNDARY` | open · TECH-DEBT | MEU-154, Session 82 (D-810) |
| `TOOLING-SHARED-REGISTRY-COUPLING` | open · TECH-DEBT | Session 76, no MEU (D-815) |
| `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE` | open · TECH-DEBT | Session 76, no MEU (D-815) |
| `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` | open · TECH-DEBT | Moved to Session 84 of `2026-11-15-hdp-framework-sync-session-grouping.md`, no MEU (D-822) |
| `CLI-DISPATCH-PLACEHOLDER-FIXTURE` | open · TECH-DEBT | Session 76, no MEU (D-815) |
| `E2E-MAIN-PROCESS-ERRORS-UNWATCHED` | open · TECH-DEBT | Session 78, no MEU (D-815) |
| `E2E-ELECTRON-LAUNCH-FLAG` | open · TECH-DEBT | Session 78, no MEU (D-815) |
| `UI-ELECTRON-LAZY-INSTALL-RACE` | open · TECH-DEBT | Session 78, no MEU (D-815) |
| `CAPTURE-HINT-TEST-PRESENCE-ONLY` | open · TECH-DEBT | Session 78, no MEU (D-815) |
| `TOOLING-TRIAGE-CLI-CP1252` | open · TECH-DEBT | Session 79, no MEU (D-815) |
| `TOOLING-TRIAGE-SCANNER-FALSE-FINDINGS` | open · TECH-DEBT | Session 79, no MEU (D-815, D-812) |
| `INSTALL-FOLDER-NAME-MISMATCH` | open · TECH-DEBT | Session 83, no MEU: the docs and the round-trip script say `Programs\av-kit-ui`; the package name stays (D-811) |
| `TRACKED-FILES-HOLD-HOME-PATH` | open · TECH-DEBT | Session 83, no MEU; a tracked-file check plus the six live files fixed (D-817, ruled A) |
| `TTS-ONNX-FP16-NONFINITE-AUDIO` | open · MEU-NEW | Session 74 (D-797 ship amendment), outside this grouping; MEU-144 held for it (D-801) |
| `DOWNLOAD-QUEUE-DRAG-OVER-MISS` | open · MONITORING | Not grouped: watch for a repeat |
| `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` | open · MONITORING | Not grouped: watch for a repeat |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | open · MONITORING | Not grouped: watch for a repeat; Session 78 notes it if its launch changes touch teardown |
| `TRANSCRIPT-ADD-CHANNEL-422` | open · MONITORING | Not grouped: watch for a repeat |
| `E2E-CLIPBOARD-PRIMER-EMPTY` | open · MONITORING | Not grouped: watch for a repeat |
| `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | open · MONITORING | Not grouped: watch for a repeat |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | mitigated · UPSTREAM | Not grouped: waits on the IDE client |
| `YOUTUBE-CAPTIONS-IP-BLOCK` | open · UPSTREAM | Not grouped: YouTube-side block, mitigated by MEU-115 and MEU-116 |
| `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` | open · UPSTREAM | Not grouped: waits on the MCP clients |
| `CAPTURE-JOURNAL-VOLATILE` | open · DEFER | Not grouped: deferred by its own ruling |
| `TTS-JA-ZH-G2P-EXTRAS` | open · DEFER | Not grouped: deferred by its own ruling |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | open · BLOCKED | Not grouped: waits for eSpeak NG on a test machine |
| `FFMPEG-LIBDVDCSS-BUNDLED` | open · CLOSE | Not grouped: accepted risk (D-266); stays open as the record |
| `MCP-AUDIT-BASELINE-PENDING-CROP` | open · TECH-DEBT | Not grouped: closes at the next release's MCP audit baseline |
| `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` | open · TECH-DEBT | Not grouped: rides the next change under the MCP audit's gated paths |
| `DOWNLOADER-ADVANCED-PANEL-GAP` | open · TECH-DEBT | Not grouped: standing debt, no current consumer |
| `TTS-VOICE-SELECT-LAYOUT-JUMP` | dismissed | Not grouped: dismissed |
| `TTS-PYTORCH-RUNTIME-SETTINGS-DOWNLOAD` | dismissed · CLOSE | Not grouped: dismissed |

---

## 2. Dependency graph + critical path

```
MEU-36, MEU-84, MEU-130 ───────────► MEU-145 ─┐
MEU-35, MEU-36, MEU-128, MEU-129 ──► MEU-146 ─┴── Session 75 (145, 146)
(tooling, no MEU) ─────────────────────────────── Session 76
MEU-122 ───────────────────────────► MEU-147 ─┐
MEU-119 ───────────────────────────► MEU-148 ─┴── Session 77 (147, 148)
(E2E harness, no MEU) ─────────────────────────── Session 78
(triage tool, no MEU) ─────────────────────────── Session 79
MEU-22, MEU-126 ───────────────────► MEU-149 ─┐
MEU-12, MEU-22, MEU-77 ────────────► MEU-150 ─┴── Session 80 (149, 150)
MEU-33, MEU-39, MEU-112 ───────────► MEU-151 ─┐
MEU-30, MEU-33, MEU-112, MEU-123 ──► MEU-152 ─┴── Session 81 (151, 152)
MEU-24 ────────────────────────────► MEU-153 ─┐
MEU-108 ───────────────────────────► MEU-154 ─┴── Session 82 (153, 154)
(docs and guard, no MEU) ──────────────────────── Session 83
```

Every prerequisite outside the batch is approved, and no MEU in the batch depends on another.

**Critical path:** none. Every session can run on its own; the order in §5 is a priority order, not a dependency chain.

**Soft order (shared files, not dependencies):**
- `capture/adapter.py` `probe`: MEU-145 and MEU-146, which is why they share Session 75.
- `TTSPage.tsx`: MEU-149 (pill) and MEU-150 (progress label).
- `ConvertPage.tsx`: MEU-151 (draft) and MEU-152 (positions).
- The READY line: MEU-153 writes it (`cli.py`), MEU-154 reads it (`python-manager.ts`).
- `ui/tests/e2e/`: Session 78 changes every launch site; Sessions 75 and 80 to 82 add no E2E launch of their own unless their plans say so.
- `tools/issue_triage*`: Session 79 only. `tests/tooling/` and `.agent/skills/cli-dispatch/`: Session 76 only, except that Session 84 of `2026-11-15-hdp-framework-sync-session-grouping.md` adds its own test file under `tests/tooling/`.
- `known-issues.yaml` and `06-gui.md`: Session 83 edits the lines that name the home folder; any other session that edits those files runs before or after it, not beside it.

None of the batch shares a file with Session 74, which touches the TTS model assets and the packaging path only.

---

## 3. Recommended grouping — 9 sessions (75–83)

### Session 75 — `capture-inbox-probe` (MEU-145, MEU-146) · P2

- **Layer / files:** `services/capture.py` (`scan_inbox`), `capture/adapter.py` (`probe`, the bake and the region view), the capture routes' error mapping, MCP `capture` `list` through the same service. Tests: unit and API with a non-image named `.png`, a PNG with a damaged IDAT, and JPEG and WebP files tagged 1 to 8, all generated in the test.
- **Why grouped:** both change how the inbox scan reads a file through `probe`, in the same function, and both come from the capture work Sessions 58 and 59 closed. MEU-145 is the only medium-severity user-facing break in the batch: one bad file in the inbox fails the whole list.
- **Order:** MEU-145 → MEU-146. MEU-145 first makes the scan survive a file it can't read; MEU-146 then changes what a readable file records.
- **Gate:** MEU-146's route (write an upright copy, rewrite the file, or keep it and apply the tag wherever pixels are read) is a plan-time Decision Brief (D-803), because the inbox holds the user's own files. MEU-145's skip-or-flag choice is decided at plan time from 09's row.
- **Cloud/local:** local.
- **Token estimate:** calibrate against Session 58 `capture-region-import` and Session 59 `capture-crop-copy` (the capture adapter, service and API with generated images).
- **Split flag:** yes, candidate. If MEU-146's brief picks the apply-the-tag-everywhere route, it touches bake and region code as well; if MEU-145's handoff passes about 50% of context, MEU-146 runs as 75b.

### Session 76 — `tooling-test-hermeticity` (no MEU) · P2

- **Layer / files:** `tests/tooling/test_framework_adoption.py` (the shared registry and resolver, and the `migrated_tree` fixture), `.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1` (the placeholder fixture pair).
- **Covers:** `TOOLING-SHARED-REGISTRY-COUPLING` (P2, medium), `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE`, `CLI-DISPATCH-PLACEHOLDER-FIXTURE`. `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` moved to Session 84 of `2026-11-15-hdp-framework-sync-session-grouping.md` (D-822), which ports upstream's fix to the same function.
- **Why grouped:** each is a tooling test that reads something outside its own fixture: the shared `P:/.agent` registry, the live governance files, or the instantiated project name. Each breaks for a reason the change under test never touched. One theme, one fix pattern (make the fixture hermetic), one test suite.
- **Order:** the registry coupling first (it is the P2 and the widest), then the governance fixture and the dispatch fixture.
- **Gate:** the dispatch fixture comes from the upstream agentic-framework copy. Whether av-kit's copy diverges or the fix goes upstream first is decided at plan time; av-kit never edits `P:/agentic-framework` from this session.
- **Cloud/local:** local (the tests read `P:/` paths today; the session's purpose is to stop that).
- **Token estimate:** calibrate against Session 49b `closeout-register-grammar` (tooling, no MEU, D-280).
- **Split flag:** no.

### Session 77 — `text-scrub-residuals` (MEU-147, MEU-148) · P3

- **Layer / files:** `services/transcript.py` (the `info.title` channel fallback and the stored `TranscriptResult.title`), the D-360 cleaning helper, `services/health.py` (`scrub_home`), and through it `scrub_line` in `services/download.py`.
- **Why grouped:** both finish a text-cleaning rule that an earlier session set and left two paths short of: D-360's title cleaning (MEU-122, Session 53) and D-335's home scrub (MEU-119, Session 52). Both are small service changes with unit tests and no renderer work.
- **Order:** MEU-147 → MEU-148.
- **Gate:** MEU-148 follows Mat's D-337 ruling: its own plan row with a Red, `GetShortPathNameW` read once and cached, Windows only.
- **Cloud/local:** either; MEU-148's lookup is faked in the tests.
- **Token estimate:** calibrate against Session 53 `transcript-metadata` and Session 52 `tts-load-fp16` (MEU-119's scrub).
- **Split flag:** no.

### Session 78 — `e2e-harness-hardening` (no MEU) · P3

- **Layer / files:** `ui/tests/e2e/` (the 14 `_electron.launch()` sites and a shared launch helper), the Vitest setup for the lazy Electron install, `ui/tests/unit/capture-page.test.ts` (AC-97.4).
- **Covers:** `E2E-MAIN-PROCESS-ERRORS-UNWATCHED`, `E2E-ELECTRON-LAUNCH-FLAG`, `UI-ELECTRON-LAZY-INSTALL-RACE`, `CAPTURE-HINT-TEST-PRESENCE-ONLY`.
- **Why grouped:** all four make the UI test suites report what really happened: a main-process exception fails the test, a launch drops `ELECTRON_RUN_AS_NODE` from the environment it passes, parallel workers no longer race the binary install, and the hint test checks the chord values. The first two share one launch helper.
- **Order:** the launch helper (flag and main-process watch together) → the install race → the hint test.
- **Cloud/local:** local (Electron E2E).
- **Token estimate:** calibrate against Session 44 `release-rc1` for the E2E launch surface, scaled down: no build, no installer.
- **Split flag:** no.

### Session 79 — `triage-tool-fixes` (no MEU) · P3

- **Layer / files:** `tools/issue_triage.py` (stdout encoding), `tools/issue_triage/verify.py` (prose read as a path, the blanket `no_test_coverage`, `last_checked` stamped without a check) and the `discover` scan roots.
- **Covers:** `TOOLING-TRIAGE-CLI-CP1252`, `TOOLING-TRIAGE-SCANNER-FALSE-FINDINGS`.
- **Why grouped:** both are the triage tool this workflow runs. This triage met both again: the cp1252 crash on a redirected receipt, and 65 scan results that were all noise (D-812).
- **Order:** the encoding fix → the scanner.
- **Cloud/local:** either.
- **Token estimate:** calibrate against Session 49b.
- **Split flag:** no. It may merge into Session 76 if Session 76's plan comes out small; that is decided when Session 76 is planned.

### Session 80 — `tts-page-polish` (MEU-149, MEU-150) · P3

- **Layer / files:** `services/tts.py` (output names; the job ID and API shape unchanged), `TTSPage.tsx` (the pill and the progress label), `tts-controls.ts` (`STATUS_COLORS`).
- **Why grouped:** both are what a user sees on the TTS page and in its output folder. They share `TTSPage.tsx`.
- **Order:** MEU-150 → MEU-149, so the pill's contrast check runs on the page's final markup.
- **Gate:** MEU-150's name scheme is a plan-time Decision Brief (D-807), because the user sees it in their folder. MEU-149's look gets Mat's check in both themes before it ships (D-806, as D-235 did for MEU-126).
- **Cloud/local:** local (Mat looks at both themes).
- **Token estimate:** calibrate against Session 56 `light-accent-contrast` (MEU-149) and Session 51 `tts-build-capability` (the TTS service and page).
- **Split flag:** no.

### Session 81 — `convert-settings-drafts` (MEU-151, MEU-152) · P4

- **Layer / files:** `useCaptureSettings.ts` (the draft holds only changed fields), `ConvertPage.tsx` (edits kept when settings arrive; queue positions), `convert-controls.ts` (time codes), `QueueCard.tsx`, `services/conversion.py` (`queue_position` and the Cut encoder).
- **Why grouped:** both are Convert-page debt from the RC1 and Session 54 reviews, and they share `ConvertPage.tsx`. MEU-151's capture half follows the same AC-112.9 shape the converter hook already has.
- **Order:** MEU-151 → MEU-152.
- **Cloud/local:** local (renderer tests).
- **Token estimate:** calibrate against Session 54 `convert-extract-index`.
- **Split flag:** no.

### Session 82 — `ready-handshake` (MEU-153, MEU-154) · P4

- **Layer / files:** `cli.py` (listen before the ready line), `ui/src/main/python-manager.ts` (`publishIfReady`, `confirmReadyAndPublish`: line buffering, once per process, the veto).
- **Why grouped:** the two ends of one line. The backend writes `AVKIT_READY`; the main process reads it. Neither failure has been seen in the real app, so the session also records whether the first request can hit the gap.
- **Order:** MEU-153 → MEU-154.
- **Gate:** the veto rule in 06's row is decided at plan time with its evidence.
- **Cloud/local:** local (the packaged backend smoke).
- **Token estimate:** calibrate against Session 44 `release-rc1` (MEU-108's READY probe).
- **Split flag:** no.

### Session 83 — `docs-path-hygiene` (no MEU) · P4

- **Layer / files:** the build plan's install-folder lines and the install round-trip script (D-811); for D-817, a tracked-file check and the six live files that name the home folder (`known-issues.yaml`, `.agent/skills/git-workflow/SKILL.md`, `_inspiration/capture-crop/design.md`, `docs/build-plan/06-gui.md`, `ui/tests/unit/capture-interactive.test.ts`, `ui/tests/unit/dev-spawn.test.ts`).
- **Covers:** `INSTALL-FOLDER-NAME-MISMATCH`, `TRACKED-FILES-HOLD-HOME-PATH`.
- **Why grouped:** both make the tracked text match what is true and safe to publish, with no product change. The installer itself is unchanged (D-811).
- **Order:** the install folder → the home path.
- **Gate:** D-817 was ruled A on 2026-11-15: the check with today's evidence files allow-listed by name, and the six live files fixed. Evidence files stay byte-for-byte.
- **Cloud/local:** either.
- **Token estimate:** calibrate against Session 49b.
- **Split flag:** no.

---

## 4. Plan-creation pathway

On Mat's word, run `/create-plan` once per session, in the §5 order. Nothing is planned now, because Mat asked for triage and grouping, not a plan. Each plan re-reads its MEU's build-plan home and the issues it closes. The no-MEU sessions plan as Session 49b did: the plan names the issues it closes, and no MEU status changes.

1. `/create-plan capture-inbox-probe` → MEU-145, MEU-146
2. `/create-plan tooling-test-hermeticity` → no MEU
3. `/create-plan text-scrub-residuals` → MEU-147, MEU-148
4. `/create-plan e2e-harness-hardening` → no MEU
5. `/create-plan triage-tool-fixes` → no MEU (or folded into 2)
6. `/create-plan tts-page-polish` → MEU-149, MEU-150
7. `/create-plan convert-settings-drafts` → MEU-151, MEU-152
8. `/create-plan ready-handshake` → MEU-153, MEU-154
9. `/create-plan docs-path-hygiene` → no MEU; D-817 ruled A

---

## 5. Prerequisite gate

- **Queue (D-816):** Session 74 first; it is prompted and ships a fix for a high-severity issue. The HDP v2 grouping (`2026-11-15-hdp-framework-sync-session-grouping.md`, D-824) puts its Sessions 84 to 86 next. Then Sessions 75 to 83 in number order: the P2 sessions (75, 76), then P3 (77 to 80), then P4 (81 to 83). Planning and plan review are not blocked; execution of any session waits for Mat's explicit message (`plan_to_exec_gate: human`).
- **Session 75:** the plan's MEU-146 brief is answered before execution.
- **Session 80:** the plan's MEU-150 brief is answered before execution; Mat looks at both themes before closeout.
- **Session 83:** D-817 was ruled A on 2026-11-15.
- No branch or worktree; main only.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 75 | `capture-inbox-probe` | MEU-145, MEU-146 | P2 | executed (Session 75) | `docs/execution/plans/2026-11-15-capture-inbox-probe/` |
| 76 | `tooling-test-hermeticity` | — | P2 | proposed | — |
| 77 | `text-scrub-residuals` | MEU-147, MEU-148 | P3 | executed (Session 77) | `docs/execution/plans/2026-11-15-text-scrub-residuals/` |
| 78 | `e2e-harness-hardening` | — | P3 | executed (Session 78) | `docs/execution/plans/2026-11-15-e2e-harness-hardening/` |
| 79 | `triage-tool-fixes` | — | P3 | executed (Session 79) | `docs/execution/plans/2026-11-15-triage-tool-fixes/` |
| 80 | `tts-page-polish` | MEU-149, MEU-150 | P3 | executed (Session 80) | `docs/execution/plans/2026-11-15-tts-page-polish/` |
| 81 | `convert-settings-drafts` | MEU-151, MEU-152 | P4 | executed (Session 81) | `docs/execution/plans/2026-11-15-convert-settings-drafts/` |
| 82 | `ready-handshake` | MEU-153, MEU-154 | P4 | proposed | — |
| 83 | `docs-path-hygiene` | — | P4 | proposed | — |

The Band column is the session's queue priority. Every MEU is registered in band P2, as the earlier triage residuals were; a session band below P2 orders the queue and changes no register field.

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Session 75:** Session 58 `capture-region-import` and Session 59 `capture-crop-copy`, the capture adapter and service with generated images.
- **Sessions 76, 79, 83:** Session 49b `closeout-register-grammar`, tooling with no MEU.
- **Session 77:** Session 53 `transcript-metadata` (MEU-122's cleaning) and Session 52 `tts-load-fp16` (MEU-119's scrub).
- **Session 78:** Session 44 `release-rc1`, for the E2E launch surface.
- **Session 80:** Session 56 `light-accent-contrast` (execution review 9,980,641 tokens) and Session 51 `tts-build-capability`.
- **Session 81:** Session 54 `convert-extract-index` (execution review 7,859,970 tokens).
- **Session 82:** Session 44 `release-rc1` (MEU-108's READY probe).
- General: Session 50 `transcript-failure-reason`.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-813 | Triage the register and group what it leaves? | human | Yes. D-801 to D-812 written; MEU-145 to MEU-154 registered and grouped into Sessions 75 to 83. No plan created. | Human-approved | Mat asked for exactly this. | USER_EXPLICIT 2026-11-15 "@.agent/skills/issue-triage/ and create new session grouping" |
| D-814 | Slicing, homes and phases | autonomous | One MEU per issue, or per group of issues that share one code path (MEU-150, 151, 152). Each home sits in the build-plan file of the layer it changes (03, 04, 06, 08, 09), all band P2. MEU-144 and row 3.21 stay held for Session 74. | Local Canon | Earlier triage residuals took one MEU per change with its home in the changed layer, band P2 (2026-11-04 rc.2 residuals). Joining issues that share one function keeps one TDD cycle per change. Numbering Session 74's ship MEU here lost: its prompt leaves that registration to Mat at its plan gate. Two-way. | — |
| D-815 | Which work shares a session, and does debt with no MEU get a session? | autonomous | Pairs by shared file or shared rule (§3). The ten tooling, E2E and docs issues run as four sessions with no MEU. The bucket tool's pairing of the capture scan with TTS FP16 is not used. | Local Canon | Session 49b ran tooling debt with no MEU (D-280), and the closeout validator accepts it. Riding the debt on unrelated MEU sessions lost: it widens their review scope for no shared code. The bucket pairing lost because the two share no file or layer (D-802). Two-way. | — |
| D-816 | Queue position | autonomous | Session 74 first, then 75 to 83 by band: P2, P3, P4. | Local Canon | Fixes for a released build go ahead of polish (D-538). Session 74 ships the fix for the one high-severity issue and is already prompted. Session 75 fixes the only medium user-facing break; Session 76 the only P2 tooling break. Two-way: one message from Mat moves it. | — |
| D-817 | What should be done about tracked files that name the home folder in full? | human | A: a check that refuses new instances, with today's evidence files allow-listed by name, and the six live files fixed. | Human-approved | Brief below. B (rewrite every file) breaks byte-for-byte evidence; C (check only) leaves the live files as they are; D (do nothing) lets the count keep growing (56 files on 2026-11-07, 66 now). Two-way: the check can be loosened in one edit. | USER_EXPLICIT 2026-11-15 "A", Mat's reply to the D-817 brief, which recommended A |

## 9. Decision Briefs

### D-817: What should be done about tracked files that name the home folder in full?   [public-exposure] [grouping]

**Ruled:** A, by Mat on 2026-11-15 ("A").

**Recommendation:** A. Add a check, run by the gate, that fails when a tracked file holds the home folder's full Windows path, with today's evidence files (handoffs, reviews, session digests and plan-folder receipts) allow-listed by name. Fix the six live files that are read and edited going forward: `known-issues.yaml`, `.agent/skills/git-workflow/SKILL.md`, `_inspiration/capture-crop/design.md`, `docs/build-plan/06-gui.md`, `ui/tests/unit/capture-interactive.test.ts` and `ui/tests/unit/dev-spawn.test.ts`. Evidence stays byte-for-byte as reviewed.

Facts (git grep over the tracked tree on 2026-11-15, outside `.agent/fleet/hub`): 66 files and 130 lines, up from 56 files and 119 lines on 2026-11-07. About 16 are handoffs, about 30 are plan-folder files and 14 are session digests, all evidence; six are live. The repository is public, and the history squashed on 2026-11-03 still holds the earlier lines, so any fix limits new exposure only.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ A: check plus allow-list, fix the six live files | — | — | D-800; D-335 |
| ⚠️ B: rewrite every file, evidence included | The tree holds no instance at all | Breaks the byte-for-byte evidence that reviews and hashes bind to (receipts and recorded hashes); the public history keeps the old lines anyway | Mat's 2026-11-07 ruling that Session 52's files are committed as they are |
| ⚠️ C: check only | Smallest change; stops growth | The six live files keep the path, and they are the ones copied into new work | — |
| ❌ D: do nothing | No change | The count grew by 10 files in 8 days; nothing stops the next one | `TRACKED-FILES-HOLD-HOME-PATH` |

**Precedent:**
- D-335 (MEU-119) scrubs the home folder from Console output at runtime; nothing covers tracked files.
- D-800 (Session 73) had the reviewer's scratch files redacted before commit, so Mat has already chosen to keep new instances out.
- On 2026-11-07 Mat ruled that Session 52's files are committed as they are and that the next triage takes this issue up. This is that triage.

**Research:** none needed beyond the register and git grep; this is a repository policy question.

**Reversibility / risk:** A and C are two-way: the check can be loosened in one edit. B is one-way for the evidence it rewrites. Under A, a later session that must quote a path writes `~` or "the home folder".
**Obviousness:** A follows D-800's direction, but it sets a repository-wide check and an allow-list that Mat will see in every gate, and the issue was explicitly left to Mat's next look.
**If you do not answer:** superseded by the ruling. Session 83's plan would have carried the install-folder fix only and asked again at its plan gate.

Carry-forward: each row appears in its consuming session's reflection `### Decisions Log` with stage `grouping`. The closeout validator reads every §8 row of the declared grouping, so a session's reflection lists them all. The lines below say which rows bear on each session.

- Sessions 75, 77, 80, 81 and 82 carry D-813, D-814, D-815 and D-816.
- Sessions 76, 78 and 79 carry D-813, D-815 and D-816.
- Session 83 carries D-813, D-815, D-816 and D-817.
