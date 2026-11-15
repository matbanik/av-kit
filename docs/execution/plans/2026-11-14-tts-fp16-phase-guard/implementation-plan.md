---
project: "2026-11-14-tts-fp16-phase-guard"
date: "2026-11-14"
source: "docs/build-plan/03-service-layer.md#tts-fp16-phase-guard-residual"
meus: ["MEU-127"]
status: "draft"
template_version: "2.3"
---

# Implementation Plan: TTS FP16 phase guard spike (Session 73)

> **Project:** `2026-11-14-tts-fp16-phase-guard`
> **Build plan:** `docs/build-plan/03-service-layer.md` §TTS FP16 phase guard (residual) (`:686-698`, anchor `tts-fp16-phase-guard-residual`). The registry row is `.agent/context/meu-registry.md:61`, and the build priority matrix row is 3.18.
>
> **Source request.** On 2026-11-07 Mat accepted the D-336 brief ("all recommendations accepted", `docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:5-53`). It keeps FP16 as shipped, keeps `TTS-ONNX-FP16-NONFINITE-AUDIO` open, and registers one follow-up MEU that tests a guarded phase computation, spike first. D-345 registered it as MEU-127 (Session 52 reflection `:136`). MEU-127 belongs to no grouping.
> **Status:** `draft`, with Amendment 1. Mat ruled at the plan gate on 2026-11-14 through the Human Decision Protocol: D-789 USER_EXPLICIT "Alone (Recommended)"; D-790 and D-791 USER_EXPLICIT "Download and read"; D-793 USER_EXPLICIT "PHASE_GUARD (Recommended)"; and the words to execute, USER_EXPLICIT "Execute (Recommended)". `plan_to_exec_gate: human`: Codex approved Amendment 1 at plan review round 3 (2026-11-14, 0 findings), so execution runs to row 9 and stops there for Mat.

## Goal

Find out whether a small change to a copy of the FP16 graph stops its non-finite audio without changing anything else, then put the measured result in front of Mat so he can decide what ships.

03's five rules are binding:
- **Spike first** (D-336): count the zero and near-zero denominators at `/decoder/decoder/generator/Div` on the failing pairs; patch a copy of the FP16 graph so it no longer divides by them; rerun the 149 `--phase sentences` jobs on the patched graph; Mat listens.
- **FP16 stays** (D-336): FP16 stays as shipped, offered and never preselected while INT8 or FP32 can run (D-330, D-331).
- **Upstream** (D-336): nothing is posted to the model's Hugging Face discussion.
- **Outcome** (D-336): what ships, a patched graph or nothing, comes back to Mat with the spike's counts.
- **Tests** (Local Canon): the packaged `--phase sentences` smoke on the patched FP16 graph, 149 jobs, each WAV with its full payload (AC-121.8).

**What the plan-time spike already found** (each number comes from a receipt under `C:/Temp/av-kit`, listed in §Planning receipts):
- **The cause.** The phase subgraph is STFT, then `Gather_4` (real part) and `Gather_5` (imaginary part), then `Div(imag, real)`, then `Atan`, then the `Where` quadrant fixes. `Atan` is `Div`'s only consumer. In FP16, frequency bin 10 (Nyquist) sometimes has a real part and an imaginary part that are both exactly 0. `0 / 0` is NaN, `Atan(NaN)` is NaN, and the NaN reaches the waveform. That happens 14 times, in exactly the 12 failing jobs, and in no passing job (`s73-plan-count.json`).
- **Not the cause.** A real part of 0 with a non-zero imaginary part gives ±Inf, and `Atan(±Inf)` is the finite ±π/2. That is the right `atan2` answer, and it happens in passing jobs too (1,287 Inf quotients in 137 passing jobs).
- **The guard.** PHASE_GUARD replaces a NaN quotient with `+0` before `Atan`, and leaves every other value as it was. `atan2(0, 0)` is `+0` in IEC 60559 Annex F, fdlibm and `torch.atan2`. On the 149 jobs the guarded graph fails none, changes exactly the 12 failing jobs, and leaves the other 137 bit-identical (`s73-plan-compare.json`).
- **The packaged path.** On a fresh onedir, the control smoke fails the same 12 jobs as Session 52's Red; the guarded smoke passes 149 of 149; INT8 passes 149 of 149. The 137 WAVs the control wrote are byte-identical to the guarded run's (`s73-plan-wavs.json`).

Execution repeats each of these steps on fresh copies with receipts, writes the outcome brief (D-797) with the counts, and gives Mat one listening folder. What ships, if anything, is Mat's ruling. If Mat rules to ship, how it ships is a plan amendment with its own Red and review. This plan changes no product code.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (2026-11-14). No payload is oversized: 03's section, the register entry, the status row, the smoke tool, Session 52's spike and test set, and the ONNX graph's phase subgraph were read by section or by node name."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`plan_to_exec_gate: human`, the Claude Code block of `.agent/context/harness.local.md`). Execution waits for Mat's explicit words at the plan gate. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit` with the `s73-*` names;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s73\tmp` for the Python suite;
  - `ELECTRON_RUN_AS_NODE` is cleared before every run, and the scripts clear it as well.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Decisions:** every decision for Mat goes to Mat through the Human Decision Protocol (AGENTS.md §Communication Policy), with a recommendation first and a do-nothing option. No decision goes to a subagent in this session.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s73-plan-2026-11-14-tts-fp16-phase-guard` and `s73-execution-2026-11-14-tts-fp16-phase-guard`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Round caps are the repository's: plan 3, execution 6. Token budgets are `off` (`.agent/review-limits.json`), so the loops stop on rounds only. Mat is not asked for a budget. The coordinator reports the token estimate and each round's spend.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, so the coordinator tells Mat before each dispatch.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path. The `--review-state-only` receipt is then rebuilt there.
- **Reviewer prompts:**
  - They name the ledger vocabulary up front: D-789 to D-798, AC-127.1 to AC-127.12, and the mechanism ids in §Single-statement contracts.
  - They forbid opening:
    - `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json` and any `.env`;
    - `.claude/settings.local.json`;
    - anything under `.agent/fleet/hub`;
    - `docs/proposals/2026-11-10-download-logic-divergence-report.md`.
  - They write `<HOME>` for the home folder.
  - When a prompt asks for `tested_state`, it names `~/.config/git/ignore` and the path that file hides, `.claude/settings.local.json` (Session 51 RULE-4).
  - `## Findings` holds only the Findings table (Session 65 RULE-3).
  - Every prompt carries the literal `### New Findings` header. It also carries the Prior Pass Summary table, with the columns Finding, Prior Status and Recheck Result (Session 66 RULE-4).
  - A recheck names each prior finding by the review's own id (Session 53 RULE-3). It asks for bare words in its Recheck cells, such as `fixed` and `open` (Session 52 RULE-1, Session 57 RULE-5).
- **Never in these rows without Mat's words:**
  - a commit, a push, a tag, a release or an upload;
  - a post to Hugging Face or anywhere else (D-336);
  - `npm run dist` or an installer build;
  - a model download other than row 0b's seven files (D-790 as ruled);
  - an `approved` verdict written by the implementer;
  - reading any user data other than row 0b's read-only SHA-256 of the same seven files under `~/.avkit/models` (Session 70 RULE-2, D-791 as ruled). No row reads the app database or Mat's settings file, and every row after 0b works from the copies under `C:/Temp/av-kit`.
- **No network:**
  - no row reaches YouTube. Only row 0b reaches the network, and only Hugging Face, for FRESH_INPUTS's seven files, with no token and its own `HF_HOME` (D-790 as ruled). The smoke runs the backend with dead proxies (`127.0.0.1:9`) and its own `HF_HOME`;
  - no row writes the system clipboard, and no clipboard Electron spec runs (`ui/tests/e2e/capture-filmstrip-actions.test.ts`, `ui/tests/e2e/capture-import.test.ts`);
  - nothing touches the installed avkit MCP servers, and no `mcp__avkit__*` tool is called;
  - no other program is stopped. Each smoke stops only the backend it started. If ShareX or another program holds a resource a row needs, the row stops and asks Mat (S13).

## Handoff Set

| MEU | Handoff | Chain |
|---|---|---|
| MEU-127 | `.agent/context/handoffs/2026-11-14-tts-fp16-phase-guard-MEU-127-handoff.md` | only |

