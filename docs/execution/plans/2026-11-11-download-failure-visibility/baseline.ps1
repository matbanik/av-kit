# Session 65 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves that D-622 to D-625 carry Mat's ruling (S14), that the queue is right (S8:
# MEU-136 approved, MEU-137 to MEU-139 pending, 003e5b1 an ancestor of HEAD), and that the
# shapes this plan calls are present by name, with this plan's own names still absent (S11).
# Then records HEAD and the dirty tree with each dirty path's SHA-256, records every Files
# Modified target's line endings and SHA-256 in s65-anchors.txt, installs Python from the lock
# without the network, proves ui/ and mcp-server/node_modules match their locks, captures the
# base Python, UI and MCP runs and ruff, and runs the plan-local selftests. A copy of Session
# 64's with the checks changed for this plan: no FFmpeg pair, Pillow or eval step (nothing here
# encodes media), and a base UI run added because ui/ files change. The base runs' own failures
# are recorded, not fatal: the session gate excuses only the Python and UI ids the base receipts
# show failing, and nothing else. Every other step is fail-fast. Run from the repository root.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-11): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-11-download-failure-visibility'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s65\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# S14: the rows run on Mat's rulings. A ruled entry's chosen starts with an option letter and a
# colon, and its human_message_reference starts USER_EXPLICIT (the plan's §1 item 1).
$ruled = @'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1], "implementation-plan.md").read_text(encoding="utf-8")
log = text[text.index("## Decision Log"):]
ok = True
for decision, letters in (("D-622", "ABC"), ("D-623", "ABC"), ("D-624", "ABC"), ("D-625", "AB")):
    m = re.search(r"^  - id: " + decision + r"\n(.*?)(?=^  - id: |^```)", log, re.DOTALL | re.MULTILINE)
    if not m:
        print(f"{decision}: no entry in the decision log")
        ok = False
        continue
    body = m.group(1)
    chosen = re.search(r'^    chosen: "(.*)"$', body, re.MULTILINE)
    ref = re.search(r"^    human_message_reference: (.*)$", body, re.MULTILINE)
    letter = chosen.group(1)[:2] if chosen else ""
    reference = ref.group(1).strip().strip("'\"") if ref else ""
    good = len(letter) == 2 and letter[0] in letters and letter[1] == ":" and reference.startswith("USER_EXPLICIT ")
    print(f"{decision}: chosen starts {letter!r}, reference starts {reference[:24]!r}, ruled={good}")
    ok = ok and good
if not ok:
    print("a decision is unruled (S14); the rows can't run without Mat's words")
sys.exit(0 if ok else 1)
'@
Invoke-Step 'rulings' @('uv', 'run', '--no-sync', 'python', '-c', $ruled, $plan)

# S8: MEU-136 approved (Session 64 closed), MEU-137 to MEU-139 pending, and Session 64's commit
# an ancestor of HEAD.
$queue = @'
import pathlib, subprocess, sys
lines = pathlib.Path(".agent/context/meu-status.yaml").read_text(encoding="utf-8").splitlines()
def status(meu):
    for n, line in enumerate(lines):
        if line.strip() == f"id: {meu}":
            for follow in lines[n + 1 : n + 40]:
                if follow.strip().startswith("status:"):
                    return follow.split(":", 1)[1].strip().strip("'\"")
            return None
    return None
want = {"MEU-136": "approved", "MEU-137": "pending", "MEU-138": "pending", "MEU-139": "pending"}
have = {meu: status(meu) for meu in want}
print(f"queue: {have}")
s64 = subprocess.run(["git", "merge-base", "--is-ancestor", "003e5b1", "HEAD"], capture_output=True).returncode
print(f"003e5b1 is an ancestor of HEAD: {s64 == 0}")
sys.exit(0 if have == want and s64 == 0 else 1)
'@
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue)

