# Session 104 row runner (task.md §Task Table "One command per row"; §Row steps).
# `row-run.ps1 -Row N` runs, in order, the steps whose id is N followed by a dot. Each step's
# output goes to its receipt under C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test and
# its exit code to <receipt>.exit. The first non-zero step stops the row; the later steps are
# printed as not_run and the script exits with that code. A *recorded* step never stops the row,
# because a later step judges its receipt. A *fallback only* step runs only when
# R/ycc-proof-pair.txt reads fallback-applies, and a *proved only* step only when
# R/ycc-proof-verdict.txt reads proved; otherwise each writes its skip line as the receipt and 0
# as its exit (D-1483). A step *in ui* runs in P:\av-kit\ui and returns.
# Before every row other than 0, `row-check.py scope-paths` runs as the S4 pre-check into
# R/ycc-row<N>-s4.txt; a non-zero exit stops the row with exit 3 before any step (D-1485).
# The block between BEGIN STEPS and END STEPS is generated from task.md by
# `row-check.py steps --emit`, and `row-check.py steps` proves the two are equal (D-1474).
# `@paths` expands to the lines of the row's snapshot path list, `@issues` to one --issue per key
# of R/ycc-issue-resolve-set.json, and `$sha` to the row-0 sha256 of .agent/context/known-issues.yaml
# in PLAN/baseline-scope.json.
param([Parameter(Mandatory)][string]$Row)
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test'
$receipts = 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
$tmp = 'C:\Temp\av-kit\s104-tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

