export const DESTRUCTIVE_ACTIONS = new Set([
  "avkit_download.remove",
  "avkit_download.clear",
  "avkit_transcript.remove",
  "avkit_tts.cancel",
  "avkit_convert.remove",
  "avkit_convert.clear",
  "avkit_capture.remove",
  "avkit_capture.flatten",
  "avkit_capture.revert",
]);

/** Destructive actions that delete or overwrite user files: the user must also accept in the IDE. */
export const USER_CONFIRM_ACTIONS = new Set([
  "avkit_capture.remove",
  "avkit_capture.flatten",
  "avkit_capture.revert",
]);

/** How long the person has to answer the IDE prompt; expiry is a refusal (cancel). */
export const USER_CONFIRM_TIMEOUT_MS = 120_000;

/**
 * A decline or cancel faster than this came from the client, not a person: no one reads and answers
 * a prompt in a quarter second. The VS Code extension auto-declines in about 1 ms (A-11).
 */
export const USER_CONFIRM_AUTODECLINE_MS = 250;

export type UserConfirmOutcome = "accept" | "decline" | "cancel" | "unsupported";

export type UserConfirmRequest = { tool: string; action: string; id: string; message: string };

/** Only the validated id is interpolated; no agent-supplied free text reaches the prompt. */
const USER_CONFIRM_MESSAGES: Record<string, (id: string) => string> = {
  "avkit_capture.remove": (id) =>
    `An AI agent asks to delete capture ${id} and its files (image, annotated copy, saved marks) from disk. Allow?`,
  "avkit_capture.flatten": (id) =>
    `An AI agent asks to bake the saved marks into capture ${id}'s image file (a backup is kept when backups are on; a JPEG/WebP shot gets a new PNG copy instead). Allow?`,
  "avkit_capture.revert": (id) => `An AI agent asks to overwrite capture ${id}'s image with its newest backup. Allow?`,
};

export function needsUserConfirm(tool: string, action: string): boolean {
  return USER_CONFIRM_ACTIONS.has(`${tool}.${action}`);
}

export function userConfirmMessage(tool: string, action: string, id: string): string {
  const build = USER_CONFIRM_MESSAGES[`${tool}.${action}`];
  if (!build) throw new Error(`${tool}.${action} is not a USER_CONFIRM action`);
  return build(id);
}

export const NON_DESTRUCTIVE_STOPS = new Set([
  "avkit_download.cancel",
  "avkit_download.stop",
  "avkit_transcript.stop",
  "avkit_convert.cancel",
]);

export function isDestructive(tool: string, action: string): boolean {
  return DESTRUCTIVE_ACTIONS.has(`${tool}.${action}`);
}

export function confirmMissing(tool: string, action: string, args: Record<string, unknown>): boolean {
  return isDestructive(tool, action) && args.confirm !== true;
}