# S11: the names this plan calls, by name, and the names it adds, still absent. A shape that
# differs in signature is found when row 1 re-reads its anchors.
$shapes = @'
import pathlib, re, sys
CORE = "packages/core/src/avkit_core"
INFRA = "packages/infrastructure/src/avkit_infra"
API = "packages/api/src/avkit_api"
ADAPTER = f"{INFRA}/youtube/adapter.py"
SERVICE = f"{CORE}/services/download.py"
DOMAIN = f"{CORE}/domain/download.py"
ERRORS = f"{CORE}/domain/errors.py"
ENUMS = f"{CORE}/domain/enums.py"
UI = "ui/src/renderer/src"
present = (
    (ADAPTER, r"^SABR_LOG_NEEDLES = \($", "SABR_LOG_NEEDLES"),
    (ADAPTER, r'^AGE_GATE_NEEDLES = \("sign in to confirm your age", "age-restricted"\)$', "AGE_GATE_NEEDLES"),
    (ADAPTER, r"^class _YtDlpLogger:$", "_YtDlpLogger"),
    (ADAPTER, r"^    def _scan\(self, message: object\) -> None:$", "_YtDlpLogger._scan"),
    (ADAPTER, r"^        yt_dlp_debug: bool = False,$", "the yt_dlp_debug bool kwarg"),
    (ADAPTER, r"^    def _base_opts\(self, logger: _YtDlpLogger\) -> dict\[str, object\]:$", "_base_opts"),
    (ADAPTER, r"^    def check_sabr_status\(self\) -> SABRStatus:$", "check_sabr_status"),
    (SERVICE, r'^log = structlog\.get_logger\(module="download"\)$', "the download logger"),
    (SERVICE, r"^    def check_sabr\(self\) -> SABRStatus:$", "check_sabr"),
    (SERVICE, r"^    def force_sabr\(self\) -> SABRStatus:$", "force_sabr"),
    (SERVICE, r"^    def clear_sabr\(self\) -> SABRStatus:$", "clear_sabr"),
    (SERVICE, r"^    def _run_one\(self, job: DownloadJob\) -> None:$", "_run_one"),
    (SERVICE, r"^    def _finish\(self, job_id: str, status: DownloadStatus, error: str \| None = None\) -> None:$", "_finish"),
    (DOMAIN, r'^SABR_STATUS_FIELDS: tuple\[str, \.\.\.\] = \("mode", "source", "checked_at"\)$', "SABR_STATUS_FIELDS"),
    (DOMAIN, r"^class SABRStatus:$", "SABRStatus"),
    (ERRORS, r"^class ExtractError\(DomainError\):$", "ExtractError"),
    (ERRORS, r"^DOMAIN_ERROR_TYPES: tuple\[type\[DomainError\], \.\.\.\] = \($", "DOMAIN_ERROR_TYPES"),
    (ENUMS, r"^class SABRMode\(StrEnum\):$", "SABRMode"),
    (f"{CORE}/domain/transcript.py", r"^class TranscriptFailureCause\(StrEnum\):$", "TranscriptFailureCause"),
    (f"{API}/wiring.py", r'^    yt_dlp_debug = settings\.get\("downloader", "yt_dlp_debug"\) is True$', "the wiring read"),
    (f"{UI}/components/queue/QueueCard.tsx", r"errorMessage\?: string \| null", "QueueCard errorMessage"),
    (f"{UI}/features/downloader/DownloaderPage.tsx", r'data-testid="sabr-status" hidden=\{!sabrActive\}', "the hidden SABR panel"),
    (f"{UI}/features/downloader/sabr-panel.ts", r"^export type SabrSnapshot = \{$", "SabrSnapshot"),
    (f"{UI}/features/downloader/useDownloadQueue.ts", r"^export type DownloadListItem = \{$", "DownloadListItem"),
    (f"{UI}/features/settings/SettingsPage.tsx", r'^            leaf="yt_dlp_debug"$', "the yt-dlp debug switch"),
    ("tests/integration/test_youtube_adapter.py", r"^SABR_LOG_NEEDLES = \($", "the test-local needles"),
    ("tests/unit/test_transcript_metadata.py", r"_YtDlpLogger\(True\)\.debug\(", "AC-122.16's debug-on line"),
    ("tests/unit/test_domain.py", r'^SPEC_SABR_STATUS_FIELDS = \("mode", "source", "checked_at"\)$', "the SPEC SABR pin"),
    ("tests/unit/test_domain.py", r'^    "ExtractError",  # TA-1 \(Session 33, MEU-76\)$', "the last error-name pin"),
)
absent = (
    (ENUMS, r"\bDownloadFailureCause\b", "DownloadFailureCause"),
    (ERRORS, r"\bDownloadFailedError\b", "DownloadFailedError"),
    (DOMAIN, r"\bdownload_failure_message\b|\bclean_line\b|\bmatched_phrase\b", "the domain names"),
    (ADAPTER, r"\bSABR_PHRASES\b|\bFAILURE_CAUSE_NEEDLES\b|\bclassify_download_error\b|\bmatched_phrase\b|\bsabr_phrase\b", "the adapter names"),
    (SERVICE, r"\bscrub_line\b", "scrub_line"),
    (SERVICE, r"download\.(started|done|failed|sabr_check|sabr_force|sabr_clear)", "the download log events"),
    (f"{UI}/features/downloader/sabr-panel.ts", r"\bsabrResultText\b", "sabrResultText"),
)
wrong = []
for rel, pattern, label in present:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if re.search(pattern, ln)]
    print(f"present {label}: {rel} lines {hits[:5]}")
    if not hits:
        wrong.append(f"missing {label}")
