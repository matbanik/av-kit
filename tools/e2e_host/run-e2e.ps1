$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
# avkit-remote-launcher
# run-e2e.ps1: the scheduled task's action, run in the signed-in session with no arguments. It
# runs the locked run's suite from runs\<id>\tree\ui and writes only under results\<id>\; DONE is
# written last, through DONE.tmp, so a poll never reads a partial one.

$RunIdPattern = '^r[0-9]{8}T[0-9]{6}Z-[0-9a-f]{7}$'
$root = $PSScriptRoot
$results = Join-Path $root 'results'
$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')

function AvDone([string]$dir, [int]$code, [string]$note) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    if ($note) { Add-Content -LiteralPath (Join-Path $dir 'meta.txt') -Value $note -Encoding ASCII }
    Set-Content -LiteralPath (Join-Path $dir 'DONE.tmp') -Value $code -Encoding ASCII
    Move-Item -LiteralPath (Join-Path $dir 'DONE.tmp') -Destination (Join-Path $dir 'DONE') -Force
    ConvertTo-Json -InputObject ([ordered]@{ reason = 'finished'; exit = $code; note = $note }) -Depth 8 -Compress
    exit $code
}

function AvStale([string]$tree, [string]$commit) {
    # global-setup.ts:40-56 on this tree, plus both markers naming the commit.
    foreach ($m in @('.avkit-remote-tree', '.avkit-remote-build')) {
        $mp = Join-Path $tree $m
        if (-not (Test-Path -LiteralPath $mp)) { return ($m + ' is missing') }
        if (([string](Get-Content -LiteralPath $mp -Raw)).Trim() -cne $commit) { return ($m + ' does not name ' + $commit) }
    }
    $ui = Join-Path $tree 'ui'
    $main = Join-Path $ui 'out\main\index.js'
    $config = Join-Path $ui 'electron.vite.config.ts'
    $html = Join-Path $ui 'out-e2e\renderer\primitive-harness.html'
    $entry = Join-Path $ui 'src\renderer\src\primitive-harness.tsx'
    foreach ($f in @($main, $config, $html, $entry)) {
        if (-not (Test-Path -LiteralPath $f -PathType Leaf)) { return ($f + ' is missing') }
    }
    $built = (Get-Item -LiteralPath $main).LastWriteTimeUtc
    $cfg = (Get-Item -LiteralPath $config).LastWriteTimeUtc
    $newest = $null
    foreach ($f in @(Get-ChildItem -LiteralPath (Join-Path $ui 'src') -Recurse -File -Force)) {
        if ($null -eq $newest -or $f.LastWriteTimeUtc -gt $newest.LastWriteTimeUtc) { $newest = $f }
    }
    if ($newest -and $newest.LastWriteTimeUtc -gt $built) { return ('ui\out\main\index.js is older than ' + $newest.FullName) }
    if ($cfg -gt $built) { return 'ui\out\main\index.js is older than electron.vite.config.ts' }
    $htmlT = (Get-Item -LiteralPath $html).LastWriteTimeUtc
    if ((Get-Item -LiteralPath $entry).LastWriteTimeUtc -gt $htmlT -or $cfg -gt $htmlT) {
        return 'ui\out-e2e\renderer\primitive-harness.html is older than its entry or the config'
    }
    return ''
}

function AvStage([string]$Dir, [string[]]$Specs, [switch]$Gated) {
    # One Playwright stage: its specs, report, logs and pid.txt go to $Dir. Only the gated stage
    # sets the clipboard gate for its own child (D-1282); every call is piped or assigned, so the
    # function returns one int (L3).
    New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    Set-Content -LiteralPath (Join-Path $Dir 'specs.txt') -Value $Specs -Encoding ASCII
    $argv = @('scripts\playwright-with-outputfile.mjs') + $Specs + @('--reporter=json', ('--outputFile=' + (Join-Path $Dir 'report.json')))
    if ($Gated) { $env:AVKIT_E2E_CLIPBOARD_GATED = '1' }
    $p = Start-Process -FilePath $nodeExe -ArgumentList $argv -WorkingDirectory $ui -RedirectStandardOutput (Join-Path $Dir 'run.log') -RedirectStandardError (Join-Path $Dir 'run.err') -NoNewWindow -PassThru
    $env:AVKIT_E2E_CLIPBOARD_GATED = $null
    $null = $p.Handle
    Set-Content -LiteralPath (Join-Path $Dir 'pid.txt') -Value @([string]$p.Id, $p.StartTime.ToUniversalTime().ToString('o')) -Encoding ASCII
    $p.WaitForExit()
    return [int]$p.ExitCode
}

