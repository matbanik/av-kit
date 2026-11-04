import { afterEach, describe, expect, it, vi } from "vitest";
import { handleTool } from "../src/toolsets/registry.js";
import {
  cleanupDirs,
  CONVERT_ACTION_INDEX,
  CAPTURE_ACTION_INDEX,
  DESTRUCTIVE_KEYS,
  EXPECTED_ACTION_INDEX,
  minimalInput,
  NON_DESTRUCTIVE_STOPS,
  okJson,
  tempAppData,
  toolEnv,
} from "./fixtures.js";

const temps: string[] = [];

afterEach(() => {
  cleanupDirs(temps);
});

describe("ZOD_STRICT_CENSUS", () => {
  it.each([...EXPECTED_ACTION_INDEX, ...CONVERT_ACTION_INDEX, ...CAPTURE_ACTION_INDEX])(
    "$tool.$action rejects extra_unknown before fetch",
    async (row) => {
      const appData = tempAppData();
      temps.push(appData);
      const fetchImpl = vi.fn();
      const args = { ...minimalInput(row.tool, row.action), extra_unknown: true };
      const result = await handleTool(row.tool, args, {
        env: toolEnv(appData),
        fetchImpl: fetchImpl as unknown as typeof fetch,
      });
      expect(result.isError).toBe(true);
      expect(result.content[0].text).toBeTruthy();
      expect(fetchImpl).toHaveBeenCalledTimes(0);
    },
  );
});

describe("DESTRUCTIVE_ACTIONS confirm", () => {
  it.each([...DESTRUCTIVE_KEYS])("%s without confirm does not fetch", async (key) => {
    const [tool, action] = key.split(".") as [string, string];
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn();
    const args = minimalInput(tool, action);
    delete args.confirm;
    const result = await handleTool(tool, args, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(0);
  });

  it.each([...DESTRUCTIVE_KEYS])("%s with confirm:false does not fetch", async (key) => {
    const [tool, action] = key.split(".") as [string, string];
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn();
    const args = { ...minimalInput(tool, action), confirm: false };
    const result = await handleTool(tool, args, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(0);
  });

  it.each([...NON_DESTRUCTIVE_STOPS])("%s succeeds without confirm", async (key) => {
    const [tool, action] = key.split(".") as [string, string];
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn(async () => okJson({ ok: true }, 202));
    const result = await handleTool(tool, { action }, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });
});

describe("VARIANT_ID_MIN", () => {
  it.each(["download", "load"] as const)(
    "avkit_models.%s empty variant_id is TOOL_ERROR with fetch 0",
    async (action) => {
      const appData = tempAppData();
      temps.push(appData);
      const fetchImpl = vi.fn();
      const result = await handleTool(
        "avkit_models",
        action === "load" ? { action, variant_id: "" } : { action, variant_id: "" },
        {
          env: toolEnv(appData),
          fetchImpl: fetchImpl as unknown as typeof fetch,
        },
      );
      expect(result.isError).toBe(true);
      expect(result.content[0].text).not.toContain("404");
      expect(fetchImpl).toHaveBeenCalledTimes(0);
    },
  );
});
