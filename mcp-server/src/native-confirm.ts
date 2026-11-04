import { execFile } from "node:child_process";
import { USER_CONFIRM_TIMEOUT_MS, type UserConfirmOutcome } from "./destructive.js";

/** Starts the dialog process and resolves its exit code (`null` when it was killed); rejects if it cannot start. */
export type DialogRunner = (
  command: string,
  args: string[],
  options: { env: NodeJS.ProcessEnv; timeout: number },
) => Promise<number | null>;

/**
 * A topmost Yes/No box with No as the default button. The message comes from the environment, so
 * no text is ever spliced into the script. Exit 0 is Yes, 1 is No; any error exits 2, so a failure
 * is never reported as the person's No.
 */
const DIALOG_SCRIPT = [
  "$ErrorActionPreference = 'Stop'",
  "trap { exit 2 }",
  "Add-Type -AssemblyName System.Windows.Forms",
  "$owner = New-Object System.Windows.Forms.Form -Property @{ TopMost = $true }",
  "$answer = [System.Windows.Forms.MessageBox]::Show($owner, $env:AVKIT_CONFIRM_MESSAGE, 'av-kit', 'YesNo', 'Warning', 'Button2')",
  "$owner.Dispose()",
  "if ($answer -eq 'Yes') { exit 0 }",
  "if ($answer -eq 'No') { exit 1 }",
  "exit 2",
].join("\n");

const ENCODED_SCRIPT = Buffer.from(DIALOG_SCRIPT, "utf16le").toString("base64");

/** The execFile shape runDialog needs; injectable so its result mapping is tested (A-11 review F1). */
export type ExecFile = (
  command: string,
  args: string[],
  options: { env: NodeJS.ProcessEnv; timeout: number; windowsHide: boolean },
  callback: (err: unknown) => void,
) => unknown;

export function dialogRunner(exec: ExecFile = execFile): DialogRunner {
  return (command, args, options) =>
    new Promise((resolve, reject) => {
      exec(command, args, { ...options, windowsHide: true }, (err) => {
        if (err === null) {
          resolve(0);
          return;
        }
        const code = (err as NodeJS.ErrnoException).code;
        if (typeof code === "string") {
          reject(err);
          return;
        }
        resolve((err as { killed?: boolean }).killed ? null : (code ?? null));
      });
    });
}

const runDialog = dialogRunner();

/**
 * DIALOG_FALLBACK (A-11): asks the person with a native Windows dialog when the IDE cannot.
 * Yes → accept, No → decline, timeout or any other exit → cancel; "unsupported" when no dialog can be shown.
 */
export async function nativeConfirm(
  message: string,
  deps: { run?: DialogRunner; platform?: NodeJS.Platform } = {},
): Promise<UserConfirmOutcome> {
  if ((deps.platform ?? process.platform) !== "win32") {
    return "unsupported";
  }
  let exit: number | null;
  try {
    exit = await (deps.run ?? runDialog)(
      "powershell.exe",
      ["-NoProfile", "-NonInteractive", "-STA", "-EncodedCommand", ENCODED_SCRIPT],
      { env: { ...process.env, AVKIT_CONFIRM_MESSAGE: message }, timeout: USER_CONFIRM_TIMEOUT_MS },
    );
  } catch {
    return "unsupported";
  }
  if (exit === 0) return "accept";
  if (exit === 1) return "decline";
  return "cancel";
}
