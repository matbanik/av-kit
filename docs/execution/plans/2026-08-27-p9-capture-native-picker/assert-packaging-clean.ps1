# Sole executable owner of the clean-path packaging oracle (AC-40.10).
#
# Round-1 finding F4: "build:picker" was not reachable from the production packaging entrypoint.
# Round-3 finding N3: the first fix used a SUBSTRING test ("dist" body contains the text
#   "build:picker"), so `dist = "echo build:picker && electron-builder ..."` passed, and the
#   clean rebuild ran `npm run build:picker` directly - never the production `dist` chain.
#
# Contract:
#   1. EXACT SEGMENT composition - splitting the "dist" body on "&&" must yield the exact
#      segment `npm run dist:prep`, and splitting "dist:prep" must yield `npm run build:picker`.
#      A segment that merely CONTAINS the script name (echo, comment, argument) does not count.
#   2. electron-builder maps the publish dir into extraResources.
#   3. Clean-path reproduction runs the PRODUCTION prep segment verbatim
#      (`npm --prefix ui run dist:prep`) from an emptied publish dir and must yield the exe.
#      Only electron-builder itself is skipped - it is the packaging step, not the sidecar build.
#
# Round-11 finding R11-4: the chain above proves the picker is BUILT, not that the package is
# CLEAN. `electron-builder` packages `ui/out` as-is, so a stale Chromium overlay bundle left in
# that directory ships inside the installer even when `ui/src` no longer mentions it. Two
# additions close that:
#   4. `dist:prep` must clean DIST_CLEAN_DIRS before it builds - every segment in
#      PICKER_PREP_REQUIRED_SEGMENTS must appear, in order, so the clean cannot be dropped or
#      run after the builds it was meant to precede. `build:picker` must carry every fragment in
#      PICKER_PUBLISH_REQUIRED_SEGMENTS, which is what pins a self-contained win-x64 publish
#      rather than a framework-dependent one that dies on a machine with no .NET runtime.
#   5. `-Installed` proves the claim where it matters: silent-install the NSIS output to a temp
#      prefix, find the picker at INSTALLED_PICKER_REL, run it, and scan the installed tree for
#      overlay leftovers. Dev-tree path resolution proves nothing about the shipped app.
#
# Round-12 finding R12-3: as written, check 5 could never have run and would not have proved
# what it claimed. Three corrections:
#   6. NSIS_OUTPUT_DIR must equal electron-builder's own `directories.output` resolved against
#      `ui/`. They disagreed (`ui/release` vs `dist`), so -Installed died on "missing
#      NSIS_OUTPUT_DIR" every time, and a stale `ui/release` would have been inspected instead
#      of the real installer.
#   7. The installer must be NEWER than this run's arm stamp. Newest-.exe-in-a-directory says
#      nothing about the build that just finished.
#   8. The INSTALLED ELECTRON APP must resolve the helper through its own
#      `resolvePickerExePath()`, invoked via PICKER_PATH_PROBE_FLAG. Launching the helper
#      directly proves the binary runs; it does not prove `{process.resourcesPath}` resolution
#      in the shipped chain, which is the failure a user actually meets.
param([switch]$SkipBuild, [switch]$SelfTest, [switch]$Installed)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) { Write-Error ('missing NAMED_SETS_FILE ' + $setsPath); exit 1 }
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$buildScript = [string]$sets.PICKER_BUILD_SCRIPT
$prepScript = [string]$sets.PICKER_PREP_SCRIPT
$distScript = [string]$sets.PICKER_DIST_SCRIPT
$distSegment = [string]$sets.PICKER_DIST_REQUIRED_SEGMENT
$prepSegments = @($sets.PICKER_PREP_REQUIRED_SEGMENTS)
$publishFragments = @($sets.PICKER_PUBLISH_REQUIRED_SEGMENTS)
$cleanDirs = @($sets.DIST_CLEAN_DIRS)
$cleanScript = [string]$sets.PICKER_CLEAN_SCRIPT
$globalJson = [string]$sets.GLOBAL_JSON_FILE
$sdkBand = [string]$sets.DOTNET_SDK_BAND
$installedRel = [string]$sets.INSTALLED_PICKER_REL
$nsisDir = [string]$sets.NSIS_OUTPUT_DIR
$overlayToken = [string]$sets.OVERLAY_FORBIDDEN_TOKEN
$overlayNamePattern = [string]$sets.OVERLAY_FORBIDDEN_NAME_PATTERN
$exitError = [int]$sets.PICKER_EXIT_ERROR
$sep = [string]$sets.PICKER_SEGMENT_SEPARATOR
$publishDir = [string]$sets.PICKER_PUBLISH_DIR
$exeRel = [string]$sets.PICKER_EXE_REL
$resFrom = [string]$sets.PICKER_EXTRARESOURCE_FROM
$resTo = [string]$sets.PICKER_EXTRARESOURCE_TO
$builderFile = [string]$sets.ELECTRON_BUILDER_FILE
$probeFlag = [string]$sets.PICKER_PATH_PROBE_FLAG
$probePrefix = [string]$sets.PICKER_PATH_PROBE_PREFIX
$armName = [string]$sets.PACKAGING_INSTALLED_ARM_NAME
. (Join-Path $PSScriptRoot 'lib-disposition.ps1')

