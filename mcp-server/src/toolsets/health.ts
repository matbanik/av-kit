import { z } from "zod";

function desc(action: string, method: string, path: string): string {
  return [
    `Workflow: probe ${action} with ${method} ${path} before starting jobs.`,
    `Prerequisite: api_base known; liveness needs no token; dependencies need a token.`,
    `Returns: JSON from ${method} ${path} (versions/status, never logs dump).`,
    `Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.`,
  ].join(" ");
}

export const healthDescriptions: Record<string, string> = {
  "avkit_health.dependencies": desc("dependencies", "GET", "/health/dependencies"),
  "avkit_health.liveness": desc("liveness", "GET", "/health"),
};

function withDesc<T extends z.ZodTypeAny>(action: string, schema: T): T {
  return schema.describe(healthDescriptions[`avkit_health.${action}`]) as T;
}

export const healthSchema = z.discriminatedUnion("action", [
  withDesc("dependencies", z.object({ action: z.literal("dependencies") }).strict()),
  withDesc("liveness", z.object({ action: z.literal("liveness") }).strict()),
]);
