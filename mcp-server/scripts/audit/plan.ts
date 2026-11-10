/**
 * AUDIT_PLAN: the ordered Phase 2 lifecycle and Phase 3 functional steps of the MEU-68 audit.
 * Every step's verdict comes from an independent REST or filesystem observation
 * (OBSERVABLE_RULE); destructive actions run the REFUSAL_ORACLE. Sequences follow the state
 * machines pinned in walkthrough.md §Row-3 pins (plan amendment A4, decision D-13).
 */
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  closeSync,
  existsSync,
  mkdirSync,
  openSync,
  readdirSync,
  readFileSync,
  readSync,
  statSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";
import { isDeepStrictEqual } from "node:util";
import { deflateSync } from "node:zlib";
import type { Fixtures } from "./fixtures.js";
import type { CleanupLedger } from "./ledger.js";
import type { RestResponse } from "./observer.js";
import type { ElicitPolicy, Mode, ObservableResult, RefusalRecord, ToolCallOutcome } from "./types.js";

export type { RestResponse } from "./observer.js";

/** Output subdirectories of ISOLATED_ROOT/out, one per ISOLATION_KEYS member. */
export type OutSub = "downloads" | "transcripts" | "models" | "tts" | "convert" | "captures" | "capture_backups" | "src";

export type StepContext = {
  mode: Mode;
  platform: string;
  fixtures: Fixtures;
  root: string;
  out: (sub: OutSub) => string;
  /** `elicit` answers a USER_CONFIRM prompt during this call (AUDIT_ELICITATION; default decline). */
  call: (tool: string, args: Record<string, unknown>, opts?: { elicit?: ElicitPolicy }) => Promise<ToolCallOutcome>;
  rest: {
    get: (p: string) => Promise<RestResponse>;
    send: (method: string, p: string, body?: unknown) => Promise<RestResponse>;
    bytes: (p: string) => Promise<{ status: number; bytes: Uint8Array }>;
  };
  ledger: CleanupLedger;
  state: Map<string, unknown>;
  firstId: (result: ToolCallOutcome) => string | null;
  poll: <T>(probe: () => Promise<T | null>, timeoutMs: number, intervalMs?: number) => Promise<T | null>;
};

export type StepOutcome =
  | {
      kind: "simple";
      isError: boolean;
      expectError: boolean;
      observable: ObservableResult | null;
      text: string;
      reason?: string;
    }
  | { kind: "destructive"; refusal: RefusalRecord; text: string; observable: ObservableResult }
  | { kind: "blocked"; by: string; detail: string };

export type StepSpec = {
  id: string;
  tool: string;
  action: string;
  phase: "lifecycle" | "functional";
  depends_on: string[];
  destructive?: boolean;
  execute: (ctx: StepContext) => Promise<StepOutcome>;
};

const SECOND = 1_000;
const MINUTE = 60 * SECOND;
const T = {
  model: 20 * MINUTE,
  tts: 10 * MINUTE,
  queue: 2 * MINUTE,
  download: 15 * MINUTE,
  convert: 5 * MINUTE,
  transcript: 3 * MINUTE,
  effect: 30 * SECOND,
};

// ---------------------------------------------------------------- helpers

/** Parses an MCP text result as JSON; null when it is not JSON. */
export function payload(result: ToolCallOutcome): unknown {
  try {
    return JSON.parse(result.text);
  } catch {
    return null;
  }
}

type Rec = Record<string, unknown>;
const asRec = (v: unknown): Rec => (v && typeof v === "object" && !Array.isArray(v) ? (v as Rec) : {});
const items = (v: unknown): Rec[] => {
  const list = asRec(v).items;
  return Array.isArray(list) ? (list as Rec[]) : [];
};
const ids = (v: unknown): string[] => items(v).map((i) => String(i.id ?? i.voice_id ?? ""));
const str = (v: unknown): string => (v === undefined || v === null ? "" : String(v));

/** True when every key of `mcp` (a sanitized subset) deep-equals the REST value. */
export function subsetEqual(mcp: unknown, rest: unknown): boolean {
  if (Array.isArray(mcp)) {
    return Array.isArray(rest) && mcp.length === rest.length && mcp.every((v, i) => subsetEqual(v, rest[i]));
  }
  if (mcp && typeof mcp === "object") {
    const r = asRec(rest);
    return Object.entries(mcp as Rec).every(([k, v]) => k in r && subsetEqual(v, r[k]));
  }
  return isDeepStrictEqual(mcp, rest);
}

function obs(ok: boolean, detail: string, errorMessage?: string | null): ObservableResult {
  return { ok, detail, errorMessage: errorMessage ?? null };
}

function within(file: string, root: string): boolean {
  const rel = path.relative(path.resolve(root), path.resolve(file));
  return rel !== "" && !rel.startsWith("..") && !path.isAbsolute(rel);
}

function fileReport(file: string, root: string): { ok: boolean; detail: string } {
  if (!file) return { ok: false, detail: "no path" };
  if (!existsSync(file)) return { ok: false, detail: `${file} missing` };
  const size = statSync(file).size;
  if (size <= 0) return { ok: false, detail: `${file} empty` };
  if (!within(file, root)) return { ok: false, detail: `${file} outside isolated root` };
  return { ok: true, detail: `${path.basename(file)} ${size} B` };
}

function head(file: string, n: number): Buffer {
  const fd = openSync(file, "r");
  try {
    const buf = Buffer.alloc(n);
    readSync(fd, buf, 0, n, 0);
    return buf;
  } finally {
    closeSync(fd);
  }
}

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function isAudio(file: string): boolean {
  const h = head(file, 4);
  return h.subarray(0, 3).toString("latin1") === "ID3" || h.subarray(0, 4).toString("latin1") === "RIFF"
    || (h[0] === 0xff && (h[1] & 0xe0) === 0xe0);
}

/** Polls `GET path` until `pick(json)` returns a value or the timeout passes. */
async function pollJson<T>(ctx: StepContext, p: string, timeoutMs: number, pick: (json: unknown) => T | null): Promise<T | null> {
  return ctx.poll(async () => {
    const res = await ctx.rest.get(p);
    return res.status === 200 ? pick(res.json) : null;
  }, timeoutMs);
}

function rowById(json: unknown, id: string): Rec | null {
  return items(json).find((i) => i.id === id) ?? null;
}

const TERMINAL = new Set(["Done", "Failed", "Cancelled", "Skipped", "AgeRestricted", "QualityBlocked"]);

// ---------------------------------------------------------------- step builders

/**
 * The MCP server's image cap, restated: the audit drives the server from outside and may not
 * import it (AC-68.2). `tests/audit/capture-image-step.test.ts` fails if the two part.
 */
export const AUDIT_IMAGE_CAP = 7_800_000;

/** The server's own refusal; a lost connection is also isError but never carries this code. */
function isImageRefusal(result: ToolCallOutcome): boolean {
  return result.isError && result.text.startsWith("payload_too_large:");
}

/** The refusal is right only when REST's own image really is over the cap. */
function refusedImageObservation(rest: { status: number; bytes: Uint8Array }): ObservableResult {
  const over = rest.status === 200 && rest.bytes.length > AUDIT_IMAGE_CAP;
  return obs(over, `MCP refused; REST ${rest.status} ${rest.bytes.length} B over the ${AUDIT_IMAGE_CAP} B cap: ${String(over)}`);
}

/** One MCP call + one observable. */
export function simpleStep(spec: {
  id: string;
  tool: string;
  action: string;
  phase?: "lifecycle" | "functional";
  depends_on?: string[];
  expectError?: boolean | ((result: ToolCallOutcome) => boolean);
  needs?: string[];
  args: (ctx: StepContext) => Record<string, unknown>;
  observe: (ctx: StepContext, result: ToolCallOutcome) => Promise<ObservableResult>;
}): StepSpec {
  return {
    id: spec.id,
    tool: spec.tool,
    action: spec.action,
    phase: spec.phase ?? "lifecycle",
    depends_on: spec.depends_on ?? [],
    execute: async (ctx) => {
      const missing = (spec.needs ?? []).find((k) => !ctx.state.has(k));
      if (missing) return { kind: "blocked", by: `state:${missing}`, detail: `${missing} was never established` };
      const result = await ctx.call(spec.tool, spec.args(ctx));
      const observable = await spec.observe(ctx, result);
      const expectError = typeof spec.expectError === "function" ? spec.expectError(result) : (spec.expectError ?? false);
      return { kind: "simple", isError: result.isError, expectError, observable, text: result.text };
    },
  };
}

/**
 * REFUSAL_ORACLE step: probe → call without confirm → probe → confirm:false → probe →
 * confirm:true → probe until changed. `probe` returns the destructive effect's state.
 * `userConfirm` (USER_CONFIRM_ACTIONS, AUDIT_ELICITATION) adds confirm:true with the IDE prompt
 * declined before the confirmed call, which then runs with the prompt accepted.
 * `confirmedEffect` narrows what counts as the confirmed call's change (by default every probe change counts).
 * `raceLost` and `attempts` (AUDIT_CANCEL_STEP): when the refusals held and the confirmed call
 * had no error and no effect, and `raceLost` says the target finished first, the precondition
 * block and the whole sequence run again, up to `attempts` times (default 1: no retry).
 */
