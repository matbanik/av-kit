# Human gate decision — authoritative D6 gate location

## Direct user authorization

Source: `USER_EXPLICIT` (Claude Code web session, 2026-09-28), answering the tooling check that asked how to handle two environment-bound Vitest failures in the Linux container.

Exact user message:

> (c) Run the final gate on your Windows machine

The option text presented to the user, which this answer selects:

> **(c) Run the final gate on your Windows machine.** Everything else runs here; H1-2 would be marked blocked until you run it.

## Evidence that prompted the decision

These results come from a pre-execution tooling check in the Claude Code cloud container, on the untouched baseline at commit `f7d3134`:

- **Vitest**: 595 passed, 2 failed.
- **AC-51.6** (`ui/tests/unit/layout-primitives.test.ts:189`) expects `819760B9…`, the SHA-256 of the `test-ids.ts` prefix in a CRLF checkout. `.gitattributes` has `* text=auto`, so the Linux checkout is LF and hashes to `DCABD0F9…`. Recomputing the prefix hash with CRLF line endings reproduces `819760B9…` exactly.
- **AC-41.3** (`ui/tests/unit/queue-canon.test.ts`) reads `P:/zorivest/ui/src/renderer/src/globals.css`, a path on the Windows `P:` drive that does not exist in the container.
- **Electron E2E** works under `xvfb-run` once `ELECTRON_DISABLE_SANDBOX=1` is set (the container runs as root). Of the 12 baseline Transcript/TTS cases, 11 passed on the first run. TTS W2-4 failed once and then passed alone. Its likely cause is a settings-hydration race, which AC-56.4 / RULE-2 addresses.
- **Electron binary**: the `npm ci` postinstall download of Electron 42.9.3 aborted through the container proxy (an undici assertion). curl fetched the same release asset, whose SHA-256 matched the package's `checksums.json` (`46fc1cd5…`). It was unpacked the way `install.js` does.

## What this decision authorizes

- **`WINDOWS_GATE`**: the authoritative PROFILE D6 fresh full gate (UI typecheck, lint, full Vitest, build, full real-Electron E2E and the source audit) runs on Mat's Windows machine via `validate-task.ps1 -Check windows-gate`. It tolerates zero failures. The execution review (H1-7) is dispatched only after its result validates against the code under review.
- **Container pre-gate**: the container runs the same stages as a non-authoritative pre-gate (H1-2) and in targeted green runs. There, only the two `ENV_BOUND_TESTS` may fail, and only with their proven environment signatures. The failures are recorded, never skipped or edited, and every other failure fails the run.
- **Push**: pushing the branch `claude/amazing-albattani-qcl51p` is what lets Mat pull the commit to test. That push, and Mat's commit of `windows-gate-result.json`, are part of this decision.
- **Turn boundary**: H1-6 is a planned turn boundary. The run stops, waits for Mat, and resumes when the result file is pushed.

This decision does not approve the plan or any implementation. It does not change the test files that contain AC-51.6 or AC-41.3. It does not authorize merge, release or deploy.
