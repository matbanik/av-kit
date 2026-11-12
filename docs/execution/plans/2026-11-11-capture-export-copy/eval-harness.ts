/**
 * Session 64 description eval harness (task rows E-1 to E-4, under D-608 A or B; implementation-plan.md EVAL_RUN).
 *
 * Run from mcp-server: `npx tsx ../docs/execution/plans/2026-11-11-capture-export-copy/eval-harness.ts <root> <command>`.
 * ROOT must sit under C:/Temp/av-kit/s64/eval/. Each command starts its own backend on ROOT with
 * Session 59's audit helper (`spawnBackend`, mcp-server/scripts/audit/backend.ts) and stops it
 * before it exits; the backend binds 127.0.0.1 port 0 and its app data is ROOT/app-data. Nothing
 * here starts or calls the installed avkit MCP servers, reads Mat's inbox or reaches anything but
 * 127.0.0.1.
 *
 *   seed [png]          PUTs the capture settings (inbox ROOT/inbox, backups ROOT/backups). With
 *                       a PNG path, copies it into the inbox, lists the captures and writes that
 *                       shot's id to ROOT/seed/source-id.txt.
 *   describe            Connects to this work tree's MCP server (mcp-server/dist/index.js) with
 *                       `buildLaunch` and prints what Claude Code gives a model for avkit_capture
 *                       and avkit_convert: the server instructions and each tool's description
 *                       and input schema. Then, after the line CUT, each tool's
 *                       `_meta.action_descriptions`, which Claude Code doesn't pass to the model
 *                       (D-521, MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL). eval-run.md takes the
 *                       text above CUT for the `real` surface and all of it for `meta`.
 *   call <tool> '<json>' One call with those arguments. Appends {at, tool, args, refused, isError,
 *                       text, images} to ROOT/ledger.jsonl and prints the result text. Image
 *                       content is saved to ROOT/views/NNN.png and its path printed. Only ALLOWED
 *                       actions go through; any other is recorded with refused true, not called.
 */
