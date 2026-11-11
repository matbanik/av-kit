import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { ListToolsRequestSchema, type ListToolsResult } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { ADD_TIMEOUT_MS, api, apiBinary, redactSecrets, toToolError } from "../client.js";
import { collectTokenSecrets } from "../config.js";
import {
  confirmMissing,
  needsUserConfirm,
  USER_CONFIRM_AUTODECLINE_MS,
  USER_CONFIRM_TIMEOUT_MS,
  userConfirmMessage,
  type UserConfirmOutcome,
  type UserConfirmRequest,
} from "../destructive.js";
import { nativeConfirm } from "../native-confirm.js";
import { captureDescriptions, captureSchema, GET_QUERY_KEYS, IMAGE_MAX_BYTES } from "./capture.js";
import { convertDescriptions, convertSchema } from "./convert.js";
import { downloadDescriptions, downloadSchema } from "./download.js";
import { healthDescriptions, healthSchema } from "./health.js";
import { modelsDescriptions, modelsSchema } from "./models.js";
import { SETTINGS_SCHEMA, SETTINGS_SCHEMA_URI, settingsDescriptions, settingsSchema } from "./settings.js";
import { transcriptDescriptions, transcriptSchema } from "./transcript.js";
import { ttsDescriptions, ttsSchema } from "./tts.js";

export type ActionRow = {
  tool: string;
  action: string;
  method: string;
  path: string;
};

