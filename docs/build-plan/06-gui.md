# Phase 6: GUI (Electron + React)

> Part of [av-kit Build Plan](../BUILD_PLAN.md) | Prerequisites: [Phase 4](04-rest-api.md) | Outputs: [Phase 7](07-distribution.md)

> **Page layout supersession:** [Phase 11 page layout canon](11-page-layout.md) governs later page composition and geometry; this Phase 6 document continues to govern the existing GUI actions, IPC, save behavior, and enablement.

---

## Goal

Build the desktop GUI as the outermost layer. The Electron shell spawns the Python backend as a child process and the React UI communicates with it via REST on localhost. Use TanStack Table for queue data grids, shadcn/ui for form components, and the same dark-mode Dracula-inspired design system as Zorivest.

> **Source files**: Behavioral contracts from [`_downloader_pseudo_logic.md`](../../_inspiration/_downloader_pseudo_logic.md), [`_transcript_pseudo_logic.md`](../../_inspiration/_transcript_pseudo_logic.md), [`_text_cleanup_pseudo_logic.md`](../../_inspiration/_text_cleanup_pseudo_logic.md), [`_kokoro_production_settings.md`](../../_inspiration/_kokoro_production_settings.md), [`_shared_patterns.md`](../../_inspiration/_shared_patterns.md), [`DESIGN_PROPOSAL.md`](../../_inspiration/DESIGN_PROPOSAL.md), [`APPLICATION_PURPOSE.md`](../../_inspiration/APPLICATION_PURPOSE.md).

---

## Loading & Startup (Performance-Tracked)

> **Design target**: < 3 seconds to usable UI with splash during backend startup ([APPLICATION_PURPOSE.md §6](../../_inspiration/APPLICATION_PURPOSE.md)).

### Startup Sequence

The splash window provides visual feedback while Python starts. The main window is loaded **in parallel** with the Python health check (not blocked on it) — skeleton screens indicate backend progress after the shell paints.

```
 Electron Main Process                  Renderer (React)
 ─────────────────────                  ─────────────────
 1. Show splash.html (lightweight)
    BrowserWindow with themed background
    └─ Display "Starting av-kit..."

 2. PythonManager (no attach — Phase 7 table)
    requestSingleInstanceLock(); loser focuses peer and exits
    If owned-orphan (Phase 7 live-identity proof): SIGTERM, then spawn new nonce
    Else spawn: --token NONCE --mcp-token … --port 0 --app-data
    Wait until backend.json pid == child (or AVKIT_READY)
    └─ Log: startup.python_spawn_ms

 3. Immediately (parallel with step 2):
    Create main BrowserWindow (security table below)
    show: false
    Load index.html ──────────────────▶ 4. React mounts AppShell
    └─ Log: startup.renderer_load_ms       └─ Nav rail renders (sync)
                                            └─ Downloader skeleton + "Connecting..."
                                            └─ Log: startup.shell_paint_ms

 5. win.once('ready-to-show')
    └─ win.show() ─────────────────────▶ 6. User sees app structure
    └─ Hide splash window                  (skeletons + "Connecting to backend...")
    └─ Log: startup.window_show_ms         Target: < 800ms from launch

                                        7. getBackendUrl() resolves (async invoke)
                                           after descriptor is ready → Query activates
                                           └─ Log: startup.data_ready_ms (< 3s)

                                        8. Lazy modules pre-cached on idle
```

**Runtime descriptor** (`{app_data}/backend.json`) is the only shared discovery object for Electron and MCP. Shape and refuse rules: [07-distribution.md](07-distribution.md). `getBackendUrl()` / `getToken()` are **async IPC invokes**, never `sendSync` of a pre-listen URL (port 0 is not a URL).

### Performance Logging

All startup timestamps are emitted to the Python backend via `POST /api/v1/health/startup-metrics` (health router — no separate logs endpoint needed). Each metric is logged as a structured event. All requests include `Authorization: Bearer {token}` via the shared `apiFetch()` wrapper.

| Metric Key | Description | Target |
|---|---|---|
| `startup.python_spawn_ms` | Time from Electron launch to Python process healthy | < 2000ms |
| `startup.renderer_load_ms` | Time from `BrowserWindow.loadURL()` to React mount | < 300ms |
| `startup.shell_paint_ms` | Time from React mount to app shell first paint | < 200ms |
| `startup.window_show_ms` | Time from launch to `win.show()` (user sees skeleton UI) | < 800ms |
| `startup.data_ready_ms` | Time from launch to live data displayed | < 3000ms |
| `startup.lazy_preload_ms` | Time from launch to all lazy modules pre-cached | < 5000ms |

> **Timing model**: `window_show_ms` (< 800ms) measures shell paint with skeletons. This occurs *before* Python is healthy. `data_ready_ms` (< 3000ms) is the full end-to-end metric including Python startup. The splash window covers the gap between launch and shell paint.

### Electron security / IPC boundary

`BrowserWindow` webPreferences (Zorivest `main/index.ts`): `nodeIntegration: false`, `contextIsolation: true`, `sandbox: true`, `webSecurity: true`. Deny `window.open` / unexpected navigation. Allowlist IPC channels only.

```typescript
// ui/src/main/preload.ts — allowlisted bridge (adapt Zorivest preload)

import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('api', {
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'), // waits for backend.json
  getToken: () => ipcRenderer.invoke('get-token'),
  logStartupMetric: (key: string, value: number) =>
    ipcRenderer.send('startup-metric', { key, value, timestamp: Date.now() }),
  showDirectoryDialog: () => ipcRenderer.invoke('show-directory-dialog'),
  showFileDialog: (filters?: Electron.FileFilter[]) =>
    ipcRenderer.invoke('show-file-dialog', filters),
  openPath: (target: string) => ipcRenderer.invoke('open-path', target),
  showItemInFolder: (target: string) => ipcRenderer.invoke('show-item-in-folder', target),
  readClipboardText: () => ipcRenderer.invoke('read-clipboard-text'),
  writeClipboardText: (text: string) => ipcRenderer.invoke('write-clipboard-text', text),
  writeClipboardImage: (png: Uint8Array) => ipcRenderer.invoke('write-clipboard-image', { png }), // PNG bytes only; main decodes and writes
  readTextFile: (opts: { maxBytes: number }) =>
    ipcRenderer.invoke('read-text-file', opts), // always opens a dialog; no raw path from renderer
  copyMcpConfig: (opts?: { pinEndpoint?: boolean }) =>
    ipcRenderer.invoke('copy-mcp-config', opts), // returns { ok: true } only — never the token
  getMcpSetupPrompt: (opts: { client: string; scope: 'user' | 'project' }) =>
    ipcRenderer.invoke('get-mcp-setup-prompt', opts), // returns { text }; the prompt never holds the token
  subscribeLogs: (cb: (batch: ConsoleEvent[]) => void) => { /* on + unsubscribe */ },
  getLogSnapshot: () => ipcRenderer.invoke('get-log-snapshot'),
});
```

**Path rules (locked):**

