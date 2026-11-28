// AC-174.18's negative (Session 106, INSTALL_STAGE_RULES): the install stage's precondition
// function refuses, with 0 installer calls and 0 changes, when the E2E account already holds any
// av-kit trace, and passes on a clean account. A fake file system and a fake registry reader
// stand in for the host; the helper is loaded by a dynamic import inside each test, so before
// Green every case fails by assertion.
import { createHash } from "node:crypto";

import { describe, expect, it } from "vitest";

const HELPER = "../e2e-install/install-helper";
const NAMESPACE = "50e065bc-3134-11e6-9bab-38c9862bdaf3";
const APP_ID = "com.avkit.app";
const PORT = 47911;

const PATHS = {
  localAppData: "C:\\Users\\e2e\\AppData\\Local",
  appData: "C:\\Users\\e2e\\AppData\\Roaming",
  desktop: "C:\\Users\\e2e\\Desktop",
  programs:
    "C:\\Users\\e2e\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs",
  root: "C:\\avkit-e2e",
};
const RUN_KEY = "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run";
const APPROVED_KEY =
  "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run";

interface Trace {
  paths?: string[];
  values?: Array<[string, string]>;
  keys?: string[];
  uninstall?: string[];
  portTaken?: boolean;
}

function fakeAccount(trace: Trace = {}) {
  const calls = { installer: 0, changes: 0 };
  const paths = new Set((trace.paths ?? []).map((p) => p.toLowerCase()));
  const values = new Set(
    (trace.values ?? []).map(([k, n]) => `${k}|${n}`.toLowerCase()),
  );
  const keys = new Set((trace.keys ?? []).map((k) => k.toLowerCase()));
  const host = {
    exists: (p: string) => paths.has(p.toLowerCase()),
    regValueExists: (key: string, name: string) =>
      values.has(`${key}|${name}`.toLowerCase()),
    regKeyExists: (key: string) => keys.has(key.toLowerCase()),
    uninstallEntries: () => [...(trace.uninstall ?? [])],
    portTaken: async () => trace.portTaken === true,
    runInstaller: async () => {
      calls.installer += 1;
      return 0;
    },
    write: () => {
      calls.changes += 1;
    },
    remove: () => {
      calls.changes += 1;
    },
  };
  return { host, calls };
}

function uuidV5(namespace: string, name: string): string {
  const ns = Buffer.from(namespace.replace(/-/g, ""), "hex");
  const h = createHash("sha1")
    .update(ns)
    .update(Buffer.from(name, "utf8"))
    .digest();
  const b = Buffer.from(h.subarray(0, 16));
  b[6] = (b[6] & 0x0f) | 0x50;
  b[8] = (b[8] & 0x3f) | 0x80;
  const x = b.toString("hex");
  return `${x.slice(0, 8)}-${x.slice(8, 12)}-${x.slice(12, 16)}-${x.slice(16, 20)}-${x.slice(20)}`;
}

async function loadHelper() {
  // Before Green the module is absent: an empty record makes the check below fail by assertion.
  const mod = (await import(HELPER).catch(() => ({}))) as Record<
    string,
    unknown
  >;
  expect(
    typeof mod.checkPreconditions,
    "install-helper exports checkPreconditions",
  ).toBe("function");
  return mod as {
    checkPreconditions: (
      host: ReturnType<typeof fakeAccount>["host"],
      paths: typeof PATHS,
      opts: { port: number },
    ) => Promise<{ ok: boolean; reason?: string; detail?: string }>;
    APP_GUID: string;
  };
}

const FOLDERS = [
  `${PATHS.localAppData}\\Programs\\av-kit`,
  `${PATHS.localAppData}\\av-kit`,
  `${PATHS.appData}\\av-kit`,
  `${PATHS.appData}\\av-kit-ui`,
  `${PATHS.localAppData}\\av-kit-ui-updater`,
];

const CASES: Array<[string, Trace, string]> = [
  ...FOLDERS.map((f): [string, Trace, string] => [
    `the folder ${f}`,
    { paths: [f] },
    "install-folder-exists",
  ]),
  [
    "an uninstall entry",
    { uninstall: ["av-kit 0.1.0-rc.5"] },
    "uninstall-entry-exists",
  ],
  ["a taken feed port", { portTaken: true }, "feed-port-taken"],
  [
    "the HKCU Run value",
    { values: [[RUN_KEY, APP_ID]] },
    "sign-in-value-exists",
  ],
  [
    "the StartupApproved\\Run value",
    { values: [[APPROVED_KEY, APP_ID]] },
    "sign-in-value-exists",
  ],
  [
    "the Desktop shortcut",
    { paths: [`${PATHS.desktop}\\av-kit.lnk`] },
    "shortcut-exists",
  ],
  [
    "the Start Menu shortcut",
    { paths: [`${PATHS.programs}\\av-kit.lnk`] },
    "shortcut-exists",
  ],
  [
    "the installer's key",
    { keys: [`HKCU\\Software\\${uuidV5(NAMESPACE, APP_ID)}`] },
    "installer-key-exists",
  ],
  [
    "an owner record",
    { paths: [`${PATHS.root}\\install-owner.json`] },
    "install-quarantined",
  ],
];

describe("install-stage preconditions", () => {
  for (const [what, trace, reason] of CASES) {
    it(`AC-174.18 refuses ${what} with ${reason}, no installer call and no change`, async () => {
      const helper = await loadHelper();
      const { host, calls } = fakeAccount(trace);
      const got = await helper.checkPreconditions(host, PATHS, { port: PORT });
      expect(got.ok).toBe(false);
      expect(got.reason).toBe(reason);
      expect(calls).toEqual({ installer: 0, changes: 0 });
    });
  }

  it("AC-174.18 passes on a clean account with no installer call and no change", async () => {
    const helper = await loadHelper();
    const { host, calls } = fakeAccount();
    const got = await helper.checkPreconditions(host, PATHS, { port: PORT });
    expect(got).toEqual({ ok: true });
    expect(calls).toEqual({ installer: 0, changes: 0 });
  });

  it("AC-174.18 APP_GUID is com.avkit.app's UUID v5 in electron-builder's namespace", async () => {
    const helper = await loadHelper();
    expect(uuidV5(NAMESPACE, APP_ID)).toBe(
      "c21620fd-8854-5989-9a80-a73c80a17704",
    );
    expect(helper.APP_GUID).toBe("c21620fd-8854-5989-9a80-a73c80a17704");
  });
});
