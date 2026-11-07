---
date: "2026-11-07"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s52-plan-2026-11-06-tts-load-fp16"
round: 4
---

# Critical Review: tts-load-fp16

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Scope

**Intent anchor:** Session 52 makes a load that fails one of its checks leave the model that was loaded in place. It makes the first-run readiness check probe the models folder the backend actually uses, without creating it. It makes a fresh install preselect ONNX INT8 instead of FP16, and proves on a fresh packaged build that INT8 generates the fixed test set with no failure. A time-boxed spike looks for the FP16 cause, and its findings, or Mat's ruling on FP16, are recorded.

**Intent achieved:** `yes`, as plan readiness. This is not an implementation or packaged-generation pass.

Reviewed the working-tree implementation plan and task, the residual specs, the three issue entries by id, grouping sections 3/6/8, production callers, affected tests, fixed test-set evidence, packaging/smoke code, and the Session 51 helpers to be copied. Applied PR-1 through PR-9, the Materiality Gate and Verdict Rule. Reviewer: Codex/OpenAI, class `avkit_independent_reviewer`; author: Claude Code/Anthropic.

Observed HEAD: `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3`. All 29 work rows are unchecked; the three implementation handoffs are absent. Git shows the untracked plan folder and the disclosed sandbox-only `.claude/settings.local.json` entry; no tracked change. That settings file was not opened.

Accepted the supplied rulings, scope/order/split, pending human choices, scheduled helper creation, token-estimate treatment, historical-hash limitations, absent GUI references and MEU-125 exclusions. All writes stayed under `C:/Temp/av-kit`. No product suite, app/server, model constructor, real inference session, package build, smoke program, download, network request, YouTube call, repository edit, commit or push ran. Secret and fleet-hub paths were not opened.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No evidence-backed High or Critical delivery defect. Nonblocking clarifications appear below; none requires a correction round.

## Checklist Results

Manual observer: `codex-independent-reviewer`; manual exit code: `null`.

### Information Retrieval (IR)

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1–PR-3: alignment, readiness, task contracts | pass | Compare work packages, ACs, task dependencies/status and current handoff existence | null | MEU-119 → MEU-120 → MEU-121; implementation unstarted; tests, code, smoke and records assigned. |
| PR-5, PR-7: sources and scope | pass | Trace ACs/exclusions to residual specs, issue decisions and grouping | null | D-221/D-222/D-239 govern the requested work; MEU-125 exists and owns the release exclusions. |
| PR-6: review readiness | pass | Inspect Handoff Set and H1 review/correction rows | null | Three handoffs and vendor-distinct review are scheduled; round-2 correction-census rule is not applicable. |
| PR-9: governing contracts | pass | Compare named contracts with ACs and task commands | null | LOAD_CHECKS, DIR_PROBE, PRESELECT_ORDER, SENTENCE_SMOKE and D-333 identify governing behavior; no materially conflicting live instruction found. |

### Design Review (DR): Q1–Q8

**Q1 — Done and packaged proof: accepted.** AC-121.1 and AC-121.6 prove which id a fresh catalog selects; AC-121.8 then exercises that same id through the real freshly packaged backend outside the checkout. Together these prove the requested selection/generation conjunction without an installer run in this session. The count is `40×3 + 20 + 8 + 1 = 149`; the passage has 96 words. A read-only call of `TextPreparationService.prepare(text, [])` preserved all 49 distinct input texts. The production service forwards that prepared text to the adapter (`services/tts.py:324–325`).

AC-121.7 is a genuine negative: adapter finite checking fails a job, the new phase must aggregate those failures and exit 1, and row 9 refuses a successful run or any other error. FP16 failure is well supported, rather than a random-rate assumption: `fp16-rate-probe.txt:29–34` records 11 failures across the exact sentence/voice set, its timing repeats also fail, and `fp16-nan-probe.txt:3–10` shows repeatable all-nonfinite output. The local ORT distribution is still 1.31.1. A fresh packaged reproduction remains execution evidence, not something established here.

On a boxed spike, the stop reason, experiments/results and any candidate are recorded in the handoff and issue verification (`task.md:60,62`). That satisfies the registered goal's **findings recorded** branch and the authorized split. It does not settle FP16's disposition or close its issue. D-333 preserves that distinction; Part A can ship while the issue remains open.

**Q2 — LOAD_CHECKS and LOAD_KEEPS: accepted.** Weight → device → format → runtime can precede unload without building B or changing the loaded model/session/device fields. `_resolve` queries and logs fallback but assigns no adapter field (`adapter.py:327–338`); the format branch only logs/raises. Weight/device failures retain CPU logging, format/runtime failures use the resolved target. The runtime memo may gain a capability answer; that is not a replacement of A.

Both service and adapter read `RUNTIME_PRESENT`; the service fills the same per-format memo before the port call (`models.py:163–171`, `adapter.py:274–284`). Thus no second runtime probe is needed and AC-117.8's service-first 422 remains. D-323's new raising-probe branch logs class only, with no detail/traceback carrying the raw text. The existing missing-weight detail remains explicitly at Mat's gate under AC-115.9.

The stated after-unload limit is accurate: a later kokoro import, vocab resolver, constructor, device move/eval, or ultimate ONNX CPU-session failure can leave the adapter unloaded on CPU. An accelerator failure followed by successful CPU fallback is not a terminal failure. Settings PUT stores values; sideload records paths; neither separately loads a model. Generate uses an already loaded adapter. Their call chains do not bypass or invalidate the reorder.

**Q3 — Amendments and contract test: accepted.** A′ injects a successful capability answer into the two import-failure fixtures while retaining their original cause, message, device/log and unloaded-state assertions (`test_tts_device_resolution.py:739–756,855–869`). It keeps the later import-failure path covered. The amended AC-75.9 changes only failed-device-probe preservation; its error/cause/log/path assertions and initially-unloaded vocab branch remain. AC-119.7/.8 correctly guard terminal failures after unload.

AC-119.9 can reach the real adapter's missing-file check: ModelService does not reject a missing ordinary weight file first. It checks not-found, capability, legacy path and vocab; `FakeAssets` supplies READY and a nonlegacy FP32 row with a disappeared file reaches `load_model` (`models.py:156–171`). FakeCatalog must not substitute another sideloaded FP32 path.

