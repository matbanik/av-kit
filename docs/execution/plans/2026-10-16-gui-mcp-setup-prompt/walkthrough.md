# Walkthrough — GUI MCP setup prompt (Session 31b)

Execution record for [implementation-plan.md](implementation-plan.md) and [task.md](task.md). Worktree `P:/av-kit-wt/s31b-gui-mcp-setup-prompt`, branch `claude/s31b-gui-mcp-setup-prompt`. Receipts are under `C:/Temp/av-kit/s31b-*.txt`; decisive lines are pasted here.

## Execution authorization

- **Execution gate (`plan_to_exec_gate: human`).** Plan review loop `s31b-plan-2026-10-16-gui-mcp-setup-prompt` closed `approved` in round 3 (3/3). On 2026-10-17 Mat asked, verbatim: `@.agent/workflows/execution-session.md  for "docs/execution/plans/2026-10-16-gui-mcp-setup-prompt" give me go or no-go`. Mat's explicit execution message, 2026-10-17, verbatim: `proceed`.
- **Grouping D-56 ruling.** Mat's message of 2026-10-16, verbatim: `1. increase budget to 20M 2. Accept 3. approved as proposed`. Item 2 accepts the plan's Decision Brief recommendation (option 1: MEU-92 `dist-mcp-server-bundle` in this session after MEU-71). Row 0 recorded it:
  - in the grouping D-56 row (`human` / `Human-approved`), the Session 31b row, the §3 graph and the §4 pathway;
  - by registering MEU-92 in `meu-status.yaml` (phase `'7'`, band P2, matrix item `7.5`, `07-distribution.md#mcp-server-bundle-residual`, depends on MEU-25 and MEU-71, `pending`) and extending the P2 band to MEU-92;
  - by adding the 07 §MCP server bundle (residual) section and naming MEU-92 in the 07 setup-prompt Command row;
  - by re-rendering: `meu_status.py render` exit 0, `render --check` exit 0 (`92 MEUs, 12 phases`; receipt `C:/Temp/av-kit/s31b-render.txt`).
- **Worktree.** The plan's worktree no longer existed. Mat, 2026-10-17, verbatim: `1. recreate as you described`. It was recreated from `main` at `6097cf5`, which contains the plan commit `7014cd0` (`git merge-base --is-ancestor 7014cd0 HEAD` true) and Sessions 37 and 39.
- **Context tools.** Mat, 2026-10-17, verbatim: `2. do not use` (Headroom). The execution-phase `context_tool_decision` is recorded in [task.md](task.md) §Context Tool Decision (`not_applicable`; no graph directory exists).
- **Session 35 in parallel.** Mat asked, verbatim: `Should we wait for Session 35 to complete before proceeding?` The recommendation was to run in parallel. Session 35 (`P:/av-kit-wt/s35-tts-voice-panel`) shares only `build-priority-matrix.md` and the rendered status files with this plan, and none of `PKG_FILES`. Whichever session lands second merges `main`, re-renders the status files and re-runs its full gate. Mat's reply was the `proceed` above. Process kills in this session are scoped to this worktree's path.
- **Drift since the plan commit.** 94 files changed on `main` between `7014cd0` and `6097cf5` (receipt `C:/Temp/av-kit/s31b-main-drift.txt`). None invalidates the plan:
  - the plan scripts resolve MEUs and rows by id, not by line;
  - `baseline.sha` and `baseline-counts.json` are written at row 0, after the drift;
  - `ui/tests/e2e/test-ids.ts:45-51` is unchanged;
  - `INDEX_ROW` is placed after the `settings:pin_mcp` row by key, and that row is now at line 100.
- **Environment.** The worktree `.venv` was created on CPython 3.12.12 (receipt `C:/Temp/av-kit/s31b-venv.txt`: `Using CPython 3.12.12`). An inherited `VIRTUAL_ENV=p:\av-kit\.venv` is unset; `validate-task.ps1` removes it itself.
- **Latest reflection rules** (`docs/execution/reflections/2026-10-16-capture-new-marks-reflection.md` §Next Session Design Rules):
  - RULE-1 (RECEIPTS_DIR and the 3.12.12 venv): applied. `validate-task.ps1` sets `RECEIPTS_DIR`, and the venv is 3.12.12.
  - RULE-2 (the execution-review prompt states the approval coupling): applied at H1-7.
  - RULE-3 (diagnostics for the known flaky E2E `DOWNLOAD-QUEUE-DRAG-OVER-MISS`): not applied. Adding those diagnostics needs its own triaged MEU and is outside `PRODUCT_SCOPE`. If AC-49.25, W2-5 or AC-49.29 trips a full Electron run here, it is handled as S8: evidence recorded, a Decision Brief, and the row is never marked `[x]`.

## Baseline (row 0)

The first run below failed and was superseded: Amendment A-1 (row 0a) and D-93 resolved both gaps, and §Baseline re-run records the passing run.

- **Row command** (task row 0, verbatim, from the worktree in `pwsh`): exit 1. Receipt `C:/Temp/av-kit/s31b-run-baseline.txt`.
- **Passed before the failure:** the headroom decision check; `prereq` (`PASS grouping D-56 ruled; MEU state {'MEU-23': 'approved', 'MEU-25': 'approved', 'MEU-71': 'pending', 'MEU-92': 'pending'}; execution_plan set`); `selftest`; `npm-ci`; `mcp-build`; `ui-build`; `ui-harness-build`. `baseline.sha` was written as `6097cf59adc7835fa6062c8bd3d55c679aef4543`.
- **Failure:** `baseline-ui-vitest`: 1 failed and 974 passed (975). `FAIL: baseline-ui-vitest failing tests: ['Phase 10 queue-card canon (MEU-41) AC-41.3 both themes declare the ported status tokens wi']`. Receipt `C:/Temp/av-kit/s31b-baseline-ui-vitest.txt`:
  - `tests/unit/queue-canon.test.ts:173`: `PILL_TOKEN_SOURCE light --color-status-pending: expected '#9a3412' to be '#ea580c'`.
- **Cause: an external repository moved; av-kit did not.**
  - `queue-canon.test.ts:12` reads `PILL_TOKEN_SOURCE = 'P:/zorivest/ui/src/renderer/src/globals.css'` from zorivest's working tree.
  - Zorivest commit `1f254832` (2026-10-16 21:30 -0400, "fix(ui): darken the light text palette and drop opaque bg-subtle under text (MEU-662)") darkened its light block. In the tokens AC-41.3 compares:
    - light status: pending `#ea580c` → `#9a3412`, filled `#16a34a` → `#166534`, rejected `#dc2626` → `#991b1b`;
    - light accents: cyan `#0e7490` → `#155e75`, orange `#ea580c` → `#9a3412`, red `#dc2626` → `#991b1b`, yellow `#ca8a04` → `#854d0e`, purple `#7c3aed` → `#6d28d9`.
  - av-kit's own token file still equals `PORTED_TOKENS`. The parent zorivest commit `61243baf` still holds every ported hex.
  - So `main` at `6097cf5` fails AC-41.3 independently of this plan. No file this plan touches is involved.
