import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import { ALLOWED_PASSTHROUGH_ENV } from "../../scripts/audit/client.js";
import { AUDIT_PLAN, destructiveStep, simpleStep, type StepSpec } from "../../scripts/audit/plan.js";
import { runAudit, type AuditOptions } from "../../scripts/audit/run.js";
import { fakeLauncher } from "./fake-backend.js";

const MCP_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const SERVER = path.join(MCP_ROOT, "dist", "index.js");

const temps: string[] = [];
afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

function options(extra: Partial<AuditOptions> = {}): AuditOptions {
  const out = mkdtempSync(path.join(os.tmpdir(), "s28-fake-out-"));
  temps.push(out);
  return {
    mode: "container",
    out,
    report: path.join(out, "report.md"),
    baseline: null,
    noBaseline: true,
    updateBaseline: false,
    server: SERVER,
    discoveryOnly: false,
    keep: false,
    agent: "vitest",
    fixtures: {},
    ...extra,
  };
}

/** A download add step whose observable is the REST row, as in AUDIT_PLAN. */
const ADD: StepSpec = simpleStep({
  id: "fake.download.add",
  tool: "avkit_download",
  action: "add",
  args: () => ({ action: "add", url: "https://www.youtube.com/watch?v=jNQXAC9IVRw", quality: "lowest" }),
  observe: async (ctx, result) => {
    const id = ctx.firstId(result);
    if (!id) return { ok: false, detail: "no id in MCP result" };
    ctx.ledger.register("download", id);
    ctx.state.set("download_id", id);
    const row = await ctx.rest.get(`/downloads/${id}`);
    return { ok: row.status === 200, detail: `GET /downloads/${id} -> ${row.status}` };
  },
});

const REMOVE: StepSpec = destructiveStep({
  id: "fake.download.remove",
  tool: "avkit_download",
  action: "remove",
  depends_on: ["fake.download.add"],
  args: (ctx) => ({ action: "remove", id: ctx.state.get("download_id") }),
  probe: async (ctx) => (await ctx.rest.get(`/downloads/${ctx.state.get("download_id")}`)).status,
  onConfirmed: (ctx) => ctx.ledger.remove("download", String(ctx.state.get("download_id"))),
});

describe("AC-68.1 / AC-68.4 launch and discovery against the built server", () => {
  it("AC-68.1 AC-68.4 launches dist/index.js over stdio, initializes, and discovers 8 tools / 75 actions", async () => {
    expect(existsSync(SERVER), "run npm run build first").toBe(true);
    const { launcher } = fakeLauncher();
    const { summary, exitCode } = await runAudit(options({ discoveryOnly: true }), { launcher });
    expect(summary.launch.initialized).toBe(true);
    expect(summary.launch.command).toBe("node");
    expect(summary.launch.args).toEqual([SERVER]);
    expect(summary.launch.env_keys.filter((k) => k.startsWith("AVKIT_")).sort()).toEqual(["AVKIT_API_TOKEN", "AVKIT_APP_DATA"]);
    expect(summary.launch.env_keys.every((k) => k.startsWith("AVKIT_") || ALLOWED_PASSTHROUGH_ENV.includes(k))).toBe(true);
    expect(summary.discovery.tools).toBe(8);
    // A7: MEU-62 download_asset; TA-1 (Session 30, MEU-67): + capture flatten and revert.
    // MEU-130 (Session 59): + capture crop.
    // MEU-133 (Session 62): + convert probe.
    // MEU-134 (Session 62): + capture frames.
    // MEU-135 (Session 63): + capture sheet.
    // MEU-136 (Session 64): + capture export.
    expect(summary.discovery.actions).toBe(75);
    expect([0, 1]).toContain(exitCode);
  });

  it("AC-68.1 without AVKIT_API_TOKEN the first tool call reports token_missing and isolation refuses (exit 3)", async () => {
    const { launcher, state } = fakeLauncher({ noTokenFile: true });
    const { summary, exitCode } = await runAudit(options(), {
      launcher,
      steps: [ADD],
      mutateLaunch: (launch) => {
        const env = { ...launch.env };
        delete env.AVKIT_API_TOKEN;
        return { ...launch, env };
      },
    });
    expect(summary.launch.initialized).toBe(true);
    expect(summary.isolation.ok).toBe(false);
    expect(summary.isolation.error ?? "").toMatch(/token_missing/);
    expect(exitCode).toBe(3);
    expect(state.lifecycleMutations()).toBe(0);
  });
});

