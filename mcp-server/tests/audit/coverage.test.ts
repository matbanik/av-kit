import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { baselineCoverage, coverage, parseBaseline } from "../../scripts/audit/classify.js";
import { CleanupLedger } from "../../scripts/audit/ledger.js";
import { AUDIT_PLAN, planKeys, type StepContext } from "../../scripts/audit/plan.js";
import { ACTION_INDEX } from "../../src/toolsets/registry.js";

const ACTION_SET = ACTION_INDEX.map((row) => `${row.tool}.${row.action}`);
const COMMITTED_BASELINE = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../../../.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json",
);
// D-499 A (Session 59, MEU-130): served actions the committed baseline doesn't hold yet,
// because YOUTUBE-CAPTIONS-IP-BLOCK blocks an authoritative --update-baseline. That update
// adds them, empties this list and closes MCP-AUDIT-BASELINE-PENDING-CROP.
// MEU-133 (Session 62): + avkit_convert.probe on the same terms. The list is in
// ACTION_INDEX order, because baselineCoverage reports `missing` in that order.
// MEU-134 (Session 62): + avkit_capture.frames, after crop.
// MEU-135 (Session 63): + avkit_capture.sheet, after frames.
// MEU-136 (Session 64): + avkit_capture.export, after sheet.
const BASELINE_PENDING = [
  "avkit_convert.probe",
  "avkit_capture.crop",
  "avkit_capture.frames",
  "avkit_capture.sheet",
  "avkit_capture.export",
];

/** The pending keys that aren't served, or that the baseline already holds. */
function pendingProblems(pending: string[], baselineKeys: string[], served: string[]): string[] {
  return pending.flatMap((key) => [
    ...(served.includes(key) ? [] : [`${key} is not served`]),
    ...(baselineKeys.includes(key) ? [`${key} is already in the baseline`] : []),
  ]);
}

describe("AC-68.5 AUDIT_PLAN coverage of AUDIT_ACTION_SET", () => {
  // 68 since MEU-62 appended avkit_models.download_asset (registry.ts; plan amendment A7).
  // TA-1 (Session 30, MEU-67): 70 with avkit_capture.flatten and avkit_capture.revert.
  // MEU-130 (Session 59): 71 with avkit_capture.crop.
  // MEU-133 (Session 62): 72 with avkit_convert.probe.
  // MEU-134 (Session 62): 73 with avkit_capture.frames.
  // MEU-135 (Session 63): 74 with avkit_capture.sheet.
  // MEU-136 (Session 64): 75 with avkit_capture.export.
  it("AC-68.5 AUDIT_ACTION_SET is the 75 registry rows", () => {
    expect(ACTION_SET).toHaveLength(75);
    expect(new Set(ACTION_SET).size).toBe(75);
  });

  it("AC-68.5 every registry action appears in at least one AUDIT_PLAN step", () => {
    expect(coverage(planKeys(AUDIT_PLAN), ACTION_SET)).toEqual([]);
  });

  it("AC-68.5 the plan calls no action outside the registry", () => {
    expect(planKeys(AUDIT_PLAN).filter((key) => !ACTION_SET.includes(key))).toEqual([]);
  });

  it("AC-68.5 removing a step reports its action as missing", () => {
    const victim = AUDIT_PLAN.find((s) => s.tool === "avkit_tts" && s.action === "voices");
    expect(victim).toBeDefined();
    const reduced = AUDIT_PLAN.filter((s) => !(s.tool === "avkit_tts" && s.action === "voices"));
    expect(coverage(planKeys(reduced), ACTION_SET)).toEqual(["avkit_tts.voices"]);
  });

  it("AC-68.5 step ids are unique and every depends_on names an earlier step", () => {
    const seen = new Set<string>();
    for (const s of AUDIT_PLAN) {
      expect(seen.has(s.id), s.id).toBe(false);
      for (const dep of s.depends_on) expect(seen.has(dep), `${s.id} -> ${dep}`).toBe(true);
      seen.add(s.id);
    }
  });

  it("AC-68.5 every destructive action is exercised through a refusal step", () => {
    const destructive = AUDIT_PLAN.filter((s) => s.destructive).map((s) => `${s.tool}.${s.action}`).sort();
    // TA-3 (Session 30, MEU-67): + capture flatten and revert.
    expect(destructive).toEqual([
      "avkit_capture.flatten",
      "avkit_capture.remove",
      "avkit_capture.revert",
      "avkit_convert.clear",
      "avkit_convert.remove",
      "avkit_download.clear",
      "avkit_download.remove",
      "avkit_transcript.remove",
      "avkit_tts.cancel",
    ]);
  });

  it("AC-68.5 baseline coverage reports missing and extra actions against AUDIT_ACTION_SET", () => {
    const entries = ACTION_SET.filter((k) => k !== "avkit_tts.voices").map((k) => {
      const [tool, action] = k.split(".") as [string, string];
      return { tool, action };
    });
    entries.push({ tool: "avkit_tts", action: "ghost" });
    expect(baselineCoverage(entries, ACTION_SET)).toEqual({ missing: ["avkit_tts.voices"], extra: ["avkit_tts.ghost"] });
    const full = ACTION_SET.map((k) => {
      const [tool, action] = k.split(".") as [string, string];
      return { tool, action };
    });
    expect(baselineCoverage(full, ACTION_SET)).toEqual({ missing: [], extra: [] });
  });

  // Second clause of AC-68.5: once the baseline exists (Part B), it covers exactly the served set.
  it("AC-68.5 the committed baseline's entries equal AUDIT_ACTION_SET less BASELINE_PENDING and every non-pass carries an issue", () => {
    // Part B committed it; from here on a missing baseline is a failure, never a skip (review R2-1).
    expect(existsSync(COMMITTED_BASELINE), COMMITTED_BASELINE).toBe(true);
    const baseline = parseBaseline(JSON.parse(readFileSync(COMMITTED_BASELINE, "utf8")));
    // D-499 A: the baseline misses exactly the pending keys and holds nothing extra.
    expect(baselineCoverage(baseline.entries, ACTION_SET)).toEqual({ missing: BASELINE_PENDING, extra: [] });
    expect(baseline.entries.filter((e) => e.status !== "pass" && !e.issue).map((e) => `${e.tool}.${e.action}`)).toEqual([]);
    expect(baseline.findings.filter((f) => !f.issue).map((f) => `${f.code}:${f.tool}`)).toEqual([]);
  });
});

