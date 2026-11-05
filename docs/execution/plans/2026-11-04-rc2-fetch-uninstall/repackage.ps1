# Session 49 prepackaged installer (task row 4; implementation-plan.md §Verification Plan 3).
# Compiles the current ui/build/installer.nsh under electron-builder's real NSIS settings (-WX)
# around RC1's unpacked app, with no build of the app, and copies the installer to
# PREPACKAGED_INSTALLER. The output goes to C:/Temp/av-kit/rc2/prepackaged-out, so RC1's
# installer in ui/dist stays as it is; the script checks that afterwards. electron-builder can
# still refresh resources/elevate.exe inside dist/win-unpacked. The installer stays on this PC.
# Exit: electron-builder's own code when it fails (S2), 20 when a precondition is missing,
# 21 when the output isn't there, 22 when RC1's installer changed.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$env:ELECTRON_RUN_AS_NODE = $null
$rc2 = 'C:/Temp/av-kit/rc2'
$rc1Installer = "$rc2/rc1-installer.exe"
$rc1Dist = 'ui/dist/av-kit-Setup-0.1.0-rc.1.exe'
$rc1Sha = 'beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7'
$out = "$rc2/prepackaged-out"
$prepackaged = "$rc2/prepackaged-installer.exe"

function Get-Sha([string]$Path) { (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant() }

if (-not (Test-Path $rc1Installer)) { Write-Output "missing RC1_INSTALLER $rc1Installer (row 0)"; exit 20 }
if ((Get-Sha $rc1Installer) -ne $rc1Sha) { Write-Output 'RC1_INSTALLER sha256 mismatch'; exit 20 }
if (-not (Test-Path 'ui/dist/win-unpacked/av-kit.exe')) { Write-Output 'missing ui/dist/win-unpacked/av-kit.exe'; exit 20 }
if (Test-Path $out) { Remove-Item -LiteralPath $out -Recurse -Force }

Push-Location ui
try {
    & npx electron-builder --win nsis --x64 --publish never --prepackaged dist/win-unpacked "-c.directories.output=$out"
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}
Write-Output "electron-builder exit=$code"
if ($code -ne 0) { exit $code }

$built = Join-Path $out 'av-kit-Setup-0.1.0-rc.1.exe'
if (-not (Test-Path $built)) { Write-Output "missing $built"; exit 21 }
Copy-Item -LiteralPath $built -Destination $prepackaged -Force
Write-Output ("PREPACKAGED_INSTALLER {0} bytes={1} sha256={2}" -f $prepackaged, (Get-Item $prepackaged).Length, (Get-Sha $prepackaged))
$distSha = Get-Sha $rc1Dist
Write-Output "ui/dist RC1 installer sha256=$distSha"
if ($distSha -ne $rc1Sha) { Write-Output 'RC1 installer in ui/dist changed'; exit 22 }
Write-Output 'repackage: PREPACKAGED_INSTALLER written; RC1 installer unchanged'
exit 0
