# Human gate decisions (planning)

These are the four questions this plan puts to Mat at the plan gate (`implementation-plan.md:93`, `:113`, `:115`, `:119`), briefed under `.agent/docs/human-decision-protocol.md`. Mat asked for them on 2026-11-07: "run HDP on the first 4 decisions and give me recommendations". A brief here authorizes nothing until Mat's ruling is recorded under it, and each brief's sources go into the decision log at that point. Receipts are under `C:/Temp/av-kit/`, prefixed `s52-hdp-`.

## D-331: which model a fresh install preselects, ONNX INT8 or ONNX FP32 (the listening verdict)   [product-preference] [planning]

**Recommendation:** INT8, unless you hear something in it you don't like. Listen to `C:/Temp/av-kit/tts-compare/listen-kokoro-onnx-int8.wav` against `listen-kokoro-onnx-fp32.wav` (`listen-kokoro-pt-fp32.wav` is the PyTorch reference). The measurements below find none of the INT8 artefacts reported elsewhere. INT8 is a 92 MB download against 326 MB and uses less memory, and it is the working choice D-239 named. What the numbers do show is that INT8 is a little slower in its timing and a little duller at the top. FP32 is measurably closer to the reference and about 10% faster on this PC. If INT8's rhythm or crispness bothers you, choose FP32.

**What the files measure** (`s52-hdp-audio-compare.json`, numpy only; script in the session scratchpad)

| Measure (listen sample, 24 kHz) | ONNX INT8 | ONNX FP32 | PyTorch FP32 (reference) |
|---|---|---|---|
| Length | 13.575 s | 13.475 s | 13.475 s |
| Clipped samples (at ±1.0) | 0 | 0 | 0 |
| Noise floor in the gaps between words | -63.3 dBFS | -64.0 dBFS | -65.6 dBFS |
| 4.8 kHz tone in the gaps, against its neighbouring bins | -2.0 dB | -2.7 dB | -2.6 dB |
| 9.6 kHz tone in the gaps | +3.6 dB | +3.3 dB | +3.2 dB |
| Energy above 8 kHz | 3.84% | 4.07% | 3.07% |
| Spectral centroid | 941 Hz | 976 Hz | 869 Hz |
| Log-mel distance to PyTorch (level-matched DTW) | 0.36 | 0.14 | — |

| Run (27 s of speech, this PC, two rounds) | ONNX INT8 | ONNX FP32 |
|---|---|---|
| File | 92.4 MB | 325.5 MB |
| Load | 0.75–0.76 s | 0.75–0.77 s |
| Generate | 3.69–3.81 s (first call 3.81–4.00 s) | 3.36–3.40 s |
| Peak memory: this run, and the 2026-11-04 probe | 1190 MB, 583 MB | 1505 MB, 817 MB |
| Speech length | 27.425 s | 27.100 s |

What the measurements say:
- **No sign of the reported INT8 fault.** sherpa-onnx #3754 reports Kokoro INT8 on ARM producing steady tones at 4.8 and 9.6 kHz, 15–20 dB above the noise floor, and whole sentences pinned at +1.0. Here INT8's gap tones are within 0.7 dB of FP32's and under +4 dB, and no sample clips. On the 27-second file, both ONNX files show a +6 dB tone at 4.8 kHz against PyTorch's -1.9 dB. That comes from the ONNX export, not from INT8.
- **INT8's difference is timing and top end.** INT8 speaks 0.7–1.2% longer (+100 ms on the listen sample, +325 ms over 27 s) and has slightly less energy above 8 kHz. Its distance from PyTorch is about 2.5 times FP32's. The Paradee paper measured the same file the same way and got the same ratio: 0.58 for the prebuilt INT8 against 0.21 for the FP32 export, with INT8 shifting durations by 65 ms. That paper puts a 3% slower speaking speed at 0.36, so INT8's difference is about the size of a slight tempo change.
- **None of this says how it sounds.** That is why D-239 left the choice to your ear.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ INT8 first, FP32 second | — | — | D-239; kokoro-js and the model card default to `q8` |
| ⚠️ FP32 first, INT8 second | Closer to the reference (0.14 against 0.36); about 10% faster here; no duration shift | A 326 MB download (3.5 times larger) and 240–315 MB more peak memory; D-239 named INT8 the working choice | Paradee Appendix B; this PC's runs |
| ❌ No verdict (status quo) | Nothing changes | S11 stops MEU-121 at row 6, and a fresh install keeps preselecting FP16, against D-239 | plan S11 |

