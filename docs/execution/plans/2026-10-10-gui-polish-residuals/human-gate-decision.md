# Human gate decision: gate location (plan time)

This file records plan-time decisions, as `.agent/docs/cloud-local-collaboration.md` §1 requires. It does **not** authorize execution. Claude Code resolves to `plan_to_exec_gate: human`, so execution starts only on a later direct user message. That message is recorded under §Execution authorization below when it arrives.

## A-1: where execution and the authoritative gate run

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-10. The planner asked, "Where should Session 31 execution and the authoritative gate run?" The user chose:

> Split like Sessions 25–29 (Recommended)

The option text shown to the user:

> I write code and tests here and run a container pre-gate that tolerates only the declared env-bound failures. You then run one WINDOWS_GATE (validate-task.ps1) on your machine, push the result JSON, and do a short manual look: header buttons, plus Settings rail and section emphasis on your large screen.

What this decides, once execution is authorized:

- **Container (cloud):** task rows 0–9 and H1-1 to H1-5. The container pre-gate (`validate-task.sh pregate`) is non-authoritative. It tolerates only the `ENV_BOUND_*` census in `implementation-plan.md` §Environment-bound census, each with a proven signature.
- **Local (Mat, Windows, `P:/av-kit`):**
  - `WINDOWS_GATE` (`validate-task.ps1 -Check windows-gate`) with zero tolerance. The local side commits and pushes the result JSON.
  - Then the `CHROME_LOOK` checklist K1–K5 on the same commit ([local-requests.md](local-requests.md) §GATE), returned one line per item. This is "the short manual look". K4 and K5 run on Mat's large screen, where R4 reproduced.
  - Row H1-6 is the planned turn boundary.
- **No LOCAL_REPRO request before execution** (plan D-10). SETTINGS-ACTIVE-SECTION-HIGHLIGHT was already reproduced on the target (Session 27 `LOCAL_REPRO` R4, `known-issues.yaml` verification block), and A-6 (`407db19`) left the scroll path untouched. HEADER-CONSOLE-SETTINGS-BUTTON-STATE is a source fact: `Header.tsx:50-67` renders two `ghost` buttons with no `aria-pressed`. AC-69.5 and AC-70.2 must go Red in the container; otherwise Stop condition S4 applies to AC-70.2.

This decision does not authorize merge, release or deploy. It approves no test-expectation change by itself: `TEST_AMENDMENTS` TA-1/TA-2 still need the independent plan approval and an execution message that does not veto them (Stop condition S8). Changes to shared machine state (`P:/.agent`, sibling repos, `model-registry.local.json`) stay one-way-door decisions (cloud-local §3.5).

## A-2: the trailing-section rail fix (plan D-9)

Source: `USER_EXPLICIT`, same exchange, 2026-10-10 (AskUserQuestion). The question: "Session 27's local repro R4 found the Settings rail stops at Convert on your large screen: Capture through MCP access never become current while you scroll. A-6 fixed only the click path. How should trailing sections become current when you scroll?" The user chose:

> Bottom spacer (Recommended)

The option text shown to the user:

> Add bottom padding to the Settings column so every section can scroll up into the rail's top band. Each section then highlights in order while you scroll, and a click on MCP puts it at the top. Cost: empty space below MCP access at the end of the page. Also re-checks the rail on scroll, so reaching the bottom marks the last section.

The plan implements this as `TAIL_SPACER` / `TAIL_SPACER_HEIGHT` (D-16) and `SCROLL_RECHECK` (D-17). The alternatives offered and declined were "Bottom fallback only" and "Progress mapping".

## Execution authorization

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-11, after the round 2 plan approval. The user's message, verbatim (the execution-authorization block):

> - I, Mat, authorize execution of docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md as approved by the independent plan review round 2 (Codex gpt-6.1-sol, verdict approved, 0 blocking, intent_achieved yes; report at .agent/context/handoffs/2026-10-10-gui-polish-residuals-plan-critical-review.md, commit 31a7058).
> - I do not veto TA-1 or TA-2 (Stop condition S8). Apply them exactly as approved, and change nothing else in those tests.
> - Scope stays the goal anchor: "Session 31 delivers MEU-69 (header Console toggle state, Commands palette button) and MEU-70 (Settings trailing-section rail fix and current-section emphasis), UI only, with no change outside ui/ and the two hub docs."

