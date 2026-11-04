import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { createServer, SERVER_INSTRUCTIONS } from "../src/index.js";

const srcRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../src");

describe("hexagonal", () => {
  it("does not import sqlite, yt-dlp, or avkit packages from src", () => {
    const files = ["config.ts", "client.ts", "index.ts"];
    const banned = /sqlalchemy|yt_dlp|youtube_transcript_api|avkit_infra|avkit_core|better-sqlite|from ['"]sqlite3['"]/;
    for (const file of files) {
      const text = readFileSync(path.join(srcRoot, file), "utf8");
      expect(text, file).not.toMatch(banned);
    }
  });
});

describe("TRANSPORT / SERVER_INSTRUCTIONS", () => {
  it("constructs an MCP server with required instruction bullets", () => {
    const server = createServer();
    expect(server).toBeDefined();
    expect(SERVER_INSTRUCTIONS).toContain("Never upload or write to YouTube");
    expect(SERVER_INSTRUCTIONS).toContain("avkit_download add");
    expect(SERVER_INSTRUCTIONS).toContain("confirm: true");
    expect(SERVER_INSTRUCTIONS).toContain("leaf keys");
  });
});

// MEU-71 SETUP_INSTRUCTION (AC-71.12): appended as the last line; the earlier lines stay as they were.
const SETUP_INSTRUCTION = "Setup: the desktop app's Settings → MCP card shows a per-client setup prompt.";
const PRIOR_INSTRUCTION_LINES = [
  "av-kit is a local YouTube read/consume toolkit. Never upload or write to YouTube.",
  "Downloads: avkit_download add → start → list until processor Idle. Pause is queue-level; items have no Paused status.",
  "Transcripts: add channel → start → get. Output is files (output_dir); tools return paths and counts, not transcript text.",
  "TTS: load a model first; prepare is preview only; generate returns the job at once; poll get; cancel stops a running job.",
  "Destructive actions require confirm: true. Download, transcript and convert remove/clear keep files on disk. Capture remove deletes the shot's files; capture flatten overwrites the image file (after a backup when capture.flatten_backup is on; a JPEG/WebP shot gets a new PNG copy instead); capture revert overwrites it from its newest backup. These three capture actions also ask the user in the IDE and are refused unless the user accepts; call them only when the user explicitly asked.",
  "Convert is local files only; never upload YouTube.",
  "Capture is local screen plus local inbox files; never upload YouTube. capture_interactive needs the desktop app overlay.",
  "Settings use leaf keys (quality, not downloader.quality) and namespace.",
];

describe("MEU-71 SETUP_INSTRUCTION (AC-71.12)", () => {
  it("AC-71.12 SERVER_INSTRUCTIONS ends with SETUP_INSTRUCTION", () => {
    const lines = SERVER_INSTRUCTIONS.split("\n");
    expect(lines[lines.length - 1]).toBe(SETUP_INSTRUCTION);
  });

  it("AC-71.12 negative: the earlier lines are unchanged and in order (append-only)", () => {
    const lines = SERVER_INSTRUCTIONS.split("\n");
    expect(lines.slice(0, PRIOR_INSTRUCTION_LINES.length)).toEqual(PRIOR_INSTRUCTION_LINES);
    expect(lines).toHaveLength(PRIOR_INSTRUCTION_LINES.length + 1);
  });
});
