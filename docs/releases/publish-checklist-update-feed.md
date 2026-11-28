# Publish checklist: the update feed

This is a standing addition to every release's publish steps, starting with the first release
that ships the in-app updater (MEU-173 and MEU-174). Use it with that release's own checklist.
For those releases it replaces line 91 of `publish-checklist-v0.1.0-rc.2.md`, which kept
`latest.yml` and the `.blockmap` back from the upload. The rc.1 and rc.2 checklists are history
and stay as they are.

An installed av-kit reads the feed from this repository's releases. It reads the release that
GitHub marks **Latest**, and it moves to that release. Uploading the feed files is what makes a
release an update, so every step below is deliberate.

## 1. What the build writes

`npm run dist` runs `electron-builder --win nsis --x64 --publish never`. The build never uploads
anything. Next to the installer in `ui/dist/` it writes:

- `av-kit-Setup-<v>.exe`, the installer;
- `latest.yml`, the feed file, which names the installer, its SHA-512 and its size;
- `av-kit-Setup-<v>.exe.blockmap`, which lets the next update download only the parts that changed.

`ui/dist/win-unpacked/resources/app-update.yml` names the feed: provider `github`, owner
`matbanik`, repo `av-kit`.

## 2. Check the feed files before the upload

Run the feed check on the build output. It reads files only, with no network and no upload. It
must end `check-update-feed: feed-ok exit=0`:

```powershell
uv run python tools/check_update_feed.py --dist ui/dist --version <v> --out C:/Temp/av-kit/feed-check-<v>.json
```

Any other last line stops the release. Its reason names the file that is wrong: `feed-missing`,
`installer-missing`, `installer-ambiguous`, `version-mismatch`, `name-mismatch`,
`sha512-mismatch`, `size-mismatch`, `blockmap-missing` or `app-config-mismatch`. Rebuild; do not
edit `latest.yml` by hand.

## 3. The upload (Mat's step)

Uploading is Mat's step. An agent never runs it, and never tags, pushes or publishes a release.
Upload all three feed assets to the release, next to the files that release's own checklist names:

```powershell
gh release upload v<v> ui/dist/av-kit-Setup-<v>.exe ui/dist/latest.yml ui/dist/av-kit-Setup-<v>.exe.blockmap --repo matbanik/av-kit   # Mat's step
```

Leave the earlier release's blockmap uploaded on that earlier release. The next update compares
against it.

## 4. Latest and pre-release

- A release that is flagged **pre-release** on GitHub is never offered to installed apps.
- The release marked **Latest** is the one that every installed app moves to. Mark a release
  Latest only when every installed app should get it.
- Publish with `--latest` and without `--prerelease` (Mat's step), as the release-body rule says.

## 5. The probe after publishing (Mat's step)

This read-only probe shows the feed file that installed apps will read. It must name the version
that was just published:

```powershell
curl -sL https://github.com/matbanik/av-kit/releases/latest/download/latest.yml   # Mat's step
```

## 6. What the release notes must say

- **Trust (D-1543).** An update is trusted because its SHA-512 matches the feed file, which is
  fetched over HTTPS from this repository's releases. The installer has no publisher signature.
  Anyone who can edit the release assets can change both the installer and the feed file.
- **The request to GitHub (D-1544).** The app now contacts `github.com` by itself to check for
  updates, on the schedule set in Settings → Updates (once a week by default, or once a month).
  **Never** turns it off.
- **The one-time manual install.** A user on rc.5 or older installs this release once by hand
  from the release page. From then on, the app updates itself. During that install, rc.5's own
  uninstaller removes the Start at sign-in entry, so a user who used Start at sign-in turns it on
  again in Settings → Startup.
