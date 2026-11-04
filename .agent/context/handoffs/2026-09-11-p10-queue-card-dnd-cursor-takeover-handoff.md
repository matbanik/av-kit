---
date: "2026-09-11"
project: "2026-09-03-p10-queue-card-dnd"
meu: "MEU-49"
status: "in_progress"
action_required: "EXECUTE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md"
build_plan_section: "bp10s10.8"
agent: "cursor-grok (takeover packet author)"
reviewer: "gpt-5.6-sol"
predecessor: "2026-09-03-p10-queue-card-dnd-MEU-49-handoff.md"
---

# Handoff: 2026-09-11-p10-queue-card-dnd-cursor-takeover-handoff

> **Status**: `in_progress`
> **Action Required**: `EXECUTE`

> [!IMPORTANT]
> **This is a harness takeover packet, not the MEU deliverable.** The MEU-49 handoff that
> row H1-6 must finalise and that `HANDOFF_MARKER_CHECK` / `HANDOFF_AC_CHECK` scan is
> [`2026-09-03-p10-queue-card-dnd-MEU-49-handoff.md`](2026-09-03-p10-queue-card-dnd-MEU-49-handoff.md)
> — the 39-AC table lives there and is **not** duplicated here, because a second copy is one
> that can drift. This file exists to move session 22 from the Claude Code driver to the
> Cursor driver without re-deriving state.

---

## Scope

**MEU**: MEU-49 — `gui-queue-dnd`, the Phase 10 exit.
**Handover**: Claude Code (Opus 5 coordinator, sessions of 2026-09-03 → 2026-09-11) → Cursor
IDE driver, coordinator Grok 4.6 Extra High.
**Predecessor**: [`2026-09-03-p10-queue-card-dnd-MEU-49-handoff.md`](2026-09-03-p10-queue-card-dnd-MEU-49-handoff.md)

The originating transcript is `f189a84c-e103-4972-b205-c178a7608de1.jsonl` (18.05 MB,
7,015 records, 2,139 assistant / 1,348 user events, 2026-09-03 → 2026-09-11). **It is not an
input to the takeover and must not be read whole.** Its final record (line 6971,
`isCompactSummary: true`, 17,267 chars) is a complete state dump and has been extracted
verbatim to
[`session-22-compaction-summary.md`](../../../docs/execution/plans/2026-09-03-p10-queue-card-dnd/session-22-compaction-summary.md).
Peak context that session ever held was 183k tokens; its live context after the final
compaction was ~79k. The decision-relevant surface is far smaller than either number.

**Read this packet in this order:**

1. [`task.md`](../../../docs/execution/plans/2026-09-03-p10-queue-card-dnd/task.md) — the row table is the resume point.
2. [`row9-drag-e2e-diagnosis.md`](../../../docs/execution/plans/2026-09-03-p10-queue-card-dnd/row9-drag-e2e-diagnosis.md) — measured root cause of the drag failures, 111 lines.
3. [`session-22-compaction-summary.md`](../../../docs/execution/plans/2026-09-03-p10-queue-card-dnd/session-22-compaction-summary.md) — the predecessor's own final state dump.
4. The MEU-49 handoff above, for the AC table.
5. [`implementation-plan.md`](../../../docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md) + [`named-sets.json`](../../../docs/execution/plans/2026-09-03-p10-queue-card-dnd/named-sets.json) — only for the named sets a given row cites.

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Resume point

Rows 1 through 8 are `[x]`. **Row 9 is the open row** and is partially delivered:

| Row 9 item | State |
|---|---|
| `DND_TESTIDS` registered, six E2E cases landed in both suites | done — AC-49.25–49.29 and 49.36 titles confirmed present in `download-queue.test.ts` and `convert-queue.test.ts` |
| Pointer drag (AC-49.25, 49.26, 49.29) | **fixed and probe-verified** — `DND_AUTOSCROLL_CONFIG` at `QueueList.tsx:327` |
| Keyboard drag (AC-49.27) | **diagnosed, unfixed** — open decision, see below |
| 5px auto-scroll margin caveat in the drag specs | not addressed |
| `command-palette-nav.spec.ts:22`, `download-queue.test.ts:723` (W1-9) | failing, untriaged; both green at the session-21 baseline of 73 |
| Rebuild → full `test:e2e` ≥ 79 runtime / ≥ 73 static → `-Gate E2eCensus` → mark `[x]` | not run since the fix |

