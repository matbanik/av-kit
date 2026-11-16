---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "tsr-plan-2026-11-15-text-scrub-residuals"
round: 2
---

# Critical Review: 2026-11-15-text-scrub-residuals

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Intent Anchor

a lone surrogate or a control character in a transcript channel's extract title or in a caption port's title never fails job creation or a fetch and never reaches a stored row or a written file, and on Windows the Console and the download log lines show the home folder's 8.3 short form as `~`, just as they show the long form.

Intent achieved: `yes` for the plan specification. Executing the revised plan supplies the missing native-success proof as well as the intended behavior. This is plan approval, not a claim that the implementation already exists or its product suites passed.

## Scope

Rechecked the full working-tree implementation plan and task, with particular attention to D-927, AC-148.8/.9 and the empty-lookup mutant. Revisited the grouping's Session 77 scope, the two issue records, build-plan residual contracts, relevant production code and regression fixtures, planning receipts and reusable checker sources. Claude Code/Anthropic authored the plan; Codex is its independent reviewer.

Plan SHA-256: `ecc63c989fc720d4d448aba9a00d404a868b50b942581abca2f71fb9047a0cd8`. Task SHA-256: `c214552a5e26c2012eb6c782f44fdcad5274f3b7e3938b3f59fea1be3e560d24`. Only the two Markdown files currently exist in this plan folder. All six scripts are explicitly scheduled: row 0 creates/copies the baseline and reusable checkers; row 3 creates the mutant plugin; H1-2 creates the session gate. Their absence is consistent with unstarted execution. The scoped product/build-plan diff query returned no paths, and implementation rows remain unchecked.

The round-1 Findings table below is preserved verbatim as history. Its open status describes round 1; the round-2 Prior Pass Summary closes R1-F1. The frontmatter counts this round's new findings: zero.

Applied PR-1 through PR-9 to delivery substance, within the user's explicit exclusion of process-paperwork findings. The request's existing execution authorization governs the plan's stale human-wait wording. Session commits remain unauthorized. No repository file was edited; no pytest, Vitest, npm, uv sync/lock or network request ran. Probe/report writes stayed under `C:/Temp/av-kit`. Protected files were not opened. The coordinator owns copying this report to the canonical path.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| R1-F1 | High | yes | control-defeat | **AC-148.1 accepts a completely missing native lookup.** It accepts `""` for the existing-folder positive case and requires `""` for the missing-path negative. An always-empty `short_path_name` therefore satisfies both. All remaining short-form tests replace that helper with the counting fake, so they cannot distinguish the broken producer. The prescribed test gate can pass while a Windows user's actual short-form home still appears in Console fields and download log lines. This defeats the delivery proof for `SHORT_PATH_NAME`, and consequently the production reach of `SHORT_FORM_SCRUB` and `SHORT_FORM_SPLIT`. Confidence: High. Violates: AC-148, specifically AC-148.1's proof of the native producer. mechanism: task-row-completion-predicate | `docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md:170`; fake boundary at `:158`; corresponding task row at `docs/execution/plans/2026-11-15-text-scrub-residuals/task.md:49` | Add a positive test that executes the real `short_path_name` helper and requires a known successful native result. A deterministic fake of the native API beneath that helper can provide a distinct short alias and check the size-query/fill sequence; retain the downstream fake-helper tests. Explicitly demonstrate that replacing the helper with `return ""` makes the new proof fail. Keep real lookup failure and non-Windows cases, without relying on the host home or enabled 8.3 naming. | open |

## Q1 — Goal and production paths

Accepted. Both `add_channel` branches converge on the naming expression (`services/transcript.py:155-180`); AC-147.2/.3 cover PlaylistInfo and VideoInfo, including empty-cleaned ID fallbacks. Listed titles/names already pass their domain guards. The fetch's chosen title feeds both raw Markdown and the stored item (`:636-650`), covered by AC-147.4/.5. Compile/zip consume those values; no third extract-title or caption-title producer was found in this scope.

For home scrubbing, `console_field` reaches `scrub_home`; `scrub_line` reaches both `_scrub_split_home` and `_scrub`/`scrub_home` (`health.py:126-132`, `download.py:107-144`). SHORT_FORM_SPLIT covers the independent split-aware path. SHORT_PATH_API and SHORT_PATH_NAME now have a positive oracle beneath the helper, connected onward to Console output. Every scoped goal clause has an AC and executable task row. No rejection remains.

## Q2 — MEU-147 design

Accepted D-922 through D-924. TEXT_CLEAN_SHARED moves D-360's cleaner verbatim and preserves whitespace normalization, Cc/Cs removal and Cf retention. The adapter imports the shared object, avoiding a core-to-infrastructure dependency or a second cleaner. Seven independent cleaner/guard vectors passed; unchanged MEU-122 regression suites remain required.

