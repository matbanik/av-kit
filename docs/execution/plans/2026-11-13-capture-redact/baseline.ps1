# Session 68 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves that the plan's Status line records Mat's execution budget and his words to
# execute (S9), that the queue is right (S8: MEU-91, MEU-100 and MEU-142 approved, MEU-103
# pending, 3c5676f an ancestor of HEAD), and that the shapes this plan calls are present by name,
# with this plan's own names and files still absent (S7). Then records HEAD and the dirty tree
# with each dirty path's SHA-256, records every Files Modified target's line endings and SHA-256
# in s68-anchors.txt, installs Python from the lock without the network, proves ui/ and
# mcp-server/node_modules match their locks, asserts the pinned FFmpeg pair that the suite's
# real-FFmpeg modules run (S4), captures the base Python, UI, MCP and capture Electron runs and
# ruff, and runs the plan-local selftests. A copy of Session 67's with the checks changed for this
# plan. The base runs' own failures are recorded, not fatal: the session gate excuses only the
# Python ids the base receipt shows failing, and nothing else. Every other step is fail-fast. Run
# from the repository root with PowerShell 7 (pwsh -NoProfile -File).
#
# docs/proposals/2026-11-10-download-logic-divergence-report.md is hashed, never opened or printed.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-13): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-13-capture-redact'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s68\tmp'
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
# execution budget and his word to execute, each as USER_EXPLICIT with a date and a quote. This
# plan has no Decision Brief, so no decision log entry needs a ruling.
$ruled = @'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1], "implementation-plan.md").read_text(encoding="utf-8")
status = [ln for ln in text.splitlines() if ln.startswith("> **Status:**")]
line = status[0] if len(status) == 1 else ""
budget = re.search(r"execution review budget to [0-9][0-9.,]*M? \(USER_EXPLICIT 2026-\d\d-\d\d '[^']+'\)", line)
execute = re.search(r"said to execute \(USER_EXPLICIT 2026-\d\d-\d\d '[^']+'\)", line)
print(f"status lines: {len(status)}")
print(f"budget: {budget.group(0) if budget else None}")
print(f"execute: {execute.group(0) if execute else None}")
ok = bool(line and budget and execute)
if not ok:
    print("the Status line lacks Mat's budget or his word to execute (S9); the rows can't run")
sys.exit(0 if ok else 1)
'@
Invoke-Step 'rulings' @('uv', 'run', '--no-sync', 'python', '-c', $ruled, $plan)

# S8: the two contract dependencies and Session 67 approved, MEU-103 pending, and Session 67's
# commit an ancestor of HEAD.
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
want = {"MEU-91": "approved", "MEU-100": "approved", "MEU-142": "approved", "MEU-103": "pending"}
have = {meu: status(meu) for meu in want}
print(f"queue: {have}")
s67 = subprocess.run(["git", "merge-base", "--is-ancestor", "3c5676f", "HEAD"], capture_output=True).returncode
print(f"3c5676f is an ancestor of HEAD: {s67 == 0}")
sys.exit(0 if have == want and s67 == 0 else 1)
'@
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue)

