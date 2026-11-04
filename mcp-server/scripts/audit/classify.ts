/**
 * Pure classification for the MEU-68 audit runner: step verdicts (OBSERVABLE_RULE), the
 * REFUSAL_ORACLE, discovery findings, DELTA, ENV_BOUND_AUDIT tolerance, exit codes, coverage,
 * the baseline schema and BASELINE_UPDATE_RULE, and ISOLATION_GUARD.
 * Names refer to docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md.
 */
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { loadSchema, validate } from "./schema.js";
import type {
  Baseline,
  DeltaRecord,
  DiscoveryFinding,
  DiscoveryResult,
  EnvFacts,
  Mode,
  ObservableResult,
  RefusalRecord,
  SettingsSchema,
  StepRecord,
  Verdict,
} from "./types.js";

/** An ENV_BOUND_AUDIT member: tolerated in container mode only with signature AND proof. */
export type CensusMember = { key: string; signature: RegExp; envProof: (env: EnvFacts) => boolean };

export class BaselineError extends Error {}
export class IsolationError extends Error {}

/** Settings path keys that are inputs (read, never written by the audit). */
export const ISOLATION_INPUT_KEYS: readonly string[] = ["downloader.ffmpeg_path", "downloader.cookie_file_path"];

type VerdictOut = { verdict: Verdict; reason: string | null };

/** OBSERVABLE_RULE: the MCP envelope alone never passes a step. */
export function stepVerdict(o: { expectError: boolean; isError: boolean; observable: ObservableResult | null }): VerdictOut {
  if (o.isError && !o.expectError) return { verdict: "fail", reason: "unexpected_error" };
  if (!o.isError && o.expectError) return { verdict: "fail", reason: "expected_error_missing" };
  if (o.observable === null) return { verdict: "fail", reason: "no_observable" };
  if (!o.observable.ok) return { verdict: "fail", reason: o.isError ? "observable_failed" : "hollow" };
  return { verdict: "pass", reason: null };
}

/** REFUSAL_ORACLE: both refusals error without changing state; the confirmed call changes it. */
export function refusalVerdict(r: RefusalRecord): VerdictOut {
  if (!r.refusal_omit.isError || !r.refusal_false.isError) return { verdict: "fail", reason: "refusal_missing" };
  if (r.refusal_omit.changed || r.refusal_false.changed) return { verdict: "fail", reason: "refusal_mutated" };
  // AUDIT_ELICITATION: a USER_CONFIRM step must also be refused when the user declines the prompt.
  if (r.user_confirm === true) {
    if (!r.refusal_declined || !r.refusal_declined.isError) return { verdict: "fail", reason: "declined_refusal_missing" };
    if (r.refusal_declined.changed) return { verdict: "fail", reason: "declined_refusal_mutated" };
  }
  if (r.confirmed.isError) return { verdict: "fail", reason: "confirmed_error" };
  if (!r.confirmed.changed) return { verdict: "fail", reason: "confirmed_no_effect" };
  return { verdict: "pass", reason: null };
}

const key = (tool: string, action: string) => `${tool}.${action}`;
const sameSet = (a: string[], b: string[]) => a.length === b.length && [...a].sort().join("\n") === [...b].sort().join("\n");

/**
 * Phase 1 classification. The served action set is `_meta.action_descriptions` (amendment A2);
 * an inputSchema that does not advertise those actions is a finding (AC-68.3).
 */
export function classifyDiscovery(input: {
  tools: { name: string; schemaActions: string[] | null; metaActions: string[] }[];
  expectedTools: readonly string[];
  baseline: Baseline | null;
  ghosts: string[];
}): DiscoveryResult {
  const findings: DiscoveryFinding[] = [];
  const servedNames = input.tools.map((t) => t.name);
  for (const name of input.expectedTools) {
    if (!servedNames.includes(name)) findings.push({ code: "missing_tool", tool: name, detail: "not served by tools/list" });
  }
  for (const name of servedNames) {
    if (!input.expectedTools.includes(name)) {
      findings.push({ code: "unexpected_tool", tool: name, detail: "served but not one of COMPOUND_TOOLS" });
    }
  }
  const served: string[] = [];
  for (const tool of input.tools) {
    served.push(...tool.metaActions.map((a) => key(tool.name, a)));
    if (tool.schemaActions === null || tool.schemaActions.length === 0) {
      findings.push({
        code: "schema_not_advertised",
        tool: tool.name,
        detail: `tools/list inputSchema exposes no action values; _meta lists ${tool.metaActions.length} actions`,
      });
    } else if (!sameSet(tool.schemaActions, tool.metaActions)) {
      findings.push({
        code: "schema_meta_disagree",
        tool: tool.name,
        detail: `inputSchema actions [${[...tool.schemaActions].sort().join(",")}] != _meta [${[...tool.metaActions].sort().join(",")}]`,
      });
    }
  }
  const baselineKeys = input.baseline ? input.baseline.entries.map((e) => key(e.tool, e.action)) : [];
  const added = input.baseline ? served.filter((k) => !baselineKeys.includes(k)) : [];
  const removed = baselineKeys.filter((k) => !served.includes(k));
  for (const k of removed) findings.push({ code: "removed_action", tool: k.split(".")[0], detail: `${k} in baseline, not served` });
  const ghost = input.ghosts.filter((k) => served.includes(k));
  for (const k of ghost) findings.push({ code: "ghost_action", tool: k.split(".")[0], detail: `${k} listed but not callable` });
  return {
    status: findings.length === 0 ? "pass" : "fail",
    tools: input.tools.length,
    actions: served.length,
    findings,
    new: added,
    removed,
    ghost,
  };
}

