# Human gate decision: gate location (plan time)

This file records plan-time decisions, as `.agent/docs/cloud-local-collaboration.md` §1 requires. It does **not** authorize execution. Claude Code resolves to `plan_to_exec_gate: human`, so execution starts only on a later direct user message. That message is recorded under §Execution authorization below when it arrives.

## A-1: where execution and the authoritative gate run

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-02. The planner asked, "Where should Session 30 execution and the authoritative gate run?" The user chose:

> Split like Sessions 25–29 (Recommended)

The option text shown to the user:

> I write code and tests here (Python service/API, MCP, UI) and run a container pre-gate that tolerates only the declared env-bound failures. You run one authoritative WINDOWS_GATE (validate-task.ps1) and push the result JSON, then do a short manual flatten → revert look and the /mcp-audit run for the two new actions.

What this decides, once execution is authorized:

- **Container (cloud):** TDD rows and the H1 rows before the gate. The container pre-gate (`validate-task.sh pregate`) is non-authoritative. It tolerates only the `ENV_BOUND_*` census in `implementation-plan.md` §Environment-bound census, each with a proven signature.
- **Local (Mat, Windows, `P:/av-kit`):** one request, three parts, on the same commit ([local-requests.md](local-requests.md) §GATE):
  1. `WINDOWS_GATE` (`validate-task.ps1 -Check windows-gate`), zero tolerance; the result JSON is committed and pushed.
  2. `FLATTEN_LOOK`: a short manual flatten → revert look at the default window, one line per item.
  3. The authoritative `/mcp-audit` run, which must cover `avkit_capture.flatten` and `avkit_capture.revert` against the updated baseline.
- The gate row is the planned turn boundary.

This decision does not authorize merge, release or deploy. At plan time it approved no change to existing test expectations; `TEST_AMENDMENTS` TA-1 to TA-5 were approved later by the execution message (§Execution authorization: "Count and changes approved"). TA-6 and TA-7 are two more pins of the same count/name-list kind that the Round 1 review found (F1). They are read as covered by that approval, because they change only counts and name lists the approved routes and error class necessarily grow, and they are listed for the user in the next report. Any other contradiction still stops execution (Stop condition S2). Changes to shared machine state (`P:/.agent`, sibling repos, `model-registry.local.json`) stay one-way-door decisions (cloud-local §3.5).

## Execution authorization

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-03, sent while the Round 1 plan review was still running. The user wrote:

> D-10: create converter that will change JPEG and WEBP to PNG. And also when saving have two other formats as options for save output. Agree with processing PNG only. But user experience has to be able accept all formats and auto covert them to PNG while leaving the original file be.
>
> Count and changes approved.
>
> User initiated delete is OK with GUI button. AI agents should never be allowed to delete unless user explicitly instructs via MCP.
>
> go ahead and proceed to execution

What this authorizes and decides:

- **Execution** of `task.md` under A-1's split, once the plan carries the decisions below (GUARDRAILS SIGN 3: direct human execution authorization satisfies the plan-to-execution gate). The in-flight Round 1 review is still collected and its findings applied before code changes.
- **D-10 (human):** PNG-only processing is kept, and the plan adds a JPEG/WebP → PNG converter that leaves the original untouched, plus JPEG and WebP as save-output options. The design details are settled in A-2.
- **`TEST_AMENDMENTS` TA-1 to TA-5:** approved ("Count and changes approved").
- **Autonomous decisions D-8, D-9, D-11 to D-21:** accepted. None were vetoed. D-19 (instruction text) is widened by A-2's MCP rule.
- **MCP destructive policy (new, human):** GUI-initiated deletes stay as they are. AI agents must never delete unless the user explicitly instructs it through MCP. Applied in A-2.
- **Commit and push** to the designated branch `claude/determined-ptolemy-ykl2u7`. Merge, release and deploy are **not** authorized.

## A-2: D-10 converter, save-output formats, MCP user confirmation

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-03 (AskUserQuestion), right after the execution message. Two parts of that message have more than one reasonable reading, so the planner asked three questions. The answers:

1. *"D-10 converter: when should a JPEG/WebP shot be converted to PNG (the original file is always left untouched)?"* The user chose:

   > On Apply to image (Recommended)

   The option text: "Apply on a JPEG/WebP writes a PNG copy next to it ({stem}.png, or {stem}_2.png if taken), carries the saved marks over, and flattens that PNG with the usual backup. The PNG appears as its own shot; the JPEG/WebP stays as it was. Nothing changes for files you never apply."

