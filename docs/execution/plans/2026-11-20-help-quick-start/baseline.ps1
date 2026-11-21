# Session 99 help-quick-start baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-17-ui-small-fixes/baseline.ps1, with the newer form of
# docs/execution/plans/2026-11-19-e2e-host-parity/baseline.ps1. Its steps:
# 1. uv sync --frozen --offline --all-packages (S7 on a held file);
# 2. the record: HEAD (recorded, never compared with a pinned commit), git status and git
#    worktree list; baseline.sha and baseline-dirty.txt; baseline-scope.json over §Files Modified
#    (each existing path by hash, each new path absent), the "Read, never changed" files (hash)
#    and the files av-kit-c4 may also write (shared, no hash); baseline-dirty-hashes.json, which
#    binds every dirty path outside this scope by hash; the row-0 copies under D/baseline-copies
#    (eol-check.py's base); baseline-skip-hashes.json over packages/ and mcp-server/;
#    baseline-eol.json; baseline-pins.json (the §Test pins files' hashes and each content
#    module's ordered topics and pinned bodies); baseline-citations.txt (each §Verification Plan 1
#    step 4 anchor found once by text, and each draft step target found as a test id); the free
#    ids (MEU-162, matrix 6.23, help-quick-start-residual, D-1289 to D-1298);
# 3. one host-load sample (host-wait.py; the 50 % limit);
# 4. the base Vitest receipt (pwsh in ui/) and the base tests/tooling pytest receipt, failures
#    recorded, not fatal;
# 5. the plan-local checkers' selftests, eol-check.py over the fresh copies, and ruff on this
#    folder's Python (Session 82 RULE-1).
# Every step except 4 is fail-fast. The scope walk drops .mcp.json, mcp-token.txt, .claude.json,
# .env, .claude/settings.local.json and .agent/fleet/hub before any stat or read. Run from the
# repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-20-help-quick-start'
$receipts = 'C:/Temp/av-kit/help-quick-start'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\help-quick-start\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 2. The record, in Python so every file is read and written as bytes.
$record = @'
import hashlib, json, pathlib, re, subprocess, sys

import yaml

