import { describe, expect, it } from "vitest";
import { ENV_BOUND_AUDIT } from "../../scripts/audit/census.js";

const BOT_WALL_STRAIGHT = "ExtractError: ERROR: [youtube] x: Sign in to confirm you're not a bot";
const BOT_WALL_CURLY = "ExtractError: ERROR: [youtube] x: Sign in to confirm you’re not a bot";

function signature(key: string): RegExp {
  const member = ENV_BOUND_AUDIT.find((entry) => entry.key === key);
  expect(member, `census member ${key}`).toBeDefined();
  return member!.signature;
}

describe("AC-76.9 CENSUS_SIGNATURE", () => {
  it("AC-76.9 download and transcript add match the ExtractError bot wall with either apostrophe", () => {
    for (const key of ["avkit_download.add", "avkit_transcript.add"]) {
      expect(signature(key).test(BOT_WALL_STRAIGHT), `${key} straight apostrophe`).toBe(true);
      expect(signature(key).test(BOT_WALL_CURLY), `${key} curly apostrophe`).toBe(true);
    }
  });

  it("AC-76.9 [neg] add signatures reject a bare internal_error; capture still matches it", () => {
    for (const key of ["avkit_download.add", "avkit_transcript.add"]) {
      expect(signature(key).test("internal_error"), key).toBe(false);
    }
    expect(signature("avkit_capture.capture").test("internal_error")).toBe(true);
  });
});
