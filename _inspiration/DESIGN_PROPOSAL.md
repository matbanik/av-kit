# av-kit — Design Proposal

> **What is this document?** Architecture blueprint for the unified YouTube media toolkit. Defines how the hybrid TypeScript + Python stack is structured, how layers connect, and key design decisions. Follows the same framework as Zorivest.

---

## 1. Architecture Overview

av-kit adopts the **identical architecture** as Zorivest:

```
┌─────────────────────────────────────────────────────┐
│                    Desktop App                       │
│  ┌──────────────────────────────────────────────┐   │
│  │          Electron (Main Process)              │   │
│  │  • PythonManager (spawn/health/shutdown)     │   │
│  │  • IPC Bridge (preload → contextBridge)      │   │
│  │  • Window State, App Menu, Feature Flags     │   │
│  └──────────────┬───────────────────────────────┘   │
│                 │ IPC                                │
│  ┌──────────────▼───────────────────────────────┐   │
│  │          React 19 (Renderer Process)          │   │
│  │  • TanStack Router (hash history)            │   │
│  │  • TanStack Query (API cache)                │   │
│  │  • Zustand (global state)                    │   │
│  │  • Features: Downloader / Transcript / TTS   │   │
│  │  • Tailwind CSS v4 + shadcn/ui               │   │
│  └──────────────┬───────────────────────────────┘   │
│                 │ HTTP (Bearer token)                │
│  ┌──────────────▼───────────────────────────────┐   │
│  │          FastAPI (Python Backend)             │   │
│  │  • REST Routes per module                    │   │
│  │  • Pydantic v2 schemas                       │   │
│  │  • structlog + correlation IDs               │   │
│  │  • Async lifespan with service wiring        │   │
│  └──────────────┬───────────────────────────────┘   │
│                 │ Service Layer                      │
│  ┌──────────────▼───────────────────────────────┐   │
│  │          Domain + Infrastructure               │   │
│  │  • Hexagonal: Ports ← Domain → Adapters      │   │
│  │  • SQLAlchemy UoW (SQLite)                   │   │
│  │  • yt-dlp adapter, Kokoro adapter, FFmpeg    │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│               MCP Server (TypeScript)                │
│  • StdioServerTransport for IDE integration         │
│  • Toolset registry with mode filtering             │
│  • Thin wrappers calling REST API via fetch()       │
└─────────────────────────────────────────────────────┘
```

---

## 2. Why This Architecture

| Decision | Rationale |
|----------|-----------|
| **Electron + React** | Proven pattern from Zorivest. Cross-platform desktop with modern web UI. React 19 + TanStack stack provides type-safe routing, server state management, and virtualized tables for download queues. |
| **FastAPI Python backend** | All three source apps are Python. yt-dlp, Kokoro, youtube-transcript-api are Python libraries. FastAPI provides async support for concurrent downloads and TTS generation. |
| **Hexagonal architecture** | Clean separation: domain logic (download states, TTS pipeline) independent from infrastructure (yt-dlp, SQLite, FFmpeg). Makes testing trivial — mock the ports. |
| **SQLite (not JSON files)** | All 3 source apps use JSON for settings. SQLite provides atomic writes, concurrent access from API + MCP, and schema evolution via inline migrations. |
| **TypeScript MCP server** | Same SDK and pattern as Zorivest. IDE integration via stdio. Tools wrap REST API calls. |
| **uv workspaces** | Monorepo package management: `packages/core`, `packages/infrastructure`, `packages/api`. Clean dependency boundaries. |

---

## 3. Package Layout

### Python Packages (uv workspaces)

