import { afterEach, describe, expect, it, vi } from "vitest";
import { handleTool } from "../src/toolsets/registry.js";
import { SETTINGS_SCHEMA, settingsSchema } from "../src/toolsets/settings.js";
import { cleanupDirs, okJson, tempAppData, toolEnv } from "./fixtures.js";

/**
 * Session 106 (MEU-174) UPDATE_INTERVAL_LEAF, AC-174.11's MCP half: `app.update_interval` is a
 * string leaf with the default `weekly` and the three wires, and `avkit_settings set` takes it.
 */

const WIRES = ["weekly", "monthly", "never"];
const temps: string[] = [];

afterEach(() => {
  cleanupDirs(temps);
});

describe("AC-174.11 UPDATE_INTERVAL_LEAF in the MCP settings tool", () => {
  it("AC-174.11 the schema resource lists app.update_interval with the default weekly and three wires", () => {
    const app = SETTINGS_SCHEMA.namespaces.app ?? {};
    expect(app.update_interval).toEqual({ type: "string", default: "weekly", enum: WIRES });
  });

  it("AC-174.11 avkit_settings set parses weekly, monthly and never in the app namespace", () => {
    for (const wire of WIRES) {
      const parsed = settingsSchema.safeParse({ action: "set", namespace: "app", update_interval: wire });
      expect(parsed.success, wire).toBe(true);
    }
  });

  it("AC-174.11 [neg] weekly parses, and daily is refused by the tool's schema before any request", async () => {
    expect(settingsSchema.safeParse({ action: "set", namespace: "app", update_interval: "weekly" }).success).toBe(true);
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn(async () => okJson({}));
    const result = await handleTool(
      "avkit_settings",
      { action: "set", namespace: "app", update_interval: "daily" },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(result.isError).toBe(true);
    expect(result.content[0].text).toContain("validation_error");
    expect(fetchImpl).toHaveBeenCalledTimes(0);
  });
});