**Precedent:**
- D-239 (`USER_EXPLICIT` 2026-11-04, `known-issues.yaml:4025-4044`): "ONNX INT8 or ONNX FP32 until the cause is known. INT8 is the working choice, as the smallest file with the least memory. Mat listens to it first." This applies directly. The ruling is already carried into `docs/build-plan/03-service-layer.md:635-636` and the grouping at `:226`.
- D-217 (Mat, the same day): PyTorch stays out of installed builds, so the choice is between the ONNX variants only. This applies directly.
- Receipt `s52-hdp-sweep-331.txt`.

**Research:** Pomera web search (Tavily, Exa).
- Practice: the [kokoro-js README](https://www.npmjs.com/package/kokoro-js?activeTab=readme) and the [onnx-community model card](https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX) both load `dtype: "q8"` in their example. The [author's announcement](https://huggingface.co/posts/Xenova/503648859052804) used `fp32`, and the README recommends `fp32` for WebGPU.
- Practice: [Brian Tung's browser benchmark](https://briantung.me/blog/tts-engines-in-the-browser) found q8 3.5 times smaller and 2.4 times slower under WASM, with "effectively identical" audio: "same duration to the sample, F0 within 1.6%, spectral centroid within 1.5%". On this PC the duration differs by about 1%.
- Authority: [Paradee, arXiv 2610.06817](https://arxiv.org/html/2610.06817v1), Appendix B. The prebuilt dynamic-INT8 file, which also quantizes activations, measures 0.58 and shifts durations by 65 ms. The FP32 export measures 0.21, a 3% tempo change 0.36, and a different voice 1.27.
- Practice (a fault to check for): [sherpa-onnx #3754](https://github.com/k2-fsa/sherpa-onnx/issues/3754) reports INT8 on ARM giving rail-pinned sentences and 4.8/9.6 kHz tones, with FP32 unaffected. The measurements above check for both.

**Obviousness test (§4):** fails test 3. D-239 made this a product choice, and the tie-breaker is how it sounds to you.

**Reversibility / risk:** two-way. `PRESELECT_ORDER` is one constant, it only sets the first-run default, and any user can pick another model. Risk: the sentence smoke (rows 9 and 10) checks that every job finishes with finite audio. It does not count samples pinned at ±1.0, which is how #3754's fault showed, intermittently and on ARM. These two files have none, and the 2026-11-04 probes didn't measure it. If you want that count on the preselected model, it would be a small addition to row 9's `--phase sentences`, as a plan amendment.

**If you do not answer:** rows 0 to 5 (MEU-119, MEU-120) can run, and MEU-121 stops at row 6 (S11).

**What the recommendation would authorize:**
1. `PRESELECT_ORDER = ['kokoro-onnx-int8', 'kokoro-onnx-fp32']` (plan `:93`), with row 6's Red encoding INT8.
2. Rows 9 and 10 and the session gate run the sentence smoke on the pinned `model_quantized.onnx`, under S12.

A ruling for FP32 instead swaps the order and runs the smoke on the pinned FP32 file. It does not authorize: removing, disabling or relabelling FP16 (D-239), any catalog, seed or download change, or the clip count unless you ask for it.

**Decision (D-331).** Source: `USER_EXPLICIT`, 2026-11-07, Claude Code (VS Code) chat. Mat wrote:

> D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed

This takes the recommendation and authorizes exactly the two items listed above it. The clip count was not asked for, so row 9's phase does not count samples at ±1.0.

## D-335: the home folder in Console lines (the missing-weight `tts.load_failed` path, raised under Session 50 RULE-1)   [source-conflict] [planning]

**Recommendation:** replace the home folder with `~` inside `console_field` (`packages/core/src/avkit_core/services/health.py`), and leave the missing-weight line and AC-115.9 as they are. Every Console field passes through that function, and stdout, the Console ring and `console.log` all receive only its output. One change there takes the Windows user name out of all three for every event. The line keeps the useful part of the path (`~\.avkit\models\…\model_quantized.onnx` still says which file is missing and where the app looked). AC-115.9's contract also stands, because `detail` still holds the cause's first line, redacted as it already is. The missing-weight line is not the only one: a read of the TTS and capture services finds six events whose text can hold a home path (table below). RULE-1 would otherwise make each of them a separate question. The cost is one new row with its own Red, in core rather than the TTS files. That widens the plan's scope, which makes it your call.

**What can carry a home path today** (read from the code; not a full sweep, which the chokepoint makes unnecessary)

| Event | Level | Field | What the text holds |
|---|---|---|---|
| `tts.load_failed` | ERROR | `detail` | A missing or unreadable weight file: its full path (`adapter.py:169-175`). `ONNX session failed`: the runtime's own text, which usually names the model file (`:384-399`). A PyTorch load: torch's text (`:350-376`) |
| `tts.generate_failed` | WARNING | `error` | A non-domain exception's text, such as an `OSError` on the output file (`services/tts.py:347-349`) |
| `tts.cleanup_failed` | WARNING | `error` | Raw `OSError` text, which names the partial file (`services/tts.py:397`) |
| `capture.revert_failed`, `capture.flatten_failed`, `capture.convert_failed` | WARNING | `error` | Raw `OSError` text (`services/capture.py:621`, `:665`, `:725`) |

ERROR lines always reach `console.log` (D-247). WARNING lines reach stdout and the Console ring, and they reach `console.log` while `app.log_to_file` is on. Fields outside `CONSOLE_FIELDS` (`path=`, `target=`) and tracebacks are already dropped.

**What the scrub would do:** the home folder becomes `~` where it starts a path. The home folder comes from `Path.home()`, read through one function the tests can patch. The scrub matches `\`, `/` and doubled `\\` separators (an `OSError`'s text quotes its path with doubled backslashes) and ignores case on Windows. It matches only when a separator, a quote or the end of the text follows, so `C:\Users\ana` doesn't match inside `C:\Users\anabel`. A path outside the home folder is unchanged. The scrub runs before the 300-character cut.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ `~` scrub in `console_field` (one new row, core) | — | — | OWASP Logging Cheat Sheet; VS Code telemetry; Session 50 RULE-1 |
| ⚠️ Fix the missing-weight line only: its cause carries the file name, or the class only as in D-323 | The smallest diff, inside `adapter.py`, which row 2 already edits, and no core change | Fixes one cause of one event. The other five events and the runtime's load text keep the user name, so they'd go on the register under your ruling (RULE-1). The file-name form loses the folder, and the class-only form changes AC-115.9 by dropping `detail` | D-323; `adapter.py:103-121` |
| ❌ Keep the path (status quo; row 2 as written) | No change, and a user reading their own log sees the full path | The Windows user name reaches `console.log` on every missing-weight failure, because errors always go to the file (D-247). It goes into any public issue that pastes the log. RULE-1 lets this stand only by your ruling | Session 50 RULE-1; OWASP |

**Precedent:**
- Session 50 RULE-1 (`docs/execution/reflections/2026-11-05-transcript-failure-reason-reflection.md:137`): "A raw or unredacted value that can reach a log, stdout or the Console is fixed in the row or raised as a question, never recorded as a residual." This applies directly; this brief is the raise.
- D-323 (this plan, `implementation-plan.md:480-488`), and `runtime_imports` before it (`adapter.py:103-121`): the line logs the cause's class only, because its text "can hold a local path". This applies by analogy; the fixes so far have been per line.
- D-247 (`USER_EXPLICIT` 2026-11-05, "D-247: yes they should go to file") and D-296 to D-305 (`docs/build-plan/03-service-layer.md:561`): errors always reach `console.log`, and Console fields are single redacted lines. This applies directly. The scrub extends that redaction and doesn't change what `detail` carries.
- No home-folder scrub exists in the backend, the main process or the MCP server (`s52-hdp-sweep-home-scrub.txt`), so this would be the first.
- Receipts `s52-hdp-sweep-path.txt` and `s52-hdp-sweep-console-tests.txt` (13 test files read Console output).

**Research:** Pomera web search (Tavily).
- Authority: the [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) lists file paths, beside personal names, among data that "may also need to be treated in some special manner before the event is recorded". It suggests de-identification: deletion, scrambling or pseudonymization.
- Authority: [OWASP DevSecOps OPR-004](https://github.com/OWASP/www-project-devsecops-verification-standard/blob/main/document/OPR-004-Application-Security-Logging.md) says sensitive personal data is "excluded or masked at the point of logging".
- Practice: the [VS Code telemetry docs](https://code.visualstudio.com/docs/configure/telemetry) say its error events "contain stack traces that have been scrubbed of user paths".
- The two tilde queries (`s52-hdp-research-path-b.txt`) found only shell usage. Nothing found argues for keeping the user name.

**Obviousness test (§4):** fails test 1. The sources agree that the user name should go, but where to fix it is a conflict between the plan's scope (row 2 keeps the line as it is, and the plan's files don't include `health.py`) and RULE-1. Widening scope is your call, as in D-175 and D-176.

**Reversibility / risk:** two-way: one function and its test. Risk: a test that asserts a raw path under the home folder in a Console message would break wherever TEMP is under the home folder. That is CI's case, though not this host's, where the suite runs with TMP and TEMP outside the home folder. So the row runs the 13 Console-reading test files once with TEMP under the home folder before its Green. It also checks that nothing reads a path back out of Console text. The amendment needs one recheck round of the plan review before execution.

**If you do not answer:** row 2 keeps the line as it is (the plan's default), the six events stay unchanged, and the reflection records this raise as unruled.

**What the recommendation would authorize:**
1. A plan amendment: one new row after row 2 and AC-119.10, with `health.py` and its unit test added to Files Modified and the scope list.
2. One recheck round of the plan review on that amendment (the rolling report, with its own `## Recheck` section).
3. The scrub in `console_field`, with a Red unit test covering the three separator forms, case, a look-alike user folder and an unchanged path outside the home folder.
4. One run of the Console-reading tests with TEMP under the home folder.

It does not authorize: editing the six log sites, `REDACT_NEEDLES`, AC-115.9's assertions, logging in Electron main or the MCP server, or any commit.

**Decision (D-335).** Source: `USER_EXPLICIT`, 2026-11-07, Claude Code (VS Code) chat. Mat wrote:

> D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed

This takes the recommendation and authorizes exactly the four items listed above it. The amendment and its recheck round come before row 0.

## D-333 E5: fetch the `onnx` package so the spike can find the first non-finite node   [externally-blocked] [planning]

**Recommendation:** yes, as the spike's last experiment and inside its 2-hour box. Pin one exact `onnx` release: the newest with a cp312 Windows wheel that is at least two weeks old, recorded in the spike summary. Fetch it only in E5's own child, with `uv run --no-sync --with onnx==<version>`. It lands in the uv cache only: `pyproject.toml`, `uv.lock` and the venv don't change, and `uv cache clean onnx` removes it. E5 is the only experiment that says where the overflow starts. E0 to E4 can show what changes the outcome (a fusion, the runtime version, the input, threading), but not which node first produces a non-finite value. That node is what any fix, or a re-export with a longer block list, would have to target.

**What E5 does:** it loads `model_fp16.onnx` with `onnx` and adds each node's output as a graph output. It runs the failing pairs through the runtime and reports the first node, in graph order, whose output holds NaN or Inf, with that node's op type and the range of its inputs. Extra graph outputs can block a fusion. If E1 shows that the failure needs one, E5 runs at the level where the failure still reproduces, and says so if none does. There is no route without the package. ORT's per-node dump exists only in debug builds, not in the PyPI wheel, and editing the graph by hand would mean parsing ONNX's protobuf schema, which is what `onnx` does.

**What the fetch is:** one wheel from PyPI, `onnx`, published by the ONNX project. The venv already holds `numpy` 2.5.4, `protobuf` 7.36.2 and `typing-extensions` 4.16.0. Anything else that release needs comes with it and is listed in the receipt. This yes lifts S5 for this package only.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ Yes: one pinned package, uv cache only, last in the box | — | — | ORT float16 docs; HF discussion #9; Paradee Appendix B |
| ⚠️ Decide at S13, after E0 to E4 | You see E0 to E4's findings first, and there's no fetch if they already name the cause | A second stop mid-spike. If the box runs out first, the spike ends at S13 without E5 | plan S13 |
| ❌ No (status quo) | No network fetch | The spike can end with a trigger but no location, and the FP16-outcome brief at S13 has less to go on | — |

**Precedent:**
- The plan (`implementation-plan.md:119`, `:206`, `:211`): E5 runs only on your yes, and `fp16-spike.py all` gets `--e5` only after it. S5 stops any package download until you rule. This applies directly.
- E2 (plan `:199`) already runs other runtime versions through `uv run --offline --with onnxruntime==<v>` from the cache. This is the same mechanism, with one online fetch. It applies directly.
- The MCP live-audit D-1 (`docs/execution/reflections/2026-10-01-mcp-live-audit-reflection.md:80`) kept a dev runner off `uv.lock`. This applies by analogy: the fetch leaves `uv.lock` alone.
- Receipts `s52-hdp-sweep-e5.txt` and `s52-hdp-sweep-e5-gated.txt`.

**Research:** Pomera web search (Tavily, Exa).
- Authority: the [ONNX Runtime float16 guide](https://onnxruntime.ai/docs/performance/model-optimizations/float16.html) tells you to install `onnx` and `onnxconverter-common` for float16 work. It describes `keep_io_types` and an op block list, and it clips constants to `max_finite_val`.
- Practice: [Kokoro-82M-v1.0-ONNX discussion #9](https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/discussions/9) ("`model.onnx` to `model_fp16.onnx`"): a user who extended `DEFAULT_OP_BLOCK_LIST` still got all-NaN output. The shipped FP16 file depends on which ops stayed in FP32.
- Authority: [Paradee, Appendix B](https://arxiv.org/html/2610.06817v1): with all weights in fp16, Kokoro is "indistinguishable from fp32" (0.11). That points at activations overflowing in particular nodes, not at weight precision, which is what E5 locates.
- Practice: [onnxconverter-common #323](https://github.com/microsoft/onnxconverter-common/issues/323) (open since 2025-09) reports float16 ReduceMean giving zeros or NaN for some inputs, and [ORT #11384](https://github.com/microsoft/onnxruntime/issues/11384) reports fp16 NaN where fp32 is fine. Overflow that depends on the input and sits in one op is a known pattern.
- Novel: [a2p.it on debugging onnxruntime-web](https://www.a2p.it/machine-learning/debugging-onnxruntime-web-models) needed a custom runtime build to see intermediate outputs, which is why E5 edits the graph instead.

**Obviousness test (§4):** externally blocked. A network fetch is S5, and only you lift it.

**Reversibility / risk:** two-way. `uv cache clean onnx` undoes the fetch, and nothing in the repo changes. Supply-chain risk is limited to one official package, exactly pinned, with its hashes recorded. E5 runs last, and the box check before it stops it like any other experiment.

**If you do not answer:** E0 to E4 run, and E5 is recorded in the summary as not run.

**What the recommendation would authorize:**
1. One fetch of `onnx==<version>`, and any dependency the venv lacks (listed), into the uv cache, in E5's child only.
2. `--e5` on `fp16-spike.py all` (plan `:211`).
3. The spike receipt records the version, the wheel hashes and the uv cache entries before and after.

It does not authorize: adding `onnx` to `pyproject.toml` or `uv.lock`, `onnxconverter-common` or any other package, any fix or re-export inside the box, or any other download (S5 still applies).

**Decision (D-333 E5).** Source: `USER_EXPLICIT`, 2026-11-07, Claude Code (VS Code) chat. Mat wrote:

> D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed

This takes the recommendation and authorizes exactly the three items listed above it.

**Planner's correction after recheck round 2 (2026-11-07), within the three items.** Round 2 found that the first E5 design, an online `uv run --with` overlay, left uv free to resolve and fetch more than the two wheels. E5 now installs exactly `onnx==1.23.2` and `ml-dtypes==0.6.0` from a hashed requirements file with `uv pip install --no-deps --require-hashes --only-binary :all:` into `C:/Temp/av-kit/s52/e5-site`, then runs offline with `PYTHONPATH` set to that folder (plan §FP16 spike, E5's fetch). The packages and the uv cache destination are unchanged; the fetch is narrower. The receipt still records the versions, the hashes and the uv cache entries before and after. `uv cache clean onnx ml-dtypes` and deleting `e5-site` undo it.

## D-330: if only FP16 is downloaded, is FP16 still preselected?   [product-preference] [planning]

**Recommendation:** yes, keep the plan's rule. Runnable rows are ranked by `PRESELECT_ORDER` (D-331's order first), and the first downloaded row in that ranking wins. A user who has only FP16 downloaded keeps FP16. The page doesn't remember a pick across launches: `chosenModel` is `useState(null)` (`TTSPage.tsx:122`), so the rule runs again every time the app opens. Under the alternative, a user who downloaded FP16 would see INT8, not downloaded, each time they open the TTS page, and would have to pick FP16 again each time. A fresh install, which is the case D-239 rules on, gets INT8 under either option. The users with only FP16 are rc.1 users who kept the preselected FP16, Mat's test PC among them (`known-issues.yaml:3504`). Whether they should be moved off FP16 is the FP16-outcome question (D-333, S13), not a preselection rule.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ Ranked, first downloaded (the plan) | — | — | `03-service-layer.md:635`; D-17; Primer Customize |
| ⚠️ INT8 preselected even when it isn't downloaded | Moves every FP16 user off the failing model. D-239's reasoning favours this: "A user who keeps the preselected model should not hit a failure" | Overrides a working download on every launch, because the pick isn't saved. Shows **Get** where the user had **Load**. Breaks D-17's first-downloaded rule. Needs a plan amendment and a recheck round | D-239 reasoning; opencode-sdlc-wizard #23 |
| ⚠️ Keep FP16, and mark it in the picker with its known failure | Tells FP16 users why to switch, without switching for them | New copy and UI outside the plan's files, which would need its own AC, review and session | agama RFC #3335 |
| ❌ Catalog order (status quo, no ranking) | No change | The catalog comes back in id order (fp16, fp32, int8, pt-fp32), so a fresh install keeps preselecting FP16, against D-239 | `tts-controls.ts:104-126`; `repositories.py:355` |

**Precedent:**
- D-239 (`USER_EXPLICIT` 2026-11-04, `03-service-layer.md:635`): "a fresh install preselects ONNX INT8 and not FP16: where the selection falls back by catalog order, INT8 comes first". This applies directly. Both options keep its letter, which covers a fresh install and the fallback. Its reasoning (`known-issues.yaml:4043`) leans towards the alternative.
- `03-service-layer.md:639` (D-239): nothing removes or disables FP16. This applies directly; neither option does.
- D-17 (2026-09-30 TTS repair, `docs/execution/reflections/2026-09-30-tts-repair-reflection.md:109`): loaded, then first downloaded, then first. This applies directly; the recommendation keeps it.
- D-217 and D-320 (`03-service-layer.md:595`, `:608`): the way to steer users away from a row has been to disable it with a reason. D-239 declined that for FP16. This applies by analogy.
- Receipt `s52-hdp-sweep-330.txt`.

**Research:** Pomera web search (Tavily, Exa).
- Practice: [Primer, Customize](https://primer.style/product/scenario-patterns/customize/): "A strong, accessible default is the starting point", and "When someone has already set a preference … honor it rather than asking them to set it again." A downloaded model is the nearest thing this page has to a stated preference.
- Practice: [opencode-sdlc-wizard #23](https://github.com/BaseInfinity/opencode-sdlc-wizard/issues/23) (2026-06) reports, as a UX bug, users made to re-pick their model "every time" because a remembered choice and the configured default disagree. The alternative would build that re-pick into every launch.
- Novel: [agama RFC #3335](https://github.com/agama-project/agama/discussions/3335) proposes a "suggested" strategy: show an inline alert instead of choosing for the user. That is the mark-it option.
- Practice: the local-model app guides searched ([LocalAI models](https://localai.io/docs/getting-started/models), LM Studio) don't settle this case: they offer candidates and let the user pick.

**Obviousness test (§4):** fails test 3. D-239's letter and its reasoning point different ways for this one case, and the plan recorded it with source Human-approved, so it is your choice.

**Reversibility / risk:** two-way. It is one branch in `defaultModelSelection`, and the user can pick any model. Risk of the recommendation: a rc.1 user who kept FP16 keeps hitting its failures until they pick another model or the FP16 outcome is ruled.

**If you do not answer:** the plan's rule stands as written.

**What the recommendation would authorize:** nothing beyond the plan as written (rows 6 and 7, D-330 in the decision log).

It does not authorize: a saved model pick, any picker copy, or disabling FP16.

**Decision (D-330).** Source: `USER_EXPLICIT`, 2026-11-07, Claude Code (VS Code) chat. Mat wrote:

> D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed

This takes the recommendation. It authorizes nothing beyond the plan as written.
