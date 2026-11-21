---
date: "2026-11-21"
project: "2026-11-20-help-quick-start"
meu: "MEU-162"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-20-help-quick-start/implementation-plan.md"
build_plan_section: "docs/build-plan/06-gui.md §Help quick start (residual) (MEU-162, matrix 6.23)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-20-e2e-clipboard-specs-handoff.md"
---

# Handoff: 2026-11-20-help-quick-start-MEU-162-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-162 Help quick start (phase 6, matrix 6.23), registered in row 1 with the dependencies MEU-23 (the page help cards) and MEU-158 (F1 help).
**Build Plan Section**: `docs/build-plan/06-gui.md` §Help quick start (residual).
**Predecessor**: [2026-11-20-e2e-clipboard-specs-handoff.md](2026-11-20-e2e-clipboard-specs-handoff.md), Session 98, committed as `e8207e1`. Session 99 ran from `f1ba411` (`baseline.sha`). Session 100 (`e2e-devpc-clipboard`) ran beside it on the same tree and committed `49ab790` with none of this plan's own paths; rows 8 to 10 and the gate ran on `49ab790` (Departures).

- **The quick start (`QUICK_START_DATA`, `QUICK_START_SCHEMA`, D-1291).** `ui/src/renderer/src/components/help/quick-start.json` holds, for each of the six pages, one intro sentence, 4 or 5 numbered steps (each with the `data-testid` of the control it names, or `null`) and one screenshot (two on Settings) with its alt text. `quick-start.ts` types it and exports `validateQuickStart`, `quickStartHash` and `quickStartHashInput`.
- **The card (`CARD_QUICK_START`, D-1289, D-1290).** `HelpCard.tsx` keeps its props, storage key, closed first visit and F1 handling. Its header adds `Quick start · N steps` (`:187-189`). Open, it shows the search, then, while the search is empty, the intro, the `<ol>` of steps and the figures (`QuickStart`, `:82-100`), and the heading "More about this page" (`:211`). Each topic is a closed `<details data-help-section>` with its title in `<summary>`, opened while a search matches (`:215-218`).
- **The screenshots (`HELP_SHOTS`, `THEME_SHOT_CSS`, `HELP_SHOTS_GEN`, `DEMO_STAGE`, `PRIVACY_GUARD`, D-1292, D-1294).** 14 WebP files and `manifest.json` in `ui/src/renderer/src/assets/help/`. `help-shots.ts` maps a name and theme to its URL and size through `import.meta.glob`. Two CSS rules show the light or the dark image with the theme. `npm --prefix ui run help:shots` takes them from the real Electron app with demo data (`ui/tests/help-shots/`), bakes the numbered badges in, and refuses any image whose clip shows a home folder or a scratch root.
- **Plain topics (`PLAIN_TOPICS`, `CONSOLE_AND_SAVE`, D-1290 A).** 31 unpinned topics in the six `*-help-content.ts` modules are rewritten in plain words, ids and order kept, each with its §Fact table keywords; the Settings Console topic and the one `four-tools` Save sentence change as D-1290 A says.
- **The STE gate (`STE_GATE`, D-1293).** The ASD-STE100 skill is vendored byte for byte in `.agent/skills/asd-ste100/` with `UPSTREAM.md` (MIT). `tools/help_guide_ste.py` lints the steps in Strict mode and the intros, alt texts and unpinned topics for `advisory-free` findings; `tests/tooling/test_help_guide_ste.py` runs it.
- **Records.** MEU-162 is `ready_for_review` with this plan folder; 06 carries the `Delivered (Session 99)` note; `commands.md` names `help:shots` and when to run it.

