---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-framework-small-syncs/implementation-plan.md"
verdict: "approved"
findings_count: 1
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "fs-plan-2026-11-15-framework-small-syncs"
round: 1
---

# Critical Review: 2026-11-15-framework-small-syncs

> **Review Mode**: `plan`
> **Verdict**: `approved`

## Intent Anchor

av-kit's `deep-research-prompting` skill carries upstream's prompt templates and image-strip script, adapted to this repository, and `agent-commit.ps1` refuses any commit whose author or committer address is not `219344396+matbanik@users.noreply.github.com`.

Executing the plan would deliver this objective for the two supported commit modes. One ancillary diagnostic contract needs correction; it does not allow an incorrect identity to pass or prevent the port.

## Scope

**Target:** the complete working-tree `implementation-plan.md` and `task.md` in `docs/execution/plans/2026-11-15-framework-small-syncs/`.

**Checklist applied:** PR-1 through PR-9, with the Materiality Gate and source/behavior checks relevant to this unstarted tooling plan. Formatting and closeout paperwork are excluded as requested.

Reviewed on `main`, HEAD `6813232d8769be71eb6e72505b6f39c58c11bddd`. Reviewed plan SHA-256: `1ee31c72697cd9d401792031dd6f1c9f66dcd58449ee8129b118b4640d6a064a`; task SHA-256: `0fc4fb6c94e19ff86a22a30e5899ea757de64d8838337b752699b77cdf83f767`.

Sources included the current skill/workflow and commit script/skill, upstream `0a8d5bc` blobs, upstream identity functions, the global strip tests, Zorivest's plan and implementation review, adoption-test fixture/oracle, copied helper sources, `.gitattributes`, guardrails, profile and CI workflows. The Session 85 plan was absent when inspected; its potential overlap is evaluated through the explicit row-0/S2 contract. Other sessions' files were not modified.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| R1-F1 | Medium | no | behavior | `CHECKER` delegates usage errors to argparse while promising that no output contains an address. Default argparse echoes rejected arguments: `--unknown fixture@example.invalid` exits 2 and includes that address in stderr. The prescribed ordinary unknown-flag test can pass without proving the stronger guarantee. This affects an operator's receipt after a malformed invocation; it does not bypass identity refusal. Confidence: High. | `docs/execution/plans/2026-11-15-framework-small-syncs/implementation-plan.md:221`; `:222`; `:285` | Specify a sanitized parser error path that emits only fixed usage/reason text. Extend AC-15 with an address-bearing rejected argument and assert exit 2, no `@`, and no traceback. | open |

## Q1 — Goal and coverage

Accepted. Rows 1–4 and AC-1–AC-10 cover the script, six templates, adaptation and upstream byte identity. Rows 5–8 and AC-11–AC-20 cover the resolved author and committer, both production modes, placement, preservation and live positive/negative checks. `UPSTREAM`, `BASE`, `ADAPTATIONS`, `EXPECTED_EMAIL` and the four production calls give these tests concrete inputs and callers.

The accepted D-883 boundary explicitly permits a local commit to exist if a late identity change is discovered, then refuses success/push and leaves remediation to Mat. This review applies that stated boundary. No High/Critical failure of the registered goal was demonstrated.

## Q2 — Identity semantics and errors

Accepted for the script's actual argv. Legacy mode supplies neither `--author` nor a separate `-c user.email=...`; exact-scope mode's pre-check temporarily supplies the same email variables that its commit block later supplies. Repository config, `author.email`, `committer.email`, environment overrides and matching `includeIf` configuration are visible to `git var`. Seven isolated scratch cases confirmed these resolutions. `%ae`/`%ce` avoid mailmap substitution. The post-check covers a resulting HEAD whose identity differs from the pre-check, including ordinary hook-induced drift.

Missing `uv` and checker failure are expressly refusals; implementation must preserve that status rather than consume it as successful helper output. Arbitrary executable hooks that rewrite history or tamper with Git's object view are not certified by this plan-time inspection. The claim that `git var` predicts *every possible* `git commit` invocation is too broad, but the supported script calls are specified. The unconditional no-address guarantee is not accepted: see R1-F1. Checker code and wrapper execution remain execution-time evidence, not results claimed here.

## Q3 — Wiring and preservation

Accepted. Legacy early check precedes `git add -A`; its late check precedes the push block. Exact-scope early check precedes signing configuration and temporary-index staging; the late check follows `verify-commit`, and that mode already requires `-NoPush`. Four parents above `.agent/skills/git-workflow/scripts` is the repository root. Passing both `--project <root>` and an absolute checker path makes the production script usable from the AC-17/AC-18 temp repo while `--repo` selects that repo for Git.

