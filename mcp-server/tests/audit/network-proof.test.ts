import { describe, expect, it } from "vitest";
import { AUDIT_FIXTURES, type Fixtures } from "../../scripts/audit/fixtures.js";
import * as np from "../../scripts/audit/network-proof.js";
import { AUDIT_PLAN } from "../../scripts/audit/plan.js";
import type { StepRecord } from "../../scripts/audit/types.js";

// Session 92 (D-1156, D-1160; MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT). The tests drive
// gatherNetworkProof and sampleBlocked through fake NetworkProbes that count calls and record
// sleeps; none spawns uv, reaches the network or sleeps.

const FIXTURES: Fixtures = { ...AUDIT_FIXTURES };
const BOT_WALL = "ExtractError: ERROR: [youtube] x: Sign in to confirm you're not a bot";
const NO_TRANSCRIPT = "no transcript fetched for 3 items";
const URL_A = FIXTURES.download_url_a;
const URL_C = FIXTURES.download_url_c;
const SOURCE = FIXTURES.transcript_source_url;

type Answers = { extract?: Record<string, boolean[]>; media?: boolean[]; captions?: boolean[] };
type Fake = np.NetworkProbes & {
  extractCalls: string[];
  mediaCalls: { url: string; wall: RegExp }[];
  captionCalls: string[];
  sleeps: number[];
};

/** Each probe returns its next scripted answer (true: blocked), then false (works). */
function fakeProbes(answers: Answers = {}): Fake {
  const extractSeen: Record<string, number> = {};
  const fake: Fake = {
    extractCalls: [],
    mediaCalls: [],
    captionCalls: [],
    sleeps: [],
    extractBlocked(url) {
      fake.extractCalls.push(url);
      const i = extractSeen[url] ?? 0;
      extractSeen[url] = i + 1;
      return answers.extract?.[url]?.[i] ?? false;
    },
    mediaBlocked(url, wall) {
      fake.mediaCalls.push({ url, wall });
      return answers.media?.[fake.mediaCalls.length - 1] ?? false;
    },
    captionsBlocked(url) {
      fake.captionCalls.push(url);
      return answers.captions?.[fake.captionCalls.length - 1] ?? false;
    },
    sleep(ms) {
      fake.sleeps.push(ms);
    },
  };
  return fake;
}

function calls(list: string[], url: string): number {
  return list.filter((u) => u === url).length;
}

function rec(id: string, tool: string, action: string, verdict: "pass" | "fail", error: string | null = null): StepRecord {
  return { id, tool, action, verdict, error } as StepRecord;
}

/** A record set that fails every ENV_BOUND_AUDIT member with its own signature. */
const ALL_FAILING: StepRecord[] = [
  rec("capture.capture", "avkit_capture", "capture", "fail", "internal_error"),
  rec("download.add.a", "avkit_download", "add", "fail", BOT_WALL),
  rec("download.add.c", "avkit_download", "add", "fail", BOT_WALL),
  rec("download.cancel", "avkit_download", "cancel", "fail", BOT_WALL),
  rec("transcript.add", "avkit_transcript", "add", "fail", BOT_WALL),
  rec("transcript.compile", "avkit_transcript", "compile", "fail", NO_TRANSCRIPT),
];

function gather(records: StepRecord[], probes: np.NetworkProbes, mode: "container" | "authoritative" = "container") {
  return np.gatherNetworkProof({ mode, fixtures: FIXTURES, steps: AUDIT_PLAN, records, probes });
}

