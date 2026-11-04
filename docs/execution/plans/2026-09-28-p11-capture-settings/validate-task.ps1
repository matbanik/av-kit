# WINDOWS_GATE for 2026-09-28-p11-capture-settings: the authoritative Phase 11 exit gate.
# It is human-run by Mat; see human-gate-decision.md.
# Run from P:/av-kit on the pushed commit under review:
#   git pull origin claude/quirky-gates-o1lql2
#   pwsh -NoProfile -File docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.ps1 -Check windows-gate
# It runs the full PROFILE D6 set (Python, UI, MCP, OpenAPI, state render, real Electron) in stage
# order through `rtk proxy`, and stops at the first failure (later stages are not_run).
# It writes windows-gate-result.json next to this script. Then commit and push only that file:
#   git add docs/execution/plans/2026-09-28-p11-capture-settings/windows-gate-result.json
#   git commit -m "docs(execution): record Session 26 Windows gate"
#   git push origin claude/quirky-gates-o1lql2
param([Parameter(Mandatory = $true)][string]$Check)
$ErrorActionPreference = 'Stop'
# Native exit codes are read explicitly from $LASTEXITCODE; never let pwsh 7.4+ turn them into throws.
$PSNativeCommandUseErrorActionPreference = $false
$rd = 'C:/Temp/av-kit'
New-Item -ItemType Directory -Force -Path $rd | Out-Null
$plan = 'docs/execution/plans/2026-09-28-p11-capture-settings'

if ($Check -ne 'windows-gate') { throw "Unknown check: $Check" }

$result = [ordered]@{
    schema          = 's26-windows-gate.v1'
    tested_commit   = (git rev-parse HEAD).Trim()
    # A leftover result file from an earlier run is not a dirty tree.
    clean_tree      = [string]::IsNullOrWhiteSpace((git status --porcelain | Where-Object { $_ -notmatch 'windows-gate-result\.json' } | Out-String))
    lockfile_sha256 = (Get-FileHash ui/package-lock.json -Algorithm SHA256).Hash
    mcp_lockfile_sha256 = (Get-FileHash mcp-server/package-lock.json -Algorithm SHA256).Hash
    electron        = ((npm --prefix ui ls electron --depth=0 2>$null) | Select-String 'electron@' | Out-String).Trim()
    node            = (node --version).Trim()
    started         = (Get-Date).ToString('o')
    stages          = @()
    vitest          = $null
    e2e             = $null
}
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_OUT_DIR -ErrorAction SilentlyContinue

function Invoke-Stage([string]$Id, [string[]]$Argv) {
    $receipt = "$rd/s26-win-$Id.txt"
    & rtk proxy @Argv *> $receipt
    $code = $LASTEXITCODE
    $script:result.stages += [ordered]@{ id = $Id; argv = ($Argv -join ' '); exit = $code; receipt = $receipt }
    Get-Content $receipt -Tail 15 | Write-Host
    return $code
}

$auditSrc = @(
    'ui/src/renderer/src/features/capture/CapturePage.tsx', 'ui/src/renderer/src/features/capture/CaptureViewport.tsx',
    'ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx', 'ui/src/renderer/src/features/capture/capture-filmstrip-label.ts',
    'ui/src/renderer/src/features/settings/SettingsPage.tsx', 'ui/src/renderer/src/features/settings/SettingsRail.tsx',
    'ui/src/renderer/src/features/settings/settings-sections.ts', 'ui/src/renderer/src/features/settings/StartAtSignInControl.tsx',
    'ui/src/renderer/src/components/ui/PathRow.tsx')
$vjson = "$rd/s26-win-vitest.json"
$ejson = "$rd/s26-win-e2e.json"
$stages = @(
    @('npm-ci',        @('npm', '--prefix', 'ui', 'ci')),
    @('mcp-npm-ci',    @('npm', '--prefix', 'mcp-server', 'ci')),
    @('py-types',      @('uv', 'run', 'pyright', 'packages/')),
    @('py-lint',       @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/')),
    @('ui-types',      @('npm', '--prefix', 'ui', 'run', 'typecheck')),
    @('ui-lint',       @('npm', '--prefix', 'ui', 'run', 'lint')),
    @('mcp-types',     @('npm', '--prefix', 'mcp-server', 'run', 'typecheck')),
    @('py-tests',      @('uv', 'run', 'pytest', 'tests/', '-x', '--tb=short', '-q')),
    @('ui-tests',      @('npm', '--prefix', 'ui', 'run', 'test', '--', '--reporter=json', "--outputFile=$vjson")),
    @('ui-build',      @('npm', '--prefix', 'ui', 'run', 'build')),
    @('ui-harness-build', @('pwsh', '-NoProfile', '-Command', "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$((Resolve-Path ui).Path)/out-e2e'; exit `$LASTEXITCODE")),
    # The MCP suite asserts the built dist exists (AC-32.8, AC-38.8), so build first.
    @('mcp-build',     @('npm', '--prefix', 'mcp-server', 'run', 'build')),
    @('mcp-tests',     @('npm', '--prefix', 'mcp-server', 'run', 'test')),
    @('openapi',       @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json')),
    @('state-render',  @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')),
    @('ui-electron',   @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', '--reporter=json', "--outputFile=$ejson")),
    @('source-audit',  (@('rg', '-n', '-e', 'TODO', '-e', 'FIXME', '-e', 'NotImplementedError', '-e', 'transition-all', '-e', 'bg-\[#') + $auditSrc))
)
# A run must never report an earlier run's counts (attempt 4 did): start from no receipts,
# and read each JSON only when the stage that writes it ran in this run.
Remove-Item -LiteralPath $vjson, $ejson -ErrorAction SilentlyContinue
$failed = $false
foreach ($s in $stages) {
    $code = Invoke-Stage $s[0] $s[1]
    if ($s[0] -eq 'source-audit') {
        # rg exit 1 means zero hits (clean); 0 means hits; 2+ means an IO error.
        $clean = ($code -eq 1)
        $result.stages[-1].exit = $(if ($clean) { 0 } else { 1 })
        $result.stages[-1].note = "rg exit $code (1 = no hits)"
        if (-not $clean) { $failed = $true; break }
    } elseif ($code -ne 0) { $failed = $true; break }
}
$ran = @($result.stages | ForEach-Object { $_.id })
if ($ran -contains 'ui-tests' -and (Test-Path $vjson)) {
    $v = Get-Content $vjson -Raw | ConvertFrom-Json
    $result.vitest = [ordered]@{ passed = $v.numPassedTests; failed = $v.numFailedTests; total = $v.numTotalTests }
}
if ($ran -contains 'ui-electron' -and (Test-Path $ejson)) {
    $e = Get-Content $ejson -Raw | ConvertFrom-Json
    $result.e2e = [ordered]@{ expected = $e.stats.expected; unexpected = $e.stats.unexpected; skipped = $e.stats.skipped; flaky = $e.stats.flaky }
}
if ($ran -contains 'ui-tests' -and $null -eq $result.vitest) { Write-Host 'FAIL: ui-tests ran but produced no Vitest JSON'; $failed = $true }
if ($ran -contains 'ui-electron' -and $null -eq $result.e2e) { Write-Host 'FAIL: ui-electron ran but produced no Playwright JSON'; $failed = $true }
$result.finished = (Get-Date).ToString('o')
$out = Join-Path $plan 'windows-gate-result.json'
$result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
Get-Content $out
if ($failed) { Write-Error 'WINDOWS_GATE failed; see the receipts named in the JSON'; exit 1 }
'PASS WINDOWS_GATE'
exit 0