PLAN = pathlib.Path("docs/execution/plans/2026-11-20-help-quick-start")
OUT = pathlib.Path("C:/Temp/av-kit/help-quick-start")
COPIES = OUT / "baseline-copies"
R = "ui/src/renderer/src"
F = f"{R}/features"
E2E = "ui/tests/e2e"
HANDOFF = ".agent/context/handoffs/2026-11-20-help-quick-start-MEU-162-handoff.md"
IMPL_REVIEW = ".agent/context/handoffs/2026-11-20-help-quick-start-implementation-critical-review.md"
PLAN_REVIEW = ".agent/context/handoffs/2026-11-20-help-quick-start-plan-critical-review.md"
REFLECTION = "docs/execution/reflections/2026-11-20-help-quick-start-reflection.md"
MEU_STATUS = ".agent/context/meu-status.yaml"
MATRIX = "docs/build-plan/build-priority-matrix.md"
GUI = "docs/build-plan/06-gui.md"
HELP_CARD = f"{R}/components/help/HelpCard.tsx"
TEST_IDS = f"{E2E}/test-ids.ts"
PACKAGE = "ui/package.json"
ELECTRON_APP = f"{E2E}/electron-app.ts"
MODULES = {
    "downloader": f"{F}/downloader/downloader-help-content.ts",
    "transcript": f"{F}/transcript/transcript-help-content.ts",
    "tts": f"{F}/tts/tts-help-content.ts",
    "converter": f"{F}/converter/convert-help-content.ts",
    "capture": f"{F}/capture/capture-help-content.ts",
    "settings": f"{F}/settings/settings-help-content.ts",
}
PAGES = {
    "downloader": (f"{F}/downloader/DownloaderPage.tsx", 574),
    "transcript": (f"{F}/transcript/TranscriptPage.tsx", 487),
    "tts": (f"{F}/tts/TTSPage.tsx", 307),
    "converter": (f"{F}/converter/ConvertPage.tsx", 602),
    "capture": (f"{F}/capture/CapturePage.tsx", 2652),
    "settings": (f"{F}/settings/SettingsPage.tsx", 624),
}
PINNED_TOPICS = ("downloader:pause", "transcript:blocked", "capture:four-tools", "capture:original-annotated")
# §Files Modified that exist at row 0, with each file's line-ending kind (measured at plan time).
MODIFIED = {
    HELP_CARD: "LF",
    f"{R}/styles.css": "CRLF",
    **{p: "CRLF" for p in MODULES.values()},
    "ui/tsconfig.json": "LF",
    PACKAGE: "CRLF",
    TEST_IDS: "CRLF",
    "ui/tests/unit/failure-reason-copy.test.ts": "LF",
    ".agent/skills/README.md": "CRLF",
    GUI: "CRLF",
    MATRIX: "CRLF",
    MEU_STATUS: "LF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
}
# The files the parallel session av-kit-c4 may also write: recorded as shared, with no hash; their
# bytes are copied as eol-check.py's base only.
SHARED = {
    ".agent/docs/commands.md": "CRLF",
    ".agent/context/current-focus.md": "CRLF",
    "docs/execution/metrics.md": "CRLF",
    ".agent/context/known-issues.yaml": "LF",
    ".agent/context/known-issues.md": "LF",
}
# §Files Modified that are new: each must be absent at row 0.
NEW = (
    f"{R}/components/help/quick-start.json",
    f"{R}/components/help/quick-start.ts",
    f"{R}/components/help/help-shots.ts",
    f"{R}/assets/help",
    "ui/playwright.help-shots.config.ts",
    "ui/tests/help-shots",
    "ui/tests/unit/help-quick-start.test.tsx",
    "ui/tests/unit/help-shots-privacy.test.ts",
    f"{E2E}/help-quick-start.test.ts",
    ".agent/skills/asd-ste100",
    "tools/help_guide_ste.py",
    "tests/tooling/test_help_guide_ste.py",
    HANDOFF,
    IMPL_REVIEW,
    REFLECTION,
)
SEAMS = {
    f"{E2E}/download-queue.test.ts": ("function seededQueue(): DownloadItem[]", "async function installSeam(page: Page, seed?: Partial<SeamSeed>)"),
    f"{E2E}/transcript-queue.test.ts": ("async function installTranscriptSeam(page: Page)",),
    f"{E2E}/tts-generate.test.ts": ("async function installTtsSeam(",),
    f"{E2E}/convert-queue.test.ts": ("async function installSeam(", "function seededQueue(): ConversionItem[]"),
    f"{E2E}/capture-inbox.test.ts": ("async function installSeam(", "async function installFidelitySeam("),
    f"{E2E}/settings.test.ts": ("async function installSettingsSeam(",),
}
PIN_FILES = (
    *(f"ui/tests/unit/{n}" for n in (
        "help-card.test.ts", "help-f1-hold.test.tsx", "capture-help-content.test.ts",
        "capture-action-row.test.ts", "capture-copy-image.behavior.test.ts",
        "capture-redact.behavior.test.ts", "capture-tool-style.test.ts",
        "failure-reason-copy.test.ts", "queue-pause-feedback.test.tsx", "layout-primitives.test.ts",
        "settings-rail.test.tsx", "common-shortcuts.test.tsx", "gui-actions-audit.test.ts",
        "capture-page.test.ts", "convert-page.test.ts",
    )),
    f"{E2E}/help-search.spec.ts",
    f"{E2E}/help-f1-mount.test.ts",
    f"{E2E}/keyboard-shortcuts.test.ts",
)
SKILL_SRC = "P:/creative-writing/.agent/skills/asd-ste100"
SKILL_FILES = ("SKILL.md", "LICENSE", "UPSTREAM.md", "references/writing-rules.md",
               "examples/before-after.md", "examples/linter-edge-cases.md", "scripts/ste-lint.py")
