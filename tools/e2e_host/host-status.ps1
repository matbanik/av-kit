$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
# host-status.ps1 -RunId: reports a run's DONE, the lock, the busy checks and the user's processes.
$Allowed = @('runid')
# Staged by tools/e2e_remote.py into <root>\bin\<set>\ beside host.json. Prints one JSON object
# on its last stdout line; exit 0 is ok, 1 a refusal with its reason, 2 usage. It never stops a
# process and never changes the scheduled task.

$RunIdPattern = '^r[0-9]{8}T[0-9]{6}Z-[0-9a-f]{7}$'
$CommitPattern = '^[0-9a-f]{40}$'

function AvOut($o, [int]$code) {
    ConvertTo-Json -InputObject $o -Depth 8 -Compress
    exit $code
}

function AvRefuse([string]$reason, [string]$detail, [int]$code) {
    AvOut ([ordered]@{ reason = $reason; detail = $detail }) $code
}

$avArgs = @{}
$i = 0
while ($i -lt $args.Count) {
    $name = [string]$args[$i]
    if (-not $name.StartsWith('-') -or ($i + 1) -ge $args.Count) {
        AvRefuse 'usage' ('unexpected argument ' + $name) 2
    }
    $avArgs[$name.Substring(1).ToLower()] = [string]$args[$i + 1]
    $i += 2
}
foreach ($k in @($avArgs.Keys)) {
    if ($Allowed -notcontains $k) { AvRefuse 'usage' ('unknown parameter -' + $k) 2 }
}

function AvArg([string]$name, [string]$pattern) {
    $v = [string]$avArgs[$name.ToLower()]
    if (-not ($v -cmatch $pattern)) { AvRefuse 'usage' ('-' + $name + ' must match ' + $pattern) 2 }
    return $v
}

function AvHostJson {
    $h = $null
    try {
        $h = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'host.json') -Raw -ErrorAction Stop | ConvertFrom-Json
    } catch {
        $h = $null
    }
    if (-not $h -or -not $h.root) { AvRefuse 'prerequisite-missing' 'host.json beside the script is missing or unreadable' 1 }
    return $h
}

function AvHash([string]$path) {
    # .NET rather than the hash cmdlet, so a module path inherited from PowerShell 7 cannot matter.
    $sha = [Security.Cryptography.SHA256]::Create()
    $fs = [IO.File]::OpenRead($path)
    try { $h = $sha.ComputeHash($fs) } finally { $fs.Close(); $sha.Dispose() }
    return ([BitConverter]::ToString($h)).Replace('-', '').ToLower()
}

