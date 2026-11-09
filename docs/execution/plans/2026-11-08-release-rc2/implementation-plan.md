---
project: "2026-11-08-release-rc2"
date: "2026-11-08"
source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md#session-57--release-rc2-meu-125--p2"
grouping_source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md"
meus: ["MEU-125"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: The second release candidate, 0.1.0-rc.2 (Session 57)

> **Project:** `2026-11-08-release-rc2`
> **Build plan:** `docs/build-plan/07-distribution.md` §Second release candidate (residual) (`:371-386`, anchor `second-release-candidate-residual`, MEU-125). Its rules reuse §Release candidate packaging (residual), MEU-110's contract.
>
> **Source request,** Mat's Session 57 brief, 2026-11-08 (`C:/Temp/av-kit/session-57-prompt.md`). One MEU, `dist-release-candidate-2` (P2), builds and checks 0.1.0-rc.2 and carries grouping D-243. It closes no product issue. Its one watch item is `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` (MONITORING, P4, D-362, `.agent/context/known-issues.yaml:4237`). Done means "every surface reads rc.2 and the version test passes; a fresh build from a clean tree passes the packaged checks, the round trip and the gate, with the build record committed; the notes, the notices line and the checklist are written and reviewed; nothing is tagged, uploaded or published."
> **Known issue:** none closed. Watch item `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE`. Cited: `FFMPEG-LIBDVDCSS-BUNDLED` (`:3401`, D-266, D-275), `MODELS-DIR-DOCS-AND-PROBE-MISMATCH` (`:3597`), `YOUTUBE-CAPTIONS-IP-BLOCK` (`:2931`), `INSTALL-FOLDER-NAME-MISMATCH` (`:3933`).
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review.
>
> Line anchors are from `main` `8bcb4a6`, read 2026-11-08. `P:/av-kit` is the only worktree (`git worktree list`, one line). The tree holds nothing but this plan folder, untracked (`git status --porcelain`, `C:/Temp/av-kit/s57-plan-tree.txt`). Session 58's capture-crop plan was committed as `8bcb4a6`, and its ids reach D-427 and MEU-132, so this plan's decisions start at D-460. MEU-113 to MEU-124 and MEU-126 are `approved`; MEU-125 is `pending` at `.agent/context/meu-status.yaml:3266` (`C:/Temp/av-kit/s57/meu-stats.txt`: 132 MEUs, 118 approved, 1 closed, 13 pending).

## Goal

**Goal anchor:** Session 57 moves every version surface to 0.1.0-rc.2, adds the libdvdcss line to the notices, builds the installer from a clean tree with the pinned FFmpeg, checks it as RC1 was checked plus MEU-114's round trip on the full build and MEU-117's and MEU-121's packaged smokes on the installer's own backend, runs a fresh gate, and writes the notes and the publish checklist. Nothing is tagged, uploaded or published: those steps are Mat's, and the checklist gives them in order.

Four things are wrong today:

1. **Every surface reads rc.1.** Thirteen files carry `0.1.0-rc.1` or `0.1.0rc1` (§Files Modified), and AC-110.9's tests pin rc.1 (`tests/unit/test_release_packaging.py:27-28`).
2. **The notices don't say the build carries libdvdcss.** The FFmpeg section of `packaging/THIRD_PARTY_NOTICES.md` names the GPL build and the source archive, and nothing about DVD code. `ffmpeg -buildconf` shows `--enable-libdvdread` and `--enable-libdvdnav` with no `--enable-libdvdcss`, and `ffmpeg.exe` holds four libdvdcss strings (`C:/Temp/av-kit/s57-plan-dvdcss-probe.txt`): BtbN's `scripts.d/50-dvd` builds libdvdcss statically and configures libdvdread with `-Dlibdvdcss=enabled` (`FFMPEG-LIBDVDCSS-BUNDLED`, `:3401`). Mat accepted shipping it (D-266) and asked for one factual line (D-275).
3. **No installer holds MEU-113 to MEU-124 or MEU-126.** RC1 was built from an earlier tree (`docs/releases/v0.1.0-rc.1-build-record.json`), and MEU-114's round trip has only run on Session 49's repackaged installer, not a full build (D-268).
4. **RC1's notes and checklist have known errors.** RC1's checklist tells the clean-machine check to look in `%LOCALAPPDATA%\av-kit\models` (`docs/releases/publish-checklist-v0.1.0-rc.1.md:134`); voice models live in `%USERPROFILE%\.avkit\models` (`MODELS-DIR-DOCS-AND-PROBE-MISMATCH`). The notes' Transcript section says the path hasn't run end to end and that the maintainer will recheck it (`docs/releases/v0.1.0-rc.1.md:48-62`), and that recheck hasn't run from another network (D-216).

The session ends when the contract's checks and Done's four lines hold, the session gate passes, and the build record, the notes, the notices line and the checklist are written and reviewed.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-08). No payload is oversized: the version edits are 13 files with exact counts, the build and checks are scripted, and the two documents are new prose read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s57-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s57\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s57-plan-2026-11-08-release-rc2` and `s57-execution-2026-11-08-release-rc2`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before each dispatch.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path, and the review-state receipt is rebuilt there (Session 49b D-290).
  - Reviewer prompts name the ledger vocabulary up front: D-460 to D-470, AC-125.1 to AC-125.24, the cited AC-72.7, AC-110.1 to AC-110.22, AC-114.5 to AC-114.9, AC-117.15 and AC-121.8, and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json` or anything under `.agent/fleet/hub`, and they write `<HOME>` for the home folder. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4).
