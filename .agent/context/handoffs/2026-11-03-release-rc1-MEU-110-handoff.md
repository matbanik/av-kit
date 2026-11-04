---
date: "2026-11-04"
project: "release-rc1"
meu: "MEU-110"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md"
build_plan_section: "bp07"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-03-release-rc1-MEU-110-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-110, `dist-release-candidate`. MIT licence, a generated complete licence list, one RC version on every surface, a real NSIS installer with packaged checks, release notes, a publish checklist, the FFmpeg re-pin Mat ruled on in D-101 and its complete corresponding source archive. It stops before every outward step.
**Build Plan Section**: [07 §Release candidate packaging (residual)](../../../docs/build-plan/07-distribution.md#release-candidate-packaging-residual).
**Predecessor**: none. The [MEU-108 handoff](2026-11-03-release-rc1-MEU-108-handoff.md), the [MEU-109 handoff](2026-11-03-release-rc1-MEU-109-handoff.md), the [MEU-111 handoff](2026-11-03-release-rc1-MEU-111-handoff.md) and the [MEU-112 handoff](2026-11-03-release-rc1-MEU-112-handoff.md) are the same plan's other MEUs.

- **Metadata (rows 6, 7).** `ui/package.json` gains description, licence, author, homepage and repository; `mcp-server/package.json` and the four `pyproject.toml` gain the licence. `ui/electron-builder.yml` ships `LICENSE` and the generated list, filters `*.zip` from the FFmpeg entry and names the installer without spaces.
- **`LICENCE_LIST` (row 8).** `tools/generate_third_party_licenses.py` reads what shipped: `COLLECT-00.toc`, `PYZ-00.toc`, `RECORD`, the npm lock's non-dev closure and the .NET runtime packs. It refuses an unowned file, a missing notice, an unexpected GPL-class licence or a stale build. CPython's native libraries come from reviewed texts in `packaging/licence-overrides/`.
- **`VERSION_ONE` (row 9).** `0.1.0-rc.1` and `0.1.0rc1`, with a drift test.
- **The re-pin and the source archive (rows 9d to 9f).** Mat ruled on D-101: keep the GPL build, re-pin to BtbN `autobuild-2026-10-31-12-59`, and publish only once its complete corresponding source is available. `tools/assemble_ffmpeg_source.py` collects FFmpeg at commit `8dca1586f468bfcbb78ae3ed618af1361d9f140a`, every dependency BtbN's recipe at `5031c6f1082414e53688d39e521849905071070d` enables, and the toolchain sources, into one archive it reads back against its manifest. `av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz` is 992,681,460 B, SHA-256 `953a62373693e388a853ee2c6dbfadf4ce12e7f4aeb13b86e26f179b48d07284`, 46.2% of GitHub's 2 GiB asset limit: 739 sources, 3,213,917,779 B before compression, and 0 matches of the old address.
- **`BUILD_RECORD` (row 10).** `build-rc.ps1` builds from clean, and `build-identity.py` hashes every tracked input outside a short exclude list. The installer is 340,348,020 B, SHA-256 `beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7`. **It is unsigned, and it holds a GPL FFmpeg build, so it goes out only with the source archive beside it (D-101).**
- **Packaged checks (rows 11, 12).** Layout, module bans with a negative control, the frozen backend, a real first conversion into a missing folder, the MCP entry, offline TTS, then a real install, launch and uninstall on this PC.
- **Release materials (row 13).** `docs/releases/v0.1.0-rc.1.md`, `publish-checklist-v0.1.0-rc.1.md` and the build record.

### Additive deviations from the plan's letter

- Every file under `*.dist-info/licenses/` counts as a notice, whatever its name, because numpy's `dragon4_LICENSE.txt` matches no name pattern.
- A namespace package's TOC source is literally `-`, not the `.` the plan says, and the generator prefers a shipped sibling to attribute it. The real PYZ has no `__main__` entry.
- `cpython-incorporated.txt` was added: `base_prefix/LICENSE.txt` lacks CPython's "Incorporated Software" section.
- Override versions are checked against the live runtime where it can be read. `ssl.OPENSSL_VERSION_INFO` misreports 3.5.4 as 3.5.0, so the check reads `ssl.OPENSSL_VERSION`; `test_openssl_version_is_the_real_one` was added after the Red receipt, with its own Red (`row8-openssl-red.txt`), when the rehearsal refused.
- libffi's Windows provenance is `cpython-source-deps` at `16fad4855b3d8c03b5910e405ff3a04395b39a98`, 3.4.2. The HACL\* text is the MIT header of CPython's vendored source, not that project's Apache-2.0 top-level file. libb2 is CC0 and needs no override.
- `type-fest` 2.19.0 is the one npm package with no licence file. The override elects its CC0-1.0 option, which also keeps a third party's gmail address out of a tracked file.
- Notices decode as UTF-8 with a latin-1 fallback. `Distribution.files` drops paths missing on disk, so `RECORD` is read directly. `write_list` deletes any old output first, because electron-builder only warns on a missing source.
- Row 9's lock refresh added six dev, optional or bundled entries under `@tailwindcss/oxide-wasm32-wasi` and the root `license: MIT` to `ui/package-lock.json` (772 to 778 entries). Nothing ships from them and `npm ci --dry-run` passes. `build-rc.ps1` uses `uv run --frozen`, clears `AVKIT_FFMPEG_URL` and `AVKIT_FFMPEG_SHA256` and passes `--publish never`.
- `latest.yml`, `.blockmap`, `builder-debug.yml` and `resources/app-update.yml` are electron-builder by-products. The app has no updater and none of them does anything.
- The smoke's first conversion runs the default encoder path because of `CONVERT-JOB-GPU-PREFERENCE-IGNORED`, which the smoke itself found (D-191). Mat overruled D-191 and MEU-112 fixed it, so the smoke now also runs a second job set to Software. Real results on this PC: `hevc_nvenc` for the default and `libx265` for Software. A machine without NVENC is a question for Mat's check from the published release.
- `BACKEND-READY-BEFORE-LISTEN` is left out of the release notes because its user effect isn't measured; the checklist says so.
- Release notes carried two markers, `[FILL-CLEAN-MACHINE: …]` and `[FILL-D101: …]`, until Mat's rulings filled them. The checklist still refuses to publish past any `[FILL-`. The old FFmpeg pin's zip stays beside the new one in the cache, because its URL 404s and this PC's cache is the only copy.

### What these checks don't prove

- The round trip ran on this PC, not a clean machine. A real F2 picker capture and first model provisioning into an empty cache are the checklist's clean-machine step. Mat waived them for now and will run them from the published release (D-204), and the release notes say the build hasn't run on a clean machine.
- The source archive is checked against BtbN's recipe and the binary's own configuration line, but nobody has built an FFmpeg from it. Its README names what it can't pin: crosstool-NG at image time; Rust, cargo-c, Meson and Ubuntu 26.04 as general-purpose tools (GPLv3 §1); rav1e's `cc`; Meson wraps and CMake download steps, including dav1d's `checkasm`. The tool counted 88 files that can fetch more while building.
- The D-101 brief covers copyright licences, not codec patents, and it isn't legal advice. libdvdcss is compiled into the pinned binary (`--enable-libdvdread`, `--enable-libdvdnav`; source `deps/libdvdcss-811ce97a1d4d` in the archive). av-kit doesn't use it. The brief names it only among the GPL-only scripts, so the question of DVD copy-protection code goes to Mat at completion.
- Row 12's process check is bounded, not a full wait: the loop leaves as soon as the count reaches 0, within its 30 s limit, and the printed text overstates the wait.
- The installed app's reach to the backend is proved by Settings' own 200 (`mcp-token.txt` in the throwaway data wasn't opened).
- A Desktop and a Start Menu shortcut existed briefly on Mat's real profile during each round trip; both were gone after uninstall.

### Rerun because of ECN-3

Rows 10 to 12 ran twice. `plan.ts` is hashed into `build_inputs`, so the MEU-111 correction made `--verify-record` report a mismatch and S8 applied. The first run's receipts are in `C:/Temp/av-kit/rc1/attempt-1/`. The installer moved from 328,402,897 B `3200bf4a…` to 328,403,592 B `532663ea…`, while the licence list stayed byte-identical (SHA-256 `afb638f2…`). Row 13's size, hash and record copy follow the rebuilt installer.

### Rerun because of Mat's rulings (ECN-6)

This was the third build. Rows 10 to 13 ran again after rows 9a to 9f. The new FFmpeg pin, the source tool and MEU-112's product code are all build inputs, so S8 applied. The installer moved from 328,403,592 B `532663ea…` to 340,346,916 B `67e6614e…`, and `build_inputs` from `617f92d1…` to `8f277206…`. The licence list stayed byte-identical (SHA-256 `afb638f2…`).

### Reruns and checklist change because of the review's findings and Mat's report (ECN-8, ECN-9, ECN-10)

Round 2's F1 fix edits `ui/src/`, so S8 applied again and rows 10 to 13 made the fourth build. The installer moved from 340,346,916 B `67e6614e…` to 340,347,815 B `2ac7ae81…`, and `build_inputs` from `8f277206…` to `aebaeb1f…`. H1-2 attempt 4 failed on that build, and the crash fix in rows 9j and 9k also edits `ui/src/`, so S8 applied once more. The fifth build is 340,347,542 B `aabc4ae1…`, with `build_inputs` `19e2e519…`. The fix for round 3's F1 (ECN-10) edits `ui/src/` too, so rows 10 to 13 ran again and made the sixth build, 340,348,020 B `beabc509…`, with `build_inputs` `08ade695…`. The licence list, the FFmpeg binaries and the source archive didn't change in any of the three.

Round 2's F2 found that checklist step 7 let the development audit take the Transcript warning out of the notes, although that audit runs the local MCP build and uv's Python, not the published app. Row 9i rewrites the step. The deciding check now runs in the app installed from the published asset (Transcript page, Compile, View compiled, read for real words), and only that result removes the section. The audit stays as supplementary evidence that tells YouTube's block from a fault. A blocked run or no run leaves the warning in place. The check for this is a text check on the document: its Red is only that check returning all False before the edit, and all True after. Nobody has run the new step, because it needs the published release (D-204). The Transcript page doesn't display an item's stored error, so the step doesn't tell Mat to look for the message on the card.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md) §MEU-110. **Execution authorization:** `USER_EXPLICIT`, 2026-11-03, "create MIT license file / prepare whatever we need to build and publish the release rc1 candidate", and 2026-11-04, "approve tripple of the token budget and add MEU-111". Plan review approved at round 3. Mat's rulings of 2026-11-04 (ECN-6): "1: recommendation accepted", "3. wave for now, I will do it once we are public directly from github, will just need reminder", "4. yes accepted, as long as it is standard convention in ohter projects", "5. single commit".

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-110.1 | unit | `LICENSE` is MIT, is installed as `resources/LICENSE`, and every package manifest declares MIT. | Human-approved (Mat 2026-11-03) | `tests/unit/test_release_packaging.py:55-88`; row 11 layout | ✅ |
| AC-110.2 | unit | The README states MIT, links `LICENSE`, says bundled components keep their own licences, and its download links reach prereleases. | Human-approved; Research-backed (GitHub REST docs: latest excludes prereleases) | `tests/unit/test_release_packaging.py:99`, `:107` | ✅ |
| AC-110.3 | unit + runtime | `electron-builder.yml` filters `*.zip` from the FFmpeg entry, and no zip lands in `resources/ffmpeg` when one sits in the source folder. | Local Canon (`INSTALLER-SHIPS-FFMPEG-ZIP`) | `tests/unit/test_release_packaging.py:118`; row 11 (`ffmpeg_zips []`, `ffmpeg_source_zip_present true`) | ✅ |
| AC-110.4 | unit | The installer's filename has no spaces, so GitHub keeps it as built. | Research-backed (GitHub REST docs: asset renaming) | `tests/unit/test_release_packaging.py:126`, `:135` | ✅ |
| AC-110.5 | unit | The generator lists every distribution that owns a file in a fixture `COLLECT-00.toc` or a module in a fixture `PYZ-00.toc`, with version, licence and the full text of every licence or notice file in its `RECORD`. A distribution reached only through the PYZ is listed. | Local Canon (`NOTICES-SPACY-TRANSITIVE`: "Generate the list from the built bundle's environment") | `tests/unit/test_generate_third_party_licenses.py:220`, `:229`, `:239`, `:258`, `:609` | ✅ |
| AC-110.6 | unit | The generator exits non-zero for a distribution with no licence or notice file, and for one whose `RECORD` lists a notice missing on disk. | Spec (07 §Release candidate) | `tests/unit/test_generate_third_party_licenses.py:275`, `:285`, `:569-596`, `:625-642` | ✅ |
| AC-110.7 | unit | The generator exits non-zero for a GPL-class component not on the allow list, and passes for an allow-listed one. | Spec; Local Canon (`03-service-layer.md:453`: espeak-ng never ships) | `tests/unit/test_generate_third_party_licenses.py:301`, `:308`, `:316`, `:326` | ✅ |
| AC-110.8 | unit + runtime | `resources/THIRD_PARTY_LICENSES.txt` is shipped and generated from the real build, after AC-110.18's stale-build guard passes. | Spec | `tests/unit/test_release_packaging.py:143`, `:150`; `tests/unit/test_generate_third_party_licenses.py:673`, `:685`; rows 10, 11 | ✅ |
| AC-110.9 | unit | Every release surface carries the one RC version; a test fails on drift. OpenAPI matches. | Spec | `tests/unit/test_release_packaging.py:156-210`; gate `openapi` | ✅ |
| AC-110.10 | runtime | A real NSIS installer is built from today's tree, after clearing the stale `ui/dist`, `packaging/build` and `packaging/dist`, with fresh backend, picker, MCP bundle and FFmpeg-with-licence; size and SHA-256 are recorded; size is under 500 MB. | Local Canon 07 `:350` | row 10 (`build-rc.ps1`, `build-record.json`) | ✅ |
| AC-110.11 | runtime | Packaged layout: `resources/` holds `LICENSE`, both notices, `ffmpeg/{ffmpeg,ffprobe}.exe` and `ffmpeg/LICENSE.txt` with no zip, the backend, the picker with its `.deps.json` and runtime files, and `mcp-server/{index.mjs,LICENSES.txt}`; the install root holds `LICENSE.electron.txt` and `LICENSES.chromium.html`. `torch`, `torchvision`, `torchaudio`, `kokoro`, `phonemizer` and `espeakng_loader` are absent from `_internal` and from the module archive inside the shipped `avkit-backend.exe`, and `misaki.espeak` is absent from that archive. The same check reports `phonemizer` on the 2026-08-24 negative-control exe. The packaged picker, run with no arguments, loads .NET and WinForms and exits `PICKER_EXIT_ERROR` (1) with `--out <path> is required`. | Local Canon 07; `tools/smoke_packaged_tts.py`; `native/region-picker/Program.cs:24,69-78` | row 11 (`tools/smoke_packaged_rc.py`), repeated on the install root in row 12 | ✅ |
| AC-110.12 | runtime | The frozen backend starts on a throwaway app-data folder, reports the RC version and the bundled FFmpeg, and completes a real first conversion into a folder that does not exist. | Spec; MEU-109 end to end | rows 11, 12 | ✅ |
| AC-110.13 | runtime | The MCP entry starts through `av-kit.exe` with `ELECTRON_RUN_AS_NODE` and reports the RC version. | Local Canon AC-92.4 | row 11 (`packaged-probes.ps1`) | ✅ |
| AC-110.14 | runtime | Packaged TTS runs offline from cached models. | Local Canon MEU-72 `PACKAGE_SMOKE` | row 11 (`smoke_packaged_tts.py offline`) | ✅ |
| AC-110.15 | runtime | The installed app from a silent NSIS install launches, reaches the backend and renders a page. The uninstaller leaves no Uninstall key, `Run` or `StartupApproved\Run` value, shortcut or install folder behind, and `%LOCALAPPDATA%/av-kit` keeps the same top-level entries. | Local Canon 07 `:310`, `:372`, §Login item uninstall `:186` | row 12 (`install-roundtrip.ps1`, `packaged-app-smoke.mjs`) | ✅ |
| AC-110.16 | static | Release notes state what the RC is, what it does not fix and how to report problems. Both the release notes and the publish checklist disclose `YOUTUBE-CAPTIONS-IP-BLOCK`, that the Transcript path isn't verified end to end while it holds, and Mat's acceptance or the recheck condition. The publish checklist gives the outward steps in order with exact commands, including `--verify-record` before the tag, a clean-machine step with a real F2 picker capture and first model provisioning into an empty cache, the Transcript recheck or acceptance before publishing, and removing the README's "No installer yet" note after publishing. D-101 is presented as a Decision Brief. | Human-approved (Mat 2026-11-03); Local Canon `YOUTUBE-CAPTIONS-IP-BLOCK` | row 13 (`release materials present: True`); row 9i (`s44-110-step7.txt`, checklist step 7 after round 2's F2); `docs/releases/` | ✅ |
| AC-110.17 | unit + runtime | `resources/THIRD_PARTY_LICENSES.txt` from the real build contains the complete text of onnxruntime's `ThirdPartyNotices.txt` and of numpy's vendored licences. A fixture proves a notice outside dist-info and outside the TOC is included. | Spec (07 §Release candidate) | `tests/unit/test_generate_third_party_licenses.py:338`; row 11 (`notice_chars`) | ✅ |
| AC-110.18 | unit | Every file and module in the build is owned by a distribution or falls in a named class (first party, CPython, CPython native library with a reviewed text, Windows runtime, source-less namespace package); anything else exits non-zero. The generator also exits non-zero when the TOCs disagree with `_internal` or with the exe's module archive. | Spec (07 §Release candidate) | `tests/unit/test_generate_third_party_licenses.py:356-549`, `:657-663`; row 10 | ✅ |
| AC-110.19 | unit + runtime | `build-identity.py --selftest` proves a PyInstaller spec, a Vite config, an MCP bundling script, `global.json` and `build-rc.ps1` each change the identity while docs, tests and `.agent` do not. The build writes a record with the identity, installer hash, FFmpeg hashes and toolchain versions. `--verify-record` passes on the result and fails on a changed product file or installer. | Spec (07 §Release candidate) | gate `build-identity-selftest`, `build-record`; row 10 | ✅ |
| AC-110.20 | unit + runtime | `tools/assemble_ffmpeg_source.py` collects, for the pinned build, FFmpeg at the exact commit, every dependency BtbN's recipe enables for win64, GPL, 8.1 at its pinned commit, the recipe at the tag and the toolchain sources verified against the recipe's own checksums, as one archive it reads back against its manifest. A fetch step it can't read, a crate from outside the registry or an archive that disagrees with the manifest stops the run. | D-101 ruling; GPLv3 §6(d) | `tests/unit/test_assemble_ffmpeg_source.py:127-569`, `:719-730`; row 9f (`pack.txt`) | ✅ |
| AC-110.21 | unit + runtime | The pin is one fact: the source tool's constants, `tools/fetch_ffmpeg_windows.ps1`, the `## FFmpeg` notice, the README and the packaged `ffmpeg.exe -version` all name the same build. Every `--enable-*` flag in that binary's own configuration line is produced by a script in the source set, apart from a short named list of FFmpeg's own options. | D-101 ruling | `tests/unit/test_assemble_ffmpeg_source.py:592-710`; `tests/unit/test_packaging_installer.py:207`; rows 9e, 9f, 11 | ✅ |
| AC-110.22 | unit + runtime | The source archive is under GitHub's 2 GiB asset limit. Its size and SHA-256 are in the release notes, and the publish checklist attaches it with the installer. | D-101 ruling; GPLv3 §6(d) | `tests/unit/test_assemble_ffmpeg_source.py:735`, `:741`; row 9f; `docs/releases/` | ✅ |
| AC-108 (cross-ref) | — | Owned by the MEU-108 handoff (the READY guard in the output handler) | plan §MEU-108 | [MEU-108 handoff](2026-11-03-release-rc1-MEU-108-handoff.md) | see MEU-108 |
| AC-109 (cross-ref) | — | Owned by the MEU-109 handoff (the output folder before FFmpeg starts) | plan §MEU-109 | [MEU-109 handoff](2026-11-03-release-rc1-MEU-109-handoff.md) | see MEU-109 |
| AC-111 (cross-ref) | — | Owned by the MEU-111 handoff (the MCP image cap and the audit's two image steps) | plan §MEU-111 | [MEU-111 handoff](2026-11-03-release-rc1-MEU-111-handoff.md) | see MEU-111 |
| AC-112 (cross-ref) | — | Owned by the MEU-112 handoff (the encoder chosen for one job) | plan §MEU-112 | [MEU-112 handoff](2026-11-03-release-rc1-MEU-112-handoff.md) | see MEU-112 |
| AC-24 (cross-ref) | regression | AC-24.10: the packaged backend folder holds its exe and support tree. It passed at row 0, not failed as the plan predicted, because this tree holds the gitignored outputs; it fails only in a clean clone, and CI deselects it (plan ECN-2) | plan ECN-2 | `tests/unit/test_packaging_backend.py:212` (gate `py-tests`) | ✅ |
| AC-25 (cross-ref) | regression | AC-25.7: the MCP snippet names the app-data folder, with no token or API base, fixed in `0eb59ab` before this baseline. AC-25.10: the NSIS check script exists and fails closed; same clean-clone note as AC-24.10 | plan ECN-2 | `tests/unit/test_packaging_installer.py:64`, `:94` (gate `py-tests`) | ✅ |
| AC-68 (cross-ref) | regression | AC-68.2: the audit runner imports nothing from the server's tree. H1-2 attempt 1 failed this test on row 5b's import; the [MEU-111 handoff](2026-11-03-release-rc1-MEU-111-handoff.md) holds the correction (D-189, ECN-3). The forbidden-pattern list is unchanged | plan ECN-3 | `mcp-server/tests/audit/run-cli.test.ts` (gate `mcp-tests`) | ✅ |
| AC-71 (cross-ref) | regression | AC-71.10: Electron with `ELECTRON_RUN_AS_NODE` on the dev server entry answers `initialize` as av-kit, and the fuse pin holds in `electron-builder.yml`, which row 7 edited | plan §Verification 1 | `ui/tests/unit/mcp-spawn-electron.test.ts:76` (gate `ui-tests`) | ✅ |
| AC-72 (cross-ref) | regression | AC-72.7: `THIRD_PARTY_NOTICES.md` stays hand-curated with its LGPL appendix and FFmpeg source section; it gains one pointer line to the generated list, and its `## FFmpeg` section names the re-pinned build | plan §MEU-110 | `tests/unit/test_packaging_installer.py:207` (gate `py-tests`) | ✅ |
| AC-92 (cross-ref) | regression | AC-92.4: the MCP entry runs through the app's own exe with `ELECTRON_RUN_AS_NODE`. It is the Local Canon behind AC-110.13 above | plan AC-110.13 | row 11 MCP probe (AC-110.13) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-110.1, AC-110.3, AC-110.4 and AC-110.8 metadata (nine tests) | `assert None == '${productName}-Setup-${version}.${ext}'`; `assert None == '../packaging/dist/THIRD_PARTY_LICENSES.txt'` | pass | `test_release_packaging.py:63-150` |
| AC-110.5 to AC-110.8, AC-110.17, AC-110.18 generator | 63 failed, each `ImportError: cannot import name 'generate_third_party_licenses' from 'tools'` | pass (64) | `test_generate_third_party_licenses.py` |
| AC-110.9 version | `assert '0.1.0' == '0.1.0rc1'` | pass | `test_release_packaging.py:156-210` |
| AC-110.21 and AC-72.7, the re-pin | `assert 'n8.1.3-27-g8dca1586f4' in '…'`: the notices still named the old build. `assert '# Pin: BtbN autobuild-2026-10-31-12-59 win64 gpl' in '# Fetch a pinned…'`: so did the fetch script | pass (91) | `test_packaging_installer.py:207`, `test_assemble_ffmpeg_source.py:592` |

Row 6's three passes (`9 failed, 3 passed`) are what already held before the row: `test_licence_file_is_mit`, `test_readme_states_licence` and `test_readme_links_reach_prereleases`. The nine failure headers name the file's other nine tests. Row 8's Red is a missing-module failure, not an assertion: it proves the tests ran against nothing, and only the Green run exercises each refusal on its own fixture. `test_openssl_version_is_the_real_one` has a real assertion Red of its own. AC-110.10 to AC-110.16 and AC-110.19's real build are runtime proofs with no Red.

The source tool's tests came after the tool (ECN-6), so they prove each refusal with bad inputs, and AC-110.20 and AC-110.22 have no Red run. The re-pin above does have one. The first pack (`pack-1.txt`, exit 3) stopped at the read-back: `deps/harfbuzz-75d8ac5d2313: 3979 of 3983` and `deps/SPIRV-Cross-300681bbcb83: 4865 of 4871`. `tarfile` keeps `member.pax_headers` from git's inner tar, and a pax `path` outranks the rewritten name; 10 files were affected, exactly the shortfall. The fix (`member.pax_headers = {}`) went in before its test had been seen to fail. That was proved afterwards by taking the fix out: `2 failed, 8 passed, 67 deselected`, `archive disagrees with the manifest: deps/lib: 7 of 8` (`source-tool-mutation.txt`).

Receipts: `C:/Temp/av-kit/s44-110-red-meta.txt`, `s44-110-green-meta.txt`, `s44-110-red-gen.txt`, `s44-110-green-gen.txt`, `s44-110-red-version.txt`, `s44-110-green-version.txt`, `s44-110-openapi.txt`, `s44-110-source-tool.txt`, `s44-110-repin-red.txt`, `s44-110-repin.txt`; under `C:/Temp/av-kit/rc1/`: `build.txt`, `build-record.json`, `build-record-check.txt`, `smoke-unpacked.json`, `packaged-probes.txt`, `install-roundtrip.txt`, `installed-app.json`, `smoke-installed.json`, `installed-app.png`, `licence-rehearsal.txt`, `release-materials.txt`, `rows/row9-lock-compare.txt`, `rows/row13-gitleaks.txt`, `ffmpeg-src/receipts/repin-config.txt`, `ffmpeg-src/receipts/pack-1.txt`, `ffmpeg-src/receipts/pack.txt`, `ffmpeg-src/receipts/address-scan.txt`, `source-tool-mutation.txt`, `address-convention/report.txt`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-red-meta", "command": "pwsh -NoProfile -File row-6.ps1 (task.md row 6 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-110 metadata Red: test_release_packaging.py for AC-110.1 to AC-110.4 and AC-110.8's builder entry, with red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 (baseline.sha) plus rows 1 to 6", "output": "9 failed, 3 passed. assert None == '${productName}-Setup-${version}.${ext}'. assert None == '../packaging/dist/THIRD_PARTY_LICENSES.txt'. red-check: 1 receipt(s), 0 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-green-meta", "command": "pwsh -NoProfile -File row-7.ps1 (task.md row 7 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-110 metadata Green: manifests, electron-builder.yml, README mentions and the notices pointer", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 7", "output": "25 passed in 13.25s."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-generator", "command": "pwsh -NoProfile -File row-8.ps1 (task.md row 8 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-110 generator Red then Green on fixture TOCs and dist-info folders, ruff, the overrides check and a rehearsal on the real tree", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 8", "output": "Red 63 failed, each ImportError: cannot import name 'generate_third_party_licenses' from 'tools' (the module did not exist yet). Green 64 passed in 4.49s."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-version", "command": "pwsh -NoProfile -File row-9.ps1 (task.md row 9 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-110 version Red then Green, lock refresh and OpenAPI regeneration", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9", "output": "Red 7 failed, 12 deselected: assert '0.1.0' == '0.1.0rc1'. Green 94 passed in 11.59s. openapi.committed.json changed only info.version."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-source-tool", "command": "pwsh -NoProfile -File row-9d.ps1 (task.md row 9d Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-110 source tool: the recipe parsers, each fail-closed refusal, archive completeness and line endings", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9d", "output": "77 passed in 9.66s."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-repin", "command": "pwsh -NoProfile -File row-9e.ps1 (task.md row 9e Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-110 re-pin Red then Green: the fetch script's pin, the notices and the README, with the pinned binary's configuration line checked against the recipe", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9e", "output": "Red 2 failed, 89 passed in 5.21s: assert 'n8.1.3-27-g8dca1586f4' in the notices, and assert '# Pin: BtbN autobuild-2026-10-31-12-59 win64 gpl' in the fetch script. Green 91 passed in 5.12s. ffmpeg version n8.1.3-27-g8dca1586f4-20261031. scripts 134 enabled 109. Configuration line explained; the one flag the recipe has that the binary doesn't use is --enable-openssl."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-source-set", "command": "pwsh -NoProfile -File row-9f.ps1 (task.md row 9f Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-110 source set: assemble, pack, read back against the manifest and check the pinned binary's configuration line, then a scan of the archive for the old address", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9f", "output": "av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz, 992681460 B, sha256 953a62373693e388a853ee2c6dbfadf4ce12e7f4aeb13b86e26f179b48d07284, 46.2% of the 2 GiB limit. sources 739; bytes before compression 3213917779. files that can fetch more while building: 88. Old-address scan: matches of the old address, any case: 0. The first pack stopped at the read-back with exit 3 and is described under FAIL_TO_PASS."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-build", "command": "pwsh -NoProfile -File row-10.ps1 (task.md row 10 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-110 real build after ECN-10: stale outputs cleared, the re-pinned FFmpeg extracted from the checked archive, backend, picker, MCP bundle, licence list, electron-builder, record", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9m, ECN-3, ECN-6, ECN-8, ECN-9 and ECN-10, build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573", "output": "build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573. Installer av-kit-Setup-0.1.0-rc.1.exe, 340348020 B, sha256 beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7, under 500 MB. ffmpeg c46215f8889634396f0ac0acac738ef2145175e5b6caf28b3daa8ac9a9980c5f, ffprobe b77db2dfcbf08886d6a29bc1fabdceea3dd559751b03087205e3e13ec85c3e15. build record: matches."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-smoke", "command": "pwsh -NoProfile -File row-11.ps1 (task.md row 11 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-110 packaged smoke on win-unpacked after ECN-10: layout, module bans against the negative control, picker, frozen backend, both conversions, licence list, MCP entry, offline TTS", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9m, ECN-3, ECN-6, ECN-8, ECN-9 and ECN-10, build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573", "output": "layout missing [], ffmpeg_zips [], ffmpeg_source_zip_present true. bans internal [] archive [], negative control espeakng_loader, kokoro, misaki.espeak, phonemizer. picker exit 1 \"--out <path> is required\". Backend version 0.1.0rc1, FFmpeg n8.1.3-27-g8dca1586f4-20261031 under resources/ffmpeg. Conversion into a folder that did not exist (folder_existed false): Done, hevc_nvenc, source_compress.mp4, 109239 B. Second job with gpu_preference software: Done, libx265. Licence list 1102016 B, onnxruntime/ThirdPartyNotices.txt 344418 characters. PASS MCP_ENTRY_PROBE started in 0.12 s, serverInfo av-kit 0.1.0-rc.1. wav_samples 41400, PASS: smoke_packaged_tts offline, with proxies at a dead port."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-roundtrip", "command": "pwsh -NoProfile -File row-12.ps1 (task.md row 12 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-110 NSIS round trip on this PC after ECN-10: S5 preconditions, silent install, install-root smoke, real app launch and quit, silent uninstall, before-and-after snapshot", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9m, ECN-3, ECN-6, ECN-8, ECN-9 and ECN-10, build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573", "output": "Installer matched the record, beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7. /D honoured. Install-root smoke passed, Software job libx265. App smoke isPackaged true, version 0.1.0-rc.1, backend status 200, page #/settings mentions FFmpeg, errors []. Uninstaller exit 0; its relaunched copy finished. Snapshot uninstall, run, startup_approved, desktop, start_menu, app_data, local_folders, roaming_folders each new [], lost []. S6: nothing left behind, and the app data keeps the same top-level entries."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-materials", "command": "pwsh -NoProfile -File row-13.ps1 (task.md row 13 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-110 release materials after ECN-10: the row's presence check, the record copy against the installer and the render check, plus gitleaks on docs/releases, run alongside the row", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9m, ECN-3, ECN-6, ECN-8, ECN-9 and ECN-10, build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573", "output": "release materials present: True. build record: matches docs\\releases\\v0.1.0-rc.1-build-record.json. gitleaks: no leaks found. Drift check passed (112 MEUs, 12 phases)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-110-step7", "command": "pwsh -NoProfile -File row-9i.ps1 (task.md row 9i Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "Round 2's F2: checklist step 7 decides from the installed published app, and the audit is supplementary. A text check on the document", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9i", "output": "step 7 checks: {'download': True, 'hash': True, 'app': True, 'supplementary': True, 'no_audit_verdict': True}. Before the edit, all five were False."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-gate-h1-2-attempt1", "command": "$env:TMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:TEMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-03-release-rc1/session-gate.ps1 *> C:/Temp/av-kit/s44-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s44-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE','build_inputs','mismatch','audit rule','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 attempt 1, the registered D6 gate, on the tree before the ECN-3 correction", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+ab9c5df667b9ca5ae9139129a9e0075c6b774bf96f173e13d8d9fae746342ea2", "output": "mcp-tests exit=1: 1 failed, 464 passed, tests/audit/run-cli.test.ts AC-68.2, the runner tree contains none of the forbidden imports, hit mcp-server/scripts/audit/plan.ts: src/toolsets. Every earlier step exit 0, including py-tests 1100 passed. ui-build through identity-after not_run (fail-fast).", "fresh": false}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-gate-h1-2", "command": "$env:TMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:TEMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-03-release-rc1/session-gate.ps1 *> C:/Temp/av-kit/s44-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s44-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE','build_inputs','mismatch','audit rule','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 attempt 6, the registered D6 gate, whole tree after ECN-6, ECN-7, ECN-8, ECN-9, ECN-10 and the rebuild", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "Every step exit 0 except mcp-audit exit 1, which audit-rule.py tolerated (rule exit 0). py-tests 1186 passed in 123.98s (0:02:03). ui-tests 108 files, 1138 passed. mcp-tests 34 files, 466 passed. ui-electron 182 passed (3.7m). mcp-audit authoritative: 98/99 pass, 0 discovery finding(s), cleanup ok, exit 1; the one failure is transcript.compile: no transcript fetched (transcripts_done 0, last_item_status Pending); live-rigging-snow_vol1.md 37 B. build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573, build record matches. task-contract 45 row(s). changed paths: 93 outside scope: [] head: 24e27354e35eccc0cfa7d7e76357e673a6e38c23 head moved (S4): False. baseline excused py [] ui []. tested_state before and after equal. session-gate: INCOMPLETE VERIFICATION: every other step exits 0, but the authoritative audit stays non-pass. Transcript is not verified end to end while YouTube blocks captions (YOUTUBE-CAPTIONS-IP-BLOCK).", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus and the audit report were updated", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "Drift check passed — SSOT loaded (112 MEUs, 12 phases), rendered regions match on-disk content The copied audit report holds no gmail-form address."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-h1-4-openapi", "command": "rtk proxy uv run python -c '<task.md row H1-4 compare of baseline.sha and the working file>' *> C:/Temp/av-kit/openapi-check.txt", "cwd": "P:/av-kit", "scope": "H1-4: the committed OpenAPI file against baseline.sha", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "info.version: 0.1.0 -> 0.1.0rc1 components and paths unchanged: True The gate's openapi step exit 0."}
```

### Quality Gate Results

`s44-gate-h1-2` is the fresh full record, and it isn't a clean pass. Its last line is:

> session-gate: INCOMPLETE VERIFICATION: every other step exits 0, but the authoritative audit stays non-pass. Transcript is not verified end to end while YouTube blocks captions (YOUTUBE-CAPTIONS-IP-BLOCK).

The gate exits 0 because D-186 tolerates exactly one state: `transcript.compile` is the only failure, it wrote a real output file, and a direct caption fetch from this machine is blocked right now. `audit-rule.py` checked all three (rule exit 0). The audit's own verdict stays non-pass (`mcp-audit authoritative: 98/99 pass, 0 discovery finding(s), cleanup ok, exit 1`), the audit report says so, and the baseline wasn't refreshed. Transcript isn't verified end to end from this machine. That run doesn't check the content of compiled output either (plan F7).

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract` (45 row(s)), `scope-paths` (93 changed paths, none outside scope, head not moved), `build-identity-selftest`, `audit-rule-selftest`, `audit-clear-selftest`: all exit 0.
- **Suites:** `py-tests` 1186 passed in 123.98s (0:02:03); `ui-tests` 108 files, 1138 passed; `mcp-tests` 34 files, 466 passed. Baseline failures excused: none.
- **Builds and state:** `mcp-build`, `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi`, `state-render`, `build-record` (`build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573`): all exit 0.
- **Runtime:** `ui-electron` 182 passed (3.7m); `mcp-audit-clear` exit 0; `mcp-audit` 98 of 99, 0 discovery findings, cleanup ok.
- **Identity:** `tested_state` `24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382`, the same before and after. Row H1-2 set `TMP` and `TEMP` under ECN-2 (D-190).
- **Attempts:** attempt 1 (`s44-gate-h1-2-attempt1`, state `…+ab9c5df6…`) failed `mcp-tests` on AC-68.2, a defect in row 5b, with 1 failed and 464 passed. Later steps didn't run. Its receipts are archived. Attempt 2 (state `…+7eba916b…`) passed on the build from before Mat's rulings (`py-tests` 1100 passed, `ui-tests` 1111 passed, `mcp-tests` 466 passed, `ui-electron` 181 passed), and ECN-6 superseded it. Attempt 3 (state `…+f52fc9d6…`) passed on the build from before round 2's findings (`py-tests` 1186 passed, `ui-tests` 1115 passed, `mcp-tests` 466 passed, `ui-electron` 181 passed), and ECN-8 superseded it. Neither has a record here, because `durable_evidence.py --require-full` accepts a passing full record only for the state under review. Attempt 4 failed `ui-electron` with 2 failed and 179 passed, AC-88.12's clipboard primer and AC-66.14's test timeout, while Mat dismissed the main-process error dialogs that ECN-9 fixes. Later steps didn't run. Its receipts are in `C:/Temp/av-kit/rc1/attempt-4/`. Attempt 5 (state `…+08022c05…`) passed on the build from before round 3's finding (`py-tests` 1186 passed, `ui-tests` 1129 passed, `mcp-tests` 466 passed, `ui-electron` 182 passed), and ECN-10 superseded it, so it has no record here for the same reason. Its receipts are in `C:/Temp/av-kit/rc1/attempt-5/`. Attempt 6 is this run, after the fix for round 3's finding and rows 10 to 13 again.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/package.json`, `mcp-server/package.json`, four `pyproject.toml` | modified | Licence, and for `ui` the description, author, homepage and repository; the RC version |
| `ui/electron-builder.yml` | modified | `artifactName`, `!*.zip` filter, `LICENSE` and generated list |
| `README.md` | modified | The two installer filename mentions and the FFmpeg lines. The "No installer yet" note stays (D-187) |
| `packaging/THIRD_PARTY_NOTICES.md` | modified | One pointer line, and `## FFmpeg` names the re-pinned build |
| `tools/generate_third_party_licenses.py`, `packaging/licence-overrides/*` | new | `LICENCE_LIST` and its ten reviewed texts |
| `tools/assemble_ffmpeg_source.py`, `tests/unit/test_assemble_ffmpeg_source.py` | new | The source archive and AC-110.20 to AC-110.22 |
| `tools/fetch_ffmpeg_windows.ps1`, `tests/unit/test_packaging_installer.py` | modified | The re-pin and its test |
| `tools/smoke_packaged_rc.py` | new | AC-110.11, AC-110.12, AC-110.17 against any install root |
| `tests/unit/test_release_packaging.py`, `tests/unit/test_generate_third_party_licenses.py` | new | AC-110.1 to AC-110.9, AC-110.17, AC-110.18 |
| `packages/api/src/avkit_api/__init__.py`, `mcp-server/src/index.ts`, `openapi.committed.json`, the three lockfiles | modified | `VERSION_ONE` |
| `docs/releases/v0.1.0-rc.1.md`, `publish-checklist-v0.1.0-rc.1.md`, `v0.1.0-rc.1-build-record.json` | new | Release materials |
| Plan folder: `build-identity.py`, `build-rc.ps1`, `packaged-probes.ps1`, `install-roundtrip.ps1`, `packaged-app-smoke.mjs`, `audit-rule.py`, `audit-clear.ps1`, `session-gate.ps1` | new or modified | The plan's scripts |
| `docs/build-plan/07-distribution.md`, `build-priority-matrix.md`, `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md`, `known-issues.yaml`, `known-issues.md` | modified | Spec, registration and the filed issues, shared with the other four MEUs |

```diff
+  artifactName: ${productName}-Setup-${version}.${ext}
```

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | None open at approval. Findings by round are in the rolling review. | — | — | — |

### Verdict

Codex approved with no findings open and `intent_achieved: yes`, at report round 4 and ledger round 2 of 6 (dispatch `s44-exec-r4b`). The reviewer's verdict and its stated limits are in `2026-11-03-release-rc1-implementation-critical-review.md`. This line only points there.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Tag, GitHub release, repository settings | out-of-scope | — | Mat directed one commit (D-206), and the outward steps wait for Mat's go-ahead (checklist steps 4 to 10). The recreation, the public switch, CI and the first dependency batch were done on Mat's direct request before this baseline. |
| Clean-machine install (07 `:372`), including DUPER | out-of-scope | — | Mat waived it for now and will run it from the published release (D-204, checklist step 6). That step covers what this PC cannot prove: a real F2 picker capture and first model provisioning into an empty cache. |
| Code signing | out-of-scope | — | 07 `:183`: "if not, ship unsigned and document SmartScreen" |
| Auto-update | out-of-scope | — | 07 `:182`: "optional; do not block ship on it" |
| CONTRIBUTING, SECURITY | out-of-scope | — | Not in 07's contract; not requested. `.github/` and CI landed in `8a11d6b` and `889d2a0`. |
| Other app bugs found while staging screenshots (transcript titles, SABR quality label, TTS GPU device option, cosmetic items) | out-of-scope | — | Not part of 07's contract; do not break the quick start. Filed as known issues and listed in the release notes (Human-approved scope: Mat reviews them there). |
| The second dependency batch and the `minimatch` dev-only alert #118 | out-of-scope | — | `docs/distribution/dependency-updates.md` §Monthly update and §Held back: the next monthly batch. |
| CI upload of an installer | out-of-scope | — | `tests/unit/test_ci_workflows.py` fails if `build-windows.yml` uploads anything or fetches FFmpeg. D-101's ruling doesn't change that: release assets come from the local build. |
| Transcript end-to-end verification while `YOUTUBE-CAPTIONS-IP-BLOCK` holds | out-of-scope | — | D-186, D-204: Mat accepted it for now and rechecks from the published release (checklist step 7) |
| Removing the README's "No installer yet" note | out-of-scope | — | D-187; checklist step 9, after publishing |

---

## Decision Log

```yaml
decision_log:
  - id: D-190
    stage: execution
    question: "The closeout validator's selftest failed 5 of 215 arms under the default temp folder, because a folder holding .agent appeared in an ancestor of it, outside the repository. Change the tool, excuse the step, or run the gate elsewhere?"
    resolution: autonomous
    class: two-way
    chosen: "No tool or gate change. H1-2 runs with TMP and TEMP in a folder with no such ancestor, so the selftest really runs, and CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR is filed."
    source_tag: Local Canon
    precedents: ["tools/validate_closeout_artifacts.py:1736-1749 project_root returns the nearest ancestor holding .agent", "plan ECN-2 records the three selftest runs"]
    research: { engine: none, sources: [] }
    reasoning: "Excusing the step would hide a real check, and the folder isn't this session's to touch. Real runs on this repository's plans are unaffected, and running elsewhere changes nothing the selftest proves. A tool fix is a separate, filed piece of work."
  - id: D-191
    stage: execution
    question: "The smoke found CONVERT-JOB-GPU-PREFERENCE-IGNORED: the Convert page's Encoder choice and avkit_convert add's gpu_preference have no effect, and only the saved setting does. Fix it in RC1 or disclose it?"
    resolution: autonomous
    class: two-way
    chosen: "File it and list it in the release notes. The smoke's conversion uses the default encoder path. Mat can overrule at completion."
    source_tag: Local Canon
    precedents: ["plan D-181 limits the RC to the named quick-start fixes, extended only by Mat's D-185", "plan Out of Scope row for other app bugs: filed as known issues and listed in the release notes"]
    research: { engine: none, sources: [] }
    reasoning: "It doesn't break the quick start and a working encoder is still chosen. A fix would be out of the approved scope and would rerun rows 10 to 12. Leaving it out of the notes wasn't an option, because users would see the dropdown do nothing. Outcome, 2026-11-04: Mat overruled this (ECN-6), and MEU-112 fixed it."
  - id: D-192
    stage: execution
    question: "Two new tracked licence texts, zlib.txt and cpython-incorporated.txt, carry five upstream authors' published addresses. The zlib notice says it may not be altered, and a standing rule bars a personal address in a new tracked file. Keep or remove?"
    resolution: autonomous
    class: two-way
    chosen: "Keep the upstream texts verbatim. Read the rule as protecting the maintainer's own address, which appears in none of them and neither does any gmail address. Flag it for Mat at completion, before anything is pushed."
    source_tag: Local Canon
    precedents: ["packaging/licence-overrides/zlib.txt:24 This notice may not be removed or altered from any source distribution", "the rule sits under the git commit identity heading and concerns the commit author's own address"]
    research: { engine: none, sources: [] }
    reasoning: "Altering the notice would break the licence the file exists to honour, and these addresses are already published by their owners inside the same projects' public sources. Nothing is committed yet, so Mat can still overrule this at ordinary cost. Outcome, 2026-11-04: replaced by D-205, Mat's ruling with its condition verified."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Initial MEU-110 handoff after H1-2 |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Re-pin, source archive, AC-110.20 to AC-110.22 and the rebuild after Mat's rulings (ECN-6); gate rebound to H1-2 attempt 3 |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Fourth build after round 2's F1, checklist step 7 rewritten for F2 (ECN-8), fifth build after the crash fix (ECN-9); gate rebound to H1-2 attempt 5 |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Sixth build after the fix for round 3's F1 (ECN-10); packaged proofs and gate rebound to H1-2 attempt 6 |
