import { mkdtempSync, rmSync } from "node:fs";
import os from "node:os";
import path from "node:path";

export const API_BASE = "http://127.0.0.1:8000/api/v1";

export type ActionRow = {
  tool: string;
  action: string;
  method: string;
  path: string;
};

export const EXPECTED_ACTION_INDEX: ActionRow[] = [
  { tool: "avkit_download", action: "add", method: "POST", path: "/downloads" },
  { tool: "avkit_download", action: "list", method: "GET", path: "/downloads" },
  { tool: "avkit_download", action: "get", method: "GET", path: "/downloads/{id}" },
  { tool: "avkit_download", action: "start", method: "POST", path: "/downloads/start" },
  { tool: "avkit_download", action: "pause", method: "POST", path: "/downloads/pause" },
  { tool: "avkit_download", action: "resume", method: "POST", path: "/downloads/resume" },
  { tool: "avkit_download", action: "cancel", method: "POST", path: "/downloads/cancel" },
  { tool: "avkit_download", action: "stop", method: "POST", path: "/downloads/stop" },
  { tool: "avkit_download", action: "reorder", method: "PUT", path: "/downloads/reorder" },
  { tool: "avkit_download", action: "reset", method: "POST", path: "/downloads/{id}/reset" },
  { tool: "avkit_download", action: "remove", method: "DELETE", path: "/downloads/{id}" },
  { tool: "avkit_download", action: "clear", method: "DELETE", path: "/downloads" },
  { tool: "avkit_download", action: "sabr_get", method: "GET", path: "/downloads/sabr" },
  { tool: "avkit_download", action: "sabr_check", method: "POST", path: "/downloads/sabr/check" },
  { tool: "avkit_download", action: "sabr_force", method: "POST", path: "/downloads/sabr/force" },
  { tool: "avkit_download", action: "sabr_clear", method: "POST", path: "/downloads/sabr/clear" },
  { tool: "avkit_download", action: "cookies_test", method: "POST", path: "/downloads/cookies/test" },
  { tool: "avkit_download", action: "apply_defaults", method: "POST", path: "/downloads/apply-defaults" },
  { tool: "avkit_transcript", action: "add", method: "POST", path: "/transcripts" },
  { tool: "avkit_transcript", action: "list", method: "GET", path: "/transcripts" },
  { tool: "avkit_transcript", action: "get", method: "GET", path: "/transcripts/{id}" },
  { tool: "avkit_transcript", action: "start", method: "POST", path: "/transcripts/start" },
  { tool: "avkit_transcript", action: "pause", method: "POST", path: "/transcripts/pause" },
  { tool: "avkit_transcript", action: "resume", method: "POST", path: "/transcripts/resume" },
  { tool: "avkit_transcript", action: "stop", method: "POST", path: "/transcripts/stop" },
  { tool: "avkit_transcript", action: "requeue", method: "POST", path: "/transcripts/{id}/requeue" },
  { tool: "avkit_transcript", action: "retry", method: "POST", path: "/transcripts/{id}/retry" },
  { tool: "avkit_transcript", action: "reorder", method: "PUT", path: "/transcripts/reorder" },
  { tool: "avkit_transcript", action: "remove", method: "DELETE", path: "/transcripts/{id}" },
  { tool: "avkit_transcript", action: "compile", method: "POST", path: "/transcripts/{id}/compile" },
  { tool: "avkit_tts", action: "prepare", method: "POST", path: "/tts/prepare" },
  { tool: "avkit_tts", action: "generate", method: "POST", path: "/tts/generate" },
  { tool: "avkit_tts", action: "get", method: "GET", path: "/tts/{id}" },
  { tool: "avkit_tts", action: "cancel", method: "DELETE", path: "/tts/{id}" },
  { tool: "avkit_tts", action: "voices", method: "GET", path: "/tts/voices" },
  { tool: "avkit_models", action: "available", method: "GET", path: "/models/available" },
  { tool: "avkit_models", action: "downloaded", method: "GET", path: "/models/downloaded" },
  { tool: "avkit_models", action: "download", method: "POST", path: "/models/download" },
  { tool: "avkit_models", action: "download_runtime", method: "GET", path: "/models/download-runtime" },
  { tool: "avkit_models", action: "load", method: "POST", path: "/models/load" },
  { tool: "avkit_models", action: "unload", method: "POST", path: "/models/unload" },
  { tool: "avkit_models", action: "status", method: "GET", path: "/models/status" },
  { tool: "avkit_settings", action: "get", method: "GET", path: "/settings/{namespace}" },
  { tool: "avkit_settings", action: "set", method: "PUT", path: "/settings/{namespace}" },
  { tool: "avkit_health", action: "dependencies", method: "GET", path: "/health/dependencies" },
  { tool: "avkit_health", action: "liveness", method: "GET", path: "/health" },
];

