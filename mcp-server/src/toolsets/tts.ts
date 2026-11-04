import { z } from "zod";

export const OUTPUT_FORMAT_WIRES = ["MP3", "WAV"] as const;

function desc(action: string, method: string, path: string): string {
  return [
    `Workflow: load a model, then avkit_tts ${action} (${method} ${path}); generate returns the job at once (status Generating); poll get until Done/Failed/Cancelled; cancel stops a running job.`,
    `Prerequisite: avkit_models.status.is_loaded or generate is 409; MCP token required.`,
    `Returns: JSON from ${method} ${path} with text_preview/text_hash, never full TTS text.`,
    `Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.`,
  ].join(" ");
}

export const ttsDescriptions: Record<string, string> = {
  "avkit_tts.prepare": desc("prepare", "POST", "/tts/prepare"),
  "avkit_tts.generate": desc("generate", "POST", "/tts/generate"),
  "avkit_tts.get": desc("get", "GET", "/tts/{id}"),
  "avkit_tts.cancel": desc("cancel", "DELETE", "/tts/{id}"),
  "avkit_tts.voices": desc("voices", "GET", "/tts/voices"),
};

function withDesc<T extends z.ZodTypeAny>(action: string, schema: T): T {
  return schema.describe(ttsDescriptions[`avkit_tts.${action}`]) as T;
}

export const ttsSchema = z.discriminatedUnion("action", [
  withDesc(
    "prepare",
    z
      .object({
        action: z.literal("prepare"),
        text: z.string(),
        enabled_steps: z.array(z.string()),
        chunk_max_chars: z.number().optional(),
      })
      .strict(),
  ),
  withDesc(
    "generate",
    z
      .object({
        action: z.literal("generate"),
        text: z.string().min(1),
        voice: z.string().min(1),
        speed: z.number().min(0.5).max(2),
        format: z.enum(OUTPUT_FORMAT_WIRES),
        enabled_steps: z.array(z.string()),
        source_kind: z.enum(["inline", "file"]).optional(),
        source_path: z.string().optional(),
      })
      .strict(),
  ),
  withDesc("get", z.object({ action: z.literal("get"), id: z.string().min(1) }).strict()),
  withDesc("cancel", z.object({ action: z.literal("cancel"), id: z.string().min(1), confirm: z.literal(true) }).strict()),
  withDesc("voices", z.object({ action: z.literal("voices") }).strict()),
]);
