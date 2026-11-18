---
project: "2026-11-17-tts-fp16-guard-ship"
date: "2026-11-17"
source: "grouping .agent/context/grouping/2026-11-17-value-triage-session-grouping.md §3 Session 74; issue TTS-ONNX-FP16-NONFINITE-AUDIO (D-797, D-801); session prompt C:/Temp/av-kit/session-74-prompt.md"
meus: ["MEU-144"]
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md"
---

# Implementation Plan: guard FP16 Kokoro's phase division in memory at load

> **Project**: `2026-11-17-tts-fp16-guard-ship`
> **Build Plan Section(s)**: a new 03 section, §TTS FP16 guard ship (residual), and matrix row 3.21 for MEU-144 (`svc-tts-fp16-guard-ship`), both written by task row 1 under D-1135 A (Mat, 2026-11-17).
> **Status**: said to execute (USER_EXPLICIT 2026-11-17 "orchestrate the plan creation for all sessions and proceed with execution for each"). `plan_to_exec_gate: human`: that message is the execution approval once the plan review approves; the plan review was approved at round 1 (.agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-plan-critical-review.md). Mat ruled A on D-1135 and D-1136 on 2026-11-17 (recorded in the Decision Log below). Session 74 runs first in the queue (grouping §8 D-1133: 74, 91, 92, 93, 94).

---

## Goal

**Goal anchor:** when a user loads ONNX FP16 Kokoro, the app builds its ONNX Runtime session from Session 73's guarded graph, made in memory from the user's own downloaded file and checked against Session 73's source hash (`ba4527a8…`) and result hash (`9037c82b…`), so the packaged `--phase sentences` smoke passes 149 of 149 jobs where today it fails 12; a file with any other size or hash loads exactly as shipped; a splice that refuses or gives another hash loads the file as shipped and logs one warning with no path; no file in the models folder is written, renamed or added; INT8 and FP32 load exactly as before; FP16 stays never preselected (D-330, D-331); nothing is posted to Hugging Face and no new package is added. Scripts and tests prove each part, with no manual check.

**Why.**

- **`TTS-ONNX-FP16-NONFINITE-AUDIO`** (`known-issues.yaml:4374`; open, high, infrastructure, P2; meu_links MEU-62, MEU-72, MEU-121, MEU-127; enrichment D-239 and D-801). In FP16, `/decoder/decoder/generator/Div` (the exported `atan2` of the phase, `Div(imag, real)`) divides 0 by 0 on 14 slots of 12 of Session 52's 149 jobs. The NaN goes through `Atan` and the job fails with "generated audio must be finite". Session 73 (MEU-127) measured a two-node guard, `PHASE_GUARD`: `Where(IsNaN(q), 0, q)` before the `Atan`. On the packaged build the guarded file passed 149 of 149, and the 137 jobs that already passed gave byte-identical WAVs. Mat listened to the 12 guarded pairs and ruled D-797 (2026-11-15, USER_EXPLICIT "Ship guarded (Recommended)").
- **The resolution path** (verbatim end): "How it ships (patch at download or load time with source and result hashes, the generator kept in FP32, or a guarded file fetched elsewhere) is a plan amendment with its own Red and review. FP16 stays never preselected while INT8 or FP32 can run, and nothing is posted to Hugging Face. Done when the app's FP16 runs the guarded graph and passes the 149-job packaged --phase sentences smoke with no failure."
- **D-801** holds MEU-144 and matrix row 3.21 for this session. D-333 (Session 52): "A fix would change the adapter, so it needs its own Red and review."

**Grouping §3 Session 74** (grouping `:78-87`): it covers the one high-severity defect a user can hit; "at its plan gate Mat confirms the MEU registration and picks the delivery route by Decision Brief"; local (packaged build, sentence smoke); calibrate against Session 73 `tts-fp16-phase-guard` and Session 52 `tts-load-fp16`; no split. Mat 2026-11-16: "This should be done with framework and scripts!", so there is no human check row; listening is part of the D-1136 brief.

**What the code shows (plan-time reads at `HEAD` `ecfa3f3`, `s74-plan-head.txt`; the queue moves, so row 0 re-reads every cited line and the handoff corrects any that moved, Session 51 RULE-3):**

- **The load path.** `packages/infrastructure/src/avkit_infra/tts/adapter.py` (CRLF, 23,421 bytes, 552 lines) `load_model` (`:286-343`) runs the load checks, calls `self.unload_model()` (`:332`) and then `session, actual = self._load_onnx(variant, path, target)` (`:338`). `_load_onnx` (`:397-418`) builds `InferenceSession(str(path), providers=_onnx_providers("cuda"))` at `:402` when the target is CUDA; if that raises, or CUDA is not among the active providers, it falls back, and the CPU session is `InferenceSession(str(path), providers=_onnx_providers("cpu"))` at `:414`. The module logger is `log = structlog.get_logger(module="tts")` (`:46`). Nothing in the adapter keeps the path after the session is built, and no log carries a path (D-323).
- **The variant and its file.** `voices.py:82-130`: `HF_FILE_MAP` maps `kokoro-onnx-fp16` to `onnx/model_fp16.onnx` at the pinned revision `ONNX_REVISION` `1939ad2a…` (`:84`); the sideload scan lists files by `SIDELOAD_SUFFIXES` (`:126`), so a second `.onnx` beside the download would show up as a model.
- **ONNX Runtime takes bytes.** ORT 1.31.1's `InferenceSession` accepts the serialized model as `bytes` (`s74-plan-timing.json`). On the real file, the guard step (read, source SHA-256, splice, result SHA-256) took 0.727 s with `splice-probe.py`'s form (splice 0.27 s; `s74-plan-timing.json`), and 0.572 to 0.649 s in three rounds with the one-join form (splice 0.030 to 0.045 s; `s74-plan-onejoin-timing.json`). Building the session from bytes saves nothing: three rounds in ORT 1.31.1 gave 1.01, 1.14 and 1.09 s from the guarded bytes and 1.03, 1.08 and 1.09 s from the path (`s74-peer-session-timing.txt`; the plan's single sample, 1.319 s against 1.734 s, built the path session while the first was still loaded). So a guarded FP16 load takes about 0.7 s longer at most.
- **Memory, measured.** `tracemalloc` on the `C:/Temp` copy: `splice-probe.py`'s form peaks at 835.3 MB, 163.2 MB after the read and 326.6 MB after the splice, because the source, `out`, `bytes(out)`, `ld(7, graph)` and the final concatenation are live at once (`s74-peer-tracemalloc.txt`). The one-join form (`onejoin-probe.py`'s `splice_onejoin`: one `b"".join` over `memoryview` slices of the source and the few new fields) peaks at 313.9 MiB (329.2 MB), 158.3 MiB (166.0 MB) above the read, and its result is byte-equal to `splice-probe.py`'s and to Session 73's guarded file (`s74-plan-onejoin.json`). For comparison, ONNX FP32 peaks at 817 MB for a whole run (`known-issues.yaml:4384`).
- **The model manager has no integrity check.** `download()` returns an existing file after `is_file()` alone (`model_manager/manager.py:67-73`), and nothing in `packages/` checks a model file's hash or size. The sideload scan (`manager.py:102-118`) walks the folder in sorted order and keeps one path per variant id (`:112-115`); the id comes from the file name (`voices.py:159-172`).
- **The splice needs no `onnx`.** A hand-written protobuf wire reader (`splice-probe.py`, stdlib only) applies `PHASE_GUARD` to the source file (163,234,740 bytes, 2,490 nodes; the `Div` is node 1686, its `Atan` node 1690) and gives 163,235,204 bytes with SHA-256 `9037c82b84dca069464f707f31a4fcb6e5d57107b0534fd4a7ae0c044396fd33`, byte-equal to Session 73's guarded file, deterministic, the source unchanged; spliced again, it refuses with "already guarded" (`s74-plan-splice.json`).
- **A model small enough for a unit test.** A 375-byte FP16 graph, `Div(a, b)` then `Atan` then `Mul` by 1.0, written with the same encoder (`synthetic-probe.py`): SHA-256 `57ba7da4…` before, 839 bytes and `fbbd7205…` after. In ORT CPU, 0/0 gives NaN before the splice and +0 (sign bit clear) after; 1/2 gives 0.463623046875, bit-identical before and after (`s74-plan-synthetic.json`).
- **Session 73's runs are still on disk** (`s74-plan-inputs.json`): `C:/Temp/av-kit/s73/models-original` (153 files, 299,058,987 bytes, with `config.json`, `kokoro-v1.0-onnx/onnx/model_fp16.onnx` and `model_quantized.onnx`, the voices and `spacy`), `s73/models-guarded`, `s73/models-download`, `s73/run-control`, `run-guarded`, `run-int8` with their app data, `s52/smoke-models`, the smoke JSONs `s73-smoke-{control,guarded,int8}.json`, `s52-smoke-red.json` (sha `add87703…`) and the test set (`docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/test-set.json`, sha `53c94154…`). No file in `s73/models-original` is newer than the first Session 73 smoke, so the packaged app did not write into its models folder (`s74-plan-models-mtime.json`). No download is needed.
- **Session 73's WAVs, by job.** Output names carry collision suffixes, so a name is not a job. Keyed by `(text_hash, voice)` from copies of each run's `avkit.db*` (`SELECT text_hash, voice, status, output_path FROM tts_jobs`): 149 jobs; Done 137 in the control, 149 guarded, 149 INT8; the control's 137 WAVs are byte-equal to the guarded run's; every key has one row (`s74-plan-wavs.json`, `wav-probe.py`).
- **The smoke** (`tools/smoke_packaged_tts.py --phase sentences`): `run_dir = backend_dir.parent`; it writes app data to `run_dir/app-data` and WAVs to `run_dir/out`; it refuses a backend or models folder inside the checkout and the real models folder; it sets dead proxies (`HTTPS_PROXY` `http://127.0.0.1:9`). The onedir is built with `tools/package_backend.py`, which at `HEAD` takes only `--stub-ok` (the prompt's "`--phase online`" is stale; the build runs as Session 73 row 1 ran it), not `npm run dist` (D-332). `packaging/dist/` and `packaging/build/` are git-ignored (`.gitignore:33-34`).
- **The preselection** is `PRESELECT_ORDER = ['kokoro-onnx-int8', 'kokoro-onnx-fp32']` at `ui/src/renderer/src/features/tts/tts-controls.ts:157`. The 03 Session 52 Delivered note cites it at `:108`; the handoff corrects that citation (RULE-3) and this session does not edit the note.
- **The register.** MEU-144, AC-144 and D-1135 onward are free (`s74-plan-meu144-grep.txt`, `s74-plan-ac144.txt`, `s74-plan-dids.txt`: 0 hits each). The SSOT holds 158 MEUs (155 approved, 1 closed, 2 pending; `meu_status.py next` gives MEU-158 and MEU-159; `s74-plan-meu-stats.txt`, `s74-plan-meu-next.txt`). No TTS or packaging file has changed since Session 73's commit `6813232`.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-17). The change is one new module and three lines of adapter.py, read verbatim at plan time with the files they touch; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern. Task-cell commands run in pwsh.
  - Receipts go under `C:/Temp/av-kit/tts-fp16-guard-ship/`, named `ff-*`; planning receipts are `s74-plan-*`.
  - Every row sets `PYTHONIOENCODING=utf-8` and `RECEIPTS_DIR=C:/Temp/av-kit`, and clears `ELECTRON_RUN_AS_NODE`. Every pytest run and every build sets `TMP` and `TEMP` to `C:\Temp\av-kit\tts-fp16-guard-ship\tmp`.
  - Vitest (the canon tests only) runs from pwsh after `Set-Location 'P:\av-kit\ui'` and returns to `P:\av-kit`.
  - A receipt that holds build or backend output is written raw under `tmp/` and then rewritten by `home-redact.py`, which replaces the home folder's prefix with `<HOME>` and deletes the raw file (Session 73 RULE-1). H1-6 scans every cited receipt for the raw prefix.
  - A smoke's backend is never killed: after each smoke the row lists any `avkit-backend.exe` whose executable is under that run folder and stops if one still runs (S13). No row stops a process by image name; other worktrees run their own apps, and ShareX is never stopped.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** local (two onedir builds and three 149-job packaged smokes; grouping §3 "Cloud/local: local").
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), run by the coordinator, with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `ff-plan-2026-11-17-tts-fp16-guard-ship` and `ff-execution-2026-11-17-tts-fp16-guard-ship`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
  - Each dispatch writes its own run log; the console output goes to a separate console file, never into the run log, and the row reads both tails (Session 88 RULE-2).
