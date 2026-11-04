# Human gate decision: execution authorization and gate location

## Direct user authorization

Source: `USER_EXPLICIT`, Claude Code web session, 2026-09-29.

**1. Execution message.** The user wrote:

> check if we can execute now since 25 has finished and I'm good with your recommendations

This accepts every ✅ recommendation in `implementation-plan.md` §Open Questions, which are recorded as `Human-approved`:

- **OQ-1 A:** run after Session 25. Session 25 is now approved on `origin/main` (`9c9557a`), merged here as `1f9b035`. `SEQUENCING_GATE` passes (`p11cs-seqgate-0929.txt`: `PASS MEU STATE: 9 MEU expectations hold`).
- **OQ-2 A:** Capture tools are disabled when no shot is selected.
- **OQ-3 A:** the Capture Settings disclosure starts closed.
- **OQ-4:** `TEST_MIGRATIONS` TM-1..TM-10 are approved as listed.
- **OQ-5:** the Windows host, refined by answer 2 below.

**2. Execution host.** The user answered the follow-up question "Where should Session 26 run?" with:

> Split like Session 25 (Recommended)

The option text presented to the user:

> I write the code and tests here and run a container pre-gate. Two known environment-only Vitest failures (AC-51.6 CRLF hash, AC-41.3 P: path) are tolerated only with their proven signatures. You then run one authoritative Phase 11 exit gate script on Windows (UI + Python + MCP + full Electron) and push its result JSON, and then the Fable execution review runs. I'd record this as a plan amendment, the way Session 25 did in human-gate-decision.md.

## What this authorizes

- **Execution in this container:** rows 1–8 and H1-1 to H1-5, as amended in `implementation-plan.md` §Execution amendments — 2026-09-29.
- **`WINDOWS_GATE`:** the authoritative Phase 11 exit gate. It is the full PROFILE D6 set: UI, harness build, full Electron, Python, MCP, OpenAPI check, state render and source audit. Mat runs it on Windows with `validate-task.ps1 -Check windows-gate`, and it tolerates zero failures. The container pre-gate is non-authoritative.
- **Push and pause:** pushing `claude/quirky-gates-o1lql2` so Mat can test that commit. Mat's commit of `windows-gate-result.json` is part of this decision. H1-6 is a planned turn boundary: the run pauses until the result is pushed.

This decision does not authorize merge, release or deploy, and it does not change the assertions of any test outside TM-1..TM-12 (TM-11 and TM-12 were added below).

## Phase-gate follow-up: pre-existing pyright error (A8)

Source: `USER_EXPLICIT`, 2026-09-29. The question asked about the pre-existing `py-types` failure at `packages/api/src/avkit_api/routes/captures.py:78`, which comes from `6b40b4d` (MEU-60) and is untouched by this session. The user answered:

> Fix it here (Recommended)

The option text:

