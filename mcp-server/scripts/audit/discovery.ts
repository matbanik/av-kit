/**
 * Phase 1 extraction from a `tools/list` entry: the action values the advertised inputSchema
 * exposes (if any) and the `_meta.action_descriptions` keys (the served action set, A2).
 */

type Json = Record<string, unknown>;

const rec = (v: unknown): Json => (v && typeof v === "object" && !Array.isArray(v) ? (v as Json) : {});

function actionValues(schema: Json): string[] {
  const action = rec(rec(schema.properties).action);
  if (typeof action.const === "string") return [action.const];
  if (Array.isArray(action.enum)) return action.enum.filter((v): v is string => typeof v === "string");
  return [];
}

/** Action literals advertised by a JSON schema (object, or anyOf/oneOf of objects); null if none. */
export function extractSchemaActions(inputSchema: unknown): string[] | null {
  const schema = rec(inputSchema);
  const branches = [...(Array.isArray(schema.anyOf) ? schema.anyOf : []), ...(Array.isArray(schema.oneOf) ? schema.oneOf : [])];
  const values = new Set<string>(actionValues(schema));
  for (const branch of branches) for (const v of actionValues(rec(branch))) values.add(v);
  return values.size === 0 ? null : [...values];
}

/** `_meta.action_descriptions` keys. */
export function extractMetaActions(meta: Record<string, unknown> | undefined): string[] {
  return Object.keys(rec(rec(meta).action_descriptions));
}

/** Text that marks a listed action as not callable (ghost). */
export const GHOST_PATTERN = /unknown_action|Tool \S+ not found|Tool \S+ disabled/;