# "Read, never changed": bound by hash; their kind is recorded, not expected.
READ_ONLY = (
    *(p for p, _ in PAGES.values()),
    f"{R}/lib/theme.ts",
    ELECTRON_APP,
    "ui/playwright.config.ts",
    *SEAMS,
    f"{E2E}/fixtures/capture-fidelity-original.png",
    *(p for p in PIN_FILES if p not in MODIFIED),
    *(f"{SKILL_SRC}/{n}" for n in SKILL_FILES),
)
# Anchors (path, plan line or None, text): found once by text; a moved line is recorded for the
# handoff; a missing or doubled anchor is S2.
ANCHORS = (
    *((p, line, f'<HelpCard feature="{k}"') for k, (p, line) in PAGES.items()),
    (HELP_CARD, None, "function readExpanded("),
    (HELP_CARD, None, "HELP_FEATURE_ROUTE[feature]"),
    (GUI, 319, "### Help (per page)"),
    (GUI, None, "## Validation Commands"),
    (MATRIX, None, "| 6.22 |"),
    (ELECTRON_APP, 112, "export async function launchElectron"),
    *((p, None, needle) for p, needles in SEAMS.items() for needle in needles),
    (TEST_IDS, None, "// MEU-51 primitive harness IDs."),
    (PACKAGE, None, '"test:e2e"'),
)
FOLDER = {"downloader": "downloader", "transcript": "transcript", "tts": "tts",
          "converter": "converter", "capture": "capture", "settings": "settings"}
# Step targets built from a template: (feature folder, template text, value text).
TEMPLATED = {
    "convert-task-compress": ("converter", "`convert-task-${value}`", "['compress', 'Compress']"),
    "settings-mode-download": ("settings", "`settings-mode-${section.key}`", "key: 'download'"),
}
SKIP_DIRS = ("packages", "mcp-server")
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
GREP_EXCLUDES = (
    ":(exclude,glob)**/.mcp.json", ":(exclude,glob)**/mcp-token.txt", ":(exclude,glob)**/.claude.json",
    ":(exclude,glob)**/.env", ":(exclude,glob)**/.env.*", ":(exclude,glob)**/.claude/settings.local.json",
    ":(exclude).agent/fleet/hub",
)
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-20-help-quick-start-",
    "docs/execution/reflections/2026-11-20-help-quick-start-",
)
TOPIC_RE = {k: re.compile(k + r":\s*'((?:[^'\\]|\\.)*)'") for k in ("id", "title", "body")}
problems = []


def secret(name):
    parts = name.split("/")
    base = parts[-1]
    return (
        base in SECRET_BASES
        or base.startswith(".env.")
        or (len(parts) >= 2 and parts[-2] == ".claude" and base == "settings.local.json")
        or name.startswith(".agent/fleet/hub/")
        or name == ".agent/fleet/hub"
    )


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def sha(path):
    p = pathlib.Path(path)
    if p.is_file():
        return hashlib.sha256(p.read_bytes()).hexdigest()
    return "absent" if not p.exists() else "not-a-file"


def eol(raw):
    crlf = raw.count(b"\r\n")
    bare = raw.count(b"\n") - crlf
    if crlf and bare:
        return "MIXED", crlf, bare
    return ("CRLF" if crlf else ("LF" if bare else "none")), crlf, bare


def text_lines(p):
    return pathlib.Path(p).read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")


def unescape(s):
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), s)


OUT.mkdir(parents=True, exist_ok=True)
head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("HEAD (recorded, not compared)", head)
origin = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True).stdout.decode().strip()
print("origin/main as found", origin or "<none>")
print("git worktree list:")
for line in git("worktree", "list").decode("utf-8").splitlines():
    print("  ", line)

porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
print("git status --porcelain --untracked-files=all:")
for line in porcelain.splitlines():
    print("  ", line)
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
(PLAN / "baseline-dirty.txt").write_bytes(porcelain.encode("utf-8"))
print("baseline-dirty.txt", len(dirty), "paths")

# Scope binding.
scope = {}
for p in MODIFIED:
    scope[p] = sha(p)
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: a modified path is missing: {p}")
for p in NEW:
    scope[p] = sha(p)
    if scope[p] != "absent":
        problems.append(f"S2: a new path already exists: {p}")
