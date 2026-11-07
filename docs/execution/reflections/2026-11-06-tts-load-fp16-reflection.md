---
date: "2026-11-07"
project: "tts-load-fp16"
meus: ["MEU-119", "MEU-120", "MEU-121"]
plan_source: "docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-07 Meta-Reflection

> **Date**: 2026-11-07
> **MEU(s) Completed**: MEU-119 `svc-tts-load-keeps-model`, MEU-120 `gui-models-dir-probe` and MEU-121 `svc-tts-fp16-nonfinite`. Session 52 closes TTS-FAILED-LOAD-DROPS-MODEL and MODELS-DIR-DOCS-AND-PROBE-MISMATCH. TTS-ONNX-FP16-NONFINITE-AUDIO stays open with its failure site recorded. Mat ruled that FP16 stays as shipped and MEU-127 takes the follow-up (D-336, D-345), and that the execution review's two findings are fixed before the commit (D-340)
> **Plan Source**: `docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review took four rounds and 22,860,314 tokens.**
     - Round 1 approved with no findings (11,373,866).
     - Mat's "E5 yes" turned E5 into an online fetch, so the amended plan went back. Round 2 was `changes_required` with one High: E5's online overlay was not limited to the two authorized wheels (7,353,486).
     - Round 3 approved and resolved F1 (1,885,360). Its section had no Prior Pass Summary table naming F1 in a Recheck Result column, though, so `--approved-state-only` still counted round 2's F1 as open and blocking, and refused.
     - Round 4 was a closure-only recheck that added `| F1 | open | fixed |` (2,247,602). It existed only for that table: RULE-1.
   - **The plan loop's budget.** The ledger stopped the plan loop twice before Mat lifted it. Mat added 12,247,732 tokens at 13:11:32Z, then 50,000,000 tokens and two rounds at 13:22:35Z ("add 50M tokens and 2 more rounds, continue").
   - **The execution loop's budget.** Mat's grant was recorded on the plan loop, the only loop open at the time. The execution loop opened later on its default budget of 6 rounds and 21,000,000 tokens. Round 1 cost 14,996,767, and the ledger holds the last round's cost in reserve, so it refuses a round 2 until Mat continues the loop (D-340): RULE-3.
   - **Execution round 2.** Mat continued the execution loop by 10,000,000 tokens at 16:34:19Z (D-340). Rows C1 to C4 fixed F1 and F2. The gate's first rerun passed, then a one-sentence correction to the register (below) changed the bound tree, so it ran once more (D-341). Round 2 cost 4,694,911 tokens: approved, F1 and F2 `fixed`, no new finding.
   - **Context.** The transcript runs from 02:18Z to 17:23Z on 2026-11-07, including the waits for Mat's rulings, and holds 43 summary or compaction records. Each restart re-read the files the next row needed.

2. **What instructions were ambiguous?**
   - **The commit trailer.** The harness asks for a Co-Authored-By trailer, and task H2-5 says the commit has none (`development-lifecycle.md:452`). The draft follows H2-5. Mat's "all recommendations accepted" took it as briefed, so neither commit carries a trailer.
   - **The FP16-outcome brief.** The plan writes it only if S13, the 2-hour box, is reached (`implementation-plan.md:522`). D-239 item 3 sends FP16's outcome back to Mat whenever FP16 can't be made to work. The spike stopped at `done`, with every experiment run and no fix, so D-338 wrote the brief anyway (D-336).
   - **"One new row" for D-335.** It became a Red half (2a) and a Green half (2b), like every other change in the plan. That is form, not scope, and D-335's reasoning says so.
   - **The closure word.** `.agent/templates/REVIEW-TEMPLATE.md:120` gives the Recheck Result column as `✅ Fixed` or `❌ Still open`. The closeout validator closes a finding only on a bare word such as `fixed` (`RECHECK_CLOSED`, `tools/validate_closeout_artifacts.py:82`). So a reviewer who copies the template literally writes a closure that the check can't read.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, again. H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **A plan-time cache probe for E2.** The plan said ORT 1.24.4 and 1.29.0 were in the uv cache (`implementation-plan.md:223`). Offline uv found neither, so E2 is `not_run`, with uv's error: RULE-2.
   - **The literal closure table in the round 3 prompt.** The prompt named the ledger vocabulary and asked for the complete rolling report. It did not spell out the Prior Pass Summary row that closes F1: RULE-1.
   - **Fault cases for the probe's cleanup and a payload check in the smoke.** Neither the plan nor its review asked for them. The execution review found both by probing (F1, F2). Rows C1 and C3 added both as Reds on Mat's D-340 ruling.
   - **An exact file claim in the round 2 prompt.** It said MEU-127 went into `docs/BUILD_PLAN.md`'s phase 3 row. The render changed only the P2 band row and the totals (`BUILD_PLAN.md:67-68`), and the hand-written phase 3 status line (`:47`) doesn't name MEU-127. The reviewer recorded it as clerical, not a finding. The line is left for the next hand edit there, since changing it now would move the bound tree after the gate.

5. **What did you do that wasn't in the prompt?**
   - **Wrote the FP16-outcome brief at `done`** (D-338, D-336).
   - **Filed the execution review's F1 and F2** as `GUI-MODELS-PROBE-LEFTOVER-FILE` and `SMOKE-TTS-WAV-HEADER-TRUSTED` (D-339). Briefed Mat on fixing them before the commit (D-340). Mat ruled fix now, and rows C1 to C4 fixed both (D-342, D-343).
   - **Removed the spike's torch-import block before row 11.** spaCy's `curated-transformers` imports torch while it phonemizes. ONNX Runtime runs without torch either way.
   - **Gave the spike's `run()` dead proxies.** No experiment or overlay child can fetch. The prior environment is kept for E5's one hashed install alone.
   - **Made `_scrub_ready` assert each name on the module before patching.** The first draft of row 2a imported `scrub_home` and failed at import, a setup failure that `red-check.py` refuses: RULE-4.
   - **Decoded each JSON stdout line in the scrub's surface test.** Stdout doubles the backslashes, so the test checks the raw stdout for the user name and the decoded `message` for the `~` path.
   - **Corrected a register sentence after row C5.** The resolve said the online and offline phases refuse 8,000 samples or fewer, but `phase_online` generates nothing. The one `resolution_path` scalar was corrected and checked against what `model.save` writes (`s52-c5-register-fix`), and round 2's prompt disclosed it.
   - **Planned the instructions change Mat asked for during execution.** Every finished execution writes the next session's prompt, and every decision put to Mat runs HDP with a recommendation. The change is made after this reflection, and the Session 53 prompt is its first output. It is the second commit, after Session 52's work.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **Row 9's packaged Red.** The `--phase sentences` smoke ran on a fresh onedir with FP16. 12 of 149 jobs failed with "generated audio must be finite": the shipped defect, in the frozen app. With INT8, the same smoke passed 149 of 149 in row 10 and again in the gate.
   - **Row 1's Red.** A load whose device, format or runtime check failed dropped the loaded model.
   - **Row 2a's Red.** The missing-weight `detail` carried the full home path into the Console and `console.log`.
   - **The probe Red.** The first-run check probed the Electron app-data models folder, not the backend's `~/.avkit/models`, and created that folder.
   - **Row 6's Red.** A fresh install preselected FP16.
   - **Rows C1 and C3's Reds.** The two probe fault cases failed with the leftover file still listed (`s52-120-c1-red`), and the header-only WAV fixture reported 100 samples where the fix reports 0 (`s52-121-c3-red`).
   - **E5.** In all 11 failing pairs, the first non-finite output in graph order is `/decoder/decoder/generator/Div`, the exported `atan2`. Two independent reports name the same node (D-336).
   - **What the tests missed.** The review's two findings came from the reviewer's own fault probes. F1 is the probe leaving its file behind when the write or the access check fails. F2 is the smoke passing a header-only WAV. Rows C1 and C3 turned both into tests.

7. **Which tests were trivially obvious?**
   - AC-119.7 and AC-119.8, the guards that a failure after the unload still leaves nothing loaded on `cpu`. They pin today's behaviour, so they pass by design. They stop a later change from reading `LOAD_KEEPS` as covering every failure (D-325).

8. **Did pyright/ruff catch anything meaningful?**
   - No defect. pyright and ruff passed on every row and in the gate.
   - The one pyright error, in `tools/smoke_packaged_tts.py:734` (`__doc__.splitlines`), is at `HEAD` too (`:611` there). It sits outside the pyright include.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. Each AC named its surface, so the review traced AC-119.1 to AC-121.9 without a question. The exception is E2's cache claim, above.

10. **Was the handoff template right-sized?**
    - Mostly. Deferred Items held every open question as a `decision` row naming Mat and its D-number.
    - The three handoffs repeat the same gate block, once per MEU (`slim_candidate`).

11. **How many tool calls did this session take?**
    - 1778 `tool_use` blocks in this conversation's transcript at row C10, planning, execution and the closeout addenda together: 1283 Bash, 217 Read, 122 Edit, 100 Write, 29 Grep, 17 Pomera web searches, 1 Pomera page read, 8 ToolSearch and 1 Monitor. 1437 of them came before H2-2.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - None. The coordinator ran every row. Codex reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-216 | triage | When are the public RC1 notes corrected, given the uncommitted draft with the DUPER results? | human | Follow D-215. The corrected notes went out on 2026-11-04 from d287c55, before this ruling. The 'your network' wording at docs/releases/v0.1.0-rc.1.md:56-57 waits for the other-network check. D-215 ended with RC1 staying up, so the draft branch does not apply | Human-approved | Publishing is outward and Mat's. The live body still says the build has not run on a clean machine and gives the wrong models path (`known-issues.yaml:3613`). | USER_EXPLICIT 2026-11-04 'All ohter recommendations are accepted' |
| D-221 | triage | How does a failed load keep the current model? | autonomous | Check weight path, device and runtime before unload_model. No load-before-unload. Test: load A, fail a load of B, status still shows A | Local Canon | The packaged build is CPU ONNX, so the GPU-memory question in the issue does not arise there. A failure after those checks can still drop the model, and the plan must state that limit (`known-issues.yaml:3571`). Two-way. | — |
| D-222 | triage | Which models folder is right, and what changes? | autonomous | The backend default ~/.avkit/models stands. setup-readiness.ts probes that same default and stops creating an empty folder. No files move. A contract test ties the two defaults together | Local Canon | Moving the default would strand files users already hold, 534 MB on the test PC. Two defaults are what drifted, so the test covers the cause (`known-issues.yaml:3627`). Two-way. | — |
| D-239 | triage | Which model does a fresh install preselect while ONNX FP16 fails on some ordinary sentences? | human | ONNX INT8 or ONNX FP32 until the cause is known. INT8 is the working choice, as the smallest file with the least memory. Mat listens to it first | Human-approved | A user who keeps the preselected model should not hit a failure on an ordinary sentence. INT8 and FP32 had no failures in the 2026-11-04 probe; INT8 is 92 MB against 326 MB (`known-issues.yaml:4034`). Mat's D-331 picked INT8 at this session's plan gate. | USER_EXPLICIT 2026-11-04 'All ohter recommendations are accepted' |
| D-240 | grouping | Where does session numbering start? | autonomous | 49 | Local Canon | Starting at 49 reuses no number. Two-way. | — |
| D-241 | grouping | Are the transcript title and channel name two MEUs? | autonomous | One, MEU-122 | Local Canon | Same enumeration, change and test fake. Two-way. | — |
| D-242 | grouping | Where do the riders go? | autonomous | By shared file | Local Canon | A rider needs a session already working in that file. Session 51 carried none. Two-way. | — |
| D-243 | grouping | Does rc.2 get its own MEU? | autonomous | Yes, MEU-125 | Local Canon | MEU-110 is approved and closed. Reopening it would hide the new gate, which repeats this session's capability smoke (D-315). Two-way. | — |
| D-244 | grouping | Which session runs first? | autonomous | Fetch and uninstall, Session 49 | Local Canon | It's the smallest, and MEU-125 reuses its round-trip script. Two-way. | — |
| D-245 | grouping | Is TTS one session or two? | autonomous | Two, Sessions 51 and 52 | Local Canon | The FP16 cause hunt has no upper bound and shouldn't hold the download refusal. Session 51 is the first of the two and carries this row. Two-way. | — |
| D-246 | grouping | Where does the FFmpeg build run, and where does the rebuilt archive live? | human | Withdrawn: no build runs | Human-approved | Mat kept FFmpeg as it is (D-266). | USER_EXPLICIT 2026-11-04 "FFmpeg, keeping libdvdcss in rc.2: yes" |
| D-247 | grouping | Do errors always go to a file? | human | Yes: errors always go to a file. Session 50's plan carried it out | Human-approved | It changes a default the user sees, so it was Mat's to rule. D-296 carried it out. | USER_EXPLICIT 2026-11-05 "D-247: yes they should go to file" |
| D-248 | grouping | Does Mat's "Proceed" confirm the grouping for the D-234 scoping review? | autonomous | Yes, with the §3 changes listed for Mat to check | Local Canon | Waiting would stop work Mat asked to go ahead, and the grouping stays reversible. Two-way. | USER_EXPLICIT 2026-11-04 "All ohter recommendations are accepted. Proceed" |
| D-249 | grouping | Does the light accent stay in MEU-118? | autonomous | No: its own MEU-126 in Session 56, optional for rc.2 | Local Canon | Scoping review F1: a separate cause, separate tests and a separate human check, sharing no file with the device select. MEU-118 here is the device select alone. Two-way. | — |
| D-250 | grouping | Does Batch E stay one session? | autonomous | No: MEU-123 in Session 54 and MEU-124 in Session 55 | Local Canon | Scoping review F2: they share no file. Two-way. | — |
| D-267 | grouping | Do the two remaining fixes stay in one session now they share no file? | autonomous | Yes, Session 49 keeps MEU-113 and MEU-114 | Local Canon | Each is a few lines, and a second plan and review would cost more than they save. Two-way. | — |
| D-277 | grouping | Does Codex recheck the grouping after round 1's fixes? | human | No. The scoping loop stays `changes_required`, recorded as not rechecked | Human-approved | Both findings were session splits, and both were applied. Each session's plan review covers its own scope, as this one's did. | USER_EXPLICIT 2026-11-05 "all recommendations are accpeted, proceed" |
| D-280 | grouping | Does the tooling session get an MEU? | autonomous | No: Session 49b is tracked by its issue | Local Canon | MEUs are build-plan product work, and Session 49b ships nothing. Two-way. | — |
| D-322 | planning | In what order does load_model check, and where does its runtime check read? | autonomous | Weight, device probe, format, then runtime through self.runtime_present (MEU-117's memo), all before unload_model; then build and assign as today | Local Canon | The format check has no side effects, so it moves up with the others and AC-119.5 keeps A on an unsupported format. Reading runtime_present adds no second probe. Doing nothing keeps the unload first, and any failed check drops A (`implementation-plan.md:530`). | — |
| D-323 | planning | What does load_model do when the runtime probe raises? | autonomous | Raise ModelLoadError('TTS runtime probe failed') from the error, and log one tts.load_failed on the target with the cause's class and no detail | Local Canon | runtime_imports never raises, so only an injected probe reaches this; it must still not escape bare (adapter.py:308). LOG_CAUSE's detail would carry the probe's raw text, which can hold a path (`implementation-plan.md:540`). | — |
| D-324 | planning | How are the two kokoro-import tests (:739, :855) handled once the runtime check runs before the unload? | autonomous | A′: _adapter gains an optional runtime_probe argument and both tests pass lambda _fmt: True; every assertion stays | Local Canon | The setup change keeps the in-load import path pinned. A2 amends the assertions and loses that coverage; B repeats what the runtime check proves and changes both tests' assertions; doing nothing leaves the adapter without a runtime check (`implementation-plan.md:550`). | — |
| D-325 | planning | What is said about a failure after the unload? | autonomous | It still leaves nothing loaded on cpu; the docstring says so, and AC-119.7, AC-119.8 and the A′ tests pin it | Local Canon | The limit is Mat's (D-221). Stating it in the docstring and pinning it with tests stops a later change from reading LOAD_KEEPS as covering every failure (`implementation-plan.md:560`). | — |
| D-326 | planning | Where does the first-run check get the backend's default? | autonomous | A DEFAULT_MODELS_DIRECTORY constant in setup-readiness.ts, '~/.avkit/models', expanded by expandUserPath; a stored value still wins | Local Canon | The readiness probe runs in the main process, also when the backend is down, so asking the backend over HTTP would leave it without an answer then. A constant tied by a contract test is the smallest change (`implementation-plan.md:570`). | — |
| D-327 | planning | What does the probe report when the models folder doesn't exist yet? | autonomous | B: the transient write-and-delete probe in the nearest existing ancestor folder; a file on the way reads false; no folder is created | Local Canon | Creating the folder needs write access to its nearest existing parent, and the same probe tests exactly that. A, accessSync alone, doesn't read Windows ACLs; C shows every fresh install as not ready (`implementation-plan.md:580`). | — |
| D-328 | planning | Where does the contract test that ties the two defaults live? | autonomous | In setup-readiness.test.ts: Vitest reads settings.py and matches the tts.models_directory SettingSpec against DEFAULT_MODELS_DIRECTORY | Local Canon | The constant being tested is on the TypeScript side, so its test reads the Python default as text. A generated shared constant would add a build step for one string (`implementation-plan.md:590`). | — |
| D-329 | planning | Does engine.py stay in this session's scope? | autonomous | Yes, read-only: AC-121.1 builds the fresh-install catalog from its SEED_VARIANTS | Local Canon | A fresh install's preselection depends on which rows are seeded and in what order. Reading the seed keeps AC-121.1 true if the seed changes; dropping it would leave a hand-written catalog in the test (`implementation-plan.md:600`). | — |
| D-330 | planning | How does the fallback rank rows, and what if only FP16 is downloaded? | human | Runnable rows ranked by PRESELECT_ORDER, the rest after them in catalog order; first downloaded of that list, else its first; only FP16 downloaded keeps FP16 | Human-approved | Ranking keeps the first-downloaded rule, so a user with a working download isn't shown a model that needs one. INT8 even when not downloaded would preselect a model that must be fetched first, on every launch (`implementation-plan.md:610`). | USER_EXPLICIT 2026-11-07 'D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed' |
| D-331 | planning | Which model does a fresh install preselect, ONNX INT8 or ONNX FP32? | human | INT8: PRESELECT_ORDER = ['kokoro-onnx-int8', 'kokoro-onnx-fp32']; row 6's Red encodes INT8; rows 9 and 10 and the gate smoke the pinned model_quantized.onnx | Human-approved | Asking at the gate means the Red, the Green and the smoke all follow one verdict. INT8 is 3.5 times smaller and uses 240-315 MB less peak memory; FP32 is closer to the reference (`implementation-plan.md:621`). | USER_EXPLICIT 2026-11-07 'D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed' |
| D-332 | planning | Where does the packaged check run? | autonomous | Here, as --phase sentences on a fresh local onedir with FP16 as the Red, and again in the session gate; MEU-125's rc.2 gate repeats it on the installer's copy | Local Canon | Done names a packaged build, and the onedir is what the installer wraps. Running FP16 first proves the check catches the failure. Leaving it to MEU-125 alone would close this session without its Done (`implementation-plan.md:632`). | — |
| D-333 | planning | What is the spike's box, what does it try, and when does the FP16 issue close? | human | 2 hours from the first spike JSON; E0 to E4 from local files; E5 last, with onnx==1.23.2 and ml-dtypes==0.6.0 installed with --no-deps --require-hashes into a Temp target; no fix inside the box; the issue closes only on a cause plus Mat's approval of a re-reviewed amendment, or on Mat's ruled outcome | Human-approved | The hunt has no upper bound. Two hours covers about ten full FP16 passes. A fix would change the adapter, so it needs its own Red and review. Mat ruled E5 yes, because only E5 says which node first goes non-finite (`implementation-plan.md:642`). | USER_EXPLICIT 2026-11-07 'D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed' |
| D-334 | planning | Which checks does the session gate run? | autonomous | Session 51's gate with smoke-sentences in place of smoke-capability; the MCP suites stay as guards; mcp-audit, build-record and smoke-capability are skipped with reasons | Local Canon | The MCP suites are cheap and catch an API change nobody planned. The capability smoke checks a refusal MEU-119 doesn't reach, and MEU-125 repeats it (`implementation-plan.md:653`). | — |
| D-335 | planning | The missing-weight tts.load_failed detail carries the full weight path, so the Windows user name reaches console.log: fix it where, or keep it? | human | HOME_SCRUB: console_field replaces the home folder with ~ before the URL, redaction and length rules; rows 2a (Red) and 2b (Green) with AC-119.10; the six log sites, REDACT_NEEDLES and AC-115.9's assertions stay unchanged | Human-approved | Every Console field passes through console_field, so one change covers the missing-weight line and the five other events whose text can hold a home path. Fixing the one line would leave the rest; keeping the path leaves the user name in every pasted log (`implementation-plan.md:663`). | USER_EXPLICIT 2026-11-07 'D-331 INT8, D-335 scrub, E5 yes, D-330 keep, proceed' |
| D-336 | execution | What happens to ONNX FP16, now that the spike has found where it fails? | human | Keep FP16 as shipped (offered, never preselected while INT8 or FP32 can run); TTS-ONNX-FP16-NONFINITE-AUDIO stays open with the failure site; MEU-127 svc-tts-fp16-phase-guard takes a guarded phase computation, spike first; nothing is posted to discussion 22 | Human-approved | E5 and two independent reports (HF discussion 22, sherpa-onnx 4086) put the failure in the exported atan2's Div at /decoder/decoder/generator/Div, so a fix is targeted and the 149-job smoke is its Red and Green. Hiding FP16 reverses D-239 just as the cause is located. Brief and ruling in closeout-decisions.md. | USER_EXPLICIT 2026-11-07 'all recommendations accepted' |
| D-337 | execution | The home-folder scrub doesn't match an 8.3 short form of the home folder: fix it, or keep it? | human | scrub_home also matches the short form, in a row of its own with a Red, in a later plan; row C5 files it as CONSOLE-HOME-SCRUB-SHORT-FORM | Human-approved | One change at console_field covers every Console detail and changes no stored setting. A long-form read covers only the models folder and follows junctions. Doing nothing keeps a known way for part of the user name to reach the Console, which Session 50's rule says is fixed or raised, never kept. Brief and ruling in closeout-decisions.md. | USER_EXPLICIT 2026-11-07 'all recommendations accepted' |
| D-338 | execution | The spike stopped at done (every experiment ran, no cause) and not at S13's 2-hour box. Is the FP16-outcome brief still written for Mat? | autonomous | Yes: D-336 in closeout-decisions.md is the FP16-outcome brief; the issue stays open and gets no --decision-issue flag | Local Canon | D-239 item 3 (`known-issues.yaml:4011`) sends FP16's outcome to Mat whenever FP16 can't be made to work, and the plan's 'only if S13' (`implementation-plan.md:522`) assumed the box would be the stop. A brief authorizes nothing, so writing it is two-way. | — |
| D-339 | closeout | How are the execution review's two non-blocking findings recorded: F1, the models probe's leftover file, and F2, the smoke's header-only WAV? | autonomous | File both, open, medium and P3: GUI-MODELS-PROBE-LEFTOVER-FILE and SMOKE-TTS-WAV-HEADER-TRUSTED, each listed under its handoff's Deferred Items; fixing them before the commit is Mat's (D-340) | Local Canon | D-200 (`2026-11-03-release-rc1-reflection.md:115`) filed a non-blocking note so the reviewer's result isn't lost. D-289 (`2026-11-05-closeout-register-grammar-reflection.md:96`) sent fix-now to Mat, and a round 2 needs a ledger continue. Neither finding puts a raw value in a log. | — |
| D-340 | closeout | Fix the execution review's two non-blocking findings before the commit, or keep them filed? | human | Fix both now (rows C1 to C4) after a continue of 10,000,000 tokens recorded at 2026-11-07T16:34:19Z, then a fresh gate (C6) and a round-2 recheck scoped to F1 and F2 (C8) | Human-approved | Both are in code this session wrote, and each fix is a few lines plus a test. D-289 is the same question, which Mat answered "Fix it now". Linking them to MEU-125 adds unrelated work to the release gate; doing nothing leaves F2's check able to pass a header-only WAV. Brief and ruling in closeout-decisions.md. | USER_EXPLICIT 2026-11-07 'all recommendations accepted' |
| D-341 | execution | Gate run 2 sees files that session-gate.ps1's allowed set refuses: the new tooling test, the matrix and the files of Mat's instruction change. Which tree does it test? | autonomous | Add those files to the allowed set (row C6), so the gate tests the tree both commits hold; ui/tests/e2e/test-ids.ts stays refused | Local Canon | A gate that refused them would fail on the tree the commits hold, and one that dropped them would test a tree that never exists. Widening the set by name keeps scope-paths refusing everything else. Two-way. | — |
| D-342 | execution | How does the probe remove a file that a failed write or access check leaves behind (review F1)? | autonomous | Name the probe path before the try; in the catch, rmSync(probe, { force: true }) inside its own try, then return false; the success path keeps its unlinkSync | Local Canon | A finally would also run after the success path's unlinkSync, so the catch is the one place a leftover can exist. force: true makes a write that never created the file a no-op, and the inner try keeps a failed removal from turning false into a throw. Two-way. | — |
| D-343 | execution | How does the smoke stop trusting a WAV header's frame count (review F2)? | autonomous | In _generate, read the declared frames and the payload; wav_samples is the declared count only when the payload holds every declared frame, else 0; wav_declared keeps the header's count | Local Canon | Reporting 0 for an incomplete file lets both phases' existing acceptance refuse it, so no acceptance changes. wav_declared keeps the header's claim in the JSON, so a failure shows what the header said. Two-way. | — |
| D-344 | closeout | Session 52's new and changed files name the home folder in full in a few lines, as 56 tracked files already do. Are they rewritten before the commit? | human | Commit Session 52's files as they are and file TRACKED-FILES-HOLD-HOME-PATH for the next triage | Human-approved | The repository is public and its old history keeps every earlier instance, so a rewrite here limits new exposure only, and it would change a plan review kept byte for byte. One issue for all 56 files lets a later plan fix them together with a check that keeps them out. | USER_EXPLICIT 2026-11-07 'all recommendations accepted' |
| D-345 | closeout | Where is D-336's follow-up registered? | autonomous | MEU-127 svc-tts-fp16-phase-guard: phase 3, band P2, matrix row 3.18, depends on MEU-121, with 03's FP16 phase guard section and MEU-127 in TTS-ONNX-FP16-NONFINITE-AUDIO's meu_links | Local Canon | The fix is in the TTS service's model graph, Phase 3, like the MEU-122 residual before it. Linking the issue to the MEU shows the next triage that the open issue has an owner. Two-way. | — |

---

## Pattern Extraction

### Patterns to KEEP
1. **A packaged Red on the shipped behaviour.** The 149-job smoke on FP16 failed 12 jobs on a fresh onedir, and INT8 passed 149 of 149 on the same build (D-332).
2. **A bounded spike with a closing rule and a network guard** (D-333). It located the failing node before the box ran out. Its findings went to Mat as a brief, not as a fix.
3. **Asking every gate question in one message, each with a recommendation and a do-nothing option.** Mat ruled all four plan-gate questions in one line. D-336, D-337 and D-340 are briefed the same way.
4. **A snapshot of the real models folder after each row that could touch it.** It found 0 changes after rows 5, 9, 10 and 11.

### Patterns to DROP
1. **Leaving the closure table to the reviewer in a recheck prompt.** Round 4 cost 2,247,602 tokens for one table row.

### Patterns to ADD
1. **A recheck prompt spells out the Prior Pass Summary row with a bare closure word.**
2. **A plan that relies on a cached artifact probes the cache offline when it is written.**
3. **When a review loop opens, check its budget against the last comparable round,** and ask Mat about a grant at the gate. A grant on one loop doesn't carry to the next.
4. **A test that patches a module name asserts the name exists first.**

### Calibration Adjustment
- **Estimated time:** the grouping gave no session estimate. The plan boxed the spike at 2 hours (D-333).
- **Actual time:**
  - About 15.1 hours of transcript time, 2026-11-07T02:18Z to 17:23Z, including the waits for Mat's rulings.
  - The spike stopped at `done` inside its box. Each 149-job smoke took about 3 minutes.
  - The plan review cost 22,860,314 tokens over four rounds. The execution review cost 14,996,767 tokens in round 1 and 4,694,911 in round 2.
- **Adjusted estimate for a three-MEU session with a packaged smoke and a spike:** a full day.
  - Budget 12M tokens for the first plan round, 15M for the execution round, and 2M to 7M for each recheck.
  - Ask Mat at the plan gate for the execution loop's budget whenever the first plan round costs more than half its loop.

---

## Next Session Design Rules

```
RULE-1: A recheck prompt gives the reviewer the literal Prior Pass Summary table, with a bare closure word (fixed, resolved, closed) in the Recheck Result column for each prior finding it closes.
SOURCE: Plan round 3 approved without that table, so --approved-state-only still counted round 2's F1 as open and blocking; round 4 (2,247,602 tokens) only added '| F1 | open | fixed |'. RECHECK_CLOSED (tools/validate_closeout_artifacts.py:82) reads bare words only, so REVIEW-TEMPLATE.md:120's '✅ Fixed' would not close it either.
EXAMPLE: "close F1 in your recheck" → "your section holds '| Finding | Prior Status | Recheck Result |' with '| F1 | open | fixed |' if F1 is fixed".
```

```
RULE-2: A plan that relies on a cached wheel, model or file probes it offline when the plan is written, and cites the receipt.
SOURCE: E2 is not_run: the plan said ORT 1.24.4 and 1.29.0 were in the uv cache (implementation-plan.md:223), and offline uv found neither.
EXAMPLE: "both are in the uv cache" → "uv's offline dry run resolves onnxruntime==1.24.4 and 1.29.0 (s53-cache-probe.txt)".
```

```
RULE-3: When a review loop opens, the coordinator compares its budget with the last comparable round's cost, and asks Mat at the gate for any grant the loop needs. A grant on one loop does not carry to another.
SOURCE: Mat's +50M and two rounds went on the plan loop; the execution loop opened on its default 21M, round 1 cost 14,996,767, and the ledger refuses round 2 until Mat continues it (D-340).
EXAMPLE: "begin the execution loop" → "plan round 1 cost 11.4M; ask Mat at the gate whether the execution loop gets more than its default 21M".
```

```
RULE-4: A test that patches a module's new name asserts the name exists first, so its Red fails by assertion and not at import.
SOURCE: Row 2a's first draft imported scrub_home from services.health and failed with ImportError, a setup failure red-check.py refuses.
EXAMPLE: "from avkit_core.services.health import scrub_home" → "assert hasattr(health, 'scrub_home'), then monkeypatch the module attribute".
```

---

## Next Day Outline

1. **Target:** done. Mat ruled D-336, D-337, D-340 and D-344 with "all recommendations accepted", and said "commit and push". Session 52's work is the first commit and the instruction change the second, both on `main`.
2. **Next session:** Session 53 `transcript-metadata` (MEU-122), per the grouping. Its prompt is `C:/Temp/av-kit/session-53-prompt.md`.
3. **Scaffold changes needed:** none open. Mat's request (every finished execution writes the next session's prompt, and every decision put to Mat runs HDP with a recommendation) is the second commit.
4. **Patterns to bake in from today:** RULE-1 to RULE-4 here, Session 51's RULE-1 to RULE-4, and Session 50's rules, all of which carried.
5. **Codex validation scope:** Session 53's plan.
6. **Time estimate:** Session 53 is one MEU on the transcript service, so half a day. Mat still has the Transcript check from another network.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | 1778 in this conversation's transcript at row C10 (1437 at H2-2), planning, execution and the addenda |
| Time to first green test | 2026-11-07T13:57:23Z (08:57 local), row 2b's scrub Green (`s52-scrub-green.txt`) |
| Tests added | pytest 1274 → 1296 (+22); Vitest 1163 → 1174 (+11, 112 files); MCP 470 → 470; Electron targeted specs 46 of 46 |
| Codex findings | Plan review: R1 approved, no findings, 11,373,866 tokens; R2 changes_required, F1 High, 7,353,486; R3 approved, F1 resolved, 1,885,360; R4 approved, closure table only, 2,247,602. Execution review: R1 approved, F1 and F2 Medium and non-blocking, 14,996,767; R2 approved, F1 and F2 `fixed`, no new finding, 4,694,911 |
| Handoff Score (X/7) | 6/7. Every AC has evidence, and the gate passed on run 1 and again on run 2 after the fixes, with nothing excused. E2 is not_run |
| Rule Adherence (%) | 88 (6 of 8 sampled rules followed in full, 2 in part; 1 more was not triggered) |
| Prompt→commit time | Planned, executed and committed on 2026-11-07, on Mat's "commit and push" |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Every Red failed by assertion, and `red-check.py` named the failing tests before each row was marked |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Both canonical reviews are Codex's reports, validated under `C:/Temp/av-kit` and copied byte for byte |
| A raw value that can reach a log, stdout or the Console is fixed in the row or raised | Session 50 rule; the brief | Yes. The home path is scrubbed (D-335), the 8.3 form is raised (D-337), and no residual records a raw value |
| A row that edits a byte-hashed file runs its hash test | Session 50 rule; the brief | Not triggered. No row edited `ui/tests/e2e/test-ids.ts` |
| Every command through RTK | AGENTS.md §RTK | Partly. Test, build and tool runs went through `rtk proxy`. Many reads and probes did not, and the RTK hook isn't installed on this PC |
| The review prompt names the ledger vocabulary and asks for the complete rolling report | Session 49b D-290; the brief | Partly. Every prompt did, but round 3's left out the literal closure table (RULE-1) |
| No branches or worktrees; never commit or push without the human | AGENTS.md §Commits | Yes. Nothing was committed or pushed before Mat's "commit and push", and both commits are on `main` |
| Preserve line endings | memory; the AC-51.6 byte hash | Yes. CRLF files stay CRLF and LF files stay LF, measured in bytes |
| Decision briefs keep a do-nothing option | the brief; HDP | Yes. D-336, D-337 and D-340 each list one |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "abbc0ef8-f081-41d1-93f1-e6e0070c4fb8"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 3}
  - {id: planning_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: commits, cited: true, influence: 3}
  - {id: validation_pipeline, cited: true, influence: 3}
  - {id: rtk_token_optimized_commands, cited: true, influence: 1}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, plan_critical_review, execution_session, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/human-decision-protocol.md
    - .agent/docs/harness-profiles.md
    - .agent/docs/commands.md
    - .agent/schemas/review-verdict.schema.v2.json
    - .agent/schemas/reflection.v1.yaml
    - .agent/templates/REVIEW-TEMPLATE.md
    - docs/execution/reflections/TEMPLATE.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:human-decisions-stay-human, P0:raw-values-fixed-or-raised, P1:independent-review-no-self-approval, P1:tests-before-production-code]
conflicts:
  - "The harness asks for a Co-Authored-By trailer on commits; task H2-5 says no AI attribution trailer. Neither commit has one, as briefed and accepted."
  - "REVIEW-TEMPLATE.md:120 gives the closure as '✅ Fixed'; the closeout validator closes a finding only on a bare word such as 'fixed'."
  - "Connected docs servers offered to publish deliverables; the user's rule keeps them as local repo files."
note: "A failed load keeps the model; the probe reads ~/.avkit/models and creates nothing; a fresh install preselects INT8 (149/149); FP16 first goes non-finite at generator/Div."
slim_candidate: ["The three handoffs repeat the same Quality Gate Results block; one block in the first handoff, linked from the other two, would say the same."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 4, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 0, medium: 0, low: 0}
    - {review: plan, round: 2, critical: 0, high: 1, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: plan, round: 4, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 2, low: 0}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {boundary_validation: 1, weak_test: 1, other: 1}
  verdicts: {approved: 5, changes_required: 1}
meu_work_classes: [correctness, correctness, mixed]
```
