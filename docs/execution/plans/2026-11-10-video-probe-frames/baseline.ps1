# Session 62 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves that D-573, D-576 and D-577 carry Mat's ruling (S14), that the queue is right
# (S8: MEU-130 approved, MEU-133 and MEU-134 pending, the rc.3 release record b1d174b an
# ancestor of HEAD), and that the shapes this plan calls are present by name, with this plan's
# own names still absent (S11). Then records HEAD and the dirty tree with each dirty path's
# SHA-256, records every Files Modified target's line endings and SHA-256 in s62-anchors.txt,
# installs Python from the lock without the network, proves ui/ and mcp-server/node_modules
# match their locks, asserts the pinned FFmpeg pair and Pillow (S4), captures the base Python
# and MCP runs and ruff, and runs the plan-local selftests. A copy of Session 61's with the
# checks changed for this plan; no UI or Electron run, because no ui/ file changes. The base
# runs' own failures are recorded, not fatal: the session gate excuses only the Python ids the
# py receipt shows failing, and nothing else. Every other step is fail-fast. Run from the
# repository root.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-10): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-10-video-probe-frames'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s62\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# S14: rows 1 to 5 run on Mat's rulings. A ruled entry's chosen starts with an option letter
# and a colon, and its human_message_reference starts USER_EXPLICIT (the plan's §1 item 1).
$ruled = @'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1], "implementation-plan.md").read_text(encoding="utf-8")
log = text[text.index("## Decision Log"):]
ok = True
for decision, letters in (("D-573", "AB"), ("D-576", "ABC"), ("D-577", "ABC")):
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
    print("a decision is unruled (S14); rows 1 to 5 can't run without Mat's words")
sys.exit(0 if ok else 1)
'@
Invoke-Step 'd573-d576-d577-ruled' @('uv', 'run', '--no-sync', 'python', '-c', $ruled, $plan)

# S8: MEU-130 approved (Session 59 closed), MEU-133 and MEU-134 pending, and the rc.3 release
# record an ancestor of HEAD (grouping D-503).
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
want = {"MEU-130": "approved", "MEU-133": "pending", "MEU-134": "pending"}
have = {meu: status(meu) for meu in want}
print(f"queue: {have}")
rc3 = subprocess.run(["git", "merge-base", "--is-ancestor", "b1d174b", "HEAD"], capture_output=True).returncode
print(f"b1d174b is an ancestor of HEAD: {rc3 == 0}")
sys.exit(0 if have == want and rc3 == 0 else 1)
'@
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue)

