# Tooling test hermeticity baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-15-framework-small-syncs/baseline.ps1, with this plan's
# steps: 1. the tree state (baseline.sha, baseline-dirty.txt, and baseline-dirty-blobs.json, the
# blob id of every baseline-dirty path's row-0 bytes for scope-check.py's HEAD rule, D-918);
# 2. the path-scoped baseline (baseline-scope.json with FIXTURE and make_fixture.py absent,
# baseline-dirty-hashes.json, baseline-api.json, the BASE copies in C:/Temp/av-kit/tth/base/ and
# tth-eol-base.txt; S2 on line endings other than the plan's contracts); 3. the NEEDLE count in
# WRAPPER and each RULE_MAP postimage pin count, each exactly 1 (S2); 4. RED_HOME rebuilt and shown
# to refuse with unknown_slug, the compiled overlay unchanged; 5. red-require.txt (12 titles, the
# first 11 from --collect-only); 6. uv sync (run first, so the collection in step 5 uses the
# locked environment), the base Python suite (tth-base-py.txt; its own failures are recorded, not
# fatal: the session gate excuses only the ids this receipt shows failing), the base adoption file
# (tth-base-adoption.txt) and the base DISPATCH_TEST with the user's own TEMP
# (tth-base-dispatch.txt and its .exit), checked with dispatch-check.py --exact-baseline;
# 7. every plan-local --selftest, then hermetic-check.py on BASE, which must refuse. Every other
# step is fail-fast. Run from the repository root.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-tooling-test-hermeticity'
$receipts = 'C:/Temp/av-kit/tth'
$env:ELECTRON_RUN_AS_NODE = $null
$env:AGENT_MODEL_REGISTRY = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = 'C:\Temp\av-kit\tth\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
New-Item -ItemType Directory -Force -Path "$receipts/base" | Out-Null

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')

# 1-5. Tree state, path-scoped baseline, needle and pins, RED_HOME and red-require.txt, in Python
# so every file is read and written as bytes.
$record = @'
import hashlib, json, os, pathlib, re, shutil, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-15-tooling-test-hermeticity")
TTH = pathlib.Path("C:/Temp/av-kit/tth")
BASE = TTH / "base"
RED_HOME = TTH / "red-home"
TEST_FILE = "tests/tooling/test_framework_adoption.py"
FIXTURE = "tests/tooling/fixtures/registry-home/model-registry.json"
MAKE = "tests/tooling/fixtures/registry-home/make_fixture.py"
DISPATCH_TEST = ".agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1"
YAML = ".agent/context/known-issues.yaml"
MD = ".agent/context/known-issues.md"
EXISTING = (TEST_FILE, DISPATCH_TEST, YAML, MD)
NEW = (FIXTURE, MAKE)
RULE_MAP = "docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md"
WRAPPER = "tools/Invoke-CodexDispatch.ps1"
NEEDLE = b"$dispatchProjectRoot = 'P:/av-kit'"
OVERLAY = ".agent/model-registry.local.yaml"
COMPILED = ".agent/model-registry.local.json"
MACHINE = pathlib.Path("P:/.agent")
TOOL_FILES = ("tools/resolve_model.py", "tools/ModelRegistry.psm1", "schema/model-registry.v1.schema.json")
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-15-tooling-test-hermeticity-",
    "docs/execution/reflections/2026-11-15-tooling-test-hermeticity-",
)
SHARED = ("docs/execution/metrics.md", ".agent/context/current-focus.md")
PREFIX = "tests/tooling/test_framework_adoption.py::"
problems = []

def git(*args, data=None):
    return subprocess.run(["git", *args], capture_output=True, check=True, input=data).stdout

def sha(path):
    p = pathlib.Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ("absent" if not p.exists() else "not-a-file")

def paths(porcelain):
    out = []
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        name = line[3:].strip()
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        out.append(name.strip('"'))
    return out

def dump(obj):
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode()

# 1. Tree state.
head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
(PLAN / "baseline-dirty.txt").write_bytes(porcelain.encode("utf-8"))
dirty = paths(porcelain)
print("baseline-dirty.txt", len(dirty), "paths")
present = [p for p in dirty if pathlib.Path(p).is_file()]
ids = git("hash-object", "--stdin-paths", data=("\n".join(present) + "\n").encode("utf-8")).decode().split()
if len(ids) != len(present):
    problems.append(f"hash-object returned {len(ids)} ids for {len(present)} paths")
blobs = dict(zip(present, ids))
blobs.update({p: "deleted" for p in dirty if p not in blobs})
(PLAN / "baseline-dirty-blobs.json").write_bytes(dump(blobs))
print("baseline-dirty-blobs.json", len(blobs), "paths,", sum(v == "deleted" for v in blobs.values()), "deleted")

