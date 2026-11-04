/**
 * MEU-68 MCP live audit runner (`npm --prefix mcp-server run audit -- --mode …`).
 * Phase 1 discovery → ISOLATION_GUARD → Phase 2/3 AUDIT_PLAN → cleanup (CLEANUP_PREDICATE) →
 * tolerance (ENV_BOUND_AUDIT) → DELTA / BASELINE_UPDATE_RULE → report. It talks to the server
 * only over stdio (05 §Client) and checks state through REST_OBSERVER and the filesystem.
 */
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { isDeepStrictEqual, parseArgs } from "node:util";
import { REPO_ROOT, spawnBackend, type BackendHandle, type BackendLauncher } from "./backend.js";
import { ENV_BOUND_AUDIT } from "./census.js";
import {
  applyTolerance,
  BaselineError,
  classifyDiscovery,
  computeDelta,
  countedFailures,
  exitCode as computeExit,
  isolationGuard,
  isolationKeys,
  IsolationError,
  parseBaseline,
  refusalVerdict,
  regressionCount,
  stepVerdict,
  writeBaselineIfAllowed,
} from "./classify.js";
import { AuditClient, buildLaunch, type Launch } from "./client.js";
import { extractMetaActions, extractSchemaActions, GHOST_PATTERN } from "./discovery.js";
import { resolveFixtures, type Fixtures } from "./fixtures.js";
import { CleanupLedger, evaluateCleanup } from "./ledger.js";
import { RestObserver } from "./observer.js";
import { AUDIT_PLAN, NETWORK_STEP_URLS, payload, type OutSub, type StepContext, type StepOutcome, type StepSpec } from "./plan.js";
import { buildSummary, writeOutputs } from "./report.js";
import {
  AUDIT_TOOLS,
  type Baseline,
  type CleanupRecord,
  type DiscoveryResult,
  type EnvFacts,
  type IsolationRecord,
  type LaunchRecord,
  type Mode,
  type SettingsSchema,
  type StepRecord,
  type Summary,
  type ToolCallOutcome,
  type Verdict,
} from "./types.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_SERVER = path.resolve(HERE, "../../dist/index.js");
const SETTINGS_SCHEMA_URI = "avkit://settings/schema";

/** Every flag the CLI accepts (docs.test.ts checks the workflow and skill cite only these). */
export const CLI_FLAGS: readonly string[] = [
  "--mode",
  "--out",
  "--report",
  "--baseline",
  "--no-baseline",
  "--update-baseline",
  "--server",
  "--discovery-only",
  "--keep",
  "--agent",
  "--fixture",
];

/** ISOLATION_KEYS → ISOLATED_ROOT/out/<sub>. A schema key missing here fails the guard closed. */
const ISOLATION_SUBDIR: Record<string, OutSub> = {
  "downloader.path": "downloads",
  "transcript.output_dir": "transcripts",
  "tts.models_directory": "models",
  "tts.output_path": "tts",
  "converter.output_dir": "convert",
  "capture.inbox_dir": "captures",
  "capture.backup_dir": "capture_backups",
};

export class CliError extends Error {
  readonly exitCode = 4;
}

export type AuditOptions = {
  mode: Mode;
  out: string;
  report: string | null;
  baseline: string | null;
  noBaseline: boolean;
  updateBaseline: boolean;
  server: string;
  discoveryOnly: boolean;
  keep: boolean;
  agent: string;
  fixtures: Record<string, string>;
};

export type AuditDeps = {
  launcher?: BackendLauncher;
  steps?: StepSpec[];
  platform?: string;
  mutateLaunch?: (launch: Launch) => Launch;
};

