# Subagent Delegation — Verification Log

> Adopters: record the resolved-driver live smoke and builder write-route probe here.
> A `[B]` is never a pass. Directory presence is NOT a detection signal — resolve the
> driver via `harness-profiles.md` + `.agent/context/harness.local.md`, then prove the
> assistant-addressable worker route.

## Resolved Driver Probe — Claude Code (2026-09-02)

resolved_driver: Claude Code
harness_version: Claude Code (Opus 5 coordinator session, 2026-09-02)
model_rung: coordinator Opus 5 · builder `.claude/agents/av-kit-builder.md` (`model: sonnet`) · verifier `.claude/agents/av-kit-verifier.md` (`model: sonnet`)
readonly_result: **pass**
write_route_result: **pass**
probe_status: **complete**

**Resolution basis (not directory presence):** the Claude Code row of
`.agent/docs/harness-profiles.md` resolves `fresh_worker` to "Agent/Task tool +
`.claude/agents/`". Both agent definitions are installed at
`.claude/agents/av-kit-builder.md` and `.claude/agents/av-kit-verifier.md`, and both were
dispatched live in this session — the route is assistant-addressable, not inferred.

**Verifier probe evidence (readonly):** dispatched `av-kit-verifier` to run the UI unit
suite and report counts only. The subagent ran the command, honoured the redirect-to-file
contract, edited nothing, and returned compact counts plus the receipt path — the readonly
route is proven end to end. Receipt: `C:/Temp/av-kit/probe-verifier-vitest.txt`.

> **Probe finding — the route passed, the command it was handed did not.** The verifier
> reported 17 files / 67 tests failed, exit 1. Coordinator re-ran the suite from `ui/`:
> **43 files / 366 tests passed, exit 0** (`C:/Temp/av-kit/probe-vitest-correct.txt`). The
> failures were an invocation artifact: `npx --prefix ui vitest run` only redirects npm's
> binary lookup, leaving process cwd at the repo root, so vitest resolves its own root to
> `P:/av-kit`, ignores `ui/vitest.config`, and sweeps in `ui/tests/e2e/*` Playwright specs
> and an archived copy under `.agent/context/isolated/`. Reproduced from the repo root:
> `npx --prefix ui vitest run` → exit 1 (`probe-vitest-prefix.txt`);
> `npm --prefix ui run test` → exit 0, 366 passed (`probe-vitest-npmrun.txt`).
> **Canonical form is `npm --prefix ui run test`** — `npm run` sets cwd to the package
> directory, and the script carries `--allowOnly=false`, which G36 requires.

**Builder write-route probe:** dispatched `av-kit-builder` with the correction that finding
produced — replace `npx --prefix ui vitest run` with `npm --prefix ui run test` across the
p10-queue-card-migration plan artifacts (13 occurrences in `task.md`, 1 in
`implementation-plan.md`), leaving the `npx --prefix ui playwright test` occurrence alone.
The subagent made the edit with `sed`, self-verified the counts, and reported a diff.
Coordinator independently confirmed: 0 remaining broken forms, 13 + 1 corrected, Playwright
occurrence intact, and all 13 edited task rows still carry identical column counts. The
write route is proven on real work, not a throwaway file.

## Resolved Driver Probe — Cursor (2026-09-11)

resolved_driver: Cursor
harness_version: Cursor IDE (Grok coordinator session, 2026-09-11)
model_rung: coordinator Cursor Grok · builder dispatched at `cursor-grok-4.6-xhigh` · verifier dispatched at `composer-2.5-fast`
readonly_result: **fail (infra)**
write_route_result: **pass**
probe_status: **incomplete — `fresh_worker` stays `none` for Cursor**

**Resolution basis (not directory presence):** Cursor `Task` tool lists subtypes; agent defs live at `.cursor/agents/av-kit-builder.md` and `av-kit-verifier.md`. `PROJECT-PROFILE.md` A6 = enable after smoke. `.agent/context/harness.local.md` keeps `fresh_worker: none` until this log has **both** receipts.

**Model-pin substitution, recorded rather than silently applied:** at probe time the pin named
in `harness.local.md` was `cursor-grok-4.6-high`, which is **not an available slug in this
harness**. The builder was dispatched at `cursor-grok-4.6-xhigh`, the nearest available 4.6
rung; the verifier ran at its registered pin, `composer-2.5-fast`. The stale slug was
corrected repo-wide to `cursor-grok-4.6-xhigh` later the same day (human direction), so this
paragraph records the substitution as it stood during the probe, not a live discrepancy.

**Verifier probe evidence (readonly): FAIL — infrastructure, not a route defect and not a
test failure.** `av-kit-verifier` was dispatched to run `npm --prefix ui run test` and report
counts only. The dispatch itself worked — the subagent received the task and formulated the
canonical command — but **the shell never spawned**, twice (with and without `rtk proxy`):

```
Terminal unavailable: this machine cannot enforce the 'workspace_readonly' sandbox policy
this command requires, because no working sandbox backend is available (Windows sandbox
helper only provides network proxy, not filesystem isolation). This is not a permission
denial.
```

No receipt was produced — `C:/Temp/av-kit/probe-cursor-verifier-vitest.txt` does not exist,
and no vitest count was observed. **This is not a `[B]` dressed as a pass:** the readonly
worker route is unusable on this Windows host as configured, so every `task.md` row carrying
`delegate_to: av-kit-verifier` must run on the coordinator under `compact_continue` until a
sandbox backend exists. Note the asymmetry — the *writable* builder route runs fine, because
it requires no sandbox policy; only the readonly policy has no Windows backend.

**Builder write-route probe: PASS, on real work.** `av-kit-builder` was dispatched to extract
the sole `isCompactSummary` record (line 6971) from an 18.05 MB Claude Code session JSONL and
write it verbatim to
`docs/execution/plans/2026-09-03-p10-queue-card-dnd/session-22-compaction-summary.md` — a real
deliverable in the session-22 takeover packet, not a throwaway file. The subagent wrote a
Python script under `C:/Temp/av-kit/` (per the standing no-heredoc rule for unicode/backslash
content), honoured the redirect contract, self-verified, and reported an honest marker
mismatch rather than papering over it (the spec's `9. Optional Next Step` appears in the
source as `9. **Optional Next Step:**`).

Coordinator independently confirmed rather than accepting the report: body length **17,267**
chars matching the source exactly, **byte-identical** to the JSONL string under a
case-sensitive ordinal comparison (`$body -ceq $src`), 148 total lines, all three content
markers present, exactly one added path in `git status --porcelain`, zero tracked files
modified, and no scratch script left in the repo tree. Receipts:
`C:/Temp/av-kit/probe-cursor-builder-extract.txt`,
`probe-cursor-builder-verify.txt`, `coord-verify-builder-probe.txt`.

> **Verdict: the flag does not flip.** The note in `harness.local.md` requires a live
> readonly-verifier smoke **and** a builder write-route receipt; one of the two failed, and a
> half-satisfied condition is not a pass. `fresh_worker: none` stands for the Cursor driver.
> The Claude Code probes above do not substitute for it.

## Pending Probe (non-resolved harness)

harness: none
status: n/a