export function destructiveStep(spec: {
  id: string;
  tool: string;
  action: string;
  depends_on?: string[];
  needs?: string[];
  args: (ctx: StepContext) => Record<string, unknown>;
  probe: (ctx: StepContext) => Promise<unknown>;
  onConfirmed?: (ctx: StepContext) => void;
  precondition?: (ctx: StepContext) => Promise<ObservableResult>;
  reestablish?: (ctx: StepContext) => Promise<void>;
  userConfirm?: boolean;
  confirmedEffect?: (ctx: StepContext, before: unknown, after: unknown) => boolean;
  raceLost?: (ctx: StepContext) => Promise<boolean>;
  attempts?: number;
}): StepSpec {
  const effect = spec.confirmedEffect ?? ((_ctx: StepContext, before: unknown, after: unknown) => !isDeepStrictEqual(after, before));
  const attempts = Math.max(1, spec.attempts ?? 1);
  const once = async (ctx: StepContext): Promise<StepOutcome> => {
    if (spec.precondition) {
      let pre = await spec.precondition(ctx);
      if (!pre.ok && spec.reestablish) {
        await spec.reestablish(ctx);
        pre = await spec.precondition(ctx);
        if (pre.ok) pre = { ...pre, detail: `precondition_reestablished; ${pre.detail}` };
      }
      if (!pre.ok) {
        return { kind: "simple", isError: false, expectError: false, observable: pre, text: "", reason: "precondition_lost" };
      }
    }
    const base = spec.args(ctx);
    const before = await spec.probe(ctx);
    const omit = await ctx.call(spec.tool, base);
    const afterOmit = await spec.probe(ctx);
    const asFalse = await ctx.call(spec.tool, { ...base, confirm: false });
    const afterFalse = await spec.probe(ctx);
    let declined: RefusalRecord["refusal_declined"];
    if (spec.userConfirm) {
      const res = await ctx.call(spec.tool, { ...base, confirm: true }, { elicit: "decline" });
      const afterDeclined = await spec.probe(ctx);
      declined = { isError: res.isError, changed: !isDeepStrictEqual(afterDeclined, before), text: res.text.slice(0, 300) };
    }
    const confirmed = await ctx.call(spec.tool, { ...base, confirm: true }, spec.userConfirm ? { elicit: "accept" } : undefined);
    const afterConfirm = confirmed.isError
      ? await spec.probe(ctx)
      : await ctx.poll(async () => {
          const now = await spec.probe(ctx);
          return effect(ctx, before, now) ? { now } : null;
        }, T.effect).then((r) => (r ? r.now : before));
    const changed = effect(ctx, before, afterConfirm);
    if (!confirmed.isError && changed) spec.onConfirmed?.(ctx);
    const refusal: RefusalRecord = {
      refusal_omit: { isError: omit.isError, changed: !isDeepStrictEqual(afterOmit, before), text: omit.text.slice(0, 300) },
      refusal_false: { isError: asFalse.isError, changed: !isDeepStrictEqual(afterFalse, before), text: asFalse.text.slice(0, 300) },
      ...(spec.userConfirm ? { refusal_declined: declined, user_confirm: true } : { user_confirm: false }),
      confirmed: { isError: confirmed.isError, changed },
    };
    return {
      kind: "destructive",
      refusal,
      text: confirmed.text,
      observable: obs(changed && !confirmed.isError, `before=${JSON.stringify(before)} after=${JSON.stringify(afterConfirm)}`),
    };
  };
  return {
    id: spec.id,
    tool: spec.tool,
    action: spec.action,
    phase: "lifecycle",
    depends_on: spec.depends_on ?? [],
    destructive: true,
    execute: async (ctx) => {
      const missing = (spec.needs ?? []).find((k) => !ctx.state.has(k));
      if (missing) return { kind: "blocked", by: `state:${missing}`, detail: `${missing} was never established` };
      for (let attempt = 1; ; attempt += 1) {
        let outcome = await once(ctx);
        if (outcome.kind !== "destructive") return outcome;
        if (attempts > 1) {
          outcome = { ...outcome, observable: { ...outcome.observable, detail: `attempt ${attempt}/${attempts}; ${outcome.observable.detail}` } };
        }
        const r = outcome.refusal;
        const held = (x: { isError: boolean; changed: boolean } | undefined) => x !== undefined && x.isError && !x.changed;
        const refusalsHeld = held(r.refusal_omit) && held(r.refusal_false) && (!spec.userConfirm || held(r.refusal_declined));
        const noEffect = !r.confirmed.isError && !r.confirmed.changed;
        if (attempt >= attempts || !refusalsHeld || !noEffect || !spec.raceLost) return outcome;
        if (!(await spec.raceLost(ctx))) return outcome;
      }
    },
  };
}

/** A step whose MCP result must equal the REST read at `restPath` (G25 parity). */
function parityStep(spec: {
  id: string;
  tool: string;
  action: string;
  phase?: "lifecycle" | "functional";
  depends_on?: string[];
  needs?: string[];
  args: (ctx: StepContext) => Record<string, unknown>;
  restPath: (ctx: StepContext) => string;
  /** Compare ids only (queues that move while observed). */
  idsOnly?: boolean;
  extra?: (ctx: StepContext, mcp: unknown, rest: unknown) => string | null;
}): StepSpec {
  return simpleStep({
    ...spec,
    observe: async (ctx, result) => {
      if (result.isError) return obs(false, `MCP error: ${result.text.slice(0, 200)}`);
      const mcp = payload(result);
      const rest = await ctx.rest.get(spec.restPath(ctx));
      if (rest.status !== 200) return obs(false, `REST ${spec.restPath(ctx)} -> ${rest.status}`);
      const same = spec.idsOnly ? isDeepStrictEqual(ids(mcp), ids(rest.json)) : subsetEqual(mcp, rest.json);
      if (!same) return obs(false, `MCP payload differs from REST ${spec.restPath(ctx)}`);
      const problem = spec.extra?.(ctx, mcp, rest.json) ?? null;
      if (problem) return obs(false, problem);
      return obs(true, `MCP == REST ${spec.restPath(ctx)}${spec.idsOnly ? ` ids=${ids(mcp).length}` : ""}`);
    },
  });
}

/** A settings.set step (used for domain setup/restore) whose observable is the REST read-back. */
function settingsStep(id: string, ns: string, values: (ctx: StepContext) => Rec, depends_on: string[] = []): StepSpec {
  return simpleStep({
    id,
    tool: "avkit_settings",
    action: "set",
    depends_on,
    args: (ctx) => ({ action: "set", namespace: ns, ...values(ctx) }),
    observe: async (ctx, result) => {
      if (result.isError) return obs(false, `MCP error: ${result.text.slice(0, 200)}`);
      const rest = await ctx.rest.get(`/settings/${ns}`);
      const want = values(ctx);
      const ok = rest.status === 200 && subsetEqual(want, rest.json);
      return obs(ok, `REST /settings/${ns} ${ok ? "==" : "!="} ${JSON.stringify(want)}`);
    },
  });
}

/** Remembers the current REST values of `keys` so a restore step can put them back. */
async function rememberSettings(ctx: StepContext, ns: string, keys: string[]): Promise<void> {
  const rest = await ctx.rest.get(`/settings/${ns}`);
  const rec = asRec(rest.json);
  ctx.state.set(`orig:${ns}`, Object.fromEntries(keys.map((k) => [k, rec[k]])));
}

function ffmpegBin(ctx: StepContext): string {
  return str(ctx.state.get("ffmpeg_path")) || "ffmpeg";
}

function makeVideo(ctx: StepContext, name: string, seconds: number, size: string): string {
  const dir = ctx.out("src");
  mkdirSync(dir, { recursive: true });
  const file = path.join(dir, name);
  const res = spawnSync(ffmpegBin(ctx), [
    "-loglevel", "error", "-y",
    "-f", "lavfi", "-i", `testsrc=duration=${seconds}:size=${size}:rate=30`,
    "-f", "lavfi", "-i", `sine=duration=${seconds}`,
    "-shortest", file,
  ], { encoding: "utf8", timeout: 2 * MINUTE });
  if (res.status !== 0) throw new Error(`ffmpeg fixture ${name} failed: ${res.error?.message ?? res.stderr}`);
  return file;
}

// ---------------------------------------------------------------- settings + health

/** One reversible leaf per namespace (settings.ts SETTINGS_SCHEMA; toggled then restored). */
const REVERSIBLE: Record<string, [string, (v: unknown) => unknown]> = {
  downloader: ["archive_tracking", (v) => !v],
  transcript: ["requests_per_hour", (v) => Number(v) + 1],
  tts: ["speed", (v) => (Number(v) === 1.25 ? 1 : 1.25)],
  app: ["console_visible", (v) => !v],
  ui: ["theme", (v) => (v === "dark" ? "light" : "dark")],
  converter: ["skip_existing", (v) => !v],
  capture: ["copy_to_clipboard", (v) => !v],
};

