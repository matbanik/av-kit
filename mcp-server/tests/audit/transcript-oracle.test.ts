import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { ENV_BOUND_AUDIT } from "../../scripts/audit/census.js";
import { applyTolerance } from "../../scripts/audit/classify.js";
import { CleanupLedger } from "../../scripts/audit/ledger.js";
import { AUDIT_PLAN, type StepContext, type StepOutcome } from "../../scripts/audit/plan.js";
import type { StepRecord, ToolCallOutcome } from "../../scripts/audit/types.js";

const temps: string[] = [];
afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

function step(id: string) {
  const found = AUDIT_PLAN.find((s) => s.id === id);
  if (!found) throw new Error(`no step ${id}`);
  return found;
}

/** A context whose REST transcript row is `job` and whose MCP call returns `result`. */
function ctxFor(job: Record<string, unknown>, result: ToolCallOutcome, root: string): StepContext {
  const state = new Map<string, unknown>([["tr_id", "tr1"]]);
  return {
    mode: "container",
    platform: "linux",
    fixtures: {} as StepContext["fixtures"],
    root,
    out: (sub) => path.join(root, "out", sub),
    call: async () => result,
    rest: {
      get: async (p) => (p === "/transcripts/tr1" ? { status: 200, json: job, text: JSON.stringify(job) } : { status: 404, json: null, text: "" }),
      send: async () => ({ status: 200, json: null, text: "" }),
      bytes: async () => ({ status: 404, bytes: new Uint8Array() }),
    },
    ledger: new CleanupLedger(),
    state,
    firstId: () => null,
    // One evaluation: the observable must decide on the state it reads, not on waiting.
    poll: async (probe) => probe(),
  };
}

function observable(outcome: StepOutcome): { ok: boolean; detail: string } {
  if (outcome.kind !== "simple" || !outcome.observable) throw new Error(`unexpected outcome ${outcome.kind}`);
  return outcome.observable;
}

function root(): string {
  const dir = mkdtempSync(path.join(os.tmpdir(), "s28-transcript-oracle-"));
  temps.push(dir);
  return dir;
}

const OK: ToolCallOutcome = { isError: false, text: "{}" };

/** A compile volume as `_volume_markdown` writes it, with one `## title` section per item. */
function volume(dir: string, titles: string[]): string {
  const file = path.join(dir, "out", "transcripts", "compiled", "chan_vol1.md");
  mkdirSync(path.dirname(file), { recursive: true });
  const lines = ["# chan", "", "## Contents", ...titles.map((t) => `- [${t}](#${t})`), ""];
  for (const t of titles) lines.push(`## ${t}`, "", "some words", "");
  writeFileSync(file, lines.join("\n"), "utf8");
  return file;
}

describe("AC-68.6 transcript lifecycle observes a fetched item (plan AUDIT_PLAN transcript row)", () => {
  it("AC-68.6 resume fails while no item is terminal (pause before item 0 fetches nothing)", async () => {
    const r = root();
    const job = { status: "Processing", transcripts_done: 0, last_item_status: "Pending" };
    const o = observable(await step("transcript.resume").execute(ctxFor(job, OK, r)));
    expect(o.ok).toBe(false);
    expect(o.detail).toContain("last_item_status Pending");
  });

  it("AC-68.6 resume passes once a transcript is fetched or an item failed, and records the item counts", async () => {
    const r = root();
    for (const [last, done] of [
      ["Done", 1],
      ["Failed", 0],
    ] as const) {
      const job = { status: "Processing", transcripts_done: done, last_item_status: last };
      const o = observable(await step("transcript.resume").execute(ctxFor(job, OK, r)));
      expect(o.ok, last).toBe(true);
      expect(o.detail, last).toContain(`last_item_status ${last}`);
      expect(o.detail, last).toContain(`transcripts_done ${done}`);
    }
  });

  it("AC-68.6 a Skipped item (no captions) alone does not end the resume poll", async () => {
    const r = root();
    const job = { status: "Processing", transcripts_done: 0, last_item_status: "Skipped" };
    expect(observable(await step("transcript.resume").execute(ctxFor(job, OK, r))).ok).toBe(false);
  });

  it("AC-68.6 compile with no fetched transcript is hollow even though a volume file exists", async () => {
    const r = root();
    const file = volume(r, []);
    const job = { status: "Pending", transcripts_done: 0, last_item_status: "Failed" };
    const o = observable(await step("transcript.compile").execute(ctxFor(job, { isError: false, text: JSON.stringify({ compiled_paths: [file] }) }, r)));
    expect(o.ok).toBe(false);
    expect(o.detail).toContain("no transcript fetched");
  });

  it("AC-68.6 compile passes when its sections match the fetched transcripts", async () => {
    const r = root();
    const file = volume(r, ["First video"]);
    const job = { status: "Pending", transcripts_done: 1, last_item_status: "Done" };
    const o = observable(await step("transcript.compile").execute(ctxFor(job, { isError: false, text: JSON.stringify({ compiled_paths: [file] }) }, r)));
    expect(o.ok).toBe(true);
    expect(o.detail).toContain("1 section(s), transcripts_done 1");
  });

  it("AC-68.6 compile fails when its sections disagree with REST transcripts_done", async () => {
    const r = root();
    const file = volume(r, ["First video"]);
    const job = { status: "Pending", transcripts_done: 2, last_item_status: "Done" };
    const o = observable(await step("transcript.compile").execute(ctxFor(job, { isError: false, text: JSON.stringify({ compiled_paths: [file] }) }, r)));
    expect(o.ok).toBe(false);
    expect(o.detail).toContain("1 section(s), transcripts_done 2");
  });
});

