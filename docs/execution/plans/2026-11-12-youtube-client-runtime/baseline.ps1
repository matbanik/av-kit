# Session 66 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves that D-640 to D-642 carry Mat's ruling (S14), that the queue is right (S8:
# MEU-139 approved, MEU-140 and MEU-141 pending, 0553779 an ancestor of HEAD), and that the
# shapes this plan calls are present by name, with this plan's own names and files still absent
# (S11). Then records HEAD and the dirty tree with each dirty path's SHA-256, records every Files
# Modified target's line endings and SHA-256 in s66-anchors.txt (with the pre-session packaged
# backend's size and time, which row 2b's Red smoke runs on), installs Python from the lock
# without the network, proves ui/ and mcp-server/node_modules match their locks, records the
# runtime facts (the yt-dlp version, whether yt_dlp_ejs imports, the user-folder Deno's version),
# captures the base Python, UI and MCP runs and ruff, and runs the plan-local selftests. A copy of
# Session 65's with the checks changed for this plan. The base runs' own failures are recorded, not
# fatal: the session gate excuses only the Python ids the base receipt shows failing, and nothing
# else. Every other step is fail-fast. Run from the repository root.
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
$plan = 'docs/execution/plans/2026-11-12-youtube-client-runtime'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s66\tmp'
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
# colon, and its human_message_reference starts USER_EXPLICIT (the plan's §1 item 1). D is each
# brief's do-nothing option, so it counts as a ruling too.
$ruled = @'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1], "implementation-plan.md").read_text(encoding="utf-8")
log = text[text.index("## Decision Log"):]
ok = True
for decision, letters in (("D-640", "ABCD"), ("D-641", "ABD"), ("D-642", "ABD")):
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

# S8: MEU-139 approved (Session 65 closed), MEU-140 and MEU-141 pending, and Session 65's commit
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
want = {"MEU-139": "approved", "MEU-140": "pending", "MEU-141": "pending"}
have = {meu: status(meu) for meu in want}
print(f"queue: {have}")
s65 = subprocess.run(["git", "merge-base", "--is-ancestor", "0553779", "HEAD"], capture_output=True).returncode
print(f"0553779 is an ancestor of HEAD: {s65 == 0}")
sys.exit(0 if have == want and s65 == 0 else 1)
'@
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue)

