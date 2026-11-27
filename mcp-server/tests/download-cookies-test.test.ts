import { afterEach, describe, expect, it, vi } from "vitest";
import { createServer } from "../src/index.js";
import { handleTool } from "../src/toolsets/registry.js";
import { API_BASE, cleanupDirs, okJson, tempAppData, toolEnv } from "./fixtures.js";

// MEU-169 (AC-169.7; COOKIE_TEST_WIRE). The avkit_download cookies_test action names the three
// outcomes in its registered description, and its reply is the API's reply unchanged.

type RegisteredTool = {
  description?: string;
  _meta?: { action_descriptions?: Record<string, string> };
};

const MARKERS = ["Workflow:", "Prerequisite:", "Returns:", "Errors:"];

const temps: string[] = [];

afterEach(() => {
  cleanupDirs(temps);
});

function cookiesTestDescription(): string {
  const server = createServer();
  const tools =
    (server as unknown as { _registeredTools: Record<string, RegisteredTool> })._registeredTools ?? {};
  return tools.avkit_download?._meta?.action_descriptions?.cookies_test ?? "";
}

describe("MEU-169 avkit_download cookies_test", () => {
  it("AC-169.7 the cookies_test description names the three outcomes", () => {
    const text = cookiesTestDescription();
    for (const marker of MARKERS) {
      expect(text.split(marker)).toHaveLength(2);
    }
    const starts = MARKERS.map((marker) => text.indexOf(marker));
    expect(starts[0]).toBe(0);
    expect([...starts].sort((a, b) => a - b)).toEqual(starts);
    for (const outcome of ["ok", "unreadable", "check_failed"]) {
      expect(text).toMatch(new RegExp(`\\b${outcome}\\b`));
    }
    expect(text).toContain("error_message");
  });

  it("AC-169.7 the cookies_test reply carries outcome and error_message", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const reply = { ok: false, outcome: "check_failed", error_message: "Sign in to confirm" };
    const fetchImpl = vi.fn(async (url: string, init?: RequestInit) => {
      expect(init?.method).toBe("POST");
      expect(String(url)).toBe(`${API_BASE}/downloads/cookies/test`);
      return okJson(reply);
    });
    const result = await handleTool(
      "avkit_download",
      { action: "cookies_test", mode: "browser", browser: "chrome" },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(result.isError).not.toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(JSON.parse(String(result.content[0]?.text))).toEqual(reply);
  });

  it("AC-169.7 an unknown input key is refused", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const fetchImpl = vi.fn();
    const result = await handleTool(
      "avkit_download",
      { action: "cookies_test", mode: "none", outcome: "ok" },
      { env: toolEnv(appData), fetchImpl: fetchImpl as unknown as typeof fetch },
    );
    expect(result.isError).toBe(true);
    expect(result.content[0].text).toContain("validation_error");
    expect(fetchImpl).toHaveBeenCalledTimes(0);
  });
});
