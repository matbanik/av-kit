# 2026-11-22 Tray show and baseline fixes · Session grouping

> **Source:** Mat's request of 2026-11-22, "add an issue where if icon in system tray is double clicked the "Show window" action needs to be executed. Than proceed with you recommendations". It came right after the 2026-11-22 triage pass, whose report recommended fixing the two baseline pytest failures that Session 101 deselected (D-1360).
> **Generated:** 2026-11-22
> **Method:**
> - Triage (`.agent/workflows/issue-triage.md`), 2026-11-22: `TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE` (D-1361) and `TOOLING-PLAN-SLUG-ANCESTOR-MATCH` (D-1362) were registered from Session 101's baseline failures, each reproduced by `C:/Temp/av-kit/2026-11-22-triage/repro.py` (receipt `repro.txt`). `TRAY-DOUBLE-CLICK-NO-SHOW` (D-1363) was registered from Mat's words above. The three entries were appended by byte scripts, `triage --output` and `render` were rerun, and the RULE-3 line-ending check (`crlf.py`) left all three register files CRLF in the working copy.
> - Reproduction: `ui/src/main/capture-tray.ts` sets a context menu and registers no `double-click` listener; a grep of `ui/src` finds none elsewhere.
> - Stage A: skipped. One small main-process change and two test or tooling fixes.
> - Stage B: one session (D-1364).
> **Origin:** the 2026-11-21 grouping is fully executed and committed (Session 101, `7f34348`); 0.1.0-rc.4 is tagged at `159e178`.
> **Status:** Active. This is a reversible draft, not a gate.
> **Parallel work:** only the `main` worktree exists, at `7f34348`. The tree holds the three triage register files and nothing else. This grouping claims D-1363 to D-1399, Session 102 and MEU-164.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (issue) | Layer | Depends on |
|-----|------|----------------|-------|------------|
| MEU-164 | `gui-tray-double-click-show` | `TRAY-DOUBLE-CLICK-NO-SHOW` | main process: `ui/src/main/capture-tray.ts`; tests: Vitest, Electron E2E; docs: `09-screenshot-capture.md` tray row | MEU-39 |

