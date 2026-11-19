---
project: "2026-11-19-e2e-host-parity"
date: "2026-11-19"
source: "grouping .agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md §3 Session 97; issues CAPTURE-TEXT-PIXEL-2PX-MINIAIR (D-1213) and E2E-HOVER-NO-POINTER-DEVICE (D-1214)"
meus: ["MEU-161"]
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md"
---

# Implementation Plan: make the capture text plate follow the bake and the E2E suite pass on the second Windows host

> **Project**: `2026-11-19-e2e-host-parity`
> **Build Plan Section(s)**: Phase 9 (screenshot capture), new MEU-161 `capture-text-plate-metrics` at matrix item 9.46, registered in row 2 (D-1250); it depends on MEU-82 (`capture-render-fidelity`) and MEU-102 (`capture-text-multiline`).
> **Status**: said to execute (USER_EXPLICIT 2026-11-18 "proceed with the next session prompt orchestration here like you did the others", with USER_EXPLICIT 2026-11-18 "make the decisions always the recommenations"). `plan_to_exec_gate: human`: those messages are the execution approval once the plan review approves and no STOP item is open; the plan review was approved at round 2 after F1 was fixed (.agent/context/handoffs/2026-11-19-e2e-host-parity-plan-critical-review.md), and no STOP item is open. Session 97 is the second and last session of the 2026-11-18 E2E-host grouping; Session 96 (`2026-11-18-e2e-remote-host`, committed as `2c41c70`) built the remote-run tool this session's acceptance run uses.

---

## Goal

**Goal anchor:** the full Electron E2E suite passes on the second Windows host (the mini-air) through `tools/e2e_remote.py run <commit>` at this session's final tree, with 232 tests, 232 expected, the two clipboard specs skipped by their tracked `skip` entries, and `tools/e2e_host/known-failures.json` holding no `known` entry; the four entries it holds now are shown passing in that run's `known_now_passing`. Two causes are fixed, each after a receipt names the side that moves with numbers from both hosts, and each with its own Red:

1. **The capture text plate.** The preview's text plate (`textBackgroundBox` in `ui/src/renderer/src/features/capture/capture-text-metrics.ts`) is 2 px narrower on the right than the plate the bake paints. The bake is the reference (D-1242): `adapter.text_plate_box` returns Pillow's inclusive `(l, t, r, b)` and `_apply_text` fills `draw.rectangle` over it, so the painted plate is `r - l + 1` wide; the preview drops that pixel and scales a 16 px glyph table linearly, where FreeType rounds each size's extents and advances itself. The preview now computes the box from a Segoe UI glyph and kerning table in font units with FreeType's 26.6 rounding and Pillow's basic-layout kerning (D-1243, `PLATE_UNITS`) and returns the painted rectangle (`PREVIEW_FOLLOWS_BAKE`). A Pillow fixture of 2,488 painted boxes pins it; the measured residual (1,702 of 2,448 breadth cases exact, 5 more than 1 px off on a side, worst 2) is pinned as a threshold and registered as a low issue (D-1244). The three fidelity specs run at a device scale of 1 on every host (`FIDELITY_FRAME`, D-1245), so the dev PC, at a scale of 2, measures what the mini-air measures.
2. **The hover colour.** The mini-air has no pointing device, so Chromium reports `hover: none`, and Tailwind v4 puts every `hover:` style inside `@media (hover: hover)`; `settings.test.ts` AC-126.8 hovers a button and waits for a colour that cannot apply there. The spec now launches with a Blink setting that states a mouse-capable device (`HOVER_CAPABLE`, D-1246), checks that the media query matches before it hovers, and no other spec changes.

The product fix is MEU-161, registered in row 2 and set `ready_for_review` in row 8 and `approved` at H2-2. Both issues are resolved through the triage tools (row 11), the residual is added as `CAPTURE-TEXT-PLATE-METRICS-RESIDUAL` (low), and grouping row 97 is set. The dev-PC full E2E stays green (232 of 232 under `flake-run.py --mode full`, the clipboard specs excluded as in Session 91). The mini-air run needs a commit, and this session commits nothing; `snapshot-commit.py` builds one from `HEAD` plus the session's working files with a temporary index, on no ref, and leaves the refs, the index, `HEAD` and the status unchanged (`SNAPSHOT_NO_REF`, D-1247).

**Why.** `CAPTURE-TEXT-PIXEL-2PX-MINIAIR` (`known-issues.yaml:5847`, medium, P2, D-1213) and `E2E-HOVER-NO-POINTER-DEVICE` (`:5887`, low, P3, D-1214). Session 96 made the mini-air a repeatable E2E host and listed these four failures as known against the two issues so a run could pass; until they are fixed, every mini-air run carries four red specs and a Windows PC that looks more like a user's machine than the dev PC does cannot gate capture text fidelity or the settings hover rule. D-1213 asks to diagnose first and to change product code or a tolerance only with the measured cause; D-1214 asks to prove the hover cause by reproducing `hover: none` on the dev PC and then make the spec state the capability it needs.

**Grouping §3 Session 97** (`:96-107`): diagnose first, with numbers from both hosts before any change; one Red per fix; the acceptance run through Session 96's tool at the final tree (232 of 232, the clipboard specs skipped); `known-failures.json` emptied of its 4 `known` entries in this session (a resolved issue whose entry stays makes the run exit 32); the dev-PC full E2E green; both issues resolved through the triage tools. The split flag at `:107` ("yes, if the pixel diagnosis finds product code; the hover fix then lands alone") fired; D-1241 keeps one session, the hover rows first and independent (handed, M-6, M-8). `:159`: Session 97 carries D-1211 and D-1216; D-1213 and D-1214 are read from known-issues.yaml.

**What the code shows (plan-time reads at `HEAD` `2c41c70`):**

- **The preview plate.** `capture-text-metrics.ts` (CRLF, 93 lines) imports `SEGOE_LA_BASE_SIZE`, `SEGOE_LA_GLYPHS`, `SEGOE_UI_ASCENDER` and `SEGOE_UI_UNITS_PER_EM` from `capture-segoe-metrics.ts` (`:5`). `segoeAscentPx` (`:12`) is FreeType's ascender: `FT_MulFix(2210, size * 64 * 65536 / 2048)` rounded up to whole pixels; `segoeLinePitchPx` (`:28`) is the ascent plus the 4 px line gap; both stay. `textBackgroundBox` (`:58`) scales each glyph's 16 px `la` extents by `size / 16` (`:60`, `:79`, the unknown glyph `FALLBACK_GLYPH { l: 0, t: 7, r: 8, b: 18, adv: 8 }` at `:51`), unions them over the lines, and rounds once at `:88-91`: `width: Math.max(1, Math.round(right) - Math.round(left))`. Its callers are `capture-hit-test.ts`, `capture-transform.ts` and `CaptureViewport.tsx`. `capture-segoe-metrics.ts` (CRLF, 102 lines) holds the units head and the 16 px table.
- **The bake plate.** `packages/infrastructure/src/avkit_infra/capture/adapter.py:223` `text_plate_box(x, y, text, font_size)` is Pillow's `ImageDraw.textbbox((x, y), text, font, anchor="la", spacing=TEXT_LINE_GAP)` with the font from `FONT_CANDIDATES = ("segoeui.ttf", "arial.ttf")` (`:73`), an inclusive `(l, t, r, b)`; `_apply_text` (`:1117`) fills `draw.rectangle(bbox, ...)` (`:1124`), which paints both edges. The plate the user sees in the PNG is `r - l + 1` by `b - t + 1`.
- **The specs.** `ui/tests/e2e/capture-inbox.test.ts` (LF, 3,708 lines): `AC-82.6 TEXT_PIXEL_ORACLE` (`:2243`), `AC-102.19 TEXT_PARITY_E2E` (`:2347`) and `AC-102.20` (`:2370`) launch through `launchApp()` (`:68`) or `fidelityViews(` (`:2301`), seed the fidelity fixture (`:2106`), zoom to 100 %, log the preview's and the bake's ink and plate boxes as a `boxes` line (`fidelityBoxes`, `:2157`) and assert every side within 1 px. `ui/tests/e2e/settings.test.ts` (CRLF, 920 lines) `AC-126.8` (`:700`) hovers `theme-light-btn` and waits for `rgb(22, 78, 99)`. Both launch through `launchElectron` (`electron-app.ts:110`, LF), argv `['-r', MAIN_ERROR_WATCH, main ?? DEFAULT_MAIN]` (`:134`), `LaunchOptions` (`:35`) `main`, `env`, `pointerShield`; no option passes Chromium flags.
- **The unit pins.** `capture-text-metrics.test.ts:12` (CRLF) `AC-59.19` expects `{ x: 10, y: 26, width: 15, height: 12 }` for `'Hi'` at 16; `capture-transform.test.ts:170` (CRLF) `AC-101.1` uses the plate's corners; `capture-text-lines.behavior.test.ts:315` (LF) `AC-102.10` compares the 16 `text_plates` of `capture-geometry.json` as `r - l` by `b - t` and a 40-case matrix with the oracle `unionOracle` (`:57`, from the 16 px table imported at `:14`); `capture-hit-test.test.ts:140` `AC-60.3` reads the plate's centre, which stays inside. Tests that read the plate through the rendered SVG move too (expert pass H1): `capture-page.behavior.test.ts` (CRLF, 4,197 lines) `AC-82.4` (`:932`), the MEU-101 block (`:3158`) and the `AC-59.19` render (`:3495`), and the E2E `AC-101.6` (`capture-inbox.test.ts:3078`). The set was found by running: the full Vitest with the planned function fails 8 of 1,633; with §Test pins the touched files pass 148 of 148, and with the old function 9 fail (`ehp-plan-h1-pins.txt`).
- **The known list.** `tools/e2e_host/known-failures.json` (LF, 740 bytes, label `mini-air`): 4 `known` entries (`capture-inbox.test.ts` `AC-82.6`, `AC-102.19`, `AC-102.20` against `CAPTURE-TEXT-PIXEL-2PX-MINIAIR`; `settings.test.ts` `AC-126.8` against `E2E-HOVER-NO-POINTER-DEVICE`) and 2 `skip` entries (`capture-filmstrip-actions.test.ts` and `capture-import.test.ts`, reason "clipboard spec; grouping §3 Gate"). `tools/e2e_remote.py summarize` exits 32 when a listed issue is not `open` or a listed test is absent, 40 on an unlisted failure, and 0 with a known test that now passes named in `known_now_passing`.
- **The mini-air runs.** Two tool runs of `a43cdb2` (`C:/Temp/av-kit/e2e-remote/r20261119T074154Z-a43cdb2/`, `r20261119T084412Z-a43cdb2/`) and three hand runs (`20261118-183804`, `-185348`, `-191358`) fail the same four specs. In all five, `AC-82.6` and `AC-102.20` log the preview plate 20, 43, 49, 66 against the bake's right 51 (ink right 47 against 48, origin 718, 442.5), and `AC-102.19` 20, 29, 49, 133 against 20, 29, 51, 134 (origin 718, 422.5): gaps `[0, 0, 2, 0]` and `[0, 0, 2, 1]` (`ehp-plan-boxes-report.txt`, `ehp-plan-boxes-miniair.txt`). The mini-air renders at a device scale of 1; `AC-126.8` receives `rgb(21, 94, 117)`.
- **The dev PC.** The same three specs pass at a device scale of 2 with a gap of `[1, 1, 1, 1]` (`ehp-plan-devpc-fidelity.txt`). `fidelity-probe.mjs` (`ehp-plan-fidelity-probe-plan.txt`) launches the built app natively and at `--force-device-scale-factor=1`, at three origins, with the plate 30 px (now) and 32 px (the bake's painted width): at a scale of 1 the 30 px plate gives `[0, 0, 2, 0]` at every origin and the 32 px plate 0; at 2 the result depends on the origin (`[1, 1, 1, 1]` at the dev PC's half-pixel origin, a right gap of 2 at a whole-pixel one). So the preview's plate width moves, and the dev PC hid it.
- **The hover cause.** `hover-probe.mjs` (`ehp-plan-hover-probe-2.txt`, `ehp-plan-hover-probe-plan.txt`; Electron 42.11.18, Chrome 148): natively `(hover: hover)` matches and the hovered button reads `rgb(22, 78, 99)`; CDP emulated media `hover: none` does not move the match; CDP touch emulation and `--blink-settings=primaryHoverType=1,availableHoverTypes=1,primaryPointerType=1,availablePointerTypes=1` give `hover: none` and `rgb(21, 94, 117)`, the mini-air's failure, also in the real `AC-126.8` (M3, `ehp-plan-m3-hover-spec.txt`); the capable setting (`2`, `2`, `4`, `4`) gives `hover: hover`, `pointer: fine` and `rgb(22, 78, 99)`, also after a hover-none launch. `--force-device-scale-factor=1` leaves hover unchanged.
- **The bake's model.** `ehp-plan-kern-model.py` mirrors the planned function in Python: each printable ASCII glyph's ink box at the `ls` anchor and advance in font units (Pillow at 2,048 px); `FT_MulFix` by `size * 2048`; each extent and advance rounded as `(v + 32) >> 6`; the pen moved by each pair's kerning; lines at `y + i * (ascent + 4)`; the painted rectangle. Against Pillow (`ehp-plan-kern-limits.txt`, `ehp-plan-kern-geometry.txt`): 15 of the 16 `text_plates` exact (`'Hi\n'` at 24 one pixel off at the top); `'Hi'` at 16 at (10, 20) is `{ x: 10, y: 26, width: 16, height: 13 }`; the fidelity marks (`'Hi'` and `'Hi\n\nHi\n'` at 32) equal the bake's `{ x: 20, y: 42, width: 32, height: 24 }` and `{ x: 20, y: 28, width: 32, height: 106 }`; the matrix 36 of 40 exact, 4 one pixel off; the 2,448-case breadth (18 texts, the last four dense in kerning pairs) 1,702 exact, 5 over 1 px, worst 2 (per side 0, 2, 1, 1). **Kerning** (expert pass M1): Pillow here has no raqm, so its basic layout adds `FT_Get_Kerning` over 372 printable-ASCII pairs (`AV` −117, `To` −211 units; `ehp-plan-kern-model.txt`); without it the model misses `AVAVAVAVAVAV` at 500 by 5 px (1,472 exact, 27 over). The other rounding variants do worse (`ehp-plan-newbox-variants.txt`), and the old table is up to 29 px off at large sizes (C0 of `ehp-plan-plate-breadth.txt`).
- **The font.** The dev PC and the mini-air carry the same `segoeui.ttf`: 960,076 bytes, SHA-256 `704eada12961a27fd271f7d3b09e2066520e758390c1776744eff430fee30f6e`, version 5.72 (`ehp-plan-font-facts-devpc.txt`, `ehp-plan-font-facts-miniair.txt`, read-only); Pillow 13.0.0.
- **The host now** (`tools/e2e_remote.py check`, read-only, `ehp-plan-check.txt`): `check: ok`; the user's session Active, unlocked; no busy process (the zorivest runner's account is absent there, reported, not refused); the task Ready, Interactive, Limited, 120 minutes, IgnoreNew; no lock; Node v26.13.0, uv, the VC++ runtime, ffmpeg and ffprobe present; 402 GB free.
- **The register.** Both issues are `open` with `meu_links: []`; `CAPTURE-TEXT-PIXEL-2PX-MINIAIR`'s `root_cause` starts "unknown." and `E2E-HOVER-NO-POINTER-DEVICE`'s starts "hypothesis:". MEU-161 and matrix item 9.46 are free (`ehp-plan-ids.txt`: 160 MEUs, max MEU-160; matrix 9.45 is MEU-160). D-1241 to D-1260 appear only in the grouping's allotment line.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-19). The change is one TS function and its glyph table, one new fixture, the named test pins, two E2E launch arguments and the known-failure list, with every input read verbatim at plan time (the metrics module, the bake's text_plate_box and _apply_text, the four spec files, both hosts' reports); that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in VS Code (`.agent/docs/harness-profiles.md`); commands run in `pwsh` from `P:/av-kit` through `rtk proxy` with the receipt pattern (`.agent/docs/commands.md`); session receipts under `C:/Temp/av-kit/e2e-host-parity/` (`D`); the remote tool's receipts under `C:/Temp/av-kit/e2e-remote/<run-id>/`. Vitest and Playwright run through `pwsh` with `ELECTRON_RUN_AS_NODE` removed, Vitest from `Set-Location 'P:\av-kit\ui'`.
- **The host:** reached only through `tools/e2e_remote.py` (`check`, `run`, `summarize`, and `release` with this session's own run id per the run book), which builds every `ssh` and `scp` argv with `-o BatchMode=yes -o StrictHostKeyChecking=yes` and the alias from the untracked local config; no row runs `ssh` itself, adds or changes a known-hosts entry, or touches the scheduled task beyond the tool's one `Start-ScheduledTask` per run.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` with `AGENT_MODEL_REGISTRY_HOME=P:/.agent` and `RECEIPTS_DIR` set (Session 82 RULE-3). Plan loop `ehp-plan-2026-11-19-e2e-host-parity`, execution loop `ehp-execution-2026-11-19-e2e-host-parity`; caps from `.agent/review-limits.json` (6 rounds, turn tokens off).
- **Never** commit, stage or push without Mat's words. The snapshot commit of row 10 is an object on no ref (D-1247); it moves no branch and stages nothing. The coordinator commits after the execution review, without a push.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-161 and both issues | `.agent/context/handoffs/2026-11-19-e2e-host-parity-MEU-161-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-19-e2e-host-parity-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-19-e2e-host-parity-implementation-critical-review.md`

One handoff named for the MEU, following `2026-11-17-video-tail-frame-MEU-160-handoff.md`; it also carries the hover fix, which is test-only and has no MEU (D-1214).

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline, copied checkers, selftests, the OS-wide probe (row 0) | — | shared | `baseline.*`, `identity.py`, `eol-check.py`, `red-check.py`, `issue-resolve.py`, `flake-run.py`, `host-load.ps1`, `D/baseline-copies/` |
| WP-2 | The diagnosis receipt from both hosts (row 1) | WP-1 | shared | `D/ehp-diagnosis-1.txt` |
| WP-3 | MEU-161 registration (row 2) | WP-1 | shared | `meu-status.yaml`, 09 section, matrix row |
| WP-4 | Static Red, hover Green, the fidelity frame and its E2E Red (rows 3 to 5) | WP-2 | shared | `e2e-harness.test.ts` block, `electron-app.ts`, `settings.test.ts`, `capture-inbox.test.ts` |
| WP-5 | Metrics Red and Green (rows 6 and 7) | WP-4 | shared | the fixture, `capture-text-plates.test.ts`, the pytest, the pins, `capture-segoe-metrics.ts`, `capture-text-metrics.ts` |
| WP-6 | MEU ready, known list emptied, the mini-air run (rows 8 to 10) | WP-5 | shared | 09 Delivered note, `known-failures.json`, `D/ehp-snapshot-10.json`, `C:/Temp/av-kit/e2e-remote/<run-id>/` |
| WP-7 | Registers and hub audit (rows 11 and 12) | WP-6 | shared | Both issues resolved, the residual issue, grouping row 97 |
| WP-8 | Closeout (H1, H2) | WP-7 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!NOTE]
> **Eight briefs are settled on their recommendations under your hand-over** ('proceed with the next session prompt orchestration here like you did the others', 2026-11-18, continuing 'make the decisions always the recommenations'). Read them if you want to overrule one before execution:
>
> - D-1241, one session or two: one session, the hover fix first and independent of the text fix, though the grouping said to split when the diagnosis found product code. This departs from the grouping and changes its scope (M-6, M-8), which the hand-over covers.
> - D-1242, which side to change: the preview's text plate grows to the plate the saved PNG paints (1 or 2 px wider and taller); saved images do not change. This is a visible change in the app (M-5), which the hand-over covers.
> - D-1243, how the preview measures text: a Segoe UI glyph and kerning table in font units with the same rounding FreeType uses and the kerning Pillow applies, so every size is measured rather than scaled from 16 px.
> - D-1244, what to do with the last few pixels: pin the measured residual as limits (at least 1,702 of 2,448 sizes exact, at most 5 more than 1 px off, never more than 2) and register a low issue for it. A pass rule is new policy (M-3), which the hand-over covers.
> - D-1255, the existing tests the bigger plate moves: eight unit tests and one E2E spec pin the old plate's numbers or points derived from it; each changed line is named with its old and new value in §Test pins, which is what makes the change not an M-7 hit.
> - D-1245, the screen scale of the fidelity specs: run them at a scale of 1 on every host, so the dev PC sees what the mini-air sees.
> - D-1246, the hover spec: launch it with a setting that says the device has a mouse, check that before hovering, and, if the mini-air still fails it, keep only that one known entry and the hover issue open.
> - D-1247, how the mini-air runs uncommitted work: a commit object on no branch, made with a temporary index, that leaves your branch, index and status untouched. It departs from "commits only on your direction" in letter (M-6), which the hand-over covers.
>
> **What touches your machines.** Row 1, the Red and Green rows and the gate launch the built app on the dev PC many times (Electron windows open and close; the clipboard specs never run). Row 10 copies a source archive to the mini-air and starts its existing task once, so Electron windows open on that desktop for about 20 minutes. Nothing costs money. Smart App Control, auto sign-in and a GitHub runner stay yours and are not planned (D-1216). No STOP item is held for you.

## Proposed Changes

### Single-statement contracts

| Id | Statement |
|---|---|
| `PREVIEW_FOLLOWS_BAKE` | `textBackgroundBox({ x, y, text, font_size })` returns the rectangle the bake paints for that mark: with Pillow's inclusive `(l, t, r, b)` from `text_plate_box`, `{ x: l, y: t, width: r - l + 1, height: b - t + 1 }`, within the residual AC-161.5 pins. |
| `PLATE_UNITS` | The box is computed from `SEGOE_UI_GLYPH_UNITS` (font units at the `ls` anchor) with FreeType's arithmetic: `FT_MulFix` by `size * 2048`, each extent and advance rounded as `(v + 32) >> 6`, the pen moved between two known glyphs by the pair's `SEGOE_UI_KERN_UNITS` step (`kernStep`), lines at `y + i * segoeLinePitchPx(size)` with the baseline `segoeAscentPx(size)` below the line top; no 16 px table and no fractional scale remain. |
| `FIDELITY_FRAME` | The three fidelity specs (`AC-82.6`, `AC-102.19`, `AC-102.20`) launch with `--force-device-scale-factor=1`, so each host measures at a device scale of 1; no other spec gets the flag. |
| `HOVER_CAPABLE` | `AC-126.8` launches with `--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4` and asserts that `(hover: hover)` matches before it hovers; no other spec gets the flag. |
| `SNAPSHOT_NO_REF` | The mini-air run's commit is `HEAD` plus the named working files, written with a temporary `GIT_INDEX_FILE` and `git commit-tree`, every git call under `GIT_OPTIONAL_LOCKS=0`, every named path differing from `HEAD`; every ref, the index, `HEAD` and `git status` are byte-for-byte the same after it, and the author is the noreply identity. |
| `KNOWN_EMPTY` | After row 9, `known-failures.json` holds no `known` entry, and its two `skip` entries and its `label` keep their row-0 values. |
| `PINS_NAMED` | Every changed or added line in an existing test file is one that §Test pins names, at the place it names: `diff-check.py` rebuilds each file from its row-0 copy by the named replacements, removals, inserted hunks (each hunk's exact lines right after or before one exact anchor line inside its named block) and named blocks (a begin anchor, the block's first line, and an end anchor, the first later line at its indent that starts with `}`), and the file must equal that, line for line. An added line that no pin names fails in every file, wherever it sits (round 1 F1). Every other line keeps its bytes and its line ending. The lines inside a named block, and the new test files, are new test code: each is proved by its Red and the test hash recorded at that Red, which holds to the gate. |
| `LOCAL_HOST_DETAILS` | The host alias, account, host folder and task path appear only in the untracked local config and in receipts under `C:/Temp/av-kit/`, never in a tracked file, the handoff or a commit message. |

### The diagnosis (row 1, before any change)

Row 1 writes `D/ehp-diagnosis-1.txt`, built by Python from receipts (Session 95 RULE-3), before any tracked file changes. It names the side that moves, with numbers from both hosts (AC-161.1, AC-161.2):

- **The mini-air.** `boxes-report.py` over both tool runs' `host/report.json`: the three specs `unexpected`, the preview and bake plates and inks, the gap per side `[0, 0, 2, 0]` (`AC-82.6`, `AC-102.20`) and `[0, 0, 2, 1]` (`AC-102.19`), the origins; `AC-126.8` `unexpected` with `rgb(21, 94, 117)`.
- **The dev PC.** `e2e-subset.ps1 -Set fidelity` at the baseline tree: the three specs `expected`, gap `[1, 1, 1, 1]`. `run-probe.ps1 -Probe fidelity`: at a scale of 1 the 30 px plate gives the mini-air's right gap of 2 and the 32 px plate 0 at all three origins, so the preview's plate width moves; the bake, the ink and the origin do not.
- **The bake's width rule.** `adapter.text_plate_box(20, 30, 'Hi', 32)` is inclusive `(20, 42, 51, 65)`, painted 32 by 24 by `_apply_text`; the preview gives 30 by 24 today.
- **The hover cause.** `run-probe.ps1 -Probe hover`: native, hover-none and capable launches with their media match and colour; then `hover-spec-red.py`, the real `AC-126.8` through copies with the planned `args` option: native passes, hover-none fails at the hover expectation with `rgb(21, 94, 117)` (M3).
- **The font.** Both hosts' `segoeui.ttf` SHA-256 from the plan-time receipts, equal, and the dev PC's read again (a different value is S2).

The receipt's last line is `moving side: preview plate width (textBackgroundBox); hover: the host's pointer capability`. A diagnosis that names another side (the bake, the origin, the font) is S5: stop and re-plan, because every later row assumes this one.

