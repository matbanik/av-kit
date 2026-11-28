# Session 106 build (docs/execution/plans/2026-11-26-app-auto-update, rows 3 and 16). A copy of
# 2026-11-22-release-rc5/build-rc5.ps1, step for step: the offline guard, the build inputs, the
# cached FFmpeg and Deno, tools/package_backend.py, dist:prep, the licence list, the pack and the
# resources check. It differs in three ways: it writes no build record, it never names a release
# version (the installer name comes from the extracted ui/package.json), and its pack step depends
# on -Mode. It builds in C:/Temp/av-kit/s106-src, a clone (--shared, no ref change in P:/av-kit)
# checked out detached at the snapshot commit that -Snapshot names; build-identity.py needs git.
#
#   -Mode product -Snapshot <snapshot json>   the committed config; output s106-out/product, the
#                                             three FEED_CHECK calls and the canary payload
#   -Mode pair -Snapshot <snapshot json> -Out <json>
#                                             two packs of one prepared tree, 0.0.901 and 0.0.902,
#                                             each from a generated copy of the config whose only
#                                             changes are the generic local feed, the version
#                                             (extraMetadata) and the output folder (D-1576);
#                                             FEED_CHECK --provider generic on 0.0.902 and the
#                                             roundtrip payload
#
# Nothing is published: --publish never, and no step uploads anything. The last line is
# `build-update: <reason> exit=<n>`. Exit = the failing step's own code, 12 for macro-missing, or
# 20 to 29 for this script's other refusals.
param(
    [Parameter(Mandatory = $true)][ValidateSet('product', 'pair')][string]$Mode,
    [Parameter(Mandatory = $true)][string]$Snapshot,
    [string]$Out = ''
)
$ErrorActionPreference = 'Stop'
$env:ELECTRON_RUN_AS_NODE = $null
$env:AVKIT_FFMPEG_URL = $null
$env:AVKIT_FFMPEG_SHA256 = $null
# offline-guard begin
foreach ($name in 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY') { Set-Item -LiteralPath "env:$name" -Value 'http://127.0.0.1:9' }
$env:NO_PROXY = '127.0.0.1,localhost'
$env:NODE_USE_ENV_PROXY = '1'
$env:ELECTRON_GET_USE_PROXY = 'true'
$env:UV_OFFLINE = '1'
$env:UV_PYTHON_DOWNLOADS = 'never'
$env:npm_config_offline = 'true'
# offline-guard end

$repo = 'P:/av-kit'
$receipts = 'C:/Temp/av-kit/2026-11-26-app-auto-update'
$src = 'C:/Temp/av-kit/s106-src'
$outRoot = 'C:/Temp/av-kit/s106-out'
$tmp = 'C:/Temp/av-kit/s106-tmp'
$payloadRoot = 'C:/Temp/av-kit/s106-payload'
$identity = 'docs/execution/plans/2026-11-08-release-rc2/build-identity.py'
$negativeControl = 'C:/Temp/av-kit/rc1/negative-control/avkit-backend.exe'
$negativeControlSha = '3d5691fc07310ca28c78d8a101fdd84d8b3100d2753605aaee6dd4a19394da87'
$cachedArchive = 'C:/Temp/av-kit/ffmpeg-dl/ffmpeg-pin.zip'
$ffmpegArchive = 'packaging/ffmpeg-win64/ffmpeg-pin.zip'
$cachedDeno = 'C:/Temp/av-kit/deno-dl'
$denoDir = 'packaging/deno-win64'
$sizeLimit = 500000000
$pairVersions = @('0.0.901', '0.0.902')
$feedPort = 47911
$feedUrl = "http://127.0.0.1:$feedPort/"
$row = if ($Mode -eq 'pair') { '16' } else { '3' }

function Stop-Build([string]$Reason, [int]$Code, [string]$Detail = '') {
    if ($Detail) { Write-Output "refused: $Detail" }
    Write-Output "build-update: $Reason exit=$Code"
    exit $Code
}

function Invoke-Step([string]$Name, [scriptblock]$Command) {
    Write-Output "== $Name"
    & $Command
    $code = $LASTEXITCODE
    Write-Output "== $Name exit=$code"
    if ($code -ne 0) { Stop-Build 'step-failed' $code "step $Name exit=$code" }
}

function Get-Sha([string]$Path) {
    (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

# The feed check run from the extracted tree; $Want is the exit it must give.
function Invoke-FeedCheck([string]$Name, [int]$Want, [string[]]$FeedArgs) {
    Write-Output "== feed check $Name (want exit $Want)"
    uv run --frozen python tools/check_update_feed.py @FeedArgs
    $code = $LASTEXITCODE
    Write-Output "== feed check $Name exit=$code"
    if ($code -ne $Want) { Stop-Build 'feed-check-unexpected' 25 "feed check $Name gave $code, not $Want" }
}

# --- the snapshot commit
if (-not (Test-Path -LiteralPath $Snapshot)) { Stop-Build 'usage' 2 "no snapshot receipt $Snapshot" }
if ($Mode -eq 'pair' -and -not $Out) { Stop-Build 'usage' 2 '-Mode pair needs -Out <json>' }
$snap = Get-Content -LiteralPath $Snapshot -Raw | ConvertFrom-Json
$commit = [string]$snap.commit
if ($commit -notmatch '^[0-9a-f]{40}$') { Stop-Build 'usage' 2 "snapshot receipt has no commit id" }
Write-Output "snapshot commit $commit"

if (-not (Test-Path -LiteralPath $negativeControl)) { Stop-Build 'negative-control' 20 "negative control missing: $negativeControl" }
$actual = Get-Sha $negativeControl
if ($actual -ne $negativeControlSha) { Stop-Build 'negative-control' 20 "negative control is $actual, expected $negativeControlSha" }
Write-Output "negative control ok: $actual"

# --- the extracted tree
if (Test-Path -LiteralPath $src) {
    Remove-Item -LiteralPath $src -Recurse -Force
    Write-Output "deleted stale $src"
}
Invoke-Step 'clone' { git clone --quiet --shared --no-checkout $repo $src }
Invoke-Step 'checkout' { git -C $src -c advice.detachedHead=false checkout --quiet --detach $commit }
Set-Location -LiteralPath $src
$head = (git rev-parse HEAD).Trim()
if ($head -ne $commit) { Stop-Build 'checkout-mismatch' 26 "the clone is at $head, not $commit" }

$nsh = 'ui/build/installer.nsh'
if (-not (Select-String -LiteralPath $nsh -SimpleMatch -Quiet -Pattern '!macro customCheckAppRunning')) {
    Stop-Build 'macro-missing' 12 "$nsh in the snapshot has no !macro customCheckAppRunning"
}
$macroRecord = [ordered]@{
    snapshot_commit  = $commit
    blob             = (git rev-parse "HEAD:$nsh").Trim()
    extracted_sha256 = Get-Sha $nsh
    working_sha256   = Get-Sha "$repo/$nsh"
}
$macroRecord | ConvertTo-Json | Set-Content -LiteralPath "$receipts/aau-row$row-macro.json" -Encoding utf8
Write-Output "macro record: $($macroRecord | ConvertTo-Json -Compress)"

$version = (Get-Content -LiteralPath 'ui/package.json' -Raw | ConvertFrom-Json).version
$installerName = "av-kit-Setup-$version.exe"
Write-Output "installer name from ui/package.json: $installerName"

Invoke-Step 'uv sync' { uv sync --frozen --offline --all-packages }
Invoke-Step 'npm ci ui' { npm --prefix ui ci }
Invoke-Step 'npm ci mcp-server' { npm --prefix mcp-server ci }

$line = uv run --frozen python $identity | Select-String -Pattern '^build_inputs [0-9a-f]{64}$'
if ($null -eq $line) { Stop-Build 'build-inputs' 21 'no build_inputs line from the identity tool' }
Write-Output "starting build_inputs $(($line.Line -split ' ')[1])"

# Each mode deletes only its own output and payload, so the other mode's stay (row 7's canary).
$ownStale = if ($Mode -eq 'pair') {
    @($pairVersions | ForEach-Object { "$outRoot/pair-$_" }) + "$payloadRoot/roundtrip"
} else {
    @("$outRoot/product", "$payloadRoot/canary")
}
foreach ($stale in @('ui/dist', 'packaging/build', 'packaging/dist', $tmp) + $ownStale) {
    if (Test-Path -LiteralPath $stale) {
        Remove-Item -LiteralPath $stale -Recurse -Force
        Write-Output "deleted stale $stale"
    }
}

# The folder is gitignored, so a fresh clone has none (D-1563).
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ffmpegArchive) | Out-Null
Copy-Item -LiteralPath $cachedArchive -Destination $ffmpegArchive -Force
Invoke-Step 'ffmpeg' { pwsh -NoProfile -File tools/fetch_ffmpeg_windows.ps1 -ExtractOnly }
New-Item -ItemType Directory -Force -Path $denoDir | Out-Null
Copy-Item -LiteralPath "$cachedDeno/deno-pin.zip" -Destination "$denoDir/deno-pin.zip" -Force
Copy-Item -LiteralPath "$cachedDeno/LICENSE.md" -Destination "$denoDir/LICENSE.md" -Force
Invoke-Step 'deno' { pwsh -NoProfile -File tools/fetch_deno_windows.ps1 -ExtractOnly }
Invoke-Step 'backend' { uv run --frozen python tools/package_backend.py }
Invoke-Step 'dist:prep' { npm --prefix ui run dist:prep }
if ($Mode -ne 'pair') {
    Invoke-Step 'licence list' { uv run --frozen python tools/generate_third_party_licenses.py }
}
else {
    # S7: the list is generated with no problem line.
    Write-Output '== licence list'
    $licOut = @(uv run --frozen python tools/generate_third_party_licenses.py 2>&1 | ForEach-Object { "$_" })
    $code = $LASTEXITCODE
    $licOut | ForEach-Object { Write-Output "  $_" }
    Write-Output "== licence list exit=$code"
    if ($code -ne 0) { Stop-Build 'step-failed' $code "step licence list exit=$code" }
    $licProblems = @($licOut | Where-Object { $_ -match 'problem|unowned|stale build' })
    if ($licProblems.Count -gt 0) { Stop-Build 'licence-problem' 28 "S7: $($licProblems -join ' | ')" }

    $asarList = "$tmp/asar-list.cjs"
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    Set-Content -LiteralPath $asarList -Encoding utf8 -Value @'
const asar = require(require.resolve('@electron/asar', { paths: [process.cwd()] }))
const names = asar.listPackage(process.argv[2]).map((s) => s.replace(/\\/g, '/'))
process.stdout.write(names.includes('/node_modules/electron-updater/package.json') ? 'present' : 'absent')
'@

    $cfgText = Get-Content -LiteralPath 'ui/electron-builder.yml' -Raw
    $publishRe = '(?m)^publish:\r?\n(?:[ \t]+[^\r\n]*\r?\n)+'
    $outputRe = '(?m)^  output: dist(\r?)$'
    if ([regex]::Matches($cfgText, $publishRe).Count -ne 1) { Stop-Build 'pair-config' 27 'ui/electron-builder.yml has no single publish block' }
    if ([regex]::Matches($cfgText, $outputRe).Count -ne 1) { Stop-Build 'pair-config' 27 'ui/electron-builder.yml has no single directories.output: dist' }
    if ($cfgText -match '(?m)^extraMetadata:') { Stop-Build 'pair-config' 27 'ui/electron-builder.yml already has extraMetadata' }

    $record = [ordered]@{ snapshot_commit = $commit; feed_url = $feedUrl; builds = [ordered]@{} }
    $outs = @{}
    foreach ($v in $pairVersions) {
        $cfgName = "electron-builder.pair-$v.yml"
        $gen = [regex]::Replace($cfgText, $publishRe, "publish:`n  - provider: generic`n    url: $feedUrl`n")
        $gen = [regex]::Replace($gen, $outputRe, "  output: dist-pair-$v`$1")
        $gen = $gen.TrimEnd() + "`nextraMetadata:`n  version: $v`n"
        Set-Content -LiteralPath "ui/$cfgName" -Encoding utf8 -NoNewline -Value $gen
        Write-Output "== generated config ui/$cfgName"
        Compare-Object ($cfgText -split '\r?\n') ($gen -split '\r?\n') | ForEach-Object { Write-Output "  $($_.SideIndicator) $($_.InputObject)" }
        Invoke-Step "electron-builder $v" {
            Push-Location ui
            try {
                npx electron-builder --config $cfgName --win nsis --x64 --publish never
            }
            finally {
                Pop-Location
            }
        }
        $o = "$outRoot/pair-$v"
        New-Item -ItemType Directory -Force -Path $outRoot | Out-Null
        Move-Item -LiteralPath "ui/dist-pair-$v" -Destination $o
        $outs[$v] = $o
        Write-Output "output $o"
        $res = "$o/win-unpacked/resources"
        $missing = @(
            'icon.png', 'icon.ico', 'avkit-backend/avkit-backend.exe', 'ffmpeg/ffmpeg.exe', 'ffmpeg/ffprobe.exe',
            'deno/deno.exe', 'deno/LICENSE.md', 'THIRD_PARTY_NOTICES.md', 'THIRD_PARTY_LICENSES.txt', 'LICENSE',
            'mcp-server', 'region-picker', 'app-update.yml'
        ) | Where-Object { -not (Test-Path -LiteralPath "$res/$_") }
        if ($missing.Count -gt 0) { Stop-Build 'resources-missing' 24 "missing from $res`: $($missing -join ', ')" }
        $inst = "$o/av-kit-Setup-$v.exe"
        if (-not (Test-Path -LiteralPath $inst)) { Stop-Build 'installer-missing' 22 "no installer at $inst" }
        $size = (Get-Item -LiteralPath $inst).Length
        $sha = Get-Sha $inst
        Write-Output "installer $v size $size sha256 $sha"
        if ($size -ge $sizeLimit) { Stop-Build 'installer-too-large' 23 "installer $v is $size B, the limit is under $sizeLimit B" }
        $appYml = @(Get-Content -LiteralPath "$res/app-update.yml")
        Write-Output "== app-update.yml $v read back"
        $appYml | ForEach-Object { Write-Output "  $_" }
        if (-not ($appYml -contains 'provider: generic') -or -not ($appYml -contains "url: $feedUrl")) {
            Stop-Build 'feed-config-not-local' 27 "S8: $res/app-update.yml does not name the generic feed $feedUrl"
        }
        Push-Location ui
        try {
            $asarState = (node $asarList "$o/win-unpacked/resources/app.asar" | Out-String).Trim()
        }
        finally {
            Pop-Location
        }
        Write-Output "app.asar $v node_modules/electron-updater/package.json $asarState"
        if ($asarState -ne 'present') { Stop-Build 'asar-missing-updater' 29 "app.asar of $v does not list node_modules/electron-updater/package.json" }
        $record.builds[$v] = [ordered]@{
            installer = "av-kit-Setup-$v.exe"; size = $size; sha256 = $sha; app_update_yml = $appYml; electron_updater_in_asar = $asarState
        }
    }

    $new = $pairVersions[1]
    $old = $pairVersions[0]
    $newOut = $outs[$new]
    Write-Output '== latest.yml 0.0.902'
    Get-Content -LiteralPath "$newOut/latest.yml" | ForEach-Object { Write-Output "  $_" }
    Invoke-FeedCheck 'pair 0.0.902 generic' 0 @('--dist', $newOut, '--version', $new, '--provider', 'generic', '--feed-url', $feedUrl, '--out', "$receipts/aau-feed-pair-16.json")

    # latest-bad.yml: the 0.0.902 feed with both SHA-512 values those of the old installer.
    $shaRe = '(?m)^\s*sha512:\s*(\S+)\s*$'
    $newYml = Get-Content -LiteralPath "$newOut/latest.yml" -Raw
    $newShas = @([regex]::Matches($newYml, $shaRe) | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
    $oldShas = @([regex]::Matches((Get-Content -LiteralPath "$($outs[$old])/latest.yml" -Raw), $shaRe) | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
    if ($newShas.Count -ne 1 -or $oldShas.Count -ne 1 -or $newShas[0] -eq $oldShas[0]) {
        Stop-Build 'bad-feed' 27 "expected one SHA-512 per feed and two different ones: new $($newShas -join ','), old $($oldShas -join ',')"
    }
    $badYml = $newYml.Replace($newShas[0], $oldShas[0])
    $badCount = ([regex]::Matches($badYml, [regex]::Escape($oldShas[0]))).Count
    if ($badCount -ne 2) { Stop-Build 'bad-feed' 27 "latest-bad.yml carries the old SHA-512 $badCount times, not 2" }

    $rt = "$payloadRoot/roundtrip"
    New-Item -ItemType Directory -Force -Path $rt | Out-Null
    Copy-Item -LiteralPath "$($outs[$old])/av-kit-Setup-$old.exe" -Destination "$rt/av-kit-Setup-$old.exe"
    Copy-Item -LiteralPath "$newOut/av-kit-Setup-$new.exe" -Destination "$rt/av-kit-Setup-$new.exe"
    Copy-Item -LiteralPath "$newOut/av-kit-Setup-$new.exe.blockmap" -Destination "$rt/av-kit-Setup-$new.exe.blockmap"
    Copy-Item -LiteralPath "$newOut/latest.yml" -Destination "$rt/latest.yml"
    Set-Content -LiteralPath "$rt/latest-bad.yml" -Encoding utf8 -NoNewline -Value $badYml
    [ordered]@{
        mode            = 'roundtrip'
        old_installer   = "av-kit-Setup-$old.exe"
        new_installer   = "av-kit-Setup-$new.exe"
        old_version     = $old
        new_version     = $new
        feed            = [ordered]@{ latest = 'latest.yml'; bad = 'latest-bad.yml'; blockmap = "av-kit-Setup-$new.exe.blockmap" }
        feed_port       = $feedPort
        snapshot_commit = $commit
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath "$rt/payload.json" -Encoding utf8
    $files = @(Get-ChildItem -LiteralPath $rt | ForEach-Object { [ordered]@{ name = $_.Name; size = $_.Length; sha256 = Get-Sha $_.FullName } })
    $files | ForEach-Object { Write-Output "payload $($_.name) $($_.size) $($_.sha256)" }
    $record.payload = $rt
    $record.payload_files = $files
    $record.licence_problem_lines = 0
    $record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Out -Encoding utf8
    Write-Output "record $Out"
    Write-Output 'build-update: pair-ok exit=0'
    exit 0
}
Invoke-Step 'electron-builder' {
    Push-Location ui
    try {
        npx electron-builder --win nsis --x64 --publish never
    }
    finally {
        Pop-Location
    }
}

# --- the output, moved out of the tree
$out = "$outRoot/product"
New-Item -ItemType Directory -Force -Path $outRoot | Out-Null
Move-Item -LiteralPath 'ui/dist' -Destination $out
Write-Output "output $out"

$resources = "$out/win-unpacked/resources"
$missing = @(
    'icon.png', 'icon.ico', 'avkit-backend/avkit-backend.exe', 'ffmpeg/ffmpeg.exe', 'ffmpeg/ffprobe.exe',
    'deno/deno.exe', 'deno/LICENSE.md', 'THIRD_PARTY_NOTICES.md', 'THIRD_PARTY_LICENSES.txt', 'LICENSE',
    'mcp-server', 'region-picker', 'app-update.yml'
) | Where-Object { -not (Test-Path -LiteralPath "$resources/$_") }
if ($missing.Count -gt 0) { Stop-Build 'resources-missing' 24 "missing from $resources`: $($missing -join ', ')" }
Write-Output 'resources check: every extraResources target and app-update.yml is present'

$installer = "$out/$installerName"
if (-not (Test-Path -LiteralPath $installer)) { Stop-Build 'installer-missing' 22 "no installer at $installer" }
$size = (Get-Item -LiteralPath $installer).Length
Write-Output "installer size $size sha256 $(Get-Sha $installer)"
if ($size -ge $sizeLimit) { Stop-Build 'installer-too-large' 23 "installer is $size B, the limit is under $sizeLimit B" }

Write-Output '== app-update.yml read back'
Get-Content -LiteralPath "$resources/app-update.yml" | ForEach-Object { Write-Output "  $_" }
Write-Output '== latest.yml'
Get-Content -LiteralPath "$out/latest.yml" | ForEach-Object { Write-Output "  $_" }

# --- FEED_CHECK three times: the output, latest.yml moved away, one changed byte
Invoke-FeedCheck 'output' 0 @('--dist', $out, '--version', $version, '--out', "$receipts/aau-feed-real-3.json")

function New-FeedCopy([string]$Name) {
    $dir = "$tmp/$Name"
    New-Item -ItemType Directory -Force -Path "$dir/win-unpacked/resources" | Out-Null
    foreach ($f in $installerName, "$installerName.blockmap", 'latest.yml') {
        Copy-Item -LiteralPath "$out/$f" -Destination "$dir/$f"
    }
    Copy-Item -LiteralPath "$resources/app-update.yml" -Destination "$dir/win-unpacked/resources/app-update.yml"
    $dir
}
$noFeed = New-FeedCopy 'feed-missing'
Move-Item -LiteralPath "$noFeed/latest.yml" -Destination "$noFeed/latest.yml.away"
Invoke-FeedCheck 'latest.yml moved away' 10 @('--dist', $noFeed, '--version', $version)

$flipped = New-FeedCopy 'one-byte'
$stream = [IO.File]::Open("$flipped/$installerName", 'Open', 'ReadWrite')
try {
    $stream.Position = 4096
    $b = $stream.ReadByte()
    $stream.Position = 4096
    $stream.WriteByte(($b -bxor 0xFF))
}
finally {
    $stream.Dispose()
}
Invoke-FeedCheck 'one changed byte' 15 @('--dist', $flipped, '--version', $version)

# --- the canary payload
$canary = "$payloadRoot/canary"
New-Item -ItemType Directory -Force -Path $canary | Out-Null
Copy-Item -LiteralPath $installer -Destination "$canary/$installerName"
[ordered]@{ mode = 'canary'; installer = $installerName; version = $version; snapshot_commit = $commit } |
    ConvertTo-Json | Set-Content -LiteralPath "$canary/payload.json" -Encoding utf8
Get-ChildItem -LiteralPath $canary | ForEach-Object { Write-Output "payload $($_.Name) $($_.Length) $(Get-Sha $_.FullName)" }

Write-Output 'build-update: product-ok exit=0'
exit 0