- **Never in these rows without Mat's words:** commit, push, tag, a release created, edited or deleted, an upload, any network request except the gate's named audit traffic (D-464), a model, runtime, FFmpeg, NuGet, npm or Python package download, or an `approved` verdict authored by the implementer. Nothing uploads, publishes or writes to YouTube.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-125 `dist-release-candidate-2` | `.agent/context/handoffs/2026-11-08-release-rc2-MEU-125-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-08-release-rc2-plan-critical-review.md` and `.agent/context/handoffs/2026-11-08-release-rc2-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts, the plan-local selftests |
| WP-2 | Red (row 1) | WP-1 | shared | AC-110.9's and AC-72.7's tests on rc.2, failing |
| WP-3 | Green (row 2) | WP-2 | shared | `VERSION_ONE`, `NOTICE_LINE` |
| WP-4 | Build (row 3) | WP-3 | shared | `CLEAN_TREE`, the installer, `C:/Temp/av-kit/s57/build-record.json` |
| WP-5 | Packaged checks and round trip (rows 4 to 7) | WP-4 | shared | Smoke, probe and round-trip JSON under `C:/Temp/av-kit/s57/` |
| WP-6 | Documents (rows 8, 9) | WP-5 | shared | `docs/releases/v0.1.0-rc.2.md`, `docs/releases/publish-checklist-v0.1.0-rc.2.md` |
| WP-7 | Records (row 10) | WP-6 | shared | The committed build record, the 07 note, MEU-125's status, grouping row 57 |
| WP-8 | Closeout (H1, H2) | WP-7 | `compact_continue` | Handoff, review, reflection, Session 58's prompt |

## User Review Required

> [!IMPORTANT]
> **Six things at this gate.** D-460 to D-463 and D-468 to D-470 are autonomous and two-way, with their alternatives in §Decision Log. The gate asks Mat to accept the plan or override one of them, and also the items below. On this harness (`plan_to_exec_gate: human`), the reviewer's approval still goes to Mat, and execution starts on Mat's next message (`create-plan.md` §5c).
>
> **1. D-464: the gate's live audit and its rule.** The session gate runs `mcp-audit` in authoritative mode, as RC1's did, because the contract asks for a fresh gate and the release carries every tool. The audit makes real requests, and Mat's answer here authorizes exactly these, made by the gate's `mcp-audit` step and nowhere else (`mcp-server/scripts/audit/fixtures.ts`):
>
> | Audit step | Host | What it fetches |
> |---|---|---|
> | `download.add.a`, `.b`, `.c` | youtube.com | yt-dlp reads each video's metadata as it is added (`packages/core/src/avkit_core/services/download.py:179`): `jNQXAC9IVRw`, `dQw4w9WgXcQ` and `aqz-KE-bpKQ` |
> | `download.sabr_check` | youtube.com | yt-dlp reads `dQw4w9WgXcQ`'s metadata again, the backend's SABR probe (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:555-561`). `download.cookies_test` runs with mode `none` and makes no request (`:571`) |
> | `download.start`, `download.cancel` | youtube.com and its media hosts | `aqz-KE-bpKQ` (Big Buck Bunny) downloads until the cancel lands (`mcp-server/scripts/audit/plan.ts:912-935`); `download.reset` puts it back in the queue behind A |
> | `download.start.again` to `download.get.done` | youtube.com and its media hosts | `jNQXAC9IVRw` downloads to completion (`plan.ts:949-1001`). `dQw4w9WgXcQ`'s media is never fetched |
> | `models.download` | huggingface.co and the storage it redirects to | The smallest ONNX variant of `onnx-community/Kokoro-82M-v1.0-ONNX` at revision `1939ad2a8e416c0acfeecc08a694d14ef25f2231`, then its voice packs from the same repository (`packages/infrastructure/src/avkit_infra/tts/voices.py:83-84`, `packages/infrastructure/src/avkit_infra/model_manager/manager.py:76`, `plan.ts:584-632`) |
> | `models.download_asset.vocab` | huggingface.co | The vocabulary file from `hexgrad/Kokoro-82M` (`packages/infrastructure/src/avkit_infra/tts/assets.py:45`) |
> | `models.download_asset.spacy` | github.com and its release storage | The pinned spaCy model wheel from `explosion/spacy-models`' releases (`assets.py:77`) |
> | `transcript.add` and the transcript steps | youtube.com | Playlist `PLav47HAVZMjnA3P7yQvneyQPiVxZ6erFS`: its flat metadata, then caption requests per video until the block pauses the job |
> | `capture.capture` | none | One real screen capture into the audit's throwaway folder |
> | `audit-rule.py`'s direct proof | youtube.com | A flat metadata read of the same playlist, then a caption fetch for its first video through the product's `TranscriptAdapter` (`audit-rule.py:186-201`), made only when every other condition of the rule already holds |
>
> Every file these steps write goes under the audit's throwaway root: `mcp-server/scripts/audit/run.ts:77` points `tts.models_directory` at its `models` folder, so `%USERPROFILE%\.avkit\models` gets no model file. All are downloads or reads; nothing uploads or writes to YouTube. YouTube still blocks caption requests from this network (`YOUTUBE-CAPTIONS-IP-BLOCK`), so the audit can't pass: since MEU-116 the transcript job pauses on the block with `BLOCK_MESSAGE` and the later transcript steps are blocked. RC1's rule tolerated Session 44's compile-only shape, which MEU-116 replaced, so it would refuse that.
> - **A, the MEU-116-shaped rule (Recommended).** `audit-rule.py` (§5) tolerates exit 1 only when the root `transcript.resume` or `transcript.start` fails with the hollow reason, `BLOCK_MESSAGE` and the Paused observable, only the chain's dependents are blocked, the changed deltas are exactly REGRESSION for the seven transcript actions, the rest matches the baseline, and the direct fetch proves the block (`captionFetchBlocked`). A tolerated run is incomplete verification, not a pass: the report stays non-pass and the gate's last line is `session-gate: INCOMPLETE VERIFICATION`. Selftest 46 of 46 (`C:/Temp/av-kit/s57-plan-audit-rule-selftest.txt`).
> - **B, do nothing.** RC1's rule, unchanged. It refuses the paused shape, so the gate stops at `mcp-audit` while the block lasts, and Done's "the gate" can't be met.
> - **C, move the audit to the checklist.** The gate skips `mcp-audit` with that reason, and the checklist runs it before publishing. The session makes no live request, and the tools ship unaudited by this session.
>
> **2. D-465: the notices' source link.** The pin doesn't change, so the source archive is the same 992,681,460 bytes RC1 attached, named `av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz` (SHA-256 `953a6237…d07284`, `C:/Temp/av-kit/s57-plan-cached-inputs.txt`). AC-110.21 requires the notice to name `{ARCHIVE_NAME}.tar.xz` (`tests/unit/test_assemble_ffmpeg_source.py:602`), and `ARCHIVE_NAME` is that name (`tools/assemble_ffmpeg_source.py:41`).
> - **A, the rc.2 tag URL with the same archive under its rc.1 name (Recommended).** The notice's URL moves to `releases/tag/v0.1.0-rc.2`, and the checklist attaches the cached archive, unchanged, to the rc.2 release. Each release then carries the source for its own binaries, and nothing is reassembled.
> - **B, keep the rc.1 URL.** The notice points at RC1's release for the source. It works only while RC1 keeps its assets, which ties the rc.2 offer to D-467.
> - **C, reassemble under an rc.2 name.** `assemble_ffmpeg_source.py` with a new `ARCHIVE_NAME`. It downloads the FFmpeg and library sources again, and the bytes would differ only in name.
>
> **3. D-466: the Transcript wording (D-216's brief).** D-216 holds the notes' "your network" wording until Transcript has run from another network.
> - **Recommendation:** Mat runs Transcript from another network before row 8, and tells the session what happened. The notes then say what that run showed.
> - **Alternative:** RC1's measured block (`docs/releases/v0.1.0-rc.1.md:50-55`: the block on the test network, the direct request's error, the path not run end to end) and its "try again later or from another network" advice, plus one line saying the other-network check hasn't run, which Mat corrects before publishing. It leaves out RC1's diagnosis "YouTube is limiting your network, not your copy of av-kit" (`:56`), which is the unverified claim D-216 holds. If Mat hasn't answered by row 8, row 8 takes this, and the handoff says so.
> - **Do nothing:** RC1's wording unchanged.
>
> This session makes no YouTube request for this; the only live reads are item 1's.
>
> **4. D-467: what happens to RC1, for the checklist.** RC1 is public (D-215) with its installer and its source archive. The checklist (row 9) writes Mat's choice as commands for Mat to run after rc.2 is published. This is not legal advice: GPL section 3 ties the source offer to the binaries, so whichever option keeps RC1's installer public keeps its source archive beside it.
> - **A, keep RC1 and say it's replaced (Recommended).** The checklist saves RC1's current body (`gh release view v0.1.0-rc.1 --json body --jq .body`), puts "Replaced by v0.1.0-rc.2" on a new first line above it, and runs `gh release edit v0.1.0-rc.1 --notes-file <that file> --latest=false`. The rest of the body and the assets stay.
> - **B, turn RC1 into a draft.** It disappears from the public page with its assets; links to it stop working.
> - **C, delete RC1.** The release and its assets go, and the tag stays unless Mat deletes it too.
> - **Do nothing:** the checklist says nothing about RC1, and both releases stay up side by side.
>
> **5. Budget.** Calibrated against Session 44 `release-rc1`, the source of the copied scripts: plan 19.1M recorded over 3 rounds (29.3M real), execution 20.8M real. This session reuses its scripts and adds the round trip and two smokes on the installer's copy. Session 56's plan cost 6.14M refused plus 5.3M, and its execution 9.98M; Session 55 RULE-4 puts a probing round at about 12M. The plan loop opens with the default 10.5M. If round 1 costs more than 5.25M, the gate asks Mat for the execution loop's budget (Session 52 RULE-3); the recommendation is about 25M (one probing round, one recheck, and the round-trip evidence to read), against the 21M default.
>
> Round 1 cost 13,056,333, so the ask fired. Mat ruled on 2026-11-08 at 22:36 EST: "Add 60M to the plan loop so round 2 can run, and set execution to 60M." The plan loop's budget is now 70.5M (`C:/Temp/av-kit/s57-plan-ledger-continue.txt`), and H1-7 opens the execution loop with `--token-budget 60000000`.
>
> **6. Clean tree at the build (CLEAN_TREE, D-462).** Today the tree is clean apart from this plan. If another session leaves uncommitted files by row 3, the build stops before it deletes anything, and the coordinator asks Mat through the Human Decision Protocol: that session commits first (recommended), or Mat names the paths to leave out of the build, or do nothing and the build waits. Nothing of another session's is committed, stashed or reverted here.
>
> **What the words in Done mean here, and the limits they leave.**
> - **"Every surface" is the 13 files `version-bump.py` edits** (§Files Modified), the 7 version tests of AC-110.9 and `tests/e2e/test_api_openapi.py:110`. The archive name `av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz` keeps its rc.1 name (D-465 A); `version-bump.py --check` allows that one name and nothing else. `docs/`, `.agent/` and the plan folders keep their historical rc.1 text.
> - **"A clean tree" is `CLEAN_TREE`:** HEAD is still row 0's, and every changed or untracked path is one rows 0 to 2 own. It isn't a committed tree: the commit is Mat's, and `build-identity.py` hashes the tree as it would be committed, so H2-5's commit carries exactly the built inputs and the record proves it (`--ref HEAD` after the commit).
> - **"The packaged checks" are RC1's** (AC-110.11 to AC-110.15, AC-110.17) on `win-unpacked` and on the installed app, with RC1's negative control.
> - **"The round trip" is MEU-114's phases A to D on this installer** with RC1's installer as the old one, on this PC (AC-114.5 to AC-114.9). A clean machine is Mat's check in the checklist, as RC1's was.
> - **"The gate" is §5's fresh run.** While YouTube blocks captions, it ends `INCOMPLETE VERIFICATION` under D-464 A, and the handoff says so; it never reads as a pass.
> - **"Reviewed" is the execution review** of the two documents and the notices line. Mat reads them before publishing.
> - **Nothing here signs the installer.** RC1 was unsigned, and the notes say so again.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `VERSION_ONE` | npm, electron-builder and the MCP server read `0.1.0-rc.2`; the Python packages, `__version__`, `uv.lock` and OpenAPI read `0.1.0rc2`; the tag will be `v0.1.0-rc.2`. The only rc.1 left in the 13 surfaces is the source archive's name. |
| `NOTICE_LINE` | The FFmpeg section of `packaging/THIRD_PARTY_NOTICES.md` gains, after "as subprocesses and never links them.", the two lines "- **DVD libraries:** this build also links libdvdread and libdvdnav, and through them libdvdcss, into `ffmpeg.exe`. av-kit never uses DVD input." Its tag URL reads `v0.1.0-rc.2`. Nothing else in the file changes. |
| `CLEAN_TREE` | Before the build deletes anything, `clean-tree.py` exits 0: HEAD equals `baseline.sha`, and every changed, deleted or untracked path is the plan folder, this session's `.agent/context/handoffs/2026-11-08-release-rc2-*` files, a version surface, a Red test file or the watch-item test. A path changed before row 0 and still changed is not allowed, even an allowed one. |
| `FRESH_BUILD` | `build-rc.ps1` deletes `ui/dist`, `packaging/build` and `packaging/dist`, extracts the cached pin with its licence, freezes the real backend (never `--stub-ok`), runs `dist:prep`, the licence generator and electron-builder with `--publish never`, and refuses an installer of 500,000,000 B or more. |
| `BUILD_RECORD` | `build-identity.py --write-record --expect-inputs` stores the tree's `build_inputs`, the installer's name, size and SHA-256, the FFmpeg archive's and binaries' SHA-256 and the toolchain fields; `--verify-record` passes on the tree and installer every later check used. |
| `PACKAGED_CHECKS` | RC1's checks on `ui/dist/win-unpacked`: `smoke_packaged_rc.py` with the negative control (AC-110.3, AC-110.11, AC-110.12, AC-110.17), the MCP probe reporting `0.1.0-rc.2` (AC-110.13), and the offline TTS phase on a copy (AC-110.14). |
| `ROUNDTRIP` | `install-roundtrip.ps1` runs MEU-114's phases A to D with RC1's installer and this one, the install-root smoke and the app smoke at each new install, and checks every uninstall leaves nothing behind and the app data unchanged. |
| `ROUNDTRIP_SAFETY` | The round trip refuses before installing anything when a precondition fails (40) or the installer isn't the recorded one (41); stops only processes whose path is under its own install folder; leaves the user's app data alone; and deletes the updater cache only when it held nothing but RC1's copy before. |
| `INSTALLED_COPY` | Phase B copies the installed `resources\avkit-backend` to `C:\Temp\av-kit\s57\installed-backend\avkit-backend`, equal to the install in file count, bytes and `avkit-backend.exe`'s SHA-256; rows 6 and 7 run on that copy. |
| `CAPABILITY_SMOKE` | MEU-117's `smoke_packaged_tts.py --phase capability` on `INSTALLED_COPY` with an absent models folder; afterwards the folder holds only the smoke's own stub and `config.json`, and the refused download left it unchanged (AC-117.15). |
| `SENTENCE_SMOKE` | MEU-121's `smoke_packaged_tts.py --phase sentences` on `INSTALLED_COPY`, the fixed test set and `kokoro-onnx-int8`, 149 jobs (AC-121.8). |
| `AUDIT_RULE` | The gate's `mcp-audit` exit 1 is tolerated only by `audit-rule.py` under D-464 A, from this run's summary, and the gate then ends `INCOMPLETE VERIFICATION`. |
| `RELEASE_NOTES` | `docs/releases/v0.1.0-rc.2.md` says what this candidate fixes and what stays open, carries D-216's corrections, D-466's Transcript wording, the caption block, the libdvdcss risk and the source archive's size and SHA-256. |
| `PUBLISH_CHECKLIST` | `docs/releases/publish-checklist-v0.1.0-rc.2.md` gives Mat's outward steps in order with exact commands: commit and push, verify the record against the pushed commit, tag, draft, attach the installer and the source archive, the clean-machine check with `%USERPROFILE%\.avkit\models`, publish, then RC1 per D-467. |
| `GUARDED_STATUS_WRITE` | Row 10 and H2-2 write `meu-status.yaml`, `BUILD_PLAN.md` and `meu-registry.md` only through `status-write.py`, which holds all three from its first read to its last write and refuses any change outside MEU-125's entry and the two generated regions. |
| `NO_RAW_CONSOLE` | No product log line is added or changed. Plan-local scripts print names, counts, exit codes and SHA-256s, never file contents, tokens or process command lines; the build record holds repository-relative paths only. |
| `NOTHING_PUBLISHED` | No row tags, pushes, creates, edits or deletes a release, or uploads anything; `git tag --list v0.1.0-rc.2` is empty at H1-3 and H2-5. |