**What Mat sees.** Each page's How it works card header now reads "How it works  Quick start · 5 steps" (4 on Transcript, Capture and Settings). Opening it shows one sentence about the page, four or five short numbered steps, and a picture of the page with the same numbers on the controls the steps name, in the light or dark theme. Below that, "More about this page" lists the old topics as one-line titles, rewritten without API words, that open on a click. Typing in the help search hides the quick start and shows only the matching topics, opened. The card still starts closed on a first visit, and F1 works as before.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-20-help-quick-start/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-20 ("1289 A, 1290 A, execute"), `plan_to_exec_gate: human`; the plan review approved at round 3 (`.agent/context/handoffs/2026-11-20-help-quick-start-plan-critical-review.md`). Receipts named by file name alone are in the session's receipts folder (the `help-quick-start` folder under `RECEIPTS_DIR`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-162.1 | unit | `validateQuickStart(QUICK_START)` returns `[]`; six pages, 4 or 5 steps, 1 or 2 shots, every target rendered on its page; each bad fixture gives one named problem | Human-approved (Mat 2026-11-20); D-1291 | `ui/tests/unit/help-quick-start.test.tsx:424`, `:440` | ✅ |
| AC-162.2 | unit (pytest) | `tools/help_guide_ste.py` exits 0 on the repository: steps Strict, intros, alts and unpinned topics 0 `advisory-free`; its selftest fixtures fail | Human-approved (Mat 2026-11-20, the asd-ste100 skill); D-1293 | `tests/tooling/test_help_guide_ste.py:96` (4 cases) | ✅ |
| AC-162.3 | unit | The closed header holds `Quick start · 5 steps`; the open card shows the intro and five steps in order before the first topic | Human-approved; D-1289, D-1291 | `ui/tests/unit/help-quick-start.test.tsx:471` | ✅ |
| AC-162.4 | unit | `css`: the two `THEME_SHOT_CSS` rules once each; `figures`: one figure per shot with a light and a dark lazy image, the alt and the manifest size; two on Settings | D-1292 | `ui/tests/unit/help-quick-start.test.tsx:501`, `:513` | ✅ |
| AC-162.5 | unit | `cookie` hides the quick start and keeps only the open `cookies` topic; clearing brings it back with every topic closed; `zzzz` shows the no-match text | Local Canon (06 §Help (per page): search); D-1290 | `ui/tests/unit/help-quick-start.test.tsx:550`; guard `:576` | ✅ (`no match` passed at Red, guard) |
| AC-162.6 | unit | With the search empty every topic is a closed `<details>` that opens on a click | D-1290 | `ui/tests/unit/help-quick-start.test.tsx:587` | ✅ |
| AC-162.7 | unit | The manifest has one entry per shot, `stepsHash` equals the data, both WebP files exist at 153,600 bytes or fewer with the manifest size | D-1292, D-1294 | `ui/tests/unit/help-quick-start.test.tsx:606` | ✅ |
| AC-162.8 | unit | `privacy`: `findPrivatePath` flags home folders and the roots, never a neutral path; `clip`: `shotClip` gives the union plus 24 px or a named error; `text`: `clipText` keeps only unmasked text inside the clip | D-1292 | `ui/tests/unit/help-shots-privacy.test.ts:68`, `:76`, `:119` | ✅ |
| AC-162.9 | unit | Topic ids and order kept; pinned text kept; every unpinned body holds its §Fact table keywords and no jargon | Human-approved (Mat 2026-11-20); D-1290 | `ui/tests/unit/help-quick-start.test.tsx:659` | ✅ |
| AC-162.10 | integration | Electron, fresh app data: every card closed on the first visit; every header reads `Quick start · N steps` | D-1289 | `ui/tests/e2e/help-quick-start.test.ts:93` (closed), `:103` (hint) | ✅ (`closed` passed at Red, guard) |
| AC-162.11 | integration | Electron, per page after its stage: the steps equal the JSON, every target visible, each image loads in its theme and hides in the other | Human-approved; D-1292, D-1294 | `ui/tests/e2e/help-quick-start.test.ts:118` (six tests) | ✅ |
| AC-162.12 | integration | Electron, Downloader: `SABR` hides the quick start and every figure and leaves one topic | Local Canon (W6-2 search) | `ui/tests/e2e/help-quick-start.test.ts:153` | ✅ |
| AC-162.13 | check | The §Test pins pass unchanged with their row-0 hashes (after D-1296) in the gate's `ui-tests` and row 9's E2E runs | Local Canon | gate `pins-unchanged`, `ui-tests`, `e2e-help-search`, `e2e-help-f1-mount`, `e2e-keyboard-shortcuts`; row 9 | ✅ |
| AC-162.14 | check | Row 8: `help:shots` exits 0, writes 14 WebP files and the manifest, one `isolation: ok` per launch and one `privacy: clean` per file; a second run gives the same manifest; the planted home path exits 1 with `privacy: blocked settings-download-light` and writes nothing | Mat 2026-11-16; D-1292, D-1295 | row 8 `hq-row8-d1295.txt`, `hq-row8-shots-check.txt`, `hq-row8-neg.txt`, `hq-row8-neg-check.txt`; D-1295 theme negative `hq-d1295-neg.txt` | ✅ |
| AC-162.15 | check | Row 2: the vendored skill files equal the creative-writing copy; `LICENSE` is MIT; `UPSTREAM.md` names the URL, commit and licence | D-1293 | row 2 `hq-row2-skill.txt`; gate `skill-identity` | ✅ |
| AC-162.16 | check | Row 9: `help-quick-start.test.ts` passes 3 runs of 3, with no `flaky` and no `unhandled rejection:` line | Mat 2026-11-16 | row 9 `hq-row9-hq.txt`, `hq-row9-runs.txt` | ✅ 27 of 27 |
| AC-115.15 (cross-ref) | guard | MEU-115's test that the Settings Console help says errors always go to the file. D-1290 A changed its one body assertion in row 4 (`ui/tests/unit/failure-reason-copy.test.ts`); it failed at Red by assertion and passes on the new Console body. Not a criterion of this plan | Human-approved (D-1290 A, M-7) | row 4 `hq-row4-console.txt`; gate `help-unit`, `ui-tests` | ✅ |
| AC-23.16, AC-51.6, AC-81.12 and AC-104.20 (cross-ref) | guard | §Test pins the plan keeps unchanged: the per-module topic keywords (`help-card.test.ts`, AC-23.16), the test-id registry prefix (`layout-primitives.test.ts:200`, AC-51.6; the five new ids are at the end of `test-ids.ts`), `four-tools` holding `HELP_EDIT_TEXT` with no `Sample` (`capture-action-row.test.ts:713-719`, AC-81.12) and the Capture copy sentence (`capture-copy-image.behavior.test.ts:815`, AC-104.20). The test files are unchanged; not criteria of this plan | Local Canon (plan §Test pins) | gate `pins-unchanged`, `help-unit`, `ui-tests` | ✅ |
| AC-158.3 to AC-158.7 (cross-ref) | guard | MEU-158's F1 hold tests (`help-f1-hold`), which D-1289 A keeps by leaving the card closed on a first visit; unchanged and not criteria of this plan | Human-approved (D-1289 A) | gate `ui-tests`, `e2e-help-f1-mount` | ✅ |
| AC-39.13, AC-33.18 and AC-61.16 (cross-ref) | guard | Older tests in `capture-page.test.ts`, `convert-page.test.ts` and `settings-page.test.ts` that pinned topic words row 6 rewrote; under D-1296 each check names the new words of the same topic. Not criteria of this plan | Human-approved (D-1296, M-7) | row 7 `hq-row7-pins.txt`; gate `help-unit`, `ui-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-162.2 repo | `AssertionError: AC-162.2 repo:` with `quick-start.json missing` and four unpinned-topic findings (`hq-row3-red.txt`, `1 failed, 3 passed in 0.09s`) | Row 6: `4 passed in 0.15s` (`hq-row6-ste.txt`) | `tests/tooling/test_help_guide_ste.py:96` |
| AC-162.1 (both tests) | `AssertionError: components/help/quick-start.ts exports validateQuickStart: expected 'undefined' to be 'function'` (`hq-row4-red.txt`, `Tests  12 failed | 1 passed (13)`) | Row 7: `Tests  2 failed | 11 passed (13)`, only `AC-162.4 figures` and AC-162.7 failing (`hq-row7-green.txt`, `hq-row7-check.txt`) | `ui/tests/unit/help-quick-start.test.tsx:424`, `:440` |
| AC-162.3 | As AC-162.1 (`hq-row4-red.txt`) | Row 7 (`hq-row7-green.txt`) | `ui/tests/unit/help-quick-start.test.tsx:471` |
| AC-162.4 css | `AssertionError: :root.dark .help-shot__img--light { display: none; }: expected +0 to be 1` (`hq-row4-red.txt`) | Row 7 (`hq-row7-green.txt`) | `ui/tests/unit/help-quick-start.test.tsx:501` |
| AC-162.4 figures | As AC-162.1 (`hq-row4-red.txt`); still failing by assertion at row 7, as planned (`hq-row7-check.txt`) | Row 8: `Tests  13 passed (13)` (`hq-row8-d1295.txt`) | `ui/tests/unit/help-quick-start.test.tsx:513` |
| AC-162.5 search | `AssertionError: quick start list before the search: expected null not to be null` (`hq-row4-red.txt`) | Row 7 (`hq-row7-green.txt`) | `ui/tests/unit/help-quick-start.test.tsx:550` |
| AC-162.6 | `AssertionError: leaf-keys element: expected 'ARTICLE' to be 'DETAILS'` (`hq-row4-red.txt`) | Row 7 (`hq-row7-green.txt`) | `ui/tests/unit/help-quick-start.test.tsx:587` |
| AC-162.7 | As AC-162.1 (`hq-row4-red.txt`); still failing by assertion at row 7, as planned (`hq-row7-check.txt`) | Row 8: `Tests  13 passed (13)` (`hq-row8-d1295.txt`) | `ui/tests/unit/help-quick-start.test.tsx:606` |
| AC-162.8 (privacy, clip, text) | `AssertionError: tests/help-shots/privacy.ts exports findPrivatePath: expected 'undefined' to be 'function'` (privacy, text) and `... clip.ts exports shotClip ...` (clip) (`hq-row4-red.txt`) | Row 7 (`hq-row7-green.txt`) | `ui/tests/unit/help-shots-privacy.test.ts:68`, `:76`, `:119` |
| AC-162.9 | `AssertionError: expected [ …(18) ] to deeply equal []` (jargon and missing keywords; `hq-row4-red.txt`) | Row 6: `Tests  1 passed | 9 skipped (10)` (`hq-row6-ac9.txt`) | `ui/tests/unit/help-quick-start.test.tsx:659` |
| AC-162.10 hint | `Error: expect(locator).toHaveText(expected) failed` (`hq-row5-red.txt`, `8 failed`, `1 passed (1.3m)`) | Row 9: `27 passed (2.3m)` over 3 runs (`hq-row9-hq.txt`) | `ui/tests/e2e/help-quick-start.test.ts:103` |
| AC-162.11 (six pages) | `Error: expect(locator).toBeVisible() failed` on the step list (`hq-row5-red.txt`) | Row 9 (`hq-row9-hq.txt`) | `ui/tests/e2e/help-quick-start.test.ts:118` |
| AC-162.12 | `Error: expect(locator).toBeVisible() failed` before the search (`hq-row5-red.txt`) | Row 9 (`hq-row9-hq.txt`) | `ui/tests/e2e/help-quick-start.test.ts:153` |

`AC-162.5 no match` and `AC-162.10 closed` passed at Red and are guards (`hq-row4-red.txt` `1 passed`; `hq-row5-red.txt` `ok 1 ... AC-162.10 closed`). AC-162.13 to AC-162.16 are checks. Every unit Red failed by assertion, never by a missing module (Session 52 RULE-4): the test file imports through `import.meta.glob` and asserts the export first. `red-check` passed each Red: `hq-row3-red-check.txt`, `hq-row4-red-check.txt` (8 required, 0 problems) and `hq-row5-red-check.txt` (0 problems, 24 step targets).

- **Row 0 baseline** (`hq-baseline.txt`): all steps exit 0; `baseline-dirty.txt 54 paths`. UI Vitest at base: `Test Files  1 failed | 146 passed (147)`, `Tests  4 failed | 1640 passed (1644)`, all 4 in Session 100's then-untracked `ui/tests/unit/e2e-clipboard-guard.test.ts` (`hq-base-ui.txt`); tooling `570 passed` (`hq-base-tooling.txt`).
- **Row 1** (`hq-register.txt`, `hq-register-render.txt`, `hq-register-check.txt`): MEU-162 registered at 6.23; the render reports 162 MEUs; the drift check passed.
- **Row 2** (`hq-row2-skill.txt`): `row-check skill: 0 problem(s)`, six files byte-equal to the creative-writing copy.
- **Row 3 Red** (`hq-row3-red.txt`): `1 failed, 3 passed in 0.09s`; the Red findings in unpinned topics were three semicolons (`transcript:cancelled`, `capture:inbox-folder`, `settings:console`) and one synonym rotation (`settings:ffmpeg`).
- **Row 4 Red** (`hq-row4-red.txt`): `Test Files  2 failed (2)`, `Tests  12 failed | 1 passed (13)`; AC-115.15 Red (`hq-row4-console.txt`): `Tests  1 failed | 1 skipped (2)`, `expected 'Set log_level, log_to_file, and conso…' to be 'Set Log level, Log to file and Consol…'`; `red-check: 1 receipt(s), runner any, 1 required test(s), 0 allowed pass(es), 0 step target(s), 0 problem(s)` (`hq-row4-console-check.txt`).
- **Row 5 Red E2E** (`hq-row5-red.txt`, Playwright 1.64.1): `8 failed`, `1 passed (1.3m)`; every stage reached its targets (`isolation: ok` on each launch).
- **Row 6** (`hq-row6-*.txt`): `quick-start.json` equals the plan's draft byte for byte (`cmp`), so row 6 made no change to the draft JSON; 31 unpinned topics rewritten; STE `4 passed in 0.15s`; AC-162.9 `Tests  1 passed | 9 skipped (10)`; the pins `Tests  85 passed (85)` in `Test Files  8 passed (8)` (`hq-row6-pins.txt`).
- **The §Fact table check.** AC-162.9 reads every unpinned body, `settings:console` included, for its §Fact table keywords (case ignored) and the jargon tokens: 1 passed at row 6 (`hq-row6-ac9.txt`), and again in the gate's `help-unit` and `ui-tests`.
- **Row 7 Green** (`hq-row7-green.txt`): `Tests  2 failed | 11 passed (13)`; `only-failing: 2 failing ['AC-162.4 figures: ...', 'AC-162.7 ...']`, `row-check only-failing: 0 problem(s)` (`hq-row7-check.txt`); the pins `Tests  246 passed (246)` in `Test Files  16 passed (16)` (`hq-row7-pins.txt`, settings-page added by D-1296).
- **Row 8 generator** (`hq-row8-d1295.txt`, the rerun after D-1295; the earlier receipts are in the scratch `pre-d1295` folder): `row-check shots: 0 problem(s)`; `shots hq-row8-shots-1.txt: isolation ok 12 (launches 12)` and the same for `hq-row8-shots-2.txt`; 14 `privacy: clean` lines in each run; the negative run `privacy: blocked settings-download-light` (`hq-row8-neg.txt`) and `assets-unchanged: 15 file(s), negative exit 1`, `row-check assets-unchanged: 0 problem(s)`; Vitest `Tests  13 passed (13)`; `row-check red-unchanged: 0 problem(s)`; `row8 exit 0`.
- **Row 9 Electron** (`hq-row9-runs.txt`, rerun after D-1295; the earlier receipts are in `pre-d1295/row9`): `e2e-count hq-row9-hq.txt: 27 AC-162 ok lines, passed [27], want 27`; `hq-row9-search.txt: passed [3]`; `hq-row9-f1.txt: passed [5]`; `hq-row9-keys.txt: passed [2]`; `row-check e2e-count: 0 problem(s)`.
- **Row 10** (`hq-row10-render-check.txt`): `Drift check passed — SSOT loaded (162 MEUs, 12 phases)`.
- **H1-1** (`task-unchecked.txt`): `unchecked implementation rows: []`.

#### Row 8 manifest (`ui/src/renderer/src/assets/help/manifest.json`, sizes from `hq-row8-shots-check.txt` after D-1295)

| File | Theme | Width | Height | Bytes |
|------|-------|-------|--------|-------|
| `downloader-light.webp` | light | 1091 | 330 | 15510 |
| `downloader-dark.webp` | dark | 1091 | 330 | 15760 |
| `transcript-light.webp` | light | 1091 | 217 | 13766 |
| `transcript-dark.webp` | dark | 1091 | 217 | 14674 |
| `tts-light.webp` | light | 1075 | 500 | 25880 |
| `tts-dark.webp` | dark | 1075 | 500 | 26094 |
| `convert-light.webp` | light | 1091 | 386 | 25186 |
| `convert-dark.webp` | dark | 1091 | 386 | 25420 |
| `capture-light.webp` | light | 1091 | 212 | 17280 |
| `capture-dark.webp` | dark | 1091 | 212 | 18050 |
| `settings-download-light.webp` | light | 804 | 102 | 5096 |
| `settings-download-dark.webp` | dark | 804 | 102 | 5076 |
| `settings-setup-light.webp` | light | 804 | 645 | 11402 |
| `settings-setup-dark.webp` | dark | 804 | 645 | 11776 |

#### Row 8 image review (`hq-row8-review.txt`, the D-1295 set; criteria: numbers on the right controls, right theme with the native selects, no text cut, no personal data)

- downloader-light 1091x330: 2 URL field, 3 Add, 4 Start, 5 Open file (step 1 has no target); light; Quality select light; no text cut (badge 2 touches the corner of the "URL" label, still readable); demo URL and "Garden tour" only. PASS
- downloader-dark 1091x330: same marks; dark tokens; Quality select dark (CSS variable); no text cut; no personal data. PASS
- transcript-light 1091x217: 1 Channel URL, 2 Add, 3 Start, 4 Open ZIP; light; no text cut; "Demo channel", path D:\Media\av-kit\transcripts\demo-a only. PASS
- transcript-dark 1091x217: same marks; dark; no select in the clip; no text cut; no personal data. PASS
- tts-light 1075x500: 1 Model list, 2 Get, 3 Text box, 4 voice search, 5 Generate; light; Model, Device and Format selects white; labels Text, Voice, Model, Device shown whole (the model name truncation is the select's own rendering); output path D:\Media\av-kit. PASS
- tts-dark 1075x500: same marks; dark; Model, Device and Format selects dark (F1 was the white Format select); no text cut; no personal data. PASS
- convert-light 1091x386: 1 Compress, 2 drop panel, 3 Balanced, 4 Add, 5 Open file; light; no text cut (badges 1 and 3 touch the edge of their radio dots); output folder D:\Media\av-kit. PASS
- convert-dark 1091x386: same marks; dark; radio groups and checkbox in dark; no text cut; no personal data. PASS
- capture-light 1091x212: 1 Capture region, 2 shot-1.png in the list at the left, 3 Arrow tool, 4 Save; light; "Named" select light; whole toolbar and Options shown, no text cut; inbox D:\Media\av-kit, fixture thumbnails only. PASS
- capture-dark 1091x212: same marks; dark; "Named" select dark; no text cut; no personal data. PASS
- settings-download-light 804x102: 1 "Saves as you type" note (whole, beside the card title "Download"), 2 Browse; light; "Download path" label whole; next row cut off cleanly above the "Quality" label; path D:\Media\av-kit. PASS
- settings-download-dark 804x102: same marks; dark; no text cut; no personal data. PASS
- settings-setup-light 804x645: 3 "3 of 4 ready" (whole), 4 Copy prompt; light; Client and Scope selects white; Readiness rows whole with Fix for FFmpeg; the prompt is masked (plain block); left edge shows only text-free slivers of the section nav. PASS
- settings-setup-dark 804x645: same marks; dark; Client and Scope selects dark (F1 was both white); mask in the dark elevated colour; no text cut; no personal data. PASS

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/help-quick-start/hq-make-scripts.py output for row 0 (task.md row 0's Validation cell: baseline.ps1 records baseline.sha, the dirty list and hashes, the scope, line-ending, skip and pin hashes, the cited anchors, the plan-local selftests and the base UI and tooling suites); receipts C:/Temp/av-kit/help-quick-start/hq-baseline.txt, hq-base-ui.txt, hq-base-tooling.txt", "scope": "Row 0: the baseline at f1ba411 and the plan-local checkers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD f1ba411 (baseline.sha) plus row 0", "output": "hq-baseline.txt: baseline-dirty.txt 54 paths; all steps exit 0. hq-base-ui.txt: Test Files  1 failed | 146 passed (147); Tests  4 failed | 1640 passed (1644) (all 4 in Session 100's untracked e2e-clipboard-guard.test.ts). hq-base-tooling.txt: 570 passed in 136.94s."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-3-4-red-unit", "command": "pwsh -NoProfile -File C:/Temp/av-kit/help-quick-start/hq-row4-run.ps1 and the row 3 script (task.md rows 3 and 4: pytest on test_help_guide_ste.py, Vitest on help-quick-start.test.tsx and help-shots-privacy.test.ts, the AC-115.15 Red, red-check.py, red-record); receipts C:/Temp/av-kit/help-quick-start/hq-row3-red.txt, hq-row3-red-check.txt, hq-row4-red.txt, hq-row4-red-check.txt, hq-row4-console.txt, hq-row4-console-check.txt", "scope": "AC-162.1 to AC-162.9 Red on the unchanged renderer; AC-162.5 no match guard passes; AC-115.15 Red after its D-1290 A assertion change", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD f1ba411 (baseline.sha) plus rows 0 to 4", "output": "hq-row3-red.txt: 1 failed, 3 passed in 0.09s; AssertionError: AC-162.2 repo: quick-start.json missing. hq-row4-red.txt: Test Files  2 failed (2); Tests  12 failed | 1 passed (13); every block by assertion. hq-row4-red-check.txt: 8 required, 0 problems. hq-row4-console.txt: Tests  1 failed | 1 skipped (2). hq-row4-console-check.txt: red-check: 1 receipt(s), runner any, 1 required test(s), 0 allowed pass(es), 0 step target(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-5-red-e2e", "command": "pwsh -NoProfile -File C:/Temp/av-kit/help-quick-start/hq-row5-run.ps1 then hq-row5b-run.ps1 (task.md row 5: host-wait, the UI build, Playwright on help-quick-start.test.ts, red-check.py with the step targets, red-record); receipts C:/Temp/av-kit/help-quick-start/hq-row5-red.txt, hq-row5-red-check.txt, hq-row5-hashes.txt", "scope": "AC-162.10 hint, AC-162.11 (six pages) and AC-162.12 Red in real Electron; AC-162.10 closed guard passes at Red", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD f1ba411 (baseline.sha) plus rows 0 to 5", "output": "hq-row5-red.txt: 8 failed; 1 passed (1.3m); AC-162.10 hint Error: expect(locator).toHaveText(expected) failed; AC-162.11 x6 and AC-162.12 Error: expect(locator).toBeVisible() failed; isolation: ok on each launch. hq-row5-red-check.txt: 0 problems, 24 step targets."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-6-7-green-unit", "command": "pwsh -NoProfile -File C:/Temp/av-kit/help-quick-start/hq-row6-run.ps1 and hq-row7-run.ps1 (task.md rows 6 and 7: the topic rewrite and quick-start.json, the STE gate, AC-162.9, the pins, the card and styles, the AC-162 unit set, typecheck, lint, only-failing, red-unchanged, eol-check); receipts C:/Temp/av-kit/help-quick-start/hq-row6-*.txt, hq-row7-*.txt", "scope": "AC-162.1 to AC-162.6, AC-162.8 and AC-162.9 Green; AC-162.4 figures and AC-162.7 still failing by assertion until row 8", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD f1ba411 (baseline.sha) plus rows 0 to 7", "output": "hq-row6-ste.txt: 4 passed in 0.15s. hq-row6-ac9.txt: Tests  1 passed | 9 skipped (10). hq-row6-pins.txt: Tests  85 passed (85). hq-row7-green.txt: Tests  2 failed | 11 passed (13). hq-row7-check.txt: row-check only-failing: 0 problem(s). hq-row7-pins.txt: Test Files  16 passed (16); Tests  246 passed (246). Types and lint clean."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-8-generator", "command": "pwsh -NoProfile -File C:/Temp/av-kit/help-quick-start/hq-row8-rerun.ps1 (task.md row 8's Validation cell after the D-1297, D-1298 and D-1295 fixes: vitest --clearCache, the UI build, two help:shots runs, row-check shots, the negative run on a planted stage copy, assets-unchanged, the AC-162 unit set, red-unchanged); receipts C:/Temp/av-kit/help-quick-start/hq-row8-d1295.txt, hq-row8-shots-1.txt, hq-row8-shots-2.txt, hq-row8-shots-check.txt, hq-row8-neg.txt, hq-row8-neg-check.txt, hq-row8-review.txt", "scope": "AC-162.14; AC-162.4 figures and AC-162.7 Green on the D-1295 images", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 49ab790 plus rows 0 to 8 and D-1295", "output": "hq-row8-shots-check.txt: 14 shots match the manifest; shots hq-row8-shots-1.txt: isolation ok 12 (launches 12); shots hq-row8-shots-2.txt: isolation ok 12 (launches 12); row-check shots: 0 problem(s). hq-row8-neg.txt: privacy: blocked settings-download-light. hq-row8-neg-check.txt: assets-unchanged: 15 file(s), negative exit 1. hq-row8-d1295.txt: Tests  13 passed (13); row-check red-unchanged: 0 problem(s); row8 exit 0. hq-row8-review.txt: 14 PASS."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-d1295-theme-negative", "command": "pwsh -NoProfile -File C:/Temp/av-kit/help-quick-start/hq-d1295-neg.ps1 (a planted copy of help-shots.shots.ts without the theme event, run on the tts stage, then removed); receipts C:/Temp/av-kit/help-quick-start/hq-d1295-neg.txt, hq-d1295-neg-exit.txt", "scope": "D-1295: applyTheme refuses a shot whose selects keep the other theme's G30 colour (round 1 F1); the wrapper exits 0 and records the planted run's expected exit 1", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 49ab790 plus rows 0 to 8 and D-1295", "output": "hq-d1295-neg.txt: Error: theme dark: select colour not switched: _r_4_=rgb(255, 255, 255), _r_5_=rgb(255, 255, 255), _r_7_=rgb(255, 255, 255); 1 failed. hq-d1295-neg-exit.txt: neg exit 1; planted copy removed: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-9-electron", "command": "pwsh -NoProfile -File C:/Temp/av-kit/help-quick-start/hq-row9-run.ps1 (task.md row 9: the UI build, host-wait before each run, Playwright --repeat-each 3 on help-quick-start.test.ts, help-search.spec.ts, help-f1-mount.test.ts and keyboard-shortcuts.test.ts once, row-check e2e-count and red-unchanged); receipts C:/Temp/av-kit/help-quick-start/hq-row9-*.txt", "scope": "AC-162.10 to AC-162.12 Green, AC-162.16 (3 runs of 3) and the help E2E pins of AC-162.13", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 49ab790 plus rows 0 to 9 and D-1295 (rerun on the retaken images)", "output": "hq-row9-hq.txt: 27 passed (2.3m). hq-row9-search.txt: 3 passed (5.0s). hq-row9-f1.txt: 5 passed (31.5s). hq-row9-keys.txt: 2 passed (16.4s). hq-row9-runs.txt: e2e-count hq-row9-hq.txt: 27 AC-162 ok lines, passed [27], want 27; row-check e2e-count: 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-h1-2-gate", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-20-help-quick-start/session-gate.ps1 *> C:/Temp/av-kit/help-quick-start/hq-gate-h1.txt (task.md row H1-2's Validation cell); step receipts C:/Temp/av-kit/help-quick-start/hq-D6-*.txt", "scope": "H1-2: the registered verification plan, identity before and after, static, targeted, host-load, fresh full and the four E2E suites, with the named skips", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "49ab790cac04dfb7cdd042476a717985d4359ac8+c172b9915978993694a33e677f113769ad092aa99478ec8b541d1fde9cfd559f", "fresh": true, "snapshot": false, "output": "hq-gate-h1.txt: tested_state before=49ab790cac04dfb7cdd042476a717985d4359ac8+c172b9915978993694a33e677f113769ad092aa99478ec8b541d1fde9cfd559f after=49ab790cac04dfb7cdd042476a717985d4359ac8+c172b9915978993694a33e677f113769ad092aa99478ec8b541d1fde9cfd559f; session-gate: all steps exit 0. hq-D6-ui-tests.txt: Test Files  149 passed (149); Tests  1657 passed (1657). hq-D6-py-tooling.txt: 574 passed in 324.19s (0:05:24). hq-D6-e2e-help-quick-start.txt: 9 passed (28.1s). hq-D6-host-load.txt: host-load: ran at 27.4 %. Rerun after D-1295 on the retaken images; the earlier gate receipts are in pre-d1295/gate."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-h1-2-recheck", "command": "uv run --no-sync python docs/execution/plans/2026-11-20-help-quick-start/identity.py --state-only, compared with the gate's tested_state line, and git rev-parse HEAD; receipt C:/Temp/av-kit/help-quick-start/hq-identity-recheck-h1-2.txt", "scope": "H1-2: the gate's tested_state re-derived after the gate process exited, before the row was marked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "49ab790cac04dfb7cdd042476a717985d4359ac8+c172b9915978993694a33e677f113769ad092aa99478ec8b541d1fde9cfd559f", "output": "hq-identity-recheck-h1-2.txt: identity now equal to the gate's tested_state: True; HEAD 49ab790cac04dfb7cdd042476a717985d4359ac8"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-h1-3-focus", "command": "uv run --no-sync python C:/Temp/av-kit/help-quick-start/hq-h1-3-focus.py, then pwsh -NoProfile -File C:/Temp/av-kit/help-quick-start/hq-h1-3-run.ps1 (task.md row H1-3's Validation cell); receipts C:/Temp/av-kit/help-quick-start/hq-focus-write-h1-3.txt, hq-render-check.txt, hq-h13-status.txt, hq-h13-check.txt", "scope": "H1-3: the Session 99 entry on top of current-focus.md; MEU-162 ready_for_review from row 10, with no new status write", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "49ab790cac04dfb7cdd042476a717985d4359ac8+c172b9915978993694a33e677f113769ad092aa99478ec8b541d1fde9cfd559f", "output": "hq-focus-write-h1-3.txt: current-focus.md 251 to 254 lines, CRLF only: True. Checks rerun after D-1295 (hq-h1-3-recheck-console.txt). hq-render-check.txt: Drift check passed — SSOT loaded (162 MEUs, 12 phases), rendered regions match on-disk content. hq-h13-check.txt: MEU-162 ready_for_review: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-h1-4-skip-basis", "command": "pwsh -NoProfile -File C:/Temp/av-kit/help-quick-start/hq-h1-4-run.ps1 (task.md row H1-4's Validation cell); receipt C:/Temp/av-kit/help-quick-start/skip-basis-check.txt", "scope": "H1-4: the basis for the skipped py-types, py-tests, openapi and mcp-* steps", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "49ab790cac04dfb7cdd042476a717985d4359ac8+c172b9915978993694a33e677f113769ad092aa99478ec8b541d1fde9cfd559f", "output": "skip-basis-check.txt (rerun after D-1295): packages or mcp-server changes since row 0: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "hq162-h1-5-sources", "command": "view_file of .agent/context/handoffs/TEMPLATE.md, 2026-11-17-ui-small-fixes-MEU-158-handoff.md and the newest other handoff by mtime, with sha256 into C:/Temp/av-kit/help-quick-start/hq-source-read-h1-5.txt", "scope": "H1-5: the template and the precedents read before this handoff", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "49ab790cac04dfb7cdd042476a717985d4359ac8+c172b9915978993694a33e677f113769ad092aa99478ec8b541d1fde9cfd559f", "output": "hq-source-read-h1-5.txt: TEMPLATE.md 1e013a15c3cecfc3c290b051a6e1e6c0ed07ad661f14a936fe786a92d06702be; 2026-11-17-ui-small-fixes-MEU-158-handoff.md 53b21ac37329d2d041421c03102a7f15a9d9c7dd0ba1cf633b4261a8380401b6; 2026-11-20-e2e-devpc-clipboard-handoff.md f7f588227cd720d3ade59776d3b1d2eedb9975bad0602e3bb4453edb64929af4 (Session 100, the newest other handoff)"}
```

### Quality Gate Results

On the final tree, from `identity-before` to `identity-after`, at `HEAD` `49ab790`; the last line of `hq-gate-h1.txt` is `session-gate: all steps exit 0`, and the gate's `tested_state` equals the identity re-derived after it (`hq-identity-recheck-h1-2.txt`). The host load before the fresh full stage read `host-load: ran at 27.4 %` (`hq-D6-host-load.txt`). This is the gate rerun after D-1295; the first gate's receipts are in the scratch `pre-d1295/gate` folder.

| Step | Stage | Result | Decisive line | Receipt |
|------|-------|--------|---------------|---------|
| `identity-before` | identity | exit 0 | `tested_state 49ab790cac04dfb7cdd042476a717985d4359ac8+c172b9915978993694a33e677f113769ad092aa99478ec8b541d1fde9cfd559f` | `hq-D6-identity-before.txt` |
| `ui-types` | static | exit 0 | `tsc --noEmit`, exit 0 | `hq-D6-ui-types.txt` |
| `ui-lint` | static | exit 0 | `eslint src/ tests/ --max-warnings 0`, exit 0 | `hq-D6-ui-lint.txt` |
| `task-contract` | static | exit 0 | `OK: 28 row(s); 10-column table (with builder_model); 26 row(s) fully checked`; `2 row(s) exempt (view_file): H1-5, H2-1` | `hq-D6-task-contract.txt` |
| `scope-paths` | static | exit 0 | `changed paths: 81 outside scope: [] other sessions plan files skipped: 0` (78 at the first gate, plus `current-focus.md`, this handoff and the round 1 review written after it); `read-never-changed files: 38 mismatch: [] baseline-dirty hash mismatch: []`; `ancestor ok: True`; `head moved (S4): False` | `hq-D6-scope-paths.txt` |
| `line-endings` | static | exit 0 | `eol-check: 39 scope path(s), 0 problem(s)` | `hq-D6-line-endings.txt` |
| `home-path` | static | exit 0 | `check_home_path: ok files=2912 allowlisted=60 nul=45` | `hq-D6-home-path.txt` |
| `skill-identity` | static | exit 0 | `row-check skill: 0 problem(s)` | `hq-D6-skill-identity.txt` |
| `pins-unchanged` | static | exit 0 | `row-check pins-unchanged: 0 problem(s)` | `hq-D6-pins-unchanged.txt` |
| `red-unchanged` | static | exit 0 | `row-check red-unchanged: 0 problem(s)` | `hq-D6-red-unchanged.txt` |
| `red-check-selftest` | static | exit 0 | `red-check selftest: 111 fixture(s) (32 positive, 79 negative), 0 wrong: []` | `hq-D6-red-check-selftest.txt` |
| `eol-check-selftest` | static | exit 0 | `eol-check selftest: 24 case(s), 0 wrong: []` | `hq-D6-eol-check-selftest.txt` |
| `row-check-selftest` | static | exit 0 | `row-check selftest: 0 wrong: []` | `hq-D6-row-check-selftest.txt` |
| `py-format` | static | exit 0 | `9 files already formatted` | `hq-D6-py-format.txt` |
| `py-lint` | static | exit 0 | `All checks passed!` | `hq-D6-py-lint.txt` |
| `ste-gate` | targeted | exit 0 | `4 passed in 0.55s` | `hq-D6-ste-gate.txt` |
| `help-unit` | targeted | exit 0 | `Test Files  18 passed (18)`; `Tests  259 passed (259)` | `hq-D6-help-unit.txt` |
| `host-load` | host | exit 0 | `host-wait: ok (27.4 %, limit 50 %)` | `hq-D6-host-load.txt` |
| `ui-tests` | full | exit 0 | `Test Files  149 passed (149)`; `Tests  1657 passed (1657)`; `baseline ui failures excused: []` | `hq-D6-ui-tests.txt` |
| `py-tooling` | full | exit 0 | `574 passed in 324.19s (0:05:24)` | `hq-D6-py-tooling.txt` |
| `ui-build` | full | exit 0 | `built in 3.93s` | `hq-D6-ui-build.txt` |
| `e2e-help-quick-start` | runtime | exit 0 | `9 passed (28.1s)`; `other outcomes=False`; `rejection-record lines=0` | `hq-D6-e2e-help-quick-start.txt` |
| `e2e-help-search` | runtime | exit 0 | `3 passed (2.6s)`; `other outcomes=False`; `rejection-record lines=0` | `hq-D6-e2e-help-search.txt` |
| `e2e-help-f1-mount` | runtime | exit 0 | `5 passed (26.6s)`; `other outcomes=False`; `rejection-record lines=0` | `hq-D6-e2e-help-f1-mount.txt` |
| `e2e-keyboard-shortcuts` | runtime | exit 0 | `2 passed (1.7s)`; `other outcomes=False`; `rejection-record lines=0` | `hq-D6-e2e-keyboard-shortcuts.txt` |
| `state-render` | full | exit 0 | `Drift check passed — SSOT loaded (162 MEUs, 12 phases)` | `hq-D6-state-render.txt` |
| `identity-after` | identity | exit 0 | the same `tested_state` as `identity-before` | `hq-D6-identity-after.txt` |
| `py-types` | static | skipped | every `packages/` file keeps its `baseline-skip-hashes.json` hash (H1-4); no Python product file changes | `hq-gate-h1.txt` |
| `py-tests` (full) | full | skipped | as `py-types`; `tests/tooling` runs in full as `py-tooling` | `hq-gate-h1.txt` |
| `openapi` | full | skipped | every `packages/api/` file keeps its hash (H1-4); no route or schema changes | `hq-gate-h1.txt` |
| `mcp-types`, `mcp-build`, `mcp-tests`, `mcp-audit` | full | skipped | every `mcp-server/` file keeps its hash (H1-4); no MCP tool changes | `hq-gate-h1.txt` |
| `e2e-other` | runtime | skipped | only the help card changed, and its four suites run above | `hq-gate-h1.txt` |
| the gate | all | pass | `session-gate: all steps exit 0` | `hq-gate-h1.txt` |

`ui-tests` is the row-0 base (1644) plus the 13 new unit tests; `py-tooling` is the base (570) plus the 4 STE gate cases.

---

## Changed Files

Counts are added / removed lines against `HEAD` `49ab790` (`git diff --numstat --ignore-cr-at-eol HEAD`); a new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `ui/src/renderer/src/components/help/quick-start.json` | `QUICK_START_DATA`: six pages, 28 steps, 7 shots | new, 223 | LF |
| `ui/src/renderer/src/components/help/quick-start.ts` | `QUICK_START_SCHEMA`: `QUICK_START`, `validateQuickStart`, `quickStartHash`, `quickStartHashInput` | new, 193 | LF |
| `ui/src/renderer/src/components/help/help-shots.ts` | `HELP_SHOTS`: `shotUrl`, `shotSize` through `import.meta.glob` | new, 36 | LF |
| `ui/src/renderer/src/components/help/HelpCard.tsx` | `CARD_QUICK_START`: hint `:187-189`, `QuickStart` `:82-100`, `HelpShot` `:44-79`, closed `<details>` topics `:215-218` | +75 / -3 | LF kept |
| `ui/src/renderer/src/styles.css` | `THEME_SHOT_CSS` and the step and figure styles, existing tokens only | +59 / -0 | CRLF kept |
| `ui/src/renderer/src/assets/help/*.webp`, `manifest.json` | 14 screenshots (5,076 to 26,094 bytes, retaken under D-1295) and their manifest | new, 15 files | binary; manifest LF |
| `ui/src/renderer/src/features/*/*-help-content.ts` (six) | `PLAIN_TOPICS` and `CONSOLE_AND_SAVE`: titles and bodies only | downloader +8/-8, transcript +9/-9, tts +10/-10, converter +11/-11, capture +12/-12, settings +9/-9 | CRLF kept |
| `ui/tsconfig.json` | `resolveJsonModule` | +2 / -1 | kept |
| `ui/package.json` | `:26` `help:shots` | +1 / -0 | CRLF kept |
| `ui/playwright.help-shots.config.ts` | the generator's Playwright config | new, 20 | LF |
| `ui/tests/help-shots/help-shots.shots.ts` | `HELP_SHOTS_GEN` (with D-1297's framing and D-1295's `applyTheme`) | new, 563 | LF |
| `ui/tests/help-shots/stage.ts` | `DEMO_STAGE`: one demo stage per page | new, 498 | LF |
| `ui/tests/help-shots/privacy.ts`, `clip.ts` | `PRIVACY_GUARD` (`findPrivatePath`, `clipText`), `shotClip` | new, 65 and 55 | LF |
| `ui/tests/unit/help-quick-start.test.tsx` | AC-162.1, AC-162.3 to AC-162.7, AC-162.9 | new, 711 | LF |
| `ui/tests/unit/help-shots-privacy.test.ts` | AC-162.8 | new, 136 | LF |
| `ui/tests/e2e/help-quick-start.test.ts` | AC-162.10 to AC-162.12 | new, 164 | LF |
| `ui/tests/e2e/test-ids.ts` | `TEST_IDS`: five help ids at the end | +6 / -0 | CRLF kept |
| `ui/tests/unit/failure-reason-copy.test.ts` | AC-115.15's Console body (D-1290 A) | +3 / -3 | kept |
| `ui/tests/unit/capture-page.test.ts`, `convert-page.test.ts`, `settings-page.test.ts` | D-1296: the new topic words | +3/-3, +1/-1, +1/-1 | kept (convert-page mixed, kept) |
| `tools/help_guide_ste.py` | `STE_GATE` linter | new, 316 | LF |
| `tests/tooling/test_help_guide_ste.py` | AC-162.2 | new, 98 | LF |
| `.agent/skills/asd-ste100/` | the vendored skill (six files, byte-equal) and `UPSTREAM.md` | new folder | as upstream |
| `.agent/skills/README.md` | the skill's row | +1 / -0 | CRLF kept |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`, `docs/build-plan/build-priority-matrix.md` | MEU-162 registered (row 1) and `ready_for_review` (row 10); `meu_status.py render` | +29/-2, +1/-0, +3/-3, +1/-0 | kept |
| `docs/build-plan/06-gui.md` | §Help quick start (residual) (row 1) and the `Delivered (Session 99)` note (row 10) | +16 / -0 | CRLF kept |
| `.agent/docs/commands.md` | the `help:shots` lines in the command block (row 10) | +5 / -0 | CRLF kept |
| `docs/execution/plans/2026-11-20-help-quick-start/` | the plan (D-1296 to D-1298 in its YAML), task (row marks), the plan-local scripts, the row-0 records and `session-gate.ps1` | new folder | LF |
| `.agent/context/handoffs/2026-11-20-help-quick-start-MEU-162-handoff.md` | this handoff | new | LF |

**The card.** `HelpCard.tsx` (LF), the open panel:

```diff
+          {searching ? null : (
+            <>
+              <QuickStart page={page} />
+              <h3 className="font-medium text-sm">More about this page</h3>
+            </>
+          )}
           {filtered.map((section) => (
-            <article key={section.id} data-help-section={section.id}>
+            <details key={section.id} data-help-section={section.id} open={searching} className="help-topic">
+              <summary className="font-medium text-sm cursor-pointer">{section.title}</summary>
```

**One step.** `quick-start.json` (LF), Downloader step 2: `"text": "Paste the link in the URL field. Ctrl+L moves the cursor to the field.", "target": "url-input"`.

Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 (round 1) | Medium | no | behavior | Some dark screenshots kept light native-control colours: the generator switched only the root `.dark` class, so `SelectInput`'s inline G30 colours stayed light (`tts-dark.webp` Format select, `settings-setup-dark.webp` Client and Scope) | `ui/tests/help-shots/help-shots.shots.ts:516` (round 1); `ui/src/renderer/src/lib/theme.ts:67`; `ui/src/renderer/src/components/ui/SelectInput.tsx:50` | Apply the full theme transition, retake the images, rerun the affected checks, add a select-colour check | fixed |

Round 1 (`.agent/context/handoffs/2026-11-20-help-quick-start-implementation-critical-review.md`, Codex): `approved`, one non-blocking Medium (F1).

Round 2 (the same rolling report, Codex recheck): `approved`; F1 `fixed`, no new findings, 0 open (`review-state-check.txt`, `exec-review.txt`: approved at round 2 of 6).

**Corrections applied after round 1 (D-1295):**

- `help-shots.shots.ts` has `applyTheme`. It does what `applyDocumentTheme` does (`theme.ts:54-76`): it sets the class, sets `colorScheme`, sends `av-kit:theme-changed` and waits two frames. It then refuses the shot when a select's inline background is still the other theme's G30 colour (`SelectInput.tsx:18-31`). This is the select-colour check that F1 asks for. Selects styled by a CSS variable follow the class and are not flagged.
- The negative: a planted copy without the event fails `tts dark` with `select colour not switched` on three white selects, exit 1, and the copy is removed (`hq-d1295-neg.txt`, `hq-d1295-neg-exit.txt`).
- The 14 images were retaken. Row 8 passed in full (`hq-row8-d1295.txt`), and the new image review checks the native selects in each theme (`hq-row8-review.txt`). Row 9 and the H1-2 gate were rerun on the new tree.
- `ui/tests/e2e/help-quick-start.test.ts` is unchanged, because it is a Red-pinned file (stop S3). Its class-only switch is enough for its own assertion, since the figure rule keys on `:root.dark`.

### Verdict

`approved` at round 2 of 6. Round 1 was approved with F1 open (non-blocking); D-1295 fixed it and the round 2 recheck confirms the fix, with no new findings.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Opening the card on a first visit, or highlighting the hint | out-of-scope | — | D-1289 A (Mat 2026-11-20) |
| Rewording the four pinned topics or splitting `four-tools` | out-of-scope | — | D-1290 A (Mat 2026-11-20) |
| A separate guide document, README images, click-to-zoom | out-of-scope | — | Plan §Out of Scope ("not too long just enough to get people curious") |
| Running `help:shots` in CI | out-of-scope | — | It needs a desktop Electron run; the drift tests in the gate catch stale images |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |

### Departures and their basis

- **The pinned topics are four, not five.** The task text says "the five pinned topics kept". D-1290 A unpinned the Settings Console topic, so the plan names four (`PINNED_TOPICS`, `implementation-plan.md:196`), and the 06 Delivered note says four. They are kept byte for byte, apart from the one `four-tools` Save sentence of `CONSOLE_AND_SAVE`: `downloader:pause` (`ui/src/renderer/src/features/downloader/downloader-help-content.ts:25`), `transcript:blocked` (`ui/src/renderer/src/features/transcript/transcript-help-content.ts:30`), `capture:original-annotated` (`ui/src/renderer/src/features/capture/capture-help-content.ts:20`) and `capture:four-tools` (`ui/src/renderer/src/features/capture/capture-help-content.ts:25`). The gate's `pins-unchanged` step holds their pin files to the row-0 hashes, and AC-162.9 compares their titles and bodies with `baseline-pins.json`.
- **Session 100 and the re-baseline.** Session 100 ran on the same tree. Before row 1 it changed `ui/tests/e2e/electron-app.ts` (in this plan's read-only scope); Mat said "continue", and row 5 re-read the file and rebound its hash. During row 8 it asked for a freeze of `ui/src`, builds and Electron launches, which this session kept until it ended its window. It then committed `49ab790` from `f1ba411` with none of this plan's own paths. `baseline.sha` keeps the row-0 value `f1ba411`; rows 8 to 10 and the gate ran on `49ab790`. The gate's `scope-paths` step accepts exactly that move: the base must be an ancestor, the commit may touch no path of this plan that is not shared, and every read-only or baseline-dirty path it touched must be clean in `git status` (`head moved (S4): False`). The four base Vitest failures were in Session 100's then-untracked test file; its commit fixed them, and the gate's `ui-tests` has no failure.
- **D-1296 (execution, human, M-7; in the plan's YAML).** Row 6's rewrite changed topic words that three older tests pinned. Mat chose "Update the 3 tests (Recommended)" on 2026-11-21: each check now names the new words of the same topic, `baseline-pins.json` holds the two new hashes, and row 7 also runs `settings-page.test.ts`.
- **D-1297 (execution, autonomous, `mandatory: none`; in the plan's YAML).** The first image review found cut text, and the second found badges over small text and half rows at the clip edges. The generator now centres the targets, widens each clip to the targets' section rows and labels, puts the badge at x-16, y-16 and moves clip edges off cut text. This departs from the `HELP_SHOTS_GEN` text "scrollIntoView({ block: 'start' }) ... the union of the target boxes plus 24 px". `shotClip`, `stage.ts`, the privacy guard and every assertion are unchanged; the privacy guard reads the final clip. The first image set is kept in the scratch `pre-review-fix` folder.
- **D-1295 (after the execution review's round 1, autonomous, `mandatory: none`; in the plan's YAML).** Round 1 approved with F1, a non-blocking Medium: dark screenshots kept light selects. The goal says the screenshot matches the light or dark theme, so the fix is in the generator only (Corrections applied, above). The E2E file stays unchanged because it is Red-pinned. Its class-only switch is enough for what it asserts. The first version of the check flagged every select with an inline style, and Downloader light failed on selects styled by `var(--color-bg-elevated)`, before any image was written (`hq-row8-d1295-attempt1.txt`; assets unchanged). The check now flags only the other theme's G30 literal. The images from before D-1295 are kept in the scratch `pre-d1295` folder.
- **D-1290's precedent wording.** The `decision_sources` probe refused the plan's YAML because one precedent named an app-data path in braces, which the placeholder pattern reads as a template slot. The precedent now says "an app-data path slot". Nothing else changed.
- **D-1298 (execution, autonomous, `mandatory: none`; in the plan's YAML).** Capture step 2 said the shot list is below the image; the filmstrip is at the left of the editor, so the step now says "Click the new shot in the list at the left of the image." This is the only change to the reviewed draft's text; row 6 itself made none. The STE gate is 0 problems, and the capture `stepsHash` and images were retaken in row 8.
- **Three plan-local checker fixes.** (1) Row 5: Playwright 1.64.1 prints a locator expect's state as its own `Error: element(s) not found` line, which `red-check.py` read as an unattributed error; it now classes that exact line as part of the assertion, only in Playwright mode and only after an assertion line in the same block (two new fixtures; selftest 111 fixtures, 0 wrong). (2) Row 7: `row-check.py only-failing` refused `--id 'AC-162.4 figures'` because the real title has a colon after the id; `_starts` now takes a space or a colon (two new self-test cases). (3) Row 8: `row-check.py neg-stage` looked for `path: 'D:\Media\av-kit'`, but row 5 wrote the Settings path in `stage.ts` as `path: media,`; its pattern now matches that line, and the plant writes the quoted home path. `stage.ts` is unchanged. Each fix kept LF and passed ruff.
- **The Vitest module cache.** The first full row 8 run failed `AC-162.4 figures` because Vitest's module cache held `help-shots.ts` as transformed at row 6, before the images existed; the cache key is the file's own content, not the files `import.meta.glob` matches. `vitest --clearCache` and a full rerun of the row passed. Known limit: adding or renaming an image without a change to `help-shots.ts` needs `--clearCache` again.
- **The task's Status cells.** Rows 0 to 10 and H1-1 first carried their evidence text in the Status cell; `lint_task_contract.py` accepts only the bare status, so the cells now read `[x]` and the evidence is in this handoff.
- **How the rows ran.** Each row's Validation cell was extracted to a `.ps1` file with an environment header (working directory, `PYTHONIOENCODING`, `PYTHONDONTWRITEBYTECODE`, `RECEIPTS_DIR`, `TMP`, `TEMP`) and run with `pwsh -NoProfile -File`. Hand edits were made by scripts that wrote bytes and asserted each anchor once. Every Electron run cleared `ELECTRON_RUN_AS_NODE`, used scratch app data and waited for the host load at or below 50 %.
- **Processes.** Each Electron run stopped only the processes it launched. No other session's app, the IDE's avkit MCP server or Mat's app was stopped.

### Execution notes

- **The plan decisions.** D-1289 A (Mat, "1289 A, 1290 A, execute"): the card stays closed on a first visit; its header gains the hint. D-1290 A (same words): every unpinned topic, the Console topic and the one `four-tools` Save sentence are rewritten in plain words; the other pinned text is kept. D-1291: the quick start lives in the card, as one JSON file. D-1292: the tracked generator, demo stages and privacy guard. D-1293: the vendored skill and its gate. D-1294: the step-hash and Electron drift guards.
- **Stops.** S4 fired before row 1 (Session 100's `electron-app.ts` change); Mat said "continue". S5 fired in row 7 (the three pinned tests); Mat decided D-1296. No other stop condition was met, and no expectation was edited at Green (S3).
- **The review fix.** Round 1's F1 was fixed under D-1295 without a stop. The decision is autonomous (`mandatory: none`), the change is in the generator only, and no Red-pinned file or assertion changed. Rows 8 and 9 and the H1-2 gate were rerun after it.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-21 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3 and H1-4 |
