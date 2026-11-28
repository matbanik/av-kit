$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
# host-prepare.ps1 -RunId -Stage: verify, extract, build or check the staleness of a run's tree.
$Allowed = @('runid', 'stage')
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

function AvZipComment([string]$path) {
    $fs = [IO.File]::OpenRead($path)
    try {
        $len = [int][Math]::Min($fs.Length, 65557)
        [void]$fs.Seek(-$len, [IO.SeekOrigin]::End)
        $buf = New-Object byte[] $len
        $got = 0
        while ($got -lt $len) {
            $n = $fs.Read($buf, $got, $len - $got)
            if ($n -le 0) { break }
            $got += $n
        }
    } finally {
        $fs.Close()
    }
    for ($j = $len - 22; $j -ge 0; $j--) {
        if ($buf[$j] -eq 0x50 -and $buf[$j + 1] -eq 0x4b -and $buf[$j + 2] -eq 5 -and $buf[$j + 3] -eq 6) {
            $clen = [int]$buf[$j + 20] + 256 * [int]$buf[$j + 21]
            if ($j + 22 + $clen -gt $len) { return $null }
            return [Text.Encoding]::ASCII.GetString($buf, $j + 22, $clen)
        }
    }
    return $null
}

function AvStep([int]$n, [string]$step, [string]$exe, [string[]]$argv, [string]$dir, [string]$logs) {
    $log = Join-Path $logs ('build-' + $n + '-' + $step + '.log')
    $err = Join-Path $logs ('build-' + $n + '-' + $step + '.err')
    $p = Start-Process -FilePath $exe -ArgumentList $argv -WorkingDirectory $dir -NoNewWindow -Wait -PassThru -RedirectStandardOutput $log -RedirectStandardError $err
    if (-not $p) { AvRefuse 'build-failed' ($step + ' did not start') 1 }
    if ($p.ExitCode -ne 0) { AvRefuse 'build-failed' ($step + ' exited ' + $p.ExitCode + '; see logs\build-' + $n + '-' + $step + '.log') 1 }
}