### Versions and notices: `VERSION_ONE`, `NOTICE_LINE` (D-461, D-465)

`version-bump.py` (row 2) holds, for each of the 13 files, its line break, its line count before and after, and each edit's exact old bytes, new bytes and count (`ui/package-lock.json` and `mcp-server/package-lock.json` hold the version twice each, `uv.lock` four times as `version = "0.1.0rc1"`, `openapi.committed.json` once as `"version": "0.1.0rc1"`). If any count or ending is off, it writes nothing. `--apply` replaces bytes in place and reads each write back; `--check` writes nothing and exits 0 only when every surface reads rc.2 and the archive name is the one rc.1 left. Plan-time dry run on copies under `C:/Temp/av-kit/s57/bump-dry` (`C:/Temp/av-kit/s57-plan-version-bump-dry.txt`): 13 files written, 0 problems, `--check` on the copies 0 problems; `--check` on today's tree 27 problems, exit 1; a destination outside `C:/Temp/av-kit` refused, exit 2.

`uv.lock` changes by the same bytes `uv lock` would write: on a copy, bumping the four `pyproject.toml` files alone makes `uv lock --check --offline` exit 1, and bumping them with the lock makes it exit 0 (`C:/Temp/av-kit/s57-plan-uv-lock-probe.txt`). Row 2 then runs `uv sync --frozen --offline --all-packages`, so the editable installs report rc2 without a download.

### The build: `CLEAN_TREE`, `FRESH_BUILD`, `BUILD_RECORD` (D-462)

`build-rc.ps1` and `build-identity.py` are Session 44's, with this plan's identity tool, installer name (`ui/dist/av-kit-Setup-0.1.0-rc.2.exe`) and record path (`C:/Temp/av-kit/s57/build-record.json`). The build runs offline from caches already on this PC (Session 52 RULE-2): the pinned FFmpeg zip at `C:/Temp/av-kit/ffmpeg-dl/ffmpeg-pin.zip` (194,182,300 B, SHA-256 `401dffcf…37034f`, the pin's own), Electron 42.11.18 and electron-builder 26.18.0's NSIS, winCodeSign and 7-Zip caches (`C:/Temp/av-kit/s57-plan-builder-cache.txt`), and every NuGet package the region picker restores (`dotnet restore native/region-picker -r win-x64` against an empty feed exited 0, `C:/Temp/av-kit/s57-plan-picker-offline-restore.txt`).

A cache miss is S13, not a download, and the build enforces it (round-1 F3). On a miss electron-builder would otherwise fetch the archive (`ui/node_modules/app-builder-lib/out/util/electronGet.js:498`), and NuGet, uv and npm would go to their feeds. `build-rc.ps1`'s `offline-guard` block points `HTTP_PROXY`, `HTTPS_PROXY` and `ALL_PROXY` at the dead `http://127.0.0.1:9` with `NO_PROXY` `127.0.0.1,localhost` (D-88), sets `NODE_USE_ENV_PROXY=1` so Node's fetch reads them and `ELECTRON_GET_USE_PROXY=true` for `@electron/get`, and sets `UV_OFFLINE=1`, `UV_PYTHON_DOWNLOADS=never` and `npm_config_offline=true`. electron-builder's own agent reads the proxy variables (`builder-util/out/nodeHttpExecutor.js:26-37`). `offline-probe.ps1` runs that block, from `build-rc.ps1` itself, and checks 7 cases in scratch with every target under `.invalid`, so a client that ignored the guard would fail on its own name lookup and reach nothing (`C:/Temp/av-kit/s57-plan-offline-probe.txt`, 7 of 7):

| Case | Passes when |
|---|---|
| Node's fetch | It fails with `ECONNREFUSED 127.0.0.1:9`, not `ENOTFOUND` |
| electron-builder's toolset download, an empty `ELECTRON_BUILDER_CACHE` | The same: the `@electron/get` path the Electron zip takes reaches only the dead proxy |
| NuGet, a missing package, an empty package folder | It fails `NU1301`. NuGet prints the same line without the guard (`C:/Temp/av-kit/s57-plan-nuget-unguarded.txt`), so the next case shows the proxy is read |
| .NET's `HttpClient` | It fails at `127.0.0.1:9`, not `No such host` |
| uv, a missing package, an empty cache | It fails "the network was disabled" |
| npm, a missing package | It fails `ENOTCACHED`, not `ENOTFOUND` |
| The region picker's real restore, `--force` | It exits 0 behind the guard, so the build's NuGet step needs nothing from the network |

Row 3 runs the probe before `build-rc.ps1`; a failing case stops the row before anything is deleted.

`build-rc.ps1`'s order: the offline guard, the negative control's SHA-256 (20), the starting `build_inputs` (21), the stale outputs deleted, `fetch_ffmpeg_windows.ps1 -ExtractOnly` on the copied pin (with `AVKIT_FFMPEG_URL` and `AVKIT_FFMPEG_SHA256` cleared), `package_backend.py`, `dist:prep`, the licence generator, electron-builder, the installer present (22) and under the limit (23), then `--write-record --expect-inputs`, which refuses if the tree moved during the build. Plain `npm run dist` can't be used: the generator needs the picker's fresh `.deps.json` from `dist:prep`, and electron-builder needs the generator's output.

`build_inputs` hashes the tree as it would be committed, minus `docs/`, `.agent/`, the test folders and the two smoke tools (`build-identity.py` `EXCLUDED_PREFIXES`, `EXCLUDED_FILES`), so rows 8 to 10 and the watch-item test don't move it, and any product file changed after row 3 does (S8). The gate's `build-record` step checks it again on the gate's tree.

`clean-tree.py` runs first in row 3. It reads `git diff --no-renames --name-only -z HEAD` and `git ls-files --others --exclude-standard -z`, so a rename into an allowed path still shows its source as deleted, and a path with a space is one entry. It also reads row 0's `baseline-dirty.txt` (round-1 F2): a path outside the plan folder that was already changed at row 0 and is still changed is refused even when rows 0 to 2 own it, because row 2's bump would sit on top of another session's edit (`ui/package.json` changed by another session would otherwise pass). A baseline line whose path git quoted, or a rename, is refused without being matched. It prints paths and counts only. Exit 0 clean, 1 dirty or HEAD moved, 2 unreadable, `baseline.sha` or `baseline-dirty.txt` missing included. Selftest in a scratch repository, 15 of 15 (`C:/Temp/av-kit/s57-clean-tree-selftest-r0fix.txt`; 13 of 13 at plan time, `C:/Temp/av-kit/s57-plan-clean-tree-selftest.txt`): clean; an allowed file modified with the plan folder untracked; this session's handoff untracked; another session's handoff untracked; an untracked file outside; a deleted file outside; a rename into an allowed path; a path with a space; back to allowed only; a baseline listing only the plan folder; an allowed path changed before row 0 and still changed; a baseline line git quoted; a baseline path since reverted; HEAD moved; an unreadable repository. On today's tree without `baseline.sha` it exits 2.

### Packaged checks and the round trip: `PACKAGED_CHECKS`, `ROUNDTRIP`, `INSTALLED_COPY` (D-463)

Row 4 runs RC1's checks on `win-unpacked`:

```powershell
rtk proxy uv run --frozen python tools/smoke_packaged_rc.py --install-root ui/dist/win-unpacked --negative-control C:/Temp/av-kit/rc1/negative-control/avkit-backend.exe --out C:/Temp/av-kit/s57/smoke-unpacked.json
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-08-release-rc2/packaged-probes.ps1
```

The negative control is RC1's stub backend, which bundles `phonemizer`; the smoke must report it there or it fails (`tools/smoke_packaged_rc.py:133`). `packaged-probes.ps1` runs Session 31b's MCP probe through `av-kit.exe` on an empty app-data folder and exits 30 unless the entry reports `"name":"av-kit","version":"0.1.0-rc.2"`, then the offline TTS phase on a copy at `C:/Temp/av-kit/s57/tts-run`, because the phase refuses a backend inside the checkout. Its online phase rebuilds the onedir and is never run.

Row 5's `install-roundtrip.ps1` is Session 49's with RC1's record check (41) and install-root smoke (44) back, and phase B's backend copy added:

| Phase | Steps | Proves |
|---|---|---|
| A | RC1 installs silently to `C:\Temp\av-kit\s57\install`, app smoke, RC1 uninstalls | RC1's uninstall leaves its installer copy (the negative control, AC-114.5) |
| B | The new installer installs, `smoke_packaged_rc.py` on the install, `INSTALLED_COPY`, app smoke, uninstall | The new uninstall removes the copy (AC-114.6) and leaves nothing behind (AC-114.7) |
| C | RC1 installs, then the new installer over it, app smoke, uninstall | An upgrade from RC1 (AC-114.8) |
| D | The new installer, then itself again, app smoke, uninstall | A reinstall over itself (AC-114.9) |

Each install runs `/S /D=<target>` with `/D=` last and unquoted, and reads the Uninstall key for the location. `packaged-app-smoke.mjs` (AC-110.15) launches the installed `av-kit.exe` through Playwright with a throwaway `AVKIT_APP_DATA` under `C:\Temp\av-kit\s57\roundtrip\app-data\<label>`, waits for the shell and the backend's health, and closes the app with `app.close()` under a timeout. Exits: 40 S5, 41 S8, 42 an install, 44 the root smoke or the backend copy, 45 an app smoke, 46 S6, 47 an MEU-114 check; the first failure's code is the exit code.

`ROUNDTRIP_SAFETY`, each its own AC (Session 56 RULE-3):

- **Preconditions (AC-125.12).** Before anything installs: `-OutDir` must sit under `C:\Temp\av-kit\s57`, both installers, the record and the negative control must exist, no `av-kit` process may run (a by-name check that only refuses and never stops), and neither `%LOCALAPPDATA%\Programs\av-kit` nor `Programs\av-kit-ui` may hold files (`INSTALL-FOLDER-NAME-MISMATCH`) (40). An `installed-backend` left by an earlier run isn't refused: phase B deletes it and copies the new install's backend in its place (`install-roundtrip.ps1`, the backend copy), so rows 6 and 7 never run on an older one. The new installer's SHA-256 must equal the record's (41). `-PreconditionsOnly` stops there. Plan-time receipt `C:/Temp/av-kit/s57-plan-roundtrip-preconditions.txt`, on a stand-in installer: matching record exit 0 with nothing installed; a wrong record exit 41; an `-OutDir` outside exit 40.
- **Process stops (AC-125.13).** `Stop-InstalledProcesses` stops only processes whose `.Path` starts with the install location ("Scoped to the install's own path, never by name"), and the uninstall wait looks for the uninstaller's `~nsu` copies by path. No process is stopped by name, and the avkit MCP servers, which run from the checkout, never match.
- **App data (AC-125.14).** No uninstall runs with `--delete-app-data`. `%APPDATA%\av-kit-ui` and `%LOCALAPPDATA%\av-kit` are snapshotted by entry names before and after each phase, never read, and a change is exit 46. Every app launch uses its own throwaway `AVKIT_APP_DATA`. One write outside it can't be avoided: the app smoke's Settings visit runs the models-folder writability probe on the default `%USERPROFILE%\.avkit\models` (`ui/src/renderer/src/features/settings/SettingsPage.tsx:330-333`, `ui/src/main/setup-readiness.ts:102-123`), which creates and deletes one `.write-probe-<uuid>` file in the nearest existing folder at or above it. No model file is read or written there.
- **Updater cache (AC-125.15).** `%LOCALAPPDATA%\av-kit-ui-updater` is deleted after a phase only when its pre-state was absent or held only RC1's installer copy; anything else is left and logged.

Rows 6 and 7 run MEU-117's and MEU-121's smokes on the installed copy, not the build tree's onedir (D-315, D-332):

```powershell
rtk proxy uv run --frozen python tools/smoke_packaged_tts.py --phase capability --backend-dir C:/Temp/av-kit/s57/installed-backend/avkit-backend --models-dir C:/Temp/av-kit/s57/capability-models --out C:/Temp/av-kit/s57/capability.json
rtk proxy uv run --frozen python tools/smoke_packaged_tts.py --phase sentences --backend-dir C:/Temp/av-kit/s57/installed-backend/avkit-backend --models-dir C:/Temp/av-kit/s57/smoke-models --test-set docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/test-set.json --variant kokoro-onnx-int8 --out C:/Temp/av-kit/s57/sentences.json
```

`capability-models` doesn't exist (`C:/Temp/av-kit/s57-plan-cached-inputs.txt`). The phase creates it with a 16-byte stub `kokoro-v1_0.pth` and a `config.json` (`tools/smoke_packaged_tts.py:596-600`) and checks that the refused download leaves it unchanged (`files_unchanged`, `:490-515`); row 6 then checks that it holds only those two files. (Corrected at row 6 under Mat's S16 ruling A, 2026-11-09: the plan first said the folder stays absent, which the tool never does.) `smoke-models` is a fresh copy of `C:/Temp/av-kit/s32-smoke-models` made in row 7. Both phases start the backend behind dead proxies (`_offline_env`, `tools/smoke_packaged_tts.py:292-311`, D-88), so a download attempt fails rather than reaching the network, and the sentence phase checks each WAV's payload (`:357-365`, D-343).

