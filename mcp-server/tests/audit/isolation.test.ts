import path from "node:path";
import { describe, expect, it } from "vitest";
import { IsolationError, isolationGuard, isolationKeys, ISOLATION_INPUT_KEYS } from "../../scripts/audit/classify.js";
import { SETTINGS_SCHEMA } from "../../src/toolsets/settings.js";

const ROOT = path.resolve("/tmp/avkit-mcp-audit-test");
const OUT = (sub: string) => path.join(ROOT, "out", sub);

const MAPPING: Record<string, string> = {
  "downloader.path": OUT("downloads"),
  "transcript.output_dir": OUT("transcripts"),
  "tts.models_directory": OUT("models"),
  "tts.output_path": OUT("tts"),
  "converter.output_dir": OUT("convert"),
  "capture.inbox_dir": OUT("captures"),
  // TA-5 (Session 30, MEU-67): AUDIT_ISOLATION.
  "capture.backup_dir": OUT("capture_backups"),
};

function readBackFrom(mapping: Record<string, string>): Record<string, Record<string, unknown>> {
  const out: Record<string, Record<string, unknown>> = {};
  for (const [key, value] of Object.entries(mapping)) {
    const [ns, leaf] = key.split(".") as [string, string];
    out[ns] = { ...(out[ns] ?? {}), [leaf]: value };
  }
  return out;
}

describe("AC-68.8 ISOLATION_KEYS derivation", () => {
  it("AC-68.8 derives the seven output path keys structurally from the settings schema", () => {
    expect(isolationKeys(SETTINGS_SCHEMA).sort()).toEqual(Object.keys(MAPPING).sort());
  });

  it("AC-68.8 ffmpeg_path and cookie_file_path are inputs, never isolation targets", () => {
    expect([...ISOLATION_INPUT_KEYS].sort()).toEqual(["downloader.cookie_file_path", "downloader.ffmpeg_path"]);
    expect(isolationKeys(SETTINGS_SCHEMA)).not.toContain("downloader.ffmpeg_path");
  });
});

describe("AC-68.8 ISOLATION_GUARD", () => {
  it("AC-68.8 passes when every output path resolves under the isolated root", () => {
    const out = isolationGuard({ schema: SETTINGS_SCHEMA, mapping: MAPPING, readBack: readBackFrom(MAPPING), root: ROOT });
    expect(out.ok).toBe(true);
    expect(Object.keys(out.paths).sort()).toEqual(Object.keys(MAPPING).sort());
  });

  it("AC-68.8 throws when one read-back path is outside the root", () => {
    const readBack = readBackFrom({ ...MAPPING, "tts.output_path": "~/Documents" });
    expect(() => isolationGuard({ schema: SETTINGS_SCHEMA, mapping: MAPPING, readBack, root: ROOT }))
      .toThrow(IsolationError);
  });

  it("AC-68.8 a sibling directory sharing the root prefix is outside the root", () => {
    const readBack = readBackFrom({ ...MAPPING, "capture.inbox_dir": `${ROOT}-evil/captures` });
    expect(() => isolationGuard({ schema: SETTINGS_SCHEMA, mapping: MAPPING, readBack, root: ROOT }))
      .toThrow(IsolationError);
  });

  it("AC-68.8 a schema with an extra unmapped *_dir key fails closed", () => {
    const schema = {
      namespaces: {
        ...SETTINGS_SCHEMA.namespaces,
        app: { ...SETTINGS_SCHEMA.namespaces.app, cache_dir: { type: "string", default: "~/.cache" } },
      },
    };
    expect(() => isolationGuard({ schema, mapping: MAPPING, readBack: readBackFrom(MAPPING), root: ROOT }))
      .toThrow(/app\.cache_dir/);
  });

  it("AC-68.8 a missing read-back value fails closed", () => {
    const partial = { ...MAPPING };
    delete partial["converter.output_dir"];
    expect(() => isolationGuard({ schema: SETTINGS_SCHEMA, mapping: MAPPING, readBack: readBackFrom(partial), root: ROOT }))
      .toThrow(IsolationError);
  });
});
