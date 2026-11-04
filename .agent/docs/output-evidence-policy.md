# Output Evidence Policy — av-kit

## Canonical receipts

Use `rtk` for every shell process. Use a verified native RTK subcommand only for compact views; use `rtk proxy` for unsupported commands and exact evidence. Exact evidence includes empty output, counts, ordering, diffs, JSON/schema, authentication, exit propagation and optimization baselines. Keep every diagnostic in the unfiltered receipt.

Redirect all process streams under `C:/Temp/av-kit/`, preserve the child exit immediately, then read the completed receipt and exit with that code. Never pipe a long-running process to a filter. Resolve PowerShell as the native shell; use `pwsh` for modern child cmdlets. Set `RECEIPTS_DIR=C:/Temp/av-kit` in each execution/dispatch process, not the machine environment.

```powershell
rtk proxy uv run pytest tests/tooling/ -q *> C:/Temp/av-kit/tooling-tests.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/tooling-tests.txt -Tail 40; exit $code
```

## Commands that may skip the receipt

Only bounded read-tool observations that are not exact-evidence claims may omit a shell receipt. An empty search cited as proof, a schema result or a test count cannot use that exemption. A compact terminal tail is a view, not the canonical record.

## Durable evidence contract

Raw receipts are working data. Before review or closeout, embed actual decisive observations in the repository handoff/walkthrough as `evidence.v1` JSON. Each record names check_id, command or manual procedure, cwd, scope, phase, exit_code, result, tested_state and output. Commands need integer exits; manual observations need procedure, named observer and null exit. `not_run` needs null exit and a reason. An external blocker requires a failed command, nonzero exit and actual diagnostics. Do not put scratch-only references in output or other observation fields.

```json
{"schema_version":"evidence.v1","check_id":"example-targeted","command":"uv run pytest tests/tooling/ -q","cwd":"P:/av-kit","scope":"tooling tests","phase":"targeted","exit_code":0,"result":"pass","tested_state":"example-only-not-execution-evidence","output":"Example: replace with actual decisive output","fresh":true}
```

The example is a shape, never a completed result. Validate actual records with `rtk proxy uv run python tools/durable_evidence.py ARTIFACT`; final evidence adds `--require-full --expected-state ACTUAL_STATE`, using the same all-stream receipt form. Obtain state independently from complete code/test/config/environment/external inputs. Missing identity disables reuse. One fresh full scoped gate precedes final review; later changes invalidate affected evidence.

## Blocked rows

A `[B]` row cites `B-ROW_ID` and `follow-up [label](durable-target)`. Its artifact contains `### B-ROW_ID`, `Reason: external-error`, `missing-dependency` or `human-decision`. External/dependency blocks embed failing evidence.v1; human decisions use `Decision: [label](durable-target)`. The task linter and closeout validator share this predicate. Unfinished implementation is never a blocker.

## Validation ownership

PROFILE D6 delegates exact current commands to [commands.md](commands.md). Follow static → targeted → fresh full; later stages are not_run after a blocking failure. Python, UI and MCP are present. Real Electron tests require a built UI and cleared ELECTRON_RUN_AS_NODE. There is no universal validate_codebase.py. Product gates apply to product/shared product changes; governance adoption uses its approved scoped suite. See [verification-principles.md](verification-principles.md).
