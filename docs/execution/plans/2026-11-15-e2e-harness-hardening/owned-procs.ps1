# Process ownership for this plan's Electron runs (implementation-plan.md AC-10). Dot-sourced by
# e2e-run.ps1, baseline.ps1 and session-gate.ps1; `pwsh -File owned-procs.ps1 -Selftest` runs the
# pure fixtures and touches no real process.
# A run starts its command in a child pwsh (the root) and polls the process table every 500 ms
# while the root runs and once more after it exits. Every process seen is kept in a history by
# pid and creation time with the last time it was seen alive; nothing is ever dropped from it.
# A process is recorded as the run's own only when its parent is proven: the parent's pid and
# creation time are a recorded identity, the child started strictly later, that identity was
# seen alive at or after the child's start (so it still held the pid then), and no other
# identity seen for that pid started between the two. Win32_Process gives only the parent's pid,
# so a child whose parent was last seen before the child started is ambiguous and refused, even
# after a process that reused the pid has exited. The root is pinned: the runner holds its
# handle until after the last snapshot, so Windows cannot give the root's pid to another
# process while the run is watched. A recorded process is never dropped.
# After the run, only a recorded process that is still alive with the same pid and creation
# time, runs this checkout's ui/node_modules/electron/dist binary and started after the script
# did is stopped, and only through a handle: the stop opens the pid, holds that handle (which
# keeps the pid from being reused), checks through it that the start time is the recorded one
# at CIM's microsecond resolution, and kills that one process, never its tree. A candidate that
# has exited, cannot be read or now names another process is listed as not stopped; nothing is
# ever stopped by pid alone. Any other process on that binary started after the script is listed as not
# stopped. An Electron app that Mat or another session starts during the run descends from no
# recorded process and is never stopped.
param([switch]$Selftest)

function Get-Ticks($Time) {
    return ([datetime]$Time).ToUniversalTime().Ticks
}

function Get-ProcKey($Proc) {
    return '{0}|{1}' -f $Proc.ProcessId, (Get-Ticks $Proc.CreationDate)
}

function New-OwnedState {
    # The run's root, recorded and pinned. Keys are strings: CIM gives UInt32 pids.
    param($Root)
    $state = @{ Owned = @{}; Seen = @{}; Pinned = @{} }
    $k = Get-ProcKey $Root
    $state.Owned[$k] = $Root
    $state.Pinned[$k] = $Root
    return $state
}

function Add-Seen([hashtable]$Seen, $Proc, [long]$At) {
    $p = [string]$Proc.ProcessId
    if (-not $Seen.ContainsKey($p)) { $Seen[$p] = @{} }
    $c = [string](Get-Ticks $Proc.CreationDate)
    if (-not $Seen[$p].ContainsKey($c) -or $Seen[$p][$c] -lt $At) { $Seen[$p][$c] = $At }
}

function Test-ProvenChild {
    # Pure: true only when the recorded identity $Parent is the process that started $Child.
    param([hashtable]$Seen, $Parent, $Child)
    if ([string]$Child.ParentProcessId -ne [string]$Parent.ProcessId) { return $false }
    $tp = Get-Ticks $Parent.CreationDate
    $tc = Get-Ticks $Child.CreationDate
    if ($tc -le $tp) { return $false }
    $hist = $Seen[[string]$Parent.ProcessId]
    if ($null -eq $hist) { return $false }
    $last = $hist[[string]$tp]
    if ($null -eq $last -or $last -lt $tc) { return $false }
    foreach ($other in @($hist.Keys)) {
        $t = [long]$other
        if ($t -gt $tp -and $t -le $tc) { return $false }
    }
    return $true
}

function Update-OwnedSet {
    # Pure: records $Snapshot, taken at $At (read before the query), in the history, then adds to
    # the owned set every process of $Snapshot whose parent is proven.
    param([hashtable]$State, [object[]]$Snapshot, [datetime]$At)
    $atTicks = Get-Ticks $At
    foreach ($p in $Snapshot) { Add-Seen $State.Seen $p $atTicks }
    foreach ($p in @($State.Pinned.Values)) { Add-Seen $State.Seen $p $atTicks }
    $changed = $true
    while ($changed) {
        $changed = $false
        foreach ($c in $Snapshot) {
            $k = Get-ProcKey $c
            if ($State.Owned.ContainsKey($k)) { continue }
            foreach ($o in @($State.Owned.Values)) {
                if (Test-ProvenChild -Seen $State.Seen -Parent $o -Child $c) {
                    $State.Owned[$k] = $c
                    $changed = $true
                    break
                }
            }
        }
    }
}