Rows 10, 11, 12, H1-1…H1-7 and H2-1…H2-5 are untouched — roughly eighteen rows plus one
Codex review loop capped at six rounds.

### Tree state (verified, not recalled)

| Fact | Evidence |
|---|---|
| `autoScroll={{ threshold: { x: 0, y: 0.05 }, acceleration: 5 }}` present | `ui/src/renderer/src/components/queue/QueueList.tsx:327` |
| Sensors block back to its canonical form, instrumentation reverted | `QueueList.tsx:301` — `useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),` |
| Temporary `ui/tests/e2e/zz-probe.spec.ts` deleted | absent from the tree |
| Typecheck and build green at the pause | `C:/Temp/av-kit/meu49-typecheck-pause.txt`, `meu49-build-pause.txt` (both EXIT=0) |
| Nothing committed — sessions 21 **and** 22 are both uncommitted | `git status --porcelain` |

---

## The one open decision — AC-49.27

`row9-drag-e2e-diagnosis.md` establishes by measurement, not inference, that the pointer and
keyboard failures share one cause: the queue is not its own scroll container, so dnd-kit
measures both its auto-scroll band and its `KeyboardSensor` clamp against the page shell's
`<main>` (rect 40–739, client 699, scrollH 848, maxScroll 148.5), in which every queue row
(548–788) sits below the vertical midpoint of 389.5. The clamp is unconditional in
`KeyboardSensor.handleKeyDown`, identical on `master`, and every member needed to override it
is `private` — **no configuration can reach it**, which is why the `autoScroll` fix closed the
pointer path and left the keyboard path dead.

The three candidates and what each costs are ranked in the diagnosis. Option 1 (give the queue
list its own bounded scroll container) is the only one that leaves `DND_SENSOR_CONFIG` and
`DND_HANDLE_CONTRACT` intact and needs no plan amendment; options 2 and 3 both violate
`DND_SENSOR_CONFIG` and require an amendment plus reviewer sign-off.

**Human direction, 2026-09-11: the takeover session re-derives this and comes back with a
recommendation before implementing.** Do not pick silently — AGENTS.md §Session Discipline
forbids silent scope cuts and silent deferrals in either direction.

Two inputs the re-derivation must weigh that are not in the diagnosis file:

- **Phase 11 collision.** Option 1 is a layout change to `DownloaderPage.tsx` and
  `ConvertPage.tsx`. `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md`
  states "**No Phase 10 reopening**" and schedules MEU-52/53/54 (session 24) to recompose those
  exact two files. Doing it now may be redone in three sessions — or may be exactly right,
  since MEU-55 adopts `QueueList` wholesale and would inherit a working keyboard path for free.
- **The 5px cliff.** dl-3's centre (699) clears the new 5% auto-scroll band (704–739) by five
  pixels. If option 1 lands, the container change likely dissolves this; if it does not, the
  drag specs must reveal the queue before grabbing so AC-49.25 does not sit on a 5px margin.

---

## Cursor harness deltas — what changes versus the Claude Code driver

`.agent/context/harness.local.md` carries per-driver blocks. The Cursor block is **not** the
one the predecessor ran under. Four differences are load-bearing.

### 1. Subagent delegation stays OFF for Cursor — the readonly route does not work on this host

`fresh_worker: none` for the Cursor driver. Both smoke probes were run on 2026-09-11 and are
recorded in [`verification-log.md`](../../skills/subagent-delegation/verification-log.md);
they **split**:

| Route | Result | Consequence |
|---|---|---|
| Builder (writable), `av-kit-builder` at `cursor-grok-4.6-xhigh` | **pass** on real work, coordinator-verified byte-identical | mechanical rows may be delegated once the flag flips |
| Verifier (readonly), `av-kit-verifier` at `composer-2.5-fast` | **fail (infra)** — shell never spawned: *"this machine cannot enforce the 'workspace_readonly' sandbox policy … no working sandbox backend is available (Windows sandbox helper only provides network proxy, not filesystem isolation)"* | readonly worker route is unusable on this host |

