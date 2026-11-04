import { mkdirSync, mkdtempSync, rmSync, symlinkSync, unlinkSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { isMainModule } from "../src/entry-guard.js";

let tmp: string;
let links: string[];

beforeEach(() => {
  tmp = mkdtempSync(path.join(os.tmpdir(), "s31b-entry-guard-"));
  links = [];
});

afterEach(() => {
  // Remove junctions first so the recursive delete never walks into a target.
  for (const link of links) {
    unlinkSync(link);
  }
  rmSync(tmp, { recursive: true, force: true });
});

function touch(...parts: string[]): string {
  const file = path.join(tmp, ...parts);
  mkdirSync(path.dirname(file), { recursive: true });
  writeFileSync(file, "export {};\n");
  return file;
}

function junction(target: string, ...parts: string[]): string {
  const link = path.join(tmp, ...parts);
  mkdirSync(path.dirname(link), { recursive: true });
  symlinkSync(target, link, "junction");
  links.push(link);
  return link;
}

/** The same path with its drive letter's case flipped (`C:\x` → `c:\x`). */
function flipDriveLetter(file: string): string {
  const first = file[0];
  const flipped = first === first.toUpperCase() ? first.toLowerCase() : first.toUpperCase();
  return flipped + file.slice(1);
}

describe("MEU-71 ENTRY_GUARD (AC-71.8)", () => {
  it("AC-71.8 isMainModule is true for the file's own path", () => {
    const file = touch("real", "index.mjs");
    expect(isMainModule(file, pathToFileURL(file).href)).toBe(true);
  });

  it("AC-71.8 isMainModule is true for a path through a directory junction to the file", () => {
    const file = touch("real", "index.mjs");
    const link = junction(path.dirname(file), "linked");
    expect(isMainModule(path.join(link, "index.mjs"), pathToFileURL(file).href)).toBe(true);
  });

  it("AC-71.8 a drive-letter case change matches on win32 (and is another path elsewhere)", () => {
    const file = touch("real", "index.mjs");
    const flipped = flipDriveLetter(file);
    if (process.platform === "win32") {
      expect(flipped).not.toBe(file);
      expect(isMainModule(flipped, pathToFileURL(file).href)).toBe(true);
    } else {
      // POSIX paths start with "/", so the flip is a no-op and the file matches itself.
      expect(flipped).toBe(file);
      expect(isMainModule(flipped, pathToFileURL(file).href)).toBe(true);
    }
  });

  it("AC-71.8 isMainModule is true for the packaged layout <tmp>/resources/mcp-server/index.mjs", () => {
    const file = touch("resources", "mcp-server", "index.mjs");
    expect(isMainModule(file, pathToFileURL(file).href)).toBe(true);
  });

  it("AC-71.8 negative: another file, an undefined argv1 and a path that does not exist are false", () => {
    const file = touch("real", "index.mjs");
    const other = touch("real", "other.mjs");
    const url = pathToFileURL(file).href;
    expect(isMainModule(other, url)).toBe(false);
    expect(isMainModule(undefined, url)).toBe(false);
    expect(isMainModule(path.join(tmp, "real", "missing.mjs"), url)).toBe(false);
    expect(isMainModule(file, pathToFileURL(path.join(tmp, "real", "missing.mjs")).href)).toBe(false);
  });
});