function AvReadLock([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    $l = $null
    try { $l = Get-Content -LiteralPath $path -Raw -ErrorAction Stop | ConvertFrom-Json } catch { $l = $null }
    if (-not $l) { return [ordered]@{ run_id = 'unreadable'; commit = ''; set = ''; created_utc = '' } }
    return $l
}

# begin busy-check
# One copy of the busy, desktop and task checks. host-facts, host-lock, host-start and host-status
# each hold it byte for byte (AC-14), because a bin set has no import path to share it from.
function AvBare($u) {
    if (-not $u) { return '' }
    return ([string]$u).Split('\')[-1].ToLower()
}

function AvScan($hj) {
    $ident = [Security.Principal.WindowsIdentity]::GetCurrent()
    $admin = [Security.Principal.WindowsBuiltInRole]::Administrator
    $elevated = (New-Object Security.Principal.WindowsPrincipal($ident)).IsInRole($admin)
    $owner = @{}
    $start = @{}
    if ($elevated) {
        $gps = @(Get-Process -IncludeUserName -ErrorAction SilentlyContinue)
    } else {
        $gps = @(Get-Process -ErrorAction SilentlyContinue)
    }
    foreach ($gp in $gps) {
        $st = $null
        try { $st = $gp.StartTime } catch { $st = $null }
        if ($st) { $start[[int]$gp.Id] = $st.ToUniversalTime().ToString('o') }
        if ($elevated) {
            if ($gp.UserName) { $owner[[int]$gp.Id] = [string]$gp.UserName }
        } elseif ($st) {
            # Without elevation only this account's own processes open, so they are its own.
            $owner[[int]$gp.Id] = [string]$ident.Name
        }
    }
    $user = ([string]$hj.user).ToLower()
    $busyUsers = @(@($hj.busy_users) | Where-Object { $_ } | ForEach-Object { ([string]$_).ToLower() })
    $testNames = @('node', 'electron', 'python', 'pytest', 'vitest')
    $busy = New-Object System.Collections.ArrayList
    $workers = New-Object System.Collections.ArrayList
    $orphans = New-Object System.Collections.ArrayList
    $mine = New-Object System.Collections.ArrayList
    $explorer = New-Object System.Collections.ArrayList
    $logonui = New-Object System.Collections.ArrayList
    $total = 0
    foreach ($cp in @(Get-CimInstance -ClassName Win32_Process -ErrorAction SilentlyContinue)) {
        $total++
        $id = [int]$cp.ProcessId
        $ppid = [int]$cp.ParentProcessId
        $name = [string]$cp.Name
        if ($name.ToLower().EndsWith('.exe')) { $name = $name.Substring(0, $name.Length - 4) }
        $low = $name.ToLower()
        $who = [string]$owner[$id]
        $bare = AvBare $who
        $created = $start[$id]
        if (-not $created -and $cp.CreationDate) { $created = $cp.CreationDate.ToUniversalTime().ToString('o') }
        if ($bare -and $busyUsers -contains $bare -and $testNames -contains $low) {
            [void]$busy.Add([ordered]@{ user = $who; name = $name; pid = $id })
        }
        if ($low -eq 'runner.worker') { [void]$workers.Add([ordered]@{ user = $who; pid = $id }) }
        if ($user -and $bare -eq $user) {
            [void]$mine.Add([ordered]@{ pid = $id; ppid = $ppid; name = $name; created = $created })
            if ($low -eq 'node' -or $low -eq 'electron') {
                [void]$orphans.Add([ordered]@{ user = $who; name = $name; pid = $id; ppid = $ppid; created = $created })
            }
        }
        if ($low -eq 'explorer') { [void]$explorer.Add([ordered]@{ session = [int]$cp.SessionId; user = $who }) }
        if ($low -eq 'logonui') { [void]$logonui.Add([int]$cp.SessionId) }
    }
    $missing = New-Object System.Collections.ArrayList
    foreach ($bu in @(@($hj.busy_users) | Where-Object { $_ })) {
        $found = $null
        try { $found = Get-LocalUser -Name ([string]$bu) -ErrorAction Stop } catch { $found = $null }
        if (-not $found) { [void]$missing.Add([string]$bu) }
    }
    $session = [ordered]@{ id = $null; state = $null }
    if (Get-Command quser.exe -ErrorAction SilentlyContinue) {
        foreach ($ln in @(quser.exe 2>$null)) {
            if ([string]$ln -match '^\s*>?(\S+)\s+(?:(\S+)\s+)?(\d+)\s+(\S+)') {
                $qn = $Matches[1].ToLower()
                $state = $Matches[4]
                if ($state -eq 'Disc') { $state = 'Disconnected' }
                $same = $qn -eq $user -or ($qn.Length -ge 20 -and $user.StartsWith($qn))
                if ($user -and $same -and ($null -eq $session.id -or ($state -eq 'Active' -and $session.state -ne 'Active'))) {
                    $session.id = [int]$Matches[3]
                    $session.state = $state
                }
            }
        }
    }
    $task = [ordered]@{
        exists = $false; state = $null; principal = $null; logon = $null; runlevel = $null
        action_exe = $null; action_args = $null; limit_min = $null; multiple = $null
    }
    $tp = [string]$hj.task
    $cut = $tp.LastIndexOf('\')
    $sched = $null
    if ($cut -ge 0) {
        $sched = Get-ScheduledTask -TaskPath $tp.Substring(0, $cut + 1) -TaskName $tp.Substring($cut + 1) -ErrorAction SilentlyContinue
    }
    if ($sched) {
        $sched = @($sched)[0]
        $task.exists = $true
        $task.state = [string]$sched.State
        $task.principal = [string]$sched.Principal.UserId
        $task.logon = [string]$sched.Principal.LogonType
        $task.runlevel = [string]$sched.Principal.RunLevel
        $act = @($sched.Actions)[0]
        if ($act) {
            $task.action_exe = [string]$act.Execute
            $task.action_args = [string]$act.Arguments
        }
        $lim = [string]$sched.Settings.ExecutionTimeLimit
        if ($lim) {
            try { $task.limit_min = [int][Xml.XmlConvert]::ToTimeSpan($lim).TotalMinutes } catch { $task.limit_min = $null }
        }
        $task.multiple = [string]$sched.Settings.MultipleInstances
    }
    $lock = AvReadLock (Join-Path ([string]$hj.root) 'avkit-remote.lock')
    return [ordered]@{
        elevated = [bool]$elevated
        procs_total = [int]$total
        owners_seen = [int]$owner.Count
        busy = @($busy)
        own_orphans = @($orphans)
        runner_workers = @($workers)
        busy_users_missing = @($missing)
        explorer = @($explorer)
        logonui_sessions = @($logonui)
        user_session = $session
        task = $task
        lock = $lock
        user_procs = @($mine)
    }
}

function AvBusyCheck($hj, $scan) {
    $items = New-Object System.Collections.ArrayList
    foreach ($b in @($scan.busy)) { [void]$items.Add((AvBare $b.user) + ' ' + $b.name + ' ' + $b.pid) }
    foreach ($w in @($scan.runner_workers)) { [void]$items.Add('Runner.Worker ' + (AvBare $w.user) + ' ' + $w.pid) }
    foreach ($o in @($scan.own_orphans)) { [void]$items.Add('orphan ' + (AvBare $o.user) + ' ' + $o.name + ' ' + $o.pid) }
    if ($items.Count -gt 0) { return [ordered]@{ reason = 'host-busy'; detail = ($items -join '; ') } }
    $want = @(@($hj.busy_users) | Where-Object { $_ })
    if ($want.Count -gt 0 -and (-not $scan.elevated -or $scan.owners_seen -eq 0)) {
        return [ordered]@{ reason = 'host-busy-unknown'; detail = 'process owners are hidden from this session' }
    }
    return $null
}

function AvDesktopCheck($hj, $scan) {
    $user = ([string]$hj.user).ToLower()
    $mine = @(@($scan.explorer) | Where-Object { (AvBare $_.user) -eq $user -and $_.session -ne 0 })
    if ($mine.Count -eq 0 -or $scan.user_session.state -ne 'Active') {
        $d = 'explorer of the user outside session 0: ' + $mine.Count + '; session ' + $scan.user_session.id + ' ' + $scan.user_session.state
        return [ordered]@{ reason = 'no-desktop-session'; detail = $d }
    }
    if ($null -ne $scan.user_session.id -and @($scan.logonui_sessions) -contains $scan.user_session.id) {
        return [ordered]@{ reason = 'desktop-locked'; detail = ('LogonUI runs in session ' + $scan.user_session.id) }
    }
    return $null
}
# end busy-check

$runId = AvArg 'RunId' $RunIdPattern
$hj = AvHostJson
$root = [string]$hj.root
$scan = AvScan $hj
$res = Join-Path $root ('results\' + $runId)
$done = $null
$dp = Join-Path $res 'DONE'
if (Test-Path -LiteralPath $dp -PathType Leaf) {
    $txt = ([string](Get-Content -LiteralPath $dp -Raw)).Trim()
    if ($txt -match '^-?[0-9]+$') { $done = [int]$txt }
}
$pidFile = $null
$pp = Join-Path $res 'pid.txt'
if (Test-Path -LiteralPath $pp -PathType Leaf) {
    $lines = @(Get-Content -LiteralPath $pp)
    if ($lines.Count -ge 2 -and ([string]$lines[0]).Trim() -match '^[0-9]+$') {
        $pidFile = [ordered]@{ pid = [int]([string]$lines[0]).Trim(); start = ([string]$lines[1]).Trim() }
    }
}
$last = $null
if ($scan.task.exists) {
    $tp = [string]$hj.task
    $cut = $tp.LastIndexOf('\')
    $info = Get-ScheduledTaskInfo -TaskPath $tp.Substring(0, $cut + 1) -TaskName $tp.Substring($cut + 1) -ErrorAction SilentlyContinue
    if ($info) { $last = [int64]$info.LastTaskResult }
}
$o = [ordered]@{
    reason = 'ok'
    run_id = $runId
    done = $done
    task = [ordered]@{ exists = $scan.task.exists; state = $scan.task.state; last_result = $last }
    lock = $scan.lock
    elevated = $scan.elevated
    owners_seen = $scan.owners_seen
    user_session = $scan.user_session
    logonui_sessions = @($scan.logonui_sessions)
    busy = @($scan.busy)
    runner_workers = @($scan.runner_workers)
    own_orphans = @($scan.own_orphans)
    pid_file = $pidFile
    user_procs = @($scan.user_procs)
}
AvOut $o 0
