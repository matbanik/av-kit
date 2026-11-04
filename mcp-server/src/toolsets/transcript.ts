import { z } from "zod";

function desc(action: string, method: string, path: string): string {
  return [
    `Workflow: call avkit_transcript ${action} to ${method} ${path}; add → start → get.`,
    `Prerequisite: channel URL and backend; rate limits from avkit_settings.`,
    `Returns: JSON from ${method} ${path} with paths and counts, never transcript body text.`,
    `Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.`,
  ].join(" ");
}

export const transcriptDescriptions: Record<string, string> = {
  "avkit_transcript.add": desc("add", "POST", "/transcripts"),
  "avkit_transcript.list": desc("list", "GET", "/transcripts"),
  "avkit_transcript.get": desc("get", "GET", "/transcripts/{id}"),
  "avkit_transcript.start": desc("start", "POST", "/transcripts/start"),
  "avkit_transcript.pause": desc("pause", "POST", "/transcripts/pause"),
  "avkit_transcript.resume": desc("resume", "POST", "/transcripts/resume"),
  "avkit_transcript.stop": desc("stop", "POST", "/transcripts/stop"),
  "avkit_transcript.requeue": desc("requeue", "POST", "/transcripts/{id}/requeue"),
  "avkit_transcript.retry": desc("retry", "POST", "/transcripts/{id}/retry"),
  "avkit_transcript.reorder": desc("reorder", "PUT", "/transcripts/reorder"),
  "avkit_transcript.remove": desc("remove", "DELETE", "/transcripts/{id}"),
  "avkit_transcript.compile": desc("compile", "POST", "/transcripts/{id}/compile"),
};

function withDesc<T extends z.ZodTypeAny>(action: string, schema: T): T {
  return schema.describe(transcriptDescriptions[`avkit_transcript.${action}`]) as T;
}

export const transcriptSchema = z.discriminatedUnion("action", [
  withDesc("add", z.object({ action: z.literal("add"), channel_url: z.string().min(1) }).strict()),
  withDesc("list", z.object({ action: z.literal("list") }).strict()),
  withDesc("get", z.object({ action: z.literal("get"), id: z.string().min(1) }).strict()),
  withDesc("start", z.object({ action: z.literal("start") }).strict()),
  withDesc("pause", z.object({ action: z.literal("pause") }).strict()),
  withDesc("resume", z.object({ action: z.literal("resume") }).strict()),
  withDesc("stop", z.object({ action: z.literal("stop") }).strict()),
  withDesc("requeue", z.object({ action: z.literal("requeue"), id: z.string().min(1) }).strict()),
  withDesc("retry", z.object({ action: z.literal("retry"), id: z.string().min(1) }).strict()),
  withDesc("reorder", z.object({ action: z.literal("reorder"), job_ids: z.array(z.string().min(1)) }).strict()),
  withDesc("remove", z.object({ action: z.literal("remove"), id: z.string().min(1), confirm: z.literal(true) }).strict()),
  withDesc("compile", z.object({ action: z.literal("compile"), id: z.string().min(1) }).strict()),
]);