const SETTINGS_STEPS: StepSpec[] = [
  {
    id: "settings.get",
    tool: "avkit_settings",
    action: "get",
    phase: "lifecycle",
    depends_on: [],
    execute: async (ctx) => {
      const namespaces = Object.keys(REVERSIBLE);
      const bad: string[] = [];
      let last: ToolCallOutcome = { isError: false, text: "" };
      for (const ns of namespaces) {
        last = await ctx.call("avkit_settings", { action: "get", namespace: ns });
        const rest = await ctx.rest.get(`/settings/${ns}`);
        if (last.isError || rest.status !== 200 || !subsetEqual(payload(last), rest.json)) bad.push(ns);
      }
      return {
        kind: "simple",
        isError: bad.length === namespaces.length && last.isError,
        expectError: false,
        observable: obs(bad.length === 0, bad.length ? `MCP != REST for ${bad.join(",")}` : `MCP == REST for ${namespaces.length} namespaces`),
        text: last.text,
      };
    },
  },
  {
    id: "settings.set",
    tool: "avkit_settings",
    action: "set",
    phase: "lifecycle",
    depends_on: ["settings.get"],
    execute: async (ctx) => {
      const bad: string[] = [];
      let last: ToolCallOutcome = { isError: false, text: "" };
      for (const [ns, [leaf, flip]] of Object.entries(REVERSIBLE)) {
        const before = asRec((await ctx.rest.get(`/settings/${ns}`)).json)[leaf];
        ctx.state.set(`reversible:${ns}`, before);
        const next = flip(before);
        last = await ctx.call("avkit_settings", { action: "set", namespace: ns, [leaf]: next });
        const after = asRec((await ctx.rest.get(`/settings/${ns}`)).json)[leaf];
        if (last.isError || !isDeepStrictEqual(after, next)) bad.push(`${ns}.${leaf}`);
      }
      return {
        kind: "simple",
        isError: last.isError,
        expectError: false,
        observable: obs(bad.length === 0, bad.length ? `not persisted: ${bad.join(",")}` : "7 leaves persisted per REST"),
        text: last.text,
      };
    },
  },
  {
    id: "settings.set.restore",
    tool: "avkit_settings",
    action: "set",
    phase: "lifecycle",
    depends_on: ["settings.set"],
    execute: async (ctx) => {
      const bad: string[] = [];
      let last: ToolCallOutcome = { isError: false, text: "" };
      for (const [ns, [leaf]] of Object.entries(REVERSIBLE)) {
        const original = ctx.state.get(`reversible:${ns}`);
        last = await ctx.call("avkit_settings", { action: "set", namespace: ns, [leaf]: original });
        const after = asRec((await ctx.rest.get(`/settings/${ns}`)).json)[leaf];
        if (last.isError || !isDeepStrictEqual(after, original)) bad.push(`${ns}.${leaf}`);
      }
      return {
        kind: "simple",
        isError: last.isError,
        expectError: false,
        observable: obs(bad.length === 0, bad.length ? `not restored: ${bad.join(",")}` : "7 leaves restored per REST"),
        text: last.text,
      };
    },
  },
];

const HEALTH_STEPS: StepSpec[] = [
  simpleStep({
    id: "health.liveness",
    tool: "avkit_health",
    action: "liveness",
    phase: "functional",
    args: () => ({ action: "liveness" }),
    observe: async (ctx, result) => {
      const rest = await ctx.rest.get("/health");
      const ok = !result.isError && rest.status === 200 && subsetEqual(payload(result), rest.json) && asRec(rest.json).status === "ok";
      return obs(ok, `REST /health -> ${rest.status} ${rest.text.slice(0, 40)}`);
    },
  }),
  parityStep({
    id: "health.dependencies",
    tool: "avkit_health",
    action: "dependencies",
    phase: "functional",
    args: () => ({ action: "dependencies" }),
    restPath: () => "/health/dependencies",
    extra: (ctx, mcp) => {
      const rec = asRec(mcp);
      const ff = asRec(rec.ffmpeg);
      if (ff.path) ctx.state.set("ffmpeg_path", ff.path);
      const both = asRec(rec.yt_dlp).available === true && ff.available === true;
      ctx.state.set("ffmpeg_available", ff.available === true);
      return ctx.mode === "authoritative" && !both ? "authoritative run requires yt-dlp and ffmpeg available" : null;
    },
  }),
];

// ---------------------------------------------------------------- models + tts

async function assetState(ctx: StepContext, asset: string): Promise<string> {
  const deps = asRec((await ctx.rest.get("/health/dependencies")).json);
  return str(asRec(deps[asset]).state);
}

/**
 * MEU-62 TTS runtime assets (A7). The state is read first: an asset that is already `ready`
 * must answer the 409 conflict contract (routes/models.py CONFLICT_409) and stay ready; a
 * missing asset must be accepted (202) and reach `ready` in /health/dependencies.
 */
function assetStep(id: string, asset: "tts_onnx_vocab" | "tts_spacy_model"): StepSpec {
  return {
    id,
    tool: "avkit_models",
    action: "download_asset",
    phase: "lifecycle",
    depends_on: ["models.download"],
    execute: async (ctx) => {
      const before = await assetState(ctx, asset);
      const result = await ctx.call("avkit_models", { action: "download_asset", asset });
      if (before === "ready") {
        const after = await assetState(ctx, asset);
        const conflict = /conflict|409|already/i.test(result.text);
        return {
          kind: "simple",
          isError: result.isError,
          expectError: true,
          observable: obs(conflict && after === "ready", `${asset} already ready: 409 contract ${String(conflict)}; state after ${after}`),
          text: result.text,
        };
      }
      if (result.isError) {
        return { kind: "simple", isError: true, expectError: false, observable: obs(false, `MCP error: ${result.text.slice(0, 200)}`), text: result.text };
      }
      const state = await ctx.poll(async () => ((await assetState(ctx, asset)) === "ready" ? "ready" : null), T.model);
      return {
        kind: "simple",
        isError: false,
        expectError: false,
        observable: obs(state === "ready", `REST /health/dependencies ${asset}: ${before} -> ${state ?? (await assetState(ctx, asset))}`),
        text: result.text,
      };
    },
  };
}

const MODEL_STEPS_BEFORE_TTS: StepSpec[] = [
  parityStep({
    id: "models.available",
    tool: "avkit_models",
    action: "available",
    args: () => ({ action: "available" }),
    restPath: () => "/models/available",
    extra: (ctx, mcp) => {
      const pick = items(mcp)
        .filter((v) => v.format === ctx.fixtures.model_format)
        .sort((a, b) => Number(a.size_bytes) - Number(b.size_bytes))[0];
      if (!pick) return `no ${ctx.fixtures.model_format} variant available`;
      ctx.state.set("variant_id", String(pick.id));
      return null;
    },
  }),
  parityStep({
    id: "models.downloaded.before",
    tool: "avkit_models",
    action: "downloaded",
    args: () => ({ action: "downloaded" }),
    restPath: () => "/models/downloaded",
  }),
  simpleStep({
    id: "models.download",
    tool: "avkit_models",
    action: "download",
    depends_on: ["models.available"],
    args: (ctx) => ({ action: "download", variant_id: ctx.state.get("variant_id") }),
    observe: async (ctx, result) => {
      if (result.isError) return obs(false, `MCP error: ${result.text.slice(0, 200)}`);
      const variant = str(ctx.state.get("variant_id"));
      const row = await pollJson(ctx, "/models/downloaded", T.model, (json) => {
        const r = rowById(json, variant);
        return r && r.is_downloaded === true ? r : null;
      });
      if (!row) {
        const rt = asRec((await ctx.rest.get("/models/download-runtime")).json);
        return obs(false, `variant ${variant} never listed as downloaded`, str(rt.error_message) || null);
      }
      const f = fileReport(str(row.path), ctx.root);
      // The row lists once the weights land. Voice packs keep the runtime busy after that
      // (MODEL_CHAINS_PACKS), and any other download started meanwhile gets a 409.
      const runtime = await pollJson(ctx, "/models/download-runtime", T.model, (json) => {
        const rt = asRec(json);
        return rt.state === "Downloading" ? null : rt;
      });
      if (!runtime) return obs(false, `voice packs still downloading after ${variant}`);
      if (runtime.state === "Failed") {
        return obs(false, `voice packs failed after ${variant}`, str(runtime.error_message) || null);
      }
      return obs(f.ok, `REST downloaded ${variant}; ${f.detail}`);
    },
  }),
  parityStep({
    id: "models.download_runtime",
    tool: "avkit_models",
    action: "download_runtime",
    phase: "functional",
    depends_on: ["models.download"],
    args: () => ({ action: "download_runtime" }),
    restPath: () => "/models/download-runtime",
  }),
  parityStep({
    id: "models.downloaded.after",
    tool: "avkit_models",
    action: "downloaded",
    depends_on: ["models.download"],
    args: () => ({ action: "downloaded" }),
    restPath: () => "/models/downloaded",
    extra: (ctx, mcp) => (ids(mcp).includes(str(ctx.state.get("variant_id"))) ? null : "variant missing from downloaded"),
  }),
  assetStep("models.download_asset.vocab", "tts_onnx_vocab"),
  assetStep("models.download_asset.spacy", "tts_spacy_model"),
  simpleStep({
    id: "models.load",
    tool: "avkit_models",
    action: "load",
    depends_on: ["models.download"],
    args: (ctx) => ({ action: "load", variant_id: ctx.state.get("variant_id"), device: "auto" }),
    observe: async (ctx, result) => {
      const st = asRec((await ctx.rest.get("/models/status")).json);
      const ok = !result.isError && st.is_loaded === true && st.variant_id === ctx.state.get("variant_id");
      return obs(ok, `REST status is_loaded=${String(st.is_loaded)} variant=${str(st.variant_id)}`, result.isError ? result.text : null);
    },
  }),
  parityStep({
    id: "models.status",
    tool: "avkit_models",
    action: "status",
    depends_on: ["models.load"],
    args: () => ({ action: "status" }),
    restPath: () => "/models/status",
  }),
];

async function ttsJob(ctx: StepContext, id: string): Promise<Rec> {
  return asRec((await ctx.rest.get(`/tts/${id}`)).json);
}

function generateArgs(ctx: StepContext, text: string): Rec {
  return { action: "generate", text, voice: ctx.fixtures.tts_voice, speed: 1, format: "MP3", enabled_steps: [] };
}