All four existing files were independently measured as entirely CRLF (301/169/283/379 line terminators). AC-19's ordered-line preservation against `BASE`, byte-level CRLF checks and adversarial placement fixture are adequate specifications for `script-check.py`. AC-17 checks actual HEAD/untracked state; AC-18 asserts the identity reason before signing rather than accepting any nonzero exit. The designated Red cases can fail by assertion without depending on a missing import.

## Q4 — Port and adaptations

Accepted. All nine upstream blob prefixes and byte counts match the plan. Reconstructing A1–A14 against the saved upstream skill found no `FORBIDDEN` match. The local output/snapshot paths, local timestamp procedure, SIGN 3 citation and the workflow's topic decision row are preserved. The optional content-seo overlay remains inert. The d2 model string is portal-template content governed by recon, not an agent routing instruction; its narrowly identified exception is justified. The migrated-tree fixture copies the four existing changed governance files, so their existing oracle remains relevant.

Six direct probes of upstream `STRIP` passed: collision avoidance, idempotence, malformed/empty/unhandled input with no writes, and titled CRLF conversion. The port checker is specified sufficiently to catch extra/missing adaptations, bad upstream bytes and unresolved links. Minor wording note: upstream's orchestration still says snapshots are shared across “all topics and projects”; A6 only removes the earlier equivalent statement. Remove “and projects” in the adaptation data for literal repo-local accuracy. This wording has no effect on the fully specified av-kit paths and does not block.

## Q5 — Earlier sessions and dirty-tree baseline

Accepted. `BASE` is explicitly the execution-start content, not HEAD. `GIT_SKILL` is preserved add-only against that content. The replaced workflow carries forward the row actually found at execution start; a change outside that row triggers S2 instead of being overwritten. A changed skill also triggers S2. This is conservative and protects changes even when Session 85's final plan is not yet available.

The baseline records unrelated dirty-path content hashes; the scope check permits those paths only while their content state remains unchanged. This detects changes to an already dirty file, unlike porcelain-only comparison. New files must start absent, all allowed outputs are inventoried, and `identity.py` includes other sessions' uncommitted bytes. `baseline.ps1`, the adapted `identity.py`, `port-check.py`, `script-check.py` and `session-gate.ps1` each have enough behavior specified to implement and test. Their scheduled absence is not a finding.

## Q6 — Tests, isolation and CI

Accepted for the local gate. The global file contains 18 test functions; AC-1–AC-6 cover their substantive behaviors and add CRLF preservation. Fresh Git-test environments plus a temporary `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM=1` and explicitly controlled identity variables support hermetic cases. AC-17's positive case intentionally reads the production constant; it does not infer a host address. The AC-18 skip is narrow, and `pytest -rs` plus the gate's skip refusal prevents missing `rtk` from masquerading as a locally verified exact-scope guard.

CI clarification: `.github/workflows/ci.yml:62` explicitly ignores **all** `tests/tooling`, so ordinary CI will not collect either new file. D-881's rationale at plan line 552 must not be read as a CI-coverage guarantee. The plan's fresh local gate explicitly runs both files, so this does not remove its delivery proof. Adding CI coverage would be a separate scope choice; no such change is required by the registered goal.

## Q7 — Safety and scope

Accepted. The enumerated writes are the scoped product/tooling files, this plan's scripts/data, listed closeout artifacts, and temp test/receipt files. Upstream, Zorivest and the machine-global skill/tests are read-only sources. The live identity check only reads Git state. The session ends uncommitted with a message draft; no row authorizes a host commit, push, configuration repair, or a write to those external sources. Scratch test repositories are the deliberate fixture exception.

The skips for UI/MCP/product type checking/OpenAPI/build match the changed surfaces. The gate still lints the new tool and copied strip script, runs the affected tests and adoption oracle, and requires a fresh full Python result against a recorded baseline. An external failure must retain its actual failure evidence; implementation must not turn an unexpected test failure or skip into a pass.

## Checklist Results

