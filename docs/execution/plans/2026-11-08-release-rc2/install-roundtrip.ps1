# Session 57 NSIS round trip on this PC (task row 5; plan D-463; MEU-114's AC-114.5 to AC-114.9 on
# the full build, D-268; plan stop conditions S5, S6, S8). A copy of Session 49's with RC1's
# build-record check (41) and install-root smoke (44) back: phase B runs tools/smoke_packaged_rc.py
# on the install, then copies its resources\avkit-backend to C:\Temp\av-kit\s57\installed-backend
# for rows 6 and 7 (the installer's copy, D-315, D-332). The precondition also refuses files in
# Programs\av-kit-ui, the folder the installer really uses (INSTALL-FOLDER-NAME-MISMATCH).
# Phases: A installs and uninstalls RC1 (the negative control: RC1's uninstall must leave the copy);
# B installs the new installer fresh; C installs it over RC1; D installs it over itself. B to D
# launch the app and must leave neither the copy nor its folder after their uninstall.
# Snapshots hold names only; the real app data's contents are never read, and every install and
# launch runs on a throwaway AVKIT_APP_DATA. A failing smoke still uninstalls; a failing phase stops
# the run after its uninstall. The run deletes %LOCALAPPDATA%\av-kit-ui-updater, whose only allowed
# pre-state is RC1's own copy (row 0 keeps that file as RC1_INSTALLER).
# Exit: 40 an S5 precondition, 41 the new installer differs from the build record (S8), 42 an
# install failed, 44 the install-root smoke or the backend copy failed, 45 an app smoke failed,
# 46 an uninstall left something behind or changed the app data (S6), 47 an MEU-114 check failed.
# The first failure's code is the exit code.
param(
    [Parameter(Mandatory)][string]$NewInstaller,
    [Parameter(Mandatory)][string]$OldInstaller,
    [Parameter(Mandatory)][string]$OutDir,
    [Parameter(Mandatory)][string]$BuildRecord,
    [switch]$PreconditionsOnly
)
$ErrorActionPreference = 'Stop'
$env:ELECTRON_RUN_AS_NODE = $null

$root = (git rev-parse --show-toplevel).Trim()
Set-Location -LiteralPath $root

$rc2 = 'C:\Temp\av-kit\s57'
$plan = 'docs/execution/plans/2026-11-08-release-rc2'
$negativeControl = 'C:/Temp/av-kit/rc1/negative-control/avkit-backend.exe'
$installedBackend = 'C:\Temp\av-kit\s57\installed-backend'
$rc1Sha = 'beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7'
$target = 'C:\Temp\av-kit\s57\install'
$appId = 'com.avkit.app'
$linkName = 'av-kit.lnk'
$ourNames = 'av-?kit|com\.avkit'
$updaterName = 'av-kit-ui-updater'
$copyName = 'installer.exe'
$installTimeoutMs = 600000
$uninstallTimeoutS = 300
$quitTimeoutS = 30

$uninstallRoot = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall'
$runKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$approvedKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run'
$desktop = [Environment]::GetFolderPath('Desktop')
$programs = [Environment]::GetFolderPath('Programs')
$realAppData = Join-Path $env:LOCALAPPDATA 'av-kit'
$roamingData = Join-Path $env:APPDATA 'av-kit-ui'
$updater = Join-Path $env:LOCALAPPDATA $updaterName
$copy = Join-Path $updater $copyName
$defaultInstalls = @(
    (Join-Path $env:LOCALAPPDATA 'Programs\av-kit'),
    (Join-Path $env:LOCALAPPDATA 'Programs\av-kit-ui')
)