const TTS_STEPS: StepSpec[] = [
  parityStep({
    id: "tts.voices",
    tool: "avkit_tts",
    action: "voices",
    args: () => ({ action: "voices" }),
    restPath: () => "/tts/voices",
    idsOnly: true,
    extra: (ctx, mcp) => (ids(mcp).includes(ctx.fixtures.tts_voice) ? null : `voice ${ctx.fixtures.tts_voice} not listed`),
  }),
  simpleStep({
    id: "tts.prepare",
    tool: "avkit_tts",
    action: "prepare",
    args: (ctx) => ({ action: "prepare", text: ctx.fixtures.tts_text, enabled_steps: [] }),
    observe: async (ctx, result) => {
      const rest = await ctx.rest.send("POST", "/tts/prepare", { text: ctx.fixtures.tts_text, enabled_steps: [] });
      const mcp = asRec(payload(result));
      const ok = !result.isError && rest.status === 200 && str(mcp.cleaned_text) !== "" && subsetEqual(mcp, rest.json);
      return obs(ok, `prepare cleaned_text ${str(mcp.cleaned_text).length} chars; REST ${rest.status}`);
    },
  }),
  simpleStep({
    id: "tts.generate",
    tool: "avkit_tts",
    action: "generate",
    depends_on: ["models.load", "models.download_asset.vocab", "models.download_asset.spacy"],
    args: (ctx) => generateArgs(ctx, ctx.fixtures.tts_text),
    observe: async (ctx, result) => {
      if (result.isError) return obs(false, `MCP error: ${result.text.slice(0, 200)}`);
      const id = ctx.firstId(result);
      if (!id) return obs(false, "no job id in MCP result");
      ctx.ledger.register("tts_job", id);
      ctx.state.set("tts_job1", id);
      const job = await pollJson(ctx, `/tts/${id}`, T.tts, (j) => (TERMINAL.has(str(asRec(j).status)) ? asRec(j) : null));
      if (!job) return obs(false, `job ${id} not terminal within ${T.tts / MINUTE} min`);
      ctx.ledger.remove("tts_job", id);
      if (job.status !== "Done") return obs(false, `job ${id} ${str(job.status)}`, str(job.error_message) || null);
      const f = fileReport(str(job.output_path), ctx.root);
      if (!f.ok) return obs(false, f.detail);
      const audio = isAudio(str(job.output_path));
      return obs(audio, `job Done; ${f.detail}; audio header ${audio ? "ok" : "missing"}`);
    },
  }),
  parityStep({
    id: "tts.get",
    tool: "avkit_tts",
    action: "get",
    depends_on: ["tts.generate"],
    args: (ctx) => ({ action: "get", id: ctx.state.get("tts_job1") }),
    restPath: (ctx) => `/tts/${str(ctx.state.get("tts_job1"))}`,
  }),
  // AUDIT_CANCEL_STEP: generate returns at once, so cancel targets a second, long job while it is
  // Generating. A job that reaches Done before the confirmed cancel lost the race and is retried
  // with a new job (3 attempts); Failed, or still Generating after the effect poll, is a real
  // failure (`confirmed_no_effect`).
  destructiveStep({
    id: "tts.cancel",
    tool: "avkit_tts",
    action: "cancel",
    depends_on: ["tts.generate"],
    precondition: async (ctx) => {
      if (!ctx.state.has("tts_job2")) return obs(false, "no running tts_job2");
      const id = str(ctx.state.get("tts_job2"));
      const status = str((await ttsJob(ctx, id)).status);
      return obs(status === "Generating", `tts_job2 ${id} ${status}`);
    },
    reestablish: async (ctx) => {
      const { action: _action, ...body } = generateArgs(ctx, ctx.fixtures.tts_cancel_text);
      const res = await ctx.rest.send("POST", "/tts/generate", body);
      const id = str(asRec(res.json).id);
      if (res.status !== 201 || id === "") return;
      ctx.ledger.register("tts_job", id);
      ctx.state.set("tts_job2", id);
    },
    args: (ctx) => ({ action: "cancel", id: ctx.state.get("tts_job2") }),
    probe: async (ctx) => (await ttsJob(ctx, str(ctx.state.get("tts_job2")))).status === "Cancelled",
    raceLost: async (ctx) => (await ttsJob(ctx, str(ctx.state.get("tts_job2")))).status === "Done",
    attempts: 3,
  }),
];

const MODEL_STEPS_AFTER_TTS: StepSpec[] = [
  simpleStep({
    id: "models.unload",
    tool: "avkit_models",
    action: "unload",
    depends_on: ["models.load"],
    args: () => ({ action: "unload" }),
    observe: async (ctx, result) => {
      const st = asRec((await ctx.rest.get("/models/status")).json);
      return obs(!result.isError && st.is_loaded === false, `REST status is_loaded=${String(st.is_loaded)}`);
    },
  }),
  parityStep({
    id: "models.status.after",
    tool: "avkit_models",
    action: "status",
    depends_on: ["models.unload"],
    args: () => ({ action: "status" }),
    restPath: () => "/models/status",
  }),
];

// ---------------------------------------------------------------- downloads

async function downloads(ctx: StepContext): Promise<Rec> {
  return asRec((await ctx.rest.get("/downloads")).json);
}

/** Fixture URL each network step uses (the census proof re-probes exactly these). */
export const NETWORK_STEP_URLS: Record<string, keyof Fixtures> = {
  "download.add.a": "download_url_a",
  "download.add.b": "download_url_b",
  "download.add.c": "download_url_c",
  "transcript.add": "transcript_source_url",
};

function addDownload(id: string, key: "download_url_a" | "download_url_b" | "download_url_c", stateKey: string): StepSpec {
  return simpleStep({
    id,
    tool: "avkit_download",
    action: "add",
    depends_on: ["download.setup"],
    args: (ctx) => ({ action: "add", url: ctx.fixtures[key], quality: "360p" }),
    observe: async (ctx, result) => {
      if (result.isError) return obs(false, `MCP error: ${result.text.slice(0, 200)}`);
      const jobId = ctx.firstId(result);
      if (!jobId) return obs(false, "no job id in MCP result");
      ctx.ledger.register("download", jobId);
      ctx.state.set(stateKey, jobId);
      const row = await ctx.rest.get(`/downloads/${jobId}`);
      const status = str(asRec(row.json).status);
      return obs(row.status === 200 && status === "Pending", `REST /downloads/${jobId} -> ${row.status} ${status}`);
    },
  });
}

const processorState = (json: unknown) => str(asRec(asRec(json).processor).state);

function waitDownload(id: string, want: (row: Rec, proc: string) => boolean, timeoutMs: number) {
  return async (ctx: StepContext) => {
    const hit = await pollJson(ctx, "/downloads", timeoutMs, (json) => {
      const row = rowById(json, str(ctx.state.get(id)));
      return row && want(row, processorState(json)) ? { row, proc: processorState(json) } : null;
    });
    return hit;
  };
}

function orderStep(id: string, depends_on: string[], order: string[]): StepSpec {
  return simpleStep({
    id,
    tool: "avkit_download",
    action: "reorder",
    depends_on,
    args: (ctx) => ({ action: "reorder", job_ids: order.map((k) => ctx.state.get(k)) }),
    observe: async (ctx, result) => {
      const want = order.map((k) => str(ctx.state.get(k)));
      const got = ids(await downloads(ctx));
      return obs(!result.isError && isDeepStrictEqual(got, want), `REST order ${got.map((g) => g.slice(0, 8)).join(",")}`);
    },
  });
}

