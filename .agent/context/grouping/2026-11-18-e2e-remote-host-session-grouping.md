# 2026-11-18 E2E on a second host · Session grouping

> **Source:** the second 2026-11-18 issue triage of `.agent/context/known-issues.yaml`, which registered three issues from the mini-air E2E runs, and Mat's 2026-11-18 requests "Also look into p:/.agent fleet setup as per the p:/agentic-framework. There is mini-air 12 windows pc that could be used to run the E2E tests rather than running them directly on this system. Another session from p:/zorivest is setting up the CI tests for Desktop for it so consider including that in the plan after the reviewer is done." and "what you creating and scheduling the job as the signed in user so I don't have to do anything manually?"
> **Generated:** 2026-11-18
> **Method:**
> - Triage (`.agent/workflows/issue-triage.md`): `discover --dry-run` found 0 candidates, and `verify --deep` found nothing before or after the edits (`C:/Temp/av-kit/triage-1118b/discover.txt`, `verify.txt`). The three issues were added through `tools/issue_triage/model.py` (`C:/Temp/av-kit/triage-1118b/classify.py`), each with its stage `triage` decision (D-1212 to D-1214). `bucket` proposed one batch, `agent-ci-e2e-fleet-host-untracked` (P2). `triage --output` rewrote `triage-output.yaml`, and `render --check` is OK.
> - Evidence: the hand setup on MINI_AIR12 and its runs, in `C:/Temp/av-kit/fleet-research/miniair/` (scripts `01`–`16`, `run-e2e.ps1`; results `20261118-173538`, `-183804`, `-185348`, `-191358`). The last run passed 228 of 232 in 19 min, with the two clipboard specs skipped by design.
> - Fleet research (read only): `C:/Temp/av-kit/fleet-research/2026-11-18-mini-air-e2e-notes.md`. The agentic-framework fleet member runs its steps in S4U scheduled tasks with no desktop and refuses `pwsh`, so it cannot run Electron E2E as it stands, and that repository is not edited from here.
> - Stage A: skipped. No MEU is needed for Session 96, which adds test tooling only. Session 97 decides whether a product change is needed; if it is, it gets a MEU then.
> - Stage B: two sessions.
> **Origin:** the 2026-11-18 register-residuals grouping is fully executed (Session 95, `eaa3c0f`); `meu_status next` reads "No pending+unblocked MEUs found".
> **Status:** Active. This is a reversible draft, not a gate. Mat asked for the fleet E2E work to be planned after the Session 95 review; the coordinator plans and executes the sessions and commits them without a push.
> **Parallel work:** only the `main` worktree exists, and HEAD is `eaa3c0f`. The highest decision ID in use is D-1206, with D-1207 to D-1210 left unused by Session 95. No Session 96 or later and no D-1211 or later was claimed anywhere. A zorivest session is preparing a GitHub Actions self-hosted runner (user `zvci`) on the same host; it is uncommitted.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (issue) | Layer | Depends on |
|-----|------|----------------|-------|------------|
| — (no MEU) | `e2e-remote-host` | `CI-E2E-FLEET-HOST-UNTRACKED` | test tooling: send a commit to a second Windows host, build it, run the full E2E suite in the signed-in desktop session, bring back the report; its run book and tests | the hand setup's proven steps |
| — (no MEU unless the diagnosis needs product code) | `e2e-host-parity` | `CAPTURE-TEXT-PIXEL-2PX-MINIAIR`, `E2E-HOVER-NO-POINTER-DEVICE` | capture text preview and bake geometry, or the spec; `settings.test.ts` AC-126.8 | Session 96, so the mini-air run that proves the fix is repeatable |

No build-plan home for Session 96: no product behaviour changes, as for Sessions 78, 90, 91 and 95.

Issue → disposition traceability (every issue open or mitigated at the start of this pass, plus the three new ones, 14 in all):

