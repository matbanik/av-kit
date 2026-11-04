# Round 2 correction notes — blast-radius census

Raw `rg -F -n` output over the plan folder's six plan files, then one disposition per hit.

```text
=== rg -F -n ""docs/build-plan","
--- rg exit 1
=== rg -F -n ".agent/context/grouping "
--- rg exit 1
=== rg -F -n "docs/build-plan docs"
--- rg exit 1
=== rg -F -n "D-1/D-2/D-3/D-5"
--- rg exit 1
=== rg -F -n "steps'][3]"
--- rg exit 1
=== rg -F -n "asset=SPACY_MODEL"
--- rg exit 1
=== rg -F -n "With `SPACY_MODEL` missing"
--- rg exit 1
=== rg -F -n "spacy.util.is_package(SPACY_MODEL)"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:122:| `SPACY_INSTALL_DIR` | `{tts.models_directory}/spacy/en_core_web_sm-3.8.0/`. This is the wheel's contents extracted as-is, including `.dist-info`, so
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:123:| `SPACY_READY` | After `activate_spacy_dir(settings)`: `spacy.util.is_package(SPACY_MODEL)` **and** `importlib.util.find_spec(SPACY_MODEL) is not Non
--- rg exit 0
=== rg -F -n "went out with the plan"
--- rg exit 1
=== rg -F -n "GATED_PATHS"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:132:| `GATED_PATHS` | The executable copy is the `gated` list in `validate-task.sh` `windows-gate-check`, and `plan_checks.py static` asserts it equals th
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:474:- code identity over `GATED_PATHS`.
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:623:| F6 Medium (`GATED_PATHS` gap) | `GATED_PATHS` now adds `openapi.committed.json`, `docs/BUILD_PLAN.md`, `docs/build-plan`, `.agent/model-registry.loc
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:625:| F8 Low (restated clusters) | The stage order is canonical in the `.sh`, and `TTS_LIVE_STEPS` in `tts_live_check.STEP_IDS` (imported by the `.sh`). `
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:659:- Any commit touching `GATED_PATHS` after the tested SHA reopens the gate (cloud-local §3.4).
docs/execution/plans/2026-09-30-tts-repair/tts_live_check.py:17:``GATED_PATHS``.
docs/execution/plans/2026-09-30-tts-repair/task.md:33:- **Named sets:** `TEST_AMENDMENTS`, `ENV_BOUND_*`, `GATED_PATHS` and `COUNT_FLOORS` are defined once, in `implementation-plan.md` §Single-statement contracts.
docs/execution/plans/2026-09-30-tts-repair/task.md:59:| H1-7 | Dispatch `/execution-critical-review` to the user-directed Fable 5.1 subagent ([human-review-decision.md](human-review-decision.md)). Correct and re-dispatch
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:621:# GATED_PATHS (implementation-plan.md §Single-statement contracts); plan_checks.py asserts equality.
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:630:    sys.exit(f"FAIL: GATED_PATHS changed since Windows-tested commit {tested} (git diff exit {code})")
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:634:    sys.exit(f"FAIL: uncommitted GATED_PATHS changes after the Windows-tested commit:\n{dirty}")
--- rg exit 0
```

| Sweep | Hit | Disposition |
|---|---|---|
| old wide `gated` entries (`"docs/build-plan",`, `.agent/context/grouping `, `docs/build-plan docs`) | — (exit 1) | confirmed-consistent: the widened list is gone from the plan and the `.sh`; `plan_checks.py static` PASS asserts they are equal |
| `D-1/D-2/D-3/D-5` | — (exit 1) | confirmed-consistent: H2-1 now names grouping D-1 to D-7 |
| `steps'][3]` | — (exit 1) | confirmed-consistent (R2-8) |
| `asset=SPACY_MODEL`, "With `SPACY_MODEL` missing" | — (exit 1) | confirmed-consistent: the enum member is qualified as `TtsAsset.SPACY_MODEL` (R2-6) |
| `spacy.util.is_package(SPACY_MODEL)` | plan:122 | confirmed-consistent: `SPACY_INSTALL_DIR` explains how name resolution works; readiness is defined only at plan:123 |
| | plan:123 | **updated**: `SPACY_READY` now = `is_package ∧ find_spec` (R2-2) |
| "went out with the plan" | — (exit 1) | confirmed-consistent: row 1 says R1–R5 are re-sent with the approved-plan message (R2-7) |
| `GATED_PATHS` | plan:132 | **updated** (R2-3), with the narrowed list and the stated SSOT rule |
| | plan:474, :659; task:33, :59; tts_live_check:17; sh:621, :630, :634 | confirmed-consistent: references by name |
| | plan:623 (Round 1 F6 log row) | confirmed-consistent as history. The "Round 2 Correction Notes" section records that R2-3 supersedes it. |

Blast-radius census: 8 notes applied, 10 sweeps, 14 hit lines; 2 updated, 12 confirmed consistent.
