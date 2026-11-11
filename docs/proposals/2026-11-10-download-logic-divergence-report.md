# Download logic: av-kit vs yt-dlp_GUI — why `gKcOjnDJfzk` failed

**Date:** 2026-11-10
**Video:** <https://www.youtube.com/watch?v=gKcOjnDJfzk>. About 2 h long. The best resolution is 464×262, labelled "240p".
**Question:** av-kit showed a bare "Failed" and wrote nothing to its logs. Checking SABR, forcing SABR and Firefox cookies did not help. `P:\yt-dlp_GUI\youtube_downloader.exe` downloaded the video. Why is the logic not the same?

## 1. Short answer

1. **The two apps' format-fetching logic is nearly the same, because av-kit copied it.** av-kit's `COOKIE_EXTRACTOR_ARGS`, `SABR_EXTRACTOR_ARGS`, `COOKIE_AUDIO_SELECTOR` and the audio selector table were copied from yt-dlp_GUI word for word. Both pin YouTube's player clients to `tv`, `web_safari`, `web` when cookies are on.
2. **That pinned client list is what fails, in both apps, for this video, today.** In repeated probes only the `visionos` client returns playable formats. `tv` returns YouTube's *"The page needs to be reloaded."* `web_safari`, `web`, `tv_samsung` and `web_embedded` return *"Requested format is not available"*. That happens with or without cookies, and on both yt-dlp versions. yt-dlp's **own default** client choice picks `visionos` and succeeds every time.
3. **yt-dlp_GUI probably got through at 10:31 because of what YouTube served at that moment and its JS setup, not better logic.** Two things favoured it. It runs a JS runtime (Node, with the EJS solver bundled), which can solve the `tv`/`web` challenges. And YouTube's SABR experiment changes from one request to the next. Run again now with the GUI's exact options on the GUI's own yt-dlp build, it fails the same way (§3, probe E).
4. **The bare "Failed" is an av-kit UI bug, separate from the download failure.** The backend stores yt-dlp's error text, and the API returns it. The Downloader page never reads it. The log file is off by design, and the yt-dlp logger throws away the message text.
5. **SABR check and SABR force could not help.** In both apps, SABR only limits the quality menu and blocks queued jobs. It never changes the options passed to yt-dlp. The 360p job already passed the SABR check, so forcing SABR did nothing to it.
6. **Firefox cookies could not help either.** Choosing Firefox (or any cookie mode) switches the clients to the failing `tv/web_safari/web` set. Separately, the Firefox cookies are stale: YouTube flags them as rotated and yt-dlp quietly continues without logging in.

## 2. Evidence: probes run on this machine

The probes only simulated (`skip_download`); nothing was downloaded. The scripts and outputs are in the session scratchpad: `ab_probe.py` and `client_probe.py`.

### 2a. av-kit's exact options, one change at a time (av-kit's yt-dlp 2026.10.26, no JS runtime)

| Case | Options | Result |
|---|---|---|
| A | **av-kit as shipped:** Firefox cookies, `player_client=[tv,web_safari,web]`, `bestvideo[height<=360]+bestaudio/best[height<=360]` | **FAIL**: The page needs to be reloaded. |
| B | A + `js_runtimes={'node':{}}` | **FAIL**: The page needs to be reloaded. |
| C | A without cookies | **FAIL**: The page needs to be reloaded. |
| D | A **without the `player_client` override** (yt-dlp picks the clients) | **OK**: `134+251`, height 262 |
| E | The GUI's options: Firefox, GUI clients, Node, HLS selector | **FAIL**: Requested format is not available (n-challenge failed, `tv` formats SABR-skipped, "only images available") |

### 2b. The same cases on yt-dlp_GUI's own build (2026.04.04 nightly, `yt_dlp_ejs` 0.8.0)

| Case | Result |
|---|---|
| A | **FAIL**: Requested format is not available (n-challenge failed, `tv` formats SABR-skipped) |
| B, C, E | **FAIL**: The page needs to be reloaded. |
| D | **OK**: `134+251`, height 262 |

The yt-dlp version doesn't change the outcome. The failure message alternates between two values from one run to the next, which is the per-request SABR experiment showing through. Only removing the client override fixes it every time.

### 2c. One client at a time (av-kit's yt-dlp, with and without Firefox cookies)

| Client | No cookies | Firefox cookies |
|---|---|---|
| `tv` | The page needs to be reloaded. | The page needs to be reloaded. |
| `web_safari` | Requested format not available | Requested format not available |
| `web` | Requested format not available | Requested format not available |
| `tv_samsung` | Requested format not available | Requested format not available |
| `web_embedded` | Requested format not available | Requested format not available |
| **`visionos`** | **OK 134+251** | **OK 134+251** |

