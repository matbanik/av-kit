import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const examplePath = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../docs/distribution/mcp.json.example");

type Example = { mcpServers?: { avkit?: { command?: unknown; args?: unknown; env?: Record<string, unknown> } } };

describe("MEU-71 EXAMPLE_CONFIG (AC-71.11)", () => {
  it("AC-71.11 mcp.json.example parses with mcpServers.avkit, ELECTRON_RUN_AS_NODE \"1\" and an AVKIT_APP_DATA key", () => {
    const parsed = JSON.parse(readFileSync(examplePath, "utf8")) as Example;
    const avkit = parsed.mcpServers?.avkit;
    expect(avkit, "mcpServers.avkit").toBeDefined();
    expect(avkit?.command).toBe("<path to av-kit.exe>");
    expect(avkit?.args).toEqual(["<av-kit resources>\\mcp-server\\index.mjs"]);
    expect(avkit?.env?.ELECTRON_RUN_AS_NODE).toBe("1");
    expect(Object.keys(avkit?.env ?? {})).toContain("AVKIT_APP_DATA");
    expect(avkit?.env?.AVKIT_APP_DATA).toBe("<app data folder>");
  });

  it("AC-71.11 negative: no AVKIT_API_TOKEN, ${ placeholder or node command", () => {
    const text = readFileSync(examplePath, "utf8");
    expect(text).not.toContain("AVKIT_API_TOKEN");
    expect(text).not.toContain("${");
    expect(text).not.toMatch(/"command"\s*:\s*"node"/);
  });
});
