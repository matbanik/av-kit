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
    expect(ACTION_INDEX).toHaveLength(70);
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
    expect(ACTION_INDEX.filter((row) => row.tool === "avkit_convert")).toHaveLength(13);
  });

  it("AC-38.2 CAPTURE_ACTIONS match REST 1:1; REST_ONLY absent", () => {
    const rows = ACTION_INDEX.filter((row) => row.tool === "avkit_capture");
    // TA-2 (Session 30, MEU-67).
    expect(rows).toHaveLength(10);
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
