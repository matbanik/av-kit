# WINDOWS_GATE for 2026-10-01-mcp-live-audit (Session 28, MEU-68): the authoritative MCP live audit.
# It is human-run by Mat; see human-gate-decision.md (H-4) and implementation-plan.md §Verification Plan 7.
# Run from P:/av-kit on the pushed commit named in the request:
#   git pull origin claude/sweet-goodall-mu69td
#   pwsh -NoProfile -File docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.ps1 -Check windows-gate -QuietMachineConfirmed
#   (optional) add -PackagedServer "<install dir>/resources/mcp-server/index.js" for the non-blocking D-6 probe
# Stage order is shared with validate-task.sh STAGES_WINDOWS. Every stage runs through `rtk proxy`
# and the script stops at the first blocking failure (later stages are not_run). mcp-audit may exit 1
# (findings recorded, AUTHORITATIVE_ACCEPTANCE decides); 2/3/4 are runner refusals/errors and fail.
# Then commit and push only the result files listed in $returnFiles:
#   git add <those paths>
#   git commit -m "docs(execution): record Session 28 Windows gate (attempt N)"
#   git push origin claude/sweet-goodall-mu69td
param(
    [Parameter(Mandatory = $true)][string]$Check,
    [switch]$QuietMachineConfirmed,
    [string]$PackagedServer = ''
)
$ErrorActionPreference = 'Stop'
# Native exit codes are read explicitly from $LASTEXITCODE; never let pwsh 7.4+ turn them into throws.
$PSNativeCommandUseErrorActionPreference = $false
$rd = 'C:/Temp/av-kit'
New-Item -ItemType Directory -Force -Path $rd | Out-Null
$plan = 'docs/execution/plans/2026-10-01-mcp-live-audit'
$baselinePath = '.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json'
$reportPath = '.agent/context/MCP/mcp-tool-audit-report.md'
$auditOut = "$rd/s28-audit"
$returnFiles = @("$plan/windows-gate-result.json", "$plan/windows-gate-baseline.json", "$plan/mcp-audit-summary.json", $baselinePath, $reportPath)

if ($Check -ne 'windows-gate') { throw "Unknown check: $Check" }

# Receipts from an earlier attempt must never be reported as this run's (cloud-local §3.2).
Get-ChildItem -Path $rd -Filter 's28-win-*' -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse
Remove-Item -LiteralPath $auditOut -Recurse -Force -ErrorAction SilentlyContinue

$exempt = ($returnFiles | ForEach-Object { [regex]::Escape($_) }) -join '|'
$result = [ordered]@{
    schema              = 's28-windows-gate.v1'
    tested_commit       = (git rev-parse HEAD).Trim()
    # Leftover result files from an earlier attempt are not a dirty tree.
    clean_tree          = [string]::IsNullOrWhiteSpace((git status --porcelain | Where-Object { $_ -notmatch $exempt } | Out-String))
    mcp_lockfile_sha256 = (Get-FileHash mcp-server/package-lock.json -Algorithm SHA256).Hash
    uv_lock_sha256      = (Get-FileHash uv.lock -Algorithm SHA256).Hash
    node                = (node --version).Trim()
    uv                  = ((uv --version) | Out-String).Trim()
    started             = (Get-Date).ToString('o')
    preflight           = $null
    stages              = @()
    mcp_tests           = $null
    audit               = $null
    packaged_probe      = $null
}
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_OUT_DIR -ErrorAction SilentlyContinue

function Invoke-Stage([string]$Id, [string[]]$Argv) {
    $receipt = "$rd/s28-win-$Id.txt"
    & rtk proxy @Argv *> $receipt
    $code = $LASTEXITCODE
    $script:result.stages += [ordered]@{ id = $Id; argv = ($Argv -join ' '); exit = $code; receipt = $receipt }
    Get-Content $receipt -Tail 15 | Write-Host
    return $code
}

# --- preflight (Session 26 RULE-2; cloud-local §3.2) ---
$busy = @(Get-Process -Name electron, playwright -ErrorAction SilentlyContinue | ForEach-Object { "$($_.Name):$($_.Id)" })
$rtk = ''
try { $rtk = ((rtk --version) | Out-String).Trim() } catch { $rtk = '' }
$afHead = ''
if (Test-Path 'P:/agentic-framework/.git') { $afHead = (git -C P:/agentic-framework rev-parse HEAD).Trim() }
$regHash = ''
if (Test-Path 'P:/.agent/model-registry.json') { $regHash = (Get-FileHash 'P:/.agent/model-registry.json' -Algorithm SHA256).Hash }
$result.preflight = [ordered]@{
    quiet_machine          = ([bool]$QuietMachineConfirmed -and $busy.Count -eq 0)
    quiet_machine_attested = [bool]$QuietMachineConfirmed
    busy_processes         = $busy
    rtk                    = $rtk
    agentic_framework_head = $afHead
    agent_registry_sha256  = $regHash
}
$pfExit = $(if ($result.preflight.quiet_machine -and $rtk -and $result.clean_tree) { 0 } else { 1 })
$result.stages += [ordered]@{ id = 'preflight'; argv = 'quiet machine + rtk + clean tree'; exit = $pfExit; receipt = '' }

