# Session 57 offline-guard probe (task row 3, before build-rc.ps1; implementation-plan.md §The
# build, round-1 F3). It runs build-rc.ps1's own guard (the lines between its `# offline-guard
# begin` and `# offline-guard end` markers) and shows that each HTTP client the build uses fails
# behind it: Node's fetch, electron-builder's toolset download (the @electron/get path the Electron
# zip also takes), NuGet, uv and npm. Every target host is under `.invalid`, so a client that
# ignored the guard would fail on its own name lookup and reach nothing; the probe tells the two
# apart by the error. Last, the region picker's real restore passes behind the guard, so the
# build's NuGet step needs no network. Scratch is C:/Temp/av-kit/s57/offline-probe, recreated each run.
# Exit 0 = every case passed, 1 = a case failed, 2 = the guard block is missing.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location -LiteralPath $root

$build = Get-Content -LiteralPath 'docs/execution/plans/2026-11-08-release-rc2/build-rc.ps1'
$begin = [Array]::IndexOf($build, '# offline-guard begin')
$end = [Array]::IndexOf($build, '# offline-guard end')
if ($begin -lt 0 -or $end -le $begin + 1) {
    Write-Output 'offline-probe: build-rc.ps1 has no offline-guard block'
    exit 2
}
Invoke-Expression (($build[($begin + 1)..($end - 1)]) -join "`n")
Write-Output ("offline-probe: guard loaded, HTTPS_PROXY={0} UV_OFFLINE={1} npm_config_offline={2}" -f $env:HTTPS_PROXY, $env:UV_OFFLINE, $env:npm_config_offline)

$scratch = 'C:/Temp/av-kit/s57/offline-probe'
if (Test-Path -LiteralPath $scratch) { Remove-Item -LiteralPath $scratch -Recurse -Force }
New-Item -ItemType Directory -Force -Path $scratch | Out-Null
$script:cases = 0
$script:failures = 0

# A case passes when the command exits non-zero, its output names the guard's refusal, and it
# shows no sign of a lookup or a response of its own.
function Test-Case([string]$Name, [int]$WantExit, [string[]]$Need, [string[]]$Forbid, [scriptblock]$Command) {
    $script:cases++
    $ErrorActionPreference = 'Continue'
    $out = (& $Command 2>&1 | Out-String)
    $code = $LASTEXITCODE
    $exitOk = if ($WantExit -eq 0) { $code -eq 0 } else { $code -ne 0 }
    $missing = @($Need | Where-Object { -not $out.Contains($_) })
    $found = @($Forbid | Where-Object { $out.Contains($_) })
    $ok = $exitOk -and $missing.Count -eq 0 -and $found.Count -eq 0
    if (-not $ok) { $script:failures++ }
    $tail = ($out -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -Last 6) -join "`n    "
    Write-Output ("offline-probe {0}: exit {1}, missing [{2}], forbidden [{3}]: {4}`n    {5}" -f $Name, $code, ($missing -join ', '), ($found -join ', '), $(if ($ok) { 'ok' } else { 'FAIL' }), $tail)
}

$catch = 'e=>{let c=e;while(c){console.log("err",c.code,c.message);c=c.cause}process.exit(1)}'
Test-Case 'node-fetch' 1 @('127.0.0.1:9') @('ENOTFOUND', 'reached') {
    node -e "setTimeout(()=>{console.log('timeout');process.exit(3)},120000).unref();fetch('https://probe.example.invalid/').then(()=>{console.log('reached');process.exit(0)},$catch)"
}

$env:ELECTRON_BUILDER_CACHE = "$scratch/eb-cache"
Test-Case 'electron-builder-toolset' 1 @('127.0.0.1:9') @('ENOTFOUND', 'reached') {
    node -e "setTimeout(()=>{console.log('timeout');process.exit(3)},120000).unref();require('./ui/node_modules/app-builder-lib/out/util/electronGet').downloadBuilderToolset({releaseName:'probe',filenameWithExt:'probe.7z',overrideUrl:'https://probe.example.invalid/probe'}).then(()=>{console.log('reached');process.exit(0)},$catch)"
}
Remove-Item -LiteralPath env:ELECTRON_BUILDER_CACHE

$nuget = "$scratch/nuget"
New-Item -ItemType Directory -Force -Path $nuget | Out-Null
Set-Content -LiteralPath "$nuget/probe.csproj" -Value '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0-windows</TargetFramework></PropertyGroup><ItemGroup><PackageReference Include="AvKit.OfflineProbe.Missing" Version="1.0.0" /></ItemGroup></Project>'
Set-Content -LiteralPath "$nuget/nuget.config" -Value '<configuration><packageSources><clear /><add key="probe" value="https://probe.example.invalid/v3/index.json" /></packageSources></configuration>'
# NuGet prints the same NU1301 line with or without the guard (plan-time comparison,
# C:/Temp/av-kit/s57-plan-nuget-unguarded.txt), so this case shows only the refusal; the HttpClient case after it
# shows that .NET's client, which NuGet uses, reads the dead proxy.
$env:NUGET_PACKAGES = "$scratch/nuget-packages"
$env:NUGET_HTTP_CACHE_PATH = "$scratch/nuget-http"
Test-Case 'nuget' 1 @('NU1301') @('Restored') {
    dotnet restore "$nuget/probe.csproj" --configfile "$nuget/nuget.config"
}
Remove-Item -LiteralPath env:NUGET_PACKAGES, env:NUGET_HTTP_CACHE_PATH
Test-Case 'dotnet-httpclient' 1 @('127.0.0.1:9') @('No such host', 'reached') {
    pwsh -NoProfile -Command {
        try {
            $null = [System.Net.Http.HttpClient]::new().GetAsync('https://probe.example.invalid/').GetAwaiter().GetResult()
            'reached'
            exit 0
        }
        catch {
            $e = $_.Exception
            while ($e) { "err $($e.Message)"; $e = $e.InnerException }
            exit 1
        }
    }
}

$uvProject = "$scratch/uv"
New-Item -ItemType Directory -Force -Path $uvProject | Out-Null
Set-Content -LiteralPath "$uvProject/pyproject.toml" -Value @(
    '[project]', 'name = "offline-probe"', 'version = "0"', 'requires-python = ">=3.12"',
    'dependencies = ["avkit-offline-probe-missing==1.0"]', '',
    '[[tool.uv.index]]', 'url = "https://probe.example.invalid/simple"', 'default = true'
)
$env:UV_CACHE_DIR = "$scratch/uv-cache"
Test-Case 'uv' 1 @('network was disabled') @('dns error', 'Resolved') {
    uv lock --project $uvProject
}
Remove-Item -LiteralPath env:UV_CACHE_DIR

Test-Case 'npm' 1 @('ENOTCACHED') @('ENOTFOUND') {
    npm view avkit-offline-probe-missing version --registry https://probe.example.invalid/ --cache "$scratch/npm-cache"
}

Test-Case 'picker-restore' 0 @('avkit-region-picker.csproj') @('NU1301', 'error') {
    # --force re-resolves every package, so a restore that is already up to date still proves it.
    dotnet restore native/region-picker -r win-x64 --force
}

Write-Output ("offline-probe: {0}/{1} passed" -f ($script:cases - $script:failures), $script:cases)
$code = [int]($script:failures -ne 0)
exit $code
