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
const BASELINE_PENDING = ["avkit_capture.crop"];

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
  it("AC-68.5 AUDIT_ACTION_SET is the 71 registry rows", () => {
    expect(ACTION_SET).toHaveLength(71);
    expect(new Set(ACTION_SET).size).toBe(71);
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
