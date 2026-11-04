import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { AUDIT_FIXTURES } from "../../scripts/audit/fixtures.js";
import { CleanupLedger } from "../../scripts/audit/ledger.js";
import { AUDIT_PLAN, type StepContext } from "../../scripts/audit/plan.js";

const temps: string[] = [];
afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

/** The variant row lists at once; each runtime read returns the next state, and the last one sticks. */
function scripted(runtime: Record<string, unknown>[]) {
  const root = mkdtempSync(path.join(os.tmpdir(), "s44-model-download-"));
  temps.push(root);
  const weights = path.join(root, "weights.onnx");
  writeFileSync(weights, "weights");
  let reads = 0;
  const ok = (json: unknown) => ({ status: 200, json, text: JSON.stringify(json) });
  const ctx: StepContext = {
    mode: "container",
    platform: "linux",
    fixtures: { ...AUDIT_FIXTURES } as unknown as StepContext["fixtures"],
    root,
    out: (sub) => path.join(root, "out", sub),
    call: async () => ({ isError: false, text: "" }),
    rest: {
      get: async (p) => {
        if (p === "/models/downloaded") return ok({ items: [{ id: "v1", is_downloaded: true, path: weights }] });
        if (p !== "/models/download-runtime") return { status: 404, json: null, text: "" };
        reads += 1;
        return ok(runtime[Math.min(reads, runtime.length) - 1]);
      },
      send: async () => ({ status: 404, json: null, text: "" }),
      bytes: async () => ({ status: 404, bytes: new Uint8Array() }),
    },
    ledger: new CleanupLedger(),
    state: new Map<string, unknown>([["variant_id", "v1"]]),
    firstId: () => null,
    poll: async (probe) => {
      for (let i = 0; i < 10; i += 1) {
        const value = await probe();
        if (value !== null) return value;
      }
      return null;
    },
  };
  return { ctx, reads: () => reads };
}

async function observe(ctx: StepContext) {
  const found = AUDIT_PLAN.find((s) => s.id === "models.download");
  if (!found) throw new Error("no step models.download");
  const outcome = await found.execute(ctx);
  if (outcome.kind !== "simple") throw new Error(`unexpected outcome ${JSON.stringify(outcome)}`);
  return outcome.observable;
}

describe("the audit's models.download step waits for the voice packs that follow the weights", () => {
  it("passes only after the runtime leaves Downloading", async () => {
    const s = scripted([{ state: "Downloading" }, { state: "Downloading" }, { state: "Idle" }]);
    const observable = await observe(s.ctx);
    expect(observable.ok).toBe(true);
    expect(s.reads()).toBe(3);
  });

  it("fails with the backend's error when the packs fail", async () => {
    const s = scripted([{ state: "Downloading" }, { state: "Failed", error_message: "voice pack af_heart failed" }]);
    const observable = await observe(s.ctx);
    expect(observable.ok).toBe(false);
    expect(observable.errorMessage).toBe("voice pack af_heart failed");
  });

  it("fails when the packs never finish", async () => {
    const s = scripted([{ state: "Downloading" }]);
    const observable = await observe(s.ctx);
    expect(observable.ok).toBe(false);
    expect(observable.detail).toContain("still downloading");
  });
});