2. *"'When saving have two other formats as options for save output': which output gets the PNG / JPEG / WebP choice?"* The user chose:

   > Save overlay copy (Recommended)

   The option text: "The baked copy written by Save overlay ({stem}.annotated.*) can be PNG (default), JPEG or WebP, chosen by a Capture setting. Apply to image keeps writing PNG, since processing is PNG only. JPEG/WebP use quality 90."

3. *"MCP rule 'AI agents should never be allowed to delete unless user explicitly instructs': how should that be enforced for the capture actions that delete or overwrite files (remove, flatten, revert)?"* The user chose:

   > Ask the user via MCP (Recommended)

   The option text: "The server pops a confirmation to you through the IDE's MCP elicitation prompt ('Delete shot X and its files?') and proceeds only if you accept. The agent's confirm:true is still required. Clients without elicitation support are refused, so an agent can never do it alone."

**How the plan carries them:** `CONVERT_ON_APPLY` and `CONVERT_NAME` (D-10, D-22), `ANNOTATED_FORMATS` (D-23) and `USER_CONFIRM` (D-24) in `implementation-plan.md`, with ACs AC-67.27 to AC-67.33. One refinement of answer 1 is logged as D-22: the converted file is named `{stem}-converted.png` rather than `{stem}.png`. A same-stem PNG would share the JPEG's sidecar and `.annotated.*` file names (`capture.py:382-387`), so flattening it would delete the JPEG's saved marks, and the JPEG must stay untouched. The user can veto D-22 at any point; it changes one naming rule.

**Scope effect:** `packages/infrastructure` (the bake gains an output format) and `avkit_capture.remove` (it now also asks the user) enter `PRODUCT_SCOPE`. The arrow rendering (`CAPTURE-BAKE-ARROW-THIN`) stays out.

## A-3: `TEST_AMENDMENTS` TA-8 (found by the row-1 census)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-03 (AskUserQuestion), during row 1. The census (`validate-task.sh census`, 435 hits) found three existing pins outside TA-1..TA-7 that the approved routes and `backup_path` change. That is Stop condition S2, so the planner asked:

> The row-1 census found three more existing test pins that the two new routes and the new detail field necessarily change; none is in the approved list: (1) tests/e2e/test_api_openapi.py — the exact route list ROUTE_INDEX and len == 71 → add the two flatten/revert routes, 73; (2) tests/e2e/test_api_downloads.py:374 ACTION_INDEX_AFTER 68 → 70 (same MCP action count as TA-1); (3) tests/e2e/test_api_captures.py:76 SHOT_DETAIL_OUT_FIELDS (exact key order of GET /captures/{id}) → append backup_path. Each only adds; every old value stays. Approve them as TA-8?

The user chose:

> Approve TA-8 (Recommended)

The option text: "Same kind as the counts you already approved: superset-only changes forced by the approved routes and backup_path. I add them as TA-8, log it as A-3, and the execution reviewer checks them."

TA-8 is defined in `implementation-plan.md` §`TEST_AMENDMENTS`. A setup-only fixture repair (g) comes with it: the route fake `FakeCapture` in `tests/e2e/test_api_captures.py` gains `latest_backup()` returning `None`, so the existing detail tests reach their assertions.

## A-4: `TEST_AMENDMENTS` TA-9 (found during row 3 Green)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-03 (AskUserQuestion), during row 3. `green-py` failed a pin the census patterns did not reach (they matched `bake(` calls, not the `ImageAnnotatePort.bake` attribute). That is Stop condition S2, so the planner asked:

> Green found one more existing pin the census missed: tests/unit/test_domain_capture.py:321 (AC-34.10) asserts ImageAnnotatePort.bake's parameters are exactly [self, original_path, annotations, output_path]. The approved design adds a 4th parameter output_format (default "png") so Save overlay can write JPEG/WebP. Approve amending that one line as TA-9 (the list gains output_format; every other assertion unchanged)?

The user chose:

> Approve TA-9 (Recommended)

The option text: "Keep the reviewed BAKE_PORT design; the pinned parameter list gains the defaulted output_format. Old calls keep working; the execution reviewer checks it."

The rejected alternative was a separate port method, leaving `bake` unchanged. TA-9 is defined in `implementation-plan.md` §`TEST_AMENDMENTS`. The census row in `walkthrough.md` records the gap and its cause.

## A-5: backup folder creation through the port (found at H1-2 pre-gate)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-03 (AskUserQuestion), during H1-2.

