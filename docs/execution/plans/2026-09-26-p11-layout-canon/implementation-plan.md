---
project: "2026-09-26-p11-layout-canon"
date: "2026-09-26"
source: "docs/BUILD_PLAN.md Phase 11; .agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md"
meus: ["MEU-50", "MEU-51"]
status: "approved_for_execution"
template_version: "2.0"
---

# Implementation Plan: Phase 11 Layout Canon and Shared Primitives

> **Project:** `2026-09-26-p11-layout-canon` (Session 23)
> **Build plan:** Phase 11 in `docs/BUILD_PLAN.md`; MEU-50 authors `docs/build-plan/11-page-layout.md`
> **Status:** Round 2 approved by independent GPT-6 Astra reviewer; user authorized execution on 2026-09-26

## Goal

Create the source of truth for the six page-layout mockups, lock all 37 decisions in their §06 sections, and implement the five unwired shared primitives assigned to MEU-51. MEU-49 is `approved` in `.agent/context/meu-status.yaml`; MEU-50/51 were approved after the independent Round 2 execution review on 2026-09-26. This session mounts the primitives only in a test-only Electron harness for E2E assertions; no product page imports them. Sessions 24–26 own product page composition and runtime wiring.

The Phase 11 product lock is `docs/BUILD_PLAN.md` §Locked decisions: composition only, with the same IPC, mutations, enablement rules, and a keep/move/change accounting for every existing test ID. The six mockups and [Phase 11 grouping](../../../../.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md) are the design inputs. The completed Phase 10 `QueueCard`/`QueueList` work and `QUEUE_SCROLL_CONTAINER_RULE` are frozen inputs, especially the controls-pane-yields clause documented in the MEU-49 reflection §Next Day Outline.

### Human-approved H1-2 gate repair amendment (2026-09-26)

The user explicitly authorized **repair of the five existing Electron E2E failures in this session** after the first full gate reported 79 passed and six failed (`C:/Temp/av-kit/p11-e2e-inner.txt`). The sixth was this session's harness test selector precondition and passed its targeted rerun after correction. The five remaining failures are Capture `W9-3`, `W9-4`, `AC-59.12`, `AC-60.12`, and Downloader `W1-9`. The original Phase 11 no-product-page-edit scope remains the product design boundary; this user-approved amendment allows the narrow test setup/fixture or product behavior repairs needed to restore those existing contracts, with no altered behavioral assertion or silent feature change. Their failing E2E cases are the Red evidence. Run each affected case after its repair, then rerun the full Electron gate before H1-3. Record every changed file and receipt in `walkthrough.md` and reconcile both MEU handoffs before independent review. This amendment does not authorize page composition or MEU-52–58 work.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "Both graphs absent in planning and execution (C:/Temp/av-kit/p11-tool-inventory.txt; p11-exec-context-inventory.txt); six short HTML sections, docs, TSX internals, and exact test/build receipts; no eligible approved Headroom payload"
  human_message_reference: null
```

Execution re-evaluation (2026-09-26): `graphify-out/graph.json` and `graphify-out-research/graph.json` are still absent (`C:/Temp/av-kit/p11-exec-context-inventory.txt`). MEU-50 reads the six short mockup sections and exact source text; MEU-51 edits TSX internals, and the expected test/build receipts are exact-evidence bypasses. No eligible Headroom payload or active approved compression disposition applies. Decision: `not_applicable` for execution; no human tool choice is needed.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-50 | `.agent/context/handoffs/2026-09-26-p11-layout-canon-MEU-50-handoff.md` |
| MEU-51 | `.agent/context/handoffs/2026-09-26-p11-layout-canon-MEU-51-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-09-26-p11-layout-canon-implementation-critical-review.md`. Rolling plan review: `.agent/context/handoffs/2026-09-26-p11-layout-canon-plan-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Freeze the 37-choice register and source-backed FIC for MEU-50 | — | `shared` | This plan and `task.md` |
| WP-2 | Red canon tests, then Phase 11 spec, tokens, supersession pointers, and TR1 grouping/SSOT description reconciliation | WP-1 | `shared` | `11-page-layout.md`, `layout-canon.test.ts`, grouping/SSOT edits, Red receipt |
| WP-3 | MEU-50 targeted gate and handoff | WP-2 | `compact_continue` | MEU-50 handoff; compact and re-read `task.md` plus handoff |
| WP-4 | Red primitive unit/E2E assertions, then five unwired primitives and test ID registration | WP-3 | `shared` | TSX components, `layout-primitives.test.ts`, `layout-primitives.test.ts` E2E, Red receipt |
| WP-5 | Wire isolated Electron harness, run real Electron E2E, MEU-51 targeted gate and handoff | WP-4 | `compact_continue` | Harness build/E2E receipts and MEU-51 handoff; compact and re-read `task.md` plus handoff |
| WP-6 | H1 closeout, independent execution review, H2 closeout | WP-5 | `shared` | Gate/dispatch receipts, rolling verdict, reflection, metrics |

