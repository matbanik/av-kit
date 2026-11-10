---
project: "2026-11-09-rc3-fixes"
status: "in_progress"
---

# Plan — rc.3 fixes from Mat's rc.2 VM test (quick plan)

**Authorization.** Mat, 2026-11-09: "fix the issues now and redeploy the rc.3 on the vm so I can
retest. If you need to do quick plan and execution in this session go ahead." This covers the
fixes, a local rc.3 build and the VM deploy. It does not cover a commit, push, tag or release:
those, and the vendor-distinct review that gates them, wait for Mat's word after the retest.

## Findings from the rc.2 VM test

1. **spaCy download fails on a fresh Windows install.** `_default_fetch` in
   `packages/infrastructure/src/avkit_infra/tts/assets.py` calls `urllib.request.urlopen` with
   Python's default context. On Windows that context loads only the roots already in the
   Windows store. A fresh install fetches roots lazily through CryptoAPI, which Python never
   triggers. The VM's store held 12 roots and lacked "USERTrust ECC Certification Authority"
   (github.com) and "ISRG Root X1" (release-assets.githubusercontent.com). The Hugging Face,
   Transcript and yt-dlp downloads already verify against certifi's bundle, which the backend
   ships (`certifi/cacert.pem`), so they worked.
2. **Transcript add is slow and silent.** `TranscriptService.add_channel` calls
   `extract_info(url)` non-flat, so yt-dlp resolves every video on every channel tab (about one
   second each) before the job exists. Measured on one channel: flat, 2.3 s; non-flat with
   only four videos per tab, 13.1 s. The page shows only a disabled button meanwhile. The
   Downloader shows "Adding — …" and then "Queued N job(s)".

## Changes