for rel, pattern, label in absent:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if re.search(pattern, ln)]
    print(f"absent {label}: {rel} lines {hits[:5]}")
    if hits:
        wrong.append(f"already present {label}")
print("shapes wrong (S11):", wrong)
sys.exit(1 if wrong else 0)
'@
Invoke-Step 'shapes' @('uv', 'run', '--no-sync', 'python', '-c', $shapes)

$head = (git rev-parse HEAD).Trim()
Set-Content -Path "$plan/baseline.sha" -Value $head -NoNewline
# Each line is the porcelain line, a tab, then the path's SHA-256 (`deleted` when it is gone).
# The session gate reads the path as the text between column 3 and the tab.
$dirty = @'
import hashlib, pathlib, subprocess, sys
out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], capture_output=True, check=True).stdout.decode("utf-8")
lines = []
for line in out.splitlines():
    path = pathlib.Path(line[3:])
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "deleted"
    lines.append(f"{line}\t{digest}")
pathlib.Path(sys.argv[1]).write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
print(f"baseline-dirty.txt {len(lines)} paths")
'@
Invoke-Step 'baseline-dirty' @('uv', 'run', '--no-sync', 'python', '-c', $dirty, "$plan/baseline-dirty.txt")
Write-Output "baseline.sha $head"