No worker is authorized by this Codex driver profile. `isolated` rows are therefore not used for implementation. The independent CLI reviewer is a separately dispatched review process, never the implementer.

## User Review Required

No new product behavior is proposed. The user explicitly chose Option 1 on 2026-09-26: a reachable Electron-only primitive harness and E2E assertions in Session 23. That `Human-approved` scope decision resolves the grouping's no-new-wave wording against `create-plan.md` §4A and emerging standard E2. The harness is test-only, and product pages remain unwired. The 37 §06 forks are resolved below by the existing Phase 11 composition lock, the mockups' explicit visual proposal, and the live Phase 10/GUI contracts. A finding that those sources cannot settle a material product choice is a human-decision gate in the review loop, not permission to invent behavior during execution. Review approval remains separate from the plan-to-execution gate; this Codex driver is not the Cursor override in `.agent/context/harness.local.md`, so the conservative `human` gate applies.

## Proposed Changes

### Authority and single-statement rules

| Name | One definition used by every AC/task |
|---|---|
| `COMPOSITION_LOCK` | Preserve existing IPC, API payloads, persisted mutations, enablement and save behavior, and all existing test IDs. A mockup may rearrange or restyle a control. The explicitly scheduled Convert staged-file × changes only local pre-Add staging, never the backend contract. Source: `docs/BUILD_PLAN.md:98`, grouping:9–13,83. |
| `PAGE_ORDER` | Downloader, Convert, Transcript, TTS, Capture, Settings; the six 2026-09-03 mockups in this order. |
| `DECISION_SET` | `DL1–DL4`, `CV1–CV7`, `TR1–TR6`, `TT1–TT7`, `CP1–CP6`, `ST1–ST7` = exactly 37 entries, each recorded once in the Phase 11 canon with choice, basis, owner MEU, and test-ID effect. |
| `QUEUE_SCROLL_CONTAINER_RULE` | Page root `h-full min-h-0`; queue region `flex-1 min-h-[20rem]`; `overflow-auto` on the page wrapper around `QueueList`, never on the list; controls above the queue form one `min-h-0 overflow-auto` pane that yields height, with `shrink-0` summary/toolbar. Source: both queue mockups §04 and MEU-49 reflection:220–227. |
| `PRESERVED_TESTIDS` | The union of existing IDs in `ui/tests/e2e/test-ids.ts` and each mockup §05 keep/move/change inventory. MEU-50 records mapping; MEU-51 adds only names for its own primitives. Consumer MEUs preserve their inherited IDs. |
| `COLUMN_CAP` | `--layout-page-max-width: 72rem` (1152 px) defined once in `ui/src/renderer/src/styles.css` and referenced by the canon for Downloader, Convert, Transcript, TTS, and Capture; Settings retains its narrower 960 px cap from its mockup §04. No new hue or duplicate light-theme geometry declaration. |
| `PRIMITIVES` | `Disclosure`, `SegmentedControl`, `StatusChip`, `FormRow`, `PathRow`, all under `ui/src/renderer/src/components/ui/`; no imports in page files this session. |
| `GUI_RULES` | G30–G37 and E2 from `.agent/docs/emerging-standards.md`; Button's current five variants/three sizes, SelectInput's G30 helper, existing theme/motion tokens. The workflow's `docs/gui-element-reference.md`, three GUI indexes, and `.agent/docs/gui-standards-enforcement.md` are absent in this tree; do not cite them as live authority. |
| `E2E_HARNESS` | A second renderer HTML entry is added only when build-time `AVKIT_PRIMITIVE_HARNESS_BUILD=1`; unset uses the ordinary product entry alone and any other nonempty value fails the build. Build the harness to `ui/out-e2e`, never `ui/out`. `ui/electron-builder.yml` packages only `out/**/*`; product build and packaged app must contain no harness HTML/entry. The test uses real Electron main from `out-e2e`, creates a separate BrowserWindow for the harness HTML, and asserts the five real primitive imports and interactions. `AVKIT_E2E_OUT_DIR` in global setup is allowlisted to `out` (default) or `out-e2e`; any other value fails before launch. Product router/main/preload and page imports stay unchanged. Source: Human-approved 2026-09-26 Option 1; `create-plan.md` §4A; emerging standard E2; local `electron.vite.config.ts`, `electron-builder.yml`, Electron E2E conventions. |
| `RED_ORACLE` | For each MEU, Vitest JSON reporter output must exist for exactly the named test file, report at least the number of ACs in that MEU as collected tests, include a test title for every AC ID, have at least one failed AC assertion whose `failureMessages` contains `AssertionError`, have no file-level collection error, and have zero pending/todo tests. A nonzero Vitest exit alone is insufficient. Test files must avoid top-level imports of files not yet created so assertion tests collect in Red. The JSON reporter fields are present in the installed Vitest 3 reporter (`ui/node_modules/vitest/dist/chunks/index.VByaPkjc.js`). |
| `SESSION_DIGEST` | `.agent/context/sessions/01a0de0f-2c40-7331-95a0-6d2a43a3e438/digest.md`, using the current `CODEX_THREAD_ID`/`CODEX_SESSION_ID` receipt `C:/Temp/av-kit/p11-session-ids.txt`. If execution resumes in a different conversation, update this plan and `task.md` to that conversation's actual ID before H2-3. |

