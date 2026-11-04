# MEU-59 blocking gate: typecheck, lint, vitest, pytest, OpenAPI, MCP tests, E2E census, scans.
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

Write-Output 'STEP typecheck'
& npm --prefix ui run typecheck *> 'C:/Temp/av-kit/meu59-typecheck.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu59-typecheck.txt' -Tail 40; exit $LASTEXITCODE }

Write-Output 'STEP lint'
& npm --prefix ui run lint *> 'C:/Temp/av-kit/meu59-lint.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu59-lint.txt' -Tail 40; exit $LASTEXITCODE }

Write-Output 'STEP vitest'
& npm --prefix ui run test *> 'C:/Temp/av-kit/meu59-vitest.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu59-vitest.txt' -Tail 40; exit $LASTEXITCODE }

Write-Output 'STEP pytest'
& uv run pytest tests/unit/test_capture_adapter.py tests/unit/test_capture_service.py tests/e2e/test_api_captures.py -q --tb=short *> 'C:/Temp/av-kit/meu59-pytest.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu59-pytest.txt' -Tail 40; exit $LASTEXITCODE }

Write-Output 'STEP openapi'
& uv run python tools/export_openapi.py --check openapi.committed.json *> 'C:/Temp/av-kit/openapi-check.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/openapi-check.txt'; exit $LASTEXITCODE }

Write-Output 'STEP mcp-test'
& npm --prefix mcp-server run test *> 'C:/Temp/av-kit/meu59-mcp-test.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu59-mcp-test.txt' -Tail 40; exit $LASTEXITCODE }

Write-Output 'STEP e2e-census'
& pwsh -NoProfile -File (Join-Path $root 'assert-e2e-census.ps1') *> 'C:/Temp/av-kit/meu59-e2e-census.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu59-e2e-census.txt'; exit $LASTEXITCODE }

Write-Output 'STEP scans'
& pwsh -NoProfile -File (Join-Path $root 'assert-meu-scans.ps1') *> 'C:/Temp/av-kit/meu59-deps.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'C:/Temp/av-kit/meu59-deps.txt'; exit $LASTEXITCODE }

'PASS: MEU-59 gate'
exit 0
