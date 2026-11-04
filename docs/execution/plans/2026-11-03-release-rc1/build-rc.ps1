# Session 44 real RC build (task row 10; implementation-plan.md Verification Plan section 3).
# Order: negative control and starting identity, stale outputs, FFmpeg with its licence, backend,
# dist:prep, licence list, electron-builder, size limit, build record. Plain `npm run dist` cannot
# be used: the generator needs the picker's fresh .deps.json from dist:prep, and electron-builder
# needs the generator's output. electron-builder only warns on a missing extraResources source, so
# this script is what stops the build when the generator refuses.
# Nothing is published: --publish never, and no step uploads anything.
# This file is hashed into build_inputs, so it must not change while a build runs.
# Exit = the failing step's own code, or 20 to 23 for this script's own refusals.
$ErrorActionPreference = 'Stop'
$env:ELECTRON_RUN_AS_NODE = $null
# The fetch tool takes these over its pinned values; the pin is the point here (D-182, S2).
$env:AVKIT_FFMPEG_URL = $null
$env:AVKIT_FFMPEG_SHA256 = $null

$root = (git rev-parse --show-toplevel).Trim()
Set-Location -LiteralPath $root

$identity = 'docs/execution/plans/2026-11-03-release-rc1/build-identity.py'
$negativeControl = 'C:/Temp/av-kit/rc1/negative-control/avkit-backend.exe'
$negativeControlSha = '3d5691fc07310ca28c78d8a101fdd84d8b3100d2753605aaee6dd4a19394da87'
$cachedArchive = 'C:/Temp/av-kit/ffmpeg-dl/ffmpeg-pin.zip'
$ffmpegArchive = 'packaging/ffmpeg-win64/ffmpeg-pin.zip'
$installer = 'ui/dist/av-kit-Setup-0.1.0-rc.1.exe'
$record = 'C:/Temp/av-kit/rc1/build-record.json'
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
