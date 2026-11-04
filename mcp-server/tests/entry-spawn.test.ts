import { spawn } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, rmSync, symlinkSync, unlinkSync, writeFileSync } from "node:fs";
import { createServer, type Server } from "node:http";
import type { AddressInfo } from "node:net";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

const here = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(here, "../dist");
const DEADLINE_MS = 15_000;

type Message = { jsonrpc: string; id?: number; result?: Record<string, unknown>; error?: unknown };
type Answer = { kind: "response"; message: Message } | { kind: "exit"; code: number | null; stderr: string } | { kind: "deadline"; stderr: string };

/** An in-test backend: `/api/v1/health` answers ok; every request path is recorded. */
function startBackend(): Promise<{ server: Server; port: number; paths: string[] }> {
  const paths: string[] = [];
  const server = createServer((req, res) => {
    paths.push(req.url ?? "");
    if (req.url === "/api/v1/health") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ status: "ok" }));
      return;
    }
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: { message: "not found" } }));
  });
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => {
      resolve({ server, port: (server.address() as AddressInfo).port, paths });
    });
  });
}

/** A stdio JSON-RPC session over a child process. `request` settles on the reply, an exit or the deadline; it never rejects. */
function startSession(command: string, args: string[], env: NodeJS.ProcessEnv) {
  const child = spawn(command, args, { env, stdio: ["pipe", "pipe", "pipe"], windowsHide: true });
  let buffer = "";
  let stderr = "";
  let exited: { code: number | null } | null = null;
  const replies = new Map<number, Message>();
  const waiters = new Set<() => void>();
  const wake = () => {
    for (const waiter of [...waiters]) waiter();
  };
  child.stderr.on("data", (chunk: Buffer) => {
    stderr += chunk.toString("utf8");
  });
  child.stdout.on("data", (chunk: Buffer) => {
    buffer += chunk.toString("utf8");
    let newline = buffer.indexOf("\n");
    while (newline >= 0) {
      const line = buffer.slice(0, newline).trim();
      buffer = buffer.slice(newline + 1);
      if (line.length > 0) {
        try {
          const message = JSON.parse(line) as Message;
          if (typeof message.id === "number") replies.set(message.id, message);
        } catch {
          // Not JSON-RPC; the reply wait reports the missing response.
        }
      }
      newline = buffer.indexOf("\n");
    }
    wake();
  });
  child.on("error", (error) => {
    stderr += String(error);
    exited = { code: null };
    wake();
  });
  child.on("exit", (code) => {
    exited = { code };
    wake();
  });

  function send(message: Record<string, unknown>): void {
    if (exited === null && child.stdin.writable) child.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", ...message })}\n`);
  }

  function request(id: number, method: string, params: Record<string, unknown>): Promise<Answer> {
    send({ id, method, params });
    return new Promise((settle) => {
      const check = () => {
        const reply = replies.get(id);
        if (reply !== undefined) return done({ kind: "response", message: reply });
        if (exited !== null) return done({ kind: "exit", code: exited.code, stderr: stderr.slice(-800) });
      };
      const timer = setTimeout(() => done({ kind: "deadline", stderr: stderr.slice(-800) }), DEADLINE_MS);
      const done = (answer: Answer) => {
        clearTimeout(timer);
        waiters.delete(check);
        settle(answer);
      };
      waiters.add(check);
      check();
    });
  }

  return { send, request, stop: () => child.kill() };
}

function expectResponse(answer: Answer, step: string): Message {
  expect(answer.kind, `${step}: ${JSON.stringify(answer)}`).toBe("response");
  return (answer as { message: Message }).message;
}

function toolText(message: Message): { isError: boolean; text: string } {
  const result = message.result as { isError?: boolean; content?: Array<{ type: string; text?: string }> } | undefined;
  return { isError: result?.isError === true, text: result?.content?.[0]?.text ?? "" };
}

let tmp: string;
let junction: string;
let backend: { server: Server; port: number; paths: string[] };

beforeAll(async () => {
  tmp = mkdtempSync(path.join(os.tmpdir(), "s31b-entry-spawn-"));
  junction = path.join(tmp, "resources", "mcp-server");
  mkdirSync(path.dirname(junction), { recursive: true });
  symlinkSync(distDir, junction, "junction");
  backend = await startBackend();
  const appData = path.join(tmp, "appdata");
  mkdirSync(appData);
  writeFileSync(
    path.join(appData, "backend.json"),
    JSON.stringify({ schema_version: 1, api_base: `http://127.0.0.1:${backend.port}/api/v1` }),
  );
});

afterAll(async () => {
  await new Promise<void>((resolve) => backend.server.close(() => resolve()));
  // Remove the junction first so the recursive delete never walks into mcp-server/dist.
  unlinkSync(junction);
  rmSync(tmp, { recursive: true, force: true });
});

describe("MEU-71 packaged-layout entry through a junction (AC-71.9)", () => {
  it(
    "AC-71.9 node <tmp>/resources/mcp-server/index.js answers initialize, liveness succeeds and dependencies reports token_missing",
    async () => {
      expect(existsSync(path.join(distDir, "index.js")), "build mcp-server first").toBe(true);
      const env: NodeJS.ProcessEnv = { ...process.env, AVKIT_APP_DATA: path.join(tmp, "appdata") };
      delete env.AVKIT_API_TOKEN;
      delete env.AVKIT_API_BASE;
      const session = startSession(process.execPath, [path.join(junction, "index.js")], env);
      try {
        const init = expectResponse(
          await session.request(1, "initialize", {
            protocolVersion: "2025-06-18",
            capabilities: {},
            clientInfo: { name: "s31b-ac-71-9", version: "0" },
          }),
          "initialize",
        );
        expect((init.result?.serverInfo as { name?: string } | undefined)?.name).toBe("av-kit");
        session.send({ method: "notifications/initialized" });

        const liveness = toolText(
          expectResponse(
            await session.request(2, "tools/call", { name: "avkit_health", arguments: { action: "liveness" } }),
            "liveness",
          ),
        );
        expect(liveness.isError, liveness.text).toBe(false);
        expect(liveness.text).toContain("ok");

        const dependencies = toolText(
          expectResponse(
            await session.request(3, "tools/call", { name: "avkit_health", arguments: { action: "dependencies" } }),
            "dependencies",
          ),
        );
        expect(dependencies.isError).toBe(true);
        expect(dependencies.text.startsWith("token_missing:"), dependencies.text).toBe(true);
      } finally {
        session.stop();
      }
      expect(backend.paths).toContain("/api/v1/health");
      expect(backend.paths.some((p) => p.includes("/health/dependencies"))).toBe(false);
    },
    3 * DEADLINE_MS + 10_000,
  );
});
