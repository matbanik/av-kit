import { randomUUID } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import http from "node:http";
import type { AddressInfo } from "node:net";
import path from "node:path";
import type { BackendHandle, BackendLauncher } from "../../scripts/audit/backend.js";
import { SETTINGS_SCHEMA } from "../../src/toolsets/settings.js";

/** Behaviour switches for the negative oracles of the fake-backend suite. */
export type FakeOptions = {
  /** POST /downloads answers 201 but stores nothing (AC-68.6 hollow). */
  hollowDownloadAdd?: boolean;
  /** PUT /settings/{ns} silently ignores these "ns.key" leaves (AC-68.8 isolation refusal). */
  ignoreSettingKeys?: string[];
  /** The download row disappears on its Nth GET (AC-68.7 refusal_mutated). */
  vanishDownloadOnGet?: number;
  /** Do not provision {app_data}/mcp-token.txt (AC-68.1 token_missing: no file fallback). */
  noTokenFile?: boolean;
};

export type FakeState = {
  requests: { method: string; path: string }[];
  /** Mutating requests outside /settings (AC-68.8: zero before the guard passes). */
  lifecycleMutations: () => number;
};

type Job = { id: string; url: string; status: string; queue_position: number };

const PREFIX = "/api/v1";

function defaults(): Record<string, Record<string, unknown>> {
  const out: Record<string, Record<string, unknown>> = {};
  for (const [ns, leaves] of Object.entries(SETTINGS_SCHEMA.namespaces)) {
    out[ns] = Object.fromEntries(Object.entries(leaves).map(([key, leaf]) => [key, leaf.default]));
  }
  return out;
}

function send(res: http.ServerResponse, status: number, body?: unknown): void {
  if (body === undefined) {
    res.writeHead(status);
    res.end();
    return;
  }
  res.writeHead(status, { "content-type": "application/json" });
  res.end(JSON.stringify(body));
}

function notFound(res: http.ServerResponse, what: string): void {
  send(res, 404, { error: { code: "not_found", message: `${what} not found`, details: null } });
}

async function readJson(req: http.IncomingMessage): Promise<Record<string, unknown>> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) chunks.push(chunk as Buffer);
  const text = Buffer.concat(chunks).toString("utf8");
  return text ? (JSON.parse(text) as Record<string, unknown>) : {};
}

/**
 * Builds a launcher that serves a small in-memory subset of the av-kit REST API on 127.0.0.1:0
 * and writes `backend.json` the way `avkit_api.cli.write_descriptor` does, so the real built
 * MCP server discovers it through AVKIT_APP_DATA exactly as it would the real backend.
 */
export function fakeLauncher(options: FakeOptions = {}): { launcher: BackendLauncher; state: FakeState } {
  const requests: { method: string; path: string }[] = [];
  const state: FakeState = {
    requests,
    lifecycleMutations: () =>
      requests.filter((r) => r.method !== "GET" && !r.path.startsWith(`${PREFIX}/settings/`)).length,
  };
  const launcher: BackendLauncher = async (root: string): Promise<BackendHandle> => {
    const guiToken = `gui-${randomUUID()}`;
    const mcpToken = `mcp-${randomUUID()}`;
    const appData = path.join(root, "app-data");
    mkdirSync(appData, { recursive: true });
    const settings = defaults();
    const jobs = new Map<string, Job>();
    const flattens = new Map<string, number>();
    let gets = 0;
    const server = http.createServer(async (req, res) => {
      const url = new URL(req.url ?? "/", "http://127.0.0.1");
      const p = url.pathname;
      const method = req.method ?? "GET";
      requests.push({ method, path: p });
      try {
        if (p === `${PREFIX}/health`) return send(res, 200, { status: "ok" });
        const auth = req.headers.authorization ?? "";
        if (auth !== `Bearer ${guiToken}` && auth !== `Bearer ${mcpToken}`) {
          return send(res, 401, { error: { code: "unauthorized", message: "bad token", details: null } });
        }
        const ns = p.match(/^\/api\/v1\/settings\/([a-z]+)$/)?.[1];
        if (ns) {
          if (!settings[ns]) return notFound(res, `namespace ${ns}`);
          if (method === "PUT") {
            const body = await readJson(req);
            for (const [key, value] of Object.entries(body)) {
              if (!options.ignoreSettingKeys?.includes(`${ns}.${key}`)) settings[ns][key] = value;
            }
          }
          return send(res, 200, settings[ns]);
        }
        if (p === `${PREFIX}/downloads` && method === "POST") {
          const body = await readJson(req);
          const job: Job = { id: randomUUID(), url: String(body.url), status: "Queued", queue_position: jobs.size };
          if (!options.hollowDownloadAdd) jobs.set(job.id, job);
          return send(res, 201, { items: [job] });
        }
        if (p === `${PREFIX}/downloads` && method === "GET") {
          return send(res, 200, { items: [...jobs.values()], processor: { state: "Idle", current_job_id: null } });
        }
        if (p === `${PREFIX}/downloads` && method === "DELETE") {
          jobs.clear();
          return send(res, 204);
        }
        const id = p.match(/^\/api\/v1\/downloads\/([0-9a-f-]{36})$/)?.[1];
        if (id) {
          if (method === "GET") {
            gets += 1;
            if (options.vanishDownloadOnGet !== undefined && gets >= options.vanishDownloadOnGet) jobs.delete(id);
            const job = jobs.get(id);
            return job ? send(res, 200, job) : notFound(res, `download ${id}`);
          }
          if (method === "DELETE") {
            return jobs.delete(id) ? send(res, 204) : notFound(res, `download ${id}`);
          }
        }
        if ([`${PREFIX}/transcripts`, `${PREFIX}/conversions`].includes(p) && method === "GET") {
          return send(res, 200, { items: [], processor: { state: "Idle", current_job_id: null } });
        }
        if ([`${PREFIX}/captures`, `${PREFIX}/captures/requests`].includes(p) && method === "GET") {
          return send(res, 200, { items: [] });
        }
        // FIXTURE_REPAIRS (b) (Session 30): flatten bumps a per-shot counter that the detail reports.
        const shot = p.match(/^\/api\/v1\/captures\/([A-Za-z0-9_-]+)(\/flatten)?$/);
        if (shot && shot[1] !== "requests") {
          const shotId = shot[1] as string;
          if (shot[2] && method === "POST") flattens.set(shotId, (flattens.get(shotId) ?? 0) + 1);
          if ((shot[2] && method === "POST") || (!shot[2] && method === "GET")) {
            return send(res, 200, { id: shotId, flatten_count: flattens.get(shotId) ?? 0 });
          }
        }
        if (p === "/openapi.json") return send(res, 200, { info: { version: "fake-0" } });
        return notFound(res, `${method} ${p}`);
      } catch (err) {
        return send(res, 500, { error: { code: "fake_error", message: String(err), details: null } });
      }
    });
    await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
    const { port } = server.address() as AddressInfo;
    const apiBase = `http://127.0.0.1:${port}${PREFIX}`;
    writeFileSync(
      path.join(appData, "backend.json"),
      JSON.stringify({ schema_version: 1, host: "127.0.0.1", port, bind: "127.0.0.1", api_base: apiBase, app_data: appData }),
    );
    if (!options.noTokenFile) writeFileSync(path.join(appData, "mcp-token.txt"), mcpToken);
    let exited = false;
    return {
      apiBase,
      guiToken,
      mcpToken,
      appData,
      stop: async () => {
        await new Promise<void>((resolve) => server.close(() => resolve()));
        exited = true;
        return { exited };
      },
    };
  };
  return { launcher, state };
}
