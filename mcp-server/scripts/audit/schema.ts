/**
 * Minimal JSON-schema subset validator for the runner's own two schemas
 * (summary.schema.json, baseline.schema.json). Supports: type, const, enum, pattern,
 * required, properties, additionalProperties:false, items, minimum. No new dependency.
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export type JsonSchema = {
  type?: string | string[];
  const?: unknown;
  enum?: unknown[];
  pattern?: string;
  required?: string[];
  properties?: Record<string, JsonSchema>;
  additionalProperties?: boolean | JsonSchema;
  items?: JsonSchema;
  minimum?: number;
};

const HERE = path.dirname(fileURLToPath(import.meta.url));

/** Loads one of the runner's schema files that sit next to this module. */
export function loadSchema(name: "summary.schema.json" | "baseline.schema.json"): JsonSchema {
  return JSON.parse(readFileSync(path.join(HERE, name), "utf8")) as JsonSchema;
}

function typeOf(value: unknown): string {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  if (typeof value === "number") return Number.isInteger(value) ? "integer" : "number";
  return typeof value;
}

function typeMatches(expected: string, actual: string): boolean {
  return expected === actual || (expected === "number" && actual === "integer");
}

/** Returns one message per violation; an empty array means valid. */
export function validate(schema: JsonSchema, value: unknown, at = "$"): string[] {
  const errors: string[] = [];
  const actual = typeOf(value);
  if (schema.type !== undefined) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!types.some((t) => typeMatches(t, actual))) {
      return [`${at}: expected ${types.join("|")}, got ${actual}`];
    }
  }
  if (schema.const !== undefined && value !== schema.const) {
    errors.push(`${at}: expected const ${JSON.stringify(schema.const)}`);
  }
  if (schema.enum !== undefined && !schema.enum.includes(value)) {
    errors.push(`${at}: ${JSON.stringify(value)} not in enum ${JSON.stringify(schema.enum)}`);
  }
  if (schema.pattern !== undefined && typeof value === "string" && !new RegExp(schema.pattern).test(value)) {
    errors.push(`${at}: ${JSON.stringify(value)} does not match ${schema.pattern}`);
  }
  if (schema.minimum !== undefined && typeof value === "number" && value < schema.minimum) {
    errors.push(`${at}: ${value} < minimum ${schema.minimum}`);
  }
  if (actual === "object") {
    const record = value as Record<string, unknown>;
    for (const key of schema.required ?? []) {
      if (!(key in record)) errors.push(`${at}: missing required ${key}`);
    }
    for (const [key, child] of Object.entries(record)) {
      const sub = schema.properties?.[key];
      if (sub) {
        errors.push(...validate(sub, child, `${at}.${key}`));
      } else if (schema.additionalProperties === false) {
        errors.push(`${at}: unexpected key ${key}`);
      } else if (typeof schema.additionalProperties === "object") {
        errors.push(...validate(schema.additionalProperties, child, `${at}.${key}`));
      }
    }
  }
  if (actual === "array" && schema.items) {
    (value as unknown[]).forEach((item, i) => errors.push(...validate(schema.items as JsonSchema, item, `${at}[${i}]`)));
  }
  return errors;
}
