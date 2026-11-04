import { describe, expect, it } from "vitest";
import { stepVerdict } from "../../scripts/audit/classify.js";
import { AUDIT_FIXTURES } from "../../scripts/audit/fixtures.js";
import { CleanupLedger } from "../../scripts/audit/ledger.js";
import { AUDIT_IMAGE_CAP, AUDIT_PLAN, type StepContext } from "../../scripts/audit/plan.js";
import type { ToolCallOutcome } from "../../scripts/audit/types.js";
import { IMAGE_MAX_BYTES } from "../../src/toolsets/capture.js";

const CAP = 7_800_000;
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const REFUSAL: ToolCallOutcome = {
  isError: true,
  text: "payload_too_large: image exceeds the 7,800,000 B MCP limit; read original_path or annotated_path",
};
const LOST_CONNECTION: ToolCallOutcome = { isError: true, text: "MCP error -32000: Connection closed" };

function pngOf(size: number): Uint8Array {
  const body = Buffer.alloc(size, 0xab);
  PNG_SIGNATURE.copy(body);
  return new Uint8Array(body);
}

function contextWith(call: ToolCallOutcome, rest: { status: number; bytes: Uint8Array }): StepContext {
  return {
    mode: "container",
    platform: "linux",
    fixtures: { ...AUDIT_FIXTURES } as unknown as StepContext["fixtures"],
    root: "unused",
    out: (sub) => `unused/${sub}`,
    call: async () => call,
    rest: {
      get: async () => ({ status: 404, json: null, text: "" }),
      send: async () => ({ status: 404, json: null, text: "" }),
      bytes: async () => rest,
    },
    ledger: new CleanupLedger(),
    state: new Map<string, unknown>([["shot_id", "s1"]]),
    firstId: () => null,
    poll: async () => null,
  };
}

/** Through the runner's own classifier: a step can observe the right thing and still fail on isError. */
async function verdictOf(stepId: string, call: ToolCallOutcome, rest: { status: number; bytes: Uint8Array }) {
  const step = AUDIT_PLAN.find((candidate) => candidate.id === stepId);
  if (!step) throw new Error(`no audit step ${stepId}`);
  const outcome = await step.execute(contextWith(call, rest));
  if (outcome.kind !== "simple") throw new Error(`${stepId} returned ${outcome.kind}`);
  return stepVerdict({ expectError: outcome.expectError, isError: outcome.isError, observable: outcome.observable }).verdict;
}

describe("MEU-111 the audit's own copy of the cap", () => {
  it("AC-111.4 matches the server's cap, which the runner may not import (AC-68.2)", () => {
    expect(AUDIT_IMAGE_CAP).toBe(CAP);
    expect(IMAGE_MAX_BYTES).toBe(CAP);
  });
});

describe.each(["capture.image", "capture.image.annotated"])("MEU-111 audit step %s", (stepId) => {
  it("AC-111.4 the refusal passes when REST's image is larger than the cap", async () => {
    expect(await verdictOf(stepId, REFUSAL, { status: 200, bytes: pngOf(CAP + 1) })).toBe("pass");
  });

  it("AC-111.4 the refusal fails when REST's image is exactly the cap", async () => {
    expect(await verdictOf(stepId, REFUSAL, { status: 200, bytes: pngOf(CAP) })).toBe("fail");
  });

  it("AC-111.4 the refusal fails when REST has no image to measure", async () => {
    expect(await verdictOf(stepId, REFUSAL, { status: 404, bytes: pngOf(CAP + 1) })).toBe("fail");
  });

  it("AC-111.4 a lost connection fails even when REST's image is larger than the cap", async () => {
    expect(await verdictOf(stepId, LOST_CONNECTION, { status: 200, bytes: pngOf(CAP + 1) })).toBe("fail");
  });

  it("AC-111.4 an intact image equal to REST's still passes", async () => {
    const bytes = pngOf(1_024);
    const intact: ToolCallOutcome = {
      isError: false,
      text: "",
      image: { data: Buffer.from(bytes).toString("base64"), mimeType: "image/png" },
    };
    expect(await verdictOf(stepId, intact, { status: 200, bytes })).toBe("pass");
  });
});
