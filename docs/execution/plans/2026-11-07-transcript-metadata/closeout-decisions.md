# Closeout decisions (execution)

Execution leaves three questions to Mat, briefed under `.agent/docs/human-decision-protocol.md`. Each asks whether to register something this session saw but did not change, and where it goes. None blocks the commit. Filing an issue puts a row in the register, and attaching it to a session changes that session's scope, so it is Mat's call, not the coordinator's (memory: a brief keeps the do-nothing option).

Second run (2026-11-07, after commit `39ac742`). Mat asked for HDP again: "I'm leaning towards fileing and incorporating into existing sessions in this grouping". Each brief now has that option. The grouping places riders by shared file (D-242: "A rider needs a session already in that file"). Two recommendations follow the lean. D-363's departs from it, for the reason given in its brief.

**Ruling:** Mat, 2026-11-07: "all recommendations are accepted". D-361 is filed as a rider in Session 55, D-362 as a watch item in Session 57's gate, and D-363 in current-focus's debt queue. The records are each issue's `decision_log` in `known-issues.yaml`, the reflection's Decisions Log and the grouping's §1 and §3.

Precedent sweep: `C:/Temp/av-kit/s53-hdp-sweep.txt`. Research receipts: `C:/Temp/av-kit/s53-hdp-web-d361a.txt` to `-d363b.txt`, all from Pomera tavily.

## D-361: a bare channel URL in the download queue lists the channel's tabs, not its videos   [product-preference] [execution]

**Recommendation:** File it as `DOWNLOAD-BARE-CHANNEL-LISTS-TABS` (open, P3) and attach it as a rider to Session 55 `download-received-quality` (MEU-124). The fix applies D-354's ruling to the download add path: flatten a bare channel's tabs one level, as `FLAT_TABS` (D-358) already does for transcripts. Session 55 already works in the file that queues the videos, so the rider meets D-242's rule.

