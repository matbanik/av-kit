# 2026-11-20 Clipboard spec files · Session grouping

> **Source:** the 2026-11-20 issue triage of `.agent/context/known-issues.yaml` (11 issues open or mitigated at the start, plus one new; all in the §1 traceability table) and Mat's requests "run triage and create new session grouping based on what is of most value to the application" (2026-11-17) and "continue orchestrating the next prompt session and the session after if there is any" (2026-11-20).
> **Generated:** 2026-11-20
> **Method:**
> - Triage (`.agent/workflows/issue-triage.md`): `discover --dry-run` found 0 candidates, and `verify --deep` found nothing before or after the edits (`C:/Temp/av-kit/triage-1120/discover-dry.txt`, `verify-deep-before.txt`, `verify-deep-after.txt`). Every issue was rechecked against the evidence since the 2026-11-18 triage: the four mini-air runs through `tools/e2e_remote.py` (two at 228 of 232 with the 4 known failures that Session 97 resolved, then two at 232 of 232), Session 97's dev-PC final full run (232 ok), and the Session 95 to 97 gates and handoffs (`recheck-runs.txt`, `s95-97-handoff-scan.txt`). D-1260 to D-1264 are stage `triage` entries in their issues' `decision_log`, written through `tools/issue_triage/model.py` (`classify.py`). `bucket` proposed no batch. `triage --output` rewrote `triage-output.yaml`, and `render --check` is OK.
> - Value sweep: `meu_status next` reads no pending MEU, and the build plan's deferred and residual sections hold only locked deferrals with their blockers still in place (`meu-next.txt`, `buildplan-deferred-sweep.txt`). The one candidate with a source and a removed blocker is the clipboard spec exclusion, which the second host now makes testable (`clipboard-rustdesk-sources.txt`).
> - Stage A: skipped. Session 98 changes test files and test tooling only, as Sessions 91 and 96 did. `meu_status render --check` is green with 161 MEUs.
> - Stage B: one session (D-1265).
> **Origin:** the 2026-11-18 E2E-on-a-second-host grouping is fully executed (Session 96 `2c41c70`, Session 97 `82a0724`); `meu_status next` reads no pending MEU.
> **Status:** Active. This is a reversible draft, not a gate. Mat asked the coordinator to continue orchestrating the next session; it plans and executes Session 98 and commits it without a push.
> **Parallel work:** only the `main` worktree exists, and HEAD is `82a0724`. The highest decision ID in use before this triage was D-1259 (Session 97's execution). No Session 98 or later, no MEU-162 or later, and no D-1260 or later was claimed anywhere (`probe-dids.txt`, `probe-sessions-meus.txt`).

---

## 1. MEU / scope summary

| MEU | Slug | Covers (issue) | Layer | Depends on |
|-----|------|----------------|-------|------------|
| — (no MEU) | `e2e-clipboard-specs` | `E2E-CLIPBOARD-SPECS-UNGATED`; watch item `E2E-CLIPBOARD-PRIMER-EMPTY` | test files: the two capture spec files that mix clipboard and non-clipboard tests; test tooling: the mini-air skip list, `tools/e2e_remote.py` and its host scripts, its tests and run book | Session 96's remote-run tooling, Session 97's empty known list |

No build-plan home: no product behaviour changes, as for Sessions 91, 95 and 96.

Issue → disposition traceability (every issue open or mitigated at the start of this pass, 11 in all, plus the new one):

| Issue | Status · category | Disposition |
|-------|-------------------|-------------|
| `E2E-CLIPBOARD-SPECS-UNGATED` | open · TECH-DEBT P3 (new) | Session 98, no MEU (D-1261) |
| `E2E-CLIPBOARD-PRIMER-EMPTY` | open · MONITORING P4 | Watch item of Session 98 (D-1262): it can recur or be closed only once AC-88.12 runs again |
| `CAPTURE-TEXT-PLATE-METRICS-RESIDUAL` | open · TECH-DEBT P4 (was unclassified) | Not grouped (D-1260): preview only, and AC-161.5 pins the measured limits, so any drift fails the gate |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | open · MONITORING P4 | Not grouped (D-1263): no hang in the four mini-air runs or Session 97's runs, but it once went 23 days unseen before recurring |
| `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | open · MONITORING P4 | Not grouped (D-1264): not seen again on either host; stays a watch item as D-362 set |
| `TOOLING-SHARED-REGISTRY-COUPLING` | mitigated · TECH-DEBT P2 | Not grouped: rides the next change to that file (D-912). Session 97's final Python gate passed with no overlay error |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | mitigated · UPSTREAM P3 | Not grouped: anthropics/claude-code#98256 still open (D-232) |
| `TRANSCRIPT-ADD-CHANNEL-422` | open · MONITORING P4 | Not grouped: not seen again |
| `CAPTURE-JOURNAL-VOLATILE` | open · DEFER P4 | Not grouped: deferred by its own ruling |
| `TTS-JA-ZH-G2P-EXTRAS` | open · DEFER P4 | Not grouped: deferred by its own ruling (D-229) |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | open · BLOCKED P3 | Not grouped: eSpeak NG is still absent from the test machines (D-230; Mat's install) |
| `FFMPEG-LIBDVDCSS-BUNDLED` | open · CLOSE P2 | Not grouped: an accepted risk (D-266) |

Host decisions that stay Mat's (none is needed for Session 98):

| Item | Disposition |
|------|-------------|
| RustDesk's clipboard setting or its service on the mini-air | Mat's: a host setting (D-1216 class). Session 98 only reads whether a remote session is connected, and never changes or stops RustDesk |
| Running the clipboard tests on the dev PC | Refused by Session 57 RULE-4: Mat uses that clipboard |
| D-1200, the FFmpeg upstream report | Mat's, carried from the previous grouping |

---

## 2. Dependency graph + critical path

```
Session 96 (e2e-remote-host) ──► Session 97 (e2e-host-parity, known list empty) ──► Session 98 (e2e-clipboard-specs)
```

**Critical path:** Session 98 alone. Its acceptance includes a mini-air run through Session 96's tooling with Session 97's empty known list.

**Shared files:** `known-issues.yaml` and this grouping's §6 row.

**Shared host:** the zorivest runner on the mini-air keeps its own lock; Session 96's tooling already refuses a busy host and never stops another run.

---

## 3. Recommended grouping — 1 session (98)

### Session 98 — `e2e-clipboard-specs` (no MEU) · P3

- **Layer / files:**
  - `ui/tests/e2e/capture-filmstrip-actions.test.ts` and `ui/tests/e2e/capture-import.test.ts`: the two tests that touch the system clipboard, AC-88.12 (a)(b)(f) and AC-132.23, move into a clipboard-only spec file, with their assertions unchanged (D-1266). The other five, AC-88.12 (c) and (d)(e), AC-89.9, AC-89.15 and AC-132.22, stay where they are.
  - `tools/e2e_host/known-failures.json`: the mini-air `skip` entries name only the clipboard-only file, and `tests/tooling/test_e2e_remote.py::test_ac_11_known_tracked_list`, which pins those entries, changes in a plan row that names it.
  - `tools/e2e_remote.py` and its host scripts in `tools/e2e_host/`: a remote-session probe before and after the clipboard file runs (D-1267), its tests, and the run book `.agent/docs/e2e-remote-host.md`.
  - The dev-PC full run's exclusion (the plan-local `flake-run.py` `EXCLUDED`, copied from Session 91's plan) names only the clipboard-only file.
- **Covers:** `E2E-CLIPBOARD-SPECS-UNGATED` (D-1261). Watch item: `E2E-CLIPBOARD-PRIMER-EMPTY` (D-1262).
- **Why (value):** five tests of user-visible capture actions (the filmstrip context menu from the keyboard, menu Delete, Shift-click batch delete with a reported failure, checkbox delete, drop import) have run in no gate since Session 91, and the two clipboard tests (Copy image, Copy full path, Ctrl+V paste import) have no host at all. The fix is test files and tooling only, and the second host gives the clipboard tests a desktop that is not the one Mat works on.
- **Acceptance direction:**
  - A dev-PC full run includes the five tests and they pass; the clipboard-only file stays excluded there.
  - Tests with a fake host prove each probe outcome: no remote session (the clipboard file runs), a connected session (it is skipped with a named reason), and an undecided probe (skipped with a named reason). A session that connects during the run voids the clipboard result with a named reason (RULE-1: probe before and after).
  - One real mini-air run through `tools/e2e_remote.py` at the final tree: the five tests pass, and the clipboard file either passes or is reported skipped with the probe's reason; either outcome is a receipt.
  - If AC-88.12 runs and its primer fails, `E2E-CLIPBOARD-PRIMER-EMPTY`'s own rule applies.
- **Gate:** no product code. No assertion changes beyond the named pin (S3). RustDesk's settings and processes are never read beyond the connection probe, never changed and never stopped. The clipboard tests never run on the dev PC. The home-path gate runs before and after, and no host detail enters a tracked file.
- **Cloud/local:** local, plus the mini-air.
- **Token estimate:** calibrate against Session 96 `e2e-remote-host` (the remote-run tooling and its fake-host tests) and Session 91 `e2e-pointer-flakes` (E2E spec work under a full-run gate).
- **Split flag:** yes. If no remote-session probe can be proven on the host, the file split ships alone and the clipboard-only file stays skipped on the mini-air with its current reason.

---

## 4. Plan-creation pathway

Mat's request continues the orchestration, so the coordinator runs plan creation for Session 98 now, followed by its Codex plan review, execution, the Codex execution review and a signed commit without a push. No session follows it in this grouping.

1. `/create-plan e2e-clipboard-specs` → no MEU, plan folder `docs/execution/plans/2026-11-20-e2e-clipboard-specs/` (dated the day the plan is made), decision ids D-1268 to D-1287

---

## 5. Prerequisite gate

- **Can begin now:** Session 98. The remote-run tooling is committed, the known list is empty, and the mini-air is set up.
- **Not for a session:** the host decisions in §1 and D-1200 stay Mat's.
- Work stays on `main` only, with no branch or worktree. The coordinator commits after the execution review and does not push.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 98 | `e2e-clipboard-specs` | — | P3 | executed (Session 98) | `docs/execution/plans/2026-11-20-e2e-clipboard-specs/` |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Session 98:** Session 96 `e2e-remote-host`, Session 91 `e2e-pointer-flakes`.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1265 | Which work is of most value to the application now, and how many sessions follow? | autonomous | One session, Session 98 `e2e-clipboard-specs`, P3, no MEU, carried by the coordinator through plan, execution and commit without a push. No session after it. | Local Canon | Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. Options: (A) Session 98 alone; (B) also group the plate residual or a monitoring issue; (C) do nothing and leave the register as triaged. A is the only candidate with a source and a removed blocker. B loses because AC-161.5 already gates the residual and no monitoring issue has recurred. C keeps seven capture tests unrun for as long as each plan copies the exclusion. M items: M-8 (it adds a session). Two-way. | — |
| D-1266 | How do the five tests that never touch the clipboard rejoin every full run? | autonomous | Move the two clipboard tests into one clipboard-only spec file with their assertions unchanged, and have the dev-PC exclusion and the mini-air skip name only that file. The plan names the new file and the pinned test it changes. | Local Canon | Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. Options: (A) split by file; (B) keep the files and filter by a test tag; (C) do nothing. A fits both runners as they stand, since the dev-PC tool and the mini-air skip list both exclude by file. B changes both selectors and leaves files that mix the two kinds. C keeps the five tests out of every gate. The skip pin in `test_ac_11_known_tracked_list` changes, so the plan must name it in a row to stay clear of M-7; Session 97 hit that pin unnamed (D-1259). M items: none. Two-way. | — |
| D-1267 | Where and when do the two clipboard tests run? | autonomous | On the mini-air only, and only when a probe before and after the run shows no remote-desktop session connected; otherwise the clipboard-only file is skipped with a named reason. RustDesk is never changed or stopped. If the plan cannot prove such a probe, the split ships alone and the file stays skipped. | Local Canon | Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations', continuing USER_EXPLICIT 2026-11-20 'continue orchestrating the next prompt session and the session after if there is any'. Options: (A) a connection probe on the mini-air; (B) turn off RustDesk's clipboard sync on that host; (C) run them on the dev PC; (D) do nothing and keep them skipped everywhere. A protects the clipboard of whoever is connected, as RULE-1 asks. B is a host setting and stays Mat's (D-1216 class). C is refused by Session 57 RULE-4. D leaves Copy image, Copy full path and Ctrl+V paste with no gate. M items: M-3 (a new run rule for the second host). Two-way. | — |
| D-1200 | Send FFmpeg a report on the open `-read_intervals START%` form (Session 93)? | open | | Local Canon | Carried from `2026-11-18-e2e-remote-host-session-grouping.md`, unchanged: Mat's to make (M-12). | — |

Carry-forward: the closeout validator reads every §8 row of this file through `--decision-source`, so the session's reflection does not restate them. Its `### Decisions Log` lists only that session's own reversible autonomous choices (HDP §6).

- Session 98 carries D-1265, D-1266 and D-1267. Its issues' D-1261 and D-1262 are read from `known-issues.yaml`.
