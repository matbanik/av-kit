# Local requests — 2026-09-30-tts-repair

Requests from the cloud driver to Mat's Windows machine (`P:/av-kit`), in the shapes from `.agent/docs/cloud-local-collaboration.md` §5.1 and §7. Each request is sent as the last block of a cloud turn; this file keeps the durable copy.

## LOCAL_REPRO — sent with the plan (task row 1)

This is the single repro request for the still-unverified UI findings (grouping §5; cloud-local §7). It runs against the **current** build, so no code from this plan is needed. Run it any time before execution reaches task row 7.

```text
LOCAL_REPRO request — 2026-09-30-tts-repair (Session 27), for the grouping's unverified UI findings
branch:   claude/vigilant-keller-tg7n45   (plan-only commit; product code identical to main)
from:     P:/av-kit, app started as you normally run it for manual testing (note dev vs packaged in the reply)
window:   default size (1280x800); no zoom
items:
  R1 TTS-GENERATE-FAILED-SILENT (GUI half): load any model, press Generate with the current machine state.
     reproduced = run bar shows "Failed" and no reason text. Record: exact run-bar text + the job's
     error_message from GET /api/v1/tts/<id> (or the Console line), and a screenshot of the run bar.
  R2 TTS-MODEL-MANAGE-AFFORDANCE: open TTS → Voice → "Manage". reproduced = four rows each with Get + Load
     whose enabled/disabled states look alike. Record: screenshot, which variants are downloaded/loaded.
  R3 CAPTURE-TOOLBAR-ICONS (for Session 29): Capture page at the default window with one shot selected.
     reproduced = the viewport toolbar overflows or wraps. Record: screenshot.
  R4 SETTINGS-ACTIVE-SECTION-HIGHLIGHT (for Session 31): scroll Settings top to bottom.
     reproduced = the rail highlight does NOT follow the section in view. Record: yes/no per section + screenshot.
  R5 TTS-LANGUAGE-VOICE-PICKER-SPACE: TTS page at the default window, HelpCard in its default state, Language = All.
     reproduced = Speed and/or Format are below the fold without scrolling. Record: which are visible + screenshot
     (feeds AC-64.6 / Stop condition S8).
return:   paste results in chat (one line per item: R<n> reproduced|not-reproduced|different: <what>) plus screenshots;
          or set verification.last_checked/method/result/evidence_file yourself and run
          `uv run python tools/issue_triage.py render`. Never hand-edit known-issues.md.
```

## GATE — sent at task row H1-6 (filled in at that time)

The template is below. `<sha>`, the attempt number and the floors are filled in when the request is sent.

```text
WINDOWS_GATE + TTS_LIVE request — 2026-09-30-tts-repair, attempt <N>
branch:   claude/vigilant-keller-tg7n45
commit:   <full sha>   (tree clean at exactly this sha; leftover windows-gate-result.json / tts-live-result.json are fine)
run:      pwsh -NoProfile -File docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1 -Check windows-gate
then:     pwsh -NoProfile -File docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1 -Check tts-live
from:     P:/av-kit, quiet machine (no other agent thread / Remote Control / Electron / Playwright — say so in the reply),
          ELECTRON_RUN_AS_NODE and AVKIT_E2E_OUT_DIR cleared (the script clears them too)
preflight: script records P:/agentic-framework HEAD + P:/.agent registry hash; if either differs from
          attempt <N-1>, it stops before stage 1 — report it
expect:   the 17 stages of validate-task.ps1 in order, all exit 0;
          vitest / e2e at or above COUNT_FLOORS (implementation-plan.md; copy the numbers in when sending), 0 failed / 0 unexpected / 0 flaky;
          tts-live: every step in tts_live_check.py STEP_IDS passes
          (needs network to huggingface.co and github.com; uses C:/Temp/av-kit/s27-live, never ~/.avkit)
return:   commit + push docs/execution/plans/2026-09-30-tts-repair/windows-gate-result.json and tts-live-result.json
          ("docs(execution): record Session 27 Windows gate (attempt N)")
on fail:  preserve ui/test-results + C:/Temp/av-kit/s27-* to C:/Temp/av-kit/keep/<sha>-attempt<N>/ FIRST;
          targeted --repeat-each into a separate dir; classify vs diff; report — do not fix without an A-decision
```

### GATE — attempt 1 (sent 2026-09-30, H1-6)