export function parseCli(argv: string[]): AuditOptions {
  let values: Record<string, string | boolean | string[] | undefined>;
  try {
    ({ values } = parseArgs({
      args: argv,
      strict: true,
      allowPositionals: false,
      options: {
        mode: { type: "string" },
        out: { type: "string" },
        report: { type: "string" },
        baseline: { type: "string" },
        "no-baseline": { type: "boolean" },
        "update-baseline": { type: "boolean" },
        server: { type: "string" },
        "discovery-only": { type: "boolean" },
        keep: { type: "boolean" },
        agent: { type: "string" },
        fixture: { type: "string", multiple: true },
      },
    }));
  } catch (err) {
    throw new CliError(`usage: ${err instanceof Error ? err.message : String(err)}`);
  }
  const mode = values.mode;
  if (mode !== "container" && mode !== "authoritative") throw new CliError("--mode must be container or authoritative");
  const noBaseline = values["no-baseline"] === true;
  const baseline = typeof values.baseline === "string" ? path.resolve(values.baseline) : null;
  const updateBaseline = values["update-baseline"] === true;
  if (updateBaseline && !baseline) throw new CliError("--update-baseline needs --baseline <path> (the file it writes)");
  if (!noBaseline && !baseline) throw new CliError("pass --baseline <path> or --no-baseline; a missing baseline is never an empty one");
  const fixtures: Record<string, string> = {};
  for (const item of (values.fixture as string[] | undefined) ?? []) {
    const eq = item.indexOf("=");
    if (eq <= 0) throw new CliError(`--fixture expects key=value, got ${item}`);
    fixtures[item.slice(0, eq)] = item.slice(eq + 1);
  }
  const out = path.resolve(
    typeof values.out === "string" ? values.out : path.join(os.tmpdir(), `avkit-mcp-audit-out-${Date.now()}`),
  );
  return {
    mode,
    out,
    report: typeof values.report === "string" ? path.resolve(values.report) : null,
    baseline,
    noBaseline,
    updateBaseline,
    server: typeof values.server === "string" ? path.resolve(values.server) : DEFAULT_SERVER,
    discoveryOnly: values["discovery-only"] === true,
    keep: values.keep === true,
    agent: typeof values.agent === "string" ? values.agent : "unspecified",
    fixtures,
  };
}

function gitCommit(): string {
  const res = spawnSync("git", ["rev-parse", "HEAD"], { cwd: REPO_ROOT, encoding: "utf8" });
  return res.status === 0 ? res.stdout.trim() : "unknown";
}

function firstId(result: ToolCallOutcome): string | null {
  const p = payload(result) as Record<string, unknown> | null;
  if (!p || typeof p !== "object") return null;
  if (typeof p.id === "string") return p.id;
  const item = p.item as Record<string, unknown> | undefined;
  if (item && typeof item.id === "string") return item.id;
  const list = p.items as Record<string, unknown>[] | undefined;
  if (Array.isArray(list) && list[0] && typeof list[0].id === "string") return list[0].id;
  return null;
}

async function poll<T>(probe: () => Promise<T | null>, timeoutMs: number, intervalMs = 500): Promise<T | null> {
  const deadline = Date.now() + timeoutMs;
  for (;;) {
    const hit = await probe();
    if (hit !== null) return hit;
    if (Date.now() >= deadline) return null;
    await new Promise((r) => setTimeout(r, intervalMs));
  }
}

function errorText(o: StepOutcome): string | null {
  if (o.kind === "simple") {
    if (o.isError && !o.expectError) return o.text;
    if (o.observable && !o.observable.ok) return o.observable.errorMessage || o.observable.detail;
    return null;
  }
  if (o.kind === "destructive") return refusalVerdict(o.refusal).verdict === "pass" ? null : o.observable.detail;
  return null;
}

function toRecord(step: StepSpec, outcome: StepOutcome, ms: number): StepRecord {
  const base = {
    id: step.id,
    tool: step.tool,
    action: step.action,
    phase: step.phase,
    blocked_by: null as string | null,
    env_bound: null,
    ms,
  };
  if (outcome.kind === "blocked") {
    return { ...base, verdict: "blocked", reason: null, is_error: null, observable: outcome.detail, error: null, blocked_by: outcome.by };
  }
  if (outcome.kind === "destructive") {
    const v = refusalVerdict(outcome.refusal);
    return {
      ...base,
      verdict: v.verdict,
      reason: v.reason,
      is_error: outcome.refusal.confirmed.isError,
      observable: outcome.observable.detail,
      error: errorText(outcome),
      refusal: outcome.refusal,
    };
  }
  const v = stepVerdict({ expectError: outcome.expectError, isError: outcome.isError, observable: outcome.observable });
  return {
    ...base,
    verdict: v.verdict,
    reason: v.verdict === "fail" ? outcome.reason ?? v.reason : null,
    is_error: outcome.isError,
    observable: outcome.observable?.detail ?? null,
    error: errorText(outcome),
  };
}

