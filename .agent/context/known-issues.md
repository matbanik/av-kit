# Known Issues — av-kit

> Auto-generated from `known-issues.yaml` by `tools/issue_triage.py render`.
> Do not edit manually. Run `uv run python tools/issue_triage.py render` to regenerate.

**Total: 167** — Active: 17 | Mitigated: 2 | Resolved: 146

## Active Issues

| Sev | ID | Title | Component | Status | Discovered |
|-----|-----|-------|-----------|--------|------------|
| 🟡 | `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | Non-English voices via the real espeak-ng CLI were never run end to end… | infrastructure | ⬜ open | 2026-10-15 |
| 🟡 | `FFMPEG-LIBDVDCSS-BUNDLED` | The installer's FFmpeg has libdvdcss compiled in, and av-kit never uses… | infrastructure | ⬜ open | 2026-11-04 |
| 🟡 | `CAPTURE-INBOX-CHANGE-KEEPS-OLD-SHOTS` | After the inbox folder is changed, the Capture list still shows the sho… | core | ⬜ open | 2026-11-26 |
| 🟡 | `APP-NO-IN-APP-UPDATE` | The app cannot update itself: a new version means a manual download fro… | infrastructure | ⬜ open | 2026-11-26 |
| 🟢 | `CAPTURE-JOURNAL-VOLATILE` | Interactive capture completion journal is in-memory only | ui | ⬜ open | 2026-09-01 |
| 🟢 | `TTS-JA-ZH-G2P-EXTRAS` | Japanese and Mandarin Kokoro voices are listed but unavailable (no misa… | infrastructure | ⬜ open | 2026-10-15 |
| 🟢 | `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | capture-inbox Electron specs occasionally hang in launch or close under… | ui | ⬜ open | 2026-10-25 |
| 🟢 | `TRANSCRIPT-ADD-CHANNEL-422` | Adding a channel returned 422 after about 8 minutes of enumeration | core | ⬜ open | 2026-11-03 |
| 🟢 | `E2E-CLIPBOARD-PRIMER-EMPTY` | AC-88.12's clipboard primer read an empty clipboard for 5 s once | ui | ⬜ open | 2026-11-04 |
| 🟢 | `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | The transcript queue E2E's seam reload failed once with ERR_ABORTED und… | ui | ⬜ open | 2026-11-07 |
| 🟢 | `CAPTURE-TEXT-PLATE-METRICS-RESIDUAL` | The preview text plate differs from the bake by 1 to 2 px in a few cases | ui | ⬜ open | 2026-11-19 |
| 🟢 | `TOOLING-RUFF-TOOLS-UNCLEAN` | ruff check and ruff format --check fail over tools/ outside CI's lint s… | agent | ⬜ open | 2026-11-20 |
| 🟢 | `CAPTURE-HOTKEY-TEXT-HARDCODED` | Capture texts say F2 after the capture key is changed | ui | ⬜ open | 2026-11-26 |
| 🟢 | `CAPTURE-ZOOM-NO-SCROLLBARS` | A zoomed Capture image has no scroll bars at the bottom and right | ui | ⬜ open | 2026-11-26 |
| 🟢 | `GUI-ENTRY-SECTIONS-NO-EMPHASIS` | The URL entry of Download and Transcript and the How it works card look… | ui | ⬜ open | 2026-11-26 |
| 🟢 | `DOWNLOADER-ADVANCED-LOOKS-LIKE-TEXT` | The Downloader's Advanced control looks like plain text, and its open p… | ui | ⬜ open | 2026-11-26 |
| 🟢 | `DOWNLOADER-COOKIE-PROFILE-UNLABELED` | The browser profile field under the Browser select has no label | ui | ⬜ open | 2026-11-26 |

## Mitigated / Workaround

| Sev | ID | Title | Component | Status |
|-----|-----|-------|-----------|--------|
| 🟠 | `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | Claude Code VS Code auto-declines MCP elicitation, so USER_CONFIRM neve… | mcp-server | 🟢 mitigated |
| 🟡 | `TOOLING-SHARED-REGISTRY-COUPLING` | Framework-adoption tests depend on the shared P:/.agent registry and re… | infrastructure | 🟢 mitigated |

## Resolved (146)

146 issues resolved. Query with `uv run python tools/issue_triage.py list --status resolved`.

---
*Managed by `tools/issue_triage.py`. See `known-issues.yaml` for full details including root cause, blast radius, and verification metadata.*
