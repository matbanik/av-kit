# Session 97 (task rows 4, 5, 7 and H1-2): runs one named subset of the touched E2E specs on this
# PC through ui/scripts/playwright-with-outputfile.mjs, with ELECTRON_RUN_AS_NODE removed, and
# writes Playwright's JSON report to -Out (list output goes to the console; redirect it).
#   fidelity  capture-inbox.test.ts, the three fidelity specs (AC-82.6, AC-102.19, AC-102.20)
#   hover     settings.test.ts, AC-126.8
#   touched   capture-inbox.test.ts and settings.test.ts in full
# -Build runs `npm --prefix ui run build` first (the specs launch the built app). It never runs the
# clipboard specs (capture-filmstrip-actions, capture-import), names no host and reads no user data.
# Usage (pwsh, from the repository root):
#   pwsh -NoProfile -File <plan>/e2e-subset.ps1 -Set fidelity -Out C:/Temp/av-kit/e2e-host-parity/x.json [-Build]
param(
    [Parameter(Mandatory = $true)][ValidateSet('fidelity', 'hover', 'touched')][string]$Set,
    [Parameter(Mandatory = $true)][string]$Out,
    [switch]$Build
)
$ErrorActionPreference = 'Stop'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
$root = (git rev-parse --show-toplevel).Trim()
Set-Location -LiteralPath $root
$outPath = [System.IO.Path]::GetFullPath($Out)
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outPath) | Out-Null
if (Test-Path -LiteralPath $outPath) { Remove-Item -LiteralPath $outPath -Force }

$sets = @{
    fidelity = @('tests/e2e/capture-inbox.test.ts', '-g', 'AC-82\.6 TEXT_PIXEL_ORACLE|AC-102\.19 TEXT_PARITY_E2E|AC-102\.20 AC-82\.6')
    hover    = @('tests/e2e/settings.test.ts', '-g', 'AC-126\.8 ')
    touched  = @('tests/e2e/capture-inbox.test.ts', 'tests/e2e/settings.test.ts')
}

if ($Build) {
    & npm --prefix ui run build
    if ($LASTEXITCODE -ne 0) {
        "e2e-subset set=$Set build exit=$LASTEXITCODE"
        exit $LASTEXITCODE
    }
}

$argv = @('ui/scripts/playwright-with-outputfile.mjs') + $sets[$Set] + @('--reporter=list,json', "--outputFile=$outPath")
& node @argv
$code = $LASTEXITCODE
"e2e-subset set=$Set exit=$code report=$([System.IO.File]::Exists($outPath))"
exit $code