> One-line typing-only change: build CaptureShotDetailOut with model_validate({...base.model_dump(), 'annotations': annotations_to_wire(...)}). Same runtime validation and payload; no API/OpenAPI change (I'll run the OpenAPI --check and the capture API tests to prove it). Recorded as a human-approved scope exception to API_SCOPE_PATHS so the Phase 11 exit gate can go green.

This authorizes that single typing-only edit as a scoped exception to `API_SCOPE_PATHS`. Any other `packages/` or `mcp-server/` change is still out of scope.

## Census follow-up: TM-11 and TM-12

Source: `USER_EXPLICIT`, 2026-09-29. The row-2 `MIGRATION_CENSUS` found two contradictions that were not listed. The user answered the stop-rule question with:

> Approve TM-11 + TM-12 (Recommended)

- **TM-11:** `capture-page.behavior.test.ts:387–410` (AC-59.7). Draw one mark first so `capture-save` mounts (CP1), then inject the malformed seam selection. The no-POST and error-status assertions are unchanged.
- **TM-12:** `capture-page.behavior.test.ts:336–348` (AC-39.28). Select a shot first (`openSelectedSurface`) before the tool assertions (CP5 / OQ-2). The Capture region `h-9` and `bg-accent` checks are unchanged. TM-10 still applies to the tool size class.
- **Conditional setup:** the same answer covers a TM-4 disclosure-toggle click in the unit suites (`:320–327`, `:785`), but only if jsdom blocks interaction with the collapsed panel. This is setup only.

## WINDOWS_GATE attempt 1 follow-up: sibling-repo drift (A11)

Source: `USER_EXPLICIT`, 2026-09-29. `WINDOWS_GATE` attempt 1 (`47efbff`, tested commit `2a7eacc`) failed py-tests at `tests/tooling/test_framework_adoption.py::test_verifier_bootstrap_accepts_captured_bytes` with `REFUSE: source revision drift`. The test pins `P:/agentic-framework` at `003929c`, and that repo is now at `fa7f8d4` with one untracked file (walkthrough §WINDOWS_GATE attempt 1). The user was offered four options: (a) put the sibling repo back on the pinned commit, (b) make the tests self-contained with a throwaway git repo fixture, (c) update the pinned SHA, (d) skip. They answered:

> Give me message for local agent for B

That selects option **(b)**, carried out by Mat's local agent on Windows. It authorizes this test-input change as a scoped exception, recorded as amendment A11:

- **Allowed file:** `tests/tooling/test_framework_adoption.py`, nothing else.
- **Allowed change:** `SOURCE` and `SHA` come from a fixture that `git init`s a throwaway repo under pytest's temp dir, commits one file, and returns the repo path and its `HEAD`. The dependent fixtures and the `verify()` helper use those values.
- **Unchanged:** test names, parametrize IDs, and every assertion and expected outcome. `verify_adoption.py` is not changed, and `P:/agentic-framework` is not touched.

This does not authorize any other test-expectation change, or merge, release or deploy.

## A11 widening: the `migrated_tree` fixture

Source: `USER_EXPLICIT`, 2026-09-29. Mat answered the local agent in the local-agent chat, and relayed this to the cloud session in the Session 26 report message: "Mat chose 'go with your recommendation' … widen A11 to the `migrated_tree` fixture."

The local agent found the narrow A11 change insufficient. `verify_adoption.py` `source_state()` also checks the digest of every manifest `source_path` in the source repo, and `migrated_tree` copies the real `adoption-manifest.json` (68 such entries). The prototype gave 87 passed, 4 failed (`REFUSE: source file drift: core/.agent/INSTANTIATE.md`). The local agent stopped and offered options. Mat approved widening A11 to cover:

- **`migrated_tree`:** in its copy of the manifest, it commits a file at each `source_path` in the fixture source repo (content = the path string) and rewrites that entry's `source_sha256` to match. The fixture repo's `HEAD` becomes `source_sha`.
- **Approval-mode manifest:** it uses the placeholder `"f"*40`, because approval mode never reads the source.

These constraints are unchanged, and the cloud agent verified them independently against `4047bfc`:

- Only `tests/tooling/test_framework_adoption.py` changes.
- Test names, parametrize IDs and assertions are identical.
- No skip, xfail or marks are added.
- `verify_adoption.py` and `P:/agentic-framework` are untouched.

Recorded as plan amendment A11-W (commit `7613beb`).

## WINDOWS_GATE attempt 3 follow-up: AC-49.26 drag race (A12)

Source: `USER_EXPLICIT`, 2026-09-29, Claude Code web session. The question:

> AC-49.26 (the MEU-49 download-queue drag test) fails about 1 run in 5 on Windows and passes 15/15 here. How should Session 26 handle it before WINDOWS_GATE attempt 4?

The user answered:

> Harden helpers (Recommended)

The option text:

> I change only the drag helpers grabRow/dragOver in download-queue.test.ts, leaving every assertion as it is. grabRow waits for the handle's position to stop moving, then waits for dnd-kit's aria-pressed="true" (the drag really started). dragOver waits for the row animations to finish, then re-aims at the target's settled center. Recorded as A12. Mat's local agent then runs AC-49.25–28 with --repeat-each=20 on Windows, and runs attempt 4 only if that's 20/20.

This authorizes changing only those two helpers in `ui/tests/e2e/download-queue.test.ts`. No assertion, test body, test name or product file may change.

## A12 repeat-check follow-up: AC-49.27 keyboard drag cancelled (A13)

Source: `USER_EXPLICIT`, 2026-09-29, Claude Code web session. The question:

> AC-49.27 (keyboard drag) failed 1 in 100 on Windows with "was cancelled". dnd-kit cancels a drag on a window resize, and the app's window resizes once right after launch (1280x800 → 1280x773, confirmed with a probe). If that resize lands late, after the pickup, the drag is cancelled. How should I handle it?

The user answered:

> Add window-settle wait (Recommended)

The option text:

> Recorded as A13. A shared helper, windowSettled(page), waits until document.visibilityState is 'visible' and no resize has fired for 300 ms. Two call sites: one new setup line in AC-49.27 before the handle is focused, and a call at the start of grabRow (the pointer sensor cancels on resize too). No assertion changes. Then the local agent repeats AC-49.25–28 and W1-14 twenty times each before attempt 4.

Implementation note: the quiet window is 500 ms rather than the 300 ms in the option text. It is a stricter wait of the same kind, and it asserts nothing. This authorizes only the helper and those two call sites in `ui/tests/e2e/download-queue.test.ts`.

## WINDOWS_GATE attempt 4 follow-up: `test_ac_12_7` race (A14)

Source: `USER_EXPLICIT`, 2026-09-29, Claude Code web session. The question:

> test_ac_12_7 (tests/unit/test_services.py) failed attempt 4 with 0 conflicts. I reproduced it here by delaying one contender 0.5 s: the test releases the held download before the second thread has called download(), so both calls succeed. The service's lock is correct. How should I handle it?

The user answered:

> Reorder test (Recommended)

The option text:

> Recorded as A14. In the contention half of test_ac_12_7 only, join both contender threads before catalog.release.set(). download() returns immediately while the catalog is held, so the second caller always sees 'Downloading' and gets ConflictError. No assertion changes, and no product change. The scratch probe with a late contender gives ['a-ok','b-conflict']. Then the local agent repeat-runs it on Windows (pytest --count or a 50× loop) before attempt 5.

This authorizes only that reordering (plus one comment) in `tests/unit/test_services.py::test_ac_12_7_immediate_return_fraction_and_lock`.

## WINDOWS_GATE attempt 5 follow-up: AC-49.25 stale `over` (A16)

Source: `USER_EXPLICIT`, 2026-09-29, Claude Code web session. The question:

> AC-49.25 failed attempt 5 one row short (PUT [dl-2, dl-1, dl-3, dl-4]). Root cause, reproduced here: dnd-kit commits the row under the pointer two React renders after the last pointer move, and the drop reads whatever is committed. If the release arrives first (under load on Windows), the drop uses the previous row. A probe that releases in the same task as the final move gives exactly that body, 3/3. How should I fix it?

The user answered:

> Wait for committed over (Recommended)

The option text:

> Recorded as A16. At the end of the dragOver helper only, wait until dnd-kit's live region says "moved to position N of M" for the target row (N is the target's position before the drag). That text is emitted only after the over is committed, so mouse.up then always drops on the target. No assertion, test body or product change. Callers: AC-49.25, 26 and 28. Then a Windows repeat check, then attempt 6.

