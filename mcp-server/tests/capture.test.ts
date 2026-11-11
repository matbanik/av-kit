import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DESTRUCTIVE_ACTIONS } from "../src/destructive.js";
import { SERVER_INSTRUCTIONS } from "../src/index.js";
import { ACTION_INDEX, COMPOUND_TOOLS, handleTool } from "../src/toolsets/registry.js";
import { SETTING_NAMESPACES, SETTINGS_SCHEMA, settingsSchema } from "../src/toolsets/settings.js";
import {
  cleanupDirs,
  listEnvelope,
  okJson,
  tempAppData,
  toolEnv,
} from "./fixtures.js";

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const CAPTURE_TS = path.join(ROOT, "src", "toolsets", "capture.ts");
const COMPOUND_DIR = path.join(ROOT, "src", "compound");
const REGISTRY_TS = path.join(ROOT, "src", "toolsets", "registry.ts");
const DIST_CAPTURE = path.join(ROOT, "dist", "toolsets", "capture.js");
const OPENAPI_COMMITTED = path.join(ROOT, "..", "openapi.committed.json");
const CAPTURE_ACTIONS = [
  { action: "list", method: "GET", path: "/captures" },
  { action: "get", method: "GET", path: "/captures/{id}" },
  { action: "image", method: "GET", path: "/captures/{id}/image" },
  { action: "capture", method: "POST", path: "/captures" },
  { action: "capture_interactive", method: "POST", path: "/captures/requests" },
  { action: "list_requests", method: "GET", path: "/captures/requests" },
  { action: "annotate", method: "POST", path: "/captures/{id}/annotate" },
  { action: "remove", method: "DELETE", path: "/captures/{id}" },
  // TA-2 (Session 30, MEU-67): +flatten, +revert after remove.
  { action: "flatten", method: "POST", path: "/captures/{id}/flatten" },
  { action: "revert", method: "POST", path: "/captures/{id}/revert" },
  // MEU-130 (Session 59): +crop after revert.
  { action: "crop", method: "POST", path: "/captures/{id}/crop" },
  // MEU-134 (Session 62): +frames after crop.
  { action: "frames", method: "POST", path: "/captures/frames" },
  // MEU-135 (Session 63): +sheet after frames.
  { action: "sheet", method: "POST", path: "/captures/sheet" },
] as const;
const REST_ONLY = ["complete", "cancel", "register"] as const;
// TA-4 (Session 30, MEU-67): + flatten_backup, backup_dir, annotated_format.
const CAPTURE_KEYS = [
  "inbox_dir",
  "hotkey",
  "copy_to_clipboard",
  "close_to_tray",
  "flatten_backup",
  "backup_dir",
  "annotated_format",
] as const;
const CAPTURE_DEFAULTS = {
  inbox_dir: "~/Pictures/av-kit",
  hotkey: "F2",
  copy_to_clipboard: false,
  close_to_tray: true,
  flatten_backup: true,
  backup_dir: "",
  annotated_format: "png",
};
const M7 = ["Workflow:", "Prerequisite:", "Returns:", "Errors:"] as const;
const SHOT_OUT_FIELDS = [
  "id",
  "original_path",
  "annotated_path",
  "sidecar_path",
  "display_name",
  "width",
  "height",
  "file_size",
  "source",
  "created_at",
  "updated_at",
] as const;
const IMAGE_MAX_BYTES = 7_800_000;
const PNG_BYTES = Uint8Array.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x6f, 0x6b]);
const SHOT_ITEM = {
  id: "s1",
  original_path: "C:/tmp/inbox/shot.png",
  annotated_path: null,
  sidecar_path: null,
  display_name: "shot.png",
  width: 32,
  height: 32,
  file_size: 12,
  source: "Hotkey",
  created_at: "2026-01-02T03:04:05Z",
  updated_at: "2026-01-02T03:04:05Z",
};
const temps: string[] = [];

afterEach(() => {
  cleanupDirs(temps);
});

function catalogEnvelope(items: unknown[] = [SHOT_ITEM]): { items: unknown[] } {
  return { items };
}

function imageResponse(body: Uint8Array, contentType = "image/png", status = 200): Response {
  return new Response(body, {
    status,
    headers: { "Content-Type": contentType },
  });
}