const DOWNLOAD_STEPS: StepSpec[] = [
  parityStep({ id: "download.list.empty", tool: "avkit_download", action: "list", args: () => ({ action: "list" }), restPath: () => "/downloads", idsOnly: true }),
  parityStep({ id: "download.sabr_get", tool: "avkit_download", action: "sabr_get", phase: "functional", args: () => ({ action: "sabr_get" }), restPath: () => "/downloads/sabr" }),
  simpleStep({
    id: "download.cookies_test",
    tool: "avkit_download",
    action: "cookies_test",
    phase: "functional",
    args: () => ({ action: "cookies_test", mode: "none" }),
    observe: async (ctx, result) => {
      const rest = await ctx.rest.send("POST", "/downloads/cookies/test", { mode: "none" });
      const ok = !result.isError && asRec(payload(result)).ok === true && asRec(rest.json).ok === true;
      return obs(ok, `MCP ok=${String(asRec(payload(result)).ok)} REST ok=${String(asRec(rest.json).ok)}`);
    },
  }),
  simpleStep({
    id: "download.sabr_force",
    tool: "avkit_download",
    action: "sabr_force",
    phase: "functional",
    args: () => ({ action: "sabr_force" }),
    observe: async (ctx, result) => {
      const s = asRec((await ctx.rest.get("/downloads/sabr")).json);
      return obs(!result.isError && s.mode === "active" && s.source === "forced", `REST sabr ${str(s.mode)}/${str(s.source)}`);
    },
  }),
  simpleStep({
    id: "download.sabr_check",
    tool: "avkit_download",
    action: "sabr_check",
    phase: "functional",
    args: () => ({ action: "sabr_check" }),
    observe: async (ctx, result) => {
      const s = asRec((await ctx.rest.get("/downloads/sabr")).json);
      const ok = !result.isError && s.checked_at !== null && subsetEqual(payload(result), s);
      return obs(ok, `REST sabr ${str(s.mode)} checked_at=${str(s.checked_at)}`, result.isError ? result.text : null);
    },
  }),
  simpleStep({
    id: "download.sabr_clear",
    tool: "avkit_download",
    action: "sabr_clear",
    phase: "functional",
    args: () => ({ action: "sabr_clear" }),
    observe: async (ctx, result) => {
      const s = asRec((await ctx.rest.get("/downloads/sabr")).json);
      return obs(!result.isError && s.mode === "inactive", `REST sabr ${str(s.mode)}`);
    },
  }),
  {
    ...settingsStep("download.setup", "downloader", () => ({ quality: "lowest" })),
    execute: async (ctx) => {
      await rememberSettings(ctx, "downloader", ["quality"]);
      return settingsStep("download.setup", "downloader", () => ({ quality: "lowest" })).execute(ctx);
    },
  },
  addDownload("download.add.a", "download_url_a", "dl_a"),
  addDownload("download.add.b", "download_url_b", "dl_b"),
  addDownload("download.add.c", "download_url_c", "dl_c"),
  simpleStep({
    id: "download.apply_defaults",
    tool: "avkit_download",
    action: "apply_defaults",
    depends_on: ["download.add.a", "download.add.b", "download.add.c"],
    args: () => ({ action: "apply_defaults" }),
    observe: async (ctx, result) => {
      const updated = asRec(payload(result)).updated;
      const rows = items(await downloads(ctx));
      const allLowest = rows.length === 3 && rows.every((r) => r.quality === "lowest");
      return obs(!result.isError && updated === 3 && allLowest, `updated=${String(updated)}; REST qualities ${rows.map((r) => str(r.quality)).join(",")}`);
    },
  }),
  orderStep("download.reorder", ["download.apply_defaults"], ["dl_c", "dl_a", "dl_b"]),
  parityStep({ id: "download.list", tool: "avkit_download", action: "list", depends_on: ["download.reorder"], args: () => ({ action: "list" }), restPath: () => "/downloads", idsOnly: true }),
  parityStep({
    id: "download.get",
    tool: "avkit_download",
    action: "get",
    depends_on: ["download.add.a"],
    args: (ctx) => ({ action: "get", id: ctx.state.get("dl_a") }),
    restPath: (ctx) => `/downloads/${str(ctx.state.get("dl_a"))}`,
  }),
  simpleStep({
    id: "download.start",
    tool: "avkit_download",
    action: "start",
    depends_on: ["download.reorder"],
    args: () => ({ action: "start" }),
    observe: async (ctx, result) => {
      const hit = await waitDownload("dl_c", (row) => row.status === "Downloading", T.queue)(ctx);
      return obs(!result.isError && hit !== null, hit ? "REST c Downloading" : "c never Downloading");
    },
  }),
  simpleStep({
    id: "download.cancel",
    tool: "avkit_download",
    action: "cancel",
    depends_on: ["download.start"],
    args: () => ({ action: "cancel" }),
    observe: async (ctx, result) => {
      const hit = await waitDownload("dl_c", (row, proc) => row.status === "Cancelled" && proc !== "Processing", T.queue)(ctx);
      if (hit) return obs(!result.isError, `REST c Cancelled, processor ${hit.proc}`);
      // R2-1: report the job's own terminal state and error, e.g. a media fetch that failed first.
      const row = asRec((await ctx.rest.get(`/downloads/${str(ctx.state.get("dl_c"))}`)).json);
      return obs(false, `c never Cancelled; REST c ${str(row.status)}`, str(row.error_message) || null);
    },
  }),
  simpleStep({
    id: "download.reset",
    tool: "avkit_download",
    action: "reset",
    depends_on: ["download.cancel"],
    args: (ctx) => ({ action: "reset", id: ctx.state.get("dl_c") }),
    observe: async (ctx, result) => {
      const row = asRec((await ctx.rest.get(`/downloads/${str(ctx.state.get("dl_c"))}`)).json);
      return obs(!result.isError && row.status === "Pending", `REST c ${str(row.status)}`);
    },
  }),
  orderStep("download.reorder.back", ["download.reset"], ["dl_a", "dl_c", "dl_b"]),
  simpleStep({
    id: "download.start.again",
    tool: "avkit_download",
    action: "start",
    depends_on: ["download.reorder.back"],
    args: () => ({ action: "start" }),
    observe: async (ctx, result) => {
      const hit = await waitDownload("dl_a", (row) => row.status !== "Pending", T.queue)(ctx);
      return obs(!result.isError && hit !== null, hit ? `REST a ${str(hit.row.status)}` : "a never left Pending");
    },
  }),
  simpleStep({
    id: "download.pause",
    tool: "avkit_download",
    action: "pause",
    depends_on: ["download.start.again"],
    args: () => ({ action: "pause" }),
    observe: async (ctx, result) => {
      const hit = await pollJson(ctx, "/downloads", T.download, (json) => (processorState(json) === "Paused" ? json : null));
      return obs(!result.isError && hit !== null, hit ? "REST processor Paused" : "processor never Paused");
    },
  }),
  simpleStep({
    id: "download.resume",
    tool: "avkit_download",
    action: "resume",
    depends_on: ["download.pause"],
    args: () => ({ action: "resume" }),
    observe: async (ctx, result) => {
      const proc = processorState(await downloads(ctx));
      return obs(!result.isError && proc === "Processing", `REST processor ${proc}`, result.isError ? result.text : null);
    },
  }),
  simpleStep({
    id: "download.stop",
    tool: "avkit_download",
    action: "stop",
    depends_on: ["download.resume"],
    args: () => ({ action: "stop" }),
    observe: async (ctx, result) => {
      const hit = await pollJson(ctx, "/downloads", T.queue, (json) => (processorState(json) === "Idle" ? json : null));
      return obs(!result.isError && hit !== null, hit ? "REST processor Idle" : "processor never Idle");
    },
  }),
  simpleStep({
    id: "download.get.done",
    tool: "avkit_download",
    action: "get",
    depends_on: ["download.stop"],
    args: (ctx) => ({ action: "get", id: ctx.state.get("dl_a") }),
    observe: async (ctx, result) => {
      const row = asRec((await ctx.rest.get(`/downloads/${str(ctx.state.get("dl_a"))}`)).json);
      if (result.isError || row.status !== "Done") return obs(false, `REST a ${str(row.status)}`, str(row.error_message) || null);
      const f = fileReport(str(row.file_path), ctx.root);
      return obs(f.ok && subsetEqual(payload(result), row), `REST a Done; ${f.detail}`);
    },
  }),
  destructiveStep({
    id: "download.remove",
    tool: "avkit_download",
    action: "remove",
    depends_on: ["download.get.done"],
    args: (ctx) => ({ action: "remove", id: ctx.state.get("dl_a") }),
    probe: async (ctx) => (await ctx.rest.get(`/downloads/${str(ctx.state.get("dl_a"))}`)).status,
    onConfirmed: (ctx) => ctx.ledger.remove("download", str(ctx.state.get("dl_a"))),
  }),
  destructiveStep({
    id: "download.clear",
    tool: "avkit_download",
    action: "clear",
    depends_on: ["download.remove"],
    args: () => ({ action: "clear" }),
    probe: async (ctx) => items(await downloads(ctx)).length,
    onConfirmed: (ctx) => {
      ctx.ledger.remove("download", str(ctx.state.get("dl_b")));
      ctx.ledger.remove("download", str(ctx.state.get("dl_c")));
    },
  }),
  {
    ...settingsStep("download.setup.restore", "downloader", (ctx) => asRec(ctx.state.get("orig:downloader")), ["download.setup"]),
  },
];

// ---------------------------------------------------------------- transcripts

async function transcriptJob(ctx: StepContext): Promise<Rec> {
  return asRec((await ctx.rest.get(`/transcripts/${str(ctx.state.get("tr_id"))}`)).json);
}

function transcriptControl(
  id: string,
  action: "start" | "pause" | "resume" | "stop",
  depends_on: string[],
  wantStatus: string,
  timeoutMs: number,
): StepSpec {
  return simpleStep({
    id,
    tool: "avkit_transcript",
    action,
    depends_on,
    args: () => ({ action }),
    observe: async (ctx, result) => {
      const hit = await ctx.poll(async () => {
        const job = await transcriptJob(ctx);
        return job.status === wantStatus ? job : null;
      }, timeoutMs);
      const now = hit ?? (await transcriptJob(ctx));
      return obs(!result.isError && hit !== null, `REST job ${str(now.status)} (want ${wantStatus})`, result.isError ? result.text : str(now.error_message) || null);
    },
  });
}

function transcriptResume(id: string, depends_on: string[], timeoutMs: number): StepSpec {
  return simpleStep({
    id,
    tool: "avkit_transcript",
    action: "resume",
    depends_on,
    args: () => ({ action: "resume" }),
    observe: async (ctx, result) => {
      const hit = await ctx.poll(async () => {
        const job = await transcriptJob(ctx);
        // A Skipped item (no captions) keeps the poll going so a later item can be fetched; a
        // Failed one ends it (compile then decides). Pending means nothing was processed yet.
        const done = typeof job.transcripts_done === "number" ? job.transcripts_done : 0;
        return job.status === "Processing" && (done >= 1 || str(job.last_item_status) === "Failed") ? job : null;
      }, timeoutMs);
      const now = hit ?? (await transcriptJob(ctx));
      const detail = `REST job ${str(now.status)} (want Processing), transcripts_done ${String(now.transcripts_done ?? 0)}, last_item_status ${str(now.last_item_status)}`;
      return obs(!result.isError && hit !== null, detail, result.isError ? result.text : str(now.error_message) || null);
    },
  });
}

/** Entries in a compiled volume's `## Contents` list: one per Done item (_volume_markdown). */
function volumeSections(file: string): number {
  const lines = readFileSync(file, "utf8").split(/\r?\n/);
  const start = lines.indexOf("## Contents");
  if (start < 0) return 0;
  let n = 0;
  for (const line of lines.slice(start + 1)) {
    if (line.trim() === "") break;
    if (line.startsWith("- [")) n += 1;
  }
  return n;
}

