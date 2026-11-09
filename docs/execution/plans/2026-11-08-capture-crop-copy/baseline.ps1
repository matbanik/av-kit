# Session 59 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves that D-499 is ruled (S12), that Session 58 has closed and rc.2's Session 57 has
# closed (S8), and that Session 58's shapes this plan calls are present by name (S11). Then
# records HEAD and the dirty tree with each dirty path's SHA-256, records every Files Modified
# target's line endings and SHA-256 in s59-anchors.txt, installs Python from the lock without
# the network, proves ui/ and mcp-server/node_modules match their locks, asserts the pinned
# FFmpeg pair and Pillow, captures the base Python, UI and MCP suites, and runs the plan-local
# selftests. A copy of Session 58's with the queue checks changed and the S11, S12 and anchor
# steps added. The base suites' own failures are recorded, not fatal: the session gate excuses
# only the ids these receipts show failing. Every other step is fail-fast. Run from the
# repository root.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-08): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
#
# -QueueWaived: only when Mat has said in words to run before Session 57 closes. It waives only
# the MEU-125 check: Session 58 must have closed whatever Mat says, because this plan calls its
# code. The row's receipt then shows the waiver, and the handoff quotes Mat's message.
param([switch]$QueueWaived)
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-08-capture-crop-copy'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s59\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# S12: row 4b's tests depend on D-499, so an unruled D-499 stops here. A ruling is a
# "**Mat's ruling" line under the D-499 heading of human-gate-decision.md.
$ruling = @'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
m = re.search(r"^## D-499\b.*?(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
lines = [ln for ln in (m.group(0).splitlines() if m else []) if ln.startswith("**Mat's ruling")]
print("D-499 section found:", bool(m))
for ln in lines:
    print(ln)
if not lines:
    print("D-499 is unruled (S12); row 4b can't be written without the ruling")
sys.exit(0 if lines else 1)
'@
Invoke-Step 'd499-ruled' @('uv', 'run', '--no-sync', 'python', '-c', $ruling, "$plan/human-gate-decision.md")

# S8: Session 58 has closed (MEU-128 and MEU-129 approved, none of its paths left in the tree)
# and Session 57 has closed (MEU-125 approved), unless Mat waived the MEU-125 check.
$queue = @'
import pathlib, subprocess, sys
lines = pathlib.Path(".agent/context/meu-status.yaml").read_text(encoding="utf-8").splitlines()
def status(meu):
    for n, line in enumerate(lines):
        if line.strip() == f"id: {meu}":
            for follow in lines[n + 1 : n + 40]:
                if follow.strip().startswith("status:"):
                    return follow.split(":", 1)[1].strip().strip("'\"")
            return None
    return None
s128, s129, s125 = status("MEU-128"), status("MEU-129"), status("MEU-125")
print(f"session 58: MEU-128 {s128}, MEU-129 {s129}")
print(f"session 57 (MEU-125 release-rc2) status: {s125}")
porcelain = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], capture_output=True, check=True).stdout.decode("utf-8").splitlines()
# Session 58's Files Modified and its own closeout files
# (docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md §Files Modified).
session58 = {
    "packages/core/src/avkit_core/domain/capture.py",
    "packages/core/src/avkit_core/domain/enums.py",
    "packages/core/src/avkit_core/ports/capture.py",
    "packages/core/src/avkit_core/services/capture.py",
    "packages/infrastructure/src/avkit_infra/capture/adapter.py",
    "packages/api/src/avkit_api/routes/captures.py",
    "packages/api/src/avkit_api/schemas/captures.py",
    "openapi.committed.json",
    "mcp-server/src/toolsets/capture.ts",
    "mcp-server/src/toolsets/registry.ts",
    "mcp-server/src/client.ts",
    "tests/unit/test_domain_capture.py",
    "tests/unit/test_domain.py",
    "tests/unit/test_capture_adapter.py",
    "tests/e2e/test_api_captures.py",
    "tests/e2e/test_api_capture_region_import.py",
    "mcp-server/tests/capture.test.ts",
    "mcp-server/tests/client.test.ts",
    "docs/build-plan/09-screenshot-capture.md",
    "docs/build-plan/00-overview.md",
    "docs/build-plan/05-mcp-server.md",
}
prefixes = (
    "docs/execution/plans/2026-11-08-capture-region-import/",
    ".agent/context/handoffs/2026-11-08-capture-region-import-",
    "docs/execution/reflections/2026-11-08-capture-region-import-",
)
left = [line for line in porcelain if line[3:] in session58 or line[3:].startswith(prefixes)]
for line in left:
    print(f"session 58 path still in the tree: {line}")
