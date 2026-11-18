# Known Issues — av-kit

> Auto-generated from `known-issues.yaml` by `tools/issue_triage.py render`.
> Do not edit manually. Run `uv run python tools/issue_triage.py render` to regenerate.

**Total: 146** — Active: 14 | Mitigated: 2 | Resolved: 128

## Active Issues

| Sev | ID | Title | Component | Status | Discovered |
|-----|-----|-------|-----------|--------|------------|
| 🟡 | `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | Non-English voices via the real espeak-ng CLI were never run end to end… | infrastructure | ⬜ open | 2026-10-15 |
| 🟡 | `FFMPEG-LIBDVDCSS-BUNDLED` | The installer's FFmpeg has libdvdcss compiled in, and av-kit never uses… | infrastructure | ⬜ open | 2026-11-04 |
| 🟢 | `CAPTURE-JOURNAL-VOLATILE` | Interactive capture completion journal is in-memory only | ui | ⬜ open | 2026-09-01 |
| 🟢 | `DOWNLOAD-QUEUE-DRAG-OVER-MISS` | Download-queue drag-over (A16 committed-over wait) occasionally misses… | ui | ⬜ open | 2026-10-01 |
| 🟢 | `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` | Capture viewport AC-66.14 middle-button pan origin occasionally off und… | ui | ⬜ open | 2026-10-17 |
| 🟢 | `TTS-JA-ZH-G2P-EXTRAS` | Japanese and Mandarin Kokoro voices are listed but unavailable (no misa… | infrastructure | ⬜ open | 2026-10-15 |
| 🟢 | `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | capture-inbox Electron specs occasionally hang in launch or close under… | ui | ⬜ open | 2026-10-25 |
| 🟢 | `TRANSCRIPT-ADD-CHANNEL-422` | Adding a channel returned 422 after about 8 minutes of enumeration | core | ⬜ open | 2026-11-03 |
| 🟢 | `DOWNLOADER-ADVANCED-PANEL-GAP` | An empty gap sits under Advanced on the Downloader page | ui | ⬜ open | 2026-11-03 |
| 🟢 | `E2E-CLIPBOARD-PRIMER-EMPTY` | AC-88.12's clipboard primer read an empty clipboard for 5 s once | ui | ⬜ open | 2026-11-04 |
| 🟢 | `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | The transcript queue E2E's seam reload failed once with ERR_ABORTED und… | ui | ⬜ open | 2026-11-07 |
| 🟢 | `HELP-F1-BEFORE-LAZY-MOUNT-LOST` | F1 on Convert or Capture can be lost while the page is still loading | ui | ⬜ open | 2026-11-17 |
| 🟢 | `UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT` | npm run preview opens no window when ELECTRON_RUN_AS_NODE is set in the… | ui | ⬜ open | 2026-11-17 |
| 🟢 | `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` | Session 64's eval describe capture decodes the MCP server's UTF-8 throu… | agent | ⬜ open | 2026-11-18 |

## Mitigated / Workaround

| Sev | ID | Title | Component | Status |
|-----|-----|-------|-----------|--------|
| 🟠 | `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | Claude Code VS Code auto-declines MCP elicitation, so USER_CONFIRM neve… | mcp-server | 🟢 mitigated |
| 🟡 | `TOOLING-SHARED-REGISTRY-COUPLING` | Framework-adoption tests depend on the shared P:/.agent registry and re… | infrastructure | 🟢 mitigated |

## Resolved (128)

128 issues resolved. Query with `uv run python tools/issue_triage.py list --status resolved`.

---
*Managed by `tools/issue_triage.py`. See `known-issues.yaml` for full details including root cause, blast radius, and verification metadata.*
