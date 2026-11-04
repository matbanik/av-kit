import { mkdtempSync, rmSync } from "node:fs";
import http from "node:http";
import type { AddressInfo } from "node:net";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { STDIO_DEFAULT_MAX_BUFFER_SIZE } from "@modelcontextprotocol/sdk/shared/stdio.js";
import { afterEach, describe, expect, it } from "vitest";
import { IMAGE_MAX_BYTES } from "../src/toolsets/capture.js";

const MCP_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SERVER = path.join(MCP_ROOT, "dist", "index.js");
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
/** The real shot that closed the connection during staging. */
const REAL_SHOT_BYTES = 8_059_548;
/** Room left for the JSON-RPC envelope around the base64; the measured envelope is 98 B. */
const ENVELOPE_RESERVE = 65_536;
const STDIO_CASE_TIMEOUT_MS = 60_000;

const temps: string[] = [];
afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

function pngOf(size: number): Buffer {
  const body = Buffer.alloc(size, 0xab);
  PNG_SIGNATURE.copy(body);
  return body;
}

type CallResult =
  | { kind: "image"; bytes: Buffer; text: ""; isError: boolean }
  | { kind: "tool_error"; bytes: null; text: string; isError: boolean }
  | { kind: "threw"; bytes: null; text: string; isError: true };

/** One tool call through the built server, its outcome recorded, then a later call on the same connection. */
async function callImage(body: Buffer): Promise<{ call: CallResult; laterCallAnswered: boolean }> {
  const stub = http.createServer((req, res) => {
    if (req.url?.includes("/captures/") && req.url.includes("/image")) {
      res.writeHead(200, { "Content-Type": "image/png" });
      res.end(body);
      return;
    }
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end("{}");
  });
  await new Promise<void>((resolve) => stub.listen(0, "127.0.0.1", resolve));
  const port = (stub.address() as AddressInfo).port;
  // A live backend.json refuses a pin that differs from it, so the server gets an empty app-data folder.
  const appData = mkdtempSync(path.join(os.tmpdir(), "s44-image-stdio-"));
  temps.push(appData);
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [SERVER],
    env: {
      AVKIT_APP_DATA: appData,
      AVKIT_API_BASE: `http://127.0.0.1:${port}/api/v1`,
      AVKIT_API_TOKEN: "stub-token",
    },
    stderr: "pipe",
  });
  const client = new Client({ name: "image-over-stdio", version: "0" }, { capabilities: {} });
  try {
    await client.connect(transport);
    let call: CallResult;
    try {
      const res = await client.callTool({ name: "avkit_capture", arguments: { action: "image", id: "s1" } });
      const content = (Array.isArray(res.content) ? res.content : []) as { type: string; data?: string; text?: string }[];
      const image = content.find((item) => item.type === "image" && typeof item.data === "string");
      call = image
        ? { kind: "image", bytes: Buffer.from(image.data as string, "base64"), text: "", isError: res.isError === true }
        : {
            kind: "tool_error",
            bytes: null,
            text: content.map((item) => item.text ?? "").join("\n"),
            isError: res.isError === true,
          };
    } catch (err) {
      call = { kind: "threw", bytes: null, text: err instanceof Error ? err.message : String(err), isError: true };
    }
    let laterCallAnswered = false;
    try {
      await client.listTools();
      laterCallAnswered = true;
    } catch {
      laterCallAnswered = false;
    }
    return { call, laterCallAnswered };
  } finally {
    await client.close().catch(() => undefined);
    await new Promise<void>((resolve) => stub.close(() => resolve()));
  }
}

describe("MEU-111 image over the real stdio transport", () => {
  it("AC-111.1 an image of exactly 7,800,000 B returns intact and the connection answers a later call", async () => {
    const body = pngOf(7_800_000);
    const { call, laterCallAnswered } = await callImage(body);
    expect(call.kind).toBe("image");
    expect(call.isError).toBe(false);
    expect(call.bytes?.equals(body)).toBe(true);
    expect(laterCallAnswered).toBe(true);
  }, STDIO_CASE_TIMEOUT_MS);

  it.each([7_800_001, REAL_SHOT_BYTES])(
    "AC-111.2 %d B returns payload_too_large naming the paths and the connection answers a later call",
    async (size) => {
      const { call, laterCallAnswered } = await callImage(pngOf(size));
      expect(call.kind).toBe("tool_error");
      expect(call.isError).toBe(true);
      expect(call.text).toContain("payload_too_large");
      expect(call.text).toContain("original_path");
      expect(call.text).toContain("annotated_path");
      expect(laterCallAnswered).toBe(true);
    },
    STDIO_CASE_TIMEOUT_MS,
  );

  it("AC-111.3 the cap's base64 plus an envelope reserve fits the SDK's stdio buffer", () => {
    expect(IMAGE_MAX_BYTES).toBe(7_800_000);
    expect(Math.ceil(IMAGE_MAX_BYTES / 3) * 4 + ENVELOPE_RESERVE).toBeLessThanOrEqual(STDIO_DEFAULT_MAX_BUFFER_SIZE);
  });
});