describe("MEU-38 avkit_capture", () => {
  it("AC-38.1 ACTION_INDEX_AFTER keeps first ACTION_INDEX_KEEP rows", () => {
    // TA-9 (Session 27, MEU-62): +1 avkit_models.download_asset, appended.
    // TA-1 (Session 30, MEU-67): +avkit_capture.flatten, +avkit_capture.revert.
    // MEU-130 (Session 59): +avkit_capture.crop after revert.
    // MEU-133 (Session 62): +avkit_convert.probe after gpu_refresh.
    // MEU-134 (Session 62): +avkit_capture.frames after crop.
    // MEU-135 (Session 63): +avkit_capture.sheet after frames.
    expect(ACTION_INDEX).toHaveLength(74);
    expect([...COMPOUND_TOOLS]).toEqual([
      "avkit_download",
      "avkit_transcript",
      "avkit_tts",
      "avkit_models",
      "avkit_settings",
      "avkit_health",
      "avkit_convert",
      "avkit_capture",
    ]);
    expect(ACTION_INDEX.slice(0, 59).every((row) => row.tool !== "avkit_capture")).toBe(true);
    expect(ACTION_INDEX.filter((row) => row.tool === "avkit_convert")).toHaveLength(14);
  });

  it("AC-38.2 CAPTURE_ACTIONS match REST 1:1; REST_ONLY absent", () => {
    const rows = ACTION_INDEX.filter((row) => row.tool === "avkit_capture");
    // TA-2 (Session 30, MEU-67); MEU-130 (Session 59): +crop; MEU-134 (Session 62): +frames.
    // MEU-135 (Session 63): +sheet.
    expect(rows).toHaveLength(13);
    expect(rows.map((row) => ({ action: row.action, method: row.method, path: row.path }))).toEqual(
      CAPTURE_ACTIONS.map((row) => ({ action: row.action, method: row.method, path: row.path })),
    );
    expect(rows.every((row) => row.path.startsWith("/captures"))).toBe(true);
    for (const action of REST_ONLY) {
      expect(rows.some((row) => row.action === action)).toBe(false);
    }
    expect(rows.some((row) => row.path.includes("/grab"))).toBe(false);
    expect(rows.some((row) => row.path.includes("/complete"))).toBe(false);
  });

  it("AC-38.3 capture schema strict extra key fails before fetch", async () => {
    const { captureSchema } = await import("../src/toolsets/capture.js");
    const parsed = captureSchema.safeParse({ action: "list", extra: true });
    expect(parsed.success).toBe(false);
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn();
    const result = await handleTool(
      "avkit_capture",
      { action: "list", extra: true },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(result.isError).toBe(true);
    expect(result.content[0].text).toContain("validation_error");
    expect(result.content[0].text).not.toContain("unknown_tool");
    expect(fetchImpl).toHaveBeenCalledTimes(0);
  });

  it("AC-38.4 DESTRUCTIVE_CAPTURE confirm; non-destructive stay out", () => {
    expect(DESTRUCTIVE_ACTIONS.has("avkit_capture.remove")).toBe(true);
    expect(DESTRUCTIVE_ACTIONS.has("avkit_capture.list")).toBe(false);
    expect(DESTRUCTIVE_ACTIONS.has("avkit_capture.get")).toBe(false);
    expect(DESTRUCTIVE_ACTIONS.has("avkit_capture.image")).toBe(false);
    expect(DESTRUCTIVE_ACTIONS.has("avkit_capture.capture")).toBe(false);
    expect(DESTRUCTIVE_ACTIONS.has("avkit_capture.capture_interactive")).toBe(false);
    expect(DESTRUCTIVE_ACTIONS.has("avkit_capture.list_requests")).toBe(false);
    expect(DESTRUCTIVE_ACTIONS.has("avkit_capture.annotate")).toBe(false);
  });

  it("AC-38.5 M7 markers and Capture local-screen instructions", async () => {
    const { captureDescriptions } = await import("../src/toolsets/capture.js");
    for (const row of CAPTURE_ACTIONS) {
      const text = captureDescriptions[`avkit_capture.${row.action}`];
      expect(typeof text).toBe("string");
      const hits = M7.filter((marker) => text.toLowerCase().includes(marker.toLowerCase()));
      expect(hits.length, row.action).toBeGreaterThanOrEqual(3);
    }
    expect(SERVER_INSTRUCTIONS.toLowerCase()).toMatch(/local screen/);
    expect(SERVER_INSTRUCTIONS).toMatch(/never upload/i);
    expect(SERVER_INSTRUCTIONS).toMatch(/YouTube/);
    expect(SERVER_INSTRUCTIONS).toMatch(/capture_interactive/);
    expect(SERVER_INSTRUCTIONS.toLowerCase()).toMatch(/desktop app/);
  });

  it("AC-38.6 SETTINGS_SCHEMA capture keys and namespace enum", () => {
    expect([...SETTING_NAMESPACES]).toContain("capture");
    const capture = SETTINGS_SCHEMA.namespaces.capture;
    expect(Object.keys(capture).sort()).toEqual([...CAPTURE_KEYS].sort());
    expect(capture.inbox_dir.default).toBe(CAPTURE_DEFAULTS.inbox_dir);
    expect(capture.hotkey.default).toBe(CAPTURE_DEFAULTS.hotkey);
    expect(capture.copy_to_clipboard.default).toBe(CAPTURE_DEFAULTS.copy_to_clipboard);
    expect(capture.close_to_tray.default).toBe(CAPTURE_DEFAULTS.close_to_tray);
    // TA-4 (Session 30, MEU-67): new defaults.
    expect(capture.flatten_backup?.default).toBe(CAPTURE_DEFAULTS.flatten_backup);
    expect(capture.backup_dir?.default).toBe(CAPTURE_DEFAULTS.backup_dir);
    expect(capture.annotated_format?.default).toBe(CAPTURE_DEFAULTS.annotated_format);
  });

  it("AC-38.7 catalog envelope rejects processor; convert still requires processor", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const convertBare = vi.fn(async () => okJson([]));
    const convertRejected = await handleTool("avkit_convert", { action: "list" }, {
      env: toolEnv(appData),
      fetchImpl: convertBare as unknown as typeof fetch,
    });
    expect(convertRejected.isError).toBe(true);
    const convertOk = vi.fn(async () => okJson(listEnvelope([{ id: "c1" }])));
    const convertAccepted = await handleTool("avkit_convert", { action: "list" }, {
      env: toolEnv(appData),
      fetchImpl: convertOk as unknown as typeof fetch,
    });
    expect(convertAccepted.isError).not.toBe(true);
    const withProcessor = vi.fn(async () =>
      okJson({ items: [{ ...SHOT_ITEM, image_bytes: "nope" }], processor: { state: "Idle" } }),
    );
    const captureRejected = await handleTool("avkit_capture", { action: "list" }, {
      env: toolEnv(appData),
      fetchImpl: withProcessor as unknown as typeof fetch,
    });
    expect(captureRejected.isError).toBe(true);
    expect(captureRejected.content[0].text).toContain("invalid_catalog_envelope");
    const catalogOk = vi.fn(async () => okJson(catalogEnvelope([{ ...SHOT_ITEM, image_bytes: "nope" }])));
    const captureAccepted = await handleTool("avkit_capture", { action: "list" }, {
      env: toolEnv(appData),
      fetchImpl: catalogOk as unknown as typeof fetch,
    });
    expect(captureAccepted.isError).not.toBe(true);
    expect(captureAccepted.content[0].text).not.toContain("image_bytes");
    expect(captureAccepted.content[0].text).not.toContain("media_bytes");
    const parsed = JSON.parse(captureAccepted.content[0].text) as { items: unknown[]; processor?: unknown };
    expect(parsed).toEqual(expect.objectContaining({ items: expect.any(Array) }));
    expect(parsed).not.toHaveProperty("processor");
  });

  it("AC-38.8 capture uses ADD_TIMEOUT_MS and dist registers capture", () => {
    const registry = readFileSync(REGISTRY_TS, "utf8");
    expect(registry).toMatch(/avkit_capture/);
    expect(registry).toMatch(/ADD_TIMEOUT_MS/);
    expect(registry).toMatch(/tool === "avkit_capture"/);
    expect(existsSync(DIST_CAPTURE)).toBe(true);
  });

  it("AC-38.9 capture tool lives at toolsets/capture.ts not compound/", () => {
    expect(existsSync(CAPTURE_TS)).toBe(true);
    expect(existsSync(COMPOUND_DIR)).toBe(false);
  });

  it("AC-38.10 missing confirm is validation_error with fetch 0", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn();
    const result = await handleTool("avkit_capture", { action: "remove", id: "s1" }, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).toBe(true);
    expect(result.content[0].text).toContain("validation_error");
    expect(result.content[0].text).not.toContain("confirm_required");
    expect(result.content[0].text).not.toContain("unknown_tool");
    expect(fetchImpl).toHaveBeenCalledTimes(0);
  });

  it("AC-38.11 image returns MCP ImageContent; text PNG and oversize fail", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const okFetch = vi.fn(async () => imageResponse(PNG_BYTES));
    const result = await handleTool("avkit_capture", { action: "image", id: "s1" }, {
      env: toolEnv(appData),
      fetchImpl: okFetch as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    const item = result.content[0] as { type: string; data?: string; mimeType?: string; text?: string };
    expect(item.type).toBe("image");
    expect(item.data).toBe(Buffer.from(PNG_BYTES).toString("base64"));
    expect(item.mimeType).toBe("image/png");
    expect(item).not.toHaveProperty("text");
    const mislabeled = vi.fn(async () => imageResponse(PNG_BYTES, "image/jpeg"));
    const annotated = await handleTool("avkit_capture", {
      action: "image",
      id: "s1",
      variant: "annotated",
    }, {
      env: toolEnv(appData),
      fetchImpl: mislabeled as unknown as typeof fetch,
    });
    expect(annotated.isError).not.toBe(true);
    const annotatedItem = annotated.content[0] as { type: string; mimeType?: string };
    expect(annotatedItem.type).toBe("image");
    expect(annotatedItem.mimeType).toBe("image/png");
    const oversize = vi.fn(async () => imageResponse(new Uint8Array(IMAGE_MAX_BYTES + 1)));
    const tooBig = await handleTool("avkit_capture", { action: "image", id: "s1" }, {
      env: toolEnv(appData),
      fetchImpl: oversize as unknown as typeof fetch,
    });
    expect(tooBig.isError).toBe(true);
    expect(tooBig.content[0].type).toBe("text");
  });

  it("AC-38.12 GET image and list_requests append variant and status query", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const imageFetch = vi.fn(async () => imageResponse(PNG_BYTES));
    await handleTool("avkit_capture", { action: "image", id: "s1", variant: "annotated" }, {
      env: toolEnv(appData),
      fetchImpl: imageFetch as unknown as typeof fetch,
    });
    expect(imageFetch).toHaveBeenCalledTimes(1);
    expect(String(imageFetch.mock.calls[0]?.[0])).toContain("variant=annotated");
    const listFetch = vi.fn(async () => okJson(catalogEnvelope([])));
    await handleTool("avkit_capture", { action: "list_requests", status: "pending" }, {
      env: toolEnv(appData),
      fetchImpl: listFetch as unknown as typeof fetch,
    });
    expect(listFetch).toHaveBeenCalledTimes(1);
    expect(String(listFetch.mock.calls[0]?.[0])).toContain("status=pending");
  });

  it("AC-38.13 capture mode body forwards REST fields; list keys; extra fails", async () => {
    const { captureSchema } = await import("../src/toolsets/capture.js");
    const extra = captureSchema.safeParse({ action: "capture", mode: "fullscreen", nope: true });
    expect(extra.success).toBe(false);
    const register = captureSchema.safeParse({
      action: "capture",
      mode: "register",
      path: "C:/tmp/inbox/shot.png",
      source: "gui",
    });
    expect(register.success).toBe(false);
    const appData = tempAppData();
    temps.push(appData);
    const bodies: unknown[] = [];
    const fetchImpl = vi.fn(async (_url: string, init?: RequestInit) => {
      bodies.push(init?.body === undefined ? undefined : JSON.parse(String(init.body)));
      return okJson({ item: SHOT_ITEM }, 201);
    });
    const fullscreen = await handleTool(
      "avkit_capture",
      { action: "capture", mode: "fullscreen" },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(fullscreen.isError).not.toBe(true);
    expect(bodies[0]).toEqual({ mode: "fullscreen" });
    const region = await handleTool(
      "avkit_capture",
      { action: "capture", mode: "region", x: 0, y: 0, width: 32, height: 32 },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(region.isError).not.toBe(true);
    expect(bodies[1]).toEqual({ mode: "region", x: 0, y: 0, width: 32, height: 32 });
    const listFetch = vi.fn(async () => okJson(catalogEnvelope([SHOT_ITEM])));
    const listed = await handleTool("avkit_capture", { action: "list" }, {
      env: toolEnv(appData),
      fetchImpl: listFetch as unknown as typeof fetch,
    });
    expect(listed.isError).not.toBe(true);
    const parsed = JSON.parse(listed.content[0].text) as { items: Array<Record<string, unknown>> };
    expect(Object.keys(parsed.items[0] ?? {})).toEqual(expect.arrayContaining([...SHOT_OUT_FIELDS]));
  });

  it("AC-59.16 annotate stays the same DTO with one arrow+text example and no new action", async () => {
    const { captureDescriptions, captureSchema } = await import("../src/toolsets/capture.js");
    const annotate = captureDescriptions["avkit_capture.annotate"];
    expect(annotate).toContain('"type": "arrow"');
    expect(annotate).toContain('"type": "text"');
    expect(annotate.toLowerCase()).not.toMatch(/\bcircle\b/);
    expect(annotate.toLowerCase()).not.toMatch(/\bmarker\b/);
    expect(ACTION_INDEX.some((row) => row.tool === "avkit_capture" && row.action === "suggest")).toBe(
      false,
    );
    const suggest = captureSchema.safeParse({ action: "suggest", id: "s1" });
    expect(suggest.success).toBe(false);
    const example = captureSchema.safeParse({
      action: "annotate",
      id: "s1",
      annotations: [
        { type: "arrow", from: [10, 10], to: [80, 40], color: "red", stroke_width: 3 },
        { type: "text", x: 12, y: 48, text: "Note", color: "white", font_size: 16 },
      ],
    });
    expect(example.success).toBe(true);
  });
});

const MEU67_ACTIONS = [
  { action: "flatten", method: "POST", path: "/captures/{id}/flatten" },
  { action: "revert", method: "POST", path: "/captures/{id}/revert" },
] as const;

describe("MEU-67 avkit_capture flatten and revert", () => {
  it.each(MEU67_ACTIONS)("AC-67.16 $action refuses missing, false and extra-key confirm with zero fetches", async (row) => {
    const appData = tempAppData();
    temps.push(appData);
    const confirmWithUser = vi.fn(async () => "accept" as const);
    const refused = [
      { action: row.action, id: "s1" },
      { action: row.action, id: "s1", confirm: false },
      { action: row.action, id: "s1", confirm: true, extra: 1 },
    ];
    for (const args of refused) {
      const fetchImpl = vi.fn();
      const result = await handleTool("avkit_capture", args, {
        env: toolEnv(appData),
        fetchImpl: fetchImpl as unknown as typeof fetch,
        confirmWithUser,
      });
      expect(result.isError, JSON.stringify(args)).toBe(true);
      expect(result.content[0].text).toContain("validation_error");
      expect(fetchImpl).toHaveBeenCalledTimes(0);
    }
    expect(confirmWithUser).toHaveBeenCalledTimes(0);
  });

  it.each(MEU67_ACTIONS)("AC-67.16 $action with confirm and an accepting user POSTs {} once", async (row) => {
    const appData = tempAppData();
    temps.push(appData);
    const detail = { ...SHOT_ITEM, annotations: [], backup_path: null };
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      calls.push({
        url: String(url),
        method: init?.method,
        body: init?.body === undefined ? undefined : JSON.parse(String(init.body)),
      });
      return okJson(detail);
    });
    const result = await handleTool("avkit_capture", { action: row.action, id: "s1", confirm: true }, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
      confirmWithUser: async () => "accept",
    });
    expect(result.isError).not.toBe(true);
    expect(calls).toHaveLength(1);
    expect(calls[0]?.method).toBe("POST");
    expect(calls[0]?.url.endsWith(row.path.replace("{id}", "s1"))).toBe(true);
    expect(calls[0]?.body).toEqual({});
    expect(JSON.parse(result.content[0].text)).toEqual(detail);
  });

  it("AC-67.17 MCP_ACTIONS follow remove; destructive; M7 descriptions; settings keys and Zod", async () => {
    const { captureDescriptions } = await import("../src/toolsets/capture.js");
    const keys = ACTION_INDEX.map((row) => `${row.tool}.${row.action}`);
    const at = keys.indexOf("avkit_capture.remove");
    expect(at).toBeGreaterThanOrEqual(0);
    expect(keys.slice(at + 1, at + 3)).toEqual(["avkit_capture.flatten", "avkit_capture.revert"]);
    for (const row of MEU67_ACTIONS) {
      const found = ACTION_INDEX.find((r) => r.tool === "avkit_capture" && r.action === row.action);
      expect(found && { method: found.method, path: found.path }).toEqual({ method: row.method, path: row.path });
      expect(DESTRUCTIVE_ACTIONS.has(`avkit_capture.${row.action}`)).toBe(true);
      const text = captureDescriptions[`avkit_capture.${row.action}`] ?? "";
      const hits = M7.filter((marker) => text.toLowerCase().includes(marker.toLowerCase()));
      expect(hits.length, row.action).toBeGreaterThanOrEqual(3);
    }
    const capture = SETTINGS_SCHEMA.namespaces.capture;
    expect(capture.flatten_backup).toEqual(expect.objectContaining({ type: "boolean", default: true }));
    expect(capture.backup_dir).toEqual(expect.objectContaining({ type: "string", default: "" }));
    expect(capture.annotated_format).toEqual(expect.objectContaining({ type: "string", default: "png" }));
    const set = (extra: Record<string, unknown>) =>
      settingsSchema.safeParse({ action: "set", namespace: "capture", ...extra }).success;
    expect(set({ flatten_backup: false, backup_dir: "C:/tmp/backups", annotated_format: "webp" })).toBe(true);
    expect(set({ annotated_format: "jpeg" })).toBe(true);
    expect(set({ flatten_backup: "yes" })).toBe(false);
    expect(set({ annotated_format: "gif" })).toBe(false);
    expect(set({ annotated_format: "jpg" })).toBe(false);
  });

  it("AC-67.18 INSTRUCTION_TEXT names the capture file effects and the user confirmation", () => {
    expect(SERVER_INSTRUCTIONS).not.toContain("Files on disk are not deleted");
    expect(SERVER_INSTRUCTIONS).toContain("Destructive actions require confirm: true.");
    expect(SERVER_INSTRUCTIONS).toContain("Download, transcript and convert remove/clear keep files on disk.");
    expect(SERVER_INSTRUCTIONS).toContain("Capture remove deletes the shot's files");
    expect(SERVER_INSTRUCTIONS).toContain("capture flatten overwrites the image file");
    expect(SERVER_INSTRUCTIONS).toContain("capture revert overwrites it from its newest backup");
    expect(SERVER_INSTRUCTIONS).toContain(
      "These three capture actions also ask the user in the IDE and are refused unless the user accepts",
    );
    expect(SERVER_INSTRUCTIONS).toContain("Never upload or write to YouTube");
  });
});

