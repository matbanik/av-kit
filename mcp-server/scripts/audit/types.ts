/**
 * Shared types for the MEU-68 MCP live audit runner (plan 2026-10-01-mcp-live-audit).
 * VERDICT and DELTA are the closed enums of the plan's single-statement contracts.
 */

export const VERDICTS = ["pass", "fail", "skip_env", "blocked"] as const;
export type Verdict = (typeof VERDICTS)[number];

export const DELTAS = ["REGRESSION", "KNOWN", "FIXED", "NEW", "REMOVED", "UNCHANGED"] as const;
export type Delta = (typeof DELTAS)[number];

export type Mode = "container" | "authoritative";

/** The 8 COMPOUND_TOOLS, restated as a closed set for the summary schema (registry.ts:22-31). */
export const AUDIT_TOOLS = [
  "avkit_download",
  "avkit_transcript",
  "avkit_tts",
  "avkit_models",
  "avkit_settings",
  "avkit_health",
  "avkit_convert",
  "avkit_capture",
] as const;
export type AuditTool = (typeof AUDIT_TOOLS)[number];

/** One MCP tools/call result as the runner sees it. */
export type ToolCallOutcome = {
  isError: boolean;
  text: string;
  image?: { data: string; mimeType: string };
};

/** A REST or filesystem observation that decides a step (OBSERVABLE_RULE). */
export type ObservableResult = {
  ok: boolean;
  detail: string;
  /** The entity's own error_message when the observable read a terminal failed state. */
  errorMessage?: string | null;
};

export type EnvBound = { member: boolean; signature_matched: boolean; env_proof: boolean };

export type RefusalProbe = { isError: boolean; changed: boolean; text: string };

export type RefusalRecord = {
  refusal_omit: RefusalProbe;
  refusal_false: RefusalProbe;
  /** AUDIT_ELICITATION: confirm: true with the IDE prompt declined (USER_CONFIRM_ACTIONS steps only). */
  refusal_declined?: RefusalProbe;
  /** True exactly for USER_CONFIRM_ACTIONS steps; absent is judged as false. */
  user_confirm?: boolean;
  confirmed: { isError: boolean; changed: boolean };
};

/** The answer the audit client gives an elicitation/create prompt during one tools/call. */
export type ElicitPolicy = "accept" | "decline";

export type StepRecord = {
  id: string;
  tool: string;
  action: string;
  phase: "lifecycle" | "functional";
  verdict: Verdict;
  reason: string | null;
  is_error: boolean | null;
  observable: string | null;
  error: string | null;
  blocked_by: string | null;
  env_bound: EnvBound | null;
  refusal?: RefusalRecord;
  ms: number;
};

export type DiscoveryFinding = { code: string; tool: string; detail: string; issue?: string };

export type DiscoveryResult = {
  status: "pass" | "fail";
  tools: number;
  actions: number;
  findings: DiscoveryFinding[];
  new: string[];
  removed: string[];
  ghost: string[];
};

export type BaselineEntry = { tool: string; action: string; status: Verdict; issue?: string };

export type Baseline = {
  schema: "mcp-audit-baseline.v1";
  recorded_commit: string;
  mode: "authoritative";
  recorded_at: string;
  entries: BaselineEntry[];
  findings: DiscoveryFinding[];
};

export type DeltaRecord = { key: string; delta: Delta; issue?: string };

export type LaunchRecord = { command: string; args: string[]; env_keys: string[]; initialized: boolean };

export type IsolationRecord = { root: string; paths: Record<string, string>; ok: boolean; error: string | null };

export type CleanupRecord = { ok: boolean; residuals: string[]; backend_exited: boolean; root_removed: boolean };

export type Counts = { pass: number; fail: number; skip_env: number; blocked: number; total: number };

export type Summary = {
  schema: "mcp-audit-summary.v1";
  mode: Mode;
  agent: string;
  date: string;
  commit: string;
  server: string;
  backend_version: string | null;
  out_dir: string;
  launch: LaunchRecord;
  isolation: IsolationRecord;
  discovery: DiscoveryResult;
  steps: StepRecord[];
  counts: Counts;
  deltas: DeltaRecord[];
  cleanup: CleanupRecord;
  consolidation: "n/a";
  exit_code: number;
};

/** Settings schema shape served as avkit://settings/schema (settings.ts SETTINGS_SCHEMA). */
export type SettingsSchema = {
  namespaces: Record<string, Record<string, { type: string; default: string | number | boolean }>>;
};

/** Facts the environment proof of an ENV_BOUND_AUDIT member reads. */
export type EnvFacts = {
  platform: string;
  ffmpegAvailable?: boolean;
  networkProbe?: Record<string, boolean>;
};