export const COMPOUND_TOOLS = [
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

export const ACTION_INDEX: ActionRow[] = [
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
  { tool: "avkit_capture", action: "list", method: "GET", path: "/captures" },
  { tool: "avkit_capture", action: "get", method: "GET", path: "/captures/{id}" },
  { tool: "avkit_capture", action: "image", method: "GET", path: "/captures/{id}/image" },
  { tool: "avkit_capture", action: "capture", method: "POST", path: "/captures" },
  { tool: "avkit_capture", action: "capture_interactive", method: "POST", path: "/captures/requests" },
  { tool: "avkit_capture", action: "list_requests", method: "GET", path: "/captures/requests" },
  { tool: "avkit_capture", action: "annotate", method: "POST", path: "/captures/{id}/annotate" },
  { tool: "avkit_capture", action: "remove", method: "DELETE", path: "/captures/{id}" },
  // MEU-67: before download_asset, which stays the last row.
  { tool: "avkit_capture", action: "flatten", method: "POST", path: "/captures/{id}/flatten" },
  { tool: "avkit_capture", action: "revert", method: "POST", path: "/captures/{id}/revert" },
  { tool: "avkit_capture", action: "crop", method: "POST", path: "/captures/{id}/crop" },
  { tool: "avkit_capture", action: "frames", method: "POST", path: "/captures/frames" },
  // MEU-62: appended so the KEEP / Convert / Capture positions stay fixed.
  { tool: "avkit_models", action: "download_asset", method: "POST", path: "/models/download" },
];

export const ACTION_DESCRIPTIONS: Record<string, string> = {
  ...downloadDescriptions,
  ...transcriptDescriptions,
  ...ttsDescriptions,
  ...modelsDescriptions,
  ...settingsDescriptions,
  ...healthDescriptions,
  ...convertDescriptions,
  ...captureDescriptions,
};

const SCHEMAS: Record<string, z.ZodType> = {
  avkit_download: downloadSchema,
  avkit_transcript: transcriptSchema,
  avkit_tts: ttsSchema,
  avkit_models: modelsSchema,
  avkit_settings: settingsSchema,
  avkit_health: healthSchema,
  avkit_convert: convertSchema,
  avkit_capture: captureSchema,
};

const TOOL_TOP_LEVEL: Record<string, string> = {
  avkit_download: "Workflow: add → start → list. Prerequisite: token. Returns: queue JSON. Errors: TOOL_ERROR.",
  avkit_transcript: "Workflow: add → start → get. Prerequisite: channel URL. Returns: paths/counts. Errors: TOOL_ERROR.",
  avkit_tts: "Workflow: load model → generate → get. Prerequisite: loaded model. Returns: preview/hash. Errors: TOOL_ERROR.",
  avkit_models: "Workflow: download → load. Prerequisite: disk. Returns: variant JSON. Errors: TOOL_ERROR.",
  avkit_settings: `Workflow: get/set leaves. Prerequisite: see ${SETTINGS_SCHEMA_URI}. Returns: leaf map. Errors: TOOL_ERROR.`,
  avkit_health: "Workflow: liveness then dependencies. Prerequisite: api_base. Returns: status JSON. Errors: TOOL_ERROR.",
  avkit_convert: "Workflow: add → start → list. Prerequisite: local files only. Returns: queue JSON. Errors: TOOL_ERROR.",
  avkit_capture: "Workflow: capture or list → get/image → annotate. Prerequisite: local screen and inbox files. Returns: catalog JSON or image. Errors: TOOL_ERROR.",
};

const FORBIDDEN_KEYS = new Set([
  "text",
  "video_ids",
  "lang_code",
  "cookie_bytes",
  "cookies",
  "media_bytes",
  "audio_bytes",
  "image_bytes",
]);

export type ToolRuntime = {
  env?: NodeJS.ProcessEnv;
  fetchImpl?: typeof fetch;
  /** USER_CONFIRM: asks the person in the IDE; absent means "unsupported" (refused). */
  confirmWithUser?: (request: UserConfirmRequest) => Promise<UserConfirmOutcome>;
};

export type ToolContent =
  | { type: "text"; text: string }
  | { type: "image"; data: string; mimeType: string };

export type ToolResult = {
  content: ToolContent[];
  isError?: boolean;
};

function interpolatePath(template: string, args: Record<string, unknown>): string {
  // Each value fills exactly one path segment: percent-encoding stops "/" and ".." from
  // reaching another route (review F1).
  return template.replace(/\{([a-z_]+)\}/g, (_m, name: string) => encodeURIComponent(String(args[name] ?? "")));
}

const FRAME_MAP = "source_x = region.x + x / scale; source_y = region.y + y / scale";

type CaptureFrame = {
  source: { width: number; height: number };
  region: { x: number; y: number; width: number; height: number };
  returned: { width: number; height: number };
  scale: number;
  clamped: boolean;
};

function parseInts(value: string | undefined, count: number): number[] | null {
  if (value === undefined) {
    return null;
  }
  const parts = value.split(",");
  if (parts.length !== count || !parts.every((part) => /^\d+$/.test(part))) {
    return null;
  }
  return parts.map((part) => Number(part));
}

/** FRAME_ITEM: the five X-Capture-* headers as one frame, or null when any is missing or bad. */
function parseCaptureFrame(headers: Record<string, string>): CaptureFrame | null {
  const source = parseInts(headers["x-capture-source"], 2);
  const region = parseInts(headers["x-capture-region"], 4);
  const returned = parseInts(headers["x-capture-returned"], 2);
  const scaleText = headers["x-capture-scale"];
  const clampedText = headers["x-capture-clamped"];
  if (source === null || region === null || returned === null || scaleText === undefined) {
    return null;
  }
  const scale = Number(scaleText);
  if (!/^\d+(\.\d+)?$/.test(scaleText) || !Number.isFinite(scale) || scale <= 0) {
    return null;
  }
  if (clampedText !== "true" && clampedText !== "false") {
    return null;
  }
  return {
    source: { width: source[0], height: source[1] },
    region: { x: region[0], y: region[1], width: region[2], height: region[3] },
    returned: { width: returned[0], height: returned[1] },
    scale,
    clamped: clampedText === "true",
  };
}

function withQuery(path: string, record: Record<string, unknown>): string {
  const params = new URLSearchParams();
  for (const key of GET_QUERY_KEYS) {
    const value = record[key];
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  }
  const qs = params.toString();
  return qs === "" ? path : `${path}?${qs}`;
}

function httpBody(method: string, parsed: Record<string, unknown>, pathTemplate: string): unknown {
  if (method === "GET" || method === "DELETE") {
    return undefined;
  }
  const out: Record<string, unknown> = {};
  const dropId = pathTemplate.includes("{id}");
  const dropNs = pathTemplate.includes("{namespace}");
  for (const [key, value] of Object.entries(parsed)) {
    if (key === "action" || key === "confirm") {
      continue;
    }
    if (key === "variant" || key === "status") {
      continue;
    }
    if (dropId && key === "id") {
      continue;
    }
    if (dropNs && key === "namespace") {
      continue;
    }
    if (value !== undefined) {
      out[key] = value;
    }
  }
  return out;
}

function assertNever(value: never): never {
  throw new Error(`unexpected value ${String(value)}`);
}

function userConfirmProceeds(outcome: UserConfirmOutcome): boolean {
  switch (outcome) {
    case "accept":
      return true;
    case "decline":
    case "cancel":
    case "unsupported":
      return false;
    default:
      return assertNever(outcome);
  }
}

async function askUser(runtime: ToolRuntime | undefined, request: UserConfirmRequest): Promise<UserConfirmOutcome> {
  if (!runtime?.confirmWithUser) {
    return "unsupported";
  }
  try {
    return await runtime.confirmWithUser(request);
  } catch {
    return "cancel";
  }
}

function isCatalogEnvelope(data: unknown): data is { items: unknown[] } {
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    return false;
  }
  const rec = data as { items?: unknown };
  return Array.isArray(rec.items) && !Object.prototype.hasOwnProperty.call(rec, "processor");
}