waived = len(sys.argv) > 1 and sys.argv[1] == "waived"
if waived and s125 != "approved":
    print("queue check for session 57 waived by Mat; quote the message in the handoff")
ok = s128 == "approved" and s129 == "approved" and not left and (s125 == "approved" or waived)
sys.exit(0 if ok else 1)
'@
$queueArg = if ($QueueWaived) { 'waived' } else { 'strict' }
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue, $queueArg)

# S11: the Session 58 names this plan calls, by name. A shape that differs from Session 58's
# plan in signature or message is found when row 1 re-reads its anchors.
$shapes = @'
import pathlib, re, sys
checks = (
    ("packages/core/src/avkit_core/domain/capture.py", r"^def resolve_region\(", "resolve_region"),
    ("packages/core/src/avkit_core/domain/enums.py", r"^\s+Import = \"Import\"", "CaptureSource.Import"),
    ("packages/infrastructure/src/avkit_infra/capture/adapter.py", r"^\s+def view\(", "CaptureAdapter.view"),
    ("packages/infrastructure/src/avkit_infra/capture/adapter.py", r"ConflictError", "ConflictError in the adapter"),
    ("packages/core/src/avkit_core/services/capture.py", r"\.avkit-tmp", "the .avkit-tmp suffix"),
)
missing = []
for rel, pattern, label in checks:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if re.search(pattern, ln)]
    print(f"{label}: {rel} lines {hits[:5]}")
    if not hits:
        missing.append(label)
print("session 58 shapes missing (S11):", missing)
sys.exit(1 if missing else 0)
'@
Invoke-Step 'session58-shapes' @('uv', 'run', '--no-sync', 'python', '-c', $shapes)

$head = (git rev-parse HEAD).Trim()
Set-Content -Path "$plan/baseline.sha" -Value $head -NoNewline
# Each line is the porcelain line, a tab, then the path's SHA-256 (`deleted` when it is gone).
# The session gate reads the path as the text between column 3 and the tab.
$dirty = @'
import hashlib, pathlib, subprocess, sys
out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], capture_output=True, check=True).stdout.decode("utf-8")
lines = []
for line in out.splitlines():
    path = pathlib.Path(line[3:])
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "deleted"
    lines.append(f"{line}\t{digest}")
pathlib.Path(sys.argv[1]).write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
print(f"baseline-dirty.txt {len(lines)} paths")
'@
Invoke-Step 'baseline-dirty' @('uv', 'run', '--no-sync', 'python', '-c', $dirty, "$plan/baseline-dirty.txt")
Write-Output "baseline.sha $head"

# Every Files Modified target's line endings and SHA-256, which each row reads before it writes.
# A new file is recorded as absent; an existing target that is missing stops here.
$anchors = @'
import hashlib, pathlib, sys
targets = (
    "packages/core/src/avkit_core/domain/capture.py",
    "packages/core/src/avkit_core/domain/enums.py",
    "packages/core/src/avkit_core/ports/capture.py",
    "packages/core/src/avkit_core/services/capture.py",
    "packages/infrastructure/src/avkit_infra/capture/adapter.py",
    "packages/api/src/avkit_api/routes/captures.py",
    "packages/api/src/avkit_api/schemas/captures.py",
    "openapi.committed.json",
    "mcp-server/src/toolsets/capture.ts",
    "mcp-server/src/toolsets/registry.ts",
    "mcp-server/scripts/audit/plan.ts",
    "tools/capture_bake_fixture.py",
    "ui/tests/e2e/fixtures/capture-region-pass.json",
    "tests/unit/test_domain_capture.py",
    "tests/unit/test_domain.py",
    "tests/unit/test_capture_service.py",
    "tests/unit/test_capture_adapter.py",
    "tests/e2e/test_api_openapi.py",
    "tests/e2e/test_api_bodies.py",
    "tests/e2e/test_api_downloads.py",
    "tests/e2e/test_api_captures.py",
    "mcp-server/tests/capture.test.ts",
    "mcp-server/tests/action-index.test.ts",
    "mcp-server/tests/convert.test.ts",
    "mcp-server/tests/m7-resource.test.ts",
    "mcp-server/tests/audit/coverage.test.ts",
    "mcp-server/tests/audit/runner-fake-backend.test.ts",
    "ui/tests/unit/capture-region-pass.test.ts",
    "docs/build-plan/09-screenshot-capture.md",
    "docs/build-plan/00-overview.md",
    "docs/build-plan/05-mcp-server.md",
    ".agent/context/meu-status.yaml",
    ".agent/context/known-issues.yaml",
    ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md",
)
new = ("tests/e2e/test_api_capture_crop.py",)
out, missing = [], []
for rel in targets:
    p = pathlib.Path(rel)
    if not p.is_file():
        missing.append(rel)
        continue
    data = p.read_bytes()
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    kind = "CRLF" if crlf and not lf else "LF" if lf and not crlf else f"MIXED crlf={crlf} lf={lf}"
    out.append(f"{hashlib.sha256(data).hexdigest()} {len(data):>9} {kind:<6} {rel}")