describe("AC-68.6 hollow success", () => {
  it("AC-68.6 a 201 whose REST row is absent fails as hollow and the run exits 1", async () => {
    const { launcher } = fakeLauncher({ hollowDownloadAdd: true });
    const { summary, exitCode } = await runAudit(options(), { launcher, steps: [ADD] });
    const add = summary.steps.find((s) => s.id === "fake.download.add");
    expect(add?.verdict).toBe("fail");
    expect(add?.reason).toBe("hollow");
    expect(exitCode).toBe(1);
    const report = readFileSync(path.join(summary.out_dir, "report.md"), "utf8");
    expect(report).toContain("fake.download.add");
  });
});

describe("AC-68.7 REFUSAL_ORACLE over the real server", () => {
  it("AC-68.7 remove without confirm is refused with state unchanged; confirm removes", async () => {
    const { launcher } = fakeLauncher();
    const { summary, exitCode } = await runAudit(options(), { launcher, steps: [ADD, REMOVE] });
    const remove = summary.steps.find((s) => s.id === "fake.download.remove");
    expect(remove?.verdict, JSON.stringify(remove)).toBe("pass");
    expect(remove?.refusal?.refusal_omit.isError).toBe(true);
    expect(remove?.refusal?.refusal_false.isError).toBe(true);
    expect(remove?.refusal?.refusal_omit.changed).toBe(false);
    expect(remove?.refusal?.confirmed.changed).toBe(true);
    expect(summary.cleanup.ok).toBe(true);
    expect(summary.steps.every((s) => s.verdict === "pass")).toBe(true);
    // Steps all pass; exit 1 only when discovery recorded findings (e.g. a filed schema finding).
    expect(exitCode).toBe(summary.discovery.findings.length > 0 ? 1 : 0);
  });

  it("AC-68.7 state that changes during a refusal probe fails as refusal_mutated", async () => {
    // GET #1 is the add observable, #2 the pre-refusal read; the row vanishes on #3 (after refusal 1).
    const { launcher } = fakeLauncher({ vanishDownloadOnGet: 3 });
    const { summary } = await runAudit(options(), { launcher, steps: [ADD, REMOVE] });
    const remove = summary.steps.find((s) => s.id === "fake.download.remove");
    expect(remove?.verdict).toBe("fail");
    expect(remove?.reason).toBe("refusal_mutated");
  });
});

describe("AC-68.8 / AC-68.9 isolation and cleanup", () => {
  it("AC-68.8 an output path the backend does not move under the root refuses the run before any lifecycle call", async () => {
    const { launcher, state } = fakeLauncher({ ignoreSettingKeys: ["tts.output_path"] });
    const { summary, exitCode } = await runAudit(options(), { launcher, steps: [ADD] });
    expect(exitCode).toBe(3);
    expect(summary.isolation.ok).toBe(false);
    expect(summary.isolation.error).toMatch(/tts\.output_path/);
    expect(state.lifecycleMutations()).toBe(0);
    expect(summary.steps).toEqual([]);
  });

  it("AC-68.8 AC-68.9 a clean run maps every output path under the root, restores settings and removes the root", async () => {
    const { launcher } = fakeLauncher();
    const { summary } = await runAudit(options(), { launcher, steps: [ADD, REMOVE] });
    expect(summary.isolation.ok).toBe(true);
    for (const value of Object.values(summary.isolation.paths)) {
      expect(path.resolve(value).startsWith(path.resolve(summary.isolation.root) + path.sep)).toBe(true);
    }
    expect(summary.cleanup).toEqual({ ok: true, residuals: [], backend_exited: true, root_removed: true });
    expect(existsSync(summary.isolation.root)).toBe(false);
  });
});

