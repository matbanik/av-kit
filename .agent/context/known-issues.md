# Known Issues — av-kit

> Auto-generated from `known-issues.yaml` by `tools/issue_triage.py render`.
> Do not edit manually. Run `uv run python tools/issue_triage.py render` to regenerate.

**Total: 142** — Active: 24 | Mitigated: 2 | Resolved: 114

## Active Issues

| Sev | ID | Title | Component | Status | Discovered |
|-----|-----|-------|-----------|--------|------------|
| 🟠 | `TTS-ONNX-FP16-NONFINITE-AUDIO` | ONNX FP16 fails on some ordinary sentences with 'generated audio must b… | infrastructure | ⬜ open | 2026-11-04 |
| 🟡 | `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | Non-English voices via the real espeak-ng CLI were never run end to end… | infrastructure | ⬜ open | 2026-10-15 |
| 🟡 | `YOUTUBE-CAPTIONS-IP-BLOCK` | YouTube is blocking caption requests from the maintainer's IP | infrastructure | ⬜ open | 2026-11-03 |
| 🟡 | `FFMPEG-LIBDVDCSS-BUNDLED` | The installer's FFmpeg has libdvdcss compiled in, and av-kit never uses… | infrastructure | ⬜ open | 2026-11-04 |
| 🟡 | `QUEUE-PAUSE-NO-FEEDBACK` | Convert and Downloader Pause gives no feedback while the current job ru… | ui | ⬜ open | 2026-11-16 |
| 🟢 | `CAPTURE-JOURNAL-VOLATILE` | Interactive capture completion journal is in-memory only | ui | ⬜ open | 2026-09-01 |
| 🟢 | `DOWNLOAD-QUEUE-DRAG-OVER-MISS` | Download-queue drag-over (A16 committed-over wait) occasionally misses… | ui | ⬜ open | 2026-10-01 |
| 🟢 | `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` | Capture viewport AC-66.14 middle-button pan origin occasionally off und… | ui | ⬜ open | 2026-10-17 |
| 🟢 | `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` | MCP audit container census network proofs are single-shot, so YouTube's… | mcp-server | ⬜ open | 2026-10-01 |
| 🟢 | `TTS-JA-ZH-G2P-EXTRAS` | Japanese and Mandarin Kokoro voices are listed but unavailable (no misa… | infrastructure | ⬜ open | 2026-10-15 |
| 🟢 | `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | capture-inbox Electron specs occasionally hang in launch or close under… | ui | ⬜ open | 2026-10-25 |
| 🟢 | `TRANSCRIPT-ADD-CHANNEL-422` | Adding a channel returned 422 after about 8 minutes of enumeration | core | ⬜ open | 2026-11-03 |
| 🟢 | `DOWNLOADER-ADVANCED-PANEL-GAP` | An empty gap sits under Advanced on the Downloader page | ui | ⬜ open | 2026-11-03 |
| 🟢 | `E2E-CLIPBOARD-PRIMER-EMPTY` | AC-88.12's clipboard primer read an empty clipboard for 5 s once | ui | ⬜ open | 2026-11-04 |
| 🟢 | `INSTALL-FOLDER-NAME-MISMATCH` | The installer uses %LOCALAPPDATA%\Programs\av-kit-ui, but the build pla… | ui | ⬜ open | 2026-11-04 |
| 🟢 | `TRACKED-FILES-HOLD-HOME-PATH` | Tracked files name the maintainer's Windows home folder in full, user n… | agent | ⬜ open | 2026-11-07 |
| 🟢 | `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | The transcript queue E2E's seam reload failed once with ERR_ABORTED und… | ui | ⬜ open | 2026-11-07 |
| 🟢 | `MCP-AUDIT-BASELINE-PENDING-CROP` | The committed MCP audit baseline has no avkit_capture.crop entry | mcp-server | ⬜ open | 2026-11-08 |
| 🟢 | `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` | Claude Code doesn't show a model the per-action text in _meta.action_de… | mcp-server | ⬜ open | 2026-11-10 |
| 🟢 | `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE` | Real-ffmpeg frame grabs near a clip's last frame occasionally fail (fra… | core | ⬜ open | 2026-11-15 |
| 🟢 | `UI-DEV-ELECTRON-RUN-AS-NODE-SILENT` | npm run dev opens no window when ELECTRON_RUN_AS_NODE is set in the IDE… | ui | ⬜ open | 2026-09-03 |
| 🟢 | `E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED` | E2E does not watch unhandled promise rejections in the Electron main pr… | ui | ⬜ open | 2026-11-15 |
| 🟢 | `CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE` | Convert Ctrl+O delivery lost before the lazy page mounts | ui | ⬜ open | 2026-11-16 |
| 🟢 | `PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD` | Full Python suite: tests with 5-second worker waits fail when the host… | infrastructure | ⬜ open | 2026-11-16 |

## Mitigated / Workaround

| Sev | ID | Title | Component | Status |
|-----|-----|-------|-----------|--------|
| 🟠 | `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | Claude Code VS Code auto-declines MCP elicitation, so USER_CONFIRM neve… | mcp-server | 🟢 mitigated |
| 🟡 | `TOOLING-SHARED-REGISTRY-COUPLING` | Framework-adoption tests depend on the shared P:/.agent registry and re… | infrastructure | 🟢 mitigated |

## Resolved (114)

114 issues resolved. Query with `uv run python tools/issue_triage.py list --status resolved`.

---
*Managed by `tools/issue_triage.py`. See `known-issues.yaml` for full details including root cause, blast radius, and verification metadata.*