for p in READ_ONLY:
    scope[p] = sha(p)
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: a read-only path is missing: {p}")
for p in SHARED:
    scope[p] = "shared"
    if not pathlib.Path(p).is_file():
        problems.append(f"S2: a shared path is missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print(
    "baseline-scope.json", len(scope), "paths:", len(MODIFIED), "modified,", len(NEW), "new (absent),",
    len(READ_ONLY), "read, never changed,", len(SHARED), "shared",
)
for p in READ_ONLY:
    if p in dirty:
        print("  read-only path dirty at row 0 (another session's; in baseline-dirty.txt):", p)


def in_scope(p):
    return p in scope or p.startswith(SCOPE_PREFIXES)


hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p) and not secret(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])

# The row-0 bytes: eol-check.py's base and the execution review's delta base.
PLAN_FILES = {p.as_posix(): "LF" for p in sorted(PLAN.iterdir()) if p.is_file() and p.suffix in (".md", ".py", ".ps1", ".json")}
copied = 0
for p in (*MODIFIED, *SHARED, *READ_ONLY, *PLAN_FILES, PLAN_REVIEW):
    src = pathlib.Path(p)
    if src.is_absolute() or not src.is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

# baseline-skip-hashes.json (H1-4): secret names dropped before any stat or read.
listed = git("ls-files", "--cached", "--others", "--exclude-standard", *SKIP_DIRS)
skip_paths = [n for n in listed.decode("utf-8").splitlines() if n and not secret(n)]
skips = {p: sha(p) for p in skip_paths if pathlib.Path(p).is_file()}
(PLAN / "baseline-skip-hashes.json").write_bytes((json.dumps(skips, indent=2, sort_keys=True) + "\n").encode())
print("baseline-skip-hashes.json", len(skips), "files:", {d: sum(1 for p in skips if p.startswith(d + "/")) for d in SKIP_DIRS})

# Line endings, measured with Python bytes.
eols = {}
for p, want in {**MODIFIED, **SHARED, **{q: None for q in READ_ONLY}, **PLAN_FILES}.items():
    if not pathlib.Path(p).is_file():
        eols[p] = {"kind": "absent", "expected": want}
        continue
    raw = pathlib.Path(p).read_bytes()
    kind, crlf, bare = eol(raw)
    eols[p] = {"kind": kind, "expected": want, "crlf": crlf, "bare_lf": bare, "bom": raw.startswith(b"\xef\xbb\xbf"), "bytes": len(raw)}
    print("eol", kind, "crlf", crlf, "bare_lf", bare, "bytes", len(raw), p)
    if want is not None and kind != want:
        problems.append(f"S2: {p} is {kind}, the plan says {want}")
(PLAN / "baseline-eol.json").write_bytes((json.dumps(eols, indent=2) + "\n").encode())
print("baseline-eol.json", len(eols), "paths")

# baseline-pins.json: the pin files' hashes; per content module the ordered topics and the
# pinned topics' title and body, read with the STE_GATE topic regex.
pins = {"files": {p: sha(p) for p in PIN_FILES}, "modules": {}}
for p, h in pins["files"].items():
    if h in ("absent", "not-a-file"):
        problems.append(f"S2: a pin file is missing: {p}")
for feature, path in MODULES.items():
    text = pathlib.Path(path).read_bytes().decode("utf-8")
    found = {k: [unescape(m.group(1)) for m in rx.finditer(text)] for k, rx in TOPIC_RE.items()}
    counts = {k: len(v) for k, v in found.items()}
    print("pins module", feature, counts, found["id"])
    if len(set(counts.values())) != 1 or not counts["id"]:
        problems.append(f"S2: {path}: id, title and body counts differ: {counts}")
        continue
    topics = [{"id": i, "title": t} for i, t in zip(found["id"], found["title"])]
    pinned = {}
    for key in PINNED_TOPICS:
        f, tid = key.split(":")
        if f != feature:
            continue
        if found["id"].count(tid) != 1:
            problems.append(f"S2: pinned topic {key} found {found['id'].count(tid)} time(s)")
            continue
        i = found["id"].index(tid)
        pinned[tid] = {"title": found["title"][i], "body": found["body"][i]}
        print("  pinned", key, repr(found["title"][i]), len(found["body"][i]), "chars")
    pins["modules"][feature] = {"path": path, "topics": topics, "pinned": pinned}
