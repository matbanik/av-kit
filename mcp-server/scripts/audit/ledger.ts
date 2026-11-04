/**
 * Cleanup ledger and CLEANUP_PREDICATE (plan §Single-statement contracts; Zorivest §Cleanup
 * Contract). Every entity the audit creates is registered when created and marked removed when
 * a removal is observed; whatever is left is a residual finding.
 */
import { isDeepStrictEqual } from "node:util";
import type { CleanupRecord } from "./types.js";

export type EntityKind = "download" | "transcript" | "conversion" | "capture" | "capture_request" | "tts_job";

export class CleanupLedger {
  private readonly open = new Map<string, { kind: EntityKind; id: string }>();

  /** Records an entity the audit created. */
  register(kind: EntityKind, id: string): void {
    this.open.set(`${kind}:${id}`, { kind, id });
  }

  /** Marks an entity as removed (observed gone through REST). */
  remove(kind: EntityKind, id: string): void {
    this.open.delete(`${kind}:${id}`);
  }

  /** Entities registered and not yet removed, in creation order. */
  outstanding(): { kind: EntityKind; id: string }[] {
    return [...this.open.values()];
  }
}

function settingsDiff(
  now: Record<string, Record<string, unknown>>,
  snapshot: Record<string, Record<string, unknown>>,
): string[] {
  const diffs: string[] = [];
  const namespaces = new Set([...Object.keys(now), ...Object.keys(snapshot)]);
  for (const ns of [...namespaces].sort()) {
    const keys = new Set([...Object.keys(now[ns] ?? {}), ...Object.keys(snapshot[ns] ?? {})]);
    for (const key of [...keys].sort()) {
      if (!isDeepStrictEqual(now[ns]?.[key], snapshot[ns]?.[key])) diffs.push(`settings ${ns}.${key}`);
    }
  }
  return diffs;
}

/**
 * CLEANUP_PREDICATE: no ledger residual, every REST count zero, settings equal the post-guard
 * snapshot, the backend exited, and the isolated root removed unless `--keep`.
 */
export function evaluateCleanup(input: {
  ledger: CleanupLedger;
  counts: Record<string, number>;
  settingsNow: Record<string, Record<string, unknown>>;
  settingsSnapshot: Record<string, Record<string, unknown>>;
  backendExited: boolean;
  rootRemoved: boolean;
  keep: boolean;
}): CleanupRecord {
  const residuals: string[] = [];
  for (const entity of input.ledger.outstanding()) residuals.push(`ledger ${entity.kind} ${entity.id}`);
  for (const [name, count] of Object.entries(input.counts)) {
    if (count !== 0) residuals.push(`rest ${name}=${count}`);
  }
  residuals.push(...settingsDiff(input.settingsNow, input.settingsSnapshot));
  if (!input.backendExited) residuals.push("backend process still running");
  if (!input.rootRemoved && !input.keep) residuals.push("isolated root not removed");
  return {
    ok: residuals.length === 0,
    residuals,
    backend_exited: input.backendExited,
    root_removed: input.rootRemoved,
  };
}