- **Finding:** the container pre-gate's full pytest run failed `tests/unit/test_services.py::test_ac_12_8_no_direct_mkdir_in_services`, an existing layering guard (MEU-12). It forbids `.mkdir` calls in `packages/core/src/avkit_core/services/` other than `health.py`.
- **The conflict:** `FLATTEN_SEQUENCE` step 3 has the service "resolve the backup dir, create it", and row 3 used `backup_dir.mkdir(...)`.
- **Why it was missed:** the targeted Green sets (`PYT`, `REGPY`) do not include `test_services.py`, and the census patterns did not reach the guard.
- **Classification:** a new contradiction (Stop condition S2), so the planner asked:

> Flatten must create the backup folder, but the AC-12.8 guard forbids directory creation inside services. How should Session 30 resolve this?

The user chose:

> Port method (Recommended)

The option text: "Add `ensure_dir(path)` to ImageAnnotatePort (ports/capture.py and the adapter, both already in the plan's file list). The service calls the port instead of mkdir. The unit-test fake port gains the method as a fixture repair. AC-12.8 stays unchanged, and no test expectation changes."

The rejected alternative was TA-10, exempting the service's mkdir from AC-12.8. The fake's new method is recorded as `FIXTURE_REPAIRS` (h) in `implementation-plan.md`.

## A-6: disabled-button reason for Apply to image and Revert (FLATTEN_LOOK attempt 1, F1)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-03 (AskUserQuestion), after `LOCAL_SEQUENCE` attempt 1.

- **Finding (F1 fail):** after one unsaved edit, Apply to image is disabled, but its reason ("Save the overlay first") never shows.
- **Cause:** the shared `Button` primitive (`ui/src/renderer/src/components/ui/Button.tsx:34`) adds `disabled:pointer-events-none`, so a disabled button cannot be hovered and its native `title` never appears. Revert's reason is hidden the same way. jsdom tests asserting the `title` attribute pass regardless.

The user chose:

> Wrapper span (Recommended)

The option text: "In CapturePage.tsx only, wrap Apply and Revert in a <span> carrying the same title, so hovering a disabled button shows the reason. The button keeps its own title, so the existing tests still hold. Add jsdom and Electron checks that the wrapper carries the reason. The toolbar icons' 'Select a shot first' is a pre-existing MEU-65 case, folded into CAPTURE-ACTION-ROW-ICONS."

Rejected alternatives:
- Change the `Button` primitive. That widens scope beyond the Files Modified table.
- Accept F1 as a known deviation and file an issue.

The fix re-runs `WINDOWS_GATE` and F1 in `LOCAL_SEQUENCE` attempt 2.

## A-7: MCP setup prompt out of Session 30; F8 re-run by hand (FLATTEN_LOOK attempt 1, F8)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-03 (AskUserQuestion), after `LOCAL_SEQUENCE` attempt 1.

**Finding (F8 not exercised):** the server was registered at local scope under `P:/av-kit`, but the VS Code extension session's project key was `p:/av-kit`, so av-kit never loaded. The user's answer to the first F8 question:

> There is issue, where in settings the IDE setup prompt cannot be viewed. I used it to copy and past and the agent still did bunch of investigating on what to do for the MCP to be setup in Claude Code. The MCP setup prompt is the issue here. It needs to follow best practice for Claude Code but also be something other agents can apply universally to various other IDE and TUI platforms.

The planner then asked whether that feature belongs in Session 30, since it touches `ui/src/main`, which this plan freezes, and specs 06/07. The user chose:

> Separate MEU, F8 by hand (Recommended)

The option text: "File MCP-SETUP-PROMPT (medium) with these research findings for its own plan session. For F8 in attempt 2, I give you an exact, researched setup recipe: a gitignored project .mcp.json, read by both the CLI and the VS Code extension, with no path-case issue. Session 30 closes on its approved scope."

`MCP-SETUP-PROMPT` is filed in `known-issues.yaml`. The F8 recipe is in `local-requests.md` §GATE attempt 2.

## A-8, A-9, A-10: after LOCAL_SEQUENCE attempt 2

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-04 (AskUserQuestion), after Mat's attempt 2 reply.

That reply reported three findings:
- `WINDOWS_GATE` stopped at preflight: `P:/.agent/model-registry.json` changed outside av-kit since attempt 1.
- F1 failed: no native hover tooltip appears on any Capture button (`CAPTURE-TOOLTIPS-NOT-SHOWN`).
- F8e was blocked: Claude Code refused `avkit_capture {action: revert, id, confirm: true}` with "Input validation error … Invalid input" before any prompt, because `tools/list` advertises an empty `inputSchema` (`MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA`).

