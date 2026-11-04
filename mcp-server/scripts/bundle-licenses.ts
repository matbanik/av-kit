import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";

export type LicenseSection = { name: string; version: string; license: string; text: string };

const LICENCE_FILE = /^(?:LICEN[CS]E|COPYING)/i;
// The package an input comes from: the last `node_modules/<name>/` in its path, scoped names included.
const PACKAGE_INPUT = /^(.*(?:^|\/)node_modules\/((?:@[^/]+\/)?[^/]+))\/(?!.*\/node_modules\/)/;

/** One section per `node_modules` package the bundle inlines, sorted by name, from an esbuild metafile. */
export function collectLicenses(metafile: { inputs: Record<string, unknown> }, root: string): LicenseSection[] {
  const packageDirs = new Map<string, string>();
  for (const input of Object.keys(metafile.inputs)) {
    const match = PACKAGE_INPUT.exec(input.replaceAll("\\", "/"));
    if (match !== null) packageDirs.set(match[1], match[2]);
  }
  const sections: LicenseSection[] = [];
  for (const [dir, name] of packageDirs) {
    const absolute = path.resolve(root, dir);
    const pkg = JSON.parse(readFileSync(path.join(absolute, "package.json"), "utf8")) as {
      version?: string;
      license?: string;
    };
    const licenceFile = readdirSync(absolute).sort().find((file) => LICENCE_FILE.test(file));
    if (licenceFile === undefined) throw new Error(`no licence file for ${name}`);
    sections.push({
      name,
      version: pkg.version ?? "",
      license: pkg.license ?? "",
      text: readFileSync(path.join(absolute, licenceFile), "utf8"),
    });
  }
  return sections.sort((a, b) => (a.name === b.name ? cmp(a.version, b.version) : cmp(a.name, b.name)));
}

function cmp(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

/** LICENSES.txt: a `<name>@<version> (<licence>)` heading line per package, then its licence text. */
export function renderLicenses(sections: LicenseSection[]): string {
  const rule = "=".repeat(78);
  const parts = sections.map(
    (s) => `${rule}\n${s.name}@${s.version} (${s.license})\n${rule}\n\n${s.text.replaceAll("\r\n", "\n").trimEnd()}\n`,
  );
  return `Third-party software inlined into index.mjs by esbuild.\n\n${parts.join("\n")}`;
}