# 2. Path-scoped baseline.
scope = {p: sha(p) for p in EXISTING + NEW}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"new path already exists: {p}")
for p in EXISTING:
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"existing path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent;", YAML, scope[YAML])

base_plans = {n for n in git("ls-tree", "--name-only", head, "docs/execution/plans/").decode().splitlines() if n}

def other_plan(p):
    folder = "/".join(p.split("/")[:4])
    return p.startswith("docs/execution/plans/2026-11-15-") and folder != p and folder not in base_plans

def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES) or other_plan(p)

hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes(dump(hashes))
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in SHARED:
    print("shared", p, "dirty" if p in dirty else "clean at HEAD", sha(p))

listed = git("ls-files", "--cached", "--others", "--exclude-standard", "--", "packages/api").decode("utf-8").splitlines()
api = {p: (hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() if pathlib.Path(p).is_file() else "deleted") for p in sorted(set(listed)) if p.strip()}
(PLAN / "baseline-api.json").write_bytes(dump(api))
print("baseline-api.json", len(api), "files under packages/api")

for p in (TEST_FILE, DISPATCH_TEST, RULE_MAP):
    dest = BASE / pathlib.Path(p).name
    dest.write_bytes(pathlib.Path(p).read_bytes())
    print("BASE", p, "->", dest.as_posix(), "sha256", sha(dest))

WANT = {
    TEST_FILE: {"bom": False, "eol": "crlf", "lines": 1072, "bytes": 40489},
    DISPATCH_TEST: {"bom": True, "eol": "crlf", "lines": 1133, "bytes": 62454},
    YAML: {"bom": False, "eol": "lf"},
    MD: {"bom": False, "eol": "lf"},
}
eol_lines = []
for p in EXISTING + NEW:
    path = pathlib.Path(p)
    if not path.is_file():
        got = {"state": "absent"}
    else:
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        lf = data.count(b"\n") - crlf
        cr = data.count(b"\r") - crlf
        got = {
            "bom": data.startswith(b"\xef\xbb\xbf"),
            "eol": "crlf" if lf == 0 and cr == 0 and crlf else ("lf" if crlf == 0 and cr == 0 and lf else f"mixed crlf={crlf} lf={lf} cr={cr}"),
            "lines": data.count(b"\n"),
            "bytes": len(data),
            "final_newline": data.endswith(b"\n"),
        }
    want = WANT.get(p, {"state": "absent"})
    ok = all(got.get(k) == v for k, v in want.items())
    eol_lines.append(f"{p}: {json.dumps(got, sort_keys=True)} {'ok' if ok else 'S2 want ' + json.dumps(want, sort_keys=True)}")
    if not ok:
        problems.append(f"S2: {p} line endings or size {got} differ from the contract {want}")
(TTH / "tth-eol-base.txt").write_bytes(("\n".join(eol_lines) + "\n").encode("utf-8"))
print("\n".join(eol_lines))

# 3. Needle and pins.
n = pathlib.Path(WRAPPER).read_bytes().count(NEEDLE)
print("NEEDLE count in WRAPPER:", n)
if n != 1:
    problems.append(f"S2: NEEDLE occurs {n} times in WRAPPER")
blocks = re.findall(r"```json\s*\n(.*?)\n```", pathlib.Path(RULE_MAP).read_text(encoding="utf-8"), re.S)
if len(blocks) != 1:
    problems.append(f"S2: RULE_MAP holds {len(blocks)} json blocks")
else:
    counts = json.loads(blocks[0])["counts"]
    rule_bytes = pathlib.Path(RULE_MAP).read_bytes()
    for name in ("AGENTS.md", "GUARDRAILS.md"):
        pin = counts[name]["postimage_sha256"]
        c = rule_bytes.count(pin.encode())
        live = sha(name)
        print(f"RULE_MAP {name} postimage pin {pin} count {c}; live sha256 {'matches' if live == pin else 'differs: ' + live}")
        if c != 1:
            problems.append(f"S2: RULE_MAP pin for {name} occurs {c} times")

# 4. RED_HOME.
live_registry = MACHINE / "model-registry.json"
live_before = sha(live_registry)
compiled_before = sha(COMPILED)
if RED_HOME.exists():
    shutil.rmtree(RED_HOME)
