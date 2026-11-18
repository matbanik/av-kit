// Session 92 (mcp-audit-refresh) plan-local check of the registered tool descriptions (DESC_PIN).
//
// Reads the built server (mcp-server/dist/index.js; createServer reads no token and starts
// nothing) and collects, for each of the eight compound tools, its top-level description,
// its _meta.action_descriptions and its advertised input schema (field descriptions included).
//
//   --record <json>                 row 0: write what the built server registers now.
//   --baseline <json> --expected <txt>
//                                   rows 4 and the gate: avkit_capture's description equals
//                                   the expected file's text exactly and is under the limit;
//                                   the other seven descriptions, every _meta map and every
//                                   advertised input schema equal the row-0 record.
//   --selftest                      runs compare() on fixtures; touches no file but a temp one.
//
// Exit 0 when every check passes, 1 when one fails, 2 on a usage error.
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SERVER = path.resolve(HERE, "../../../../mcp-server/dist/index.js");
const CAPTURE = "avkit_capture";
const LIMIT = 4096;
const TOOLS = [
  "avkit_download",
  "avkit_transcript",
  "avkit_tts",
  "avkit_models",
  "avkit_settings",
  "avkit_health",
  "avkit_convert",
  "avkit_capture",
];

/**
 * What the built server advertises, as plain JSON: the tools/list result a client sees
 * (description, the advertised JSON input schema with its field descriptions, and _meta).
 * createServer() connects no transport, reads no token and starts no backend.
 */
export async function collect(serverPath = SERVER) {
  const mod = await import(pathToFileURL(serverPath).href);
  const server = mod.createServer();
  const handler = server.server?._requestHandlers?.get("tools/list");
  if (typeof handler !== "function") throw new Error("tools/list handler not found on the built server");
  const listed = await handler({ method: "tools/list", params: {} }, {});
  const byName = new Map((listed?.tools ?? []).map((tool) => [tool.name, tool]));
  const out = {};
  for (const name of TOOLS) {
    const tool = byName.get(name);
    out[name] = tool
      ? {
          description: tool.description ?? null,
          meta: tool._meta?.action_descriptions ?? null,
          schema: tool.inputSchema ?? null,
        }
      : null;
  }
  return out;
}

function same(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

/** Problems in `now` against the row-0 record `base` and the expected capture text. */
export function compare(base, now, expected) {
  const problems = [];
  for (const name of TOOLS) {
    const b = base[name];
    const n = now[name];
    if (!b || !n) {
      problems.push(`${name}: not registered (${b ? "now" : "at row 0"})`);
      continue;
    }
    if (name === CAPTURE) {
      if (n.description !== expected) problems.push(`${name}: description differs from the expected file`);
      if (typeof n.description !== "string" || n.description.length >= LIMIT) {
        problems.push(`${name}: description length ${n.description?.length} is not under ${LIMIT}`);
      }
      if (n.description === b.description) problems.push(`${name}: description is still the row-0 text`);
    } else if (n.description !== b.description) {
      problems.push(`${name}: description changed`);
    }
    if (!same(n.meta, b.meta)) problems.push(`${name}: _meta.action_descriptions changed`);
    if (!same(n.schema, b.schema)) problems.push(`${name}: the advertised input schema changed`);
  }
  return problems;
}

function selftest() {
  const base = {};
  for (const name of TOOLS) base[name] = { description: `old ${name}`, meta: { a: `m ${name}` }, schema: { a: `z ${name}` } };
  const expected = "Call image to view a frame or sheet.";
  const good = structuredClone(base);
  good[CAPTURE].description = expected;
  const cases = [
    ["positive control", good, 0],
    ["capture text still the old one", base, 2],
    ["capture text differs from expected", (() => { const x = structuredClone(good); x[CAPTURE].description = "other"; return x; })(), 1],
    ["capture text at the limit", (() => { const x = structuredClone(good); x[CAPTURE].description = "x".repeat(LIMIT); return x; })(), 2],
    ["another tool's description changed", (() => { const x = structuredClone(good); x.avkit_tts.description = "new"; return x; })(), 1],
    ["a _meta map changed", (() => { const x = structuredClone(good); x[CAPTURE].meta = { a: "changed" }; return x; })(), 1],
    ["an input schema changed", (() => { const x = structuredClone(good); x.avkit_convert.schema = { a: "changed" }; return x; })(), 1],
    ["a tool missing", (() => { const x = structuredClone(good); x.avkit_health = null; return x; })(), 1],
  ];
  let failed = 0;
  for (const [label, now, want] of cases) {
    const got = compare(base, now, expected).length;
    const ok = got === want;
    if (!ok) failed += 1;
    console.log(`${ok ? "PASS" : "FAIL"} selftest ${label}: ${got} problem(s), want ${want}`);
  }
  const dir = mkdtempSync(path.join(os.tmpdir(), "mar-desc-selftest-"));
  try {
    const file = path.join(dir, "expected.txt");
    writeFileSync(file, Buffer.from(expected, "utf8"));
    const back = readFileSync(file, "utf8");
    const ok = back === expected;
    if (!ok) failed += 1;
    console.log(`${ok ? "PASS" : "FAIL"} selftest expected file round trip`);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
  console.log(failed === 0 ? "desc-check selftest: ok" : `desc-check selftest: ${failed} failed`);
  return failed === 0 ? 0 : 1;
}

function arg(argv, name) {
  const i = argv.indexOf(name);
  return i >= 0 && i + 1 < argv.length ? argv[i + 1] : null;
}

async function main(argv) {
  if (argv.includes("--selftest")) return selftest();
  const record = arg(argv, "--record");
  if (record) {
    const now = await collect();
    writeFileSync(record, Buffer.from(`${JSON.stringify(now, null, 2)}\n`, "utf8"));
    const cap = now[CAPTURE]?.description ?? "";
    console.log(`recorded ${Object.keys(now).length} tools to ${path.basename(record)}; ${CAPTURE} description ${cap.length} chars`);
    return 0;
  }
  const baseline = arg(argv, "--baseline");
  const expectedPath = arg(argv, "--expected");
  if (!baseline || !expectedPath) {
    console.error("usage: desc-check.mjs --record <json> | --baseline <json> --expected <txt> | --selftest");
    return 2;
  }
  const base = JSON.parse(readFileSync(baseline, "utf8"));
  const expected = readFileSync(expectedPath, "utf8");
  if (expected.includes("\r")) {
    console.log("FAIL the expected file holds a CR");
    return 1;
  }
  const now = await collect();
  const problems = compare(base, now, expected);
  const cap = now[CAPTURE]?.description ?? "";
  console.log(`${CAPTURE} description: ${cap.length} chars (limit ${LIMIT}), equals expected: ${cap === expected}`);
  for (const p of problems) console.log(`FAIL ${p}`);
  console.log(problems.length === 0 ? "desc-check: ok" : `desc-check: ${problems.length} problem(s)`);
  return problems.length === 0 ? 0 : 1;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = await main(process.argv.slice(2));
}
