---
project: "2026-11-15-convert-settings-drafts"
date: "2026-11-15"
source: "grouping .agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md §3 Session 81; issues SETTINGS-DRAFT-STALE-BASELINE and CONVERT-ADVANCED-EDIT-REPLACED (triage D-808), CONVERT-CUT-TIME-RAW-MS, CONVERT-POSITIONS-NOT-RENUMBERED and CONVERT-CUT-ENCODER-LABEL (triage D-809; Session 54 D-373, D-380)"
meus: ["MEU-151", "MEU-152"]
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
---

# Implementation Plan: Keep settings edits and label the Convert queue truthfully

> **Project**: `2026-11-15-convert-settings-drafts`
> **Build Plan Section(s)**: 06 [§Settings drafts keep edits (residual)](../../../build-plan/06-gui.md#settings-draft-baseline-residual) (MEU-151, matrix 6.19) and 08 [§Convert queue labels (residual)](../../../build-plan/08-video-conversion.md#convert-queue-labels-residual) (MEU-152, matrix 8.11)
> **Status:** said to execute (USER_EXPLICIT 2026-11-15 'proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions.'). `plan_to_exec_gate: human`; the plan review was approved at round 2 (.agent/context/handoffs/2026-11-15-convert-settings-drafts-plan-critical-review.md). **Amended in execution (A1, 2026-11-16):** Mat's row-5 check found that a second Add of the same file overwrote the first job's output, and he chose to fix it in this session (D-1060, USER_EXPLICIT 2026-11-16 'Fix in Session 81'). §Execution amendment A1 says what changed; the amendment goes to a plan review before any A1 product edit. Round 1 of that review, `C:/Temp/av-kit/csd-a1-plan-review-round-1.md` (canonical copy `.agent/context/handoffs/2026-11-16-convert-settings-drafts-amendment-a1-plan-critical-review.md`), found two more overwrite routes (A1-R1-F1, A1-R1-F2); they are corrected inside A1 (D-1064, D-1065). The review approved A1 at round 2 (`C:/Temp/av-kit/csd-a1-plan-review-round-2.md`; the canonical copy above is rolling), with A1-R1-F1 and A1-R1-F2 rechecked fixed, against plan SHA-256 `1b2d711c…` and task SHA-256 `f2ebe98b…`; this sentence was added after that approval, as bookkeeping, not a scope change. **Amended again in execution (A2, 2026-11-16):** Mat replaced row 5's manual round 2 with Electron E2E tests (D-975, USER_EXPLICIT 2026-11-16 'why are you giving me e2e tests manually! This should be done with framework and scripts! It delays the development!'); §Execution amendment A2 says what changed. A2 has no plan review of its own; the H1-7 execution review covers it.

---

## Goal

**Goal anchor:** an open capture settings edit keeps only what the user changed, follows every other saved value and saves only the changed fields; a Convert Advanced edit (CQ, scale, audio) or preset pick survives settings arriving or changing; and a Convert queue card shows a Cut's in and out points as time codes, a waiting job's current place in the queue, and, for a Cut, the encoder it really runs; and two Adds of the same file never queue the same output file (amendment A1).

This is Session 81 of the post-rc.3 grouping (§3: "both are Convert-page debt from the RC1 and Session 54 reviews, and they share `ConvertPage.tsx`"). Order: MEU-151, then MEU-152 (grouping §3).

**MEU-151 (`SETTINGS-DRAFT-STALE-BASELINE`, `CONVERT-ADVANCED-EDIT-REPLACED`).**

- `useCaptureSettings.ts:83-88` copies the whole form into its draft on the first edit (`{ ...(current ?? baseline), ...patch }`). From then on the form stops following a refetch, and `save()` (`:90-98`) writes the stale copy back over the newer values. `useConverterSettings.ts:63-70` already has the fixed shape: a `Partial<ConverterForm>` draft over the latest baseline (AC-112.9, RC1 plan D-212).
- `ConvertPage.tsx:269-280` resets the preset, CQ, scale and audio from `converter.form.default_preset` whenever settings arrive or change, unless `presetTouched` is set, and only `selectPreset` (`:320-327`) sets it. So a CQ, scale or audio edit made before settings load, or before the saved default preset changes, is replaced (RC1, plan D-208: a CQ of 31 went back to 25). The encoder dropdown next to it was fixed under AC-112.8 with `encoderChoice` (`:195-196`).

**MEU-152 (`CONVERT-CUT-TIME-RAW-MS`, `CONVERT-POSITIONS-NOT-RENUMBERED`, `CONVERT-CUT-ENCODER-LABEL`).**

- `convertModeSegment` prints a Cut's raw `in_ms` and `out_ms` (`convert-controls.ts:202-206`, `1000–4500`).
- The stored `queue_position` is 0-based and set once at enqueue (`services/conversion.py:217`, `repositories.py:411-416`; 02 "Rewrite queue_position 0..n-1"). The page prints it as stored (`ConvertPage.tsx:525`), but `QueueCard` documents `position` as 1-based (`QueueCard.tsx:74`) and 10 §zone 2 says "1-based queue position" (`10-queue-card-ui.md:87`). So the first card shows 0, a removed job leaves a gap, and a finished job ahead never lowers the "Waiting - position n in queue" text (`QueueCard.tsx:283-284`).
- `_dispatch` resolves and saves an encoder for every kind except Extract (`services/conversion.py:527-538`, EXTRACT_NO_ENCODER). A Cut never uses it: Fast Copy is `-c copy` and the re-encode is fixed at `libx265` (`media/adapter.py:758-777`). So on an NVIDIA machine a Fast Copy Cut row reads `hevc_nvenc`.

**MEU-152, amendment A1 (`CONVERT-OUTPUT-NAME-REUSED`, found in row 5).**

- `add_to_queue` keeps the output names it hands out in `reserved` (`services/conversion.py:215`), a set local to one call, and `_resolve_output` avoids only a name that is on disk or in that set (`:405-408`). A waiting job has no file yet, so a second Add of the same file, in a separate call, gets the first job's name again. FFmpeg runs with `-y` (`media/adapter.py:439,741,770`), so the second job overwrites the first job's output. 08 says a duplicate destination gets `_1`, `_2` (`08-video-conversion.md:292`). Mat saw it in row 5 (HC-2: 'job 1 and 2 where working on the same video, looks like 2 overwrote 1. But jobs finished'). The row-0 copy of `conversion.py` has the same per-call set, so the defect predates this session (`C:/Temp/av-kit/convert-settings-drafts/cs81-amend-a1-probe.txt`).
- A1's plan review (round 1) found two more routes to the same overwrite, both older than this session. **A1-R1-F1:** `_jobs_for_path` marks a row `Failed` on a probe or track error even when `_resolve_output` returned the skip alias (`:305-320`). With `skip_existing` on and job A running at `clip_cut.mp4` with its partial file on disk, a second Add whose probe fails becomes a `Failed` job at A's path, and `reset_failed` later retries it there. **A1-R1-F2:** Remove and Clear delete the row but do not stop a running media call (`:263-273`), and `_dispatch` still writes its path after the row is gone (`:527-598`). An Add after the remove sees neither a stored row nor a file, gets A's name, and later overwrites A's output.

## Execution amendment A1 (2026-11-16)

- **Why.** Row 5's first round found the overwrite above (HC-2). Mat was offered "Register, continue" (recommended), "Fix in Session 81" and "Record only", and chose "Fix in Session 81" (D-1060). `.agent/workflows/execution-session.md:120` sends a spec gap found mid-execution back to planning and asks for approval of the revised plan, so this amendment goes to a Codex plan review before any A1 product edit. It amends this plan in place; it is not a `-v2` folder (D-1063). Round 1 of that review (`C:/Temp/av-kit/csd-a1-plan-review-round-1.md` (canonical copy `.agent/context/handoffs/2026-11-16-convert-settings-drafts-amendment-a1-plan-critical-review.md`)) returned `changes_required` with A1-R1-F1 and A1-R1-F2. Both are corrected inside A1 as review corrections (D-1064, D-1065, AC-152.18 to AC-152.20): they serve the same rule Mat ruled on, that a second Add never overwrites the first job's output, so they are not a new scope change.
- **What changes.** Three contracts (`QUEUE_OUTPUT_RESERVED`, `QUEUE_ADD_SERIAL`, `ACTIVE_WRITER_RESERVED`); one more edit to `services/conversion.py` (§MEU-152 item 6); one new test file, `tests/unit/test_convert_output_reserved.py` (AC-152.13 to AC-152.16 and AC-152.18 to AC-152.20; AC-152.17 runs existing tests); task rows 4a (Red) and 4b (Green); a fifth human check, HC-5; and a sixth issue, `CONVERT-OUTPUT-NAME-REUSED`, added and resolved in row 7. Decisions D-1060 to D-1065 (D-1064 and D-1065 are the round-1 review corrections). The execution decisions D-973 (row 5's process handling) and D-974 (the red-check pytest header) are still recorded at H1-6, as planned.
- **What stays.** Rows 0 to 4 and their receipts stand, and no expectation they set changes. No API route, OpenAPI document, MCP tool shape, adapter or database schema changes. `tests/unit/test_conversion_service.py`, AC-30.2 included, stays "Read, never changed". AC-30.1's statuses and error reporting are unchanged, and so is what Remove and Clear do to a running media call. `baseline-scope.json` and the other row-0 files are not rewritten; the new test file's absence before A1 is in `cs81-amend-a1-probe.txt`.
- **What reruns.** Row 5 runs again in full on the fixed build, with HC-1 to HC-5. The first round's file is kept as `cs81-human-check-r1.txt`, and the first-round app is stopped the D-973 way before the relaunch. Rows 6 to 8 and H1 run with the counts this amendment sets, and the session gate runs every suite.

## Execution amendment A2 (2026-11-16)

- **Why.** Row 5's second round was set up as a look by Mat in the real app. Mat rejected it: 'why are you giving me e2e tests manually! This should be done with framework and scripts! It delays the development!' (USER_EXPLICIT 2026-11-16, relayed verbatim by the coordinator). That changes how row 5 is validated and adds ACs, so it is his ruling (D-975, `resolution: human`, `mandatory: [M-8]`). The coordinator set no separate plan-review round for A2; the H1-7 execution review covers it.
- **What changes.** Row 5 becomes an Electron E2E row, with one AC per former check, in two new LF files: AC-151.14 (HC-4) in `ui/tests/e2e/capture-settings-draft.test.ts`, and AC-152.21 (HC-1), AC-152.22 (HC-2), AC-152.23 (HC-3) and AC-152.24 (HC-5) in `ui/tests/e2e/convert-queue-labels.test.ts`. Each test launches the built app through `launchElectron` (`ui/tests/e2e/electron-app.ts`) with `AVKIT_APP_DATA` in a new folder under the temp folder, acts on the real backend that main spawns, and makes its fixture clips with FFmpeg in that folder; nothing reads or writes the normal profile, database or settings. The session gate gains the runtime step `ui-electron-a2`. Writing the two files is not an M-7 change: no existing test's assertion changes. The test seams are D-976.
- **What it means for HC-1 to HC-5 and S7.** Round 1's words stay as evidence in `C:/Temp/av-kit/convert-settings-drafts/cs81-human-check-r1.txt` (HC-1, HC-3 and HC-4 pass; HC-2 the overwrite that led to A1). Round 2 has no human answers: its app was stopped the D-973 way (`cs81-dev-app-check.txt`) before Mat answered, and no pass is written for him; `cs81-human-check.txt` states that round 2 was replaced by the E2E tests under D-975, with his words. HC-1, HC-2, HC-3, HC-4 and HC-5 are now AC-152.21, AC-152.22, AC-152.23, AC-151.14 and AC-152.24. AC-152.22 checks HC-2's numbering and waiting texts, and AC-152.24 the overwrite that round 1 reported. HC-3 no longer depends on this PC's GPU: AC-152.23 refuses any encoder name on a Fast copy card and needs a null stored encoder. HC-4's "set it back afterwards" falls away, because the profile is a scratch folder. S7 now covers a failing A2 test too.
- **Red.** HC-1 to HC-4 pin behaviour that rows 2 and 4 already built, so a Red run against this tree is not meaningful; they ran against the current build and pass. HC-5's Red against `b6b124a` is skipped: it needs the service file as it was before row 4b, which means changing the tree or adding a worktree, both outside this session's rules. Row 4a's unit Red already proved the defect (`cs81-a1-red-py.txt`).
- **What stays.** No product file changes, and rows 0 to 4b and their receipts stand. `baseline-scope.json` is not rewritten; row 0's `baseline-dirty.txt` lists neither new file, so both were absent before A2.
- **First runs.** In the first run AC-152.22 failed on the test's own expectation: it said the second job was next after the remove, while the first job still waited. The expectation was corrected before any pass, and no product code changed. Of the three flake runs that followed, r2 failed: AC-152.21 hit the 240 s test timeout with no step named, and the worker then hit its 60 s teardown timeout, on a loaded machine. Nothing it launched was left running. The tests had unbounded waits (ffmpeg, ffprobe and powershell child runs, backend requests and the app close), so they were bounded: each has its own time limit and each step prints a timed `[s81-e2e]` line. If close does not finish, the Electron process that launch started is killed through its own handle, and an afterEach closes an app that a timed-out test left open. No product code changed. Row 5's three runs, after that fix, are the passing evidence. The receipts are in §Planning receipts.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). The change touches two hooks or components, one helper module, one service function and their tests, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern.
  - Receipts go under `C:/Temp/av-kit/convert-settings-drafts/`, named `cs81-*`. Pytest runs with `TMP` and `TEMP` at `C:\Temp\av-kit\convert-settings-drafts\tmp`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
  - Vitest runs from pwsh at `P:/av-kit` through `npm --prefix ui run test -- tests/unit/<files>`; from the Bash tool it fails with "reading 'config'".
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone; a process is stopped only through `dev-app-procs.py`, by the process id and creation time recorded at launch (D-973), never by name or by path alone.
- **Cloud-local contract:** not applicable; the driver OS is the target OS. Row 5's round 1 needed Mat at this PC; since A2 (D-975) row 5 runs as Electron E2E tests on this PC (grouping §3 "Cloud/local: local").
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `csd-plan-2026-11-15-convert-settings-drafts` (as run) and `cs81-execution-2026-11-15-convert-settings-drafts`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
- **Queue:** Session 87 runs and is committed first. Sessions 75 to 80 run before this one, and Mat has not said whether each is committed after it closes, so their changes may be uncommitted when this session starts. Baselines and scope checks are path-scoped and bound to content (§Verification Plan 1). Execution waits for Mat's message (`plan_to_exec_gate: human`).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-151 settings drafts keep edits | `.agent/context/handoffs/2026-11-15-convert-settings-drafts-MEU-151-handoff.md` |
| MEU-152 Convert queue labels | `.agent/context/handoffs/2026-11-15-convert-settings-drafts-MEU-152-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-15-convert-settings-drafts-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-15-convert-settings-drafts-implementation-critical-review.md`

One handoff per MEU follows `2026-11-14-capture-shapes-steps`. Session 54 `convert-extract-index` (plan, MEU-123 handoff, reflection) is the Convert precedent.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`, `baseline-copies/`, `baseline-predecessor.diff`, `cs81-base-py.txt`, `cs81-base-ui.txt` |
| WP-2 | MEU-151: Red, then Green (rows 1 and 2) | WP-1 | shared | `capture-settings-draft.behavior.test.ts`, `useCaptureSettings.ts`, `ConvertPage.tsx` (Advanced fields), the two behavior test files |
| WP-3 | MEU-152: Red, then Green (rows 3 and 4) | WP-2 | shared | `convert-queue-labels.test.ts`, `test_convert_cut_encoder.py`, `convert-time.ts`, `convert-controls.ts`, `QueueCard.tsx`, `ConvertPage.tsx` (cards), `services/conversion.py`; A1 (rows 4a and 4b): `test_convert_output_reserved.py` and `services/conversion.py` again |
| WP-4 | The real-app checks (row 5): round 1 Mat's look (M-10), then Electron E2E tests (A2, D-975) | WP-3 | shared | `ui/tests/e2e/capture-settings-draft.test.ts`, `ui/tests/e2e/convert-queue-labels.test.ts`, `cs81-human-check.txt` |
| WP-5 | Registers and status (rows 6 to 8) | WP-4 | shared | 06 and 08 Delivered notes, `known-issues.yaml` and `.md`, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, grouping §6 row 81 |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | Two handoffs, the review, the reflection |

## User Review Required

> [!IMPORTANT]
> **One choice was a real product fork, and it is handed to the agent.** What the number on a waiting Convert card means had more than one sensible reading. It is written as a brief (D-970, §Decision Log) and settled by your hand-over for this grouping ("like we did here. But use the new HDP process."). One line from you overturns it. Every other decision is autonomous and hits nothing on the §4a list.
>
> **No step needs you now (row 5).** Round 1 of row 5 was your look in the real app, and it found the overwrite that amendment A1 fixed. You replaced round 2 with tests (D-975): row 5 now runs Electron E2E tests against the real app, one per check (AC-151.14 and AC-152.21 to AC-152.24), and the session gate runs them again.
>
> **What changes for you:**
>
> - An open capture settings edit no longer brings back old values: another field saved elsewhere while you edit stays saved, and Save sends only what you changed. A Save with nothing changed sends nothing.
> - A CQ, scale or audio choice on the Convert page stays as you set it when settings load late or when the saved default preset changes. Picking a preset still resets the three, as today.
> - A Cut card reads `00:00:01.000–00:00:04.500`, not `1000–4500`.
> - Queue cards are numbered 1, 2, 3 with no gaps, and a waiting card says where it stands among the waiting jobs now: `Waiting - next`, then `Waiting - 2 in line` and so on (D-970).
> - A Fast Copy Cut shows no encoder; a re-encode Cut shows `libx265`. A Cut no longer runs the GPU check.
> - Adding the same file again while its first job has not finished gives the new job its own output name (`clip_cut_1.mp4`), so the second job no longer overwrites the first one's output (amendment A1, D-1060).
> - A job removed or cleared while it is converting keeps its output name until that conversion stops, and an Add whose file check fails gets its own name too, so neither can overwrite another job's output later (A1 review corrections, D-1064, D-1065).
>
> **What this plan leaves out:** the same raw position on the Downloader and Transcript queues, renumbering the stored positions, the converter Save body, and rewriting old Cut rows (§Out of Scope).

## Proposed Changes

### Single-statement contracts

- **`CAPTURE_DRAFT_CHANGED_ONLY` (MEU-151, D-966):** `useCaptureSettings` keeps `draft: Partial<CaptureForm> | null`; `form` is `{ ...baseline, ...draft }`, recomputed from the latest `query.data`; `patchForm` merges the patch into the draft only (`{ ...current, ...patch }`), never the baseline, and then removes every draft key whose value equals the latest baseline's value for that key; a draft left with no key becomes `null`. So an edit set back to the saved value leaves the draft, and a later refetch shows in that field again.
- **`CAPTURE_SAVE_CHANGED_ONLY` (MEU-151, D-966):** `save()` first validates the merged `form` with `parseSettingsPut('capture', form)` (a refusal throws `SettingsValidationError` and sends no PUT). It then PUTs to `/settings/capture` only the draft keys whose value differs from the latest baseline, in `CaptureForm` key order. When no key differs, it sends no PUT. In both cases it clears the draft and invalidates `CAPTURE_SETTINGS_KEY`. `isDirty` stays `query.data !== undefined && !sameForm(form, baseline)`.
- **`CONVERT_FIELD_CHOICE` (MEU-151, D-967):** `ConvertPage` keeps `presetChoice: PresetWire | null` and `cqChoice`, `scaleChoice`, `audioChoice`, each `null` until the user sets that field. `savedPreset` is `converter.form.default_preset` when `converter.ready`, else `PRESET_DEFAULT`. `preset = presetChoice ?? savedPreset`, and each of `cq`, `scaleHeight`, `audioMode` is its choice, else the value from `presetAdvanced(preset)`. `presetTouched` and the settings effect at `:269-280` are removed. The pattern is AC-112.8's `encoderChoice`. Unlike the capture draft, a choice equal to the preset's value is kept: Convert's choices are picks for the next Add and are never written back to settings, so a kept choice cannot overwrite another client's saved value, and it records that the user picked that value, so a later preset or settings change leaves it (an `encoderChoice` equal to the saved encoder is kept the same way, `ConvertPage.tsx:727`).
- **`CONVERT_PRESET_PICK` (MEU-151, D-967):** `selectPreset(next)` sets `presetChoice` to `next` and clears the three field choices, so CQ, scale and audio show `presetAdvanced(next)`, as today.
- **`CONVERT_TIMECODE` (MEU-152, D-969):** `convert-time.ts` exports `formatConvertTime(ms: number): string | null`, giving `HH:MM:SS.mmm` with two-digit hours, as `format_timecode` (`services/video_input.py:168-173`) does. It returns `null` for a value that is not a finite, whole, non-negative number, or that is above `CONVERT_TIME_MAX_MS = 359_999_999` (`TIME_MAX_MS`, `video_input.py:31`). `parseConvertTime(formatConvertTime(ms))` equals `ms` for every value it formats.
- **`CUT_SEGMENT_TIMECODE` (MEU-152, D-969):** `convertModeSegment` gives a Cut `${formatConvertTime(in_ms)}–${formatConvertTime(out_ms)}`, and `null` (the segment is dropped, as for a sparse Cut) when either side is `null` or does not format.
- **`QUEUE_ROW_NUMBER` (MEU-152, D-970):** `convert-controls.ts` exports `convertQueuePositions(items: readonly { id: string; status: string }[]): Map<string, { row: number; waiting: number | null }>`. `row` is the item's 1-based index in the array as the page renders it (the API's `list_ordered` order). `status` is the queue row's `status: string` (`useConversionQueue.ts:23`). `waiting` is, for a `Pending` item, 1 plus the number of `Pending` items before it, and `null` for every other status. Stored `queue_position` values are not read.
- **`WAITING_POSITION` (MEU-152, D-970):** `QueueCardJob` gains an optional `waitingPosition?: number`. When `waitingPosition` is set, the Pending meta text is `Waiting - next` for 1 and `` `Waiting - ${String(job.waitingPosition)} in line` `` above 1; it never says "position", because on the Convert page Done cards stay above the waiting ones until Clear finished, so the corner number and the waiting rank differ on most waiting cards. When `waitingPosition` is unset, the text stays `` `Waiting - position ${String(job.position)} in queue` ``, byte for byte. Zone 2 still shows `job.position`. `ConvertPage` passes `position: row` and `waitingPosition: waiting ?? undefined` from `convertQueuePositions(items)`. Other pages pass no `waitingPosition`, so their cards render byte for byte as today.
- **`CUT_NO_GPU_ENCODER` (MEU-152, D-968):** in `_dispatch`, a Cut saves `gpu_encoder` `None` when its copy mode is Fast Copy or `None`, and `"libx265"` when it is `Reencode`, and runs neither `detect_gpu` nor `_resolve_encoder`. Compress is unchanged (AC-123.8), and so are Extract (EXTRACT_NO_ENCODER, AC-123.6) and the adapter.
- **`QUEUE_OUTPUT_RESERVED` (MEU-152, amendment A1, D-1061, D-1062, D-1064):** `services/conversion.py` gains `OUTPUT_HOLDING_STATUSES = frozenset({Pending, Processing, Failed, Cancelled})`. Inside its unit of work, `add_to_queue` builds `held`, the `output_path` of each stored job whose status is in that set, from the `list_ordered()` result it already reads for `position`, then adds the running media calls' paths (`ACTIVE_WRITER_RESERVED`), and passes it through `_jobs_for_path` to `_resolve_output` beside the per-call `reserved`. The suffix loop then avoids a candidate that is on disk, in `reserved` or in `held`. The skip test keeps its disk rule (on disk, not in `reserved`, and `skip_existing` on) and gains one condition: the row has no probe or track error (`allow_skip`). So a held name with no file is suffixed and queued `Pending`, never `Skipped`, and AC-30.2 holds as written. A row that ends `Failed` takes the suffix loop like any `Pending` row, so it never gets an existing file's path or a held name and `reset_failed` cannot retry it onto another job's output; its `Failed` status and `error_message` stay as AC-30.1 has them (D-1064, A1-R1-F1). A `Done` or `Skipped` job holds no name: a file on disk already blocks it, and a deleted file frees it. Remove and Clear free a stored name by deleting the row, except while that job's media call runs, when `ACTIVE_WRITER_RESERVED` keeps it held. Paths compare as `Path` values, so case-insensitively on Windows.
- **`QUEUE_ADD_SERIAL` (MEU-152, amendment A1, D-1061):** `ConversionService.__init__` gains `self._add_lock = threading.Lock()`, and `add_to_queue` holds it from its queue read to its commit, probes included, so two Adds at the same time never read the same queue. The lock is per service; the API process builds one `ConversionService` (`wiring.py:228`) and is the one process that writes the queue (the MCP server calls the API over HTTP).
- **`ACTIVE_WRITER_RESERVED` (MEU-152, amendment A1, review correction A1-R1-F2, D-1065):** `ConversionService.__init__` gains `self._active_outputs: set[Path]` and its own `self._writer_lock = threading.Lock()`. `_run_one` adds the job's `output_path` to the set under `_writer_lock` before it first reads the row, and discards it in a `finally` once `_dispatch` has returned or raised. So the name stays held for as long as the media call can write, whether or not the row still exists. `add_to_queue`, holding `_add_lock`, copies the set into `held` under `_writer_lock` after its queue read: a job the worker takes after that read was a stored `Pending` row at the read, and one it took before is already in the set. The worker never takes `_add_lock`, so a slow probe in an Add never delays a job's start or finish. Removing a `Pending` job, or a Clear with no media call running, still frees those names at once. A remove or Clear still does not stop a running media call (unchanged; §Out of Scope).

### MEU-151: drafts that keep edits

1. **`ui/src/renderer/src/features/capture/useCaptureSettings.ts` (CRLF).** Change the draft state to `Partial<CaptureForm> | null`, compute `form` with `useMemo` over `baseline` and `draft`, and rewrite `patchForm` and `save` (`CAPTURE_DRAFT_CHANGED_ONLY`, `CAPTURE_SAVE_CHANGED_ONLY`). A short comment names AC-112.9 and D-966. `CaptureForm`, `CAPTURE_DEFAULTS`, `asForm`, `sameForm` and the returned shape are unchanged, so `CapturePage.tsx:447` and `SettingsPage.tsx:356` need no change.
2. **`ui/src/renderer/src/features/converter/ConvertPage.tsx` (CRLF).**
   - Replace `preset`/`setPreset`, `presetTouched`, `defaults`, `cq`, `scaleHeight` and `audioMode` (`:188-194`) with the four choice states and the derived values (`CONVERT_FIELD_CHOICE`).
   - Delete the settings effect (`:269-280`).
   - Rewrite `selectPreset` (`:320-327`) per `CONVERT_PRESET_PICK`.
   - The CQ, scale and audio `onChange` handlers (`:707`, `:717`, `:723`) set `cqChoice`, `scaleChoice` and `audioChoice`.
   - `buildCreateInput` and `setConvertFormSnapshot` read the derived values, so their wire shapes are unchanged. Drop `useRef` from the React import only if nothing else uses it.

### MEU-152: Convert queue labels

1. **`ui/src/renderer/src/features/converter/convert-time.ts` (CRLF).** Add `CONVERT_TIME_MAX_MS` and `formatConvertTime` (`CONVERT_TIMECODE`) after `parseConvertTime`, with a comment naming `format_timecode` and D-969.
2. **`ui/src/renderer/src/features/converter/convert-controls.ts` (MIXED: 8 bare-LF lines at `:174-177` and `:227-230`, CRLF elsewhere).** Import `formatConvertTime`; change the Cut branch of `convertModeSegment` (`CUT_SEGMENT_TIMECODE`) and its doc comment; append `convertQueuePositions` (`QUEUE_ROW_NUMBER`). Every new or changed line is CRLF; the 8 bare-LF lines stay as they are.
3. **`ui/src/renderer/src/components/queue/QueueCard.tsx` (CRLF).** Add `waitingPosition?: number` to `QueueCardJob` with a doc comment, correct the `position` comment (`:74`, "1-based row in the list the page renders"), and give the Pending text (`:284`) the `WAITING_POSITION` wording, keeping today's text when `waitingPosition` is unset.
4. **`ConvertPage.tsx` (CRLF).** Build `const positions = convertQueuePositions(items)` beside `cards` and map `position` and `waitingPosition` from it (`:523-532`).
5. **`packages/core/src/avkit_core/services/conversion.py` (CRLF).** In `_dispatch` (`:527-532`), add the Cut branch (`CUT_NO_GPU_ENCODER`) before the encoder resolution, and extend the comment to name `CUT_NO_GPU_ENCODER` and D-968. The Cut dispatch (`:579-593`) is unchanged. `queue_position` is not touched (D-970, §Out of Scope).
6. **`packages/core/src/avkit_core/services/conversion.py` (CRLF), amendment A1.** Add `OUTPUT_HOLDING_STATUSES` and, in `__init__` (`:166`), `self._add_lock`. In `add_to_queue` (`:211-227`), take the lock around the unit of work, build `held` from the `list_ordered()` result already read for `position`, and pass it through `_jobs_for_path` (`:285`) to `_resolve_output` (`:387-411`), whose suffix loop (`:408`) also avoids `held` (`QUEUE_OUTPUT_RESERVED`, `QUEUE_ADD_SERIAL`). In `_jobs_for_path` (`:305-320`), work out the row's `error` before calling `_resolve_output` and pass `allow_skip=error is None`; the skip line (`:405`) gains only that condition (D-1064). In `__init__` add `self._active_outputs` and `self._writer_lock`; in `_run_one` (`:498-525`), add the job's `output_path` under `_writer_lock` before the row read and discard it in a `finally` after `_dispatch`; and in `add_to_queue`, copy the set into `held` after the queue read (`ACTIVE_WRITER_RESERVED`, D-1065). `reserved` is unchanged. Comments name the three contracts and D-1060, D-1061, D-1064 and D-1065. Line numbers are those after row 4 (`cs81-amend-a1-probe.txt`).

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `PUT /settings/capture` body from the renderer | `capturePutSchema` (`settings-schemas.ts:80-90`), `routes/settings.py:41` (`model_dump(exclude_unset=True)`) | A subset of the seven capture leaves, each validated as part of the merged form first; the server already writes only the leaves it receives | Unchanged (`.strict()`) |
| `ConversionJob.gpu_encoder` (stored; REST and MCP read) | `domain/conversion.py`; `services/conversion.py` `_dispatch` | Unchanged shape (nullable string). New values for a Cut: `None` or `"libx265"`, as 08 §Cut encoder specifies | Unchanged |
| `QueueCardJob` (renderer-internal) | `QueueCard.tsx` | One optional field, `waitingPosition` | Not a wire shape |
| `ConversionJob.output_path` at enqueue (stored; REST and MCP read) | `services/conversion.py` `add_to_queue`, `_resolve_output` | Unchanged shape. New rule (A1): a new job's path is never the stored path of a `Pending`, `Processing`, `Failed` or `Cancelled` job, nor the path of a media call still running; a new `Failed` job never takes an existing file's path | Unchanged |

No API route, OpenAPI document, MCP tool shape or database schema changes. `queue_position` keeps its stored 0-based values in REST and MCP, so there is no M-4 hit (D-970).

### Acceptance Criteria

Test titles start with the AC id (`AC-151.1 …`, `test_ac_152_10_…`), so `red-check.py --require` matches each exactly.

- **AC-151.1 to AC-151.6 and AC-151.8** are in `ui/tests/unit/capture-settings-draft.behavior.test.ts` (new, LF). The hook tests use `renderHook` inside a `QueryClientProvider` with a fetch stub whose GET answer is a mutable object, as `settings-runtime.test.ts` does. AC-151.8 renders `SettingsPage` with the same stub (testids `settings-leaf-capture-inbox_dir`, `settings-leaf-hotkey`, `capture-settings-save`).
- **AC-151.7** is appended to the describe `'MEU-39 capture GUI runtime (exec r1 F1 F2 F5)'` (`capture-page.behavior.test.ts:190`, CRLF), using its mutable `captureSettings`, `renderPage()`, `flush()` and `putCount()`.
- **AC-151.9** moves two existing pins in `capture-page.behavior.test.ts` (named here, so they are approved scope, not M-7):
  - `:392`, in `'AC-39.4 AC-39.15 Capture page Save PUTs capture settings only when dirty'`: `toMatchObject({ inbox_dir: 'C:/Pictures/inbox-2', hotkey: 'F2' })` becomes `toEqual({ inbox_dir: 'C:/Pictures/inbox-2' })`.
  - `:1231`, in `'AC-57.1 header row: capped page, Capture region first, closed Settings disclosure owns inbox/hotkey/Save'` (`:1202`): `toMatchObject({ inbox_dir: 'C:/Pictures/inbox-3', hotkey: 'F2' })` becomes `toEqual({ inbox_dir: 'C:/Pictures/inbox-3' })`.
- **AC-151.9, D-1066** (Mat's ruling after the first H1-2 gate, 2026-11-16) moves three more existing pins, named here so they are approved scope, not M-7. Each pinned the old seven-key Save after an inbox edit, which CAPTURE_SAVE_CHANGED_ONLY (D-966) ends; each now expects the Save body's keys to be only `inbox_dir`, through its file's `CARD_KEYS` constant, and its title says so. Every other check stays, including AC-143.30's check that the GET keeps `tool_lock`. All three files are LF and stay LF.
  - `ui/tests/unit/capture-shapes.behavior.test.ts`: `AC-107.27 after a step style commit the Capture card's unsaved edit stays and its Save sends only inbox_dir`.
  - `ui/tests/unit/capture-style-flow.behavior.test.ts`: `AC-105.23 a style PUT keeps the Capture card's unsaved edit, whose Save sends only inbox_dir`.
  - `ui/tests/unit/capture-tool-flow.behavior.test.ts`: `AC-143.30 after a Lock click the Capture card's unsaved edit stays, its Save sends only inbox_dir, and the GET keeps tool_lock`.
- **AC-151.10 to AC-151.12** are appended after `:526` to the describe `'MEU-33 convert GUI runtime (exec r1 F1–F4)'` (`convert-page.behavior.test.ts:70`, CRLF), with one new helper beside `savedSettingChangesTo` (`:336`) that changes `converterGet.default_preset` and invalidates the settings query.
- **AC-152.1 to AC-152.8** are in `ui/tests/unit/convert-queue-labels.test.ts` (new, LF). Each test imports the module as a namespace and asserts `typeof … === 'function'` for `formatConvertTime` or `convertQueuePositions` first, so Red fails by assertion (Session 52 RULE-4).
- **AC-152.3** moves one existing pin in `convert-controls.test.ts:229` (CRLF), in `'AC-45.17 convertMetaSegments returns CONVERT_META_SEGMENTS with null fields dropped'` (`:218`): `'1000–4500'` becomes `'00:00:01.000–00:00:04.500'`. The sparse pin at `:252` (`['Cut']`) stays.
- **AC-152.9** is appended to the describe `'MEU-45 ConvertPage queue surface'` (`convert-page.behavior.test.ts:674`), whose fixtures map `queue_position: row.position` (`:714`).
- **AC-152.10 and AC-152.11** are in `tests/unit/test_convert_cut_encoder.py` (new, LF), importing `_stack`, `_nvidia_caps`, `_process`, `_write_clip`, `GpuCountingMedia` and `RecordingMedia` from `tests.unit.test_conversion_service` (the `tests/e2e/test_api_captures.py:874` import shape), each with `@pytest.mark.parametrize("ac_id", …)` and `@pytest.mark.unit`.
- **AC-151.13 and AC-152.12** run existing tests unchanged.
- **AC-152.13 to AC-152.16 and AC-152.18 to AC-152.20** (amendment A1; AC-152.18 to AC-152.20 are the round-1 review corrections) are in `tests/unit/test_convert_output_reserved.py` (new, LF), with the import shape and markers of `test_convert_cut_encoder.py` (`_stack`, `_write_clip` and `RecordingMedia` from `tests.unit.test_conversion_service`; `@pytest.mark.unit`; `@pytest.mark.parametrize("ac_id", …)`). They test behaviour through `add_to_queue`, which exists, so `DECLARED_NEW` gains nothing. AC-152.15 and AC-152.20 are guards and pass in Red. AC-152.18 to AC-152.20 hold the worker with a `RecordingMedia` subclass whose media call waits on a `threading.Event` or `should_stop()` (10 s timeout) and writes bytes naming its call to `output_path`: before the wait for AC-152.18 (FFmpeg's partial file), after it for AC-152.19 and AC-152.20. Each test sets the event in a `finally`, so a Red failure never leaves the worker waiting. **AC-152.17** runs existing tests unchanged.
- **AC-151.14 and AC-152.21 to AC-152.24** (amendment A2, D-975) are Electron tests in `ui/tests/e2e/capture-settings-draft.test.ts` and `ui/tests/e2e/convert-queue-labels.test.ts` (new, LF; the unit files of the same names in `ui/tests/unit/` are other files). Each test launches the built app through `launchElectron` with `AVKIT_APP_DATA` in a new folder under the temp folder, waits for the real backend, and makes its fixture clips with FFmpeg in that folder; the seams are D-976. Titles start with the AC id. They have no Red (§Execution amendment A2).

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-151.1 | unit | The capture hook with a loaded baseline: after `patchForm({ inbox_dir: 'X' })`, the GET answer changes `hotkey` to `F3` and the query refetches; `form` then has `inbox_dir` `X` and `hotkey` `F3`, and the other five leaves follow the new answer. | Local Canon (06 §Settings drafts keep edits: Draft; AC-112.9, D-212; D-966) | In Red the form keeps the hotkey from the first edit, so the `F3` equality fails |
| AC-151.2 | unit | Continuing AC-151.1, `save()` sends exactly one PUT whose parsed body equals `{ inbox_dir: 'X' }` (`toEqual`). | Local Canon (06 Draft: "Save writes only the changed fields"; D-966) | In Red the body holds all seven leaves with the stale hotkey |
| AC-151.3 | unit | An edit set back to the saved value leaves the draft. With saved `hotkey` `F2`: `patchForm({ inbox_dir: 'X' })`, `patchForm({ hotkey: 'F9' })`, `patchForm({ hotkey: 'F2' })`; the GET answer then changes `hotkey` to `F3` and the query refetches; `form.hotkey` is `F3`, and `save()` sends exactly one PUT whose parsed body equals `{ inbox_dir: 'X' }` (`toEqual`). A single edit set back to the saved value leaves `isDirty` false, and `save()` sends no PUT and clears the draft. An edit that a refetch makes equal to the new saved value also sends no PUT. By D-1067 (execution review CS81-R1-F1, added after that review), such an edit leaves the draft for good: with saved `hotkey` `F2`, `patchForm({ inbox_dir: 'X' })` and `patchForm({ hotkey: 'F9' })`, then the GET answer changes `hotkey` to `F9` and the query refetches, then to `F3` and the query refetches again, all before any Save; `form.hotkey` is `F3`, and `save()` sends exactly one PUT whose parsed body equals `{ inbox_dir: 'X' }` (`toEqual`). | Local Canon (06 Draft; D-966; plan review R1-F1; execution review CS81-R1-F1, D-1067) | In Red `form.hotkey` stays `F2` after the refetch and `save()` sends a full PUT |
| AC-151.4 | unit | A `patchForm({ hotkey: 'F9' })` made before the first GET resolves is kept after it resolves, and the other six leaves come from the loaded answer, not from `CAPTURE_DEFAULTS`. | Local Canon (06 Draft; D-966) | In Red the six leaves keep the defaults copied into the draft |
| AC-151.5 | unit | A merged form that `parseSettingsPut('capture', …)` refuses (an `annotated_format` outside `ANNOTATED_FORMATS`) makes `save()` reject with `SettingsValidationError` and sends no PUT. | Local Canon (`settings-schemas.ts:151-164`; D-966) | The refused value is the negative; any PUT fails |
| AC-151.6 | unit | After a successful Save, `isDirty` is false, the draft is empty, and a later GET change shows in `form` for every leaf, the saved one included. | Local Canon (06 Draft; D-966) | A leaf that stays pinned to the draft fails |
| AC-151.7 | unit | Capture page: open the Settings disclosure, change the inbox path, then change `captureSettings.hotkey` to `F7` and refetch; the hotkey field shows `F7`, Save sends one PUT with only `inbox_dir`, and after Save both fields show the merged values. | Local Canon (06 §Settings drafts keep edits: Tests) | In Red the PUT carries `hotkey: 'F2'` |
| AC-151.8 | unit | Settings page Capture card: the same sequence through `settings-leaf-capture-inbox_dir`, a refetch that changes the hotkey, and `capture-settings-save`; `settings-leaf-hotkey` shows the new hotkey and the PUT body is only `inbox_dir`. | Local Canon (06 Tests; D-966) | In Red the hotkey input keeps the old value |
| AC-151.9 | unit | The two moved pins (`capture-page.behavior.test.ts:392` and `:1231`) assert the partial body with `toEqual`; by D-1066, `capture-shapes.behavior.test.ts` AC-107.27, `capture-style-flow.behavior.test.ts` AC-105.23 and `capture-tool-flow.behavior.test.ts` AC-143.30 expect the Save body's keys to be only `inbox_dir`, with every other check unchanged. | Local Canon (06 Draft; named rows, HDP §4a M-7) | In Red the body has seven leaves, so `toEqual` fails |
| AC-151.10 | unit | With settings answered late (`renderConvertBeforeSettings`), a CQ of 31, a scale of 720 and an audio mode other than the preset's, each set before the answer, survive it: the Add body (`window.api` create input) and the command snapshot carry them. | Local Canon (06 Edit kept; RC1 D-208, AC-112.8) | In Red each value returns to the preset's |
| AC-151.11 | unit | With settings loaded, each of the three edits survives a change of the saved default preset, while the preset itself, untouched, follows the new default. | Local Canon (06 Edit kept: "A field the user has not touched still follows them") | In Red the edit is replaced |
| AC-151.12 | unit | Untouched CQ, scale and audio follow a default-preset change; a preset pick resets all three to the picked preset's values; a picked preset is not replaced by a later default-preset change. | Local Canon (06 Edit kept; D-967) | A picked preset that follows the default fails |
| AC-151.13 | unit, e2e | Existing tests pass unchanged: `capture-page.test.ts`, `settings-page.test.ts`, `convert-page.test.ts`, the AC-112.8 and AC-112.9 tests of `convert-page.behavior.test.ts` (`:345-531`), and the Electron tests `W9-3`, `AC-57.10 header` and `AC-67.24` of `ui/tests/e2e/capture-inbox.test.ts`. | Local Canon (AC-39.x, AC-57.x, AC-67.24, AC-112.8, AC-112.9) | A changed Save count, body key or follow rule fails one of them |
| AC-151.14 | e2e | Amendment A2, was HC-4. In the real app with a scratch profile and the real backend: on the Settings page, changing only the capture inbox folder and pressing Save sends one PUT whose body keys are only `inbox_dir`; the saved hotkey is unchanged, in the backend and in the field; the Capture page's Options then show the new folder and the same hotkey. | Local Canon (06 Draft; D-966; D-975) | A PUT with other keys, a changed hotkey, or a Capture page that shows the old folder fails |
| AC-152.1 | unit | `formatConvertTime` exists; `0` gives `00:00:00.000`, `1000` gives `00:00:01.000`, `4500` gives `00:00:04.500`, `3_723_004` gives `01:02:03.004`, `359_999_999` gives `99:59:59.999`. | Local Canon (08 §Convert queue labels: Cut times; `format_timecode`; D-969) | In Red the export is missing, so the `typeof` assertion fails |
| AC-152.2 | unit | `parseConvertTime(formatConvertTime(ms)) === ms` for the AC-152.1 values and `59_999`; `-1`, `1.5`, `NaN`, `Infinity` and `360_000_000` give `null`. | Local Canon (`convert-time.ts:1-25`; `TIME_MAX_MS`; D-969) | The five refused values are the negatives |
| AC-152.3 | unit | `convertMetaSegments` for a Cut with `in_ms` 1000 and `out_ms` 4500 gives `'00:00:01.000–00:00:04.500'` as its mode segment (the moved pin at `convert-controls.test.ts:229`); with `out_ms` `360_000_000` the mode segment is dropped; the sparse Cut (`:252`) still gives `['Cut']`. | Local Canon (08 Cut times; AC-45.17 null-drop rule; D-969) | In Red the segment is `1000–4500` |
| AC-152.4 | unit | `convertQueuePositions` exists; for `[Processing, Pending, Pending]` with stored positions 0, 1, 2 it gives rows 1, 2, 3 and waiting `null`, 1, 2. | Local Canon (08 §Convert queue labels: Position; `10-queue-card-ui.md:87`; D-970, handed to the agent) | In Red the export is missing |
| AC-152.5 | unit | After a finish: `[Done, Processing, Pending, Pending]` gives rows 1 to 4 and waiting `null`, `null`, 1, 2, so the first waiting job reads 1 although two cards are above it. | Local Canon (08 Position: "after a job ahead finishes"; D-970, handed to the agent) | A waiting value counting the Done or Processing card fails |
| AC-152.6 | unit | After a remove: stored positions 0, 2, 5 (a gap) give rows 1, 2, 3 and contiguous waiting values. | Local Canon (08 Position: "is removed"; D-970, handed to the agent) | A row equal to a stored position fails |
| AC-152.7 | unit | After a move: the array order decides, not the stored value (items in the order with stored positions 2, 0, 1 give rows 1, 2, 3 in array order). | Local Canon (08 Position: "is moved"; D-970, handed to the agent) | A row sorted by stored position fails |
| AC-152.8 | unit | `QueueCard` with a Pending job and `position` 3 shows `3` in `queue-card-position` and, with `waitingPosition` 1, the text `Waiting - next`; with `waitingPosition` 2, `Waiting - 2 in line`; neither text contains `position`. Without `waitingPosition` the text is still `Waiting - position 3 in queue`. The existing slot-baseline test of `queue-card.test.ts` passes, and `ui/tests/unit/fixtures/queue-slot-baseline.json` keeps its row-0 hash: its one `Waiting - position` line is on the path without `waitingPosition`, which this plan leaves byte for byte. | Local Canon (`WAITING_POSITION`; D-970, handed to the agent) | In Red the text says `position 3` |
| AC-152.9 | unit | `ConvertPage` over a queue with stored positions 0, 2, 5 and statuses Processing, Pending, Pending shows zone-2 numbers 1, 2, 3 and the waiting texts `Waiting - next` and `Waiting - 2 in line`. | Local Canon (08 Position; D-970, handed to the agent) | In Red the first card shows 0 |
| AC-152.10 | unit | A Fast Copy Cut, and a Cut whose `copy_mode` is `None`, run `Done` with the GPU setting at Auto on NVIDIA capabilities: `gpu_encoder` is `None`, `GpuCountingMedia.detect_gpu_calls` is 0, and the recorded `CutOptions.copy_mode` is `FastCopy`. | Local Canon (08 §Convert queue labels: Cut encoder; EXTRACT_NO_ENCODER; D-968) | In Red `gpu_encoder` is `hevc_nvenc` and the GPU check ran |
| AC-152.11 | unit | A Reencode Cut on NVIDIA capabilities stores `"libx265"` with 0 GPU checks; a Fast Copy Cut with the setting at Software and no software encoder available runs `Done` with no error; a legacy `Failed` Cut row holding `hevc_nvenc`, retried with `reset_failed`, ends `Done` with `None`. | Local Canon (08 Cut encoder and Tests; AC-123.6, AC-123.7 shapes; D-968) | In Red the first stores `hevc_nvenc` and the third keeps it |
| AC-152.12 | integration, e2e | Existing tests pass unchanged: `tests/unit/test_conversion_service.py -k "ac_123_6 or ac_123_7 or ac_123_8 or ac_112_4"`, the rest of `convert-controls.test.ts`, `queue-card.test.ts`, `convert-page.test.ts`, and the Electron file `ui/tests/e2e/convert-queue.test.ts`. | Local Canon (AC-123.6 to AC-123.8, AC-112.4, AC-45.x) | A Compress or Extract encoder change, or a changed card for another page, fails one of them |
| AC-152.13 | unit | Two separate `add_to_queue` calls of the same source, with no output file on disk, give two different output paths, both `Pending`, with `skip_existing` off and on: a Cut gives `clip_cut.mp4`, then `clip_cut_1.mp4`, and a third call `clip_cut_2.mp4`; a Compress gives `clip_compress.mp4`, then `clip_compress_1.mp4`. The Cut case also runs on a SQLite unit of work in `tmp_path` (the `create_sqlite_engine` stack of `test_conversion_service.py:550-566`). | Local Canon (08:292 duplicate destination; HC-2; D-1060, D-1061) | In Red the second call gets `clip_cut.mp4` again |
| AC-152.14 | unit | A first job set to `Processing`, `Failed` or `Cancelled`, with no file on disk, still holds its name, so a later Add gets `_1`. A `Failed` first job sent back with `reset_failed` keeps its path, and it and the later job keep different paths. | Local Canon (08:292; `REQUEUEABLE_CONVERSION_STATUSES`, `domain/conversion.py:56`; `reset_failed`, `:328-337`; D-1061) | In Red the later Add gets the first job's name |
| AC-152.15 | unit | Guard: with no media call running, removing the waiting first job, and `clear_queue`, each free its name for the next Add; a `Done` job whose file was deleted frees its name; a `Done` job whose file is on disk gives `Skipped` with `skip_existing` on and `_1` with it off. | Local Canon (08:292; AC-30.2's skip rule; D-1061, D-1062) | A name still held after a remove or a Clear, or a `Done` row that blocks a deleted file's name, fails |
| AC-152.16 | unit | Two threads call `add_to_queue` at once for the same source, through a `RecordingMedia` subclass whose `probe` waits at a two-party `threading.Barrier` (2 s timeout; `BrokenBarrierError` returns normally): both calls finish within 10 s and get different paths. | Local Canon (`QUEUE_ADD_SERIAL`; the sync route `routes/conversions.py:152-160` runs on FastAPI's thread pool; D-1061) | In Red both threads read the empty queue, pass the barrier together and get the same name; `held` without the lock fails the same way |
| AC-152.17 | integration, e2e | Existing tests pass unchanged: the whole of `tests/unit/test_conversion_service.py` (AC-30.2 included) and `tests/e2e/test_api_conversions.py`. | Local Canon (AC-30.x, AC-31.x) | A changed suffix, skip or route result fails one of them |
| AC-152.18 | unit | Review correction A1-R1-F1. With `skip_existing` on, job A runs at `clip_cut.mp4`, held after writing its partial file. A second Add of the same file whose probe fails gives a `Failed` job B with an `error_message`, at `clip_cut_1.mp4`, never A's path. Once A finishes, `reset_failed(B)` keeps `clip_cut_1.mp4`, and B's retry run, with the probe working, leaves A's file with A's bytes. A probe failure with skip on beside a `Done` job's file on disk likewise gives `Failed` at `_1`, not that file's path. | Local Canon (08:292; AC-30.1; AC-30.2's skip rule; `conversion.py:305-320`; D-1064) | In Red, and with `held` alone, B is `Failed` at `clip_cut.mp4` and its retry overwrites A's file |
| AC-152.19 | unit | Review correction A1-R1-F2, for Remove and for Clear. Job A's media call runs, held before it creates its file; A is removed (or the queue is cleared). An Add of the same file then gets `clip_cut_1.mp4`, not A's path. Released, A's call writes `clip_cut.mp4`, the worker runs B to `Done` at `clip_cut_1.mp4`, and each file holds its own call's bytes. | Local Canon (08:292; `conversion.py:263-273`, `:527-598`; D-1065) | In Red, and with `held` built from stored rows only, B gets `clip_cut.mp4` and A's file ends with B's bytes |
| AC-152.20 | unit | Guard: a running call's name is freed when the call exits. Job A's call is held before it creates its file, A is removed and the processor is cancelled; once the worker is idle and no file exists, an Add of the same file gets `clip_cut.mp4` again. And while A's call runs, removing a second, `Pending` job frees that job's name at once. | Local Canon (D-1061, D-1065) | A name still held after its call exits, or a `Pending` job's name kept after its remove, fails |
| AC-152.21 | e2e | Amendment A2, was HC-1. In the real app, a Fast copy Cut from `00:00:01.000` to `00:00:02.500` of a fixture clip shows `00:00:01.000–00:00:02.500` in its card, waiting (beside `Waiting - next`) and after Done. | Local Canon (08 Cut times; D-969; D-975) | Raw milliseconds or a missing segment fails |
| AC-152.22 | e2e | Amendment A2, was HC-2. In the real app, four queued Cuts read 1 to 4, with `Waiting - next`, `Waiting - 2 in line`, `Waiting - 3 in line` and `Waiting - 4 in line`. Removing the third leaves 1 to 3, the last reading `Waiting - 3 in line`. After Start, once the first is Done and the second runs, the third reads `Waiting - next`, the first shows no waiting text, and the rows stay 1 to 3. | Local Canon (08:646; D-970; D-975) | A gap, a 0, or a waiting text that does not move up fails |
| AC-152.23 | e2e | Amendment A2, was HC-3. In the real app, the card of a Fast copy Cut shows no encoder name in any card text recorded while it waits, runs and is Done, and its stored `gpu_encoder` is null; a re-encode Cut beside it shows `libx265`. | Local Canon (08 Cut encoder; D-968; D-975) | Any encoder name on the copy card fails |
| AC-152.24 | e2e | Amendment A2, was HC-5. In the real app, two separate Adds of one fixture video as Cut (different ranges) give `<stem>_cut.mp4` and `<stem>_cut_1.mp4` in the saved output folder while both wait; after both are Done both files exist, each with its own duration and a different SHA-256. | Local Canon (08:292; D-1060, D-1061; D-975) | One name for both, or one file overwritten by the other, fails |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| What the capture draft holds and what Save sends | Local Canon | 06 Draft row; the converter hook's shape (D-966) |
| Whether a Save with no changed key sends a PUT | Local Canon | No (D-966) |
| How Convert keeps CQ, scale and audio edits | Local Canon | Per-field choices, AC-112.8's pattern (D-967) |
| The Cut time code format and its range | Local Canon | `format_timecode` and `TIME_MAX_MS` (D-969) |
| What a waiting card's number means | Ambiguous local canon (tag `Local Canon`), handed to the agent | D-970 (brief, M-5) |
| A Cut's stored encoder | Local Canon | 08 Cut encoder row (D-968) |
| What else stays as it is | Local Canon | D-971 |
| Where the tests live and what the gate runs | Local Canon | D-972 |
| Whether a second Add may reuse a waiting job's output name (A1) | Local Canon | No (08:292); fixed in this session by Mat's ruling (D-1060, human) |
| Which stored jobs hold a name, and how Adds at the same time are kept apart (A1) | Local Canon | D-1061 |
| `skip_existing` when a name is held but no file exists (A1) | Local Canon | Suffix, not skip (D-1062) |
| Where A1 lives in this plan, and what reruns | Local Canon | D-1063 |
| A `Failed` new row's path when skip is on and its name is taken (A1-R1-F1) | Local Canon | Suffix, never the skip alias (D-1064) |
| How long a removed or cleared job's name stays held (A1-R1-F2) | Local Canon | Until its media call exits (D-1065) |
| How row 5's real-app checks run (A2) | Local Canon | Electron E2E tests in place of a manual round 2, by Mat's ruling (D-975, human); the test seams (D-976) |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `ui/src/renderer/src/features/capture/useCaptureSettings.ts` | modify | CRLF, kept | Partial draft; Save sends changed keys only |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | CRLF, kept | Per-field choices; card positions from `convertQueuePositions` |
| `ui/src/renderer/src/features/converter/convert-time.ts` | modify | CRLF, kept | `CONVERT_TIME_MAX_MS`, `formatConvertTime` |
| `ui/src/renderer/src/features/converter/convert-controls.ts` | modify | MIXED, kept (8 bare-LF lines unchanged; new lines CRLF) | Cut time codes; `convertQueuePositions` |
| `ui/src/renderer/src/components/queue/QueueCard.tsx` | modify | CRLF, kept | Optional `waitingPosition`; corrected `position` comment |
| `packages/core/src/avkit_core/services/conversion.py` | modify | CRLF, kept | `CUT_NO_GPU_ENCODER` in `_dispatch`; `QUEUE_OUTPUT_RESERVED` and `QUEUE_ADD_SERIAL` in `add_to_queue` and `_jobs_for_path`, `ACTIVE_WRITER_RESERVED` in `_run_one` (A1) |
| `ui/tests/unit/capture-settings-draft.behavior.test.ts` | new | LF | AC-151.1 to AC-151.6, AC-151.8 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | CRLF, kept | AC-151.7 appended; the two AC-151.9 pins |
| `ui/tests/unit/capture-shapes.behavior.test.ts` | modify (D-1066) | LF, kept | AC-107.27's Save pin: only `inbox_dir` |
| `ui/tests/unit/capture-style-flow.behavior.test.ts` | modify (D-1066) | LF, kept | AC-105.23's Save pin: only `inbox_dir` |
| `ui/tests/unit/capture-tool-flow.behavior.test.ts` | modify (D-1066) | LF, kept | AC-143.30's Save pin: only `inbox_dir`; the `tool_lock` GET check kept |
| `ui/tests/unit/convert-page.behavior.test.ts` | modify | CRLF, kept | AC-151.10 to AC-151.12, AC-152.9 appended; one helper |
| `ui/tests/unit/convert-queue-labels.test.ts` | new | LF | AC-152.1, AC-152.2, AC-152.4 to AC-152.8 and AC-152.3's out-of-range case |
| `ui/tests/unit/convert-controls.test.ts` | modify | CRLF, kept | The AC-152.3 pin at `:229` |
| `tests/unit/test_convert_cut_encoder.py` | new | LF | AC-152.10, AC-152.11 |
| `tests/unit/test_convert_output_reserved.py` | new (A1) | LF | AC-152.13 to AC-152.16, AC-152.18 to AC-152.20 |
| `ui/tests/e2e/capture-settings-draft.test.ts` | new (A2) | LF | AC-151.14 (Electron) |
| `ui/tests/e2e/convert-queue-labels.test.ts` | new (A2) | LF | AC-152.21 to AC-152.24 (Electron) |
| `docs/build-plan/06-gui.md` | modify | CRLF, kept | A `Delivered (Session 81)` note under §Settings drafts keep edits |
| `docs/build-plan/08-video-conversion.md` | modify | LF, kept | A `Delivered (Session 81)` note under §Convert queue labels, naming A1's suffix rule too |
| `.agent/context/known-issues.yaml` | modify (tool) | LF, kept | `CONVERT-OUTPUT-NAME-REUSED` added through `issue_triage.py add` (A1), then the six issues resolved through `issue-resolve.py` |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/meu-status.yaml` | modify (tool) | LF, kept | MEU-151 and MEU-152: `ready_for_review`, then `approved` (H2-2) |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | regenerate | LF | `meu_status.py render` |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | modify | LF, kept | §6 row 81 only: `executed (Session 81)` and this plan folder |

Line endings were measured with Python bytes (`C:/Temp/av-kit/convert-settings-drafts/cs81-eol.txt`). A CRLF file is read and written with `newline=""` from CRLF text. For the MIXED file the check is that its bare-LF count stays 8. The session gate checks every file in this table again. The A1 test file was added after row 0: `baseline-scope.json` does not list it and is not rewritten, its absence before A1 is in `C:/Temp/av-kit/convert-settings-drafts/cs81-amend-a1-probe.txt`, and the gate's `line-endings` step checks it against this table (LF). A2's two Electron files were added after row 0 as well: `baseline-scope.json` does not list them and is not rewritten, row 0's `baseline-dirty.txt` lists neither (so both were absent at row 0), and the gate's `line-endings` step checks them (LF).

### Project files

- **Plan-local scripts**, all in this plan folder: `baseline.ps1`, `red-check.py`, `identity.py`, `issue-resolve.py`, `session-gate.ps1`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json` in this plan folder; `baseline-copies/` and `baseline-predecessor.diff` in `C:/Temp/av-kit/convert-settings-drafts/`.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the two handoffs, the rolling reviews and the reflection.
- **Read, never changed:** `ui/tests/unit/fixtures/queue-slot-baseline.json` (CRLF), `ui/tests/e2e/convert-queue.test.ts` and `capture-inbox.test.ts` (LF), `tests/unit/test_conversion_service.py` (CRLF). `baseline-scope.json` records them too, and the gate's `scope-paths` refuses a change.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json` and `baseline-copies/`), not to `HEAD`, and changes only its own entries or lines in it (D-971). Row 0 accepts what an earlier session left in a scoped file while the row-0 anchors hold (§Verification Plan 1).

| File | Siblings | Rule |
|---|---|---|
| `.agent/context/known-issues.yaml`, `known-issues.md` | Sessions 75 to 80 and 82 close their own issues before or after this one; Session 79 changes `tools/issue_triage*`, which row 7 runs but never edits; Session 83 rewrites lines that name the home folder, after this one (grouping §2 soft order) | Row 7 changes only the five issues' `status`, `verification` and `resolution_path`, names no home path, and binds to the row-0 hash (S4). If Session 79 changed the render tool, row 7 uses it as it stands |
| `meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md` | Sessions 75, 77, 80, 82 | Only MEU-151's and MEU-152's rows change, through `meu_status.py` |
| Grouping §6 table | Every session of the grouping | Only row 81 changes |
| `docs/build-plan/06-gui.md` | Session 80 (its §TTS status pill home, `:1630-1642`) and Session 82 (§READY line buffering, `:1656` on) add their own Delivered notes; Session 83 may touch home-path lines | Only the one `Delivered (Session 81)` note under `#settings-draft-baseline-residual` is added; the row-8 check counts it, not the file hash |
| `docs/build-plan/08-video-conversion.md` | None in this grouping | Only the one Delivered note is added |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

No sibling session edits a product or test file of this plan (grouping §3; Sessions 75 and 78 touch `capture-inbox.test.ts` or the capture probe, so that E2E file's row-0 content, whatever an earlier session left in it, is the baseline: row 0 records its hash and copy and checks only that the three test titles the gate selects are there, and the gate runs it as it stands).

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| The Downloader and Transcript queues, which also print the stored 0-based `queue_position` (`DownloaderPage.tsx:478`, `transcript-card.ts:134`) | out-of-scope | — | 08 §Convert queue labels covers the Convert queue only (D-971). The MEU-152 handoff names it as a residual for triage |
| Renumbering stored `queue_position` values after a finish, remove or move | out-of-scope | — | 08 Position: "The queue order itself is unchanged"; changing the REST and MCP values would be an M-4 hit (D-970, D-971) |
| The converter Save body (`useConverterSettings`), which still sends the full form | out-of-scope | — | RC1 D-212 set it, and neither issue names it (D-971) |
| Rewriting the `gpu_encoder` of Cut rows already stored | out-of-scope | — | A rewrite of stored data; a retried Cut gets the new value at dispatch, as EXTRACT_NO_ENCODER does (D-968) |
| The adapter's Cut commands | out-of-scope | — | 08 Cut encoder describes what they already do |
| MEU-144 and the TTS model assets (Session 74) | out-of-scope | — | Session brief |
| Stored jobs that already share an output path | out-of-scope | — | A rewrite of stored rows; A1 stops new collisions at enqueue (D-1061) |
| A lock across processes, or a unique index on `output_path` | out-of-scope | — | One API process writes the queue (`wiring.py:228`). An index is a schema change (M-4) and would refuse AC-30.2's `Skipped` row, which shares its path with the first job (D-1061) |
| Stopping a running media call when its job is removed or cleared | out-of-scope | — | A change to what Remove and Clear do while a job runs; A1 keeps the running call's name held instead (D-1065) |
| Checking the output path again when a job starts | out-of-scope | — | The path shown at Add is the path written; A1 keeps that (D-1061) |
| Whether the Downloader and TTS queues name their outputs the same way | out-of-scope | — | Not checked; the MEU-152 handoff names it for triage (D-1063) |

## BUILD_PLAN.md Audit

MEU-151 and MEU-152 are registered (`meu-status.yaml:3931` and `:3957`, `pending`, matrix 6.19 and 8.11; dependencies MEU-33, MEU-39, MEU-112 and MEU-30, MEU-33, MEU-112, MEU-123, all `approved`). Row 8 sets both to `ready_for_review` with this plan's `execution_plan` through `tools/meu_status.py update`, and H2-2 sets both to `approved`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/convert-settings-drafts/cs81-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/convert-settings-drafts/cs81-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. **Tree state.** It records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`. Sessions 75 to 80 may be listed there.
2. **Path-scoped baseline.**
   - It writes `baseline-scope.json`: for each path in §Files Modified and §Project files "Read, never changed", its SHA-256, or `absent`. The three new test files must be `absent`.
   - It writes `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope, or `deleted`. S4 and the gate's `scope-paths` compare against it.
   - It copies each scoped path that exists, byte for byte, to `C:/Temp/av-kit/convert-settings-drafts/baseline-copies/<path>`, and writes `C:/Temp/av-kit/convert-settings-drafts/baseline-predecessor.diff`: `git diff HEAD -- <path>` for each scoped path that `baseline-dirty.txt` lists. The copies are the base of the execution review's delta.
   - It writes `baseline-eol.json`: each scoped path's line-ending kind (CRLF, LF or MIXED) and bare-LF count. A kind other than the one §Files Modified and §Project files give, or a bare-LF count in `convert-controls.ts` other than 8, is S2. Rows 2 and 4 and the gate check against these same kinds.
   - It writes `baseline-skip-hashes.json`: the SHA-256 of each file under `packages/api/` and `mcp-server/` that `git ls-files --cached --others --exclude-standard` lists. H1-4 and the gate's `openapi` and `mcp-*` skips compare against it.
   - It checks the row-0 anchors below in the row-0 content: each string occurs at least once, and the three new test files are `absent`. A missing anchor is S2. A scoped file that an earlier session changed (Sessions 75 and 78 may leave `capture-inbox.test.ts` or the capture files changed) is accepted while its anchors hold. No scoped file is compared with `HEAD`: an earlier session's uncommitted edit is allowed, and under `* text=auto` (`.gitattributes:2`) a CRLF working file never matches its LF blob byte for byte.

   | File | Row-0 anchors (each at least once) |
   |---|---|
   | `useCaptureSettings.ts` | `patchForm`; `parseSettingsPut('capture', form)`; `CAPTURE_SETTINGS_KEY` |
   | `ConvertPage.tsx` | `presetTouched`; `selectPreset`; `position: item.queue_position` |
   | `convert-time.ts` | `export function parseConvertTime` |
   | `convert-controls.ts` | `${row.in_ms}–${row.out_ms}`; `convertMetaSegments` |
   | `QueueCard.tsx` | `Waiting - position ${String(job.position)} in queue` |
   | `services/conversion.py` | `def _dispatch`; `if job.kind is not ConversionKind.Extract:` |
   | `capture-page.behavior.test.ts` | `describe('MEU-39 capture GUI runtime (exec r1 F1 F2 F5)'`; `AC-39.4 AC-39.15 Capture page Save PUTs capture settings only when dirty`; `AC-57.1 header row` |
   | `convert-page.behavior.test.ts` | `describe('MEU-33 convert GUI runtime (exec r1 F1–F4)'`; `async function renderConvertBeforeSettings(`; `async function savedSettingChangesTo(`; `queue_position: row.position` |
   | `convert-controls.test.ts` | `'1000–4500'`; `AC-45.17 convertMetaSegments` |
   | `tests/unit/test_conversion_service.py` | `class RecordingMedia`; `def _stack(`; `def _write_clip(`; `def _nvidia_caps(`; `def _process(`; `class GpuCountingMedia(`; `def test_ac_112_4_`; `def test_ac_123_6_`; `def test_ac_123_7_`; `def test_ac_123_8_` |
   | `ui/tests/e2e/convert-queue.test.ts` | `test('W8-1 `; `test('W8-7 ` |
   | `ui/tests/e2e/capture-inbox.test.ts` | `test('W9-3 `; `test('AC-57.10 header`; `test('AC-67.24 ` |
   | `queue-slot-baseline.json` | `Waiting - position 1 in queue` |
   | `docs/build-plan/06-gui.md` | `<a id="settings-draft-baseline-residual"></a>` |
   | `docs/build-plan/08-video-conversion.md` | `<a id="convert-queue-labels-residual"></a>` |

   At planning time every anchor holds and the three new files are absent (`C:/Temp/av-kit/convert-settings-drafts/anchor-probe.txt`).
3. **Base receipts.** It runs `uv sync --frozen --all-packages`, the base Python suite (`cs81-base-py.txt`, with `TMP` and `TEMP` at `C:\Temp\av-kit\convert-settings-drafts\tmp`) and the base Vitest suite (`cs81-base-ui.txt`).
4. **Plan-local scripts.**
   - It copies `red-check.py` and `identity.py` from `docs/execution/plans/2026-11-15-framework-small-syncs/`, with this plan's `PLAN` and `PROJECT_ARTIFACTS`, and `DECLARED_NEW` extended with `formatConvertTime`, `convertQueuePositions` and `CONVERT_TIME_MAX_MS`.
   - It copies `issue-resolve.py` from `docs/execution/plans/2026-11-15-closeout-record-once/` with `SCRATCH` at `C:/Temp/av-kit/convert-settings-drafts/issue-resolve`.
   - It runs the `red-check.py` and `identity.py` selftests.

If any step fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require AC-<meu>.<n>` (Vitest) and `--require test_ac_<meu>_<n>` (pytest) check every new AC test of the row that fails today, and each moved pin by its existing title (`AC-39.4 AC-39.15 …`, `AC-57.1 header row`, `AC-45.17 …`).
- **Three new tests are guards and pass in Red.** AC-151.5 (a refused value sends no PUT), AC-151.6 (after Save every leaf follows the saved values) and AC-151.12 (untouched fields follow; a pick resets; a picked preset stays) pin behaviour that already holds and must survive the rewrite, so they are not required to fail.
- **A1 adds two guards.** AC-152.15 (with no media call running, a remove, a Clear and a deleted `Done` file free a name; a `Done` file on disk still gives `Skipped`) and AC-152.20 (a running call's name is freed once the call exits) pin behaviour that holds today and must survive the change, so row 4a does not require them. AC-152.13, AC-152.14, AC-152.16, AC-152.18 and AC-152.19 call `add_to_queue`, which exists, so they fail by assertion without an existence check.
- **A2's Electron tests have no Red.** AC-151.14 and AC-152.21 to AC-152.23 pin behaviour that rows 2 and 4 built, and AC-152.24's Red would need the service as it was before row 4b; row 4a's unit Red proved that defect (`cs81-a1-red-py.txt`). Row 5 runs them three times on the current build.
- **New names fail by assertion.** Each test asserts the new export exists (`typeof … === 'function'`, `hasattr`) before it calls it.
- **Moved pins are written in Red.** Rows 1 and 3 change the three named pins (AC-151.9, AC-152.3) to their new values, so they fail in Red against today's code, and Green makes them pass without another edit.
- **Expectations stay immutable in Green.** A Green row that needs a changed expectation stops on S3.
- **Line endings.** The CRLF files are measured with Python bytes and written with `newline=""`; the MIXED file keeps 8 bare-LF lines.

### Session gate (H1-2)

`session-gate.ps1` follows the peer's shape (`2026-11-07-convert-extract-index/session-gate.ps1`, `2026-11-15-closeout-record-once/session-gate.ps1`):

- one receipt per step in `C:/Temp/av-kit/convert-settings-drafts/`, named `cs81-D6-<step>`;
- fail-fast, with later steps printed as `not_run`;
- the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types` (`pyright packages/`); `py-lint` (`ruff check packages/ tests/`); `py-format` (`ruff format --check` on `services/conversion.py`, `tests/unit/test_convert_cut_encoder.py` and `tests/unit/test_convert_output_reserved.py`); `ui-types` (`npm --prefix ui run typecheck`); `ui-lint` (`npm --prefix ui run lint`); `task-contract`; `scope-paths` (every changed path is in §Files Modified, in this plan folder, in the closeout artifacts or in `baseline-dirty.txt`; every "Read, never changed" file and every `baseline-dirty.txt` path outside this scope keeps its row-0 hash); `line-endings` (each §Files Modified file keeps its row-0 kind; the MIXED file keeps 8 bare-LF lines); `red-check-selftest` |
| Targeted | `meu-151-ui` (the new draft file, `capture-page.behavior.test.ts`, `convert-page.behavior.test.ts`, `capture-page.test.ts`, `settings-page.test.ts`, `convert-page.test.ts`); `meu-152-ui` (`convert-queue-labels.test.ts`, `convert-controls.test.ts`, `queue-card.test.ts`); `meu-152-py` (`test_convert_cut_encoder.py`, `test_convert_output_reserved.py`, `test_conversion_service.py` and `tests/e2e/test_api_conversions.py`) |
| Fresh full | `py-tests` (`pytest tests/ --tb=short -q -rfE`); `ui-tests` (`npm --prefix ui run test`); `ui-build` (`npm --prefix ui run build`); `state-render` (`meu_status.py render --check`); `issues-render-check` (`issue_triage.py render --check`) |
| Runtime | `ui-electron-convert` (`npm --prefix ui run test:e2e -- tests/e2e/convert-queue.test.ts`); `ui-electron-capture` (`npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts -g "W9-3|AC-57.10 header|AC-67.24"`); `ui-electron-a2` (`npm --prefix ui run test:e2e -- tests/e2e/capture-settings-draft.test.ts tests/e2e/convert-queue-labels.test.ts`; A2, D-975) |
| Skipped, with reason | `openapi`: every `packages/api/` file keeps its `baseline-skip-hashes.json` hash (H1-4). `mcp-*`: every `mcp-server/` file keeps its `baseline-skip-hashes.json` hash (H1-4); `gpu_encoder` keeps its nullable shape. `build-record`: no build. GUI references: `gui-refs-not-shipped` (no GUI reference image is shipped for these surfaces) |

`py-tests` and `ui-tests` excuse only ids that row 0's receipts show failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a row-0 anchor missing, a new test file present, or a line-ending kind other than the plan's | Stop. An earlier session changed what this plan relies on; bring the missing anchor and `C:/Temp/av-kit/convert-settings-drafts/baseline-predecessor.diff` to Mat. A changed scoped file whose anchors hold is not S2 |
| S3 | A Red receipt fails `red-check.py`, or a Green row needs a changed expectation | Fix the test setup; do not move to Green, and never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path changes content, or `known-issues.yaml` no longer has its row-0 hash at row 7 | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An existing test outside AC-151.9 (with D-1066's three pins: `capture-shapes.behavior.test.ts` AC-107.27, `capture-style-flow.behavior.test.ts` AC-105.23 and `capture-tool-flow.behavior.test.ts` AC-143.30), AC-151.13, AC-152.3, AC-152.12 and AC-152.17 fails after Green | Stop: that is an M-7 question (§4a), not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | Mat reports a fail in row 5 (round 1), or one of row 5's A2 Electron tests fails (D-975) | Record his words, or the failing test and its receipt; fix it inside this plan's ACs and repeat row 5, or, if the fix needs a new AC or a changed rule, stop for Mat (M-8). Row 5's first round found the HC-2 overwrite, and Mat ruled it fixed in this session (D-1060): that is amendment A1, with its plan review's round-1 corrections (D-1064, D-1065) inside the same ruling. A2 (D-975) replaced round 2 with those tests |

## Decision Log

> [!NOTE]
> D-966 to D-969, D-971 and D-972 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. D-970 hit M-5, so it is a brief (below); it is settled by Mat's hand-over for this grouping and recorded `autonomous` with its `mandatory: [M-5]` list kept. Applied rulings get no new record (HDP §6): RC1 D-208 and D-212, Session 54 D-373 and D-380. The grouping rows D-813 to D-817 stay in the grouping file's §8 and are not copied here; H2-2 reads them through `--decision-source` on the grouping file (this plan's `grouping_source`), and the issues' rows (D-373, D-380, D-808, D-809) through `--decision-issue`. The grouping's old "Carry-forward" wording (§9, `:325`, "each row appears in its consuming session's reflection") is ignored under the new HDP §6: the reflection's `### Decisions Log` lists only this session's reversible autonomous choices. D-973 to D-976 are left free for execution. Amendment A1 adds D-1060 to D-1063 at stage `execution`: D-1060 is Mat's ruling (`resolution: human`, `mandatory: [M-8, M-10]`), and D-1061 to D-1063 are autonomous with `mandatory: none`. The A1 plan review's round 1 (A1-R1-F1, A1-R1-F2) adds D-1064 and D-1065, autonomous with `mandatory: none`, as corrections inside D-1060's ruling, and narrows D-1061's release rule. D-973 (row 5's process handling) and D-974 (the red-check pytest header) are recorded here at H1-6, as planned. Amendment A2 adds D-975, Mat's ruling to replace row 5's manual round 2 with Electron E2E tests (`resolution: human`, `mandatory: [M-8]`), and D-976, the tests' seams (autonomous, `mandatory: none`); both are recorded here at H1-6 with D-973 and D-974. D-1066 is Mat's ruling after the first H1-2 gate (`resolution: human`, `mandatory: [M-7, M-8]`): three existing capture tests that pinned the seven-key Save move to the partial body, inside AC-151.9. D-1067 is a correction from the execution review's round 1 (CS81-R1-F1), autonomous under Mat's hand-over (HDP §6) with `mandatory: none`: when the saved answer changes, a draft leaf it now equals leaves the draft, so a second refetch reaches it. It adds one test to the session's own new file under AC-151.3, whose text now names the case; these plan edits were made after that review. D-1068 is autonomous under the same hand-over with `mandatory: none`: the third gate run, after D-1067, failed at `py-tests` on one test this session does not touch, which passed alone three times, so the gate reruns in full from H1-2 with nothing registered in this session. The fourth run failed at `py-tests` on another such test, `test_tts_assets.py` AC-62.16; D-1068 covers it too, and the fifth run went ahead once the host's CPU load was measured at 10%.

```yaml
decision_log:
  - id: D-966
    stage: planning
    question: "What does the capture settings draft hold, and what does Save send?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Only the changed fields, over the latest saved values. patchForm drops a key that a patch sets back to the latest saved value, and the draft becomes null when it empties. Save validates the merged form, then PUTs only the draft keys that differ from the latest saved values; with none, it sends no PUT. Either way it clears the draft."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/06-gui.md:1652 — Draft: the draft holds only the fields the user changed, and Save writes only the changed fields"
      - "ui/src/renderer/src/features/converter/useConverterSettings.ts:63-70 — the converter hook's Partial draft over the latest baseline (AC-112.9)"
      - "docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md:470 — D-212"
      - "packages/api/src/avkit_api/routes/settings.py:41 — the server writes only the leaves it receives"
    research: { engine: none, sources: [] }
    reasoning: "06 states the rule outright, and the converter hook already has the draft shape, so only Save needs a choice. The server writes only the leaves it receives, so a partial body is the only way Save can avoid writing a stale copy of a field the user never touched. Sending the full merged form lost: it writes back the current saved values, which a concurrent save could still race. Validating the merged form keeps today's refusal of a bad value before any request. Skipping a PUT with nothing changed follows from the rule and matches isDirty. Dropping a key set back to the saved value keeps a later refetch visible in that field; a kept key would mask it, and Save would write the old value over another client's (plan review R1-F1). Convert's per-field choices keep a value equal to the preset's (D-967), because they are never written back to settings. Two-way: one function."
  - id: D-967
    stage: planning
    question: "How does the Convert page keep a CQ, scale or audio edit when settings arrive or change?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A choice per field (preset, CQ, scale, audio), null until the user sets it; each shown value is its choice or else the value derived from the current preset, and the current preset is the user's pick or else the saved default. A preset pick clears the three field choices. The settings effect and presetTouched go."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/06-gui.md:1653 — Edit kept: an edited field is not replaced; an untouched field follows settings"
      - "docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md:181 — AC-112.8, encoderChoice over the saved encoder"
      - "ui/src/renderer/src/features/converter/ConvertPage.tsx:320-327 — selectPreset already resets the three fields"
    research: { engine: none, sources: [] }
    reasoning: "Deriving the shown value from a null choice is the pattern AC-112.8 set on the same page, and it removes the effect that causes the bug instead of guarding it. A touched flag per field lost: it keeps the effect and adds three refs that must stay in step with the state. Keeping a pick-resets-the-three rule keeps today's preset behaviour, which neither issue questions. A choice equal to the preset's value stays a choice, unlike a capture draft key (D-966): it is never saved, so it cannot overwrite another client, and it keeps the user's pick when the preset or settings change. Two-way: page-local state."
  - id: D-968
    stage: planning
    question: "What does a Cut store as its encoder?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "None for Fast Copy or a missing copy mode, libx265 for a re-encode, with no GPU check; stored rows are not rewritten, and a retried Cut gets the new value at dispatch."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/08-video-conversion.md:647 — Cut encoder: none for Fast Copy, libx265 for a re-encode"
      - "docs/execution/plans/2026-11-07-convert-extract-index/implementation-plan.md:120 — EXTRACT_NO_ENCODER: no GPU check, and saving None clears an older label at dispatch"
      - "packages/infrastructure/src/avkit_infra/media/adapter.py:758-777 — Fast Copy is -c copy; the re-encode is fixed at libx265"
    research: { engine: none, sources: [] }
    reasoning: "08 states the values, and the adapter shows they are what the Cut runs. Session 54 filed the defect with no Cut change (its D-373 and D-380, applied here, not re-recorded) and set the dispatch-time pattern for Extract, so the same shape is reused. A migration of stored rows lost: it rewrites user data for a label, and a retried job already gets the new value. Two-way: one branch in _dispatch."
  - id: D-969
    stage: planning
    question: "How does a Cut card write its in and out points?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "HH:MM:SS.mmm with two-digit hours, through a new formatConvertTime beside parseConvertTime; a value that is negative, fractional, not finite or above 99:59:59.999 gives null, and then the Cut segment is dropped."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/08-video-conversion.md:645 — Cut times: time codes, per the Media probe timecode"
      - "packages/core/src/avkit_core/services/video_input.py:168 — format_timecode, HH:MM:SS.mmm"
      - "packages/core/src/avkit_core/services/video_input.py:31 — TIME_MAX_MS, the largest value two-digit hours can show"
      - "ui/src/renderer/src/features/converter/convert-time.ts:1 — the Cut inputs parse the same clock form"
    research: { engine: none, sources: [] }
    reasoning: "08 names the timecode format, and the Cut inputs already accept that form, so a card value can be typed back as it reads. Dropping an unformattable segment follows the AC-45.17 rule that a null field is dropped, not shown as a dash. A shorter M:SS form lost: it differs from the inputs and from the probe. Two-way: a display helper."
  - id: D-970
    stage: planning
    question: "What number does a waiting Convert card show?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-5]
    chosen: "A: the card's corner number is its 1-based row in the list as shown, and a waiting card's text gives its rank among the waiting jobs (1 plus the number of waiting jobs ahead of it), worded 'Waiting - next' for 1 and 'Waiting - N in line' above 1, never 'position'; both are worked out in the page, and the stored positions, the API and MCP are unchanged."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/08-video-conversion.md:646 — Position: the number on a waiting card says where it stands in the queue now; the queue order itself is unchanged"
      - "docs/build-plan/10-queue-card-ui.md:87 — zone 2 is the 1-based queue position"
      - "ui/src/renderer/src/components/queue/QueueCard.tsx:74 — position is documented as 1-based"
      - "packages/infrastructure/src/avkit_infra/database/repositories.py:411-416 — stored positions are 0-based and rewritten only on reorder"
      - "packages/core/src/avkit_core/services/conversion.py:217 and :263-267 — add takes the list length and remove does not renumber"
      - "C:/Temp/av-kit/convert-settings-drafts/csd-expert-pass.txt — the HDP 5a expert pass, result changed"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling of the same day ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this brief set. The canon is ambiguous local canon, which is why M-5 applies: 10 and 08 each fix one number and together support both A and B. A keeps the corner number what 10 and QueueCard already say it is, a 1-based row, which also ends today's 0 on the first card, and makes the waiting text the number 08 asks for: it drops when a job ahead finishes, is removed or is moved. The expert pass changed the wording, not the numbers: Done cards stay above the waiting ones until Clear finished, so the two numbers differ on most waiting cards, and the text says 'next' or 'N in line' instead of 'position'. 'N in line' was picked over 'N waiting ahead' because it shows the rank itself, the number 08 says the card gives, and it counts down to 'next'. Reading array order also sidesteps stored positions that can collide after a remove and an add (inference from conversion.py:217 and :263-267, not run). Working it out in the page keeps the stored values, the API and MCP as they are, so there is no one-way change. B, the waiting rank in both places, lost: Done and running cards would have no corner number. E, the corner as index plus 1 with the waiting text reading it, is cheaper but fails 08:646: the number would not drop after a finish while Done cards stay above. C, keeping things as they are, lost: the first card reads 0 and a waiting number never drops, which is the filed defect. D, counting the running job as ahead, lost: it is not waiting, so the next job would read 2. Renumbering on the server lost: it changes the queue_position values REST and MCP return (M-4). Two-way: one helper and one optional field."
  - id: D-971
    stage: planning
    question: "What does this session leave as it is, and how does it share files with the other sessions?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The rows of §Out of Scope stay as they are. Every scoped file, product and test files included, is bound to its row-0 content (hashes and copies), not HEAD; a file an earlier session changed is accepted while the row-0 anchors hold, and only this session's lines in a shared file change."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/08-video-conversion.md:637 — the residual names the Convert queue only"
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:118-127 — the soft order of the sessions that share files"
      - "session brief — baselines path-scoped and bound to content"
      - ".gitattributes:2 — * text=auto: a CRLF working file differs from its HEAD blob byte for byte"
    research: { engine: none, sources: [] }
    reasoning: "Each out-of-scope row is outside both issues and both homes, or would change stored data or a public value. The Downloader's raw position is the same defect on another page, so the handoff names it for triage instead of widening this plan. Content binding lets Sessions 75 to 80 leave uncommitted work in the tree without stopping this one. Row 0 checks the anchors this plan relies on instead of HEAD equality, because Sessions 75 and 78 may leave allowed edits in capture-inbox.test.ts and the capture files, and a CRLF checkout never matches its LF blob byte for byte; after row 0, S4 protects that content (plan review R1-F2). Two-way: a later triage can take any row."
  - id: D-972
    stage: planning
    question: "Where do the new tests live, and what does the session gate run?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Three new LF files for the new behaviour (the capture draft, the queue labels, the Cut encoder), the page-level tests appended to the existing behavior files beside their helpers, and the gate of §Session gate with both Electron files."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-07-convert-extract-index/session-gate.ps1 — the Convert gate shape with ui-electron on convert-queue.test.ts"
      - "tests/e2e/test_api_captures.py:874 — a test imports helpers from tests.unit.test_conversion_service"
      - "ui/tests/unit/convert-page.behavior.test.ts:314 — renderConvertBeforeSettings, the late-settings helper"
    research: { engine: none, sources: [] }
    reasoning: "New files keep each Red run to the new tests, and appending the page tests reuses the existing render helpers instead of copying them. The capture E2E subset covers the three Electron tests that send a capture settings PUT. Two-way: test layout."
  - id: D-1060
    stage: execution
    question: "Mat's row-5 check found that a second Add of the same video overwrote the first job's output (HC-2). Is it fixed in this session?"
    resolution: human
    class: two-way
    mandatory: [M-8, M-10]
    chosen: "Fix in Session 81: amendment A1 (QUEUE_OUTPUT_RESERVED, QUEUE_ADD_SERIAL, ACTIVE_WRITER_RESERVED, AC-152.13 to AC-152.20, task rows 4a and 4b, HC-5, issue CONVERT-OUTPUT-NAME-REUSED), plan-reviewed before any A1 product edit, then row 5 again in full."
    source_tag: Human-approved
    precedents:
      - "docs/build-plan/08-video-conversion.md:292 — a duplicate destination gets _1, _2, or Skipped under skip_existing"
      - "packages/core/src/avkit_core/services/conversion.py:215 — reserved is local to one add_to_queue call"
      - ".agent/workflows/execution-session.md:120 — a spec gap found mid-execution goes back to planning and a revised plan's approval"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-human-check-r1.txt — Mat's row-5 round-1 words, HC-2 the overwrite"
    research: { engine: none, sources: [] }
    reasoning: "S7 sends a fail whose fix needs a new AC to Mat (M-8), and the answer came from him at the row-5 stop (M-10). He was offered Register, continue (recommended: file the defect, which predates this session, and close the session on its own ACs), Fix in Session 81, and Record only, and he chose Fix in Session 81. Two-way: the fix is one service function and one test file."
    human_message_reference: "USER_EXPLICIT 2026-11-16 'Fix in Session 81'"
  - id: D-1061
    stage: execution
    question: "Which stored jobs hold an output name against a new Add, and how are two Adds at the same time kept apart?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A job that is Pending, Processing, Failed or Cancelled holds its stored output_path, and the suffix loop avoids a held name as it avoids a file on disk or a name handed out earlier in the same call. Done and Skipped jobs hold no name. A remove or Clear frees a stored name, except while that job's media call still runs (D-1065). add_to_queue holds a per-service threading lock from its queue read to its commit."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/08-video-conversion.md:292 — duplicate destination: auto-suffix _1, _2"
      - "packages/core/src/avkit_core/services/conversion.py:405-408 — the suffix loop already avoids names reserved within one call"
      - "packages/core/src/avkit_core/domain/conversion.py:56 and :328-337 — a Failed or Cancelled job can go back to Pending with its stored output_path"
      - "packages/api/src/avkit_api/routes/conversions.py:152-160 — a sync route, run on FastAPI's thread pool"
      - "packages/api/src/avkit_api/wiring.py:228 — one ConversionService per API process"
    research: { engine: none, sources: [] }
    reasoning: "Extending the per-call reservation to the stored queue is the smallest change that makes 08:292 hold across Adds. Holding Pending and Processing only lost: reset_failed sends a Failed or Cancelled job back with its stored path, so a later Add given that name would collide again. Holding Done and Skipped too lost: their files on disk already block the name, and a held Done row would keep a deleted file's name taken. Re-resolving the name when a job is sent back lost: it changes a path the card already showed. The unit of work alone lost: pysqlite opens its transaction at the first write, not at the read, so two Adds on the thread pool can read the same queue (an inference from the driver's default, not run); the lock closes that, and AC-152.16 tests it. The lock is held across the probes, so a second Add waits for the first one's ffprobe calls; splitting the probes from the naming lost, because it restructures _jobs_for_path for a wait the user starts. A unique index on output_path lost: it is a schema change (M-4), and AC-30.2's Skipped row shares its path with the first job. Two-way: one service function."
  - id: D-1062
    stage: execution
    question: "With skip_existing on, what does an Add do when its name is held by a job that has not finished and no file exists yet?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "It suffixes the name and queues the job Pending, as with skip_existing off; Skipped still needs the file on disk, so AC-30.2 holds as written."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/conversion.py:405-408 — within one call a reserved name is suffixed, never skipped"
      - "tests/unit/test_conversion_service.py:323-338 — AC-30.2: Skipped needs the file on disk"
      - "docs/build-plan/08-video-conversion.md:292 — Skipped under skip_existing is for a destination that exists"
    research: { engine: none, sources: [] }
    reasoning: "The output name does not encode the job: two Cuts of one file with different ranges both name the source's stem plus _cut and its extension, so skipping the second would drop a different job the user asked for. The in-call rule already suffixes a reserved name with skip_existing on, and this extends it unchanged. Not M-5: local canon (08:292 speaks of a destination that exists) and the in-call precedent decide it. Not M-7: no existing assertion changes. Two-way: one condition."
  - id: D-1063
    stage: execution
    question: "Where does amendment A1 live in this plan, and what reruns?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Under MEU-152, which already changes services/conversion.py in this plan and depends on MEU-30: AC-152.13 to AC-152.20 with one new LF test file, task rows 4a (Red) and 4b (Green), HC-5 in row 5, which runs again in full, and a sixth issue, CONVERT-OUTPUT-NAME-REUSED, added and resolved in row 7; all in this plan folder, with no -v2 folder."
    source_tag: Local Canon
    precedents:
      - ".agent/workflows/execution-session.md:120 — update the plan and get the revised plan approved"
      - ".agent/workflows/execution-session.md:18 — a -v2 folder is for a project replanned on the same day"
      - "docs/execution/plans/2026-11-15-convert-settings-drafts/task.md H1-1 — row ids matching [0-9]+[a-z]? are implementation rows"
      - ".agent/context/meu-status.yaml:3957 — MEU-152, with MEU-30 among its dependencies"
    research: { engine: none, sources: [] }
    reasoning: "MEU-152 already changes conversion.py and labels the Convert queue cards, where the overwrite shows, so a new MEU lost: it adds a registry row and a handoff for one function. Adding the issue to the register now lost: row 7 binds the register to its row-0 hash (S4), so the add runs in row 7 after that check, and the resolve binds to the hash right after the add. A -v2 folder lost: rows 0 to 4 and their receipts stand, and this amends the approved plan rather than replanning it. Rows 4a and 4b keep Red before Green. Two-way: plan layout."
  - id: D-1064
    stage: execution
    question: "A1-R1-F1: with skip_existing on, which path does a new row get when its probe or track check fails and its name is taken?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The skip alias is given only to a row with no error (allow_skip). A row that ends Failed takes the suffix loop, so its path is neither on disk nor held, and reset_failed retries it there; its Failed status and error_message are unchanged (AC-30.1). A genuine Skipped row keeps AC-30.2's alias."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/conversion.py:305-320 — an error makes the row Failed after _resolve_output returned the skip alias"
      - "packages/core/src/avkit_core/domain/conversion.py:328-337 — reset_failed keeps output_path"
      - "tests/unit/test_conversion_service.py:301-320 and :656-678 — AC-30.1 asserts statuses only"
      - "docs/build-plan/08-video-conversion.md:292 — Skipped is for a destination that exists; a job to be written gets _1, _2"
      - "C:/Temp/av-kit/csd-a1-plan-review-round-1.md (canonical copy .agent/context/handoffs/2026-11-16-convert-settings-drafts-amendment-a1-plan-critical-review.md) — A1-R1-F1"
    research: { engine: none, sources: [] }
    reasoning: "A Skipped row is terminal and writes nothing, so sharing an existing path is harmless; a Failed row can be sent back to Pending with its stored path, so it must get a path a job may write. Deciding the error first and skipping the alias keeps the change to one condition in the resolver and leaves every AC-30.1 and AC-30.2 assertion as it is. Re-resolving the path inside reset_failed lost: it changes a path the card already showed (D-1061). Making the row Skipped instead of Failed lost: it hides the probe error AC-30.1 reports. Within D-1060's ruling: it closes another route to the same overwrite. Two-way: one condition."
  - id: D-1065
    stage: execution
    question: "A1-R1-F2: how long does a removed or cleared job hold its output name while its media call may still write?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Until the media call exits. _run_one keeps the job's output_path in _active_outputs under its own _writer_lock, added before its row read and discarded in a finally after _dispatch; add_to_queue copies the set into held after its queue read. Remove and Clear still do not stop a running call. A Pending job's remove, or a Clear with no call running, frees names at once."
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/conversion.py:263-273 — remove and clear_queue delete rows only"
      - "packages/core/src/avkit_core/services/conversion.py:498-525 and :527-598 — _run_one holds the job and _dispatch writes its path after the row is gone"
      - "docs/build-plan/08-video-conversion.md:292 — duplicate destination: auto-suffix _1, _2"
      - "C:/Temp/av-kit/csd-a1-plan-review-round-1.md (canonical copy .agent/context/handoffs/2026-11-16-convert-settings-drafts-amendment-a1-plan-critical-review.md) — A1-R1-F2"
    research: { engine: none, sources: [] }
    reasoning: "The writer, not the row, decides whether a path can still be written, so the reservation follows the writer. A set in the service is enough because one process runs the worker and the Adds (wiring.py:228). Reading it after the queue read leaves no gap: a job the worker takes later was a stored Pending row at the read, and one it took earlier is already in the set. Its own lock, not _add_lock, keeps a slow probe from delaying the worker. Making Remove and Clear stop the running call lost: it changes what they do (AC-30.10 keeps files, and the Pause and Cancel paths own stopping), which is outside A1. Refusing to remove a running job lost: it changes an API result. Within D-1060's ruling: it closes another route to the same overwrite. Two-way: one service class."
  - id: D-973
    stage: execution
    question: "How does row 5 stop the dev app it launched, when other worktrees and Mat's own app run Electron processes under P:/av-kit/ui?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Row 5 starts the dev app detached with Start-Process -PassThru, records the process tree under that pwsh with dev-app-procs.py record (each process's id, parent id, creation time and role), and stops it only with dev-app-procs.py check --stop, which ends a process by its id after checking its creation time again. Nothing is stopped by name or by path alone, and the avkit MCP servers never count. Both rounds' apps were stopped this way."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-convert-settings-drafts/task.md:38 — the Processes rule: record at launch, stop only through check --stop, by id and creation time"
      - "docs/execution/plans/2026-11-15-convert-settings-drafts/dev-app-procs.py:1 — a copy of Session 80's checker, unchanged below its first lines"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-dev-app-check-r1.txt — round 1: 14 of this launch's left, 0 not this launch's; after --stop 0 left, 0 not this launch's"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-dev-app-check.txt — round 2, stopped before Mat answered (D-975): the same counts"
    research: { engine: none, sources: [] }
    reasoning: "A process id alone can be reused, so the creation time is checked again before each stop. Stopping by name lost: Mat's app and other sessions' apps run electron.exe from the same folder. Stopping by path lost for the same reason. Waiting for Mat to quit with no check lost: an orphaned backend would hold the profile and its port. Two-way: a plan-local script."
  - id: D-974
    stage: execution
    question: "Does this session's copy of red-check.py take the D-919 pytest header form?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Yes. red-check.py:91 is ^_+ (.+?) _+\\s*$, Session 76's D-919 form, because rows 3 and 4a feed pytest receipts whose parametrized titles can be wider than the terminal, and pytest then frames them with one underscore on each side."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-tooling-test-hermeticity/red-check.py:82 — the D-919 form"
      - "docs/execution/plans/2026-11-15-tts-page-polish/implementation-plan.md D-964 — not widened there, because no pytest receipt reached its red-check.py; a later copy takes the newest holder's form (Session 79 RULE-2)"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-152-red-py-check.txt — red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-a1-red-py-check.txt — red-check: 1 receipt(s), 5 required test(s), 0 problem(s)"
    research: { engine: none, sources: [] }
    reasoning: "The pattern only splits pytest failure blocks. Here two Red rows feed pytest receipts, and the A1 titles such as test_ac_152_18_failed_add_beside_running_job[AC-152.18-probe-fail-beside-running] are long enough to get one underscore on a side, which the older ^_{3,} form would miss, so a failing test would go uncounted. Keeping the older form lost for that reason. Two-way: one regular expression, pinned by the script's selftest."
  - id: D-975
    stage: execution
    question: "Row 5's second round was set up as Mat's look in the real app. How is row 5 validated instead?"
    resolution: human
    class: two-way
    mandatory: [M-8]
    chosen: "Amendment A2: Electron E2E tests replace the manual round 2, one AC per former check: AC-151.14 (HC-4) in ui/tests/e2e/capture-settings-draft.test.ts, and AC-152.21 (HC-1), AC-152.22 (HC-2), AC-152.23 (HC-3) and AC-152.24 (HC-5) in ui/tests/e2e/convert-queue-labels.test.ts. Row 5 runs them three times, and the session gate runs them again as ui-electron-a2. Round 1's words stay as evidence, and no round-2 result is written for Mat."
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-human-check-r1.txt — Mat's round-1 words, kept"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-human-check.txt — round 2 replaced under D-975; Mat gave no round-2 pass or fail"
      - "ui/tests/e2e/electron-app.ts:69 — launchElectron, which drops ELECTRON_RUN_AS_NODE and needs a scratch profile"
    research: { engine: none, sources: [] }
    reasoning: "The change sets new ACs and a new way to validate row 5, so it is Mat's call (M-8), and he made it in his own words. The tests check what the manual round would have checked, on the built app with the real backend, and they run again in the gate, so a later change is caught without a person. Red is not meaningful for AC-151.14 and AC-152.21 to AC-152.23, which were written after the product fix; AC-152.24's Red was not run, because the A1 fix it checks was already in place (§Execution amendment A2). Two-way: two test files."
    human_message_reference: "USER_EXPLICIT 2026-11-16 'why are you giving me e2e tests manually! This should be done with framework and scripts! It delays the development!'"
  - id: D-976
    stage: execution
    question: "Which seams do the A2 Electron tests use to drive the real app without touching the normal profile or other sessions' processes?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Five seams. (1) AVKIT_APP_DATA is a new folder under tmpdir() for each launch, and fixture clips and output folders are made with ffmpeg inside it. (2) The tests wait past main's port-9 placeholder backend until the real backend answers. (3) The Convert file picker is the one IPC handler show-files-dialog, replaced inside main through app.evaluate with one that returns the test's paths; nothing else in main changes. (4) The backend that main spawned is found by its pid in the scratch profile and stopped by that pid and its start time, never by name. (5) Every wait, child process and request is bounded, and if app.close does not finish in time, the Electron process this launch started is killed through its own handle."
    source_tag: Local Canon
    precedents:
      - "ui/src/main/index.ts:150 and :223 — AVKIT_APP_DATA moves the whole profile"
      - "ui/src/main/index.ts:475 and :630 — the port-9 placeholder published before the backend is ready"
      - "ui/src/main/ipc.ts:369 — the show-files-dialog handler"
      - "ui/tests/e2e/convert-queue-labels.test.ts:281-285 — the handler replaced through app.evaluate"
      - "ui/tests/e2e/capture-settings-draft.test.ts:132-147 and ui/tests/e2e/convert-queue-labels.test.ts:218-233 — the bounded close"
    research: { engine: none, sources: [] }
    reasoning: "A scratch profile keeps the normal database and settings untouched, as the brief requires. Waiting on the real backend avoids a request to the placeholder. A native dialog cannot be driven by Playwright, and replacing the one handler leaves the page's own Add path in use. Stopping the backend by pid and start time follows D-973's rule. Unbounded waits made an early run hang until the test timeout; with bounds, a slow step fails with its own name, and row 5's third run shows the close bound at work (an app.close that did not finish, then the kill through the handle, with nothing left over). Changing main or adding a test-only route lost: it is a product change outside A2. Two-way: two test files."
  - id: D-1066
    stage: execution
    question: "The first H1-2 gate failed on three existing capture tests that pin the old seven-key Save after an inbox edit. Change them, or keep the seven-key Save?"
    resolution: human
    class: two-way
    mandatory: [M-7, M-8]
    chosen: "Update the three tests: capture-shapes.behavior.test.ts AC-107.27, capture-style-flow.behavior.test.ts AC-105.23 and capture-tool-flow.behavior.test.ts AC-143.30 each expect the Save body's keys to be only inbox_dir, through the file's CARD_KEYS constant, with its title changed to say so. Every other check stays, including AC-143.30's check that the GET keeps tool_lock. They join AC-151.9 and S5's named tests. The gate then reruns in full from H1-2. In the same rerun, the A2 file ui/tests/e2e/convert-queue-labels.test.ts names its app.evaluate callback's first parameter _app, not _electron, so e2e-harness.test.ts AC-2 (only electron-app.ts names the Playwright launcher) passes; nothing that test checks changes."
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-gate-h1-run1.txt — the first gate: ui-tests 4 failed, 1565 passed; AC-107.27, AC-105.23 and AC-143.30 expected seven keys and got only inbox_dir, and e2e-harness AC-2 listed convert-queue-labels.test.ts beside electron-app.ts"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-d1066-check.txt — the three changed files and e2e-harness.test.ts after the change: 4 files, 139 tests passed"
      - "D-966 — CAPTURE_SAVE_CHANGED_ONLY, the rule the three pins contradicted"
      - "AC-151.9 — the two capture-page.behavior.test.ts pins moved the same way"
    research: { engine: none, sources: [] }
    reasoning: "The three tests are outside the plan's named rows, so changing their assertions is M-7, and S5 stopped the session for Mat (M-8). He chose to update them. The other choices were to keep the seven-key Save, which reverses D-966 and reopens SETTINGS-DRAFT-STALE-BASELINE, or to leave the gate failing and hold the session. Two-way: three test constants and titles."
    human_message_reference: "USER_EXPLICIT 2026-11-16 AskUserQuestion, option chosen: 'Update the 3 tests (Recommended)'"
  - id: D-1067
    stage: execution
    question: "The execution review's round 1 (CS81-R1-F1) found that a draft leaf a refetch makes equal to the saved value stays in the draft, so a second refetch cannot reach it. How does the capture draft drop such a leaf, without a stale form on screen?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "useCaptureSettings keeps the baseline it last pruned for. When the baseline changes, the same render sets that baseline and replaces the draft with changedOnly(draft, baseline): every leaf equal to the new baseline leaves the draft for good, the other differing leaves stay, and a draft left empty becomes null. The prune runs during render (React's adjust-state-on-change pattern), so React discards that render and renders again before committing, and no committed render shows the stale leaf. AC-151.3 gains the two-refetch test in ui/tests/unit/capture-settings-draft.behavior.test.ts."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/cs81-exec-review-round-1.md — CS81-R1-F1, High, at useCaptureSettings.ts:106"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-d1067-red.txt — the new AC-151.3 test against the unchanged hook: 1 failed, 9 passed; expected 'F9' to be 'F3'"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-d1067-green.txt — the six MEU-151 files after the fix: 301 passed"
      - "D-966 — CAPTURE_DRAFT_CHANGED_ONLY, which the fix completes: the rest come from the latest answer"
    research: { engine: none, sources: [] }
    reasoning: "The review's rule is that a leaf the saved answer catches up to is no longer an edit, and only an edit may hide a later answer. Pruning in an effect keyed on the baseline lost: the effect runs after the commit, so one committed render shows F9 before the prune lands. A ref holding the previous baseline lost: React's rules forbid reading or writing a ref during render, because a discarded render would still have changed it. Pruning only inside form's useMemo lost: the stale leaf stays in the draft, so Save would still send it. Not on the §4a list: it changes no existing assertion (the test is the session's own new one, so not M-7), no stored data, schema or contract, and it follows D-966's own words. Two-way: one hook block and one test."
  - id: D-1068
    stage: execution
    question: "The third H1-2 gate run, after D-1067, failed at py-tests on tests/integration/test_youtube_adapter.py::test_ac_122_8_surrogate_title_survives_real_storage, and the fourth on tests/integration/test_tts_assets.py::test_ac_62_16_model_overshoot_is_clipped_not_failed; this session touches neither. Rerun the gate, register the flakes, or hold the session?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Rerun the whole gate from H1-2 as written, and register nothing in this session; the coordinator registers the flake after Session 81 commits, so this session's issue-register delta stays row 7's issues. The third run's receipts are kept as cs81-gate-h1-run3.txt and gate-run3/. If the fourth run fails again on the same test, the session stops; any other failure is a stop as usual. The fourth run's receipts are kept as cs81-gate-h1-run4.txt and gate-run4/. The fifth run went ahead after the coordinator measured the host's CPU load at 10%; if it fails on any test, the session stops and the three timing failures go to Mat."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-gate-h1-run3.txt — py-tests exit=1: 1 failed, 3031 passed, 37 warnings in 676.19s (the second run took 457.59s); the steps after it not_run by fail-fast"
      - "C:/Temp/av-kit/convert-settings-drafts/gate-run3/cs81-D6-py-tests.txt — test_youtube_adapter.py:940 got TranscriptStatus.Processing after service._thread.join(timeout=5)"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-d1067-py-diag.txt — the same test alone, three times: 1 passed in 2.93s, 0.47s, 0.50s"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-gate-h1-run2.txt — the second run passed the same test with the same Python code"
      - "C:/Temp/av-kit/convert-settings-drafts/cs81-gate-h1-run4.txt — py-tests exit=1: 1 failed, 3031 passed, 37 warnings in 911.43s; AC-122.8 passed"
      - "C:/Temp/av-kit/convert-settings-drafts/gate-run4/cs81-D6-py-tests.txt — test_tts_assets.py:260 got 'Downloading' from wait_idle, whose limit is 5 seconds (test_tts_assets.py:177)"
      - "C:/Temp/av-kit/convert-settings-drafts/gate4-procs-compare.txt — twelve other sessions' processes started during the fourth run's py-tests; none was this gate's, and none was stopped"
    research: { engine: none, sources: [] }
    reasoning: "D-1067 changed one TypeScript hook and one UI test; no Python file changed between the second run, which passed, and the third. The test waits 5 seconds for a worker thread, and the third run's suite took 48% longer under host load, so the likely cause is the bounded wait, not the code under test. The fourth run failed the same way in another test: a 5-second wait (wait_idle) under heavier load, the suite at 911 seconds; both failures are 5-second waits under host load, on code this session does not touch. Rerunning the gate as written changes no plan, contract or test. Rerunning py-tests alone lost: the gate's rule is a full rerun. Registering the flake here lost: it would widen this session's register delta beyond row 7. Changing the test's timeout lost: it is outside this session's files (M-7). Two-way: one rerun."
```

Expert pass (fresh context): 1 brief. Holds: none. Changed: D-970. Not adopted: none. Receipt: `C:/Temp/av-kit/convert-settings-drafts/csd-expert-pass.txt`.

### D-970: What number does a waiting Convert card show?

**I recommend A: the number in the card's corner is its row in the list as you see it (1, 2, 3, with no gaps), and a waiting card's text gives its place among the waiting jobs: `Waiting - next`, then `Waiting - 2 in line`, `Waiting - 3 in line`.** The queue-card design and the card code already call the corner number a 1-based position, so A also ends the 0 on today's first card. The waiting text is the number the Convert design asks for: it goes down when a job ahead finishes, is removed or is moved. Both are worked out in the app from the list it already has, so nothing stored changes, and reading the list order also avoids stored positions that can repeat after a remove and an add (an inference from the code, not run). Finished cards stay above the waiting ones until Clear finished, so most waiting cards carry two different numbers; the waiting text therefore never says "position" (changed by the expert pass). A can still fail if a corner 5 next to `Waiting - next` reads as a contradiction. Undoing it is one small change in the app, with no data to repair.

- B: both places show the waiting rank. One number per card, but a finished or running card would have no corner number. Today the Downloader and Transcript cards print the stored 0-based value, so under A the Convert corner is the only 1-based one until that residual is fixed; B does not change that.
- C: keep things as they are: the first card shows 0, a removed job leaves a gap, and a waiting card's number never goes down when jobs ahead finish.
- D: like A, but the running job counts as ahead. The next job to run would read "2 in line", which says it is not next.
- E: only the corner becomes the row plus one, and the waiting text keeps reading it. One line of code, but the waiting number would not drop after a job ahead finishes while finished cards stay above, so it fails the Convert design (08:646).

Refs: `docs/build-plan/08-video-conversion.md:646`, `docs/build-plan/10-queue-card-ui.md:87`, `QueueCard.tsx:74,283-284`, `ConvertPage.tsx:525,557`, `repositories.py:411-416`, `conversion.py:217,263-267`, `DownloaderPage.tsx:478`, `transcript-card.ts:134`, `C:/Temp/av-kit/convert-settings-drafts/csd-expert-pass.txt`, `CONVERT-POSITIONS-NOT-RENUMBERED`, MEU-152, AC-152.4 to AC-152.9, M-5 (a renumbering on the server is M-4 and was not offered).

### D-1060: Fix the second Add's overwrite in this session? (Mat's ruling)

Mat's row-5 words: 'job 1 and 2 where working on the same video, looks like 2 overwrote 1. But jobs finished'. The cause is the per-call `reserved` set (`services/conversion.py:215`, `:405-408`): a second Add of a file whose first job has not finished gets the same output name, and FFmpeg's `-y` overwrites the first output. It predates this session. He was offered: Register, continue (recommended: file the defect and close this session on its own ACs); Fix in Session 81; Record only (the do-nothing option). He chose **Fix in Session 81** (USER_EXPLICIT 2026-11-16 'Fix in Session 81'), which is amendment A1.

Refs: `docs/build-plan/08-video-conversion.md:292`, `services/conversion.py:215,405-408`, `media/adapter.py:439,741,770`, `C:/Temp/av-kit/convert-settings-drafts/cs81-human-check-r1.txt`, D-1061 to D-1065, M-8, M-10.

## Research References

- Local only. `format_timecode` and `TIME_MAX_MS` (`packages/core/src/avkit_core/services/video_input.py:31,168-173`) and `parseConvertTime` (`convert-time.ts:4-25`) fix the time code. `routes/settings.py:41` (`model_dump(exclude_unset=True)`) shows the server writes only the leaves it receives. No web source was needed.

## Planning receipts

All under `C:/Temp/av-kit/convert-settings-drafts/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `cs81-eol.txt` | Line endings, line counts, sizes and SHA-256 prefixes of every file in §Files Modified and §Project files at `HEAD` `6aaf9b0`; the three new test files absent |
| `pre-plan-decision-probe.txt` | `decision_sources` on the grouping and `known-issues.yaml` with the five issues: D-813 to D-817 (grouping), D-808 and D-809 (triage), D-373 and D-380 (planning, issue `CONVERT-CUT-ENCODER-LABEL`) |
| `plan-decision-probe.txt` | The same with this plan added: D-966 to D-972 at stage `planning`, and no stage conflict |
| `anchor-probe.txt` | Each row-0 anchor of §Verification Plan 1 counted in the tree: all present; the three new test files absent; every CRLF scoped file differs from its HEAD blob by bytes while `git status` lists none of them (`* text=auto`) |
| `cs81-amend-a1-probe.txt` | Amendment A1 (2026-11-16): the line numbers it cites; `services/conversion.py` CRLF at SHA-256 `21ff80a6…` after row 4; the row-0 copy holding the same per-call `reserved` set; `tests/unit/test_convert_output_reserved.py` absent; Windows path equality case-insensitive |
| `cs81-a2-e2e-try1.txt`, `cs81-a2-e2e-try2.txt`, `cs81-a2-e2e-r1.txt` to `-r3.txt`, `cs81-a2-eslint.txt`, `cs81-a2-tsc.txt` | Amendment A2 (2026-11-16): the first run, where AC-152.22's own expectation was wrong and was corrected before any pass; then try2, r1 and r3 with all five Electron tests passing, and r2 with AC-152.21 at its test timeout (unbounded waits, bounded afterwards; see §Execution amendment A2, First runs); ESLint and `tsc` clean on the bounded tests |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the 06 and 08 home sections and the five issues | `csd-plan-2026-11-15-convert-settings-drafts` |
| Row checks | Each row's validation command | `task.md` |
| Amendment review | §Execution amendment A1 and task rows 4a, 4b, 5 and 7 as amended, before any A1 product edit | Codex plan review, run by the coordinator: loop `csd-plan-a1-2026-11-16-convert-settings-drafts`; round 1 `C:/Temp/av-kit/csd-a1-plan-review-round-1.md` (canonical copy `.agent/context/handoffs/2026-11-16-convert-settings-drafts-amendment-a1-plan-critical-review.md`), `changes_required` (A1-R1-F1, A1-R1-F2, corrected by D-1064 and D-1065); A2 (D-975) has no review round of its own, and the H1-7 execution review covers it |
| Real-app checks | Round 1: Mat's look (`cs81-human-check-r1.txt`). Round 2, replaced under A2 (D-975): the Electron tests AC-151.14 and AC-152.21 to AC-152.24, three runs | Row 5; the gate's `ui-electron-a2` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from the row-0 copies (`C:/Temp/av-kit/convert-settings-drafts/baseline-copies/`) in the §Files Modified paths, the six new test files whole, against AC-151.1 to AC-151.14 and AC-152.1 to AC-152.24 | `cs81-execution-2026-11-15-convert-settings-drafts` |