Rolling reviews:
- `.agent/context/handoffs/2026-11-14-tts-fp16-phase-guard-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-14-tts-fp16-phase-guard-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| WP | Rows | Content | Context |
|---|---|---|---|
| WP-1 | 0, 0b | Baseline: rulings, queue, dirty paths, anchors, input hashes, offline install, base Python suite, selftests; then the fresh download and the installed-file hashes (D-790, D-791 as ruled) | shared |
| WP-2 | 1 | A fresh onedir and the five run and model copies | shared |
| WP-3 | 2, 3, 4 | The guarded copy, the denominator count and the graph compare | shared |
| WP-4 | 5, 6, 7, 8 | The control, guarded and INT8 smokes, and the WAV identity and listening folder | shared |
| WP-5 | 9 | The outcome brief (D-797) and Mat's listening and ruling | human gate |
| WP-6 | 10 | 03's Delivered note, the register entry and the status | shared |
| WP-7 | H1, H2 | Gate, handoff, review, reflection, records, next prompt | compact_continue |

## User Review Required

**Carried rulings:**
- **D-336** (human, USER_EXPLICIT 2026-11-07 "all recommendations accepted"; brief `docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:5-53`; Session 52 reflection `docs/execution/reflections/2026-11-06-tts-load-fp16-reflection.md:127`) set 03's four Human-approved rules.
- **D-345** (autonomous, Session 52 reflection `:136`) registered MEU-127.
- **D-239** (the register entry's own decision log, `.agent/context/known-issues.yaml:4019`): FP16's fate comes back to Mat, and nothing removes or disables it.
- **D-330 and D-331** (Session 52 plan): FP16 is offered and never preselected while INT8 or FP32 can run. This plan doesn't touch the preselect order.

**Questions at the plan gate.** Each has a brief in §Decision briefs, with the recommendation first and a do-nothing option:
- **D-789, the session shape.** Recommendation: one MEU, one session, no grouping. Do nothing: MEU-127 stays `pending`.
- **D-790, the inputs.** Recommendation: no download. Every row uses Session 52's cached copies under `C:/Temp/av-kit/s52`, checked by SHA-256 at row 0. Do nothing: the same.
- **D-791, user data.** Recommendation: no read of `~/.avkit/models`, the app database or the settings file. Do nothing: the same.
- **D-793, the guard and 03's wording.** Recommendation: PHASE_GUARD, the measured two-node guard after the `Div`, reading 03's "so it no longer divides by them" as "so their division no longer reaches the phase". Do nothing: run no patch, and MEU-127 stays `pending`.
- **The words to execute.** Recommendation: execute this plan as reviewed. Do nothing: nothing runs.

**Plan-gate rulings (2026-11-14),** each `USER_EXPLICIT` through the Human Decision Protocol:
- D-789: "Alone (Recommended)".
- D-790 and D-791: first "Download or read". That option joined two choices, so the coordinator asked which one, and Mat answered "Download and read". This is against the recommendation, so Amendment 1 below adds row 0b.
- D-793: "PHASE_GUARD (Recommended)".
- Execute: "Execute (Recommended)". Mat gave it in the same exchange as the D-790 and D-791 ruling, and the follow-up question said that either choice changes row 0 as a plan amendment. Row 0 runs only after Codex approves Amendment 1 (plan review round 2).

**Amendment 1** (D-790 and D-791 as ruled; D-798) changes the round-1 plan as follows:
- **New row 0b** runs `fresh-inputs.py run` (FRESH_INPUTS, INSTALLED_READ, AC-127.12).
  - Before the client loads, it drops inherited `HF_*` and `HUGGINGFACE_*` variables from its own process and keeps every client cache in its private `s73/hf-home`. It fetches each file with `force_download`, so an inherited cache can't stand in for the download (round 2, F1).
  - It downloads the spike's seven inputs from Hugging Face at the app's own pins into `C:/Temp/av-kit/s73/models-download`: `voices.py`'s `ONNX_REPO` at `ONNX_REVISION` `1939ad2a…`, and `config.json` from `hexgrad/Kokoro-82M` unpinned, the way `vocab.py` fetches it.
  - It hashes the same seven files under `<HOME>/.avkit/models`, read only and by exact path.
  - It compares both sets with Session 52's cached copies.
- **Row 1** copies the seven downloaded files over the same paths in `models-original` and `models-guarded`, so the spike patches and runs the downloaded bytes. Row 0b requires those bytes to equal the cached ones, so every plan-time hash and AC value still holds.
- **Allowances and stops.** S5, AC-127.11 and the harness lists now allow exactly row 0b's download and read. A new stop, S18, fires on a downloaded or installed file that differs. AC-127.12 is new.
- **The gate** lints `fresh-inputs.py` and runs its selftest; row 0 runs that selftest too.
- **Unchanged:**
  - the gate's `gate-patch` still copies Session 52's cache, which row 0b proves byte-equal to the download;
  - the Python environment still installs offline from the lock;
  - no row reads the app database or the settings file.

**Questions during execution:**
- **D-797, the outcome** (row 9). The brief goes into `closeout-decisions.md` with the counts and the listening folder. Do nothing: ship nothing, FP16 stays as shipped, and the issue stays open. If Mat rules to ship, how it ships is a plan amendment with its own Red and review, not a row of this plan.
- **Listening.** Mat listens to one folder, `C:/Temp/av-kit/s73/listen`, named in the brief: 12 pairs of WAVs, the guarded FP16 output and INT8's output of the same job, plus `listen.txt`. A plan-time folder from the same steps already exists at `C:/Temp/av-kit/s73/plan-listen`, if Mat wants to listen before the gate.
- Any change to an approved contract or AC is a Decision Brief (Session 59 RULE-3), and S12 says how.

**Token estimate.** No budget applies, so these are for reporting only:
- plan review: about 11.4M tokens for round 1 and about 5.7M for each recheck (Session 52: 11.37M, 7.35M, 1.89M; Session 72: 12.77M, 4.38M);
- execution review: about 15M for round 1 and about 7.5M for each recheck (Session 52 round 1: 14.99M; Session 72: 12.39M).

## Proposed Changes

### Single-statement contracts

| Id | Contract |
|---|---|
| PHASE_GUARD | The guarded graph adds `PhaseGuard_IsNaN = IsNaN(q)` and `PhaseGuard_Where = Where(PhaseGuard_IsNaN, PhaseGuard_zero, q)` after `q = Div_output_0`, with `PhaseGuard_zero` an FP16 scalar `+0` initializer, and points `Atan` at `PhaseGuard_Where`. A NaN quotient becomes `+0`; ±Inf, ±0 and every finite value pass through bit for bit. Nothing else in the graph changes |
| PATCH_COPY | `phase-guard.py patch` writes the guarded graph only to a copy that lies outside all three of the checkout, `C:/Temp/av-kit/s52/smoke-models` and `~/.avkit`; it builds the graph twice and requires the same bytes, runs `onnx.checker.check_model`, and requires the source file's SHA-256 to be unchanged |
| DENOM_COUNT | `phase-guard.py count` runs Session 52's 149 jobs on a tapped copy of the original FP16 graph and counts, per job, the zeros and subnormals of the real part, the zeros of the imaginary part, the both-zero slots and their bins, the ratio overflows, and the NaN and Inf values of `Div`, `Atan`, the phase and the waveform |
| GRAPH_COMPARE | `phase-guard.py compare` runs the 149 jobs on the original and the guarded graph in ONNX Runtime and records which jobs fail, which change, and that the rest are bit-identical |
| RUN_COPIES | Each smoke runs on its own copy of one fresh onedir and its own copy of the cached models, under `C:/Temp/av-kit/s73`, because `--phase sentences` deletes and recreates `app-data` and `out` beside the backend folder |
| SENTENCE_SMOKE | `tools/smoke_packaged_tts.py --phase sentences` with Session 52's test set (`fp16-test-set/test-set.json`, 149 jobs), unchanged |
| WAV_IDENTITY | `phase-guard.py wavs` reads the WAV path of each job from a copy of each run's database, requires every job the control passed to have byte-identical WAVs in the control and guarded runs, and requires every job the control failed to have a complete guarded WAV and a complete INT8 WAV |
| LISTEN_FOLDER | `phase-guard.py wavs` copies the guarded and INT8 WAVs of each control-failed job into one folder, numbered by job, with `listen.txt` listing each pair's job, voice, length and file names |
| FRESH_INPUTS | `fresh-inputs.py run` downloads exactly seven files into a new folder under `C:/Temp/av-kit/s73`: the FP16 and INT8 graphs, the four test-set voices and `config.json`. Each comes from the repository, file name and revision that the app's own constants name (`HF_FILE_MAP`, `ONNX_REVISION`, `ONNX_VOCAB_REPO`). The script refuses `HF_ENDPOINT`, `HF_HUB_OFFLINE`, `TRANSFORMERS_OFFLINE`, `HUGGINGFACE_CO_STAGING` and `HF_HUB_ENABLE_HF_TRANSFER`. Before the Hugging Face client loads, it drops every other inherited `HF_*` and `HUGGINGFACE_*` variable from its own process (names recorded, values never) and points `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE` and `HF_ASSETS_CACHE` into its private `s73/hf-home`. It then checks that the loaded client's caches all lie there. It sends no token, and it fetches each file with `force_download`, so neither an inherited cache nor a file already in the destination can stand in for a fresh body download (plan review round 2, F1). Each file must land at its planned path, each pinned file's commit must equal the pin, and each file's SHA-256 must equal Session 52's cached copy |
| INSTALLED_READ | `fresh-inputs.py run` opens only the seven files FRESH_INPUTS names, by exact path, under `<HOME>/.avkit/models` (the app's default `models_directory`; the settings file is not read), and only to hash them. It lists no folder and copies or writes nothing there. A missing file is recorded as `absent`. A file that is present must equal Session 52's cached copy. The receipt writes `<HOME>` for the home folder, and the script refuses to write a raw home path |
| OUTCOME_BRIEF | D-797's brief in `closeout-decisions.md` carries the counts, the smoke results, the WAV identity result, the listening folder, a recommendation first and a do-nothing option, and authorizes nothing until Mat's ruling is recorded under it |

### MEU-127 `svc-tts-fp16-phase-guard`

**Boundary inventory.** This plan adds no product boundary. Its inputs are local files, read by plan-local scripts:

| Boundary | Input | Refusal |
|---|---|---|
| `phase-guard.py patch` | an ONNX file and a destination | refuses a graph that is already guarded, that has other than exactly one node named `Div` in the decoder's phase subgraph, whose quotient is a graph output, or whose quotient has other than exactly one `Atan` consumer; refuses a destination that equals the source or lies in `C:/Temp/av-kit/s52/smoke-models`, the checkout or `~/.avkit` |
| `phase-guard.py wavs` | run folders, a control receipt, a destination | refuses a destination outside `C:/Temp/av-kit/s73`; reads each run's database only through a copy |
| `tools/smoke_packaged_tts.py` | a backend folder and a models folder | refuses a models folder in the checkout or `~/.avkit`, and a backend folder in the checkout |
| `fresh-inputs.py run` | a destination and a receipt path | refuses a destination that lies outside `C:/Temp/av-kit/s73`, is that folder itself, or already exists; refuses an existing private `HF_HOME`; refuses `HF_ENDPOINT`, `HF_HUB_OFFLINE`, `TRANSFORMERS_OFFLINE`, `HUGGINGFACE_CO_STAGING` and `HF_HUB_ENABLE_HF_TRANSFER`; refuses to start if the client is already loaded, or if a loaded client's caches lie outside the private `HF_HOME`; refuses a file that lands anywhere but its planned path; refuses a receipt that still holds a raw home path |

**Input matrix (Session 64 RULE-1, Session 72 RULE-1).** Each quotient case, worked through PHASE_GUARD's actual code at plan time. The selftest (`C:/Temp/av-kit/s73-plan-selftest.txt`, 24 of 24) builds a 10-slot fixture and runs it with ONNX Runtime's graph optimisations off and on:

| Slot | `imag / real` | Original quotient | Guarded quotient | AC |
|---|---|---|---|---|
| 0 | `0 / 0` | NaN | `+0` (bits `0x0000`) | AC-127.1 |
| 1 | `-0 / 0` | NaN | `+0` | AC-127.1 |
| 2 | `0 / -0` | NaN | `+0` | AC-127.1 |
| 3 | `1 / 0` | `+Inf` | `+Inf`, bit-identical | AC-127.1 |
| 4 | `-1 / 0` | `-Inf` | `-Inf`, bit-identical | AC-127.1 |
| 5 | ordinary | finite | bit-identical | AC-127.1 |
| 6 | subnormal denominator | finite or Inf | bit-identical | AC-127.1 |
| 7 | large over small | finite | bit-identical | AC-127.1 |
| 8 | overflow to Inf | `Inf` | bit-identical | AC-127.1 |
| 9 | `0 / x` | `±0` | bit-identical | AC-127.1 |

And each job class, through the real graph:

| Job class | Count | Original | Guarded | AC |
|---|---|---|---|---|
| Control-failed jobs | 12 | 14 both-zero slots, all at bin 10; 14 NaN quotients; non-finite waveform | finite; passes the smoke | AC-127.3, AC-127.4, AC-127.6 |
| Control-passed jobs | 137 | no both-zero slot; 1,287 Inf quotients mapped to ±π/2 | bit-identical tensors and byte-identical WAVs | AC-127.4, AC-127.8 |
| Same jobs on INT8 | 149 | passes | not patched | AC-127.7 |

**Acceptance criteria.** The plan-time values come from §Planning receipts. Execution repeats each step on fresh copies, and the receipts must show the same values.

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-127.1 | unit | PHASE_GUARD selftest: `phase-guard.py selftest` exits 0 with 24 of 24 checks. On the 10-slot fixture, under `ORT_DISABLE_ALL` and `ORT_ENABLE_ALL`, the original quotient is NaN at exactly slots 0, 1 and 2; the guarded quotient is `+0` bits at those slots and bit-identical at the other seven; the guarded output is finite. The guarded graph has `IsNaN`, then `Where`, then `Atan` reading the `Where`; opset 20 and IR 9 are unchanged. The five graph refusals and four destination refusals each raise `PatchError`. Receipt `s73-phase-guard-selftest.json` | Spec: 03 Spike first; Annex F `atan2(±0, ±0)` | the refusal cases; slot 3 and slot 4 keep ±Inf |
| AC-127.2 | integration | PATCH_COPY: row 2's `patch` exits 0, and `s73-patch.json` records `div_index` 1686, `nodes_before` 2490, `nodes_after` 2492, the two inserted node names and the initializer name, `deterministic` true, `src_unchanged` true with the source SHA-256 `ba4527a8…c334a` before and after, the checker passed, and the destination SHA-256 `9037c82b…fd33` with 163,235,204 bytes. The destination is in `C:/Temp/av-kit/s73/models-guarded` | Spec: 03 Spike first ("in a copy") | the selftest's destination refusals |
| AC-127.3 | integration | DENOM_COUNT: row 3's `count` exits 0 on the original FP16 copy. `s73-count.json` records 149 jobs; `failing_count` 12, the same 12 job keys as §Input matrix; `div_nan_jobs_equal_failing_jobs` true; `both_zero_bins` `[10]`; failing totals real_zero 108, imag_zero 475,659, both_zero 14, real_subnormal 1,171,881, ratio_overflow 8, div_nan 14, div_inf 102, atan_nan 14, phase_nan 14, waveform_nonfinite 1,981,200; passing totals real_zero 1,186, imag_zero 5,155,668, both_zero 0, real_subnormal 12,864,773, ratio_overflow 101, div_nan 0, div_inf 1,287, atan_nan 0, phase_nan 0, waveform_nonfinite 0; `model_unchanged` true | Spec: 03 Spike first ("counts the zero and near-zero denominators") | passing jobs have 0 NaN |
| AC-127.4 | integration | GRAPH_COMPARE: row 4's `compare` exits 0. `s73-compare.json` records 149 jobs, `guarded_failing` empty, `changed` equal to `original_failing` (the 12), `unchanged_jobs` 137, and both SHA-256 values as AC-127.2 states | Spec: 03 Spike first | the 137 unchanged jobs |
| AC-127.5 | packaged | Control Red parity: row 5's SENTENCE_SMOKE on `s73/run-control` with the original FP16 copy exits 1 with 149 jobs, 12 failures, each `generated audio must be finite`, no other failure and no error, and its failure set (kind, index, voice) equals the one in Session 52's `C:/Temp/av-kit/s52-smoke-red.json` | Human-approved: D-239 (AC-121.7) | Is the Red of AC-127.6 |
| AC-127.6 | packaged | The 03 Tests rule: row 6's SENTENCE_SMOKE on `s73/run-guarded` with the guarded copy passes 149 of 149 with `variant_id` `kokoro-onnx-fp16`, no failure, no error and no forbidden folder in the onedir. Each WAV passes the smoke's own payload check (the declared frames are all present). The session gate runs it again on its own fresh copies (`smoke-guarded`) | Local Canon: 03 Tests (AC-121.8) | Yes: AC-127.5 |
| AC-127.7 | packaged | INT8 reference: row 7's SENTENCE_SMOKE on `s73/run-int8` with `kokoro-onnx-int8` passes 149 of 149 with no failure and no error | Spec: 03 FP16 stays (INT8 is the preselected variant) | — |
| AC-127.8 | integration | WAV_IDENTITY and LISTEN_FOLDER: row 8's `wavs` exits 0. `s73-wavs.json` records `control_failed` 12, `control_passed_identical` 137, `control_passed_differing` empty and no problem. `C:/Temp/av-kit/s73/listen` holds 25 files: 12 pairs named `NN-kind-II-voice-fp16-guarded.wav` and `NN-kind-II-voice-int8.wav`, each complete at 24,000 Hz, and `listen.txt` | Spec: 03 Spike first ("Mat listens") | a differing passed job fails the row |
| AC-127.9 | human gate | OUTCOME_BRIEF: `closeout-decisions.md` holds `## D-797` with the counts of AC-127.3, the smoke results of AC-127.5 to AC-127.7, the identity result of AC-127.8, the listening folder, a recommendation first, a do-nothing option (ship nothing, FP16 as shipped, the issue open) and `**Mat's ruling:**` with a `USER_EXPLICIT` quote. Nothing is posted upstream | Human-approved: D-336 (Outcome, Upstream) | row 9 stays `[B]` until the ruling |
| AC-127.10 | integration | The records: 03 gets a `> **Delivered (Session 73).**` note after the section's table naming the mechanism ids, AC-127.1 to AC-127.11, D-797's ruling and this plan folder, in CRLF; `TTS-ONNX-FP16-NONFINITE-AUDIO` gets the found `root_cause`, a `verification` with this session's method and result, and a `resolution_path` and `status` that follow D-797 (D-792), through `issue-resolve.py` with `issue-resolve: 0 problem(s)`; `known-issues.md` is re-rendered with `issue_triage.py render`; MEU-127 is `ready_for_review` with this plan as `execution_plan`; `meu_status.py render --check` and `issue_triage.py render --check` pass | Local Canon | the register's sha guard; render checks |
| AC-127.11 | integration | Isolation: no model file and no copy of the graph is in the checkout (`git ls-files '*.onnx'` is empty, and no `*.onnx` is in the checkout outside `.venv/`, where `onnxruntime` ships three test models of its own); no path under `packages/`, `ui/`, `mcp-server/`, `tools/` or `tests/` and not `openapi.committed.json` differs from `baseline.sha` (H1-4); no row but 0b reaches the network or reads `~/.avkit`; row 0b reads only INSTALLED_READ's seven files there (AC-127.12); no row reads the app database or settings file; every smoke receipt records the dead proxies; nothing is posted | Human-approved: D-336 (Upstream); D-790 and D-791 as ruled | H1-4's isolation check; the scope-paths step |
| AC-127.12 | integration | FRESH_INPUTS and INSTALLED_READ. `fresh-inputs.py selftest` passes 32 of 32, offline, on its own fixtures. Five of those cases come from `client-check`, run in a child process: the real client, inherited `HF_HOME`, `HF_HUB_CACHE`, `HUGGINGFACE_HUB_CACHE`, `HF_XET_CACHE` and `HF_TOKEN`, an inherited cache that already holds the file, and a stale copy in the destination, with the network forbidden. The client must drop the inherited variables, keep every cache private, send no token and still transfer the body once. Two mutants fail it: one without `force_download` and one without the confinement (`C:/Temp/av-kit/s73-plan-fresh-mutants.txt`) (`C:/Temp/av-kit/s73-plan-fresh-selftest.txt`). Row 0b's `run` exits 0. `s73-fresh-inputs.json` records: 7 files; the FP16 download's SHA-256 `ba4527a8…c334a` and INT8's `fbae9257…1478`; every `download_equals_cached` true; commit `1939ad2a8e416c0acfeecc08a694d14ef25f2231` for each of the six pinned files; every `installed_equals_cached` true, or null where the file is absent; `force_download` true; `client_confined` lists the five cache constants; `problems` empty; `installed_root` `<HOME>/.avkit/models`; and no raw home path | Human-approved: D-790 and D-791, USER_EXPLICIT 2026-11-14 "Download and read" | the selftest's refusals, and its cases of a different download, installed file, commit and cached hash |