# S7: the names this plan calls, by name, and the names and files it adds, still absent. A shape
# that differs in signature is found when row 1 re-reads its anchors.
$shapes = @'
import pathlib, re, sys
CORE = "packages/core/src/avkit_core"
INFRA = "packages/infrastructure/src/avkit_infra"
API = "packages/api/src/avkit_api"
UI = "ui/src/renderer/src/features/capture"
DOMAIN = f"{CORE}/domain/capture.py"
present = (
    (DOMAIN, r"^class EraserAnnotation:$", "EraserAnnotation"),
    (DOMAIN, r"^Annotation = \($", "the Annotation union"),
    (DOMAIN, r"^def clip_mark\($", "clip_mark"),
    (DOMAIN, r"^        case EraserAnnotation\(\):$", "clip_mark's eraser case"),
    (DOMAIN, r"^            assert_never\(mark\)$", "clip_mark's assert_never"),
    (DOMAIN, r"^_HalfOpenMark = TypeVar\($", "_HalfOpenMark"),
    (DOMAIN, r"^def _clip_half_open\($", "_clip_half_open"),
    (DOMAIN, r"^def _require_color\(", "_require_color"),
    (f"{CORE}/domain/enums.py", r'^    Eraser = "Eraser"$', "AnnotationType.Eraser"),
    (f"{CORE}/services/capture.py", r"^def _annotation_from_wire\(item: object\) -> Annotation:$", "_annotation_from_wire"),
    (f"{CORE}/services/capture.py", r"^def _annotation_to_wire\(annotation: Annotation\) -> dict\[str, object\]:$", "_annotation_to_wire"),
    (f"{CORE}/services/capture.py", r"^    def _clamp_annotation\($", "_clamp_annotation"),
    (f"{INFRA}/capture/adapter.py", r"^def region_clip\($", "region_clip"),
    (f"{INFRA}/capture/adapter.py", r"^def apply_region_pass\(canvas: Image\.Image, annotations: Sequence\[Annotation\]\) -> Image\.Image:$", "apply_region_pass"),
    (f"{INFRA}/capture/adapter.py", r"^    def _apply\(self, canvas: Image\.Image, annotation: Annotation\) -> Image\.Image:$", "the adapter's _apply"),
    (f"{INFRA}/capture/adapter.py", r"^def _color_rgb\(color: str\) -> tuple\[int, int, int\]:$", "_color_rgb"),
    (f"{API}/schemas/captures.py", r"^class EraserAnnotationIn\(ApiModel\):$", "EraserAnnotationIn"),
    (f"{API}/schemas/captures.py", r"^AnnotationIn = Annotated\[$", "the AnnotationIn union"),
    (f"{API}/routes/captures.py", r"^def _annotations_from_in\(items: list\[AnnotationIn\]\) -> list\[Annotation\]:$", "_annotations_from_in"),
    ("mcp-server/src/toolsets/capture.ts", r"^const eraserAnn = z$", "the MCP eraserAnn"),
    ("mcp-server/src/toolsets/capture.ts", r'^const annotation = z\.discriminatedUnion\("type", \[$', "the MCP annotation union"),
    (f"{UI}/capture-annotate.ts", r"z\.discriminatedUnion\('type', \[arrowSchema, rectSchema, highlightSchema, textSchema, pixelateSchema, eraserSchema\]\),$", "the UI annotate union"),
    (f"{UI}/capture-region-pass.ts", r"^export type RegionMark = Extract<Annotation, \{ type: 'pixelate' \| 'eraser' \}>$", "RegionMark"),
    (f"{UI}/capture-region-pass.ts", r"^export function applyRegionPass\(", "applyRegionPass"),
    (f"{UI}/capture-transform.ts", r"^export type BoxMark = Extract<Annotation, \{ type: 'rect' \| 'highlight' \| 'pixelate' \| 'eraser' \}>$", "BoxMark"),
    (f"{UI}/CaptureViewport.tsx", r"^export type CaptureTool = 'select' \| 'arrow' \| 'box' \| 'highlight' \| 'text' \| 'pixelate' \| 'eraser' \| 'crop'$", "CaptureTool"),
    (f"{UI}/capture-toolbar.ts", r"^  'capture-tool-pixelate': \{ icon: Grid3x3, name: 'Pixelate' \},$", "the Pixelate button"),
    (f"{UI}/capture-toolbar.ts", r"^  'capture-tool-eraser': \{ icon: Eraser, name: 'Eraser' \},$", "the Eraser button"),
    (f"{UI}/capture-toolbar.ts", r"^export type OptionGroup = 'color' \| 'stroke' \| 'text' \| 'block'$", "OptionGroup"),
    (f"{UI}/ToolbarIconButton.tsx", r"^  const label = shortcut === undefined \? name : `\$\{name\} \(\$\{shortcut\}\)`$", "the icon button label"),
    (f"{UI}/capture-help-content.ts", r"Pixelate and Eraser change the pixels under them", "the help body's region sentence"),
    ("tools/capture_bake_fixture.py", r"^        \*crop_cases\(\),$", "the fixture's crop cases"),
    ("ui/tests/e2e/test-ids.ts", r"^// MEU-51 primitive harness IDs\.", "the AC-51.6 hash boundary"),
    ("ui/tests/e2e/test-ids.ts", r"^export const CAPTURE_TOOL_PIXELATE = 'capture-tool-pixelate'$", "CAPTURE_TOOL_PIXELATE"),
    ("docs/build-plan/09-screenshot-capture.md", r"^### Redact mark", "09 §Redact mark"),
    ("docs/build-plan/gui-actions-index.md", r"^\| `capture:tool_pixelate` \| Pixelate tool \|", "the gui index pixelate row"),
)
# 'redact' in any capture file this plan writes (case-insensitive), and the rename's text.
absent_files = (
    DOMAIN, f"{CORE}/domain/enums.py", f"{CORE}/services/capture.py", f"{INFRA}/capture/adapter.py",
    f"{API}/schemas/captures.py", f"{API}/routes/captures.py", "openapi.committed.json",
    "mcp-server/src/toolsets/capture.ts", f"{UI}/capture-annotate.ts", f"{UI}/capture-region-pass.ts",
    f"{UI}/CaptureViewport.tsx", f"{UI}/capture-toolbar.ts", f"{UI}/ToolbarIconButton.tsx",
    f"{UI}/CapturePage.tsx", f"{UI}/capture-hit-test.ts", f"{UI}/capture-transform.ts",
    f"{UI}/capture-help-content.ts", "ui/tests/e2e/test-ids.ts", "tools/capture_bake_fixture.py",
    "ui/tests/e2e/fixtures/capture-region-pass.json", "docs/build-plan/gui-actions-index.md",
)
absent = re.compile(r"(?i)redact|smart eraser")
new_files = (
    "tests/unit/test_capture_redact.py",
    "tests/e2e/test_api_capture_redact.py",
    "ui/tests/unit/capture-redact.behavior.test.ts",
)
wrong = []
for rel, pattern, label in present:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if re.search(pattern, ln)]
    print(f"present {label}: {rel} lines {hits[:5]}")
    if len(hits) != 1:
        wrong.append(f"{label}: {len(hits)} match(es), want 1")