export const CONVERT_ACTION_INDEX: ActionRow[] = [
  { tool: "avkit_convert", action: "add", method: "POST", path: "/conversions" },
  { tool: "avkit_convert", action: "list", method: "GET", path: "/conversions" },
  { tool: "avkit_convert", action: "get", method: "GET", path: "/conversions/{id}" },
  { tool: "avkit_convert", action: "start", method: "POST", path: "/conversions/start" },
  { tool: "avkit_convert", action: "pause", method: "POST", path: "/conversions/pause" },
  { tool: "avkit_convert", action: "resume", method: "POST", path: "/conversions/resume" },
  { tool: "avkit_convert", action: "cancel", method: "POST", path: "/conversions/cancel" },
  { tool: "avkit_convert", action: "reorder", method: "PUT", path: "/conversions/reorder" },
  { tool: "avkit_convert", action: "reset", method: "POST", path: "/conversions/{id}/reset" },
  { tool: "avkit_convert", action: "remove", method: "DELETE", path: "/conversions/{id}" },
  { tool: "avkit_convert", action: "clear", method: "DELETE", path: "/conversions" },
  { tool: "avkit_convert", action: "gpu", method: "GET", path: "/conversions/gpu" },
  { tool: "avkit_convert", action: "gpu_refresh", method: "POST", path: "/conversions/gpu/refresh" },
  { tool: "avkit_convert", action: "probe", method: "POST", path: "/conversions/probe" },
];

export const CAPTURE_ACTION_INDEX: ActionRow[] = [
  { tool: "avkit_capture", action: "list", method: "GET", path: "/captures" },
  { tool: "avkit_capture", action: "get", method: "GET", path: "/captures/{id}" },
  { tool: "avkit_capture", action: "image", method: "GET", path: "/captures/{id}/image" },
  { tool: "avkit_capture", action: "capture", method: "POST", path: "/captures" },
  { tool: "avkit_capture", action: "capture_interactive", method: "POST", path: "/captures/requests" },
  { tool: "avkit_capture", action: "list_requests", method: "GET", path: "/captures/requests" },
  { tool: "avkit_capture", action: "annotate", method: "POST", path: "/captures/{id}/annotate" },
  { tool: "avkit_capture", action: "remove", method: "DELETE", path: "/captures/{id}" },
  // TA-2 (Session 30, MEU-67): +flatten, +revert after remove.
  { tool: "avkit_capture", action: "flatten", method: "POST", path: "/captures/{id}/flatten" },
  { tool: "avkit_capture", action: "revert", method: "POST", path: "/captures/{id}/revert" },
];

export const EXPECTED_COMPOUND_TOOLS = [
  "avkit_download",
  "avkit_transcript",
  "avkit_tts",
  "avkit_models",
  "avkit_settings",
  "avkit_health",
  "avkit_convert",
  "avkit_capture",
] as const;

export const OLD_TOOL_NAMES = [
  "avkit_download_add",
  "avkit_download_start",
  "avkit_download_stop",
  "avkit_download_status",
  "avkit_download_list",
  "avkit_transcript_add",
  "avkit_transcript_start",
  "avkit_transcript_status",
  "avkit_transcript_compile",
  "avkit_tts_generate",
  "avkit_tts_voices",
  "avkit_tts_model_status",
  "avkit_tts_model_load",
  "avkit_settings_get",
  "avkit_settings_set",
] as const;

export const DESTRUCTIVE_KEYS = [
  "avkit_download.remove",
  "avkit_download.clear",
  "avkit_transcript.remove",
  "avkit_tts.cancel",
  "avkit_convert.remove",
  "avkit_convert.clear",
  "avkit_capture.remove",
  // TA-2 (Session 30, MEU-67).
  "avkit_capture.flatten",
  "avkit_capture.revert",
] as const;

export const NON_DESTRUCTIVE_STOPS = [
  "avkit_download.cancel",
  "avkit_download.stop",
  "avkit_transcript.stop",
  "avkit_convert.cancel",
] as const;

export const M7_MARKERS = ["Workflow:", "Prerequisite:", "Returns:", "Errors:"] as const;

