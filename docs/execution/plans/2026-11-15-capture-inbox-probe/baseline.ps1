# Session 75 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves that the plan's Status line records Mat's words to execute (S9), that the queue is
# right (S8: MEU-35, MEU-36, MEU-84, MEU-128, MEU-129, MEU-130 and MEU-136 approved, MEU-145 and
# MEU-146 pending, 6aaf9b0 an ancestor of HEAD), copies the capture code and tests this plan edits
# or reads to C:/Temp/av-kit/capture-inbox-probe/row0/ (S2 binds to that content, not to HEAD), and
# that the shapes this plan calls are
# present by name, with this plan's own names and files still absent (S7). Then records HEAD and
# the dirty tree with each dirty path's SHA-256, records every Files Modified and read-only
# target's line endings and SHA-256 in s75-anchors.txt, installs Python from the lock without the
# network, proves ui/ and mcp-server/node_modules match their locks, asserts the pinned FFmpeg
# pair that the suite's real-FFmpeg modules run (S4), captures the base Python, UI, MCP and
# capture Electron runs and ruff, and runs the plan-local selftests. A copy of Session 72's
# (docs/execution/plans/2026-11-14-capture-shapes-steps/baseline.ps1) with the checks changed for
# this plan: no D-n carries the execute words (the Status line alone does), and there are no
# base bakes, never-probe or openapi-delta steps. The base runs' own failures are recorded, not
# fatal: the session gate excuses only the Python ids the base receipt shows failing, and nothing
# else. Every other step is fail-fast. Run from the repository root with PowerShell 7
# (pwsh -NoProfile -File).
#
# docs/proposals/2026-11-10-download-logic-divergence-report.md is hashed, never opened or printed.
# No step reads user data: the capture inbox, its sidecars, the app database or the settings file.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-15): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-capture-inbox-probe'
$receipts = 'C:/Temp/av-kit/capture-inbox-probe'
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\capture-inbox-probe\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# S9: the rows run only on Mat's words at the plan gate. The header's Status line must quote his
# word to execute as USER_EXPLICIT with a date and a quote. Mat's message to the coordinator
# ("proceed with planning and execution ...") is that word once the plan review approves; the
# coordinator writes it into the Status line at the gate.
$ruled = @'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1], "implementation-plan.md").read_text(encoding="utf-8")
status = [ln for ln in text.splitlines() if ln.startswith("> **Status:**")]
line = status[0] if len(status) == 1 else ""
execute = re.search(r"said to execute \(USER_EXPLICIT 2026-\d\d-\d\d '[^']+'\)", line)
print(f"status lines: {len(status)}")
print(f"execute: {execute.group(0) if execute else None}")
ok = bool(line and execute)
if not ok:
    print("the Status line lacks Mat's word to execute (S9); the rows can't run")
sys.exit(0 if ok else 1)
'@
Invoke-Step 'rulings' @('uv', 'run', '--no-sync', 'python', '-c', $ruled, $plan)

# S8: the contract dependencies approved, this session's two MEUs pending, and the planning HEAD
# an ancestor of HEAD. MEU-35 and MEU-36 are the capture service and inbox scan, MEU-84 the
# region view, MEU-128 and MEU-129 the region import and the view frame, MEU-130 the crop and
# MEU-136 the export whose AC-136.7 pin moves.
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
want = {
    "MEU-35": "approved", "MEU-36": "approved", "MEU-84": "approved", "MEU-128": "approved",
    "MEU-129": "approved", "MEU-130": "approved", "MEU-136": "approved",
    "MEU-145": "pending", "MEU-146": "pending",
}
have = {meu: status(meu) for meu in want}
print(f"queue: {have}")
base = subprocess.run(["git", "merge-base", "--is-ancestor", "6aaf9b0", "HEAD"], capture_output=True).returncode
print(f"6aaf9b0 is an ancestor of HEAD: {base == 0}")
sys.exit(0 if have == want and base == 0 else 1)
'@
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue)

