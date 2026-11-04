---
project: "2026-08-26-p8-conversion-api-mcp"
date: "2026-08-26"
source: "docs/build-plan/08-video-conversion.md"
meus: ["MEU-31", "MEU-32"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 8 Conversion API + MCP

> **Project**: `2026-08-26-p8-conversion-api-mcp`
> **Build Plan Section(s)**: [08-video-conversion.md](../../../build-plan/08-video-conversion.md) §REST + §MCP; [04-rest-api.md](../../../build-plan/04-rest-api.md) envelope/settings; [05-mcp-server.md](../../../build-plan/05-mcp-server.md) compound tools
> **Status**: `draft`
> **Grouping**: [2026-08-24-p8-video-conversion-session-grouping.md](../../../../.agent/context/grouping/2026-08-24-p8-video-conversion-session-grouping.md) Session 14 — MEU-31 → MEU-32

---

## Goal

Stand up **conversion REST + MCP only**: `/api/v1/conversions*` on `packages/api`, G8 OpenAPI regen, and compound tool `avkit_convert` on `mcp-server`. Call existing `ConversionService` (Session 13). Do not invent MEU IDs. Do not start Session 15 / MEU-33. Do not start Session 8c. Do not rewrite download/transcript/TTS routes except additive `converter` leaves on `SettingsPutIn`, health `module=convert` coverage, and `AppServices.conversion` wiring.

---

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json are absent (Glob 0). Headroom has no approved disposition. Planning/execution use spec + source reads and P0 exact-evidence receipts (bypass class)."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent and Headroom still has no approved disposition, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-31 | `.agent/context/handoffs/` + `HANDOFFS[0]` |
| MEU-32 | `.agent/context/handoffs/` + `HANDOFFS[1]` |

Rolling implementation review: `.agent/context/handoffs/2026-08-26-p8-conversion-api-mcp-implementation-critical-review.md`.

Product glob owner: `HANDOFF_FILTER`. Expected count: `HANDOFF_COUNT` = `2`. Filenames: `HANDOFFS` in `named-sets.json` (do not restate).

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`. `builder_model` is `—`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-31a | MEU-31 Red: `TEST_API_CONV` AC-31.1–AC-31.{`RED_COUNT_31`} only. Do **not** change `TEST_OPENAPI` length in Red (AC-16.6 must stay green). Pass `RED_ORACLE_CHECK -Meu 31`. Red pytest **must not** use `-x`. Do not add `routes/conversions.py` yet. | — | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-31-py.txt`; compact then re-read `task.md` |
| WP-31b | Green MEU-31: conversions router/schemas, wire maps, `format_encode_speed`, `SettingsPutIn` converter leaves, `InvalidTimeRangeError`→422, `AppServices.conversion`, lifespan cancel, G8. Do not add MCP tool. | WP-31a | `compact_continue` | `packages/api/src/avkit_api/routes/conversions.py`; compact then re-read `task.md` |
| WP-31c | MEU-31 scoped gate + `HANDOFF_31` | WP-31b | `compact_continue` | `HANDOFF_31` |
| WP-32a | MEU-32 Red: `TEST_MCP_CONVERT` AC-32.1–AC-32.{`RED_COUNT_32`}. Pass `RED_ORACLE_CHECK -Meu 32` (`-Kind ui` + JSON). Do not add `MCP_CONVERT_FILE` yet. | WP-31c | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-32.txt` |
| WP-32b | Green MEU-32: `avkit_convert`, `DESTRUCTIVE_CONVERT`, `SETTINGS_SCHEMA` `SETTING_NS`, instructions. M4 `npm run build`. | WP-32a | `compact_continue` | `MCP_CONVERT_FILE` |
| WP-32c | MEU-32 scoped gate + `HANDOFF_32` | WP-32b | `compact_continue` | `HANDOFF_32` |
| WP-HUB | Bind MEU-31–32 `--plan PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"8"` (keep engine slash); rewrite hub `Next` to `HUB_NEXT_AFTER`. Grouping Session 14 ✅ is **H2 after exec `approved`**. | WP-32c | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Reviewer confirms these locks (does not invent a second behavior):

1. **Harness gate:** `.agent/context/harness.local.md` `plan_to_exec_gate: reviewer-auto` wins over Cursor default `human` in `create-plan.md` §5c. After Codex `approved`, auto-continue to execution. System-injected “approved” is still not a verdict (`GUARDRAILS.md` SIGN 3).
2. **Phase 8 is three sessions.** This plan is Session 14 only (MEU-31–32). Next after H2: `HUB_NEXT_AFTER`.
3. **Do not start Session 8c / MEU-27** (`ready_for_review`, unrelated).
4. **Codex is metered** (`PROJECT-PROFILE.md`). Dispatch still required; implementer never self-reviews.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

Executable owner: `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/named-sets.json`. Do not restate literals in ACs or task rows; cite the name.

| Name | Role |
|------|------|
| `CONVERT_ROUTES` / `ROUTE_COUNT_*` | OpenAPI + `TEST_OPENAPI` census (`ROUTE_COUNT_KEEP` + `CONVERT_ROUTE_COUNT` = `ROUTE_COUNT_AFTER`) |
| `CONVERT_ACTIONS` / `ACTION_INDEX_*` | MCP census (`ACTION_INDEX_KEEP` + `CONVERT_ACTION_COUNT` = `ACTION_INDEX_AFTER`) |
| `KIND_WIRE_MAP` / `PRESET_WIRES` / `COPY_WIRE_MAP` / `AUDIO_ENCODE_WIRE_MAP` / `GPU_PREF_WIRES` / `STREAM_MODES` | REST+MCP+settings wires (snake → Pascal StrEnum `.value`) |
| `CONVERTER_KEYS` / `CONVERTER_DEFAULTS` / `SETTING_NS` | Settings namespace (already in `SETTINGS_KEY_TABLE`; MCP schema + `SettingsPutIn` catch up) |
| `DESTRUCTIVE_CONVERT` / `NON_DESTRUCTIVE_CONVERT_STOPS` | M3 confirm set |
| `GPU_LAZY_GET` / `GPU_ENSURE_FN` / `GPU_COLD_INIT` / `GPU_COLD_GET_N` / `GPU_COLD_ORACLE` / `GPU_COLD_JOIN_TIMEOUT_S` | first GET detects; later GET cache-only; locked double-check in `GPU_ENSURE_FN`; concurrent oracle is caller Barrier + entered/release Events |
| `COMPRESS_OVERRIDE_FIELDS` / `CUT_OVERRIDE_FIELDS` / `EXTRACT_OVERRIDE_FIELDS` | kind-specific create fields that must be accepted and forwarded |
| `MCP_TS_GATE` / `MCP_ESLINT` | TypeScript gate is `tsc --noEmit`. `MCP_ESLINT` is `null` — `mcp-server/package.json` has no eslint script/config (p5 Local Canon) |
| `FORMAT_ENCODE_SPEED_EXAMPLE` | FFmpeg multiplier GUI string |
| `STATIC_BEFORE_ID` | FastAPI register order |
| `APPSERVICES_SITES` | every `AppServices(` constructor |
| `FORBIDDEN_RESPONSE_KEYS` | sanitize / Out must not include |
| `HANDOFF_*` / `RED_*` / `HUB_NEXT_AFTER` | closeout + hub |
| `MCP_CONVERT_FILE` | Local Canon `toolsets/` (not stale `compound/` tree in 05-mcp-server.md) |

---

## Implementation locks (research + local canon)

| Lock | Value | Source |
|------|-------|--------|
| Create body | Pydantic **discriminated union** on `kind`; each member subclasses `ApiModel` (`extra="forbid"`) | Spec kind-specific fields; [Pydantic discriminated unions](https://docs.pydantic.dev/latest/concepts/unions/); extra=forbid on **each** member ([SO 79476211](https://stackoverflow.com/questions/79476211/pydantic-validation-issue-with-union-models-and-extra-forbid)) |
| Extract | `stream_mode` required ∈ `STREAM_MODES`; `stream_index` optional per Spec 465. No third mode this session. | Spec 465; `ConversionAddSpec` already validates `STREAM_MODES` |
| Paths | API checks each path is absolute **and** `Path.is_file()` before `add_to_queue`; else 422 | Spec 436–437 |
| GPU GET | `GPU_LAZY_GET` via `GPU_ENSURE_FN` + `GPU_COLD_INIT`. Empty session → `detect_gpu()` once; cached session → `get_gpu()` only. Always 200 `GPUCapabilitiesOut` matching the domain VO (`recommended_encoder: str`, no `probed`, not null). Route note “does not re-run” means **no second 1-frame**, not “never detect”. Do **not** reuse `ConversionService._lock` (owns `start_processing` only). Concurrent proof is `GPU_COLD_ORACLE` (not an N-party Barrier inside `detect_gpu`). | Spec 250 + 447; Local Canon `tests/unit/test_services.py` callers Barrier then `entered`/`release` Events; Research-backed double-checked locking |
| GPU POST refresh | always `detect_gpu()`; 200 same Out shape | Spec 448 |
| Speed/eta | Wire `speed`/`eta` strings. `eta` = `format_eta`. `speed` = `format_encode_speed` (`{n:.2f}x`), **not** `format_speed` | Spec 473; Local Canon `DownloadJobOut`; Session 13 reflection (FFmpeg `speed=` is a realtime multiplier stored in `speed_bps`) |
| Start 409 | `ConflictError` if processor `Processing` — copy downloads router, not silent return | Spec 449; Local Canon `downloads.py` 150–151 |
| Reset 409 | service `reset_failed` `ConflictError` if not Failed | Spec 457 |
| DELETE | 204; service `remove`/`clear_queue` only — files stay | Spec 454, 458 |
| Lists | `{ items, processor }` | Spec 427; Local Canon `DownloadListOut` |
| POST create | 201 `{ items }` | Spec 445 |
| Empty POST bodies | `EmptyIn \| None = Body(default=None)` | Local Canon downloads start/pause/cancel |
| `InvalidTimeRangeError` | add to `DOMAIN_HTTP_MAP` → **422** (today it is an unmapped `DomainError` → 500) | fail-closed; Spec cut range |
| Settings PUT | add `default_preset`, `skip_existing`, `gpu_preference` to `SettingsPutIn` (`output_dir` already exists). Unknown leaf → 422 via SettingsService | Spec 477–487; `extra="forbid"` |
| Settings GET `converter` | 200 because `SETTING_NAMESPACES` already includes `SETTING_NS`; unknown namespace still 404 | Spec 479; `settings.py` `_require_namespace` |
| Console module | keep `module: str` (04 ellipsis). Prove `CONSOLE_MODULE_CONVERT` serializes on `/health/console` | Spec 488; 04-rest-api.md 322 |
| Lifespan | `services.conversion.cancel_processing()` on shutdown; **do not** reuse download spy (AC-14.7 `cancel_calls == 1` must stay) | Local Canon `main.py` lifespan |
| MCP layout | `MCP_CONVERT_FILE` under `toolsets/` | Local Canon p5; 05 tree `compound/` is stale |
| MCP confirm | `DESTRUCTIVE_CONVERT` require `confirm: true`; `cancel` is **not** destructive | Spec 496; 05-mcp-server.md 88–95 |
| MCP settings | add `SETTING_NS` to `SETTING_NAMESPACES` + `SETTINGS_SCHEMA.namespaces.converter` = `CONVERTER_KEYS` | G29 / M2 |
| No `stop` alias | Convert has no download-style `stop` | Spec MCP table omits it |
| `convert()` frozen | do not edit FFmpeg `convert()` | Session 13 lock |
| 4A | skip — no renderer controls | create-plan §4A |
| Closeout | named receipts + `assert-handoff-markers.ps1` + `tools/check_exec_review.py` (`validate_closeout_artifacts.py` is not in this tree) | Local Canon p8-conversion-engine |

---

## G29 wiring checklist

| Layer | Ready? | Evidence |
|-------|--------|----------|
| DB `conversion_jobs` | YES | MEU-29 approved |
| `ConversionService` | YES | MEU-30 approved |
| REST `/conversions*` | NO → this plan MEU-31 | |
| `AppServices.conversion` + `get_conversion_service` | NO → MEU-31 | `APPSERVICES_SITES` |
| MCP `avkit_convert` | NO → MEU-32 after REST green | G29: do not register MCP before routes exist |
| MCP `SETTINGS_SCHEMA` converter | NO → MEU-32 | REST namespace already allowed |
| GUI Convert page | deferred MEU-33 | grouping Session 15 |

---

## Proposed Changes

### MEU-31 — `api-conversion`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-Input Error | Create/Update Parity | Source |
|---------|-------------|-------------------|--------------------|---------------------|----------------------|--------|
| REST body POST `/conversions` | `ConversionCreateIn` (discriminated union) | `paths` min 1; `kind` ∈ `KIND_WIRE_MAP`; compress `preset` default `balanced` ∈ `PRESET_WIRES` plus `COMPRESS_OVERRIDE_FIELDS`; cut `in_ms`/`out_ms` ints ≥0 `out_ms>in_ms` plus `CUT_OVERRIDE_FIELDS`; extract `stream_mode` ∈ `STREAM_MODES` plus `EXTRACT_OVERRIDE_FIELDS` | `extra="forbid"` on each union member | 422 | N/A (no PATCH) | Spec 429–467 |
| REST PUT `/conversions/reorder` | `ReorderIn` (reuse downloads shape `{ job_ids }`) | nonempty permutation | forbid | 422 | — | Spec 453 |
| REST PUT `/settings/converter` | `SettingsPutIn` | `CONVERTER_KEYS` | forbid; unknown key 422 | 422; unknown ns 404 | same leaves as create defaults | Spec 477–487 |
| File paths | API `Path` checks | absolute + `is_file()` | — | 422 | — | Spec 436 |
| Python `assert` | forbidden as validation | — | — | — | — | Spec 439 |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-31.1 | integration | `POST /conversions` → 201 `{ items }` for compress; maps `KIND_WIRE_MAP` / `PRESET_WIRES` into `ConversionAddSpec`; dual Bearer required. | Spec 445, 461–463 | extra field `nope` → 422 not 201 |
| AC-31.2 | integration | `GET /conversions` → 200 `{ items, processor }` with `QUEUE_NAME` runtime. | Spec 446 | bare array → fail |
| AC-31.3 | integration | Sequential `GPU_LAZY_GET`: first `GET /conversions/gpu` on empty session calls `detect_gpu` once and returns 200 `GPUCapabilitiesOut` with non-empty `recommended_encoder` (domain VO; no `probed` field). Second GET does not increment the detect counter. Overlap is AC-31.22. | Spec 250, 447 | second GET increments detect → fail |
| AC-31.4 | integration | `POST /conversions/gpu/refresh` always calls `detect_gpu` (increments counter even after a cached GET) and returns 200 same Out shape. | Spec 448 | refresh without detect → fail |
| AC-31.5 | integration | `POST /conversions/start` → 202; if processor `Processing` → 409 `ConflictError` envelope. | Spec 449 | start while Processing → 202 → fail |
| AC-31.6 | integration | `POST` pause/resume/cancel → 202. | Spec 450–452 | 200/204 → fail |
| AC-31.7 | integration | `PUT /conversions/reorder` `{ job_ids }` → 200 `{ items }`. | Spec 453 | extra key → 422 |
| AC-31.8 | integration | `DELETE /conversions` → 204; fake `clear_queue` called; no filesystem unlink. | Spec 454 | 200 + file delete → fail |
| AC-31.9 | integration | `GET /conversions/{id}` → 200; unknown id → 404 envelope. | Spec 456 | unknown → 500 → fail |
| AC-31.10 | integration | `POST /conversions/{id}/reset` → 200 when Failed; else 409. | Spec 457 | reset Pending → 200 → fail |
| AC-31.11 | integration | `DELETE /conversions/{id}` → 204; `remove` called; files stay. | Spec 458 | unlink output → fail |
| AC-31.12 | integration | Relative path, missing file, and directory path each → 422 before `add_to_queue`. Unknown preset → 422. | Spec 436, 467 | relative path reaches service → fail |
| AC-31.13 | integration | Discriminated union: cut without `in_ms`/`out_ms` → 422; extract without `stream_mode` → 422; cut body with `preset` → 422; `out_ms <= in_ms` → 422. | Spec 461–465; Research-backed unions | flat model ignoring `preset` on cut → fail |
| AC-31.14 | unit | `format_encode_speed(1.25) == FORMAT_ENCODE_SPEED_EXAMPLE`; `format_encode_speed(None) is None`; `format_speed(1.25)` is **not** that string (contains byte units). | Spec 473; Session 13 reflection | reuse `format_speed` for conversion Out → fail |
| AC-31.15 | integration | `ConversionJobOut` includes Spec field list; `speed`/`eta` strings; `kind`/`preset_id`/`copy_mode`/`audio_mode` are wires; `FORBIDDEN_RESPONSE_KEYS` absent. | Spec 471–475 | raw `speed_bps` on wire → fail |
| AC-31.16 | integration | `GET/PUT /settings/converter` 200 with `CONVERTER_KEYS`; unknown leaf 422; `GET /settings/nope` 404. | Spec 477–487; 04-rest-api 302 | `default_preset` PUT 422 because missing `SettingsPutIn` field → fail (this is the bug to fix) |
| AC-31.17 | integration | Live OpenAPI contains `CONVERT_ROUTES`; conversion `STATIC_BEFORE_ID` register before `/{id}`; unauthenticated `/conversions` → 401; `/health/console` can emit `CONSOLE_MODULE_CONVERT`. Green also updates `TEST_OPENAPI` `ROUTE_INDEX` to `ROUTE_COUNT_AFTER` so AC-16.6 stays true. | Spec 425, 488; G8; Local Canon AC-16.6/16.8 | missing `/conversions/gpu` in schema → fail |
| AC-31.18 | integration | G29: `build_services` exposes `.conversion`; `GET /conversions` 200 on tmp SQLite; lifespan calls conversion `cancel_processing` **and** AC-14.7 download `cancel_calls == 1` still; `InvalidTimeRangeError` maps 422 in `DOMAIN_HTTP_MAP`. | G29; Local Canon lifespan | unmapped time-range → 500 → fail |
| AC-31.19 | integration | Compress POST with `COMPRESS_OVERRIDE_FIELDS` set → 201 and fake `add_to_queue` receives a `ConversionAddSpec` with those values mapped through `AUDIO_ENCODE_WIRE_MAP` / `GPU_PREF_WIRES`. | Spec 461–463 | overrides dropped / never passed to spec → fail |
| AC-31.20 | integration | Cut POST with `CUT_OVERRIDE_FIELDS` `copy_mode=reencode` → 201 and spec.copy_mode is `Reencode`. Default omitted `copy_mode` → `FastCopy`. | Spec 464 | `copy_mode` ignored → fail |
| AC-31.21 | integration | Extract POST with `stream_mode=first` and `EXTRACT_OVERRIDE_FIELDS` `stream_index=2` → 201 and spec.stream_index==2. | Spec 465 | stream_index dropped → fail |
| AC-31.22 | unit | `GPU_COLD_ORACLE` against `GPU_ENSURE_FN` on one fake service. GET `/conversions/gpu` must call `GPU_ENSURE_FN` (spy). Do not use serialized HTTP as the overlap mechanism. | `GPU_COLD_INIT`; Local Canon `test_services.py` starters/`entered`/`release`; Research-backed double-check | unlocked helper: `detect_calls == GPU_COLD_GET_N` after `entered` (before release), or a worker still alive after join timeout → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Route table, envelopes, 201/202/204/409 | Spec | 08 §REST |
| extra=forbid / 422 / dual Bearer | Local Canon | Phase 4 `ApiModel` + `require_bearer` |
| Discriminated create body | Research-backed | Pydantic unions docs + extra=forbid per member |
| GPU first GET vs refresh | Spec | 08 line 250 names GET as a `detect_gpu` trigger; line 447 forbids **re-run** |
| GPU cold-init atomicity | Research-backed + Local Canon | `GPU_COLD_INIT` on `GPU_ENSURE_FN`; overlap oracle is `GPU_COLD_ORACLE`; engine `_lock` remains start-only |
| Speed `Nx` vs KB/s | Local Canon + Spec | Session 13 stored multiplier in `speed_bps`; schema-layer GUI **string** |
| `SettingsPutIn` converter leaves | Spec | 08 keys; current schema omits three leaves |
| `InvalidTimeRangeError` HTTP | fail-closed Local Canon | `DOMAIN_HTTP_MAP` pattern |
| MCP / GUI | deferred | MEU-32 / MEU-33 |

#### Control bindings

| AC | Observable | Traceable chain | Negative oracle |
|----|------------|-----------------|-----------------|
| AC-31.3 | fake `detect_gpu` counter | `GET /conversions/gpu` → `GPU_ENSURE_FN` → empty session → `detect_gpu`; cached → `get_gpu` only | second GET counter > 1 → fail |
| AC-31.22 | `GPU_COLD_ORACLE` observables (`detect_calls==1` before release; threads dead after join) | GET handler → `GPU_ENSURE_FN` → `GPU_COLD_INIT` lock → double-check `get_gpu` → `detect_gpu` | unlocked helper: `detect_calls == GPU_COLD_GET_N` while `entered` is set and release is unset → fail |
| AC-31.5 | HTTP 409 + envelope `ConflictError` | `POST /start` → router Processing check → `ConflictError` → `domain_error_handler` | Processing + 202 → fail |
| AC-31.12 | HTTP 422; service `add_to_queue` call count 0 | route validator → `Path.is_absolute`/`is_file` | relative path increments add counter → fail |
| AC-31.13 | HTTP 422 `validation_error` | FastAPI → Pydantic union member `extra=forbid` | cut+`preset` accepted → fail |
| AC-31.16 | HTTP 422 unknown leaf | `PUT /settings/converter` → `SettingsPutIn` dump → `SettingsService.set_namespace` | unknown key 200 → fail |
| AC-31.18 | `DOMAIN_HTTP_MAP[InvalidTimeRangeError]==422`; spy cancel counts | `register_exception_handlers` + `create_app` lifespan | time-range 500 or download cancel_calls≠1 → fail |
| AC-31.19–21 | spy `ConversionAddSpec` fields | `POST /conversions` → route map wires → `add_to_queue(paths, spec)` | override JSON present but spec field None → fail |

Atomicity: settings PUT remains `set_namespace` (existing). GPU cold cache is `GPU_COLD_INIT` on `GPU_ENSURE_FN` (not `ConversionService._lock`). Exhaustiveness: `KIND_WIRE_MAP` keys must equal `ConversionKind` members (owned enum — adding a kind without a wire breaks the census test). Fail-closed: unknown preset / kind / stream_mode → 422.

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/wire.py` | modify | conversion wire maps from named sets |
| `packages/api/src/avkit_api/formatters.py` | modify | `format_encode_speed` |
| `packages/api/src/avkit_api/errors.py` | modify | `InvalidTimeRangeError` → 422 |
| `packages/api/src/avkit_api/schemas/conversions.py` | new | In/Out models |
| `packages/api/src/avkit_api/schemas/settings.py` | modify | `CONVERTER_KEYS` leaves |
| `packages/api/src/avkit_api/routes/conversions.py` | new | `CONVERT_ROUTES`; static before `{id}`; `GPU_ENSURE_FN` + `GPU_COLD_INIT` + `GPU_COLD_ORACLE` |
| `packages/api/src/avkit_api/routes/__init__.py` | modify | export if needed |
| `packages/api/src/avkit_api/main.py` | modify | include router; lifespan cancel conversion |
| `packages/api/src/avkit_api/wiring.py` | modify | `ConversionService` on `AppServices` |
| `packages/api/src/avkit_api/dependencies.py` | modify | `get_conversion_service` |
| `tools/export_openapi.py` | modify | dummy `.conversion` |
| `openapi.committed.json` | modify | G8 after `--check` FAIL |
| `TEST_API_CONV` | new | AC-31.* |
| `TEST_OPENAPI` | modify | `ROUTE_COUNT_AFTER` |
| `APPSERVICES_SITES` tests | modify | `conversion=` argument |
| `TEST_WIRING` | modify | GET `/conversions` smoke |

---

### MEU-32 — `mcp-convert`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-Input Error | Create/Update Parity | Source |
|---------|-------------|-------------------|--------------------|---------------------|----------------------|--------|
| MCP `avkit_convert` | Zod discriminated union `.strict()` | `CONVERT_ACTIONS`; add fields match REST wires including `COMPRESS_OVERRIDE_FIELDS`, `CUT_OVERRIDE_FIELDS`, `EXTRACT_OVERRIDE_FIELDS` | `.strict()` | TOOL_ERROR validation before fetch | — | Spec 495–511; M2/M3 |
| MCP `avkit_settings` namespace | `z.enum(SETTING_NAMESPACES)` | add `SETTING_NS` | strict | validation_error | GET/SET same keys | G29 |
| Destructive | `confirm: z.literal(true)` | `DESTRUCTIVE_CONVERT` | — | TOOL_ERROR without fetch | — | M3 |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-32.1 | unit | `ACTION_INDEX` length `ACTION_INDEX_AFTER`; `COMPOUND_TOOLS` == `COMPOUND_TOOLS_AFTER`; existing `ACTION_INDEX_KEEP` rows unchanged. | M2; Spec MCP table | length remains `ACTION_INDEX_KEEP` after convert added → fail |
| AC-32.2 | unit | Each `CONVERT_ACTIONS` row matches REST method/path 1:1. No second URL space. No `stop` action. | Spec 499–511 | `/convert` or `/ffmpeg` path → fail |
| AC-32.3 | unit | Convert add schema `.strict()`; extra key fails `safeParse` before `fetch`. | M3; Local Canon downloadSchema | extra key still fetches → fail |
| AC-32.4 | unit | `DESTRUCTIVE_CONVERT` in `DESTRUCTIVE_ACTIONS`; `confirm: true` required; `NON_DESTRUCTIVE_CONVERT_STOPS` not in the set. | Spec 496; 05 88–95 | `cancel` requires confirm → fail |
| AC-32.5 | unit | Every convert action description includes `M7_MARKERS` (≥3 of 4). `SERVER_INSTRUCTIONS` say Convert is local files only and never upload YouTube. | M7; Spec 513 | missing Workflow: → fail |
| AC-32.6 | unit | `SETTINGS_SCHEMA.namespaces.converter` keys == `CONVERTER_KEYS` with `CONVERTER_DEFAULTS`; settings `z.enum` includes `SETTING_NS`. | G29; Spec 477 | get namespace `converter` Zod-fail → fail |
| AC-32.7 | integration | `handleTool` list requires `{ items, processor }`; `sanitize` drops `FORBIDDEN_RESPONSE_KEYS`. | M2; Spec 512 | list bare array accepted → fail |
| AC-32.8 | integration | After Green, `npm run build` (M4); `dist/` registers `avkit_convert`. `add` uses `ADD_TIMEOUT_MS` like download/transcript add. | M4; Local Canon registry timeout | live IDE uses stale dist without convert → fail |
| AC-32.9 | unit | Convert tool lives at `MCP_CONVERT_FILE` (not `src/compound/`). | Local Canon p5 tree | new `compound/` package → fail |
| AC-32.10 | unit | Missing `confirm` on remove/clear → TOOL_ERROR before fetch (download Local Canon: required `z.literal(true)` fails Zod first, so code is `validation_error` not `confirm_required`). Fetch spy count 0. | M3; Local Canon `download.ts` remove/clear | fetch runs without confirm → fail |
| AC-32.11 | integration | Convert `add` Zod accepts and `httpBody` forwards REST kind-specific fields (`COMPRESS_OVERRIDE_FIELDS`, `CUT_OVERRIDE_FIELDS`, `EXTRACT_OVERRIDE_FIELDS`) unchanged; extra unknown key still fails `.strict()`. | Spec 461–465, 499; M2 | compress `cq` stripped from fetch body → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Action table | Spec | 08 §MCP |
| confirm / strict / M7 / M4 | Local Canon | 05-mcp-server.md + emerging M2–M7 |
| File path `toolsets/` vs `compound/` | Local Canon | p5 actual tree wins over stale 05 diagram |
| Settings converter in MCP schema | G29 | REST already allows namespace |
| `estimate_output_size` MCP | deferred | Spec 417 “MCP may expose later”; not in MCP table |
| GUI | deferred | MEU-33 |

#### Control bindings

| AC | Observable | Traceable chain | Negative oracle |
|----|------------|-----------------|-----------------|
| AC-32.3 | `safeParse.success===false` | `convertSchema` → `handleTool` before `api()` | extra key + fetch called → fail |
| AC-32.4 / 32.10 | TOOL_ERROR; fetch count 0 | Zod `.strict()` + required `confirm: true` → `handleTool` returns before `api()` | remove without confirm fetches → fail |
| AC-32.11 | fetch body JSON | `handleTool` → `httpBody` → `api(POST,/conversions,body)` | `cq` in tool args but absent in fetch body → fail |
| AC-32.1 | `ACTION_INDEX.length` | `registry.ts` export | ≠ `ACTION_INDEX_AFTER` → fail |
| AC-32.7 | TOOL_ERROR `invalid_list_envelope` | `handleTool` → `isListEnvelope` | bare array returned as success → fail |

Fail-closed: unknown convert action → `unknown_action`. Exhaustiveness: `CONVERT_ACTIONS` vs OpenAPI `CONVERT_ROUTES` (same 13 operations; MCP paths omit `API_PREFIX`).

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `MCP_CONVERT_FILE` | new | Zod union + M7 descriptions |
| `mcp-server/src/toolsets/registry.ts` | modify | register tool, `ACTION_INDEX`, timeout for add |
| `mcp-server/src/toolsets/settings.ts` | modify | `SETTING_NS` + schema keys + leaves |
| `mcp-server/src/destructive.ts` | modify | `DESTRUCTIVE_CONVERT` |
| `mcp-server/src/index.ts` | modify | instructions line |
| `mcp-server/tests/fixtures.ts` | modify | expected index, destructive, `minimalInput` |
| `TEST_MCP_INDEX` / `TEST_MCP_CONFIRM` / m7 tests | modify | `ACTION_INDEX_AFTER` / `COMPOUND_TOOLS_AFTER` |
| `TEST_MCP_CONVERT` | new | AC-32.* |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Convert GUI, NavRail `/convert`, Wave 8 E2E, settings Convert card | deferred | MEU-33 | grouping Session 15; 08 §GUI; MEU-33 registered |
| Downloader Done row → Add to Convert | out-of-scope | — | 08 lines 535–541 named integration deferral “not this phase’s GUI”; not owned by MEU-33 |
| Timeline / 2-pass / size-target / `estimate_output_size` MCP | out-of-scope | — | 08 lines 417, 541–543, 579–584 |
| SSE encode progress | out-of-scope | — | 08 line 579 |
| `wmic` GPU detect | out-of-scope | — | 08 line 584; already banned MEU-29 |
| Session 8c / MEU-27 | out-of-scope | — | grouping: do not start 8c; MEU-27 is `ready_for_review` |
| Rewrite download/transcript/TTS routers except listed additive wiring | out-of-scope | — | grouping Session 14 file list; 08 “do not invent parallel paths” |
| `avkit_convert.stop` alias | out-of-scope | — | Spec MCP table omits `stop` (download-only) |
| `convert()` TTS/download audio rewrite | out-of-scope | — | 08 line 577; Session 13 freeze |
| Git commit / push | out-of-scope | — | AGENTS.md human approval gate |

---

## BUILD_PLAN.md Audit

This project **does** update the hub `Next:` field and phase `"8"` `execution_plans`. Do not hand-edit AUTOGEN tables.

Validation (H1 / WP-HUB):

```powershell
uv run python -c "from pathlib import Path; import json, re, sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-26-p8-conversion-api-mcp'; SLASH=PLAN+'/'; NEXT=json.loads(Path(PLAN+'/named-sets.json').read_text(encoding='utf-8'))['HUB_NEXT_AFTER']; MEUS=('MEU-31','MEU-32'); data=load(); p8=next(p for p in data['phases'] if str(p['id'])=='8'); eps=list(p8.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 8 missing PLAN_FOLDER_SLASH'); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

There is **no CLI** for phase `execution_plans` — edit YAML then `meu_status.py render`. MEU `--plan` has **no trailing slash**; phase list **has** trailing slash.

---

## Verification Plan

Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is optional; P0 redirect to `C:/Temp/av-kit/` is mandatory. Red pytest **must not** use `-x`. Green/gate **keep `-x`**. Parametrize `ids=["AC-31.N"]` hyphen form.

### 1. MEU-31 Red oracle
```powershell
uv run pytest tests/e2e/test_api_conversions.py --tb=short -v *> C:/Temp/av-kit/fail-to-pass-meu-31-py.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'MEU-31 Red unexpectedly green'; Get-Content C:/Temp/av-kit/fail-to-pass-meu-31-py.txt | Select-Object -Last 40; exit 1 }; pwsh -NoProfile -File docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-red-oracle.ps1 -Kind py -Meu 31 -Receipt C:/Temp/av-kit/fail-to-pass-meu-31-py.txt; $ocode=$LASTEXITCODE; if ($ocode -ne 0) { Get-Content C:/Temp/av-kit/fail-to-pass-meu-31-py.txt | Select-Object -Last 40; exit $ocode }; 'PASS: FAIL_TO_PASS MEU-31'
```

### 2. MEU-31 Green / scoped gate
```powershell
uv run pytest tests/e2e/test_api_conversions.py tests/e2e/test_api_openapi.py tests/e2e/test_api_auth.py tests/e2e/test_api_health_settings.py tests/integration/test_api_wiring.py -x --tb=short -v *> C:/Temp/av-kit/pytest-meu-31-green.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-meu-31-green.txt | Select-Object -Last 40; exit $code
```

```powershell
uv run ruff check packages/api tests/e2e/test_api_conversions.py tests/e2e/test_api_openapi.py *> C:/Temp/av-kit/ruff-meu-31.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ruff-meu-31.txt; exit $code
```

```powershell
uv run pyright packages/api *> C:/Temp/av-kit/pyright-meu-31.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pyright-meu-31.txt | Select-Object -Last 40; exit $code
```

### 3. OpenAPI (G8) — this session **does** touch `packages/api`
```powershell
uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```
If `[FAIL]` / drift, then:
```powershell
uv run python tools/export_openapi.py -o openapi.committed.json *> C:/Temp/av-kit/openapi-regen.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-regen.txt; exit $code
```

### 4. MEU-32 Red oracle
```powershell
pwsh -NoProfile -Command { Push-Location mcp-server; npx vitest run tests/convert.test.ts --reporter=verbose --reporter=json --outputFile=C:/Temp/av-kit/fail-to-pass-meu-32.json; $c=$LASTEXITCODE; Pop-Location; exit $c } *> C:/Temp/av-kit/fail-to-pass-meu-32.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'MEU-32 Red unexpectedly green'; Get-Content C:/Temp/av-kit/fail-to-pass-meu-32.txt | Select-Object -Last 40; exit 1 }; pwsh -NoProfile -File docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-red-oracle.ps1 -Kind ui -Meu 32 -Receipt C:/Temp/av-kit/fail-to-pass-meu-32.txt -JsonReceipt C:/Temp/av-kit/fail-to-pass-meu-32.json; $ocode=$LASTEXITCODE; if ($ocode -ne 0) { Get-Content C:/Temp/av-kit/fail-to-pass-meu-32.txt | Select-Object -Last 40; exit $ocode }; 'PASS: FAIL_TO_PASS MEU-32'
```
(Redirect the vitest stdout to `fail-to-pass-meu-32.txt` via `*>` on the wrapper command in `task.md`.)

### 5. MEU-32 Green / M4
```powershell
pwsh -NoProfile -Command { Push-Location mcp-server; npx tsc --noEmit; $c=$LASTEXITCODE; if ($c -ne 0) { exit $c }; npx vitest run; $c=$LASTEXITCODE; if ($c -ne 0) { exit $c }; npm run build; exit $LASTEXITCODE } *> C:/Temp/av-kit/mcp-meu-32-green.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/mcp-meu-32-green.txt | Select-Object -Last 40; exit $code
```

### 6. Anti-placeholder / G36
```powershell
rg -n -e TODO -e FIXME -e NotImplementedError packages/api/src mcp-server/src *> C:/Temp/av-kit/anti-placeholder-h1.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-placeholder-h1.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-placeholder-h1.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }
rg -n -e "it\.skip|describe\.skip|test\.skip|it\.todo|\bxit\(|\bxdescribe\(" mcp-server/tests tests/e2e/test_api_conversions.py *> C:/Temp/av-kit/g36-h1.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/g36-h1.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/g36-h1.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }
```

---

## Open Questions

Research resolved these; reviewer confirms. Not `Human-decision-required`.

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| Unprobed GET `/gpu` | A: `GPU_LAZY_GET` — first GET detects, later GET cache | Spec 250 + 447 | Matches “GET is a trigger” and “do not re-run” | — | ✅ |
| | B: sentinel `probed:false` / null encoder | planner r1 (withdrawn) | — | Conflicts with VO `recommended_encoder: str` | ❌ |
| | C: GET never detects | misread of 447 | — | Contradicts Spec 250 | ❌ |
| GPU cold-init race | A: `GPU_COLD_INIT` + `GPU_COLD_ORACLE` | Local Canon callers Barrier + `entered`/`release` Events | Session 14; terminating oracle | — | ✅ |
| | B: reuse `ConversionService._lock` | engine already has a lock | Mixes GPU with start_processing; reopens MEU-29 | ❌ |
| | C: N-party Barrier inside fake `detect_gpu` | planner r3 (withdrawn) | — | Deadlocks the lock in `GPU_COLD_INIT` | ❌ |
| Conversion `speed` string | A: `format_encode_speed` `Nx` | Session 13 reflection; FFmpeg speed factor | Honest GUI | Different from download KB/s | ✅ |
| | B: reuse `format_speed` | Local Canon DownloadJobOut literally | One helper | `1.25` → `1.3 B/s` | ❌ |
| Create body shape | A: discriminated union per kind | [Pydantic unions](https://docs.pydantic.dev/latest/concepts/unions/) | Wrong-kind fields 422 | Three models | ✅ |
| | B: one flat model | DownloadCreateIn | Fewer types | cut+`preset` silently stored | ❌ |
| MCP file path | A: `toolsets/convert.ts` | p5 Local Canon | Matches live tree | 05 diagram says `compound/` | ✅ |
| | B: `src/compound/convert.ts` | 05-mcp-server.md tree | Matches stale diagram | Splits package layout | ❌ |

---

## Research References

- [08-video-conversion.md](../../../build-plan/08-video-conversion.md) §REST §MCP
- [04-rest-api.md](../../../build-plan/04-rest-api.md) envelopes, settings namespace, console module
- [05-mcp-server.md](../../../build-plan/05-mcp-server.md) M2–M7, `DESTRUCTIVE_ACTIONS`
- [Pydantic discriminated unions](https://docs.pydantic.dev/latest/concepts/unions/)
- [FastAPI #5120](https://github.com/fastapi/fastapi/issues/5120) — **not** used as GPU contract (withdrawn)
- Session 13 reflection: `docs/execution/reflections/2026-08-24-p8-conversion-engine-reflection.md` (speed multiplier; Next = this slug)
- Local Canon: `packages/api/src/avkit_api/routes/downloads.py`, `mcp-server/src/toolsets/download.ts`
- Emerging: M2, M3, M4, M5, M6, M7, G8, G29