```text
WINDOWS_GATE + TTS_LIVE request — 2026-09-30-tts-repair, attempt 1
branch:   claude/vigilant-keller-tg7n45
commit:   the branch head (code = d793f1fd98690ea43ce86cf10a98470dbd1745cf; later commits are docs/.agent only,
          outside GATED_PATHS, so windows-gate-check binds either sha). Tree clean at the head you run.
run:      pwsh -NoProfile -File docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1 -Check windows-gate
then:     pwsh -NoProfile -File docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1 -Check tts-live
from:     P:/av-kit, quiet machine (no other agent thread / Remote Control / Electron / Playwright — say so in the reply),
          ELECTRON_RUN_AS_NODE and AVKIT_E2E_OUT_DIR cleared (the script clears them too)
preflight: first attempt — the script records P:/agentic-framework HEAD + P:/.agent registry hash as the reference
expect:   the 17 stages of validate-task.ps1 in order, all exit 0;
          vitest >= 675 and e2e >= 110 (COUNT_FLOORS), 0 failed / 0 unexpected / 0 flaky;
          (container pre-gate on d793f1f saw vitest 700, e2e 111 + 4 Windows-only capture-picker specs, pytest 566)
          tts-live: every step in tts_live_check.py STEP_IDS passes
          (fresh-rows, variant-download, spacy-autoload, generate-wav, console-events;
           needs network to huggingface.co and github.com; uses C:/Temp/av-kit/s27-live, never ~/.avkit;
           container run: generate-wav Done, 2.075 s WAV)
return:   commit + push docs/execution/plans/2026-09-30-tts-repair/windows-gate-result.json and tts-live-result.json
          ("docs(execution): record Session 27 Windows gate (attempt 1)")
on fail:  preserve ui/test-results + C:/Temp/av-kit/s27-* to C:/Temp/av-kit/keep/<sha>-attempt1/ FIRST;
          targeted --repeat-each into a separate dir; classify vs diff; report — do not fix without an A-decision
```

### A-2 rebind + GATE — attempt 2 (sent 2026-09-30)

```text
A-2 REBIND (local agent, Mat's Windows host; human-gate-decision.md §A-2 is the authority)
branch:   claude/vigilant-keller-tg7n45, pull the head first; tree clean
edit 1:   docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md
          embedded rule-map.v1 JSON: ONLY counts."AGENTS.md".postimage_sha256 and counts."GUARDRAILS.md".postimage_sha256
          := sha256 of the checkout files (Get-FileHash -Algorithm SHA256, lower-cased)
edit 2:   docs/execution/plans/2026-09-26-framework-update-adoption/adoption-manifest.json
          protected_files += {"path": ".agent/docs/human-decision-protocol.md", "preimage_sha256": "<sha256 of the checkout file>"}
          (append; keep the file's existing formatting/indentation)
verify:   uv run pytest tests/tooling/test_framework_adoption.py -q -p no:cacheprovider   → all pass
          then the full suite without -x: uv run pytest tests/ -q -p no:cacheprovider      → 0 failed
stop:     if ANY tests/tooling failure remains (rule coverage, routing census, file drift, …): make no further edit,
          revert nothing else, report the REFUSE line(s) — that is a new decision, not part of A-2
commit:   "chore(governance): rebind 2026-09-26 adoption records to current governance (S27 A-2)"; push

WINDOWS_GATE request — 2026-09-30-tts-repair, attempt 2 (only after the rebind commit is pushed)
commit:   the new branch head (code under test unchanged since d793f1f; the rebind files are outside GATED_PATHS)
run:      pwsh -NoProfile -File docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1 -Check windows-gate
          (TTS_LIVE attempt 1 PASS stands — not re-run)
from:     P:/av-kit, quiet machine (say so), ELECTRON_RUN_AS_NODE and AVKIT_E2E_OUT_DIR cleared
preflight: must match attempt 1's reference (agentic-framework 4033418f66d2…, registry sha256 B06D7CDA110C…); if not, stop and report
expect:   17 stages in order, all exit 0; vitest >= 675, e2e >= 110, 0 failed / 0 unexpected / 0 flaky
return:   commit + push windows-gate-result.json ("docs(execution): record Session 27 Windows gate (attempt 2)")
on fail:  preserve to C:/Temp/av-kit/keep/<sha>-attempt2/ FIRST; classify vs diff; report — no fix without an A-decision
```

### GATE — attempt 3 (sent 2026-10-01, after A-3)

