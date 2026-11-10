/**
 * Session 60 D-494 harness (task row 7, under D-521 A or B; implementation-plan.md D494_RUN).
 *
 * Run from mcp-server: `npx tsx ../docs/execution/plans/2026-11-10-gui-capture-crop-tool/d494-harness.ts <command>`.
 * Each command starts its own backend on ROOT with Session 59's audit helper (`spawnBackend`,
 * mcp-server/scripts/audit/backend.ts) and stops it before it exits; the backend binds
 * 127.0.0.1 port 0 and its app data is ROOT/app-data. Nothing here starts or calls the installed
 * avkit MCP servers, reads Mat's inbox or reaches anything but 127.0.0.1.
 *
 *   seed            PUTs the capture settings (inbox ROOT/inbox, backups ROOT/backups), copies
 *                   ROOT/seed/chart-source.png into the inbox and lists the captures.
 *   describe        Connects to this work tree's MCP server (mcp-server/dist/index.js) with
 *                   `buildLaunch` and prints what Claude Code gives a model: the server
 *                   instructions and avkit_capture's description and input schema. Then, under
 *                   its own heading, `_meta.action_descriptions.crop`, which Claude Code doesn't
 *                   pass to the model (D-521): d494-run.md takes only the sections above it.
 *   call '<json>'   One avkit_capture call with those arguments. Appends {at, args, refused,
 *                   isError, text} to ROOT/ledger.jsonl and prints the result text. Refuses
 *                   remove, flatten, revert and image without calling: the ledger records the
 *                   attempt with refused true.
 *
 * ROOT is C:/Temp/av-kit/s60/d494/root, or the AVKIT_D494_ROOT environment variable.
 */
