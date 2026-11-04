# Round 1 → Round 2 blast-radius census (plan-corrections Step 5c)

- **Receipt:** raw, unfiltered sweep at `${RECEIPTS_DIR}/p11cs-census-r1.txt`, with `RECEIPTS_DIR=/tmp/claude-0/-home-user-av-kit/732d64b0-ff02-55ac-8b7c-1f17da32a6cc/scratchpad/receipts`. It holds 37 `rg -F -n` sweeps over `implementation-plan.md` and `task.md`, 164 lines, with each sweep's `rg_exit` recorded.
- **Re-sweep after fixes:** `58.12`, `hub row`, `OQ-1..OQ-4`.
- **Disposition key:** `updated` means edited in this round; `confirmed-consistent` means the hit already agreed with the new value; `stale→fixed` means the sweep found an out-of-date site and it was then corrected. Line numbers refer to the files at census time.

## Old values (expected to be gone)

| Value | Hits | Disposition |
|---|---|---|
| `TM-1..TM-4` | 0 (rg_exit 1) | Gone. Every site now says TM-1..TM-7. |
| `hub-audit` | 0 | Gone. The canon edit was removed. |
| `schemas/capture.py` | 0 | Gone; corrected to `captures.py`. |
| `useSettingsPage.ts:74` | 0 | Gone; corrected to `:67–79` / `:126–144`. |
| `mcp-server/src` | 0 | Gone; replaced by `API_SCOPE_PATHS`. |
| `rows 1–7` | 0 | Gone; now rows 1–8. |
| `Four items` | 0 | Gone; now Five items. |
| `row 5`, `rows 2`, `rows 3` | 0 | No stale row cross-references. |
| `canon text` | plan:124 | confirmed-consistent (states the canon is *not* edited) |
| `canon text` | plan:241 | **stale→fixed** ("canon label left unchanged … AC-50.4") |
| `OQ-1..OQ-4` | task:35 | **stale→fixed** (now `OQ-1..OQ-5`); re-sweep shows 0 hits |
| `9 section` | plan:124, plan:280 | confirmed-consistent (both say the label stays and why) |

## New values (every site must agree)

| Value | Sites | Disposition |
|---|---|---|
| `TM-1..TM-7` / `TM-5` / `TM-6` / `TM-7` | plan:105, 140, 177, 201, 203, 387, 406; task:37 | All updated this round and consistent. TM-5/6 → unit file row; TM-7 → E2E row; OQ-4 names TM-1..TM-7; task row 3 applies TM-1..TM-7. |
| `captures.py` | plan:131, 412 | updated |
| `flushPut` | plan:125, 412 | updated |
| `packages/api` | plan:131 | confirmed-consistent (a schema path, not a scope set) |
| `packages/api` | plan:340 | confirmed-consistent (an API subset of `API_SCOPE_PATHS`; the re-plan trigger) |
| `API_SCOPE_PATHS` | plan:138, 332, 412; task:47 | updated; task H1-4 command now uses `packages/` and `mcp-server/` |
| `597` / `≥ 95` / `COUNT_FLOORS` | plan:142, 143, 331, 410; task:45 | Updated. Defined once in `COUNT_FLOORS`. Task H1-2 passes `--min-vitest 597 --min-e2e 95` to `plan_checks.py counts`, which is the executable instance of the same named floor. |
| `--new-file` | plan:300, 408; task:37, 40 | updated; the flag is present in both Red rows |
| `DOC_READING_TESTS` / `post-review` | plan:142, 144, 145, 280, 281, 338, 407, 410; task:46 (H1-3), 54 (H2-2) | Updated. Task H1-3 and H2-2 run the same three tests named in the definition. |
| `1–8` | task:44 | updated; the H1-1 script checks `list('12345678')` |
| `Five items` | plan:100 | updated |
| `CAPTURE_READY_SIGNAL` / `CAPTURE_SOURCE_LOCATION` / `MIGRATION_CENSUS` / `MCP_TOKEN_TEXT` | plan:135–140, 173, 176, 230, 366, 387, 406; task:36–38 | Updated. Each is defined once in the single-statement table and referenced elsewhere. |
| `EXECUTION_HOST` / `OQ-5` | plan:68, 106, 365, 388, 409; task:35 | updated |
| `AC-58.13` | plan:234, 411; task:40 (range `58.1–58.13`) | updated |
| `row 2` / `row 6` | plan:139; task:39 | updated (`MIGRATION_CENSUS` = task row 2; row 5 now says "before row 6") |
| `58.12` (re-sweep) | plan:233, 257, 358 | confirmed-consistent (each refers to AC-58.12 itself) |

## Summary

**Blast-radius census:** 37 values and variants swept; 10 sweeps returned no hits (every old value is gone); 90 hit lines, each dispositioned in the tables above; 2 stale sites (plan:241, task:35) fixed after the sweep and re-swept to 0.

`lint_task_contract.py` passes on the corrected `task.md` (`p11cs-plan-task-lint-r2.txt`: OK, 18 rows, exit 0). `plan_checks.py self-test` passes 26 cases (`p11cs-plan-checks-selftest-r2.txt`, exit 0).