function transcriptTransition(id: string, action: "requeue" | "retry", depends_on: string[], expectConflict: boolean): StepSpec {
  return simpleStep({
    id,
    tool: "avkit_transcript",
    action,
    depends_on,
    expectError: expectConflict,
    args: (ctx) => ({ action, id: ctx.state.get("tr_id") }),
    observe: async (ctx, result) => {
      const job = await transcriptJob(ctx);
      if (expectConflict) {
        const ok = /ConflictError|illegal transcript transition/.test(result.text) && job.status === "Pending";
        return obs(ok, `409 contract: ${result.text.slice(0, 120)}; REST job ${str(job.status)}`);
      }
      return obs(!result.isError && job.status === "Pending", `REST job ${str(job.status)}`);
    },
  });
}

const TRANSCRIPT_STEPS: StepSpec[] = [
  parityStep({ id: "transcript.list.empty", tool: "avkit_transcript", action: "list", args: () => ({ action: "list" }), restPath: () => "/transcripts", idsOnly: true }),
  {
    ...settingsStep("transcript.setup", "transcript", () => ({ delay_between_requests: 3, max_retries: 0 })),
    execute: async (ctx) => {
      await rememberSettings(ctx, "transcript", ["delay_between_requests", "max_retries"]);
      return settingsStep("transcript.setup", "transcript", () => ({ delay_between_requests: 3, max_retries: 0 })).execute(ctx);
    },
  },
  simpleStep({
    id: "transcript.add",
    tool: "avkit_transcript",
    action: "add",
    depends_on: ["transcript.setup"],
    args: (ctx) => ({ action: "add", channel_url: ctx.fixtures.transcript_source_url }),
    observe: async (ctx, result) => {
      if (result.isError) return obs(false, `MCP error: ${result.text.slice(0, 200)}`);
      const id = ctx.firstId(result);
      if (!id) return obs(false, "no job id in MCP result");
      ctx.ledger.register("transcript", id);
      ctx.state.set("tr_id", id);
      const job = await transcriptJob(ctx);
      const ok = job.status === "Pending" && Number(job.video_count) >= 4 && within(str(job.output_dir), ctx.root);
      return obs(ok, `REST job ${str(job.status)} video_count=${str(job.video_count)} output_dir in root=${String(within(str(job.output_dir), ctx.root))}`);
    },
  }),
  parityStep({ id: "transcript.list", tool: "avkit_transcript", action: "list", depends_on: ["transcript.add"], args: () => ({ action: "list" }), restPath: () => "/transcripts", idsOnly: true }),
  parityStep({
    id: "transcript.get",
    tool: "avkit_transcript",
    action: "get",
    depends_on: ["transcript.add"],
    args: (ctx) => ({ action: "get", id: ctx.state.get("tr_id") }),
    restPath: (ctx) => `/transcripts/${str(ctx.state.get("tr_id"))}`,
  }),
  simpleStep({
    id: "transcript.reorder",
    tool: "avkit_transcript",
    action: "reorder",
    depends_on: ["transcript.add"],
    args: (ctx) => ({ action: "reorder", job_ids: [ctx.state.get("tr_id")] }),
    observe: async (ctx, result) => {
      const got = ids((await ctx.rest.get("/transcripts")).json);
      return obs(!result.isError && isDeepStrictEqual(got, [str(ctx.state.get("tr_id"))]), `REST order ${got.length} job(s)`);
    },
  }),
  // Pause lands at the next item boundary (transcript.py:412-423), so Processing → Paused is deterministic.
  transcriptControl("transcript.start", "start", ["transcript.reorder"], "Processing", T.transcript),
  transcriptControl("transcript.pause", "pause", ["transcript.start"], "Paused", T.transcript),
  // Plan row: resume, then poll until an item is terminal (a fetched transcript, or a Failed item).
  // Pause is checked before item 0 too, so Paused alone never proves a fetch.
  transcriptResume("transcript.resume", ["transcript.pause"], T.transcript),
  transcriptControl("transcript.pause.again", "pause", ["transcript.resume"], "Paused", T.transcript),
  // Worker thread has exited after the pause, so stop runs _apply_stop: Paused → Cancelled (:546-553).
  transcriptControl("transcript.stop", "stop", ["transcript.pause.again"], "Cancelled", T.transcript),
  transcriptTransition("transcript.requeue", "requeue", ["transcript.stop"], false),
  // Plan row: requeue and retry each meet the 409 contract once (Pending -> Pending is illegal).
  transcriptTransition("transcript.requeue.conflict", "requeue", ["transcript.requeue"], true),
  transcriptTransition("transcript.retry.conflict", "retry", ["transcript.requeue"], true),
  transcriptControl("transcript.start.again", "start", ["transcript.requeue"], "Processing", T.transcript),
  transcriptControl("transcript.pause.third", "pause", ["transcript.start.again"], "Paused", T.transcript),
  transcriptControl("transcript.stop.again", "stop", ["transcript.pause.third"], "Cancelled", T.transcript),
  transcriptTransition("transcript.retry", "retry", ["transcript.stop.again"], false),
  simpleStep({
    id: "transcript.compile",
    tool: "avkit_transcript",
    action: "compile",
    depends_on: ["transcript.retry"],
    args: (ctx) => ({ action: "compile", id: ctx.state.get("tr_id") }),
    observe: async (ctx, result) => {
      if (result.isError) return obs(false, `MCP error: ${result.text.slice(0, 200)}`);
      const p = asRec(payload(result));
      const files = (Array.isArray(p.compiled_paths) ? p.compiled_paths : []).map(str);
      if (files.length === 0) return obs(false, `compile returned no paths: ${result.text.slice(0, 160)}`);
      const reports = files.map((f) => fileReport(f, ctx.root));
      const job = await transcriptJob(ctx);
      const done = typeof job.transcripts_done === "number" ? job.transcripts_done : 0;
      const items = `transcripts_done ${done}, last_item_status ${str(job.last_item_status)}`;
      // A volume of headings only is the G25 hollow case: compile ran, nothing was fetched.
      if (done < 1) return obs(false, `no transcript fetched (${items}); ${reports.map((r) => r.detail).join("; ")}`);
      const sections = reports.every((r) => r.ok) ? files.reduce((n, f) => n + volumeSections(f), 0) : -1;
      const detail = `${reports.map((r) => r.detail).join("; ")}; ${sections} section(s), transcripts_done ${done}`;
      return obs(reports.every((r) => r.ok) && sections === done, detail);
    },
  }),
  destructiveStep({
    id: "transcript.remove",
    tool: "avkit_transcript",
    action: "remove",
    depends_on: ["transcript.add"],
    needs: ["tr_id"],
    args: (ctx) => ({ action: "remove", id: ctx.state.get("tr_id") }),
    probe: async (ctx) => (await ctx.rest.get(`/transcripts/${str(ctx.state.get("tr_id"))}`)).status,
    onConfirmed: (ctx) => ctx.ledger.remove("transcript", str(ctx.state.get("tr_id"))),
  }),
  {
    ...settingsStep("transcript.setup.restore", "transcript", (ctx) => asRec(ctx.state.get("orig:transcript")), ["transcript.setup"]),
  },
];

// ---------------------------------------------------------------- conversions

async function conversions(ctx: StepContext): Promise<Rec> {
  return asRec((await ctx.rest.get("/conversions")).json);
}

function addConversion(id: string, stateKey: string, file: string, seconds: number, size: string): StepSpec {
  return simpleStep({
    id,
    tool: "avkit_convert",
    action: "add",
    args: (ctx) => ({ action: "add", kind: "compress", paths: [ctx.state.get(`${stateKey}:src`) ?? makeSource(ctx, stateKey, file, seconds, size)] }),
    observe: async (ctx, result) => {
      if (result.isError) return obs(false, `MCP error: ${result.text.slice(0, 200)}`);
      const jobId = ctx.firstId(result);
      if (!jobId) return obs(false, "no job id in MCP result");
      ctx.ledger.register("conversion", jobId);
      ctx.state.set(stateKey, jobId);
      const row = asRec((await ctx.rest.get(`/conversions/${jobId}`)).json);
      return obs(row.status === "Pending" && within(str(row.output_path), ctx.root), `REST ${str(row.status)} output in root=${String(within(str(row.output_path), ctx.root))}`);
    },
  });
}

function makeSource(ctx: StepContext, stateKey: string, file: string, seconds: number, size: string): string {
  const made = makeVideo(ctx, file, seconds, size);
  ctx.state.set(`${stateKey}:src`, made);
  return made;
}

function waitConversion(stateKey: string, want: (row: Rec, proc: string) => boolean, timeoutMs: number) {
  return async (ctx: StepContext) =>
    pollJson(ctx, "/conversions", timeoutMs, (json) => {
      const row = rowById(json, str(ctx.state.get(stateKey)));
      return row && want(row, processorState(json)) ? { row, proc: processorState(json) } : null;
    });
}

function convertControl(
  id: string,
  action: "start" | "pause" | "resume" | "cancel",
  depends_on: string[],
  until: (ctx: StepContext) => Promise<{ proc: string } | null>,
  label: string,
): StepSpec {
  return simpleStep({
    id,
    tool: "avkit_convert",
    action,
    depends_on,
    args: () => ({ action }),
    observe: async (_ctx, result) => {
      const hit = await until(_ctx);
      return obs(!result.isError && hit !== null, hit ? `${label}; processor ${hit.proc}` : `never: ${label}`, result.isError ? result.text : null);
    },
  });
}

