---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-hdp-expert-pass/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ep-plan-2026-11-15-hdp-expert-pass"
round: 1
---

# Critical Review: 2026-11-15-hdp-expert-pass

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Scope

**Intent anchor:** Before Mat sees a set of Decision Briefs, one fresh-context advisory reviewer (`avkit_peer_reviewer`, the Claude Code agent `av-kit-peer-reviewer`) tests each recommendation, and a ruling Mat hands back to the agent for one brief set is recorded as the agent's ruling.

**Target:** the working-tree implementation-plan.md, task.md and ep-check.py in `docs/execution/plans/2026-11-15-hdp-expert-pass/` (`PLAN`). Reviewed against Session 85's plan and checker, Session 84's record-once contract and current validator reader, upstream `a73d6df`, Zorivest's HD3 plan/reflection/handoff, routing/delegation, dispatch callers, local agents and both registries. Applied PR-1 through PR-9, Materiality Gate and relevant DR checks.

Claude/Anthropic authored the plan; this Codex reviewer did not. D-860 through D-862 and the grouping rulings were accepted as given. D-863 through D-874 were assessed for sound execution. No repository files were edited. All reviewer writes are under `C:/Temp/av-kit`; no network, pytest, dependency synchronization, lock update, npm command, live-overlay compilation or model invocation was performed.

HEAD observed: `6813232d8769be71eb6e72505b6f39c58c11bddd`. Review-file identity: `review-state:08b008a689d678af5552e4dc8cb9204e4439cd13c5eff223eeccfe2d41e46b8f` (SHA-256 over each target path, NUL, and its bytes, in implementation-plan/task/ep-check order). This identifies the reviewed plan files; it is not an execution D6 identity.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1. Goal and observable behavior

Accepted. Row 2 and AC-1 through AC-4 install the pre-presentation expert pass and hand-over rule; row 3 and AC-6/AC-7 supply its packet and indexes; row 4 and AC-9 through AC-11 supply the resolvable class and agent; row 5 and AC-8 connect the class name to the agent and routing table. The `HDP` entrypoint explicitly requires one fresh-context pass per set, three questions per recommendation, author verification, and the set result line (`ep-check.py:66-92`). It preserves the upstream fallback and skip rules.

The hand-over text preserves `resolution: autonomous`, the agent's own basis tag, the human's quoted hand-over and the mandatory list, with the one-set/no-M-or-M-3/M-5/M-6/M-8 limit (`ep-check.py:103-110`). It does not misattribute the resulting choice to Mat. This is a prose workflow contract, not a new automated enforcement gate. D-872 explicitly excludes live invocation during installation; this review establishes configuration and planned behavior, not an observed Claude run.

## Q2. Upstream port and record-once compatibility

Accepted. Fresh `git show` blobs from `a73d6df` passed `EP upstream`: §5a, the M-3 clause, the hand-over paragraph and the skill match after reversing the documented av-kit substitutions. The routing-table replacement is correct: av-kit has a CLI Dispatch Decision Table. The local agent removes the framework-instantiation/global-sync instructions, uses local provenance, and adds the text-return case needed by the packet (`ep-check.py:212-259`). Zorivest HD3-D2 through HD3-D5 and its executed D-13 record support the placement, no size floor, retained generic adversarial wording, and autonomous record.

Session 84's boundary inventory states that stage-log `resolution`, `class`, source tags and related fields are not newly constrained; its new checks require a nonblank question/choice/reasoning and reject pending choices (`2026-11-15-closeout-record-once/implementation-plan.md:240`). The current reader likewise has no class/source-tag/mandatory eligibility restriction (`tools/validate_closeout_artifacts.py:1330`). Session 85 makes `mandatory` optional. A completed handed-over entry fits these checks; no validator change is needed. The plan does not claim that the closeout validator enforces the hand-over's substantive eligibility rule.

## Q3. Registry class and local agent

