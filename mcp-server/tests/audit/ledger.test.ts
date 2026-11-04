import { describe, expect, it } from "vitest";
import { CleanupLedger, evaluateCleanup } from "../../scripts/audit/ledger.js";

const ZERO = { downloads: 0, transcripts: 0, conversions: 0, captures: 0, capture_requests: 0 };
const SETTINGS = { ui: { theme: "dark" }, tts: { voice: "am_eric" } };

function clean(ledger: CleanupLedger) {
  return evaluateCleanup({
    ledger,
    counts: ZERO,
    settingsNow: structuredClone(SETTINGS),
    settingsSnapshot: SETTINGS,
    backendExited: true,
    rootRemoved: true,
    keep: false,
  });
}

describe("AC-68.9 cleanup ledger", () => {
  it("AC-68.9 entities registered and removed leave nothing outstanding", () => {
    const ledger = new CleanupLedger();
    ledger.register("download", "d1");
    ledger.register("capture", "s1");
    ledger.remove("download", "d1");
    ledger.remove("capture", "s1");
    expect(ledger.outstanding()).toEqual([]);
    expect(clean(ledger)).toEqual({ ok: true, residuals: [], backend_exited: true, root_removed: true });
  });

  it("AC-68.9 an unremoved job is a named residual and cleanup fails", () => {
    const ledger = new CleanupLedger();
    ledger.register("download", "d1");
    const out = clean(ledger);
    expect(out.ok).toBe(false);
    expect(out.residuals).toEqual(["ledger download d1"]);
  });

  it("AC-68.9 a non-zero REST count is a residual even when the ledger is empty", () => {
    const out = evaluateCleanup({
      ledger: new CleanupLedger(),
      counts: { ...ZERO, conversions: 2 },
      settingsNow: SETTINGS,
      settingsSnapshot: SETTINGS,
      backendExited: true,
      rootRemoved: true,
      keep: false,
    });
    expect(out.ok).toBe(false);
    expect(out.residuals).toEqual(["rest conversions=2"]);
  });

  it("AC-68.9 a settings value not restored to the snapshot is a residual", () => {
    const out = evaluateCleanup({
      ledger: new CleanupLedger(),
      counts: ZERO,
      settingsNow: { ...SETTINGS, ui: { theme: "light" } },
      settingsSnapshot: SETTINGS,
      backendExited: true,
      rootRemoved: true,
      keep: false,
    });
    expect(out.ok).toBe(false);
    expect(out.residuals).toEqual(["settings ui.theme"]);
  });

  it("AC-68.9 a backend that did not exit fails cleanup", () => {
    const out = evaluateCleanup({
      ledger: new CleanupLedger(),
      counts: ZERO,
      settingsNow: SETTINGS,
      settingsSnapshot: SETTINGS,
      backendExited: false,
      rootRemoved: true,
      keep: false,
    });
    expect(out.ok).toBe(false);
    expect(out.residuals).toEqual(["backend process still running"]);
  });

  it("AC-68.9 a kept root is allowed only with --keep", () => {
    const base = {
      ledger: new CleanupLedger(),
      counts: ZERO,
      settingsNow: SETTINGS,
      settingsSnapshot: SETTINGS,
      backendExited: true,
      rootRemoved: false,
    };
    expect(evaluateCleanup({ ...base, keep: true }).ok).toBe(true);
    expect(evaluateCleanup({ ...base, keep: false }).residuals).toEqual(["isolated root not removed"]);
  });
});