All results below are plan-review observations, not execution certificates. Manual observer: `codex-independent-reviewer`; manual exit codes are null.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Read both complete target files and compare rows 0–8 to work packages and ACs | null | Same two deliverables, baseline, Red/Green order and gates |
| PR-2 Not started | pass | `rtk proxy python -B -c <existence/hash inspection>` | 0 | Both new test files, CHECKER, STRIP and implementation handoff absent; task rows unchecked |
| PR-3 Task contracts | pass | Inspect every task row for owner, deliverable, validation, dependency and status | null | Rows include concrete outputs and commands; scheduled helpers are specified |
| PR-4 Validation realism | pass | Trace each goal clause through ACs, task commands and the actual commit script | null | Real-byte equality and temp-repo script checks; diagnostic exception R1-F1 remains nonblocking |
| PR-5 Source backing | pass | Compare upstream blobs, global tests, Zorivest review and local canon to the AC table | null | Nine blob identities match; 18 global test functions; D-876/D-883/D-884 authority accepted as directed |
| PR-6 Corrections readiness | pass | Inspect scoped plan/task and review handoff paths | null | Round 1; no prior correction census required |
| PR-7 Scope discipline | pass | Compare excluded work to grouping scope and given decisions | null | No required deliverable displaced into a future MEU |
| PR-8 Controls and negative oracles | pass | Trace four planned production calls and test negative observables against current script | null | Calls precede staging/push; wrong identity asserts HEAD unchanged; no demonstrated material false-pass |
| PR-9 Single-statement discipline | pass | Inspect named contracts, AC references, adaptation data and baseline definitions | null | Governing values are explicit; no materially conflicting behavior identified |
| Independent upstream/diagnostic probes | pass | `rtk proxy python -B C:/Temp/av-kit/fs-review-probes.py` | 0 | Nine blob IDs/counts match; CRLF counts match; diagnostic leak reproduced |
| Independent Git resolution probes | pass | `rtk proxy python -B C:/Temp/av-kit/fs/review/identity-probe.py` | 0 | Seven isolated cases passed, including `includeIf` |
| Independent strip probes | pass | `rtk proxy python -B C:/Temp/av-kit/fs/review/strip-probe.py` | 0 | Six direct cases passed against upstream blob `4ef304e` |
| Execution suites / production wrapper | n/a | Not run: pytest, uv sync/lock, npm, agent-commit.ps1 | null | Read-only plan review; no execution result asserted |

```json
{"schema_version":"evidence.v1","check_id":"fs-review-source-and-diagnostic","command":"rtk proxy python -B C:/Temp/av-kit/fs-review-probes.py","cwd":"P:/av-kit","scope":"upstream blobs, specified adaptations, source test count, CRLF and argparse behavior","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-sha256:1ee31c72697cd9d401792031dd6f1c9f66dcd58449ee8129b118b4640d6a064a;task-sha256:0fc4fb6c94e19ff86a22a30e5899ea757de64d8838337b752699b77cdf83f767","output":"Matched 234d25a/26816, 4ef304e/7898, ef187b4/1805, e4c6c0d/1843, 24fff82/1825, 30d2dde/7676, cf92ba1/2407, eef9dbe/1193, d9bf24f/783. CRLF totals 301/169/283/379 equal LF totals. 18 upstream test functions. argparse rejected --unknown fixture@example.invalid with exit 2 and echoed the fixture address. This is a successful reproducer, not a passing no-address contract.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"fs-review-git-identities","command":"rtk proxy python -B C:/Temp/av-kit/fs/review/identity-probe.py","cwd":"P:/av-kit","scope":"scratch Git identity resolution with synthetic addresses and isolated global/system configuration","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Git executable on reviewer host; isolated scratch repo; plan identity-mode design","output":"7 cases passed: good config, author environment override, committer environment override, author.email, committer.email, EMAIL ignored with user.email, matching includeIf override. No host config read or modified.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"fs-review-strip","command":"rtk proxy python -B C:/Temp/av-kit/fs/review/strip-probe.py","cwd":"P:/av-kit","scope":"direct strip_file calls against upstream blob 4ef304e with scratch files","phase":"targeted","exit_code":0,"result":"pass","tested_state":"upstream:0a8d5bc:strip_embedded_images.py:4ef304e","output":"6 cases passed: reference/inline filename collision, idempotence, malformed payload beside valid image, empty payload beside valid image, unhandled embedded URI beside valid image, and CRLF reference-title preservation. All failure cases left report bytes and image-directory state unchanged.","fresh":true}
```

## Verdict

`approved` — the plan is executable and would deliver the registered goal. No evidence-backed High/Critical blocker was found. R1-F1 is a nonblocking diagnostic behavior defect; sanitize parser errors during implementation. Correct the minor cross-project wording and CI rationale without claiming CI coverage that the current workflow excludes.

The report is `C:/Temp/av-kit/fs-plan-review-round-1.md`; the coordinator owns copying it to the canonical review location. This reviewer made no repository edits, ran no prohibited suites or wrapper, changed no host Git configuration, and made no network requests. Implementation approval is not commit authorization.
