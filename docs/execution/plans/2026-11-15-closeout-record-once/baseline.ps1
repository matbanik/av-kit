# Closeout-record-once baseline (task row 0; implementation-plan.md §Verification Plan 1).
# Records HEAD, the dirty tree and the content hashes of this session's files; checks that the
# validator and the two test files equal HEAD; keeps a copy of the base validator; records the
# selftest's arms under a temp folder outside the home folder, and the selftest's result under
# the default temp (the known issue: 5 failures at plan time); installs from the lock; captures
# the base Python suite; checks the known-issues render; runs the plan-local selftests, the
# stage-log survey and the old-reflections check on the base validator.
# The base Python suite's own failures and the default-temp selftest are recorded, not fatal.
# Every other step is fail-fast. Run from the repository root.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-closeout-record-once'
$receipts = 'C:/Temp/av-kit/cro'
$validator = 'tools/validate_closeout_artifacts.py'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = "$receipts/tmp"
New-Item -ItemType Directory -Force -Path $tmp, "$receipts/base" | Out-Null

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
Write-Output ("baseline-dirty.txt {0} paths" -f (Get-Content "$plan/baseline-dirty.txt").Count)

# Content binding (S4). The validator and the two test files must equal HEAD (CRLF read as LF,
# since the blobs are LF and the work tree CRLF); known-issues.yaml and known-issues.md belong to
# the uncommitted triage workstream too, so only their hashes are recorded. Row 7 passes the
# recorded known-issues.yaml hash to issue-resolve.py --expect-sha256. Every baseline-dirty.txt
# path is hashed into baseline-dirty-content.txt too (added after plan review R1, Q8), so the
# gate's scope-paths step can show each one kept its row 0 content (S4), not only its status.
$contentCheck = @'
import hashlib, pathlib, subprocess, sys
head_bound = sys.argv[4:7]
recorded = sys.argv[7:]
lines, bad = [], []
dirty = []
for entry in pathlib.Path(sys.argv[3]).read_text(encoding="utf-8-sig").splitlines():
    if len(entry) < 4:
        continue
    rel = entry[3:].split(" -> ")[-1].strip().strip('"')
    path = pathlib.Path(rel)
    dirty.append(f"{rel} sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}" if path.is_file() else f"{rel} absent")
pathlib.Path(sys.argv[2]).write_text("\n".join(dirty) + "\n", encoding="utf-8", newline="\n")
print(f"baseline-dirty-content.txt {len(dirty)} path(s)")
for rel in head_bound + recorded:
    work = pathlib.Path(rel).read_bytes()
    crlf = work.count(b"\r\n")
    bare = work.count(b"\n") - crlf
    lines.append(f"{rel} sha256 {hashlib.sha256(work).hexdigest()} crlf {crlf} bare-lf {bare}")
    if rel in head_bound:
        blob = subprocess.run(["git", "show", "HEAD:" + rel], capture_output=True, check=True).stdout
        if work.replace(b"\r\n", b"\n") != blob.replace(b"\r\n", b"\n"):
            bad.append(rel)
pathlib.Path(sys.argv[1]).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
print("\n".join(lines))
print("differ from HEAD:", bad)
sys.exit(10 if bad else 0)
'@
Set-Content -Path "$receipts/content-check.py" -Value $contentCheck -Encoding utf8
Invoke-Step 'content-binding' @('uv', 'run', 'python', "$receipts/content-check.py", "$plan/baseline-content.txt",
    "$plan/baseline-dirty-content.txt", "$plan/baseline-dirty.txt",
    $validator, 'tests/tooling/test_closeout_register_grammar.py', 'tests/tooling/test_framework_adoption.py',
    '.agent/context/known-issues.yaml', '.agent/context/known-issues.md')

Copy-Item -Path $validator -Destination "$receipts/base/validate_closeout_artifacts.py" -Force
Write-Output "base validator copied to $receipts/base/validate_closeout_artifacts.py"

# The selftest under a temp folder with no .agent above it: the arm baseline (219 at plan time).
$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run python $validator --selftest *> "$receipts/cro-base-selftest.txt"
$code = $LASTEXITCODE
Get-Content "$receipts/cro-base-selftest.txt" -Tail 2
Write-Output "baseline step selftest exit=$code"
if ($code -ne 0) { exit $code }
Invoke-Step 'arms-before' @('uv', 'run', 'python', "$plan/selftest-arms-check.py", '--write-before', "$plan/selftest-arms-before.txt", "$receipts/cro-base-selftest.txt")
$arms = (Get-Content "$plan/selftest-arms-before.txt").Count
Write-Output "selftest-arms-before.txt $arms arm(s)"
if ($arms -ne 219) { Write-Output 'expected 219 arms, the plan-time count'; exit 11 }

# The selftest under the user's own temp: the known issue. Recorded, not fatal (5 failures at plan time).
$env:TMP = $userTmp
$env:TEMP = $userTemp
& rtk proxy uv run python $validator --selftest *> "$receipts/cro-base-selftest-default-tmp.txt"
Write-Output ("baseline step selftest-default-tmp exit={0} (recorded; the known issue)" -f $LASTEXITCODE)
Get-Content "$receipts/cro-base-selftest-default-tmp.txt" -Tail 1

Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')

$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/cro-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/cro-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/cro-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
$env:TMP = $userTmp
$env:TEMP = $userTemp

# known-issues.md must already match the register; a failure here is another session's drift (S8).
Invoke-Step 'issues-render-check' @('uv', 'run', 'python', 'tools/issue_triage.py', 'render', '--check')

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'arms-check-selftest' @('uv', 'run', 'python', "$plan/selftest-arms-check.py", '--selftest')
Invoke-Step 'survey-selftest' @('uv', 'run', 'python', "$plan/stage-log-survey.py", '--selftest', '--validator', "$receipts/base/validate_closeout_artifacts.py")
Invoke-Step 'reflections-check-selftest' @('uv', 'run', 'python', "$plan/reflections-check.py", '--selftest')
Invoke-Step 'survey-base' @('uv', 'run', 'python', "$plan/stage-log-survey.py", '--validator', "$receipts/base/validate_closeout_artifacts.py", '--out', "$receipts/cro-base-survey.txt")
Invoke-Step 'reflections-base' @('uv', 'run', 'python', "$plan/reflections-check.py", '--before', "$receipts/base/validate_closeout_artifacts.py", '--after', "$receipts/base/validate_closeout_artifacts.py", '--out', "$receipts/cro-base-reflections.txt")
Write-Output 'baseline: all steps exit 0'
exit 0
