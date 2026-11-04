import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "esbuild";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { collectLicenses } from "../scripts/bundle-licenses.js";
import { BUNDLE_OPTIONS } from "../scripts/bundle.js";

const mcpRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

let root: string;

/** Writes `node_modules/<name>` with a package.json and, when given, one licence file. */
function fixturePackage(name: string, version: string, license: string, licenceFile?: [string, string]): void {
  const dir = path.join(root, "node_modules", ...name.split("/"));
  mkdirSync(dir, { recursive: true });
  writeFileSync(path.join(dir, "package.json"), JSON.stringify({ name, version, license }));
  if (licenceFile !== undefined) writeFileSync(path.join(dir, licenceFile[0]), licenceFile[1]);
}

/** The package names a metafile's inputs come from (the last `node_modules/` segment, scoped names included). */
function packagesIn(inputs: Record<string, unknown>): string[] {
  const names = new Set<string>();
  for (const input of Object.keys(inputs)) {
    const match = /(?:^|\/)node_modules\/((?:@[^/]+\/)?[^/]+)\/(?!.*\/node_modules\/)/.exec(input);
    if (match !== null) names.add(match[1]);
  }
  return [...names].sort();
}

beforeEach(() => {
  root = mkdtempSync(path.join(os.tmpdir(), "s31b-bundle-licenses-"));
});

afterEach(() => {
  rmSync(root, { recursive: true, force: true });
});

describe("MEU-92 BUNDLE_LICENSES (AC-92.2)", () => {
  it("AC-92.2 collectLicenses returns one section per node_modules package, sorted, with name, version, licence id and text", () => {
    fixturePackage("zeta-pkg", "3.0.1", "ISC", ["LICENSE", "zeta licence text\n"]);
    fixturePackage("@scope/beta", "2.1.0", "Apache-2.0", ["LICENCE.md", "beta licence text\n"]);
    fixturePackage("alpha", "1.0.0", "MIT", ["COPYING", "alpha licence text\n"]);
    const metafile = {
      inputs: {
        "src/index.ts": { bytes: 1, imports: [] },
        "node_modules/alpha/lib/a.js": { bytes: 1, imports: [] },
        "node_modules/zeta-pkg/index.js": { bytes: 1, imports: [] },
        "node_modules/@scope/beta/dist/beta.js": { bytes: 1, imports: [] },
        "node_modules/alpha/lib/b.js": { bytes: 1, imports: [] },
      },
      outputs: {},
    };

    const sections = collectLicenses(metafile, root);

    expect(sections).toEqual([
      { name: "@scope/beta", version: "2.1.0", license: "Apache-2.0", text: "beta licence text\n" },
      { name: "alpha", version: "1.0.0", license: "MIT", text: "alpha licence text\n" },
      { name: "zeta-pkg", version: "3.0.1", license: "ISC", text: "zeta licence text\n" },
    ]);
  });

  it("AC-92.2 a package with no licence file throws no licence file for <name>", () => {
    fixturePackage("alpha", "1.0.0", "MIT", ["LICENSE", "alpha licence text\n"]);
    fixturePackage("bare-pkg", "0.1.0", "MIT");
    const metafile = {
      inputs: {
        "node_modules/alpha/index.js": { bytes: 1, imports: [] },
        "node_modules/bare-pkg/index.js": { bytes: 1, imports: [] },
      },
      outputs: {},
    };

    expect(() => collectLicenses(metafile, root)).toThrow("no licence file for bare-pkg");
  });

  it("AC-92.2 bundle/LICENSES.txt names every package in the real build's metafile", async () => {
    const result = await build({ ...BUNDLE_OPTIONS, absWorkingDir: mcpRoot, write: false });
    const packages = packagesIn(result.metafile.inputs);
    expect(packages.length).toBeGreaterThan(0);
    const licences = readFileSync(path.join(mcpRoot, "bundle", "LICENSES.txt"), "utf8");
    for (const name of packages) {
      expect(licences, name).toMatch(new RegExp(`^${name.replace(/[.*+?^${}()|[\]\\/]/g, "\\$&")}@`, "m"));
    }
  });
});