const WORST: Verdict[] = ["fail", "blocked", "skip_env", "pass"];

/** One verdict per `tool.action`: the worst across its steps. */
function aggregate(records: StepRecord[]): { key: string; verdict: Verdict }[] {
  const by = new Map<string, Verdict>();
  for (const r of records) {
    const k = `${r.tool}.${r.action}`;
    const prev = by.get(k);
    if (!prev || WORST.indexOf(r.verdict) < WORST.indexOf(prev)) by.set(k, r.verdict);
  }
  return [...by.entries()].map(([key, verdict]) => ({ key, verdict }));
}

async function isolate(
  client: AuditClient,
  rest: RestObserver,
  root: string,
  out: (s: OutSub) => string,
): Promise<{ record: IsolationRecord; schema: SettingsSchema }> {
  const schema = JSON.parse(await client.readResourceText(SETTINGS_SCHEMA_URI)) as SettingsSchema;
  // First tool calls of the run: a token/config problem surfaces here (A3a).
  for (const ns of Object.keys(schema.namespaces)) {
    const r = await client.call("avkit_settings", { action: "get", namespace: ns });
    if (r.isError) throw new IsolationError(`settings.get ${ns}: ${r.text}`);
  }
  const keys = isolationKeys(schema);
  const mapping: Record<string, string> = {};
  for (const k of keys) {
    const sub = ISOLATION_SUBDIR[k];
    if (sub) {
      mapping[k] = out(sub);
      mkdirSync(mapping[k], { recursive: true });
    }
  }
  const byNs = new Map<string, Record<string, string>>();
  for (const [k, v] of Object.entries(mapping)) {
    const [ns, leaf] = k.split(".") as [string, string];
    byNs.set(ns, { ...(byNs.get(ns) ?? {}), [leaf]: v });
  }
  for (const [ns, values] of byNs) {
    const r = await client.call("avkit_settings", { action: "set", namespace: ns, ...values });
    if (r.isError) throw new IsolationError(`settings.set ${ns}: ${r.text}`);
  }
  const readBack: Record<string, Record<string, unknown>> = {};
  for (const k of keys) {
    const ns = k.split(".")[0];
    if (!readBack[ns]) readBack[ns] = ((await rest.get(`/settings/${ns}`)).json ?? {}) as Record<string, unknown>;
  }
  const guard = isolationGuard({ schema, mapping, readBack, root });
  return { record: { root, paths: guard.paths, ok: true, error: null }, schema };
}

async function readSettings(rest: RestObserver, schema: SettingsSchema): Promise<Record<string, Record<string, unknown>>> {
  const out: Record<string, Record<string, unknown>> = {};
  for (const ns of Object.keys(schema.namespaces)) out[ns] = ((await rest.get(`/settings/${ns}`)).json ?? {}) as Record<string, unknown>;
  return out;
}

async function bestEffort(fn: () => Promise<unknown>, notes: string[], label: string): Promise<void> {
  try {
    await fn();
  } catch (err) {
    notes.push(`${label}: ${err instanceof Error ? err.message : String(err)}`);
  }
}