One alternative description is inaccurate but does not invalidate A′: **moving only an engine import is not load-before-unload** (`implementation-plan.md:102,499`); `runtime_imports` itself imports KModel before unload. Constructing B there would violate D-221. A2 would lose the original later-import coverage, although its default-probe failure is not identical to an injected-False test. Do-nothing correctly leaves direct adapter callers unprotected.

**Q4 — MODELS_DEFAULT and DIR_PROBE: accepted, with an implementation caution.** On this Windows host, Node `join(homedir(), '.avkit', 'models')` and Python `Path('~/.avkit/models').expanduser()` both produce `C:\Users\Mat\.avkit\models`. The SettingSpec text match is valid at `settings.py:67`. Stored values still win; no caller outside setup-readiness requires the old helper argument. IPC and Settings consume the same boolean, and AC-58.12 allows any honest readiness count from zero to four.

The chosen ancestor probe is suitable for a genuinely missing path, including the disclosed transient file in the home folder on a fresh install. A file encountered on the path returns false. At a drive root, `dirname(candidate) === candidate` must terminate the walk. Apply the plan's **missing-path** wording literally: EACCES/EPERM must return false, not be treated as ENOENT followed by a successful probe of an unrelated writable parent. The scheduled implementation/tests must preserve that distinction; no intended permission bypass is specified. `accessSync(W_OK)` alone is correctly rejected as a Windows ACL check. No file migration or RC1 checklist edit is introduced.

**Q5 — PRESELECT_ORDER: accepted.** All five state-table rows follow the ranking rule: fresh→INT8; FP16+FP32 downloaded→FP32; all ONNX downloaded→INT8; only FP16 downloaded→FP16; unavailable INT8 with no downloads→FP32. Chosen and loaded precedence remains, absent `available` still means available, and a pending/empty catalog returns null. AC-117.13 fixtures retain their results, AC-117.14 still selects its downloaded FP32, and AC-63.x uses legacy ids that keep catalog order. The other files that render/reference TTSPage showed no conflicting selected-value expectation; row 7 appropriately runs the full UI suite.

`engine.py` is justified as a read-only source: `_seed_model_variants` supplies null paths/not-downloaded flags (`:95–105`) and the repository sorts ids (`repositories.py:355`). Extracting those seeded rows as text is enough for the selection test; a seed rewrite that breaks extraction must fail the test rather than fall back to a hand-written catalog. Mat's listening gate, FP32 alternative and only-FP16 choice remain intact.

**Q6 — FP16_SPIKE: accepted as a bounded investigation, with limits stated.** Local copied weights/vocab/voice packs and one cached G2P pass support E0–E4 without inference on the real models folder. Reproducing failure, changing one variable, checking every pair, restoring the control and repeating the candidate is sound evidence for a causal candidate; it is not permission to implement a fix. E3 must meet the full-pair confirmation rule before its candidate is called a cause. E5 remains separately authorized.

The installed `uv help run` confirms `--offline` uses cached/local data only and `--with` installs the alternative runtime in a separate overlay. It also says normal project synchronization precedes execution: **the command alone does not guarantee an unchanged project environment/lock**. Use `--no-sync` (which implies frozen) when implementing that no-mutation boundary; cache misses remain not-run, never a fetch. No overlay command was executed during review.

The plan names a two-hour scheduling box checked before experiments (`implementation-plan.md:204–211`); this does not itself demonstrate interruption of an in-flight ORT call. Carry the remaining budget into experiment/child timeouts when implementing the scheduled script, so S13 can save its boxed summary and let Part A proceed. This is an implementation caution, not a demonstrated material false-pass in an existing script. Row 11's actual stop predicate was independently exercised: missing and unknown stop reasons are rejected.

**Q7 — Red and guards: accepted.** The required pytest prefixes match the proposed new names; `-k "ac_119 or ac_75_9 or ac_98_5"` includes the intended amended test and A′ guards. Assertions fail on current unload-first behavior, ignored runtime probes, or zero probe calls. The UI namespace/property assertions avoid required-test missing-name errors; AC-120.2 checks the new export before calling the currently argument-requiring function. AC-120.3 can use the existing appData argument to reach an assertion rather than a setup TypeError. Existing exports suffice for the other Reds. The selected files do not pull in another MEU's new tests before its Red.

The copied checker enforces assertion attribution and non-digit title boundaries (`red-check.py:216–217`); required names cannot silently select nothing. AC-119.7/.8, AC-120.5/.6 and AC-121.5 honestly pass before Green. Scratch executions of the actual row 9–11 predicates rejected unexpected smoke success, wrong failure kind, no failures, 148 jobs, failed Green jobs, an empty Green object and absent/unknown spike stop reasons. No materially missing deliverable was demonstrated to false-pass these controls. Actual product Red/Green results remain future work.

**Q8 — Order and safety: accepted.** No row authorizes commit, push or publication. Tests use fakes and temporary paths; the real files are only read for copies/dev checks, except the disclosed readiness probe file. Both smoke-source and dev assets currently read READY, including 54/54 packs, supporting the fast paths without an asset fetch. The evidence probes are historical inputs, not programs the plan should rerun with their original downloads. The spike must similarly omit those download calls.

Row 9's Copy-Item reads the source FP16 file; it does not move or modify it. The package build overwrites generated ignored packaging output, then runs a fresh outside-checkout copy without `--stub-ok`. S3 protects concurrent scope/HEAD changes and S4 compares real model files. S5 remains a stop-before-fetch rule; a snapshot is detection, not authorization to download. The issue resolver's held Windows handle, expected-hash check and staged semantic validation protect shared-main register edits; its existing subset support permits FP16 verification alone. Only Mat's D-333 outcome changes FP16 status. Network/YouTube audit, installer build-record and repeated capability smoke exclusions are justified by the supplied scope and MEU-125 ownership.

### Observed evidence