// MEU-130 capture-crop-copy (Session 59): the audit plan's crop step (D-492) and D-499 A.
describe("MEU-130 crop audit", () => {
  it("AC-130.27 AUDIT_PLAN crops after revert", async () => {
    const ids = AUDIT_PLAN.map((s) => s.id);
    const step = AUDIT_PLAN.find((s) => s.id === "capture.crop");
    expect(step).toBeDefined();
    if (!step) return;
    expect(ids.indexOf("capture.crop")).toBe(ids.indexOf("capture.revert") + 1);
    expect([step.tool, step.action, step.depends_on]).toEqual(["avkit_capture", "crop", ["capture.flatten"]]);
    expect(step.destructive ?? false).toBe(false);
    // The step on a fake context: the args it sends and the shot it registers for cleanup.
    const calls: { tool: string; args: Record<string, unknown> }[] = [];
    const ledger = new CleanupLedger();
    const ctx: StepContext = {
      mode: "container",
      platform: "linux",
      fixtures: {} as unknown as StepContext["fixtures"],
      root: "unused",
      out: (sub) => `unused/${sub}`,
      call: async (tool, args) => {
        calls.push({ tool, args });
        return { isError: false, text: JSON.stringify({ item: { id: "c1", source: "Crop" }, source_id: "s1" }) };
      },
      rest: {
        get: async () => ({ status: 404, json: null, text: "" }),
        send: async () => ({ status: 404, json: null, text: "" }),
        bytes: async () => ({ status: 404, bytes: new Uint8Array() }),
      },
      ledger,
      state: new Map<string, unknown>([["shot_id", "s1"]]),
      firstId: () => "c1",
      poll: async () => null,
    };
    await step.execute(ctx);
    expect(calls).toEqual([
      { tool: "avkit_capture", args: { action: "crop", id: "s1", x: 0, y: 0, width: 8, height: 8 } },
    ]);
    expect(ledger.outstanding()).toEqual([{ kind: "capture", id: "c1" }]);
  });

  it("AC-130.28 the committed baseline misses only the pending keys", () => {
    expect(existsSync(COMMITTED_BASELINE), COMMITTED_BASELINE).toBe(true);
    const baseline = parseBaseline(JSON.parse(readFileSync(COMMITTED_BASELINE, "utf8")));
    const baselineKeys = baseline.entries.map((e) => `${e.tool}.${e.action}`);
    expect(baselineCoverage(baseline.entries, ACTION_SET)).toEqual({ missing: BASELINE_PENDING, extra: [] });
    expect(pendingProblems(BASELINE_PENDING, baselineKeys, ACTION_SET)).toEqual([]);
    // Negative controls: the helper flags a pending key the baseline already holds, and one not served.
    expect(pendingProblems(BASELINE_PENDING, [...baselineKeys, "avkit_capture.crop"], ACTION_SET)).toEqual([
      "avkit_capture.crop is already in the baseline",
    ]);
    expect(pendingProblems(["avkit_capture.ghost"], baselineKeys, ACTION_SET)).toEqual([
      "avkit_capture.ghost is not served",
    ]);
  });
});

