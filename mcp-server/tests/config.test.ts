import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { resolveApiBase, resolveAppData, resolveToken } from "../src/config.js";

const temps: string[] = [];

function tempAppData(): string {
  const dir = mkdtempSync(path.join(os.tmpdir(), "avkit-mcp-"));
  temps.push(dir);
  return dir;
}

afterEach(() => {
  for (const dir of temps.splice(0)) {
    rmSync(dir, { recursive: true, force: true });
  }
});

describe("DISCOVERY_ORDER", () => {
  it("fails app_not_running without env or descriptor and never guesses port 0", () => {
    const appData = tempAppData();
    const result = resolveApiBase({ AVKIT_APP_DATA: appData });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("app_not_running");
      expect(JSON.stringify(result)).not.toMatch(/127\.0\.0\.1:0/);
    }
  });

  it("uses backend.json api_base when env pin is unset", () => {
    const appData = tempAppData();
    writeFileSync(
      path.join(appData, "backend.json"),
      JSON.stringify({
        schema_version: 1,
        host: "127.0.0.1",
        port: 51234,
        api_base: "http://127.0.0.1:51234/api/v1",
      }),
    );
    const result = resolveApiBase({ AVKIT_APP_DATA: appData });
    expect(result).toEqual({ ok: true, apiBase: "http://127.0.0.1:51234/api/v1" });
  });

  it("accepts a pin without a descriptor (dev uvicorn)", () => {
    const appData = tempAppData();
    const result = resolveApiBase({
      AVKIT_APP_DATA: appData,
      AVKIT_API_BASE: "http://127.0.0.1:8000/api/v1",
    });
    expect(result).toEqual({ ok: true, apiBase: "http://127.0.0.1:8000/api/v1" });
  });
});

describe("STALE_PIN", () => {
  it("rejects a pin whose host/port mismatches the live descriptor and does not invent a fetch", () => {
    const appData = tempAppData();
    writeFileSync(
      path.join(appData, "backend.json"),
      JSON.stringify({
        schema_version: 1,
        host: "127.0.0.1",
        port: 51234,
        api_base: "http://127.0.0.1:51234/api/v1",
      }),
    );
    const result = resolveApiBase({
      AVKIT_APP_DATA: appData,
      AVKIT_API_BASE: "http://127.0.0.1:9/api/v1",
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("stale_pin");
    }
  });
});

describe("TOKEN_SOURCES", () => {
  it("prefers AVKIT_API_TOKEN over mcp-token.txt and never returns a GUI nonce from backend.json", () => {
    const appData = tempAppData();
    writeFileSync(path.join(appData, "mcp-token.txt"), "file-token\n");
    writeFileSync(
      path.join(appData, "backend.json"),
      JSON.stringify({ api_base: "http://127.0.0.1:1/api/v1", nonce: "GUI-NONCE" }),
    );
    const result = resolveToken({
      AVKIT_APP_DATA: appData,
      AVKIT_API_TOKEN: "env-token",
    });
    expect(result).toEqual({ ok: true, token: "env-token" });
    expect(JSON.stringify(result)).not.toContain("GUI-NONCE");
  });

  it("falls through blank env to mcp-token.txt", () => {
    const appData = tempAppData();
    writeFileSync(path.join(appData, "mcp-token.txt"), "  file-token  \n");
    const result = resolveToken({
      AVKIT_APP_DATA: appData,
      AVKIT_API_TOKEN: "   ",
    });
    expect(result).toEqual({ ok: true, token: "file-token" });
  });

  it("returns token_missing without leaking a token string", () => {
    const appData = tempAppData();
    const result = resolveToken({ AVKIT_APP_DATA: appData });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("token_missing");
      expect(result.error.message.toLowerCase()).not.toMatch(/bearer |sk-|nonce/i);
    }
  });
});

describe("APP_DATA_OVERRIDE", () => {
  it("uses AVKIT_APP_DATA instead of DEFAULT_APP_DATA", () => {
    const appData = tempAppData();
    expect(resolveAppData({ AVKIT_APP_DATA: appData, LOCALAPPDATA: "C:\\Other" })).toBe(appData);
  });
});

describe("invalid pin suffix", () => {
  it("rejects AVKIT_API_BASE without /api/v1", () => {
    const result = resolveApiBase({
      AVKIT_APP_DATA: tempAppData(),
      AVKIT_API_BASE: "http://127.0.0.1:8000",
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("invalid_api_base");
    }
  });

  it("rejects a non-URL pin that only contains the /api/v1 substring", () => {
    const result = resolveApiBase({
      AVKIT_APP_DATA: tempAppData(),
      AVKIT_API_BASE: "not-a-url/api/v1",
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("invalid_api_base");
    }
  });

  it("does not consume backend.json when schema_version is not 1", () => {
    const appData = tempAppData();
    writeFileSync(
      path.join(appData, "backend.json"),
      JSON.stringify({
        schema_version: 999,
        host: "127.0.0.1",
        port: 51234,
        api_base: "http://127.0.0.1:51234/api/v1",
      }),
    );
    const result = resolveApiBase({ AVKIT_APP_DATA: appData });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("app_not_running");
    }
  });
});