### A-8: gate drift

> Accept new hash (Recommended)

The option text: "Record A-8 accepting the new registry hash (say in 'Other' what changed if you know). validate-task.ps1 gains an explicit -AcceptDrift A-8 switch that records the old and new hashes in the result JSON, and windows-gate-check accepts drift only when it names an A-decision. The full gate then runs on the new registry, so nothing from attempt 1's gate is reused."

### A-9: MCP advertised schema

> Fix in Session 30 (Recommended)

The option text: "Plan amendment: registry.ts (already in the Files table) advertises one object schema per tool in tools/list: action as an enum plus every action's fields typed and optional, with passthrough so handleTool's strict per-action union still rejects bad combinations and extra keys. New AC-67.34 is tested through a real SDK client. The audit is re-run (the 8 schema_not_advertised findings should flip to FIXED), then WINDOWS_GATE and F8. This touches every avkit tool's advertised schema."

**Implementation note:** `tests/m7-resource.test.ts` reads the per-action descriptions from the registered union's `options`. Registering a flat object instead would change that existing expectation, which no TA approves.
- So the registered schema stays the strict union. Server-side validation is therefore unchanged and stricter than passthrough.
- Only the `tools/list` response is rewritten to advertise the typed flat object (`ADVERTISED_SCHEMA`).
- This keeps every existing test expectation and still meets the option's intent: a typed schema for clients, with strict per-action validation at the server.

### A-10: F1 tooltip

> Rendered tooltip (Recommended)

The option text: "In CapturePage.tsx only: the A-6 wrapper also renders a small visible role=tooltip label on hover or focus when Apply/Revert is disabled, so it doesn't depend on native tooltips. It is Electron-tested for visibility. The app-wide native tooltip problem stays CAPTURE-TOOLTIPS-NOT-SHOWN for its own session."

## A-11: confirmation dialog fallback, after FLATTEN_LOOK attempt 3 F8

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code VS Code session), 2026-10-04.