```
packages/
├── core/src/avkit_core/
│   ├── domain/          # Entities, enums, value objects
│   │   ├── download.py  # DownloadJob, DownloadStatus, QualityPreset
│   │   ├── transcript.py # TranscriptJob, ChannelResolution
│   │   ├── tts.py       # TTSJob, ModelVariant, VoiceConfig
│   │   └── enums.py     # Shared enums (JobStatus, MediaFormat)
│   ├── ports/           # Protocol interfaces
│   │   ├── youtube.py   # YouTubePort (download, extract IDs)
│   │   ├── tts.py       # TTSPort (generate, list voices)
│   │   ├── media.py     # MediaPort (convert, probe)
│   │   └── storage.py   # StoragePort (UoW protocol)
│   ├── application/     # Use cases, DTOs
│   └── services/        # Service layer orchestration
│
├── infrastructure/src/avkit_infra/
│   ├── database/        # SQLAlchemy models, repos, UoW
│   ├── youtube/         # yt-dlp adapter (implements YouTubePort)
│   ├── tts/             # Kokoro pipeline adapter (implements TTSPort)
│   ├── transcript/      # youtube-transcript-api adapter
│   ├── media/           # FFmpeg adapter (implements MediaPort)
│   └── model_manager/   # HuggingFace Hub download + cache management
│
└── api/src/avkit_api/
    ├── main.py          # App factory, lifespan, middleware
    ├── dependencies.py  # DI providers (get_download_service, etc.)
    ├── routes/          # One file per module
    │   ├── downloads.py
    │   ├── transcripts.py
    │   ├── tts.py
    │   ├── models.py    # Model management (download/load/unload)
    │   ├── settings.py
    │   └── health.py
    └── schemas/         # Pydantic v2 request/response models
```

### TypeScript Packages (npm workspaces)

```
ui/                      # Electron + React desktop app
├── src/main/            # Electron main process + PythonManager
├── src/preload/         # Context bridge
└── src/renderer/src/
    ├── features/
    │   ├── downloader/  # Download queue, quality selector, progress
    │   ├── transcript/  # Channel input, batch progress, compiled output
    │   ├── tts/         # Text input, model manager, voice selector
    │   └── settings/    # Unified settings panel
    ├── components/      # Shared UI components (AppShell, DataTable, etc.)
    └── stores/          # Zustand stores for cross-feature state

mcp-server/              # TypeScript MCP server
└── src/
    ├── tools/           # Tool implementations calling REST API
    └── toolsets/        # Registry, seed, mode filtering
```

---

## 4. Communication Patterns

### Electron ↔ FastAPI
- Electron main spawns Python subprocess (`PythonManager`)
- Ephemeral Bearer token generated per session
- Health check with exponential backoff (100ms → 5s cap)
- All API calls from React renderer go through `window.api.getBackendUrl()`

### Long-Running Operations
- Downloads, transcript batches, and TTS generation are long-running
- **Pattern**: Start job → return job ID → poll for progress via SSE or polling endpoint
- Job state machine: `Pending → Running → Done | Failed | Cancelled`
- Cancellation via `DELETE /api/v1/downloads/{id}` or similar

### MCP ↔ FastAPI
- MCP server is a separate process connecting via stdio to IDE
- MCP tools call REST API via HTTP fetch (same as GUI)
- Uses pre-provisioned API key for auth

---

## 5. Data Persistence

### SQLite Database (single file)
- **Settings table**: Key-value with module namespace (downloader.quality, tts.voice, etc.)
- **Download jobs table**: URL, status, quality, progress, file path, timestamps
- **Transcript jobs table**: Channel URL, video IDs, status, progress
- **TTS jobs table**: Input text hash, voice, speed, output path, status
- **Archive table**: Previously downloaded video IDs for dedup
- **Model registry table**: Model name, variant, path, size, loaded status

### Inline Migrations (no Alembic)
Following Zorivest pattern: append-only list of `ALTER TABLE` statements in `main.py`, run at startup with try/except for idempotency.

---

## 6. Testing Strategy

| Layer | Framework | Scope |
|-------|-----------|-------|
| **Domain** | pytest | Pure unit tests, no IO |
| **Infrastructure** | pytest + tmp_path SQLite | Adapter tests with real DB |
| **API** | pytest + TestClient | Route tests with mocked services |
| **MCP** | vitest | Tool registration and mocked fetch |
| **GUI** | vitest + testing-library/react | Component tests |
| **E2E** | Playwright | Full app flow tests |

### TDD Cycle
Same as Zorivest: Red → Green → Quality (pyright + ruff) → Full Suite → Handoff

---

## 7. Distribution

| Component | Packaging |
|-----------|-----------|
| **Python backend** | PyInstaller single executable |
| **Electron app** | electron-builder (Windows NSIS installer) |
| **Kokoro model** | NOT bundled — downloaded on first use via Model Manager |
| **FFmpeg** | Bundled binary OR detected from system PATH |
| **yt-dlp** | Bundled as Python dependency (pip install) |
