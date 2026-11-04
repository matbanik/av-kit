import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

/**
 * ENTRY_GUARD: true when `argv1` names this module's file, through any junction or symlink.
 * Node runs the main module from its realpath, so both sides are compared resolved; win32 paths ignore case.
 */
export function isMainModule(argv1: string | undefined, importMetaUrl: string): boolean {
  if (argv1 === undefined) return false;
  try {
    const entry = realpathSync.native(argv1);
    const self = realpathSync.native(fileURLToPath(importMetaUrl));
    return process.platform === "win32" ? entry.toLowerCase() === self.toLowerCase() : entry === self;
  } catch {
    return false;
  }
}