function isListEnvelope(data: unknown): data is { items: unknown[]; processor: unknown } {
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    return false;
  }
  const rec = data as { items?: unknown; processor?: unknown };
  return Array.isArray(rec.items) && rec.processor !== undefined && rec.processor !== null;
}

function sanitize(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(sanitize);
  }
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [key, child] of Object.entries(value as Record<string, unknown>)) {
      if (FORBIDDEN_KEYS.has(key)) {
        continue;
      }
      out[key] = sanitize(child);
    }
    return out;
  }
  return value;
}

export async function handleTool(tool: string, args: unknown, runtime?: ToolRuntime): Promise<ToolResult> {
  const env = runtime?.env ?? process.env;
  const schema = SCHEMAS[tool];
  if (!schema) {
    return toToolError({ code: "unknown_tool", message: `unknown tool ${tool}` }, env);
  }
  const parsed = schema.safeParse(args);
  if (!parsed.success) {
    return toToolError({
      code: "validation_error",
      message: parsed.error.issues.map((issue) => issue.message).join("; "),
    }, env);
  }
  const record = parsed.data as Record<string, unknown>;
  const action = String(record.action);
  if (confirmMissing(tool, action, record)) {
    return toToolError({ code: "confirm_required", message: `${tool}.${action} requires confirm: true` }, env);
  }
  if (needsUserConfirm(tool, action)) {
    const id = String(record.id);
    const outcome = await askUser(runtime, { tool, action, id, message: userConfirmMessage(tool, action, id) });
    if (!userConfirmProceeds(outcome)) {
      return toToolError({
        code: "user_confirmation_refused",
        message: `${tool}.${action} was not run: the user confirmation outcome was ${outcome}`,
      }, env);
    }
  }
  const row = ACTION_INDEX.find((item) => item.tool === tool && item.action === action);
  if (!row) {
    return toToolError({ code: "unknown_action", message: `${tool}.${action}` }, env);
  }
  // QUERY_GET_ONLY (MEU-128, D-413): a POST capture region keeps x, y, width and height in
  // its body and sends no query string.
  const path = row.method === "GET"
    ? withQuery(interpolatePath(row.path, record), record)
    : interpolatePath(row.path, record);
  const timeoutMs = (
    ((tool === "avkit_download" || tool === "avkit_transcript" || tool === "avkit_convert") && action === "add")
    // FRAMES_MCP under D-577 A: frames waits up to FRAMES_RETURN_S + COMMIT_WAIT_S (111 s).
    || (tool === "avkit_capture" && (action === "capture" || action === "crop" || action === "frames"))
  )
    ? ADD_TIMEOUT_MS
    : undefined;
  if (tool === "avkit_capture" && action === "image") {
    const binary = await apiBinary(row.method, path, {
      env,
      fetchImpl: runtime?.fetchImpl,
      timeoutMs,
    });
    if (!binary.ok) {
      return toToolError(binary.error, env);
    }
    if (binary.bytes.byteLength > IMAGE_MAX_BYTES) {
      return toToolError({
        code: "payload_too_large",
        message: `image exceeds the ${IMAGE_MAX_BYTES} B MCP limit; read original_path or annotated_path from avkit_capture get and open that file, or pass max_edge (64 to 2576) or x, y, width and height for a smaller image`,
      }, env);
    }
    const image = {
      type: "image" as const,
      data: Buffer.from(binary.bytes).toString("base64"),
      mimeType: binary.mimeType,
    };
    // FRAME_ITEM (MEU-128, D-412): the frame text first when all five headers parse.
    const frame = parseCaptureFrame(binary.captureHeaders);
    if (frame === null) {
      return { content: [image] };
    }
    return {
      content: [
        { type: "text", text: JSON.stringify({ frame, map: FRAME_MAP }) },
        image,
      ],
    };
  }
  const result = await api(row.method, path, httpBody(row.method, record, row.path), {
    env,
    fetchImpl: runtime?.fetchImpl,
    timeoutMs,
  });
  if (!result.ok) {
    return toToolError(result.error, env);
  }
  if (tool === "avkit_capture" && (action === "list" || action === "list_requests")) {
    if (!isCatalogEnvelope(result.data)) {
      return toToolError({
        code: "invalid_catalog_envelope",
        message: "capture list must return { items } without processor",
      }, env);
    }
  } else if (action === "list" && !isListEnvelope(result.data)) {
    return toToolError({
      code: "invalid_list_envelope",
      message: "list must return { items, processor }, not a bare array",
    }, env);
  }
  return {
    content: [{
      type: "text",
      text: redactSecrets(JSON.stringify(sanitize(result.data)), collectTokenSecrets(env)),
    }],
  };
}