### MEU-50 — `canon-page-layout`

#### Decision register to write into `11-page-layout.md`

Every row is a **plan choice** for MEU-50 to promote into the spec. `M` means the mockup's proposed presentation, `C` the current behavior under `COMPOSITION_LOCK`, and `G` a grouping/Phase 10 constraint. The source for each row is the named mockup's §06 plus the cited §04/§05 where applicable. These are not permission to change the existing wire contract.

| ID | Locked choice for the Phase 11 canon | Owner |
|---|---|---|
| DL1 | Advanced opens initially only when cookie mode is not `none` or SABR is active; subsequent toggle is local presentation state (M). | MEU-53 |
| DL2 | Show nonzero status chips in the header; preserve the full eight-count data in the existing summary model and make it accessible in the More read-only summary (M+C). | MEU-52 |
| DL3 | One page-agnostic queue header component mounts on Downloader and Convert in the same MEU (G). | MEU-52 |
| DL4 | Show active SABR as a warning chip beside Quality, with the same state and controls retained in Advanced (M+C). | MEU-53 |
| CV1 | Staged files become removable chips; × removes one path from local pre-Add staging only and issues no API request (M+G). | MEU-54 |
| CV2 | Add label includes the staged count when nonzero; keep its existing action and test ID (M+C). | MEU-54 |
| CV3 | Keep the editable Output folder row and explicit Save on Convert; Settings keeps its own explicit Save (C). | MEU-54 |
| CV4 | Save is ghost while clean and primary when dirty, with the existing dirty-dot semantics (M+C). | MEU-54 |
| CV5 | Retain the exact `gpuChipLabel` strings; change container styling only (C). | MEU-54 |
| CV6 | Show one Refresh GPU control next to the chip at all times; remove the hidden duplicate only if the same command remains reachable (M+C). | MEU-54 |
| CV7 | Card line two uses only task metadata already carried by the queue item; fall back to task kind when preset/encoder are absent, with no new API field (C). | MEU-54 |
| TR1 | Three toolbar actions (Start, Pause/Resume, Stop); no new Clear finished action or empty fourth overflow (C). | MEU-55 |
| TR2 | One Pause/Resume node switches the two existing test IDs and labels according to state (M+C). | MEU-55 |
| TR3 | Opening a card menu also selects that card, preserving the single-select model (M+C). | MEU-55 |
| TR4 | Card links/menu show only actions already available for that status; preserve current route/IPC and hide unavailable actions (C). | MEU-55 |
| TR5 | Processing line three shows last title; other cards show output root with raw/compiled paths available through the preserved output-tree affordance/accessible text (M+C). | MEU-55 |
| TR6 | Transcript remains single-select; no checkbox/bulk action is introduced by MEU-55 (G+C). | MEU-55 |
| TT1 | Keep native format `<select>` and `format-select` ID inside the new row (C, G30). | MEU-56 |
| TT2 | Humanize cleanup step labels while preserving the exact API values (M+C). | MEU-56 |
| TT3 | Shorten the visible loaded-model chip; retain full variant/device/bytes in accessible details within Manage (M+C). | MEU-56 |
| TT4 | Render Open file/folder only when an output exists, retaining both action IDs when rendered (M). | MEU-56 |
| TT5 | Keep the idle “No output yet” text in a muted run-bar slot so the empty state is explicit (C). | MEU-56 |
| TT6 | No voice preview control; no endpoint exists and Phase 11 adds no API (C). | MEU-56 |
| TT7 | Run bar stays static below the columns, not viewport-sticky (M). | MEU-56 |
| CP1 | Save overlay appears only when dirty; the existing `capture-save` ID is present when actionable (M+C). | MEU-57 |
| CP2 | Hotkey key cap sits inside the Capture button when registered; no fake key cap when unregistered (M). | MEU-57 |
| CP3 | Keep the page-level Settings disclosure and the Settings-page controls; same existing save targets (M+C). | MEU-57 |
| CP4 | Filmstrip strips date from the visible name and shows time below; full original name remains accessible (M). | MEU-57 |
| CP5 | Keep tools visible but disabled when no shot is selected, matching current enablement (C). | MEU-57 |
| CP6 | `capture-status` remains the existing error/status channel; optional shot info is separate display text and never masks errors (C). | MEU-57 |
| ST1 | Style the existing native cookie radios as a segment; keep their IDs and radio behavior (C, G30). | MEU-58 |
| ST2 | Label the existing autosave, explicit-save, and immediate-apply sections; do not unify their mutations (C). | MEU-58 |
| ST3 | Rail active state follows scroll by IntersectionObserver, with click/keyboard navigation and a no-observer fallback (M). | MEU-58 |
| ST4 | Number hints are sourced field by field from existing `06-gui.md`/settings validation; no invented unit or range (C). | MEU-58 |
| ST5 | Checkbox explanation copy is written only where a source-backed statement exists; otherwise keep the HelpCard link instead of speculative prose (C). | MEU-58 |
| ST6 | Keep Audio format enabled when Audio only is off, because disabling it would change the existing enablement rule (C). | MEU-58 |
| ST7 | Readiness count and rail warning use the existing readiness state only; show no fabricated count before it loads (C). | MEU-58 |