$tjson = "$rd/s28-win-mcp-tests.json"
# npm --prefix runs scripts with cwd mcp-server/, so runner paths must be absolute.
$repo = (Resolve-Path .).Path -replace '\\', '/'
$stages = @(
    @('mcp-npm-ci', @('npm', '--prefix', 'mcp-server', 'ci')),
    @('uv-sync',    @('uv', 'sync', '--frozen', '--all-packages')),
    @('mcp-types',  @('npm', '--prefix', 'mcp-server', 'run', 'typecheck')),
    # The MCP suite and the audit both need the built dist (M4).
    @('mcp-build',  @('npm', '--prefix', 'mcp-server', 'run', 'build')),
    @('mcp-tests',  @('npm', '--prefix', 'mcp-server', 'run', 'test', '--', '--reporter=json', "--outputFile=$tjson")),
    @('mcp-audit',  @('npm', '--prefix', 'mcp-server', 'run', 'audit', '--', '--mode', 'authoritative', '--no-baseline', '--update-baseline',
                      '--baseline', "$repo/$baselinePath", '--report', "$repo/$reportPath",
                      '--out', $auditOut, '--agent', 'local-windows-gate'))
)
$failed = ($pfExit -ne 0)
if (-not $failed) {
    foreach ($s in $stages) {
        $code = Invoke-Stage $s[0] $s[1]
        if ($s[0] -eq 'mcp-audit') {
            $result.stages[-1].note = 'exit 1 = findings recorded (allowed); 2/3/4 = runner refused or errored'
            if ($code -notin 0, 1) { $failed = $true; break }
        } elseif ($code -ne 0) { $failed = $true; break }
    }
}
$ran = @($result.stages | ForEach-Object { $_.id })
if ($ran -contains 'mcp-tests' -and (Test-Path $tjson)) {
    $t = Get-Content $tjson -Raw | ConvertFrom-Json
    $result.mcp_tests = [ordered]@{ passed = $t.numPassedTests; failed = $t.numFailedTests; total = $t.numTotalTests }
}
if ($ran -contains 'mcp-tests' -and $null -eq $result.mcp_tests) { Write-Host 'FAIL: mcp-tests ran but produced no Vitest JSON'; $failed = $true }
if ($ran -contains 'mcp-audit') {
    $summary = "$auditOut/mcp-audit-summary.json"
    if ((Test-Path $summary) -and (Test-Path $baselinePath)) {
        Copy-Item $summary "$plan/mcp-audit-summary.json" -Force
        Copy-Item $baselinePath "$plan/windows-gate-baseline.json" -Force
        $s = Get-Content $summary -Raw | ConvertFrom-Json
        $result.audit = [ordered]@{ mode = $s.mode; steps = @($s.steps).Count; cleanup_ok = $s.cleanup.ok; summary_sha256 = (Get-FileHash $summary -Algorithm SHA256).Hash }
    } else { Write-Host 'FAIL: mcp-audit produced no summary or baseline'; $failed = $true }
}
# Optional D-6 probe: never blocking, recorded for MCP-PACKAGED-ENTRY-UNREACHABLE verification only.
if (-not $failed -and $PackagedServer) {
    $code = Invoke-Stage 'packaged-probe' @('npm', '--prefix', 'mcp-server', 'run', 'audit', '--', '--mode', 'authoritative', '--discovery-only',
        '--no-baseline', '--server', $PackagedServer, '--out', "$rd/s28-win-packaged-probe", '--agent', 'local-windows-gate')
    $result.stages[-1].note = 'non-blocking D-6 probe of the installed MCP server'
    $result.packaged_probe = [ordered]@{ server = $PackagedServer; exit = $code }
}
$result.finished = (Get-Date).ToString('o')
$out = Join-Path $plan 'windows-gate-result.json'
$result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
Get-Content $out
if ($failed) { Write-Error 'WINDOWS_GATE failed; preserve C:/Temp/av-kit/s28-win-* and s28-audit to C:/Temp/av-kit/keep/<sha>-attempt<N>/ before any rerun'; exit 1 }
'PASS WINDOWS_GATE (cloud runs validate-task.sh windows-gate-check)'
'Return files: ' + ($returnFiles -join ', ')
exit 0