function Test-OnDist($Proc, [string]$Dist, [datetime]$Started) {
    return [bool]($Proc.ExecutablePath -and
        $Proc.ExecutablePath.StartsWith($Dist, [StringComparison]::OrdinalIgnoreCase) -and
        (Get-Ticks $Proc.CreationDate) -ge (Get-Ticks $Started))
}

function Select-OwnedLeftovers {
    # Pure: the live processes of $Snapshot that are in $Owned (same pid and creation time), run
    # an executable under $Dist and started at or after $Started.
    param([hashtable]$Owned, [object[]]$Snapshot, [string]$Dist, [datetime]$Started)
    return @($Snapshot | Where-Object { $Owned.ContainsKey((Get-ProcKey $_)) -and (Test-OnDist $_ $Dist $Started) })
}

function Select-UnprovenElectron {
    # Pure: the processes on $Dist started at or after $Started that are not recorded. Listed only.
    param([hashtable]$Owned, [object[]]$Snapshot, [string]$Dist, [datetime]$Started)
    return @($Snapshot | Where-Object { -not $Owned.ContainsKey((Get-ProcKey $_)) -and (Test-OnDist $_ $Dist $Started) })
}

function Get-ProcSnapshot {
    return @(Get-CimInstance Win32_Process -Property ProcessId, ParentProcessId, CreationDate, ExecutablePath, Name |
            Select-Object ProcessId, ParentProcessId, CreationDate, ExecutablePath, Name)
}

function Invoke-OwnedRun {
    # Runs `rtk proxy @Argv *> $Receipt` in a child pwsh and returns @{ Code; Owned }.
    param([string[]]$Argv, [string]$Receipt)
    $json = ConvertTo-Json -InputObject @($Argv) -Compress
    $quoted = $Receipt.Replace("'", "''")
    $cmd = "`$a = @(ConvertFrom-Json @'`n$json`n'@); & rtk proxy @a *> '$quoted'; exit `$LASTEXITCODE"
    $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
    $child = Start-Process -FilePath 'pwsh' -ArgumentList @('-NoProfile', '-NonInteractive', '-EncodedCommand', $enc) -NoNewWindow -PassThru
    # Holding the handle keeps the root's pid reserved until this function returns.
    $null = $child.Handle
    $at = [datetime]::UtcNow
    $snap = Get-ProcSnapshot
    $root = @($snap | Where-Object { $_.ProcessId -eq $child.Id }) | Select-Object -First 1
    if ($null -eq $root) {
        $root = [pscustomobject]@{ ProcessId = $child.Id; ParentProcessId = $PID; CreationDate = $child.StartTime; ExecutablePath = $null; Name = 'pwsh' }
    }
    $state = New-OwnedState $root
    while ($true) {
        Update-OwnedSet -State $state -Snapshot $snap -At $at
        if ($child.HasExited) { break }
        Start-Sleep -Milliseconds 500
        $at = [datetime]::UtcNow
        $snap = Get-ProcSnapshot
    }
    $at = [datetime]::UtcNow
    $snap = Get-ProcSnapshot
    Update-OwnedSet -State $state -Snapshot $snap -At $at
    $child.WaitForExit()
    return [pscustomobject]@{ Code = $child.ExitCode; Owned = $state.Owned }
}

function Get-MicroTicks([long]$Ticks) {
    # CIM's CreationDate keeps whole microseconds (probe/ctime-res.txt), so a start time read from
    # a handle is compared at that resolution: both values truncated to 10 ticks, then equal.
    return $Ticks - ($Ticks % 10)
}

function Invoke-VerifiedStop {
    # Pure given $Open: opens the candidate's pid through $Open and holds that object's handle,
    # which keeps the pid from being reused; checks through the same object that its start time
    # is the recorded creation time; and kills only that object, never its tree. It never stops a
    # process by pid. Returns 'stopped', 'gone' (exited or unreadable at open, at the start time
    # or at the kill) or 'mismatch' (the pid now belongs to another process).
    param($Candidate, [scriptblock]$Open)
    $p = $null
    try {
        try {
            $p = & $Open $Candidate.ProcessId
            $null = $p.Handle
            $start = $p.StartTime
        } catch { return 'gone' }
        if ($null -eq $p -or $null -eq $start) { return 'gone' }
        if ((Get-MicroTicks (Get-Ticks $start)) -ne (Get-MicroTicks (Get-Ticks $Candidate.CreationDate))) { return 'mismatch' }
        try { $p.Kill($false) } catch { return 'gone' }
        return 'stopped'
    } finally {
        if ($null -ne $p) { $p.Dispose() }
    }
}

