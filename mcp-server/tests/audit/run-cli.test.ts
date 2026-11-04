import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ALLOWED_PASSTHROUGH_ENV, buildLaunch } from "../../scripts/audit/client.js";
import { CliError, main, parseCli, runAudit } from "../../scripts/audit/run.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SCRIPTS = path.resolve(HERE, "../../scripts");
const PATTERNS = readFileSync(path.join(HERE, "forbidden-imports.txt"), "utf8")
  .split("\n")
  .map((l) => l.trim())
  .filter(Boolean);

/** Same check as validate-task.sh `scope` (rg -f forbidden-imports.txt), over every file under dir. */
function forbiddenHits(dir: string): string[] {
  const hits: string[] = [];
  for (const name of readdirSync(dir)) {
    const full = path.join(dir, name);
    if (statSync(full).isDirectory()) {
      hits.push(...forbiddenHits(full));
      continue;
    }
    const text = readFileSync(full, "utf8");
    for (const pattern of PATTERNS) if (text.includes(pattern)) hits.push(`${full}: ${pattern}`);
  }
  return hits;
}

const temps: string[] = [];
afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("AC-68.12 CLI parsing fails closed", () => {
  it("AC-68.12 a valid container invocation parses", () => {
    const opts = parseCli(["--mode", "container", "--no-baseline", "--out", "/tmp/x", "--agent", "a"]);
    expect(opts.mode).toBe("container");
    expect(opts.noBaseline).toBe(true);
    expect(opts.out).toBe(path.resolve("/tmp/x"));
  });

  it("AC-68.12 an unknown flag is a CliError with exit 4", () => {
    expect(() => parseCli(["--mode", "container", "--no-baseline", "--frobnicate"])).toThrow(CliError);
    try {
      parseCli(["--mode", "container", "--frobnicate"]);
    } catch (err) {
      expect((err as CliError).exitCode).toBe(4);
    }
  });

  it("AC-68.12 a missing or invalid --mode is rejected", () => {
    expect(() => parseCli(["--no-baseline"])).toThrow(/--mode/);
    expect(() => parseCli(["--mode", "everything", "--no-baseline"])).toThrow(/--mode/);
  });

  it("AC-68.12 --update-baseline needs --baseline", () => {
    expect(() => parseCli(["--mode", "authoritative", "--no-baseline", "--update-baseline"])).toThrow(/--baseline/);
  });

  it("AC-68.12 neither --baseline nor --no-baseline is an error (a missing baseline is never empty)", () => {
    expect(() => parseCli(["--mode", "container"])).toThrow(/--no-baseline/);
  });

  it("AC-68.12 main returns 4 for an unknown flag and never launches a backend", async () => {
    const launcher = vi.fn();
    const code = await main(["--mode", "container", "--no-baseline", "--bogus"], { launcher });
    expect(code).toBe(4);
    expect(launcher).not.toHaveBeenCalled();
  });
});

describe("AC-68.1 MCP_LAUNCH env shape", () => {
  it("AC-68.1 passes exactly the copyMcpConfig keys plus allowed OS keys", () => {
    const launch = buildLaunch({
      serverPath: "/repo/mcp-server/dist/index.js",
      token: "tok",
      appData: "/tmp/root/app-data",
      parentEnv: { PATH: "/bin", HOME: "/root", AVKIT_API_BASE: "http://evil/api/v1", SECRET: "x", AVKIT_E2E_OUT_DIR: "y" },
    });
    expect(launch.command).toBe("node");
    expect(launch.args).toEqual(["/repo/mcp-server/dist/index.js"]);
    expect(Object.keys(launch.env).sort()).toEqual(["AVKIT_API_TOKEN", "AVKIT_APP_DATA", "HOME", "PATH"]);
    expect(launch.env.AVKIT_API_TOKEN).toBe("tok");
    expect(launch.env.AVKIT_APP_DATA).toBe("/tmp/root/app-data");
    expect(ALLOWED_PASSTHROUGH_ENV).toEqual(["PATH", "SystemRoot", "TEMP", "TMP", "HOME", "USERPROFILE"]);
  });
});

describe("AC-68.2 no in-process shortcut", () => {
  it("AC-68.2 the runner tree contains none of the forbidden imports", () => {
    expect(PATTERNS).toEqual(["src/toolsets", "dist/toolsets", "handleTool", "registerMcpSurface"]);
    expect(forbiddenHits(SCRIPTS)).toEqual([]);
  });

  it("AC-68.2 the check finds a seeded forbidden import", () => {
    const dir = mkdtempSync(path.join(os.tmpdir(), "s28-forbidden-"));
    temps.push(dir);
    writeFileSync(path.join(dir, "x.ts"), 'import { handleTool } from "../../src/toolsets/registry.js";\n');
    expect(forbiddenHits(dir).length).toBeGreaterThan(0);
  });
});

describe("AC-68.10 / AC-68.11 a missing baseline is never an empty one", () => {
  it("AC-68.11 --update-baseline with a missing --baseline exits 4, never launches and writes nothing", async () => {
    for (const [mode, platform] of [
      ["container", "linux"],
      ["authoritative", "win32"],
    ] as const) {
      const out = mkdtempSync(path.join(os.tmpdir(), "s28-missing-baseline-"));
      temps.push(out);
      const missing = path.join(out, "typo", "baseline-snapshot.json");
      const launcher = vi.fn(async () => {
        throw new Error("the backend must not be launched");
      });
      const { exitCode } = await runAudit(
        {
          mode,
          out,
          report: path.join(out, "report.md"),
          baseline: missing,
          noBaseline: false,
          updateBaseline: true,
          server: path.join(out, "unused.js"),
          discoveryOnly: true,
          keep: false,
          agent: "vitest",
          fixtures: {},
        },
        { launcher, platform },
      );
      expect(exitCode, mode).toBe(4);
      expect(launcher, mode).not.toHaveBeenCalled();
      expect(existsSync(missing), mode).toBe(false);
    }
  });
});
