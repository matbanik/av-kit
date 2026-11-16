---
project: "2026-11-15-tts-page-polish"
date: "2026-11-15"
source: "grouping .agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md §3 Session 80; issues TTS-STATUS-PILL-BELOW-AA-CONTRAST (triage D-806, Mat's D-455), TTS-AUDIO-RANDOM-FILE-NAMES and TTS-SEGMENTS-LABEL-IS-PROGRESS-SCALE (triage D-807)"
meus: ["MEU-150", "MEU-149"]
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
---

# Implementation Plan: A readable TTS progress label and an AA status pill

> **Project**: `2026-11-15-tts-page-polish`
> **Build Plan Section(s)**: 03 [§TTS output names and progress (residual)](../../../build-plan/03-service-layer.md#tts-output-names-progress-residual) (MEU-150, matrix 3.24) and 06 [§TTS status pill contrast (residual)](../../../build-plan/06-gui.md#tts-status-pill-contrast-residual) (MEU-149, matrix 6.18)
> **Status:** said to execute (USER_EXPLICIT 2026-11-15 'proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions.'). `plan_to_exec_gate: human`; the plan review was approved at round 1 (.agent/context/handoffs/2026-11-15-tts-page-polish-plan-critical-review.md).

---

## Goal

**Goal anchor:** the TTS page shows a job's progress as a percentage and never calls the 1000-step progress scale segments; each TTS output file keeps a name that says what the clip is and never overwrites a file already in the folder; and every TTS status pill label reads at 4.5:1 or more against its fill in both themes, which Mat confirms by looking at both themes before it ships.

This is Session 80 of the post-rc.3 grouping (§3: "both are what a user sees on the TTS page and in its output folder"). Order: MEU-150, then MEU-149, so the pill's contrast check runs on the page's final markup (grouping §3).

**MEU-150 (`TTS-AUDIO-RANDOM-FILE-NAMES`, `TTS-SEGMENTS-LABEL-IS-PROGRESS-SCALE`).**

- **The file names are already fixed.** Both issues were filed on 2026-11-03 against `<job id>.wav` and `<job id>.mp3`. On 2026-11-09 Mat ruled in the rc.3 retest that the MP3 name "should be somethign like first 3 words from the Text with dash followed by voice", and chose "Lowercase slug (Recommended)" (`docs/execution/plans/2026-11-09-rc3-fixes/implementation-plan.md:64-70`, change F5 at `:86`). That change shipped:
  - `output_stem` (`domain/tts.py:365-385`) builds the stem;
  - `_free_paths` (`services/tts.py:84-96`) moves to `-2`, `-3` and so on while the WAV or MP3 name is taken;
  - `tests/unit/test_tts_output_name.py` pins both.
  
  The issue's `root_cause` still describes the uuid names, and so does the 03 home section (`03-service-layer.md:774`). That section was registered on 2026-11-15, six days after F5, from the issue's 2026-11-03 text (`last_checked` 2026-11-04). Triage D-807 copied it without rechecking the code, so it was already out of date when it was written. That is a stale description, not a conflict with Mat's ruling, and F5 meets the home's Name, Safe and Job rules (`:778-780`). D-955 records Mat's rc.3 scheme as the answer to the brief the Name rule asks for. This plan adds guard tests for those rules. It changes no Python product code.
- **The progress label is new work.** `segments_total` is `TTS_PROGRESS_RESOLUTION` (`services/tts.py:45`), a 1000-step scale, and `TTSPage.tsx:740` prints it as `Segments 250/1000`. The page will show `25%`, and the bar will be labelled `Generation progress` (D-959). The API's `segments_done` and `segments_total` names are kept (D-962). The bar's value is floored the same way, so a screen reader never hears 100 while the label shows `99%` (D-963).

**MEU-149 (`TTS-STATUS-PILL-BELOW-AA-CONTRAST`).** `TTSPage.tsx:721-723` draws the job status as `text-xs text-fg` on a solid fill from `STATUS_COLORS` (`tts-controls.ts:14-21`). The plan-time probe measured each pair from `styles.css` (`C:/Temp/av-kit/tts-page-polish/contrast-probe.txt`):

| Theme | Status labels and their contrast |
|---|---|
| Dark (the default) | Idle and Cancelled 4.41, Failed 2.95, Pending 1.60, Generating 1.30, Done 1.29 |
| Light | Idle and Cancelled 5.71, Done 4.44, Failed 3.03, Generating 2.01, Pending 2.00 |

The pill becomes the page's own `StatusChip`, which already draws the loaded-model and asset chips on this page (`TTSPage.tsx:455`, `:537`). It uses a 10% status-hue fill with `text-fg`, which is the second look the 06 Look row names (D-956). The probe's worst pair is 6.86:1, dark `info` over `bg-elevated` (`chip-probe.txt`). Mat looks at both themes in the running app before closeout (D-806; row 5, M-10).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). The change touches two renderer modules and four test files, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern.
  - Receipts go under `C:/Temp/av-kit/tts-page-polish/`, named `tpp-*`. Pytest runs with `TMP` and `TEMP` at `C:\Temp\av-kit\tts-page-polish\tmp`.
  - Every row runs in `pwsh` from `P:/av-kit`. It sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
  - Vitest runs as `npm --prefix ui run test -- …` from pwsh, never from the Bash tool.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone. A process is stopped only by its id, through `dev-app-procs.py`, never by name.
- **Cloud-local contract:** local. Mat looks at both themes in the running app (grouping §3 "Cloud/local: local").
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `tpp-plan-2026-11-15-tts-page-polish` and `tpp-execution-2026-11-15-tts-page-polish`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
- **Queue:** Session 87 runs and is committed first. Sessions 75 to 79 run before this one, and Mat has not said whether each is committed after it closes, so their changes may be uncommitted when this session starts. Baselines and scope checks are path-scoped and bound to content (§Verification Plan 1). Execution waits for Mat's message (`plan_to_exec_gate: human`).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-150 output names and progress label | `.agent/context/handoffs/2026-11-15-tts-page-polish-MEU-150-handoff.md` |
| MEU-149 status pill contrast | `.agent/context/handoffs/2026-11-15-tts-page-polish-MEU-149-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-15-tts-page-polish-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-15-tts-page-polish-implementation-critical-review.md`