For every row, the spec cites its mockup path/§06 and the `COMPOSITION_LOCK` where it overrules a mockup option. The spec also carries a `§Supersession` table linking `06-gui.md`, `08-video-conversion.md`, `09-screenshot-capture.md`, and `10-queue-card-ui.md`; the two closed MEU-48 ACs explicitly transfer to MEU-55 (`ChannelCard` shared primitives, no percentage-width motion) and MEU-56 (shared `ProgressBar`). No former behavior silently disappears.

#### Boundary Inventory

MEU-50 writes documentation and CSS tokens only. No REST/MCP/file-import/env/UI payload boundary is introduced. The spec must record that MEU-51 is presentational and that later page MEUs retain the existing boundary schemas; Phase 11 cannot alter API validation or 422 mapping.

#### Acceptance Criteria

| AC | Type | Description and observable/call chain | Source | Negative Test |
|---|---|---|---|---|
| AC-50.1 | unit | `layout-canon.test.ts` finds `docs/build-plan/11-page-layout.md` with sections `Scope and non-goals`, `Decision register`, `Shared layout primitives`, `Queue header row`, six page sections, `Supersession`, `Test-ID migration`, and `Verification`; each of `DECISION_SET` appears exactly once as a decision row with owner and basis. | Local Canon grouping:63–87; six mockups §06 | Missing/duplicated decision ID or blank basis fails. |
| AC-50.2 | unit | The canon states `COMPOSITION_LOCK`; every decision that chooses existing behavior over new mockup behavior cites it, and a mechanical census confirms no new API endpoint, persisted mutation, or enablement rule is asserted as Session 23 work. `CV1` is named as a local-only pre-Add edit. | Spec `docs/BUILD_PLAN.md:98`; Local Canon grouping:9–13,83 | A staged-file × that calls the backend, or a new Transcript delete fan-out in Session 23, fails. |
| AC-50.3 | unit | `QUEUE_SCROLL_CONTAINER_RULE` appears once in the canon with all four clauses, and the Downloader/Convert mockup §04 source links and MEU-49 reflection are named. | Local Canon MEU-49 reflection:220–227; mockups §04 | Dropping controls-pane-yields or moving `overflow-auto` onto `QueueList` fails. |
| AC-50.4 | unit | Each mockup §05 has a keep/move/change mapping into its owner MEU, tied to `PRESERVED_TESTIDS`; closed MEU-48 ACs appear under Supersession with MEU-55/56 owners. The canon's TR1 three-action choice is reconciled in the grouping and MEU-55 SSOT description; H1-3 then renders that source to the generated registry. | Local Canon grouping:22–59; mockups §05; `COMPOSITION_LOCK` | Missing existing ID, lost inherited AC, or live four-slot MEU-55 instruction in source fails. |
| AC-50.5 | unit | `COLUMN_CAP` is declared once and canonically referenced; zone/form-grid/disclosure/segment/chip/save-caption vocabulary is recorded once. CSS color/motion uses existing theme tokens, with no raw hex or geometric animation in new rules. | Local Canon grouping:33,79; mockups §04; `GUI_RULES` | A second cap value, hardcoded dark-only color, or `transition-all` fails. |
| AC-50.6 | integration | The existing `docs/BUILD_PLAN.md` opening and Phase Specs links resolve to the new `11-page-layout.md`; hand-maintained spec-status prose uses the exact postcondition in the BUILD_PLAN audit, while generated tracker rows remain owned by `tools/meu_status.py`. Chain: source doc → live hub link/status → render/check receipt. | Local Canon `docs/BUILD_PLAN.md:34,36,119`; create-plan §4 | Link target absent, old “registered, not yet specced” prose retained, or generated status manually altered fails. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Phase/scope, MEU order, no page mount | `Spec` | `docs/BUILD_PLAN.md:98`; grouping:63–87, 144–162 |
| All §06 choices | `Local Canon` + `Spec` | Each choice is fixed by the mockup's proposed presentation subject to `COMPOSITION_LOCK`; full `DECISION_SET` above becomes `11-page-layout.md` canon. |
| Scroll geometry | `Local Canon` | Both queue mockups §04, approved MEU-49 reflection:220–227 |
| Disclosure keyboard/ARIA | `Research-backed` | W3C APG Disclosure: https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/ |
| Native radio segment semantics | `Research-backed` | W3C APG Radio Group: https://www.w3.org/WAI/ARIA/apg/patterns/radio/ |
| Closed MEU-48 transfer | `Local Canon` | Grouping:38–59; `.agent/context/meu-status.yaml` MEU-48 closed_reason |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `docs/build-plan/11-page-layout.md` | new | Phase 11 canon and 37 decisions |
| `ui/tests/unit/layout-canon.test.ts` | new | Red-first canon/supersession/token oracles |
| `ui/src/renderer/src/styles.css` | modify | Declare `COLUMN_CAP` once in `:root`; no new hues or light-theme duplicate |
| `docs/BUILD_PLAN.md` | modify | Verify existing Phase 11 links resolve after canon creation; reconcile hand-maintained status prose |
| `docs/build-plan/06-gui.md`, `08-video-conversion.md`, `09-screenshot-capture.md`, `10-queue-card-ui.md` | modify | Short supersession pointers only; preserve historical behavior text |
| `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md` | modify | Reconcile MEU-55 four-slot shorthand with canonical TR1; preserve historical grouping rationale |
| `.agent/context/meu-status.yaml` | modify | Reconcile MEU-55 description with TR1 and bind/update MEU-50/51 through `meu_status.py` |
| `.agent/context/meu-registry.md` | generated | Render the reconciled MEU-55 description from the SSOT; do not hand-edit |

