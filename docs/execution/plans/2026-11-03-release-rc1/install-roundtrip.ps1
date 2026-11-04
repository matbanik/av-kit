# Session 44 NSIS round trip on this PC (task row 12; AC-110.15; plan stop conditions S5, S6, S8).
# This proves the installer, the installed app and the uninstaller here. It does not replace the
# clean-machine test. Snapshots hold names only; the real app data's contents are never read, and
# the app runs on a throwaway AVKIT_APP_DATA. A failing smoke still uninstalls.
# Exit: 40 an S5 precondition, 41 the installer differs from the build record (S8), 42 the install
# failed, 44 the install-root smoke failed, 45 the app smoke failed, 46 the uninstall left something
# behind or changed the app data (S6). The first failure's code is the exit code.
$ErrorActionPreference = 'Stop'
$env:ELECTRON_RUN_AS_NODE = $null

$root = (git rev-parse --show-toplevel).Trim()
Set-Location -LiteralPath $root

$rc = 'C:/Temp/av-kit/rc1'
$plan = 'docs/execution/plans/2026-11-03-release-rc1'
$installer = 'ui/dist/av-kit-Setup-0.1.0-rc.1.exe'
$target = 'C:\Temp\av-kit\rc1\install'
$throwawayAppData = "$rc/install-app-data"
$negativeControl = "$rc/negative-control/avkit-backend.exe"
$appId = 'com.avkit.app'
$linkName = 'av-kit.lnk'
$ourNames = 'av-?kit|com\.avkit'
$installTimeoutMs = 600000
$uninstallTimeoutS = 300
$quitTimeoutS = 30

$uninstallRoot = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall'
$runKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$approvedKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run'
$desktop = [Environment]::GetFolderPath('Desktop')
$programs = [Environment]::GetFolderPath('Programs')
$realAppData = Join-Path $env:LOCALAPPDATA 'av-kit'
$defaultInstall = Join-Path $env:LOCALAPPDATA 'Programs\av-kit'

function Get-ValueNames([string]$Key) {
    if (Test-Path -LiteralPath $Key) { @((Get-Item -LiteralPath $Key).GetValueNames() | Sort-Object) }
    else { @() }
}

function Get-ChildNames([string]$Folder) {
    if (Test-Path -LiteralPath $Folder) {
        @(Get-ChildItem -LiteralPath $Folder -Force -Name | Sort-Object)
    }
    else { @() }
}

function Get-LinkNames([string]$Folder, [switch]$Recurse) {
    if (Test-Path -LiteralPath $Folder) {
        @(Get-ChildItem -LiteralPath $Folder -Filter '*.lnk' -Recurse:$Recurse -Force -Name -ErrorAction SilentlyContinue | Sort-Object)
    }
    else { @() }
}

function Get-AvkitUninstallEntries {
    $roots = @(
        $uninstallRoot,
        'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall',
        'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
    )
    foreach ($key in $roots) {
        if (-not (Test-Path -LiteralPath $key)) { continue }
        foreach ($entry in Get-ChildItem -LiteralPath $key -ErrorAction SilentlyContinue) {
            $name = $entry.GetValue('DisplayName')
            if ($name -like 'av-kit*') { $entry }
        }
    }
}

function Get-Snapshot([string]$Label) {
    $snapshot = [ordered]@{
        uninstall        = @(Get-ChildNames $uninstallRoot)
        run              = @(Get-ValueNames $runKey)
        startup_approved = @(Get-ValueNames $approvedKey)
        desktop          = @(Get-LinkNames $desktop)
        start_menu       = @(Get-LinkNames $programs -Recurse)
        app_data         = @(Get-ChildNames $realAppData)
        local_folders    = @(Get-ChildItem -LiteralPath $env:LOCALAPPDATA -Directory -Force -Name -Filter 'av-kit*' | Sort-Object)
        roaming_folders  = @(Get-ChildItem -LiteralPath $env:APPDATA -Directory -Force -Name -Filter 'av-kit*' | Sort-Object)
    }
    $snapshot | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath "$rc/snapshot-$Label.json" -Encoding utf8
    $snapshot
}