The asymmetry is the actionable part: a *writable* Cursor subagent runs shell fine because it
needs no sandbox policy, while a *readonly* one cannot run any command at all on Windows. So
`fresh_worker` does not flip — the condition in `harness.local.md` requires both receipts, and
a half-satisfied condition is not a pass.

**What this costs the takeover.** Row 10 (the MEU-49 gate — seven verbose receipts: typecheck,
lint, vitest, mount gate, build, full Playwright, pytest) is pinned
`delegate_to: av-kit-verifier` precisely because its output would flood a coordinator. On
Cursor it must run under `compact_continue` on the coordinator instead, reading each receipt
tail rather than the whole log. Rows 9 and 12 are `delegate_to: av-kit-builder`, so they are
delegable on the writable route if the flag flips. Two workarounds exist if the verbosity
becomes a problem, neither adopted here: dispatch the validation to a *writable* worker
instructed not to write (weaker guarantee — the readonly property becomes a promise instead of
an enforced policy), or stand up a sandbox backend on the host.

### 2. `builder_model` pins in `task.md` are Claude Code slugs

| `task.md` pin | Rows | Cursor equivalent |
|---|---|---|
| `opus-5` | 1, 3, 5, 6, 7, H1-1, H1-5, H1-6, H2-1, H2-2 | the coordinator itself (Grok 4.6 Extra High) — these are correctness-class rows and stay off the builder tier |
| `sonnet-5` | 2, 2a, 3a, 4, 4a, 4b, 8, 9, 10, 11, 12, H1-2, H1-3, H1-4, H1-6a, H2-3, H2-4, H2-5 | `av-kit-builder` / `av-kit-verifier` at `composer-2.5-fast`, or `cursor-grok-4.6-xhigh` for rows needing more reasoning |

All of these rows are already `[x]` except 9, 10, 11, 12 and the H-rows, so the translation
only has to hold for those.

### 3. Coordinator model pin — resolved 2026-09-11 to `cursor-grok-4.6-xhigh`

Three files had disagreed: `AGENTS.md` and `model-routing.md` pinned Cursor at
`cursor-grok-4.5-high-fast`, while `harness.local.md` and `PROJECT-PROFILE.md` named
`cursor-grok-4.6-high` — a slug that does not resolve in this Cursor `Task` catalog at all.
On human direction the pin is now **`cursor-grok-4.6-xhigh`** everywhere it is live, replacing
both older values rather than accreting beside them (AGENTS.md deletion budget).

Swept: `AGENTS.md`, `PROJECT-PROFILE.md`, `.agent/context/harness.local.md`,
`.cursor/agents/av-kit-builder.md`, `.agent/docs/harness-profiles.md`,
`.agent/docs/model-routing.md`, `.agent/docs/model-delegation.md`,
`.agent/skills/subagent-delegation/SKILL.md`, the three workflows (`cli-dispatch`,
`create-plan`, `delegated-plan-creation`) and all four plan/task templates.

**Deliberately not swept:** the seven completed `docs/execution/plans/2026-08-*/` task tables
and the 2026-08 handoffs. Their `builder_model` cells record which model actually ran those
rows; rewriting them would falsify the execution record rather than update a pin.

One structural defect was corrected in passing: `harness.local.md` carried the Cursor
builder/verifier pins as a bullet under its **Claude Code** per-driver heading. They now sit in
the Cursor Notes section where they apply.

### 4. Gates and dispatch that carry over unchanged

- `plan_to_exec_gate` is `reviewer-auto` on the Cursor block versus `human` on the Claude Code
  block, but this is **moot**: the plan is approved and the user's explicit `proceed` was given
  in session 22. Execution continues; no new gate opens.
- Codex dispatch for H1-7 works from Cursor. `codex` resolves on PATH
  (`C:\Users\Mat\AppData\Roaming\npm\codex.ps1`) and `tools/Invoke-CodexDispatch.ps1` exists.
  Auth was not exercised. Never bare `codex exec`.
