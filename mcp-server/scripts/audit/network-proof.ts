/**
 * Census network proof (Session 92, D-1156, D-1160; MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT). The
 * container audit's environment proof for the network census members, moved from run.ts with
 * its rules unchanged except for the sampling: each direct fetch is tried up to
 * NETWORK_PROOF_SAMPLES times, NETWORK_PROOF_GAP_MS apart, and counts as blocked at the first
 * blocked try. The probes sit behind NetworkProbes so the tests drive gatherNetworkProof and
 * sampleBlocked with fakes; the runner passes REAL_PROBES.
 */
import { spawnSync } from "node:child_process";
import { REPO_ROOT } from "./backend.js";
import { ENV_BOUND_AUDIT } from "./census.js";
import type { Fixtures } from "./fixtures.js";
import { NETWORK_STEP_URLS, type StepSpec } from "./plan.js";
import type { Mode, StepRecord } from "./types.js";

/** How many times each network proof is tried (D-1156). */
export const NETWORK_PROOF_SAMPLES = 3;
/** The wait between two tries, in milliseconds (D-1156). */
export const NETWORK_PROOF_GAP_MS = 5000;

/** The direct fetches the census proof makes, and the wait between two tries (D-1160). */
export type NetworkProbes = {
  extractBlocked(url: string): boolean;
  mediaBlocked(url: string, wall: RegExp): boolean;
  captionsBlocked(url: string): boolean;
  sleep(ms: number): void;
};

/**
 * Calls `once` up to NETWORK_PROOF_SAMPLES times and returns true at the first call that
 * returns true, false when every call returned false. It sleeps NETWORK_PROOF_GAP_MS between
 * two calls only, never before the first or after the last.
 */
export function sampleBlocked(once: () => boolean, probes: Pick<NetworkProbes, "sleep">): boolean {
  for (let i = 0; i < NETWORK_PROOF_SAMPLES; i++) {
    if (i > 0) probes.sleep(NETWORK_PROOF_GAP_MS);
    if (once()) return true;
  }
  return false;
}

/** Environment proof for the network census members: can yt-dlp extract the fixture at all? */
function youtubeExtractWorks(url: string): boolean {
  const code = [
    "import sys, yt_dlp",
    "with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as y:",
    "    y.extract_info(sys.argv[1], download=False)",
  ].join("\n");
  const res = spawnSync("uv", ["run", "python", "-c", code, url], {
    cwd: REPO_ROOT,
    encoding: "utf8",
    timeout: 180_000,
  });
  return res.status === 0;
}

/** True only when a direct yt-dlp test fetch (first bytes of the media) fails with `wall`. */
function mediaFetchBlocked(url: string, wall: RegExp): boolean {
  const code = [
    "import sys, tempfile, yt_dlp",
    "with tempfile.TemporaryDirectory() as d:",
    "    opts = {'quiet': True, 'no_warnings': True, 'format': 'worst', 'test': True, 'outtmpl': d + '/%(id)s.%(ext)s'}",
    "    try:",
    "        with yt_dlp.YoutubeDL(opts) as y:",
    "            y.download([sys.argv[1]])",
    "    except Exception as exc:",
    "        print(str(exc))",
    "        sys.exit(3)",
  ].join("\n");
  const res = spawnSync("uv", ["run", "python", "-c", code, url], {
    cwd: REPO_ROOT,
    encoding: "utf8",
    timeout: 180_000,
  });
  return res.status === 3 && wall.test(`${res.stdout ?? ""}${res.stderr ?? ""}`);
}