The plan writes one handoff per MEU, as `2026-11-14-capture-shapes-steps` does.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-readonly.json`, `tpp-base-py.txt`, `tpp-base-ui.txt` |
| WP-2 | MEU-150: Red, then Green (rows 1 and 2) | WP-1 | shared | `tts-controls.ts` `progressLabel`, `TTSPage.tsx` progress label, the AC-150 tests |
| WP-3 | MEU-149: Red, then Green (rows 3 and 4) | WP-2 | shared | `tts-controls.ts` `TTS_STATUS_TONE`, `TTSPage.tsx` pill, `ui/tests/unit/tts-pill-contrast.test.ts` |
| WP-4 | Mat's look at both themes (row 5, M-10) | WP-3 | shared | `human-check.md` |
| WP-5 | Build-plan notes, then registers and status (rows 6 and 7) | WP-4 | shared | 03 and 06 Delivered notes, the 06 wireframe, `known-issues.yaml` and `.md`, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, grouping §6 row 80 |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | Two handoffs, the review, the reflection |

## User Review Required

> [!NOTE]
> **One thing needs your eyes: row 5.** After the code is done, the executor starts the dev app and asks you to look at the TTS page's status pill in both themes (D-806). That is the only stop. Two choices have briefs below. The file names (D-955) were already settled by your rc.3 ruling; the brief is there because the 03 rule for them asks for one. The pill's look (D-956) was handed to the agent under your 2026-11-15 ruling. Both recommendations are taken, and the briefs show the options.
>
> **What changes for you:**
>
> - The TTS run bar shows `25%` instead of `Segments 250/1000`. The text preview and hash after it stay. A screen reader hears the same number.
> - The status pill (Idle, Pending, Generating, Done, Failed, Cancelled) becomes a soft-tinted chip with normal text, like the page's other chips. It reads clearly in dark and in light. In light the tint is faint by design, because the word carries the status; you judge it in row 5.
> - File names stay as you ruled for rc.3: `hello-world-again-am_eric.mp3`, then `-2`, `-3` and so on. A file already in the folder is never overwritten. Old uuid-named files keep their names. The plan only adds tests that lock this in.
>
> **What this plan leaves out:** a name template setting, renaming old uuid-named files, and an exclusive-create reservation of the output name (§Out of Scope).

## Proposed Changes

### Single-statement contracts

**MEU-150**

- **`PROGRESS_PERCENT` (D-959):** `tts-controls.ts` exports `progressLabel(done: number, total: number): string`.
  - It returns `` `${p}%` ``, where `p` is `Math.floor(100 * done / total)` clamped to the range 0 to 100.
  - A `total` of 0 or less, or a `done` or `total` that is not finite, gives `'0%'`.
  - It also exports `progressFraction(done: number, total: number): number`, which returns that same `p` divided by 100 (`0` where the label is `'0%'`), so the label and the bar share one clamp (D-963).
  - `TTSPage.tsx` prints `progressLabel(job?.segments_done ?? 0, job?.segments_total ?? 0)` where it printed `Segments {done}/{total}`. The preview and hash that follow are kept.
- **`PROGRESS_ARIA` (D-959, D-963):** the run bar's `ProgressBar` (`testId="segment-progress-bar"`) gets `ariaLabel="Generation progress"` and `value={progressFraction(segmentsDone, segmentsTotal)}`. The bar rounds `value × 100` for `aria-valuenow` (`ProgressBar.tsx:78,86`), and a floored value rounds to itself, so `aria-valuenow` equals the label's number: at 999 of 1000 both say 99. `ProgressBar.tsx` does not change, so its other users (`QueueCard.tsx`, `TranscriptPage.tsx` and this page's download bar) keep their rounding. The test ids `segment-progress` and `segment-progress-bar` are kept, because the E2E test reads them (`ui/tests/e2e/tts-generate.test.ts`).
- **`NAME_SCHEME_KEPT` (D-955):** an output's stem stays `output_stem(text, voice)` (`domain/tts.py:369-385`), as shipped in rc.3 F5:
  - the casefolded first three words, each kept to its letters and digits, joined by `-`;
  - at most 60 characters, or `speech` when no word is left;
  - then `-`, then the voice kept to its letters, digits and `_` (`voice` when nothing is left).
  
  The WAV and MP3 share the stem. No Python product file changes.
- **`NAME_SAFE_GUARD` (D-958):** for any text, the stem holds none of `< > : " / \ | ? *`, no control character, no `.` and no space. It does not end in a dot or a space, and it is not a reserved Windows device name with or without an extension: it always ends with `-<voice>`. The output stays directly inside the output folder.
- **`NAME_COLLISION_GUARD` (D-957):** `_free_paths` (`services/tts.py:84-96`) is kept. A stem whose WAV or MP3 name is taken, by an earlier job or by the user's own file, moves to `-2`, `-3` and so on. The file already there keeps its bytes.
- **`LEGACY_OUTPUT_KEPT`:** a uuid-named output file from before rc.3 stays as it is. The job ID stays a uuid4 string (`services/tts.py:257`), and the output path names the new file.
- **`API_SHAPE_UNCHANGED` (D-962):** no route, schema or MCP tool changes. `openapi.committed.json` passes `tools/export_openapi.py --check`, and no file under `packages/` or `mcp-server/` changes from its row-0 content.

**MEU-149**

- **`PILL_CHIP_TONES` (D-956):** `tts-controls.ts` exports `TTS_STATUS_TONE: Record<JobStatus, StatusChipTone>`. It imports the type with `import type` from `../../components/ui/StatusChip`. The mapping follows the queue header's `toneFor` (`QueueHeaderRow.tsx:42-48`): done is `success`, failed `danger`, running `info`, waiting `warning`, anything else `neutral`.

  | Status | Tone |
  |---|---|
  | Idle | `neutral` |
  | Pending | `warning` |
  | Generating | `info` |
  | Done | `success` |
  | Failed | `danger` |
  | Cancelled | `neutral` |
- **`PILL_LABEL_KEPT`:** `TTSPage.tsx` draws the pill as `<StatusChip testId="tts-status-pill" label={status} tone={TTS_STATUS_TONE[status as JobStatus] ?? 'neutral'} />`. The label is still the status word. An unknown status falls back to `neutral`, as the old map fell back to `bg-neutral`. `:126` becomes `const status = job?.status || 'Idle'`. The API types `status` as a free string (`openapi.committed.json:3948-3951`), and `StatusChip` throws on a blank label (`StatusChip.tsx:24`), so a blank status shows `Idle` instead of crashing the page where the old span showed nothing.
- **`STATUS_COLORS_RETIRED`:** `STATUS_COLORS` is deleted from `tts-controls.ts`, and `TTSPage.tsx` no longer imports it. No TTS source names it, and the AC-43.2 census of legacy status maps shrinks to `transcript-controls.ts`.
- **`PILL_CONTRAST_TEST` (D-960):** `ui/tests/unit/tts-pill-contrast.test.ts` (new, LF) reads the tokens from `styles.css` at test time. Dark is the `@theme {` block. Light is `:root:not(.dark) {` laid over dark.
  - For each status, it renders `StatusChip` with `TTS_STATUS_TONE[status]` and reads the fill token, its alpha and the label token from the class the chip ships (`bg-<token>/<n>`, `text-<token>`).
  - It checks the label against the fill composited over `--color-bg`, `--color-bg-elevated` and `--color-surface-0`, in both themes: 6 statuses × 3 backdrops × 2 themes, each at 4.5:1 or more.
  - The ratio is WCAG 2.2's, with the 0.04045 threshold, unrounded. The composite is source-over per channel, rounded half up, as `light-accent-contrast.test.ts` does (`TINT_MODEL`, `CONTRAST_FLOOR`).
  - A calibration case shows the helper measures the old dark Generating pair (`text-fg` on a solid `--color-accent`) below the floor, at 1.30 to two places.
- **`QUEUE_TOKENS_UNCHANGED`:** `StatusChip.tsx`, `ProgressBar.tsx`, `status-tokens.ts`, `styles.css` and `ui/tests/e2e/test-ids.ts` do not change. AC-43.3, AC-43.5 and AC-51.3 pass unchanged.
- **`THEME_CHECK` (D-806, M-10):** Mat looks at the pill in the running dev app in dark and in light, and his words are recorded verbatim in `human-check.md` and in the 06 Delivered note (row 5).

### MEU-150: the progress label, and guards on the shipped names

1. **`tts-controls.ts` (CRLF).** Add `progressLabel` and `progressFraction` (`PROGRESS_PERCENT`) below `SPEED_PRESETS`, with a doc comment that says the scale is `TTS_PROGRESS_RESOLUTION`, not a segment count.
2. **`TTSPage.tsx` (CRLF).**
   - Import `progressLabel` and `progressFraction`.
   - At `:740`, replace `Segments {job?.segments_done ?? 0}/{job?.segments_total ?? 0}` with `{progressLabel(job?.segments_done ?? 0, job?.segments_total ?? 0)}`.
   - At `:736`, set `ariaLabel="Generation progress"`.
   - At `:735`, set `value={progressFraction(segmentsDone, segmentsTotal)}` (D-963). Both test ids stay.
3. **`tests/unit/test_tts_output_name.py` (LF).** Add AC-150.4 to AC-150.7 as guard tests of the shipped behaviour. They pass at Red, because the product already does what they check. A guard that fails is S7.

### MEU-149: the pill

1. **`tts-controls.ts` (CRLF).** Delete `STATUS_COLORS` (`:14-21`). Add `import type { StatusChipTone } from '../../components/ui/StatusChip'` and `TTS_STATUS_TONE` (`PILL_CHIP_TONES`).
2. **`TTSPage.tsx` (CRLF).**
   - In the `./tts-controls` import (`:37-47`), replace `STATUS_COLORS` with `TTS_STATUS_TONE` and `type JobStatus`.
   - At `:126`, change `job?.status ?? 'Idle'` to `job?.status || 'Idle'` (`PILL_LABEL_KEPT`).
   - Replace the `<span>` at `:721-723` with the `StatusChip` (`PILL_LABEL_KEPT`). `StatusChip` is already imported at `:11`.
