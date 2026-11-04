# av-kit Architecture

> **Target-state architecture** for the unified YouTube media toolkit.

## Monorepo Layout

```
p:\av-kit\
├── pyproject.toml              # Root uv workspace config
├── uv.lock
├── package.json                # Root npm workspace config
├── AGENTS.md                   # AI agent instructions
├── GUARDRAILS.md               # Safety protocols
│
│   ═══ PYTHON PACKAGES (uv workspaces) ═══
├── packages/
│   ├── core/                   # Domain + application layer
│   │   └── src/avkit_core/
│   │       ├── domain/         # Entities, value objects, enums
│   │       ├── application/    # Use cases, DTOs
│   │       ├── ports/          # Protocol interfaces
│   │       └── services/       # Service layer
│   ├── infrastructure/         # Adapters
│   │   └── src/avkit_infra/
│   │       ├── database/       # SQLAlchemy repos, UoW, models
│   │       ├── youtube/        # yt-dlp adapter
│   │       ├── tts/            # Kokoro pipeline adapter
│   │       ├── transcript/     # youtube-transcript-api adapter
│   │       ├── media/          # FFmpeg adapter
│   │       └── model_manager/  # HuggingFace Hub download + cache
│   └── api/                    # FastAPI REST layer
│       └── src/avkit_api/
│
│   ═══ TYPESCRIPT PACKAGES (npm workspaces) ═══
├── ui/                         # Electron + React desktop app
├── mcp-server/                 # TypeScript MCP server
└── tests/                      # Python tests
```

## Dependency Rule

```
Domain (entities, ports) ← Application (services, DTOs) ← Infrastructure (adapters, repos)
                                    ↑
                              API (routes, schemas)
```

**Never import infrastructure from domain.** Domain defines ports (protocols); infrastructure implements them.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| GUI | Electron v41 + electron-vite + React 19 |
| Styling | Tailwind CSS v4 + shadcn/ui |
| State | Zustand v5 + TanStack Query v5 |
| Router | TanStack Router (hash history) |
| Backend | FastAPI 0.115+ + Pydantic v2 |
| Database | SQLite via SQLAlchemy |
| Python mgmt | uv workspaces |
| TS mgmt | npm workspaces |
| MCP | @modelcontextprotocol/sdk (StdioServerTransport) |
| Testing | pytest + vitest + Playwright |
| Quality | pyright + ruff + tsc + eslint |
