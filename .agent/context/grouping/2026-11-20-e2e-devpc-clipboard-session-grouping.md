# 2026-11-20 Dev-PC clipboard writers · Session grouping

> **Source:** the second 2026-11-20 issue triage of `.agent/context/known-issues.yaml` (12 issues open or mitigated at the start, plus one new; all in the §1 traceability table) and Mat's requests "run triage and create new session grouping based on what is of most value to the application" (2026-11-17) and "continue with next prompt" (2026-11-20), after Session 98 was committed as `e8207e1`.
> **Generated:** 2026-11-20
> **Method:**
> - Triage (`.agent/workflows/issue-triage.md`): `discover --dry-run` found 0 candidates, and `verify --deep` found nothing before or after the edits (`C:/Temp/av-kit/triage-1120b/discover-dry.txt`, `verify-deep-before.txt`, `verify-deep-after.txt`). Every issue was rechecked against Session 98's four full runs (two mini-air main stages and two dev-PC runs, 237 of 237 each, flaky 0) and its two gated stages (outcome `run`, 2 of 2). D-1299 to D-1301 are stage `triage` entries in their issues' `decision_log`, written through `tools/issue_triage/model.py` (`classify.py`). `bucket` proposed no batch. `triage --output` rewrote `triage-output.yaml`, and `render --check` is OK.
> - Recheck of the new issue: a search of `ui/tests/e2e` for copy-button test ids, not only for `clipboard.` calls, found four dev-PC clipboard writers where Session 98 (D-1277) named two. Two of them copy the MCP config, whose JSON holds the test app's `AVKIT_API_TOKEN` (`ui/src/main/ipc.ts:419`, `ui/src/main/index.ts:411`).
> - Value sweep: `meu_status next` reads no pending MEU (`meu-next.txt`). Session 99 (`help-quick-start`, MEU-162) is being planned by another session and is not part of this grouping.
> - Stage A: skipped. Session 100 changes test files and test tooling only, as Sessions 91, 96 and 98 did.
> - Stage B: one session (D-1302).
> **Origin:** the first 2026-11-20 grouping is fully executed (Session 98 `e8207e1`).
> **Status:** Active. This is a reversible draft, not a gate. Mat asked the coordinator to continue with the next prompt; it plans and executes Session 100 and commits it without a push.
> **Parallel work:** only the `main` worktree exists, at `e8207e1`. Another session (`av-kit-b3`) is planning Session 99 `help-quick-start` (MEU-162, AC-162.1 to AC-162.16, decisions D-1289 to D-1298, more from D-1350 if needed) in the untracked `docs/execution/plans/2026-11-20-help-quick-start/`. That folder is foreign: never read, bound or committed here. This grouping claims D-1299 to D-1349, Session 100 and no MEU. Both sessions write `current-focus.md`, `docs/execution/metrics.md` and possibly `.agent/docs/commands.md`; each re-reads those just before its write and commits exact paths only.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (issue) | Layer | Depends on |
|-----|------|----------------|-------|------------|
| — (no MEU) | `e2e-devpc-clipboard` | `E2E-DEVPC-CLIPBOARD-SPECS`; watch item `E2E-CLIPBOARD-PRIMER-EMPTY` | test files: `console-chrome.test.ts`, `mcp-setup-prompt.test.ts`, `settings.test.ts`, the gated clipboard file(s), the launch helper `electron-app.ts`; test tooling: the gated entry in `tools/e2e_host/known-failures.json` if a file is added, its pin, the run book and the dev-PC flake runner | Session 98's gated stage and session probe |

No build-plan home: no product behaviour changes, as for Sessions 91, 96 and 98.

Issue → disposition traceability (every issue open or mitigated at the start of this pass, 12 in all, plus the new one):