for rel in new:
    out.append(f"{'present' if pathlib.Path(rel).exists() else 'absent'} new {rel}")
pathlib.Path(sys.argv[1]).write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
print("missing targets:", missing)
sys.exit(1 if missing else 0)
'@
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', '-c', $anchors, "$receipts/s59-anchors.txt")

# --offline: this step can't fetch a package.
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--offline', '--all-packages')

$lockSync = @'
import json, pathlib, sys
pkg = sys.argv[1]
lock = json.loads(pathlib.Path(pkg, "package-lock.json").read_text(encoding="utf-8"))["packages"]
want = {k: v.get("version") for k, v in lock.items() if k.startswith("node_modules/") and not v.get("optional")}
missing = sorted(k for k in want if not pathlib.Path(pkg, k, "package.json").exists())
have = {k: json.loads(pathlib.Path(pkg, k, "package.json").read_text(encoding="utf-8")).get("version") for k in want if k not in missing}
bad = sorted(k for k in have if have[k] != want[k])
for k in bad[:20]: print("version differs", k, want[k], have[k])
for k in missing[:20]: print("missing", k)
print(f"{pkg} lock sync: {len(want)} locked packages, {len(bad)} differ, {len(missing)} missing")
sys.exit(1 if bad or missing else 0)
'@
Invoke-Step 'ui-lock-sync' @('uv', 'run', 'python', '-c', $lockSync, 'ui')
Invoke-Step 'mcp-lock-sync' @('uv', 'run', 'python', '-c', $lockSync, 'mcp-server')

# The full Python suite runs Session 54's real-FFmpeg module; a missing or truncated binary is
# Stop Condition S4, not a fetch.
foreach ($name in @('ffmpeg.exe', 'ffprobe.exe')) {
    $exe = Join-Path $root "packaging/ffmpeg-win64/$name"
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
        Write-Output "baseline step ffmpeg-pair exit=1 ($name is missing; S4)"
        exit 1
    }
    $size = (Get-Item -LiteralPath $exe).Length
    if ($size -le 1024) {
        Write-Output ("baseline step ffmpeg-pair exit=1 ({0} is {1} B; S4)" -f $name, $size)
        exit 1
    }
    $first = (& $exe -version | Select-Object -First 1)
    Write-Output ("{0} {1} B: {2}" -f $name, $size, $first)
}
Write-Output 'baseline step ffmpeg-pair exit=0'

# D-481 and D-482 rest on Pillow 13.0.0's crop and PNG save, and Session 58's view on its
# MAX_IMAGE_PIXELS (89,478,485 at plan time, s59-plan-probes.txt); another version is S4.
$pillow = @'
import sys
import PIL
from PIL import Image
print(f"pillow {PIL.__version__} MAX_IMAGE_PIXELS {Image.MAX_IMAGE_PIXELS}")
sys.exit(0 if PIL.__version__ == "13.0.0" and Image.MAX_IMAGE_PIXELS == 89478485 else 1)
'@
Invoke-Step 'pillow-version' @('uv', 'run', 'python', '-c', $pillow)

& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/s59-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s59-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s59-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test *> "$receipts/s59-base-ui.txt"
Write-Output ("base suite ui exit={0} receipt={1}/s59-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s59-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run test *> "$receipts/s59-base-mcp.txt"
Write-Output ("base suite mcp exit={0} receipt={1}/s59-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s59-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