- **Queue:** Session 74 runs first, so no earlier session touches its files. Sessions 91 to 94 plan in parallel (their plan folders are untracked at plan time) and touch shared files only after Session 74's commit: Session 93 owns `tests/integration/`, and Sessions 91 to 94 write the registers and the grouping. The baselines and scope checks are path-scoped and bound to content at row 0 (§Verification Plan 1).
- **Host load:** every smoke, every full pytest run and the gate start only at or below 50 % (`host-load`, Session 81 RULE-2, with this session's 50 % bar).
- **Never in these rows without Mat's words:** commit, push, a download of any kind, a read of user data (the real models folder, the app database, the settings file), a post to Hugging Face, a new package, or writing an `approved` verdict. Mat pushes himself.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-144 | `.agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-MEU-144-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and plan-local checkers (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`, `red-check.py`, `identity.py`, `issue-resolve.py`, `eol-check.py`, `smoke-check.py`, `home-redact.py`, `host-load.ps1` |
| WP-2 | Register MEU-144 (row 1; D-1135) | WP-1 | shared | `register-meu-144.py`; 03 §TTS FP16 guard ship (residual); matrix row 3.21; MEU-144 `pending` |
| WP-3 | The packaged Red on today's tree (rows 2 and 3) | WP-2 | shared | `run-control`, `models-copy`, `ff-smoke-control.json`, `ff-wavs-control.json` |
| WP-4 | The guard: unit and integration Red, Green, the real-file check (rows 4 to 6; D-1136) | WP-3 | shared | `phase_guard.py`, `adapter.py`, `tests/tts_onnx_synthetic.py`, the two test files, `guard-check.py` |
| WP-5 | The packaged Green and INT8 (rows 7 and 8) | WP-4 | shared | `run-guarded`, `run-int8`, `ff-smoke-guarded.json`, `ff-smoke-int8.json`, the WAV and snapshot receipts |
| WP-6 | Records (row 9) | WP-5 | shared | The 03 Delivered note, the issue resolved, MEU-144 `ready_for_review`, grouping row 74 |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!IMPORTANT]
> **Your two rulings (2026-11-17):**
>
> - **D-1135, the registration: A.** MEU-144 is registered with its own 03 section and matrix row 3.21, as D-801 held them.
> - **D-1136, how the guarded graph ships: A.** It is built in memory each time FP16 loads, from your downloaded file, checked against Session 73's two hashes. That one choice also settles five more things the session prompt reserved for you: no new package, no download, no read of your data, no new listening (the graph is byte-equal to the one you heard), and the issue closes when the 149-job smoke passes, with FP16's preselection left as it is.
>
> The plan is written under those two rulings; every row that rests on one is marked in `task.md`. If you change either, the marked rows are re-planned and the plan goes back to review before anything runs (S17).
>
> **What changes for you:**
>
> - Picking ONNX FP16 in the TTS page no longer fails 12 of the 149 test sentences with "generated audio must be finite". Loading it takes about 0.7 s longer at most, and while it loads it holds up to about 330 MB more memory (329.2 MB measured, `s74-plan-onejoin.json`).
> - Your downloaded FP16 file stays exactly as it is on disk, and no file is added to your models folder.
> - If the FP16 file is ever a different one (a newer upstream file, a sideloaded file), the app loads it as before, with no change.
> - INT8 and FP32, and which model is picked for you first, don't change.

## Proposed Changes

### Single-statement contracts

- **`GUARD_IN_MEMORY` (D-1136 A):** a new module `packages/infrastructure/src/avkit_infra/tts/phase_guard.py` (CRLF, stdlib plus `structlog`) exports `SpliceError`, `splice(src: bytes) -> bytes`, a frozen dataclass `GuardSpec(source_sha256: str, source_bytes: int, guarded_sha256: str)`, `KOKORO_FP16 = GuardSpec("ba4527a874b42b21e35f468c10d326fdff3c7fc8cac1f85e9eb6c0dfc35c334a", 163234740, "9037c82b84dca069464f707f31a4fcb6e5d57107b0534fd4a7ae0c044396fd33")` and `guarded_model(path: Path, variant_id: str, spec: GuardSpec | None = None) -> str | bytes`. `splice` is `splice-probe.py`'s `splice` in `onejoin-probe.py`'s one-join form (`ONE_JOIN`), returning only the bytes, with its constants (`G = "/decoder/decoder/generator/"`, `DIV`, `PhaseGuard_IsNaN`, `PhaseGuard_Where`, `PhaseGuard_zero`, `PhaseGuard_IsNaN_output_0`, `PhaseGuard_Where_output_0`, `FLOAT16 = 10`, the zero initializer `ld(5, varint((2 << 3) | 0) + varint(FLOAT16) + ld(8, GUARD_ZERO.encode()) + ld(9, b"\x00\x00"))`) and its refusals, each a `SpliceError` with the exact text: "truncated varint", "varint too long", "unsupported wire type {wt}", "field runs past its message", "expected one graph, found {n}", "already guarded", "expected one /decoder/decoder/generator/Div, found {n}", "Div is not one Div with one output", "quotient is a graph output", "quotient must feed exactly one Atan", "no initializer"; a `UnicodeDecodeError` from a name is raised as a `SpliceError` from it.
- **`GUARD_GATE` (D-1137):** with `spec=None`, `guarded_model` reads the module's `KOKORO_FP16` at call time and applies it only when `variant_id == "kokoro-onnx-fp16"`; any other id returns `str(path)` with no stat. With a spec, in order: `path.stat()` (an `OSError`, or a size other than `spec.source_bytes`, returns `str(path)` with no read and no log); `path.read_bytes()` (an `OSError` or `MemoryError` returns `str(path)`); the source SHA-256 (any other value returns `str(path)`, no log: `GUARD_PASS_THROUGH`).
- **`GUARD_REFUSE` (D-1137):** when the source hash matches, `splice` runs; any exception from it, or a result whose SHA-256 is not `spec.guarded_sha256`, returns `str(path)` and logs one `log.warning("tts.phase_guard", variant_id=variant_id, outcome="refused", reason=...)`, where `reason` is the exception's class name or `"result_hash"`. The splice runs only on the exact hashed input and its output must match one hash, so a bug in the reader can never reach a user; the worst case is the file loaded as shipped.
- **`GUARD_APPLIED`:** a result with the right hash is returned as `bytes`, with one `log.info("tts.phase_guard", variant_id=variant_id, outcome="applied")`. The module's logger is `structlog.get_logger(module="tts")`. No event carries a path, a file name or an exception message (D-323). `guarded_model` never raises.
- **`ONE_JOIN`:** `splice` builds its result with one `b"".join` over `memoryview` slices of the source and the new fields (the Atan node rewritten, the two guard nodes, the zero initializer, and the graph's new tag and length, computed from the part lengths); it makes no other copy of the graph or the file. The `tracemalloc` peak of one `guarded_model` call on the real file, its own read included, is at most 400,000,000 bytes: 329.2 MB measured at plan time (`s74-plan-onejoin.json`), where `splice-probe.py`'s form peaks at 835.3 MB (`s74-peer-tracemalloc.txt`).
- **`GUARD_BYTES_EQUAL`:** on the user's unmodified download (Session 73's source hash), the bytes ORT loads are Session 73's guarded file byte for byte (`9037c82b…`), the graph Mat heard (D-797).
- **`BOTH_SESSIONS`:** `_load_onnx` calls `model = guarded_model(path, variant.id)` once, before `if target == "cuda":`, and passes `model` in place of `str(path)` to both `InferenceSession` calls (`:402`, `:414`), so a CUDA failure falls back to CPU on the same object without a second splice. `adapter.py` imports `guarded_model` at module level (`from avkit_infra.tts.phase_guard import guarded_model`), so PyInstaller's import analysis bundles the module and tests can wrap `avkit_infra.tts.adapter.guarded_model`. No other line of `adapter.py` changes; the PyTorch path and `packaging/avkit-backend.spec` are unchanged.
- **`NO_FILE_WRITE`:** nothing in the guard opens a file for writing, renames or creates one; the models folder's files keep their bytes and modification times, and no file is added.
- **`PRESELECT_KEPT`:** `tts-controls.ts` (`PRESELECT_ORDER`, `:157`), `voices.py` and the catalog are unchanged; FP16 stays offered and never preselected while INT8 or FP32 can run (D-330, D-331).
- **`WAV_BY_JOB`:** packaged WAVs are compared per job, keyed by `(text_hash, voice)` from copies of each run's `app-data/avkit.db*`, never by file name; each key has exactly one row.
- **`BUILD_SAME`:** the onedir built from today's tree before the change reproduces Session 73's control: the same 12 failures by `(kind, index, voice)` and the same 137 WAVs by job.

### The guard (rows 4 to 6)

