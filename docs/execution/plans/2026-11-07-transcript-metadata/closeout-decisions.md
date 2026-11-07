# Closeout decisions (execution)

Execution leaves three questions to Mat, briefed under `.agent/docs/human-decision-protocol.md`. Each asks whether to register something this session saw but did not change. None blocks the commit. Filing an issue puts a row in the register that the next triage has to rule on, so it is Mat's call, not the coordinator's (memory: a brief keeps the do-nothing option).

## D-361: a bare channel URL in the download queue lists the channel's tabs, not its videos   [product-preference] [execution]

**Recommendation:** File it as `DOWNLOAD-BARE-CHANNEL-LISTS-TABS` (open, P3) for the next triage, with this session's measurement as its evidence and no code change now. D-354's ruling covered the transcript listing, and changing which videos a download job queues needs its own plan and review.

**What is known:**
- `extract_info` returns `_playlist_from_info(info)` for a playlist dict (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:469`), and `_playlist_from_info` takes `video_ids` from the top-level `entries` (`:257-268`).
- Row 0a's live measurement (D-353) found that a bare channel URL's top-level entries are its tabs: `entries: 3; _type {playlist: 3}`, each tab holding the videos (`C:/Temp/av-kit/s53-shapes.txt:24-28`).
- So a bare channel URL in the download queue gets the tabs' IDs as its "videos". This is read from the code and the measured shape. No download was run, because the brief forbids writing to YouTube and a test download was outside this plan.
- `FLAT_TABS` (D-358) already does the flattening for transcripts in `_listed_videos`. The same rule could serve downloads, but it would change which videos a download job queues.

**Why not the others:**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ File `DOWNLOAD-BARE-CHANNEL-LISTS-TABS`, open, P3; no code change | — | — | D-354, D-358 (`implementation-plan.md:488`, `:529`); `s53-shapes.txt:24-28` |
| ⚠️ Fix it in this session: apply FLAT_TABS in `_playlist_from_info` | The download side matches the transcript side now | A new plan amendment, Red and Green rows, a gate rerun and a round 3 review on a reviewed tree; it changes download behaviour that this plan kept unchanged (AC-122.6) | AC-122.6; ledger at 12,892,273 of 21,000,000 |
| ⚠️ Do nothing: leave it in this handoff's Deferred Items only | No register row, nothing for the next triage | The handoff is the only record, and the next triage reads the register, not old handoffs | Handoff §Deferred Items |

**Precedent:** D-339 (`2026-11-06-tts-load-fp16-reflection.md:130`) filed non-blocking findings so the result isn't lost. D-344 filed `TRACKED-FILES-HOLD-HOME-PATH` for the next triage rather than fixing it at closeout.

**Reversibility / risk:** Two-way. An issue row can be closed or reworded. If filing is wrong, the cost is one triage row.

**If you do not answer:** Nothing is filed. The finding stays in the handoff's Deferred Items, and Session 54's prompt lists D-361 as open.

## D-362: the transcript queue E2E's seam reload failed once under load   [governance-value] [execution]

**Recommendation:** File it as `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` (open, P4), citing the first attempt's receipts. Gate scripts are fail-fast, so a recurrence stops a later session's gate in the same way.

**What is known:**
- Gate run 2's first attempt failed W2-4 ("E2E_HAPPY_PATH via E2E_SEAM") with `page.reload: net::ERR_ABORTED; maybe frame was detached?` in `installTranscriptSeam` (`ui/tests/e2e/transcript-queue.test.ts:177`). The other 10 tests passed.
- No row changed a file under `ui/`. On that attempt pytest took 305 s against 191 s on the rerun, and the Electron spec took 2.6 min against 22 s.
- The unchanged rerun passed 11 of 11. Round 2 judged the rerun sound and noted that load is not proven to be the cause.
- Receipts: `C:/Temp/av-kit/s53-gate-r2a/`.

**Why not the others:**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ File `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE`, open, P4 | — | — | `s53-gate-r2a/`; handoff §Quality Gate Results |
| ⚠️ Fix it now, e.g. wait for the load state before the reload | The flake may stop | A UI test change outside this MEU's scope, with no way to show the fix works from one failure in many runs | — |
| ⚠️ Do nothing: leave it in the handoff and the reflection only | No register row | A later gate that hits it starts from nothing | — |

**Precedent:** D-344 filed a cross-cutting observation for the next triage rather than acting at closeout.

**Reversibility / risk:** Two-way. If filing is wrong, the cost is one triage row.

**If you do not answer:** Nothing is filed, and Session 54's prompt lists D-362 as open.

## D-363: two older text paths into transcript storage aren't cleaned   [governance-value] [execution]

**Recommendation:** File it as `TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS` (open, P3) for the next triage. The fix would reuse D-360's cleaner, but these are older paths that this MEU didn't add, and round 2 approved the delta without them.

**What is known:**
- Round 2 (`2026-11-07-transcript-metadata-implementation-critical-review.md:168`) notes that the `info.title` channel fallback (`packages/core/src/avkit_core/services/transcript.py:169`) and a separately supplied `TranscriptResult.title` aren't cleaned by D-360.
- `channel_name` was `info.title` before this MEU, so a lone surrogate in a channel's title could already fail job creation the way F1 did. This MEU made the path rarer, since the listed channel now comes first.
- The real caption adapter falls back to the video ID when no title is given (`infra/transcript/adapter.py:63-66`), per the same review note.

**Why not the others:**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ File `TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS`, open, P3 | — | — | Review round 2 note; D-360 |
| ⚠️ Fix it in this session: clean `info.title` and the result's title with `_clean_text`'s rule | Closes the last known surrogate path in transcripts | A plan amendment, a Red and Green row, a gate rerun and a round 3 review on a tree already approved | Ledger at 12,892,273 of 21,000,000 |
| ⚠️ Do nothing: leave it in the review note | No register row | The note lives only in a review file that the next triage doesn't read | — |

**Precedent:** D-360 fixed the path this MEU created. Session 50's rule covers raw values that reach a log, and these reach storage, not the Console.

**Reversibility / risk:** Two-way. If filing is wrong, the cost is one triage row.

**If you do not answer:** Nothing is filed, and Session 54's prompt lists D-363 as open.
