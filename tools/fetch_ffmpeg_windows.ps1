# Fetch a pinned Windows FFmpeg essentials build into FFMPEG_VENDOR.
# URL + SHA256 are mandatory. Never download an unpinned floating "latest".
# Pin: BtbN autobuild-2026-10-31-12-59 win64 gpl (not /latest/).
# The build's GPL-3.0 LICENSE.txt is required and lands next to the binaries (D-87,
# packaging/THIRD_PARTY_NOTICES.md).
param(
    [string]$OutDir = 'packaging/ffmpeg-win64',
    [string]$Url = $(if ($env:AVKIT_FFMPEG_URL) { $env:AVKIT_FFMPEG_URL } else { 'https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2026-10-31-12-59/ffmpeg-n8.1.3-27-g8dca1586f4-win64-gpl-8.1.zip' }),
    [string]$Sha256 = $(if ($env:AVKIT_FFMPEG_SHA256) { $env:AVKIT_FFMPEG_SHA256 } else { '401DFFCF14C301082E1FC03B0BC876B92EA676BFC521FC56E80A1537D137034F' }),
    [switch]$ExtractOnly
)
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Url)) {
    Write-Error 'FETCH_FFMPEG requires a pinned URL (AVKIT_FFMPEG_URL or -Url).'
    exit 2
}
if ($Sha256 -notmatch '^[0-9A-Fa-f]{64}$') {
    Write-Error 'FETCH_FFMPEG requires a nonempty 64-hex SHA256 (AVKIT_FFMPEG_SHA256 or -Sha256).'
    exit 2
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$archive = Join-Path $OutDir 'ffmpeg-pin.zip'
if (-not $ExtractOnly) {
    Invoke-WebRequest -Uri $Url -OutFile $archive
}
if (-not (Test-Path -LiteralPath $archive)) {
    Write-Error ('missing archive ' + $archive)
    exit 2
}
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash
if ($actual.ToLowerInvariant() -ne $Sha256.ToLowerInvariant()) {
    Write-Error ("SHA256 mismatch actual=" + $actual + " expected=" + $Sha256)
    exit 3
}
$stage = Join-Path $OutDir '_extract'
if (Test-Path -LiteralPath $stage) {
    Remove-Item -LiteralPath $stage -Recurse -Force
}
Expand-Archive -LiteralPath $archive -DestinationPath $stage -Force
$bins = @(Get-ChildItem -Path $stage -Recurse -Include 'ffmpeg.exe', 'ffprobe.exe')
if ($bins.Count -lt 2) {
    Write-Error 'archive missing ffmpeg.exe or ffprobe.exe'
    exit 4
}
# The shallowest LICENSE.txt is the build's own (BtbN puts it in the archive root folder).
$license = Get-ChildItem -Path $stage -Recurse -File -Filter 'LICENSE.txt' |
    Sort-Object { $_.FullName.Length } | Select-Object -First 1
if ($null -eq $license) {
    Remove-Item -LiteralPath $stage -Recurse -Force
    # Not Write-Error: under ErrorActionPreference Stop it throws (exit 1) before exit 6.
    [Console]::Error.WriteLine('archive missing LICENSE.txt')
    exit 6
}
foreach ($bin in $bins) {
    if ($bin.Length -le 1024) {
        Write-Error ('refusing stub payload ' + $bin.Name + ' bytes=' + $bin.Length)
        exit 5
    }
    Copy-Item -LiteralPath $bin.FullName -Destination (Join-Path $OutDir $bin.Name) -Force
}
Copy-Item -LiteralPath $license.FullName -Destination (Join-Path $OutDir 'LICENSE.txt') -Force
Remove-Item -LiteralPath $stage -Recurse -Force
Write-Output ("PASS: FETCH_FFMPEG sha256=" + $actual)
exit 0