3. **`ui/tests/unit/tts-pill-contrast.test.ts` (new, LF):** `PILL_CONTRAST_TEST`.

### Existing test assertions that change (named for §4a M-7)

Each change below names the test and its new assertion, so it is approved scope, not an M-7 hit. No other existing test changes. One that fails after Green is S5.

| Test | File (line endings) | Today | After |
|---|---|---|---|
| `AC-56.5 generating shows the shared ProgressBar in the slot, then output on completion` | `ui/tests/unit/tts-page.behavior.test.ts:425` (CRLF) | `:435` `expect(byTestId('segment-progress').textContent).toContain('Segments 2/8')` | `:435` becomes `toContain('25%')`, and one line after it adds `expect(byTestId('segment-progress').textContent).not.toContain('Segments')`. The fixture (`:180`, 2 of 8) and every other line stay |
| `AC-22.24 STATUS_COLORS SPEED_PRESETS and no raw hex` | `ui/tests/unit/tts-page.test.ts:405` (CRLF) | Destructures `STATUS_COLORS` and checks that `STATUS_COLORS.Generating` is a `bg-` class with no `#` | Title `AC-22.24 SPEED_PRESETS, the status tones and no raw hex`. It loads the module as a namespace (`const controls = await import(…)`), keeps the `SPEED_PRESETS` check and asserts `Object.prototype.hasOwnProperty.call(controls, 'STATUS_COLORS')` is `false`. It asserts that every value of `controls.TTS_STATUS_TONE` is one of `neutral`, `info`, `success`, `warning`, `danger`, and that `ttsSources().join('\n')` does not match `/\bSTATUS_COLORS\b/`. The raw-hex, `SelectInput` and `styles` checks stay. This is the shape of AC-45.12 (`convert-controls.test.ts:187`) |
| `AC-43.2 status pill table is a single hex-free statement with no rival status map` | `ui/tests/unit/queue-primitives.test.ts:376` (CRLF) | The census at `:402-406` lists `transcript-controls.ts`, `tts/TTSPage.tsx` and `tts/tts-controls.ts` | The census is `['ui/src/renderer/src/features/transcript/transcript-controls.ts']`. The comment at `:389-397` gains one sentence: MEU-149 moves the TTS pill onto `StatusChip`, so only the transcript controls module keeps the legacy map |

AC-22.10 (`tts-page.test.ts:230`, the `segments_done` and `segments_total` names in the sources) still passes, because the page still reads both fields.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `TTSJobOut` (`segments_done`, `segments_total`, `output_path`, `id`) | `packages/api` (`openapi.committed.json:3925`) | Unchanged (D-962) | Unchanged |
| TTS output file names in the user's output folder | `domain/tts.py` `output_stem`, `services/tts.py` `_free_paths` | Unchanged (D-955); guarded by AC-150.4 to AC-150.7 | — |
| The run bar's text and accessible names | `TTSPage.tsx` | Text only: a percentage; the bar's label `Generation progress` | — |

No API route, OpenAPI document, MCP tool shape or database schema changes.

### Acceptance Criteria

Python tests are named `test_ac_<meu>_<n>_…`. The Vitest titles start with the AC id, so `red-check.py --require AC-150.1` matches each exactly.

- **Python** (`tests/unit/test_tts_output_name.py`, LF): `test_ac_150_4_unsafe_text_gives_a_safe_name`, `test_ac_150_5_text_with_no_word_gives_speech`, `test_ac_150_6_a_users_file_is_never_overwritten`, `test_ac_150_7_legacy_output_and_job_id_are_kept`. The generate cases use `_Stack` and `_require` from `tests.unit.test_tts_async`, as the file's existing tests do. They create `stack.root` before they place a file in it.
- **Vitest** (exact titles):
  - in `ui/tests/unit/tts-page.test.ts`: `AC-150.1 progressLabel gives a floored percentage of the progress scale` and `AC-149.1 TTS_STATUS_TONE maps every job status to a StatusChip tone`;
  - in `ui/tests/unit/tts-page.behavior.test.ts`: `AC-150.2 the run bar shows progress as a percentage, never as segments`, `AC-150.3 the progress bar is labelled Generation progress` and `AC-149.4 the run bar's status pill is a StatusChip with the status tone`;
  - in `ui/tests/unit/tts-pill-contrast.test.ts`: `AC-149.5 every TTS status pill reads at 4.5:1 in both themes` and `AC-149.5 the ratio helper measures the old solid fills below the floor`.
