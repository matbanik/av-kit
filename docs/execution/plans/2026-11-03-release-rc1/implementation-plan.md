---
project: "2026-11-03-release-rc1"
date: "2026-11-03"
source: "docs/build-plan/07-distribution.md#release-candidate-packaging-residual"
meus: ["MEU-108", "MEU-109", "MEU-110"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Release candidate 1 preparation (Session 44)

> **Project:** `2026-11-03-release-rc1`
> **Build plan:**
> - `docs/build-plan/07-distribution.md` §Release candidate packaging (residual), new in row 1 (MEU-110)
> - `docs/build-plan/07-distribution.md` §PythonManager (`:199`), §FFmpeg (`:157`), §Electron packaging (`:175`), §Testing (`:344`), §Exit checklist (`:360`) are Local Canon
> - `docs/build-plan/06-gui.md` §Ready probe (residual), new in row 1 (MEU-108)
> - `docs/build-plan/08-video-conversion.md` §Output folder (residual), new in row 1 (MEU-109)
>
> **Source request:** Mat, 2026-11-03: "create MIT license file / prepare whatever we need to build and publish the release rc1 candidate".
> **Known issues:** `FFMPEG-GPL-BUILD`, `FFMPEG-PIN-URL-404` (both held on D-101), `INSTALLER-SHIPS-FFMPEG-ZIP`, `NOTICES-SPACY-TRANSITIVE`; new this session: `GUI-READY-PROBE-BLOCKS-MAIN`, `CONVERT-OUTPUT-DIR-MISSING`.
> **Status:** `draft`. `plan_to_exec_gate: human`; Mat's message above is the execution direction for reversible preparation only (see §User Review Required).
>
> Line anchors are from `main` `3dd591c`. The tree holds the uncommitted public README, `docs/images/` and `LICENSE` from this conversation.

## Goal

The repository is about to go public and the first release candidate is due. Nothing has been released before, so this is the first time anyone outside this machine runs the installer. Four things stand between today's `main` and a release that can be published:

1. **Two bugs a new user hits in the first five minutes, both inside the README's quick start.**
   - Every chunk of backend output runs a blocking PowerShell process query on the main thread (`ui/src/main/index.ts:279`, `ui/src/main/live-identity.ts:126`), so the window freezes during busy work.
   - Convert's default output folder does not exist on a fresh machine and nothing creates it, so the first conversion always fails with `ffmpeg exited 4294967294` (`packages/core/src/avkit_core/services/conversion.py:353`).
2. **Licensing that a public release must get right.** There is no licence metadata, and `THIRD_PARTY_NOTICES.md` names 6 components of a bundle whose backend alone holds 69 Python distributions (`NOTICES-SPACY-TRANSITIVE`; §Planning receipts).
3. **An installer that has never been built from today's tree or run through NSIS.** The local backend is from 2026-08-24, the local FFmpeg folder has no `LICENSE.txt`, and `current-focus.md` records that packaged probes have not run since the 31b merge. That backend predates the current spec and carries GPL `phonemizer` inside its module archive, so the old `ui/dist/av-kit Setup 0.1.0.exe` must never be uploaded.
4. **A human decision.** D-101 (FFmpeg licence posture) is open and gates public distribution. This plan prepares the brief, not the ruling.

The session ends with a built, tested installer on disk, release notes, an exact publish checklist and the D-101 brief. It stops before every outward step.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-03). A headroom binary is on PATH but no payload here is oversized: the scope is a named list of files read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy` with receipts under `C:/Temp/av-kit`.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`, under ledger loops `s44-plan-2026-11-03-release-rc1` and `s44-execution-2026-11-03-release-rc1`. Claude wrote the plan, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable or the ledger refuses a round, the fallback is Mat. Each round is metered; the coordinator warns before dispatching.
- **Never in this session:** commit, push, tag, create a GitHub release, upload an asset, change repository visibility, edit repository settings, re-pin FFmpeg, rule on D-101, merge `pill-palette-darker`, touch DUPER, or author an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-108` | `.agent/context/handoffs/2026-11-03-release-rc1-MEU-108-handoff.md` |
| `MEU-109` | `.agent/context/handoffs/2026-11-03-release-rc1-MEU-109-handoff.md` |
| `MEU-110` | `.agent/context/handoffs/2026-11-03-release-rc1-MEU-110-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-03-release-rc1-plan-critical-review.md` and `.agent/context/handoffs/2026-11-03-release-rc1-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| Package | Rows | Strategy | Why |
|---|---|---|---|
| Registration | 0, 1 | shared | Short; every later row reads the same state |
| Two fixes | 2 to 5 | shared | Small, independent, Red then Green |
| Packaging code | 6 to 9 | shared | Metadata, the licence generator and the version bump interact through the build |
| Real build and smoke | 10 to 12 | compact_continue | Long-running; output is durable receipts |
| Release materials | 13 | shared | Written from the verified build |
| Closeout | H1, H2 | per template | |

