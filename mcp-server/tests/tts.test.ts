import { afterEach, describe, expect, it, vi } from "vitest";
import { SERVER_INSTRUCTIONS } from "../src/index.js";
import { handleTool } from "../src/toolsets/registry.js";
import { ttsDescriptions } from "../src/toolsets/tts.js";
import { cleanupDirs, okJson, tempAppData, toolEnv } from "./fixtures.js";

const temps: string[] = [];

afterEach(() => {
  cleanupDirs(temps);
});

const GENERATE_TEXT = "generate returns the job at once (status Generating); poll get until Done/Failed/Cancelled; cancel stops a running job";
const INSTRUCTIONS_LINE = "TTS: load a model first; prepare is preview only; generate returns the job at once; poll get; cancel stops a running job.";

async function call(args: Record<string, unknown>, fetchImpl: ReturnType<typeof vi.fn>) {
  const appData = tempAppData();
  temps.push(appData);
  return handleTool("avkit_tts", args, {
    env: toolEnv(appData),
    fetchImpl: fetchImpl as unknown as typeof fetch,
  });
}

describe("MEU-77 AC-77.12 avkit_tts generate is asynchronous (MCP_TTS_TEXT)", () => {
  it("AC-77.12 generate returns the Generating job on the first call and its description says so", async () => {
    const job = { id: "job-1", status: "Generating", text_preview: "Hello there.", segments_done: 0 };
    const fetchImpl = vi.fn(async () => okJson(job, 201));
    const result = await call(
      { action: "generate", text: "Hello there.", voice: "am_eric", speed: 1, format: "MP3", enabled_steps: [] },
      fetchImpl,
    );
    expect(result.isError).not.toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
    const [url, init] = fetchImpl.mock.calls[0] as unknown as [string, RequestInit];
    expect(String(url)).toMatch(/\/tts\/generate$/);
    expect(init.method).toBe("POST");
    expect(JSON.parse(result.content[0].text)).toEqual(job);
    expect(ttsDescriptions["avkit_tts.generate"]).toContain(GENERATE_TEXT);
  });

  it("AC-77.12 SERVER_INSTRUCTIONS carries the asynchronous TTS line", () => {
    expect(SERVER_INSTRUCTIONS.split("\n")).toContain(INSTRUCTIONS_LINE);
  });

  it("AC-77.12 [neg] neither text says generate is one job", () => {
    expect(ttsDescriptions["avkit_tts.generate"]).not.toContain("generate is one job");
    expect(SERVER_INSTRUCTIONS).not.toContain("generate is one job");
  });
});
