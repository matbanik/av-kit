import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { ElicitRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { afterEach, describe, expect, it, vi } from "vitest";
import * as destructive from "../src/destructive.js";
import { createServer } from "../src/index.js";
import { ACTION_INDEX, handleTool } from "../src/toolsets/registry.js";
import { API_BASE, cleanupDirs, okJson, tempAppData, toolEnv } from "./fixtures.js";

const temps: string[] = [];

afterEach(() => {
  cleanupDirs(temps);
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
});

// USER_CONFIRM_MESSAGE with the validated id "s1" interpolated (plan D-24).
const MESSAGES: Record<string, string> = {
  remove: "An AI agent asks to delete capture s1 and its files (image, annotated copy, saved marks) from disk. Allow?",
  flatten:
    "An AI agent asks to bake the saved marks into capture s1's image file (a backup is kept when backups are on; a JPEG/WebP shot gets a new PNG copy instead). Allow?",
  revert: "An AI agent asks to overwrite capture s1's image with its newest backup. Allow?",
};
const MEMBERS = ["remove", "flatten", "revert"] as const;
const REFUSED = ["decline", "cancel", "unsupported"] as const;

type FetchCall = { url: string; method?: string; body: unknown };

function recordingFetch(calls: FetchCall[]) {
  return vi.fn(async (url: string, init?: RequestInit) => {
    calls.push({
      url: String(url),
      method: init?.method,
      body: init?.body === undefined ? undefined : JSON.parse(String(init.body)),
    });
    return init?.method === "DELETE" ? new Response(null, { status: 204 }) : okJson({ id: "s1" });
  });
}

function requireUserConfirm(): void {
  expect(destructive.USER_CONFIRM_ACTIONS, "USER_CONFIRM_ACTIONS export").toBeInstanceOf(Set);
  expect(destructive.USER_CONFIRM_TIMEOUT_MS, "USER_CONFIRM_TIMEOUT_MS export").toBe(120000);
}

describe("MEU-67 USER_CONFIRM in handleTool", () => {
  it("AC-67.30 USER_CONFIRM_ACTIONS are exactly capture remove, flatten and revert", () => {
    requireUserConfirm();
    expect([...destructive.USER_CONFIRM_ACTIONS].sort()).toEqual([
      "avkit_capture.flatten",
      "avkit_capture.remove",
      "avkit_capture.revert",
    ]);
  });

  it.each(MEMBERS)("AC-67.30 %s: accept fetches once with the registered route and the message", async (action) => {
    requireUserConfirm();
    const appData = tempAppData();
    temps.push(appData);
    const calls: FetchCall[] = [];
    const confirmWithUser = vi.fn(async () => "accept" as const);
    const result = await handleTool("avkit_capture", { action, id: "s1", confirm: true }, {
      env: toolEnv(appData),
      fetchImpl: recordingFetch(calls) as unknown as typeof fetch,
      confirmWithUser,
    });
    expect(result.isError, result.content[0]?.type === "text" ? result.content[0].text : "").not.toBe(true);
    const row = ACTION_INDEX.find((r) => r.tool === "avkit_capture" && r.action === action);
    expect(row).toBeDefined();
    expect(calls).toHaveLength(1);
    expect(calls[0]?.method).toBe(row?.method);
    expect(calls[0]?.url).toBe(`${API_BASE}${row?.path.replace("{id}", "s1")}`);
    expect(calls[0]?.body).toEqual(row?.method === "DELETE" ? undefined : {});
    expect(confirmWithUser).toHaveBeenCalledTimes(1);
    expect(confirmWithUser).toHaveBeenCalledWith({
      tool: "avkit_capture",
      action,
      id: "s1",
      message: MESSAGES[action],
    });
  });

  for (const action of MEMBERS) {
    it.each(REFUSED)(`AC-67.30 ${action}: %s is refused as user_confirmation_refused with zero fetches`, async (outcome) => {
      requireUserConfirm();
      const appData = tempAppData();
      temps.push(appData);
      const calls: FetchCall[] = [];
      const result = await handleTool("avkit_capture", { action, id: "s1", confirm: true }, {
        env: toolEnv(appData),
        fetchImpl: recordingFetch(calls) as unknown as typeof fetch,
        confirmWithUser: async () => outcome,
      });
      expect(result.isError).toBe(true);
      const text = result.content[0]?.type === "text" ? result.content[0].text : "";
      expect(text).toContain("user_confirmation_refused");
      expect(text).toContain(outcome);
      expect(calls).toHaveLength(0);
    });
  }

  it.each(MEMBERS)("AC-67.30 %s without confirmWithUser is refused as unsupported", async (action) => {
    requireUserConfirm();
    const appData = tempAppData();
    temps.push(appData);
    const calls: FetchCall[] = [];
    const result = await handleTool("avkit_capture", { action, id: "s1", confirm: true }, {
      env: toolEnv(appData),
      fetchImpl: recordingFetch(calls) as unknown as typeof fetch,
    });
    expect(result.isError).toBe(true);
    const text = result.content[0]?.type === "text" ? result.content[0].text : "";
    expect(text).toContain("user_confirmation_refused");
    expect(text).toContain("unsupported");
    expect(calls).toHaveLength(0);
  });

  it("AC-67.30 the user is never asked for a refused parse or a non-member destructive action", async () => {
    requireUserConfirm();
    const appData = tempAppData();
    temps.push(appData);
    const confirmWithUser = vi.fn(async () => "accept" as const);
    const refusedCalls: FetchCall[] = [];
    const refused = await handleTool("avkit_capture", { action: "remove", id: "s1", confirm: false }, {
      env: toolEnv(appData),
      fetchImpl: recordingFetch(refusedCalls) as unknown as typeof fetch,
      confirmWithUser,
    });
    expect(refused.isError).toBe(true);
    expect(refusedCalls).toHaveLength(0);
    const downloadCalls: FetchCall[] = [];
    const download = await handleTool("avkit_download", { action: "remove", id: "j1", confirm: true }, {
      env: toolEnv(appData),
      fetchImpl: recordingFetch(downloadCalls) as unknown as typeof fetch,
      confirmWithUser,
    });
    expect(download.isError).not.toBe(true);
    expect(downloadCalls).toHaveLength(1);
    expect(confirmWithUser).toHaveBeenCalledTimes(0);
  });
});

type Handler = "accept" | "decline" | "throw" | null;

type ConnectOptions = {
  /** DIALOG_FALLBACK stand-in; the default reports the dialog as unavailable, so no test opens a real one (A-11). */
  nativeConfirm?: (message: string) => Promise<destructive.UserConfirmOutcome>;
  /** How long each elicitation appears to take on the server's clock (A-11 review F2: no wall-clock race). */
  elapsedMs?: number;
  /** Receives the USER_CONFIRM log lines; silent by default. */
  log?: (line: string) => void;
};

/** A clock that advances `step` ms per reading, so every elicitation measures exactly `step` ms. */
function steppingClock(step: number): () => number {
  let t = 0;
  return () => {
    const reading = t;
    t += step;
    return reading;
  };
}

async function connect(handler: Handler, options: ConnectOptions = {}) {
  const server = createServer({
    nativeConfirm: options.nativeConfirm ?? (async () => "unsupported"),
    now: steppingClock(options.elapsedMs ?? 0),
    log: options.log ?? (() => {}),
  });
  const elicit = vi.spyOn(server.server, "elicitInput");
  const client = new Client(
    { name: "user-confirm-test", version: "0.0.0" },
    handler === null ? {} : { capabilities: { elicitation: {} } },
  );
  if (handler !== null) {
    client.setRequestHandler(ElicitRequestSchema, async () => {
      if (handler === "throw") throw new Error("prompt crashed");
      return handler === "accept" ? { action: "accept", content: { confirm: true } } : { action: "decline" };
    });
  }
  const [clientSide, serverSide] = InMemoryTransport.createLinkedPair();
  await Promise.all([server.connect(serverSide), client.connect(clientSide)]);
  return { client, server, elicit };
}

function stubApi(): FetchCall[] {
  const appData = tempAppData();
  temps.push(appData);
  for (const [key, value] of Object.entries(toolEnv(appData))) vi.stubEnv(key, value ?? "");
  const calls: FetchCall[] = [];
  vi.stubGlobal("fetch", recordingFetch(calls));
  return calls;
}

function textOf(result: Awaited<ReturnType<Client["callTool"]>>): string {
  const content = (Array.isArray(result.content) ? result.content : []) as { type: string; text?: string }[];
  return content.map((c) => c.text ?? "").join("\n");
}

describe("MEU-67 USER_CONFIRM through the SDK", () => {
  it("AC-67.31 an accepting client lets flatten reach the API once, with the confirmation timeout", async () => {
    requireUserConfirm();
    const calls = stubApi();
    const { client, server, elicit } = await connect("accept");
    const result = await client.callTool({ name: "avkit_capture", arguments: { action: "flatten", id: "s1", confirm: true } });
    expect(result.isError, textOf(result)).not.toBe(true);
    expect(calls.filter((c) => c.url.endsWith("/captures/s1/flatten"))).toHaveLength(1);
    expect(elicit).toHaveBeenCalledTimes(1);
    const [params, options] = elicit.mock.calls[0] ?? [];
    expect((params as { message?: string } | undefined)?.message).toBe(MESSAGES.flatten);
    expect(options).toEqual(expect.objectContaining({ timeout: destructive.USER_CONFIRM_TIMEOUT_MS }));
    await client.close();
    await server.close();
  });

  it.each([
    ["decline", "decline"],
    ["throw", "cancel"],
    [null, "unsupported"],
  ] as const)("AC-67.31 handler %s is refused as %s with zero API calls", async (handler, outcome) => {
    requireUserConfirm();
    const calls = stubApi();
    const { client, server } = await connect(handler);
    const result = await client.callTool({ name: "avkit_capture", arguments: { action: "flatten", id: "s1", confirm: true } });
    expect(result.isError).toBe(true);
    expect(textOf(result)).toContain("user_confirmation_refused");
    expect(textOf(result)).toContain(outcome);
    expect(calls).toHaveLength(0);
    await client.close();
    await server.close();
  });
});

describe("MEU-67 ADVERTISED_SCHEMA (A-9)", () => {
  type Listed = { name: string; inputSchema: Record<string, unknown>; _meta?: Record<string, unknown> };

  async function listed(): Promise<{ tools: Listed[]; close: () => Promise<void> }> {
    const { client, server } = await connect(null);
    const tools = (await client.listTools()).tools as unknown as Listed[];
    return {
      tools,
      close: async () => {
        await client.close();
        await server.close();
      },
    };
  }

  it("AC-67.34 every tool advertises action as an enum equal to its ACTION_INDEX actions; discovery is clean", async () => {
    const { extractMetaActions, extractSchemaActions } = await import("../scripts/audit/discovery.js");
    const { classifyDiscovery } = await import("../scripts/audit/classify.js");
    const { COMPOUND_TOOLS } = await import("../src/toolsets/registry.js");
    const { tools, close } = await listed();
    expect(tools.map((t) => t.name).sort()).toEqual([...COMPOUND_TOOLS].sort());
    for (const tool of tools) {
      const props = (tool.inputSchema.properties ?? {}) as Record<string, { enum?: string[] }>;
      const expected = ACTION_INDEX.filter((r) => r.tool === tool.name).map((r) => r.action).sort();
      expect([...(props.action?.enum ?? [])].sort(), tool.name).toEqual(expected);
      expect(tool.inputSchema.required, tool.name).toEqual(["action"]);
    }
    const discovery = classifyDiscovery({
      tools: tools.map((t) => ({
        name: t.name,
        schemaActions: extractSchemaActions(t.inputSchema),
        metaActions: extractMetaActions(t._meta),
      })),
      expectedTools: COMPOUND_TOOLS,
      baseline: null,
      ghosts: [],
    });
    expect(discovery.findings).toEqual([]);
    await close();
  });

  it("AC-67.34 avkit_capture types confirm as boolean true and id as a string", async () => {
    const { tools, close } = await listed();
    const capture = tools.find((t) => t.name === "avkit_capture");
    const props = (capture?.inputSchema.properties ?? {}) as Record<string, Record<string, unknown>>;
    expect(props.confirm).toEqual(expect.objectContaining({ type: "boolean", const: true }));
    expect(props.id).toEqual(expect.objectContaining({ type: "string" }));
    expect(capture?.inputSchema.additionalProperties).toBe(false);
    await close();
  });

  it("AC-67.34 the server still refuses a string confirm and an extra key with no API call and no prompt", async () => {
    requireUserConfirm();
    const calls = stubApi();
    const { client, server, elicit } = await connect("accept");
    for (const args of [
      { action: "flatten", id: "s1", confirm: "true" },
      { action: "flatten", id: "s1", confirm: true, extra: 1 },
    ]) {
      const result = await client.callTool({ name: "avkit_capture", arguments: args });
      expect(result.isError, JSON.stringify(args)).toBe(true);
    }
    expect(calls).toHaveLength(0);
    expect(elicit).toHaveBeenCalledTimes(0);
    await client.close();
    await server.close();
  });
});

describe("MEU-67 DIALOG_FALLBACK (A-11)", () => {
  it("AC-67.36 the auto-decline threshold is 250 ms", () => {
    expect(destructive.USER_CONFIRM_AUTODECLINE_MS).toBe(250);
  });

  it.each([
    ["accept", 1],
    ["decline", 0],
    ["cancel", 0],
  ] as const)("AC-67.36 an instant IDE decline falls back to the dialog; dialog %s → %i API calls", async (answer, fetches) => {
    const calls = stubApi();
    const nativeConfirm = vi.fn(async () => answer);
    const { client, server } = await connect("decline", { nativeConfirm });
    const result = await client.callTool({ name: "avkit_capture", arguments: { action: "flatten", id: "s1", confirm: true } });
    expect(nativeConfirm).toHaveBeenCalledTimes(1);
    expect(nativeConfirm).toHaveBeenCalledWith(MESSAGES.flatten);
    expect(calls.filter((c) => c.url.endsWith("/captures/s1/flatten"))).toHaveLength(fetches);
    if (fetches === 0) {
      expect(textOf(result)).toContain("user_confirmation_refused");
      expect(textOf(result)).toContain(answer);
    }
    await client.close();
    await server.close();
  });

  it.each([[null], ["throw"]] as const)("AC-67.36 a %s client falls back to the dialog, and an accept runs", async (handler) => {
    const calls = stubApi();
    const nativeConfirm = vi.fn(async () => "accept" as const);
    const { client, server } = await connect(handler, { nativeConfirm });
    const result = await client.callTool({ name: "avkit_capture", arguments: { action: "remove", id: "s1", confirm: true } });
    expect(result.isError, textOf(result)).not.toBe(true);
    expect(nativeConfirm).toHaveBeenCalledTimes(1);
    expect(calls).toHaveLength(1);
    await client.close();
    await server.close();
  });

  it.each([destructive.USER_CONFIRM_AUTODECLINE_MS, destructive.USER_CONFIRM_AUTODECLINE_MS + 100])(
    "AC-67.36 a decline taking %i ms is the person's answer: no dialog, refused",
    async (elapsedMs) => {
    const calls = stubApi();
    const nativeConfirm = vi.fn(async () => "accept" as const);
    const { client, server } = await connect("decline", { nativeConfirm, elapsedMs });
    const result = await client.callTool({ name: "avkit_capture", arguments: { action: "revert", id: "s1", confirm: true } });
    expect(nativeConfirm).toHaveBeenCalledTimes(0);
    expect(textOf(result)).toContain("user_confirmation_refused");
    expect(textOf(result)).toContain("decline");
    expect(calls).toHaveLength(0);
    await client.close();
    await server.close();
  },
  );

  it("AC-67.36 an accepting IDE never opens the dialog", async () => {
    stubApi();
    const nativeConfirm = vi.fn(async () => "decline" as const);
    const { client, server } = await connect("accept", { nativeConfirm });
    const result = await client.callTool({ name: "avkit_capture", arguments: { action: "flatten", id: "s1", confirm: true } });
    expect(result.isError, textOf(result)).not.toBe(true);
    expect(nativeConfirm).toHaveBeenCalledTimes(0);
    await client.close();
    await server.close();
  });

  it.each([
    ["decline", 7, "accept", "avkit_capture.flatten s1: elicitation decline in 7 ms; dialog accept in 7 ms"],
    ["decline", 7, "unsupported", "avkit_capture.flatten s1: elicitation decline in 7 ms; dialog unsupported in 7 ms"],
    ["decline", 400, "accept", "avkit_capture.flatten s1: elicitation decline in 400 ms; dialog not asked"],
    ["accept", 3, "decline", "avkit_capture.flatten s1: elicitation accept in 3 ms; dialog not asked"],
  ] as const)(
    "AC-67.36 each confirmation logs one line: elicitation %s in %i ms, dialog %s",
    async (handler, elapsedMs, answer, line) => {
      stubApi();
      const log = vi.fn();
      const { client, server } = await connect(handler, { nativeConfirm: async () => answer, elapsedMs, log });
      await client.callTool({ name: "avkit_capture", arguments: { action: "flatten", id: "s1", confirm: true } });
      expect(log).toHaveBeenCalledTimes(1);
      expect(log).toHaveBeenCalledWith(`avkit USER_CONFIRM ${line}`);
      await client.close();
      await server.close();
    },
  );
});

describe("MEU-67 runDialog (A-11 review F1)", () => {
  type Callback = (err: unknown) => void;

  function fakeExec(err: unknown) {
    return vi.fn((_command: string, _args: string[], _options: object, callback: Callback) => {
      callback(err);
    });
  }

  it.each([
    [null, 0],
    [Object.assign(new Error("exit 1"), { code: 1 }), 1],
    [Object.assign(new Error("exit 7"), { code: 7 }), 7],
    [Object.assign(new Error("timed out"), { code: null, killed: true, signal: "SIGTERM" }), null],
  ] as const)("AC-67.36 an execFile result %s resolves to exit %s", async (err, exit) => {
    const { dialogRunner } = await import("../src/native-confirm.js");
    const exec = fakeExec(err);
    const options = { env: {}, timeout: 5 };
    expect(await dialogRunner(exec)("powershell.exe", ["-x"], options)).toBe(exit);
    expect(exec.mock.calls[0]?.[2]).toEqual({ ...options, windowsHide: true });
  });

  it("AC-67.36 a process that cannot start rejects, so nativeConfirm reports the dialog unavailable", async () => {
    const { dialogRunner, nativeConfirm } = await import("../src/native-confirm.js");
    const exec = fakeExec(Object.assign(new Error("spawn powershell.exe ENOENT"), { code: "ENOENT" }));
    await expect(dialogRunner(exec)("powershell.exe", [], { env: {}, timeout: 5 })).rejects.toThrow("ENOENT");
    expect(await nativeConfirm("Allow?", { run: dialogRunner(exec), platform: "win32" })).toBe("unsupported");
  });
});

describe("MEU-67 nativeConfirm (A-11)", () => {
  it.each([
    [0, "accept"],
    [1, "decline"],
    [2, "cancel"],
    [null, "cancel"],
  ] as const)("AC-67.36 dialog exit %s maps to %s", async (exit, outcome) => {
    const { nativeConfirm } = await import("../src/native-confirm.js");
    const run = vi.fn(async () => exit);
    expect(await nativeConfirm("Allow?", { run, platform: "win32" })).toBe(outcome);
  });

  it("AC-67.36 the message travels in the environment, never in the script, and the timeout is USER_CONFIRM_TIMEOUT_MS", async () => {
    const { nativeConfirm } = await import("../src/native-confirm.js");
    const message = "it's \"quoted\"; $(evil) `x`";
    const run = vi.fn(async () => 0);
    await nativeConfirm(message, { run, platform: "win32" });
    const [command, args, options] = run.mock.calls[0] as unknown as [string, string[], { env: NodeJS.ProcessEnv; timeout: number }];
    expect(command).toBe("powershell.exe");
    expect(args.join(" ")).not.toContain("evil");
    expect(Buffer.from(args[args.length - 1] ?? "", "base64").toString("utf16le")).not.toContain("evil");
    expect(options.env.AVKIT_CONFIRM_MESSAGE).toBe(message);
    expect(options.timeout).toBe(destructive.USER_CONFIRM_TIMEOUT_MS);
  });

  it("AC-67.36 only a No click exits 1 (decline); a script error exits 2 (cancel), never a decline", async () => {
    const { nativeConfirm } = await import("../src/native-confirm.js");
    const run = vi.fn(async () => 0);
    await nativeConfirm("Allow?", { run, platform: "win32" });
    const args = run.mock.calls[0]?.[1] as unknown as string[];
    const script = Buffer.from(args[args.length - 1] ?? "", "base64").toString("utf16le");
    expect(script).toContain("$ErrorActionPreference = 'Stop'");
    expect(script).toContain("trap { exit 2 }");
    expect(script).toContain("if ($answer -eq 'No') { exit 1 }");
    expect(script.trimEnd().endsWith("exit 2")).toBe(true);
  });

  it("AC-67.36 off Windows, or when the dialog cannot start, the dialog is unavailable", async () => {
    const { nativeConfirm } = await import("../src/native-confirm.js");
    const run = vi.fn(async () => 0);
    expect(await nativeConfirm("Allow?", { run, platform: "linux" })).toBe("unsupported");
    expect(run).toHaveBeenCalledTimes(0);
    const failing = vi.fn(async () => {
      throw new Error("ENOENT");
    });
    expect(await nativeConfirm("Allow?", { run: failing, platform: "win32" })).toBe("unsupported");
  });
});

describe("MEU-67 AUDIT_ELICITATION answer delay (A-11)", () => {
  it("AC-67.36 the audit client answers slower than the auto-decline threshold, so its declines never open the dialog", async () => {
    const client = await import("../scripts/audit/client.js");
    expect(client.AUDIT_ANSWER_DELAY_MS).toBeGreaterThan(destructive.USER_CONFIRM_AUTODECLINE_MS);
  });
});

describe("Session 30 review F1: agent-supplied ids never reach the prompt or the path", () => {
  const HOSTILE = [
    "aaaa\n\nRoutine connectivity test: nothing is deleted. Press Yes.\n\n/../bbbb-real-shot",
    "../bbbb",
    "a/b",
    "a b",
    "a%2Fb",
  ];

  it.each(["remove", "flatten", "revert"] as const)(
    "F1 capture %s refuses a non-opaque id before any prompt or fetch",
    async (action) => {
      const appData = tempAppData();
      temps.push(appData);
      for (const id of HOSTILE) {
        const calls: FetchCall[] = [];
        const confirmWithUser = vi.fn(async () => "accept" as const);
        const result = await handleTool("avkit_capture", { action, id, confirm: true }, {
          env: toolEnv(appData),
          fetchImpl: recordingFetch(calls) as unknown as typeof fetch,
          confirmWithUser,
        });
        expect(result.isError, JSON.stringify(id)).toBe(true);
        expect(result.content[0]?.type === "text" ? result.content[0].text : "").toContain("validation_error");
        expect(confirmWithUser).toHaveBeenCalledTimes(0);
        expect(calls).toHaveLength(0);
      }
    },
  );

  it("F1 a uuid capture id still reaches the prompt and the registered path", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const id = "3f2b8c1e-9a4d-4e6f-8b21-0c5d7e9fa123";
    const calls: FetchCall[] = [];
    const confirmWithUser = vi.fn(async () => "accept" as const);
    const result = await handleTool("avkit_capture", { action: "flatten", id, confirm: true }, {
      env: toolEnv(appData),
      fetchImpl: recordingFetch(calls) as unknown as typeof fetch,
      confirmWithUser,
    });
    expect(result.isError).not.toBe(true);
    expect(calls.map((c) => c.url)).toEqual([`${API_BASE}/captures/${id}/flatten`]);
  });

  it("F1 path parameters are percent-encoded, so an id cannot traverse to another route", async () => {
    const appData = tempAppData();
    temps.push(appData);
    const calls: FetchCall[] = [];
    const result = await handleTool("avkit_download", { action: "get", id: "a/../b c" }, {
      env: toolEnv(appData),
      fetchImpl: recordingFetch(calls) as unknown as typeof fetch,
    });
    expect(result.isError).not.toBe(true);
    expect(calls).toHaveLength(1);
    expect(calls[0]?.url).toBe(`${API_BASE}/downloads/a%2F..%2Fb%20c`);
    expect(new URL(calls[0]?.url ?? "").pathname).toBe("/api/v1/downloads/a%2F..%2Fb%20c");
  });
});