`phase_guard.py` is about 170 lines: the wire reader ported from `splice-probe.py` and the splice in its one-join form from `onejoin-probe.py` (both kept in scratch), `GuardSpec`, `KOKORO_FP16` and `guarded_model`. `adapter.py` gains one import line and changes three lines in `_load_onnx` (one inserted, two replaced), CRLF kept. The tests use a synthetic model (`tests/tts_onnx_synthetic.py`, CRLF), whose `build()` is `synthetic-probe.py`'s builder, with keyword arguments for the refusal shapes: `div_names` (default one `G + "Div"`), `div_op` (`"Div"`), `atan` (`True`; `False` feeds the quotient to the `Mul`), `quotient_output` (`False`), `initializer` (`True`), `graphs` (1), `name_bytes` (raw bytes for the `Div`'s name, for invalid UTF-8). It also exports `SOURCE_SHA256`, `GUARDED_SHA256`, `SOURCE_BYTES` and `SPEC`, the synthetic `GuardSpec`. The tests' Red asserts `importlib.util.find_spec("avkit_infra.tts.phase_guard") is not None` first and imports inside the test body, so no Red fails by a missing module (Session 52 RULE-4).

### The packaged proofs (rows 2, 3, 7 and 8)

- **Row 2** checks that none of `run-control`, `run-guarded`, `run-int8` and `models-copy` exists under the scratch folder (S9; never delete one), builds the onedir from today's tree, copies `packaging/dist/avkit-backend` to `run-control/avkit-backend`, copies `C:/Temp/av-kit/s73/models-original` to `models-copy`, checks the copy (the exe and `_internal` exist, no `torch`, `kokoro`, `phonemizer` or `espeakng_loader` under `_internal`, the FP16 file's SHA-256 is `ba4527a8…`) and writes `ff-models-snapshot-0.json` (each file's relative path, size, SHA-256 and `st_mtime_ns`).
- **Row 3** runs the FP16 smoke on `run-control` and `models-copy`. It must exit 1 and match Session 73's control (`smoke-check.py control`), then `BUILD_SAME`'s WAVs (`smoke-check.py wavs --against run-control --expect-done 137`).
- **Row 7** rebuilds after Green into `run-guarded` and `run-int8`, runs the FP16 smoke on `run-guarded` and `models-copy` (must exit 0, 149 of 149; `WAV_BY_JOB` against Session 73's `run-guarded`, 149 equal), and compares `models-copy` with `ff-models-snapshot-0.json` (`NO_FILE_WRITE`).
- **Row 8** runs the INT8 smoke on `run-int8` and `models-copy` (149 of 149; 149 WAVs equal to Session 73's `run-int8` by job), then the snapshot again.

### Registration and records (rows 1 and 9)

- **Row 1 (D-1135 A, D-1139):** `register-meu-144.py`, shaped like `2026-11-17-queue-pause-feedback/register-meu-155.py` (it uses `tools.meu_status.model`, takes `--expect-sha256` for `meu-status.yaml` and reads the 03 and matrix hashes from `baseline-scope.json`, has `--dry-run` and `--selftest`, and refuses on drift; its `--delivered NOTE_FILE` mode, used in row 9, appends the CRLF Delivered note and refuses if one is already there), writes:
  - **03** (CRLF): `<a id="tts-fp16-guard-ship-residual"></a>`, a blank line, `## TTS FP16 guard ship (residual)`, a blank line, a `> **MEU-144.**` paragraph (registered 2026-11-17 from D-797 and D-801 in Session 74; depends on MEU-127), and a rule table, inserted before `:704` (`<a id="download-failure-reason-residual"></a>`). Rules: Ships guarded (D-797: the guarded graph ships, through this session's own Red and review, D-333); Delivery (`GUARD_IN_MEMORY`, `GUARD_GATE`, `GUARD_REFUSE`, D-1136); FP16 stays (offered, never preselected while INT8 or FP32 can run, D-330, D-331); Upstream (nothing posted to Hugging Face, D-336); Tests (the packaged `--phase sentences` smoke, 149 jobs, on what the app loads, Local Canon).
  - **The matrix** (CRLF): `| 3.21 | MEU-144 | \`svc-tts-fp16-guard-ship\` | [03 §TTS FP16 guard ship (residual)](03-service-layer.md#tts-fp16-guard-ship-residual) | MEU-127 |` between `:53` and `:54`.
  - **`meu-status.yaml`** (LF): MEU-144 (`slug: svc-tts-fp16-guard-ship`, `phase: '3'`, `band: P2` (the register's key, as MEU-127 has at `:3332`), `matrix_item: '3.21'`, `depends_on: [MEU-127]`, `status: pending`, `source` naming D-797, D-801 and this plan) after the last phase-3 entry, between `:3753` and `:3780`. Two texts already name MEU-144 as held and are reworded, not extended: the phase-3 note's last sentence (`:42-43`, "matrix row 3.21 is held for Session 74's MEU-144.") becomes "MEU-144 residual (TTS FP16 guard ship) registered 2026-11-17 in Session 74 on matrix row 3.21.", and the P2 range's "with MEU-144 held for Session 74" (`:4171`) becomes "with MEU-144 registered in Session 74"; the range bounds stay. Then `meu_status.py render` regenerates `meu-registry.md` and `BUILD_PLAN.md`.
- **Row 9 (D-1139):** a `> **Delivered (Session 74).**` note appended to the new 03 section (with the counts copied from rows 3, 6, 7 and 8 and the receipts named); `issue-resolve.py` sets `TTS-ONNX-FP16-NONFINITE-AUDIO` to `resolved` with `verification` and `meu_links` plus MEU-144, the `resolution_path` kept verbatim; `issue_triage.py render` and `render --check`; `meu_status.py update MEU-144 ready_for_review`, `render`, `render --check`; grouping §6 row 74 (`:162`, LF) becomes `| 74 | \`tts-fp16-guard-ship\` | MEU-144 | P2 | executed (Session 74) | \`docs/execution/plans/2026-11-17-tts-fp16-guard-ship/\` |`.

### Test pins

Each pin is cited by file, line and description (Session 83 RULE-1: no other family's AC ids are copied here as this plan's).

| Pin | What it checks | After this change |
|---|---|---|
| `tests/integration/test_tts_device_resolution.py`: the `Engines.session_class` fake (`:126`), `_adapter` (`:132`), `_variant` (`:140`, `kokoro-onnx-fp32` over a 7-byte `b"weights"` file), `capture_logs` and `_events` (`:159`) | CUDA and CPU session construction, the fallback logs and their fields | Unchanged file. Its variant is FP32, so `GUARD_GATE` returns `str(path)` with no stat; the fake still receives the path string |
| `tests/integration/test_tts_models.py:278` (`FakeSession`) | The load and unload sequence with a fake session | Unchanged file; its variants never have the FP16 size, so the guard passes through |
| `tests/integration/test_tts_no_torch.py:72` (`FakeSession.__init__(self, path, ...)` stores the path; `kokoro-onnx-int8`) | An ONNX load needs no torch | Unchanged; INT8 passes through with no stat |
| `tests/e2e/test_api_model_load_keeps.py:35-43` (the Session "records the file name it was built on" through `Path(str(path)).name`; a 16-byte INT8 file) | A failed load keeps the loaded model | Unchanged; INT8 passes through, so the recorded name is unchanged |

These four files are AC-144.10's guard: they pass unchanged at Red and Green, byte-identical to row 0. Any other existing test that fails after Green is S5, an M-7 question, not a fix.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| The ONNX model handed to `InferenceSession` | `phase_guard.guarded_model` | `str(path)`, or `bytes` whose SHA-256 is the spec's `guarded_sha256` | Nothing else; never a file written to disk |
| The `tts.phase_guard` log event | `phase_guard.py` | `variant_id`, `outcome` (`applied`, `refused`), `reason` on `refused` only (an exception class name or `result_hash`), and the logger's bound `module` | No path, no file name, no exception text (D-323) |
| `GuardSpec` | `phase_guard.py` | Three fields; `KOKORO_FP16` holds Session 73's pins | Internal; no setting, no API field |

No API route, OpenAPI document, MCP tool shape, persisted setting, catalog entry or database schema changes (M-4 kept clear).

### Acceptance Criteria

- **Titles.** Every new test is `test_ac_144_<n>_<word>…`; `red-check.py --require test_ac_144_1` matches up to a non-digit, so it never matches `test_ac_144_10`.
- **New names fail by assertion at Red.** Each new test asserts `importlib.util.find_spec("avkit_infra.tts.phase_guard") is not None` first and imports inside its body (`DECLARED_NEW`: `phase_guard`, `guarded_model`, `splice`, `GuardSpec`, `KOKORO_FP16`, `SpliceError`).
- **Required at Red:** AC-144.1 to AC-144.9 and AC-144.11. **Guard, passes at Red:** AC-144.10.
- **Checks, not test titles:** AC-144.12 to AC-144.17; rows 3 and 6 to 9 run them.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-144.1 | unit | `splice(build())` on the synthetic model returns 839 bytes with SHA-256 `fbbd7205e07079c6aa2670e6a0a8333844b1c9b44486549ace3e9b33f66526b7`; a second call returns equal bytes; the input still hashes to `57ba7da424695a40e2a43ad0f7b271685a6cd729439d930c0e9ff52c4f41348b`. | Local Canon (`PHASE_GUARD`, Session 73; `s74-plan-synthetic.json`) | In Red the module does not exist |
| AC-144.2 | unit | ORT CPU sessions from the source and the spliced bytes: `a=0, b=0` gives NaN from the source and `+0` with the sign bit clear from the guarded graph; `a=1, b=2` gives the same FP16 bytes from both (`0.463623046875`). | Local Canon (D-797; GRAPH_COMPARE, Session 73) | A guard that changes a finite phase fails it |
| AC-144.3 | unit | Each refusal raises `SpliceError` with its exact text: the spliced bytes ("already guarded"); two `Div` names and none ("expected one /decoder/decoder/generator/Div, found 2" and "found 0"); `div_op="Mul"` ("Div is not one Div with one output"); `quotient_output=True` ("quotient is a graph output"); `atan=False` ("quotient must feed exactly one Atan"); `initializer=False` ("no initializer"); `graphs=2` and `graphs=0` ("expected one graph, found 2", "found 0"); `build()[:-1]` ("field runs past its message"); `b"\x80"` ("truncated varint"); `b"\xff" * 11` ("varint too long"); `b"\x0b"` ("unsupported wire type 3"); `name_bytes=b"\xff"` (a `SpliceError` whose `__cause__` is a `UnicodeDecodeError`). | Local Canon (`GUARD_IN_MEMORY`); prompt `:80-82` | A splice that guesses on a shape it doesn't know fails it |
| AC-144.4 | unit | `GUARD_GATE`: with `pathlib.Path.read_bytes` patched to raise, `guarded_model` returns `str(path)` and logs nothing for an INT8 id on a missing path, an FP16 id on a missing path, and an FP16 id on a file one byte longer than the spec's size. | Local Canon (`GUARD_GATE`, D-1137) | A guard that reads every file fails it |
| AC-144.5 | unit | A file of the spec's size whose hash differs returns `str(path)` and logs nothing (`GUARD_PASS_THROUGH`). | Local Canon; prompt `:81` ("a source file with an unknown hash is not patched and FP16 still loads as shipped") | A guard that patches an unknown file fails it |
| AC-144.6 | unit | `GUARD_REFUSE`: a spec whose source is the spliced synthetic file returns `str(path)` with one warning `{event: "tts.phase_guard", outcome: "refused", reason: "SpliceError", variant_id}`; a spec with the right source and a wrong `guarded_sha256` returns `str(path)` with one warning, `reason: "result_hash"`; no value in any event holds `str(tmp_path)` or the file name. | Local Canon; prompt `:81-82` ("a result whose hash is wrong is refused"); D-323 | A guard that returns unverified bytes fails it |
| AC-144.7 | unit | `GUARD_APPLIED`: with the synthetic spec, the result is `bytes` equal to `splice(build())`, and the log holds exactly one event, whose keys are exactly `event`, `log_level`, `module`, `variant_id`, `outcome`, with `outcome: "applied"`, `log_level: "info"`. | Local Canon (`GUARD_APPLIED`) | A missing or chatty event fails it |
| AC-144.8 | unit | `NO_FILE_WRITE`: after an applied, a refused and a pass-through call on the same folder, every file keeps its bytes and `st_mtime_ns`, and the folder lists the same names. | Local Canon (`NO_FILE_WRITE`; prompt `:84-85`) | A guard that writes a sidecar or patches in place fails it |
| AC-144.9 | integration | `BOTH_SESSIONS` (`tests/integration/test_tts_phase_guard_load.py`): `KokoroAdapter.load_model` on an FP16 variant over the synthetic file, with `KOKORO_FP16` patched to the synthetic spec, a CUDA device probe and a recording `InferenceSession` fake that raises for CUDA providers: the fake is called twice, both times with the same `bytes` object (`is`), equal to `splice(build())`; the wrapped `guarded_model` is called once; the adapter reports `cpu`. With CUDA accepted, the one CUDA session gets the bytes. An INT8 variant gives both calls `str(path)`. | Local Canon (`BOTH_SESSIONS`; `adapter.py:397-418`) | A guard on one branch only, or two splices, fails it |
| AC-144.10 | guard | The four pin files in §Test pins pass at Red and at Green and are byte-identical to row 0 (`baseline-scope.json`). | Local Canon (§Test pins) | A guard that changes the path a fake receives fails it |
| AC-144.11 | integration | Real ORT through the adapter: `load_model` on CPU over the synthetic file with the synthetic spec patched in gives a session whose `run(["y"], {a: 0, b: 0})` is `+0`; with `KOKORO_FP16` left as shipped (the size differs) the same file gives NaN. | Local Canon (`GUARD_IN_MEMORY`, `GUARD_GATE`) | In Red the module does not exist |
| AC-144.12 | check | `guard-check.py` on `models-copy`: `guarded_model(<models-copy FP16>, "kokoro-onnx-fp16")` returns 163,235,204 bytes with SHA-256 `9037c82b…`; the file keeps SHA-256 `ba4527a8…`, its size and `st_mtime_ns`; an ORT CPU session builds from the bytes; one `applied` event; the INT8 file returns `str`; the `tracemalloc` peak of the FP16 call, its read included, is at most 400,000,000 bytes (`ONE_JOIN`; 329.2 MB at plan time); the receipt prints the wall time and the peak. | Local Canon (`GUARD_BYTES_EQUAL`; D-797) | A splice that differs from Session 73's bytes fails it (S10) |
| AC-144.13 | check | Packaged Red (row 3): the FP16 smoke on the pre-change build exits 1 with 149 jobs and 12 failures, all "generated audio must be finite", equal by `(kind, index, voice)` to `s52-smoke-red.json` and `s73-smoke-control.json`; the dead proxy is set; no errors and no forbidden folders. `BUILD_SAME`: its 137 Done WAVs equal Session 73's `run-control` by job. | Local Canon (resolution path; Session 73 row 5) | A tree that no longer fails, or fails differently, stops (S11) |
| AC-144.14 | check | Packaged Green (row 7): the FP16 smoke on the post-change build and the same unmodified `models-copy` exits 0, 149 of 149, no failures; `WAV_BY_JOB`: all 149 WAVs equal Session 73's `run-guarded` by job; `NO_FILE_WRITE`: `models-copy` equals `ff-models-snapshot-0.json`. | Local Canon (the resolution path's done condition; D-797) | One failing job, a WAV that differs, or a changed model file fails it |
| AC-144.15 | check | INT8 (row 8): the INT8 smoke on the post-change build passes 149 of 149, and its 149 WAVs equal Session 73's `run-int8` by job; the snapshot still matches. | Local Canon (`GUARD_GATE`: other variants unchanged) | A guard that reaches INT8 fails it |
| AC-144.16 | check | `PRESELECT_KEPT`: `tts-controls.ts` and `voices.py` keep their row-0 SHA-256, and the `PRESELECT_ORDER` line still reads `['kokoro-onnx-int8', 'kokoro-onnx-fp32']`. | Human-approved (D-330, D-331; D-797) | A preselection change fails it |
| AC-144.17 | check | Records (row 9): `TTS-ONNX-FP16-NONFINITE-AUDIO` is `resolved` with `verification` and `meu_links` holding MEU-62, MEU-72, MEU-121, MEU-127 and MEU-144, the `resolution_path` byte-equal to row 0's; `issue_triage.py render --check` passes; MEU-144 is `ready_for_review`; `meu_status.py render --check` passes; the 03 section holds the Delivered note; grouping row 74 reads `executed (Session 74)` with this plan folder and no other grouping line changed. | Local Canon (D-797, D-801; D-1139) | A missing record or a changed resolution path fails it |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Which graph ships | Human-approved | Session 73's guarded graph (D-797) |
| How it reaches the app | Human-approved (Mat, 2026-11-17) | In memory at load, from the user's file, checked by both hashes (D-1136 A) |
| Which files the guard touches | Local Canon | Only an FP16 file with Session 73's size and source hash; never written (`GUARD_GATE`, `NO_FILE_WRITE`; D-1137) |
| What a failed guard does | Local Canon | Loads the file as shipped and logs one warning with no path (D-1137; D-323) |
| Preselection | Human-approved | Unchanged (D-330, D-331) |
| How the fix is proved | Human-approved | Scripts and tests (Mat 2026-11-16); design D-1138 |
| Registration | Human-approved (Mat, 2026-11-17) | MEU-144, 03 section, matrix 3.21 (D-1135 A; D-801) |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `packages/infrastructure/src/avkit_infra/tts/phase_guard.py` | new | CRLF | `GUARD_IN_MEMORY`, `GUARD_GATE`, `GUARD_REFUSE`, `GUARD_APPLIED` |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modify | CRLF, kept | `BOTH_SESSIONS`: one import, one inserted line, two replaced |
| `tests/tts_onnx_synthetic.py` | new | CRLF | The synthetic FP16 model builder and its pins |
| `tests/unit/test_tts_phase_guard.py` | new | CRLF | AC-144.1 to AC-144.8 |
| `tests/integration/test_tts_phase_guard_load.py` | new | CRLF | AC-144.9, AC-144.11 |
| `docs/build-plan/03-service-layer.md` | modify (script) | CRLF, kept | Row 1: the MEU-144 section before `:704`; row 9: its Delivered note |
| `docs/build-plan/build-priority-matrix.md` | modify (script) | CRLF, kept | Row 1: row 3.21 |
| `.agent/context/meu-status.yaml` | modify (script, tool) | LF, kept | Row 1: MEU-144 `pending`, `:43`, `:4171`; row 9: `ready_for_review`; H2-2: `approved` |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | regenerate | LF | `meu_status.py render` |
| `.agent/context/known-issues.yaml` | modify (script) | LF, kept | Row 9: the issue resolved |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` | modify | LF, kept | Row 74 (`:162`) only |

**Line endings** were measured with Python bytes (`s74-plan-eol.json`, `s74-plan-eol2.txt`). CRLF: `adapter.py`, `voices.py`, 03 (84,852 bytes), the matrix (25,606 bytes), `current-focus.md`, `docs/execution/metrics.md` (111,325 bytes), `test_tts_models.py`, `test_tts_device_resolution.py`, `test_tts_no_torch.py`, `tests/tts_g2p_fakes.py`, `test_tts_async.py`, `test_tts_g2p.py`, `test_tts_assets.py`, `tts-controls.ts`. LF: `meu-status.yaml` (149,432 bytes), `meu-registry.md`, `BUILD_PLAN.md`, `known-issues.yaml` (518,856 bytes), `known-issues.md`, the grouping (19,174 bytes), `test_api_model_load_keeps.py`, the tts `__init__.py`. The four new Python files are CRLF, as their neighbours are. A CRLF file is read and written with `newline=""` from CRLF text; `eol-check.py` checks every scope path after rows 1, 5 and 9 and in the gate. This plan's markdown files are LF.

### Project files

- **Plan-local scripts**, all in this plan folder, written at execution (none exists at plan time):
  - row 0: `baseline.ps1`, and `red-check.py`, `identity.py`, `issue-resolve.py` and `eol-check.py` copied from `2026-11-17-test-run-reliability/` with this plan's values; `smoke-check.py` (`copies`, `control`, `green`, `wavs` and `snapshot` modes, with a `--selftest` on synthetic JSON and SQLite fixtures), `home-redact.py` (with a `--selftest`) and `host-load.ps1`, new;
  - row 1: `register-meu-144.py` (its `--delivered` mode runs in row 9);
  - row 6: `guard-check.py`;
  - H1-2: `session-gate.ps1`.
- **Scratch references** (read only): the plan-time probes `splice-probe.py`, `synthetic-probe.py`, `timing-probe.py` and `wav-probe.py` in `C:/Temp/av-kit/tts-fp16-guard-ship/`; Session 73's runs and models under `C:/Temp/av-kit/s73/`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`.
- **Read, never changed (bound in `baseline-scope.json`):** `ui/src/renderer/src/features/tts/tts-controls.ts`, `packages/infrastructure/src/avkit_infra/tts/voices.py`, `packages/infrastructure/src/avkit_infra/tts/__init__.py`, `packaging/avkit-backend.spec`, `tools/package_backend.py`, `tools/smoke_packaged_tts.py`, the four pin files, `tests/tts_g2p_fakes.py`, `docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/test-set.json`.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the handoff, the rolling reviews and the reflection.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json`), not to `HEAD`, and changes only its own entries or lines in it.

| File | Siblings | Rule |
|---|---|---|
| `known-issues.yaml`, `known-issues.md` | Sessions 91 to 94 (after this commit) | `issue-resolve.py` changes only this issue and binds to a hash (S4) |
| `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md` | Session 94 (MEU-158, MEU-159) | `register-meu-144.py` binds to a hash; only MEU-144 and the two summary lines change |
| Grouping §6 table | Sessions 91 to 94 | Only row 74 changes |
| `tests/integration/` | Session 93 (owns it after this commit) | One new file only; no existing file changes |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Keeping the generator in FP32 (`node_block_list`) | out-of-scope | — | D-1136: needs `onnx` and a re-export, unmeasured |
| Posting anything to Hugging Face | out-of-scope | — | D-336, D-797 |
| A preselection change for FP16 | out-of-scope | — | D-330, D-331; a separate question for Mat (prompt `:123-125`) |
| Redacting the raw home prefix in the 24 tracked files (`s73-tracked-home-scan.txt`, plus the two `known-issues.yaml` hits) | out-of-scope | — | Prompt `:128-136`: its own docs-only change after Session 74 lands; carried as an open item in the H2-6 prompt |
| A CUDA hardware proof | out-of-scope | — | No CUDA device on this host; `BOTH_SESSIONS` is proved with a fake (AC-144.9) |
| Asserting the `tts.phase_guard` event in the packaged backend's log | out-of-scope | — | The 149 of 149 and `WAV_BY_JOB` prove the packaged graph; the event is pinned in unit tests (AC-144.7) |
| Session 73 RULE-2 download variables | out-of-scope | — | No download path runs (D-1136 A) |
| Caching the guarded bytes on disk or in memory across loads | out-of-scope | — | `NO_FILE_WRITE`; a load is rare and costs about 0.7 s at most (`s74-plan-onejoin-timing.json`, `s74-peer-session-timing.txt`) |

## BUILD_PLAN.md Audit

Row 1 adds MEU-144 to `meu-status.yaml` and regenerates `meu-registry.md` and `docs/BUILD_PLAN.md`; row 9 and H2-2 change only its status. H1-3 confirms the render:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/tts-fp16-guard-ship/ff-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/tts-fp16-guard-ship/ff-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` follows `2026-11-17-test-run-reliability/baseline.ps1`:

1. **Tree state.** `baseline.sha` (`HEAD`), `baseline-dirty.txt` (`git status --porcelain --untracked-files=all`), the worktree list, and the host load.
2. **Path-scoped baseline, bound to content.**
   - `baseline-scope.json`: the SHA-256 of each §Files Modified path and each "Read, never changed" path, or `absent`; the four new Python files and the handoff must be `absent`.
   - `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope, or `deleted`.
   - `baseline-eol.json`: for each scope path, its kind (`CRLF`, `LF`, `MIXED`) and its CRLF and bare-LF counts.
   - `baseline-skip-hashes.json`: the SHA-256 of every tracked or untracked, not-ignored file under `ui/`, `mcp-server/`, `tools/`, `packages/api/` and `packages/core/`; at the gate none may differ, be added or be removed (H1-4).
   - A copy of each scope file's bytes under `C:/Temp/av-kit/tts-fp16-guard-ship/baseline-copies/<path>`.
   - **The S2 binding: every cited line is re-read.** Each anchor is found by its text and counted once: `adapter.py`'s two `InferenceSession(str(path)` lines and `log = structlog.get_logger(module="tts")`; `voices.py`'s `ONNX_REVISION` and `SIDELOAD_SUFFIXES`; `PRESELECT_ORDER` in `tts-controls.ts`; 03's `download-failure-reason-residual` anchor and `tts-fp16-phase-guard-residual` section; the matrix's row 3.20; `meu-status.yaml`'s last phase-3 entry, the phase-3 note and the P2 range; grouping row 74 `proposed`; the issue `open` with its four meu_links; MEU-144, `AC-144.` and D-1135 to D-1144 absent from the registers and the handoffs; `phase_guard.py` absent. Each anchor's current line number is printed beside its plan-time number; a moved line is recorded and corrected in the handoff (Session 51 RULE-3), and only a missing or doubled anchor stops (S2).
   - The inputs: each Session 73 path named in §Goal exists, with the FP16 sha in `s73/models-original`, and the two smoke JSONs and the test set keep their plan-time SHA-256 (S8).
3. **Base receipts.** The host-load wait runs first. Then the full Python suite with the D6 argv without `-x`, `TMP` and `TEMP` set (`ff-base-py.txt`); failures are recorded, not fatal, and the gate excuses only those ids (the Session 49b baseline rule). `ruff format --check` and `ruff check` on `adapter.py` and the four pin files (`ff-base-ruff.txt`; all clean at plan time, `s74-plan-ruff-base.txt`).
4. **Plan-local scripts.**
   - `red-check.py` and `identity.py` are copied from `2026-11-17-test-run-reliability/` with this plan's `PLAN`, `PROJECT_ARTIFACTS` (the handoff, the reviews, the reflection, `metrics.md`, `current-focus.md`) and `DECLARED_NEW`; `red-check.py`'s boundary fixtures are renamed so that `test_ac_144_1` is checked against `test_ac_144_10` to `test_ac_144_17`; `identity.py`'s other-plan skip covers untracked `docs/execution/plans/2026-11-1[5-7]-<slug>/` folders other than this one.
   - `issue-resolve.py` is copied with `SCRATCH` at `C:/Temp/av-kit/tts-fp16-guard-ship/issue-resolve` and `RESOLVE_KEYS` of `status`, `verification` and `meu_links`.
   - `eol-check.py` is copied with this plan's scope and `baseline-copies/`.
   - `smoke-check.py` and `home-redact.py` are new (below), each with a `--selftest`.
   - `host-load.ps1` is new: it samples `Win32_Processor.LoadPercentage` five times; above 50 % it waits, re-sampling every 30 s for up to 20 minutes, prints the value it ran at, and exits 1 after 20 minutes (S15). Rows 3, 7 and 8, the base receipts and the gate's `host-load` step call it.
   - The selftests run, and `ruff format --check` and `ruff check` run on the plan folder's Python (Session 82 RULE-1).
5. **Secrets and the fleet hub.** The scope walk drops `.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.claude/settings.local.json` and `.agent/fleet/hub` before any stat or read (Session 83 RULE-2).

If any step except the base Python receipt fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** Row 4 runs the two new files and `red-check.py --require` names `test_ac_144_1` to `test_ac_144_9` and `test_ac_144_11`; each must fail by `AssertionError` on the `find_spec` line or after it. The same row runs the four pin files, which must pass (AC-144.10).
- **Expectations stay immutable in Green** (S3). Row 4 records the SHA-256 of the three new test-side files (`ff-red-hashes.json`); row 5 checks them.
- **Green** (row 5) runs the two new files, the four pin files and the other TTS tests next to the adapter (`tests/integration/test_tts_assets.py`, `tests/integration/test_tts_voice_packs.py`, `tests/unit/test_tts_async.py`, `tests/unit/test_tts_g2p.py`), then `ruff format --check` and `ruff check` on the changed and new Python files, `pyright packages/`, and `eol-check.py`.

### 3. The real-file and packaged proofs (rows 2, 3 and 6 to 8)

- **`guard-check.py`** (row 6, AC-144.12) puts `packages/infrastructure/src` on `sys.path`, imports `phase_guard`, records the FP16 file's SHA-256, size and `st_mtime_ns` in `models-copy`, starts `tracemalloc`, calls `guarded_model` under `structlog.testing.capture_logs`, checks the result's length and SHA-256, builds an ORT CPU session from it, calls `guarded_model` on the INT8 file, re-reads the FP16 file's identity, and prints one JSON object with each check, the wall time and the peak. Exit 0 only when every check holds, the peak included (at most 400,000,000 bytes, `ONE_JOIN`); a pass-through or refusal on the real file, or a peak over the limit, is S10.
- **`smoke-check.py`**:
  - `copies --run RUN_DIR --models DIR`: exit 0 when `RUN_DIR/avkit-backend/avkit-backend.exe` and `_internal` exist, no `torch`, `kokoro`, `phonemizer` or `espeakng_loader` folder is under `_internal`, and the FP16 file in `DIR` has SHA-256 `ba4527a8…` and 163,234,740 bytes.
  - `control SMOKE_JSON`: exit 0 when `passed` is false, `jobs` is 149, `variant_id` is `kokoro-onnx-fp16`, there are 12 failures, each "generated audio must be finite", the failure set by `(kind, index, voice)` equals both `s52-smoke-red.json` and `s73-smoke-control.json`, `errors` and `forbidden_dirs` are empty and `proxy.HTTPS_PROXY` is `http://127.0.0.1:9`.
  - `green SMOKE_JSON --variant ID`: exit 0 when `passed` is true, `jobs` is 149, `failures`, `errors` and `forbidden_dirs` are empty, the variant matches and the dead proxy is set.
  - `wavs RUN_DIR --against S73_RUN --expect-done N --out JSON`: copies each run's `app-data/avkit.db*` under `tmp/` (never opened in place), keys rows by `(text_hash, voice)`, requires 149 keys with one row each in both, and exit 0 only when `N` keys are `Done` in both with byte-equal WAVs and, for `N` 149, every key is `Done`.
  - `snapshot DIR --out JSON` and `snapshot DIR --compare JSON`: each file's relative path, size, SHA-256 and `st_mtime_ns`; compare exits 0 only on equality, with no file added or removed.
- **`home-redact.py RAW OUT`** replaces every form of the home prefix (`Path.home()` with backslashes, with forward slashes, and JSON-escaped) with `<HOME>`, writes `OUT`, deletes `RAW`, and exits 1 if any form is left; with `--in-place` it rewrites a JSON file and checks that it still parses; with `--scan-cited HANDOFF --scan-dir DIR` (H1-6, S16) it reads every `ff-*` receipt name the handoff cites, scans each one under `DIR` for every form of the prefix, and exits 1 on a hit or a cited receipt that is missing.
- **After each smoke** the row lists `avkit-backend.exe` processes whose executable is under that run folder; one still running is S13 (detect, never kill).

### Session gate (H1-2)

`session-gate.ps1` follows `2026-11-17-test-run-reliability/session-gate.ps1`: one receipt per step in `C:/Temp/av-kit/tts-fp16-guard-ship/`, named `ff-D6-<step>`; fail-fast, with later steps printed as `not_run`; the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `task-contract`; `scope-paths` (every changed path is in §Files Modified, this plan folder, the closeout artifacts or `baseline-dirty.txt`, and every `baseline-dirty.txt` path outside this scope keeps its row-0 content); `line-endings` (`eol-check.py`); `home-path` (`tools/check_home_path.py`); `red-check-selftest`, `eol-check-selftest`, `smoke-check-selftest`, `home-redact-selftest`; `py-format` (`ruff format --check` on `phase_guard.py`, `adapter.py`, the three new test-side files and this plan folder's Python); `py-lint` (the D6 argv, `ruff check packages/ tests/`, plus this plan folder's Python); `py-types` (`pyright packages/`) |
| Targeted | `meu-144-unit` (`tests/unit/test_tts_phase_guard.py`); `meu-144-integration` (`tests/integration/test_tts_phase_guard_load.py` and the four pin files); `guard-check` (`guard-check.py` on `models-copy`) |
| Host load | `host-load`: samples `Win32_Processor.LoadPercentage` five times; above 50 % it waits, re-sampling every 30 s for up to 20 minutes, and records the value it ran at (Session 81 RULE-2, with this session's 50 % bar); still above 50 % after 20 minutes is S15 |
| Fresh full | `py-tests` (the D6 argv, `TMP` and `TEMP` set); `state-render` (`meu_status.py render --check`); `issues-render-check` (`issue_triage.py render --check`); `canon-vitest` (pwsh in `ui/`: `npm run test -- tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts`, which read `meu-status.yaml` and `BUILD_PLAN.md`) |
| Skipped, with reason | `ui-types`, `ui-lint`, `ui-tests` (full), `ui-build`, `ui-electron`, `mcp-*`: every file under `ui/` and `mcp-server/` keeps its `baseline-skip-hashes.json` hash, and none was added or removed (H1-4). `openapi`: `packages/api/` and `packages/core/` keep their hashes, so no route or schema changed. The packaged smokes are not rerun in the gate: rows 7 and 8 ran them on the final `phase_guard.py` and `adapter.py`, and `scope-paths` with `identity.py` shows neither changed since (their SHA-256 are recorded in `ff-green-source-hashes.json` at row 7 and compared here) |

If `py-tests` stops on an id that `ff-base-py.txt` shows failing, the step runs the D6 argv again without `-x` and passes when its failures are a subset of the base ids. A full-run failure on a test outside this scope that is not in the base is rerun once alone; if it passes, the gate is rerun once after the host-load wait, and a second failure is S5.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds an anchor missing or counted twice, the issue not `open`, MEU-144, `AC-144.` or an id from D-1135 to D-1144 already in use, `phase_guard.py` present, or grouping row 74 not `proposed` | Stop; another session moved this ground. Bring the binding receipt to Mat. A line that only moved is recorded and corrected in the handoff (RULE-3), not a stop |
| S3 | A Red receipt fails `red-check.py` (a Red that passes on old code, a module-not-found or collection error), the AC-144.10 guard fails at Red, or a Green row needs a changed expectation | Fix the test setup; never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, a `baseline-dirty.txt` path changes content, or a register lacks its expected hash when its script runs | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An existing test fails after Green (M-7), or a full-run failure repeats (§Session gate) | Stop: an M-7 question, not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | A build fails | Stop with the redacted build receipt; never change the spec or the environment to pass |
| S8 | A Session 73 input named in §Goal is missing or changed | Stop. Getting it again is a download, which is Mat's (D-1136) |
| S9 | A run folder or `models-copy` already exists at row 2 or row 7 | Stop and tell Mat; never delete one |
| S10 | `guard-check.py` sees the guard pass through or refuse on `models-copy`, a result other than `9037c82b…`, or a `tracemalloc` peak over 400,000,000 bytes | Stop and route back: the shipped file or the splice differs from Session 73's |
| S11 | The control smoke (row 3) does not exit 1, or its failures differ from Session 52's and Session 73's | Stop: today's tree no longer matches the measured defect; bring the receipt to Mat |
| S12 | A WAV differs by job (`BUILD_SAME`, `WAV_BY_JOB` or INT8), or a key has more than one row | Stop and bring the job list to Mat: a WAV that differs from what Mat heard is a listening question under D-1136 |
| S13 | An `avkit-backend.exe` under a run folder still runs after its smoke | Detect, never kill; stop and tell Mat the pid |
| S14 | A file under `ui/`, `mcp-server/`, `tools/`, `packages/api/` or `packages/core/`, or `voices.py`, `tts-controls.ts` or `packaging/avkit-backend.spec`, changes | Stop: this session changes only the guard and the adapter |
| S15 | The host load stays above 50 % for 20 minutes before a smoke, a full pytest run or the gate | Stop and tell Mat; never run them above 50 % |
| S16 | A cited receipt, a plan file or the handoff holds the raw home prefix | Redact it with `home-redact.py` and rescan; a tracked file outside this scope is the out-of-scope redaction item, recorded, not edited |
| S17 | Mat changes his D-1135 A or D-1136 A ruling, or rules a folded item (D-1136) differently | The rows marked in `task.md` are re-planned and the plan goes back to review before execution |

## Decision Log

> [!NOTE]
> **Two briefs were Mat's, and he ruled A on both (USER_EXPLICIT 2026-11-17, AskUserQuestion in the coordinator session, relayed by the coordinator).** D-1135 (the registration) hits M-8 (a new MEU). D-1136 (the delivery route) hits M-5 (what a user's FP16 load does, and whether a file in their models folder changes); its alternatives hit M-2 (B overwrites the only copy of the pinned bytes; C writes 163 MB into the user's models folder but destroys nothing) and M-4 and M-12 (D needs a host and a published file). Both are reserved by the session prompt (`:87-128`: the registration and how it ships) and by grouping §5 ("Mat confirms the MEU registration and picks the delivery route at its plan gate"), so neither was handed to the agent, whatever its M list. Both are recorded in the `decision_log:` below with `resolution: human`, `source_tag: Human-approved`, the chosen option and `human_message_reference` quoting his words.
>
> **Folded into D-1136.** The prompt also reserves a new dependency, a download, a user-data read, listening and closing the issue. Under D-1136 A none of them needs a choice: A adds no package and downloads nothing; it reads only `C:/Temp` copies; the bytes it loads equal the file Mat heard (`GUARD_BYTES_EQUAL`), so the prompt's own rule gives no new listening; and the issue closes on the resolution path's smoke with the preselection left as a separate question. They are stated in D-1136's brief and confirmed with it rather than briefed one by one. Under any other option each comes back as its own brief.
>
> **Autonomous with `mandatory: none`:** D-1137 (the guard's design), D-1138 (the test design) and D-1139 (the record mechanics). Each passed the §4a list and the §4 test, and each is conditional on D-1135 A and D-1136 A (S17). No M item is hit: no API, OpenAPI or MCP change (M-4 clear), no user data read or written (M-2 clear), no existing test's assertion changes (M-7 clear), no new policy (M-3 clear).
>
> **Earlier rows are not copied here.** D-239 and D-801 are on the issue's `enrichment.decision_log`; D-1131 to D-1134 are in grouping §8 (Session 74 carries D-1131 and D-1133); D-797 is a Session 73 execution decision (`2026-11-14-tts-fp16-phase-guard/implementation-plan.md:529`) and D-336, D-333, D-330 and D-331 are Session 52's; this plan applies them and gives them no new record. H2-2 reads them through `--decision-source` on the grouping, on Session 73's plan and on `.agent/context/known-issues.yaml` with `--decision-issue TTS-ONNX-FP16-NONFINITE-AUDIO`. `decision_sources` was probed at plan time with this plan as a source (Session 90 RULE-2, `s74-plan-decision-probe.txt`): with this plan, the grouping and the register it reads D-1131 to D-1134 (grouping), D-1137 to D-1139 (planning), D-239 and D-801, but not D-797, which it reads only when Session 73's plan is added; it did not read D-1135 or D-1136 while they were `open_decisions`; with Mat's rulings recorded in `decision_log`, a rerun reads both with stage `planning` from this plan (`s74-plan-decision-probe-ruled.txt`). Under HDP §6 the reflection's `### Decisions Log` lists only this session's reversible autonomous choices. D-1140 to D-1144 stay free for execution.

```yaml
decision_log:
  - id: D-1137
    stage: planning
    question: "How does the guard decide which file to splice, and what does it do when it can't?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "GUARD_GATE then GUARD_REFUSE: only the kokoro-onnx-fp16 id is considered; a stat whose size is not the spec's returns the path with no read; a source hash other than Session 73's returns the path with no log; a splice that raises, or a result whose hash is not Session 73's guarded hash, returns the path and logs one tts.phase_guard warning with the variant id, outcome refused and a reason that is a class name or result_hash; an applied guard logs one info event; no event carries a path; guarded_model never raises; it is called once in _load_onnx before the CUDA branch and its result feeds both InferenceSession calls; nothing is cached or written."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/session-74-prompt.md:80-82 - a source with an unknown hash is not patched and FP16 still loads as shipped; a result whose hash is wrong is refused"
      - "packages/infrastructure/src/avkit_infra/tts/adapter.py:397-418 - the CUDA session and the CPU fallback both take the model"
      - ".agent/context/known-issues.yaml:4374 - the resolution path: patch at load time with source and result hashes"
      - "D-323 - no log carries a local path"
      - "C:/Temp/av-kit/tts-fp16-guard-ship/s74-plan-timing.json - the size gate skips the 0.2 s hash for any other file"
    research: { engine: none, sources: [] }
    reasoning: "The size check first means an INT8, FP32 or sideloaded file costs one stat. A silent pass-through on an unknown hash is the prompt's own rule: a newer upstream file is not Session 73's graph, so it loads as shipped and the issue's register entry still describes it. A refusal on a known source is a defect in the guard itself, so it is logged, once and without a path, and the load still goes ahead as shipped rather than failing the user's load. Raising instead lost: a guard bug would block FP16 entirely, worse than today. One call before the branch keeps the CUDA fallback from splicing twice. Two-way: one module and three adapter lines."
  - id: D-1138
    stage: planning
    question: "How are the guard and the shipped graph proved?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Unit and integration tests on a 375-byte synthetic FP16 Div then Atan graph built by tests/tts_onnx_synthetic.py, run through real ONNX Runtime (0/0 gives NaN before and +0 after; 1/2 bit-identical) with the module's KOKORO_FP16 patched to the synthetic spec; the refusals built as variants of the same graph; guard-check.py on a C:/Temp copy of Session 73's original models for the real 163 MB file; the packaged FP16 smoke on a build of today's tree before the change (Red, 12 of 149, equal to Sessions 52 and 73), after it (Green, 149 of 149) and INT8, with WAVs compared per job against Session 73's runs and the models copy snapshotted before and after; no model file in the repository and no read of the user's models folder."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/tts-fp16-guard-ship/s74-plan-synthetic.json - the synthetic graph shows the defect and the fix in ORT"
      - "C:/Temp/av-kit/tts-fp16-guard-ship/s74-plan-splice.json - the stdlib splice is byte-equal to Session 73's guarded file"
      - "C:/Temp/av-kit/tts-fp16-guard-ship/s74-plan-wavs.json - Session 73's WAVs by job: 137, 149, 149"
      - "docs/execution/plans/2026-11-14-tts-fp16-phase-guard/task.md rows 1 and 5 - the build, copy and control shape"
      - "Mat 2026-11-16: 'This should be done with framework and scripts!'"
    research: { engine: none, sources: [] }
    reasoning: "A unit test cannot hold a 163 MB model, and committing one is ruled out, so the synthetic graph carries the same Div then Atan shape and the same failure. The real file is checked once by script against Session 73's exact bytes, and the packaged smoke is the resolution path's own done condition. Comparing WAVs by job proves the app's in-memory graph gives what Mat heard, so no listening is needed. A Red on today's build shows the defect still reproduces before the change. Two-way: tests and plan-local scripts."
  - id: D-1139
    stage: planning
    question: "How are MEU-144 and the issue recorded?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "register-meu-144.py writes the 03 section before :704, matrix row 3.21 and the meu-status entry, each bound to its row-0 SHA-256, then meu_status.py render; row 9 appends the 03 Delivered note, resolves the issue through issue-resolve.py with status, verification and meu_links (MEU-144 added, the resolution_path kept verbatim), renders both registers, sets MEU-144 ready_for_review and sets grouping row 74 to executed; the stale tts-controls.ts:108 citation in 03's Session 52 note is corrected in the handoff, not edited."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-queue-pause-feedback/register-meu-155.py - the registration script shape"
      - "docs/execution/plans/2026-11-17-test-run-reliability/issue-resolve.py - the resolve script shape"
      - ".agent/context/known-issues.yaml:4421 - D-801 holds MEU-144 and matrix row 3.21"
      - "docs/build-plan/03-service-layer.md:688-702 - the MEU-127 section the new one follows"
    research: { engine: none, sources: [] }
    reasoning: "The scripts bind each register to its content, so a parallel session's write stops the row instead of being overwritten. Keeping the resolution path verbatim keeps D-797's text where Mat ruled it. Editing the Session 52 note would change approved text for a line number; the handoff records the move. Two-way: register rows."
  - id: D-1135
    stage: planning
    question: "Should the FP16 guard ship as its own MEU, MEU-144, with its own build-plan section?"
    resolution: human
    class: governance-value
    mandatory: [M-8]
    chosen: "A: register MEU-144 (svc-tts-fp16-guard-ship), matrix row 3.21, a new 03 section after the MEU-127 section, depending on MEU-127"
    recommendation: "A: register MEU-144 (svc-tts-fp16-guard-ship), matrix row 3.21, a new 03 section after the MEU-127 section restating D-797, D-336, D-333 and D-330 and D-331, depending on MEU-127"
    alternatives:
      - "B: reopen MEU-127 and deliver under it"
      - "C: fix it with no MEU, as test and tooling debt is"
      - "Do nothing: no session; FP16 stays as shipped and the issue stays open"
    source_tag: Human-approved
    precedents:
      - ".agent/context/known-issues.yaml:4421 - D-801 holds MEU-144 and matrix row 3.21 for this session"
      - "C:/Temp/av-kit/session-74-prompt.md:88-93 - the registration is Mat's at the plan gate"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:150 - Mat confirms the MEU registration at the plan gate"
    research: { engine: none, sources: [] }
    reasoning: "Ruled by Mat on 2026-11-17 in the coordinator session's AskUserQuestion, relayed to this plan by the coordinator: A, as recommended. Reserved by the session prompt and grouping §5. M-8: a new MEU. B lost because MEU-127 is an approved measurement spike and a product change under it mixes the two; C lost because the register would lose the link from the issue to the code that fixed it; doing nothing leaves FP16 failing 12 of 149. Rows 1 and 9, H1-3, H1-6 and H2-2 rest on A."
    human_message_reference: "USER_EXPLICIT 2026-11-17 AskUserQuestion 'A: register MEU-144 (Recommended)'"
  - id: D-1136
    stage: planning
    question: "How does the guarded graph reach a user who picks ONNX FP16?"
    resolution: human
    class: product-preference
    mandatory: [M-5]
    chosen: "A: build the guarded graph in memory on each FP16 load from the user's file, checked against Session 73's source and result hashes; no file is written; no new package, no download, no user-data read, no new listening; the issue closes when the 149-job packaged smoke passes, and FP16's preselection stays a separate question"
    recommendation: "A: build the guarded graph in memory on each FP16 load from the user's file, checked against Session 73's source and result hashes; no file is written; no new package, no download, no user-data read, no new listening; the issue closes when the 149-job packaged smoke passes, and FP16's preselection stays a separate question"
    alternatives:
      - "B: patch the downloaded file once in place, after download or on first load, checked by both hashes"
      - "C: write the guarded graph beside the download as a second file and load that"
      - "D: fetch a guarded file from another host"
      - "E: keep the generator in FP32 with a node_block_list re-export"
      - "Do nothing: ship nothing yet; FP16 stays as shipped"
    source_tag: Human-approved
    precedents:
      - ".agent/context/known-issues.yaml:4374 - D-797's resolution path names the three routes"
      - "docs/execution/plans/2026-11-14-tts-fp16-phase-guard/closeout-decisions.md:35-38 - the three routes"
      - "C:/Temp/av-kit/session-74-prompt.md:94-128 - how it ships, a dependency, the inputs, a user-data read, listening and closing the issue are Mat's"
      - "C:/Temp/av-kit/session-74-prompt.md:100-103 - the prompt recommends patching the file once (B)"
      - "C:/Temp/av-kit/tts-fp16-guard-ship/s74-plan-timing.json - ORT accepts bytes; the guard step took 0.727 s in the first splice form"
      - "C:/Temp/av-kit/tts-fp16-guard-ship/s74-plan-onejoin-timing.json - the guard step takes 0.572 to 0.649 s in the one-join form"
      - "C:/Temp/av-kit/s74-peer-session-timing.txt - a session from bytes builds no faster than from the path"
      - "C:/Temp/av-kit/s74-peer-tracemalloc.txt - the first splice form peaks at 835.3 MB"
      - "C:/Temp/av-kit/tts-fp16-guard-ship/s74-plan-onejoin.json - the one-join form peaks at 329.2 MB and gives the same bytes"
      - "packages/infrastructure/src/avkit_infra/model_manager/manager.py:67-73 - an existing file is reused after is_file() only; no integrity check"
      - "packages/infrastructure/src/avkit_infra/model_manager/manager.py:102-118 - the sideload scan keeps one path per variant id, in sorted order"
    research: { engine: none, sources: [] }
    reasoning: "Ruled by Mat on 2026-11-17 in the coordinator session's AskUserQuestion, relayed to this plan by the coordinator: A, as recommended, after the expert pass. The ruling also settles the five folded items. Reserved by the session prompt and grouping §5; M-5 for A. The prompt recommended B (session-74-prompt.md:100-103), and A departs from it. B overwrites the only copy of the pinned bytes, so undoing it means a new download (M-2); a safe rewrite of 163 MB needs a temp file and a rename; and B still needs the read and the hash check on each load, so it saves only the splice and one hash, about 0.3 s. C destroys nothing, but it writes 163 MB into the user's folder under a name that competes with the original for the one FP16 entry in the sideload scan, where sort order decides the winner, and it needs the same redirect code as A. D hits M-4 and M-12; E needs a new package. A is undone by reverting the code. Rows 4 to 9, H1-6 and H2-2 rest on A, and the folded items hold only under A."
    human_message_reference: "USER_EXPLICIT 2026-11-17 AskUserQuestion 'A: guard in memory (Recommended)'"
  - id: D-1140
    stage: execution
    question: "How are the four sibling sessions' plan folders and plan reviews, written while this session runs, treated by the scope, identity and baseline checks?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "As foreign: the plan folders e2e-pointer-flakes, mcp-audit-refresh, ui-small-fixes and video-tail-frame and their untracked handoffs are recorded in baseline-dirty.txt, never hashed, read or bound by baseline.ps1, skipped by identity.py's OTHER_PLAN and OTHER_HANDOFF patterns, and left out of the scope checks and commit-paths.txt."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/dispatch/s74-executor-brief.txt - the sibling paths are foreign: never touch them, exclude them from the scope checks and commit-paths, record them in baseline-dirty.txt"
      - "docs/execution/plans/2026-11-17-test-run-reliability/identity.py - the other-plan skip this copy extends"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md - Sessions 91 to 94 are planned beside Session 74"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.', and USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The HDP recommendation is to skip them: their planners write those files while this session runs, so binding them would stop every row on another session's work, and no suite or gate step reads them (tests/ and tools/ name only fixed plan and handoff paths). Opening or hashing them would also risk acting on another session's evidence. Two-way: plan-local script patterns only; no product file, register or test changes."
  - id: D-1141
    stage: execution
    question: "Row 0's base ruff step failed because tests/integration/test_tts_models.py, a read-only pin file, is not ruff-formatted at 174bafa. Is that drift fatal to the baseline?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Not fatal: baseline.ps1 records ruff format --check and ruff check on adapter.py and the four pin files as the base, stays fatal on ruff format --check of adapter.py and on ruff check of all five, and prints that the pin-file format drift is recorded as base; row 0 was rerun and passed (the first run's receipts kept as ff-run1-*)."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/tts-fp16-guard-ship/ff-run1-base-ruff.txt - test_tts_models.py would be reformatted; ruff check passes"
      - "git log -- tests/integration/test_tts_models.py - the file is unchanged since b216681"
      - "the 174bafa tree: 25 files under packages/ and tests/ are not ruff-formatted"
      - "implementation-plan.md §Session gate - the gate's py-format step covers only this plan's five Python files"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.', and USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The HDP recommendation is to record the drift as base: the pin files are read, never changed, in this plan, so formatting one would change a file outside scope and break the AC-144.10 hash binding; the drift predates this session and is shared by 25 other files; the gate's own format step covers only this plan's five Python files. adapter.py, which this session edits, stays fatal on both checks, so nothing this session writes can hide behind the base. Stopping the session for a base formatting gap lost. Two-way: one plan-local script step."
  - id: D-1142
    stage: execution
    question: "Session 91's plan review stopped on a review-ledger mechanism that needs Mat. Which session does H2-6's next-session prompt start, and what does its check accept?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Session 92 (mcp-audit-refresh), with the queue 92, 93, 94 and then 91; the prompt starts 'Start Session 92' and names docs/execution/plans/2026-11-17-mcp-audit-refresh/, and says Session 91 is deferred until Mat continues its plan-review loop. H2-6's row text and check in task.md accept 'Start Session 92' with 'mcp-audit-refresh' in place of 'Start Session 91' with 'e2e-pointer-flakes'; the 'Queue empty after Session 74' branch and the MEU-144 and queue-receipt checks are kept."
    source_tag: Local Canon
    precedents:
      - "the coordinator's relay of 2026-11-18 - Session 91's plan review hit a review-ledger mechanism stop that needs Mat; the queue now runs 92 next, then 93, 94, and 91 last"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md §8 D-1133 - the queue 74, 91, 92, 93, 94 this reorders"
      - ".agent/workflows/execution-session.md §6 - the next-session prompt comes from the queue"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md §2 - critical path none; soft order: Session 94 after Session 91's commit (shared ui/tests/e2e/)"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.', and USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. The HDP recommendation is to follow the coordinator's order: a prompt that starts Session 91 would send the next session into a plan whose review loop is stopped until Mat acts, and grouping §2 gives no critical path (Sessions 92 to 94 do not depend on 91). One soft order is crossed: §2 puts Session 94 after Session 91's commit, since both edit ui/tests/e2e/, so that 94's gate runs on the steadier suite; with 91 last, Session 94's gate may meet the pointer flakes and need reruns, and the next-session prompt says so. The grouping's D-1133 order is not rewritten here; this plan only points its own prompt at the next runnable session and keeps 91 in the queue. Session 91's plan folder was not opened (D-1140); the stop is taken from the coordinator's relay. Two-way: one plan-local row and a prompt file outside the repo."
```

Expert pass (fresh context): 2 briefs. Holds: D-1135. Changed: D-1136. Not adopted: none.

### D-1135: Should the FP16 guard ship as its own MEU?

**I recommend A: register it as MEU-144, with its own section in the service-layer plan and row 3.21 in the build matrix.** The triage held exactly that number and row for this fix (D-801). It follows the section where Session 73 measured the guard, restates your rulings that bind it (ship the guarded graph, nothing posted upstream, a fix gets its own Red and review, FP16 never preselected), and depends on MEU-127. The session then closes it through review like any other MEU.

- B: reopen MEU-127 and deliver under it. MEU-127 was the measurement and is approved; reopening it mixes a finished spike with a product change.
- C: fix it with no MEU, as test and tooling debt is. This is a product change in the TTS adapter, and the register would lose the link from the issue to the code that fixed it.
- Do nothing: no session runs. FP16 stays as shipped (offered, never preselected, failing 12 of 149), and the issue stays open.

Ruling: Mat chose A on 2026-11-17 ("A: register MEU-144 (Recommended)", AskUserQuestion in the coordinator session).

Refs: `known-issues.yaml:4421` (D-801), `session-74-prompt.md:88-93`, grouping `:150`, `03-service-layer.md:688-704`, `build-priority-matrix.md:53`, M-8.

### D-1136: How does the guarded graph reach a user who picks ONNX FP16?

**I recommend A: build the guarded graph in memory each time FP16 loads, from the user's own downloaded file, and use it only when it matches Session 73's two hashes.** The app reads the file, checks it is exactly the file Session 73 measured, adds the two-node guard, checks the result is exactly the file you listened to, and hands those bytes to ONNX Runtime. Nothing on disk changes. A different file (a newer upstream file, a sideloaded one) loads as it does today. A load takes about 0.7 s longer at most (0.57 to 0.65 s measured), and while it loads it holds up to about 330 MB more memory (329 MB measured), because the splice builds its result in one pass. The splice runs only on the exact file it hashed, and its output must match one hash, so a bug in it can never reach you; the worst case is the file loaded as shipped. Undoing A means reverting the code. The session prompt recommended B; A departs from it for the reasons under B. With A: no new package is added (the splice needs only Python's standard library); nothing is downloaded (every input is already in `C:/Temp`); none of your data is read (the checks run on `C:/Temp` copies); no new listening is needed (the bytes equal the file you heard, so the session prompt's own rule applies); and the issue closes when the 149-job packaged smoke passes, with FP16's place in the preselection left as a separate question for you.

- B: patch the downloaded file once, in place, after download or on the first load. This is what the session prompt recommended. It overwrites the only copy of the pinned bytes, so undoing it means a new download. Rewriting 163 MB safely needs a temp file and a rename. Each load still has to read the file and check its hash, so B saves only the splice and one hash, about 0.3 s of A's 0.57 to 0.65 s per load (`s74-plan-onejoin-timing.json`).
- C: write the guarded graph beside the download as a second file and load that. It destroys nothing and is undone by deleting the file. But it adds 163 MB to your models folder, the app writes into that folder, and the new file competes with the original for the one FP16 entry in the model list, so the scan's sort order decides which one loads. It also needs the same redirect code as A.
- D: fetch a guarded file from another host. It needs a host and a published file, which are yours to approve, and a new download step.
- E: keep the generator in FP32 with a `node_block_list` re-export. It needs the `onnx` package in the build and has no measurement behind it.
- Do nothing: ship nothing yet. FP16 stays as shipped, never preselected, failing 12 of 149, and the issue stays open.

Expert pass: changed from the earlier wording: the load cost was a third of a second from one sample and is about 0.7 s at most, because a session builds no faster from bytes than from the path; the memory was inferred and is now measured, with the splice built in one join (329.2 MB peak against 835.3 MB) and an upper limit in AC-144.12; and B's and C's reasons now match the model manager's code, with B named as the session prompt's recommendation.

Ruling: Mat chose A on 2026-11-17 ("A: guard in memory (Recommended)", AskUserQuestion in the coordinator session), after the expert pass; the five folded items are settled with it.

Refs: `known-issues.yaml:4374` (D-797), `closeout-decisions.md:35-38`, `session-74-prompt.md:94-128`, `session-74-prompt.md:100-103` (B recommended), `adapter.py:397-418`, `voices.py:84`, `:126`, `voices.py:159-172`, `manager.py:67-73`, `manager.py:102-118`, `s74-plan-splice.json`, `s74-plan-timing.json`, `s74-plan-onejoin.json`, `s74-plan-onejoin-timing.json`, `s74-peer-tracemalloc.txt`, `s74-peer-session-timing.txt`, `s74-plan-synthetic.json`, `s74-plan-wavs.json`, M-2, M-4, M-5, M-12.

## Research References

- **ONNX Runtime `InferenceSession(path_or_bytes, sess_options=None, providers=None)`:** the first argument may be a path or the serialized model as `bytes`; ORT 1.31.1 on this host built a CPU session from the 163 MB guarded bytes in 1.319 s in one sample (`s74-plan-timing.json`), and in three rounds in 1.01, 1.14 and 1.09 s from the bytes against 1.03, 1.08 and 1.09 s from the path (`s74-peer-session-timing.txt`), so building from bytes saves nothing.
- **Protocol Buffers wire format:** each field is a varint tag `(field_number << 3) | wire_type`; wire types 0 (varint), 1 (64-bit), 2 (length-delimited) and 5 (32-bit) are the ones an ONNX `ModelProto` uses; 3 and 4 (groups) are deprecated and refused. In `ModelProto`, `graph` is field 7; in `GraphProto`, `node` is 1, `initializer` 5, `output` 12; in `NodeProto`, `input` 1, `output` 2, `name` 3, `op_type` 4; in `TensorProto`, `dims` 1, `data_type` 2, `name` 8, `raw_data` 9; FLOAT16 is data type 10.
- **ONNX `IsNaN` (opset 9+) and `Where` (opset 9+):** `IsNaN` gives a boolean mask; `Where(cond, x, y)` broadcasts a scalar `x`, so a one-element FP16 zero initializer replaces each NaN quotient.
- **IEEE 754 binary16:** `0x0000` is +0 and `0x3c00` is 1.0; `atan(+0)` is +0 with the sign bit clear.
- **`structlog.testing.capture_logs`:** collects each event dict, with the logger's bound values, in place of the configured processors.

## Planning receipts

All under `C:/Temp/av-kit/tts-fp16-guard-ship/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `s74-plan-head.txt` | `HEAD` `ecfa3f3`, one worktree (`main`) |
| `s74-plan-inputs.json`, `probe-inputs.py` | Every Session 73 and Session 52 input exists; `s52/e5-site` holds the onnx 1.23.2 dist-info (not used) |
| `s74-plan-splice.json`, `splice-probe.py` | The stdlib splice is byte-equal to Session 73's guarded file, deterministic, refuses a second splice |
| `s74-plan-timing.json`, `timing-probe.py` | Read, hash, splice and session times; ORT accepts bytes |
| `s74-plan-onejoin.json`, `s74-plan-onejoin.txt`, `onejoin-probe.py` | The splice in one join: byte-equal to Session 73's guarded file and to `splice-probe.py`; `tracemalloc` peak 313.9 MiB (329.2 MB), read included |
| `s74-plan-onejoin-timing.json`, `s74-plan-onejoin-timing.txt`, `onejoin-timing-probe.py` | The guard step in the one-join form: 0.572 to 0.649 s over three rounds |
| `C:/Temp/av-kit/s74-peer-tracemalloc.txt`, `C:/Temp/av-kit/s74-peer-session-timing.txt` | The expert pass's receipts: the first splice form peaks at 835.3 MB; a session builds no faster from bytes |
| `s74-plan-synthetic.json`, `synthetic-probe.py` | The 375-byte synthetic graph: NaN before, +0 after, finite bit-identical |
| `s74-plan-wavs.json`, `s74-plan-wavs.txt`, `wav-probe.py` | Session 73's WAVs by job: 149 jobs; Done 137, 149, 149; 137 control WAVs equal the guarded run's; one row per key |
| `s74-plan-models-mtime.json`, `models-mtime-probe.py` | `s73/models-original`: 153 files, none newer than the first Session 73 smoke |
| `s74-plan-eol.json`, `s74-plan-eol2.txt`, `eol-probe.py` | Line endings and sizes of the scope |
| `s74-plan-ssot.txt`, `s74-plan-meu-next.txt`, `s74-plan-meu-stats.txt`, `s74-plan-meu-entries.txt`, `s74-plan-meu144-grep.txt` | The SSOT: 158 MEUs, `next` MEU-158 and MEU-159, MEU-144 free |
| `s74-plan-ac144.txt`, `s74-plan-dids.txt` | 0 hits each: `AC-144.` and D-1135 onward are free |
| `s74-plan-ruff-base.txt` | `adapter.py` and `test_tts_device_resolution.py` are format-clean at base |
| `s74-plan-decision-probe.txt`, `decision-probe.py` | `decision_sources` with this plan, the grouping, the register and the issue, then with Session 73's plan added |
| `s74-plan-decision-probe-ruled.txt` | The same probe after Mat's rulings: D-1135 and D-1136 read with stage `planning` from this plan, 11 ids, then 22 with Session 73's plan (D-797 read) |
| `s74-plan-lint.txt` | `lint_task_contract.py` on `task.md` |
| `peer-h-rows.txt` | Session 89's H1 and H2 rows, the shape this plan's follow |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the issue, D-797, D-801, grouping §3 Session 74, the session prompt and the code reads above | `ff-plan-2026-11-17-tts-fp16-guard-ship` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-144.1 to AC-144.17 | `ff-execution-2026-11-17-tts-fp16-guard-ship` |
