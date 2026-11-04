import { describe, expect, it } from "vitest";
import {
  applyTolerance,
  classifyDiscovery,
  countedFailures,
  exitCode,
  refusalVerdict,
  stepVerdict,
  type CensusMember,
} from "../../scripts/audit/classify.js";
import type { Baseline, StepRecord } from "../../scripts/audit/types.js";

const TOOLS = ["avkit_a", "avkit_b"] as const;

function record(partial: Partial<StepRecord> & Pick<StepRecord, "id" | "tool" | "action" | "verdict">): StepRecord {
  return {
    phase: "lifecycle",
    reason: null,
    is_error: false,
    observable: null,
    error: null,
    blocked_by: null,
    env_bound: null,
    ms: 1,
    ...partial,
  };
}

function baselineOf(keys: string[]): Baseline {
  return {
    schema: "mcp-audit-baseline.v1",
    recorded_commit: "a".repeat(40),
    mode: "authoritative",
    recorded_at: "2026-10-01T00:00:00Z",
    entries: keys.map((k) => {
      const [tool, action] = k.split(".") as [string, string];
      return { tool, action, status: "pass" as const };
    }),
    findings: [],
  };
}

describe("AC-68.6 OBSERVABLE_RULE step verdict", () => {
  it("AC-68.6 passes only when the call matches expectation and the observable holds", () => {
    expect(stepVerdict({ expectError: false, isError: false, observable: { ok: true, detail: "row Queued" } }))
      .toEqual({ verdict: "pass", reason: null });
  });

  it("AC-68.6 an MCP success whose observable fails is hollow", () => {
    expect(stepVerdict({ expectError: false, isError: false, observable: { ok: false, detail: "GET 404" } }))
      .toEqual({ verdict: "fail", reason: "hollow" });
  });

  it("AC-68.6 the envelope alone never passes (missing observable)", () => {
    expect(stepVerdict({ expectError: false, isError: false, observable: null }))
      .toEqual({ verdict: "fail", reason: "no_observable" });
  });

  it("AC-68.6 an unexpected tool error fails", () => {
    expect(stepVerdict({ expectError: false, isError: true, observable: { ok: true, detail: "x" } }))
      .toEqual({ verdict: "fail", reason: "unexpected_error" });
  });

  it("AC-68.6 an expected error that does not arrive fails", () => {
    expect(stepVerdict({ expectError: true, isError: false, observable: { ok: true, detail: "x" } }))
      .toEqual({ verdict: "fail", reason: "expected_error_missing" });
  });
});

describe("AC-68.7 REFUSAL_ORACLE verdict", () => {
  const probe = (isError: boolean, changed: boolean) => ({ isError, changed, text: "Input validation error" });

  it("AC-68.7 passes when both refusals error without change and confirm changes state", () => {
    expect(refusalVerdict({
      refusal_omit: probe(true, false),
      refusal_false: probe(true, false),
      confirmed: { isError: false, changed: true },
    })).toEqual({ verdict: "pass", reason: null });
  });

  it("AC-68.7 a refusal that mutated state fails as refusal_mutated", () => {
    expect(refusalVerdict({
      refusal_omit: probe(true, true),
      refusal_false: probe(true, false),
      confirmed: { isError: false, changed: true },
    })).toEqual({ verdict: "fail", reason: "refusal_mutated" });
  });

  it("AC-68.7 a destructive call accepted without confirm fails as refusal_missing", () => {
    expect(refusalVerdict({
      refusal_omit: probe(true, false),
      refusal_false: probe(false, false),
      confirmed: { isError: false, changed: true },
    })).toEqual({ verdict: "fail", reason: "refusal_missing" });
  });

  it("AC-68.7 a confirmed call with no effect fails", () => {
    expect(refusalVerdict({
      refusal_omit: probe(true, false),
      refusal_false: probe(true, false),
      confirmed: { isError: false, changed: false },
    })).toEqual({ verdict: "fail", reason: "confirmed_no_effect" });
  });
});

