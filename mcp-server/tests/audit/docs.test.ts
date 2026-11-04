import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { CLI_FLAGS } from "../../scripts/audit/run.js";

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const WORKFLOW = path.join(REPO, ".agent/workflows/mcp-audit.md");
const SKILL = path.join(REPO, ".agent/skills/mcp-tool-audit/SKILL.md");
const PKG = JSON.parse(readFileSync(path.join(REPO, "mcp-server/package.json"), "utf8")) as { scripts: Record<string, string> };

/** `npm run <name>` / `npm --prefix mcp-server run <name>` citations. */
function citedScripts(md: string): string[] {
  return [...md.matchAll(/npm (?:--prefix \S+ )?run ([a-z][\w:-]*)/g)].map((m) => m[1]);
}

/** `--flag` citations that follow an `audit` invocation on the same line. */
function citedFlags(md: string): string[] {
  const flags: string[] = [];
  for (const line of md.split("\n")) {
    if (!/run audit/.test(line)) continue;
    for (const m of line.matchAll(/\s(--[a-z][a-z-]*)/g)) flags.push(m[1]);
  }
  return flags;
}

function unknownCitations(md: string): string[] {
  const scripts = citedScripts(md).filter((s) => !(s in PKG.scripts)).map((s) => `npm run ${s}`);
  const flags = citedFlags(md).filter((f) => f !== "--prefix" && !CLI_FLAGS.includes(f));
  return [...scripts, ...flags];
}

function read(file: string): string {
  return readFileSync(file, "utf8");
}

describe("AC-68.16 workflow and skill documents", () => {
  it("AC-68.16 both documents exist", () => {
    expect(existsSync(WORKFLOW), WORKFLOW).toBe(true);
    expect(existsSync(SKILL), SKILL).toBe(true);
  });

  it("AC-68.16 both carry frontmatter with a description", () => {
    for (const file of [WORKFLOW, SKILL].filter(existsSync)) {
      // CRLF-tolerant: the Windows checkout normalizes .md to CRLF (.gitattributes text=auto).
      expect(read(file)).toMatch(/^---\r?\n[\s\S]*?description:[\s\S]*?\r?\n---\r?\n/);
    }
    expect(existsSync(WORKFLOW) && existsSync(SKILL)).toBe(true);
  });

  it("AC-68.16 the skill documents triggers, both modes, isolation, cleanup, baseline policy, findings and the IDE spot-check", () => {
    expect(existsSync(SKILL)).toBe(true);
    const md = existsSync(SKILL) ? read(SKILL) : "";
    for (const needle of [
      "## When to Invoke",
      "container",
      "authoritative",
      "ISOLATION_GUARD",
      "CLEANUP_PREDICATE",
      "BASELINE_UPDATE_RULE",
      "issue_triage.py add",
      "IDE spot-check",
      "_zorivest_mcp_tool_audit_skill.md",
    ]) {
      expect(md, needle).toContain(needle);
    }
  });

  it("AC-68.16 the workflow cites the audit script and the skill", () => {
    expect(existsSync(WORKFLOW)).toBe(true);
    const md = existsSync(WORKFLOW) ? read(WORKFLOW) : "";
    expect(citedScripts(md)).toContain("audit");
    expect(md).toContain(".agent/skills/mcp-tool-audit/SKILL.md");
  });

  it("AC-68.16 every npm script and audit flag the documents cite exists", () => {
    expect(existsSync(WORKFLOW) && existsSync(SKILL)).toBe(true);
    for (const file of [WORKFLOW, SKILL].filter(existsSync)) {
      expect(unknownCitations(read(file)), file).toEqual([]);
    }
  });

  it("AC-68.16 a citation of a missing script or flag is caught", () => {
    expect(unknownCitations("npm --prefix mcp-server run audit-x\nnpm --prefix mcp-server run audit -- --mode container --frob")).toEqual([
      "npm run audit-x",
      "--frob",
    ]);
  });

  it("AC-68.16 both documents are indexed", () => {
    expect(read(path.join(REPO, ".agent/workflows/README.md"))).toContain("mcp-audit.md");
    expect(read(path.join(REPO, ".agent/skills/README.md"))).toContain("mcp-tool-audit");
  });
});
