---
date: "2026-10-01"
project: "tts-repair"
meus: ["MEU-62", "MEU-63", "MEU-64"]
plan_source: "docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md"
template_version: "2.0"
---

# 2026-10-01 Meta-Reflection

> **Date**: 2026-10-01 (session started 2026-09-30)
> **MEU(s) Completed**: MEU-62 `svc-tts-runtime-assets`, MEU-63 `gui-tts-model-manager`, MEU-64 `gui-tts-text-panel`
> **Plan Source**: `docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**

   The authoritative Windows gate took seven attempts.
   - Attempt 1 failed on a pre-existing main failure: the 2026-09-26 adoption verifier pins `AGENTS.md`/`GUARDRAILS.md` bytes, and f34e8a9 edited them (A-2 rebind).
   - Attempt 2 surfaced a startup reload race in `ui/src/main/index.ts`: every e2e seam reloads, the first `loadFile` aborts, and the window was never shown and was throttled to about 1 fps (A-3).
   - Attempts 3 and 4 found a MEU-62 test-isolation defect twice. My first fix was proven on one file only; the leak crossed files.
   - Attempt 5 hit Electron 42's lazy-install race in parallel Vitest workers (A-5).
   - Attempt 6 exposed a `SettingsRail` click-lock race that A-3 had un-masked (A-6), plus my own AC-63.5 poll-timing flake.
   - Attempt 7 passed everything except one drag miss that Mat attributed to his own mouse input (A-7, accepted with the check still reporting FAIL).

   Each loop cost a Windows round-trip. Before that, the real-network `tts-live-pre` found two product defects in the container that every faked suite missed: Kokoro output overshooting ±1.0, and kokoro 0.9.4 `KPipeline.Result` chunks dropping the phonemes.

2. **What instructions were ambiguous?**

   The "quiet machine" precondition says nothing about other agents that start a test run *during* the gate (attempts 5–7). Also unclear: whether the local agent's "sorted position" instruction or the decision record's "append" governs (A-2 note). In the request I wrote, "expected" meant "total", though Playwright's `expected` means passed, so the attempt-7 e2e count was wrong.

3. **What instructions were unnecessary?**

   Per-MEU repetition of the project-wide gate evidence, again. The walkthrough already holds the canonical record.

4. **What was missing?**

   - **Hermeticity of `~`.** The plan had no rule that every test building services must not see the real user home. Startup activation of the default `~/.avkit/models` is process-wide (`sys.path`).
   - **A container proxy for Windows-only timing.** For example, Chromium's Windows smooth-scroll duration. It was found only by simulating a 1.5 s scroll.
   - **A gate-side materialization of Electron**, as the container's `electron-setup` already had.

5. **What did you do that wasn't in the prompt?**

   - Fixed two live-only product defects (D-33, D-34).
   - Root-caused and fixed the startup reload race (A-3) and the rail click-lock race (A-6) as product fixes, each under an explicit human carve-out.
   - Added failure-time drag diagnostics (A-4), which later turned an "undiagnosable" miss into a one-line explanation.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - `tts-live-pre` (real network): Kokoro overshoot (generate failed) and the `KPipeline.Result` phoneme drop (0.325 s of noise).
   - `startup-reveal.test.ts` (Red 6/6): the window was never shown after an early reload, and boot aborted before its tail.
   - The new A-6 spec (Red 3/3): the rail highlight lands on Capture after a slow smooth scroll.
   - AC-62.x pytest: the pre-job 409 and the every-`Failed`-has-a-reason contract.
   - AC-64.6 Electron: Speed/Format below the fold at the default window (it confirmed LOCAL_REPRO R5).
   - Mat's full `pytest tests/` run: the cross-file `sys.path` leak, which a single-file run cannot see.

7. **Which tests were trivially obvious?**

   `test_ac_62_9`'s `spacy.cli.download` spy (review F4) cannot fail under the engine fakes. The decisive assertions in that test are elsewhere.

8. **Did pyright/ruff catch anything meaningful?**

   pyright caught an untyped `.cpu()` on a torch tensor in `_as_float32_pcm`. ruff caught only long lines, one of them in my own parity test before the pre-gate would have.

### Workflow Signal Log

9. **Was the FIC useful as written?**

   Yes. The single-statement contracts (`REQUIRED_TTS_ASSETS`, `RUN_BAR_ERROR`, `MODEL_ACTION`, `VOCAB_LOCATION`) made Red tests direct. The `TEST_AMENDMENTS` census missed two Python sites, which pre-gate attempt 1 caught: a `FIXTURE_REPAIRS` health fake, and a TA-9 count in `test_api_downloads.py`.

10. **Was the handoff template right-sized?**

    Mostly. The AC-coverage validator matches AC *families* (`AC-62`), so every handoff must list every plan family, including other MEUs' families; that added a cross-reference table to each.

11. **How many tool calls did this session take?**

    Not tracked precisely; several hundred across planning, three MEUs, seven Windows gate loops and closeout.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**

    No implementation rows were delegated. The plan review (2 rounds) and the execution review (1 round) were dispatched to a separate-context Fable 5.1 Agent subagent, the user-authorized same-vendor route. Neither needed rework. Windows-gate execution was delegated to Mat's local agent through prompts; its reports were precise, and twice better diagnosed than my request had anticipated (the A/B for A-3 and the attempt-4 cross-file leak).

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1 | grouping | How are the TTS runtime assets provisioned? | human | Managed downloads in the model-manager flow plus Dependencies readiness rows; nothing bundled | Human-approved | Bundling adds about 13 MB and pins the spaCy model; a pip extra cannot reach a packaged app (grouping §8 D-1, triage D-22). | USER_EXPLICIT 2026-09-30 'D-22: follow you recommendation' |
| D-2 | grouping | Residual MEUs under original phases or a new Phase 12? | autonomous | Original phases with `(residual)` sections | Local Canon | The MEU-59/60/61 precedent; a new phase would split canon across two docs (grouping §8 D-2). | — |
| D-3 | grouping | One TTS session or an engine/page split? | autonomous | One session with a split flag at the MEU-62 handoff | Local Canon | A shared `TTSPage.tsx`; page-first could not verify a Failed-free run bar (grouping §8 D-3). | — |
| D-4 | grouping | Where does the MCP audit sit? | autonomous | Session 28, after the TTS repair | Local Canon | The baseline should record a working `tts.generate` (grouping §8 D-4). | — |
| D-5 | grouping | Are the TECH-DEBT/DEFER rows MEUs in this batch? | autonomous | No | Local Canon | `issue-triage.md` routes TECH-DEBT to a debt batch and DEFER out of scope (grouping §8 D-5). | — |
| D-6 | grouping | Zoom wheel semantics | autonomous | Plain wheel zooms about the cursor | Research-backed | It matches the user's words and image-viewer convention (grouping §8 D-6). | — |
| D-7 | grouping | Rename the header palette control? | autonomous | "Commands Ctrl+K" with a command icon | Research-backed | It opens the command palette, not Settings (grouping §8 D-7). | — |
| D-8 | planning | Does the PyTorch variant need `config.json` too? | autonomous | Every variant requires `VOCAB_LOCATION`; PyTorch passes it as `KModel(config=…)` | Research-backed | kokoro 0.9.4 `KModel(config=None)` fetches from Hugging Face at load (plan D-8). | — |
| D-9 | planning | Where does the vocab live and how is it found? | autonomous | One `models_dir/config.json`, resolved per call | Local Canon | A single file for every variant, and a changed setting takes effect without a restart (plan D-9). | — |
| D-10 | planning | Which loads trigger spaCy, and which generations need it? | autonomous | Any load; generate needs it for lang `a`/`b` or the `chunk` step | Research-backed | misaki `en.G2P` and `prepare._chunk` both load spaCy (plan D-10, Review R1 F3). | — |
| D-11 | planning | How does `en_core_web_sm` become importable without pip? | autonomous | Pinned, sha256-verified wheel, extracted atomically, put on `sys.path` | Research-backed | No pip at runtime; a zip-slip guard (plan D-11). | — |
| D-12 | planning | Which endpoint does asset Get use? | autonomous | `POST /models/download` takes exactly one of a `variant_id` or an `asset` body | Local Canon | "No new REST route" (plan D-12). | — |
| D-13 | planning | How does the failure reason reach the Console? | autonomous | `CONSOLE_FIELDS` appended, then redacted | Local Canon | Other events stay byte-identical (plan D-13). | — |
| D-14 | planning | The asset row shape | autonomous | `TtsAssetOut{available, version, state}` | Local Canon | A superset of the existing rows (plan D-14). | — |
| D-15 | planning | Test ids for the single model action | autonomous | `data-testid` follows `MODEL_ACTION` | Local Canon | Registry names are kept (plan D-15). | — |
| D-16 | planning | Where does `language-select` go? | autonomous | A compact select in the popup header, ANDed with the query | Local Canon | It retains the functionality (plan D-16). | — |
| D-17 | planning | Default selection; when the preview clears | autonomous | Loaded → first downloaded → first; preview unmounts on edit/Apply | Local Canon | A stale preview misleads (plan D-17). | — |
| D-18 | planning | MEU-63 scope after LOCAL_REPRO R2 did not reproduce | human | A: keep MEU-63 as scoped | Human-approved | It rests on the user's explicit product decision; MEU-62 brings back the mixed Get states (plan §D-18). | USER_EXPLICIT 2026-09-30 'proceed, D-18 A' |
| D-19 | execution | What does `model-manager` mark? | autonomous | The "Model details" panel, inline beside the picker | Local Canon | It keeps every AC-56.6 Electron expectation (MEU-63 handoff D-19). | — |
| D-20 | execution | Where does the vocab fetch live, given the `ModelCatalogPort` pin? | autonomous | Behind `TtsAssetPort` (an injected `fetch_vocab`) | Local Canon | Avoids changing the pinned port methods (MEU-62 handoff D-20). | — |
| D-21 | execution | How does infra name the spaCy model? | autonomous | `SPACY_MODEL` in the domain | Local Canon | Dependency direction (MEU-62 handoff D-21). | — |
| D-23 | execution | Service/response shape for asset downloads | autonomous | `download_asset`; a null `variant` plus `asset`; ready → 409 | Local Canon | Callers stay byte-compatible (MEU-62 handoff D-23). | — |
| D-24 | execution | Targeted pytest with the baseline env-bound failure | autonomous | `pytest_paths_ok` (failed set ⊆ baseline) | Local Canon | The same declared rule on a subset (MEU-62 handoff D-24). | — |
| D-25 | execution | UI asset body schema | autonomous | A separate strict schema | Local Canon | `buildDownloadBody` callers stay unchanged (MEU-62 handoff D-25). | — |
| D-26 | execution | Asset chip wording and back-compat | autonomous | Ready/Missing/Downloading; rows only when present | Local Canon | Never fabricate a state (MEU-62 handoff D-26). | — |
| D-27 | execution | Where the `MODEL_ACTION` test-id map lives | autonomous | In `TTSPage.tsx` | Local Canon | The AC-22.22 source pin (MEU-63 handoff D-27). | — |
| D-28 | execution | Refresh after a background download | autonomous | Invalidate on the Downloading → other transition | Local Canon | Completion is only visible in the runtime (MEU-63 handoff D-28). | — |
| D-29 | execution | Combobox match fields and order | autonomous | id, description, language; catalog order | Local Canon | The wire has no `name`; AC-56.4 order (MEU-64 handoff D-29). | — |
| D-30 | execution | Where the combobox test ids live | autonomous | The page passes `testIds` | Local Canon | The AC-22.22 pin; `testId`-prop idiom (MEU-64 handoff D-30). | — |
| D-31 | execution | The chip before the catalog loads | autonomous | "Loading voices…" | Local Canon | Never fabricate a state; the TA-5 race (MEU-64 handoff D-31). | — |
| D-32 | execution | When the voice popup closes | autonomous | Escape or an outside press; select keeps it open | Research-backed | APG combobox; AC-56.4 multi-activation (MEU-64 handoff D-32). | — |
| D-33 | execution | Real Kokoro output exceeds ±1.0 | autonomous | Clip in `_as_float32_pcm` | Research-backed | Matches the reference 16-bit write; the writer contract stays strict (MEU-62 handoff D-33). | — |
| D-34 | execution | Reading kokoro 0.9.4 `KPipeline.Result` chunks | autonomous | `_chunk_part` reads fields or tuple positions | Research-backed | Handles the pinned release and tuple fakes (MEU-62 handoff D-34). | — |
| A-1 | planning | Where do execution and the authoritative gate run? | human | Split like Sessions 25/26: container pre-gate, then Windows `WINDOWS_GATE` + `TTS_LIVE` run by Mat | Human-approved | Windows-only stages and real network (human-gate-decision.md §A-1). | USER_EXPLICIT 2026-09-30 'Split like Sessions 25/26 (Recommended)' |
| A-2 | execution | Attempt 1: a pre-existing adoption-verifier failure | human | Rebind the 2026-09-26 adoption records on Windows | Human-approved | The A17 precedent; a record-only change (human-gate-decision.md §A-2). | USER_EXPLICIT 2026-09-30 'Rebind records (Recommended)' |
| A-3 | execution | Attempt 2: the startup reload race | human | Product fix: reveal on `ready-to-show`; boot survives an aborted load | Human-approved | Removes the root cause for all 6 seam specs (§A-3). | USER_EXPLICIT 2026-10-01 'Product fix (Recommended)' |
| A-4 | execution | A drag-over miss after A-3 | human | Harden and instrument the download-queue drag helpers | Human-approved | Makes a recurrence diagnosable (§A-4). | USER_EXPLICIT 2026-10-01 'Harden + instrument (Recommended)' |
| A-5 | execution | Attempt 5: the Electron lazy-install race | human | The gate `npm-ci` stage runs `install.js` serially | Human-approved | The twin of the container's `electron-setup` (§A-5). | USER_EXPLICIT 2026-10-01 'Gate-script fix (Recommended)' |
| A-6 | execution | Attempt 6: the Settings-rail click lock | human | The lock lasts until the scroll settles | Human-approved | A real Windows bug un-masked by A-3 (§A-6). | USER_EXPLICIT 2026-10-01 'Product fix (Recommended)' |
| A-7 | execution | Attempt 7: one drag miss from human input | human | Accept the result; `windows-gate-check` still FAIL | Human-approved | The miss was caused by the user's interaction; the waiver change to the check was blocked by the safety system (§A-7). | USER_EXPLICIT 2026-10-01 'accept the explanation … no need to redo the run' + option 3 |

D-22 was not used, to avoid a collision with triage D-22. The triage decisions in `known-issues.yaml` are cited in prose only.

---

## Pattern Extraction

### Patterns to KEEP
1. **A real-network live check in the container before any Windows request.** It found both live-only product defects without spending a Windows round-trip.
2. **Failure-time diagnostics in flaky helpers.** One A-4 line turned "undiagnosable" into "human input".
3. **Proving Red for gate-found defects with a deterministic container reproduction.** Examples: a forced early reload, a fake home spaCy install, a simulated 1.5 s scroll.

### Patterns to DROP
1. **Scoping a hermeticity fix to the file where the symptom appeared.** The attempt-3 fix was proven on `test_tts_assets.py` alone; the leak was process-wide.

### Patterns to ADD
1. **Every test that builds services runs with the real home unreachable.** This is now enforced suite-wide by `tests/conftest.py` `_restore_import_path`, plus the per-file `isolated_home`.
2. **Verify the quiet-machine precondition for the whole gate run**, not only at its start. Other agents' recurring test runs must be paused.

### Calibration Adjustment
- Estimated time: one session with one Windows round-trip.
- Actual time: about two days, with seven Windows round-trips.
- Adjusted estimate for similar MEUs: when a session touches the Electron main process, timing-sensitive UI, or user-home state, plan for at least three Windows gate loops.

---

## Next Session Design Rules

```
RULE-1: Any process-wide state a service adds (sys.path, env, caches) must be undone per test, suite-wide.
SOURCE: WINDOWS_GATE attempts 3 and 4 (spaCy install leaked from ~/.avkit across test files).
EXAMPLE: per-file isolated_home only → tests/conftest.py autouse sys.path restore after every test.
```

```
RULE-2: A gate failure on Windows-only timing gets a deterministic container replay before any fix.
SOURCE: A-6 (Windows smooth scroll outlasting an 800 ms lock; replayed with a 1.5 s scroll).
EXAMPLE: "can't reproduce here" → override scrollIntoView with a slow animation, prove Red, then fix.
```

```
RULE-3: Gate requests state the counts in the runner's own vocabulary.
SOURCE: Attempt 7 count note (Playwright "expected" = passed, not total).
EXAMPLE: "e2e 116 expected" → "e2e 118 total, all expected (passed), 0 unexpected, 0 flaky".
```

---

## Next Day Outline

1. Session 28: the MCP audit (grouping D-4), with a working `tts.generate` in its baseline.
2. Follow-ups filed from this session's review: the Settings asset row never leaves "Downloading" (F1), and `sys.path.append` for the spaCy dir (F3).
3. Keep the A-4 drag diagnostics and the A-5 gate stage; reuse the startup-reveal spec as a guard.
4. Review route: the same user-authorized Fable 5.1 subagent unless the user changes it.
5. Time estimate: one session plus at least one Windows gate loop.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | not tracked precisely (several hundred) |
| Time to first green test | MEU-62 Green on day 1 |
| Tests added | 21 pytest, 30 Vitest/MCP, 8 Electron (counted from the session diff) |
| Codex findings | Plan review: R1 10 (3 High), R2 8 (0 High). Execution review: R1 6 (0 High; 2 Medium, 4 Low), approved |
| Handoff Score (X/7) | 6/7 (review F5: two line-range drifts) |
| Rule Adherence (%) | 90 |
| Prompt→commit time | 2026-09-30 → 2026-10-01 |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes, including every gate-found fix (A-3, A-6, D-33, D-34, isolation) |
| No test expectation change outside `TEST_AMENDMENTS` without approval | AGENTS.md §Testing & TDD | Yes. Two census misses were applied under TA-9/`FIXTURE_REPAIRS` and disclosed; my own test timing fixes were disclosed |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes (Fable 5.1 subagent wrote both verdicts) |
| Flake is not a root cause | AGENTS.md / GUARDRAILS | Yes for attempts 2–6. Attempt 7 was accepted on the user's explanation, recorded as A-7 |
| Hermetic tests (no reliance on real user state) | AGENTS.md §Testing | **No** at first. The attempt-3 fix was incomplete; fixed suite-wide in attempt 4 |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "session-27-tts-repair-2026-09-30"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 2}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: planning_contract, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, plan_critical_review, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/docs/cloud-local-collaboration.md
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - docs/build-plan/03-service-layer.md
    - docs/build-plan/11-page-layout.md
    - docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md
    - docs/execution/plans/2026-09-30-tts-repair/task.md
    - docs/execution/plans/2026-09-30-tts-repair/human-review-decision.md
    - docs/execution/plans/2026-09-30-tts-repair/human-gate-decision.md
decisive_rules:
  - P1:tests-before-production-corrections
  - P1:independent-review-no-self-approval
  - P1:human-approval-for-test-changes
  - P1:no-tolerated-failure-in-authoritative-gate
  - P1:flake-is-not-a-root-cause
conflicts:
  - "The zero-tolerance authoritative gate met a failure the user attributed to his own input (A-7). A waiver-aware check change was blocked by the session safety system, so H1-6 closed on the user's explicit acceptance while windows-gate-check still reports FAIL."
  - "The review workflow dispatches through the Codex CLI, absent on the web platform; the user directed a same-vendor Fable 5.1 subagent route (human-review-decision.md)."
  - "The Priority 0 RTK receipt contract assumes rtk, which the container lacks; receipts used plain redirects with immediate exit capture."
note: "Session 27 makes TTS produce audio (Windows TTS_LIVE: missing→ready, a 2.075 s WAV) and fail visibly, and ships the model picker and text-panel UX. Execution review approved in Round 1 (0 blocking). Seven Windows gate attempts; five gate-found defects were fixed under explicit A-decisions or as our own defects, each proven Red first."
slim_candidate: ["The AC-coverage validator's family-level matching forces every handoff to list every other MEU's AC families; a per-MEU scope key would remove the cross-reference tables"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 2, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 3, medium: 4, low: 3}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 3, low: 5}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 2, low: 4}
  churned_findings: 0
  finding_categories: {contract_drift: 3, weak_test: 2, claim_to_state_drift: 2, other: 4}
  verdicts: {changes_required: 1, approved: 2}
meu_work_classes: [correctness, mixed, mixed]
```