### The gate's audit: `AUDIT_RULE` (D-464, D-468)

`audit-rule.py` reads this run's `mcp-audit-summary.json` and the HEAD it ran on. Exit 0 tolerated, 1 refused, 2 unreadable. It tolerates the caption block only in MEU-116's shape (§User Review Required item 1, option A) and refuses Session 44's compile-only shape, any other failing action, a summary from another HEAD, and a missing or failed direct fetch. `audit-clear.ps1` runs just before `mcp-audit` and exits 0 only when the old output folder is gone; it refuses a folder outside `C:\Temp\av-kit\` (selftest 8 of 8, `C:/Temp/av-kit/s57-plan-audit-clear-selftest.txt`), so the rule never reads an earlier run's summary. The audit report stays under `C:/Temp/av-kit/s57-D6-mcp-audit/` while the gate runs, so `tested_state` doesn't move, and H1-3 copies it to `.agent/context/MCP/mcp-tool-audit-report.md`. The baseline snapshot is never refreshed here.

### The documents: `RELEASE_NOTES`, `PUBLISH_CHECKLIST` (D-466, D-467)

Row 8 writes `docs/releases/v0.1.0-rc.2.md` from RC1's sections (`docs/releases/v0.1.0-rc.1.md`: Install `:11`, What's fixed `:32`, Transcript `:48`, How this build was tested `:63`, Known problems `:108`, Licences `:158`, Report a problem `:179`):

- **What's fixed** names MEU-113 to MEU-124 and MEU-126 in a user's words, one line each, from their handoffs.
- **What stays open** names the open register issues a user can meet, `YOUTUBE-CAPTIONS-IP-BLOCK` and the TTS pill (`TTS-STATUS-PILL-BELOW-AA-CONTRAST`) among them, and says the installer is unsigned.
- **D-216's corrections:** voice models live in `%USERPROFILE%\.avkit\models`; the clean-machine, F2 and first-model checks ran on 2026-11-04 (Mat's, `docs/releases/v0.1.0-rc.1.md` as corrected in `d287c55`); Transcript per D-466.
- **How this build was tested** gives this session's checks with their results, the caption block (AC-110.16), and the gate's `INCOMPLETE VERIFICATION` if D-464 A tolerated the audit.
- **Licences** gives the libdvdcss line's substance (D-266's accepted risk), and the source archive's name, size and SHA-256 (AC-110.22).

Row 9 writes `docs/releases/publish-checklist-v0.1.0-rc.2.md` from RC1's (`docs/releases/publish-checklist-v0.1.0-rc.1.md`, sections `:10` to `:267`): where things stand; commit and push `main`; verify the build record against the pushed commit (`build-identity.py --ref origin/main --verify-record docs/releases/v0.1.0-rc.2-build-record.json`); tag; create the draft with `gh release create v0.1.0-rc.2 --draft --prerelease` and the installer and the source archive attached; the clean-machine check, which looks in `%USERPROFILE%\.avkit\models` for voice models (RC1's `:134` named `%LOCALAPPDATA%\av-kit\models`, `MODELS-DIR-DOCS-AND-PROBE-MISMATCH`); the Transcript recheck; publish; then RC1 per D-467. Every command is for Mat to run; the session runs none of them (`NOTHING_PUBLISHED`).

### Where values go (Session 50 RULE-1; D-468)

No product code changes, so no log line, stdout line or Console field is added or changed. The values this session moves are version strings, one notices line and two new documents. The plan-local scripts print file names, counts, exit codes and SHA-256s (`version-bump.py`, `clean-tree.py`, `build-identity.py`, `install-roundtrip.ps1`), never file contents, tokens or a process's command line. `packaged-probes.ps1` reads the MCP probe's JSON for the name and version only. `install-roundtrip.ps1`'s snapshots hold entry names, never contents, and its `Log` writes the home folder as `<HOME>` in its plain, JSON-escaped and forward-slash forms (round-1 F5; `C:/Temp/av-kit/s57-plan-home-mask-check.txt`), so the updater and roaming-folder lines name no home path. The build record holds repository-relative paths (`installer.path` is `ui/dist/…`; RC1's committed record holds no home path), so committing it at row 10 publishes no home folder. The audit's summary and report stay under `C:/Temp/av-kit` until H1-3, which copies the report, as RC1's was. Session 53 RULE-1, Session 54 RULE-1 and RULE-2, and Session 55 RULE-3 have no target: no field carries outside text into the product, no `packages/core/src` file changes, no real stack is built outside `wiring.py`, and nothing fans out.

### Spec text (D3)

| File | Lines | Change |
|---|---|---|
| `docs/build-plan/07-distribution.md` | after `:386`, before `---` (`:388`) | A `> **Delivered (Session 57).**` note: the mechanism ids, the installer's size and SHA-256, the build record path, each check's result with its receipt, the gate's last line, D-464 to D-467 as Mat answered them, and this plan folder |

Row 10 re-reads the anchor before it writes (Session 51 RULE-3). `07-distribution.md` is CRLF, 468 lines.

### MEU-125 `dist-release-candidate-2`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| npm and MCP versions | `ui/package.json`, `mcp-server/package.json`, their locks, `mcp-server/src/index.ts:20` | `0.1.0-rc.2` | No other field changes |
| Python and OpenAPI versions | four `pyproject.toml`, `avkit_api/__init__.py`, `uv.lock`, `openapi.committed.json` | `0.1.0rc2` | `uv.lock` changes only in the four workspace members' `version` lines |
| FFmpeg notice | `packaging/THIRD_PARTY_NOTICES.md` | `NOTICE_LINE`; the pin facts of AC-110.21 unchanged | 224 to 226 CRLF lines |
| FFmpeg pin | `tools/fetch_ffmpeg_windows.ps1:8-9` | `n8.1.3-27-g8dca1586f4`, `autobuild-2026-10-31-12-59`, SHA-256 `401dffcf…` | Unchanged (S2) |
| Installer | electron-builder `ui/electron-builder.yml` | NSIS x64, `av-kit-Setup-0.1.0-rc.2.exe`, under 500,000,000 B | `--publish never` |
| Build record | `build-identity.py` | `s44.build-record.v1` | Repository-relative paths only |
| Release documents | `docs/releases/` | New files only | RC1's documents unchanged |

#### Acceptance Criteria