/** True only when the product's TranscriptAdapter is IP-blocked for the source's first video. */
function captionFetchBlocked(sourceUrl: string): boolean {
  const code = [
    "import sys, yt_dlp",
    "from avkit_core.domain.errors import TranscriptRetryableError",
    "from avkit_infra.transcript.adapter import TranscriptAdapter",
    "with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True, 'extract_flat': True}) as y:",
    "    info = y.extract_info(sys.argv[1], download=False)",
    "entries = info.get('entries') or [info]",
    "try:",
    "    TranscriptAdapter().get_transcript(entries[0]['id'], ['en'])",
    "except TranscriptRetryableError:",
    "    sys.exit(3)",
  ].join("\n");
  const res = spawnSync("uv", ["run", "python", "-c", code, sourceUrl], {
    cwd: REPO_ROOT,
    encoding: "utf8",
    timeout: 180_000,
  });
  return res.status === 3;
}

/** The runner's probes: the three direct fetches above and a synchronous sleep. */
export const REAL_PROBES: NetworkProbes = {
  extractBlocked: (url) => !youtubeExtractWorks(url),
  mediaBlocked: (url, wall) => mediaFetchBlocked(url, wall),
  captionsBlocked: (url) => captionFetchBlocked(url),
  // Blocks the thread, so the census block in runAudit stays synchronous.
  sleep: (ms) => {
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
  },
};

export type NetworkProofInput = {
  mode: Mode;
  fixtures: Fixtures | null | undefined;
  steps: readonly Pick<StepSpec, "id" | "tool" | "action">[];
  records: readonly Pick<StepRecord, "id" | "tool" | "action" | "verdict" | "error">[];
  probes: NetworkProbes;
};

/**
 * The census network proof (the row-0 rules of run.ts, each fetch sampled): undefined unless
 * the mode is container and fixtures are set. Only the ENV_BOUND_AUDIT members whose steps are
 * in NETWORK_STEP_URLS and that have a failing record matching their signature are probed, each
 * URL on its own, plus cancel (the media wall on download_url_c) and compile (the retryable
 * caption error on transcript_source_url). A key is false (the proof holds) when the fetch was
 * blocked; undefined when no key was probed.
 */
export function gatherNetworkProof(input: NetworkProofInput): Record<string, boolean> | undefined {
  const { mode, fixtures, steps, records, probes } = input;
  if (mode !== "container" || !fixtures) return undefined;
  const networkKeys = new Set(
    steps.filter((s) => s.id in NETWORK_STEP_URLS).map((s) => `${s.tool}.${s.action}`),
  );
  const networkCandidates = ENV_BOUND_AUDIT.filter((m) => networkKeys.has(m.key));
  const probe: Record<string, boolean> = {};
  for (const member of networkCandidates) {
    const failing = records.filter(
      (r) => r.verdict === "fail" && `${r.tool}.${r.action}` === member.key && member.signature.test(r.error ?? ""),
    );
    if (failing.length === 0) continue;
    const urls = [...new Set(failing.map((r) => NETWORK_STEP_URLS[r.id]).map((k) => (k ? fixtures[k] : undefined)))];
    // Proof holds only if every failing step's own URL is also blocked at one of its tries.
    probe[member.key] = !urls.every(
      (url) => url !== undefined && sampleBlocked(() => probes.extractBlocked(url), probes),
    );
  }
  const cancel = ENV_BOUND_AUDIT.find((m) => m.key === "avkit_download.cancel");
  const cancelFailed = records.some(
    (r) => r.verdict === "fail" && cancel && `${r.tool}.${r.action}` === cancel.key && cancel.signature.test(r.error ?? ""),
  );
  if (cancel && cancelFailed) {
    probe[cancel.key] = !sampleBlocked(() => probes.mediaBlocked(fixtures.download_url_c, cancel.signature), probes);
  }
  const compile = ENV_BOUND_AUDIT.find((m) => m.key === "avkit_transcript.compile");
  const compileFailed = records.some(
    (r) => r.verdict === "fail" && compile && `${r.tool}.${r.action}` === compile.key && compile.signature.test(r.error ?? ""),
  );
  if (compile && compileFailed) {
    probe[compile.key] = !sampleBlocked(() => probes.captionsBlocked(fixtures.transcript_source_url), probes);
  }
  return Object.keys(probe).length > 0 ? probe : undefined;
}
