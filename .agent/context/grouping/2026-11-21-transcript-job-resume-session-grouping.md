# 2026-11-21 Transcript job resume · Session grouping

> **Source:** Mat's request of 2026-11-21, "can we add resume as action on the job in the 3 dot menu where the remove, open folder and compile options are?". It came after a transcript job paused by a caption block on a VPN could not be resumed from the app and was resumed through the MCP tool `avkit_transcript resume`.
> **Generated:** 2026-11-21
> **Method:**
> - Triage (`.agent/workflows/issue-triage.md`), narrowed to the new issue: `TRANSCRIPT-PAUSED-JOB-NO-RESUME-AFTER-RESTART` was added through `issue_triage.py add`, and its D-1350 entry was written through `tools/issue_triage/model.py`. `discover --dry-run` found 0 candidates. `verify --deep` found nothing, and plain `verify` lists the same seven `meu_completed` notes as at `159e178`. `triage --output` rewrote `triage-output.yaml`, and `render --check` is OK (`C:/Temp/av-kit/2026-11-21-transcript-job-resume/`). The other open issues were last rechecked in the second 2026-11-20 pass; nothing has run since then that changes them, so they keep their dispositions.
> - Reproduction: after a restart, the MCP list showed the job `Paused` and the processor `Idle`, and the page offered no Resume. A plan-time probe seeded a Paused job with one Done item into a scratch `avkit.db`, built the real services and resumed it from Idle; it reached `Done` with no caption request (`plan-probe-seed.txt`).
> - Stage A: skipped. One small GUI change plus a one-line service guard.
> - Stage B: one session (D-1351).
> **Origin:** the second 2026-11-20 grouping is fully executed (Session 100), and Session 99 (MEU-162) is committed (`0829061`); 0.1.0-rc.4 is tagged at `159e178`.
> **Status:** Active. This is a reversible draft, not a gate.
> **Parallel work:** only the `main` worktree exists, at `159e178`, with a clean tree. This grouping claims D-1350 to D-1399, Session 101 and MEU-163.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (issue) | Layer | Depends on |
|-----|------|----------------|-------|------------|
| MEU-163 | `gui-transcript-job-resume` | `TRANSCRIPT-PAUSED-JOB-NO-RESUME-AFTER-RESTART` | renderer: `features/transcript/transcript-controls.ts`, `transcript-card.ts`, `transcript-commands.ts`, `TranscriptPage.tsx`; core: `services/transcript.py` `resume_processing`; tests: Vitest, pytest, Electron E2E; docs: `gui-actions-index.md` | MEU-44, MEU-55, MEU-116 |

