# Human gate decisions (planning)

These are the two questions this plan puts to Mat at the plan gate (`implementation-plan.md` §User Review Required), briefed under `.agent/docs/human-decision-protocol.md`. A brief here authorizes nothing until Mat's ruling is recorded under it, and each brief's sources go into the decision log.

## D-353: measure the URL shapes live, once, read-only   [externally-blocked] [planning]

**Recommendation:** yes, run the measurement once: four URLs, field presence only, before any code is written. D-223 says "the plan must measure", and today's evidence is yt-dlp's own recorded test expectations, read from its source. They've never been seen on this network, and YouTube changes these pages without notice. The cost is a handful of read-only page requests on endpoints the caption block doesn't name. It is also the only check of the session that looks at real YouTube, because the tests run on fakes either way.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ Measure once with `--live` | — | — | D-223; layered testing practice |
| ⚠️ Mat runs it later from another network, at MEU-125 | No request from this network now; it joins the Transcript check you already owe from another network | A wrong shape is found after this session's design is reviewed and committed | Memory of the RC1 checks: "Transcript from another network is still open" |
| ❌ Don't measure (do nothing): `--recorded` only, stated as `live: not measured` | No request at all; nothing can add to the 429 | D-223's "must measure" stays unmet, and the shapes are only yt-dlp's expectations. Issue 6006 shows flat results can differ. If the shape is wrong, titles stay IDs in production while every test passes | yt-dlp source; issue 6006 |

**Precedent:**
- D-223 (triage, `known-issues.yaml`, `TRANSCRIPT-TITLE-IS-VIDEO-ID`): "The plan must measure which URL shapes return titles." It applies directly, and this is the plan.
- Your brief: "A live measurement is a read-only request to YouTube. If the plan needs one, it comes to me as a Decision Brief."
- `YOUTUBE-CAPTIONS-IP-BLOCK` is open: 429 on `www.youtube.com/api/timedtext` from this network, while "listing a video's captions succeeds". The measurement doesn't call `api/timedtext`.

**Research:** native web search.
- Practice: [integration testing patterns](https://agentfactory.panaversity.org/docs/TypeScript-Language-Realtime-Interaction/testing-typescript-ai/integration-testing-patterns) describes mocks for speed, recorded fixtures for reliable CI, and occasional live calls to check that the fixtures are still accurate.
- Practice: [contract testing strategies](https://bdfinst.github.io/ai-patterns/contract-testing-strategies) makes recorded fixtures the CI default. No source I found addresses a third-party scraper specifically, where the target has no contract, so this is by analogy.
- Community: [yt-dlp issue 6006](https://github.com/yt-dlp/yt-dlp/issues/6006) reports that a flat title can differ when it holds a mention, and that dropping flat makes large listings much slower. It's closed, and it doesn't say whether that was fixed.

**Obviousness test (§4):** not obvious. It's a request to an outside service from a network with an open block, and your brief reserved it.

**Reversibility / risk:** a request can't be taken back, but it writes nothing and uploads nothing. It's about eight page requests, because the bare channel fetches up to three tabs and the watch page also fetches its player data. It downloads no media and requests no captions. If the code's shape is wrong, both options fail safe to today's display.

**If you do not answer:** row 0a runs `--recorded`, the receipt says `live: not measured`, the handoff repeats that, and no YouTube request is made.

**What the recommendation would authorize:**
1. Replacing `--recorded` with `--live` in row 0a, and nothing else.
2. One run of `measure-shapes.py --live` on `https://www.youtube.com/channel/UCTwECeGqMZee77BjdoYtI2Q/videos`, the same channel without `/videos`, playlist `PLav47HAVZMjnA3P7yQvneyQPiVxZ6erFS` and watch `jNQXAC9IVRw`, with `playlistend: 3`, no cookies and `download=False`.
3. A receipt listing which fields are present, never their values. A bot wall or 429 records that URL as `not run`, and it isn't retried.

It does not authorize: any retry, caption request, download or cookie use; any other URL; any write to YouTube.

**Decision (D-353).** Source: `USER_EXPLICIT`, 2026-11-07, Claude Code (VS Code) chat. Mat wrote:

> proceed, D-353 yes, D-354 Flatten the tabs now

This takes the recommendation and authorizes exactly the three items listed above it. Row 0a runs `--live` once, before the plan recheck, because D-354's ruling now depends on the nested shape. The receipt therefore also records, for each nested tab, whether it holds an `entries` list and which fields its inner entries have, still never their values.

## D-354: a bare channel URL whose channel has Streams or Shorts tabs   [product-preference] [planning]

**Recommendation:** no code change here; file `TRANSCRIPT-CHANNEL-HOME-NESTED-TABS` for the next triage. From yt-dlp's source, a URL such as `https://www.youtube.com/@chan` returns nested tab playlists when more than one of its tabs gives a result, and a sole tab directly (`_tab.py:2416-2417`). In the nested case, today's job then gets one item whose "video ID" is the channel's ID, and its fetch fails. That's a bug in which videos a job gets, not in what they're called. Neither issue names it, and fixing it changes a job's video set on a shape nobody has measured.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ File the issue, no code change | — | — | Session 52's D-337 and D-344 were filed the same way |
| ⚠️ Flatten the nested tabs now, in `_listed_videos` | A bare URL would get real videos and titles in this session | Adds streams and shorts to a job, with a video set you haven't ruled on; adds a design question and tests to one MEU; shape not measured unless D-353 is yes | `_tab.py:2354-2386`, `:2403-2425` |
| ❌ Do nothing, unfiled | No register change | The bug stays unrecorded, and a bare URL keeps giving a job that fails. It's visible to anyone who pastes a channel's home URL | `adapter.py:119-134` |

**Precedent:**
- D-241 (grouping §8): one MEU for one enumeration and one fake. Flattening would widen that.
- D-337 and D-344 (Session 52, your rulings): a neighbouring defect found while planning was filed for the next triage, not fixed in the session.
- `_tab.py`'s own message says to pass a tab's URL or the Uploads playlist for a single list, so a job's choice of tabs is a real product question.

**Research:** none beyond the source read. It's an internal scope call.

**Obviousness test (§4):** not obvious, because the flatten option is a product change to which videos a job holds.

**Reversibility / risk:** filing is reversible and adds one register entry. The plan's code keeps today's behaviour for this shape, except that the nested entry never takes a tab's title as a video title (AC-122.3).

**If you do not answer:** no issue is filed, the code behaves as in the recommendation, and the closeout says the question stayed open.

**What the recommendation would authorize:**
1. Row 5 files `TRANSCRIPT-CHANNEL-HOME-NESTED-TABS` with `tools/issue_triage.py add`, status open, for the next triage. If D-353 is yes, its text cites what the measurement found for the bare channel. Otherwise it says the shape is from source only.

It does not authorize: flattening, adding Streams or Shorts to a job, or any change to `_unique_preserve_ids`.

**Decision (D-354).** Source: `USER_EXPLICIT`, 2026-11-07, Claude Code (VS Code) chat. Mat wrote:

> proceed, D-353 yes, D-354 Flatten the tabs now

This takes the alternative, not the recommendation. It authorizes flattening the nested tabs in `_listed_videos`, so a transcript job from a bare channel URL holds the videos of each tab yt-dlp returns, Streams and Shorts included (`FLAT_TABS`, D-358, AC-122.18). No issue is filed. It doesn't change `_unique_preserve_ids` or any download path, which the option didn't name. The recommendation's reasoning above stays as written. The amendment goes to one recheck round of the plan review before row 0.
