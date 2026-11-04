/**
 * MCP_LAUNCH and the SDK stdio client the runner uses as an IDE would (05 §Client; D-2).
 * The launch env is exactly the copyMcpConfig payload ({AVKIT_API_TOKEN, AVKIT_APP_DATA},
 * ui/src/main/ipc.ts:392-405) plus the OS keys below. AVKIT_API_BASE is never set, so the
 * server discovers the API through {AVKIT_APP_DATA}/backend.json. The SDK transport also merges
 * its own DEFAULT_INHERITED_ENV_VARS (no AVKIT_* key among them), as every SDK client does (A5).
 */
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { ElicitRequestSchema, type ElicitResult } from "@modelcontextprotocol/sdk/types.js";
import { USER_CONFIRM_AUTODECLINE_MS } from "../../src/destructive.js";
import type { ElicitPolicy, ToolCallOutcome } from "./types.js";

/** AUDIT_ELICITATION: the client answers USER_CONFIRM prompts as the operator's stand-in. */
export const AUDIT_CLIENT_CAPABILITIES = { elicitation: {} };

/**
 * The audit answers a prompt as the operator would, not instantly: an answer faster than
 * USER_CONFIRM_AUTODECLINE_MS reads as a client auto-decline and opens the native dialog (A-11).
 */
export const AUDIT_ANSWER_DELAY_MS = USER_CONFIRM_AUTODECLINE_MS * 2;

/** An unplanned prompt is never auto-accepted. */
export const DEFAULT_ELICIT_POLICY: ElicitPolicy = "decline";

export function elicitAnswer(policy: ElicitPolicy): ElicitResult {
  return policy === "accept" ? { action: "accept", content: { confirm: true } } : { action: "decline" };
}

/** OS keys a child process needs to start; nothing else from the parent env is passed. */
export const ALLOWED_PASSTHROUGH_ENV: readonly string[] = ["PATH", "SystemRoot", "TEMP", "TMP", "HOME", "USERPROFILE"];

export type Launch = { command: string; args: string[]; env: Record<string, string> };

export function buildLaunch(input: {
  serverPath: string;
  token: string;
  appData: string;
  parentEnv: Record<string, string | undefined>;
}): Launch {
  const env: Record<string, string> = {};
  for (const key of ALLOWED_PASSTHROUGH_ENV) {
    const value = input.parentEnv[key];
    if (value !== undefined && value !== "") env[key] = value;
  }
  env.AVKIT_API_TOKEN = input.token;
  env.AVKIT_APP_DATA = input.appData;
  return { command: "node", args: [input.serverPath], env };
}

type ContentItem = { type: string; text?: string; data?: string; mimeType?: string };

/** Thin wrapper over the SDK client: never throws for a tool error, captures server stderr. */
export class AuditClient {
  private readonly client = new Client(
    { name: "avkit-mcp-audit", version: "0.1.0" },
    { capabilities: AUDIT_CLIENT_CAPABILITIES },
  );
  /** The policy of the tools/call in flight; calls are sequential, so one slot is enough. */
  private policy: ElicitPolicy = DEFAULT_ELICIT_POLICY;

  constructor() {
    this.client.setRequestHandler(ElicitRequestSchema, async () => {
      const policy = this.policy;
      await new Promise((resolve) => setTimeout(resolve, AUDIT_ANSWER_DELAY_MS));
      return elicitAnswer(policy);
    });
  }
  private transport: StdioClientTransport | null = null;
  private stderrText = "";
  initialized = false;

  async connect(launch: Launch): Promise<void> {
    this.transport = new StdioClientTransport({
      command: launch.command,
      args: launch.args,
      env: launch.env,
      stderr: "pipe",
    });
    this.transport.stderr?.on("data", (chunk: Buffer) => {
      this.stderrText += chunk.toString("utf8");
    });
    await this.client.connect(this.transport);
    this.initialized = true;
  }

  stderr(): string {
    return this.stderrText;
  }

  async listTools(): Promise<{ name: string; inputSchema: unknown; _meta?: Record<string, unknown> }[]> {
    const out: { name: string; inputSchema: unknown; _meta?: Record<string, unknown> }[] = [];
    let cursor: string | undefined;
    do {
      const page = await this.client.listTools(cursor ? { cursor } : undefined);
      for (const tool of page.tools) out.push({ name: tool.name, inputSchema: tool.inputSchema, _meta: tool._meta });
      cursor = page.nextCursor;
    } while (cursor);
    return out;
  }

  async readResourceText(uri: string): Promise<string> {
    const res = await this.client.readResource({ uri });
    const first = res.contents[0] as { text?: string } | undefined;
    if (!first || typeof first.text !== "string") throw new Error(`resource ${uri} has no text content`);
    return first.text;
  }

  /** tools/call; protocol errors (e.g. SDK input validation) come back as isError results. */
  async call(name: string, args: Record<string, unknown>, opts?: { elicit?: ElicitPolicy }): Promise<ToolCallOutcome> {
    this.policy = opts?.elicit ?? DEFAULT_ELICIT_POLICY;
    try {
      const res = await this.client.callTool({ name, arguments: args });
      const content = (Array.isArray(res.content) ? res.content : []) as ContentItem[];
      const text = content.filter((c) => c.type === "text").map((c) => c.text ?? "").join("\n");
      const img = content.find((c) => c.type === "image" && typeof c.data === "string");
      return {
        isError: res.isError === true,
        text,
        ...(img ? { image: { data: img.data as string, mimeType: img.mimeType ?? "" } } : {}),
      };
    } catch (err) {
      return { isError: true, text: err instanceof Error ? err.message : String(err) };
    } finally {
      this.policy = DEFAULT_ELICIT_POLICY;
    }
  }

  /** Close error text, if the transport was already gone (e.g. after a server crash). */
  closeError: string | null = null;

  async close(): Promise<void> {
    try {
      await this.client.close();
    } catch (err) {
      this.closeError = err instanceof Error ? err.message : String(err);
    }
  }
}
