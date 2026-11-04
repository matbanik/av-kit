/**
 * AUDIT_FIXTURES (plan §Single-statement contracts, D-7 as amended by A4). Every value can be
 * overridden with `--fixture key=value`. All YouTube use is read-only consumption (PROFILE E3).
 */

export const AUDIT_FIXTURES = {
  /** 19 s "Me at the zoo": the download that completes. */
  download_url_a: "https://www.youtube.com/watch?v=jNQXAC9IVRw",
  /** The backend's own SABR_PROBE_URL (youtube/adapter.py:82): a queued item never started. */
  download_url_b: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  /** Big Buck Bunny (10 min, CC-BY): long enough to be the deterministic cancel target. */
  download_url_c: "https://www.youtube.com/watch?v=aqz-KE-bpKQ",
  /**
   * Blender Studio's public "Live: Rigging Snow" playlist (9 videos): two pause→stop cycles need
   * at least 3 fetched items (A4a). A9 replaced a watch_videos anonymous list, which the backend's
   * YouTubeAdapter cannot extract (AttributeError on its flat entries).
   */
  transcript_source_url: "https://www.youtube.com/playlist?list=PLav47HAVZMjnA3P7yQvneyQPiVxZ6erFS",
  tts_voice: "af_heart",
  /** Short on purpose: the generate step waits for Done within the audit's TTS timeout. */
  tts_text: "The audit checks every tool.",
  /** AUDIT_CANCEL_STEP: long enough (about 3,500 characters) to still be Generating at cancel. */
  tts_cancel_text: Array(60).fill("The audit keeps this job running long enough to cancel it.").join(" "),
  /** Preferred model format; the smallest variant of this format is downloaded. */
  model_format: "ONNX",
} as const;

export type FixtureKey = keyof typeof AUDIT_FIXTURES;
export type Fixtures = { [K in FixtureKey]: string };

/** Applies `--fixture key=value` overrides; unknown keys are an error (fail closed). */
export function resolveFixtures(overrides: Record<string, string>): Fixtures {
  const out: Record<string, string> = { ...AUDIT_FIXTURES };
  for (const [key, value] of Object.entries(overrides)) {
    if (!(key in AUDIT_FIXTURES)) throw new Error(`unknown fixture ${key}`);
    if (value.trim() === "") throw new Error(`fixture ${key} is empty`);
    out[key] = value;
  }
  return out as Fixtures;
}