$runId = AvArg 'RunId' $RunIdPattern
$stage = AvArg 'Stage' '^(verify|extract|build|stale)$'
$hj = AvHostJson
$root = [string]$hj.root
$lock = AvReadLock (Join-Path $root 'avkit-remote.lock')
if (-not $lock -or [string]$lock.run_id -cne $runId) {
    $holder = 'none'
    if ($lock) { $holder = [string]$lock.run_id }
    AvRefuse 'host-locked' ('holder=' + $holder) 1
}
$commit = [string]$lock.commit
$rd = Join-Path $root ('runs\' + $runId)
$tree = Join-Path $rd 'tree'
$reqPath = Join-Path $rd 'request.json'

if ($stage -eq 'stale') {
    $why = AvStale $tree $commit
    if ($why) { AvRefuse 'build-stale' $why 1 }
    AvOut ([ordered]@{ reason = 'ok'; stage = $stage }) 0
}

if (-not (Test-Path -LiteralPath $reqPath -PathType Leaf)) { AvRefuse 'request-missing' ('runs\' + $runId + '\request.json') 1 }
$req = $null
try { $req = Get-Content -LiteralPath $reqPath -Raw -ErrorAction Stop | ConvertFrom-Json } catch { $req = $null }
if (-not $req) { AvRefuse 'request-missing' 'request.json is unreadable' 1 }
if ([string]$req.commit -cne $commit) { AvRefuse 'commit-mismatch' ('the request names ' + $req.commit + ', the lock ' + $commit) 1 }
$zip = Join-Path $rd 'src.zip'

if ($stage -eq 'verify') {
    if (-not (Test-Path -LiteralPath $zip -PathType Leaf)) { AvRefuse 'upload-mismatch' 'src.zip is missing' 1 }
    if ((AvHash $zip) -ne [string]$req.zip_sha256) { AvRefuse 'upload-mismatch' 'src.zip' 1 }
    foreach ($prop in @($req.stub.PSObject.Properties)) {
        $f = Join-Path $rd ('publish\' + $prop.Name)
        if (-not (Test-Path -LiteralPath $f -PathType Leaf)) { AvRefuse 'upload-mismatch' ($prop.Name + ' is missing') 1 }
        if ((AvHash $f) -ne [string]$prop.Value) { AvRefuse 'upload-mismatch' $prop.Name 1 }
    }
    # HOST_PAYLOAD (Session 106): each payload entry by name, size and SHA-256.
    if ($null -ne $req.payload) {
        foreach ($e in @($req.payload)) {
            $n = [string]$e.name
            if ($n -notmatch '^[A-Za-z0-9._-]{1,100}$') { AvRefuse 'payload-mismatch' ('a bad payload name ' + $n) 1 }
            $f = Join-Path $rd ('payload\' + $n)
            if (-not (Test-Path -LiteralPath $f -PathType Leaf)) { AvRefuse 'payload-mismatch' ($n + ' is missing') 1 }
            if ((Get-Item -LiteralPath $f).Length -ne [long]$e.size) { AvRefuse 'payload-mismatch' ($n + ' size') 1 }
            if ((AvHash $f) -ne [string]$e.sha256) { AvRefuse 'payload-mismatch' $n 1 }
        }
    }
    $comment = AvZipComment $zip
    if ($comment -cne $commit) { AvRefuse 'commit-mismatch' ('the zip comment is ' + $comment) 1 }
    AvOut ([ordered]@{ reason = 'ok'; stage = $stage }) 0
}

if ($stage -eq 'extract') {
    if (Test-Path -LiteralPath $tree) { AvRefuse 'receipt-exists' ('runs\' + $runId + '\tree exists; a run extracts once') 1 }
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [IO.Compression.ZipFile]::ExtractToDirectory($zip, $tree)
    } catch {
        AvRefuse 'upload-mismatch' ('the extract failed: ' + $_.Exception.Message) 1
    }
    $now = [DateTime]::UtcNow
    $newest = $null
    $files = @(Get-ChildItem -LiteralPath $tree -Recurse -File -Force)
    foreach ($f in $files) {
        if ($null -eq $newest -or $f.LastWriteTimeUtc -gt $newest) { $newest = $f.LastWriteTimeUtc }
    }
    if ($null -eq $newest) { AvRefuse 'upload-mismatch' 'the archive holds no file' 1 }
    $epoch = (New-Object DateTime 1970, 1, 1, 0, 0, 0, ([DateTimeKind]::Utc)).AddSeconds([double]$req.commit_epoch)
    $skew = [int64][Math]::Round(($newest - $now).TotalSeconds)
    $offset = [int64][Math]::Round(($newest - $epoch).TotalSeconds)
    $t = (Get-Date).AddSeconds(-120)
    foreach ($item in @(Get-ChildItem -LiteralPath $tree -Recurse -Force)) { $item.LastWriteTime = $t }
    (Get-Item -LiteralPath $tree).LastWriteTime = $t
    $pub = Join-Path $tree 'native\region-picker-stub\publish'
    New-Item -ItemType Directory -Force -Path $pub | Out-Null
    foreach ($f in @(Get-ChildItem -LiteralPath (Join-Path $rd 'publish') -File)) {
        Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $pub $f.Name) -Force
    }
    [IO.File]::WriteAllText((Join-Path $tree '.avkit-remote-tree'), $commit)
    AvOut ([ordered]@{ reason = 'ok'; stage = $stage; files = $files.Count; mtime_skew_s = $skew; commit_offset_s = $offset }) 0
}

# build
$marker = Join-Path $tree '.avkit-remote-tree'
if (-not (Test-Path -LiteralPath $marker) -or ([string](Get-Content -LiteralPath $marker -Raw)).Trim() -cne $commit) {
    AvRefuse 'commit-mismatch' 'the tree is not this commit; run extract first' 1
}
$logs = Join-Path $rd 'logs'
New-Item -ItemType Directory -Force -Path $logs | Out-Null
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
$nodeExe = [string]$hj.node_exe
$nodeDir = Split-Path -Parent $nodeExe
$env:Path = $nodeDir + ';' + $env:Path
$npm = Join-Path $nodeDir 'npm.cmd'
$uvCmd = Get-Command uv.exe -ErrorAction SilentlyContinue
if (-not $uvCmd) { AvRefuse 'build-failed' 'uv-sync: uv.exe is not on PATH' 1 }
$ui = Join-Path $tree 'ui'
$mcp = Join-Path $tree 'mcp-server'
$outE2e = $tree.Replace('\', '/') + '/ui/out-e2e'
AvStep 1 'uv-sync' $uvCmd.Source @('sync', '--frozen', '--all-packages') $tree $logs
AvStep 2 'ui-npm-ci' $npm @('--prefix', 'ui', 'ci') $tree $logs
AvStep 3 'electron-binary' $nodeExe @('node_modules/electron/install.js') $ui $logs
AvStep 4 'ui-build' $npm @('--prefix', 'ui', 'run', 'build') $tree $logs
$env:AVKIT_PRIMITIVE_HARNESS_BUILD = '1'
AvStep 5 'harness-build' $npm @('--prefix', 'ui', 'run', 'build', '--', '--outDir', $outE2e) $tree $logs
Remove-Item Env:AVKIT_PRIMITIVE_HARNESS_BUILD -ErrorAction SilentlyContinue
AvStep 6 'mcp-npm-ci' $npm @('ci', '--ignore-scripts') $mcp $logs
AvStep 7 'mcp-build' $npm @('run', 'build') $mcp $logs
[IO.File]::WriteAllText((Join-Path $tree '.avkit-remote-build'), $commit)
AvOut ([ordered]@{ reason = 'ok'; stage = $stage; steps = 7 }) 0
