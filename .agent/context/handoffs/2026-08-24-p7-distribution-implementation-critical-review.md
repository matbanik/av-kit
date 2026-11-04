---
date: 2026-08-24
review_mode: implementation
target_plan: docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md
verdict: approved
findings_count: 0
round: 2
template_version: 2.1
requested_verbosity: standard
agent: gpt-5.6-sol
---

# Critical Review: p7-distribution Implementation

> **Review Mode**: `implementation`
> **Verdict**: `changes_required`

## Intent Anchor

Session 12 was supposed to deliver MEU-24 and MEU-25 as a usable Windows distribution surface: a localhost-only PyInstaller onedir backend and an NSIS installer carrying the resources-root backend, FFmpeg/ffprobe, and MCP payloads. The approved plan permits a blocked live PyInstaller run and defers clean-VM install/launch, but it does not permit non-executable payloads to be represented as completed integration ACs or an unpinned FFmpeg download to be accepted.

---

## Findings

| # | Finding | Severity | Confidence | File:Line | Recommendation | Status |
|---|---------|----------|------------|-----------|----------------|--------|
| F1 | **AC-24.10 and the installed runtime payload are false-green.** The MEU-24 AC table marks the packaged smoke `✅`, while its evidence says no live PyInstaller COLLECT ran and only an `MZ` layout stub exists. The MEU-25 AC table likewise marks the NSIS integration `✅` while admitting that both FFmpeg files are `MZ` stubs. Independent file-state evidence found the source backend, `ffmpeg.exe`, and `ffprobe.exe` are each 2 bytes (the stub writer emits exactly `b"MZ"`), and the actual `ui/dist/win-unpacked/resources/` copies are also 2 bytes. Directly starting all three fails with “not a valid application for this OS platform.” This is not the separately deferred clean-VM check: it is a local, deterministic failure of the packaged executables and violates AC-24.10's run/READY observable and the distribution intent. | High | High | `tools/package_backend.py:25-31`; `.agent/context/handoffs/2026-08-24-p7-distribution-MEU-24-handoff.md:44,60,79`; `.agent/context/handoffs/2026-08-24-p7-distribution-MEU-25-handoff.md:44,62`; `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:205`; `docs/build-plan/07-distribution.md:7-9,22-30,155-165` | Build a real PyInstaller onedir and smoke `PACK_DIST_EXE` with `SPAWN_FLAGS` through descriptor + `AVKIT_READY`; fetch real FFmpeg/ffprobe; rebuild NSIS and re-run the local payload probes. Until then, record AC-24.10/the live run as `[B]` with the required external-error receipt instead of `✅`. Keep `CLEAN_VM` as its separate later `[B]`. | open |
| F2 | **`FETCH_FFMPEG` is not SHA256-pinned and fail-opens.** Its default SHA is empty, and comparison executes only when the supplied hash is nonblank. An independent temp-only probe passed an arbitrary ZIP containing text files named `ffmpeg.exe` and `ffprobe.exe` with `-Sha256 ""`; the script printed `PASS: FETCH_FFMPEG`. The installer test only asserts that the script exists, so it cannot catch this contract failure. This violates the approved plan's locked “URL + SHA256 pin” rule and can admit tampered or wrong release content into the installer. | High | High | `tools/fetch_ffmpeg_windows.ps1:1-7,24-27,33-43`; `tests/unit/test_packaging_installer.py:91-108`; `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:77,112,236,265`; `.agent/context/handoffs/2026-08-24-p7-distribution-MEU-25-handoff.md:62` | Commit a nonempty 64-hex SHA256 for the selected immutable archive; reject blank/malformed hashes before download or extraction; always compare before copying binaries. Add negative tests for blank SHA, mismatch, and malformed/non-executable payloads. | open |

No Critical findings were identified. Both High findings are behavioral/contract failures and independently satisfy the Materiality Gate for `changes_required`.

---

## Scope

**Target**: `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md`

**Review Type**: multi-handoff implementation review, Round 1

**Correlation rationale**: the explicit plan slug/date and plan `Handoff Set` bind exactly the two named MEU handoffs. Scope remained locked to Session 12 (`MEU-24` + `MEU-25`); Session 8c and Phase 8 were not reviewed or started.

**Reviewed artifacts**:

- Plan, task table, named sets, Phase 7 distribution spec, and MEU-24/MEU-25 SSOT entries.
- Both correlated MEU handoffs.
- All user-named packaging code/config/docs, all five test files, and all three assertion scripts.
- Current `packaging/dist`, `packaging/ffmpeg-win64`, `ui/dist`, and `ui/dist/win-unpacked/resources` file state because the workspace may not be a git repository.