- **Evidence-only runs outside the gate** (no baseline counts written):
  - `mcp-server` Vitest: exit 0, 26 files, 428 passed (`C:/Temp/av-kit/s31b-s8-mcp-vitest.txt`).
  - Full Playwright: exit 1, 153 passed and 4 failed (`C:/Temp/av-kit/s31b-s8-e2e.txt`). All four failures are `tests/e2e/capture-picker.test.ts` (:203, :227, :243, :260), each failing in 1–7 ms with `Error: the deterministic sidecar stub is missing: run "npm --prefix ui run build:picker-stub"` (or `spawn … avkit-region-picker-stub.exe ENOENT`). The stub lives under the gitignored `native/**/publish/`, so a freshly created worktree does not have it.
  - Stub built with the repo's own script: `npm --prefix ui run build:picker-stub`, exit 0 (`C:/Temp/av-kit/s31b-s8-picker-stub.txt`). It writes only ignored output; `git status` shows nothing under `native/`. Re-running `capture-picker.test.ts` alone gave exit 0, 4 passed (`C:/Temp/av-kit/s31b-s8-e2e-capture-picker.txt`). This second gap is environment setup that has now been done. It needs no decision, and the next baseline run covers it.

### S8 stop: AC-41.3 reads a live external file (row 0 stays `[ ]`, human decision)

Plan §Stop Conditions S8: "A gate failure that is not a product defect (environment, flaky infrastructure): Record the evidence and present a Decision Brief; never mark the row `[x]`." `baseline-counts.json` was not written, and no test has been edited.

Decision Brief (AC-41.3), superseded by Mat's direction below:

| Option | Change | Effect | Reversible |
|--------|--------|--------|------------|
| 1 (recommended) | On `main`, read AC-41.3's `PILL_TOKEN_SOURCE` from the zorivest commit the port was taken from (`git -C P:/zorivest show 61243baf:ui/src/renderer/src/globals.css`, which holds every `PORTED_TOKENS` hex: light pending `#ea580c`, filled `#16a34a`, canceled `#64748b`, rejected `#dc2626`). The assertions and `PORTED_TOKENS` are unchanged. Then merge `main` here and re-run `-Check baseline` | The test checks provenance against a fixed source and no longer breaks when zorivest moves. Session 35 gets the same fix | Two-way |
| 2 | Port MEU-662's darker light palette into av-kit and update `PORTED_TOKENS` | A product and visual change outside this plan's `PRODUCT_SCOPE`; it needs its own triaged MEU. The test stays coupled to zorivest's live working tree | Two-way, but larger |
| 3 | Plan correction: exclude AC-41.3 from the baseline, `COUNT_FLOORS` and the gate | Weakens the gate and needs edits to `plan_checks.py` and the plan | Two-way |

In every option, a known-issue entry should record that AC-41.3 read a live external working tree. Adopting MEU-662's contrast palette can go to triage separately.

#### Mat's direction and the HDP re-run

Mat, 2026-10-17, verbatim: `decouple anything to do with zorivest and create our own copy of files` / `run human decision protocol and give me recommendation again`. The decision to decouple is made. What follows applies `.agent/docs/human-decision-protocol.md` to the remaining forks.

**Precedent sweep** (receipt `C:/Temp/av-kit/s31b-zv-active-paths.txt`):

- Code: one runtime read, `ui/tests/unit/queue-canon.test.ts:12` (`PILL_TOKEN_SOURCE`). `chrome-zorivest.test.ts` reads only av-kit's renderer. The `mcp-server/scripts/audit` mentions are comments.
- Canon that points at the live tree:
  - `docs/build-plan/10-queue-card-ui.md:64` and `:116-117` ("Colour is whatever `P:/zorivest` declares; av-kit authors no hue of its own");
  - `docs/build-plan/gui-actions-index.md:3` ("Zorivest twin: `P:/zorivest/docs/build-plan/gui-actions-index.md`");
  - `docs/BUILD_PLAN.md:129` principle 4 ("check Zorivest before inventing GUI chrome");
  - `.agent/docs/cloud-local-collaboration.md:220` (AC-41.3 already fails in cloud containers because the path is absent).
- Path citations in active records: `globals.css` (4), `05n-agent-connect.md` (1, the D-51 source behind this plan), `gui-actions-index.md` (1). Other mentions in active build-plan docs name Zorivest as the origin of a pattern ("Adapt Zorivest `AppShell.tsx`"). They do not make av-kit read anything.
- The same class was decided before:
  - `_inspiration/_zorivest_mcp_tool_audit_skill.md`: Mat committed a copy of a zorivest file so av-kit would stop extracting it from `P:/zorivest` (known-issues `MCP-LIVE-AUDIT-WORKFLOW`, 2026-09-30).
  - Known issue `QUEUE-PILL-TOKEN-DRIFT` (open): its resolution path was to re-port MEU-662's three hexes.
  - Session 37 amendment A-4 (Mat chose option 1, 2026-10-16): AC-41.3 was carried as a listed baseline failure.
  - 2026-10-14 `plan_checks.py:62` `BASELINE_RED`: the same test, the same cause, an earlier zorivest move (accent cyan).
  - So AC-41.3 has broken three times as zorivest moved.
- zorivest state: HEAD `ca693695`, with 218 uncommitted working-tree entries. A live read is not a stable input.

**Research** (rung 1, Pomera `tavily`/`exa`):

- testRigor, hermetic testing (practice): a failure should mean a bug in the code, not an external factor.
- open-mercato PR #4277 (practice): `globals.css` tokens are held in a committed canonical snapshot, and a drift check names each drifted token.
- RevealUI 942c83a (practice): a canonical `tokens.css` mirror with `MANIFEST.sha256`, and a parity test that fails on drift.
- WebAIM, Contrast (authority): WCAG 1.4.3 requires 4.5:1 for text; 1.4.11 requires 3:1 for icons and other non-text.
- TestParty, 1.4.11 (practice): status icons are held to 3:1.
- Against the pills: labels are `text-fg` (4.5:1 is cleared, worst case 6.61, `10-queue-card-ui.md:118-120`). The hue only colours the icon and a 10% fill. On white, light `#ea580c` is about 3.56:1 and `#16a34a` about 3.30:1, so the current hexes pass 1.4.11.

**D-89 (autonomous, Local Canon plus Research-backed): the shape of the copy.**

- Copies go under `_inspiration/zorivest/`, following the `_zorivest_mcp_tool_audit_skill.md` precedent.
- Each file is taken from a named zorivest commit with `git show <sha>:<path>`, never from the working tree.
- A `PROVENANCE.md` records source path, commit, date and sha256 for each copy.
- `queue-canon.test.ts` reads the copy. Its assertions and `PORTED_TOKENS` do not change.
- Why this needs no ruling: it converges on precedent and research, is two-way, has no user-visible effect, and sets no threshold.

**Human-gated briefs D-90, D-91 and D-92** were presented in the reply that ended that turn.

#### Mat's ruling

Mat, 2026-10-17, verbatim: `D-90 61243baf, D-91 A, D-92 A-1`.

- **D-90:** the copy of `globals.css` is Zorivest `61243baf`, the commit before MEU-662. It equals what av-kit ships, so nothing visible changes.
- **D-91 A:** every dependency on the Zorivest checkout goes and the history stays. AC-41.3 reads the copy, and the four canon pointers make av-kit the owner, with Zorivest as provenance only. `globals.css` and `gui-actions-index.md` are copied at `61243baf`, `05n-agent-connect.md` at `ca693695`. `QUEUE-PILL-TOKEN-DRIFT` closes with its re-port path overturned. Closed plans, handoffs, reflections and decision records are not edited.
- **D-92 A-1:** plan amendment A-1 adds row 0a before the baseline. H1-7 reviews it, and at closeout it is proposed as its own commit ahead of the MEU-71/92 commit.
- **D-93 (autonomous, Local Canon):** `baseline` and `gate` build the region-picker stub before the Electron suite (RULE-1). This closes the second gap above.
- The plan records D-89 to D-93 in its Decision Log and §Amendment A-1, and task row 0a is added.

