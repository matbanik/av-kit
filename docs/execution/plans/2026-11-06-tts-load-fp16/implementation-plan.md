---
project: "2026-11-06-tts-load-fp16"
date: "2026-11-06"
source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md#session-52--tts-load-fp16-meu-119-meu-120-meu-121--p2"
grouping_source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md"
meus: ["MEU-119", "MEU-120", "MEU-121"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: A failed load keeps the model, the first-run check probes the backend's folder, and a fresh install preselects INT8 (Session 52)

> **Project:** `2026-11-06-tts-load-fp16`
> **Build plan:** `docs/build-plan/03-service-layer.md` §TTS load keeps the current model (residual) (`:612-625`, MEU-119) and §TTS ONNX FP16 audio (residual) (`:627-641`, MEU-121), and `docs/build-plan/06-gui.md` §Models folder probe (residual) (`:1560-1572`, MEU-120). The scope is grouping §3 Session 52 (`.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:172`).
>
> **Source requests,** Mat, 2026-11-06. The Session 52 brief orders MEU-119, then MEU-120, then MEU-121, and sets a split flag: the preselection ships while the FP16 cause hunt runs as a time-boxed spike. Done means "a failed load leaves the working model loaded; the first-run check probes the folder the backend uses and creates none; a fresh install preselects a model that generates the 40 sentences and the 96-word passage with no failure; the cause of the FP16 failure, or the outcome for FP16, is recorded". The brief asks the plan to say where the packaged check runs: here (D-332), and MEU-125 repeats it at the rc.2 gate.
> **Known issues:** `TTS-FAILED-LOAD-DROPS-MODEL` (P3; triage D-221), `MODELS-DIR-DOCS-AND-PROBE-MISMATCH` (P3; D-222, with D-216 recorded under it) and `TTS-ONNX-FP16-NONFINITE-AUDIO` (P2; D-239, Mat's ruling).
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review.
>
> Line anchors are from `main` `b6c3895`, read 2026-11-06 and 2026-11-07. The only untracked path at plan time is this plan folder, which holds the FP16 test set (`fp16-test-set/`, 7 files, copied 2026-11-06 per the brief). Only one worktree is open (`git worktree list`: `P:/av-kit b6c3895 [main]`).
>
> **Amended 2026-11-07 after the plan gate.** Mat ruled the four gate questions on 2026-11-07 ("D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed"; briefs and rulings in `human-gate-decision.md`). D-335 adds rows 2a and 2b, AC-119.10, `HOME_SCRUB`, `health.py` and its unit test. The amendment also corrects the D-324 B wording and adds `--no-sync` to the spike's overlays, both from the round-1 review. It goes to one recheck round of the plan review before row 0.
>
> **Corrected 2026-11-07 after recheck round 2.** Round 2 found that E5's online `--with` overlay left uv free to resolve and fetch more than the two pinned wheels (F1). E5 now installs exactly the two hashed pins with `uv pip install --no-deps --require-hashes --only-binary :all:` into a Temp target, then runs offline (§FP16 spike, E5's fetch). The wheels still enter the uv cache, inside D-333 E5's three items. The 8.3 row in §Out of Scope now says a stored `tts.models_directory` can hold a short form. Both go to recheck round 3.

## Goal

**Goal anchor:** Session 52 makes a load that fails one of its checks leave the model that was loaded in place. It makes the first-run readiness check probe the models folder the backend actually uses, without creating it. It makes a fresh install preselect ONNX INT8 instead of FP16, and proves on a fresh packaged build that INT8 generates the fixed test set with no failure. A time-boxed spike looks for the FP16 cause, and its findings, or Mat's ruling on FP16, are recorded.

Four things are wrong today:

1. **A failed load drops the working model.** `load_model` (`tts/adapter.py:286`) calls `self.unload_model()` at `:299`, before the weight check (`:301`), the device probe (`:306`) and the format branch (`:313-320`). It never reads `runtime_present` (`:274`); only the service does (`services/models.py:163`). So a load of B that fails a check leaves nothing loaded, even though A was working.
2. **The first-run check probes a folder the backend doesn't use, and creates it.** `defaultModelsDirectory` (`ui/src/main/setup-readiness.ts:51-53`) returns `{appData}/models`. On Windows that is `%LOCALAPPDATA%/av-kit/models` (`ui/src/main/index.ts:147-157`), while the backend's default is `~/.avkit/models` (`services/settings.py:67`) and no default is stored in the database (`settings.py:175-182` returns `spec.default`). `probeModelsDirWritable` (`:82`) then creates the missing folder (`:90`).
3. **A fresh install preselects FP16.** The catalog is read in id order (`database/repositories.py:355`), which puts `kokoro-onnx-fp16` first among the runnable rows of a CPU build. With nothing downloaded, `defaultModelSelection` (`tts-controls.ts:111-125`) returns `runnable[0]`. FP16 returned no finite samples on 11 of 140 sentence runs, and `_as_float32_pcm` (`adapter.py:179-192`) rightly fails the whole job with "generated audio must be finite".
4. **The FP16 cause is unknown.** What is known: it isn't length; for a voice the same sentence fails every time with every sample non-finite; FP32 and INT8 from the same revision pass; an older FP16 file failed the same two sentences but not the chunk; only onnxruntime 1.31.1 with default session options has been tried.

The session ends when the sentence smoke (`SENTENCE_SMOKE`, AC-121.8) passes on a fresh onedir with the preselected variant, and the spike's findings are recorded (AC-121.9).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-07). A headroom binary is on PATH but no payload here is oversized: the scope is a named list of adapter, main-process, renderer, smoke-tool and test files, read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s52-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s52\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s52-plan-2026-11-06-tts-load-fp16` and `s52-execution-2026-11-06-tts-load-fp16`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator warns before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290).
  - Reviewer prompts name the ledger vocabulary up front, forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json` and any `.env`, and, when they ask for `tested_state`, name `~/.config/git/ignore` and the paths it hides (`.claude/settings.local.json`; Session 51 RULE-4).
- **Never in these rows without Mat's words:** commit, push, a real model, voice, runtime or Python package download, a YouTube request of any kind, or an `approved` verdict authored by the implementer. Mat's E5 yes (D-333, 2026-11-07) lifts the package rule for E5's two hashed pins, `onnx==1.23.2` and `ml-dtypes==0.6.0`, fetched into the uv cache and installed into a Temp target in E5's step only.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-119 `svc-tts-load-keeps-model` | `.agent/context/handoffs/2026-11-06-tts-load-fp16-MEU-119-handoff.md` |
| MEU-120 `gui-models-dir-probe` | `.agent/context/handoffs/2026-11-06-tts-load-fp16-MEU-120-handoff.md` |
| MEU-121 `svc-tts-fp16-nonfinite` | `.agent/context/handoffs/2026-11-06-tts-load-fp16-MEU-121-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-06-tts-load-fp16-plan-critical-review.md` and `.agent/context/handoffs/2026-11-06-tts-load-fp16-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `models-before.json`, base suite, dev check and asset receipts |
| WP-2 | MEU-119 load order (rows 1, 2) and the Console home-folder scrub (rows 2a, 2b) | WP-1 | shared | `LOAD_CHECKS`, `LOAD_KEEPS`, `HOME_SCRUB`; the amended AC-75.9 test; the contract test; the TEMP-under-home receipt |
| WP-3 | MEU-120 models folder probe (rows 3 to 5) | WP-2 | shared | `MODELS_DEFAULT`, `DIR_PROBE`; settings E2E receipt |
| WP-4 | MEU-121 preselection (rows 6 to 8) | WP-3 | shared | `PRESELECT_ORDER`; renderer and E2E receipts |
| WP-5 | MEU-121 sentence smoke (rows 9, 10) | WP-4 | shared | `--phase sentences`, a fresh onedir, the Red and Green smoke receipts |
| WP-6 | MEU-121 FP16 spike (row 11), time-boxed | WP-5 | shared | `fp16-spike.py`, the spike receipts, the findings in the MEU-121 handoff |
| WP-7 | Records (row 12) | WP-6 | shared | Hub, MEU status, register, renders, grouping tracker |
| WP-8 | Closeout (H1, H2) | WP-7 | `compact_continue` | Handoffs, review, reflection |

**The split (brief: "Split flag yes").** Part A is WP-2 to WP-5: the load order, the probe, the preselection and the sentence smoke. It ships whatever the spike finds. Part B is WP-6. If the spike runs past its box (D-333) without a cause, `TTS-ONNX-FP16-NONFINITE-AUDIO` stays open with the findings in its `verification`, it gets no `--decision-issue` flag, and the FP16 outcome comes back to Mat as a brief. Nothing removes or disables FP16 (D-239).

## User Review Required

> [!IMPORTANT]
> **The listening verdict is asked at this gate (D-331).** Please listen to `C:/Temp/av-kit/tts-compare/listen-kokoro-onnx-int8.wav` (the FP32 alternative is `listen-kokoro-onnx-fp32.wav`) and say which one a fresh install preselects. Row 6's Red encodes that id, so without the verdict nothing in MEU-121 starts (S11). INT8 gives `PRESELECT_ORDER = ['kokoro-onnx-int8', 'kokoro-onnx-fp32']`. FP32 gives `['kokoro-onnx-fp32', 'kokoro-onnx-int8']`, and the smoke's Green then uses the pinned FP32 file (row 9).
> **Ruled 2026-11-07: INT8.** The ids in this plan are the INT8 ones, and S11 is met.
>
> **Two tests change their expectations, each from the residual sections, not for convenience.**
> - `test_ac_75_9_raising_probe_or_vocab_is_model_load_error_neg` (`tests/integration/test_tts_device_resolution.py:620`) loads A, fails the device probe and asserts nothing is loaded (`:643`). D-221 reverses that for a failed check, and the grouping's scoping review approved this one amendment (03 `:623`). After row 1 the test asserts A is still loaded on `cuda`. The `ModelLoadError`, cause, logging and path-redaction assertions stay, and the vocab half (`:645-657`) starts unloaded and doesn't change. The `load_model` docstring (`adapter.py:289-291`) changes with it.
> - The setup-readiness test "defaults models directory to app-data models" (`ui/tests/unit/setup-readiness.test.ts:30-32`) expects `{appData}/models`. D-222 sets the backend default, so after row 3 it expects `~/.avkit/models` expanded (AC-120.2).
>
> **The open test, `test_ac_75_9_engine_import_failure_is_model_load_error_neg` (`:739`), and its twin `test_ac_98_5_kokoro_import_logs` (`:855`) (D-324).** The new runtime check (D-322) reads `runtime_present`. Its default probe, `runtime_imports` (`adapter.py:103-121`), imports kokoro and returns `False` when the import fails. Both tests make the kokoro import fail and expect the in-load path's error: "PyTorch model failed to load" with the import error as cause in `:739`, and the cause and the `ImportError` log in `:855`. With the default probe they would now get the refusal before the unload. The plan takes A′; this gate, the plan review or Mat can change it.
> - **A′ (chosen):** `_adapter` (`:132`) gains an optional `runtime_probe` argument, and these two tests pass `lambda _fmt: True`. That is setup only: every assertion stays, and the two tests then pin the after-unload path (D-325), which a probe that said yes and an import that failed later still reach. AC-119.3 covers the absent runtime with a load already in place.
> - **A2:** amend both tests' assertions to the refusal. They would then duplicate AC-119.3, and nothing would pin the in-load import failure.
> - **B:** move the engine imports themselves before the unload. An import alone isn't load-before-unload (`runtime_imports` already imports `KModel` before it), but it repeats what the runtime check proves, and both tests would change their assertions to A kept, as in A2. Building B's model there would be load-before-unload, which D-221 refuses.
> - **Do nothing:** no runtime check in the adapter. The service already refuses the absent runtime with 422 first (MEU-117), so over HTTP the model is kept, but a direct caller of the port still loses A.
>
> **What the probe reports for a folder that doesn't exist yet (D-327).** The plan takes B; this gate can change it.
> - **B (chosen):** the probe walks up to the nearest existing ancestor. If that is a folder, it writes and deletes the same transient `.write-probe-<uuid>` file there that it already writes in an existing folder, and reports the result. If it is a file, the probe reports `false`. No folder is created; the backend creates the folder at its first download (`model_manager/assets.py:214`, `:308`, `:352`). For the default path on a fresh install the ancestor is the user's home folder, so a transient file appears there for an instant.
> - **A:** check the ancestor with `accessSync(W_OK)` only. It writes nothing, but on Windows that call doesn't read the folder's ACL, so it reports writable for nearly any existing folder.
> - **C:** report `false` until the folder exists. Every fresh install would then show the models row not ready until the first download.
> - **Do nothing:** keep creating `{appData}/models`. The probe keeps reporting on a folder the backend doesn't use.
>
> **The dev app and the Settings E2E now probe the real `~/.avkit/models` (D-327).** With no stored `tts.models_directory`, the probe reads the backend default, which on this host is the real models folder. It writes and deletes its transient probe file there, as it did in `{appData}/models` before. The models snapshot (§3) is file-level, so a leftover probe file is S4.
>
> **A log line that carries a path, raised here per Session 50's rule.** The missing-weight `tts.load_failed` line puts the cause's text in `detail` (`adapter.py:148-158`, AC-115.9), and that cause is `FileNotFoundError(<weight path>)` (`:173-175`). So the full weight path reaches the Console and `console.log` today. Row 2 moves that check but keeps its log line as it is. Say if the path should leave the line; that would be a change to AC-115.9's contract (D-247). The new raising-runtime-probe line logs only the cause's class (D-323).
> **Ruled 2026-11-07: the scrub (D-335).** The line and AC-115.9 stay as they are. Rows 2a and 2b replace the home folder with `~` in every Console field (`HOME_SCRUB`, §Home folder scrub), which covers this line and the five other events whose text can hold a home path.
>
> **Only FP16 downloaded keeps FP16 (D-330).** A user who downloaded only FP16 still gets FP16 preselected, because the first-downloaded rule stays and nothing disables FP16 (D-239). The alternative is to preselect INT8 even when it isn't downloaded, which shows a model that needs a download first.
> **Ruled 2026-11-07: keep.** The rule stands as written.
>
> **The sentence smoke runs in this session (D-332), and MEU-125 repeats it at the rc.2 gate.** Row 9 adds `--phase sentences` to `tools/smoke_packaged_tts.py`, builds a fresh onedir and runs FP16 as the Red. Row 10 runs the preselected variant as the Green: 149 jobs, offline, on copies of the cached models outside the checkout and outside `~/.avkit/models`.
>
> **The FP16 spike is boxed at 2 hours (D-333).** It runs experiments E1 to E4 in row 11 from local files only. E5, which localizes the first non-finite node, needs the `onnx` package, which isn't installed and isn't in the uv cache. Installing it is a network fetch, so E5 runs only if you say yes here. No fix is built inside the box. A cause that points at a fix comes back to you as a plan amendment, re-reviewed before any code changes.
> **Ruled 2026-11-07: E5 yes.** `onnx==1.23.2`, with `ml-dtypes==0.6.0`, the one dependency the venv lacks, enters the uv cache in E5's step only, installed with `--no-deps --require-hashes` into a Temp target, and row 11 runs `fp16-spike.py all --e5` (§FP16 spike, E5's fetch).
>
> **The token estimate,** calibrated against Session 42 `tts-sideload-load` (plan review 12.8M over 2 rounds, execution 4.1M over 1) and Session 51 (plan review 7.5M and execution 8.7M, one round each). This delta is three small MEUs: an adapter reorder, a main-process probe and a renderer rule, plus a new smoke phase and a spike outside the reviewed code. Expect 1 to 2 plan rounds (about 7M to 13M) and 1 to 2 execution rounds (about 6M to 12M). The harness budgets are 10.5M for the plan review and 21M for the execution review, so a second plan round that runs past 10.5M needs Mat's grant.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `LOAD_CHECKS` | `load_model` runs, in this order, the weight check, the device probe, the format check and the runtime check, all before `unload_model`. |
| `LOAD_KEEPS` | A load that fails one of `LOAD_CHECKS` leaves the adapter's fields as they were, so the status still shows the loaded variant on its device. |
| `MODELS_DEFAULT` | `DEFAULT_MODELS_DIRECTORY` in `setup-readiness.ts` is `'~/.avkit/models'`, the backend's `tts.models_directory` default, and a contract test holds the two equal. |
| `DIR_PROBE` | `probeModelsDirWritable` never creates a folder. An existing folder gets the write-and-delete probe; a missing one gets it in its nearest existing ancestor folder; a file on the way reads `false`. |
| `PRESELECT_ORDER` | The ids `defaultModelSelection` ranks first when it falls back: `['kokoro-onnx-int8', 'kokoro-onnx-fp32']` (or FP32 first, per the listening verdict), then the catalog order. |
| `SENTENCE_SMOKE` | `--phase sentences` of the packaged smoke: one variant, offline, the 40 sentences (three voices), the first 20 with a fourth voice, the 8 paragraphs and the 96-word passage, 149 jobs, each `Done` with audio. |
| `FP16_SPIKE` | The time-boxed hunt for the FP16 cause in row 11, run from local files only, recorded whatever it finds. |
| `HOME_SCRUB` | `console_field` replaces the home folder with `~` where it starts a path, before the URL, redaction and length rules, so no Console field reaches stdout, the Console ring or `console.log` with the user's home folder in it (D-335). |