- `readTextFile` **always** opens a file dialog in main. Allowed extensions: `.txt`, `.md`. `maxBytes` default 2 MiB. The renderer cannot pass an arbitrary path.
- Denied even if the user picks them: `{app_data}/mcp-token.txt`, `{app_data}/backend.json`, `{app_data}/avkit.db`, any path matching `*token*`.
- `openPath` / `showItemInFolder` reject URLs and those secret files. Allowed: download/transcript/tts **output** paths returned by the API, plus dialog-chosen files.
- `{app_data}` is **not** a generic readable root.
- `copyMcpConfig`: main reads `mcp-token.txt` and writes the clipboard JSON from [07-distribution.md](07-distribution.md). The renderer never receives the token.
- `getMcpSetupPrompt`: main builds the per-client setup prompt from [07 §MCP setup prompt (residual)](07-distribution.md#mcp-setup-prompt-residual) (the app executable with `ELECTRON_RUN_AS_NODE=1` and the server path); it never reads `mcp-token.txt`.

```typescript
// ui/src/renderer/src/lib/api.ts — response-aware wrapper

export async function apiFetch<T = undefined>(path: string, init?: RequestInit): Promise<T> {
  const [base, token] = await Promise.all([window.api.getBackendUrl(), window.api.getToken()]);
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: { ...init?.headers, Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
  });
  const raw = await res.text();
  const body = raw.length === 0 ? undefined : JSON.parse(raw);
  if (!res.ok) {
    const env = body?.error;
    throw new ApiError(res.status, env?.code ?? 'HTTP_ERROR', env?.message ?? raw, env?.details ?? null);
  }
  if (res.status === 204 || body === undefined) return undefined as T;
  return body as T;
}
```

Mutation hooks that hit 204 routes (`DELETE` download/transcript/tts, `POST /models/unload`, `POST /health/startup-metrics`) must type `apiFetch<void>`. Contract-test every 204 path plus one `ErrorEnvelope` 422.

### Progressive Loading Strategy

| Time Window | What Renders | Fallback |
|---|---|---|
| 0–800ms | App shell: nav rail + header + Downloader skeleton + "Connecting..." | Themed `backgroundColor` (no white flash) |
| 800ms–3s | Backend comes online; skeleton → data hydrate | "Connecting to backend..." indicator per panel |
| > 3s | Localized "Still loading…" message per panel | Only in the affected panel, never full-screen block |

**Key rules:**
- **No full-screen splash/spinner in the React app** — Python cold start uses a separate Electron `splash.html` window; once the main window appears, only skeleton screens are shown
- **Skeleton screens** over shimmer effects (media app context; shimmer is distracting)
- **Main window created in parallel with Python startup** — not blocked on health check
- **TanStack Router `lazy()`** for all routes except Downloader (Downloader is the default route, in main bundle)
- **Idle pre-caching**: after Downloader renders, use `requestIdleCallback` to pre-import lazy modules

**Technology stack** (identical to Zorivest):
- **Routing**: TanStack Router v1 with `createHashHistory()` (required for Electron)
- **Server state**: TanStack Query v5 (`staleTime: 0` for queue data freshness)
- **Local UI state**: Zustand v5 (slice pattern, `persist` → electron-store)
- **CSS**: Tailwind CSS v4 with `@tailwindcss/vite`
- **Components**: shadcn/ui (compact preset for dense layout) + Radix UI
- **Performance**: React Compiler 1.0 (Babel plugin, automatic memoization)
- **Forms**: React Hook Form v7 + Zod (`useWatch()` not `watch()` for React Compiler compat)

```typescript
// ui/src/renderer/src/router.tsx — TanStack Router with hash history + lazy code splitting

import {
  createRouter,
  createHashHistory,
  createRootRoute,
  createRoute,
  Outlet,
} from '@tanstack/react-router'
import { AppShell } from './components/layout/AppShell'
import { DownloaderPage } from './features/downloader/DownloaderPage'  // in main bundle (startup page)
import { ModuleSkeleton } from './components/ModuleSkeleton'

const hashHistory = createHashHistory()

const rootRoute = createRootRoute({
  component: () => (
    <AppShell>
      <Outlet />
    </AppShell>
  ),
  pendingComponent: ModuleSkeleton,
})

const downloaderRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: DownloaderPage,
})

const transcriptRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/transcript',
}).lazy(() => import('./features/transcript/TranscriptPage'))

const ttsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/tts',
}).lazy(() => import('./features/tts/TTSPage'))

const convertRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/convert',
}).lazy(() => import('./features/converter/ConvertPage'))  // Phase 8

const captureRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/capture',
}).lazy(() => import('./features/capture/CapturePage'))  // Phase 9

const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/settings',
}).lazy(() => import('./features/settings/SettingsPage'))

const routeTree = rootRoute.addChildren([
  downloaderRoute,
  transcriptRoute,
  ttsRoute,
  convertRoute,
  captureRoute,
  settingsRoute,
])

export const router = createRouter({
  routeTree,
  history: hashHistory,
  defaultPreload: 'intent',  // Preload on hover/focus
})
```

---

## Main Window Layout

> **Design basis**: Zorivest desktop app — persistent left navigation rail, dark theme, card-based content sections with muted borders. av-kit follows the identical layout pattern: dark background (`#282a36`), left nav rail with icon + text labels, content area with header bar.

### App Shell Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  av-kit              File  Edit  View  Window  Help                   ─ □ ×             │
├──────┬───────────────────────────────────────────────────────────────────────────────────┤
│      │  CONTENT HEADER                                                                   │
│  NAV │  ┌──────────────────────────────────────┐    Model: ⚪ None    🟢 Connected       │
│ RAIL │  │ av-kit                               │                     ⌘K Search          │
│      │  └──────────────────────────────────────┘                                         │
│ ──── ├───────────────────────────────────────────────────────────────────────────────────┤
│      │                                                                                   │
│  📥  │  CONTENT AREA                                                                    │
│ Down │                                                                                   │
│      │  (Rendered by active route — Downloader is default)                              │
│  📝  │                                                                                   │
│ Trans│                                                                                   │
│      │                                                                                   │
│  🔊  │                                                                                   │
│ TTS  │                                                                                   │
│      │                                                                                   │
│  🎬  │                                                                                   │
│ Conv │                                                                                   │
│      │                                                                                   │
│  📷  │                                                                                   │
│ Capt │                                                                                   │
│      │                                                                                   │
│ ──── │                                                                                   │
│  ⚙️  │  CONTENT AREA                              │ CONSOLE PANEL (right side sheet)   │
│ Sett │  (active route)                            │ [Expand] [Collapse] [X]            │
│      │                                            │ [Clear] [Filter ▼] [Search]        │
│  ▼   │                                            │ [14:32:01] [Downloader] Starting…  │
│ Coll │                                            │ [14:32:03] Format selected: 1080p  │
│      │                                            │ [14:32:15] [yt-dlp] [DEBUG] …      │
├──────┴───────────────────────────────────────────────────────────────────────────────────┤
│  Ready                                                                   v0.1.0-dev     │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### Navigation Rail

| Position | Icon | Label | Route | Shortcut | Notes |
|---|---|---|---|---|---|
| Top (1st) | 📥 | Downloader | `/` | `Ctrl+1` | **Default route** — Download queue and URL input |
| Top (2nd) | 📝 | Transcript | `/transcript` | `Ctrl+2` | Channel transcript batch processing |
| Top (3rd) | 🔊 | TTS | `/tts` | `Ctrl+3` | Text-to-speech with model management |
| Top (4th) | 🎬 | Convert | `/convert` | `Ctrl+4` | Local compress / cut / extract — [08-video-conversion.md](08-video-conversion.md) |
| Top (5th) | 📷 | Capture | `/capture` | `Ctrl+5` | Region inbox + annotate — [09-screenshot-capture.md](09-screenshot-capture.md) |
| Bottom | ⚙️ | Settings | `/settings` | `Ctrl+,` | Settings, appearance (pinned bottom) |
| Bottom | ▼ | Collapse | — | `Ctrl+B` | Toggle rail between expanded/collapsed mode |

**Rail behavior:**
- Always visible (no auto-hide)
- Active item highlighted with accent bar (cyan `#8be9fd`, matching Zorivest)
- Collapsed mode on windows < 960px width (icons only, no labels)
- Rail width persisted via `usePersistedState('ui.rail.collapsed')`

### Content Header

Always present above the content area. Contains:
- **App title** — "av-kit" branding text
- **Model status indicator** — shows currently loaded TTS model ("⚪ None", "🟢 Kokoro FP16", "🔄 Loading...")
- **Connection status** — backend health indicator (🟢 Connected / 🔴 Disconnected)
- **Command palette trigger** — `Ctrl+K` search bar

### Command palette and action registry

Adapt Zorivest `registry/types.ts`, `commandRegistry.ts`, `CommandPalette.tsx`, `AppShell.tsx`.

| Rule | Detail |
|------|--------|
| Wiring | Ctrl+K / header field; every registry chord is bound from the registry (§Shortcut binding) |
| Type | `CommandRegistryEntry`: `id`, `label`, `category` (`navigation`\|`download`\|`transcript`\|`tts`\|`convert`\|`capture`\|`settings`\|`help`\|`appearance`), `keywords[]`, `action()`, optional `shortcut`, `icon`, `page` (the owning page), `stateful` (runs only when its page enables it) and `palette` (`false`: never listed) |
| Inventory | Every button lives in [gui-actions-index.md](gui-actions-index.md). Palette-eligible actions are `Palette = yes` rows; the palette lists them by the context-aware model (§Command palette curation) |
| Search | Fuse (or equivalent) over `label` + `keywords`; arrow keys + Enter; Esc closes |
| Audit | Bidirectional: palette-yes ids registered; every Phase 6 button has an index row; every REST/IPC cell exists ([gui-actions-index.md](gui-actions-index.md)) |

### Help (per page)

Adapt Zorivest `HelpSearchField`, `useHelpSearch`, `*HelpCard.tsx`, `*-help-content.ts`.

| Page | Content module | Topics (minimum) |
|------|----------------|------------------|
| Downloader | `downloader-help-content.ts` | URL types, SABR, cookies, archive, pause vs cancel |
| Transcript | `transcript-help-content.ts` | Resume via items, Stop → Cancelled + requeue, compile/zip, rate limits |
| TTS | `tts-help-content.ts` | Prepare steps, voices/lang_code, model download vs load, file/paste |
| Convert | `converter-help-content.ts` | Presets, GPU auto, cut copy vs re-encode, extract containers, sequential queue — [08](08-video-conversion.md) |
| Capture | `capture-help-content.ts` | F2 vs ShareX, inbox, annotation tools, original vs annotated, tray — [09](09-screenshot-capture.md) |
| Settings | `settings-help-content.ts` | Leaf keys, FFmpeg probe, MCP config, console |

Each page mounts a `HelpCard` (accessible disclosure, persist collapse). Shared search filters registered sections. E2E wave `gui-help`.

### Console Panel (Right Side Sheet)

> **Source**: [`_shared_patterns.md §1`](../../_inspiration/_shared_patterns.md), [`_downloader_pseudo_logic.md §9`](../../_inspiration/_downloader_pseudo_logic.md). Unifies the console/logging pattern found across all three source apps. Placement follows the Zorivest Trade detail pane (right complementary sheet), not a bottom dock.

A shared log viewer as a right side sheet. Closed by default (unmounted). Header **Console** (left of **Commands Ctrl+K**) toggles it; expand fills the content row and hides `main`:

| Feature | Description | Source |
|---|---|---|
| Log level filtering | Exclusive level buttons: DEBUG, INFO, WARNING, ERROR, CRITICAL (exact token match; default DEBUG) | [_shared_patterns.md §1](../../_inspiration/_shared_patterns.md); MEU-27 |
| Console output theme | `console-output` uses `--color-console-bg` / `--color-console-fg` (black / console green) | MEU-27 live preview |
| Module prefix tags | `[Downloader]`, `[Transcript]`, `[TTS]`, `[Convert]`, `[Capture]`, `[yt-dlp]` | All source apps + Phase 8/9 |
| yt-dlp debug toggle | Separate checkbox: "Show yt-dlp debug output" | [_downloader_pseudo_logic.md §9](../../_inspiration/_downloader_pseudo_logic.md) |
| Search/filter | Text search within displayed logs | [_shared_patterns.md §1](../../_inspiration/_shared_patterns.md) |
| Log to file | Toggle to persist console output to `{app_data}/logs/console.log` | [_shared_patterns.md §1](../../_inspiration/_shared_patterns.md) |
| Clear button | Clears current log display (not backend logs) | All three source apps |
| Copy to clipboard | Copy selected or all log lines | [_shared_patterns.md §1](../../_inspiration/_shared_patterns.md) |
| Expand / collapse | Single toggle on the panel header left; expand fills the content row (`w-full`, hides `main`); collapse restores the 40% drawer and keeps the pane mounted | Zorivest Trade drawer; MEU-27 |
| Close | `console:close` / Escape / header toggle unmount the pane | Zorivest Trade drawer |
| Virtual scrolling | Handles 10k+ log lines without performance degradation | — |

**Visibility persistence**: open/expanded stored via `usePersistedState('ui.panel.console.visible')` and `usePersistedState('ui.panel.console.expanded')`.

**Transport (locked — no SSE):**

1. **`HealthService` is the only `seq` allocator** (monotonic `uint64`, starts at 1 each process). The structlog processor assigns `seq`, enqueues the ring, and writes the **same** JSON object to stdout (`seq` included). Process restart resets `seq`.
2. Poll `GET /health/console?after_seq=` at 500 ms while the dock is expanded (5 s when collapsed). This is the authoritative structured stream.
3. Electron main tails owned-child stdout. Lines **with** `seq` are the same events as the ring — drop them on the IPC path (renderer already has them from REST) or forward and let the UI key by `seq` (no second allocator).
4. Lines **without** `seq` (uvicorn access, foreign noise) are tagged `source: stdout` and `id: ipc:{n}` (main-process counter). They **never** reuse backend `seq`. Do not dedup them against the ring.
5. `useBackendLogs` keys ring events by `seq` and stdout-only by `ipc:*`. Clear affects the **view** only.
6. File persist is backend-side when `app.log_to_file` is true (`{app_data}/logs/console.log`).
7. Redact Bearer tokens, cookie bytes, and MCP token values before display.

### Module Internal Navigation

Each nav rail item maps to a single-page module. No internal tab routing — each page manages its own layout:

| Module | Internal Layout | Description |
|---|---|---|
| Downloader | URL bar + SABR indicator + queue table + controls | Video/playlist/channel download with quality negotiation |
| Transcript | Channel input + channel queue cards + processing controls | Batch transcript extraction with rate limiting |
| TTS | Text input + cleanup pipeline + model manager + voice selector | Text preparation → generation |
| Convert | Task segment + drop zone + presets + queue table + controls | Local compress / cut / extract — full layout in [08-video-conversion.md](08-video-conversion.md) |
| Capture | Inbox header + filmstrip + paint viewport | Region capture + annotate — full layout in [09-screenshot-capture.md](09-screenshot-capture.md) |
| Settings | Vertical section cards (per Zorivest pattern) | Per-module defaults, appearance |

---

## Downloader Page (`/` — Default Route)

> **Source**: [`_downloader_pseudo_logic.md`](../../_inspiration/_downloader_pseudo_logic.md). The Downloader page is the startup default — users land here when opening the app. It follows a top-to-bottom flow: SABR indicator → URL input → queue table → control bar.

### Layout

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  Downloader                                                       Downloader  Ctrl+1 │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─ SABR STATUS ───────────────────────────────────────────────────────────────────┐ │
│  │  ⚠️ SABR RESTRICTION ACTIVE — Quality limited to 360p, audio to MP3/M4A       │ │
│  │  [Check SABR]  [Force SABR]  [Clear SABR]                                      │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ URL INPUT ─────────────────────────────────────────────────────────────────────┐ │
│  │ 📎 Paste YouTube URL:  [https://www.youtube.com/watch?v=...         ] [+ Add]  │ │
│  │                                                                                 │ │
│  │  Quality: [1080p ▼]   [□ Audio Only]   Audio Format: [default ▼]               │ │
│  │                                                                                 │ │
│  │  ── Cookie Authentication ──────────────────────────────────────────            │ │
│  │  ( ) None  (●) From Browser  ( ) From File                                     │ │
│  │  Browser: [chrome ▼]   Profile: [Default        ]                              │ │
│  │  ⚠️ Close browser first!                               [🔌 Test Cookies]       │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ DOWNLOAD QUEUE ────────────────────────────────────────────────────────────────┐ │
│  │  ┌────────┬──────────────────────┬──────────┬──────────┬──────────┬───────────┐ │ │
│  │  │ Status │ Title                │ Quality  │ Size     │ Progress │ Speed     │ │ │
│  │  ├────────┼──────────────────────┼──────────┼──────────┼──────────┼───────────┤ │ │
│  │  │ 🔄     │ React Tutorial P1    │ 1080p    │ 245 MB   │ ████░ 78%│ 12.3 MB/s │ │ │
│  │  │ ⏳     │ React Tutorial P2    │ 1080p    │ 312 MB   │          │ —         │ │ │
│  │  │ ⏳     │ React Tutorial P3    │ 1080p    │ 198 MB   │          │ —         │ │ │
│  │  │ ✅     │ Node.js Crash Course │ 720p     │ 156 MB   │ ██████ ✓ │ Done      │ │ │
│  │  │ 🟠     │ Premium Tutorial     │ 1080p    │ —        │ Blocked  │ —         │ │ │
│  │  │ 🟤     │ Age Restricted Vid   │ Best     │ —        │ Restrict │ —         │ │ │
│  │  │ ❌     │ Deleted Video        │ Best     │ —        │ Failed   │ —         │ │ │
│  │  └────────┴──────────────────────┴──────────┴──────────┴──────────┴───────────┘ │ │
│  │                                                                                 │ │
│  │  Summary: 7 items — 1 downloading, 2 pending, 1 done, 1 blocked, 1 restricted  │ │
│  │           1 failed                                                              │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ QUEUE CONTROLS ───────────────────────────────────────────────────────────────┐  │
│  │  [▶ Start] [⏸ Pause] [▶ Resume] [⏹ Cancel] [↑ Up] [↓ Down] [⤒ Top] [⤓ Bot]  │  │
│  │  [↻ Reset Selected]  [🗑 Remove Selected]  [🗑 Clear All]                      │  │
│  └────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### SABR Indicator Panel

> **Source**: [`_downloader_pseudo_logic.md §3`](../../_inspiration/_downloader_pseudo_logic.md). YouTube's Server-Adaptive Bitrate system blocks certain download clients from high-quality formats.

| State | Display | Quality Impact |
|---|---|---|
| **Not Restricted** | Hidden (no banner) | Full quality ladder available |
| **SABR Active** | ⚠️ warning banner (orange frame) | Quality locked to 360p; audio locked to `standard_mp3`, `high_m4a` |
| **Checking** | 🔄 spinner + "Checking SABR status..." | — |

| Button | Action | API Call |
|---|---|---|
| Check SABR | Run test extraction on known video | `POST /api/v1/downloads/sabr/check` |
| Force SABR | Activate SABR mode without detection | `POST /api/v1/downloads/sabr/force` |
| Clear SABR | Deactivate SABR mode | `POST /api/v1/downloads/sabr/clear` |

**SABR mode activation effects**:
- Quality dropdown restricted to SABR-compatible options only (`360p`)
- Audio format dropdown restricted to `standard_mp3`, `high_m4a`
- All queue items using incompatible quality get status updated to `QualityBlocked` (orange)
- Items already `QualityBlocked` reset to `Pending` when SABR is cleared

**Detection sources** ([_downloader_pseudo_logic.md §3](../../_inspiration/_downloader_pseudo_logic.md)):
- **Passive detection**: yt-dlp logger watches for SABR indicator strings during download:
  - `"require a gvs po token"`
  - `"android client sabr formats require"`
  - `"ios client sabr formats require"`
- **Manual check**: `Check SABR` button runs test extraction
- **Force mode**: `Force SABR` activates without detection

### URL Input Bar Fields

| Field | Type | Default | Notes |
|---|---|---|---|
| URL input | `text` | — | Auto-detects: video / playlist / channel / shorts ([§1](../../_inspiration/_downloader_pseudo_logic.md)) |
| Quality | `select` | `1080p` | Options: Best, 2160p (4K), 1440p (2K), 1080p, 720p, 480p, 360p, 240p, 144p, Lowest |
| Audio Only | `checkbox` | `false` | When checked, shows Audio Format selector (hidden by default) |
| Audio Format | `select` | `default` | Options: default (Auto), best (Highest), lowest (Smallest), low_webm (~48kbps Opus), medium_webm (~70kbps Opus), standard_webm (~128kbps Opus), standard_m4a (~128kbps AAC), standard_mp3 (~192kbps MP3), high_m4a (~160kbps AAC). Restricted under SABR ([§6](../../_inspiration/_downloader_pseudo_logic.md)) |
| Cookie Auth | `radio` | `None` | None / From Browser / From File ([§5](../../_inspiration/_downloader_pseudo_logic.md)) |
| Browser | `select` | `chrome` | Options: chrome, firefox, edge, brave, opera, vivaldi, chromium, whale, safari. Only visible when "From Browser" selected |
| Browser Profile | `text` | `""` | Optional profile name for multi-profile browsers |
| Cookie File | `file input` | `""` | Netscape-format cookies.txt path. Only visible when "From File" selected |
| Test Cookies | `button` | — | `POST /api/v1/downloads/cookies/test` — `{ mode, browser?, profile?, cookie_file? }`. Paths only; never cookie bytes. Warning: "Close browser first!" ([§5](../../_inspiration/_downloader_pseudo_logic.md)) |

> **Quality/audio dropdown behavior under SABR**: When SABR mode activates, the quality dropdown options are dynamically restricted to `[360p]` and the audio format dropdown to `[standard_mp3, high_m4a]`. When SABR clears, full options restore ([_downloader_pseudo_logic.md §2](../../_inspiration/_downloader_pseudo_logic.md)).

### Download Queue Table (TanStack Table)

```typescript
// ui/src/renderer/src/features/downloader/DownloadQueueTable.tsx

import { createColumnHelper } from '@tanstack/react-table';

interface DownloadJob {
  id: string;
  url: string;
  video_id: string;
  title: string;
  quality: string;
  audio_only: boolean;
  audio_format: string;
  status: 'Pending' | 'Downloading' | 'Done' | 'Failed'
        | 'Skipped' | 'QualityBlocked' | 'AgeRestricted' | 'Cancelled';
  progress: number;       // 0.0 – 1.0
  speed: string | null;   // "12.3 MB/s" or null
  eta: string | null;     // "2:30" or null
  file_size: number | null;
  file_path: string | null;
  error_message: string | null;
  queue_position: number;
  created_at: string;
}
```

> **Status field includes all domain states**: `QualityBlocked` and `AgeRestricted` are first-class statuses matching the `DownloadStatus` enum in [Phase 1](01-domain-layer.md) and the state machine in [_downloader_pseudo_logic.md §4](../../_inspiration/_downloader_pseudo_logic.md). Note: `Paused` is **not** a per-item status — it is a queue-level state (the queue processor is paused, not individual items). The `DownloadStatus` enum in [Phase 0](00-overview.md) does not include `Paused`; individual items remain `Pending` or `Downloading` while the queue processor is paused.

### Status State Machine (Per-Item)

```
Pending ──→ Downloading ──→ Done
                │              ↑
                ├──→ Failed ───┘ (via Reset)
                ├──→ Cancelled
                ├──→ Skipped (duplicate/archive)
                ├──→ QualityBlocked (SABR)
                └──→ AgeRestricted
```

### Queue Processor State Machine

```
Idle ──→ Processing ──→ Idle (queue exhausted)
              │
              ├──→ Paused ──→ Processing (via Resume)
              └──→ Idle (via Cancel)
```

> **Pause is queue-level, not per-item**: When the user clicks Pause, the queue processor finishes the current download and then enters the `Paused` state. Individual items stay in their current status (`Downloading` completes to `Done` or `Failed`; remaining `Pending` items stay `Pending`). This aligns with the `DownloadStatus` enum in [Phase 0](00-overview.md), which does not include a `Paused` member.

### Queue Controls

> [!NOTE]
> **Superseded for queue surfaces by docs/build-plan/10-queue-card-ui.md**  
> The 13-button glyph toolbar below is reduced to 4 + overflow — see [Phase 10 Toolbar reduction](10-queue-card-ui.md#toolbar-reduction) and [Kebab menu](10-queue-card-ui.md#kebab-menu). The block is retained as the historical spec; the routes it names are unchanged.

> **Source**: [`APPLICATION_PURPOSE.md §4A`](../../_inspiration/APPLICATION_PURPOSE.md) — "reorder, pause, resume, cancel". [`_downloader_pseudo_logic.md §4`](../../_inspiration/_downloader_pseudo_logic.md) — Move Up/Down/Top/Bottom, Reset Selected, Clear All. [`_shared_patterns.md §2`](../../_inspiration/_shared_patterns.md) — unified `start()`, `stop()`, `pause()`, `resume()`.

| Button | Action | API Call | Enabled When |
|---|---|---|---|
| ▶ Start | Begin sequential queue processing | `POST /api/v1/downloads/start` | Queue has pending items, not processing |
| ⏸ Pause | Pause after current item completes | `POST /api/v1/downloads/pause` | Processing is active |
| ▶ Resume | Resume paused processing | `POST /api/v1/downloads/resume` | Processing is paused |
| ⏹ Cancel | Cancel current download, stop processing | `POST /api/v1/downloads/cancel` | Processing is active or paused |
| ↑ Up | Move selected item up in queue | `PUT /api/v1/downloads/reorder` | Item selected, not first |
| ↓ Down | Move selected item down in queue | `PUT /api/v1/downloads/reorder` | Item selected, not last |
| ⤒ Top | Move selected item to top | `PUT /api/v1/downloads/reorder` | Item selected, not first |
| ⤓ Bottom | Move selected item to bottom | `PUT /api/v1/downloads/reorder` | Item selected, not last |
| ↻ Reset | Reset selected failed items to Pending | `POST /api/v1/downloads/{id}/reset` | Failed item(s) selected |
| 🗑 Remove | Remove selected items from queue | `DELETE /api/v1/downloads/{id}` | Item(s) selected |
| 🗑 Clear All | Remove all items from queue | `DELETE /api/v1/downloads` | Queue not empty |

### Status Summary Bar

> **Source**: [`_downloader_pseudo_logic.md §4`](../../_inspiration/_downloader_pseudo_logic.md) — all status counts always displayed.

**Per-item status counts** (always displayed):

| Status | Color | Icon |
|---|---|---|
| Downloading | Blue (`#8be9fd`) | 🔄 |
| Pending | Gray (`#6272a4`) | ⏳ |
| Done | Green (`#50fa7b`) | ✅ |
| Failed | Red (`#ff5555`) | ❌ |
| Skipped | Purple (`#bd93f9`) | ⏭ |
| QualityBlocked | Orange (`#ffb86c`) | 🟠 |
| AgeRestricted | Brown (`#c4a882`) | 🟤 |
| Cancelled | Muted (`#44475a`) | 🚫 |

**Queue processor state** (shown as a separate indicator, not a per-item count):

| State | Color | Icon | Display |
|---|---|---|---|
| Idle | Gray | — | Hidden |
| Processing | Blue (`#8be9fd`) | 🔄 | "Processing..." |
| Paused | Yellow (`#f1fa8c`) | ⏸ | "Queue Paused" |

### REST Endpoints Consumed

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/downloads` | Add URL to queue |
| `GET` | `/api/v1/downloads` | List envelope `{ items, processor }` — not a bare array |
| `GET` | `/api/v1/downloads/{id}` | Get single job status |
| `POST` | `/api/v1/downloads/start` | Start queue processing |
| `POST` | `/api/v1/downloads/pause` | Pause queue processing |
| `POST` | `/api/v1/downloads/resume` | Resume queue processing |
| `POST` | `/api/v1/downloads/cancel` | Cancel current + stop queue |
| `DELETE` | `/api/v1/downloads/{id}` | Remove from queue |
| `DELETE` | `/api/v1/downloads` | Clear all queue items |
| `POST` | `/api/v1/downloads/{id}/reset` | Reset failed job |
| `PUT` | `/api/v1/downloads/reorder` | Reorder queue |
| `POST` | `/api/v1/downloads/sabr/check` | Run SABR detection check |
| `POST` | `/api/v1/downloads/sabr/force` | Force SABR mode on |
| `POST` | `/api/v1/downloads/sabr/clear` | Clear SABR mode |
| `GET` | `/api/v1/downloads/sabr` | Get current SABR session status (does not run a check) |
| `POST` | `/api/v1/downloads/cookies/test` | Verify cookie extraction |
| `POST` | `/api/v1/downloads/apply-defaults` | Apply Settings quality/audio to pending/blocked rows |

Routes live in [Phase 4](04-rest-api.md). `apiFetch('/downloads')` assumes the Electron base URL already includes `/api/v1`.

### Queue Polling Strategy

```typescript
// GET /downloads returns { items, processor } — processor.state drives the indicator
type DownloadList = {
  items: DownloadJob[];
  processor: { state: 'Idle' | 'Processing' | 'Paused'; current_job_id: string | null };
};

const { data } = useQuery<DownloadList>({
  queryKey: ['downloads'],
  queryFn: () => apiFetch('/downloads'),
  refetchInterval: (query) =>
    query.state.data?.processor.state === 'Processing' ? 1000 : 5000,
});
const queue = data?.items ?? [];
const isProcessing = data?.processor.state === 'Processing';
```

Do not read `isProcessing` before `data` exists (temporal dead zone). Cover active/idle cadence with a hook unit test.


---

## Transcript Page (`/transcript`)

> **Source**: [`_transcript_pseudo_logic.md`](../../_inspiration/_transcript_pseudo_logic.md). Channel transcript batch processing with YAML frontmatter, compiled Markdown with TOC, multi-volume splitting, and resume capability.

### Layout

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  Transcript                                                      Transcript  Ctrl+2  │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─ CHANNEL INPUT ─────────────────────────────────────────────────────────────────┐ │
│  │ 📺 Channel URL:  [https://www.youtube.com/@channel...           ] [+ Add]      │ │
│  │    Accepts: /@handle, /c/name, /channel/UCxxx, /user/name                       │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ CHANNEL QUEUE ─────────────────────────────────────────────────────────────────┐ │
│  │                                                                                 │ │
│  │  ┌──────────────────────────────────────────────────────────────────────────┐   │ │
│  │  │ ✅ [DONE] Code With Antonio                                             │   │ │
│  │  │    142 videos · 142/142 transcripts · 2.4M words                       │   │ │
│  │  │    Output: transcripts/code_with_antonio/                               │   │ │
│  │  │    [📖 View Compiled] [📦 Open ZIP] [📂 Open Folder] [🗑 Remove]       │   │ │
│  │  └──────────────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                                 │ │
│  │  ┌──────────────────────────────────────────────────────────────────────────┐   │ │
│  │  │ 🔄 Processing: Fireship                                                │   │ │
│  │  │    523 videos · 287/523 transcripts · 1.1M words                       │   │ │
│  │  │    ████████████░░░░░░░ 54.9%                                           │   │ │
│  │  │    Rate: 1 req/6s · Batch 6/11 · ETA: ~39 min                         │   │ │
│  │  │    Last: "JavaScript in 100 Seconds" ✅                                │   │ │
│  │  └──────────────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                                 │ │
│  │  ┌──────────────────────────────────────────────────────────────────────────┐   │ │
│  │  │ ⏳ Queued: Theo - t3.gg                                                │   │ │
│  │  │    891 videos · 0/891 transcripts                                      │   │ │
│  │  │    [↑] [↓] [🗑 Remove]                                                │   │ │
│  │  └──────────────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                                 │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ PROCESSING CONTROLS ──────────────────────────────────────────────────────────┐  │
│  │  [▶ Start]  [⏸ Pause]  [▶ Resume]  [⏹ Stop]                                  │  │
│  └────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### Channel Queue Card Fields

> **Source**: [`_transcript_pseudo_logic.md §5`](../../_inspiration/_transcript_pseudo_logic.md).

| Field | Source | Notes |
|---|---|---|
| Channel name | `TranscriptJob.channel_name` | Resolved from URL on add |
| Status badge | `TranscriptJob.status` | ⏳ Queued, 🔄 Processing, ⏸ Paused, ✅ Done, ❌ Failed |
| Video count | `TranscriptJob.video_count` | From API (not `video_ids.length` — that field was dropped) |
| Transcripts done | `TranscriptJob.transcripts_done` | `COUNT(items WHERE Done)` — **not** `progress.json` |
| Word count | `TranscriptJob.word_count` | Denormalized on the job row |
| Progress bar | `transcripts_done / video_count` | Visual progress indicator |
| Rate display | From rate limiting settings | `1 req/{delay}s` |
| Batch progress | Service-computed on `GET /transcripts/{id}` if present | Optional; do not invent a second store |
| ETA | Computed from rate + remaining pending items | Estimated time to completion |
| Last processed | `last_title` + `last_item_status` | "JavaScript in 100 Seconds" ✅ |
| Output path | `TranscriptJob.output_dir` | Directory containing raw + compiled output |

### Channel Queue Management

> **Source**: [`_transcript_pseudo_logic.md §1, §6`](../../_inspiration/_transcript_pseudo_logic.md).

- Channels can be **added**, **removed**, and **reordered** (Move Up / Move Down)
- Queue is **persisted between sessions** (SQLite, not JSON config)
- Completed channels show `✅ [DONE]` prefix with green accent
- Channel resolution accepts all URL formats: `/@handle`, `/c/name`, `/channel/UCxxx`, `/user/username`

### Output Structure

> **Source**: [`_transcript_pseudo_logic.md §4, §8`](../../_inspiration/_transcript_pseudo_logic.md).

```
{TranscriptJob.output_dir}/          # already {transcript.output_dir}/{slug(channel_name)}
├── raw/
│   ├── {video_id}.md              # Individual transcript with YAML frontmatter
│   └── ...
├── compiled/
│   ├── {channel_name}_vol1.md     # Compiled Markdown with TOC
│   └── {channel_name}_vol2.md     # (if word count > max_words_per_document)
├── progress.json                  # Optional write-through export — not resume SoT
└── {channel_name}_raw.zip         # Archive of raw files (auto-created on completion)
```

**Individual transcript format** (YAML frontmatter):
```markdown
---
video_id: dQw4w9WgXcQ
title: "Video Title"
channel: "Channel Name"
url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
date: 2026-05-26
---

# Video Title

Transcript text content here, one line per transcript segment...
```

**Compiled Markdown format**:
- H1 heading: Channel name
- Table of contents with links to each video section
- H2 heading per video: Video title
- Full transcript text under each heading
- Multi-volume splitting at configurable `max_words_per_document` (default: 490,000)
- Volume naming: `{channel_name}_vol1.md`, `{channel_name}_vol2.md`

### Completed Channel Actions

| Button | Action | Notes |
|---|---|---|
| 📖 View Compiled | Open compiled Markdown in system viewer | IPC `openPath` (first volume) |
| 📦 Open ZIP | Open raw transcript archive | IPC `openPath` |
| 📂 Open Folder | Open output directory | IPC `openPath` |
| ↺ Requeue | `Cancelled` → `Pending` | `POST /transcripts/{id}/requeue` — hidden unless status is `Cancelled` |
| ↻ Retry | `Failed` → `Pending` | `POST /transcripts/{id}/retry` — hidden unless status is `Failed` |
| 🗑 Remove | Remove channel from queue | Confirmation dialog; does not delete files |

### REST Endpoints Consumed

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/transcripts` | Add channel to queue |
| `GET` | `/api/v1/transcripts` | List envelope `{ items, processor }` — not a bare array |
| `GET` | `/api/v1/transcripts/{id}` | Job + aggregates (`transcripts_done`, `last_title`) — no transcript text |
| `DELETE` | `/api/v1/transcripts/{id}` | Remove channel from queue |
| `PUT` | `/api/v1/transcripts/reorder` | Reorder channel queue |
| `POST` | `/api/v1/transcripts/start` | Start batch processing |
| `POST` | `/api/v1/transcripts/pause` | Pause processing |
| `POST` | `/api/v1/transcripts/resume` | Resume processing |
| `POST` | `/api/v1/transcripts/stop` | Stop — parent `Cancelled` |
| `POST` | `/api/v1/transcripts/{id}/requeue` | Requeue a cancelled channel |
| `POST` | `/api/v1/transcripts/{id}/retry` | Retry a failed channel |
| `POST` | `/api/v1/transcripts/{id}/compile` | Compile channel Markdown |

Poll `GET /transcripts` the same way as downloads: unwrap `items`, use `processor` for the Start/Pause/Resume/Stop bar. Do not read `progress.json` for card state.

---

## TTS Page (`/tts`)

> **Source**: [`_text_cleanup_pseudo_logic.md`](../../_inspiration/_text_cleanup_pseudo_logic.md), [`_kokoro_production_settings.md`](../../_inspiration/_kokoro_production_settings.md), [`APPLICATION_PURPOSE.md §4C`](../../_inspiration/APPLICATION_PURPOSE.md). Text-to-speech with a two-phase workflow: (1) text preparation pipeline, (2) Kokoro generation.

### Layout

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  Text-to-Speech                                                         TTS  Ctrl+3  │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─ TEXT INPUT ───────────────────────┬─ MODEL & VOICE ─────────────────────────────┐│
│  │                                    │                                              ││
│  │  [📂 Load File]  [📋 Paste]       │  ── Model Manager ────────────────────────── ││
│  │                                    │                                              ││
│  │  ┌──────────────────────────────┐  │  ┌──────────────────────────────────────┐   ││
│  │  │                              │  │  │ Loaded: 🟢 Kokoro ONNX FP16         │   ││
│  │  │  Enter or paste text here    │  │  │ Device: CUDA (RTX 4070)             │   ││
│  │  │  for speech generation...    │  │  │ VRAM: 412 MB                         │   ││
│  │  │                              │  │  │                                      │   ││
│  │  │                              │  │  │ [Unload Model]                       │   ││
│  │  │                              │  │  └──────────────────────────────────────┘   ││
│  │  │                              │  │                                              ││
│  │  │                              │  │  Available Models:                           ││
│  │  │                              │  │  ┌────────────────────┬───────┬──────────┐  ││
│  │  │                              │  │  │ Model              │ Size  │ Status   │  ││
│  │  │                              │  │  ├────────────────────┼───────┼──────────┤  ││
│  │  │                              │  │  │ PyTorch FP32       │ 326MB │ [⬇ Get]  │  ││
│  │  │                              │  │  │ ONNX FP16          │ 163MB │ 🟢 Ready │  ││
│  │  │                              │  │  │ ONNX INT8          │  82MB │ [⬇ Get]  │  ││
│  │  │                              │  │  └────────────────────┴───────┴──────────┘  ││
│  │  │                              │  │                                              ││
│  │  └──────────────────────────────┘  │  ── Voice Selection ─────────────────────── ││
│  │                                    │                                              ││
│  │  Stats: 1,247 words · 42 sentences │  Language: [English (US) ▼]                  ││
│  │  Est. duration: ~5 min 30s         │                                              ││
│  │                                    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ││
│  │  ── Text Preparation Pipeline ──── │  │ 🎤 Heart  │  │ 🎤 Bella │  │ 🎤 Adam  │  ││
│  │  [●] Punctuation normalization     │  │ af_heart  │  │ af_bella │  │ am_adam  │  ││
│  │  [●] Symbol conversion             │  │ Female    │  │ Female   │  │ Male     │  ││
│  │  [●] Number expansion              │  │  ● ───────│  │          │  │          │  ││
│  │  [●] Currency formatting            │  └──────────┘  └──────────┘  └──────────┘  ││
│  │  [●] ALL CAPS normalization        │                                              ││
│  │  [ ] Chapter marker standardization│  Speed: ◄──────●──────► 1.0x                 ││
│  │  [●] URL/email removal             │  Output: [MP3 ▼]   Path: [~/Documents ▼]     ││
│  │  [●] Page number removal           │                                              ││
│  │  [●] Whitespace normalization      │                                              ││
│  │  [●] Smart TTS chunking (250 chars)│                                              ││
│  │  [●] Kokoro-specific normalization │  (required post-cleanup step)                ││
│  │                                    │                                              ││
│  │  [🔧 Preview Cleaned Text]         │                                              ││
│  └────────────────────────────────────┴──────────────────────────────────────────────┘│
│                                                                                      │
│  ┌─ GENERATE ──────────────────────────────────────────────────────────────────────┐ │
│  │  [🔊 Generate]  [⏹ Cancel]  ████████████████░░░░░░ 68%  ·  Segment 34/50     │ │
│  │                                                                                 │ │
│  │  Last output: speech_output_2026-05-30.mp3    [📂 Open File] [📂 Open Folder]   │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### Text Preparation Pipeline

> **Source**: [`_text_cleanup_pseudo_logic.md §Part 2`](../../_inspiration/_text_cleanup_pseudo_logic.md) — 10-step TTS normalization pipeline. [`_kokoro_production_settings.md §3`](../../_inspiration/_kokoro_production_settings.md) — Kokoro-specific rules.

The pipeline runs **before generation** as a configurable preprocessing step. Each step has a toggle checkbox. Steps are implemented server-side in `TextPreparationService`; the GUI controls which steps are enabled.

| # | Step | Default | Source | Description |
|---|---|---|---|---|
| 1 | Punctuation normalization | ✅ On | [cleanup §1](../../_inspiration/_text_cleanup_pseudo_logic.md) | Collapse `???→?`, `!!!→!`, `....→…`, `---→—` |
| 2 | Symbol conversion | ✅ On | [cleanup §2](../../_inspiration/_text_cleanup_pseudo_logic.md) | `™→trademark`, `®→registered`, `&→and`, `@→at`, `#5→number 5` |
| 3 | Number expansion | ✅ On | [cleanup §3](../../_inspiration/_text_cleanup_pseudo_logic.md), [Kokoro §3A](../../_inspiration/_kokoro_production_settings.md) | Ordinals to words; spell ALL numbers (Kokoro: "thirty" not "30") |
| 4 | Currency formatting | ✅ On | [cleanup §4](../../_inspiration/_text_cleanup_pseudo_logic.md) | `$100→100 dollars`, `€50→50 euros` |
| 5 | ALL CAPS normalization | ✅ On | [cleanup §5](../../_inspiration/_text_cleanup_pseudo_logic.md) | Words >4 chars → Title Case; ≤4 chars kept (acronyms) |
| 6 | Chapter marker standardization | ❌ Off | [cleanup §6](../../_inspiration/_text_cleanup_pseudo_logic.md) | `CHAPTER→Chapter`, Roman numerals → Arabic. Off by default (book-specific) |
| 7 | URL/email removal | ✅ On | [cleanup §7](../../_inspiration/_text_cleanup_pseudo_logic.md) | URLs → `[link]`, emails → `[email]` |
| 8 | Page number removal | ✅ On | [cleanup §8](../../_inspiration/_text_cleanup_pseudo_logic.md) | Remove standalone number-only lines (`^\s*\d+\s*$`), collapse resulting blank lines |
| 9 | Whitespace normalization | ✅ On | [cleanup §9](../../_inspiration/_text_cleanup_pseudo_logic.md) | Collapse spaces, normalize line endings, max 2 blank lines |
| 10 | Smart TTS chunking | ✅ On | [cleanup §10](../../_inspiration/_text_cleanup_pseudo_logic.md) | Sentence-aware chunking via spaCy, configurable `max_chars` (default: 250) |
| **11** | **Kokoro-specific normalization** | ✅ On | [Kokoro §3](../../_inspiration/_kokoro_production_settings.md) | Acronym spacing ("AI"→"A I"), sentence length <25 words, Unicode cleanup (curly quotes→straight), ellipses removal. **Required post-cleanup step, not part of the original 10-step pipeline.** |

**Preview button**: `🔧 Preview Cleaned Text` opens a diff view showing raw → cleaned text side-by-side. Server-side: `POST /api/v1/tts/prepare` with `{ text, enabled_steps[] }` returns cleaned text.

### Text Input Area Fields

| Field | Type | Notes |
|---|---|---|
| Text area | `textarea` | Multi-line, resizable, with character/word counter |
| Load File button | `file input` | IPC `readTextFile` — `.txt`/`.md` only, `maxBytes` 2 MiB |
| Paste button | `button` | IPC `readClipboardText` — not `navigator.clipboard` in the sandboxed renderer |
| Word count | `readonly` | Computed on text change |
| Sentence count | `readonly` | Computed on text change |
| Duration estimate | `readonly` | ~150 words/minute at speed 1.0 |

### Model Manager Panel

LM Studio-inspired workflow: Browse → Download → Load → Use → Unload

| Field | Source | Notes |
|---|---|---|
| Loaded model | `GET /api/v1/models/status` | Shows currently loaded model or "None" |
| Device | `GET /api/v1/models/status` | CUDA / MPS / CPU with GPU name |
| VRAM/RAM usage | `GET /api/v1/models/status` | Memory consumption of loaded model |
| Available models | `GET /api/v1/models/available` | Four seeded variants: PyTorch FP32, ONNX FP32, ONNX FP16, ONNX INT8 |
| Download status | `GET /api/v1/models/download-runtime` | Bind percent to the row whose `id === runtime.variant_id`. Other rows stay Get/Ready. Poll 1s while `Downloading` |
| Load button | Per-model | `POST /api/v1/models/load` with device preference |
| Unload button | Global | `POST /api/v1/models/unload` |
| Device selector | `select` | Auto / CUDA / CPU (shown during load action) |

### Voice Selector Grid

Voice cards displayed in a responsive grid, filtered by language:

| Language | Lang Code | Voices | Default |
|---|---|---|---|
| English (US) | `a` | af_heart, af_bella, af_nicole, af_sarah, af_sky, am_adam, am_michael, am_eric (20 total) | am_eric |
| English (UK) | `b` | bf_emma, bf_isabella, bm_george, bm_lewis (8 total) | bf_emma |
| Spanish | `e` | ef_dora, em_alex, em_santa | ef_dora |
| French | `f` | ff_siwis | ff_siwis |
| Hindi | `h` | hf_alpha, hf_beta, hm_omega, hm_psi | hf_alpha |
| Italian | `i` | if_sara, im_nicola | if_sara |
| Japanese | `j` | jf_alpha, jf_gongitsune, jm_kumo (5 total) | jf_alpha |
| Portuguese (BR) | `p` | pf_dora, pm_alex, pm_santa | pf_dora |

> **Critical rule** ([_kokoro_production_settings.md §1](../../_inspiration/_kokoro_production_settings.md)): Voice prefix first character = required lang_code. The UI auto-selects the correct lang_code when a voice is chosen — users never see or set lang_code directly. Using wrong lang_code produces accented/garbled output.

### Generation Controls

| Field | Type | Default | Notes |
|---|---|---|---|
| Speed slider | `range` | 1.0 | Range: 0.5 – 2.0, step 0.1 ([_tts_pseudo_logic.md §2](../../_inspiration/_tts_pseudo_logic.md)). Presets: 0.8 (technical), 1.0 (normal), 1.1 (casual) |
| Output format | `select` | MP3 | MP3, WAV |
| Output path | `directory picker` | `tts.output_path` (`~/Documents`) | Native Electron directory dialog; same default as Settings |
| Generate button | `button` | — | Disabled until model loaded + text entered |

### REST Endpoints Consumed

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/tts/generate` | Start generation (sends text + voice + speed + enabled cleanup steps) |
| `GET` | `/api/v1/tts/{id}` | Get job status + progress (segment N/M) |
| `DELETE` | `/api/v1/tts/{id}` | Cancel generation |
| `GET` | `/api/v1/tts/voices` | List available voices |
| `POST` | `/api/v1/tts/prepare` | Preview text cleanup (returns cleaned text without generating) |
| `GET` | `/api/v1/models/available` | `{ items: ModelVariantOut[] }` — unwrap `items`; `is_loaded` is on `/models/status`, not the variant |
| `GET` | `/api/v1/models/downloaded` | `{ items }` |
| `POST` | `/api/v1/models/download` | Download a variant |
| `POST` | `/api/v1/models/load` | Load model (with device preference) |
| `POST` | `/api/v1/models/unload` | Unload model |
| `GET` | `/api/v1/models/status` | Loaded model only (`is_loaded`, device, memory) |
| `GET` | `/api/v1/models/download-runtime` | In-flight HF fetch (`variant_id`, `state`, `fraction`) |

`POST /tts/generate` body: `text`, `voice`, `speed`, `format`, `enabled_steps`, `source_kind` (`inline`\|`file`), `source_path?` (filename metadata only — backend does not open it). File-load uses IPC `readTextFile` (dialog). Job responses have `text_preview` / `text_hash` — **not** the full text. Editor resume is `PUT /settings/tts` key `input_text`. Cancel is on the Generate bar (`DELETE /tts/{id}`).

---

## Convert Page (`/convert`)

> **SSOT:** [08-video-conversion.md](08-video-conversion.md). Do not implement under MEU-19–23.

Lazy route `/convert`, rail item below TTS, `Ctrl+4`. Downloader-shaped queue: task segment (Compress / Cut / Extract) → drop/browse → named presets (default Balanced) → Add → table → Start/Pause/Resume/Cancel. GPU is a status chip. Advanced CQ/scale/audio is collapsed. No inner routes.

---

## Capture Page (`/capture`)

> **SSOT:** [09-screenshot-capture.md](09-screenshot-capture.md). Do not implement under MEU-19–23 or MEU-33.

Lazy route `/capture`, rail item below Convert, `Ctrl+5`. Inbox path + hotkey + **Capture region**; filmstrip + viewport with arrow/box/highlight/text/pixelate/eraser; Save bakes `{stem}.annotated.png`. Tray + global F2 live in Electron main. Catalog poll `{ items }` (no processor). No inner routes.

---

## Settings Page (`/settings`)

> Follows the Zorivest Settings page pattern — vertical stack of card sections with grouped settings. Dark theme cards with muted borders.

### Layout

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  Settings                                                         Settings  Ctrl+,   │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─ DOWNLOAD SETTINGS ──────────────────────────────────────────────────────────────┐│
│  │                                                                                  ││
│  │  Download Path        [C:\Users\Mat\Downloads\av-kit         ] [Browse...]       ││
│  │  Default Quality      [1080p ▼]  [Apply to pending]                              ││
│  │  FFmpeg path          [                                      ] [Browse...]       ││
│  │  Default Audio Format [default ▼]   (9 options per §6 of downloader logic)       ││
│  │  Cookie Mode          ( ) None  (●) Browser  ( ) File                            ││
│  │  Cookie Browser       [chrome ▼]                                                 ││
│  │  Cookie Browser Profile [Default    ]                                            ││
│  │  Cookie File Path     [                                      ] [Browse...]       ││
│  │  Archive Tracking     [●] Skip previously downloaded videos                      ││
│  │  yt-dlp Debug Output  [□] Show yt-dlp debug messages in console                 ││
│  │                                                                                  ││
│  └──────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                      │
│  ┌─ TRANSCRIPT SETTINGS ────────────────────────────────────────────────────────────┐│
│  │                                                                                  ││
│  │  Output Directory     [C:\Users\Mat\Documents\Transcripts    ] [Browse...]       ││
│  │  Requests per Hour    [300    ]                                                  ││
│  │  Delay Between (sec)  [6      ]                                                  ││
│  │  Max Retries          [3      ]                                                  ││
│  │  Retry Delay (sec)    [30     ]                                                  ││
│  │  Batch Size           [50     ]                                                  ││
│  │  Batch Pause (sec)    [300    ]                                                  ││
│  │  Max Videos/Channel   [0      ]     0 = no limit                                 ││
│  │  Max Words/Volume     [490000 ]     Split compiled Markdown at this word count    ││
│  │                                                                                  ││
│  └──────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                      │
│  ┌─ TTS SETTINGS ───────────────────────────────────────────────────────────────────┐│
│  │                                                                                  ││
│  │  Models Directory     [~/.avkit/models                       ] [Browse...]       ││
│  │  Default Voice        [am_eric ▼]                                                ││
│  │  Default Speed        [1.0 ▼]                                                    ││
│  │  Default Output Format[MP3 ▼]                                                    ││
│  │  Default Device       [Auto ▼]      Options: Auto, CUDA, CPU                    ││
│  │  Chunk Max Chars      [250   ]      Smart TTS chunking threshold                 ││
│  │                                                                                  ││
│  └──────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                      │
│  ┌─ CONVERT SETTINGS ───────────────────────────────────────────────────────────────┐│
│  │  Output Directory     [~/Videos/av-kit                       ] [Browse...]       ││
│  │  Default Preset       [Balanced ▼]                                               ││
│  │  Skip existing        [●]                                                        ││
│  │  GPU preference       [Auto ▼]      Auto, NVIDIA, AMD, Intel, Software           ││
│  └──────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                      │
│  ┌─ CONSOLE & LOGGING ──────────────────────────────────────────────────────────────┐│
│  │                                                                                  ││
│  │  Default Log Level    [INFO ▼]      DEBUG | INFO | WARNING | ERROR | CRITICAL    ││
│  │  Log to File          [□]           Persist to {app_data}/logs/console.log       ││
│  │  Console Visible      [●]           Show console panel on startup                ││
│  │                                                                                  ││
│  └──────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                      │
│  ┌─ APPEARANCE ─────────────────────────────────────────────────────────────────────┐│
│  │                                                                                  ││
│  │  Theme       [🌙 Dark]  [☀️ Light]                                               ││
│  │                                                                                  ││
│  └──────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                      │
│  ┌─ STARTUP ────────────────────────────────────────────────────────────────────────┐│
│  │  Start av-kit when I sign in  [□]   per-user Run key; default off                ││
│  │  Start minimized              [□]   only while the parent is on; tray + F2       ││
│  │  (hidden in unpackaged / Linux; not a Windows service)                           ││
│  └──────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                      │
│  ┌─ DEPENDENCIES ───────────────────────────────────────────────────────────────────┐│
│  │                                                                                  ││
│  │  yt-dlp       v2026.05.15    ✅ Available                                        ││
│  │  FFmpeg       7.1.2          ✅ Available      [🔄 Check Dependencies]            ││
│  │                                                                                  ││
│  └──────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### Settings Key Convention

Logical keys below are `namespace.leaf`. Persist with `PUT /api/v1/settings/{namespace}` and a **leaf-key** body (`{ "quality": "1080p" }`, not `{ "downloader.quality": "1080p" }`). Extra keys → 422.

| Key | Type | Default | Source |
|---|---|---|---|
| `downloader.path` | `string` | `~/Downloads/av-kit` | [Downloader §8](../../_inspiration/_downloader_pseudo_logic.md) |
| `downloader.ffmpeg_path` | `string` | `""` | Phase 7 probe #1 — empty means skip to bundle |
| `downloader.quality` | `string` | `1080p` | [Downloader §8](../../_inspiration/_downloader_pseudo_logic.md) |
| `downloader.audio_only` | `boolean` | `false` | [Downloader §8](../../_inspiration/_downloader_pseudo_logic.md) |
| `downloader.audio_format` | `string` | `default` | [Downloader §8](../../_inspiration/_downloader_pseudo_logic.md) |
| `downloader.cookie_mode` | `string` | `none` | [Downloader §8](../../_inspiration/_downloader_pseudo_logic.md) |
| `downloader.cookie_browser` | `string` | `chrome` | [Downloader §8](../../_inspiration/_downloader_pseudo_logic.md) |
| `downloader.cookie_browser_profile` | `string` | `""` | [Downloader §8](../../_inspiration/_downloader_pseudo_logic.md) |
| `downloader.cookie_file_path` | `string` | `""` | [Downloader §8](../../_inspiration/_downloader_pseudo_logic.md) |
| `downloader.archive_tracking` | `boolean` | `true` | [Downloader §7](../../_inspiration/_downloader_pseudo_logic.md) |
| `downloader.yt_dlp_debug` | `boolean` | `false` | [Downloader §8](../../_inspiration/_downloader_pseudo_logic.md) |
| `transcript.output_dir` | `string` | `~/Documents/Transcripts` | [Transcript §7](../../_inspiration/_transcript_pseudo_logic.md) |
| `transcript.requests_per_hour` | `number` | `300` | [Transcript §3](../../_inspiration/_transcript_pseudo_logic.md) |
| `transcript.delay_between_requests` | `number` | `6` | [Transcript §3](../../_inspiration/_transcript_pseudo_logic.md) |
| `transcript.max_retries` | `number` | `3` | [Transcript §3](../../_inspiration/_transcript_pseudo_logic.md) |
| `transcript.retry_delay` | `number` | `30` | [Transcript §3](../../_inspiration/_transcript_pseudo_logic.md) |
| `transcript.batch_size` | `number` | `50` | [Transcript §3](../../_inspiration/_transcript_pseudo_logic.md) |
| `transcript.pause_between_batches` | `number` | `300` | [Transcript §3](../../_inspiration/_transcript_pseudo_logic.md) |
| `transcript.playlist_end` | `number` | `0` | [Transcript §7](../../_inspiration/_transcript_pseudo_logic.md) |
| `transcript.max_words_per_document` | `number` | `490000` | [Transcript §4](../../_inspiration/_transcript_pseudo_logic.md) |
| `tts.models_directory` | `string` | `~/.avkit/models` | — |
| `tts.voice` | `string` | `am_eric` | [Kokoro §1](../../_inspiration/_kokoro_production_settings.md) |
| `tts.speed` | `number` | `1.0` | [Kokoro §2](../../_inspiration/_kokoro_production_settings.md) |
| `tts.output_format` | `string` | `MP3` | — |
| `tts.output_path` | `string` | `~/Documents` | [TTS §7](../../_inspiration/_tts_pseudo_logic.md) |
| `tts.device` | `string` | `auto` | — |
| `tts.chunk_max_chars` | `number` | `250` | [Cleanup §10](../../_inspiration/_text_cleanup_pseudo_logic.md) |
| `tts.input_text` | `string` | `""` | [TTS §7](../../_inspiration/_tts_pseudo_logic.md) — last entered text saved for resume after restart |
| `converter.output_dir` | `string` | `~/Videos/av-kit` | [08-video-conversion.md](08-video-conversion.md) |
| `converter.default_preset` | `string` | `balanced` | Phase 8 |
| `converter.skip_existing` | `boolean` | `true` | Phase 8 |
| `converter.gpu_preference` | `string` | `auto` | Phase 8 |
| `capture.inbox_dir` | `string` | `~/Pictures/av-kit` | [09-screenshot-capture.md](09-screenshot-capture.md) |
| `capture.hotkey` | `string` | `F2` | Phase 9 |
| `capture.copy_to_clipboard` | `boolean` | `false` | Phase 9 |
| `capture.close_to_tray` | `boolean` | `true` | Phase 9 |
| `app.log_level` | `string` | `INFO` | [_shared_patterns.md §1](../../_inspiration/_shared_patterns.md) |
| `app.log_to_file` | `boolean` | `false` | [_shared_patterns.md §1](../../_inspiration/_shared_patterns.md) |
| `app.console_visible` | `boolean` | `true` | [Downloader §8](../../_inspiration/_downloader_pseudo_logic.md) |
| `ui.theme` | `string` | `dark` | — |
| `ui.rail.collapsed` | `boolean` | `false` | — |
| `ui.panel.console.visible` | `boolean` | `false` | — |
| `ui.panel.console.expanded` | `boolean` | `false` | — |

**Not a settings key:** login-item state lives in the OS, not SQLite. Do **not** add `app.open_at_login` or `app.start_minimized`. `PUT /settings/{namespace}` extra-forbid already rejects those leaves.

### Startup (login item)

> **MEU-61.** Per-user “Start av-kit when I sign in”. This is **not** Zorivest’s Service Manager checkbox labeled “Auto-start on boot” (Windows service / WinSW / UAC / LocalSystem). av-kit has no Windows service — see [Dependencies / readiness / MCP](#dependencies--readiness--mcp-settings-cards) (**not** service-install). Twin to port: Zorivest `ui/src/main/login-item.ts` + `StartAtSignInControl.tsx` (MEU-495), not `ServiceManager.setAutoStart`.

**Promise:** after this Windows (or macOS) user signs in, the OS starts the **installed** `av-kit.exe` as that user. Electron then spawns the FastAPI child (`spawnOwned`) as today. Nobody signed in ⇒ the app is not running.

**Source of truth:** the OS login-item store. Windows: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` plus Explorer `StartupApproved\Run` (Task Manager → Startup can disable an entry without deleting it). Not `electron-store`, not `PUT /settings/{namespace}`.

**API:** Electron [`app.setLoginItemSettings` / `app.getLoginItemSettings`](https://www.electronjs.org/docs/latest/api/app) — documented **macOS and Windows only**. If `path`/`args` passed to `set` are not the same pair passed to `get`, `openAtLogin` is wrong. Linux: the call is a no-op — do not draw a control that would lie.

**Support classification** (`classifyLoginItemSupport`), widest-first so the reason shown is the honest one:

| Reason | When | UI |
|--------|------|----|
| `platform` | not `win32` and not `darwin` | draw nothing |
| `not-packaged` | `app.isPackaged === false` | draw nothing (dev `electron.exe` must not enter the Run key) |
| supported | packaged `win32` / `darwin` | draw the Startup card |

av-kit Phase 7 ships **NSIS only** — there is no portable target in this MEU. A later portable **must** add a `portable` refusal before offering the toggle (Zorivest `PORTABLE-AUTOSTART-EXTRACTION-PATH`: a portable is `packaged: true` and extracts to `%TEMP%\nsm*.tmp\...`).

**Pinned registry value name:** `LOGIN_ITEM_NAME` = `com.avkit.app` (electron-builder `appId` in `ui/electron-builder.yml`). Pass `name: LOGIN_ITEM_NAME` on every `setLoginItemSettings` so NSIS uninstall and Electron agree. Do not rely on Electron’s default AppUserModelId remaining equal to `appId`.

**Path / args:** `path` is always `process.execPath`. av-kit is NSIS, not Squirrel — do **not** use the Electron docs’ parent-directory Update.exe stub. `args` is either `[]` (windowed) or `[START_MINIMIZED_FLAG]` where `START_MINIMIZED_FLAG` = `--start-minimized`. Match that token as a whole argv entry, never a substring (Chromium inserts other switches; a file path could contain the letters).

**Read (`readStartAtSignIn`):** live from the OS every time (Task Manager can change it). **Windows:** probe the minimized argv first, then windowed. `openAtLogin` is necessary and not sufficient: also honor `executableWillLaunchAtLogin === false` and a matching `launchItems[].enabled === false`. Absent Windows approval fields mean “nothing said”, never “disabled”. `startMinimizedSupported` is `true`. **macOS:** `path`/`args`/`name` and `openAsHidden`/`wasOpenedAsHidden` are not a working minimized store on current Electron (42.x types: `openAsHidden` does not work on macOS 13+; Electron issue [#37228](https://github.com/electron/electron/issues/37228) / PR [#37244](https://github.com/electron/electron/pull/37244) — SMAppService dropped hidden login). `enabled` is `openAtLogin`. `minimized` is always `false`. `startMinimizedSupported` is `false`.

**Write (`writeStartAtSignIn`):** the renderer sends only two booleans. Main validates `typeof === 'boolean'` for both; any other type throws `TypeError` and must not call Electron. **Windows:** clear the variant that is **not** being registered (`openAtLogin: false` with the other `args`) then write the requested variant (`args` `[]` or `[START_MINIMIZED_FLAG]`). Do **not** pass `openAsHidden`. **macOS:** `args` stay `[]`; persist only `openAtLogin`; ignore the minimized boolean (Electron cannot keep a hidden login item on macOS 13+). Return a fresh `readStartAtSignIn` (a declined OS write shows as off). Unsupported copies return the unsupported state without throwing. Turning `enabled` off clears `minimized` regardless of the second argument.

**Default:** **off.** First packaged launch does not register a login item. Human-approved 2026-09-20 (request to implement the prior recommendation).

**Start minimized:** **Windows only.** Drawn **only while** the parent checkbox is on **and** `startMinimizedSupported` is true ([UX2](../../.agent/docs/emerging-standards.md) exception: the field is always irrelevant when there is no launch, and the Startup section header is the containing context). Packaged macOS still shows “Start av-kit when I sign in” (`openAtLogin` / `SMAppService.mainAppService` default) but does **not** draw Start minimized — Electron 42 cannot persist or observe a hidden login item on macOS 13+. On a `--start-minimized` launch, keep the existing `show: false` BrowserWindow and skip `window.show()` via `revealMainWindow` (the only `show()` in `index.ts` lives in that helper). Tray **Show window** still shows it. Close-to-tray (`capture.close_to_tray`) is independent. Do **not** use Electron `openAsHidden` on either platform as the advertised Start minimized path. `loginLaunchShouldHideWindow` may still honor pre-Ventura `wasOpenedAsHidden` as best-effort so `index.ts` never contains the `openAsHidden` token; that is not a Settings control.

**Apply model:** immediate. No Settings Save, no G23 dirty pulse, no `PUT /settings`. G23 applies to forms that persist app data; this control writes the OS.

**IPC** (allowlisted kebab-case, same family as `get-setup-readiness`):

| Channel | Payload | Result |
|---------|---------|--------|
| `login-item-get` | empty / `{}` `.strict()` | `LoginItemState` |
| `login-item-set` | `{ enabled: boolean, minimized: boolean }` `.strict()` | `LoginItemState` (read-back) |

Both booleans are **required** on set (a missing `minimized` is reject, not “default windowed”). Extra fields reject. The renderer never sends `path`, `args`, or `name`.

**Preload:** `window.api.loginItemGet(): Promise<LoginItemState>` and `window.api.loginItemSet(enabled: boolean, minimized: boolean): Promise<LoginItemState>`. If the method is missing (older preload), the Settings effect treats the copy as unsupported and does not throw.

`LoginItemState`:

```ts
type LoginItemState =
  | {
      supported: true
      enabled: boolean
      minimized: boolean
      startMinimizedSupported: boolean
    }
  | { supported: false; reason: 'platform' | 'not-packaged'; enabled: false; minimized: false }
```

`minimized` is only ever true alongside `enabled: true` and `startMinimizedSupported: true`.

**HelpCard:** Settings help gains a Startup section whose body contains the sentence that the control registers a per-user Startup entry, needs no administrator approval, can be turned off here or in Task Manager → Startup, and that Start minimized waits in the notification area so F2 still works.

**E2E:** Playwright launches unpackaged Electron (`app.isPackaged === false`), so the card **must not** appear. Extend Wave 4 `settings.test.ts` with a named case whose title contains `AC-61.17`: assert `start-at-sign-in-panel` is absent. Unit/RTL tests inject `supported: true` and use `start-at-sign-in-checkbox` / `start-minimized-checkbox`. A live Run-key mutation is not an agent-sandbox requirement; packaged VM proof stays the Phase 7 clean-machine `[B]` path.

**Uninstall:** [07-distribution.md](07-distribution.md) NSIS `customUnInstall` deletes the pinned Run value **and** the matching `StartupApproved\Run` value via two executable (non-comment) `DeleteRegValue HKCU` statements (a Run entry is a **value**, not a key).

**Out of this card:** Windows service start-type, MCP “start with the app”, `openAsHidden` as a Settings/minimized store (Electron 42: unavailable on macOS 13+; Windows does not honor it as this tray path), command-palette rows, REST/MCP ownership.

### Dependencies / readiness / MCP (settings cards)

Adapt Zorivest `SettingsLayout`, `SetupReadinessPanel`, `McpServerStatusPanel` — **not** trading, service-install, or MCP Guard. The Startup card above is the login-item, not a service manager.

| Card | Shows | Actions |
|------|-------|---------|
| Dependencies | yt-dlp + FFmpeg version/path, TTS assets (vocab, spaCy model, voice packs; ready/missing/downloading), eSpeak NG (Detected + version, or Not installed + guidance) from `GET /health/dependencies` | Check Dependencies; Get per missing TTS asset; Copy link (eSpeak NG releases URL) |
| Setup readiness | Backend descriptor present, port > 0, models dir writable, FFmpeg probe result | Deep-link to the failing card |
| MCP / API access | Descriptor present (port shown, not copied), token **masked** (`mcp-token.txt` exists: yes/no). Never display the token. Client and scope selectors and a read-only setup prompt ([07 §MCP setup prompt (residual)](07-distribution.md#mcp-setup-prompt-residual)) | **Copy prompt** → `window.api.getMcpSetupPrompt({ client, scope })`, then `writeClipboardText`. **Advanced** (closed by default) holds **Copy MCP config** → `window.api.copyMcpConfig()` (default omits `AVKIT_API_BASE`) and optional **Pin current endpoint** via `copyMcpConfig({ pinEndpoint: true })` |

### REST Endpoints Consumed

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/v1/settings/{namespace}` | Get namespace settings |
| `PUT` | `/api/v1/settings/{namespace}` | Update namespace settings (leaf keys, including `ffmpeg_path`) |
| `POST` | `/api/v1/downloads/apply-defaults` | Apply quality/audio defaults to pending rows |
| `GET` | `/api/v1/health/dependencies` | Check yt-dlp + FFmpeg status |
| `GET` | `/api/v1/health/console` | Console catch-up (`after_seq`) |

---

## Shared Components (`components/`)

### DataTable

> [!NOTE]
> **Superseded for queue surfaces by docs/build-plan/10-queue-card-ui.md**  
> Queue surfaces render row-cards, not tables — see [Phase 10 QueueCard anatomy](10-queue-card-ui.md#queuecard-anatomy). The block below is retained as the historical spec and still applies to any non-queue table.

TanStack Table wrapper providing consistent table behavior across Downloader and future features:

| Feature | Implementation |
|---|---|
| Sorting | Column header click, multi-column via Shift+click |
| Selection | Single or multi-row selection with highlight |
| Virtual scrolling | `@tanstack/react-virtual` for 1000+ row queues |
| Resizable columns | Drag column header border |
| Status icons | Custom cell renderer with emoji status badges |
| Progress bar | Inline progress bar with percentage text |

### DirectoryPicker

Native Electron directory dialog component:

```typescript
// ui/src/renderer/src/components/DirectoryPicker.tsx

export function DirectoryPicker({ value, onChange, label }: DirectoryPickerProps) {
  const handleBrowse = async () => {
    const result = await window.api.showDirectoryDialog();
    if (result) onChange(result);
  };

  return (
    <div className="directory-picker">
      <label>{label}</label>
      <input type="text" value={value} readOnly />
      <button onClick={handleBrowse}>Browse...</button>
    </div>
  );
}
```

### ProgressBar

Animated progress component:

```typescript
interface ProgressBarProps {
  value: number;    // 0.0 – 1.0
  label?: string;   // e.g. "45.2%" or "Segment 34/50"
  variant?: 'default' | 'success' | 'error';
}
```

### StatusBadge

Colored status indicators used across all feature pages — colors match the Status Summary Bar table in Downloader.

---

## E2E Testing — Incremental Activation Waves

> Playwright Electron E2E test scaffolding at `ui/tests/e2e/`. Tests activate incrementally as GUI pages are built.

### Wave Activation Schedule

| Wave | Gate | Tests Activated | Cumulative | `data-testid` to Add |
|:----:|------|-----------------|:----------:|----------------------|
| 0 | `gui-shell` | `launch.test.ts` (3) | **3** | `nav-downloader`, `nav-transcript`, `nav-tts`, `nav-settings`, `nav-collapse` |
| 1 | `gui-downloader` | `download-queue.test.ts` (6) | **9** | `downloader-page`, `url-input`, `add-btn`, `queue-table`, `queue-row`, `start-btn`, `pause-btn`, `resume-btn`, `cancel-btn`, `sabr-status`, `sabr-check-btn` |
| 2 | `gui-transcript` | `transcript-queue.test.ts` (4) | **13** | `transcript-page`, `channel-input`, `channel-card`, `compile-btn`, `channel-progress` |
| 3 | `gui-tts` | `tts-generate.test.ts` (6) | **19** | `tts-page`, `text-input`, `model-manager`, `voice-grid`, `generate-btn`, `speed-slider`, `cleanup-pipeline`, `preview-cleanup-btn` |
| 4 | `gui-settings` | `settings.test.ts` (4) | **23** | `settings-page`, `download-settings`, `transcript-settings`, `tts-settings`, `console-settings`, `appearance-settings`, `start-at-sign-in-panel` (absent unless packaged), `start-at-sign-in-checkbox`, `start-minimized-checkbox`, `dependencies-section` |
| 5 | `gui-console` | `console-panel.test.ts` (3) | **26** | `console-panel`, `console-filter`, `console-search`, `console-clear`, `console-collapse`, `console-ytdlp-toggle` |
| 6 | `gui-help` | `help-search.spec.ts` (2) | **28** | `help-card`, `help-search` |
| 7 | `gui-palette` | `command-palette-nav.spec.ts` (2) | **30** | `command-palette`, `command-palette-input` |
| 8 | `gui-convert` | `convert-queue.test.ts` (6) | **36** | `nav-convert`, `convert-page`, `convert-dropzone`, `convert-browse`, `convert-add`, `convert-task-compress`, `convert-queue`, `convert-start` — [08](08-video-conversion.md) |
| 9 | `gui-capture` | `capture-inbox.test.ts` | **42** | `nav-capture`, `capture-page`, `capture-region`, `capture-filmstrip`, `capture-viewport`, `capture-tool-arrow`, `capture-save` — [09](09-screenshot-capture.md) |

> [!IMPORTANT]
> **Build before every E2E run.** Wave 0 tests require `npm run build` (alias for `electron-vite build`) to produce `out/main/index.js` and a healthy Python backend (automated by `global-setup.ts`). Playwright launches the compiled bundle, not source files.

### `data-testid` Convention

All test IDs are defined in `ui/tests/e2e/test-ids.ts`. Constants use `SCREAMING_SNAKE_CASE`, values use `kebab-case`.

> [!IMPORTANT]
> When implementing any GUI component, add `data-testid` attributes using the constants from `ui/tests/e2e/test-ids.ts`. The feature is not complete until its wave's E2E tests pass.

### Exit Criterion

All **30** Playwright E2E tests pass after Waves 0–7. Harness must match Zorivest: `pages/AppPage.ts` (splash vs main window), `global-setup.ts` / `global-teardown.ts` (compiled `out/main`, owned backend, log capture). Agent sandbox may still be `[B]` + CI (`E2E-SANDBOX-NODISPLAY`).

---

## GUI Shipping Gate (Mandatory for All GUI Features)

> [!CAUTION]
> **Every GUI feature must include Playwright Electron E2E proof before completion.** A feature coded but not reachable through the app shell/navigation has zero user value.

Before any GUI feature can be marked complete, it must satisfy ALL of the following:

1. **Route/Nav assertion**: A Playwright E2E test opens the real Electron app, navigates to the feature's page through the nav rail, and verifies the feature's root `data-testid` is visible.
2. **`data-testid` registration**: All interactive elements use constants from `ui/tests/e2e/test-ids.ts`.
3. **Happy path E2E**: At least one E2E test exercises the primary happy path.
4. **Build gate**: `cd ui && npm run build && npx playwright test <target>` passes before handoff.
5. **Wave assignment**: The feature's tests are registered in the E2E Wave Activation Schedule above.

---

## API wiring (Phase 4 is authoritative)

Route list, status codes, and wire enums live in [04-rest-api.md](04-rest-api.md). This page must not invent parallel URLs.

| GUI must | Because |
|----------|---------|
| Treat `GET /downloads` and `GET /transcripts` as `{ items, processor }` | Processor Idle/Processing/Paused is session state, not a job status |
| Map quality/audio as GUI strings (`1080p`, `default`) | Domain stores `P1080` / `Default`; the API maps |
| Bind transcript cards to `video_count`, `transcripts_done`, `word_count`, `output_dir`, `last_title` | `video_ids` / `processed_ids` / `progress.json` are not the API |
| Unwrap `{ items }` on `/models/available` and `/models/downloaded` | Variant rows have no durable `is_loaded` |
| Call `POST /downloads/cookies/test` for Test Cookies | Cookie **paths** only |
| `PUT /settings/{namespace}` with leaf keys | Dotted names in the settings table are documentation, not JSON keys |
| Treat 204 as success with no JSON body | `apiFetch<void>` |
| Poll `GET /models/download-runtime` for Get-percent | Not `ModelStatus.download_fraction` |
| Poll `GET /health/console?after_seq=` when the dock is open | Console transport; no SSE |
| Register every action in [gui-actions-index.md](gui-actions-index.md) | Command ids + testids |

---

## Deferred Features (P2)

The following features are explicitly **deferred** to a future phase:

| Feature | Rationale |
|---|---|
| **MCP Guard (lock/unlock)** | Phase 5 MCP server defines auth and toolsets but no guard/lock mechanism. Defer until the MCP server design includes this concept. |
| **OCR text cleaning (Part 1 of cleanup pipeline)** | Only needed for scanned source text. The 10-step TTS normalization pipeline (Part 2) is sufficient for transcript and user-pasted text. |
| **SSE for real-time progress** | MVP uses polling. SSE can be added later for lower latency. |
| **Multi-file TTS batch generation** | Single text → single output for MVP. Batch queue deferred. |
| **Convert timeline / 2-pass / size-target / Downloader handoff** | Specified as Phase 8 named deferrals in [08-video-conversion.md](08-video-conversion.md). Convert **page** itself is in scope for Phase 8. |
| **Capture window/GIF/upload/macOS overlay** | Specified as Phase 9 named deferrals in [09-screenshot-capture.md](09-screenshot-capture.md). Capture **page + tray + F2** are in scope for Phase 9. |

---

## Exit Criteria

- Electron app launches, spawns Python backend with ephemeral Bearer token
- **App shell (nav rail + header + console) renders within 800ms** (skeleton state, before Python healthy)
- **Live data displayed within 3s** from launch (< 3s target per [APPLICATION_PURPOSE.md §6](../../_inspiration/APPLICATION_PURPOSE.md))
- **Lazy modules load on navigation** without full-page spinner
- **Startup performance metrics logged** to Python backend via authenticated API
- Downloader page:
  - URL input → auto-detect type → queue → download → completion flow works end-to-end
  - SABR detection: passive (during download), manual (Check SABR), forced (Force SABR)
  - SABR mode: quality/audio dropdowns dynamically restricted, QualityBlocked status applied
  - Full quality ladder: Best, 2160p, 1440p, 1080p, 720p, 480p, 360p, 240p, 144p, Lowest
  - Full audio format ladder: 9 options including SABR-restricted subset
  - Cookie auth: 9 browsers, profile selection, cookies.txt file, test button
  - Queue controls: Start, Pause, Resume, Cancel, Move Up/Down/Top/Bottom, Reset, Remove, Clear All
  - All 8 per-item statuses rendered with correct colors: Pending, Downloading, Done, Failed, Skipped, QualityBlocked, AgeRestricted, Cancelled
  - Queue processor state indicator: Idle (hidden), Processing, Paused — displayed separately from per-item counts
- Transcript page:
  - Channel add → resolve video IDs → batch download with rate limiting → completion
  - YAML frontmatter on individual transcripts
  - Compiled Markdown with TOC and heading hierarchy
  - Multi-volume splitting at configurable word count
  - Resume across sessions from SQLite `TranscriptItem` aggregates on `GET /transcripts` (optional `progress.json` export on disk is not read)
  - ZIP archive auto-created on channel completion
  - Channel queue: add, remove, reorder, persist across sessions
  - Rate display: requests/hour, delay, batch progress, ETA
- TTS page:
  - Text input (paste, file load) with stats (words, sentences, estimated duration)
  - 10-step text preparation pipeline with per-step toggle checkboxes
  - Kokoro-specific normalization (number spelling, acronym spacing, sentence length)
  - Preview cleaned text before generation
  - Model download → load → generate → output flow works
  - 54 voices across 8 languages with auto lang_code selection
  - Speed control with content-type presets (0.8 technical, 1.0 normal, 1.1 casual)
- Settings page: all settings from all 3 source apps saved and restored across sessions
- Startup card (MEU-61): packaged Windows/macOS offers “Start av-kit when I sign in” (OS Run key, default off); unpackaged and Linux draw nothing; not a Windows service
- Console panel:
  - 5 log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
  - yt-dlp debug toggle (separate from app log level)
  - Module prefix tags, color-coded output, search/filter, log-to-file, copy
- Theme toggle: dark/light switch persists across sessions
- Dependencies: yt-dlp and FFmpeg version check
- Command palette: `Ctrl+K` opens search, all pages reachable
- Window position/size restored on app restart
- All API calls authenticated with Bearer token via `apiFetch()` wrapper

## Outputs

- Electron main process with Python backend lifecycle management + ephemeral Bearer token
- **AppShell component** with left nav rail + content header + console panel + route outlet
- **DownloaderPage** (default route, in main bundle) with SABR indicator, URL input, queue table, full controls
- **TranscriptPage** (lazy) with channel input, channel queue cards, compiled output, resume state
- **TTSPage** (lazy) with text input, cleanup pipeline, model manager, voice selector, generation controls
- **SettingsPage** (lazy) with per-module sections covering all settings from source apps
- **ConsolePanel** (shared) with 5 log levels, yt-dlp debug, search/filter, log-to-file
- React components: `DataTable`, `DirectoryPicker`, `ProgressBar`, `StatusBadge`
- React hooks: `useNotifications()`, `usePersistedState()`
- Shared `apiFetch()` wrapper with Bearer token injection
- TanStack Router hash routing for 4 primary routes
- TanStack Query configuration with queue-specific polling intervals
- Zustand layout store with persist middleware
- Static command registry: `commandRegistry.ts`
- Window state persistence via electron-store
- `globals.css` with Tailwind `@theme` block (Dracula-based dark theme)

<a id="header-toggles-residual"></a>

### Header toggles (residual)

> **MEU-69.** Registered 2026-09-30 from known issue `HEADER-CONSOLE-SETTINGS-BUTTON-STATE`. `Header.tsx` renders `Console` and `Settings: Ctrl+K` as `variant="ghost"` text with no icon, border or pressed state; with the Console panel open the header still shows an idle label, and the palette control is labelled Settings although it opens the command palette.

| Rule | Contract | Source |
|------|----------|--------|
| Console toggle | `header-console-btn` is a toggle button: `aria-pressed={consoleOpen}`, label text constant, pressed state shown by a tinted background plus a terminal icon; Enter/Space toggle; focus stays on the button | Research-backed ([WAI-ARIA APG button](https://w3.org/WAI/ARIA/apg/patterns/button), [SLDS toggle button](https://lightningdesignsystem.com/accessibility/patterns/togglebutton)) |
| Palette control | `header-palette-btn` reads **Commands** with a command/search icon and the `Ctrl+K` hint; `aria-label` updated; opens the same palette | Local Canon [§Command palette](#command-palette-and-action-registry); Human-approved 2026-09-30 (read as buttons) |
| Button affordance | Both controls use the shared `Button` with a visible hover/border treatment from G34 sizes and G32 colors; no new component | Local Canon G32/G34 |
| Pressed variant | Unpressed `outline`; pressed `secondary` with `border border-transparent`, so the toggle's width never changes when the panel opens | Session 31 plan D-11 |
| Accessible names | The Console toggle's name is always "Console" (`aria-pressed` carries the state); the palette control's name is "Commands" with `aria-keyshortcuts="Control+K"` and the title "Open the command palette (Ctrl+K)", so the visible label is in the name (WCAG 2.5.3) | Session 31 plan D-12 |
| Test IDs | `header-console-btn` and `header-palette-btn` keep; Playwright asserts `aria-pressed` flips with the panel and the console E2E wave stays green | Spec |

<a id="path-fields-residual"></a>

### Path fields (residual)

> **MEU-93.** Registered 2026-10-17 from known issue `GUI-CONVERT-OUTPUT-NO-BROWSE`. The Convert **Output folder** is a bare `<input>` (`ConvertPage.tsx:751-758`, `convert-output-dir`) with no folder picker, while Settings edits the same `converter.output_dir` through `components/ui/PathRow.tsx` (input + Browse via `window.api.showDirectoryDialog`). `TTSPage.tsx:643-667` hand-rolls a third variant (read-only input + ghost Browse).

| Rule | Contract | Source |
|------|----------|--------|
| One primitive | Every page field that edits a folder path renders `PathRow` with a Browse button that calls `window.api.showDirectoryDialog()`; a cancelled dialog leaves the value unchanged | Triage D-76; Spec [§DirectoryPicker](#directorypicker) |
| Convert output | Convert **Output folder** becomes `PathRow` (input `convert-output-dir` kept, Browse `convert-output-dir-browse`); typed edits still patch `converter.form.output_dir` | Triage D-76 |
| TTS output | The TTS output path becomes `PathRow readOnly` (`output-path` and `browse-output-btn` kept) | Triage D-76 |
| No API change | `converter.output_dir` and `tts.output_path` stay the existing settings leaves; no REST or IPC change | Local Canon [§Settings Key Convention](#settings-key-convention) |
| Tests | Unit: Browse writes the chosen folder, cancel keeps the value (Convert and TTS); Electron: Convert Browse with a stubbed dialog fills the field; `gui-actions-index.md` gains the `convert-output-dir-browse` row | Local Canon (AC-23.20 audit) |

> **Delivered (Session 40).**
> - `PathRow` gains `placeholder` and `browseDisabled`.
> - Convert **Output folder** is a `PathRow` (`convert-output-dir`, Browse `convert-output-dir-browse`; `gui-actions-index.md` row `convert:browse_output_dir`).
> - TTS output is a `PathRow readOnly` (`output-path`, `browse-output-btn`).
> - Settings capture **Backup folder** (`settings-capture-backup`) uses the same primitive.
> - AC-93.1 to AC-93.8. Gate runs 1–4 stand as the gate on Mat's ruling, 2026-10-26 (D-120); the Codex execution review is in `.agent/context/handoffs/2026-10-24-gui-theme-path-fields-implementation-critical-review.md`.
> - Plan `docs/execution/plans/2026-10-24-gui-theme-path-fields/`.

<a id="theme-reactive-selects-residual"></a>

### Theme-reactive selects (residual)

> **MEU-94.** Registered 2026-10-17 from known issue `GUI-LIGHT-THEME-SELECT-STALE-DARK`. `getG30Styles()` (`SelectInput.tsx:19`) reads `html.dark` once at render into an inline style. `index.html` boots with `class="dark"` and `lib/theme.ts` applies the persisted `ui.theme` only after an async `GET /settings/ui`, and `THEME_CHANGED_EVENT` re-renders `AppShell` only (route pages arrive as `children`), so selects keep dark colours in Light. Measured 2026-10-17: all 8 Settings selects stay `rgb(26,26,46)` after switching to Light; TTS selects are dark on a light cold boot.

| Rule | Contract | Source |
|------|----------|--------|
| Reactive styles | One hook (`useDocumentTheme`, subscribing to `THEME_CHANGED_EVENT`) backs `useG30Styles()`/`SelectInput`, so every G30 consumer re-renders with the current theme; no consumer reads the DOM class at render time | Triage D-77; Local Canon emerging-standards G30 |
| One copy | `ConsolePanel.tsx`'s duplicate of `getG30Styles` is removed in favour of the shared primitive | Triage D-77 |
| Option menu | The native option-menu pair follows the theme (light pair in Light, dark pair in Dark) instead of the fixed light pair | Triage D-77 |
| First paint | The persisted theme is applied before the first route renders, so a cold boot in Light never paints a dark select | Triage D-77; Spec §Progressive Loading Strategy |
| Tests | Electron, both themes: after a live toggle and after a cold boot with the theme persisted, every visible `select` on Settings, TTS and Convert computes the theme's background/foreground (G30 checklist item 6) | Triage D-77; Local Canon G30 |

> **Delivered (Session 40).**
> - `useDocumentTheme` (`lib/theme.ts`, through `useSyncExternalStore`) backs `g30StylesFor`/`useG30Styles()`. `getG30Styles` and the fixed `NATIVE_OPTION_MENU_STYLE` are removed, and `ConsolePanel` uses the shared hook.
> - `boot-theme.ts`, the first import of `main.tsx`, applies the persisted `av-kit.ui.theme` before the first render.
> - The boot `GET /settings/ui` (`useSyncDocumentTheme`) retries a 503 (250/500/1000 ms, then every 2 s within 60 s).
> - `AppShell` holds routes behind `RouteThemePending` ("Connecting...", then "Still loading…" after 3 s) until the theme settles.
> - AC-94.1 to AC-94.11. Gate runs 1–4 stand as the gate on Mat's ruling, 2026-10-26 (D-120); the Codex execution review is in `.agent/context/handoffs/2026-10-24-gui-theme-path-fields-implementation-critical-review.md`.
> - Plan `docs/execution/plans/2026-10-24-gui-theme-path-fields/`.

<a id="shortcut-binding-residual"></a>

### Shortcut binding (residual)

> **MEU-95.** Registered 2026-10-17 from known issue `GUI-SHORTCUTS-ADVERTISED-UNBOUND`. `registry/commandRegistry.ts` and `NavRail.tsx` label Ctrl+1/2/3, Ctrl+, and Ctrl+B, and [§Command palette](#command-palette-and-action-registry) specifies them, but `AppShell.tsx:49-76` binds only Ctrl+K, Ctrl+4 and Ctrl+5.

| Rule | Contract | Source |
|------|----------|--------|
| Registry-driven | The AppShell keydown map is built from each registry entry's `shortcut` field; a shortcut shown in the palette, rail or a tooltip is always bound, and AppShell binds no chord outside the registry (Ctrl+K stays the palette opener). Bindings AppShell does not dispatch stay where they are: Capture's Electron-main `globalShortcut` (F2) and its page/editor-scoped zoom keys are out of scope, and remain collision constraints under D-89 | Triage D-78; Human-approved (triage D-89, Mat 2026-10-17) |
| Advertised set | Ctrl+1..5 navigate, Ctrl+, opens Settings, Ctrl+B collapses the rail, as already labelled | Spec [§Command palette](#command-palette-and-action-registry) |
| Text fields | Ctrl chords fire from any focus, as Ctrl+K already does (`AppShell.tsx:50`); no registry chord takes a field's own editing keys (Ctrl+A/C/V/X/Z, plain Enter) | Local Canon (`AppShell.tsx:50`) |
| Tests | Unit: every registry entry with a `shortcut` dispatches its action through the keydown map, and no two entries share a chord; Electron: each nav chord reaches its route | Triage D-78 |

> **Delivered (Session 41).**
> - `registry/shortcuts.ts` builds the AppShell keydown map from each registry entry's `shortcut` (`buildShortcutMap`, `createShortcutHandler`). AppShell's one handler replaces the hard-coded navigation and Ctrl+B branches. Ctrl+K stays the palette opener.
> - `RESERVED_CHORDS` keeps field editing keys, Capture's zoom keys and F2 out of the registry. NavRail hints come from `ariaKeyshortcuts`.
> - AC-95.1 to AC-95.8.
> - Gate: `session-gate.ps1` run 4, all steps exit 0 (walkthrough §Gate).
> - Plan `docs/execution/plans/2026-10-26-gui-keyboard-palette/`.

> **Delivered (Session 43).**
> - Capture handles Ctrl+Z, Ctrl+Y and Ctrl+Shift+Z itself while its image has focus ([09](09-screenshot-capture.md#canvas-history-chords) §Canvas history chords; D-163). They stay in `RESERVED_CHORDS`, whose comment now says so, so no registry entry takes them.
> - AC-99.1 to AC-99.7.
> - Gate: `session-gate.ps1`, all steps exit 0 (walkthrough §Gate).
> - Plan `docs/execution/plans/2026-10-29-capture-editor-repair/`.

<a id="command-palette-curation-residual"></a>

### Command palette curation (residual)

> **MEU-96.** Registered 2026-10-17 from known issue `GUI-COMMAND-PALETTE-CURATION`. The palette lists 40 commands in 8 groups regardless of page or state (`listCommands` memoised once in `CommandPalette.tsx:43`), has no Appearance command, and runs destructive commands without the page's confirmation (`download:clear` → `DELETE /downloads`, `download-commands.ts:178,232`).

| Rule | Contract | Source |
|------|----------|--------|
| Context-aware | Global commands always (navigation, Appearance, console, rail, help, Settings); the current page's commands listed first; commands that cannot run now hidden; Pause/Resume one state-aware entry; the list recomputes when the page or state changes | Human-approved (triage D-87, Mat 2026-10-17) |
| Appearance | Two commands, **Appearance: Dark** (Ctrl+Shift+D) and **Appearance: Light** (Ctrl+Shift+L), each setting `ui.theme` through the same path as the Settings buttons | Human-approved (triage D-88, Mat 2026-10-17) |
| Destructive | Clear and Cancel commands open the same `ConfirmModal` the page toolbar uses; nothing is deleted without it | Triage D-79 |
| Labels | Internal labels are renamed to user words (for example "Check SABR", "Preview TTS cleanup", "Focus download URL"); the rail toggle reads as a toggle; the Generate TTS command never posts a hard-coded voice | Triage D-87 |
| Index | `gui-actions-index.md` Palette column and the [§Command palette](#command-palette-and-action-registry) "Palette shows only `Palette = yes` rows" rule are amended to the context-aware model; the AC-23.20 audit stays bidirectional | Spec amendment under D-87 |
| Tests | Unit: palette contents per page and per queue state; Appearance commands set the theme; Electron: palette Clear opens the confirm and Cancel keeps the queue | Triage D-79, D-87, D-88 |

> **Delivered (Session 41).**
> - `registry/command-state.ts`: pages publish the enabled state of their controls, and the palette (`paletteCommands`) lists the context-aware set. It shows global commands, then the current page's, hides those that cannot run now, and re-reads on route and state changes.
> - **Appearance: Dark** (Ctrl+Shift+D) and **Appearance: Light** (Ctrl+Shift+L) set `ui.theme` through `registry/appearance.ts`, the Settings PUT path.
> - Palette Clear and Cancel open the page's `ConfirmModal`. Labels use user words.
> - `gui-actions-index.md` gains the Appearance rows and the Settings copy rows (`GUI-AUDIT-CLIPBOARD-RESOLVER`).
> - AC-96.1 to AC-96.13.
> - Gate: `session-gate.ps1` run 4, all steps exit 0 (walkthrough §Gate).
> - Plan `docs/execution/plans/2026-10-26-gui-keyboard-palette/`.

<a id="common-shortcuts-residual"></a>

### Common shortcuts (residual)

> **MEU-97.** Registered 2026-10-17 from known issue `GUI-KEYBOARD-SHORTCUTS-COMMON`. Only navigation carries shortcuts; page primary actions, focus-URL, console, help and theme have none, and only Ctrl+K has a visible hint.

| Rule | Contract | Source |
|------|----------|--------|
| Core set | Ctrl+L focus URL (Downloader, Transcript); Ctrl+Enter page primary action; Ctrl+O Browse files (Convert); Ctrl+S save capture (Capture); Ctrl+J console; F1 help; plus MEU-96's Ctrl+Shift+D/L | Human-approved (triage D-89, Mat 2026-10-17) |
| Page scope | Page chords are registered per page and inert elsewhere; all are registry entries bound by MEU-95's map | Triage D-89; Local Canon [§Shortcut binding](#shortcut-binding-residual) |
| No collisions | No chord collides with Capture's Ctrl+=/-/0 zoom keys, the F2 capture hotkey or another registry entry | Human-approved (triage D-89) |
| Hints | Each bound control shows its chord in its tooltip and carries `aria-keyshortcuts` | Triage D-89; Research-backed ([WAI-ARIA `aria-keyshortcuts`](https://www.w3.org/TR/wai-aria-1.2/#aria-keyshortcuts)) |
| Tests | Unit: chord table has no duplicates or reserved chords; Electron: each chord runs its action on its page and does nothing on another | Triage D-89 |

> **Delivered (Session 41).**
> - Chords: Ctrl+L focus URL (Downloader, Transcript), Ctrl+Enter page primary (`page:primary`, `PAGE_PRIMARY_CONTROL`), Ctrl+O Browse (Convert), Ctrl+S Save (Capture, pressing `capture-save`), Ctrl+J console, F1 help.
> - Each control in `BOUND_CONTROLS` shows its chord in its hint and carries `aria-keyshortcuts`. A modified Enter passes through the open palette.
> - A registry chord bubbles out of Capture's focused draw surface to the shell.
> - The index Trigger cells name the chords. AC-97.1 to AC-97.11.
> - Gate: `session-gate.ps1` run 4, all steps exit 0 (walkthrough §Gate).
> - Plan `docs/execution/plans/2026-10-26-gui-keyboard-palette/`.

<a id="ready-probe-residual"></a>

### Ready probe (residual)

> **MEU-108.** Registered 2026-11-03 from known issue `GUI-READY-PROBE-BLOCKS-MAIN`. The main process's output handler runs `queryLiveProcess` for every chunk of backend output before it looks at the text, and on Windows that call runs PowerShell synchronously, so ordinary logging can stall the window.

| Rule | Contract | Source |
|------|----------|--------|
| Guard | `READY_GUARD`: `live-identity`'s process query runs only for an output chunk that carries a usable `AVKIT_READY` line. Every other chunk does no process query and publishes nothing. | Known issue |
| Unusable READY | `AVKIT_READY port=0` does no process query and publishes nothing. | Existing `port=0` rule in `python-manager.ts` |
| Usable READY | One process query, then the same publish as `confirmReadyAndPublish`: same `apiBase`, same token. The ownership checks don't change. | [07 §PythonManager](07-distribution.md) step 3 |
| One test of READY | The guard and the publisher read one shared regex, so they can't disagree. | This section |
| Log after the window | `LOG_AFTER_WINDOW`: backend output can arrive after the window is destroyed or its renderer is torn down. `forwardConsoleLines` sends nothing then and throws nothing, because an uncaught throw stops the main process behind an error dialog. The line stays in the in-memory log either way. | Mat's report, Session 44 |
| Shape | New exported `publishIfReady` in `ui/src/main/python-manager.ts` takes the chunk text and an injected `queryLive`. The output handler in `ui/src/main/index.ts` calls only that and keeps its published log note. | This section |

> **Delivered (Session 44).**
> - `publishIfReady` in `ui/src/main/python-manager.ts` runs the process query only for a chunk carrying a usable `AVKIT_READY` line. The guard and the publisher read one shared regex, and `index.ts` calls it for every chunk.
> - The backend descriptor read sits behind the same guard, so an ordinary chunk touches neither.
> - `ui/tests/unit/ready-probe-guard.test.ts`, AC-108.1 to AC-108.6.
> - `forwardConsoleLines` in `ui/src/main/python-manager.ts` is the output handler's only route to the window. `ui/tests/e2e/backend-output-after-close.test.ts`, AC-108.7, runs the real handler in real Electron with the window destroyed.
> - Gate: the shared `session-gate.ps1` record in the MEU-108 handoff.
> - Plan `docs/execution/plans/2026-11-03-release-rc1/`.

## Validation Commands

```bash
npx tsc --noEmit
npx vitest run
npx eslint src/ --max-warnings 0
npx playwright test
```
