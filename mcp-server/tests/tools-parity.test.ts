import { afterEach, describe, expect, it, vi } from "vitest";
import { handleTool } from "../src/toolsets/registry.js";
import {
  API_BASE,
  cleanupDirs,
  listEnvelope,
  okJson,
  tempAppData,
  toolEnv,
} from "./fixtures.js";

const temps: string[] = [];

afterEach(() => {
  cleanupDirs(temps);
});

describe("LIST_ENVELOPE", () => {
  it.each(["avkit_download", "avkit_transcript"] as const)(
    "%s.list rejects a bare array",
    async (tool) => {
      const appData = tempAppData();
      temps.push(appData);
      const fetchImpl = vi.fn(async () => okJson([]));
      const result = await handleTool(tool, { action: "list" }, {
        env: toolEnv(appData),
        fetchImpl: fetchImpl as unknown as typeof fetch,
      });
      expect(result.isError).toBe(true);
      expect(result.content[0].text.toLowerCase()).toMatch(/envelope|items|processor/);
    },
  );

  it("download.list accepts { items, processor }", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn(async () => okJson(listEnvelope([{ id: "j1" }])));
    const result = await handleTool("avkit_download", { action: "list" }, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    const parsed = JSON.parse(result.content[0].text) as { items: unknown[]; processor: unknown };
    expect(Array.isArray(parsed.items)).toBe(true);
    expect(parsed.processor).toBeTruthy();
  });
});

describe("ERROR_ENVELOPE surface", () => {
  it("API 422 envelope becomes TOOL_ERROR with code and message", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn(
      async () =>
        new Response(JSON.stringify({ error: { code: "validation_error", message: "unknown leaf", details: null } }), {
          status: 422,
        }),
    );
    const result = await handleTool(
      "avkit_settings",
      { action: "set", namespace: "ui", rail: false },
      {
        env: toolEnv(appData),
        fetchImpl: fetchImpl as unknown as typeof fetch,
      },
    );
    expect(result.isError).toBe(true);
    expect(result.content[0].text).toContain("validation_error");
    expect(result.content[0].text).toContain("unknown leaf");
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it("API 409 envelope becomes TOOL_ERROR with code and message", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn(
      async () =>
        new Response(JSON.stringify({ error: { code: "conflict", message: "already processing" } }), {
          status: 409,
        }),
    );
    const result = await handleTool("avkit_download", { action: "start" }, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).toBe(true);
    expect(result.content[0].text).toContain("conflict");
    expect(result.content[0].text).toContain("already processing");
  });
});

describe("FORBIDDEN_RESULT_FIELDS", () => {
  it("strips leaked text, video_ids, and lang_code from the tool result", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn(
      async () =>
        okJson({
          id: "tts1",
          text: "SECRET",
          text_preview: "hi",
          text_hash: "abc",
          video_ids: ["x"],
          lang_code: "en",
        }),
    );
    const result = await handleTool("avkit_tts", { action: "get", id: "tts1" }, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    expect(result.content[0].text).not.toContain("SECRET");
    expect(result.content[0].text).not.toContain("video_ids");
    expect(result.content[0].text).not.toContain("lang_code");
    expect(result.content[0].text).toContain("text_preview");
  });
});

describe("VOICES_FACADE", () => {
  it("avkit_tts.voices GETs /tts/voices only", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      expect(init?.method).toBe("GET");
      expect(String(url)).toBe(`${API_BASE}/tts/voices`);
      return okJson({ items: [{ voice_id: "am_eric", language: "en", gender: "m", style_description: "x" }] });
    });
    const result = await handleTool("avkit_tts", { action: "voices" }, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });
});

describe("RULE-2 reorder", () => {
  it.each([
    ["avkit_download", "/downloads/reorder", ["b", "a"]],
    ["avkit_transcript", "/transcripts/reorder", ["t2", "t1"]],
  ] as const)("%s.reorder forwards exact job_ids", async (tool, path, jobIds) => {
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      expect(init?.method).toBe("PUT");
      expect(String(url)).toBe(`${API_BASE}${path}`);
      const body = JSON.parse(String(init?.body)) as { job_ids: string[] };
      expect(body.job_ids).toEqual([...jobIds]);
      return okJson(listEnvelope(jobIds.map((id) => ({ id }))));
    });
    const result = await handleTool(tool, { action: "reorder", job_ids: [...jobIds] }, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    const parsed = JSON.parse(result.content[0].text) as { items: { id: string }[] };
    expect(parsed.items.map((i) => i.id)).toEqual([...jobIds]);
  });
});

describe("SETTINGS_UI_API_KEYS", () => {
  it("theme-only ui set is forwarded as leaf keys", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      expect(init?.method).toBe("PUT");
      expect(String(url)).toBe(`${API_BASE}/settings/ui`);
      expect(JSON.parse(String(init?.body))).toEqual({ theme: "dark" });
      return okJson({ theme: "dark" });
    });
    const result = await handleTool("avkit_settings", { action: "set", namespace: "ui", theme: "dark" }, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
  });
});