function AvProbeWrite([string]$Path) {
    # A probe that throws or returns nothing is written as undecided-probe-failed.
    $pr = $null
    try { $pr = AvSessionProbe } catch { $pr = $null }
    if ($null -eq $pr -or -not $pr.state) {
        $pr = [ordered]@{ state = 'undecided'; reason = 'undecided-probe-failed'; rustdesk_version = $null; procs = @(); utc = [DateTime]::UtcNow.ToString('o') }
    }
    # A write that fails is logged by name in meta.txt and never stops the run; the missing
    # file then voids the gated stage in the tool (D-1284).
    try {
        Set-Content -LiteralPath $Path -Value (ConvertTo-Json -InputObject $pr -Depth 8 -Compress) -Encoding ASCII -ErrorAction Stop
    } catch {
        Add-Content -LiteralPath (Join-Path (Split-Path -Parent $Path) 'meta.txt') -Value ('probe-write-failed ' + (Split-Path -Leaf $Path)) -Encoding ASCII
    }
    return $pr
}

# begin session-probe
# One copy of the session probe (Session 98, D-1270, D-1271). host-facts, host-status and run-e2e
# each hold it byte for byte. It only reads process, session and file-version state; it returns
# no account, address or folder, and it never changes RustDesk or ends a process.
function AvProbeFacts {
    $f = [ordered]@{ error = $null; procs = @(); service_pid = $null; service_session = $null; rustdesk_version = $null; sessions = @() }
    $all = @()
    try {
        $all = @(Get-CimInstance -ClassName Win32_Process -Filter "Name = 'rustdesk.exe' OR Name = 'rdpclip.exe'" -ErrorAction Stop)
    } catch {
        $f.error = 'processes'
        return $f
    }
    $procs = @()
    foreach ($p in $all) {
        $cl = $p.CommandLine
        $sw = $null
        if ($null -ne $cl) {
            $t = ([string]$cl).Trim()
            if ($t.StartsWith('"')) {
                $i = $t.IndexOf('"', 1)
                if ($i -gt 0) { $t = $t.Substring($i + 1) } else { $t = '' }
            } else {
                $i = $t.IndexOf(' ')
                if ($i -gt 0) { $t = $t.Substring($i) } else { $t = '' }
            }
            $words = @()
            foreach ($w in @($t.Trim() -split '\s+' | Where-Object { $_ })) {
                if ($w -cmatch '^--?[A-Za-z][A-Za-z0-9-]*$') { $words += $w } else { $words += '<arg>' }
            }
            $sw = $words -join ' '
        }
        $started = $null
        if ($p.CreationDate) { $started = ([datetime]$p.CreationDate).ToUniversalTime().ToString('o') }
        $procs += [ordered]@{ name = ([string]$p.Name).ToLower(); pid = [int]$p.ProcessId; ppid = [int]$p.ParentProcessId; session = [int]$p.SessionId; readable = ($null -ne $cl); switches = $sw; started = $started }
    }
    $f.procs = $procs
    try {
        $svc = @(Get-CimInstance -ClassName Win32_Service -Filter "Name = 'RustDesk'" -ErrorAction Stop)
        if ($svc.Count -gt 0 -and [int]$svc[0].ProcessId -gt 0) {
            $f.service_pid = [int]$svc[0].ProcessId
            foreach ($p in $all) {
                if ([int]$p.ProcessId -eq $f.service_pid) { $f.service_session = [int]$p.SessionId }
            }
        }
    } catch {
        $f.error = 'service'
    }
    foreach ($p in $all) {
        if ($null -eq $f.rustdesk_version -and ([string]$p.Name) -eq 'rustdesk.exe' -and $p.ExecutablePath) {
            try { $f.rustdesk_version = [string](Get-Item -LiteralPath $p.ExecutablePath -ErrorAction Stop).VersionInfo.FileVersion } catch { $f.rustdesk_version = $null }
        }
    }
    if (-not (Get-Command qwinsta.exe -ErrorAction SilentlyContinue)) {
        $f.error = 'qwinsta'
        return $f
    }
    $rows = @(qwinsta.exe 2>$null)
    if ($LASTEXITCODE -ne 0) {
        $f.error = 'qwinsta'
        return $f
    }
    $sessions = @()
    foreach ($ln in $rows) {
        $s = [string]$ln
        if ($s.Length -lt 2) { continue }
        if ($s.Substring(1) -match '^(\S*)\s+(?:(\S+)\s+)?(\d+)\s+(\S+)') {
            $n = $Matches[1].ToLower()
            $sid = [int]$Matches[3]
            $st = [string]$Matches[4]
            if ($n -notmatch '^(console|services|rdp-tcp(#\d+)?)$') { $n = '<other>' }
            $sessions += [ordered]@{ name = $n; id = $sid; state = $st }
        }
    }
    $f.sessions = $sessions
    return $f
}