## Amendment A-1 (row 0a)

- **Copies** (`_inspiration/zorivest/`, taken with `git -C P:/zorivest show <commit>:<path>`; the Zorivest repository was only read). Each git blob id equals Zorivest's:

  | File | Commit | Blob | Bytes (LF) |
  |------|--------|------|------------|
  | `globals.css` | `61243baf` | `f12b4614baee11f07eb4512dde34727c1a5e6b81` | 14513 |
  | `gui-actions-index.md` | `61243baf` | `0425de06becf0a0bebf0a31a210320ab3af209f6` | 18580 |
  | `05n-agent-connect.md` | `ca693695` | `e864dd8ec88508a69a91520f9215a1ac9ee9ce0d` | 178314 |

  `PROVENANCE.md` holds each row with its sha256, and a table of who cites each copy.
- **Red** before the test change: `npm --prefix ui run test -- tests/unit/queue-canon.test.ts` gave 1 failed and 7 passed. AC-41.3 failed on `Expected "#ea580c" Received "#9a3412"` from the live Zorivest file. Receipt `C:/Temp/av-kit/s31b-0a-red-queue-canon.txt`.
- **Test change:** `queue-canon.test.ts:12` `PILL_TOKEN_SOURCE` now reads `resolve(repoRoot, '_inspiration/zorivest/globals.css')`, and the comment at `:49` names it. The assertions, the test title and `PORTED_TOKENS` are unchanged.
- **Green:** the same command gave 8 passed. Receipt `C:/Temp/av-kit/s31b-0a-green-queue-canon.txt`.
- **Canon:**
  - `10-queue-card-ui.md` `:64` and §Status token table: av-kit owns its pill palette, seeded from the copy;
  - `gui-actions-index.md:3`: av-kit owns its index, modelled on the copy;
  - `BUILD_PLAN.md` golden rule 4: "Patterns originally from Zorivest … do not consult `P:/zorivest`";
  - `cloud-local-collaboration.md`: AC-41.3 leaves `ENV_BOUND_TESTS`.
- **Issue:** `QUEUE-PILL-TOKEN-DRIFT` is `resolved`, with its evidence in this file. Both render checks pass (`C:/Temp/av-kit/s31b-0a-render-check.txt`).
- **Validation:**
  - Task row 0a verbatim (`-Check decouple`): exit 0. `PASS decouple: copies match PROVENANCE.md; no live Zorivest path in 474 files; AC-41.3 reads the copy; QUEUE-PILL-TOKEN-DRIFT resolved`; queue-canon 8 of 8; both render checks. Receipt `C:/Temp/av-kit/s31b-run-decouple.txt`.
  - `-Check static`: exit 0, `PASS static: 21 rows, 20 -Check names, 19 ACs covered`, `PASS selftest` (the decouple self-test included), `PASS task-lint`. Receipt `C:/Temp/av-kit/s31b-run-static.txt`. The first run failed the task lint because row 0a named two contract-style identifiers the plan does not define; the row was reworded.
  - Row 0a is `[x]`.

## Baseline re-run (row 0)

- **Row command** (task row 0, verbatim, from the worktree in `pwsh`): exit 0. Receipt `C:/Temp/av-kit/s31b-run-baseline.txt`. It replaces the failed first run above.
- **Steps:** the headroom decision check; `prereq` (`PASS grouping D-56 ruled; MEU state {'MEU-23': 'approved', 'MEU-25': 'approved', 'MEU-71': 'pending', 'MEU-92': 'pending'}; execution_plan set`); `selftest`; `npm-ci`; `mcp-build`; `ui-build`; `ui-harness-build`; `picker-stub` (D-93); then the three suites.
- **Counts:** ui Vitest 975 passed of 975 (AC-41.3 now reads the copy); mcp-server Vitest 428 passed of 428; Playwright 157 passed, 0 skipped, 0 unexpected, 0 flaky (4.8 m), the four `capture-picker` specs included.
- **Written:** `baseline.sha` = `6097cf59adc7835fa6062c8bd3d55c679aef4543` (HEAD); `baseline-counts.json` = `{ui_vitest_passed: 975, ui_vitest_failed: 0, mcp_vitest_passed: 428, mcp_vitest_failed: 0, e2e_expected: 157, e2e_skipped: 0, e2e_unexpected: 0, e2e_flaky: 0}`. Last line `PASS baseline @ 6097cf59adc7835fa6062c8bd3d55c679aef4543`.
- Row 0 is `[x]`.

## Census (row 1)

- **Row command** (task row 1, verbatim): exit 0, `PASS census: 173 lines in C:/Temp/av-kit/s31b-census.txt`. Receipt `C:/Temp/av-kit/s31b-run-census.txt`. Of the 173 lines, 172 are hits; line 1 is the `rtk` hook banner.
- **Result:** 172 hits, all classified as TA-1, TA-2, TA-3 or `unaffected`. No `new-contradiction`, so Stop condition S2 does not apply. The table was generated from the receipt by a script that fails on any hit without a disposition.
- **Dispositions** (rows grouped by file and disposition; the last two rows fold every hit of the same kind across files):