```json
{"schema_version":"evidence.v1","check_id":"s52-readonly-contract-probe","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s52-readonly-probe.py","cwd":"P:/av-kit","scope":"test-set count, preparation identity, seed order, asset readiness, default path and unstarted state","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main b6c38952d1a96e3bbdc9c11c94bcdb60330152b3; working-tree Session 52 draft; local dev environment and cached assets","output":"40 sentences; 8 paragraphs; 96 passage words; 149 jobs. Empty enabled_steps preserves all 49 texts. Seed id order fp16, fp32, int8, pt-fp32. Smoke-source and dev assets all ready; 54/54 voice packs in each. Node/Python defaults equal C:/Users/Mat/.avkit/models. ORT 1.31.1. No implementation handoffs; 29 unchecked work rows, zero completed. Network-negative guard refused resolution before any request.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s52-task-predicate-negatives","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s52-predicate-probe.ps1","cwd":"P:/av-kit","scope":"current task rows 9, 10 and 11 predicates extracted into scratch; synthetic objects only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main b6c38952d1a96e3bbdc9c11c94bcdb60330152b3; working-tree task.md","output":"Intended Red/Green and cause/done/box/control accepted. Unexpected-success, other-error, no-failure, incomplete-set, failed-job, empty-object, missing-stop and unknown-stop each rejected as expected. predicate-probe: PASS.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s52-plan-contract-trace","procedure":"Read plan/task and source/decision anchors; trace production entrypoints, test fixtures, packaged phase extension and copied helpers; compare Q1-Q8 and PR-1 through PR-9 to the registered goal.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Session 52 plan readiness","phase":"targeted","exit_code":null,"result":"pass","tested_state":"main b6c38952d1a96e3bbdc9c11c94bcdb60330152b3; working-tree Session 52 draft","output":"No evidence-backed High/Critical delivery defect. Load preservation, aligned no-mkdir probe, preselection plus real packaged sentence smoke and recorded split-spike findings have reachable production paths and planned negative checks. Human execution/listening/outcome gates remain.","fresh":true}
```

Other commands: numbered bounded reads through `s52-read.py`, targeted `rtk proxy rg` searches, Git HEAD/status and `uv help run` (exit 0). Initial scratch-probe failures came from AST literal evaluation of multiplied seed sizes and an overly broad audit hook rejecting NUL; both were corrected under Temp before the passing run. A mistaken `model_manager/assets.py` read was replaced by the real `tts/assets.py` source. Failed exploratory reads/probes are not used as evidence of a product defect or pass.

## Verdict

`approved` — executing this plan can deliver the registered intent. No blocking finding or required correction round. Carry the nonblocking alternative-description and implementation cautions above into the scheduled work. Approval does not supply Mat's execution authorization or listening verdict.

**Residual risk:** no fresh inference/package/runtime evidence was produced in this review. The future code must substantiate the specified permission-error handling, isolation and spike stop behavior, as well as the actual 149-job Red/Green. The coordinator may copy this report unchanged to the canonical review path. Completion-preflight was applied to this review artifact only; no implementation row was marked complete.

🕐 Completed: 2026-11-07 01:10 (EST)


## Recheck (Round 2)

**Date:** 2026-11-07. **Workflow:** `/plan-critical-review`, amendment-only recheck. **Reviewer:** `codex-independent-reviewer`, Codex/OpenAI, class `avkit_independent_reviewer`. Claude Code/Anthropic wrote the plan. Round 1's Scope, Findings, Checklist Results, Q1–Q8 and Verdict above are preserved as historical round-1 results; the frontmatter and this section describe round 2.

**Intent anchor:** Session 52 makes a load that fails one of its checks leave the model that was loaded in place. It makes the first-run readiness check probe the models folder the backend actually uses, without creating it. It makes a fresh install preselect ONNX INT8 instead of FP16, and proves on a fresh packaged build that INT8 generates the fixed test set with no failure. A time-boxed spike looks for the FP16 cause, and its findings, or Mat's ruling on FP16, are recorded.

**Intent achieved:** `partial`, as plan readiness: the scrub amendment is implementable, but E5 does not enforce the newly authorized download boundary. This is no implementation, test-suite or packaged-generation certification.

**Scope:** the working-tree amendment to `implementation-plan.md` and `task.md`, D-335's logging/test call chains, the supplied six plan-time receipts, the saved PyPI metadata behind the pins, the existing red checker to be copied, pytest's temp-root implementation, and local `uv help run`. Observed branch `main`, HEAD `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3`. Mat's four rulings and all round-1 accepted scope remain given. No repository file was written. No pytest, Vitest, Playwright, gate, build, smoke, application, inference, `uv run --with`, install or network request ran. All scratch writes stayed under `C:/Temp/av-kit`; prohibited secret/hub paths were not opened.

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High (confidence: High) | yes | behavior | **E5's online overlay is not restricted to the two authorized wheel downloads.** `--no-sync` protects the project venv/lock; it does not restrict the separate overlay's dependency resolution. The saved metadata gives ONNX open lower bounds on numpy, protobuf and typing-extensions, and ml-dtypes an open numpy lower bound. Installed versions satisfying those bounds do not pin that separate resolution: local `uv help run` explicitly permits overlay/project conflicts and defaults to the highest compatible versions. Thus a newer compatible transitive release can be selected and fetched during E5, beyond Mat's exception, even while `uv pip list`, `pyproject.toml` and `uv.lock` stay unchanged. Discovering this after the child cannot enforce S5's stop-before-fetch requirement. This affects the operator running row 11 and the `FP16_SPIKE`/AC-121.9 execution boundary; violates **AC-121**. | `docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md:235`; `:241`; `:485`; `docs/execution/plans/2026-11-06-tts-load-fp16/task.md:62` | Bound network access before resolution: fetch only the two recorded wheel URLs to Temp and verify their recorded SHA-256s, then run E5's overlay offline with `--no-sync` and those local wheels. Any dependency cache miss must be `not_run`/S5 before another fetch. Retain the venv/file comparisons; if claiming detection of every other new cached package, compare the complete relevant cache inventory, not just the two named package directories. An equivalent demonstrably enforced two-wheel boundary is acceptable. | open |

### R1 — HOME_SCRUB correctness