| Issue | Status · category | Disposition |
|-------|-------------------|-------------|
| `CI-E2E-FLEET-HOST-UNTRACKED` | open · PLAN-NEW P2 (new) | Session 96, no MEU (D-1212) |
| `CAPTURE-TEXT-PIXEL-2PX-MINIAIR` | open · TECH-DEBT P2 (new) | Session 97, diagnose first (D-1213) |
| `E2E-HOVER-NO-POINTER-DEVICE` | open · TECH-DEBT P3 (new) | Session 97 (D-1214) |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | open · MONITORING P4 | Not grouped (D-1197). No hang in the four mini-air runs either |
| `TOOLING-SHARED-REGISTRY-COUPLING` | mitigated · TECH-DEBT P2 | Not grouped: rides the next change to that file (D-912) |
| `TRANSCRIPT-ADD-CHANNEL-422` | open · MONITORING | Not grouped: not seen again |
| `E2E-CLIPBOARD-PRIMER-EMPTY` | open · MONITORING | Not grouped: not seen again; the clipboard specs stay off the mini-air because RustDesk syncs its clipboard |
| `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | open · MONITORING | Not grouped: not seen again, including on the mini-air |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | mitigated · UPSTREAM | Not grouped: the upstream issue is still open |
| `CAPTURE-JOURNAL-VOLATILE` | open · DEFER | Not grouped: deferred by its own ruling |
| `TTS-JA-ZH-G2P-EXTRAS` | open · DEFER | Not grouped: deferred by its own ruling |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | open · BLOCKED | Not grouped: waits for eSpeak NG on a test machine (Mat's install) |
| `FFMPEG-LIBDVDCSS-BUNDLED` | open · CLOSE | Not grouped: an accepted risk (D-266) |
| `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` | resolved | Session 95 (`eaa3c0f`) |

Host decisions that stay Mat's (none is needed for either session; D-1216):

| Item | Disposition |
|------|-------------|
| Turning Smart App Control off on the mini-air | Mat's: it is permanent without a Windows reset. The sessions use the sha256-checked gyan.dev 9.0.2 release ffmpeg, which it allows |
| Auto sign-in with a stored password | Mat's: it stores a credential. The tooling instead refuses with a named reason when nobody is signed in or the desktop is locked |
| A GitHub Actions self-hosted runner for av-kit | Mat's (M-12 class, outward): av-kit is public, and GitHub warns that a self-hosted runner on a public repository can run code from a fork's pull request. Not proposed |
| D-1200, the FFmpeg upstream report | Mat's, carried from the previous grouping |

---

## 2. Dependency graph + critical path

```
hand setup (2026-11-18, 228/232) ──► Session 96 (e2e-remote-host) ──► Session 97 (e2e-host-parity)
```

**Critical path:** 96 then 97. Session 97's acceptance includes a mini-air run through Session 96's tooling.

**Shared files:** none between them except `known-issues.yaml` and this grouping's §6 rows. Session 96 adds files; Session 97 changes `capture-inbox.test.ts`, `settings.test.ts` and, if the diagnosis needs it, capture renderer code.

**Shared host:** the zorivest runner (`zvci`) uses the same 4-core host. Session 96's tooling refuses to start while a `zvci` process or another av-kit run is active, and never stops either.

---

## 3. Recommended grouping — 2 sessions (96, 97)

### Session 96 — `e2e-remote-host` (no MEU) · P2

- **Layer / files:**
  - New tracked tooling that a coordinator runs on the dev PC. The plan picks its home and language with an HDP brief (for example a plan-local script promoted to `tools/`, or a `ui/scripts/` entry next to `playwright-with-outputfile.mjs`).
  - The host side: the build and run scripts it copies over, adapted from `02-build.ps1`, `11-rerun.ps1` and `run-e2e.ps1`.
  - A run book in `.agent/docs/` naming the host prerequisites the hand setup found: Node, the Visual C++ runtime, the release ffmpeg on the run's PATH only, the out-e2e harness build, the mtime reset, and the Interactive-logon task as the signed-in user.
  - Its tests.
- **Covers:** `CI-E2E-FLEET-HOST-UNTRACKED` (D-1212).
- **Shape (D-1215):** SSH with the pinned host alias, `scp` of a `git archive` of the asked commit, a build on the host, then `Start-ScheduledTask` on an Interactive-logon task registered for the signed-in user, polling for a `DONE` file, and copying `meta.txt`, `report.json` and a summary back to `C:/Temp/av-kit/`. Nothing is stored: no password, no token.
- **Refusals, each with a named reason and a non-zero exit:**
  - session 0 or no signed-in user;
  - a locked desktop;
  - a busy host: a `zvci` process, or another av-kit run's lock;
  - a source tree whose recorded commit is not the one asked for;
  - a stale build.
- **Host details:** the host alias, the account and the folder go in an untracked local config, never in a tracked file (the repo is public), with a tracked example.
- **Acceptance direction:**
  - Tests with fake `ssh`/`scp` prove each refusal and that the summary is read from `report.json`, not from the console.
  - One real run of HEAD on the mini-air through the tooling ends with the counts in a receipt: 228 of 232 expected, with the 4 known failures named and no others.
- **Gate:** no product code. The clipboard specs stay skipped on that host. No process on the host is stopped except the run's own, by recorded pid. The home-path gate runs before and after.
- **Cloud/local:** local, plus the mini-air.
- **Token estimate:** calibrate against Session 90 `test-run-reliability` (E2E runner tooling) and Session 83 `docs-path-hygiene` (one tool and its tests).
- **Split flag:** no.

### Session 97 — `e2e-host-parity` (no MEU unless the diagnosis needs one) · P2

- **Layer / files:** `ui/tests/e2e/capture-inbox.test.ts` AC-82.6, AC-102.19 and AC-102.20, and the capture text bake or preview code if the measured cause is there; `ui/tests/e2e/settings.test.ts` AC-126.8.
- **Covers:** `CAPTURE-TEXT-PIXEL-2PX-MINIAIR` (D-1213), `E2E-HOVER-NO-POINTER-DEVICE` (D-1214).
- **Acceptance direction:**
  - The pixel specs: measure the preview and bake boxes on both hosts and name which side moves before any change. The product is fixed if it is wrong; a tolerance changes only if both sides are correct and the difference is measured rasterisation.
  - The hover spec: reproduce `hover: none` on the dev PC first, then make the spec state the hover capability it needs.
  - A mini-air run through Session 96's tooling passes 232 of 232 (clipboard specs skipped), and the dev-PC run stays green.
- **Gate:** never edit a test to pass (S3). If the cause is in the product, Stage A adds a MEU before the code changes.
- **Cloud/local:** local, plus the mini-air.
- **Token estimate:** calibrate against Session 82 (text parity) and Session 91 `e2e-pointer-flakes`.
- **Split flag:** yes, if the pixel diagnosis finds product code; the hover fix then lands alone.

---

## 4. Plan-creation pathway

Mat's requests continue the orchestration, so the coordinator runs plan creation for Session 96 now, followed by its Codex plan review, execution, the Codex execution review and a signed commit without a push. Session 97 follows the same way after Session 96 is committed.

1. `/create-plan e2e-remote-host` → no MEU, plan folder `docs/execution/plans/2026-11-18-e2e-remote-host/`, decision ids D-1221 to D-1240
2. `/create-plan e2e-host-parity` → after Session 96; decision ids from D-1241

---

## 5. Prerequisite gate

- **Can begin now:** Session 96. The host is set up and reachable, and the signed-in desktop is live.
- **Waits:** Session 97 waits for Session 96's commit.
- **Not for a session:** the host decisions in §1 and D-1200 stay Mat's.
- Work stays on `main` only, with no branch or worktree. The coordinator commits each session after its execution review and does not push.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 96 | `e2e-remote-host` | — | P2 | executed (Session 96) | `docs/execution/plans/2026-11-18-e2e-remote-host/` |
| 97 | `e2e-host-parity` | — | P2 | pending | — |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Session 96:** Session 90 `test-run-reliability`, Session 83 `docs-path-hygiene`.
- **Session 97:** Session 82 text parity, Session 91 `e2e-pointer-flakes`.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1211 | Triage the mini-air findings, group them, and carry the result through plan, execution and commit as in the last grouping? | human | Yes. D-1212 to D-1214 are written, and Sessions 96 and 97 are grouped. The coordinator plans, executes and commits them without a push, and the triage workflow's step 8 stop is passed on this request. | Human-approved | Mat asked for the fleet E2E work to be included in the plan after the Session 95 review, and for the orchestration to run as before; that run carried each session from triage to commit with no push. | USER_EXPLICIT 2026-11-18 "consider including that in the plan after the reviewer is done"; USER_EXPLICIT 2026-11-18 "proceed with the next session prompt orchestration here like you did the others" |
| D-1215 | How does the tracked tooling reach the host's desktop? | autonomous | SSH with the pinned alias, a `git archive` copy, a host build, and an Interactive-logon scheduled task registered for the signed-in user, polled for `DONE`. The plan picks the files and language. | Local Canon | It is the route that already passed 228 of 232 with nothing stored, and it is what Mat asked for ("scheduling the job as the signed in user so I don't have to do anything manually"). The fleet member cannot run it (S4U, no desktop, no `pwsh`), and changing the agentic-framework is outside this repository. A GitHub self-hosted runner would put a public repository's pull requests on a home machine and needs Mat's registration (D-1216). Doing nothing keeps every full run on the shared dev PC. `mandatory: none`. Two-way. | — |
| D-1216 | Do the sessions need any of the host decisions in §1 (Smart App Control, auto sign-in, a GitHub runner)? | autonomous | No. Each stays Mat's and unchanged; the tooling works without them and refuses with a named reason when the desktop is not signed in or is locked. | Local Canon | Each of them is permanent, stores a credential or is outward-facing (HDP M-12 class), which a hand-over does not cover. None is needed: the release ffmpeg passes Smart App Control, and a signed-in session is what Mat already keeps on that host. `mandatory: none`. | — |
| D-1200 | Send FFmpeg a report on the open `-read_intervals START%` form (Session 93)? | open | | Local Canon | Carried from `2026-11-18-eval-describe-session-grouping.md`, unchanged: Mat's to make (M-12). | — |

Carry-forward: the closeout validator reads every §8 row of this file through `--decision-source`, so each session's reflection does not restate them. Its `### Decisions Log` lists only that session's own reversible autonomous choices (HDP §6).

- Session 96 carries D-1211, D-1215 and D-1216. Its issue's D-1212 is read from `known-issues.yaml`.
- Session 97 carries D-1211 and D-1216. Its issues' D-1213 and D-1214 are read from `known-issues.yaml`.
