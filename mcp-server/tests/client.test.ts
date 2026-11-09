import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { api, apiBinary, toToolError } from "../src/client.js";
import { handleTool } from "../src/toolsets/registry.js";

const temps: string[] = [];

function tempAppData(): string {
  const dir = mkdtempSync(path.join(os.tmpdir(), "avkit-mcp-client-"));
  temps.push(dir);
  return dir;
}

afterEach(() => {
  for (const dir of temps.splice(0)) {
    rmSync(dir, { recursive: true, force: true });
  }
});

describe("TOOL_ERROR / FETCH_FAILED", () => {
  it("maps HTTP 503 without envelope to fetch_failed and isError tool shape", async () => {
    const appData = tempAppData();
    writeFileSync(path.join(appData, "mcp-token.txt"), "tok");
    const fetchImpl = vi.fn(async () => new Response("down", { status: 503 }));
    const result = await api("GET", "/health/dependencies", undefined, {
      env: {
        AVKIT_APP_DATA: appData,
        AVKIT_API_BASE: "http://127.0.0.1:8000/api/v1",
      },
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("fetch_failed");
      const tool = toToolError(result.error);
      expect(tool.isError).toBe(true);
      expect(tool.content[0].text).toContain("fetch_failed");
      expect(tool).not.toHaveProperty("ok");
    }
  });

  it("surfaces ERROR_ENVELOPE code and message from 422", async () => {
    const appData = tempAppData();
    writeFileSync(path.join(appData, "mcp-token.txt"), "tok");
    const fetchImpl = vi.fn(
      async () =>
        new Response(JSON.stringify({ error: { code: "validation_error", message: "bad", details: null } }), {
          status: 422,
        }),
    );
    const result = await api("POST", "/downloads", { url: "x" }, {
      env: {
        AVKIT_APP_DATA: appData,
        AVKIT_API_BASE: "http://127.0.0.1:8000/api/v1",
      },
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("validation_error");
      expect(result.error.message).toBe("bad");
      const tool = toToolError(result.error);
      expect(tool.isError).toBe(true);
      expect(tool.content[0].text).toContain("validation_error");
      expect(tool.content[0].text).toContain("bad");
    }
  });

  it("sets AbortSignal.timeout so a hang is not the contract", async () => {
    const appData = tempAppData();
    writeFileSync(path.join(appData, "mcp-token.txt"), "tok");
    const fetchImpl = vi.fn(async (_url: string, init?: RequestInit) => {
      expect(init?.signal).toBeDefined();
      return new Response(JSON.stringify({ status: "ok" }), { status: 200 });
    });
    const result = await api("GET", "/health", undefined, {
      env: {
        AVKIT_APP_DATA: appData,
        AVKIT_API_BASE: "http://127.0.0.1:8000/api/v1",
      },
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.ok).toBe(true);
  });
});

describe("token gate", () => {
  it("does not fetch authenticated routes without a token", async () => {
    const appData = tempAppData();
    const fetchImpl = vi.fn();
    const result = await api("GET", "/health/dependencies", undefined, {
      env: {
        AVKIT_APP_DATA: appData,
        AVKIT_API_BASE: "http://127.0.0.1:8000/api/v1",
      },
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(fetchImpl).toHaveBeenCalledTimes(0);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("token_missing");
    }
  });

  it("allows liveness without a token once api_base is known", async () => {
    const appData = tempAppData();
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      expect(String(url)).toBe("http://127.0.0.1:8000/api/v1/health");
      expect(init?.headers && (init.headers as Record<string, string>).Authorization).toBeUndefined();
      return new Response(JSON.stringify({ status: "ok" }), { status: 200 });
    });
    const result = await api("GET", "/health", undefined, {
      env: {
        AVKIT_APP_DATA: appData,
        AVKIT_API_BASE: "http://127.0.0.1:8000/api/v1",
      },
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.ok).toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it("sends Bearer from mcp-token.txt and never puts the token in TOOL_ERROR text", async () => {
    const appData = tempAppData();
    writeFileSync(path.join(appData, "mcp-token.txt"), "secret-token");
    const fetchImpl = vi.fn(async (_url: string, init?: RequestInit) => {
      const headers = init?.headers as Record<string, string>;
      expect(headers.Authorization).toBe("Bearer secret-token");
      return new Response(JSON.stringify({ error: { code: "conflict", message: "busy" } }), { status: 409 });
    });
    const result = await api("POST", "/downloads/start", {}, {
      env: {
        AVKIT_APP_DATA: appData,
        AVKIT_API_BASE: "http://127.0.0.1:8000/api/v1",
      },
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      const tool = toToolError(result.error, {
        AVKIT_APP_DATA: appData,
        AVKIT_API_BASE: "http://127.0.0.1:8000/api/v1",
      });
      expect(tool.content[0].text).not.toContain("secret-token");
    }
  });

  it("redacts an env token reflected in an API 422 envelope from handler TOOL_ERROR", async () => {
    const appData = tempAppData();
    const token = "ROUND1_SECRET_TOKEN";
    const fetchImpl = vi.fn(
      async () =>
        new Response(
          JSON.stringify({ error: { code: "validation_error", message: `reflected ${token}` } }),
          { status: 422 },
        ),
    );
    const env = {
      AVKIT_APP_DATA: appData,
      AVKIT_API_BASE: "http://127.0.0.1:8000/api/v1",
      AVKIT_API_TOKEN: token,
    };
    const result = await handleTool("avkit_download", { action: "start" }, {
      env,
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).toBe(true);
    expect(result.content[0].text).not.toContain(token);
    expect(result.content[0].text).toContain("validation_error");
    expect(result.content[0].text).toContain("[redacted]");
  });

  it("redacts a file token reflected in an API 422 envelope from handler TOOL_ERROR", async () => {
    const appData = tempAppData();
    const token = "FILE_SECRET_TOKEN";
    writeFileSync(path.join(appData, "mcp-token.txt"), `${token}\n`);
    const fetchImpl = vi.fn(
      async () =>
        new Response(
          JSON.stringify({ error: { code: "validation_error", message: `reflected ${token}` } }),
          { status: 422 },
        ),
    );
    const result = await handleTool("avkit_download", { action: "start" }, {
      env: {
        AVKIT_APP_DATA: appData,
        AVKIT_API_BASE: "http://127.0.0.1:8000/api/v1",
      },
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.isError).toBe(true);
    expect(result.content[0].text).not.toContain(token);
    expect(result.content[0].text).toContain("[redacted]");
  });
});

// MEU-128 capture-region-view (Session 58): apiBinary hands the frame headers to the image branch.
describe("MEU-128 apiBinary capture headers", () => {
  it("AC-128.21 apiBinary returns the x-capture headers", async () => {
    const appData = tempAppData();
    writeFileSync(path.join(appData, "mcp-token.txt"), "tok");
    const fetchImpl = vi.fn(async () => new Response(Uint8Array.from([0x89, 0x50, 0x4e, 0x47]), {
      status: 200,
      headers: {
        "Content-Type": "image/png",
        "X-Capture-Source": "40,30",
        "X-Capture-Region": "0,0,40,30",
        "X-Capture-Returned": "40,30",
        "X-Capture-Scale": "1.000000",
        "X-Capture-Clamped": "false",
        "X-Request-ID": "req-1",
        "X-Other": "kept out",
      },
    }));
    const result = await apiBinary("GET", "/captures/s1/image", {
      env: {
        AVKIT_APP_DATA: appData,
        AVKIT_API_BASE: "http://127.0.0.1:8000/api/v1",
      },
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.ok).toBe(true);
    const headers = result.ok ? (result as { captureHeaders?: unknown }).captureHeaders : undefined;
    expect(headers).toEqual({
      "x-capture-source": "40,30",
      "x-capture-region": "0,0,40,30",
      "x-capture-returned": "40,30",
      "x-capture-scale": "1.000000",
      "x-capture-clamped": "false",
    });
  });
});
