import { afterEach, describe, expect, it, vi } from "vitest";
import { createServer } from "../src/index.js";
import {
  ACTION_INDEX,
  COMPOUND_TOOLS,
  handleTool,
  OLD_TOOL_NAMES as EXPORTED_OLD_NAMES,
} from "../src/toolsets/registry.js";
import {
  API_BASE,
  cleanupDirs,
  CAPTURE_ACTION_INDEX,
  CONVERT_ACTION_INDEX,
  EXPECTED_ACTION_INDEX,
  EXPECTED_COMPOUND_TOOLS,
  expectedBody,
  interpolatePath,
  listEnvelope,
  minimalInput,
  OLD_TOOL_NAMES,
  okJson,
  tempAppData,
  toolEnv,
} from "./fixtures.js";

const temps: string[] = [];

afterEach(() => {
  cleanupDirs(temps);
});

function registeredToolNames(server: ReturnType<typeof createServer>): string[] {
  const internal = server as unknown as { _registeredTools: Record<string, unknown> };
  return Object.keys(internal._registeredTools ?? {});
}

describe("ACTION_INDEX census", () => {
  it("exports ACTION_INDEX_AFTER rows; KEEP rows unchanged; registers COMPOUND_TOOLS", () => {
    // TA-9 (Session 27, MEU-62): +1 avkit_models.download_asset, appended.
    // TA-1 (Session 30, MEU-67): +avkit_capture.flatten, +avkit_capture.revert.
    // MEU-130 (Session 59): +avkit_capture.crop after revert.
    // MEU-133 (Session 62): +avkit_convert.probe after gpu_refresh.
    // MEU-134 (Session 62): +avkit_capture.frames after crop.
    expect(ACTION_INDEX).toHaveLength(73);
    expect(EXPECTED_ACTION_INDEX).toHaveLength(46);
    expect(ACTION_INDEX.slice(0, 46)).toEqual(EXPECTED_ACTION_INDEX);
    expect([...COMPOUND_TOOLS]).toEqual([...EXPECTED_COMPOUND_TOOLS]);
    expect([...EXPORTED_OLD_NAMES]).toEqual([...OLD_TOOL_NAMES]);
    const names = registeredToolNames(createServer());
    expect(names.sort()).toEqual([...EXPECTED_COMPOUND_TOOLS].sort());
    for (const old of OLD_TOOL_NAMES) {
      expect(names).not.toContain(old);
    }
    expect(names).not.toContain("avkit_health_startup_metrics");
    expect(names).not.toContain("avkit_health_console");
    expect(names).toContain("avkit_convert");
    expect(names).toContain("avkit_capture");
  });

  it.each([...EXPECTED_ACTION_INDEX, ...CONVERT_ACTION_INDEX, ...CAPTURE_ACTION_INDEX])(
    "$tool.$action calls $method $path",
    async (row) => {
      const appData = tempAppData();
      temps.push(appData);
      const args = minimalInput(row.tool, row.action);
      const expectedPath = interpolatePath(row.path, args);
      const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
        expect(init?.method).toBe(row.method);
        expect(String(url)).toBe(`${API_BASE}${expectedPath}`);
        const actualBody = init?.body === undefined ? undefined : JSON.parse(String(init.body));
        expect(actualBody).toEqual(expectedBody(row.tool, row.action));
        if (row.tool === "avkit_capture" && (row.action === "list" || row.action === "list_requests")) {
          return okJson({ items: [] });
        }
        if (row.tool === "avkit_capture" && row.action === "image") {
          return new Response(Uint8Array.from([0x89, 0x50, 0x4e, 0x47]), {
            status: 200,
            headers: { "Content-Type": "image/png" },
          });
        }
        if (row.action === "list") {
          return okJson(listEnvelope());
        }
        if (row.action === "cookies_test") {
          const body = (actualBody ?? {}) as Record<string, unknown>;
          expect(body).not.toHaveProperty("cookie");
          expect(body).not.toHaveProperty("cookies");
          expect(body).not.toHaveProperty("cookie_bytes");
          expect(JSON.stringify(body)).not.toMatch(/cookie_bytes|Set-Cookie/i);
        }
        return okJson({ ok: true });
      });
      const result = await handleTool(row.tool, args, {
        env: toolEnv(appData),
        fetchImpl: fetchImpl as unknown as typeof fetch,
        // FIXTURE_REPAIRS (e) (Session 30): USER_CONFIRM_ACTIONS rows reach their fetch.
        confirmWithUser: async () => "accept",
      });
      expect(result.isError).not.toBe(true);
      expect(fetchImpl).toHaveBeenCalledTimes(1);
    },
  );

  it("download.stop posts to /downloads/stop (alias of cancel)", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      expect(init?.method).toBe("POST");
      expect(String(url)).toBe(`${API_BASE}/downloads/stop`);
      return okJson({ ok: true }, 202);
    });
    const result = await handleTool("avkit_download", { action: "stop" }, {
      env: toolEnv(appData),
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });
});