# R12-3 (6): electron-builder's `directories.output` is the ONLY authority on where the
# installer lands. Returns the declared value, or $null when absent.
function Get-BuilderOutputDir {
    param([string]$Yaml)
    $lines = @($Yaml -split "`r?`n")
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^\s*directories\s*:\s*$') {
            for ($j = $i + 1; $j -lt $lines.Count; $j++) {
                if ($lines[$j] -match '^\S') { break }          # dedented out of the block
                if ($lines[$j] -match '^\s+output\s*:\s*(\S+)\s*$') {
                    return $Matches[1].Trim('"').Trim("'")
                }
            }
            return $null
        }
    }
    return $null
}

# Compares the configured NSIS_OUTPUT_DIR against that declared value resolved relative to the
# ui/ package. Returns $null when they agree, else the error text.
function Test-NsisOutputDir {
    param([string]$Yaml, [string]$Configured)
    $declared = Get-BuilderOutputDir -Yaml $Yaml
    if ($null -eq $declared) {
        return 'electron-builder config declares no directories.output - NSIS_OUTPUT_DIR cannot be verified against it'
    }
    $expected = ('ui/' + $declared.Trim('/')) -replace '\\', '/'
    $actual = $Configured.Trim('/') -replace '\\', '/'
    if ($expected -ne $actual) {
        return ('NSIS_OUTPUT_DIR is "' + $Configured + '" but electron-builder writes to "' + $expected +
                '" (directories.output: ' + $declared + ') - the installed proof would inspect the wrong directory, or none')
    }
    return $null
}

# R12-3 (8): the installed app prints exactly one PICKER_PATH= line. Returns $null when the
# resolved path is usable, else the error text. Existence is passed in so the check is pure.
function Test-ProbeOutput {
    param([string[]]$Lines, [string]$Prefix, [string]$InstallPrefix, [scriptblock]$Exists)
    $hits = @($Lines | Where-Object { $_ -and $_.StartsWith($Prefix) })
    if ($hits.Count -ne 1) {
        return ('installed app printed ' + $hits.Count + ' "' + $Prefix + '" lines, expected exactly 1 - the probe flag is not wired to the real resolver')
    }
    $resolved = $hits[0].Substring($Prefix.Length).Trim()
    if ([string]::IsNullOrWhiteSpace($resolved)) { return 'installed app resolved an empty picker path' }
    $norm = $resolved -replace '\\', '/'
    $pref = $InstallPrefix -replace '\\', '/'
    if ($norm.ToLowerInvariant().IndexOf($pref.ToLowerInvariant()) -ne 0) {
        return ('installed app resolved "' + $resolved + '", which is outside the install prefix "' + $InstallPrefix +
                '" - the shipped resolver is still pointing at a dev-tree path')
    }
    if (-not (& $Exists $resolved)) {
        return ('installed app resolved "' + $resolved + '", which does not exist - extraResources did not land where the runtime looks')
    }
    return $null
}