if sum(len(m["pinned"]) for m in pins["modules"].values()) != len(PINNED_TOPICS):
    problems.append("S2: not every pinned topic was recorded")
(PLAN / "baseline-pins.json").write_bytes((json.dumps(pins, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
print("baseline-pins.json", len(pins["files"]), "files,", sum(len(m["topics"]) for m in pins["modules"].values()), "topics")

# baseline-citations.txt: the anchors, and every draft step target as a test id.
cites = []
for p, plan_line, needle in ANCHORS:
    lines = text_lines(p)
    hits = [i + 1 for i, ln in enumerate(lines) if needle in ln]
    if len(hits) != 1:
        state = "missing" if not hits else f"doubled {hits}"
        problems.append(f"S2: anchor {needle!r} in {p}: {state}")
    else:
        state = "at line" if plan_line in (None, hits[0]) else f"moved from {plan_line}"
    cites.append(f"anchor {p}:{hits[0] if len(hits) == 1 else '-'} {state} hits={len(hits)} :: {needle}")
fixture = f"{E2E}/fixtures/capture-fidelity-original.png"
cites.append(f"file {fixture} {'present' if pathlib.Path(fixture).is_file() else 'MISSING'}")


def literal_hits(folder, target):
    quoted = (f"'{target}'", f'"{target}"', f"`{target}`")
    out = []
    for f in sorted(pathlib.Path(folder).rglob("*.ts*")):
        for n, ln in enumerate(f.read_bytes().decode("utf-8").splitlines(), 1):
            if any(q in ln for q in quoted):
                out.append(f"{f.as_posix()}:{n}")
    return out


draft = json.loads((PLAN / "quick-start-draft.json").read_bytes().decode("utf-8"))
targets = 0
for page, data in draft["pages"].items():
    for n, step in enumerate(data["steps"], 1):
        target = step.get("target")
        if not target:
            cites.append(f"target {page} step {n}: none")
            continue
        targets += 1
        feature = literal_hits(f"{F}/{FOLDER[page]}", target)
        shared = [] if feature else literal_hits(f"{R}/components", target)
        if feature or shared:
            where = "feature folder" if feature else "components/"
            cites.append(f"target {page} step {n} {target}: {where} {len(feature or shared)} hit(s), first {(feature or shared)[0]}")
            continue
        if target in TEMPLATED:
            folder, template, value = TEMPLATED[target]
            t_hits, v_hits = [], []
            for f in sorted(pathlib.Path(f"{F}/{folder}").rglob("*.ts*")):
                for k, ln in enumerate(f.read_bytes().decode("utf-8").splitlines(), 1):
                    if template in ln:
                        t_hits.append(f"{f.as_posix()}:{k}")
                    if value in ln:
                        v_hits.append(f"{f.as_posix()}:{k}")
            if t_hits and v_hits:
                cites.append(f"target {page} step {n} {target}: templated, template {t_hits[0]}, value {v_hits[0]}")
                continue
        cites.append(f"target {page} step {n} {target}: MISSING")
        problems.append(f"S2: step target {target} ({page} step {n}) is not a test id in its folder or components/")
for line in cites:
    print(line)
(PLAN / "baseline-citations.txt").write_bytes(("\n".join(cites) + "\n").encode("utf-8"))
print("baseline-citations.txt", len(ANCHORS), "anchors,", targets, "step targets")

# Free ids.
meus = yaml.safe_load(pathlib.Path(MEU_STATUS).read_bytes().decode("utf-8"))
rows = meus.get("meus", meus.get("rows", [])) if isinstance(meus, dict) else []
ids = {r.get("id") for r in rows if isinstance(r, dict)}
items = {str(r.get("matrix_item")) for r in rows if isinstance(r, dict)}
raw_status = pathlib.Path(MEU_STATUS).read_bytes().decode("utf-8")
matrix_rows = [ln for ln in text_lines(MATRIX) if ln.startswith("| 6.23 |")]
print("meu-status rows", len(rows), "MEU-162 in ids:", "MEU-162" in ids, "6.23 in items:", "6.23" in items,
      "'MEU-162' in text:", "MEU-162" in raw_status, "matrix rows '| 6.23 |':", len(matrix_rows))
if not rows or "MEU-162" in ids or "6.23" in items or "MEU-162" in raw_status or matrix_rows:
    problems.append("S2: MEU-162 or 6.23 is taken (or the MEU rows did not parse)")


def grep_lines(pattern):
    run = subprocess.run(["git", "grep", "--untracked", "-n", "-E", pattern, "--", ".", *GREP_EXCLUDES], capture_output=True)
    if run.returncode not in (0, 1):
        problems.append(f"git grep {pattern!r} exited {run.returncode}")
    return [ln for ln in run.stdout.decode("utf-8", "replace").splitlines() if ln]


residual = [ln for ln in grep_lines("help-quick-start-residual") if not ln.startswith(SCOPE_PREFIXES)]
print("help-quick-start-residual outside this plan:", [ln[:120] for ln in residual] or "none")
if residual:
    problems.append("S2: the anchor help-quick-start-residual is already used")
decisions = [ln for ln in grep_lines(r"D-(1289|129[0-8])\b") if not ln.startswith(SCOPE_PREFIXES)]
for ln in decisions:
    named = "help-quick-start" in ln
    print("D-1289..D-1298 outside this plan:", ln.split(":", 2)[0], "names this plan" if named else "FOREIGN USE")
    if not named:
        problems.append(f"S2: D-1289 to D-1298 used outside this plan: {ln[:160]}")

for p in sorted(PLAN_FILES):
    print("plan file", p, sha(p)[:16])
print("plan review", PLAN_REVIEW, sha(PLAN_REVIEW)[:16])
for p in problems:
    print("PROBLEM:", p)
print(f"baseline record: {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
'@

New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8

# 1. The environment (S7 on a held file).
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--offline', '--all-packages')
# 2. The record.
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. One host-load sample (the 50 % limit).
& rtk proxy uv run --no-sync python "$plan/host-wait.py" > "$receipts/hq-base-load.txt" 2>&1
$loadCode = $LASTEXITCODE
Get-Content "$receipts/hq-base-load.txt" | Select-Object -Last 3
Write-Output ("baseline step host-load exit={0} receipt={1}/hq-base-load.txt" -f $loadCode, $receipts)
if ($loadCode -ne 0) { exit $loadCode }

# 4. The base receipts: failures recorded, not fatal; the gate excuses only those ids.
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/hq-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Set-Content -Path "$receipts/hq-base-ui.txt.exit" -Value $uiCode -Encoding ascii
Write-Output ("base suite ui exit={0} receipt={1}/hq-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/hq-base-ui.txt" | Select-String -Pattern 'Test Files|Tests |FAIL ' | Select-Object -Last 12

& rtk proxy uv run --no-sync pytest tests/tooling -q *> "$receipts/hq-base-tooling.txt"
$toolCode = $LASTEXITCODE
Set-Content -Path "$receipts/hq-base-tooling.txt.exit" -Value $toolCode -Encoding ascii
Write-Output ("base suite tooling exit={0} receipt={1}/hq-base-tooling.txt" -f $toolCode, $receipts)
Get-Content "$receipts/hq-base-tooling.txt" | Select-String -Pattern '^FAILED|^ERROR|passed|failed' | Select-Object -Last 12

# 5. The plan-local checkers, then ruff on this folder's Python (Session 82 RULE-1).
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'host-wait-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/host-wait.py", '--selftest')
Invoke-Step 'row-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/row-check.py", '--selftest')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
Write-Output ("baseline plan Python: {0}" -f ($planPy -join ', '))
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Write-Output 'baseline: all steps exit 0'
exit 0
