---
project: "2026-11-15-tooling-test-hermeticity"
date: "2026-11-15"
source: "grouping .agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md §3 Session 76; .agent/context/known-issues.yaml TOOLING-SHARED-REGISTRY-COUPLING (:33), TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE (:859), CLI-DISPATCH-PLACEHOLDER-FIXTURE (:5244)"
grouping_source: ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
meus: []
status: "draft"
template_version: "2.3"
---

# Implementation Plan: Hermetic fixtures for the adoption and dispatch tests

> **Project**: `2026-11-15-tooling-test-hermeticity`
> **Build Plan Section(s)**: none (tooling tests and their fixtures; no MEU)
> **Status:** said to execute (USER_EXPLICIT 2026-11-15 'proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions.'). `plan_to_exec_gate: human`; the plan review was approved at round 1 (.agent/context/handoffs/2026-11-15-tooling-test-hermeticity-plan-critical-review.md).

---

## Goal

**Goal anchor:** each tooling test in this scope reads only its own fixture, except one named test that is kept live on purpose. The registry tests resolve against a tracked synthetic registry in a temp registry home. The governance tests check a migrated tree whose rule-map pins and backlinks follow the bytes that tree holds, and one test still checks the tracked rule-map pins against the live instruction files (D-132). The dispatch placeholder arm builds its token at run time. A change to the machine registry, the live governance files or the instantiated project name then no longer reds them, and every assertion they make is unchanged.

This is Session 76 of the 2026-11-15 post-rc.3 grouping (§3, `:143-152`). It has no MEU. It resolves two issues and mitigates the third, in the grouping's order.

**1. `TOOLING-SHARED-REGISTRY-COUPLING`** (P2, `known-issues.yaml:33`).
- Five test functions in `tests/tooling/test_framework_adoption.py`, 16 cases in all, run the machine resolver against `--project ROOT` with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`. The resolver reads `AGENT_MODEL_REGISTRY` first and otherwise finds the registry next to itself (`resolve_model.py:365-368`, `:396-403`), so the machine registry is live:
  - `test_registry_contract_preserves_bindings` ×7;
  - `test_registry_contract_vendor_independence` ×2;
  - `test_registry_contract_unsupported_harness_refused`;
  - `test_registry_contract_bad_configuration_refused` ×3;
  - `test_review_pipeline_wrapper_refuses_before_provider` ×3, through `tools/Invoke-CodexDispatch.ps1`.
- A registry bump on the machine, or an ambient `AGENT_MODEL_REGISTRY`, reds them for a reason the change under test never touched. It happened three times (the issue's decision log, D-70).
- Session 86 (`6aaf9b0`) just rebound the overlay and `routing-census.md`. The fix must leave the file passing on that tree.
- **Residual, by design:** the issue's stated symptom is that a machine registry bump fails py-tests until the overlay is revalidated (`:40`). After this plan, that still happens through `tests/tooling/test_hdp_expert_pass.py::test_ac_10_compiled_registry_is_current_and_adds_only_the_peer_reviewer`, which compares the compiled stamp with the live registry's hash. The wrapper refuses the same stale stamp at every real dispatch, so that red is a true signal. `::test_ac_9_peer_reviewer_class_resolves_only_on_claude_code_agents` also resolves live, but it reds only when a bump changes the peer-reviewer route. Both are Session 86's tests and stay. So row 8 marks this issue `mitigated`, not `resolved` (D-912).

**2. `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE`** (P3, `:859`).
- `migrated_tree` (`:370-392`) copies the live `AGENTS.md` and `GUARDRAILS.md`. The verifier checks them against records frozen at the 2026-09-26 adoption:
  - the `postimage_sha256` pins in `rule-preservation.md`;
  - the manifest's file list.
- Every governance edit reds four tests until someone rebinds the tracked pin by hand.
- Mat ruled on this: D-132, USER_EXPLICIT 2026-10-27, "Update pin, commit+push (Recommended)". The reason recorded was that carrying the four failures "would hide later rule-map drift" (`docs/execution/reflections/2026-10-26-tts-sideload-load-reflection.md:116`). This plan keeps that signal in one test, `test_ac_14`, and removes it from the other cases (D-915).
- Today the pins match the live bytes (plan-time probe), so the tests pass. The next edit will red them again.

**3. `CLI-DISPATCH-PLACEHOLDER-FIXTURE`** (P4, `:5244`).
- Arm 2 of `Test-CliDispatch.ps1`'s receipts-path block (`:559-571`) needs a path that holds the template token `{{PROJECT_NAME}}`.
- Instantiation replaced that token with `av-kit` in av-kit's copy, so the guard sees a real path, creates it and passes it. Every run reports 31 total and 2 FAIL.
- Every gate that runs the dispatch tests must allow exactly that pair (D-739).

`CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is not here: it moved to Session 84 of the HDP grouping (D-822) and is resolved.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). The payload is one CRLF test file, one PowerShell test arm and a small JSON fixture, all read and edited verbatim with byte checks; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host.
  - Validation goes through `rtk proxy`.
  - Receipts go under `C:/Temp/av-kit/tth/` and are named `tth-*`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
  - No row sets `AGENT_MODEL_REGISTRY`, except the hostile runs named in §Verification Plan. Those set it in a child process only.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` does not apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `tth-plan-2026-11-15-tooling-test-hermeticity` and `tth-execution-2026-11-15-tooling-test-hermeticity`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
- **Queue:** Session 87 (`framework-small-syncs`) runs and is committed first, then Sessions 75 to 83 run in number order on `main`. Session 75 may still be uncommitted when this session starts, so every baseline is path-scoped and bound to content (D-918).
- **Execution gate:** `plan_to_exec_gate: human`. Mat's message ("proceed with planning and execution …") is the execution approval once the plan review approves.
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| Tooling test hermeticity (no MEU) | `.agent/context/handoffs/2026-11-15-tooling-test-hermeticity-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-15-tooling-test-hermeticity-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-15-tooling-test-hermeticity-implementation-critical-review.md`

There is one non-MEU handoff, as in `2026-11-05-closeout-register-grammar` (Session 49b, the size reference the grouping names) and `2026-11-15-framework-small-syncs`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-api.json`, `red-require.txt`, `C:/Temp/av-kit/tth/base/`, `C:/Temp/av-kit/tth/red-home/`, the plan-local checkers |
| WP-2 | Registry fixture: Red, then Green (rows 1 and 2) | WP-1 | shared | `FIXTURE`, `make_fixture.py`, `TEST_FILE` |
| WP-3 | Governance fixture: Red, then Green (rows 3 and 4) | WP-2 | shared | `TEST_FILE` |
| WP-4 | Dispatch arm: Red, then Green (rows 5 and 6) | WP-1 | shared | `DISPATCH_TEST` |
| WP-5 | Live probe and registers (rows 7 and 8) | WP-3, WP-4 | shared | `known-issues.yaml`, `known-issues.md` |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | Handoff, review, reflection |

## User Review Required

