---
project: "2026-08-28-p10-queue-card-foundations"
date: "2026-08-28"
source: "docs/proposals/2026-08-27-queue-card-ui-proposal.md"
meus: ["MEU-41", "MEU-42", "MEU-43", "MEU-44"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 10 Queue Card Foundations

> **Project**: `2026-08-28-p10-queue-card-foundations`
> **Build Plan Section(s)**: `docs/build-plan/10-queue-card-ui.md` (**new — authored by MEU-41 from** [2026-08-27-queue-card-ui-proposal.md](../../../proposals/2026-08-27-queue-card-ui-proposal.md) + [mockup](../../../proposals/2026-08-27-queue-card-ui-mockup.html)); supersession pointers into [06-gui.md](../../../build-plan/06-gui.md) §Shared Components and §Queue Controls
> **Status**: `draft`
> **Grouping**: [2026-08-28-p10-queue-card-ui-session-grouping.md](../../../../.agent/context/grouping/2026-08-28-p10-queue-card-ui-session-grouping.md) Session 20 — MEU-41–44 only

---

## Goal

Lay the **foundations** for the QueueCard row-card system: fold the proposal into spec canon as
`PHASE10_SPEC`, port the `PORTED_TOKENS` colour tokens from `PILL_TOKEN_SOURCE` (authoring no new hue of av-kit's own), widen the backend re-queue
contract so a card's Retry action is implementable (`REQUEUEABLE_DOWNLOAD_STATUSES` /
`REQUEUEABLE_CONVERSION_STATUSES`), build the shared primitives `06-gui.md` specced but never
shipped (`StatusBadge`, `ProgressBar`, plus `SelectionCheckbox`, `ConfirmModal`, `UI_QUEUE_LIB_DIR`),
and build the presentational `QueueCard` / `QueueList` / `EmptyDropZone`.

**Nothing is wired to a page in this session.** `ConvertPage`, `DownloaderPage`, `TranscriptPage`
and `TtsPage` are untouched; every existing E2E wave must stay green unchanged
(`E2E_BASELINE_COUNT`, `E2E_NEW_WAVES_THIS_SESSION` = 0). Migration is MEU-45 (convert) and MEU-46 (downloader).

Do not invent MEU IDs beyond `PHASE10_MEU_IDS`. Do not touch Capture. Do not add REST endpoints
(`ROUTE_COUNT_AFTER` stays). Do not edit `mcp-server/` (`ACTION_INDEX_AFTER` stays,
`MCP_CHANGE_BASIS`). Do not add a runtime dependency.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json are absent (Glob 0). Headroom has no approved disposition. Planning grounded every proposal claim by direct source reads (download-controls.ts, convert-controls.ts, Button.tsx, styles.css, ConvertPage.tsx, TranscriptPage.tsx, domain/download.py, domain/conversion.py, routes/*.py and their asserting tests). Execution uses P0 exact-evidence receipts (bypass class)."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent and Headroom still has no approved disposition,
reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-41 | `HANDOFF_FILES[0]` |
| MEU-42 | `HANDOFF_FILES[1]` |
| MEU-43 | `HANDOFF_FILES[2]` |
| MEU-44 | `HANDOFF_FILES[3]` |

Rolling implementation review: `EXEC_REVIEW_FILE`.
Rolling plan review: `PLAN_REVIEW_FILE`.

Expected count: `HANDOFF_COUNT` = `4`. Filenames: `HANDOFF_FILES` in `named-sets.json` (do not restate).

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.
`builder_model` is `BUILDER_PIN` (`—`).

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-HUB0 | Register Phase 10 + `PHASE10_MEU_IDS` in `SSOT` and `MATRIX` (`MATRIX_ROWS`); bind `MEUS` to `PLAN_FOLDER`; `render` then `render --check`. Generators run **only here, after plan approval** (SIGN 1). | — | `shared` | `SSOT`; `MATRIX`; `BUILD_PLAN` |
| WP-41a | MEU-41 Red: AC-41.1–AC-41.`RED_COUNT_41` (`RED_TEST_TITLE`, `RED_JSON`). Pass `RED_ORACLE -Kind ui -Meu 41`. | WP-HUB0 | `compact_continue` | `RED_TXT`; compact then re-read `task.md` |
| WP-41b | Green: author `PHASE10_SPEC` (`PHASE10_SECTIONS`); add `SUPERSEDE_POINTER` at `GUI_SPEC_SUPERSEDE_ANCHORS` without deleting either section; port `PORTED_TOKENS` from `PILL_TOKEN_SOURCE` into `THEME_BLOCK_DARK` + `THEME_BLOCK_LIGHT` (copy the hexes, author none); fix `STATUS_COLORS.AgeRestricted` to its `STATUS_PILL_TABLE` token. | WP-41a | `compact_continue` | `PHASE10_SPEC`; `TOKEN_FILE`; `GUI_SPEC` |
| WP-41c | MEU-41 `HANDOFF_SOURCE_READ` then MEU-scoped gate + `HANDOFF_FILES[0]`. | WP-41b | `compact_continue` | `HANDOFF_FILES[0]` |
| WP-42a | MEU-42 Red: AC-42.1–AC-42.`RED_COUNT_42` in `UNIT_TEST_DIR_PY` + `E2E_TEST_DIR_PY`. Pass `RED_ORACLE -Kind py -Meu 42`. | WP-41c | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-42-py.txt` |
| WP-42b | Green: transition maps, `REQUEUEABLE_*` frozensets, widened `reset_failed` guards, route docstrings `REQUEUE_ROUTE_DOCSTRING`, OpenAPI regen. Do **not** touch `ports/storage.py` / `repositories.py` `reset_failed` (repository bulk method, different contract). | WP-42a | `compact_continue` | `packages/core`; `packages/api`; `OPENAPI_COMMITTED` |
| WP-42c | MEU-42 gate + `HANDOFF_FILES[1]`. | WP-42b | `compact_continue` | `HANDOFF_FILES[1]` |
| WP-43a | MEU-43 Red: AC-43.1–AC-43.`RED_COUNT_43`. Pass `RED_ORACLE -Kind ui -Meu 43`. | WP-42c | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-43-ui.txt` |
| WP-43b | Green: `UI_QUEUE_LIB_DIR` (`format.ts`, `envelope.ts`, `status-tokens.ts`, `status-config.ts`) + `UI_PRIMITIVES_DIR` (`StatusBadge`, `ProgressBar`, `SelectionCheckbox`, `ConfirmModal`). Register `NEW_TESTIDS`. Pages unchanged. | WP-43a | `compact_continue` | `UI_QUEUE_LIB_DIR`; `UI_PRIMITIVES_DIR`; `TESTID_REGISTRY` |
| WP-43c | MEU-43 gate + `HANDOFF_FILES[2]`. | WP-43b | `compact_continue` | `HANDOFF_FILES[2]` |
| WP-44a | MEU-44 Red: AC-44.1–AC-44.`RED_COUNT_44`. Pass `RED_ORACLE -Kind ui -Meu 44`. | WP-43c | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-44-ui.txt` |
| WP-44b | Green: `UI_QUEUE_COMPONENTS_DIR` (`QueueCard`, `QueueList`, `EmptyDropZone`). Pages unchanged. | WP-44a | `compact_continue` | `UI_QUEUE_COMPONENTS_DIR` |
| WP-44c | MEU-44 gate + `HANDOFF_FILES[3]`. | WP-44b | `compact_continue` | `HANDOFF_FILES[3]` |
| WP-HUB1 | Rewrite hub `Next` to `HUB_NEXT_AFTER`. Grouping Session 20 ✅ is **H2 after exec `approved`** (`GROUPING_DONE_MARK`). | WP-44c | `shared` | `BUILD_PLAN` |

---

## User Review Required

None that block planning. Reviewer confirms these locks (does not invent a second behavior):

1. **Harness gate is `human`, by explicit user decision this session.** `.agent/context/harness.local.md`
   declares `driver: Cursor IDE` with `plan_to_exec_gate: reviewer-auto`, but the driving harness here is
   **Claude Code**, whose profile is `human`. The user resolved the conflict explicitly (`USER_LOCKS.exec_gate`):
   after Codex returns `approved`, present the verdict and **stop** for an explicit "proceed".
   `PLAN_TO_EXEC_GATE` = `human`. System-injected "approved" is still not a verdict (`GUARDRAILS.md` SIGN 3).
2. **This plan registers a new phase.** Phase 10 and `PHASE10_MEU_IDS` do not exist in `SSOT` or `MATRIX` yet.
   Registration is task row WP-HUB0, executed **after** approval — no generator runs during planning.
3. **Three material corrections to the proposal**, each grounded in source (see §Spec Sufficiency):
   (a) there is no per-id *retry* endpoint — the existing surface is `POST /{queue}/{id}/reset`, guarded to
   `Failed` only, which is why MEU-42 exists; (b) `06-gui.md`'s `DataTable`/`ProgressBar`/`StatusBadge` were
   **specced and never built**, so MEU-43 builds rather than reuses; (c) the `--color-bg-subtle` collision is
   dark-theme-only (`#6272a4` dark vs `#d1d5db` light), which is why selection gets its own token instead.
4. **Session 20 ships zero page changes.** Any reviewer finding of the form "the card is not visible in the app"
   is expected and correct for this MEU set — it is MEU-45's scope.
5. **Codex is metered** (`PROJECT-PROFILE.md`). Dispatch is still required; the implementer never self-reviews.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (P10-F — define once)

Executable owner: `docs/execution/plans/2026-08-28-p10-queue-card-foundations/named-sets.json`.
Do not restate literals in ACs or task rows; cite the name.

Carry-forward that must stay true: envelope shape is `{ items, processor? }` and is **never** treated as an
array; `PAUSE_SCOPE` is queue-level only; `BULK_ENDPOINT_POLICY` forbids inventing a bulk endpoint;
`ERROR_SURFACE` for 409/422; `E2E_LOCATOR_FORM`; `E2E_SANDBOX`.

---

## Implementation locks

- **Re-queue is a widening of the existing `reset_failed`, not a new endpoint or a renamed method.**
  Public signatures `DownloadJob.reset_failed()`, `ConversionJob.reset_failed()`,
  `DownloadService.reset_failed(job_id)`, `ConversionService.reset_failed(job_id)` and both routes
  keep their names and paths. `ROUTE_COUNT_AFTER` and `ACTION_INDEX_AFTER` are unchanged.
- **`Skipped` is never re-queueable** (`USER_LOCKS.retry_scope`). `Done` is never re-queueable.
- **`ports/storage.py` / `infrastructure/database/repositories.py` `reset_failed(self) -> None` is a different
  method** — a repository bulk reset asserted by `tests/unit/test_domain.py` protocol-method census. It is
  out of scope and must not be renamed or re-guarded.
- **Tokens are additive.** Do **not** repoint `--color-status-pending`; the Pending-pill recolor rides with the
  migration MEUs. `FORBIDDEN_SELECTION_FILL` is never used as a selection surface.
- **`ProgressBar` never animates geometry** (`G33_RULE`): fill is `transform: scaleX(value)` with
  `transform-origin: left`, transition limited to `transform` with `--duration-normal` / `--ease-out`.
- **`ConfirmModal` is a portal** (`G20_RULE`); `window.confirm` is forbidden.
- **No unified cross-feature status enum** (`STATUS_CONFIG_POLICY`) — each feature keeps its own
  `JOB_STATUSES`; the shared layer is parameterized over them.
- **No new dependency.** `VIRTUALIZATION_DECISION` = none; dnd-kit is MEU-49.
- Do not edit `mcp-server/`. OpenAPI `-o` regen is permitted **only** in MEU-42 (route docstrings change);
  every other gate uses `--check`.

Research URLs used to lock under-specified behavior:

- [WCAG 2.2 SC 1.4.3 Contrast (Minimum) — 4.5:1](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [WCAG 2.2 SC 1.4.1 Use of Color — status must not be color-only](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)
- [WCAG relative luminance / contrast-ratio definitions](https://www.w3.org/TR/WCAG22/#dfn-relative-luminance)
- [ARIA `progressbar` role and `aria-valuenow`](https://www.w3.org/WAI/ARIA/apg/patterns/meter/)
- [ARIA Authoring Practices — Menu Button pattern (kebab)](https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/)
- [ARIA Authoring Practices — Dialog (Modal) pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)
- [MDN — `HTMLInputElement.indeterminate`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/indeterminate)
- [MDN — HTML Drag and Drop API (`dragenter`/`dragover`/`dragleave` counting)](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API)
- [Tailwind CSS v4 `@theme` — custom colors generate utilities](https://tailwindcss.com/docs/theme)
- [Testing Library — prefer `userEvent` over `fireEvent`](https://testing-library.com/docs/user-event/intro)

---

## §4A GUI Element Compliance

**Triggered:** MEU-43 and MEU-44 create GUI elements (primitives + card). They are **not mounted on any
page** this session, so the census is a *component* census, not a page census.

| Check | Result |
|-------|--------|
| `docs/gui-element-reference.md` | **Absent** — G31–G35 + Spec tokens; fallback table below is the mapping |
| Button/input/output indexes | **Absent** except `gui-actions-index.md`; no new page actions this session → index unchanged |
| E2E written+wired | `E2E_NEW_WAVES_THIS_SESSION` = 0. No page-visible control is added, so E2 is satisfied by (a) component tests for every element below and (b) all existing waves staying green at `E2E_BASELINE_COUNT`. Wave for these elements is written in MEU-45 when they first mount. |
| G30–G35 / E2 | G30 N/A (no `<SelectInput>` added). G31 shared `bg-accent` only — no per-page accent fork; the variant grid is untouched. G32 `G32_RULE` (the Zorivest `SelectionCheckbox`/`BulkActionBar` hex fallbacks are stripped on port). G33 `G33_RULE` — `ProgressBar` uses `transform`, never `width`. G34 `G34_RULE` — no new `Button` variant/size. G35 tiers below. |
| G20 | `ConfirmModal` is the portal primitive; `G20_RULE` |
| G11 | N/A — no palette command added (no page surface yet) |
| G16 | CSP untouched |
| G23 | N/A — no form/dirty surface added |
| G26 | N/A — no HelpCard change |
| G27 | N/A — no new IPC channel |
| G7 | Card title/meta truncate with ellipsis **and** carry a `title` attribute (AC-44.7) |
| 10-item enforcement doc | **Absent** — this table is the mapping |

**Local fallback:** `G34_RULE` 5 variants × 3 sizes. Card row actions `sm`; modal actions `sm`.

| Element | Variant | Size | States | testid | Feedback |
|---------|---------|------|--------|--------|----------|
| Status badge | output | — | one per `STATUS_PILL_TABLE` key + unknown fallback | `status-badge` | T0 (render only); always renders a text label |
| Progress bar | output | — | 0 / partial / 1 / indeterminate-absent | `progress-bar` | T0; `role="progressbar"` |
| Selection checkbox | input | sm | unchecked / checked / indeterminate / disabled | `selection-checkbox` | T0; click does not activate the card |
| Confirm modal | dialog | — | open / closed | `confirm-modal` | T2 on confirm (caller-owned) |
| Confirm modal — confirm | destructive | sm | default/hover/focus/disabled | `confirm-modal-confirm` | T2; verb label from caller, never "OK" |
| Confirm modal — cancel | outline | sm | default/hover/focus | `confirm-modal-cancel` | T0; initial focus target |
| Queue list | output | — | empty / non-empty / drag-over | `queue-list` | T0 |
| Queue card | output (body `role="button"`) | — | default / hover / focus / checkbox-selected / detail-open | `queue-card` | T0; Enter+Space activate |
| Card position | output | — | default | `queue-card-position` | T0 |
| Card status icon | output | — | one per status | `queue-card-status-icon` | T0; lucide, paired with the text pill |
| Card title | output | — | default / truncated | `queue-card-title` | T0; `title` attr |
| Card meta | output | — | pending / in-flight / done / failed | `queue-card-meta` | T0 |
| Card primary action | primary (Retry) / ghost (Open file) / destructive (Cancel) | sm | default/hover/focus/disabled/absent | `queue-card-primary-action` | T1 — caller-owned callback |
| Card kebab | ghost | sm | closed / open | `queue-card-kebab` | T0 opens `queue-card-menu` |
| Card menu | menu | — | open / closed | `queue-card-menu` | T0; `aria-haspopup="menu"`, Escape closes |
| Empty drop zone | output | — | `DRAG_STATES` | `empty-drop-zone` | T0 |
| Empty drop zone — Browse | secondary | md | default/hover/focus | `empty-drop-zone-browse` | T1 — caller-owned callback |
| Drop overlay (non-empty list) | output | — | hidden / visible | `queue-drop-overlay` | T0 |

---

## Proposed Changes

### MEU-41 — `canon-queue-cards`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| _(none)_ | — | MEU-41 changes markdown canon and CSS custom properties only. It adds no request/response surface, no form, no file import, and no env/config input. | n/a | n/a | n/a | Boundary Input Contract — external-input MEUs only |

Python `assert` is not validation (N/A — no runtime input surface in this MEU).

#### Acceptance Criteria

> Tag: `unit` or `integration`. Each control AC names observable + call chain + negative oracle.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-41.1 | unit | **Canon exists.** Observable: `PHASE10_SPEC` exists and contains every heading in `PHASE10_SECTIONS`. Chain: test reads the file from disk. Negative: file absent, or any `PHASE10_SECTIONS` entry missing → fail. | Spec (proposal §10 "folds into spec canon") | a stub file with only a title |
| AC-41.2 | unit | **Supersession pointers, not deletions.** Observable: `GUI_SPEC` still contains both original blocks named in `GUI_SPEC_SUPERSEDE_ANCHORS`, **and** each is annotated with `SUPERSEDE_POINTER`. Chain: test reads `GUI_SPEC`. Negative: either section deleted, or annotated without naming `PHASE10_SPEC` → fail. | Local Canon (proposal §11 conflicts 1–2); AGENTS.md "flag the conflict, do not silently pick one" | delete the DataTable spec |
| AC-41.3 | unit | **Tokens added to both themes.** Observable: `TOKEN_FILE` defines each key of `PORTED_TOKENS` in `THEME_BLOCK_DARK` with its `dark` value and in `THEME_BLOCK_LIGHT` with its `light` value, **each hex byte-identical to the same token in `PILL_TOKEN_SOURCE`**; and no `--color-*` token exists in `TOKEN_FILE` that `PILL_TOKEN_SOURCE` does not also define with the same value, for every token `STATUS_PILL_TABLE` names. Chain: test parses both stylesheets and diffs them. Negative: token declared only in `@theme` (light theme silently inherits dark); a hex that differs from Zorivest's by one digit; any av-kit-authored pill hue → fail. | `USER_LOCKS.pill_palette`; Local Canon `styles.css` light block pattern; [Tailwind v4 @theme](https://tailwindcss.com/docs/theme) | dark-only declaration; av-kit-local hue |
| AC-41.4 | unit | **Selection fill never reuses `FORBIDDEN_SELECTION_FILL`.** Observable: no file under `UI_ROOT` pairs a selected/active state with `FORBIDDEN_SELECTION_FILL`; permitted fills are `SELECTION_FILL_ALLOWED`. Chain: source scan test. Negative: `selected ? 'bg-bg-subtle' : …` → fail. | Local Canon (proposal §11 conflict 5; `--color-bg-subtle` is `#6272a4` dark vs `#d1d5db` light) | reuse bg-subtle for selection |
| AC-41.5 | unit | **`AgeRestricted` uses the Spec token.** Observable: `download-controls.ts` `STATUS_COLORS.AgeRestricted` equals `STATUS_PILL_TABLE.AgeRestricted.fillClass` (`bg-accent-red/10`), not `bg-accent-pink`. Chain: import `STATUS_COLORS`. Negative: value still `bg-accent-pink`; any status mapped to a token absent from `PILL_TOKEN_SOURCE` → fail. | `USER_LOCKS.pill_palette` supersedes the `06-gui.md` "AgeRestricted Brown" wording — Zorivest has no brown, and `--color-accent-red` is the hue it already repointed for AA (`#ffa0a0`, commented "was #ff5555 @ 2.91:1") | keep the pink deviation; invent a brown |
| AC-41.6 | unit | **Locks recorded verbatim as spec.** Observable: `PHASE10_SPEC` states each `USER_LOCKS` decision — sticky bulk bar, verb-labeled remove confirm with undo deferred, dnd deferred to MEU-49, single density, in-flight-row-only Cancel wired to queue-level cancel (named with `CANCEL_CONTROL_LABEL` per `CANCEL_SCOPE_RULE`), Done-only Clear finished with files retained — and for Clear finished the canon states **every** clause of `CLEAR_FINISHED_SEMANTICS`: the Done id set is snapshotted once before the first request, each `DELETE /{id}` is independent, a failure never aborts the remaining ids, confirmed deletions are never rolled back, no media is deleted from disk, exactly one list refetch reconciles the result, and the `G35_RULE` toast reports removed count, failed count, and a reason per failure. Chain: test greps the canon for each lock and each `CLEAR_FINISHED_SEMANTICS` clause. Negative: any lock missing or contradicted; canon that says only "partial-result toast" and leaves abort-on-first-failure open → fail. | Human-approved (`USER_LOCKS`); `CLEAR_FINISHED_SEMANTICS` (reviewer R4-F4) | canon that leaves a lock open |
| AC-41.7 | unit | **Re-queue contract and non-goals recorded.** Observable: `PHASE10_SPEC` names `REQUEUEABLE_DOWNLOAD_STATUSES`, `REQUEUEABLE_CONVERSION_STATUSES`, `PAUSE_SCOPE`, `BULK_ENDPOINT_POLICY`, and every `OUT_OF_SCOPE` entry. Chain: test greps the canon. Negative: canon implies a per-item cancel or a bulk endpoint → fail. | Human-approved + Local Canon `06-gui.md:503-524` | invent POST /{queue}/bulk in canon |
| AC-41.8 | unit | **Phase 10 registered in the SSOT-rendered hub.** Observable: `BUILD_PLAN` contains a Phase 10 section and `MATRIX` contains every row of `MATRIX_ROWS`; `SSOT` contains every id in `PHASE10_MEU_IDS`. Chain: test reads `BUILD_PLAN` + `MATRIX` + `SSOT` (all written by WP-HUB0 via `meu_status.py render`; AUTOGEN tables are never hand-edited). Negative: hub edited by hand so `render --check` would drift → fail. | Local Canon `.agent/context/meu-status.yaml` + `tools/meu_status.py` | hand-edit AUTOGEN table |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Proposal becomes canon | Spec | proposal §10 "folds into spec canon"; `PHASE10_SPEC` |
| DataTable spec superseded | Local Canon | proposal §11 conflict 1; `06-gui.md:1090-1143` specced, never built (verified: no `DataTable.tsx` in `UI_PRIMITIVES_DIR`) |
| Glyph control labels superseded | Local Canon | proposal §11 conflict 2; `06-gui.md:526-542` |
| AgeRestricted hue | Human-approved | `USER_LOCKS.pill_palette` supersedes both `06-gui.md`'s Brown `#c4a882` and proposal §5's pink: AgeRestricted takes the existing shared `--color-accent-red`, so no `--color-age-restricted` token is created. `PORTED_TOKENS` adds only the four `--color-status-*` hexes Zorivest declares and av-kit lacks |
| Light-theme value for every ported token | Human-approved | `USER_LOCKS.pill_palette` — the light value is whatever `PILL_TOKEN_SOURCE` declares, copied verbatim. av-kit is missing the light `--color-status-pending` that Zorivest has; porting the family closes that gap rather than authoring a substitute |
| Selection fill | Human-approved + Local Canon | `SELECTION_FILL_SOURCE`. No `--color-bg-selected` token is authored — `PILL_TOKEN_SOURCE`'s own card list uses `border-accent bg-accent/10`, which `CARD_STATE_CLASSES` already matches byte-for-byte. Its `checkbox-selected` step (`bg-bg-subtle`) is the single disclosed divergence: proposal §11 conflict 5 forbids that fill because `--color-bg-subtle` inverts between themes (`#6272a4` dark vs `#d1d5db` light), so av-kit uses `bg-accent/5` |
| AgeRestricted pink deviation | Spec wins | `download-controls.ts` deviates from `06-gui.md`; Spec is authoritative |
| Six open decisions in proposal §12 | Human-approved | `USER_LOCKS` — all six locked by the user this session |
| BUILD_PLAN marks all phases complete | Local Canon | proposal §11 conflict 3; resolved by registering Phase 10 in `SSOT` and re-rendering |
| `gui-element-reference.md` absent | Local Canon | proposal §11 conflict 4; §4A fallback table above |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `PHASE10_SPEC` | new | Phase 10 canon: `PHASE10_SECTIONS` |
| `GUI_SPEC` | edit | `SUPERSEDE_POINTER` at `GUI_SPEC_SUPERSEDE_ANCHORS`; nothing deleted |
| `TOKEN_FILE` | edit | `PORTED_TOKENS` in both theme blocks, hexes copied from `PILL_TOKEN_SOURCE` |
| `ui/src/renderer/src/features/downloader/download-controls.ts` | edit | `STATUS_COLORS.AgeRestricted` → Spec token |
| `SSOT`, `MATRIX`, `BUILD_PLAN` | edit / regen | WP-HUB0: Phase 10 + `PHASE10_MEU_IDS` + `MATRIX_ROWS`; `render` |
| `UNIT_TEST_DIR_UI/queue-canon.test.ts` | new | AC-41.* |

---

### MEU-42 — `svc-requeue-widening`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| `POST /downloads/{id}/reset` | existing `EmptyIn \| None` body + path `id: str` | body has no fields; `id` is an opaque string | `extra="forbid"` (unchanged — do not relax) | extra key → 422; unknown id → `REQUEUE_NOTFOUND_CODE`; non-re-queueable status → `REQUEUE_CONFLICT_CODE` | n/a (no create/update pair) | `routes/downloads.py:233`; Boundary Input Contract |
| `POST /conversions/{id}/reset` | existing `EmptyIn \| None` body + path `id: str` | same | `extra="forbid"` (unchanged) | same | n/a | `routes/conversions.py:255` |
| Domain guard | `DownloadJob.reset_failed` / `ConversionJob.reset_failed` | status ∈ `REQUEUEABLE_*_STATUSES` | n/a (no external input) | `ConflictError` → mapped to `REQUEUE_CONFLICT_CODE` | n/a | proposal §4 Retry; `USER_LOCKS.retry_scope` |

Python `assert` is not validation — the guard is an explicit `if … raise ConflictError`, not an `assert`
(`assert` bytecode is omitted under `-O`).

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-42.1 | unit | **Single-statement re-queueable sets.** Observable: `REQUEUEABLE_DOWNLOAD_STATUSES` is a module-level `frozenset` in `domain/download.py` equal to `REQUEUEABLE_DOWNLOAD_STATUSES`; `REQUEUEABLE_CONVERSION_STATUSES` likewise in `domain/conversion.py`. Plus `REQUEUE_STATUS_EXHAUSTIVENESS`, so a status added to either enum without being classified fails immediately. Chain: import the constants. Negative: the set is inlined in the guard, duplicated in the service/route, or a member of `DOWNLOAD_STATUSES` / `CONVERSION_STATUSES` appears in neither partition → fail. | Local Canon single-statement rule; `USER_LOCKS.retry_scope` | inline status tuple in the guard |
| AC-42.2 | unit | **Download transition map gains exactly the re-queue edges.** Observable: `Pending ∈ DOWNLOAD_TRANSITIONS[s]` for every `s` in `REQUEUEABLE_DOWNLOAD_STATUSES`; `Pending ∉ DOWNLOAD_TRANSITIONS.get(s, frozenset())` for every `s` in `NON_REQUEUEABLE_DOWNLOAD_STATUSES`. Chain: import `DOWNLOAD_TRANSITIONS`. Negative: `Skipped` or `Done` gains a `Pending` edge; `Downloading → Pending` added → fail. | `USER_LOCKS.retry_scope`; `domain/download.py:28` | make every terminal state re-queueable |
| AC-42.3 | unit | **Conversion transition map stays exhaustive.** Observable: `CONVERSION_TRANSITIONS[Cancelled] == frozenset({Pending})`; `set(CONVERSION_TRANSITIONS) == set(ConversionStatus)` still holds; `Done` and `Skipped` remain `frozenset()`. Chain: import `CONVERSION_TRANSITIONS`. Negative: a key removed (breaks the existing exhaustiveness assertion) → fail. | `domain/conversion.py:34`; existing `test_ac_28_6_conversion_transitions_exhaustive` | drop a key while editing |
| AC-42.4 | unit | **`DownloadJob.reset_failed` accepts the widened set.** Domain-level only — the blocker revalidation of `REQUEUE_BLOCKER_POLICY` lives in the service (AC-42.10), because the domain object cannot see the SABR snapshot or the downloader defaults. Observable: from each status in `REQUEUEABLE_DOWNLOAD_STATUSES` the result matches `REQUEUE_RESET_FIELDS` (status `Pending`, `error_message` `None`, `progress` `0.0`). Chain: construct the job → call. Negative: any member still raises → fail. | proposal §4 Retry; `USER_LOCKS.retry_scope` | leave the guard at `is not Failed` |
| AC-42.5 | unit | **`DownloadJob.reset_failed` still refuses the rest.** Observable: `ConflictError` from every status in `NON_REQUEUEABLE_DOWNLOAD_STATUSES`, and the error message names the re-queueable set rather than only "Failed". Chain: call → catch. Negative: `Skipped` or `Done` succeeds → fail. | `USER_LOCKS.retry_scope` (Skipped excluded); existing `test_ac_3_4_*` | widen to all statuses |
| AC-42.6 | unit | **`ConversionJob.reset_failed` mirrors it.** Observable: succeeds from `REQUEUEABLE_CONVERSION_STATUSES` with `REQUEUE_RESET_FIELDS`; `ConflictError` from `NON_REQUEUEABLE_CONVERSION_STATUSES`. Chain: construct → call. Negative: `Processing → Pending` allowed → fail. | proposal §4; `domain/conversion.py:310` | allow re-queue mid-flight |
| AC-42.7 | integration | **Services persist the widened re-queue.** Observable: `DownloadService.reset_failed(id)` / `ConversionService.reset_failed(id)` on a `Cancelled` job return a `Pending` job **and** the repository round-trip shows `Pending` after commit; unknown id raises `NotFoundError`. Chain: service → `uow.<repo>.get` → `job.reset_failed()` → `save` → `commit`. Negative: returns the updated job without saving; signature renamed → fail. | `services/download.py:303`; `services/conversion.py:230` | in-memory-only update |
| AC-42.8 | integration | **Both reset routes honor the widened contract.** Observable: for each queue, `POST /{queue}/{id}/reset` returns 200 with `status="Pending"` for every seeded re-queueable status, `REQUEUE_CONFLICT_CODE` for every non-re-queueable status, and `REQUEUE_NOTFOUND_CODE` for an unknown id; the extra-field 422 behavior of `EmptyIn` is unchanged. Route docstrings read `REQUEUE_ROUTE_DOCSTRING`. Blocker states are the AC-42.10 case and are asserted there, not here. Chain: TestClient → route → service → domain. Negative: 500 instead of 409; `extra="forbid"` relaxed to allow a `status` field → fail. | `routes/downloads.py:233`; `routes/conversions.py:255`; `ERROR_SURFACE` | map ConflictError to 500 |
| AC-42.9 | integration | **Surface counts are flat and OpenAPI is regenerated.** Observable: `OPENAPI_COMMITTED` regenerated so `OPENAPI_EXPORT --check` exits 0 with the new docstring descriptions; path count still `ROUTE_COUNT_AFTER`; `mcp-server/src/**/*.ts` is byte-identical to its `FROZEN_GLOBS` baseline and its action count is still `ACTION_INDEX_AFTER`. Chain: `OPENAPI_EXPORT -o` then `--check`. Negative: a new path appears; `mcp-server/src/toolsets/*.ts` edited → fail. | `MCP_CHANGE_BASIS`; Local Canon OpenAPI drift gate | add POST /{queue}/{id}/retry |
| AC-42.10 | integration | **Blocker re-queue revalidates instead of laundering.** Observable, per `REQUEUE_BLOCKER_POLICY`: (a) `DownloadService.reset_failed(id)` on a `QualityBlocked` job first applies the current downloader defaults (the same `quality` / `audio_format` / `audio_only` mapping `apply_defaults_to_pending` writes) and then re-evaluates `_incompatible(job)` against the live SABR snapshot; (b) when the job is now compatible — or SABR is not `Active` — it persists as `Pending`, exactly as AC-42.7 requires; (c) when it is **still** incompatible under Active SABR the job stays `QualityBlocked`, nothing is written, and `POST /downloads/{id}/reset` answers `REQUEUE_BLOCKER_CONFLICT_CODE` with a message containing `BLOCKER_REMEDIATION['QualityBlocked']` verbatim, so the response names the setting to change rather than saying only "conflict"; (d) an `AgeRestricted` job re-queues unconditionally — no SABR check — because cookie and auth options are read at execution time. Chain: seed SABR `Active` + a blocked job → TestClient `POST /downloads/{id}/reset` → service → `_incompatible` → repo. Negative (each must fail): the service resets a still-incompatible `QualityBlocked` job to `Pending` (the worker would then run it with the very quality the lock rejected, since `_run_one` never re-runs `apply_lock`); the 409 body omits the remediation string; `AgeRestricted` is gated on SABR. | Research-backed (reviewer R4-F2), verified against `services/download.py` `apply_lock`/`_run_one`/`apply_defaults_to_pending`; `REQUEUE_BLOCKER_POLICY` | reuse the generic reset path for blocker states |
| AC-42.11 | integration | **Every `QualityBlocked` job carries a real reason.** Observable, per `BLOCKER_REASON_RULE`: for **both** producers named in `BLOCKER_REASON_PRODUCERS['QualityBlocked']` — `enqueue` (which today constructs the job with `error_message=None` in the very branch that just chose `QualityBlocked`) and `apply_lock` (which today transitions `Pending → QualityBlocked` without adding one) — the job read back **from the repository after commit**, and the job serialized by `GET /downloads`, both carry `error_message` equal to `BLOCKER_REASON_TEMPLATE['QualityBlocked']` **verbatim** — the template interpolates no job field, per `BLOCKER_REASON_COPY_RULE`. The assertion is made against the persisted/serialized payload, never a hand-built `DownloadJob`, so it is the data the card actually receives. Neither producer writes the reason itself: both reach `SqlAlchemyDownloadRepository.add`/`.save`, where `BLOCKER_REASON_ENFORCEMENT['boundary-normalizer']` supplies it (AC-42.14). This AC therefore proves the *outcome* at the two entry paths; AC-42.14 proves the *mechanism* that makes forgetting impossible. `AgeRestricted` is asserted to **already** conform (`_run_one`'s `AgeRestrictedError` handler passes `str(exc)` into `_finish`) and is not changed. Chain: `enqueue` under an Active SABR lock → `uow.downloads.get` → TestClient `GET /downloads`; then `apply_lock` on a seeded `Pending` job → same reads. Negative (each must fail): either producer leaves `error_message` `None`; the reason is written by the API layer or the UI instead of at the transition; the string is inlined rather than rendered from `BLOCKER_REASON_TEMPLATE`; the template regains a `{quality}`-style placeholder, or any other job field, or the acronym SABR. | Research-backed (reviewer R5-F1), verified against `services/download.py:228-247` (enqueue), `:351-365` (`apply_lock`), `:506-507` (the conforming AgeRestricted path); `BLOCKER_REASON_RULE` | let AC-44.15 pass on a fabricated prop while production blocks a user with no explanation |
| AC-42.12 | integration | **A blocked job's reason survives the rest of its life.** Observable, per `BLOCKER_REASON_INVARIANT` clause (1) and `BLOCKER_REASON_PRODUCERS['QualityBlocked']['persists-while-blocked']`: after **each** of the two mutations that touch an already-`QualityBlocked` row, the row read back from the repository and the row serialized by `GET /downloads` still carry `error_message` == `BLOCKER_REASON_TEMPLATE['QualityBlocked']`. The two cases, both seeded as *persisted state*, not as fresh enqueues: **(a) the legacy row** — a `QualityBlocked` job written straight to the repository with `error_message=None` (the shape every row blocked before this MEU shipped already has on disk), then `apply_lock()` under an Active SABR snapshot → the reason is backfilled; **(b) Apply Defaults on a blocked row** — `apply_defaults_to_pending()` rewrites `quality`/`audio_format`/`audio_only` on a blocked job (`services/download.py:369-391` matches `QualityBlocked`, not just `Pending`) → the row it saves still carries the reason, and the reason still reads true of the row, because the template interpolates nothing. Chain: repository seed → service call → `uow.downloads.get` → TestClient `GET /downloads`. **(c) the refused Retry** — a legacy `QualityBlocked` row, `POST /downloads/{id}/retry` while still incompatible: the route answers `REQUEUE_BLOCKER_CONFLICT_CODE` **and** the row is canonicalized on the way out, per `BLOCKER_REASON_ENFORCEMENT['refusal-canonicalization']`, so the card the user is looking at when the refusal lands is not the blank one. Negative (each must fail): the legacy row stays reasonless after `apply_lock` (today `apply_lock` matches an already-blocked row and then falls through with no write at all); `apply_defaults_to_pending` blanks `error_message` while saving; the invariant is enforced in the API serializer or the card instead of at the persist site; the 409 path writes nothing and leaves the row blank. | Research-backed (reviewer R6-F1), verified against `services/download.py:351-365` (the fall-through branch) and `:369-391` (Apply Defaults matching `QualityBlocked`); `BLOCKER_REASON_INVARIANT` | ship a card whose explanation is blank for every job blocked before release, or that contradicts the quality printed beside it |
| AC-42.13 | integration | **Un-blocking clears the reason.** Observable, per `BLOCKER_REASON_INVARIANT` clause (2): after `clear_sabr()` moves a `QualityBlocked` job to `Pending`, the persisted row and the `GET /downloads` payload both carry `error_message is None`. `DownloadJob.transition` is `replace(self, status=...)` (`domain/download.py:111-119`) and preserves `error_message` verbatim, so `clear_sabr` (`services/download.py:335-348`) must clear it explicitly. The domain's `reset_failed` is asserted to **already** conform (`domain/download.py:121-128` sets `error_message=None`) and is not changed; AC-42.10's widened re-queue inherits that. Chain: seed a `QualityBlocked` job carrying the reason → `clear_sabr()` → repository read → `GET /downloads`. Negative (each must fail): the now-`Pending` job still carries the blocker reason (the card would explain a block that no longer exists); the clearing is done by filtering in the component or the serializer rather than at the transition; `reset_failed` stops clearing it. | Research-backed (self-caught while verifying R6-F1 — the reviewer named the staleness, this is its mirror on the exit edge); `BLOCKER_REASON_INVARIANT` | leave a stale "why this is blocked" sentence on a job that is queued and about to run |
| AC-42.14 | integration | **The reason cannot be forgotten, because no callsite supplies it.** Observable, per `BLOCKER_REASON_ENFORCEMENT['boundary-normalizer']`: `normalize_blocker_reason` is a pure function in `domain/download.py` over `BLOCKER_REASONS`, and `SqlAlchemyDownloadRepository.add` and `.save` — the only two write paths into `download_jobs` — apply it. Assert at the repository, with **no service involved**: `add` a `QualityBlocked` `DownloadJob` built with `error_message=None`, commit, read back → the reason is there; `save` a blocked row whose message was blanked → same. Clause (2) at the same boundary: `save` a `Pending` job still carrying `BLOCKER_REASONS[QualityBlocked]` → the message is cleared. And the narrowness that makes clause (2) safe: `save` a `Failed` job whose `error_message` is a real traceback → it is **preserved untouched**, because the clear fires only when the message is exactly one of the `BLOCKER_REASONS` values. Chain: `uow.downloads` directly → `uow.commit()` → `uow.downloads.get`. Negative (each must fail): the normalization lives in a service, a route, or `_job_out` instead of the repository (a future callsite could then bypass it); it stamps a reason onto a non-blocker status; it clears any non-empty `error_message` rather than only a blocker reason. | Research-backed (reviewer R7-F1, whose remedy is to centralize at the domain/persistence boundary); `BLOCKER_REASON_ENFORCEMENT`; verified against `repositories.py` `add`/`save` being the sole writers (`reorder` touches `queue_position`, `delete`/`delete_all` remove rows, bulk `reset_failed` selects `Failed`) | let the invariant depend on every future author remembering four callsites |
| AC-42.15 | integration | **An upgraded queue explains itself before the user touches anything.** Observable, per `BLOCKER_REASON_ENFORCEMENT['upgrade-backfill']`: seed a database file the way a pre-release install leaves it — a `QualityBlocked` row with `error_message` NULL — then open a **fresh engine** so `apply_migrations()` runs, and call `GET /downloads`. The payload carries the reason, with **no `apply_lock`, no Apply Defaults, no Retry, no service call of any kind** in the test. That absence is the entire point of the AC: it is the path a person who upgrades and simply opens the queue actually takes. Idempotency: run `apply_migrations()` a second time against the same file → zero rows change, and a blocked row whose message was already correct is untouched. The statement's WHERE clause is `BLOCKER_REASON_MIGRATION_PREDICATE` and its literal is built from `BLOCKER_REASONS` at import, never retyped. Chain: raw SQL seed → new engine → `apply_migrations` → TestClient `GET /downloads`. Negative (each must fail): the backfill is a one-shot script or a documented manual step rather than an entry in the append-only `MIGRATIONS` list; it runs after routes can serve (the row is listable while still blank); it overwrites a message that is already present; re-running it rewrites rows. | Research-backed (reviewer R7-F1) — verified against `migrations.py:11-86`, an append-only list applied by `apply_migrations()` at engine init; `BLOCKER_REASON_ENFORCEMENT` | ship a release where every already-blocked job shows a blank explanation until the user happens to trigger a service path |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Card needs a Retry action | Spec | proposal §4 primary-action zone |
| No per-id retry endpoint exists | Local Canon | verified: only `POST /{queue}/{id}/reset`, guarded to `Failed` |
| Which statuses become re-queueable | Human-approved | `USER_LOCKS.retry_scope` (Cancelled + QualityBlocked + AgeRestricted; Skipped excluded) |
| Where the reason invariant is enforced | Research-backed (reviewer R7-F1) | `BLOCKER_REASON_ENFORCEMENT`. Round 7 stated an invariant over persisted state but enforced it at two optional service paths, so an upgrading user who merely opened the queue — or clicked Retry and was refused — still saw a blank card. Enforcement moves to `SqlAlchemyDownloadRepository.add`/`.save` (the only writers) plus one idempotent migration for rows that already exist. The service-side reason writes are deleted, not added to |
| Whether the reason clear can eat a real error | Research-backed (self-derived from the same remedy) | Clause (2) fires only when a non-blocker row's `error_message` is **exactly** one of the `BLOCKER_REASONS` values. An unconditional clear at the boundary would silently erase a `Failed` job's traceback — AC-42.14 asserts that case explicitly |
| Whether the blocker reason is job-specific | Research-backed (reviewer R6-F1) | `BLOCKER_REASON_COPY_RULE`. Round 6 formatted `{quality}` into the stored sentence, which is precisely what let it go stale: `apply_defaults_to_pending` (`services/download.py:369-391`) rewrites a blocked row's quality without touching `error_message`. The template is now quality-independent and acronym-free, so the maintenance obligation collapses to *presence* (AC-42.12) rather than *recomputation*; the job-specific detail already lives in the card's meta zone |
| Reason lifetime on the exit edge | Research-backed (self-caught) | `BLOCKER_REASON_INVARIANT` clause (2). `transition()` is `replace(self, status=...)` and keeps `error_message`, so `clear_sabr` would hand every un-blocked job back to the queue still displaying its blocker reason. AC-42.13 clears it at the transition. This is not in the reviewer's finding — it is the same defect class on the other edge, found while verifying R6-F1 |
| Where the card's open-region ends | Research-backed (reviewer R6-F2) | `CLICKABLE_REGION_RULE`. The mockup nests the primary action and the kebab inside the body element that proposal §4 makes `role="button"`; its own zone strip (mockup:278) already treats them as separate right-edge columns, so hoisting them out is layout-neutral. AC-44.16 asserts ancestry and independent operation for all three interactive zones |
| Where a blocker reason comes from | Research-backed (reviewer R5-F1) | `BLOCKER_REASON_RULE`. Verified: `AgeRestricted` already gets one (`_run_one` → `_finish(error=str(exc))`), but **both** `QualityBlocked` producers leave `error_message=None`. The card copy `BLOCKER_META_RULE` requires therefore has no producer until AC-42.11 adds one at the transition — the reason is job data, not component copy |
| Re-queue from a **blocker** state | Research-backed (reviewer R4-F2) | `REQUEUE_BLOCKER_POLICY`. Verified against `services/download.py`: `apply_lock()` only ever moves `Pending → QualityBlocked`, and `_run_one` does **not** re-run it — so a plain reset drops a QualityBlocked job straight into the pool the worker drains, defeating the guard that blocked it. `QualityBlocked → Pending` must therefore apply current downloader defaults and re-evaluate `_incompatible(job)` against the live SABR snapshot, answering `REQUEUE_BLOCKER_CONFLICT_CODE` with `BLOCKER_REMEDIATION` when it is still incompatible. `AgeRestricted` is unconditional: cookie/auth options are read at execution time |
| Widening breaks no existing test | Local Canon | every existing negative assertion seeds `Pending` or `Done` — `test_ac_3_4_*`, `test_ac_28_5_*`, `test_ac_31_10_*`, `test_ac_15_5_*`, `test_services.py:869`; neither status enters the widened set |
| Keep method name `reset_failed` | Local Canon | renaming would break the MCP `reset` action mapping and `ROUTE_COUNT_AFTER`/`ACTION_INDEX_AFTER` flatness |
| Repository `reset_failed` untouched | Local Canon | `ports/storage.py:34` + `repositories.py:107` are a bulk method asserted by `test_domain.py:1386` protocol census |
| Docstring change ⇒ OpenAPI drift | Local Canon | FastAPI uses the docstring as the operation description |
| No MCP change | Local Canon | `MCP_CHANGE_BASIS` — `desc()` is formulaic over method+path |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/download.py` | edit | `REQUEUEABLE_DOWNLOAD_STATUSES`; `DOWNLOAD_TRANSITIONS` re-queue edges; `reset_failed` guard |
| `packages/core/src/avkit_core/domain/conversion.py` | edit | `REQUEUEABLE_CONVERSION_STATUSES`; `CONVERSION_TRANSITIONS[Cancelled]`; `reset_failed` guard |
| `packages/core/src/avkit_core/services/download.py` | edit | `reset_failed` gains the `REQUEUE_BLOCKER_POLICY` branch (AC-42.10) and saves the job through the normalizing repository before raising the 409 (AC-42.12c). **No reason-writing code**: Round 7's four per-callsite writes are deleted in favour of the boundary normalizer, per reviewer R7-F1 |
| `packages/core/src/avkit_core/domain/download.py` | edit | (with the re-queue edits above) `BLOCKER_REASONS` and the pure `normalize_blocker_reason` (AC-42.14) |
| `packages/infrastructure/src/avkit_infra/database/repositories.py` | edit | `SqlAlchemyDownloadRepository.add`/`.save` apply `normalize_blocker_reason` — the single enforcement point for `BLOCKER_REASON_INVARIANT` (AC-42.14) |
| `packages/infrastructure/src/avkit_infra/database/migrations.py` | edit | one appended idempotent UPDATE statement backfilling legacy `QualityBlocked` rows, built from `BLOCKER_REASONS` (AC-42.15) |
| `packages/api/src/avkit_api/routes/downloads.py` | edit | docstring → `REQUEUE_ROUTE_DOCSTRING` |
| `packages/api/src/avkit_api/routes/conversions.py` | edit | docstring → `REQUEUE_ROUTE_DOCSTRING` |
| `OPENAPI_COMMITTED` | regen | `-o` then `--check` |
| `UNIT_TEST_DIR_PY/test_domain.py`, `test_domain_conversion.py`, `test_services.py` | edit | add AC-42.* cases; **do not modify existing assertions** |
| `E2E_TEST_DIR_PY/test_api_downloads.py`, `test_api_conversions.py` | edit | add AC-42.8 cases |

> `services/conversion.py` is unchanged in code — it already delegates to the domain guard, and AC-42.6/42.7
> add coverage rather than a rewrite. `services/download.py` **is** changed, for two reasons the reviewer
> established and this plan accepted: the blocker revalidation of AC-42.10 needs the live SABR snapshot and
> the downloader defaults, neither of which the domain object can see; and the blocker reason of AC-42.11 has
> to exist for **every** persisted blocked row, which is a persisted-state invariant and therefore belongs at the
> persistence boundary rather than at service callsites (reviewer R7-F1). That is why this MEU now also touches
> `repositories.py` and `migrations.py`: one normalizer on `add`/`save` covers every future write, and one appended
> idempotent UPDATE statement covers the rows that already exist on an upgrading user's disk. Both edits stay
> inside this MEU's file set — no new module, no signature change, no repository or MCP surface touched.

---

### MEU-43 — `gui-queue-primitives`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| Queue list envelope parse | `UI_QUEUE_LIB_DIR/envelope.ts` Zod `.strict()` on the wrapper | must have `items: unknown[]`; `processor` optional | reject arrays and unknown wrapper keys | parse failure surfaces via `ERROR_SURFACE`; never `data.map` on the raw response | GET only | Local Canon envelope carry-forward |
| `StatusBadge` status prop | TS union per feature (`STATUS_CONFIG_FEATURES`) | member of that feature's `JOB_STATUSES` | unknown value → neutral fallback badge, never a crash | renders fallback + text label | n/a | proposal §5 |
| `ProgressBar` value prop | component guard | finite number clamped to `[0,1]` | n/a | `NaN` / out-of-range clamps; no `aria-valuenow` outside 0–100 | n/a | [ARIA progressbar](https://www.w3.org/WAI/ARIA/apg/patterns/meter/) |
| `ConfirmModal` props | component contract | `confirmLabel` required, non-empty verb | n/a | missing verb label is a type error, not a silent "OK" | n/a | `G20_RULE`; `USER_LOCKS.remove_confirm` |

Python `assert` is not validation (N/A in renderer — Zod + TS unions).

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-43.1 | unit | **`formatFileSize` is defined once.** Observable: exactly one definition repo-wide, in `UI_QUEUE_LIB_DIR/format.ts`; both `DEDUP_TARGETS.formatFileSize` directories import it. Chain: source scan + import test. Negative: a second `function formatFileSize` / `const formatFileSize =` anywhere under `UI_ROOT` → fail. | Local Canon (verified duplicate in both queue tables); proposal §2 | keep one copy and re-declare the other |
| AC-43.2 | unit | **Status pill table is single-statement and hex-free.** Observable: `UI_QUEUE_LIB_DIR/status-tokens.ts` exports one record whose key set equals `STATUS_PILL_TABLE`'s, each entry carrying exactly `{ slug, token, fillAlpha, fillClass, labelClass, iconClass }` deep-equal to the `STATUS_PILL_TABLE` record — one **hue** token per status driving `fillClass` and `iconClass`, with `labelClass` fixed at `text-fg` for every status per `PILL_CLASS_RULE`; the module contains **no hex literal at all** — every colour is a CSS custom property name resolved at render time (`G32_RULE`). Chain: import the record and compare to the named set. Negative: a second status→color map anywhere under `UI_ROOT`; any `#rrggbb` in `status-tokens.ts`; a `labelClass` that varies by status → fail. | proposal §5 (fill + alpha); single-statement rule; `G32_RULE` | duplicate map in StatusBadge |
| AC-43.3 | unit | **Measured contrast matrix — all 80 label pairings, no debt set.** Observable: the test parses `CONTRAST_THEME_SOURCE` into its dark and light token maps, then for **every** `STATUS_PILL_TABLE` entry × **every** `CONTRAST_BACKDROPS` entry × both themes (80 pairings) resolves the entry's hue `token` to its hex *from the stylesheet*, alpha-composites it at `fillAlpha` over the backdrop (itself resolved from `--color-bg` / `--color-bg-elevated` / `--color-accent`), and measures the WCAG relative-luminance ratio of **`--color-fg`** — the label colour, per `PILL_CLASS_RULE` — against that composite. Two assertions, both unconditional: (1) **every one of the 80 label pairings is ≥ `CONTRAST_MIN`** (measured worst case `CONTRAST_WORST_MEASURED`); (2) the computed matrix equals `CONTRAST_MEASURED`'s `label` array **exactly**, ratio by ratio, so a token value that moves without the baseline moving fails. There is no pass/debt partition and no exemption — the earlier one is withdrawn with the same-token label that made it necessary. The `icon` array is recomputed and compared too, but is **advisory only** per `STATUS_ICON_RULE`. No hex is restated in the test. Chain: parse `TOKEN_FILE` → resolve → composite → ratio(`--color-fg`, composite) → diff against `CONTRAST_MEASURED`. Negative (four, each must fail the suite): (a) edit one ported token hex by one digit without regenerating the baseline; (b) raise one `fillAlpha` to 0.6; (c) evaluate the dark token map against the light backdrops; (d) set any status's `labelClass` back to its own hue token — the measured light `Paused` pairing falls to 2.23 and the suite must go red. | `USER_LOCKS.pill_palette` (Human-approved) for the hues; reviewer R4-F1 for the decoupled label; [WCAG 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) + [luminance](https://www.w3.org/TR/WCAG22/#dfn-relative-luminance); `CONTRAST_RULE` | ship a measured-and-documented failure set; eyeball the palette |
| AC-43.4 | unit | **Token/CSS parity and class→token binding.** Observable: every `token` in `STATUS_PILL_TABLE` is defined in **both** `THEME_BLOCK_DARK` and `THEME_BLOCK_LIGHT` of `TOKEN_FILE`; each entry's `fillClass` and `iconClass` are exactly the Tailwind forms of that entry's hue `token` (at `fillAlpha` for the fill), every entry's `labelClass` is the single shared `text-fg`, and `--color-fg` itself is defined in both theme blocks — so the classes AC-43.3 measures are the classes `StatusBadge` renders; and no `fillClass` uses `/20` on an `--color-accent-*` hue (Zorivest MEU-389). Chain: test parses `TOKEN_FILE` + derives the class strings. Negative: a token defined in only one theme block; a `labelClass` naming a status hue instead of `text-fg`; an `iconClass` naming a different token than `fillClass`; an accent hue at `/20` → fail. | `PILL_CLASS_RULE`; `G32_RULE`; Local Canon | hardcode a colour in TS only; let the label hue drift per status |
| AC-43.5 | unit | **`StatusBadge` renders text, not colour alone.** Observable: for every status, the badge renders a non-empty text label carrying `labelClass` on the `fillClass` from `status-tokens.ts`, and the card's left-edge status icon carries `iconClass` **and** `aria-hidden="true"` per `STATUS_ICON_RULE`; unknown status renders the neutral fallback with the raw string as label; `data-testid="status-badge"`. Chain: render → query. Negative: colour-only dot with no label; a status icon that is exposed to the accessibility tree (it would double-announce the pill text); crash on unknown status → fail. | [WCAG 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html); Zorivest `AccountTypeBadge` variant-map pattern | icon-only badge |
| AC-43.6 | unit | **`ProgressBar` never animates geometry.** Observable: the fill element's inline style uses `transform: scaleX(<clamped>)` with `transform-origin: left`; the component's `className` contains no `w-[` / `width:` on the fill and no `transition-all`; transition is limited to `transform` with `--duration-normal` / `--ease-out`. Chain: render → inspect style + class strings. Negative: `style={{ width: \`${p}%\` }}` (the current `ChannelCard` pattern) → fail. | `G33_RULE`; proposal §2 (Transcript violation) | width-percentage fill |
| AC-43.7 | unit | **`ProgressBar` ARIA + clamping.** Observable: `role="progressbar"`, `aria-valuemin=0`, `aria-valuemax=100`, `aria-valuenow` = rounded percent; values `<0`, `>1`, `NaN` clamp into range without throwing; `data-testid="progress-bar"`. Chain: render with edge values. Negative: `aria-valuenow="NaN"`; unbounded value → fail. | [ARIA progressbar](https://www.w3.org/WAI/ARIA/apg/patterns/meter/) | no ARIA on a visual-only bar |
| AC-43.8 | unit | **`SelectionCheckbox` indeterminate + isolation.** Observable: `indeterminate` is set imperatively on the DOM node (the attribute does not exist in HTML); `onChange` fires with the next checked value; a click does **not** bubble to an ancestor `role="button"`; `accentColor` resolves from `var(--color-accent)` with **no** hex fallback; `data-testid="selection-checkbox"` overridable. Chain: `userEvent.click` inside a wrapper button. Negative: hex fallback retained from the Zorivest source; click activates the wrapper → fail. | [MDN indeterminate](https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/indeterminate); `G32_RULE`; Zorivest port | keep `#6366f1` fallback |
| AC-43.9 | unit | **`ConfirmModal` is a portal dialog with a verb label.** Observable: renders through a portal outside the triggering subtree; `role="dialog"`, `aria-modal="true"`, `aria-labelledby` bound to its title; confirm button text is the caller's verb (never "OK"/"Yes"); testids `confirm-modal`, `confirm-modal-confirm`, `confirm-modal-cancel`. Chain: render → query document body. Negative: `window.confirm` anywhere under `UI_ROOT`; generic "OK" label → fail. | `G20_RULE`; `USER_LOCKS.remove_confirm`; [APG dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) | native confirm |
| AC-43.10 | unit | **`ConfirmModal` dismissal + focus.** Observable: Escape and backdrop click both invoke cancel; initial focus lands on the cancel control; Tab cycles within the dialog; confirm invokes the caller callback exactly once. Chain: `userEvent` keyboard + click. Negative: Escape closes without calling cancel; focus stays on the page behind → fail. | [APG dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/); `G37_RULE` | no focus management |
| AC-43.11 | unit | **Envelope parser is the only reader.** Observable: `UI_QUEUE_LIB_DIR/envelope.ts` returns `{ items, processor? }`, throws on a bare array, and **rejects** any unknown top-level wrapper key per `ENVELOPE_UNKNOWN_KEY_POLICY` (Zod `.strict()`); the rejection surfaces through `ERROR_SURFACE` rather than being swallowed; no queue module calls `.map` on a raw fetch result. Chain: parse fixtures + assert the surfaced error. Negative: array input silently accepted; `{ items: [], nope: 1 }` parsing successfully; an unknown-key rejection that throws without reaching `ERROR_SURFACE` → fail. | `ENVELOPE_UNKNOWN_KEY_POLICY` (AGENTS.md Boundary Input Contract item 4) | treat response as array |
| AC-43.12 | unit | **Per-feature status configs, no unified enum.** Observable: `UI_QUEUE_LIB_DIR/status-config.ts` exports one config per `STATUS_CONFIG_FEATURES` entry, and each config's key set equals that feature's own `JOB_STATUSES` (imported from the feature module, not restated). Chain: compare key sets. Negative: a single cross-feature status union; `Downloading` offered to the convert queue → fail. | `STATUS_CONFIG_POLICY`; verified divergent `JOB_STATUSES` in both controls modules | one merged status enum |
| AC-43.13 | unit | **Standards sweep + registry, pages untouched.** Observable: no raw hex in any `className` under `UI_PRIMITIVES_DIR` / `UI_QUEUE_LIB_DIR`; no `transition-all` or arbitrary `duration-*`; no new `Button` variant or size (`G34_RULE`); no `test.skip`/`.only`/`.todo` in `UNIT_TEST_DIR_UI` (`G36_RULE`); no `TODO`/`FIXME`/`NotImplementedError`; `NEW_TESTIDS` present in `TESTID_REGISTRY`; `PAGE_ISOLATION_CHECK` passes, which is the sole owner of `PAGE_ISOLATION_RULE` — frozen files byte-identical, the two `CARVE_OUT_FILES` limited to `CARVE_OUT_RULE`, no file outside `NEW_SURFACE_EXEMPT` referencing any `NEW_SURFACE_MODULES` string (direct **or** re-exported), the E2E title **set** preserved at `E2E_BASELINE_COUNT`, and every `PRESERVED_TESTIDS` id still in `TESTID_REGISTRY`. Chain: source scans + baseline comparison + registry read. Negative: `ConvertPage.tsx` imports `StatusBadge` this MEU; a barrel re-export reaches it indirectly; a frozen page's markup changes → fail. | `G32_RULE`, `G33_RULE`, `G34_RULE`, `G36_RULE`; AGENTS.md anti-slop; E2 | wire a page early |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| `StatusBadge` / `ProgressBar` are new, not reused | Local Canon | `06-gui.md:1090-1143` specced them; `UI_PRIMITIVES_DIR` contains only `Button` + `SelectInput` |
| `SelectionCheckbox` shape | Local Canon (port) | Zorivest `components/SelectionCheckbox.tsx`, hex fallbacks stripped for `G32_RULE` |
| `StatusBadge` variant-map shape | Local Canon (port) | Zorivest `features/trades/AccountTypeBadge.tsx` |
| Status→token mapping | Human-approved | `USER_LOCKS.pill_palette`: "colour should be whatever it is in the zorivest repo". `STATUS_PILL_TABLE` maps each status onto a token that `PILL_TOKEN_SOURCE` already defines — including Zorivest's `--color-status-{pending,filled,canceled,rejected}` family, which Zorivest declares but never consumes. The proposal's §5 fill/alpha table is superseded where the two disagree |
| Pill label colour | Human-approved + Research-backed | **Reviewer R4-F1, accepted.** The lock is `USER_LOCKS.pill_palette`: av-kit authors no hue. Round 4 read that as *copy Zorivest's chip class* (`bg-<token>/10 text-<token>`) and measured the result at **28 of 80** pairings clearing `CONTRAST_MIN` — light `Paused` 2.23, `Done` 2.47. Shipping 52 unreadable label states is not acceptable, and a tracked debt issue does not make a label readable. Resolution: keep the Zorivest hue on the **fill** and the left-edge **icon**, and take the label from **`--color-fg`** — itself one of the 30 tokens the two repos hold byte-identically, so the lock is still satisfied in full and no hue is av-kit-authored. Measured: **80 of 80** clear `CONTRAST_MIN`, worst `CONTRAST_WORST_MEASURED`. This is also what the proposal's own mockup already does — `.pill.red { background: rgba(255,85,85,.18); color: #ff9e9e; }` (mockup:151) decouples fill from foreground — so the decoupling is Spec-backed, not invented. Shared token **values** are left untouched: no app-wide repoint. The `--color-pill-*-fg` tokens Round 2 invented stay withdrawn. **Interpretive call disclosed at the Step 5c gate:** the user said colour comes from Zorivest; this reads that as Zorivest's *token values*, not Zorivest's *class combination*. |
| Contrast must be verified in both themes | Research-backed | WCAG 1.4.3; proposal §5 "verify ≥4.5:1 in BOTH themes" — implemented as a stylesheet-parsing oracle (`CONTRAST_RULE`) over all four `CONTRAST_BACKDROPS` card states, so no browser is needed and the measured colours are the rendered ones |
| Colour must not be the only status signal | Research-backed | WCAG 1.4.1 |
| Progress must not animate width | Local Canon | `G33_RULE`; current `ChannelCard` `width: ${percent}%` is the violation being retired |
| `indeterminate` is DOM-only | Research-backed | MDN — no HTML attribute; must be set on the node |
| Confirm is a portal with a verb label | Human-approved + Local Canon | `USER_LOCKS.remove_confirm`; `G20_RULE` |
| No unified status enum | Local Canon | verified divergent `JOB_STATUSES` between the two controls modules |
| `buildReorderBody` duplication | deferred | `DEDUP_TARGETS.buildReorderBody` is byte-identical, but both call sites are page-owned; dedup lands with MEU-45 to keep this MEU page-free |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `UI_QUEUE_LIB_DIR/format.ts` | new | single `formatFileSize` |
| `UI_QUEUE_LIB_DIR/status-tokens.ts` | new | `STATUS_PILL_TABLE` record (`slug`/`token`/`fillAlpha`/`fillClass`/`labelClass`/`iconClass`); no hex literals |
| `UI_QUEUE_LIB_DIR/status-config.ts` | new | per-`STATUS_CONFIG_FEATURES` configs |
| `UI_QUEUE_LIB_DIR/envelope.ts` | new | `{ items, processor? }` parser |
| `UI_PRIMITIVES_DIR/StatusBadge.tsx` | new | variant-map badge, always text-labelled |
| `UI_PRIMITIVES_DIR/ProgressBar.tsx` | new | `transform: scaleX` fill + ARIA |
| `UI_PRIMITIVES_DIR/SelectionCheckbox.tsx` | new | ported, token-only |
| `UI_PRIMITIVES_DIR/ConfirmModal.tsx` | new | portal dialog |
| `ui/src/renderer/src/features/converter/ConvertQueueTable.tsx`, `.../downloader/DownloadQueueTable.tsx` | edit | import `formatFileSize` from `UI_QUEUE_LIB_DIR`; delete the local copies. **No other change** — markup and testids stay identical |
| `TESTID_REGISTRY` | edit | add `NEW_TESTIDS` |
| `UNIT_TEST_DIR_UI/queue-primitives.test.ts(x)` | new | AC-43.* |

> The two queue-table edits are the single exception to "pages untouched": they are import-only deletions of a
> duplicated helper, asserted by AC-43.1 and guarded by AC-43.13's testid/E2E-count checks.

---

### MEU-44 — `gui-queue-card`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| `QueueCard` props | TS component contract | `id: string`; `position: number ≥ 1`; `status` ∈ the feature config's keys; `progress?: 0..1`; callbacks optional | excess props are a type error | unknown status → neutral badge (AC-43.5); missing callback → control not rendered, never a no-op button | n/a | proposal §4 |
| `EmptyDropZone` drop payload | component-owned `DataTransfer` read | files only; caller supplies the accept predicate | n/a | rejected drop shows the reason during drag, performs no callback | n/a | proposal §9; [MDN DnD](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) |

No network surface: `QueueCard`, `QueueList` and `EmptyDropZone` are presentational and never call `apiFetch`.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-44.1 | unit | **Zone contract and DOM order.** Observable: a card renders the zones of `QUEUE_CARD_ZONE_ORDER` in that document order, each with its `NEW_TESTIDS` id; optional zones are absent (not empty placeholders) when their data is absent. Chain: render → ordered query. Negative: pill before title; an empty `<div>` standing in for an absent zone → fail. | Spec proposal §4 anatomy | reorder zones per page |
| AC-44.2 | unit | **Card body is an accessible button, checkbox is not nested in it.** Observable: the body region has `role="button"` and `tabIndex=0`; Enter and Space each invoke `onOpen` exactly once; the `selection-checkbox` node is **not** a descendant of that region. Chain: `userEvent.keyboard`. Negative: checkbox nested inside the `role="button"` (invalid nesting, click ambiguity); Space scrolls instead of activating → fail. AC-44.16 extends this ancestry proof to the other two interactive zones, which this AC alone does not cover. | Spec proposal §4; `G37_RULE`; [APG button](https://www.w3.org/WAI/ARIA/apg/patterns/button/) | nest an interactive control in a button |
| AC-44.3 | unit | **State precedence and selection fill.** Observable: with both detail-open and checkbox-selected true the card carries `CARD_STATE_CLASSES['detail-open']`; selected-only carries `CARD_STATE_CLASSES['checkbox-selected']`; neither carries `FORBIDDEN_SELECTION_FILL`; default carries `CARD_STATE_CLASSES.default`. Chain: render each combination. Negative: selected wins over detail-open; `bg-bg-subtle` used → fail. | Spec proposal §4 precedence; `SELECTION_FILL_ALLOWED` | reuse bg-subtle |
| AC-44.4 | unit | **Exactly one primary action, chosen by state.** Observable: the primary slot contains at most `PRIMARY_ACTION_MAX_PER_CARD` control; re-queueable status → Retry; `Done` → Open file; in-flight → Cancel; otherwise the slot is empty. Every rendered control has an accessible name and a `title`. Chain: render per status. Negative: Retry and Open file rendered together; an icon-only control with no accessible name → fail. | Spec proposal §4; `PRIMARY_ACTION_MAP` | render every action on every card |
| AC-44.5 | unit | **Per-card Cancel is queue-level and in-flight-only.** Observable: Cancel renders only when `isInFlight` is true, and clicking it invokes the `onCancelQueue` prop — the same callback name the page will wire to `POST /{queue}/cancel`; there is no per-item cancel prop or path in the component. Chain: render + `userEvent.click`. Negative: Cancel rendered on a `Pending` card; a `cancelItem(id)` prop exists → fail. | Human-approved `USER_LOCKS.per_card_cancel`; `PAUSE_SCOPE` | invent per-item cancel |
| AC-44.6 | unit | **Meta zone is state-dependent.** Observable: in-flight → progress zone present; `Pending` → progress absent and meta shows the queue-position wait text; `Done` → size text; `Failed` → truncated error with the full text in `title`. Chain: render per status. Negative: a 0% bar rendered for `Pending`; full untruncated error breaking the row → fail. | Spec proposal §4 | always render the bar |
| AC-44.7 | unit | **Title/meta truncate with a tooltip.** Observable: title and meta carry a truncation class and a `title` attribute equal to the full string. Chain: render a long string. Negative: truncation without `title` (content unreachable) → fail. | `G7`; Spec proposal §4 | CSS-only ellipsis |
| AC-44.8 | unit | **Kebab menu — per-action applicability, state-correct labels, keyboard.** Observable: the kebab has `aria-haspopup="menu"` and `aria-expanded`; opening renders `queue-card-menu`. Membership follows `KEBAB_MENU_ORDER_SEMANTICS`: `KEBAB_MENU_ORDER` is a list of **action ids** fixing relative order; each id renders with its `KEBAB_ACTION_LABELS` label; an action whose callback is missing or whose `KEBAB_AVAILABILITY` condition is false is **absent from the DOM**, never disabled and never a no-op. Availability is evaluated **per action, never per group**. Four rendered cases, all with every callback supplied: (a) a `Done` job in the middle of a multi-item list — all eight ids, `copy-location` labelled `Copy path`; (b) a `Pending` job **first in a multi-item list** — `copy-location`, `move-down`, `move-bottom`, `remove`, labelled `Copy URL` / `Move down` / `Move to bottom` / `Remove`; the downward moves are **present**, because first-ness excludes only `move-up` and `move-top`; (c) the **only** job in a one-item queue — `copy-location` and `remove` alone, since no move target exists in either direction; (d) a card given only `onRemove` — `Remove` alone. In every case the surviving items appear in `KEBAB_MENU_ORDER` order with `remove` last and styled destructive. `copy-location`'s label and its clipboard payload are asserted **together** in (a) and (b): `Copy path` writes the output path, `Copy URL` writes the source URL, so the item can never name one and copy the other. Escape closes and returns focus to the kebab; arrow keys move between the rendered items. Chain: render each case → `userEvent` keyboard → ordered query → clipboard spy. Negative (each must fail): `open-file` rendered on a `Pending` card; **`move-down` or `move-bottom` missing from a first-but-not-last row** (it would silently strip two promised operations from the top row of every multi-item queue); any item rendered `disabled`/`aria-disabled` instead of omitted; `move-up` present on the first row; `copy-location` labelled `Copy path` while it copies a URL; items out of `KEBAB_MENU_ORDER` order; `remove` not last; menu not closable by keyboard. | Spec proposal §4/§7 (`Copy path/URL`, proposal:78) + mockup:287 (`Copy URL`); `KEBAB_MENU_ORDER_SEMANTICS`, `KEBAB_ACTION_LABELS`, `KEBAB_AVAILABILITY` (reviewer R4-F5, corrected by R5-F2/R5-F4); [APG menu button](https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/) | mouse-only menu; dead menu items; an expected set that drops applicable actions |
| AC-44.9 | unit | **`QueueList` preserves server order and parameterizes row ids.** Observable: cards render in the exact prop order (no client sort); `data-testid="queue-list"`; the per-row testid comes from a prop so Convert and Download can pass their `PRESERVED_TESTIDS` values in MEU-45. Chain: render a shuffled-position list. Negative: list sorts by status or position internally; row testid hardcoded → fail. | Spec proposal §4; Local Canon reorder is server-owned | client-side re-sort |
| AC-44.10 | unit | **`EmptyDropZone` offers a non-drag path.** Observable: renders the dashed zone, microcopy, and an `empty-drop-zone-browse` button that invokes `onBrowse`; the button is reachable by keyboard. Chain: `userEvent.click` + Tab. Negative: drag-only empty state with no Browse affordance → fail. | Spec proposal §9; WCAG dragging-movements alternative | drag as the only path |
| AC-44.11 | unit | **Four drag states with a rejection reason.** Observable: the zone reflects each of `DRAG_STATES`; an invalid drag shows the rejection reason **during** the drag, not after the drop; enter/leave use a counter so child elements do not flicker the state. Chain: fire drag events over a nested child. Negative: state resets on `dragleave` from a child; reason shown only post-drop → fail. | Spec proposal §9; [MDN DnD](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) | leave-on-child bug |
| AC-44.12 | unit | **Non-empty list stays a drop target.** Observable: dragging over a populated `QueueList` shows `queue-drop-overlay` with the compact add prompt and the list remains visible behind it. Chain: fire drag over a populated list. Negative: drop target only in the empty state → fail. | Spec proposal §9 | empty-state-only dropping |
| AC-44.13 | unit | **Standards sweep, no dependency, pages untouched.** Observable: no raw hex in `className`; no `transition-all`/arbitrary durations; no new `Button` variant/size; no `test.skip`/`.only`/`.todo`; no `TODO`/`FIXME`; `ui/package.json` dependencies unchanged (no dnd-kit, no `@tanstack/react-virtual`); no page file imports `UI_QUEUE_COMPONENTS_DIR`; `PRESERVED_TESTIDS` unchanged and the existing E2E specs still total `E2E_BASELINE_COUNT`. Chain: source scans + `package.json` diff. Negative: dnd-kit added "to save time later"; `ConvertPage` imports `QueueList` → fail. | `G32_RULE`, `G33_RULE`, `G34_RULE`, `G36_RULE`; `VIRTUALIZATION_DECISION`; `USER_LOCKS.drag_and_drop` | pull MEU-49 forward |
| AC-44.14 | unit | **Cancel discloses that it stops the queue.** Observable, per `CANCEL_SCOPE_RULE`: the in-flight card's cancel control has accessible name exactly `CANCEL_CONTROL_LABEL` and `title` exactly `CANCEL_CONTROL_TITLE`; the accessible name is not any member of `CANCEL_LABEL_FORBIDDEN` (equality, so `Cancel queue` is not caught by the `Cancel` entry); and activation invokes `onCancelQueue` **directly** — per `CANCEL_CONFIRM_POLICY` the action opens **no** confirmation dialog, because proposal:146-149 puts queue-level Cancel of a re-queueable job on the ladder as explicitly no-dialog. The whole disclosure therefore lives in the label and the title, which is exactly why both are locked strings. Chain: render an in-flight card → `getByRole('button', {name: CANCEL_CONTROL_LABEL})` → assert `title` → `userEvent.click` → assert `onCancelQueue` called once and **no dialog role in the document**. Negative (each must fail): the control is named `Cancel`, `Cancel item`, `Cancel download`, or `Stop`; the `title` is a generic tooltip; clicking opens a `ConfirmModal` or any `role="dialog"` before `onCancelQueue` fires. | Human-approved `USER_LOCKS.per_card_cancel` + Research-backed (reviewer R4-F3); `CANCEL_SCOPE_RULE`; `CANCEL_CONFIRM_POLICY` (reviewer R5-F3); mockup:287 (the mockup's own tooltip was already scope-bearing) | a row-local control named `Cancel`; a confirm dialog on a cheap, re-queueable stop |
| AC-44.15 | unit | **Blocker cards say why they are blocked and what to change.** Observable, per `BLOCKER_META_RULE`: for each status in `BLOCKER_STATUSES` the meta zone renders **both** the job's `error_message` and `BLOCKER_REMEDIATION[status]` verbatim, and **neither string is authored by the component**: the reason is read off the job (produced at the transition by AC-42.11, so a real blocked job carries it) and the remediation comes from the shared map. The two are rendered as distinct elements — reason answers *what happened*, remediation answers *what to change* — so neither can be substituted for the other. Chain: render a `QualityBlocked` card and an `AgeRestricted` card → query the meta zone. Negative (each must fail): a blocker card shows only the pill; the remediation copy is inlined as a string literal in the component (it would drift from the 409 body AC-42.10 asserts); the component substitutes the remediation for a missing reason, masking the AC-42.11 producer bug; `BLOCKER_REMEDIATION` gains a status with no card rendering for it. | Research-backed (reviewer R4-F2); `BLOCKER_META_RULE`; pairs with AC-42.10 (the refusal a user can hit is the refusal the card explains) and with AC-42.11 (the reason exists in production data, not only in the fixture) | a Retry button that legitimately refuses with no on-card explanation |
| AC-44.16 | unit | **No interactive control lives inside the card's open-region.** Observable, per `CLICKABLE_REGION_RULE`: for **every** id in `CARD_INTERACTIVE_ZONES` — `selection-checkbox`, `primary-action`, `kebab-trigger` — the node is present in the card and is **not** a descendant of the `role="button"` region (assert ancestry directly: the open-region element does not contain the control, and the control's nearest `[role="button"]` ancestor is not the open-region). Rendered on a card that has all three: a `Failed` job (primary action = Retry) with selection enabled and a kebab. Each control is then operable **independently**: `Tab` reaches it as its own stop, and activating it by click **and** by keyboard invokes its own callback exactly once while `onOpen` is **not** called. This is the finding's real cost — AC-44.2 proves only the checkbox, and the mockup nests the other two inside `<div class="body">` (mockup:261-277), the element proposal §4 gives `role="button"`. Chain: `userEvent.tab` / `userEvent.click` / `userEvent.keyboard` per `G37_RULE`. Negative (each must fail): the primary action or the kebab trigger renders inside the open-region; activating Retry also fires `onOpen` through bubbling; a control is reachable only by clicking the card first. | Research-backed (reviewer R6-F2) — axe `nested-interactive`, WCAG 2.2 SC 4.1.2, and [HTML §4.10.6](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) forbidding interactive content in `button`; `CLICKABLE_REGION_RULE`; extends AC-44.2 | ship a Retry that also opens the item, and a menu trigger with no independent semantics |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Card anatomy / zone order | Spec | proposal §4 |
| State precedence | Spec | proposal §4; selection fill from `SELECTION_FILL_ALLOWED` |
| Cancel control wording | Research-backed (reviewer R4-F3) | `CANCEL_SCOPE_RULE`. The control sits on one row but stops the whole queue, so its accessible name is locked to `CANCEL_CONTROL_LABEL` and its title to `CANCEL_CONTROL_TITLE`; `CANCEL_LABEL_FORBIDDEN` names the bare strings that would mislead. The mockup's tooltip was already scope-bearing — the AC now matches it |
| Whether Cancel confirms | Spec (reviewer R5-F3) | `CANCEL_CONFIRM_POLICY`. proposal:146-149 assigns queue-level Cancel of a re-queueable job **no dialog** — re-queue is cheap, and the stop is time-sensitive. Round 5 briefly required a confirm as part of the wording fix; that was a scope invention against the Spec and is withdrawn. `ConfirmModal` stays reserved for Remove and Clear |
| Blocker-state card meta | Research-backed (reviewer R4-F2) | `BLOCKER_META_RULE` + `BLOCKER_REMEDIATION`. A blocker row must say why it is blocked and which setting unblocks it, or a legitimately-refused Retry reads as a broken button |
| Kebab applicability | Research-backed (reviewer R4-F5, corrected R5-F2) | `KEBAB_MENU_ORDER_SEMANTICS` + `KEBAB_AVAILABILITY`. `KEBAB_MENU_ORDER` is a relative order over applicable supplied **action ids**, not a membership requirement — the R4 reading forced dead `Open file` / `Move up` items onto a first Pending row, and the R5 expected set over-corrected by dropping `Move down`/`Move to bottom` from that same row. Availability is per action: only a **one-item** queue loses all four moves |
| Copy action label | Spec (reviewer R5-F4) | `KEBAB_ACTION_LABELS['copy-location']`. The proposal writes it `Copy path/URL` (proposal:78) and the mockup renders it `Copy URL` (mockup:287); before an output path exists the action copies the source URL. One canonical id and order slot, label chosen by state — a fixed `Copy path` would name something other than what it puts on the clipboard |
| One state-dependent primary action | Spec | proposal §4; `PRIMARY_ACTION_MAP` |
| Cancel is queue-level, in-flight only | Human-approved | `USER_LOCKS.per_card_cancel`; `PAUSE_SCOPE` |
| Kebab contents/order | Spec + Research-backed | proposal §4/§7; APG menu-button keyboard contract |
| Card body activation semantics | Research-backed | APG button — Enter and Space both activate; interactive controls must not nest |
| Empty state + four drag states | Spec | proposal §9 |
| Drag counter to avoid child flicker | Research-backed | MDN DnD event model |
| No virtualization | Local Canon | `VIRTUALIZATION_DECISION`; lists are far below `VIRTUALIZATION_THRESHOLD` |
| Reorder still server-owned | Local Canon | `buildReorderBody` sends a full permutation; the list must not re-sort |
| No page migration here | Local Canon | grouping Session 20 vs 21 |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `UI_QUEUE_COMPONENTS_DIR/QueueCard.tsx` | new | two-row card, `QUEUE_CARD_ZONE_ORDER` |
| `UI_QUEUE_COMPONENTS_DIR/QueueCardMenu.tsx` | new | kebab menu; `KEBAB_MENU_ORDER` ids + `KEBAB_ACTION_LABELS` + `KEBAB_AVAILABILITY` |
| `UI_QUEUE_COMPONENTS_DIR/QueueList.tsx` | new | ordered list + drop overlay |
| `UI_QUEUE_COMPONENTS_DIR/EmptyDropZone.tsx` | new | dashed zone + Browse + `DRAG_STATES` |
| `TESTID_REGISTRY` | edit | card/list/empty ids from `NEW_TESTIDS` |
| `UNIT_TEST_DIR_UI/queue-card.test.tsx` | new | AC-44.* |

Do **not** modify `packages/`, `mcp-server/`, `OPENAPI_COMMITTED` (except MEU-42's regen), or any file under
`ui/src/renderer/src/features/*/Page*.tsx`.

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Capture inbox card treatment | out-of-scope | — | proposal §1 — `CaptureInbox` is a thumbnail filmstrip, not a work queue |
| Convert page migration + toolbar 13→4 | deferred | MEU-45 | `GROUPING_FILE` Session 21 |
| Downloader page migration + summary bar | deferred | MEU-46 | `GROUPING_FILE` Session 21 |
| Selection model, `BulkActionBar`, shift-click, Ctrl/Cmd-A, Clear finished | deferred | MEU-47 | `GROUPING_FILE` Session 21; `USER_LOCKS.bulk_bar_placement` / `clear_finished` |
| Transcript `ChannelCard` G33 fix; TTS `ProgressBar` | deferred | MEU-48 | `GROUPING_FILE` Session 22 |
| dnd-kit drag reorder + live-region announcements | deferred | MEU-49 | `USER_LOCKS.drag_and_drop`; proposal §8 phase 2 |
| Undo-toast after Remove | out-of-scope | — | `USER_LOCKS.remove_confirm` — the API cannot restore a removed job; confirm-first instead |
| Density toggle | out-of-scope | — | `USER_LOCKS.density_toggle` — single density |
| Per-item cancel or per-item pause endpoint | out-of-scope | — | `PAUSE_SCOPE` (`06-gui.md:503-524`); `USER_LOCKS.per_card_cancel` |
| Bulk REST endpoint | out-of-scope | — | `BULK_ENDPOINT_POLICY` — none exists; client fan-out only |
| Re-queue from `Skipped` or `Done` | out-of-scope | — | `USER_LOCKS.retry_scope`; `NON_REQUEUEABLE_*_STATUSES` |
| Renaming `reset_failed` / adding a `/retry` path | out-of-scope | — | `ROUTE_COUNT_AFTER` + `ACTION_INDEX_AFTER` flatness; MCP `reset` action mapping |
| `ports/storage.py` + `repositories.py` `reset_failed` | out-of-scope | — | repository bulk method asserted by `tests/unit/test_domain.py:1386` protocol census |
| `mcp-server/` edits | out-of-scope | — | `MCP_CHANGE_BASIS` |
| Repointing `--color-status-pending` | deferred | MEU-45, MEU-46 | tokens here are additive; pill recolor rides with the migration |
| `buildReorderBody` dedup | deferred | MEU-45 | `DEDUP_TARGETS.buildReorderBody`; both call sites are page-owned |
| Session 22 `/create-plan` (`p10-queue-card-convergence`) | deferred | MEU-48 | `GROUPING_FILE` order |
| List virtualization | out-of-scope | — | `VIRTUALIZATION_DECISION`; no new dependency |
| New Playwright wave | deferred | MEU-45 | `E2E_NEW_WAVES_THIS_SESSION` = 0 — no page-visible control is added; E2 met by component tests + existing waves green |
| Session 21 `/create-plan` (`p10-queue-card-migration`) | deferred | MEU-45 | `GROUPING_FILE` order; `HUB_NEXT_AFTER` |

---

## BUILD_PLAN.md Audit

This project **does** update the hub, and it is the **first plan to register a new phase**. WP-HUB0 adds a
Phase 10 record to `SSOT` (band `BAND`, source `PHASE10_SPEC`, `execution_plans` = [`PLAN_FOLDER_SLASH`];
`PRIOR_PLAN_SLASHES` is empty because the phase is new), adds `PHASE10_MEU_IDS` as MEU records, adds
`MATRIX_ROWS` to `MATRIX`, binds `MEUS` to `PLAN_FOLDER`, and regenerates via `meu_status.py render`.
WP-HUB1 rewrites the hub `Next` field from `HUB_NEXT_BEFORE` to `HUB_NEXT_AFTER`. AUTOGEN tables are never
hand-edited. Do **not** mark `GROUPING_FILE` Session 20 complete until H2 after exec `approved`
(`GROUPING_DONE_MARK`).

```powershell
rtk proxy uv run python -c "from pathlib import Path; import json, re, sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-28-p10-queue-card-foundations'; SLASH=PLAN+'/'; sets=json.loads(Path(PLAN+'/named-sets.json').read_text(encoding='utf-8')); NEXT=sets['HUB_NEXT_AFTER']; ALL=sets['PHASE10_MEU_IDS']; MEUS=sets['MEUS']; data=load(); p10=next((p for p in data['phases'] if str(p['id'])=='10'), None); p10 is None and sys.exit('phase 10 missing'); eps=list(p10.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 10 missing PLAN_FOLDER_SLASH'); miss=next((k for k in ALL if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

---

## Verification Plan

> Classify every command through `.agent/docs/output-evidence-policy.md`. Exact-evidence: `rtk proxy`.
> Capture `$LASTEXITCODE` immediately, before any `Get-Content`.

### 1. UI Red oracle (MEU-41, MEU-43, MEU-44)

Run per MEU with `-Meu 41 | 43 | 44`; the receipt names carry the MEU number (`RED_TXT` / `RED_JSON`).

```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npx vitest run --allowOnly=false --reporter=default --reporter=json --outputFile=C:/Temp/av-kit/fail-to-pass-meu-41-ui.json; exit $LASTEXITCODE } *> C:/Temp/av-kit/fail-to-pass-meu-41-ui.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'UI Red unexpectedly green'; Get-Content C:/Temp/av-kit/fail-to-pass-meu-41-ui.txt; exit 1 }; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-28-p10-queue-card-foundations/assert-red-oracle.ps1 -Kind ui -Meu 41 -Receipt C:/Temp/av-kit/fail-to-pass-meu-41-ui.txt -JsonReceipt C:/Temp/av-kit/fail-to-pass-meu-41-ui.json *> C:/Temp/av-kit/red-oracle-meu-41.txt; $ocode=$LASTEXITCODE; Get-Content C:/Temp/av-kit/red-oracle-meu-41.txt; if ($ocode -ne 0) { Get-Content C:/Temp/av-kit/fail-to-pass-meu-41-ui.txt | Select-Object -Last 40; exit $ocode }; 'PASS: FAIL_TO_PASS red'; exit 0
```

### 2. Python Red oracle (MEU-42)

```powershell
rtk proxy uv run pytest tests/unit tests/e2e/test_api_downloads.py tests/e2e/test_api_conversions.py --tb=short -q *> C:/Temp/av-kit/fail-to-pass-meu-42-py.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'Python Red unexpectedly green'; Get-Content C:/Temp/av-kit/fail-to-pass-meu-42-py.txt; exit 1 }; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-28-p10-queue-card-foundations/assert-red-oracle.ps1 -Kind py -Meu 42 -Receipt C:/Temp/av-kit/fail-to-pass-meu-42-py.txt *> C:/Temp/av-kit/red-oracle-meu-42.txt; $ocode=$LASTEXITCODE; Get-Content C:/Temp/av-kit/red-oracle-meu-42.txt; if ($ocode -ne 0) { Get-Content C:/Temp/av-kit/fail-to-pass-meu-42-py.txt | Select-Object -Last 40; exit $ocode }; 'PASS: FAIL_TO_PASS red'; exit 0
```

> **No pytest JSON plugin is required or used.** `-Kind py` parses the plain `-Receipt` text, matching both
> the dotted id (`AC-42.2`) and the snake form pytest emits in node ids (`test_ac_42_2_*`), on `FAILED` /
> `FAIL` / `AssertionError` lines. `-JsonReceipt` is a UI-only input and is not passed here. This path is
> proven by `RED_SELFTEST` cases `py-text-snake`, `py-text-multi-id`, `py-unrelated-only`, and
> `py-collect-error`, which run at task row 1 before any Red row.

### 3. Python Green / MEU-42 gate

```powershell
rtk proxy pwsh -NoProfile -Command { rtk proxy uv run pytest tests/unit tests/integration tests/e2e -x --tb=short -q; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; rtk proxy uv run pyright packages/; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; rtk proxy uv run ruff check packages/ tests/; exit $LASTEXITCODE } *> C:/Temp/av-kit/py-green-meu-42.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/py-green-meu-42.txt | Select-Object -Last 40; exit $code
```

### 4. UI Green / MEU gate (MEU-41, 43, 44)

```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npx tsc --noEmit; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx vitest run --allowOnly=false; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx eslint src/ tests/ --max-warnings 0; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm run build; exit $LASTEXITCODE } *> C:/Temp/av-kit/ui-green.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ui-green.txt | Select-Object -Last 40; exit $code
```

### 5. OpenAPI drift

`OPENAPI_EXPORT` is the sole generator. MEU-42 regenerates (`-o`) because the route docstrings change; every other MEU uses `--check` only.

```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

### 6. Page-isolation + E2E-baseline oracle (proves "nothing wired")

Sole executable owner of `PAGE_ISOLATION_RULE` is `PAGE_ISOLATION_CHECK`.

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-28-p10-queue-card-foundations/assert-page-isolation.ps1 *> C:/Temp/av-kit/page-isolation.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/page-isolation.txt; exit $code
```

> **This tree is not a git work tree**, so there is no `git diff` to compare against. The oracle is instead
> capture-then-verify: task row 1 runs it with `-Capture` **before any edit**, writing `PAGE_BASELINE`
> (SHA-256 per frozen file, plus the carve-out files' line sets, testid multisets, and the E2E title set).
> Every later run verifies against that baseline. MEU-43's two edits to `ConvertQueueTable.tsx` /
> `DownloadQueueTable.tsx` stay legal only under `CARVE_OUT_RULE`: added lines must be `import` lines
> containing `CARVE_OUT_ALLOWED_IMPORT`, removed lines must lie inside the local
> `CARVE_OUT_REMOVABLE_SYMBOL` block, and the `data-testid` multiset must be unchanged — so replacing table
> markup inline is rejected. Reachability is inverted rather than blacklisted: no file under
> `REACHABILITY_SCAN_ROOT` outside `NEW_SURFACE_EXEMPT` may **resolve** an import specifier to any
> `NEW_SURFACE_MODULES` entry, which also closes the barrel/re-export bypass. Resolution, not
> substring-matching of file text, is what makes that true: this repo imports relatively (`../../components/ui/Button`), so a barrel at
> `components/index.ts` re-exporting `'./queue/QueueCard'` contains no `components/queue/` substring at all
> and raw text matching could not have seen the very bypass it was written to close. Matching is against the
> resolved suffix, not the exempt directory, so pre-existing neighbours such as `components/ui/Button` stay
> legal while the two new `components/ui/*` modules do not. The carve-out files are the single sanctioned
> doorway into the new surface, and only for `CARVE_OUT_ALLOWED_IMPORT`. `FROZEN_RATIONALE` states the
> VCS substitute once: `FROZEN_GLOBS` byte-freezes `mcp-server/src/**/*.ts`, `ui/package.json`, and
> `ui/package-lock.json` for the whole session, proving `MCP_CHANGE_BASIS` and the no-new-dependency rule
> by content. The E2E half of the baseline is a title **set** plus count (`E2E_BASELINE_BASIS`), so a
> rename that holds the count constant is still rejected.

**Negative direction is proven, not asserted (R1-F2).** A gate that only ever reports PASS on an unchanged
tree proves nothing, so `PAGE_ISOLATION_SELFTEST` builds a synthetic fixture repo under `SELFTEST_DIR`,
captures a baseline from it, applies **one** mutation per case, and asserts this same script rejects it *with
the expected reason*. Task row 1 runs it **before** `-Capture`, because a baseline recorded by an unproven
oracle is worthless. The case list — 17 rejections and 2 accepts, one mutation class each — is enumerated
once, in `PAGE_ISOLATION_SELFTEST`, and is not restated here; the script prints the count it actually ran, so
a case added or dropped without updating that key is visible on the receipt rather than only in prose.

Writing it immediately paid for itself: the self-test failed on first run and exposed two silent defects in
the oracle that the positive path can never surface. (1) `'\\'` in a PowerShell single-quoted string is
**two** backslashes, so `.Replace('\\','/')` was a no-op on `Split-Path` output — every parent segment was
dropped and each relative specifier resolved to a bare suffix, making the whole reachability rule vacuous.
(2) `.Split(@([char]92,[char]47))` binds the wrong overload without an explicit `[char[]]` cast and returned
the path unsplit. Both now have named-regression cases. This is the same failure class the reviewer flagged
in R1-F1/F2 — a control that looks correct and enforces nothing — caught here by testing the control instead
of trusting it.

### 7. Existing Playwright waves stay green (or `[B]` `E2E_SANDBOX`)

```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npm run build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx playwright test; exit $LASTEXITCODE } *> C:/Temp/av-kit/e2e-regression.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e-regression.txt | Select-Object -Last 40; exit $code
```

---

## Stop Conditions

1. **DONE** — every `task.md` row `[x]` or valid `[B]`; exec review `approved`; closeout artifacts pass markers.
2. Plan-review round cap **`PLAN_REVIEW_MAX_ROUND`** — HARD STOP, present remaining-risk buckets.
3. Exec-review round cap **`EXEC_REVIEW_MAX_ROUND`** — HARD STOP.
4. All CLI reviewer rungs rate-limited — HARD STOP; never self-review.
5. **Human-decision gate at Step 5c** — `PLAN_TO_EXEC_GATE` is `human` by explicit user decision. On Codex
   `approved`, present the verdict and **end the turn**; execution begins only on the user's next explicit
   chat message.
6. `~50%` context checkpoint — finish the current MEU handoff, compact, continue.

Do not stop after writing this plan. Auto-dispatch `/plan-critical-review`. Do not run project tests,
generators, or `tools/` scripts during plan review (`GUARDRAILS.md` SIGN 1).