| Issue | Status · category | Disposition |
|-------|-------------------|-------------|
| `E2E-DEVPC-CLIPBOARD-SPECS` | open · TECH-DEBT P3 (was low P4) | Session 100, no MEU (D-1299): corrected to four tests, C1-5, AC-71.15 (b), AC-71.15 (d) and W4-3 |
| `E2E-CLIPBOARD-PRIMER-EMPTY` | open · MONITORING P4 | Watch item of Session 100 (D-1301): closes after five gated `run` outcomes with 2 of 2 and no primer failure, counted from `r20261120T215925Z-9ac9adc`; two so far |
| `TOOLING-RUFF-TOOLS-UNCLEAN` | open · TECH-DEBT P4 (new) | Not grouped (D-1300): 10 ruff errors and 15 unformatted files in `tools/`, outside CI's lint scope; fixed by the next session that changes those tools |
| `CAPTURE-TEXT-PLATE-METRICS-RESIDUAL` | open · TECH-DEBT P4 | Not grouped (D-1260): preview only; AC-161.5 pins the limits |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | open · MONITORING P4 | Not grouped (D-1263): four more clean full runs in Session 98 |
| `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | open · MONITORING P4 | Not grouped (D-1264): W2-4 passed in Session 98's four full runs |
| `TRANSCRIPT-ADD-CHANNEL-422` | open · MONITORING P4 | Not grouped: not seen again |
| `CAPTURE-JOURNAL-VOLATILE` | open · DEFER P4 | Not grouped: deferred by its own ruling |
| `TTS-JA-ZH-G2P-EXTRAS` | open · DEFER P4 | Not grouped: deferred by its own ruling (D-229) |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | open · BLOCKED P3 | Not grouped: eSpeak NG is still absent from the dev PC (D-230; Mat's install) |
| `FFMPEG-LIBDVDCSS-BUNDLED` | open · CLOSE P2 | Not grouped: an accepted risk (D-266) |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | mitigated · UPSTREAM P3 | Not grouped: anthropics/claude-code#98256 still open, updated 2026-11-20 (D-232) |
| `TOOLING-SHARED-REGISTRY-COUPLING` | mitigated · TECH-DEBT P2 | Not grouped: rides the next change to that file (D-912) |

Items that stay Mat's (none is needed for Session 100): D-1200 (the FFmpeg upstream report, M-12), and D-1216's host items (Smart App Control, auto sign-in, a GitHub runner) and RustDesk's own settings on the mini-air.

---

## 2. Dependency graph + critical path

```
Session 96 (e2e-remote-host) ──► Session 98 (e2e-clipboard-specs, gated stage) ──► Session 100 (e2e-devpc-clipboard)
Session 99 (help-quick-start, MEU-162, another session) ── independent; shares only closeout files
```

**Critical path:** Session 100 alone. Its acceptance includes a mini-air run through Session 98's gated stage.

**Shared files:** `known-issues.yaml`, `current-focus.md`, `docs/execution/metrics.md`, and this grouping's §6 row. Session 99 writes the second and third at its own closeout.

**Shared hosts:** the dev PC runs both sessions' E2E work, so each full run waits for the load probe (50 % or less). The mini-air keeps one lock, and the tooling refuses a busy host.

---

## 3. Recommended grouping — 1 session (100)

### Session 100 — `e2e-devpc-clipboard` (no MEU) · P3

- **Layer / files:**
  - `ui/tests/e2e/console-chrome.test.ts` (C1-5), `mcp-setup-prompt.test.ts` (AC-71.15 (b) and (d)) and `settings.test.ts` (W4-3): the steps that write and read the system clipboard move into the gated stage with their assertions unchanged; the rest of each test stays where it is (D-1303). AC-71.15 (e) needs the token that (d) copies, so the plan names how (e) gets it without the clipboard.
  - The gated file: either `capture-system-clipboard.test.ts` gains the moved blocks, or a second gated file joins it and `tools/e2e_host/known-failures.json`'s `gated` list, `run-e2e.ps1`'s gated stage and `test_ac_11_known_tracked_list` change with a named pin. The plan picks one and names every pin it touches (Session 97 RULE-1).
  - `ui/tests/e2e/electron-app.ts`, the one launch helper: a dev-PC guard (D-1304).
  - The run book `.agent/docs/e2e-remote-host.md` and `.agent/docs/commands.md` name the guard.
- **Covers:** `E2E-DEVPC-CLIPBOARD-SPECS` (D-1299). Watch item: `E2E-CLIPBOARD-PRIMER-EMPTY` (D-1301).
- **Why (value):** each dev-PC full run overwrites Mat's clipboard about four times, twice with a JSON block holding an API token, and Windows clipboard history can keep those entries. Session 98's gated stage already gives these tests a host that is not Mat's desk, so the fix is test files and tooling only, and the guard makes `CLIPBOARD_NEVER_DEVPC` true for every later spec.
- **Acceptance direction:**
  - A dev-PC full run passes with the guard on and records zero clipboard writes; the kept parts of C1-5, AC-71.15 and W4-3 still run there.
  - A test of the guard proves a clipboard write in a non-gated launch fails that test with a named message, and that the gated launch is not blocked.
  - One real mini-air run through `tools/e2e_remote.py` at the final tree: the main stage passes, and the gated stage either runs the moved tests and passes or reports its probe reason; either outcome is a receipt, and a `run` outcome counts toward D-1301's bar.
  - RULE-1 of Session 98 applies to any new observation the guard writes: missing, empty and invalid each reach a non-pass outcome.
- **Gate:** no product code. No assertion changes beyond the moves and the named pins (S3). The clipboard steps never run on the dev PC, and `AVKIT_E2E_CLIPBOARD_GATED` is never set there. RustDesk is never read beyond the session probe, changed or stopped. The home-path gate runs before and after, and no host detail enters a tracked file.
- **Cloud/local:** local, plus the mini-air.
- **Token estimate:** calibrate against Session 98 `e2e-clipboard-specs` (the same split and gated run) and Session 91 `e2e-pointer-flakes`.
- **Split flag:** yes. If the launch-helper guard cannot be proven without product code, the moves ship alone and the guard becomes a static scan of `ui/tests/e2e` for clipboard calls and copy-button test ids outside the gated files.

---

## 4. Plan-creation pathway

Mat's request continues the orchestration, so the coordinator runs plan creation for Session 100 now, followed by its Codex plan review, execution, the Codex execution review and a signed commit without a push. No session follows it in this grouping.

1. `/create-plan e2e-devpc-clipboard` → no MEU, plan folder `docs/execution/plans/2026-11-20-e2e-devpc-clipboard/` (dated the day the plan is made), decision ids from D-1305 to D-1349

---

## 5. Prerequisite gate

- **Can begin now:** Session 100. The gated stage is committed (`e8207e1`) and the mini-air is set up.
- **Not for a session:** D-1200 and D-1216's host items stay Mat's.
- Work stays on `main` only, with no branch or worktree. The coordinator commits after the execution review, with exact paths that leave Session 99's files out, and does not push.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 100 | `e2e-devpc-clipboard` | — | P3 | executed (Session 100) | `docs/execution/plans/2026-11-20-e2e-devpc-clipboard/` |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Session 100:** Session 98 `e2e-clipboard-specs`, Session 91 `e2e-pointer-flakes`.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1302 | Which work is of most value to the application now, and how many sessions follow? | autonomous | One session, Session 100 `e2e-devpc-clipboard`, P3, no MEU, carried by the coordinator through plan, execution and commit without a push. No session after it. Session 99 stays with its own session. | Local Canon | Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. Options: (A) Session 100 alone; (B) also fold the ruff cleanup of `tools/` into it; (C) do nothing and leave the register as triaged. A is the only open issue with a cause, a fix and a host ready for it. B loses because the reformat touches 15 files of a tool Session 99 is running now (D-1300). C keeps four clipboard writes, two with a token, in every dev-PC run. M items: M-8 (it adds a session). Two-way. | — |
| D-1303 | How do the four dev-PC clipboard writers stop writing Mat's clipboard? | autonomous | Move the steps that write and read the system clipboard into the gated stage on the mini-air, with their assertions unchanged, and keep the rest of each test in its file. The plan picks the existing gated file or a second one and names each pin it changes. | Local Canon | Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. Options: (A) move them into the gated stage; (B) stub the main-process clipboard under `AVKIT_E2E` in product code and assert the recorded text; (C) do nothing. A follows Session 98's `CLIPBOARD_SPLIT` and keeps every assertion on the real clipboard. B changes product code for a test and stops proving the OS clipboard. C keeps the writes. M items: none. Two-way. | — |
| D-1304 | How does `CLIPBOARD_NEVER_DEVPC` stay true for later specs? | autonomous | In every launch without `AVKIT_E2E_CLIPBOARD_GATED=1`, the launch helper `electron-app.ts` replaces the main-process clipboard writers with ones that record the call and fail the test with a named message. Test code only. If that cannot be proven, a static scan of `ui/tests/e2e` for clipboard calls and copy-button ids outside the gated files takes its place (split flag). | Local Canon | Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue with next prompt'. Options: (A) a runtime guard in the one launch helper; (B) a static scan only; (C) rely on each plan's flake-runner guard. A catches writes through any button, which is how two of the four writers were missed; B misses them; C protects only the runs that use that plan's runner. M items: M-3 (a new run rule for every E2E launch). Two-way. | — |
| D-1200 | Send FFmpeg a report on the open `-read_intervals START%` form (Session 93)? | open | | Local Canon | Carried from `2026-11-20-e2e-clipboard-specs-session-grouping.md`, unchanged: Mat's to make (M-12). | — |

Carry-forward: the closeout validator reads every §8 row of this file through `--decision-source`, so the session's reflection does not restate them. Its `### Decisions Log` lists only that session's own reversible autonomous choices (HDP §6).

- Session 100 carries D-1302, D-1303 and D-1304. Its issues' D-1299 and D-1301 are read from `known-issues.yaml`.
