# Session 67 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves that D-671 carries Mat's ruling (S9), that the queue is right (S8: MEU-141
# approved, MEU-142 pending, 3435b7e an ancestor of HEAD), and that the shapes this plan calls
# are present by name, with this plan's own names and files still absent (S7). Then records HEAD
# and the dirty tree with each dirty path's SHA-256, records every Files Modified target's line
# endings and SHA-256 in s67-anchors.txt, installs Python from the lock without the network,
# proves ui/ and mcp-server/node_modules match their locks, asserts the pinned FFmpeg pair (S4),
# captures the base Python, UI and MCP runs and ruff, and runs the plan-local selftests. A copy
# of Session 66's with the checks changed for this plan and Session 54's FFmpeg-pair check. The
# base runs' own failures are recorded, not fatal: the session gate excuses only the Python ids
# the base receipt shows failing, and nothing else. Every other step is fail-fast. Run from the
# repository root with PowerShell 7 (pwsh -NoProfile -File).
#
# docs/proposals/2026-11-10-download-logic-divergence-report.md is hashed, never opened or printed.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-12): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-12-download-audio-extract'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s67\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# S9: the rows run on Mat's ruling of the one brief. A ruled entry's chosen starts with an option
# letter and a colon, and its human_message_reference starts USER_EXPLICIT. D is the brief's
# do-nothing option, so it counts as a ruling too.
$ruled = @'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1], "implementation-plan.md").read_text(encoding="utf-8")
log = text[text.index("## Decision Log"):]
ok = True
for decision, letters in (("D-671", "ABD"),):
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
    print("a decision is unruled (S9); the rows can't run without Mat's words")
sys.exit(0 if ok else 1)
'@
Invoke-Step 'rulings' @('uv', 'run', '--no-sync', 'python', '-c', $ruled, $plan)

# S8: MEU-141 approved (Session 66 closed), MEU-142 pending, and Session 66's commit an
# ancestor of HEAD.
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
want = {"MEU-141": "approved", "MEU-142": "pending"}
have = {meu: status(meu) for meu in want}
print(f"queue: {have}")
s66 = subprocess.run(["git", "merge-base", "--is-ancestor", "3435b7e", "HEAD"], capture_output=True).returncode
print(f"3435b7e is an ancestor of HEAD: {s66 == 0}")
sys.exit(0 if have == want and s66 == 0 else 1)
'@
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue)

