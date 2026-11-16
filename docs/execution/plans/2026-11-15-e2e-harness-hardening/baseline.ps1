# E2E harness hardening baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-15-framework-small-syncs/baseline.ps1, with this plan's
# steps: 1. the tree state (baseline.sha, baseline-dirty.txt); 2. the path-scoped baseline
# (baseline-scope.json with every new path absent, baseline-dirty-hashes.json, the BASE copies in
# C:/Temp/av-kit/e2e-harness-hardening/base/), with the 20 launch-site files checked against the
# list this plan was written from (S1 when a site file is added or removed; the count inside them
# is recorded in baseline-sites.json, not fixed at 21), the sibling-shared anchors checked once
# each in the live text, and baseline-untouched.json, all bound to content, never to HEAD; 3. the
# Electron binary check; 4. the three builds the full Electron suite reads (out/, the isolated
# primitive harness in out-e2e/ and the region-picker stub); 5. the base Vitest suite; 6. the
# base full Electron suite with ELECTRON_RUN_AS_NODE unset (its passed count goes to
# base-e2e-count.txt); 7. the flag negative: launch.test.ts with ELECTRON_RUN_AS_NODE=1 must fail
# with "bad option" (AC-18's negative); 8. the seven plan-local selftests and mutation.py status. Every step is fail-fast.
# Electron processes that this script's own runs launched and left running are reported and
# stopped through owned-procs.ps1: recorded by pid and creation time in the run's own process
# tree, each child only when its parent was proven to hold the pid when it started, then intersected with this checkout's Electron binary and the script's start time. Mat's
# app and other sessions' apps keep running, even on this checkout's binary.
# Run from the repository root (P:/av-kit, main only).
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-e2e-harness-hardening'
$receipts = 'C:/Temp/av-kit/e2e-harness-hardening'
$env:ELECTRON_RUN_AS_NODE = $null
$env:DEBUG = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
$tmp = 'C:\Temp\av-kit\e2e-harness-hardening\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$started = Get-Date
$electronDist = (Join-Path $root 'ui\node_modules\electron\dist\').Replace('/', '\')
. (Join-Path $PSScriptRoot 'owned-procs.ps1')

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1-2. Tree state and the path-scoped baseline, in Python so every file is read and written as bytes.
$record = @'
import hashlib, json, pathlib, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-15-e2e-harness-hardening")
BASE = pathlib.Path("C:/Temp/av-kit/e2e-harness-hardening/base")
E2E = "ui/tests/e2e/"
SITES = (
    "backend-output-after-close.test.ts", "capture-filmstrip-actions.test.ts", "capture-import.test.ts",
    "capture-inbox.test.ts", "capture-picker.test.ts", "command-palette-nav.spec.ts",
    "console-chrome.test.ts", "console-panel.test.ts", "convert-queue.test.ts",
    "download-queue.test.ts", "help-search.spec.ts", "keyboard-shortcuts.test.ts",
    "launch.test.ts", "layout-primitives.test.ts", "mcp-setup-prompt.test.ts",
    "settings.test.ts", "startup-reveal.test.ts", "theme-probe.ts",
    "transcript-queue.test.ts", "tts-generate.test.ts",
)
EXISTING = tuple(E2E + s for s in SITES) + (
    "ui/tests/unit/layout-primitives.test.ts",
    "ui/tests/unit/capture-page.test.ts",
    "ui/tests/unit/capture-page.behavior.test.ts",
    "ui/vitest.config.ts",
    ".agent/context/known-issues.yaml",
    ".agent/context/known-issues.md",
    # Row 12 sets its §6 row 78 to executed; no other line.
    ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md",
    # Never edited: the mutant's target, bound so mutation.py status can prove the restore.
    "ui/src/renderer/src/features/capture/CapturePage.tsx",
)
NEW = (
    "ui/tests/e2e/electron-env.ts",
    "ui/tests/e2e/electron-app.ts",
    "ui/tests/e2e/main-error-watch.cjs",
    "ui/tests/e2e/electron-harness.test.ts",
    "ui/tests/e2e/fixtures/startup-throw-main.mjs",
    "ui/tests/unit/e2e-harness.test.ts",
    "ui/tests/unit/global-setup.ts",
    "ui/tests/unit/vitest-global-setup.test.ts",
)
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-15-e2e-harness-hardening-",
    "docs/execution/reflections/2026-11-15-e2e-harness-hardening-",
)
SHARED = ("docs/execution/metrics.md", ".agent/context/current-focus.md")
problems = []

def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout

def sha(path):
    p = pathlib.Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ("absent" if not p.exists() else "not-a-file")