/** DELTA per plan rule; baseline-only keys are REMOVED. */
export function computeDelta(current: { key: string; verdict: Verdict }[], baseline: Baseline | null): DeltaRecord[] {
  const prior = new Map((baseline?.entries ?? []).map((e) => [key(e.tool, e.action), e]));
  const out: DeltaRecord[] = current.map(({ key: k, verdict }) => {
    const before = baseline ? prior.get(k) : undefined;
    if (!before) return { key: k, delta: "NEW" };
    const wasPass = before.status === "pass";
    const isPass = verdict === "pass";
    if (wasPass && isPass) return { key: k, delta: "UNCHANGED" };
    if (wasPass && !isPass) return { key: k, delta: "REGRESSION" };
    if (!wasPass && isPass) return { key: k, delta: "FIXED" };
    return before.issue ? { key: k, delta: "KNOWN", issue: before.issue } : { key: k, delta: "KNOWN" };
  });
  const seen = new Set(current.map((c) => c.key));
  for (const k of prior.keys()) if (!seen.has(k)) out.push({ key: k, delta: "REMOVED" });
  return out;
}

/** Counts REGRESSION and REMOVED deltas (both block a baseline update). */
export function regressionCount(deltas: DeltaRecord[]): number {
  return deltas.filter((d) => {
    switch (d.delta) {
      case "REGRESSION":
      case "REMOVED":
        return true;
      case "KNOWN":
      case "FIXED":
      case "NEW":
      case "UNCHANGED":
        return false;
      default: {
        const unreachable: never = d.delta;
        throw new Error(`unhandled delta ${String(unreachable)}`);
      }
    }
  }).length;
}

/** Parses and validates a baseline; never returns an empty baseline for malformed input. */
export function parseBaseline(raw: unknown): Baseline {
  const errors = validate(loadSchema("baseline.schema.json"), raw);
  if (errors.length > 0) throw new BaselineError(`invalid baseline: ${errors.join("; ")}`);
  const baseline = raw as Baseline;
  const seen = new Set<string>();
  for (const e of baseline.entries) {
    const k = key(e.tool, e.action);
    if (seen.has(k)) throw new BaselineError(`invalid baseline: duplicate entry ${k}`);
    seen.add(k);
  }
  return baseline;
}

/** BASELINE_UPDATE_RULE. */
export function baselineUpdateDecision(input: {
  mode: Mode;
  platform: string;
  cleanupOk: boolean;
  regressions: number;
}): { allowed: boolean; reason: string } {
  if (input.mode !== "authoritative") return { allowed: false, reason: "only an authoritative run may update the baseline" };
  if (input.platform !== "win32") return { allowed: false, reason: `authoritative baseline requires win32, not ${input.platform}` };
  if (!input.cleanupOk) return { allowed: false, reason: "cleanup did not complete" };
  if (input.regressions > 0) return { allowed: false, reason: `${input.regressions} regression(s) present` };
  return { allowed: true, reason: "authoritative, win32, clean, no regression" };
}

/** Writes `next` to `file` only when the rule allows it; a refusal leaves the file untouched. */
export function writeBaselineIfAllowed(
  file: string,
  next: Baseline,
  input: { mode: Mode; platform: string; cleanupOk: boolean; regressions: number },
): { allowed: boolean; reason: string } {
  const decision = baselineUpdateDecision(input);
  if (!decision.allowed) return decision;
  parseBaseline(next);
  mkdirSync(path.dirname(file), { recursive: true });
  writeFileSync(file, `${JSON.stringify(next, null, 2)}\n`, "utf8");
  return decision;
}

/**
 * Container mode turns a `fail` into `skip_env` only for an ENV_BOUND_AUDIT member whose
 * signature matches its error AND whose environment proof holds. Everything else is unchanged
 * (fail closed). Authoritative mode tolerates nothing.
 */