$script:OpenProcess = { param($Id) [System.Diagnostics.Process]::GetProcessById([int]$Id) }

function Stop-OwnedElectron {
    param([string]$Label, [hashtable]$Owned, [string]$Dist, [datetime]$Started)
    $snap = Get-ProcSnapshot
    $left = Select-OwnedLeftovers -Owned $Owned -Snapshot $snap -Dist $Dist -Started $Started
    $stopped = 0
    foreach ($p in $left) {
        $outcome = Invoke-VerifiedStop -Candidate $p -Open $script:OpenProcess
        if ($outcome -eq 'stopped') {
            $stopped++
            Write-Output ("{0}: left running pid={1} path={2}; launched by this run, stopped through its verified handle" -f $Label, $p.ProcessId, $p.ExecutablePath)
        } else {
            Write-Output ("{0}: not stopped pid={1} path={2}; {3} at the stop" -f $Label, $p.ProcessId, $p.ExecutablePath, $outcome)
        }
    }
    foreach ($p in (Select-UnprovenElectron -Owned $Owned -Snapshot $snap -Dist $Dist -Started $Started)) {
        Write-Output ("{0}: not stopped pid={1} path={2}; not proven launched by this run" -f $Label, $p.ProcessId, $p.ExecutablePath)
    }
    Write-Output ("{0}: {1} leftover electron.exe launched by this run, {2} stopped ({3} processes recorded)" -f $Label, $left.Count, $stopped, $Owned.Count)
}