yt-dlp 2026.10.26 picks its default clients itself (`yt_dlp/extractor/youtube/_video.py:143-145, 2972-2977`):
- `_DEFAULT_CLIENTS = ('tv_samsung','visionos','web')`
- `_DEFAULT_JSLESS_CLIENTS = ('visionos',)`, used when no JS runtime is found
- `_DEFAULT_AUTHED_CLIENTS = ('web_embedded','tv_samsung','web')`, used when logged in

**Any hard-coded `player_client` list replaces this choice.** Both apps' cookie-mode list leaves out `visionos`.

There is also a quiet side effect. yt-dlp shows its *"No supported JavaScript runtime"* warning only when no `player_client` is requested (`_video.py:2994`). So the override also hides the one warning that would have explained the problem.

## 3. Side-by-side diff of the download logic

File references: **GUI** = `P:\yt-dlp_GUI\youtube_downloader.py`; **AK** = `packages/infrastructure/src/avkit_infra/youtube/adapter.py` unless another file is named.

| # | Area | yt-dlp_GUI | av-kit | Matters for this video? |
|---|---|---|---|---|
| 1 | Call style | Python `YoutubeDL.download([url])` on a worker thread (GUI:2953-2970) | Python `YoutubeDL.extract_info(url, download=True)` (AK:504-505) | No |
| 2 | yt-dlp version | 2026.04.04 nightly, `yt-dlp[default]` (`build.bat`) | 2026.10.26; plain `"yt-dlp"`, no `[default]` extra (`packages/infrastructure/pyproject.toml:12`, `uv.lock:3359`) | No (§2b) |
| 3 | **JS runtime** | `js_runtimes={'node':{}}` (GUI:1222). Node 26 on PATH. `yt_dlp_ejs` solver bundled in the exe | **Not set.** yt-dlp defaults to `deno`, which isn't on PATH (`~/.deno/bin` only). `yt_dlp_ejs` not installed. The packaged backend has no solver script (`packaging/avkit-backend.spec`) | **Yes, partly.** Without JS, `tv/web*` can never solve the n-challenge, so av-kit can't win even when YouTube serves those clients well |
| 4 | **player_client, cookie mode** | `['tv','web_safari','web']` (GUI:961-967) | `['tv','web_safari','web']` (AK:67-71), copied | **Yes, the root cause.** Leaves out `visionos`, the only working client today |
| 5 | player_client, no-cookie mode | `android, tv, ios` + `player_skip` + `skip:[hls,dash]` (GUI:969-977) | Same, copied (AK:72-80) | Would fail too. `android/ios` need a PO token, `tv` fails |
| 6 | Dead extractor args | `include_hls_manifest` / `include_dash_manifest`: not real YouTube args | Copied, so also dead | No |
| 7 | **Video selector, 360p, cookies** | `best[height<=360][protocol=m3u8_native]/best[height<=360][protocol=m3u8]/best[protocol=m3u8_native]/best[protocol=m3u8]/worst` (GUI:1029-1044). Ends in **`/worst`**, needs no merge | `bestvideo[height<=360]+bestaudio/best[height<=360]` (AK:102-110). **No catch-all, needs an ffmpeg merge** | Somewhat. The GUI's last `/worst` accepts nearly anything. av-kit's string has no last resort |
| 8 | Video selector, 360p, no cookies | `best[height<=360]/best[height<=480]/best` | Same as #7 (cookie mode doesn't change it) | — |
| 9 | Audio selectors | Table (GUI:994-1004); HLS-only selector in cookie mode | Same table and cookie selector, copied (AK:53-66) | No (this was a video job) |
| 10 | MP3 postprocessor | `FFmpegExtractAudio` mp3/192 (GUI:1134-1160). Added **twice**, a GUI bug | **None.** "standard_mp3" is only a selector name, so an "MP3" job saves `.m4a`/`.webm` | Separate av-kit bug |
| 11 | `merge_output_format` | `'mp4'` | Not set | No |
| 12 | Retries | `retries`, `fragment_retries`, `extractor_retries` = 5; HTTP backoff `min(4**n,60)` | yt-dlp defaults (10/10/3) | No |
| 13 | Network tuning | `socket_timeout=10`, `http_chunk_size=1 MiB`, `concurrent_fragment_downloads=3`, sleep 0.5–1 s, Chrome-91 User-Agent, `nocheckcertificate=True` | None | No |
| 14 | Error tolerance | `ignoreerrors=True`; `ignore_no_formats_error=True` in cookie mode (GUI:941, 1248-1250). Success = the file exists on disk (GUI:1667-1800) | Neither. A yt-dlp `DownloadError` raises and the job becomes Failed | Changes *how* failure shows, not *whether* it happens |
| 15 | Cookie tuple | `('firefox',)` | `('firefox', None)` (AK:421) | No (same meaning) |
| 16 | Checks before download | Add-time extraction **with** the cookie/client options; `check_quality_before_download` pass | Add-time extraction **without** cookies or `extractor_args` (AK:468-477), so it **succeeds through `visionos`** and the job is queued; the download then uses the failing clients | Explains why the job queues fine and fails later |
| 17 | Fallback on failure | 403 → steps down quality on the next Start (GUI:3392-3434). In practice seldom reached because of #14 | **None.** One attempt, manual reset (`services/download.py:319-343`) | Neither tries another client |
| 18 | SABR effect | Limits menus to 360p / MP3+M4A; rewrites queued items (GUI:3813-3939). **No `ydl_opts` change** | Moves jobs to QualityBlocked unless 360p/Lowest or MP3/M4A (`services/download.py:51,73-76,383-398`). **No `ydl_opts` change.** The check probes `dQw4w9WgXcQ` with the no-cookie options, not your video | Can't fix a client-selection failure |

