import path from "node:path";
import os from "node:os";
import { describe, expect, it } from "vitest";
import { refusalVerdict } from "../../scripts/audit/classify.js";
import { AUDIT_FIXTURES } from "../../scripts/audit/fixtures.js";
import { CleanupLedger } from "../../scripts/audit/ledger.js";
import { AUDIT_PLAN, destructiveStep, type StepContext, type StepOutcome } from "../../scripts/audit/plan.js";
import type { ToolCallOutcome } from "../../scripts/audit/types.js";

function step(id: string) {
  const found = AUDIT_PLAN.find((s) => s.id === id);
  if (!found) throw new Error(`no step ${id}`);
  return found;
}

/**
 * A scripted backend: POST /tts/generate creates `job<n>` with `postStatus`; a confirmed cancel
 * moves the job to `onConfirm(attempt)` (or leaves it). Refusals (no confirm, confirm:false) are
 * MCP errors that change nothing. `poll` evaluates its probe once.
 */
function scripted(opts: { postStatus?: string; onConfirm: (attempt: number) => string | null }) {
  const jobs = new Map<string, string>([["first", "Done"]]);
  const posts: Record<string, unknown>[] = [];
  const cancels: string[] = [];
  let confirms = 0;
  const ledger = new CleanupLedger();
  const state = new Map<string, unknown>([["tts_job1", "first"]]);
  const root = path.join(os.tmpdir(), "s33-tts-cancel-step");
  const call = async (_tool: string, args: Record<string, unknown>): Promise<ToolCallOutcome> => {
    if (args.confirm !== true) return { isError: true, text: '{"code":"confirm_required"}' };
    confirms += 1;
    const id = String(args.id);
    cancels.push(id);
    const next = opts.onConfirm(confirms);
    if (next !== null && jobs.has(id)) jobs.set(id, next);
    return { isError: false, text: "" };
  };
  const ctx: StepContext = {
    mode: "container",
    platform: "linux",
    fixtures: { ...AUDIT_FIXTURES } as unknown as StepContext["fixtures"],
    root,
    out: (sub) => path.join(root, "out", sub),
    call,
    rest: {
      get: async (p) => {
        const id = p.replace(/^\/tts\//, "");
        const status = jobs.get(id);
        if (status === undefined) return { status: 404, json: null, text: "" };
        const json = { id, status };
        return { status: 200, json, text: JSON.stringify(json) };
      },
      send: async (method, p, body) => {
        if (method !== "POST" || p !== "/tts/generate") return { status: 404, json: null, text: "" };
        posts.push(body as Record<string, unknown>);
        const id = `job${posts.length}`;
        jobs.set(id, opts.postStatus ?? "Generating");
        const json = { id, status: jobs.get(id) };
        return { status: 201, json, text: JSON.stringify(json) };
      },
      bytes: async () => ({ status: 404, bytes: new Uint8Array() }),
    },
    ledger,
    state,
    firstId: () => null,
    poll: async (probe) => probe(),
  };
  return { ctx, jobs, posts, cancels, ledger, state };
}

function destructive(outcome: StepOutcome) {
  if (outcome.kind !== "destructive") throw new Error(`unexpected outcome ${JSON.stringify(outcome)}`);
  return outcome;
}

describe("MEU-77 AC-77.13 audit tts.cancel targets a running job (AUDIT_CANCEL_STEP)", () => {
  it("AC-77.13 AUDIT_FIXTURES.tts_cancel_text is long enough to keep a job running", () => {
    expect("tts_cancel_text" in AUDIT_FIXTURES).toBe(true);
    const text = String((AUDIT_FIXTURES as Record<string, unknown>).tts_cancel_text);
    expect(text.length).toBeGreaterThanOrEqual(1500);
  });

  it("AC-77.13 (a) a Generating job cancelled on attempt 1 passes and is registered", async () => {
    const s = scripted({ onConfirm: () => "Cancelled" });
    const outcome = await step("tts.cancel").execute(s.ctx);
    expect(outcome.kind).toBe("destructive");
    const d = destructive(outcome);
    expect(refusalVerdict(d.refusal)).toEqual({ verdict: "pass", reason: null });
    expect(d.observable.detail).toContain("attempt 1/3");
    expect(s.posts).toHaveLength(1);
    expect(s.posts[0].text).toBe((AUDIT_FIXTURES as Record<string, unknown>).tts_cancel_text);
    expect(s.posts[0].voice).toBe(AUDIT_FIXTURES.tts_voice);
    expect("action" in s.posts[0]).toBe(false);
    expect(s.ledger.outstanding()).toContainEqual({ kind: "tts_job", id: "job1" });
    expect(s.state.get("tts_job2")).toBe("job1");
    expect(s.cancels).toEqual(["job1"]);
    expect(s.jobs.get("job1")).toBe("Cancelled");
  });

  it("AC-77.13 (b) a job that finishes first is retried and the second is cancelled", async () => {
    const s = scripted({ onConfirm: (attempt) => (attempt === 1 ? "Done" : "Cancelled") });
    const outcome = await step("tts.cancel").execute(s.ctx);
    expect(outcome.kind).toBe("destructive");
    const d = destructive(outcome);
    expect(refusalVerdict(d.refusal)).toEqual({ verdict: "pass", reason: null });
    expect(d.observable.detail).toContain("attempt 2/3");
    expect(s.posts).toHaveLength(2);
    expect(s.cancels).toEqual(["job1", "job2"]);
    expect(s.state.get("tts_job2")).toBe("job2");
  });

  it("AC-77.13 (c) every job finishing first is confirmed_no_effect after exactly 3 POSTs", async () => {
    const s = scripted({ onConfirm: () => "Done" });
    const outcome = await step("tts.cancel").execute(s.ctx);
    expect(outcome.kind).toBe("destructive");
    const d = destructive(outcome);
    expect(refusalVerdict(d.refusal)).toEqual({ verdict: "fail", reason: "confirmed_no_effect" });
    expect(d.observable.detail).toContain("attempt 3/3");
    expect(s.posts).toHaveLength(3);
  });

  it("AC-77.13 (d) a job still Generating after the effect poll is not retried", async () => {
    const s = scripted({ onConfirm: () => null });
    const outcome = await step("tts.cancel").execute(s.ctx);
    expect(outcome.kind).toBe("destructive");
    const d = destructive(outcome);
    expect(refusalVerdict(d.refusal)).toEqual({ verdict: "fail", reason: "confirmed_no_effect" });
    expect(s.posts).toHaveLength(1);
    expect(s.jobs.get("job1")).toBe("Generating");
  });

  it("AC-77.13 [neg] a POST that answers Done gives precondition_lost", async () => {
    const s = scripted({ postStatus: "Done", onConfirm: () => "Cancelled" });
    const outcome = await step("tts.cancel").execute(s.ctx);
    expect(outcome.kind).toBe("simple");
    expect(outcome.kind === "simple" ? outcome.reason : null).toBe("precondition_lost");
    expect(s.cancels).toEqual([]);
  });

  it("AC-77.13 [neg] a destructiveStep without attempts runs once and never calls raceLost", async () => {
    const s = scripted({ onConfirm: () => null });
    s.state.set("target", "job-x");
    s.jobs.set("job-x", "Generating");
    let raceCalls = 0;
    const single = destructiveStep({
      id: "probe.single",
      tool: "avkit_tts",
      action: "cancel",
      args: (ctx) => ({ action: "cancel", id: ctx.state.get("target") }),
      probe: async (ctx) => s.jobs.get(String(ctx.state.get("target"))) === "Cancelled",
      raceLost: async () => {
        raceCalls += 1;
        return true;
      },
    } as Parameters<typeof destructiveStep>[0]);
    const d = destructive(await single.execute(s.ctx));
    expect(refusalVerdict(d.refusal)).toEqual({ verdict: "fail", reason: "confirmed_no_effect" });
    expect(s.cancels).toEqual(["job-x"]);
    expect(raceCalls).toBe(0);
  });
});
