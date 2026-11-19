# Known Issues — av-kit

> Auto-generated from `known-issues.yaml` by `tools/issue_triage.py render`.
> Do not edit manually. Run `uv run python tools/issue_triage.py render` to regenerate.

**Total: 149** — Active: 11 | Mitigated: 2 | Resolved: 134

## Active Issues

| Sev | ID | Title | Component | Status | Discovered |
|-----|-----|-------|-----------|--------|------------|
| 🟡 | `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | Non-English voices via the real espeak-ng CLI were never run end to end… | infrastructure | ⬜ open | 2026-10-15 |
| 🟡 | `FFMPEG-LIBDVDCSS-BUNDLED` | The installer's FFmpeg has libdvdcss compiled in, and av-kit never uses… | infrastructure | ⬜ open | 2026-11-04 |
| 🟡 | `CI-E2E-FLEET-HOST-UNTRACKED` | The full Electron E2E suite can run on a second Windows host (MINI_AIR1… | agent | ⬜ open | 2026-11-18 |
| 🟡 | `CAPTURE-TEXT-PIXEL-2PX-MINIAIR` | Capture text preview and its baked PNG land 2 px apart on the mini-air… | ui | ⬜ open | 2026-11-18 |
| 🟢 | `CAPTURE-JOURNAL-VOLATILE` | Interactive capture completion journal is in-memory only | ui | ⬜ open | 2026-09-01 |
| 🟢 | `TTS-JA-ZH-G2P-EXTRAS` | Japanese and Mandarin Kokoro voices are listed but unavailable (no misa… | infrastructure | ⬜ open | 2026-10-15 |
| 🟢 | `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | capture-inbox Electron specs occasionally hang in launch or close under… | ui | ⬜ open | 2026-10-25 |
| 🟢 | `TRANSCRIPT-ADD-CHANNEL-422` | Adding a channel returned 422 after about 8 minutes of enumeration | core | ⬜ open | 2026-11-03 |
| 🟢 | `E2E-CLIPBOARD-PRIMER-EMPTY` | AC-88.12's clipboard primer read an empty clipboard for 5 s once | ui | ⬜ open | 2026-11-04 |
| 🟢 | `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | The transcript queue E2E's seam reload failed once with ERR_ABORTED und… | ui | ⬜ open | 2026-11-07 |
| 🟢 | `E2E-HOVER-NO-POINTER-DEVICE` | settings AC-126.8 fails on a host with no mouse: the hover colour never… | ui | ⬜ open | 2026-11-18 |

## Mitigated / Workaround

| Sev | ID | Title | Component | Status |
|-----|-----|-------|-----------|--------|
| 🟠 | `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | Claude Code VS Code auto-declines MCP elicitation, so USER_CONFIRM neve… | mcp-server | 🟢 mitigated |
| 🟡 | `TOOLING-SHARED-REGISTRY-COUPLING` | Framework-adoption tests depend on the shared P:/.agent registry and re… | infrastructure | 🟢 mitigated |

## Resolved (134)

134 issues resolved. Query with `uv run python tools/issue_triage.py list --status resolved`.

---
*Managed by `tools/issue_triage.py`. See `known-issues.yaml` for full details including root cause, blast radius, and verification metadata.*
