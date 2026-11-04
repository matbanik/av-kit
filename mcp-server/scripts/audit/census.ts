/**
 * ENV_BOUND_AUDIT (container mode only). Members were added only with a row-6/row-3 proof
 * (cloud-local-collaboration.md §4; plan amendment A4f). Each needs its signature AND its
 * environment proof; authoritative mode consults none of this.
 */
import type { CensusMember } from "./classify.js";

/** The API masks >=500 domain text (errors.py), so a 500/503 surfaces as internal_error; the yt-dlp bot wall is ExtractError (422) and keeps its text. */
const MASKED_500 = /internal_error/;
const BOT_WALL = /confirm you.re not a bot/i;

export const ENV_BOUND_AUDIT: CensusMember[] = [
  {
    // capture_fullscreen -> _require_windows (avkit_infra/capture/adapter.py:113,159-161) -> HTTP 503.
    key: "avkit_capture.capture",
    signature: MASKED_500,
    envProof: (env) => env.platform !== "win32",
  },
  {
    // yt-dlp extract on a datacenter IP: "Sign in to confirm you're not a bot" -> ExtractError, HTTP 422.
    // Proof: every URL a failing step of this action used also fails a direct yt-dlp extract
    // outside the runner (the bot check is per video and per moment, so it is probed per URL).
    key: "avkit_download.add",
    signature: BOT_WALL,
    envProof: (env) => env.networkProbe?.["avkit_download.add"] === false,
  },
  {
    // The media download hits YouTube's datacenter wall after a successful add, so the job is
    // Failed before cancel can act: "Sign in to confirm you're not a bot", or a 403 on the media
    // fetch itself. Proof: the container host AND a direct yt-dlp test fetch of the cancel
    // target's own URL fails with the same wall (review round 1 OOC-2: host alone was weak).
    key: "avkit_download.cancel",
    signature: /confirm you.re not a bot|HTTP Error 403: Forbidden/i,
    envProof: (env) => env.platform !== "win32" && env.networkProbe?.["avkit_download.cancel"] === false,
  },
  {
    key: "avkit_transcript.add",
    signature: BOT_WALL,
    envProof: (env) => env.networkProbe?.["avkit_transcript.add"] === false,
  },
  {
    // youtube-transcript-api from a datacenter IP raises RequestBlocked/IpBlocked, so every item
    // fails and compile has nothing to collect. Proof: a direct caption fetch of the fixture's
    // first video, through the product's own TranscriptAdapter, raises the retryable block error
    // (captions simply missing does not count).
    key: "avkit_transcript.compile",
    signature: /^no transcript fetched/,
    envProof: (env) => env.networkProbe?.["avkit_transcript.compile"] === false,
  },
];
