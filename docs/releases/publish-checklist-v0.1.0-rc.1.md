# Publish checklist: v0.1.0-rc.1

Every step below is outward or decides what goes outward, so each one waits for Mat's go-ahead.
Nothing here makes the repository public or reviews its exposure; both are done.

Run the commands in `pwsh` from the root of `P:/av-kit`, on the PC that built the installer,
unless a step says otherwise. Run the steps in order, except steps 6 and 7: Mat runs those last,
from the published release. Release notes: [`v0.1.0-rc.1.md`](v0.1.0-rc.1.md).

## Where things stand

| Item | Value |
|---|---|
| Installer | `ui/dist/av-kit-Setup-0.1.0-rc.1.exe`, 340,348,020 B |
| SHA-256 | `beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7` |
| Build record | [`v0.1.0-rc.1-build-record.json`](v0.1.0-rc.1-build-record.json) |
| FFmpeg in that build | BtbN `n8.1.3-27-g8dca1586f4`, win64 GPL, release `autobuild-2026-10-31-12-59`. Mat ruled D-101 on 2026-11-04. |
| FFmpeg source | `C:/Temp/av-kit/rc1/ffmpeg-src/av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz`, 992,681,460 B |
| Its SHA-256 | `953a62373693e388a853ee2c6dbfadf4ce12e7f4aeb13b86e26f179b48d07284` |
| Code signing | None. SmartScreen warns, and the notes say so. |

**Known limitation, accepted for now:** `YOUTUBE-CAPTIONS-IP-BLOCK`. YouTube is blocking caption
requests from this PC's network, so the Transcript path isn't verified end to end on this build
while the block holds. The release notes disclose it. Mat accepted this for now on 2026-11-04, and
step 7 rechecks it after publishing.

**Left out of the notes on purpose:** `BACKEND-READY-BEFORE-LISTEN`, because its effect on users
hasn't been measured. It has only been seen in the audit runner.

**Waived until the release is public (Mat, 2026-11-04):** the clean-machine install, the real F2
capture and the first voice model download. The notes say none of them has run on this build. Mat
runs them from the published release, so remind Mat once step 8 is done.

**Rules that stop the release:**

- A `--verify-record` mismatch: rerun rows 10 to 12 of the plan's `task.md`. Never edit the record.
- Any other session's commits or paths appearing in this work: stop and ask Mat.

## 0. D-101 ruling

Mat ruled on 2026-11-04: keep the GPL build, re-pin it to a retained build and publish its complete
corresponding source with the release. The Decision Brief at the end of this file holds the reasons.

## 1. Apply the ruling

Done before the build this file describes. The fetch script, the `## FFmpeg` notice, the README and
`tools/assemble_ffmpeg_source.py` all name the same build, a test holds them together, and the
installer's `ffmpeg.exe -version` agrees. The release notes carry the FFmpeg text, and
`FFMPEG-GPL-BUILD` and `FFMPEG-PIN-URL-404` are closed.

## 2. Commit and push `main`

It's public the moment it lands, so scan first. `OLD_ADDRESS` holds the old personal address, in
this shell only. Never write it to a file.

```powershell
if (-not $env:OLD_ADDRESS) { throw 'Set $env:OLD_ADDRESS in this shell first.' }
git grep -n -I --untracked -i -F -e $env:OLD_ADDRESS     # must print nothing
git grep -n -I --untracked -E -e '@gmai[l]'              # must print only the search pattern in the plan's task.md
git config user.email                                    # must be the noreply address
```

Then commit with the drafted message and check CI at that commit. The repo's rule is no AI
attribution trailer.

```powershell
$env:ELECTRON_RUN_AS_NODE = $null
pwsh -NoProfile -File .agent/skills/git-workflow/scripts/agent-commit.ps1 -Message '<message from C:/Temp/av-kit/commit-draft.txt>'
git log -1 --format='%H %ae %ce'                         # both addresses must be the noreply address
gh run list --repo matbanik/av-kit --commit (git rev-parse HEAD) --json name,status,conclusion
```

Wait until every run has `status` `completed` and `conclusion` `success`.

## 3. Verify the build against the pushed commit

```powershell
git fetch origin main
git rev-parse HEAD origin/main                           # both lines must match
uv run --frozen python docs/execution/plans/2026-11-03-release-rc1/build-identity.py --verify-record docs/releases/v0.1.0-rc.1-build-record.json --ref HEAD
```

It must print `build record: matches`, which ties the pushed commit to the installer's bytes. On a
mismatch, go back to rows 10 to 12. Never edit the record.

## 4. Tag

```powershell
git tag -a v0.1.0-rc.1 -m 'av-kit 0.1.0-rc.1'
git cat-file -p v0.1.0-rc.1                              # the tagger must be the noreply address
git push origin v0.1.0-rc.1
```