const CONVERT_STEPS: StepSpec[] = [
  parityStep({ id: "convert.list.empty", tool: "avkit_convert", action: "list", args: () => ({ action: "list" }), restPath: () => "/conversions", idsOnly: true }),
  parityStep({ id: "convert.gpu", tool: "avkit_convert", action: "gpu", phase: "functional", args: () => ({ action: "gpu" }), restPath: () => "/conversions/gpu" }),
  simpleStep({
    id: "convert.gpu_refresh",
    tool: "avkit_convert",
    action: "gpu_refresh",
    phase: "functional",
    args: () => ({ action: "gpu_refresh" }),
    observe: async (ctx, result) => {
      const rest = asRec((await ctx.rest.get("/conversions/gpu")).json);
      const ok = !result.isError && rest.checked_at === asRec(payload(result)).checked_at;
      return obs(ok, `REST checked_at=${str(rest.checked_at)}`);
    },
  }),
  addConversion("convert.add.long1", "cv_l1", "long1.mp4", 10, "1280x720"),
  addConversion("convert.add.short", "cv_s", "short.mp4", 2, "320x240"),
  addConversion("convert.add.long2", "cv_l2", "long2.mp4", 10, "1280x720"),
  parityStep({ id: "convert.list", tool: "avkit_convert", action: "list", depends_on: ["convert.add.long1", "convert.add.short", "convert.add.long2"], args: () => ({ action: "list" }), restPath: () => "/conversions", idsOnly: true }),
  parityStep({
    id: "convert.get",
    tool: "avkit_convert",
    action: "get",
    depends_on: ["convert.add.long1"],
    args: (ctx) => ({ action: "get", id: ctx.state.get("cv_l1") }),
    restPath: (ctx) => `/conversions/${str(ctx.state.get("cv_l1"))}`,
  }),
  convertControl("convert.start", "start", ["convert.list"], waitConversion("cv_l1", (r) => r.status === "Processing", T.queue), "long1 Processing"),
  convertControl("convert.cancel", "cancel", ["convert.start"], waitConversion("cv_l1", (r, p) => r.status === "Cancelled" && p === "Idle", T.queue), "long1 Cancelled"),
  simpleStep({
    id: "convert.reset",
    tool: "avkit_convert",
    action: "reset",
    depends_on: ["convert.cancel"],
    args: (ctx) => ({ action: "reset", id: ctx.state.get("cv_l1") }),
    observe: async (ctx, result) => {
      const row = asRec((await ctx.rest.get(`/conversions/${str(ctx.state.get("cv_l1"))}`)).json);
      return obs(!result.isError && row.status === "Pending", `REST long1 ${str(row.status)}`);
    },
  }),
  simpleStep({
    id: "convert.reorder",
    tool: "avkit_convert",
    action: "reorder",
    depends_on: ["convert.reset"],
    args: (ctx) => ({ action: "reorder", job_ids: ["cv_s", "cv_l1", "cv_l2"].map((k) => ctx.state.get(k)) }),
    observe: async (ctx, result) => {
      const want = ["cv_s", "cv_l1", "cv_l2"].map((k) => str(ctx.state.get(k)));
      const got = ids(await conversions(ctx));
      return obs(!result.isError && isDeepStrictEqual(got, want), `REST order matches=${String(isDeepStrictEqual(got, want))}`);
    },
  }),
  convertControl("convert.start.again", "start", ["convert.reorder"], waitConversion("cv_s", (r) => r.status !== "Pending", T.queue), "short started"),
  // Pause is deferred until the current job ends (walkthrough §Row-3 pins), then the processor is Paused.
  convertControl("convert.pause", "pause", ["convert.start.again"], async (ctx) => pollJson(ctx, "/conversions", T.convert, (j) => (processorState(j) === "Paused" ? { proc: "Paused" } : null)), "processor Paused"),
  convertControl("convert.resume", "resume", ["convert.pause"], async (ctx) => {
    const proc = processorState(await conversions(ctx));
    return proc === "Processing" ? { proc } : null;
  }, "processor Processing"),
  convertControl("convert.cancel.again", "cancel", ["convert.resume"], async (ctx) => pollJson(ctx, "/conversions", T.queue, (j) => (processorState(j) === "Idle" && items(j).some((r) => r.status === "Cancelled") ? { proc: "Idle" } : null)), "a job Cancelled, processor Idle"),
  simpleStep({
    id: "convert.get.done",
    tool: "avkit_convert",
    action: "get",
    depends_on: ["convert.cancel.again"],
    args: (ctx) => ({ action: "get", id: ctx.state.get("cv_s") }),
    observe: async (ctx, result) => {
      const row = asRec((await ctx.rest.get(`/conversions/${str(ctx.state.get("cv_s"))}`)).json);
      if (result.isError || row.status !== "Done") return obs(false, `REST short ${str(row.status)}`, str(row.error_message) || null);
      const f = fileReport(str(row.output_path), ctx.root);
      return obs(f.ok, `REST short Done; ${f.detail}`);
    },
  }),
  destructiveStep({
    id: "convert.remove",
    tool: "avkit_convert",
    action: "remove",
    depends_on: ["convert.get.done"],
    args: (ctx) => ({ action: "remove", id: ctx.state.get("cv_s") }),
    probe: async (ctx) => (await ctx.rest.get(`/conversions/${str(ctx.state.get("cv_s"))}`)).status,
    onConfirmed: (ctx) => ctx.ledger.remove("conversion", str(ctx.state.get("cv_s"))),
  }),
  destructiveStep({
    id: "convert.clear",
    tool: "avkit_convert",
    action: "clear",
    depends_on: ["convert.remove"],
    args: () => ({ action: "clear" }),
    probe: async (ctx) => items(await conversions(ctx)).length,
    onConfirmed: (ctx) => {
      ctx.ledger.remove("conversion", str(ctx.state.get("cv_l1")));
      ctx.ledger.remove("conversion", str(ctx.state.get("cv_l2")));
    },
  }),
];

// ---------------------------------------------------------------- captures

const CRC_TABLE = Array.from({ length: 256 }, (_, n) => {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});

