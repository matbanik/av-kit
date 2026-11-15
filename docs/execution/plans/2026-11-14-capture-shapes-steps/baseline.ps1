# Session 72 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves that the plan's Status line records Mat's words to execute and that D-782 carries
# them (S9; the review loops have no token budget, so none is quoted), that the queue is right
# (S8: MEU-100, MEU-105 and MEU-143 approved, MEU-106 and MEU-107 pending, 5db3623 an ancestor
# of HEAD), and that the shapes this plan calls are present by name, with this plan's own names
# and files still absent (S7). Then records HEAD and the dirty tree with each dirty path's
# SHA-256, records every Files Modified target's line endings and SHA-256 in s72-anchors.txt,
# records the base adapter's "end" arrow and "rect" bakes on AC-106.8's and AC-106.11's inputs
# in s72-base-bakes.txt, installs Python from the lock without the network, proves ui/ and
# mcp-server/node_modules match their locks, asserts the pinned FFmpeg pair that the suite's
# real-FFmpeg modules run (S4), captures the base Python, UI, MCP and capture Electron runs and
# ruff, and runs the plan-local selftests. A copy of Session 71b's with the checks changed for
# this plan. The base runs' own failures are recorded, not fatal: the session gate excuses only
# the Python ids the base receipt shows failing, and nothing else. Every other step is
# fail-fast. Run from the repository root with PowerShell 7 (pwsh -NoProfile -File).
#
# docs/proposals/2026-11-10-download-logic-divergence-report.md is hashed, never opened or printed.
# No step reads user data: the capture inbox, its sidecars, the app database or the settings file.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-14): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-14-capture-shapes-steps'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s72\tmp'
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
# word to execute as USER_EXPLICIT with a date and a quote, and D-782 must carry the same ruling.
$ruled = @'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1], "implementation-plan.md").read_text(encoding="utf-8")
status = [ln for ln in text.splitlines() if ln.startswith("> **Status:**")]
line = status[0] if len(status) == 1 else ""
execute = re.search(r"said to execute \(USER_EXPLICIT 2026-\d\d-\d\d '[^']+'\)", line)
start = text.find("  - id: D-782\n")
end = text.find("```", start)
d782 = text[start:end] if 0 <= start < end else ""
ref = re.search(r"human_message_reference: \"(USER_EXPLICIT 2026-\d\d-\d\d '[^']+')\"", d782)
ruled = "resolution: human" in d782 and ref is not None
same = bool(execute and ref and ref.group(1) in execute.group(0))
print(f"status lines: {len(status)}")
print(f"execute: {execute.group(0) if execute else None}")
print(f"D-782 ruled by Mat: {ruled}; the same words as the Status line: {same}")
ok = bool(line and execute and ruled and same)
if not ok:
    print("the Status line lacks Mat's word to execute, or D-782 lacks the same ruling (S9); the rows can't run")
sys.exit(0 if ok else 1)
'@
Invoke-Step 'rulings' @('uv', 'run', '--no-sync', 'python', '-c', $ruled, $plan)

# S8: the contract dependencies (MEU-100's toolbar and handles, MEU-105's style store, MEU-143's
# tool flow) approved, this session's two MEUs pending, and Session 71b's commit an ancestor of
# HEAD.
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
want = {"MEU-100": "approved", "MEU-105": "approved", "MEU-143": "approved", "MEU-106": "pending", "MEU-107": "pending"}
have = {meu: status(meu) for meu in want}
print(f"queue: {have}")
base = subprocess.run(["git", "merge-base", "--is-ancestor", "5db3623", "HEAD"], capture_output=True).returncode
print(f"5db3623 is an ancestor of HEAD: {base == 0}")
sys.exit(0 if have == want and base == 0 else 1)
'@
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue)

