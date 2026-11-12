# Fetch a pinned Windows Deno build into packaging/deno-win64 (MEU-141 DENO_BUNDLE, D-649).
# URL + SHA256 are mandatory for the archive and for the licence. Never fetch an unpinned "latest".
# Pin: denoland/deno v2.9.8 deno-x86_64-pc-windows-msvc.zip, and LICENSE.md at the v2.9.8 tag.
# Deno is MIT; its LICENSE.md lands next to deno.exe as resources/deno/LICENSE.md (DENO_LICENCE,
# packaging/THIRD_PARTY_NOTICES.md).
param(
    [string]$OutDir = 'packaging/deno-win64',
    [string]$Url = $(if ($env:AVKIT_DENO_URL) { $env:AVKIT_DENO_URL } else { 'https://github.com/denoland/deno/releases/download/v2.9.8/deno-x86_64-pc-windows-msvc.zip' }),
    [string]$Sha256 = $(if ($env:AVKIT_DENO_SHA256) { $env:AVKIT_DENO_SHA256 } else { 'cba84b26e0df5ae7f74fc66b86a95b866872a86292ebd84fa1e959927edd93bf' }),
    [string]$LicenseUrl = 'https://raw.githubusercontent.com/denoland/deno/v2.9.8/LICENSE.md',
    [string]$LicenseSha256 = 'f62497fffecc0852960c8d3e6934b9db86d16396e9b604072e923892cae3a588',
    [switch]$ExtractOnly
)
$ErrorActionPreference = 'Stop'
# Each refusal writes to stderr directly: the error cmdlet throws under Stop and exits 1,
# so the documented exit code below it would never run.
if ([string]::IsNullOrWhiteSpace($Url)) {
    [Console]::Error.WriteLine('FETCH_DENO requires a pinned URL (AVKIT_DENO_URL or -Url).')
    exit 2
}
if ($Sha256 -notmatch '^[0-9A-Fa-f]{64}$') {
    [Console]::Error.WriteLine('FETCH_DENO requires a nonempty 64-hex SHA256 (AVKIT_DENO_SHA256 or -Sha256).')
    exit 2
}
if ([string]::IsNullOrWhiteSpace($LicenseUrl)) {
    [Console]::Error.WriteLine('FETCH_DENO requires a pinned licence URL (-LicenseUrl).')
    exit 2
}
if ($LicenseSha256 -notmatch '^[0-9A-Fa-f]{64}$') {
    [Console]::Error.WriteLine('FETCH_DENO requires a nonempty 64-hex licence SHA256 (-LicenseSha256).')
    exit 2
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$archive = Join-Path $OutDir 'deno-pin.zip'
$license = Join-Path $OutDir 'LICENSE.md'
if (-not $ExtractOnly) {
    Invoke-WebRequest -Uri $Url -OutFile $archive
    Invoke-WebRequest -Uri $LicenseUrl -OutFile $license
}
foreach ($needed in @($archive, $license)) {
    if (-not (Test-Path -LiteralPath $needed)) {
        [Console]::Error.WriteLine('missing ' + $needed)
        exit 2
    }
}
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash
if ($actual.ToLowerInvariant() -ne $Sha256.ToLowerInvariant()) {
    [Console]::Error.WriteLine("SHA256 mismatch actual=" + $actual + " expected=" + $Sha256)
    exit 3
}
# The licence is checked before anything is extracted, so a wrong licence ships nothing.
$licenseActual = (Get-FileHash -Algorithm SHA256 -LiteralPath $license).Hash
if ($licenseActual.ToLowerInvariant() -ne $LicenseSha256.ToLowerInvariant()) {
    [Console]::Error.WriteLine("licence SHA256 mismatch actual=" + $licenseActual + " expected=" + $LicenseSha256)
    exit 3
}
$stage = Join-Path $OutDir '_extract'
if (Test-Path -LiteralPath $stage) {
    Remove-Item -LiteralPath $stage -Recurse -Force
}
Expand-Archive -LiteralPath $archive -DestinationPath $stage -Force
$bin = Get-ChildItem -Path $stage -Recurse -File -Filter 'deno.exe' |
    Sort-Object { $_.FullName.Length } | Select-Object -First 1
if ($null -eq $bin) {
    Remove-Item -LiteralPath $stage -Recurse -Force
    [Console]::Error.WriteLine('archive missing deno.exe')
    exit 4
}
if ($bin.Length -le 1024) {
    Remove-Item -LiteralPath $stage -Recurse -Force
    [Console]::Error.WriteLine('refusing stub payload deno.exe bytes=' + $bin.Length)
    exit 5
}
Copy-Item -LiteralPath $bin.FullName -Destination (Join-Path $OutDir 'deno.exe') -Force
Remove-Item -LiteralPath $stage -Recurse -Force
Write-Output ("PASS: FETCH_DENO sha256=" + $actual)
exit 0