for rel in absent_files:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if absent.search(ln)]
    print(f"absent redact/Smart eraser: {rel} lines {hits[:5]}")
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
# keeps each line's own ending (S63 RULE-3). The two files dirty at plan time (09 and the
# grouping) are recorded here too; rows byte-edit them. The divergence report is hashed only.
$anchors = @'
import hashlib, pathlib, sys
targets = (
    "packages/core/src/avkit_core/domain/enums.py",
    "packages/core/src/avkit_core/domain/capture.py",
    "packages/core/src/avkit_core/services/capture.py",
    "packages/infrastructure/src/avkit_infra/capture/adapter.py",
    "packages/api/src/avkit_api/schemas/captures.py",
    "packages/api/src/avkit_api/routes/captures.py",
    "openapi.committed.json",
    "tools/capture_bake_fixture.py",
    "mcp-server/src/toolsets/capture.ts",
    "mcp-server/tests/capture.test.ts",
    "ui/src/renderer/src/features/capture/capture-annotate.ts",
    "ui/src/renderer/src/features/capture/capture-region-pass.ts",
    "ui/src/renderer/src/features/capture/CaptureViewport.tsx",
    "ui/src/renderer/src/features/capture/capture-toolbar.ts",
    "ui/src/renderer/src/features/capture/ToolbarIconButton.tsx",
    "ui/src/renderer/src/features/capture/CapturePage.tsx",
    "ui/src/renderer/src/features/capture/capture-hit-test.ts",
    "ui/src/renderer/src/features/capture/capture-transform.ts",
    "ui/src/renderer/src/features/capture/capture-help-content.ts",
    "ui/tests/e2e/test-ids.ts",
    "ui/tests/e2e/capture-inbox.test.ts",
    "ui/tests/e2e/fixtures/capture-region-pass.json",
    "ui/tests/unit/capture-region-pass.test.ts",
    "ui/tests/unit/capture-toolbar.test.ts",
    "ui/tests/unit/icon-hints.test.ts",
    "ui/tests/unit/capture-page.behavior.test.ts",
    "ui/tests/unit/capture-page.test.ts",
    "ui/tests/unit/capture-hit-test.test.ts",
    "ui/tests/unit/capture-help-content.test.ts",
    "ui/tests/unit/capture-crop-tool.behavior.test.ts",
    "tests/unit/test_domain.py",
    "tests/unit/test_domain_capture.py",
    "tests/unit/test_capture_service.py",
    "docs/build-plan/09-screenshot-capture.md",
    "docs/build-plan/06-gui.md",
    "docs/build-plan/gui-actions-index.md",
    ".agent/context/meu-status.yaml",
    "docs/BUILD_PLAN.md",
    ".agent/context/meu-registry.md",
    ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md",
)
new = (
    "tests/unit/test_capture_redact.py",
    "tests/e2e/test_api_capture_redact.py",
    "ui/tests/unit/capture-redact.behavior.test.ts",
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
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', '-c', $anchors, "$receipts/s68-anchors.txt")

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

& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE > "$receipts/s68-base-py.txt" 2>&1
Write-Output ("base suite py exit={0} receipt={1}/s68-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s68-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test > "$receipts/s68-base-ui.txt" 2>&1
Write-Output ("base suite ui exit={0} receipt={1}/s68-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s68-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run build > "$receipts/s68-base-mcp-build.txt" 2>&1
Write-Output ("base mcp build exit={0} receipt={1}/s68-base-mcp-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix mcp-server run test > "$receipts/s68-base-mcp.txt" 2>&1
Write-Output ("base suite mcp exit={0} receipt={1}/s68-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s68-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

# The capture Electron spec the gate runs, on a fresh build, so its base count is on record.
& rtk proxy npm --prefix ui run build > "$receipts/s68-base-ui-build.txt" 2>&1
Write-Output ("base ui build exit={0} receipt={1}/s68-base-ui-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts > "$receipts/s68-base-e2e.txt" 2>&1
Write-Output ("base capture e2e exit={0} receipt={1}/s68-base-e2e.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s68-base-e2e.txt" | Select-String -Pattern '^\s+\d+ (passed|failed|skipped|flaky)' | Select-Object -Last 6

& rtk proxy uv run --no-sync ruff check packages/ tests/ tools/ > "$receipts/s68-base-ruff.txt" 2>&1
Write-Output ("base ruff exit={0} receipt={1}/s68-base-ruff.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s68-base-ruff.txt" -Tail 5

Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'id-length-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/id-length.py", '--selftest')
Invoke-Step 'never-probe-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/assert-never-probe.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