# S11: the names this plan calls, by name, and the names and files it adds, still absent. A shape
# that differs in signature is found when row 1 re-reads its anchors.
$shapes = @'
import pathlib, re, sys
CORE = "packages/core/src/avkit_core"
INFRA = "packages/infrastructure/src/avkit_infra"
API = "packages/api/src/avkit_api"
ADAPTER = f"{INFRA}/youtube/adapter.py"
SETTINGS_UI = "ui/src/renderer/src/features/settings"
present = (
    ("tests/unit/test_domain.py", r'^    assert list\(youtube_extract\.parameters\) == \["self", "url", "flat"\]$', "the port signature pin (row 1 moves it)"),
    ("tests/unit/test_transcript_metadata.py", r'^    assert hints == \{"url": str, "flat": bool, "return": VideoInfo \| PlaylistInfo\}$', "the AC-122.6 hints pin (row 1 moves it)"),
    ("tests/unit/test_transcript_metadata.py", r'^    assert list\(inspect\.signature\(YouTubePort\.extract_info\)\.parameters\) == \["self", "url", "flat"\]$', "the AC-122.6 parameters pin (row 1 moves it)"),
    (ADAPTER, r"^COOKIE_EXTRACTOR_ARGS: dict\[str, dict\[str, object\]\] = \{$", "COOKIE_EXTRACTOR_ARGS"),
    (ADAPTER, r"^SABR_EXTRACTOR_ARGS: dict\[str, dict\[str, object\]\] = \{$", "SABR_EXTRACTOR_ARGS"),
    (ADAPTER, r"^FAILURE_CAUSE_NEEDLES: tuple\[", "FAILURE_CAUSE_NEEDLES"),
    (ADAPTER, r"^def _quality_selector\(preset: QualityPreset\) -> str:$", "_quality_selector"),
    (ADAPTER, r"^def classify_download_error\(text: str, sabr_matched: bool\) -> tuple\[DownloadFailureCause, str\]:$", "classify_download_error"),
    (ADAPTER, r"^class YouTubeAdapter:$", "YouTubeAdapter"),
    (ADAPTER, r"^    def _base_opts\(self, logger: _YtDlpLogger\) -> dict\[str, object\]:$", "_base_opts"),
    (ADAPTER, r"^    def _cookie_opts\(self, options: DownloadOptions\) -> dict\[str, object\]:$", "_cookie_opts"),
    (ADAPTER, r"^    def extract_info\(self, url: str, flat: bool = False\) -> VideoInfo \| PlaylistInfo:$", "YouTubeAdapter.extract_info"),
    (ADAPTER, r"^    def download\(self, url: str, options: DownloadOptions\) -> DownloadResult:$", "YouTubeAdapter.download"),
    (ADAPTER, r"^    def check_sabr_status\(self\) -> SABRStatus:$", "check_sabr_status"),
    (f"{CORE}/services/extract.py", r"^class ExtractCoordinator:$", "ExtractCoordinator"),
    (f"{CORE}/services/extract.py", r"^    def extract_info\(self, url: str, flat: bool = False\) -> VideoInfo \| PlaylistInfo:$", "ExtractCoordinator.extract_info"),
    (f"{CORE}/ports/youtube.py", r"^    def extract_info\(self, url: str, flat: bool = False\) -> VideoInfo \| PlaylistInfo: \.\.\.$", "the port's extract_info"),
    (f"{CORE}/services/download.py", r"^def scrub_line\(text: str\) -> str:$", "scrub_line"),
    (f"{CORE}/services/settings.py", r"^SETTINGS_KEY_TABLE: dict\[tuple\[str, str\], SettingSpec\] = \{$", "SETTINGS_KEY_TABLE"),
    (f"{CORE}/services/settings.py", r'^    \("downloader", "ffmpeg_path"\): SettingSpec\("string", ""\),$', "the ffmpeg_path setting"),
    (f"{CORE}/services/health.py", r"^class HealthService:$", "HealthService"),
    (f"{CORE}/domain/health.py", r"^class DependencyHealth:$", "DependencyHealth"),
    (f"{INFRA}/media/adapter.py", r"^class FFmpegAdapter:$", "FFmpegAdapter"),
    (f"{INFRA}/media/adapter.py", r"^    def _resolve_ffmpeg\(self\) -> Path \| None:$", "FFmpegAdapter._resolve_ffmpeg"),
    (f"{API}/wiring.py", r"^def bundled_ffmpeg\(\) -> Path \| None:$", "bundled_ffmpeg"),
    (f"{API}/schemas/health.py", r"^class DependenciesOut\(ApiModel\):$", "DependenciesOut"),
    (f"{API}/schemas/settings.py", r"^    ffmpeg_path: str \| None = None$", "the API ffmpeg_path leaf"),
    (f"{SETTINGS_UI}/settings-schemas.ts", r"^    ffmpeg_path: z\.string\(\)\.nullable\(\)\.optional\(\),$", "the UI ffmpeg_path leaf"),
    ("mcp-server/src/toolsets/settings.ts", r'^      ffmpeg_path: \{ type: "string", default: "" \},$', "the MCP ffmpeg_path schema leaf"),
    ("mcp-server/src/toolsets/settings.ts", r"^  ffmpeg_path: z\.string\(\)\.optional\(\),$", "the MCP ffmpeg_path zod leaf"),
    ("mcp-server/scripts/audit/classify.ts", r'^export const ISOLATION_INPUT_KEYS: readonly string\[\] = \["downloader\.ffmpeg_path", "downloader\.cookie_file_path"\];$', "ISOLATION_INPUT_KEYS"),
    ("packages/infrastructure/pyproject.toml", r'^    "yt-dlp",$', "the yt-dlp dependency"),
    ("packaging/avkit-backend.spec", r"^from PyInstaller\.utils\.hooks import collect_data_files, collect_submodules$", "the spec's hook import"),
    ("packaging/avkit-backend.spec", r"^hiddenimports = \[$", "the spec's hiddenimports"),
    ("packaging/avkit-backend.spec", r'^datas = \[\*collect_data_files\("misaki"\)\]$', "the spec's datas"),
    ("ui/electron-builder.yml", r"^  - from: \.\./packaging/ffmpeg-win64$", "the ffmpeg extraResources entry"),
    (".gitignore", r"^packaging/ffmpeg-win64/$", "the ffmpeg ignore line"),
    ("tools/generate_third_party_licenses.py", r'^GPL_ALLOWED = frozenset\(\{"num2words"\}\)', "GPL_ALLOWED"),
    ("tools/generate_third_party_licenses.py", r'^OTHER_LISTS = """', "OTHER_LISTS"),
)
absent = (
    (ADAPTER, r"\b_attempt_opts\b|\bclient_side_error\b|\bjs_runtime\b|\bjs_runtimes\b", "the adapter names"),
    (f"{CORE}/domain/health.py", r"\bJsRuntimeStatus\b|\bjs_runtime\b", "JsRuntimeStatus"),
    (f"{CORE}/services/settings.py", r"\bdeno_path\b", "the core deno_path setting"),
    (f"{CORE}/services/extract.py", r"\boptions\b", "the coordinator options keyword"),
    (f"{API}/schemas/health.py", r"\bJsRuntimeOut\b|\bjs_runtime\b", "JsRuntimeOut"),
    (f"{API}/schemas/settings.py", r"\bdeno_path\b", "the API deno_path leaf"),
    (f"{API}/wiring.py", r"\bbundled_deno\b|\bJsRuntimeLocator\b", "bundled_deno"),
    (f"{SETTINGS_UI}/settings-schemas.ts", r"\bdeno_path\b", "the UI deno_path leaf"),
    ("mcp-server/src/toolsets/settings.ts", r"\bdeno_path\b", "the MCP deno_path leaf"),
    ("mcp-server/scripts/audit/classify.ts", r"\bdeno_path\b|\bAUDIT_INPUT\b", "the audit deno_path names"),
    ("packaging/avkit-backend.spec", r"\byt_dlp_ejs\b", "the solver collection"),
    ("packages/infrastructure/pyproject.toml", r"yt-dlp-ejs", "the yt-dlp-ejs dependency"),
    ("ui/electron-builder.yml", r"deno-win64", "the Deno extraResources entry"),
    (".gitignore", r"deno-win64", "the Deno ignore line"),
)
new_files = (
    f"{INFRA}/youtube/js_runtime.py",
    "tools/fetch_deno_windows.ps1",
    "tools/smoke_packaged_runtime.py",
    "tests/integration/test_youtube_client_fallback.py",
    "tests/unit/test_extract_options.py",
    "tests/e2e/test_api_client_fallback.py",
    "tests/unit/test_js_runtime.py",
    "tests/integration/test_js_runtime_wiring.py",
    "tests/e2e/test_api_js_runtime.py",
    "tests/unit/test_fetch_deno.py",
    "ui/tests/unit/settings-runtime.test.ts",
    "mcp-server/tests/settings-runtime.test.ts",
    "docs/execution/plans/2026-11-12-youtube-client-runtime/active-meus.txt",
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
for rel in new_files:
    exists = pathlib.Path(rel).exists()
    print(f"absent new file {rel}: exists={exists}")
    if exists:
        wrong.append(f"new file already present {rel}")
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
# keeps each line's own ending (S63 RULE-3). The divergence report is hashed only. The pre-session
# packaged backend is recorded by size and time (row 2b's Red smoke runs on it); it may be absent,
# and then row 2b builds one first.
$anchors = @'
import datetime, hashlib, pathlib, sys
CORE = "packages/core/src/avkit_core"
INFRA = "packages/infrastructure/src/avkit_infra"
API = "packages/api/src/avkit_api"
SETTINGS_UI = "ui/src/renderer/src/features/settings"
targets = (
    f"{INFRA}/youtube/adapter.py",
    f"{CORE}/ports/youtube.py",
    f"{CORE}/services/extract.py",
    f"{CORE}/services/download.py",
    f"{CORE}/services/settings.py",
    f"{CORE}/services/health.py",
    f"{CORE}/domain/health.py",
    f"{API}/wiring.py",
    f"{API}/schemas/health.py",
    f"{API}/schemas/settings.py",
    f"{API}/routes/health.py",
    "openapi.committed.json",
    "packages/infrastructure/pyproject.toml",
    "uv.lock",
    "packaging/avkit-backend.spec",
    "packaging/THIRD_PARTY_NOTICES.md",
    "ui/electron-builder.yml",
    ".gitignore",
    "tools/generate_third_party_licenses.py",
    "mcp-server/src/toolsets/settings.ts",
    "mcp-server/scripts/audit/classify.ts",
    "mcp-server/tests/audit/isolation.test.ts",
    "ui/tests/e2e/test-ids.ts",
    f"{SETTINGS_UI}/SettingsPage.tsx",
    f"{SETTINGS_UI}/settings-schemas.ts",
    f"{SETTINGS_UI}/useSettingsPage.ts",
    "tests/integration/test_youtube_adapter.py",
    "tests/unit/test_services.py",
    "tests/e2e/real_stack.py",
    "tests/e2e/test_api_error_surface.py",
    "tests/integration/test_download_received_quality.py",
    "tests/integration/test_api_wiring.py",
    "tests/e2e/test_api_health_settings.py",
    "tests/e2e/test_api_auth.py",
    "docs/build-plan/02-infrastructure.md",
    "docs/build-plan/06-gui.md",
    "docs/build-plan/07-distribution.md",
    ".agent/context/known-issues.yaml",
    ".agent/context/known-issues.md",
    ".agent/context/meu-status.yaml",
    "docs/BUILD_PLAN.md",
    ".agent/context/meu-registry.md",
    ".agent/context/grouping/2026-11-10-download-reliability-session-grouping.md",
)
new = (
    f"{INFRA}/youtube/js_runtime.py",
    "tools/fetch_deno_windows.ps1",
    "tools/smoke_packaged_runtime.py",
    "tests/integration/test_youtube_client_fallback.py",
    "tests/unit/test_extract_options.py",
    "tests/e2e/test_api_client_fallback.py",
    "tests/unit/test_js_runtime.py",
    "tests/integration/test_js_runtime_wiring.py",
    "tests/e2e/test_api_js_runtime.py",
    "tests/unit/test_fetch_deno.py",
    "ui/tests/unit/settings-runtime.test.ts",
    "mcp-server/tests/settings-runtime.test.ts",
)
hashed_only = ("docs/proposals/2026-11-10-download-logic-divergence-report.md",)
onedir = pathlib.Path("packaging/dist/avkit-backend/avkit-backend.exe")
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
if onedir.is_file():
    st = onedir.stat()
    stamp = datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
    out.append(f"pre-session onedir {onedir.as_posix()} size={st.st_size} mtime={stamp}")
else:
    out.append(f"pre-session onedir {onedir.as_posix()} absent")
pathlib.Path(sys.argv[1]).write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
print("missing targets:", missing, "new files already present:", present)
sys.exit(1 if missing or present else 0)
'@
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', '-c', $anchors, "$receipts/s66-anchors.txt")

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

# Session 52 RULE-2: the runtime facts the rows rely on, recorded before any row runs. The Deno
# path is printed with <HOME> for the home folder. Nothing here reaches the network.
$runtimeFacts = @'
import importlib.metadata, importlib.util, pathlib, subprocess, sys
print("yt-dlp", importlib.metadata.version("yt-dlp"))
print("yt_dlp_ejs importable:", importlib.util.find_spec("yt_dlp_ejs") is not None)
deno = pathlib.Path.home() / ".deno" / "bin" / "deno.exe"
if deno.is_file():
    first = subprocess.run([str(deno), "--version"], capture_output=True, text=True, timeout=30).stdout.splitlines()
    print("<HOME>/.deno/bin/deno.exe:", first[0] if first else "no output")
else:
    print("<HOME>/.deno/bin/deno.exe: absent")
'@
Invoke-Step 'runtime-facts' @('uv', 'run', '--no-sync', 'python', '-c', $runtimeFacts)

& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE > "$receipts/s66-base-py.txt" 2>&1
Write-Output ("base suite py exit={0} receipt={1}/s66-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s66-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test > "$receipts/s66-base-ui.txt" 2>&1
Write-Output ("base suite ui exit={0} receipt={1}/s66-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s66-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run build > "$receipts/s66-base-mcp-build.txt" 2>&1
Write-Output ("base mcp build exit={0} receipt={1}/s66-base-mcp-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix mcp-server run test > "$receipts/s66-base-mcp.txt" 2>&1
Write-Output ("base suite mcp exit={0} receipt={1}/s66-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s66-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy uv run --no-sync ruff check packages/ tests/ > "$receipts/s66-base-ruff.txt" 2>&1
Write-Output ("base ruff exit={0} receipt={1}/s66-base-ruff.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s66-base-ruff.txt" -Tail 5

Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