### The glyph table: `ui/src/renderer/src/features/capture/capture-segoe-metrics.ts` (CRLF stays CRLF)

Generated, never hand-edited: `segoe-units.py --write` (row 7) writes the whole file as bytes, CRLF, UTF-8 with no BOM. It keeps the `SEGOE_UNITS` head (`SEGOE_UI_UNITS_PER_EM = 2048`, `SEGOE_UI_ASCENDER = 2210`, which `AC-82.1` reads) and replaces the 16 px table (`SEGOE_LA_BASE_SIZE`, `SegoeGlyph`, `SEGOE_LA_GLYPHS`) with `SegoeGlyphUnits`, `SEGOE_UI_GLYPH_UNITS` and `SEGOE_UI_KERN_UNITS`: 95 glyph entries, one per printable ASCII character (0x20 to 0x7E), each `{ l, t, r, b, adv }` in font units at the `ls` anchor (`t` negative above the baseline), from Pillow's FreeType at 2,048 px (`getbbox(ch, anchor='ls')`, `getlength(ch)`), and the 372 non-zero kerning pairs among them in font units (`FT_Get_Kerning` unscaled, expert pass M1). The comment names the generator path and the font's SHA-256, so `segoe-units.py --check` fails on a different font. Every value is whole (a fraction stops the generator). The plan-time output (`ehp-plan-segoe-units-k.ts`, 10,335 bytes, 157 lines, SHA-256 prefix `f93720ecdc6cb72d`) is what row 7 must reproduce; its first glyphs are `" ": { l: 0, t: 0, r: 561, b: 0, adv: 561 }` and `"!": { l: 0, t: -1434, r: 582, b: 18, adv: 582 }`.

The two old names are imported only by `capture-text-metrics.ts:5` and `capture-text-lines.behavior.test.ts:14` (`grep -rn SEGOE_LA_ ui packages mcp-server/src`, plan time); both lose them in rows 6 and 7. No Python file reads the TS table.

### The plate: `ui/src/renderer/src/features/capture/capture-text-metrics.ts` (CRLF stays CRLF)

Row 7 changes only the import line (`:5`), `FALLBACK_GLYPH` (`:51`) and the body and comment of `textBackgroundBox` (`:53-93`), and adds `mulFix`, `pixRound` and `kernStep` before it (the comments elided with `...` are written whole). `segoeAscentPx`, `svgTextBaselineY`, `TEXT_LINE_GAP_PX`, `segoeLinePitchPx`, `textLines` and the two types keep their bytes.

```ts
import { SEGOE_UI_ASCENDER, SEGOE_UI_GLYPH_UNITS, SEGOE_UI_KERN_UNITS, SEGOE_UI_UNITS_PER_EM } from './capture-segoe-metrics'

/** The unknown-glyph box in font units: the old 16 px fallback (l 0, t 7, r 8, b 18, adv 8 at `la`) at 128 units a px. */
const FALLBACK_GLYPH_UNITS = { l: 0, t: -1408, r: 1024, b: 0, adv: 1024 }

/** FreeType's FT_MulFix: (a * b + 0x8000) / 0x10000, rounded half away from zero; exact below 2^53. */
function mulFix(a: number, b: number): number {
  const magnitude = Math.floor((Math.abs(a) * Math.abs(b) + 0x8000) / 0x10000)
  return a < 0 !== b < 0 ? -magnitude : magnitude
}

/** FreeType's FT_PIX_ROUND of a 26.6 value, in whole px: (v + 32) >> 6, written without a 32-bit shift. */
function pixRound(value26: number): number {
  return Math.floor((value26 + 32) / 64)
}

/** The bake's kerning step for a pair (Pillow's basic layout over FT_Get_Kerning): ... rounded to whole px. */
function kernStep(pair: string, size: number, scale: number): number {
  const units = SEGOE_UI_KERN_UNITS[pair]
  if (!units) return 0
  let kern26 = mulFix(units, scale)
  if (size < 25) {
    const magnitude = Math.floor((Math.abs(kern26) * size + 12) / 25)
    kern26 = kern26 < 0 ? -magnitude : magnitude
  }
  return pixRound(kern26)
}

/** TEXT_PLATE_UNITS (MEU-161, D-1243) and PREVIEW_FOLLOWS_BAKE (D-1242): ... the box is `r - l + 1` by `b - t + 1`. */
export function textBackgroundBox(input: TextMetricsInput): TextBackgroundBox {
  const size = Math.max(1, input.font_size)
  const scale = (size * 64 * 0x10000) / SEGOE_UI_UNITS_PER_EM
  const ascent = segoeAscentPx(size)
  const pitch = segoeLinePitchPx(size)
  const multiline = input.text.includes('
')
  const lines = multiline ? textLines(input.text) : [input.text.length > 0 ? input.text : ' ']
  // left, top, right, bottom: the inclusive pixel extents, as Pillow's textbbox reports them
  ...
  lines.forEach((line, index) => {
    const lineTop = input.y + index * pitch
    if (line.length === 0) { /* the point (input.x, lineTop) */ return }
    const baseline = lineTop + ascent
    let pen26 = 0
    let previous = ''
    for (const ch of line) {
      const known = SEGOE_UI_GLYPH_UNITS[ch]
      if (previous && known) pen26 += kernStep(previous + ch, size, scale)
      const glyph = known ?? FALLBACK_GLYPH_UNITS
      const origin = input.x + pixRound(pen26)
      left = Math.min(left, origin + pixRound(mulFix(glyph.l, scale)))
      top = Math.min(top, baseline + pixRound(mulFix(glyph.t, scale)))
      right = Math.max(right, origin + pixRound(mulFix(glyph.r, scale)))
      bottom = Math.max(bottom, baseline + pixRound(mulFix(glyph.b, scale)))
      pen26 += pixRound(mulFix(glyph.adv, scale)) * 64
      previous = known ? ch : ''
    }
  })
  return { x: left, y: top, width: Math.max(1, right - left + 1), height: Math.max(1, bottom - top + 1) }
}
```

**Kerning** (expert pass M1). Pillow here has no raqm, so its basic layout moves the pen by `FT_Get_Kerning` for each pair, shrunk below 25 px; it adds the rounded px count to a pen kept in 1/64 px, so a pair moves the glyph by the step rounded at the next `pixRound`, which the model mirrors. Kerning applies only between two known glyphs. A Pillow built with raqm, or a Pillow change to its layout, moves the bake's plates, so the fixture head records `pillow` and `raqm` and `plate-fixture.py --check` fails on either (AC-161.4).

`SEGOE_UI_ASCENDER` stays imported because `segoeAscentPx` reads it. The scale is an integer for every whole size (`size * 2048`), and the products stay below 2^53 up to size 500 (`1676 * 500 * 2048 + 0x8000` is about 1.7e9). The transforms store a whole `font_size` (`capture-transform.ts:145` rounds it); the old function did not round its input either, and for a fraction the model still returns whole pixels through `pixRound`. The function stays pure, synchronous and allocation-light; it runs on each render of a text mark and on each pointer move over one (the hit test), with at most the mark's characters in its loop, as now.

