import { writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { build, type BuildOptions } from "esbuild";
import { isMainModule } from "../src/entry-guard.js";
import { collectLicenses, renderLicenses } from "./bundle-licenses.js";

const mcpRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

/** BUNDLE_SCRIPT: one ESM file with every dependency inlined; the banner gives CommonJS dependencies a `require`. */
export const BUNDLE_OPTIONS = {
  entryPoints: ["src/index.ts"],
  bundle: true,
  platform: "node",
  format: "esm",
  target: "node22",
  metafile: true,
  outfile: "bundle/index.mjs",
  banner: { js: "import { createRequire } from 'node:module'; const require = createRequire(import.meta.url);" },
} as const satisfies BuildOptions;

/** Writes bundle/index.mjs and bundle/LICENSES.txt; a dependency without a licence file fails the build. */
export async function bundle(): Promise<void> {
  const result = await build({ ...BUNDLE_OPTIONS, absWorkingDir: mcpRoot });
  const licences = renderLicenses(collectLicenses(result.metafile, mcpRoot));
  writeFileSync(path.join(mcpRoot, "bundle", "LICENSES.txt"), licences);
}

if (isMainModule(process.argv[1], import.meta.url)) {
  await bundle();
}
