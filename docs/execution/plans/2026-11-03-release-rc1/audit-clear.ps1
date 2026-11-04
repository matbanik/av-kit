# Session 44: clear the live audit's output before it runs (implementation-plan.md §Verification Plan 5, D-186).
# A crashed Node process also exits 1 and run.ts reuses folders, so audit-rule.py must never read an
# earlier run's summary. A held file survives Remove-Item, and on ErrorActionPreference Continue the
# script carries on, so this is its own gate step: exit 0 only when the folder is gone. Any other
# result makes the gate's fail-fast skip the audit and the rule. It refuses a folder outside C:/Temp/av-kit.
#
# -Selftest proves that with a held file, then against a copy of session-gate.ps1 cut down to the
# clear and audit steps, with a child that exits 1 in place of the audit. The copy runs the gate's
# real step loop. Exit 0 = cleared (or every case passed), 1 = not cleared (or a case failed).
param([string]$Dir, [switch]$Selftest)
$ErrorActionPreference = 'Stop'
$scratch = 'C:\Temp\av-kit\'

function Get-ClearProblem([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    if (-not $full.StartsWith($scratch, [StringComparison]::OrdinalIgnoreCase)) { return "$full is outside $scratch" }
    if (Test-Path -LiteralPath $full) { Remove-Item -LiteralPath $full -Recurse -Force -ErrorAction SilentlyContinue -ErrorVariable held }
    if (Test-Path -LiteralPath $full) { return "$full could not be cleared: $($held | Select-Object -First 1)" }
    return $null
}

if (-not $Selftest) {
    if (-not $Dir) { Write-Output 'give -Dir or -Selftest'; exit 1 }
    $problem = Get-ClearProblem $Dir
    if ($problem) { Write-Output "audit-clear refuses: $problem"; exit 1 }
    Write-Output "audit-clear: $Dir is clear"
    exit 0
}

$script:failures = 0
$script:total = 0
function Test-Case([string]$Name, [bool]$Ok, [string]$Detail) {
    $script:total++
    if (-not $Ok) { $script:failures++ }
    Write-Output ("{0} {1} -> {2}" -f $(if ($Ok) { 'PASS' } else { 'FAIL' }), $Name, $Detail)
}
function Copy-Replacing([string]$Text, [string]$Old, [string]$New) {
    $count = ([regex]::Matches($Text, [regex]::Escape($Old))).Count
    if ($count -ne 1) { throw "the gate no longer holds this text exactly once: $Old" }
    return $Text.Replace($Old, $New)
}

$probe = Join-Path $scratch 's44-audit-clear-probe'
$out = Join-Path $probe 'D6-mcp-audit'
$summary = Join-Path $out 'mcp-audit-summary.json'
$copy = Join-Path $probe 'gate-copy.ps1'
function New-StaleSummary {
    New-Item -ItemType Directory -Path $out -Force | Out-Null
    # An empty summary: the rule refuses it without any YouTube traffic if a defect ever reaches it.
    Set-Content -LiteralPath $summary -Value '{}'
}

Test-Case 'a folder outside the receipts is refused' ([bool](Get-ClearProblem 'C:/Temp/s44-audit-clear-outside')) 'nothing is deleted'
if (Test-Path -LiteralPath $probe) {
    $leftover = Get-ClearProblem $probe
    if ($leftover) { throw $leftover }
}
$problem = Get-ClearProblem $out
Test-Case 'an absent folder is clear' (-not $problem) "$problem"

New-StaleSummary
$problem = Get-ClearProblem $out
Test-Case 'an old summary is removed' ((-not $problem) -and -not (Test-Path -LiteralPath $summary)) "$problem"

New-StaleSummary
$gate = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'session-gate.ps1') -Raw
$gate = Copy-Replacing $gate "`$receipts = 'C:/Temp/av-kit'" "`$receipts = '$($probe -replace '\\', '/')'"
$gate = Copy-Replacing $gate 'function Get-TestedState([string]$Receipt) {' @'
$steps = @($steps | Where-Object { $_.Id -in @('mcp-audit-clear', 'mcp-audit') })
$steps[1].Argv = @('node', '-e', 'process.exit(1)')
function Get-TestedState([string]$Receipt) {
'@
Set-Content -LiteralPath $copy -Value $gate
function Invoke-GateCopy {
    Push-Location $PSScriptRoot
    try {
        $lines = @(& pwsh -NoProfile -File $copy 2>&1 | ForEach-Object { "$_" })
        return [pscustomobject]@{ Code = $LASTEXITCODE; Text = ($lines -join "`n") }
    } finally {
        Pop-Location
    }
}

$hold = [IO.File]::Open($summary, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
try {
    $problem = Get-ClearProblem $out
    Test-Case 'a held summary is not clear' ([bool]$problem -and (Test-Path -LiteralPath $summary)) "$problem"
    $run = Invoke-GateCopy
    $stopped = $run.Text -match '(?m)^mcp-audit-clear stage=runtime exit=1 ' -and $run.Text -match '(?m)^mcp-audit stage=runtime not_run '
    Test-Case 'a held summary stops the gate before the audit' ($stopped -and $run.Code -ne 0) "gate exit=$($run.Code)"
    Test-Case 'a held summary never reaches the rule' ($run.Text -notmatch 'audit rule') 'no rule output'
} finally {
    $hold.Dispose()
}

$run = Invoke-GateCopy
$reachedChild = $run.Text -match '(?m)^mcp-audit-clear stage=runtime exit=0 ' -and $run.Text -match '(?m)^mcp-audit stage=runtime exit=1 '
Test-Case 'once released, the old summary is gone before the child exits 1' $reachedChild "gate exit=$($run.Code)"
$unreadable = $run.Text -match 'mcp-audit audit rule: exit=2 '
Test-Case 'a crash with no summary is not tolerated' ($unreadable -and $run.Code -eq 1) "gate exit=$($run.Code)"

$leftover = Get-ClearProblem $probe
if ($leftover) { Write-Output "could not remove the probe folder: $leftover" }
Write-Output ("audit-clear selftest: {0} of {1} passed" -f ($script:total - $script:failures), $script:total)
exit $(if ($script:failures -or $leftover) { 1 } else { 0 })