| # | Change | Files |
|---|---|---|
| F1 | `_default_fetch` passes `ssl.create_default_context(cafile=certifi.where())` to `urlopen`, the same trust the other downloads use. `certifi` becomes a direct dependency of avkit-infrastructure (it is already locked and bundled). | `tts/assets.py`, `packages/infrastructure/pyproject.toml`, `uv.lock` |
| F2 | `add_channel` asks for a flat extract; the folder title and the video ids read the same from it (`_playlist_from_info` and `_listed_videos` already flatten channel tabs, D-358). `ExtractCoordinator` keys its cache by `(url, flat)`, so a flat result never answers a non-flat request. | `services/transcript.py`, `services/extract.py` |
| F3 | TranscriptPage shows a status line while adding ("Adding — reading the channel's video list…") and after it ("Queued N videos from …"), like the Downloader. | `TranscriptPage.tsx` and its test |
| V | Version 0.1.0-rc.3 on Session 57's 13 surfaces, the two test constants and the notices source link (D-465 A's pattern), by exact byte replacement. In the clone only (see B). | as in Session 57 |
| B | Build `av-kit-Setup-0.1.0-rc.3.exe` offline with `build-rc3.ps1` (Session 57's script with the rc.3 installer name and record path). | clone's `ui/dist/` |
| D | Revert the VM to `clean`, deploy the installer to the guest Desktop, verify its hash. | — |

**Build source (Mat's ruling, 2026-11-09: "Clean clone + fixes").** The main tree held another
session's uncommitted capture work (MEU-128/129), then under review; it was committed as `8e79282`
during this session. rc.3 is `e0c1d0b` (rc.2) plus these fixes only: a plain local clone at
`C:/Temp/av-kit/rc3-src`, HEAD detached at `e0c1d0b` (no branch, no worktree), with the changed
files copied in byte for byte and the version bumped there. The main tree keeps the fixes at the
rc.2 version, so nothing here touches the other session's files (`openapi.committed.json` among
them).
The Downloader's own add is out of scope: Mat reports it fast.

## Tests (TDD)

- **F1 Red:** a test captures the `context` `_default_fetch` hands to `urlopen` and asserts it is
  an `ssl.SSLContext` whose CA list holds ISRG Root X1 and USERTrust ECC Certification Authority.
- **F2 Red:** a test records the `flat` argument of every `extract_info` call during
  `add_channel` and asserts only `True` is used; a coordinator test asserts a flat and a
  non-flat request for one URL reach the port separately.
- **F3 Red:** a vitest test asserts the adding status line appears while the POST is pending and
  the queued line after it resolves.
- Then the affected suites, ruff, pyright, UI typecheck, lint and tests.

## Not done here

Commit, push, tag `v0.1.0-rc.3`, the draft release, the release notes, the registers and the
Codex review. The rc.2 tag and draft stay as they are.

## Round 2 — Mat's rc.3 retest (2026-11-09)

Mat: "spaCy now downloads but when I hit gate on any of the models progress it is at 0% for very
long time looking like it is frozen"; the MP3 name "should be somethign like first 3 words from
the Text with dash followed by voice"; Transcript "adds playlist quickly but seems stuck and not
processing any transcripts." Rulings (AskUserQuestion): "Show retries on card (Recommended)",
"Lowercase slug (Recommended)".

Findings:

4. `ModelCatalogAdapter.download` calls `hf_hub_download` with no progress hook: it reports 0.0,
   then 1.0 when the whole file (80–330 MB) is on disk.
5. `TTSService._work` names the output `<job-uuid>.mp3` / `.wav`.
6. The guest log holds `transcript.blocked`, and one fetch of the same video from the host
   (same public IP through NAT) raises `IpBlocked`: YouTube refuses this network, which is not an
   rc.3 regression. The three retries wait 30 s each with nothing on the card, then the job
   pauses with the block message.

| # | Change | Files |
|---|---|---|
| F4 | `hf_hub_download(..., tqdm_class=...)`: a quiet tqdm subclass reports `n / total` to `on_progress` on both the HTTP and the Xet path (it defines `update_transfer`, so Xet uses one bar). `tqdm` becomes a direct dependency (already locked). | `model_manager/progress.py` (new), `model_manager/manager.py`, `pyproject.toml`, `uv.lock` |
| F5 | Output stem `<first three words>-<voice>`, lowercase, punctuation dropped, the word part at most 60 characters, `speech` when no word is left; `-2`, `-3`… when the WAV or MP3 name is taken. The WAV and MP3 share the stem. | `domain/tts.py`, `services/tts.py`, `test_tts_async.py` (its `files` helper lists the whole output folder, which is stricter) |
| F6 | While a blocked video waits to retry, the Processing job's `error_message` holds `retry_message(attempt, attempts, delay)` and the card shows it; it clears when the fetch ends (the block pause then writes its own message). A job starting a run clears an old message. No log line per retry: AC-115.7 pins one line per blocked video (`transcript.blocked`), so the per-retry log offered in the question waits for Mat. | `domain/transcript.py`, `services/transcript.py`, `TranscriptPage.tsx` and its test |

Then the clone takes the changed files byte for byte (the capture commit `8e79282` touches none of
them), the installer is rebuilt as rc.3, and the VM is reverted and redeployed.

## Rounds 3 to 5 (2026-11-09)

| # | Change | Files |
|---|---|---|
| R3 | D-1 and D-2 below: `lineMeetsLevel` shows a level and every more severe one; the Console opens at `app.log_level` (read once, a click wins, an unknown or failed answer keeps DEBUG); the Settings hint; spec rows `06-gui.md:342`, `gui-actions-index.md:114`. | `ConsolePanel.tsx`, `AppShell.tsx`, `SettingsPage.tsx`, `console-level-threshold.test.ts` (new), `console-polish.test.ts` |
| F7 | Mat: "wav and mp3 are being created even though only mp3 is selected". `_work` removes the WAV once the MP3 is encoded and the cancel check passes, through `_remove_partial` (a failed unlink logs `tts.cleanup_failed` and the job still ends Done). Source: `_inspiration/_tts_pseudo_logic.md:181` "Delete temp WAV after conversion". | `services/tts.py`, `test_tts_mp3_only.py` (new), `test_tts_async.py` |
| P | Mat: "can we change the publisher in the installer to focalia.ai?" `ui/package.json` `author` is `focalia.ai` (installer Publisher, exe CompanyName); `electron-builder.yml` pins `copyright` to the licence holder, Mat Banik. | `ui/package.json`, `ui/electron-builder.yml`, `test_release_packaging.py` |

## Review scope

The vendor-distinct execution review covers F1 to F7, R3 and P in the uncommitted main-tree delta.
The acceptance criteria these changes touch, and the families a blocking finding may cite:

- AC-27 (Console level buttons): AC-27.8 and AC-27.9 changed to the threshold by D-1.
- AC-55 (Transcript page): F3 and F6's card lines.
- AC-62 (TTS assets download): F1.
- AC-73 (model download): F4; AC-73.8's fake takes `tqdm_class` apart.
- AC-77 (TTS jobs): F5 and F7; AC-77.1 and AC-77.5 take the new names, and AC-77.5's
  uncancelled job keeps only the MP3.
- AC-110 (release metadata): P; AC-110.1's author changed at Mat's request.
- AC-115 (transcript failure reasons): F2 and F6; AC-115.7 (a retry logs nothing) holds.

## Decision Log

Mat, 2026-11-09: "I though that if I click debug I will see all messages including DEBUG, INFO,
WARNING, ERROR etc. Than whan I select INFO I will not see DEBUG but all others will be included.
… Run HDP for me and find out what the recommendation should be." Not part of the rc.3 fixes;
Mat accepted both recommendations on 2026-11-09; they are built as round 3 (task.md rows 19-24).

```yaml
decision_log:
  - id: D-1
    stage: execution
    question: "Console Level buttons: show the selected level only, or the selected level and everything more severe?"
    resolution: human
    class: product-preference
    chosen: "the selected level and above (DEBUG shows all; default DEBUG)"
    human_message_reference: "USER_EXPLICIT 2026-11-09 'recommendations to decisions are accepted, proceed as recommended'"
    source_tag: Research-backed
    precedents:
      - "docs/execution/plans/2026-08-20-p6-gui-console-polish/implementation-plan.md:78 — MEU-27 replaced MEU-26's threshold filter with exact match, from the Human words 'buttons … only the DEBUG events' (elided quote; full message not found in the repo)"
      - "docs/execution/plans/2026-08-20-p6-gui-console-polish/implementation-plan.md:327 — 'Keep dropdown + threshold' rejected because 'User asked for buttons + only DEBUG'"
      - "docs/build-plan/06-gui.md:342 — 'Exclusive level buttons … (exact token match; default DEBUG)'"
    research:
      engine: native
      sources:
        - "https://developer.android.com/studio/debug/logcat — level:INFO shows INFO and more severe (official docs)"
        - "https://docs.python.org/3/library/logging.html — setLevel passes messages at or above the level (official docs)"
        - "https://mailman.qos.ch/pipermail/logback-dev/2008-September/002829.html — logback LBCLASSIC-73: an exact-match level filter surprised users; greater-or-equal asked for"
        - "https://docs.oracle.com/middleware/12211/wls/WLACH/taskhelp/domain_log_filters/FilterLogMessages.html — threshold by default, exact level as an opt-in"
    reasoning: "Mat's model is the threshold every major viewer and Python's own logging use. The 2026-08 exact-match rule rests on an elided quote that can also be read as 'with DEBUG selected I see only…'; Mat's 2026-11-09 words are explicit and later."
  - id: D-2
    stage: execution
    question: "Settings → app.log_level is saved but nothing reads it: wire it, or remove it?"
    resolution: human
    class: product-preference
    chosen: "make it the level the Console opens at"
    human_message_reference: "USER_EXPLICIT 2026-11-09 'recommendations to decisions are accepted, proceed as recommended'"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/settings.py:77 — ('app','log_level') default INFO; rg finds no reader outside settings and the Settings page"
      - "_inspiration/_shared_patterns.md:93 — app.log_level listed as an app setting"
    research:
      engine: native
      sources:
        - "https://docs.python.org/3/library/logging.html — a level setting is a threshold"
    reasoning: "A setting that does nothing misleads. Using it as the Console's starting level gives it a visible job without dropping any lines from console.log or the ring."
```