### MEU-51 — `gui-layout-primitives`

#### Component contract

`Disclosure` is a controlled presentational wrapper (`open`, `onOpenChange`, stable `id`/accessible label), renders a canonical `Button` trigger with `aria-expanded` and `aria-controls`, and hides the content from focus when closed. `SegmentedControl` is a controlled single-choice group over native radios with caller-supplied `name`, option IDs/test IDs, labels and values; no component-level persistence or mutation. `StatusChip` has a closed semantic tone set mapped to existing theme tokens, always renders text plus optional count/indicator, and is never color-only. `FormRow` links label/hint/error to its supplied control. `PathRow` composes `FormRow`, an input, and an optional canonical Browse `Button`; the page owns the path schema and browse callback. These components do not import API clients or page modules. Only `E2E_HARNESS` mounts them this session.

#### Boundary Inventory

| Surface | Schema owner | Field constraints / extra-field policy | Error mapping / parity |
|---|---|---|---|
| `SegmentedControl` user choice | Caller-supplied finite `options` plus component runtime membership guard | Only an option's value may be emitted; unknown value cannot call `onValueChange`; no free-form extra fields | No REST boundary; consumers keep current create/update validation |
| `PathRow` text and Browse event | Existing consuming page's schema/validator, not the primitive | Primitive forwards value/change without transforming; Browse invokes supplied callback exactly once | No REST boundary in Session 23; later page MEUs must preserve current 422 behavior |
| `Disclosure` click | Controlled `open` prop / `onOpenChange` | Boolean next state only; closed content not keyboard reachable | No payload; consumer owns any persisted setting |
| `AVKIT_PRIMITIVE_HARNESS_BUILD` build environment | `electron.vite.config.ts` exact-value guard | Unset means product-only input; `1` adds test-only HTML; other nonempty values fail. No extra environment settings consumed by this guard | Invalid value fails build before output; no REST mapping or create/update path |
| `AVKIT_E2E_OUT_DIR` test environment | `ui/tests/e2e/global-setup.ts` allowlist | Unset/`out` selects production E2E build; `out-e2e` selects isolated harness build; all other values fail before launch | Invalid value fails setup, and missing selected main bundle fails; no REST mapping or create/update path |

#### Acceptance Criteria

