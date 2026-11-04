import { mkdtempSync, readdirSync, readFileSync, rmSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { redact, redactDeep } from "../../scripts/audit/redact.js";
import { buildSummary, writeOutputs } from "../../scripts/audit/report.js";
import type { StepRecord } from "../../scripts/audit/types.js";

const GUI = "gui-secret-token-1234567890";
const MCP = "mcp-secret-token-0987654321";

const temps: string[] = [];
afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("AC-68.14 secret redaction", () => {
  it("AC-68.14 redact removes every occurrence of each secret", () => {
    expect(redact(`a ${GUI} b ${MCP} c ${GUI}`, [GUI, MCP])).toBe("a [redacted] b [redacted] c [redacted]");
  });

  it("AC-68.14 redactDeep walks nested objects and arrays", () => {
    const out = redactDeep({ args: { token: MCP }, list: [`Bearer ${GUI}`] }, [GUI, MCP]);
    expect(JSON.stringify(out)).not.toContain(GUI);
    expect(JSON.stringify(out)).not.toContain(MCP);
  });

  it("AC-68.14 empty secrets never blank the text", () => {
    expect(redact("unchanged", ["", "  "])).toBe("unchanged");
  });

  it("AC-68.14 no output file contains a token after writeOutputs", () => {
    const dir = mkdtempSync(path.join(os.tmpdir(), "s28-redact-"));
    temps.push(dir);
    const step: StepRecord = {
      id: "download.add",
      tool: "avkit_download",
      action: "add",
      phase: "lifecycle",
      verdict: "fail",
      reason: "unexpected_error",
      is_error: true,
      observable: `GET with ${GUI}`,
      error: `token_missing ${MCP}`,
      blocked_by: null,
      env_bound: null,
      ms: 3,
    };
    const summary = buildSummary({
      mode: "container",
      agent: "test",
      commit: "0".repeat(40),
      server: "dist/index.js",
      backendVersion: "0.1.0",
      launch: { command: "node", args: ["dist/index.js"], env_keys: ["AVKIT_API_TOKEN"], initialized: true },
      isolation: { root: dir, paths: {}, ok: true, error: null },
      discovery: { status: "pass", tools: 8, actions: 67, findings: [], new: [], removed: [], ghost: [] },
      steps: [step],
      deltas: [],
      cleanup: { ok: true, residuals: [], backend_exited: true, root_removed: true },
      exitCode: 1,
    });
    writeOutputs({
      dir,
      summary,
      records: [{ ...step, args: { token: MCP } }],
      secrets: [GUI, MCP],
      serverStderr: `stderr mentions ${MCP} and ${GUI}`,
      reportPath: path.join(dir, "report.md"),
    });
    const files = readdirSync(dir);
    expect(files.sort()).toEqual(["actions.jsonl", "mcp-audit-summary.json", "report.md", "server-stderr.txt"]);
    for (const name of files) {
      const text = readFileSync(path.join(dir, name), "utf8");
      expect(text, name).not.toContain(GUI);
      expect(text, name).not.toContain(MCP);
    }
  });
});