## 4. Why av-kit showed "Failed" and logged nothing

The error text exists, but four separate gaps hide it:

1. **The UI doesn't read the field.** `adapter.py:517` stores `DomainError(str(exc))`, and `services/download.py:544-549` saves it to `download_jobs.error_message`. The API returns it (`routes/downloads.py:56`). But `useDownloadQueue.ts` `DownloadListItem` has no `error_message` field, and the `DownloaderPage.tsx` card mapping never sets `errorMessage`. So `QueueCard.tsx:277-278` falls back to `META_PLACEHOLDER` (`'—'`). Transcript and TTS pages *do* show their `error_message`.
2. **The yt-dlp logger drops its text.** `_YtDlpLogger._scan` (`adapter.py:315-340`) logs only when `yt_dlp_debug` is on, as `debug("yt-dlp", message=...)`. The Console keeps only `CONSOLE_FIELDS = (job_id, video_id, variant_id, device, error, detail, request_id, route)` (`services/health.py:47-56`). `message` isn't in that list, so even debug mode shows bare `yt-dlp` lines.
3. **A failed download logs nothing.** `_run_one` and `_finish` log nothing on failure. The only download log event is the success line (`adapter.py:546`).
4. **console.log is off.** `app.log_to_file='false'` was set 2026-11-03 22:55. That matches the file's last write. Only ERROR/CRITICAL lines persist regardless (`health.py:61-62`), and a failed download produces none.

For comparison, yt-dlp_GUI with debug on (your setting) sends every yt-dlp `warning` and `error` line to its console widget (GUI:21-98, 927-933). There you would have seen *"The page needs to be reloaded"* or the n-challenge and SABR warnings.

## 5. Recommended changes in av-kit, in priority order

| # | Change | Fixes |
|---|---|---|
| R1 | Stop pinning `player_client` in cookie mode; let yt-dlp choose its defaults. Or, at the least, add `visionos` to the list. If a fixed list is kept for members-only HLS, retry once with no `extractor_args` when the first attempt fails | This video and the whole class like it (root cause, §2c) |
| R2 | Make a JS runtime available. Either ship deno, or set `js_runtimes` to deno on its known path or to Node. Add `yt-dlp[default]`, which pulls in `yt-dlp-ejs`, and collect its `.js` files in `avkit-backend.spec` | The `tv`/`web` clients and full format lists; parity with the GUI |
| R3 | Show `error_message` on Failed Downloader cards (`useDownloadQueue.ts`, `DownloaderPage.tsx`) | The bare "Failed" |
| R4 | Log the failure: a `download.failed` event with the `error` field (a `CONSOLE_FIELDS` member) at WARNING or ERROR. Also put `_YtDlpLogger` warnings and errors in a kept field such as `detail` | Empty logs |
| R5 | Give the video selector a last resort: `.../best/worst`, or `bv*[height<=N]+ba/b[height<=N]/b` | Failures caused by the selector alone |
| R6 | Add the `FFmpegExtractAudio` postprocessor for `standard_mp3` / `high_m4a` | "MP3" jobs that don't produce MP3 files (separate bug) |
| R7 | Run the add-time check with the same cookie and client options as the download, or drop the claim that queuing proves the job can be downloaded | A job that queues fine, then fails |
| R0 | Do nothing; tell users to switch cookie mode or use the GUI | Nothing. Same-class videos keep failing silently |

