# Publish checklist: v0.1.0-rc.2

Every step below is outward or decides what goes outward, so each one waits for Mat's go-ahead.
Session 57 (MEU-125) built and checked this release candidate and ran none of these steps.

Run the commands in `pwsh` from the root of `P:/av-kit`, on the PC that built the installer,
unless a step says otherwise. Run the steps in order. Steps 5 and 6 run from the draft's own
assets, before step 7 publishes it. Release notes: [`v0.1.0-rc.2.md`](v0.1.0-rc.2.md).

## Where things stand

| Item | Value |
|---|---|
| Installer | `ui/dist/av-kit-Setup-0.1.0-rc.2.exe`, 340,362,828 B |
| SHA-256 | `547b1f5019e79f2b2a44fbc79aedc16c45bf26c753c1ada9845dcdd8037f74c8` |
| Build record | [`v0.1.0-rc.2-build-record.json`](v0.1.0-rc.2-build-record.json), `build_inputs` `df8c41a9079c6a8bd431e8cb5e8315b3b1d3171a7df327b1e88400ebb9c7f4d3` |
| FFmpeg in that build | BtbN `n8.1.3-27-g8dca1586f4`, win64 GPL, release `autobuild-2026-10-31-12-59`, the same pin as `v0.1.0-rc.1` (D-101). It links libdvdcss, which av-kit never uses (D-266, `FFMPEG-LIBDVDCSS-BUNDLED`). |
| FFmpeg source | `C:/Temp/av-kit/rc1/ffmpeg-src/av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz`, 992,681,460 B, unchanged since `v0.1.0-rc.1`. It keeps its rc.1 name, and `THIRD_PARTY_NOTICES.md` points at the rc.2 release for it (D-465). |
| Its SHA-256 | `953a62373693e388a853ee2c6dbfadf4ce12e7f4aeb13b86e26f179b48d07284` |
| Code signing | None. SmartScreen warns, and the notes say so. |

**Known limitation, accepted for now:** `YOUTUBE-CAPTIONS-IP-BLOCK`. YouTube blocked caption
requests from this PC's network when RC1 was tested. On 2026-11-09 the gate's live audit fetched
and compiled one video's captions on the same network, through the backend of a checkout, but the
installed app's Transcript path isn't verified end to end on this build. The notes disclose both,
say the other-network check hasn't run (D-466, D-475), and leave out RC1's claim that the cause is
the network. Step 6 is that check.

**Left out of the notes on purpose:** `BACKEND-READY-BEFORE-LISTEN` and `GUI-READY-CHUNK-BOUNDARY`,
because neither has been seen in the app.

**Rules that stop the release:**