/** The object branches of a tool's per-action union (descriptions are on the branches). */
function branchesOf(schema: z.ZodTypeAny): z.ZodObject[] {
  if (schema instanceof z.ZodObject) {
    return [schema];
  }
  if (schema instanceof z.ZodUnion || schema instanceof z.ZodDiscriminatedUnion) {
    return (schema.options as z.ZodTypeAny[]).flatMap(branchesOf);
  }
  throw new Error(`unsupported tool schema ${schema.constructor.name}`);
}

function unwrapOptional(schema: z.ZodTypeAny): z.ZodTypeAny {
  return schema instanceof z.ZodOptional ? unwrapOptional(schema.unwrap() as z.ZodTypeAny) : schema;
}

/**
 * ADVERTISED_SCHEMA (A-9): one flat object per tool for tools/list — `action` as an enum of the
 * tool's actions, every other branch field typed and optional. Only advertised; the registered
 * strict union still validates every call.
 */
export function advertisedSchema(tool: string): z.ZodObject {
  const actions = ACTION_INDEX.filter((row) => row.tool === tool).map((row) => row.action);
  if (actions.length === 0) {
    throw new Error(`no actions for ${tool}`);
  }
  const fields = new Map<string, z.ZodTypeAny[]>();
  for (const branch of branchesOf(SCHEMAS[tool])) {
    for (const [key, field] of Object.entries(branch.shape as Record<string, z.ZodTypeAny>)) {
      if (key === "action") {
        continue;
      }
      const inner = unwrapOptional(field);
      const seen = fields.get(key) ?? [];
      const sig = JSON.stringify(toJsonSchemaCompat(z.object({ v: inner })));
      if (!seen.some((other) => JSON.stringify(toJsonSchemaCompat(z.object({ v: other }))) === sig)) {
        seen.push(inner);
      }
      fields.set(key, seen);
    }
  }
  const shape: Record<string, z.ZodTypeAny> = {
    action: z.enum(actions as [string, ...string[]]).describe(`One of: ${actions.join(", ")}.`),
  };
  for (const [key, list] of fields) {
    const typed = list.length === 1 ? list[0] : z.union(list as [z.ZodTypeAny, z.ZodTypeAny, ...z.ZodTypeAny[]]);
    shape[key] = typed.optional();
  }
  return z.object(shape).strict();
}

type ListToolsHandler = (request: unknown, extra: unknown) => Promise<ListToolsResult>;

/** Rewrites tools/list so each compound tool advertises ADVERTISED_SCHEMA (A-9). */
function advertiseSchemas(server: McpServer): void {
  const handlers = (server.server as unknown as { _requestHandlers: Map<string, ListToolsHandler> })._requestHandlers;
  const original = handlers.get("tools/list");
  if (original === undefined) {
    throw new Error("tools/list handler missing; register tools first");
  }
  const advertised = Object.fromEntries(
    COMPOUND_TOOLS.map((name) => [name, toJsonSchemaCompat(advertisedSchema(name), { strictUnions: true, pipeStrategy: "input" })]),
  );
  server.server.removeRequestHandler("tools/list");
  server.server.setRequestHandler(ListToolsRequestSchema, async (request, extra) => {
    const result = await original(request, extra);
    return {
      ...result,
      tools: result.tools.map((tool) =>
        tool.name in advertised ? { ...tool, inputSchema: advertised[tool.name] as ListToolsResult["tools"][number]["inputSchema"] } : tool,
      ),
    };
  });
}

