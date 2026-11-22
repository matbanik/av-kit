import { describe, expect, it } from "vitest";
import { SETTINGS_SCHEMA } from "../src/toolsets/settings.js";

/**
 * MEU-163 (Session 101) TRANSCRIPT_DEFAULTS, AC-163.10's MCP half: the transcript defaults the MCP
 * settings schema ships are Mat's values (Mat 2026-11-21, D-1355).
 */

const MATS_VALUES: Record<string, number> = {
  requests_per_hour: 20,
  delay_between_requests: 120,
  max_retries: 1,
  retry_delay: 7,
  batch_size: 5,
  pause_between_batches: 500,
  playlist_end: 0,
  max_words_per_document: 490000,
};

describe("AC-163.10 the MCP settings schema ships the transcript defaults", () => {
  it("AC-163.10 each transcript number leaf defaults to Mat's value", () => {
    const transcript = SETTINGS_SCHEMA.namespaces.transcript ?? {};
    const found = Object.fromEntries(Object.keys(MATS_VALUES).map((key) => [key, transcript[key]]));
    const want = Object.fromEntries(
      Object.entries(MATS_VALUES).map(([key, value]) => [key, { type: "number", default: value }]),
    );
    expect(found).toEqual(want);
  });
});