# S7: the names this plan calls, by name, and the names and files it adds, still absent. A shape
# that differs in signature is found when row 1 re-reads its anchors.
$shapes = @'
import pathlib, re, sys
CORE = "packages/core/src/avkit_core"
INFRA = "packages/infrastructure/src/avkit_infra"
API = "packages/api/src/avkit_api"
SERVICE = f"{CORE}/services/download.py"
present = (
    (SERVICE, r"^    def _run_one\(self, job: DownloadJob\) -> None:$", "_run_one"),
    (SERVICE, r"^    def _finish\(self, job_id: str, status: DownloadStatus, error: str \| None = None\) -> None:$", "_finish"),
    (SERVICE, r"^def scrub_line\(text: str\) -> str:$", "scrub_line"),
    (SERVICE, r"^def first_line\(text: str\) -> str:$", "first_line"),
    (SERVICE, r"^_LINE_BREAKS = re\.compile\(", "_LINE_BREAKS"),
    (f"{CORE}/ports/media.py", r"^    def convert\(self, input_path: Path, output_path: Path, options: ConvertOptions\) -> None: \.\.\.$", "MediaPort.convert"),
    (f"{CORE}/domain/progress.py", r"^class ConvertOptions:$", "ConvertOptions"),
    (f"{CORE}/domain/download.py", r"^def download_failure_message\(cause: DownloadFailureCause, reason: str \| None = None\) -> str:$", "download_failure_message"),
    (f"{CORE}/domain/errors.py", r"^class FFmpegNotFoundError\(DomainError\):$", "FFmpegNotFoundError"),
    (f"{CORE}/services/tts.py", r"^TTS_MP3_CONVERT = ConvertOptions\($", "TTS_MP3_CONVERT (the 192 kbps precedent)"),
    (f"{INFRA}/media/adapter.py", r'raise FFmpegNotFoundError\("ffmpeg binary was not found"\)', "the adapter's missing-binary text"),
    (f"{API}/wiring.py", r"^    media = FFmpegAdapter\($", "the shared media adapter"),
    (f"{API}/wiring.py", r"^    download = DownloadService\($", "the DownloadService construction"),
    (".github/workflows/ci.yml", r"^          --deselect tests/integration/test_video_real_ffmpeg\.py$", "the last CI deselect"),
    ("tests/unit/test_conversion_service.py", r'^    assert "conversion_jobs" not in inspect\.getsource\(download_mod\)$', "the AC-30.8 source pin"),
)
absent = (
    (SERVICE, r"\bAUDIO_EXTRACT\b|\blast_line\b|\bMediaPort\b|\b_media\b|\bConvertOptions\b|\bsource_kept\b|\bpartial_kept\b|\bFFmpegNotFoundError\b", "the service names"),
    (".github/workflows/ci.yml", r"test_download_audio_extract_real_ffmpeg", "the new CI deselect"),
    ("tests/integration/test_api_wiring.py", r"\bdownload\._media\b", "the shared-media wiring test"),
)
new_files = (
    "tests/unit/test_download_audio_extract.py",
    "tests/integration/test_download_audio_extract_real_ffmpeg.py",
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
# The wiring's DownloadService call holds no media keyword yet (D-664 adds it).
wiring = pathlib.Path(f"{API}/wiring.py").read_text(encoding="utf-8")
start = wiring.index("    download = DownloadService(")
call = wiring[start : wiring.index("\n    )", start)]
print(f"absent media keyword in the DownloadService call: {'media=' not in call}")
if "media=" in call:
    wrong.append("already present media= in the DownloadService call")
for rel in new_files:
    exists = pathlib.Path(rel).exists()
    print(f"absent new file {rel}: exists={exists}")
    if exists:
        wrong.append(f"new file already present {rel}")
print("shapes wrong (S7):", wrong)
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
# keeps each line's own ending (S63 RULE-3). The divergence report is hashed only.
$anchors = @'
import hashlib, pathlib, sys
targets = (
    "packages/core/src/avkit_core/services/download.py",
    "packages/api/src/avkit_api/wiring.py",
    "tests/e2e/real_stack.py",
    "tests/e2e/test_api_error_surface.py",
    "tests/integration/test_download_received_quality.py",
    "tests/unit/test_download_failure_visibility.py",
    "tests/unit/test_extract_options.py",
    "tests/unit/test_services.py",
    "tests/integration/test_api_wiring.py",
    ".github/workflows/ci.yml",
    "docs/build-plan/03-service-layer.md",
    ".agent/context/known-issues.yaml",
    ".agent/context/known-issues.md",
    ".agent/context/meu-status.yaml",
    "docs/BUILD_PLAN.md",
    ".agent/context/meu-registry.md",
    ".agent/context/grouping/2026-11-10-download-reliability-session-grouping.md",
)
new = (
    "tests/unit/test_download_audio_extract.py",
    "tests/integration/test_download_audio_extract_real_ffmpeg.py",
)
hashed_only = ("docs/proposals/2026-11-10-download-logic-divergence-report.md",)
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
for rel in hashed_only:
    p = pathlib.Path(rel)
    digest = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "absent"
    out.append(f"{digest} hashed-only {rel}")
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
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', '-c', $anchors, "$receipts/s67-anchors.txt")

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
Invoke-Step 'ui-lock-sync' @('uv', 'run', '--no-sync', 'python', '-c', $lockSync, 'ui')
Invoke-Step 'mcp-lock-sync' @('uv', 'run', '--no-sync', 'python', '-c', $lockSync, 'mcp-server')

# S4: the real-FFmpeg module (AC-142.17) runs this pair; a missing or truncated binary stops here.
foreach ($name in @('ffmpeg.exe', 'ffprobe.exe')) {
    $exe = Join-Path $root "packaging/ffmpeg-win64/$name"
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
        Write-Output "baseline step ffmpeg-pair exit=1 ($name is missing; S4)"
        exit 1
    }
    $size = (Get-Item -LiteralPath $exe).Length
    if ($size -le 1024) {
        Write-Output ("baseline step ffmpeg-pair exit=1 ({0} is {1} B; S4)" -f $name, $size)
        exit 1
    }
    $versionText = @(& $exe -version)
    $versionExit = $LASTEXITCODE
    $first = $versionText | Select-Object -First 1
    if ($versionExit -ne 0) {
        Write-Output ("baseline step ffmpeg-pair exit=1 ({0} -version exit={1}; S4)" -f $name, $versionExit)
        exit 1
    }
    Write-Output ("{0} {1} B: {2}" -f $name, $size, $first)
}
Write-Output 'baseline step ffmpeg-pair exit=0'

& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE > "$receipts/s67-base-py.txt" 2>&1
Write-Output ("base suite py exit={0} receipt={1}/s67-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s67-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test > "$receipts/s67-base-ui.txt" 2>&1
Write-Output ("base suite ui exit={0} receipt={1}/s67-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s67-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run build > "$receipts/s67-base-mcp-build.txt" 2>&1
Write-Output ("base mcp build exit={0} receipt={1}/s67-base-mcp-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix mcp-server run test > "$receipts/s67-base-mcp.txt" 2>&1
Write-Output ("base suite mcp exit={0} receipt={1}/s67-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s67-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy uv run --no-sync ruff check packages/ tests/ > "$receipts/s67-base-ruff.txt" 2>&1
Write-Output ("base ruff exit={0} receipt={1}/s67-base-ruff.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s67-base-ruff.txt" -Tail 5

Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