**What is known:**
- The download add path calls `extract_info` and queues one item for each id in `PlaylistInfo.video_ids` (`packages/core/src/avkit_core/services/download.py:177-186`).
- `_playlist_from_info` takes `video_ids` from the top-level `entries` (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:257-268`, called at `:469`).
- Row 0a's live measurement (D-353) found that a bare channel URL's top-level entries are its tabs (`entries: 3; _type {playlist: 3}`), so the download queue gets the tabs' ids as its "videos" (`C:/Temp/av-kit/s53-shapes.txt:24-28`). This is read from the code and the measured shape. No download was run.
- Session 55's contract names `services/download.py:213,235` (`docs/build-plan/06-gui.md:1582-1594`). The real quality is only known from the youtube adapter's download result (`adapter.py:486`), so its plan will probably edit `adapter.py` as well. That second file is my reading, not yet confirmed by a plan.

**Why not the others:**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ File it, P3, as a rider in Session 55 (MEU-124) | — | — | D-242 (grouping :268); D-354, D-358 (`implementation-plan.md:488`, `:529`); `services/download.py:177-186` |
| ⚠️ File it, P3, for the next triage only | Session 55 keeps its scope as planned | rc.2 ships with downloads and transcripts reading a bare channel two different ways. A later session reopens the same file. | D-344 |
| ⚠️ Its own MEU and session (a Session 55b) | Its own plan and review, separate from the quality column | A full plan and review cycle for a few lines in a file that Session 55 already has open | Grouping §7 calibration |
| ⚠️ Do nothing: leave it in this handoff's Deferred Items | No register row and no scope change | The next triage reads the register, not old handoffs, so the finding is lost | Handoff §Deferred Items |

**Precedent:** D-242 and D-99 place riders by shared file. D-354, Mat's ruling to flatten the tabs, set the rule for transcripts. D-339 filed non-blocking findings so the result isn't lost.

**Research:**
- [yt-dlp #11976](https://github.com/yt-dlp/yt-dlp/issues/11976): with `--flat-playlist`, a bare channel URL yields ids from all of the channel's tabs. People ask how to leave Shorts out, so "all tabs" is the expected default.
- [Nic's notes](https://notes.nicolasdeville.com/python/library-yt-dlp): Python callers using `extract_flat` handle the nested shape themselves, treating an entry whose `_type == 'playlist'` as a tab and reading its entries.
- [ytdlp.online](https://ytdlp.online/youtube-channel-downloader): each upload lives in exactly one tab (Videos, Shorts or Live), so flattening the tabs one level doesn't queue a video twice.
- [Super User 1752396](https://superuser.com/questions/1752396/how-to-download-all-videos-with-yt-dlp-from-a-youtube-channel-after-the-redesign): channel tabs date from YouTube's 2022 redesign, and yt-dlp changed its tab handling then.

**Reversibility / risk:** Two-way. The rider changes which items a bare channel URL queues, from three tab ids to the channel's videos. A URL that names a tab (`/videos`) is unchanged. If Session 55's plan finds that it doesn't touch the add path after all, its plan gate can move the rider out.

**If you do not answer:** Nothing is filed and Session 55's scope stays as it is. Session 54's prompt lists D-361 as open.

## D-362: the transcript queue E2E's seam reload failed once under load   [governance-value] [execution]

**Recommendation:** File it as `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` (MONITORING, P4) and attach it to Session 57 `release-rc2` as a watch item, with no code change now. Session 57's gate runs this test anyway. Its plan names the issue, and if W2-4 fails again there or in an earlier gate, the fix goes in before the release. The likely fix is to wait for the first load to settle before `page.reload()`.

**What is known:**
- Gate run 2's first attempt failed W2-4 ("E2E_HAPPY_PATH via E2E_SEAM") with `page.reload: net::ERR_ABORTED; maybe frame was detached?` (`ui/tests/e2e/transcript-queue.test.ts:177`). The other 10 tests passed.
- No row changed a file under `ui/`. On that attempt pytest took 305 s against 191 s on the rerun, and the Electron spec took 2.6 min against 22 s. The unchanged rerun passed 11 of 11. Round 2 judged the rerun sound and noted that load is not proven to be the cause.
- No remaining session edits `transcript-queue.test.ts`, so no rider fits by shared file. Session 57's gate is the next run of this test in every case.
- Receipts: `C:/Temp/av-kit/s53-gate-r2a/`.

**Why not the others:**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ File it as MONITORING, P4, and attach it to Session 57's gate as a watch item | — | — | `s53-gate-r2a/`; grouping :63 |
| ⚠️ File it in current-focus's debt queue only, like `E2E-CLIPBOARD-PRIMER-EMPTY` | Matches the grouping's existing E2E rows exactly | The release session's plan doesn't name it, so a recurrence there starts from nothing | Grouping :63, :65 |
| ⚠️ Fix it now as a rider: wait for the load state before the reload | The flake may stop before rc.2 | One failure can't show that a fix works. No remaining session is in that file, which breaks D-242. | Playwright #5111 |
| ⚠️ Do nothing: leave it in the handoff and the reflection | No register row | A later gate that hits it starts from nothing | — |

**Precedent:** `E2E-CLIPBOARD-PRIMER-EMPTY` was filed as MONITORING and placed before Session 57 (grouping :63). Session 53's RULE-4 sets how a gate handles such a failure: rerun once, keep the receipts and disclose both attempts.

**Research:**
- [Playwright #5111](https://github.com/microsoft/playwright/issues/5111): a maintainer traced `page.reload` `ERR_ABORTED; maybe frame was detached?` to a reload issued while another navigation was still in flight. That fits a slow first load under heavy load.
- [Playwright #34889](https://github.com/microsoft/playwright/issues/34889): the same error on `page.reload`, with several unrelated causes reported, so one failure doesn't identify which one this is.
- [Endform](https://endform.dev/blog/quarantine-flaky-playwright-tests): a retry runs on the same overloaded machine, and a pass on retry isn't a fix. The test still needs a ticket with an owner.
- [Trunk](https://trunk.io/blog/the-ultimate-guide-to-flaky-tests): track flaky tests in the issue tracker under a tag, and keep running them.

**Reversibility / risk:** Two-way. A watch item adds one line to Session 57's plan and no code. The risk is that it recurs in Session 57's gate and costs a rerun, which RULE-4 already handles.

**If you do not answer:** Nothing is filed and Session 57's scope stays as it is. Session 54's prompt lists D-362 as open.

## D-363: two older text paths into transcript storage aren't cleaned   [governance-value] [execution]

**Recommendation:** File it as `TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS` (TECH-DEBT, P3) in current-focus's debt queue, not as a rider in a session. This departs from your lean: no remaining session works in `services/transcript.py` or the caption adapter, and D-242 holds that a rider needs a session already in the file. The debt-queue placement keeps it inside this grouping as the E2E rows are, landing before Session 57 if wanted.

**What is known:**
- Round 2 notes that the `info.title` channel fallback (`packages/core/src/avkit_core/services/transcript.py:169`) and a separately supplied `TranscriptResult.title` aren't cleaned by D-360 (`2026-11-07-transcript-metadata-implementation-critical-review.md:168`).
- D-360's guard covers `VideoListing` (`domain/download.py:278`, `:295`). `TranscriptJob.channel_name` has no such guard, so a lone surrogate in an extract title, on a channel whose flat listing has no channel name, would still fail job creation as F1 did. That path predates this MEU, and this MEU made it rarer, since the listed channel name now comes first.
- The real caption adapter falls back to the video id when no title is given (`packages/infrastructure/src/avkit_infra/transcript/adapter.py:63-66`).
- The fix is small: reuse D-360's cleaner at both points, plus one real-storage regression (Session 53 RULE-1).

**Why not the others:**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ File it, P3, in current-focus's debt queue | — | — | D-242 (grouping :268); grouping :63, :65 |
| ⚠️ File it, P3, as a rider in Session 55 (your lean) | Lands on a named session's plan and review | Session 55 is already five layers (domain, service, database, API, GUI). This adds a second service and a storage regression in files it doesn't touch, against D-242. | D-242; `06-gui.md:1582-1594` |
| ⚠️ File it, P3, for the next triage only | No scope change in this grouping | It waits for the next triage, though the fix is known and small | D-344 |
| ⚠️ Do nothing: leave it in the review note | No register row | The note lives only in a review file that the next triage doesn't read | — |

**Precedent:** D-360 fixed the path that this MEU created. The grouping's debt-queue rows (:63, :65) are the in-grouping home for work that has no session in its files. D-344 filed a pre-existing observation rather than fixing it at closeout.

**Research:**
- [bpo-18814](https://bugs.python.org/issue18814): a string holding a lone surrogate fails `.encode('utf-8')` with "surrogates not allowed". The core developers preferred fixing the source over adding a general cleaner.
- [Armin Ronacher, "The Updated Guide to Unicode on Python"](https://lucumr.pocoo.org/2013/7/2/the-updated-guide-to-unicode): strings that may carry surrogates have to be resolved before they reach APIs that can't take them.
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html): validate values after parsing and before storage. Here that means cleaning at the two points where outside text enters, as D-360 did for the listing.

**Reversibility / risk:** Two-way. The failure needs a lone surrogate in an extract title together with a missing channel name, so P3 fits. A debt-queue item can be promoted to a rider later if a session ends up in those files.

**If you do not answer:** Nothing is filed and no session's scope changes. Session 54's prompt lists D-363 as open.
