# 2026-11-04 rc.2 triage residuals · Session grouping

> **Source:** `.agent/context/known-issues.yaml` after the 2026-11-04 `/issue-triage` run, with the decisions in each issue's `enrichment.decision_log`. Mat's message that day: "OK we will go with pythorch remove as you originally suggested. All ohter recommendations are accepted. Proceed". Mat later that day: "FFmpeg, keeping libdvdcss in rc.2: yes" (D-266).
> **Generated:** 2026-11-04
> **Method:** Stage A (issues → MEU-113–126, registered in `meu-status.yaml`, `render --check` green; build-plan homes in 03, 06, 07 and 08; matrix rows 3.12–3.17, 6.14–6.17, 7.7–7.9, 8.9) + Stage B (MEUs → Sessions 49–57), plus tooling Session 49b with no MEU (D-274, D-280).
> **Origin:** RC1 went out on 2026-11-04. The walkthroughs and the triage found what needs a new release candidate: a Transcript job that fails with no reason and keeps requesting while blocked, a PyTorch model the installed app downloads and can never load, and an FP16 model that fails on some ordinary sentences. The triage also found that the pinned FFmpeg links libdvdcss, and Mat kept it as an accepted risk (D-266).
> **Status:** Active — reversible draft, not a gate. Nothing here approves a plan or authorizes execution. Scoping review status is in §9.
> **Parallel work:** one other session has uncommitted release documents in the same tree (`current-focus.md`, the RC1 plan, task and reflection, the RC1 publish checklist). None of them is touched here. No other worktree exists and no MEU-113 or later is claimed anywhere.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (known issues) | Layer | Depends on |
|-----|------|-----------------------|-------|------------|
| MEU-113 | `dist-fetch-exit-codes` | `FETCH-FFMPEG-EXIT-CODES` (re-scoped by D-266) | Tools | MEU-25, MEU-110 |
| MEU-114 | `dist-uninstall-installer-copy` | `UNINSTALL-LEAVES-INSTALLER-COPY` (D-228) | Installer | MEU-25 |
| MEU-115 | `svc-transcript-failure-reason` | `TRANSCRIPT-FAILED-NO-REASON` (D-218); rider `CONSOLE-FAILURE-DETAIL-LOST` | Service, port, adapter, API, GUI | MEU-11, MEU-13, MEU-16, MEU-21, MEU-27 |
| MEU-116 | `svc-transcript-block-stop` | `TRANSCRIPT-BLOCK-KEEPS-REQUESTING` (D-219, D-220) | Service | MEU-11, MEU-115 |
| MEU-117 | `svc-tts-build-capability` | `TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME` (D-217, D-237) | Adapter, service, API, MCP, GUI | MEU-72, MEU-75, MEU-98 |
| MEU-118 | `gui-tts-device-options` | `TTS-DEVICE-OPTIONS-IN-CPU-BUILD` (D-226) | GUI | MEU-23, MEU-75, MEU-117 |
| MEU-119 | `svc-tts-load-keeps-model` | `TTS-FAILED-LOAD-DROPS-MODEL` (D-221) | Adapter | MEU-62, MEU-75, MEU-98 |
| MEU-120 | `gui-models-dir-probe` | `MODELS-DIR-DOCS-AND-PROBE-MISMATCH` (D-222) | GUI main process | MEU-23 |
| MEU-121 | `svc-tts-fp16-nonfinite` | `TTS-ONNX-FP16-NONFINITE-AUDIO` (D-239) | GUI, adapter investigation | MEU-62, MEU-72, MEU-117 |
| MEU-122 | `svc-transcript-metadata` | `TRANSCRIPT-TITLE-IS-VIDEO-ID` (D-223), `TRANSCRIPT-CHANNEL-IS-PLAYLIST-NAME` (D-224) | Service, port, adapter | MEU-7, MEU-11 |
| MEU-123 | `convert-extract-stream-index` | `CONVERT-EXTRACT-STREAM-INDEX-MISMATCH` (D-227); rider `CONVERT-EXTRACT-ENCODER-LABEL` | Service, media adapter | MEU-29, MEU-30 |
| MEU-124 | `download-received-quality` | `DOWNLOAD-ROW-SHOWS-REQUESTED-QUALITY` (D-225) | Domain, service, database, API, GUI | MEU-10, MEU-20 |
| MEU-125 | `dist-release-candidate-2` | The accepted batching: the new build, gate, notes and checklist | Release | MEU-110, MEU-113, MEU-114, MEU-115, MEU-116, MEU-117, MEU-118, MEU-119, MEU-120, MEU-121 |
| MEU-126 | `gui-light-accent-contrast` | `LIGHT-ACCENT-BELOW-AA-CONTRAST` (D-235) | GUI | MEU-26 |