**Scope exclusions honored**: no FastAPI router/MCP tool rewrite was required; conceptual `extra/` diagram text was not treated as the runtime path; Settings/Help and chrome were not rewound; no MEU IDs were invented.

---

## Commands Executed

| Command / probe | Result | Receipt |
|---|---|---|
| Registered packaging pytest (`test_packaging_backend.py`, `test_packaging_installer.py`, `test_ffmpeg_bundle_wire.py`) | PASS — 20 passed | `C:/Temp/av-kit/p7-exec-r1-pytest-packaging.txt` |
| Scoped Vitest (`dev-spawn.test.ts`, `copy-mcp-config.test.ts`, `--allowOnly=false`) | PASS — 4 passed | `C:/Temp/av-kit/p7-exec-r1-vitest.txt` |
| `assert-nsis-pack.ps1 -BuildReceipt C:/Temp/av-kit/nsis-build.txt` | PASS — at least one artifact exists and all measured executables are below 524288000 bytes | `C:/Temp/av-kit/p7-exec-r1-nsis-pack.txt` |
| OpenAPI `export_openapi.py --check` | PASS — no drift | `C:/Temp/av-kit/p7-exec-r1-openapi.txt` |
| MEU-24 / MEU-25 red oracles | PASS — 10 mapped failing AC titles each | `C:/Temp/av-kit/p7-exec-r1-red-oracle-24.txt`; `C:/Temp/av-kit/p7-exec-r1-red-oracle-25.txt` |
| Handoff marker assertion + independent AC-set comparison | PASS — 2 handoffs; all 10 AC IDs per handoff present | `C:/Temp/av-kit/p7-exec-r1-handoff-markers.txt`; `C:/Temp/av-kit/p7-exec-r1-ac-coverage.txt` |
| Pyright on `packages/` | PASS — 0 errors | `C:/Temp/av-kit/p7-exec-r1-pyright.txt` |
| UI TypeScript and ESLint checks | PASS | `C:/Temp/av-kit/p7-exec-r1-tsc.txt`; `C:/Temp/av-kit/p7-exec-r1-eslint.txt` |
| Ruff on scoped Python/spec/tests | FAIL — two E501 lines in new MEU-25 tests; non-material by itself | `C:/Temp/av-kit/p7-exec-r1-ruff.txt` |
| Artifact size/hash inventory | FAIL contract — backend + ffmpeg + ffprobe source payloads are each 2 bytes | `C:/Temp/av-kit/p7-exec-r1-artifact-probe.txt`; `C:/Temp/av-kit/p7-exec-r1-dist-exes.txt` |
| Direct backend/FFmpeg/ffprobe execution | FAIL — all three are invalid Windows applications | `C:/Temp/av-kit/p7-exec-r1-payload-exec.txt` |
| Blank-SHA arbitrary archive probe against `fetch_ffmpeg_windows.ps1` | FAIL contract — script exited 0 and printed PASS | `C:/Temp/av-kit/p7-exec-r1-ffmpeg-unpinned-bypass.txt` |
| SSOT inspection | PASS — MEU-24 and MEU-25 are `ready_for_review` and bound to the exact plan | `C:/Temp/av-kit/p7-exec-r1-ssot-711-762.txt` |
| Review frontmatter/table structure parse | PASS | `C:/Temp/av-kit/p7-exec-r1-review-structure.txt` |
| `check_exec_review.py` closeout check | Expected FAIL — this tool accepts only `approved`; it reported the present `changes_required` verdict, so H1-7 correctly remains open | `C:/Temp/av-kit/p7-exec-r1-review-check.txt` |

The NSIS receipt is fresh relative to the installer artifact. Its successful build does not cure F1: `win-unpacked/resources` proves electron-builder copied the two-byte payloads into the distribution.

---

## Checklist Results

### Implementation Review (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 Live runtime evidence | fail | No real packaged-backend run exists; direct local execution of the packaged payload fails. NSIS build/size is not launch evidence. |
| IR-2 Stub behavioral compliance | fail | The layout stubs preserve names/directories only; they cannot start the backend or FFmpeg. |
| IR-3 Error mapping completeness | n/a | FastAPI routers were explicitly out of scope and remained untouched. |
| IR-4 Fix generalization | n/a | Round 1; no prior execution-review correction to generalize. |
| IR-5 Test rigor audit | fail | Two scoped files are 🔴 and allowed the concrete payload defects to pass; per-file grades below. |
| IR-6 Boundary validation coverage | fail | `FETCH_FFMPEG` accepts blank SHA256 and arbitrary archive content. Other scoped path/config boundaries match the approved contract. |
| IR-7 Deferral and AC coverage integrity | fail | All AC IDs appear in the matching handoffs, but AC-24.10 is integration-typed and marked `✅` despite only a stub/unit oracle; AC-25.10 proves build/size while the packaged runtime payload is invalid. The separately deferred clean-VM check was not treated as AC-25.10. |

