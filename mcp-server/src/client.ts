import { collectTokenSecrets, resolveApiBase, resolveToken, type ConfigError } from "./config.js";

export type EnvelopeError = {
  code: string;
  message: string;
  details?: unknown;
};

export type ApiOk<T> = { ok: true; data: T };
export type ApiErr = { ok: false; error: ConfigError | EnvelopeError; status?: number };
export type ApiResult<T> = ApiOk<T> | ApiErr;

export const ADD_TIMEOUT_MS = 120_000;
export const DEFAULT_TIMEOUT_MS = 30_000;

export const AUTH_EXEMPT_PATHS = new Set(["/health"]);

function joinUrl(base: string, path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${base.replace(/\/$/, "")}${p}`;
}

function parseEnvelope(body: unknown, fallbackStatus: number): EnvelopeError {
  if (body && typeof body === "object" && "error" in body) {
    const err = (body as { error?: { code?: unknown; message?: unknown; details?: unknown } }).error;
    if (err && typeof err.code === "string" && typeof err.message === "string") {
      return { code: err.code, message: err.message, details: err.details ?? null };
    }
  }
  return {
    code: "fetch_failed",
    message: `HTTP ${fallbackStatus}`,
  };
}

export function redactSecrets(text: string, secrets: string[]): string {
  let out = text;
  for (const secret of secrets) {
    if (secret) {
      out = out.split(secret).join("[redacted]");
    }
  }
  return out;
}

function redactUnknown(value: unknown, secrets: string[]): unknown {
  if (typeof value === "string") {
    return redactSecrets(value, secrets);
  }
  if (Array.isArray(value)) {
    return value.map((item) => redactUnknown(item, secrets));
  }
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [key, child] of Object.entries(value as Record<string, unknown>)) {
      out[key] = redactUnknown(child, secrets);
    }
    return out;
  }
  return value;
}

export function toToolError(
  error: ConfigError | EnvelopeError,
  env?: NodeJS.ProcessEnv,
): {
  content: [{ type: "text"; text: string }];
  isError: true;
} {
  const secrets = collectTokenSecrets(env);
  const text = redactSecrets(`${error.code}: ${error.message}`, secrets);
  return {
    content: [{ type: "text", text }],
    isError: true,
  };
}

export async function api<T>(
  method: string,
  path: string,
  body?: unknown,
  options?: {
    env?: NodeJS.ProcessEnv;
    timeoutMs?: number;
    fetchImpl?: typeof fetch;
  },
): Promise<ApiResult<T>> {
  const env = options?.env ?? process.env;
  const base = resolveApiBase(env);
  if (!base.ok) {
    return { ok: false, error: base.error };
  }

  const exempt = AUTH_EXEMPT_PATHS.has(path);
  let token: string | undefined;
  if (!exempt) {
    const tok = resolveToken(env);
    if (!tok.ok) {
      return { ok: false, error: tok.error };
    }
    token = tok.token;
  } else {
    const tok = resolveToken(env);
    if (tok.ok) {
      token = tok.token;
    }
  }

  const headers: Record<string, string> = { Accept: "application/json" };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const timeoutMs = options?.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const fetchImpl = options?.fetchImpl ?? fetch;
  try {
    const res = await fetchImpl(joinUrl(base.apiBase, path), {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(timeoutMs),
    });
    let parsed: unknown = null;
    const text = await res.text();
    if (text) {
      try {
        parsed = JSON.parse(text) as unknown;
      } catch {
        parsed = text;
      }
    }
    if (!res.ok) {
      const secrets = collectTokenSecrets(env);
      const envelope = parseEnvelope(parsed, res.status);
      return {
        ok: false,
        error: {
          code: envelope.code,
          message: redactSecrets(envelope.message, secrets),
          details: redactUnknown(envelope.details, secrets),
        },
        status: res.status,
      };
    }
    return { ok: true, data: redactUnknown(parsed, collectTokenSecrets(env)) as T };
  } catch {
    return {
      ok: false,
      error: { code: "fetch_failed", message: "fetch failed" },
    };
  }
}

export type ApiBinaryOk = { ok: true; bytes: Uint8Array; mimeType: string };
export type ApiBinaryResult = ApiBinaryOk | ApiErr;

function sniffImageMime(bytes: Uint8Array, declared: string): string {
  if (
    bytes.length >= 8
    && bytes[0] === 0x89
    && bytes[1] === 0x50
    && bytes[2] === 0x4e
    && bytes[3] === 0x47
    && bytes[4] === 0x0d
    && bytes[5] === 0x0a
    && bytes[6] === 0x1a
    && bytes[7] === 0x0a
  ) {
    return "image/png";
  }
  if (bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) {
    return "image/jpeg";
  }
  if (
    bytes.length >= 12
    && bytes[0] === 0x52
    && bytes[1] === 0x49
    && bytes[2] === 0x46
    && bytes[3] === 0x46
    && bytes[8] === 0x57
    && bytes[9] === 0x45
    && bytes[10] === 0x42
    && bytes[11] === 0x50
  ) {
    return "image/webp";
  }
  return declared;
}

export async function apiBinary(
  method: string,
  path: string,
  options?: {
    env?: NodeJS.ProcessEnv;
    timeoutMs?: number;
    fetchImpl?: typeof fetch;
  },
): Promise<ApiBinaryResult> {
  const env = options?.env ?? process.env;
  const base = resolveApiBase(env);
  if (!base.ok) {
    return { ok: false, error: base.error };
  }
  const tok = resolveToken(env);
  if (!tok.ok) {
    return { ok: false, error: tok.error };
  }
  const headers: Record<string, string> = {
    Accept: "image/*, application/json",
    Authorization: `Bearer ${tok.token}`,
  };
  const timeoutMs = options?.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const fetchImpl = options?.fetchImpl ?? fetch;
  try {
    const res = await fetchImpl(joinUrl(base.apiBase, path), {
      method,
      headers,
      signal: AbortSignal.timeout(timeoutMs),
    });
    const declared = (res.headers.get("Content-Type") ?? "application/octet-stream").split(";")[0]?.trim()
      || "application/octet-stream";
    const buffer = new Uint8Array(await res.arrayBuffer());
    const mimeType = sniffImageMime(buffer, declared);
    if (!res.ok) {
      let parsed: unknown = null;
      const text = new TextDecoder().decode(buffer);
      if (text) {
        try {
          parsed = JSON.parse(text) as unknown;
        } catch {
          parsed = text;
        }
      }
      const secrets = collectTokenSecrets(env);
      const envelope = parseEnvelope(parsed, res.status);
      return {
        ok: false,
        error: {
          code: envelope.code,
          message: redactSecrets(envelope.message, secrets),
          details: redactUnknown(envelope.details, secrets),
        },
        status: res.status,
      };
    }
    return { ok: true, bytes: buffer, mimeType };
  } catch {
    return {
      ok: false,
      error: { code: "fetch_failed", message: "fetch failed" },
    };
  }
}