describe("AC-68.3 discovery classification", () => {
  const served = (name: string, actions: string[], schemaActions: string[] | null = actions) => ({
    name,
    schemaActions,
    metaActions: actions,
  });

  it("AC-68.3 served-not-baselined actions are NEW and not findings", () => {
    const out = classifyDiscovery({
      tools: [served("avkit_a", ["x", "y"]), served("avkit_b", ["z"])],
      expectedTools: TOOLS,
      baseline: baselineOf(["avkit_a.x", "avkit_b.z"]),
      ghosts: [],
    });
    expect(out.new).toEqual(["avkit_a.y"]);
    expect(out.findings).toEqual([]);
    expect(out.status).toBe("pass");
    expect(out.actions).toBe(3);
  });

  it("AC-68.3 baselined-not-served actions are REMOVED findings", () => {
    const out = classifyDiscovery({
      tools: [served("avkit_a", ["x"]), served("avkit_b", ["z"])],
      expectedTools: TOOLS,
      baseline: baselineOf(["avkit_a.x", "avkit_a.gone", "avkit_b.z"]),
      ghosts: [],
    });
    expect(out.removed).toEqual(["avkit_a.gone"]);
    expect(out.findings.map((f) => f.code)).toContain("removed_action");
    expect(out.status).toBe("fail");
  });

  it("AC-68.3 served actions whose call is unknown are GHOST findings", () => {
    const out = classifyDiscovery({
      tools: [served("avkit_a", ["x"]), served("avkit_b", ["z"])],
      expectedTools: TOOLS,
      baseline: null,
      ghosts: ["avkit_b.z"],
    });
    expect(out.ghost).toEqual(["avkit_b.z"]);
    expect(out.findings.map((f) => f.code)).toEqual(["ghost_action"]);
  });

  it("AC-68.3 an inputSchema that does not advertise the actions is a finding", () => {
    const out = classifyDiscovery({
      tools: [served("avkit_a", ["x"], null), served("avkit_b", ["z"])],
      expectedTools: TOOLS,
      baseline: null,
      ghosts: [],
    });
    expect(out.findings).toEqual([
      expect.objectContaining({ code: "schema_not_advertised", tool: "avkit_a" }),
    ]);
    expect(out.status).toBe("fail");
  });

  it("AC-68.3 schema literals disagreeing with _meta keys is a finding", () => {
    const out = classifyDiscovery({
      tools: [served("avkit_a", ["x", "y"], ["x"]), served("avkit_b", ["z"])],
      expectedTools: TOOLS,
      baseline: null,
      ghosts: [],
    });
    expect(out.findings.map((f) => f.code)).toEqual(["schema_meta_disagree"]);
  });

  it("AC-68.4 an unexpected 9th tool and a missing tool are findings", () => {
    const out = classifyDiscovery({
      tools: [served("avkit_a", ["x"]), served("avkit_extra", ["q"])],
      expectedTools: TOOLS,
      baseline: null,
      ghosts: [],
    });
    const codes = out.findings.map((f) => `${f.code}:${f.tool}`).sort();
    expect(codes).toEqual(["missing_tool:avkit_b", "unexpected_tool:avkit_extra"]);
    expect(out.tools).toBe(2);
  });
});