Pytest names in rows 1 and 2 are the existing tests of AC-110.9, AC-72.7 and AC-110.21; no test file is added. The rest are the scripted checks of rows 3 to 10 and the gate, each with its receipt.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-125.1 | unit | AC-110.9's seven version tests (`tests/unit/test_release_packaging.py:159`, `:169`, `:176`, `:186`, `:194`, `:206`, `:212`) pass with `RC_NPM = "0.1.0-rc.2"` and `RC_PY = "0.1.0rc2"`, and `tests/e2e/test_api_openapi.py:110` passes | Human-approved: triage batching, 07 `:379`; Local Canon: AC-110.9 | Yes: Red, all seven fail on rc.1 |
| AC-125.2 | unit | AC-72.7's FFmpeg needles hold the rc.2 tag URL, `"libdvdcss"` and `"av-kit never uses DVD input"`, and still the rc.1 archive name | Human-approved: D-275, 07 `:384`; D-465 | Yes: Red, the three new needles fail |
| AC-125.3 | unit, guard | AC-110.20 and AC-110.21 pass unchanged: the notice states the pin as one fact (build, `BUILD_TAG`, `FFMPEG_COMMIT`, `{ARCHIVE_NAME}.tar.xz`), and the fetch tool's pinned URL and SHA-256 are unchanged | Human-approved: D-266, 07 `:381` | Guard: passes in Red and Green |
| AC-125.4 | static | `version-bump.py --check` exits 0, `uv lock --check --offline` exits 0 and `export_openapi.py --check openapi.committed.json` exits 0 | Local Canon: AC-110.9's OpenAPI half; Session 52 RULE-2 | Yes: `--check` on today's tree, 27 problems, exit 1 |
| AC-125.5 | plan-local script | `CLEAN_TREE`: `clean-tree.py` exits 0 at row 3 before the build deletes anything; its selftest's 15 cases pass | Human-approved: Mat's brief ("from a clean tree; another session's files are an HDP"); 07 `:382` | Yes: the selftest's dirty, deleted, rename, space, baseline-carried, quoted-baseline and HEAD-moved cases exit 1 |
| AC-125.6 | build | `FRESH_BUILD`: `build-rc.ps1` exits 0 with the real backend, from deleted outputs, and the installer is under 500,000,000 B (AC-110.10) | Local Canon: 07 §Release candidate packaging, AC-110.10 | Yes: exits 20 on a wrong negative control, 23 at the limit |
| AC-125.7 | build | `BUILD_RECORD`: the record is written with `--expect-inputs`, `--verify-record` passes at row 3 and in the gate, and the `build-identity.py` selftest passes (AC-110.19) | Local Canon: AC-110.19; S8 | Yes: the selftest's mismatch cases; the round trip's 41 on a wrong record |
| AC-125.8 | packaged | `smoke_packaged_rc.py` passes on `win-unpacked` with the negative control (AC-110.3, AC-110.11, AC-110.12, AC-110.17), and AC-110.1 to AC-110.8 and AC-110.18 pass in the gate's Python suite | Local Canon: `LICENCE_LIST`, AC-110.1 to AC-110.18 | Yes: the smoke fails unless it finds `phonemizer` in the negative control |
| AC-125.9 | packaged | The MCP probe through `av-kit.exe` reports `"name":"av-kit","version":"0.1.0-rc.2"` (AC-110.13) | Local Canon: AC-110.13 | Yes: exit 30 on any other version |
| AC-125.10 | packaged | The offline TTS phase passes on a copy of `win-unpacked`'s backend behind dead proxies (AC-110.14) | Local Canon: AC-110.14; D-88 | Its own negative probe |
| AC-125.11 | packaged | `ROUNDTRIP`: `install-roundtrip.ps1` exits 0 through phases A to D (AC-114.5 to AC-114.9), with the install-root smoke and the app smoke (AC-110.15) passing at each new install | Human-approved: 07 `:382`; Local Canon: D-268, AC-114.5 to AC-114.9 | Yes: phase A, RC1's uninstall leaves its copy |
| AC-125.12 | plan-local script | `ROUNDTRIP_SAFETY` preconditions: exit 40 for an `-OutDir` outside `C:\Temp\av-kit\s57`, a missing input, a running `av-kit` or files in either default install folder; exit 41 when the installer isn't the record's; `-PreconditionsOnly` installs nothing | Human-approved: Mat's brief (stop conditions before any install); Session 56 RULE-3 | Yes: the plan-time receipt's 41 and 40 |
| AC-125.13 | plan-local script | `ROUNDTRIP_SAFETY` process stops: only processes whose path is under the install location are stopped, and none by name | Human-approved: Mat's brief ("stop only recorded process ids, never by name"); memory rule on worktree-scoped kills | Read at plan time and in review: `Stop-InstalledProcesses` filters by `.Path` |
| AC-125.14 | plan-local script | `ROUNDTRIP_SAFETY` app data: no `--delete-app-data`; `%APPDATA%\av-kit-ui` and `%LOCALAPPDATA%\av-kit` keep the same entry names across every phase; launches use throwaway `AVKIT_APP_DATA` | Local Canon: AC-114.7; D-268 | Yes: exit 46 on a change |
| AC-125.15 | plan-local script | `ROUNDTRIP_SAFETY` updater cache: `%LOCALAPPDATA%\av-kit-ui-updater` is deleted only when it was absent or held only RC1's copy before the phase | Local Canon: Session 49's round trip | Logged and left otherwise |
| AC-125.16 | packaged | `INSTALLED_COPY`: the copy equals the install in file count, total bytes and `avkit-backend.exe`'s SHA-256 | Local Canon: D-315, D-332 | Yes: exit 44 on a difference |
| AC-125.17 | packaged | `CAPABILITY_SMOKE` passes on `INSTALLED_COPY` from an absent models folder, which afterwards holds only the smoke's stub and `config.json`, with `files_unchanged` true (AC-117.15) | Human-approved: 07 `:382`; Local Canon: AC-117.15 | Its own checks: the 409 and the unchanged folder |
| AC-125.18 | packaged | `SENTENCE_SMOKE` passes all 149 jobs on `INSTALLED_COPY` (AC-121.8) | Human-approved: 07 `:382`; Local Canon: AC-121.8 | AC-121.7's FP16 Red, already recorded |
| AC-125.19 | gate | The session gate's last line is `session-gate: all steps exit 0`, or `session-gate: INCOMPLETE VERIFICATION` only by `AUDIT_RULE`; `audit-rule.py` (46 of 46) and `audit-clear.ps1` (8 of 8) selftests pass | Human-approved: D-464; Local Canon: 07 `:382` ("a fresh gate") | Yes: the rule's selftest refusals |
| AC-125.20 | document | `RELEASE_NOTES` holds each part of §The documents, the archive's size and SHA-256 (AC-110.22) and the caption block (AC-110.16), and no home path | Human-approved: D-216, D-466, 07 `:383` | Review |
| AC-125.21 | document | `PUBLISH_CHECKLIST` holds the steps of §The documents in order with exact commands, attaches the source archive, checks `%USERPROFILE%\.avkit\models` and writes D-467's choice for RC1 | Human-approved: D-266, D-101, D-467, 07 `:385`; RC1 plan D-238 | Review; `grep` finds no `%LOCALAPPDATA%\av-kit\models` |
| AC-125.22 | plan-local script | `GUARDED_STATUS_WRITE` for row 10 and H2-2: a write before the hold is kept, one during it fails in the writer, a change outside MEU-125's entry and the regions is refused with nothing written, and `--verify` catches a later stale save | Local Canon: Session 56 AC-126.10; Session 55 RULE-2 | Yes: the selftest's control, in which the unguarded tool loses an interleaved write |
| AC-125.23 | static | `NO_RAW_CONSOLE`: no file under `packages/`, `ui/src/` or `mcp-server/src/` changes except `mcp-server/src/index.ts:20`'s version, and no new committed file holds the home folder (`grep -n "Users\\\\"` on the documents and the record finds nothing) | Local Canon: Session 50 RULE-1 | The scope-paths step refuses any other product path |
| AC-125.24 | static | `NOTHING_PUBLISHED`: `git tag --list v0.1.0-rc.2` prints nothing at H1-3 and H2-5, and no row's command tags, pushes or runs `gh release` | Local Canon: PROFILE E5; 07 `:386` | The scope check and the review |

