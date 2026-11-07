import { afterEach, describe, expect, it, vi } from "vitest";
import { ACTION_DESCRIPTIONS, handleTool } from "../src/toolsets/registry.js";
import { M7_MARKERS, cleanupDirs, okJson, tempAppData, toolEnv } from "./fixtures.js";

// MODEL_REASONS[PyTorch] (packages/core/src/avkit_core/domain/tts.py, D-310).
const REASON = "This build can't run PyTorch models. Choose an ONNX model.";

const temps: string[] = [];

afterEach(() => {
  cleanupDirs(temps);
});

async function call(args: Record<string, unknown>, fetchImpl: ReturnType<typeof vi.fn>) {
  const appData = tempAppData();
  temps.push(appData);
  return handleTool("avkit_models", args, {
    env: toolEnv(appData),
    fetchImpl: fetchImpl as unknown as typeof fetch,
  });
}

describe("MEU-117 AC-117.10 avkit_models descriptions name build capability", () => {
  it("AC-117.10 available names devices, available and reason, with the four markers", () => {
    const text = ACTION_DESCRIPTIONS["avkit_models.available"];
    expect(text).toContain("devices, available and reason");
    for (const marker of M7_MARKERS) expect(text).toContain(marker);
  });

  it("AC-117.10 download names the 409 for a variant this build can't run, with the four markers", () => {
    const text = ACTION_DESCRIPTIONS["avkit_models.download"];
    expect(text).toMatch(/409[^.]*a variant this build can't run/);
    for (const marker of M7_MARKERS) expect(text).toContain(marker);
  });
});

describe("MEU-117 AC-117.11 avkit_models passes build capability through", () => {
  it("AC-117.11 returns an unavailable row from available unchanged", async () => {
    const item = {
      id: "kokoro-pt-fp32",
      name: "PyTorch FP32",
      format: "PyTorch",
      precision: "FP32",
      size_bytes: 16,
      path: null,
      is_downloaded: false,
      devices: ["auto", "cpu"],
      available: false,
      reason: REASON,
    };
    const fetchImpl = vi.fn(async () => okJson({ items: [item] }));
    const result = await call({ action: "available" }, fetchImpl);
    expect(result.isError).not.toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(JSON.parse(result.content[0].text)).toEqual({ items: [item] });
  });

  it("AC-117.11 turns the download 409 into TOOL_ERROR with the reason after one fetch", async () => {
    const fetchImpl = vi.fn(
      async () =>
        new Response(JSON.stringify({ error: { code: "ConflictError", message: REASON, details: null } }), {
          status: 409,
        }),
    );
    const result = await call({ action: "download", variant_id: "kokoro-pt-fp32" }, fetchImpl);
    expect(result.isError).toBe(true);
    expect(result.content[0].text).toBe(`ConflictError: ${REASON}`);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });
});
