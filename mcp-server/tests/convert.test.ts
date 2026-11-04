import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DESTRUCTIVE_ACTIONS, NON_DESTRUCTIVE_STOPS } from "../src/destructive.js";
import { SERVER_INSTRUCTIONS } from "../src/index.js";
import { ACTION_INDEX, COMPOUND_TOOLS, handleTool } from "../src/toolsets/registry.js";
import { SETTING_NAMESPACES, SETTINGS_SCHEMA } from "../src/toolsets/settings.js";
import {
  cleanupDirs,
  EXPECTED_ACTION_INDEX,
  listEnvelope,
  okJson,
  tempAppData,
  toolEnv,
} from "./fixtures.js";

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const CONVERT_TS = path.join(ROOT, "src", "toolsets", "convert.ts");
const COMPOUND_DIR = path.join(ROOT, "src", "compound");
const REGISTRY_TS = path.join(ROOT, "src", "toolsets", "registry.ts");
const DIST_CONVERT = path.join(ROOT, "dist", "toolsets", "convert.js");
const CONVERT_ACTIONS = [
  { action: "add", method: "POST", path: "/conversions" },
  { action: "list", method: "GET", path: "/conversions" },
  { action: "get", method: "GET", path: "/conversions/{id}" },
  { action: "start", method: "POST", path: "/conversions/start" },
  { action: "pause", method: "POST", path: "/conversions/pause" },
  { action: "resume", method: "POST", path: "/conversions/resume" },
  { action: "cancel", method: "POST", path: "/conversions/cancel" },
  { action: "reorder", method: "PUT", path: "/conversions/reorder" },
  { action: "reset", method: "POST", path: "/conversions/{id}/reset" },
  { action: "remove", method: "DELETE", path: "/conversions/{id}" },
  { action: "clear", method: "DELETE", path: "/conversions" },
  { action: "gpu", method: "GET", path: "/conversions/gpu" },
  { action: "gpu_refresh", method: "POST", path: "/conversions/gpu/refresh" },
] as const;
const CONVERTER_KEYS = ["output_dir", "default_preset", "skip_existing", "gpu_preference"] as const;
const CONVERTER_DEFAULTS = {
  output_dir: "~/Videos/av-kit",
  default_preset: "balanced",
  skip_existing: true,
  gpu_preference: "auto",
};
const M7 = ["Workflow:", "Prerequisite:", "Returns:", "Errors:"] as const;
const temps: string[] = [];

afterEach(() => {
  cleanupDirs(temps);
});