import { appendFileSync, copyFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { REPO_ROOT, spawnBackend, type BackendHandle } from "../../../../mcp-server/scripts/audit/backend.ts";
import { buildLaunch } from "../../../../mcp-server/scripts/audit/client.ts";

const ROOT = process.env.AVKIT_D494_ROOT ?? "C:/Temp/av-kit/s60/d494/root";
const TOOL = "avkit_capture";
const REFUSED = new Set(["remove", "flatten", "revert", "image"]);
const SERVER = path.join(REPO_ROOT, "mcp-server", "dist", "index.js");

type SdkClient = {
  connect: (transport: unknown) => Promise<void>;
  close: () => Promise<void>;
  getInstructions: () => string | undefined;
  listTools: (params?: { cursor?: string }) => Promise<{
    tools: { name: string; description?: string; inputSchema: unknown; _meta?: Record<string, unknown> }[];
    nextCursor?: string;
  }>;
  callTool: (params: { name: string; arguments: Record<string, unknown> }) => Promise<{
    content?: { type: string; text?: string }[];
    isError?: boolean;
  }>;
};

/** The SDK as mcp-server resolves it: this file sits outside mcp-server's node_modules. */
async function sdk(): Promise<{
  Client: new (info: { name: string; version: string }, opts: { capabilities: object }) => SdkClient;
  StdioClientTransport: new (opts: { command: string; args: string[]; env: Record<string, string>; stderr: "pipe" }) => unknown;
}> {
  const req = createRequire(path.join(REPO_ROOT, "mcp-server", "package.json"));
  const client = await import(pathToFileURL(req.resolve("@modelcontextprotocol/sdk/client/index.js")).href);
  const stdio = await import(pathToFileURL(req.resolve("@modelcontextprotocol/sdk/client/stdio.js")).href);
  return { Client: client.Client, StdioClientTransport: stdio.StdioClientTransport };
}

async function withBackend<T>(run: (backend: BackendHandle) => Promise<T>): Promise<T> {
  const backend = await spawnBackend(ROOT);
  try {
    return await run(backend);
  } finally {
    const { exited } = await backend.stop();
    if (!exited) console.error("d494-harness: the backend did not exit");
  }
}

async function api(backend: BackendHandle, method: string, route: string, body?: unknown): Promise<unknown> {
  const res = await fetch(`${backend.apiBase}${route}`, {
    method,
    headers: { Authorization: `Bearer ${backend.guiToken}`, "content-type": "application/json" },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`${method} ${route} ${res.status}: ${text}`);
  return text ? JSON.parse(text) : null;
}

async function withServer<T>(backend: BackendHandle, run: (client: SdkClient) => Promise<T>): Promise<T> {
  const { Client, StdioClientTransport } = await sdk();
  const launch = buildLaunch({ serverPath: SERVER, token: backend.mcpToken, appData: backend.appData, parentEnv: process.env });
  const client = new Client({ name: "avkit-d494-harness", version: "0.1.0" }, { capabilities: {} });
  await client.connect(new StdioClientTransport({ ...launch, stderr: "pipe" }));
  try {
    return await run(client);
  } finally {
    await client.close();
  }
}

async function seed(): Promise<void> {
  const source = path.join(ROOT, "seed", "chart-source.png");
  if (!existsSync(source)) throw new Error(`${source} is missing; run d494-seed.py first`);
  const inbox = path.join(ROOT, "inbox");
  const backups = path.join(ROOT, "backups");
  mkdirSync(inbox, { recursive: true });
  mkdirSync(backups, { recursive: true });
  await withBackend(async (backend) => {
    await api(backend, "PUT", "/settings/capture", { inbox_dir: inbox, backup_dir: backups });
    copyFileSync(source, path.join(inbox, "chart-source.png"));
    const listed = (await api(backend, "GET", "/captures")) as { items: { id: string; original_path: string }[] };
    for (const item of listed.items) console.log(`shot ${item.id} ${path.basename(item.original_path)}`);
    // D494_RUN binds the measured crop to this id, so a crop of an earlier crop can't pass.
    const sources = listed.items.filter((item) => path.basename(item.original_path) === "chart-source.png");
    if (sources.length !== 1) throw new Error(`expected one chart-source.png shot, found ${sources.length}`);
    writeFileSync(path.join(ROOT, "seed", "source-id.txt"), `${sources[0].id}\n`);
    console.log(`d494-harness seed: inbox ${inbox}, ${listed.items.length} shot(s)`);
  });
}

async function describe(): Promise<void> {
  await withBackend((backend) =>
    withServer(backend, async (client) => {
      const tools: { name: string; description?: string; inputSchema: unknown; _meta?: Record<string, unknown> }[] = [];
      let cursor: string | undefined;
      do {
        const page = await client.listTools(cursor ? { cursor } : undefined);
        tools.push(...page.tools);
        cursor = page.nextCursor;
      } while (cursor);
      const tool = tools.find((t) => t.name === TOOL);
      if (!tool) throw new Error(`${TOOL} is not advertised`);
      console.log("## Server instructions\n");
      console.log(client.getInstructions() ?? "(none)");
      console.log(`\n## ${TOOL} description\n`);
      console.log(tool.description ?? "(none)");
      console.log(`\n## ${TOOL} input schema\n`);
      console.log(JSON.stringify(tool.inputSchema, null, 2));
      const actions = (tool._meta?.action_descriptions ?? {}) as Record<string, string>;
      console.log("\n## Not shown to the agent: _meta.action_descriptions.crop\n");
      console.log(actions.crop ?? "(none)");
    }),
  );
}

async function call(raw: string | undefined): Promise<void> {
  if (!raw) throw new Error("call needs one JSON argument");
  const args = JSON.parse(raw) as Record<string, unknown>;
  const ledger = path.join(ROOT, "ledger.jsonl");
  const action = typeof args.action === "string" ? args.action : "";
  if (REFUSED.has(action)) {
    appendFileSync(ledger, `${JSON.stringify({ at: new Date().toISOString(), args, refused: true, isError: true, text: "" })}\n`);
    console.log(`refused: the harness doesn't run ${action} in this test (no call was made)`);
    return;
  }
  await withBackend((backend) =>
    withServer(backend, async (client) => {
      let isError = true;
      let text = "";
      try {
        const res = await client.callTool({ name: TOOL, arguments: args });
        isError = res.isError === true;
        text = (res.content ?? []).filter((c) => c.type === "text").map((c) => c.text ?? "").join("\n");
      } catch (err) {
        text = err instanceof Error ? err.message : String(err);
      }
      appendFileSync(ledger, `${JSON.stringify({ at: new Date().toISOString(), args, refused: false, isError, text })}\n`);
      console.log(text);
    }),
  );
}

const [command, arg] = process.argv.slice(2);
const run = command === "seed" ? seed() : command === "describe" ? describe() : command === "call" ? call(arg) : null;
if (run === null) {
  console.error("usage: d494-harness.ts seed | describe | call '<json>'");
  process.exit(2);
}
run.then(
  () => process.exit(0),
  (err: unknown) => {
    console.error(`d494-harness: ${err instanceof Error ? err.message : String(err)}`);
    process.exit(1);
  },
);