**Findings → MEU traceability.** Every open, mitigated or dismissed issue appears once.

| Known issue | Category | MEU / disposition |
|-------------|----------|-------------------|
| `FETCH-FFMPEG-EXIT-CODES` | TECH-DEBT | MEU-113 |
| `UNINSTALL-LEAVES-INSTALLER-COPY` | MEU-NEW | MEU-114 |
| `CONSOLE-FAILURE-DETAIL-LOST` | TECH-DEBT | MEU-115 (rider) |
| `TRANSCRIPT-FAILED-NO-REASON` | MEU-NEW | MEU-115 |
| `TRANSCRIPT-BLOCK-KEEPS-REQUESTING` | MEU-NEW | MEU-116 |
| `TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME` | MEU-NEW | MEU-117 |
| `TTS-DEVICE-OPTIONS-IN-CPU-BUILD` | MEU-NEW | MEU-118 |
| `TTS-FAILED-LOAD-DROPS-MODEL` | MEU-NEW | MEU-119 |
| `MODELS-DIR-DOCS-AND-PROBE-MISMATCH` | MEU-NEW | MEU-120 |
| `TTS-ONNX-FP16-NONFINITE-AUDIO` | MEU-NEW | MEU-121 |
| `TRANSCRIPT-CHANNEL-IS-PLAYLIST-NAME` | MEU-NEW | MEU-122 |
| `TRANSCRIPT-TITLE-IS-VIDEO-ID` | MEU-NEW | MEU-122 |
| `CONVERT-EXTRACT-ENCODER-LABEL` | TECH-DEBT | MEU-123 (rider) |
| `CONVERT-EXTRACT-STREAM-INDEX-MISMATCH` | MEU-NEW | MEU-123 |
| `DOWNLOAD-ROW-SHOWS-REQUESTED-QUALITY` | MEU-NEW | MEU-124 |
| `LIGHT-ACCENT-BELOW-AA-CONTRAST` | TECH-DEBT | MEU-126 |
| `BACKEND-READY-BEFORE-LISTEN` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | MONITORING | Not an MEU: monitoring, acts on recurrence |
| `CAPTURE-HINT-TEST-PRESENCE-ONLY` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `CAPTURE-JOURNAL-VOLATILE` | DEFER | Not an MEU: deferred, no change |
| `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` | MONITORING | Not an MEU: monitoring, acts on recurrence |
| `CLOSEOUT-CHECK-REFUSES-REGISTER` | TECH-DEBT | Not an MEU: Session 49b, a tooling session tracked by the issue (D-274, D-280) |
| `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `CONVERT-ADVANCED-EDIT-REPLACED` | TECH-DEBT | Not an MEU: first in current-focus's debt queue. Needs a build, so it would land before Session 57 if wanted |
| `CONVERT-CUT-TIME-RAW-MS` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `CONVERT-POSITIONS-NOT-RENUMBERED` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `DOWNLOAD-QUEUE-DRAG-OVER-MISS` | MONITORING | Not an MEU: monitoring, acts on recurrence |
| `DOWNLOADER-ADVANCED-PANEL-GAP` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `E2E-CLIPBOARD-PRIMER-EMPTY` | MONITORING | Not an MEU: first in current-focus's debt queue. Needs a build, so it would land before Session 57 if wanted |
| `E2E-ELECTRON-LAUNCH-FLAG` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `E2E-MAIN-PROCESS-ERRORS-UNWATCHED` | TECH-DEBT | Not an MEU: first in current-focus's debt queue. Needs a build, so it would land before Session 57 if wanted |
| `FFMPEG-LIBDVDCSS-BUNDLED` | CLOSE | Not an MEU: accepted risk, Mat's D-266 |
| `GUI-READY-CHUNK-BOUNDARY` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `INSTALL-FOLDER-NAME-MISMATCH` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | UPSTREAM | Not an MEU: upstream, mitigated |
| `SETTINGS-DRAFT-STALE-BASELINE` | TECH-DEBT | Not an MEU: first in current-focus's debt queue. Needs a build, so it would land before Session 57 if wanted |
| `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `TOOLING-SHARED-REGISTRY-COUPLING` | TECH-DEBT | Not an MEU: P2 tooling debt that ships nothing and is outside the accepted batches, so no release waits on it |
| `TOOLING-TRIAGE-CLI-CP1252` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `TOOLING-TRIAGE-SCANNER-FALSE-FINDINGS` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `TRANSCRIPT-ADD-CHANNEL-422` | MONITORING | Not an MEU: monitoring, acts on recurrence |
| `TTS-AUDIO-RANDOM-FILE-NAMES` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | BLOCKED | Not an MEU: blocked until Mat installs eSpeak NG 1.52 and runs AC-74.11 |
| `TTS-JA-ZH-G2P-EXTRAS` | DEFER | Not an MEU: deferred (D-229) |
| `TTS-PYTORCH-RUNTIME-SETTINGS-DOWNLOAD` | CLOSE | Not an MEU: dismissed and not built. Mat's D-217 ruling supersedes D-236 |
| `TTS-SEGMENTS-LABEL-IS-PROGRESS-SCALE` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `TTS-VOICE-SELECT-LAYOUT-JUMP` | none | Not an MEU: dismissed earlier, no change |
| `UI-ELECTRON-LAZY-INSTALL-RACE` | TECH-DEBT | Not an MEU: standing debt queue, outside the accepted batches |
| `YOUTUBE-CAPTIONS-IP-BLOCK` | UPSTREAM | Not an MEU: upstream, stays open. MEU-115 and MEU-116 change only how the app reports a block and stop on one |