if ($Selftest) {
    $t0 = [datetime]'2026-11-15T10:00:00Z'
    $dist = 'P:\av-kit\ui\node_modules\electron\dist\'
    $exe = $dist + 'electron.exe'
    $node = 'C:\node\node.exe'
    $other = 'C:\Other\electron\dist\electron.exe'
    function P([int]$Id, [int]$Parent, [int]$Sec, [string]$Path, [string]$Name = 'x') {
        return [pscustomobject]@{ ProcessId = $Id; ParentProcessId = $Parent; CreationDate = $t0.AddSeconds($Sec); ExecutablePath = $Path; Name = $Name }
    }
    function At([double]$Sec) { return $t0.AddSeconds($Sec) }
    $root = P 100 7 1 'C:\pwsh\pwsh.exe' 'pwsh'
    $tree = @(
        (P 101 100 2 'C:\rtk\rtk.exe'),                  # rtk proxy
        (P 102 101 3 $node),                             # npm, then the Playwright runner
        (P 104 103 5 $exe 'electron.exe'),               # the main process's renderer
        (P 108 103 7 $node)                              # a non-Electron descendant
    )
    $main = P 103 102 4 $exe 'electron.exe'              # the launched main process
    $second = P 105 102 6 $exe 'electron.exe'            # a second launch, exits before snapshot 2
    $strangers = @(
        (P 200 50 5 $exe 'electron.exe'),                # unrelated: same path, started during the run (Mat or another session)
        (P 201 200 6 $exe 'electron.exe'),               # its renderer
        (P 300 50 -10 $exe 'electron.exe'),              # unrelated: same path, running before the script started
        (P 400 77 8 $other 'electron.exe')               # another worktree's app
    )
    $orphan = P 107 103 9 $exe 'electron.exe'            # started while 103 was alive; 103 then exits
    $reuser = P 105 60 12 $exe 'electron.exe'            # unrelated process that reused owned pid 105
    $reuserChild = P 106 105 13 $exe 'electron.exe'      # its child; outlives the reuser
    $late = P 109 103 14 $exe 'electron.exe'             # parent pid 103, started after 103 was last seen
    $rootChild = P 110 100 15 $node                      # the pinned root's child, seen after the root left the table
    # Snapshot 1 at 8.5 s, while the run is going.
    $snap1 = @($root, $main, $second) + $tree + $strangers
    # Snapshot 2 at 10.5 s: 105 has exited; 103 is alive and has started 107.
    $snap2 = @($root, $main, $orphan) + $tree + $strangers
    # Snapshot 3 at 14.5 s: 103 has exited; an unrelated process holds pid 105 and has a child.
    $snap3 = @($root, $orphan, $reuser, $reuserChild, $late) + $tree + $strangers
    # Snapshot 4 at 16.5 s: the reuser has exited and its child survives; the root has exited.
    $snap4 = @($orphan, $reuserChild, $late, $rootChild) + $tree + $strangers
    $failures = 0
    $cases = 0
    function Check([string]$Name, $Got, $Want) {
        $script:cases++
        $g = (@($Got) | Sort-Object) -join ','
        $w = (@($Want) | Sort-Object) -join ','
        if ($g -eq $w) { Write-Output "ok   $Name ($g)" } else { $script:failures++; Write-Output "FAIL $Name got=[$g] want=[$w]" }
    }
    function Ids($Procs) { return @($Procs | ForEach-Object ProcessId) }
    $state = New-OwnedState $root
    Update-OwnedSet -State $state -Snapshot $snap1 -At (At 8.5)
    Check 'snapshot 1 records the session tree only' (Ids $state.Owned.Values) @(100, 101, 102, 103, 104, 105, 108)
    Check 'mid-run: unrelated same-path Electron started during the run is excluded (200, 201)' (Ids (Select-OwnedLeftovers -Owned $state.Owned -Snapshot $snap1 -Dist $dist -Started $t0)) @(103, 104, 105)
    Update-OwnedSet -State $state -Snapshot $snap2 -At (At 10.5)
    Check 'snapshot 2: a child started while its recorded parent was seen alive is recorded (107)' (Ids $state.Owned.Values) @(100, 101, 102, 103, 104, 105, 107, 108)
    Update-OwnedSet -State $state -Snapshot $snap3 -At (At 14.5)
    Check 'snapshot 3: the child of the process that reused pid 105 is refused (106)' (Ids @($state.Owned.Values | Where-Object ProcessId -eq 106)) @()
    Check 'snapshot 3: a child started after its parent was last seen is ambiguous and refused (109)' (Ids @($state.Owned.Values | Where-Object ProcessId -eq 109)) @()
    Update-OwnedSet -State $state -Snapshot $snap4 -At (At 16.5)
    Check 'snapshot 4: after the reuser exits, its surviving child is still refused (106)' (Ids @($state.Owned.Values | Where-Object ProcessId -eq 106)) @()
    Check 'snapshot 4: the pinned root still proves a child seen after it left the table (110)' (Ids @($state.Owned.Values | Where-Object ProcessId -eq 110)) @(110)
    Check 'snapshot 4: recorded processes are kept after they exit (103, 105)' (Ids @($state.Owned.Values | Where-Object { $_.ProcessId -in 103, 105 })) @(103, 105)
    $left = Select-OwnedLeftovers -Owned $state.Owned -Snapshot $snap4 -Dist $dist -Started $t0
    Check 'after the run: the renderer and the orphan; not 106, 109, 200, 201, 300 or 400' (Ids $left) @(104, 107)
    Check 'a recorded descendant on another path is never stopped (108)' (Ids @($left | Where-Object ProcessId -eq 108)) @()
    Check 'after the run: the unproven same-path processes are only listed (106, 109, 200, 201)' (Ids (Select-UnprovenElectron -Owned $state.Owned -Snapshot $snap4 -Dist $dist -Started $t0)) @(106, 109, 200, 201)
    $early = @{}
    $pre = P 500 7 -5 $exe 'electron.exe'
    $early[(Get-ProcKey $pre)] = $pre
    Check 'a recorded process that started before the script is excluded' (Ids (Select-OwnedLeftovers -Owned $early -Snapshot @($pre) -Dist $dist -Started $t0)) @()
    $same = New-OwnedState $root
    Update-OwnedSet -State $same -Snapshot @($root, (P 111 100 1 $exe 'electron.exe')) -At (At 2)
    Check 'a child with the same creation time as its parent is refused (111)' (Ids @($same.Owned.Values | Where-Object ProcessId -eq 111)) @()
    Check 'path match ignores case' (Ids (Select-OwnedLeftovers -Owned $state.Owned -Snapshot @((P 104 103 5 $exe.ToUpper() 'electron.exe')) -Dist $dist -Started $t0)) @(104)
    $oldRule = @($snap1 | Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($dist, [StringComparison]::OrdinalIgnoreCase) -and $_.CreationDate -ge $t0 })
    Check 'negative: the old path-and-time rule would also stop 200 and 201' (Ids $oldRule) @(103, 104, 105, 200, 201)
    # Negative: the round-1 rule checked for a pid reuser in the current snapshot only.
    function Update-CurrentSnapshotOnly([hashtable]$Owned, [object[]]$Snapshot) {
        $changed = $true
        while ($changed) {
            $changed = $false
            foreach ($c in $Snapshot) {
                $k = Get-ProcKey $c
                if ($Owned.ContainsKey($k)) { continue }
                foreach ($o in @($Owned.Values)) {
                    if ($c.ParentProcessId -ne $o.ProcessId -or $c.CreationDate -lt $o.CreationDate) { continue }
                    $r = @($Snapshot | Where-Object { $_.ProcessId -eq $o.ProcessId -and $_.CreationDate -ne $o.CreationDate -and $_.CreationDate -le $c.CreationDate })
                    if ($r.Count -gt 0) { continue }
                    $Owned[$k] = $c
                    $changed = $true
                    break
                }
            }
        }
    }
    $r1 = @{}
    $r1[(Get-ProcKey $root)] = $root
    foreach ($s in @(, $snap1) + @(, $snap2) + @(, $snap3)) { Update-CurrentSnapshotOnly -Owned $r1 -Snapshot $s }
    Check 'negative: the current-snapshot-only rule refuses 106 while the reuser is in the table' (Ids @($r1.Values | Where-Object ProcessId -eq 106)) @()
    Update-CurrentSnapshotOnly -Owned $r1 -Snapshot $snap4
    Check 'negative: the current-snapshot-only rule records 106 once the reuser exits, and 109' (Ids @($r1.Values | Where-Object { $_.ProcessId -in 106, 109 })) @(106, 109)
    # The stop boundary: the candidate is proven from a snapshot, then may exit and its pid be
    # reused before the stop. Each fake stands for the process the pid names at the stop.
    $calls = [System.Collections.Generic.List[string]]::new()
    function Fake([datetime]$Start, [string]$Fail = '') {
        $o = [pscustomobject]@{ Handle = 1; Fail = $Fail; StartUtc = $Start }
        $o | Add-Member -MemberType ScriptProperty -Name StartTime -Value {
            if ($this.Fail -eq 'start') { throw [InvalidOperationException]'exited' }
            $this.StartUtc
        }
        $o | Add-Member -MemberType ScriptMethod -Name Kill -Value {
            param($Tree)
            $calls.Add("kill($Tree)")
            if ($this.Fail -eq 'kill') { throw [InvalidOperationException]'exited' }
        }
        $o | Add-Member -MemberType ScriptMethod -Name Dispose -Value { $calls.Add('dispose') }
        return $o
    }
    function Opener($Target, [switch]$Gone) {
        return { param($Id) if ($Gone) { throw [ArgumentException]"no process $Id" }; $calls.Add("open($Id)"); $Target }.GetNewClosure()
    }
    function StopCase($Candidate, $Open) {
        $calls.Clear()
        $r = Invoke-VerifiedStop -Candidate $Candidate -Open $Open
        return ('{0}|{1}' -f $r, ($calls -join ';'))
    }
    $cand = P 120 103 5 $exe 'electron.exe'
    $start = $t0.AddSeconds(5)
    Check 'stop: the pid now names a replacement started later; refused, no kill' (StopCase $cand (Opener (Fake $start.AddSeconds(5)))) 'mismatch|open(120);dispose'
    Check 'stop: the candidate exited before the open; refused' (StopCase $cand (Opener $null -Gone)) 'gone|'
    Check 'stop: the candidate exited between the open and the start time; refused, handle released' (StopCase $cand (Opener (Fake $start 'start'))) 'gone|open(120);dispose'
    Check 'stop: the verified candidate is killed through its own handle, not its tree' (StopCase $cand (Opener (Fake $start))) 'stopped|open(120);kill(False);dispose'
    Check 'stop: sub-microsecond ticks that CIM drops still match' (StopCase $cand (Opener (Fake $start.AddTicks(7)))) 'stopped|open(120);kill(False);dispose'
    Check 'stop: a start time one microsecond later is a mismatch' (StopCase $cand (Opener (Fake $start.AddTicks(10)))) 'mismatch|open(120);dispose'
    Check 'stop: the candidate exits after the check; the held handle keeps the pid, the kill fails harmlessly' (StopCase $cand (Opener (Fake $start 'kill'))) 'gone|open(120);kill(False);dispose'
    # Negative: a pid-only stop after the snapshot kills whatever holds the pid at that moment.
    $replacement = Fake $start.AddSeconds(5)
    $calls.Clear()
    $p = & (Opener $replacement) $cand.ProcessId
    $p.Kill($true)
    Check 'negative: a pid-only stop would kill the replacement and its tree' ($calls -join ';') 'open(120);kill(True)'
    $src = Get-Content -LiteralPath $PSCommandPath
    $pidStops = @($src | Where-Object { $_ -match ('^[^#]*\b' + 'Stop-' + 'Process\b') })
    Check 'no line of this script stops a process by pid' $pidStops.Count 0
    Write-Output ("owned-procs selftest: {0} of {1} passed" -f ($cases - $failures), $cases)
    if ($failures -gt 0) { exit 1 }
    exit 0
}