Build-plan home: [10 §Per-job resume (residual)](../../../docs/build-plan/10-queue-card-ui.md#transcript-job-resume-residual), matrix 10.12.

Issue → disposition traceability (the new issue, plus every issue open or mitigated at the start of this pass):

| Issue | Status · category | Disposition |
|-------|-------------------|-------------|
| `TRANSCRIPT-PAUSED-JOB-NO-RESUME-AFTER-RESTART` | open · MEU-NEW P3 (new) | Session 101, MEU-163 (D-1350, D-1351) |
| `TOOLING-RUFF-TOOLS-UNCLEAN` | open · TECH-DEBT P4 | Not grouped (D-1300): Session 101 changes no file in `tools/` |
| `CAPTURE-TEXT-PLATE-METRICS-RESIDUAL` | open · TECH-DEBT P4 | Not grouped (D-1260) |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | open · MONITORING P4 | Not grouped (D-1263, D-1197's reopen rule) |
| `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | open · MONITORING P4 | Watch item of Session 101: it adds tests to `transcript-queue.test.ts`, which uses the seam reload. Session 53 RULE-4 governs a recurrence (D-362) |
| `E2E-CLIPBOARD-PRIMER-EMPTY` | open · MONITORING P4 | Not grouped (D-1301's close bar) |
| `TRANSCRIPT-ADD-CHANNEL-422` | open · MONITORING P4 | Not grouped: not seen again |
| `CAPTURE-JOURNAL-VOLATILE` | open · DEFER P4 | Not grouped: deferred by its own ruling |
| `TTS-JA-ZH-G2P-EXTRAS` | open · DEFER P4 | Not grouped (D-229) |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | open · BLOCKED P3 | Not grouped: eSpeak NG still absent (D-230; Mat's install) |
| `FFMPEG-LIBDVDCSS-BUNDLED` | open · CLOSE P2 | Not grouped: an accepted risk (D-266) |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | mitigated · UPSTREAM P3 | Not grouped (D-232) |
| `TOOLING-SHARED-REGISTRY-COUPLING` | mitigated · TECH-DEBT P2 | Not grouped (D-912) |

Items that stay Mat's (none is needed for Session 101): D-1200 (the FFmpeg upstream report, M-12), and D-1216's host items.

---

## 2. Dependency graph + critical path

```
MEU-44 (queue card) ──► MEU-55 (transcript layout, card kebab) ──► MEU-163 (card Resume)
MEU-116 (block pauses the job) ─────────────────────────────────┘
```

**Critical path:** Session 101 alone. MEU-44, MEU-55 and MEU-116 are approved.

**Shared files:** `known-issues.yaml`, `current-focus.md`, `docs/execution/metrics.md` and this grouping's §6 row.

---

## 3. Recommended grouping — 1 session (101)

### Session 101 — `transcript-job-resume` (MEU-163) · P3

- **Layer / files:**
  - `features/transcript/transcript-controls.ts`: a per-card resume rule beside the existing ones, so the card module still restates no rule.
  - `transcript-card.ts`: `resume-job` first in `TRANSCRIPT_MENU_ORDER`, with its own test id so it never clashes with the toolbar's `resume-btn`.
  - `transcript-commands.ts` and `TranscriptPage.tsx`: a card command that rechecks the rule on fresh data, then sends the existing bodyless `POST /transcripts/resume`.
  - `packages/core/src/avkit_core/services/transcript.py`: `resume_processing` refuses while a job runs, as 03 already says (`03-service-layer.md:878`).
  - `docs/build-plan/gui-actions-index.md`: a row for the card action.
- **Covers:** `TRANSCRIPT-PAUSED-JOB-NO-RESUME-AFTER-RESTART` (D-1350).
- **Why (value):** a job that YouTube's caption block paused is stuck after every restart. Today the only ways out are the MCP tool or Remove, and Remove drops the job's progress. Mat hit it on 2026-11-21 and asked for this fix.
- **Acceptance direction:**
  - Unit: the rule is true only for the first Paused job while no job runs. The menu lists Resume first for that card and not for others. The command sends nothing when the rule no longer holds. The AC-55.5 menu pin is unchanged.
  - pytest: resume is refused while a job runs, and every job's status is unchanged. Resume from Idle still finishes a Paused job.
  - Electron E2E through the seam: the card's Resume on a Paused card with the processor Idle sends one bodyless resume. No card offers it while a job runs.
  - Electron E2E on the real backend: a Paused job with all items Done is seeded into a fresh app-data `avkit.db`. After launch, the card's Resume takes it to `Done` with no network.
- **Gate:** no API route, request body, OpenAPI document or MCP tool changes. The toolbar keeps three actions (11 TR1), and Start keeps skipping Paused jobs. No existing assertion changes.
- **Cloud/local:** local.
- **Token estimate:** calibrate against Session 89 `queue-convert-fixes` (MEU-156, a queue-rule change with a real-backend E2E).
- **Split flag:** no.

---

## 4. Plan-creation pathway

1. `/create-plan transcript-job-resume` → MEU-163, plan folder `docs/execution/plans/2026-11-21-transcript-job-resume/`, decision ids from D-1352 to D-1399.

---

## 5. Prerequisite gate

- **Can begin now:** Session 101.
- Work stays on `main` only, with no branch or worktree. Commits only on Mat's direction.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 101 | `transcript-job-resume` | MEU-163 | P3 | executed (Session 101) | `docs/execution/plans/2026-11-21-transcript-job-resume/` |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Session 101:** Session 89 `queue-convert-fixes`.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1351 | How is the card Resume scheduled? | autonomous | One session, Session 101 `transcript-job-resume`, P3, MEU-163, run now through plan, execution and both Codex reviews. Commit only on Mat's direction. | Local Canon | Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) Session 101 alone, now; (B) fold it into a wider transcript session with `TRANSCRIPT-ADD-CHANNEL-422`; (C) do nothing and keep the MCP tool as the way out. A is what Mat asked for and has a known cause and a small fix. B waits on an issue with no repro. C leaves a dead end on the page. M items: M-8 (it adds a session). Two-way. | — |
| D-1200 | Send FFmpeg a report on the open `-read_intervals START%` form (Session 93)? | open | | Local Canon | Carried from `2026-11-20-e2e-devpc-clipboard-session-grouping.md`, unchanged: Mat's to make (M-12). | — |

Carry-forward: the closeout validator reads every §8 row of this file through `--decision-source`, so the session's reflection does not restate them. Its `### Decisions Log` lists only that session's own reversible autonomous choices (HDP §6).

- Session 101 carries D-1351. Its issue's D-1350 is read from `known-issues.yaml`.
