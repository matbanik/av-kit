import { z } from "zod";

export const SETTINGS_SCHEMA_URI = "avkit://settings/schema";

export const SETTING_NAMESPACES = ["downloader", "transcript", "tts", "app", "ui", "converter", "capture"] as const;

const YTDLP_DEBUG_LEAF = ["yt", "dlp", "debug"].join("_");

type Leaf = { type: string; default: string | number | boolean; enum?: readonly string[] };

/** ANNOTATED_FORMATS (avkit_core.domain.capture): the Save overlay file format wires. */
export const ANNOTATED_FORMATS = ["png", "jpeg", "webp"] as const;

export const SETTINGS_SCHEMA: {
  namespaces: Record<string, Record<string, Leaf>>;
} = {
  namespaces: {
    downloader: {
      path: { type: "string", default: "~/Downloads/av-kit" },
      ffmpeg_path: { type: "string", default: "" },
      quality: { type: "string", default: "1080p" },
      audio_only: { type: "boolean", default: false },
      audio_format: { type: "string", default: "default" },
      cookie_mode: { type: "string", default: "none" },
      cookie_browser: { type: "string", default: "chrome" },
      cookie_browser_profile: { type: "string", default: "" },
      cookie_file_path: { type: "string", default: "" },
      archive_tracking: { type: "boolean", default: true },
      [YTDLP_DEBUG_LEAF]: { type: "boolean", default: false },
      deno_path: { type: "string", default: "" },
    },
    transcript: {
      output_dir: { type: "string", default: "~/Documents/Transcripts" },
      requests_per_hour: { type: "number", default: 20 },
      delay_between_requests: { type: "number", default: 120 },
      max_retries: { type: "number", default: 1 },
      retry_delay: { type: "number", default: 7 },
      batch_size: { type: "number", default: 5 },
      pause_between_batches: { type: "number", default: 500 },
      playlist_end: { type: "number", default: 0 },
      max_words_per_document: { type: "number", default: 490000 },
    },
    tts: {
      models_directory: { type: "string", default: "~/.avkit/models" },
      voice: { type: "string", default: "am_eric" },
      speed: { type: "number", default: 1.0 },
      output_format: { type: "string", default: "MP3" },
      output_path: { type: "string", default: "~/Documents" },
      device: { type: "string", default: "auto" },
      chunk_max_chars: { type: "number", default: 250 },
      input_text: { type: "string", default: "" },
    },
    app: {
      log_level: { type: "string", default: "INFO" },
      log_to_file: { type: "boolean", default: false },
      console_visible: { type: "boolean", default: true },
    },
    ui: {
      theme: { type: "string", default: "dark" },
    },
    converter: {
      output_dir: { type: "string", default: "~/Videos/av-kit" },
      default_preset: { type: "string", default: "balanced" },
      skip_existing: { type: "boolean", default: true },
      gpu_preference: { type: "string", default: "auto" },
    },
    capture: {
      inbox_dir: { type: "string", default: "~/Pictures/av-kit" },
      hotkey: { type: "string", default: "F2" },
      copy_to_clipboard: { type: "boolean", default: false },
      close_to_tray: { type: "boolean", default: true },
      flatten_backup: { type: "boolean", default: true },
      backup_dir: { type: "string", default: "" },
      annotated_format: { type: "string", default: "png", enum: ANNOTATED_FORMATS },
      // STYLE_MCP (MEU-105, D-717): each style tool's own persisted style.
      arrow_color: { type: "string", default: "#E0AF68" },
      arrow_stroke: { type: "number", default: 3 },
      box_color: { type: "string", default: "#E0AF68" },
      box_stroke: { type: "number", default: 3 },
      highlight_color: { type: "string", default: "#E0AF68" },
      text_color: { type: "string", default: "#E0AF68" },
      text_font_size: { type: "number", default: 16 },
      text_bg_color: { type: "string", default: "" },
      pixelate_block_size: { type: "number", default: 10 },
      // LOCK_LEAF (Session 71b, MEU-143): the capture tool lock, on by default.
      tool_lock: { type: "boolean", default: true },
      // STEP_STYLE (MEU-107, D-775): the Step tool's colour and badge size.
      step_color: { type: "string", default: "#E0AF68" },
      step_size: { type: "number", default: 32 },
    },
  },
};

