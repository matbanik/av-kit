# Known Issues — av-kit

> Auto-generated from `known-issues.yaml` by `tools/issue_triage.py render`.
> Do not edit manually. Run `uv run python tools/issue_triage.py render` to regenerate.

**Total: 122** — Active: 37 | Mitigated: 1 | Resolved: 82

## Active Issues

| Sev | ID | Title | Component | Status | Discovered |
|-----|-----|-------|-----------|--------|------------|
| 🟠 | `TTS-ONNX-FP16-NONFINITE-AUDIO` | ONNX FP16 fails on some ordinary sentences with 'generated audio must b… | infrastructure | ⬜ open | 2026-11-04 |
| 🟡 | `TOOLING-SHARED-REGISTRY-COUPLING` | Framework-adoption tests depend on the shared P:/.agent registry and re… | infrastructure | ⬜ open | 2026-09-30 |
| 🟡 | `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | Non-English voices via the real espeak-ng CLI were never run end to end… | infrastructure | ⬜ open | 2026-10-15 |
| 🟡 | `YOUTUBE-CAPTIONS-IP-BLOCK` | YouTube is blocking caption requests from the maintainer's IP | infrastructure | ⬜ open | 2026-11-03 |
| 🟡 | `FFMPEG-LIBDVDCSS-BUNDLED` | The installer's FFmpeg has libdvdcss compiled in, and av-kit never uses… | infrastructure | ⬜ open | 2026-11-04 |
| 🟡 | `TOOLING-TRIAGE-SCANNER-FALSE-FINDINGS` | verify --deep and discover report noise, and verify stamps last_checked… | infrastructure | ⬜ open | 2026-11-04 |
| 🟢 | `CAPTURE-JOURNAL-VOLATILE` | Interactive capture completion journal is in-memory only | ui | ⬜ open | 2026-09-01 |
| 🟢 | `E2E-ELECTRON-LAUNCH-FLAG` | ELECTRON_RUN_AS_NODE in the IDE terminal breaks every Electron launch -… | ui | ⬜ open | 2026-09-02 |
| 🟢 | `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE` | Framework-adoption verifier tests pin the live AGENTS/GUARDRAILS to the… | infrastructure | ⬜ open | 2026-09-30 |
| 🟢 | `UI-ELECTRON-LAZY-INSTALL-RACE` | Electron 42 binary installs lazily on first require; parallel Vitest wo… | ui | ⬜ open | 2026-10-01 |
| 🟢 | `DOWNLOAD-QUEUE-DRAG-OVER-MISS` | Download-queue drag-over (A16 committed-over wait) occasionally misses… | ui | ⬜ open | 2026-10-01 |
| 🟢 | `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` | Capture viewport AC-66.14 middle-button pan origin occasionally off und… | ui | ⬜ open | 2026-10-17 |
| 🟢 | `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` | MCP audit container census network proofs are single-shot, so YouTube's… | mcp-server | ⬜ open | 2026-10-01 |
| 🟢 | `TTS-JA-ZH-G2P-EXTRAS` | Japanese and Mandarin Kokoro voices are listed but unavailable (no misa… | infrastructure | ⬜ open | 2026-10-15 |
| 🟢 | `TOOLING-TRIAGE-CLI-CP1252` | issue_triage.py bucket and --help crash with UnicodeEncodeError when ou… | infrastructure | ⬜ open | 2026-10-17 |
| 🟢 | `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | capture-inbox Electron specs occasionally hang in launch or close under… | ui | ⬜ open | 2026-10-25 |
| 🟢 | `CAPTURE-HINT-TEST-PRESENCE-ONLY` | Capture's AC-97.4 hint test checks that the shortcut props exist, not t… | ui | ⬜ open | 2026-10-26 |
| 🟢 | `BACKEND-READY-BEFORE-LISTEN` | The backend prints AVKIT_READY before its socket listens, so an immedia… | api | ⬜ open | 2026-11-03 |
| 🟢 | `TRANSCRIPT-ADD-CHANNEL-422` | Adding a channel returned 422 after about 8 minutes of enumeration | core | ⬜ open | 2026-11-03 |
| 🟢 | `TTS-SEGMENTS-LABEL-IS-PROGRESS-SCALE` | The TTS progress label reads 'Segments 0/1000' whatever the text's leng… | core | ⬜ open | 2026-11-03 |
| 🟢 | `TTS-AUDIO-RANDOM-FILE-NAMES` | Generated audio files have random ID names | core | ⬜ open | 2026-11-03 |
| 🟢 | `CONVERT-POSITIONS-NOT-RENUMBERED` | Convert's queue numbers aren't renumbered | core | ⬜ open | 2026-11-03 |
| 🟢 | `CONVERT-CUT-TIME-RAW-MS` | A cut job's row shows its times in raw milliseconds | ui | ⬜ open | 2026-11-03 |
| 🟢 | `DOWNLOADER-ADVANCED-PANEL-GAP` | An empty gap sits under Advanced on the Downloader page | ui | ⬜ open | 2026-11-03 |
| 🟢 | `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` | validate_closeout_artifacts --selftest fails when a .agent folder sits… | agent | ⬜ open | 2026-11-04 |
| 🟢 | `E2E-MAIN-PROCESS-ERRORS-UNWATCHED` | The E2E suite does not notice an uncaught exception in the main process | ui | ⬜ open | 2026-11-04 |
| 🟢 | `E2E-CLIPBOARD-PRIMER-EMPTY` | AC-88.12's clipboard primer read an empty clipboard for 5 s once | ui | ⬜ open | 2026-11-04 |
| 🟢 | `SETTINGS-DRAFT-STALE-BASELINE` | An unsaved capture settings edit freezes the other capture settings at… | ui | ⬜ open | 2026-11-04 |
| 🟢 | `CONVERT-ADVANCED-EDIT-REPLACED` | An Advanced edit on Convert snaps back when settings load late or the d… | ui | ⬜ open | 2026-11-04 |
| 🟢 | `GUI-READY-CHUNK-BOUNDARY` | A READY line split across output chunks can be missed, and two READY ch… | ui | ⬜ open | 2026-11-04 |
| 🟢 | `LIGHT-ACCENT-BELOW-AA-CONTRAST` | The light theme's accent colour puts button labels below 4.5:1 contrast | ui | ⬜ open | 2026-11-04 |
| 🟢 | `INSTALL-FOLDER-NAME-MISMATCH` | The installer uses %LOCALAPPDATA%\Programs\av-kit-ui, but the build pla… | ui | ⬜ open | 2026-11-04 |
| 🟢 | `CONSOLE-HOME-SCRUB-SHORT-FORM` | The Console's home-folder scrub misses the 8.3 short form of the home f… | core | ⬜ open | 2026-11-07 |
| 🟢 | `TRACKED-FILES-HOLD-HOME-PATH` | Tracked files name the maintainer's Windows home folder in full, user n… | agent | ⬜ open | 2026-11-07 |
| 🟢 | `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | The transcript queue E2E's seam reload failed once with ERR_ABORTED und… | ui | ⬜ open | 2026-11-07 |
| 🟢 | `TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS` | Two older title paths into transcript storage skip the lone-surrogate c… | core | ⬜ open | 2026-11-07 |
| 🟢 | `CONVERT-CUT-ENCODER-LABEL` | A cut is labelled with an encoder it does not use | core | ⬜ open | 2026-11-07 |

## Mitigated / Workaround

| Sev | ID | Title | Component | Status |
|-----|-----|-------|-----------|--------|
| 🟠 | `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | Claude Code VS Code auto-declines MCP elicitation, so USER_CONFIRM neve… | mcp-server | 🟢 mitigated |

## Resolved (82)

82 issues resolved. Query with `uv run python tools/issue_triage.py list --status resolved`.

---
*Managed by `tools/issue_triage.py`. See `known-issues.yaml` for full details including root cause, blast radius, and verification metadata.*