| AC | Type | Description and observable/call chain | Source | Negative Test |
|---|---|---|---|---|
| AC-51.1 | unit | `Disclosure` trigger is a canonical `Button`, has `aria-expanded`/`aria-controls`, toggles via click/Enter/Space, and closed children cannot receive focus. Chain: native button → `onOpenChange` → controlled rerender → attributes/visibility. | Research-backed W3C APG Disclosure; `GUI_RULES` | A visual-only open class with stale `aria-expanded`, or hidden-but-focusable child, fails. |
| AC-51.2 | unit | `SegmentedControl` preserves caller option IDs on native radios, their common `name`, one checked value, arrow-key radio behavior, and emits only a supplied option value. Chain: radio change → membership guard → callback. | Research-backed W3C APG Radio Group; mockups Downloader/Settings §04 | Unknown value or two checked options, or button group with lost IDs, fails. |
| AC-51.3 | unit | `StatusChip` renders readable label/count under every tone in a finite token map; theme token classes only, no status-color inference from uncontrolled string, no color-only meaning. | Local Canon `10-queue-card-ui.md` §Status token table; `GUI_RULES` | New raw hex or empty accessible label fails. |
| AC-51.4 | unit | `FormRow` links label to control and hint/error via `aria-describedby`; `PathRow` keeps the caller's path string exact and Browse invokes the supplied callback once by click/keyboard. Chain: input and canonical Button → callbacks. | Local Canon `06-gui.md` §Settings; W3C APG Button: https://www.w3.org/WAI/ARIA/apg/patterns/button/ | Unlabelled input, altered path, double browse, or dead Browse fails. |
| AC-51.5 | unit | `PRIMITIVES` are importable in isolation, have no page/API imports, no `TODO`/`FIXME`/placeholder, use G32/G33/G34 tokens, and do not add a dependency or new Button variant/size. | Local Canon grouping:144–162; `GUI_RULES` | A page import, `transition-all`, hardcoded hex, or sixth Button variant fails. |
| AC-51.6 | unit | New primitive locator constants are registered once in `ui/tests/e2e/test-ids.ts`; components accept caller IDs for future page-specific instances. Existing `PRESERVED_TESTIDS` retain their exact string values. | Local Canon grouping:79–80; `06-gui.md` §data-testid | An existing ID renamed or hardcoded duplicate on two instances fails. |
| AC-51.7 | integration + E2E | Write `layout-primitives.test.ts` E2E before the primitive implementation. `E2E_HARNESS` imports the five real components and mounts local controlled state in a separate real Electron BrowserWindow. Playwright asserts disclosure click/Enter/Space and closed-focus behavior; radio choice and keyboard/checked/visual state; chip readable tone/count; form label/hint/error association; exact path edit and Browse callback. The harness build must contain its HTML, the ordinary product build/package must exclude it, selected-build global setup must fail closed, existing Electron waves must remain green, and no product page may import a new primitive. Consumer MEUs 52–58 still own their first product-page E2E assertions. | Human-approved 2026-09-26 Option 1; `create-plan.md` §4A; emerging standard E2; `E2E_HARNESS` | Missing/unreachable harness, mocked or placeholder control, dead callback, false green from stale `out`, harness in product output, page mount, or existing-wave regression fails. |

