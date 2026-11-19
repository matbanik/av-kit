# 2026-11-18 Register residuals · Session grouping

> **Source:** the 2026-11-18 issue triage of `.agent/context/known-issues.yaml` (11 issues open or mitigated at the start; all in the §1 traceability table), the open human decisions in the post-Session-91 next-session prompt, and Mat's request "proceed with the next session prompt orchestration here like you did the others".
> **Generated:** 2026-11-18
> **Method:**
> - Triage (`.agent/workflows/issue-triage.md`): `discover --dry-run` found 0 candidates, and `verify --deep` found nothing before or after the edits (`C:/Temp/av-kit/triage-1118/discover.txt`, `verify.txt`, `verify2.txt`). The edits were made through `tools/issue_triage/model.py` (`C:/Temp/av-kit/triage-1118/classify.py`). D-1196 and D-1197 are stage `triage` entries in their issues' `decision_log`. `bucket` found no actionable issue to group, because no issue is MEU-NEW. `triage --output` rewrote `triage-output.yaml`, and `render --check` is OK.
> - Rechecks:
>   - Session 64's describe receipt holds 9 mojibake arrows, 2 mojibake en dashes and no real arrow, read byte by byte.
>   - The home-path gate is green: `check_home_path: ok files=2695 allowlisted=60` (`home-check.txt`).
>   - anthropics/claude-code#98256 is still open; it was last updated 2026-11-13.
>   - Session 90's handoff confirms 3 of 7 failed full runs. The 2026-11-17 grouping's §3 and D-1133 and three register notes say 4 of 7.
> - Stage A: skipped. No MEU is needed, because the one session changes tooling and its run book, not the product.
> - Stage B: one session.
> **Origin:** the 2026-11-17 value-triage grouping is fully executed (Sessions 74 and 91 to 94); `meu_status next` reads "No pending+unblocked MEUs found". Session 92 filed `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` (D-1186), and Session 91 left `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` open after it did not reproduce.
> **Status:** Active. This is a reversible draft, not a gate. Mat asked for the orchestration to continue as before, so the coordinator plans and executes Session 95 and commits it without a push.
> **Parallel work:** none seen. Only the `main` worktree exists, and HEAD is `1ea63a1`. The highest decision ID in use is D-1195, and D-1154 and D-1193 to D-1195 were left unused by Session 91. No Session 95 or later and no D-1196 or later was claimed anywhere.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (issue) | Layer | Depends on |
|-----|------|----------------|-------|------------|
| — (no MEU) | `eval-describe-raw-bytes` | `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` | agent tooling: Session 64's eval run book `docs/execution/plans/2026-11-11-capture-export-copy/eval-run.md` step 3 and a raw-byte describe capture with a mojibake guard; its tests | Session 92's `eval-rerun.py` guard (D-1186) as the model |

No build-plan home: no product behaviour changes, as for Sessions 78, 90 and 91.

Issue → disposition traceability (every issue open or mitigated at the start, 11 in all):