### IR-5 Per-File Test Rigor Grades

| Test file | Grade | Evidence |
|---|---|---|
| `tests/unit/test_packaging_backend.py` | 🔴 Weak | AC-24.8 checks only the prefix constant; AC-24.10 accepts the two-byte stub based on file/directory existence and never runs the exe. |
| `tests/unit/test_packaging_installer.py` | 🔴 Weak | Predominantly phrase scans; AC-25.10 checks script text/existence rather than running the pack check or validating installed payloads; fetch coverage checks only `fetch.is_file()`. |
| `tests/unit/test_ffmpeg_bundle_wire.py` | 🟡 Adequate | Exact frozen sibling and PATH precedence are asserted, but production wiring is verified by source-string inspection and dummy `MZ` files, not adapter construction/binary behavior. |
| `ui/tests/unit/dev-spawn.test.ts` | 🟢 Strong | Exact resources-root path plus `extra/` negative and READY port behavior are asserted. |
| `ui/tests/unit/copy-mcp-config.test.ts` | 🟢 Strong | Exercises real IPC output and asserts token/app-data inclusion plus `AVKIT_API_BASE` omission. |

### Adversarial Verification (AV)

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 Failing-then-passing proof | pass | Both red oracles independently revalidated 10 AC titles. |
| AV-2 No bypass hacks | pass | No skips/only/early-return bypasses observed in the named tests. |
| AV-3 Changed paths exercised by assertions | fail | Packaged executable behavior and the FFmpeg SHA gate are not meaningfully asserted. |
| AV-4 No skipped/xfail masking | pass | No scoped skip/xfail masking found. |
| AV-5 No unresolved placeholders | fail | The built delivery payload intentionally contains layout stubs; they are not functional deliverables. |
| AV-6 Source-backed criteria | fail | The source-backed nonempty SHA pin and functional distribution intent are not satisfied. |

### Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | fail | Both integration AC rows are `✅`, but their evidence/current artifacts prove stubbed runtime payloads. |
| DR-2 Residual old terms | pass | No runtime `extra/avkit-backend`, onefile, `0.0.0.0`, or production `AVKIT_FFMPEG_BUNDLE` regression was found. |
| DR-3 Downstream references updated | pass | MCP snippet/default copy and resources-root paths are consistent. |
| DR-4 Verification robustness | fail | Existing checks allow F1 and F2 to pass green. |
| DR-5 Evidence auditability | pass | Registered receipts and artifact state were reproducible. |
| DR-6 Cross-reference integrity | fail | Build-plan “backend + bundled FFmpeg” delivery claims do not match the current executable payloads. |
| DR-7 Evidence freshness | partial | NSIS receipt/artifact are fresh; the handoff's 221943296-byte “artifact” number is the recursively measured `win-unpacked/av-kit.exe`, while the top-level NSIS is 101348502 bytes. Both remain below the cap; this size-label drift is Low/non-blocking. |
| DR-8 Completion vs residual risk | fail | Handoff prose acknowledges the blocked/stub state while its AC tables still mark integration completion. |

---

## Open Questions / Assumptions

- The workspace was reviewed from current file state rather than git diff, as directed.
- Absence of a clean Windows VM is accepted as the plan's separate later `[B]`; neither finding requires a VM.
- The registered NSIS check's under-cap result is accepted. Its recursive maximum is not treated as the top-level installer's exact size.
- The two scoped Ruff E501 failures are a non-blocking quality note under the user-specified Materiality Gate; they should still be corrected with the substantive work.

---

## Follow-up Actions

1. Route corrections through `/execution-corrections`; do not patch within this review.
2. Replace the two-byte backend stub with a real PyInstaller COLLECT onedir and capture the AC-24.10 spawn/descriptor/READY receipt, or mark the run validly `[B]` with an external-error receipt.
3. Make the FFmpeg fetch SHA mandatory, fetch real `ffmpeg.exe`/`ffprobe.exe`, prove `-version`, and rebuild NSIS.
4. Strengthen the two 🔴 test files so the observed stub and blank-SHA cases fail.
5. Re-run packaging pytest, Vitest, Ruff, Pyright, TSC/ESLint, OpenAPI, NSIS pack, direct payload probes, and this rolling execution review.

