---
project: "2026-11-21-release-rc4"
source: "docs/execution/plans/2026-11-09-rc3-fixes/task.md (rows 39 to 43, the rc.3 release steps)"
status: "in_progress"
---

# Task — release 0.1.0-rc.4

> **Authorization:** Mat, 2026-11-21, "create new release executable and post it on github". This
> covers the version bump commit, pushing `main`, the signed tag and its push, and the GitHub
> prerelease. The steps follow the rc.3 release (rows 39 to 43 of the rc.3 task log).
> **Receipts:** `C:/Temp/av-kit/rc4/`, and the VM receipts in `C:/Temp/zorivest/`.
> **Build script:** `build-rc4.ps1` in this folder. It sits outside build_inputs, so its SHA-256 is
> recorded here: `982ab4974a20a71baa6c09355f0bf260b7a9abfbfc0c89b1715fd28f49a076c1`
> (`build-script-sha.txt`).

| # | Task | Validation | Status |
|---|---|---|---|
| 1 | Bump every version surface to 0.1.0-rc.4 on `main` (npm `0.1.0-rc.4`, Python `0.1.0rc4`); commit `99a9c8e` and push | `bump.txt`: 15 files; `main-bump-check.txt`: `uv lock --check` ok, 40 passed, OpenAPI `--check` exit 0 | `[x]` |
| 2 | Clone detached at `99a9c8e` in `C:/Temp/av-kit/rc4-src`; offline setup | `setup.txt`, `setup2.txt` (`uv sync --frozen --all-packages`; the first sync without `--all-packages` installed 22 packages only) | `[x]` |
| 3 | Round 1 build with a straight copy of `build-rc3.ps1` | `r1-build-record.json`: 340,780,319 B, SHA-256 `819713d2…`. The installer held no Deno: `build-rc3.ps1` predates MEU-141, which added `resources/deno`, and electron-builder does not fail on a missing extraResources source. `r1-vm-check.txt` caught it. Not released; its receipts are kept as `r1-*` | `[x]` |
| 4 | `build-rc4.ps1`: copy the pinned Deno archive and licence from the cache, run `tools/fetch_deno_windows.ps1 -ExtractOnly` (both hashes checked), and after electron-builder refuse (exit 24) when any extraResources target is missing from `win-unpacked` | the script SHA-256 above | `[x]` |
| 5 | Round 2 build with `build-rc4.ps1` in the clone; smoke, version info, asar, Deno; build identity against `99a9c8e` | `build.txt` exit 0, both FETCH PASS lines, `resources check: every extraResources target is present`; `build-record.json`: 371,756,139 B, SHA-256 `4d8879cb096b1fcf0eebd8025276811285ecc4c65dedfb705349ff6472ea79e2`, build_inputs `171f5f30…`; `smoke-unpacked.txt` PASS at `0.1.0rc4`; `identity-99a9c8e.txt` matches; `versioninfo.txt` focalia.ai, 0.1.0-rc.4; `asar-check.txt` 6 True (quick start, 14 WebP images, version, author); `clone-version-tests.txt` 40 passed; `deno-version.txt` deno 2.9.8, packaged SHA equals the pin | `[x]` |
| 6 | VM revert to `clean-zorivest`, deploy, guest hash; silent install with presence checks (Deno included and run), Apps entry, silent uninstall | `C:/Temp/zorivest/avkit-rc4-revert.txt`, `avkit-rc4-deploy.txt`, `avkit-rc4-guesthash.txt` (`4d8879cb…`), `avkit-rc4-installcheck.txt`, `vm-check.txt`: install exit 0; app, backend, FFmpeg, Deno and its licence, licence list present; deno 2.9.8 runs; Apps entry `av-kit 0.1.0-rc.4`, publisher focalia.ai; uninstall exit 0 leaves no app, entry or updater copy | `[x]` |
| 7 | AC-106.5's `openapi-delta.py` refused the bump (`info.version` changed); it now sets the base's `info.version` before the compare, and its selftest has a version-bump-only case | `delta-selftest.txt` 9 cases, 0 wrong; `delta-check.txt` pass; `delta-tests.txt` 21 passed | `[x]` |
| 8 | Suites on `99a9c8e` | `rel-ui.txt` 1,657 passed; `rel-mcp.txt` 2 timeouts under the overlapping Python run, `rel-mcp-rerun.txt` 553 passed; `rel-py.txt` 47 failed: 45 closeout tooling tests that need `PYTHONUTF8=1` on Windows (`rel-py-rerun.txt` 102 passed with it, `rel-py-rerun-noutf8.txt` 45 failed without it), one timing flake that passed on rerun, and AC-106.5 (row 7); `rel-py2.txt` (`PYTHONUTF8=1`, row 7 in place): 3,339 passed | `[x]` |
| 9 | Release notes `docs/releases/v0.1.0-rc.4.md` and build record `v0.1.0-rc.4-build-record.json`; docs commit; build identity on the docs commit; signed tag `v0.1.0-rc.4`; `gh release create` prerelease with the installer, `THIRD_PARTY_LICENSES.txt` and the rc.1 FFmpeg source archive | the docs commit holds this log with this row open; the tag, identity and release results are in Mat's report and `C:/Temp/av-kit/rc4/` (`identity-head.txt`, `tag-verify.txt`, `gh-release-view.txt`) | `[ ]` |
