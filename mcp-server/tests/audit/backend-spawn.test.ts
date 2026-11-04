import { mkdtempSync, rmSync } from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { startBackendProcess } from "../../scripts/audit/backend.js";

const temps: string[] = [];
afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

function alive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

describe("AC-68.9 a backend that never reports ready is stopped, not leaked", () => {
  it("AC-68.9 the ready timeout kills the child and names its pid", async () => {
    const root = mkdtempSync(path.join(os.tmpdir(), "s28-never-ready-"));
    temps.push(root);
    // A process that stays up and never prints AVKIT_READY (cross-platform: node itself).
    const err = await startBackendProcess(root, process.execPath, ["-e", "setInterval(() => {}, 1000)"], 300).then(
      () => null,
      (e: unknown) => e as Error,
    );
    expect(err?.message).toMatch(/not ready in 300 ms/);
    const pid = Number(/pid (\d+)/.exec(err?.message ?? "")?.[1]);
    expect(pid).toBeGreaterThan(0);
    expect(alive(pid)).toBe(false);
  });
});

function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address() as net.AddressInfo;
      server.close(() => resolve(port));
    });
  });
}

function accepts(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const socket = net.connect(port, "127.0.0.1");
    socket.once("connect", () => {
      socket.destroy();
      resolve(true);
    });
    socket.once("error", () => resolve(false));
  });
}

describe("the audit's first request can't beat the backend's socket", () => {
  it("waits for the port to accept after AVKIT_READY", async () => {
    const root = mkdtempSync(path.join(os.tmpdir(), "s44-ready-early-"));
    temps.push(root);
    const port = await freePort();
    // cli.py prints AVKIT_READY after binding and before uvicorn listens; this leaves a wider gap.
    const script = `console.log("AVKIT_READY port=${port} instance=x"); setTimeout(() => require("node:net").createServer().listen(${port}, "127.0.0.1"), 500);`;
    const backend = await startBackendProcess(root, process.execPath, ["-e", script], 10_000);
    try {
      expect(await accepts(port)).toBe(true);
    } finally {
      await backend.stop();
    }
  });

  it("stops a backend that reports ready and never accepts", async () => {
    const root = mkdtempSync(path.join(os.tmpdir(), "s44-ready-never-"));
    temps.push(root);
    const port = await freePort();
    const script = `console.log("AVKIT_READY port=${port} instance=x"); setInterval(() => {}, 1000);`;
    const err = await startBackendProcess(root, process.execPath, ["-e", script], 300).then(
      () => null,
      (e: unknown) => e as Error,
    );
    expect(err?.message).toMatch(new RegExp(`port ${port} refused connections for 300 ms`));
    const pid = Number(/pid (\d+)/.exec(err?.message ?? "")?.[1]);
    expect(pid).toBeGreaterThan(0);
    expect(alive(pid)).toBe(false);
  });
});