# Every Files Modified target's line endings and SHA-256, which each row reads before it writes.
# A new file is recorded as absent; an existing target that is missing stops here. A MIXED file
# keeps each line's own ending (S63 RULE-3).
$anchors = @'
import hashlib, pathlib, sys
CORE = "packages/core/src/avkit_core"
INFRA = "packages/infrastructure/src/avkit_infra"
API = "packages/api/src/avkit_api"
UI = "ui/src/renderer/src"
targets = (
    f"{CORE}/domain/enums.py",
    f"{CORE}/domain/errors.py",
    f"{CORE}/domain/download.py",
    f"{CORE}/services/download.py",
    f"{INFRA}/youtube/adapter.py",
    f"{API}/wiring.py",
    f"{UI}/features/downloader/DownloaderPage.tsx",
    f"{UI}/features/downloader/useDownloadQueue.ts",
    f"{UI}/features/downloader/sabr-panel.ts",
    "tests/unit/test_domain.py",
    "tests/unit/test_transcript_metadata.py",
    "tests/integration/test_youtube_adapter.py",
    "tests/integration/test_api_wiring.py",
    "ui/tests/unit/downloader-page.behavior.test.ts",
    "ui/tests/unit/settings-page.test.ts",
    "docs/build-plan/01-domain-layer.md",
    "docs/build-plan/02-infrastructure.md",
    "docs/build-plan/03-service-layer.md",
    "docs/build-plan/06-gui.md",
    ".agent/context/known-issues.yaml",
    ".agent/context/known-issues.md",
    ".agent/context/meu-status.yaml",
    "docs/BUILD_PLAN.md",
    ".agent/context/meu-registry.md",
    ".agent/context/grouping/2026-11-10-download-reliability-session-grouping.md",
)
new = (
    "tests/unit/test_download_failure_visibility.py",
    "tests/integration/test_youtube_adapter_visibility.py",
    "tests/e2e/test_api_download_visibility.py",
    "ui/tests/unit/sabr-panel.test.ts",
)
out, missing, present = [], [], []
for rel in targets:
    p = pathlib.Path(rel)
    if not p.is_file():
        missing.append(rel)
        continue
    data = p.read_bytes()
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    kind = "CRLF" if crlf and not lf else "LF" if lf and not crlf else f"MIXED crlf={crlf} lf={lf}"
    out.append(f"{hashlib.sha256(data).hexdigest()} {len(data):>9} {kind:<6} {rel}")
for rel in new:
    exists = pathlib.Path(rel).exists()
    out.append(f"{'present' if exists else 'absent'} new {rel}")
    if exists:
        present.append(rel)
pathlib.Path(sys.argv[1]).write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
print("missing targets:", missing, "new files already present:", present)
sys.exit(1 if missing or present else 0)
'@
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', '-c', $anchors, "$receipts/s65-anchors.txt")

# --offline: this step can't fetch a package.
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--offline', '--all-packages')

$lockSync = @'
import json, pathlib, sys
pkg = sys.argv[1]
lock = json.loads(pathlib.Path(pkg, "package-lock.json").read_text(encoding="utf-8"))["packages"]
want = {k: v.get("version") for k, v in lock.items() if k.startswith("node_modules/") and not v.get("optional")}
missing = sorted(k for k in want if not pathlib.Path(pkg, k, "package.json").exists())
have = {k: json.loads(pathlib.Path(pkg, k, "package.json").read_text(encoding="utf-8")).get("version") for k in want if k not in missing}
bad = sorted(k for k in have if have[k] != want[k])
for k in bad[:20]: print("version differs", k, want[k], have[k])
for k in missing[:20]: print("missing", k)
print(f"{pkg} lock sync: {len(want)} locked packages, {len(bad)} differ, {len(missing)} missing")
sys.exit(1 if bad or missing else 0)
'@
Invoke-Step 'ui-lock-sync' @('uv', 'run', 'python', '-c', $lockSync, 'ui')
Invoke-Step 'mcp-lock-sync' @('uv', 'run', 'python', '-c', $lockSync, 'mcp-server')

& rtk proxy uv run pytest tests/ --tb=short -q -rfE > "$receipts/s65-base-py.txt" 2>&1
Write-Output ("base suite py exit={0} receipt={1}/s65-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s65-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test > "$receipts/s65-base-ui.txt" 2>&1
Write-Output ("base suite ui exit={0} receipt={1}/s65-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s65-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run build > "$receipts/s65-base-mcp-build.txt" 2>&1
Write-Output ("base mcp build exit={0} receipt={1}/s65-base-mcp-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix mcp-server run test > "$receipts/s65-base-mcp.txt" 2>&1
Write-Output ("base suite mcp exit={0} receipt={1}/s65-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s65-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy uv run ruff check packages/ tests/ > "$receipts/s65-base-ruff.txt" 2>&1
Write-Output ("base ruff exit={0} receipt={1}/s65-base-ruff.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s65-base-ruff.txt" -Tail 5

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