# S11: the names this plan calls, by name, and the names it adds, still absent. A shape that
# differs in signature is found when row 1 re-reads its anchors.
$shapes = @'
import pathlib, re, sys
CORE = "packages/core/src/avkit_core"
ADAPTER = "packages/infrastructure/src/avkit_infra/media/adapter.py"
present = (
    (f"{CORE}/ports/media.py", r"^class MediaPort\(Protocol\):", "MediaPort"),
    (f"{CORE}/ports/media.py", r"^    def probe\(self, file_path: Path\) -> MediaInfo: \.\.\.", "MediaPort.probe"),
    (ADAPTER, r"^    def _require_ffmpeg\(self\) -> Path:", "_require_ffmpeg"),
    (ADAPTER, r"^    def _run\(self, command: list\[str\]\) -> subprocess\.CompletedProcess\[str\]:", "FFmpegAdapter._run"),
    (f"{CORE}/services/capture.py", r"^def import_stem\(", "import_stem"),
    (f"{CORE}/services/capture.py", r"^    def _import_dest\(", "_import_dest"),
    (f"{CORE}/services/capture.py", r"^CAPTURE_FILE_LOCK = ", "CAPTURE_FILE_LOCK"),
    (f"{CORE}/services/capture.py", r'^TMP_SUFFIX = "\.avkit-tmp"', "TMP_SUFFIX"),
    (f"{CORE}/services/capture.py", r"^    def _upsert_shot\(", "_upsert_shot"),
    (f"{CORE}/services/conversion.py", r"^class ConversionService:", "ConversionService"),
    ("mcp-server/src/client.ts", r"^export const ADD_TIMEOUT_MS = 120_000;", "ADD_TIMEOUT_MS"),
    ("mcp-server/src/toolsets/registry.ts", r'\(tool === "avkit_capture" && \(action === "capture" \|\| action === "crop"\)\)', "the ADD_TIMEOUT_MS capture selection"),
    ("mcp-server/src/toolsets/registry.ts", r'action: "gpu_refresh", method: "POST"', "the gpu_refresh ACTION_INDEX row"),
    ("mcp-server/src/toolsets/registry.ts", r'action: "crop", method: "POST"', "the crop ACTION_INDEX row"),
    ("mcp-server/tests/audit/coverage.test.ts", r'^const BASELINE_PENDING = \["avkit_capture\.crop"\];', "BASELINE_PENDING"),
    ("mcp-server/tests/audit/runner-fake-backend.test.ts", r"^    expect\(summary\.discovery\.actions\)\.toBe\(71\);", "the built-server action count 71"),
    ("mcp-server/scripts/audit/plan.ts", r"^function makeVideo\(", "makeVideo"),
    ("mcp-server/scripts/audit/plan.ts", r'id: "convert\.gpu_refresh"', "the convert.gpu_refresh audit step"),
    ("mcp-server/scripts/audit/plan.ts", r'id: "capture\.crop"', "the capture.crop audit step"),
)
absent = (
    (f"{CORE}/ports/capture.py", r"\bFramePort\b|\bFrameSeek\b", "FramePort and FrameSeek"),
    (ADAPTER, r"\bgrab_frame\b", "grab_frame"),
    (f"{CORE}/services/conversion.py", r"\bprobe_file\b", "probe_file"),
    (f"{CORE}/services/capture.py", r"\bframes_from_video\b|\bFRAMES_DEADLINE_S\b|\bvideo_input\b", "frames_from_video"),
    ("packages/api/src/avkit_api/routes/conversions.py", r'"/probe"', "the /probe route"),
    ("packages/api/src/avkit_api/routes/captures.py", r'"/frames"', "the /frames route"),
    ("packages/api/src/avkit_api/schemas/conversions.py", r"\bConversionProbe(In|Out)\b", "the probe schemas"),
    ("packages/api/src/avkit_api/schemas/captures.py", r"\bCaptureFrames(In|Out)\b", "the frames schemas"),
    ("packages/api/src/avkit_api/wiring.py", r"\bframes=", "frames= in wiring"),
    ("mcp-server/src/toolsets/convert.ts", r'z\.literal\("probe"\)|avkit_convert\.probe', "the probe member"),
    ("mcp-server/src/toolsets/capture.ts", r'z\.literal\("frames"\)|avkit_capture\.frames|FRAMES_TEXT', "the frames member"),
    ("mcp-server/src/toolsets/registry.ts", r'action: "(probe|frames)"', "the probe and frames ACTION_INDEX rows"),
    ("mcp-server/scripts/audit/plan.ts", r'id: "(convert\.probe|capture\.frames)"', "the probe and frames audit steps"),
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
# _run passes text=True and no encoding= (D-573's subject).
adapter = pathlib.Path(ADAPTER).read_text(encoding="utf-8")
run = re.search(r"^    def _run\(self.*?(?=^    def )", adapter, re.DOTALL | re.MULTILINE)
body = run.group(0) if run else ""
print(f"_run: text=True {'text=True' in body}, encoding= {'encoding=' in body}")
if "text=True" not in body or "encoding=" in body:
    wrong.append("_run's decoding is not text=True with no encoding")
# CaptureSource ends with Crop and has no Video member.
enums = pathlib.Path(f"{CORE}/domain/enums.py").read_text(encoding="utf-8")
block = re.search(r"^class CaptureSource\(StrEnum\):\n(.*?)(?=^\S)", enums, re.DOTALL | re.MULTILINE)
members = re.findall(r'^    (\w+) = "', block.group(1), re.MULTILINE) if block else []
print(f"CaptureSource members: {members}")
if not members or members[-1] != "Crop" or "Video" in members:
    wrong.append("CaptureSource does not end with Crop, or already has Video")
print("shapes wrong (S11):", wrong)
sys.exit(1 if wrong else 0)
'@
Invoke-Step 'shapes' @('uv', 'run', '--no-sync', 'python', '-c', $shapes)

$head = (git rev-parse HEAD).Trim()
Set-Content -Path "$plan/baseline.sha" -Value $head -NoNewline
# Each line is the porcelain line, a tab, then the path's SHA-256 (`deleted` when it is gone).
# The session gate reads the path as the text between column 3 and the tab. The other session's
# proposal is hashed here and never opened as text.
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
# A new file is recorded as absent; an existing target that is missing stops here.
$anchors = @'
import hashlib, pathlib, sys
CORE = "packages/core/src/avkit_core"
API = "packages/api/src/avkit_api"
targets = (
    f"{CORE}/ports/capture.py",
    f"{CORE}/domain/enums.py",
    f"{CORE}/services/conversion.py",
    f"{CORE}/services/capture.py",
    "packages/infrastructure/src/avkit_infra/media/adapter.py",
    f"{API}/routes/conversions.py",
    f"{API}/schemas/conversions.py",
    f"{API}/routes/captures.py",
    f"{API}/schemas/captures.py",
    f"{API}/wiring.py",
    "openapi.committed.json",
    "mcp-server/src/toolsets/convert.ts",
    "mcp-server/src/toolsets/capture.ts",
    "mcp-server/src/toolsets/registry.ts",
    "mcp-server/scripts/audit/plan.ts",
    "tests/unit/test_domain_capture.py",
    "tests/unit/test_domain.py",
    "tests/e2e/test_api_captures.py",
    "tests/e2e/test_api_openapi.py",
    "tests/e2e/test_api_downloads.py",
    "tests/e2e/test_api_bodies.py",
    "tests/e2e/test_api_conversions.py",
    "mcp-server/tests/convert.test.ts",
    "mcp-server/tests/capture.test.ts",
    "mcp-server/tests/action-index.test.ts",
    "mcp-server/tests/m7-resource.test.ts",
    "mcp-server/tests/fixtures.ts",
    "mcp-server/tests/audit/coverage.test.ts",
    "mcp-server/tests/audit/runner-fake-backend.test.ts",
    ".github/workflows/ci.yml",
    "docs/build-plan/08-video-conversion.md",
    "docs/build-plan/09-screenshot-capture.md",
    ".agent/context/meu-status.yaml",
    "docs/BUILD_PLAN.md",
    ".agent/context/meu-registry.md",
    ".agent/context/grouping/2026-11-09-video-stills-session-grouping.md",
)
new = (
    f"{CORE}/services/video_input.py",
    "tests/unit/test_video_input.py",
    "tests/unit/test_conversion_probe.py",
    "tests/unit/test_media_adapter_frames.py",
    "tests/unit/test_capture_frames_service.py",
    "tests/e2e/test_api_conversion_probe.py",
    "tests/e2e/test_api_capture_frames.py",
    "tests/integration/test_video_real_ffmpeg.py",
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
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', '-c', $anchors, "$receipts/s62-anchors.txt")

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

# The real-FFmpeg modules run the pinned pair; a missing or truncated binary is Stop Condition
# S4, not a fetch.
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
    $first = (& $exe -version | Select-Object -First 1)
    if ($LASTEXITCODE -ne 0) {
        Write-Output ("baseline step ffmpeg-pair exit=1 ({0} -version exit {1}; S4)" -f $name, $LASTEXITCODE)
        exit 1
    }
    Write-Output ("{0} {1} B: {2}" -f $name, $size, $first)
}
Write-Output 'baseline step ffmpeg-pair exit=0'

# FRAME_WRITE checks each grabbed PNG with Pillow, and the capture inbox rests on 13.0.0.
$pillow = @'
import sys
import PIL
from PIL import Image
print(f"pillow {PIL.__version__} MAX_IMAGE_PIXELS {Image.MAX_IMAGE_PIXELS}")
sys.exit(0 if PIL.__version__ == "13.0.0" and Image.MAX_IMAGE_PIXELS == 89478485 else 1)
'@
Invoke-Step 'pillow-version' @('uv', 'run', 'python', '-c', $pillow)

& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/s62-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s62-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s62-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run build *> "$receipts/s62-base-mcp-build.txt"
Write-Output ("base mcp build exit={0} receipt={1}/s62-base-mcp-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix mcp-server run test *> "$receipts/s62-base-mcp.txt"
Write-Output ("base suite mcp exit={0} receipt={1}/s62-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s62-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy uv run ruff check packages/ tests/ *> "$receipts/s62-base-ruff.txt"
Write-Output ("base ruff exit={0} receipt={1}/s62-base-ruff.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s62-base-ruff.txt" -Tail 5

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
