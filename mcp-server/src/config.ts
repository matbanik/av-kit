import os from "node:os";
import path from "node:path";
import { readFileSync } from "node:fs";

export type ConfigErrorCode =
  | "app_not_running"
  | "stale_pin"
  | "invalid_api_base"
  | "token_missing";

export type ConfigError = {
  code: ConfigErrorCode;
  message: string;
};

export type ApiBaseOk = { ok: true; apiBase: string };
export type ApiBaseErr = { ok: false; error: ConfigError };
export type ApiBaseResult = ApiBaseOk | ApiBaseErr;

export type TokenOk = { ok: true; token: string };
export type TokenErr = { ok: false; error: ConfigError };
export type TokenResult = TokenOk | TokenErr;

type Env = NodeJS.ProcessEnv;

function envOf(env?: Env): Env {
  return env ?? process.env;
}

export function resolveAppData(env?: Env): string {
  const e = envOf(env);
  const override = e.AVKIT_APP_DATA?.trim();
  if (override) {
    return override;
  }
  if (process.platform === "win32") {
    const local = e.LOCALAPPDATA?.trim();
    if (local) {
      return path.join(local, "av-kit");
    }
  }
  return path.join(os.homedir(), ".avkit");
}

function parseHostPort(urlText: string): { host: string; port: string } | null {
  try {
    const u = new URL(urlText);
    return { host: u.hostname, port: u.port || (u.protocol === "https:" ? "443" : "80") };
  } catch {
    return null;
  }
}

export function parseHttpApiBase(urlText: string): string | null {
  try {
    const parsed = new URL(urlText);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      return null;
    }
    if (!parsed.pathname.includes("/api/v1")) {
      return null;
    }
    return urlText.replace(/\/$/, "");
  } catch {
    return null;
  }
}

function readDescriptor(appData: string): { api_base?: string; host?: string; port?: number } | null {
  try {
    const raw = readFileSync(path.join(appData, "backend.json"), "utf8");
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    if (parsed.schema_version !== 1) {
      return null;
    }
    return {
      api_base: typeof parsed.api_base === "string" ? parsed.api_base : undefined,
      host: typeof parsed.host === "string" ? parsed.host : undefined,
      port: typeof parsed.port === "number" ? parsed.port : undefined,
    };
  } catch {
    return null;
  }
}

export function collectTokenSecrets(env?: Env): string[] {
  const e = envOf(env);
  const found = new Set<string>();
  const fromEnv = e.AVKIT_API_TOKEN?.trim();
  if (fromEnv) {
    found.add(fromEnv);
  }
  try {
    const fromFile = readFileSync(path.join(resolveAppData(e), "mcp-token.txt"), "utf8").trim();
    if (fromFile) {
      found.add(fromFile);
    }
  } catch {
    // missing file is not a secret source
  }
  return [...found];
}

export function resolveApiBase(env?: Env): ApiBaseResult {
  const e = envOf(env);
  const pin = e.AVKIT_API_BASE?.trim();
  const appData = resolveAppData(e);
  const desc = readDescriptor(appData);

  if (pin) {
    const parsedPin = parseHttpApiBase(pin);
    if (!parsedPin) {
      return {
        ok: false,
        error: {
          code: "invalid_api_base",
          message: "AVKIT_API_BASE must be an http(s) URL that includes /api/v1",
        },
      };
    }
    if (desc) {
      const pinHp = parseHostPort(pin);
      const descUrl = desc.api_base ?? (desc.host && desc.port != null ? `http://${desc.host}:${desc.port}/api/v1` : "");
      const descHp = desc.host && desc.port != null
        ? { host: desc.host, port: String(desc.port) }
        : parseHostPort(descUrl);
      if (pinHp && descHp && (pinHp.host !== descHp.host || pinHp.port !== descHp.port)) {
        return {
          ok: false,
          error: {
            code: "stale_pin",
            message: "AVKIT_API_BASE host/port does not match the live backend.json descriptor",
          },
        };
      }
    }
    return { ok: true, apiBase: parsedPin };
  }

  if (desc?.api_base) {
    const parsedDesc = parseHttpApiBase(desc.api_base);
    if (parsedDesc) {
      return { ok: true, apiBase: parsedDesc };
    }
  }

  return {
    ok: false,
    error: {
      code: "app_not_running",
      message: "av-kit is not running: set AVKIT_API_BASE or start the app so backend.json exists",
    },
  };
}

export function resolveToken(env?: Env): TokenResult {
  const e = envOf(env);
  const fromEnv = e.AVKIT_API_TOKEN?.trim();
  if (fromEnv) {
    return { ok: true, token: fromEnv };
  }
  const appData = resolveAppData(e);
  try {
    const fromFile = readFileSync(path.join(appData, "mcp-token.txt"), "utf8").trim();
    if (fromFile) {
      return { ok: true, token: fromFile };
    }
  } catch {
    // fall through
  }
  return {
    ok: false,
    error: {
      code: "token_missing",
      message: "MCP token missing: set AVKIT_API_TOKEN or write mcp-token.txt",
    },
  };
}
