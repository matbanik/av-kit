import { z } from "zod";

export const DEVICE_WIRES = ["auto", "cuda", "cpu", "mps"] as const;
// Wire values of the backend TtsAsset enum (MEU-62 TTS_ASSETS).
export const TTS_ASSET_WIRES = ["tts_onnx_vocab", "tts_spacy_model", "tts_voice_packs"] as const;

function desc(action: string, method: string, path: string): string {
  return [
    `Workflow: available → download → load, then TTS; action ${action} is ${method} ${path}.`,
    `Prerequisite: disk space; variant_id min 1 on download/load; MCP token required.`,
    `Returns: JSON from ${method} ${path} (variant metadata, never model bytes).`,
    `Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.`,
  ].join(" ");
}

export const modelsDescriptions: Record<string, string> = {
  "avkit_models.available": desc("available", "GET", "/models/available"),
  "avkit_models.downloaded": desc("downloaded", "GET", "/models/downloaded"),
  "avkit_models.download": desc("download", "POST", "/models/download"),
  "avkit_models.download_runtime": desc("download_runtime", "GET", "/models/download-runtime"),
  "avkit_models.load": desc("load", "POST", "/models/load"),
  "avkit_models.unload": desc("unload", "POST", "/models/unload"),
  "avkit_models.status": desc("status", "GET", "/models/status"),
  "avkit_models.download_asset": [
    "Workflow: dependencies → download_asset → download_runtime, before TTS generate;",
    "action download_asset is POST /models/download with body {asset}.",
    `Prerequisite: asset is one of ${TTS_ASSET_WIRES.join(", ")}; MCP token required.`,
    "Returns: JSON from POST /models/download ({variant: null, asset}); 409 when a download runs or the asset is ready.",
    "Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.",
  ].join(" "),
};

function withDesc<T extends z.ZodTypeAny>(action: string, schema: T): T {
  return schema.describe(modelsDescriptions[`avkit_models.${action}`]) as T;
}

export const modelsSchema = z.discriminatedUnion("action", [
  withDesc("available", z.object({ action: z.literal("available") }).strict()),
  withDesc("downloaded", z.object({ action: z.literal("downloaded") }).strict()),
  withDesc("download", z.object({ action: z.literal("download"), variant_id: z.string().min(1) }).strict()),
  withDesc("download_runtime", z.object({ action: z.literal("download_runtime") }).strict()),
  withDesc(
    "load",
    z
      .object({
        action: z.literal("load"),
        variant_id: z.string().min(1),
        device: z.enum(DEVICE_WIRES).optional(),
      })
      .strict(),
  ),
  withDesc("unload", z.object({ action: z.literal("unload") }).strict()),
  withDesc("status", z.object({ action: z.literal("status") }).strict()),
  withDesc(
    "download_asset",
    z.object({ action: z.literal("download_asset"), asset: z.enum(TTS_ASSET_WIRES) }).strict(),
  ),
]);