- P0 shell rules are driver-independent: `native_shell: powershell`, `*>` redirect to
  `C:/Temp/av-kit/` with forward slashes, no piping a long-running process to a filter,
  `$LASTEXITCODE` captured before any `Get-Content`.
- Known harness trap carried from `current-focus.md`: `rtk proxy` and nested
  `pwsh -Command { … }` serialise child output as CLIXML and corrupt it past ~4 KB. Run
  single-level `pwsh` for receipts larger than that.
- `ELECTRON_RUN_AS_NODE` must be unset before any Playwright run, and `npm --prefix ui run build`
  must precede it — the global setup is fail-closed on `ui/src` being newer than `ui/out`.

---

## Evidence

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| JSONL structural scan (record types, timestamps, usage maxima) | 0 | 7,015 lines; 2,139 assistant / 1,348 user; 2026-09-03 → 2026-09-11; peak context 183,247 tokens; final live context ~79k |
| `isCompactSummary` locate | 0 | line 6971 (1-based), `type=user`, content is a 17,267-char string |
| `Select-String` on `QueueList.tsx` for `autoScroll\|KeyboardSensor\|DndContext` | 0 | `:301` sensors canonical, `:327` `DND_AUTOSCROLL_CONFIG` present |
| `Select-String` for `AC-49.(25\|26\|27\|28\|29\|36)` in both E2E suites | 0 | 7 hits in `download-queue.test.ts`, 3 in `convert-queue.test.ts` |
| Cursor readonly-verifier smoke probe (`npm --prefix ui run test`) | n/a — process never spawned | **fail (infra)**: `workspace_readonly` sandbox policy unenforceable on this Windows host; no receipt produced |
| Cursor builder write-route probe (compaction-summary extraction) | 0 | **pass**: `session-22-compaction-summary.md`, 148 lines, body 17,267 chars |
| Coordinator re-verification of the builder output | 0 | body `-ceq` the JSONL source string (byte-identical), 3/3 markers, exactly 1 added path, 0 tracked files modified, no scratch in tree — `C:/Temp/av-kit/coord-verify-builder-probe.txt` |

### Quality Gate Results

```
Not re-run by this packet. Last known: typecheck EXIT=0, build EXIT=0 (2026-09-11 pause).
Playwright before the autoScroll fix: 73 passed / 6 failed.
Vitest: see the Cursor verifier probe receipt.
```

---

## Changed Files

This packet changes no production code. Files added or updated by the takeover pass:

| File | Action | Summary |
|------|--------|---------|
| `.agent/context/handoffs/2026-09-11-p10-queue-card-dnd-cursor-takeover-handoff.md` | new | this packet |
| `docs/execution/plans/2026-09-03-p10-queue-card-dnd/session-22-compaction-summary.md` | new | verbatim extraction of the predecessor's final compaction summary |
| `.agent/skills/subagent-delegation/verification-log.md` | modified | Cursor readonly + write-route probe receipts |
| 13 governance/template files (see §Cursor harness deltas item 3) | modified | Cursor model pin swept to `cursor-grok-4.6-xhigh`; 55 occurrences |

---

## Deferred Items

| Item | Reason | Deferred-to | Follow-up |
|------|--------|-------------|-----------|
| `fresh_worker: none → Task tool + .cursor/agents/` in `harness.local.md` | **not deferred — not earned.** The readonly smoke failed on infrastructure, so the two-receipt condition is unmet and the flag correctly stays `none`. Reopen only if a sandbox backend is stood up on the host, or if the human decides a writable-worker-instructed-not-to-write is an acceptable substitute for the enforced readonly policy | blocked on host capability, not on a decision | `verification-log.md` §Cursor 2026-09-11 |
| ~~Cursor coordinator pin~~ | **closed 2026-09-11** — human directed the change; swept repo-wide to `cursor-grok-4.6-xhigh` across 13 live governance/template files, historical plan records left intact | — | §Cursor harness deltas item 3 |
| AC-49.27 keyboard fix | human direction 2026-09-11: takeover session re-derives and recommends first | row 9, this project | §The one open decision |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-11 | cursor-grok | Takeover packet authored; Cursor smoke probes dispatched; two governance edits staged for human adoption |