Accepted. An independent temporary overlay was compiled and checked with the actual shared resolver. The compiled result differed from the live baseline only by `classes.avkit_peer_reviewer`. Its binding and shared contract fields equal `peer_reviewer`; the additional forbidden-model constraint is intentional. Resolution returned `opus`, `claude-opus-5-5`, `high`, `anthropic`. All three unsupported harnesses refused with `unresolvable_on_harness`. The independent reviewer still resolved to OpenAI with vendor diversity.

The class carries `not_a_reviewer: true`, has no Codex binding, and is never inserted into the independent-reviewer chain. Its agent instructions prohibit verdicts and approvals. The new header follows the existing local agents' AUTOGEN/local-class layout and uses resolver-derived frontmatter; `EP newfiles` checks exact provenance at execution time. D-866's existing stale markers remain the given pre-existing observation. The tool allowlist includes Bash, so the no-repository-writes rule is also an instruction restriction; this plan does not add an OS-level sandbox.

## Q4. Ordering and Session 85 anchors

Accepted. Session 85 specifies §4a with the relevant M rows, the plain M-3 note, ordered §5/§6 followed by §7, and the overturn paragraph. It inserts the exact Open decisions bullet (`hdp-v2-protocol/implementation-plan.md:98-140,187-193`). Its commands.md change is to the HDP row, and its cli-dispatch skill edit removes a later stale phrase; both leave Session 86's insertion/replacement anchors intact (`:228-233`). The cli-dispatch workflow is unchanged there.

Session 85 uses its own plan-local oracle and adds no durable test pinning the absence of §5a or the hand-over paragraph (`:246-254,326-332`). Its absence predicates run before this session, as S5 anticipates. On today's pre-85 tree, `EP anchors` exits 1 with exactly two affected-file gaps: HDP's missing §4a/M rows and delegation's missing Open decisions bullet. That is the expected dependency state, not a failed readiness claim. A temporary reconstruction of the specified upstream HDP anchors accepted the `EP` edit; the other real-file anchors also accepted their planned edits. S1 remains a real stop if Session 85 lands differently.

## Q5. Tests, Red and byte checks

Accepted as a prospective test plan. The ten required Red tests all have missing behavior before execution. Existence assertions precede reads; AC-9 asserts resolver success rather than allowing an exception to escape; AC-10 asserts the six-class result. These can fail by assertion without importing a nonexistent production module. The existing red-check helper distinguishes numeric test identifiers and rejects setup/collection errors. New tests are not yet written, so actual Red/Green remains execution evidence to collect.

`EP selftest` ran 45 checks with zero failures. Independently, `delta_problems` accepted planned bytes and rejected an unrelated edit in a CRLF file and a CRLF-to-LF change. `eol_problems` also rejected that changed ending. Delta uses exact bytes (`ep-check.py:492-501`); it catches moved or exchanged endings that aggregate ending counts alone would not detect. The compiled comparison is intentionally structural JSON plus LF, preserving every old class and metadata field. The `Baseline copy`, `Planned bytes` and `Upstream` contracts therefore have working positive and negative oracles.

## Q6. Safety, scope and gate skips

Accepted. Planned source writes are enumerated, closeout/project writes are declared, and `EP scope` checks HEAD plus hashes of unrelated baseline-dirty paths. The resolver write path was verified on a temporary copy and emits the local compiled sibling; no global sync is scheduled. No row commits, writes the shared registry, or modifies either upstream repository. Dependency sync and suite execution may have ordinary ignored environment/cache effects; those are not source edits certified by `EP scope`.

The governance gate appropriately skips product type/UI/MCP/OpenAPI/build checks because their inputs are unchanged, and retains the Python suite, adoption checks through that suite, registry checks, render check and closeout selftest. S4 protects other workstreams; S5 prevents silently editing an existing test to accommodate a collision. No product-gate pass or completed implementation is claimed by this plan review.

## Checklist Results