// MEU-134 capture-video-frames (Session 62): the audit plan's probe and frames steps.
describe("MEU-134 probe and frames audit", () => {
  it("AC-134.16 AUDIT_PLAN probes after gpu_refresh and grabs frames after crop", async () => {
    const ids = AUDIT_PLAN.map((s) => s.id);
    const frames = AUDIT_PLAN.find((s) => s.id === "capture.frames");
    expect(frames, "capture.frames step").toBeDefined();
    if (!frames) return;
    expect(ids.indexOf("capture.frames")).toBe(ids.indexOf("capture.crop") + 1);
    expect([frames.tool, frames.action]).toEqual(["avkit_capture", "frames"]);
    expect(frames.destructive ?? false).toBe(false);
    const probe = AUDIT_PLAN.find((s) => s.id === "convert.probe");
    expect(probe, "convert.probe step").toBeDefined();
    if (!probe) return;
    expect(ids.indexOf("convert.probe")).toBe(ids.indexOf("convert.gpu_refresh") + 1);
    expect([probe.tool, probe.action]).toEqual(["avkit_convert", "probe"]);
    // The frames step on a fake context, with the probe step's clip already made.
    const calls: { tool: string; args: Record<string, unknown> }[] = [];
    const ledger = new CleanupLedger();
    const clip = "unused/src/probe.mp4";
    const ctx: StepContext = {
      mode: "container",
      platform: "linux",
      fixtures: {} as unknown as StepContext["fixtures"],
      root: "unused",
      out: (sub) => `unused/${sub}`,
      call: async (tool, args) => {
        calls.push({ tool, args });
        return {
          isError: false,
          text: JSON.stringify({
            video: { path: clip, duration_ms: 2000, width: 320, height: 240, fps: 30 },
            frames: [
              { id: "f1", path: "unused/probe-t00h00m00.000s.png", time_ms: 0, timecode: "00:00:00.000", width: 320, height: 240 },
            ],
          }),
        };
      },
      rest: {
        get: async () => ({ status: 404, json: null, text: "" }),
        send: async () => ({ status: 404, json: null, text: "" }),
        bytes: async () => ({ status: 404, bytes: new Uint8Array() }),
      },
      ledger,
      state: new Map<string, unknown>([["probe:src", clip]]),
      firstId: () => "f1",
      poll: async () => null,
    };
    await frames.execute(ctx);
    expect(calls).toEqual([{ tool: "avkit_capture", args: { action: "frames", path: clip, at: [0] } }]);
    expect(ledger.outstanding()).toEqual([{ kind: "capture", id: "f1" }]);
  });

  it("AC-134.16 coverage fails when the frames step is missing", () => {
    const without = AUDIT_PLAN.filter((s) => s.id !== "capture.frames");
    expect(without.length).toBe(AUDIT_PLAN.length - 1);
    expect(coverage(planKeys(without), ACTION_SET)).toEqual(["avkit_capture.frames"]);
    expect(coverage(planKeys(AUDIT_PLAN), ACTION_SET)).toEqual([]);
  });
});