```text
WINDOWS_GATE + TTS_LIVE request — 2026-09-30-tts-repair, attempt 3
branch:   claude/vigilant-keller-tg7n45 — run on the head after 054f2c7 (A-3 product fix; tree clean)
run:      pwsh -NoProfile -File docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1 -Check windows-gate
then:     pwsh -NoProfile -File docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1 -Check tts-live
          (BOTH, on the SAME commit: tts-live-check requires tts-live.tested_commit == windows-gate.tested_commit)
from:     P:/av-kit, quiet machine (say so), ELECTRON_RUN_AS_NODE and AVKIT_E2E_OUT_DIR cleared
preflight: must match attempts 1–2 (agentic-framework 4033418f66d2…, registry sha256 B06D7CDA110C…); drift → stop, report
expect:   17 stages in order, all exit 0; vitest >= 675 (attempt 2: 702), e2e >= 110 with 0 failed / 0 unexpected / 0 flaky
          (expected count now 115 = 113 + 2 new startup-reveal specs); tts-live: all 5 STEP_IDS pass
          (container after A-3: e2e 113 passed + 4 Windows-only capture-picker, suite 2.3 min; drag specs ~2 s)
return:   commit + push windows-gate-result.json and tts-live-result.json
          ("docs(execution): record Session 27 Windows gate (attempt 3)")
on fail:  preserve to C:/Temp/av-kit/keep/<sha>-attempt3/ FIRST; targeted --repeat-each in a separate dir;
          classify vs diff and vs origin/main; report — no fix without an A-decision
```

### GATE — attempt 4 (sent 2026-10-01, after A-4)

```text
WINDOWS_GATE + TTS_LIVE request — 2026-09-30-tts-repair, attempt 4
branch:   claude/vigilant-keller-tg7n45 — the head carrying ae8aaef (MEU-62 hermeticity) and the A-4 helper commit; tree clean
run:      validate-task.ps1 -Check windows-gate, then -Check tts-live — BOTH on the SAME commit
from:     P:/av-kit, quiet machine; ELECTRON_RUN_AS_NODE / AVKIT_E2E_OUT_DIR cleared; real ~/.avkit/models left AS IS
          (do NOT move the spaCy install aside — the fix must hold with it present)
preflight: must match attempts 1–3 (agentic-framework 4033418f…, registry B06D7CDA…)
expect:   17 stages exit 0; pytest 0 failed (incl. test_tts_assets.py with the real home install present);
          vitest >= 675; e2e >= 110 with 0 unexpected / 0 flaky (115 expected);
          tts-live: 5 steps pass AND fresh-rows shows tts_spacy_model "missing" and spacy-autoload "missing" -> "ready"
          (site_spacy false)
return:   commit + push windows-gate-result.json + tts-live-result.json ("… Windows gate (attempt 4)")
on fail:  preserve to C:/Temp/av-kit/keep/<sha>-attempt4/ FIRST (a dragOver timeout now carries
          "A-4 drag diagnostics: {...}" — paste it verbatim); classify; report — no fix without an A-decision
```

### GATE — attempt 5 (sent 2026-10-01)

Same as attempt 4, on the head carrying the `tests/conftest.py` `_restore_import_path` fix: WINDOWS_GATE then TTS_LIVE on the SAME commit. Real `~/.avkit/models` stays as is. Expect 17 stages exit 0; pytest 0 failed; vitest ≥ 675; e2e 115 expected / 0 unexpected / 0 flaky; tts-live 5/5 with spaCy `missing → ready`. Return both JSONs ("… (attempt 5)"). On failure: preserve to `keep/<sha>-attempt5/` first, paste any `A-4 drag diagnostics` verbatim, classify, report. No fix without an A-decision.

### GATE — attempt 6 (sent 2026-10-01, after A-5)

Same as attempt 5, on the head carrying the A-5 `npm-ci` stage change in `validate-task.ps1`. The `npm-ci` stage now ends with a serial `node ui/node_modules/electron/install.js` and a `path.txt` check; its receipt `s27-win-npm-ci.txt` should show the download, or an immediate no-op. WINDOWS_GATE then TTS_LIVE on the SAME commit. Real `~/.avkit/models` stays as is. Expect 17 stages exit 0, pytest 0 failed, Vitest ≥ 675 with 0 failed, e2e 115 expected / 0 unexpected / 0 flaky, and TTS_LIVE 5/5 `missing → ready`. If the `npm-ci` stage itself fails, report its receipt verbatim (it is the new code). No fix without an A-decision.

### GATE — attempt 7 (sent 2026-10-01, after A-6)

Same as attempt 6, on the head carrying:
- `9279725`: AC-63.5 waits one job poll;
- the A-6 `SettingsRail` click-lock fix and its new e2e spec.

WINDOWS_GATE, then TTS_LIVE, on the SAME commit. Real `~/.avkit/models` stays as is. Expect: 17 stages exit 0; pytest 0 failed; Vitest ≥ 675 with 0 failed; **e2e 118 total, all expected** (attempt 6's 117 total + the A-6 spec) / 0 unexpected / 0 flaky [count corrected after attempt 7: Playwright's "expected" means passed]; TTS_LIVE 5/5 `missing → ready`. On failure: preserve to `keep/<sha>-attempt7/` first, paste any `A-4 drag diagnostics` verbatim, run targeted repeats, classify, report. No fix without an A-decision.