The tag push also starts `build-windows.yml`, which builds without FFmpeg and uploads nothing. Its
installer isn't the release.

## 5. Create the draft

Upload the installer, `THIRD_PARTY_LICENSES.txt` and the FFmpeg source archive, which the D-101
ruling requires. The archive is about 1 GB, so the upload takes a while. `latest.yml`, the
`.blockmap`, `builder-debug.yml` and `win-unpacked/` stay here: the app has no updater, and those
files are by-products of the build.

The list and the archive hold third-party authors' addresses as they published them (77 gmail-form
addresses in the list on this build), so check that the old personal address isn't one of them. The
commands check the list. The archive was checked when it was packed, so they check that it's still
the same file.

```powershell
if (Select-String -Path docs/releases/v0.1.0-rc.1.md -SimpleMatch '[FILL-D101' -Quiet) { throw 'Fill in the FFmpeg text first (step 1).' }
if (-not $env:OLD_ADDRESS) { throw 'Set $env:OLD_ADDRESS in this shell first.' }
if (Select-String -Path packaging/dist/THIRD_PARTY_LICENSES.txt -SimpleMatch $env:OLD_ADDRESS -Quiet) { throw 'The old address is in the licence list.' }
$source = 'C:/Temp/av-kit/rc1/ffmpeg-src/av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz'
if ((Get-FileHash -Algorithm SHA256 $source).Hash -ne '953a62373693e388a853ee2c6dbfadf4ce12e7f4aeb13b86e26f179b48d07284') { throw 'The source archive is not the one that was checked.' }
gh release create --draft --prerelease v0.1.0-rc.1 ui/dist/av-kit-Setup-0.1.0-rc.1.exe packaging/dist/THIRD_PARTY_LICENSES.txt $source --repo matbanik/av-kit --verify-tag --title 'av-kit 0.1.0-rc.1' --notes-file docs/releases/v0.1.0-rc.1.md
gh release view v0.1.0-rc.1 --repo matbanik/av-kit --json isDraft,isPrerelease,assets
```

## 6. Clean-machine verification

Mat waived this until the release is public, and runs it after step 10, from the published asset,
on a Windows PC that has never had av-kit.

```powershell
gh release download v0.1.0-rc.1 --repo matbanik/av-kit --pattern 'av-kit-Setup-0.1.0-rc.1.exe' --dir av-kit-rc1
(Get-FileHash -Algorithm SHA256 av-kit-rc1/av-kit-Setup-0.1.0-rc.1.exe).Hash   # must match the build record
```

Then check by hand:

1. Run the installer, through SmartScreen's warning. Open av-kit from the Start Menu.
2. **Settings** shows FFmpeg available, with its path inside the install folder.
3. **First model provisioning into an empty cache:** confirm that `%LOCALAPPDATA%\av-kit\models` has
   no voice model. On the TTS page, pick a voice, download its model, generate speech and play it.
4. **A real F2 picker capture:** with av-kit in the tray, press <kbd>F2</kbd> from another app, drag
   a region, add an arrow, pixelate something and save. Reopen the shot on the Capture page.
5. Download one short video, then click **Open file**.
6. Convert that video with the default output folder.
7. Uninstall from Windows Settings. The program files and shortcuts go, and
   `%LOCALAPPDATA%\av-kit` stays.

Then replace `This build hasn't been run on a clean machine.` and the sentence after it in the
release notes with what happened, including any failure, and publish them with
`gh release edit v0.1.0-rc.1 --repo matbanik/av-kit --notes-file docs/releases/v0.1.0-rc.1.md`. A
failure that needs a new installer means a new release candidate, and Mat decides whether this one
stays up.

## 7. Transcript recheck

Mat accepted this limitation for now, and rechecks after step 10. Only a run through the app
installed from the published asset can take the warning out of the notes.

Use the install from step 6. On another PC, get it the same way:

```powershell
gh release download v0.1.0-rc.1 --repo matbanik/av-kit --pattern 'av-kit-Setup-0.1.0-rc.1.exe' --dir av-kit-rc1
(Get-FileHash -Algorithm SHA256 av-kit-rc1/av-kit-Setup-0.1.0-rc.1.exe).Hash   # must match the build record
```

Then check by hand in the installed app:

1. On the **Transcript** page, paste a small public channel's URL into **Channel URL**. Click **Add**,
   then **Start**.
2. Wait for the card to count transcripts, such as `3 / 3 transcripts`.
3. Click **Compile (3 done)**, then **View compiled**.
4. Read the file that opens. It must hold the videos' real spoken words, not only a heading.