function AvProbeClassify($f) {
    if ($null -ne $f.error -and [string]$f.error -ne '') { return [ordered]@{ state = 'undecided'; reason = 'undecided-probe-failed' } }
    $procs = @(@($f.procs) | Where-Object { $null -ne $_ })
    $rd = @($procs | Where-Object { [string]$_.name -eq 'rustdesk.exe' })
    foreach ($p in $rd) {
        if ($p.readable) {
            $words = @(([string]$p.switches) -split ' ' | Where-Object { $_ })
            if ($words -contains '--cm' -or $words -contains '--cm-no-ui') { return [ordered]@{ state = 'connected'; reason = 'connected-rustdesk-cm' } }
        }
    }
    if (@($procs | Where-Object { [string]$_.name -eq 'rdpclip.exe' }).Count -gt 0) { return [ordered]@{ state = 'connected'; reason = 'connected-rdp' } }
    foreach ($s in @(@($f.sessions) | Where-Object { $null -ne $_ })) {
        if ([string]$s.name -match '^rdp-tcp#\d+$' -and [string]$s.state -eq 'Active') { return [ordered]@{ state = 'connected'; reason = 'connected-rdp' } }
    }
    $svc = -1
    if ($null -ne $f.service_pid -and $null -ne $f.service_session -and [int]$f.service_session -eq 0) { $svc = [int]$f.service_pid }
    foreach ($p in $rd) {
        if (-not $p.readable -and -not ($svc -gt 0 -and ([int]$p.pid -eq $svc -or [int]$p.ppid -eq $svc))) {
            return [ordered]@{ state = 'undecided'; reason = 'undecided-unreadable' }
        }
    }
    foreach ($p in $rd) {
        if ($p.readable -and @('--service', '--server', '--tray') -cnotcontains ([string]$p.switches).Trim()) {
            return [ordered]@{ state = 'undecided'; reason = 'undecided-rustdesk-other' }
        }
    }
    return [ordered]@{ state = 'none'; reason = 'no-remote-session' }
}

function AvSessionProbe {
    $f = $null
    try { $f = AvProbeFacts } catch { $f = [ordered]@{ error = 'probe'; procs = @(); rustdesk_version = $null } }
    $c = AvProbeClassify $f
    $out = @()
    foreach ($p in @(@($f.procs) | Where-Object { $null -ne $_ })) {
        $out += [ordered]@{ name = [string]$p.name; session = $p.session; switches = $p.switches; readable = [bool]$p.readable; started = $p.started }
    }
    return [ordered]@{ state = $c.state; reason = $c.reason; rustdesk_version = $f.rustdesk_version; procs = $out; utc = [DateTime]::UtcNow.ToString('o') }
}
# end session-probe