**Accepted.** The proposed literal-part matching rule supports native, forward, mixed and doubled backslashes; quoted exception text and a home alone; Windows case folding with a case-sensitive alternative; look-alike names, mid-word/mid-path exclusions; and empty/bare-drive guards. Escape each home component with `re.escape` when implementing literal matching, including metacharacters in a legitimate home-folder name. The scratch implementation used the supplied left boundary `(?<![\w\\/.~-])`, right lookahead `(?=[\\/'"]|$)`, and only the specified conditional `IGNORECASE` flag.

The probe passed 27 matching/pipeline assertions, including a metacharacter-bearing Windows and POSIX home, the 290-character prefix and the final 300-character limit. `file:///C:/Users/...` survives the home match's slash boundary but the existing URL matcher still replaces the whole URL with `[link]`. A `Bearer`/`Authorization` string enclosing the home path still redacts the remainder. No `REDACT_NEEDLES` change is needed. The scratch probe also confirms that today's `console_field` retains the synthetic home, so this is future Green behavior rather than a claim about current code.

**Nonblocking factual caveat:** `implementation-plan.md:402` overstates that the product's paths are all long forms. A stored `tts.models_directory` can contain `C:\Users\RUNNER~1\models`: settings preserve the string (`settings.py:141–145`), and `models_directory` calls only `expanduser`, not `resolve` (`models.py:54–56`). Sideloading retains the path spelling (`model_manager/manager.py:97–113`), and a later missing-weight error uses that stored path in `detail` (`tts/adapter.py:148–158,167–175`). The scratch encoding/path probe confirms preservation without touching the filesystem. The disclosed 8.3 limitation can therefore arise from a stored setting, even though the default and pytest's resolved temp root use long forms. This does not reopen the explicitly supplied exclusion or require adding short-name matching; describe the exclusion accurately.

### R2 — Logging coverage and consumers

**Accepted for the D-335 scope.** The affected production paths carry their path-bearing text in `error` or `detail`. Both, together with every other member of `CONSOLE_FIELDS`, pass through `console_field` in `health.py:178–182`. One resulting `message` feeds the ring (`:191–198`), stdout (`:199–200`) and `console.log` (`:201–202`); downstream rendering receives the safe message after the raw dictionary/traceback is removed (`:203–205`). A real `HealthService` with the proposed field function substituted in memory produced scrubbed ring, stdout and file output under Temp, with the filed message equal to the ring message. The raw event/module are not processed by `console_field`; they are not the six affected path-bearing values. The broader Electron/renderer stdout view remains outside the promised change to these backend Console fields, consistent with the explicit main/MCP logging exclusions.

The saved consumer sweep agrees with current `useBackendLogs.ts`, `ConsolePanel.tsx` and health route code: they display/forward messages, without extracting a filesystem path from them. The separate Console-log-file label uses a separately supplied path. Existing AC-115.9/.10 expectations exercise ordering, single-line shape, URLs, redaction and cuts with synthetic non-home values; their assertions need no amendment. No conflicting path expectation was found in the identified Console-reading tests.

### R3 — Rows 2a/2b and TEMP-under-home proof

**Accepted as planned validation, not executed product evidence.** AC-119.10 and row 2a specify the separator, case, look-alike/outside/mid-path, prefix-cut, empty/bare-drive and three-surface cases. Each test first asserts `hasattr` for the missing `home_folder`/`scrub_home`, before monkeypatching either name or `HOME_IGNORES_CASE`; it therefore fails today by assertion. The current file contains no `ac_119_10` test name. The new prefix confines `-k ac_119_10` to the appended tests, and the existing checker's non-digit boundary accepts `test_ac_119_10_...` but rejects `test_ac_119_100_...`. A synthetic receipt passed the existing checker on an assertion and was refused on `AttributeError` and on the wrong prefix. No pytest process ran.

Row 2b first runs `test_services.py` and `test_console_level.py`, then all ten identified executable Console-reading files with TMP/TEMP under LOCALAPPDATA. The eleventh file is the imported `api_fakes.py` helper. This is the right identified set for the scrub's expectation-regression check; integration tests that merely capture raw structured dictionaries are unaffected by a rendering-only change. `_pytest/tmpdir.py:202` resolves the temp root, supporting the stated long-form CI case. Row 2b uses a separate pytest process, so tempfile's cached root in a previous process does not defeat the override. S14 correctly stops on an unexpected existing assertion change instead of authorizing edits to AC-115.9. Row 3 depends on 2b, preserving the MEU boundary.

### R4 — E5's fetch and offline children

**Not accepted: F1.** The two recorded package versions, wheel names, hashes and release dates agree with the saved PyPI records. ONNX's ordinary dependency set is numpy, protobuf, typing-extensions and ml-dtypes; the Pillow requirement is an unrequested extra. ml-dtypes 0.6.0 requires numpy >=2.0 on Python 3.12, which installed numpy 2.5.4 satisfies. These facts establish compatibility, not an online-resolution whitelist.

Local help confirms that `--no-sync` avoids project-environment synchronization and implies frozen, so adding it to the offline children resolves the round-1 isolation caution. E2's `--offline` also prevents an uncached dependency from becoming a download. E5 deliberately omits that boundary while only two top-level requirements are pinned. The three installed dependency versions do not become constraints merely because `s52-onnx-deps.txt` lists them. The requested version checks, venv package lists and unchanged project files are useful observations but do not prevent transitive downloads. Listings restricted to `pypi/onnx` and `pypi/ml-dtypes` also cannot themselves show an added third package elsewhere in the cache. S5 correctly names only E5 as the exception; its two-wheel limit needs enforcement before E5's resolver can fetch.

### R5 — Rulings, dependencies and records

**Accepted.** D-330 and D-331 record human product preferences (keep the only-downloaded FP16 rule; select INT8). D-333 records human permission lifting an external fetch block, with both pins and E5 last inside the existing box; D-335 records the human resolution of the scope/source conflict in favor of a central scrub. Their `resolution`, `source_tag`, class and verbatim human references agree with the given rulings. D-324 now correctly distinguishes importing an engine before unload from constructing B there; the chosen A′ setup and unchanged assertions remain clear.

