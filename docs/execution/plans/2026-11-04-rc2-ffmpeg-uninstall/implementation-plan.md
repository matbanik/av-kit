---
project: "2026-11-04-rc2-ffmpeg-uninstall"
date: "2026-11-04"
source: "docs/build-plan/07-distribution.md#ffmpeg-no-libdvdcss-residual"
grouping_source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md"
meus: ["MEU-113", "MEU-114"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: FFmpeg without libdvdcss and a clean uninstall (Session 49)

> **Project:** `2026-11-04-rc2-ffmpeg-uninstall`
> **Build plan:**
> - `docs/build-plan/07-distribution.md` §FFmpeg without libdvdcss (residual, `:334`) and §Uninstall removes the installer copy (residual, `:349`)
> - `docs/build-plan/07-distribution.md` §FFmpeg (`:157`), §Second release candidate (`:362`) and D-101's record (`:327`) are Local Canon
>
> **Source requests,** Mat, 2026-11-04: "OK we will go with pythorch remove as you originally suggested. All ohter recommendations are accepted. Proceed". That accepted triage D-214 (build FFmpeg from BtbN's recipe without the DVD scripts) and D-228 (uninstall removes the installer copy).
> **Known issues:** `FFMPEG-LIBDVDCSS-BUNDLED`, `FETCH-FFMPEG-EXIT-CODES`, `UNINSTALL-LEAVES-INSTALLER-COPY`.
> **Status:** `draft`. `plan_to_exec_gate: human`; Mat's message above directs planning. Execution waits for Mat's own go-ahead.
>
> Line anchors are from `main` `d287c55`. The tree isn't clean at that commit: it holds the uncommitted triage records and another session's closeout files. Row 0 records whatever is there at execution time.

## Goal

**Goal anchor:** Session 49 takes libdvdcss out of the FFmpeg av-kit ships by building FFmpeg from BtbN's recipe with the DVD scripts off and re-pinning to that build with a matching source set, makes the fetch script return its documented exit codes and makes the uninstaller remove the installer copy, with every outward step waiting on Mat.

Three things are wrong today:

1. **The shipped FFmpeg holds libdvdcss.** The pinned BtbN build (`ffmpeg.exe` SHA-256 `c46215f8…`) reports `--enable-libdvdread` and `--enable-libdvdnav`, lists the `dvdvideo` demuxer and contains `Could not open %s with libdvdcss.` and `DVDCSS_METHOD`. No av-kit feature reads DVDs. Mat ruled on 2026-11-04 that it comes out (D-214). BtbN publishes no build without it, so av-kit has to build its own, and that build has never been run anywhere.
2. **`tools/fetch_ffmpeg_windows.ps1` documents exit codes 2 to 5 and returns 1.** `Write-Error` under `$ErrorActionPreference='Stop'` throws before `exit` runs. Exit 6 already avoids this (`:50-52`). The tests only assert non-zero (`tests/unit/test_packaging_installer.py:152,172`).
3. **Uninstall leaves a 340 MB copy of the installer** at `%LOCALAPPDATA%\av-kit-ui-updater\installer.exe`. The electron-builder template writes it on install, and nothing removes it (D-228).

The session ends with a tested no-libdvdcss build, its source set, a local installer that carries it, a round trip that proves the clean uninstall, and a publish packet for Mat. Version stays `0.1.0-rc.1`, because MEU-125 moves it, and the local installer is never uploaded.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-04). A headroom binary is on PATH but no payload here is oversized: the scope is a named list of files read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy` with receipts under `C:/Temp/av-kit` and `C:/Temp/av-kit/rc2/`.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS. The FFmpeg build runs in WSL on the same machine.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`, under ledger loops `s49-plan-2026-11-04-rc2-ffmpeg-uninstall` and `s49-execution-2026-11-04-rc2-ffmpeg-uninstall`. Claude wrote the plan, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable or the ledger refuses a round, the fallback is Mat. Each round is metered; the coordinator warns before dispatching.
- **Never in these rows without Mat's words:** commit, push, tag, create or edit a GitHub release, create a fork or repository, upload an asset, change RC1's state, install Docker, or author an `approved` verdict. Never `docker login` or `docker push`.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-113` | `.agent/context/handoffs/2026-11-04-rc2-ffmpeg-uninstall-MEU-113-handoff.md` |
| `MEU-114` | `.agent/context/handoffs/2026-11-04-rc2-ffmpeg-uninstall-MEU-114-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-04-rc2-ffmpeg-uninstall-plan-critical-review.md` and `.agent/context/handoffs/2026-11-04-rc2-ffmpeg-uninstall-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts |
| WP-2 | Fetch exit codes (rows 1, 2) | WP-1 | shared | Tests and script |
| WP-3 | Clean uninstall, proved on a repackaged installer (rows 3 to 6) | WP-1 | shared | Macro, pin, `ROUND_TRIP`, round-trip receipts |
| WP-4 | Absence gate and real negatives (rows 7 to 9) | WP-1 | shared | `ABSENCE_GATE`, negatives receipt |
| WP-5 | Recipe patch, driver and generator comparison (rows 10 to 12) | WP-4 | shared | `RECIPE_PATCH`, `BUILD_DRIVER`, comparison receipt |
| WP-6 | Docker and the real build (rows 13 to 15) | WP-5, D-246 | compact_continue | `BUILD_OUT` with zip, `sha256.txt`, `build-info.json`; compact, then re-read `task.md` and `build-info.json` |
| WP-7 | Pin, source set and encoders (rows 16 to 22) | WP-6, D-251 | shared | Pin edits, `SOURCE_ARCHIVE`, encoder check |
| WP-8 | Full installer and round trip (rows 23, 24) | WP-7 | compact_continue | `BUILD_RECORD`, round-trip receipts; compact, then re-read `task.md` and the record |
| WP-9 | Records and publish packet (rows 25, 26) | WP-8 | shared | Hub, register, `publish-ffmpeg-nodvd.md` |
| WP-10 | Closeout, then publication on Mat's words (H1, H2, row 27) | WP-9 | `compact_continue` | Handoffs, review, reflection |

MEU-114 doesn't wait for FFmpeg (D-264). If the build stalls, rows 0 to 12 still stand and MEU-114 can close as the grouping's 49b, with MEU-113 left open.

## User Review Required

> [!IMPORTANT]
> **Two decisions are Mat's, and both have a recommendation below: where the build runs (D-246) and where the built zip lives (D-251).** The rows follow the recommended branch. Rows 0 to 12 need neither. Another answer to D-246 changes rows 13 and 14 through a recorded plan amendment.
>
> **Publishing the zip is itself object-code distribution under the GPL.** The source archive or clear directions to it must sit next to the zip from the moment it goes up, and must stay as long as needed. So the order is build, gate, assemble source, then publish both together in one release. D-251's brief offers one sentence that authorises the publish in advance, so row 27 needn't wait for another message.
>
> **Docker in Ubuntu is a system change that needs Mat's password.** Row 13 is Mat's. The install commands are in §Verification Plan 4, and D-246 lists how to remove it.
>
> **The build's time is unknown.** Nobody has run this recipe here. It can take many hours of machine time, so the PC has to stay awake. D-265 sets a stop-loss of two full runs or 24 hours of machine time, whichever comes first. At that point the coordinator stops and asks Mat.
>
> **Real installs run on this PC (rows 6, 24).** Each phase installs silently into `C:\Temp\av-kit\rc2\install`, launches with a throwaway `AVKIT_APP_DATA`, and uninstalls with `/S`, never `--delete-app-data`. `%LOCALAPPDATA%\av-kit` keeps its top-level entries and the check proves it. **The round trip deletes the 340 MB `%LOCALAPPDATA%\av-kit-ui-updater\installer.exe` left by Mat's earlier install.** It's identical to the RC1 installer (SHA-256 `beabc509…`), and row 0 keeps a copy as `RC1_INSTALLER`. S5 re-checks the machine and stops if anything has changed.
>
> **RC1 isn't touched here.** The newer ruling and the older one disagree about taking it down (D-215 against RC1 plan D-238), and that question goes to Mat separately. It doesn't change this plan's order.
>
> **The two local installers are never uploaded.** They carry version `0.1.0-rc.1`, the same as the published RC1. The first also still holds RC1's stock FFmpeg, because it repackages RC1's unpacked folder.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `RECIPE_PATCH` | `packaging/ffmpeg-recipe/no-dvd.patch`, the exact text in §Recipe patch, LF bytes, SHA-256 `90e7bbbe58fe9ffb33366f1bfc0939770454f581aa93227490523e62bad0f26e`. |
| `RECIPE_TREE` | `889c3500c50d31f0ec4718753b077dbe74117d32`: the git tree of BtbN commit `5031c6f1082414e53688d39e521849905071070d` after `RECIPE_PATCH`. Measured the same in WSL and on Windows. |
| `BUILD_DRIVER` | `tools/build_ffmpeg_nodvd.py`. Python standard library only, run in WSL. |
| `ABSENCE_GATE` | `tools/check_no_libdvdcss.py`, with exactly one of `--bin-dir`, `--zip`, `--source-archive`. |
| `NODVD_ASSET` | `ffmpeg-n8.1.3-27-g8dca1586f4-win64-gpl-8.1-nodvd.zip`. |
| `NODVD_TAG` | `ffmpeg-n8.1.3-27-g8dca1586f4-nodvd`. |
| `BUILD_OUT` | `C:/Temp/av-kit/rc2/ffmpeg-build`, which WSL sees as `/mnt/c/Temp/av-kit/rc2/ffmpeg-build`. |
| `BUILT_BIN` | `C:/Temp/av-kit/rc2/ffmpeg-built`: row 15 copies the built `ffmpeg.exe` and `ffprobe.exe` here. |
| `SOURCE_ARCHIVE` | `C:/Temp/av-kit/rc2/ffmpeg-src/av-kit-0.1.0-rc.2-ffmpeg-source.tar.xz`. |
| `RC1_INSTALLER` | `C:/Temp/av-kit/rc2/rc1-installer.exe`, SHA-256 `beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7`. |
| `PREPACKAGED_INSTALLER` | `C:/Temp/av-kit/rc2/prepackaged-installer.exe`: the new NSIS macro around RC1's unpacked app. |
| `NEW_INSTALLER` | `C:/Temp/av-kit/rc2/new-installer.exe`: the full build carrying the new FFmpeg. |
| `BUILD_RECORD` | `C:/Temp/av-kit/rc2/build-record.json`. |
| `ROUND_TRIP` | `docs/execution/plans/2026-11-04-rc2-ffmpeg-uninstall/install-roundtrip.ps1`. |

### Recipe patch

Five files change. Each DVD script answers `return -1` first, which is the same off path LGPL builds use, so `generate.sh` emits no DVD stage and writes `--disable-libdvdread --disable-libdvdnav`. `build.sh` and the toolchain Dockerfile pin the two commits they'd otherwise take at their floating heads. `scripts.d/zz-final.sh` keeps `echo dvd`; removing that line alone would leave the source assembler reading the scripts as on and emit no disable flags.

```diff
diff --git a/build.sh b/build.sh
index a97e55c..8c64672 100755
--- a/build.sh
+++ b/build.sh
@@ -39,6 +39,7 @@ cat <<EOF >"$BUILD_SCRIPT"
 
     git clone --filter=blob:none --branch='$GIT_BRANCH' '$FFMPEG_REPO' ffmpeg
     cd ffmpeg
+    git checkout 8dca1586f468bfcbb78ae3ed618af1361d9f140a
 
     ./configure --prefix=/ffbuild/prefix --pkg-config-flags="--static" \$FFBUILD_TARGET_FLAGS \$FF_CONFIGURE \
         --extra-cflags="\$FF_CFLAGS" --extra-cxxflags="\$FF_CXXFLAGS" --extra-libs="\$FF_LIBS" \
diff --git a/images/base-win64/Dockerfile b/images/base-win64/Dockerfile
index eacbdeb..931b4c8 100644
--- a/images/base-win64/Dockerfile
+++ b/images/base-win64/Dockerfile
@@ -4,6 +4,7 @@ FROM $GH_REPO/base:latest${BASE_TAG_SUFFIX}
 
 RUN --mount=src=ct-ng-config,dst=/.config \
     git clone --filter=blob:none https://github.com/crosstool-ng/crosstool-ng.git /ct-ng && cd /ct-ng && \
+    git checkout b1a94f65c5187d99037a4e2f57aefbdf995a9677 && \
     ./bootstrap && \
     ./configure --enable-local && \
     make -j$(nproc) && \
diff --git a/scripts.d/50-dvd/30-libdvdcss.sh b/scripts.d/50-dvd/30-libdvdcss.sh
index 664a541..d944212 100755
--- a/scripts.d/50-dvd/30-libdvdcss.sh
+++ b/scripts.d/50-dvd/30-libdvdcss.sh
@@ -4,6 +4,7 @@ SCRIPT_REPO="https://code.videolan.org/videolan/libdvdcss.git"
 SCRIPT_COMMIT="811ce97a1d4d1c9d936f4b2707f533a9ef768251"
 
 ffbuild_enabled() {
+    return -1
     [[ $VARIANT == lgpl* ]] && return -1
     (( $(ffbuild_ffver) >= 700 )) || return -1
     return 0
diff --git a/scripts.d/50-dvd/40-libdvdread.sh b/scripts.d/50-dvd/40-libdvdread.sh
index f642327..8e9df32 100755
--- a/scripts.d/50-dvd/40-libdvdread.sh
+++ b/scripts.d/50-dvd/40-libdvdread.sh
@@ -4,6 +4,7 @@ SCRIPT_REPO="https://code.videolan.org/videolan/libdvdread.git"
 SCRIPT_COMMIT="0f30df53125b564ef45903714403ce0a1e6c5e9e"
 
 ffbuild_enabled() {
+    return -1
     [[ $VARIANT == lgpl* ]] && return -1
     (( $(ffbuild_ffver) >= 700 )) || return -1
     return 0
diff --git a/scripts.d/50-dvd/50-libdvdnav.sh b/scripts.d/50-dvd/50-libdvdnav.sh
index 3986a88..107332d 100755
--- a/scripts.d/50-dvd/50-libdvdnav.sh
+++ b/scripts.d/50-dvd/50-libdvdnav.sh
@@ -4,6 +4,7 @@ SCRIPT_REPO="https://code.videolan.org/videolan/libdvdnav.git"
 SCRIPT_COMMIT="8147ccd35e5aae4afdd21171cf7b6b4d8f179d28"
 
 ffbuild_enabled() {
+    return -1
     [[ $VARIANT == lgpl* ]] && return -1
     (( $(ffbuild_ffver) >= 700 )) || return -1
     return 0
```

The measured file is `C:/Temp/av-kit/rc2-plan/no-dvd.patch`. Row 11 copies it byte for byte; if that file is gone, it re-creates the text above. The patch's SHA-256 and `RECIPE_TREE` decide either way. Git would turn the file into CRLF on checkout under `* text=auto`, so `.gitattributes` gains `packaging/ffmpeg-recipe/*.patch text eol=lf`.

### What can make the build quietly wrong

| Trap | Evidence | Guard |
|---|---|---|
| `build.sh` silently uses BtbN's stock image, with libdvdcss, when the local image is missing | BtbN's maintainer: "Are you sure your makeimage step succeeded? If not, build.sh will just fetch an image from GitHub and build that" (issue #598) | `REGISTRY_OVERRIDE=local.avkit.invalid` renames every image, so a pull can't succeed. A non-zero `makeimage.sh` stops the driver, and `docker image inspect` must find the image before `build.sh` runs. `ABSENCE_GATE` then checks the result. |
| `QUICKBUILD` builds on BtbN's floating registry image | `makeimage.sh`: without it, `base` and `target-base` are baked from this recipe | The driver clears `QUICKBUILD` and `GITHUB_REPOSITORY`. |
| `build.sh` clones the head of `release/8.1` | `build.sh:40-41` | `RECIPE_PATCH` checks out `8dca1586f4…`. |
| The toolchain Dockerfile clones crosstool-NG's newest commit | `images/base-win64/Dockerfile` | `RECIPE_PATCH` checks out `b1a94f65c5…`, the commit the config was saved with. Fallback: D-254. |
| `download.sh` fetches libdvdcss sources even for a disabled script | `download.sh` has no `ffbuild_enabled` check | `.cache/` is never published and is never evidence of absence. The binaries and `SOURCE_ARCHIVE` are what `ABSENCE_GATE` reads. |
| The zip gets BtbN's stock asset name | `build.sh` names it from the version | The driver renames it to `NODVD_ASSET`, so the two can't be mistaken. |

### `BUILD_DRIVER`

Run as `python3 -I /mnt/p/av-kit/tools/build_ffmpeg_nodvd.py --work ~/av-kit-ffmpeg --out /mnt/c/Temp/av-kit/rc2/ffmpeg-build --log /mnt/c/Temp/av-kit/rc2/ffmpeg-build-run.log [--resume]`. `--work` goes through `Path.expanduser()`, and `--log` writes the children's output, so neither needs a shell. It has no Linux-only imports at module level, so its logic is unit-tested on Windows with a fake runner. Constants duplicate the assembler's, and a test asserts they match.

1. **Preflight, exit 2:** Linux; `docker buildx version` answers; `--work` isn't under `/mnt/` and is empty, or `--resume` was given, which keeps `.cache` and rechecks the tree.
2. **Recipe, exit 3:** fetch BtbN `5031c6f` with `core.autocrlf=false`; `git apply --index` `RECIPE_PATCH`; `git diff --cached --name-only` equals the five files; `git write-tree` equals `RECIPE_TREE`. No docker call has happened yet.
3. **Generated text, exit 3:** with `REGISTRY_OVERRIDE=local.avkit.invalid` and `QUICKBUILD` and `GITHUB_REPOSITORY` cleared, run `./generate.sh win64 gpl 8.1`. `dockerfile_findings` requires no `AS dvd`, no `50-dvd` stage line, both `--disable` flags in `FF_CONFIGURE` and no `--enable-libdvd`.
4. **Images, exit 4 and 5:** `./makeimage.sh win64 gpl 8.1`; non-zero exits 4 and `build.sh` never runs. `docker image inspect` on the local image name; absent exits 5.
5. **Build, exit 6:** `./build.sh win64 gpl 8.1`.
6. **Result, exit 7:** exactly one zip in `artifacts/` whose name holds `-g8dca1586f4-`; renamed to `NODVD_ASSET`.
7. **Outputs:** zip, `sha256.txt` and `build-info.json` (recipe tree, FFmpeg commit, docker version, start, stop, duration) copied to `--out`, then the sentinel `exit-code.txt`, which is written on every exit.

Two more modes need no Docker. `--generate-only` runs steps 2 and 3 on the stock and the patched recipe (row 12). `--verify-output DIR` runs on Windows and checks the sentinel, name, hash and recipe tree (rows 14 and 15).

**No commit is made** in the build, so no git identity is involved.

### `ABSENCE_GATE`

| Mode | Checks | Why this shape |
|---|---|---|
| `--bin-dir DIR` | For each of `ffmpeg.exe` and `ffprobe.exe`: `-version` starts with `ffmpeg version` or `ffprobe version` and has a `configuration:` line; no `--enable-libdvd`; `-demuxers` has no `dvdvideo`; streaming byte scan with chunk overlap finds no `libdvdcss` or `DVDCSS_`. | A broken binary is a refusal, not a pass. |
| `--zip FILE` | In place, no extraction: must hold `ffmpeg.exe`; `libdvdcss` and `DVDCSS_` banned in every member; `--enable-libdvd` banned in `.exe` members. | The stock zip's docs name `--enable-libdvd` and `dvdvideo` but never `libdvdcss` (`C:/Temp/av-kit/s49-stock-zip-scan.txt`), so banning the flag everywhere would refuse a clean build for its documentation. |
| `--source-archive FILE` | Lists the tar.xz: no `deps/libdvdcss-*`, `deps/libdvdread-*` or `deps/libdvdnav-*`; holds `ffmpeg/`, `MANIFEST.tsv` and `no-dvd.patch`; the recipe's three `50-dvd` scripts read off. | Same rule as D-214's "Done when", and it refuses an archive that's simply missing the source. |

Row 9 runs it on real stock inputs, which must fail: `C:/Temp/av-kit/ffmpeg-dl/` binaries, `C:/Temp/av-kit/ffmpeg-dl/ffmpeg-pin.zip` and RC1's `C:/Temp/av-kit/rc1/ffmpeg-src/av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz`.

### Source assembler

`tools/assemble_ffmpeg_source.py` keeps `BUILDS_REPO` and `BUILDS_COMMIT` upstream and gains `RECIPE_PATCH` and `RECIPE_TREE`.

- In the bare store, with a temporary `GIT_INDEX_FILE`: `read-tree <commit>`, `apply --cached <patch>`, `write-tree`. A hash other than `RECIPE_TREE` is refused. This was measured on Windows at plan time. `_git` gains an `env` parameter.
- `recipe_scripts()` and the `ffmpeg-builds` tree read that tree, and `archive_tree` accepts a tree id. So `collect` leaves out the three DVD repositories, and `check_configuration` refuses a stock binary because nothing explains `--enable-libdvdread` any more (exit 5).
- The manifest row keeps BtbN's URL and the requested upstream commit, and records the resolved tree.
- `no-dvd.patch` and `build_ffmpeg_nodvd.py` join the archive root through `DOCUMENTS` and `pack()`, so the archive publishes the recipe change and the steps that drove it.
- `ARCHIVE_NAME`, `BUILD_TAG`, `BUILD_ASSET` and `BUILD_SHA256` move to the new build. The README is rewritten for a self-built binary: it names the recipe change, the tree id and the driver, and drops the crosstool-NG line from its "does not pin everything" list unless D-254's fallback applied.

### Other consumers of the pin

| File | Change |
|---|---|
| `tools/fetch_ffmpeg_windows.ps1` | URL, SHA and the header comment (`# Pin: av-kit <tag> win64 gpl nodvd`) |
| `tools/deps_report.py:32` | `FFMPEG_URL_PATTERN` becomes `https://github\.com/[^/'"\s]+/[^/'"\s]+/releases/download/[^'"\s]+`. Today's BtbN-only pattern raises `ScannerError` on any other owner. |
| `packaging/THIRD_PARTY_NOTICES.md:61-71` | §FFmpeg: built from BtbN's recipe with the DVD scripts off, the new source archive and release URL |
| `README.md:205-216` | The advice to pass a current BtbN build goes, because it brings libdvdcss back. It's replaced by the driver and `ABSENCE_GATE`. |
| `docs/build-plan/07-distribution.md:157-171` | Only a live statement naming the stock pin. `:327` stays as history. |
| `tests/unit/test_packaging_installer.py:224-232`, `tests/unit/test_assemble_ffmpeg_source.py` (`test_ac_110_21`) | Needles follow the new pin. `:249`'s fixture root name stays, because the rename only touches the zip's filename. |

`docs/releases/*rc.1*` stays as history. The RC2 notes and checklist are MEU-125's.

### Encoders

`ConversionCompressIn` has no codec field (`packages/api/src/avkit_api/schemas/conversions.py:19-28`), and software preference picks `libx265` whenever it's there (`packages/core/src/avkit_core/services/conversion.py:411-416`). So the product can't reach x264 on this binary. `tools/smoke_packaged_rc.py` therefore gains direct encodes with the packaged `ffmpeg.exe` (`-c:v libx264`, `-c:v libx265`), read back through `ffprobe`, next to its existing product job (`_first_conversion`). A pure `_check_encoders` is unit-tested in a new `tests/unit/test_smoke_packaged_rc.py`. The tool lives in `tools/`, so MEU-125 reuses it.

### Uninstall macro

`customUnInstall` in `ui/build/installer.nsh` gains this block after its two `DeleteRegValue` lines:

```nsis
${ifNot} ${isUpdated}
  ${if} $installMode == "all"
    SetShellVarContext current
  ${endif}
  Delete "$LOCALAPPDATA\${APP_INSTALLER_STORE_FILE}"
  RMDir "$LOCALAPPDATA\av-kit-ui-updater"
  ${if} $installMode == "all"
    SetShellVarContext all
  ${endif}
${endIf}
```

It mirrors the template that writes the copy (`app-builder-lib/templates/nsis/include/installer.nsh:88-96`), including the switch to per-user app data on a machine-wide install, and `APP_INSTALLER_STORE_FILE` is defined for the uninstaller's compile too (`NsisTarget.js:461-463`, `:609-613`). `RMDir` has no `/r`, so it's the narrowest action available: a folder holding anything else stays. An upgrade doesn't reach the block, because `installUtil.nsh:205-206` always passes `--updated` to the old uninstaller.

**The uninstaller that runs is the one the installed version wrote** (electron.build). So rc.1 to rc.2 still runs rc.1's uninstaller, and the fix takes effect on rc.2's own uninstall. `ROUND_TRIP` tests both.

### `ROUND_TRIP`

A copy of RC1's script, with parameters `-NewInstaller`, `-OldInstaller`, `-Smoke launch|full`, `-OutDir`, optional `-BuildRecord` and `-PreconditionsOnly`, and paths under `C:/Temp/av-kit/rc2/`. It keeps exit codes 40 (S5 precondition), 41 (installer differs from the build record), 42 (install failed), 44 (install-root smoke), 45 (app smoke) and 46 (uninstall left something or changed the app data), and adds 47 for this MEU's checks. RC1's S6 loop only flags a folder that was gained, so it can't see this bug; these checks are explicit.

| Phase | Steps | Must hold |
|---|---|---|
| Pre-state | Read `%LOCALAPPDATA%\av-kit-ui-updater` | Absent, or holds only `installer.exe` with SHA-256 `beabc509…` |
| A, negative control | `RC1_INSTALLER` install, uninstall | The copy is **still there**. If it isn't, the check observes nothing and the script exits 47. |
| B, fresh new | New install, smoke, uninstall | Copy present after install; copy and folder gone after uninstall; `%APPDATA%\av-kit-ui` still there; `%LOCALAPPDATA%\av-kit` top-level entries unchanged |
| C, upgrade | RC1, then new over it, launch, uninstall | App launches; copy and folder gone after uninstall |
| D, install over | New, new again, launch, uninstall | Copy present and app launches after the second install; copy and folder gone after uninstall |

`${isUpdated}`'s skip can't be observed at runtime, because the install rewrites the copy straight afterwards. The macro pin proves that structure (AC-114.1). Process stops are scoped by install path only.

### MEU-113 `dist-ffmpeg-no-libdvdcss`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `tools/fetch_ffmpeg_windows.ps1` parameters and `AVKIT_FFMPEG_*` env | The script's `param` block | URL non-blank; SHA-256 is 64 hex; archive must exist | PowerShell refuses an unknown parameter |
| `BUILD_DRIVER` CLI | `argparse` | `--work` not under `/mnt/`; empty unless `--resume`; `--log` is a file path the driver writes; `--generate-only` and `--verify-output` exclude a build | `argparse` exits 2 on unknown arguments |
| `ABSENCE_GATE` CLI | `argparse` mutually exclusive required group | Exactly one mode; the path must exist | `argparse` exits 2 on unknown arguments |
| Files `ABSENCE_GATE` reads | Its own readers | Treated as untrusted data; zip and tar are listed or streamed, never extracted to disk | Not applicable |

No REST, MCP or UI surface changes, so `openapi` and `mcp-*` don't apply.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-113.1 | unit | The fetch script exits 2, with its message on stderr, for a blank URL, a malformed SHA and a missing archive. | Local Canon (`FETCH-FFMPEG-EXIT-CODES`; 07 §FFmpeg without libdvdcss) | Today each returns 1 (`C:/Temp/av-kit/fetch-exit-blank-sha.txt`) |
| AC-113.2 | unit | It exits 3 on a SHA mismatch. | Local Canon (same) | Today 1 (`C:/Temp/av-kit/fetch-exit-sha-mismatch.txt`) |
| AC-113.3 | unit | It exits 4 when the archive holds no `ffmpeg.exe` or `ffprobe.exe`. | Local Canon (same) | A zip with only `ffprobe.exe` |
| AC-113.4 | unit | It exits 5 for a stub of 1024 B or less. | Local Canon (same) | A 1 KB `ffmpeg.exe` |
| AC-113.5 | unit | The script has no `Write-Error` left. | Local Canon (same) | A test fails on any occurrence |
| AC-113.6 | unit | `RECIPE_PATCH` names exactly the five files. | Human-approved (D-214) | A sixth file, or a missing one, fails |
| AC-113.7 | unit | After `git apply` in a temp repo, `enabled_for_build` reads all three DVD scripts off; the pre-image reads on. Pre-images come from the patch's own context lines, so the test needs no network. | Human-approved (D-214) | The pre-image is the negative |
| AC-113.8 | unit | `RECIPE_PATCH` is LF only with the recorded SHA-256, and `.gitattributes` pins it. | Local Canon (git `text=auto` here converts on checkout) | A CRLF copy fails |
| AC-113.9 | unit | `dockerfile_findings` flags stock-shaped text and passes patched-shaped text. | Human-approved (D-214) | An `AS dvd` line; a `50-dvd` stage line; a missing `--disable`; an `--enable-libdvd` |
| AC-113.10 | integration | The real `generate.sh` in WSL: stock is flagged and patched is clean, with no Docker. | Human-approved (D-214) | Stock is the negative |
| AC-113.11 | unit | With a fake runner, the driver runs its steps in the fixed order with `REGISTRY_OVERRIDE` set and `QUICKBUILD` and `GITHUB_REPOSITORY` cleared. | Research-backed (BtbN #598) | A pre-set `QUICKBUILD` doesn't reach the child |
| AC-113.12 | unit | A failed `makeimage.sh` or a missing local image means `build.sh` never runs (exit 4, exit 5). | Research-backed (BtbN #598) | Both cases, asserting no `build.sh` call |
| AC-113.13 | unit | A tree other than `RECIPE_TREE` exits 3 before any docker call. | Human-approved (D-214) | A changed patch |
| AC-113.14 | unit | The driver refuses `--work` under `/mnt/`, and a non-empty `--work` without `--resume`. | Local Canon (WSL's Windows mounts are slow and lose modes) | Both cases |
| AC-113.15 | integration | A real build leaves `NODVD_ASSET`, `sha256.txt` and `build-info.json` with `RECIPE_TREE`, and `--verify-output` passes. | Human-approved (D-214) | `--verify-output` refuses a changed zip |
| AC-113.16 | unit | `ABSENCE_GATE` refuses `-version` output with `--enable-libdvd`. | Human-approved (D-214) | The stock configuration line |
| AC-113.17 | unit | It refuses `-demuxers` output with `dvdvideo`. | Human-approved (D-214) | A stock line |
| AC-113.18 | unit | The byte scan finds `libdvdcss` and `DVDCSS_` across a chunk boundary. | Human-approved (D-214) | A needle split at the boundary |
| AC-113.19 | unit | A binary with no version banner or `configuration:` line is a refusal. | Local Canon (a check that can't read must not pass) | Empty output; an error exit |
| AC-113.20 | unit | `--zip` applies §`ABSENCE_GATE`'s rules, and refuses a zip with no `ffmpeg.exe`. | Human-approved (D-214) | `--enable-libdvd` in an `.exe` is refused and in an `.html` is allowed; `DVDCSS_` in any member is refused |
| AC-113.21 | unit | `--source-archive` applies its rules. | Human-approved (D-214, D-101) | A `deps/libdvdcss-x/` member; no `ffmpeg/`; no `no-dvd.patch`; a recipe script reading on |
| AC-113.22 | integration | The real stock binaries, stock zip and RC1 source archive each fail `ABSENCE_GATE`, for the expected reason. | Human-approved (D-214) | These are the negatives |
| AC-113.23 | integration | The built binaries and zip pass `ABSENCE_GATE`. Their configuration keeps `--enable-gpl`, `--enable-libx264` and `--enable-libx265`, names `-g8dca1586f4-`, and `-encoders` lists both encoders. | Human-approved (D-214) | AC-113.22 proves the gate can fail |
| AC-113.24 | unit | The fetch script's URL and SHA equal the assembler's `BUILD_*`, and its pin comment names the tag. | Local Canon (AC-110.21) | The old pin fails |
| AC-113.25 | unit | The assembler refuses a tree other than `RECIPE_TREE`. | Human-approved (D-214) | A changed patch |
| AC-113.26 | unit | `collect` skips the DVD repositories with the patched scripts. | Human-approved (D-214, D-101) | The stock scripts include them |
| AC-113.27 | unit | `check_configuration` refuses a stock `-version` output with the patched scripts. | Local Canon (AC-110.21) | Stock version text |
| AC-113.28 | unit | The archive holds `no-dvd.patch` and `build_ffmpeg_nodvd.py`, and its README names the recipe change, the tree id and the driver. | Human-approved (D-101: publish the recipe change) | Removing either document fails the archive check |
| AC-113.29 | integration | A real assembly with the built `ffmpeg.exe` exits 0, is under 2 GiB, reads back against its manifest and passes `ABSENCE_GATE --source-archive`. | Human-approved (D-214, D-101) | AC-113.22's RC1 archive |
| AC-113.30 | unit | `deps_report` finds the new URL on any GitHub owner, still once only. | Local Canon (`tools/deps_report.py:171`) | Two URLs raise `ScannerError`; a non-GitHub URL isn't matched |
| AC-113.31 | unit | NOTICES names the new build, the recipe change and the new source archive. | Local Canon (AC-110.21) | The old needles fail |
| AC-113.32 | unit | The README drops the advice to pass a current BtbN build and names the driver and `ABSENCE_GATE`. | Local Canon (D-214: that advice would bring libdvdcss back) | The old sentence fails |
| AC-113.33 | unit | `_check_encoders` refuses a missing output, a wrong codec and a short duration. | Local Canon (07 §Tests: "through x264 and x265") | Each case |
| AC-113.34 | integration | On the installed `resources/ffmpeg`, `ABSENCE_GATE` passes, both direct encodes pass, and the product job completes. | Local Canon (07 §Tests) | The smoke's stock negative isn't needed: AC-113.22 covers the gate and AC-113.33 the encoder check |
| AC-113.35 | integration | After Mat's words: a fresh download from the pinned URL matches the SHA, and the zip and `SOURCE_ARCHIVE` sit in one release. | Human-approved (D-214, D-251) | `fetch_ffmpeg_windows.ps1` refuses a wrong SHA (AC-113.2) |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| What comes out, and what stays | Human-approved | D-214: scripts off; GPL, x264 and x265 stay |
| What "absent" means | Human-approved | D-214's "Done when", plus the zip rule measured at plan time |
| Where the build runs | Human-approved (pending) | D-246 |
| Where the zip lives | Human-approved (pending) | D-251 |
| Which FFmpeg commit | Local Canon | D-253: same commit, so DVD is the only change |
| How the recipe is identified without a commit | Local Canon | D-262: tree hash |
| How the build is protected from the stock image | Research-backed | BtbN #598, D-254 |
| Exit codes | Local Canon | Script header; exit 6's pattern at `:50-52` |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `tools/fetch_ffmpeg_windows.ps1` | modify | Exit codes; new pin |
| `tools/check_no_libdvdcss.py` | new | `ABSENCE_GATE` |
| `tools/build_ffmpeg_nodvd.py` | new | `BUILD_DRIVER` |
| `packaging/ffmpeg-recipe/no-dvd.patch` | new | `RECIPE_PATCH` |
| `.gitattributes` | modify | One line for the patch |
| `tools/assemble_ffmpeg_source.py` | modify | Patched recipe, new pin, README |
| `tools/deps_report.py` | modify | URL pattern |
| `tools/smoke_packaged_rc.py` | modify | Encoder checks and `ABSENCE_GATE` |
| `packaging/THIRD_PARTY_NOTICES.md` | modify | §FFmpeg |
| `README.md` | modify | §Building the installer |
| `docs/build-plan/07-distribution.md` | modify | Live statements only |
| `tests/unit/test_packaging_installer.py` | modify | Exit codes, needles |
| `tests/unit/test_check_no_libdvdcss.py` | new | AC-113.16 to AC-113.21 |
| `tests/unit/test_build_ffmpeg_nodvd.py` | new | AC-113.6 to AC-113.9, AC-113.11 to AC-113.14 |
| `tests/unit/test_assemble_ffmpeg_source.py` | modify | AC-113.25 to AC-113.28, new needles |
| `tests/unit/test_deps_report.py` | modify | AC-113.30 |
| `tests/unit/test_smoke_packaged_rc.py` | new | AC-113.33 |

### MEU-114 `dist-uninstall-installer-copy`

#### Boundary Inventory

No external input surface. The macro reads NSIS variables only, and the path comes from the template's define.

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| None | — | — | — |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-114.1 | unit | `customUnInstall` holds `Delete` and a non-recursive `RMDir` inside the not-updated guard. | Local Canon (07 §Uninstall; D-228) | A macro with the guard removed fails |
| AC-114.2 | unit | The folder name equals `ui/package.json`'s name plus `-updater`. | Local Canon (`app-builder-lib/out/appInfo.js:126`) | A changed name fails |
| AC-114.3 | unit | AC-61.18's two `DeleteRegValue` lines stay the only two, and there's no `RMDir /r`. | Local Canon (AC-61.18; D-258) | An `RMDir /r` fails |
| AC-114.4 | integration | NSIS compiles the macro under `-WX`. | Local Canon (`NsisTarget.js:623`) | electron-builder's own exit code |
| AC-114.5 | integration | Phase A: RC1's uninstall leaves the copy, so the check can see the bug. | Local Canon (D-228) | This is the negative control |
| AC-114.6 | integration | Phase B: the new uninstall removes the copy and its folder. | Local Canon (07 §Uninstall) | Phase A |
| AC-114.7 | integration | Phase B: `%APPDATA%\av-kit-ui` stays, and `%LOCALAPPDATA%\av-kit`'s top-level entries are unchanged. | Local Canon (07 §Uninstall; `ui/electron-builder.yml:18`) | Exit 46 or 47 if either changes |
| AC-114.8 | integration | Phase C: RC1 to new launches, and the later uninstall is clean. | Local Canon (07 §Uninstall: an upgrade still works) | Exit 42 or 45 |
| AC-114.9 | integration | Phase D: new over itself keeps the copy and launches, and the later uninstall is clean. | Local Canon (07 §Uninstall) | Exit 47 if the copy is missing after the second install |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| What's removed and what stays | Local Canon | 07 §Uninstall; D-228 |
| The path | Local Canon | The template's define, read at plan time from electron-builder's source |
| Which uninstaller runs | Research-backed | electron.build NSIS docs |
| Naming `%APPDATA%\av-kit-ui` in the notes | Local Canon | Deferred to MEU-125, whose §Second release candidate writes the notes |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/build/installer.nsh` | modify | The block in §Uninstall macro |
| `ui/tests/unit/login-item-nsh.test.ts` | modify | AC-114.1 to AC-114.3 |

### Project files

Plan-local scripts, listed in §Verification Plan: `baseline.sha`, `baseline-dirty.txt`, `baseline.ps1`, `red-check.py`, `identity.py`, `repackage.ps1`, `install-roundtrip.ps1`, `absence-negatives.ps1`, `absence-built.ps1`, `build-installer.ps1`, `build-identity.py`, `session-gate.ps1`, `publish-ffmpeg-nodvd.md`. State: `docs/BUILD_PLAN.md` (rendered), `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `.agent/context/known-issues.{yaml,md}`, `.agent/context/current-focus.md`, `docs/execution/metrics.md`, the handoffs, the rolling reviews and the reflection.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Release-notes wording for `%APPDATA%\av-kit-ui`, RC2 notes | deferred | MEU-125 | `07-distribution.md:362` §Second release candidate owns the notes; they can only be written once rc.2's contents are known |
| Version bump to `0.1.0-rc.2` | deferred | MEU-125 | `07` §Second release candidate; AC-110.9 keeps one version across surfaces until then |
| RC2 publish checklist, and moving `ROUND_TRIP` into `tools/` if rc.2 needs it | deferred | MEU-125 | Same section: it runs "the checks MEU-113, MEU-114, MEU-117 and MEU-121 add" |
| RC1 notes corrections (D-216) | deferred | MEU-125 | Grouping §5; carried into rc.2's notes |
| RC1's draft state (D-215) | out-of-scope | — | Human-approved question to Mat: D-215 conflicts with RC1 plan D-238 (`docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md:494-499`), and no row touches a release |
| A newer FFmpeg or security rebase | out-of-scope | — | `07` §FFmpeg without libdvdcss says "at the pinned commit `5031c6f`"; D-253 |
| Publishing `.cache` | out-of-scope | — | Holds libdvdcss sources; `07` §Source archive requires no `deps/libdvdcss-*` |
| `_extract` left behind on exits 4 and 5 | out-of-scope | — | `07` §Exit codes covers codes only; existing behaviour |
| Other triage MEUs | out-of-scope | — | Grouping sessions 50 to 57 |

## BUILD_PLAN.md Audit

This project adds no build-plan section; the two residual sections were registered with the triage. It may amend a live statement in `07-distribution.md:157-171`. `docs/BUILD_PLAN.md` regions regenerate through `tools/meu_status.py render`, and row 25 is the explicit D3 hub task.

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s49-render-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s49-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` records `HEAD` in `baseline.sha` and `git status --porcelain` in `baseline-dirty.txt`, runs `uv sync --frozen --all-packages`, `npm --prefix ui ci`, `node ui/node_modules/electron/install.js`, `npm --prefix mcp-server ci` and `npm --prefix mcp-server run build`, then captures the base suites to `s49-base-py.txt` and `s49-base-ui.txt`. It copies `ui/dist/av-kit-Setup-0.1.0-rc.1.exe` to `RC1_INSTALLER` and checks its SHA-256 **before anything can overwrite it**. It also checks the negative control at `C:/Temp/av-kit/rc1/negative-control/avkit-backend.exe` against `3d5691fc07310ca28c78d8a101fdd84d8b3100d2753605aaee6dd4a19394da87`, which `tools/smoke_packaged_rc.py` needs. Row 0 then runs `red-check.py --selftest` and `identity.py --selftest`.

Pytest runs with `TMP` and `TEMP` at `C:\Temp\av-kit\rc2\tmp`, as RC1 did, so the selftest arms aren't misled by `C:/Users/Mat/.agent` (RC1 ECN-2, `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR`). Only ids the baseline receipt really shows failing are excused. `AC-24.10` and `AC-25.10` depend on gitignored binaries being present.

`red-check.py` and `identity.py` are copies with this plan's values: `DECLARED_NEW` holds `check_no_libdvdcss`, `build_ffmpeg_nodvd`, `dockerfile_findings`, `_check_encoders`, `RECIPE_PATCH` and `RECIPE_TREE` alongside the names `red-check.py --selftest` needs, and `PLAN` holds this folder. `packaged-app-smoke.mjs` is reused from RC1's folder by path.

### 2. Red then Green (rows 1 to 4, 7, 8, 10, 11, 16 to 19, 21, 22)

Each Red receipt holds an assertion failure or a declared-new name's absence, never a setup failure. Red tests import new tools inside the test body (`from tools import check_no_libdvdcss`, as `tests/unit/test_assemble_ffmpeg_source.py:60-63` does), so a missing tool reads as a declared-new name. Pytest names are `test_ac_113_<n>_…`, so `--require test_ac_113_<n>` matches them exactly and doesn't also match `test_ac_113_<n>0` (`red-check.py:209`). Vitest titles begin `AC-114.<n>`. AC-113.26 and AC-113.27 go through `recipe_scripts()` on a local fixture store with `RECIPE_TREE` and `BUILDS_COMMIT` monkeypatched, so they stay red until it reads the patched tree. Expectations stay immutable in Green.

### 3. Prepackaged proof of MEU-114 (rows 4 to 6)

`repackage.ps1` clears `ELECTRON_RUN_AS_NODE`, requires `RC1_INSTALLER`, runs `npx electron-builder --win nsis --x64 --publish never --prepackaged dist/win-unpacked` from `ui`, and copies the result to `PREPACKAGED_INSTALLER`. That proves the macro under `-WX` (AC-114.4) with no FFmpeg build. If `--prepackaged` refuses, rows 5 and 6 move behind row 23 and use `NEW_INSTALLER`, and the coordinator records that in an ECN.

### 4. Docker and the real build (rows 13 to 15)

Mat runs the install, from Docker's official page, in the Ubuntu distro:

```bash
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin
```

The Ubuntu user is already in a `docker` group and systemd is already on, so nothing else changes. Open a new WSL session afterwards.

Row 14 launches the driver detached, because a background task in this harness dies at two hours:

```powershell
Start-Process -WindowStyle Hidden wsl.exe -ArgumentList '-d Ubuntu -e python3 -I /mnt/p/av-kit/tools/build_ffmpeg_nodvd.py --work ~/av-kit-ffmpeg --out /mnt/c/Temp/av-kit/rc2/ffmpeg-build --log /mnt/c/Temp/av-kit/rc2/ffmpeg-build-run.log'
```

It's one string because `Start-Process` joins an argument array without quoting. `wsl.exe -e` runs no shell, so there's nothing to escape. That process holds the WSL session open, and the coordinator watches `exit-code.txt`. A failed build leaves its log, and `--resume` keeps `.cache`. D-265 applies.

### 5. Source set (row 20)

```powershell
rtk proxy uv run python tools/assemble_ffmpeg_source.py --work C:/Temp/av-kit/rc2/ffmpeg-src --ffmpeg-exe C:/Temp/av-kit/rc2/ffmpeg-built/ffmpeg.exe
```

RC1's run took about an hour and made a 992,681,460 B archive. RC1's work folder isn't reused, because it's that release's evidence.

### 6. Real installer (row 23)

`build-installer.ps1` is RC1's `build-rc.ps1` with these differences: `$cachedArchive` is `BUILD_OUT/NODVD_ASSET`, `$record` is `BUILD_RECORD`, and it runs `ABSENCE_GATE --bin-dir packaging/ffmpeg-win64` straight after `-ExtractOnly`. It deletes `ui/dist`, which is why row 0 keeps `RC1_INSTALLER`. `build-identity.py` is RC1's with `BUILD_SCRIPT` repointed at this file. `tools/`, `packaging/` and `.gitattributes` edits move the identity, so they must all land before this row. Docs, tests and `tools/smoke_packaged_rc.py` don't.

### 7. Publication (rows 26, 27)

`publish-ffmpeg-nodvd.md` gives exact commands for D-251's ruling: create the fork, push the recipe commit under the noreply identity with its `^{tree}` equal to `RECIPE_TREE`, then `gh release create` with the zip, `SOURCE_ARCHIVE` and clear source directions in the notes. Publishing comes before pushing the pin commit, so the pin is never dead on `main`. The new URL can be written first because builds read the cached zip with `-ExtractOnly`. Row 27 sits after H1-7b in the task table because it runs only after review and only on Mat's words. It holds `[B]` with a `### B-27` block until then.

### Plan-local scripts

Written with their rows and kept in this plan folder:

- `baseline.ps1` (row 0)
- `red-check.py`, `identity.py` (row 0)
- `repackage.ps1` (row 4)
- `install-roundtrip.ps1` (row 5)
- `absence-negatives.ps1` (row 9)
- `absence-built.ps1` (row 15)
- `build-installer.ps1`, `build-identity.py` (row 23)
- `publish-ffmpeg-nodvd.md` (row 26)
- `session-gate.ps1` (H1-2)

### Session gate (H1-2)

`session-gate.ps1` is RC1's shape: one receipt per step in `C:/Temp/av-kit`, fail-fast, later steps printed `not_run`, `TMP` and `TEMP` set as in §1, `ELECTRON_RUN_AS_NODE` cleared.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`), `build-identity-selftest`, `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `state-render`, `build-record` (`build-identity.py --verify-record`) |
| Skipped, with reason | `openapi`: no `packages/api` change. `mcp-types`, `mcp-tests`, `mcp-build`, `mcp-audit`: no MCP change; the audit is required before the version bump, which is MEU-125. `ui-electron`: no main, preload or renderer change, and `packaged-app-smoke.mjs` launches the real packaged Electron in row 24. |

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | A build-input edit lands after row 23 | S8 applies |
| S3 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S4 | `HEAD` moves from `baseline.sha`, or a path outside `baseline-dirty.txt` and this plan appears | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | Before any install: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` or `...\Explorer\StartupApproved\Run` has `com.avkit.app`; an av-kit Uninstall entry exists; `C:\Temp\av-kit\rc2\install` exists; `%LOCALAPPDATA%\Programs\av-kit` holds anything; a Desktop or Start Menu `av-kit.lnk` exists; `av-kit.exe` is running; or `%LOCALAPPDATA%\av-kit-ui-updater` holds anything but the known copy | Skip the install, record `[B]`, list it for Mat |
| S6 | An uninstall leaves something else behind, or `%LOCALAPPDATA%\av-kit` loses a top-level entry | Report with the snapshot diff; don't retry |
| S7 | Codex is unavailable or the ledger refuses | Mat |
| S8 | `build-identity.py --verify-record` mismatch | Rerun rows 23 and 24; never edit the record |
| S9 | The recipe, generator or `makeimage` check refuses | Never bypass. Report to Mat; a changed `RECIPE_TREE` needs D-254's recorded amendment |
| S10 | The build fails twice, or passes 24 hours of machine time (D-265) | Stop and report. MEU-114 stands and MEU-113 stays open |
| S11 | `ABSENCE_GATE` fails on a real build | Stop. Never widen the rule; report which needle and where |
| S12 | The real source assembly can't find a dependency at its pinned commit | Report to Mat. Nothing is published without the complete source |

## Decision Log

> [!WARNING]
> D-246 and D-251 need Mat. The rest pass the obviousness test and are recorded here with their reasons. Carried from the grouping and not relisted in the block, because the grouping's rows hold them: D-240 (numbering), D-242 (exit codes ride in MEU-113), D-243 (rc.2 is its own MEU), D-244 (this session first) and D-248 (Mat's "Proceed" as the scoping review's confirmation). D-214 and D-228 are in `.agent/context/known-issues.yaml`. D-246 asked two questions in the grouping; this plan keeps the build host under D-246 and splits the zip's home into D-251.

```yaml
decision_log:
  - id: D-246
    stage: grouping
    question: "Where does the FFmpeg build run?"
    resolution: human
    class: externally-blocked
    chosen: "pending Mat; recommended Docker Engine in WSL Ubuntu"
    source_tag: Research-backed
    precedents: ["docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md:495 — the D-101 brief weighed a custom build: av-kit takes on the recipe, the toolchain and security updates", "docs/build-plan/07-distribution.md:327 — stock BtbN re-pin, superseded for libdvdcss by D-214"]
    research: { engine: tavily, sources: ["https://docs.docker.com/engine/install/ubuntu — official install and purge steps; Ubuntu 24.04 supported", "https://docs.github.com/en/actions/reference/limits — a job stops at 6 hours", "https://github.com/BtbN/FFmpeg-Builds/issues/598 — maintainer: build.sh fetches the stock image if makeimage failed"] }
    reasoning: "This machine has 24 vCPU, 30 GB of RAM and 902 GB free in WSL, with no job limit, and nothing goes outward until the result is good. See the brief."
  - id: D-251
    stage: planning
    question: "Where does the built zip live, so the pin's URL can reach it?"
    resolution: human
    class: one-way-door
    chosen: "pending Mat; recommended a release on a fork of BtbN/FFmpeg-Builds under Mat's account"
    source_tag: Research-backed
    precedents: ["docs/releases/publish-checklist-v0.1.0-rc.1.md:276-296 — D-101's section 6(d) routes and source availability", ".agent/context/known-issues.yaml FFMPEG-PIN-URL-404 — a dead pin link held a release"]
    research: { engine: tavily, sources: ["https://www.gnu.org/licenses/gpl-3.0.en.html — section 6(d): source may be on a different server with clear directions next to the object code", "https://stackoverflow.com/questions/5207269 — release assets are the usual home for large binaries"] }
    reasoning: "A fork shows the recipe change in GitHub's compare view, keeps av-kit's Releases page clean, and its URL is live whatever happens to rc.2. See the brief."
  - id: D-252
    stage: planning
    question: "How are the DVD scripts turned off?"
    resolution: autonomous
    class: two-way
    chosen: "A patch that adds return -1 as the first line of ffbuild_enabled in all three scripts"
    source_tag: Research-backed
    precedents: ["tools/assemble_ffmpeg_source.py:202 — enabled_for_build reads a plain return -1 as off"]
    research: { engine: tavily, sources: ["https://github.com/BtbN/FFmpeg-Builds/issues/598 — maintainer: flat out removing scripts will make image generation fail"] }
    reasoning: "It takes the off path LGPL builds use, so generate.sh writes the disable flags. Deleting the scripts breaks generation, and removing echo dvd alone leaves the scripts reading as on."
  - id: D-253
    stage: planning
    question: "Which FFmpeg commit is built?"
    resolution: autonomous
    class: two-way
    chosen: "The current pin, 8dca1586f468"
    source_tag: Local Canon
    precedents: ["tools/assemble_ffmpeg_source.py:40 — the pinned commit", "docs/build-plan/07-distribution.md:334 — the recipe at the pinned commit"]
    research: { engine: none, sources: [] }
    reasoning: "DVD stays the only change between RC1's FFmpeg and this one, so any behaviour change has one suspect."
  - id: D-254
    stage: planning
    question: "How much of the toolchain comes from the recipe?"
    resolution: autonomous
    class: two-way
    chosen: "All of it: no QUICKBUILD, crosstool-NG pinned, REGISTRY_OVERRIDE set"
    source_tag: Research-backed
    precedents: ["tools/assemble_ffmpeg_source.py:53 — the crosstool-NG commit the config was saved with"]
    research: { engine: tavily, sources: ["https://github.com/BtbN/FFmpeg-Builds/issues/598 — the stock-image fallback"] }
    reasoning: "BtbN's registry images float and could hold anything, which would defeat the source set. If commit b1a94f6 can't build, the coordinator drops that hunk, re-measures RECIPE_TREE in a recorded amendment, and keeps the README's float paragraph."
  - id: D-255
    stage: planning
    question: "What does the absence check read?"
    resolution: autonomous
    class: two-way
    chosen: "The binaries, the zip and the source archive, with real stock negatives"
    source_tag: Local Canon
    precedents: ["C:/Temp/av-kit/s49-stock-zip-scan.txt — which members hold which strings"]
    research: { engine: none, sources: [] }
    reasoning: "D-214's Done-when names all three. The zip rule follows the measured scan, so documentation can't cause a false refusal."
  - id: D-256
    stage: planning
    question: "What are the asset and tag called?"
    resolution: autonomous
    class: two-way
    chosen: "A -nodvd suffix on BtbN's asset name, and tag ffmpeg-n8.1.3-27-g8dca1586f4-nodvd"
    source_tag: Local Canon
    precedents: ["tools/assemble_ffmpeg_source.py:35 — the stock asset name"]
    research: { engine: none, sources: [] }
    reasoning: "The stock name would be identical to BtbN's and hide what the file is."
  - id: D-257
    stage: planning
    question: "What happens to deps_report's BtbN-only pattern and the README's advice?"
    resolution: autonomous
    class: two-way
    chosen: "Any GitHub release URL matches, and the advice is replaced by the driver"
    source_tag: Local Canon
    precedents: ["tools/deps_report.py:32 — the pattern", "README.md:211-216 — the advice"]
    research: { engine: none, sources: [] }
    reasoning: "Both would break or undo D-214 whichever home D-251 picks, as long as it's GitHub."
  - id: D-258
    stage: planning
    question: "How does the macro remove the copy?"
    resolution: autonomous
    class: two-way
    chosen: "Delete through the template's own define, then a non-recursive RMDir, inside the not-updated guard"
    source_tag: Local Canon
    precedents: ["ui/build/installer.nsh — customUnInstall", "ui/electron-builder.yml:18 — deleteAppDataOnUninstall stays false"]
    research: { engine: tavily, sources: ["https://www.electron.build/docs/nsis — the uninstaller semantics"] }
    reasoning: "No recursive delete on an environment-derived path. A folder holding anything else stays."
  - id: D-259
    stage: planning
    question: "How are x264 and x265 both proved?"
    resolution: autonomous
    class: two-way
    chosen: "Direct encodes in tools/smoke_packaged_rc.py, beside the product job"
    source_tag: Local Canon
    precedents: ["packages/api/src/avkit_api/schemas/conversions.py:19-28 — no codec field", "packages/core/src/avkit_core/services/conversion.py:411-416 — software prefers libx265"]
    research: { engine: none, sources: [] }
    reasoning: "The product can't reach x264 on this binary. Adding a codec field for a test would change the API contract."
  - id: D-260
    stage: planning
    question: "Which version do these builds carry?"
    resolution: autonomous
    class: two-way
    chosen: "App version stays 0.1.0-rc.1, ARCHIVE_NAME moves to rc.2, RC1's installer is preserved, and nothing is uploaded"
    source_tag: Local Canon
    precedents: ["docs/build-plan/07-distribution.md:362 — MEU-125 moves the version", "tests/unit/test_release_packaging.py:27 — one version across surfaces"]
    research: { engine: none, sources: [] }
    reasoning: "The source archive belongs to rc.2, and no test ties its name to the app version. The local build stays on this PC."
  - id: D-261
    stage: planning
    question: "What does the session gate cover?"
    resolution: autonomous
    class: two-way
    chosen: "The set in Verification Plan, Session gate, with openapi, mcp and ui-electron skipped for stated reasons"
    source_tag: Local Canon
    precedents: [".agent/docs/commands.md:190-207 — the D6 stages", "AGENTS.md:82 — static, targeted, then one fresh full gate"]
    research: { engine: none, sources: [] }
    reasoning: "No API, MCP or app source changes. The packaged round trip launches real Electron."
  - id: D-262
    stage: planning
    question: "How is the patched recipe identified?"
    resolution: autonomous
    class: two-way
    chosen: "By git tree hash, not by a commit"
    source_tag: Local Canon
    precedents: ["C:/Temp/av-kit/s49-recipe-probe-win.txt, s49-recipe-probe-wsl.txt — the same hash from both"]
    research: { engine: none, sources: [] }
    reasoning: "A tree has no author or date, so it needs no identity and doesn't depend on D-251. The fork's commit must carry the same tree."
  - id: D-263
    stage: planning
    question: "What language is the driver in?"
    resolution: autonomous
    class: two-way
    chosen: "Python with the standard library only"
    source_tag: Local Canon
    precedents: ["tools/assemble_ffmpeg_source.py — the same style, and tested with fakes"]
    research: { engine: none, sources: [] }
    reasoning: "It's testable on Windows with a fake runner and also runs on a Linux runner. Only the patch then needs an LF rule."
  - id: D-264
    stage: planning
    question: "Does MEU-114 wait for the FFmpeg build?"
    resolution: autonomous
    class: two-way
    chosen: "No: it's proved first on a repackaged installer, and the round trip repeats on the full build"
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:139 — the split flag", "ui/dist/win-unpacked — RC1's unpacked app is still on disk"]
    research: { engine: none, sources: [] }
    reasoning: "The build's time is the largest unknown, and MEU-114 doesn't depend on it."
  - id: D-265
    stage: planning
    question: "When does the coordinator stop trying the build?"
    resolution: autonomous
    class: two-way
    chosen: "After two full runs or 24 hours of machine time, whichever comes first"
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:138 — the time isn't known"]
    research: { engine: none, sources: [] }
    reasoning: "It keeps an unbounded job bounded and sends the choice back to Mat. Mat can change the number; it's raised in User Review Required."
```

### D-246 — Where does the FFmpeg build run?

**Recommendation:** Docker Engine in WSL Ubuntu on this PC. It has the most power, no job limit and fast retries, and nothing goes outward until the result is good. **Reversibility:** two-way; Docker's official purge removes it, though the Ubuntu virtual disk can grow and doesn't shrink by itself. **Default if unanswered:** MEU-114, the exit codes and every offline row proceed; rows 13 to 24 stay `[B]`.

**Precedents:** the D-101 brief weighed a custom build at `docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md:495`. **Research:** tavily, read below. Status quo (the stock BtbN build) is ruled out by D-214.

Measured here on 2026-11-04: Ubuntu 24.04.3, 24 vCPU, 30 GB of RAM, 902 GB free, systemd on, the user already in a `docker` group, no docker installed, and `sudo` needs Mat's password.

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|---|---|---|---|---|
| Docker Engine in WSL Ubuntu (recommended) | https://docs.docker.com/engine/install/ubuntu | — | — | ✅ |
| GitHub runner on a public repo | https://docs.github.com/en/actions/reference/limits ; https://craci.com/compare/github-actions-runner-providers | No change to this PC; clean machine; public logs; attestation possible | 4 vCPU and 16 GB; a job stops at 6 hours against an unproven cold build, and BtbN gets around that with staged jobs and registry caches; a workflow needs a push to `main` or a fork before it can run | ⚠️ |
| Docker Desktop on Windows | https://docs.docker.com/engine/install/ubuntu | A familiar GUI | A second, heavier install with its own licence terms, for the same WSL engine | ❌ |

**Install commands and how to reverse them:** §Verification Plan 4. To remove: `sudo apt purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-ce-rootless-extras`, then `sudo rm -rf /var/lib/docker /var/lib/containerd` and remove the source file and keyring.

### D-251 — Where does the built zip live?

The pin's URL has to point at the 194 MB zip. **Publishing it anywhere is object-code distribution under the GPL,** so `SOURCE_ARCHIVE` or clear directions to it go up in the same step and stay as long as needed.

**Recommendation:** A, a release on a fork of `BtbN/FFmpeg-Builds` under Mat's account. It shows the recipe change in GitHub's compare view, keeps av-kit's Releases page for av-kit, and its URL stays live whatever happens to rc.2. **Reversibility:** one-way once published, as the zip may have been downloaded and the source duty follows it. Before publishing, the choice is free, and it only sets the URL and tag. **Default if unanswered:** the build and gates run; rows 16, 17, 26 and 27 stay `[B]`, along with what depends on them.

**Precedents:** `docs/releases/publish-checklist-v0.1.0-rc.1.md:276-296` (D-101's routes, available "for as long as needed"); `FFMPEG-PIN-URL-404` (a dead pin link held a release). **Research:** tavily; GPLv3 §6(d) (source may sit on a different server, with clear directions next to the object code).

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|---|---|---|---|---|
| A: fork with a release (recommended) | https://github.com/BtbN/FFmpeg-Builds ; GPLv3 §6(d) | — | — | ✅ |
| B: a dedicated pre-release in av-kit | https://docs.github.com/en/rest/releases/releases | No new repository, and the patch is already in that repo | Clutters the `/releases` page the README links to; `/releases/latest` skips pre-releases, so that link can't simply move; worst if RC1 goes to draft, when the page shows only FFmpeg | ⚠️ |
| C: a new small repository, not a fork | GPLv3 §6(d) | Not tied to BtbN's network | One more repository with no compare view, though the patch is the diff | ⚠️ |
| D: attach it to the rc.2 release | `FFMPEG-PIN-URL-404` | No new repository or release entry, and the source is already there | 404s until rc.2 publishes; an extra asset users can mistake for the app; that release must stay up | ❌ |

The URL under A would be `https://github.com/matbanik/FFmpeg-Builds/releases/download/ffmpeg-n8.1.3-27-g8dca1586f4-nodvd/ffmpeg-n8.1.3-27-g8dca1586f4-win64-gpl-8.1-nodvd.zip`. Forks turn Actions and scheduled workflows off by default, so nothing runs there. A tracked file in the repository, or LFS, doesn't fit a 194 MB binary.

**One sentence to save a later stop:** "Publish when the gates and the review pass" lets row 27 run without another message. Without it, row 27 waits at `[B]` for Mat's words.

## Research References

- BtbN recipe: https://github.com/BtbN/FFmpeg-Builds (README, and `5031c6f`'s scripts read from `C:/Temp/av-kit/rc1/ffmpeg-src/tars/ffmpeg-builds.tar`). Primary.
- BtbN maintainer on removing scripts and the stock-image fallback: https://github.com/BtbN/FFmpeg-Builds/issues/598. Primary.
- Docker Engine on Ubuntu: https://docs.docker.com/engine/install/ubuntu. Official.
- GitHub Actions limits: https://docs.github.com/en/actions/reference/limits. Official.
- GitHub releases: https://docs.github.com/en/rest/releases/releases. Official.
- electron-builder NSIS: https://www.electron.build/docs/nsis. Official.
- GPLv3 §6(d): https://www.gnu.org/licenses/gpl-3.0.en.html. Primary.
- libdvdcss background: https://en.wikipedia.org/wiki/Libdvdcss ; https://jbkempf.com/blog/2025/DVD_audio_edition. Secondary, context only.
- Runner comparison: https://craci.com/compare/github-actions-runner-providers ; https://github.com/orgs/community/discussions/210874. Secondary.
- Docker in WSL without Desktop: https://nickjanetakis.com/blog/install-docker-in-wsl-2-without-docker-desktop ; https://forums.docker.com/t/running-docker-without-docker-desktop/134922. Secondary.

## Planning receipts

- Recipe patch: `C:/Temp/av-kit/s49-recipe-probe-wsl.txt` and `s49-recipe-probe-win.txt`. Upstream tree `322b4b725d2e1a6bd52719e751ff3766de406b2c`, patched `RECIPE_TREE`, the same from both. The assembler reads stock as on and all three patched scripts as off.
- `generate.sh`'s off path, by reading only: `C:/Temp/av-kit/s49-generate-sh.txt`. Row 12 runs it.
- Stock zip scan, 44 members: `C:/Temp/av-kit/s49-stock-zip-scan.txt`. All three `.exe` files hold every needle; four HTML docs name `--enable-libdvd` and `dvdvideo`, and none names `libdvdcss` or `DVDCSS_`.
- Exit codes today: `C:/Temp/av-kit/fetch-exit-blank-sha.txt`, `fetch-exit-sha-mismatch.txt`, each exit 1.
- Issue evidence: `C:/Temp/av-kit/issue-dvd/evidence.txt`.
- Research: `C:/Temp/av-kit/s49-research-q1.txt` to `s49-research-q6.txt`. Precedent sweep: `C:/Temp/av-kit/precedent-sweep.txt`.
- Measured on 2026-11-04: `HEAD` `d287c55`; `%LOCALAPPDATA%\av-kit-ui-updater\installer.exe` 340,348,020 B, SHA-256 `beabc509…`; `%LOCALAPPDATA%\Programs\av-kit` absent; `ui/dist/win-unpacked` present; no `docker`, `podman` or `nerdctl` in WSL or on Windows.
- Not run at plan time: the recipe's scripts, Docker, any install.

## Validation stage contract

Static: `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths`, `build-identity-selftest`, `red-check-selftest`. Targeted: the named test files in each Red and Green row. Fresh full: `py-tests`, `ui-tests`, `ui-build`, `state-render`, `build-record`. Runtime: rows 6 and 24 (real NSIS install, real packaged Electron), row 12 (real generator) and rows 14, 15, 20 and 23 (real build, real assembly), bound to the same tree through `BUILD_RECORD`, which the gate's `build-record` step checks. Identity comes from `identity.py`, independent of the receipts. Blocking: all, native shell PowerShell, `evidence.v1` output. Intermediate reuse stays off.