export function minimalInput(tool: string, action: string): Record<string, unknown> {
  const key = `${tool}.${action}`;
  const table: Record<string, Record<string, unknown>> = {
    "avkit_download.add": { action: "add", url: "https://youtu.be/x", quality: "1080p" },
    "avkit_download.list": { action: "list" },
    "avkit_download.get": { action: "get", id: "j1" },
    "avkit_download.start": { action: "start" },
    "avkit_download.pause": { action: "pause" },
    "avkit_download.resume": { action: "resume" },
    "avkit_download.cancel": { action: "cancel" },
    "avkit_download.stop": { action: "stop" },
    "avkit_download.reorder": { action: "reorder", job_ids: ["b", "a"] },
    "avkit_download.reset": { action: "reset", id: "j1" },
    "avkit_download.remove": { action: "remove", id: "j1", confirm: true },
    "avkit_download.clear": { action: "clear", confirm: true },
    "avkit_download.sabr_get": { action: "sabr_get" },
    "avkit_download.sabr_check": { action: "sabr_check" },
    "avkit_download.sabr_force": { action: "sabr_force" },
    "avkit_download.sabr_clear": { action: "sabr_clear" },
    "avkit_download.cookies_test": { action: "cookies_test", mode: "none" },
    "avkit_download.apply_defaults": { action: "apply_defaults" },
    "avkit_transcript.add": { action: "add", channel_url: "https://youtube.com/@c" },
    "avkit_transcript.list": { action: "list" },
    "avkit_transcript.get": { action: "get", id: "t1" },
    "avkit_transcript.start": { action: "start" },
    "avkit_transcript.pause": { action: "pause" },
    "avkit_transcript.resume": { action: "resume" },
    "avkit_transcript.stop": { action: "stop" },
    "avkit_transcript.requeue": { action: "requeue", id: "t1" },
    "avkit_transcript.retry": { action: "retry", id: "t1" },
    "avkit_transcript.reorder": { action: "reorder", job_ids: ["t2", "t1"] },
    "avkit_transcript.remove": { action: "remove", id: "t1", confirm: true },
    "avkit_transcript.compile": { action: "compile", id: "t1" },
    "avkit_tts.prepare": { action: "prepare", text: "hi", enabled_steps: [] },
    "avkit_tts.generate": {
      action: "generate",
      text: "hi",
      voice: "am_eric",
      speed: 1,
      format: "MP3",
      enabled_steps: [],
    },
    "avkit_tts.get": { action: "get", id: "tts1" },
    "avkit_tts.cancel": { action: "cancel", id: "tts1", confirm: true },
    "avkit_tts.voices": { action: "voices" },
    "avkit_models.available": { action: "available" },
    "avkit_models.downloaded": { action: "downloaded" },
    "avkit_models.download": { action: "download", variant_id: "v1" },
    "avkit_models.download_runtime": { action: "download_runtime" },
    "avkit_models.load": { action: "load", variant_id: "v1" },
    "avkit_models.unload": { action: "unload" },
    "avkit_models.status": { action: "status" },
    "avkit_settings.get": { action: "get", namespace: "downloader" },
    "avkit_settings.set": { action: "set", namespace: "ui", theme: "dark" },
    "avkit_health.dependencies": { action: "dependencies" },
    "avkit_health.liveness": { action: "liveness" },
    "avkit_convert.add": { action: "add", kind: "compress", paths: ["C:/tmp/a.mp4"] },
    "avkit_convert.list": { action: "list" },
    "avkit_convert.get": { action: "get", id: "c1" },
    "avkit_convert.start": { action: "start" },
    "avkit_convert.pause": { action: "pause" },
    "avkit_convert.resume": { action: "resume" },
    "avkit_convert.cancel": { action: "cancel" },
    "avkit_convert.reorder": { action: "reorder", job_ids: ["c2", "c1"] },
    "avkit_convert.reset": { action: "reset", id: "c1" },
    "avkit_convert.remove": { action: "remove", id: "c1", confirm: true },
    "avkit_convert.clear": { action: "clear", confirm: true },
    "avkit_convert.gpu": { action: "gpu" },
    "avkit_convert.gpu_refresh": { action: "gpu_refresh" },
    "avkit_convert.probe": { action: "probe", path: "C:/tmp/clip.mp4" },
    "avkit_capture.list": { action: "list" },
    "avkit_capture.get": { action: "get", id: "s1" },
    "avkit_capture.image": { action: "image", id: "s1" },
    "avkit_capture.capture": { action: "capture", mode: "fullscreen" },
    "avkit_capture.capture_interactive": { action: "capture_interactive" },
    "avkit_capture.list_requests": { action: "list_requests" },
    "avkit_capture.annotate": { action: "annotate", id: "s1", annotations: [] },
    "avkit_capture.remove": { action: "remove", id: "s1", confirm: true },
    "avkit_capture.flatten": { action: "flatten", id: "s1", confirm: true },
    "avkit_capture.revert": { action: "revert", id: "s1", confirm: true },
    "avkit_capture.frames": { action: "frames", path: "C:/tmp/clip.mp4", count: 3 },
  };
  const found = table[key];
  if (!found) {
    throw new Error(`no minimal input for ${key}`);
  }
  return { ...found };
}

