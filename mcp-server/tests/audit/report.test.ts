import { describe, expect, it } from "vitest";
import { buildSummary, renderReport, validateSummary } from "../../scripts/audit/report.js";
import type { StepRecord } from "../../scripts/audit/types.js";

function step(tool: string, action: string, verdict: StepRecord["verdict"], extra: Partial<StepRecord> = {}): StepRecord {
  return {
    id: `${tool}.${action}`,
    tool,
    action,
    phase: "lifecycle",
    verdict,
    reason: verdict === "pass" ? null : "hollow",
    is_error: false,
    observable: verdict === "pass" ? "REST row present" : null,
    error: verdict === "pass" ? null : "GET 404",
    blocked_by: null,
    env_bound: null,
    ms: 5,
    ...extra,
  };
}

function summaryFor(mode: "container" | "authoritative") {
  return buildSummary({
    mode,
    agent: "claude-code-cloud",
    commit: "0123456789abcdef0123456789abcdef01234567",
    server: "/repo/mcp-server/dist/index.js",
    backendVersion: "0.1.0",
    launch: { command: "node", args: ["/repo/mcp-server/dist/index.js"], env_keys: ["AVKIT_API_TOKEN", "AVKIT_APP_DATA", "PATH"], initialized: true },
    isolation: { root: "/tmp/r", paths: { "downloader.path": "/tmp/r/out/downloads" }, ok: true, error: null },
    discovery: {
      status: "fail",
      tools: 8,
      actions: 67,
      findings: [{ code: "schema_not_advertised", tool: "avkit_download", detail: "inputSchema has no action property" }],
      new: [],
      removed: [],
      ghost: [],
    },
    steps: [
      step("avkit_health", "liveness", "pass", { phase: "functional" }),
      step("avkit_download", "add", "fail"),
      step("avkit_download", "get", "blocked", { blocked_by: "avkit_download.add", reason: null, error: null }),
    ],
    deltas: [{ key: "avkit_download.add", delta: "NEW" }],
    cleanup: { ok: true, residuals: [], backend_exited: true, root_removed: true },
    exitCode: 1,
  });
}

describe("AC-68.13 summary schema", () => {
  it("AC-68.13 a built summary validates against summary.schema.json", () => {
    expect(validateSummary(summaryFor("authoritative"))).toEqual([]);
  });

  it("AC-68.13 a summary missing mode fails validation", () => {
    const bad = { ...summaryFor("container") } as Record<string, unknown>;
    delete bad.mode;
    expect(validateSummary(bad).join("\n")).toMatch(/mode/);
  });

  it("AC-68.13 a step tool outside the 8 compound tools fails validation", () => {
    const bad = summaryFor("container");
    bad.steps[0] = { ...bad.steps[0], tool: "avkit_unknown" };
    expect(validateSummary(bad).join("\n")).toMatch(/tool/);
  });

  it("AC-68.13 counts are derived from the steps", () => {
    const s = summaryFor("container");
    expect(s.counts).toEqual({ pass: 1, fail: 1, skip_env: 0, blocked: 1, total: 3 });
  });
});

describe("AC-68.13 report rendering", () => {
  it("AC-68.13 the report carries the header, scorecard, matrix, functional table, issues and delta", () => {
    const md = renderReport(summaryFor("authoritative"));
    for (const needle of [
      "# MCP Tool Audit Report",
      "| Date |",
      "| Agent | claude-code-cloud |",
      "| Mode | authoritative |",
      "| Backend version | 0.1.0 |",
      "| Commit | 0123456789abcdef0123456789abcdef01234567 |",
      "| Server | /repo/mcp-server/dist/index.js |",
      "| Tools / actions | 8 / 67 |",
      "## Scorecard",
      "## Lifecycle matrix",
      "## Functional results",
      "## Issues log",
      "## Discovery findings",
      "## Regression delta",
      "## Cleanup",
      "schema_not_advertised",
    ]) {
      expect(md).toContain(needle);
    }
    expect(md).not.toContain("non-authoritative container subset");
  });

  it("AC-68.13 a container report states it is a non-authoritative subset", () => {
    expect(renderReport(summaryFor("container"))).toContain("non-authoritative container subset");
  });

  it("AC-68.13 the consolidation score is reported as not applicable (D-10)", () => {
    expect(renderReport(summaryFor("authoritative"))).toMatch(/Consolidation score: n\/a/);
  });
});
