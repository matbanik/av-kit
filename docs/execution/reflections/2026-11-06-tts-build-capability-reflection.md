---
date: "2026-11-06"
project: "tts-build-capability"
meus: ["MEU-117", "MEU-118"]
plan_source: "docs/execution/plans/2026-11-06-tts-build-capability/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-06 Meta-Reflection

> **Date**: 2026-11-06
> **MEU(s) Completed**: MEU-117 `svc-tts-build-capability` and MEU-118 `gui-tts-device-options`. Session 51 closes TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME and TTS-DEVICE-OPTIONS-IN-CPU-BUILD; D-237 (no espeak) still binds
> **Plan Source**: `docs/execution/plans/2026-11-06-tts-build-capability/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **Gate run 1.** It failed at `ui-tests` on one test, AC-118.2 "a CUDA report offers auto, cuda and cpu". The select still listed `auto, cpu`, the list from before the report arrives. TanStack Query notifies its observers on a `setTimeout(0)`, and the test's setup sync, `settled()`, waited only a microtask after it saw the new state, so the assertion could run before the page re-rendered. Row 11's full suite had passed. The fix waits for a `setTimeout(0)` inside `act` and changes no assertion and no source file. The file then passed 15 runs of 15, the full UI suite passed twice, and the whole gate ran again: RULE-1.
   - **The register resolve.** The first `issue-resolve.py` dry run refused with ".issues[82]: keys differ", because `TTS-DEVICE-OPTIONS-IN-CPU-BUILD` had no `resolution_path` to replace. The plan-local script gained `set_fields`, which adds a missing key before `category`, and a dry run to `--target` passed before the real write: RULE-2.
   - **Context.** The conversation was compacted 25 times in about 3.4 hours, and each restart re-read the files the next row needed.

2. **What instructions were ambiguous?**
   - The harness asks for a Co-Authored-By trailer, and task H2-5 says the commit has no AI attribution trailer. The draft follows H2-5, and I raise the conflict with Mat before any commit.

3. **What instructions were unnecessary?**
   - The `07-distribution.md:30` and `:227` correction. The brief was written from the triage, before commit 83229ea changed both lines, so row 4 only re-checked them (D-319).
   - H2-1's source read. H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **A setup sync that matches the query library.** `settled()` assumed a microtask was enough. RULE-1.
   - **Key coverage for the register write.** Nothing in the plan probed whether both issues held the keys the resolve replaces. RULE-2.
   - **Current line citations.** Three plan citations had moved or weren't there: `_DEVICE_ORDER` is at `adapter.py:71`, not `:67`; 03's anchor became `adapter.py:340-350`, not `:298-308`; and the `settings.test.ts:297` and `:304` device lookups that AC-118.5 cites don't exist. Each handoff discloses its own. RULE-3.
   - **The user-level git ignore in the identity question.** Codex's sandbox doesn't read `~/.config/git/ignore`, so its `identity.py --state-only` counted `.claude/settings.local.json` and gave another value. The reviewer wrote a probe to reconcile it. RULE-4.

5. **What did you do that wasn't in the prompt?**
   - Added `set_fields` to the plan-local `issue-resolve.py` (above).
   - Gave `installSettingsSeam` an `options.device` beside the plan's `options.catalog`, so the AC-118.5 test can seed a stored `cuda`.
   - Corrected the MEU-117 handoff's register-resolve note after the review's Q8 showed it named the wrong issue for `.issues[82]`.
   - The shared `CONFLICT_409` text also describes the `/models/load` 409, so the OpenAPI diff changed two 409 descriptions as well as the download's. All three stay within the §Spec text, and the MEU-117 handoff discloses it.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **AC-117.15's Red on the pre-session onedir.** The new `--phase capability` ran on the 2026-11-04 build and stopped at `listed_fields`, with no `available` field on any row, before any download request. That is the shipped defect in the frozen app, where torch is absent for real. The same phase passed on a fresh build.
   - **Row 3's service Red.** Loading `kokoro-pt-fp32` gave `ConflictError('tts asset missing: tts_onnx_vocab')`, which tells the user to fetch an asset for a model that can't run. D-311 puts the reason first.
   - **Row 5's renderer Red.** The PyTorch option was enabled as "PyTorch FP32 — downloaded", and `defaultModelSelection` chose it.
   - AC-118.2 in gate run 1 caught a race in the test's own setup, not in the product.

7. **Which tests were trivially obvious?**
   - AC-117.11, the guard that the MCP descriptions keep their four markers. It passes by design and protects them from a later edit.

8. **Did pyright/ruff catch anything meaningful?**
   - No defect. pyright and ruff passed on every row and in the gate. The one pyright error in `tools/smoke_packaged_tts.py:414` is at `HEAD` too, outside the pyright include.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. Each AC named its surface, so the review traced AC-117.6 to AC-117.9 from the service through the route to MCP without a question. The three stale citations above are the exception.

10. **Was the handoff template right-sized?**
    - Yes. The execution notes held every deviation, and after the review only its two Q8 notes were added.

11. **How many tool calls did this session take?**
    - 981 `tool_use` blocks in this conversation's transcript at H2-2, planning and execution together: 773 Bash, 124 Read, 41 Write, 32 Edit and 25 Grep.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - None. The coordinator ran every row. Codex reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-217 | triage | What does a build that cannot run PyTorch do with the PyTorch model? | human | List it disabled with a reason in any build that can't run it, refuse its download with a 409, and correct `07-distribution.md:30` and `:227`. No runtime download and no bundled torch. `npm run dev` keeps working | Human-approved | Mat chose this after asking what PyTorch adds over the three ONNX variants: the same Kokoro-82M model, about 1.5x on this PC's CPU, and no PyTorch-only feature. Disabled with a reason follows D-70 and leaves an explanation beside a file RC1 testers already hold. It reverses D-236. | USER_EXPLICIT 2026-11-04 'OK we will go with pythorch remove as you originally suggested' |
| D-226 | triage | Which device options does a CPU build offer? | autonomous | Only what the backend reports for this build, from the same capability source as D-217. A stored value it cannot honour keeps the existing device fallback | Local Canon | Two lists of what a build can do would drift, as the models folder did. Whatever D-217 rules, this stands. Two-way. | — |
| D-236 | triage | Does the installed app get a download for the PyTorch runtime and what it needs? | human | Superseded by D-217 on 2026-11-04, not built | Human-approved | Mat first asked for the download to be filed, then chose to keep PyTorch out of installed builds. The filing recorded a direction, not an approved plan. | USER_EXPLICIT 2026-11-04 'also make the download avilable in settings will all other dependencies that needs to be also filed as an issue and be part of the triage' |
| D-237 | triage | Does 'all other dependencies' include espeak: the GPL library that kokoro imports, and the eSpeak NG program? | human | No to both. espeak is never downloaded or bundled, and the eSpeak NG row stays install guidance | Human-approved | Taken literally, the request pulls GPL code into the backend process of an MIT app, against D-61. With no runtime download, the question doesn't arise. This session imports nothing new. | USER_EXPLICIT 2026-11-04 'All ohter recommendations are accepted' |
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
| D-309 | planning | How does the backend decide whether a variant can run in this build? | autonomous | `runtime_imports(fmt)` in the adapter: ONNX is True; PyTorch is False when torch is None, without importing kokoro, else True when `from kokoro import KModel` succeeds and False with a class-name-only WARNING when it raises; memoized per format under a lock and exposed by the port as `runtime_present` | Human-approved | Importing KModel is the test the load itself runs, so the list and the load can't disagree. `find_spec` would miss a native DLL failure. Probing at startup would add about 3 s to every dev start. A packaged build has no torch, so it returns before any kokoro import and AC-72.1 holds. | USER_EXPLICIT 2026-11-04 'OK we will go with pythorch remove as you originally suggested' (D-217) |
| D-310 | planning | What does an unavailable variant say, and in what form? | autonomous | A fixed text per format in `MODEL_REASONS`; PyTorch says "This build can't run PyTorch models. Choose an ONNX model."; `ModelAvailability(available, reason)` carries it, the reason set exactly when the variant is unavailable | Local Canon | The same words reach the list, the 409, the 422, the log and MCP, and only text survives all five. A closed code with a renderer map would leave the 409, the 422 and MCP without words. The texts never hold exception text, so nothing raw reaches a log. Mat accepted the texts at the plan gate. | USER_EXPLICIT 2026-11-06 'proceed' |
| D-311 | planning | Where and in what order are the download and the load refused? | autonomous | `ModelService.availability(fmt)`; the download warms the probe before its lock, keeps the in-flight 409 and NotFoundError first, then raises `ConflictError(reason)` before `_start_locked`; the load raises `ModelLoadError(reason)` after NotFoundError and before the legacy and vocab checks; each logs one WARNING | Human-approved | Refusing in the service covers the route and MCP at once, and refusing before `_start_locked` means no thread and no file. Warming outside the lock keeps a 3 s first import from holding it. Refusing in the route would leave the service open to other callers. | USER_EXPLICIT 2026-11-04 'OK we will go with pythorch remove as you originally suggested' (D-217) |
| D-312 | planning | Does the adapter's own load error say the same reason? | autonomous | Option A: the adapter raises `MODEL_REASONS[PyTorch]` where it said "PyTorch runtime is not bundled"; the two AC-98.5 tests and AC-115.9's last block are amended; "PyTorch model failed to load" stays | Local Canon | One text on every path keeps the log's detail and any direct caller in step with the API. Option B, doing nothing in the adapter, is safe through the API but leaves a second wording for one cause. Mat accepted A at the plan gate. | USER_EXPLICIT 2026-11-06 'proceed' |
| D-313 | planning | Where does the Settings device select get what the backend reports? | autonomous | From the catalog: `buildDevices` joins `DEVICE_FLOOR` with the devices of every row whose `available` isn't false, kept to `DEVICE_ORDER`, in `tts-devices.ts` | Local Canon | The catalog's devices and available fields are the capability source the residual names, so a second route would be a second copy of the same answer. Doing nothing keeps cuda and mps on a CPU-only build. Mat accepted `/models/available` as the source at the plan gate. | USER_EXPLICIT 2026-11-06 'proceed' |
| D-314 | planning | What does the Settings select show before the report arrives, and for a stored value the build can't honour? | autonomous | Pending or failed: `DEVICE_FLOOR` plus the stored value; after the report, a stored value that isn't offered shows as auto and nothing is written; choosing writes once as today; `TTS_DEVICES` goes | Local Canon | Showing the stored value while the report loads avoids a flash of auto that looks like a change. Not writing auto keeps the user's choice for a later build that can use it. Sharing the TTS page's query means one fetch per cache window. | — |
| D-315 | planning | Does the packaged smoke that checks the 409 run here or at MEU-125's rc.2 gate? | autonomous | Here: `--phase capability` in `tools/smoke_packaged_tts.py`, Red on a copy of the 2026-11-04 onedir, Green on a fresh build copied outside the checkout, offline on stub files; MEU-125 repeats it at rc.2 | Local Canon | The Done line is about an installed build, and the frozen app is where torch is absent for real. A onedir build needs no installer and no network. Waiting would leave the Done line unproven for a whole session. | — |
| D-316 | planning | How is 'the dev venv still loads and generates' checked, and how is the real models folder protected? | autonomous | `dev-pytorch-check.py` runs the backend as `npm run dev` does, offline, with the real models folder, and loads and generates with `kokoro-pt-fp32`; `models-snapshot.py` records the folder at row 0 and compares it after rows 2, 4, 9 and 12 and in the gate | Human-approved | Running the backend as Electron does proves the dev path without a window. Offline mode and the fast path mean the check writes no file, and the snapshot proves it. A manual app launch would prove the same with no receipt. | USER_EXPLICIT 2026-11-04 'OK we will go with pythorch remove as you originally suggested' (D-217) |
| D-317 | planning | What does the TTS page's own device fallback read? | autonomous | `selectedModel?.devices ?? DEVICE_FLOOR`, the shared constant in place of the literal; the behaviour doesn't change | Local Canon | The page already reads the selected model's devices, so only its fallback names the floor. One constant keeps Settings and the page from drifting. | — |
| D-318 | planning | What changes in MCP? | autonomous | Only the available and download descriptions, as explicit entries that keep the four markers; the JSON and the 409 already pass through | Local Canon | An agent reads the description before it calls, so naming the fields and the 409 there tells it to check `available` first. A code change would add nothing the route doesn't already send. | — |
| D-319 | planning | Does 07-distribution.md need the D-217 correction? | autonomous | No edit: `:30` and `:227` already say it (commit 83229ea); row 4 checks both; `:226` is stale and stays out of scope | Local Canon | The brief was written from the triage, before the triage commit changed these lines. Re-checking proves the wording without a second edit. Mat kept `:226` out of scope at the plan gate. | USER_EXPLICIT 2026-11-06 'proceed' |
| D-320 | planning | How does a disabled model option look? | autonomous | It keeps its G30 pair; it can't be chosen, and its label carries the reason | Local Canon | G30 exists because the native list ignored the theme, and a muted pair would be a new palette decision. The reason in the label says more than a grey row. Mat accepted it at the plan gate. | USER_EXPLICIT 2026-11-06 'proceed' |
| D-321 | planning | What does the session gate cover? | autonomous | Identity, the static checks, the full Python, UI, OpenAPI, MCP and render checks, the settings and tts-generate Electron specs, package-build, smoke-capability, dev-pytorch and models-untouched; mcp-audit and build-record skipped | Local Canon | The session changes core, infrastructure, the API contract, MCP text, the renderer and the packaged behaviour, so each has its check. mcp-audit would touch the network and YouTube, and there is no installer to record. | — |

---

## Pattern Extraction

### Patterns to KEEP
1. **A packaged-smoke phase whose Red is the shipped build.** Running `--phase capability` on the pre-session onedir showed the defect where users meet it, and the fresh build showed the fix (D-315).
2. **A snapshot of the real models folder after each row that could touch it** (D-316). The reviewer confirmed from it that 159 files were unchanged.
3. **Naming the ledger vocabulary and the carried rules in the review prompt up front.** Both reviews approved in one round, with no refusal and no clarification.
4. **Probing `--decision-issue` at plan time** (`s51-decision-issue-probe.txt`), so the H2-2 cell named all three issues before closeout.

### Patterns to DROP
1. **Writing an execution note from memory.** The register-resolve note named the issue the session is about, not the one in the refusal. The receipt held the right index.

### Patterns to ADD
1. **A UI test's setup sync waits for the data library's own notify** before it asserts a render.
2. **A plan probes the keys each register write needs, per target issue.**

### Calibration Adjustment
- Estimated time: the grouping gave no time, only "calibrate against Session 35 `tts-voice-panel`".
- Actual time: about 3.4 hours of transcript time, 2026-11-06T22:31Z to 2026-11-07T01:55Z (17:31 to 20:55 local), with one round in each review.
- Adjusted estimate for a two-MEU capability session with a packaged smoke: half a day. Budget 8M tokens per review round (7,450,042 and 8,724,472 here), plus 4M per correction round if one is needed.

---

## Next Session Design Rules

```
RULE-1: A UI test that waits for a query's new state also waits one macrotask inside act before it asserts the render.
SOURCE: Gate run 1 failed on AC-118.2: TanStack Query notifies its observers on a setTimeout(0), and settled() waited only a microtask, so the assertion saw the list from before the report.
EXAMPLE: "await vi.waitFor(() => expect(state.status).toBe('success'))" → "...; await act(async () => { await new Promise((r) => setTimeout(r, 0)) })".
```

```
RULE-2: A plan that writes register fields probes, per target issue, that each key it replaces exists, or its script adds a missing key at its schema place.
SOURCE: issue-resolve.py refused ".issues[82]: keys differ" because TTS-DEVICE-OPTIONS-IN-CPU-BUILD had no resolution_path.
EXAMPLE: "replace resolution_path on both issues" → "probe: present in TTS-PYTORCH-OFFERED-WITHOUT-RUNTIME, absent in TTS-DEVICE-OPTIONS-IN-CPU-BUILD; set_fields inserts it before category".
```

```
RULE-3: Each row re-reads the lines it edits, and a plan citation that moved is corrected in the handoff, not followed.
SOURCE: _DEVICE_ORDER was at adapter.py:71, not :67; 03's anchor became :340-350, not :298-308; AC-118.5's settings.test.ts:297 and :304 lookups didn't exist.
EXAMPLE: "edit adapter.py:67 as the plan says" → "grep _DEVICE_ORDER finds :71; the handoff notes 'the plan cites :67; it is at :71'".
```

```
RULE-4: A review prompt that asks for tested_state names the user-level git ignore and the paths it hides.
SOURCE: Codex's sandbox doesn't read ~/.config/git/ignore, so its identity counted .claude/settings.local.json and differed; the reviewer wrote a probe to reconcile it.
EXAMPLE: "recompute identity.py --state-only" → "recompute it; ~/.config/git/ignore hides .claude/settings.local.json, which your sandbox may count as untracked".
```

---

## Next Day Outline

1. **Target:** Mat's direction on this session's commit. The draft goes to `C:/Temp/av-kit/commit-draft.txt`. Committing and pushing need Mat's words.
2. **Scaffold changes needed:** none.
3. **Issues to pick up:** Session 52 `tts-load-fp16` (MEU-119 to MEU-121) per the grouping, which needs this session. The rc.2 repeat of the capability smoke belongs to MEU-125.
4. **Patterns to bake in from today:** RULE-1 to RULE-4, and Session 50's RULE-1, RULE-2 and RULE-4, which carried.
5. **Codex validation scope:** Session 52's plan.
6. **Time estimate:** Session 52 per the grouping. Its FP16 cause hunt has no upper bound, and its plan sets the time box. Mat still has the Transcript check from another network.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | 981 in this conversation's transcript at H2-2, planning and execution |
| Time to first green test | 2026-11-07T00:37Z (19:37 local on 2026-11-06), the port Green (`s51-port-green`) |
| Tests added | pytest 1265 → 1274 (+9); Vitest 1144 → 1163 (+19, 109 → 112 files); MCP 466 → 470 (+4, 34 → 35 files) |
| Codex findings | Plan review: R1 approved, no findings, 7,450,042 tokens. Execution review: R1 approved, no findings, 8,724,472 tokens; its Q8 noted one wrong issue name in a handoff note, corrected |
| Handoff Score (X/7) | 6/7. Every AC has evidence, the gate passed with nothing excused and no correction round ran; one execution note named the wrong issue until the review caught it |
| Rule Adherence (%) | 92 |
| Prompt→commit time | Planned and executed on 2026-11-06 (local); the commit waits on Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Every Red failed by assertion, and `red-check.py` named the failing tests before each row was marked (Session 50 RULE-4) |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. The canonical review is Codex's report, validated under `C:/Temp/av-kit` and copied byte for byte |
| A raw value that can reach a log, stdout or the Console is fixed in the row or raised | Session 50 RULE-1; the brief | Yes. The reasons are fixed texts, and a failed kokoro import logs its class name only (D-309, D-310). No residual records a raw value |
| A row that edits a byte-hashed file runs its hash test | Session 50 RULE-2; the brief | Not triggered. No row edited `ui/tests/e2e/test-ids.ts`; the gate ran AC-51.6 and AC-81.13, and the review checked both prefix hashes |
| Every command through RTK | AGENTS.md §RTK | Partly. Row 11's UI typecheck and lint ran without `rtk proxy`; the gate ran both again under it |
| No branches or worktrees; never commit or push without the human | AGENTS.md §Commits | Yes. The work is uncommitted on `main`, and nothing was pushed |
| Preserve line endings | memory; the AC-51.6 byte hash | Yes. CRLF files stay CRLF and LF files stay LF, measured in bytes |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "32a1f22e-5e94-451c-9adf-db4d00cf5a2a"
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
  workflows: [create_plan, plan_critical_review, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/commands.md
    - .agent/docs/harness-profiles.md
    - .agent/docs/output-evidence-policy.md
    - .agent/docs/cloud-local-collaboration.md
    - .agent/schemas/review-verdict.schema.v2.json
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/TEMPLATE.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:human-decisions-stay-human, P1:independent-review-no-self-approval, P1:tests-before-production-code, P1:preserve-line-endings]
conflicts:
  - "The harness asks for a Co-Authored-By trailer on commits; task H2-5 says no AI attribution trailer. The draft has none, and the conflict goes to Mat before any commit."
  - "Connected artifact and docs servers offered to publish deliverables; the user's rule keeps them as local repo files."
note: "A variant whose runtime can't import is listed disabled with a reason and refused before any job or file; Settings offers only the devices a runnable variant reports."
slim_candidate: ["H2-1's view_file row re-reads the template and schema that H2-2's check validates against anyway."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 1, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {}
  verdicts: {approved: 2}
meu_work_classes: [correctness, correctness]
```
