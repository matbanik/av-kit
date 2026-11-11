import { z } from "zod";

const PRESET_WIRES = ["archival", "high_quality", "balanced", "sharing", "mobile"] as const;
const COPY_WIRES = ["fast_copy", "reencode"] as const;
const AUDIO_ENCODE_WIRES = ["copy", "aac_96", "aac_128", "aac_192"] as const;
const GPU_PREF_WIRES = ["auto", "nvidia", "amd", "intel", "software"] as const;
const STREAM_MODES = ["first", "all"] as const;
/** PROBE_MCP (MEU-133): what `probe` reads, and that it changes nothing. */
const PROBE_TEXT =
  "Reads a local video's duration, size, codecs and streams without changing it or writing a job. " +
  "duration_ms and timecode are null for a raw stream with no duration. " +
  "Use it before avkit_capture frames to pick times.";

function desc(action: string, method: string, path: string): string {
  return [
    `Workflow: call avkit_convert ${action} to ${method} ${path} then poll list/get.`,
    `Prerequisite: local absolute file paths; Convert never uploads YouTube.`,
    `Returns: JSON from ${method} ${path} with path pointers, never media bytes.`,
    `Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.`,
  ].join(" ");
}

export const convertDescriptions: Record<string, string> = {
  "avkit_convert.add": desc("add", "POST", "/conversions"),
  "avkit_convert.list": desc("list", "GET", "/conversions"),
  "avkit_convert.get": desc("get", "GET", "/conversions/{id}"),
  "avkit_convert.start": desc("start", "POST", "/conversions/start"),
  "avkit_convert.pause": desc("pause", "POST", "/conversions/pause"),
  "avkit_convert.resume": desc("resume", "POST", "/conversions/resume"),
  "avkit_convert.cancel": desc("cancel", "POST", "/conversions/cancel"),
  "avkit_convert.reorder": desc("reorder", "PUT", "/conversions/reorder"),
  "avkit_convert.reset": desc("reset", "POST", "/conversions/{id}/reset"),
  "avkit_convert.remove": desc("remove", "DELETE", "/conversions/{id}"),
  "avkit_convert.clear": desc("clear", "DELETE", "/conversions"),
  "avkit_convert.gpu": desc("gpu", "GET", "/conversions/gpu"),
  "avkit_convert.gpu_refresh": desc("gpu_refresh", "POST", "/conversions/gpu/refresh"),
  "avkit_convert.probe": `${desc("probe", "POST", "/conversions/probe")} ${PROBE_TEXT}`,
};

function withDesc<T extends z.ZodTypeAny>(action: string, schema: T): T {
  return schema.describe(convertDescriptions[`avkit_convert.${action}`]) as T;
}

const compressAdd = withDesc(
  "add",
  z
    .object({
      action: z.literal("add"),
      kind: z.literal("compress"),
      paths: z.array(z.string().min(1)).min(1),
      preset: z.enum(PRESET_WIRES).optional(),
      cq: z.number().int().nonnegative().optional(),
      scale_height: z.number().int().nonnegative().optional(),
      audio_mode: z.enum(AUDIO_ENCODE_WIRES).optional(),
      gpu_preference: z.enum(GPU_PREF_WIRES).optional(),
    })
    .strict(),
);

const cutAdd = withDesc(
  "add",
  z
    .object({
      action: z.literal("add"),
      kind: z.literal("cut"),
      paths: z.array(z.string().min(1)).min(1),
      in_ms: z.number().int().nonnegative(),
      out_ms: z.number().int().nonnegative(),
      copy_mode: z.enum(COPY_WIRES).optional(),
    })
    .strict(),
);

const extractAdd = withDesc(
  "add",
  z
    .object({
      action: z.literal("add"),
      kind: z.literal("extract"),
      paths: z.array(z.string().min(1)).min(1),
      stream_mode: z.enum(STREAM_MODES),
      stream_index: z.number().int().nonnegative().optional(),
    })
    .strict(),
);

export const convertSchema = z.union([
  compressAdd,
  cutAdd,
  extractAdd,
  withDesc("list", z.object({ action: z.literal("list") }).strict()),
  withDesc("get", z.object({ action: z.literal("get"), id: z.string().min(1) }).strict()),
  withDesc("start", z.object({ action: z.literal("start") }).strict()),
  withDesc("pause", z.object({ action: z.literal("pause") }).strict()),
  withDesc("resume", z.object({ action: z.literal("resume") }).strict()),
  withDesc("cancel", z.object({ action: z.literal("cancel") }).strict()),
  withDesc(
    "reorder",
    z.object({ action: z.literal("reorder"), job_ids: z.array(z.string().min(1)).min(1) }).strict(),
  ),
  withDesc("reset", z.object({ action: z.literal("reset"), id: z.string().min(1) }).strict()),
  withDesc(
    "remove",
    z.object({ action: z.literal("remove"), id: z.string().min(1), confirm: z.literal(true) }).strict(),
  ),
  withDesc("clear", z.object({ action: z.literal("clear"), confirm: z.literal(true) }).strict()),
  withDesc("gpu", z.object({ action: z.literal("gpu") }).strict()),
  withDesc("gpu_refresh", z.object({ action: z.literal("gpu_refresh") }).strict()),
  // PROBE_MCP (MEU-133): read-only; the path goes in the POST body, with the default timeout.
  withDesc(
    "probe",
    z.object({ action: z.literal("probe"), path: z.string().min(1).max(4096) }).strict(),
  ),
]);
