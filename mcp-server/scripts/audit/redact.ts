/**
 * Secret redaction for every string the runner writes to disk (AC-68.14; 05 §What this layer
 * must not do: never store the Bearer token in tool results or logs).
 */

const PLACEHOLDER = "[redacted]";
/** Shorter strings would blank ordinary words; real tokens are UUID-length. */
const MIN_SECRET_LENGTH = 4;

function usable(secrets: string[]): string[] {
  return [...new Set(secrets.map((s) => s.trim()).filter((s) => s.length >= MIN_SECRET_LENGTH))]
    // Longest first so a secret that contains another is replaced whole.
    .sort((a, b) => b.length - a.length);
}

/** Replaces every occurrence of each secret in `text`. */
export function redact(text: string, secrets: string[]): string {
  let out = text;
  for (const secret of usable(secrets)) out = out.split(secret).join(PLACEHOLDER);
  return out;
}

/** Deep copy of `value` with every string (keys included) passed through {@link redact}. */
export function redactDeep<T>(value: T, secrets: string[]): T {
  const list = usable(secrets);
  const walk = (v: unknown): unknown => {
    if (typeof v === "string") return redact(v, list);
    if (Array.isArray(v)) return v.map(walk);
    if (v && typeof v === "object") {
      return Object.fromEntries(Object.entries(v as Record<string, unknown>).map(([k, child]) => [redact(k, list), walk(child)]));
    }
    return v;
  };
  return walk(value) as T;
}