> [!IMPORTANT]
> **The tests stop reading your machine registry.** They resolve against `tests/tooling/fixtures/registry-home/model-registry.json`, a small synthetic registry with these limits:
> - It holds only the eight model ids that the project overlay already names.
> - Each id carries only the fields the resolver reads (vendor, harness ids, efforts, capabilities, auth mode and price band).
> - It holds no prices, sources, notes, URLs or paths.
>
> At run time, the tests copy the resolver's code (`resolve_model.py`, `ModelRegistry.psm1` and the schema) from `P:/.agent` into a temp folder. They never read `P:/.agent/model-registry.json` (D-911). The fixture's `coordinator` binding is synthetic: it names the overlay's model, not the live one.
>
> **One new upkeep step:** when you rebind a model in the project overlay, the fixture needs the same change. Run `uv run python tests/tooling/fixtures/registry-home/make_fixture.py`, which sits next to the fixture. The tests' expected-model lists change in that edit anyway.
>
> **The governance fixture follows its own bytes, except in one test.** The migrated tree rebinds its copy of the rule-map pins to the files it copied, and it copies any instruction-file link target that the 2026-09-26 manifest predates. One new test, `test_ac_14`, still compares the tracked `rule-preservation.md` pins with the live `AGENTS.md` and `GUARDRAILS.md`, as your D-132 ruling wants. After a governance edit you get one red instead of four, its message prints the exact rebind command, and you still rebind by hand (D-915). The pin oracle itself stays tested (AC-8).
>
> **The dispatch arm builds its token at run time.** This is av-kit's own change to a file copied from upstream. Upstream is not edited, and upstream has the same latent defect, which the handoff names for you (D-913).
>
> **One thing for you to do by hand, if you want it:** an empty folder, `%TEMP%\av-kit\receipts\dispatch-tests`, was left by the old arm on 2026-11-14. The session does not delete it (D-914). The handoff gives the one-line command.
>
> **What stays live on purpose:**
> - `test_hdp_expert_pass.py` keeps its two live checks: `test_ac_9_…` resolves the peer-reviewer route, and `test_ac_10_…` checks the compiled stamp against the machine registry (Session 86's tests, D-912). A machine registry bump therefore still reds `test_ac_10_…` until the overlay is revalidated. That is why `TOOLING-SHARED-REGISTRY-COUPLING` is marked `mitigated`, not `resolved`.
> - This session's gate runs `live-probe.py` once against the real machine registry: all seven project bindings and the reviewer route. It is a plan-local check, not one that stays. Between sessions, a registry edit that breaks a coordinator, builder, verifier or router binding is caught only when something resolves that class live; the resolver then refuses it (D-912).
>
> **`TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE`** is marked `resolved`. Its resolution says the one remaining red, `test_ac_14`, is kept by design under D-132.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `TEST_FILE` | `tests/tooling/test_framework_adoption.py`. CRLF on all 1072 lines, no BOM, 40489 bytes at plan time. It stays CRLF. |
| `DISPATCH_TEST` | `.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1`. UTF-8 BOM, CRLF on all 1133 lines, 62454 bytes at plan time. Both stay. |
| `FIXTURE` | `tests/tooling/fixtures/registry-home/model-registry.json`. A new file, LF. |
| `MACHINE_TOOLS` | `Path("P:/.agent")`, the one constant in `TEST_FILE` that names the machine home. Only `TOOL_FILES` are copied from it. |
| `TOOL_FILES` | `tools/resolve_model.py`, `tools/ModelRegistry.psm1`, `schema/model-registry.v1.schema.json` (relative to `MACHINE_TOOLS`) |
| `OVERLAY` | `.agent/model-registry.local.yaml`, the project overlay. Not edited. |
| `WRAPPER` | `tools/Invoke-CodexDispatch.ps1`. Not edited. Its line endings are mixed (1462 CRLF, 1 LF), so it is only ever copied byte for byte. |
| `NEEDLE` | `$dispatchProjectRoot = 'P:/av-kit'`, which occurs exactly once in `WRAPPER` (plan-time count) |
| `VERIFIER` | `docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py`. Not edited. |
| `RULE_MAP` | `docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md`. CRLF, 105740 bytes. Not edited: only the migrated tree's copy is rebound. Each of its two `postimage_sha256` values occurs once in the file (plan-time count). |
| `BASE(path)` | The bytes of an existing file, copied by row 0 to `C:/Temp/av-kit/tth/base/`. These are the bytes the earlier sessions left, not `HEAD` (D-918). |
| `RED_HOME` | `C:/Temp/av-kit/tth/red-home/`, built by row 0: `TOOL_FILES` copied, plus the live registry with the `cursor-grok-4.6` catalog entry removed |
| `HOSTILE` | The environment `AGENT_MODEL_REGISTRY=C:/Temp/av-kit/tth/red-home/model-registry.json`, set in a child process only |
| `RED_IDS` | The pytest ids in `red-require.txt`, written by row 0 (§Verification Plan 2) |

### The registry fixture (`FIXTURE`, D-911)

`FIXTURE` is the output of `json.dumps(data, indent=2, sort_keys=True) + "\n"`, written with LF.

- **Top-level keys:** exactly `schema_version` (1), `updated` (`"2026-11-15"`), `bump_gate` (`"human"`), `catalog` and `classes`.
- **`catalog`:**
  - It holds exactly the slugs that `OVERLAY` binds or forbids: `cursor-grok-4.6`, `claude-opus-5`, `claude-sonnet-5-5`, `composer-2.5-fast`, `gpt-6.1-sol`, `claude-haiku-5-5`, `claude-opus-5-5` and `claude-fable-5-2`.
  - Each entry carries only `vendor`, `harness_ids`, `price_band`, `capabilities`, `efforts` and `auth`. The values are copied from the live registry at row 2.
  - Each bound slug's `capabilities` are cut to the tokens that `OVERLAY`'s contracts for that slug require. `cursor-grok-4.6` also carries the global `coordinator` contract's tokens. The unbound `claude-fable-5-2` carries `["agentic_exec"]`.
- **`classes`:** only `coordinator`. Its contract is copied from the live registry. Its one binding is synthetic: `cursor-task` → `cursor-grok-4.6` at `xhigh`, the slug the overlay's `avkit_coordinator` binds. The live global binding is `cursor-grok-4.7`, which the fixture does not carry. The class exists so that the overlay's `global-redefinition` fault has a global class to collide with.
- **Generator:** `tests/tooling/fixtures/registry-home/make_fixture.py`, tracked next to the fixture (D-911).
  - It uses the standard library only. It has no `test_` prefix, so pytest does not collect it, and it must pass `ruff check`.
  - It reads `OVERLAY` and a registry (`--registry`, default `P:/.agent/model-registry.json`) and writes `FIXTURE`, so the result is deterministic.
  - **Upkeep coupling:** a change to an overlay binding or contract needs `make_fixture.py` re-run and the fixture committed with it. That edit changes the `preserves_bindings` expected list anyway. A stale fixture fails loudly: the strict validate or the resolve in `build_registry_home` refuses it.
  - `FIXTURE` is tracked data and nothing regenerates it at test time.
- **Plan-time proof:** `C:/Temp/av-kit/tth/probe-mincap.txt` shows that this shape compiles `OVERLAY` and that every case of the five test functions (16 cases) passes against it:
  - a 3804-byte file;
  - all eight bindings;
  - vendor `openai` refused and `anthropic` resolving to `gpt-6.1-sol`;
  - the unsupported harness refused;
  - all three faults refused.

- **Strict schema proof:** `C:/Temp/av-kit/tth/probe-strict.txt` shows that `resolve_model.py validate --registry <copy> --strict` passes on the cut-down shape (`strict=yes compiled=unchecked`, exit 0, copy unchanged). `probe-strict-neg.txt` (a catalog entry without `vendor`) and `probe-strict-neg2.txt` (the coordinator binding slug set to `invented`) both exit 1.

`fixture-check.py` (AC-1) checks this section's limits and runs the same strict validate on a temp copy. It also checks that no string in `FIXTURE` holds `http`, `/`, `\`, `@`, `$` or `P:`, and that `make_fixture.py` regenerates `FIXTURE` byte for byte.

### The registry home (`TEST_FILE`, rows 1 and 2)

The new code goes after `verify()` (`:79`):

- **`MACHINE_TOOLS`** is a module constant.
- **`FIXTURE`** is the constant `ROOT / "tests/tooling/fixtures/registry-home/model-registry.json"`.
- **`build_registry_home(dest: Path) -> dict`** is a plain helper:
  1. It asserts each `MACHINE_TOOLS / rel` in `TOOL_FILES` is a file, so a missing tool fails loudly. Then it copies them to `dest/home/<rel>`.
  2. It copies `FIXTURE` to `dest/home/model-registry.json`.
  3. It runs `resolve_model.py validate --registry <dest/home/model-registry.json> --strict` with the environment below, and asserts exit 0 with stdout and stderr in the message. It never passes `--write-compiled` here, because that writes the tool's own `model-registry.json` and would overwrite the copy. The `--overlay` path below loads the registry without checking it (`resolve_model.py:527`, `:2356-2361`), so this step is the only run-time schema check of `FIXTURE`.
  4. It copies `ROOT / OVERLAY` byte for byte to `dest/project/.agent/model-registry.local.yaml`.
  5. It runs `resolve_model.py validate --overlay <that copy> --write-compiled` with the environment below, and asserts exit 0.
  6. It returns `resolver`, `project` and `env`. `env` is `{"AGENT_MODEL_REGISTRY": <dest/home/model-registry.json>}`, which overrides any ambient value through `run()`'s merge. `AGENT_MODEL_REGISTRY_HOME` is not set: the resolver never reads it, and the wrapper ignores it when `AGENT_MODEL_REGISTRY` is set (`tools/Invoke-CodexDispatch.ps1:554-563`). The wrapper loads `ModelRegistry.psm1` from the registry file's parent folder, which is why the tool files sit next to the copy.
- **Why one temp home for all 16 cases (D-911):** 13 cases could instead run `P:/.agent/tools/resolve_model.py` in place with `AGENT_MODEL_REGISTRY` set to the tracked fixture. That route is not taken. `resolve` with `--project ROOT` would read the tracked compiled overlay `.agent/model-registry.local.json`, so AC-2 could not prove a compile without writing that tracked file. The three wrapper cases need the temp home anyway, because the module refuses an overlay stamped for another registry (`ModelRegistry.psm1:712`). One helper keeps every case on the same inputs.
- **`registry_home`** is a module-scoped fixture: `build_registry_home(tmp_path_factory.mktemp("registry-home"))`. It is added in row 2.
- **`fixture_wrapper(dest: Path, project: Path) -> Path`** reads `ROOT / "tools/Invoke-CodexDispatch.ps1"` as bytes, asserts `NEEDLE` occurs exactly once, replaces it with `$dispatchProjectRoot = '<project as posix>'` and writes `dest / "Invoke-CodexDispatch.ps1"`. It is added in row 2.
- **New test `test_ac_2_fixture_registry_home_compiles`** (row 1):
  - It first asserts `FIXTURE.is_file()`, so Red fails by assertion.
  - It then calls `build_registry_home(tmp_path)`.
  - It asserts that the compiled overlay `dest/project/.agent/model-registry.local.json` holds the SHA-256 of `FIXTURE`'s bytes as its registry stamp.
  - Negative: an overlay copy whose `avkit_coordinator` `cursor-task` slug is `invented` fails `validate` with `unknown_slug` in stderr.

### The rewired registry tests (row 2)

Every `assert` statement and every `parametrize` list stays byte for byte; `hermetic-check.py --asserts` proves it against `BASE`. The changes are to inputs only:

| Test | Input before | Input after | Assertions (unchanged) |
|---|---|---|---|
| `test_registry_contract_preserves_bindings` (7 cases) | `Path("P:/.agent/tools/resolve_model.py")`, `--project ROOT`, `env={"AGENT_MODEL_REGISTRY_HOME": "P:/.agent"}` | takes `registry_home`; `registry_home["resolver"]`, `--project registry_home["project"]`, `env=registry_home["env"]` | `assert result.returncode == 0, result.stdout + result.stderr`; `assert expected in result.stdout` |
| `test_registry_contract_vendor_independence` (2 cases) | as above | as above | `assert (result.returncode != 0) == bool(expected), …`; `assert ("vendor_diversity_violation" if expected else "gpt-6.1-sol") in (result.stderr if expected else result.stdout)` |
| `test_registry_contract_unsupported_harness_refused` | as above | as above | `assert result.returncode != 0 and "unresolvable_on_harness" in result.stderr` |
| `test_registry_contract_bad_configuration_refused` (3 cases) | `ROOT/OVERLAY` read and mutated into `tmp_path/overlay.yaml`; `env = {"AGENT_MODEL_REGISTRY_HOME": "P:/.agent"}`; `bad-explicit` resolves with `--project ROOT` | Same overlay read and mutation. `env = dict(registry_home["env"])`, then `bad-explicit` sets `AGENT_MODEL_REGISTRY` to `tmp_path/absent.json` as before and resolves with `--project registry_home["project"]`. Both calls use `registry_home["resolver"]` | `assert overlay.is_file(), "project overlay missing"`; `assert result.returncode != 0, result.stdout + result.stderr` |
| `test_review_pipeline_wrapper_refuses_before_provider` (3 cases) | `env = os.environ \| {"RECEIPTS_DIR": "C:/Temp/av-kit", "AGENT_MODEL_REGISTRY_HOME": "P:/.agent"}`; runs `ROOT / "tools/Invoke-CodexDispatch.ps1"` | `env = os.environ \| {"RECEIPTS_DIR": "C:/Temp/av-kit"} \| registry_home["env"]`; `bad-registry` still sets `AGENT_MODEL_REGISTRY` to `tmp_path/absent.json` after that; runs `fixture_wrapper(tmp_path / "wrapper", registry_home["project"])`; `cwd=ROOT` unchanged | `assert result.returncode != 0, …`; `assert not marker.exists(), …`; `assert expected in result.stdout + result.stderr` with the same three expected strings |

`test_validation_stages_live_runtime_inputs` (`:838-878`) is unchanged. Its `AGENT_MODEL_REGISTRY` is a stage-state mutation that points at a missing file. `live_runtime_identity` reads a registry only when that variable is set, and the host leaves it unset.

### The governance fixture (rows 3 and 4, D-915)

`migrated_tree` becomes a one-line delegate to a plain helper, `build_migrated_tree(dest: Path, overrides: dict[str, bytes] | None = None) -> Path`.

- **Row 3 (pure refactor):** the helper does exactly what `migrated_tree` does today.
  - Wherever it would read `ROOT / path`, it reads `overrides[path.as_posix()]` when that key is present.
  - An override for a path outside the manifest is not copied.
- **Row 4 (Green)** adds two steps after the copy and before the manifest is written:
  1. **Backlink closure.** It finds every relative `](link)` target in the copied `AGENTS.md` and `GUARDRAILS.md`, using `VERIFIER`'s own regex, skip rule and `#` split. Any target that the tree lacks but `ROOT` or `overrides` has is copied in.
     - A target that is missing in both stays missing, so the verifier still refuses a broken link.
     - Each closure file is copied once. The closure does not recurse.
  2. **Pin rebind.** In the copied `RULE_MAP`, it replaces each `postimage_sha256` value of `counts["AGENTS.md"]` and `counts["GUARDRAILS.md"]` with the SHA-256 of the copied file.
     - The replacement is bytewise, of the 64-hex string. It asserts each old value occurs exactly once, so CRLF and every other byte are kept.
     - The preimage values, block counts and mappings are not touched.

The live content is still what gets copied. So the oracles that are policy on the live tree still run on real bytes:
- the size caps;
- the lost-local-rule regexes;
- the registry owners;
- the routing census.

Sibling plans rely on that census (§Sibling overlap). What stops reding in these cases is the comparison with records frozen at 2026-09-26. That comparison moves to one test, `test_ac_14`, which keeps it on the real tree.

New tests, after `test_governance_preservation_and_routing_inventory`:

| Test | Builds | Expects |
|---|---|---|
| `test_ac_6_pin_follows_the_copied_instructions` | `build_migrated_tree(tmp_path, {"AGENTS.md": live bytes + b"Fixture note appended after adoption.\r\n"})` | `verify(root, "static")` exits 0. Red: exit 1 with `rule map identity mismatch: AGENTS.md` |
| `test_ac_7_backlink_closure_copies_new_targets` | `AGENTS.md` override with `b"[fixture policy](.agent/docs/fixture-new-policy.md)\r\n"` appended, and `.agent/docs/fixture-new-policy.md` → `b"# Fixture policy\r\n"` | exit 0. Red: exit 1 with `broken instruction backlink` |
| `test_ac_8_pin_oracle_still_refuses` | `build_migrated_tree(tmp_path)`; then, in the copied `RULE_MAP`, the `AGENTS.md` postimage value is replaced with `"0" * 64` (count 1 asserted) | exit 1 and `rule map identity mismatch` in stdout, before and after row 4 |
| `test_ac_14_tracked_rule_map_pin_matches_live_instructions` (row 4) | Nothing is built for the live half: it reads the real `ROOT / RULE_MAP` and the real `AGENTS.md` and `GUARDRAILS.md` | See below |

**`test_ac_14`, the one kept D-132 signal (D-915).** A plain helper, `tracked_pin_mismatches(root: Path) -> list[str]`, parses `root / RULE_MAP`'s one JSON block with `VERIFIER`'s `embedded_json` regex (`TEST_FILE` gains `import re`). For `AGENTS.md` and `GUARDRAILS.md` it compares `counts[name]["postimage_sha256"]` with the SHA-256 of `root / name`. For each mismatch it returns one message that names:
- the file, the old pin and the new hash;
- the rebind command, which replaces the 64-hex string bytewise and asserts it occurs once: `uv run python -c "import pathlib; p=pathlib.Path('<RULE_MAP>'); b=p.read_bytes(); assert b.count(b'<old>')==1; p.write_bytes(b.replace(b'<old>', b'<new>'))"`, with the real values filled in;
- the rule: check the rule map still covers the edited file's blocks first, then commit the rebind alone (D-132, `c34866b`).

The test asserts `tracked_pin_mismatches(ROOT) == []`, with the joined messages as the assertion message. Its negative half is in the same test: on a `tmp_path` copy of `RULE_MAP`, `AGENTS.md` (plus one appended byte) and `GUARDRAILS.md`, the helper returns exactly one message, and that message holds `AGENTS.md` and `p.write_bytes(`. This test runs on the real tree on purpose and stays blocking in `py-tests`. After a governance edit it is the one red, where today there are four.

The `migrated_tree` users keep every assertion and parametrize list (`hermetic-check.py --asserts`):

| Test | Input before | Input after | Assertions (unchanged) |
|---|---|---|---|
| `test_review_pipeline_governance_static_oracles` (none, youtube, template, backlink, routing) | `migrated_tree`, frozen pins and the manifest's file list | `migrated_tree` → `build_migrated_tree(tmp_path)` with closure and rebind | `assert result.returncode == (0 if mutation == "none" else 1), …` |
| `test_governance_preservation_and_routing_inventory` (registry, rule-map, fallback, pin, history) | as above | as above | `assert result.returncode == (0 if mutation == "history" else 1), …` |
| `test_registry_contract_generic_class_census` (2 cases) | as above | as above | `assert result.returncode == 1, …`; `assert "global routing class" in result.stdout` |

The `backlink` mutation still fails after row 4: its target, `.agent/docs/missing-required-policy.md`, is in neither `ROOT` nor the overrides. The `rule-map` mutation replaces the whole copied `RULE_MAP` after the build, so it still fails.

### The dispatch arm (rows 5 and 6, D-913)

`DISPATCH_TEST` arm 2 (`:559-571`) changes in three assignment lines plus its comment. The token is never written out in the file, so instantiation cannot rewrite it:

```powershell
            $phToken = ('{' * 2) + 'PROJECT_NAME' + ('}' * 2)
            $phBase = Join-Path ([System.IO.Path]::GetTempPath()) ('cli-dispatch-ph-' + [guid]::NewGuid().ToString('N'))
            $env:RECEIPTS_DIR = Join-Path (Join-Path $phBase $phToken) 'receipts'
```

- The comment above it says, in words and without the literal token, that the token is assembled at run time because instantiation rewrites the literal. It also says the path sits in a fresh folder under the real temp folder, so creating it would succeed, and a pass proves the guard fired.
- The two `Write-TestResult` lines stay byte for byte. So does every line outside arm 2's comment and the three assignment lines.
- **Census dependency:** `DISPATCH_TEST` is in the 2026-09-26 adoption manifest, so `migrated_tree` copies it and `VERIFIER`'s routing census scans every line (`verify_adoption.py:250-300`). The new comment and lines must not match its three patterns: the routing-class pattern (`--class` or `resolve` followed by `builder`, `coordinator` or `verifier`), the unconfigured-routing pattern (`default reviewer:` or `fallback:` followed by a vendor or model family name) and the numeric model-pin pattern (a model family name followed by a digit). `dispatch-check.py --source` checks every changed line against those patterns, copied verbatim from `VERIFIER`, so a slip fails in row 6 rather than in the gate's adoption run.
- The guard (`:162`, `-match '\{\{'`) is unchanged.
- The second assertion now checks a fresh `$phBase` that no earlier run could have created.
- The BOM and CRLF are kept.
- The expected run is FAIL 0 with a total of at least 31, using the default `-Test wrapper-contract`, which makes no live Codex call.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `FIXTURE` | `schema/model-registry.v1.schema.json` (machine). It is checked against the schema and the semantic rules by `resolve_model.py validate --registry <copy> --strict`, in `build_registry_home` (every test run) and in `fixture-check.py`. The `validate --overlay` and `resolve` paths load it without checking it | The keys of §The registry fixture | `fixture-check.py` refuses any other key, slug or capability token |
| `build_migrated_tree` `overrides` | `TEST_FILE` | Keys are POSIX relative paths; values are bytes | A key outside the manifest and the closure is not copied |

No public API, MCP tool or OpenAPI shape changes.

### Acceptance Criteria

The new pytest tests are named `test_ac_<n>_…` and live in `TEST_FILE`: AC-2, AC-6, AC-7, AC-8 and AC-14. The other ACs are plan-local checks or runs of the existing tests.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-1 | unit | `fixture-check.py` passes on `FIXTURE`, which must meet all of these:<br>• `resolve_model.py validate --registry <temp copy> --strict` exits 0, and the copy is unchanged<br>• `make_fixture.py` writes bytes equal to `FIXTURE` into a temp path<br>• top-level keys exactly as §The registry fixture<br>• the slug set equals `OVERLAY`'s bound plus forbidden slugs<br>• each entry has only the six keys<br>• each capability token is in `OVERLAY`'s contract tokens, plus the `coordinator` contract tokens and `agentic_exec`<br>• no string holds `http`, `/`, `\`, `@`, `$` or `P:`<br>• the file is LF with a trailing newline, and is equal to `json.dumps(…, indent=2, sort_keys=True)` of itself | Local Canon (D-911) | `--selftest` refuses a copy with `price_per_mtok`, one with a `sources` key, one with an unknown slug, one with a URL string, one with CRLF, and one whose catalog entry lacks `vendor` (the strict validate refuses it) |
| AC-2 | integration | `test_ac_2_fixture_registry_home_compiles`: `build_registry_home` validates `FIXTURE` with `--strict`, compiles `OVERLAY` against it with exit 0, and the compiled stamp equals `FIXTURE`'s SHA-256 | Local Canon (D-911); Research-backed (probe-mincap) | An overlay naming `invented` fails with `unknown_slug` |
| AC-3 | integration | The four registry tests (13 cases) pass on the fixture, and still pass under `HOSTILE`. Before row 2, `RED_IDS` fail under `HOSTILE` by assertion | Local Canon (D-911; TOOLING-SHARED-REGISTRY-COUPLING) | The `HOSTILE` run is the negative: it proves the tests no longer read the ambient registry |
| AC-4 | integration | `test_review_pipeline_wrapper_refuses_before_provider` (3 cases) runs a temp copy of `WRAPPER` with `NEEDLE` replaced once and the fixture environment. It passes, and under `HOSTILE` too. The fake provider is never called | Local Canon (D-911) | `fixture_wrapper` asserts the needle count is 1, so a moved line fails loudly; the `bad-registry` case keeps its `registry_not_found` refusal |
| AC-5 | unit | `hermetic-check.py` passes. Its checks:<br>• `TEST_FILE` is CRLF on every line with no BOM<br>• `P:/.agent` occurs exactly once (`MACHINE_TOOLS`)<br>• no line holds both `AGENT_MODEL_REGISTRY_HOME` and `P:/`<br>• no call passes `"--project"` followed by `ROOT` (AST)<br>• the string `tools/Invoke-CodexDispatch.ps1` occurs only inside `fixture_wrapper`<br>• `--asserts`: for every test named in §The rewired registry tests and §The governance fixture, the AST dumps of its `assert` statements and its decorator list equal `BASE`'s | Local Canon (§4a M-7 rows above) | `--selftest` refuses a copy with an extra `P:/.agent`, one with `--project ROOT`, one with a changed assert, one with a changed parametrize list and one with an LF line. Run on `BASE`, it refuses (the Red half) |
| AC-6 | integration | `test_ac_6_pin_follows_the_copied_instructions` passes | Local Canon (D-915; TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE) | Red: exit 1 with `rule map identity mismatch` |
| AC-7 | integration | `test_ac_7_backlink_closure_copies_new_targets` passes | Local Canon (D-915) | Red: exit 1 with `broken instruction backlink` |
| AC-8 | integration | `test_ac_8_pin_oracle_still_refuses` passes before and after row 4 | Local Canon (D-915) | It is itself the negative: a wrong pin is still refused after the rebind |
| AC-9 | integration | The 12 `migrated_tree` cases (static_oracles ×5, preservation ×5, census ×2) pass after rows 3 and 4 with unchanged assertions; the `backlink` and `rule-map` mutations still exit 1 | Local Canon (D-915) | Those two mutations are the negatives |
| AC-10 | integration | `DISPATCH_TEST` reports FAIL 0, with a total of at least 31, and both `placeholder receipts dir refused` and `refusal created no placeholder dir` PASS (`dispatch-check.py --expect-clean`). `dispatch-check.py --source` passes:<br>• arm 2 holds no `{{`<br>• the file keeps the BOM and CRLF on every line<br>• the two `Write-TestResult` lines are byte-equal to `BASE`<br>• every line outside arm 2's comment and assignments is byte-equal to `BASE`<br>• no changed line matches `VERIFIER`'s three census patterns (routing class, unconfigured routing, numeric model pin), copied verbatim | Local Canon (D-913; CLI-DISPATCH-PLACEHOLDER-FIXTURE) | Red: row 0's receipt passes `--exact-baseline` (exactly that FAIL pair). `--selftest` refuses a source with the literal token, one with an LF line, one with a changed assertion line and one whose new comment names a model family followed by a digit |
| AC-11 | integration | `pytest TEST_FILE` on the real tree, normal environment: 0 failed, and passed equals row 0's count plus 5 | Local Canon (session brief: still passes after Session 86) | A count other than base + 5 fails `adoption-check` (`hermetic-check.py --count`) in the gate |
| AC-12 | integration | `live-probe.py`, run once in this session's gate with `AGENT_MODEL_REGISTRY` removed, against the real machine registry and `--project P:/av-kit`:<br>• each of the 7 `test_registry_contract_preserves_bindings` cases (its `class_name`, `harness` and `expected`, read from `BASE`'s parametrize list by AST) exits 0 with `--format json` and prints `expected`<br>• `resolve avkit_independent_reviewer --harness codex-cli --author-vendor anthropic` prints `gpt-6.1-sol`<br>• `validate --overlay .agent/model-registry.local.yaml --check-compiled` exits 0<br>It is plan-local and is not kept as a test (D-912) | Local Canon (D-912) | `--author-vendor openai` must exit non-zero with `vendor_diversity_violation`; `--selftest` refuses a case list shorter than 7 |
| AC-13 | integration | `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE` and `CLI-DISPATCH-PLACEHOLDER-FIXTURE` are `resolved`, and `TOOLING-SHARED-REGISTRY-COUPLING` is `mitigated` with its residual stated (D-912), each with `verification` and `resolution_path`. `issue-resolve.py` reports no other parsed difference, and `issue_triage.py render --check` exits 0 after `render`. `known-issues.yaml` and `known-issues.md` stay LF | Local Canon (the brief: registers through the repo tools) | `issue-resolve.py` refuses a key outside its three, another issue, and a wrong `--expect-sha256` |
| AC-14 | integration | `test_ac_14_tracked_rule_map_pin_matches_live_instructions` passes on the real tree: the tracked `RULE_MAP` pins equal the SHA-256 of the live `AGENTS.md` and `GUARDRAILS.md` | Human-approved (D-132, USER_EXPLICIT 2026-10-27); Local Canon (D-915) | The same test's `tmp_path` half: one appended byte gives exactly one message, holding `AGENTS.md` and the `p.write_bytes(` rebind command |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| What the registry tests resolve against | Local Canon | D-911 (brief, handed): a tracked synthetic registry, with tool code copied at run time |
| Which live check remains | Local Canon | D-912 (brief, handed) |
| Where the dispatch fix lands | Local Canon | D-913 (brief, handed): av-kit's copy; upstream untouched |
| The leftover temp folder | Local Canon | D-914 (brief, handed): left for Mat, with a command |
| How the governance fixture stops pinning live bytes | Local Canon; Human-approved (D-132) | D-915 (brief, handed, lists M-6): pin rebind plus backlink closure in the copy; one test keeps the tracked pin check on the real tree |
| Which assertions may change | Local Canon | None. Every changed test is named above with its unchanged assertions (§4a M-7) |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `tests/tooling/test_framework_adoption.py` | modify | CRLF, kept (write with `newline=""` from CRLF text) | Registry home with strict validate, wrapper copy, migrated-tree helper, tracked-pin helper, five new tests |
| `tests/tooling/fixtures/registry-home/model-registry.json` | new | LF | The synthetic registry |
| `tests/tooling/fixtures/registry-home/make_fixture.py` | new | LF | The fixture's generator, kept next to it (D-911); standard library only, not collected by pytest |
| `.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1` | modify | UTF-8 BOM and CRLF, kept | Arm 2's token and base path |
| `.agent/context/known-issues.yaml` | modify, by `issue-resolve.py` only | LF, kept | The three issues' `status`, `verification` and `resolution_path` |
| `.agent/context/known-issues.md` | regenerate, by `issue_triage.py render` only | LF, kept | Their rows |

### Project files

- **Plan-local scripts**, all in this plan folder:
  - `baseline.ps1`, `session-gate.ps1`;
  - `red-check.py`, `identity.py` and `scope-check.py`, copied from `2026-11-15-framework-small-syncs` with this plan's `PLAN`, `PROJECT_ARTIFACTS` and scope. `scope-check.py` changes in two ways, so that nothing compares a scoped file with `HEAD` (D-918):
    - Its `HEAD` rule: where the peer requires `git rev-parse HEAD` to equal `baseline.sha`, this copy lets `HEAD` move only by commits whose changed paths (`git diff --name-only <baseline.sha> HEAD`) are all in `baseline-dirty.txt` and still have their row-0 bytes in `baseline-dirty-hashes.json`. That is an earlier session's work committed unchanged. Any other moved path is S4. Its other-plan list is read from `baseline.sha`'s tree, not `HEAD`'s.
    - A `--subtree packages/api` mode: it hashes every file under that path that `git ls-files --cached --others --exclude-standard` lists and compares the set with row 0's `baseline-api.json`. H1-4 uses it;
  - `issue-resolve.py`, copied from `2026-11-15-closeout-record-once` with `SCRATCH = C:/Temp/av-kit/tth`;
  - `fixture-check.py`, `hermetic-check.py`, `dispatch-check.py` (adapted from `2026-11-14-review-limits-no-token-budget`) and `live-probe.py`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-api.json`, `red-require.txt`.
- **State:** `docs/execution/metrics.md`, `.agent/context/current-focus.md`, the handoff, the rolling reviews and the reflection.

### Plan-local checkers

- **`make_fixture.py`** is not plan-local: it is tracked next to `FIXTURE` (§The registry fixture). It reads a registry (`--registry`, default `P:/.agent/model-registry.json`, read only) and `OVERLAY`, builds the data of §The registry fixture, and writes `FIXTURE`, or the path given by `--out`. It never writes elsewhere.
- **`fixture-check.py`** checks AC-1. It reads `FIXTURE`, `OVERLAY` and `make_fixture.py`'s output in a temp path. It runs `resolve_model.py validate --registry <temp copy> --strict` without `--write-compiled`, from a temp copy of `TOOL_FILES`, so `P:/.agent` is never written. It has `--selftest` with its own fixtures.
- **`hermetic-check.py`** checks AC-5. It has three more modes:
  - `--asserts` compares against `C:/Temp/av-kit/tth/base/test_framework_adoption.py`.
  - `--eol` checks the line endings of every path in §Files Modified: CRLF with no BOM for `TEST_FILE`; BOM and CRLF for `DISPATCH_TEST`; LF for the other four.
  - `--count RECEIPT` is the gate's `adoption-check` (AC-11). It reads the receipt's pytest summary line and `C:/Temp/av-kit/tth/tth-base-adoption.txt`'s, and passes only when the receipt shows 0 failed, 0 errors and exactly base passed plus 5.
  - `--selftest` uses its own fixtures, including summary lines for `--count`.
- **`dispatch-check.py`** is the review-limits copy, with `MIN_TOTAL = 31` and `BASELINE_FAILS` kept. It adds these modes:
  - `--expect-clean`: FAIL 0, and both names PASS;
  - `--source`: AC-10, including the census patterns, copied verbatim from `VERIFIER:250-300`;
  - `--selftest`, covering the new modes.
- **`live-probe.py`** checks AC-12. It reads the 7 `preserves_bindings` cases from `BASE`'s parametrize list by AST and resolves each against the real machine registry, then the reviewer route both ways, then `--check-compiled`. It runs once, in row 7 and the gate's `live-probe` step, and is not kept after the session (D-912). It has `--selftest`.
- **`red-check.py`** is used unchanged in logic. Its `--require` takes full pytest ids, read from `red-require.txt` by the row command.

### Sibling overlap

| Path | Sibling | How this plan binds |
|---|---|---|
| `tests/tooling/` | Session 76 only (grouping `:124`). Session 84 (HDP grouping) added `test_closeout_record_once.py`. Session 83 adds `test_check_home_path.py` after this session | This plan edits only `TEST_FILE` and adds `FIXTURE`. It touches no other file in the folder |
| `TEST_FILE` consumers | Session 79 (`triage-tool-fixes`) and Session 83 (`docs-path-hygiene`) run `TEST_FILE` in their gates and rely on `migrated_tree` copying live bytes and running the census | The copy and the census stay (D-915). Their runs see 5 more passing tests |
| Files that `migrated_tree` copies (`AGENTS.md`, skills, templates, `commands.md`) | Session 87 and Session 83 edit some of them | The rebind and closure make their edits safe for this fixture; the census still applies to them. An edit to `AGENTS.md` or `GUARDRAILS.md` still reds `test_ac_14`, whose message gives the rebind command, so such a session rebinds `RULE_MAP` alone, as D-132 rules |
| `known-issues.yaml`, `known-issues.md`, `current-focus.md`, `metrics.md` | Every session in the set | Bound by content: row 0 records their hashes; `issue-resolve.py --expect-sha256` refuses a moved register (S4) |
| `.agent/skills/cli-dispatch/` | Session 76 only (grouping `:124`) | No sibling runs `dispatch-check.py --exact-baseline` (plan-time grep of the 2026-11-15 plans), so no sibling gate depends on the two FAILs |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Removing the empty `%TEMP%\av-kit\receipts\dispatch-tests` folder | human action | — | D-914: the handoff gives Mat the command |
| `test_hdp_expert_pass.py`'s two live checks against the machine registry: `test_ac_9_peer_reviewer_class_resolves_only_on_claude_code_agents` and `test_ac_10_compiled_registry_is_current_and_adds_only_the_peer_reviewer` | out-of-scope | — | Session 86's deliberate live checks, kept (D-912). `test_ac_10_…` still reds on every machine registry bump, the residual that leaves `TOOLING-SHARED-REGISTRY-COUPLING` `mitigated` |
| CI not running `tests/tooling/` | out-of-scope | — | No CI change is in the grouping's scope for Session 76; D-917 |
| The 11 files under the census prefixes that the 2026-09-26 manifest predates (plan-time probe) | out-of-scope | — | Bringing them into the fixture would widen the census to files no test covers today; D-917 |
| Porting the dispatch fix upstream, or editing `P:/agentic-framework` | out-of-scope | — | Hard constraint; D-913 names the defect for Mat |
| Editing `VERIFIER`, `RULE_MAP` or the adoption manifest | out-of-scope | — | They are the 2026-09-26 session's evidence; only the fixture's copies change (D-915) |
| The grouping's §6 status row for Session 76 | out-of-scope | — | The coordinator updates the shared grouping file; D-917 |
| `Test-CliDispatch.ps1` live arms (`-Test` other than `wrapper-contract`) | out-of-scope | — | They call Codex and Claude; the gate runs the default contract arms |

## BUILD_PLAN.md Audit

This project adds no build-plan section and changes no MEU, so `docs/BUILD_PLAN.md` and `meu-status.yaml` do not change. Other sessions may have uncommitted edits in them, and this session leaves those alone. H1-3 proves the render is consistent:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/tth/tth-render-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/tth/tth-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following, in order. If any step fails, the row fails and nothing else runs.

1. **Tree state.** It records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`. The earlier sessions' work is expected there. `baseline.sha` is a reference point only: no check compares a scoped file with it or with `HEAD`.
2. **Path-scoped baseline.**
   - It writes `baseline-scope.json`: for each path in §Files Modified, its SHA-256, or `absent`. `FIXTURE` must be `absent`.
   - It writes `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope, or `deleted`.
   - It writes `baseline-api.json`: the SHA-256 of every file under `packages/api` that `git ls-files --cached --others --exclude-standard` lists, for H1-4's skip check.
   - It copies `TEST_FILE`, `DISPATCH_TEST` and `RULE_MAP` to `C:/Temp/av-kit/tth/base/` as `BASE`.
   - It writes the line endings of each scope file to `tth-eol-base.txt`, measured with Python bytes. If they differ from §Single-statement contracts, that is S2.
3. **Needle and pins.** `NEEDLE` must occur exactly once in `WRAPPER`, and each `RULE_MAP` postimage value exactly once in `RULE_MAP`. Otherwise S2.
4. **`RED_HOME`.** It copies `TOOL_FILES` and the live registry into `RED_HOME`, removes the `cursor-grok-4.6` catalog entry from the copy, and checks that `resolve_model.py validate --overlay OVERLAY` with `HOSTILE` exits non-zero with `unknown_slug`.
5. **`red-require.txt`.** It writes the 12 full pytest ids that must fail under `HOSTILE` in row 1:
   - the 7 `preserves_bindings` ids;
   - the 2 `vendor_independence` ids;
   - `test_registry_contract_unsupported_harness_refused`;
   - `test_review_pipeline_wrapper_refuses_before_provider[same-vendor]`;
   - `test_ac_2_fixture_registry_home_compiles`.

   The first 11 are taken from `pytest TEST_FILE --collect-only -q`, with the `tests/tooling/test_framework_adoption.py::` prefix removed. That leaves `name[params]`, the failure-block title that `red-check.py --require` matches. The count of 11 is checked there. The AC-2 id is added by name, because it does not exist until row 1.
6. **Base receipts.**
   - It runs `uv sync --frozen --all-packages`.
   - It runs the base Python suite (`tth-base-py.txt`), with `TMP` and `TEMP` at `C:\Temp\av-kit\tth\tmp`.
   - It runs the base adoption file (`tth-base-adoption.txt`), whose passed count AC-11 uses.
   - It runs the base `DISPATCH_TEST` with the user temp folder (`tth-base-dispatch.txt`, plus its `.exit`).
7. **Plan-local scripts.** It copies and writes the checkers of §Project files and runs every `--selftest`. Each selftest uses its own fixtures, not the repo files. It also runs `hermetic-check.py` on `BASE`, which must refuse (the Red half of AC-5).

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` checks that exactly, with `--require` for each id.
- **Registry (row 1).**
  - Row 1 adds `MACHINE_TOOLS`, the `FIXTURE` constant, `build_registry_home` (with its strict-validate step) and the AC-2 test. It does not add `FIXTURE` itself.
  - It runs the selection `-k "preserves_bindings or vendor_independence or unsupported_harness or bad_configuration or wrapper_refuses or test_ac_2_"` under `HOSTILE`.
  - The old tests fail because the ambient registry wins over `AGENT_MODEL_REGISTRY_HOME`. AC-2 fails on `FIXTURE.is_file()`.
  - `bad_configuration` and the other wrapper cases may pass, because they assert a refusal.
- **Registry (row 2).**
  - Row 2 adds `make_fixture.py` and writes `FIXTURE` with it, then adds `registry_home` and `fixture_wrapper` and rewires the five test functions (16 cases).
  - The same selection under `HOSTILE` then passes, and so does the whole file under the normal environment.
- **Governance (rows 3 and 4).**
  - Row 3 is the pure refactor plus the three new tests. AC-6 and AC-7 fail by assertion, while AC-8 and the 12 existing cases pass.
  - Row 4 adds closure and rebind, plus `tracked_pin_mismatches` and `test_ac_14`. Then all of them pass. `test_ac_14` passes on today's tree, because the tracked pins match the live files, so it has no Red. Its negative is its own `tmp_path` half.
- **Dispatch (rows 5 and 6).**
  - Row 5's Red is row 0's base receipt: `dispatch-check.py --exact-baseline` shows exactly the two FAILs.
  - Row 6 edits arm 2, then runs `--expect-clean` and `--source`.
- **Expectations stay immutable in Green.** `hermetic-check.py --asserts` proves it for every existing test this plan touches.
- **Line endings.** `TEST_FILE` is CRLF, and `DISPATCH_TEST` is BOM and CRLF. They are measured with Python bytes and written with `newline=""` from CRLF text, with the BOM kept. `hermetic-check.py --eol` runs after every editing row.

### 3. Live probe (row 7)

`live-probe.py` runs AC-12 against the real machine registry and the real compiled overlay: the 7 project bindings, the reviewer route and the compiled stamp. Apart from `make_fixture.py` in row 2 and Session 86's `test_ac_9` and `test_ac_10` in `py-tests`, it is the only step that reads `P:/.agent/model-registry.json`. A failure here means a live route is broken, which is S6, not a test defect.

### Session gate (H1-2)

`session-gate.ps1` follows the peer's shape:

- one receipt per step in `C:/Temp/av-kit/tth/`, named `tth-D6-<step>`;
- fail-fast, with later steps printed as `not_run`;
- the last line is `session-gate: all steps exit 0`.

A step that needs `HOSTILE` sets it in a `try`/`finally` around that step's process only.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `tools-lint` (`ruff check tests/tooling/`); `py-lint` (`ruff check packages/ tests/`); `task-contract`; `scope-paths` (`scope-check.py`: every changed path is in §Files Modified, this plan folder or the closeout artifacts, or is in `baseline-dirty.txt` with its row-0 content); `fixture-check`; `hermetic-check` (with `--asserts` and `--eol`); `dispatch-source` (`dispatch-check.py --source`); `red-check-selftest` |
| Targeted | `adoption-tests` (`pytest TEST_FILE`, then `adoption-check`: 0 failed, passed = base + 5); `adoption-hostile` (row 1's selection under `HOSTILE`, 0 failed); `dispatch-tests` (`DISPATCH_TEST` with `UserTemp`, then `dispatch-check.py --expect-clean`) |
| Fresh full | `py-tests` (the full suite); `state-render`; `issues-render` (`issue_triage.py render --check`); `closeout-selftest`; `live-probe` (AC-12) |
| Skipped, with reason | `py-types`: nothing under `packages/` changes. `ui-*`: nothing under `ui/` changes. `mcp-*`: no MCP change. `openapi`: no `packages/api` file differs from row 0's `baseline-api.json` (H1-4). `build-record`: no build |

`py-tests` excuses only the ids that row 0's receipt shows failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds line endings other than §Single-statement contracts, a `NEEDLE` count other than 1, or a `RULE_MAP` pin count other than 1 | Stop; an earlier session changed a file this plan binds to. Bring the measurement to Mat |
| S3 | A Red receipt fails `red-check.py` | Fix the test setup; do not move to Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path changes content during the session, or `HEAD` moves by a commit that touches any other path, or `issue-resolve.py` refuses the register hash | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | A rewired test cannot pass without changing an assertion or a parametrize list, or another `VERIFIER` check refuses the AC-6 or AC-7 tree | Stop; that is an M-7 change this plan does not name. Bring it to Mat |
| S6 | `live-probe.py` fails | Stop; a live project binding or the reviewer route is broken, and only Mat changes the machine registry |
| S7 | Codex is unavailable or the ledger refuses | Mat |

## Decision Log

> [!NOTE]
> D-916 to D-918 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. D-911 to D-915 failed the §4 test, because each has a credible alternative, so each is written as a Brief below. Mat handed this set to the agent on 2026-11-15. Each is therefore recorded `resolution: autonomous`, with the agent's own tag and its `mandatory:` list, and none hits an item that stays Mat's.
>
> This plan has no STOP item. D-914 picks the option that avoids M-2. D-911 checked M-12: the fixture names only model ids that the tracked overlay already names. D-915 lists M-6, because it touches Mat's D-132 ruling; M-6 can be handed, it keeps D-132's signal in `test_ac_14`, and it does not hit M-11, because that test stays blocking. Every changed test is named with its assertions, so §4a M-7 is approved scope.
>
> The grouping rows D-813, D-815 and D-816 stay in the grouping file's §8 and are not copied here. H2-2 reads them through `--decision-source` on the grouping file (this plan's `grouping_source`). It reads the issue decision logs through `--decision-issue`.
>
> The grouping's old "Carry-forward" wording (`:325-329`, "each row appears in its consuming session's reflection") is ignored under the new HDP §6: the reflection's `### Decisions Log` lists only this session's reversible autonomous choices.
>
> D-919 to D-921 are left free for execution.

```yaml
decision_log:
  - id: D-911
    stage: planning
    question: "What do the registry tests resolve against instead of the machine registry?"
    resolution: autonomous
    class: source-conflict
    mandatory: none
    chosen: "A: a tracked synthetic registry (tests/tooling/fixtures/registry-home/model-registry.json, written by make_fixture.py beside it) in a temp registry home. build_registry_home checks it with validate --registry --strict (never --write-compiled, which would overwrite the copy), copies the resolver's tool code from P:/.agent at run time, compiles the overlay in a temp project, and the dispatch wrapper runs from a temp copy whose project root points at that project. Its env sets only AGENT_MODEL_REGISTRY. The fixture's coordinator binding is synthetic (the overlay's cursor-grok-4.6), not the live one."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:33 — the issue's durable fix: give these tests a fixture registry home, a snapshot of the resolver contract plus a registry"
      - "C:/Temp/av-kit/tth/probe-mincap.txt — a 3804-byte registry carries every case of the five test functions (16 cases)"
      - "C:/Temp/av-kit/tth/probe-strict.txt — validate --registry --strict passes on that shape and leaves the copy unchanged; probe-strict-neg.txt and probe-strict-neg2.txt exit 1"
      - "tests/tooling/test_framework_adoption.py:65-76 — run() merges the test env last, so a fixture env overrides the ambient one"
      - "C:/Temp/av-kit/tooling-test-hermeticity/tth-expert-pass.txt — the expert pass's D-911 findings"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this set, so the recommendation is chosen. The registry data is what drifted all three times; the tool code is what the tests are about, so copying it keeps them testing the real resolver. The strict validate is the only run-time schema check of the fixture, because the --overlay and resolve paths load the registry unchecked (resolve_model.py:527, :2356-2361). A tracked snapshot of the tools lost: it publishes machine tooling upstream does not ship to adopters and goes stale against the resolver it claims to test. Copying the live registry into the temp home lost: it fixes the stamp but a removed slug still reds the tests. Running 13 cases in place with AGENT_MODEL_REGISTRY lost: resolve with --project ROOT reads the tracked compiled overlay, so AC-2 could not prove a compile without writing a tracked file, and the three wrapper cases need the temp home anyway. The cost: an overlay rebind now also needs make_fixture.py re-run, in the same edit that changes the expected-model list. M-12 checked: the fixture names only ids the tracked overlay already names, with no prices, sources or paths."
  - id: D-912
    stage: planning
    question: "Which live check of the real registry remains?"
    resolution: autonomous
    class: source-conflict
    mandatory: none
    chosen: "A: no new kept or opt-in pytest. The live checks that stay are Session 86's test_hdp_expert_pass.py::test_ac_9_peer_reviewer_class_resolves_only_on_claude_code_agents and ::test_ac_10_compiled_registry_is_current_and_adds_only_the_peer_reviewer (blocking --check-compiled), and the wrapper failing closed at every real dispatch. This session's gate runs live-probe.py once over all 7 project bindings, the reviewer route and the compiled stamp (AC-12); it is plan-local and not kept. TOOLING-SHARED-REGISTRY-COUPLING is marked mitigated, because a machine registry bump still reds test_ac_10 until the overlay is revalidated."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:33 — 'keeping one opt-in live check' (D-70, autonomous)"
      - "tests/tooling/test_hdp_expert_pass.py:499 and :526 — the two live checks"
      - ".agent/docs/issue-lifecycle-guide.md:359 — mitigated means partially addressed"
      - "C:/Temp/av-kit/tooling-test-hermeticity/tth-expert-pass.txt — the expert pass's D-912 findings"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this set, so the recommendation is chosen. A live check of the stamp already exists and blocks, which is stronger than opt-in, and its red on a bump is a true signal, because the wrapper refuses the same stale stamp. A kept live test of the 7 bindings lost: it is the coupling this issue removes. An env-gated pytest lost: skipped by default, it is a test no gate runs, close to waiving it (M-11). Marking the issue resolved lost: its own symptom (known-issues.yaml:40) stays true through test_ac_10, and no ruling chose to keep that red, so resolved would overclaim. The stated loss: between sessions, a registry edit that breaks a coordinator, builder, verifier or router binding is caught only when something resolves that class live, and the resolver then refuses it. Keeping the 16 cases live lost: that is the defect."
  - id: D-913
    stage: planning
    question: "Where does the dispatch placeholder fix land?"
    resolution: autonomous
    class: source-conflict
    mandatory: none
    chosen: "A: in av-kit's copy, as a divergence: arm 2 assembles the token at run time under a fresh temp folder; upstream is not edited, and the handoff names upstream's latent defect for Mat."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/tth/up-clidispatch-log.txt — no upstream commit touches the arm after the copy"
      - ".agent/context/known-issues.yaml:5244 — 'give the fixture a path that still holds the token after instantiation'"
      - "P:/zorivest — no such arm in its copy (plan-time search)"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this set, so the recommendation is chosen. Upstream's literal token is correct until a project instantiates it, so the defect only shows in adopters; av-kit is the adopter and the only place this session may write. Upstream-first lost: av-kit cannot edit upstream, and the two FAILs would stay until a re-port. Keeping D-739's allowance lost: every gate keeps carrying an exception for a known false failure."
  - id: D-914
    stage: planning
    question: "What happens to the empty folder the old arm left in the user temp folder?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: leave it; the handoff gives Mat a one-line removal command and the issue's resolution says so."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:5244 notes — 'clean the leftover %TEMP%/av-kit/receipts/dispatch-tests'"
      - "plan-time listing — the folder and its parent hold no files"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this set, so the recommendation is chosen. The folder is empty and harmless, and after the fix nothing recreates it. Deleting it in the session lost: it removes something outside the repository, which is M-2 and would make this a STOP item for no gain. Saying nothing lost: the issue asks for the cleanup, so Mat should know it is his to do."
  - id: D-915
    stage: planning
    question: "How does the governance fixture stop pinning the live instruction files?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6]
    chosen: "A, narrowed by the expert pass: build_migrated_tree keeps copying live bytes, copies any link target of AGENTS.md and GUARDRAILS.md that the manifest predates, and rebinds the copied rule map's two postimage pins to the copied files, for the 12 existing cases and AC-6 and AC-7. One new test, test_ac_14_tracked_rule_map_pin_matches_live_instructions, keeps D-132's check on the real tree: it compares the tracked rule-preservation.md pins with the live files and, on a mismatch, prints the bytewise rebind command. AC-8 proves a wrong pin is still refused in the copy."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:859 — the dangling backlink, then the rule-map hash"
      - "docs/execution/reflections/2026-10-26-tts-sideload-load-reflection.md:116 — D-132, USER_EXPLICIT 2026-10-27 'Update pin, commit+push (Recommended)'; carrying the four failures 'would hide later rule-map drift'"
      - ".agent/context/known-issues.yaml:870 — D-132's hand rebind (c34866b)"
      - "docs/execution/plans/2026-11-15-framework-small-syncs/implementation-plan.md AC-10 — a sibling relies on the census over live bytes"
      - "C:/Temp/av-kit/tooling-test-hermeticity/tth-expert-pass.txt — the expert pass's D-915 findings and the cheaper option"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this set, so the recommendation is chosen. M-6 is listed because D-132 is a USER_EXPLICIT ruling that the tracked pin stays checked and is rebound by hand, and this choice touches it. It keeps that ruling's signal in test_ac_14 rather than removing it, so it can be handed to the agent. M-11 is not hit: no blocking check is waived, because test_ac_14 runs in py-tests on the real tree and still fails on drift; only the three duplicate reds go. A fully synthetic tree lost: it drops the census over live bytes that Sessions 79, 83 and 87 rely on. A git snapshot at the adoption commit lost: after the history squash that hash resolves only in the backup bundles. Rebinding in every case, the first draft, lost: nothing would check the tracked pin again, which is the drift D-132 wanted visible. Keeping things as they are lost: every governance edit reds four tests."
  - id: D-916
    stage: planning
    question: "Which gate steps run?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The steps of §Session gate: Python lint and tests, the adoption file normally and under HOSTILE, the dispatch tests, the plan-local checks, the registers and the live probe; types, UI, MCP, OpenAPI and build skipped with reasons."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-framework-small-syncs/implementation-plan.md §Session gate — the shape for a tooling session"
      - "docs/execution/plans/2026-11-14-review-limits-no-token-budget/session-gate.ps1 — the dispatch-tests step with UserTemp"
    research: { engine: none, sources: [] }
    reasoning: "One Python test file, one PowerShell test and two registers change, so their tests and checks run; nothing under packages/ or ui/ changes. The hostile run is the proof the tests no longer read the ambient registry."
  - id: D-917
    stage: planning
    question: "What stays out of scope?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The rows of §Out of Scope"
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:143-152 — Session 76's scope"
    research: { engine: none, sources: [] }
    reasoning: "Each row is outside the three issues, belongs to another session, or is a hard constraint of this set."
  - id: D-918
    stage: planning
    question: "What does this session bind to, given earlier sessions may be uncommitted?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Row 0's bytes: scope checks by path and content, not HEAD; HEAD may move only by commits whose changed paths are all in baseline-dirty.txt with their row-0 bytes; the OpenAPI skip compares packages/api with row 0's hashes, not with a commit; the registers bound by hash through issue-resolve.py --expect-sha256; S4 on any drift."
    source_tag: Local Canon
    precedents:
      - "the session brief — baselines path-scoped and bound to content"
      - "docs/execution/plans/2026-11-15-closeout-record-once/implementation-plan.md — the same binding for the shared register"
    research: { engine: none, sources: [] }
    reasoning: "Mat has not said whether each session is committed after it closes, so HEAD may lag the tree. Binding to row-0 content keeps the earlier sessions' work safe either way."
```

Expert pass (fresh context): 5 briefs. Holds: D-913, D-914. Changed: D-911, D-912, D-915. Not adopted: none.

Receipt: `C:/Temp/av-kit/tooling-test-hermeticity/tth-expert-pass.txt` (av-kit-peer-reviewer, fresh context, 2026-11-15). Its optional route for D-911, running 13 cases in place with `AGENT_MODEL_REGISTRY`, was weighed and not taken; the reason is in D-911's reasoning.

### D-911: What should the registry tests resolve against instead of your machine registry?

**I recommend A: a small synthetic registry in the repository, used through a temp registry home.** The tests still run the real resolver code, which they copy from `P:/.agent` at run time. The helper first checks the fixture with `validate --registry --strict`, then compiles the project overlay against it in a temp project, and the wrapper cases run a temp copy of the dispatch wrapper. A registry bump or an ambient `AGENT_MODEL_REGISTRY` then cannot red them; the plan-time probe shows every case passing on a 3.8 KB file. The fixture's coordinator binding is synthetic: it names the overlay's model, not the live one.

A can fail if a resolver update needs a registry field the fixture lacks. The strict validate in `build_registry_home` then fails every registry test with the validator's message, and the fix is one field in the fixture. A new optional field with a silent default would not be caught. A also adds upkeep: when you rebind a model in the overlay, you re-run `tests/tooling/fixtures/registry-home/make_fixture.py`, in the same edit that changes the tests' expected models. Undo: revert one test file and the fixture folder.

- B: track a snapshot of the resolver tools too. That is fully hermetic, but it publishes machine tooling that upstream does not ship to adopters, and the snapshot goes stale against the resolver it claims to test.
- C: copy the live registry into the temp home. It fixes the stale stamp, but a removed or renamed model still reds the tests.
- D: keep things as they are. The tests red on every registry change, as they have three times.

Refs: `known-issues.yaml:33` (D-70), `C:/Temp/av-kit/tth/probe-mincap.txt`, `probe-strict.txt`, `probe-red2.txt`, `resolve_model.py:527` and `:2356-2361`, M-12 (not hit).

### D-912: Which live check of the real registry remains?

**I recommend A: no new kept or opt-in test.** Session 86's `test_hdp_expert_pass.py` keeps two live checks that block: `test_ac_9_…` resolves the peer-reviewer route, and `test_ac_10_…` checks the compiled overlay's stamp against the machine registry. The wrapper refuses a broken route at every real dispatch. This session's gate runs `live-probe.py` once over all seven project bindings, the reviewer route and the stamp; it is not kept afterwards.

What this leaves: a machine registry bump still reds `test_ac_10_…` until the overlay is revalidated. That red is true, because the wrapper would refuse the same stale stamp. So `TOOLING-SHARED-REGISTRY-COUPLING` is marked `mitigated`, not `resolved`. Between sessions, a registry edit that breaks a coordinator, builder, verifier or router binding is caught only when something resolves that class live, and the resolver then refuses it.

A can fail if Session 86's tests are later made hermetic too; then nothing checks the live registry between sessions. Undo: add a test.

- B: add an env-gated pytest that skips by default. It does what the issue's wording says, but a skipped test is one no gate runs.
- C: keep the 16 cases live. That is the defect.

Refs: `known-issues.yaml:33` and `:40`, `tests/tooling/test_hdp_expert_pass.py:499` and `:526`, `issue-lifecycle-guide.md:359`, AC-12, AC-13, M-11.

### D-913: Where does the dispatch placeholder fix go?

**I recommend A: in av-kit's copy, as av-kit's own change.** Arm 2 builds the token at run time, so instantiation cannot rewrite it, and it uses a fresh folder under the real temp folder. Upstream's copy is correct until a project instantiates it, so the bug shows only in adopters, and av-kit is the adopter. The handoff names the upstream defect for you.

A can fail if a later re-port of the dispatch skill overwrites av-kit's copy; the two FAILs would come back and the handoff note says why. Undo: three lines.

- B: fix upstream first, then re-port. That is cleaner, but this session cannot edit upstream, so the two FAILs stay until you do.
- C: keep things as they are, with D-739's allowance. Every gate keeps an exception for a known false failure.

One dependency: the file is in the 2026-09-26 adoption manifest, so the routing census scans the new comment. `dispatch-check.py --source` checks the changed lines against the census patterns.

Refs: `known-issues.yaml:5244`, D-739, `C:/Temp/av-kit/tth/up-clidispatch-log.txt`, `verify_adoption.py:250-300`, arm 2 at `Test-CliDispatch.ps1:559-571`.

### D-914: What happens to the empty folder the old arm left in your temp folder?

**I recommend A: leave it, and give you a one-line command in the handoff.** The folder and its parent are empty, and nothing creates them after the fix. A can fail only in the sense that the folder stays until you run the command. Undo: nothing to undo.

- B: delete it in the session. That is tidier, but it deletes something outside the repository, which is yours to rule (M-2).
- C: keep things as they are and say nothing. The issue asks for the cleanup, so you would not know it is still there.

Refs: `known-issues.yaml:5244` notes, M-2.

### D-915: How does the governance fixture stop pinning the live instruction files?

**I recommend A: the fixture rebinds its own copy of the pins and copies any new link target, and one test keeps checking the tracked pins.** The copy still holds the live files, so the size caps, the rule checks and the routing census keep running on real bytes, and Sessions 79, 83 and 87 rely on that census. A new test proves a wrong pin is still refused in the copy. A second new test, `test_ac_14`, compares the tracked `rule-preservation.md` pins with the live `AGENTS.md` and `GUARDRAILS.md`. After a governance edit you get one red instead of four, and its message prints the rebind command.

This touches your D-132 ruling ("Update pin, commit+push (Recommended)", 2026-10-27), so it is listed as M-6. It keeps that ruling's point: rule-map drift stays visible, and you still rebind by hand. It is not M-11, because no blocking check is waived: `test_ac_14` runs in `py-tests` on the real tree. A can fail if a future verifier check reads another frozen record; that is S5. Undo: revert the helper and the two tests.

- B: a fully synthetic governance tree. It is fully hermetic, but it drops the census over live bytes that three sibling sessions rely on.
- C: rebind the pins in every case, with no tracked-pin test. That removes the last check of the tracked rule map, which D-132 wanted kept.
- D: keep things as they are, with D-132's hand rebind and four reds per edit.

Refs: `known-issues.yaml:859`, D-132 (`docs/execution/reflections/2026-10-26-tts-sideload-load-reflection.md:116`, `c34866b`), `VERIFIER` `governance_inventory`, AC-6 to AC-9, AC-14, M-6, M-11.

## Research References

- `P:/.agent/tools/resolve_model.py` and `ModelRegistry.psm1`, read only, as they stand at plan time. They are primary for the resolution order: the resolver reads an explicit `AGENT_MODEL_REGISTRY` first and otherwise the registry next to itself, and never reads `AGENT_MODEL_REGISTRY_HOME`; the wrapper uses `AGENT_MODEL_REGISTRY_HOME` only when `AGENT_MODEL_REGISTRY` is unset; the whole overlay is validated on each resolve, and the Python path does not check the compiled stamp.
- `P:/agentic-framework` `core/.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1` log (`C:/Temp/av-kit/tth/up-clidispatch-log.txt`). Primary; upstream has no fix.
- `VERIFIER` `static()` (`:150-191`) and `governance_inventory()` (`:206+`). Primary for which checks read frozen records.
- `.agent/context/known-issues.yaml` `:33`, `:859` and `:5244`.

## Planning receipts

All of these are under `C:/Temp/av-kit/tth/`. Every probe was read-only with respect to the repository, and none of the receipts is tracked.

- **`probe_home.py` / `probe-home.txt`:** a temp home with a copy of the live registry, a temp project and a wrapper copy with `NEEDLE` replaced (count 1). They show the mechanism works: compile, all bindings, vendor cases, the unsupported harness and all three wrapper faults.
- **`probe_synthetic.py` / `probe-synth.txt`:** the same with a synthetic registry (the six keys, eight slugs, one global class). Every case passed.
- **`probe_mincap.py` / `probe-mincap.txt`:** capabilities cut to the contract tokens; 3804 bytes; every case passed.
- **`probe-red.txt`, `probe-red2.txt`:**
  - The Python resolver does not check the stamp.
  - A registry minus `cursor-grok-4.6` makes every resolve fail with `unknown_slug`, and the wrapper fail with `overlay_not_validated`.
  - That makes it the Red for `HOSTILE`.
- **`probe_migrated.py` / `probe-migrated.txt`:**
  - `VERIFIER static` exits 0 on today's migrated tree, and both pins match the live bytes.
  - No instruction backlink leaves the manifest.
  - 11 files under the census prefixes are not in the manifest.
- **`up-clidispatch-log.txt`:** the upstream log for the dispatch test.
- **`probe-strict/`, `probe-strict.txt`, `probe-strict-neg.txt`, `probe-strict-neg2.txt`:** `validate --registry <copy> --strict` on a copy of the 3804-byte fixture shape exits 0 with `strict=yes compiled=unchecked`, and the copy is unchanged. A copy without one entry's `vendor` exits 1, and so does one whose coordinator binding slug is `invented`.
- **Line endings:** Python byte counts, as in §Single-statement contracts.
- **Not run at plan time:** any test suite, any edit, any plan-local checker.

## Validation stage contract

- **Static:** `tools-lint`, `py-lint`, `task-contract`, `scope-paths`, `fixture-check`, `hermetic-check`, `dispatch-source`, `red-check-selftest`.
- **Targeted:** the adoption file (normally and under `HOSTILE`) and the dispatch tests.
- **Fresh full:** `py-tests`, `state-render`, `issues-render`, `closeout-selftest`.
- **Runtime:** `live-probe` (AC-12), against the real machine registry.
- **Identity:** `identity.py`, independent of the receipts. It hashes `HEAD`, plus the content of the tracked diff and the untracked files, minus this session's closeout artifacts. Other sessions' uncommitted files are therefore bound by content.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