type BlockBounds = { minimum: number; maximum: number; default: number };

describe("MEU-90 avkit_capture pixelate", () => {
  it("AC-90.4 annotate accepts a pixelate with and without block_size and forwards it unchanged", async () => {
    const { captureSchema } = await import("../src/toolsets/capture.js");
    const sized = { type: "pixelate", x: 2, y: 3, width: 20, height: 10, block_size: 7 };
    const unsized = { type: "pixelate", x: 30, y: 4, width: 12, height: 9 };
    const body = { action: "annotate", id: "s1", annotations: [sized, unsized] };
    expect(captureSchema.safeParse(body).success).toBe(true);
    for (const bad of [{ ...sized, block_size: 1 }, { ...sized, color: "red" }]) {
      const refused = captureSchema.safeParse({ ...body, annotations: [bad] });
      expect(refused.success, JSON.stringify(bad)).toBe(false);
    }

    // PIXELATE_BLOCK parity: the bounds come from PixelateAnnotationIn in the committed OpenAPI.
    const committed = JSON.parse(readFileSync(OPENAPI_COMMITTED, "utf8")) as {
      components: { schemas: Record<string, { properties: Record<string, BlockBounds> }> };
    };
    const block = committed.components.schemas.PixelateAnnotationIn?.properties.block_size;
    expect(block).toBeDefined();
    const { minimum, maximum } = block as BlockBounds;
    expect([minimum, maximum, (block as BlockBounds).default]).toEqual([2, 100, 10]);
    const accepts = (value: number): boolean =>
      captureSchema.safeParse({ ...body, annotations: [{ ...sized, block_size: value }] }).success;
    expect([minimum - 1, minimum, maximum, maximum + 1].map(accepts)).toEqual([false, true, true, false]);

    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      calls.push({
        url: String(url),
        method: init?.method,
        body: init?.body === undefined ? undefined : JSON.parse(String(init.body)),
      });
      return okJson(SHOT_ITEM);
    });
    const result = await handleTool("avkit_capture", body, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    expect(calls).toHaveLength(1);
    expect(calls[0]?.method).toBe("POST");
    expect(calls[0]?.url.endsWith("/captures/s1/annotate")).toBe(true);
    expect(calls[0]?.body).toEqual({ annotations: [sized, unsized] });
  });
});