| File | Lines | Disposition |
|------|-------|-------------|
| `mcp-server/tests/tts.test.ts` | :2, :42, :43, :48 | unaffected: `SETUP_INSTRUCTION` is appended; the existing lines and their order stay |
| `mcp-server/tests/tools-parity.test.ts` | :161 | unaffected: `SETTINGS_UI_API_KEYS` is a different identifier the `API_KEYS` pattern also matches |
| `mcp-server/tests/convert.test.ts` | :6, :128, :129, :130 | unaffected: `SETUP_INSTRUCTION` is appended; the existing lines stay |
| `mcp-server/tests/runtime.test.ts` | :5, :20, :24, :25, :26, :27 | unaffected: AC-71.12 appends `SETUP_INSTRUCTION` and an append-only test; these assertions stay |
| `mcp-server/tests/m7-resource.test.ts` | :3, :60 | unaffected: `SETUP_INSTRUCTION` is appended; the existing lines stay |
| `mcp-server/tests/capture.test.ts` | :6, :173, :174, :175, :176, :177, :463, :464, :465, :466, :467, :468, :469, :472 | unaffected: `SETUP_INSTRUCTION` is appended; the existing lines stay |
| `ui/tests/unit/web-prefs-ipc.test.ts` | :3, :17, :18, :19, :30, :31 | unaffected (note): its expectation, that every test-side channel is registered, does not change. It reads the list TA-1 extends, so between rows 2 and 3 it fails until row 3 registers the channel. It is not in the row 2 Red set, and row 5 runs it green |
| `mcp-server/tests/audit/run-cli.test.ts` | :75, :77, :83 | unaffected: the MEU-68 audit runner's own `node` launch fixture, not the shipped example or the packaged entry |
| `ui/tests/e2e/test-ids.ts` | :45, :46, :51 | unaffected: existing ids unchanged; `NEW_TESTIDS` is appended as one block |
| `ui/tests/unit/ipc-strict-census.test.ts` | :3, :55, :73 | unaffected: iterates the test-side lists; TA-1 extends the list, and `IPC_NO_PAYLOAD` stays as is |
| `ui/tests/unit/ipc-strict-census.test.ts` | :54 | TA-1: count pin 20 → 21; the valid (~:25) and type-failure (~:48) tables gain `get-mcp-setup-prompt` |
| `ui/tests/unit/ipc-channels.ts` | :1 | TA-1: `get-mcp-setup-prompt` appended after `'write-clipboard-image'` (:21) |
| `ui/tests/unit/ipc-channels.ts` | :33 | unaffected: the new channel takes a payload, so it is not in `IPC_NO_PAYLOAD` (TA-1) |
| `ui/tests/unit/clipboard-image-main.test.ts` | :8, :9, :10, :100, :102, :104 | unaffected: equality with the test-side list holds once TA-1 and row 3 both add the channel |
| `ui/tests/unit/clipboard-image-main.test.ts` | :101 | TA-1: count pin 20 → 21 |
| `mcp-server/tests/audit/report.test.ts` | :28, :30, :85 | unaffected: the MEU-68 audit report fixture strings; `copy-mcp-config` keys are unchanged |
| `ui/tests/unit/login-item-ipc.test.ts` | :7, :27, :28, :29, :46, :47, :48, :49, :52, :58, :59 | unaffected: membership and list equality, unchanged expectations |
| `ui/tests/unit/login-item-ipc.test.ts` | :50, :51 | TA-1: count pins 20 → 21 |
| `ui/tests/unit/gui-actions-audit.test.ts` | :7, :9, :37, :38, :43, :70, :165, :209, :212, :232, :233, :269, :270 | unaffected: existing rows, ids and channels keep their expectations (`copy-mcp-btn`, `pin-mcp-btn`, `mcp-token-present` stay in source) |
| `ui/tests/unit/gui-actions-audit.test.ts` | :29 | TA-2: `SETTINGS_HELP_TESTIDS` gains `mcp-copy-prompt-btn` → `settings:copy_mcp_prompt` |
| `ui/tests/unit/gui-actions-audit.test.ts` | :66 | TA-2: `resolveIpcChannel` gains a first line mapping `getMcpSetupPrompt` to `get-mcp-setup-prompt` |
| `ui/tests/unit/settings-rail.test.tsx` | :480 | unaffected: the token chip stays outside the disclosure; jsdom finds it either way |
| `ui/tests/unit/settings-page.test.ts` | :483, :732, :733 | unaffected: token chip text and `loginItemGet`; unchanged |
| `ui/tests/e2e/settings.test.ts` | :9 | unaffected: test path resolution, not an entry guard |
| `ui/tests/e2e/settings.test.ts` | :149, :150 | TA-3: W4-2 clicks `mcp-advanced-summary` first; the visibility assertions do not change |
| `ui/tests/e2e/settings.test.ts` | :155 | unaffected: `mcp-token-present` stays outside the Advanced disclosure (`CARD_LAYOUT`) |
| `ui/tests/e2e/settings.test.ts` | :179, :180 | TA-3: W4-3 clicks `mcp-advanced-summary` first; the clicks do not change |

- Row 1 is `[x]`.

## Red (row 2)

`-Check red71` exited 0 with `PASS red71` (receipt `C:/Temp/av-kit/s31b-run-red71.txt`).

- **mcp-server build:** `PASS mcp-build`, so AC-71.9 spawns today's `dist/index.js`.
- **ui Vitest** (`s31b-red71-ui-vitest.json`): 9 files, 17 failed and 22 passed.
  - `mcp-setup-prompt`, `mcp-server-entry` and `mcp-spawn-electron` fail to load on the missing `src/main/mcp-setup-prompt`. All three are declared new-module files.
  - `mcp-prompt-ipc`: 4 assertion failures (the channel is unknown and the preload key is absent).
  - `settings-mcp-prompt`: 8 assertion failures (the new testids are absent).
  - TA pins fail as amended: `clipboard-image-main` (1), `login-item-ipc` (1) and `gui-actions-audit` (3: AC-23.19, AC-23.20 and AC-71.14). `ipc-strict-census` passes; it is checked green from row 3.
- **mcp-server Vitest** (`s31b-red71-mcp-vitest.json`): 4 files, 5 failed and 2 passed.
  - `entry-guard` fails to load on the missing `src/entry-guard.js` (declared).
  - `entry-spawn` (1): the junction launch exits before `initialize` answers, so the answer kind is `exit`, not `response`.
  - `example-config` (2).
  - `runtime` (2): AC-71.12 sees 8 lines, not 9.
- **`vitest-red`:** `PASS MEU-71 Vitest RED: 18 assertion failures, 0 missing-symbol`. The load-tolerated files are exactly the four declared, and the TA pins fail as listed. Nothing fell under S4.
- **Build:** `PASS ui-build`.
- **Electron Red** (`s31b-red71-e2e.json`): `-g AC-71` ran 2 tests and both failed. Test 1 has no `mcp-client-select`. In test 2, `mcp-advanced` is missing, so `not.toHaveAttribute('open')` fails. `e2e-red`: `PASS MEU-71 E2E RED: ['AC-71.15']`.
- Row 2 is `[x]`.

## Green, main and server half (row 3)

`-Check green71-main` exited 0 with `PASS green71-main` (receipt `C:/Temp/av-kit/s31b-run-green71-main.txt`). The steps: `PASS mcp-types`, `PASS mcp-build`, mcp-server Vitest 12 of 12, and ui Vitest 40 of 40 on the main-half set.

- **New files:**
  - `ui/src/main/mcp-setup-prompt.ts`: `CLIENT_SET` (`MCP_CLIENTS`), `SCOPE_RULE`, `PROMPT_BUILDER`, the three client block kinds and `SERVER_ENTRY`.
  - `mcp-server/src/entry-guard.ts`: `ENTRY_GUARD`.
- **Changed files:**
  - `mcp-server/src/index.ts`: the `isMainModule` guard replaces the suffix check, and `SETUP_INSTRUCTION` is appended.
  - `ui/src/main/ipc.ts`: `PROMPT_CHANNEL`, `PROMPT_PAYLOAD`, `LAUNCH_DEP`, `PROMPT_HANDLER` and `LAUNCH_MISSING_ERROR`.
  - `ui/src/main/index.ts`: `mcpServerLaunch` is `{ command: process.execPath, serverPath: mcpServerEntry({ packaged: app.isPackaged, resourcesPath: process.resourcesPath, dirname: __dirname }) }`.
  - `ui/src/main/preload.ts`: `PRELOAD_KEY`.
  - `ui/src/renderer/src/env.d.ts`: the optional `getMcpSetupPrompt?` key.
- **Stop conditions:** S3 did not trigger: AC-71.10's Electron spawn answered `initialize` as `av-kit`, and its first stdout line was the JSON-RPC response. S5 did not trigger: the AC-71.8 junction case and the AC-71.9 junction launch both pass.
- **Sequencing fix: `EXAMPLE_CONFIG` written in row 3, not row 4.** `green71-main` runs `$mcp71`, which includes `example-config.test.ts` (AC-71.11). Row 3 could not go green with the old example, so `docs/distribution/mcp.json.example` was rewritten here to the `EXAMPLE_CONFIG` shape: the generic `JSON_BLOCKS` form, `avkit`, the three placeholders, and no `AVKIT_API_TOKEN`. It is a docs file with no runtime reader, so the move changes no behaviour. Row 4 still lists the file and keeps it unchanged.
- Row 3 is `[x]`.

