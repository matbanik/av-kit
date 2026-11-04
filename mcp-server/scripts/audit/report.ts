/**
 * Summary (mcp-audit-summary.v1), Markdown report and on-disk outputs for the MEU-68 runner.
 * Every string written to disk passes through redaction (AC-68.14).
 */
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { redact, redactDeep } from "./redact.js";
import { loadSchema, validate } from "./schema.js";
import type {
  CleanupRecord,
  Counts,
  DeltaRecord,
  DiscoveryResult,
  IsolationRecord,
  LaunchRecord,
  Mode,
  StepRecord,
  Summary,
} from "./types.js";
import { AUDIT_TOOLS } from "./types.js";

export type SummaryInput = {
  mode: Mode;
  agent: string;
  commit: string;
  server: string;
  backendVersion: string | null;
  launch: LaunchRecord;
  isolation: IsolationRecord;
  discovery: DiscoveryResult;
  steps: StepRecord[];
  deltas: DeltaRecord[];
  cleanup: CleanupRecord;
  exitCode: number;
  outDir?: string;
  date?: string;
};

function countsOf(steps: StepRecord[]): Counts {
  const counts: Counts = { pass: 0, fail: 0, skip_env: 0, blocked: 0, total: steps.length };
  for (const s of steps) counts[s.verdict] += 1;
  return counts;
}

export function buildSummary(input: SummaryInput): Summary {
  return {
    schema: "mcp-audit-summary.v1",
    mode: input.mode,
    agent: input.agent,
    date: input.date ?? new Date().toISOString(),
    commit: input.commit,
    server: input.server,
    backend_version: input.backendVersion,
    out_dir: input.outDir ?? "",
    launch: input.launch,
    isolation: input.isolation,
    discovery: input.discovery,
    steps: input.steps,
    counts: countsOf(input.steps),
    deltas: input.deltas,
    cleanup: input.cleanup,
    consolidation: "n/a",
    exit_code: input.exitCode,
  };
}

/** Violations of summary.schema.json; empty means valid. */
export function validateSummary(summary: unknown): string[] {
  return validate(loadSchema("summary.schema.json"), summary);
}

const cell = (v: unknown) => String(v ?? "").replace(/\|/g, "\\|").replace(/\n/g, " ");

function table(header: string[], rows: unknown[][]): string {
  const lines = [`| ${header.join(" | ")} |`, `|${header.map(() => "---").join("|")}|`];
  for (const row of rows) lines.push(`| ${row.map(cell).join(" | ")} |`);
  return lines.join("\n");
}

