# Known Issues — av-kit

> Auto-generated from `known-issues.yaml` by `tools/issue_triage.py render`.
> Do not edit manually. Run `uv run python tools/issue_triage.py render` to regenerate.

**Total: 73** — Active: 19 | Mitigated: 1 | Resolved: 52

## Active Issues

| Sev | ID | Title | Component | Status | Discovered |
|-----|-----|-------|-----------|--------|------------|
| 🟡 | `TOOLING-SHARED-REGISTRY-COUPLING` | Framework-adoption tests depend on the shared P:/.agent registry and re… | infrastructure | ⬜ open | 2026-09-30 |
| 🟡 | `FFMPEG-GPL-BUILD` | The installer ships a GPL-3.0 BtbN FFmpeg build (libx264/libx265) | infrastructure | ⬜ open | 2026-10-15 |
| 🟡 | `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | Non-English voices via the real espeak-ng CLI were never run end to end… | infrastructure | ⬜ open | 2026-10-15 |
| 🟢 | `CAPTURE-JOURNAL-VOLATILE` | Interactive capture completion journal is in-memory only | ui | ⬜ open | 2026-09-01 |
| 🟢 | `E2E-ELECTRON-LAUNCH-FLAG` | ELECTRON_RUN_AS_NODE in the IDE terminal breaks every Electron launch -… | ui | ⬜ open | 2026-09-02 |
| 🟢 | `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE` | Framework-adoption verifier tests pin the live AGENTS/GUARDRAILS to the… | infrastructure | ⬜ open | 2026-09-30 |
| 🟢 | `UI-ELECTRON-LAZY-INSTALL-RACE` | Electron 42 binary installs lazily on first require; parallel Vitest wo… | ui | ⬜ open | 2026-10-01 |
| 🟢 | `DOWNLOAD-QUEUE-DRAG-OVER-MISS` | Download-queue drag-over (A16 committed-over wait) occasionally misses… | ui | ⬜ open | 2026-10-01 |
| 🟢 | `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` | Capture viewport AC-66.14 middle-button pan origin occasionally off und… | ui | ⬜ open | 2026-10-17 |
| 🟢 | `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` | MCP audit container census network proofs are single-shot, so YouTube's… | mcp-server | ⬜ open | 2026-10-01 |
| 🟢 | `TTS-JA-ZH-G2P-EXTRAS` | Japanese and Mandarin Kokoro voices are listed but unavailable (no misa… | infrastructure | ⬜ open | 2026-10-15 |
| 🟢 | `FFMPEG-PIN-URL-404` | The pinned BtbN FFmpeg release URL returns 404 | infrastructure | ⬜ open | 2026-10-15 |
| 🟢 | `INSTALLER-SHIPS-FFMPEG-ZIP` | The installer ships the 168 MB ffmpeg-pin.zip download archive | infrastructure | ⬜ open | 2026-10-15 |
| 🟢 | `FETCH-FFMPEG-EXIT-CODES` | fetch_ffmpeg_windows.ps1 exit codes 2 to 5 are never returned (Write-Er… | infrastructure | ⬜ open | 2026-10-15 |
| 🟢 | `NOTICES-SPACY-TRANSITIVE` | THIRD_PARTY_NOTICES omits most bundled backend dependencies (spaCy's tr… | infrastructure | ⬜ open | 2026-10-15 |
| 🟢 | `TOOLING-TRIAGE-CLI-CP1252` | issue_triage.py bucket and --help crash with UnicodeEncodeError when ou… | infrastructure | ⬜ open | 2026-10-17 |
| 🟢 | `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | capture-inbox Electron specs occasionally hang in launch or close under… | ui | ⬜ open | 2026-10-25 |
| 🟢 | `PACKAGING-MCP-SNIPPET-TOKEN-STALE` | test_mcp_snippet_keys (AC-25.7) still requires AVKIT_API_TOKEN in mcp.j… | infrastructure | ⬜ open | 2026-10-25 |
| 🟢 | `CAPTURE-HINT-TEST-PRESENCE-ONLY` | Capture's AC-97.4 hint test checks that the shortcut props exist, not t… | ui | ⬜ open | 2026-10-26 |

## Mitigated / Workaround

| Sev | ID | Title | Component | Status |
|-----|-----|-------|-----------|--------|
| 🟠 | `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | Claude Code VS Code auto-declines MCP elicitation, so USER_CONFIRM neve… | mcp-server | 🟢 mitigated |

## Resolved (52)

52 issues resolved. Query with `uv run python tools/issue_triage.py list --status resolved`.

---
*Managed by `tools/issue_triage.py`. See `known-issues.yaml` for full details including root cause, blast radius, and verification metadata.*