/** Removes or restores what the steps left behind, through REST; returns counts and settings. */
async function cleanUp(
  rest: RestObserver,
  ledger: CleanupLedger,
  schema: SettingsSchema,
  snapshot: Record<string, Record<string, unknown>>,
  notes: string[],
): Promise<{ counts: Record<string, number>; settingsNow: Record<string, Record<string, unknown>> }> {
  for (const p of ["/downloads/stop", "/transcripts/stop", "/conversions/cancel"]) {
    await bestEffort(() => rest.send("POST", p), notes, p);
  }
  for (const { kind, id } of ledger.outstanding()) {
    await bestEffort(async () => {
      const route: Record<string, [string, string]> = {
        download: ["DELETE", `/downloads/${id}`],
        transcript: ["DELETE", `/transcripts/${id}`],
        conversion: ["DELETE", `/conversions/${id}`],
        capture: ["DELETE", `/captures/${id}`],
        capture_request: ["POST", `/captures/requests/${id}/cancel`],
        tts_job: ["DELETE", `/tts/${id}`],
      };
      const [method, p] = route[kind];
      const res = await rest.send(method, p, method === "POST" ? {} : undefined);
      if ([200, 204, 404, 409].includes(res.status)) ledger.remove(kind, id);
      else notes.push(`cleanup ${kind} ${id}: HTTP ${res.status}`);
    }, notes, `cleanup ${kind} ${id}`);
  }
  await bestEffort(() => rest.send("POST", "/models/unload"), notes, "models unload");
  const now = await readSettings(rest, schema);
  for (const [ns, values] of Object.entries(snapshot)) {
    const diff = Object.fromEntries(Object.entries(values).filter(([k, v]) => !isDeepStrictEqual(now[ns]?.[k], v)));
    if (Object.keys(diff).length > 0) await bestEffort(() => rest.send("PUT", `/settings/${ns}`, diff), notes, `restore ${ns}`);
  }
  const count = async (p: string) => {
    const res = await rest.get(p);
    const items = (res.json as { items?: unknown[] } | null)?.items;
    return Array.isArray(items) ? items.length : -1;
  };
  return {
    counts: {
      downloads: await count("/downloads"),
      transcripts: await count("/transcripts"),
      conversions: await count("/conversions"),
      captures: await count("/captures"),
      capture_requests: await count("/captures/requests?status=pending"),
    },
    settingsNow: await readSettings(rest, schema),
  };
}

/** Environment proof for the network census members: can yt-dlp extract the fixture at all? */
function youtubeExtractWorks(url: string): boolean {
  const code = [
    "import sys, yt_dlp",
    "with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as y:",
    "    y.extract_info(sys.argv[1], download=False)",
  ].join("\n");
  const res = spawnSync("uv", ["run", "python", "-c", code, url], {
    cwd: REPO_ROOT,
    encoding: "utf8",
    timeout: 180_000,
  });
  return res.status === 0;
}

/** True only when a direct yt-dlp test fetch (first bytes of the media) fails with `wall`. */
function mediaFetchBlocked(url: string, wall: RegExp): boolean {
  const code = [
    "import sys, tempfile, yt_dlp",
    "with tempfile.TemporaryDirectory() as d:",
    "    opts = {'quiet': True, 'no_warnings': True, 'format': 'worst', 'test': True, 'outtmpl': d + '/%(id)s.%(ext)s'}",
    "    try:",
    "        with yt_dlp.YoutubeDL(opts) as y:",
    "            y.download([sys.argv[1]])",
    "    except Exception as exc:",
    "        print(str(exc))",
    "        sys.exit(3)",
  ].join("\n");
  const res = spawnSync("uv", ["run", "python", "-c", code, url], {
    cwd: REPO_ROOT,
    encoding: "utf8",
    timeout: 180_000,
  });
  return res.status === 3 && wall.test(`${res.stdout ?? ""}${res.stderr ?? ""}`);
}

/** True only when the product's TranscriptAdapter is IP-blocked for the source's first video. */
function captionFetchBlocked(sourceUrl: string): boolean {
  const code = [
    "import sys, yt_dlp",
    "from avkit_core.domain.errors import TranscriptRetryableError",
    "from avkit_infra.transcript.adapter import TranscriptAdapter",
    "with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True, 'extract_flat': True}) as y:",
    "    info = y.extract_info(sys.argv[1], download=False)",
    "entries = info.get('entries') or [info]",
    "try:",
    "    TranscriptAdapter().get_transcript(entries[0]['id'], ['en'])",
    "except TranscriptRetryableError:",
    "    sys.exit(3)",
  ].join("\n");
  const res = spawnSync("uv", ["run", "python", "-c", code, sourceUrl], {
    cwd: REPO_ROOT,
    encoding: "utf8",
    timeout: 180_000,
  });
  return res.status === 3;
}