F8 failed on the client side. Claude Code VS Code 2.1.289 declares the elicitation capability, but it declined the revert prompt itself, 23 ms after the call, without showing anything (`MCP-ELICITATION-VSCODE-AUTO-DECLINE`; anthropics/claude-code #98978). Mat asked for research under KISS, noting it is a local app, so security is not a major concern. The recommendation was:
- Keep elicitation first.
- When the client cannot ask, or declines faster than a person could (250 ms, the may-I PR #1 precedent), the MCP server shows a native topmost Windows Yes/No dialog itself.
- There are no backend or GUI changes.
- Recycle-Bin removal is not bundled.

Mat's answer:

> can you just make the ammendemnts and change code now?

This amends D-24's "an IDE without elicitation refuses the three actions". Every other D-24 rule is unchanged: only an explicit accept runs, and every other outcome is refused with zero API calls. Contracts `DIALOG_FALLBACK` and `USER_CONFIRM_AUTODECLINE_MS`, AC-67.36, task row 4.

**Implementation notes:**
- **Existing tests.** `user-confirm.test.ts`'s `connect()` now passes a stub dialog that reports itself unavailable, so the existing AC-67.31 refusal cases keep their expectations and no test opens a real dialog. No existing assertion changed.
- **Audit client.** It answers after `AUDIT_ANSWER_DELAY_MS` (500 ms). Its planned declines therefore stay the operator's answer, and a live audit never opens the dialog. The launch env (`MCP_LAUNCH`) is unchanged.
- **Instructions text.** `SERVER_INSTRUCTIONS` still says "ask the user in the IDE" (pinned by `capture.test.ts:469`). The IDE is still asked first, so the text is not changed.

## A-12: revalidate av-kit's registry overlay (repeats A17)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code VS Code session), 2026-10-07.

`WINDOWS_GATE` attempt 3 failed in pytest at `test_review_pipeline_wrapper_refuses_before_provider[same-vendor|unknown-class]` with `overlay_not_validated`:
- The shared `P:/.agent/model-registry.json` now hashes to `ad9a09de…`.
- The tracked `.agent/model-registry.local.json` still recorded `validated_against: b06d7cda…`.
- A-8 accepts drift in the gate preflight only.

The recommendation was to approve, for Session 30, the rule Session 26 approved as A17 (`docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md:451`):
- Revalidate with the resolver's project-scoped validate/compile: no global sync, and nothing written to `P:/.agent`.
- Only `validated_against` in `.agent/model-registry.local.json` may change.
- Any binding or class change stops the step.
- `TOOLING-SHARED-REGISTRY-COUPLING` is raised to medium because the failure recurred.

Mat's answer:

> go 1–2

(Item 1 committed and pushed A-11 in `2863665`. Item 2 is this decision.)

## A-13: accept the external-input changes since A-8's baseline (execution review round 1, F3)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-10. The user replied "ok lets do this" and relayed the local agent's request, which quotes Mat:

> ok i'm fine with A-13

**What A-13 accepts, through the current state.** Attempt 1's preflight is the A-8 reference.

| External input | Attempt 1 (A-8 reference) | Attempt 4 preflight | Now (before attempt 5) |
|---|---|---|---|
| `P:/agentic-framework` HEAD | `4033418f…` | `47a205c4…` | `80461f6` (via `11210cb` model-orchestration refresh and `80461f6` dispatch resume/fork) |
| `P:/.agent/model-registry.json` sha256 | `B06D7CDA…` | `AD9A09DE…` | `A7C95972C1E83885AA339873BDBF35CD5A6DAF3FB593F0D894F658BBFB80EBFA` |

**What A-13 resolves and authorizes:**
- **Review round 1, F3:** A-8's quoted text accepted only the registry hash, so no decision named the framework HEAD change. A-13 now names both inputs and resolves F3.
- **Overlay revalidation:** the local agent may repeat the A-12 revalidation, because `.agent/model-registry.local.json` still pins `validated_against: ad9a09de…` and pytest would fail with `overlay_not_validated` as in attempt 3.
  - Same rule as A-12 / Session 26 A17: project-scoped `resolve_model.py validate --overlay … --strict --write-compiled`, with no global sync and nothing written to `P:/.agent`.
  - Only `validated_against` may change; any binding or class change stops the step.
  - It is committed before attempt 5.
- **Attempt 5's `WINDOWS_GATE`** runs with `-AcceptDrift A-13`, so its preflight records the drift against attempt 4's committed hashes under this decision.

## A-14: follow the shared registry's model renames in av-kit's overlay (stopped A-13 step)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code VS Code session, local agent), 2026-10-10.

The A-13 revalidation changed only `validated_against` (→ `a7c95972…`), with `P:/.agent` unchanged (56 files, hashes identical before and after). But 3 of the 91 tests in `tests/tooling/test_framework_adoption.py` still failed, in `test_registry_contract_preserves_bindings[avkit_builder|avkit_verifier|avkit_router]`, with `slug_not_on_harness`. The shared registry (`P:/.agent` `91d7ee1`, `af7658d`) retired `claude-sonnet-5` and `claude-haiku-4-5` and published their successors, `claude-sonnet-5-5` and `claude-haiku-5-5`. A-13 forbids a binding change, so the step stopped. The recommendation was to move the three bindings to the successors and keep the same efforts. The Claude Code names stay `sonnet` and `haiku`.

Mat's answer:

> yes

**What changed** (`.agent/model-registry.local.yaml`, recompiled into `.local.json` by the same project-scoped validate):

| Class | Harness | Before | After |
|---|---|---|---|
| `avkit_builder` | `claude-code-agents` | `claude-sonnet-5`, medium | `claude-sonnet-5-5`, medium |
| `avkit_verifier` | `claude-code-agents` | `claude-sonnet-5`, medium | `claude-sonnet-5-5`, medium |
| `avkit_router` | `claude-code-agents` | `claude-haiku-4-5`, low | `claude-haiku-5-5`, low |
| `avkit_independent_reviewer` | `codex-cli` | `gpt-5.6-sol` | `gpt-6.1-sol`, same `effort_map` |

**Disclosure:** the fourth row was not in the question Mat answered. It carries out his Round 2 direction (`human-review-decision.md`, "codex cli gpt-6.1-sol high"), and it matches the shared `independent_reviewer` class. `Invoke-CodexDispatch.ps1` takes the model from this class binding, so without the change Round 2 would run `gpt-5.6-sol`. No class was added, removed or tightened (`tightened_classes=[] allowlist_extra=0`).

**Follow-ons, in the same commit:**
- `test_registry_contract_vendor_independence` expects `gpt-6.1-sol`.
- The 2026-09-26 routing census (`routing-census.md`) gets new line hashes and table text for the eight changed binding lines. Classification and reason are unchanged.
- `test_framework_adoption.py`: 91 passed.