# S2 binds to content, not HEAD: Sessions 87 and 75 to 83 share main and may leave work
# uncommitted, so a scoped file that differs from HEAD is reported here, never fatal. Each of
# these files is copied byte for byte to $receipts/row0/<path> (D-908); that copy, with its
# SHA-256 in s75-anchors.txt, is the base every later check and the execution review's delta
# read. What this plan relies on in a file a sibling may also have changed is checked by the
# shapes step below (S7: every named shape present, every new name absent), not by HEAD
# equality. Only the hashes are printed.
$headEqual = @'
import hashlib, pathlib, shutil, subprocess, sys
paths = (
    "packages/infrastructure/src/avkit_infra/capture/adapter.py",
    "packages/core/src/avkit_core/services/capture.py",
    "packages/core/src/avkit_core/ports/capture.py",
    "packages/core/src/avkit_core/domain/capture.py",
    "packages/api/src/avkit_api/routes/captures.py",
    "mcp-server/src/toolsets/capture.ts",
    "mcp-server/src/toolsets/registry.ts",
    "mcp-server/tests/capture.test.ts",
    "tests/unit/test_capture_export_adapter.py",
    "tests/unit/test_capture_export_service.py",
    "tests/unit/test_capture_service.py",
    "tests/unit/test_capture_adapter.py",
    "tests/unit/test_capture_render.py",
    "tests/e2e/test_api_capture_crop.py",
    "ui/tests/e2e/capture-inbox.test.ts",
    "ui/src/renderer/src/features/capture/CaptureViewport.tsx",
    "ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx",
    "ui/src/renderer/src/features/capture/capture-clipboard.ts",
    "ui/src/main/clipboard-image.ts",
    "docs/build-plan/09-screenshot-capture.md",
    "openapi.committed.json",
)
differs = []
row0 = pathlib.Path(sys.argv[1])
# git diff applies the checkout filters, so a CRLF working file whose blob git stores as LF
# reads as unchanged; comparing raw bytes with `git show HEAD:` would call every CRLF file
# changed. A path that is untracked is a difference too.
for rel in paths:
    now = pathlib.Path(rel).read_bytes()
    copy = row0 / rel
    copy.parent.mkdir(parents=True, exist_ok=True)
    # A re-run never keeps a stale copy: the copy is rewritten from the bytes read now.
    copy.write_bytes(now)
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], capture_output=True).returncode == 0
    same = tracked and subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel]).returncode == 0
    print(f"{'same' if same else 'differs'} {hashlib.sha256(now).hexdigest()[:16]} {rel}")
    if not same:
        differs.append(rel)
print("differ from HEAD (reported, not fatal; row0 copies are the base):", differs)
sys.exit(0)
'@

