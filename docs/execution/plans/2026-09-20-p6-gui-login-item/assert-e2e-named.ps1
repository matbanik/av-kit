# Named Playwright AC-61.17: census then run then classify. Grep/spec from named-sets.json.
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('named', 'gate')]
    [string]$Mode
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$sets = Get-Content -LiteralPath (Join-Path $root 'named-sets.json') -Raw | ConvertFrom-Json
$case = [string]$sets.E2E_GREP
$specRepo = [string]$sets.E2E_SPEC
$specNpm = $specRepo
if ($specRepo.StartsWith('ui/')) { $specNpm = $specRepo.Substring(3) }
$greenReceipt = [string]$sets.E2E_GREEN_RECEIPT
$greenJson = [string]$sets.E2E_GREEN_JSON
$classify = Join-Path $root 'assert-e2e-classify.ps1'
$census = Join-Path $root 'assert-e2e-census.ps1'

if ($Mode -eq 'gate') {
    & pwsh -NoProfile -File $classify -Mode gate
    exit $LASTEXITCODE
}

& pwsh -NoProfile -File $census
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$env:ELECTRON_RUN_AS_NODE = $null
& npm --prefix ui run test:e2e -- $specNpm --grep $case --reporter=json --outputFile=$greenJson *> $greenReceipt
$pw = $LASTEXITCODE
& pwsh -NoProfile -File $classify -Mode named -Receipt $greenReceipt -JsonReceipt $greenJson -PlaywrightExit $pw
exit $LASTEXITCODE