**Build-plan homes:** 03 §Transcript failure reason, §Transcript block stop, §TTS build capability, §TTS load keeps the current model, §TTS ONNX FP16 audio, §Transcript source metadata; 06 §TTS device options, §Models folder probe, §Downloader received quality, §Light accent contrast; 07 §Fetch script exit codes, §Uninstall removes the installer copy, §Second release candidate, and the corrected Models text; 08 §Extract stream index. All are marked (residual).

---

## 2. Dependency graph + critical path

```
MEU-25, MEU-110 ─────────► MEU-113 exit codes ─────────────────┐  Session 49  rc2-fetch-uninstall
MEU-25 ──────────────────► MEU-114 uninstall ──────────────────┤  Session 49
MEU-11, 13, 16, 21, 27 ──► MEU-115 reason ──► MEU-116 stop ────┤  Session 50  transcript-failure-reason
MEU-72, 75, 98 ──────────► MEU-117 capability ─┬─► MEU-118 ────┤  Session 51  tts-build-capability
                                               │   (+MEU-23, 75)
                                               └─► MEU-121 ────┤  Session 52  tts-load-fp16
                                                   (+MEU-62, 72)
MEU-62, 75, 98 ──────────► MEU-119 load order ─────────────────┤  Session 52
MEU-23 ──────────────────► MEU-120 folder probe ───────────────┴─► MEU-125 rc.2  Session 57  release-rc2
MEU-7, 11 ───────────────► MEU-122 titles, channel ┄┄┄ soft ┄┄┄┄┄┄┄┄┘  Session 53  transcript-metadata
MEU-29, 30 ──────────────► MEU-123 extract index ┄┄┄┄┄ soft ┄┄┄┄┄┄┄┄┘  Session 54  convert-extract-index
MEU-10, 20 ──────────────► MEU-124 received quality ┄┄ soft ┄┄┄┄┄┄┄┄┘  Session 55  download-received-quality
MEU-26 ──────────────────► MEU-126 light accent ┄┄┄┄┄┄ soft ┄┄┄┄┄┄┄┄┘  Session 56  light-accent-contrast
```

Every prerequisite outside the batch is approved. A solid line is a registered dependency. MEU-125's soft lines are not: MEU-122 to MEU-124 and MEU-126 go in the build if they're done by then.

**Critical path:** MEU-117 → MEU-121 → MEU-125 and MEU-115 → MEU-116 → MEU-125.

**Soft order (shared files, not dependencies):** Session 53 follows Session 50 because both edit `services/transcript.py`. MEU-121 comes last inside Session 52 because its cause hunt has no upper bound.