# S7: the names this plan calls, by name, and the names and files it adds, still absent. A shape
# that differs in signature is found when row 1 re-reads its anchors. A row's last field is the
# number of lines it must match. CRLF files read the same: splitlines() drops the CR.
$shapes = @'
import pathlib, re, sys
CORE = "packages/core/src/avkit_core"
WIRE = f"{CORE}/services/capture.py"
ADAPTER = "packages/infrastructure/src/avkit_infra/capture/adapter.py"
ROUTE = "packages/api/src/avkit_api/routes/captures.py"
PORT = f"{CORE}/ports/capture.py"
DOMAIN = f"{CORE}/domain/capture.py"
SERVICE_TEST = "tests/unit/test_capture_service.py"
EXPORT_SERVICE_TEST = "tests/unit/test_capture_export_service.py"
RENDER_TEST = "tests/unit/test_capture_render.py"
MCP_CAPTURE = "mcp-server/src/toolsets/capture.ts"
MCP_TEST = "mcp-server/tests/capture.test.ts"
EXPORT_TEST = "tests/unit/test_capture_export_adapter.py"
CROP_TEST = "tests/e2e/test_api_capture_crop.py"
E2E = "ui/tests/e2e/capture-inbox.test.ts"
SPEC = "docs/build-plan/09-screenshot-capture.md"
present = (
    (ADAPTER, r"^EXIF_ORIENTATION_TAG = 0x0112$", "EXIF_ORIENTATION_TAG", 1),
    (ADAPTER, r'^_UPRIGHT_MODES = frozenset\(\{"RGB", "RGBA", "L", "LA"\}\)$', "_UPRIGHT_MODES", 1),
    (ADAPTER, r"^def _encode_view\(image: Image\.Image, suffix: str\) -> bytes:$", "_encode_view", 1),
    (ADAPTER, r"^    def probe\(self, path: Path\) -> ImageProbe:$", "probe", 1),
    (ADAPTER, r"^    def view\(self, path: Path, frame: ViewFrame\) -> bytes:$", "view", 1),
    (ADAPTER, r"^    def crop\($", "crop", 1),
    (ADAPTER, r"^    def bake\($", "bake", 1),
    (ADAPTER, r"^    def render\(self, original_path: Path, annotations: Sequence\[Annotation\]\) -> bytes:$", "render", 1),
    (ADAPTER, r"^    def export\($", "export", 1),
    (ADAPTER, r"^    def write_upright_png\(", "write_upright_png", 1),
    (ADAPTER, r'^            image\.save\(output_path, format="PNG"\)$', "_write_png's explicit format (STAGED_REBAKE)", 1),
    (ADAPTER, r"^            image\.save\(output_path, format=pil_format, quality=LOSSY_QUALITY\)$", "_write_lossy's explicit format (STAGED_REBAKE)", 1),
    (ADAPTER, r"UnidentifiedImageError", "UnidentifiedImageError uses", 4),
    (ADAPTER, r"# RETURN_UNCHANGED: the whole image at scale 1 is the file itself\.", "RETURN_UNCHANGED", 1),
    (WIRE, r'^log = structlog\.get_logger\(module="capture"\)$', "the capture logger", 1),
    (WIRE, r'^SCAN_EXTENSIONS = \("\.png", "\.jpg", "\.jpeg", "\.webp"\)$', "SCAN_EXTENSIONS", 1),
    (WIRE, r"^    def scan_inbox\(self\) -> list\[CaptureShot\]:$", "scan_inbox", 1),
    (WIRE, r"^                    probe = self\._annotate\.probe\(resolved\)$", "the scan's uncaught probe", 1),
    (WIRE, r"^                    elif existing\.file_size != probe\.file_size:$", "the scan's update test", 1),
    (WIRE, r"^    def register_shot\(", "register_shot", 1),
    (WIRE, r"^    def _import_in_place\(self, resolved: Path\) -> CaptureShot:$", "_import_in_place", 1),
    (WIRE, r"^            if existing\.file_size == probe\.file_size:$", "_import_in_place's early return", 1),
    (WIRE, r"^    def _upsert_shot\($", "_upsert_shot", 1),
    (WIRE, r"existing\.file_size == probe\.file_size and existing\.source == source", "_upsert_shot's early return", 1),
    (WIRE, r"^def parse_sidecar_document\(payload: object\) -> list\[object\]:$", "parse_sidecar_document", 1),
    (WIRE, r"ignoring unknown top-level keys", "the sidecar's unknown-key rule", 1),
    (WIRE, r"^                # RECONCILE \(MEU-84, D-15\)", "the reconcile comment", 1),
    (WIRE, r"^    def annotate_and_save\($", "annotate_and_save", 1),
    (WIRE, r"^    def read_image\(self, shot_id: str, variant: str\) -> bytes:$", "read_image", 1),
    (WIRE, r"^    def _rebake_annotated\($", "_rebake_annotated", 1),
    (WIRE, r"^import os$", "the module's os import (STAGED_REBAKE)", 1),
    (WIRE, r"^                    if child\.name\.lower\(\)\.endswith\(ANNOTATED_SUFFIXES\):$", "the scan's annotated-name skip", 1),
    (WIRE, r"^def annotated_path_for\(original: Path, output_format: AnnotatedFormat\) -> Path:$", "annotated_path_for", 1),
    (WIRE, r"^def _sidecar_for\(original: Path\) -> Path:$", "_sidecar_for", 1),
    (WIRE, r"^    def _unlink_if_file\(self, path: Path \| None\) -> None:$", "_unlink_if_file", 1),
    (DOMAIN, r'^ANNOTATED_EXT: dict\[str, str\] = \{"png": "\.png", "jpeg": "\.jpg", "webp": "\.webp"\}$', "ANNOTATED_EXT", 1),
    (PORT, r"^class ImageAnnotatePort\(Protocol\):$", "ImageAnnotatePort", 1),
    (SERVICE_TEST, r"^class FakeCapturePort:$", "FakeCapturePort", 1),
    (EXPORT_SERVICE_TEST, r"^class FakeAnnotate:$", "FakeAnnotate", 1),
    (RENDER_TEST, r"^    def __getattr__\(self, name: str\) -> object:$", "_RenderingPort's __getattr__", 1),
    (ROUTE, r'^@router\.get\("/\{id\}/image", ', "the image route", 1),
    (ROUTE, r"^    # MEU-128 \(D-411\): with none of x, y, width, height, unit and max_edge, the file's bytes$", "the route's D-411 comment", 1),
    (MCP_TEST, r'\{ action: "list", method: "GET", path: "/captures" \}', "the MCP list pin", 1),
    (EXPORT_TEST, r"^def test_ac_136_7_exif_orientation_is_not_applied\(", "AC-136.7", 1),
    (CROP_TEST, r"^def test_ac_130_21_damaged_source_is_422\(", "AC-130.21", 1),
    (CROP_TEST, r"^        intact = source\.read_bytes\(\)$", "AC-130.21's copy", 1),
    (CROP_TEST, r"^        source\.write_bytes\(intact\)$", "AC-130.21's restore", 1),
    (E2E, r"^async function launchApp\(", "launchApp", 1),
    (E2E, r"^import \{ spawn, type ChildProcess \} from 'node:child_process'$", "the child_process import that gains spawnSync", 1),
    (SPEC, r'^<a id="scan-skips-unreadable-files"></a>$', "09 §Scan skips unreadable files", 1),
    (SPEC, r'^<a id="exif-orientation-on-scan"></a>$', "09 §EXIF orientation on scan", 1),
    (SPEC, r"^> \*\*MEU-145\.\*\*", "09's MEU-145 note", 1),
    (SPEC, r"^> \*\*MEU-146\.\*\*", "09's MEU-146 note", 1),
)
# This plan's names, labels and test titles, absent from every file it writes or reads.
absent_files = (
    ADAPTER, WIRE, ROUTE, MCP_CAPTURE, MCP_TEST, EXPORT_TEST, CROP_TEST, E2E,
    SERVICE_TEST, "tests/unit/test_capture_adapter.py", PORT, EXPORT_SERVICE_TEST, RENDER_TEST,
)
absent = re.compile(
    r"shown_orientation|SHOWN_ORIENTATION_FORMATS|_open_shown|SCAN_SKIPPED_EVENT|"
    r"capture\.scan_skipped|_scan_skipped|AC-145\.|AC-146\.|test_ac_145_|test_ac_146_|"
    r"exif_orientation_is_applied|read_shown|shown_tag|baked_orientation|"
    r"STALE_BAKE_FAILED_EVENT|capture\.stale_bake_failed|_stale_bake_failed|orientation_fixtures|"
    r"_restage_annotated|_recover_restage|_discard_rebake|RecoverResult|STAGED_REBAKE|\.rebake-"
)
spec_absent = re.compile(r"Delivered \(Session 75\)|AC-145\.|AC-146\.")
new_files = (
    "tests/unit/test_capture_scan_unreadable.py",
    "tests/unit/test_capture_orientation.py",
    "tests/e2e/test_api_capture_scan_unreadable.py",
    "tests/e2e/test_api_capture_orientation.py",
    "tests/orientation_fixtures.py",
)
wrong = []
for rel, pattern, label, count in present:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if re.search(pattern, ln)]
    print(f"present {label}: {rel} lines {hits[:5]}")
    if len(hits) != count:
        wrong.append(f"{label}: {len(hits)} match(es), want {count}")