### Load order (MEU-119, D-322, D-323)

`load_model` becomes:

1. `_require_weight_path(variant)`. A failure logs on `cpu`, as today, and re-raises.
2. `self._resolve(variant, device)`. A raising probe logs on `cpu` and raises "TTS device probe failed" with the cause, as today.
3. The format check. A format that is neither PyTorch nor ONNX raises the `ValidationError`, logged on the target, as today (`:317-320`), now before the unload.
4. The runtime check, `self.runtime_present(variant.format)`. `False` raises `ModelLoadError(MODEL_REASONS[variant.format])`, logged on the target with no cause, which is what `_load_pytorch` already says for torch absent (`test_ac_98_5_torch_absent_logs`, `:838`, holds). A probe that raises is caught: the adapter logs one `tts.load_failed` with the cause's class and no `detail`, and raises `ModelLoadError("TTS runtime probe failed")` from it (D-323).
5. `self.unload_model()`.
6. Build the model or session in locals, then assign the fields, as today.

**The runtime check reads MEU-117's capability source.** `runtime_present` is the adapter's memo of `runtime_imports` (`:274-284`), the same one `ModelService.availability` reads before it calls the port (`services/models.py:163`). Through the API the service has already probed the format, so the adapter's check reads the memo and probes nothing new. A direct caller probes once, and the memo holds the answer for the service. MEU-117's 422 stays: the service still refuses first and never calls the port (AC-117.8, unchanged).

**The limit (D-221, D-325).** The checks can't see everything. A failure after the unload still leaves nothing loaded on `cpu`. That covers a kokoro import inside `_load_pytorch` (`:347`), the `KModel` constructor (`:360`), the `.to` move and `eval`, and the ONNX CPU session (`:396`). Building B before dropping A is load-before-unload, which D-221 refuses. The docstring (`:289-291`) says this.

### Home folder scrub (MEU-119, D-335)

`packages/core/src/avkit_core/services/health.py` gains three names, and `console_field` (`:93-96`) changes by one call:

- `home_folder()` returns `str(Path.home())`, or `""` when `Path.home()` raises `RuntimeError`. It is the one function the tests patch.
- `HOME_IGNORES_CASE = sys.platform == "win32"`, read at call time, so a test can set it either way.
- `scrub_home(text)` strips trailing separators from the home folder. It returns `text` unchanged when the result is empty or holds no separator, because a bare drive such as `C:` would otherwise turn every `C:\` into `~\`. Otherwise it splits the home folder on `\` and `/` and matches its parts joined by `\`, `/` or a doubled `\\` (an `OSError`'s text quotes its path with doubled backslashes). A match must not follow a word character, a separator, `.`, `~` or `-`, and must be followed by a separator, a quote or the end of the text, so `C:\Users\ana` doesn't match inside `C:\Users\anabel` and `/home/ana` doesn't match inside `/srv/home/ana`. Case is ignored while `HOME_IGNORES_CASE` is true. Each match becomes `~`, and the rest of the path keeps its separators.
- `console_field` becomes `redact_message(replace_links(scrub_home(single)))[:FIELD_LIMIT]`. The scrub runs first, so the 300-character cut can't leave part of a user name that the scrub would no longer recognise. A `file://` URL still becomes `[link]`.