for rel in TOOL_FILES:
    (RED_HOME / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(MACHINE / rel, RED_HOME / rel)
reg = json.loads(live_registry.read_text(encoding="utf-8"))
del reg["catalog"]["cursor-grok-4.6"]
(RED_HOME / "model-registry.json").write_bytes((json.dumps(reg, indent=2) + "\n").encode("utf-8"))
env = {k: v for k, v in os.environ.items() if k != "AGENT_MODEL_REGISTRY"}
env["AGENT_MODEL_REGISTRY"] = (RED_HOME / "model-registry.json").as_posix()
r = subprocess.run([sys.executable, str(MACHINE / "tools/resolve_model.py"), "validate", "--overlay", OVERLAY],
                   capture_output=True, text=True, encoding="utf-8", env=env, check=False)
print("RED_HOME validate --overlay under HOSTILE: exit", r.returncode, "|", (r.stderr or r.stdout).strip()[-200:])
if r.returncode == 0 or "unknown_slug" not in r.stderr:
    problems.append("RED_HOME does not refuse the overlay with unknown_slug")
if sha(COMPILED) != compiled_before or sha(live_registry) != live_before:
    problems.append("the RED_HOME probe changed the compiled overlay or the live registry")
else:
    print("compiled overlay and live registry unchanged")

# 5. red-require.txt.
c = subprocess.run([sys.executable, "-m", "pytest", TEST_FILE, "--collect-only", "-q"], capture_output=True,
                   text=True, encoding="utf-8", check=False)
ids = [ln[len(PREFIX):].strip() for ln in c.stdout.splitlines() if ln.startswith(PREFIX)]
groups = {
    "preserves_bindings": [i for i in ids if i.startswith("test_registry_contract_preserves_bindings[")],
    "vendor_independence": [i for i in ids if i.startswith("test_registry_contract_vendor_independence[")],
    "unsupported_harness": [i for i in ids if i == "test_registry_contract_unsupported_harness_refused"],
    "wrapper_same_vendor": [i for i in ids if i == "test_review_pipeline_wrapper_refuses_before_provider[same-vendor]"],
}
print("collected", len(ids), "ids; exit", c.returncode, {k: len(v) for k, v in groups.items()})
require = [i for k in groups for i in groups[k]]
if [len(v) for v in groups.values()] != [7, 2, 1, 1] or len(require) != 11:
    problems.append(f"red-require: expected 7+2+1+1 = 11 collected ids, got {[len(v) for v in groups.values()]}")
require.append("test_ac_2_fixture_registry_home_compiles")
(PLAN / "red-require.txt").write_bytes(("\n".join(require) + "\n").encode("utf-8"))
print("red-require.txt", len(require), "titles")
for t in require:
    print("   ", t)

for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', 'python', "$receipts/baseline-record.py")

# 6. The base receipts: the Python suite and the adoption file with TMP and TEMP outside the user
# profile, then DISPATCH_TEST with the user's own TEMP.
$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/tth-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/tth-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/tth-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
& rtk proxy uv run pytest tests/tooling/test_framework_adoption.py --tb=short -q *> "$receipts/tth-base-adoption.txt"
Write-Output ("base adoption exit={0} receipt={1}/tth-base-adoption.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/tth-base-adoption.txt" -Tail 3
$env:TMP = $userTmp
$env:TEMP = $userTemp
$leftover = Join-Path $userTemp 'av-kit/receipts/dispatch-tests'
$before = if (Test-Path -LiteralPath $leftover) { (Get-Item -LiteralPath $leftover).LastWriteTime.ToString('s') } else { 'absent' }
& rtk proxy pwsh -NoProfile -File .agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1 *> "$receipts/tth-base-dispatch.txt"
$dispatchCode = $LASTEXITCODE
Set-Content -Path "$receipts/tth-base-dispatch.txt.exit" -Value $dispatchCode
$after = if (Test-Path -LiteralPath $leftover) { (Get-Item -LiteralPath $leftover).LastWriteTime.ToString('s') } else { 'absent' }
Write-Output ("base dispatch exit={0} receipt={1}/tth-base-dispatch.txt; the leftover %TEMP% dispatch-tests folder mtime before={2} after={3}" -f $dispatchCode, $receipts, $before, $after)
Invoke-Step 'dispatch-exact-baseline' @('uv', 'run', 'python', "$plan/dispatch-check.py", '--exact-baseline', '--exit-file', "$receipts/tth-base-dispatch.txt.exit", "$receipts/tth-base-dispatch.txt")

# 7. The plan-local checkers' selftests, then hermetic-check.py on BASE, which must refuse.
Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'dispatch-check-selftest' @('uv', 'run', 'python', "$plan/dispatch-check.py", '--selftest')
Invoke-Step 'fixture-check-selftest' @('uv', 'run', 'python', "$plan/fixture-check.py", '--selftest')
Invoke-Step 'hermetic-check-selftest' @('uv', 'run', 'python', "$plan/hermetic-check.py", '--selftest')
Invoke-Step 'live-probe-selftest' @('uv', 'run', 'python', "$plan/live-probe.py", '--selftest')
& rtk proxy uv run python "$plan/hermetic-check.py" --file "$receipts/base/test_framework_adoption.py"
$code = $LASTEXITCODE
Write-Output ("baseline step hermetic-check-on-BASE exit={0} (must be non-zero)" -f $code)
if ($code -eq 0) { Write-Output 'hermetic-check.py accepted BASE; the Red half of AC-5 failed'; exit 1 }
Write-Output 'baseline: all steps exit 0'
exit 0