## User Review Required

> [!IMPORTANT]
> **D-101 gates public distribution, and it is Mat's call.** This session builds with the current GPL FFmpeg pin, taken from the cached archive whose SHA-256 matches the pin. That build proves the pipeline and is a valid private RC. Under the recommended ruling it would be rebuilt with a re-pinned FFmpeg, with the complete source set assembled, before anyone outside can download it. See D-101 in the Decision Log.
>
> **Mat's message authorizes preparation, not publication.** Commit, push, the tag (AGENTS.md: "never push any ref other than `main`"), the GitHub release, and the private-to-public switch each wait for an explicit go-ahead. The publish checklist lists them in order with exact commands.
>
> **A real install runs on this PC (row 12).** NSIS has never been exercised, and `win-unpacked` does not test it. Row 12 runs the installer silently into a throwaway folder, launches the installed app with a throwaway `AVKIT_APP_DATA`, runs the uninstaller, and compares a before and after snapshot of the Uninstall key, the `Run` and `StartupApproved\Run` values and the shortcuts. Today neither registry location has an av-kit value, no Uninstall entry or install exists and no `av-kit.exe` is running (checked 2026-11-03), so the uninstaller's cleanup removes nothing of Mat's. `%LOCALAPPDATA%/av-kit` does hold Mat's real database and settings. The throwaway `AVKIT_APP_DATA` keeps the app out of it, `deleteAppDataOnUninstall` stays `false`, `--delete-app-data` is never passed, and the snapshot proves the folder's top-level entries survive. Row 12 re-checks all of this (S5) and stops if anything has changed. This does not replace the clean-machine test.

## Proposed Changes

### Single-statement contracts

- `READY_GUARD`: `live-identity`'s process query runs only for an output chunk that carries a usable `AVKIT_READY` line. Every other chunk does no process query.
- `OUTPUT_PARENT`: `encode`, `cut` and `extract_stream` create `output_path.parent` before starting FFmpeg, matching `capture/adapter.py:359`.
- `LICENCE_LIST`: the installer carries a generated file that lists every third-party component actually in the build, with the full text of every licence or notice its distribution carries. Generation fails rather than ship an unattributed, unowned or unexpected-GPL component, or read a stale build.
- `VERSION_ONE`: one release version, spelled per ecosystem, on every shipped surface; a test fails when they drift.
- `BUILD_RECORD`: the build writes the identity of its inputs, the installer's name, size and SHA-256, and its toolchain. `build-identity.py --verify-record` fails when the tree or the installer no longer matches.

### MEU-108 — `gui-ready-probe-guard`

Spec section added to `06-gui.md`. Today's `onChildOutput` closure in `ui/src/main/index.ts:266-292` calls `queryLiveProcess` before `confirmReadyAndPublish` looks at the text, which is why it runs for every chunk.

- New exported `publishIfReady` in `ui/src/main/python-manager.ts` takes the chunk text and an injected `queryLive`. It tests the text with the regex `confirmReadyAndPublish` uses, returns `false` without querying when there is no usable READY line, and otherwise delegates to `confirmReadyAndPublish`. The regex moves to one shared constant so the guard and the publisher cannot disagree.
- `index.ts` calls `publishIfReady` and keeps the published log note as is.

| AC | Statement | Source |
|---|---|---|
| AC-108.1 | A chunk with no `AVKIT_READY` line calls `queryLive` zero times and publishes nothing. | Spec (06 §Ready probe) |
| AC-108.2 | `AVKIT_READY port=0` calls `queryLive` zero times and publishes nothing. | Spec; existing `port=0` rule `python-manager.ts:98` |
| AC-108.3 | A usable READY chunk calls `queryLive` once and publishes the same `apiBase` and token as `confirmReadyAndPublish`. | Local Canon 07 §PythonManager step 3 |
| AC-108.4 | `index.ts` no longer calls `queryLiveProcess` outside `publishIfReady`'s injected callback in the output handler. | Spec; source-text test |

**Red:** AC-108.1 fails decisively only once the helper exists with today's behaviour, so row 2 first extracts `publishIfReady` as a behaviour-preserving move (query first, then match), then adds the tests. The Red is an assertion failure on `queryLive` call count, not an import failure.

