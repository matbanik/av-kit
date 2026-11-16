"""Session 79 live smoke (task row 10; plan AC-13).

Runs the fixed tool against the real tree and a copy of the real register, read-only:

1. The real register's SHA-256 is recorded, and the register is copied to
   C:/Temp/av-kit/triage-tool-fixes/smoke/known-issues.yaml.
2. verify --deep, in process (verify_deep on the loaded copy, project_root = the repository) and
   through the CLI (--yaml <copy> verify --deep, cwd = the repository):
   no no_test_coverage finding; every file_missing names an issue whose resolution_path passes
   _is_path_like and holds no whitespace (each is printed as `real:`); the CLI exit is 1 when there
   are findings and 0 when there are none; the copy's bytes are unchanged (read-only, D-947).
3. discover, in process (scan_todos) and through the CLI (--yaml <copy> discover --root R
   --dry-run), for R = . and the subroots mcp-server, ui and packaging: no candidate of a noise
   class (a path under a tree that git reports as ignored, from
   `git ls-files --others --ignored --exclude-standard --directory`, or under one of the plan's
   inventoried trees; the scanner's own module; a .jar; a file with a NUL byte in its first 8000
   bytes); any other candidate is printed as `real:`. Each CLI `New candidates:` count equals the
   in-process count. _repo_root of each subroot is the repository. The walk from each root lists
   no file under a noise tree; from . it lists tools/issue_triage.py and more than 500 files.
   A root inside an excluded tree (mcp-server/bundle, ui/out, when present) gives 0 candidates in
   process and `New candidates: 0` through the CLI. Oracle check: every inventoried tree present on
   disk is classified as noise, so a tree the scanner omits fails the smoke instead of printing
   `real:`.
4. --help under PYTHONIOENCODING=cp1252 and PYTHONUTF8=0 exits 0 (AC-1 on the real console path).
5. The real register's SHA-256 is unchanged.

Run from the repository root: `uv run python <plan>/live-smoke.py`. Exit 0 on pass, 1 on fail.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

REGISTER = ROOT / ".agent/context/known-issues.yaml"
SCRATCH = Path("C:/Temp/av-kit/triage-tool-fixes/smoke")
CLI = ROOT / "tools/issue_triage.py"
# The plan's DISCOVER_ROOTS inventory (D-948), as repository paths; native/*/publish is matched below.
INVENTORY = (
    "_inspiration/external_code/",
    "mcp-server/bundle/",
    "mcp-server/dist/",
    "ui/out/",
    "ui/out-e2e/",
    "ui/dist/",
    "packaging/build/",
    "packaging/dist/",
    "packaging/ffmpeg-win64/",
    "packaging/deno-win64/",
    ".serena/cache/",
)
SUBROOTS = ("mcp-server", "ui", "packaging")
INSIDE_EXCLUDED = ("mcp-server/bundle", "ui/out")
SELF_MODULE = "tools/issue_triage/discover.py"
problems: list[str] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cli(args: list[str], extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    env = dict(os.environ)
    env.pop("PYTHONUTF8", None)
    env["PYTHONIOENCODING"] = "utf-8"
    env.update(extra_env or {})
    return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, env=env, capture_output=True)


def norm(p: str) -> str:
    return p.replace("\\", "/")


def has_nul(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            return b"\x00" in fh.read(8000)
    except OSError:
        return False


def ignored_trees() -> tuple[str, ...]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "--directory"],
            cwd=ROOT, capture_output=True, check=True,
        ).stdout.decode("utf-8", errors="replace")
    except (OSError, subprocess.CalledProcessError) as exc:
        problems.append(f"git could not list the ignored trees: {type(exc).__name__}")
        return ()
    return tuple(sorted({ln.strip() for ln in out.splitlines() if ln.strip().endswith("/")}))


IGNORED_TREES = ignored_trees()
NOISE_TREES = tuple(sorted(set(INVENTORY) | set(IGNORED_TREES)))


def noise_tree(rel: str) -> str | None:
    rel = norm(rel)
    for tree in NOISE_TREES:
        if rel.startswith(tree):
            return tree
    parts = rel.split("/")
    if len(parts) > 3 and parts[0] == "native" and "publish" in parts[2:-1]:
        return "native/*/publish/"
    return None


def noise_class(rel: str) -> str | None:
    rel = norm(rel)
    tree = noise_tree(rel)
    if tree:
        return f"generated, fetched or vendored tree {tree}"
    if rel == SELF_MODULE or rel.endswith("/" + SELF_MODULE):
        return "the scanner's own module"
    if rel.lower().endswith(".jar"):
        return "a .jar"
    if has_nul(ROOT / rel):
        return "a file with a NUL byte"
    return None


real_before = sha(REGISTER)
print("register sha256 before", real_before)
SCRATCH.mkdir(parents=True, exist_ok=True)
copy = SCRATCH / "known-issues.yaml"
shutil.copyfile(REGISTER, copy)
copy_sha = sha(copy)
if copy_sha != real_before:
    problems.append("the copy differs from the register")

from tools.issue_triage import discover, model, verify  # noqa: E402

for name, mod in (
    ("_is_path_like", verify),
    ("_strip_location", verify),
    ("verify_deep", verify),
    ("scan_todos", discover),
    ("_walk_source_files", discover),
    ("_repo_root", discover),
):
    if not hasattr(mod, name):
        problems.append(f"missing {mod.__name__}.{name}")
if problems:
    for p in problems:
        print("PROBLEM:", p)
    sys.exit(1)

# 2. verify --deep.
data = model.load(copy)
by_id = {i["id"]: i for i in data.get("issues", [])}
findings = verify.verify_deep(data, project_root=ROOT)
types = sorted({f["type"] for f in findings})
print("verify_deep findings", len(findings), "types", types)
for f in findings:
    if f["type"] != "file_missing":
        problems.append(f"verify_deep emitted {f['type']} for {f['issue_id']}")
        continue
    value = by_id.get(f["issue_id"], {}).get("resolution_path")
    ok = verify._is_path_like(value) and isinstance(value, str) and not re.search(r"\s", value.strip())
    print(f"real: file_missing {f['issue_id']} {value!r}")
    if not ok:
        problems.append(f"file_missing on a value that is not path-shaped: {f['issue_id']}")
cli = run_cli(["--yaml", str(copy), "verify", "--deep"])
out = cli.stdout.decode("utf-8", errors="replace")
print("cli verify --deep exit", cli.returncode, "last line", (out.strip().splitlines() or [""])[-1][:160])
if "no_test_coverage" in out:
    problems.append("the CLI printed no_test_coverage")
if cli.returncode != (1 if findings else 0):
    problems.append(f"cli verify --deep exit {cli.returncode} with {len(findings)} finding(s)")
if sha(copy) != copy_sha:
    problems.append("verify --deep changed the copy's bytes")
else:
    print("copy unchanged after verify --deep")

# 3. discover.
print("ignored trees from git", len(IGNORED_TREES), "noise trees", len(NOISE_TREES))
if not IGNORED_TREES:
    problems.append("git listed no ignored tree, so the noise oracle has no git half")
for tree in INVENTORY:
    if (ROOT / tree).is_dir() and not noise_class(tree + "x.js"):
        problems.append(f"oracle: the inventoried tree {tree} is not classified as noise")
existing = set(by_id)
repo = ROOT.resolve()


def cli_count(root_arg: str) -> int | None:
    cli = run_cli(["--yaml", str(copy), "discover", "--root", root_arg, "--dry-run"])
    out = cli.stdout.decode("utf-8", errors="replace")
    m = re.search(r"New candidates: (\d+)", out)
    print(f"cli discover --root {root_arg} exit", cli.returncode, "count", m.group(1) if m else None)
    if cli.returncode != 0 or not m:
        problems.append(f"cli discover --root {root_arg} did not exit 0 with a count")
        return None
    return int(m.group(1))


for sub in (".", *SUBROOTS):
    base = ROOT / sub
    prefix = "" if sub == "." else sub + "/"
    if not base.is_dir():
        problems.append(f"liveness: the subroot {sub} is missing")
        continue
    if discover._repo_root(base) != repo:
        problems.append(f"_repo_root({sub}) is {discover._repo_root(base)}, not the repository")
    walk = [norm(str(p.relative_to(ROOT))) for p in discover._walk_source_files(base, discover._repo_root(base))]
    print(f"walk --root {sub} files", len(walk))
    if sub == ".":
        if "tools/issue_triage.py" not in walk:
            problems.append("liveness: the walk does not list tools/issue_triage.py")
        if len(walk) <= 500:
            problems.append(f"liveness: the walk lists only {len(walk)} files")
    leaked = [p for p in walk if noise_tree(p)]
    if leaked:
        problems.append(f"the walk from {sub} lists {len(leaked)} file(s) under a noise tree, first {leaked[0]}")
    cands = [c for c in discover.scan_todos(base, existing_issue_ids=existing) if not c.get("linked_issue_id")]
    print(f"scan_todos --root {sub} new candidates", len(cands))
    for c in cands:
        rel = prefix + norm(c["file_path"])
        kind = noise_class(rel)
        if kind:
            problems.append(f"noise candidate ({kind}): {rel}:{c['line_number']}")
        else:
            print(f"real: {c['pattern']} {rel}:{c['line_number']}")
    got = cli_count(sub)
    if got is not None and got != len(cands):
        problems.append(f"cli discover --root {sub} counted {got}, in process {len(cands)}")
for sub in INSIDE_EXCLUDED:
    if not (ROOT / sub).is_dir():
        print(f"root inside an excluded tree {sub}: absent, skipped")
        continue
    n = len(discover.scan_todos(ROOT / sub, existing_issue_ids=existing))
    print(f"scan_todos --root {sub} findings", n)
    if n:
        problems.append(f"a root inside the excluded tree {sub} gave {n} finding(s)")
    got = cli_count(sub)
    if got not in (0, None):
        problems.append(f"cli discover --root {sub} counted {got}, expected 0")
if sha(copy) != copy_sha:
    problems.append("discover --dry-run changed the copy's bytes")

# 4. cp1252 --help.
cli = run_cli(["--help"], {"PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"})
print("cp1252 --help exit", cli.returncode, "arrow bytes", b"\xe2\x86\x92" in cli.stdout)
if cli.returncode != 0:
    problems.append("--help under cp1252 did not exit 0")

# 5. The real register.
real_after = sha(REGISTER)
print("register sha256 after", real_after)
if real_after != real_before:
    problems.append("the real register changed")

for p in problems:
    print("PROBLEM:", p)
print("live-smoke:", "fail" if problems else "pass")
sys.exit(1 if problems else 0)
