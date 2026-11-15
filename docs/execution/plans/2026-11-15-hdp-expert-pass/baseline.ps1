# HDP expert-pass baseline (task row 0; implementation-plan.md §Verification Plan 1).
# Re-fetches the upstream a73d6df HDP and expert-pass skill and proves the plan constants equal them
# (EP upstream); proves Session 85's anchors (EP anchors, S1); records baseline.sha, the dirty tree
# with a sha256 per path and byte copies of the nine modified files (EP baseline); checks the
# compiled registry is current with five classes; installs from the lock; captures the base Python
# suite; runs the plan-local selftests. The base Python suite's own failures are recorded, not
# fatal: the session gate excuses only the ids this receipt shows failing. Every other step is
# fail-fast. Run from the repository root.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-hdp-expert-pass'
$receipts = 'C:/Temp/av-kit/s86'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = 'C:\Temp\av-kit\s86\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1. Upstream: the exact blob bytes, written by Python so no shell re-encodes them.
$fetch = @'
import hashlib, subprocess, sys
for spec, out in zip(sys.argv[1::2], sys.argv[2::2]):
    data = subprocess.run(["git", "-C", "P:/agentic-framework", "show", spec], capture_output=True, check=True).stdout
    open(out, "wb").write(data)
    print("fetched", spec, "bytes", len(data), "sha256", hashlib.sha256(data).hexdigest())
'@
Set-Content -Path "$receipts/fetch-upstream.py" -Value $fetch -Encoding utf8
Invoke-Step 'upstream-fetch' @('uv', 'run', 'python', "$receipts/fetch-upstream.py",
    'a73d6df:core/.agent/docs/human-decision-protocol.md', "$receipts/upstream-hdp-a73d6df.md",
    'a73d6df:core/.agent/skills/expert-pass/SKILL.md', "$receipts/upstream-expert-pass-SKILL.md")
Invoke-Step 'ep-upstream' @('uv', 'run', 'python', "$plan/ep-check.py", 'upstream', '--hdp', "$receipts/upstream-hdp-a73d6df.md", '--skill', "$receipts/upstream-expert-pass-SKILL.md")

# 2. Session 85's anchors (S1 on any problem), then the baseline record.
Invoke-Step 'ep-anchors' @('uv', 'run', 'python', "$plan/ep-check.py", 'anchors')
Invoke-Step 'ep-baseline' @('uv', 'run', 'python', "$plan/ep-check.py", 'baseline')
Write-Output ("baseline.sha {0}" -f (Get-Content "$plan/baseline.sha"))
Write-Output ("baseline-dirty.txt {0} paths" -f (Get-Content "$plan/baseline-dirty.txt").Count)

# 3. The compiled registry is current, with the five existing classes.
Invoke-Step 'check-compiled' @('uv', 'run', 'python', 'P:/.agent/tools/resolve_model.py', 'validate', '--overlay', '.agent/model-registry.local.yaml', '--check-compiled')
$classes = @'
import json, sys
c = sorted(json.load(open(".agent/model-registry.local.json", encoding="utf-8"))["classes"])
print("compiled classes", len(c), c)
sys.exit(0 if len(c) == 5 and "avkit_peer_reviewer" not in c else 14)
'@
Set-Content -Path "$receipts/compiled-classes.py" -Value $classes -Encoding utf8
Invoke-Step 'compiled-five-classes' @('uv', 'run', 'python', "$receipts/compiled-classes.py")

# 4. Install from the lock; the base Python suite with TMP and TEMP outside the user profile.
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/s86-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s86-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s86-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
$env:TMP = $userTmp
$env:TEMP = $userTemp

# 5. The plan-local checkers (red-check.py and identity.py, copied from
# 2026-11-14-review-limits-no-token-budget with this plan's PLAN and PROJECT_ARTIFACTS).
Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'ep-selftest' @('uv', 'run', 'python', "$plan/ep-check.py", 'selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