describe("MEU-91 avkit_capture eraser", () => {
  it("AC-91.4 annotate accepts an eraser (a rectangle only) and forwards it unchanged", async () => {
    const { captureSchema } = await import("../src/toolsets/capture.js");
    const eraser = { type: "eraser", x: 2, y: 3, width: 20, height: 10 };
    const body = { action: "annotate", id: "s1", annotations: [eraser] };
    expect(captureSchema.safeParse(body).success).toBe(true);
    // Negative: REGION_DTO gives an eraser no color and no block.
    for (const bad of [{ ...eraser, color: "red" }, { ...eraser, block_size: 10 }]) {
      const refused = captureSchema.safeParse({ ...body, annotations: [bad] });
      expect(refused.success, JSON.stringify(bad)).toBe(false);
    }

    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      calls.push({
        url: String(url),
        method: init?.method,
        body: init?.body === undefined ? undefined : JSON.parse(String(init.body)),
      });
      return okJson(SHOT_ITEM);
    });
    const result = await handleTool("avkit_capture", body, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    expect(calls).toHaveLength(1);
    expect(calls[0]?.method).toBe("POST");
    expect(calls[0]?.url.endsWith("/captures/s1/annotate")).toBe(true);
    expect(calls[0]?.body).toEqual({ annotations: [eraser] });
  });
});

// MEU-128 capture-region-view (Session 58): QUERY_GET_ONLY, FRAME_ITEM and OVERSIZE_HINT.
const FRAME_HEADER_VALUES = {
  "X-Capture-Source": "2000,1500",
  "X-Capture-Region": "100,200,800,600",
  "X-Capture-Returned": "1568,1176",
  "X-Capture-Scale": "1.960000",
  "X-Capture-Clamped": "false",
} as const;
const OVERSIZE_TODAY =
  `image exceeds the ${IMAGE_MAX_BYTES} B MCP limit; read original_path or annotated_path from avkit_capture get and open that file`;

function framedResponse(headers: Record<string, string>): Response {
  return new Response(PNG_BYTES, {
    status: 200,
    headers: { "Content-Type": "image/png", ...headers },
  });
}

