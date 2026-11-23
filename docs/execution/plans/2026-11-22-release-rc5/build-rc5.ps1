# rc.5 build (docs/execution/plans/2026-11-22-release-rc5). A copy of rc.4's build-rc4.ps1
# with the rc.5 installer name and record path; it runs in the clean clone C:/Temp/av-kit/rc5-src.
# rc.4 added Deno (MEU-141): the pinned archive and licence are copied from the cache and checked by
# tools/fetch_deno_windows.ps1 -ExtractOnly, and after electron-builder every extraResources target
# must exist in win-unpacked (the first rc.4 build shipped without Deno and only drew a warning).
# Order: negative control and starting identity, stale outputs, FFmpeg with its licence, Deno with
# its licence, backend, dist:prep, licence list, electron-builder, resources check, size limit,
# build record. Plain `npm run dist` cannot
# be used: the generator needs the picker's fresh .deps.json from dist:prep, and electron-builder
# needs the generator's output. electron-builder only warns on a missing extraResources source, so
# this script is what stops the build when the generator refuses.
# Nothing is published: --publish never, and no step uploads anything.
# Unlike build-rc.ps1, this copy sits outside build_inputs (docs/ is not hashed); the task log
# records its SHA-256 instead. It must not change while a build runs.
# Exit = the failing step's own code, or 20 to 24 for this script's own refusals.
$ErrorActionPreference = 'Stop'
$env:ELECTRON_RUN_AS_NODE = $null
# The fetch tool takes these over its pinned values; the pin is the point here (D-182, S2).
$env:AVKIT_FFMPEG_URL = $null
$env:AVKIT_FFMPEG_SHA256 = $null
# Round-1 F3: a cache miss fails its step (S13) instead of downloading. Every proxy variable points
# at a dead local port (D-88): electron-builder's toolset agent, NuGet and uv read them, Node's
# fetch reads them with NODE_USE_ENV_PROXY, and @electron/get with ELECTRON_GET_USE_PROXY. uv and
# npm also run offline. offline-probe.ps1 runs these lines and shows each client failing behind them.
# offline-guard begin
foreach ($name in 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY') { Set-Item -LiteralPath "env:$name" -Value 'http://127.0.0.1:9' }
$env:NO_PROXY = '127.0.0.1,localhost'
$env:NODE_USE_ENV_PROXY = '1'
$env:ELECTRON_GET_USE_PROXY = 'true'
$env:UV_OFFLINE = '1'
$env:UV_PYTHON_DOWNLOADS = 'never'
$env:npm_config_offline = 'true'
# offline-guard end

$root = (git rev-parse --show-toplevel).Trim()
Set-Location -LiteralPath $root

$identity = 'docs/execution/plans/2026-11-08-release-rc2/build-identity.py'
$negativeControl = 'C:/Temp/av-kit/rc1/negative-control/avkit-backend.exe'
$negativeControlSha = '3d5691fc07310ca28c78d8a101fdd84d8b3100d2753605aaee6dd4a19394da87'
$cachedArchive = 'C:/Temp/av-kit/ffmpeg-dl/ffmpeg-pin.zip'
$ffmpegArchive = 'packaging/ffmpeg-win64/ffmpeg-pin.zip'
$cachedDeno = 'C:/Temp/av-kit/deno-dl'
$denoDir = 'packaging/deno-win64'
$installer = 'ui/dist/av-kit-Setup-0.1.0-rc.5.exe'
$record = 'C:/Temp/av-kit/rc5/build-record.json'
$sizeLimit = 500000000

function Invoke-Step([string]$Name, [scriptblock]$Command) {
    Write-Output "== $Name"
    & $Command
    $code = $LASTEXITCODE
    Write-Output "== $Name exit=$code"
    if ($code -ne 0) { exit $code }
}

if (-not (Test-Path -LiteralPath $negativeControl)) {
    Write-Output "refused: negative control missing: $negativeControl"
    exit 20
}
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $negativeControl).Hash.ToLowerInvariant()
if ($actual -ne $negativeControlSha) {
    Write-Output "refused: negative control is $actual, expected $negativeControlSha"
    exit 20
}
Write-Output "negative control ok: $actual"

$line = uv run --frozen python $identity | Select-String -Pattern '^build_inputs [0-9a-f]{64}$'
if ($null -eq $line) {
    Write-Output 'refused: no build_inputs line from the identity tool'
    exit 21
}
$startInputs = ($line.Line -split ' ')[1]
Write-Output "starting build_inputs $startInputs"

foreach ($stale in 'ui/dist', 'packaging/build', 'packaging/dist') {
    if (Test-Path -LiteralPath $stale) {
        Remove-Item -LiteralPath $stale -Recurse -Force
        Write-Output "deleted stale $stale"
    }
}

Copy-Item -LiteralPath $cachedArchive -Destination $ffmpegArchive -Force
Invoke-Step 'ffmpeg' { pwsh -NoProfile -File tools/fetch_ffmpeg_windows.ps1 -ExtractOnly }
New-Item -ItemType Directory -Force -Path $denoDir | Out-Null
Copy-Item -LiteralPath "$cachedDeno/deno-pin.zip" -Destination "$denoDir/deno-pin.zip" -Force
Copy-Item -LiteralPath "$cachedDeno/LICENSE.md" -Destination "$denoDir/LICENSE.md" -Force
Invoke-Step 'deno' { pwsh -NoProfile -File tools/fetch_deno_windows.ps1 -ExtractOnly }
Invoke-Step 'backend' { uv run --frozen python tools/package_backend.py }
Invoke-Step 'dist:prep' { npm --prefix ui run dist:prep }
Invoke-Step 'licence list' { uv run --frozen python tools/generate_third_party_licenses.py }
Invoke-Step 'electron-builder' {
    Push-Location ui
    try {
        npx electron-builder --win nsis --x64 --publish never
    }
    finally {
        Pop-Location
    }
}

$resources = 'ui/dist/win-unpacked/resources'
$missing = @(
    'icon.png', 'icon.ico', 'avkit-backend/avkit-backend.exe', 'ffmpeg/ffmpeg.exe', 'ffmpeg/ffprobe.exe',
    'deno/deno.exe', 'deno/LICENSE.md', 'THIRD_PARTY_NOTICES.md', 'THIRD_PARTY_LICENSES.txt', 'LICENSE',
    'mcp-server', 'region-picker'
) | Where-Object { -not (Test-Path -LiteralPath "$resources/$_") }
if ($missing.Count -gt 0) {
    Write-Output "refused: missing from $resources`: $($missing -join ', ')"
    exit 24
}
Write-Output 'resources check: every extraResources target is present'

if (-not (Test-Path -LiteralPath $installer)) {
    Write-Output "refused: no installer at $installer"
    exit 22
}
$size = (Get-Item -LiteralPath $installer).Length
Write-Output "installer size $size"
if ($size -ge $sizeLimit) {
    Write-Output "refused: installer is $size B, the limit is under $sizeLimit B"
    exit 23
}

Invoke-Step 'build record' {
    uv run --frozen python $identity --write-record $record --installer $installer --ffmpeg-archive $ffmpegArchive --expect-inputs $startInputs
}
Write-Output 'build-rc: done'
exit 0
