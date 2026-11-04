---
date: "2026-09-02"
project: "2026-08-28-p10-queue-card-foundations"
meu: "MEU-41"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-28-p10-queue-card-foundations/implementation-plan.md"
build_plan_section: "bp10s10.1"
agent: "claude-opus-5"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-27-p9-capture-native-picker-MEU-40-handoff.md"
---

# Handoff: 2026-08-28-p10-queue-card-foundations-MEU-41-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-41 — `canon-queue-cards`. Author the Phase 10 spec canon
(`docs/build-plan/10-queue-card-ui.md`), annotate the two superseded `06-gui.md` blocks with
pointers instead of deleting them, port the four status-pill tokens from Zorivest into both
av-kit themes, and correct the one `AgeRestricted` status colour that deviated from the pill
palette.

**Build Plan Section**: [10 §Scope and non-goals](../../../docs/build-plan/10-queue-card-ui.md#scope-and-non-goals) (matrix item 10.1)

**Predecessor**: [`2026-08-27-p9-capture-native-picker-MEU-40-handoff.md`](2026-08-27-p9-capture-native-picker-MEU-40-handoff.md)

**Deliberately NOT in this MEU** — MEU-41 writes *canon and tokens only*. No component,
no page, no route, no service is touched. `PAGE_ISOLATION_RULE` is enforced at the gate:
every file under `FROZEN_GLOBS` (feature `*.tsx`, `router.tsx`, `main.tsx`, `mcp-server/src`,
`ui/package.json`, `ui/package-lock.json`) is byte-identical to the row-1 baseline.

---

## Acceptance Criteria

> All eight plan ACs are present. No AC was dropped or deferred.

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-41.1 | unit | **Canon exists.** `PHASE10_SPEC` (`docs/build-plan/10-queue-card-ui.md`) exists and carries every heading in `PHASE10_SECTIONS` (12 sections). | Spec (proposal §10) | `ui/tests/unit/queue-canon.test.ts` → `AC-41.1 canon exists and carries every Phase 10 section heading` | ✅ |
| AC-41.2 | unit | **Supersession pointers, not deletions.** `06-gui.md` still contains both `GUI_SPEC_SUPERSEDE_ANCHORS` blocks (`### DataTable`, `### Queue Controls`) **and** each is annotated with `SUPERSEDE_POINTER`. | Local Canon (proposal §11 conflicts 1–2); AGENTS.md "flag the conflict, do not silently pick one" | `queue-canon.test.ts` → `AC-41.2 06-gui.md keeps both superseded blocks and annotates each with the pointer` | ✅ |
| AC-41.3 | unit | **Tokens added to both themes.** Each `PORTED_TOKENS` key is declared in `THEME_BLOCK_DARK` and `THEME_BLOCK_LIGHT` with a hex byte-identical to `PILL_TOKEN_SOURCE` (`P:/zorivest/ui/src/renderer/src/globals.css`); no `STATUS_PILL_TABLE` token diverges from Zorivest. | `USER_LOCKS.pill_palette`; Local Canon `styles.css` light-block pattern; [Tailwind v4 `@theme`](https://tailwindcss.com/docs/theme) | `queue-canon.test.ts` → `AC-41.3 both themes declare the ported status tokens with Zorivest hexes` | ✅ |
| AC-41.4 | unit | **Selection fill never reuses `FORBIDDEN_SELECTION_FILL`.** No file under `UI_ROOT` pairs a selected/active state with `bg-bg-subtle`; permitted fills are `SELECTION_FILL_ALLOWED`, and the canon names them. | Local Canon (proposal §11 conflict 5 — `--color-bg-subtle` is `#6272a4` dark vs `#d1d5db` light) | `queue-canon.test.ts` → `AC-41.4 selection fill never reuses bg-bg-subtle and canon names the allowed fills` | ✅ |
| AC-41.5 | unit | **`AgeRestricted` uses the Spec token.** `download-controls.ts` `STATUS_COLORS.AgeRestricted` equals `STATUS_PILL_TABLE.AgeRestricted.fillClass` (`bg-accent-red/10`), not `bg-accent-pink`. | `USER_LOCKS.pill_palette` (supersedes the `06-gui.md` "AgeRestricted Brown" wording — Zorivest has no brown) | `queue-canon.test.ts` → `AC-41.5 STATUS_COLORS.AgeRestricted uses the Spec pill token` | ✅ |
| AC-41.6 | unit | **Locks recorded verbatim as spec.** The canon states each `USER_LOCKS` decision and, for Clear finished, **every** `CLEAR_FINISHED_SEMANTICS` clause (snapshot-once, independent `DELETE /{id}`, no abort on failure, no rollback, no disk deletion, exactly one refetch, `G35_RULE` toast with removed/failed/reason). | Human-approved (`USER_LOCKS`); `CLEAR_FINISHED_SEMANTICS` (reviewer R4-F4) | `queue-canon.test.ts` → `AC-41.6 canon records every user lock, including all Clear-finished clauses` | ✅ |
| AC-41.7 | unit | **Re-queue contract and non-goals recorded.** The canon names `REQUEUEABLE_DOWNLOAD_STATUSES`, `REQUEUEABLE_CONVERSION_STATUSES`, `PAUSE_SCOPE`, `BULK_ENDPOINT_POLICY` and every `OUT_OF_SCOPE` entry. | Human-approved + Local Canon `06-gui.md:503-524` | `queue-canon.test.ts` → `AC-41.7 canon records the re-queue contract, pause scope, bulk policy and non-goals` | ✅ |
| AC-41.8 | unit | **Phase 10 registered in the SSOT-rendered hub.** `BUILD_PLAN` carries a Phase 10 section, `MATRIX` carries every `MATRIX_ROWS` row, `SSOT` carries every `PHASE10_MEU_IDS` id. | Local Canon `.agent/context/meu-status.yaml` + `tools/meu_status.py` | `queue-canon.test.ts` → `AC-41.8 Phase 10 is registered across BUILD_PLAN, the matrix and the SSOT` | ✅ |

### Disclosures the reviewer should check first

1. **AC-41.8 Red-ability.** Task row 1 (`WP-HUB0`) registered Phase 10 in the SSOT and rendered
   the AUTOGEN regions *before* the Red run, so the SSOT and matrix halves of AC-41.8 were
   already satisfied at Red. AC-41.8 was nevertheless genuinely Red because its third clause
   requires the two **hand-maintained** `docs/BUILD_PLAN.md` tables — the `## Build Phases`
   row and the `## Phase Specs` row — which live *outside* the AUTOGEN markers and were
   authored in Green. **No AUTOGEN table was hand-edited at any point**; `meu_status.py render
   --check` is clean.
2. **AC-41.4 is a composite** (canon assertion + permanent source scan) by construction. Zero
   `bg-bg-subtle` selection pairings exist in the tree today, and the three existing
   selected-state pairings all live in `FROZEN_GLOBS` files that MEU-41 may not touch. A pure
   source scan would therefore have been green at Red, so the AC pairs the scan (a permanent
   regression guard for MEU-45+) with a canon assertion that names `SELECTION_FILL_ALLOWED` —
   the canon half is what made it Red.
3. **AC-41.3 has a workstation dependency.** It reads `PILL_TOKEN_SOURCE` at
   `P:/zorivest/ui/src/renderer/src/globals.css`. If that path is absent the test **fails
   loudly** — it does not skip, per G36. This is the same disclosure class as `E2E_SANDBOX`:
   a reviewer without the Zorivest tree mounted will see AC-41.3 fail for environment, not
   for defect. The ported hexes are quoted verbatim in the Evidence section below so the
   comparison can be made by eye.

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

All eight tests were written in `ui/tests/unit/queue-canon.test.ts` **before** any canon, token
or `download-controls.ts` edit, and observed failing. The Red receipt is
`C:/Temp/av-kit/fail-to-pass-meu-41-ui.txt` (+ `.json`); the oracle receipt is
`C:/Temp/av-kit/red-oracle-meu-41.txt` → `PASS: RED_ORACLE ui MEU-41 AC-41 count=8`.

| Test | Red Output (snippet) | Green Output | File:Line |
|------|---------------------|--------------|-----------|
| `AC-41.1 canon exists and carries every Phase 10 section heading` | `missing docs/build-plan/10-queue-card-ui.md: expected false to be true` | passes — 12 of 12 `PHASE10_SECTIONS` headings present | `ui/tests/unit/queue-canon.test.ts` |
| `AC-41.2 06-gui.md keeps both superseded blocks and annotates each with the pointer` | `### DataTable lacks SUPERSEDE_POINTER: expected '### DataTable\n\nTanStack Table wrapp…' to contain 'Superseded for queue surfaces by docs…'` | passes — both anchors present, each annotated | `docs/build-plan/06-gui.md:529`, `:1099` |
| `AC-41.3 both themes declare the ported status tokens with Zorivest hexes` | `ui/src/renderer/src/styles.css light --color-status-pending: expected undefined to be '#ea580c'` | passes — 4 tokens × 2 themes byte-identical to Zorivest | `ui/src/renderer/src/styles.css:57-59`, `:110-113` |
| `AC-41.4 selection fill never reuses bg-bg-subtle and canon names the allowed fills` | `missing docs/build-plan/10-queue-card-ui.md: expected false to be true` | passes — canon names `SELECTION_FILL_ALLOWED`; source scan finds 0 forbidden pairings | `docs/build-plan/10-queue-card-ui.md` §Card state precedence |
| `AC-41.5 STATUS_COLORS.AgeRestricted uses the Spec pill token` | `expected 'bg-accent-pink' to be 'bg-accent-red/10'` | passes | `ui/src/renderer/src/features/downloader/download-controls.ts:49` |
| `AC-41.6 canon records every user lock, including all Clear-finished clauses` | canon file absent → all 18 lock/clause greps unmatched | passes — 18 of 18 matched | `docs/build-plan/10-queue-card-ui.md` §User locks, §Selection and bulk model |
| `AC-41.7 canon records the re-queue contract, pause scope, bulk policy and non-goals` | canon file absent → all 14 contract greps unmatched | passes — 14 of 14 matched | `docs/build-plan/10-queue-card-ui.md` §Re-queue contract, §Scope and non-goals |
| `AC-41.8 Phase 10 is registered across BUILD_PLAN, the matrix and the SSOT` | `docs/BUILD_PLAN.md` had no `## Build Phases` Phase 10 row and no `## Phase Specs` row for `10-queue-card-ui.md` | passes | `docs/BUILD_PLAN.md` (hand-maintained tables); `docs/build-plan/build-priority-matrix.md:59-67` |

Red totals: `Test Files 1 failed | 40 passed (41)`, `Tests 8 failed | 329 passed (337)`.
No test assertion was modified between Red and Green (test immutability).

### Commands Executed

Every command ran under the P0 redirect-to-file pattern with receipts under `C:/Temp/av-kit/`.

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `assert-page-isolation.ps1 -SelfTest` + `assert-red-oracle.ps1 -SelfTest` (row 1) | 0 | both oracles proved they REJECT every mutation class, not merely that they pass a clean tree |
| `assert-page-isolation.ps1 -Capture` (row 1) | 0 | `PAGE_BASELINE` written — `C:/Temp/av-kit/page-isolation-baseline.json`, 20,368 bytes |
| `python tools/meu_status.py render` then `render --check` (row 1, `WP-HUB0`) | 0 | Phase 10 + MEU-41–49 registered; AUTOGEN regions rendered from the SSOT; drift check clean |
| `npx vitest run --allowOnly=false` (row 2, Red) | 1 by design | `Tests 8 failed \| 329 passed (337)` — receipt `C:/Temp/av-kit/fail-to-pass-meu-41-ui.txt` |
| `assert-red-oracle.ps1 -Kind ui -Meu 41` (row 2) | 0 | `PASS: RED_ORACLE ui MEU-41 AC-41 count=8` — 8 distinct mapped ids, equal to `RED_COUNT_41` |
| `tsc --noEmit` → `vitest run --allowOnly=false` → `eslint src/ tests/ --max-warnings 0` → `npm run build` (row 3, Green) | 0 | `Test Files 41 passed (41)`, `Tests 337 passed (337)`, three `built in …` lines — receipt `C:/Temp/av-kit/ui-green-meu-41.txt` |
| Row 4 `MEU_SCOPED_GATE_UI` (the above, plus anti-placeholder on `PLACEHOLDER_PATHS_41`, G36 on `G36_TEST_PATHS_UI`, `PAGE_ISOLATION_CHECK`, `HANDOFF_SOURCE_READ_41` + handoff existence/ordering/AC-coverage checks) | 0 | `PASS: MEU-41 MEU_SCOPED_GATE_UI` — receipt `C:/Temp/av-kit/handoff-meu-41.txt` |

### Quality Gate Results

```
tsc --noEmit:                 0 errors
vitest:                     337 passed, 0 failed (41 files)
eslint --max-warnings 0:      0 warnings
npm run build:                0 errors (main + preload + renderer)
anti-placeholder:             0 matches (PLACEHOLDER_PATHS_41)
G36 skip/only scan:           0 matches (ui/tests/unit, ui/tests/e2e)
PAGE_ISOLATION_CHECK:         PASS — every FROZEN_GLOBS file byte-identical to baseline
registry drift:               clean (meu_status.py render --check)
```

**Final session-close verification (task.md H1-2, 2026-09-02).** Re-run over the whole tree after all four MEUs landed: pytest 507 passed - pyright 0 errors - ruff clean - tsc 0 errors - vitest 366 passed (43 files) - eslint clean - electron-vite build ok - `export_openapi.py --check` clean - `PASS: PAGE_ISOLATION frozen=28 carveout=2 scanned=73 e2e=59 preserved=42`. Receipt `C:/Temp/av-kit/full-verify.txt`.

**Playwright E2E passes: 59 passed / 0 failed, EXIT=0** (task.md H1-2a), on a bundle rebuilt after the last source change (P9 RULE-1). Receipt `C:/Temp/av-kit/e2e-regression-rerun.txt`. This **retracts** the earlier `[B]` and its "external electron 42.9.3 / playwright-core 1.62.1 incompatibility" claim: the real cause of `electron.exe: bad option: --remote-debugging-port=0` was `ELECTRON_RUN_AS_NODE=1` set in the agent's own shell (inherited from the Cursor extension host) and spread into the launched app by `...process.env` at all 14 `_electron.launch()` sites. Proof: `electron --version` prints `v24.18.1` with the variable set and `v42.9.3` without. Known-issue `E2E-ELECTRON-LAUNCH-FLAG` has been re-filed against that real cause (env leakage through `...process.env`, severity lowered to low). The specs stay written and wired; no wave was added or removed (`E2E_NEW_WAVES_THIS_SESSION` = 0).

### Ported token values (AC-41.3 — verbatim from `P:/zorivest/ui/src/renderer/src/globals.css`)

| Token | Dark | Light |
|-------|------|-------|
| `--color-status-pending` | `#ffb86c` | `#ea580c` |
| `--color-status-filled` | `#50fa7b` | `#16a34a` |
| `--color-status-rejected` | `#ff5555` | `#dc2626` |
| `--color-status-canceled` | `#6272a4` | `#64748b` |

The five accent tokens the pill table also uses (`accent-cyan`, `accent-yellow`, `accent-purple`,
`accent-orange`, `accent-red`) already matched Zorivest byte-for-byte and were **not** touched.
No existing av-kit token was repointed.

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `docs/build-plan/10-queue-card-ui.md` | new | 327 | The Phase 10 canon — 12 `PHASE10_SECTIONS` headings, the 9-slice in-scope table, the 8-row non-goals table, `USER_LOCKS`, the 10-row status token table, card-state precedence, primary-action map, kebab table, bulk/selection model, toolbar reduction, reorder model, re-queue contract, supersession table |
| `docs/build-plan/06-gui.md` | modified | 527-530, 1097-1100 | Two `> [!NOTE]` supersession blocks inserted. **Nothing deleted** |
| `ui/src/renderer/src/styles.css` | modified | 57-59, 110-113 | Four status-pill tokens added to the dark `@theme` block and the light `:root:not(.dark)` block |
| `ui/src/renderer/src/features/downloader/download-controls.ts` | modified | 49 | `AgeRestricted` pill token corrected to the Spec value |
| `ui/tests/unit/queue-canon.test.ts` | new | 285 | AC-41.1 – AC-41.8 |
| `docs/BUILD_PLAN.md` | modified | Build Phases + Phase Specs tables | Phase 10 rows added to the two **hand-maintained** (non-AUTOGEN) tables |
| `.agent/context/meu-status.yaml` | modified | phase `'10'`, `MEU-41`–`MEU-49`, P2 band range | SSOT registration (row 1) |
| `.agent/context/meu-registry.md`, `docs/build-plan/build-priority-matrix.md` | modified | AUTOGEN regions | Rendered from the SSOT by `tools/meu_status.py render` — never hand-edited |
| `docs/execution/plans/2026-08-28-p10-queue-card-foundations/task.md` | modified | rows 1–4 | Rows closed with evidence |
| `docs/execution/plans/2026-08-28-p10-queue-card-foundations/named-sets.json` | modified | `E2E_BASELINE_COUNT`, `E2E_BASELINE_BASIS` | Stale planning constant corrected 55 → 59 — see §Plan-constant corrections |
| `docs/execution/plans/2026-08-28-p10-queue-card-foundations/implementation-plan.md` | modified | §Verification Plan §1 | Stale `-Meu 42 \| 43 \| 44` literal corrected to `-Meu 41 \| 43 \| 44` (MEU-40→MEU-41 renumber residue) |

**`06-gui.md` — pointer, not deletion** (both blocks follow the same shape):

```diff
 ### DataTable

+> [!NOTE]
+> **Superseded for queue surfaces by docs/build-plan/10-queue-card-ui.md**
+> Queue surfaces render row-cards, not tables — see [Phase 10 QueueCard anatomy](10-queue-card-ui.md#queuecard-anatomy). The block below is retained as the historical spec and still applies to any non-queue table.
+
 TanStack Table wrapper providing consistent table behavior across Downloader and future features:
```

**`styles.css` — both themes, Zorivest hexes:**

```diff
   --color-status-pending: #ffb86c;
+  --color-status-filled: #50fa7b;
+  --color-status-rejected: #ff5555;
+  --color-status-canceled: #6272a4;
```

```diff
   --color-success-ring: #16a34a;
+  --color-status-pending: #ea580c;
+  --color-status-filled: #16a34a;
+  --color-status-rejected: #dc2626;
+  --color-status-canceled: #64748b;
```

**`download-controls.ts` — the one Spec-conformance fix:**

```diff
-  AgeRestricted: 'bg-accent-pink',
+  AgeRestricted: 'bg-accent-red/10',
```

---

## Plan-constant corrections (2026-09-02)

Two plan-file constants were stale before MEU-41 ran. Both are recorded here rather than
silently patched, per AGENTS.md §Communication Policy.

**1. `E2E_BASELINE_COUNT` 55 → 59.** The first row-4 gate run failed:

```
E2E test count 59 != E2E_BASELINE_COUNT 55
```

This is **concurrent-session drift in a planning constant, not a Phase 10 change.** The
constant was counted on 2026-08-28 (`49 test( calls in *.test.ts + 6 in *.spec.ts`). On
2026-09-01 the concurrent `2026-08-27-p9-capture-native-picker` session landed
`ui/tests/e2e/capture-picker.test.ts` (4 tests, its AC-40.18) — confirmed by that session's
handoff, `npx playwright test tests/e2e/capture-picker.test.ts` → `4 expected`. Recount on
2026-09-02: 53 in `*.test.ts` + 6 in `*.spec.ts` = 59, and the delta is exactly those 4 tests.
**Phase 10 has added no E2E test.**

The oracle was not weakened. `assert-page-isolation.ps1` check 4 has two independent parts,
and the *identity* part — a `Compare-Object` of the full E2E title SET against the row-1
content baseline — **passed clean** both before and after the correction; only the second
tripwire, the literal count, was stale. That tripwire exists to catch a baseline captured on
an already-mutated tree, so pointing it at the truthful current count preserves its function.
`assert-page-isolation.ps1 -SelfTest` was re-run after the edit and still **rejects all 19
mutation classes** (`PASS: PAGE_ISOLATION selftest 19 cases`, receipt
`C:/Temp/av-kit/page-iso-selftest-r2.txt`). `E2E_BASELINE_BASIS` now records the recount and
this rationale.

**2. `-Meu 42 | 43 | 44` → `-Meu 41 | 43 | 44`** in `implementation-plan.md`
§Verification Plan §1. Residue of the MEU-40→MEU-41 renumber (MEU-40 was claimed by the
concurrent p9 session, so this plan's ids shifted +1). Prose only — no executable receipt
referenced the wrong number; every task-table command already carried `-Meu 41`.

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
| — | — | _pending review_ | — | — | — |

### Verdict

_pending_

---

## Deferred Items

_No AC was deferred. The items below are Phase 10 scope that MEU-41 deliberately does not
implement, each already registered as a scheduled MEU in the SSOT._

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| Convert / Downloader / Transcript page migration to `QueueList` | out-of-scope (canon MEU) | MEU-45, MEU-46, MEU-48 | `.agent/context/meu-status.yaml` phase `'10'` |
| Selection model, sticky bulk bar, Clear finished fan-out | out-of-scope (canon MEU) | MEU-47 | canon §Selection and bulk model |
| Drag-and-drop reorder (`dnd-kit`) | `USER_LOCKS.dnd_deferred` | MEU-49 | canon §Reorder model |
| Remove-confirm undo toast | `USER_LOCKS.remove_confirm` — light verb-labeled confirm ships, undo deferred | MEU-47 | canon §User locks |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-02 | claude-opus-5 | Initial handoff — MEU-41 canon + tokens, 8 ACs, gate green |
| Plan constants corrected | 2026-09-02 | claude-opus-5 | `E2E_BASELINE_COUNT` 55→59 (concurrent-session drift); stale `-Meu` literal |
