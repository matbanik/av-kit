import { afterEach, describe, expect, it, vi } from "vitest";
import { TTS_ASSET_WIRES } from "../src/toolsets/models.js";
import { ACTION_DESCRIPTIONS, ACTION_INDEX, handleTool } from "../src/toolsets/registry.js";
import { cleanupDirs, okJson, tempAppData, toolEnv } from "./fixtures.js";

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

describe("MEU-62 AC-62.13 avkit_models.download_asset", () => {
  it("AC-62.13 is registered once on POST /models/download, appended after the capture rows", () => {
    const rows = ACTION_INDEX.filter((row) => row.tool === "avkit_models" && row.action === "download_asset");
    expect(rows).toEqual([
      { tool: "avkit_models", action: "download_asset", method: "POST", path: "/models/download" },
    ]);
    expect(ACTION_INDEX[ACTION_INDEX.length - 1]).toEqual(rows[0]);
    expect(ACTION_DESCRIPTIONS["avkit_models.download_asset"]).toContain("download_asset");
  });

  it.each(["tts_onnx_vocab", "tts_spacy_model", "tts_voice_packs"])(
    "AC-62.13 posts {asset: %s} to /models/download",
    async (asset) => {
      const fetchImpl = vi.fn(async () => okJson({ variant: null, asset }, 202));
      const result = await call({ action: "download_asset", asset }, fetchImpl);
      expect(result.isError).not.toBe(true);
      expect(fetchImpl).toHaveBeenCalledTimes(1);
      const [url, init] = fetchImpl.mock.calls[0] as unknown as [string, RequestInit];
      expect(String(url)).toMatch(/\/models\/download$/);
      expect(init.method).toBe("POST");
      expect(JSON.parse(String(init.body))).toEqual({ asset });
    },
  );

  it.each([
    { action: "download_asset", asset: "x" },
    { action: "download_asset", asset: "tts_spacy_model", extra: 1 },
    { action: "download_asset" },
    { action: "download_asset", asset: "tts_spacy_model", variant_id: "kokoro-onnx-int8" },
  ])("AC-62.13 rejects %j before fetch", async (args) => {
    const fetchImpl = vi.fn();
    const result = await call(args, fetchImpl);
    expect(result.isError).toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(0);
  });
});

describe("MEU-73 AC-73.13 voice packs on avkit_models.download_asset", () => {
  it("AC-73.13 TTS_ASSET_WIRES lists the three wires in backend declaration order", () => {
    expect([...TTS_ASSET_WIRES]).toEqual(["tts_onnx_vocab", "tts_spacy_model", "tts_voice_packs"]);
    expect(ACTION_DESCRIPTIONS["avkit_models.download_asset"]).toContain("tts_voice_packs");
  });

  it("AC-73.13 posts {asset: tts_voice_packs} and still rejects an unknown wire", async () => {
    const fetchImpl = vi.fn(async () => okJson({ variant: null, asset: "tts_voice_packs" }, 202));
    const result = await call({ action: "download_asset", asset: "tts_voice_packs" }, fetchImpl);
    expect(result.isError).not.toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
    const [, init] = fetchImpl.mock.calls[0] as unknown as [string, RequestInit];
    expect(JSON.parse(String(init.body))).toEqual({ asset: "tts_voice_packs" });
    const rejected = vi.fn();
    const bad = await call({ action: "download_asset", asset: "tts_voice_pack" }, rejected);
    expect(bad.isError).toBe(true);
    expect(rejected).toHaveBeenCalledTimes(0);
  });
});