The same message also directed:
- Resolve the round 2 finding F5 at row 5, before the new test is written, through the recorded correction route (done: implementation-plan.md §Round 2 Correction Notes).
- `WINDOWS_GATE` runs on Mat's machine. The cloud writes it as a local request and stops at H1-6 until the receipts return.
- The execution review is a new ledger loop (`--review-mode execution`, its own loop id, the goal anchor quoted verbatim in its prompt), dispatched locally with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`, and sized at `begin` so 2–3 rounds fit without a mid-loop `continue` (one high-effort round cost about 8.6M–9.6M tokens).
- Commit and push as work proceeds, one logical change per commit.

What this authorizes:
- **Execution** of `task.md` rows 0–9 and H1-1 to H2-3, under A-1's split (container, then `WINDOWS_GATE` + `CHROME_LOOK` on Mat's machine).
- **`TEST_AMENDMENTS` TA-1 and TA-2**, exactly as defined; S8 does not fire.
- **Autonomous decisions D-10 to D-21**: accepted; none vetoed.
- **Commit and push** to the designated branch `claude/vigilant-volta-f04tvs`.
- Merge, release and deploy are **not** authorized. `.agent/model-registry.local.*` and `P:/.agent` are not touched (the overlay's `validated_against a7c95972` comes from the `3e65499` cherry-pick).

## A-3: rail group headings read as non-interactive (CHROME_LOOK follow-up)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code, VS Code, local dispatcher session), 2026-10-14, while returning `CHROME_LOOK` attempt 1. The user's message, verbatim:

> K1 through K5 looks as expected. If you can do one quick modification for headings: PAGES TTS APP SETUP I'd like to make it clear they are not clicable and change something like background color to make visual divers. Let me check it before we move on.

The change (`SettingsRail.tsx`, the group heading `<p>` only): `cursor-default select-none`, a token tint `bg-bg-subtle/20` with `rounded-[var(--radius-control)]` and `py-1`, `tracking-wider`, and `self-stretch` at the wide breakpoint so the tint spans the rail column. No hover state, no `tabindex`, no role change; the `role="group"` / `aria-labelledby` wiring and every rail entry are unchanged. A new append-only `settings-rail.test.tsx` case (went Red first) pins it: each heading is a `P` outside any button or link, without `tabindex`, carrying `cursor-default`, `select-none` and `bg-bg-subtle/20` and no `hover:` class, and no rail entry carries the tint. No existing test changed (AC-70.7 holds).

The user checked the result in the dev app before approving it, verbatim:

> looks good we can continue now

Scope: UI only, inside `ui/` (the Settings rail, MEU-70's surface); the goal anchor is unchanged. The change touches `GATED_PATHS`, so `WINDOWS_GATE` runs again (attempt 2) on the commit that carries it, and `CHROME_LOOK` is recorded against that commit. The hub docs say nothing about the heading style, so no hub change follows.

## A-4: accept the agentic-framework preflight drift (WINDOWS_GATE attempt 2)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code, VS Code, local dispatcher session), 2026-10-14 (AskUserQuestion). `validate-task.ps1 -Check windows-gate` attempt 2 on `3dc8fd2` stopped before stage 1: `P:/agentic-framework` HEAD moved from `80461f6` (attempt 1) to `e387dec`, while the `P:/.agent/model-registry.json` hash stayed `A7C95972…`. The three framework commits (`7621e45`, `7ddf016`, `e387dec`) add an opt-in agent stop-email notifier with its tests and a known-issues register, and touch the framework's own copies of the dispatch wrappers and `harness-profiles.md`; av-kit runs its own `tools/` copies, which did not change. The question asked how to proceed; the user chose:

> Accept and re-run (Recommended)

The option text shown to the user: "I record your acceptance as decision A-4 and re-run attempt 2 on 3dc8fd2. The drift record already holds the new head, so the preflight passes, and the pytest floor of 629 carries forward. av-kit runs its own tools/ copies, so the framework commits shouldn't affect this gate."

The drift record is preserved at `C:/Temp/av-kit/keep/3dc8fd2-attempt2-preflight/windows-gate-result.json`. The re-run compares against it (new head, `pytest_floor` 629), on the commit that carries this decision; the code under `GATED_PATHS` is that of `3dc8fd2`.

## A-5: port Zorivest's light cyan into av-kit (WINDOWS_GATE attempt 2 failure)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code, VS Code, local dispatcher session), 2026-10-14 (AskUserQuestion). `WINDOWS_GATE` attempt 2 on `f9303a1` (code of `3dc8fd2`) passed every stage up to `ui-tests`, which failed one of 774: AC-41.3 (`queue-canon.test.ts`, MEU-41), `--color-accent-cyan light diverges from PILL_TOKEN_SOURCE: expected '#0891b2' to be '#0e7490'`. Classification: external drift, not the Session 31 diff. `PILL_TOKEN_SOURCE` is `P:/zorivest/ui/src/renderer/src/globals.css`; Zorivest commit `7b73b5b7` (2026-10-14 19:44, MEU-661, "Light accent is #0e7490") changed that token after attempt 1. Every other pill token still matches. Receipts are preserved at `C:/Temp/av-kit/keep/f9303a1-attempt2/`. The question offered porting the cyan token only, porting cyan plus the light `--color-accent`, or stopping; the user chose:

> Port cyan token only (Recommended)

The option text shown to the user: "Record A-5 and change one line in ui/src/renderer/src/styles.css: light --color-accent-cyan becomes #0e7490, the minimum that restores the 'av-kit authors no hue' parity the test enforces. av-kit's light --color-accent is also #0891b2 and stays as is; I'd log a follow-up for whether it should match Zorivest's new accent. Then re-run the gate (attempt 3)."

The change is that one line, inside `ui/` but outside the MEU-69/70 surface; no test changes. It is listed in implementation-plan.md §Execution Correction Notes (Files Modified addition) so `PRODUCT_SCOPE` stays exact. Follow-up for the reflection: whether av-kit's light `--color-accent` (`#0891b2`) should follow Zorivest's new light accent.