function Get-Segments {
    param([string]$Body, [string]$Separator)
    @(($Body -split [regex]::Escape($Separator)) | ForEach-Object { ($_ -replace '\s+', ' ').Trim() })
}

function Test-PackagingScripts {
    param($Scripts)
    $names = @($Scripts.PSObject.Properties.Name)
    foreach ($required in @($buildScript, $prepScript, $distScript)) {
        if ($names -notcontains $required) { return 'ui/package.json has no "' + $required + '" script' }
    }
    $distSegs = Get-Segments -Body ([string]$Scripts.$distScript) -Separator $sep
    if ($distSegs -notcontains $distSegment) {
        return '"' + $distScript + '" has no exact "' + $sep + '"-separated segment "' + $distSegment + '" - a clean package would ship no region picker (segments: ' + ($distSegs -join ' | ') + ')'
    }
    $prepSegs = Get-Segments -Body ([string]$Scripts.$prepScript) -Separator $sep
    $lastAt = -1
    foreach ($required in $prepSegments) {
        $at = [array]::IndexOf($prepSegs, $required)
        if ($at -lt 0) {
            return '"' + $prepScript + '" has no exact "' + $sep + '"-separated segment "' + $required + '" (segments: ' + ($prepSegs -join ' | ') + ')'
        }
        if ($at -lt $lastAt) {
            return '"' + $prepScript + '" runs "' + $required + '" out of order - the clean must precede the builds or it deletes what it just built'
        }
        $lastAt = $at
    }
    $publishBody = [string]$Scripts.$buildScript
    foreach ($frag in $publishFragments) {
        if ($publishBody.IndexOf($frag) -lt 0) {
            return '"' + $buildScript + '" is missing "' + $frag + '" - a framework-dependent or wrong-RID publish will not run on a user machine'
        }
    }
    return $null
}