This authorizes only that wait, plus the pre-drag position lookup it needs, inside `dragOver` in `ui/tests/e2e/download-queue.test.ts`.

## WINDOWS_GATE attempt 6 follow-up: stale registry overlay (A17)

Source: `USER_EXPLICIT`, 2026-09-30, Claude Code web session. The question:

> Attempt 6 failed because P:/.agent/model-registry.json changed (your zorivest gpt-6.1 bump), so av-kit's tracked overlay (.agent/model-registry.local.json, validated_against 7e85d6f3…) is now stale. The resolver refuses it, which is by design. How should Session 26 handle this?

The user answered:

> Revalidate overlay (Recommended)

The option text:

> Recorded as A17. The local agent revalidates av-kit's overlay against the current P:/.agent registry using the resolver's project-scoped validate/compile, not a global sync. It may change only .agent/model-registry.local.json, and only its validated_against hash. If any binding or class changes, it stops and reports. It commits that, reruns the full Python suite without -x, then runs gate attempt 7. Decoupling these tests from the shared P:/.agent is filed as a follow-up, not done here.

This authorizes that one field change, made on Mat's Windows host by the local agent. It does not authorize writing to `P:/.agent`, a global `sync`, any binding change, or any change to the tests. Follow-up: `TOOLING-SHARED-REGISTRY-COUPLING` in `.agent/context/known-issues.yaml`.