const USER_CONFIRM_SCHEMA = {
  type: "object" as const,
  properties: { confirm: { type: "boolean" as const, title: "Allow" } },
  required: ["confirm"],
};

/** USER_CONFIRM over MCP elicitation (form mode); anything but an explicit accept is a refusal. */
async function elicit(server: McpServer, request: UserConfirmRequest): Promise<UserConfirmOutcome> {
  if (!server.server.getClientCapabilities()?.elicitation?.form) {
    return "unsupported";
  }
  try {
    const result = await server.server.elicitInput(
      { message: request.message, requestedSchema: USER_CONFIRM_SCHEMA },
      { timeout: USER_CONFIRM_TIMEOUT_MS },
    );
    if (result.action === "accept" && result.content?.confirm === true) {
      return "accept";
    }
    return result.action === "decline" ? "decline" : "cancel";
  } catch {
    return "cancel";
  }
}

export type McpSurfaceOptions = {
  /** DIALOG_FALLBACK prompt; "unsupported" means no dialog could be shown. */
  nativeConfirm?: (message: string) => Promise<UserConfirmOutcome>;
  /** Monotonic milliseconds for the auto-decline timing (A-11 review F2). */
  now?: () => number;
  /** One line per USER_CONFIRM; stderr by default, which the IDE keeps in its MCP log (stdout is the protocol). */
  log?: (line: string) => void;
};

/**
 * Elicitation first; when the client cannot ask, or refuses faster than a person could
 * (USER_CONFIRM_AUTODECLINE_MS), the person is asked with a native dialog instead (A-11).
 */
function confirmWithFallback(
  server: McpServer,
  fallback: (message: string) => Promise<UserConfirmOutcome>,
  now: () => number,
  log: (line: string) => void,
): (request: UserConfirmRequest) => Promise<UserConfirmOutcome> {
  return async (request) => {
    const started = now();
    const outcome = await elicit(server, request);
    const elapsed = Math.round(now() - started);
    const head = `avkit USER_CONFIRM ${request.tool}.${request.action} ${request.id}: elicitation ${outcome} in ${elapsed} ms`;
    const clientAnswered = outcome === "unsupported" || elapsed < USER_CONFIRM_AUTODECLINE_MS;
    if (outcome === "accept" || !clientAnswered) {
      log(`${head}; dialog not asked`);
      return outcome;
    }
    const dialogStarted = now();
    const asked = await fallback(request.message);
    log(`${head}; dialog ${asked} in ${Math.round(now() - dialogStarted)} ms`);
    return asked === "unsupported" ? outcome : asked;
  };
}

export function registerMcpSurface(server: McpServer, options: McpSurfaceOptions = {}): void {
  const confirmWithUser = confirmWithFallback(
    server,
    options.nativeConfirm ?? nativeConfirm,
    options.now ?? (() => performance.now()),
    options.log ?? ((line) => process.stderr.write(`${line}
`)),
  );
  for (const name of COMPOUND_TOOLS) {
    const action_descriptions = Object.fromEntries(
      ACTION_INDEX
        .filter((row) => row.tool === name)
        .map((row) => [row.action, ACTION_DESCRIPTIONS[`${name}.${row.action}`]]),
    );
    server.registerTool(
      name,
      {
        title: name,
        description: TOOL_TOP_LEVEL[name],
        inputSchema: SCHEMAS[name],
        _meta: { action_descriptions },
      },
      async (args) => handleTool(name, args, { confirmWithUser }),
    );
  }
  advertiseSchemas(server);
  server.registerResource(
    "settings-schema",
    SETTINGS_SCHEMA_URI,
    { description: `Locked settings key table at ${SETTINGS_SCHEMA_URI}` },
    async () => ({
      contents: [
        {
          uri: SETTINGS_SCHEMA_URI,
          mimeType: "application/json",
          text: JSON.stringify(SETTINGS_SCHEMA),
        },
      ],
    }),
  );
}