**Spec sufficiency.** Every 03 rule has an AC:
- Spike first: AC-127.1 to AC-127.4 and AC-127.8.
- FP16 stays: no row changes the preselect order or the model list, and §Files Modified holds no product file; AC-127.7 records the reference.
- Upstream: AC-127.9 and AC-127.11.
- Outcome: AC-127.9.
- Tests: AC-127.6.
- D-790 and D-791 as ruled: AC-127.12, with AC-127.11 holding every other row to no network and no user data.

### Files Modified

The endings come from the plan-time Python byte count. Row 0 records them again, with SHA-256, in `C:/Temp/av-kit/s73-anchors.txt`.

| File | Endings | Rows |
|---|---|---|
| `docs/build-plan/03-service-layer.md` (the Delivered note) | CRLF | 10 |
| `.agent/context/known-issues.yaml` (one issue's four keys) | LF | 10 |
| `.agent/context/known-issues.md` (rendered) | LF | 10 |
| `.agent/context/meu-status.yaml` (MEU-127) | LF | 10, H2-2 |
| `.agent/context/meu-registry.md` (rendered) | LF | 10, H2-2 |
| `docs/BUILD_PLAN.md` (rendered; P2's counts change only at `approved`) | LF | H2-2 |
| `docs/execution/plans/2026-11-14-tts-fp16-phase-guard/closeout-decisions.md` (new) | LF | 9 |

No file under `packages/`, `ui/`, `mcp-server/`, `tools/` or `tests/` changes, and neither does `openapi.committed.json`.

### Project files

These project files are written:
- this folder's plan, task, `closeout-decisions.md` and plan-local scripts;
- the handoff, the two rolling reviews and the reflection;
- `docs/execution/metrics.md` (CRLF) and `.agent/context/current-focus.md` (CRLF);
- `C:/Temp/av-kit/session-74-prompt.md`, written after the next-work probe at H2.

Nothing under `C:/Temp/av-kit/s73` is in the checkout, and no model file is ever committed.

## Out of Scope

| Item | Kind | Deferred to | Basis |
|---|---|---|---|
| Shipping the guarded graph (patching at download or load, or fetching a patched file) | amendment | a plan amendment, if Mat rules to ship at D-797 | 03 Outcome; D-336 brief `:18-20` |
| A post to Hugging Face or sherpa-onnx | outward-facing | never without Mat's words | 03 Upstream |
| Removing, hiding or relabelling FP16 | product | none | 03 FP16 stays; D-239 |
| An installer build or `npm run dist` | build | none | Session 73 prompt |
| Adding `onnx` to the backend's dependencies | dependency | the amendment, if any | the spike reads `onnx` from Session 52's `e5-site` only |
| A `Div` count on INT8 | measurement | none | the taps are typed FP16 in the FP16 graph; INT8 passes 149 of 149 on the packaged path (AC-127.7). The D-336 brief named it as free, but INT8's graph has its own node names and types, so it is not free here |
| Patch B (an epsilon added to every denominator) | alternative | none | measured to change passing jobs; D-793 |
| Refreshing `triage-output.yaml` | register | the next triage | D-792 |
| Downloading FP32, the other 50 voices or the spaCy model | measurement | none | D-798: the spike runs FP16 and INT8 on four voices |

## BUILD_PLAN.md Audit

`uv run python tools/meu_status.py render --check` passes at plan time. MEU-127 (`meu-status.yaml:3324`) is `pending`, band P2, and MEU-121 is `approved` (`C:/Temp/av-kit/s73-meu-stats.txt`). Row 10 sets MEU-127 to `ready_for_review`, and H2-2 sets it to `approved` after Codex approves, or leaves it where Mat's ruling holds it. P2's row (`docs/BUILD_PLAN.md:67`, 130 and 129) changes only at `approved`.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`:
1. **Rulings (S9).** Checks that this plan's single `> **Status:**` line carries the execute words with a `USER_EXPLICIT` quote, and stops if not.
2. **Queue (S8).** MEU-121 is `approved`, MEU-127 is `pending`, and `58d028e` is an ancestor of `HEAD`.
3. **Records.** Writes `baseline.sha` and `baseline-dirty.txt` with each dirty path's SHA-256. Writes `C:/Temp/av-kit/s73-anchors.txt` with the SHA-256 and endings of every file row 10 writes, and checks that 03's anchor and its `> **MEU-127.**` note exist. `docs/proposals/2026-11-10-download-logic-divergence-report.md` is hashed, never opened.
4. **Inputs (S10, D-790).** Checks by SHA-256 that `C:/Temp/av-kit/s52/smoke-models` holds the planned `model_fp16.onnx` (`ba4527a8…c334a`) and `model_quantized.onnx` (`fbae9257…1478`) and no other ONNX file, plus `config.json` and the four voices; that the phonemes file and `e5-site` exist; and that `e5-site` gives `onnx` 1.23.2 and `onnxruntime` 1.31.1. Nothing under `~/.avkit` is read.
5. **Install (S4).** `uv sync --frozen --offline --all-packages`.
6. **Base suite.** The whole Python suite, recorded in `s73-base-py.txt` and not fatal: the gate excuses only the ids it shows failing.
7. **Selftests.** `phase-guard.py selftest`, `fresh-inputs.py selftest` and `identity.py --selftest`, each on its own fixtures (Session 56 RULE-4).

### 2. Spike rows

| Row | What runs | Pass |
|---|---|---|
| 0b | `fresh-inputs.py run` into `models-download`, with the installed files' hashes (D-790, D-791 as ruled). `models-download` and `hf-home` must be absent first (S17) | AC-127.12 |
| 1 | `tools/package_backend.py`, then five copies under `C:/Temp/av-kit/s73`: `run-control`, `run-guarded` and `run-int8`, each holding `avkit-backend`; `models-original` and `models-guarded`, each a copy of Session 52's cached models with row 0b's seven downloaded files copied over the same paths (D-798). Every target folder must be absent first (S17) | the build exits 0; each copy's `avkit-backend.exe` exists; no forbidden folder (`torch`, `kokoro`, `phonemizer`, `espeakng_loader`) is in any onedir; both model copies' FP16 file has the source SHA-256 |
| 2 | `phase-guard.py patch` from `models-original` to `models-guarded` | AC-127.2 |
| 3 | `phase-guard.py count` on `models-original`'s FP16 file | AC-127.3 |
| 4 | `phase-guard.py compare` on `models-original` against `models-guarded` | AC-127.4 |
| 5 | SENTENCE_SMOKE, FP16, `run-control`, `models-original` | AC-127.5 |
| 6 | SENTENCE_SMOKE, FP16, `run-guarded`, `models-guarded` | AC-127.6 |
| 7 | SENTENCE_SMOKE, INT8, `run-int8`, `models-original` | AC-127.7 |
| 8 | `phase-guard.py wavs` on the three runs to `s73/listen` | AC-127.8 |
| 9 | D-797's brief; Mat listens and rules | AC-127.9 |
| 10 | 03's note, the register, the status and the renders | AC-127.10 |

The rows have no Red and Green, because the spike changes no product code. AC-127.5 is the Red of the 03 Tests rule, and AC-127.6 is its Green, on the same onedir build.

### Plan-local scripts

| Script | What it does | Plan-time result |
|---|---|---|
| `phase-guard.py` | PHASE_GUARD, PATCH_COPY, DENOM_COUNT, GRAPH_COMPARE, WAV_IDENTITY and LISTEN_FOLDER. It runs the graph with Session 52's `e5-site` (`onnx` 1.23.2, `onnxruntime` 1.31.1) and its phonemes and test set; it changes no product code | selftest 24 of 24 (`C:/Temp/av-kit/s73-plan-selftest.txt`); `patch`, `count`, `compare` and `wavs` ran on plan-time copies (§Planning receipts) |
| `fresh-inputs.py` | FRESH_INPUTS and INSTALLED_READ, row 0b only | selftest 32 of 32 (`C:/Temp/av-kit/s73-plan-fresh-selftest.txt`), with F1's real-client regression and its two failing mutants (`C:/Temp/av-kit/s73-plan-fresh-mutants.txt`); ruff and `ruff format --check` clean (`C:/Temp/av-kit/s73-plan-fresh-ruff.txt`). `run` doesn't run at plan time, because it reaches the network and reads user data |
| `identity.py` | binds the tested state; a copy of Session 52's with this plan's paths | selftest (`C:/Temp/av-kit/s73-plan-identity-selftest.txt`) |
| `issue-resolve.py` | row 10's register write; a copy of Session 52's, with `root_cause` added to its keys (D-792) | used at row 10 only |
| `baseline.ps1` | row 0 | parses; it runs nothing at plan time |
| `session-gate.ps1` | H1-2 | parses; it runs nothing at plan time |

### Session gate (H1-2)

`session-gate.ps1` runs each step with its own receipt (`s73-D6-<id>.txt`) and exit code:

| Step | Command |
|---|---|
| Identity before | `identity.py` |
| Static | pyright on `packages/`; `ruff check packages/ tests/`; `ruff check` on `phase-guard.py` and `fresh-inputs.py`; `ruff check --extend-ignore E501` on the two copied scripts (D-796); `lint_task_contract.py`; the scope-paths check (S3); the `phase-guard.py`, `fresh-inputs.py` and `identity.py` selftests |
| Fresh full | the whole Python suite (TMP and TEMP at `C:\Temp\av-kit\s73\tmp`; only the ids that row 0's receipt shows failing are excused); `meu_status.py render --check`; `issue_triage.py render --check` |
| Runtime | `gate-patch`: a fresh copy of Session 52's models under `C:/Temp/av-kit/s73/gate` and the guarded graph written into it; `patch-same`: the gate's graph has row 2's SHA-256; `package-build`; `smoke-guarded`: AC-127.6's smoke on a fresh copy of that onedir; `smoke-guarded-check`: 149 jobs, passed, no failure, no error, no forbidden folder; `smoke-leftover`: no `avkit-backend.exe` under the gate folder still runs (S16) |
| Identity after | `identity.py`, which must equal the before value |
| Skipped with reason | the UI and MCP suites and builds, the OpenAPI check and the Electron specs (no file under `ui/`, `mcp-server/` or `packages/` changes); `mcp-audit` (network and the installed servers); `build-record` (no release) |

The handoff copies its counts from the receipts (Session 63 RULE-2).

### Runtime prerequisites (Session 67 RULE-3)

- PowerShell 7 (`pwsh`), `uv`, `rtk`, and the locked Python environment, installed offline.
- `C:/Temp/av-kit/s52/smoke-models`, `C:/Temp/av-kit/s52/e5-site`, `C:/Temp/av-kit/s52-spike-phonemes.json` and `C:/Temp/av-kit/s52-smoke-red.json`, unchanged since Session 52.
- `docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/test-set.json` and Session 52's `fp16-spike.py`, which `phase-guard.py` imports.
- About 3 GB free under `C:/Temp/av-kit/s73` for three onedir copies and two model copies.
- No program holding the backend's port range or the run folders.
- For row 0b only: network access to Hugging Face, and `<HOME>/.avkit/models` readable. A file that isn't installed is recorded as `absent`, not as an error.

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | graphify output appears in the checkout | stop and re-plan the Context Tool Decision |
| S2 | A row's pass values differ from the plan-time values in an AC | stop. A difference goes to Mat as S12 says, with both receipts |
| S3 | `HEAD` moves; or a path outside this plan and `baseline-dirty.txt` changes; or a `baseline-dirty.txt` path this plan doesn't write changes its SHA-256 | stop and ask Mat. Never commit, stash or revert another session's work |
| S4 | `uv sync --frozen --offline` fails at baseline | stop and ask Mat |
| S5 | Any of these: a row other than 0b reaches the network or downloads a model; row 0b fetches anything but FRESH_INPUTS's seven files; a row other than 0b reads `~/.avkit`; row 0b opens anything there but INSTALLED_READ's seven files; any row reads the app database or the settings file, or writes the system clipboard | stop |
| S6 | A raw home path or secret reaches a log line, a receipt quoted in a handoff, or the brief | write `<HOME>` instead, or ask |
| S7 | `package_backend.py` fails, or a forbidden folder is in the onedir | stop and ask Mat |
| S8 | The queue isn't as row 0 expects | stop and ask Mat |
| S9 | The Status line lacks the execute words | stop at row 0 |
| S10 | A cached input has another SHA-256 or is missing; or Codex is unavailable or the ledger refuses a round | stop and ask Mat; for Codex, Mat reviews |
| S11 | A status file is dirty from another session | copy it to `C:/Temp/av-kit/s73/pre-status/`, byte-edit only MEU-127's fields, and prove them with `render --check` and a diff (Session 61 RULE-5) |
| S12 | A contract or AC in this plan needs to change | record a departure before the gate. One that changes an AC goes to Mat as a Decision Brief whose do-nothing option is "record it as a departure and keep the approved text" (Session 59 RULE-3) |
| S13 | A program other than this session's holds a resource that a row needs, such as a port, a file lock or a key like ShareX's F2 | stop and ask Mat. Never stop another program |
| S14 | The control smoke's failure set differs from Session 52's | stop and send Mat the two sets; the spike's premise has moved |
| S15 | The guarded smoke fails any job | stop. The failure, its message and the count go to Mat in D-797's brief, whose recommendation then cannot be to ship |
| S16 | A smoke leaves a backend process running after it exits. The smoke stops its own backend through its process handle and records no PID, so rows 5 to 7 and the gate list every `avkit-backend.exe` whose path is under that run's folder | stop only that process, by the PID the listing shows for that path (Session 56 RULE-2), and record it in the row's receipt. Never stop a backend by name |
| S17 | A run or model folder that row 0b or row 1 creates already exists | stop and ask Mat; never delete it |
| S18 | Row 0b finds a downloaded file that differs from Session 52's cached copy, a pinned file from another commit, or an installed file that differs | stop and send Mat the receipt. Either the spike's inputs or the user's installed file have moved, and Mat decides which files the spike runs on |

## Decision Log

> [!WARNING]
> D-792 and D-794 to D-796 are autonomous, and each lists its alternatives in `reasoning`. D-789, D-790, D-791 and D-793 were asked at the plan gate, and Mat ruled on 2026-11-14 (§User Review Required). D-797 is the outcome, asked at row 9. D-798 is autonomous: it records how Amendment 1 carries out the D-790 and D-791 ruling. D-789 to D-798 were free at plan time (`C:/Temp/av-kit/s73-plan-did-probe.txt`).
>
> Carried, and not relisted in the block:
> - D-336: human, `USER_EXPLICIT 2026-11-07 "all recommendations accepted"`, Session 52 reflection `:127`, brief `docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:5-53`;
> - D-345: autonomous, Session 52 reflection `:136`;
> - D-239: the register entry's own decision log; the plan-time probe with `--decision-issue TTS-ONNX-FP16-NONFINITE-AUDIO` returns it.
>
> The reflection carries these and every id the decision probe returns (Session 54 RULE-5). D-336 and D-345 live in Session 52's reflection, which the probe doesn't read, so they are carried by hand.

```yaml
decision_log:
  - id: D-789
    stage: planning
    question: "Does MEU-127 run alone, or join other work in a grouping?"
    resolution: human
    class: two-way
    chosen: "one MEU in one session, no grouping"
    source_tag: Human-approved
    precedents:
      - "docs/build-plan/03-service-layer.md:690 - MEU-127 registered alone from the D-336 ruling"
      - ".agent/context/meu-registry.md:61 - MEU-127 belongs to no grouping"
      - "C:/Temp/av-kit/s73-meu-next.txt - the queue names MEU-127 next"
    research:
      engine: none
      sources: []
    reasoning: "The spike changes no product code and its outcome is a ruling, so nothing else can share its rows. Joining a grouping lost: no grouping names it, and a new grouping would need its own synthesis. Do nothing keeps MEU-127 pending. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-14 plan gate, answer 'Alone (Recommended)'"
  - id: D-790
    stage: planning
    question: "Which model and build inputs does the spike use?"
    resolution: human
    class: two-way
    chosen: "download, against the recommendation: row 0b downloads the seven spike inputs from Hugging Face at the app's own pins and requires each to equal Session 52's cached copy, and rows 1 to 8 run on the downloaded bytes; the cached copies are still checked by SHA-256 at row 0, and the locked Python environment still installs offline"
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/s73-plan-build.txt - the onedir builds offline from the lock"
      - "docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md - Session 52 cached the same files and hashed them"
    research:
      engine: none
      sources: []
    reasoning: "Every input already exists with a known hash, so a download adds a network step and nothing else. Downloading fresh copies lost at plan time: it reaches the network and could fetch a different file. Mat ruled for the download; D-798 records how it runs, and S18 stops on a different file. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-14 plan gate, answers 'Download or read' and then 'Download and read'"
  - id: D-791
    stage: planning
    question: "Does any row read user data: ~/.avkit/models, the app database or the settings file?"
    resolution: human
    class: two-way
    chosen: "read, against the recommendation: row 0b takes a read-only SHA-256 of the same seven files under the installed models folder, by exact path, and each one present must equal Session 52's cached copy; no row reads the app database or the settings file, and each smoke keeps its own app-data folder"
    source_tag: Human-approved
    precedents:
      - "tools/smoke_packaged_tts.py - refuses a models folder in the checkout or ~/.avkit"
      - "Session 70 RULE-2 - ask before any user-data read"
    research:
      engine: none
      sources: []
    reasoning: "The cached models are the files the user would have, by hash, so reading the user's own copies proves nothing more. Reading the installed models lost at plan time: it is user data. Mat ruled for the read; D-798 limits it to the seven files and to hashing. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-14 plan gate, answers 'Download or read' and then 'Download and read'"
  - id: D-792
    stage: planning
    question: "What does row 10 write to TTS-ONNX-FP16-NONFINITE-AUDIO, and how is known-issues.md refreshed?"
    resolution: autonomous
    class: two-way
    chosen: "root_cause becomes the found cause (0/0 at bin 10 of the FP16 STFT reaching Div and Atan); verification records this session's method and result; resolution_path and status follow D-797 (open with the guarded graph named as a tested fix, unless Mat rules to ship, which leaves it open until the amendment lands); known-issues.md is refreshed with issue_triage.py render only"
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:4019 - the entry's root_cause says the cause is unknown"
      - "docs/execution/plans/2026-11-06-tts-load-fp16/issue-resolve.py - Session 52's guarded register write"
      - "C:/Temp/av-kit/s73-plan-count.json - the cause, measured"
    research:
      engine: none
      sources: []
    reasoning: "The register should say what the spike found, whatever ships. Closing the issue lost: the user's FP16 file is unchanged until a fix ships. Running issue_triage.py triage lost: it rewrites triage-output.yaml, which is outside this plan's scope, and its --help crashes at baseline. render writes only known-issues.md. Two-way."
    human_message_reference: null
  - id: D-793
    stage: planning
    question: "Which guard does the spike test, and does it meet 03's 'so it no longer divides by them'?"
    resolution: human
    class: two-way
    chosen: "PHASE_GUARD, IsNaN and Where after the Div, mapping only a NaN quotient to +0, reading 03's words as 'so their division no longer reaches the phase'"
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/s73-plan-compare.json - PHASE_GUARD fixes the 12 failing jobs and leaves 137 bit-identical"
      - "C:/Temp/av-kit/s73-plan-count.json - every NaN is a 0/0; 1,287 Inf quotients in passing jobs give the right atan2 answer"
      - "docs/build-plan/03-service-layer.md:694 - the Spike first rule"
    research:
      engine: web
      sources:
        - "https://netlib.org/fdlibm/w_atan2.c"
        - "https://kiwix.lema.org/stackoverflow.com_en_all_2023-11/questions/55037585/is-it-safe-to-assume-that-atan2-00-returns-0"
        - "https://au.mathworks.com/matlabcentral/answers/578281-atan2-0-0-is-not-undefined-nan"
        - "https://gist.github.com/nikola-j/b5bb6b141b8d9920318677e1bba70466"
        - "https://discuss.pytorch.org/t/how-to-avoid-nan-output-from-atan2-during-backward-pass/176890"
        - "https://huggingface.co/mlboydaisuke/Kokoro-82M-ExecuTorch"
    reasoning: "The measured guard changes only the 14 NaN slots, to the value atan2(0,0) has in Annex F, fdlibm and torch. An epsilon on every denominator lost: it changes the passing jobs. Replacing the denominator with 1 where both parts are 0 gives the same output at those slots and stops the 0/0 division itself, but it is not measured and needs four nodes. Replacing every zero denominator lost: it would turn the right ±pi/2 answers into wrong ones. Do nothing runs no patch and leaves MEU-127 pending. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-14 plan gate, answer 'PHASE_GUARD (Recommended)'"
  - id: D-794
    stage: planning
    question: "Which onedir and which control does execution use?"
    resolution: autonomous
    class: two-way
    chosen: "one fresh onedir built at row 1 from HEAD, copied once per run; a control FP16 smoke on the original graph on the same build, whose failure set must equal Session 52's"
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/s73-plan-control-smoke.json - the plan-time control matches s52-smoke-red.json"
      - "tools/smoke_packaged_tts.py - the sentences phase deletes app-data and out beside the backend folder"
    research:
      engine: none
      sources: []
    reasoning: "A control on the same build shows that the guard, not the build, changes the result. Reusing Session 52's onedir lost: the tree has moved since. One shared run folder lost: each sentences run deletes the folders the last one wrote, and row 8 needs all three. Two-way."
    human_message_reference: null
  - id: D-795
    stage: planning
    question: "What goes in the listening folder?"
    resolution: autonomous
    class: two-way
    chosen: "the 12 control-failed jobs, each as a pair: the guarded FP16 WAV and the INT8 WAV of the same job, numbered by job, with listen.txt; the 137 other jobs are byte-identical to the shipped FP16 output, so they are not in the folder"
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/s73-plan-wavs.txt - the plan-time folder and its lengths"
      - "docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:22 - the WER card's quality caveat for FP16"
    research:
      engine: none
      sources: []
    reasoning: "Only the 12 jobs sound different from today's FP16, and INT8 is what a fresh install uses, so the pair is the comparison Mat needs. All 149 jobs lost: 137 are byte-identical to today's output. The original FP16 WAVs can't be included: those jobs wrote no audio. Two-way."
    human_message_reference: null
  - id: D-796
    stage: planning
    question: "What does the session gate run?"
    resolution: autonomous
    class: two-way
    chosen: "the Python static checks and suite, the task lint, the scope-paths check, the three selftests, the two renders, and AC-127.6's smoke again on fresh copies with a fresh patch that must match row 2's bytes; ruff runs plain on phase-guard.py and fresh-inputs.py and with E501 ignored on the two copied scripts; the UI and MCP steps are skipped with a reason"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-06-tts-load-fp16/session-gate.ps1 - Session 52's gate shape"
      - "C:/Temp/av-kit/s73-plan-ruff.txt - the copied scripts keep Session 52's long lines"
    research:
      engine: none
      sources: []
    reasoning: "No file under ui/, mcp-server/ or packages/ changes, so their suites prove nothing new. Running the UI and MCP suites lost: time with no new signal. Reformatting the copies lost: they would no longer diff cleanly against their sources. Two-way."
    human_message_reference: null
  - id: D-798
    stage: planning
    question: "How does the plan carry out the D-790 and D-791 ruling, download and read?"
    resolution: autonomous
    class: two-way
    chosen: "Amendment 1: new row 0b runs fresh-inputs.py, which downloads exactly the seven spike inputs at the app's own pins into C:/Temp/av-kit/s73/models-download with no token, a private HF_HOME holding every client cache, inherited HF variables dropped before the client loads, and force_download on every file, hashes the same seven installed files read only by exact path, and stops on any difference (S18); row 1 copies the downloaded files over both model copies; plan review round 2 reviews the amendment before row 0 runs"
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/tts/voices.py:83-96 - ONNX_REPO, ONNX_REVISION and HF_FILE_MAP, the app's own pins"
      - "packages/infrastructure/src/avkit_infra/model_manager/vocab.py:29 - config.json is fetched with no revision"
      - "packages/core/src/avkit_core/services/settings.py:77 - the default models_directory"
      - ".agent/workflows/create-plan.md:491-498 - answers given at the gate are folded into the plan, and the review loop resumes"
      - "C:/Temp/av-kit/s73-plan-fresh-selftest.txt - the offline selftest, 32 of 32"
      - "C:/Temp/av-kit/s73-plan-fresh-mutants.txt - the two mutants that fail the real-client regression"
      - ".agent/context/handoffs/2026-11-14-tts-fp16-phase-guard-plan-critical-review.md - round 2 F1, an inherited cache standing in for the download"
    research:
      engine: none
      sources: []
    reasoning: "The app's own constants decide what is fetched, so the download is the file a user gets today. Requiring equality with Session 52's copies keeps every plan-time value and AC-127.5's Red parity, and a difference stops for Mat instead of silently moving the baseline. Running rows 1 to 8 on the cached copies alone lost: Mat asked for the download, so the spike runs the downloaded bytes. Downloading FP32 or all 54 voices lost: the spike runs FP16 and INT8 on four voices. Listing the installed folder lost: it would open more than the ruling needs. Trusting HF_HOME alone lost: round 2 showed that an inherited HF_HUB_CACHE overrides it and the client then copies the files from that cache, so the run drops inherited HF variables, pins every cache inside its private home and forces each body download. Reading the settings file for a custom models_directory lost: the ruling named the installed model, not the settings file, so the default path is read and a moved folder shows as absent. Two-way."
    human_message_reference: null
  - id: D-797
    stage: execution
    question: "What ships from the FP16 phase guard spike, the guarded graph or nothing?"
    resolution: human
    class: product-preference
    chosen: "ship the guarded graph: how it ships is a plan amendment with its own Red and review; FP16 stays never preselected while INT8 or FP32 can run; TTS-ONNX-FP16-NONFINITE-AUDIO stays open until the fix lands; nothing is posted upstream"
    source_tag: Human-approved
    precedents:
      - "docs/build-plan/03-service-layer.md:697 - the Outcome rule, what ships comes back to Mat with the counts"
      - "docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:53 - D-336, a guarded phase fix, spike first"
      - "C:/Temp/av-kit/s73-compare.json - the guard changes the 12 failing jobs and leaves 137 bit-identical"
      - "C:/Temp/av-kit/s73-smoke-guarded.json - the guarded FP16 passes 149 of 149 on the packaged build"
    research:
      engine: pomera tavily
      sources:
        - "https://www.adrianlyjak.com/p/onnx"
        - "https://onnxruntime.ai/docs/performance/model-optimizations/float16.html"
        - "https://docs.openclaw.ai/plugins/onnx"
    reasoning: "Recommended: ship the guarded graph through a plan amendment with its own Red and review, if the 12 listening pairs sound right, FP16 still never preselected and the issue open until the fix lands. Ship nothing lost on the measurements: a two-node guard fixes all 12 failing jobs and changes none of the 137 others. Do nothing holds row 9 and row 10. The brief is in closeout-decisions.md. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-15 row 9, answer 'Ship guarded (Recommended)' after the listening folder"
  - id: D-799
    stage: execution
    question: "Row 10's S11 diff shows docs/BUILD_PLAN.md's Total row changing from 141 + 1 blocked to 141 + 1 ready + 1 blocked. Does that break 'only MEU-127's entry and rows may change'?"
    resolution: autonomous
    class: two-way
    chosen: "no: the Total row is rendered from the status file, and its one change is MEU-127 moving from pending, which the row doesn't count, to ready_for_review; meu-status.yaml changed only in MEU-127's entry, meu-registry.md only in MEU-127's row, and meu_status.py render --check passes"
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/s73/pre-status - the three files before row 10"
      - "C:/Temp/av-kit/s73-r10-render.txt - render --check passes"
      - "tools/meu_status.py - render writes the Total row from the status counts"
    research:
      engine: none
      sources: []
    reasoning: "S11 guards against another MEU's entry changing; a total derived from MEU-127's own status is part of MEU-127's change. Hand-restoring the old total lost: render --check would then fail. Stopping for Mat lost: nothing outside MEU-127 changed. Two-way."
    human_message_reference: null
```

D-797 (the outcome, stage `execution`) and any other execution decision go into this block during execution, before H1-6 (Session 71 RULE-4).

## Decision briefs

### D-789 — Does MEU-127 run alone in this session?

**Recommendation:** One MEU, one session, no grouping. **Reversibility:** two-way. **Default if unanswered:** MEU-127 stays `pending` and nothing runs.

**Precedents:** 03 `:690` (registered alone from D-336); `meu-registry.md:61`. **Research:** none needed; the queue probe (`C:/Temp/av-kit/s73-meu-next.txt`) names MEU-127 next.

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|---|---|---|---|---|
| One MEU, one session | 03; the queue | — | — | ✅ |
| Join another grouping | none names it | could share a gate run | the spike shares no rows with any other MEU, and its outcome is a ruling | ❌ |
| Do nothing | — | no tokens spent | FP16 keeps failing 12 of 149 jobs with no measured fix; the issue has no path | ⚠️ |

**Mat's ruling (2026-11-14):** USER_EXPLICIT "Alone (Recommended)".

### D-790 — Which inputs does the spike use?

**Recommendation:** No download. Use Session 52's cached models and the offline lock, checked by SHA-256 at row 0. **Reversibility:** two-way. **Default if unanswered:** the same; no download.

**Precedents:** Session 52 hashed the same files; `C:/Temp/av-kit/s73-plan-build.txt` built offline. **Research:** none needed.

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|---|---|---|---|---|
| Cached copies, checked by hash | Session 52 | — | — | ✅ |
| Download fresh copies | Hugging Face | proves today's upstream file | reaches the network; a changed file would break parity with Session 52 | ❌ |
| Do nothing | — | — | the same as the recommendation | ✅ |

**Mat's ruling (2026-11-14):** USER_EXPLICIT "Download or read", and then, asked which, "Download and read". Both the download and the read are in, through Amendment 1 (row 0b, D-798).

### D-791 — Does any row read user data?

**Recommendation:** No. Every row uses the copies under `C:/Temp/av-kit`, and each smoke has its own app-data folder. **Reversibility:** two-way. **Default if unanswered:** no read.

**Precedents:** Session 70 RULE-2; `tools/smoke_packaged_tts.py` refuses `~/.avkit`. **Research:** none needed.

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|---|---|---|---|---|
| No read | Session 70 RULE-2 | — | — | ✅ |
| Read `~/.avkit/models` to confirm the user's file | — | confirms the installed file's hash | user data; the cached file already has the hash the app downloads | ❌ |
| Do nothing | — | — | the same as the recommendation | ✅ |

**Mat's ruling (2026-11-14):** USER_EXPLICIT "Download and read". Row 0b hashes only the seven named files under `~/.avkit/models`. The app database and the settings file are still not read.

### D-793 — Which guard, and does it meet 03's wording?

**Recommendation:** PHASE_GUARD: `IsNaN` and `Where` after the `Div`, mapping only a NaN quotient to `+0`. 03 says the patch makes the graph "no longer divide by them" (the zero and near-zero denominators). Read that as "their division no longer reaches the phase". The division still runs, but its NaN never reaches `Atan`. **Reversibility:** two-way; it is a copy. **Default if unanswered:** no patch runs, and MEU-127 stays `pending`.

**Precedents:** the plan-time spike (`s73-plan-count.json`, `s73-plan-compare.json`, `s73-plan-patched-smoke.json`). **Research:** `atan2(±0, ±0)` is `±0` or `±π` in IEC 60559 Annex F and fdlibm, and `+0` for `torch.atan2(0, 0)` (sources in D-793's YAML). Kokoro's ExecuTorch port reports NaN from its FP16 vocoder too.

What the count found: the 14 NaN quotients are all `0 / 0` at bin 10. A zero real part with a non-zero imaginary part gives ±Inf, and `Atan(±Inf)` is ±π/2, the right `atan2` value. That happens 1,287 times in the 137 passing jobs, so those divisions must stay as they are.

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|---|---|---|---|---|
| PHASE_GUARD: NaN quotient to `+0` | the plan-time spike | — | — | ✅ |
| Substitute the denominator with 1 where both parts are 0 | 03's literal wording | no `0 / 0` runs at all; the same output at those slots (`0 / 1 = 0`) | not measured; four nodes, not two; one more patch and compare before row 2 | ⚠️ |
| Add an epsilon to every denominator | the PyTorch forum's common fix | one node | changes all 137 passing jobs | ❌ |
| Do nothing | — | no spike tokens | 03's Spike first rule isn't met, and the issue has no tested fix | ⚠️ |

**Mat's ruling (2026-11-14):** USER_EXPLICIT "PHASE_GUARD (Recommended)".

## Research References

- IEC 60559 Annex F on `atan2(±0, ±0)`, via a Stack Overflow mirror: https://kiwix.lema.org/stackoverflow.com_en_all_2023-11/questions/55037585/is-it-safe-to-assume-that-atan2-00-returns-0
- fdlibm's `atan2` wrapper: https://netlib.org/fdlibm/w_atan2.c
- MathWorks on `atan2(0, 0)`: https://au.mathworks.com/matlabcentral/answers/578281-atan2-0-0-is-not-undefined-nan
- A NaN-safe `atan2` for PyTorch: https://gist.github.com/nikola-j/b5bb6b141b8d9920318677e1bba70466
- The PyTorch forum on `atan2` NaN: https://discuss.pytorch.org/t/how-to-avoid-nan-output-from-atan2-during-backward-pass/176890
- Kokoro's ExecuTorch port, whose FP16 vocoder gave NaN: https://huggingface.co/mlboydaisuke/Kokoro-82M-ExecuTorch
- D-336's sources (Hugging Face onnx-community discussion 22, sherpa-onnx issue 4086, the ONNX Runtime float16 `node_block_list`, and the `safwan-o` WER card) are in Session 52's brief.

## Planning receipts

| Receipt | What it holds |
|---|---|
| `C:/Temp/av-kit/s73-meu-stats.txt`, `C:/Temp/av-kit/s73-meu-next.txt` | MEU-121 `approved`; MEU-127 `pending`, P2, next in the queue |
| `C:/Temp/av-kit/s73-plan-did-probe.txt` | D-789 to D-798 are free |
| `C:/Temp/av-kit/s73-plan-build.txt` | `package_backend.py` built a onedir offline |
| `C:/Temp/av-kit/s73-plan-selftest.txt` | `phase-guard.py selftest`, 24 of 24 |
| `C:/Temp/av-kit/s73-plan-identity-selftest.txt` | `identity.py --selftest`, 0 failures |
| `C:/Temp/av-kit/s73-plan-ruff.txt` | ruff on the three scripts, with E501 ignored on the copies |
| `C:/Temp/av-kit/s73-plan-patch.json` | PATCH_COPY's values in AC-127.2, to a plan-time copy |
| `C:/Temp/av-kit/s73-plan-count.json` | DENOM_COUNT's values in AC-127.3 |
| `C:/Temp/av-kit/s73-plan-compare.json` | GRAPH_COMPARE's values in AC-127.4 |
| `C:/Temp/av-kit/s73-plan-control-smoke.json` | the control smoke: 12 failures, all non-finite, equal to `s52-smoke-red.json` |
| `C:/Temp/av-kit/s73-plan-patched-smoke.json` | the guarded smoke: 149 of 149 |
| `C:/Temp/av-kit/s73-plan-int8-smoke.json` | the INT8 smoke: 149 of 149 |
| `C:/Temp/av-kit/s73-plan-wavs.json`, `C:/Temp/av-kit/s73-plan-wavs.txt` | WAV identity: 137 identical, 12 pairs in `C:/Temp/av-kit/s73/plan-listen` |
| `C:/Temp/av-kit/s73-plan-decision-probe.txt` | the decision probe: the plan alone, and the plan with the register and `--decision-issue TTS-ONNX-FP16-NONFINITE-AUDIO` |
| `C:/Temp/av-kit/s73-plan-task-lint.txt` | `lint_task_contract.py` on `task.md`, with `RECEIPTS_DIR=C:/Temp/av-kit` |
| `C:/Temp/av-kit/s73-plan-fresh-selftest.txt` | `fresh-inputs.py selftest`, 32 of 32, offline (Amendment 1, with round 2 F1's real-client regression) |
| `C:/Temp/av-kit/s73-plan-fresh-mutants.txt` | F1's regression on two mutants: without `force_download`, 31 of 32 (`client_fresh_body` fails); without the confinement, 27 of 32 (all five client cases fail) |
| `C:/Temp/av-kit/s73-plan-fresh-ruff.txt` | ruff and `ruff format --check` on `fresh-inputs.py`, clean |
| `C:/Temp/av-kit/s73-plan-hfhub.txt` | `huggingface_hub` 2.3.0 in the locked environment; its local-folder metadata's first line is the commit |

## Validation stage contract

- **Static:** pyright, `ruff check packages/ tests/`, ruff on the plan-local scripts, `lint_task_contract.py`, the scope-paths check, and the `phase-guard.py`, `fresh-inputs.py` and `identity.py` selftests.
- **Targeted:** each spike row's own script and smoke receipts, checked against the AC values.
- **Fresh full:** the session gate runs the whole Python suite, the two renders, a fresh patch that must match row 2's bytes, a fresh onedir, and AC-127.6's smoke on fresh copies.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