| What you saw | What it means | What to do |
|---|---|---|
| The compiled file holds the videos' real words | Transcript ran end to end on the published build. | Remove the section `Transcript isn't verified on this build` from the notes, and publish them with `gh release edit v0.1.0-rc.1 --repo matbanik/av-kit --notes-file docs/releases/v0.1.0-rc.1.md`. |
| No transcripts arrived, or the card shows Failed | It could be YouTube's block or a fault. The page doesn't show which. | Run the development audit below. The notes stay as written until then. |
| The card counted transcripts, but the compiled file has no real words | The published build may be wrong. | Stop. Mat decides whether the release stays up. |
| You didn't run this check | Transcript stays unverified. | The notes stay as written. |

### Development audit

This is supplementary evidence. It runs the local MCP build and uv's Python from a checkout, not the
published app, so its result can't take the warning out of the notes. Its job here is to tell
YouTube's block from a fault. It uses real YouTube traffic and the real screen, so don't run it while
you're using the PC.

```powershell
$env:ELECTRON_RUN_AS_NODE = $null
$plan = 'docs/execution/plans/2026-11-03-release-rc1'
$auditOut = 'C:/Temp/av-kit/D6-mcp-audit'
npm --prefix mcp-server run build
pwsh -NoProfile -File "$plan/audit-clear.ps1" -Dir $auditOut
if ($LASTEXITCODE -ne 0) { throw 'audit-clear failed: stop the release.' }
npm --prefix mcp-server run audit -- --mode authoritative --baseline "$PWD/.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json" --report "$auditOut/mcp-tool-audit-report.md" --out $auditOut --agent claude-code
$LASTEXITCODE
```

On exit 1, run the rule that decides whether `YOUTUBE-CAPTIONS-IP-BLOCK` is the only thing wrong:

```powershell
uv run --frozen python "$plan/audit-rule.py" "$auditOut/mcp-audit-summary.json" --head (git rev-parse HEAD)
$LASTEXITCODE
```

| Outcome | What it means | What to do |
|---|---|---|
| Audit exit 1, rule exit 0 | Tolerated: YouTube's block is still the only finding, and Transcript stays unverified. | The notes stay as written. Recheck when the block lifts, or from a network YouTube isn't blocking. |
| Audit exit 0 | The block has lifted and the development path works, but the published app still hasn't shown real words. | The notes stay as written. Repeat the check in the installed app. If it still gets no captions, stop: Mat decides whether the release stays up. |
| Anything else | The audit or the rule refused. | Stop. Mat decides whether the release stays up. |

A tolerated run isn't a clean audit, and it doesn't check what compile writes. It proves a block
exists, not that the fetch path works.

## 8. Publish the draft

```powershell
if (Select-String -Path docs/releases/v0.1.0-rc.1.md -SimpleMatch '[FILL-' -Quiet) { throw 'The notes still hold a FILL marker.' }
$assets = (gh release view v0.1.0-rc.1 --repo matbanik/av-kit --json assets | ConvertFrom-Json).assets.name
if ($assets -notcontains 'av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz') { throw 'The FFmpeg source archive is not attached.' }
gh release edit v0.1.0-rc.1 --repo matbanik/av-kit --notes-file docs/releases/v0.1.0-rc.1.md --draft=false
gh release view v0.1.0-rc.1 --repo matbanik/av-kit --json isDraft,isPrerelease,url,assets
```

`isDraft` must be `false` and `isPrerelease` `true`.

## 9. Remove the README's "No installer yet" note

Delete these two lines at `README.md:49-50` and the blank line after them:

```markdown
> **No installer yet.** The first release candidate is being prepared. Until it's out,
> you can [build from source](#build-from-source).
```

Then commit and push the README with the final release notes. `README.md` isn't hashed into the
build identity, and `**.md` changes skip CI.

```powershell
pwsh -NoProfile -File .agent/skills/git-workflow/scripts/agent-commit.ps1 -Message 'docs: point the README at the first release candidate'
```

## 10. Repository description and topics

The wording is a proposal, for Mat to change.

```powershell
gh repo edit matbanik/av-kit --description 'Save YouTube videos and captions, read text aloud, shrink videos and mark up screenshots, all on your own Windows PC.' --add-topic windows --add-topic electron --add-topic youtube --add-topic transcripts --add-topic text-to-speech --add-topic ffmpeg --add-topic screenshot --add-topic mcp
```

## D-101: Decision Brief

**Ruled 2026-11-04.** Mat: "recommendation accepted". The price the brief asks for, measured before
any upload: 739 sources, 3,213,917,779 B before compression, 992,681,460 B packed against
GitHub's 2 GiB limit for one file. The brief below stays as Mat read it.

**Question:** Which FFmpeg licence posture does the public installer ship under? This one is Mat's
to decide, not an agent's.

**Recommendation:** Keep the GPL build, re-pin to BtbN's month-end build `autobuild-2026-10-31-12-59` (BtbN keeps each month's last build for two years, and only the last 14 dailies), and publish only once its complete corresponding source is available. GPL keeps the `libx265` and `libx264` fallback Convert already uses, and an LGPL build would barely shrink the source set: 92 repositories against 104. av-kit's own code stays MIT. This is not a small step. Assembling and hosting that source is real work that nobody has measured, so price it before committing. If it proves too large, the custom minimal build is the option that really shrinks it.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ GPL, re-pinned to a retained build, with complete source available | — | — | https://www.gnu.org/licenses/gpl-3.0.en.html §5, §6(d); https://raw.githubusercontent.com/BtbN/FFmpeg-Builds/master/README.md; `tools/fetch_ffmpeg_windows.ps1` |
| ⚠️ Custom minimal build: FFmpeg, x264, x265, the GPU encoder headers and only what av-kit uses | The only option here that really shrinks the source set. Smaller installer. Keeps `libx265` and `libx264`, so Convert's code does not change. | av-kit takes on a build recipe, a toolchain and security updates. What the app needs from FFmpeg beyond Convert's encoders is unaudited. Every encoder path needs retesting. Cost not estimated; needs its own MEU. | `adapter.py:40`, `adapter.py:521-534` |
| ⚠️ LGPL build, Convert's software encoders changed | Removes GPL from the installer. Software H.264 and H.265 remain through `libopenh264` and `libkvazaar`. | The source set barely shrinks: 94 build scripts and 92 repositories against 106 and 104, and that source must still be provided. Needs a Convert MEU and new encoder tests: `adapter.py:521-534` falls back only to `libx265` then `libx264`, and `adapter.py:589` hard-codes `libx265`, so a re-encode cut fails on any LGPL build even with a GPU. Quality and speed of the replacement encoders are unmeasured. | https://ffmpeg.org/legal.html, `C:/Temp/av-kit/rc1/d101-exact.txt` |
| ⚠️ Do not bundle FFmpeg; download or locate it on first use | av-kit distributes no FFmpeg, so no source obligation. Smaller installer. | Changes 07 `:159` ("bundle ... in resources/ffmpeg", "Do not leave 'bundle OR PATH' as an open product decision"). New first-run step and failure mode; the README's "FFmpeg comes inside the installer" goes. | `docs/build-plan/07-distribution.md:157-171` |
| ❌ Ship as is | No work. | `NOTICES` points to tag `n8.1.2`, but the binary is `n8.1.2-44-g7c533d0f86`, so the source named is not the exact source, and it offers none for the enabled dependencies. That does not meet GPLv3 §6. BtbN has pruned the tag, so the pinned archive's URL is dead too. | https://www.gnu.org/licenses/gpl-3.0.en.html §6, `FFMPEG-PIN-URL-404` |

**Precedent:** D-87 (Session 32) chose to bundle a GPL BtbN build for the software fallback and disclose it. `FFMPEG-GPL-BUILD` left the posture open for this moment.

**Research:** GPLv3 §6 is the controlling text for a GPL build. FFmpeg's legal page is a checklist for LGPL library linking, so it guides the LGPL row rather than the recommendation.

- **What "complete" means:** FFmpeg at the exact commit, every enabled static dependency at its pinned commit, and BtbN's recipe at the tag with its patches and toolchain.
- **How much:** a static read of the candidate tag's scripts, never run, gives 106 enabled scripts and 104 distinct repositories on 10 hosts for GPL, 2 of them Subversion, and 94 scripts and 92 repositories for LGPL. Twelve scripts are GPL-only: avisynth, davs2, libdvdcss, libdvdread, libdvdnav, frei0r, rubberband, vidstab, x264, x265, xavs2 and xvid. Three scripts have conditions the scan could not parse (`50-schannel.sh`, `50-vaapi/50-libva.sh`, `55-rustdedup.sh`), so the counts could move slightly. The archive's size is unmeasured.
- **How to provide it:** §6(d) allows source on another server with clear directions, but the distributor must keep it available "for as long as needed". That leaves three routes: attach an archive to the release (GitHub's per-asset limit applies), host a mirror, or verify and maintain the external locations.
- **av-kit's own licence:** av-kit runs FFmpeg as a separate process (`adapter.py:277`) and does not link it, which fits GPLv3 §5's aggregate language. That is a conclusion from the architecture, not a ruling.
- **Retention:** BtbN's README at the tag says "The last build of each month is kept for two years." and "The last 14 daily builds are kept."

This brief covers copyright licences, not codec patents, and it is not legal advice.

**Reversibility / risk:** One-way for each release: an installer cannot be unshipped. If the choice is wrong, the exposure is a licence violation on a public download. The repository is public, but no installer has been distributed and FFmpeg's binaries aren't tracked, so the choice is still free.

**If you do not answer:** No installer is uploaded. The checklist holds at step 0.