for rel, pattern in [(r, absent) for r in absent_files] + [(SPEC, spec_absent)]:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if pattern.search(ln)]
    print(f"absent names and labels: {rel} lines {hits[:5]}")
    if hits:
        wrong.append(f"already present in {rel}")
for rel in new_files:
    exists = pathlib.Path(rel).exists()
    print(f"absent new file {rel}: exists={exists}")
    if exists:
        wrong.append(f"new file already present {rel}")
print("shapes wrong (S7):", wrong)
sys.exit(1 if wrong else 0)
'@
Invoke-Step 'shapes' @('uv', 'run', '--no-sync', 'python', '-c', $shapes)
# The copies are written only after the shapes step passes: a re-run of row 0 after row 1 stops
# at shapes (the new names exist), so it can never overwrite the row-0 copies with edited content.
Invoke-Step 'row0-copies' @('uv', 'run', '--no-sync', 'python', '-c', $headEqual, "$receipts/row0")

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

# Every Files Modified target's and every read-only file's line endings and SHA-256, which each
# row reads before it writes. A new file is recorded as absent; an existing target that is
# missing stops here. Row 6 reads known-issues.yaml's SHA-256 from this receipt for
# issue-resolve.py --expect-sha256. The divergence report is hashed only.
$anchors = @'
import hashlib, pathlib, sys
targets = (
    "packages/infrastructure/src/avkit_infra/capture/adapter.py",
    "packages/core/src/avkit_core/services/capture.py",
    "packages/core/src/avkit_core/ports/capture.py",
    "packages/api/src/avkit_api/routes/captures.py",
    "tests/unit/test_capture_service.py",
    "tests/unit/test_capture_export_service.py",
    "tests/unit/test_capture_export_adapter.py",
    "tests/e2e/test_api_capture_crop.py",
    "ui/tests/e2e/capture-inbox.test.ts",
    "docs/build-plan/09-screenshot-capture.md",
    ".agent/context/meu-status.yaml",
    "docs/BUILD_PLAN.md",
    ".agent/context/meu-registry.md",
    ".agent/context/known-issues.yaml",
    ".agent/context/known-issues.md",
    ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md",
    "docs/execution/metrics.md",
    ".agent/context/current-focus.md",
    # Read, never changed (the gate's scope-paths refuses a change).
    "packages/core/src/avkit_core/domain/capture.py",
    "mcp-server/src/toolsets/capture.ts",
    "mcp-server/src/toolsets/registry.ts",
    "mcp-server/tests/capture.test.ts",
    "tests/unit/test_capture_adapter.py",
    "tests/unit/test_capture_render.py",
    "ui/src/renderer/src/features/capture/CaptureViewport.tsx",
    "ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx",
    "ui/src/renderer/src/features/capture/capture-clipboard.ts",
    "ui/src/main/clipboard-image.ts",
    "docs/build-plan/build-priority-matrix.md",
    "openapi.committed.json",
)
new = (
    "tests/unit/test_capture_scan_unreadable.py",
    "tests/unit/test_capture_orientation.py",
    "tests/e2e/test_api_capture_scan_unreadable.py",
    "tests/e2e/test_api_capture_orientation.py",
    "tests/orientation_fixtures.py",
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
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', '-c', $anchors, "$receipts/s75-anchors.txt")

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

# S4: the suite's real-FFmpeg modules (Sessions 54, 62 and 67) run this pair; a missing or
# truncated binary stops here. This session adds no real-FFmpeg module.
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

& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE > "$receipts/s75-base-py.txt" 2>&1
Write-Output ("base suite py exit={0} receipt={1}/s75-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s75-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test > "$receipts/s75-base-ui.txt" 2>&1
Write-Output ("base suite ui exit={0} receipt={1}/s75-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s75-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run build > "$receipts/s75-base-mcp-build.txt" 2>&1
Write-Output ("base mcp build exit={0} receipt={1}/s75-base-mcp-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix mcp-server run test > "$receipts/s75-base-mcp.txt" 2>&1
Write-Output ("base suite mcp exit={0} receipt={1}/s75-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s75-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

# The capture Electron spec the gate runs, on a fresh build, so its base count is on record.
& rtk proxy npm --prefix ui run build > "$receipts/s75-base-ui-build.txt" 2>&1
Write-Output ("base ui build exit={0} receipt={1}/s75-base-ui-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts > "$receipts/s75-base-e2e.txt" 2>&1
Write-Output ("base capture e2e exit={0} receipt={1}/s75-base-e2e.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s75-base-e2e.txt" | Select-String -Pattern '^\s+\d+ (passed|failed|skipped|flaky)' | Select-Object -Last 6

& rtk proxy uv run --no-sync ruff check packages/ tests/ > "$receipts/s75-base-ruff.txt" 2>&1
Write-Output ("base ruff exit={0} receipt={1}/s75-base-ruff.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s75-base-ruff.txt" -Tail 5

Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'id-length-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/id-length.py", '--selftest')
Invoke-Step 'issue-resolve-help' @('uv', 'run', '--no-sync', 'python', "$plan/issue-resolve.py", '--help')
Write-Output 'baseline: all steps exit 0'
exit 0