---

## Verdict

`changes_required` — the structural/path contracts and registered unit gates are largely correct, but the built distribution currently carries non-executable backend and FFmpeg payloads and the FFmpeg fetch path accepts unpinned content. These are High runtime/distribution-contract failures, not clerical or clean-VM-only gaps.

## Residual Risk

After F1/F2 are corrected, clean-Windows install/launch, dependency health, upgrade persistence, and full shipped MCP smoke remain the plan's later environment evidence. That residual risk is acceptable only as the already-declared separate `[B]`; it must not be used to represent locally invalid payloads as complete.

---

## Corrections Applied (2026-08-24) — after Round 1 F1/F2

**Findings resolved by implementer**: 2/2 pending independent recheck

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F1 | Two-byte stub payloads marked complete | Real PyInstaller COLLECT (`excludes` torch); lazy torch import so API boots; READY smoke `AVKIT_READY port=58252`; real BtbN FFmpeg/ffprobe; NSIS rebuilt | `C:/Temp/av-kit/pack-smoke.txt`; `ffmpeg-version.txt`; `nsis-size-run.txt` `PASS: SIZE_CAP bytes=288524010`; installed exe sizes backend 46468963 / ffmpeg 144441856 / ffprobe 144236032 |
| F2 | Blank SHA256 fail-open | Script requires 64-hex SHA; always compares; refuses stub bins; default pin `5EFB8182…BDAB`; tests reject blank + mismatch | `pytest-p7-corrections.txt` 22 passed; `ffmpeg-extract.txt` |

Ruff E501 on MEU-25 tests also wrapped. AC-24.9 now asserts `torch` is in Analysis `excludes` and absent from `hiddenimports`.

---

## Round 2 Recheck (2026-08-24)

### Intent Anchor

This recheck independently verifies that the Windows distribution now contains functional backend and FFmpeg payloads, preserves the packaged READY/descriptor contract, produces an under-cap NSIS artifact, and rejects unpinned FFmpeg input before extraction. The current file state and fresh Round 2 probes achieve that intent; the separate clean-VM install/launch evidence remains outside AC-24.10 and AC-25.10 as locked by the approved plan.

### Findings First

No findings. F1 and F2 are independently reproduced as fixed, and no new evidence-backed High or Critical behavioral, contract, test-rigor, persistence, security, or false-claim defect was found. `findings_count` is `0`.

### Prior Finding Closure

| Finding | Recheck result | Evidence |
|---|---|---|
| F1 — two-byte stub payloads marked complete | ✅ Closed | Both source and installed backend executables are 46,468,963-byte AMD64 PE32+ files with identical SHA256 `3D5691FC07310CA28C78D8A101FDD84D8B3100D2753605AAEE6DD4A19394DA87` (`C:/Temp/av-kit/p7-exec-r2-pe-probe.txt`). The smoke receipt independently parses to `AVKIT_READY port=58252` with `descriptor_ok=True` (`p7-exec-r2-pack-smoke-check.txt`). Vendor and installed FFmpeg/ffprobe all run `-version` and exit 0 (`p7-exec-r2-ffmpeg-version.txt`). The NSIS assertion passes at 288,524,010 bytes under the 524,288,000-byte cap (`p7-exec-r2-nsis-pack.txt`). AC-24.10 and AC-25.10 may remain ✅ (`2026-08-24-p7-distribution-MEU-24-handoff.md:44`; `2026-08-24-p7-distribution-MEU-25-handoff.md:44`). |
| F2 — blank SHA256 fail-open | ✅ Closed | `FETCH_FFMPEG` carries the required 64-hex default pin and rejects any non-64-hex value before creating the output directory or touching an archive (`tools/fetch_ffmpeg_windows.ps1:7,15-19`). A direct blank-SHA probe exited 1, emitted no PASS marker, and left no output directory (`C:/Temp/av-kit/p7-exec-r2-blank-sha-probe.txt`). The required blank and mismatch tests both passed in the 22-test registered gate (`tests/unit/test_packaging_installer.py:136,156`; `p7-exec-r2-pytest.txt`). |

### Commands Executed