export function expectedBody(tool: string, action: string): unknown {
  const key = `${tool}.${action}`;
  const table: Record<string, unknown> = {
    "avkit_download.add": { url: "https://youtu.be/x", quality: "1080p" },
    "avkit_download.list": undefined,
    "avkit_download.get": undefined,
    "avkit_download.start": {},
    "avkit_download.pause": {},
    "avkit_download.resume": {},
    "avkit_download.cancel": {},
    "avkit_download.stop": {},
    "avkit_download.reorder": { job_ids: ["b", "a"] },
    "avkit_download.reset": {},
    "avkit_download.remove": undefined,
    "avkit_download.clear": undefined,
    "avkit_download.sabr_get": undefined,
    "avkit_download.sabr_check": {},
    "avkit_download.sabr_force": {},
    "avkit_download.sabr_clear": {},
    "avkit_download.cookies_test": { mode: "none" },
    "avkit_download.apply_defaults": {},
    "avkit_transcript.add": { channel_url: "https://youtube.com/@c" },
    "avkit_transcript.list": undefined,
    "avkit_transcript.get": undefined,
    "avkit_transcript.start": {},
    "avkit_transcript.pause": {},
    "avkit_transcript.resume": {},
    "avkit_transcript.stop": {},
    "avkit_transcript.requeue": {},
    "avkit_transcript.retry": {},
    "avkit_transcript.reorder": { job_ids: ["t2", "t1"] },
    "avkit_transcript.remove": undefined,
    "avkit_transcript.compile": {},
    "avkit_tts.prepare": { text: "hi", enabled_steps: [] },
    "avkit_tts.generate": {
      text: "hi",
      voice: "am_eric",
      speed: 1,
      format: "MP3",
      enabled_steps: [],
    },
    "avkit_tts.get": undefined,
    "avkit_tts.cancel": undefined,
    "avkit_tts.voices": undefined,
    "avkit_models.available": undefined,
    "avkit_models.downloaded": undefined,
    "avkit_models.download": { variant_id: "v1" },
    "avkit_models.download_runtime": undefined,
    "avkit_models.load": { variant_id: "v1" },
    "avkit_models.unload": {},
    "avkit_models.status": undefined,
    "avkit_settings.get": undefined,
    "avkit_settings.set": { theme: "dark" },
    "avkit_health.dependencies": undefined,
    "avkit_health.liveness": undefined,
    "avkit_convert.add": { kind: "compress", paths: ["C:/tmp/a.mp4"] },
    "avkit_convert.list": undefined,
    "avkit_convert.get": undefined,
    "avkit_convert.start": {},
    "avkit_convert.pause": {},
    "avkit_convert.resume": {},
    "avkit_convert.cancel": {},
    "avkit_convert.reorder": { job_ids: ["c2", "c1"] },
    "avkit_convert.reset": {},
    "avkit_convert.remove": undefined,
    "avkit_convert.clear": undefined,
    "avkit_convert.gpu": undefined,
    "avkit_convert.gpu_refresh": {},
    "avkit_convert.probe": { path: "C:/tmp/clip.mp4" },
    "avkit_capture.list": undefined,
    "avkit_capture.get": undefined,
    "avkit_capture.image": undefined,
    "avkit_capture.capture": { mode: "fullscreen" },
    "avkit_capture.capture_interactive": {},
    "avkit_capture.list_requests": undefined,
    "avkit_capture.annotate": { annotations: [] },
    "avkit_capture.remove": undefined,
    "avkit_capture.flatten": {},
    "avkit_capture.revert": {},
    "avkit_capture.frames": { path: "C:/tmp/clip.mp4", count: 3 },
  };
  if (!(key in table)) {
    throw new Error(`no expected body for ${key}`);
  }
  return table[key];
}

export function interpolatePath(template: string, args: Record<string, unknown>): string {
  return template.replace(/\{([a-z_]+)\}/g, (_m, name: string) => String(args[name]));
}

export function tempAppData(): string {
  return mkdtempSync(path.join(os.tmpdir(), "avkit-mcp-18-"));
}

export function cleanupDirs(dirs: string[]): void {
  for (const dir of dirs.splice(0)) {
    rmSync(dir, { recursive: true, force: true });
  }
}

export function toolEnv(appData: string): NodeJS.ProcessEnv {
  return {
    AVKIT_APP_DATA: appData,
    AVKIT_API_BASE: API_BASE,
    AVKIT_API_TOKEN: "tok",
  };
}

export function okJson(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export function listEnvelope(items: unknown[] = []): { items: unknown[]; processor: { state: string; current_job_id: null } } {
  return { items, processor: { state: "Idle", current_job_id: null } };
}
