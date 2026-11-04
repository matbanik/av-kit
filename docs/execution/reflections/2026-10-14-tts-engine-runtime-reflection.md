---
date: "2026-10-15"
project: "tts-engine-runtime"
meus: ["MEU-73", "MEU-74", "MEU-72"]
plan_source: "docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md"
template_version: "2.0"
---

# 2026-10-15 Meta-Reflection

> **Date**: 2026-10-15 (plan written and reviewed 2026-10-14; execution, Windows gate and execution review 2026-10-15)
> **MEU(s) Completed**: MEU-73 `tts-voice-packs-managed`, MEU-74 `tts-language-runtime`, MEU-72 `tts-packaged-onnx-runtime`
> **Plan Source**: `docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**

   - **The packaged smoke.** `PACKAGE_SMOKE` needed two attempts (Row 12). Attempt 1 passed `ONLINE_PROVISION` and `INSTALLER_STAGE`, then the offline `POST /models/load` returned 500. The cause is old: a sideloaded variant is listed as downloaded, but its DB row has no path, so it cannot be loaded. Attempt 1 also showed that spaCy was being read from Mat's real home folder, not from the provisioned models folder, through a stale `sys.path` entry. All three fixes went into the new smoke harness (`tools/smoke_packaged_tts.py`), and no product file changed. Both causes are filed as issue candidates.
   - **The census.** Row 1's census missed one exact-shape assertion (`test_api_tts_models.py`, AC-16.7), which surfaced at row 5 as census S2b and needed a human decision (D-95, TA-14). The census grepped for the touched names, but a dictionary-equality assertion on a route response names none of them.
   - **The Windows gate.** Attempt 1 missed two Electron specs (AC-63.5, AC-49.28) while about 150 node and python processes from other sessions shared the machine. Both passed 10/10 alone, and attempt 2 passed 17/17 with no file changed.
   - **Closeout plumbing.** `handoff-ac` wants every plan AC id named in every handoff, including the ones a MEU does not touch (AC-2, AC-16, AC-23 in the MEU-73 and MEU-72 handoffs). The closeout validator treats any lowercase word in angle brackets as a template placeholder. That caught two approved plan decisions: D-71's man-page argument for `--tie` and D-74's per-voice file name. Both were respelled (`--tie=CHAR`, `voices/VOICE_ID.bin`) without changing their meaning (walkthrough §H1-6).
   - **The execution-review record.** The ledger refused the first record with `target-plan-mismatch`, and no round was consumed. The dispatcher had been started from the main checkout, so its sibling `review_ledger.py` resolved the verdict's relative `target_plan` against `P:/av-kit`, not the worktree. The unchanged verdict was then recorded with the worktree's ledger script.

2. **What instructions were ambiguous?**

   - **The review mode name.** Task row H1-6 says `-Kind implementation`, but the dispatcher accepts only `plan|execution|discovery|handoff|multi-handoff`. The ledger and the JSON verdict say `execution`, while the plan's `review-check` and the report frontmatter say `implementation`. The prompt explained the mapping to the reviewer.
   - **"Opens through the existing external-link path" (AC-74.7).** No such path exists: main denies `window.open` and navigation. It needed a human decision (D-96).

3. **What instructions were unnecessary?**

   None outright. The rule that the evidence table and the task table share a `| N |` row shape is a parser hazard, not an instruction: `cmd_task_state` read the evidence rows as task rows, and H1-1 failed until they were relabelled `| Row N |`.

4. **What was missing?**

   - **A census pass for exact-shape assertions on changed wire types.** When a plan adds fields to a response model, every test that compares a whole response row with `==` must be found, not only tests that name the fields (D-95).
   - **A local eSpeak NG install for LOCAL-ESPEAK.** The build machine has none, so AC-74.11 stays unverified and is filed as an issue.
   - **A live pin check for build inputs.** The FFmpeg pin URL had gone 404 since the last packaging session, and nothing checks it before a gate needs it.

5. **What did you do that wasn't in the prompt?**

   - Ran a flake probe (`--repeat-each 5`) on the two attempt-1 misses before re-running the gate, so attempt 2 was a classified re-run rather than a retry.
   - Proved the Row 12 load 500 from source and from the frozen exe before changing the smoke harness, so the harness fix could not be hiding a regression this plan caused.
   - Kept the attempt-1 gate and smoke artifacts under `C:/Temp/av-kit/` with `-attempt1` suffixes.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **`PACKAGE_SMOKE`.** It found two real product defects outside this plan's fence: the sideload load 500, and the stale spaCy `sys.path` entry. The negative probe proved that the dead proxy really denied the app's own download client.
   - **The `ESPEAK_MAP_PARITY` test (row 6).** Its original `sys.modules` assertion could never pass in the pytest process, which exposed that `avkit_infra.tts` still pulled in `kokoro` → `misaki.espeak` at import (D-98). MEU-72's `IMPORT_HYGIENE` (AC-72.1) then pinned the real fix in a fresh interpreter.
   - **`ta-check`.** It refused two TA ranges whose edges were off by blank separator lines (TA-3a, TA-3b), which kept the "no other assertion changed" claim exact.
   - **`hub` (AC-23.20).** It refused a `gui-actions-index` row whose IPC cell it cannot resolve, which led to D-100's deferral rather than a forced test change.
   - **The execution review (Codex, F1).** `plan_checks.py static` rejected Row 4's D-90..D-94, which only the MEU-73 handoff defined. Its selftest also injected D-99 as an undefined decision after D-99 had been defined. The finding was clerical, but H2-3's `plan-static` would have failed on it.

7. **Which tests were trivially obvious?**

   AC-73.14 and AC-74.10 (the OpenAPI regeneration checks) and AC-73.13 (the MCP wire enum gaining one member). They are parity locks, not behaviour tests.

8. **Did pyright/ruff catch anything meaningful?**

   pyright caught the pair type change in `TtsService.list_voices` (D-89) at every caller before the tests ran. `tsc` caught D-99: `VoiceOut` gained a boolean field, so the `Record<string, string>` cast in `TTSPage.tsx` stopped overlapping. ruff found style issues only.

### Workflow Signal Log

9. **Was the FIC useful as written?**

   Yes. Named contracts (`VOICE_REASON`, `ESPEAK_G2P`, `G2P_ROUTE`, `CHUNK_RULE`, `ONNX_FEEDS`, `SPEC_BUNDLE`, `OFFLINE_SMOKE`, `NEGATIVE_PROBE`) mapped one to one to tests and to the handoff AC tables. Two contracts were too strong as written: the `sys.modules` line (D-98), and "opens" in AC-74.7 (D-96). Both were corrected by human decision before Green.

10. **Was the handoff template right-sized?**

    Mostly. The "Other plan AC references" table is the price of `handoff-ac` naming every plan AC in every handoff. For a three-MEU session, that is about ten rows of "untouched" per handoff. The handoffs again restate gate evidence that `walkthrough.md` holds canonically.

11. **How many tool calls did this session take?**

    Not tracked precisely. There were several hundred across planning, three plan review rounds, 14 execution rows, two gate attempts, two smoke attempts and one execution review round.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**

    No rows were delegated to a subagent. Claude Code (Opus) ran every row locally in one session, with compaction at MEU boundaries. Both reviews went to Codex `gpt-6.1-sol` at `high` effort through `Invoke-CodexDispatch.ps1` (D-80): the plan review in three rounds, and the execution review in one round (approved, one Low finding).

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1 | grouping | When are the gated build-plan edits written? | autonomous | After Session 30's execution review approves | Local Canon | Grouping §8 D-1 (carried). Session 32 wrote its own hub lines at row 13 (D-85), after Session 30 had merged. | — |
| D-2 | grouping | Does `MCP-SETUP-PROMPT` join Session 31? | human | Yes, as MEU-71 | Human-approved | Grouping §8 D-2 (carried). It does not affect this session. | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-3 | grouping | Are the tech-debt rows MEUs? | autonomous | No; a separate debt batch | Local Canon | Grouping §8 D-3 (carried). `TTS-SPACY-SYSPATH-PREPEND` (TECH-DEBT) was absorbed into MEU-73 as its triage note asked (AC-73.12). | — |
| D-4 | grouping | Session order | autonomous | 31 → P2 sessions 32, 33, 34 → P3 → P4 | Local Canon | Grouping §8 D-4 (carried). Session 32 ran after Session 31 merged (S1). | — |
| D-5 | grouping | Keep TTS page work out of the engine session? | autonomous | Yes, Session 35 after Session 33 | Local Canon | Grouping §8 D-5. This is why `TTSPage.tsx` stays unchanged here (D-99). | — |
| D-6 | grouping | Where does the independent MEU scoping review run? | human | Codex scoping review on the grouping draft | Human-approved | Grouping §8 D-6 (carried). | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-7 | grouping | Repair the shared `status_labels` in `meu-status.yaml`? | autonomous | Yes, every row rebuilt from its own status | Local Canon | Grouping §8 D-7 (carried). H1-3's render kept them per-row. | — |
| D-70 | planning | ja/zh voices: add the misaki extras or mark them unavailable? | human | Mark unavailable (`language_unsupported`, 409); follow-up issue | Human-approved | The extras add hundreds of MB and a new licence review. Honest availability now; `TTS-JA-ZH-G2P-EXTRAS` filed at H2-2. | USER_EXPLICIT 2026-10-14 'Mark unavailable (Recommended)' |
| D-71 | planning | Non-English phonemes without shipping GPL code? | autonomous | The user-installed `espeak-ng` CLI as a subprocess; misaki's Apache-2.0 maps ported | Local Canon | Loading a GPL library in process is the grey area D-61 flagged; phonemizer is GPL source. An arm's-length program keeps the TTS runtime GPL-free. | — |
| D-72 | planning | English out-of-dictionary fallback? | autonomous | espeak `EN_E2M` fallback when detected, else none (word skipped) | Local Canon | English stays available without espeak; rare words go silent instead of failing the job. The spaCy guard stops a mid-job network install. | — |
| D-73 | planning | Which ONNX export does the catalog download? | autonomous | `onnx-community/Kokoro-82M-v1.0-ONNX` at a pinned revision; legacy v0.19 paths refused | Research-backed | The shipped vocab and packs are v1.0, and a v0.19 graph mispronounces. A revision-scoped dir stops the sideload from reusing the old file. | — |
| D-74 | planning | Voice pack format and granularity | autonomous | One managed asset of all 54 `.bin` packs | Local Canon | Per-voice assets would need a parameterised asset port, wire and health row. 28 MB at once keeps the MEU-62 shape. `.bin` avoids torch. | — |
| D-75 | planning | Does the PyTorch path keep `KPipeline`? | autonomous | No; both formats share the G2P route and chunking | Local Canon | `KPipeline` reintroduces `misaki.espeak` and lazy `.pt` fetches. | — |
| D-76 | planning | num2words (LGPL-2.1) in the frozen bundle? | autonomous | Bundled as replaceable source, listed in NOTICES | Research-backed | LGPL permits distribution with notice and replaceability, which source collection gives (AC-72.6, AC-72.7). | — |
| D-77 | planning | How is espeak-ng detected? | autonomous | `which`, then the two standard dirs; re-probe per call; version cached | Local Canon | No latch, so "Check dependencies" sees a fresh install without a restart. | — |
| D-78 | planning | Chunking without `KPipeline` | autonomous | `CHUNK_RULE` in `avkit_infra.tts.g2p` | Local Canon | The model limit is 510 tokens, and natural boundaries keep prosody (AC-72.3). | — |
| D-79 | planning | How are the gate and smoke bound when commits are the user's? | autonomous | The driver runs both; both bind to `WORKTREE_IDENTITY`; Mat commits after review | Local Canon | The same evidence strength as a commit sha, without auto-committing. H1-2 bound both to `cd879e6e`. | — |
| D-80 | planning | Reviewer route | autonomous | Codex `avkit_independent_reviewer` via `Invoke-CodexDispatch`, effort high; caps 3 and 6 | Local Canon | Vendor-distinct from the author. Used for both loops. | — |
| D-81 | planning | Free-text reason or closed code? | autonomous | A closed `VOICE_REASON` enum; the UI owns the wording | Local Canon | Closed sets fail closed and let the GUI and MCP clients branch. | — |
| D-82 | planning | When does Session 32 split? | autonomous | At row 8 if coordinator context > ~50% | Local Canon | Checked at row 8: 16.4% used, so no split (walkthrough §Split). | — |
| D-83 | planning | `COUNT_FLOORS` source | autonomous | Session 30's gate; S1 if Session 31 merges first | Local Canon | S1 fired at row 2, and the floors were re-derived as 800 / 137 / 655 on the merged tree. | — |
| D-84 | planning | MCP surface for the new asset | autonomous | Add `tts_voice_packs` to `TTS_ASSET_WIRES`; no new audit step | Local Canon | Parity with the API enum; no action is added, so the census is unchanged (AC-73.13). | — |
| D-85 | planning | How far does the hub reconciliation reach? | autonomous | Only the lines this session's contracts change | Local Canon | Other missing matrix rows belong to sessions not yet run. Done at row 13. | — |
| D-86 | planning | Which MEU owns the G2P router and the `KPipeline` removal? | autonomous | MEU-72 (row 10) | Local Canon | Each MEU's ACs trace to its own spec section; the `G2P_SEAM` fixture kept rows 2 and 5 stable across the rewrite. | — |
| D-87 | planning | Does "no GPL code" cover the shipped BtbN FFmpeg build? | human | Scope the anchor to the TTS runtime; disclose FFmpeg in NOTICES; ship its LICENSE.txt; file `FFMPEG-GPL-BUILD` | Human-approved | Swapping the build changes Convert's encoders, outside this session. Plan review R1 F1 found the original anchor false; the user narrowed it. | USER_EXPLICIT 2026-10-14 'Scope anchor + notice (Recommended)' |
| D-88 | planning | How does the packaged smoke prove generation with no network? | autonomous | A fresh frozen process outside the checkout, every proxy at a dead port, plus `NEGATIVE_PROBE` | Local Canon | A firewall rule needs elevation on every run. The negative probe proves the denial for the app's own client. | — |
| D-89 | execution | Census S2: `VoiceConfig` is fixed at five fields by AC-2.10/2.12 and spec 01. How is availability carried? | human | A separate frozen `VoiceAvailability` value paired with each `VoiceConfig` | Human-approved | Availability depends on the runtime; `VoiceConfig` is the static catalog row. No test amendment and no spec 01 change. | USER_EXPLICIT 2026-10-15 'Separate value (Recommended)' (AskUserQuestion, census S2) |
| D-90 | execution | Row 2: TA-3a stops at line 610, but line 611 asserts the message of the replaced failure | autonomous | Widen TA-3a to 597-611 | Local Canon | Line 611 checks the error text of the exact failure being replaced, so it changes with 603-610. No AC or TA id changes, and `ta-check` enforces the new range. | — |
| D-91 | execution | S1: the branch was fast-forwarded to `c72fc44` during row 2. How do the baseline and floors follow? | autonomous | `baseline.sha` → `c72fc44`; `COUNT_FLOORS` 800 / 137 / 655; the prereq S1 guard moves to `c72fc44` | Local Canon | No MEU-73 product file had changed yet, so `ta-check` and `api-scope` diff against the tree MEU-73 builds on. | — |
| D-92 | execution | AC-73.10 Downloading tests flaked because a refetch during the first fetch is deduped into it | autonomous | Add the setup helper `waitForRuntimeDownloading()`; no assertion changes | Local Canon | Without it, the flipped state arrives at the next 1 s poll, just past `vi.waitFor`'s default. Only the setup is synchronised. | — |
| D-93 | execution | The `useEffect`-keyed settle hook missed Downloading → Failed in about 3 of 5 runs | autonomous | `useRefreshDependenciesOnSettle` subscribes to QueryCache `updated` events | Local Canon | React can batch two runtime results into one render, so Downloading is never rendered. It is a real product race, and it passed 6/6 after the change. | — |
| D-94 | execution | pyright rejects a torch tensor for `KPipeline`'s voice parameter, which is annotated as an optional `str` | autonomous | Type the tensor `Any` at the one call site, with a comment citing kokoro `load_voice` | Research-backed | The runtime accepts the tensor; only the annotation is narrow. MEU-72 then removed `KPipeline`. | — |
| D-95 | execution | Census S2b: AC-16.7 asserts the exact `/tts/voices` row and is not in `TEST_AMENDMENTS` | human | Add TA-14: the expected dict gains `available` and `reason` | Human-approved | AC-16.7's control is the facade; the exact dict is incidental. Omitting the fields would contradict AC-74.3. | USER_EXPLICIT 2026-10-15 'Add TA-14 (Recommended)' (AskUserQuestion, census S2b) |
| D-96 | execution | AC-74.7's link "opens through the existing external-link path", which does not exist | human | Show the URL as text plus a Copy link button using the existing clipboard IPC | Human-approved | An `openExternal` channel would add three files and a main-process surface for one link. | USER_EXPLICIT 2026-10-15 'URL + Copy link (Recommended)' (AskUserQuestion, eSpeak link) |
| D-97 | execution | Where is `TtsRuntimeError` defined? | autonomous | In `espeak.py`, as a `DomainError` subclass | Local Canon | The contract names the error but not its module; beside its only raiser stays inside the Files Modified fence. | — |
| D-98 | execution | The parity test's `sys.modules` assertion can never pass in the pytest process | human | An AST import scan of `espeak.py`; the runtime check stays with MEU-72 `IMPORT_HYGIENE` | Human-approved | A process-wide check measures whatever else pytest imported. The scan tests the adapter's own source. | USER_EXPLICIT 2026-10-15 'AST import scan (Recommended)' (AskUserQuestion, parity fix) |
| D-99 | execution | `VoiceOut` gains a boolean, and `tsc` fails at `TTSPage.tsx:126` | autonomous | Type `useVoices` rows as `VoiceOut[]` at the source | Local Canon | A direct consequence of the plan's field types; a type-only line with no runtime effect. Editing `TTSPage.tsx` would touch a file no plan table lists. | — |
| D-100 | execution | The Copy link button has no test id and no index row | autonomous | Add the test id and its registry line; defer the index row | Local Canon | The canon requires both, but the immutable AC-23.20 audit cannot resolve a `writeClipboardText` cell (`gui-actions-audit.test.ts:66-77`). Deferred with "Copy log path" as one follow-up issue. | — |

D-90 to D-94 are the MEU-73 execution decisions. The MEU-73 handoff recorded them, and the H1-6 F1 correction copied them verbatim into the plan's `decision_log`. The execution review added no decision, because F1 was a clerical correction. The triage decisions in `known-issues.yaml` are cited in prose only.

---

## Pattern Extraction

### Patterns to KEEP
1. **Stop on census surprises.** S2 and S2b both stopped for a human decision before Green, and neither became a silent test edit.
2. **Prove a pre-existing cause before fixing a harness.** The Row 12 load 500 was reproduced from source and from the frozen exe against baseline code, so the smoke harness change could not be hiding a regression.
3. **Classify a gate miss before re-running.** A `--repeat-each` probe on the two attempt-1 misses separated host-load flakes from a regression.
4. **Bind the gate and the smoke to one tree identity.** `WORKTREE_IDENTITY` let the uncommitted tree carry commit-strength evidence (D-79).

### Patterns to DROP
1. **Restating gate evidence in every handoff.** Three handoffs each carry the same H1-2 JSON block; the walkthrough is canonical.

### Patterns to ADD
1. **Census: exact-shape assertions on every changed wire model.** Search the tests for `==` comparisons against whole response rows of any model the plan extends, not just for the field names.
2. **A build-input liveness check before a packaging gate.** HEAD each pinned download URL (FFmpeg) in the preflight, so a dead pin is a decision before the gate rather than a 404 in the middle of it.
3. **The closeout validator's placeholder regex in `plan-static`.** Run it over the plan's `decision_log` at plan time, so angle-bracket tokens are caught before approval.
4. **Dispatch reviews from the worktree.** Start `Invoke-CodexDispatch.ps1` with the worktree as the working directory, so the ledger it pairs with resolves the plan path inside the worktree.

### Calibration Adjustment
- Estimated time: one planning session plus one execution session, one gate loop and one or two review rounds.
- Actual time: planning and three plan review rounds on 2026-10-14; execution, two gate attempts, two smoke attempts and one execution review round on 2026-10-15.
- Adjusted estimate for similar MEUs: for packaging work, budget one extra smoke attempt. A fresh frozen process exposes state assumptions (home folder, sideloads) that the dev tree hides.

---

## Next Session Design Rules

```
RULE-1: A census for a plan that extends a response model greps the tests for whole-row equality against that route, not only for the touched names.
SOURCE: Census S2b (test_api_tts_models.py AC-16.7 compared the /tts/voices row as a four-key dict; found at row 5, not row 1).
EXAMPLE: "grep available|reason|VoiceOut" → plus "grep '== {' near GET /tts/voices in tests/".
```

```
RULE-2: A packaged smoke runs every frozen process with a fresh HOME and app-data, and records which folder each managed asset was read from.
SOURCE: PACKAGE_SMOKE attempt 1 (spaCy read from Mat's ~/.avkit through a stale sys.path entry).
EXAMPLE: "spaCy already_ready" accepted → "spaCy ready from s32-smoke-models" asserted.
```

```
RULE-3: The plan's gate preflight checks every pinned external download (HEAD request) and stops before stage 1 when one is gone.
SOURCE: Row 9 (BtbN FFmpeg pin 404; the build used a cached archive with a matching SHA).
EXAMPLE: 404 during the provisioning step → "pin dead" decided in the preflight.
```

---

## Next Day Outline

1. Session 33 per the 2026-10-09 grouping (P2), via `/create-plan`. Session 32 touched `mcp-server` (`TTS_ASSET_WIRES`), so run `/mcp-audit` before or with it.
2. Triage the Session 32 candidates: `MODEL-SIDELOAD-LOAD-500` and `TTS-SPACY-SYSPATH-STALE-DIR` (product), `FFMPEG-PIN-URL-404` and `INSTALLER-SHIPS-FFMPEG-ZIP` (packaging), `NOTICES-SPACY-TRANSITIVE`, `FETCH-FFMPEG-EXIT-CODES`, `GUI-AUDIT-CLIPBOARD-RESOLVER`.
3. Install eSpeak NG 1.52 on the build machine and run LOCAL-ESPEAK (`TTS-ESPEAK-LIVE-PATH-UNVERIFIED`).
4. Bake in RULE-1 to RULE-3.
5. Review route: Codex `gpt-6.1-sol` through `Invoke-CodexDispatch.ps1`, unless the user changes it.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | not tracked precisely (several hundred) |
| Time to first green test | MEU-73 Green on 2026-10-15, right after its Red receipts |
| Tests added | pytest 655 → 803 (+148); Vitest 800 → 816 (+16); Electron 137 → 138 (+1, AC-74.9); MCP wire cases for AC-73.13; 14 existing expectations amended exactly as approved (TA-1 to TA-14, `ta-check` pass) |
| Codex findings | Plan review: three rounds, approved at round 3. Execution review: R1 approved (1 Low, non-blocking: F1, stale decision references in the plan verifiers; fixed) |
| Handoff Score (X/7) | 6/7 (the review found no handoff defect, but `handoff-ac` failed until the untouched-AC rows were added at H1-5) |
| Rule Adherence (%) | 90 |
| Prompt→commit time | 2026-10-14 → 2026-10-15 (commit by Mat after review) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Red receipts for every MEU before its Green |
| No test expectation change without approval | AGENTS.md §Testing & TDD | Yes. TA-1 to TA-13 approved in the plan review, TA-14 by the human (D-95); `ta-check` passes |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex wrote every verdict, and the reports were copied verbatim |
| Never commit or push | user standing rule | Yes. The tree is uncommitted; Mat commits from the H2-3 draft |
| Census before Red | plan row 1 | **Partly.** The census missed AC-16.7's exact-dict assertion, found at row 5 (D-95) |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "session-32-tts-engine-runtime-2026-10-15"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 2}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, execution_session, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: [timestamp]
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - docs/build-plan/03-service-layer.md
    - docs/build-plan/07-distribution.md
    - docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md
    - docs/execution/plans/2026-10-14-tts-engine-runtime/task.md
    - .agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md
decisive_rules:
  - P1:tests-before-production-corrections
  - P1:human-approval-for-test-changes
  - P1:independent-review-no-self-approval
  - P1:no-tolerated-failure-in-authoritative-gate
  - P1:gate-failure-preserve-classify-decide
conflicts:
  - "Task row H1-6 names -Kind implementation, but the dispatcher accepts only execution; the ledger says execution while the review file and review-check say implementation."
  - "handoff-ac requires every plan AC id in every handoff, so each MEU handoff lists ACs it never touched as 'untouched' rows."
  - "The closeout validator's placeholder regex refused man-page and path syntax (a lowercase word in angle brackets) inside approved plan decisions."
note: "Session 32 makes the Kokoro voice packs one managed asset (MEU-73), adds per-voice availability with eSpeak NG detected as a user-installed CLI and ja/zh honestly unavailable (MEU-74), and ships av-kit's own G2P with a torch-free frozen ONNX runtime, NOTICES and an offline packaged smoke (MEU-72). The Windows gate of record is attempt 2 at WORKTREE_IDENTITY cd879e6e (17/17; pytest 803, Vitest 816, Electron 138/0/0/0); PACKAGE_SMOKE generated 41,400 samples offline from the installer's backend. The plan review approved at round 3, and the execution review approved at round 1 with one Low clerical finding (F1), fixed."
slim_candidate: ["The three MEU handoffs restate the same H1-2 gate JSON that walkthrough.md holds canonically", "handoff-ac's every-AC-in-every-handoff rule produces 'untouched' rows with no review value"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 3, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 3, medium: 1, low: 0}
    - {review: plan, round: 2, critical: 0, high: 1, medium: 0, low: 1}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 0, low: 1}
  churned_findings: 1
  finding_categories: {claim_to_state_drift: 1, boundary_validation: 1, weak_test: 1, contract_drift: 2, fix_generalization_miss: 1, stale_reference: 1}
  verdicts: {changes_required: 2, approved: 2}
meu_work_classes: [mixed, correctness, correctness]
```
