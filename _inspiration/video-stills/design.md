# Video stills and image export — agent-first design

> **Date:** 2026-11-09 · **Status:** inspiration design, not a plan. MEU ids, ACs and build-plan
> rows are assigned when a planning session adopts it. · **Research:** `pomera_web_search`
> (tavily, exa), receipts `C:/Temp/av-kit/stills-research-{01..12}-*.md`. Local receipts
> `C:/Temp/av-kit/stills-precedent-sweep.txt`, `stills-local-facts.txt`, `-2.txt`, `-3.txt`,
> `stills-precheck.txt`. · **Human decisions:** five, D-1 to D-5 (§13), ruled 2026-11-09: "all
> recommendations accepted, proceed". · **Grouping:**
> `.agent/context/grouping/2026-11-09-video-stills-session-grouping.md` (MEU-133 to MEU-136).

## 1. The ask

> "Also since we have ffmpeg already in av-kit are we able to grab screenshots from video with the
> agent with it or ffmpeg still needs to be used directly for that. This is for review of meeting
> vidoes or footage from security cameras as an example" (Mat, 2026-11-09)

> "Do web resesearch into each feature and create design doc in _insperiation. Run HDP for each
> decision needed when creating the design from existing art and code. Goal is to design something
> lighweight and with specific purpose in mind rather than going after all bells and wisels."
> (Mat, 2026-11-09)

The earlier answer in this session was no. An agent cannot get a still from a video through av-kit
today. `avkit_convert` can only compress, cut and extract audio, MCP has no probe, and agents call
ffmpeg directly (L-1, L-2). The same question asked which other image features agents need beyond
crop. §4 answers that from usage.

**Three purposes set the scope.** Anything that serves none of them is deferred.

| Purpose | What the agent must do | The hard part |
|---|---|---|
| **Meeting video review** | Find what was on screen at a moment, such as a slide, a demo or a whiteboard, and quote the time. | Picking times. A transcript time or a coarse overview does that. |
| **Security footage review** | Find when something happened in hours of mostly static footage, then pull the evidence frame. | Coverage. Hours of video cannot be viewed frame by frame. |
| **Agent image changes** | Turn a shot into a deliverable: smaller, a different format, metadata removed. | Size. Usage shows this is the most common edit after crop (§4). |

## 2. The shape in one screen

| Agent need | What av-kit adds | API | MCP | GUI |
|---|---|---|---|---|
| **Know the video.** Duration, size and fps before choosing times. | **Probe.** Wraps the existing `MediaPort.probe`. | `POST /conversions/probe` | `avkit_convert probe` | — |
| **See the whole video at once.** An index, not evidence. | **Sheet.** One PNG shot with a grid of frames, each stamped with its time, plus a cell→time map in the response. Calling it on a narrower range zooms in. | `POST /captures/sheet` | `avkit_capture sheet` | The shot appears on the Capture page (D-5) |
| **Pull the evidence.** A full-resolution frame at an exact time. | **Frames.** One PNG shot per time, at explicit times or N evenly spaced. | `POST /captures/frames` | `avkit_capture frames` | The shots appear on the Capture page |
| **Make a deliverable smaller.** | **Export.** A new shot that is resized and re-encoded (PNG, JPEG or WebP), with metadata removed (D-3). | `POST /captures/{id}/export` | `avkit_capture export` | — (D-5) |

**The review loop** applies to both footage purposes:

1. `probe` the video to get its duration.
2. `sheet` the whole video, then view it.
3. `sheet` the range between the two cells that bracket the event. Each step narrows the range 9×.
4. `frames` at the chosen cell times, then view them with `image` (region and `max_edge` exist, MEU-128).
5. `crop` (MEU-130) or `export` the evidence.

The agent quotes the times in the **response**, never a time it read off a picture (R-6). The rule
from Mat's camera work holds: *"The AI is a search index. It is never the evidence."* (L-14). The
sheet is the index, and the full-resolution frames are the evidence.

**Every output is a capture shot in the inbox,** so region view, crop, annotate and the Capture page
work on it unchanged. The video itself is never copied or changed.

## 3. Local facts