Guards that run unchanged in row 2 (Session 55 RULE-1; every reader of the notices or the version, `grep` at plan time): `tests/unit/test_release_packaging.py`, `tests/unit/test_packaging_installer.py`, `tests/unit/test_assemble_ffmpeg_source.py`, `tests/unit/test_generate_third_party_licenses.py` and `tests/e2e/test_api_openapi.py`. The MCP server has no test that reads its version; AC-125.9 reads it from the built entry. The whole Python, UI and MCP suites run in the session gate.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| The version strings and the tag | Human-approved | 07 `:379` |
| The contents, MEU-113 to MEU-124 and MEU-126 | Human-approved | 07 `:380`; all 13 are `approved` |
| The FFmpeg pin and libdvdcss shipping | Human-approved | D-266; 07 `:381` |
| The notice line's words | Human-approved, wording inferred | D-275 asks for one factual line; the wording states the build fact (`C:/Temp/av-kit/s57-plan-dvdcss-probe.txt`) and is reviewed |
| The notices' source URL | Human decision at this gate | D-465 |
| What "clean tree" means at the build | Inferred, flagged | D-462: `CLEAN_TREE` |
| The round trip on the full build | Human-approved | 07 `:382`; D-268; D-463 for the additions |
| The two smokes on the installer's copy | Human-approved | 07 `:382`; D-315, D-332 |
| The gate's audit and its rule | Human decision at this gate | D-464 |
| The Transcript wording | Human decision, at this gate and row 8 | D-466 (D-216's brief) |
| RC1's fate in the checklist | Human decision at this gate | D-467 |
| The models path in the checklist | Local Canon | `MODELS-DIR-DOCS-AND-PROBE-MISMATCH`; 07 `:385` |
| Nothing publishes | Local Canon | 07 `:386`; PROFILE E5 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `tests/unit/test_release_packaging.py` | Modify | Row 1: `RC_NPM`, `RC_PY` (`:27-28`) |
| `tests/unit/test_packaging_installer.py` | Modify | Row 1: AC-72.7's needles (`:222-233`): the URL to rc.2, `"libdvdcss"`, `"av-kit never uses DVD input"` |
| `ui/package.json`, `ui/package-lock.json` | Modify | `VERSION_ONE` (1 and 2 occurrences) |
| `mcp-server/package.json`, `mcp-server/package-lock.json`, `mcp-server/src/index.ts` | Modify | `VERSION_ONE` (1, 2 and 1) |
| `pyproject.toml`, `packages/api/pyproject.toml`, `packages/core/pyproject.toml`, `packages/infrastructure/pyproject.toml`, `packages/api/src/avkit_api/__init__.py` | Modify | `VERSION_ONE` (1 each) |
| `uv.lock`, `openapi.committed.json` | Modify | `VERSION_ONE` (4 and 1) |
| `packaging/THIRD_PARTY_NOTICES.md` | Modify | `NOTICE_LINE` and the tag URL |
| `docs/releases/v0.1.0-rc.2.md` | New | `RELEASE_NOTES` |
| `docs/releases/publish-checklist-v0.1.0-rc.2.md` | New | `PUBLISH_CHECKLIST` |
| `docs/releases/v0.1.0-rc.2-build-record.json` | New | Row 10: a byte copy of `C:/Temp/av-kit/s57/build-record.json` |
| `docs/build-plan/07-distribution.md` | Modify | §Spec text |
| `ui/tests/e2e/transcript-queue.test.ts` | Modify, only if the watch item fails twice | D-470 |

No test id is added, so `ui/tests/e2e/test-ids.ts` and its byte-hash tests aren't touched (S12). Line endings (`C:/Temp/av-kit/s57-plan-line-endings.txt`; the version surfaces in `version-bump.py` `EDITS`): CRLF are `ui/package.json` (71), `ui/package-lock.json` (11,338), `mcp-server/package.json` (26), `mcp-server/package-lock.json` (2,896), `mcp-server/src/index.ts` (35), `packages/infrastructure/pyproject.toml` (30), `openapi.committed.json` (6,516), `THIRD_PARTY_NOTICES.md` (224), `test_packaging_installer.py` (368), `07-distribution.md` (468), the grouping file (322), `current-focus.md` and `metrics.md`. LF are the other three `pyproject.toml`, `__init__.py`, `uv.lock` (3,361), `test_release_packaging.py` (212), the register, its render and `meu-status.yaml`. Each row measures with Python bytes before it writes and writes by byte replacement or with `newline=""`, then checks the counts. New files are LF.

### Project files

- `docs/execution/plans/2026-11-08-release-rc2/`: `implementation-plan.md`, `task.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `red-check.py`, `identity.py`, `version-bump.py`, `clean-tree.py`, `offline-probe.ps1`, `build-rc.ps1`, `build-identity.py`, `packaged-probes.ps1`, `install-roundtrip.ps1`, `packaged-app-smoke.mjs`, `audit-rule.py`, `audit-clear.ps1`, `status-write.py` and `session-gate.ps1`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, and the grouping tracker row 57 (`.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:260`).
- `.agent/context/known-issues.yaml` and its render `known-issues.md`, only if the watch item fails twice (D-470).
- `.agent/context/handoffs/2026-11-08-release-rc2-*.md`, `docs/execution/reflections/2026-11-08-release-rc2-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`, `.agent/context/MCP/mcp-tool-audit-report.md`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Tagging, the draft, the upload, publishing, RC1's edit | Outward step | None; Mat's, by the checklist | 07 `:386`; PROFILE E5 |
| A clean-machine run and the Transcript recheck from another network | Human check | None; the checklist | D-216; RC1's checklist §6, §7 |
| Code signing | Distribution | None | RC1 shipped unsigned; not asked |
| A new FFmpeg pin or a build without libdvdcss | Packaging | None | D-266 |
| Renaming the source archive | Packaging | None, unless Mat picks D-465 C | D-465 |
| `MEU-127` `svc-tts-fp16-phase-guard` | Product | MEU-127 | 07 `:380` names MEU-113 to MEU-124 and MEU-126 |
| Fixing `INSTALL-FOLDER-NAME-MISMATCH` | Neighbouring issue | Its own placement | The round trip only refuses files in both folders |
| Refreshing the audit baseline snapshot | Audit | None | §5: the baseline stays |

## BUILD_PLAN.md Audit

MEU-125 is at `.agent/context/meu-status.yaml:3266`, status `pending`. Plan time: 132 MEUs, 118 approved and 1 closed, 13 pending (`C:/Temp/av-kit/s57/meu-stats.txt`). Row 10 sets `ready_for_review` and H2-2 sets `approved`, each with `status-write.py` (`GUARDED_STATUS_WRITE`, D-469), Session 56's script with `--row MEU-125`. No other session holds uncommitted lines in the three files today, but `tools/meu_status.py update` and `render` load and save whole files without a lock, so the guard stays: it holds the three files through Windows handles from its first read to its last write, runs the tool's own update and render on staged copies, refuses any change outside MEU-125's entry and the two generated regions, keeps the bytes it read under `--keep`, and writes the diff to `--diff-out`. `--verify MEU-125=STATUS` runs at H1-3 and before H2-5. Plan-time selftest, 9 cases (`C:/Temp/av-kit/s57-plan-status-write-selftest.txt`), including the positive control in which the unguarded tool loses an interleaved write, and a run on copies of today's files that changes only MEU-125's row and the regions. The render check also runs at row 10 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s57-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s57-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` is Session 56's without the matrix steps, with this session's selftests:

1. Creates `C:\Temp\av-kit\s57\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256.
2. Runs `uv sync --frozen --offline --all-packages`, so this step can't fetch a package (plan-time dry run: `C:/Temp/av-kit/s57-plan-uv-offline-dry-run.txt`, 122 packages, no changes), and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason. It asserts the pinned FFmpeg pair under `packaging/ffmpeg-win64/` exists and is over 1024 B; a missing pair is S4, not a fetch.
3. Captures the base Python suite to `s57-base-py.txt`, the base UI suite to `s57-base-ui.txt` and the base MCP suite to `s57-base-mcp.txt`, with `TMP` and `TEMP` at `C:\Temp\av-kit\s57\tmp`.
4. Runs the `red-check.py`, `identity.py`, `build-identity.py`, `audit-rule.py`, `audit-clear.ps1` and `status-write.py` selftests. `clean-tree.py --selftest` runs in row 3 before the check itself.

The plan-local copies:

- **`red-check.py`** is Session 56's. `DECLARED_NEW` holds no name of this session's, because the Reds edit existing constants and needles, and keeps the selftest fixtures' names (`C:/Temp/av-kit/s57-plan-red-check-selftest.txt`, 0 wrong). Row 1 requires the eight pytest names by `--require`: AC-110.9's seven (`test_npm_manifests_carry_version`, `test_npm_locks_carry_version`, `test_mcp_server_reports_version`, `test_python_manifests_carry_version`, `test_api_package_carries_version`, `test_uv_lock_carries_version`, `test_openapi_carries_version`) and `test_ac_72_7_third_party_notices`. A title matches only up to a non-digit or non-word boundary, and every failure it counts must be an assertion.
- **`identity.py`** is Session 56's with `PLAN` set to this folder and `NAMED_DISTRIBUTIONS` empty. It still binds the pinned FFmpeg pair. `PROJECT_ARTIFACTS` are this plan's `*.md`, the handoff, review and reflection files, `docs/execution/metrics.md`, `.agent/context/current-focus.md` and `.agent/context/MCP/mcp-tool-audit-report.md`, which are written after the gate (`C:/Temp/av-kit/s57-plan-identity-selftest.txt`, 0 failures).
- **`build-identity.py`** is Session 44's with this record schema (`C:/Temp/av-kit/s57-plan-build-identity-selftest.txt`).

### 2. Red, then Green (rows 1 and 2)

- **No type-only row (D-461).** No row adds a name, so Session 53 RULE-2 and Session 52 RULE-4 have no target.
- **Row 1's Red** edits only `RC_NPM` and `RC_PY` and AC-72.7's needle tuple, then runs `test_release_packaging.py` and `test_packaging_installer.py::test_ac_72_7_third_party_notices`. `red-check.py` reads the receipt and requires AC-110.9's seven tests and AC-72.7 to fail by assertion, never by collection or import.
- **Row 2's Green** runs `version-bump.py --apply`, then `uv lock --check --offline`, `uv sync --frozen --offline --all-packages`, the five guard files of §Acceptance Criteria, `export_openapi.py --check openapi.committed.json` and `version-bump.py --check`.
- **Expectations stay immutable in Green.** No test file changes in row 2.

### 3. The build (row 3)

`clean-tree.py --selftest`, then `clean-tree.py` (S10), then `offline-probe.ps1` (S13), then `build-rc.ps1`, then `build-identity.py --verify-record C:/Temp/av-kit/s57/build-record.json`. A clean-tree exit 1 stops before `build-rc.ps1` deletes anything. Any product file changed after this row reruns rows 3 to 7 (S8).

### 4. Packaged checks (rows 4 to 7)

§Packaged checks and the round trip. Row 5 runs `install-roundtrip.ps1 -PreconditionsOnly` first, then the full run:

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-08-release-rc2/install-roundtrip.ps1 -NewInstaller ui/dist/av-kit-Setup-0.1.0-rc.2.exe -OldInstaller C:/Temp/av-kit/rc2/rc1-installer.exe -OutDir C:\Temp\av-kit\s57\roundtrip -BuildRecord C:/Temp/av-kit/s57/build-record.json
```

RC1's installer is the cached copy (340,348,020 B, SHA-256 `beabc509…09768a7`, RC1's record). Rows 6 and 7 need row 5's `INSTALLED_COPY`, which outlives the uninstall.

### 5. Session gate (H1-2)