$S = [System.Collections.Generic.List[hashtable]]::new()
# BEGIN STEPS
$S.Add(@{ Id = '0.1'; Flags = ''; Receipt = 'ycc-baseline.txt'; Argv = @('pwsh', '-NoProfile', '-File', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/baseline.ps1') })
$S.Add(@{ Id = '0.2'; Flags = ''; Receipt = 'ycc-row-check-selftest.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', '--selftest') })
$S.Add(@{ Id = '0.3'; Flags = ''; Receipt = 'ycc-red-check-selftest.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/red-check.py', '--selftest') })
$S.Add(@{ Id = '0.4'; Flags = ''; Receipt = 'ycc-eol-check-selftest.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/eol-check.py', '--selftest') })
$S.Add(@{ Id = '0.5'; Flags = ''; Receipt = 'ycc-snapshot-selftest.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/snapshot-commit.py', '--selftest', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/snapshot-selftest') })
$S.Add(@{ Id = '0.6'; Flags = ''; Receipt = 'ycc-proof-selftest.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/proof-extract.py', '--selftest') })
$S.Add(@{ Id = '0.7'; Flags = ''; Receipt = 'ycc-steps.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'steps') })
$S.Add(@{ Id = '0.8'; Flags = ''; Receipt = 'ycc-plan-lint.txt'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test') })
$S.Add(@{ Id = '0.9'; Flags = 'recorded'; Receipt = 'ycc-base-py.txt'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q') })
$S.Add(@{ Id = '0.10'; Flags = 'recorded,ui'; Receipt = 'ycc-base-ui.txt'; Argv = @('npm', 'run', 'test') })
$S.Add(@{ Id = '0.11'; Flags = 'recorded'; Receipt = 'ycc-base-mcp.txt'; Argv = @('npm', '--prefix', 'mcp-server', 'test') })
$S.Add(@{ Id = '1.1'; Flags = 'recorded'; Receipt = 'ycc-proof-before.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/proof-extract.py', '--require-version', '2026.10.26', '--expect', 'challenge-errors', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-proof-before.json') })
$S.Add(@{ Id = '1.2'; Flags = ''; Receipt = 'ycc-row1-recorded.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'proof-recorded', 'before') })
$S.Add(@{ Id = '2.1'; Flags = 'recorded'; Receipt = 'ycc-row2-red.txt'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_ytdlp_lock.py', '--tb=short', '-q') })
$S.Add(@{ Id = '2.2'; Flags = ''; Receipt = 'ycc-row2-red-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/red-check.py', '--runner', 'pytest', '--require', 'test_ac_168_1_lock_holds_the_fixed_release', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-row2-red.txt') })
$S.Add(@{ Id = '2.3'; Flags = ''; Receipt = 'ycc-row2-lint.txt'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'tests/unit/test_ytdlp_lock.py') })
$S.Add(@{ Id = '2.4'; Flags = ''; Receipt = 'ycc-row2-record.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'red-record', '--row', '2', 'tests/unit/test_ytdlp_lock.py') })
$S.Add(@{ Id = '3.1'; Flags = ''; Receipt = 'ycc-row3-lock.txt'; Argv = @('uv', 'lock', '--upgrade-package', 'yt-dlp==2026.11.23') })
$S.Add(@{ Id = '3.2'; Flags = ''; Receipt = 'ycc-row3-lock-diff.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'lock') })
$S.Add(@{ Id = '3.3'; Flags = ''; Receipt = 'ycc-row3-sync.txt'; Argv = @('uv', 'sync', '--locked', '--all-packages') })
$S.Add(@{ Id = '3.4'; Flags = ''; Receipt = 'ycc-row3-lock-check.txt'; Argv = @('uv', 'lock', '--check') })
$S.Add(@{ Id = '3.5'; Flags = ''; Receipt = 'ycc-row3-installed.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'lock', '--installed') })
$S.Add(@{ Id = '3.6'; Flags = ''; Receipt = 'ycc-row3-green.txt'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_ytdlp_lock.py', '--tb=short', '-q') })
$S.Add(@{ Id = '3.7'; Flags = ''; Receipt = 'ycc-row3-redhash.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'red-unchanged') })
$S.Add(@{ Id = '3.8'; Flags = ''; Receipt = 'ycc-row3-eol.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/eol-check.py') })
$S.Add(@{ Id = '4.1'; Flags = ''; Receipt = 'ycc-row4-suites.txt'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_fetch_deno.py', 'tests/integration/test_youtube_adapter.py', 'tests/integration/test_youtube_client_fallback.py', 'tests/unit/test_extract_options.py', 'tests/integration/test_js_runtime_wiring.py', '--tb=short', '-q') })
$S.Add(@{ Id = '4.2'; Flags = ''; Receipt = 'ycc-row4-pins.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'pins-unchanged', '--row', '4') })
$S.Add(@{ Id = '5.1'; Flags = 'recorded'; Receipt = 'ycc-proof-after.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/proof-extract.py', '--require-version', '2026.11.23', '--expect', 'clean', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-proof-after.json') })
$S.Add(@{ Id = '5.2'; Flags = ''; Receipt = 'ycc-row5-recorded.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'proof-recorded', 'after') })
$S.Add(@{ Id = '5.3'; Flags = ''; Receipt = 'ycc-row5-classify.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'proof-pair', '--classify', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-proof-pair.txt') })
$S.Add(@{ Id = '5a.1'; Flags = 'fallback,recorded'; Receipt = 'ycc-row5a-red.txt'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_ytdlp_lock.py', '--tb=short', '-q') })
$S.Add(@{ Id = '5a.2'; Flags = 'fallback'; Receipt = 'ycc-row5a-red-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/red-check.py', '--runner', 'pytest', '--require', 'test_ac_168_6_adapter_passes_player_js_variant_tv', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-row5a-red.txt') })
$S.Add(@{ Id = '5a.3'; Flags = 'fallback'; Receipt = 'ycc-row5a-record.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'red-record', '--row', '5a', 'tests/unit/test_ytdlp_lock.py') })
$S.Add(@{ Id = '5a.4'; Flags = ''; Receipt = 'ycc-row5a-gate.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'variant-gate', '--stage', 'red') })
$S.Add(@{ Id = '5b.1'; Flags = 'fallback'; Receipt = 'ycc-row5b-green.txt'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_ytdlp_lock.py', 'tests/integration/test_youtube_adapter.py', 'tests/integration/test_youtube_client_fallback.py', 'tests/unit/test_extract_options.py', '--tb=short', '-q') })
$S.Add(@{ Id = '5b.2'; Flags = 'fallback,recorded'; Receipt = 'ycc-proof-fallback.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/proof-extract.py', '--require-version', '2026.11.23', '--variant', 'tv', '--expect', 'clean', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-proof-fallback.json') })
$S.Add(@{ Id = '5b.3'; Flags = 'fallback'; Receipt = 'ycc-row5b-recorded.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'proof-recorded', 'fallback') })
$S.Add(@{ Id = '5b.4'; Flags = ''; Receipt = 'ycc-row5b-gate.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'variant-gate', '--stage', 'green') })
$S.Add(@{ Id = '5b.5'; Flags = ''; Receipt = 'ycc-row5b-redhash.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'red-unchanged') })
$S.Add(@{ Id = '5b.6'; Flags = ''; Receipt = 'ycc-row5b-eol.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/eol-check.py') })
$S.Add(@{ Id = '5c.1'; Flags = ''; Receipt = 'ycc-row5c-verdict.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'proof-pair', '--require-proved', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-proof-verdict.txt') })
$S.Add(@{ Id = '6.1'; Flags = ''; Receipt = 'ycc-row6-package.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/package_backend.py') })
$S.Add(@{ Id = '6.2'; Flags = ''; Receipt = 'ycc-row6-smoke.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/smoke_packaged_runtime.py', '--backend-dir', 'packaging/dist/avkit-backend', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-smoke.json') })
$S.Add(@{ Id = '6.3'; Flags = ''; Receipt = 'ycc-row6-licences.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/generate_third_party_licenses.py', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-licences.txt') })
$S.Add(@{ Id = '6.4'; Flags = ''; Receipt = 'ycc-row6-licence-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'licence') })
$S.Add(@{ Id = '6.5'; Flags = ''; Receipt = 'ycc-row6-licence-tests.txt'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_generate_third_party_licenses.py', '--tb=short', '-q') })
$S.Add(@{ Id = '7.1'; Flags = ''; Receipt = 'ycc-row7-type-only.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'type-only') })
$S.Add(@{ Id = '7.2'; Flags = 'recorded'; Receipt = 'ycc-row7-red.txt'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_domain.py', 'tests/unit/test_services.py', 'tests/integration/test_youtube_adapter.py', 'tests/e2e/test_api_downloads.py', '--tb=short', '-q') })
$S.Add(@{ Id = '7.3'; Flags = ''; Receipt = 'ycc-row7-red-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/red-check.py', '--runner', 'pytest', '--require', 'test_ac_169_1_result_refuses_a_mismatched_outcome', '--require', 'test_ac_169_2_outcome_follows_the_failing_step', '--require', 'test_ac_169_3_malformed_cookie_file_is_unreadable_without_a_request', '--require', 'test_ac_169_4_adapter_message_is_the_first_line', '--require', 'test_ac_169_4_service_scrubs_the_message', '--require', 'test_ac_169_5_reply_carries_each_outcome', '--require', 'test_ac_15_7_cookie_test_envelope', '--require', 'test_ac_6_13_test_cookies_never_raises_cookie_error', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-row7-red.txt') })
$S.Add(@{ Id = '7.4'; Flags = ''; Receipt = 'ycc-row7-lint.txt'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'tests/') })
$S.Add(@{ Id = '7.5'; Flags = ''; Receipt = 'ycc-row7-pins.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'pins-moved', '--row', '7') })
$S.Add(@{ Id = '7.6'; Flags = ''; Receipt = 'ycc-row7-record.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'red-record', '--row', '7', 'tests/unit/test_domain.py', 'tests/unit/test_services.py', 'tests/integration/test_youtube_adapter.py', 'tests/e2e/test_api_downloads.py', 'tests/e2e/api_fakes.py') })
$S.Add(@{ Id = '8.1'; Flags = ''; Receipt = 'ycc-row8-green.txt'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_domain.py', 'tests/unit/test_services.py', 'tests/integration/test_youtube_adapter.py', 'tests/e2e/test_api_downloads.py', '--tb=short', '-q') })
$S.Add(@{ Id = '8.2'; Flags = ''; Receipt = 'ycc-row8-types.txt'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') })
$S.Add(@{ Id = '8.3'; Flags = ''; Receipt = 'ycc-row8-lint.txt'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') })
$S.Add(@{ Id = '8.4'; Flags = ''; Receipt = 'ycc-row8-redhash.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'red-unchanged') })
$S.Add(@{ Id = '8.5'; Flags = ''; Receipt = 'ycc-row8-eol.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/eol-check.py') })
$S.Add(@{ Id = '9.1'; Flags = 'recorded'; Receipt = 'ycc-row9-drift.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') })
$S.Add(@{ Id = '9.2'; Flags = ''; Receipt = 'ycc-row9-write.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/export_openapi.py', '-o', 'openapi.committed.json') })
$S.Add(@{ Id = '9.3'; Flags = ''; Receipt = 'ycc-row9-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') })
$S.Add(@{ Id = '9.4'; Flags = ''; Receipt = 'ycc-row9-openapi.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'openapi') })
$S.Add(@{ Id = '10a.1'; Flags = 'recorded'; Receipt = 'ycc-row10a-red.txt'; Argv = @('npm', '--prefix', 'mcp-server', 'test', '--', 'tests/download-cookies-test.test.ts') })
$S.Add(@{ Id = '10a.2'; Flags = ''; Receipt = 'ycc-row10a-red-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/red-check.py', '--runner', 'vitest', '--require', 'AC-169.7 the cookies_test description names the three outcomes', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-row10a-red.txt') })
$S.Add(@{ Id = '10a.3'; Flags = ''; Receipt = 'ycc-row10a-record.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'red-record', '--row', '10a', 'mcp-server/tests/download-cookies-test.test.ts') })
$S.Add(@{ Id = '10b.1'; Flags = ''; Receipt = 'ycc-row10b-tests.txt'; Argv = @('npm', '--prefix', 'mcp-server', 'test') })
$S.Add(@{ Id = '10b.2'; Flags = ''; Receipt = 'ycc-row10b-types.txt'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') })
$S.Add(@{ Id = '10b.3'; Flags = ''; Receipt = 'ycc-row10b-redhash.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'red-unchanged') })
$S.Add(@{ Id = '10b.4'; Flags = ''; Receipt = 'ycc-row10b-eol.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/eol-check.py') })
$S.Add(@{ Id = '11.1'; Flags = ''; Receipt = 'ycc-row11-test-ids.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'test-ids') })
$S.Add(@{ Id = '11.2'; Flags = 'recorded,ui'; Receipt = 'ycc-row11-red.txt'; Argv = @('npx', 'vitest', 'run', '--allowOnly=false', 'tests/unit/cookie-test-result.test.ts', 'tests/unit/sabr-panel.test.ts', 'tests/unit/downloader-page.behavior.test.ts') })
$S.Add(@{ Id = '11.3'; Flags = ''; Receipt = 'ycc-row11-red-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/red-check.py', '--runner', 'vitest', '--require', 'AC-169.8 each reply gives its text', '--require', 'AC-169.8 a failed outcome with no message drops the colon part', '--require', 'AC-169.9 each outcome shows its text with role status', '--require', 'AC-169.9 a new test and a changed cookie setting remove the result', '--require', 'AC-169.10 the button is busy while the request is pending', '--require', 'AC-169.10 a second click while pending sends no second request', '--require', 'AC-170.1 a detected result says that Check SABR does not use cookies', '--require', 'AC-138.8 each snapshot gives its contract text', '--require', 'AC-138.8 the time is zero-padded local time', '--require', 'AC-138.8 the SABR panel shows an Inactive and an Active check with their time', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-row11-red.txt') })
$S.Add(@{ Id = '11.4'; Flags = ''; Receipt = 'ycc-row11-types.txt'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') })
$S.Add(@{ Id = '11.5'; Flags = ''; Receipt = 'ycc-row11-lint.txt'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') })
$S.Add(@{ Id = '11.6'; Flags = ''; Receipt = 'ycc-row11-pins.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'pins-moved', '--row', '11') })
$S.Add(@{ Id = '11.7'; Flags = ''; Receipt = 'ycc-row11-record.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'red-record', '--row', '11', 'ui/tests/unit/cookie-test-result.test.ts', 'ui/tests/unit/sabr-panel.test.ts', 'ui/tests/unit/downloader-page.behavior.test.ts', 'ui/tests/e2e/downloader-cookie-test.test.ts') })
$S.Add(@{ Id = '11a.1'; Flags = ''; Receipt = 'ycc-row11a-paths.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'snapshot-paths', '--stage', 'red', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-snapshot-red-paths.txt') })
$S.Add(@{ Id = '11a.2'; Flags = ''; Receipt = 'ycc-row11a-snapshot.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/snapshot-commit.py', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-snapshot-red.json', '@paths') })
$S.Add(@{ Id = '11a.3'; Flags = ''; Receipt = 'ycc-row11a-verify.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/snapshot-commit.py', '--verify', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-snapshot-red.json') })
$S.Add(@{ Id = '11a.4'; Flags = ''; Receipt = 'ycc-row11a-host.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/e2e_remote.py', 'check', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-e2e-check-red.json') })
$S.Add(@{ Id = '12.1'; Flags = 'ui'; Receipt = 'ycc-row12-green.txt'; Argv = @('npx', 'vitest', 'run', '--allowOnly=false', 'tests/unit/cookie-test-result.test.ts', 'tests/unit/downloader-page.behavior.test.ts', '-t', 'AC-169') })
$S.Add(@{ Id = '12.2'; Flags = ''; Receipt = 'ycc-row12-types.txt'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') })
$S.Add(@{ Id = '12.3'; Flags = ''; Receipt = 'ycc-row12-lint.txt'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') })
$S.Add(@{ Id = '12.4'; Flags = ''; Receipt = 'ycc-row12-redhash.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'red-unchanged') })
$S.Add(@{ Id = '12.5'; Flags = ''; Receipt = 'ycc-row12-eol.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/eol-check.py') })
$S.Add(@{ Id = '13.1'; Flags = 'ui'; Receipt = 'ycc-row13-green.txt'; Argv = @('npx', 'vitest', 'run', '--allowOnly=false', 'tests/unit/cookie-test-result.test.ts', 'tests/unit/sabr-panel.test.ts', 'tests/unit/downloader-page.behavior.test.ts') })
$S.Add(@{ Id = '13.2'; Flags = ''; Receipt = 'ycc-row13-types.txt'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') })
$S.Add(@{ Id = '13.3'; Flags = ''; Receipt = 'ycc-row13-lint.txt'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') })
$S.Add(@{ Id = '13.4'; Flags = ''; Receipt = 'ycc-row13-redhash.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'red-unchanged') })
$S.Add(@{ Id = '13.5'; Flags = ''; Receipt = 'ycc-row13-eol.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/eol-check.py') })
$S.Add(@{ Id = '14.1'; Flags = ''; Receipt = 'ycc-row14-kept.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'kept') })
$S.Add(@{ Id = '14.2'; Flags = ''; Receipt = 'ycc-row14-sabr.txt'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_services.py', 'tests/integration/test_youtube_adapter.py', '-k', 'sabr', '--tb=short', '-q') })
$S.Add(@{ Id = '14.3'; Flags = ''; Receipt = 'ycc-row14-pins.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'pins-unchanged', '--row', '14') })
$S.Add(@{ Id = '15.1'; Flags = ''; Receipt = 'ycc-row15-paths.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'snapshot-paths', '--stage', 'green', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-snapshot-paths.txt') })
$S.Add(@{ Id = '15.2'; Flags = ''; Receipt = 'ycc-row15-snapshot.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/snapshot-commit.py', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-snapshot.json', '@paths') })
$S.Add(@{ Id = '15.3'; Flags = ''; Receipt = 'ycc-row15-verify.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/snapshot-commit.py', '--verify', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-snapshot.json') })
$S.Add(@{ Id = '15.4'; Flags = ''; Receipt = 'ycc-row15-host.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/e2e_remote.py', 'check', '--out', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-e2e-check.json') })
$S.Add(@{ Id = '17.1'; Flags = ''; Receipt = 'ycc-row17-result.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'e2e-result') })
$S.Add(@{ Id = '18.1'; Flags = ''; Receipt = 'ycc-row18-canon.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/canon-edit.py') })
$S.Add(@{ Id = '18.2'; Flags = ''; Receipt = 'ycc-row18-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'canon') })
$S.Add(@{ Id = '18.3'; Flags = ''; Receipt = 'ycc-row18-eol.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/eol-check.py') })
$S.Add(@{ Id = '18.4'; Flags = ''; Receipt = 'ycc-row18-home.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/check_home_path.py') })
$S.Add(@{ Id = '19.1'; Flags = ''; Receipt = 'ycc-row19-issue.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/issue-resolve.py', '@issues', '--set-file', 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-issue-resolve-set.json', '--expect-sha256', '$sha') })
$S.Add(@{ Id = '19.2'; Flags = ''; Receipt = 'ycc-row19-issues-render.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/issue_triage.py', 'render') })
$S.Add(@{ Id = '19.3'; Flags = ''; Receipt = 'ycc-row19-crlf.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/crlf.py') })
$S.Add(@{ Id = '19.4'; Flags = ''; Receipt = 'ycc-row19-issues-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/issue_triage.py', 'render', '--check') })
$S.Add(@{ Id = '19.5'; Flags = ''; Receipt = 'ycc-row19-meu169.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'update', 'MEU-169', 'ready_for_review', '--plan', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/implementation-plan.md') })
$S.Add(@{ Id = '19.6'; Flags = ''; Receipt = 'ycc-row19-meu170.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'update', 'MEU-170', 'ready_for_review', '--plan', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/implementation-plan.md') })
$S.Add(@{ Id = '19.7'; Flags = 'proved'; Receipt = 'ycc-row19-meu168.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'update', 'MEU-168', 'ready_for_review', '--plan', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/implementation-plan.md') })
$S.Add(@{ Id = '19.8'; Flags = ''; Receipt = 'ycc-row19-render.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'render') })
$S.Add(@{ Id = '19.9'; Flags = ''; Receipt = 'ycc-row19-render-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'render', '--check') })
$S.Add(@{ Id = '19.10'; Flags = ''; Receipt = 'ycc-row19-grouping.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/canon-edit.py', '--grouping') })
$S.Add(@{ Id = '19.11'; Flags = ''; Receipt = 'ycc-row19-register.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'register') })
$S.Add(@{ Id = 'H1-3.1'; Flags = ''; Receipt = 'ycc-h13-render.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'render', '--check') })
$S.Add(@{ Id = 'H1-3.2'; Flags = ''; Receipt = 'ycc-h13-status.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'status', '--stage', 'ready') })
$S.Add(@{ Id = 'H1-4.1'; Flags = ''; Receipt = 'ycc-h14-openapi.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') })
$S.Add(@{ Id = 'H1-4.2'; Flags = ''; Receipt = 'ycc-h14-no-deselect.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'no-deselect') })
$S.Add(@{ Id = 'H2-2.1'; Flags = ''; Receipt = 'ycc-reflection-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/validate_closeout_artifacts.py', '--reflection', 'docs/execution/reflections/2026-11-26-ytdlp-challenge-and-cookie-test-reflection.md', '--reflection-template', 'docs/execution/reflections/TEMPLATE.md', '--reflection-schema', '.agent/schemas/reflection.v1.yaml', '--decision-source', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/implementation-plan.md', '--decision-source', '.agent/context/handoffs/2026-11-26-ytdlp-challenge-and-cookie-test-MEU-168-handoff.md', '--decision-source', '.agent/context/handoffs/2026-11-26-ytdlp-challenge-and-cookie-test-MEU-169-handoff.md', '--decision-source', '.agent/context/handoffs/2026-11-26-ytdlp-challenge-and-cookie-test-MEU-170-handoff.md', '--decision-source', '.agent/context/grouping/2026-11-26-ui-findings-and-auto-update-session-grouping.md', '--decision-source', '.agent/context/known-issues.yaml', '--decision-issue', 'YTDLP-CHALLENGE-SOLVE-FAILS', '--decision-issue', 'DOWNLOADER-COOKIE-TEST-SILENT', '--decision-issue', 'SABR-CHECK-IGNORES-COOKIES') })
$S.Add(@{ Id = 'H2-2.2'; Flags = ''; Receipt = 'ycc-h22-meu169.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'update', 'MEU-169', 'approved') })
$S.Add(@{ Id = 'H2-2.3'; Flags = ''; Receipt = 'ycc-h22-meu170.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'update', 'MEU-170', 'approved') })
$S.Add(@{ Id = 'H2-2.4'; Flags = 'proved'; Receipt = 'ycc-h22-meu168.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'update', 'MEU-168', 'approved') })
$S.Add(@{ Id = 'H2-2.5'; Flags = ''; Receipt = 'ycc-h22-render.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'render') })
$S.Add(@{ Id = 'H2-2.6'; Flags = ''; Receipt = 'ycc-h22-render-check.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'render', '--check') })
$S.Add(@{ Id = 'H2-2.7'; Flags = 'ui'; Receipt = 'ycc-h22-canon.txt'; Argv = @('npm', 'run', 'test', '--', 'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts') })
$S.Add(@{ Id = 'H2-2.8'; Flags = ''; Receipt = 'ycc-h22-status.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'status', '--stage', 'approved') })
$S.Add(@{ Id = 'H2-3.1'; Flags = ''; Receipt = 'ycc-h23-metrics.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'metrics') })
$S.Add(@{ Id = 'H2-5.1'; Flags = ''; Receipt = 'ycc-h25-commit-draft.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'commit-draft') })
$S.Add(@{ Id = 'H2-6.1'; Flags = ''; Receipt = 'ycc-h26-next-prompt.txt'; Argv = @('uv', 'run', '--no-sync', 'python', 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py', 'next-prompt') })
# END STEPS

function Read-Word([string]$Name) {
    $path = "$receipts/$Name"
    if (-not (Test-Path -LiteralPath $path)) { return '' }
    $first = Get-Content -LiteralPath $path -TotalCount 1
    if ($null -eq $first) { return '' }
    return $first.Trim()
}

function Expand-Argv([string[]]$Argv) {
    $out = [System.Collections.Generic.List[string]]::new()
    foreach ($a in $Argv) {
        if ($a -eq '@paths') {
            $list = if ($Row -eq '11a') { 'ycc-snapshot-red-paths.txt' } else { 'ycc-snapshot-paths.txt' }
            foreach ($p in (Get-Content -LiteralPath "$receipts/$list")) {
                if ($p.Trim() -ne '') { $out.Add($p.Trim()) }
            }
        } elseif ($a -eq '@issues') {
            $set = Get-Content -LiteralPath "$receipts/ycc-issue-resolve-set.json" -Raw | ConvertFrom-Json
            foreach ($k in $set.PSObject.Properties.Name) { $out.Add('--issue'); $out.Add($k) }
        } elseif ($a -eq '$sha') {
            $scope = Get-Content -LiteralPath "$plan/baseline-scope.json" -Raw | ConvertFrom-Json
            $out.Add($scope.'.agent/context/known-issues.yaml'.sha256)
        } else {
            $out.Add($a)
        }
    }
    return , $out.ToArray()
}

$mine = @($S | Where-Object { $_.Id.StartsWith("$Row.") })
if ($mine.Count -eq 0) {
    Write-Output "row ${Row}: no steps in task.md §Row steps; run the row's Validation cell"
    exit 2
}

if ($Row -ne '0') {
    $s4 = "$receipts/ycc-row$Row-s4.txt"
    & rtk proxy uv run --no-sync python "$plan/row-check.py" scope-paths *> $s4
    $code = $LASTEXITCODE
    Set-Content -Path "$s4.exit" -Value $code -Encoding ascii
    Write-Output "s4 pre-check exit=$code receipt=$s4"
    Get-Content $s4 | Select-Object -Last 6
    if ($code -ne 0) {
        Write-Output "row ${Row}: S4 pre-check failed; no step ran"
        exit 3
    }
}

for ($i = 0; $i -lt $mine.Count; $i++) {
    $step = $mine[$i]
    $flags = @($step.Flags -split ',' | Where-Object { $_ -ne '' })
    $receipt = "$receipts/$($step.Receipt)"
    $skip = $null
    if ($flags -contains 'fallback' -and (Read-Word 'ycc-proof-pair.txt') -ne 'fallback-applies') {
        $skip = 'skipped: fallback not needed'
    }
    if ($flags -contains 'proved' -and (Read-Word 'ycc-proof-verdict.txt') -ne 'proved') {
        $skip = 'skipped: MEU-168 not proved'
    }
    if ($null -ne $skip) {
        Set-Content -Path $receipt -Value $skip -Encoding utf8
        Set-Content -Path "$receipt.exit" -Value 0 -Encoding ascii
        Write-Output ("{0} {1} receipt={2}" -f $step.Id, $skip, $receipt)
        continue
    }
    $argv = Expand-Argv $step.Argv
    if ($flags -contains 'ui') { Push-Location 'P:\av-kit\ui' }
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    if ($flags -contains 'ui') { Pop-Location }
    Set-Content -Path "$receipt.exit" -Value $code -Encoding ascii
    $kind = if ($flags -contains 'recorded') { ' recorded' } else { '' }
    Write-Output ("{0}{1} exit={2} receipt={3}" -f $step.Id, $kind, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -ne 0 -and -not ($flags -contains 'recorded')) {
        for ($j = $i + 1; $j -lt $mine.Count; $j++) {
            Write-Output ("{0} not_run reason=fail-fast after {1}" -f $mine[$j].Id, $step.Id)
        }
        Write-Output "row ${Row}: failed at $($step.Id)"
        exit $code
    }
}
Write-Output "row ${Row}: all steps exit 0"
exit 0