- **New names fail by assertion.** Each test that reads `progressLabel`, `progressFraction` or `TTS_STATUS_TONE` loads `tts-controls` as a namespace and asserts `typeof controls.progressLabel === 'function'`, `typeof controls.progressFraction === 'function'` or `typeof controls.TTS_STATUS_TONE === 'object'` first. So Red fails by assertion, never by a `TypeError` (`red-check.py` Verification Plan §2).
- **AC-150.8, AC-150.9, AC-149.6 to AC-149.8** are checked by row, gate and closeout commands; they have no test title of their own.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-150.1 | unit | `progressLabel` exists. `(0, 1000)` gives `0%`, `(250, 1000)` `25%`, `(999, 1000)` `99%`, `(1000, 1000)` `100%`, `(2, 8)` `25%` and `(1, 3)` `33%`. `(1200, 1000)` gives `100%` and `(-5, 1000)` gives `0%`. `(5, 0)`, `(5, -1)`, `(NaN, 1000)` and `(5, Infinity)` give `0%`. `progressFraction` gives `0.99` for `(999, 1000)`, `0.25` for `(250, 1000)`, `1` for `(1200, 1000)` and `0` for `(5, 0)` | Local Canon (03 §TTS output names and progress: Progress label; D-959, D-963) | The out-of-range and non-finite inputs are the negatives |
| AC-150.2 | unit | With a Generating job at 250 of 1000, the `segment-progress` text holds `25%`, then ` · Hello` and ` · abcdef01`. It holds neither `Segments` nor `/1000`. A job at 0 of 1000 shows `0%`. The changed AC-56.5 (2 of 8) shows `25%` and no `Segments` | Local Canon (03 Progress label; D-959) | In Red the text is `Segments 250/1000`, so the `not` assertions fail |
| AC-150.3 | unit | The `segment-progress-bar` element has `aria-label="Generation progress"` and `role="progressbar"`, and no element on the page is labelled `Segment progress`. With a Generating job at 999 of 1000, the bar's `aria-valuenow` is `99` and the `segment-progress` text holds `99%` | Local Canon (D-959, D-963) | In Red the label is `Segment progress` and the 999 of 1000 bar says `100` |
| AC-150.4 | unit | Parametrized `output_stem` over texts that hold `< > : " / \ \| ? *`, control characters, `..\..\x`, `CON`, `nul.txt`, `COM¹ LPT1`, trailing dots and trailing spaces. Each stem holds none of those characters, no `.` and no space. It does not end in a dot or a space, and neither it nor its part before a `.` is a reserved device name. A generate from `..\..\escape` writes a file whose parent is `stack.root` | Local Canon (03 Safe; 09 §Export copy `export_stem`, D-612); Research-backed (Microsoft Learn, "Naming files, paths, and namespaces": the reserved characters, names and trailing dot or space) | Each unsafe text is a negative |
| AC-150.5 | unit | A generate from a text made only of forbidden characters (`<>:"/\|?*`) writes `speech-am_eric.mp3`. The stem alone is already pinned by `test_output_stem` (`test_tts_output_name.py:26`) | Local Canon (rc.3 F5: "`speech` when no word is left") | — |
| AC-150.6 | unit | With the user's own `hello-world-again-am_eric.mp3` already in the folder, and nothing else, an MP3 generate of `Hello world again` writes `hello-world-again-am_eric-2.mp3`. The same holds for a lone `.wav` of that stem. In both cases the user's file keeps its bytes | Local Canon (03 Name: "A name never overwrites an existing file"; D-666 `MP3_RESERVE`; D-957) | A write over the user's file fails the bytes check |
| AC-150.7 | unit | A legacy `<uuid4>.mp3` in the folder keeps its name and bytes after a generate. The new job's `id` parses as a version-4 UUID, and its `output_path` is the stem-named file, not `<id>.mp3` | Local Canon (03 Job: "The job ID and the API shape are unchanged … Existing output keeps its name") | A renamed or removed legacy file fails |
| AC-150.8 | contract | `tools/export_openapi.py --check openapi.committed.json` exits 0, and no path under `packages/` or `mcp-server/` changes from its row-0 content (H1-4, `readonly-check.py`) | Local Canon (03 Job; D-962) | A changed schema fails the check |
| AC-150.9 | docs | `03-service-layer.md` (CRLF, kept) holds one `> **Delivered (Session 80).**` note under its home section, which says the section's uuid wording was already out of date when it was registered. The 06 wireframe's run bar line reads `68%  ·  Hello · abcdef01  │`, and its output example reads `the-quick-brown-af_heart.mp3`. Each line keeps its length. The ProgressBar spec's example at `:1228` reads `"Item 34/50"` | Local Canon (D-955, D-959) | The old strings `Segment 34/50` and `speech_output_2026-05-30.mp3` are absent from 06 |
| AC-149.1 | unit | `TTS_STATUS_TONE` exists. Its keys equal `JOB_STATUSES` in order, and its values match the `PILL_CHIP_TONES` table | Local Canon (D-956, handed over) | A missing status or a non-chip tone fails |
| AC-149.2 | unit | The changed AC-22.24: `STATUS_COLORS` is not an own property of `tts-controls`, no TTS source matches `\bSTATUS_COLORS\b`, and every `TTS_STATUS_TONE` value is a `StatusChipTone` | Local Canon (AC-45.12 precedent; D-956) | In Red the module still exports the map |
| AC-149.3 | unit | The changed AC-43.2: the legacy status-map census is `transcript-controls.ts` alone | Local Canon (AC-43.2's "shrink it as each page migrates") | In Red the census still lists the two TTS files |
| AC-149.4 | unit | The `tts-status-pill` element reads `Idle` with `data-tone="neutral"` and classes holding `bg-neutral/10` and `text-fg`. After Generate it reads `Generating` with `data-tone="info"` and `bg-accent-cyan/10`. When done it reads `Done` with `data-tone="success"`. No pill class is a solid `bg-neutral`, `bg-status-pending`, `bg-accent`, `bg-accent-green` or `bg-error`. A job whose `status` is `''` shows the pill as `Idle` with `data-tone="neutral"`, and the page renders without a throw | Local Canon (D-956, handed over) | In Red the pill has no test id; with `??` a blank status would reach `StatusChip`'s throw |
| AC-149.5 | unit | `PILL_CONTRAST_TEST`: all 36 pairs reach 4.5:1, and the calibration case measures the old dark Generating pair at 1.30 | Local Canon (06 §TTS status pill contrast: Floor, Tests; D-235 model); Research-backed (WCAG 2.2 SC 1.4.3, relative luminance) | The calibration pair is the negative |
| AC-149.6 | regression | AC-43.3, AC-43.5 (`queue-primitives.test.ts`) and AC-51.3 (`layout-primitives.test.ts`) pass unchanged. `StatusChip.tsx`, `ProgressBar.tsx`, `status-tokens.ts`, `styles.css` and `ui/tests/e2e/test-ids.ts` keep their row-0 bytes (`scope-paths`, H1-4) | Local Canon (06 Scope: "Queue pills have their own tokens and floor") | A changed token file fails |
| AC-149.7 | e2e | `ui/tests/e2e/tts-generate.test.ts` passes unchanged in the gate's `ui-electron` step | Local Canon (the TTS E2E contract) | — |
| AC-149.8 | docs | `06-gui.md` (CRLF, kept) holds one `> **Delivered (Session 80).**` note under its home section. The note quotes Mat's words from `human-check.md` verbatim | Local Canon (06 Look: "Mat looks at both themes before it ships"; D-806) | A note without the quote fails row 6 |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| The output name scheme | Local Canon (Mat's rc.3 ruling) | D-955: Mat's rc.3 F5 ruling, applied |
| How a name collision is handled | Local Canon | D-957: `_free_paths`, `-2`, `-3` |
| Which characters are safe on Windows | Research-backed | D-958: safe by construction, guarded by tests |
| What the progress label shows | Local Canon | D-959: floored percentage |
| The bar's screen-reader value | Local Canon | D-963: floored like the label, on this page only |
| The pill's look | Local Canon | D-956, handed over: `StatusChip` tones |
| How contrast is measured | Local Canon (D-235 model) | D-960 |
| The API field names | Local Canon | D-962: unchanged |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `ui/src/renderer/src/features/tts/tts-controls.ts` | modify | CRLF, kept | `progressLabel`, `progressFraction`, `TTS_STATUS_TONE`; `STATUS_COLORS` deleted |
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modify | CRLF, kept | The percentage, the bar's label and value, the `StatusChip` pill and its blank-status default |
| `ui/tests/unit/tts-page.test.ts` | modify | CRLF, kept | AC-150.1, AC-149.1; AC-22.24 changed |
| `ui/tests/unit/tts-page.behavior.test.ts` | modify | CRLF, kept | AC-150.2, AC-150.3, AC-149.4; AC-56.5 changed |
| `ui/tests/unit/queue-primitives.test.ts` | modify | CRLF, kept | AC-43.2's census |
| `ui/tests/unit/tts-pill-contrast.test.ts` | new | LF | AC-149.5 |
| `tests/unit/test_tts_output_name.py` | modify | LF, kept | AC-150.4 to AC-150.7 |
| `docs/build-plan/03-service-layer.md` | modify | CRLF, kept | `Delivered (Session 80)` under §TTS output names and progress |
| `docs/build-plan/06-gui.md` | modify | CRLF, kept | `Delivered (Session 80)` under §TTS status pill contrast; the two wireframe strings at `:828` and `:830`; the ProgressBar spec's `"Segment 34/50"` example at `:1228` |
| `.agent/context/known-issues.yaml` | modify (tool) | LF, kept | The three issues resolved through `issue-resolve.py` |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/meu-status.yaml` | modify (tool) | LF, kept | MEU-150 and MEU-149: `ready_for_review`, then `approved` (H2-2) |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | regenerate | LF | `meu_status.py render` |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | modify | LF, kept | §6 row 80 only: `executed (Session 80)` and this plan folder |

Line endings were measured with Python bytes (`C:/Temp/av-kit/tts-page-polish/tpp-eol.txt`, HEAD `6aaf9b0`). Seven of these files are CRLF. A CRLF file is read and written as bytes, or with `newline=""` from CRLF text, and the session gate's `line-endings` step checks every file in this table again.

The grouping §3 lists `services/tts.py` among Session 80's files. It does not change here: rc.3 F5 already did that work (D-955). Row 0 records it as a read-only file by content (`baseline-readonly.json`), with `domain/tts.py`, `StatusChip.tsx`, `ProgressBar.tsx`, `status-tokens.ts`, `styles.css`, `ui/tests/e2e/test-ids.ts`, `ui/tests/e2e/tts-generate.test.ts` and `openapi.committed.json`. No check compares any of them with `HEAD`; H1-4 compares them with their row-0 content.

### Project files

- **Plan-local scripts**, all in this plan folder:
  - `baseline.ps1`: row 0.
  - `red-check.py`: a copy of Session 72's, with `DECLARED_NEW` holding `progressLabel`, `progressFraction` and `TTS_STATUS_TONE`. Its selftest has 64 fixtures and 0 wrong (`tpp-plan-red-selftest.txt`).
  - `identity.py`: a copy of Session 87's, which prints `tested_state <head>+<sha>`.
  - `scope-check.py`: a copy of Session 87's, with this plan's `PLAN`.
  - `issue-resolve.py`: a copy of Session 84's, with `SCRATCH` at `C:/Temp/av-kit/tts-page-polish/issue-resolve` and without `root_cause` in `RESOLVE_KEYS`.
  - `dev-app-procs.py`: a copy of Session 56's (D-458), unchanged below its first lines. Its selftest has 0 failures (`tpp-plan-devapp-selftest.txt`).
  - `session-gate.ps1`: H1-2.
  - `readonly-check.py`: H1-4. It compares the read-only files, and the paths under `packages/` and `mcp-server/`, with their row-0 content, never with `HEAD`. Run against the dry baseline, it exits 0 (`tpp-plan-readonly-dry.txt`).
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-readonly.json`, and the row-0 copies in `C:/Temp/av-kit/tts-page-polish/base/`.
- **Row 5 data:** `human-check.md` (LF).
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the two handoffs, the rolling reviews and the reflection.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json`), not to `HEAD`, and changes only its own entries or lines in it.

| File | Siblings | Rule |
|---|---|---|
| `.agent/context/known-issues.yaml`, `known-issues.md` | Sessions 75 to 79 and 81 to 83 close their own issues. Session 83 rewrites the lines that name the home folder (grouping §2 soft order) | Row 7 changes only the three issues' `status`, `verification` and `resolution_path`, names no home path, and binds to the row-0 hash (S4). Session 83 runs after this one |
| `meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md` | Sessions 75, 77, 81 and 82 | Only MEU-149's and MEU-150's rows change, through `meu_status.py` |
| Grouping §6 table | Every session of the grouping | Only row 80 changes |
| `docs/build-plan/03-service-layer.md` | Session 77 adds two Delivered notes in other sections | Row 0 checks only that the home section exists and holds no Delivered note, and copies the file as it is to `base/`. Row 6 adds one note inside this plan's section |
| `docs/build-plan/06-gui.md` | Session 83 later edits other lines | The same section check. Row 6 changes the note, the two wireframe strings and the `:1228` example only |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

No sibling session edits a product or test file of this plan:

- Session 79 changes `tools/issue_triage*`, which row 7 runs. Row 7 runs the tool as it is at row 7.
- Session 78 changes the E2E launch helper, which the gate's `ui-electron` step uses through `tts-generate.test.ts`.
- Session 81 edits `QueueCard.tsx`, which none of this plan's tests import.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| A name template setting, or any name scheme other than rc.3 F5 | out-of-scope | — | D-955 (option C) |
| Renaming existing uuid-named outputs | out-of-scope | — | 03 Job: "Existing output keeps its name" |
| An exclusive-create (`open("xb")`) reservation of the output name, as `MP3_RESERVE` does for downloads | out-of-scope | — | D-957. The residual risk is another program creating the same name between the check and the write. The MEU-150 handoff names it for triage |
| A real segment count from the service | out-of-scope | — | D-962: the API shape stays; the home allows a percentage |
| Queue pills and their tokens | out-of-scope | — | 06 Scope row |
| Announcing status changes to a screen reader (a live region on the pill) | out-of-scope | — | WCAG 2.2 SC 4.1.3. Only failures reach `role="alert"` today (`TTSPage.tsx:726`), and the pill swap does not change that. The MEU-149 handoff names it for triage |
| MEU-144 and the TTS model assets (Session 74) | out-of-scope | — | Session brief |

## BUILD_PLAN.md Audit

MEU-150 and MEU-149 are registered in `meu-status.yaml` as `pending`:

| MEU | Matrix | Dependencies (all `approved`) |
|---|---|---|
| MEU-150 `svc-tts-output-names-progress` | 3.24 | MEU-12, MEU-22, MEU-77 |
| MEU-149 `gui-tts-status-pill-contrast` | 6.18 | MEU-22, MEU-126 |

Row 7 sets both to `ready_for_review` with this plan's `execution_plan` through `tools/meu_status.py update`, and H2-2 sets both to `approved`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/tts-page-polish/tpp-render-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/tts-page-polish/tpp-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following, fail-fast except where noted:

1. **Tree state.** It records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`. Sessions 75 to 79 may be listed there.
2. **Path-scoped baseline.**
   - It writes `baseline-scope.json`: for each path in §Files Modified, its SHA-256, or `absent`. `ui/tests/unit/tts-pill-contrast.test.ts` and `human-check.md` must be `absent`.
   - It writes `baseline-readonly.json`: the SHA-256 of each of the nine read-only files (`openapi.committed.json`, `domain/tts.py`, `services/tts.py`, `StatusChip.tsx`, `ProgressBar.tsx`, `status-tokens.ts`, `styles.css`, `ui/tests/e2e/test-ids.ts`, `ui/tests/e2e/tts-generate.test.ts`). H1-4 compares against it.
   - It writes `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope, or `deleted`. Another session's new plan folder counts as outside this scope. S4 and the gate's `scope-paths` compare against it.
   - It copies every existing scope file and every read-only file to `C:/Temp/av-kit/tts-page-polish/base/`. That is the row-0 content, and the execution review diffs against it.
3. **S2 binding, by content.** No file is compared with `HEAD`. Sessions 75 to 79 may leave a file of this plan changed and uncommitted; its row-0 content is this plan's baseline, and the receipt prints each product, test and read-only file as `dirty at row 0` or `clean at HEAD`.
   - The two home sections must exist between their anchors and hold no `Delivered` note. The rest of 03 and 06 may hold an earlier session's note.
   - The 06 wireframe's `68%  ·  Segment 34/50     │` and its `Last output: speech_output_2026-05-30.mp3    [`, and the ProgressBar spec line at `:1228`, must each occur once.
   - `tts-controls.ts` must export `STATUS_COLORS` and have no `progressLabel`, `progressFraction` or `TTS_STATUS_TONE` yet. `TTSPage.tsx` must print `Segments`, have no `tts-status-pill`, and still hold `const status = job?.status ?? 'Idle'` and the run bar's `value={segmentsTotal > 0 ? segmentsDone / segmentsTotal : 0}`. These anchors show the code still has the shape rows 2 and 4 edit, whoever changed it last.
   - The three issues must be `open`, MEU-149 and MEU-150 `pending`, and grouping row `| 80 |` `proposed`.
4. **Base receipts.** It runs `uv sync --frozen --all-packages`, the base Python suite (`tpp-base-py.txt`, with `TMP` and `TEMP` at `C:\Temp\av-kit\tts-page-polish\tmp`) and the base UI suite (`tpp-base-ui.txt`). Their failures are recorded, not fatal. The session gate excuses only the Python ids this receipt shows failing, and the UI suite excuses nothing.
5. **Selftests.** It runs the `red-check.py`, `identity.py` and `dev-app-procs.py` selftests.

A plan-time dry run of steps 1 to 3, with its output redirected under `C:/Temp/av-kit/tts-page-polish/dry/`, exits 0 (`tpp-plan-baseline-dry.txt`). Re-run on `HEAD` `3397e78`, it finds 50 dirty paths, 2 of them outside this scope, 16 scope paths, 2 of them absent, and 9 read-only paths. `readonly-check.py --plan-dir` on that dry output exits 0 (`tpp-plan-readonly-dry.txt`).

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require <title>` checks every AC test of the row, and the `.exit` file beside the receipt must hold a non-zero code.
  - Row 1 requires AC-150.1, AC-150.2, AC-150.3 and AC-56.5.
  - Row 3 requires AC-149.1, AC-22.24, AC-43.2, AC-149.4 and AC-149.5.
- **The Python guards are not a Red.** AC-150.4 to AC-150.7 check behaviour that rc.3 shipped. Row 1 writes them and runs them once, expecting a pass. A failure there is S7, because the fix would be a product change that this plan does not hold.
- **New names fail by assertion.** Each test asserts the new export's type before it calls it.
- **Expectations stay immutable in Green.** A Green row that needs a changed expectation stops on S3.
- **Line endings.** The CRLF files are measured with Python bytes and written as bytes. Each Green row checks its files.

### 3. Mat's look (row 5, D-806, M-10)

After row 4, the executor launches the dev app detached, so it outlives the harness:

```powershell
$p = Start-Process pwsh -ArgumentList '-NoProfile','-Command',"Set-Location P:/av-kit/ui; `$env:ELECTRON_RUN_AS_NODE=`$null; npm run dev *> C:/Temp/av-kit/tts-page-polish/tpp-dev-app.txt" -PassThru
rtk proxy uv run python docs/execution/plans/2026-11-15-tts-page-polish/dev-app-procs.py record --root-pid $p.Id --out C:/Temp/av-kit/tts-page-polish/dev-app-launch.json *> C:/Temp/av-kit/tts-page-polish/tpp-dev-app-record.txt
```

`record` waits up to 120 s for the Electron process and the backend under the launched pwsh, and writes each process of that tree as its id, its parent's id, its creation time and a role. It exits 1 if a role never appears (S9).

Then the executor stops and asks Mat, in plain words:

> The TTS page's status pill is now a tinted chip. Please look at it in the dev app that just opened, in both themes:
>
> 1. Open TTS. With a model loaded, the pill reads **Idle**.
> 2. Type a sentence or two and press **Generate**. While it runs, the pill reads **Generating** and the bar shows a percentage, such as `25%`, instead of `Segments 250/1000`.
> 3. When it finishes, the pill reads **Done**. If you press **Cancel** during a run instead, it reads **Cancelled**.
> 4. Switch theme in **Settings** (Light, or Ctrl+Shift+L), and repeat steps 1 to 3 in the other theme.
> 5. Quit the app from the tray.
>
> Is each pill easy to read in both themes? Say "approved", or tell me what to change.

The row writes `human-check.md` (LF) with:

- `decision: approve` or `decision: changes`;
- `human_message_reference: USER_EXPLICIT 2026-11-DD 'words'`, with Mat's words verbatim;
- a "What Mat was asked" section quoting the request above, and a "The launch" section naming the record receipt.

After Mat quits the app, `dev-app-procs.py check --record C:/Temp/av-kit/tts-page-polish/dev-app-launch.json` lists what is left of this launch. If it lists this launch's processes, the row runs it again with `--stop` into `tpp-dev-app-stop.txt`. That ends each process by its id, after checking its creation time again. A process still listed after that is S9. A process it lists as not this launch's belongs to another worktree; it is named to Mat and left alone. The avkit MCP servers are never touched.

- **Approve:** the session goes on to row 6.
- **Changes:** stop (S8). Rows 1 to 4 stay in the work tree. No Delivered note and no register change is written. The change Mat asks for goes back to him as a new decision.

### Session gate (H1-2)

`session-gate.ps1` follows the peers' shape: `2026-11-15-framework-small-syncs/session-gate.ps1` for the runner, and `2026-11-08-light-accent-contrast/session-gate.ps1` for the UI and Electron steps.

- It writes one receipt per step in `C:/Temp/av-kit/tts-page-polish/`, named `tpp-D6-<step>.txt`.
- It is fail-fast: a later step is printed as `not_run`.
- Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity-before` and `identity-after` (`identity.py`); the two `tested_state` lines must match |
| Static | `py-lint` (`ruff check packages/ tests/`); `py-format` (`ruff format --check tests/unit/test_tts_output_name.py`); `py-types` (`pyright packages/`); `ui-types`; `ui-lint`; `task-contract`; `scope-paths` (every changed path is in §Files Modified, this plan folder, the closeout artifacts or `baseline-dirty.txt`, and every `baseline-dirty.txt` path outside this scope keeps its row-0 content); `line-endings` (each §Files Modified file keeps its row-0 kind, and the new test is LF); `red-check-selftest` |
| Targeted | `tts-py-targeted` (`test_tts_output_name.py` and `test_tts_async.py` with `-rs`; a skip fails it); `tts-ui-targeted` (`tts-page`, `tts-page.behavior`, `tts-pill-contrast`, `queue-primitives`, `layout-primitives` and `tts-run-bar`) |
| Fresh full | `py-tests` (`pytest tests/ --tb=short -q -rfE`, with the row-0 baseline rule); `openapi` (`export_openapi.py --check openapi.committed.json`); `ui-tests` (the whole UI suite, which also runs `layout-canon` and `queue-canon` over row 7's register writes); `ui-build`; `state-render` (`meu_status.py render --check`); `issues-render` (`issue_triage.py render --check`) |
| Runtime | `ui-electron` (`npm --prefix ui run test:e2e -- tests/e2e/tts-generate.test.ts`, with `ELECTRON_RUN_AS_NODE` cleared) |
| Skipped, with reason | `mcp-*`: no MCP change, and `openapi` pins the API shape (AC-150.8). `build-record`: no build |

`py-tests` excuses only the ids that row 0's receipt shows failing. `ui-tests` excuses nothing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a new path already present, a scope or read-only file missing, a home section missing or already delivered, or an anchor missing. A file that only differs from `HEAD` is not S2: its row-0 content is the baseline | Stop. An earlier session moved the code this plan edits out of the shape it planned for; bring the diff to Mat |
| S3 | A Red receipt fails `red-check.py`, or a Green row needs a changed expectation | Fix the test setup; do not move to Green, and never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, a `baseline-dirty.txt` path changes content, or `known-issues.yaml` no longer has its row-0 hash at row 7 | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An existing test outside §Existing test assertions that change fails after Green | Stop: that is an M-7 question (§4a), not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | A guard test AC-150.4 to AC-150.7 fails in row 1 | Stop. The shipped name scheme has a defect, and a fix to `services/tts.py` or `domain/tts.py` is outside this plan; brief Mat |
| S8 | Mat answers anything but approval in row 5 | Stop; rows 6 and 7 do not run |
| S9 | `dev-app-procs.py record` exits 1, or a process of this launch is still listed after `--stop` | Stop; name the process ids to Mat |

## Decision Log

> [!NOTE]
> D-957 to D-963 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. D-955 and D-956 are written as Briefs below. D-956 failed the §4 test (a product fork, M-5). D-955 has no M hit: Mat's rc.3 ruling is local canon (HDP §4a M-5), and nothing conflicts with it (M-6). It keeps a brief only because the 03 Name rule (`03-service-layer.md:778`) and triage D-807 (`known-issues.yaml:3218`) ask for a plan-time brief on the scheme. Mat handed this set to the agent on 2026-11-15, so each brief is recorded `resolution: autonomous` with the agent's own tag and its `mandatory:` list. Neither hits an item that stays Mat's, so there is no STOP item. The human check in row 5 is an M-10 action, not a decision, and has no id.
>
> D-455 (Mat's ruling to file the whole pill), D-806 and D-807 (triage), and Mat's rc.3 F5 ruling are applied here, not re-recorded. The grouping rows D-813 to D-817 stay in the grouping file's §8 and are not copied here; H2-2 reads them through `--decision-source` on the grouping file (this plan's `grouping_source`), and D-455, D-806 and D-807 through `--decision-issue` on the three issues (plan-time probe `C:/Temp/av-kit/tts-page-polish/tpp-decision-probe.txt`). The grouping's old "Carry-forward" wording (`:325`, "each row appears in its consuming session's reflection") is ignored under the new HDP §6: the reflection's `### Decisions Log` lists only this session's reversible autonomous choices. D-964 and D-965 are left free for execution.

```yaml
decision_log:
  - id: D-955
    stage: planning
    question: "What name does a TTS output file get in the user's output folder?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: keep the rc.3 F5 scheme Mat ruled on 2026-11-09 (the first three words, lowercase, a dash, then the voice; -2, -3 when taken; speech when no word is left), change no product code, add guard tests, and redraw the 06 wireframe's output example in that form."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-09-rc3-fixes/implementation-plan.md:64-70 — Mat: 'first 3 words from the Text with dash followed by voice'; ruling 'Lowercase slug (Recommended)'"
      - "docs/execution/plans/2026-11-09-rc3-fixes/implementation-plan.md:86 — F5, the shipped scheme"
      - "packages/core/src/avkit_core/domain/tts.py:365-385 — output_stem"
      - "docs/build-plan/03-service-layer.md:740 — downloads: a taken name gains -2, -3 (MP3_RESERVE, D-666)"
      - "packages/core/src/avkit_core/services/capture.py:255 — export_stem: a safe stem plus a tag, or a fallback word (D-612)"
      - "docs/build-plan/03-service-layer.md:774,778 — registered 2026-11-15 from the issue's 2026-11-03 text; the Name rule asks for a plan-time brief"
      - ".agent/context/known-issues.yaml:3218 — D-807: 'The name scheme is a plan-time Decision Brief, because the user sees it in their folder.'"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this set, so the recommendation is chosen. No M item hits: Mat's 2026-11-09 rc.3 ruling is local canon, so M-5 does not apply, and nothing conflicts with it, so M-6 does not either. The 03 home's uuid wording is a stale description, not a conflict: the home was registered on 2026-11-15 from the issue's 2026-11-03 text (last_checked 2026-11-04), and triage D-807 copied it without rechecking the code. The brief is kept, not dropped as an applied ruling like D-455, D-806 and D-807, because the home's Name rule and D-807 both ask for a plan-time brief on the scheme, and keeping it costs Mat no stop. F5 already meets the home's Name rule (says what the clip is, never overwrites, -2 on a taken name), matching how downloads (D-666) and capture exports (D-612, with _2) name files. A date-time prefix lost because it reverses Mat's own words. A template setting lost because nobody asked for one. Two-way: no code changes; the scheme is one function."
  - id: D-956
    stage: planning
    question: "How does the TTS status pill reach 4.5:1 in both themes?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-5]
    chosen: "A: draw the pill with the page's own StatusChip and a per-status tone (Idle and Cancelled neutral, Pending warning, Generating info, Done success, Failed danger): a 10% status-hue fill with text-fg."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/06-gui.md:1640 — the Look row names 'a 10% status-hue fill with text-fg as the queue pills use' as an allowed way"
      - "ui/src/renderer/src/features/tts/TTSPage.tsx:455,537 — the loaded-model and asset chips on the same page are StatusChips"
      - "ui/tests/unit/layout-primitives.test.ts:257-260 — TTSPage adopts StatusChip"
      - "ui/src/renderer/src/components/queue/QueueHeaderRow.tsx:42-48 — toneFor maps queue statuses onto the same StatusChip tones: done success, failed danger, running info, waiting warning"
      - "C:/Temp/av-kit/tts-page-polish/chip-probe.txt — the worst chip pair is 6.86:1 (dark info over bg-elevated); light pairs run 11.39 to 13.50"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this set, so the recommendation is chosen. The chip is a primitive the page already uses, whose tones were measured, and its worst pair clears the floor by a wide margin, so a later token change is unlikely to push it under. The tones follow toneFor in the queue header, so one meaning gets one tone across pages. The page defaults a blank status to Idle with ||, because StatusChip throws on a blank label (StatusChip.tsx:24) where the old span showed nothing. In light the 10% tint is faint by design (about 223,231,237 on f5f6fa for info); the word carries the status, and Mat judges the tint in row 5. The queue StatusBadge lost because it is keyed by queue statuses, so the TTS page would need an alias map and would tie TTS to queue tokens the 06 Scope row keeps apart. Solid fills with a label colour per fill lost because their margins are thin (4.71 and 4.83) and need two new colour rules per theme. Keeping the pill as it is fails the floor. Mat sees the result in row 5 before it ships. Two-way: one component swap."
  - id: D-957
    stage: planning
    question: "How is an output name collision handled?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Keep _free_paths (services/tts.py:84-96): it moves to -2, -3 while the WAV or MP3 name exists; no exclusive-create reservation is added."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/tts.py:84-96 — one generation runs at a time (_current_id), so no job takes the name between the check and the write"
      - "packages/core/src/avkit_core/services/download.py:213-231 — MP3_RESERVE uses open('xb'), because downloads run several jobs at once"
    research: { engine: none, sources: [] }
    reasoning: "The home asks that a name never overwrite an existing file and that a taken name get a suffix; _free_paths does both, and AC-150.6 now pins it against the user's own lone WAV or MP3. The TTS service runs one job at a time, so the only race left is another program writing that exact name during the write, which the handoff names for triage. An exclusive-create reservation lost because it changes the filesystem port's write path, which is beyond this MEU's residual. Two-way."
  - id: D-958
    stage: planning
    question: "What makes a name safe on Windows?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Safe by construction, with guard tests only: output_stem keeps letters and digits per word, joins them with -, and always ends with a dash and the voice id, so no forbidden character, dot, space, trailing dot or reserved device name can appear."
    source_tag: Research-backed
    precedents:
      - "packages/core/src/avkit_core/domain/tts.py:378,384 — each word keeps only isalnum characters; the voice keeps isalnum or _"
      - "docs/build-plan/03-service-layer.md:779 — the Safe rule"
    research: { engine: none, sources: ["Microsoft Learn, Naming files, paths, and namespaces: reserved characters (the angle brackets, colon, double quote, slash, backslash, pipe, question mark and asterisk), control characters, the device names CON PRN AUX NUL COM1-9 LPT1-9 (also COM and LPT with superscript digits) with or without an extension, and no trailing dot or space"] }
    reasoning: "None of the reserved characters is a letter or digit, so none survives the filter. Every stem ends with a dash and the voice id, so its base name is never a bare device name; that also covers COM and LPT with superscript digits, which isalnum keeps. A reserved-name list in code lost because the suffix already rules every one out, and a list could fall out of date. Two-way: tests only."
  - id: D-959
    stage: planning
    question: "What does the run bar show for progress?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A floored percentage, progressLabel(done, total), clamped to 0-100 and 0% when the total is 0 or a value is not finite; the bar's accessible name becomes Generation progress; the 06 wireframe's run-bar line shows the percentage, then the preview and hash, at the same width; the bar's value is floored the same way (D-963)."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/03-service-layer.md:781 — 'shows a percentage, or a real segment count if the service reports one'"
      - "packages/core/src/avkit_core/services/tts.py:45 — TTS_PROGRESS_RESOLUTION = 1000"
    research: { engine: none, sources: [] }
    reasoning: "The home allows a percentage, and the service reports a scale, not a segment count. A floor never shows 100% before the job is done. Rounding lost because 999 of 1000 would read 100% while the job still runs. The accessible name says segments today, which is the same error for a screen reader. Two-way."
  - id: D-960
    stage: planning
    question: "How does the contrast test read and measure the pill?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Read the tokens from styles.css at test time, render StatusChip per status and read its fill, alpha and label classes, and check each label over the fill composited on bg, bg-elevated and surface-0 in both themes at 4.5:1 unrounded, with a calibration case on the old solid fill."
    source_tag: Local Canon
    precedents:
      - "ui/tests/unit/light-accent-contrast.test.ts:1-30 — TINT_MODEL and CONTRAST_FLOOR (D-235, MEU-126)"
      - "docs/build-plan/06-gui.md:1642 — the Tests row"
    research: { engine: none, sources: [] }
    reasoning: "Reading what the chip ships means a later edit to the chip or a token moves the test with nothing to re-pin, as Session 56 did. The three backdrops are the page and card surfaces the run bar can sit on. The calibration case shows the helper can fail. Two-way."
  - id: D-961
    stage: planning
    question: "How are the three issues closed?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Resolve all three through issue-resolve.py bound to the row-0 register hash. root_cause stands as the record of what was seen; resolution_path says the file names were fixed by rc.3 F5 on 2026-11-09 and pinned here, and the label and pill were fixed in this session."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-closeout-record-once/issue-resolve.py — the register tool path"
    research: { engine: none, sources: [] }
    reasoning: "The register is changed only through the tools. Rewriting root_cause lost because it records what was seen on 2026-11-03. Two-way."
  - id: D-962
    stage: planning
    question: "Do the API's segments_done and segments_total names change?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "No. The API, OpenAPI document and MCP shapes stay; only the page's label changes."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/03-service-layer.md:780 — 'The job ID and the API shape are unchanged'"
      - "openapi.committed.json:3925 — segments_total"
    research: { engine: none, sources: [] }
    reasoning: "The home fixes the API shape, so a rename would be an M-4 change with no build-plan basis. The page alone mislabels the scale, so the label is where the fix goes. Two-way."
  - id: D-963
    stage: planning
    question: "How does the run bar's screen-reader value agree with the floored label?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Floor on this page only: tts-controls exports progressFraction(done, total), the same clamp as progressLabel divided by 100, and the run bar passes value={progressFraction(segmentsDone, segmentsTotal)}; ProgressBar.tsx does not change."
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/components/ui/ProgressBar.tsx:78,86 — aria-valuenow is Math.round of the value times 100"
      - "C:/Temp/av-kit/tts-page-polish/tpp-expert-pass.txt:29 — at 999 of 1000 a screen reader hears 100 while the label shows 99%"
    research: { engine: none, sources: [] }
    reasoning: "A floored value makes the bar's rounding a no-op, so aria-valuenow equals the label's number and the fill matches it. aria-valuetext lost because ProgressBar has no prop for it, and adding one changes a shared primitive. A floor inside ProgressBar lost because it changes every other user of the bar (QueueCard, TranscriptPage and this page's download bar). AC-150.1 and AC-150.3 pin it. Two-way: one expression."
  - id: D-964
    stage: execution
    question: "Does red-check.py's pytest header pattern widen to the D-919 form (Session 79 RULE-2)?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "No. red-check.py:86 keeps ^_{3,} (.+?) _{3,}\\s*$ as reviewed; no line of the script changes."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-tts-page-polish/task.md rows 1 and 3 — red-check.py reads only tpp-150-red.txt and tpp-149-red.txt, both Vitest receipts"
      - "docs/execution/plans/2026-11-15-tts-page-polish/implementation-plan.md §Stop Conditions S7 — the Python guards AC-150.4 to AC-150.7 must pass when written; a failure is S7, not a Red"
      - "docs/execution/plans/2026-11-15-tooling-test-hermeticity/red-check.py:82 — the D-919 form, ^_+ (.+?) _+\\s*$"
    research: { engine: none, sources: [] }
    reasoning: "The pattern only splits pytest failure blocks, and no pytest receipt reaches red-check.py in this session: both Red rows feed Vitest receipts, and the Python guards are checked by pytest's own exit code (row 1 stops on S7 if one fails). Widening would change a reviewed script with no receipt to exercise the change, and would move the selftest away from what the plan review approved. A later plan that copies this oracle copies from the newest holder (Session 79 RULE-2), which is Session 76's D-919 form, not this file. Two-way: one regular expression."
  - id: D-1050
    stage: execution
    question: "The first H1-7 Codex dispatch stopped on a usage limit before any review (S6, reviewer unavailable). Wait, or route the review elsewhere?"
    resolution: human
    class: externally-blocked
    mandatory: [M-9]
    chosen: "Wait for Nov 18 (Recommended). Mat then switched the Codex account and asked for a retry; the coordinator re-dispatched round 1 on the same HEAD 771c279 and the same identity.py tested_state, and it approved."
    source_tag: Human-approved
    precedents:
      - "docs/execution/plans/2026-11-15-tts-page-polish/implementation-plan.md §Stop Conditions S6 — Codex unavailable or the ledger refuses: Mat"
      - "C:/Temp/av-kit/dispatch/tpp-exec-r1-usage-limit/ — the failed attempt, kept; the ledger recorded no round for it"
    research: { engine: none, sources: [] }
    reasoning: "The dispatch on 2026-11-16 at about 13:52 exited before any review, with Codex reporting a usage limit ('try again at Nov 18th, 2026 10:00 AM'). Every reviewer rung was unavailable, which is M-9 and the plan's S6, so the choice was Mat's. The coordinator asked him through AskUserQuestion and he chose the recommended wait. He then wrote 'codex account has been switch try again'. Before the second dispatch the coordinator checked that HEAD and identity.py --state-only were unchanged, so the approved round reviewed the gated state."
    human_message_reference: "USER_EXPLICIT 2026-11-16 'Wait for Nov 18 (Recommended)'"
```

Expert pass (fresh context): 2 briefs. Holds: D-956. Changed: D-955. Not adopted: none. Receipt: `C:/Temp/av-kit/tts-page-polish/tpp-expert-pass.txt`.

### D-955: What name does a generated TTS file get in your output folder?

**I recommend A: keep the scheme you chose for rc.3: the first three words, lowercase, a dash, then the voice, such as `hello-world-again-am_eric.mp3`, with `-2`, `-3` when the name is taken.** It already shipped, it says what the clip is, and it never overwrites a file. The plan adds tests that lock it in, and redraws the GUI wireframe's example in this form. You already ruled on this, so nothing is open; the brief is here because the 03 rule for these names asks for one. The 03 section still describes uuid names because it was copied from the 2026-11-03 issue on 2026-11-15 without a fresh look at the code. That text was out of date when it was written, and the Delivered note says so. A can fail if three words are not enough to tell clips apart; then the voice and `-2` still keep the names unique. Undo: one function.

- B: put a date and time first, such as `2026-11-15_1432_hello-world-again.mp3`, as the old wireframe example did. It sorts by time, but it reverses your rc.3 words and makes names longer.
- C: keep things as they are. This is the same as A without the new tests and the wireframe edit.

Refs: rc.3 F5 (`docs/execution/plans/2026-11-09-rc3-fixes/implementation-plan.md:64-70,86`), `domain/tts.py:365-385`, `services/tts.py:84-96`, `03-service-layer.md:774,778`, D-807 (`known-issues.yaml:3218`), D-666, D-612.

### D-956: How does the TTS status pill become easy to read in both themes?

**I recommend A: draw it with the page's own status chip, which has a soft 10% tint of the status colour and normal text.** The same chip already shows the loaded model and the assets on this page, and its tones match the queue header's, so Done, Failed and a running job look the same across pages. Its weakest pair measures 6.86:1, against a floor of 4.5:1. In light the tint is faint by design, because the word carries the status; you judge it in row 5. A can fail if you want the status to stand out more than a tint allows; row 5 is where you say so. Undo: one component swap.

- B: use the queue's status badge. It matches the queue pages, but TTS would need a mapping onto queue statuses, which the GUI spec keeps apart.
- C: keep the solid fills and pick a label colour per fill. The look stays bold, but the margins are thin (4.71:1 and 4.83:1) and need new colour rules in both themes.
- Keep things as they are: Generating and Done read about 1.3:1 in dark, which fails the floor the spec sets.

Refs: 06 §TTS status pill contrast (`06-gui.md:1631-1642`), `QueueHeaderRow.tsx:42-48` (`toneFor`), `TTSPage.tsx:455,537,721-723`, `chip-probe.txt`, `contrast-probe.txt`, D-806, D-455, D-235, M-5.

## Research References

- **WCAG 2.2 SC 1.4.3 Contrast (Minimum):** 4.5:1 for normal text; the `text-xs` label is normal text. The relative-luminance formula uses the 0.04045 threshold, and the ratio is `(L1 + 0.05) / (L2 + 0.05)`. The model is the same as `light-accent-contrast.test.ts`.
- **Microsoft Learn, "Naming files, paths, and namespaces":** lists the reserved characters `< > : " / \ | ? *` and the characters 1 to 31. It lists the reserved names `CON`, `PRN`, `AUX`, `NUL`, `COM0` to `COM9` and `LPT0` to `LPT9`, including the superscript-digit forms, which are reserved with or without an extension. It also says not to end a name with a space or a period.

## Planning receipts

All are under `C:/Temp/av-kit/tts-page-polish/` and were made read-only against the repository:

| Receipt | What it shows |
|---|---|
| `contrast-probe.txt` | Today's pill ratios per status and theme, the solid-fill label options, and the queue-token 10% wash |
| `chip-probe.txt` | The `StatusChip` tones' ratios over three backdrops in both themes; the worst is 6.86 |
| `tpp-decision-probe.txt` | `decision_sources` on the grouping alone reads D-813 to D-817; with the three issues it adds D-455, D-806 and D-807 |
| `tpp-eol.txt` | Line endings, sizes and SHA-256 prefixes of every file in §Files Modified and the read-only files at `HEAD` `6aaf9b0` |
| `tpp-plan-baseline-dry.txt` | `baseline.ps1` steps 1 to 3 on a copy, with output redirected under `dry/`, at `HEAD` `3397e78` |
| `tpp-plan-readonly-dry.txt` | `readonly-check.py` against the dry baseline |
| `tpp-expert-pass.txt` | The §5a expert pass on D-955 and D-956 |
| `tpp-plan-red-selftest.txt`, `tpp-plan-identity-selftest.txt`, `tpp-plan-devapp-selftest.txt` | The plan-local selftests |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the 03 and 06 home sections, the rc.3 F5 ruling and the three issues | `tpp-plan-2026-11-15-tts-page-polish` |
| Row checks | Each row's validation command | `task.md` |
| Human check | Mat's look at both themes | Row 5 |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from the row-0 copies in `C:/Temp/av-kit/tts-page-polish/base/` in the §Files Modified paths (not from `baseline.sha`, which would fold in other sessions' uncommitted work), against AC-150.1 to AC-149.8 | `tpp-execution-2026-11-15-tts-page-polish` |