describe("AC-68.12 fail-closed tolerance", () => {
  const census: CensusMember[] = [
    {
      key: "avkit_capture.capture",
      signature: /screen capture requires Windows/,
      envProof: (env) => env.platform !== "win32",
    },
  ];
  const linux = { platform: "linux" };

  it("AC-68.12 a census member with matching signature and proof becomes skip_env in container mode", () => {
    const out = applyTolerance(
      [record({ id: "c1", tool: "avkit_capture", action: "capture", verdict: "fail", error: "screen capture requires Windows" })],
      "container",
      census,
      linux,
    );
    expect(out[0].verdict).toBe("skip_env");
    expect(out[0].env_bound).toEqual({ member: true, signature_matched: true, env_proof: true });
    expect(countedFailures(out, "container")).toEqual([]);
  });

  it("AC-68.12 a member whose text does not match stays a failure", () => {
    const out = applyTolerance(
      [record({ id: "c1", tool: "avkit_capture", action: "capture", verdict: "fail", error: "boom" })],
      "container",
      census,
      linux,
    );
    expect(out[0].verdict).toBe("fail");
    expect(countedFailures(out, "container").map((r) => r.id)).toEqual(["c1"]);
  });

  it("AC-68.12 a non-member with matching text stays a failure", () => {
    const out = applyTolerance(
      [record({ id: "d1", tool: "avkit_download", action: "add", verdict: "fail", error: "screen capture requires Windows" })],
      "container",
      census,
      linux,
    );
    expect(out[0].verdict).toBe("fail");
  });

  it("AC-68.12 a member without its environment proof stays a failure", () => {
    const out = applyTolerance(
      [record({ id: "c1", tool: "avkit_capture", action: "capture", verdict: "fail", error: "screen capture requires Windows" })],
      "container",
      census,
      { platform: "win32" },
    );
    expect(out[0].verdict).toBe("fail");
  });

  it("AC-68.12 authoritative mode never tolerates a census member", () => {
    const out = applyTolerance(
      [record({ id: "c1", tool: "avkit_capture", action: "capture", verdict: "fail", error: "screen capture requires Windows" })],
      "authoritative",
      census,
      linux,
    );
    expect(out[0].verdict).toBe("fail");
    expect(countedFailures(out, "authoritative")).toHaveLength(1);
  });

  it("AC-68.12 blocked is tolerated only beneath a tolerated step", () => {
    const steps = [
      record({ id: "c1", tool: "avkit_capture", action: "capture", verdict: "fail", error: "screen capture requires Windows" }),
      record({ id: "c2", tool: "avkit_capture", action: "get", verdict: "blocked", blocked_by: "c1" }),
      record({ id: "d1", tool: "avkit_download", action: "add", verdict: "fail", error: "boom" }),
      record({ id: "d2", tool: "avkit_download", action: "get", verdict: "blocked", blocked_by: "d1" }),
    ];
    const out = applyTolerance(steps, "container", census, linux);
    expect(countedFailures(out, "container").map((r) => r.id).sort()).toEqual(["d1", "d2"]);
  });

  it("AC-68.12 exit codes: runner error 4, isolation 3, baseline 2, failures or findings 1, else 0", () => {
    const base = { runnerError: false, isolationRefused: false, baselineRefused: false, counted: 0, findings: 0, cleanupOk: true };
    expect(exitCode(base)).toBe(0);
    expect(exitCode({ ...base, counted: 1 })).toBe(1);
    expect(exitCode({ ...base, findings: 1 })).toBe(1);
    expect(exitCode({ ...base, cleanupOk: false })).toBe(1);
    expect(exitCode({ ...base, baselineRefused: true, counted: 1 })).toBe(2);
    expect(exitCode({ ...base, isolationRefused: true })).toBe(3);
    expect(exitCode({ ...base, runnerError: true, isolationRefused: true })).toBe(4);
  });
});

describe("AC-67.32 AUDIT_ELICITATION", () => {
  const probe = (isError: boolean, changed: boolean) => ({ isError, changed, text: "user_confirmation_refused: decline" });
  const base = {
    refusal_omit: probe(true, false),
    refusal_false: probe(true, false),
    confirmed: { isError: false, changed: true },
  };

  it("AC-67.32 the audit client declares elicitation and declines by default", async () => {
    const client = await import("../../scripts/audit/client.js");
    expect(client.AUDIT_CLIENT_CAPABILITIES).toEqual({ elicitation: {} });
    expect(client.DEFAULT_ELICIT_POLICY).toBe("decline");
    expect(client.elicitAnswer?.("decline")).toEqual({ action: "decline" });
    expect(client.elicitAnswer?.("accept")).toEqual({ action: "accept", content: { confirm: true } });
  });

  it("AC-67.32 a user_confirm record passes only with a declined refusal that errored without change", () => {
    expect(refusalVerdict({ ...base, user_confirm: true, refusal_declined: probe(true, false) }))
      .toEqual({ verdict: "pass", reason: null });
  });

  it("AC-67.32 a user_confirm record without refusal_declined fails", () => {
    expect(refusalVerdict({ ...base, user_confirm: true }))
      .toEqual({ verdict: "fail", reason: "declined_refusal_missing" });
  });

  it("AC-67.32 a declined call that succeeded fails", () => {
    expect(refusalVerdict({ ...base, user_confirm: true, refusal_declined: probe(false, false) }))
      .toEqual({ verdict: "fail", reason: "declined_refusal_missing" });
  });

  it("AC-67.32 a declined call that changed the probe fails", () => {
    expect(refusalVerdict({ ...base, user_confirm: true, refusal_declined: probe(true, true) }))
      .toEqual({ verdict: "fail", reason: "declined_refusal_mutated" });
  });

  it("AC-67.32 a user_confirm: false record is judged as before", () => {
    expect(refusalVerdict({ ...base, user_confirm: false })).toEqual({ verdict: "pass", reason: null });
    expect(refusalVerdict({ ...base, user_confirm: false, confirmed: { isError: false, changed: false } }))
      .toEqual({ verdict: "fail", reason: "confirmed_no_effect" });
  });
});