## A-6: re-baseline the 16 light-cyan contrast rows (WINDOWS_GATE attempt 3 failure)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code, VS Code, local dispatcher session), 2026-10-14 (AskUserQuestion). `WINDOWS_GATE` attempt 3 on `da1d111` passed every stage up to `ui-tests`, which failed one of 774: AC-43.3 (`queue-primitives.test.ts`, MEU-43), whose measured contrast matrix must equal `docs/execution/plans/2026-08-28-p10-queue-card-foundations/contrast-matrix.json` exactly. Classification: a knock-on of A-5, which the dispatcher should have caught by running the full Vitest suite before committing A-5. Receipts are preserved at `C:/Temp/av-kit/keep/da1d111-attempt3/`. The question offered re-baselining the 16 rows, reverting A-5, or stopping; the user chose:

> Re-baseline 16 rows (Recommended)

The option text shown to the user: "Record A-6 (TEST_AMENDMENTS-class, data only): update just those 16 ratio values in contrast-matrix.json to the values the test computes, changing no assertion or test code. Run the full Vitest suite locally first this time, then run gate attempt 4."

The amendment, light theme, `--color-accent-cyan` (Processing and Downloading, same values for both), by backdrop `card` / `hover` / `checkbox-selected` / `detail-open`:
- `label` (gated, `CONTRAST_MIN` 4.5): 12.1 / 12.99 / 11.46 / 10.91 → 11.85 / 12.74 / 11.28 / 10.65. All stay above `CONTRAST_MIN`; `CONTRAST_WORST_MEASURED` 6.61 is unchanged.
- `icon` (advisory, `STATUS_ICON_RULE`): 3.41 / 3.68 / 3.22 / 3.05 → 4.96 / 5.36 / 4.69 / 4.43. These rows were already at or above 3.0, so "12 of 80 below the 3.0 advisory" is unchanged.

No test code, assertion, named set or other row changed. Before this commit the full Vitest suite passed locally (83 files, 774 tests).