describe("AC-68.12 the compile census member needs its signature and its proof", () => {
  const record: StepRecord = {
    id: "transcript.compile",
    tool: "avkit_transcript",
    action: "compile",
    phase: "lifecycle",
    verdict: "fail",
    reason: "hollow",
    is_error: false,
    observable: "no transcript fetched (transcripts_done 0, last_item_status Failed)",
    error: "no transcript fetched (transcripts_done 0, last_item_status Failed)",
    blocked_by: null,
    env_bound: null,
    ms: 1,
  };

  it("AC-68.12 a blocked caption fetch on the container host is skip_env", () => {
    const [r] = applyTolerance([record], "container", ENV_BOUND_AUDIT, { platform: "linux", networkProbe: { "avkit_transcript.compile": false } });
    expect(r.verdict).toBe("skip_env");
  });

  it("AC-68.12 without the proof, or in authoritative mode, it stays a failure", () => {
    expect(applyTolerance([record], "container", ENV_BOUND_AUDIT, { platform: "linux" })[0].verdict).toBe("fail");
    expect(applyTolerance([record], "container", ENV_BOUND_AUDIT, { platform: "linux", networkProbe: { "avkit_transcript.compile": true } })[0].verdict).toBe("fail");
    expect(applyTolerance([record], "authoritative", ENV_BOUND_AUDIT, { platform: "win32", networkProbe: { "avkit_transcript.compile": false } })[0].verdict).toBe("fail");
  });

  it("AC-68.12 a different compile failure does not match the signature", () => {
    const other = { ...record, error: "live-x_vol1.md outside isolated root", observable: "live-x_vol1.md outside isolated root" };
    expect(applyTolerance([other], "container", ENV_BOUND_AUDIT, { platform: "linux", networkProbe: { "avkit_transcript.compile": false } })[0].verdict).toBe("fail");
  });
});

describe("AC-68.6 transcript 409 conflict contract covers requeue and retry (plan AUDIT_PLAN transcript row)", () => {
  it("AC-68.6 requeue and retry each run once on an illegal state and expect the conflict", () => {
    const conflicts = AUDIT_PLAN.filter((s) => s.tool === "avkit_transcript" && /\.conflict$/.test(s.id)).map((s) => s.action).sort();
    expect(conflicts).toEqual(["requeue", "retry"]);
  });

  it("AC-68.6 requeue on a Pending job passes only with the 409 envelope and the status unchanged", async () => {
    const r = root();
    const conflict: ToolCallOutcome = { isError: true, text: "ConflictError: illegal transcript transition Pending -> Pending" };
    const s = step("transcript.requeue.conflict");
    expect(observable(await s.execute(ctxFor({ status: "Pending" }, conflict, r))).ok).toBe(true);
    expect(observable(await s.execute(ctxFor({ status: "Pending" }, OK, r))).ok).toBe(false);
  });
});

describe("AC-68.12 the download.cancel census member needs the media-fetch wall and its direct proof", () => {
  const base: StepRecord = {
    id: "download.cancel",
    tool: "avkit_download",
    action: "cancel",
    phase: "lifecycle",
    verdict: "fail",
    reason: "hollow",
    is_error: false,
    observable: "c never Cancelled; REST c Failed",
    error: "ERROR: unable to download video data: HTTP Error 403: Forbidden",
    blocked_by: null,
    env_bound: null,
    ms: 1,
  };
  const proven = { platform: "linux", networkProbe: { "avkit_download.cancel": false } };

  it("AC-68.12 a 403 media fetch, also failing a direct fetch on the container host, is skip_env", () => {
    expect(applyTolerance([base], "container", ENV_BOUND_AUDIT, proven)[0].verdict).toBe("skip_env");
    const bot = { ...base, error: "ERROR: [youtube] aqz-KE-bpKQ: Sign in to confirm you’re not a bot." };
    expect(applyTolerance([bot], "container", ENV_BOUND_AUDIT, proven)[0].verdict).toBe("skip_env");
  });

  it("AC-68.12 without the direct-fetch proof, on win32, or in authoritative mode it stays a failure", () => {
    expect(applyTolerance([base], "container", ENV_BOUND_AUDIT, { platform: "linux" })[0].verdict).toBe("fail");
    expect(applyTolerance([base], "container", ENV_BOUND_AUDIT, { platform: "win32", networkProbe: { "avkit_download.cancel": false } })[0].verdict).toBe("fail");
    expect(applyTolerance([base], "authoritative", ENV_BOUND_AUDIT, proven)[0].verdict).toBe("fail");
    const other = { ...base, error: "c never Cancelled; REST c Downloading" };
    expect(applyTolerance([other], "container", ENV_BOUND_AUDIT, proven)[0].verdict).toBe("fail");
  });
});