def endings(data):
    crlf, lf = data.count(b"\r\n"), data.count(b"\n")
    return "CRLF" if lf and crlf == lf else ("LF" if crlf == 0 else f"mixed {crlf}/{lf}")

head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
(PLAN / "baseline-dirty.txt").write_bytes(porcelain.encode("utf-8"))
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
print("baseline-dirty.txt", len(dirty), "paths")

live_sites = sorted(p.name for p in pathlib.Path(E2E).iterdir() if p.is_file() and b"_electron.launch(" in p.read_bytes())
if tuple(live_sites) != tuple(sorted(SITES)):
    problems.append(f"S1: the launch-site files differ from the plan's 20: added {sorted(set(live_sites) - set(SITES))} removed {sorted(set(SITES) - set(live_sites))}")
# The site count binds to the row-0 content, not to HEAD or to the plan-time 21: an earlier session
# of the grouping (Session 75 appends AC-146.19 to capture-inbox.test.ts) may have left a site file
# changed and uncommitted. site-check.py derives every rule from the BASE copies, so a different
# count inside the 20 files is recorded, not a stop; a site in a file outside the 20 is S1 above.
per_file = {s: pathlib.Path(E2E + s).read_bytes().count(b"_electron.launch(") for s in SITES}
count = sum(per_file.values())
(PLAN / "baseline-sites.json").write_bytes((json.dumps(per_file, indent=2, sort_keys=True) + "\n").encode())
print("launch sites", count, "in", len(live_sites), "files", "(plan time: 21 in 20)" if count != 21 else "")
# The sections this plan relies on in files a sibling also edits, checked in the live text: each
# anchor must occur exactly once (S1 otherwise). They are compatible when they are present and
# unique; HEAD equality is not required.
ANCHORS = (
    ("ui/tests/unit/capture-page.test.ts", b"describe('MEU-97 capture hints (AC-97.4)', () => {"),
    ("ui/tests/unit/capture-page.test.ts", b"it('AC-97.4 HINTS capture-save passes its chord to ToolbarIconButton and capture-region carries its own', () => {"),
    ("ui/tests/unit/capture-page.behavior.test.ts", b"describe('MEU-39 capture GUI runtime (exec r1 F1 F2 F5)'"),
    ("ui/tests/unit/layout-primitives.test.ts", b"expect(e2e).toContain('_electron.launch')"),
    ("ui/vitest.config.ts", b"include: ['src/**/*.test.{ts,tsx}', 'tests/unit/**/*.test.{ts,tsx}'],"),
    ("ui/tests/e2e/theme-probe.ts", b"export async function launchWithAppData("),
)
for path, anchor in ANCHORS:
    n = pathlib.Path(path).read_bytes().count(anchor)
    print("anchor", path, n, anchor[:60].decode())
    if n != 1:
        problems.append(f"S1: {path} holds {n} copies of {anchor[:60].decode()!r}, the plan needs exactly 1")
if b"globalSetup" in pathlib.Path("ui/vitest.config.ts").read_bytes():
    problems.append("S1: ui/vitest.config.ts already has a globalSetup")

scope = {p: sha(p) for p in EXISTING + NEW}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"new path already exists: {p}")
for p in EXISTING:
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"existing path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent")

HEAD_PLANS = {n for n in git("ls-tree", "--name-only", "HEAD", "docs/execution/plans/").decode().splitlines() if n}

def other_plan(p):
    folder = "/".join(p.split("/")[:4])
    return p.startswith("docs/execution/plans/2026-11-15-") and folder != p and folder not in HEAD_PLANS

def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES) or other_plan(p)

hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in SHARED + tuple(p for p in EXISTING if p in dirty):
    print("dirty-at-row-0" if p in dirty else "clean at HEAD", p, sha(p))

for p in EXISTING:
    data = pathlib.Path(p).read_bytes()
    dest = BASE / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print("BASE", p, endings(data), "sha256", sha(dest))
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', 'python', "$receipts/baseline-record.py")
# The skip basis of the gate (openapi, py-*, mcp-*), bound to this content, never to HEAD.
Invoke-Step 'untouched-record' @('uv', 'run', 'python', "$plan/untouched-check.py", '--record')

# 3. The Electron binary this checkout launches (the install race's precondition, AC-13).
$binary = Join-Path $electronDist 'electron.exe'
if (-not (Test-Path $binary)) { Write-Output "baseline: $binary is missing; run node node_modules/electron/install.js in ui (S1)"; exit 1 }
Write-Output ("electron binary present {0}" -f $binary)