const FAKE_SHOT = "fake-shot-1";

/** AC-67.19 test-local USER_CONFIRM step over FIXTURE_REPAIRS (b) (Round 1 F3 option ii). */
const FLATTEN: StepSpec = destructiveStep({
  id: "fake.capture.flatten",
  tool: "avkit_capture",
  action: "flatten",
  userConfirm: true,
  args: () => ({ action: "flatten", id: FAKE_SHOT }),
  probe: async (ctx) => ((await ctx.rest.get(`/captures/${FAKE_SHOT}`)).json as { flatten_count?: number }).flatten_count,
});

describe("AC-67.19 capture flatten/revert audit steps", () => {
  it("AC-67.19 AUDIT_STEPS: flatten and revert are destructive, ordered and chained", () => {
    const ids = AUDIT_PLAN.map((s) => s.id);
    const flatten = AUDIT_PLAN.find((s) => s.id === "capture.flatten");
    const revert = AUDIT_PLAN.find((s) => s.id === "capture.revert");
    expect(flatten && { tool: flatten.tool, action: flatten.action, destructive: flatten.destructive, deps: flatten.depends_on })
      .toEqual({ tool: "avkit_capture", action: "flatten", destructive: true, deps: ["capture.annotate"] });
    expect(revert && { tool: revert.tool, action: revert.action, destructive: revert.destructive, deps: revert.depends_on })
      .toEqual({ tool: "avkit_capture", action: "revert", destructive: true, deps: ["capture.flatten"] });
    expect(ids.indexOf("capture.flatten")).toBe(ids.indexOf("capture.image.annotated") + 1);
    expect(ids.indexOf("capture.revert")).toBe(ids.indexOf("capture.flatten") + 1);
    // MEU-130 (Session 59, D-492): capture.crop sits between revert and capture_interactive.
    expect(ids.indexOf("capture.crop")).toBe(ids.indexOf("capture.revert") + 1);
    // MEU-134 (Session 62, D-591): capture.frames sits right after crop.
    expect(ids.indexOf("capture.frames")).toBe(ids.indexOf("capture.crop") + 1);
    // MEU-135 (Session 63): capture.sheet sits right after frames.
    expect(ids.indexOf("capture.sheet")).toBe(ids.indexOf("capture.frames") + 1);
    // MEU-136 (Session 64): capture.export sits between sheet and capture_interactive.
    expect(ids.indexOf("capture.export")).toBe(ids.indexOf("capture.sheet") + 1);
    expect(ids.indexOf("capture.capture_interactive")).toBe(ids.indexOf("capture.export") + 1);
  });

  it("AC-67.19 a userConfirm step refuses omit, false and a declined prompt; the accepted call flattens once", async () => {
    const { launcher, state } = fakeLauncher();
    const { summary } = await runAudit(options(), { launcher, steps: [FLATTEN] });
    expect(summary.isolation.ok, summary.isolation.error ?? "").toBe(true);
    expect(path.resolve(summary.isolation.paths["capture.backup_dir"] ?? "")).toBe(
      path.join(path.resolve(summary.isolation.root), "out", "capture_backups"),
    );
    const step = summary.steps.find((s) => s.id === "fake.capture.flatten");
    expect(step?.verdict, JSON.stringify(step)).toBe("pass");
    expect(step?.refusal?.user_confirm).toBe(true);
    expect(step?.refusal?.refusal_omit).toEqual(expect.objectContaining({ isError: true, changed: false }));
    expect(step?.refusal?.refusal_false).toEqual(expect.objectContaining({ isError: true, changed: false }));
    expect(step?.refusal?.refusal_declined).toEqual(expect.objectContaining({ isError: true, changed: false }));
    expect(step?.refusal?.refusal_declined?.text).toContain("user_confirmation_refused");
    expect(step?.refusal?.confirmed).toEqual({ isError: false, changed: true });
    const posts = state.requests.filter((r) => r.method === "POST" && r.path.endsWith(`/captures/${FAKE_SHOT}/flatten`));
    expect(posts).toHaveLength(1);
  });
});