if ($SelfTest) {
    $goodPrep = ($prepSegments -join ' && ')
    $good = [pscustomobject]@{
        'build:picker' = 'dotnet publish native/region-picker -c Release -r win-x64 --self-contained true -p:PublishSingleFile=false -o native/region-picker/publish'
        'clean:out'    = 'rimraf out ../native/region-picker/publish'
        'build'        = 'electron-vite build'
        'dist:prep'    = $goodPrep
        'dist'         = 'npm run dist:prep && electron-builder --win nsis --x64'
    }
    $err = Test-PackagingScripts -Scripts $good
    if ($null -ne $err) { Write-Error ('SELFTEST valid packaging scripts rejected: ' + $err); exit 1 }

    # P1 - the exact round-3 N3 false-pass: a segment that merely MENTIONS the script name.
    $echoed = [pscustomobject]@{
        'build:picker' = 'dotnet publish native/region-picker -c Release -r win-x64 --self-contained true -p:PublishSingleFile=false -o native/region-picker/publish'
        'dist:prep'    = $goodPrep
        'dist'         = 'echo dist:prep && electron-builder --win nsis --x64'
    }
    if ($null -eq (Test-PackagingScripts -Scripts $echoed)) {
        Write-Error 'SELFTEST P1 "echo dist:prep" accepted - composition test is a substring match'; exit 1
    }

    # P2 - prep script that does not actually invoke the picker build.
    $hollowPrep = [pscustomobject]@{
        'build:picker' = 'dotnet publish native/region-picker -c Release -r win-x64 --self-contained true -p:PublishSingleFile=false -o native/region-picker/publish'
        'dist:prep'    = 'echo build:picker'
        'dist'         = 'npm run dist:prep && electron-builder --win nsis --x64'
    }
    if ($null -eq (Test-PackagingScripts -Scripts $hollowPrep)) {
        Write-Error 'SELFTEST P2 hollow dist:prep accepted'; exit 1
    }

    # P3 - dist does not compose prep at all.
    $uncomposed = [pscustomobject]@{
        'build:picker' = 'dotnet publish native/region-picker -c Release -r win-x64 --self-contained true -p:PublishSingleFile=false -o native/region-picker/publish'
        'dist:prep'    = $goodPrep
        'dist'         = 'electron-builder --win nsis --x64'
    }
    if ($null -eq (Test-PackagingScripts -Scripts $uncomposed)) {
        Write-Error 'SELFTEST P3 uncomposed dist accepted'; exit 1
    }

    # P4 - a required script missing entirely.
    $missing = [pscustomobject]@{ 'dist' = 'npm run dist:prep && electron-builder --win nsis --x64' }
    if ($null -eq (Test-PackagingScripts -Scripts $missing)) {
        Write-Error 'SELFTEST P4 missing build:picker/dist:prep accepted'; exit 1
    }

    # P5 - R11-4 itself: a prep chain that builds without cleaning, so `ui/out` keeps whatever the
    # last Chromium-overlay build left behind and electron-builder packages it.
    $noClean = [pscustomobject]@{
        'build:picker' = 'dotnet publish native/region-picker -c Release -r win-x64 --self-contained true -p:PublishSingleFile=false -o native/region-picker/publish'
        'dist:prep'    = (($prepSegments | Where-Object { $_ -ne ('npm run ' + $cleanScript) }) -join ' && ')
        'dist'         = 'npm run dist:prep && electron-builder --win nsis --x64'
    }
    if ($null -eq (Test-PackagingScripts -Scripts $noClean)) {
        Write-Error 'SELFTEST P5 prep chain with no clean accepted - stale ui/out would ship'; exit 1
    }

    # P6 - clean present but moved to the end, where it deletes what it was meant to precede.
    $lateClean = [pscustomobject]@{
        'build:picker' = 'dotnet publish native/region-picker -c Release -r win-x64 --self-contained true -p:PublishSingleFile=false -o native/region-picker/publish'
        'dist:prep'    = ((@($prepSegments[1..($prepSegments.Count - 1)]) + @($prepSegments[0])) -join ' && ')
        'dist'         = 'npm run dist:prep && electron-builder --win nsis --x64'
    }
    if ($null -eq (Test-PackagingScripts -Scripts $lateClean)) {
        Write-Error 'SELFTEST P6 clean-after-build accepted'; exit 1
    }

    # P7 - framework-dependent publish: builds here, dies on a machine with no .NET runtime.
    $fdd = [pscustomobject]@{
        'build:picker' = 'dotnet publish native/region-picker -c Release -o native/region-picker/publish'
        'dist:prep'    = $goodPrep
        'dist'         = 'npm run dist:prep && electron-builder --win nsis --x64'
    }
    if ($null -eq (Test-PackagingScripts -Scripts $fdd)) {
        Write-Error 'SELFTEST P7 framework-dependent publish accepted'; exit 1
    }

    if ([string]::IsNullOrWhiteSpace($installedRel)) { Write-Error 'SELFTEST INSTALLED_PICKER_REL empty'; exit 1 }
    if ($cleanDirs.Count -lt 1) { Write-Error 'SELFTEST DIST_CLEAN_DIRS empty'; exit 1 }

    # P8 - the exact round-12 defect: NSIS_OUTPUT_DIR naming a directory electron-builder does
    #      not write to. The negative case is the value this plan actually shipped.
    $yamlGood = "appId: com.avkit.app`ndirectories:`n  output: dist`nfiles:`n  - out/**/*`n"
    if ($null -eq (Test-NsisOutputDir -Yaml $yamlGood -Configured 'ui/release')) {
        Write-Error 'SELFTEST P8 a NSIS_OUTPUT_DIR disagreeing with directories.output was accepted'; exit 1
    }
    if ($null -eq (Test-NsisOutputDir -Yaml "appId: x`nfiles:`n  - out/**/*`n" -Configured 'ui/dist')) {
        Write-Error 'SELFTEST P8b an absent directories.output was accepted'; exit 1
    }
    $p8 = Test-NsisOutputDir -Yaml $yamlGood -Configured 'ui/dist'
    if ($null -ne $p8) { Write-Error ('SELFTEST P8c the agreeing pair was rejected: ' + $p8); exit 1 }

    # P9 - the probe must catch a resolver that answers with a dev-tree path, which is exactly
    #      what a hardcoded path or a `process.resourcesPath` mistake produces.
    $yes = { param($p) $true }
    $no = { param($p) $false }
    if ($null -eq (Test-ProbeOutput -Lines @('PICKER_PATH=P:/av-kit/native/region-picker/publish/avkit-region-picker.exe') -Prefix 'PICKER_PATH=' -InstallPrefix 'C:/Temp/prefix' -Exists $yes)) {
        Write-Error 'SELFTEST P9 a resolved path outside the install prefix was accepted'; exit 1
    }
    if ($null -eq (Test-ProbeOutput -Lines @('nothing here') -Prefix 'PICKER_PATH=' -InstallPrefix 'C:/Temp/prefix' -Exists $yes)) {
        Write-Error 'SELFTEST P9b a missing probe line was accepted'; exit 1
    }
    if ($null -eq (Test-ProbeOutput -Lines @('PICKER_PATH=C:/Temp/prefix/resources/region-picker/avkit-region-picker.exe') -Prefix 'PICKER_PATH=' -InstallPrefix 'C:/Temp/prefix' -Exists $no)) {
        Write-Error 'SELFTEST P9c a resolved path that does not exist was accepted'; exit 1
    }
    $p9 = Test-ProbeOutput -Lines @('boot', 'PICKER_PATH=C:/Temp/prefix/resources/region-picker/avkit-region-picker.exe') -Prefix 'PICKER_PATH=' -InstallPrefix 'C:/Temp/prefix' -Exists $yes
    if ($null -ne $p9) { Write-Error ('SELFTEST P9d a correctly resolved path was rejected: ' + $p9); exit 1 }

    # P10 - an installer left over from an earlier build must not satisfy this run.
    $t10 = Join-Path ([System.IO.Path]::GetTempPath()) ('pkg-selftest-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $t10 | Out-Null
    try {
        $inst = Join-Path $t10 'Setup.exe'; $st = Join-Path $t10 'run.stamp'
        'installer' | Set-Content -LiteralPath $inst
        'stamp' | Set-Content -LiteralPath $st
        (Get-Item -LiteralPath $inst).LastWriteTimeUtc = (Get-Item -LiteralPath $st).LastWriteTimeUtc.AddSeconds(-60)
        if ($null -eq (Test-ArtifactFresh -Artifact $inst -Stamp $st)) {
            Write-Error 'SELFTEST P10 an installer predating the arm stamp was accepted as this run''s output'; exit 1
        }
        (Get-Item -LiteralPath $inst).LastWriteTimeUtc = (Get-Item -LiteralPath $st).LastWriteTimeUtc.AddSeconds(5)
        $p10 = Test-ArtifactFresh -Artifact $inst -Stamp $st
        if ($null -ne $p10) { Write-Error ('SELFTEST P10b a freshly built installer was rejected: ' + $p10); exit 1 }
    } finally { Remove-Item -LiteralPath $t10 -Recurse -Force -ErrorAction SilentlyContinue }

    if ([string]::IsNullOrWhiteSpace($probeFlag)) { Write-Error 'SELFTEST PICKER_PATH_PROBE_FLAG empty'; exit 1 }
    if ($null -eq $sets.RUN_STAMPS.$armName) { Write-Error ('SELFTEST RUN_STAMPS has no "' + $armName + '" entry - row 9a cannot arm'); exit 1 }

    'PASS: PACKAGING_CLEAN_PATH self-test (P1 echoed segment, P2 hollow prep, P3 uncomposed dist, P4 missing script, P5 no clean, P6 clean-after-build, P7 framework-dependent publish, P8/P8b NSIS_OUTPUT_DIR disagreeing with or missing directories.output, P9/P9b/P9c a dev-tree, absent or nonexistent resolver answer, P10 a stale installer all rejected; P8c/P9d/P10b the correct shapes accepted)'
    exit 0
}

# 1. package.json: exact-segment composition dist -> dist:prep -> build:picker.
$pkgPath = 'ui/package.json'
if (-not (Test-Path -LiteralPath $pkgPath)) { Write-Error ('missing ' + $pkgPath); exit 1 }
$pkg = Get-Content -LiteralPath $pkgPath -Raw | ConvertFrom-Json
$scripts = $pkg.scripts
$scriptErr = Test-PackagingScripts -Scripts $scripts
if ($null -ne $scriptErr) { Write-Error $scriptErr; exit 1 }
$distBody = [string]$scripts.$distScript

# 2. electron-builder maps the publish output into extraResources.
$builderPath = 'ui/electron-builder.yml'
if (-not (Test-Path -LiteralPath $builderPath)) { Write-Error ('missing ' + $builderPath); exit 1 }
$builder = Get-Content -LiteralPath $builderPath -Raw
if ($builder.IndexOf($resFrom) -lt 0) { Write-Error ('electron-builder.yml missing extraResources from: ' + $resFrom); exit 1 }
if ($builder.IndexOf($resTo) -lt 0) { Write-Error ('electron-builder.yml missing extraResources to: ' + $resTo); exit 1 }
# R12-3 (6): NSIS_OUTPUT_DIR is only meaningful if it is where electron-builder actually writes.
$outErr = Test-NsisOutputDir -Yaml $builder -Configured $nsisDir
if ($null -ne $outErr) { Write-Error $outErr; exit 1 }

# 3. Clean-path reproduction through the PRODUCTION prep segment, not the leaf build script.
if (-not $SkipBuild) {
    if (Test-Path -LiteralPath $publishDir) {
        Remove-Item -LiteralPath $publishDir -Recurse -Force
    }
    if (Test-Path -LiteralPath $exeRel) {
        Write-Error ('clean-path setup failed: ' + $exeRel + ' still present after removing ' + $publishDir)
        exit 1
    }
    npm --prefix ui run $prepScript
    if ($LASTEXITCODE -ne 0) { Write-Error ('"' + $prepScript + '" failed with exit ' + $LASTEXITCODE); exit $LASTEXITCODE }
}
if (-not (Test-Path -LiteralPath $exeRel)) {
    Write-Error ('clean packaging path produced no ' + $exeRel)
    exit 1
}
$exe = Get-Item -LiteralPath $exeRel
[pscustomobject]@{
    distScript   = $distBody
    prepScript   = [string]$scripts.$prepScript
    buildScript  = [string]$scripts.$buildScript
    ranSegment   = ('npm --prefix ui run ' + $prepScript)
    exe          = $exe.FullName
    exeBytes     = $exe.Length
    cleanRebuild = (-not $SkipBuild)
} | ConvertTo-Json -Depth 3
if ($exe.Length -lt 1) { Write-Error 'published exe is empty'; exit 1 }

# 4. SDK pinning: without global.json the sidecar builds against whatever SDK the machine happens
#    to have, and "works on mine" is the only guarantee anyone gets.
if (-not (Test-Path -LiteralPath $globalJson)) { Write-Error ('missing ' + $globalJson + ' - the .NET SDK is unpinned'); exit 1 }
$gj = Get-Content -LiteralPath $globalJson -Raw | ConvertFrom-Json
if (([string]$gj.sdk.version).IndexOf($sdkBand) -ne 0) {
    Write-Error ($globalJson + ' pins sdk.version "' + [string]$gj.sdk.version + '", expected the ' + $sdkBand + 'xx band'); exit 1
}

# 5. -Installed: the only place packaged path resolution and the absence of overlay leftovers can
#    actually be observed. Requires the dist script to have produced an installer first.
if ($Installed) {
    # Generous: an NSIS install of an Electron app plus a self-contained .NET sidecar writes
    # thousands of files, and a slow disk must not read as a packaging defect.
    $installWaitSeconds = 300
    if (-not (Test-Path -LiteralPath $nsisDir)) { Write-Error ('missing NSIS_OUTPUT_DIR ' + $nsisDir + ' - run the dist script first'); exit 1 }
    $installer = @(Get-ChildItem -LiteralPath $nsisDir -Filter '*.exe' -File | Sort-Object LastWriteTime -Descending)
    if ($installer.Count -lt 1) { Write-Error ('no installer .exe in ' + $nsisDir); exit 1 }
    # R12-3 (7): the newest .exe in a directory is not evidence about the build that just ran.
    $armEntry = $sets.RUN_STAMPS.$armName
    if ($null -eq $armEntry) { Write-Error ('RUN_STAMPS has no "' + $armName + '" entry'); exit 1 }
    $freshErr = Test-ArtifactFresh -Artifact $installer[0].FullName -Stamp ([string]$armEntry.stamp)
    if ($null -ne $freshErr) { Write-Error ($freshErr + ' - arm with arm-run.ps1 -Name ' + $armName + ' before running the dist script'); exit 1 }
    $prefix = Join-Path ([System.IO.Path]::GetTempPath()) ('avkit-installed-' + [guid]::NewGuid().ToString('N'))
    try {
        # The one-click NSIS stub hands off to its own child and returns long before the tree is
        # written, so `&` + an immediate Test-Path races the install and reports a correctly
        # packaged helper as missing. Wait for the process, then poll for the artifact under a
        # bounded deadline - a helper that never appears still fails this gate.
        $installProc = Start-Process -FilePath $installer[0].FullName -ArgumentList '/S', ('/D=' + $prefix) -Wait -PassThru
        $installExit = $installProc.ExitCode
        if ($installExit -ne 0) { Write-Error ('silent install failed with exit ' + $installExit); exit 1 }
        $installedExe = Join-Path $prefix $installedRel
        $installDeadline = (Get-Date).AddSeconds($installWaitSeconds)
        while (-not (Test-Path -LiteralPath $installedExe) -and (Get-Date) -lt $installDeadline) {
            Start-Sleep -Milliseconds 500
        }
        if (-not (Test-Path -LiteralPath $installedExe)) {
            Write-Error ('installed app has no region picker at ' + $installedRel + ' - extraResources did not land where the runtime looks')
            exit 1
        }
        # Bogus argv: the helper must refuse deterministically rather than hang or crash, and it
        # must do so from the INSTALLED layout, which is what proves the self-contained publish
        # brought its own runtime.
        # The helper is a WinExe (GUI subsystem): `&` does not wait for it, so $LASTEXITCODE
        # reports the previous command's status instead of the picker's. Start-Process -Wait
        # -PassThru observes the real exit code; -NoNewWindow keeps its stderr in this receipt.
        $argvProc = Start-Process -FilePath $installedExe -ArgumentList '--no-such-flag' -Wait -PassThru -NoNewWindow
        $probeExit = $argvProc.ExitCode
        if ($probeExit -ne $exitError) {
            Write-Error ('installed picker answered bogus argv with exit ' + $probeExit + ', expected PICKER_EXIT_ERROR ' + $exitError)
            exit 1
        }
        # R12-3 (8): the shipped resolver, running under the shipped layout. This is the check
        # that speaks to what a user meets when F2 cannot find the helper.
        $appExe = @(Get-ChildItem -LiteralPath $prefix -Filter '*.exe' -File -ErrorAction SilentlyContinue |
                    Where-Object { $_.Name -notlike 'Uninstall*' } | Sort-Object Length -Descending)
        if ($appExe.Count -lt 1) { Write-Error ('installed prefix ' + $prefix + ' contains no application .exe to probe'); exit 1 }
        $probeOut = @(& $appExe[0].FullName $probeFlag 2>&1 | ForEach-Object { [string]$_ })
        $probeErr = Test-ProbeOutput -Lines $probeOut -Prefix $probePrefix -InstallPrefix $prefix -Exists { param($p) Test-Path -LiteralPath $p }
        if ($null -ne $probeErr) { Write-Error $probeErr; exit 1 }

        # Scope the token scan to the app payload. Electron's own launcher binary embeds the
        # names of every Electron API it exposes, so av-kit.exe contains the literal string
        # whether or not av-kit ever calls it - scanning it asserts something about Electron,
        # not about this app. Everything av-kit ships (app.asar, its unpacked files and every
        # extraResources entry, including the region picker) lives under resources\, so a real
        # overlay leftover still cannot hide from this check.
        $payloadDir = Join-Path $prefix 'resources'
        if (-not (Test-Path -LiteralPath $payloadDir)) { Write-Error ('installed prefix ' + $prefix + ' has no resources directory to scan'); exit 1 }
        $tokenHits = @(Get-ChildItem -LiteralPath $payloadDir -Recurse -File -ErrorAction SilentlyContinue | Select-String -Pattern $overlayToken -SimpleMatch).Count
        $staleNames = @(Get-ChildItem -LiteralPath $prefix -Recurse -File -Filter $overlayNamePattern -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
        [pscustomobject]@{
            installer      = $installer[0].FullName
            prefix         = $prefix
            installedExe   = $installedExe
            bogusArgvExit  = $probeExit
            overlayTokens  = $tokenHits
            staleArtifacts = $staleNames
        } | ConvertTo-Json -Depth 3
        if ($tokenHits -ne 0) { Write-Error ('installed app still contains ' + $overlayToken + ' ' + $tokenHits + ' times'); exit 1 }
        if ($staleNames.Count -ne 0) { Write-Error ('installed app still ships overlay artifacts: ' + ($staleNames -join ',')); exit 1 }
    } finally {
        # Cleanup races the same handoff: on an early failure the uninstaller may not exist yet,
        # and deleting a tree the installer is still writing silently leaves the install behind.
        # Shorter budget than the install: on a failure path the uninstaller may never appear,
        # and cleanup must not stall the gate for minutes before reporting the real error.
        $uninstallDeadline = (Get-Date).AddSeconds(60)
        $uninstaller = @()
        while ($uninstaller.Count -lt 1 -and (Get-Date) -lt $uninstallDeadline) {
            $uninstaller = @(Get-ChildItem -LiteralPath $prefix -Filter 'Uninstall*.exe' -File -ErrorAction SilentlyContinue)
            if ($uninstaller.Count -lt 1) { Start-Sleep -Milliseconds 500 }
        }
        if ($uninstaller.Count -ge 1) {
            Start-Process -FilePath $uninstaller[0].FullName -ArgumentList '/S' -Wait | Out-Null
            Start-Sleep -Seconds 5
        }
        for ($attempt = 0; $attempt -lt 10 -and (Test-Path -LiteralPath $prefix); $attempt++) {
            Remove-Item -LiteralPath $prefix -Recurse -Force -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $prefix) { Start-Sleep -Seconds 2 }
        }
        if (Test-Path -LiteralPath $prefix) {
            Write-Warning ('could not remove the temp install prefix ' + $prefix + ' - delete it by hand')
        }
    }
    'PASS: PACKAGING_INSTALLED'
    exit 0
}
'PASS: PACKAGING_CLEAN_PATH'
exit 0
