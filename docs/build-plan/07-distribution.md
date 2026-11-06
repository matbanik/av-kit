# Phase 7 — Distribution

> Part of [av-kit Build Plan](../BUILD_PLAN.md) | Prerequisites: [Phase 4](04-rest-api.md), [Phase 5](05-mcp-server.md), [Phase 6](06-gui.md)

---

## Goal

Ship a Windows-first desktop installer that starts the Electron shell, a localhost FastAPI backend, and (optionally) an MCP stdio server — without bundling Kokoro weights. After install, everything except YouTube / Hugging Face calls and the one-time pinned spaCy model wheel (`github.com/explosion/spacy-models` releases; [03 §TTS runtime assets](03-service-layer.md#tts-runtime-assets-residual)) works offline.

| Source | Decision |
|--------|----------|
| Spec | [Phase 2](02-infrastructure.md) `{app_data}/avkit.db`, FFmpeg probe order; [Phase 4](04-rest-api.md) bind `127.0.0.1`, dual Bearer; [Phase 5](05-mcp-server.md) `AVKIT_API_*`; [Phase 6](06-gui.md) spawn + splash |
| Local Canon | [APPLICATION_PURPOSE.md §6](../../_inspiration/APPLICATION_PURPOSE.md): &lt; 3s usable UI, &lt; 500MB without models, Windows 10/11 primary |
| Research-backed | PyInstaller onefile/onedir for FastAPI; electron-builder NSIS `extraResources`; do not stuff CUDA or `.onnx` weights into the installer |
| Human-approved | 2026-08-18 phase specs: no job/media blobs in SQLite; MCP token ≠ GUI nonce; models via Model Manager |

This file **locks** choices the old stub left as “OR”. If a later phase needs a new persistable path or setting, change Phase 1/6 first.

---

## What ships vs what does not

| In the installer | Not in the installer |
|------------------|----------------------|
| Electron app (`ui` build) | Kokoro `.onnx` / `.pth` weights |
| FastAPI backend (PyInstaller) | CUDA / cuDNN |
| Bundled `ffmpeg` + `ffprobe` (Windows) | YouTube cookies |
| `onnxruntime` (CPU) | User downloads, transcripts, TTS output |
| `mcp-server/dist` + IDE snippet | PyTorch runtime (see Models) |
| Empty app-data scaffold on first run | `avkit.db` from a dev machine |

Disk target: **&lt; 500MB installed, without models** ([APPLICATION_PURPOSE.md §6](../../_inspiration/APPLICATION_PURPOSE.md)). Weights stay in `tts.models_directory` (default `~/.avkit/models/` or `%USERPROFILE%/.avkit/models/`).

---

## On-disk layout after install

```
{install}/                         # e.g. %LOCALAPPDATA%/Programs/av-kit
├── av-kit.exe                     # Electron
├── resources/
│   ├── extra/
│   │   ├── avkit-backend/         # PyInstaller onedir (preferred over onefile)
│   │   │   └── avkit-backend.exe
│   │   ├── ffmpeg/
│   │   │   ├── ffmpeg.exe
│   │   │   └── ffprobe.exe
│   │   └── mcp-server/            # compiled JS (Phase 5 dist/)
│   └── app.asar
└── ...

{app_data}/                        # %LOCALAPPDATA%/av-kit  (Phase 2)
├── avkit.db
├── logs/console.log               # errors always; every line if app.log_to_file
├── mcp-token.txt                  # provisioned MCP Bearer (created first run)
└── ...

{models}/                          # setting tts.models_directory
└── (downloaded variants)

HF cache (voices): ~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/
```

SQLite, logs, and the MCP token stay in `{app_data}`, **not** under `{install}` (upgrades must not wipe the queue).

---

## Backend packaging (PyInstaller)

**Form:** `onedir` (`avkit-backend/`), not `onefile`. Onefile extracts to a temp dir on every launch and fights the &lt; 3s / &lt; 2s Python-healthy budget ([06-gui.md](06-gui.md) `startup.python_spawn_ms`).

**Entry:** FastAPI `create_app()` + uvicorn, bind **`127.0.0.1`**, port **ephemeral** (`--port 0`). After listen, write the runtime descriptor (below) **atomically**, then print `AVKIT_READY port={n} instance={id}` on stdout. Do not bind `0.0.0.0`.

### Runtime descriptor (`{app_data}/backend.json`)

Zorivest twin: `ui/src/main/backend-descriptor.ts` (adapt; av-kit has no trading DB identity fields).

```json
{
  "schema_version": 1,
  "pid": 12345,
  "instance_id": "uuid-per-process",
  "executable_path": "C:/Program Files/av-kit/resources/avkit-backend/avkit-backend.exe",
  "host": "127.0.0.1",
  "port": 51234,
  "bind": "127.0.0.1",
  "api_base": "http://127.0.0.1:51234/api/v1",
  "app_data": "C:/Users/…/AppData/Local/av-kit",
  "started_at": "2026-08-18T20:00:00Z"
}
```

**Never** write the GUI nonce or MCP token into this file. Also write `{app_data}/backend-port.txt` (port digits only) as a convenience sibling — **not** a second source of truth.

**Ownership model (locked — no attach):** Electron never reuses a backend it did not spawn. The spawn nonce lives only in the owning main process. There is no credential in `backend.json` that a second Electron could present. **Never** decide “this pid is ours” from descriptor fields alone.

**Resolved identity (Electron, not the file):**

| Name | Source |
|------|--------|
| `ours.exe` | Bundled backend path from `process.resourcesPath` (`…/resources/avkit-backend/avkit-backend.exe` on Windows). Not `backend.json.executable_path`. |
| `ours.app_data` | The `--app-data` path this Electron would pass (same resolver as Phase 2). Not `backend.json.app_data`. |

**Live identity (OS query of `pid`):** query the running process. Windows: `QueryFullProcessImageNameW` (image) + process command line (`Win32_Process.CommandLine` or equivalent). Linux: `/proc/{pid}/exe` + `/proc/{pid}/cmdline`. macOS: `proc_pidpath` + `KERN_PROCARGS2`. Normalize paths (realpath, Windows case/`\\?\`) before compare.

| Query outcome | Action |
|---------------|--------|
| Image or cmdline query **fails** (access denied, empty, pid gone mid-check) | **Refuse**. Do not kill. |
| `live.image` ≠ `ours.exe` | **Refuse**. Do not kill. |
| `live.cmdline` lacks `--app-data` whose argument equals `ours.app_data` | **Refuse**. Do not kill. |

Descriptor fields, **if** the file parses as a schema we understand, are a **consistency check only**: `descriptor.app_data` must equal `ours.app_data` **and** `descriptor.executable_path` must equal `live.image`. Either mismatch → **Refuse**. Do not kill. Do not use `descriptor.executable_path` as the “is this our binary?” target.

| Condition | Action |
|-----------|--------|
| This process **lost** `app.requestSingleInstanceLock()` | Focus the first window and **exit**. Do not spawn, attach, or kill |
| No file, or `pid` not running | Spawn (overwrite descriptor) |
| `pid` running, we hold the lock, **and** the live-identity proof above succeeds | **Owned orphan** (GUI crashed). SIGTERM that pid, wait until it exits, then spawn with a **new** nonce |
| `pid` running and live-identity proof fails | **Refuse**. Do not kill. Surface “another av-kit backend is using this data dir” |
| File has unknown keys / `schema_version` we do not support, and `pid` **is running** | **Refuse** + upgrade/downgrade message. **Never spawn** and **never kill** |
| File has unknown keys / newer schema, and `pid` is **dead** | Spawn (overwrite) |

On owned-child exit, delete or tombstone the descriptor so MCP does not target a dead port. Tests: fresh spawn; Electron crash + surviving backend; second launch; foreign/stale descriptor; **PID reuse** (file claims our exe, live image is foreign → refuse, no SIGTERM); query failure → refuse; `--app-data` mismatch → refuse; parseable descriptor vs live image mismatch → refuse; unsupported schema + live pid; shutdown ownership.

**CLI (PythonManager spawn):**

```
avkit-backend.exe --token <GUI_NONCE> --mcp-token <PROVISIONED> --port 0 --app-data <path>
```

| Flag | Rule |
|------|------|
| `--token` | Ephemeral GUI Bearer ([Phase 4](04-rest-api.md)). New each Electron launch |
| `--mcp-token` | Stable key from `{app_data}/mcp-token.txt` (create if missing). MCP uses this, **not** the GUI nonce ([Phase 5](05-mcp-server.md)) |
| `--port 0` | OS-assigned localhost port; **never** expose port 0 to the renderer. Publish `api_base` from `backend.json` after bind |
| `--app-data` | Must match Phase 2 `{app_data}` so API + MCP share `avkit.db` (WAL) |

`GET /api/v1/health` stays **unauthenticated** so the splash can poll before the renderer has the nonce.

**Hidden imports (minimum):** `yt_dlp`, `youtube_transcript_api`, `sqlalchemy`, `pydantic`, `uvicorn`, `avkit_api`, `avkit_core`, `avkit_infra`, `structlog`. Add others only when a smoke run fails on a clean machine.

**Do not collect:**

- Files under `tts.models_directory` or HF hub cache
- Dev `avkit.db`
- `.env` with secrets

**GPU:** Detect CUDA / MPS at **runtime** (`DeviceType.Auto`). Do not ship a CUDA-enabled wheel in the NSIS payload. CPU `onnxruntime` is enough for first launch. **Phase 8 Convert** uses the same rule: NVENC/AMF/QSV come from the **system GPU driver** + the bundled FFmpeg build; missing hardware encoders → software fallback ([08-video-conversion.md](08-video-conversion.md)). Not a Phase 7 ship-gate.

**Phase 9 Capture** tray icon assets ship with the Electron app (`extraResources` / `build/icon.*` as needed). The global hotkey is runtime Electron, but the **region picker is an installer artifact**: `native/region-picker/publish/` is published by `dotnet publish` and shipped as the `region-picker/` `extraResources` entry, so the packaged app resolves it at `{process.resourcesPath}/region-picker/avkit-region-picker.exe` ([09-screenshot-capture.md](09-screenshot-capture.md)). Not a Phase 7 ship-gate.

**spaCy (TTS chunk step):** If the `chunk` prepare step needs `en_core_web_sm`, either bundle that small model next to the backend or degrade: `prepare` with `chunk` enabled returns 503/`FFmpeg`-style dependency error only for that step — do not fail the whole app at startup.

---

## FFmpeg (locked)

**Windows (ship gate):** bundle `ffmpeg.exe` + `ffprobe.exe` in `resources/ffmpeg/`.

**Probe order** (Phase 2 `MediaPort.is_available`, now concrete):

1. Setting `downloader.ffmpeg_path` if set and the file exists ([06-gui.md](06-gui.md) key table)
2. Bundled `{install}/resources/ffmpeg/ffmpeg.exe`
3. `PATH`

Missing after all three → `FFmpegNotFoundError`; Settings → Check Dependencies shows unavailable. Audio-only formats that need convert and TTS MP3 fail at use time, not at splash.

**macOS / Linux (secondary):** bundle if the CI job can; otherwise document Homebrew/`ffmpeg` on PATH. Same probe order.

Do not leave “bundle OR PATH” as an open product decision for Windows.

---

## Electron packaging (electron-builder)

| Item | Rule |
|------|------|
| Target | Windows **NSIS** (x64). macOS/Linux configs may exist but are not the Phase 7 exit gate |
| `extraResources` | `avkit-backend/`, `ffmpeg/`, `mcp-server/`, `region-picker/` (self-contained .NET 8 `win-x64` publish of `native/region-picker`, built by `npm run build:picker` before `electron-builder`) |
| Icon / metadata | av-kit name, version from `ui/package.json` |
| Auto-update | `electron-updater` **optional**; do not block ship on it |
| Code signing | If certs exist, sign; if not, ship unsigned and document SmartScreen — not a domain change |
| Login item (MEU-61) | Per-user Run key from Settings; **not** a Windows service. See below |

### Login item uninstall (MEU-61)

Packaged NSIS installs may register a **per-user** login item from Settings ([06-gui.md §Startup](06-gui.md#startup-login-item)). This is not WinSW, not LocalSystem, and not “Auto-start on boot” in the Zorivest Service Manager sense.

- `app.setLoginItemSettings` `path` = `process.execPath` (NSIS layout). Do **not** use the Electron docs’ Squirrel `Update.exe` stub (one directory up).
- Registry **value** name is `LOGIN_ITEM_NAME` = `com.avkit.app` (same string as electron-builder `appId`). Pass it as `name` on every write.
- `ui/build/installer.nsh` defines `customUnInstall`. After stripping NSIS `;` comments, the remaining code **must** contain **exactly two** executable `DeleteRegValue HKCU` statements (a Run entry is a value, not a key):
  1. `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` / value `com.avkit.app` (the line must **not** contain `StartupApproved`)
  2. `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run` / value `com.avkit.app`
  A comment that only mentions the second key does **not** satisfy this contract.
- `ui/electron-builder.yml` `nsis.include` **value** (the YAML mapping under `nsis:`, not a comment and not a string elsewhere in the file) is `build/installer.nsh` (same relative form as Zorivest; file lives at `ui/build/installer.nsh`).
- Uninstall still does **not** delete `{app_data}` unless the user opts in (`deleteAppDataOnUninstall: false` stays).

### PythonManager (must match Phase 6)

Copy-adapt Zorivest `python-manager.ts` / `backend-descriptor.ts` / `backend-activation.ts`.

1. Show splash.
2. Take the single-instance lock, then spawn-or-reap using the table above. **Never attach.** Spawn flags: `--token`, `--mcp-token`, `--port 0`, `--app-data`.
3. Wait for valid `backend.json` whose `pid` equals the child we just spawned (or `AVKIT_READY`). Then poll `GET {api_base}/health` (100ms → 5s). Record `startup.python_spawn_ms`.
4. Only then resolve `getBackendUrl` / `getToken` invokes. Main window may already be painted with skeletons.
5. On quit of the **owned** child: SIGTERM/taskkill; backend lifespan cancels processors and unloads TTS. Do not kill a refused foreign pid.
6. `POST /health/startup-metrics` uses the **GUI** Bearer, not the MCP token.

`getBackendUrl()` includes `/api/v1`. `getToken()` is the spawn nonce only. Both are async.

---

## Kokoro / models

Unchanged from the old stub, aligned with Phase 2 seed ids:

| id | In installer? |
|----|----------------|
| `kokoro-onnx-fp32` | No — Model Manager download |
| `kokoro-onnx-fp16` | No — Model Manager download |
| `kokoro-onnx-int8` | No |
| `kokoro-pt-fp32` | No weights **and** no PyTorch wheel in NSIS |

**ONNX** variants load with bundled `onnxruntime`.  
**Known gap (Session 27):** in the frozen app, `kokoro.KPipeline` is `None` because the packaging excludes torch. So even ONNX generation, which uses the pipeline's G2P, does not synthesize in the packaged build today. This contradicts the line above; it is tracked as `TTS-PACKAGED-RUNTIME-EXCLUDED` and fixed by [MEU-72](#packaged-onnx-tts-runtime-residual).  
**PyTorch** variant: a build that can't import the runtime lists it disabled with a reason in `/models/available` and refuses its download with a 409 ([MEU-117](03-service-layer.md#tts-build-capability-residual), triage D-217). There is no optional extra, no runtime download and no bundled torch. `npm run dev` has torch in the repo's `.venv` and loads the variant as before.

Voices: first-use HF cache (`hexgrad/Kokoro-82M`). Offline after that.

First-run Model Manager test (checklist): wipe `{models}` + HF cache → download INT8 → load → one `generate`.

<a id="packaged-onnx-tts-runtime-residual"></a>

### Packaged ONNX TTS runtime (residual)

> **MEU-72.** Registered 2026-10-09 from `TTS-PACKAGED-RUNTIME-EXCLUDED`. `packaging/avkit-backend.spec:35` excludes torch and kokoro imports torch, so `KPipeline` is `None` in the frozen app (`tts/adapter.py:15-22`); there are no hiddenimports for the G2P stack (spec:14-24). ONNX generation therefore fails in the installed build.

> **Delivered (Session 32).** The adapter phonemizes through av-kit's own `KokoroG2p` (misaki English plus the eSpeak NG CLI) and chunks at 510 symbols; the ONNX path runs without torch or kokoro, and the PyTorch path calls `KModel` only. The spec bundles misaki, spaCy, num2words (as replaceable `.py`) and onnxruntime, and excludes kokoro, phonemizer, espeakng_loader and `misaki.espeak`. `packaging/THIRD_PARTY_NOTICES.md` ships as `resources/THIRD_PARTY_NOTICES.md`, beside FFmpeg's `LICENSE.txt`. `tools/smoke_packaged_tts.py` is the `PACKAGE_SMOKE` stage: it provisions online, builds the installer, then generates offline from a copy of the backend behind a dead proxy and records the shipped MCP entry. Plan `docs/execution/plans/2026-10-14-tts-engine-runtime/`.

| Rule | Contract | Source |
|------|----------|--------|
| No torch | torch stays out of the installer (500 MB budget) | Spec this file (PyTorch line above; exit checklist) |
| ONNX without torch | The ONNX path runs the G2P directly and `onnxruntime`, with no dependency on `kokoro.KPipeline`/`KModel` or torch; the PyTorch path keeps using kokoro when torch is present | Triage D-41; Research-backed (kokoro-onnx runs Kokoro on onnxruntime without torch) |
| Bundle | PyInstaller hiddenimports/data cover the G2P stack; spaCy and voice packs stay managed downloads (MEU-62, MEU-73) | Human-approved D-22 |
| Smoke | A packaged-build check loads an ONNX variant and generates a short WAV; the same installer run records whether the shipped MCP entry starts (`MCP-PACKAGED-ENTRY-UNREACHABLE`, candidate) | Triage D-41 |
| Tests | Unit/regression: ONNX generate with torch import blocked yields samples; the packaged smoke is a local `WINDOWS_GATE` stage | Local Canon cloud-local §1 |

---

## MCP on a shipped machine

Ship `resources/mcp-server/`: the self-contained `index.mjs` and `LICENSES.txt` from [§MCP server bundle (residual)](#mcp-server-bundle-residual). The Settings MCP card's setup prompt ([§MCP setup prompt (residual)](#mcp-setup-prompt-residual)) registers that entry per client.

Document for Cursor / Claude / Windsurf (`mcp.json`):

| Env | Value |
|-----|--------|
| `AVKIT_API_BASE` | Optional override. If unset, the MCP client **must** read `{app_data}/backend.json` → `api_base` |
| `AVKIT_API_TOKEN` | Contents of `{app_data}/mcp-token.txt` |
| `AVKIT_APP_DATA` | Optional override of `{app_data}` for descriptor + token paths |

The GUI nonce **must not** be copied into `mcp.json`. Settings **Copy MCP config** (default) writes only:

```json
{ "AVKIT_API_TOKEN": "<from mcp-token.txt>", "AVKIT_APP_DATA": "<app_data>" }
```

It **omits** `AVKIT_API_BASE` so the MCP client keeps reading `{app_data}/backend.json` after `--port 0` restarts. An **advanced** “Pin current endpoint” control may add `AVKIT_API_BASE`; if that pin’s host/port does not match the live descriptor, the client returns a structured stale-pin error instead of calling the dead port.

MCP Guard / lock stays **deferred** ([06-gui.md](06-gui.md)).

<a id="mcp-setup-prompt-residual"></a>

### MCP setup prompt (residual)

> **MEU-71.** Registered 2026-10-09 from `MCP-SETUP-PROMPT` (Mat's Session 30 FLATTEN_LOOK F8). **Copy MCP config** copies only `{AVKIT_API_TOKEN, AVKIT_APP_DATA}`: no server command or path, no client-specific placement, nothing the user can read. A Claude Code local-scope registration keyed to `P:/av-kit` never loaded in a session opened as `p:/av-kit`.

| Rule | Contract | Source |
|------|----------|--------|
| Viewable prompt | The Settings MCP card shows a setup prompt the user can read and copy, written so any agent can apply it on another IDE or TUI | Human-approved 2026-10-03, triage D-46 |
| Scope | User scope by default, so the entry is not keyed to a project path (Claude Code: `claude mcp add --scope user`; other clients: their global config). A project-scope block is offered as "this repo only", at each client's project destination (Claude Code `.mcp.json`, Cursor `.cursor/mcp.json`, Codex `.codex/config.toml`, VS Code `.vscode/mcp.json`). Local scope is never emitted | Human-approved 2026-10-16, triage D-48 (supersedes D-47's project scope) |
| Command | `command` is the app's own executable (`process.execPath`), `env` sets `ELECTRON_RUN_AS_NODE=1`, and the absolute server path goes in `args`, in dev and packaged modes. No `npx`, no bare `node`. MEU-71 fixes the `mcp-server/src/index.ts` entry guard so the packaged path starts. Bundling the server's dependencies is MEU-92 ([§MCP server bundle](#mcp-server-bundle-residual), grouping D-56; `MCP-PACKAGED-ENTRY-UNREACHABLE`). A test pins Electron's RunAsNode fuse on | Human-approved 2026-10-16, triage D-50 |
| Clients | One block per client, shown by a selector: Claude Code, Codex (`~/.codex/config.toml` `[mcp_servers.avkit]`), Cursor (`mcpServers`), VS Code (`servers` with `type: "stdio"`), Claude Desktop (with the MSIX-virtualized config path note), Windsurf (labelled community), then a generic block | Triage D-51 |
| Token boundary | No block contains the token or a `${AVKIT_API_TOKEN}` expansion: the server reads `{app_data}/mcp-token.txt` itself. Every block emits the app's resolved `AVKIT_APP_DATA`, because the app and server defaults diverge when a client launches the server without `LOCALAPPDATA`. **Copy MCP config** and **Pin endpoint & copy** stay as above (the audit runner uses them) | Triage D-49 (supersedes D-47's `${VAR}` clause), amended by D-57; Local Canon 06 `copyMcpConfig` |
| Prompt steps | Back up the target file to `<file>.avkit-backup-<UTC>` and merge, never overwrite; a conditional restart line ("If the tools do not appear, quit and reopen <client>, then reply Ready"); verify with `avkit_health` `action: "dependencies"`, which needs the token and must return successfully (`liveness` alone never counts); end with exactly one `RESULT: connected` or `RESULT: failed (<step>, <error>)` line, `<error>` being the server's error code (for example `token_missing`, `app_not_running`) | Triage D-52 amended by D-58, D-53 |
| UI | The Settings MCP card holds the client selector, a read-only prompt viewer and **Copy prompt**; `copy-mcp-btn` and `pin-mcp-btn` move under an Advanced disclosure with testids and gui-actions-index rows unchanged | Triage D-54 |
| Docs | This section, `05-mcp-server.md` and the server instructions name the same placement; there is no MCP README, so `docs/distribution/mcp.json.example` carries the client example. gui-actions-index gains the Copy prompt row together with its Red test (Session 31b row 2), because the index audit fails on a row whose channel is not yet registered | Local Canon; Session 31b plan D-77, D-78 |
| Tests | Golden output per client block; a regex test that no block contains a fixture token; every block carries `AVKIT_APP_DATA`; a negative case where liveness succeeds but dependencies fails with `token_missing` yields `RESULT: failed`; main-process test that the token never reaches the renderer; existing copy/pin assertions unchanged; Electron case for select, view and copy | Local Canon; zorivest AC-747.1/.7/.10 |

<a id="mcp-server-bundle-residual"></a>

### MCP server bundle (residual)

> **MEU-92.** Registered 2026-10-17 under grouping D-56 (Mat accepted 2026-10-16) for `MCP-PACKAGED-ENTRY-UNREACHABLE`. The packaged app ships the server's `dist/` without its `node_modules`, so `av-kit.exe` with `ELECTRON_RUN_AS_NODE=1` fails on the packaged entry with `ERR_MODULE_NOT_FOUND` (Session 32), and the MCP setup prompt above would point a shipped machine at a server that cannot start.

| Rule | Contract | Source |
|------|----------|--------|
| Bundle | `npm --prefix mcp-server run bundle` writes `mcp-server/bundle/index.mjs` (`esbuild` pinned exactly, ESM, every dependency inlined) and `LICENSES.txt` (one section per bundled package, sorted by name; a package with no licence file fails the build). `mcp-server/bundle/` is gitignored | Grouping D-56; Session 31b plan D-83, D-85 |
| Packaging | `electron-builder.yml` `extraResources` copies `../mcp-server/bundle` to `resources/mcp-server`, which holds only `index.mjs` and `LICENSES.txt`; `dist:prep` ends by building the bundle. The packaged server path the setup prompt emits is `resources/mcp-server/index.mjs` | Session 31b plan D-83 |
| Pass condition | `MCP_ENTRY_PROBE` on a freshly built `win-unpacked` tree: `av-kit.exe` with `ELECTRON_RUN_AS_NODE=1` starts the in-place entry and a hermetic copy, and each answers `initialize` as `av-kit`. A record of an earlier probe is not a pass | p7 RULE-1; Session 31b plan D-84 |
| Tests | A temp-directory copy of the bundle with no `node_modules` above it answers `initialize`; `collectLicenses` fixture cases, including the missing-licence error; pins on `electron-builder.yml`, `dist:prep`, `.gitignore` and the `esbuild` version | Session 31b plan AC-92.1–92.3 |

<a id="release-candidate-packaging-residual"></a>

### Release candidate packaging (residual)

> **MEU-110.** Registered 2026-11-03 from Mat's request to prepare the first release candidate. The only installer on disk is a local build from 2026-09-01 that predates the licence file and must not be uploaded. Tag, release, upload and the FFmpeg licence ruling (D-101) stay with Mat; nothing in this section publishes.

| Rule | Contract | Source |
|------|----------|--------|
| Licence | `LICENSE` is MIT and is installed as `resources/LICENSE`. Every package manifest declares MIT. The README links it and says bundled components keep their own licences. | Mat 2026-11-03 |
| Licence list | `LICENCE_LIST`: the installer carries a generated `resources/THIRD_PARTY_LICENSES.txt` listing every third-party component actually in the build, with the full text of every licence or notice its distribution carries, including notices outside dist-info and outside the build's TOC. `tools/generate_third_party_licenses.py` reads what shipped, not what the environment holds. | `NOTICES-SPACY-TRANSITIVE` |
| Fails closed | Generation exits non-zero for a component with no notice, a notice its `RECORD` lists but disk lacks, a GPL-class licence not on the explicit allow list, payload outside the named classes (first party, CPython, CPython native library with a reviewed text, Windows runtime, source-less namespace package), or a stale build whose TOCs disagree with `_internal` or the exe's module archive. | This section |
| Version | `VERSION_ONE`: one release version on every shipped surface. `0.1.0-rc.1` for npm and electron-builder, `0.1.0rc1` for Python and OpenAPI, tag `v0.1.0-rc.1`. A test fails when they drift. | This section |
| Installer | `av-kit-Setup-<version>.exe`, no spaces, so GitHub keeps the name. The FFmpeg entry filters `*.zip`. The installer stays under the 500 MB budget. | `INSTALLER-SHIPS-FFMPEG-ZIP`; GitHub REST docs (asset renaming) |
| Fresh build | The installer comes from today's tree, after clearing `ui/dist`, `packaging/build` and `packaging/dist`, with a fresh backend, picker, MCP bundle and FFmpeg with its licence. | This section |
| Build record | `BUILD_RECORD`: the build writes the identity of its inputs, the installer's name, size and SHA-256, and its toolchain. `build-identity.py --verify-record` fails when the tree or the installer no longer matches. | This section |
| Packaged checks | Packaged layout, including the absence of `torch`, `kokoro`, `phonemizer` and `espeakng_loader`. The frozen backend reports the version and completes a first conversion into a folder that doesn't exist. The MCP entry starts through `av-kit.exe`. TTS runs offline from cached models. A silent install launches, reaches the backend and renders a page, and uninstall leaves no key, value, shortcut or install folder while `%LOCALAPPDATA%/av-kit` keeps the same top-level entries. | MEU-72 `PACKAGE_SMOKE`; AC-92.4; [§Login item uninstall](#login-item-uninstall-meu-61) |
| Release materials | Release notes say what the RC is, what it doesn't fix and how to report problems. A publish checklist gives the outward steps in order with exact commands. D-101 is presented as a Decision Brief. | Mat 2026-11-03 |

> **Delivered (Session 44).**
> - `LICENSE` and the MIT metadata in every manifest. One RC version on every surface: `0.1.0-rc.1` for npm and electron-builder, `0.1.0rc1` for Python.
> - `tools/generate_third_party_licenses.py` builds `THIRD_PARTY_LICENSES.txt` from what the build shipped and fails closed. `packaging/licence-overrides/` holds the upstream texts it can't read from the build.
> - `build-rc.ps1` built the real installer, recorded in `docs/releases/v0.1.0-rc.1-build-record.json`. `tools/smoke_packaged_rc.py`, `packaged-probes.ps1` and `install-roundtrip.ps1` checked the packaged tree and a real install and uninstall on the build PC. That doesn't replace the clean-machine test.
> - `docs/releases/v0.1.0-rc.1.md` and `publish-checklist-v0.1.0-rc.1.md`. Nothing was tagged or uploaded.
> - Mat ruled D-101 on 2026-11-04: the GPL build stays, re-pinned to BtbN `autobuild-2026-10-31-12-59`. `tools/assemble_ffmpeg_source.py` builds its complete corresponding source archive, and the publish checklist refuses to publish without that archive attached.
> - AC-110.1 to AC-110.22.
> - Gate: the shared `session-gate.ps1` record in the MEU-110 handoff.
> - Plan `docs/execution/plans/2026-11-03-release-rc1/`.

<a id="fetch-exit-codes-residual"></a>

### Fetch script exit codes (residual)

> **MEU-113.** Registered 2026-11-04 from `FETCH-FFMPEG-EXIT-CODES`. It was first registered to build FFmpeg without libdvdcss; the same day Mat kept FFmpeg as it is, including libdvdcss, as an accepted risk (triage D-266). The approved build plan is parked, never run, at `docs/execution/plans/2026-11-04-rc2-ffmpeg-uninstall/`.

| Rule | Contract | Source |
|------|----------|--------|
| Exit codes | `fetch_ffmpeg_windows.ps1` returns its documented codes 2 to 5 through the stderr pattern exit 6 already uses. | Local Canon: known issue `FETCH-FFMPEG-EXIT-CODES` |
| Tests | The tests assert the exact codes, not just a nonzero exit. | Local Canon: known issue `FETCH-FFMPEG-EXIT-CODES` |

> **Delivered (Session 49).**
> - `tools/fetch_ffmpeg_windows.ps1` writes each refusal to stderr and returns its documented code: 2 for a blank URL, a malformed SHA or a missing archive, 3 for a SHA mismatch, 4 for a missing `ffmpeg.exe` or `ffprobe.exe` and 5 for a stub. No `Write-Error` remains.
> - `tests/unit/test_packaging_installer.py` asserts the exact codes. The two earlier tests now assert 2 and 3.
> - AC-113.1 to AC-113.5.
> - Gate: the shared `session-gate.ps1` record in the MEU-113 handoff.
> - Plan `docs/execution/plans/2026-11-04-rc2-fetch-uninstall/`.

<a id="uninstall-installer-copy-residual"></a>

### Uninstall removes the installer copy (residual)

> **MEU-114.** Registered 2026-11-04 from `UNINSTALL-LEAVES-INSTALLER-COPY`. electron-builder copies the running installer to `%LOCALAPPDATA%\av-kit-ui-updater` on install (`app-builder-lib/templates/nsis/include/installer.nsh:93`), and no template removes it. `customUnInstall` in `ui/build/installer.nsh` deletes only the two Run values. Measured on the published RC1: 340,348,020 B stays after uninstall. `ui/package.json` has no `electron-updater`, so av-kit never reads the copy.

| Rule | Contract | Source |
|------|----------|--------|
| Removed | `customUnInstall` deletes the copy and its folder, skipping `${isUpdated}`. | Local Canon: triage D-228 |
| Upgrade | An upgrade still works, checked on the next build. | Local Canon: triage D-228 |
| Kept | `%APPDATA%\av-kit-ui` stays, per `deleteAppDataOnUninstall: false`, and the notes name it. | Local Canon: triage D-228 |
| Tests | A pin on the macro in `ui/tests/unit/login-item-nsh.test.ts`; `install-roundtrip.ps1` checks the folder is gone after uninstall and `%APPDATA%\av-kit-ui` is still there, and an install over an existing one keeps working. | Local Canon |

> **Delivered (Session 49).**
> - `customUnInstall` in `ui/build/installer.nsh` deletes `$LOCALAPPDATA\${APP_INSTALLER_STORE_FILE}` and removes `av-kit-ui-updater` with a non-recursive `RMDir`, skipping `${isUpdated}`. A per-machine install switches to the current user's folders for the two lines and back. `%APPDATA%\av-kit-ui` stays.
> - `ui/tests/unit/login-item-nsh.test.ts` pins the macro and the folder name.
> - `repackage.ps1` rebuilt the installer from the existing `win-unpacked` with only the macro changed, and `install-roundtrip.ps1` ran it on the build PC. RC1's uninstall leaves the copy, the negative control. The new uninstall removes the copy and its folder. RC1 to new and new over itself both launch, and the uninstall after each is clean. MEU-125 repeats the round trip on the full rc.2 build (plan D-268).
> - AC-114.1 to AC-114.9.
> - Gate: the shared `session-gate.ps1` record in the MEU-114 handoff.
> - Plan `docs/execution/plans/2026-11-04-rc2-fetch-uninstall/`.

<a id="second-release-candidate-residual"></a>

### Second release candidate (residual)

> **MEU-125.** Registered 2026-11-04. The triage batching Mat accepted that day makes batches A to C its minimum, and batch A is now the two fixes in MEU-113 and MEU-114. Tag, release, upload and what happens to RC1 stay with Mat; nothing in this section publishes.

| Rule | Contract | Source |
|------|----------|--------|
| Version | `VERSION_ONE` moves to `0.1.0-rc.2` for npm and electron-builder, `0.1.0rc2` for Python and OpenAPI, tag `v0.1.0-rc.2`. | Human-approved: triage batching, Mat 2026-11-04; [§Release candidate packaging](#release-candidate-packaging-residual) |
| Contents | MEU-113 to MEU-121 are the minimum. MEU-122 to MEU-124 and MEU-126 go in if they're done by then. | Human-approved: triage batching, Mat 2026-11-04; Local Canon: grouping D-249 for MEU-126 |
| FFmpeg | The pin stays the stock BtbN GPL build and libdvdcss ships, an accepted risk. | Human-approved: triage D-266 |
| Build and gate | The rules of [§Release candidate packaging](#release-candidate-packaging-residual) apply again from a clean tree: `LICENCE_LIST`, Fresh build, `BUILD_RECORD` and Packaged checks, plus the checks MEU-114, MEU-117 and MEU-121 add, including MEU-114's round trip on the full build, and a fresh gate. | Human-approved: triage batching, Mat 2026-11-04; Local Canon: Session 49 plan D-268 for the round trip |
| Notes | New release notes say what this candidate fixes and what stays open, and carry D-216's corrections. The 'your network' wording waits for the other-network check. | Human-approved: triage D-216 |
| Notices | The FFmpeg section of `packaging/THIRD_PARTY_NOTICES.md` gains one factual line: the build includes libdvdcss, and av-kit never uses DVD input. | Human-approved: triage D-275 |
| Checklist | A new publish checklist gives the outward steps in order with exact commands, attaches the FFmpeg source archive for the unchanged pin, checks `~/.avkit/models` for voice models and includes what happens to RC1 once this candidate replaces it. | Human-approved: triage D-266, D-101; RC1 plan D-238; known issue `MODELS-DIR-DOCS-AND-PROBE-MISMATCH` |
| Publishing | Nothing here tags, uploads or changes a release. | Local Canon: PROFILE E5 |

---

## Platforms

| Platform | Phase 7 gate |
|----------|----------------|
| Windows 10/11 x64 | **Yes** — NSIS, bundled FFmpeg, clean-machine smoke |
| macOS | Secondary — same layout, `pwsh`/Seatbelt notes in [macos-setup](../../.agent/docs/macos-setup.md) when packaging there |
| Linux | Secondary |

Do not claim cross-platform ship until the Windows gate is green.

---

## Security / privacy (install-time)

- Bind localhost only.
- Do not log `--token` / `--mcp-token`.
- Uninstall: NSIS may remove `{install}`. **Do not** auto-delete `{app_data}` (queue + archive + MCP token) unless the user checks a “remove data” box. **Do** delete the MEU-61 login-item Run value (`com.avkit.app`) and the matching `StartupApproved\Run` value so Task Manager → Startup does not keep a dead entry.
- Cookies: never packaged; user settings hold **paths** only.

---

## What this layer must not do

| Forbidden | Why |
|-----------|-----|
| Bundle Kokoro weights or CUDA | Size + license + GPU variance |
| Bundle a developer `avkit.db` | Would leak queue/history |
| `onefile` PyInstaller as the default | Startup budget |
| Bind `0.0.0.0` | Phase 4 |
| Use the GUI nonce as the MCP token | Phase 5 |
| Treat `progress.json` or yt-dlp archive files as SoT | Phase 1–2 |
| Require auto-update or signing to call the phase done | Optional |
| Invent a ConversionJob / ModelFetchJob for the installer | Phase 1 / 8. Convert jobs are runtime SQLite, not installer artifacts |
| Invent CaptureShot rows at install time | Phase 9. Inbox files are user data, not packaged |
| Invent a Windows service / WinSW / `sc config` auto-start for the backend | Phase 6 forbids service-install. Login item is the per-user Run key (MEU-61) |

---

## Testing (Phase 7)

| Case | Assert |
|------|--------|
| Clean Windows VM, no FFmpeg on PATH | `GET /health/dependencies` → ffmpeg available (bundled) |
| Clean VM, no HF cache | App starts; TTS Generate disabled until download; download INT8 works |
| Installer size | Payload without models under 500MB (measure the NSIS, not `%LOCALAPPDATA%`) |
| Upgrade install | Existing `{app_data}/avkit.db` queue still listed |
| Quit | Backend process gone; no orphan `ffmpeg` |
| MCP | With app running + `mcp-token.txt`, `avkit_health.dependencies` succeeds; with app quit, structured error |
| Splash | `window_show_ms` &lt; 800ms; `data_ready_ms` &lt; 3000ms on a warm disk (log, do not fail CI on a slow VM without a `[B]` follow-up) |

No live YouTube required for the install smoke. One optional live download on a dedicated job.

---

## Exit checklist

- [ ] PyInstaller `onedir` spec; hidden-import smoke on a clean venv
- [ ] electron-builder NSIS + `extraResources` (backend, ffmpeg, mcp-server, region-picker)
- [ ] `dotnet publish` of `native/region-picker` runs before packaging; the installed tree carries `resources/region-picker/avkit-region-picker.exe` and it runs without a machine-wide .NET runtime
- [ ] FFmpeg bundled; probe order implemented
- [ ] Spawn flags: `--token`, `--mcp-token`, `--port 0`, `--app-data`
- [ ] `{app_data}/mcp-token.txt` + `backend-port.txt` created on first run
- [ ] Model Manager on a machine with empty HF cache
- [ ] PyTorch variant does not pull torch into the installer
- [ ] Uninstall leaves `{app_data}` unless the user opts in
- [ ] Uninstall removes `HKCU\...\Run\com.avkit.app` and the matching `StartupApproved\Run` value (MEU-61)
- [ ] Windows 10/11 x64 clean-machine install + launch + Settings → Check Dependencies
- [ ] IDE `mcp.json` snippet in repo docs (not a second API)

---

## Validation commands

There is no single unit test for an installer. Use the registered receipts in [`.agent/docs/commands.md`](../../.agent/docs/commands.md) for the packaged backend/UI, then the checklist above on a clean machine.

```bash
# After packaging locally — exact receipts TBD in commands.md when the spec file exists
# Measure installer size; launch; curl GET http://127.0.0.1:<port>/api/v1/health
```