R1 alone would have made this download succeed (probe D). R3 and R4 would have made the failure readable.

## 6. Follow-up: Check SABR shows nothing, and av-kit logs much less

### 6a. Check SABR gives a wrong answer, and the page doesn't show the answer it gives

I ran av-kit's exact probe on 2026-11-10: `SABR_EXTRACTOR_ARGS` (android/ios/tv) against `SABR_PROBE_URL`. yt-dlp **did** report SABR, twice:

> `Some android client https formats have been skipped as they are missing a URL. YouTube may have enabled the SABR-only streaming experiment for the current session.` (and the same for `ios`)

**av-kit still returns Inactive.** `SABR_LOG_NEEDLES` (`adapter.py:81-85`) looks only for `require a gvs po token`, `android client sabr formats require` and `ios client sabr formats require`. Current yt-dlp no longer uses that wording. This list was copied from the GUI's *real-time logger* phrases (GUI:77-84). The GUI's *Check button* probe (`detect_sabr_mode`) also matches the broader `'sabr'`, `'missing a url'`, `'forcing sabr'` (GUI:3717), plus a "no direct HTTPS URLs" test. av-kit did not copy that part.

**The page then shows nothing for Inactive.** The `sabr-status` line is `hidden={!sabrActive}` (`DownloaderPage.tsx:664`). The page never renders `checked_at` or `source`. `run()` (`DownloaderPage.tsx:386-397`) shows a message only when the request throws. So a check that succeeds and returns Inactive changes nothing on screen.

**Nothing is logged either.** `check_sabr` (`services/download.py:345-356`), `check_sabr_status` (`adapter.py:555-561`) and the route (`routes/downloads.py:101-108`) have no log call. The yt-dlp warnings above reach `_YtDlpLogger._scan` and are dropped (§4, item 2).

### 6b. Why the GUI's console shows many more lines

| Source of lines | yt-dlp_GUI | av-kit |
|---|---|---|
| App's own log calls | `log_message(...)`: **279 calls**, covering steps, progress every 5 s, "Finalizing…", errors with troubleshooting hints, SABR and cookie diagnostics | **4** in the download path: `add_to_queue_extract_start`, extract done, duplicate skip, success (`services/download.py:178-199`, `adapter.py:546`). Nothing on failure, on SABR check, or on progress |
| yt-dlp's own lines | `YtDlpLogger` forwards every debug/info/warning/error line as `[yt-dlp] …` when `yt_dlp_debug` is on (yours is) (GUI:21-98, 927-933) | `downloader.yt_dlp_debug` defaults to `False` (`services/settings.py:57`). It isn't in your DB and **there is no UI control for it** (only the API schema has it). Even when on, the text goes in a `message=` field that `CONSOLE_FIELDS` strips, so you get bare `yt-dlp` lines (`health.py:47-56`). It is read once at backend start (`wiring.py:149`) |
| Level setting | `log_level=DEBUG` filters the console | `app.log_level='DEBUG'` is stored but nothing in `packages/` reads it |
| To disk | None (console widget only) | `console.log` only when `app.log_to_file` is on (it's off) or the level is ERROR/CRITICAL |

Additional recommendations:

| # | Change |
|---|---|
| R8 | Widen `SABR_LOG_NEEDLES` to the GUI's probe set (`sabr`, `missing a url`, `forcing sabr`, `po token`) |
| R9 | Always show the check result: "SABR inactive — checked 12:47" as well as active; show `checked_at` and `source` |
| R10 | Log `download.sabr_check` with mode, source and the matched warning (in `detail`) |
| R11 | Add a "yt-dlp debug output" toggle in Settings, put the logger's text into a kept Console field, and apply the toggle without a backend restart |
| R12 | Log each job's start, progress milestones and failure (with `error`) so the Console tells the story of a download, as the GUI's does |

## 7. Limits

- The failed row was gone from the database (0 rows in `download_jobs`), so av-kit's actual stored error text could not be read. The cause is shown by re-running av-kit's exact options (§2a, case A), not from the original row.
- Why the GUI succeeded at 10:31 is inferred: Node+EJS plus YouTube's per-request SABR variation. The same GUI options fail now (§2b, E). Retrying the video in the GUI now would confirm this.
- The two sides were analysed by two parallel read-only subagents. I spot-checked the key line references (adapter options, the logger, `CONSOLE_FIELDS`, the `QueueCard` placeholder, the missing `error_message` in the downloader feature, the absence of postprocessors and `js_runtimes`).