What a line keeps: the missing-weight `detail` reads `~\.avkit\models\kokoro-v1.0-onnx\onnx\model_quantized.onnx`, which still says which file is missing and where the app looked. AC-115.9's contract stands: `detail` is still the cause's first line, single-line, redacted and cut.

What doesn't change: the six log sites, `REDACT_NEEDLES`, the event names (each is a constant), and logging in Electron main and the MCP server. Fields outside `CONSOLE_FIELDS` and tracebacks are already dropped. Nothing reads a path back out of Console text: the renderer's `useBackendLogs.ts` and `ConsolePanel.tsx` display the message, and the MCP server doesn't read the Console (`C:/Temp/av-kit/s52-d335-consumers.txt`).

**The TEMP-under-home run.** CI runs the suite on `windows-latest`, where pytest resolves `tmp_path` to the long form under the runner's home folder (pytest 9.2.0 `_pytest/tmpdir.py:202` calls `resolve()` on the temp root, which expands an 8.3 `TEMP`). There, a Console message that held a raw `tmp_path` would now show `~`. A search of the 11 test files that read Console output finds no message assertion that holds a path (`C:/Temp/av-kit/s52-d335-path-asserts.txt`). Row 2b proves it by running the 10 test files among them once with `TMP` and `TEMP` under the home folder (`$env:LOCALAPPDATA\Temp\avkit-s52-home-tmp`, created and removed by the row). The 11th, `tests/e2e/api_fakes.py`, is a helper that the e2e files import. They don't include the closeout selftest that `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` concerns. A failure there is an expectation change, which is S14.

### Models folder probe (MEU-120, D-326, D-327, D-328)

- `export const DEFAULT_MODELS_DIRECTORY = '~/.avkit/models'`. `defaultModelsDirectory()` takes no argument and returns `expandUserPath(DEFAULT_MODELS_DIRECTORY)`. `readTtsModelsDirectory` uses it at both fallbacks (`:62`, `:79`). A stored value still wins, as today.
- `probeModelsDirWritable` loses `mkdirSync` (`:90`, and the import at `:6`). For a missing path it walks `dirname` up to the nearest existing entry. A folder gets the transient probe file, deleted at once; a file reads `false`; a walk that reaches the root with nothing found reads `false`. An existing folder keeps today's probe (`:93-101`).
- The contract test (AC-120.1) reads `packages/core/src/avkit_core/services/settings.py` from Vitest and matches `("tts", "models_directory"): SettingSpec("string", "<default>")` against `DEFAULT_MODELS_DIRECTORY`.
- `index.ts` and `ipc.ts` don't change: `probeSetupReadiness` keeps its signature, and nothing else calls `defaultModelsDirectory` (`grep`, 2026-11-07).

### Preselection (MEU-121, D-329, D-330)

- `export const PRESELECT_ORDER = ['kokoro-onnx-int8', 'kokoro-onnx-fp32'] as const` in `tts-controls.ts`.
- `defaultModelSelection` keeps its first two rules (the chosen row while runnable, the loaded row). The fallback ranks the runnable rows by their place in `PRESELECT_ORDER`, with every other row after them in catalog order (a stable sort), and returns the first downloaded row of that list, else its first row. MEU-117's skip of unavailable rows (D-320) stays.
- `engine.py` stays in scope as a read-only source (D-329). AC-121.1 reads `SEED_VARIANTS` from it and builds the fresh catalog a new install gets, sorted by id as `list_catalog` returns it (`repositories.py:355`). The test then holds the preselection to what a fresh install sees, not to a hand-written list.

| Catalog state (CPU build, PyTorch unavailable) | Today | After row 7 |
|---|---|---|
| Nothing downloaded or loaded (fresh install) | `kokoro-onnx-fp16` | `kokoro-onnx-int8` |
| FP16 and FP32 downloaded | `kokoro-onnx-fp16` | `kokoro-onnx-fp32` |
| Every ONNX row downloaded | `kokoro-onnx-fp16` | `kokoro-onnx-int8` |
| Only FP16 downloaded | `kokoro-onnx-fp16` | `kokoro-onnx-fp16` (D-330) |
| INT8 served unavailable, nothing downloaded | `kokoro-onnx-fp16` | `kokoro-onnx-fp32` |

