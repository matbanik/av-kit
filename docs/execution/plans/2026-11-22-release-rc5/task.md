---
project: "2026-11-22-release-rc5"
source: "docs/execution/plans/2026-11-21-release-rc4/task.md (the rc.4 release steps)"
status: "in_progress"
---

# Task — release 0.1.0-rc.5

> **Authorization:** Mat, 2026-11-22, "create new release candidate executable", "Cut it so it is
> TLDR only few lines for av-kit 0.1.0-rc.5" and "make it so the release also shows up on
> https://github.com/matbanik/av-kit page". This covers the version bump commit, pushing `main`,
> the signed tag and its push, and the GitHub release. The release is published as the latest
> full release, not a prerelease, so GitHub's repository page lists it; its body is a short TLDR
> that links to the full notes in this repository.
> **Receipts:** `C:/Temp/av-kit/rc5/`, and the VM receipts in `C:/Temp/zorivest/`.
> **Build script:** `build-rc5.ps1` in this folder, a copy of `build-rc4.ps1` with the rc.5
> installer name, record path and header. It sits outside build_inputs, so its SHA-256 is recorded
> here: `9a1c4aee63d9578bc96aeaae3fa2e714cec3195258d07b277e3c2227802a871e` (`build-script-sha.txt`).

| # | Task | Validation | Status |
|---|---|---|---|
| 1 | Bump every version surface to 0.1.0-rc.5 on `main` (npm `0.1.0-rc.5`, Python `0.1.0rc5`); commit `a5e4667` and push | `bump.txt`: 15 files, 21 replacements; `bump-checks.txt`: `uv lock --check` ok, OpenAPI `--check` exit 0; `bump-tests.txt` 40 passed. The bump script also pointed the README's download links at `/releases/latest`; AC-110.2 (`test_readme_links_reach_prereleases`) refused it, because GitHub's `/releases/latest` skips prereleases, so that README edit was reverted before the commit | `[x]` |
| 2 | Clone detached at `a5e4667` in `C:/Temp/av-kit/rc5-src`; offline setup | `setup.txt`: lock, sync, both `npm ci` exit 0; version tests 39 passed and AC-25.10 failed for want of the extracted FFmpeg, as in rc.4's `setup2.txt` (row 3 reruns it after the build); OpenAPI `--check` exit 0 | `[x]` |
| 3 | Build with `build-rc5.ps1` in the clone; smoke, version info, asar, Deno; build identity against `a5e4667` | `build.txt` exit 0, both FETCH PASS lines, `resources check: every extraResources target is present`; `build-record.json`: 371,754,272 B, SHA-256 `4a61e2cf4b7af41221eca3689421435f4110a3c601448f5433ecb64dfaadf5ed`, build_inputs `fd90350c…`; `smoke-unpacked.txt` PASS at `0.1.0rc5`; `identity-a5e4667.txt` matches; `versioninfo.txt` focalia.ai, 0.1.0-rc.5; `asar-check.txt` 6 True; `clone-version-tests.txt` 40 passed; `deno-version.txt` deno 2.9.8, packaged SHA equals the pin | `[x]` |
| 4 | VM revert to `clean-zorivest`, deploy, guest hash; silent install with presence checks (Deno included and run), Apps entry, silent uninstall | `vm-check.txt`, `C:/Temp/zorivest/avkit-rc5-*.txt`: guest SHA-256 `4a61e2cf…`; install exit 0; app, backend, FFmpeg, Deno and its licence, licence list present; deno 2.9.8 runs; Apps entry `av-kit 0.1.0-rc.5`, publisher focalia.ai; uninstall exit 0 leaves no app, entry or updater copy | `[x]` |
| 5 | Suites on `a5e4667` (`PYTHONUTF8=1` for pytest) | `rel-py.txt` 3,348 passed; `rel-ui.txt` 1,674 passed; `rel-mcp.txt` 554 passed | `[x]` |
| 6 | Release notes `docs/releases/v0.1.0-rc.5.md` and build record `v0.1.0-rc.5-build-record.json`; docs commit; build identity on the docs commit; signed tag `v0.1.0-rc.5`; `gh release create --latest` (not a prerelease) with the TLDR body `C:/Temp/av-kit/rc5/gh-body.md`, the installer, `THIRD_PARTY_LICENSES.txt` and the rc.1 FFmpeg source archive | the docs commit holds this log with this row open; the tag, identity and release results are in Mat's report and `C:/Temp/av-kit/rc5/` (`identity-head.txt`, `tag-verify.txt`, `gh-release-view.txt`) | `[ ]` |
