---
date: "2026-08-27"
project: "p9-capture-api-mcp"
meu: "MEU-38"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-27-p9-capture-api-mcp/implementation-plan.md"
build_plan_section: "docs/build-plan/09-screenshot-capture.md §MCP"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-27-p9-capture-api-mcp-MEU-37-handoff.md"
---

# Handoff: 2026-08-27-p9-capture-api-mcp-MEU-38-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-38 — compound tool `avkit_capture` at `mcp-server/src/toolsets/capture.ts`, ACTION_INDEX 67, catalog `{ items }` (no processor), binary ImageContent, `DESTRUCTIVE_CAPTURE` = `avkit_capture.remove`, settings `capture` namespace, M4 dist. REST-only: register / complete / cancel. No Capture GUI. Session 8c stays pending.
**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §MCP
**Predecessor**: MEU-37 capture REST

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-38.1 | unit | ACTION_INDEX length 67; COMPOUND_TOOLS_AFTER; KEEP 59 rows without capture | M2; Spec MCP | `capture.test.ts` AC-38.1 | ✅ |
| AC-38.2 | unit | CAPTURE_ACTIONS 1:1 REST; no complete/cancel/register; no `/grab` | Spec 442–451 | `capture.test.ts` AC-38.2 | ✅ |
| AC-38.3 | unit | capture schema `.strict()`; extra key fails `safeParse` before fetch | M1; Local Canon | `capture.test.ts` AC-38.3 | ✅ |
| AC-38.4 | unit | `avkit_capture.remove` destructive; NON_DESTRUCTIVE_CAPTURE not in set | Spec 436; 05 88–95 | `capture.test.ts` AC-38.4 | ✅ |
| AC-38.5 | unit | M7 markers; Capture is local screen + local files; `capture_interactive` needs desktop app | M7; Spec 455 | `capture.test.ts` AC-38.5 | ✅ |
| AC-38.6 | unit | SETTINGS_SCHEMA capture keys/defaults; enum includes `capture` | G29; Spec 417 | `capture.test.ts` AC-38.6 | ✅ |
| AC-38.7 | integration | capture list/list_requests `{ items }` reject `processor` (`invalid_catalog_envelope`); convert list still `{ items, processor }`; sanitize drops `image_bytes` | M2; Spec 390; G25 | `capture.test.ts` AC-38.7 | ✅ |
| AC-38.8 | integration | `capture` uses ADD_TIMEOUT_MS; dist/capture.js after M4 | M4; Local Canon | `capture.test.ts` AC-38.8 | ✅ |
| AC-38.9 | unit | tool at `src/toolsets/capture.ts`; no `src/compound/` | Local Canon p5 | `capture.test.ts` AC-38.9 | ✅ |
| AC-38.10 | unit | missing confirm on remove → `validation_error`; fetch 0 | M3; Local Canon | `capture.test.ts` AC-38.10 | ✅ |
| AC-38.11 | integration | image content `type`/`data`/`mimeType`; oversize TOOL_ERROR not image | Spec 438; MCP 2025-06-18 | `capture.test.ts` AC-38.11 | ✅ |
| AC-38.12 | integration | GET `variant` and `status` appended as query | Spec 392, 397 | `capture.test.ts` AC-38.12 | ✅ |
| AC-38.13 | integration | fullscreen/region `httpBody` forwards REST fields; extra `.strict()` fail; list keys include SHOT_OUT | Spec 447; M2 | `capture.test.ts` AC-38.13 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-38.1–AC-38.13 | `PASS: RED_ORACLE ui MEU-38 AC-38 count=13` | 13 capture tests inside 214 passed | `C:/Temp/av-kit/fail-to-pass-meu-38.txt`; `C:/Temp/av-kit/mcp-meu-38-green.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `assert-red-oracle.ps1 -Kind ui -Meu 38` | 0 | `PASS: RED_ORACLE ui MEU-38 AC-38 count=13` |
| `npx tsc --noEmit` + `npx vitest run` + `npm run build` | 0 | 214 passed (`C:/Temp/av-kit/mcp-meu-38-green.txt`) |

### Quality Gate Results

```
vitest: 214 passed (C:/Temp/av-kit/mcp-meu-38-green.txt)
tsc --noEmit: pass
npm run build: pass
RED_ORACLE ui MEU-38: PASS (count=13)
ACTION_INDEX_AFTER: 67
COMPOUND_TOOLS includes avkit_capture
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `mcp-server/src/toolsets/capture.ts` | new | schema | Zod union; no register mode; M7 descriptions; IMAGE_MAX_BYTES |
| `mcp-server/src/toolsets/registry.ts` | modified | index | ACTION_INDEX 67; catalog vs queue envelopes; image branch; GET query; ADD_TIMEOUT_MS on capture |
| `mcp-server/src/client.ts` | modified | binary | `apiBinary` for image/* GET |
| `mcp-server/src/toolsets/settings.ts` | modified | ns | `capture` namespace + CAPTURE_KEYS leaves |
| `mcp-server/src/destructive.ts` | modified | set | `avkit_capture.remove` |
| `mcp-server/src/index.ts` | modified | instructions | local screen; capture_interactive needs desktop app |
| `mcp-server/tests/capture.test.ts` | new | AC-38.* | Red/Green contract |
| `mcp-server/tests/fixtures.ts` | modified | census | CAPTURE_ACTION_INDEX; minimalInput; DESTRUCTIVE_KEYS |
| `mcp-server/tests/action-index.test.ts` | modified | 67 | capture rows; catalog/image fetch stubs |
| `mcp-server/tests/convert.test.ts` | modified | census | ACTION_INDEX 67 + avkit_capture |
| `mcp-server/tests/m7-resource.test.ts` | modified | 67 | description census |
| `mcp-server/tests/strict-confirm.test.ts` | modified | census | CAPTURE_ACTION_INDEX extra-key rows |
| `mcp-server/dist/toolsets/capture.js` | generated | M4 | live IDE surface |

```diff
 if (tool === "avkit_capture" && (action === "list" || action === "list_requests")) {
   if (!isCatalogEnvelope(result.data)) {
     return toToolError({ code: "invalid_catalog_envelope", ... });
   }
 }
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/execution-critical-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | pending independent review | — | — | open |

### Verdict

`pending` — implementer does not author the verdict

## Corrections Applied (2026-08-27)

**Findings resolved**: Green-phase (not reviewer)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| 1 | AC-38.8 dist missing during first vitest-before-build | `npm run build` then re-run official Green chain | 214 passed; dist/capture.js exists |

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| Capture GUI / tray / F2 overlay | out-of-scope | MEU-39 | grouping Session 18 |
| MCP complete/cancel/register | out-of-scope | — | Spec omits; overlay uses REST |
| Session 8c / MEU-27 | human-gated | MEU-27 | stays ⬜ pending |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-27 | cursor-grok | MEU-38 Red→Green + M4 build + handoff |
| H1 refresh | 2026-08-27 | cursor-grok | H1-2 214 vitest; SSOT ready_for_review |
| Exec r1 corrections | 2026-08-27 | cursor-grok | F1 ImageContent magic sniff; 214 vitest |