## Green, renderer half (row 4)

`-Check green71` exited 0 with `PASS green71` (receipt `C:/Temp/av-kit/s31b-run-green71.txt`).

- **Checks passed:**
  - `PASS mcp-build`.
  - mcp-server Vitest: 12 of 12.
  - ui Vitest: 56 of 56 on `$ui71`, including the eight AC-71.13 card tests and AC-71.14.
  - `PASS ui-build`.
  - Electron `-g AC-71`: 2 passed, 0 skipped (`s31b-green71-e2e.json`).
- **`SettingsPage.tsx`:**
  - `CARD_LAYOUT`: the chip, the Client and Scope `GridSelect`s, the read-only viewer, **Copy prompt**, and the `role="status"` line.
  - `ADVANCED_DISCLOSURE`: a closed `<details>` around the unchanged `copy-mcp-btn` and `pin-mcp-btn`.
  - `SCOPE_DISABLED`: the optional `GridSelect` `disabled` prop. A user-only client forces scope to `user`.
  - `COPY_PROMPT` and `PROMPT_UNAVAILABLE`.
- **Renderer client list.** The renderer keeps its own `CLIENT_SET` copy (`MCP_CLIENT_OPTIONS`), because importing `src/main/mcp-setup-prompt.ts` would pull `node:path` into the renderer bundle. AC-71.13 pins the renderer list and AC-71.1 pins the main list, both against `CLIENT_SET`.
- **Prompt fetch.** Each fetch clears the viewer first, so a failed fetch never leaves another client's text for Copy, and Copy stays disabled while the viewer is empty. A response that arrives after the pair has changed is dropped.
- `EXAMPLE_CONFIG` was already written in row 3; this row leaves it unchanged.
- Row 4 is `[x]`.

## MEU-71 gate (row 5)

### Run 1: failed at `gate71-repeat` (stop S8, D-94 open)

`-Check gate71` exited 1 (receipts copied to `C:/Temp/av-kit/s31b-run-gate71-run1.txt` and `s31b-gate71-repeat-run1.txt`, because a re-run overwrites them).

- **Steps that passed:** `PASS ui-types`, `PASS ui-lint`, `PASS mcp-types`, `PASS mcp-build`, `PASS gate71-mcp-vitest: 438 passed of 438`, `PASS gate71-ui-vitest: 157 passed of 157`, `PASS ui-build`, `PASS gate71-e2e: expected 15 skipped 0`.
- **The failure:** `FAIL: gate71-repeat unexpected/flaky specs (flaky counts as a failure): ['mcp-setup-prompt.test.ts: AC-71.15 Codex prompt carries execPath and app data, Copy prompt fills the clipboard, Claude Desktop disables scope']`. 19 of 20 passed; repeat 3 of the first AC-71.15 test failed at `mcp-setup-prompt.test.ts:113`: after the status showed `Copied the Codex setup prompt.`, `clipboard.readText()` still returned `s31b-clipboard-sentinel`.
- **Cause (not a product defect).** The test writes the sentinel to the system clipboard immediately before clicking Copy prompt. Windows clipboard listeners open the clipboard right after every write (`EnableClipboardHistory` is `1` on this machine), and Chromium's clipboard write gives up silently when it cannot take the clipboard lock within a few short retries. The Copy write landed while the listener still held the lock for the sentinel write, so it was dropped. The repo already records this race at `ui/tests/e2e/capture-filmstrip-actions.test.ts:188` ("Clipboard listeners (Windows clipboard history, screenshot tools) open the clipboard right after every write"). The second AC-71.15 test has the same sentinel-then-click shape (`:137`) and passed all 10 repeats.
- Row 5 stays `[ ]` (S8). The fix is the open decision D-94.

### D-94 ruling and the test change

Mat, 2026-10-17, verbatim: `A`.

- **D-94 A:** in both AC-71.15 tests the click and the clipboard read run inside `expect(async () => { … }).toPass({ timeout: 10_000 })`, so a copy dropped on the clipboard lock is clicked again. The assertions are unchanged: test 1 still requires the clipboard to equal the viewer text and then the `Copied the Codex setup prompt.` status; test 2 still requires a read that is not the sentinel and a non-empty `AVKIT_API_TOKEN`. Test 2's retry also treats an empty read as a lost race, as the filmstrip precedent does, so `JSON.parse` never sees an empty string.
- gate71 is re-run from the start.

### Run 2: passed

`-Check gate71` exited 0 with `PASS gate71` (receipt `C:/Temp/av-kit/s31b-run-gate71.txt`).

- **Steps:** `PASS ui-types`, `PASS ui-lint`, `PASS mcp-types`, `PASS mcp-build`, `PASS gate71-mcp-vitest: 438 passed of 438`, `PASS gate71-ui-vitest: 157 passed of 157`, `PASS ui-build`, `PASS gate71-e2e: expected 15 skipped 0`, `PASS gate71-repeat: expected 20 skipped 0`.
- **Tested state:** HEAD `6097cf59adc7835fa6062c8bd3d55c679aef4543` plus 52 uncommitted product paths (`git diff --name-only HEAD` and untracked, excluding the plan folder and handoffs). The per-file `sha256sum` manifest is `C:/Temp/av-kit/s31b-gate71-run2-manifest.txt`, and its sha256 is `8d59648a24fb71ca1d01a74a1543e17c07065a32641da933b309ad8a5b401077`. The D-94 test edit (13:54:22) predates the run (the first Vitest step started at 13:55:04).
- **Self-review before the handoff:** the handoff's Red rows match §Red (row 2); every AC row names its test file and lines; the evidence records keep the scratch root in `command` only; the Decision Log carries D-89 to D-96, with D-95 (EXAMPLE_CONFIG written in row 3) and D-96 (the renderer's own CLIENT_SET copy) logged as autonomous two-way calls.
- Handoff: `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-MEU-71-handoff.md`. Row 5 is `[x]`.

## Red (row 6)

`-Check red92` exited 0 with `PASS red92` (receipt `C:/Temp/av-kit/s31b-run-red92.txt`). It deleted `mcp-server/bundle` first.

- **mcp-server Vitest** (`s31b-red92-mcp-vitest.json`): 2 files, 5 failed.
  - `bundle-licenses.test.ts` fails to load: `Cannot find module '../scripts/bundle-licenses.js'` (the declared new-module file).
  - `bundle.test.ts`, AC-92.1: `npm --prefix mcp-server run bundle: expected false to be true` (the existence assertion, not a load error).
  - `bundle.test.ts`, AC-92.3 (4 tests, one per pin): the yml does not match the `../mcp-server/bundle` → `mcp-server` pair; `dist:prep` is `npm run clean:out && npm run build && npm run build:picker`; `.gitignore` lacks `mcp-server/bundle/`; `scripts.bundle` is `undefined`.
