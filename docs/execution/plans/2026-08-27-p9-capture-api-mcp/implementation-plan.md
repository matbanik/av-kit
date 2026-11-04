---
project: "2026-08-27-p9-capture-api-mcp"
date: "2026-08-27"
source: "docs/build-plan/09-screenshot-capture.md"
meus: ["MEU-37", "MEU-38"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 9 Capture API + MCP

> **Project**: `2026-08-27-p9-capture-api-mcp`
> **Build Plan Section(s)**: [09-screenshot-capture.md](../../../build-plan/09-screenshot-capture.md) §REST + §MCP; [04-rest-api.md](../../../build-plan/04-rest-api.md) envelope/settings; [05-mcp-server.md](../../../build-plan/05-mcp-server.md) compound tools
> **Status**: `draft`
> **Grouping**: [2026-08-26-p9-screenshot-capture-session-grouping.md](../../../../.agent/context/grouping/2026-08-26-p9-screenshot-capture-session-grouping.md) Session 17 — MEU-37 → MEU-38

---

## Goal

Stand up **capture REST + MCP only**: `/api/v1/captures*` on `packages/api`, G8 OpenAPI regen, and compound tool `avkit_capture` on `mcp-server`. Call existing `CaptureService` (Session 16). Do not invent MEU IDs. Do not start Session 18 / MEU-39. Do not start Session 8c. Do not rewrite download/transcript/TTS/convert routers except additive `capture` leaves on `SettingsPutIn`, health `module=capture` coverage, `AppServices.capture` wiring, and the MCP catalog-envelope / binary-image branches required by this spec.

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
| MEU-37 | `.agent/context/handoffs/` + `HANDOFFS[0]` |
| MEU-38 | `.agent/context/handoffs/` + `HANDOFFS[1]` |

Rolling implementation review: `EXEC_REVIEW_FILE`. Rolling plan review: `PLAN_REVIEW_FILE`.

Product glob owner: `HANDOFF_FILTER`. Expected count: `HANDOFF_COUNT` = `2`. Filenames: `HANDOFFS` in `named-sets.json` (do not restate).

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`. `builder_model` is `—`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-37a | MEU-37 Red: `TEST_API_CAP` AC-37.1–AC-37.{`RED_COUNT_37`} only. Do **not** change `TEST_OPENAPI` length in Red (AC-16.6 must stay green). Pass `assert-red-oracle.ps1 -Kind py -Meu 37`. Red pytest **must not** use `-x`. Do not add `routes/captures.py` yet. | — | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-37-py.txt`; compact then re-read `task.md` |
| WP-37b | Green MEU-37: captures router/schemas, wire maps, `SettingsPutIn` capture leaves, `DOMAIN_HTTP_CAPTURE`, `AppServices.capture`, `list_requests` + repo `list()`, G8. Do not add MCP tool. | WP-37a | `compact_continue` | `packages/api/src/avkit_api/routes/captures.py`; compact then re-read `task.md` |
| WP-37c | MEU-37 scoped gate + `HANDOFFS[0]` | WP-37b | `compact_continue` | `HANDOFFS[0]` |
| WP-38a | MEU-38 Red: `TEST_MCP_CAPTURE` AC-38.1–AC-38.{`RED_COUNT_38`}. Pass `assert-red-oracle.ps1 -Kind ui -Meu 38`. Do not add `MCP_CAPTURE_FILE` yet. | WP-37c | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-38.txt` |
| WP-38b | Green MEU-38: `avkit_capture`, `DESTRUCTIVE_CAPTURE`, settings `SETTING_NS` schema, catalog envelope, binary `image` content, instructions. M4 `npm run build`. | WP-38a | `compact_continue` | `MCP_CAPTURE_FILE` |
| WP-38c | MEU-38 scoped gate + `HANDOFFS[1]` | WP-38b | `compact_continue` | `HANDOFFS[1]` |
| WP-HUB | Bind MEU-37–38 `--plan PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"9"` (**keep** `ENGINE_PLAN_SLASH`); rewrite hub `Next` to `HUB_NEXT_AFTER`. Grouping Session 17 ✅ is **H2 after exec `approved`**. | WP-38c | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Reviewer confirms these locks (does not invent a second behavior):

1. **Harness gate:** `.agent/context/harness.local.md` `plan_to_exec_gate: reviewer-auto` wins over Cursor default `human` in `create-plan.md` §5c. After Codex `approved`, auto-continue to execution. System-injected “approved” is still not a verdict (`GUARDRAILS.md` SIGN 3).
2. **Phase 9 is three sessions.** This plan is Session 17 only (MEU-37–38). Next after H2: `HUB_NEXT_AFTER`.
3. **Do not start Session 8c / MEU-27** (`ready_for_review`, unrelated).
4. **Codex is metered** (`PROJECT-PROFILE.md`). Dispatch still required; implementer never self-reviews.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

Executable owner: `docs/execution/plans/2026-08-27-p9-capture-api-mcp/named-sets.json`. Do not restate literals in ACs or task rows; cite the name.

| Name | Role |
|------|------|
| `CAPTURE_ROUTES` / `ROUTE_COUNT_*` | OpenAPI + `TEST_OPENAPI` census (`ROUTE_COUNT_KEEP` + `CAPTURE_ROUTE_COUNT` = `ROUTE_COUNT_AFTER`) |
| `CAPTURE_ACTIONS` / `ACTION_INDEX_*` | MCP census (`ACTION_INDEX_KEEP` + `CAPTURE_ACTION_COUNT` = `ACTION_INDEX_AFTER`) |
| `REST_ONLY_ROUTES` | Overlay/Electron REST that Spec MCP table omits (`register`, complete, cancel) |
| `POST_MODES` / `REGISTER_SOURCE_WIRES` / `CAPTURE_SOURCE_OUT_WIRES` | register **In** lowercase (Spec 407); shot **Out** Pascal enum `.value` (04 status-wire canon) |
| `REQUEST_STATUS_QUERY_WIRES` / `REQUEST_STATUS_OUT_WIRES` / `VARIANT_WIRES` / `GET_QUERY_KEYS` | GET `?status=` lowercase (Spec 171 `status=pending`); request **Out** Pascal (04 `DownloadStatus.Pending` → `Pending`) |
| `CAPTURE_KEYS` / `CAPTURE_DEFAULTS` / `SETTING_NS` | Settings namespace (already in `SETTINGS_KEY_TABLE`; MCP schema + `SettingsPutIn` catch up) |
| `DESTRUCTIVE_CAPTURE` / `NON_DESTRUCTIVE_CAPTURE` | M3 confirm set |
| `IMAGE_MAX_BYTES` / `IMAGE_MAX_BYTES_HUMAN` / `IMAGE_MIME_MAP` / `IMAGE_DEFAULT_VARIANT` / `MCP_IMAGE_*` | GET byte cap; `IMAGE_MAX_BYTES_HUMAN` is the **once-only** unit label beside the integer |
| `CATALOG_ENVELOPE_KEY` / `FORBIDDEN_LIST_KEY` / `INVALID_CATALOG_CODE` | `{ items }` without `processor` |
| `DOMAIN_HTTP_CAPTURE` | input errors 422; grab/platform unavailable 503 (04-rest-api status table) |
| `PATH_ID_TYPE` / `PATH_ID_UNKNOWN_HTTP` | `{id}` is `str` like downloads; unknown/malformed → 404 |
| `MCP_TS_GATE` / `MCP_ESLINT` | TypeScript gate is `tsc --noEmit`. `MCP_ESLINT` is `null` |
| `STATIC_BEFORE_ID` | FastAPI register order (`/requests` before `/{id}`) |
| `APPSERVICES_SITES` | every `AppServices(` constructor |
| `FORBIDDEN_RESPONSE_KEYS` | sanitize / Out must not include |
| `HANDOFF_*` / `RED_*` / `HUB_NEXT_AFTER` | closeout + hub |
| `MCP_CAPTURE_FILE` | Local Canon `toolsets/` (not stale `compound/` tree) |

---

## Implementation locks (research + local canon)

| Lock | Value | Source |
|------|-------|--------|
| Create body | Pydantic **discriminated union** on `mode` ∈ `POST_MODES`; each member subclasses `ApiModel` (`extra="forbid"`). `register` requires `path` + `source` ∈ `REGISTER_SOURCE_WIRES`. `fullscreen` has no extra fields. `region` requires `x`,`y`,`width`,`height` ints; width/height ≥ `CAPTURE_MIN_EDGE_PX`. | Spec 401–411; [Pydantic discriminated unions](https://docs.pydantic.dev/latest/concepts/unions/); extra=forbid on **each** member ([SO 79476211](https://stackoverflow.com/questions/79476211/pydantic-validation-issue-with-union-models-and-extra-forbid)) |
| List envelope | `{ items }` **without** `FORBIDDEN_LIST_KEY`. Catalog, not a queue. | Spec 390 |
| POST create | 201 `{ item }` (singular). | Spec 391 |
| Interactive 409 | `CaptureRequestConflictError` (subclass of `ConflictError`) → 409. | Spec 257, 393; existing `DOMAIN_HTTP_MAP[ConflictError]` |
| Complete body | `{ "path": "..." }` extra=forbid. One UoW in service (Session 16 F2) — unknown id + valid PNG → 404 and **no** new shot. | Spec 394; Session 16 RULE-2 |
| Cancel body | `EmptyIn \| None = Body(default=None)` | Local Canon downloads start/pause/cancel |
| Interactive create body | `POST /captures/requests` uses `EmptyIn \| None = Body(default=None)`; extra key → 422 | Spec 393; Local Canon empty POST |
| Path `{id}` | `PATH_ID_TYPE` (`str`), not FastAPI `UUID`. Unknown or malformed → `PATH_ID_UNKNOWN_HTTP` (404 `NotFoundError`), same as `downloads.py` `get_download(id: str)`. Domain UUID check is on entity construct, not the path. | Local Canon Phase 4 routes; Phase 4 404 unknown job; Spec 310 reuse `NotFoundError` |
| Image GET | Query `variant` ∈ `VARIANT_WIRES`, default `IMAGE_DEFAULT_VARIANT`. Dual Bearer. Bytes + `IMAGE_MIME_MAP` Content-Type. `len(bytes) > IMAGE_MAX_BYTES` → HTTP 413 envelope. Missing file → 404. | Spec 397, 514; RFC 9110 §15.5.14 names 413; product SSOT is Spec (oversized **response**); cite `IMAGE_MAX_BYTES` not a restated MiB phrase |
| Annotate | Discriminated union on `type` matching Session 16 annotation VOs; empty array allowed; extra=forbid; unknown color → 422 via `AnnotationValidationError`. | Spec 259–274, 398 |
| DELETE | 204; service `remove` **deletes files**. | Spec 399 |
| Paths | Service `_require_inbox_file` already raises `InboxPathError`; map `DOMAIN_HTTP_CAPTURE`. Do not re-implement containment in the router. | Spec 380; Session 16 service |
| Settings PUT | add `CAPTURE_KEYS` to `SettingsPutIn`. Unknown leaf → 422. GET `/settings/capture` already allowed (`SETTING_NAMESPACES`). | Spec 417–427 |
| Console module | keep `module: str` (04 ellipsis). Prove `CONSOLE_MODULE_CAPTURE` serializes on `/health/console`. | Spec 428; Local Canon AC-31.17 |
| Lifespan | **Do not** add capture cancel. Keep AC-14.7 download `cancel_calls == 1` and conversion cancel. Capture is not a processor. | Spec 51; Local Canon `main.py` |
| `list_requests` | Add `CaptureRequestRepository.list()` + `CaptureService.list_requests(status=)` that calls `expire_stale_requests` then lists. API does not own UoW. Update engine fakes (`TEST_INFRA_CAP` method census, `FakeCaptureRequestRepo`). Query filter tokens are `REQUEST_STATUS_QUERY_WIRES`; listed Out statuses are `REQUEST_STATUS_OUT_WIRES`. | Spec 392, 357, 171; G29; 04-rest-api.md 122 |
| Shot/request Out wires | `CaptureShotOut.source` ∈ `CAPTURE_SOURCE_OUT_WIRES`; register **In** stays `REGISTER_SOURCE_WIRES`. | Spec 407 In; 04-rest-api.md 122 Out |
| Domain HTTP | Map `DOMAIN_HTTP_CAPTURE` into `DOMAIN_HTTP_MAP`. 422 = InboxPath/AnnotationValidation only. 503 = CaptureFailed + CaptureNotSupported (04 line 99 analog: required backend/environment missing). Do not emit 501. | Spec 232, 272, 299, 308; 04-rest-api.md 87–99 |
| MCP layout | `MCP_CAPTURE_FILE` under `toolsets/` | Local Canon p5; 05 tree `compound/` is stale |
| MCP actions | Exactly `CAPTURE_ACTIONS`. Do **not** add MCP complete/cancel/register. Overlay uses `REST_ONLY_ROUTES`. | Spec 442–451; Local Canon convert omitted `stop` |
| MCP confirm | `DESTRUCTIVE_CAPTURE` require `confirm: true`; `NON_DESTRUCTIVE_CAPTURE` not in the set. | Spec 436; 05-mcp-server.md 88–95 |
| MCP list envelope | `avkit_capture` `list` and `list_requests` use catalog check (`items` array, `FORBIDDEN_LIST_KEY` absent). Convert/download `list` still require `{ items, processor }`. | Spec 390 vs Local Canon `isListEnvelope` |
| MCP image | `handleTool` action `image` returns MCP ImageContent (`MCP_IMAGE_FIELDS`) from binary GET. Cap `IMAGE_MAX_BYTES`. `list`/`get` stay JSON paths. | Spec 438; [MCP tools Image Content](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) |
| MCP GET query | Append `GET_QUERY_KEYS` present on the parsed args as `?variant=` / `?status=`. `status` tokens ∈ `REQUEST_STATUS_QUERY_WIRES`. | Spec 392, 397, 171 |
| MCP timeout | `capture` (fullscreen/region grab) uses `ADD_TIMEOUT_MS` like convert `add`. | Local Canon registry timeout |
| MCP settings | add `SETTING_NS` to `SETTING_NAMESPACES` + `SETTINGS_SCHEMA.namespaces.capture` = `CAPTURE_KEYS` | G29 / M2 |
| Instructions | Capture is **local screen + local files**. Still never upload YouTube. `capture_interactive` needs the desktop app (tray). Fullscreen/region bbox works if the API process can see the session desktop. | Spec 455 |
| No `from __future__ import annotations` on `ports/capture.py` | Session 16 lock; do not reopen the port file. | Session 16 |
| No `mkdir` in services | Session 16 `test_ac_12_8_no_direct_mkdir_in_services`. | Session 16 |
| G8 | `--check` then `-o` on drift. This session **does** change `packages/api/`. | G8; Session 16 skipped G8 |
| 4A | skip — no renderer controls | create-plan §4A |
| Closeout | named receipts + `assert-handoff-markers.ps1` + `assert-exec-review-dispatch.ps1` + `tools/check_exec_review.py` | Local Canon p9-capture-engine |

---

## G29 wiring checklist

| Layer | Ready? | Evidence |
|-------|--------|----------|
| DB `capture_shots` / `capture_requests` | YES | MEU-35 approved |
| `CaptureService` | YES | MEU-36 approved (`list_requests` added this session) |
| REST `/captures*` | NO → this plan MEU-37 | |
| `AppServices.capture` + `get_capture_service` | NO → MEU-37 | `APPSERVICES_SITES` |
| MCP `avkit_capture` | NO → MEU-38 after REST green | G29: do not register MCP before routes exist |
| MCP `SETTINGS_SCHEMA` capture | NO → MEU-38 | REST namespace already allowed |
| GUI Capture page / tray / F2 | deferred MEU-39 | grouping Session 18 |

---

## Proposed Changes

### MEU-37 — `api-capture`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-Input Error | Create/Update Parity | Source |
|---------|-------------|-------------------|--------------------|---------------------|----------------------|--------|
| REST body POST `/captures` | `CaptureCreateIn` (discriminated union on `mode`) | `POST_MODES`; register `path` absolute + `source` ∈ `REGISTER_SOURCE_WIRES`; region ints ≥0, edge ≥ `CAPTURE_MIN_EDGE_PX` | `extra="forbid"` on each member | 422 | N/A (no PATCH) | Spec 401–411 |
| REST body POST `/captures/requests` | `EmptyIn \| None = Body(default=None)` | no fields | forbid | 422 | — | Spec 393; Local Canon empty POST |
| REST body POST `…/complete` | `CaptureCompleteIn` | `path` non-empty str | forbid | 422 | — | Spec 394 |
| REST body POST `…/cancel` | `EmptyIn \| None = Body(default=None)` | no fields | forbid | 422 | — | Spec 395; Local Canon empty POST |
| REST body POST `…/annotate` | `AnnotateIn` `{ annotations: [...] }` | annotation discriminated union; colors named or `#RRGGBB`; text 1–500 | forbid | 422 | empty array clears bake | Spec 259–274, 398 |
| REST query GET `/captures/requests` | FastAPI `Query` | `status` optional ∈ `REQUEST_STATUS_QUERY_WIRES` | unknown → 422 | 422 | — | Spec 171, 392 |
| REST query GET `…/image` | FastAPI `Query` | `variant` ∈ `VARIANT_WIRES` default `IMAGE_DEFAULT_VARIANT` | unknown → 422 | 422 | — | Spec 397 |
| REST path `{id}` on shot GET/image/annotate/DELETE | FastAPI `id: PATH_ID_TYPE` | unconstrained `str` (not UUID type) | — | `PATH_ID_UNKNOWN_HTTP` | — | Local Canon `downloads.py` `get_download(id: str)`; Phase 4 404; Spec 310 |
| REST path `{id}` on request complete/cancel | FastAPI `id: PATH_ID_TYPE` | unconstrained `str` | — | `PATH_ID_UNKNOWN_HTTP` | — | Local Canon; Spec 310 |
| REST PUT `/settings/capture` | `SettingsPutIn` | `CAPTURE_KEYS` | forbid; unknown key 422 | 422; unknown ns 404 | same leaves as defaults | Spec 417–427 |
| File paths | service `_require_inbox_file` | inbox file | — | `InboxPathError` → 422 | — | Spec 380, 232 |
| Image bytes | route after `read_image` | `IMAGE_MAX_BYTES` | — | 413 / 404 | — | Spec 397 |
| Python `assert` | forbidden as validation | — | — | — | — | Spec 384 |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-37.1 | integration | `GET /captures` → 200 `{ items }` with `CATALOG_ENVELOPE_KEY`; `FORBIDDEN_LIST_KEY` absent; dual Bearer required. Calls `list_shots`. | Spec 390 | bare array or `processor` present → fail |
| AC-37.2 | integration | `POST /captures` `mode=register` → 201 `{ item }`; maps `REGISTER_SOURCE_WIRES` into `CaptureSource`; extra field `nope` → 422. | Spec 391, 407 | extra field 201 → fail |
| AC-37.3 | integration | `POST /captures` `mode=fullscreen` → 201; fake `capture_fullscreen` called once. `CaptureFailedError` maps `DOMAIN_HTTP_CAPTURE` **503**. `CaptureNotSupportedError` maps **503**. | Spec 408; 04-rest-api.md 99 (503 when required binary/environment missing) | fullscreen 422 on black-frame error → fail |
| AC-37.4 | integration | `POST /captures` `mode=region` with edge ≥ `CAPTURE_MIN_EDGE_PX` → 201 and `capture_region` receives `BBox`. Width `7` → 422. | Spec 409 | width 7 → 201 → fail |
| AC-37.5 | integration | `GET /captures/requests` expires then lists `{ items }`. `?status=` token ∈ `REQUEST_STATUS_QUERY_WIRES` (example `pending` per Spec 171). Unknown status → 422. Listed `status` fields use `REQUEST_STATUS_OUT_WIRES`. | Spec 171, 392, 357; 04-rest-api.md 122 | omit expire (stale Pending still listed) → fail |
| AC-37.6 | integration | `POST /captures/requests` empty/`EmptyIn` → 201 request Out. Extra key → 422. Second Pending → 409 envelope (`CaptureRequestConflictError`). | Spec 257, 393 | extra key 201 or second 201 → fail |
| AC-37.7 | integration | `POST …/complete` `{ path }` → 200 completed request with `shot_id`. Extra key → 422. Unknown UUID + valid path → 404 and fake shot-insert count stays 0 (Session 16 F2 at HTTP). | Spec 394; RULE-2 | unknown id creates shot row → fail |
| AC-37.8 | integration | `POST …/cancel` → 200 cancelled; empty/`EmptyIn` body. | Spec 395 | extra key 200 → fail |
| AC-37.9 | integration | `GET /captures/{id}` → 200 metadata + path strings, **no** bytes; unknown id → 404 envelope. | Spec 396 | response contains raw PNG bytes → fail |
| AC-37.10 | integration | `GET …/image?variant=original` → 200 `IMAGE_MIME_MAP` bytes; unauthenticated → 401; missing annotated → 404; fake bytes longer than `IMAGE_MAX_BYTES` → 413 envelope. Default variant is `IMAGE_DEFAULT_VARIANT`. | Spec 397, 514 | unauthenticated 200 → fail |
| AC-37.11 | integration | `POST …/annotate` `{ annotations }` → 200 shot Out; empty array allowed; extra field → 422; unknown color → 422. | Spec 398, 272 | extra key 200 → fail |
| AC-37.12 | integration | `DELETE /captures/{id}` → 204; fake `remove` called; unknown → 404. | Spec 399 | 200 + skip remove → fail |
| AC-37.13 | integration | `GET/PUT /settings/capture` 200 with `CAPTURE_KEYS` / `CAPTURE_DEFAULTS`; unknown leaf 422; `GET /settings/nope` 404. | Spec 417–427 | `inbox_dir` PUT 422 because missing `SettingsPutIn` field → fail |
| AC-37.14 | integration | Live OpenAPI contains `CAPTURE_ROUTES`; capture `STATIC_BEFORE_ID` register before `/{id}`; unauthenticated `/captures` → 401; `/health/console` can emit `CONSOLE_MODULE_CAPTURE`. Green also updates `TEST_OPENAPI` `ROUTE_INDEX` to `ROUTE_COUNT_AFTER` so AC-16.6 stays true. | Spec 386, 428, 430; G8; Local Canon AC-16.6/16.8 | `/captures/requests` missing from schema → fail |
| AC-37.15 | integration | G29: `build_services` exposes `.capture`; `GET /captures` 200 on tmp SQLite; lifespan still calls download `cancel_processing` (`cancel_calls == 1`) and conversion cancel; **no** capture processor cancel; `DOMAIN_HTTP_CAPTURE` entries exist. All `APPSERVICES_SITES` construct `capture=`. | G29; Local Canon lifespan | unmapped `InboxPathError` → 500 → fail |
| AC-37.16 | integration | Discriminated union: register without `path` → 422; fullscreen body with `x` → 422; region without `height` → 422. | Spec 401–411; Research-backed unions | flat model ignoring extra region fields → fail |
| AC-37.17 | integration | `CaptureShotOut` fields == `CAPTURE_SHOT_OUT_FIELDS`; `source` ∈ `CAPTURE_SOURCE_OUT_WIRES` (Pascal enum `.value`). Paths as strings; `FORBIDDEN_RESPONSE_KEYS` absent. Request Out == `CAPTURE_REQUEST_OUT_FIELDS`; `status` ∈ `REQUEST_STATUS_OUT_WIRES`. | Spec 413–415; 04-rest-api.md 122 | `source=hotkey` lowercase on GET item → fail |
| AC-37.18 | integration | `CaptureRequestRepository.list()` exists on the port + SQLAlchemy repo; `CaptureService.list_requests` expires then returns rows (optional status filter). Engine fakes (`TEST_INFRA_CAP` method census, `FakeCaptureRequestRepo` in services/conversion tests) implement `list`. | Spec 392; G29 | GET `/captures/requests` reaches UoW from the router → fail |
| AC-37.19 | integration | Shot/request `{id}` is `PATH_ID_TYPE`. `not-a-uuid` and unknown UUID on GET/DELETE/complete/cancel/image/annotate → `PATH_ID_UNKNOWN_HTTP` envelope, not 422 and not 500. | Local Canon `downloads.py:228`; Phase 4 404; Spec 310 | `not-a-uuid` → 422 → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Route table, envelopes, 201/204/409, image GET | Spec | 09 §REST |
| extra=forbid / 422 / dual Bearer | Local Canon | Phase 4 `ApiModel` + `require_bearer` |
| Discriminated POST body | Research-backed | Pydantic unions docs + extra=forbid per member |
| Oversized image HTTP | Spec | 09 line 397; named set `IMAGE_MAX_BYTES`; RFC 9110 names 413 |
| CaptureFailed / CaptureNotSupported HTTP | `DOMAIN_HTTP_CAPTURE` 503 | Local Canon 04-rest-api.md 99 (503 when required binary/environment missing); analog FFmpeg. Black-frame / mss permission / platform-unsupported is runtime environment, not request schema. Do **not** invent 501 (Phase 4 status table has none). Do **not** map grab failure to 422. |
| Path `{id}` | `PATH_ID_TYPE` + `PATH_ID_UNKNOWN_HTTP` | Local Canon Phase 4 `id: str`; 404 unknown job |
| `{ items }` no processor | Spec | 09 line 390 |
| Settings PUT capture leaves | Spec | 09 keys; current `SettingsPutIn` omits them |
| Capture domain HTTP map 422 subset | Spec + Local Canon | `InboxPathError` / `AnnotationValidationError` are request/path validation (Spec 232, 272; Phase 4 422) |
| `list_requests` on service | Spec + G29 | GET `/captures/requests` cannot talk to UoW |
| MCP / GUI | deferred | MEU-38 / MEU-39 |

#### Control bindings

| AC | Observable | Traceable chain | Negative oracle |
|----|------------|-----------------|-----------------|
| AC-37.1 | JSON keys `items` present, `processor` absent | `GET /captures` → `list_shots` → `CaptureListOut` | `processor` in body → fail |
| AC-37.3 | HTTP 503 envelope for grab/platform errors | `CaptureFailedError` / `CaptureNotSupportedError` → `DOMAIN_HTTP_CAPTURE` 503 | black-frame 422 → fail |
| AC-37.6 | HTTP 409 + envelope `ConflictError` | `POST /requests` → `request_interactive` → `CaptureRequestConflictError` → `domain_error_handler` | second Pending + 201 → fail |
| AC-37.7 | HTTP 404; fake `shot_inserts == 0` | complete route → `complete_request` one UoW | unknown UUID inserts shot → fail |
| AC-37.10 | status 413 / 401 / `Content-Type` | `read_image` → `len(bytes) > IMAGE_MAX_BYTES` → `HTTPException(413)` | oversized PNG 200 → fail |
| AC-37.16 | HTTP 422 `validation_error` | FastAPI → Pydantic union member `extra=forbid` | fullscreen+`x` accepted → fail |
| AC-37.15 | `DOMAIN_HTTP_MAP` entries; spy cancel counts | `register_exception_handlers` + `create_app` lifespan | `InboxPathError` 500 or download `cancel_calls≠1` → fail |
| AC-37.18 | `list()` on repo + service | GET `/requests` → `list_requests` → `uow.capture_requests.list` | router imports `SqlAlchemyUnitOfWork` → fail |
| AC-37.19 | HTTP 404 envelope | path `id: PATH_ID_TYPE` → service `get_shot` / `complete_request` / `remove` → `NotFoundError` | `not-a-uuid` 422 or 500 → fail |

Atomicity: complete/register stay one UoW inside `CaptureService` (Session 16). Settings PUT remains `set_namespace`. Exhaustiveness: `CAPTURE_SOURCE_OUT_WIRES` must equal `CaptureSource` member `.value`s. Fail-closed: unknown `mode` / `variant` / query `status` / annotation `type` → 422.

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/wire.py` | modify | `CAPTURE_SOURCE_OUT_WIRES` + `REQUEST_STATUS_OUT_WIRES` (Pascal); register In still `REGISTER_SOURCE_WIRES` |
| `packages/core/src/avkit_core/ports/storage.py` | modify | `CaptureRequestRepository.list()` |
| `packages/core/src/avkit_core/services/capture.py` | modify | `list_requests` only (no mkdir, no grab rewrite) |
| `packages/infrastructure/src/avkit_infra/database/repositories.py` | modify | SQLAlchemy `list()` |
| `packages/api/src/avkit_api/errors.py` | modify | `DOMAIN_HTTP_CAPTURE` |
| `packages/api/src/avkit_api/schemas/captures.py` | new | In/Out models |
| `packages/api/src/avkit_api/schemas/settings.py` | modify | `CAPTURE_KEYS` leaves |
| `packages/api/src/avkit_api/routes/captures.py` | new | `CAPTURE_ROUTES`; static `/requests` before `/{id}` |
| `packages/api/src/avkit_api/main.py` | modify | include router; no capture lifespan cancel |
| `packages/api/src/avkit_api/wiring.py` | modify | `CaptureService` + `CaptureAdapter` on `AppServices` |
| `packages/api/src/avkit_api/dependencies.py` | modify | `get_capture_service` |
| `tools/export_openapi.py` | modify | dummy `.capture` |
| `openapi.committed.json` | modify | G8 after `--check` FAIL |
| `TEST_API_CAP` | new | AC-37.* |
| `TEST_OPENAPI` | modify | `ROUTE_COUNT_AFTER` |
| `APPSERVICES_SITES` tests | modify | `capture=` argument |
| `TEST_WIRING` | modify | GET `/captures` smoke |
| `TEST_INFRA_CAP` + engine fakes | modify | `list` on request repo census |

---

### MEU-38 — `mcp-capture`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-Input Error | Create/Update Parity | Source |
|---------|-------------|-------------------|--------------------|---------------------|----------------------|--------|
| MCP `list` | Zod `.strict()` action object | no extra fields | `.strict()` | TOOL_ERROR `validation_error` before fetch | — | Spec 442; M1 |
| MCP `get` | Zod `.strict()` | `id` string (same `PATH_ID_TYPE` as REST; unknown → REST 404 TOOL_ERROR) | `.strict()` | extra key TOOL_ERROR; unknown id TOOL_ERROR from REST 404 | — | Spec 443; Local Canon path ids |
| MCP `image` | Zod `.strict()` | `id`; optional `variant` ∈ `VARIANT_WIRES` | `.strict()` | extra key TOOL_ERROR | — | Spec 438, 444 |
| MCP `capture` | Zod discriminated `mode` ∈ `{fullscreen,region}` | region ints ≥0, edge ≥ `CAPTURE_MIN_EDGE_PX`; **no** `register` | `.strict()` | extra key / `register` TOOL_ERROR | — | Spec 447; REST-only register |
| MCP `capture_interactive` | Zod `.strict()` | no extra fields (empty body) | `.strict()` | extra key TOOL_ERROR | — | Spec 448 |
| MCP `list_requests` | Zod `.strict()` | optional `status` ∈ `REQUEST_STATUS_QUERY_WIRES` | `.strict()` | extra / unknown status TOOL_ERROR | — | Spec 449; Spec 171 |
| MCP `annotate` | Zod `.strict()` | `id` + annotations matching REST `AnnotateIn` | `.strict()` | extra key TOOL_ERROR | — | Spec 450 |
| MCP `remove` | Zod `.strict()` + `confirm: true` | `id`; `DESTRUCTIVE_CAPTURE` | `.strict()` | missing confirm TOOL_ERROR before fetch | — | Spec 451; M3 |
| MCP `avkit_settings` namespace | `z.enum(SETTING_NAMESPACES)` | add `SETTING_NS` | strict | validation_error | GET/SET same keys | G29 |
| Image bytes | `handleTool` image branch | `IMAGE_MAX_BYTES`; `MCP_IMAGE_FIELDS` | — | TOOL_ERROR | — | Spec 438 |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-38.1 | unit | `ACTION_INDEX` length `ACTION_INDEX_AFTER`; `COMPOUND_TOOLS` == `COMPOUND_TOOLS_AFTER`; existing `ACTION_INDEX_KEEP` rows unchanged. | M2; Spec MCP table | length remains `ACTION_INDEX_KEEP` after capture added → fail |
| AC-38.2 | unit | Each `CAPTURE_ACTIONS` row matches REST method/path 1:1. No second URL space. `REST_ONLY_ROUTES` not in `ACTION_INDEX`. | Spec 442–451 | MCP `complete` / `/grab` path → fail |
| AC-38.3 | unit | Capture schema `.strict()`; extra key fails `safeParse` before `fetch`. | M1; Local Canon `convertSchema` | extra key still fetches → fail |
| AC-38.4 | unit | `DESTRUCTIVE_CAPTURE` in `DESTRUCTIVE_ACTIONS`; `confirm: true` required; `NON_DESTRUCTIVE_CAPTURE` not in the set. | Spec 436; 05 88–95 | `list` requires confirm → fail |
| AC-38.5 | unit | Every capture action description includes `M7_MARKERS` (≥3 of 4). `SERVER_INSTRUCTIONS` say Capture is local screen + local files, never upload YouTube, and `capture_interactive` needs the desktop app. | M7; Spec 455 | missing `Workflow:` → fail |
| AC-38.6 | unit | `SETTINGS_SCHEMA.namespaces.capture` keys == `CAPTURE_KEYS` with `CAPTURE_DEFAULTS`; settings `z.enum` includes `SETTING_NS`. | G29; Spec 417 | get namespace `capture` Zod-fail → fail |
| AC-38.7 | integration | `handleTool` capture `list` / `list_requests` require `{ items }` and reject `FORBIDDEN_LIST_KEY` (`INVALID_CATALOG_CODE`). Convert `list` still requires `{ items, processor }`. Sanitize drops `FORBIDDEN_RESPONSE_KEYS`. | M2; Spec 390; G25 | capture list with `processor` accepted → fail |
| AC-38.8 | integration | After Green, `npm run build` (M4); `dist/` registers `avkit_capture`. `capture` uses `ADD_TIMEOUT_MS`. | M4; Local Canon registry timeout | live IDE uses stale dist without capture → fail |
| AC-38.9 | unit | Capture tool lives at `MCP_CAPTURE_FILE` (not `src/compound/`). | Local Canon p5 tree | new `compound/` package → fail |
| AC-38.10 | unit | Missing `confirm` on remove → TOOL_ERROR before fetch (required `z.literal(true)` fails Zod first, so code is `validation_error` not `confirm_required`). Fetch spy count 0. | M3; Local Canon `download.ts` remove | fetch runs without confirm → fail |
| AC-38.11 | integration | Action `image` returns content item with `MCP_IMAGE_FIELDS` (`type`=`MCP_IMAGE_CONTENT_TYPE`, base64 `data`, `mimeType` from `IMAGE_MIME_MAP`). JSON-stringified PNG as `type:text` fails. Oversize → TOOL_ERROR, not image content. | Spec 438; [MCP Image Content](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) | `type:text` of raw bytes → fail |
| AC-38.12 | integration | GET `image` / `list_requests` append `GET_QUERY_KEYS` (`variant`, `status`) onto the fetch URL. | Spec 392, 397 | `variant` in args but fetch URL has no query → fail |
| AC-38.13 | integration | Capture `capture` Zod accepts `mode=fullscreen` and `mode=region` with bbox ints and `httpBody` forwards REST fields; extra unknown key still fails `.strict()`. G25: list item keys include `CAPTURE_SHOT_OUT_FIELDS`. | Spec 447; M2 | region `width` stripped from fetch body → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Action table | Spec | 09 §MCP |
| confirm / strict / M7 / M4 | Local Canon | 05-mcp-server.md + emerging M1–M7 |
| File path `toolsets/` vs `compound/` | Local Canon | p5 actual tree wins over stale 05 diagram |
| Settings capture in MCP schema | G29 | REST already allows namespace |
| MCP image bytes | Spec + Research-backed | 09 line 438 exception; MCP 2025-06-18 ImageContent |
| Catalog vs queue list envelope | Spec | 09 line 390 vs convert `{ items, processor }` |
| MCP complete/cancel | out-of-scope | Spec MCP table omits; overlay uses REST |
| GUI | deferred | MEU-39 |

#### Control bindings

| AC | Observable | Traceable chain | Negative oracle |
|----|------------|-----------------|-----------------|
| AC-38.3 | `safeParse.success===false` | `captureSchema` → `handleTool` before `api()` | extra key + fetch called → fail |
| AC-38.4 / 38.10 | TOOL_ERROR; fetch count 0 | Zod `.strict()` + required `confirm: true` → return before `api()` | remove without confirm fetches → fail |
| AC-38.7 | TOOL_ERROR `INVALID_CATALOG_CODE` | capture list → catalog check, not `isListEnvelope` | `processor` on capture list succeeds → fail |
| AC-38.11 | content `[0].type === image` | `handleTool` image → binary GET → ImageContent | JSON parse of PNG as tool text → fail |
| AC-38.12 | fetch URL query string | `GET_QUERY_KEYS` append after `interpolatePath` | `status=pending` dropped → fail |
| AC-38.1 | `ACTION_INDEX.length` | `registry.ts` export | ≠ `ACTION_INDEX_AFTER` → fail |

Fail-closed: unknown capture action → `unknown_action`. Exhaustiveness: `CAPTURE_ACTIONS` vs OpenAPI `CAPTURE_ROUTES` minus `REST_ONLY_ROUTES`.

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `MCP_CAPTURE_FILE` | new | Zod union + M7 descriptions |
| `mcp-server/src/toolsets/registry.ts` | modify | register tool, `ACTION_INDEX`, catalog check, image branch, timeout, query keys |
| `mcp-server/src/client.ts` | modify | binary GET when `Content-Type` is image/* (or capture image helper) |
| `mcp-server/src/toolsets/settings.ts` | modify | `SETTING_NS` + schema keys + leaves |
| `mcp-server/src/destructive.ts` | modify | `DESTRUCTIVE_CAPTURE` |
| `mcp-server/src/index.ts` | modify | instructions lines |
| `mcp-server/tests/fixtures.ts` | modify | expected index, destructive, `minimalInput` |
| `TEST_MCP_INDEX` / `TEST_MCP_CONFIRM` / m7 tests | modify | `ACTION_INDEX_AFTER` / `COMPOUND_TOOLS_AFTER` |
| `TEST_MCP_CAPTURE` | new | AC-38.* |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Capture GUI, tray, F2 overlay, NavRail `/capture`, Wave 9 E2E, settings Capture card | deferred | MEU-39 | grouping Session 18; 09 §GUI; MEU-39 registered |
| MCP `complete` / `cancel` / `register` | out-of-scope | — | 09 lines 442–451 omit them; overlay uses REST (09 line 171) |
| HotkeyConflictError REST 409 | out-of-scope | — | 09 line 306 Electron-only |
| Session 8c / MEU-27 | out-of-scope | — | grouping: do not start 8c |
| Rewrite download/transcript/TTS/convert routers except listed additive wiring | out-of-scope | — | grouping Session 17 file list; 09 “do not invent parallel paths” |
| `captures` queue name / processor | out-of-scope | — | 09 line 51; Session 16 `FORBIDDEN_QUEUE_NAME` |
| ShareX C# paste | out-of-scope | — | 09 Golden Rule 5; 09 lines 540–544 |
| SSE | out-of-scope | — | 09 line 490 |
| Git commit / push | out-of-scope | — | AGENTS.md human approval gate |

---

## BUILD_PLAN.md Audit

This project **does** update the hub `Next:` field and phase `"9"` `execution_plans`. Keep `ENGINE_PLAN_SLASH`. Do not hand-edit AUTOGEN tables.

Validation (H1 / WP-HUB):

```powershell
rtk proxy uv run python -c "from pathlib import Path; import json, re, sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-27-p9-capture-api-mcp'; SLASH=PLAN+'/'; ENGINE='docs/execution/plans/2026-08-26-p9-capture-engine/'; NEXT=json.loads(Path(PLAN+'/named-sets.json').read_text(encoding='utf-8'))['HUB_NEXT_AFTER']; MEUS=('MEU-37','MEU-38'); data=load(); p9=next(p for p in data['phases'] if str(p['id'])=='9'); eps=list(p9.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 9 missing PLAN_FOLDER_SLASH'); ENGINE not in eps and sys.exit('phase 9 missing ENGINE_PLAN_SLASH'); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

There is **no CLI** for phase `execution_plans` — edit YAML then `meu_status.py render`. MEU `--plan` has **no trailing slash**; phase list **has** trailing slash.

---

## Verification Plan

Classify every command through `.agent/docs/output-evidence-policy.md`. Prefix executable segments with `rtk proxy`. P0 redirect to `C:/Temp/av-kit/` is mandatory. Red pytest **must not** use `-x`. Green/gate **keep `-x`**. Parametrize `ids=["AC-37.N"]` hyphen form.

### 1. MEU-37 Red oracle
```powershell
rtk proxy uv run pytest tests/e2e/test_api_captures.py --tb=short -v *> C:/Temp/av-kit/fail-to-pass-meu-37-py.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'MEU-37 Red unexpectedly green'; Get-Content C:/Temp/av-kit/fail-to-pass-meu-37-py.txt | Select-Object -Last 40; exit 1 }; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-27-p9-capture-api-mcp/assert-red-oracle.ps1 -Kind py -Meu 37 -Receipt C:/Temp/av-kit/fail-to-pass-meu-37-py.txt; $ocode=$LASTEXITCODE; if ($ocode -ne 0) { Get-Content C:/Temp/av-kit/fail-to-pass-meu-37-py.txt | Select-Object -Last 40; exit $ocode }; 'PASS: FAIL_TO_PASS MEU-37'
```

### 2. MEU-37 Green / scoped gate
```powershell
rtk proxy uv run pytest tests/e2e/test_api_captures.py tests/e2e/test_api_openapi.py tests/e2e/test_api_auth.py tests/e2e/test_api_health_settings.py tests/e2e/test_api_conversions.py tests/integration/test_api_wiring.py -x --tb=short -v *> C:/Temp/av-kit/pytest-meu-37-green.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-meu-37-green.txt | Select-Object -Last 40; exit $code
```

```powershell
rtk proxy uv run ruff check packages/api tests/e2e/test_api_captures.py tests/e2e/test_api_openapi.py *> C:/Temp/av-kit/ruff-meu-37.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ruff-meu-37.txt; exit $code
```

```powershell
rtk proxy uv run pyright packages/api *> C:/Temp/av-kit/pyright-meu-37.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pyright-meu-37.txt | Select-Object -Last 40; exit $code
```

### 3. OpenAPI (G8) — this session **does** touch `packages/api`
```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```
If `[FAIL]` / drift, then:
```powershell
rtk proxy uv run python tools/export_openapi.py -o openapi.committed.json *> C:/Temp/av-kit/openapi-regen.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-regen.txt; exit $code
```

### 4. MEU-38 Red oracle
```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location mcp-server; npx vitest run tests/capture.test.ts --reporter=verbose --reporter=json --outputFile=C:/Temp/av-kit/fail-to-pass-meu-38.json; $c=$LASTEXITCODE; Pop-Location; exit $c } *> C:/Temp/av-kit/fail-to-pass-meu-38.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'MEU-38 Red unexpectedly green'; Get-Content C:/Temp/av-kit/fail-to-pass-meu-38.txt | Select-Object -Last 40; exit 1 }; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-27-p9-capture-api-mcp/assert-red-oracle.ps1 -Kind ui -Meu 38 -Receipt C:/Temp/av-kit/fail-to-pass-meu-38.txt -JsonReceipt C:/Temp/av-kit/fail-to-pass-meu-38.json; $ocode=$LASTEXITCODE; if ($ocode -ne 0) { Get-Content C:/Temp/av-kit/fail-to-pass-meu-38.txt | Select-Object -Last 40; exit $ocode }; 'PASS: FAIL_TO_PASS MEU-38'
```

### 5. MEU-38 Green / M4
```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location mcp-server; npx tsc --noEmit; $c=$LASTEXITCODE; if ($c -ne 0) { exit $c }; npx vitest run; $c=$LASTEXITCODE; if ($c -ne 0) { exit $c }; npm run build; exit $LASTEXITCODE } *> C:/Temp/av-kit/mcp-meu-38-green.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/mcp-meu-38-green.txt | Select-Object -Last 40; exit $code
```

### 6. Anti-placeholder / G36
```powershell
rtk proxy rg -n -e TODO -e FIXME -e NotImplementedError packages/api/src mcp-server/src *> C:/Temp/av-kit/anti-placeholder-h1.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-placeholder-h1.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-placeholder-h1.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }
rtk proxy rg -n -e "it\.skip|describe\.skip|test\.skip|it\.todo|\bxit\(|\bxdescribe\(" mcp-server/tests tests/e2e/test_api_captures.py *> C:/Temp/av-kit/g36-h1.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/g36-h1.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/g36-h1.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }
```

---

## Open Questions

Research resolved these; reviewer confirms. Not `Human-decision-required`.

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| MCP vs REST action count | A: `CAPTURE_ACTIONS` (8); overlay keeps `REST_ONLY_ROUTES` | Spec 442–451 | Matches convert omitting `stop` | MCP cannot complete overlay | ✅ |
| | B: add MCP complete/cancel/register | planner completeness | Agent can finish without tray | Contradicts Spec table + 09 line 455 tray requirement | ❌ |
| Oversized image status | A: HTTP 413 when `len > IMAGE_MAX_BYTES` | Spec 397 | Product SSOT | RFC 9110 413 is request-oriented | ✅ |
| | B: 500 / 404 | RFC literalism | Matches “request content” reading | Contradicts Spec 397 | ❌ |
| Request catalog | A: add repo `list()` + `list_requests` | Spec 392; G29 | MCP poll can see Completed + `shot_id` | Touches engine fakes | ✅ |
| | B: GET only `get_pending_request` | existing port | Smaller diff | Completed requests invisible; MCP workflow broken | ❌ |
| Capture list envelope | A: catalog `{ items }` only | Spec 390 | Honest (not a queue) | Split from convert `isListEnvelope` | ✅ |
| | B: emit dummy `processor` | reuse convert check | One envelope helper | Spec forbids `processor` | ❌ |
| MCP image payload | A: MCP ImageContent `type`/`data`/`mimeType` | Spec 438; MCP 2025-06-18 | Vision models can annotate | Client binary path | ✅ |
| | B: base64 inside JSON text | current `api()` JSON-only | Less client change | Spec says image content, not path JSON | ❌ |
| Discriminated POST | A: union on `mode` | Pydantic unions + extra=forbid per member | Wrong-mode fields 422 | Three models | ✅ |
| | B: one flat model | fewer types | register+`x` silently stored | ❌ |
| Path `{id}` validation | A: `PATH_ID_TYPE` `str`; unknown/malformed → `PATH_ID_UNKNOWN_HTTP` (404) | Local Canon `downloads.py` `id: str`; Phase 4 404 unknown job; Spec 310 `NotFoundError` | Matches live download/convert routes | Spec IDs are UUID strings but path is not typed UUID | ✅ |
| | B: FastAPI `UUID` → 422 on malformed | Spec UUID wording | Strict format | Diverges from every Phase 4 `{id}` route | ❌ |
| Grab/platform HTTP | A: `CaptureFailedError` + `CaptureNotSupportedError` → 503 | 04-rest-api.md 99 | Environment/runtime, not schema | 503 table example is FFmpeg-named | ✅ |
| | B: 422 / 501 | none | Looks like validation / “not implemented” | 422 contradicts Phase 4 422 row; 501 is absent from Phase 4 | ❌ |
| Request status wires | A: query `REQUEST_STATUS_QUERY_WIRES`; Out `REQUEST_STATUS_OUT_WIRES` | Spec 171 query `pending`; 04-rest-api.md 122 `Pending` | Matches Electron poll + REST Out canon | Two sets | ✅ |
| | B: one lowercase set for query and Out | Spec 171 only | Simpler | Conflicts with conversion `.value` Pascal Out | ❌ |

---

## Research References

- [09-screenshot-capture.md](../../../build-plan/09-screenshot-capture.md) §REST §MCP
- [04-rest-api.md](../../../build-plan/04-rest-api.md) envelopes, settings namespace, console module
- [05-mcp-server.md](../../../build-plan/05-mcp-server.md) M1–M7, `DESTRUCTIVE_ACTIONS`
- [Pydantic discriminated unions](https://docs.pydantic.dev/latest/concepts/unions/)
- [MCP tools — Image Content](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [RFC 9110 §15.5.14 413 Content Too Large](https://www.rfc-editor.org/rfc/rfc9110.html#name-413-content-too-large)
- Session 16 reflection: `docs/execution/reflections/2026-08-26-p9-capture-engine-reflection.md` (RULE-1–3; Next = this slug)
- Peer: `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/`
- Local Canon: `packages/api/src/avkit_api/routes/conversions.py`, `mcp-server/src/toolsets/convert.ts`
- Emerging: M1, M2, M3, M4, M5, M6, M7, G8, G25, G29, G36
