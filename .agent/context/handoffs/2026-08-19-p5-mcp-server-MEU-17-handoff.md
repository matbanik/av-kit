---
date: "2026-08-19"
project: "p5-mcp-server"
meu: "MEU-17"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-19-p5-mcp-server/implementation-plan.md"
build_plan_section: "bp05s1"
agent: "cursor-grok-4.6"
reviewer: "pending-codex"
predecessor: "2026-08-19-p4-rest-api-MEU-16-handoff.md"
---

# Handoff: 2026-08-19-p5-mcp-server-MEU-17-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-17 — MCP runtime: `mcp-server/` scaffold, `DISCOVERY_ORDER`, `STALE_PIN`, `TOKEN_SOURCES`, `TOOL_ERROR` client, stdio `TRANSPORT` + `SERVER_INSTRUCTIONS`. No compound tools yet.
**Build Plan Section**: `docs/build-plan/05-mcp-server.md` Runtime / Client
**Predecessor**: MEU-16 REST closeout

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-17.1 | unit | **Control `DISCOVERY_ORDER`.** Observable: returned `api_base` string or `TOOL_ERROR.code`. Chain: `resolveApiBase` → env → descriptor → fail. Negative: unset env + missing descriptor → `app_not_running`; never `http://127.0.0.1:0` or a hard-coded port. | Spec Runtime | `tests/config.test.ts` `DISCOVERY_ORDER` | ✅ |
| AC-17.2 | unit | **Control `STALE_PIN`.** Observable: `TOOL_ERROR.code === stale_pin` and mock `fetch` call count `0`. Chain: `resolveApiBase` compares pin host+port to descriptor. Negative: pin `http://127.0.0.1:9/api/v1` vs descriptor port `51234` still fetches. Pin without descriptor is allowed (dev uvicorn). | Local Canon 07 236 | `tests/config.test.ts` `STALE_PIN` | ✅ |
| AC-17.3 | unit | **Control `TOKEN_SOURCES` / `MCP_TOKEN_SOURCE`.** Observable: Authorization header value on an authenticated `api()` call. Chain: `resolveToken` → `client.api` header. Negative: GUI nonce string used when `mcp-token.txt` and env differ; token substring appears in `TOOL_ERROR` text or logs. Blank env falls through to file. | Spec Auth | `tests/config.test.ts` `TOKEN_SOURCES`; `tests/client.test.ts` Bearer header | ✅ |
| AC-17.4 | unit | `AVKIT_APP_DATA` overrides `DEFAULT_APP_DATA` for both descriptor and token paths. | Spec Runtime | `tests/config.test.ts` `APP_DATA_OVERRIDE` | ✅ |
| AC-17.5 | unit | `AVKIT_API_BASE` without `/api/v1` → `invalid_api_base`; no fetch. | Spec Discovery (1) | `tests/config.test.ts` `invalid pin suffix` | ✅ |
| AC-17.6 | integration | **Control `TOOL_ERROR` / `FETCH_FAILED`.** Observable: handler-shaped result `isError===true` and text includes `fetch_failed` or HTTP `503` / envelope `code`. Chain: mocked `fetch` reject or 503 → `client.api`. Negative: uncaught hang (AbortSignal never set) or public `{ok:false}` object as the tool result. | Spec Client; Research-backed MCP errors | `tests/client.test.ts` `TOOL_ERROR / FETCH_FAILED` | ✅ |
| AC-17.7 | unit | Authenticated call without token → `token_missing` and fetch count `0`. `AUTH_EXEMPT_ACTIONS` (liveness helper) may call `GET /health` with no Bearer once `api_base` is known. | Spec Auth; p4 exempt path | `tests/client.test.ts` `token gate` | ✅ |
| AC-17.8 | unit | **Control hexagonal.** Observable: `SCAN_MCP_LIBS_ARGS` receipt empty. Chain: package source only. Negative: any `MEU17_TOUCHED` src import of sqlite/yt-dlp/`avkit_core`. | Spec Thin wrapper | `tests/runtime.test.ts` `hexagonal` | ✅ |
| AC-17.9 | unit | Stdio server constructs with `TRANSPORT` and `SERVER_INSTRUCTIONS` text present (tools may be empty until MEU-18). | Spec index.ts | `tests/runtime.test.ts` `TRANSPORT / SERVER_INSTRUCTIONS` | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| `DISCOVERY_ORDER` app_not_running | `expected true to be false` — stub `resolveApiBase` always returned `{ ok: true, apiBase: "http://127.0.0.1:0/api/v1" }` (M5 guessed-port, not vitest crash) | passed | `mcp-server/src/config.ts:68`; `mcp-server/tests/config.test.ts:22` |
| `DISCOVERY_ORDER` descriptor / pin | `expected { ok: true, … }` deep-equal fail (stub ignored env + `backend.json`) | passed | `mcp-server/src/config.ts:74-104`; `mcp-server/tests/config.test.ts:32` |
| `STALE_PIN` | `expected true to be false` (stub never returned `stale_pin`) | passed | `mcp-server/src/config.ts:90-98`; `mcp-server/tests/config.test.ts:58` |
| `invalid pin suffix` | `expected true to be false` (stub accepted pin without `/api/v1`) | passed | `mcp-server/src/config.ts:75-82`; `mcp-server/tests/config.test.ts:125` |
| liveness no Bearer | `expected false to be true` (`result.ok`) — stub pin/path blocked `/health` | passed | `mcp-server/src/client.ts:63-81`; `mcp-server/tests/client.test.ts:106` |