WP-2, the MEU-119 header, rows 2a/2b and row 3's dependency carry the new work in order. H1-6 explicitly includes AC-119.10 and the TEMP-under-home receipt; H1-7 carries AC-119.1–.10, D-335 and the contracts into the execution ledger/reviewer request; H2-2 carries D-322–D-335 into the reflection. Row 11 passes `--e5`. No additional scope or gate ruling is requested by this review.

### Checklist Results and observed evidence

Manual observer: `codex-independent-reviewer`; manual exit: `null`.

| Check | Result | Procedure / command | Exit | Decisive evidence |
|---|---|---|---|---|
| R1 / PR-4, PR-8: matching and pipeline | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s52-r2-probe.py` with PYTHONDONTWRITEBYTECODE=1, HF_HUB_OFFLINE=1 | 0 | 27 matching/pipeline assertions passed; current field retains the synthetic home; scratch Green covers the required forms and cut. |
| R2 / PR-8: affected production paths and consumers | pass | Trace health field rendering through its three sinks and inspect the saved consumer/path-assertion sweeps against the current sources | null | `health.py:178–205` shares the safe message across the sinks; no message-to-path consumer found; existing sampled expectations stay valid. |
| R3 / PR-1, PR-4: Red attribution and test selection | pass | Same scratch command, invoking existing red-check functions on synthetic receipts only; read rows 2a/2b and pytest tmpdir source | 0 | Assertion accepted; missing-name and wrong-prefix refused; ten executable Console-reading files plus helper accounted for; TMP/TEMP override targets the CI-relevant case. |
| R4 / PR-4, PR-8: E5 download boundary | fail | Compare plan :235–241/S5 with local `uv help run` and the saved ONNX/ml-dtypes metadata | null | Help :128–130 permits independent overlay conflicts; :171–175 protects venv/lock; :431–440 defaults to highest compatible resolution. Neither the command nor the after-the-fact checks restrict fetches to the two wheels. |
| R5 / PR-1, PR-5: human rulings and carry-through | pass | Compare supplied verbatim ruling with decisions D-324/D-330/D-331/D-333/D-335 and task rows 2–3/11/H1-6/H1-7/H2-2 | null | Rulings and source/classes align; new AC and its evidence reach the handoff, review request and reflection. |
| Product Red/Green, TEMP-under-home suite, packaged build and inference | n/a | Explicitly prohibited in this review | null | Remain future execution evidence. |

```json
{"schema_version":"evidence.v1","check_id":"s52-r2-amendment-probe","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s52-r2-probe.py","cwd":"P:/av-kit","scope":"synthetic HOME_SCRUB rule, current HealthService sinks in scratch, stored-path encoding and existing red-check receipt parsing","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main b6c38952d1a96e3bbdc9c11c94bcdb60330152b3; working-tree Session 52 amendment; existing health.py/red-check.py; synthetic strings and Temp-only log file","output":"network guard: blocked before name resolution; matching and pipeline assertions: 27 passed; current implementation retains synthetic home; HealthService with scratch field: ring, stdout, console.log all scrubbed; 8.3 stored path preserved; no current ac_119_10 test; synthetic assertion accepted, AttributeError and wrong-prefix refused; probe: PASS","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s52-r2-e5-boundary","procedure":"Read amended E5 command and S5, saved PyPI dependency metadata, and locally generated uv help run; distinguish project sync isolation from unconstrained online overlay resolution and distinguish pre-fetch enforcement from after-the-fact detection.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"FP16_SPIKE E5 two-wheel fetch exception; AC-121","phase":"targeted","exit_code":null,"result":"fail","tested_state":"main b6c38952d1a96e3bbdc9c11c94bcdb60330152b3; working-tree amendment; installed uv CLI help; supplied saved package metadata","output":"--with overlays may conflict with project dependencies; --no-sync avoids syncing and implies frozen; resolution defaults to highest compatible versions. ONNX and ml-dtypes leave numpy/protobuf/typing-extensions open above lower bounds. An extra transitive wheel fetch is not prevented by venv/lock/file or subsequent cache comparisons. No resolver, install or network operation was executed.","fresh":true}
```

Exploratory scratch syntax/import-name mistakes were corrected under Temp before the passing probe; a nonexistent guessed supervisor path was replaced with reads of the actual main-process sources. These errors are not product failures or product passes. The completion-preflight skill was consulted and applied to the review deliverable only; all implementation rows remain unstarted and no canonical artifact was edited. The coordinator must copy the complete rolling report after validating it.

### Verdict

`changes_required` — one evidence-backed High finding, F1, on E5's download boundary. HOME_SCRUB, the new Red/Green rows, the relevant existing-test guards and the human-ruling records are accepted. Correct F1 within the existing loop or take the unresolved boundary to Mat; this review does not authorize an additional recheck round or any execution/download.


## Recheck (Round 3)

**Date:** 2026-11-07. **Workflow:** `/plan-critical-review`, correction-only recheck. **Reviewer:** `codex-independent-reviewer`, Codex/OpenAI, class `avkit_independent_reviewer`; author: Claude Code/Anthropic. Earlier sections, including the complete round-2 recheck, are preserved as historical results. Frontmatter and this section carry round 3.

**Intent anchor:** Session 52 makes a load that fails one of its checks leave the model that was loaded in place. It makes the first-run readiness check probe the models folder the backend actually uses, without creating it. It makes a fresh install preselect ONNX INT8 instead of FP16, and proves on a fresh packaged build that INT8 generates the fixed test set with no failure. A time-boxed spike looks for the FP16 cause, and its findings, or Mat's ruling on FP16, are recorded.

**Intent achieved:** `yes`, as plan readiness. Round-1 and round-2 accepted work remains accepted; this is not implementation or packaged-generation evidence.

**Scope:** only round-2 F1's E5 correction, its carry-through in the task/constraints/S5/D-333 records, and the corrected 8.3 exclusion row. Read the supplied probe receipt and its two scripts without executing them, compared the supplied cache fingerprints, checked the saved pin/dependency metadata, read local uv help, and traced the exclusion's cited source lines. HEAD remains `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3`. No product tests, build, smoke, application, inference, network request, download, actual install, repository mutation or uv-cache write was performed. The independent dry run below used both `--offline` and `--dry-run`, plus `--no-cache`; all reviewer writes stayed under `C:/Temp/av-kit`.

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High (original; confidence: High) | no | behavior | **Resolved.** E5 no longer asks an online overlay to resolve dependencies. Its exact two-entry hashed requirements file, `--no-deps`, wheel-only install and Temp target enforce the authorized package boundary before transitive resolution; the subsequent child is offline with `--no-sync`. This resolves the `FP16_SPIKE`/AC-121.9 boundary finding under family **AC-121**. Local help and the supplied real local-wheel hash/dependency negatives support the change. | `docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md:239`, `:241`, `:244`, `:250`, `:255`, `:264`; `docs/execution/plans/2026-11-06-tts-load-fp16/task.md:62` | No further correction required. Implement the specified flags, provenance assertions and stop checks without weakening them. | fixed |

No open High or Critical finding. The previous nonblocking 8.3 factual caveat is corrected.

### Q-F1 — E5 boundary

1. **Accepted: the two-wheel boundary.** For the recorded CPython 3.12 Windows x64 environment and PyPI releases, the two exact requirements select the recorded wheels. `--no-deps` removes all transitive requirements from resolution; `--only-binary :all:` excludes source/build work; the two hashes require the selected bytes to match. `--no-config` bypasses project/user configuration files and the explicit default index names PyPI. The specified resolve has no third package to fetch; index metadata for the two packages is part of their authorized fetch. This is an acceptable equivalent to fetching the two recorded URLs directly. Hash verification occurs on obtained bytes: it is not a claim that a wrong-hash download is rejected before transfer.

2. **Accepted, with its limits: probe evidence.** `s52-e5-bound-probe.txt:1-13` shows one pinned package selected without dependencies, and a cache hash miss planning a download; that dry run does not prove downloaded-file verification. Lines 24-58 show the stronger local-wheel checks: right hash/no-deps succeeds, wrong hash fails with `Hash mismatch` and leaves only `.lock`, and removing no-deps reaches the deliberately nonexistent dependency and fails offline. The plan's paragraph at `implementation-plan.md:250-253` describes those observations accurately. The before/after receipts contain identical recorded cache digest/count (`f3fd31444908e93be79ba8b56c8b7017`, `3757`); these are aggregate fingerprints, not a reproduced full listing. I did not repeat the actual installs.

3. **Accepted: project isolation.** Local install help defines `--target` as installing into the supplied directory instead of the virtual/system environment. `--python .venv/Scripts/python.exe` supplies interpreter/platform selection; it does not override that target. This `uv pip install` operation does not synchronize a project or update its manifest/lock. Local run help confirms `--no-sync` avoids environment synchronization and implies frozen. Before/after venv package lists and manifest/lock hashes remain useful backstops (`implementation-plan.md:247`, `:255-262`).

4. **Accepted as a planned assertion, not an executed E5 result: import provenance.** `PYTHONPATH=e5-site` puts the two installed modules ahead of venv site-packages. With only those two distributions in the target, existing numpy, protobuf (Python module `google.protobuf`) and onnxruntime remain provided by the venv. The explicit module-file and version assertions must refuse any different origin/version (`implementation-plan.md:255-260`). No ONNX import or inference was needed to judge that design.

5. **Accepted: backstops and failure handling.** The cache census now covers every package name under every `wheels-v*/<source>/` and `simple-v*/<source>/` directory, instead of looking only beneath the two permitted package names. Its comparison, the exact target-distribution set, venv list and manifest/lock hashes detect the specified deviations. These remain detection checks; no-deps/wheel/hash controls supply the install boundary. Failed installs are `not_run` with their diagnostic, with no retry using looser flags. Unexpected distribution/cache/project changes are S5 and stop the spike (`implementation-plan.md:255-264`).

6. **Accepted: D-333 E5 items 1-3.** The same two authorized packages enter the uv cache in E5's child only, `--e5` remains on row 11, and versions/hashes/cache observations are recorded. A Temp install target changes isolation, not the authorized package set or cache destination. It adds no package, model re-export or code fix (`human-gate-decision.md:165-178`; `implementation-plan.md:647`; `task.md:62`).

7. **Accepted: S5 remains a single-step exception.** Constraints, E5's ruled note, the no-download paragraph, S5 and task wording consistently name only E5's install of these two hashed pins. E2 and E5's run child remain offline (`implementation-plan.md:67`, `:127`, `:230`, `:255`, `:470`, `:508`; `task.md:15`, `:40`, `:62`).

### Q-C — 8.3 limit

**Accepted.** The corrected row distinguishes the identified default/app-data/temp paths from saved configuration. `services/settings.py:141-145` preserves a string's spelling; `services/models.py:54-56` calls only `expanduser`; and `model_manager/manager.py:97-113` retains the discovered path. `_require_weight_path` chains `FileNotFoundError(str(missing))` at `tts/adapter.py:167-175`, and `_log_load_failed` uses that cause's first line for `detail` at `:148-158`. A stored short-form home path can therefore survive `HOME_SCRUB` into that detail. The row now explicitly says so and retains the limit raised with Mat (`implementation-plan.md:425`). Its anchors support the corrected statement. No short-name matching fix is requested or implied.

### Checklist Results and observed evidence

Manual observer: `codex-independent-reviewer`; manual exit: `null`.

| Check | Result | Procedure / command | Exit | Decisive evidence |
|---|---|---|---|---|
| Q-F1 / PR-4, PR-8: authorized install boundary | pass | Compare exact E5 command, local `uv pip install --help`, saved metadata, probe scripts and receipt | null | Two exact hashed requirements; dependencies ignored; source builds excluded; real local-wheel negative rejects a hash mismatch. |
| Q-F1: independent read-only dependency-selection check | pass | `rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s52-r3-dry-probe.ps1` | 0 | CPython 3.12.12; resolved/would install only `s52probe` despite its nonexistent dependency; no actual install/download. |
| Q-F1 / PR-1, PR-5: isolation, authorization and S5 carry-through | pass | Compare install/run help, E5 provenance/backstop rules, task row 11 and D-333 items 1-3 | null | Temp target; offline/no-sync child; all-package cache-name census; failed install not_run with no relaxed retry; only E5 install excepted. |
| Q-C: factual correction and source anchors | pass | Trace stored setting through path expansion, sideload and missing-weight cause/detail | null | Short spelling is preserved; row :425 now discloses that path reaching detail unscrubbed. |
| Product tests, actual E5 install/imports, packaged build/generation | n/a | Outside authorized read-only review | null | Remain execution evidence. |

```json
{"schema_version":"evidence.v1","check_id":"s52-r3-offline-dry-selection","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s52-r3-dry-probe.ps1","cwd":"P:/av-kit","scope":"local synthetic wheel with nonexistent dependency; target C:/Temp/av-kit/s52/r3-dry-site","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main b6c38952d1a96e3bbdc9c11c94bcdb60330152b3; existing local s52probe 0.0.1 wheel; CPython 3.12.12; PYTHONDONTWRITEBYTECODE=1","output":"Executed uv pip install --offline --dry-run --no-cache --no-config --default-index https://pypi.org/simple --no-deps --require-hashes --only-binary :all: --python .venv/Scripts/python.exe --target C:/Temp/av-kit/s52/r3-dry-site -r C:/Temp/av-kit/s52/e5-probe/local-good.txt. Resolved 1 package; Would download 1 package; Would install 1 package: s52probe @ file:///C:/Temp/av-kit/s52/e5-probe/wheels/s52probe-0.0.1-py3-none-any.whl. preserved_exit=0. Would download describes a dry-run plan for a local file, not a network transfer.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s52-r3-correction-trace","procedure":"Compare revised E5 install/run and S5 against local uv help, saved PyPI records, the supplied offline probe and its source scripts, D-333 E5 items 1-3 and task carry-through; trace the corrected 8.3 row against its current source anchors.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"round-2 F1 and nonblocking 8.3 caveat only","phase":"targeted","exit_code":null,"result":"pass","tested_state":"main b6c38952d1a96e3bbdc9c11c94bcdb60330152b3; working-tree Session 52 correction; local uv help; supplied saved receipts","output":"F1 fixed: no-deps bounds resolution to two hashed binary requirements, installed into Temp; run child offline/no-sync with module-origin assertions; broader cache census and unchanged-project checks retained; failed install not_run without relaxed retry; only E5 install is S5's exception. The 8.3 row accurately discloses stored-path spelling and missing-weight detail propagation. No new blocking defect established.","fresh":true}
```

**Assumptions/open questions:** none newly raised. The given pins, rulings and accepted earlier scope remain given. **Residual risk:** the real two-wheel fetch, imports, spike and packaged 149-job pass have not run in this review and must still satisfy the planned checks. Completion-preflight applies to the review artifact only; no product task was completed or edited. The coordinator copies this complete report to the canonical path after validation.

### Verdict

`approved` — F1 is fixed, the 8.3 factual caveat is corrected, and no open evidence-backed High or Critical finding remains. Executing the corrected plan can deliver the registered intent.


## Recheck (Round 4)

**Date:** 2026-11-07. **Workflow:** `/plan-critical-review`, closure-only recheck. **Reviewer:** `codex-independent-reviewer`, Codex/OpenAI, class `avkit_independent_reviewer`; plan author: Claude Code/Anthropic. The complete historical report above is unchanged except its frontmatter round, which now carries round 4; verdict remains `approved` and findings_count remains 0.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High (original; confidence: High) | no | behavior | Resolved in round 3; the same E5 two-wheel boundary remains specified. Round-3 evidence and judgment stand; no substantive re-review or new finding. | `docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md:239`, `:241`, `:244`, `:255`, `:264`; `docs/execution/plans/2026-11-06-tts-load-fp16/task.md:62`; prior evidence: `.agent/context/handoffs/2026-11-06-tts-load-fp16-plan-critical-review.md:208`, `:214`, `:245`, `:249` | No further correction required. Carry round 3's fixed judgment into the review state. | fixed |

Confirmed that the canonical round-3 report is byte-identical to its Temp original and matches the supplied SHA-256 `95e42dc888604e22c05fd607c4efc75b83c6bc3cfcccb395db494b0d295022df`. All 14 files in the plan folder, including its nested fixed-test-set inputs, have modification times at or before 08:33:44 EST on 2026-11-07, consistent with the supplied pre-dispatch chronology; the Temp round-3 report was saved at 08:40:11 EST. Rechecked only the unchanged F1-related E5 clauses, task row 11 and D-333 correction against round 3's cited evidence. The two hashed binary requirements, `--no-deps`, Temp install target, offline/no-sync run child, provenance/backstop checks and refusal to retry with looser flags remain in place. F1 remains fixed. No other surface was re-reviewed and no new finding was identified.

### Checked state and evidence

| File | Last write (UTC) | SHA-256 |
|---|---|---|
| `baseline.ps1` | `2026-11-07T13:13:20.360682+00:00` | `82a551e81f40696a606bd57191080ab07b8d95f1250e1ecdc9c19c212c2ef2e2` |
| `fp16-test-set/fp16-nan-probe.txt` | `2026-11-07T04:08:46.408143+00:00` | `16691cef9a0b340565c4a771e34f228ca68ee8f949bfe2b791d6b66ed05050b0` |
| `fp16-test-set/fp16-rate-probe.txt` | `2026-11-07T04:08:46.408143+00:00` | `3b6c09bdc449befc55e25e792bb6e9809946548657cd047e473843fad57755a8` |
| `fp16-test-set/fp16_nan_probe.py` | `2026-11-07T04:08:46.406143+00:00` | `9e584ba2419ce350a2c6f25f4eb015f5a0b6ed0e60ce07be2cc1f6836fc08aa9` |
| `fp16-test-set/fp16_rate_probe.py` | `2026-11-07T04:08:46.407143+00:00` | `df1a4eea15adda1baafb84034b904688262a4e33276d7d3a3275cff9d57884dd` |
| `fp16-test-set/phonemes.json` | `2026-11-07T04:08:46.408143+00:00` | `91d91708b9f5d8f65393371470d7182f689f58f30bf82f7a2bfc69fa74a42f40` |
| `fp16-test-set/test-set.json` | `2026-11-07T04:08:46.413148+00:00` | `53c941543295b48439b633faf2746b33123c17482207a4a6e99faad6f6760ef3` |
| `fp16-test-set/tts_variant_compare.py` | `2026-11-07T04:08:46.407143+00:00` | `878004afb8203d84729bdac4dd0ac1dea889cfd298e33f0f1ad90a930960472e` |
| `human-gate-decision.md` | `2026-11-07T13:31:14.390740+00:00` | `995471128586151296d09d80f0c1500b32d26689fdeb387d26690ddab6a627a2` |
| `identity.py` | `2026-11-07T13:12:49.157919+00:00` | `589412ab9e1294a07fd07ca6470fecfae0023e2651ff030ca45ee74f72c9e00d` |
| `implementation-plan.md` | `2026-11-07T13:33:44.507259+00:00` | `0b323a49ea5247a26d45e880fafd3e5f9a41b2376bfe9dd0a397f0c1bc07c85c` |
| `models-snapshot.py` | `2026-11-07T13:12:49.157919+00:00` | `331dd604dd0810f12eda13bc600a432f1d33620d2338d020fe4752610b09971a` |
| `red-check.py` | `2026-11-07T13:12:49.157161+00:00` | `085569cea36fc48f294d34391aa70edb267fd6a0b6e525d693cd341d9c34b287` |
| `task.md` | `2026-11-07T13:31:06.337304+00:00` | `2e136807621b22e29d7a05a257727252f9c68734612b59d5409ccce661f9d586` |

```json
{"schema_version": "evidence.v1", "check_id": "s52-r4-f1-closure", "procedure": "Compare canonical round-3 report with the supplied SHA-256 and Temp original; inspect all 14 plan-folder file timestamps and hashes, including nested fixed-test-set inputs; read only F1-related E5 constraints, task carry-through and D-333 correction; preserve the historical report bytes except frontmatter round and append the explicit closure table.", "observer": "codex-independent-reviewer", "cwd": "P:/av-kit", "scope": "round-4 closure-only recheck of previously resolved F1", "phase": "targeted", "exit_code": null, "result": "pass", "tested_state": "docs/execution/plans/2026-11-06-tts-load-fp16/baseline.ps1 sha256=82a551e81f40696a606bd57191080ab07b8d95f1250e1ecdc9c19c212c2ef2e2 mtime_ns=1794057200360682200; docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/fp16-nan-probe.txt sha256=16691cef9a0b340565c4a771e34f228ca68ee8f949bfe2b791d6b66ed05050b0 mtime_ns=1794024526408142900; docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/fp16-rate-probe.txt sha256=3b6c09bdc449befc55e25e792bb6e9809946548657cd047e473843fad57755a8 mtime_ns=1794024526408142900; docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/fp16_nan_probe.py sha256=9e584ba2419ce350a2c6f25f4eb015f5a0b6ed0e60ce07be2cc1f6836fc08aa9 mtime_ns=1794024526406143200; docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/fp16_rate_probe.py sha256=df1a4eea15adda1baafb84034b904688262a4e33276d7d3a3275cff9d57884dd mtime_ns=1794024526407143000; docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/phonemes.json sha256=91d91708b9f5d8f65393371470d7182f689f58f30bf82f7a2bfc69fa74a42f40 mtime_ns=1794024526408142900; docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/test-set.json sha256=53c941543295b48439b633faf2746b33123c17482207a4a6e99faad6f6760ef3 mtime_ns=1794024526413148200; docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/tts_variant_compare.py sha256=878004afb8203d84729bdac4dd0ac1dea889cfd298e33f0f1ad90a930960472e mtime_ns=1794024526407143000; docs/execution/plans/2026-11-06-tts-load-fp16/human-gate-decision.md sha256=995471128586151296d09d80f0c1500b32d26689fdeb387d26690ddab6a627a2 mtime_ns=1794058274390740500; docs/execution/plans/2026-11-06-tts-load-fp16/identity.py sha256=589412ab9e1294a07fd07ca6470fecfae0023e2651ff030ca45ee74f72c9e00d mtime_ns=1794057169157918600; docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md sha256=0b323a49ea5247a26d45e880fafd3e5f9a41b2376bfe9dd0a397f0c1bc07c85c mtime_ns=1794058424507258900; docs/execution/plans/2026-11-06-tts-load-fp16/models-snapshot.py sha256=331dd604dd0810f12eda13bc600a432f1d33620d2338d020fe4752610b09971a mtime_ns=1794057169157918600; docs/execution/plans/2026-11-06-tts-load-fp16/red-check.py sha256=085569cea36fc48f294d34391aa70edb267fd6a0b6e525d693cd341d9c34b287 mtime_ns=1794057169157160700; docs/execution/plans/2026-11-06-tts-load-fp16/task.md sha256=2e136807621b22e29d7a05a257727252f9c68734612b59d5409ccce661f9d586 mtime_ns=1794058266337304300", "output": "Canonical and Temp round-3 report SHA-256 both 95e42dc888604e22c05fd607c4efc75b83c6bc3cfcccb395db494b0d295022df. All 14 plan-folder files last written by 2026-11-07 13:33:44 UTC (08:33:44 EST), before round-3 dispatch as established by the supplied chronology; Temp round-3 report last written 13:40:11 UTC. E5 still specifies exactly two hashed binary requirements, no-deps, a Temp target, an offline/no-sync child, origin/cache/project checks and no relaxed retry. Round-3 F1 judgment stands; no new finding.", "fresh": true}
```

**Assumptions/open questions:** none newly raised. **Residual risk:** prior execution-only work, including the real E5 fetch/imports, spike and packaged 149-job proof, remains execution evidence; this review certifies plan readiness only. Completion-preflight was consulted and applied only to this review deliverable. No repository file, product task status or uv cache was written. No product test, install, network request, model construction, inference, app, build, smoke or YouTube call ran. The coordinator saves this complete rolling report to the canonical path.

### Verdict

`approved` — round 3's F1 judgment stands on the unchanged plan files. F1 is explicitly closed for the rolling review state; there are zero open blocking findings. Executing the approved plan can deliver the registered intent.
