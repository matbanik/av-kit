---
project: "2026-08-26-p9-capture-engine"
date: "2026-08-26"
source: "docs/build-plan/09-screenshot-capture.md"
meus: ["MEU-34", "MEU-35", "MEU-36"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 9 Capture Engine

> **Project**: `2026-08-26-p9-capture-engine`
> **Build Plan Section(s)**: [09-screenshot-capture.md](../../../build-plan/09-screenshot-capture.md) §Domain + §Infrastructure + §Service layer
> **Status**: `draft`
> **Grouping**: [2026-08-26-p9-screenshot-capture-session-grouping.md](../../../../.agent/context/grouping/2026-08-26-p9-screenshot-capture-session-grouping.md) Session 16 — MEU-34 → MEU-35 → MEU-36

---

## Goal

Stand up the **capture engine** only: domain types + ports + errors, ninth/tenth tables `capture_shots` / `capture_requests` + Pillow bake + mss grab adapter, and `CaptureService` (inbox scan, register, synchronous grab, interactive request state, annotate/bake, file-deleting remove). USER_EXPLICIT 2026-08-26 `/create-plan p9-capture-engine` starts the Phase 9 pathway after the Phase 9 spec + ShareX source map. Grouping **does not** pack MEU-37–39 into this plan (fan-out exception). Do not invent MEU IDs. Do not start Session 8c (MEU-27). Do not rewrite FastAPI routers, MCP tools, tray/hotkey/overlay, or the Capture page.

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
| MEU-34 | `.agent/context/handoffs/` + `HANDOFFS[0]` |
| MEU-35 | `.agent/context/handoffs/` + `HANDOFFS[1]` |
| MEU-36 | `.agent/context/handoffs/` + `HANDOFFS[2]` |

Rolling implementation review: `.agent/context/handoffs/2026-08-26-p9-capture-engine-implementation-critical-review.md`.

Product glob owner: `HANDOFF_FILTER`. Expected count: `HANDOFF_COUNT` = `3`. Filenames: `HANDOFFS` in `named-sets.json` (do not restate).

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-34a | MEU-34 Red: `TEST_DOMAIN_CAP` AC-34.1–AC-34.`RED_COUNT_34` + expand `TEST_DOMAIN` `SETTING_NAMESPACES` / `ENUM_MEMBERS` / `INFRA_NAMES`. Write `API_BASELINE`. Pass `RED_ORACLE_CHECK -Meu 34`. Red pytest **must not** use `-x`. Do not add `capture.py` yet. | — | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-34-py.txt`; `API_BASELINE`; compact then re-read `task.md` |
| WP-34b | Green MEU-34: enums, `CaptureShot` / `CaptureRequest` / annotation + `BBox` / `ImageProbe`, ports, errors, `SETTING_NS`. Do not add tables or Pillow. | WP-34a | `compact_continue` | `packages/core/src/avkit_core/domain/capture.py`; compact then re-read `task.md` |
| WP-34c | MEU-34 scoped gate (`assert-meu-scoped-gate.ps1 -Meu 34`: pytest + pyright + ruff + anti-placeholder/G36) + `HANDOFF_34` | WP-34b | `compact_continue` | `HANDOFF_34` |
| WP-35a | MEU-35 Red: `TEST_INFRA_CAP` AC-35.1–35.14 (`RED_COUNT_35`). Expand `TEST_SQLITE` `TABLES` / `UOW_ATTRIBUTES` / `INFRA_LAYOUT`. Pass `RED_ORACLE_CHECK -Meu 35`. Do not add tables yet. | WP-34c | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-35-py.txt` |
| WP-35b | Green MEU-35: tables + UoW + `INFRA_CAPTURE_REL` (mss grab + Pillow bake). Expand FakeUoW copies. Ban `PIL_FORBIDDEN` in core. | WP-35a | `compact_continue` | `packages/infrastructure/src/avkit_infra/capture/adapter.py`; `models.py` |
| WP-35c | MEU-35 scoped gate (`assert-meu-scoped-gate.ps1 -Meu 35`) + `HANDOFF_35` | WP-35b | `compact_continue` | `HANDOFF_35` |
| WP-36a | MEU-36 Red: `TEST_SVC_CAP` AC-36.1–AC-36.`RED_COUNT_36`. Pass `RED_ORACLE_CHECK -Meu 36`. Do not add `CaptureService` yet. | WP-35c | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-36-py.txt` |
| WP-36b | Green MEU-36: `CaptureService` + `CAPTURE_KEYS` + FakeCapturePort. G29 tmp-SQLite. No REST. | WP-36a | `compact_continue` | `packages/core/src/avkit_core/services/capture.py` |
| WP-36c | MEU-36 scoped gate (`assert-meu-scoped-gate.ps1 -Meu 36`) + `HANDOFF_36` | WP-36b | `compact_continue` | `HANDOFF_36` |
| WP-HUB | Bind MEU-34–36 `--plan PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"9"`; rewrite hub `Next` to `HUB_NEXT_AFTER`. Grouping Session 16 ✅ is **H2 after exec `approved`**. | WP-36c | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Spec locks + grouping Session 16 are already `Human-approved` / `Spec`. Reviewer confirms these locks (does not invent a second behavior):

1. **Harness gate:** `.agent/context/harness.local.md` `plan_to_exec_gate: reviewer-auto` wins over Cursor default `human`. After Codex `approved`, auto-continue to execution. System-injected “approved” is still not a verdict (`GUARDRAILS.md` SIGN 3).
2. **Phase 9 is three sessions.** This plan is Session 16 only. Next after H2: `HUB_NEXT_AFTER`.
3. **Do not start Session 8c / MEU-27.**
4. **Not a processor queue.** Do not add `FORBIDDEN_QUEUE_NAME` to `QUEUE_NAMES`.
5. **Grab backend is `GRAB_BACKEND` (mss)** because Spec BBox is virtual-desktop pixels in the same space as mss monitors. Pillow `ImageGrab` is not the grab path.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (single-statement rule)

Executable owner: `docs/execution/plans/2026-08-26-p9-capture-engine/named-sets.json`. Do not restate literals in ACs or task rows; cite the name.

| Name | Role |
|------|------|
| `SETTING_NS` | `"capture"` added to `SETTING_NAMESPACES` (MEU-34) |
| `FORBIDDEN_QUEUE_NAME` | must **not** be in `QUEUE_NAMES` |
| `CAPTURE_SOURCE_MEMBERS` / `CAPTURE_REQUEST_STATUS_MEMBERS` / `ANNOTATION_TYPE_MEMBERS` | StrEnum members; persist `.name` |
| `ANNOTATION_WIRE` | `.name.lower()` map for sidecar/API (API mapping is MEU-37; domain exposes `to_wire` / `from_wire`) |
| `NAMED_COLORS` / `TEXT_MAX_CHARS` / `HIGHLIGHT_OPACITY_MIN` / `HIGHLIGHT_OPACITY_MAX` | annotation color, text length, highlight opacity inclusive bounds |
| `ANNOTATION_CLAMP_MIN` | service clamps integer annotation coords to `[ANNOTATION_CLAMP_MIN, width]` / `[ANNOTATION_CLAMP_MIN, height]` |
| `CAPTURE_MIN_EDGE_PX` | reject bbox width/height below this |
| `REQUEST_TTL_S` | Pending → Expired after this many seconds |
| `TIMESTAMP_FORMAT` | local-clock filename stem |
| `SCAN_EXTENSIONS` | non-recursive inbox scan |
| `ANNOTATED_SUFFIX` / `SIDECAR_SUFFIX` / `SIDECAR_VERSION` | bake + sidecar naming |
| `GRAB_BACKEND` / `MSS_VIRTUAL_INDEX` | mss `monitors[0]` fullscreen; region `{left,top,width,height}` |
| `BLACK_LUM_MAX` | grayscale mean at or below this → `CaptureFailedError` |
| `ARROWHEAD_*` | line + triangle head |
| `FONT_CANDIDATES` | Segoe UI → Arial → `ImageFont.load_default()` |
| `PIL_FORBIDDEN` | core import ban |
| `CAPTURE_KEYS` / `CAPTURE_DEFAULTS` | `SETTINGS_KEY_TABLE` (MEU-36); REST PUT is MEU-37 |
| `CAPTURE_SHOT_COLUMNS` / `CAPTURE_REQUEST_COLUMNS` | table + entity field set |
| `UOW_CAPTURE_ATTRS` | UnitOfWork attributes |
| `INFRA_CAPTURE_REL` | adapter path under `avkit_infra/` |
| `LOG_MODULE` | structlog `module=` |
| `API_TREE` / `API_BASELINE` | SHA256 manifest of `packages/api`; H1-4 fail-closed |
| `HANDOFF_*` / `RED_*` / `HUB_NEXT_AFTER` | closeout + hub |
| `REVIEWER_AGENT` / `EXEC_REVIEW_FILE` / `DISPATCH_*` / `DISPATCH_ID_FIELD` / `EXEC_REVIEW_MODE` / `EXEC_REVIEW_APPROVED` | H1-7 provenance: exact dispatch folder + `final.md` verdict token + frontmatter `dispatch_id` |
| `PLACEHOLDER_PATHS_*` / `G36_TEST_PATHS_*` / `GATE_*` | MEU-scoped quality gate file lists (every Files Modified product/test path) |
| `REFLECTION_FILE` / `METRICS_SLUG` / `REFLECTION_MARKERS` | H2-2 / H2-4 closeout structural checks |

Plan-folder helpers (not product code): `assert-red-oracle.ps1`, `assert-api-tree-hash.ps1`, `assert-openapi-skip.ps1`, `assert-handoff-markers.ps1`, `assert-handoff-acs.ps1`, `assert-anti-placeholder.ps1`, `assert-meu-scoped-gate.ps1`, `assert-exec-review-dispatch.ps1`.

---

## Implementation locks (research + local canon)

| Lock | Value | Source |
|------|-------|--------|
| Grab | `GRAB_BACKEND` only. `capture_fullscreen` → `sct.grab(sct.monitors[MSS_VIRTUAL_INDEX])`. `capture_region` → `sct.grab({"left": x, "top": y, "width": w, "height": h})`. Tests inject a fake `mss.mss` so CI needs no display. | Spec 293; [mss monitors](https://python-mss.readthedocs.io/latest/usage.html); [mss region grab](https://python-mss.readthedocs.io/v10.2.0/examples.html) |
| Bake highlight | RGBA overlay + `Image.alpha_composite` (RGB `ImageDraw` fill replaces pixels; alpha is ignored). | Spec 137–140; [SO 43618910](https://stackoverflow.com/questions/43618910/pil-drawing-a-semi-transparent-square-overlay-on-image); [Pillow #2496](https://github.com/python-pillow/Pillow/issues/2496) |
| Bake arrow | `ImageDraw.line` + triangle `polygon` at the head. Head length `max(ARROWHEAD_MIN_PX, stroke_width * ARROWHEAD_LENGTH_FACTOR)`; half-angle `ARROWHEAD_ANGLE_RAD`. | Spec 137; [Pillow ImageDraw](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html) |
| Bake text | `ImageFont.truetype` over `FONT_CANDIDATES` in `%WINDIR%/Fonts`, else `load_default()`. | Spec 336 |
| Black frame | Convert to `L`; `ImageStat.Stat.mean[0] <= BLACK_LUM_MAX` or 0×0 / empty file → `CaptureFailedError`. Do not write a success PNG. | Spec 187, 304; [Pillow ImageStat](https://pillow.readthedocs.io/en/stable/reference/ImageStat.html) |
| Timestamp | `datetime.now()` (local, not UTC) + `TIMESTAMP_FORMAT`; collision `_2`, `_3` before `.png`. | Spec 169, 362 |
| Register | Idempotent: same resolved `original_path` + same `file_size` returns the existing row; size change refreshes probe fields. Do **not** raise 409 on re-register. Interactive second Pending still `CaptureRequestConflictError`. | Spec 353 |
| Inbox | `Path.resolve()` then `relative_to(inbox.resolve())`; `ValueError` / not absolute → `InboxPathError`. Non-recursive `SCAN_EXTENSIONS`. | Spec 231–232, 350 |
| Scan prune | Missing original file → delete the row (inbox is source of files). | Spec 232 |
| Remove | Delete original + sidecar + annotated files, then the row (unlike Convert clear). | Spec 150, 360 |
| Empty annotate | Empty `annotations` list removes annotated file + sidecar and clears those fields. | Spec 274 |
| Highlight opacity | Inclusive `[HIGHLIGHT_OPACITY_MIN, HIGHLIGHT_OPACITY_MAX]`. Outside range → `AnnotationValidationError` at VO construction (MEU-34). | Spec 269 |
| Annotation clamp | `CaptureService.annotate_and_save` clamps integer coords to `[ANNOTATION_CLAMP_MIN, shot.width]` / `[ANNOTATION_CLAMP_MIN, shot.height]` **before** `ImageAnnotatePort.bake`. Domain VOs may hold out-of-bounds ints; bake must not receive them. | Spec 274 |
| Settings | MEU-34 adds `SETTING_NS`. MEU-36 adds `CAPTURE_KEYS`. REST is MEU-37. | Spec 417–426 |
| UoW | Short scopes; one commit per register/scan/annotate/remove/request transition. | Local Canon Phase 2/3 |
| G29 | Engine wiring = tables + adapter + service. API/MCP/GUI are scheduled MEU-37–39, not stubs this session. tmp-SQLite smoke AC-36.13. | Local Canon p8 AC-30.12; G29 |
| 4A | skip — no renderer controls | create-plan §4A |
| ShareX | Read flow only. Do not paste C#. | Spec 540–584; Golden Rule 5 |

---

## Proposed Changes

### MEU-34 — `domain-capture`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| Python `CaptureShot` / `CaptureRequest` / `Annotation` / `BBox` constructors | frozen dataclasses + `require_*` | enums `.name`; absolute `Path`; `CAPTURE_MIN_EDGE_PX`; `TEXT_MAX_CHARS`; `NAMED_COLORS` or `#RRGGBB`; highlight opacity `[HIGHLIGHT_OPACITY_MIN, HIGHLIGHT_OPACITY_MAX]` | extra fields → `TypeError` |
| REST / MCP / GUI / overlay IPC | — | — | **deferred** MEU-37 / MEU-38 / MEU-39 |

Python `assert` is not validation.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-34.1 | unit | StrEnums `CaptureSource`, `CaptureRequestStatus`, `AnnotationType` match named-set member lists; persist `.name`; `AnnotationType.to_wire()` equals `ANNOTATION_WIRE`. `TEST_DOMAIN` `ENUM_MEMBERS` includes the three enums. | Spec 202–208 | unknown member construction succeeds → fail |
| AC-34.2 | unit | `QUEUE_NAMES` does **not** contain `FORBIDDEN_QUEUE_NAME`. `QueueRuntime(queue_name=FORBIDDEN_QUEUE_NAME, …)` raises `ValidationError`. | Spec 200 | `"captures"` accepted → fail |
| AC-34.3 | unit | `SETTING_NAMESPACES` includes `SETTING_NS`. `Setting(namespace=SETTING_NS, …)` constructs. Unknown namespace still `ValidationError`. | Spec 419 | `capture` rejected → fail |
| AC-34.4 | unit | `CaptureShot` fields == `CAPTURE_SHOT_COLUMNS`; frozen; extra kwarg `TypeError`; relative `original_path` → `ValidationError`; width/height/file_size `>= 0`. | Spec 212–226 | relative path accepted → fail |
| AC-34.5 | unit | `CaptureRequest` fields == `CAPTURE_REQUEST_COLUMNS`; `shot_id` optional until Completed; extra kwarg `TypeError`. | Spec 236–246 | extra field accepted → fail |
| AC-34.6 | unit | `CAPTURE_REQUEST_TRANSITIONS` is exhaustive over `CaptureRequestStatus` (every member is a key). Pending → Completed/Cancelled/Expired only. | Spec 248–255 | missing `Expired` key → fail |
| AC-34.7 | unit | Annotation VOs: unknown type/color → `AnnotationValidationError`; empty text or length `> TEXT_MAX_CHARS` → `AnnotationValidationError`; negative rect size → `AnnotationValidationError`; extra field `TypeError`. | Spec 259–274, 307 | `color="purple"` accepted → fail |
| AC-34.8 | unit | `BBox` width or height `< CAPTURE_MIN_EDGE_PX` → `ValidationError`. | Spec 334, 409 | 7×7 bbox accepted → fail |
| AC-34.9 | unit | `ImageProbe` fields `width`, `height`, `file_size`; extra kwarg `TypeError`. | Spec 293 | missing field required → fail |
| AC-34.10 | unit | `ScreenCapturePort` has `capture_fullscreen` / `capture_region`; `ImageAnnotatePort` has `probe` / `bake`. Signatures take `Path` + `BBox` / `Sequence[Annotation]`. | Spec 276–295 | `mss` imported from `packages/core` → fail |
| AC-34.11 | unit | Errors `CaptureNotSupportedError`, `CaptureFailedError`, `InboxPathError`, `AnnotationValidationError`, `CaptureRequestConflictError` exist. `HotkeyConflictError` is **not** defined in Python. | Spec 299–310 | `HotkeyConflictError` class exists → fail |
| AC-34.12 | unit | `TEST_DOMAIN` `INFRA_NAMES` includes `PIL_FORBIDDEN`. No file under `packages/core` imports those modules. | Local Canon AC-5.16; Spec 340 | `from PIL import Image` in core → fail |
| AC-34.13 | unit | Highlight `opacity` outside inclusive `[HIGHLIGHT_OPACITY_MIN, HIGHLIGHT_OPACITY_MAX]` → `AnnotationValidationError`. Bounds 0 and 1 construct. | Spec 269 | `opacity=2` constructs → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Enums, entities, ports, errors | Spec | 09 §Domain |
| Highlight opacity bounds | Spec | 09:269; `HIGHLIGHT_OPACITY_*` |
| No `QueueRuntime` for captures | Spec | 09:200 |
| `SETTING_NS` this MEU | Spec + sequencing | service needs namespace before REST |
| Inbox containment | Spec | enforced in MEU-36 (needs settings); domain requires absolute path only |
| REST/MCP/GUI validation | deferred | MEU-37–39 |

#### Control bindings

| AC | Observable | Traceable chain | Negative oracle |
|----|------------|-----------------|-----------------|
| AC-34.2 | `ValidationError` from `QueueRuntime.__post_init__` | `QueueRuntime(queue_name=FORBIDDEN_QUEUE_NAME)` | instance constructed → fail |
| AC-34.6 | `CAPTURE_REQUEST_TRANSITIONS.keys()` | `domain/capture.py` import | `set(CaptureRequestStatus) - keys` nonempty → fail |
| AC-34.7 | `AnnotationValidationError` | `Annotation` / typed VO ctor | unknown color constructs → fail |
| AC-34.8 | `ValidationError` | `BBox(...)` | 7 px edge constructs → fail |
| AC-34.11 | `getattr(errors, "HotkeyConflictError", None)` | `domain/errors.py` | class present → fail |
| AC-34.12 | ast imports ∩ `PIL_FORBIDDEN` | core `rglob("*.py")` | nonempty hit list → fail |
| AC-34.13 | `AnnotationValidationError` | Highlight VO ctor | `opacity=2` constructs → fail |

Atomicity: constructors are single statements. Exhaustiveness: `CAPTURE_REQUEST_TRANSITIONS` over owned enum. Fail-closed: unknown annotation type/color.

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/enums.py` | modify | capture enums |
| `packages/core/src/avkit_core/domain/capture.py` | new | shot, request, annotations, BBox, ImageProbe, transitions |
| `packages/core/src/avkit_core/domain/settings.py` | modify | `SETTING_NS` |
| `packages/core/src/avkit_core/domain/errors.py` | modify | capture errors; do not add HotkeyConflictError |
| `packages/core/src/avkit_core/ports/capture.py` | new | ScreenCapturePort, ImageAnnotatePort |
| `tests/unit/test_domain_capture.py` | new | AC-34.* |
| `tests/unit/test_domain.py` | modify | `ENUM_MEMBERS`, `SETTING_NAMESPACES`, `INFRA_NAMES` |

---

### MEU-35 — `infra-capture`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| SQLite `capture_shots` / `capture_requests` | ORM row ↔ entity mapper | TEXT enum `.name`; Path as TEXT; unique `original_path` | unknown columns not written |
| mss grab region dict | `CaptureAdapter` | ints; `CAPTURE_MIN_EDGE_PX` | extra mss keys only from BBox |
| Pillow bake list | `CaptureAdapter.bake` | domain Annotation VOs already validated | extra annotation keys never reach Draw |
| REST/MCP | — | — | deferred MEU-37/38 |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-35.1 | integration | Tables `capture_shots` and `capture_requests` exist; **no** STI `jobs` table. Unique index on `original_path`; indexes `created_at`, `status`, `expires_at`. `TEST_SQLITE` `TABLES` includes both names. | Spec 316–325 | `jobs` table created → fail |
| AC-35.2 | integration | Greenfield CREATE in `models.py`; `migrations.py` `CREATE TABLE IF NOT EXISTS` no-op-safe for both tables. | Spec 320 | second apply raises → fail |
| AC-35.3 | integration | `UnitOfWork` has `UOW_CAPTURE_ATTRS`. `capture_shots`: add/get/list/save/delete/`get_by_path`. `capture_requests`: add/get/save/`get_pending_request`. | Spec 327 | missing `get_by_path` → fail |
| AC-35.4 | integration | Columns == named-set column lists; round-trip a fully populated `CaptureShot` and `CaptureRequest` through real UoW. | Spec 216–246 | dropped `sidecar_path` on save → fail |
| AC-35.5 | integration | Infrastructure `pyproject.toml` declares `pillow` and `mss`. Core still has zero `PIL_FORBIDDEN` imports. | Spec 340 | pillow only in core extra → fail |
| AC-35.6 | unit | `capture_fullscreen` calls fake mss `grab` with `monitors[MSS_VIRTUAL_INDEX]`; writes PNG; returns `ImageProbe`. | Spec 329–334; mss docs | grab of `monitors[1]` as fullscreen → fail |
| AC-35.7 | unit | `capture_region` grab dict uses `left`/`top`/`width`/`height` from `BBox`. Width/height `< CAPTURE_MIN_EDGE_PX` does not call grab. | Spec 334; mss examples | 7 px grab invoked → fail |
| AC-35.8 | unit | `sys.platform != "win32"` → `CaptureNotSupportedError` before grab. | Spec 303 | Linux grab succeeds → fail |
| AC-35.9 | unit | All-black / empty bitmap → `CaptureFailedError`; no success PNG left at `output_path`. | Spec 187, 304 | black PNG registered as success → fail |
| AC-35.10 | unit | `probe` opens with Pillow; non-image / missing file → `InboxPathError`. | Spec 335, 305 | text file probes as image → fail |
| AC-35.11 | integration | `bake` writes `output_path`; SHA256 of original bytes unchanged. | Spec 233, 336 | original mutated → fail |
| AC-35.12 | unit | Highlight on a white 32×32 fixture changes mean luminance via alpha composite (not opaque replace of the rect to the named color). | Spec 139; SO 43618910 | rect pixels become solid named color at opacity 0.4 → fail |
| AC-35.13 | unit | Arrow bake draws a line whose head triangle uses `ARROWHEAD_*`. Text bake uses `FONT_CANDIDATES` then default. | Spec 137, 336 | no polygon / no line → fail |
| AC-35.14 | unit | New adapter logs `module=LOG_MODULE`. `INFRA_LAYOUT` includes `INFRA_CAPTURE_REL`. `UOW_ATTRIBUTES` includes `UOW_CAPTURE_ATTRS` and existing `conversion_jobs` (catch-up: the attr already exists on SqlAlchemyUnitOfWork). FakeUoW in `TEST_SERVICES` and `TEST_SVC_CONV` grow the two capture repos. | Spec 338; Local Canon UoW | UoW missing `capture_shots` → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Ninth/tenth tables + UoW | Spec | 09 §Infrastructure |
| mss grab recipe | Research-backed | mss usage + examples URLs |
| Bake geometry | Research-backed | Pillow ImageDraw + alpha_composite |
| Live display grab | Spec | fake mss in unit; live mss not a ship gate this session |
| REST bytes cap 15 MiB | deferred | MEU-37 |

#### Control bindings

| AC | Observable | Traceable chain | Negative oracle |
|----|------------|-----------------|-----------------|
| AC-35.1 | sqlite `sqlite_master` names | `models.py` CREATE → engine | `"jobs" in tables` → fail |
| AC-35.6 | fake mss last grab target | `CaptureAdapter.capture_fullscreen` → `mss.grab` | target ≠ `monitors[0]` → fail |
| AC-35.7 | fake mss call count | `capture_region` undersize | grab_count ≠ 0 → fail |
| AC-35.9 | `CaptureFailedError` + `output_path.exists()` | `capture_fullscreen` → ImageStat | exists True after black → fail |
| AC-35.11 | SHA256 original before/after bake | `bake` → Pillow save | hashes differ → fail |
| AC-35.12 | mean of highlight rect vs named color | `bake` highlight opacity 0.4 | pixels == opaque named RGB → fail |

Atomicity: each UoW `commit` is the session commit. Fail-closed: non-Windows and black frame do not write success files.

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/infrastructure/pyproject.toml` | modify | pillow, mss |
| `packages/infrastructure/src/avkit_infra/database/models.py` | modify | CaptureShotRow, CaptureRequestRow |
| `packages/infrastructure/src/avkit_infra/database/migrations.py` | modify | IF NOT EXISTS both tables |
| `packages/infrastructure/src/avkit_infra/database/mappers.py` | modify | capture mappers |
| `packages/infrastructure/src/avkit_infra/database/repositories.py` | modify | capture repos |
| `packages/infrastructure/src/avkit_infra/database/unit_of_work.py` | modify | `UOW_CAPTURE_ATTRS` |
| `packages/core/src/avkit_core/ports/storage.py` | modify | CaptureShotRepository, CaptureRequestRepository, UoW attrs |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | new | mss + Pillow |
| `tests/unit/test_capture_adapter.py` | new | AC-35.* |
| `tests/integration/test_sqlite_uow.py` | modify | `TABLES`, `UOW_ATTRIBUTES`, `INFRA_LAYOUT` |
| `tests/unit/test_services.py` | modify | FakeUoW capture repos |
| `tests/unit/test_conversion_service.py` | modify | FakeUoW capture repos |

---

### MEU-36 — `svc-capture`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `packages/core/src/avkit_core/services/capture.py` | Python domain types (wire mapping is MEU-37) | absolute paths inside inbox; Annotation VOs; clamp coords to `[ANNOTATION_CLAMP_MIN, width]` / `[ANNOTATION_CLAMP_MIN, height]` before bake | unexpected kwargs → `TypeError` |
| Settings `capture.*` | `SETTINGS_KEY_TABLE` | `CAPTURE_KEYS` / `CAPTURE_DEFAULTS` | unknown leaf → `ValidationError` (existing SettingsService) |
| REST body | — | — | deferred MEU-37 |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-36.1 | integration | `scan_inbox` lists only `SCAN_EXTENSIONS`, non-recursive; upserts by resolved path with source `Scan`. | Spec 350 | `.gif` or nested folder file inserted → fail |
| AC-36.2 | integration | Scan deletes rows whose original file vanished. | Spec 232, 350 | missing file still listed → fail |
| AC-36.3 | unit | `list_shots` newest `created_at` desc, then filename. Calls scan first. | Spec 127, 351 | oldest first → fail |
| AC-36.4 | unit | `register_shot`: not absolute / outside inbox / `..` escape → `InboxPathError`. Same path + same size returns existing id (idempotent). | Spec 231, 353 | `../` path inserts → fail |
| AC-36.5 | unit | `capture_fullscreen` / `capture_region` write `{inbox}/{TIMESTAMP_FORMAT}.png` using **local** `datetime.now()`; collision `_2` then `_3`; sources `McpFullscreen` / `McpRegion`. | Spec 354, 362 | UTC stem or overwrite without suffix → fail |
| AC-36.6 | unit | `request_interactive` inserts Pending `expires_at = now + REQUEST_TTL_S`. Second Pending → `CaptureRequestConflictError`. | Spec 257, 355 | two Pending rows → fail |
| AC-36.7 | unit | `expire_stale_requests` (from list/get) Pending past ttl → Expired. | Spec 254, 357 | stale stays Pending → fail |
| AC-36.8 | integration | `complete_request` registers path and sets Completed + `shot_id`. `cancel_request` → Cancelled, no shot. | Spec 356 | complete without path succeeds → fail |
| AC-36.9 | integration | `annotate_and_save` writes sidecar `SIDECAR_VERSION` + `ANNOTATION_WIRE` list and bakes `ANNOTATED_SUFFIX`. Empty list deletes annotated + sidecar and clears fields. Extra sidecar keys ignored on **read**; write path uses domain VOs only. | Spec 261–274, 358 | empty list leaves annotated PNG → fail |
| AC-36.10 | unit | `read_image(id, original\|annotated)`; annotated missing → `NotFoundError`. Unknown id → `NotFoundError`. | Spec 359, 310 | missing annotated returns original bytes → fail |
| AC-36.11 | integration | `remove` deletes original + sidecar + annotated then the row. File-delete count ≥ 1 when files existed. | Spec 150, 360 | row gone, files remain → fail |
| AC-36.12 | unit | `SETTINGS_KEY_TABLE` has `CAPTURE_KEYS` with `CAPTURE_DEFAULTS`. Unknown capture leaf → `ValidationError`. | Spec 421–426 | missing `inbox_dir` → fail |
| AC-36.13 | integration | G29 tmp-SQLite: register + list via real UoW. Download/TTS/Conversion service **source** does not insert `CaptureShot` / call `CaptureService`. | Spec 234; Local Canon G29 | `DownloadService` writes capture row → fail |
| AC-36.14 | unit | `annotate_and_save` clamps integer coords to `[ANNOTATION_CLAMP_MIN, shot.width]` / `[ANNOTATION_CLAMP_MIN, shot.height]` before `bake`. Inclusive: `x==width` is unchanged. | Spec 274 | FakeAnnotatePort `bake` receives `x > width` → fail |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Scan/register/grab/request/annotate/remove | Spec | 09 §Service |
| Annotation coordinate clamp | Spec | 09:274; `ANNOTATION_CLAMP_MIN` |
| Idempotent register | Spec | 09:353 allows 409 **or** idempotent — lock idempotent |
| Converter/TTS/download isolation | Spec | 09:234 |
| REST 15 MiB / MCP image content | deferred | MEU-37 / MEU-38 |
| Electron overlay write | deferred | MEU-39 calls `register_shot` |

#### Control bindings

| AC | Observable | Traceable chain | Negative oracle |
|----|------------|-----------------|-----------------|
| AC-36.4 | `InboxPathError` | `CaptureService.register_shot` → resolve/relative_to | `..` path creates row → fail |
| AC-36.6 | `CaptureRequestConflictError` | `request_interactive` twice | second returns 201-equivalent row → fail |
| AC-36.9 | sidecar JSON + annotated exists | `annotate_and_save` → adapter.bake | empty list, annotated exists → fail |
| AC-36.11 | `Path.exists()` after remove | `remove` → unlink then repo.delete | files remain → fail |
| AC-36.13 | inspect source of download/tts/conversion services | module source | `CaptureService` / `capture_shots` substring → fail |
| AC-36.14 | last bake annotations coords | `annotate_and_save` → FakeAnnotatePort | `x > shot.width` in bake args → fail |

Atomicity: each mutating method is one UoW enter/commit. Fail-closed: unknown settings leaf; path escape.

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/capture.py` | new | CaptureService |
| `packages/core/src/avkit_core/services/settings.py` | modify | `CAPTURE_KEYS` |
| `tests/unit/test_capture_service.py` | new | AC-36.* |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| REST `/captures` + OpenAPI + `capture` settings HTTP + image 15 MiB | deferred | MEU-37 | grouping Session 17; Spec 368–432 |
| MCP `avkit_capture` (including image-bytes exception) | deferred | MEU-38 | grouping Session 17; Spec 434–455 |
| Capture page, rail, tray, F2, overlay, Wave 9, Settings Capture card | deferred | MEU-39 | grouping Session 18; Spec 81–182, 158–187, 459–474 |
| In-overlay arrows / ShapeManager | out-of-scope | — | Spec 484; 09:46; ShareX map 574–575 |
| Window / fullscreen GUI buttons, extra tools, timer, uploaders, GIF, scrolling, SSE, recursive inbox, macOS/Linux overlay | out-of-scope | — | Spec named deferrals 478–492 |
| Session 8c console polish | out-of-scope | — | MEU-27 grouping 8c; Spec 492; do not start |
| Add `FORBIDDEN_QUEUE_NAME` to `QUEUE_NAMES` | out-of-scope | — | Spec 200 |
| Paste ShareX / nomacs / Shotik / MCP-server C# or Python | out-of-scope | — | Spec 524; BUILD_PLAN Golden Rule 5; ShareX map 544 |
| Invent extra MEU IDs / pack MEU-37–39 | out-of-scope | — | grouping Session 16 MEU-34–36 only |
| Rewrite FastAPI/MCP/chrome this session | out-of-scope | — | grouping Session 16 layer/files |
| Live unattended mss of the developer desktop as a blocking test | out-of-scope | — | Spec 512 (fake port in unit; live is integration-only, not this session’s ship gate) |

---

## BUILD_PLAN.md Audit

This project **does** require hub updates after execution (H1-3 / WP-HUB): bind MEU-34–36 `execution_plan`; append `docs/execution/plans/2026-08-26-p9-capture-engine/` to phase `"9"` `execution_plans`; set unique hub `Next:` to `HUB_NEXT_AFTER` (`/create-plan p9-capture-api-mcp`). Do not hand-edit AUTOGEN tables.

Planning-time check (no SSOT writes until H1):

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re,sys; t=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), t); print('hub_next', hits); sys.exit(0 if hits else 1)" *> C:/Temp/av-kit/build-plan-audit.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/build-plan-audit.txt; exit $code
```

Execution validation is the `SSOT_PLAN_BOUND` command in `task.md` row 10.

---

## Verification Plan

### 1. MEU-34 unit
```powershell
rtk proxy uv run pytest tests/unit/test_domain_capture.py tests/unit/test_domain.py -x --tb=short -v *> C:/Temp/av-kit/pytest-meu-34.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-meu-34.txt | Select-Object -Last 40; exit $code
```

### 2. MEU-35 unit + sqlite integration
```powershell
rtk proxy uv run pytest tests/unit/test_capture_adapter.py tests/integration/test_sqlite_uow.py tests/unit/test_services.py tests/unit/test_conversion_service.py -x --tb=short -v *> C:/Temp/av-kit/pytest-meu-35.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-meu-35.txt | Select-Object -Last 40; exit $code
```

### 3. MEU-36 unit
```powershell
rtk proxy uv run pytest tests/unit/test_capture_service.py tests/unit/test_services.py tests/unit/test_conversion_service.py -x --tb=short -v *> C:/Temp/av-kit/pytest-meu-36.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-meu-36.txt | Select-Object -Last 40; exit $code
```

### 4. Types / lint / anti-placeholder (touched packages)
**Scheduled in `task.md` rows 3, 6, 9, and H1-2** via `assert-meu-scoped-gate.ps1` (`GATE_PYTEST_*` + `GATE_PYRIGHT_*` + `GATE_RUFF_*` + `assert-anti-placeholder.ps1`). Do not treat this section as an unscheduled check.

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-26-p9-capture-engine/assert-meu-scoped-gate.ps1 -Meu all *> C:/Temp/av-kit/meu-all-gate.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/meu-all-gate.txt | Select-Object -Last 40; exit $code
```

### 5. OpenAPI
**Skip this session** — no `API_TREE` edits. H1-4 runs `assert-openapi-skip.ps1` against `API_BASELINE` (written at row 1). Missing baseline or hash drift → fail (G8 required). Do not use git.

### 6. Regression (H1-2)
Same command as §4 (`-Meu all`): pytest unit+integration, pyright core+infrastructure, ruff, anti-placeholder/G36.

### 7. Independent-review provenance (H1-7 / H2-4)
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-26-p9-capture-engine/assert-exec-review-dispatch.ps1 *> C:/Temp/av-kit/exec-review-dispatch.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/exec-review-dispatch.txt; exit $code }; rtk proxy uv run python tools/check_exec_review.py --self-test *> C:/Temp/av-kit/exec-review-selftest.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/exec-review-selftest.txt; exit $code }; rtk proxy uv run python tools/check_exec_review.py --review-file .agent/context/handoffs/2026-08-26-p9-capture-engine-implementation-critical-review.md --expected-mode implementation --expected-target docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md --max-round 6 *> C:/Temp/av-kit/exec-review.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/exec-review-dispatch.txt; Get-Content C:/Temp/av-kit/exec-review-selftest.txt; Get-Content C:/Temp/av-kit/exec-review.txt; exit $code
```

---

## Open Questions

None remaining as human gates. Forks resolved **Research-backed** in Implementation locks.

**Instruction conflict (recorded, not a product fork):** `AGENTS.md` P0 and `TASK-TEMPLATE.md` require `rtk proxy` (or verified native RTK) on executable segments. `.agent/docs/output-evidence-policy.md` and `.agent/docs/commands.md` call RTK optional if missing from PATH. This plan follows **P0 + TASK-TEMPLATE + plan-review Finding 5**: every task validation uses `rtk proxy`. Missing `rtk` at execution is `[B]` (missing dependency), not a silent drop of the prefix.

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| Grab library | mss (`GRAB_BACKEND`) | Spec 293; [mss usage](https://python-mss.readthedocs.io/latest/usage.html) | BBox space matches Spec; multi-monitor virtual desktop at index 0 | Windows-first (already locked) | ✅ |
| | Pillow `ImageGrab` | Spec 333 “or” | fewer deps | coordinate space not the Spec mss lock | ❌ |
| Highlight bake | RGBA overlay + `alpha_composite` | [SO 43618910](https://stackoverflow.com/questions/43618910/pil-drawing-a-semi-transparent-square-overlay-on-image); [Pillow #2496](https://github.com/python-pillow/Pillow/issues/2496) | real translucency | extra buffer | ✅ |
| | `ImageDraw` fill on RGB | Pillow default | simpler | alpha ignored; opaque replace | ❌ |
| Re-register same path | Idempotent same size | Spec 353 | Electron retry-safe | no 409 | ✅ |
| | Always 409 | Spec 353 alt | stricter | overlay retries fail | ❌ |

---

## Emerging standards (this session)

| ID | Apply? | How |
|----|--------|-----|
| G8 | no (skip with hash) | `API_TREE` hash == `API_BASELINE`; G8 applies in MEU-37 |
| G29 | yes | AC-36.13 + wiring checklist (DB+adapter+service this session; API/MCP/GUI scheduled) |
| G36 | yes | no skip/xfail neutralization in Green |
| M2/M3/M7 | no | MCP is MEU-38 |
| G5/G11/G21/G31 | no | GUI is MEU-39 |
| M5 | yes | Red oracle scripts |
| UX2 | n/a | no renderer |

---

## Stop conditions

- Plan review round cap 3 without `approved`
- All reviewer rungs unavailable
- Reviewer human-decision question
- During execution: `[B]` only with external-error receipt (missing Pillow/mss install is a Green dependency add, not `[B]`)

---

## Research References

- [09-screenshot-capture.md](../../../build-plan/09-screenshot-capture.md)
- ShareX source map in that file (intent, not code)
- [python-mss usage](https://python-mss.readthedocs.io/latest/usage.html)
- [python-mss region examples](https://python-mss.readthedocs.io/v10.2.0/examples.html)
- [Pillow ImageDraw](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html)
- [Pillow ImageStat](https://pillow.readthedocs.io/en/stable/reference/ImageStat.html)
- [Pillow #2496 fill alpha](https://github.com/python-pillow/Pillow/issues/2496)
- Local Canon: `ConversionJob` / `conversion_jobs` / `ConversionService` / `SETTINGS_KEY_TABLE`; p3 G29 tmp-SQLite