Build-plan home: [09 §Tray double-click](../../../docs/build-plan/09-screenshot-capture.md#tray-double-click), matrix 9.47.

The session also carries two TECH-DEBT fixes as non-MEU rows (no build-plan home, as for other register debt):

- `TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE`: `tests/unit/test_capture_adapter.py` AC-130.10 compares the ICC profiles with the header's creation date and time (bytes 24 to 35) masked.
- `TOOLING-PLAN-SLUG-ANCESTOR-MATCH`: `tools/validate_closeout_artifacts.py` `plan_slug` reads the slug from the plan's own folder only, so no dated ancestor (a dated TEMP included) can supply it.

Issue → disposition traceability (the three new issues, plus every issue open or mitigated at the start of this pass):

| Issue | Status · category | Disposition |
|-------|-------------------|-------------|
| `TRAY-DOUBLE-CLICK-NO-SHOW` | open · MEU-NEW P3 (new) | Session 102, MEU-164 (D-1363, D-1364) |
| `TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE` | open · TECH-DEBT P3 (new) | Session 102, debt row (D-1361, D-1364) |
| `TOOLING-PLAN-SLUG-ANCESTOR-MATCH` | open · TECH-DEBT P3 (new) | Session 102, debt row (D-1362, D-1364) |
| `TOOLING-RUFF-TOOLS-UNCLEAN` | open · TECH-DEBT P4 | Not grouped (D-1300): its files are `tools/issue_triage*` and `tools/meu_status*`, and Session 102 changes neither. `ruff check tools/validate_closeout_artifacts.py` already passes |
| `CAPTURE-TEXT-PLATE-METRICS-RESIDUAL` | open · TECH-DEBT P4 | Not grouped (D-1260) |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | open · MONITORING P4 | Watch item of Session 102: its new E2E spec launches and closes the app. D-1197's reopen rule governs a recurrence |
| `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | open · MONITORING P4 | Not grouped: Session 102 touches no transcript spec |
| `E2E-CLIPBOARD-PRIMER-EMPTY` | open · MONITORING P4 | Not grouped (D-1301's close bar) |
| `TRANSCRIPT-ADD-CHANNEL-422` | open · MONITORING P4 | Not grouped: not seen again |
| `CAPTURE-JOURNAL-VOLATILE` | open · DEFER P4 | Not grouped: deferred by its own ruling |
| `TTS-JA-ZH-G2P-EXTRAS` | open · DEFER P4 | Not grouped (D-229) |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | open · BLOCKED P3 | Not grouped: eSpeak NG still absent (D-230; Mat's install) |
| `FFMPEG-LIBDVDCSS-BUNDLED` | open · CLOSE P2 | Not grouped: an accepted risk (D-266) |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | mitigated · UPSTREAM P3 | Not grouped (D-232) |
| `TOOLING-SHARED-REGISTRY-COUPLING` | mitigated · TECH-DEBT P2 | Not grouped (D-912) |

Items that stay Mat's (none is needed for Session 102): D-1200 (the FFmpeg upstream report, M-12), and D-1216's host items.

---

## 2. Dependency graph + critical path

```
MEU-39 (tray, close-to-tray) ──► MEU-164 (tray double-click runs Show window)
TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE   (no dependency)
TOOLING-PLAN-SLUG-ANCESTOR-MATCH        (no dependency)
```

**Critical path:** Session 102 alone. MEU-39 is approved. The two debt rows run first, so the session's full pytest gate runs with no `--deselect`.

**Shared files:** `known-issues.yaml`, `current-focus.md`, `docs/execution/metrics.md` and this grouping's §6 row.

---

## 3. Recommended grouping — 1 session (102)

### Session 102 — `tray-show-and-baseline-fixes` (MEU-164 + 2 debt rows) · P3

- **Layer / files:**
  - `ui/src/main/capture-tray.ts`: one show function inside `startCaptureTray`, used by the Show window menu item and by a new `tray.on('double-click', …)` listener. Under `AVKIT_E2E` only, the tray and its menu are exposed on a `globalThis` hook, as `e2e-shell.ts` does for the shell log.
  - `ui/tests/unit/`: a Vitest file with `electron` mocked, and the four existing source-text pins on `capture-tray.ts` (`app-icon`, `capture-main.behavior`, `capture-page`, `login-item-ipc`) kept passing unchanged.
  - `ui/tests/e2e/`: a spec that hides, then minimizes, the window and drives the tray's `double-click` and the menu item through the hook.
  - `tests/unit/test_capture_adapter.py`: AC-130.10 compares the profiles with bytes 24 to 35 masked.
  - `tools/validate_closeout_artifacts.py`: `plan_slug` reads only the plan's own folder; a pytest file pins it, and the selftest is run under a dated TEMP.
  - Docs: the 09 tray row and a residual section, matrix row 9.47.
- **Covers:** `TRAY-DOUBLE-CLICK-NO-SHOW` (D-1363), `TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE` (D-1361), `TOOLING-PLAN-SLUG-ANCESTOR-MATCH` (D-1362).
- **Why (value):** after close-to-tray, the window comes back only through the right-click menu; double-click to reopen is the usual Windows tray behaviour, and Mat asked for it. The two debt fixes give every later gate a full pytest run with nothing deselected by name.
- **Acceptance direction:**
  - Unit: `startCaptureTray` registers one `double-click` listener; it and the Show window item call the same function, which shows and focuses the window. The four source-text pins still pass.
  - Electron E2E: with the window hidden, a tray double-click makes it visible; the menu item does the same.
  - pytest: AC-130.10 passes when the two profiles differ only in their creation time, and still fails when any other byte differs. `plan_slug` refuses a loose plan under a dated ancestor and returns the slug for a real plan path; the closeout selftest exits 0 under a dated TEMP.
- **Gate:** no API route, IPC channel, preload surface, OpenAPI document or MCP tool changes. The tray menu keeps its four items in order. No existing assertion changes, except AC-130.10's one comparison.
- **Cloud/local:** local. The E2E spec needs no clipboard, so it runs on the dev PC.
- **Token estimate:** calibrate against Session 101 `transcript-job-resume` (MEU-163, a small GUI change with an Electron E2E and one service guard).
- **Split flag:** no.

---

## 4. Plan-creation pathway

1. `/create-plan tray-show-and-baseline-fixes` → MEU-164 plus the two debt rows, plan folder `docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/`, decision ids from D-1365 to D-1399.

---

## 5. Prerequisite gate

- **Can begin now:** Session 102.
- Work stays on `main` only, with no branch or worktree. Commits only on Mat's direction.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 102 | `tray-show-and-baseline-fixes` | MEU-164 | P3 | executed (Session 102) | `docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/` |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Session 102:** Session 101 `transcript-job-resume`.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1364 | How are the tray double-click and the two baseline-failure fixes scheduled? | autonomous | One session, Session 102 `tray-show-and-baseline-fixes`, P3: MEU-164 plus the two TECH-DEBT fixes as non-MEU rows, debt rows first. Run now through plan, execution and both Codex reviews. Commit only on Mat's direction. | Local Canon | Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) one session for all three, now; (B) two sessions, the tray change alone and the two debt fixes together; (C) do nothing beyond registering the issues, so gates keep deselecting the two tests by name. A is what the triage report recommended and Mat told the agent to proceed with; all three are small, share no file, and the debt fixes let this session's own gate run with nothing deselected. B doubles the plan, review and closeout cost for under a day's work. C leaves the tray as Mat asked it not to be. M items: M-8 (it adds a session). Two-way. | USER_EXPLICIT 2026-11-22 'Than proceed with you recommendations' |
| D-1200 | Send FFmpeg a report on the open `-read_intervals START%` form (Session 93)? | open | | Local Canon | Carried from `2026-11-21-transcript-job-resume-session-grouping.md`, unchanged: Mat's to make (M-12). | — |

Carry-forward: the closeout validator reads every §8 row of this file through `--decision-source`, so the session's reflection does not restate them. Its `### Decisions Log` lists only that session's own reversible autonomous choices (HDP §6).

- Session 102 carries D-1364. Its issues' D-1361, D-1362 and D-1363 are read from `known-issues.yaml`.