| Check | Result | Procedure or command | Exit | Evidence |
|---|---|---|---|---|
| PR-1, PR-3: alignment and task contracts | pass | Manual comparison by codex-independent-reviewer of all implementation/task rows and AC-1 through AC-14 | null | Rows 0-6 implement baseline, Red, HDP, packet/indexes, registry/agent, routing and Green in dependency order. H1/H2 follow. |
| PR-2: unstarted | pass | File existence/HEAD probe recorded in ep-paths-r1.txt and manual task review | 0 | All execution rows unchecked; new skill, agent and test absent; HEAD 6813232. |
| PR-4, PR-8: checker reality | pass | `python docs/execution/plans/2026-11-15-hdp-expert-pass/ep-check.py selftest` | 0 | 45 checks; `selftest: 0 failure(s)`. |
| PR-4, DR-4: independent probes | pass | `python C:/Temp/av-kit/ep-review-probe-r1.py` | 0 | Fresh upstream comparison, specified Session 85 anchors, CRLF negative probes, temporary resolver compilation and four-harness resolution; `PROBE PASS`. |
| PR-5: source-backed port | pass | `python docs/execution/plans/2026-11-15-hdp-expert-pass/ep-check.py upstream --hdp C:/Temp/av-kit/ep/review/upstream-hdp.md --skill C:/Temp/av-kit/ep/review/upstream-skill.md` | 0 | `upstream: the constants match a73d6df`. |
| PR-6, PR-7: readiness/scope | pass | Manual inventory and source review by codex-independent-reviewer; ep-paths-r1.txt | null | Required existing executables exist; new helpers have creation rows; no missing required deliverable or disguised deferral. |
| PR-9: single statements | pass | Manual comparison by codex-independent-reviewer of named contracts, ACs, task references and EP constants | null | No contradictory live behavioral definitions found. |
| Report structure and target binding | pass | `python tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/ep-plan-review-round-1.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-15-hdp-expert-pass/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/ep/review/report-state.json` | 0 | `OK: review_mode=plan; round 1 of 3; verdict=approved; open findings=0`. |
| Runtime invocation and execution suites | n/a | Excluded from this read-only plan review | null | Installation and Red/Green execution remain future work. |

```json
{"schema_version":"evidence.v1","check_id":"ep-review-selftest","command":"python docs/execution/plans/2026-11-15-hdp-expert-pass/ep-check.py selftest","cwd":"P:/av-kit","scope":"plan-local oracle selftest","phase":"targeted","exit_code":0,"result":"pass","tested_state":"review-state:08b008a689d678af5552e4dc8cb9204e4439cd13c5eff223eeccfe2d41e46b8f","output":"45 checks; selftest: 0 failure(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"ep-review-independent-probes","command":"python C:/Temp/av-kit/ep-review-probe-r1.py","cwd":"P:/av-kit","scope":"upstream blobs, planned edits and temporary project overlay","phase":"targeted","exit_code":0,"result":"pass","tested_state":"review-state:08b008a689d678af5552e4dc8cb9204e4439cd13c5eff223eeccfe2d41e46b8f","output":"Fresh a73d6df HDP/skill match; specified Session 85 anchors accepted; unrelated CRLF-file edit and changed ending refused; temporary compile/check exit 0; only advisory class added; supported harness resolves to opus/high/anthropic; cursor-task, codex-cli and claude-p each exit 1 with unresolvable_on_harness; independent reviewer remains OpenAI and vendor-distinct; PROBE PASS","fresh":true}
```

Commands above ran through `rtk proxy` with `PYTHONDONTWRITEBYTECODE=1`, all streams redirected under `C:/Temp/av-kit`, and child exits preserved. Initial upstream access needed command-local `git -c safe.directory=P:/agentic-framework`; no Git configuration was edited. The diagnostic about the inaccessible user ignore file and the resulting local-settings untracked entry were treated as the supplied sandbox observation; that file was not opened.

## Verdict

`approved` — executing this plan after Session 85 closes would deliver the registered intent. No material delivery defect or demonstrated false-passing control was found. The coordinator can save this report to the canonical rolling review path and proceed under Mat's existing execution authorization. The session remains uncommitted and ends with a commit-message draft.