// MEU-135 capture-video-sheet (Session 63): the audit plan's sheet step.
describe("MEU-135 sheet audit", () => {
  it("AC-135.19 sheet parity and audit coverage: AUDIT_PLAN makes a sheet after frames on the probe clip", async () => {
    const ids = AUDIT_PLAN.map((s) => s.id);
    const sheet = AUDIT_PLAN.find((s) => s.id === "capture.sheet");
    expect(sheet, "capture.sheet step").toBeDefined();
    if (!sheet) return;
    expect(ids.indexOf("capture.frames")).toBeGreaterThan(-1);
    expect(ids.indexOf("capture.sheet")).toBe(ids.indexOf("capture.frames") + 1);
    expect([sheet.tool, sheet.action]).toEqual(["avkit_capture", "sheet"]);
    expect(sheet.destructive ?? false).toBe(false);
    // The sheet step on a fake context, with the probe step's clip already made.
    const calls: { tool: string; args: Record<string, unknown> }[] = [];
    const ledger = new CleanupLedger();
    const clip = "unused/src/probe.mp4";
    const ctx: StepContext = {
      mode: "container",
      platform: "linux",
      fixtures: {} as unknown as StepContext["fixtures"],
      root: "unused",
      out: (sub) => `unused/${sub}`,
      call: async (tool, args) => {
        calls.push({ tool, args });
        return {
          isError: false,
          text: JSON.stringify({
            video: { path: clip, duration_ms: 2000, width: 320, height: 240, fps: 30 },
            shot: { id: "sh1", path: "unused/probe-sheet-00h00m00s-00h00m02s.png", width: 1250, height: 938 },
            spacing_ms: 500,
            cells: [
              { cell: 1, time_ms: 250, timecode: "00:00:00.250" },
              { cell: 2, time_ms: 750, timecode: "00:00:00.750" },
              { cell: 3, time_ms: 1250, timecode: "00:00:01.250" },
              { cell: 4, time_ms: 1750, timecode: "00:00:01.750" },
            ],
          }),
        };
      },
      rest: {
        get: async () => ({ status: 200, json: { id: "sh1" }, text: "" }),
        send: async () => ({ status: 404, json: null, text: "" }),
        bytes: async () => ({ status: 404, bytes: new Uint8Array() }),
      },
      ledger,
      state: new Map<string, unknown>([["probe:src", clip]]),
      firstId: () => "sh1",
      poll: async () => null,
    };
    const outcome = await sheet.execute(ctx);
    expect(calls).toEqual([{ tool: "avkit_capture", args: { action: "sheet", path: clip, grid: 2 } }]);
    expect(ledger.outstanding()).toEqual([{ kind: "capture", id: "sh1" }]);
    // NO_RAW_OUTPUT: the step's observation names the cell count and the shot id, never a path.
    const observed = JSON.stringify((outcome as { observable?: unknown }).observable ?? null);
    expect(observed).toContain("4");
    expect(observed).toContain("sh1");
    expect(observed).not.toContain("unused/");
  });

  it("AC-135.19 sheet parity and audit coverage: coverage fails when the sheet step is missing", () => {
    const without = AUDIT_PLAN.filter((s) => s.id !== "capture.sheet");
    expect(without.length).toBe(AUDIT_PLAN.length - 1);
    expect(coverage(planKeys(without), ACTION_SET)).toEqual(["avkit_capture.sheet"]);
    expect(coverage(planKeys(AUDIT_PLAN), ACTION_SET)).toEqual([]);
  });

  it("AC-135.19 sheet parity and audit coverage: BASELINE_PENDING ends with the served sheet action", () => {
    // MEU-136 (Session 64): avkit_capture.export follows sheet and is last.
    expect(BASELINE_PENDING.slice(-2)).toEqual(["avkit_capture.sheet", "avkit_capture.export"]);
    expect(ACTION_SET).toContain("avkit_capture.sheet");
    expect(ACTION_SET.indexOf("avkit_capture.sheet")).toBe(ACTION_SET.indexOf("avkit_capture.frames") + 1);
  });
});

// MEU-136 capture-export-copy (Session 64): EXPORT_AUDIT.
describe("MEU-136 export audit", () => {
  it("AC-136.18 export parity and audit coverage: AUDIT_PLAN has an export step after sheet that depends on crop", () => {
    const ids = AUDIT_PLAN.map((s) => s.id);
    const step = AUDIT_PLAN.find((s) => s.id === "capture.export");
    expect(ids.indexOf("capture.sheet")).toBeGreaterThan(-1);
    expect(ids.indexOf("capture.export")).toBe(ids.indexOf("capture.sheet") + 1);
    expect(
      step && { tool: step.tool, action: step.action, phase: step.phase, deps: step.depends_on },
    ).toEqual({ tool: "avkit_capture", action: "export", phase: "lifecycle", deps: ["capture.crop"] });
    expect(step?.destructive ?? false).toBe(false);
    expect(ids.indexOf("capture.crop")).toBeLessThan(ids.indexOf("capture.export"));
  });

  it("AC-136.18 export parity and audit coverage: coverage fails when the export step is missing", () => {
    const without = AUDIT_PLAN.filter((s) => s.id !== "capture.export");
    expect(without.length).toBe(AUDIT_PLAN.length - 1);
    expect(coverage(planKeys(without), ACTION_SET)).toEqual(["avkit_capture.export"]);
    expect(coverage(planKeys(AUDIT_PLAN), ACTION_SET)).toEqual([]);
  });

  it("AC-136.18 export parity and audit coverage: BASELINE_PENDING ends with the served export action", () => {
    expect(BASELINE_PENDING[BASELINE_PENDING.length - 1]).toBe("avkit_capture.export");
    expect(ACTION_SET).toContain("avkit_capture.export");
    expect(ACTION_SET.indexOf("avkit_capture.export")).toBe(ACTION_SET.indexOf("avkit_capture.sheet") + 1);
  });
});