# 4. The builds the full Electron suite reads (the RC2 gate's harness and stub steps).
Invoke-Step 'ui-build' @('npm', '--prefix', 'ui', 'run', 'build')
$harnessBuild = "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$root/ui/out-e2e'; exit `$LASTEXITCODE"
Invoke-Step 'ui-harness-build' @('pwsh', '-NoProfile', '-Command', $harnessBuild)
Invoke-Step 'ui-picker-stub' @('npm', '--prefix', 'ui', 'run', 'build:picker-stub')

# 5. The base Vitest suite (pwsh, never the Bash tool: memory vitest-from-pwsh-not-bash). TMP and
# TEMP stay under C:/Temp/av-kit from here on, so every mkdtempSync(tmpdir()) app-data folder of
# the Electron runs lands there too.
$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy npm --prefix ui run test *> "$receipts/ehh-base-ui.txt"
$code = $LASTEXITCODE
Write-Output ("base ui exit={0} receipt={1}/ehh-base-ui.txt" -f $code, $receipts)
Get-Content "$receipts/ehh-base-ui.txt" | Select-String -Pattern '^\s+(Test Files|Tests)\s' | Select-Object -Last 2
if ($code -ne 0) { Write-Output 'baseline: the base Vitest suite fails; the gate excuses nothing (S1)'; exit $code }

# 6. The base full Electron suite, ELECTRON_RUN_AS_NODE unset.
$run = Invoke-OwnedRun -Argv @('npm', '--prefix', 'ui', 'run', 'test:e2e') -Receipt "$receipts/ehh-base-e2e.txt"
$code = $run.Code
Write-Output ("base e2e exit={0} receipt={1}/ehh-base-e2e.txt" -f $code, $receipts)
Get-Content "$receipts/ehh-base-e2e.txt" | Select-String -Pattern '^\s+\d+ (passed|failed|skipped|flaky|did not run)' | Select-Object -Last 6
Stop-OwnedElectron -Label 'base e2e' -Owned $run.Owned -Dist $electronDist -Started $started
if ($code -ne 0) { Write-Output 'baseline: the base Electron suite fails (S1; D-941 allows one whole repeat of this step only for a known MONITORING signature)'; exit $code }
$passed = Select-String -Path "$receipts/ehh-base-e2e.txt" -Pattern '^\s+(\d+) passed' | Select-Object -Last 1
if ($null -eq $passed) { Write-Output 'baseline: no passed count in the base e2e receipt'; exit 1 }
Set-Content -Path "$plan/base-e2e-count.txt" -Value $passed.Matches[0].Groups[1].Value -Encoding ascii
Write-Output ("base-e2e-count.txt {0}" -f $passed.Matches[0].Groups[1].Value)

# 7. The flag negative (AC-18): with ELECTRON_RUN_AS_NODE=1 the BASE launch dies with "bad option".
# DEBUG=pw:browser in the child only (D-1030): Playwright prints electron.exe's stderr only under it.
$flagLine = "`$env:ELECTRON_RUN_AS_NODE='1'; `$env:DEBUG='pw:browser'; npm --prefix ui run test:e2e -- tests/e2e/launch.test.ts; exit `$LASTEXITCODE"
$run = Invoke-OwnedRun -Argv @('pwsh', '-NoProfile', '-Command', $flagLine) -Receipt "$receipts/ehh-base-flag.txt"
$code = $run.Code
$env:ELECTRON_RUN_AS_NODE = $null
$env:DEBUG = $null
Write-Output ("base flag exit={0} receipt={1}/ehh-base-flag.txt" -f $code, $receipts)
Stop-OwnedElectron -Label 'base flag' -Owned $run.Owned -Dist $electronDist -Started $started
if ($code -eq 0 -or -not (Select-String -Path "$receipts/ehh-base-flag.txt" -Pattern 'bad option' -SimpleMatch -Quiet)) {
    Write-Output 'baseline: the BASE launch did not fail with "bad option" under ELECTRON_RUN_AS_NODE=1, so AC-18 has no negative (S1)'
    exit 1
}
# 8. The plan-local checkers (TMP and TEMP still under C:/Temp/av-kit, away from the home folder).
Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'mutation-selftest' @('uv', 'run', 'python', "$plan/mutation.py", '--selftest')
Invoke-Step 'mutation-status' @('uv', 'run', 'python', "$plan/mutation.py", 'status')
Invoke-Step 'site-check-selftest' @('uv', 'run', 'python', "$plan/site-check.py", '--selftest')
Invoke-Step 'untouched-selftest' @('uv', 'run', 'python', "$plan/untouched-check.py", '--selftest')
Invoke-Step 'owned-procs-selftest' @('pwsh', '-NoProfile', '-File', "$plan/owned-procs.ps1", '-Selftest')
Invoke-Step 'scope-check-selftest' @('uv', 'run', 'python', "$plan/scope-check.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
