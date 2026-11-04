import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { baselineCoverage, coverage, parseBaseline } from "../../scripts/audit/classify.js";
import { AUDIT_PLAN, planKeys } from "../../scripts/audit/plan.js";
import { ACTION_INDEX } from "../../src/toolsets/registry.js";

const ACTION_SET = ACTION_INDEX.map((row) => `${row.tool}.${row.action}`);
const COMMITTED_BASELINE = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../../../.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json",
);

describe("AC-68.5 AUDIT_PLAN coverage of AUDIT_ACTION_SET", () => {
  // 68 since MEU-62 appended avkit_models.download_asset (registry.ts; plan amendment A7).
  // TA-1 (Session 30, MEU-67): 70 with avkit_capture.flatten and avkit_capture.revert.
  it("AC-68.5 AUDIT_ACTION_SET is the 70 registry rows", () => {
    expect(ACTION_SET).toHaveLength(70);
    expect(new Set(ACTION_SET).size).toBe(70);
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
  it("AC-68.5 the committed baseline's entries equal AUDIT_ACTION_SET and every non-pass carries an issue", () => {
    // Part B committed it; from here on a missing baseline is a failure, never a skip (review R2-1).
    expect(existsSync(COMMITTED_BASELINE), COMMITTED_BASELINE).toBe(true);
    const baseline = parseBaseline(JSON.parse(readFileSync(COMMITTED_BASELINE, "utf8")));
    expect(baselineCoverage(baseline.entries, ACTION_SET)).toEqual({ missing: [], extra: [] });
    expect(baseline.entries.filter((e) => e.status !== "pass" && !e.issue).map((e) => `${e.tool}.${e.action}`)).toEqual([]);
    expect(baseline.findings.filter((f) => !f.issue).map((f) => `${f.code}:${f.tool}`)).toEqual([]);
  });
});
