import { createHash } from "node:crypto";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  BaselineError,
  baselineUpdateDecision,
  computeDelta,
  parseBaseline,
  writeBaselineIfAllowed,
} from "../../scripts/audit/classify.js";
import type { Baseline } from "../../scripts/audit/types.js";

const COMMIT = "0123456789abcdef0123456789abcdef01234567";

function baseline(entries: Baseline["entries"]): Baseline {
  return {
    schema: "mcp-audit-baseline.v1",
    recorded_commit: COMMIT,
    mode: "authoritative",
    recorded_at: "2026-10-01T00:00:00Z",
    entries,
    findings: [],
  };
}

const temps: string[] = [];
afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("AC-68.10 DELTA classification", () => {
  const prior = baseline([
    { tool: "t", action: "stays_pass", status: "pass" },
    { tool: "t", action: "breaks", status: "pass" },
    { tool: "t", action: "still_broken", status: "fail", issue: "ISSUE-1" },
    { tool: "t", action: "gets_fixed", status: "fail", issue: "ISSUE-2" },
    { tool: "t", action: "gone", status: "pass" },
  ]);
  const current = [
    { key: "t.stays_pass", verdict: "pass" as const },
    { key: "t.breaks", verdict: "fail" as const },
    { key: "t.still_broken", verdict: "fail" as const },
    { key: "t.gets_fixed", verdict: "pass" as const },
    { key: "t.brand_new", verdict: "pass" as const },
  ];
  const deltas = Object.fromEntries(computeDelta(current, prior).map((d) => [d.key, d]));

  it("AC-68.10 pass to non-pass is REGRESSION", () => {
    expect(deltas["t.breaks"]?.delta).toBe("REGRESSION");
  });
  it("AC-68.10 fail to non-pass is KNOWN and carries the baseline issue", () => {
    expect(deltas["t.still_broken"]).toEqual({ key: "t.still_broken", delta: "KNOWN", issue: "ISSUE-1" });
  });
  it("AC-68.10 fail to pass is FIXED", () => {
    expect(deltas["t.gets_fixed"]?.delta).toBe("FIXED");
  });
  it("AC-68.10 an action absent from the baseline is NEW", () => {
    expect(deltas["t.brand_new"]?.delta).toBe("NEW");
  });
  it("AC-68.10 a baselined action not served now is REMOVED", () => {
    expect(deltas["t.gone"]?.delta).toBe("REMOVED");
  });
  it("AC-68.10 pass to pass is UNCHANGED", () => {
    expect(deltas["t.stays_pass"]?.delta).toBe("UNCHANGED");
  });
  it("AC-68.10 with no baseline every current action is NEW", () => {
    expect(computeDelta(current, null).every((d) => d.delta === "NEW")).toBe(true);
  });
});

describe("AC-68.10 baseline schema", () => {
  const good = baseline([{ tool: "t", action: "a", status: "pass" }]);

  it("AC-68.10 a well-formed baseline parses", () => {
    expect(parseBaseline(JSON.parse(JSON.stringify(good)))).toEqual(good);
  });
  it("AC-68.10 a wrong schema id is rejected", () => {
    expect(() => parseBaseline({ ...good, schema: "other.v1" })).toThrow(BaselineError);
  });
  it("AC-68.10 a duplicate entry is rejected", () => {
    expect(() => parseBaseline({ ...good, entries: [...good.entries, ...good.entries] })).toThrow(BaselineError);
  });
  it("AC-68.10 an extra key is rejected", () => {
    expect(() => parseBaseline({ ...good, extra: true })).toThrow(BaselineError);
  });
  it("AC-68.10 a non-40-hex commit is rejected", () => {
    expect(() => parseBaseline({ ...good, recorded_commit: "abc" })).toThrow(BaselineError);
  });
  it("AC-68.10 a malformed baseline is never an empty baseline", () => {
    expect(() => parseBaseline({})).toThrow(BaselineError);
    expect(() => parseBaseline(null)).toThrow(BaselineError);
  });
});

describe("AC-68.11 BASELINE_UPDATE_RULE", () => {
  const ok = { mode: "authoritative" as const, platform: "win32", cleanupOk: true, regressions: 0 };

  it("AC-68.11 authoritative win32 run with clean cleanup and no regression may update", () => {
    expect(baselineUpdateDecision(ok).allowed).toBe(true);
  });
  it("AC-68.11 container mode is refused", () => {
    expect(baselineUpdateDecision({ ...ok, mode: "container" }).allowed).toBe(false);
  });
  it("AC-68.11 a regression is refused", () => {
    expect(baselineUpdateDecision({ ...ok, regressions: 1 }).allowed).toBe(false);
  });
  it("AC-68.11 a non-win32 platform is refused", () => {
    expect(baselineUpdateDecision({ ...ok, platform: "linux" }).allowed).toBe(false);
  });
  it("AC-68.11 failed cleanup is refused", () => {
    expect(baselineUpdateDecision({ ...ok, cleanupOk: false }).allowed).toBe(false);
  });

  it("AC-68.11 a refused update leaves the baseline file byte-identical", () => {
    const dir = mkdtempSync(path.join(os.tmpdir(), "s28-baseline-"));
    temps.push(dir);
    const file = path.join(dir, "baseline-snapshot.json");
    writeFileSync(file, JSON.stringify(baseline([{ tool: "t", action: "a", status: "pass" }]), null, 2));
    const before = createHash("sha256").update(readFileSync(file)).digest("hex");
    const written = writeBaselineIfAllowed(file, baseline([{ tool: "t", action: "a", status: "fail" }]), {
      ...ok,
      mode: "container",
    });
    expect(written.allowed).toBe(false);
    expect(createHash("sha256").update(readFileSync(file)).digest("hex")).toBe(before);
  });

  it("AC-68.11 an allowed update writes the new baseline", () => {
    const dir = mkdtempSync(path.join(os.tmpdir(), "s28-baseline-"));
    temps.push(dir);
    const file = path.join(dir, "baseline-snapshot.json");
    const next = baseline([{ tool: "t", action: "a", status: "pass" }]);
    expect(writeBaselineIfAllowed(file, next, ok).allowed).toBe(true);
    expect(existsSync(file)).toBe(true);
    expect(existsSync(file) ? parseBaseline(JSON.parse(readFileSync(file, "utf8"))) : null).toEqual(next);
  });
});