describe("MEU-128 image region", () => {
  it("AC-128.18 image sends the region fields as query keys", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string }[] = [];
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      calls.push({ url: String(url), method: init?.method });
      return imageResponse(PNG_BYTES);
    });
    const result = await handleTool("avkit_capture", {
      action: "image",
      id: "s1",
      x: 0.25,
      y: 0.5,
      width: 0.25,
      height: 0.125,
      unit: "fraction",
      max_edge: 2576,
    }, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    expect(calls).toHaveLength(1);
    expect(calls[0]?.method).toBe("GET");
    const url = new URL(calls[0]?.url ?? "");
    expect(url.pathname.endsWith("/captures/s1/image")).toBe(true);
    expect(Object.fromEntries(url.searchParams)).toEqual({
      x: "0.25",
      y: "0.5",
      width: "0.25",
      height: "0.125",
      unit: "fraction",
      max_edge: "2576",
    });
  });

  it("AC-128.19 capture region sends no query string", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      calls.push({
        url: String(url),
        method: init?.method,
        body: init?.body === undefined ? undefined : JSON.parse(String(init.body)),
      });
      return okJson({ item: SHOT_ITEM }, 201);
    });
    const result = await handleTool(
      "avkit_capture",
      { action: "capture", mode: "region", x: 10, y: 20, width: 32, height: 40 },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(result.isError).not.toBe(true);
    expect(calls).toHaveLength(1);
    expect(calls[0]?.method).toBe("POST");
    expect(calls[0]?.url).not.toContain("?");
    expect(calls[0]?.url.endsWith("/captures")).toBe(true);
    expect(calls[0]?.body).toEqual({ mode: "region", x: 10, y: 20, width: 32, height: 40 });
  });

  it("AC-128.20 image returns the frame item before the image", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const framed = vi.fn(async () => framedResponse({ ...FRAME_HEADER_VALUES }));
    const result = await handleTool("avkit_capture", { action: "image", id: "s1" }, {
      env: toolEnv(appData),
      fetchImpl: framed as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    expect(result.content.map((item) => item.type)).toEqual(["text", "image"]);
    const text = (result.content[0] as { text: string }).text;
    const parsed = JSON.parse(text) as { frame: unknown; map: string };
    expect(parsed.frame).toEqual({
      source: { width: 2000, height: 1500 },
      region: { x: 100, y: 200, width: 800, height: 600 },
      returned: { width: 1568, height: 1176 },
      scale: 1.96,
      clamped: false,
    });
    expect(parsed.map).toContain("source_x = region.x + x / scale");
    expect(parsed.map).toContain("source_y = region.y + y / scale");
    const image = result.content[1] as { type: string; data?: string; mimeType?: string };
    expect(image.data).toBe(Buffer.from(PNG_BYTES).toString("base64"));
    expect(image.mimeType).toBe("image/png");

    const { "X-Capture-Scale": _scale, ...partial } = FRAME_HEADER_VALUES;
    const unframed = vi.fn(async () => framedResponse(partial));
    const alone = await handleTool("avkit_capture", { action: "image", id: "s1" }, {
      env: toolEnv(appData),
      fetchImpl: unframed as unknown as typeof fetch,
    });
    expect(alone.isError).not.toBe(true);
    expect(alone.content.map((item) => item.type)).toEqual(["image"]);
  });

  it("AC-128.22 an oversize image names max_edge", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const oversize = vi.fn(async () => imageResponse(new Uint8Array(IMAGE_MAX_BYTES + 1)));
    const result = await handleTool("avkit_capture", { action: "image", id: "s1" }, {
      env: toolEnv(appData),
      fetchImpl: oversize as unknown as typeof fetch,
    });
    expect(result.isError).toBe(true);
    const text = result.content[0].text;
    expect(text).toContain("payload_too_large");
    expect(text).toContain(OVERSIZE_TODAY);
    expect(text).toContain("max_edge (64 to 2576)");
  });

  it("AC-128.23 image region fields are bounded", async () => {
    const { captureSchema } = await import("../src/toolsets/capture.js");
    const base = { action: "image", id: "s1" } as const;
    const region = { x: 0.25, y: 0, width: 0.5, height: 0.5 };
    expect(captureSchema.safeParse({ ...base, ...region, unit: "fraction" }).success).toBe(true);
    expect(captureSchema.safeParse({ ...base, ...region, max_edge: 64 }).success).toBe(true);
    for (const bad of [
      { ...region, x: -1 },
      { ...region, width: 0 },
      { ...region, unit: "inch" },
      { max_edge: 63 },
      { max_edge: 2577 },
      { max_edge: 100.5 },
    ]) {
      expect(captureSchema.safeParse({ ...base, ...bad }).success, JSON.stringify(bad)).toBe(false);
    }
  });

  it("AC-128.24 image describes the region and the frame", async () => {
    const { captureDescriptions } = await import("../src/toolsets/capture.js");
    const { advertisedSchema } = await import("../src/toolsets/registry.js");
    const text = captureDescriptions["avkit_capture.image"] ?? "";
    for (const needle of ["max_edge", "2576", "fraction", "region.x + x / scale"]) {
      expect(text, needle).toContain(needle);
    }
    expect(M7.filter((marker) => text.includes(marker)).length).toBeGreaterThanOrEqual(3);
    const keys = Object.keys(advertisedSchema("avkit_capture").shape);
    expect(keys).toEqual(expect.arrayContaining(["x", "y", "width", "height", "unit", "max_edge"]));
  });
});

// MEU-129 capture-image-import (Session 58): IMPORT_MODE over MCP (D-415, design §6.7).
describe("MEU-129 capture import", () => {
  it("AC-129.12 capture import sends mode and path", async () => {
    const { ADD_TIMEOUT_MS } = await import("../src/client.js");
    const { captureSchema } = await import("../src/toolsets/capture.js");
    const source = "C:/elsewhere/shot.png";
    expect(
      captureSchema.safeParse({ action: "capture", mode: "import", path: source }).success,
    ).toBe(true);
    expect(
      captureSchema.safeParse({ action: "capture", mode: "import", path: source, nope: 1 }).success,
    ).toBe(false);
    expect(captureSchema.safeParse({ action: "capture", mode: "import" }).success).toBe(false);
    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      calls.push({
        url: String(url),
        method: init?.method,
        body: init?.body === undefined ? undefined : JSON.parse(String(init.body)),
      });
      return okJson({ item: { ...SHOT_ITEM, source: "Import" } }, 201);
    });
    const timeout = vi.spyOn(AbortSignal, "timeout");
    try {
      const result = await handleTool(
        "avkit_capture",
        { action: "capture", mode: "import", path: source },
        { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
      );
      expect(result.isError).not.toBe(true);
      expect(calls).toHaveLength(1);
      expect(calls[0]?.method).toBe("POST");
      expect(calls[0]?.url).not.toContain("?");
      expect(calls[0]?.url.endsWith("/captures")).toBe(true);
      expect(calls[0]?.body).toEqual({ mode: "import", path: source });
      expect(timeout).toHaveBeenCalledWith(ADD_TIMEOUT_MS);
    } finally {
      timeout.mockRestore();
    }
  });

  it("AC-129.13 capture describes import", async () => {
    const { captureDescriptions } = await import("../src/toolsets/capture.js");
    const { advertisedSchema } = await import("../src/toolsets/registry.js");
    const text = captureDescriptions["avkit_capture.capture"] ?? "";
    expect(text).toContain("mode=import");
    expect(text).toContain("never changed");
    const shape = advertisedSchema("avkit_capture").shape as Record<
      string,
      { safeParse(value: unknown): { success: boolean } }
    >;
    expect(Object.keys(shape)).toEqual(expect.arrayContaining(["mode", "path"]));
    expect(shape.mode?.safeParse("import").success).toBe(true);
    expect(shape.mode?.safeParse("fullscreen").success).toBe(true);
  });
});