- A `--verify-record` mismatch: rebuild and recheck (the plan's rows 3 to 7). Never edit the record.
- Any other session's commits or paths appearing in this work: stop and ask Mat.
- A failure in step 5 or 6 that needs a new installer: stop. Mat decides whether to publish.

## 1. Commit and push `main`

The session commits only on Mat's words, with the message it drafted at
`C:/Temp/av-kit/commit-draft.txt` and no AI attribution trailer. If that commit has landed, skip to
the push.

It's public the moment it lands, so scan first. `OLD_ADDRESS` holds the old personal address, in
this shell only. Never write it to a file.

```powershell
if (-not $env:OLD_ADDRESS) { throw 'Set $env:OLD_ADDRESS in this shell first.' }
git grep -n -I --untracked -i -F -e $env:OLD_ADDRESS     # must print nothing
git grep -n -I --untracked -l -E -e '@gmai[l]'           # must list only plan task.md files, which hold the search pattern
git config user.email                                    # must be the noreply address
```

Then commit if needed, push and check CI at that commit:

```powershell
$env:ELECTRON_RUN_AS_NODE = $null
pwsh -NoProfile -File .agent/skills/git-workflow/scripts/agent-commit.ps1 -Message (Get-Content -Raw C:/Temp/av-kit/commit-draft.txt)
git log -1 --format='%H %ae %ce'                         # both addresses must be the noreply address
git push origin main
gh run list --repo matbanik/av-kit --commit (git rev-parse HEAD) --json name,status,conclusion
```

Wait until every run has `status` `completed` and `conclusion` `success`.

## 2. Verify the build against the pushed commit

```powershell
git fetch origin main
git rev-parse HEAD origin/main                           # both lines must match
uv run --frozen python docs/execution/plans/2026-11-08-release-rc2/build-identity.py --ref origin/main --verify-record docs/releases/v0.1.0-rc.2-build-record.json
```

It must print `build record: matches`, which ties the pushed commit to the installer's bytes.

## 3. Tag

```powershell
git tag -a v0.1.0-rc.2 -m 'av-kit 0.1.0-rc.2'
git cat-file -p v0.1.0-rc.2                              # the tagger must be the noreply address
git push origin v0.1.0-rc.2
```

The tag push also starts `build-windows.yml`, which builds without FFmpeg and uploads nothing. Its
installer isn't the release.

## 4. Create the draft

Upload the installer, `THIRD_PARTY_LICENSES.txt` and the FFmpeg source archive, which D-101
requires beside every installer that carries this FFmpeg. The archive is about 1 GB, so the upload
takes a while. `latest.yml`, the `.blockmap`, `builder-debug.yml` and `win-unpacked/` stay here.

```powershell
if (-not $env:OLD_ADDRESS) { throw 'Set $env:OLD_ADDRESS in this shell first.' }
if (Select-String -Path packaging/dist/THIRD_PARTY_LICENSES.txt -SimpleMatch $env:OLD_ADDRESS -Quiet) { throw 'The old address is in the licence list.' }
if ((Get-FileHash -Algorithm SHA256 ui/dist/av-kit-Setup-0.1.0-rc.2.exe).Hash -ne '547b1f5019e79f2b2a44fbc79aedc16c45bf26c753c1ada9845dcdd8037f74c8') { throw 'The installer is not the recorded one.' }
$source = 'C:/Temp/av-kit/rc1/ffmpeg-src/av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz'
if ((Get-FileHash -Algorithm SHA256 $source).Hash -ne '953a62373693e388a853ee2c6dbfadf4ce12e7f4aeb13b86e26f179b48d07284') { throw 'The source archive is not the one that was checked.' }
gh release create v0.1.0-rc.2 --draft --prerelease ui/dist/av-kit-Setup-0.1.0-rc.2.exe packaging/dist/THIRD_PARTY_LICENSES.txt $source --repo matbanik/av-kit --verify-tag --title 'av-kit 0.1.0-rc.2' --notes-file docs/releases/v0.1.0-rc.2.md
gh release view v0.1.0-rc.2 --repo matbanik/av-kit --json isDraft,isPrerelease,assets
```

`isDraft` and `isPrerelease` must both be `true`, with the three assets listed.

## 5. Clean-machine check

Run this on a Windows PC that has never had av-kit, from the draft's asset. A draft's assets need
`gh` signed in as Mat.

```powershell
gh release download v0.1.0-rc.2 --repo matbanik/av-kit --pattern 'av-kit-Setup-0.1.0-rc.2.exe' --dir av-kit-rc2
(Get-FileHash -Algorithm SHA256 av-kit-rc2/av-kit-Setup-0.1.0-rc.2.exe).Hash   # must match the build record
```

Then check by hand:

1. Run the installer, through SmartScreen's warning. Open av-kit from the Start Menu.
2. **Settings** shows FFmpeg available, with its path inside the install folder, and the TTS device
   offers only `auto` and `cpu`.
3. **First voice model into an empty folder:** confirm that `%USERPROFILE%\.avkit\models` doesn't
   exist or holds no voice model. On the TTS page, ONNX INT8 is preselected and PyTorch FP32 is
   listed as unavailable. Download INT8, generate speech and play it.
4. **A real F2 capture:** with av-kit in the tray, press <kbd>F2</kbd> from another app, drag a
   region, add an arrow, pixelate something and save. Reopen the shot on the Capture page.
5. Download one short video. The row shows the quality that arrived. Click **Open file**.
6. Convert that video: compress it, cut a few seconds, and extract its audio as AAC, which must end
   in `.m4a`.
7. Uninstall from Windows Settings. The program files, the shortcuts and
   `%LOCALAPPDATA%\av-kit-ui-updater` go; `%LOCALAPPDATA%\av-kit`, `%APPDATA%\av-kit-ui` and
   `%USERPROFILE%\.avkit\models` stay.

If anything fails, correct the release notes' "How this build was tested" section with what
happened before step 7. A failure that needs a new installer stops the release.

When every item passes, replace the notes' sentence that starts `Not checked by those runs` with
what ran, and the sentence that ends `before this release is published.` under "Corrections to the
0.1.0-rc.1 notes" with the date of this check.

## 6. Transcript recheck

This is D-216's open check, and the reason the notes hold D-466's wording. Run it in an app
installed from the draft's asset, from a network other than the one RC1 was blocked on (a phone
hotspot will do), and note which network it was.

1. On the **Transcript** page, paste a small public channel's URL into **Channel URL**. Click **Add**,
   then **Start**.
2. Wait for the card to count transcripts, such as `3 / 3 transcripts`. A failed video now shows its
   reason.
3. Click **Compile (3 done)**, then **View compiled**.
4. Read the file that opens. It must hold the videos' real spoken words and real video titles.