export async function runAudit(options: AuditOptions, deps: AuditDeps = {}): Promise<{ summary: Summary; exitCode: number }> {
  const launcher = deps.launcher ?? spawnBackend;
  const steps = deps.steps ?? AUDIT_PLAN;
  const platform = deps.platform ?? process.platform;
  mkdirSync(options.out, { recursive: true });
  const reportPath = options.report ?? path.join(options.out, "report.md");
  const root = mkdtempSync(path.join(os.tmpdir(), "avkit-mcp-audit-"));
  const outDir = (sub: OutSub) => path.join(root, "out", sub);
  const client = new AuditClient();
  const ledger = new CleanupLedger();
  const notes: string[] = [];
  const secrets: string[] = [];
  const records: StepRecord[] = [];
  const ghosts: string[] = [];
  let launch: LaunchRecord = { command: "node", args: [options.server], env_keys: [], initialized: false };
  let isolation: IsolationRecord = { root, paths: {}, ok: false, error: options.discoveryOnly ? "skipped (discovery-only)" : null };
  let discovery: DiscoveryResult = { status: "fail", tools: 0, actions: 0, findings: [], new: [], removed: [], ghost: [] };
  let baseline: Baseline | null = null;
  let backend: BackendHandle | null = null;
  let rest: RestObserver | null = null;
  let backendVersion: string | null = null;
  let runnerError: string | null = null;
  let isolationRefused = false;
  let schema: SettingsSchema | null = null;
  let snapshot: Record<string, Record<string, unknown>> = {};
  let fixtures: Fixtures | null = null;
  let toolList: { name: string; schemaActions: string[] | null; metaActions: string[] }[] = [];
  let counts: Record<string, number> = {};
  let settingsNow: Record<string, Record<string, unknown>> = {};

  try {
    fixtures = resolveFixtures(options.fixtures);
    // BASELINE_UPDATE_RULE: a missing file is exit 4 unless --no-baseline, with or without
    // --update-baseline, and before anything is spawned.
    if (!options.noBaseline && options.baseline) {
      if (!existsSync(options.baseline)) throw new BaselineError(`baseline ${options.baseline} not found`);
      baseline = parseBaseline(JSON.parse(readFileSync(options.baseline, "utf8")));
    }
    backend = await launcher(root);
    secrets.push(backend.guiToken, backend.mcpToken);
    rest = new RestObserver(backend.apiBase, backend.guiToken);
    const openapi = await rest.getOrigin("/openapi.json");
    const info = (openapi.json as { info?: { version?: unknown } } | null)?.info;
    backendVersion = typeof info?.version === "string" ? info.version : null;
    let built = buildLaunch({ serverPath: options.server, token: backend.mcpToken, appData: backend.appData, parentEnv: process.env });
    if (deps.mutateLaunch) built = deps.mutateLaunch(built);
    launch = { command: built.command, args: built.args, env_keys: Object.keys(built.env).sort(), initialized: false };
    await client.connect(built);
    launch.initialized = client.initialized;
    toolList = (await client.listTools()).map((t) => ({
      name: t.name,
      schemaActions: extractSchemaActions(t.inputSchema),
      metaActions: extractMetaActions(t._meta),
    }));
    if (!options.discoveryOnly) {
      try {
        const iso = await isolate(client, rest, root, outDir);
        isolation = iso.record;
        schema = iso.schema;
        snapshot = await readSettings(rest, schema);
      } catch (err) {
        isolationRefused = true;
        isolation = { root, paths: {}, ok: false, error: err instanceof Error ? err.message : String(err) };
      }
    }
    if (!options.discoveryOnly && !isolationRefused && schema) {
      const observer = rest;
      const ctx: StepContext = {
        mode: options.mode,
        platform,
        fixtures,
        root,
        out: outDir,
        call: (tool, args, opts) => client.call(tool, args, opts),
        rest: { get: (p) => observer.get(p), send: (m, p, b) => observer.send(m, p, b), bytes: (p) => observer.bytes(p) },
        ledger,
        state: new Map(),
        firstId,
        poll,
      };
      const byId = new Map<string, StepRecord>();
      for (const step of steps) {
        const started = Date.now();
        const blocker = step.depends_on.find((d) => byId.get(d)?.verdict !== "pass");
        let outcome: StepOutcome;
        if (blocker) {
          outcome = { kind: "blocked", by: blocker, detail: `${blocker} did not pass` };
        } else {
          try {
            outcome = await step.execute(ctx);
          } catch (err) {
            outcome = {
              kind: "simple",
              isError: false,
              expectError: false,
              observable: { ok: false, detail: `exception: ${err instanceof Error ? err.message : String(err)}` },
              text: "",
              reason: "exception",
            };
          }
        }
        const rec = toRecord(step, outcome, Date.now() - started);
        if (rec.is_error && GHOST_PATTERN.test(rec.error ?? "")) ghosts.push(`${rec.tool}.${rec.action}`);
        records.push(rec);
        byId.set(step.id, rec);
      }
    }
  } catch (err) {
    runnerError = err instanceof Error ? err.message : String(err);
    notes.push(`runner error: ${runnerError}`);
  }

  // Cleanup always runs (Zorivest §Cleanup Contract).
  if (rest && schema && !isolationRefused && !options.discoveryOnly) {
    try {
      ({ counts, settingsNow } = await cleanUp(rest, ledger, schema, snapshot, notes));
    } catch (err) {
      notes.push(`cleanup: ${err instanceof Error ? err.message : String(err)}`);
      counts = { cleanup_error: 1 };
    }
  }
  await client.close();
  let backendExited = backend === null;
  if (backend) backendExited = (await backend.stop()).exited;
  if (!options.keep) rmSync(root, { recursive: true, force: true, maxRetries: 5, retryDelay: 500 });
  const rootRemoved = !existsSync(root);
  const cleanup: CleanupRecord = evaluateCleanup({
    ledger,
    counts,
    settingsNow,
    // Steps ran → compare with the post-guard snapshot; otherwise nothing was changed or read.
    settingsSnapshot: schema && !isolationRefused && !options.discoveryOnly ? snapshot : settingsNow,
    backendExited,
    rootRemoved,
    keep: options.keep,
  });

  discovery = classifyDiscovery({ tools: toolList, expectedTools: AUDIT_TOOLS, baseline, ghosts });
  const env: EnvFacts = { platform };
  // The network proof is only gathered when a network census member already failed with its
  // signature, so the default test suite never touches YouTube (05 §Testing).
  const networkKeys = new Set(
    steps.filter((s) => s.id in NETWORK_STEP_URLS).map((s) => `${s.tool}.${s.action}`),
  );
  const networkCandidates = ENV_BOUND_AUDIT.filter((m) => networkKeys.has(m.key));
  if (options.mode === "container" && fixtures) {
    const probe: Record<string, boolean> = {};
    for (const member of networkCandidates) {
      const failing = records.filter(
        (r) => r.verdict === "fail" && `${r.tool}.${r.action}` === member.key && member.signature.test(r.error ?? ""),
      );
      if (failing.length === 0) continue;
      const urls = [...new Set(failing.map((r) => NETWORK_STEP_URLS[r.id]).map((k) => (k ? fixtures?.[k] : undefined)))];
      // Proof holds only if every failing step's own URL also fails a direct extract.
      probe[member.key] = !urls.every((url) => url !== undefined && !youtubeExtractWorks(url));
    }
    const cancel = ENV_BOUND_AUDIT.find((m) => m.key === "avkit_download.cancel");
    const cancelFailed = records.some(
      (r) => r.verdict === "fail" && cancel && `${r.tool}.${r.action}` === cancel.key && cancel.signature.test(r.error ?? ""),
    );
    if (cancel && cancelFailed) probe[cancel.key] = !mediaFetchBlocked(fixtures.download_url_c, cancel.signature);
    const compile = ENV_BOUND_AUDIT.find((m) => m.key === "avkit_transcript.compile");
    const compileFailed = records.some(
      (r) => r.verdict === "fail" && compile && `${r.tool}.${r.action}` === compile.key && compile.signature.test(r.error ?? ""),
    );
    if (compile && compileFailed) probe[compile.key] = !captionFetchBlocked(fixtures.transcript_source_url);
    if (Object.keys(probe).length > 0) env.networkProbe = probe;
  }
  const tolerated = applyTolerance(records, options.mode, ENV_BOUND_AUDIT, env);
  const counted = countedFailures(tolerated, options.mode);
  const current = aggregate(tolerated);
  const deltas = computeDelta(current, baseline);
  let baselineRefused = false;
  if (options.updateBaseline && options.baseline && runnerError === null && !isolationRefused) {
    const commit = gitCommit();
    const next: Baseline = {
      schema: "mcp-audit-baseline.v1",
      recorded_commit: commit,
      mode: "authoritative",
      recorded_at: new Date().toISOString(),
      entries: current.map(({ key, verdict }) => {
        const [tool, action] = key.split(".") as [string, string];
        return { tool, action, status: verdict };
      }),
      findings: discovery.findings.map(({ code, tool, detail }) => ({ code, tool, detail })),
    };
    try {
      const decision = writeBaselineIfAllowed(options.baseline, next, {
        mode: options.mode,
        platform,
        cleanupOk: cleanup.ok,
        regressions: regressionCount(deltas),
      });
      if (!decision.allowed) {
        baselineRefused = true;
        notes.push(`baseline not written: ${decision.reason}`);
      }
    } catch (err) {
      baselineRefused = true;
      notes.push(`baseline not written: ${err instanceof Error ? err.message : String(err)}`);
    }
  }
  const code = computeExit({
    runnerError: runnerError !== null,
    isolationRefused,
    baselineRefused,
    counted: counted.length,
    findings: discovery.findings.length,
    cleanupOk: cleanup.ok,
  });
  const summary = buildSummary({
    mode: options.mode,
    agent: options.agent,
    commit: gitCommit(),
    server: options.server,
    backendVersion,
    launch,
    isolation,
    discovery,
    steps: tolerated,
    deltas,
    cleanup,
    exitCode: code,
    outDir: options.out,
  });
  writeOutputs({
    dir: options.out,
    summary,
    records: [...tolerated, ...notes.map((note) => ({ note }))],
    secrets,
    serverStderr: client.stderr(),
    reportPath,
  });
  return { summary, exitCode: code };
}