// MEU-130 capture-crop-copy (Session 59): CROP_MCP (D-492, D-494).
describe("MEU-130 capture crop", () => {
  it("AC-130.23 crop sends the box as the POST body", async () => {
    const { ADD_TIMEOUT_MS } = await import("../src/client.js");
    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      calls.push({
        url: String(url),
        method: init?.method,
        body: init?.body === undefined ? undefined : JSON.parse(String(init.body)),
      });
      return okJson({ item: { ...SHOT_ITEM, id: "c1", source: "Crop" }, source_id: "s1" }, 201);
    });
    const timeout = vi.spyOn(AbortSignal, "timeout");
    try {
      const result = await handleTool(
        "avkit_capture",
        {
          action: "crop",
          id: "s1",
          x: 0.25,
          y: 0.5,
          width: 0.5,
          height: 0.25,
          unit: "fraction",
          name: "detail",
        },
        { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
      );
      expect(calls).toHaveLength(1);
      expect(result.isError).not.toBe(true);
      expect(calls[0]?.method).toBe("POST");
      expect(calls[0]?.url).not.toContain("?");
      expect(calls[0]?.url.endsWith("/captures/s1/crop")).toBe(true);
      expect(calls[0]?.body).toEqual({
        x: 0.25,
        y: 0.5,
        width: 0.5,
        height: 0.25,
        unit: "fraction",
        name: "detail",
      });
      expect(timeout).toHaveBeenCalledWith(ADD_TIMEOUT_MS);
    } finally {
      timeout.mockRestore();
    }
  });

  it("AC-130.24 crop fields are bounded", async () => {
    const { captureSchema } = await import("../src/toolsets/capture.js");
    const base: Record<string, unknown> = {
      action: "crop",
      id: "s1",
      x: 0.25,
      y: 0,
      width: 0.5,
      height: 1,
      unit: "fraction",
      name: "detail",
    };
    expect(captureSchema.safeParse(base).success).toBe(true);
    expect(
      captureSchema.safeParse({ action: "crop", id: "s1", x: 0, y: 0, width: 8, height: 8 }).success,
    ).toBe(true);
    expect(captureSchema.safeParse({ ...base, name: "a".repeat(80) }).success).toBe(true);
    for (const bad of [
      { x: -1 },
      { width: 0 },
      { unit: "inch" },
      { name: "" },
      { name: "a".repeat(81) },
      { nope: 1 },
    ]) {
      expect(captureSchema.safeParse({ ...base, ...bad }).success, JSON.stringify(bad)).toBe(false);
    }
    for (const key of ["id", "x", "y", "width", "height"]) {
      const partial = { ...base };
      delete partial[key];
      expect(captureSchema.safeParse(partial).success, `without ${key}`).toBe(false);
    }
  });

  it("AC-130.25 crop describes a new shot", async () => {
    const { captureDescriptions } = await import("../src/toolsets/capture.js");
    const { advertisedSchema } = await import("../src/toolsets/registry.js");
    const { USER_CONFIRM_ACTIONS } = await import("../src/destructive.js");
    const raw: unknown = captureDescriptions["avkit_capture.crop"];
    expect(typeof raw).toBe("string");
    const text = String(raw);
    for (const needle of ["NEW shot", "never changed", "applied", "clipped", "-crop WxH+X+Y +repage"]) {
      expect(text, needle).toContain(needle);
    }
    expect(M7.filter((marker) => text.includes(marker)).length).toBeGreaterThanOrEqual(3);
    const keys = Object.keys(advertisedSchema("avkit_capture").shape);
    expect(keys).toEqual(expect.arrayContaining(["x", "y", "width", "height", "unit", "name"]));
    expect(DESTRUCTIVE_ACTIONS.has("avkit_capture.crop")).toBe(false);
    expect(USER_CONFIRM_ACTIONS.has("avkit_capture.crop")).toBe(false);
  });

  it("AC-130.26 ACTION_INDEX has the crop row after revert", () => {
    // MEU-134 (Session 62): +avkit_capture.frames after crop.
    // MEU-135 (Session 63): +avkit_capture.sheet after frames.
    expect(ACTION_INDEX).toHaveLength(74);
    const keys = ACTION_INDEX.map((row) => `${row.tool}.${row.action}`);
    const revert = keys.indexOf("avkit_capture.revert");
    expect(revert).toBeGreaterThan(-1);
    expect(keys[revert + 1]).toBe("avkit_capture.crop");
    expect(ACTION_INDEX[revert + 1]).toEqual({
      tool: "avkit_capture",
      action: "crop",
      method: "POST",
      path: "/captures/{id}/crop",
    });
    expect(keys[keys.length - 1]).toBe("avkit_models.download_asset");
    expect(ACTION_INDEX.filter((row) => row.tool === "avkit_capture")).toHaveLength(13);
  });
});

// MEU-134 capture-video-frames (Session 62): FRAMES_MCP.
const FRAMES_PATH = "C:\\videos\\clip.mp4";
const FRAMES_BODY = {
  video: { path: FRAMES_PATH, duration_ms: 3000, width: 320, height: 240, fps: 25 },
  frames: [
    {
      id: "f1",
      path: "C:/tmp/inbox/clip-t00h00m00.500s.png",
      time_ms: 500,
      timecode: "00:00:00.500",
      width: 320,
      height: 240,
    },
    {
      id: "f2",
      path: "C:/tmp/inbox/clip-t00h00m01.500s.png",
      time_ms: 1500,
      timecode: "00:00:01.500",
      width: 320,
      height: 240,
    },
  ],
};
const FRAMES_TEXT_MARKERS = [
  // D-605 (Session 63, MEU-135): the workflow line names sheet between probe and frames.
  "Workflow: call avkit_convert probe for the duration, then avkit_capture sheet to find the moment, then frames to POST /captures/frames for exact stills, then image to view a frame.",
  "Prerequisite: a local absolute video path and FFmpeg; the video is read in place, never changed or uploaded.",
  "Returns: JSON with the video's duration and size and each new shot's id, path, time_ms and timecode; no image bytes.",
  "Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.",
] as const;

function framesFetch(calls: { url: string; method?: string; body: unknown }[]) {
  return vi.fn(async (url: string, init?: RequestInit) => {
    calls.push({
      url: String(url),
      method: init?.method,
      body: init?.body === undefined ? undefined : JSON.parse(String(init.body)),
    });
    return okJson(FRAMES_BODY, 201);
  });
}