AC-117.13 (`ui/tests/unit/tts-model-selection.test.ts`), AC-117.14 (`ui/tests/e2e/tts-generate.test.ts:891-922`) and AC-63.x (`tts-page.behavior.test.ts`) hold unchanged under this rule (traced 2026-11-07: AC-117.14's catalog has INT8 not downloaded and FP32 downloaded, so it still expects FP32).

### Sentence smoke (MEU-121, D-332)

`tools/smoke_packaged_tts.py` gains `--phase sentences` with `--test-set <json>` and `--variant <id>`. `_register_variant` (`:304`) takes the variant id as a keyword argument. `_generate` (`:314-344`) takes the variant id, the text and the voice, plus `load`, which says whether it loads the model first. Each defaults to today's value, so `phase_offline` doesn't change. The scripts that import from the tool don't use either function: `dev-pytorch-check.py` has its own `_generate`, and `smoke_packaged_rc.py` imports only `Backend` (`grep`, 2026-11-07). The module docstring gains a `--phase sentences` paragraph.

The phase:

- refuses a `--backend-dir` inside the repository and a `--models-dir` inside the repository or equal to `~/.avkit/models`, like `phase_capability` (`:533`);
- starts the copied backend behind the dead proxies (`_offline_env`, `:284`) with fresh app data under the run folder, and sets `tts.models_directory` to `--models-dir`;
- registers `--variant` through the download fast path (`_download_target`, `:184`); with the proxies dead, any real fetch fails, so nothing downloads (S5);
- loads `--variant` on `cpu` once and runs the test set's 149 jobs one at a time: each of the 40 sentences with `af_heart`, `am_michael` and `af_bella`, the first 20 with `bf_emma`, the 8 paragraphs and the passage with `af_heart`, at speed 1.0 and `WAV`. Each job sends `enabled_steps: []`, as `_generate` does today, so the text reaches the model as written, the way the 2026-11-04 probes fed it. The page's default steps rewrite numbers and symbols, which would change the test set;
- passes only when every job ends `Done` with more than 0 samples in a WAV inside the run folder. The JSON lists each failure's kind, index, voice and `error_message`, and holds `variant_id` and `jobs`, the number of jobs run.

Inputs: a fresh onedir copied to `C:/Temp/av-kit/s52/backend/avkit-backend`, and `C:/Temp/av-kit/s52/smoke-models`, a copy of Session 32's `C:/Temp/av-kit/s32-smoke-models` (vocab, spaCy, the four voices and `model_quantized.onnx`, whose SHA-256 row 0 checks against the pinned file). For the Red, row 9 also copies the real `model_fp16.onnx` into it, read only from `~/.avkit/models`. If the listening verdict is FP32, row 9 copies the pinned `C:/Temp/av-kit/tts-compare/pinned/onnx/model.onnx` there as well.

### FP16 spike (MEU-121, D-333)

`fp16-spike.py` (plan-local) builds on `fp16-test-set/fp16_nan_probe.py` and `fp16_rate_probe.py`. Its `phonemize` step runs once in the dev environment. It activates the spaCy copy in `C:/Temp/av-kit/s52/smoke-models` and phonemizes the 40 sentences with `KokoroG2p(EspeakCliAdapter())`, as the rate probe did: lang `a`, and lang `b` for the first 20. It writes the result to `C:/Temp/av-kit/s52-spike-phonemes.json`. `fp16-test-set/phonemes.json` holds only the passage's 6 sentences, so it isn't enough.

Each experiment then reads that file and runs ORT directly on the FP16 copy in `C:/Temp/av-kit/s52/smoke-models`, as the nan probe does: vocab ids, the voice pack's style row for the token count, and speed. It covers the rate probe's 140 (sentence, voice) pairs, and writes one JSON per experiment to `C:/Temp/av-kit/s52-spike-<id>.json`. Each JSON holds the onnxruntime version, the session options, the non-finite sample count for each pair, and the start and end times. The paragraphs aren't run: FP16 passed all 8 on 2026-11-04 (`fp16-rate-probe.txt:32`), and the spike looks for what makes the 11 failing pairs fail (`:29-34`).

| Id | Experiment | What it would show |
|---|---|---|
| E0 | Default session, ORT 1.31.1 (the control) | The rate probe's 11 failing pairs reproduce on the copy; if they don't, the spike stops and records that |
| E1 | `graph_optimization_level` at `ORT_DISABLE_ALL`, `ORT_ENABLE_BASIC`, `ORT_ENABLE_EXTENDED` | A graph rewrite (a fusion) produces the overflow |
| E2 | ORT 1.24.4 and 1.29.0 from the uv cache (`uv run --offline --no-sync --with onnxruntime==<v>`); 1.20.1 is cached only for cp311 and isn't tried | A runtime regression |
| E3 | For the failing pairs: the style row (`ref_s` index ±1, ±2), speed 0.9 and 1.1, and the trailing punctuation token | Whether the trigger is the style vector or the token sequence |
| E4 | `intra_op_num_threads=1`, `enable_cpu_mem_arena=False` | A threading or arena effect |
| E5 | Mat's yes (D-333, 2026-11-07): each node's output added as a graph output with the `onnx` package, run on the failing pairs, to find the first node in graph order whose output holds NaN or Inf | Where in the graph it starts |

Each run first asserts `onnxruntime.__version__` is the one it asked for, so an E2 overlay that didn't take is recorded as not run. An experiment that can't resolve offline is recorded as not run, with its error. A **cause** means one change makes every test-set pair finite, and undoing it brings the failure back. The spike stops at whichever comes first: a cause, the end of the experiments, or the 2-hour box measured from the first spike JSON's start time (S13).

`fp16-spike.py all` runs the whole spike in row 11. It phonemizes, then runs E0 to E4 in order, each E2 version in its own `uv run --offline --no-sync --with onnxruntime==<v>` child. `--no-sync` keeps every overlay from syncing the project venv. It checks the box before each experiment. A setting that makes every pair finite is run again straight after E0's control, so the summary shows the failure coming back without it. The run writes `C:/Temp/av-kit/s52-spike-summary.json`, which holds:
- each experiment's status: `run`, `not_run` with its error, or `boxed`;
- the stop reason: `cause`, `done`, `box` or `control`;
- the candidate setting, if one was found.

It exits 0 whichever way the spike stops, and 1 only on its own error. `--e5` adds E5 after E4, and row 11 passes it (D-333 E5 yes).

**E5's fetch.** E5's step is the one step in this plan allowed to reach PyPI, and only for two wheels. The pins were picked at plan time from PyPI's release data (`C:/Temp/av-kit/s52-onnx-pin.txt`, `s52-ml-dtypes-pin.txt`). Each is the newest release with a cp312 Windows wheel uploaded at least two weeks before 2026-11-07: `onnx-1.23.2-cp312-abi3-win_amd64.whl` (2026-10-06, SHA-256 `9b382ba898a7c142a0801d03cf04ecabced96c1543c7b643a86f0928143802de`), and `ml_dtypes-0.6.0-cp312-cp312-win_amd64.whl` (2026-08-13, SHA-256 `2a3e9d53925597fbffafd2a37048dadeddd0bdaba58058f6ae0869ed709a184d`). `ml_dtypes>=0.5.4` is the one dependency of `onnx` 1.23.2 that the venv lacks. The venv already meets `numpy>=1.23.2` (2.5.4), `protobuf>=6.31.1` (7.36.2) and `typing_extensions>=4.7.1` (4.16.0) (`C:/Temp/av-kit/s52-onnx-deps.txt`). Neither package is in the uv cache today.

After the box check, E5's step runs two children in turn. The first writes `C:/Temp/av-kit/s52/e5-requirements.txt`, holding exactly `onnx==1.23.2 --hash=sha256:<onnx>` and `ml-dtypes==0.6.0 --hash=sha256:<ml_dtypes>` with the two SHA-256s above, and runs once:

`uv pip install --no-config --default-index https://pypi.org/simple --no-deps --require-hashes --only-binary :all: --python .venv/Scripts/python.exe --target C:/Temp/av-kit/s52/e5-site -r C:/Temp/av-kit/s52/e5-requirements.txt`

Each flag bounds the fetch:
- `--no-deps`: uv installs the two named requirements and resolves nothing else, so no third package is looked up or fetched;
- `--require-hashes`: uv refuses any file whose SHA-256 isn't one of the two recorded, so a different wheel or build fails the install;
- `--only-binary :all:`: no source download or build;
- `--target`: the install goes to a Temp folder, and the project venv, `pyproject.toml` and `uv.lock` aren't touched;
- `--no-config` and `--default-index`: no project or user setting changes the index.

A plan-time offline probe shows these flags hold (`C:/Temp/av-kit/s52-e5-bound-probe.txt`, uv 0.12.5, no fetch, uv cache inventory unchanged). The locked onnxruntime 1.31.1 wheel, with its four dependencies, stood in for a pin in a `--dry-run`, and with `--no-deps` uv planned exactly that one package. On a tiny local wheel that declares a dependency existing nowhere, installed for real with `--no-cache`:
- the right hash with `--no-deps` installed it and ignored the dependency;
- a wrong hash failed with "Hash mismatch" and installed nothing;
- without `--no-deps`, uv looked the dependency up and failed.

The wheels enter the uv cache, as D-333 E5 item 1 says. If `e5-site` already holds exactly the distributions `onnx-1.23.2.dist-info` and `ml_dtypes-0.6.0.dist-info`, as on a re-run, the install is skipped and recorded. Any other distribution there stops E5 as not run. uv's `.lock` file and any console scripts don't count. The second child runs E5 offline: `uv run --offline --no-sync python fp16-spike.py e5` with `PYTHONPATH=C:/Temp/av-kit/s52/e5-site`. It asserts that `onnx.__file__` and `ml_dtypes.__file__` are under `e5-site`, and that `numpy`, `protobuf` and `onnxruntime` load from the venv.

The E5 JSON records:
- the requirements file's text and the install's exit code and output;
- the child's `onnx.__version__`, `ml_dtypes.__version__` and `onnxruntime.__version__` (1.31.1), with each module's file;
- the distributions in `e5-site`, which must be exactly the two;
- the uv cache's package entries before the install and after the run child: the names under each `wheels-v*/<source>/` and `simple-v*/<source>/` folder of `uv cache dir`;
- `uv pip list` of the project venv, and the SHA-256s of `pyproject.toml` and `uv.lock`, before and after, which must match.

A new cache entry for any name other than `onnx` and `ml-dtypes`, a third distribution in `e5-site`, a changed venv, or a change to `pyproject.toml` or `uv.lock` is S5. The spike stops there, and E5's result is kept but marked. A failed install, such as a hash mismatch, no matching wheel or no network, records E5 as not run with its error. Nothing retries it with looser flags. E5 adds each node's output to a copy of the FP16 model in `C:/Temp/av-kit/s52/`, never to the copy the other experiments read. If E1 found a failure that needs a fusion, E5 runs at the level where it still reproduces, and records whether any level does.

### Spec text (D3)

| File | Lines | Change |
|---|---|---|
| `docs/build-plan/03-service-layer.md` | after `:625` | A "Delivered (Session 52)" note for MEU-119: `LOAD_CHECKS`, `LOAD_KEEPS`, the D-221 limit, D-324 and the amended test. It also says that the registered text cites the 2026-11-04 tree, and gives the `b6c3895` lines (`adapter.py:299`, `:289-291`; test `:620-643`, `:645-657`, `:738-756`). |
| `docs/build-plan/03-service-layer.md` | after `:641` | A "Delivered (Session 52)" note for MEU-121: `PRESELECT_ORDER`, the listening verdict, `SENTENCE_SMOKE` and the spike's result or Mat's outcome. It gives the `b6c3895` lines for `:631` (`adapter.py:179-192`, `tts-controls.ts:104-125`). |
| `docs/build-plan/06-gui.md` | after `:1572` | A "Delivered (Session 52)" note for MEU-120: `MODELS_DEFAULT`, `DIR_PROBE`, D-327's report for a missing folder, and that no files move. |

Row 12 re-reads each anchor before it writes (Session 51 RULE-3), and it cites the lines as they read after rows 2, 4 and 7. The registered text above each table is history and isn't rewritten.

### MEU-119 `svc-tts-load-keeps-model`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `KokoroAdapter.load_model(variant, device)` | `avkit_infra.tts.adapter` | Unchanged signature; raises `ModelLoadError` or `ValidationError` | No new parameter |
| `tts.load_failed` log event | `adapter._log_load_failed` | `variant_id`, `device`, `error`, optional `detail`; the raising runtime probe adds no `detail` (D-323) | No new field |
| `console_field(value)` and every Console line | `avkit_core.services.health` | Unchanged signature; the result is single-line, home folder as `~` (`HOME_SCRUB`), links as `[link]`, redacted, at most `FIELD_LIMIT` characters | `CONSOLE_FIELDS` unchanged |
| `POST /api/v1/models/load`, `GET /api/v1/models/status` | `avkit_api.routes.models` | Unchanged; `ModelLoadError` is 422 (`LOAD_ERROR_HTTP`) | Unchanged; the OpenAPI check is a guard (S6) |

#### Acceptance Criteria

Pytest names are `test_ac_119_<n>_…`. Each AC-119.1 to AC-119.5 test loads A (ONNX on `cuda`, `_load_cuda_first`), replaces `adapter.unload_model` with a spy, fails a load of B, and asserts the raised error, the status `(True, A.id, "cuda")`, zero spy calls, `engines.calls == []`, one `tts.load_failed`, and no path in the error (`_assert_no_path`).

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-119.1 | unit | B's weight file is missing: "model weight file is missing", A kept | Local Canon: triage D-221 | Yes: Red, today the status is unloaded |
| AC-119.2 | unit | The device probe raises on B: "TTS device probe failed" with the cause, A kept | Local Canon: triage D-221 | Yes: Red |
| AC-119.3 | unit | B is PyTorch and its runtime is absent (an injected probe says `False`): `MODEL_REASONS[PyTorch]`, logged on the target with `ModelLoadError`, A kept | Local Canon: triage D-221; MEU-117 `MODEL_REASONS` | Yes: Red, today B loads |
| AC-119.4 | unit | The runtime probe raises on B: "TTS runtime probe failed" with the cause; the log carries the cause's class and no `detail`; A kept | Local Canon: D-323; Session 50 raw-value rule | Yes: Red, today B loads |
| AC-119.5 | unit | B's format is neither PyTorch nor ONNX: the `ValidationError`, A kept | Local Canon: triage D-221 | Yes: Red |
| AC-119.6 | unit | On a fresh adapter, a load probes the format's runtime once through `runtime_present`, and a second load probes nothing more | Local Canon: brief ("reads MEU-117's capability source") | Yes: Red, today zero probe calls |
| AC-119.7 | unit | After the checks pass, a `KModel` constructor failure leaves nothing loaded on `cpu` | Local Canon: triage D-221; AC-75.4 | Guard: passes in Red |
| AC-119.8 | unit | After the checks pass, an ONNX CPU session failure leaves nothing loaded on `cpu` | Local Canon: triage D-221; AC-75.5 | Guard: passes in Red |
| AC-119.9 | contract | `tests/e2e/test_api_model_load_keeps.py`: a real `ModelService` over a real `KokoroAdapter` (fake `InferenceSession`, `FakeAssets`, models folder under `tmp_path`). `POST /models/load` INT8 answers 200. FP32, whose row holds a path whose file is gone, answers 422 "model weight file is missing". `GET /models/status` still shows INT8 on `cpu` | Local Canon: brief | Yes: Red, today the status is unloaded |
| AC-75.9 (amended) | unit | `test_ac_75_9_raising_probe_or_vocab_is_model_load_error_neg` asserts A is still loaded after the failed probe | Local Canon: triage D-221; grouping scoping review round 1 | Yes: Red |
| AC-119.10 | unit | `tests/unit/test_services.py`, with `home_folder` patched to a synthetic `C:\Users\SYNTHETIC_HOME_USER`: `console_field` turns the home folder into `~` with `\`, `/` and doubled `\\` separators, and with the home folder alone at the end; it ignores case while `HOME_IGNORES_CASE` is true and keeps case while it is false; it leaves a look-alike user folder (`…USER2\x`), a path outside the home folder and a path in the middle of another path unchanged; with a 290-character prefix the cut keeps no part of the user name; a bare drive or an empty home folder changes nothing. Through a real `HealthService` with `log_to_file` on, one `log.error` whose `detail` is `FileNotFoundError(<home>\.avkit\models\m.onnx)` and whose `error` is an `OSError` text with doubled backslashes reaches the ring, stdout and `console.log` with `~` and without the user name | Human-approved: D-335; Session 50 raw-value rule | Yes: Red, today the user name is kept |

Guards that run unchanged in row 2: `test_ac_75_9_engine_import_failure_is_model_load_error_neg` and `test_ac_98_5_kokoro_import_logs` with A′ setup (D-324), `test_ac_98_5_torch_absent_logs`, `test_ac_98_4_missing_weight_logs_load_failed`, `test_ac_98_5_unsupported_format_logs`, `test_ac_115_9_load_failed_carries_detail`, and AC-117.8 (`tests/e2e/test_api_model_capability.py`). Guards that run unchanged in row 2b: the AC-115.9 and AC-115.10 Console tests in `tests/unit/test_services.py` and `tests/unit/test_console_level.py`, and then all 10 Console-reading test files under the TEMP-under-home run.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Which checks run before the unload | Specified | 03 `:620` and the brief: weight, device, runtime; D-322 adds the format check, which has no side effects |
| Where the runtime check reads | Specified | Brief: MEU-117's capability source; `runtime_present` (D-322) |
| A raising runtime probe | Gap filled | D-323: `ModelLoadError` with the cause, class-only log |
| The conflicting import tests | Specified as open | 03 `:624`; D-324 A′, to review and Mat |
| A failure after the unload | Specified | 03 `:622`; D-325 |
| The home folder in a Console field | Human-ruled | D-335: the scrub in `console_field`; the log sites and AC-115.9 unchanged |

### MEU-120 `gui-models-dir-probe`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `SetupReadinessResult.modelsDirWritable` | `ui/src/main/setup-readiness.ts` | `boolean`; the meaning is D-327's | Unchanged type |
| `get-setup-readiness` IPC | `ui/src/main/ipc.ts:431` | No payload (`noPayloadSchema`) | Unchanged |
| `DEFAULT_MODELS_DIRECTORY` | `setup-readiness.ts` (new export) | `'~/.avkit/models'`, equal to `settings.py:67` (AC-120.1) | — |

#### Acceptance Criteria

Vitest titles begin `AC-120.<n>`. Each test works in its own `mkdtempSync` folder.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-120.1 | contract | `DEFAULT_MODELS_DIRECTORY` exists and equals the `tts.models_directory` default read from `settings.py` | Local Canon: triage D-222 ("Tied") | Yes: Red, the export is missing |
| AC-120.2 | unit (amended) | `defaultModelsDirectory()` is `join(homedir(), '.avkit', 'models')` | Local Canon: triage D-222 ("Default") | Yes: Red |
| AC-120.3 | unit | `readTtsModelsDirectory` with no database, and with a database that has no row, returns that default | Local Canon: triage D-222 | Yes: Red, today `{appData}/models` |
| AC-120.4 | unit | A missing folder two levels under a writable folder reads `true`; afterwards the intermediate folder doesn't exist and the writable folder is empty | Local Canon: triage D-222 ("No empty folder"); D-327 | Yes: Red, today the folder is created |
| AC-120.5 | unit | A missing folder under a regular file reads `false` and creates nothing | Local Canon: D-327 | Guard: passes in Red |
| AC-120.6 | unit | An existing folder reads `true` and holds no probe file afterwards | Local Canon: D-327 | Guard: passes in Red |

The Settings E2E (`ui/tests/e2e/settings.test.ts`, AC-58.12 readiness count and card) runs again in row 5 on the built app, with its temporary `AVKIT_APP_DATA`.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Which default the probe uses | Specified | 06 `:1568`: the backend default (D-326) |
| A missing folder | Specified as open | Brief: "the plan says what it reports"; D-327 |
| Moving files from `{appData}/models` | Specified | 06 `:1570`: none |
| Where the two defaults are tied | Gap filled | D-328: Vitest reads `settings.py` |
| The RC1 checklist | Specified | 06 `:1572`: MEU-125 |

### MEU-121 `svc-tts-fp16-nonfinite`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `defaultModelSelection(input)` | `tts-controls.ts` | Unchanged signature; returns an id or `null` | — |
| `PRESELECT_ORDER` | `tts-controls.ts` (new export) | Two seeded ONNX ids (AC-121.2) | — |
| `smoke_packaged_tts.py --phase sentences` | `tools/smoke_packaged_tts.py` | `--test-set`, `--variant`, `--backend-dir`, `--models-dir`, `--out`; JSON `phase`, `variant_id`, `jobs`, `failures`, `passed` | The other phases unchanged |
| `fp16-test-set/test-set.json` | This plan folder | 40 sentences, 8 paragraphs, the 96-word passage, the voices; read-only | — |

#### Acceptance Criteria

Vitest and Playwright titles begin `AC-121.<n>`. The ids below are for the INT8 verdict; an FP32 verdict swaps INT8 and FP32 in AC-121.1 to AC-121.4 and AC-121.6 before row 6 (D-331).

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-121.1 | unit | The fresh catalog from `engine.py`'s `SEED_VARIANTS`, sorted by id, nothing downloaded or loaded, PyTorch unavailable: the selection is `kokoro-onnx-int8` | Human-approved: triage D-239 | Yes: Red, today FP16 |
| AC-121.2 | unit | `PRESELECT_ORDER` exists, is `['kokoro-onnx-int8', 'kokoro-onnx-fp32']`, and each id is a seeded variant | Human-approved: D-239; Local Canon: D-330 | Yes: Red, the export is missing |
| AC-121.3 | unit | Several rows downloaded: FP16 and FP32 give FP32; every ONNX row gives INT8; only FP16 gives FP16 | Local Canon: D-330 | Yes: Red for the first two |
| AC-121.4 | unit | INT8 served unavailable and nothing downloaded: FP32 | Local Canon: D-320, D-330 | Yes: Red, today FP16 |
| AC-121.5 | unit | The chosen and loaded rules and MEU-117's skip are unchanged: the AC-117.13 tests pass unchanged | Local Canon: D-320 | Guard |
| AC-121.6 | E2E | On the built app with nothing downloaded or loaded, the TTS page's model select shows `kokoro-onnx-int8` | Human-approved: D-239 | No Red: its negative is AC-121.1 |
| AC-121.7 | packaged | `SENTENCE_SMOKE` on FP16 exits 1, with at least one "generated audio must be finite" failure and no other kind of failure | Human-approved: D-239 ("fixed test set") | Is the Red of AC-121.8 |
| AC-121.8 | packaged | `SENTENCE_SMOKE` on `PRESELECT_ORDER[0]` passes all 149 jobs on a fresh onedir | Human-approved: D-239 ("Done") | Yes: AC-121.7 |
| AC-121.9 | record | The spike's experiments and results, and the cause or Mat's outcome, are in the MEU-121 handoff and the issue's `verification` | Human-approved: D-239 | — |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| INT8 first, FP32 the alternative | Specified | 03 `:635`; the listening verdict at this gate (D-331) |
| Only FP16 downloaded | Gap filled | D-330 |
| Where the packaged check runs | Specified as open | Brief; D-332: here, and again at MEU-125's rc.2 gate |
| The time box | Specified as open | Brief: "the plan sets the time box"; D-333 |
| What happens to FP16 if no cause is found | Specified | 03 `:639`: Mat's ruling; nothing removes or disables it |
| `engine.py` | Specified as open | Brief: keep with a reason or drop; D-329 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modify | `LOAD_CHECKS` order, the runtime check (D-322, D-323), the docstring (D-325) |
| `tests/integration/test_tts_device_resolution.py` | modify | The amended AC-75.9 test; `_adapter`'s `runtime_probe` argument and A′ setup in `:739` and `:855` (D-324); an additive AC-119.1 to AC-119.8 section at the end |
| `tests/e2e/test_api_model_load_keeps.py` | new | AC-119.9 |
| `packages/core/src/avkit_core/services/health.py` | modify | `home_folder`, `HOME_IGNORES_CASE`, `scrub_home`, and the scrub in `console_field` (D-335) |
| `tests/unit/test_services.py` | modify | An additive AC-119.10 section at the end |
| `ui/src/main/setup-readiness.ts` | modify | `DEFAULT_MODELS_DIRECTORY`, `defaultModelsDirectory()`, `DIR_PROBE` |
| `ui/tests/unit/setup-readiness.test.ts` | modify | The amended default test (AC-120.2) and AC-120.1, .3 to .6 |
| `ui/src/renderer/src/features/tts/tts-controls.ts` | modify | `PRESELECT_ORDER` and the fallback rank; the docstring |
| `ui/tests/unit/tts-model-selection.test.ts` | modify | AC-121.1 to AC-121.5, appended |
| `ui/tests/e2e/tts-generate.test.ts` | modify | AC-121.6, appended |
| `tools/smoke_packaged_tts.py` | modify | `--phase sentences`, `--test-set`, `--variant`; keyword arguments on `_register_variant` and `_generate`; the docstring |
| `docs/build-plan/03-service-layer.md` | modify | Two Delivered notes (D3) |
| `docs/build-plan/06-gui.md` | modify | One Delivered note (D3) |

No row edits `ui/tests/e2e/test-ids.ts` (AC-51.6, AC-81.13), and the E2E test uses the existing `model-select` id. `packages/api/` doesn't change, so `openapi.committed.json` doesn't either (S6). `packages/infrastructure/src/avkit_infra/database/engine.py` is read, not edited (D-329). Most of these files are CRLF in the working tree. Each row measures the line endings with Python bytes first and writes with `newline=""`, so the endings don't change. New files in this plan folder are LF.

### Project files

The registers and renders that row 12 writes: `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`, `.agent/context/known-issues.yaml` with its render, `.agent/context/triage-output.yaml`, and the grouping file's §6 row 52 (`:242`, CRLF). The closeout files: the three handoffs, the two rolling reviews, the reflection, `docs/execution/metrics.md` and `.agent/context/current-focus.md`. And this plan folder.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Removing, hiding or disabling the FP16 variant | Mat's ruling | — | D-239: "Nothing removes or disables it" (03 `:639`) |
| A code fix for FP16 found by the spike | Needs an amendment | — | D-333: a cause comes back to Mat as an amendment, re-reviewed before code changes |
| Building B before dropping A | Refused | — | D-221: no load-before-unload (03 `:620`) |
| Moving files out of `{appData}/models` | Refused | — | D-222 "No move" (06 `:1570`) |
| The RC1 checklist path | Other MEU | MEU-125 | 06 `:1572` |
| Editing the six log sites, `REDACT_NEEDLES` or AC-115.9's assertions; logging in Electron main or the MCP server | Mat's ruling | — | D-335: the scrub in `console_field` covers the field, and AC-115.9 (D-247) keeps it |
| An 8.3 short form of the home folder (`C:\Users\RUNNER~1`) | Raised with Mat | — | `HOME_SCRUB` matches the long form `Path.home()` gives. The default models folder, the Electron app-data folders, temp files made beside their destination (`filesystem/writer.py:31`) and pytest's temp root are long forms, and no Console field is built from `TEMP` (`C:/Temp/av-kit/s52-d335-tempsources.txt`). A stored `tts.models_directory` keeps the spelling it was saved with: settings store the string as given (`services/settings.py:141-145`), `models_directory` only calls `expanduser` (`services/models.py:54-56`), and sideload keeps the path (`model_manager/manager.py:97-113`). A short form saved there reaches a missing-weight `detail` (`tts/adapter.py:148-158`, `:167-175`) unscrubbed |
| Repeating Session 51's capability smoke | Other MEU | MEU-125 | The service refuses before the adapter, so MEU-119 doesn't reach it; AC-117.8 runs in `py-tests`; MEU-125's rc.2 gate repeats it |
| An installer build | Other MEU | MEU-125 | The onedir is enough for `SENTENCE_SMOKE` (D-332) |

## BUILD_PLAN.md Audit

Row 12 adds Delivered notes to the residual sections in `03-service-layer.md` and `06-gui.md`. It sets MEU-119, MEU-120 and MEU-121 to `ready_for_review` with this `execution_plan` through `tools/meu_status.py`, then renders `docs/BUILD_PLAN.md`. The check:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s52-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s52-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`.
2. Runs `models-snapshot.py --record`, which writes `models-before.json`. A re-run compares instead.
3. Runs `uv sync --frozen --all-packages` and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason: the avkit MCP servers in use run from those trees. It then captures the base Python suite to `s52-base-py.txt`, the base UI suite to `s52-base-ui.txt` and the base MCP suite to `s52-base-mcp.txt`, with `TMP` and `TEMP` at `C:\Temp\av-kit\s52\tmp`.
4. Runs Session 51's `DEV_CHECK` unchanged (`docs/execution/plans/2026-11-06-tts-build-capability/dev-pytorch-check.py`, strict mode) to `s52-base-dev.txt`. A failure is S9.
5. Checks the smoke and spike inputs to `s52-base-assets.txt`. `s32-smoke-models` must hold `config.json`, `spacy/`, the four voices and `model_quantized.onnx`, and that file's SHA-256 must equal the pinned `tts-compare/pinned/onnx/model_quantized.onnx`. The real `~/.avkit/models/kokoro-v1.0-onnx/onnx/model_fp16.onnx` must be 163,234,740 bytes with SHA-256 prefix `ba4527a874b42b21`. The pinned `model.onnx` must have prefix `8fbea51ea711f2af`. A mismatch is S10.
6. Runs `red-check.py --selftest`, `identity.py --selftest` and `models-snapshot.py --selftest`.

`red-check.py`, `identity.py` and `models-snapshot.py` are copies of Session 51's, with this plan's values:

- **`red-check.py`.** `DECLARED_NEW` holds this plan's new names, `DEFAULT_MODELS_DIRECTORY`, `PRESELECT_ORDER`, `home_folder`, `scrub_home` and `HOME_IGNORES_CASE`, and keeps the selftest fixtures' names. Session 51's names leave it.
- **`identity.py`.** `PLAN` is this folder, and `NAMED_DISTRIBUTIONS` stays empty: no Python dependency changes.
- **`PROJECT_ARTIFACTS`.** It holds this plan's `*.md`, the three handoffs, the review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`, which are written after the gate. The registers and renders stay bound, because row 12 writes them before H1-2. So do `fp16-spike.py` and `fp16-test-set/`.
- **`models-snapshot.py`.** Unchanged apart from its docstring's session line.

### 2. Red then Green (rows 1 to 10)

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error, and it refuses a required test that fails on a missing name. So a required test first asserts that the new name exists: `import * as readiness` with `expect(readiness).toHaveProperty('DEFAULT_MODELS_DIRECTORY')`, and the same for `PRESELECT_ORDER` on `tts-controls`. AC-120.2 asserts it too, because `defaultModelsDirectory()` with no argument throws a `TypeError` in `path.join` today, which `red-check.py` counts as unattributed. Row 1's Python Red needs no new name, since `runtime_probe` exists since Session 51. Row 2a's does: AC-119.10 first asserts that `health` has `home_folder` and `scrub_home`, so it fails by assertion and never on an `AttributeError` from `monkeypatch`. A raised-error test that doesn't raise yet fails with `Failed: DID NOT RAISE`, which `red-check.py` counts as an assertion (`PYTEST_ASSERTION`).
- **`--require` matches a failure title up to a non-digit boundary (`AC-100.7` never matches `AC-100.70`), so the amended tests are required by their full names.** These are `test_ac_75_9_raising_probe_or_vocab_is_model_load_error_neg` and the Vitest title `AC-120.2 the default models folder is the backend's`.
- **One runner summary per receipt.**
- **Guards pass in Red by design.** These are AC-119.7, AC-119.8, AC-120.5, AC-120.6 and AC-121.5, the A′ tests `:739` and `:855`, and the part of AC-121.3 that keeps FP16. No Red row requires them.
- **AC-121.6 has no Red of its own.** It is an E2E check after Green (row 8), and its negative is AC-121.1 (row 6).
- **The smoke's Red is its own kind (row 9).** `SENTENCE_SMOKE` isn't a test runner, so `red-check.py` doesn't read it. Row 9 checks its JSON directly: exit 1, `variant_id` FP16, at least one failure, and every failure's `error_message` is "generated audio must be finite" (any other message is S2).
- **Expectations stay immutable in Green.** The two amended tests change in their Red rows (1 and 3), each with the §User Review Required basis. The A′ change is setup in row 1.
- **Session 51 RULE-1 has no target here.** The new unit tests call pure functions and the readiness producers, with no query to wait for. AC-121.6 waits through Playwright's `toHaveValue`.
- **No real download.** Every Python test uses fakes or a monkeypatched session. The smoke runs offline on copies. The spike reads copies and the uv cache with `--offline`, except E5's install of its two hashed pins with `--no-deps --require-hashes` (D-333 E5 yes). Any other step that would fetch a model, a voice, a runtime or a package is S5.
- **Raw values (Session 50).** No new line logs an exception's text: AC-119.4 holds the new log line to the class. The home folder in a Console field, which reaches stdout, the Console ring and `console.log` today, is fixed in rows 2a and 2b (D-335, AC-119.10).

### 3. The real models folder stays untouched

`models-snapshot.py --compare models-before.json` exits 1 if any file under `~/.avkit/models` was added, removed, resized or rewritten. It runs at the end of rows 2, 5, 8, 9, 10 and 11, and in the session gate (`models-untouched`). Three things read that folder. `DEV_CHECK`'s fast path writes nothing. Row 9 copies `model_fp16.onnx` out of it. The settings and TTS E2E specs run the probe, whose transient file must be gone (S4).

### Plan-local scripts

Written with their rows and kept in this plan folder:

- `baseline.ps1`, `red-check.py`, `identity.py`, `models-snapshot.py` (row 0)
- `fp16-spike.py` (row 11)
- `issue-resolve.py` (row 12). It is Session 51's, taking `--issue` once per issue, with the exclusive handle, `--expect-sha256`, the staged save and the `--set-file` refusal of any other key. A named issue's set may hold a subset of `RESOLVE_KEYS`, so the FP16 issue can take `verification` alone (D-333).
- `session-gate.ps1` (H1-2)

### Session gate (H1-2)

`session-gate.ps1` is Session 51's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s52-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`; `ui/tests/e2e/test-ids.ts` refused), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `openapi` (a guard: no drift), `mcp-types`, `mcp-tests`, `mcp-build`, `state-render`, `issues-render` |
| Runtime | `ui-electron` targeted to the `settings` and `tts-generate` specs; `package-build` (`tools/package_backend.py`); `smoke-sentences` on `PRESELECT_ORDER[0]` on a fresh copy outside the checkout; `dev-pytorch`; `models-untouched` |
| Skipped, with reason | `mcp-audit`: live network and YouTube. `build-record`: no installer build. `smoke-capability`: §Out of Scope. |

`py-tests`, `ui-tests` and `mcp-tests` excuse only ids that row 0's receipts show failing, as Session 51 did.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py`, or row 9's smoke Red check | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`, or a path outside `baseline-dirty.txt` and this plan appears | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S4 | `models-snapshot.py --compare` reports a change to the real models folder | Stop; find what wrote it before anything else runs |
| S5 | Any step would make a real model, voice, runtime or package download, or any YouTube request. The one exception is E5's install of `onnx==1.23.2` and `ml-dtypes==0.6.0` with `--no-deps --require-hashes` (D-333 E5 yes); anything else E5's checks find is S5 | Stop before it runs; bring it to Mat |
| S6 | `openapi` drifts at all | Stop; `packages/api/` isn't in scope, so report the diff to Mat |
| S7 | Codex is unavailable or the ledger refuses | Mat |
| S8 | The packaged build fails, or it holds a `FORBIDDEN_DIRS` entry | Stop; report the build receipt to Mat |
| S9 | `DEV_CHECK` fails at row 0 | Stop; the dev path is broken before any change, so bring it to Mat |
| S10 | A row 0 asset check fails | Stop; the smoke's or the spike's inputs aren't the files the brief names, so bring it to Mat |
| S11 | Row 6 is reached without Mat's listening verdict | Stop MEU-121 and ask Mat; rows 0 to 5 may already be done |
| S12 | `SENTENCE_SMOKE` fails on `PRESELECT_ORDER[0]` (row 10 or the gate) | Stop; the preselected model doesn't meet Done, so bring the failures to Mat |
| S13 | The spike reaches its 2-hour box without a cause | Stop the spike; record the findings; send Mat the FP16-outcome brief (D-333); continue to row 12 with Part A |
| S14 | Row 2b's TEMP-under-home run fails a test, or any existing test's expectation would have to change for `HOME_SCRUB` | Stop; D-335 doesn't change AC-115.9's or any other test's assertions, so bring the failure to Mat |

## Decision Log

> [!WARNING]
> Mat's brief and triage D-221, D-222 and D-239 settle the scope. D-324 and D-327 list their options in §User Review Required, a do-nothing option among them, and D-333's FP16-outcome brief is written only if S13 is reached. The four gate questions, D-331, D-335, D-333 E5 and D-330, have Decision Briefs in `human-gate-decision.md`, each with its options, a do-nothing option among them, and Mat's 2026-11-07 ruling.
>
> Carried from the grouping and not relisted in the block, because the grouping's rows hold them: every §8 row, D-240 to D-250, D-267, D-277 and D-280, with stage `grouping`. Of those, D-245 makes TTS two sessions, and Session 52 carries it (`:287`). The closeout check reads all of them, and D-246 stays as a withdrawn row.
>
> The triage decisions are in `.agent/context/known-issues.yaml`: D-221 under `TTS-FAILED-LOAD-DROPS-MODEL`, D-222 and D-216 (human) under `MODELS-DIR-DOCS-AND-PROBE-MISMATCH`, and D-239 under `TTS-ONNX-FP16-NONFINITE-AUDIO`. The probe (`C:/Temp/av-kit/s52-decision-issue-probe.txt`) confirms that the MODELS-DIR flag pulls D-216 in beside D-222. H2-2 passes `--decision-issue` for the two issues this session closes, and for the FP16 issue only if it closes (D-333).

```yaml
decision_log:
  - id: D-322
    stage: planning
    question: "In what order does load_model check, and where does its runtime check read?"
    resolution: autonomous
    class: two-way
    chosen: "Weight, device probe, format, then runtime through self.runtime_present (MEU-117's memo), all before unload_model; then build and assign as today"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:620 — the checks run before unload_model, no load-before-unload", "packages/core/src/avkit_core/services/models.py:163 — the service reads the same availability before it calls the port", "packages/infrastructure/src/avkit_infra/tts/adapter.py:274-284 — runtime_present probes at most once per format"]
    research: { engine: none, sources: [] }
    reasoning: "The format check has no side effects, so it moves up with the others and AC-119.5 keeps A on an unsupported format. Reading runtime_present adds no second probe: through the API the service has already filled the memo. Doing nothing keeps the unload first, and any failed check drops A."
  - id: D-323
    stage: planning
    question: "What does load_model do when the runtime probe raises?"
    resolution: autonomous
    class: two-way
    chosen: "Raise ModelLoadError('TTS runtime probe failed') from the error, and log one tts.load_failed on the target with the cause's class and no detail"
    source_tag: Local Canon
    precedents: ["packages/infrastructure/src/avkit_infra/tts/adapter.py:103-121 — runtime_imports logs a failed import by class only, as its text can hold a local path", "docs/execution/reflections/2026-11-05-transcript-failure-reason-reflection.md — Session 50: a raw value that can reach a log is fixed in the row"]
    research: { engine: none, sources: [] }
    reasoning: "runtime_imports never raises, so only an injected probe reaches this; it must still not escape bare, as the device probe's branch says (adapter.py:308). LOG_CAUSE's detail would carry the probe's raw text, which can hold a path. The alternative, LOG_CAUSE with detail, matches the device probe's line but logs that text."
  - id: D-324
    stage: planning
    question: "How are the two kokoro-import tests (:739, :855) handled once the runtime check runs before the unload?"
    resolution: autonomous
    class: two-way
    chosen: "A′: _adapter gains an optional runtime_probe argument and both tests pass lambda _fmt: True; every assertion stays"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:624 — the plan names how the test is handled and takes it to review or Mat", "tests/integration/test_tts_device_resolution.py:1004 — tests already inject runtime_probe"]
    research: { engine: none, sources: [] }
    reasoning: "The setup change keeps the in-load import path pinned, which a probe that said yes and a later failing import still reach. A2 amends the assertions and loses that coverage. B, moving the engine imports before the unload, repeats what the runtime check proves and changes both tests' assertions as A2 does; building B's model there would be load-before-unload. Doing nothing leaves the adapter without a runtime check. The plan review and Mat see it at the gate."
  - id: D-325
    stage: planning
    question: "What is said about a failure after the unload?"
    resolution: autonomous
    class: two-way
    chosen: "It still leaves nothing loaded on cpu; the docstring says so, and AC-119.7, AC-119.8 and the A′ tests pin it"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:622 — After the unload", "known issue TTS-FAILED-LOAD-DROPS-MODEL — triage D-221, no load-before-unload"]
    research: { engine: none, sources: [] }
    reasoning: "The limit is Mat's (D-221). Stating it in the docstring and pinning it with tests stops a later change from reading LOAD_KEEPS as covering every failure."
  - id: D-326
    stage: planning
    question: "Where does the first-run check get the backend's default?"
    resolution: autonomous
    class: two-way
    chosen: "A DEFAULT_MODELS_DIRECTORY constant in setup-readiness.ts, '~/.avkit/models', expanded by expandUserPath; a stored value still wins"
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:1568 — the backend default stands and the probe uses it", "packages/core/src/avkit_core/services/settings.py:67 — the default", "packages/core/src/avkit_core/services/settings.py:175-182 — the default is never stored"]
    research: { engine: none, sources: [] }
    reasoning: "The readiness probe runs in the main process, also when the backend is down, so asking the backend over HTTP would leave it without an answer then. A constant tied by a contract test is the smallest change. Doing nothing keeps the probe on a folder the backend doesn't use."
  - id: D-327
    stage: planning
    question: "What does the probe report when the models folder doesn't exist yet?"
    resolution: autonomous
    class: two-way
    chosen: "B: the transient write-and-delete probe in the nearest existing ancestor folder; a file on the way reads false; no folder is created"
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:1569 — the probe stops creating an empty folder", "packages/infrastructure/src/avkit_infra/model_manager/assets.py:214 — the backend creates the folder at its first download", "ui/src/main/setup-readiness.ts:93-101 — the probe an existing folder already gets"]
    research: { engine: none, sources: [] }
    reasoning: "Creating the folder needs write access to its nearest existing parent, and the same probe the existing folder gets tests exactly that. A, accessSync alone, doesn't read Windows ACLs. C shows every fresh install as not ready. Doing nothing keeps the mismatch. The choice is at the gate."
  - id: D-328
    stage: planning
    question: "Where does the contract test that ties the two defaults live?"
    resolution: autonomous
    class: two-way
    chosen: "In setup-readiness.test.ts: Vitest reads settings.py and matches the tts.models_directory SettingSpec against DEFAULT_MODELS_DIRECTORY"
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:1571 — Tied", "ui/tests/unit/tts-model-selection.test.ts — renderer tests already read seeded ids by name"]
    research: { engine: none, sources: [] }
    reasoning: "The constant being tested is on the TypeScript side, so its test reads the Python default as text. A Python test reading the TypeScript would work as well; a generated shared constant would add a build step for one string."
  - id: D-329
    stage: planning
    question: "Does engine.py stay in this session's scope?"
    resolution: autonomous
    class: two-way
    chosen: "Yes, read-only: AC-121.1 builds the fresh-install catalog from its SEED_VARIANTS"
    source_tag: Local Canon
    precedents: ["packages/infrastructure/src/avkit_infra/database/engine.py:23-28 — SEED_VARIANTS", "packages/infrastructure/src/avkit_infra/database/repositories.py:355 — the catalog is read in id order"]
    research: { engine: none, sources: [] }
    reasoning: "A fresh install's preselection depends on which rows are seeded and in what order they come back. Reading the seed keeps AC-121.1 true to a fresh install if the seed changes. Dropping it, which the brief allows, would leave a hand-written catalog in the test."
  - id: D-330
    stage: planning
    question: "How does the fallback rank rows, and what if only FP16 is downloaded?"
    resolution: human
    class: product-preference
    chosen: "Runnable rows ranked by PRESELECT_ORDER, the rest after them in catalog order; first downloaded of that list, else its first; only FP16 downloaded keeps FP16"
    source_tag: Human-approved
    precedents: ["docs/build-plan/03-service-layer.md:635 — where the selection falls back by catalog order, INT8 comes first", "docs/build-plan/03-service-layer.md:639 — nothing removes or disables FP16", "docs/execution/reflections/2026-09-30-tts-repair-reflection.md:109 — D-17: loaded, then first downloaded, then first"]
    research: { engine: tavily, sources: ["https://primer.style/product/scenario-patterns/customize/ — honor a preference the user already set", "https://github.com/BaseInfinity/opencode-sdlc-wizard/issues/23 — re-picking a model every launch reported as a UX bug", "https://github.com/agama-project/agama/discussions/3335 — suggest inline instead of choosing for the user"] }
    reasoning: "Ranking keeps the first-downloaded rule, so a user who has a working download isn't shown a model that needs one. The alternative, INT8 even when not downloaded, would steer away from FP16 harder but preselect a model that must be fetched first, on every launch, because the pick isn't saved. Marking FP16 in the picker needs new UI outside this plan. Doing nothing keeps FP16 on a fresh install. Brief in human-gate-decision.md."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed'"
  - id: D-331
    stage: planning
    question: "Which model does a fresh install preselect, ONNX INT8 or ONNX FP32 (the listening verdict, asked at the plan gate)?"
    resolution: human
    class: product-preference
    chosen: "INT8: PRESELECT_ORDER = ['kokoro-onnx-int8', 'kokoro-onnx-fp32']; row 6's Red encodes INT8; rows 9 and 10 and the gate smoke the pinned model_quantized.onnx; no count of samples at ±1.0 (not asked for)"
    source_tag: Human-approved
    precedents: ["docs/build-plan/03-service-layer.md:634 — Mat listens to the INT8 sample before this ships", ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:226 — the listening note", ".agent/context/known-issues.yaml:4025-4044 — D-239: INT8 or FP32 until the cause is known, INT8 the working choice"]
    research: { engine: tavily, sources: ["https://www.npmjs.com/package/kokoro-js?activeTab=readme — examples load dtype q8", "https://briantung.me/blog/tts-engines-in-the-browser — q8 3.5 times smaller, audio effectively identical", "https://arxiv.org/html/2610.06817v1 — Appendix B: dynamic INT8 0.58, FP32 0.21 against the reference", "https://github.com/k2-fsa/sherpa-onnx/issues/3754 — INT8 on ARM: rail-pinned sentences and 4.8/9.6 kHz tones, checked for and absent here"] }
    reasoning: "Asking at the gate means the Red, the Green and the smoke all follow one verdict. INT8 is 3.5 times smaller, uses 240-315 MB less peak memory, and showed none of #3754's fault on this PC; FP32 is closer to the reference. No verdict would stop MEU-121 at row 6 (S11). Brief in human-gate-decision.md."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed'"
  - id: D-332
    stage: planning
    question: "Where does the packaged check run?"
    resolution: autonomous
    class: two-way
    chosen: "Here, as --phase sentences on a fresh local onedir with FP16 as the Red, and again in the session gate; MEU-125's rc.2 gate repeats it on the installer's copy"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-06-tts-build-capability/implementation-plan.md — Session 51 D-315 ran its capability smoke here on a fresh local build", "docs/build-plan/03-service-layer.md:640 — Done is on a packaged build"]
    research: { engine: none, sources: [] }
    reasoning: "Done names a packaged build, and the onedir is what the installer wraps. Running FP16 first proves the check catches the failure. Leaving it to MEU-125 alone would close this session without its Done."
  - id: D-333
    stage: planning
    question: "What is the spike's box, what does it try, and when does the FP16 issue close?"
    resolution: human
    class: externally-blocked
    chosen: "2 hours from the first spike JSON; E0 to E4 from local files; E5 runs last, with onnx==1.23.2 and ml-dtypes==0.6.0 fetched into the uv cache and installed with --no-deps --require-hashes into a Temp target in its step only (Mat's yes); no fix inside the box; the issue closes only on a cause plus Mat's approval of a re-reviewed amendment, or on Mat's ruled outcome; otherwise it stays open with verification only"
    source_tag: Human-approved
    precedents: ["docs/build-plan/03-service-layer.md:639 — the FP16 outcome comes back to Mat", "known issue TTS-ONNX-FP16-NONFINITE-AUDIO — triage D-239, split flag yes", "docs/execution/reflections/2026-10-01-mcp-live-audit-reflection.md:80 — D-1 kept a dev runner off uv.lock"]
    research: { engine: tavily, sources: ["https://onnxruntime.ai/docs/performance/model-optimizations/float16.html — float16 work uses the onnx package; op block list and keep_io_types", "https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/discussions/9 — a longer block list still gave all-NaN output", "https://arxiv.org/html/2610.06817v1 — Appendix B: fp16 weights alone are indistinguishable from fp32, pointing at activations", "https://www.a2p.it/machine-learning/debugging-onnxruntime-web-models — intermediate outputs need a graph edit or a custom build"] }
    reasoning: "The hunt has no upper bound, and the brief asks the plan to cap it. A full FP16 pass of the 140 pairs took about 2 minutes on 2026-11-04 (fp16-rate-probe.txt), so two hours covers E0 to E4, about ten full passes plus E3's runs on the failing pairs, with room to repeat one. A fix would change the adapter, so it needs its own Red and review. The box and the closing rule are the planner's and stood at the gate; the fetch was S5's to lift, and Mat ruled E5 yes, because only E5 says which node first goes non-finite. Deciding at S13 would add a second stop; no would leave the outcome brief with a trigger but no location. Brief in human-gate-decision.md."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed'"
  - id: D-334
    stage: planning
    question: "Which checks does the session gate run?"
    resolution: autonomous
    class: two-way
    chosen: "Session 51's gate with smoke-sentences in place of smoke-capability; the MCP suites stay as guards; mcp-audit, build-record and smoke-capability are skipped with reasons"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-06-tts-build-capability/implementation-plan.md — Session 51 §Session gate"]
    research: { engine: none, sources: [] }
    reasoning: "The MCP suites are cheap and catch an API change nobody planned. The capability smoke checks a refusal MEU-119 doesn't reach, and MEU-125 repeats it."
  - id: D-335
    stage: planning
    question: "The missing-weight tts.load_failed detail carries the full weight path, so the Windows user name reaches console.log (Session 50 RULE-1): fix it where, or keep it?"
    resolution: human
    class: source-conflict
    chosen: "HOME_SCRUB: console_field replaces the home folder with ~ before the URL, redaction and length rules; rows 2a (Red) and 2b (Green) with AC-119.10; health.py and tests/unit/test_services.py join Files Modified; the six log sites, REDACT_NEEDLES, AC-115.9's assertions and Electron main or MCP logging stay unchanged; one TEMP-under-home run of the 11 Console-reading test files"
    source_tag: Human-approved
    precedents: ["docs/execution/reflections/2026-11-05-transcript-failure-reason-reflection.md:137 — Session 50 RULE-1: a raw value that can reach a log is fixed in the row or raised", "docs/build-plan/03-service-layer.md:561 — D-247 and D-296 to D-305: errors always reach console.log, Console fields are single redacted lines", "packages/infrastructure/src/avkit_infra/tts/adapter.py:103-121 — runtime_imports logs a failed import by class only, as its text can hold a local path"]
    research: { engine: tavily, sources: ["https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html — file paths and personal names may need de-identification before the event is recorded", "https://github.com/OWASP/www-project-devsecops-verification-standard/blob/main/document/OPR-004-Application-Security-Logging.md — sensitive personal data masked at the point of logging", "https://code.visualstudio.com/docs/configure/telemetry — error stack traces scrubbed of user paths"] }
    reasoning: "Every Console field passes through console_field, and stdout, the ring and console.log receive only its output, so one change covers the missing-weight line and the five other events whose text can hold a home path. Fixing the one line would leave the rest for separate rulings and either lose the folder or change AC-115.9. Keeping the path leaves the user name in every pasted log. Mat's 'one new row' is written as a Red half (2a) and a Green half (2b), as every other change in this plan is; that is form, not scope. Brief in human-gate-decision.md."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed'"
```

## Research References

- `docs/build-plan/03-service-layer.md:612-641` and `docs/build-plan/06-gui.md:1560-1572` (the residual contracts).
- `.agent/context/known-issues.yaml` (the three issues), and the grouping file §3 `:172`, §6 `:242` and §8.
- `fp16-test-set/` (copied 2026-11-06): `fp16_nan_probe.py`, `fp16_rate_probe.py`, `tts_variant_compare.py`, `fp16-nan-probe.txt`, `fp16-rate-probe.txt`, `phonemes.json` and `test-set.json` (`C:/Temp/av-kit/s52-test-set-copy.txt` holds each file's bytes, line endings and SHA-256).
- Session 51's plan, task and reflection (`docs/execution/plans/2026-11-06-tts-build-capability/`, `docs/execution/reflections/2026-11-06-tts-build-capability-reflection.md`), and Session 50's reflection.

## Planning receipts

- `C:/Temp/av-kit/s52-decision-issue-probe.txt`: the decisions the closeout check reads for each issue and for the grouping.
- `C:/Temp/av-kit/s52-register-keys.txt`: Session 51 RULE-2. Each of the three issues already holds `status`, `verification` and `resolution_path`, so the resolve script adds no key. The register's SHA-256 was `d0040c2ed12d23c28c16ca170b66c2eda9fe317ff085ee49d23fd326c8df1fd1` at plan time; row 12 reads it again for `--expect-sha256`.
- `C:/Temp/av-kit/s52-meu-stats.txt`: 126 MEUs, 112 completed, 14 pending.
- `C:/Temp/av-kit/s52-test-set-copy.txt` and `C:/Temp/av-kit/s52-issue-read.txt`.
- D-335 (2026-11-07): `C:/Temp/av-kit/s52-d335-consumers.txt` (nothing reads a path back out of Console text), `s52-d335-path-asserts.txt` (no Console message assertion holds a path, in the 11 Console-reading test files) and `s52-d335-tempsources.txt` (where the product's temp files and paths come from, CI's runners, and pytest's temp root).
- D-333 E5 (2026-11-07): `C:/Temp/av-kit/s52-onnx-pin.txt`, `s52-ml-dtypes-pin.txt` and `s52-onnx-deps.txt`, from PyPI's JSON for each package (`s52-onnx-pypi.json`, `s52-onnx-1.23.2-pypi.json`, `s52-ml-dtypes-pypi.json`). These were metadata reads only; no wheel was fetched. `uv pip install --help` (uv 0.12.5) lists every flag E5's install uses. `C:/Temp/av-kit/s52-e5-bound-probe.txt` (round 2 F1) is the offline probe of `--no-deps` and `--require-hashes`, with the uv cache inventory before and after in `s52-e5-probe-cache-before.txt` and `s52-e5-probe-cache-after.txt`.
- Step 4A GUI check (`gui-refs-not-shipped`, items 3 and 5):
  - E2: the TTS model select's default value changes, and AC-121.6 checks it on the built app.
  - G30: the model select keeps its option pairs. No new styling.
  - G32: no colour value is added.
  - G31 and G33 to G35 don't apply: no new control, label, layout or icon.
  - No test id is added, so `test-ids.ts` and its byte-hash tests aren't touched.
- Not run at plan time: any suite, build or smoke. Row 0 runs them.

## Validation stage contract

- **Static:** `pyright packages/`, `ruff`, the UI typecheck and lint, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each Red and Green row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python, UI and MCP suites, the UI and MCP builds, the OpenAPI guard and the two render checks, in the session gate.
- **Runtime:** the settings and TTS E2E specs on the built app, a fresh onedir, `SENTENCE_SMOKE` on the preselected variant, `DEV_CHECK` and the models snapshot.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime. The gate records it before and after, and H1-6b checks each handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
