import { describe, expect, it } from "vitest";
import type { z } from "zod";
import { createServer, SERVER_INSTRUCTIONS } from "../src/index.js";
import { ACTION_DESCRIPTIONS, ACTION_INDEX } from "../src/toolsets/registry.js";
import { SETTINGS_SCHEMA, SETTINGS_SCHEMA_URI } from "../src/toolsets/settings.js";
import { M7_MARKERS } from "./fixtures.js";

type RegisteredTool = {
  description?: string;
  inputSchema?: { options?: z.ZodTypeAny[] };
  _meta?: { action_descriptions?: Record<string, string> };
};

function registeredTools(server: ReturnType<typeof createServer>): Record<string, RegisteredTool> {
  return (server as unknown as { _registeredTools: Record<string, RegisteredTool> })._registeredTools ?? {};
}

function optionAction(option: z.ZodTypeAny): string | undefined {
  const shape = (option as z.ZodObject<z.ZodRawShape>).shape;
  const literal = shape?.action as { value?: string } | undefined;
  return literal?.value;
}

function registeredActionDescriptions(server: ReturnType<typeof createServer>): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [toolName, tool] of Object.entries(registeredTools(server))) {
    for (const option of tool.inputSchema?.options ?? []) {
      const action = optionAction(option);
      if (!action || !option.description) {
        continue;
      }
      out[`${toolName}.${action}`] = option.description;
    }
  }
  return out;
}

function registeredResourceUris(server: ReturnType<typeof createServer>): string[] {
  const internal = server as unknown as {
    _registeredResources: Record<string, { uri?: string }>;
  };
  const rec = internal._registeredResources ?? {};
  return [...new Set([...Object.keys(rec), ...Object.values(rec).map((r) => r.uri ?? "")])].filter(Boolean);
}

describe("M7_PER_ACTION", () => {
  it("ACTION_DESCRIPTIONS has exactly 71 keys each with ≥3 distinct M7 markers", () => {
    const keys = Object.keys(ACTION_DESCRIPTIONS).sort();
    const expected = ACTION_INDEX.map((r) => `${r.tool}.${r.action}`).sort();
    expect(keys).toEqual(expected);
    // TA-9 (Session 27, MEU-62): +1 avkit_models.download_asset.
    // TA-1 (Session 30, MEU-67): +avkit_capture.flatten, +avkit_capture.revert.
    // MEU-130 (Session 59): +avkit_capture.crop after revert.
    expect(keys).toHaveLength(71);
    for (const key of keys) {
      const text = ACTION_DESCRIPTIONS[key];
      expect(typeof text).toBe("string");
      const hits = M7_MARKERS.filter((m) => text.toLowerCase().includes(m.toLowerCase()));
      expect(hits.length, key).toBeGreaterThanOrEqual(3);
    }
    expect(SERVER_INSTRUCTIONS).toContain("Never upload or write to YouTube");
    expect(ACTION_DESCRIPTIONS["avkit_settings.get"]).toContain(SETTINGS_SCHEMA_URI);
    expect(ACTION_DESCRIPTIONS["avkit_settings.set"]).toContain(SETTINGS_SCHEMA_URI);
  });

  it("registers the 71 ACTION_DESCRIPTIONS on Zod action options and listTools _meta", () => {
    const server = createServer();
    const fromSchema = registeredActionDescriptions(server);
    const expected = ACTION_INDEX.map((row) => `${row.tool}.${row.action}`).sort();
    expect(Object.keys(fromSchema).sort()).toEqual(expected);
    // TA-1 (Session 30, MEU-67); MEU-130 (Session 59): +avkit_capture.crop.
    expect(Object.keys(fromSchema)).toHaveLength(71);
    const tools = registeredTools(server);
    for (const row of ACTION_INDEX) {
      const key = `${row.tool}.${row.action}`;
      expect(fromSchema[key]).toBe(ACTION_DESCRIPTIONS[key]);
      const hits = M7_MARKERS.filter((marker) => fromSchema[key].toLowerCase().includes(marker.toLowerCase()));
      expect(hits.length, key).toBeGreaterThanOrEqual(3);
      expect(tools[row.tool]?._meta?.action_descriptions?.[row.action]).toBe(ACTION_DESCRIPTIONS[key]);
    }
  });
});

describe("SETTINGS_SCHEMA_URI", () => {
  it("resource is registered and omits rail/panel geometry keys", () => {
    expect(SETTINGS_SCHEMA_URI).toBe("avkit://settings/schema");
    const uris = registeredResourceUris(createServer());
    expect(uris).toContain(SETTINGS_SCHEMA_URI);
    const dumped = JSON.stringify(SETTINGS_SCHEMA);
    expect(dumped).not.toMatch(/rail/);
    expect(dumped).not.toMatch(/panel/);
    expect(dumped).toContain("theme");
    expect(dumped).toContain("downloader");
    expect(dumped).toContain("transcript");
    expect(dumped).toContain("tts");
    expect(dumped).toContain("app");
    expect(dumped).toContain("ui");
    expect(dumped).toContain("converter");
    expect(SETTINGS_SCHEMA).toHaveProperty("namespaces");
  });
});
