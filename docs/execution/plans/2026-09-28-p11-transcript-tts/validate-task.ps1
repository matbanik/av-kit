# WINDOWS_GATE for 2026-09-28-p11-transcript-tts (human-run by Mat; see human-gate-decision.md).
# Run from P:/av-kit on the pushed commit under review:
#   git pull origin claude/amazing-albattani-qcl51p
#   pwsh -NoProfile -File docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.ps1 -Check windows-gate
# It runs the PROFILE D6 UI stages in order through `rtk proxy`, stops at the first failure
# (later stages are not_run), and writes windows-gate-result.json next to this script.
# Then commit and push only that file:
#   git add docs/execution/plans/2026-09-28-p11-transcript-tts/windows-gate-result.json
#   git commit -m "docs(execution): record Session 25 Windows gate"
#   git push origin claude/amazing-albattani-qcl51p
param([Parameter(Mandatory = $true)][string]$Check)
$ErrorActionPreference = 'Stop'
# Native exit codes are read explicitly from $LASTEXITCODE; never let pwsh 7.4+ turn them into throws.
$PSNativeCommandUseErrorActionPreference = $false
$rd = 'C:/Temp/av-kit'
New-Item -ItemType Directory -Force -Path $rd | Out-Null
$plan = 'docs/execution/plans/2026-09-28-p11-transcript-tts'

if ($Check -ne 'windows-gate') { throw "Unknown check: $Check" }

$result = [ordered]@{
    schema         = 's25-windows-gate.v1'
    tested_commit  = (git rev-parse HEAD).Trim()
    # A leftover result file from an earlier run is not a dirty tree.
    clean_tree     = [string]::IsNullOrWhiteSpace((git status --porcelain | Where-Object { $_ -notmatch 'windows-gate-result\.json' } | Out-String))
    lockfile_sha256 = (Get-FileHash ui/package-lock.json -Algorithm SHA256).Hash
    electron       = ((npm --prefix ui ls electron --depth=0 2>$null) | Select-String 'electron@' | Out-String).Trim()
    node           = (node --version).Trim()
    started        = (Get-Date).ToString('o')
    stages         = @()
    vitest         = $null
    e2e            = $null
}
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_OUT_DIR -ErrorAction SilentlyContinue

function Invoke-Stage([string]$Id, [string[]]$Argv) {
    $receipt = "$rd/s25-win-$Id.txt"
    & rtk proxy @Argv *> $receipt
    $code = $LASTEXITCODE
    $script:result.stages += [ordered]@{ id = $Id; argv = ($Argv -join ' '); exit = $code; receipt = $receipt }
    Get-Content $receipt -Tail 15 | Write-Host
    return $code
}

$pages = @('ui/src/renderer/src/features/transcript/TranscriptPage.tsx', 'ui/src/renderer/src/features/tts/TTSPage.tsx')
$auditSrc = $pages + @(
    'ui/src/renderer/src/features/transcript/transcript-card.ts', 'ui/src/renderer/src/features/transcript/TranscriptToolbar.tsx',
    'ui/src/renderer/src/features/tts/tts-run-bar.ts', 'ui/src/renderer/src/components/queue/QueueCard.tsx',
    'ui/src/renderer/src/components/queue/QueueCardMenu.tsx', 'ui/src/renderer/src/components/queue/QueueList.tsx',
    'ui/src/renderer/src/components/queue/QueueHeaderRow.tsx', 'ui/src/renderer/src/components/ui/ProgressBar.tsx')
$vjson = "$rd/s25-win-vitest.json"
$ejson = "$rd/s25-win-e2e.json"
$stages = @(
    @('npm-ci',      @('npm', '--prefix', 'ui', 'ci')),
    @('ui-types',    @('npm', '--prefix', 'ui', 'run', 'typecheck')),
    @('ui-lint',     @('npm', '--prefix', 'ui', 'run', 'lint')),
    @('ui-tests',    @('npm', '--prefix', 'ui', 'run', 'test', '--', '--reporter=json', "--outputFile=$vjson")),
    @('ui-build',    @('npm', '--prefix', 'ui', 'run', 'build')),
    @('ui-harness-build', @('pwsh', '-NoProfile', '-Command', "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$((Resolve-Path ui).Path)/out-e2e'; exit `$LASTEXITCODE")),
    @('ui-electron', @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', '--reporter=json', "--outputFile=$ejson")),
    @('source-audit', (@('rg', '-n', '-e', 'TODO', '-e', 'FIXME', '-e', 'NotImplementedError', '-e', 'transition-all', '-e', 'bg-\[#') + $auditSrc)),
    @('width-audit', @('rg', '-n', '-e', 'width:', '-e', 'style=\{\{\s*width', $pages[0], $pages[1]))
)
$failed = $false
foreach ($s in $stages) {
    $code = Invoke-Stage $s[0] $s[1]
    if ($s[0] -eq 'source-audit' -or $s[0] -eq 'width-audit') {
        # rg exit 1 means zero hits (clean); 0 means hits; 2+ means an IO error.
        $clean = ($code -eq 1)
        $result.stages[-1].exit = $(if ($clean) { 0 } else { 1 })
        $result.stages[-1].note = "rg exit $code (1 = no hits)"
        if (-not $clean) { $failed = $true; break }
    } elseif ($code -ne 0) { $failed = $true; break }
}
if (Test-Path $vjson) {
    $v = Get-Content $vjson -Raw | ConvertFrom-Json
    $result.vitest = [ordered]@{ passed = $v.numPassedTests; failed = $v.numFailedTests; total = $v.numTotalTests }
}
if (Test-Path $ejson) {
    $e = Get-Content $ejson -Raw | ConvertFrom-Json
    $result.e2e = [ordered]@{ expected = $e.stats.expected; unexpected = $e.stats.unexpected; skipped = $e.stats.skipped; flaky = $e.stats.flaky }
}
$ran = @($result.stages | ForEach-Object { $_.id })
if ($ran -contains 'ui-tests' -and $null -eq $result.vitest) { Write-Host 'FAIL: ui-tests ran but produced no Vitest JSON'; $failed = $true }
if ($ran -contains 'ui-electron' -and $null -eq $result.e2e) { Write-Host 'FAIL: ui-electron ran but produced no Playwright JSON'; $failed = $true }
$result.finished = (Get-Date).ToString('o')
$out = Join-Path $plan 'windows-gate-result.json'
$result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
Get-Content $out
if ($failed) { Write-Error 'WINDOWS_GATE failed; see the receipts named in the JSON'; exit 1 }
'PASS WINDOWS_GATE'
exit 0