CHANNEL_FALLBACK_CLEAN uses the ID already computed in both branches and preserves the raw extract-title slug. RESULT_TITLE_CLEAN preserves listed-title precedence. CLEAN_AT_ENTRY is sound for these new entry values: adding refusal guards to TranscriptJob/TranscriptItem would also reject older rows during reconstruction (`database/mappers.py:188-203`), while guarding TranscriptResult would reject input that the service must repair. The plan proves the cleaned values satisfy the existing guard. Historical-row remediation and transcript-body cleaning remain explicitly outside this fix. No additional mandatory-human hit was identified.

## Q3 — MEU-148 design

Accepted D-927. SHORT_PATH_API loads GetShortPathNameW only on Windows with the correct wide-string pointer/DWORD signature and explicit loading-failure behavior. SHORT_PATH_NAME's size query includes the terminator, the fill excludes it, and `0 < written < size` rejects a failed or insufficient-buffer result. Off Windows the seam returns None. The independent reconstruction passed the success sequence and all five AC-148.9 cases; a real scratch-folder Win32 lookup returned a same-file path and the missing-path lookup returned empty.

SHORT_FORM_CACHE includes failed lookups, keys by the stripped long home, and isolates synthetic homes via fresh patched dictionaries. Its production bound remains the application's fixed home value; this change does not introduce a new variable-key source. Existing home_folder-patched callers retain their long-form behavior. SHORT_FORM_SCRUB and SHORT_FORM_SPLIT reuse D-335/D-627 boundary and case rules; the independent composition retained SYNTHE~10, another drive, a preceding word character and a nested path. No new behavior defect from the private seam was found.

## Q4 — Tests, Red and isolation

Accepted the revised proof. AC-148.8 leaves short_path_name real, substitutes only its native callable, requires a distinct alias and the query/fill call sequence, and follows its result through home_forms and console_field (`implementation-plan.md:159-181`). AC-148.9 separately exercises failure results. AC-148.1 now accurately limits its permissive existing-directory assertion to smoke coverage; it is no longer the sole direct success proof.

The always-empty mutation fails AC-148.8's helper-result and Console-result assertions. Row 4 loads the plugin with `-p mutant_empty_lookup`, records its nonzero exit, rejects any passed case, and invokes the existing Red checker with `--require test_ac_148_8` (`task.md:49-50`). H1-2 independently includes the same mutant step (`implementation-plan.md:296`). Missing/failed plugin loading cannot supply the required assertion failure. The Red checker selftest passed 36 fixtures, including 25 refusal cases. This closes R1-F1 without a new import/collection/setup dependency.

The initial Reds assert new symbols before patching/calling them. Synthetic homes and scratch/tmp_path native probes keep these tests off the real home. AC-147.5 explicitly requires SQLite, SqlAlchemyUnitOfWork, FilesystemAdapter, engine disposal and a fresh-unit-of-work read-back; it is a real storage regression. Longer-name, drive/boundary, non-Windows, failed-lookup and split-name negatives remain meaningful. Future test code and the actual pytest-plugin lifecycle still require execution verification; they were not run here.

## Q5 — Order and overlap

Accepted the unchanged MEU order and content-scoped baselines. Row 0 runs after Sessions 75/76 and snapshots shared-file bytes then, rather than requiring a clean tree or assuming those sessions are committed. S2 applies to the five product files and 03 source, which earlier sessions do not edit. S4 also checks content changes in already-dirty external paths. The future gate must implement these rules rather than inherit its peer's HEAD-movement rejection (`task.md:40-44`; `implementation-plan.md:259-274`).

Row 5 derives known-issues.yaml's expected hash from row 0, so it preserves earlier issue updates. The source issue-resolve.py holds a Windows handle denying concurrent writers, stages via issue_triage.model.save, and verifies parsed changes only under the two named issues' status, verification and resolution_path. Session 83 follows this session. MEU status and generated registers are changed through meu_status.py and issue_triage.py. No new overlap hazard was introduced by D-927.

## Q6 — Safety and gate scope

Accepted. The private seam and its tests/plugin fit the updated file inventory and plan folder; all added commands direct receipts to scratch. The setup dependency sync is explicitly declared. Product and build-plan CRLF files have row/gate byte checks; new Python files and the mutant use LF. No additional product path, schema, renderer, MCP shape or API/OpenAPI shape is introduced.

Static checks, affected tests and a fresh full Python suite remain required. The gate now adds the mutant without replacing the normal MEU-148 run or the scrub-caller regressions. Separate AC-119.10 and caller invocations also fix the prior incidental `-k` filtering ambiguity. UI/E2E/OpenAPI skips remain appropriate for this service-only change. The two UI canon tests supplement Python verification for changed status documents and run again after H2 status writes; they are sufficient for that limited UI impact.