Receipts: `C:/Temp/av-kit/fail-to-pass-meu-17.txt` (6 failed / 11 passed of 17). Green: `C:/Temp/av-kit/pytest-mcp-17.txt` (17 passed; `tsc --noEmit` + `npm run build` exit 0). Scaffold: `C:/Temp/av-kit/mcp-scaffold.txt`. Source-read: `C:/Temp/av-kit/handoff-source-read.txt` (`TEMPLATE=`, `PEER=`, `PASS: HANDOFF_SOURCE_READ`) written before this file.

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| Row 1 `mcp-scaffold` (`npm install` + dep pins) | 0 | `PASS: mcp-server scaffold` |
| Row 2 `fail-to-pass-meu-17.txt` | 1 | 6 failed / 11 passed — guessed-port stub, not config crash |
| Row 3 `pytest-mcp-17.txt` | 0 | 17 passed; tsc + build |
| Row 4 `MEU_SCOPED_GATE` (this handoff) | 0 | `PASS: MEU-17 MEU_SCOPED_GATE` |

### Quality Gate Results

```
tsc --noEmit: 0 errors
vitest MEU-17: 17 passed
npm run build: exit 0
anti-placeholder / SCAN_MCP_LIBS / G36: 0 matches (`C:/Temp/av-kit/handoff-meu-17.txt`)
MEU_SCOPED_GATE: PASS
```

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `mcp-server/package.json` | new | `MCP_SDK` `^1.30.0`, `ZOD_PIN` `^3.25.0`, vitest, tsc, tsx |
| `mcp-server/tsconfig.json` | new | Node16 ESM, `outDir: dist` |
| `mcp-server/vitest.config.ts` | new | `tests/**/*.test.ts` |
| `mcp-server/src/config.ts` | new | `DISCOVERY_ORDER`, `STALE_PIN`, `TOKEN_SOURCES`, `DEFAULT_APP_DATA` |
| `mcp-server/src/client.ts` | new | `api()`, `toToolError()`, timeouts, `/health` auth-exempt |
| `mcp-server/src/index.ts` | new | `StdioServerTransport` + `SERVER_INSTRUCTIONS`; no compound tools |
| `mcp-server/tests/config.test.ts` | new | AC-17.1–17.5 |
| `mcp-server/tests/client.test.ts` | new | AC-17.6–17.7 |
| `mcp-server/tests/runtime.test.ts` | new | AC-17.8–17.9 |

```diff
+  if (pin) {
+    if (!pin.includes("/api/v1")) {
+      return { ok: false, error: { code: "invalid_api_base", message: "..." } };
+    }
+    // STALE_PIN vs live backend.json host+port; pin without descriptor allowed
+  }
```

```diff
+  const exempt = AUTH_EXEMPT_PATHS.has(path);
+  if (!exempt) {
+    const tok = resolveToken(env);
+    if (!tok.ok) {
+      return { ok: false, error: tok.error };
+    }
+  }
+  signal: AbortSignal.timeout(timeoutMs),
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | — | — | — | — | — |

### Verdict

`pending` — implementor does not author `approved`.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-19 | cursor-grok-4.6 | Initial MEU-17 handoff |
| Submitted for review | 2026-08-19 | cursor-grok-4.6 | Awaits project H1-7 Codex |