- **`vitest-red`:** `PASS MEU-92 Vitest RED: 5 assertion failures, 0 missing-symbol, load-tolerated files ['bundle-licenses.test.ts'], TA pins failing []`. Nothing fell under S4.
- **Test shape.** `bundle.test.ts` uses node builtins and Vitest only; its spawn helper settles on the reply, an exit or a 15 s deadline and never rejects. The AC-92.1 copy goes under the OS temp directory, and the child runs with that directory as `cwd` and without `NODE_PATH`, so nothing resolves from the repository. `bundle-licenses.test.ts` builds its fixture packages in a temp directory at run time (a committed `node_modules` fixture would be gitignored), and its real-build case runs esbuild with the exported `BUNDLE_OPTIONS` (`write: false`) and checks `LICENSES.txt` against package names it derives from the metafile itself.
- AC-92.4 is runtime-only and is proved in row 8. Row 6 is `[x]`.

## Green (row 7)

- **esbuild pin:** `npm --prefix mcp-server install --save-dev --save-exact esbuild@0.28.2` exited 0 (`s31b-green92-npm-install.txt`). esbuild 0.28.2 was already in the lockfile through `tsx`, so the change is the `"esbuild": "0.28.2"` devDependency line and two lockfile lines.
- **`BUNDLE_SCRIPT`:** `mcp-server/scripts/bundle.ts` exports `BUNDLE_OPTIONS` (the plan's options, `as const satisfies BuildOptions`) and `bundle()`, which builds with `absWorkingDir` set to `mcp-server/` and writes `bundle/LICENSES.txt`; the script runs `bundle()` only as the main module (`isMainModule` from `src/entry-guard.ts`), so the AC-92.2 real-build case can import the options. `package.json` gains `"bundle": "tsx scripts/bundle.ts"`.
- **`BUNDLE_LICENSES`:** `mcp-server/scripts/bundle-licenses.ts` `collectLicenses(metafile, root)` keys each input on its last `node_modules/<name>/` segment (scoped names included), reads that package's `package.json` and its first `LICENSE*` / `LICENCE*` / `COPYING*` file, throws `no licence file for <name>` when there is none, and sorts by name. `renderLicenses` writes a `<name>@<version> (<licence>)` heading per package.
- **`PACKAGING_INPUTS`:** `ui/electron-builder.yml` `from: ../mcp-server/bundle` (`to: mcp-server` unchanged); `ui/package.json` `dist:prep` ends with `&& npm --prefix ../mcp-server run bundle`; `.gitignore` gains `mcp-server/bundle/` after `mcp-server/dist/`.
- **The real bundle:** `index.mjs` (793,592 bytes) and `LICENSES.txt` naming 8 packages: `@modelcontextprotocol/sdk@1.30.0`, `ajv@8.20.0`, `ajv-formats@3.0.1`, `fast-deep-equal@3.1.3`, `fast-uri@3.1.5`, `json-schema-traverse@1.0.0`, `zod@3.25.76`, `zod-to-json-schema@3.25.2`. Every package had a licence file, so S6 did not trigger.
- **Run 1 (setup defect, fixed):** `-Check green92` exited 1 (receipts kept as `s31b-run-green92-run1.txt` and `s31b-green92-mcp-vitest-run1.json`). Every AC-92.1 assertion passed; the `finally` block's `rmSync` then failed with `EPERM` because the killed child still held the temp directory as its working directory. The helper now settles only after the child has exited. No assertion changed (AGENTS.md:57, setup repair).
- **Run 2:** `-Check green92` exited 0: `PASS mcp-types`, `PASS mcp-bundle`, `PASS green92-mcp-vitest: 8 passed of 8`, `PASS green92` (`s31b-run-green92.txt`).
- Row 7 is `[x]`.

## Packaged probe (row 8)

### Run 1: the build passed, the probe harness could not launch the exe (D-97)

`-Check pkg-probe` exited 1 (receipt kept as `C:/Temp/av-kit/s31b-run-pkg-probe-run1.txt`).

- `PASS packaging pins`, `PASS pkg-dist-prep` (ui build, the region-picker `dotnet publish`, the bundle), `PASS pkg-builder` (`electron-builder --win dir --x64`, Electron 42.9.3).
- Both `mcp-probe` stages raised `FileNotFoundError: [WinError 2]` at `subprocess.Popen`, so no report was written and `pkg-result` failed with `report missing`.
- **Cause (the harness, not the product).** `mcp_probe` passed the relative program path `ui/dist/win-unpacked/av-kit.exe` to `Popen`. `Path.exists()` accepts it, but Windows `CreateProcess` does not find a relative program path written with `/`. A direct check: the relative path raised the same `FileNotFoundError`, and the resolved absolute path ran `av-kit.exe -e "console.log(process.versions.node)"` with `ELECTRON_RUN_AS_NODE=1` (exit 0, `24.18.1`).
- **D-97 (autonomous, two-way):** `mcp_probe` now launches `str(Path(argv[0]).resolve())`. The existence check, the `initialize` request, the 10 s deadline and `probe_passed` are unchanged. `plan_checks.py selftest` still passes. pkg-probe re-runs from the start.

### Run 2: passed

`-Check pkg-probe` exited 0 with `PASS pkg-probe` (receipt `C:/Temp/av-kit/s31b-run-pkg-probe.txt`; result `pkg-probe-result.json`, schema `s31b-pkg-probe.v2`).

- `PASS packaging pins`, `PASS pkg-dist-prep`, `PASS pkg-builder`.
- **In place:** `PASS MCP_ENTRY_PROBE started in 0.17 s`; `first_stdout` carries `"serverInfo":{"name":"av-kit","version":"0.1.0"}`.
- **Hermetic copy** (`C:/Temp/av-kit/s31b-pkg-probe/mcp-server/index.mjs`, no `node_modules` above it): `PASS MCP_ENTRY_PROBE started in 0.11 s`, the same `serverInfo`.
- `PASS PKG_PROBE: bundle and LICENSES.txt byte-equal in win-unpacked (2ee9a90bc366), both probes started; proof bound to 10 files`. The recorded `exit_code` 1 for each probe is the probe's own `kill()` after the reply.
- **Not provisioned, and not needed for AC-92.4:** this worktree has no `packaging/dist/avkit-backend` or `packaging/ffmpeg-win64` (gitignored build outputs; see Session 34 A-7). electron-builder logged `file source doesn't exist` for both and built the tree without them. The probe reads only `av-kit.exe` and `resources/mcp-server/`, so the missing backend and FFmpeg folders do not affect it. No tracked file changed for this.
- Row 8 is `[x]`.

## MEU-92 gate (row 9)

`-Check gate92` exited 0 with `PASS gate92` (receipt `C:/Temp/av-kit/s31b-run-gate92.txt`).

- **Steps:** `PASS mcp-types`, `PASS mcp-build`, `PASS mcp-bundle`, `PASS gate92-mcp-vitest: 446 passed of 446` (gate71's 438 plus the 8 MEU-92 tests), `PASS gate92-ui-vitest: 56 passed of 56` (the MEU-71 set, re-run because `SERVER_ENTRY` names `index.mjs`), `PASS PKG_EVIDENCE: ... passed and all 10 bound files are unchanged`.
- **Tested state:** HEAD `6097cf59adc7835fa6062c8bd3d55c679aef4543` plus 61 uncommitted product paths (`git diff --name-only HEAD` and untracked, excluding the plan folder and handoffs). The per-file `sha256sum` manifest is `C:/Temp/av-kit/s31b-gate92-manifest.txt`, and its sha256 is `1ee1a6d1012cf5f521bfb0596eb8bfc37cc0e479d5356a6ca182f0e220bd6e03`.
- **Self-review before the handoff:** the Red rows match §Red (row 6); each AC row names its test file; the evidence records keep the scratch root in `command` only; the cross-ref rows cover AC-23, AC-41 and AC-71; D-97 (the probe launch path) and D-98 (the AC-92.2 real-build metafile) are logged as autonomous two-way calls.
- Handoff: `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-MEU-92-handoff.md`. Row 9 is `[x]`.
- **`handoff-ac` dry run:** the first run refused the MEU-71 Decision Log item D-89, whose `chosen` text quoted `git show <sha>:<path>` and so matched the validator's `<[a-z-]+>` placeholder pattern. It now reads "git show of that commit and path" (wording only), and both handoffs pass.

## Hub reconciliation (row 10)

`-Check hub` exited 0: `PASS hub reconciliation`, `PASS hub-vitest: 22 passed of 22` (gui-actions-audit, layout-canon, queue-canon), `PASS hub` (receipt `C:/Temp/av-kit/s31b-run-hub.txt`). All four files keep CRLF.

- `07-distribution.md` §MCP on a shipped machine: `Ship resources/mcp-server/` (the bundle's `index.mjs` and `LICENSES.txt`), linking §MCP server bundle and §MCP setup prompt. The old `resources/extra/mcp-server/` path is gone.
- `06-gui.md`: the preload listing gains `getMcpSetupPrompt` (invokes `get-mcp-setup-prompt`, returns `{ text }`) and a path-rules bullet saying main never reads `mcp-token.txt` for it. The Settings MCP card row names the client and scope selectors, the read-only prompt, **Copy prompt**, and the Advanced disclosure around **Copy MCP config** and **Pin current endpoint**.
- `05-mcp-server.md` Phase 7 row: ships the self-contained bundle as `resources/mcp-server`, registered per client by the setup prompt (app executable, `ELECTRON_RUN_AS_NODE=1`, `AVKIT_APP_DATA`, no token). It replaces the old "document `AVKIT_API_TOKEN` for IDE config" text, which the token boundary contradicts.
- `build-priority-matrix.md`: rows 7.3 (MEU-71) and 7.5 (MEU-92), in matrix order around 7.4, each linking its 07 residual anchor with its `depends_on` from `meu-status.yaml`.
- Row 10 is `[x]`.

## Gate (H1-2)

`-Check gate` exited 0 with `PASS gate` (receipt `C:/Temp/av-kit/s31b-run-gate.txt`; result `gate-result.json`, schema `s31b-gate.v1`, `passed: true`). It ran 2026-10-17 14:09:47 to 14:14:32 (-04:00) on Node v24.19.0 and Electron 42.9.3.

- **Stages, in order, all exit 0:** `gate-npm-ci`, `gate-ui-types`, `gate-ui-lint`, `gate-mcp-types`, `gate-mcp-build`, `gate-mcp-bundle`, `gate-pkg-current` (`PKG_EVIDENCE` after the fresh bundle), `gate-ui-build`, `gate-ui-harness-build`, `gate-picker-stub`, `gate-mcp-tests`, `gate-ui-tests`, `gate-ui-electron`, `gate-state-render`, `gate-task-contract`, `gate-source-audit` (rg exit 1, no hits), `gate-floors`.
- **Counts:** ui Vitest 1006 of 1006; mcp-server Vitest 446 of 446; Electron 159 expected, 0 unexpected, 0 skipped, 0 flaky.
- **`COUNT_FLOORS`:** `PASS COUNT_FLOORS: ui vitest 1006 (baseline 975, +31), mcp vitest 446 (baseline 428, +18), e2e 159 (baseline 157, +2), packaged proof current`.
- **Input identity:** `tested_commit` `6097cf59adc7835fa6062c8bd3d55c679aef4543` plus the 61 uncommitted `ui/`, `mcp-server/` and `docs/` paths whose working-tree sha256 values `gate-result.json` records, and both lockfile hashes.
- **Skipped stages (scope basis, recorded in `gate-result.json`):** py-types, py-lint, py-tests and openapi (no change under `packages/`, `openapi.committed.json`, `pyproject.toml` or `uv.lock`); mcp-audit (no MCP tool, schema or annotation change; AC-71.12 covers the server instructions).
- **Before the run:** no process from this worktree held `node_modules` (a path-scoped process listing showed only the listing's own shells).

## MCP_PROMPT_LOOK (H1-2)

The dev app was launched detached for Mat at 2026-10-17 14:15 (`Start-Process pwsh`, `npm run dev` in `ui/`, ELECTRON_RUN_AS_NODE removed; log `C:/Temp/av-kit/s31b-look-dev.txt`). Mat's answers for L1 to L5 are recorded here verbatim when they arrive.

Mat (chat, 2026-10-17), verbatim: "All looks good. I run test on Claude Desktop, see bellow output from the chat with Sonnet 5.5 Medium", followed by the pasted transcript of the Claude Desktop agent applying the prompt.

| Item | Result | Basis |
|---|---|---|
| L1 card layout, Advanced closed | pass | "All looks good" |
| L2 scope disabled for user-only clients | pass | "All looks good" |
| L3 apply the prompt in a client | pass, run on **Claude Desktop** instead of the plan's Claude Code (user scope) | Pasted transcript: the agent backed up `claude_desktop_config.json` to `claude_desktop_config.json.avkit-backup-20261017T181903Z`, merged `avkit` under `mcpServers` keeping the four other servers, confirmed both the `electron.exe` and `index.js` paths exist, asked for a restart, then `avkit_health` `action: "dependencies"` succeeded and the reply ended `RESULT: connected`. It also reported no MSIX install (standard `%APPDATA%` path) and `tts_espeak` not available, which is a dependency state, not a prompt result. |
| L4 readable in both themes, no token | pass | "All looks good" |
| L5 (optional) Codex block | not run | Optional; Mat did not report it |

- **Variance from the plan's L3 wording:** the plan names Claude Code and `/mcp`. Mat exercised the Claude Desktop block, which is the user-only client with the MSIX path note, and the same backup, merge, restart and verify steps ended `RESULT: connected`. The Claude Code block is covered by its golden file and AC-71.1/AC-71.2 but was not applied by hand. This is flagged to the execution reviewer rather than re-asked.
- **Left in place on Mat's machine:** the Claude Desktop `avkit` entry points at this worktree's dev `electron.exe` and `mcp-server/dist/index.js`, so it stops working when the worktree is removed; the backup file restores the previous config. Claude did not open the config file.
- H1-2 is `[x]`.

## Execution review round 1 (H1-7)

Dispatch (2026-10-17): two attempts exited 1 before Codex started, both refused by `tools/Invoke-CodexDispatch.ps1`'s path checks, which accept only `P:/av-kit` as the repository root (`WorkingDirectory must be under the repository root.`, then `PromptFile does not exist.` for the relative worktree path). Neither recorded a ledger round (receipts `C:/Temp/av-kit/s31b-exec-dispatch-r1-attempt1-workdir.txt`, `-attempt2-promptpath.txt`). Following Session 35, the prompt now says the work exists only in the worktree, the dispatcher starts in `P:/av-kit`, and the prompt file is copied to `C:/Temp/av-kit/dispatch/s31b-exec-r1-prompt.txt`.

Round 1: Codex `gpt-6.1-sol`, `changes_required`, `intent_achieved: partial`, 2 findings, 11,498,809 tokens (receipt `C:/Temp/av-kit/s31b-exec-dispatch-r1.txt`; report copied verbatim to `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-implementation-critical-review.md`). The ledger refuses round 2 on tokens: 11.5M spent plus an 11.5M reserve exceeds the 21M budget, so round 2 needs Mat's `continue`.

- **F1 (High, blocking, AC-71):** the Claude Desktop block chose the MSIX file in step 1 but named the standard `%APPDATA%` file in step 2, so an MSIX install could be changed without a backup. Fixed: step 1 now settles on one file (the MSIX path when a `%LOCALAPPDATA%\Packages\Claude_*` folder exists, otherwise the standard path; "Use that one file in every step below."), and the Claude Desktop backup step names "the file chosen in step 1" through a new optional `Block.backup` text. Every other client's output is byte-identical (the other 10 of the 11 goldens unchanged; round 2 corrected the count from 12). Red: new test `AC-71.4 negative: Claude Desktop backs up the one file step 1 chose, MSIX included (review F1)` failed 1 of 13 on its first assertion (`s31b-f1-red.txt`); Green 13 of 13 after the fix and the `claude-desktop-user.txt` golden update (`s31b-f1-green.txt`). The hub line (07 `:284`, "with the MSIX-virtualized config path note") still holds.
- **F2 (Low, non-blocking):** `plan_checks.py static` reported D-94 and D-97 as undefined because it read decision ids only from the plan. It now also reads the `  - id: D-n` records of the two work handoffs; an id defined nowhere still fails. Red `s31b-f2-red.txt` (exit 1, those two lines), Green `s31b-f2-green.txt` (`PASS static`), selftest `s31b-f2-selftest.txt` (`PASS selftest`).
- **Closeout validator repair (not a finding):** two plan decision records carried text the closeout placeholder pattern matches (D-79's `$` brace example path and D-89's angle-bracket `git show` form). Both are reworded with the meaning unchanged; D-89 now matches the MEU-71 handoff's wording.
- **Gate after the fixes:** `-Check gate` exit 0 (`s31b-run-gate.txt`; the H1-2 receipt is kept as `s31b-run-gate-h1-2.txt`, which embeds that run's full result JSON; a separate `s31b-gate-result-h1-2.json` copy was never written, as round 2 noted): ui Vitest 1007 of 1007 (+1, the F1 test), mcp-server 446 of 446, Electron 159 expected and 0 unexpected, `COUNT_FLOORS` pass, `PKG_EVIDENCE` current (no bound file changed). This `gate-result.json` replaces the H1-2 one as the gate of record.
- **D-99 (token budget for round 2):** Mat, verbatim, 2026-10-17: "B: approved for 50M", then on D-99a (total versus added): "A" (a total budget of 50M, so 29M added). Neither reply reaches the ledger's 20-character `--said` floor (`MIN_RATIONALE`), and Claude does not compose words for it, so `continue` waits for Mat's own sentence.
  Mat, verbatim, 2026-10-17: "Approved: raise the execution review budget to 50M total." Recorded with `tools/review_ledger.py continue --tokens 29000000 --by Mat` and that sentence as `--said`; the ledger grant reads round 2, owner Mat, granted `2026-10-17T14:59:40-04:00`, tokens 29,000,000, lifted `tokens`.

## Execution review round 2 (H1-7)

Dispatch `s31b-exec-r2` (prompt `review-prompt-execution-r2.md`, copied to `C:/Temp/av-kit/dispatch/s31b-exec-r2-prompt.txt`), receipt `C:/Temp/av-kit/s31b-exec-dispatch-r2.txt`, wrapper exit 0. The dispatcher recorded `round 2 verdict=approved agent='gpt-6.1-sol' blocking=0 intent_achieved=yes usage=3,825,102`; every checklist row is `pass`. The report is appended verbatim to the canonical review file as "## Round 2 Recheck — 2026-10-17", and its frontmatter replaces the file's (round 2, `approved`, 0 findings).

- **F1 and F2:** fixed. No new finding.
- **Two record corrections the reviewer noted (no finding raised):** there are 11 client/scope goldens, so the F1 fix left 10 others unchanged, not 12; and the separate `s31b-gate-result-h1-2.json` copy was never written (the H1-2 receipt embeds that run's result JSON). Both lines in §Execution review round 1 are corrected. The round-2 prompt keeps its original wording, as sent.
- **Ledger totals:** 2 of 6 rounds, 15,323,911 tokens of the 50M budget.
- `-Check review-check -Mode execution -Cap 6`: exit 0, `PASS execution review approved, round 2, agent gpt-6.1-sol` (receipt `C:/Temp/av-kit/s31b-run-exec-review.txt`).
- H1-7 is `[x]`.

## Closeout (H2)

- **H2-1:** reflection `docs/execution/reflections/2026-10-16-gui-mcp-setup-prompt-reflection.md`, validated with every decision source (38 of 38 decisions reconciled).
- **H2-2:** MEU-71 and MEU-92 `approved`; grouping 31b `approved`; `MCP-SETUP-PROMPT` and `MCP-PACKAGED-ENTRY-UNREACHABLE` resolved; metrics row; `PASS POST_REVIEW_STATE`.
- **H2-3:** `static`, `handoff-ac` and `scope` pass. D-99 was added to the MEU-71 handoff Decision Log, because `task.md` cites it.
- **Commit drafts (Mat commits; nothing is committed or pushed).** Commit 1 is A-1 only (D-92), so Session 35 can take it from `main` on its own:
  - Commit 1 paths: `_inspiration/zorivest/`, `ui/tests/unit/queue-canon.test.ts`, `docs/build-plan/10-queue-card-ui.md`, `.agent/docs/cloud-local-collaboration.md`. Three files mix A-1 and MEU-71/92 hunks (`docs/BUILD_PLAN.md` golden rule 4, `docs/build-plan/gui-actions-index.md:3`, and the `QUEUE-PILL-TOKEN-DRIFT` entry in `known-issues.yaml`/`.md`); a path-level split puts them in commit 2, and a hunk-level split needs staged patches.
  - Commit 1 message: `chore(canon): decouple av-kit from the live Zorivest checkout (Session 31b A-1)`, body: "AC-41.3 reads av-kit's committed copy of Zorivest globals.css at 61243baf (_inspiration/zorivest/, PROVENANCE.md) instead of P:/zorivest's working tree, and the queue-card canon names av-kit as the owner of its pill palette. Resolves QUEUE-PILL-TOKEN-DRIFT. Decisions D-89 to D-92."
  - Commit 2 message: `feat(mcp): per-client MCP setup prompt and bundled packaged MCP server (MEU-71, MEU-92)`, body: "The Settings MCP card shows and copies a per-client setup prompt built in main with no token input; the mcp-server entry guard compares real paths. The packaged app ships a self-contained esbuild bundle as resources/mcp-server, proved by MCP_ENTRY_PROBE on a built win-unpacked tree. Resolves MCP-SETUP-PROMPT and MCP-PACKAGED-ENTRY-UNREACHABLE. Plan review approved round 3, execution review approved round 2 (Codex gpt-6.1-sol)."
  - Neither message carries an AI attribution trailer.