describe("MEU-32 avkit_convert", () => {
  it("AC-32.1 ACTION_INDEX_AFTER keeps first ACTION_INDEX_KEEP rows", () => {
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
    expect(ACTION_INDEX.slice(0, 46)).toEqual(EXPECTED_ACTION_INDEX);
    expect(EXPECTED_ACTION_INDEX).toHaveLength(46);
  });

  it("AC-32.2 CONVERT_ACTIONS match REST 1:1 with no stop", () => {
    const rows = ACTION_INDEX.filter((row) => row.tool === "avkit_convert");
    expect(rows).toHaveLength(13);
    expect(rows.map((row) => ({ action: row.action, method: row.method, path: row.path }))).toEqual(
      CONVERT_ACTIONS.map((row) => ({ action: row.action, method: row.method, path: row.path })),
    );
    expect(rows.some((row) => row.action === "stop")).toBe(false);
    expect(rows.every((row) => row.path.startsWith("/conversions"))).toBe(true);
    expect(rows.some((row) => row.path.includes("/ffmpeg") || row.path === "/convert")).toBe(false);
  });

  it("AC-32.3 convert add schema strict extra key fails before fetch", async () => {
    const { convertSchema } = await import("../src/toolsets/convert.js");
    const parsed = convertSchema.safeParse({
      action: "add",
      kind: "compress",
      paths: ["C:/tmp/a.mp4"],
      extra: true,
    });
    expect(parsed.success).toBe(false);
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn();
    const result = await handleTool(
      "avkit_convert",
      { action: "add", kind: "compress", paths: ["C:/tmp/a.mp4"], extra: true },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(result.isError).toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(0);
    const emptyReorder = convertSchema.safeParse({ action: "reorder", job_ids: [] });
    expect(emptyReorder.success).toBe(false);
    const emptyFetch = vi.fn();
    const emptyResult = await handleTool(
      "avkit_convert",
      { action: "reorder", job_ids: [] },
      { env: toolEnv(appData), fetchImpl: emptyFetch as unknown as typeof fetch },
    );
    expect(emptyResult.isError).toBe(true);
    expect(emptyFetch).toHaveBeenCalledTimes(0);
  });

  it("AC-32.4 DESTRUCTIVE_CONVERT confirm; cancel is not destructive", () => {
    expect(DESTRUCTIVE_ACTIONS.has("avkit_convert.remove")).toBe(true);
    expect(DESTRUCTIVE_ACTIONS.has("avkit_convert.clear")).toBe(true);
    expect(DESTRUCTIVE_ACTIONS.has("avkit_convert.cancel")).toBe(false);
    expect(NON_DESTRUCTIVE_STOPS.has("avkit_convert.cancel")).toBe(true);
  });

  it("AC-32.5 M7 markers and Convert local-files instructions", async () => {
    const { convertDescriptions } = await import("../src/toolsets/convert.js");
    for (const row of CONVERT_ACTIONS) {
      const text = convertDescriptions[`avkit_convert.${row.action}`];
      expect(typeof text).toBe("string");
      const hits = M7.filter((marker) => text.toLowerCase().includes(marker.toLowerCase()));
      expect(hits.length, row.action).toBeGreaterThanOrEqual(3);
    }
    expect(SERVER_INSTRUCTIONS.toLowerCase()).toMatch(/local files only/);
    expect(SERVER_INSTRUCTIONS).toMatch(/never upload/i);
    expect(SERVER_INSTRUCTIONS).toMatch(/YouTube/);
  });

  it("AC-32.6 SETTINGS_SCHEMA converter keys and namespace enum", () => {
    expect([...SETTING_NAMESPACES]).toContain("converter");
    const converter = SETTINGS_SCHEMA.namespaces.converter;
    expect(Object.keys(converter).sort()).toEqual([...CONVERTER_KEYS].sort());
    expect(converter.output_dir.default).toBe(CONVERTER_DEFAULTS.output_dir);
    expect(converter.default_preset.default).toBe(CONVERTER_DEFAULTS.default_preset);
    expect(converter.skip_existing.default).toBe(CONVERTER_DEFAULTS.skip_existing);
    expect(converter.gpu_preference.default).toBe(CONVERTER_DEFAULTS.gpu_preference);
  });

  it("AC-32.7 list requires envelope; sanitize drops forbidden keys", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const bare = vi.fn(async () => okJson([]));
    const rejected = await handleTool("avkit_convert", { action: "list" }, {
      env: toolEnv(appData),
      fetchImpl: bare as unknown as typeof fetch,
    });
    expect(rejected.isError).toBe(true);
    expect(rejected.content[0].text.toLowerCase()).toMatch(/envelope|items|processor/);
    const okFetch = vi.fn(async () =>
      okJson({
        items: [{ id: "c1", media_bytes: "nope", audio_bytes: "nope", cookie_bytes: "nope" }],
        processor: { state: "Idle", current_job_id: null },
      }),
    );
    const accepted = await handleTool("avkit_convert", { action: "list" }, {
      env: toolEnv(appData),
      fetchImpl: okFetch as unknown as typeof fetch,
    });
    expect(accepted.isError).not.toBe(true);
    expect(accepted.content[0].text).not.toContain("media_bytes");
    expect(accepted.content[0].text).not.toContain("audio_bytes");
    expect(accepted.content[0].text).not.toContain("cookie_bytes");
    const parsed = JSON.parse(accepted.content[0].text) as { items: unknown[]; processor: unknown };
    expect(parsed).toEqual(expect.objectContaining({ items: expect.any(Array), processor: expect.anything() }));
    void listEnvelope;
  });

  it("AC-32.8 add uses ADD_TIMEOUT_MS and dist registers convert", () => {
    const registry = readFileSync(REGISTRY_TS, "utf8");
    expect(registry).toMatch(/avkit_convert/);
    expect(registry).toMatch(/ADD_TIMEOUT_MS/);
    expect(registry).toMatch(/tool === "avkit_convert"/);
    expect(existsSync(DIST_CONVERT)).toBe(true);
  });

  it("AC-32.9 convert tool lives at toolsets/convert.ts not compound/", () => {
    expect(existsSync(CONVERT_TS)).toBe(true);
    expect(existsSync(COMPOUND_DIR)).toBe(false);
  });

  it("AC-32.10 missing confirm is validation_error with fetch 0", async () => {
    const appData = tempAppData();
    temps.push(appData);
    for (const action of ["remove", "clear"] as const) {
      const fetchImpl = vi.fn();
      const args = action === "remove" ? { action, id: "c1" } : { action };
      const result = await handleTool("avkit_convert", args, {
        env: toolEnv(appData),
        fetchImpl: fetchImpl as unknown as typeof fetch,
      });
      expect(result.isError).toBe(true);
      expect(result.content[0].text).toContain("validation_error");
      expect(result.content[0].text).not.toContain("confirm_required");
      expect(fetchImpl).toHaveBeenCalledTimes(0);
    }
  });

  it("AC-32.11 kind-specific add fields are forwarded; extra key still fails", async () => {
    const { convertSchema } = await import("../src/toolsets/convert.js");
    const extra = convertSchema.safeParse({
      action: "add",
      kind: "compress",
      paths: ["C:/tmp/a.mp4"],
      cq: 18,
      nope: true,
    });
    expect(extra.success).toBe(false);
    const appData = tempAppData();
    temps.push(appData);
    const bodies: unknown[] = [];
    const fetchImpl = vi.fn(async (_url: string, init?: RequestInit) => {
      bodies.push(init?.body === undefined ? undefined : JSON.parse(String(init.body)));
      return okJson({ items: [{ id: "c1" }] }, 201);
    });
    const compress = await handleTool(
      "avkit_convert",
      {
        action: "add",
        kind: "compress",
        paths: ["C:/tmp/a.mp4"],
        cq: 18,
        scale_height: 720,
        audio_mode: "aac_192",
        gpu_preference: "nvidia",
      },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(compress.isError).not.toBe(true);
    expect(bodies[0]).toEqual({
      kind: "compress",
      paths: ["C:/tmp/a.mp4"],
      cq: 18,
      scale_height: 720,
      audio_mode: "aac_192",
      gpu_preference: "nvidia",
    });
    const cut = await handleTool(
      "avkit_convert",
      { action: "add", kind: "cut", paths: ["C:/tmp/a.mp4"], in_ms: 0, out_ms: 1000, copy_mode: "reencode" },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(cut.isError).not.toBe(true);
    expect(bodies[1]).toEqual({
      kind: "cut",
      paths: ["C:/tmp/a.mp4"],
      in_ms: 0,
      out_ms: 1000,
      copy_mode: "reencode",
    });
    const extract = await handleTool(
      "avkit_convert",
      { action: "add", kind: "extract", paths: ["C:/tmp/a.mp4"], stream_mode: "first", stream_index: 2 },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(extract.isError).not.toBe(true);
    expect(bodies[2]).toEqual({
      kind: "extract",
      paths: ["C:/tmp/a.mp4"],
      stream_mode: "first",
      stream_index: 2,
    });
  });
});
