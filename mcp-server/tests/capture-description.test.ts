import { createHash } from "node:crypto";
import { describe, expect, it } from "vitest";
import { createServer } from "../src/index.js";
import { captureDescriptions } from "../src/toolsets/capture.js";
import { ACTION_INDEX } from "../src/toolsets/registry.js";

// Session 92 (D-1134 A, D-1157; MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL). The registered
// avkit_capture top-level description: the lead, the four markers once, then one line per action
// made only of that action's own sentences (DESC_TRACE). The other seven descriptions and the
// capture action text stay as they were at row 0.

type RegisteredTool = {
  description?: string;
  _meta?: { action_descriptions?: Record<string, string> };
};

function registeredTools(): Record<string, RegisteredTool> {
  const server = createServer();
  return (server as unknown as { _registeredTools: Record<string, RegisteredTool> })._registeredTools ?? {};
}

const LEAD =
  "Call image to view a frame or sheet. To zoom, call sheet again with a narrower start and end; no state is kept between calls.";
const ZOOM = "To zoom, call sheet again with a narrower start and end";
const MARKERS = ["Workflow:", "Prerequisite:", "Returns:", "Errors:"];
const ACTION_HEADS = ["image", "capture", "annotate", "flatten", "revert", "crop", "frames", "sheet", "export"];
const SENTENCE_SPLIT = /(?<=\.)\s+(?=[A-Z])/;

/** The row-0 SHA-256 of the other seven top-level descriptions (plan §Acceptance Criteria AC-10). */
const OTHER_SEVEN: Record<string, string> = {
  avkit_download: "c22a90eba581b02973d531d87ca02ac43fa5226e73ad4c890f01fa257c0496d8",
  avkit_transcript: "c6b3660065afdc2cc9f36021433c6ff4f1dcd6cd25c90e1137d2c01cbea01379",
  avkit_tts: "df5d6471a68ba7ed77c54b02db24929ded517cebfe3dd1d61596b78888af1ec7",
  avkit_models: "2345edcba75c2441a16c92340c70c7979cc0ee92b26a0cdbc7e69000c9bddf41",
  avkit_settings: "160dfcbbdcd118fd98e8ff890e0e58d5e157c964b209c1b7dbae1d4b4a4b2702",
  avkit_health: "4c49f8fc874d1ca8131c0fc4f998333bae5bef4c15834dfca71ff079d490583b",
  avkit_convert: "215e7640860933c37722ba8ab3e959efa8404903f5ca570867a716f2b18bbaaf",
};

function captureLines(): string[] {
  return (registeredTools().avkit_capture?.description ?? "").split("\n");
}

describe("Session 92 avkit_capture description", () => {
  it("AC-7 the description is under 4,096 characters, line 1 is the lead and it holds the zoom sentence", () => {
    const text = registeredTools().avkit_capture?.description ?? "";
    const lines = text.split("\n");
    expect(lines[0]).toBe(LEAD);
    expect(text).toContain(ZOOM);
    expect(text.length).toBeLessThan(4096);
  });

  it("AC-8 lines 2 to 5 start with the four markers and lines 6 to 14 with the nine actions in ACTION_INDEX order", () => {
    const lines = captureLines();
    expect(lines).toHaveLength(14);
    expect(lines.slice(1, 5).map((ln, i) => ln.startsWith(`${MARKERS[i]} `))).toEqual([true, true, true, true]);
    const elsewhere = lines.filter((ln, i) => (i < 1 || i > 4) && MARKERS.some((m) => ln.startsWith(m)));
    expect(elsewhere).toEqual([]);
    expect(lines.slice(5).map((ln) => ln.slice(0, ln.indexOf(": ")))).toEqual(ACTION_HEADS);
    const order = ACTION_INDEX.filter((r) => r.tool === "avkit_capture").map((r) => r.action);
    const positions = ACTION_HEADS.map((a) => order.indexOf(a));
    expect(positions.every((p) => p >= 0)).toBe(true);
    expect([...positions].sort((a, b) => a - b)).toEqual(positions);
  });

  it("AC-9 every sentence of lines 6 to 14 is in its action's registered _meta text (DESC_TRACE)", () => {
    const lines = captureLines();
    const actionLines = lines.slice(5);
    expect(actionLines).toHaveLength(ACTION_HEADS.length);
    const meta = registeredTools().avkit_capture?._meta?.action_descriptions ?? {};
    const missing: string[] = [];
    actionLines.forEach((line, i) => {
      const head = `${ACTION_HEADS[i]}: `;
      expect(line.startsWith(head)).toBe(true);
      const text = meta[ACTION_HEADS[i]] ?? "";
      for (const sentence of line.slice(head.length).split(SENTENCE_SPLIT)) {
        if (!text.includes(sentence)) missing.push(`${ACTION_HEADS[i]}: ${sentence}`);
      }
    });
    expect(missing).toEqual([]);
  });

  it("AC-10 the other seven descriptions keep their row-0 SHA-256", () => {
    const tools = registeredTools();
    const got = Object.fromEntries(
      Object.keys(OTHER_SEVEN).map((name) => [
        name,
        createHash("sha256")
          .update(tools[name]?.description ?? "", "utf8")
          .digest("hex"),
      ]),
    );
    expect(got).toEqual(OTHER_SEVEN);
  });

  it("AC-10 the registered capture _meta.action_descriptions equals captureDescriptions with bare keys", () => {
    const meta = registeredTools().avkit_capture?._meta?.action_descriptions;
    const bare = Object.fromEntries(
      Object.entries(captureDescriptions).map(([key, text]) => [key.replace(/^avkit_capture\./, ""), text]),
    );
    expect(meta).toEqual(bare);
  });
});