The AC-51.7 unit assertion is written before the harness implementation and fails in Red on absent/wrong entry wiring, missing E2E assertions, missing isolation guard, or a page import; the real Electron test is also written before implementation but runs only after the isolated build exists. The E2E test checks `out-e2e` freshness itself before launching, so the full existing-wave run remains valid when global setup selects ordinary `out`. The selected-build global setup checks source and `electron.vite.config.ts` freshness, plus harness HTML existence when `out-e2e` is selected. No skipped or todo assertion satisfies AC-51.7.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Five components, unwired | `Spec` | Grouping:68,79–80,144–162 |
| Controlled disclosure, native radio, accessible button | `Research-backed` | W3C APG URLs above; local `Button.tsx` / `SelectionCheckbox.tsx` patterns |
| Chip colors and tokens | `Local Canon` | `10-queue-card-ui.md` §Status token table, `styles.css`, G32/G33 |
| E2E timing | `Human-approved` | User chose Option 1 on 2026-09-26: Session 23 test-only Electron wave satisfies §4A/E2; grouping's no-new-wave clause is reconciled during execution, while first product-page assertions remain with consumers |
| External-input boundary | `Spec` + `Human-approved` | No new REST/MCP/file input; the two new build/test environment inputs are allowlisted as above; UI callers retain existing schemas and 422 mappings |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/components/ui/Disclosure.tsx` | new | Controlled disclosure |
| `ui/src/renderer/src/components/ui/SegmentedControl.tsx` | new | Native radio group visual segment |
| `ui/src/renderer/src/components/ui/StatusChip.tsx` | new | Compact text status/count chip |
| `ui/src/renderer/src/components/ui/FormRow.tsx` | new | Label/control/hint/error layout |
| `ui/src/renderer/src/components/ui/PathRow.tsx` | new | FormRow with path/Browse composition |
| `ui/tests/unit/layout-primitives.test.ts` | new | Red-first behavior and negative oracles |
| `ui/tests/e2e/test-ids.ts` | modify | Register primitive IDs, preserve existing values |
| `ui/tests/e2e/layout-primitives.test.ts` | new | Red-first real Electron primitive assertions using a separate harness window |
| `ui/src/renderer/primitive-harness.html` | new | Test-only renderer entry, never included in product build |
| `ui/src/renderer/src/primitive-harness.tsx` | new | Mount the real primitives with local controlled state and visible callback evidence |
| `ui/electron.vite.config.ts` | modify | Conditionally include harness entry only for the allowlisted test build flag |
| `ui/tests/e2e/global-setup.ts` | modify | Select exact `out` or `out-e2e` build and check its freshness; reject other values |
| `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md` | modify | Reconcile Session 23 no-new-E2E wording with the human-approved test-only wave while preserving product-page deferral |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Queue header mount on Downloader and Convert | deferred | MEU-52 | Grouping:68–83, 164–178 explicitly schedules first consumer after MEU-51. |
| Downloader/Convert add-panel composition | deferred | MEU-53, MEU-54 | Grouping:81–83 and sessions 24. |
| Transcript/TTS page composition and inherited MEU-48 ACs | deferred | MEU-55, MEU-56 | Grouping:38–59,84–85,180–190. |
| Capture/Settings page composition, including MEU-61 login-item control retention | deferred | MEU-57, MEU-58 | Grouping:86–87,192–200,221. |
| API, backend, or new mutation/enablement logic | out-of-scope | — | `docs/BUILD_PLAN.md:98` and grouping:9–13,222–223 explicitly lock Phase 11 to composition. |
| Product-page E2E assertions for first primitive consumers | deferred | MEU-52–58 | Session 23 covers real primitive behavior in `E2E_HARNESS`; consumer MEUs prove each product-page composition when mounted there. |

## BUILD_PLAN.md Audit

The hub already has Phase 11 links in its opening index and Phase Specs table (`docs/BUILD_PLAN.md:34,119`), but the targets do not yet exist and hand-maintained status prose still says “registered, not yet specced” (`:36`). MEU-50 creates the target and changes that sentence to “Phase 11 page layout spec exists; page composition remains scheduled for MEU-52–58.” Status cells and MEU summary are SSOT-generated; execution uses `tools/meu_status.py` update/render/check and never hand-edits generated spans. The audit must reject the old prose, require the exact new sentence, and require the linked target to exist.

```powershell
rtk proxy pwsh -NoProfile -Command { $hub=[IO.File]::ReadAllText('docs/BUILD_PLAN.md'); if($hub.Contains('registered, not yet specced') -or -not $hub.Contains('Phase 11 page layout spec exists; page composition remains scheduled for MEU-52–58.') -or -not $hub.Contains('[11-page-layout.md](build-plan/11-page-layout.md)') -or -not (Test-Path 'docs/build-plan/11-page-layout.md')){Write-Error 'Phase 11 hub postcondition failed'; exit 1}; 'PASS Phase 11 hub' } *> C:/Temp/av-kit/p11-hub-audit.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11-hub-audit.txt; exit $code
```

## Verification Plan

No project tests, scripts, generators, or `--check` gates run before independent plan approval (`create-plan.md` §5b). During execution, capture each command's all-stream receipt and exit code. The Red receipts must show the named failing ACs before production/spec changes; an infrastructure error does not count as Red. After each code change, run the targeted test again.

| Check | Exact command (PowerShell from repo root) | Expected |
|---|---|---|
| MEU-50 Red | Exact `RED_ORACLE` command in `task.md` row 2 writes `p11-canon-red.json` and `p11-canon-red.txt`. | Nonzero Vitest exit plus collected AC-50.1–50.6 assertion failures; no file-level error or pending/todo test. |
| MEU-50 Green | `rtk proxy npm --prefix ui run test -- tests/unit/layout-canon.test.ts *> C:/Temp/av-kit/p11-canon-vitest.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11-canon-vitest.txt -Tail 40; exit $code` | 0 exit after canon. |
| MEU-51 Red | Exact `RED_ORACLE` command in `task.md` row 7 writes `p11-primitives-red.json` and `p11-primitives-red.txt`. | Nonzero Vitest exit plus collected AC-51.1–51.7 assertion failures; no file-level error or pending/todo test. |
| MEU-51 Green | `rtk proxy npm --prefix ui run test -- tests/unit/layout-primitives.test.ts *> C:/Temp/av-kit/p11-primitives-vitest.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11-primitives-vitest.txt -Tail 40; exit $code` | 0 exit after components. |
| Isolated harness build | `rtk proxy pwsh -NoProfile -Command { $env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; rtk proxy npm --prefix ui run build -- --outDir P:/av-kit/ui/out-e2e *> C:/Temp/av-kit/p11-harness-build.txt; exit $LASTEXITCODE } *> C:/Temp/av-kit/p11-harness-build-wrapper.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11-harness-build.txt -Tail 40; exit $code` | 0 exit; `ui/out-e2e/main/index.js` and `ui/out-e2e/renderer/primitive-harness.html` exist. |
| Primitive Electron E2E | `rtk proxy pwsh -NoProfile -Command { $env:ELECTRON_RUN_AS_NODE=$null; $env:AVKIT_E2E_OUT_DIR='out-e2e'; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/layout-primitives.test.ts *> C:/Temp/av-kit/p11-primitives-e2e.txt; exit $LASTEXITCODE } *> C:/Temp/av-kit/p11-primitives-e2e-wrapper.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11-primitives-e2e.txt -Tail 40; exit $code` | 0 exit; real Electron harness assertions for each interactive primitive and visual state pass, with no skipped/todo cases. |
| UI type | `rtk proxy npm --prefix ui run typecheck *> C:/Temp/av-kit/p11-typecheck.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11-typecheck.txt -Tail 40; exit $code` | 0 exit. |
| UI lint | `rtk proxy npm --prefix ui run lint *> C:/Temp/av-kit/p11-lint.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11-lint.txt -Tail 40; exit $code` | 0 exit. |
| UI full unit | `rtk proxy npm --prefix ui run test *> C:/Temp/av-kit/p11-vitest.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11-vitest.txt -Tail 40; exit $code` | 0 exit and baseline plus new cases. |
| UI product build | `rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/p11-build.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11-build.txt -Tail 40; exit $code` | 0 exit; `ui/out/renderer/primitive-harness.html` absent, product entry present, and `ui/electron-builder.yml` still includes only `out/**/*`. |
| Existing Electron waves | `rtk proxy pwsh -NoProfile -Command { $env:ELECTRON_RUN_AS_NODE=$null; $env:AVKIT_E2E_OUT_DIR=$null; rtk proxy npm --prefix ui run test:e2e *> C:/Temp/av-kit/p11-e2e-inner.txt; exit $LASTEXITCODE } *> C:/Temp/av-kit/p11-e2e.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11-e2e-inner.txt -Tail 40; exit $code` | Existing wave titles/cases pass against fresh ordinary `out`; on a real external launch failure, `[B]` requires exact receipt and CI follow-up. |
| SSOT transition | Exact H1-3 command in `task.md` updates both MEUs with `--plan`, renders/checks, and asserts both YAML blocks plus the generated MEU-55 TR1 description. | 0 exit and explicit `ready_for_review`/plan/three-action postconditions. |
| Closeout | Exact H2-4 command in `task.md`, then its Final completion gate after H2-5. | Handoff/AC, approved review, reflection, metrics/digest, and 23-row postconditions pass. |

OpenAPI `--check` is conditional only if `packages/api/` changes; this plan touches no API file, so H1 records a scoped skip. A page mount or API diff is scope drift and requires re-planning.

## GUI Element Compliance Check

The five intended components include interactive controls, so `create-plan.md` §4A is triggered. The named GUI reference, three element indexes, and enforcement checklist are absent (receipt `C:/Temp/av-kit/p11-all-docs.txt`); the live authorities are `Button.tsx`, `SelectInput.tsx`, `styles.css`, `06-gui.md` §data-testid, `10-queue-card-ui.md` §Status token table, and G30–G37/E2 in `.agent/docs/emerging-standards.md`. Disclosure/Browse use canonical `Button` variants/sizes; segment uses native radios; path fields retain labels; chips have readable text. Unit tests and a written, wired, real-Electron test-only primitive wave cover Session 23 interaction. The first product-page E2E oracles remain mandatory in MEU-52–58. The independent reviewer must check `E2E_HARNESS` against §4A and the user's Option 1 decision; absent files are not claimed as checked.

## Stop Conditions

Stop execution if MEU-49 loses its `approved` prerequisite, an external-input boundary or API change becomes necessary, a §06 choice cannot be reconciled with `COMPOSITION_LOCK`, Red cannot be demonstrated, any P1 UI gate remains failing, or the independent reviewer reports `changes_required`. A human decision is required only for a genuine product fork still unresolved after the local canon and review. Commit/push/merge/release/deploy remain human-gated.

## Open Questions

TR1 is resolved by source to three existing action slots. The grouping describes MEU-55 as a four-slot toolbar, while Transcript mockup §06 expressly permits three slots if its new Clear finished action is out of scope. `COMPOSITION_LOCK` makes that new mutation out of scope. An explicit user choice of four would require a sourced nonmutating fourth action or a change to the Phase 11 behavior lock.

| Question | Option | Source | Benefit | Cost | Recommendation |
|---|---|---|---|---|---|
| Transcript toolbar | Three existing action slots | `docs/BUILD_PLAN.md:98`; Transcript mockup §06 | Preserves current mutation set and has no empty menu. | Differs from grouping's MEU-55 shorthand. | ✅ Draft TR1 |
| Transcript toolbar | Four slots with Clear finished | Grouping:84; Transcript mockup §06 | Matches the drawn header and grouping wording. | Introduces a new destructive queue mutation, conflicting with `COMPOSITION_LOCK`. | ⚠️ Requires explicit scope change |
| Session 23 E2E | Add an Electron-only primitive harness and E2E now | Human-approved 2026-09-26 Option 1; `create-plan.md` §4A; emerging standard E2 | Meets the written-and-wired timing requirement while preserving the product-page lock. | Adds an isolated test build and harness maintenance surface. | ✅ Chosen; encoded in AC-51.7 |

The human-approved test-only harness resolves the §4A/E2 versus grouping conflict; the grouping's Session 23 prose is scheduled for reconciliation. Review should also scrutinize CV1, TT4/CP1 (conditional rendering versus retained test IDs), and harness isolation/reachability. A materially different required behavior becomes a human-decision gate before execution.

## Research References

- W3C APG Disclosure: https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/
- W3C APG Radio Group: https://www.w3.org/WAI/ARIA/apg/patterns/radio/
- W3C APG Button: https://www.w3.org/WAI/ARIA/apg/patterns/button/
- Local design inputs: six `docs/proposals/2026-09-03-*-page-layout-mockup.html` files, §04–§06.
- Carry-forward: `docs/execution/reflections/2026-09-03-p10-queue-card-dnd-reflection.md` §Next Day Outline.