import { appendFileSync, copyFileSync, existsSync, mkdirSync, readdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { REPO_ROOT, spawnBackend, type BackendHandle } from "../../../../mcp-server/scripts/audit/backend.ts";
import { buildLaunch } from "../../../../mcp-server/scripts/audit/client.ts";

const EVAL_BASE = "C:/Temp/av-kit/s64/eval/";
const CUT = "<!-- CUT: the real surface ends above this line -->";
const TOOLS = ["avkit_capture", "avkit_convert"];
const ALLOWED: Record<string, Set<string>> = {
  avkit_capture: new Set(["list", "get", "image", "frames", "sheet", "export", "crop"]),
  avkit_convert: new Set(["probe"]),
};
const CALL_TIMEOUT_MS = 600_000;
const SERVER = path.join(REPO_ROOT, "mcp-server", "dist", "index.js");

type Content = { type: string; text?: string; data?: string; mimeType?: string };
type ToolInfo = { name: string; description?: string; inputSchema: unknown; _meta?: Record<string, unknown> };
type SdkClient = {
  connect: (transport: unknown) => Promise<void>;
  close: () => Promise<void>;
  getInstructions: () => string | undefined;
  listTools: (params?: { cursor?: string }) => Promise<{ tools: ToolInfo[]; nextCursor?: string }>;
  callTool: (
    params: { name: string; arguments: Record<string, unknown> },
    resultSchema?: unknown,
    options?: { timeout?: number },
  ) => Promise<{ content?: Content[]; isError?: boolean }>;
};

/** The root argument, refused unless it sits under EVAL_BASE. */
function evalRoot(raw: string | undefined): string {
  if (!raw) throw new Error("the first argument is the eval root");
  const root = path.resolve(raw).replaceAll("\\", "/");
  if (!root.toLowerCase().startsWith(EVAL_BASE.toLowerCase()) || root.length <= EVAL_BASE.length) {
    throw new Error(`the eval root must sit under ${EVAL_BASE}`);
  }
  return root;
}

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

async function withBackend<T>(root: string, run: (backend: BackendHandle) => Promise<T>): Promise<T> {
  const backend = await spawnBackend(root);
  try {
    return await run(backend);
  } finally {
    const { exited } = await backend.stop();
    if (!exited) console.error("eval-harness: the backend did not exit");
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
  const client = new Client({ name: "avkit-s64-eval-harness", version: "0.1.0" }, { capabilities: {} });
  await client.connect(new StdioClientTransport({ ...launch, stderr: "pipe" }));
  try {
    return await run(client);
  } finally {
    await client.close();
  }
}

async function seed(root: string, png: string | undefined): Promise<void> {
  const inbox = path.join(root, "inbox");
  const backups = path.join(root, "backups");
  const seedDir = path.join(root, "seed");
  if (existsSync(inbox) && readdirSync(inbox).length > 0) throw new Error(`${inbox} already holds files`);
  mkdirSync(inbox, { recursive: true });
  mkdirSync(backups, { recursive: true });
  mkdirSync(seedDir, { recursive: true });
  await withBackend(root, async (backend) => {
    await api(backend, "PUT", "/settings/capture", { inbox_dir: inbox, backup_dir: backups });
    if (png !== undefined) {
      if (!existsSync(png)) throw new Error(`${png} is missing; run eval-seed.py first`);
      const name = path.basename(png);
      copyFileSync(png, path.join(inbox, name));
      const listed = (await api(backend, "GET", "/captures")) as { items: { id: string; original_path: string }[] };
      const sources = listed.items.filter((item) => path.basename(item.original_path) === name);
      if (sources.length !== 1) throw new Error(`expected one ${name} shot, found ${sources.length}`);
      // EVAL_RUN binds the measured export to this id, so an export of another shot can't pass.
      writeFileSync(path.join(seedDir, "source-id.txt"), `${sources[0].id}\n`);
      console.log(`shot ${sources[0].id} ${name}`);
    }
    console.log(`eval-harness seed: inbox ${inbox}`);
  });
}

async function describe(root: string): Promise<void> {
  await withBackend(root, (backend) =>
    withServer(backend, async (client) => {
      const tools: ToolInfo[] = [];
      let cursor: string | undefined;
      do {
        const page = await client.listTools(cursor ? { cursor } : undefined);
        tools.push(...page.tools);
        cursor = page.nextCursor;
      } while (cursor);
      const picked = TOOLS.map((name) => {
        const tool = tools.find((t) => t.name === name);
        if (!tool) throw new Error(`${name} is not advertised`);
        return tool;
      });
      console.log("## Server instructions\n");
      console.log(client.getInstructions() ?? "(none)");
      for (const tool of picked) {
        console.log(`\n## ${tool.name} description\n`);
        console.log(tool.description ?? "(none)");
        console.log(`\n## ${tool.name} input schema\n`);
        console.log(JSON.stringify(tool.inputSchema, null, 2));
      }
      console.log(`\n${CUT}`);
      for (const tool of picked) {
        const actions = (tool._meta?.action_descriptions ?? {}) as Record<string, string>;
        console.log(`\n## ${tool.name} action notes\n`);
        for (const [key, text] of Object.entries(actions)) console.log(`- ${key}: ${text}`);
      }
    }),
  );
}

async function call(root: string, tool: string | undefined, raw: string | undefined): Promise<void> {
  if (!tool || !raw) throw new Error("call needs a tool name and one JSON argument");
  const args = JSON.parse(raw) as Record<string, unknown>;
  const ledger = path.join(root, "ledger.jsonl");
  const action = typeof args.action === "string" ? args.action : "";
  if (!ALLOWED[tool]?.has(action)) {
    appendFileSync(ledger, `${JSON.stringify({ at: new Date().toISOString(), tool, args, refused: true, isError: true, text: "", images: [] })}\n`);
    console.log(`refused: the harness doesn't run ${tool} ${action} in this test (no call was made)`);
    return;
  }
  await withBackend(root, (backend) =>
    withServer(backend, async (client) => {
      let isError = true;
      let text = "";
      const images: string[] = [];
      try {
        const res = await client.callTool({ name: tool, arguments: args }, undefined, { timeout: CALL_TIMEOUT_MS });
        isError = res.isError === true;
        const parts: string[] = [];
        for (const c of res.content ?? []) {
          if (c.type === "text") parts.push(c.text ?? "");
          if (c.type === "image" && c.data) {
            const views = path.join(root, "views");
            mkdirSync(views, { recursive: true });
            const file = path.join(views, `${String(readdirSync(views).length + 1).padStart(3, "0")}.png`);
            writeFileSync(file, Buffer.from(c.data, "base64"));
            images.push(file);
            parts.push(`image saved: ${file.replaceAll("\\", "/")} (open it with the Read tool to view it)`);
          }
        }
        text = parts.join("\n");
      } catch (err) {
        text = err instanceof Error ? err.message : String(err);
      }
      appendFileSync(ledger, `${JSON.stringify({ at: new Date().toISOString(), tool, args, refused: false, isError, text, images })}\n`);
      console.log(text);
    }),
  );
}

const [rawRoot, command, ...rest] = process.argv.slice(2);
let run: Promise<void> | null = null;
try {
  const root = evalRoot(rawRoot);
  run = command === "seed" ? seed(root, rest[0]) : command === "describe" ? describe(root) : command === "call" ? call(root, rest[0], rest[1]) : null;
} catch (err) {
  console.error(`eval-harness: ${err instanceof Error ? err.message : String(err)}`);
  process.exit(2);
}
if (run === null) {
  console.error("usage: eval-harness.ts <root> seed [png] | describe | call <tool> '<json>'");
  process.exit(2);
}
run.then(
  () => process.exit(0),
  (err: unknown) => {
    console.error(`eval-harness: ${err instanceof Error ? err.message : String(err)}`);
    process.exit(1);
  },
);