$lock = $null
$lockPath = Join-Path $root 'avkit-remote.lock'
if (Test-Path -LiteralPath $lockPath) {
    try { $lock = Get-Content -LiteralPath $lockPath -Raw -ErrorAction Stop | ConvertFrom-Json } catch { $lock = $null }
}
$runId = ''
if ($lock) { $runId = [string]$lock.run_id }
if (-not ($runId -cmatch $RunIdPattern)) {
    AvDone (Join-Path $results ('no-lock-' + $stamp)) 95 'refused: no lock names a run'
}
$commit = [string]$lock.commit
$res = Join-Path $results $runId
if (Test-Path -LiteralPath $res) {
    AvDone (Join-Path $results ('dup-' + $stamp)) 95 ('refused: results\' + $runId + ' already exists')
}
New-Item -ItemType Directory -Force -Path $res | Out-Null
$sid = (Get-Process -Id $PID).SessionId
$meta = Join-Path $res 'meta.txt'
$who = $env:USERDOMAIN + '\' + $env:USERNAME
$lines = @(('run_id=' + $runId), ('commit=' + $commit), ('user=' + $who), ('session=' + $sid), ('start=' + [DateTime]::UtcNow.ToString('o')))
Set-Content -LiteralPath $meta -Value $lines -Encoding ASCII

$rd = Join-Path $root ('runs\' + $runId)
$reqPath = Join-Path $rd 'request.json'
if (-not (Test-Path -LiteralPath $reqPath -PathType Leaf)) { AvDone $res 95 'refused: request-missing' }
$req = $null
try { $req = Get-Content -LiteralPath $reqPath -Raw -ErrorAction Stop | ConvertFrom-Json } catch { $req = $null }
if (-not $req) { AvDone $res 95 'refused: request-missing (unreadable)' }
if ([string]$req.commit -cne $commit) { AvDone $res 98 'refused: commit-mismatch (the request is another commit)' }
$tree = Join-Path $rd 'tree'
$tm = Join-Path $tree '.avkit-remote-tree'
if (-not (Test-Path -LiteralPath $tm) -or ([string](Get-Content -LiteralPath $tm -Raw)).Trim() -cne $commit) {
    AvDone $res 98 'refused: commit-mismatch (the tree is not this commit)'
}
$why = AvStale $tree $commit
if ($why) { AvDone $res 99 ('refused: build-stale: ' + $why) }
if ($sid -eq 0) { AvDone $res 96 'refused: no-desktop-session (session 0)' }
$state = ''
if (Get-Command quser.exe -ErrorAction SilentlyContinue) {
    foreach ($ln in @(quser.exe 2>$null)) {
        if ([string]$ln -match '^\s*>?(\S+)\s+(?:(\S+)\s+)?(\d+)\s+(\S+)') {
            if ([int]$Matches[3] -eq $sid) { $state = $Matches[4] }
        }
    }
}
if ($state -ne 'Active') { AvDone $res 96 ('refused: no-desktop-session (session ' + $sid + ' is ' + $state + ')') }
if (@(Get-Process -Name LogonUI -ErrorAction SilentlyContinue | Where-Object { $_.SessionId -eq $sid }).Count -gt 0) {
    AvDone $res 97 'refused: desktop-locked'
}

Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_CLIPBOARD_GATED -ErrorAction SilentlyContinue
$nodeExe = [string]$req.node_exe
$env:Path = (Split-Path -Parent $nodeExe) + ';' + [string]$req.ffmpeg_bin + ';' + $env:Path
$diag = Join-Path $res 'diag'
New-Item -ItemType Directory -Force -Path $diag | Out-Null
$env:AVKIT_E2E_DIAG_DIR = $diag
$ui = Join-Path $tree 'ui'
$skip = @(@($req.skip) | Where-Object { $_ } | ForEach-Object { [string]$_ })
$gatedNames = @(@($req.gated) | Where-Object { $_ } | ForEach-Object { [string]$_ })
$all = @(Get-ChildItem -LiteralPath (Join-Path $ui 'tests\e2e') -File | Where-Object { ($_.Name -like '*.test.ts' -or $_.Name -like '*.spec.ts') -and ($skip -notcontains $_.Name) } | ForEach-Object { $_.Name } | Sort-Object)
$specs = @($all | Where-Object { $gatedNames -notcontains $_ })
$gspecs = @($all | Where-Object { $gatedNames -contains $_ })
Add-Content -LiteralPath $meta -Value ('specs=' + $specs.Count + ' skip=' + ($skip -join ',') + ' gated=' + ($gspecs -join ',')) -Encoding ASCII
Set-Content -LiteralPath (Join-Path $res 'stage.txt') -Value 'main' -Encoding ASCII
$code = AvStage $res $specs
Add-Content -LiteralPath $meta -Value ('exit=' + $code + ' end=' + [DateTime]::UtcNow.ToString('o')) -Encoding ASCII

# The gated stage (D-1269): only when the request names gated files, and only when the probe
# before it reads no remote session. DONE carries the main stage's exit; the tool judges the
# gated stage from its files.
$gatedExit = ''
$before = ''
$after = ''
if ($gspecs.Count -gt 0) {
    $pb = AvProbeWrite (Join-Path $res 'probe-before.json')
    $before = [string]$pb.state + '/' + [string]$pb.reason
    if ([string]$pb.state -eq 'none') {
        Set-Content -LiteralPath (Join-Path $res 'stage.txt') -Value 'gated' -Encoding ASCII
        $gatedExit = AvStage (Join-Path $res 'gated') $gspecs -Gated
        $pa = AvProbeWrite (Join-Path $res 'probe-after.json')
        $after = [string]$pa.state + '/' + [string]$pa.reason
    }
}
Add-Content -LiteralPath $meta -Value @(('gated_exit=' + $gatedExit), ('probe_before=' + $before), ('probe_after=' + $after)) -Encoding ASCII
AvDone $res $code ''