function crc32(buf: Buffer): number {
  let c = 0xffffffff;
  for (const byte of buf) c = CRC_TABLE[(c ^ byte) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

/** A 64x64 opaque PNG for the container seed (no image dependency). */
function seedPng(file: string): void {
  const w = 64;
  const h = 64;
  const raw = Buffer.concat(Array.from({ length: h }, () => Buffer.concat([Buffer.from([0]), Buffer.alloc(w * 3, 0x40)])));
  const chunk = (type: string, data: Buffer) => {
    const len = Buffer.alloc(4);
    len.writeUInt32BE(data.length);
    const td = Buffer.concat([Buffer.from(type, "latin1"), data]);
    const crc = Buffer.alloc(4);
    crc.writeUInt32BE(crc32(td) >>> 0);
    return Buffer.concat([len, td, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8;
  ihdr[9] = 2;
  const png = Buffer.concat([PNG_SIGNATURE, chunk("IHDR", ihdr), chunk("IDAT", deflateSync(raw)), chunk("IEND", Buffer.alloc(0))]);
  mkdirSync(path.dirname(file), { recursive: true });
  writeFileSync(file, png);
}

function shotFiles(row: Rec): string[] {
  return [row.original_path, row.annotated_path, row.sidecar_path].map(str).filter(Boolean);
}

async function captureDetail(ctx: StepContext): Promise<{ status: number; row: Rec }> {
  const res = await ctx.rest.get(`/captures/${str(ctx.state.get("shot_id"))}`);
  return { status: res.status, row: asRec(res.json) };
}

function sha256Of(file: string): string | null {
  return file && existsSync(file) ? createHash("sha256").update(readFileSync(file)).digest("hex") : null;
}

/** AUDIT_STEPS flatten probe: the original's bytes, the annotated copy, and the isolated backup folder. */
async function flattenProbe(ctx: StepContext): Promise<{ status: number; original_sha256: string | null; annotated_exists: boolean; backup_count: number }> {
  const { status, row } = await captureDetail(ctx);
  const dir = ctx.out("capture_backups");
  const annotated = str(row.annotated_path);
  return {
    status,
    original_sha256: sha256Of(str(row.original_path)),
    annotated_exists: annotated !== "" && existsSync(annotated),
    backup_count: existsSync(dir) ? readdirSync(dir).filter((f) => f.toLowerCase().endsWith(".png")).length : 0,
  };
}

const CAPTURE_STEPS: StepSpec[] = [
  parityStep({ id: "capture.list.empty", tool: "avkit_capture", action: "list", args: () => ({ action: "list" }), restPath: () => "/captures", idsOnly: true }),
  {
    id: "capture.capture",
    tool: "avkit_capture",
    action: "capture",
    phase: "lifecycle",
    depends_on: [],
    execute: async (ctx) => {
      const result = await ctx.call("avkit_capture", { action: "capture", mode: "fullscreen" });
      let observable: ObservableResult;
      const id = result.isError ? null : ctx.firstId(result);
      if (id) {
        ctx.ledger.register("capture", id);
        ctx.state.set("shot_id", id);
        const { status, row } = await captureDetail(ctx);
        const f = fileReport(str(row.original_path), ctx.root);
        observable = obs(status === 200 && f.ok, `REST shot ${status}; ${f.detail}`);
      } else {
        observable = obs(false, `MCP error: ${result.text.slice(0, 200)}`);
      }
      if (!id && ctx.mode === "container") {
        // D-8: the container seeds one shot through REST register mode so the dependents still run.
        const file = path.join(ctx.out("captures"), "audit-seed.png");
        seedPng(file);
        const seeded = await ctx.rest.send("POST", "/captures", { mode: "register", path: file, source: "scan" });
        const seededId = str(asRec(asRec(seeded.json).item).id);
        if (seeded.status === 201 && seededId) {
          ctx.ledger.register("capture", seededId);
          ctx.state.set("shot_id", seededId);
        }
      }
      return { kind: "simple", isError: result.isError, expectError: false, observable, text: result.text };
    },
  },
  parityStep({
    id: "capture.list",
    tool: "avkit_capture",
    action: "list",
    needs: ["shot_id"],
    args: () => ({ action: "list" }),
    restPath: () => "/captures",
    idsOnly: true,
    extra: (ctx, mcp) => (ids(mcp).includes(str(ctx.state.get("shot_id"))) ? null : "shot missing from list"),
  }),
  parityStep({
    id: "capture.get",
    tool: "avkit_capture",
    action: "get",
    needs: ["shot_id"],
    args: (ctx) => ({ action: "get", id: ctx.state.get("shot_id") }),
    restPath: (ctx) => `/captures/${str(ctx.state.get("shot_id"))}`,
  }),
  simpleStep({
    id: "capture.image",
    tool: "avkit_capture",
    action: "image",
    needs: ["shot_id"],
    expectError: isImageRefusal,
    args: (ctx) => ({ action: "image", id: ctx.state.get("shot_id") }),
    observe: async (ctx, result) => {
      const restPath = `/captures/${str(ctx.state.get("shot_id"))}/image`;
      if (isImageRefusal(result)) return refusedImageObservation(await ctx.rest.bytes(restPath));
      if (result.isError || !result.image) return obs(false, `no image content: ${result.text.slice(0, 160)}`);
      const mcpBytes = Buffer.from(result.image.data, "base64");
      const rest = await ctx.rest.bytes(restPath);
      const same = rest.status === 200 && Buffer.compare(mcpBytes, Buffer.from(rest.bytes)) === 0;
      const png = mcpBytes.subarray(0, 8).equals(PNG_SIGNATURE);
      return obs(same && png, `MCP image ${mcpBytes.length} B == REST ${rest.bytes.length} B: ${String(same)}; PNG ${String(png)}`);
    },
  }),
  simpleStep({
    id: "capture.annotate",
    tool: "avkit_capture",
    action: "annotate",
    needs: ["shot_id"],
    args: (ctx) => ({
      action: "annotate",
      id: ctx.state.get("shot_id"),
      annotations: [{ type: "rect", x: 2, y: 2, width: 20, height: 20, color: "#ff0000", stroke_width: 2 }],
    }),
    observe: async (ctx, result) => {
      const { row } = await captureDetail(ctx);
      const annotated = fileReport(str(row.annotated_path), ctx.root);
      const sidecar = fileReport(str(row.sidecar_path), ctx.root);
      return obs(!result.isError && annotated.ok && sidecar.ok, `annotated ${annotated.detail}; sidecar ${sidecar.detail}`);
    },
  }),
  simpleStep({
    id: "capture.image.annotated",
    tool: "avkit_capture",
    action: "image",
    depends_on: ["capture.annotate"],
    expectError: isImageRefusal,
    args: (ctx) => ({ action: "image", id: ctx.state.get("shot_id"), variant: "annotated" }),
    observe: async (ctx, result) => {
      const restPath = `/captures/${str(ctx.state.get("shot_id"))}/image?variant=annotated`;
      if (isImageRefusal(result)) return refusedImageObservation(await ctx.rest.bytes(restPath));
      if (result.isError || !result.image) return obs(false, `no image content: ${result.text.slice(0, 160)}`);
      const mcpBytes = Buffer.from(result.image.data, "base64");
      const rest = await ctx.rest.bytes(restPath);
      const same = rest.status === 200 && Buffer.compare(mcpBytes, Buffer.from(rest.bytes)) === 0;
      return obs(same, `annotated MCP ${mcpBytes.length} B == REST: ${String(same)}`);
    },
  }),
  destructiveStep({
    id: "capture.flatten",
    tool: "avkit_capture",
    action: "flatten",
    depends_on: ["capture.annotate"],
    needs: ["shot_id"],
    userConfirm: true,
    args: (ctx) => ({ action: "flatten", id: ctx.state.get("shot_id") }),
    precondition: async (ctx) => {
      const p = await flattenProbe(ctx);
      if (p.status === 200 && p.original_sha256 && !ctx.state.has("pre_flatten_sha")) ctx.state.set("pre_flatten_sha", p.original_sha256);
      return obs(p.status === 200 && p.annotated_exists, `saved marks before flatten: ${JSON.stringify(p)}`);
    },
    probe: flattenProbe,
    // A confirmed flatten bakes (sha differs), drops the annotated copy and writes exactly one backup.
    confirmedEffect: (_ctx, before, after) => {
      const b = before as Awaited<ReturnType<typeof flattenProbe>>;
      const a = after as Awaited<ReturnType<typeof flattenProbe>>;
      return a.status === 200 && a.original_sha256 !== null && a.original_sha256 !== b.original_sha256
        && !a.annotated_exists && a.backup_count === b.backup_count + 1;
    },
  }),
  destructiveStep({
    id: "capture.revert",
    tool: "avkit_capture",
    action: "revert",
    depends_on: ["capture.flatten"],
    needs: ["shot_id", "pre_flatten_sha"],
    userConfirm: true,
    args: (ctx) => ({ action: "revert", id: ctx.state.get("shot_id") }),
    probe: async (ctx) => {
      const { status, row } = await captureDetail(ctx);
      return { status, original_sha256: sha256Of(str(row.original_path)) };
    },
    // A confirmed revert restores the bytes recorded before capture.flatten.
    confirmedEffect: (ctx, _before, after) =>
      (after as { original_sha256: string | null }).original_sha256 === str(ctx.state.get("pre_flatten_sha")),
  }),
  // CROP_MCP (MEU-130, D-492): an 8x8 crop of the shot is a new Crop shot, and the source's
  // bytes are the same before and after. Its own execute reads the source's SHA-256 first.
  {
    id: "capture.crop",
    tool: "avkit_capture",
    action: "crop",
    phase: "lifecycle",
    depends_on: ["capture.flatten"],
    execute: async (ctx) => {
      if (!ctx.state.has("shot_id")) return { kind: "blocked", by: "state:shot_id", detail: "shot_id was never established" };
      const before = await captureDetail(ctx);
      const sourceSha = sha256Of(str(before.row.original_path));
      const result = await ctx.call("avkit_capture", {
        action: "crop",
        id: ctx.state.get("shot_id"),
        x: 0,
        y: 0,
        width: 8,
        height: 8,
      });
      const id = result.isError ? null : ctx.firstId(result);
      let observable: ObservableResult;
      if (id) {
        ctx.ledger.register("capture", id);
        const crop = await ctx.rest.get(`/captures/${id}`);
        const row = asRec(crop.json);
        const f = fileReport(str(row.original_path), ctx.root);
        const after = await captureDetail(ctx);
        const unchanged = sourceSha !== null && sha256Of(str(after.row.original_path)) === sourceSha;
        const isCrop = crop.status === 200 && row.source === "Crop";
        observable = obs(
          isCrop && f.ok && unchanged,
          `REST crop ${crop.status} source ${str(row.source)}; ${f.detail}; source bytes unchanged ${String(unchanged)}`,
        );
      } else {
        observable = obs(false, `MCP error or no id: ${result.text.slice(0, 200)}`);
      }
      return { kind: "simple", isError: result.isError, expectError: false, observable, text: result.text };
    },
  },
  simpleStep({
    id: "capture.capture_interactive",
    tool: "avkit_capture",
    action: "capture_interactive",
    args: () => ({ action: "capture_interactive" }),
    observe: async (ctx, result) => {
      const id = result.isError ? null : ctx.firstId(result);
      if (!id) return obs(false, `MCP error or no id: ${result.text.slice(0, 160)}`);
      ctx.ledger.register("capture_request", id);
      ctx.state.set("capture_request", id);
      const rest = await ctx.rest.get("/captures/requests?status=pending");
      return obs(ids(rest.json).includes(id), `REST pending requests include ${id}: ${String(ids(rest.json).includes(id))}`);
    },
  }),
  parityStep({
    id: "capture.list_requests",
    tool: "avkit_capture",
    action: "list_requests",
    needs: ["capture_request"],
    args: () => ({ action: "list_requests", status: "pending" }),
    restPath: () => "/captures/requests?status=pending",
    idsOnly: true,
    extra: (ctx, mcp) => (ids(mcp).includes(str(ctx.state.get("capture_request"))) ? null : "request missing"),
  }),
  destructiveStep({
    id: "capture.remove",
    tool: "avkit_capture",
    action: "remove",
    userConfirm: true,
    needs: ["shot_id"],
    args: (ctx) => ({ action: "remove", id: ctx.state.get("shot_id") }),
    // 09 §remove: files (original, annotated, sidecar) are deleted, then the row.
    probe: async (ctx) => {
      const { status, row } = await captureDetail(ctx);
      const files = status === 200 ? shotFiles(row) : (ctx.state.get("shot_files") as string[] | undefined) ?? [];
      if (status === 200) ctx.state.set("shot_files", files);
      return { status, present: files.filter((f) => existsSync(f)).length };
    },
    onConfirmed: (ctx) => ctx.ledger.remove("capture", str(ctx.state.get("shot_id"))),
  }),
];

// ---------------------------------------------------------------- assembly

/** Phase 2/3 steps in execution order. */
export const AUDIT_PLAN: StepSpec[] = [
  ...SETTINGS_STEPS,
  ...HEALTH_STEPS,
  ...MODEL_STEPS_BEFORE_TTS,
  ...TTS_STEPS,
  ...MODEL_STEPS_AFTER_TTS,
  ...DOWNLOAD_STEPS,
  ...TRANSCRIPT_STEPS,
  ...CONVERT_STEPS,
  ...CAPTURE_STEPS,
];

/** `tool.action` for every step, in plan order (duplicates kept). */
export function planKeys(plan: StepSpec[]): string[] {
  return plan.map((s) => `${s.tool}.${s.action}`);
}
