import { z } from "zod";

export const QUALITY_WIRES = [
  "best",
  "2160p",
  "1440p",
  "1080p",
  "720p",
  "480p",
  "360p",
  "240p",
  "144p",
  "lowest",
] as const;

export const AUDIO_WIRES = [
  "default",
  "best",
  "lowest",
  "low_webm",
  "medium_webm",
  "standard_webm",
  "standard_m4a",
  "standard_mp3",
  "high_m4a",
] as const;

export const COOKIE_MODE_WIRES = ["none", "browser", "file"] as const;

function desc(action: string, method: string, path: string): string {
  return [
    `Workflow: call avkit_download ${action} to ${method} ${path} then poll list/get.`,
    `Prerequisite: backend running and MCP token; cookies via avkit_settings if needed.`,
    `Returns: JSON from ${method} ${path} with file_path pointers, never media bytes.`,
    `Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.`,
  ].join(" ");
}

export const downloadDescriptions: Record<string, string> = {
  "avkit_download.add": desc("add", "POST", "/downloads"),
  "avkit_download.list": desc("list", "GET", "/downloads"),
  "avkit_download.get": desc("get", "GET", "/downloads/{id}"),
  "avkit_download.start": desc("start", "POST", "/downloads/start"),
  "avkit_download.pause": desc("pause", "POST", "/downloads/pause"),
  "avkit_download.resume": desc("resume", "POST", "/downloads/resume"),
  "avkit_download.cancel": desc("cancel", "POST", "/downloads/cancel"),
  "avkit_download.stop": desc("stop", "POST", "/downloads/stop"),
  "avkit_download.reorder": desc("reorder", "PUT", "/downloads/reorder"),
  "avkit_download.reset": desc("reset", "POST", "/downloads/{id}/reset"),
  "avkit_download.remove": desc("remove", "DELETE", "/downloads/{id}"),
  "avkit_download.clear": desc("clear", "DELETE", "/downloads"),
  "avkit_download.sabr_get": desc("sabr_get", "GET", "/downloads/sabr"),
  "avkit_download.sabr_check": desc("sabr_check", "POST", "/downloads/sabr/check"),
  "avkit_download.sabr_force": desc("sabr_force", "POST", "/downloads/sabr/force"),
  "avkit_download.sabr_clear": desc("sabr_clear", "POST", "/downloads/sabr/clear"),
  "avkit_download.cookies_test": desc("cookies_test", "POST", "/downloads/cookies/test"),
  "avkit_download.apply_defaults": desc("apply_defaults", "POST", "/downloads/apply-defaults"),
};

function withDesc<T extends z.ZodTypeAny>(action: string, schema: T): T {
  return schema.describe(downloadDescriptions[`avkit_download.${action}`]) as T;
}

export const downloadSchema = z.discriminatedUnion("action", [
  withDesc(
    "add",
    z
      .object({
        action: z.literal("add"),
        url: z.string().min(1),
        quality: z.enum(QUALITY_WIRES),
        audio_only: z.boolean().optional(),
        audio_format: z.enum(AUDIO_WIRES).optional(),
      })
      .strict(),
  ),
  withDesc("list", z.object({ action: z.literal("list") }).strict()),
  withDesc("get", z.object({ action: z.literal("get"), id: z.string().min(1) }).strict()),
  withDesc("start", z.object({ action: z.literal("start") }).strict()),
  withDesc("pause", z.object({ action: z.literal("pause") }).strict()),
  withDesc("resume", z.object({ action: z.literal("resume") }).strict()),
  withDesc("cancel", z.object({ action: z.literal("cancel") }).strict()),
  withDesc("stop", z.object({ action: z.literal("stop") }).strict()),
  withDesc("reorder", z.object({ action: z.literal("reorder"), job_ids: z.array(z.string().min(1)) }).strict()),
  withDesc("reset", z.object({ action: z.literal("reset"), id: z.string().min(1) }).strict()),
  withDesc("remove", z.object({ action: z.literal("remove"), id: z.string().min(1), confirm: z.literal(true) }).strict()),
  withDesc("clear", z.object({ action: z.literal("clear"), confirm: z.literal(true) }).strict()),
  withDesc("sabr_get", z.object({ action: z.literal("sabr_get") }).strict()),
  withDesc("sabr_check", z.object({ action: z.literal("sabr_check") }).strict()),
  withDesc("sabr_force", z.object({ action: z.literal("sabr_force") }).strict()),
  withDesc("sabr_clear", z.object({ action: z.literal("sabr_clear") }).strict()),
  withDesc(
    "cookies_test",
    z
      .object({
        action: z.literal("cookies_test"),
        mode: z.enum(COOKIE_MODE_WIRES),
        browser: z.string().optional(),
        profile: z.string().optional(),
        cookie_file: z.string().optional(),
      })
      .strict(),
  ),
  withDesc("apply_defaults", z.object({ action: z.literal("apply_defaults") }).strict()),
]);