**What a user sees.** Each text mark's plate in the preview grows by one pixel on the right and one at the bottom at most sizes (`'Hi'` at 16: 15 by 12 becomes 16 by 13; at 32: 30 by 24 becomes 32 by 24), and by up to a few pixels for long texts at large sizes, where the 16 px table drifted (plan-time breadth: the old function is up to 29 px short). The plate now covers what the saved PNG paints. The handles of a selected text mark sit on the plate's corners (`capture-transform.ts:125`), so they move with it; a corner drag scales about the new opposite corner (`AC-101.1`'s grown mark needs the handle at 42, 32 instead of 40, 30 to reach size 32). The saved image, the sidecar and every stored value are unchanged: only the preview's rectangle changes.

### The launch option: `ui/tests/e2e/electron-app.ts` (LF stays LF)

`LaunchOptions` (`:35`) gains one field with its comment, a named hunk of these two lines right after its last field `  pointerShield?: false` (`:41`), and `launchElectron` (`:110`) passes it after the main entry (two named replacements):

```ts
  /** CHROMIUM_ARGS (Session 97): extra Chromium switches after the main entry; FIDELITY_FRAME and HOVER_CAPABLE use it. */
  args?: readonly string[]
...
export async function launchElectron({ main, env = {}, pointerShield, args }: LaunchOptions = {}): Promise<ElectronApplication> {
...
      args: ['-r', MAIN_ERROR_WATCH, main ?? DEFAULT_MAIN, ...(args ?? [])],
```

Electron reads Chromium switches anywhere on its command line, and the main entry ignores trailing arguments (plan-time `hover-probe.mjs` and `fidelity-probe.mjs` pass them the same way to their own app). The default launch gets no extra argument, so every other spec launches exactly as now. `e2e-harness.test.ts` `AC-2` (one launcher name) and `AC-19` (the scratch check before the launch call) keep passing: the launch call and `requireScratchAppData(env` keep their single occurrence and their order.

### The fidelity frame: `ui/tests/e2e/capture-inbox.test.ts` (LF stays LF)

- Right after the last import line (`import { pointerOn, settle, settledBox, windowSettled } from './pointer-settle'`, `:9`), one named hunk of three lines: a blank line; the comment line `// FIDELITY_FRAME (Session 97, D-1245): the fidelity specs measure at a device scale of 1 on every host, the second host's native scale; at 2 the dev PC halves a pixel gap and hid the 2 px plate drift.`; and `const FIDELITY_ARGS = ['--force-device-scale-factor=1'] as const`.
- `launchApp()` (`:68`) becomes `launchApp(args: readonly string[] = [])` and passes `args` to `launchElectron` (one inserted line, `    args,`, right after `  return launchElectron({` inside `launchApp`).
- `AC-82.6 TEXT_PIXEL_ORACLE` (`:2243`) and `fidelityViews(` (`:2301`, used by `AC-102.19` and `AC-102.20`) call `launchApp(FIDELITY_ARGS)`.
- Every other `launchApp()` call in the file stays as it is. No fidelity expectation line changes: the specs' own 1 px rule now meets the real pixel grid on every host.
- `AC-101.6` (`:3078`, H1): at size 2 on the 8 by 8 sample the new plate is 2 rows tall, so `'Note'` from (3, 6) would end below the image; the mark moves to (3, 4), where the `'Done'` plate {3, 6, 5, 2} keeps its se corner on the image corner (8, 8), the drag premise. Written at row 5 (so `diff-check.py --expect-changed` covers the file once), first run at row 7 (D-1242, D-1255; §Test pins).

### The hover capability: `ui/tests/e2e/settings.test.ts` (CRLF stays CRLF)

- Right after the import line `} from './theme-probe'` (`:20`), one named hunk of three lines: a blank line; the comment line `// HOVER_CAPABLE (Session 97, D-1246): AC-126.8 checks a hover colour, and Tailwind v4 applies hover: only under (hover: hover); this states a mouse-capable device so a host with no pointing device (the second host) runs the same rule.`; and `const HOVER_CAPABLE_ARGS = ['--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4'] as const`.
- `launchApp()` (`:22`) gains the same `args` parameter and the same inserted `    args,` line right after `  return launchElectron({`, and `AC-126.8 light accent paints the ruled colours` (`:700`) calls `launchApp(HOVER_CAPABLE_ARGS)`.
- In `AC-126.8`, right before the line `  await lightBtn.hover()`, one inserted line, the precondition as a hard assertion: `  expect(await page.evaluate(() => matchMedia('(hover: hover)').matches), 'HOVER_CAPABLE: (hover: hover) matches before the hover').toBe(true)`. It fails the test; it is never a skip, a `return` or a guard around the rest. A host where the setting does not take effect then fails here, named, rather than as a colour timeout or a silent pass. No `return`, `test.skip` or `test.fixme` sits between `launchApp(HOVER_CAPABLE_ARGS)` and the colour assertion (AC-161.9 reads this; round 1 F1).
- No other spec, file or line changes. CRLF is kept on every line (row 4's `eol-check.py`).

### The known list: `tools/e2e_host/known-failures.json` (LF stays LF)

Row 9 removes the four `known` entries and nothing else: `label` (`mini-air`) and the two `skip` entries keep their row-0 values (`KNOWN_EMPTY`). The file is written by a row-9 Python command that loads the JSON, checks the row-0 hash, deletes the four entries by their file and AC id, asserts the rest equals the row-0 data without them, and writes LF bytes with the file's own indent and final newline (Session 83 RULE-3). `load_known` (`tools/e2e_remote.py:391-402`) requires only that `known` and `skip` are lists of objects, so an empty `known` list loads, and `summarize` reads the register only when entries remain (`:796`). `known_now_passing` lists only tests that match an entry, so the run itself, with the emptied list, cannot show the four passing; row 10 therefore summarizes the same report a second time with `--known` set to the row-0 copy, while both issues are still `open` (D-1253). Row 9 proves the list's effect before the run: `summarize` on the `a43cdb2` mini-air report exits 40 naming the four with the emptied list, and 0 with the row-0 copy.

### The tests

**New: `ui/tests/e2e/fixtures/capture-text-plates.json`** (LF; row 6; `plate-fixture.py --write`; 39,108 bytes at plan time, SHA-256 prefix `36b15443d46282a6`). A head (`generator`, `font`, `font_sha256`, `pillow`, `raqm`, and `box`, the rule "[x, y, width, height] painted by the bake: adapter.text_plate_box (l, t, r, b) as [l, t, r - l + 1, b - t + 1]") and two sections, each with its origin `x` and `y`, its `sizes` and its `cases`: `breadth`, 18 texts at (20, 30) by 136 sizes (1 to 128, 160, 177, 200, 215, 256, 354, 400, 500), 2,448 boxes, the last four texts dense in kerning pairs; `matrix`, 10 multi-line texts at (10, 20) by sizes 8, 16, 32 and 64, 40 boxes. Each case is `{ "text": ..., "boxes": [...] }` with one `[x, y, width, height]` per size, in the order of `sizes`.

**New: `ui/tests/unit/capture-text-plates.test.ts`** (LF; row 6; Vitest, node environment), `describe('MEU-161 text plate metrics')`:

- `AC-161.3 SEGOE_UI_GLYPH_UNITS holds the 95 printable ASCII glyphs in font units`: loaded by dynamic `import()` inside the test (so the Red is an assertion on a missing export, not a collection error); 95 keys, `' '` to `'~'`; every value an integer; `SEGOE_UI_UNITS_PER_EM` 2048 and `SEGOE_UI_ASCENDER` 2210; `SEGOE_UI_KERN_UNITS` with 372 integer entries, each key two printable ASCII characters; and `'SEGOE_LA_GLYPHS' in mod` is false (L2: an `in` test, so an export of `undefined` still fails).
- `AC-161.5 PREVIEW_FOLLOWS_BAKE breadth`: for every breadth case, the per-side difference between `textBackgroundBox` and the fixture (left `x`, top `y`, right `x + width - 1`, bottom `y + height - 1`); at least 1,702 cases exact on all four sides, at most 5 cases over 1 px on any side, none over 2. The test prints the counts and every case over 1 px.
- `AC-161.5 PREVIEW_FOLLOWS_BAKE matrix`: 36 of the 40 cases exact; the four others are named with their model box and differ by 1 px on one side: `'Hello\nW\ngy'` at 32 (height 111 against 110), at 64 (211 against 212), `'i\nWWWW'` at 8 (width 29 against 30), `'Hello'` at 8 (height 7 against 8). A fifth difference, or a change in one of the four, fails.
- `AC-161.5 PREVIEW_FOLLOWS_BAKE the fidelity marks`: `'Hi'` at 32 at (20, 30) is `{ x: 20, y: 42, width: 32, height: 24 }` and `'Hi\n\nHi\n'` at 32 at (20, 16) is `{ x: 20, y: 28, width: 32, height: 106 }`, the bake's painted plates of the E2E fixture.

**New: `tests/unit/test_capture_text_plates.py`** (LF; row 6; pytest, `@pytest.mark.unit`), `test_ac_161_6_plate_fixture_matches_pillow`: when the local `segoeui.ttf` SHA-256 equals the fixture's `font_sha256`, every one of the 2,488 cases equals the painted box from `adapter.text_plate_box` (the same reading as `AC-102.7` at `test_capture_text_lines.py:164`); when it differs (a CI runner with another font build), only the fixture's own recorded values are checked (L3): its shape (head keys, 2,448 breadth and 40 matrix boxes, four whole numbers each) and its recorded `'Hi'` at 16 at (20, 30), `[20, 36, 16, 13]`; the live `text_plate_box` is never compared there, because another font paints other boxes. The test prints that the font differs. It never skips (AC-161.6). The comparison lives in a module-level helper, `fixture_mismatches(path)`, which returns every case whose box differs from the bake, so row 6 can run it on a changed copy. It passes at Red, because it checks the fixture against the bake, not the preview; it guards the fixture.

**Edited:** `capture-text-metrics.test.ts`, `capture-transform.test.ts`, `capture-text-lines.behavior.test.ts`, `capture-page.behavior.test.ts`, `e2e-harness.test.ts` and the `AC-101.6` lines of `capture-inbox.test.ts`, each named in §Test pins.

**`ui/tests/unit/e2e-harness.test.ts`** (LF; row 3), a new `describe('Session 97 host parity')` after the Session 78 block, reading the files as text the way `AC-19` does. It is one named block: its begin anchor is its first line, `describe('Session 97 host parity', () => {`; its end anchor is the first later `})` at column 0; it sits right after the Session 78 block's closing `})` and one blank line, and no other line of the file changes:

- `AC-161.8 FIDELITY_FRAME the three fidelity specs launch at a device scale of 1, and only they`: `electron-app.ts` declares `args?: readonly string[]` in `LaunchOptions` and holds `main ?? DEFAULT_MAIN, ...(args ?? [])` once; `capture-inbox.test.ts` holds `'--force-device-scale-factor=1'` once, in `FIDELITY_ARGS`, and `launchApp(FIDELITY_ARGS)` exactly twice, once inside the `AC-82.6 TEXT_PIXEL_ORACLE` test and once inside `fidelityViews(`; no other file under `ui/tests/e2e` holds `force-device-scale-factor`.
- `AC-161.9 HOVER_CAPABLE AC-126.8 states a mouse-capable device and checks it before the hover`: `settings.test.ts` holds the capable `--blink-settings` string once, in `HOVER_CAPABLE_ARGS`, and `launchApp(HOVER_CAPABLE_ARGS)` once, inside the `AC-126.8` test; that test holds the precondition as a hard assertion, `matchMedia('(hover: hover)')` inside an `expect(` that ends `.toBe(true)`, before its first `.hover(`; and no line from `launchApp(HOVER_CAPABLE_ARGS)` to `toHaveCSS('background-color', 'rgb(22, 78, 99)')` is a `return` or holds `test.skip` or `test.fixme` (round 1 F1); no other file under `ui/tests/e2e` holds `blink-settings`.

Both fail by assertion at row 3 (the strings are absent), and pass after rows 4 and 5.

### Test pins

Each pin is cited by its file, line and description; `diff-check.py` enforces the list (`PINS_NAMED`). The AC ids in this table that do not start with `AC-161.` belong to MEU-59, MEU-82, MEU-101, MEU-102, MEU-126 and Session 78 (Session 83 RULE-1); this plan changes their lines only as named. The changed values move by design (D-1242, D-1255): the plate grows to the painted one, and each new value is the planned function's output, proven at plan time (`ehp-plan-h1-pins.txt`: the touched files 148 of 148 with these pins and the planned function, 9 failures with the old one).

| Pin | What it checks | After this change |
|---|---|---|
| `capture-text-metrics.test.ts:12-18` (`AC-59.19 TEXT_MODULE`), `toEqual({ x: 10, y: 26, width: 15, height: 12 })` | `'Hi'` at 16 at (10, 20) | **Changed value (M-7, named).** Old `width: 15, height: 12`; new `width: 16, height: 13`, the bake's painted plate (`adapter.text_plate_box(10, 20, 'Hi', 16)` is `(10, 26, 25, 38)`). Anchors and `y` unchanged |
| `capture-transform.test.ts:170` (`AC-101.1 TEXT_SCALE`), `:189` `toEqual({ x: 10, y: 6, width: 15, height: 12 })` | The edge mark's plate | **Changed value.** New `width: 16, height: 13` |
| `capture-transform.test.ts:190` `at(40, 30)` and `:192` `toEqual({ x: 10, y: 6, width: 30, height: 24 })` | A corner drag that grows the edge mark to size 32 | **Changed values.** The handle moves to `at(42, 32)` (twice the new plate from the anchor, so the drag still lands on size 32; `ehp-plan-transform.txt`: at 40, 30 it gives 30), and the grown plate is `width: 32, height: 24`. `:191` (`{ x: 10, y: -6, font_size: 32 }`) is unchanged. Every other line of `AC-101.1` (twice the plate, the anchors, the four corner cases at `:193` on) is unchanged and passes with the new box (`ehp-plan-transform.txt`, 26 `ok` lines) |
| `capture-text-lines.behavior.test.ts:14` (the `SEGOE_LA_BASE_SIZE, SEGOE_LA_GLYPHS` import), `:53` `MATRIX_TEXTS`, `:54` `FALLBACK`, `:56-84` `unionOracle` | The line-union oracle over the 16 px table | **Removed** (the lines from `const MATRIX_TEXTS` up to `type Shot`, and the import). The oracle re-implemented the old function; the matrix moves to the Pillow fixture and `AC-161.5`, against the bake itself |
| `capture-text-lines.behavior.test.ts:315-337` (`AC-102.10 textBackgroundBox equals each text_plates box and the line-union oracle; a trailing \n reaches the empty line`) | The 16 `text_plates` of `capture-geometry.json` as `r - l` by `b - t`; the oracle matrix; `'Hi'` ending at 38 and `'Hi\n'` at 42 | **Replaced block (M-7, named; `Wildcard`: begin anchor the new title line, end anchor its first later `  })`; its lines are proved by the row-6 Red and `ehp-test-sha-6.json`), titled `AC-102.10 textBackgroundBox equals each painted text_plates box; a trailing \n reaches the empty line`.** The 16 plates as `r - l + 1` by `b - t + 1`: 15 exact, and `'Hi\n'` at 24 at its fixture origin named as the one residual, `{ x: 10, y: 28, width: 24, height: 23 }` against the painted `{ x: 10, y: 29, width: 24, height: 22 }` (top 1 px higher, bottom equal); the trailing pins become 39 and 43 (each one more, the painted bottom row). `capture-geometry.json` keeps its bytes |
| `e2e-harness.test.ts` (whole file) | Session 78's harness checks | **One named new block** (`NewBlock`): begin anchor `describe('Session 97 host parity', () => {`, end anchor its first later `})` at column 0, placed right after the Session 78 block's closing `})` (`:135`) and one blank line. Every existing line keeps its bytes, and any other added line fails. The block's own lines are proved by the row-3 Red and `ehp-test-sha-3.json` |
| `capture-hit-test.test.ts:140` (`AC-60.3`) | The plate's centre is hittable | Unchanged; passes with the new box (centre 18, 32.5 inside `{ 10, 26, 16, 13 }`) |
| `capture-page.behavior.test.ts:932` (`AC-82.4`), `:959`, `:960`, `:962` | The rendered plate's SVG `width`, `height` and the hit range | **Changed values (M-7, named).** `'15',` to `'16',`; `'12',` to `'13',`; the comment `x 50..125, y 130..190` to `x 50..130, y 130..195` |
| `capture-page.behavior.test.ts:3159` (the MEU-101 describe comment) | The corner plate in CSS | **Changed comment.** `{1,2,5,1}: CSS (25,50)-(150,75)` to `{1,3,4,2}: CSS (25,75)-(125,125)` |
| `capture-page.behavior.test.ts:3211` (`AC-101.2`) | A double-click inside the plate reopens the mark | **Changed point.** `doubleClickAt(surface, 87, 62)` to `(surface, 75, 100)`, the new plate's centre |
| `capture-page.behavior.test.ts:3264` (`AC-101.4 a selected text mark has four corners`), `:3270`, `:3271`, `:3277`, `:3279`, `:3280` | The se handle, its drag and the scaled mark | **Changed values.** The comment `image (6,3), CSS (150,75); CSS (175,100) is image (7,4): ratio max(6/5, 2/1)` to `image (5,5), CSS (125,125); CSS (150,175) is image (6,7): ratio max(5/4, 4/2)`; `drag(surface, 150, 75, 175, 100)` to `drag(surface, 125, 125, 150, 175)`; `(3.5,2), CSS (87.5,50)` to `(3,3), CSS (75,75)`; `cssX: 87.5,` to `cssX: 75,`; `cssY: 50,` to `cssY: 75,` |
| `capture-page.behavior.test.ts:3292` (`AC-101.4 after a corner scale`), `:3296` | The same drag | **Changed call.** `drag(surface, 150, 75, 175, 100)` to `drag(surface, 125, 125, 150, 175)` |
| `capture-page.behavior.test.ts:3495` (`AC-59.19` render), `:3536`, `:3537` | The rendered plate's size | **Changed values.** `toBe('15')` to `toBe('16')`; `toBe('12')` to `toBe('13')` |
| `capture-inbox.test.ts:3078` (`AC-101.6`), `:3091`, `:3098`, `:3099`, `:3111`, `:3113`, `:3114` | A text mark's corner drag on the 8 by 8 sample | **Changed values (row 5).** `clickSampleImagePoint(page, 3, 6)` to `(page, 3, 4)`; the comment `from (3,6) has the plate {3,7,4,1}; its centre is image (5,7.5).` to `from (3,4) has the plate {3,6,6,2}; its centre is image (6,7).`; `sampleImagePagePoint(page, 5, 7.5)` to `(page, 6, 7)`; `'Done', x: 3, y: 6, font_size: 2` to `y: 4`; `` `Done` has the plate {3,7,5,1} `` to `{3,6,5,2}`; `the nw corner (3,7) out` to `(3,6) out` |
| `capture-text-metrics.test.ts:22-48` (`AC-82.1`, `AC-82.3`) | `SEGOE_UNITS` and the ascent | Unchanged and passing: the head and `segoeAscentPx` keep their values |
| `tests/unit/test_capture_text_lines.py:164` (`AC-102.7`) | `capture-geometry.json` against Pillow | Unchanged: the bake and the fixture do not change |
| `capture-inbox.test.ts:2243`, `:2301` | `launchApp()` in `AC-82.6` and `fidelityViews` | **Changed call (named):** `launchApp(FIDELITY_ARGS)`. No expectation line changes |
| `settings.test.ts:700` (`AC-126.8`) | `launchApp()` and the hover colour | **Changed call and one inserted hard precondition (named):** `launchApp()` to `launchApp(HOVER_CAPABLE_ARGS)`; the line `  expect(await page.evaluate(() => matchMedia('(hover: hover)').matches), 'HOVER_CAPABLE: (hover: hover) matches before the hover').toBe(true)` right before `  await lightBtn.hover()`, inside `AC-126.8`. The colour expectations are unchanged |
| `settings.test.ts:20` (after `} from './theme-probe'`) | The imports | **Inserted hunk (named):** a blank line, the `// HOVER_CAPABLE (Session 97, D-1246): ...` comment line and `const HOVER_CAPABLE_ARGS = [...] as const` (§The hover capability) |
| `capture-inbox.test.ts:9` (after the `./pointer-settle` import) | The imports | **Inserted hunk (named):** a blank line, the `// FIDELITY_FRAME (Session 97, D-1245): ...` comment line and `const FIDELITY_ARGS = ['--force-device-scale-factor=1'] as const` (§The fidelity frame) |
| `capture-inbox.test.ts:68`, `settings.test.ts:22` (`launchApp`) | The scratch app data | **Changed signature:** an optional `args`, passed through by one inserted line, `    args,`, right after `  return launchElectron({` inside `launchApp`; the default keeps every other launch as it is |
| `electron-app.ts:35`, `:110`, `:134` | The launcher | **Changed:** `args` in the `launchElectron` destructuring and the spread (two named replacements), and one inserted hunk right after `  pointerShield?: false` (`:41`) in `export interface LaunchOptions`: the `CHROMIUM_ARGS` comment line and `  args?: readonly string[]`. The default argv is unchanged |

**Insertions (round 1 F1).** In every file of this table, an added line passes only as a line of a named hunk at its anchor or inside a named block; `diff-check.py` rebuilds the file from its row-0 copy by these rules and requires equality, so an unnamed added line (such as an early `return` before the `AC-126.8` precondition), a hunk at another place or a missing hunk fails. A new test file is checked by its Red and its frozen test hash, and `diff-check.py` only allows its path.

Any other existing test that fails after Green is S3. A Green that needs a test change not named here is S3 and M-7: stop.

### Plan-local files (written at plan time)

This folder already holds, all LF, ruff-clean (Python), with no host detail:

| File | Purpose | Rows |
|---|---|---|
| `boxes-report.py` | Prints the fidelity `boxes` lines and the plate gap per side from Playwright JSON reports | 1, 5, 7, 10 |
| `fidelity-probe.mjs`, `hover-probe.mjs`, `probe-app.cjs`, `run-probe.ps1` | The plan-time probes, rerun in the diagnosis; they launch only `probe-app.cjs` and close what they launched | 1 |
| `e2e-subset.ps1` | Runs the `fidelity`, `hover` or `touched` subset with a JSON report; never the clipboard specs | 1, 4, 5, 7, H1-2 |
| `segoe-units.py` | Generates, writes or checks the glyph table (`--out`, `--write`, `--check`) | 0, 7, H1-2 |
| `plate-fixture.py` | Generates, writes or checks the Pillow fixture | 0, 6, H1-2 |
| `diff-check.py` | `PINS_NAMED`: each edited test file rebuilt from its row-0 copy by the named rules and compared line for line, with a selftest | 0, 6, 7, H1-2 |
| `snapshot-commit.py` | `SNAPSHOT_NO_REF`: the commit on no ref, its verify, its selftest | 0, 10, H1-2 |
| `hover-spec-red.py` | The real `AC-126.8` under hover-none through copies with the planned `args` option, no tracked file written (M3) | 1 |
| `meu-register.py` | MEU-161 in `meu-status.yaml`, the Phase 9 section and the matrix, with a dry run and a selftest | 0, 2, H2-2 |
| `host-details-scan.py` | `LOCAL_HOST_DETAILS`: scans this session's tracked files for the local config's values, printing key names only | 0, 12, H1-2 |

Copied at row 0 (Session 96 RULE-3, each from the newest ruff-clean folder that holds it, named in its docstring): `identity.py`, `eol-check.py`, `red-check.py` and `host-load.ps1` from `2026-11-18-e2e-remote-host/`; `issue-resolve.py` from `2026-11-17-video-tail-frame/` (it carries `meu_links` and `root_cause`); `flake-run.py` from `2026-11-17-e2e-pointer-flakes/` (its receipt folder set to `D`). Each copy changes only its scope lists, its scratch folder and its docstring's first paragraph, and its selftest passes at row 0. Row 0 also writes `baseline.ps1`; H1-2 writes `session-gate.ps1`.

**No partial file (Session 95 RULE-1).** `plate-fixture.py` and `segoe-units.py` write through `write_new`: `--out` creates its file exclusively and removes it on a write error; `--write` writes `<file>.ehp-tmp` and replaces the tracked file in one `os.replace`, so an error keeps the old bytes. `EHP_WRITE_FAULT=1` injects the error after the create. Plan time (`ehp-plan-fault.txt`): with the fault, `--out` exits 1 and leaves no file, for both scripts; an existing `--out` file refuses with exit 1 and keeps its bytes; a normal `--out` exits 0. The `--write` fault is tested at rows 6 and 7 (exit 1, the tracked file's hash unchanged, no `.ehp-tmp` left), because it touches the tracked tree.

### Boundary Inventory

| Boundary | Input | Owner | Refusal |
|---|---|---|---|
| `textBackgroundBox` input | `{ x, y, text, font_size }` from a stored text mark | `capture-text-metrics.ts` | None: an unknown character uses `FALLBACK_GLYPH_UNITS`, a size below 1 is 1, an empty text measures one space (as now). No new failure path |
| The glyph table | `SEGOE_UI_GLYPH_UNITS`, generated | `segoe-units.py` | `--check` exit 1 on any byte difference, a different font SHA-256 or a fraction (AC-161.3) |
| The Pillow fixture | `capture-text-plates.json` | `plate-fixture.py` | `--check` exit 1 on a difference, font or Pillow change (AC-161.4); `test_capture_text_plates.py` on CI (AC-161.6) |
| Generator writes | `--out FILE`, `--write` | `write_new` in both generators | `--out` that exists: exit 1, its bytes kept; a write or close error after the create: exit 1, no file (`--out`) or the old bytes (`--write`), no `.ehp-tmp` left (Session 95 RULE-1; AC-161.10 sentinels) |
| `LaunchOptions.args` | A spec's Chromium switches | `electron-app.ts` | None at runtime: test-only; AC-161.8 and AC-161.9 bind which specs pass which switch |
| Snapshot commit | `HEAD`, the named working paths, `git config` identity | `snapshot-commit.py` | Exit 1 on a non-noreply author, an existing `--out`, a guard change (refs, index, `HEAD`, status), `INDEX_CHANGED` (the index hash after the first status differs at the end), `UNCHANGED_SCOPE` (a named path equal to `HEAD`) or a verify mismatch; exit 2 on usage (AC-161.10) |
| Remote run | The snapshot commit | `tools/e2e_remote.py run` (Session 96, unchanged) | Its exit table: 20 to 24 host busy or locked (S10), 25 to 34 and 10, 11 (S11), 40 an unlisted failure (S12), 32 a stale known list |
| Remote lock release | `release <run-id>` | `tools/e2e_remote.py release` (Session 96) | Session 96 RULE-1: a final-release failure (exit 10 or 11, `lock_kept`) leaves the lock; this plan adds no lock code. Row 10's stop handles it: record it, run `release` with this session's own run id once more, and never release another run's lock (S11) |
| Known list | `known-failures.json` | Row 9's Python | A row-0 hash mismatch or any change beyond the four entries stops the row (AC-161.11) |
| Registers | `known-issues.yaml`, `meu-status.yaml`, the grouping row | `tools/issue_triage.py`, `issue-resolve.py`, `meu-register.py`, `tools/meu_status.py` | Each tool's own refusals; a hash mismatch against row 0 is S4 |
| Receipts | `D/` and `C:/Temp/av-kit/e2e-remote/<run-id>/` | Each row | A receipt parsed later is written by Python (Session 95 RULE-2/3) |

No API route, OpenAPI document, MCP tool shape, backend service, persisted setting, stored annotation or database schema changes, so M-4 stays clear. The bake (`adapter.py`) is not edited. Nothing reads user data: the specs use a scratch `AVKIT_APP_DATA` and the fake E2E backend, and the probes load no av-kit code.

### Acceptance Criteria

Each AC has an observable, the call chain it runs through and a negative oracle. AC-161.3, AC-161.5, AC-161.8 and AC-161.9 are Vitest tests that fail at Red (FAIL_TO_PASS); AC-161.6 is a pytest guard that passes at Red and after; the rest are row or gate checks. The E2E parts of AC-161.5, AC-161.8 and AC-161.9 are dev-PC runs through `e2e-subset.ps1`, and AC-161.11 is the mini-air run.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-161.1 | row | `D/ehp-diagnosis-1.txt`, written by Python at row 1 before any tracked file differs from `baseline-scope.json`, holds numbers from both hosts: the mini-air's three fidelity specs from both tool runs (preview and bake plate and ink, gap per side, origin) and `AC-126.8`'s received colour; the dev PC's native fidelity run (gap per side, device scale), the scale-1 probe at plate widths 30 and 32 at three origins, the hover probe's native, hover-none and capable launches, the bake's inclusive and painted plate for `'Hi'` at 32, and the font SHA-256 of both hosts | Grouping §3 "diagnose first"; D-1213; D-1214 | A section with no number from one host, or a scope file whose hash differs from row 0 when the receipt is written, fails the row |
| AC-161.2 | row | The receipt's last line is `moving side: preview plate width (textBackgroundBox); hover: the host's pointer capability`, and its numbers carry it: at a scale of 1 the 30 px plate gives the mini-air's right gap of 2 and the 32 px plate 0 on every side at all three origins; the hover-none launch reproduces `rgb(21, 94, 117)` and the capable one `rgb(22, 78, 99)`; `hover-spec-red.py` runs the real `AC-126.8` through copies with the planned `args` option: it passes natively and fails under hover-none with `rgb(21, 94, 117)` at the hover expectation (M3) | D-1242; D-1246 | Any other moving side, or a probe that does not reproduce, is S5 |
| AC-161.3 | test | `capture-text-plates.test.ts` `AC-161.3`: `SEGOE_UI_GLYPH_UNITS` has the 95 printable ASCII keys, integer values, the head 2048 and 2210, `SEGOE_UI_KERN_UNITS` with 372 integer entries, and `'SEGOE_LA_GLYPHS' in mod` false; `segoe-units.py --check` exits 0, the module is CRLF and names the font SHA-256 (`SEGOE_UNITS` → `SEGOE_UI_GLYPH_UNITS` → `textBackgroundBox`) | `PLATE_UNITS`; D-1243 | Fails by assertion at row 6 (the export is absent); `--check` exits 1 at row 6; a `--write` with `EHP_WRITE_FAULT=1` at row 7 exits 1 and leaves the old hash |
| AC-161.4 | row | `capture-text-plates.json` holds 2,448 breadth and 40 matrix cases, the head names the font SHA-256, Pillow `13.0.0` and `raqm` false, it is LF with one final LF, and `plate-fixture.py --check` exits 0 | D-1251 | `--check` exits 1 before row 6 (no file); a `--write` with the fault at row 6 exits 1 and leaves no file and no `.ehp-tmp` |
| AC-161.5 | test | `AC-161.5` (three tests): breadth per side (left, top, right `x + width - 1`, bottom `y + height - 1`) at least 1,702 of 2,448 exact, at most 5 cases over 1 px, none over 2; the matrix 36 of 40 exact and the four named differences exactly; the two fidelity marks equal the bake's painted plates. E2E: the three fidelity specs pass on the dev PC at a scale of 1 with a gap of at most 1 on every side (`boxes-report.py`) | `PREVIEW_FOLLOWS_BAKE`; D-1242; D-1244 | All three fail by assertion at row 6 (the old box is `r - l` wide); the E2E specs fail at row 5 with the right gap of 2 |
| AC-161.6 | test | `test_capture_text_plates.py`: with the fixture's font, all 2,488 cases equal the painted `adapter.text_plate_box`; with another font, only the fixture's recorded values (its shape and its `'Hi'` at 16, `[20, 36, 16, 13]`), never the live bake; never skipped | D-1251 | A fixture with one changed box fails it (row 6 checks this on a copy in `D` through the module's `fixture_mismatches(path)` helper, never on the tracked file) |
| AC-161.7 | row | `PINS_NAMED`: `diff-check.py --expect-changed` over the edited test files exits 0; every changed or added line is a §Test pins entry at the place it names (the file equals its row-0 copy rebuilt by the named replacements, removals, hunks and blocks; an unnamed added line fails in every file, round 1 F1); line endings per line match the row-0 copy; `capture-geometry.json` keeps its row-0 hash; the pins pass at Green | M-7; D-1252; D-1255 | `diff-check.py --selftest` (an unnamed change, a removed line, a CRLF flip, an unlisted path each fail; on the real files, each intended edit passes, and each of these fails: an unnamed added line in every file that takes added lines, the round-1 early-return guard before the `AC-126.8` precondition, the precondition missing or after the hover, an added `test.skip()`, a line outside the e2e-harness block; `ehp-plan-diffcheck-selftest-r1.txt`, 34 cases) |
| AC-161.8 | test | `e2e-harness.test.ts` `AC-161.8 FIDELITY_FRAME` (the static reads in §The tests). E2E at row 5: with the frame on and the old plate, the dev PC's three fidelity specs fail with the mini-air's gap (right 2) | `FIDELITY_FRAME`; D-1245 | Fails by assertion at row 3; at row 5 `red-check.py --require AC-82.6 --require AC-102.19 --require AC-102.20` over the subset receipt, and `boxes-report.py` showing right 2 |
| AC-161.9 | test | `e2e-harness.test.ts` `AC-161.9 HOVER_CAPABLE` (the static reads). The precondition is a hard `expect(...).toBe(true)`, and no `return`, `test.skip` or `test.fixme` sits between `launchApp(HOVER_CAPABLE_ARGS)` and the colour assertion (round 1 F1). E2E at row 4: `AC-126.8` passes on the dev PC with the setting and its precondition | `HOVER_CAPABLE`; D-1246 | Fails by assertion at row 3; the row-1 hover probe's hover-none launch gives the mini-air's colour (the reproduction the fix answers); the static read and `diff-check.py` both fail the round-1 early-return guard (`ehp-plan-pin-probe-intended-r1.txt`) |
| AC-161.10 | row | `SNAPSHOT_NO_REF`: `snapshot-commit.py --selftest` passes; the row-10 snapshot's guards (`.git/index` bytes, `for-each-ref`, `HEAD`'s target, `status --porcelain=v1 -z`) are equal before and after, every git call runs with `GIT_OPTIONAL_LOCKS=0`, the index hash is taken after the first status, every named path differs from `HEAD`, its author is the noreply identity, and `--verify` exits 0 at row 10 and in the gate. No overwrite: at row 0 a sentinel file at each `--out` path of `plate-fixture.py`, `segoe-units.py` and `snapshot-commit.py` refuses with exit 1 and keeps its bytes (Session 96 RULE-2) | D-1247 | The selftest's negative cases (an existing `--out`, a non-noreply address, an edit after the build, an index written during the build `INDEX_CHANGED`, a named path equal to `HEAD` `UNCHANGED_SCOPE`) each refuse (`ehp-plan-snapshot-selftest-m2.txt`) |
| AC-161.11 | row | `KNOWN_EMPTY` and the mini-air run: after row 9 the known list has no `known` entry and its `label` and two `skip` entries equal row 0's; `tools/e2e_remote.py run <snapshot>` exits 0 with `tests` 232, `expected` 232, `unexpected` 0, `flaky` 0, `skipped` 0, `spec_files` 27, `known` and `new` empty, the two clipboard specs not run; `summarize` of the same report with the row-0 known copy exits 0 with the four in `known_now_passing`; the run's three fidelity `boxes` lines show a gap of at most 1 on every side | Grouping §3 Session 97; D-1253 | Row 9: `summarize` of the `a43cdb2` report exits 40 naming the four with the emptied list and 0 with the row-0 copy |
| AC-161.12 | row | `LOCAL_HOST_DETAILS`: `host-details-scan.py` over this session's new and edited tracked files, this plan folder and the handoff exits 0; `tools/check_home_path.py` shows no new hit before (row 0) and after (gate) | Brief §Security; Session 96 AC-21 | A scan of a scratch file holding the config's alias exits 1 (row 0, in `D`, printing the key name only) |
| AC-161.13 | row | MEU-161 `capture-text-plate-metrics` at matrix 9.46 in `meu-status.yaml`, the Phase 9 section and the matrix; `pending` at row 2, `ready_for_review` at row 8, `approved` at H2-2; `meu_status.py render --check` exits 0; `layout-canon` and `queue-canon` pass | D-1250 | `meu-register.py --selftest` refuses a second registration |
| AC-161.14 | row | Both issues `resolved` through `issue-resolve.py` (verification naming the row-10 run id and counts, `resolution_path` this plan, `root_cause` the measured cause, kerning named, `meu_links` `[MEU-161]` on the pixel issue only); `CAPTURE-TEXT-PLATE-METRICS-RESIDUAL` added (low, `ui`) through `tools/issue_triage.py add`; grouping row 97 (`:134`) set to MEU-161, `executed (Session 97)` and this plan's folder; `issue_triage.py render --check` exits 0 | Grouping §3; D-1244 | `issue-resolve.py` refuses a key outside its list; a register hash other than row 0's stops the row (S4) |
| AC-161.15 | gate | `session-gate.ps1` ends `session-gate: all steps exit 0` (§Session gate) | Brief §Gate | Fail-fast; later steps `not_run` |

### Spec Sufficiency Table

| Question | Answer | Source |
|---|---|---|
| Which side is the reference? | The bake: the saved PNG is what the user keeps and shares, and the preview must show it | D-1242; MEU-82 `TEXT_PIXEL_ORACLE` |
| What does the bake paint? | Pillow's inclusive `textbbox` filled by `draw.rectangle`: `r - l + 1` by `b - t + 1` | `adapter.py:223`, `:1124`; row 1 |
| How does the preview measure? | Font-unit glyph boxes, FreeType's scale and rounding per glyph, Pillow's basic-layout kerning per pair | D-1243; `ehp-plan-kern-model.py` |
| How close is close enough? | The measured residual as limits, plus a low issue | D-1244 |
| Which scale do the fidelity specs measure at? | 1, on every host | D-1245 |
| How does the hover spec get hover? | A Blink setting for a mouse-capable device, checked before the hover | D-1246 |
| How does the mini-air run uncommitted work? | A commit on no ref, built with a temporary index | D-1247 |
| What does the CI runner check? | The pytest guard: exact with the fixture's font, the shape otherwise | D-1251; `ci.yml` runs `pytest tests/` on `windows-latest` |
| One session or two? | One; the hover rows first and independent | D-1241 |
| Does `adapter.py` change? | No | D-1242 |
| Does `capture-geometry.json` change? | No; `AC-102.10` reads it as painted boxes | §Test pins |

#### Files Modified

| Path | Change | Row | Line endings |
|---|---|---|---|
| `ui/tests/unit/e2e-harness.test.ts` | The Session 97 block | 3 | LF (135 lines) |
| `ui/tests/e2e/electron-app.ts` | The `args` option | 4 | LF (169) |
| `ui/tests/e2e/settings.test.ts` | `HOVER_CAPABLE_ARGS`, `launchApp(args)`, `AC-126.8` call and precondition | 4 | CRLF (920) |
| `ui/tests/e2e/capture-inbox.test.ts` | `FIDELITY_ARGS`, `launchApp(args)`, two calls; the `AC-101.6` pins | 5 | LF (3,708) |
| `ui/tests/e2e/fixtures/capture-text-plates.json` | New | 6 | LF |
| `ui/tests/unit/capture-text-plates.test.ts` | New | 6 | LF |
| `tests/unit/test_capture_text_plates.py` | New | 6 | LF |
| `ui/tests/unit/capture-text-metrics.test.ts` | `AC-59.19` value | 6 | CRLF (50) |
| `ui/tests/unit/capture-transform.test.ts` | `AC-101.1` values | 6 | CRLF (209) |
| `ui/tests/unit/capture-text-lines.behavior.test.ts` | Import and oracle removed, `AC-102.10` replaced | 6 | LF (449) |
| `ui/tests/unit/capture-page.behavior.test.ts` | The `AC-82.4`, MEU-101 and `AC-59.19` render pins (H1) | 6 | CRLF (4,197) |
| `ui/src/renderer/src/features/capture/capture-segoe-metrics.ts` | Generated: the units table | 7 | CRLF (102 now) |
| `ui/src/renderer/src/features/capture/capture-text-metrics.ts` | Import, fallback, `textBackgroundBox` | 7 | CRLF (93) |
| `tools/e2e_host/known-failures.json` | The four `known` entries removed | 9 | LF (12) |
| `tests/tooling/test_e2e_remote.py` | `test_ac_11_known_tracked_list`: the expected `known` list `[]` (D-1259, M-7, after the plan's approval) | H1-2 | LF (2,305) |
| `.agent/context/meu-status.yaml` | MEU-161 and the P2 range; status at rows 8 and H2-2 | 2, 8, H2-2 | LF (4,223) |
| `docs/build-plan/09-screenshot-capture.md` | `## Residuals registered 2026-11-19` and the MEUs row; the Delivered note at row 8 | 2, 8 | CRLF (1,480) |
| `docs/build-plan/build-priority-matrix.md` | Row 9.46 | 2 | CRLF (197) |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | Generated by `meu_status.py render` | 2, 8, H2-2 | LF (256, 161) |
| `.agent/context/known-issues.yaml` | Two issues resolved, one added | 11 | LF (5,924) |
| `.agent/context/known-issues.md` | Generated by `render` | 11 | LF |
| `.agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md` | Row 97 (`:134`) only | 11 | LF (159) |
| `.agent/context/current-focus.md` | One entry | H1-3 | CRLF (236) |
| `docs/execution/metrics.md` | One row | H2-3 | CRLF (106) |
| The handoff, the two reviews, the reflection | New | H1-6, H1-7, H2-2 | LF |
| This plan folder's row-0 copies, `baseline.ps1`, `session-gate.ps1` | New | 0, H1-2 | LF |

**Outside the repository** (never tracked): receipts under `D` and `C:/Temp/av-kit/e2e-remote/<run-id>/`; on the mini-air, the tool's own `runs\<run-id>\` and `results\<run-id>\` under its configured root (Session 96's layout; nothing else there is touched); the snapshot commit object in `.git/objects`, on no ref.

**Read, never changed** (bound in `baseline-scope.json`): `packages/infrastructure/src/avkit_infra/capture/adapter.py`, `ui/tests/e2e/fixtures/capture-geometry.json` (CRLF, 84 lines), `ui/tests/unit/capture-hit-test.test.ts` (CRLF, 299), `tests/unit/test_capture_text_lines.py`, `tools/e2e_remote.py`, every other `tools/e2e_host/*` file, `ui/tests/e2e/electron-env.ts`, `ui/tests/e2e/global-setup.ts`, `ui/playwright.config.ts`, `ui/scripts/playwright-with-outputfile.mjs`, `ui/package.json`, `.github/workflows/ci.yml`.

**Line endings** were measured with Python bytes (`ehp-plan-eol-3.txt`, and again for this table): `capture-segoe-metrics.ts`, `capture-text-metrics.ts`, `settings.test.ts`, `capture-text-metrics.test.ts`, `capture-transform.test.ts`, `capture-page.behavior.test.ts`, `capture-hit-test.test.ts`, `capture-geometry.json`, `09-screenshot-capture.md`, `build-priority-matrix.md`, `current-focus.md` and `metrics.md` are CRLF and stay CRLF; every other scope file is LF and stays LF. New files are LF, written as bytes (Session 83 RULE-3). The two generators write CRLF and LF as named.

**Foreign class** (Session 92 RULE-3): `.agent/model-registry.local.json`, `.claude/agents/*.md` and `.cursor/agents/*.md` belong to the coordinator. Row 0 binds them by hash; a change during the session is recorded in the handoff, is not S4, and stays out of the commit paths.

## Out of Scope

| Item | Basis |
|---|---|
| The bake (`adapter.py`), `capture-geometry.json` and any stored image or sidecar | D-1242: the bake is the reference |
| Non-ASCII glyph tables, other fonts, a font fallback chain in the preview | The fallback glyph stands in as now; the residual issue records it |
| Exact per-pixel parity beyond the AC-161.5 limits | D-1244; `CAPTURE-TEXT-PLATE-METRICS-RESIDUAL` |
| `tools/e2e_remote.py`, the host scripts, the host's task or config | Session 96's; this session uses them unchanged |
| Session 96's deferred `check --out` empty stage folder | Brief §Out of scope |
| Smart App Control, auto sign-in, a GitHub runner, any workflow change | D-1216; brief |
| Host hardware, display settings or a pointing device on the mini-air | Brief; D-1246 states the capability in the spec instead |
| The clipboard specs (`capture-filmstrip-actions`, `capture-import`) | Grouping §3 Gate; never run here |
| The coordinator's scratch scripts | Brief; they stay where they are |
| `py-types`, MCP and OpenAPI suites | `packages/` and `mcp-server/` unchanged (H1-4 proves it) |

## BUILD_PLAN.md Audit

MEU-161 `capture-text-plate-metrics` is a new Phase 9 row (matrix 9.46, after MEU-160 at 9.45), depending on MEU-82 and MEU-102, in the P2 band (D-1250). `docs/BUILD_PLAN.md` and `meu-registry.md` are regenerated by `tools/meu_status.py render`, never hand-edited; `render --check` and the two canon tests run at rows 2 and 8, H2-2 and the gate. The hover fix has no MEU (D-1214: a test that states its capability). The dry run at plan time (`ehp-plan-meu-dryrun.txt`) gives `meu-status.yaml` 151,600 → 152,635 bytes, `09-screenshot-capture.md` 161,512 → 163,835 and `build-priority-matrix.md` 25,900 → 26,042.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1` (in the shape of `2026-11-18-e2e-remote-host/baseline.ps1`) records `HEAD` (`2c41c70` at plan time), the dirty set with its hashes, `git worktree list` and the host load (Session 91 RULE-1: the OS-wide probe of load, Electron and node processes before any measurement row); `git log --oneline 2c41c70..HEAD` and the scope diff since `2c41c70`, which must be empty (S2); `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json` (`packages/`, `mcp-server/{src,scripts,tests}`, `native/`), the walk dropping the secret names and `.agent/fleet/hub/` before any stat (Session 83 RULE-2); byte copies of every scope file under `D/baseline-copies/` (the input of `diff-check.py` and `eol-check.py`); the S2 anchors (§What the code shows: the line numbers, the 4 `known` and 2 `skip` entries, both issues `open` with `meu_links: []`, row 97 at `:134` `pending`, MEU-161 and 9.46 free, the dev PC's font SHA-256); `uv sync --frozen --offline --all-packages` and the home-path check; the copied checkers, their selftests and ruff on this folder's Python (Session 82 RULE-1, Session 74 RULE-3); the `--out` sentinels and fault cases of AC-161.10; `meu-register.py --dry-run --baseline-scope` and `--selftest`; `snapshot-commit.py --selftest`; `diff-check.py --selftest`; `segoe-units.py --out` and `plate-fixture.py --out` to `D`, compared with the plan-time hashes (`f93720ecdc6cb72d`, `36b15443d46282a6` prefixes; a difference is S9).

### 2. Red, then Green (rows 3 to 7)

The hover fix lands first and alone (D-1241): row 3 writes the static Red for both fixes (AC-161.8, AC-161.9 fail by assertion, `red-check.py --require`); row 4 is the hover Green (AC-161.9 passes, AC-161.8 still fails, `AC-126.8` passes on the dev PC). Row 5 adds the fidelity frame: AC-161.8 passes, and the three fidelity specs now fail on the dev PC by assertion with the mini-air's gap (the E2E Red of the plate fix). Row 6 writes the fixture, the new tests and the named pins: AC-161.3 and AC-161.5 fail by assertion, the changed pins fail (they move by design, D-1242, D-1255), AC-161.6 passes. Row 7 writes the module and the function: every Vitest passes, the moved pins included, the fidelity subset passes at a scale of 1 with gaps of at most 1, and the `touched` subset passes. Each Red receipt is checked by `red-check.py`, and each test file's hash at Red is recorded and must equal the hash at Green (S3), except the pins row 6 itself writes.

### 3. Real host (row 10)

`snapshot-commit.py --out D/ehp-snapshot-10.json` over the §Files Modified product and test paths and the known list, `--verify`, `tools/e2e_remote.py check`, then `tools/e2e_remote.py run <commit>`; `boxes-report.py` on its report; `summarize` with the row-0 known copy. A busy, locked or unsigned host is S10, any other refusal S11, a count other than AC-161.11's S12 (with D-1246's hover fallback named there), a scope change after the run S13.

### Session gate (H1-2)

`session-gate.ps1`, in the shape of Session 96's, fail-fast, later steps printed `not_run`, last line `session-gate: all steps exit 0`:

| Stage | Steps |
|---|---|
| Identity | `identity-before` (`identity.py`, which clears `ELECTRON_RUN_AS_NODE`, Session 88 RULE-3) |
| Static | `task-contract`; `scope-paths`; `line-endings` (`eol-check.py`); `home-path` (`tools/check_home_path.py`); `host-details` (`host-details-scan.py`); `pins` (`diff-check.py --expect-changed` the seven edited test files and `electron-app.ts`; the pins move by design, D-1255); `red-check-selftest`, `eol-check-selftest`, `diff-check-selftest`, `snapshot-selftest`; `py-format` and `py-lint` (`ruff format --check` and `ruff check` on `tests/unit/test_capture_text_plates.py` and this folder's Python; `ruff check packages/ tests/`); `segoe-check`; `fixture-check`; `known-empty` (KNOWN_EMPTY against the row-0 copy); `snapshot-verify` (`--verify D/ehp-snapshot-10.json`, else S13) |
| UI static | `ui-types` (`npm --prefix ui run typecheck`), `ui-lint` (`npm --prefix ui run lint`) |
| Tests | `ui-tests` (Vitest through `pwsh` from `ui`, the full suite); `py-tests` (`uv run pytest tests/ -x -q`, because `tests/unit` gains a file); `canon` (`layout-canon`, `queue-canon`) |
| Host load | `host-load` (Session 81 RULE-2; 50 %) |
| E2E | `ui-build` (`npm --prefix ui run build`); `e2e-touched` (`e2e-subset.ps1 -Set touched`); `e2e-full` (`flake-run.py --mode full --runs 1 --no-burn --label gate`: 232 of 232 in 27 files, the clipboard specs excluded; an unrecorded failure is rerun once alone, and a second failure or any `unhandled rejection:` line stops) |
| Registers | `issues-render-check`; `state-render` (`meu_status.py render --check`); `remote-evidence` (row 10's `summary.json`: exit 0, 232 and 232, commit equal to the snapshot) |
| Identity | `identity-after` |
| Skipped, with reasons | `py-types`, `mcp-types`, `mcp-tests`, `mcp-build`, `openapi`, `mcp-audit`: every file under `packages/`, `mcp-server/{src,scripts,tests}` and `native/` keeps its row-0 hash (H1-4) |

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` appears | Stop; re-plan the context tool decision |
| S2 | A row-0 anchor is gone or changed in meaning, a commit since `2c41c70` touches a scope path, an issue is not `open`, row 97 is not `pending`, MEU-161 or 9.46 is taken, or the dev PC's font SHA-256 differs from the plan's | Stop; a moved line only is fixed in the handoff (Session 51 RULE-3); a taken id moves to the next free one through `meu-register.py --meu --matrix`, recorded in the handoff |
| S3 | A Red test fails for a setup reason or passes, a Green needs a test change §Test pins does not name (M-7), an existing test fails after Green, or a dev-PC E2E output holds `unhandled rejection:` | Stop; never edit a test to pass |
| S4 | `git status` lists a path outside this plan's scope, `baseline-dirty.txt` and the foreign class, or a scope path no earlier row wrote differs from `baseline-scope.json` | Stop and ask the coordinator; never commit, stash or revert another session's work |
| S5 | The diagnosis names another moving side, a probe does not reproduce, or row 5's frame does not give the mini-air's gap on the dev PC | Stop and re-plan: every later row assumes the measured side |
| S6 | Codex is unavailable or the ledger refuses a round | The coordinator |
| S7 | `uv sync` fails on a held file | Tell the coordinator; never stop a process |
| S8 | The home-path check or the host-detail scan finds a new hit | Stop; fix the file, never extend the allow-list |
| S9 | A generator's row-0 output differs from the plan-time hash, `--check` fails after its write row, or the Green residual is outside AC-161.5's limits | Stop: the model or the font is not what the plan measured; never loosen a limit (M-3, M-7) |
| S10 | At row 10 the host refuses 20, 21, 22, 23 (a lock this session did not take) or 24, or the run's `overlap` is not empty | Not a finding: record, wait 15 minutes and run `check` again, up to 8 times; still refused, tell the coordinator. Never stop a process, release another run's lock or start the task by hand |
| S11 | At row 10 any other refusal (10, 11, 25 to 31, 33, 34), or the final release keeps the lock (`lock_kept`) | Stop and record; `release` with this session's own run id once; never bypass or re-pin the host key (11 goes to Mat), install anything or change the task; a second S11 goes to the coordinator |
| S12 | Row 10's counts are not AC-161.11's | If only `AC-126.8` fails: D-1246's fallback (restore its entry with its row-0 bytes, snapshot and run once more, keep the hover issue open with its verification and `root_cause` updated, resolve only the pixel issue, tell the coordinator). Any other failure, a fidelity spec included: a finding, not a retry; stop, record the summary and `boxes` lines in the handoff, and tell the coordinator; no change to the known list or a test |
| S13 | A snapshot scope file changes after row 10 | Snapshot and run row 10 once more on the final files, once only; a later change goes to the coordinator |

## Decision Log

> [!NOTE]
> D-1241 to D-1247 and D-1255 are this plan's eight briefs. Their §4a check: no push, merge or release (M-1): the snapshot of row 10 is a commit object on no ref, and the coordinator commits after the review without a push; nothing destructive (M-2): no stored image, sidecar or register entry is deleted, and the known list loses four entries whose issues this session resolves; D-1244 sets a pass rule for the preview's residual, which is new policy (M-3); no API, MCP tool or external contract changes (M-4): `textBackgroundBox` keeps its signature and its five callers; D-1242 changes what the preview shows, 1 or 2 px of plate (M-5); D-1241 departs from the grouping's split flag (M-6) and adds a MEU and product code to a session the grouping sized without one (M-8); D-1247 builds a commit object although the brief says not to commit, which is a conflict in letter (M-6); no existing test assertion changes beyond §Test pins, which names each test and its new value, so D-1255 is not an M-7 hit (HDP `:158`); no review exit (M-9); no human action (M-10): the mini-air is set up and signed in; nothing is waived (M-11): the fidelity specs keep their tolerances, the clipboard skip is the grouping's rule, and the hover spec states its capability instead of being skipped; no disclosure (M-12): nothing leaves Mat's machines, and the host details stay in the untracked config; no new permission or trusted remote (M-13): the host key was pinned in Session 96; no headless session (M-14). So D-1241 is `mandatory: [M-6, M-8]`, D-1242 `[M-5]`, D-1244 `[M-3]`, D-1247 `[M-6]`, and D-1243, D-1245, D-1246 and D-1255 `mandatory: none`; all eight are handed to the agent under Mat's 2026-11-18 words, which name M-3, M-5, M-6 and M-8. D-1248 to D-1254 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. `open_decisions` is empty and there is no STOP item. D-1256 and D-1257 are left for execution, and D-1258 to D-1260 stay free.
>
> **Earlier rows are not copied here.** D-1200, D-1211, D-1215 and D-1216 live in the grouping's §8, and D-1213 and D-1214 in the two issues' `enrichment.decision_log`. H2-2 reads them through `--decision-source` on the grouping (this plan's `grouping_source`) and `.agent/context/known-issues.yaml`, with `--decision-issue CAPTURE-TEXT-PIXEL-2PX-MINIAIR` and `--decision-issue E2E-HOVER-NO-POINTER-DEVICE`. `decision_sources` was probed at plan time with that source list: 4 ids from the grouping alone, 6 with the register and both issues, and a third run against this plan with them (Session 90 RULE-2; `ehp-plan-decisions.txt`, `ehp-plan-decisions-2.txt`). Under HDP §6 the reflection's `### Decisions Log` lists only this session's reversible autonomous choices.

```yaml
decision_log:
  - id: D-1241
    stage: planning
    question: "The grouping says to split Session 97 if the pixel diagnosis finds product code. Split it, or run one session?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6, M-8]
    chosen: "A: one session. The hover fix lands first and alone in rows 3 and 4, independent of the text fix, and is proved on the dev PC before row 5 starts; the text fix adds MEU-161 in row 2 before any product code, as the grouping's gate asks; both issues are resolved after one mini-air run."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md:107 — split flag: yes, if the pixel diagnosis finds product code; the hover fix then lands alone"
      - ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md:104 — if the cause is in the product, Stage A adds a MEU before the code changes"
      - "C:/Temp/av-kit/dispatch/s97-planner-brief.md — one plan, both issues resolved, the known list emptied of its 4 entries in this session"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-boxes-miniair.txt and ehp-plan-fidelity-probe-plan.txt — the cause is measured at plan time: the preview plate is 2 px narrow"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The split flag guards against a hover fix waiting on an unknown product change. The plan-time measurements already name the product side and its size (a 30 px plate where the bake paints 32), so the product change is known and bounded: one function, one generated table, named test pins. A keeps what the flag protects: the hover rows come first, touch no capture file, and pass on their own at row 4. One mini-air run then checks both, and the known list can be emptied in one step; split sessions would need two runs and leave the list half emptied, which exits 32 until the second session lands. B, two sessions, follows the flag's letter at the cost of a second plan, a second mini-air run and a run in between that must carry the pixel entries. C, the hover fix only, leaves the pixel issue open with its cause known. D, doing nothing, leaves both issues open and every mini-air run carrying four known failures. Departing from a grouping flag is M-6, and adding a MEU and product code to this session's scope is M-8; the hand-over covers both. Undo: the coordinator can still split before execution. Two-way."
  - id: D-1242
    stage: planning
    question: "The preview's text plate is narrower than the plate the bake paints. Which side changes?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-5]
    chosen: "A: the preview follows the bake. textBackgroundBox returns the rectangle Pillow paints, r - l + 1 by b - t + 1 over the inclusive textbbox; adapter.py, every saved image and capture-geometry.json stay as they are."
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:223, :1117, :1124 — text_plate_box returns Pillow's inclusive box and draw.rectangle fills it"
      - "docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md — MEU-82 TEXT_PIXEL_ORACLE: the preview must show what the bake writes"
      - "tests/unit/test_capture_text_lines.py:164 — AC-102.7 pins the bake's painted plates against capture-geometry.json"
      - ".agent/context/known-issues.yaml:5871 — D-1213: fix the product if it is wrong; a tolerance only if both sides are correct"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The saved PNG is what the user keeps and shares, so it is the reference, and the preview is the side that is wrong: at a scale of 1 its plate is 30 px where the bake paints 32. A changes only what the preview draws, 1 or 2 px more plate to the right and bottom, and no stored file. B, the bake follows the preview, would change every image saved from now on against the ones already saved, break AC-102.7 and capture-geometry.json, and still leave the preview's 16 px table scaled per size, which is off by up to 29 px at large sizes. C, widen the fidelity tolerance, is what D-1213 rules out while a side is measurably wrong. D, doing nothing, keeps three specs failing on the mini-air and the preview showing a plate the saved image does not have. A visible change in the app is M-5; the hand-over covers it. Undo: revert one function and the generated table. Two-way."
  - id: D-1243
    stage: planning
    question: "How should the preview measure the plate so it matches the bake at every size?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a generated Segoe UI glyph and kerning table in font units (2048 per em) and FreeType's arithmetic per glyph, with the pen moved by Pillow's basic-layout kerning step per pair: FT_MulFix scaling with its rounding and 26.6 pixel rounding, the baseline at the line top plus the rounded ascent, lines at a pitch of the font size plus 4; the table is generated from the font by segoe-units.py with the font's SHA-256 in its header."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-kern-limits.txt — with kerning 1,702 of 2,448 exact, 5 cases over 1 px, worst [0,2,1,1]; without it 1,472 exact, 27 over, worst right 5 on AVAVAVAVAVAV at 500"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-kern-model.txt — no raqm, 372 printable-ASCII kerning pairs (AV -117, To -211 units)"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-newbox-variants.txt — the chosen rounding ties for best at 1,290 exact on its own 8-line case set; the other variants fall to 639"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-fixture-xcheck-sides.txt — the old 16 px table: worst 29 px and 107 cases over 1 (C0), 30 and 95 with the inclusive edge only (C1), 5 and 41 rounded once from units (C2)"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-font-facts-devpc.txt and ehp-plan-font-facts-miniair.txt — the same font bytes on both hosts"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The bake measures with FreeType through Pillow, which scales each glyph's outline box in font units and rounds in 26.6, and, without raqm, moves the pen by each pair's kerning (expert pass M1); a table in the same units with the same arithmetic and kerning reproduces it, and the measurements show it: 15 of the 16 stored plates exact and 36 of the 40 matrix cases. B, another rounding of the same table, ties at best and is worse elsewhere. C, keeping today's 16 px table, with the inclusive edge or rounded once from units, leaves errors of 5 to 30 px at large sizes. D, doing nothing, keeps the 2 px gap at common sizes and the 29 px error at large ones. Without kerning a kerning-dense title at 500 px misses by 5 px. The cost is a 95-glyph and 372-pair table and a generator that must be rerun if the font changes, which the pytest guard and --check catch. Undo: revert the table and the function. Two-way."
  - id: D-1244
    stage: planning
    question: "The model leaves a residual of at most 2 px on some sizes. How is it pinned and tracked?"
    resolution: autonomous
    class: governance-value
    mandatory: [M-3]
    chosen: "A: pin the measured residual as limits in AC-161.5 (breadth per side: at least 1,702 of 2,448 exact, the breadth holding four kerning-dense texts, at most 5 cases over 1 px, none over 2; the matrix: 36 of 40 exact with the four differences named exactly; the two fidelity marks exact) and register CAPTURE-TEXT-PLATE-METRICS-RESIDUAL, low, for the rest; a later change may tighten a limit but never loosen one without a new decision."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-kern-limits.txt — the measured residual with kerning modelled"
      - "ui/tests/e2e/capture-inbox.test.ts — the fidelity specs allow 1 px per side"
      - ".agent/context/known-issues.yaml:5871 — D-1213: a tolerance changes only on a measured cause"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Kerning is now modelled (M1: without it the main cause past about 150 px), so the residual is hinting and per-glyph rounding; it is at most 2 px on one side in 5 of 2,448 cases, none at the three sizes the fidelity specs use. A turns the measurement into a ratchet: the unit test fails if the model gets worse, and the issue keeps the last pixels visible. B, exact parity, needs a FreeType rasteriser in the renderer and no plan-time measure shows a path to it. C, one blanket 1 px tolerance per case, would fail 5 cases or, if set to 2, hide a regression of the 1,702 exact ones. D, no unit pin, leaves only three E2E specs to catch a regression, at three sizes. Setting a pass rule is new policy (M-3); the hand-over covers it. Undo: change the limits by a new decision. Two-way."
  - id: D-1245
    stage: planning
    question: "The dev PC runs the fidelity specs at a device scale of 2 and hides the gap. At which scale should they run?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: at a scale of 1 on every host: the three fidelity specs' launches pass --force-device-scale-factor=1 through electron-app.ts's new args option (FIDELITY_FRAME); every other spec keeps the host's scale."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-devpc-fidelity.txt — the dev PC at scale 2: gap [1,1,1,1], passing"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-fidelity-probe-plan.txt — the dev PC at scale 1: a 30 px plate gives the mini-air's [0,0,2,0], a 32 px plate 0 at three origins"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-boxes-miniair.txt — the mini-air runs at a scale of 1"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Scale 1 removes the origin dependence: the 30 px plate fails at every probed origin, and the 32 px plate passes; at scale 2 the result depends on the origin: the dev PC's half-pixel origin gives [1,1,1,1], an integer origin gives a right gap of 2 (L1; ehp-plan-fidelity-probe-plan.txt). That is why the dev PC never saw it. A makes the dev PC see what the mini-air sees, so the Red reproduces at row 5 without the mini-air, and the specs measure the same thing on every host. B, the native scale, keeps the dev PC blind to this class of drift. C, a scale of 2 everywhere, would hide it on the mini-air too. D, doing nothing, is B. The cost is one launch option on three specs. Undo: drop the argument. Two-way."
  - id: D-1246
    stage: planning
    question: "The hover spec fails on a host with no pointing device. How should it state the capability it needs?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: launch AC-126.8's app with --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 (HOVER_CAPABLE) and assert matchMedia('(hover: hover)') before hovering; if the mini-air still fails it, restore only its known entry (row-0 bytes), keep the hover issue open with its verification and root_cause updated, and resolve the pixel issue alone."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-hover-probe-plan.txt — native rgb(22, 78, 99); hover none rgb(21, 94, 117), the mini-air's colour; the capable setting rgb(22, 78, 99)"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-hover-probe-2.txt — CDP emulated media does not change the hover match in this Electron; touch emulation and the hover-none setting do"
      - ".agent/context/known-issues.yaml:5910 — D-1214: make the spec state the hover capability it needs"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-m3-hover-spec.txt — the real AC-126.8 through the planned args option: native passes, hover-none fails with rgb(21, 94, 117)"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Tailwind v4 puts hover styles inside @media (hover: hover), so on a host without a mouse the colour cannot change; the spec tests a hover style and must say it needs a hover-capable device. A states that in the launch, and the precondition makes a host that ignores the setting fail with a named message rather than a colour timeout. The fallback keeps the mini-air run honest if the setting does not take there, which the plan could not test on the mini-air without a run. B, CDP emulation, did not move the media match at plan time, and touch emulation moves it only towards none. C, asserting the hover-none behaviour on hosts without a mouse, tests Tailwind rather than the app and makes the spec mean different things per host; the product has no hover-none rule to assert. D, doing nothing, keeps the known entry and the issue open. Undo: drop the argument and the precondition. Two-way."
  - id: D-1247
    stage: planning
    question: "The mini-air run needs a commit at the final tree, and the session may not commit. How does it run?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6]
    chosen: "A: snapshot-commit.py builds a commit object on no ref: a temporary index (GIT_INDEX_FILE) read from HEAD, the scope files added from the working tree, git write-tree and git commit-tree with the noreply identity in AGENTS.md §Commits; every git call runs with GIT_OPTIONAL_LOCKS=0 and the index hash is taken after the first status (M2); it refuses unless .git/index, every ref, HEAD's target and the status are byte-equal before and after and every named path differs from HEAD; tools/e2e_remote.py run takes that commit id unchanged."
    source_tag: Local Canon
    precedents:
      - "tools/e2e_remote.py:364 — run resolves any commit object with rev-parse --verify; :190 archives it with git archive"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-snapshot-selftest-m2.txt — the guards hold on a repository copy, and each negative case refuses, INDEX_CHANGED and UNCHANGED_SCOPE included"
      - "C:/Temp/av-kit/dispatch/s97-planner-brief.md — the run at the final tree; never commit, stage or push"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The run must test the final tree, and the tool archives a commit. A gives it one without staging, moving a branch or touching the index: the object is reachable from no ref, so no push can carry it and git gc prunes it after its expiry. The rule against committing protects Mat's branch and index; A leaves both byte-equal and proves it, so it keeps the rule's purpose while departing from its letter (M-6), which the hand-over covers. B, run at HEAD, tests the code before the fix. C, wait for the coordinator's commit, moves the run after the review and the issue resolution, so the known list would be emptied before the run that justifies it. D, teach e2e_remote.py to archive the working tree, changes Session 96's tool, which is out of scope. Doing nothing, no mini-air run, fails the grouping's acceptance. Undo: none needed; the object is unreferenced. Two-way."
  - id: D-1248
    stage: planning
    question: "Does the diagnosis need a new mini-air run before any change?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "No. Row 1 builds the diagnosis from the two existing mini-air runs' reports and plan-time read-only font facts, plus dev-PC probes at a scale of 1, written by Python into ehp-diagnosis-1.txt; the final mini-air run at row 10 is the check."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-boxes-miniair.txt — both mini-air runs carry each spec's preview and bake boxes"
      - ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md:101 — measure on both hosts before any change"
    research: { engine: none, sources: [] }
    reasoning: "The mini-air reports already hold the numbers the grouping asks for, and the dev PC reproduces them at a scale of 1, so a new 20-minute run would measure nothing new and load a shared host. Two-way."
  - id: D-1249
    stage: planning
    question: "Where do the new tests live, and what happens to AC-102.10's union oracle?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A new ui/tests/unit/capture-text-plates.test.ts for AC-161.3 and AC-161.5, the Session 97 block at the end of e2e-harness.test.ts for AC-161.8 and AC-161.9, and the oracle in capture-text-lines.behavior.test.ts removed with AC-102.10 reading the fixture's painted boxes; every changed line is in §Test pins."
    source_tag: Local Canon
    precedents:
      - "ui/tests/unit/e2e-harness.test.ts:46 — the Session 78 block of static spec checks"
      - "ui/tests/unit/capture-text-lines.behavior.test.ts:56-84 — the oracle rebuilds the old box from the table this session replaces"
    research: { engine: none, sources: [] }
    reasoning: "A new file keeps the new ACs together and away from older pins; the oracle would duplicate the function it checks, so the fixture, built from the bake, replaces it. Two-way."
  - id: D-1250
    stage: planning
    question: "Which MEU carries the product change, and how is it registered?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "MEU-161 capture-text-plate-metrics at matrix 9.46 in Phase 9, depending on MEU-82 and MEU-102, P2, registered by the plan-local meu-register.py (copied from the video-tail-frame pattern) and rendered by tools/meu_status.py."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-ids.txt — MEU-160 is the last id and 9.45 the last matrix item"
      - "docs/execution/plans/2026-11-17-video-tail-frame/ — MEU-160 registered by a plan-local script, then render"
    research: { engine: none, sources: [] }
    reasoning: "The grouping asks for a MEU before product code; the next free id and matrix item follow the last ones, and the script refuses a second registration. Two-way."
  - id: D-1251
    stage: planning
    question: "How is the plate fixture built, and what checks it on a host with a different font?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "plate-fixture.py writes ui/tests/e2e/fixtures/capture-text-plates.json from adapter.text_plate_box: 18 texts at 136 sizes and 10 texts at 4 sizes, with the font SHA-256, the Pillow version and raqm in its head; test_capture_text_plates.py compares every case exactly when the font matches and otherwise checks only the fixture's recorded shape and anchor, never skipping."
    source_tag: Local Canon
    precedents:
      - "tests/unit/test_capture_text_lines.py:164 — AC-102.7 compares stored plates with the bake exactly"
      - ".github/workflows/ci.yml — pytest tests/ runs on windows-latest, whose Segoe UI may differ"
    research: { engine: none, sources: [] }
    reasoning: "The fixture is the bake's own output, so the Vitest checks the model against the bake without Python; the guard catches a stale fixture where the font matches and does not fail CI on a runner with another font build. Two-way."
  - id: D-1252
    stage: planning
    question: "How is it proved that only the named test lines change?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "diff-check.py rebuilds each edited test file and electron-app.ts from its row-0 copy by the rules of its RULES table (the §Test pins: replacements, removals, inserted hunks of exact lines at one exact anchor line inside a named block, and named new or rewritten blocks with begin and end anchors) and requires the file to equal that, line for line; an added line no rule names fails in every file; line endings must match per line, and an unlisted path fails; its selftest covers each refusal, the round-1 early-return mutant included."
    source_tag: Local Canon
    precedents:
      - "AGENTS.md S3 — never edit a test to pass"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-diffcheck-selftest-r1.txt — the selftest passes, 34 cases"
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-pin-probe-r1.txt — the round-1 reviewer probe: the early-return mutant now fails"
    research: { engine: none, sources: [] }
    reasoning: "A rule table makes M-7's named changes checkable rather than a reviewer's reading. Plan review round 1 (F1) showed that accepting any added line in a file marked inserts=True let a guard that closed the app and returned before the AC-126.8 precondition pass, so every added line is now a named hunk at a named place, and the lines inside a named block are proved by their Red and their frozen hash. Two-way."
  - id: D-1253
    stage: planning
    question: "With the known list emptied, how does the run show the four known tests now pass?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Row 10 runs tools/e2e_remote.py summarize a second time on the run's report with --known set to the row-0 copy of the list, while both issues are still open; its known_now_passing must name the four."
    source_tag: Local Canon
    precedents:
      - "tools/e2e_remote.py:793-840 — summarize computes known_now_passing only from listed entries"
      - "tools/e2e_remote.py:391-402 — load_known needs known and skip as lists"
    research: { engine: none, sources: [] }
    reasoning: "The emptied list cannot name what it no longer holds, and the issues must still be open for the old list to load; row 11 resolves them after. Two-way."
  - id: D-1254
    stage: planning
    question: "How does the gate run the dev-PC E2E suite, and which suites does it skip?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The full dev-PC E2E through the copied flake-run.py --mode full --runs 1 --no-burn (232 of 232 in 27 files, the clipboard specs excluded, one solo rerun of an unrecorded failure), after the touched subset; py-types, the MCP suites and OpenAPI are skipped because packages/, mcp-server/ and native/ keep their row-0 hashes."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-e2e-pointer-flakes/ — flake-run.py and the clipboard exclusion"
      - ".agent/docs/commands.md — the D6 rows"
    research: { engine: none, sources: [] }
    reasoning: "The tool already excludes the clipboard specs and records each failure; the skipped suites cannot see a change outside their inputs. Two-way."
  - id: D-1255
    stage: planning
    question: "The bigger plate moves eight existing unit tests and one E2E spec that pin the old plate's numbers or points derived from it. Change their lines?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: change exactly the lines §Test pins names, each with its old and new value: AC-59.19 (metrics and render), AC-101.1, AC-82.4, AC-101.2, both AC-101.4 tests, AC-102.10 and the E2E AC-101.6; every new value is the planned function's output; diff-check.py enforces the list."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-host-parity/ehp-plan-h1-pins.txt — planned function, unchanged tests: 8 of 1,633 fail; with the pins: 148 of 148; old function with the pins: 9 fail"
      - ".agent/docs/human-decision-protocol.md:158 — M-7 is a hit only when no approved plan row names the test and the new assertion"
      - "C:/Temp/av-kit/e2e-host-parity/ehp97-expert-pass.txt — H1: the plan missed the SVG-reading tests"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The tests pin the old plate because the old plate was the product's rule; D-1242 changes that rule, so their values move by design. Each changed line is named with its old and new value in an approved plan row, which makes it not an M-7 hit, and diff-check.py refuses any other line. A keeps every test's purpose and its premise (AC-101.6's mark moves to y 4 so its se corner stays on the image corner). B, keep the old pins, means keeping the old plate, which D-1242 rejects. C, rewrite the tests to compute their values from textBackgroundBox, would make them check the function against itself. Doing nothing leaves 8 unit tests and one E2E spec failing after Green, which is S3. Undo: revert the named lines with the function. Two-way."
  - id: D-1256
    stage: execution
    question: "Row 12 asks docs/BUILD_PLAN.md to name the slug capture-text-plate-metrics, which the generator never writes there. How is the hub audit checked?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: row 12 checks what tools/meu_status.py render writes: docs/BUILD_PLAN.md names MEU-161, and .agent/context/meu-registry.md names MEU-161 and capture-text-plate-metrics; the rest of row 12 is unchanged and runs once more in full."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-host-parity/ehp-hub-audit-12-first.txt: BUILD_PLAN.md and the registry name MEU-161: False"
      - "tools/meu_status/render.py:88 and :124: the two BUILD_PLAN.md regions name MEU ids, never a slug"
      - "AC-161.13 (implementation-plan.md:359): MEU-161 in meu-status.yaml, the Phase 9 section and the matrix, and render --check"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Row 12's first check asked docs/BUILD_PLAN.md to hold both MEU-161 and the slug capture-text-plate-metrics, and it printed False (ehp-hub-audit-12-first.txt). BUILD_PLAN.md is generated by tools/meu_status.py render, whose two regions there (the phase tracker and the MEU summary, tools/meu_status/render.py:88 and :124) name MEU ids and never a slug: at HEAD 2c41c70 the file names MEU-160 but not its slug video-tail-frame. The slug lives in the registry the same render writes (.agent/context/meu-registry.md), and AC-161.13 asks for neither file by name. A, check what the generator writes (BUILD_PLAN.md names MEU-161; meu-registry.md names MEU-161 and its slug), keeps the check's purpose, that the hub shows the new MEU, and drops nothing AC-161.13 asks for, so it is not an M-11 waiver and not an M-8 scope change. B, hand-edit BUILD_PLAN.md to add the slug, is refused: generated Markdown is never hand-edited, and render --check would fail on it. C, change the renderer, is outside Files Modified (tools/). Doing nothing leaves row 12 unchecked, so H1-1 and the handoff cannot pass. Undo: restore the row-12 cell's first check. Two-way."
  - id: D-1257
    stage: execution
    question: "The first H1-2 gate failed at ui-tests: the standards sweeps AC-44.13 and AC-43.13 refuse the skip tokens the Session 97 block holds in e2e-harness.test.ts. How is it fixed?"
    resolution: autonomous
    class: two-way
    mandatory: [M-6]
    chosen: "A: rewrite the two lines inside the session block (the filter as a regular expression with the same matches, the message without the tokens); record the new hash in ehp-test-sha-3b.json; build a new no-ref snapshot and run row 10 once more on the second host into the 10b receipts (S13); the gate reads the 3b and 10b receipts; then the gate runs again from the start."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-host-parity/ehp-D6-ui-tests.txt: Tests  2 failed | 1637 passed (1639), AC-44.13 and AC-43.13 name e2e-harness.test.ts"
      - "ui/tests/unit/queue-card.test.ts:775 and ui/tests/unit/queue-primitives.test.ts:830: the sweeps over every file under ui/tests/unit"
      - "D-1247: the snapshot commit on no ref (SNAPSHOT_NO_REF)"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The first H1-2 gate (stamp 20261119-092449, ehp-gate-h1.txt and ehp-D6-ui-tests.txt) failed at ui-tests: 2 failed of 1639, the standards sweeps AC-44.13 (queue-card.test.ts:775) and AC-43.13 (queue-primitives.test.ts:830), which refuse the literal skip tokens in any file under ui/tests/unit. The Session 97 block this session wrote in e2e-harness.test.ts held them in its AC-161.9 filter and in that expectation's message. A, rewrite those two lines inside the session's own NewBlock so the filter is a regular expression with the same matches and the message names a skip or fixme call; no matcher or expected value changes, so it is not M-7. The file then differs from its Red hash and from snapshot ed48964, so its new hash goes into a new receipt (ehp-test-sha-3b.json, row 3's kept), the gate reads that receipt, and, as S13, a new no-ref snapshot is built and row 10 runs once more on the second host into the 10b receipts, which the gate's snapshot-verify and remote-evidence steps read; the first snapshot and run are superseded and kept. B, change the two sweep tests, is refused under S3 and is outside Files Modified. Doing nothing leaves the gate red, so H1-2 cannot pass. The second snapshot is a commit object on no ref like D-1247's (M-6). Undo: restore the two lines and the gate's receipt names. Two-way. Ruled by the coordinator on the HDP recommendation."
  - id: D-1258
    stage: execution
    question: "Row 10b, the second run on the second host, passed 232 of 232, but its summarize with the row-0 known list exits 32, known-failures-stale, because row 11 resolved the issues that list names. How is AC-161.11 shown?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: AC-161.11 is shown by run 10b own counts (ehp-run-10b-check.txt) and box gaps (ehp-boxes-10b.txt) plus run 10 known_now_passing (ehp-sum-10-old.txt); the snapshots differ only in ui/tests/unit/e2e-harness.test.ts (ehp-snapshot-diff-10-10b.txt); the exit-32 receipt and ehp-row10b-finding.txt are disclosed; the issue records keep citing run 10; then the gate runs again from the start."
    source_tag: Local Canon
    precedents:
      - "tools/e2e_remote.py:808 and :874: a known entry whose issue is not open is stale, exit 32"
      - "D-1257: the S13 rerun of row 10"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Row 10 ran once more under S13 after D-1257 (snapshot 484d4ab, run r20261119T143010Z-484d4ab): 232 of 232 with the known list empty, exit 0, commit equal to the snapshot, overlap empty (ehp-run-10b-check.txt), and every fidelity plate gap 0 (ehp-boxes-10b.txt). Its summarize with the row-0 list printed the four tests as known now passing and then refused with known-failures-stale, exit 32 (ehp-sum-10b-old.txt, ehp-row10b-finding.txt): row 11 resolved both issues that list names, and tools/e2e_remote.py refuses a known entry whose issue is not open (:808, :820, :874). That refusal is correct. A, AC-161.11 is shown by run 10b's own counts and gaps plus run 10's known_now_passing (ehp-sum-10-old.txt, exit 0, four): the two snapshots differ in one path, ui/tests/unit/e2e-harness.test.ts (ehp-snapshot-diff-10-10b.txt), a Vitest unit file the host's E2E run never executes; the row-11 issue records keep citing run 10 and are not edited again. B, a third run, cannot succeed: every later run summarized against the row-0 list stays stale. Doing nothing leaves the session stopped before H1-2. No M hit: no criterion, test, issue record or stop condition changes. Two-way. Ruled by the coordinator on the HDP recommendation."
  - id: D-1259
    stage: execution
    question: "The H1-2 gate fails at py-tests: tests/tooling/test_e2e_remote.py test_ac_11_known_tracked_list pins the four known entries that row 9 removed (D-1253), and no plan row names that test. What happens to it?"
    resolution: autonomous
    class: two-way
    mandatory: [M-7]
    chosen: "A: only the expected known list in test_ac_11_known_tracked_list becomes [] (the skip, label and KNOWN_FILE assertions kept); a receipt shows it fails with a known entry put back; the path joins Files Modified, the gate scope and baseline-scope.json with the HEAD hash; no new mini-air run; the gate runs again from the start."
    source_tag: Local Canon
    precedents:
      - "D-1253: the known list emptied at row 9 (KNOWN_EMPTY)"
      - "human-decision-protocol.md:158, M-7"
      - "D-1257: a test line changed after approval under the hand-over"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'proceed with the next session prompt orchestration here like you did the others', continuing USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Mat's 2026-11-18 instruction 'If you do not believe you can make the decisions run HDP and take recommenations from that!' covers M-hit briefs during this orchestration run. The H1-2 gate (stamp 20261119-095620) ran its steps to ui-tests with exit 0 and failed at py-tests: tests/tooling/test_e2e_remote.py test_ac_11_known_tracked_list pins the tracked known list to its four Session 96 entries, and row 9 emptied that list by design (D-1253, KNOWN_EMPTY); no plan row names the test. A, only that test's expected known list becomes [], its skip, label and KNOWN_FILE assertions and every other line unchanged, LF kept; a receipt shows it still fails when a known entry is put back; the path joins Files Modified, the gate's scope set, identity.py, eol-check.py, diff-check.py's allowed set and baseline-scope.json with HEAD's hash; it is not a snapshot path, so the mini-air run is not repeated; the gate runs again from the start. B, keeping the test, leaves a test that contradicts D-1253 and a gate that cannot pass, the failure left as a finding for a later session. Doing nothing leaves the session stopped before H1-2 passes. M-7: an existing test's assertion changes with no approved plan row naming it; flagged in the handoff for Mat. Two-way. Ruled by the coordinator on the HDP recommendation."
open_decisions: []
```

Expert pass (fresh context): `ehp97-expert-pass.txt`, every finding adopted: H1 → D-1255 and §Test pins; M1 → D-1243, D-1244, the fixture texts and `raqm`; M2 → D-1247 and `snapshot-commit.py`; M3 → row 1's `hover-spec-red.py`; L1 → D-1245; L2 → AC-161.3; L3 → AC-161.6.

Plan review round 1 (`ehp-plan-review-round-1.md`, changes_required, one High finding): F1, `diff-check.py` accepted every added line in a file marked `inserts=True`, so a guard in `AC-126.8` that closed the app and returned before the hover precondition passed with no problem, and `PINS_NAMED` could not stop it. Fixed: each added line is a named hunk of exact lines at one exact anchor inside a named block (`Insert`); new test code is a named block with begin and end anchors (`NewBlock`, `Wildcard`), proved by its Red and its frozen hash; the `inserts` flag is gone, and each file must equal its row-0 copy rebuilt by its rules. The precondition is a hard `expect(...).toBe(true)`, and AC-161.9's static read refuses a `return`, `test.skip` or `test.fixme` between the launch and the colour assertion. Changed: `PINS_NAMED`, §The launch option, §The fidelity frame, §The hover capability, §The tests, §Test pins, AC-161.7, AC-161.9, D-1252, rows 3 to 7 and the receipts. Receipts: `ehp-plan-diffcheck-selftest-r1.txt` (34 cases), `ehp-plan-pin-probe-r1.txt` (the reviewer's probe copied and run unchanged: the mutant now fails) and `ehp-plan-pin-probe-intended-r1.txt` (the intended edit passes, the mutant fails both checks).

### D-1241: One session or two, now that the pixel diagnosis found product code?

**I recommend A: one session, with the hover fix landing first and on its own.** The grouping said to split if the text fix needed product code, so the hover fix would not wait on an unknown change. The cause is now measured and small (one function and a generated table), so A keeps what the flag protects: the hover rows touch no capture file and pass on their own at row 4. One mini-air run then checks both fixes, and the known list is emptied in one step. A can fail if the text fix grows during execution; the hover fix is already in by then, and the coordinator can still split. Undo: split before execution. This departs from the grouping (M-6) and adds a MEU to the session (M-8), both covered by your hand-over.

- B: two sessions, as the flag says. A second plan and a second mini-air run, and a run in between that must carry the pixel entries.
- C: the hover fix only. The pixel issue stays open with its cause known.
- D: do nothing. Both issues stay open, and every mini-air run carries four known failures.

Refs: D-1241; D-1213; D-1214; grouping `:96-107`.

### D-1242: Should the preview change, or the saved image?

**I recommend A: the preview follows the saved image.** The preview's text plate grows by 1 or 2 px to the right and bottom so that it matches what the saved PNG paints; no saved image changes. The saved image is what you keep and share, and at a scale of 1 the preview's plate is 30 px where the image paints 32. A can fail if a user preferred the tighter plate; it is 1 or 2 px. Undo: revert one function and its table. This changes what the app shows (M-5), covered by your hand-over.

- B: the saved image follows the preview. Images saved from now on would differ from earlier ones, two stored test fixtures would break, and the preview would still be off by up to 29 px at large sizes.
- C: widen the test tolerance. The issue's own ruling forbids it while one side is measurably wrong.
- D: do nothing. Three specs keep failing on the mini-air, and the preview keeps showing a plate the image does not have.

Refs: D-1242; D-1213; MEU-82.

### D-1243: How should the preview measure text?

**I recommend A: a Segoe UI table in the font's own units, with the same rounding FreeType uses and the kerning Pillow adds.** The saved image is drawn by FreeType, so measuring the same way matches it: 15 of the 16 stored plates exactly, 36 of 40 matrix cases, and every side within 2 px over 2,448 cases; without kerning a title like `AVAV` at 500 px misses by 5. The table is generated from the font file and records its fingerprint, so a font change is caught. A can fail if a host has a different Segoe UI build; the Python guard and the generator's check say so. Undo: revert the table and the function.

- B: another rounding of the same table. It ties at best and is worse in other cases.
- C: keep today's 16 px table and fix only the edge. Large sizes stay off by 5 to 30 px.
- D: do nothing. The 2 px gap stays at common sizes and the 29 px error at large ones.

Refs: D-1243; `ehp-plan-kern-limits.txt`.

### D-1244: What about the last few pixels?

**I recommend A: pin the measured residual as limits and register a low issue for it.** At least 1,702 of 2,448 sides exact, at most 5 cases more than 1 px off, none more than 2; four named matrix differences. With kerning modelled, what remains is hinting and rounding. The test then fails if the model gets worse, and the issue keeps the remainder visible. A can fail if a later font build moves a case past a limit; the limit is then reviewed by a new decision, never loosened in place. Undo: change the limits by a new decision. A pass rule is new policy (M-3), covered by your hand-over.

- B: exact parity. It needs FreeType's rasteriser inside the app, and nothing measured shows a way to it.
- C: one blanket tolerance. At 1 px, 5 cases fail; at 2 px, a regression of the exact cases hides.
- D: no unit limit. Only three E2E specs, at three sizes, would catch a regression.

Refs: D-1244; D-1213.

### D-1245: At which screen scale should the fidelity specs run?

**I recommend A: at a scale of 1 on every host.** At 2 the result depends on where the image lands: the dev PC's half-pixel origin reads [1,1,1,1] and passes, while a whole-pixel origin shows the 2 px gap; that is why only the mini-air saw it. At a scale of 1 the gap is the same at every origin, so the dev PC reproduces the mini-air's exactly, so the fix can be proved before the mini-air run. A can fail if a spec relies on the scale elsewhere; only the three fidelity specs change. Undo: drop the launch option.

- B: the host's own scale. The dev PC stays blind to this kind of drift.
- C: a scale of 2 everywhere. The mini-air would hide it too.
- D: do nothing. The same as B.

Refs: D-1245; `ehp-plan-fidelity-probe-plan.txt`.

### D-1246: How should the hover spec get a mouse on a host without one?

**I recommend A: launch that spec's app with a Blink setting that says the device has a mouse, and check the media query before hovering.** The style under test only applies on hover-capable devices, so the spec should say it needs one; the check turns a host that ignores the setting into a clear failure instead of a colour timeout. On the dev PC the setting gives the expected colour, and the hover-none setting reproduces the mini-air's colour. A can fail if the mini-air ignores the setting, which could not be tested there without a run; the run then keeps only that one known entry and the hover issue open, and the pixel issue is resolved alone. Undo: drop the setting and the check.

- B: emulate through Chrome DevTools. Emulated media did not move the hover match in this Electron, and touch emulation moves it only towards no hover.
- C: assert the no-hover behaviour on hosts without a mouse. It tests Tailwind, not the app, and the spec would mean different things per host.
- D: do nothing. The known entry and the issue stay.

Refs: D-1246; D-1214.

### D-1247: How does the mini-air run test the uncommitted final tree?

**I recommend A: a snapshot commit object on no branch, built with a temporary index.** The run tool archives a commit, and the run must test the final files. The snapshot moves no branch, stages nothing and leaves the index and status byte-equal, which the script checks before and after; nothing can push it, and git prunes it later. It uses the noreply identity. A can fail if the scope changes after the run; the run is then repeated once on a new snapshot. Undo: none needed. Making a commit object while the rule says not to commit departs from the rule's letter (M-6), covered by your hand-over.

- B: run at the current commit. It tests the code before the fix.
- C: wait for the coordinator's commit. The run would come after the review and after the issues are resolved.
- D: change the run tool to archive the working tree. That is Session 96's tool and out of scope.
- Do nothing: no mini-air run. The grouping's acceptance fails.

Refs: D-1247; `tools/e2e_remote.py:364`.

### D-1255: May the existing tests that pin the old plate change?

**I recommend A: change exactly the named lines, each with its old and new value.** Eight unit tests and one E2E spec read the plate's numbers or click points derived from it; with the plate 1 or 2 px bigger they fail by design. Each changed line is in §Test pins with its old and new value, the values are the planned function's own output (148 of 148 pass at plan time, `ehp-plan-h1-pins.txt`), and `diff-check.py` refuses any other line. A can fail if a test's premise moves with the plate; AC-101.6's mark moves to y 4 to keep its premise. Undo: revert the lines with the function.

- B: keep the old pins. That keeps the old plate, which D-1242 rejects.
- C: compute the values from the function in each test. The tests would check the function against itself.
- Do nothing: eight unit tests and one E2E spec fail after Green (S3).

Refs: D-1255; D-1242; HDP M-7.

## Research References

- **FreeType fixed-point arithmetic:** `FT_MulFix(a, b)` returns `(a * b + 0x8000) >> 16` with the sign applied to the magnitudes, and outline coordinates are in 26.6 pixels, rounded with `(x + 32) & -64` (`FT_PIX_ROUND`); a glyph's scaled box is its font-unit box multiplied by `size * 64 * 65536 / units_per_em` through `FT_MulFix`. The plan's model reproduces Pillow's measurements with this arithmetic (`ehp-plan-newbox.txt`); hinting, which the model leaves out, is the measured residual. **Pillow basic layout** (no raqm, `features.check('raqm')` false): the pen moves by `FT_Get_Kerning` per pair, shrunk below 25 px, and the rounded px count is added in 1/64 px (`getlength('AV')` at 64 px is 80.9375 against 81).
- **Pillow `ImageDraw`:** `textbbox(xy, text, font, anchor='la', spacing=4)` returns `(left, top, right, bottom)` in pixels; `rectangle([x0, y0, x1, y1])` fills both corner pixels, so the painted plate is `x1 - x0 + 1` wide (measured on the bake, `ehp-plan-newbox-2.txt`). Pillow 13.0.0 on both hosts.
- **Chromium switches:** `--force-device-scale-factor=1` sets the device scale for every window of the process; `--blink-settings=key=value,...` sets Blink web preferences at start, including `primaryHoverType` and `availableHoverTypes` (2 is hover) and `primaryPointerType` and `availablePointerTypes` (4 is fine). Measured on Electron 42 with Chrome 148 (`ehp-plan-hover-probe-plan.txt`, `ehp-plan-fidelity-probe-plan.txt`).
- **Tailwind CSS v4:** the `hover:` variant is emitted inside `@media (hover: hover)`, so it applies only where the primary input can hover (the v4 upgrade guide's hover change). The probe agrees: under the hover-none setting `:hover` still matches the button while its colour stays at rest (`matches_hover_pseudo` true, `rgb(21, 94, 117)` before and after).

## Planning receipts

All under `C:/Temp/av-kit/e2e-host-parity/`, read-only against the repository; the host was read through Session 96's tool and the alias in the local config, writing only under this session's own folder in the configured root:

| Receipt | What it shows |
|---|---|
| `ehp-plan-check.txt`, `ehp-plan-host-mkdir.txt`, `ehp-plan-host-scp.txt` | `tools/e2e_remote.py check` (idle, no lock); the session's own host folder and the probe upload |
| `ehp-plan-boxes-report.txt`, `ehp-plan-boxes-miniair.txt` | Both mini-air runs: the fidelity boxes, gaps and origins |
| `ehp-plan-devpc-fidelity.txt`, `-report.json`, `ehp-plan-fidelity-probe*.txt`, `ehp-plan-fidelity-w32.txt` | The dev PC natively (scale 2, [1,1,1,1]) and at scale 1 (30 px [0,0,2,0], 32 px 0) |
| `ehp-plan-hover-probe*.txt`, `ehp-plan-m3-hover-spec.txt`, `ehp-plan-hover-spec-red-run*.txt` | The hover launches and colours; the real `AC-126.8` under hover-none (M3) |
| `ehp-plan-font-facts-devpc.txt`, `ehp-plan-font-facts-miniair.txt` | Segoe UI bytes, SHA-256 and version on both hosts; Pillow's version |
| `ehp-plan-newbox*.txt`, `ehp-plan-plate-model*.txt`, `ehp-plan-plate-breadth.txt`, `ehp-plan-fixture-xcheck*.txt` | The unkerned model, its rounding variants and the old table's candidates |
| `ehp-plan-kern-model.txt`, `ehp-plan-kern-limits.txt`, `ehp-plan-kern-geometry.txt` | Kerning (M1): the pairs, the 2,448-case limits, the marks and `text_plates` |
| `ehp-plan-h1-pins.txt`, `ehp-plan-transform.txt` | H1: the full Vitest with the planned function, the pinned and Red views; the transform pins |
| `ehp-plan-segoe-units-k.ts`, `ehp-plan-generators-rerun.txt`, `ehp-plan-segoe-check-pre.txt`, `ehp-plan-fault.txt` | The generated module and fixture, hashes reproduced; `--check` before the write; the write-fault path |
| `ehp-plan-ids.txt`, `ehp-plan-meu-dryrun.txt`, `ehp-plan-meu-selftest.txt`, `ehp-plan-meu-section.txt` | MEU-161, 9.46 and D-1241 to D-1260 free; `meu-register.py` dry run, selftest and text |
| `ehp-plan-snapshot-selftest-3.txt`, `ehp-plan-snapshot-selftest-m2.txt`, `ehp-plan-diffcheck-selftest-2.txt`, `ehp-plan-diffcheck-selftest-r1.txt` | The snapshot selftest on a repository copy (M2 included); the diff-check selftest, before and after round 1 |
| `ehp-plan-pin-probe-r1.txt`, `ehp-plan-pin-probe-intended-r1.txt` | Round 1 F1: the reviewer's early-return probe now fails; the intended edit passes and the mutant fails `diff-check.py` and the AC-161.9 static read |
| `ehp-plan-eol*.txt`, `ehp-plan-ruff-sources*.txt`, `ehp-plan-decisions*.txt` | Line endings by bytes; ruff on this folder; `decision_sources` probes |
| `ehp-plan-subset-list.txt`, `ehp-plan-report-probe.txt`, `ehp-plan-probe-pids.txt` | The subset sets; the known list against the `a43cdb2` report; every probe pid and its end |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against both issues, grouping §3 Session 97 and §8, the s97 brief, `adapter.py`, `capture-text-metrics.ts`, the specs and the planning receipts | `ehp-plan-2026-11-19-e2e-host-parity` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, the row-1, row-5, row-7 and row-10 receipts, against AC-161.1 to AC-161.15 | `ehp-execution-2026-11-19-e2e-host-parity` |
