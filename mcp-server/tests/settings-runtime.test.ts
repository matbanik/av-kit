import { describe, expect, it } from "vitest";
import { SETTINGS_SCHEMA, settingsSchema } from "../src/toolsets/settings.js";

/**
 * MEU-141 (Session 66) DENO_SETTING, AC-141.1's MCP half: `downloader.deno_path` is a string leaf
 * defaulting to "", last in the downloader namespace, and `avkit_settings set` accepts it.
 */

const PICKED = "C:/deno/deno.exe";

describe("AC-141.1 DENO_SETTING in the MCP settings schema", () => {
  it("AC-141.1 downloader.deno_path is a string leaf defaulting to empty, last in the namespace", () => {
    const downloader = SETTINGS_SCHEMA.namespaces.downloader ?? {};
    expect(Object.keys(downloader)).toContain("deno_path");
    expect(downloader.deno_path).toEqual({ type: "string", default: "" });
    expect(Object.keys(downloader).at(-1)).toBe("deno_path");
  });

  it("AC-141.1 avkit_settings set takes deno_path in the downloader namespace", () => {
    const parsed = settingsSchema.safeParse({ action: "set", namespace: "downloader", deno_path: PICKED });
    expect(parsed.success).toBe(true);
  });

  it("AC-141.1 [neg] an unknown downloader leaf is still refused", () => {
    const parsed = settingsSchema.safeParse({ action: "set", namespace: "downloader", deno_path_extra: PICKED });
    expect(parsed.success).toBe(false);
  });
});
