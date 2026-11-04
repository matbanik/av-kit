import { spawn } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const here = path.dirname(fileURLToPath(import.meta.url));
const mcpRoot = path.resolve(here, "..");
const repoRoot = path.resolve(mcpRoot, "..");
const bundleDir = path.join(mcpRoot, "bundle");
const DEADLINE_MS = 15_000;

type Answer =
  | { kind: "response"; message: { id?: number; result?: { serverInfo?: { name?: string } } } }
  | { kind: "exit"; code: number | null; stderr: string }
  | { kind: "deadline"; stderr: string };

/**
 * Sends one `initialize` over stdio and settles on the reply, an exit or the deadline; it never rejects.
 * It settles only once the child has exited, so the caller can delete the child's working directory.
 */
function initialize(command: string, args: string[], cwd: string, env: NodeJS.ProcessEnv): Promise<Answer> {
  const child = spawn(command, args, { cwd, env, stdio: ["pipe", "pipe", "pipe"], windowsHide: true });
  let buffer = "";
  let stderr = "";
  let answer: Answer | null = null;
  return new Promise<Answer>((settle) => {
    const timer = setTimeout(() => done({ kind: "deadline", stderr: stderr.slice(-800) }), DEADLINE_MS);
    const done = (first: Answer) => {
      clearTimeout(timer);
      answer ??= first;
      if (child.exitCode !== null || child.signalCode !== null) settle(answer);
      else child.kill();
    };
    child.on("close", () => settle(answer ?? { kind: "exit", code: child.exitCode, stderr: stderr.slice(-800) }));
    child.stderr.on("data", (chunk: Buffer) => {
      stderr += chunk.toString("utf8");
    });
    child.stdout.on("data", (chunk: Buffer) => {
      buffer += chunk.toString("utf8");
      for (const line of buffer.split("\n").slice(0, -1)) {
        try {
          const message = JSON.parse(line) as { id?: number };
          if (message.id === 1) return done({ kind: "response", message });
        } catch {
          // Not JSON-RPC; the deadline or exit reports the missing response.
        }
      }
    });
    child.on("error", (error) => done({ kind: "exit", code: null, stderr: String(error) }));
    child.on("exit", (code) => done({ kind: "exit", code, stderr: stderr.slice(-800) }));
    child.stdin.write(
      `${JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "s31b-ac-92-1", version: "0" } },
      })}\n`,
    );
  });
}

describe("MEU-92 self-contained bundle (AC-92.1)", () => {
  it(
    "AC-92.1 bundle/index.mjs exists and a copy with no node_modules above it answers initialize as av-kit",
    async () => {
      expect(existsSync(path.join(bundleDir, "index.mjs")), "npm --prefix mcp-server run bundle").toBe(true);
      // The copy lives under the OS temp directory, so no repository node_modules is on its resolution path.
      const tmp = mkdtempSync(path.join(os.tmpdir(), "s31b-bundle-"));
      try {
        const copy = path.join(tmp, "mcp-server");
        cpSync(bundleDir, copy, { recursive: true });
        const appData = path.join(tmp, "appdata");
        mkdirSync(appData);
        const env: NodeJS.ProcessEnv = { ...process.env, AVKIT_APP_DATA: appData };
        delete env.AVKIT_API_TOKEN;
        delete env.AVKIT_API_BASE;
        delete env.NODE_PATH;
        const answer = await initialize(process.execPath, [path.join(copy, "index.mjs")], tmp, env);
        expect(answer.kind, JSON.stringify(answer)).toBe("response");
        const message = (answer as { message: { result?: { serverInfo?: { name?: string } } } }).message;
        expect(message.result?.serverInfo?.name).toBe("av-kit");
      } finally {
        rmSync(tmp, { recursive: true, force: true });
      }
    },
    DEADLINE_MS + 10_000,
  );
});

describe("MEU-92 PACKAGING_INPUTS and BUNDLE_SCRIPT (AC-92.3)", () => {
  it("AC-92.3 electron-builder.yml copies ../mcp-server/bundle to mcp-server and no longer names ../mcp-server/dist", () => {
    const yml = readFileSync(path.join(repoRoot, "ui", "electron-builder.yml"), "utf8");
    expect(yml).toMatch(/^\s*- from: \.\.\/mcp-server\/bundle\r?\n\s*to: mcp-server\s*$/m);
    expect(yml).not.toContain("../mcp-server/dist");
  });

  it("AC-92.3 ui dist:prep ends by building the bundle", () => {
    const pkg = JSON.parse(readFileSync(path.join(repoRoot, "ui", "package.json"), "utf8")) as {
      scripts?: Record<string, string>;
    };
    expect(pkg.scripts?.["dist:prep"]?.endsWith("&& npm --prefix ../mcp-server run bundle"), pkg.scripts?.["dist:prep"]).toBe(true);
  });

  it("AC-92.3 .gitignore ignores mcp-server/bundle/", () => {
    const lines = readFileSync(path.join(repoRoot, ".gitignore"), "utf8").split(/\r?\n/);
    expect(lines).toContain("mcp-server/bundle/");
  });

  it("AC-92.3 mcp-server package.json has the bundle script and esbuild pinned to exactly 0.28.2", () => {
    const pkg = JSON.parse(readFileSync(path.join(mcpRoot, "package.json"), "utf8")) as {
      scripts?: Record<string, string>;
      devDependencies?: Record<string, string>;
    };
    expect(pkg.scripts?.bundle).toBe("tsx scripts/bundle.ts");
    expect(pkg.devDependencies?.esbuild).toBe("0.28.2");
  });
});