# Round-1 F5: the receipt names the home folder `<HOME>`, never its expanded path, in the plain,
# JSON-escaped and forward-slash forms the smoke tool and the paths above can print.
$homeDir = $env:USERPROFILE.TrimEnd('\')
$homeForms = @($homeDir.Replace('\', '\\'), $homeDir, $homeDir.Replace('\', '/')) | ForEach-Object { [regex]::Escape($_) }
$homePattern = '(?i)' + ($homeForms -join '|')
# Straight to stdout: inside a function, Write-Output would become the function's return value.
function Log([string]$Message) { [Console]::Out.WriteLine(($Message -replace $homePattern, '<HOME>')) }

function Get-Sha([string]$Path) { (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant() }

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

# The updater folder stays out of local_folders: RC1's S6 loop only flags what was gained, so it
# can't see this bug. The phases check the copy and its folder explicitly instead.
function Get-Snapshot([string]$Label) {
    $snapshot = [ordered]@{
        uninstall        = @(Get-ChildNames $uninstallRoot)
        run              = @(Get-ValueNames $runKey)
        startup_approved = @(Get-ValueNames $approvedKey)
        desktop          = @(Get-LinkNames $desktop)
        start_menu       = @(Get-LinkNames $programs -Recurse)
        app_data         = @(Get-ChildNames $realAppData)
        local_folders    = @(Get-ChildItem -LiteralPath $env:LOCALAPPDATA -Directory -Force -Name -Filter 'av-kit*' | Where-Object { $_ -ne $updaterName } | Sort-Object)
        roaming_folders  = @(Get-ChildItem -LiteralPath $env:APPDATA -Directory -Force -Name -Filter 'av-kit*' | Sort-Object)
    }
    $record = [ordered]@{ updater = @(Get-ChildNames $updater) }
    foreach ($section in $snapshot.Keys) { $record[$section] = $snapshot[$section] }
    $record | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $OutDir "snapshot-$Label.json") -Encoding utf8
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
        Log "still running from the install: $($process.Name) ($($process.Id)); stopping it"
        Stop-Process -Id $process.Id -Force
    }
}

function New-ThrowawayAppData([string]$Label) {
    $folder = Join-Path $OutDir "app-data\$Label"
    if (Test-Path -LiteralPath $folder) { Remove-Item -LiteralPath $folder -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
    $folder
}

function Set-Failure([int]$Code, [string]$Message) {
    Log "FAIL ($Code): $Message"
    if ($script:firstFailure -eq 0) { $script:firstFailure = $Code }
}

function Get-CopyState {
    if (Test-Path -LiteralPath $copy) { "present, sha256 $(Get-Sha $copy)" }
    elseif (Test-Path -LiteralPath $updater) { "absent; folder holds [$((Get-ChildNames $updater) -join ', ')]" }
    else { 'absent, and so is the folder' }
}

# Installs silently into $target. An install that fails is left for inspection: the run stops.
function Install-Avkit([string]$Installer, [string]$Label) {
    # Set before the installer runs, so anything it might launch stays off the real app data too.
    $env:AVKIT_APP_DATA = New-ThrowawayAppData "$Label-install"
    Log "== $Label install: $Installer"
    $setup = Start-Process -FilePath $Installer -ArgumentList '/S', "/D=$target" -PassThru
    $null = $setup.Handle
    if (-not $setup.WaitForExit($installTimeoutMs)) {
        Log "install: still running after $installTimeoutMs ms; left for inspection"
        exit 42
    }
    Log "== $Label install exit=$($setup.ExitCode)"
    $entries = @(Get-AvkitUninstallEntries)
    if ($setup.ExitCode -ne 0 -or $entries.Count -ne 1) {
        Log "install: exit $($setup.ExitCode), $($entries.Count) Uninstall entries; left for inspection"
        exit 42
    }
    $entry = $entries[0]
    $uninstallString = $entry.GetValue('UninstallString')
    $script:uninstaller = if ($uninstallString -match '^"([^"]+)"') { $Matches[1] } else { $null }
    $script:location = if ($script:uninstaller) { Split-Path -Parent $script:uninstaller } else { $null }
    if (-not $script:location -or -not (Test-Path -LiteralPath $script:location)) {
        Log "install: no install location in UninstallString: $uninstallString"
        exit 42
    }
    $script:installKey = "HKCU:\Software\$($entry.PSChildName)"
    Log "Uninstall entry: $($entry.PSChildName) version $($entry.GetValue('DisplayVersion'))"
    Log "real location: $($script:location) (/D honoured: $($script:location -ieq $target))"
    Log "install key $($script:installKey) present: $(Test-Path -LiteralPath $script:installKey)"
    # A silent install must not start the app; the smoke needs a clean start too.
    Log "processes running after the silent install: $(@(Get-InstalledProcesses $script:location).Count)"
    Stop-InstalledProcesses $script:location
    Log "installer copy after the install: $(Get-CopyState)"
}

function Invoke-AppSmoke([string]$Label) {
    $env:AVKIT_APP_DATA = New-ThrowawayAppData "$Label-smoke"
    Log "== $Label app smoke"
    & node "$plan/packaged-app-smoke.mjs" $script:location (Join-Path $OutDir "$Label-app.json") (Join-Path $OutDir "$Label-app.png") |
        ForEach-Object { Log "$_" }
    $code = $LASTEXITCODE
    Log "== $Label app smoke exit=$code"
    if ($code -ne 0) { Set-Failure 45 "$Label app smoke exited $code" }

    # The app's quit path stops its backend, so nothing should outlive the app. A survivor is a
    # failure: stopping it quietly would hide a real leak from anyone who installs this.
    $quitDeadline = (Get-Date).AddSeconds($quitTimeoutS)
    while (@(Get-InstalledProcesses $script:location).Count -gt 0 -and (Get-Date) -lt $quitDeadline) {
        Start-Sleep -Seconds 1
    }
    $survivors = @(Get-InstalledProcesses $script:location)
    Log "processes from the install $quitTimeoutS s after the app closed: $($survivors.Count)"
    if ($survivors.Count -gt 0) {
        $survivors | ForEach-Object { Log "survivor: $($_.Name) ($($_.Id))" }
        Stop-InstalledProcesses $script:location
        Set-Failure 45 "$Label left $($survivors.Count) process(es) running"
    }
}

# Uninstalls with /S and never --delete-app-data, then compares with the phase's first snapshot.
function Uninstall-Avkit([string]$Label, $Before, $Installed) {
    Stop-InstalledProcesses $script:location
    Log "== $Label uninstall"
    $remove = Start-Process -FilePath $script:uninstaller -ArgumentList '/currentuser', '/S' -PassThru
    $null = $remove.Handle
    if ($remove.WaitForExit($uninstallTimeoutS * 1000)) { Log "uninstaller exit=$($remove.ExitCode)" }
    else { Log "uninstaller still running after $uninstallTimeoutS s" }
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
        $waiting = $copies.Count -gt 0 -or (Test-Path -LiteralPath $script:location) -or @(Get-AvkitUninstallEntries).Count -gt 0
    } while ($waiting -and (Get-Date) -lt $deadline)
    Log "== $Label uninstall finished: relaunched copy seen: $copySeen; still waiting at the deadline: $waiting"

    $after = Get-Snapshot "$Label-after"
    $left = @()
    foreach ($section in $Before.Keys) {
        $added = @($Installed[$section] | Where-Object { $Before[$section] -notcontains $_ })
        $gained = @($after[$section] | Where-Object { $Before[$section] -notcontains $_ })
        $lost = @($Before[$section] | Where-Object { $after[$section] -notcontains $_ })
        Log "$section : install added [$($added -join ', ')]; after uninstall, new [$($gained -join ', ')], lost [$($lost -join ', ')]"
        $ours = @($gained | Where-Object { $added -contains $_ -or $_ -match $ourNames -or $section -eq 'app_data' })
        if ($ours.Count -gt 0) { $left += "$section left behind: $($ours -join ', ')" }
        if ($lost.Count -gt 0 -and $section -eq 'app_data') { $left += "app_data lost: $($lost -join ', ')" }
    }
    if (Test-Path -LiteralPath $script:location) { $left += "install folder still exists: $($script:location)" }
    if (Test-Path -LiteralPath $script:installKey) { $left += "install key still exists: $($script:installKey)" }
    if (@(Get-AvkitUninstallEntries).Count -gt 0) { $left += 'Uninstall entry still exists' }
    foreach ($key in $runKey, $approvedKey) {
        if ((Get-ValueNames $key) -contains $appId) { $left += "$key still has a $appId value" }
    }
    if ($left.Count -gt 0) {
        $left | ForEach-Object { Log "S6: $_" }
        Set-Failure 46 "$Label uninstall left something behind or changed the app data"
    }
    else {
        Log "S6 ($Label): nothing left behind, and the app data keeps the same top-level entries"
    }
    # AC-114.7: normal roaming data is never removed.
    if ($script:roamingBefore -and -not (Test-Path -LiteralPath $roamingData)) {
        Set-Failure 47 "AC-114.7 ${Label}: $roamingData is gone"
    }
    Log "installer copy after the uninstall: $(Get-CopyState)"
}

# RC1's install-root smoke, then the backend copy rows 6 and 7 start (it outlives the uninstall).
function Invoke-RootSmoke([string]$Label) {
    $env:AVKIT_APP_DATA = New-ThrowawayAppData "$Label-root-smoke"
    Log "== $Label install-root smoke"
    & uv run --frozen python tools/smoke_packaged_rc.py --install-root $script:location --negative-control $negativeControl --out (Join-Path $OutDir "$Label-smoke-installed.json") |
        ForEach-Object { Log "$_" }
    $code = $LASTEXITCODE
    Log "== $Label install-root smoke exit=$code"
    if ($code -ne 0) { Set-Failure 44 "$Label install-root smoke exited $code" }

    $source = Join-Path $script:location 'resources\avkit-backend'
    $dest = Join-Path $installedBackend 'avkit-backend'
    if (Test-Path -LiteralPath $installedBackend) { Remove-Item -LiteralPath $installedBackend -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $installedBackend | Out-Null
    Copy-Item -LiteralPath $source -Destination $dest -Recurse
    $want = @(Get-ChildItem -LiteralPath $source -Recurse -File -Force)
    $got = @(Get-ChildItem -LiteralPath $dest -Recurse -File -Force)
    $wantBytes = ($want | Measure-Object -Property Length -Sum).Sum
    $gotBytes = ($got | Measure-Object -Property Length -Sum).Sum
    Log "backend copy: $($got.Count) of $($want.Count) files, $gotBytes of $wantBytes B, at $dest"
    $exe = Join-Path $dest 'avkit-backend.exe'
    if ($want.Count -eq 0 -or $got.Count -ne $want.Count -or $gotBytes -ne $wantBytes -or -not (Test-Path -LiteralPath $exe)) {
        Set-Failure 44 "$Label backend copy differs from the install"
    }
    elseif ((Get-Sha $exe) -ne (Get-Sha (Join-Path $source 'avkit-backend.exe'))) {
        Set-Failure 44 "$Label backend copy's avkit-backend.exe differs from the install's"
    }
}

function Assert-CopyGone([string]$Label, [string]$Ac) {
    if ((Test-Path -LiteralPath $copy) -or (Test-Path -LiteralPath $updater)) {
        Set-Failure 47 "$Ac ${Label}: the copy or its folder is still there after the uninstall"
    }
    else { Log "$Ac ${Label}: the copy and its folder are gone after the uninstall" }
}

function Stop-IfFailed([string]$Label) {
    if ($script:firstFailure -ne 0) {
        Log "install-roundtrip: stopped after phase $Label; exit $($script:firstFailure)"
        exit $script:firstFailure
    }
    Log "== phase $Label passed"
}

# S5: refuse before anything changes.
$blocked = @()
foreach ($installer in $NewInstaller, $OldInstaller) {
    if (-not (Test-Path -LiteralPath $installer -PathType Leaf)) { $blocked += "S5: missing installer $installer" }
}
foreach ($file in $BuildRecord, $negativeControl) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { $blocked += "S5: missing $file" }
}
$outFull = [IO.Path]::GetFullPath($OutDir)
if (-not $outFull.StartsWith("$rc2\", [StringComparison]::OrdinalIgnoreCase)) { $blocked += "S5: -OutDir must sit under $rc2" }
if ($blocked.Count -eq 0) {
    $oldSha = Get-Sha $OldInstaller
    $newSha = Get-Sha $NewInstaller
    Log "old installer sha256 $oldSha"
    Log "new installer sha256 $newSha"
    if ($oldSha -ne $rc1Sha) { $blocked += "S5: the old installer is not RC1's ($rc1Sha)" }
    if ($newSha -eq $rc1Sha) { $blocked += 'S5: the new installer is RC1 itself' }
}
foreach ($key in $runKey, $approvedKey) {
    if ((Get-ValueNames $key) -contains $appId) { $blocked += "S5: $key has a $appId value" }
}
foreach ($entry in @(Get-AvkitUninstallEntries)) { $blocked += "S5: Uninstall entry exists: $($entry.Name)" }
if (Test-Path -LiteralPath $target) { $blocked += "S5: $target already exists" }
foreach ($folder in $defaultInstalls) {
    if ((Get-ChildNames $folder).Count -gt 0) { $blocked += "S5: $folder holds files" }
}
$linkPattern = "(^|\\)$([regex]::Escape($linkName))$"
if ((Get-LinkNames $desktop) -match $linkPattern) { $blocked += "S5: $linkName exists on the Desktop" }
if ((Get-LinkNames $programs -Recurse) -match $linkPattern) { $blocked += "S5: $linkName exists in the Start Menu" }
if (Get-Process -Name 'av-kit' -ErrorAction SilentlyContinue) { $blocked += 'S5: av-kit.exe is running' }
# Pre-state: the updater folder is absent, or holds only RC1's own copy.
$updaterNames = @(Get-ChildNames $updater)
if ($updaterNames.Count -gt 0) {
    if ($updaterNames.Count -ne 1 -or $updaterNames[0] -ne $copyName) {
        $blocked += "S5: $updater holds [$($updaterNames -join ', ')], not only $copyName"
    }
    elseif ((Get-Sha $copy) -ne $rc1Sha) { $blocked += "S5: $copy is not RC1's installer" }
}
Log "pre-state: $updater $(if (Test-Path -LiteralPath $updater) { "holds [$($updaterNames -join ', ')]" } else { 'is absent' })"
if ($blocked.Count -gt 0) {
    $blocked | ForEach-Object { Log $_ }
    exit 40
}
Log 'S5 preconditions: clear'
$record = Get-Content -LiteralPath $BuildRecord -Raw | ConvertFrom-Json
if ($newSha -ne $record.installer.sha256) {
    Log "S8: the new installer is $newSha, the build record says $($record.installer.sha256)"
    exit 41
}
Log "the new installer matches the build record: $newSha"
if ($PreconditionsOnly) {
    Log 'preconditions only: nothing was installed or removed'
    exit 0
}

if (Test-Path -LiteralPath $OutDir) { Remove-Item -LiteralPath $OutDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$NewInstaller = (Resolve-Path -LiteralPath $NewInstaller).Path
$OldInstaller = (Resolve-Path -LiteralPath $OldInstaller).Path
$script:firstFailure = 0
$script:roamingBefore = Test-Path -LiteralPath $roamingData
Log "$roamingData present before the run: $($script:roamingBefore)"

# A, the negative control: RC1's uninstall must leave the copy, or the checks below observe nothing.
$before = Get-Snapshot 'A-before'
Install-Avkit $OldInstaller 'A'
$installed = Get-Snapshot 'A-installed'
Uninstall-Avkit 'A' $before $installed
if (Test-Path -LiteralPath $copy) { Log "AC-114.5 A: RC1's uninstall left the copy, so the check can see the bug" }
else { Set-Failure 47 "AC-114.5 A: the copy is gone after RC1's uninstall, so the check observes nothing" }
Stop-IfFailed 'A'

# B, fresh new: the copy is there after the install, and the uninstall removes it and its folder.
$before = Get-Snapshot 'B-before'
Install-Avkit $NewInstaller 'B'
if (-not (Test-Path -LiteralPath $copy)) { Set-Failure 47 'AC-114.6 B: no copy after the install' }
$installed = Get-Snapshot 'B-installed'
Invoke-RootSmoke 'B'
Invoke-AppSmoke 'B'
Uninstall-Avkit 'B' $before $installed
Assert-CopyGone 'B' 'AC-114.6'
Stop-IfFailed 'B'

# C, upgrade: RC1, then the new installer over it. NSIS runs RC1's uninstaller with --updated.
$before = Get-Snapshot 'C-before'
Install-Avkit $OldInstaller 'C-old'
Install-Avkit $NewInstaller 'C-new'
$installed = Get-Snapshot 'C-installed'
Invoke-AppSmoke 'C'
Uninstall-Avkit 'C' $before $installed
Assert-CopyGone 'C' 'AC-114.8'
Stop-IfFailed 'C'

# D, install over: the new installer twice. The second install must still leave its copy.
$before = Get-Snapshot 'D-before'
Install-Avkit $NewInstaller 'D-first'
Install-Avkit $NewInstaller 'D-second'
if (-not (Test-Path -LiteralPath $copy)) { Set-Failure 47 'AC-114.9 D: no copy after the second install' }
$installed = Get-Snapshot 'D-installed'
Invoke-AppSmoke 'D'
Uninstall-Avkit 'D' $before $installed
Assert-CopyGone 'D' 'AC-114.9'
Stop-IfFailed 'D'

Log 'install-roundtrip: exit 0'
exit 0