describe("Session 92 census network proof", () => {
  it("AC-1 NETWORK_PROOF_SAMPLES is 3 and NETWORK_PROOF_GAP_MS is 5000", () => {
    expect(np.NETWORK_PROOF_SAMPLES).toBe(3);
    expect(np.NETWORK_PROOF_GAP_MS).toBe(5000);
  });

  it("AC-1 sampleBlocked with tries false, false, true returns true after 3 calls and 2 sleeps of 5000", () => {
    const probes = fakeProbes();
    const tries = [false, false, true];
    let n = 0;
    const blocked = np.sampleBlocked(() => tries[n++] ?? false, probes);
    expect(n).toBe(3);
    expect(probes.sleeps).toEqual([5000, 5000]);
    expect(blocked).toBe(true);
  });

  it("AC-1 sampleBlocked with every try false returns false after exactly 3 calls", () => {
    const probes = fakeProbes();
    let n = 0;
    const blocked = np.sampleBlocked(() => {
      n++;
      return false;
    }, probes);
    expect(n).toBe(3);
    expect(probes.sleeps).toEqual([5000, 5000]);
    expect(blocked).toBe(false);
  });

  it("AC-2 add and transcript: a URL blocked only at its second try lets the proof hold", () => {
    const probes = fakeProbes({ extract: { [URL_A]: [false, true], [URL_C]: [true], [SOURCE]: [false, true] } });
    const probe = gather(ALL_FAILING, probes);
    expect(calls(probes.extractCalls, URL_A)).toBe(2);
    expect(calls(probes.extractCalls, URL_C)).toBe(1);
    expect(calls(probes.extractCalls, SOURCE)).toBe(2);
    expect(probe?.["avkit_download.add"]).toBe(false);
    expect(probe?.["avkit_transcript.add"]).toBe(false);
  });

  it("AC-2 add and transcript: a URL that works at all three tries counts the failure after 3 calls for that URL", () => {
    const probes = fakeProbes({ extract: { [URL_A]: [true] } });
    const probe = gather(ALL_FAILING, probes);
    expect(calls(probes.extractCalls, URL_A)).toBe(1);
    expect(calls(probes.extractCalls, URL_C)).toBe(3);
    expect(calls(probes.extractCalls, SOURCE)).toBe(3);
    expect(probe?.["avkit_download.add"]).toBe(true);
    expect(probe?.["avkit_transcript.add"]).toBe(true);
  });

  it("AC-3 cancel and compile: a fetch blocked only at its second try lets the proof hold", () => {
    const probes = fakeProbes({ extract: { [URL_A]: [true], [URL_C]: [true], [SOURCE]: [true] }, media: [false, true], captions: [false, true] });
    const probe = gather(ALL_FAILING, probes);
    expect(probes.mediaCalls.length).toBe(2);
    expect(probes.captionCalls.length).toBe(2);
    expect(probes.mediaCalls.every((c) => c.url === URL_C && c.wall.test("HTTP Error 403: Forbidden"))).toBe(true);
    expect(probes.captionCalls.every((u) => u === SOURCE)).toBe(true);
    expect(probe?.["avkit_download.cancel"]).toBe(false);
    expect(probe?.["avkit_transcript.compile"]).toBe(false);
  });

  it("AC-3 cancel and compile: a fetch that works at all three tries counts the failure after 3 calls", () => {
    const probes = fakeProbes({ extract: { [URL_A]: [true], [URL_C]: [true], [SOURCE]: [true] } });
    const probe = gather(ALL_FAILING, probes);
    expect(probes.mediaCalls.length).toBe(3);
    expect(probes.captionCalls.length).toBe(3);
    expect(probe?.["avkit_download.cancel"]).toBe(true);
    expect(probe?.["avkit_transcript.compile"]).toBe(true);
  });

  it("AC-5 authoritative mode gives undefined and calls no probe", () => {
    const probes = fakeProbes({ extract: { [URL_A]: [true], [URL_C]: [true], [SOURCE]: [true] }, media: [true], captions: [true] });
    expect(gather(ALL_FAILING, probes, "authoritative")).toBeUndefined();
    expect([probes.extractCalls, probes.mediaCalls, probes.captionCalls, probes.sleeps].map((l) => l.length)).toEqual([0, 0, 0, 0]);
  });

  it("AC-5 no fixtures gives undefined", () => {
    const probes = fakeProbes();
    const probe = np.gatherNetworkProof({ mode: "container", fixtures: null, steps: AUDIT_PLAN, records: ALL_FAILING, probes });
    expect(probe).toBeUndefined();
    expect([probes.extractCalls, probes.mediaCalls, probes.captionCalls].map((l) => l.length)).toEqual([0, 0, 0]);
  });

  it("AC-5 no failing record that matches a signature gives undefined", () => {
    const probes = fakeProbes();
    const passing = ALL_FAILING.map((r) => ({ ...r, verdict: "pass" as const, error: null }));
    expect(gather(passing, probes)).toBeUndefined();
    expect([probes.extractCalls, probes.mediaCalls, probes.captionCalls].map((l) => l.length)).toEqual([0, 0, 0]);
  });

  it("AC-5 a failing record with another signature is not probed", () => {
    const probes = fakeProbes({ extract: { [SOURCE]: [true] } });
    const records = [
      rec("download.add.a", "avkit_download", "add", "fail", "internal_error"),
      rec("download.cancel", "avkit_download", "cancel", "fail", "timed out waiting for Downloading"),
      rec("transcript.add", "avkit_transcript", "add", "fail", BOT_WALL),
      rec("transcript.compile", "avkit_transcript", "compile", "fail", "compile returned 0 files"),
    ];
    const probe = gather(records, probes);
    expect(Object.keys(probe ?? {})).toEqual(["avkit_transcript.add"]);
    expect(probes.extractCalls).toEqual([SOURCE]);
    expect([probes.mediaCalls.length, probes.captionCalls.length]).toEqual([0, 0]);
  });

  it("AC-5 the probed keys equal the row-0 rule's for a record set that fails every member", () => {
    const probes = fakeProbes({ extract: { [URL_A]: [true], [URL_C]: [true], [SOURCE]: [true] }, media: [true], captions: [true] });
    const probe = gather(ALL_FAILING, probes);
    expect(Object.keys(probe ?? {}).sort()).toEqual([
      "avkit_download.add",
      "avkit_download.cancel",
      "avkit_transcript.add",
      "avkit_transcript.compile",
    ]);
    expect(Object.values(probe ?? {})).toEqual([false, false, false, false]);
  });

  it("AC-5 a URL blocked at its first try is called once, with no sleep", () => {
    const probes = fakeProbes({ extract: { [URL_A]: [true] } });
    const probe = gather([rec("download.add.a", "avkit_download", "add", "fail", BOT_WALL)], probes);
    expect(probes.extractCalls).toEqual([URL_A]);
    expect(probes.sleeps).toEqual([]);
    expect(probe).toEqual({ "avkit_download.add": false });
  });
});