describe("MEU-134 capture frames", () => {
  it("AC-134.15 frames accepts the at and count shapes and refuses the rest before fetch", async () => {
    const { captureSchema } = await import("../src/toolsets/capture.js");
    const good: Record<string, unknown>[] = [
      { action: "frames", path: FRAMES_PATH, at: [0, 1.5, "00:00:02.250"] },
      { action: "frames", path: FRAMES_PATH, at: Array.from({ length: 20 }, (_v, i) => i) },
      { action: "frames", path: FRAMES_PATH, count: 3 },
      { action: "frames", path: FRAMES_PATH, count: 20, start: 1, end: "2.5" },
      { action: "frames", path: FRAMES_PATH, at: ["1".repeat(32)] },
    ];
    for (const args of good) {
      expect(captureSchema.safeParse(args).success, JSON.stringify(args)).toBe(true);
    }
    const bad: Record<string, unknown>[] = [
      { action: "frames", path: FRAMES_PATH, at: [1], count: 2 },
      { action: "frames", path: FRAMES_PATH },
      { action: "frames", path: FRAMES_PATH, at: [1], start: 0 },
      { action: "frames", path: FRAMES_PATH, at: [1], end: 2 },
      { action: "frames", path: FRAMES_PATH, at: Array.from({ length: 21 }, (_v, i) => i) },
      { action: "frames", path: FRAMES_PATH, at: [] },
      { action: "frames", path: FRAMES_PATH, count: 21 },
      { action: "frames", path: FRAMES_PATH, count: 0 },
      { action: "frames", path: FRAMES_PATH, count: 1.5 },
      { action: "frames", path: FRAMES_PATH, at: [-1] },
      { action: "frames", path: FRAMES_PATH, count: 2, start: -1 },
      { action: "frames", path: FRAMES_PATH, at: ["1".repeat(33)] },
      { action: "frames", path: FRAMES_PATH, at: [""] },
      { action: "frames", path: FRAMES_PATH, count: 2, start: null },
      { action: "frames", path: FRAMES_PATH, count: 2, nope: 1 },
      { action: "frames", path: "", count: 2 },
      { action: "frames", path: "a".repeat(4097), count: 2 },
    ];
    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = framesFetch(calls);
    for (const args of bad) {
      expect(captureSchema.safeParse(args).success, JSON.stringify(args).slice(0, 120)).toBe(false);
      const result = await handleTool("avkit_capture", args, {
        env: toolEnv(appData),
        fetchImpl: fetchImpl as unknown as typeof fetch,
      });
      expect(result.isError, JSON.stringify(args).slice(0, 120)).toBe(true);
    }
    expect(fetchImpl).toHaveBeenCalledTimes(0);
  });

  it("AC-134.15 frames posts the body minus action with ADD_TIMEOUT_MS (D-577 A)", async () => {
    const { ADD_TIMEOUT_MS } = await import("../src/client.js");
    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = framesFetch(calls);
    const timeout = vi.spyOn(AbortSignal, "timeout");
    try {
      const result = await handleTool(
        "avkit_capture",
        { action: "frames", path: FRAMES_PATH, count: 2, start: 0, end: "3" },
        { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
      );
      expect(calls).toHaveLength(1);
      expect(result.isError).not.toBe(true);
      expect(calls[0]?.method).toBe("POST");
      expect(calls[0]?.url).not.toContain("?");
      expect(calls[0]?.url.endsWith("/captures/frames")).toBe(true);
      expect(calls[0]?.body).toEqual({ path: FRAMES_PATH, count: 2, start: 0, end: "3" });
      expect(timeout).toHaveBeenCalledWith(ADD_TIMEOUT_MS);
      calls.length = 0;
      await handleTool(
        "avkit_capture",
        { action: "frames", path: FRAMES_PATH, at: [0.5, "00:00:01.500"] },
        { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
      );
      expect(calls[0]?.body).toEqual({ path: FRAMES_PATH, at: [0.5, "00:00:01.500"] });
    } finally {
      timeout.mockRestore();
    }
  });

  it("AC-134.15 frames has its own four markers, says at or after and names avkit_convert probe", async () => {
    const { captureDescriptions } = await import("../src/toolsets/capture.js");
    const text = captureDescriptions["avkit_capture.frames"] ?? "";
    expect(text.length).toBeGreaterThan(0);
    for (const line of FRAMES_TEXT_MARKERS) {
      expect(text, line).toContain(line);
    }
    expect(text).not.toContain("Prerequisite: local screen grab or inbox files");
    expect(text).toContain("at or after");
    expect(text).toContain("avkit_convert probe");
    expect(text).toContain("Give at (1-20 times");
    expect(text).toContain("A raw stream with no duration takes only at");
    expect(M7.filter((marker) => text.includes(marker))).toEqual([...M7]);
    expect(DESTRUCTIVE_ACTIONS.has("avkit_capture.frames")).toBe(false);
  });

  it("AC-134.16 ACTION_INDEX has the frames row after crop", () => {
    const keys = ACTION_INDEX.map((row) => `${row.tool}.${row.action}`);
    const crop = keys.indexOf("avkit_capture.crop");
    expect(crop).toBeGreaterThan(-1);
    expect(keys[crop + 1]).toBe("avkit_capture.frames");
    expect(ACTION_INDEX[crop + 1]).toEqual({
      tool: "avkit_capture",
      action: "frames",
      method: "POST",
      path: "/captures/frames",
    });
    // MEU-135 (Session 63): +avkit_capture.sheet after frames.
    expect(ACTION_INDEX).toHaveLength(74);
    expect(keys[keys.length - 1]).toBe("avkit_models.download_asset");
  });

  it("AC-134.16 transport parity: the fake backend's 201 body reaches the tool result", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = framesFetch(calls);
    const result = await handleTool(
      "avkit_capture",
      { action: "frames", path: FRAMES_PATH, at: [0.5, 1.5] },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(calls).toHaveLength(1);
    expect(result.isError).not.toBe(true);
    const parsed = JSON.parse(result.content[0].text) as typeof FRAMES_BODY;
    expect(Object.keys(parsed).sort()).toEqual(["frames", "video"]);
    expect(Object.keys(parsed.video).sort()).toEqual(Object.keys(FRAMES_BODY.video).sort());
    expect(parsed.frames.map((f) => Object.keys(f).sort())).toEqual(
      FRAMES_BODY.frames.map((f) => Object.keys(f).sort()),
    );
    expect(parsed).toEqual(FRAMES_BODY);
  });
});

// MEU-135 capture-video-sheet (Session 63): SHEET_MCP.
const SHEET_PATH = "C:\\videos\\clip.mp4";
const SHEET_BODY = {
  video: { path: SHEET_PATH, duration_ms: 3000, width: 320, height: 240, fps: 25 },
  shot: {
    id: "sh1",
    path: "C:/tmp/inbox/clip-sheet-00h00m00s-00h00m03s.png",
    width: 1250,
    height: 938,
  },
  spacing_ms: 750,
  cells: [
    { cell: 1, time_ms: 375, timecode: "00:00:00.375" },
    { cell: 2, time_ms: 1125, timecode: "00:00:01.125" },
    { cell: 3, time_ms: 1875, timecode: "00:00:01.875" },
    { cell: 4, time_ms: 2625, timecode: "00:00:02.625" },
  ],
};
const SHEET_TEXT_MARKERS = [
  "Workflow: call avkit_convert probe for the duration, then avkit_capture sheet to POST /captures/sheet for a grid over a span, then frames for exact stills, then image to view the sheet.",
  "Prerequisite: a local absolute video path and FFmpeg; the video is read in place, never changed or uploaded.",
  "Returns: JSON with the video's duration and size, the new shot's id, path and size, spacing_ms and each cell's number, time_ms and timecode; no image bytes.",
  "Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.",
] as const;
// D-605: FRAMES_TEXT's workflow line names sheet between probe and frames.
const FRAMES_WORKFLOW_WITH_SHEET =
  "Workflow: call avkit_convert probe for the duration, then avkit_capture sheet to find the moment, then frames to POST /captures/frames for exact stills, then image to view a frame.";

function sheetFetch(calls: { url: string; method?: string; body: unknown }[]) {
  return vi.fn(async (url: string, init?: RequestInit) => {
    calls.push({
      url: String(url),
      method: init?.method,
      body: init?.body === undefined ? undefined : JSON.parse(String(init.body)),
    });
    return okJson(SHEET_BODY, 201);
  });
}

describe("MEU-135 capture sheet", () => {
  it("AC-135.18 capture sheet schema, call and description: the schema takes path and every optional key", async () => {
    const { captureSchema } = await import("../src/toolsets/capture.js");
    const good: Record<string, unknown>[] = [
      { action: "sheet", path: SHEET_PATH },
      { action: "sheet", path: SHEET_PATH, start: 1, end: "2.5", grid: 2, max_edge: 64 },
      { action: "sheet", path: SHEET_PATH, grid: 5, max_edge: 2576 },
      { action: "sheet", path: SHEET_PATH, start: "00:00:01.000", end: "1".repeat(32) },
      { action: "sheet", path: SHEET_PATH, start: 0 },
      { action: "sheet", path: "a".repeat(4096) },
    ];
    for (const args of good) {
      expect(captureSchema.safeParse(args).success, JSON.stringify(args).slice(0, 120)).toBe(true);
    }
  });

  it("AC-135.18 capture sheet schema, call and description: refusals come before fetch", async () => {
    const { captureSchema } = await import("../src/toolsets/capture.js");
    const bad: Record<string, unknown>[] = [
      { action: "sheet", path: SHEET_PATH, nope: 1 },
      { action: "sheet", path: "" },
      { action: "sheet", path: "a".repeat(4097) },
      { action: "sheet" },
      { action: "sheet", path: SHEET_PATH, grid: 1 },
      { action: "sheet", path: SHEET_PATH, grid: 6 },
      { action: "sheet", path: SHEET_PATH, grid: 2.5 },
      { action: "sheet", path: SHEET_PATH, grid: "3" },
      { action: "sheet", path: SHEET_PATH, grid: null },
      { action: "sheet", path: SHEET_PATH, max_edge: 63 },
      { action: "sheet", path: SHEET_PATH, max_edge: 2577 },
      { action: "sheet", path: SHEET_PATH, max_edge: 100.5 },
      { action: "sheet", path: SHEET_PATH, max_edge: null },
      { action: "sheet", path: SHEET_PATH, start: -1 },
      { action: "sheet", path: SHEET_PATH, end: -1 },
      { action: "sheet", path: SHEET_PATH, start: "1".repeat(33) },
      { action: "sheet", path: SHEET_PATH, end: "" },
      { action: "sheet", path: SHEET_PATH, start: null },
      { action: "sheet", path: SHEET_PATH, at: [1] },
      { action: "sheet", path: SHEET_PATH, count: 4 },
    ];
    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = sheetFetch(calls);
    for (const args of bad) {
      expect(captureSchema.safeParse(args).success, JSON.stringify(args).slice(0, 120)).toBe(false);
      const result = await handleTool("avkit_capture", args, {
        env: toolEnv(appData),
        fetchImpl: fetchImpl as unknown as typeof fetch,
      });
      expect(result.isError, JSON.stringify(args).slice(0, 120)).toBe(true);
    }
    expect(fetchImpl).toHaveBeenCalledTimes(0);
    expect(calls).toEqual([]);
  });

  it("AC-135.18 capture sheet schema, call and description: it posts the body minus action with ADD_TIMEOUT_MS (D-601 A)", async () => {
    const { ADD_TIMEOUT_MS } = await import("../src/client.js");
    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = sheetFetch(calls);
    const timeout = vi.spyOn(AbortSignal, "timeout");
    try {
      const result = await handleTool(
        "avkit_capture",
        { action: "sheet", path: SHEET_PATH, start: 0, end: "3", grid: 2, max_edge: 1568 },
        { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
      );
      expect(calls).toHaveLength(1);
      expect(result.isError).not.toBe(true);
      expect(calls[0]?.method).toBe("POST");
      expect(calls[0]?.url).not.toContain("?");
      expect(calls[0]?.url.endsWith("/captures/sheet")).toBe(true);
      expect(calls[0]?.body).toEqual({ path: SHEET_PATH, start: 0, end: "3", grid: 2, max_edge: 1568 });
      expect(timeout).toHaveBeenCalledWith(ADD_TIMEOUT_MS);
      calls.length = 0;
      timeout.mockClear();
      await handleTool(
        "avkit_capture",
        { action: "sheet", path: SHEET_PATH },
        { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
      );
      expect(calls).toHaveLength(1);
      expect(calls[0]?.body).toEqual({ path: SHEET_PATH });
      expect(timeout).toHaveBeenCalledWith(ADD_TIMEOUT_MS);
    } finally {
      timeout.mockRestore();
    }
  });

  it("AC-135.18 capture sheet schema, call and description: its own four markers and the zoom advice", async () => {
    const { captureDescriptions } = await import("../src/toolsets/capture.js");
    const { advertisedSchema } = await import("../src/toolsets/registry.js");
    const { USER_CONFIRM_ACTIONS } = await import("../src/destructive.js");
    const text = captureDescriptions["avkit_capture.sheet"] ?? "";
    expect(text.length).toBeGreaterThan(0);
    for (const line of SHEET_TEXT_MARKERS) {
      expect(text, line).toContain(line);
    }
    expect(M7.filter((marker) => text.includes(marker))).toEqual([...M7]);
    const lower = text.toLowerCase();
    for (const needle of ["cite times from cells", "narrower start and end", "no state is kept", "can be missed"]) {
      expect(lower, needle).toContain(needle);
    }
    expect(text).toContain("grid 2-5 (default 3, so 9 cells)");
    expect(text).toContain("max_edge 64-2576 (default 1568)");
    expect(text).toContain("Needs a video with a duration.");
    expect(text).not.toContain("Prerequisite: local screen grab or inbox files");
    const keys = Object.keys(advertisedSchema("avkit_capture").shape);
    expect(keys).toEqual(expect.arrayContaining(["path", "start", "end", "grid", "max_edge"]));
    expect(DESTRUCTIVE_ACTIONS.has("avkit_capture.sheet")).toBe(false);
    expect(USER_CONFIRM_ACTIONS.has("avkit_capture.sheet")).toBe(false);
  });

  it("AC-135.18 capture sheet schema, call and description: frames' workflow names sheet between probe and frames (D-605)", async () => {
    const { captureDescriptions } = await import("../src/toolsets/capture.js");
    const frames = captureDescriptions["avkit_capture.frames"] ?? "";
    expect(frames).toContain(FRAMES_WORKFLOW_WITH_SHEET);
    const workflow = frames.slice(frames.indexOf("Workflow:"));
    const probe = workflow.indexOf("probe");
    const sheet = workflow.indexOf("sheet");
    const then = workflow.indexOf("then frames");
    expect([probe > -1, sheet > probe, then > sheet]).toEqual([true, true, true]);
  });

  it("AC-135.19 sheet parity and audit coverage: ACTION_INDEX has the sheet row after frames", () => {
    expect(ACTION_INDEX).toHaveLength(74);
    const keys = ACTION_INDEX.map((row) => `${row.tool}.${row.action}`);
    const crop = keys.indexOf("avkit_capture.crop");
    const frames = keys.indexOf("avkit_capture.frames");
    expect(crop).toBeGreaterThan(-1);
    expect(frames).toBe(crop + 1);
    expect(keys[frames + 1]).toBe("avkit_capture.sheet");
    expect(ACTION_INDEX[frames + 1]).toEqual({
      tool: "avkit_capture",
      action: "sheet",
      method: "POST",
      path: "/captures/sheet",
    });
    expect(keys.filter((key) => key === "avkit_capture.sheet")).toHaveLength(1);
    expect(keys[keys.length - 1]).toBe("avkit_models.download_asset");
    expect(ACTION_INDEX.filter((row) => row.tool === "avkit_capture")).toHaveLength(13);
  });

  it("AC-135.19 sheet parity and audit coverage: the fake backend's 201 body reaches the tool result", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const calls: { url: string; method?: string; body: unknown }[] = [];
    const fetchImpl = sheetFetch(calls);
    const result = await handleTool(
      "avkit_capture",
      { action: "sheet", path: SHEET_PATH, grid: 2 },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(calls).toHaveLength(1);
    expect(result.isError).not.toBe(true);
    const parsed = JSON.parse(result.content[0].text) as typeof SHEET_BODY;
    expect(Object.keys(parsed).sort()).toEqual(["cells", "shot", "spacing_ms", "video"]);
    expect(Object.keys(parsed.video).sort()).toEqual(Object.keys(SHEET_BODY.video).sort());
    expect(Object.keys(parsed.shot).sort()).toEqual(["height", "id", "path", "width"]);
    expect(parsed.cells.map((c) => Object.keys(c).sort())).toEqual(
      SHEET_BODY.cells.map(() => ["cell", "time_ms", "timecode"]),
    );
    expect(parsed).toEqual(SHEET_BODY);
  });
});