| Issue | Status · category | Disposition |
|-------|-------------------|-------------|
| `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` | open · TECH-DEBT P4 (was unclassified) | Session 95, no MEU (D-1196) |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | open · MONITORING P4 (was TECH-DEBT P3) | Not grouped (D-1197): Session 91's 13 instrumented acceptance and watch runs had no hang. The phase logging stays, and the next hang reopens it as P3 |
| `TOOLING-SHARED-REGISTRY-COUPLING` | mitigated · TECH-DEBT P2 | Not grouped: one test still reads the machine registry (D-912). It rides the next change to that file, and Session 95 does not touch it |
| `TRANSCRIPT-ADD-CHANNEL-422` | open · MONITORING | Not grouped: not seen again |
| `E2E-CLIPBOARD-PRIMER-EMPTY` | open · MONITORING | Not grouped: not seen again |
| `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | open · MONITORING | Not grouped: not seen again |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | mitigated · UPSTREAM | Not grouped: anthropics/claude-code#98256 is still open, so DIALOG_FALLBACK stays |
| `CAPTURE-JOURNAL-VOLATILE` | open · DEFER | Not grouped: deferred by its own ruling |
| `TTS-JA-ZH-G2P-EXTRAS` | open · DEFER | Not grouped: deferred by its own ruling |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | open · BLOCKED | Not grouped: waits for eSpeak NG on a test machine (Mat's install) |
| `FFMPEG-LIBDVDCSS-BUNDLED` | open · CLOSE | Not grouped: an accepted risk (D-266). It stays open as the record |

Open human decisions from the next-session prompt → disposition (D-1199 unless noted):

| Item | Disposition |
|------|-------------|
| D-1152 and D-1153 (Session 91 execution) | Kept as recorded. The execution review accepted the rerun evidence |
| Redacting the raw home prefix in tracked files | **Already settled by D-1199 applying D-817.** Mat ruled D-817 A on 2026-11-15. Under that ruling a gate refuses new instances, evidence files stay byte for byte on the allowlist, and the live files were fixed, the two `known-issues.yaml` hits among them (Session 83). The gate is green today. Option B, rewriting every file, was the one Mat turned down. `current-focus.md:31` names the home path in words and holds no path. Rewriting history is a push (M-1) and is not proposed |
| FP16 preselection | Never preselected (D-330, D-331). The guard fixed the failures, not the default |
| The README screenshot showing the old Downloader gap | Not retaken until Mat asks (D-1129). A retake needs a real app run |
| An upstream FFmpeg report on `-read_intervals START%` | **Open, and Mat's to make (D-1200, M-12).** Mat files it or tells the agent to draft it |
| The 2026-11-17 count "4 of 7" | Corrected to 3 of 7 by a note on each of the three issues. The 2026-11-17 grouping and the D-1126 question are records and stay as written |

---

## 2. Dependency graph + critical path

```
Session 92 eval-rerun.py guard (D-1186, committed) ──► Session 95 (eval-describe-raw-bytes)
```

**Critical path:** Session 95 alone.

**Shared files:** none with open work. The Session 64 plan folder was last changed by Session 64. Session 92's folder is read, not edited.

---

## 3. Recommended grouping — 1 session (95)

### Session 95 — `eval-describe-raw-bytes` (no MEU) · P4

- **Layer / files:**
  - `docs/execution/plans/2026-11-11-capture-export-copy/eval-run.md`. Step 3 captures `describe` through a shell redirect, so PowerShell decodes the server's UTF-8 through the console code page.
  - A raw-byte describe capture, a script or a step in the existing `eval-check.py`. The plan picks which, with an HDP brief.
  - The tests that prove its guard.
  - Session 64's `task.md` row E-1 is an executed record and stays as written; a dated note in `eval-run.md` points at the new step.
- **Covers:** `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` (D-1196).
- **Model:** Session 92's `eval-rerun.py` captured describe with a subprocess as raw bytes and refused cp437 mojibake fail-closed. The plan reuses that guard; it does not write a second one. If both plan folders can call it, the plan says where the single copy lives.
- **Acceptance direction:**
  - The capture on the real harness writes the server's stdout bytes unchanged, with no mojibake sequence.
  - A cp437-decoded fixture built from real arrow and dash bytes is refused with a non-zero exit, and so is a mixed one.
  - `eval-run.md` step 3 names the new command.
  - The issue is resolved through the triage tool.
- **Gate:**
  - No model call and no eval run: the live surface was already evaluated on clean text by Session 92, and a rerun of Session 64's eval would measure a surface no client serves.
  - No network. No product code.
  - The home-path gate runs before and after.
  - Edits keep each file's line endings.
- **Cloud/local:** local.
- **Token estimate:** calibrate against Session 83 `docs-path-hygiene`, one tool, its tests and a few doc edits, and Session 92's eval-rerun row. Well under the per-session ceiling.
- **Split flag:** no.

---

## 4. Plan-creation pathway

Mat's request continues the orchestration, so the coordinator runs plan creation for Session 95 now, followed by its Codex plan review, execution, the Codex execution review and a signed commit without a push.

1. `/create-plan eval-describe-raw-bytes` → no MEU, plan folder `docs/execution/plans/2026-11-18-eval-describe-raw-bytes/`, decision ids from D-1201

---

## 5. Prerequisite gate

- **Can begin now:** Session 95. Its only input, Session 92's guard, is committed.
- **Not for a session:**
  - `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` waits for Mat's eSpeak NG install.
  - The FFmpeg report waits for Mat (D-1200).
- Work stays on `main` only, with no branch or worktree. The coordinator commits the session after its execution review and does not push.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 95 | `eval-describe-raw-bytes` | — | P4 | proposed | `docs/execution/plans/2026-11-18-eval-describe-raw-bytes/` |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Session 95:** Session 83 `docs-path-hygiene`, and Session 92 `mcp-audit-refresh`'s eval-rerun row.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1198 | Triage what the register still holds, group it, and carry the result through plan, execution and commit as in the last grouping? | human | Yes. D-1196 and D-1197 are written, and Session 95 is grouped. The coordinator plans, executes and commits it without a push, and the triage workflow's step 8 stop is passed on this request. | Human-approved | Mat asked for the next-session prompt's orchestration "like you did the others". That run carried each session from triage to commit with no push. Stopping after triage would ask again what Mat has already said. | USER_EXPLICIT 2026-11-18 "proceed with the next session prompt orchestration here like you did the others" |
| D-1199 | Which work forms a session, and what happens to the prompt's other open items? | autonomous | Session 95 alone, no MEU: the eval describe capture fix. Everything else is not grouped (§1). The home-prefix redaction applies D-817 A, so the evidence files stay byte for byte. FP16 stays never preselected (D-330, D-331). D-1152 and D-1153 are kept. The README screenshot waits for Mat (D-1129). | Local Canon | The mojibake is the only issue with a fix ready to copy (Session 92's guard). Every other row is monitoring, deferred, blocked, upstream or an accepted risk, each by its own ruling. Redaction was decided by Mat's D-817 A, which turned down rewriting every file: a session that rewrote the evidence would reverse a USER_EXPLICIT ruling (M-6) for no new reason, because the gate is green. Do nothing for the mojibake was weighed: it leaves a trap in a run book a later eval will follow, for a small cost to fix. `mandatory: none`. | — |
| D-1200 | Send FFmpeg a report on the open `-read_intervals START%` form (Session 93)? | open | | Local Canon | A report to a third party is a new external disclosure (M-12), which a hand-over does not cover (HDP §6). Recommendation: Mat files a short report on FFmpeg's tracker with the four `ffprobe.c` citations and Session 93's row 2 counts, under his own name, or tells the agent to draft it for him to send. Do nothing: av-kit is fixed either way (`BOUNDED_TAIL_READ`), and other ffprobe users keep the bug until someone reports it. | — |

Carry-forward: the closeout validator reads every §8 row of this file through `--decision-source`, so the session's reflection does not restate them. Its `### Decisions Log` lists only that session's own reversible autonomous choices (HDP §6).

- Session 95 carries D-1198 and D-1199. Its issue's D-1196 is read from `known-issues.yaml`.