export function applyTolerance(records: StepRecord[], mode: Mode, census: CensusMember[], env: EnvFacts): StepRecord[] {
  return records.map((r) => {
    if (r.verdict !== "fail") return r;
    const member = census.find((m) => m.key === key(r.tool, r.action));
    if (!member) return r;
    const signature_matched = member.signature.test(r.error ?? "");
    const env_proof = member.envProof(env);
    const env_bound = { member: true, signature_matched, env_proof };
    if (mode === "container" && signature_matched && env_proof) return { ...r, verdict: "skip_env", env_bound };
    return { ...r, env_bound };
  });
}

/** Non-pass records that count: in container mode `blocked` counts unless its root is skip_env. */
export function countedFailures(records: StepRecord[], mode: Mode): StepRecord[] {
  const byId = new Map(records.map((r) => [r.id, r]));
  const rootTolerated = (r: StepRecord): boolean => {
    let cur: StepRecord | undefined = r;
    const visited = new Set<string>();
    while (cur && cur.verdict === "blocked" && cur.blocked_by && !visited.has(cur.id)) {
      visited.add(cur.id);
      cur = byId.get(cur.blocked_by);
    }
    return cur?.verdict === "skip_env";
  };
  return records.filter((r) => {
    switch (r.verdict) {
      case "pass":
        return false;
      case "fail":
        return true;
      case "skip_env":
        return mode === "authoritative";
      case "blocked":
        return mode === "authoritative" || !rootTolerated(r);
      default: {
        const unreachable: never = r.verdict;
        throw new Error(`unhandled verdict ${String(unreachable)}`);
      }
    }
  });
}

/** 4 runner error > 3 isolation refused > 2 baseline refused > 1 failures/findings/cleanup > 0. */
export function exitCode(input: {
  runnerError: boolean;
  isolationRefused: boolean;
  baselineRefused: boolean;
  counted: number;
  findings: number;
  cleanupOk: boolean;
}): number {
  if (input.runnerError) return 4;
  if (input.isolationRefused) return 3;
  if (input.baselineRefused) return 2;
  if (input.counted > 0 || input.findings > 0 || !input.cleanupOk) return 1;
  return 0;
}

/** Members of `actionSet` that no plan step covers, in actionSet order. */
export function coverage(planKeys: string[], actionSet: string[]): string[] {
  const covered = new Set(planKeys);
  return actionSet.filter((k) => !covered.has(k));
}

/** Baseline entries compared with AUDIT_ACTION_SET. */
export function baselineCoverage(
  entries: { tool: string; action: string }[],
  actionSet: string[],
): { missing: string[]; extra: string[] } {
  const keys = entries.map((e) => key(e.tool, e.action));
  return { missing: actionSet.filter((k) => !keys.includes(k)), extra: keys.filter((k) => !actionSet.includes(k)) };
}

const PATH_LIKE = /^(path|.+_path|.+_dir|.+_directory)$/;

/** ISOLATION_KEYS: path-like string settings minus ISOLATION_INPUT_KEYS, derived from the schema. */
export function isolationKeys(schema: SettingsSchema): string[] {
  const out: string[] = [];
  for (const [ns, leaves] of Object.entries(schema.namespaces)) {
    for (const [leaf, spec] of Object.entries(leaves)) {
      const k = `${ns}.${leaf}`;
      if (spec.type === "string" && PATH_LIKE.test(leaf) && !ISOLATION_INPUT_KEYS.includes(k)) out.push(k);
    }
  }
  return out;
}

function within(child: string, root: string): boolean {
  const rel = path.relative(path.resolve(root), path.resolve(child));
  return rel !== "" && !rel.startsWith("..") && !path.isAbsolute(rel);
}

/**
 * ISOLATION_GUARD over a REST read-back: every ISOLATION_KEYS member must be mapped and resolve
 * strictly inside `root`. Throws IsolationError naming the first offending key.
 */
export function isolationGuard(input: {
  schema: SettingsSchema;
  mapping: Record<string, string>;
  readBack: Record<string, Record<string, unknown>>;
  root: string;
}): { ok: true; paths: Record<string, string> } {
  const paths: Record<string, string> = {};
  for (const k of isolationKeys(input.schema)) {
    if (!(k in input.mapping)) throw new IsolationError(`${k} is a path-like setting with no isolation mapping`);
    const [ns, leaf] = k.split(".") as [string, string];
    const value = input.readBack[ns]?.[leaf];
    if (typeof value !== "string" || value === "") throw new IsolationError(`${k} read back as ${JSON.stringify(value)}`);
    if (value.startsWith("~") || !within(value, input.root)) {
      throw new IsolationError(`${k}=${value} is outside the isolated root ${input.root}`);
    }
    paths[k] = value;
  }
  return { ok: true, paths };
}
