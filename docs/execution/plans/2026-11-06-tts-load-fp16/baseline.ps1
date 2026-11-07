# Session 52 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# Records HEAD and the dirty tree, snapshots the real models folder (MODELS_SNAPSHOT), installs
# Python from the lock, proves ui/ and mcp-server/node_modules match their locks, captures the base
# Python, UI and MCP suites, runs Session 51's DEV_CHECK strictly, checks the smoke and spike
# inputs, and runs the plan-local selftests. The base suites' own failures are recorded, not
# fatal: the session gate excuses only the ids these receipts show failing. Every other step is
# fail-fast. Run from the repository root.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-07): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-06-tts-load-fp16'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s52\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

$head = (git rev-parse HEAD).Trim()
Set-Content -Path "$plan/baseline.sha" -Value $head -NoNewline
git status --porcelain --untracked-files=all | Set-Content -Path "$plan/baseline-dirty.txt"
Write-Output "baseline.sha $head"
Write-Output ("baseline-dirty.txt {0} paths" -f @(Get-Content "$plan/baseline-dirty.txt").Count)

# `--record` refuses to overwrite, so a re-run compares against the first snapshot instead (S4).
if (Test-Path "$plan/models-before.json") {
    Invoke-Step 'models-compare' @('uv', 'run', 'python', "$plan/models-snapshot.py", '--compare', "$plan/models-before.json")
} else {
    Invoke-Step 'models-record' @('uv', 'run', 'python', "$plan/models-snapshot.py", '--record', "$plan/models-before.json")
}
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')

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

& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/s52-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s52-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s52-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test *> "$receipts/s52-base-ui.txt"
Write-Output ("base suite ui exit={0} receipt={1}/s52-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s52-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run test *> "$receipts/s52-base-mcp.txt"
Write-Output ("base suite mcp exit={0} receipt={1}/s52-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s52-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

# Session 51's DEV_CHECK, unchanged and strict, before any change; a failure is S9.
& rtk proxy uv run python docs/execution/plans/2026-11-06-tts-build-capability/dev-pytorch-check.py *> "$receipts/s52-base-dev.txt"
$code = $LASTEXITCODE
Get-Content "$receipts/s52-base-dev.txt" -Tail 25
Write-Output ("baseline step dev-pytorch exit={0}" -f $code)
if ($code -ne 0) { Write-Output 'S9: the dev path fails before any change'; exit $code }

# The smoke and spike inputs; a mismatch is S10. Reads only: nothing here writes the models folder.
$assets = @'
import hashlib, pathlib, sys
def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
smoke = pathlib.Path("C:/Temp/av-kit/s32-smoke-models")
pinned = pathlib.Path("C:/Temp/av-kit/tts-compare/pinned/onnx")
real_fp16 = pathlib.Path.home() / ".avkit" / "models" / "kokoro-v1.0-onnx" / "onnx" / "model_fp16.onnx"
problems = []
for rel in ["config.json", "spacy", *(f"kokoro-v1.0-onnx/voices/{v}.bin" for v in ("af_heart", "am_michael", "af_bella", "bf_emma")), "kokoro-v1.0-onnx/onnx/model_quantized.onnx"]:
    present = (smoke / rel).exists()
    print(f"{'present' if present else 'MISSING'} {smoke / rel}")
    if not present:
        problems.append(f"missing {rel}")
quantized = smoke / "kokoro-v1.0-onnx/onnx/model_quantized.onnx"
if quantized.exists():
    a, b = sha(quantized), sha(pinned / "model_quantized.onnx")
    print(f"model_quantized.onnx smoke {a} pinned {b}")
    if a != b:
        problems.append("model_quantized.onnx differs from the pinned file")
size = real_fp16.stat().st_size
fp16 = sha(real_fp16)
print(f"real model_fp16.onnx bytes {size} sha256 {fp16}")
if size != 163234740 or not fp16.startswith("ba4527a874b42b21"):
    problems.append("the real model_fp16.onnx is not the 2026-11-04 file")
fp32 = sha(pinned / "model.onnx")
print(f"pinned model.onnx sha256 {fp32}")
if not fp32.startswith("8fbea51ea711f2af"):
    problems.append("the pinned model.onnx is not the 2026-11-04 file")
for p in problems:
    print("S10:", p)
print(f"assets: {len(problems)} problems")
sys.exit(1 if problems else 0)
'@
& rtk proxy uv run python -c $assets *> "$receipts/s52-base-assets.txt"
$code = $LASTEXITCODE
Get-Content "$receipts/s52-base-assets.txt"
Write-Output ("baseline step assets exit={0}" -f $code)
if ($code -ne 0) { Write-Output 'S10: a smoke or spike input differs'; exit $code }

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'models-snapshot-selftest' @('uv', 'run', 'python', "$plan/models-snapshot.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
