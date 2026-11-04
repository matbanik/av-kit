import { mkdtempSync, rmSync } from "node:fs";
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