function Get-InstalledProcesses([string]$Location) {
    $prefix = (Resolve-Path -LiteralPath $Location).Path.TrimEnd('\') + '\'
    foreach ($process in Get-Process) {
        $path = $null
        try { $path = $process.Path } catch { continue }
        if ($path -and $path.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { $process }
    }
}

# Scoped to the install's own path, never by name: other av-kit copies on this PC are not ours.
function Stop-InstalledProcesses([string]$Location) {
    foreach ($process in @(Get-InstalledProcesses $Location)) {
        Write-Output "still running from the install: $($process.Name) ($($process.Id)); stopping it"
        Stop-Process -Id $process.Id -Force
    }
}

# S5: refuse before anything changes.
$blocked = @()
foreach ($key in $runKey, $approvedKey) {
    if ((Get-ValueNames $key) -contains $appId) { $blocked += "S5: $key has a $appId value" }
}
foreach ($entry in @(Get-AvkitUninstallEntries)) { $blocked += "S5: Uninstall entry exists: $($entry.Name)" }
if (Test-Path -LiteralPath $target) { $blocked += "S5: $target already exists" }
if ((Get-ChildNames $defaultInstall).Count -gt 0) { $blocked += "S5: $defaultInstall holds files" }
$linkPattern = "(^|\\)$([regex]::Escape($linkName))$"
if ((Get-LinkNames $desktop) -match $linkPattern) { $blocked += "S5: $linkName exists on the Desktop" }
if ((Get-LinkNames $programs -Recurse) -match $linkPattern) { $blocked += "S5: $linkName exists in the Start Menu" }
if (Get-Process -Name 'av-kit' -ErrorAction SilentlyContinue) { $blocked += 'S5: av-kit.exe is running' }
if ($blocked.Count -gt 0) {
    $blocked | ForEach-Object { Write-Output $_ }
    exit 40
}
Write-Output 'S5 preconditions: clear'

$record = Get-Content -LiteralPath "$rc/build-record.json" -Raw | ConvertFrom-Json
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $installer).Hash.ToLowerInvariant()
if ($actual -ne $record.installer.sha256) {
    Write-Output "S8: installer is $actual, the build record says $($record.installer.sha256)"
    exit 41
}
Write-Output "installer matches the build record: $actual"

if (Test-Path -LiteralPath $throwawayAppData) {
    Remove-Item -LiteralPath $throwawayAppData -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $throwawayAppData | Out-Null
# Set before the installer runs, so anything it might launch stays off the real app data too.
$env:AVKIT_APP_DATA = $throwawayAppData

$before = Get-Snapshot 'before'

Write-Output '== install'
$setup = Start-Process -FilePath (Resolve-Path -LiteralPath $installer).Path -ArgumentList '/S', "/D=$target" -PassThru
$null = $setup.Handle
if (-not $setup.WaitForExit($installTimeoutMs)) {
    Write-Output "install: still running after $installTimeoutMs ms; left for inspection"
    exit 42
}
Write-Output "== install exit=$($setup.ExitCode)"

$entries = @(Get-AvkitUninstallEntries)
if ($setup.ExitCode -ne 0 -or $entries.Count -ne 1) {
    Write-Output "install: exit $($setup.ExitCode), $($entries.Count) Uninstall entries; left for inspection"
    exit 42
}
$entry = $entries[0]
$uninstallString = $entry.GetValue('UninstallString')
$uninstaller = if ($uninstallString -match '^"([^"]+)"') { $Matches[1] } else { $null }
$location = if ($uninstaller) { Split-Path -Parent $uninstaller } else { $null }
if (-not $location -or -not (Test-Path -LiteralPath $location)) {
    Write-Output "install: no install location in UninstallString: $uninstallString"
    exit 42
}
Write-Output "Uninstall entry: $($entry.PSChildName) version $($entry.GetValue('DisplayVersion'))"
Write-Output "real location: $location (/D honoured: $($location -ieq $target))"
$installKey = "HKCU:\Software\$($entry.PSChildName)"
Write-Output "install key $installKey present: $(Test-Path -LiteralPath $installKey)"

$installed = Get-Snapshot 'installed'
Write-Output "shortcuts added: desktop [$(@($installed.desktop | Where-Object { $before.desktop -notcontains $_ }) -join ', ')], start menu [$(@($installed.start_menu | Where-Object { $before.start_menu -notcontains $_ }) -join ', ')]"

$firstFailure = 0

# A silent install must not start the app; the check after the smokes needs a clean start too.
Write-Output "processes running after the silent install: $(@(Get-InstalledProcesses $location).Count)"
Stop-InstalledProcesses $location

Write-Output '== install-root smoke'
uv run --frozen python tools/smoke_packaged_rc.py --install-root $location --negative-control $negativeControl --out "$rc/smoke-installed.json"
$code = $LASTEXITCODE
Write-Output "== install-root smoke exit=$code"
if ($code -ne 0 -and $firstFailure -eq 0) { $firstFailure = 44 }

Write-Output '== app smoke'
node "$plan/packaged-app-smoke.mjs" $location "$rc/installed-app.json" "$rc/installed-app.png"
$code = $LASTEXITCODE
Write-Output "== app smoke exit=$code"
if ($code -ne 0 -and $firstFailure -eq 0) { $firstFailure = 45 }

# The app's quit path stops its backend, so nothing should outlive the app. Give it time, then treat
# a survivor as a failure: stopping it quietly would hide a real leak from anyone who installs this.
$quitDeadline = (Get-Date).AddSeconds($quitTimeoutS)
while (@(Get-InstalledProcesses $location).Count -gt 0 -and (Get-Date) -lt $quitDeadline) {
    Start-Sleep -Seconds 1
}
$survivors = @(Get-InstalledProcesses $location)
Write-Output "processes from the install $quitTimeoutS s after the app closed: $($survivors.Count)"
if ($survivors.Count -gt 0) {
    $survivors | ForEach-Object { Write-Output "survivor: $($_.Name) ($($_.Id))" }
    Stop-InstalledProcesses $location
    if ($firstFailure -eq 0) { $firstFailure = 45 }
}

Write-Output '== uninstall'
$remove = Start-Process -FilePath $uninstaller -ArgumentList '/currentuser', '/S' -PassThru
$null = $remove.Handle
if ($remove.WaitForExit($uninstallTimeoutS * 1000)) { Write-Output "uninstaller exit=$($remove.ExitCode)" }
else { Write-Output "uninstaller still running after $uninstallTimeoutS s" }
# NSIS relaunches the uninstaller from a temp copy and the first process exits at once, so the
# first exit says nothing: wait for the copy to finish and for what it removes to go.
$deadline = (Get-Date).AddSeconds($uninstallTimeoutS)
$copySeen = $false
do {
    Start-Sleep -Seconds 2
    $copies = @(Get-Process | Where-Object {
            $path = $null
            try { $path = $_.Path } catch { }
            $path -and $path -like '*\~nsu*'
        })
    if ($copies.Count -gt 0) { $copySeen = $true }
    $waiting = $copies.Count -gt 0 -or (Test-Path -LiteralPath $location) -or @(Get-AvkitUninstallEntries).Count -gt 0
} while ($waiting -and (Get-Date) -lt $deadline)
Write-Output "== uninstall finished: relaunched copy seen: $copySeen; still waiting at the deadline: $waiting"

$after = Get-Snapshot 'after'
$left = @()
foreach ($section in $before.Keys) {
    $added = @($installed[$section] | Where-Object { $before[$section] -notcontains $_ })
    $gained = @($after[$section] | Where-Object { $before[$section] -notcontains $_ })
    $lost = @($before[$section] | Where-Object { $after[$section] -notcontains $_ })
    Write-Output "$section : install added [$($added -join ', ')]; after uninstall, new [$($gained -join ', ')], lost [$($lost -join ', ')]"
    $ours = @($gained | Where-Object { $added -contains $_ -or $_ -match $ourNames -or $section -eq 'app_data' })
    if ($ours.Count -gt 0) { $left += "$section left behind: $($ours -join ', ')" }
    if ($lost.Count -gt 0 -and $section -eq 'app_data') { $left += "app_data lost: $($lost -join ', ')" }
}
if (Test-Path -LiteralPath $location) { $left += "install folder still exists: $location" }
if (Test-Path -LiteralPath $installKey) { $left += "install key still exists: $installKey" }
if (@(Get-AvkitUninstallEntries).Count -gt 0) { $left += 'Uninstall entry still exists' }
foreach ($key in $runKey, $approvedKey) {
    if ((Get-ValueNames $key) -contains $appId) { $left += "$key still has a $appId value" }
}
if ($left.Count -gt 0) {
    $left | ForEach-Object { Write-Output "S6: $_" }
    if ($firstFailure -eq 0) { $firstFailure = 46 }
}
else {
    Write-Output 'S6: nothing left behind, and the app data keeps the same top-level entries'
}

Write-Output "install-roundtrip: exit $firstFailure"
exit $firstFailure