# S7: the names this plan calls, by name, and the names and files it adds, still absent. A shape
# that differs in signature is found when row 1 re-reads its anchors. A row's last field is the
# number of lines it must match.
$shapes = @'
import pathlib, re, sys
CORE = "packages/core/src/avkit_core"
API = "packages/api/src/avkit_api"
UI = "ui/src/renderer/src/features/capture"
REG = "ui/src/renderer/src/registry"
DOMAIN = f"{CORE}/domain/capture.py"
ENUMS = f"{CORE}/domain/enums.py"
WIRE = f"{CORE}/services/capture.py"
SERVICE = f"{CORE}/services/settings.py"
ADAPTER = "packages/infrastructure/src/avkit_infra/capture/adapter.py"
CAPTURES_IN = f"{API}/schemas/captures.py"
ROUTE = f"{API}/routes/captures.py"
SCHEMA = f"{API}/schemas/settings.py"
MCP_CAPTURE = "mcp-server/src/toolsets/capture.ts"
MCP = "mcp-server/src/toolsets/settings.ts"
ANNOTATE = f"{UI}/capture-annotate.ts"
PUT = "ui/src/renderer/src/features/settings/settings-schemas.ts"
STYLE = f"{UI}/capture-tool-style.ts"
TOOLBAR = f"{UI}/capture-toolbar.ts"
HIT = f"{UI}/capture-hit-test.ts"
TRANSFORM = f"{UI}/capture-transform.ts"
HEADS = f"{UI}/capture-arrow-head.ts"
COMMANDS = f"{UI}/capture-commands.ts"
VIEWPORT = f"{UI}/CaptureViewport.tsx"
PAGE = f"{UI}/CapturePage.tsx"
HELP = f"{UI}/capture-help-content.ts"
SHORTCUTS = f"{REG}/shortcuts.ts"
REGISTRY = f"{REG}/commandRegistry.ts"
IDS = "ui/tests/e2e/test-ids.ts"
INDEX = "docs/build-plan/gui-actions-index.md"
SPEC = "docs/build-plan/09-screenshot-capture.md"
present = (
    (DOMAIN, r"^class ArrowAnnotation:$", "ArrowAnnotation", 1),
    (DOMAIN, r"^class RectAnnotation:$", "RectAnnotation", 1),
    (DOMAIN, r"^class TextAnnotation:$", "TextAnnotation", 1),
    (DOMAIN, r"^def clip_mark\($", "clip_mark", 1),
    (DOMAIN, r"^def _clip_arrow\($", "_clip_arrow", 1),
    (DOMAIN, r"^def _clip_rect\($", "_clip_rect", 1),
    (DOMAIN, r"^def _clip_text\($", "_clip_text", 1),
    (DOMAIN, r"^\s+assert_never\(mark\)$", "clip_mark's assert_never", 1),
    (WIRE, r"^def _annotation_from_wire\(item: object\) -> Annotation:$", "_annotation_from_wire", 1),
    (WIRE, r"^def _annotation_to_wire\(annotation: Annotation\) -> dict\[str, object\]:$", "_annotation_to_wire", 1),
    (WIRE, r"^    def _clamp_annotation\($", "_clamp_annotation", 1),
    (WIRE, r"unexpected redact field\(s\)", "the redact field refusal", 1),
    (ADAPTER, r"^SUPERSAMPLE = 4$", "SUPERSAMPLE", 1),
    (ADAPTER, r"^def arrowhead_vertices\($", "arrowhead_vertices", 1),
    (ADAPTER, r"^def arrow_shaft_end\($", "arrow_shaft_end", 1),
    (ADAPTER, r"^def _load_font\(font_size: int\)", "_load_font", 1),
    (ADAPTER, r"^    def _apply_arrow\(self, canvas: Image\.Image, annotation: ArrowAnnotation\) -> Image\.Image:$", "_apply_arrow", 1),
    (ADAPTER, r"^    def _apply_rect\(self, canvas: Image\.Image, annotation: RectAnnotation\) -> Image\.Image:$", "_apply_rect", 1),
    (CAPTURES_IN, r"^class ArrowAnnotationIn\(ApiModel\):$", "ArrowAnnotationIn", 1),
    (CAPTURES_IN, r"^class RectAnnotationIn\(ApiModel\):$", "RectAnnotationIn", 1),
    (CAPTURES_IN, r"^class RedactAnnotationIn\(ApiModel\):$", "RedactAnnotationIn", 1),
    (CAPTURES_IN, r"^AnnotationIn = Annotated\[$", "AnnotationIn", 1),
    (ROUTE, r"^def _annotations_from_in\(items: list\[AnnotationIn\]\) -> list\[Annotation\]:$", "_annotations_from_in", 1),
    (SERVICE, r'^    \("capture", "tool_lock"\): SettingSpec\("boolean", True\),$', "the tool_lock row", 1),
    (SCHEMA, r"^    tool_lock: StrictBool \| None = None$", "SettingsPutIn.tool_lock", 1),
    (MCP_CAPTURE, r"^const arrowAnn = z$", "arrowAnn", 1),
    (MCP_CAPTURE, r"^const rectAnn = z$", "rectAnn", 1),
    (MCP_CAPTURE, r"^const redactAnn = z$", "redactAnn", 1),
    (MCP, r'^      tool_lock: \{ type: "boolean", default: true \},$', "SETTINGS_SCHEMA's tool_lock", 1),
    (MCP, r"^  tool_lock: z\.boolean\(\)\.optional\(\),$", "settingsLeaves' tool_lock", 1),
    (ANNOTATE, r"^export const annotateInSchema = z$", "annotateInSchema", 1),
    (PUT, r"^export const captureStylePutSchema = z$", "captureStylePutSchema", 1),
    (STYLE, r"^export const TOOL_STYLE_LEAVES: ", "TOOL_STYLE_LEAVES", 1),
    (STYLE, r"^const NUMBER_RANGE: ", "NUMBER_RANGE", 1),
    (STYLE, r"^export function styleToolFor\(tool: CaptureTool, mode: RedactMode\): StyleTool \| null \{$", "styleToolFor", 1),
    (STYLE, r"^export function styleToolOfMark\(mark: Annotation\): StyleTool \| null \{$", "styleToolOfMark", 1),
    (TOOLBAR, r"^export const TOOL_BUTTON_IDS: Readonly<Record<CaptureTool, ToolbarButtonId>> = \{$", "TOOL_BUTTON_IDS", 1),
    (TOOLBAR, r"^export const TOOL_LETTERS: Readonly<Record<CaptureTool, string>> = \{$", "TOOL_LETTERS", 1),
    (TOOLBAR, r"^function strokeApplies\(tool: CaptureTool, selected: Annotation \| null\): boolean \{$", "strokeApplies", 1),
    (TOOLBAR, r"^export function optionGroups\($", "optionGroups", 1),
    (HIT, r"^function hitBody\(mark: Annotation, input: HitTestInput\): boolean \{$", "hitBody", 1),
    (HIT, r"^export function translateBody<T extends Annotation>\($", "translateBody", 1),
    (HIT, r"^export function markLabel\(mark: Annotation, index: number\): string \{$", "markLabel", 1),
    (TRANSFORM, r"^export function isBoxMark\(mark: Annotation\): mark is BoxMark \{$", "isBoxMark", 1),
    (PAGE, r"^function createDrawnMark\($", "createDrawnMark", 1),
    (PAGE, r"^function historyOwnsFocus\(\): boolean \{$", "historyOwnsFocus", 1),
    (COMMANDS, r"^export const CAPTURE_EVENTS = \{$", "CAPTURE_EVENTS", 1),
    (REGISTRY, r"^export const CAPTURE_TOOL_IDS = \[$", "CAPTURE_TOOL_IDS", 1),
    (REGISTRY, r"^    id: 'capture:tool_crop',$", "the capture:tool_crop entry", 1),
    (SHORTCUTS, r"^export const RESERVED_CHORDS: ReadonlySet<string> = new Set\(\[$", "RESERVED_CHORDS", 1),
    (HELP, r"Six annotation tools: Arrow, Box, Highlight and Text draw on the selected shot;", "the Six annotation tools sentence", 1),
    (HELP, r"box, highlight, redact, pixelate or eraser", "the resize sentence", 1),
    (INDEX, r"^\| `capture:tool_eraser` \|", "capture:tool_eraser", 1),
    (INDEX, r"^\| `capture:style_tool` \|", "capture:style_tool", 1),
    (INDEX, r"^\| `capture:redo` \|", "capture:redo", 1),
    (IDS, r"^// MEU-51 primitive harness IDs\.", "the AC-51.6 hash boundary", 1),
    (IDS, r"^// MEU-105 Capture style \(additive IDs\)\.$", "the MEU-105 test-id block", 1),
    (SPEC, r'^<a id="line-and-ellipse"></a>$', "09 §Line and ellipse", 1),
    (SPEC, r'^<a id="step-mark"></a>$', "09 §Step mark", 1),
    (SPEC, r"^> \*\*MEU-106\.\*\* Synthesis slice 7", "09's MEU-106 note", 1),
    (SPEC, r"^> \*\*MEU-107\.\*\* Synthesis slice 8", "09's MEU-107 note", 1),
)
# This plan's names, keys, labels and files, absent from every file it writes. 09's rule rows
# already name the contract (Ctrl+D, step), so 09 is checked for the Delivered note only.
absent_files = (
    DOMAIN, ENUMS, WIRE, SERVICE, ADAPTER, CAPTURES_IN, ROUTE, SCHEMA, MCP_CAPTURE, MCP, ANNOTATE,
    PUT, STYLE, TOOLBAR, HIT, TRANSFORM, HEADS, COMMANDS, VIEWPORT, PAGE, HELP, SHORTCUTS,
    REGISTRY, IDS, INDEX, "openapi.committed.json", "mcp-server/tests/capture.test.ts",
    "tests/unit/test_capture_service.py", "ui/tests/e2e/capture-inbox.test.ts",
    "ui/tests/e2e/fixtures/capture-geometry.json", "ui/tests/unit/capture-help-content.test.ts",
)
absent = re.compile(
    r"StepAnnotation|AnnotationType\.Step|\bstepAnn\b|step_badge_layout|step_text_color|"
    r"arrow_shaft_span|arrowShaftSpan|_clip_ellipse|_clip_step|shapeOption|duplicateMark|"
    r"nextStepNumber|LetterTool|CAPTURE_EDIT_IDS|step_color|step_size|capture:duplicate|"
    r"capture:tool_step|capture-tool-step|Ctrl\+D\b|Seven annotation tools|"
    r"Step numbers stop at 999|AC-106\.|AC-107\."
)
spec_absent = re.compile(r"Delivered \(Session 72\)|AC-106\.|AC-107\.")
new_files = (
    f"{UI}/capture-shapes.ts",
    f"{UI}/capture-step.ts",
    "tests/unit/test_capture_shapes.py",
    "tests/unit/test_capture_step.py",
    "tests/e2e/test_api_capture_shapes.py",
    "tests/e2e/test_api_capture_step.py",
    "ui/tests/unit/capture-shapes.test.ts",
    "ui/tests/unit/capture-shapes.behavior.test.ts",
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
# keeps each line's own ending (S63 RULE-3). Rows 5 and 6 and H2 byte-edit the actions index, 09,
# meu-status, the build plan, the registry and the grouping. The divergence report is hashed only.
$anchors = @'
import hashlib, pathlib, sys
UI = "ui/src/renderer/src/features/capture"
REG = "ui/src/renderer/src/registry"
targets = (
    "packages/core/src/avkit_core/domain/capture.py",
    "packages/core/src/avkit_core/domain/enums.py",
    "packages/core/src/avkit_core/services/capture.py",
    "packages/core/src/avkit_core/services/settings.py",
    "packages/infrastructure/src/avkit_infra/capture/adapter.py",
    "packages/api/src/avkit_api/schemas/captures.py",
    "packages/api/src/avkit_api/routes/captures.py",
    "packages/api/src/avkit_api/schemas/settings.py",
    "openapi.committed.json",
    "mcp-server/src/toolsets/capture.ts",
    "mcp-server/src/toolsets/settings.ts",
    f"{UI}/capture-annotate.ts",
    f"{UI}/capture-arrow-head.ts",
    f"{UI}/capture-hit-test.ts",
    f"{UI}/capture-transform.ts",
    f"{UI}/capture-tool-style.ts",
    f"{UI}/capture-toolbar.ts",
    f"{UI}/capture-commands.ts",
    "ui/src/renderer/src/features/settings/settings-schemas.ts",
    f"{REG}/commandRegistry.ts",
    f"{UI}/CaptureViewport.tsx",
    f"{UI}/CapturePage.tsx",
    f"{UI}/capture-help-content.ts",
    "ui/tests/e2e/test-ids.ts",
    "ui/tests/e2e/fixtures/capture-geometry.json",
    "ui/tests/e2e/capture-inbox.test.ts",
    "ui/tests/unit/fixtures/chord-table.ts",
    "ui/tests/unit/capture-arrow-head.test.ts",
    "ui/tests/unit/capture-redact.behavior.test.ts",
    "ui/tests/unit/capture-help-content.test.ts",
    "ui/tests/unit/capture-tool-lock.test.ts",
    "ui/tests/unit/capture-tool-flow.behavior.test.ts",
    "ui/tests/unit/capture-style-flow.behavior.test.ts",
    "ui/tests/unit/capture-action-row.test.ts",
    "ui/tests/unit/shortcuts.test.ts",
    "ui/tests/unit/common-shortcuts.test.tsx",
    "ui/tests/unit/gui-actions-audit.test.ts",
    "tests/unit/test_domain.py",
    "tests/unit/test_domain_capture.py",
    "tests/unit/test_capture_service.py",
    "tests/unit/test_capture_adapter.py",
    "tests/unit/test_capture_style_settings.py",
    "tests/unit/test_capture_tool_lock.py",
    "mcp-server/tests/capture.test.ts",
    "docs/build-plan/gui-actions-index.md",
    "docs/build-plan/09-screenshot-capture.md",
    ".agent/context/meu-status.yaml",
    "docs/BUILD_PLAN.md",
    ".agent/context/meu-registry.md",
    ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md",
    "docs/execution/metrics.md",
    ".agent/context/current-focus.md",
)
new = (
    f"{UI}/capture-shapes.ts",
    f"{UI}/capture-step.ts",
    "tests/unit/test_capture_shapes.py",
    "tests/unit/test_capture_step.py",
    "tests/e2e/test_api_capture_shapes.py",
    "tests/e2e/test_api_capture_step.py",
    "ui/tests/unit/capture-shapes.test.ts",
    "ui/tests/unit/capture-shapes.behavior.test.ts",
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
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', '-c', $anchors, "$receipts/s72-anchors.txt")

# AC-106.8 and AC-106.30: the base adapter's "end" arrow and "rect" bakes, which the new adapter
# must reproduce exactly when head and shape take their defaults. The hash is over the baked RGB
# pixels (render's PNG decoded), so a PNG encoder setting can't move it. The marks are #FF0000
# on white, on AC-106.8's and AC-106.11's geometry; row 3 writes these hashes into AC-106.8 and
# AC-106.30 as literals, with the same inputs.
$bakes = @'
import hashlib, io, pathlib, sys, tempfile
from PIL import Image
from avkit_core.domain.capture import ArrowAnnotation, RectAnnotation
from avkit_infra.capture.adapter import CaptureAdapter
cases = (
    ("end-arrow", (120, 60), ArrowAnnotation(from_xy=(10, 30), to_xy=(110, 30), color="#FF0000", stroke_width=3)),
    ("rect", (80, 60), RectAnnotation(x=10, y=10, width=60, height=40, color="#FF0000", stroke_width=3)),
)
out = []
with tempfile.TemporaryDirectory(dir=sys.argv[2]) as tmp:
    for name, size, mark in cases:
        src = pathlib.Path(tmp, f"{name}.png")
        Image.new("RGB", size, "white").save(src)
        png = CaptureAdapter(platform="win32").render(src, [mark])
        with Image.open(io.BytesIO(png)) as baked:
            pixels = baked.convert("RGB").tobytes()
        out.append(f"{hashlib.sha256(pixels).hexdigest()} {size[0]}x{size[1]} {name} {mark!r}")
pathlib.Path(sys.argv[1]).write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
'@
Invoke-Step 'base-bakes' @('uv', 'run', '--no-sync', 'python', '-c', $bakes, "$receipts/s72-base-bakes.txt", $tmp)

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

& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE > "$receipts/s72-base-py.txt" 2>&1
Write-Output ("base suite py exit={0} receipt={1}/s72-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s72-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test > "$receipts/s72-base-ui.txt" 2>&1
Write-Output ("base suite ui exit={0} receipt={1}/s72-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s72-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run build > "$receipts/s72-base-mcp-build.txt" 2>&1
Write-Output ("base mcp build exit={0} receipt={1}/s72-base-mcp-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix mcp-server run test > "$receipts/s72-base-mcp.txt" 2>&1
Write-Output ("base suite mcp exit={0} receipt={1}/s72-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s72-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

# The capture Electron spec the gate runs, on a fresh build, so its base count is on record.
& rtk proxy npm --prefix ui run build > "$receipts/s72-base-ui-build.txt" 2>&1
Write-Output ("base ui build exit={0} receipt={1}/s72-base-ui-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts > "$receipts/s72-base-e2e.txt" 2>&1
Write-Output ("base capture e2e exit={0} receipt={1}/s72-base-e2e.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s72-base-e2e.txt" | Select-String -Pattern '^\s+\d+ (passed|failed|skipped|flaky)' | Select-Object -Last 6

& rtk proxy uv run --no-sync ruff check packages/ tests/ > "$receipts/s72-base-ruff.txt" 2>&1
Write-Output ("base ruff exit={0} receipt={1}/s72-base-ruff.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s72-base-ruff.txt" -Tail 5

Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'id-length-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/id-length.py", '--selftest')
Invoke-Step 'never-probe-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/assert-never-probe.py", '--selftest')
Invoke-Step 'openapi-delta-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/openapi-delta.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