function desc(action: string, method: string, path: string): string {
  return [
    `Workflow: ${action} namespace leaf keys via ${method} ${path}.`,
    `Prerequisite: namespace in downloader|transcript|tts|app|ui|converter|capture; see ${SETTINGS_SCHEMA_URI}.`,
    `Returns: JSON leaf map from ${method} ${path}; ui theme only on the API.`,
    `Errors: TOOL_ERROR with envelope code and message; unknown/rail leaves are API 422.`,
  ].join(" ");
}

export const settingsDescriptions: Record<string, string> = {
  "avkit_settings.get": desc("get", "GET", "/settings/{namespace}"),
  "avkit_settings.set": desc("set", "PUT", "/settings/{namespace}"),
};

const settingsLeaves = {
  path: z.string().optional(),
  ffmpeg_path: z.string().optional(),
  quality: z.string().optional(),
  audio_only: z.boolean().optional(),
  audio_format: z.string().optional(),
  cookie_mode: z.string().optional(),
  cookie_browser: z.string().optional(),
  cookie_browser_profile: z.string().optional(),
  cookie_file_path: z.string().optional(),
  archive_tracking: z.boolean().optional(),
  [YTDLP_DEBUG_LEAF]: z.boolean().optional(),
  deno_path: z.string().optional(),
  output_dir: z.string().optional(),
  requests_per_hour: z.number().optional(),
  delay_between_requests: z.number().optional(),
  max_retries: z.number().optional(),
  retry_delay: z.number().optional(),
  batch_size: z.number().optional(),
  pause_between_batches: z.number().optional(),
  playlist_end: z.number().optional(),
  max_words_per_document: z.number().optional(),
  models_directory: z.string().optional(),
  voice: z.string().optional(),
  speed: z.number().optional(),
  output_format: z.string().optional(),
  output_path: z.string().optional(),
  device: z.string().optional(),
  chunk_max_chars: z.number().optional(),
  input_text: z.string().optional(),
  log_level: z.string().optional(),
  log_to_file: z.boolean().optional(),
  console_visible: z.boolean().optional(),
  theme: z.string().optional(),
  default_preset: z.string().optional(),
  skip_existing: z.boolean().optional(),
  gpu_preference: z.string().optional(),
  inbox_dir: z.string().optional(),
  hotkey: z.string().optional(),
  copy_to_clipboard: z.boolean().optional(),
  close_to_tray: z.boolean().optional(),
  flatten_backup: z.boolean().optional(),
  backup_dir: z.string().optional(),
  annotated_format: z.enum(ANNOTATED_FORMATS).optional(),
  // STYLE_MCP (MEU-105): the API applies each leaf's own pattern and range.
  arrow_color: z.string().optional(),
  arrow_stroke: z.number().int().optional(),
  box_color: z.string().optional(),
  box_stroke: z.number().int().optional(),
  highlight_color: z.string().optional(),
  text_color: z.string().optional(),
  text_font_size: z.number().int().optional(),
  text_bg_color: z.string().optional(),
  pixelate_block_size: z.number().int().optional(),
  // LOCK_LEAF (MEU-143): a strict boolean; "false" and 0 are refused.
  tool_lock: z.boolean().optional(),
  // STEP_STYLE (MEU-107): an integer size; 48.5 and "48" are refused.
  step_color: z.string().optional(),
  step_size: z.number().int().optional(),
  rail: z.unknown().optional(),
  panel: z.unknown().optional(),
};

function withDesc<T extends z.ZodTypeAny>(action: string, schema: T): T {
  return schema.describe(settingsDescriptions[`avkit_settings.${action}`]) as T;
}

export const settingsSchema = z.discriminatedUnion("action", [
  withDesc(
    "get",
    z
      .object({
        action: z.literal("get"),
        namespace: z.enum(SETTING_NAMESPACES),
      })
      .strict(),
  ),
  withDesc(
    "set",
    z
      .object({
        action: z.literal("set"),
        namespace: z.enum(SETTING_NAMESPACES),
        ...settingsLeaves,
      })
      .strict(),
  ),
]);