### MEU-109 — `convert-output-folder`

Spec section added to `08-video-conversion.md`. The fix belongs in the infrastructure adapter: core services do not touch the filesystem for this and `capture/adapter.py:359,375` is the precedent. A failed `mkdir` raises `OSError`, which `_process` already reports through `_finish(Failed, error=str(exc))` (`conversion.py:468-472`), so the user reads the path problem instead of an FFmpeg exit code.

| AC | Statement | Source |
|---|---|---|
| AC-109.1 | `encode` to a path whose parent folders do not exist creates them before FFmpeg starts. | Spec (08 §Output folder) |
| AC-109.2 | `cut` does the same. | Spec |
| AC-109.3 | `extract_stream` does the same. | Spec |
| AC-109.4 | An existing folder is left alone and its contents survive. | Spec |
| AC-109.5 | When the folder cannot be created, the job ends `Failed` with an error naming the path, and FFmpeg never starts. | Spec; `conversion.py:468-472` |

**Red:** in `tests/unit/test_ffmpeg_conversion.py`, a recording `Popen` captures `output.parent.is_dir()` at spawn time. Today it records `False`. Real FFmpeg against a missing folder is proved in row 11.

### MEU-110 — `dist-release-candidate`

Spec section added to `07-distribution.md`.

**Licence and metadata (rows 6, 7).** `ui/package.json` gets a user-facing `description` (it feeds the installer's file properties), `license`, `author`, `homepage`, `repository`. `mcp-server/package.json` and the four `pyproject.toml` get `license`. `electron-builder.yml` ships `../LICENSE` as `resources/LICENSE` and the generated list as `resources/THIRD_PARTY_LICENSES.txt`, adds the `!*.zip` filter on the FFmpeg entry and sets `artifactName`. The README's licence section, download links and an RC note are updated.

**Complete licence list (row 8).** New `tools/generate_third_party_licenses.py`. It reads what actually shipped, not what the environment holds:

- **Python, the payload:** reads `COLLECT-00.toc` (every file in `_internal`) and `PYZ-00.toc` (every module inside the exe). It refuses a stale build: `COLLECT` destinations must equal the `_internal` folder on disk, and `PYZ` names must equal the module archive inside `avkit-backend.exe`. A probe build of today's spec met both exactly.
- **Python, the owners:** maps each source path to its owning distribution through `importlib.metadata` `RECORD` data. Each owner contributes name, version, licence and the full text of every licence or notice file anywhere in its `RECORD`, whether or not that file is in a TOC. Notice files match, case-insensitively, `(^|/)(licen[cs]e|copying|notice|thirdpartynotices|third[-_]party|authors)[^/]*$`. That is how `onnxruntime/ThirdPartyNotices.txt` (343,249 bytes, in no TOC) and numpy's vendored licences reach the list. A `RECORD`-listed notice missing on disk, or an owner with no notice at all, refuses.
- **Python, the payload with no owner:** every such file or module must fall into one named class, or generation refuses:
  - first party: the repository's `packages/` and `__main__`, left off the list;
  - CPython: stdlib modules, `base_library.zip`, `DLLs/*.pyd`, `python3.dll` and `python312.dll`, under `sys.base_prefix/LICENSE.txt` (PSF terms and bzip2);
  - CPython's other native libraries, which that file does not cover: OpenSSL, libffi, SQLite, xz, expat, libmpdec, zlib and HACL\*. Their texts come from reviewed files in `packaging/licence-overrides/`, each carrying the upstream text, version and source URL;
  - Windows runtime, matched by filename wherever PyInstaller found it: `api-ms-win-*`, `ucrtbase`, `vcruntime140*`, `msvcp140*`. The probe took 47 of these from a JDK folder on `PATH`, so the build record hashes them;
  - namespace packages with no source file (TOC source `.`), attributed to their top-level distribution.

  The bootloader's GPL-with-exception terms are stated.
- **npm:** the non-dev closure of `ui/package-lock.json`. Every bare import in `ui/src` resolves to a production dependency or to `electron` (checked 2026-11-03), so this closure is complete for the renderer and the main process. `mcp-server` keeps its own `LICENSES.txt`.
- **.NET:** the licences of the exact runtime packs named by the fresh `native/region-picker/publish/*.deps.json`, from `~/.nuget/packages/microsoft.netcore.app.runtime.win-x64/<version>/{LICENSE.TXT,THIRD-PARTY-NOTICES.TXT}` and `microsoft.windowsdesktop.app.runtime.win-x64/<version>/LICENSE`. `build:picker` publishes the runtime self-contained and the publish folder carries no licence. A missing pack or file refuses, so the generator runs after `build:picker`.
- **Electron and Chromium:** not generated. electron-builder keeps `LICENSE.electron.txt` and `LICENSES.chromium.html` in the install root, and AC-110.11 checks them.
- **Fails closed:** any component with no licence text, any unowned payload outside the classes above, or a licence that is GPL-class and not on an explicit allow list, exits non-zero. The allow list starts as `num2words` (LGPL, already covered by AC-72.7's LGPL appendix) and the avkit workspace itself is excluded as first-party. `phonemizer-fork` (GPLv3+) is in `.venv`; if it reaches the bundle, the build fails.
- **Output:** `packaging/dist/THIRD_PARTY_LICENSES.txt` (gitignored, built output), also attached to the release. `THIRD_PARTY_NOTICES.md` stays hand-curated for AC-72.7 and gains one pointer line.

**Release materials (row 13).** The publish checklist runs in this order: D-101 ruling; if the ruling changes FFmpeg, re-pin and refresh the cached archive, update the `## FFmpeg` section of `THIRD_PARTY_NOTICES.md`, the tests that pin the old version (`test_packaging_installer.py:224-225,246`) and the README's FFmpeg lines, assemble the complete source set, rerun rows 10 to 12 and copy the new build record to `docs/releases/`; Mat's exposure review (commit email, `C:\Users\Mat` paths in tracked files, `docs`, `.agent` and `_inspiration` going public, root `rottiboo.png`); commit and push `main`; `build-identity.py --verify-record docs/releases/v0.1.0-rc.1-build-record.json --ref HEAD`, which must match the pushed commit and the installer's bytes; tag `v0.1.0-rc.1`; `gh release create --draft --prerelease` with the installer and `THIRD_PARTY_LICENSES.txt`; clean-machine verification from the draft's asset, including a real F2 picker capture and first model provisioning into an empty cache; switch the repository public and publish the draft; repository description and topics.

**Version (row 9).** `0.1.0-rc.1` in `ui/package.json`, `mcp-server/package.json` and `mcp-server/src/index.ts`; `0.1.0rc1` in `packages/api/src/avkit_api/__init__.py`, the four `pyproject.toml` and `openapi.committed.json` (regenerated through `tools/export_openapi.py`). Lockfiles follow. Fixtures in `mcp-server/tests/audit/*` and `bundle-licenses.test.ts`, and the audit client's own version in `scripts/audit/client.ts:56`, are not release surfaces and stay.

| AC | Statement | Source |
|---|---|---|
| AC-110.1 | `LICENSE` is MIT, is installed as `resources/LICENSE`, and every package manifest declares MIT. | Human-approved (Mat 2026-11-03) |
| AC-110.2 | The README states MIT, links `LICENSE`, says bundled components keep their own licences, and its download links reach prereleases. | Human-approved; Research-backed (GitHub REST docs: latest excludes prereleases) |
| AC-110.3 | `electron-builder.yml` filters `*.zip` from the FFmpeg entry, and no zip lands in `resources/ffmpeg` when one sits in the source folder. | Local Canon (`INSTALLER-SHIPS-FFMPEG-ZIP`) |
| AC-110.4 | The installer's filename has no spaces, so GitHub keeps it as built. | Research-backed (GitHub REST docs: asset renaming) |
| AC-110.5 | The generator lists every distribution that owns a file in a fixture `COLLECT-00.toc` or a module in a fixture `PYZ-00.toc`, with version, licence and the full text of every licence or notice file in its `RECORD`. A distribution reached only through the PYZ is listed. | Local Canon (`NOTICES-SPACY-TRANSITIVE`: "Generate the list from the built bundle's environment") |
| AC-110.6 | The generator exits non-zero for a distribution with no licence or notice file, and for one whose `RECORD` lists a notice missing on disk. | Spec (07 §Release candidate) |
| AC-110.7 | The generator exits non-zero for a GPL-class component not on the allow list, and passes for an allow-listed one. | Spec; Local Canon (`03-service-layer.md:453`: espeak-ng never ships) |
| AC-110.8 | `resources/THIRD_PARTY_LICENSES.txt` is shipped and generated from the real build, after AC-110.18's stale-build guard passes. | Spec |
| AC-110.9 | Every release surface carries the one RC version; a test fails on drift. OpenAPI matches. | Spec |
| AC-110.10 | A real NSIS installer is built from today's tree, after clearing the stale `ui/dist`, `packaging/build` and `packaging/dist`, with fresh backend, picker, MCP bundle and FFmpeg-with-licence; size and SHA-256 are recorded; size is under 500 MB. | Local Canon 07 `:350` |
| AC-110.11 | Packaged layout: `resources/` holds `LICENSE`, both notices, `ffmpeg/{ffmpeg,ffprobe}.exe` and `ffmpeg/LICENSE.txt` with no zip, the backend, the picker with its `.deps.json` and runtime files, and `mcp-server/{index.mjs,LICENSES.txt}`; the install root holds `LICENSE.electron.txt` and `LICENSES.chromium.html`. `torch`, `torchvision`, `torchaudio`, `kokoro`, `phonemizer` and `espeakng_loader` are absent from `_internal` and from the module archive inside the shipped `avkit-backend.exe`, and `misaki.espeak` is absent from that archive. The same check reports `phonemizer` on the 2026-08-24 negative-control exe. The packaged picker, run with no arguments, loads .NET and WinForms and exits `PICKER_EXIT_ERROR` (1) with `--out <path> is required`. | Local Canon 07; `tools/smoke_packaged_tts.py`; `native/region-picker/Program.cs:24,69-78` |
| AC-110.12 | The frozen backend starts on a throwaway app-data folder, reports the RC version and the bundled FFmpeg, and completes a real first conversion into a folder that does not exist. | Spec; MEU-109 end to end |
| AC-110.13 | The MCP entry starts through `av-kit.exe` with `ELECTRON_RUN_AS_NODE` and reports the RC version. | Local Canon AC-92.4 |
| AC-110.14 | Packaged TTS runs offline from cached models. | Local Canon MEU-72 `PACKAGE_SMOKE` |
| AC-110.15 | The installed app from a silent NSIS install launches, reaches the backend and renders a page. The uninstaller leaves no Uninstall key, `Run` or `StartupApproved\Run` value, shortcut or install folder behind, and `%LOCALAPPDATA%/av-kit` keeps the same top-level entries. | Local Canon 07 `:310`, `:372`, §Login item uninstall `:186` |
| AC-110.16 | Release notes state what the RC is, what it does not fix and how to report problems. The publish checklist gives the outward steps in order with exact commands, including `--verify-record` before the tag and a clean-machine step with a real F2 picker capture and first model provisioning into an empty cache. D-101 is presented as a Decision Brief. | Human-approved (Mat 2026-11-03) |
| AC-110.17 | `resources/THIRD_PARTY_LICENSES.txt` from the real build contains the complete text of onnxruntime's `ThirdPartyNotices.txt` and of numpy's vendored licences. A fixture proves a notice outside dist-info and outside the TOC is included. | Spec (07 §Release candidate) |
| AC-110.18 | Every file and module in the build is owned by a distribution or falls in a named class (first party, CPython, CPython native library with a reviewed text, Windows runtime, source-less namespace package); anything else exits non-zero. The generator also exits non-zero when the TOCs disagree with `_internal` or with the exe's module archive. | Spec (07 §Release candidate) |
| AC-110.19 | `build-identity.py --selftest` proves a PyInstaller spec, a Vite config, an MCP bundling script, `global.json` and `build-rc.ps1` each change the identity while docs, tests and `.agent` do not. The build writes a record with the identity, installer hash, FFmpeg hashes and toolchain versions. `--verify-record` passes on the result and fails on a changed product file or installer. | Spec (07 §Release candidate) |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Ruling on D-101, re-pinning FFmpeg (`FFMPEG-PIN-URL-404`) | out-of-scope | — | `.agent/context/grouping/2026-10-17-gui-shell-and-tts-sideload-session-grouping.md:167`: "Not an agent call. No MEU is registered until Mat rules." |
| Commit, push, tag, GitHub release, visibility switch, repository settings | out-of-scope | — | AGENTS.md §Commits; Mat's request says "prepare" |
| Clean-machine install (07 `:372`), including DUPER | out-of-scope | — | Needs a clean machine, and DUPER is an in-use desktop. Listed in the publish checklist as a gate before the public switch, for Mat to run or waive. That step covers what this PC cannot prove: a real F2 picker capture and first model provisioning into an empty cache. |
| Merging `claude/pill-palette-darker` | out-of-scope | — | Uncommitted work in another worktree; `current-focus.md` plan, Mat's direction needed. RC1 ships without it unless Mat says otherwise. |
| Code signing | out-of-scope | — | 07 `:183`: "if not, ship unsigned and document SmartScreen" |
| Auto-update | out-of-scope | — | 07 `:182`: "optional; do not block ship on it" |
| CI, `.github/`, CONTRIBUTING, SECURITY | out-of-scope | — | Not in 07's contract; not requested |
| Other app bugs found while staging screenshots (transcript titles, SABR quality label, TTS GPU device option, cosmetic items) | out-of-scope | — | Not part of 07's contract; do not break the quick start. Filed as known issues and listed in the release notes (Human-approved scope: Mat reviews them there). |

## BUILD_PLAN.md Audit

This project adds three residual sections and three matrix rows. `docs/BUILD_PLAN.md` regions regenerate through `tools/meu_status.py render`; validation is `rtk proxy uv run python tools/meu_status.py render --check`.

## Verification Plan

### 1. Prerequisites and baseline (row 0)

Record `HEAD` in `baseline.sha`. `uv sync --frozen --all-packages`, `npm --prefix ui ci`, `npm --prefix mcp-server ci`. Baseline Python and UI suites to `s44-base-py.txt` and `s44-base-ui.txt`; expected failures are the environmental packaging ids from S43's gate. Row 0 rebuilds nothing else.

### 2. Red then Green (rows 2 to 5, 8, 9)

Each Red receipt holds a decisive assertion failure, not an import failure. Expectations stay immutable in Green.

### 3. Real build (row 10)

`build-rc.ps1`, in order:

1. Clear `ELECTRON_RUN_AS_NODE`. Refuse unless the negative control `C:/Temp/av-kit/rc1/negative-control/avkit-backend.exe` (the 2026-08-24 exe, kept at plan time) still has its recorded SHA-256. Record the starting `build_inputs`.
2. Delete the stale gitignored outputs `ui/dist`, `packaging/build` and `packaging/dist`.
3. Copy the cached archive to `packaging/ffmpeg-win64/ffmpeg-pin.zip` and run `tools/fetch_ffmpeg_windows.ps1 -ExtractOnly`, so `LICENSE.txt` is present and the SHA-256 is rechecked. The zip left in that folder is what AC-110.3's filter must keep out.
4. Build the backend with `uv run python tools/package_backend.py` (never `--stub-ok`).
5. `npm --prefix ui run dist:prep`, then the generator, then electron-builder from `ui`. Plain `npm run dist` cannot be used: the generator needs the picker's fresh `.deps.json` from `dist:prep`, and electron-builder needs the generator's output.
6. Fail if the installer is 500 MB or larger. `build-identity.py --write-record C:/Temp/av-kit/rc1/build-record.json --expect-inputs <start>` refuses if an input changed during the build.

Any product correction after this row means rerunning rows 10 to 12, and `--verify-record` flags it (S8).

### 4. Packaged smoke (rows 11, 12)

`tools/smoke_packaged_rc.py` proves AC-110.11, AC-110.12 and AC-110.17 against any install root, so the same checks run on `win-unpacked` and on the NSIS install. Its bans read the module archive inside the shipped exe through PyInstaller's `CArchiveReader`: `tools/smoke_packaged_tts.py` only tests for folders under `_internal`, which would have passed the 2026-08-24 build with `phonemizer` inside its exe. The negative control proves the new check would have caught it. AC-110.13 reuses `plan_checks.py mcp-probe` from Session 31b. AC-110.14 runs `tools/smoke_packaged_tts.py --phase offline` on a copy of the packaged backend with the models cached at `C:/Temp/av-kit/s32-smoke-models`. Its online phase is not run, because it rebuilds the onedir. `packaged-app-smoke.mjs` launches the real `av-kit.exe` through Playwright with a throwaway `AVKIT_APP_DATA` for AC-110.15.

`install-roundtrip.ps1` installs with `/S /D=C:\Temp\av-kit\rc1\install`, with `/D` last and unquoted. It reads the real location from the Uninstall key, because `/D` may not be honoured, and tests that location. It uninstalls with `/S`, never `--delete-app-data`, and waits for the uninstaller's relaunched copy to finish, with a bounded timeout, before comparing snapshots.

### Plan-local scripts

Written with their rows and kept in this plan folder: `build-rc.ps1` (row 10), `packaged-probes.ps1` (row 11, MCP probe and offline TTS), `install-roundtrip.ps1` and `packaged-app-smoke.mjs` (row 12), `build-identity.py` (hashes every tracked file outside a short exclude list, with `--selftest`, `--write-record` and `--verify-record`), `red-check.py`, `identity.py`, `session-gate.ps1`. The product-side tools are `tools/generate_third_party_licenses.py` (shipped output) and `tools/smoke_packaged_rc.py` (reusable for later releases).

### 5. Session gate (row H1-2): `session-gate.ps1`

PROFILE D6, adapted from S43: identity, static checks, scope paths, `build-identity.py --selftest`, full suites, OpenAPI, state render, `build-identity.py --verify-record` (fails if a product input or the installer changed after row 10), the Electron suite, identity again. `mcp-audit` is not run: no MCP tool contract changes, and only the `serverInfo` version moves.

### 6. OpenAPI drift

`packages/api` changes only `__version__`. `openapi.committed.json` is regenerated and `tools/export_openapi.py --check` must pass (AC-110.9).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A graph directory appears | Re-decide the context tool |
| S2 | The build can only proceed by re-pinning FFmpeg or changing its licence posture | Stop; D-101 |
| S3 | The generator finds an unexpected GPL-class component or an unowned payload in the bundle | Stop and report; do not widen the allow list or add an override silently |
| S4 | `HEAD` moves or another session's paths appear | Stop; re-baseline with Mat |
| S5 | Any row 12 precondition fails. `HKCU\...\Run` or `...\Explorer\StartupApproved\Run` has a `com.avkit.app` value; an av-kit Uninstall entry exists; `C:/Temp/av-kit/rc1/install` already exists; `%LOCALAPPDATA%/Programs/av-kit` holds anything (NSIS deletes the install folder recursively, and `/D` may not be honoured); a Desktop or Start Menu `av-kit.lnk` exists; or `av-kit.exe` is running | Skip the install, record `[B]`, list it for Mat |
| S6 | A row 12 uninstall leaves anything behind, or `%LOCALAPPDATA%/av-kit` loses a top-level entry | Report exactly what, with the snapshot diff |
| S7 | Reviewer unavailable or ledger refuses a round | Fallback is Mat |
| S8 | `build-identity.py --verify-record` reports a mismatch after row 10 | Rerun rows 10 to 12; never edit the record |

## Decision Log

```yaml
decision_log:
  - id: D-178
    question: How is the release candidate version spelled?
    class: autonomous
    stage: planning
    decision: "0.1.0-rc.1 for npm, electron-builder and the tag v0.1.0-rc.1; 0.1.0rc1 for Python."
    basis: "Each ecosystem's own rule: SemVer 2.0 pre-release (https://semver.org), PEP 440 normalised form (https://peps.python.org/pep-0440/). tests/e2e/test_api_openapi.py:110 pins the schema version to __version__, so OpenAPI follows Python's spelling."
  - id: D-179
    question: What is the installer filename?
    class: autonomous
    stage: planning
    decision: "artifactName av-kit-Setup-${version}.${ext}."
    basis: "GitHub renames asset filenames with special characters (https://docs.github.com/en/rest/releases/assets), so the built name would otherwise differ from the README. No test or doc outside the README pins the old name (git grep, 2026-11-03)."
  - id: D-180
    question: Is the complete licence list committed or generated at build time?
    class: autonomous
    stage: planning
    decision: "Generated into packaging/dist at build time, shipped in the installer, attached to the release; not committed."
    basis: "It must match what was actually bundled. NOTICES-SPACY-TRANSITIVE notes: generate it from the built bundle's environment instead of maintaining names by hand."
  - id: D-181
    question: Which known bugs does the RC fix?
    class: autonomous
    stage: planning
    decision: "The two that break the README's quick start. Others go in the release notes."
    basis: "A release candidate tests readiness; it does not need every bug closed. These two make the documented first-run flow fail or hang."
  - id: D-182
    question: Which FFmpeg does this session's build use?
    class: autonomous
    stage: planning
    decision: "The current pin, from the cached archive whose SHA-256 matches tools/fetch_ffmpeg_windows.ps1."
    basis: "Grouping :167 forbids an agent re-pin. The pin's URL is dead upstream, and -ExtractOnly is the supported reuse path. The D-101 ruling can force a rebuild; the checklist says when."
  - id: D-183
    question: Which PyInstaller build data does the licence generator trust?
    class: autonomous
    stage: planning
    decision: "COLLECT-00.toc and PYZ-00.toc, each checked against what is really on disk and inside the exe, plus every notice file in each owner's RECORD."
    basis: "Plan review F1: a TOC lists files that entered the bundle, but onnxruntime's 343,249-byte ThirdPartyNotices.txt is in no TOC, so a TOC-only list ships its natives without their notices. COLLECT and PYZ are the last build steps, and a probe of today's spec shows both match the output exactly."
  - id: D-184
    question: How is the installer bound to the commit that gets published?
    class: autonomous
    stage: planning
    decision: "Hash every tracked file outside a short exclude list, and write a build record holding that identity and the installer's hash. --verify-record checks it at the gate and again before the tag."
    basis: "Plan review F3: the earlier allow-list omitted real inputs such as packaging/avkit-backend.spec, ui/electron.vite.config.ts, mcp-server/scripts/bundle.ts and global.json, so changing them passed unnoticed. Inverting the list means a new input is covered by default, and hashing the installer catches a rebuild from the same tree."
```

### D-101: Which FFmpeg licence posture does the public installer ship under?   [human] [distribution]

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

**Reversibility / risk:** One-way for each release: an installer cannot be unshipped. If the choice is wrong, the exposure is a licence violation on a public download. Before the repository goes public the choice is still free, because nothing has been distributed.

**If you do not answer:** The private RC stays private. The checklist holds the public switch at step 0.

## Research References

- FFmpeg legal checklist: https://ffmpeg.org/legal.html
- GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html
- GitHub release assets (renaming): https://docs.github.com/en/rest/releases/assets
- GitHub releases (latest excludes prereleases): https://docs.github.com/en/rest/releases/releases
- BtbN retention and variants: https://raw.githubusercontent.com/BtbN/FFmpeg-Builds/master/README.md
- SemVer: https://semver.org ; PEP 440: https://peps.python.org/pep-0440/
- Not used as authority: https://hoop.dev/blog/ffmpeg-license-and-compliance-essentials/ ; https://gitlab.eclipse.org/eclipsefdn/emo-team/iplab/-/issues/7912 (secondary sources, no close precedent).

## Planning receipts

- Public-readiness audit: `C:/Temp/av-kit/rc1/gitleaks-history.{json,txt}`: 14 commits, 21 `generic-api-key` hits, every one read and false-positive (filename-keyed SHA-256 digests, a pytest node id, two test fixtures). `gitleaks dir` on `README.md` and `LICENSE`: no leaks.
- Cached FFmpeg archive SHA-256 equals the pin: `5efb8182e0770c7af639ce46c229e5a5ea585884f17d2e94983051d8da90bdab`.
- `/releases/latest` and asset-renaming behaviour read from GitHub's REST docs, 2026-11-03.
- Throwaway probe build of today's spec, outside the repository: `C:/Temp/av-kit/rc1/probe/`, scan `C:/Temp/av-kit/rc1/probe-scan.txt`. `COLLECT` matches `_internal` and `PYZ` matches the exe's module archive exactly; no banned module; 69 owned distributions, none without a notice; only `num2words` (LGPL) is GPL-class. This is evidence for the design, not a build this session ships.
- The 2026-08-24 exe's real module archive: `C:/Temp/av-kit/rc1/pyz-real.txt` holds `phonemizer`, `espeakng_loader`, `misaki.espeak` and `kokoro`. Negative control kept at `C:/Temp/av-kit/rc1/negative-control/avkit-backend.exe`, SHA-256 `3d5691fc07310ca28c78d8a101fdd84d8b3100d2753605aaee6dd4a19394da87`.
- CPython's native libraries: `C:/Temp/av-kit/rc1/runtime-versions.txt` (OpenSSL 3.5.4, SQLite 3.50.4, expat 2.7.3, libmpdec 2.5.1, zlib 1.3.1). `sys.base_prefix/LICENSE.txt` has no text for OpenSSL, libffi, SQLite, xz, expat, libmpdec, zlib or HACL\*; it does cover bzip2.
- D-101 source counts from a static read of the candidate tag's scripts: `C:/Temp/av-kit/rc1/d101-exact.txt`.
- `build-identity.py --selftest`: `C:/Temp/av-kit/rc1/build-identity-selftest.txt`, 18 checks passed in a scratch repository. `--write-record` first runs for real in row 10.

## Validation stage contract

Static: `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, `scope-paths`, `build-identity-selftest`. Targeted: named test files in each Red and Green row. Fresh full: `py-tests`, `ui-tests`, `mcp-build`, `mcp-tests`, `ui-build`, `openapi`, `state-render`, `build-record`. Runtime: `ui-electron`, then the packaged rows 11 and 12, which bind to the same tree through the build record (`BUILD_RECORD`), checked at the gate's `build-record` step and again before the tag. Identity is obtained by `identity.py`, independent of the receipts. Blocking: all, native shell PowerShell, `evidence.v1` output.

## Execution Correction Notes

None yet.
