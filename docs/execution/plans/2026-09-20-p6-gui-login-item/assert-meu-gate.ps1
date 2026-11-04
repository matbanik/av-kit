# MEU-61 blocking gate: typecheck, lint, vitest, OpenAPI, E2E census, named classify, scans.
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

Write-Output 'STEP typecheck'
& npm --prefix ui run typecheck *> 'C:/Temp/av-kit/meu61-typecheck.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu61-typecheck.txt' -Tail 40; exit $LASTEXITCODE }

Write-Output 'STEP lint'
& npm --prefix ui run lint *> 'C:/Temp/av-kit/meu61-lint.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu61-lint.txt' -Tail 40; exit $LASTEXITCODE }

Write-Output 'STEP vitest'
& npm --prefix ui run test *> 'C:/Temp/av-kit/meu61-vitest.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu61-vitest.txt' -Tail 40; exit $LASTEXITCODE }

Write-Output 'STEP pytest-skip'
'SKIP: packages/api and Python capture surfaces not in MEU-61 scope' | Set-Content 'C:/Temp/av-kit/meu61-pytest-skip.txt'

Write-Output 'STEP openapi'
& uv run python tools/export_openapi.py --check openapi.committed.json *> 'C:/Temp/av-kit/openapi-check.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/openapi-check.txt'; exit $LASTEXITCODE }

Write-Output 'STEP mcp-skip'
'SKIP: mcp-server not in MEU-61 scope' | Set-Content 'C:/Temp/av-kit/meu61-mcp-skip.txt'

Write-Output 'STEP e2e-census'
& pwsh -NoProfile -File (Join-Path $root 'assert-e2e-census.ps1') *> 'C:/Temp/av-kit/meu61-e2e-census.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu61-e2e-census.txt'; exit $LASTEXITCODE }

Write-Output 'STEP e2e-named-result'
& pwsh -NoProfile -File (Join-Path $root 'assert-e2e-named.ps1') -Mode gate *> 'C:/Temp/av-kit/meu61-e2e-gate.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu61-e2e-gate.txt'; exit $LASTEXITCODE }

Write-Output 'STEP scans'
& pwsh -NoProfile -File (Join-Path $root 'assert-meu-scans.ps1') *> 'C:/Temp/av-kit/meu61-deps.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu61-deps.txt'; exit $LASTEXITCODE }

'PASS: MEU-61 gate'
exit 0
