---
project: "2026-11-09-rc3-fixes"
source: "docs/execution/plans/2026-11-09-rc3-fixes/implementation-plan.md"
status: "in_progress"
---

# Task — rc.3 fixes and VM build (quick plan)

> **Authorization:** Mat, 2026-11-09, "fix the issues now and redeploy the rc.3 on the vm so I can
> retest. If you need to do quick plan and execution in this session go ahead." No commit, push,
> tag or release; those and the vendor-distinct review wait for Mat's word.
> **Receipts:** `C:/Temp/av-kit/s58rc3/`.

| # | Task | Validation | Status |
|---|---|---|---|
| 1 | Red: `tests/unit/test_tts_fetch_tls.py`, `tests/unit/test_transcript_flat_extract.py` | `red-py.txt`: 3 failed by assertion | `[x]` |
| 2 | Green F1 (certifi context, `certifi` dependency, `uv lock --offline`) and F2 (flat extract, cache keyed by `(url, flat)`) | `green-py.txt`: 3 passed | `[x]` |
| 3 | Red F3: two vitest cases in `transcript-page.behavior.test.ts` | `red-ui.txt`: 2 failed (`add-status` missing) | `[x]` |
| 4 | Green F3: `add-status` line in `TranscriptPage.tsx`, `video_count` on `TranscriptJobOut` | `green-ui.txt`: 42 passed | `[x]` |
| 5 | Broad checks in the main tree | ruff, format, pyright clean; pytest 1298 passed plus the one fixed fake (`_BotWallCoordinator` took no `flat`); UI typecheck, lint, 1185 tests | `[x]` |
| 6 | Clean clone at `e0c1d0b`, copy the fixes in, bump to rc.3 (Mat's ruling) | `bump.txt`: 15 files, 0 problems | `[x]` |
| 7 | Offline setup of the clone; version, OpenAPI and fix tests there | `setup.txt`: lock check, sync and both `npm ci` offline; 124 pytest passed; OpenAPI check; 42 vitest passed | `[x]` |
| 8 | Build `av-kit-Setup-0.1.0-rc.3.exe` with `build-rc3.ps1` in the clone | `build.txt`, `build-record.json`: 340,360,903 B, SHA-256 `5f7805361b14b14cb9bc08ce4dd495b0d547fa6df3b0dd5d3c7994629e826196`, build_inputs `dfd9a3d4…` (first run stopped at Copy-Item: the ignored `packaging/ffmpeg-win64` folder was absent in the clone; created, rerun passed). `smoke-unpacked.txt`: PASS, version 0.1.0rc3. `pyz-check.txt`: the packaged backend holds the certifi context, the flat add and the `(url, flat)` cache key | `[x]` |
| 9 | Revert the VM to `clean`; deploy the installer; guest hash equals the host's | `C:/Temp/zorivest/avkit-rc3-revert.txt` (snapshot `clean-zorivest` restored, WinRM up); `avkit-rc3-deploy.txt`; `avkit-rc3-guesthash.txt`: guest SHA-256 `5f780536…e826196` equals the host's | `[x]` |
| 10 | Report to Mat; the review, commit, tag and registers wait for Mat | reported 2026-11-09 | `[x]` |

## Round 2 — Mat's rc.3 retest (2026-11-09)

> Mat: model progress "at 0% for very long time"; the MP3 name "is very long squenace of letters
> and numbers"; Transcript "seems stuck and not processing any transcripts". Rulings: "Show
> retries on card (Recommended)", "Lowercase slug (Recommended)". Round 1 receipts were kept as
> `r1-build.txt`, `r1-build-record.json`, `r1-smoke-unpacked.*`, `r1-pyz-check.txt`.

| # | Task | Validation | Status |
|---|---|---|---|
| 11 | Red F4/F5/F6: `test_model_download_progress.py`, `test_tts_output_name.py`, `test_transcript_retry_message.py` | `red2-py.txt`: 14 failed by the missing feature | `[x]` |
| 12 | Green F4 (`progress.py`, `tqdm_class` on both downloads, `tqdm` dependency, offline relock), F5 (`output_stem`, `_free_paths`), F6 (`retry_message`, job message while Processing, cleared after) | `green2-py.txt`: 215 passed (the AC-73.8 pin test now takes `tqdm_class` apart; no per-retry log line, so AC-115.7's one line per blocked video holds) | `[x]` |
| 13 | Red/Green F6 UI: Processing in `JOB_MESSAGE_STATUSES` | `red2-ui.txt`: 1 failed; `green2-ui.txt`: 21 passed | `[x]` |
| 14 | Broad checks in the main tree | `ruff2.txt` clean; pyright 0 errors; `full2-py.txt` 1443 passed, 1 failed: `test_framework_adoption.py::…[validate_closeout_artifacts.py]`, which fails the same way at `e0c1d0b` (`clone-tooling.txt`), so it predates this round; ruff format flags 25 files that this round did not change, and none of this round's lines; UI typecheck, lint, 1186 tests | `[x]` |
| 15 | Copy into the clone in its line endings; `tqdm` in the clone's rc3 pyproject; offline relock, sync; tests there | `clone-lock2.txt`, `clone-sync2.txt`; `clone-py2.txt` 229 passed; `clone-ui2.txt` 21 passed | `[x]` |
| 16 | Rebuild with `build-rc3.ps1` in the clone | `build.txt`, `build-record.json`: 340,365,381 B, SHA-256 `6875c3a531fd9612a451486a090a5fc21778254ae61e1c6014ca34e10202647f`, build_inputs `ed7601b5…`; `smoke-unpacked.txt` PASS, version 0.1.0rc3; `pyz-check.txt` all True (round 1 plus F4, F5, F6); `asar-check.txt`: the renderer's set holds `Processing` | `[x]` |
| 17 | Revert the VM; deploy; guest hash equals the host's | `C:/Temp/zorivest/avkit-rc3-revert.txt`, `avkit-rc3-deploy.txt`, `avkit-rc3-guesthash.txt`: guest SHA-256 `6875c3a5…647f` equals the host's (round 1 files kept as `r1-avkit-rc3-*.txt`) | `[x]` |
| 18 | Report to Mat, with the Console level briefs (plan `## Decision Log` D-1, D-2); the review, commit, tag and registers wait for Mat | reported 2026-11-09 | `[x]` |

## Round 3 — Console level rulings D-1 and D-2 (2026-11-09)

> Mat: "recommendations to decisions are accepted, proceed as recommended". D-1: a level button
> shows its level and everything more severe (DEBUG shows all; default DEBUG). D-2: Settings →
> Log level (`app.log_level`) is the level the Console opens at; nothing is dropped from
> `console.log` or the ring. Round 2 receipts were kept as `r2-build.txt`, `r2-build-record.json`,
> `r2-smoke-unpacked.*`, `r2-pyz-check.txt`, `r2-asar-check.txt`.

| # | Task | Validation | Status |
|---|---|---|---|
| 19 | Red: `console-level-threshold.test.ts` (new); AC-27.8 and AC-27.9 in `console-polish.test.ts` rewritten to the threshold, citing D-1 | `red3-ui.txt`: 6 failed by the missing feature, 10 passed | `[x]` |
| 20 | Green: `lineMeetsLevel` replaces `lineMatchesExactLevel`; `loadStartLevel` read once on mount, a click wins, an unknown or failed answer keeps DEBUG; AppShell passes `apiFetch('/settings/app')`; the Settings Log level hint; spec rows `06-gui.md:342`, `gui-actions-index.md:114` | `green3-ui.txt`: 16 passed | `[x]` |
| 21 | Broad UI checks in the main tree | `ui-tsc3.txt` 0 errors; `ui-lint3.txt` clean; `ui-vitest3.txt` 114 files, 1192 tests passed | `[x]` |
| 22 | Copy into the clone in its line endings (`copy_round3.py`); clone tests | `clone-ui3.txt` 18 passed; `clone-tsc3.txt` 0 errors | `[x]` |
| 23 | Rebuild with `build-rc3.ps1` in the clone; smoke; pyz and asar checks | `build.txt`, `build-record.json`: 340,365,493 B, SHA-256 `ca0da0df495dd9b2b6fc0b352b0214f8027118ed8aac1265afa289d95335b136`, build_inputs `fe74a2c6…`; `smoke-unpacked.txt` PASS, version 0.1.0rc3; `pyz-check.txt` 12 True, 0 False; `asar-check.txt`: F6 set, the D-2 hint, the D-1 `indexOf` compare, `/settings/app` read | `[x]` |
| 24 | Deploy to the VM without a revert (Mat's models and settings stay; reinstall over); guest hash equals the host's | `C:/Temp/zorivest/avkit-rc3-deploy.txt`, `avkit-rc3-guesthash.txt`: guest SHA-256 `ca0da0df…5b136` equals the host's (round 2 files kept as `r2-avkit-rc3-*.txt`) | `[x]` |
| 25 | Report to Mat; the review, commit, tag and registers wait for Mat | reported 2026-11-09 | `[x]` |

## Round 4 — F7: an MP3 job leaves a WAV beside it (2026-11-09)

> Mat: "wav and mp3 are being created even though only mp3 is selected … I'm guessing it is
> because mp3 is being created from wav?"; "if i select wav it only generates wav". Cause: the MP3
> is encoded from a WAV that `_work` never removed (also so at `e0c1d0b`, named by job id).
> `_inspiration/_tts_pseudo_logic.md:181`: "Delete temp WAV after conversion". AC-77.5 requires
> only that the MP3 is kept; its two-file assertion recorded the old behaviour. Round 3 receipts
> were kept as `r3-*`.

| # | Task | Validation | Status |
|---|---|---|---|
| 26 | Red: `test_tts_mp3_only.py` (MP3 only; WAV only; a locked WAV ends Done and logs `tts.cleanup_failed`); AC-77.5's file list becomes the MP3 alone | `red4-py.txt`: 3 failed, 1 passed | `[x]` |
| 27 | Green: `_work` calls `_remove_partial(job_id, (wav_path,))` after the MP3 encode and cancel check | `green4-py.txt`: 66 passed | `[x]` |
| 28 | Broad checks in the main tree | `ruff4.txt` clean, format clean; `pyright4.txt` 0 errors; `full4-py.txt` 1446 passed, 1 failed: the pre-existing `test_framework_adoption.py::…[validate_closeout_artifacts.py]` | `[x]` |
| 29 | Copy into the clone (`copy_round4.py`); clone tests | `clone-py4.txt` 66 passed | `[x]` |
| 30 | Rebuild; smoke; pyz check with F7; asar check | `build.txt`, `build-record.json`: 340,364,473 B, SHA-256 `b99aafc56cd43cb606f579fdbbab5255e61cc14661ff268ecb1e0e0443ebd6e8`, build_inputs `3da1ec91…`; `smoke-unpacked.txt` PASS; `pyz-check.txt` 13 True, 0 False (F7 `_work` calls `_remove_partial`); `asar-check.txt` F6, D-1, D-2 present | `[x]` |
| 31 | Deploy to the VM without a revert; guest hash equals the host's | `C:/Temp/zorivest/avkit-rc3-deploy.txt`, `avkit-rc3-guesthash.txt`: guest SHA-256 `b99aafc5…ebd6e8` equals the host's (round 3 files kept as `r3-avkit-rc3-*.txt`) | `[x]` |

## Round 5 — installer publisher focalia.ai (2026-11-09)

> Mat: "can we change the publisher in the installer to focalia.ai?" The installer takes its
> Publisher (Apps & Features) and both exes' CompanyName from `ui/package.json` `author`; its
> default copyright line also names the author. The copyright is pinned to the licence holder
> (`LICENSE`: Mat Banik), so only the publisher changes. The UAC prompt's "Unknown publisher"
> comes from the missing code signature and does not change. Round 4 receipts kept as `r4-*`.

| # | Task | Validation | Status |
|---|---|---|---|
| 32 | Red: AC-110.1 `author == "focalia.ai"`; new `test_exe_copyright_names_the_licence_holder` | `red5-py.txt`: 2 failed, 18 passed | `[x]` |
| 33 | Green: `author` `focalia.ai`; `copyright: Copyright © 2026 Mat Banik` in `electron-builder.yml` (main and clone; the clone's test keeps its rc.3 bump) | `green5-py.txt` 20 passed; `clone-py5.txt` 20 passed | `[x]` |
| 34 | Rebuild; smoke; pyz and asar checks; installer and app exe version info | `build.txt`, `build-record.json`: 340,365,336 B, SHA-256 `682d4d01ae1f6b35acc24574b219be0c3222505d63c824328d8cb0e51f73fda9`, build_inputs `f5658331…`; `versioninfo5.txt`: both exes CompanyName focalia.ai, copyright Mat Banik; `smoke-unpacked.txt` PASS; `pyz-check.txt` 13 True, 0 False; `asar-check.txt` F6, D-1, D-2 and the author present | `[x]` |
| 35 | Deploy to the VM without a revert; guest hash equals the host's | `C:/Temp/zorivest/avkit-rc3-deploy.txt`, `avkit-rc3-guesthash.txt`: guest SHA-256 `682d4d01…73fda9` equals the host's (round 4 files kept as `r4-avkit-rc3-*.txt`) | `[x]` |

## Review — Codex execution review (2026-11-09)

> Mat: "continue with codex review now". Loop `rc3-execution-2026-11-09-rc3-fixes` (execution,
> 6 rounds, 21M tokens), opened with the plan's §Review scope (`C:/Temp/av-kit/rc3-ledger-begin.txt`).

| # | Task | Validation | Status |
|---|---|---|---|
| 36 | Codex round 1 (read-only, high) | `C:/Temp/av-kit/dispatch/rc3-exec-r1-run.txt`: ledger recorded round 1 `approved`, 0 blocking, usage 5,976,320; report saved to `.agent/context/handoffs/2026-11-09-rc3-fixes-implementation-critical-review.md` | `[x]` |
| 37 | R1-F1 (Medium, non-blocking): `test_tts_fetch_tls.py` spies on `ssl.create_default_context` and asserts `cafile == certifi.where()` and that its context reaches `urlopen` (main and clone; test only, no rebuild) | `r1f1-mutant.txt`: real fetch passes, a no-`cafile` mutant fails by assertion at :70; `r1f1-green.txt` 29 passed; `r1f1-static.txt` ruff, format, pyright clean | `[x]` |
| 38 | Commit and push the fixes on `main` at the rc.2 version (Mat: "commit fixes first and push them, not sure if we can rebuild since github actions are out of minutes"). The rc.3 version bump, a rebuild from `main`, the tag and the release wait for Mat; the VM-tested installer (`682d4d01…`) came from `e0c1d0b` plus these fixes and matches no `main` commit | `git log -1`; `git status -sb` shows `main` even with `origin/main` | `[x]` |