| What you saw | What it means | What to do |
|---|---|---|
| The compiled file holds the videos' real words | Transcript runs end to end on this build from that network. | Remove the section `Transcript on this build` from the notes. Under Known problems, replace the item that starts `The installed app's Transcript path isn't verified` (two lines) with: Transcript ran end to end in an app installed from this page on `<date>`, from `<network>`. YouTube can block caption requests from some networks; if it does, try again later or from another network, then choose **Resume**. (`YOUTUBE-CAPTIONS-IP-BLOCK`) |
| The job paused with YouTube's block message on the other network too | The block isn't only the test network's, or the cause is elsewhere. | In the section `Transcript on this build`, replace the line `Transcript hasn't been tried from another network.` with: On `<date>`, the installed app's Transcript job was blocked from `<network>` too, so the block isn't limited to the test network and its cause isn't confirmed. Replace the section's last paragraph, which starts `The maintainer rechecks Transcript`, with: This release goes out with that gap by the maintainer's decision. Keep the other lines and the Known problems line, which stay true. Mat decides whether to publish. |
| The card counted transcripts, but the compiled file has no real words | The build may be wrong. | Stop. Mat decides whether to publish. |
| You didn't run this check | Transcript stays unverified, and the notes stay as written. | Publish with the notes as they are, or wait. |

To tell YouTube's block from a fault on this PC, the session gate's audit and its rule can run from
a checkout. They make real YouTube requests (D-464) and use the real screen:

```powershell
$env:ELECTRON_RUN_AS_NODE = $null
$plan = 'docs/execution/plans/2026-11-08-release-rc2'
$auditOut = 'C:/Temp/av-kit/s57-D6-mcp-audit'
npm --prefix mcp-server run build
pwsh -NoProfile -File "$plan/audit-clear.ps1" -Dir $auditOut
if ($LASTEXITCODE -ne 0) { throw 'audit-clear failed: stop.' }
npm --prefix mcp-server run audit -- --mode authoritative --baseline "$PWD/.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json" --report "$auditOut/mcp-tool-audit-report.md" --out $auditOut --agent claude-code
$LASTEXITCODE
uv run --frozen python "$plan/audit-rule.py" "$auditOut/mcp-audit-summary.json" --head (git rev-parse HEAD)
$LASTEXITCODE
```

Audit exit 1 with rule exit 0 means YouTube's block, in MEU-116's paused shape, is still the only
finding. Audit exit 0 means the block has lifted for this network. Anything else stops the release.
A tolerated run proves a block exists, not that Transcript works, so it can't take the warning out
of the notes.

## 7. Publish the draft

```powershell
if (Select-String -Path docs/releases/v0.1.0-rc.2.md -SimpleMatch 'the result is added here' -Quiet) { throw 'The notes still wait for the gate result.' }
$assets = (gh release view v0.1.0-rc.2 --repo matbanik/av-kit --json assets | ConvertFrom-Json).assets.name
foreach ($name in 'av-kit-Setup-0.1.0-rc.2.exe', 'THIRD_PARTY_LICENSES.txt', 'av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz') {
    if ($assets -notcontains $name) { throw "$name is not attached." }
}
gh release edit v0.1.0-rc.2 --repo matbanik/av-kit --notes-file docs/releases/v0.1.0-rc.2.md --draft=false
gh release view v0.1.0-rc.2 --repo matbanik/av-kit --json isDraft,isPrerelease,url,assets
```

`isDraft` must be `false` and `isPrerelease` `true`. If steps 5 or 6 changed the notes, commit and
push them too; `**.md` changes skip CI.

## 8. Mark v0.1.0-rc.1 as replaced (D-467)

Mat ruled D-467 option A on 2026-11-09: keep `v0.1.0-rc.1` and its assets, including its installer
and the source archive beside it, and say it's replaced. This keeps its links working and its GPL
source beside its binary.

```powershell
$old = (gh release view v0.1.0-rc.1 --repo matbanik/av-kit --json body --jq .body) -join "`n"
$file = 'C:/Temp/av-kit/rc1-notes-replaced.md'
$line = 'Replaced by v0.1.0-rc.2: https://github.com/matbanik/av-kit/releases/tag/v0.1.0-rc.2'
Set-Content -LiteralPath $file -Value ($line + "`n`n" + $old) -Encoding utf8NoBOM -NoNewline
Get-Content -LiteralPath $file -TotalCount 3                 # the first line is the replaced line
gh release edit v0.1.0-rc.1 --repo matbanik/av-kit --notes-file $file --latest=false
gh release view v0.1.0-rc.1 --repo matbanik/av-kit --json isDraft,isPrerelease,assets
```

`v0.1.0-rc.1` stays a published prerelease with its assets. Nothing here deletes or drafts it.