/** Markdown report in the Zorivest §Output Format shape, adapted to av-kit (D-10: no score). */
export function renderReport(s: Summary): string {
  const out: string[] = ["# MCP Tool Audit Report", ""];
  if (s.mode === "container") {
    out.push(
      "> **non-authoritative container subset** — run in the Linux container (cloud-local-collaboration.md §4).",
      "> Only the Windows WINDOWS_GATE run is authoritative (05-mcp-server.md §MCP live audit, Where it runs).",
      "",
    );
  }
  out.push(
    table(["Field", "Value"], [
      ["Date", s.date],
      ["Agent", s.agent],
      ["Mode", s.mode],
      ["Backend version", s.backend_version ?? "unknown"],
      ["Commit", s.commit],
      ["Server", s.server],
      ["Tools / actions", `${s.discovery.tools} / ${s.discovery.actions}`],
      ["Exit code", s.exit_code],
    ]),
    "",
    `Consolidation score: n/a (8 compound tools; consolidation already done, D-10).`,
    "",
    "## Scorecard",
    "",
  );
  const domains = AUDIT_TOOLS.filter((t) => s.steps.some((x) => x.tool === t));
  out.push(
    table(
      ["Tool", "Steps", "Pass", "Fail", "Skip (env)", "Blocked"],
      domains.map((t) => {
        const st = s.steps.filter((x) => x.tool === t);
        const n = (v: string) => st.filter((x) => x.verdict === v).length;
        return [t, st.length, n("pass"), n("fail"), n("skip_env"), n("blocked")];
      }),
    ),
    "",
    `Totals: ${s.counts.pass} pass, ${s.counts.fail} fail, ${s.counts.skip_env} skip_env, ${s.counts.blocked} blocked of ${s.counts.total}.`,
    "",
    "## Lifecycle matrix",
    "",
    table(
      ["Step", "Tool.action", "Verdict", "Observable"],
      s.steps.filter((x) => x.phase === "lifecycle").map((x) => [x.id, `${x.tool}.${x.action}`, x.verdict, x.observable ?? ""]),
    ),
    "",
    "## Functional results",
    "",
    table(
      ["Step", "Tool.action", "Status", "Error", "Notes"],
      s.steps.filter((x) => x.phase === "functional").map((x) => [x.id, `${x.tool}.${x.action}`, x.verdict, x.error ?? "", x.observable ?? ""]),
    ),
    "",
    "## Issues log",
    "",
  );
  const issues = s.steps.filter((x) => x.verdict !== "pass");
  out.push(
    issues.length === 0
      ? "None."
      : table(
          ["Severity", "Step", "Tool.action", "Verdict", "Reason", "Error"],
          issues.map((x) => [
            x.verdict === "fail" ? "high" : "info",
            x.id,
            `${x.tool}.${x.action}`,
            x.verdict,
            x.reason ?? (x.blocked_by ? `blocked by ${x.blocked_by}` : ""),
            x.error ?? "",
          ]),
        ),
    "",
    "## Discovery findings",
    "",
    s.discovery.findings.length === 0
      ? "None."
      : table(["Code", "Tool", "Detail", "Issue"], s.discovery.findings.map((f) => [f.code, f.tool, f.detail, f.issue ?? ""])),
    "",
    "## Regression delta",
    "",
  );
  const interesting = s.deltas.filter((d) => d.delta !== "UNCHANGED");
  out.push(
    interesting.length === 0
      ? "No change against the baseline."
      : table(["Tool.action", "Delta", "Issue"], interesting.map((d) => [d.key, d.delta, d.issue ?? ""])),
    "",
    "## Cleanup",
    "",
    table(["ok", "backend exited", "root removed", "residuals"], [
      [s.cleanup.ok, s.cleanup.backend_exited, s.cleanup.root_removed, s.cleanup.residuals.join("; ") || "none"],
    ]),
    "",
    "## Isolation",
    "",
    table(["Setting", "Path"], Object.entries(s.isolation.paths)),
    s.isolation.error ? `\nIsolation error: ${s.isolation.error}` : "",
    "",
  );
  return out.join("\n");
}

/** Writes actions.jsonl, mcp-audit-summary.json, server-stderr.txt and the report, all redacted. */
export function writeOutputs(input: {
  dir: string;
  summary: Summary;
  records: unknown[];
  secrets: string[];
  serverStderr: string;
  reportPath: string;
}): void {
  mkdirSync(input.dir, { recursive: true });
  const summary = redactDeep(input.summary, input.secrets);
  writeFileSync(
    path.join(input.dir, "actions.jsonl"),
    input.records.map((r) => JSON.stringify(redactDeep(r, input.secrets))).join("\n") + (input.records.length ? "\n" : ""),
    "utf8",
  );
  writeFileSync(path.join(input.dir, "mcp-audit-summary.json"), `${JSON.stringify(summary, null, 2)}\n`, "utf8");
  writeFileSync(path.join(input.dir, "server-stderr.txt"), redact(input.serverStderr, input.secrets), "utf8");
  mkdirSync(path.dirname(input.reportPath), { recursive: true });
  writeFileSync(input.reportPath, redact(renderReport(summary), input.secrets), "utf8");
}
