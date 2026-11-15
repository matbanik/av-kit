# Session 73 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# Session 52's shape (docs/execution/plans/2026-11-06-tts-load-fp16/baseline.ps1), with this plan's
# steps. Checks the plan gate's words and the queue, records HEAD and the dirty tree with each dirty
# path's SHA-256, records the endings and hashes of the files row 10 edits, checks the cached model
# and build inputs offline by hash (no read of ~/.avkit), installs Python from the lock offline,
# captures the base Python suite and runs the plan-local selftests. Row 0b, not this script, makes
# the download and the installed-file read that Mat ruled for (Amendment 1). The base suite's own failures
# are recorded, not fatal: the session gate excuses only the ids its receipt shows failing. Every
# other step is fail-fast. Run from the repository root with PowerShell 7.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-14-tts-fp16-phase-guard'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s73\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$py = @('uv', 'run', '--offline', '--no-sync', 'python')

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1. Rulings (S9) and queue (S8).
$rulings = @'
import pathlib, re, sys
plan = pathlib.Path("docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md")
status = [l for l in plan.read_text(encoding="utf-8").splitlines() if l.startswith("> **Status:**")]
ok = len(status) == 1 and "USER_EXPLICIT" in status[0] and re.search(r"execute", status[0], re.I)
print("status lines:", len(status), "execute words with USER_EXPLICIT:", bool(ok))
sys.exit(0 if ok else 1)
'@
Invoke-Step 'rulings' ($py + @('-c', $rulings))

$queue = @'
import subprocess, sys
import yaml
rows = {r["id"]: r for r in yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))["meus"]}
want = {"MEU-121": "approved", "MEU-127": "pending"}
have = {k: rows.get(k, {}).get("status") for k in want}
anc = subprocess.run(["git", "merge-base", "--is-ancestor", "58d028e", "HEAD"]).returncode == 0
print("queue", have, "58d028e ancestor of HEAD:", anc)
sys.exit(0 if have == want and anc else 1)
'@
Invoke-Step 'queue' ($py + @('-c', $queue))

# 2. Records: HEAD, the dirty tree with hashes, and the endings and hashes of row 10's targets.
$head = (git rev-parse HEAD).Trim()
Set-Content -Path "$plan/baseline.sha" -Value $head -NoNewline
$records = @'
import hashlib, pathlib, subprocess, sys
plan = pathlib.Path("docs/execution/plans/2026-11-14-tts-fp16-phase-guard")
never_open = "docs/proposals/2026-11-10-download-logic-divergence-report.md"
raw = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "-z"], capture_output=True, check=True).stdout.decode("utf-8")
lines = []
for entry in (e for e in raw.split("\0") if e):
    path = entry[3:]
    p = pathlib.Path(path)
    digest = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "absent"
    lines.append(f"{entry[:2]} {path}  sha256={digest}")
(plan / "baseline-dirty.txt").write_text("".join(l + "\n" for l in lines), encoding="utf-8", newline="")
print("baseline-dirty.txt", len(lines), "paths")
targets = ["docs/build-plan/03-service-layer.md", ".agent/context/meu-status.yaml", ".agent/context/known-issues.yaml", ".agent/context/known-issues.md", ".agent/context/meu-registry.md", "docs/BUILD_PLAN.md", never_open]
out = []
for t in targets:
    data = pathlib.Path(t).read_bytes()
    crlf = data.count(b"\r\n")
    endings = "hash only (never opened)" if t == never_open else f"crlf={crlf} lf={data.count(b'\n') - crlf} lone_cr={data.count(b'\r') - crlf}"
    out.append(f"{t} sha256={hashlib.sha256(data).hexdigest()} {endings}")
text = pathlib.Path("docs/build-plan/03-service-layer.md").read_text(encoding="utf-8")
anchor = '<a id="tts-fp16-phase-guard-residual"></a>' in text and "> **MEU-127.**" in text
out.append(f"03 anchor and MEU-127 note present: {anchor}")
pathlib.Path("C:/Temp/av-kit/s73-anchors.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
sys.exit(0 if anchor else 1)
'@
Invoke-Step 'records' ($py + @('-c', $records))

# 3. Inputs (S10): the cached copies and the offline wheels, by hash. Nothing under ~/.avkit is read.
$inputs = @'
import hashlib, pathlib, sys
def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
models = pathlib.Path("C:/Temp/av-kit/s52/smoke-models")
expect = {
    models / "kokoro-v1.0-onnx/onnx/model_fp16.onnx": "ba4527a874b42b21e35f468c10d326fdff3c7fc8cac1f85e9eb6c0dfc35c334a",
    models / "kokoro-v1.0-onnx/onnx/model_quantized.onnx": "fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478",
}
problems = []
for path, want in expect.items():
    have = sha(path) if path.is_file() else "absent"
    print(path, have)
    if have != want:
        problems.append(f"{path.name} is not the expected file")
onnx_files = sorted(p.name for p in (models / "kokoro-v1.0-onnx/onnx").glob("*.onnx"))
print("onnx files:", onnx_files)
if onnx_files != ["model_fp16.onnx", "model_quantized.onnx"]:
    problems.append("the cached onnx folder holds other files")
for rel in ["config.json", *(f"kokoro-v1.0-onnx/voices/{v}.bin" for v in ("af_heart", "am_michael", "af_bella", "bf_emma"))]:
    if not (models / rel).is_file():
        problems.append(f"missing {rel}")
for path in ("C:/Temp/av-kit/s52-spike-phonemes.json", "C:/Temp/av-kit/s52/e5-site/onnx/__init__.py"):
    if not pathlib.Path(path).is_file():
        problems.append(f"missing {path}")
sys.path.insert(0, "C:/Temp/av-kit/s52/e5-site")
import onnx, onnxruntime
print("onnx", onnx.__version__, onnx.__file__)
print("onnxruntime", onnxruntime.__version__)
if onnx.__version__ != "1.23.2" or onnxruntime.__version__ != "1.31.1":
    problems.append("onnx or onnxruntime is not the planned version")
for p in problems:
    print("S10:", p)
print(f"inputs: {len(problems)} problems")
sys.exit(1 if problems else 0)
'@
& rtk proxy @py -c $inputs *> "$receipts/s73-base-inputs.txt"
$code = $LASTEXITCODE
Get-Content "$receipts/s73-base-inputs.txt"
Write-Output ("baseline step inputs exit={0}" -f $code)
if ($code -ne 0) { Write-Output 'S10: a cached input differs'; exit $code }

# 4. Install from the lock, offline (S4).
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--offline', '--all-packages')

# 5. Base Python suite, recorded and not fatal.
& rtk proxy uv run --offline --no-sync pytest tests/ --tb=short -q -rfE *> "$receipts/s73-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s73-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s73-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

# 6. Selftests, each on its own fixtures (Session 56 RULE-4).
Invoke-Step 'phase-guard-selftest' ($py + @("$plan/phase-guard.py", 'selftest'))
Invoke-Step 'fresh-inputs-selftest' ($py + @("$plan/fresh-inputs.py", 'selftest'))
Invoke-Step 'identity-selftest' ($py + @("$plan/identity.py", '--selftest'))
Write-Output 'baseline: all steps exit 0'
exit 0