| # | Fact | Evidence |
|---|---|---|
| L-1 | `avkit_convert` has only three `add` kinds: compress, cut, extract. It has no frame grab and no probe action. | `mcp-server/src/toolsets/convert.ts:42-73`, `:85-102` |
| L-2 | `FFmpegAdapter.probe` already returns `MediaInfo` (duration, container, codecs, width, height, fps, streams) from ffprobe JSON. No route or MCP action exposes it. | `packages/infrastructure/src/avkit_infra/media/adapter.py:403-426`; `domain/progress.py:100-114`; route list `routes/conversions.py:149-266` |
| L-3 | `CaptureService` is wired with only the capture, annotate and settings ports. It has no `MediaPort`. `ConversionService` gets the same `FFmpegAdapter`, which resolves the ffmpeg path live. | `packages/api/src/avkit_api/wiring.py:152-155`, `:215`, `:217-222` |
| L-4 | Convert is a queue (add, start, poll). Capture calls are synchronous and return the shot. | `convert.ts:11`, `:85-102`; `capture.ts:35-38`; `routes/captures.py:244` |
| L-5 | Import (MEU-129) is the precedent for writing a file into the inbox: a `.avkit-tmp` temporary file, `CAPTURE_FILE_LOCK`, a unique name, register under a source, fixed error messages that name no path. | `services/capture.py:61`, `:78`, `:94`, `:449`, `:549` |
| L-6 | `CaptureSource` ends with `Import`. Crop (MEU-130, approved plan) adds `Crop` with no register wire value (D-484). | `domain/enums.py:209-219`; `domain/wire.py:89-93`; `docs/execution/plans/2026-11-08-capture-crop-copy/implementation-plan.md:170`, `:245` |
| L-7 | The MCP `image` action already takes a region and `max_edge` (64–2576) and fails past 7.8 MB with a hint to pass them. | `capture.ts:12`, `:30-31`, `:189-198` |
| L-8 | The capture adapter already draws text with a resolved TrueType font (falling back to Pillow's default) and writes JPEG/WebP at `LOSSY_QUALITY = 90`. | `packages/infrastructure/src/avkit_infra/capture/adapter.py:56`, `:132-143`, `:226-234`, `:475-479` |
| L-9 | Each `withDesc` action carries the M7 markers. Capture's shared Prerequisite line says "local screen grab or inbox files", which a video path does not fit. | `capture.ts:35-38`; `convert.ts:11-12`; `.agent/docs/emerging-standards.md` M7 |
| L-10 | Named deferrals this design touches: "ShareX uploaders, after-upload, OCR, GIF, **video**, scrolling capture — Out of product" (screen *recording*), and "Downloader / **Convert → Capture handoff** — Would reopen those pages". | `docs/build-plan/09-screenshot-capture.md:1091`, `:1092` |
| L-11 | The crop design deferred "resize and cover-crop, rotate and flip, a crop format option, persisted crop provenance". Export reopens the first and third. | `09-screenshot-capture.md:1097`; `_inspiration/capture-crop/design.md:327-340` |
| L-12 | Convert defers a timeline player and subtitle extract. It returns "paths and status, never media bytes". Cut accepts `HH:MM:SS.mmm` or seconds. | `docs/build-plan/08-video-conversion.md:170`, `:179`, `:516`, `:544` |
| L-13 | `P:/ffmpeg` (the presentation work) grabbed `tMMmSS.png` stills with input seek and stacked a 2×2 sheet with `xstack`, all by direct ffmpeg calls. | session receipts in `stills-precedent-sweep.txt` |
| L-14 | `P:/carmen/camera` built its own review set: input-seek grabs, a contact strip labelled `HH:MM:SS`, keyframe-only scoring (`-skip_frame nokey`). Its strategy says the AI is a search index, never the evidence. | `P:/carmen/camera/tools/make_review_set.py:54`, `:63-75`; `door_scan.py:37`, `:73`, `:85`; `AI_ANALYSIS_STRATEGY.md:18` |
| L-15 | The video conversion pseudo-logic already sketches an ffprobe analysis step before any operation. | `_inspiration/_video_conversion_pseudo_logic.md:32-54` |
| L-16 | The next free MEU id on `main` is MEU-133. Only the `main` worktree exists, and no doc claims MEU-133 or higher. | `C:/Temp/av-kit/stills-precheck.txt` |

## 4. How agents work with images and video here today

The counts cover distinct shell commands and script bodies across 1641 Claude Code transcripts on
this machine (receipt `stills-precedent-sweep.txt`; the script is in the session scratchpad).
Survey scripts that name every operation are excluded.

| Operation | Uses | Read |
|---|---|---|
| `ffprobe` | 118 | Agents inspect media often. Probe is cheap to expose (L-2). |
| Video frame grab | 4 | Rare today, but both real reviews (L-13, L-14) needed it and built it by hand. |
| Contact sheet from video | 3 | The same two projects. |
| Scene or change detection | 0 | Not used. Carmen wrote its own scorer instead (L-14). |
| Resize (magick 26, Pillow 36) | 62 | **The most common edit.** It is mostly for size, not for viewing. Viewing is covered by `max_edge` (L-7). |
| Quality, format and strip (magick 20, Pillow 43) | 63 | Re-encoding to shrink a file or change its format. It usually goes with resize. |
| Crop (magick 16, Pillow 27) | 43 | Covered by MEU-128 and MEU-130. |
| Paste or canvas (Pillow) | 43 | Mostly figure building inside larger scripts. Append or montage: 7. |
| `-extent` / pad | 13 | Mostly for social thumbnails. |
| Rotate or flip (magick 7, Pillow 9) | 16 | Mostly EXIF upright, which import already handles. |
| Compare / diff | 4 | Rare. |
| Trim | 2 | Rare. |
| PDF rasterise | 30 | Outside this design (§9). |
| OCR | 8 | Outside this design (§9). |

**Reading.** The video side is low-volume but high-value: each review that happened needed custom
code. On the image side, after crop, the one edit with real volume is resize plus re-encode for a
smaller deliverable. Everything else is rare or already covered.

## 5. Research findings

| # | Finding | Label | Source |
|---|---|---|---|
| R-1 | Video MCP servers converge on three calls: **info/probe**, **frames at explicit timestamps**, and **N evenly spaced frames in a start/end window**, with a hard cap (mcp-video-reader caps at 20, default 10). Several return paths, not bytes. | practice | [mcp-video-reader](https://github.com/lawriec/mcp-video-reader); [media-mcp](https://github.com/woosal1337/media-mcp); [video-use](https://github.com/therealfloatdev/video-use); [video-vision-mcp](https://pypi.org/project/video-vision-mcp/0.3.0/); [GetVideoFrames](https://getvideoframes.com/developers/mcp/) |
| R-2 | "Ears always, eyes only when ears fail": use the transcript to pick times, then grab frames at those times. | practice | [media-mcp](https://github.com/woosal1337/media-mcp) |
| R-3 | Input seek (`-ss` before `-i`) is fast and **frame-accurate when transcoding** (since FFmpeg 2.1). A time between frames gives a real nearby frame. Nothing is written past the end. | authority | [FFmpeg wiki: Seeking](https://trac.ffmpeg.org/wiki/Seeking); [ffmpeg-cookbook](https://ffmpeg-cookbook.com/en/articles/extract-frames); [video.stackexchange](https://video.stackexchange.com/questions/37425/ffmpeg-input-ss-accuracy) |
| R-4 | **Timestamped grid sheets** are the common LLM overview. Cells are about 384–512 px on the long side, 3×3 is the usual default with 4–36 cells, every cell is stamped with time or index, and a text map ties each cell to its time. | practice | [llm-frames](https://github.com/john-ver/llm-frames); [vid2grid](https://github.com/IanHeinrich/vid2grid); [clipsheet](https://github.com/sjwithaimhub/clipsheet); [ilinxa-capture](https://github.com/ilinxa/ilinxa-capture) |
| R-5 | **Grid, choose cells, zoom into the window between them.** | practice | [overcast frame-grid skill](https://github.com/kdr/overcast/blob/main/skills/overcast-frame-grid/SKILL.md) |
| R-6 | "Map the chosen cell back to its real timestamp — never use a time the model typed." Uniform sampling missed 9 of 28 shots in one test. That is the known limit of uniform sampling. | practice | [overcast](https://github.com/kdr/overcast/blob/main/skills/overcast-frame-grid/SKILL.md); [video-timeline](https://github.com/Megapixel99/video-timeline) |
| R-7 | CCTV-with-LLM pipelines run a cheap detector first and show the VLM only events. Scene detection plus perceptual-hash dedupe handles overnight footage. Raw video in a model costs about 258 tokens per second. | practice | [peepshow](https://www.peepshow.dev/how-to/cctv-llm-analysis); [Aizip](https://aizip.ai/news/vlm); [Superb AI](https://superb-ai.com/en/resources/blog/vlm-video-analytics-vs-ai-cctv-detection-en); [Frigate #58](https://github.com/blakeblackshear/frigate/issues/58) |
| R-8 | Slide and change detectors **need per-video calibration** ("one fixed number does not work"). They mask webcam tiles and re-grab the slide at full resolution from inside its dwell time. `mpdecimate` depends on its thresholds and drops frames even from a static video. | practice | [video-slide-extractor](https://github.com/larry-xue/video-slide-extractor); [summarize slides](https://summarize.sh/docs/commands/slides.html); [AutoSlides](https://github.com/bit-admin/AutoSlides-Extractor); [trembit mpdecimate](https://trembit.com/blog/ffmpeg-mpdecimate-filter-for-dummies); [superuser](https://superuser.com/questions/1706239/using-ffmpeg-mpdecimate-to-get-rid-of-exact-duplicate-frames-i-e-losslessly) |
| R-9 | Claude vision: 1568 px long edge on the standard tier, with a visual-token ceiling of about 1568 tokens (tokens ≈ w×h/750). 2576 px and about 4784 tokens on the high-res tier (Opus 4.7 and later). Larger images are downscaled first. The guidance is to resize and crop before upload. Images under 200 px degrade results. | authority | [Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision); [claudecodecamp](https://www.claudecodecamp.com/p/images-cost-3x-more-tokens-in-claude-opus-4-7); [ai-tldr token cost](https://ai-tldr.dev/learn/multimodal-ai/vision-models/image-token-cost) |
| R-10 | MCP tools can return image content, resource links or structured content. Inline only small images the model must see, and return paths for the rest. Base64 costs 1.33×, and neither the spec nor the SDK sets a size limit. | authority + practice | [MCP spec 2026-07-28 tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools); [mcporbit](https://mcporbit.com/blog/return-an-image-from-an-mcp-tool); [python-sdk #2557](https://github.com/modelcontextprotocol/python-sdk/issues/2557) |
| R-11 | Agents need a probe before trimming or scaling, or they guess duration. Single-purpose probe tools are common. | practice | [pollinations PR #19175](https://github.com/pollinations/pollinations/pull/19175); [video-probe-mcp](https://github.com/dvnc-labs/video-probe-mcp); [NoahWorkman mcp-ffmpeg](https://github.com/NoahWorkman/mcp-ffmpeg); [Ashutos1997 ffmpeg-mcp-server](https://github.com/Ashutos1997/ffmpeg-mcp-server) |
| R-12 | For deliverables: resize to the useful maximum, PNG for screenshots and text, JPEG or WebP for photos, strip metadata. | practice | [costrouter](https://costrouter.ai/en/blog/how-to-send-images-to-an-llm-api-a-practical-vision-guide-for-developers); [developersdigest](https://www.developersdigest.tech/blog/claude-vision-api-production-guide) |
| R-13 | ffmpeg `drawtext` can stamp `%{pts:hms}` (HH:MM:SS.mmm). The text must be escaped inside the filtergraph and needs a font. | authority | [drawtext docs](https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filters/Video/drawtext.html); [ffmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) |
| R-14 | EXIF orientation is handled by `ImageOps.exif_transpose`. Rotation is otherwise a rare edit. | authority | [Pillow ImageOps](https://pillow.readthedocs.io/en/stable/reference/ImageOps.html); [alexwlchan](https://alexwlchan.net/notes/2024/photos-can-have-orientation-in-exif) |

## 6. Agent design (first priority)

### 6.1 Times

- **Input:** seconds as a number (`725.5`), or a string `SS`, `MM:SS` or `HH:MM:SS`, each with an
  optional `.mmm` (`"12:05"`, `"00:12:05.500"`). This matches convert cut (L-12) and R-1.
- **Output:** every time is echoed as both `time_ms` (an integer) and `timecode` (`HH:MM:SS.mmm`).
- **Times are relative to the file start.** A wall-clock time from a camera file name is for the
  agent to add (§9).
- A time is checked against the probed duration before anything is grabbed. A time at or past the
  end is rejected with a fixed message that gives the duration (D-15).

### 6.2 `probe` (on `avkit_convert`)

```ts
withDesc("probe", z.object({ action: z.literal("probe"), path: z.string().min(1) }).strict())
// POST /conversions/probe {path} -> 200
// { path, duration_ms, timecode, container, video_codec, audio_codec, width, height, fps, has_video, has_audio }
```

Read-only and synchronous. It reuses `MediaPort.probe` (L-2) as it is.

### 6.3 `frames` (on `avkit_capture`)

There are two shapes, following the two `capture` modes (`capture.ts:150-176`):

```ts
const time = z.union([z.number().min(0), z.string().regex(TIMECODE_RE)]);
withDesc("frames", z.object({
  action: z.literal("frames"), path: z.string().min(1),
  at: z.array(time).min(1).max(FRAMES_MAX),          // explicit times
}).strict()),
withDesc("frames", z.object({
  action: z.literal("frames"), path: z.string().min(1),
  count: z.number().int().min(1).max(FRAMES_MAX),    // evenly spaced
  start: time.optional(), end: time.optional(),
}).strict()),
// POST /captures/frames -> 201
// { video: {path, duration_ms, width, height, fps},
//   frames: [{id, path, time_ms, timecode, width, height}] }
```

- **Even spacing** uses the midpoint of each of `count` equal parts of `[start, end)`. This avoids
  the black first frame and the empty end of file (D-9, R-3).
- **Seek:** `ffmpeg -ss T -i V -frames:v 1` with a decode, never `-c copy`, written as a PNG at
  full source resolution (D-7).
- **Duplicate times** are collapsed. The response is in time order.
- **Response:** paths and ids, never image bytes. The agent views a frame with
  `image {id, max_edge | region}` (D-10, L-7, R-10).

### 6.4 `sheet` (on `avkit_capture`)

```ts
withDesc("sheet", z.object({
  action: z.literal("sheet"), path: z.string().min(1),
  start: time.optional(), end: time.optional(),
  grid: z.number().int().min(SHEET_GRID_MIN).max(SHEET_GRID_MAX).optional(),   // grid × grid cells
  max_edge: z.number().int().min(REGION_MAX_EDGE_MIN).max(REGION_MAX_EDGE_MAX).optional(),
}).strict()),
// POST /captures/sheet -> 201
// { video: {...}, shot: {id, path, width, height}, spacing_ms,
//   cells: [{cell: 1, time_ms, timecode}, ...] }      // cells read left to right, top to bottom
```

- **Construction:** ffmpeg grabs each cell already scaled to the cell size (input seek with
  `scale`). Pillow pastes the cells into the grid and stamps each one with its number and
  `HH:MM:SS` (plus `.mmm` when the spacing is under 10 s), using the font the annotate text
  already resolves (L-8). Neither `drawtext` nor `xstack` is used (D-13).
- **Size:** the sheet fits the standard vision tier without a server-side downscale. The long edge
  is at most `max_edge` (default 1568), and the area is held under the token ceiling (D-4, R-9).
- **Zoom** is the same call with a narrower `start` and `end`. No session state is kept.

### 6.5 `export` (on `avkit_capture`, D-3)

```ts
withDesc("export", z.object({
  action: z.literal("export"), id: captureId,
  format: z.enum(["png", "jpeg", "webp"]),
  max_edge: z.number().int().min(REGION_MAX_EDGE_MIN).optional(),   // only shrinks
  quality: z.number().int().min(1).max(100).optional(),            // jpeg/webp; default LOSSY_QUALITY
}).strict()),
// POST /captures/{id}/export -> 201  { shot: {id, path, width, height, bytes}, source_id }
```

- **Source:** the shot as it is shown. That is the annotated bake when marks exist, otherwise the
  original. The export has no marks of its own.
- **Output:** a new shot. The source is untouched, as in crop D-1 (`capture-crop/design.md:590`).
- **Metadata:** none is written. Pillow saves without EXIF.
- **Shared pipeline:** export reuses the crop copy pipeline (temporary file, lock, unique name,
  register) from MEU-130.

### 6.6 Descriptions (M7)

Each new action states its own markers, because capture's shared Prerequisite does not fit a
video path (L-9):

- **frames and sheet:**
  - Workflow: probe, then sheet, then frames, then image.
  - Prerequisite: a local absolute video path; ffmpeg is available; nothing is uploaded.
  - Returns: shot ids, paths and times, with no bytes.
  - Errors: fixed messages (§8).
- **sheet** also says to cite the times in `cells`, never times read off the image (R-6).

## 7. GUI design (second priority)

**There is no new GUI in v1 (D-5).** Frames, sheets and exports are ordinary inbox shots, so the
Capture page already lists, opens, zooms, crops and annotates them. A human who wants a still
today pauses a player and takes a screenshot, and the hotkey grab already covers that.

If a GUI is wanted later, the smallest useful piece is a **Grab frame** dialog on the Capture page:
a video path plus a time field, which calls `POST /captures/frames`. A timeline scrubber stays
under 08's named deferral (L-12).

## 8. Data and file contract

| Item | Contract |
|---|---|
| Frame name | `{video_stem}-t{HH}h{MM}m{SS}.{mmm}s.png`, for example `standup-t00h12m05.500s.png`. Collisions get `_2` and so on, checked against files and rows (crop and import precedent, L-5). Windows forbids `:` in names. |
| Sheet name | `{video_stem}-sheet-{start}-{end}.png` with `HHhMMmSSs` times, for example `door-sheet-00h00m00s-08h00m00s.png`. |
| Export name | `{stem}-export.{png,jpg,webp}`, then `_2`. |
| Source | `CaptureSource.Video` for frames and sheets, and `CaptureSource.Export` for exports. Neither has a register wire value (D-12, crop D-484). The column stores `.name`, so no migration is needed. |
| Provenance | Not persisted. The file name carries the time, and the response carries the video path and times (D-17). |
| Video file | Read in place from a local absolute path. It is never copied into the inbox, never changed, and has no size limit. URLs are rejected (D-16). |
| Writes | Each output follows the import pattern: a `.avkit-tmp` file, then `os.replace` under `CAPTURE_FILE_LOCK`, then register. A failed grab leaves no partial shot (L-5). |
| Errors (fixed, no paths) | `video file not found`; `not a video: no video stream`; `time {t} is past the end ({duration})`; `start must be before end`; `ffmpeg is not available` (the existing not-found error); `frame grab failed at {t}`. Plus the strict-schema rejection of extra keys. |

## 9. Deferred and rejected

| Item | Status | Why |
|---|---|---|
| Scene, slide or motion detection | Deferred (D-2) | It needs calibration for each video (R-8), and there were 0 local uses (§4). The sheet zoom loop covers coverage at a known cost. It is the first follow-up if events between samples are missed (§11). |
| Dedupe (`mpdecimate`, pHash) | Deferred | Thresholds are fragile (R-8). It only matters once there is detection. |
| Subtitle extract | Deferred | Already deferred in 08 (`:544`). |
| Wall-clock labels for camera files | Deferred | Each camera vendor names files differently. The agent adds the offset to the file's start time. |
| OCR | Out of scope | Claude reads text in a region view (MEU-128). There were 8 local uses. |
| PDF rasterise | Out of scope | Not image editing and not video. There were 30 uses, which makes it a separate design if ever. |
| Rotate and flip | Deferred | 16 uses, mostly EXIF upright, which import already handles (R-14). Still deferred by 09 `:1097`. |
| Pad, extent, cover-crop | Deferred | 13 uses, mostly social thumbnails. None of the three purposes needs it. |
| Compare/diff, trim, compose/append | Deferred | 4, 2 and 7 uses. |
| GUI Grab frame and a timeline | Deferred (D-5) | §7. |
| Persisted provenance | Deferred | Needs a schema migration, as in crop. |
| Inline image bytes from `frames` or `sheet` | **Rejected** | R-10 and 08 `:516` ("never media bytes"). One `image` call shows a shot. |
| ffmpeg `drawtext` or `tile` for sheets | **Rejected** | Filtergraph escaping and font paths (R-13). Pillow already draws the labels (L-8). |
| A separate `avkit_video` tool | **Rejected** (D-1) | Outputs are capture shots. A new tool would duplicate list, get and image. |
| URLs or yt-dlp sources | **Rejected** | Local files only (server instructions; `convert.ts:12`). A YouTube video is downloaded first. |

## 10. Slices

| Slice | Scope | Depends on |
|---|---|---|
| **S1** Probe | `POST /conversions/probe`, `avkit_convert probe`, tests | — |
| **S2** Frames | `FramePort` (`probe` and `grab_frame`) on `FFmpegAdapter`, wired into `CaptureService`; `CaptureSource.Video`; times parsing; `POST /captures/frames`; MCP `frames`; tests | D-1, D-4 (ruled) |
| **S3** Sheet | Pillow grid and labels, size budget, `POST /captures/sheet`, MCP `sheet`, tests | S2; D-4 (ruled) |
| **S4** Export | `CaptureSource.Export`, `POST /captures/{id}/export`, MCP `export`, tests | D-3 (ruled); MEU-130 (copy pipeline) |

The suggested order is S1, S2, S3, S4. S1 waits on nothing. D-1 to D-5 were ruled on 2026-11-09.
The slices are registered as MEU-133 (S1), MEU-134 (S2), MEU-135 (S3) and MEU-136 (S4), and grouped
into sessions in `.agent/context/grouping/2026-11-09-video-stills-session-grouping.md`.

**Parity gates (G25).** API and MCP field parity for every new action (M1, M2). The GUI surface is
"none, the existing shot list" (D-5). None of the actions is destructive: each writes only new files
(M3 does not apply).

## 11. Risks and tests

| Risk | Test or guard |
|---|---|
| Wrong frame for a time | A synthetic video with a frame counter burned in (`testsrc2`, 25 fps). Grab at 0.0, 1.0, 1.02 and the last frame, then read the counter. **Open check at planning:** does input seek return the frame at or after T, or the nearest one? Record which and say it in the description. |
| VFR or odd timebases (phone video, CCTV) | A VFR fixture. Assert that the reported `time_ms` matches the requested time to within one frame interval, and that no grab returns empty. |
| Times past the end | Rejected before any grab, with the duration in the message. Also test the last half-second. |
| Raw camera streams with no duration (`.h264`, `.dav`) | Probe gives `duration_ms: null`. `sheet` and `count` frames fail with a fixed message. `at` frames still work. **Open check:** whether a copy remux through `avkit_convert cut` fixes it. |
| Slow synchronous calls on long 4K HEVC | **Planning probe:** time 20 frames and a 5×5 sheet on a 4K HEVC 2 h file. If either is close to the MCP request timeout, lower the cap (D-4) rather than add a queue. |
| Sheet downscaled by the API | Assert w×h/750 ≤ the tier budget and long edge ≤ `max_edge` for every grid and the common aspect ratios (16:9, 4:3, 9:16). |
| Labels unreadable | Label height scales with the cell. Render a 5×5 at 1568 and check legibility on a mostly white frame and a mostly black frame (outlined text). |
| Events between samples are missed (R-6) | Known limit of uniform sampling. The description says so and points to the zoom loop. Deferred detection is the fix if real use misses events. |
| Large PNG frames from 4K video | Already handled by `image` `max_edge` and region (L-7). The description says so. |
| Export bigger than its source | For PNG→PNG at the same size, the response gives `bytes`, so the agent can see it. No guard is needed. |
| Name race | Two `frames` calls at the same time produce `_2` names, never an overwrite (the crop test pattern). |
| Descriptions mislead agents | A small eval: (1) find the slide shown at a transcript time in a 1 h meeting recording; (2) find when a car arrives in a 2 h driveway clip with the sheet zoom loop; (3) shrink a 4K screenshot to a JPEG under 500 KB. |

## 12. Decision log

```yaml
decision_log:
  - id: D-1
    stage: planning
    question: "Where do video stills live in av-kit?"
    resolution: human
    class: product-preference
    chosen: "avkit_capture actions frames and sheet, writing inbox shots"
    source_tag: Human-approved
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1091 — 'video' Out of product (screen recording)"
      - "docs/build-plan/09-screenshot-capture.md:1092 — Convert → Capture handoff deferred"
      - "mcp-server/src/toolsets/convert.ts:11 — convert is a queue; capture.ts:35-38 — capture is synchronous"
    research:
      engine: tavily, exa
      sources:
        - "https://github.com/lawriec/mcp-video-reader — synchronous extract_frames, capped"
        - "https://github.com/woosal1337/media-mcp — returns paths per timestamp"
        - "https://github.com/kdr/overcast/blob/main/skills/overcast-frame-grid/SKILL.md — grid then zoom"
    reasoning: "Touches two named 09 deferrals, so it is human-gated. Brief in section 13. Mat accepted the recommendation."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'all recommendations accepted, proceed'"

  - id: D-2
    stage: planning
    question: "What does the video v1 cover?"
    resolution: human
    class: product-preference
    chosen: "probe + frames + sheet; change detection deferred"
    source_tag: Human-approved
    precedents:
      - "P:/carmen/camera/tools/door_scan.py:37 — keyframe scoring built by hand"
      - "stills-precedent-sweep.txt — 0 scene-detect uses, 4 frame grabs, 3 sheets"
    research:
      engine: tavily, exa
      sources:
        - "https://github.com/larry-xue/video-slide-extractor — per-video calibration"
        - "https://www.peepshow.dev/how-to/cctv-llm-analysis — detect first for overnight footage"
        - "https://github.com/john-ver/llm-frames — timestamped grid"
    reasoning: "Scope fork against Mat's 'lightweight' goal. Sources split on whether detection is essential for CCTV. Brief in section 13. Mat accepted the recommendation."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'all recommendations accepted, proceed'"

  - id: D-3
    stage: planning
    question: "Is an export copy (resize, format, strip) in v1?"
    resolution: human
    class: product-preference
    chosen: "Yes, as one small export action"
    source_tag: Human-approved
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1097 — resize and format option deferred by the crop design"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:475-479 — _write_lossy exists"
    research:
      engine: tavily
      sources:
        - "https://costrouter.ai/en/blog/how-to-send-images-to-an-llm-api-a-practical-vision-guide-for-developers — resize, format, strip"
    reasoning: "Reopens a named deferral, so it is human-gated. Brief in section 13. Mat accepted the recommendation."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'all recommendations accepted, proceed'"

  - id: D-4
    stage: planning
    question: "Caps and defaults for frames and sheets"
    resolution: human
    class: governance-value
    chosen: "FRAMES_MAX 20; sheet grid default 3, range 2-5; sheet max_edge default 1568 (range 64-2576) with area held under the tier token budget"
    source_tag: Human-approved
    precedents:
      - "mcp-server/src/toolsets/capture.ts:30-31 — REGION_MAX_EDGE 64-2576"
    research:
      engine: tavily, exa
      sources:
        - "https://github.com/lawriec/mcp-video-reader — 1-20 frames, default 10"
        - "https://github.com/sjwithaimhub/clipsheet — 3x3 default"
        - "https://platform.claude.com/docs/en/build-with-claude/vision — 1568 px; >20 images lowers the per-image limit"
    reasoning: "Governance numbers. Brief in section 13. Mat accepted the recommendation."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'all recommendations accepted, proceed'"

  - id: D-5
    stage: planning
    question: "Is there a GUI in v1?"
    resolution: human
    class: product-preference
    chosen: "No new GUI; outputs appear on the Capture page as shots"
    source_tag: Human-approved
    precedents:
      - "docs/build-plan/08-video-conversion.md:170 — timeline player deferred"
    research:
      engine: none
      sources: []
    reasoning: "Product fork on surfaces. Brief in section 13. Mat accepted the recommendation."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'all recommendations accepted, proceed'"

  - id: D-6
    stage: planning
    question: "How is probe exposed?"
    resolution: autonomous
    class: two-way
    chosen: "POST /conversions/probe {path} and avkit_convert probe; reuses MediaPort.probe"
    source_tag: Research-backed
    precedents:
      - "packages/infrastructure/src/avkit_infra/media/adapter.py:403-426 — probe exists"
      - "docs/build-plan/08-video-conversion.md:389 — ffprobe JSON"
    research:
      engine: exa
      sources:
        - "https://github.com/pollinations/pollinations/pull/19175 — agents probe before trimming"
        - "https://github.com/dvnc-labs/video-probe-mcp — one narrow probe tool"
    reasoning: "Probe describes media, which is convert's domain. Convert cut also needs it. POST matches convert add's body style and avoids a Windows path in a query string."

  - id: D-7
    stage: planning
    question: "How is a frame grabbed?"
    resolution: autonomous
    class: two-way
    chosen: "Input seek -ss T -i V -frames:v 1, decoded, PNG at source resolution"
    source_tag: Research-backed
    precedents:
      - "P:/carmen/camera/tools/make_review_set.py:54 — input seek"
    research:
      engine: tavily
      sources:
        - "https://trac.ffmpeg.org/wiki/Seeking — frame-accurate when transcoding"
        - "https://ffmpeg-cookbook.com/en/articles/extract-frames — real nearby frame"
    reasoning: "Fast and accurate. Output seek is slow on long files, and copy seek snaps to keyframes."

  - id: D-8
    stage: planning
    question: "Time format in and out"
    resolution: autonomous
    class: two-way
    chosen: "In: seconds or [HH:]MM:SS[.mmm]; out: time_ms and HH:MM:SS.mmm"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/08-video-conversion.md — cut accepts HH:MM:SS.mmm or seconds"
    research:
      engine: exa
      sources:
        - "https://pypi.org/project/video-vision-mcp/0.3.0/ — accepts '00:42' and 12.5"
    reasoning: "Matches cut. Agents copy times from transcripts in either form."

  - id: D-9
    stage: planning
    question: "Where do count frames fall?"
    resolution: autonomous
    class: two-way
    chosen: "Midpoints of count equal parts of [start, end)"
    source_tag: Research-backed
    precedents: []
    research:
      engine: tavily
      sources:
        - "https://ffmpeg-cookbook.com/en/articles/extract-frames — nothing written past the end"
    reasoning: "Avoids the black first frame and the empty end of file. Every frame stands for an equal slice."

  - id: D-10
    stage: planning
    question: "Do frames and sheet return bytes?"
    resolution: autonomous
    class: two-way
    chosen: "No; ids, paths and times. View with image."
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/08-video-conversion.md:516 — never media bytes"
      - "mcp-server/src/toolsets/capture.ts:189-198 — image with region and max_edge"
    research:
      engine: exa
      sources:
        - "https://mcporbit.com/blog/return-an-image-from-an-mcp-tool — inline only what the model must see"
        - "https://github.com/woosal1337/media-mcp — returns paths"
    reasoning: "Twenty inline 4K frames would flood the context. The agent picks what to view."

  - id: D-11
    stage: planning
    question: "File names"
    resolution: autonomous
    class: two-way
    chosen: "{stem}-tHHhMMmSS.mmms.png; {stem}-sheet-{start}-{end}.png; {stem}-export.{ext}; _2 on collision"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:549 — _import_dest unique naming"
      - "P:/ffmpeg — tMMmSS.png stills"
    research:
      engine: exa
      sources:
        - "https://summarize.sh/docs/commands/slides.html — slide_0001_18.60s.png"
    reasoning: "A human scanning the inbox sees the time. Windows forbids ':'."

  - id: D-12
    stage: planning
    question: "Capture source for the new shots"
    resolution: autonomous
    class: two-way
    chosen: "CaptureSource.Video (frames, sheets) and CaptureSource.Export; no register wire values"
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-08-capture-crop-copy/implementation-plan.md:170 — Crop with no wire value (D-484)"
      - "packages/core/src/avkit_core/domain/enums.py:209-219"
    research:
      engine: none
      sources: []
    reasoning: "Same pattern as Crop. No migration, because the column stores .name."

  - id: D-13
    stage: planning
    question: "How is the sheet built and labelled?"
    resolution: autonomous
    class: two-way
    chosen: "ffmpeg grabs scaled cells; Pillow tiles them and draws the labels with the annotate font"
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:132-143 — _load_font"
      - "P:/carmen/camera/tools/make_review_set.py:63-75 — contact strip with labels drawn after the grab"
    research:
      engine: tavily
      sources:
        - "https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filters/Video/drawtext.html — drawtext escaping and font"
    reasoning: "One labelling path already exists and is tested. It avoids filtergraph escaping on Windows paths."

  - id: D-14
    stage: planning
    question: "Sheet labels and the cell map"
    resolution: autonomous
    class: two-way
    chosen: "Cell number + HH:MM:SS (with .mmm below 10 s spacing) on every cell; response cells[] maps number to time"
    source_tag: Research-backed
    precedents:
      - "P:/carmen/camera/tools/make_review_set.py:75 — HH:MM:SS label"
    research:
      engine: tavily, exa
      sources:
        - "https://github.com/kdr/overcast/blob/main/skills/overcast-frame-grid/SKILL.md — never use a time the model typed"
        - "https://github.com/sjwithaimhub/clipsheet — manifest maps cell to time"
        - "https://github.com/IanHeinrich/vid2grid — time and index on every cell"
    reasoning: "The number lets the agent point. The response gives the true time."

  - id: D-15
    stage: planning
    question: "Times outside the video"
    resolution: autonomous
    class: two-way
    chosen: "Rejected before any grab, with a fixed message that gives the duration"
    source_tag: Research-backed
    precedents: []
    research:
      engine: tavily
      sources:
        - "https://ffmpeg-cookbook.com/en/articles/extract-frames — nothing written past the end"
    reasoning: "Silent clamping would hand back a frame the agent did not ask for."

  - id: D-16
    stage: planning
    question: "Video input rules"
    resolution: autonomous
    class: two-way
    chosen: "Local absolute path, read in place, never copied or changed, no size limit, no URLs"
    source_tag: Local Canon
    precedents:
      - "mcp-server/src/toolsets/convert.ts:12 — local absolute file paths"
    research:
      engine: none
      sources: []
    reasoning: "Only the PNG outputs enter the inbox. Copying hours of video would serve nothing."

  - id: D-17
    stage: planning
    question: "Persist video provenance on the shot?"
    resolution: autonomous
    class: two-way
    chosen: "No; the file name and the response carry it"
    source_tag: Local Canon
    precedents:
      - "_inspiration/capture-crop/design.md:334 — provenance deferred, needs a migration"
    research:
      engine: none
      sources: []
    reasoning: "Same reasoning as crop."

  - id: D-18
    stage: planning
    question: "Remaining deferrals (section 9)"
    resolution: autonomous
    class: two-way
    chosen: "Dedupe, subtitles, wall-clock labels, rotate/flip, pad, compare, trim, compose deferred; OCR and PDF out of scope"
    source_tag: Research-backed
    precedents:
      - "stills-precedent-sweep.txt — usage counts in section 4"
      - "docs/build-plan/08-video-conversion.md:544; 09-screenshot-capture.md:1097"
    research:
      engine: tavily
      sources:
        - "https://trembit.com/blog/ffmpeg-mpdecimate-filter-for-dummies — fragile thresholds"
        - "https://pillow.readthedocs.io/en/stable/reference/ImageOps.html — exif_transpose"
    reasoning: "Each serves none of the three purposes, or is rare (section 4). All are additive later."

  - id: D-19
    stage: planning
    question: "How does CaptureService reach ffmpeg?"
    resolution: autonomous
    class: two-way
    chosen: "A narrow FramePort (probe, grab_frame) implemented by the existing FFmpegAdapter instance"
    source_tag: Local Canon
    precedents:
      - "packages/api/src/avkit_api/wiring.py:152-155 — one FFmpegAdapter, ffmpeg path resolved live"
    research:
      engine: none
      sources: []
    reasoning: "Capture needs two calls, not the whole MediaPort. Sharing the instance keeps the ffmpeg setting in one place."

  - id: D-20
    stage: planning
    question: "Export details (if D-3 is yes)"
    resolution: autonomous
    class: two-way
    chosen: "Source is the shot as shown (bake if marked); max_edge only shrinks; png/jpeg/webp; quality default LOSSY_QUALITY 90; no metadata; new shot"
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:56 — LOSSY_QUALITY = 90"
      - "_inspiration/capture-crop/design.md:590 — copy, source untouched"
    research:
      engine: tavily
      sources:
        - "https://www.developersdigest.tech/blog/claude-vision-api-production-guide — resize and strip"
    reasoning: "A deliverable is what the user sees. The quality value already exists, so no new governance number."
```

## 13. Decision Briefs

### D-1: Where do video stills live?   [product-preference] [planning]

**Ruling (Mat, 2026-11-09):** "all recommendations accepted, proceed". The recommended option.
The brief below is kept as the record.

**Recommendation:** Add `frames` and `sheet` as **`avkit_capture` actions** that write ordinary
inbox shots. Region view, crop, annotate and the Capture page then work on them with no new code.
The calls are synchronous like every capture call, which matches the video MCP servers found
(R-1). This reverses one named deferral in part: "Convert → Capture handoff" (09 `:1092`) becomes
"a video path in, capture shots out". It does not touch "video — Out of product" (`:1091`), which
is about recording the screen.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ `avkit_capture frames` / `sheet`, writing inbox shots | — | — | `capture.ts:35-38`; [mcp-video-reader](https://github.com/lawriec/mcp-video-reader); [overcast](https://github.com/kdr/overcast/blob/main/skills/overcast-frame-grid/SKILL.md) |
| ⚠️ An `avkit_convert` kind (`add kind:"frames"`, queued) | Convert already owns ffmpeg. The queue survives long jobs and shows progress. | Three calls (add, start, poll) for one still. The outputs are files outside capture, so viewing, cropping or annotating them needs import first. | `convert.ts:11`, `:42-73` |
| ⚠️ A new `avkit_video` tool | A clean name. Room to grow. | Duplicates list, get and image for its outputs, and adds a tool for agents to learn. | [video-use](https://github.com/therealfloatdev/video-use) |
| ❌ Do nothing: agents keep calling ffmpeg directly | No work. | Every review rebuilds seek, labels and sheets (L-13, L-14). Agents without a shell can't do it at all. Mat's question was whether av-kit can do it. | `stills-precedent-sweep.txt` |

**Precedent:** Import (MEU-129) already brings an outside file into capture as a shot (L-5). Crop
(MEU-130) adds a source member with no wire value (L-6).
**Research:** tavily and exa. Video MCP servers expose frames as synchronous calls that return
paths. Receipts `stills-research-01-mcp-frames.md` and `-11-return-shape.md`.
**Reversibility / risk:** two-way before release. The service code is the same under any of the
three homes, and only the MCP and route layer differs. The risk is slow synchronous calls on long
4K files (§11), which is bounded by D-4.
**If you do not answer:** (Superseded by the ruling above.) S1 (probe) can be planned and built now. S2 and S3 are planned on the
recommendation and held at the plan gate.

### D-2: What does the video v1 cover?   [product-preference] [planning]

**Ruling (Mat, 2026-11-09):** "all recommendations accepted, proceed". The recommended option.
The brief below is kept as the record.

**Recommendation:** **probe + frames + sheet**, with change detection deferred. Meeting review
needs frames at known times (from a transcript or a sheet). Security review needs coverage, which
the sheet zoom loop gives at about four sheets to narrow 8 hours to seconds (9× per step). That is
roughly 4 × 1.6k tokens. Detection is the strongest tool for security footage (R-7), but it needs
calibration for each video (R-8), and there were no local uses.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ probe + frames + sheet | — | — | [llm-frames](https://github.com/john-ver/llm-frames); [overcast](https://github.com/kdr/overcast/blob/main/skills/overcast-frame-grid/SKILL.md); [mcp-video-reader](https://github.com/lawriec/mcp-video-reader) |
| ⚠️ probe + frames only (no sheet) | Smaller: one slice fewer. | An overview costs `count` images instead of one, about 9× the tokens for a 3×3 view. The agent must build its own time map. Both local reviews built a sheet by hand (L-13, L-14). | [vid2grid](https://github.com/IanHeinrich/vid2grid); `make_review_set.py:63` |
| ⚠️ Recommended + change detection (`select=gt(scene,t)` or keyframe diff) | Catches short events between samples, which is the real CCTV need (R-7). | Needs a full decode of hours of video and a threshold tuned for each video (R-8). It is the heaviest slice by far, and against "lightweight". It can be added later without changing the other calls. | [video-slide-extractor](https://github.com/larry-xue/video-slide-extractor); [peepshow](https://www.peepshow.dev/how-to/cctv-llm-analysis); `door_scan.py:37` |
| ❌ Do nothing | No work. | As in D-1. | — |

**Precedent:** Carmen built keyframe scoring for one camera and one door (L-14). It is a good
recipe and a bad default.
**Research:** tavily and exa. Receipts `-03-sheet.md`, `-04-cctv.md`, `-06-slides.md`, `-09-dedupe.md`.
**Reversibility / risk:** two-way. Detection would be an extra action that returns times to feed
`frames`, so nothing in v1 changes when it is added. The risk is that v1 misses short events in
footage. The description names that limit.
**If you do not answer:** (Superseded by the ruling above.) The design keeps the recommendation. S1 and S2 do not depend on this
decision. S3 (sheet) is held at the plan gate.

### D-3: Is an export copy (resize, format, strip) in v1?   [product-preference] [planning]

**Ruling (Mat, 2026-11-09):** "all recommendations accepted, proceed". The recommended option.
The brief below is kept as the record.

**Recommendation:** **Yes, as one small `export` action.** Resize plus re-encode is the most
common image edit agents run here after crop (62 resize and 63 quality/format uses, §4). The
pieces exist (`_write_lossy`, `LOSSY_QUALITY`, the MEU-130 copy pipeline). This reopens part of
09 `:1097` (resize, format option). Cover-crop, pad and rotate stay deferred.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ `export {id, format, max_edge?, quality?}` → new shot | — | — | `adapter.py:475-479`; [costrouter](https://costrouter.ai/en/blog/how-to-send-images-to-an-llm-api-a-practical-vision-guide-for-developers) |
| ⚠️ Fold it into crop (`crop` gains `max_edge` and `format`) | No new action. | Changes the approved MEU-130 contract mid-flight. An export without a crop has to pass a whole-image box. | `implementation-plan.md:168-170` |
| ⚠️ Resize only, no format change | Smaller. | Most of the size win comes from JPEG/WebP for photos and video stills (R-12). PNG→PNG at a smaller size still leaves agents on magick for format. | `stills-research-07-export.md` |
| ❌ Do nothing (keep the 09 `:1097` deferral) | No work, and the crop design's line stands. | Agents keep using ImageMagick or Pillow for the most common edit, and agents without a shell can't make a small deliverable. | §4 |

**Precedent:** The crop design deferred this as "image conversion, not crop"
(`capture-crop/design.md:332`). The pattern stays the same: a new shot, source untouched.
**Research:** tavily. Receipt `stills-research-07-export.md`.
**Reversibility / risk:** two-way. It is additive and writes only new files.
**If you do not answer:** (Superseded by the ruling above.) S4 is not planned. S1 to S3 are unaffected.

### D-4: Caps and defaults   [governance-value] [planning]

**Ruling (Mat, 2026-11-09):** "all recommendations accepted, proceed". The recommended option.
The brief below is kept as the record.

**Recommendation:**

| Number | Value | Why |
|---|---|---|
| `FRAMES_MAX` (per `frames` call) | **20** | mcp-video-reader's cap. Above 20 images in one request, Claude lowers the per-image size limit (R-9). It also bounds a synchronous call. |
| Sheet grid | default **3** (3×3), range **2–5** | 3×3 is the common default (R-4). At 1568 px a 5×5 grid gives cells about 300 px wide, close to the 200 px floor (R-9). 6×6 would cross it. |
| Sheet `max_edge` | default **1568**, range **64–2576** (the existing `REGION_MAX_EDGE` constants) | Standard tier by default, high-res tier on request (R-9). |
| Sheet area | held to w×h/750 ≤ **1568** tokens (≤ **4784** when `max_edge` > 1568) | Otherwise the API downscales a 16:9 1568-wide sheet anyway (R-9). |

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ 20 / 3 (2–5) / 1568 / token budget | — | — | [mcp-video-reader](https://github.com/lawriec/mcp-video-reader); [clipsheet](https://github.com/sjwithaimhub/clipsheet); [Claude vision](https://platform.claude.com/docs/en/build-with-claude/vision) |
| ⚠️ Larger: 36 frames, grids up to 6×6 | Fewer calls on long footage. | Cells under about 260 px at 1568, and more than 20 images per request lowers the per-image limit. The synchronous call time doubles. | [llm-frames](https://github.com/john-ver/llm-frames) (4–36) |
| ⚠️ Smaller: 10 frames, fixed 3×3 | Simpler and faster. | One more zoom step on long footage. | [mcp-video-reader](https://github.com/lawriec/mcp-video-reader) (default 10) |
| ❌ No caps | — | An unbounded synchronous call, and an unbounded inbox write from one call. | — |

**Precedent:** `REGION_MAX_EDGE_MIN/MAX` (`capture.ts:30-31`) are reused as they are. Only
`FRAMES_MAX` and the grid range are new numbers.
**Research:** tavily and exa. Receipts `-01-`, `-03-`, `-05-vision-limits.md`.
**Reversibility / risk:** two-way. These are constants. The planning probe (§11) may lower
`FRAMES_MAX` if 20 frames of 4K HEVC is slow.
**If you do not answer:** (Superseded by the ruling above.) S2 and S3 are planned with these values, flagged as unratified
governance numbers, and held at the plan gate.

### D-5: Is there a GUI in v1?   [product-preference] [planning]

**Ruling (Mat, 2026-11-09):** "all recommendations accepted, proceed". The recommended option.
The brief below is kept as the record.

**Recommendation:** **No new GUI.** The outputs are ordinary shots, so the Capture page shows them,
and the crop and annotate tools work on them. The three purposes are agent work. A human who wants
one still can pause a player and press the capture hotkey. The smallest later addition is a **Grab
frame** dialog (§7).

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ No new GUI; shots appear on the Capture page | — | — | `08-video-conversion.md:170` |
| ⚠️ A Grab frame dialog (path and time) on the Capture page | A human can pull an exact frame without a player. | One more GUI slice with its own E2E and parity gates. There is no user request for it. | — |
| ⚠️ A video timeline with a scrubber | The natural human tool. | Reverses 08's named "no timeline player" deferral. It is the heaviest GUI there is. | `08-video-conversion.md:170`, `:544` |
| ❌ Do nothing beyond v1 (which is what the recommendation is) | — | — | — |

The recommendation already is the status quo for the GUI, so the do-nothing row adds nothing new.
**Precedent:** The 08 timeline deferral. The capture list shows every source.
**Research:** none needed. This is a surface choice with no outside convention.
**Reversibility / risk:** two-way. The dialog can come later and calls the same route.
**If you do not answer:** (Superseded by the ruling above.) No GUI slice is planned.

## 14. Sources

**Official documentation**
- FFmpeg seeking: https://trac.ffmpeg.org/wiki/Seeking
- FFmpeg filters: https://ffmpeg.org/ffmpeg-filters.html
- drawtext: https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filters/Video/drawtext.html
- Claude vision: https://platform.claude.com/docs/en/build-with-claude/vision
- MCP spec 2026-07-28, tools: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- Pillow ImageOps: https://pillow.readthedocs.io/en/stable/reference/ImageOps.html

**Practice: video MCP servers and frame tools**
- mcp-video-reader: https://github.com/lawriec/mcp-video-reader
- media-mcp: https://github.com/woosal1337/media-mcp
- video-use: https://github.com/therealfloatdev/video-use
- video-vision-mcp: https://pypi.org/project/video-vision-mcp/0.3.0/
- GetVideoFrames MCP: https://getvideoframes.com/developers/mcp/
- video-probe-mcp: https://github.com/dvnc-labs/video-probe-mcp
- NoahWorkman mcp-ffmpeg: https://github.com/NoahWorkman/mcp-ffmpeg
- Ashutos1997 ffmpeg-mcp-server: https://github.com/Ashutos1997/ffmpeg-mcp-server
- pollinations PR #19175: https://github.com/pollinations/pollinations/pull/19175

**Practice: sheets and grids**
- llm-frames: https://github.com/john-ver/llm-frames
- vid2grid: https://github.com/IanHeinrich/vid2grid
- clipsheet: https://github.com/sjwithaimhub/clipsheet
- ilinxa-capture: https://github.com/ilinxa/ilinxa-capture
- overcast frame-grid skill: https://github.com/kdr/overcast/blob/main/skills/overcast-frame-grid/SKILL.md
- video-timeline: https://github.com/Megapixel99/video-timeline

**Practice: CCTV, slides and dedupe**
- peepshow: https://www.peepshow.dev/how-to/cctv-llm-analysis
- Aizip VLM: https://aizip.ai/news/vlm
- Superb AI: https://superb-ai.com/en/resources/blog/vlm-video-analytics-vs-ai-cctv-detection-en
- Frigate #58: https://github.com/blakeblackshear/frigate/issues/58
- video-slide-extractor: https://github.com/larry-xue/video-slide-extractor
- summarize slides: https://summarize.sh/docs/commands/slides.html
- AutoSlides: https://github.com/bit-admin/AutoSlides-Extractor
- mpdecimate: https://trembit.com/blog/ffmpeg-mpdecimate-filter-for-dummies
- mpdecimate (superuser): https://superuser.com/questions/1706239/using-ffmpeg-mpdecimate-to-get-rid-of-exact-duplicate-frames-i-e-losslessly

**Practice: image delivery and MCP returns**
- costrouter vision guide: https://costrouter.ai/en/blog/how-to-send-images-to-an-llm-api-a-practical-vision-guide-for-developers
- developersdigest vision guide: https://www.developersdigest.tech/blog/claude-vision-api-production-guide
- claudecodecamp, Opus 4.7 image tokens: https://www.claudecodecamp.com/p/images-cost-3x-more-tokens-in-claude-opus-4-7
- ai-tldr image token cost: https://ai-tldr.dev/learn/multimodal-ai/vision-models/image-token-cost
- mcporbit, returning images: https://mcporbit.com/blog/return-an-image-from-an-mcp-tool
- python-sdk #2557: https://github.com/modelcontextprotocol/python-sdk/issues/2557
- ffmpeg-cookbook frames: https://ffmpeg-cookbook.com/en/articles/extract-frames
- input -ss accuracy: https://video.stackexchange.com/questions/37425/ffmpeg-input-ss-accuracy
- EXIF orientation: https://alexwlchan.net/notes/2024/photos-can-have-orientation-in-exif