`session-gate.ps1` is RC1's gate with this plan's scope, receipts and audit rule and Session 56's baseline rule. It writes one receipt per step in `C:/Temp/av-kit`, named `s57-D6-<step>`. It is fail-fast and prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1, clears `ELECTRON_RUN_AS_NODE` and sets `RECEIPTS_DIR`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, `scope-paths` (§Files Modified and §Project files, plus `baseline-dirty.txt`; `ui/tests/e2e/test-ids.ts` refused; HEAD must not move), and the `red-check.py`, `build-identity.py`, `audit-rule.py` and `audit-clear.ps1` selftests |
| Fresh full | `py-tests`, `ui-tests`, `mcp-build`, `mcp-tests`, `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi`, `state-render`, `issues-render`, `build-record` (`--verify-record` on the gate's tree) |
| Runtime | `ui-electron` (the whole Electron suite, because the release carries every page), `mcp-audit-clear`, then `mcp-audit` in authoritative mode with the named traffic of D-464 |
| Identity | `identity-npm`, `identity-after` |

- **`py-tests` keeps Session 49b's baseline rule:** exit 1 passes only when every FAILED id also FAILED in row 0's `s57-base-py.txt` and nothing ERRORs. `ui-tests` and `mcp-tests` excuse nothing.
- **"mcp-audit now runs"**, last, because it uses real YouTube traffic and the real screen. Exit 0 passes. Exit 1 continues only through `AUDIT_RULE`, and "a tolerated run is incomplete verification, not a pass": the last line is then `session-gate: INCOMPLETE VERIFICATION`. "The rule reads only this run's summary", which `mcp-audit-clear` guarantees, and "the baseline stays". The report is copied at H1-3.
- **The watch item (D-470).** `ui-electron` runs `ui/tests/e2e/transcript-queue.test.ts:177` (W2-4). If the gate stops there, it is rerun once unchanged and both runs' receipts are kept (Session 53 RULE-4). If W2-4 fails again, the fix (wait for the first load to settle before `page.reload()`) lands before the release, in `transcript-queue.test.ts` only, the register's `resolution_path` and `verification` record it, and the gate runs again. The test folder is outside `build_inputs`, so the build doesn't rerun. If it passes, the handoff records that it passed.
- **A step that fails in a file this session didn't touch** is rerun once unchanged, with both receipts kept.

### Plan-local scripts

- `baseline.ps1`, `red-check.py`, `identity.py`, `build-identity.py`: §1.
- `version-bump.py` (row 2): §Versions and notices.
- `clean-tree.py`, `offline-probe.ps1`, `build-rc.ps1` (row 3): §The build.
- `packaged-probes.ps1` (row 4), `install-roundtrip.ps1` and `packaged-app-smoke.mjs` (row 5): §Packaged checks and the round trip.
- `audit-rule.py`, `audit-clear.ps1`, `session-gate.ps1` (H1-2): §The gate's audit and §5.
- `status-write.py` (row 10 and H2-2): §BUILD_PLAN.md Audit.

Each `.ps1` written from Python takes raw-string paths and was checked for control characters (Session 56 RULE-1; `C:/Temp/av-kit/s57-plan-line-endings.txt`). Each selftest sets its own fixture state (Session 56 RULE-4).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | The FFmpeg pin, its cached zip's SHA-256 or `ARCHIVE_NAME` differs from this plan's | Stop: a re-pin or a new archive needs Mat's words |
| S3 | `HEAD` moves from `baseline.sha` other than by the commits `ruled-commits.txt` names (Mat's S3 ruling A, 2026-11-09), or a path outside this plan's scope appears | Stop and tell Mat; never commit, stash or revert another session's work |
| S4 | The pinned FFmpeg pair is missing or under 1024 B, or a GPL-incompatible or unowned licence class appears (AC-110.18) | Stop: a fetch is a download, and a licence change needs Mat |
| S5 | `install-roundtrip.ps1` exits 40 | Nothing was installed. Name the precondition to Mat; never stop a process or clear a folder to make it pass |
| S6 | An uninstall leaves something behind or changes the app data (46), or an MEU-114 check fails (47) | Stop and tell Mat; the release waits |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | `--verify-record` fails, the round trip exits 41, or a product file changes after row 3 | Rerun rows 3 to 7 on the changed tree before the gate |
| S9 | `audit-rule.py` refuses (1) or can't read the summary (2) | The gate fails; stop and tell Mat with the rule's receipt |
| S10 | `clean-tree.py` exits 1 at row 3 | Stop before the build deletes anything; HDP for Mat (§User Review Required item 6) |
| S11 | W2-4 fails twice (D-470) | Land the fix in `transcript-queue.test.ts`, record it in the register, and rerun the gate |
| S12 | A row finds it must edit `ui/tests/e2e/test-ids.ts` | Stop, add ids in an additive block at the end, and run AC-51.6 and AC-81.13 in that row's own check |
| S13 | A step needs a download: a cache miss in Electron, electron-builder, NuGet, npm or uv, or a model | Stop: a download needs Mat's words |
| S14 | Any network request outside the gate's named audit traffic, any upload, tag, push or release change, or any write to YouTube | Stop and tell Mat |
| S15 | `status-write.py` refuses, or `--verify` fails | Nothing was written. Rerun once and keep both receipts; a second refusal or any `--verify` failure stops and tells Mat |
| S16 | A packaged smoke or probe fails (rows 4, 6, 7) | Stop; a product fix is a new decision for Mat, and any fix reruns rows 3 to 7 |

## Decision Log

> [!WARNING]
> Mat's brief and the triage batching settle the scope, and grouping D-243 makes MEU-125 the last session of the batch. D-460 to D-463 and D-468 to D-470 didn't need Mat: each is autonomous with its alternatives in `reasoning`. D-464 to D-467 were open at this gate. Mat accepted every recommendation on 2026-11-09 ("all recommendations accpeted proceed"), and the block records them with those words as `human_message_reference`. D-466's recommendation needs Mat's other-network Transcript run; if no result has arrived by row 8, row 8 takes the alternative and the handoff says so.
>
> Carried and not relisted in the block: every grouping §8 row, D-240 to D-250, D-267, D-277 and D-280, with stage `grouping`; D-243 is among them. The register holds D-214, D-215, D-266 and D-275 under `FFMPEG-LIBDVDCSS-BUNDLED` and D-216 and D-222 under `MODELS-DIR-DOCS-AND-PROBE-MISMATCH` (stage `triage`), and D-362 under `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` (stage `execution`). This plan cites them in prose only, so no id carries a second stage. The probe (`C:/Temp/av-kit/s57-decision-issue-probe.txt`), run with this plan as a source (Session 54 RULE-5), shows what the closeout's flags pull in. With `--decision-issue` naming those three issues, it reads 28 ids and refuses none. With no `--decision-issue`, it refuses the register. H2-2 passes the three issues, one flag each.

```yaml
decision_log:
  - id: D-460
    stage: planning
    question: "In what order do the rows run?"
    resolution: autonomous
    class: two-way
    chosen: "Row 0 baseline; row 1 the version and notices Red; row 2 the Green; row 3 the clean-tree check, the build and the record; row 4 the checks on win-unpacked; row 5 the round trip with the installed copy; rows 6 and 7 the capability and sentence smokes on that copy; row 8 the notes; row 9 the checklist; row 10 the records and grouping row 57; then H1 and H2"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-03-release-rc1/task.md: RC1's rows", "docs/build-plan/07-distribution.md:382: the build and gate rule", "Session 53 RULE-2: a type-only row exists for a shared missing name"]
    research: { engine: none, sources: [] }
    reasoning: "The build needs the versions first, and every check needs the one recorded installer, so the build sits between the Green and the checks. The smokes on the installed copy follow the round trip that makes it. The notes follow the checks so they report results, and the records come last so a failed check leaves nothing to undo. No row adds a name, so there is no type-only row. Writing the documents first would put unmeasured results in them."
  - id: D-461
    stage: planning
    question: "How do the version surfaces and the notices move, and what proves it?"
    resolution: autonomous
    class: two-way
    chosen: "VERSION_ONE and NOTICE_LINE: Red first on AC-110.9's constants and AC-72.7's needles, then version-bump.py --apply with exact counts and endings for 13 files, uv lock --check --offline and uv sync --frozen --offline, and version-bump.py --check, which allows only the archive's rc.1 name"
    source_tag: Local Canon
    precedents: ["tests/unit/test_release_packaging.py:27-28, :159-212: AC-110.9", "tests/unit/test_packaging_installer.py:222-233: AC-72.7", "C:/Temp/av-kit/s57-plan-version-bump-dry.txt", "C:/Temp/av-kit/s57-plan-uv-lock-probe.txt"]
    research: { engine: none, sources: [] }
    reasoning: "The tests already pin every surface, so moving their constants is the Red, and the scripted bump with exact counts can't miss or double an occurrence or change a line ending. Running uv lock would rewrite the lock through the resolver, which may want the network; the probe shows the byte edit is what uv lock --check accepts offline. Editing by hand risks a missed surface that only the packaged probe would catch."
  - id: D-462
    stage: planning
    question: "How is the installer built and tied to the tree, and what is a clean tree?"
    resolution: autonomous
    class: two-way
    chosen: "Session 44's build-rc.ps1 and build-identity.py with this plan's names; CLEAN_TREE by clean-tree.py before anything is deleted, which allows only rows 0 to 2's paths and refuses a baseline-dirty path; the record verified at row 3, by the round trip (41) and in the gate; any product change after row 3 reruns rows 3 to 7 (S8)"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md:279-291: RC1's build", "Mat's Session 57 brief: another session's uncommitted files at the build row are an HDP", "C:/Temp/av-kit/s57-plan-clean-tree-selftest.txt"]
    research: { engine: none, sources: [] }
    reasoning: "RC1's scripts proved the order and the record, so copying them keeps that proof. The tree can't be committed before the build, because the commit is Mat's, so the record hashes the tree as it would be committed and the checklist re-verifies it against the pushed commit. clean-tree.py makes the brief's rule a check rather than a reading of git status. Allowing baseline-dirty paths, as the gate does, would let another session's file into the installer."
  - id: D-463
    stage: planning
    question: "What does the round trip add to Session 49's for the full build?"
    resolution: autonomous
    class: two-way
    chosen: "RC1's record check (41) and install-root smoke (44) back, phase B's INSTALLED_COPY for rows 6 and 7, both default install folders in the precondition, and ROUNDTRIP_SAFETY's four properties as AC-125.12 to AC-125.15"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-04-rc2-fetch-uninstall/implementation-plan.md:191-195: AC-114.5 to AC-114.9", "Local Canon D-268: MEU-114's round trip on the full build", "D-315, D-332: the smokes on the installer's copy", "Session 56 RULE-3: each safety property its own AC", "known issue INSTALL-FOLDER-NAME-MISMATCH"]
    research: { engine: none, sources: [] }
    reasoning: "Session 49 ran on a repackaged installer, so it dropped the record and the root smoke; on the full build both apply again. The installer's own backend is what users get, so the smokes run on a copy of it rather than the build tree's onedir. The installer really uses Programs\\av-kit-ui, so the precondition checks both folders. Running the smokes on win-unpacked would test a tree the installer may not reproduce."
  - id: D-468
    stage: planning
    question: "Which checks does the session gate run, and where do values go?"
    resolution: autonomous
    class: two-way
    chosen: "RC1's gate: identity, static with the plan-local selftests, the full Python, UI and MCP suites with Session 49b's baseline rule, the builds, OpenAPI, the renders and the build record, the whole Electron suite, then mcp-audit under AUDIT_RULE; no product log line changes, scripts print names, counts and SHA-256s, and the committed record holds relative paths only"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md:302-321: RC1's gate", "Session 50 RULE-1"]
    research: { engine: none, sources: [] }
    reasoning: "The release carries every page and tool, so the gate runs every suite and the audit rather than a targeted subset. The build record step proves the gate's tree is the built one. Session 56 skipped the audit because nothing it changed reached a tool; this session ships them all."
  - id: D-469
    stage: planning
    question: "How do row 10 and H2-2 write MEU-125's status?"
    resolution: autonomous
    class: governance-value
    chosen: "GUARDED_STATUS_WRITE: Session 56's status-write.py with --row MEU-125, --keep and --diff-out, and --verify at H1-3 and before H2-5"
    source_tag: Local Canon
    precedents: ["Session 56 D-454 and AC-126.10", "C:/Temp/av-kit/s57-plan-status-write-selftest.txt"]
    research: { engine: none, sources: [] }
    reasoning: "No other session holds lines in the three files today, but one may start, and the status tool saves whole files without a lock. The guard costs one script that already passed its selftest. Calling the tool directly would be simpler and would lose a parallel write silently."
  - id: D-470
    stage: planning
    question: "How does the session handle the watch item E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE?"
    resolution: autonomous
    class: two-way
    chosen: "W2-4 runs in the gate's ui-electron step. A failure is rerun once unchanged with both receipts kept; a second failure lands the fix (wait for the first load to settle before page.reload()) in transcript-queue.test.ts before the release, records it in the register and reruns the gate; a pass is recorded in the handoff"
    source_tag: Human-approved
    precedents: [".agent/context/known-issues.yaml:4237: the issue and its resolution_path", "Session 53 RULE-4", "Mat's Session 57 brief"]
    research: { engine: none, sources: [] }
    reasoning: "The brief and the register give the rule; this plan only places it in the gate. The test folder is outside build_inputs, so the fix doesn't rerun the build. Fixing it now without a recurrence would change a passing test on one data point."
  - id: D-464
    stage: planning
    question: "How does the session gate treat the live mcp-audit while YouTube blocks captions, and which live requests does it make?"
    resolution: human
    class: governance-value
    chosen: "A: the MEU-116-shaped AUDIT_RULE; the gate's mcp-audit step makes exactly the requests in §User Review Required item 1's table, a tolerated run is INCOMPLETE VERIFICATION and never a pass"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md:308-310, :396-397: RC1's D-186 audit rule", "docs/execution/reflections/2026-11-03-release-rc1-reflection.md:235, :294: RC1 accepted an INCOMPLETE VERIFICATION gate", "known issue YOUTUBE-CAPTIONS-IP-BLOCK"]
    research: { engine: native, sources: ["https://developer.harness.io/docs/continuous-integration/use-ci/run-tests/test-management/ci-test-quarantine — a temporarily down external service justifies quarantine; a test failing every run does not", "https://oneuptime.com/blog/post/2026-07-28-quarantine-flaky-tests/view — quarantined checks keep running, with an owner, a reinstatement rule and the release manager told", "https://docs.trunk.io/flaky-tests/quarantine-service-availability — when the tolerance can't be decided, failures count as failures"] }
    reasoning: "A audits every tool on the shipped build and tolerates one proven failure shape only, refusing any other delta. B, RC1's rule, refuses MEU-116's paused shape, so the gate can't finish while the block lasts. C ships the tools unaudited by this session and moves the same failure to Mat's checklist."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'all recommendations accpeted proceed' (in reply to the Decision Briefs for D-464 to D-467)"
  - id: D-465
    stage: planning
    question: "Where do the notices point for the FFmpeg source, and under what name?"
    resolution: human
    class: two-way
    chosen: "A: the notice links releases/tag/v0.1.0-rc.2, and the checklist attaches the cached archive unchanged, keeping its name av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz"
    source_tag: Human-approved
    precedents: ["known-issues.yaml:2195: D-101, keep GPL and publish the complete source with the release", "docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md:414: D-202, one archive beside the installer", "docs/releases/publish-checklist-v0.1.0-rc.1.md:100-115, :236: RC1 attached the archive and checked its SHA-256", "known-issues.yaml:3449, :3468: GPL-3.0 section 6(d)"]
    research: { engine: native, sources: ["https://f.sfconservancy.org/Copyleft/guide/commit/a5079818d48715fe4aef512f930be756071cb4be — 6(d): equivalent access to the source in the same way through the same place", "https://lists.gnu.org/r/emacs-devel/2016-08/msg00409.html — FSF FAQ: a site that happens to hold the source today isn't enough", "https://sprintlaw.com.au/articles/gplv3-object-code-matching-source-handover/ — tie the binary and the source to the same release"] }
    reasoning: "A puts each release's source beside its own binaries and reassembles nothing, keeping the SHA-256 RC1 published. B ties rc.2's offer to RC1 keeping its assets, which D-467 B or C would break. C re-downloads about 990 MB for bytes that differ only in name."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'all recommendations accpeted proceed' (in reply to the Decision Briefs for D-464 to D-467)"
  - id: D-466
    stage: planning
    question: "What do the release notes say about Transcript while the other-network check is open (D-216)?"
    resolution: human
    class: externally-blocked
    chosen: "Recommendation: Mat runs Transcript from another network before row 8 and reports the result, and the notes say what it showed; if no result has arrived by row 8, row 8 writes the alternative (RC1's measured block and retry advice, one line that the check hasn't run, without RC1's 'not your copy of av-kit' diagnosis) and the handoff says so"
    source_tag: Human-approved
    precedents: ["known-issues.yaml:3625-3630: D-216, the 'your network' wording waits for the other-network check", ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:241: Session 57 settles that wording", "docs/releases/v0.1.0-rc.1.md:50-57: RC1's block and diagnosis"]
    research: { engine: native, sources: ["https://pypi.org/project/youtube_transcript_api — YouTube blocks most cloud-provider IPs (RequestBlocked or IpBlocked)", "https://transcriptapi.com/blog/youtube-transcript-api-not-working — RequestBlocked is broader than an IP block, so it doesn't prove the cause", "https://community.latenode.com/t/django-app-youtube-transcript-extraction-fails-on-cloud-hosting-but-works-locally/23360 — an apparent network block was SSL or DNS"] }
    reasoning: "A run from another network settles D-216 with evidence. The alternative keeps every sentence measured and drops the unproven cause. Doing nothing ships the cause claim D-216 held back."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'all recommendations accpeted proceed' (in reply to the Decision Briefs for D-464 to D-467)"
  - id: D-467
    stage: planning
    question: "What does the checklist do with RC1 after rc.2 is published?"
    resolution: human
    class: one-way-door
    chosen: "A: keep RC1 with its assets; save its body with gh release view v0.1.0-rc.1 --json body --jq .body, put 'Replaced by v0.1.0-rc.2' on a new first line, and run gh release edit v0.1.0-rc.1 --notes-file that-file --latest=false"
    source_tag: Human-approved
    precedents: ["docs/execution/reflections/2026-11-06-tts-load-fp16-reflection.md:74: D-215, RC1 stays up and its fate on replacement is Mat's call in MEU-125's checklist", "docs/execution/reflections/2026-11-03-release-rc1-reflection.md:131: D-238, RC1 stays up until a new build replaces it", "known-issues.yaml:3469: a very small audience, and rc.2 supersedes it"]
    research: { engine: native, sources: ["https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository — notes and the pre-release and latest flags can be edited after publishing", "https://cli.github.com/manual/gh_release_edit — --latest is a boolean flag; gh 2.98.0's help shows the =false form for --draft", "https://www.scivision.dev/github-delete-release-tag/ — deleting a release leaves its tag"] }
    reasoning: "A is reversible and keeps RC1's installer beside its source and its links working; RC1 is a prerelease, so --latest=false is redundant and harmless. A draft breaks the links until republished, and deleting can't be undone and leaves the tag. Doing nothing leaves RC1 with no sign it was replaced."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'all recommendations accpeted proceed' (in reply to the Decision Briefs for D-464 to D-467)"
```

## Research References

- `docs/build-plan/07-distribution.md:371-386` (the residual contract) and §Release candidate packaging (residual), MEU-110's rules.
- RC1's plan, task and scripts (`docs/execution/plans/2026-11-03-release-rc1/`: build `:279-291`, smoke `:292-297`, gate `:302-321`), its notes and checklist (`docs/releases/v0.1.0-rc.1.md`, `docs/releases/publish-checklist-v0.1.0-rc.1.md`) and its build record.
- Session 49's round trip (`docs/execution/plans/2026-11-04-rc2-fetch-uninstall/`, AC-114.5 to AC-114.9 at `:191-195`).
- MEU-117's and MEU-121's plans (`docs/execution/plans/2026-11-06-tts-build-capability/`, AC-117.15 `:253`; `docs/execution/plans/2026-11-06-tts-load-fp16/`, AC-121.8 `:377`).
- Session 56's plan and scripts (`docs/execution/plans/2026-11-08-light-accent-contrast/`), the structure this plan follows.
- `.agent/context/known-issues.yaml`: `FFMPEG-LIBDVDCSS-BUNDLED` `:3401`, `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` `:4237`, `MODELS-DIR-DOCS-AND-PROBE-MISMATCH` `:3597`, `YOUTUBE-CAPTIONS-IP-BLOCK` `:2931`, `INSTALL-FOLDER-NAME-MISMATCH` `:3933`, D-216 `:3625`.
- The grouping file §6 row 57 (`:260`) and §8 (D-243).

## Planning receipts

- `C:/Temp/av-kit/s57-plan-tree.txt`: the tree at plan time, the worktree list and the highest decision ids in use.
- `C:/Temp/av-kit/s57-plan-line-endings.txt`: every plan-local script's endings and control characters.
- `C:/Temp/av-kit/s57-plan-cached-inputs.txt`: RC1's installer, the source archive, the pinned zip, the negative control, the smoke models and the FFmpeg pair, with sizes and SHA-256s; the capability models folder absent; 0 missing.
- `C:/Temp/av-kit/s57-plan-builder-cache.txt` and `s57-plan-picker-offline-restore.txt` (Session 52 RULE-2): the Electron, electron-builder and NuGet caches the build needs.
- `C:/Temp/av-kit/s57-plan-uv-offline-dry-run.txt` and `s57-plan-uv-lock-probe.txt`: `uv sync --frozen --offline` needs nothing; the lock edit is what `uv lock --check --offline` accepts.
- `C:/Temp/av-kit/s57-plan-dvdcss-probe.txt`: the libdvdcss strings in `ffmpeg.exe` (`NOTICE_LINE`).
- `C:/Temp/av-kit/s57-plan-version-bump-dry.txt`: `version-bump.py` on copies; the work tree untouched.
- `C:/Temp/av-kit/s57-plan-clean-tree-selftest.txt`: 13 of 13. At execution start the coordinator added this session's handoff prefix, which the canonical plan review needs (`identity.py` and `session-gate.ps1` already used it), and two cases: `C:/Temp/av-kit/s57-clean-tree-selftest-r0fix.txt`, 15 of 15. At row 3 the check refused 9 untracked paths of the capture-crop-copy session (MEU-130), all under `docs/` or `.agent/` (`C:/Temp/av-kit/s57-clean-tree.txt`), and Mat ruled S10 option B on 2026-11-09 ("B"): leave those 9 paths out. The coordinator added a repeatable `--leave-out PATH`, which refuses a path `build-identity.py`'s `in_identity` counts as a build input, and four cases (`C:/Temp/av-kit/s57-clean-tree-selftest.txt`, 19 of 19); the ruled check passed with the 9 paths named (`C:/Temp/av-kit/s57-clean-tree-b.txt`). The first build then stopped at S13 (`C:/Temp/av-kit/s57/build-attempt1-s13.txt`): with the Electron 42.11.18 zip cached, `@electron/get` still fetches `SHASUMS256.txt` on every build (`ui/node_modules/app-builder-lib/out/util/electronGet.js:627-634`), a case `offline-probe.ps1` didn't cover. The zip's SHA-256 matched `ui/node_modules/electron/checksums.json` (`C:/Temp/av-kit/s57-electron-sums-check.txt`), and Mat ruled S13 option A on 2026-11-09 ("A"): the coordinator wrote `%LOCALAPPDATA%\electron\Cache\SHASUMS256.txt-42.11.18` from that file (`C:/Temp/av-kit/s57-electron-sums-seed.txt`), which electron-builder reads so the check runs offline, and reran row 3 with the guard unchanged.
- S3 after row 7 (2026-11-09): HEAD moved from `baseline.sha` `8bcb4a6` to `8ce8b95` through Mat's two commits `cbc6e22` (`.agent/context/current-focus.md`) and `8ce8b95` (the capture-crop-copy plan, including the 9 paths S10 left out), both docs-only. The build record still matched the tree (`C:/Temp/av-kit/s57-head-moved-verify.txt`), so rows 3 to 7 stand. Mat ruled option A ("Accept the commits"): `baseline.sha` stays row 0's record, `ruled-commits.txt` names the two commits, and the gate's `scope-paths` step accepts a moved HEAD only when `baseline.sha` is an ancestor, every commit since it is ruled, and each ruled commit touches only `docs/` or `.agent/` paths outside this plan's prefixes; anything else is still S3. Test of the edited step on the live tree, 3 cases (accepted; a list missing one commit refused; a ruled commit with a wider path refused): `C:/Temp/av-kit/s57-scope-ruled-test.txt`.
- `C:/Temp/av-kit/s57-plan-offline-probe.txt`: `offline-probe.ps1` with build-rc.ps1's guard, 7 of 7; `s57-plan-nuget-unguarded.txt`: the same NuGet case without it.
- `C:/Temp/av-kit/s57-plan-home-mask-check.txt`: `install-roundtrip.ps1`'s Log writes `<HOME>` for the home folder in all three spellings.
- `C:/Temp/av-kit/s57-plan-ps-parse.txt`: every plan-local `.ps1` parses with 0 errors.
- `C:/Temp/av-kit/s57-plan-roundtrip-preconditions.txt`: the round trip's precondition and record refusals on a stand-in installer.
- `C:/Temp/av-kit/s57-plan-red-check-selftest.txt`, `s57-plan-identity-selftest.txt`, `s57-plan-build-identity-selftest.txt`, `s57-plan-audit-rule-selftest.txt`, `s57-plan-audit-clear-selftest.txt` and `s57-plan-status-write-selftest.txt`.
- `C:/Temp/av-kit/s57/meu-stats.txt`.
- `C:/Temp/av-kit/s57-decision-issue-probe.txt`: the closeout flags with this plan as a source.
- `C:/Temp/av-kit/s57-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`.
- Step 4A GUI check (`gui-refs-not-shipped`): no page, control or text in the app changes; only the version string the app reports.
- Not run at plan time: any suite, the build, a packaged check, the round trip or the audit. Row 0 runs the suites.

## Validation stage contract

- **Static:** `pyright packages/`, `ruff`, the UI and MCP typechecks and the UI lint, `lint_task_contract.py`, the scope-paths check and the plan-local selftests.
- **Targeted:** each row's own checks, with `red-check.py` reading row 1's receipt, and every reader of the version and the notices in row 2.
- **Fresh full:** the whole Python, UI and MCP suites, the UI and MCP builds, the OpenAPI guard, the two render checks and the build record, in the session gate.
- **Runtime:** the fresh build, the packaged checks on `win-unpacked`, the round trip, the two smokes on the installed copy, the whole Electron suite and the authoritative MCP audit.
- **Human:** Mat's answers at this gate (D-464 to D-467) and, if Mat chooses, the other-network Transcript run before row 8.
- **Plan-local scripts:** the selftests in row 0 and the gate, `clean-tree.py` in row 3, and `status-write.py --verify` at H1-3 and before H2-5.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime; `build-identity.py` binds the installer to the tree. The gate records both, and H1-6b checks the handoff's evidence against them.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
