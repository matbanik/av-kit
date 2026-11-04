/**
 * Isolated backend for the audit (H-2): the same argv Electron's dev spawn uses
 * (ui/src/main/python-manager.ts:16-35), with app-data under ISOLATED_ROOT. The interpreter is
 * resolved once through `uv run python` and then spawned directly, so stopping it stops the API
 * (no uv wrapper process left behind on Windows).
 */
import { spawn, spawnSync, type ChildProcess } from "node:child_process";
import { randomUUID } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export type BackendHandle = {
  apiBase: string;
  guiToken: string;
  mcpToken: string;
  appData: string;
  stop: () => Promise<{ exited: boolean }>;
};

/** Starts a backend whose app-data lives under `root` and writes backend.json there. */
export type BackendLauncher = (root: string) => Promise<BackendHandle>;

/** Repo root (scripts/audit → mcp-server → repo); `uv` must run here, not in mcp-server/. */
export const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");

const READY = /AVKIT_READY port=(\d+)/;
const READY_TIMEOUT_MS = 60_000;

function resolvePython(): string {
  const res = spawnSync("uv", ["run", "python", "-c", "import sys; print(sys.executable)"], {
    cwd: REPO_ROOT,
    encoding: "utf8",
    timeout: 120_000,
    // No shell: libuv resolves uv.exe on Windows, and a shell would break the -c quoting.
  });
  const exe = (res.stdout ?? "").trim().split(/\r?\n/).pop() ?? "";
  if (res.status !== 0 || !exe) throw new Error(`uv run python failed: ${res.error?.message ?? res.stderr}`);
  return exe;
}

function waitReady(child: ChildProcess, timeoutMs: number): Promise<number> {
  return new Promise((resolve, reject) => {
    let seen = "";
    const timer = setTimeout(() => reject(new Error(`backend not ready in ${timeoutMs} ms: ${seen.slice(-500)}`)), timeoutMs);
    const onData = (chunk: Buffer) => {
      seen += chunk.toString("utf8");
      const m = READY.exec(seen);
      if (m) {
        clearTimeout(timer);
        resolve(Number(m[1]));
      }
    };
    child.stdout?.on("data", onData);
    child.stderr?.on("data", (chunk: Buffer) => {
      seen += chunk.toString("utf8");
    });
    child.once("exit", (code) => {
      clearTimeout(timer);
      reject(new Error(`backend exited ${String(code)} before ready: ${seen.slice(-500)}`));
    });
  });
}

async function stopChild(child: ChildProcess, isExited: () => boolean): Promise<boolean> {
  if (isExited()) return true;
  child.kill();
  const deadline = Date.now() + 10_000;
  while (!isExited() && Date.now() < deadline) await new Promise((r) => setTimeout(r, 100));
  if (!isExited()) child.kill("SIGKILL");
  const hard = Date.now() + 5_000;
  while (!isExited() && Date.now() < hard) await new Promise((r) => setTimeout(r, 100));
  return isExited();
}

/**
 * Spawns `command args` with app-data under `root` and waits for AVKIT_READY. A process that
 * never reports ready is stopped before the error propagates: a live child would hold the
 * runner's event loop open (and the isolated root) after the run has already failed.
 */
export async function startBackendProcess(
  root: string,
  command: string,
  args: string[],
  readyTimeoutMs: number = READY_TIMEOUT_MS,
): Promise<{ child: ChildProcess; port: number; stop: () => Promise<{ exited: boolean }> }> {
  const appData = path.join(root, "app-data");
  mkdirSync(appData, { recursive: true });
  const child = spawn(command, args, {
    cwd: REPO_ROOT,
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, AVKIT_APP_DATA: appData },
  });
  let exited = false;
  child.once("exit", () => {
    exited = true;
  });
  let port: number;
  try {
    port = await waitReady(child, readyTimeoutMs);
  } catch (err) {
    const stopped = await stopChild(child, () => exited);
    const message = err instanceof Error ? err.message : String(err);
    throw new Error(`${message} (pid ${String(child.pid)} ${stopped ? "killed" : "still running"})`);
  }
  // Keep draining output so the backend never blocks on a full pipe.
  child.stdout?.resume();
  child.stderr?.resume();
  return { child, port, stop: async () => ({ exited: await stopChild(child, () => exited) }) };
}

/** Default launcher: the real `python -m avkit_api` on 127.0.0.1:0. */
export const spawnBackend: BackendLauncher = async (root) => {
  const appData = path.join(root, "app-data");
  mkdirSync(appData, { recursive: true });
  const guiToken = randomUUID();
  const mcpToken = randomUUID();
  // Electron provisions mcp-token.txt (ui/src/main/index.ts:155-163); the IDE config reads it.
  writeFileSync(path.join(appData, "mcp-token.txt"), mcpToken, "utf8");
  const python = resolvePython();
  const { port, stop } = await startBackendProcess(root, python, [
    "-m",
    "avkit_api",
    "--token",
    guiToken,
    "--mcp-token",
    mcpToken,
    "--port",
    "0",
    "--app-data",
    appData,
  ]);
  return { apiBase: `http://127.0.0.1:${port}/api/v1`, guiToken, mcpToken, appData, stop };
};