export async function main(argv: string[], deps: AuditDeps = {}): Promise<number> {
  let options: AuditOptions;
  try {
    options = parseCli(argv);
  } catch (err) {
    if (err instanceof CliError) {
      process.stderr.write(`${err.message}\n`);
      return err.exitCode;
    }
    throw err;
  }
  const { summary, exitCode } = await runAudit(options, deps);
  process.stdout.write(
    `mcp-audit ${summary.mode}: ${summary.counts.pass}/${summary.counts.total} pass, ` +
      `${summary.discovery.findings.length} discovery finding(s), cleanup ${summary.cleanup.ok ? "ok" : "FAILED"}, exit ${exitCode}\n` +
      `summary: ${path.join(summary.out_dir, "mcp-audit-summary.json")}\n`,
  );
  return exitCode;
}

/** True when this module is the CLI entry (tsx scripts/audit/run.ts); case-insensitive on Windows. */
function isMain(): boolean {
  if (!process.argv[1]) return false;
  const norm = (p: string) => (process.platform === "win32" ? path.resolve(p).toLowerCase() : path.resolve(p));
  return norm(process.argv[1]) === norm(fileURLToPath(import.meta.url));
}

if (isMain()) {
  main(process.argv.slice(2)).then(
    (code) => {
      process.exitCode = code;
    },
    (err: unknown) => {
      process.stderr.write(`mcp-audit runner error: ${err instanceof Error ? err.stack ?? err.message : String(err)}\n`);
      process.exitCode = 4;
    },
  );
}