## Checklist Results

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Manual full plan/task comparison by codex-independent-reviewer | null | Same MEUs, order, six scripts, nine MEU-148 ACs, private seam and mutant. |
| PR-2 Not started | pass | Scoped `rtk proxy git diff --name-only --` query over the five product paths and 03 source, plus manual row/folder inspection | 0 | No diff paths; rows unchecked; scripts explicitly scheduled. |
| PR-3 Task contracts | pass | Manual task-table inspection by codex-independent-reviewer | null | Owners, outputs, dependencies and validation remain explicit. |
| PR-4 Validation realism | pass | `rtk proxy python -B C:/Temp/av-kit/text-scrub-residuals/review/round2-contract-probe.py` plus manual row-4/gate trace | 0 | New success/scrub oracle rejects always-empty helper; failure scripts and actual Win32 scratch lookup pass. |
| PR-5 Source-backed choices | pass | Manual comparison by codex-independent-reviewer against 03, issue records, D-337/D-360 and HDP | null | D-927 strengthens evidence for the existing approved lookup design; no existing assertion is changed. |
| PR-6 Substantive correction readiness | pass | Manual recheck of R1-F1, revised plan/task and separate MEU handoffs by codex-independent-reviewer | null | Required corrective proof is carried through ACs, row 4 and H1-2. Process-paperwork review is excluded by the user. |
| PR-7 Scope discipline | pass | Manual comparison by codex-independent-reviewer with Session 77, both issues and the 03 residual sections | null | No scoped producer or scrub path is deferred. |
| PR-8 Reachability and negative oracle | pass | Manual production call-chain trace and round2-contract-probe.py | 0 | Native callable → real helper → home_forms → Console has an explicit success oracle; mutant fails it. |
| PR-9 Single-statement discipline | pass | Manual named-contract/AC/task comparison by codex-independent-reviewer | null | SHORT_PATH_API, SHORT_PATH_NAME and existing named contracts determine behavior; no materially competing rule. |
| Existing Red checker | pass | `rtk proxy python -B docs/execution/plans/2026-11-15-framework-small-syncs/red-check.py --selftest` with TMP/TEMP under review scratch | 0 | 36 fixtures (11 positive, 25 negative), 0 wrong. |
| Product suites / implementation verification | n/a | Not run under the read-only plan-review contract | null | No product runner, dependency install or lock operation ran. |

### Decisive evidence

```json
{"schema_version":"evidence.v1","check_id":"tsr-plan-r2-native-oracle","command":"rtk proxy python -B C:/Temp/av-kit/text-scrub-residuals/review/round2-contract-probe.py","cwd":"P:/av-kit","scope":"D-927 specification reconstruction, existing cleaner/scrub functions extracted in memory, real Win32 lookup on scratch paths","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"plan-sha256:ecc63c989fc720d4d448aba9a00d404a868b50b942581abca2f71fb9047a0cd8;task-sha256:c214552a5e26c2012eb6c782f44fdcad5274f3b7e3938b3f59fea1be3e560d24","output":"D-927 reconstruction: distinct alias and exact query/fill sequence pass. AC-148.9 reconstruction: five failure cases return empty; query-zero never fills. AC-148.8 oracle: both success and scrub assertions reject always-empty mutant (2/2). Existing pattern composition: 5 positives / 4 boundary negatives pass. Existing D-360 cleaner/guard: 7 vectors pass. Real Win32 scratch-folder lookup: samefile=True; missing scratch path returns empty. No product import, test runner, repository write, real-home lookup or network request.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"tsr-plan-r2-red-check-selftest","command":"rtk proxy python -B docs/execution/plans/2026-11-15-framework-small-syncs/red-check.py --selftest","cwd":"P:/av-kit","scope":"Reusable Red receipt checker; TMP/TEMP=C:/Temp/av-kit/text-scrub-residuals/review","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"reviewed reusable checker source in working tree","output":"red-check selftest: 36 fixture(s) (11 positive, 25 negative), 0 wrong: []","fresh":true}
```

The reconstruction tests the specified algorithm and oracle, not unwritten implementation. R1-F1 is closed because the revised plan now requires nonempty success through the real helper and a gate that rejects its always-empty replacement. Execution review must still verify the actual code, fake, plugin and receipts.

## Verdict

`approved` — R1-F1 is fixed in the plan; no new finding. The revised plan delivers the scoped goal and carries a meaningful native-success proof. Implementation/testing and historical-row or transcript-body remediation are not certified by this approval. The session ends uncommitted with a commit-message draft, as requested.

## Recheck (round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F1 | open | fixed |

### Corrections Applied

- D-927 adds the private native-callable seam below the production helper (`implementation-plan.md:112-113`, `:389-402`).
- AC-148.8 requires a successful distinct alias, the two-call sequence and its Console effect; AC-148.9 covers native failure results (`implementation-plan.md:180-181`).
- Row 4 and H1-2 require assertion failure under the always-empty mutant, rejecting a passing selected case (`task.md:50`; `implementation-plan.md:296`). The independent reconstruction confirms the strengthened oracle distinguishes that mutant.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No new findings.

### Verdict

`approved` — no unresolved blocking finding; no additional human decision required for this plan approval.