| Command / probe | Result | Receipt |
|---|---|---|
| Registered packaging pytest: backend, installer, FFmpeg bundle wire | PASS — 22 passed, including both required F2 negative tests | `C:/Temp/av-kit/p7-exec-r2-pytest.txt` |
| Registered scoped Vitest: dev spawn + MCP copy, `--allowOnly=false` | PASS — 2 files, 4 tests | `C:/Temp/av-kit/p7-exec-r2-vitest.txt` |
| Registered `assert-nsis-pack.ps1 -BuildReceipt C:/Temp/av-kit/nsis-build.txt` | PASS — `SIZE_CAP bytes=288524010` | `C:/Temp/av-kit/p7-exec-r2-nsis-pack.txt` |
| Registered OpenAPI `export_openapi.py --check` | PASS — exit 0, no drift output | `C:/Temp/av-kit/p7-exec-r2-openapi.txt` |
| .NET PE-header parse + size/hash of source and installed backend | PASS — both AMD64 PE32+, 46,468,963 bytes, identical SHA256 | `C:/Temp/av-kit/p7-exec-r2-pe-probe.txt` |
| Parse `C:/Temp/av-kit/pack-smoke.txt` for READY and descriptor marker | PASS — port 58252 (> 0), `descriptor_ok=True` | `C:/Temp/av-kit/p7-exec-r2-pack-smoke-check.txt` |
| Vendor and installed `ffmpeg.exe` / `ffprobe.exe -version` | PASS — all four exit 0 | `C:/Temp/av-kit/p7-exec-r2-ffmpeg-version.txt` |
| Direct blank-SHA pre-extraction probe | PASS — child exit 1, no PASS marker, no output directory | `C:/Temp/av-kit/p7-exec-r2-blank-sha-probe.txt` |

### Checklist Results

#### Implementation Review (IR)

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass | Packaged backend smoke reports READY on port 58252 and `descriptor_ok`; all four FFmpeg/ffprobe payloads run. |
| IR-2 Stub behavioral compliance | pass | The reviewed distribution no longer carries the two-byte stubs: both backend copies parse as PE32+, and FFmpeg/ffprobe execute successfully. |
| IR-3 Error mapping completeness | n/a | FastAPI route error mapping was outside this distribution correction scope. |
| IR-4 Fix generalization | pass | F1 was checked at both vendor/source and installed locations; F2 was checked for blank and mismatched SHA paths. |
| IR-5 Test rigor audit | pass | `test_packaging_backend.py` 🟡 Adequate; `test_packaging_installer.py` 🟢 Strong for F1/F2 negatives and 🟡 elsewhere; `test_ffmpeg_bundle_wire.py` 🟡 Adequate; `dev-spawn.test.ts` 🟢 Strong; `copy-mcp-config.test.ts` 🟢 Strong. No scoped test is 🔴 Weak for the corrected failures. |
| IR-6 Boundary validation coverage | pass | SHA validation is unconditional, runs before output-directory/archive work, and is behaviorally tested for blank and mismatch cases. |
| IR-7 Deferral and AC coverage integrity | pass | AC-24.10 has real packaged smoke evidence; AC-25.10 has a real local installer artifact under the cap. Clean-VM install/launch remains the separately declared later `[B]`. |

#### Documentation Review (DR)

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | pass | Current executable sizes, PE headers, runtime output, SHA behavior, and installer size reproduce the correction claims. |
| DR-2 Residual old terms | n/a | No terminology migration was part of this recheck. |
| DR-3 Downstream references updated | pass | Both AC integration rows cite the corrected current receipts and may remain ✅. |
| DR-4 Verification robustness | pass | Fresh probes exercise executable parsing/running and direct negative SHA behavior beyond phrase scans. |
| DR-5 Evidence auditability | pass | Every registered gate and focused probe has a fresh `C:/Temp/av-kit/p7-exec-r2-*` receipt. |
| DR-6 Cross-reference integrity | pass | Handoff integration claims now agree with current source and installed payload state. |
| DR-7 Evidence freshness | pass | All registered gates and focused probes were rerun in Round 2; the smoke receipt is dated 2026-08-24. |
| DR-8 Completion vs residual risk | pass | The clean-VM evidence remains explicitly separate and is not used to satisfy either local integration AC. |

### Open Questions / Assumptions

- The workspace has no `.git` metadata, so this recheck used current file state, direct executable probes, and exact receipts rather than diff history.
- The approved plan's clean-Windows install/launch evidence remains a separate later `[B]`; Round 2 does not start Session 8c or Phase 8.

### Final Verdict

`approved` — F1 and F2 are closed with independent current-state and behavioral evidence. The registered packaging, UI, NSIS, and OpenAPI gates pass, and no new High or Critical behavioral finding exists.

### Follow-up Actions

None within this review. Stop at the review boundary; Session 8c and Phase 8 were not started.

### Residual Risk

Clean-Windows install/launch, upgrade persistence, dependency health, and full shipped MCP smoke remain the plan's separately declared environment evidence. That residual risk is accepted for this local distribution recheck and does not weaken the reproduced F1/F2 closure.