**Tooling first:** Session 49b changes only `tools/` and the register's form. It runs after Session 49 and before Session 50, so later closing sessions read the register directly (D-274).

**Parallel tiers:** Sessions 49, 50 and 51 share no files and could run in any order; main-only work runs them one at a time. Session 52 needs Session 51. Session 57 needs 49 to 52.

---

## 3. Recommended grouping — 10 sessions (49, 49b, 50–57)

The triage proposed five batches: A (FFmpeg, uninstall), B (Transcript failures), C (TTS), D (titles and channel), E (extract index, received quality). rc.2's minimum is A to C, with D and E if they're quick.

**Changes from the batches Mat accepted, for Mat to check:**

- Batch C gained the FP16 issue.
- The PyTorch runtime download is gone (D-217 supersedes D-236).
- `LIGHT-ACCENT-BELOW-AA-CONTRAST` wasn't in a batch and has its own MEU, which rc.2 takes if it's done by then (D-249).
- Batch E runs as two sessions, each still optional for rc.2 (D-250).
- rc.2 has its own MEU at the end (D-243).
- Title and channel are one MEU, not two (D-241).
- TTS runs as two sessions, not one (D-245).
- Batch A lost the FFmpeg build: Mat kept FFmpeg as it is, including libdvdcss (D-266). Its exit-code rider now stands as MEU-113, and the two fixes stay in one session (D-267).
- Session 49b, a tooling session with no MEU, fixes the closeout check before Session 50 (Mat's D-274, D-280).

### Session 49 — `rc2-fetch-uninstall` (MEU-113, MEU-114) · P2

- **Layer / files:** `tools/fetch_ffmpeg_windows.ps1`, `tests/unit/test_packaging_installer.py`, `ui/build/installer.nsh`, `install-roundtrip.ps1`, `ui/tests/unit/login-item-nsh.test.ts`.
- **Why grouped:** both were batch A, neither touches app code, and each is too small to justify a plan of its own, though they share no file (D-267).
- **Order:** MEU-113 → MEU-114.
- **Cloud/local:** local for both, including the install round trip.
- **Token estimate:** calibrate against the packaging part of Session 44 `release-rc1`.
- **Split flag:** no.

### Session 49b — `closeout-register-grammar` (no MEU; `CLOSEOUT-CHECK-REFUSES-REGISTER`) · P3

- **Layer / files:** `tools/issue_triage/model.py`, `tools/validate_closeout_artifacts.py`, their tests, and one reformat of `.agent/context/known-issues.yaml` with every parsed value asserted equal.
- **Scope:** `model.save` writes indented, unwrapped YAML; `--decision-issue` becomes repeatable; the six logs the placeholder check still refuses are reworded with the same meaning.
- **Why here:** Mat ruled it runs after Session 49 and before Session 50 (D-274), so Sessions 50 to 57 close without Session 49's extract workaround (D-272).
- **Cloud/local:** local.
- **Token estimate:** calibrate against Session 33 `capture-chrome`, whose D-39 changed the same validator.
- **Split flag:** no.

### Session 50 — `transcript-failure-reason` (MEU-115, MEU-116) · P2

- **Layer / files:** `services/transcript.py`, `ports/transcript.py`, `transcript/adapter.py`, `routes/transcripts.py`, `TranscriptPage.tsx`, `transcript-help-content.ts`, `services/health.py`.
- **Why grouped:** both change the run loop and how a block is reported, and the pause reason in MEU-116 is the message from MEU-115.
- **Order:** MEU-115 → MEU-116.
- **Cloud/local:** local. Tests use a fake port and clock, with no YouTube requests.
- **Token estimate:** calibrate against Session 42 `tts-sideload-load` (service, route and GUI message).
- **Split flag:** yes, candidate. MEU-116 can run as 50b if MEU-115's handoff passes ~50% context.

### Session 51 — `tts-build-capability` (MEU-117, MEU-118) · P2

- **Layer / files:** `tts/adapter.py`, `services/models.py`, `routes/models.py`, `04-rest-api.md`, `TTSPage.tsx`, `tts-controls.ts`, `SettingsPage.tsx`, MCP schema tests.
- **Why grouped:** the device select reads the capability source MEU-117 adds.
- **Order:** MEU-117 → MEU-118.
- **Cloud/local:** local (Electron E2E, `ELECTRON_RUN_AS_NODE` cleared).
- **Token estimate:** calibrate against Session 35 `tts-voice-panel` (Voice availability has the same shape).
- **Split flag:** no.

### Session 52 — `tts-load-fp16` (MEU-119, MEU-120, MEU-121) · P2

- **Layer / files:** `tts/adapter.py`, `tests/integration/test_tts_device_resolution.py`, `setup-readiness.ts`, `tts-controls.ts`, `engine.py`, the fixed sentence set in the plan folder.
- **Why grouped:** the three fresh-install and load fixes in batch C after the capability work, each small except the FP16 cause hunt.
- **Order:** MEU-119 → MEU-120 → MEU-121.
- **Cloud/local:** local. The cause hunt needs the pinned ONNX files.
- **Token estimate:** calibrate against Session 42 `tts-sideload-load`. The cause hunt has no upper bound.
- **Split flag:** yes. The preselection change can ship while the cause hunt runs on as a time-boxed spike, and the plan sets the time box.

### Session 53 — `transcript-metadata` (MEU-122) · P2

- Service, port and adapter change using the enumeration `add_channel` already runs. Kept apart from Session 50 because Mat accepted this batch as "if quick", so it can't hold back the failure fixes. Calibrate against Session 42 `tts-sideload-load`.

### Session 54 — `convert-extract-index` (MEU-123) · P2

- Batch E's extraction fix: service and media adapter, with the encoder label rider. Calibrate against Session 42 `tts-sideload-load`.

### Session 55 — `download-received-quality` (MEU-124) · P2

- Batch E's quality fix: domain, service, database, API and GUI. It shares no file with Session 54, so it has its own plan (D-250). Calibrate against the MEU-112 part of Session 44 `release-rc1`, which added a job column the same way.

### Session 56 — `light-accent-contrast` (MEU-126) · P2 band, issue P4

- Two light tokens, a contrast test and Mat's look at the light theme. It runs after the P2 issues because the issue is P4. Calibrate against the renderer part of Session 41 `gui-keyboard-palette`.

### Session 57 — `release-rc2` (MEU-125) · P2

- Version, clean build, gate, notes and checklist. Calibrate against Session 44 `release-rc1`, whose review rounds cost 4.5M to 10M tokens each. Publishing stays with Mat.

---

## 4. Plan-creation pathway

Run `/create-plan` once per session, in order. Session 49 is planned now, following Mat's "Proceed", and was re-planned after D-266. The later sessions are planned one at a time.

1. `/create-plan rc2-fetch-uninstall` → MEU-113, MEU-114
   Then `/create-plan closeout-register-grammar` → Session 49b, no MEU, issue `CLOSEOUT-CHECK-REFUSES-REGISTER`
2. `/create-plan transcript-failure-reason` → MEU-115, MEU-116
3. `/create-plan tts-build-capability` → MEU-117, MEU-118
4. `/create-plan tts-load-fp16` → MEU-119, MEU-120, MEU-121
5. `/create-plan transcript-metadata` → MEU-122
6. `/create-plan convert-extract-index` → MEU-123
7. `/create-plan download-received-quality` → MEU-124
8. `/create-plan light-accent-contrast` → MEU-126
9. `/create-plan release-rc2` → MEU-125

Each plan follows `.agent/docs/cloud-local-collaboration.md`: gate location and reviewer route at plan time, the `ENV_BOUND_*` census, and both gate scripts built from one stage list.

---

## 5. Prerequisite gate

- **Session 49b:** Session 49 has closed, with D-272's extract.
- **Session 50:** Session 49b has closed (D-274). Mat has ruled that errors always go to a file (D-247).
- **Session 52:** Mat listens to the INT8 sample before the preselection ships (D-239).
- **Session 56:** Mat looks at the light theme before it ships (D-235).
- **Session 57:** the check from another network settles the release notes' 'your network' wording (D-216).
- **Capture sessions:** the 2026-10-29 grouping's pending sessions (MEU-102 to MEU-107) wait behind these, because they fix no release problem and these do.
- **Commit:** the register rulings, this grouping and its registration are committed together in exact-scope mode, without a push (Mat's D-276). The push waits for Mat, who reads the register's libdvdcss wording first.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 49 | `rc2-fetch-uninstall` | MEU-113, MEU-114 | P2 | pending | `docs/execution/plans/2026-11-04-rc2-fetch-uninstall/` |
| 49b | `closeout-register-grammar` | none (`CLOSEOUT-CHECK-REFUSES-REGISTER`) | P3 | executed | `docs/execution/plans/2026-11-05-closeout-register-grammar/` |
| 50 | `transcript-failure-reason` | MEU-115, MEU-116 | P2 | pending | — |
| 51 | `tts-build-capability` | MEU-117, MEU-118 | P2 | pending | — |
| 52 | `tts-load-fp16` | MEU-119, MEU-120, MEU-121 | P2 | pending | — |
| 53 | `transcript-metadata` | MEU-122 | P2 | pending | — |
| 54 | `convert-extract-index` | MEU-123 | P2 | pending | — |
| 55 | `download-received-quality` | MEU-124 | P2 | pending | — |
| 56 | `light-accent-contrast` | MEU-126 | P2 | pending | — |
| 57 | `release-rc2` | MEU-125 | P2 | pending | — |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- Session 44 `release-rc1` (packaging, source archive, gate) — Session 57. Its packaging part — Session 49. Its MEU-112 part — Session 55.
- Session 42 `tts-sideload-load` (service, route, GUI message) — Sessions 50, 52, 53 and 54.
- Session 35 `tts-voice-panel` (availability with a reason) — Session 51.
- Session 41 `gui-keyboard-palette` (GUI MEUs with Electron tests) — the renderer part of Session 51, and Session 56.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-240 | Where does session numbering start? | autonomous | 49 | Local Canon | Session 44 became `release-rc1` while the 2026-10-29 grouping's table still names 44 `capture-redact`, and 45 to 48 are its pending sessions. Starting at 49 reuses no number. Two-way. | — |
| D-241 | Are the transcript title and channel name two MEUs? | autonomous | One, MEU-122 | Local Canon | Same enumeration, same `add_channel` change, same test fake. Two would edit the same lines twice. Two-way. | — |
| D-242 | Where do the riders go? | autonomous | By shared file: Console fields in MEU-115, the encoder label in MEU-123. FFmpeg exit codes were a rider in MEU-113 until D-266 made them its whole scope | Local Canon | A rider needs a session already in that file. The first draft also put the light accent in MEU-118; D-249 replaced that. Two-way. | — |
| D-243 | Does rc.2 get its own MEU? | autonomous | Yes, MEU-125 | Local Canon | MEU-110 is approved and closed, and the fixes in batches A to C need a new release candidate. Reopening an approved MEU would hide the new gate. Two-way. | — |
| D-244 | Which session runs first? | autonomous | Fetch and uninstall, Session 49 | Local Canon | It's the smallest and is already planned, and its round trip script is reused by MEU-125. The earlier reason, the FFmpeg build's unknowns, went with D-266. No dependency needs it first. Two-way. | — |
| D-245 | Is TTS one session or two? | autonomous | Two, Sessions 51 and 52 | Local Canon | The FP16 cause hunt has no upper bound and shouldn't hold the download refusal. Two-way. | — |
| D-246 | Where does the FFmpeg build run, and where does the rebuilt archive live? | human | Withdrawn: no build runs | Human-approved | Mat kept FFmpeg as it is, so neither question remains (D-266). | USER_EXPLICIT 2026-11-04 "FFmpeg, keeping libdvdcss in rc.2: yes" |
| D-247 | Do errors always go to a file? | human | Yes: errors always go to a file. Session 50's plan carries it out | Human-approved | It changes a default the user sees (`app.log_to_file` is off), so it was Mat's to rule. | USER_EXPLICIT 2026-11-05 "D-247: yes they should go to file" |
| D-248 | Does Mat's "Proceed" confirm the grouping for the D-234 scoping review? | autonomous | Yes, with the changes listed in §3 for Mat to check | Local Canon | D-234 runs the review after Mat confirms the grouping. Mat accepted the batching and said proceed, but hasn't seen this file. Waiting would stop work Mat asked to go ahead; the grouping stays reversible. Two-way. | USER_EXPLICIT 2026-11-04 "All ohter recommendations are accepted. Proceed" |
| D-249 | Does the light accent stay in MEU-118? | autonomous | No: its own MEU-126 in Session 56, optional for rc.2 | Local Canon | Scoping review F1 (AC-2): separate cause, tests and human check, sharing no file with the device select. Mat's D-235 ruling names no release and the issue is P4, so rc.2 doesn't wait for it. Two-way. | — |
| D-250 | Does Batch E stay one session? | autonomous | No: MEU-123 in Session 54 and MEU-124 in Session 55, both still optional for rc.2 | Local Canon | Scoping review F2 (AC-4): they share no file, so one plan would chain unrelated work. Mat accepted the batch's place in the release, which doesn't change. Two-way. | — |
| D-267 | Do the two remaining fixes stay in one session now they share no file? | autonomous | Yes, Session 49 keeps MEU-113 and MEU-114 | Local Canon | D-250 split Batch E because its parts shared no file, and this is the same test. They stay together because Mat was told Session 49 shrinks to these two fixes, each is a few lines, and a second plan and review would cost more than it saves. Two-way. | — |
| D-277 | Does Codex recheck the grouping after round 1's fixes? | human | No. The scoping loop stays `changes_required`, recorded as not rechecked, and each session's plan review covers its own scope | Human-approved | Round 1's two findings were session splits, both applied (D-249, D-250). A recheck would cost at least 3,376,218 more tokens to confirm them, and no plan depends on the scoping approval. Alternatives: Mat reads §3 and §8, or a granted round 2 that would also re-read D-266 and D-267. Two-way. | USER_EXPLICIT 2026-11-05 "all recommendations are accpeted, proceed" |
| D-280 | Does the tooling session get an MEU? | autonomous | No: Session 49b is tracked by its issue | Local Canon | MEUs are build-plan product work and none has a home in `tools/`; earlier tooling plans ran without one (`docs/execution/plans/2026-09-26-framework-update-adoption/`). A build-plan home would add a matrix row for a change that ships nothing. Two-way. | — |

Carry-forward: each row appears in its consuming session's reflection `### Decisions Log` with stage `grouping`. The closeout validator reads every §8 row of the declared grouping, so a session's reflection lists them all; the lines below say which rows bear on that session.

- Session 49 carries D-240, D-242, D-243, D-244, D-246, D-248 and D-267.
- Session 49b carries D-280.
- Session 50 carries D-242 and D-247.
- Session 51 carries D-245.
- Session 52 carries D-245.
- Session 53 carries D-241.
- Session 54 carries D-242 and D-250.
- Session 55 carries D-250.
- Session 56 carries D-249.
- Session 57 carries D-243.

---

## 9. Scoping review criteria (D-234)

The independent MEU scoping review checks this proposal against these criteria; a blocking finding cites one of them.

**Status:** loop `s49-55-grouping-scoping-2026-11-04`, round 1 of 2 (Codex, 5,188,109 tokens): `changes_required`. AC-1, AC-3, AC-5 and AC-6 passed. Its two blocking findings are applied here and have not been rechecked: F1 (AC-2), MEU-118 bundled the light accent, now D-249; F2 (AC-4), Session 54 chained unrelated work, now D-250. The ledger refuses round 2 on tokens until a named human continues it. That review saw the FFmpeg build in Session 49. Mat's D-266 removed it afterwards, and that change hasn't been rechecked. On 2026-11-05 Mat ruled not to recheck it (D-277).

**MEU-119's amended expectation:** the review approved the amendment for `test_ac_75_9_raising_probe_or_vocab_is_model_load_error_neg` only and found no other named test affected, with one open point now in 03 §TTS load keeps the current model: the engine import test at `:735-752`.

- **AC-1** Every open, mitigated or dismissed known issue in `known-issues.yaml` maps to exactly one MEU or a named non-MEU disposition (§1 traceability), with no issue in two MEUs.
- **AC-2** Each MEU is one coherent change with its own TDD cycle: not two unrelated changes, and not so large that one plan cannot carry it.
- **AC-3** Every MEU's dependencies are registered MEUs, no session schedules an MEU before its prerequisites, and the critical path in §2 matches `meu-status.yaml`.
- **AC-4** Sessions follow one-project-per-session and shared-file continuity; split candidates are flagged; nothing P2 waits behind P3/P4 work without a stated reason.
- **AC-5** Every build-plan row in the homes has a source label (`Spec` / `Local Canon` / `Research-backed` / `Human-approved`) that matches the recorded decision and does not widen it.
- **AC-6** No Human-approved rule is reversed or amended without a recorded human ruling.
