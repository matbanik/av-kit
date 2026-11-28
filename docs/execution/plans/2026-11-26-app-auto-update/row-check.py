"""Session 106 row checks (task rows 1 to 18 and H1; implementation-plan.md §Verification Plan).

Written in the shape of Session 103's (2026-11-26-capture-key-inbox-scrollbars/row-check.py),
whose helpers (``Ctx``, red-record, red-unchanged, canon, the register and status readers and the
selftest frame) it keeps. Every subcommand exits 0 when it finds no problem, 1 when it does, 2 on
a usage error:

* ``red-record --row N FILE ...``: the hashes of a Red row's test files (``aau-red-hashes.json``)
  and their byte copies under ``aau-red-copies/row<N>/``.
* ``red-unchanged``: every recorded Red file still has the hash its latest row recorded.
* ``openapi-leaf``: ``openapi.committed.json`` names ``update_interval`` in the settings request
  model (``SettingsPutIn``) and keeps CRLF line endings throughout.
* ``electron-binary``: ``ui/node_modules/electron/dist/electron.exe`` is still there.
* ``canon``: each canon-edit.py edit is applied to its ``R/canon-before`` bytes.
* ``register``: ``APP-NO-IN-APP-UPDATE`` is ``resolved`` in ``known-issues.yaml``.
* ``status MEU... STATUS``: each named MEU has that status in ``meu-status.yaml``.
* ``macro-current FILE``: ``ui/build/installer.nsh`` has the SHA-256 that row 3 recorded in FILE
  (key ``working_sha256``) and still holds ``!macro customCheckAppRunning``.
* ``scope-paths``: every changed or new path (``git diff HEAD`` and the untracked files) is in
  ``baseline-scope.json``, this plan's own (plan folder, handoffs, reflection), another session's
  plan or artifact, or a row-0 dirty path whose bytes are unchanged (S4); a release note path
  outside the scope is a problem (S6).
* ``remote-run-2``: row 17's run receipt ends ``e2e-remote: ok exit=0``, its ``summary.json``
  names row 16's snapshot commit and the same run id, ``aau-row17-run-check.txt`` ends
  ``run-check: 0 problem(s)``, and no product path of the scope (``ui/``, ``packages/``,
  ``mcp-server/``, ``tools/``, ``tests/``, ``openapi.committed.json``) differs from that snapshot
  commit (a changed product file means rows 16 and 17 run again).
* ``--selftest``: each check's passing case passes and its failing case fails.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass

import yaml

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SLUG = "2026-11-26-app-auto-update"
PLAN_REL = f"docs/execution/plans/{SLUG}"
RECEIPTS = pathlib.Path("C:/Temp/av-kit") / SLUG
RED_STORE = "aau-red-hashes.json"
RED_COPIES = "aau-red-copies"

OPENAPI = "openapi.committed.json"
REGISTER = ".agent/context/known-issues.yaml"
MEU_STATUS = ".agent/context/meu-status.yaml"
NSH = "ui/build/installer.nsh"
ELECTRON_EXE = "ui/node_modules/electron/dist/electron.exe"
ISSUE = "APP-NO-IN-APP-UPDATE"
MEUS = ("MEU-173", "MEU-174")
MACRO = "!macro customCheckAppRunning"
SNAP_16 = "aau-snapshot-16.json"
RUN_17 = "aau-row17-run.txt"
RUN_CHECK_17 = "aau-row17-run-check.txt"
PRODUCT = ("ui/", "packages/", "mcp-server/", "tools/", "tests/", "openapi.committed.json")
SECRET_NAMES = {".mcp.json", "mcp-token.txt", ".claude.json", ".env", "settings.local.json"}
HUB = ".agent/fleet/hub"
E2E_LINE = re.compile(r"^e2e-remote: (\S+) exit=(-?\d+) run=(\S+) receipts=(.+?)\s*$")
OTHER_PLAN = re.compile(r"^docs/execution/plans/2026-11-(?:1[6-9]|2\d)-[^/]+/")
OTHER_ARTIFACT = re.compile(
    r"^(?:\.agent/context/handoffs/2026-11-2\d-|docs/proposals/2026-11-2\d-|"
    r"docs/execution/reflections/2026-11-2\d-|\.agent/context/grouping/2026-11-2\d-)"
)
RELEASE = re.compile(r"changelog|release[-_ ]?notes?|docs/releases/v", re.IGNORECASE)


def _load(name: str, file: str, folder: pathlib.Path = HERE):
    spec = importlib.util.spec_from_file_location(name, folder / file)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


eolc = _load("aau_eol_check", "eol-check.py")
SCOPE: dict[str, str] = eolc.SCOPE
PINS: dict[str, str] = eolc.PINS
GROUPING: str = eolc.GROUPING


@dataclass
class Ctx:
    root: pathlib.Path = ROOT
    r: pathlib.Path = RECEIPTS
    plan: pathlib.Path = HERE

    @property
    def copies(self) -> pathlib.Path:
        return self.r / "baseline-copies"

    def base(self, name: str) -> bytes:
        return (self.copies / name).read_bytes()

    def now(self, name: str) -> bytes:
        return (self.root / name).read_bytes()


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "absent"


def rel(path: pathlib.Path, root: pathlib.Path) -> str:
    path = path if path.is_absolute() else root / path
    return path.resolve().relative_to(root.resolve()).as_posix()


# --- red-record, red-unchanged (Session 103's)
def _red_data(record: pathlib.Path) -> dict:
    if not record.is_file():
        return {"order": [], "rows": {}}
    return json.loads(record.read_text(encoding="utf-8"))


def red_record(ctx: Ctx, row: str, files: list[str]) -> list[str]:
    root, store = ctx.root, ctx.r
    record = store / RED_STORE
    data = _red_data(record)
    entry: dict[str, str] = {}
    for f in files:
        p = pathlib.Path(f)
        p = p if p.is_absolute() else root / p
        if not p.is_file():
            return [f"red-record: {f} is not a file"]
        entry[rel(p, root)] = sha(p)
    if row in data["rows"] and data["rows"][row] != entry:
        return [f"red-record: row {row} is already recorded with other hashes: {data['rows'][row]}"]
    for name in entry:
        dest = store / RED_COPIES / f"row{row}" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((root / name).read_bytes())
    if row not in data["rows"]:
        data["order"].append(row)
    data["rows"][row] = entry
    store.mkdir(parents=True, exist_ok=True)
    record.write_bytes((json.dumps(data, indent=2) + "\n").encode("utf-8"))
    for name, h in entry.items():
        print(f"red-record row {row}: {name} {h}")
    return []


def red_unchanged(ctx: Ctx) -> list[str]:
    record = ctx.r / RED_STORE
    if not record.is_file():
        return [f"red-unchanged: {record} missing"]
    data = _red_data(record)
    latest: dict[str, tuple[str, str]] = {}
    for row in data["order"]:
        for name, want in data["rows"][row].items():
            latest[name] = (row, want)
    problems: list[str] = []
    for name, (row, want) in sorted(latest.items()):
        got = sha(ctx.root / name)
        print(f"red-unchanged {name} (latest row {row}): {'ok' if got == want else 'CHANGED'}")
        if got != want:
            problems.append(f"red-unchanged: {name} (row {row}) is {got[:16]}, not {want[:16]}")
    if not latest:
        problems.append("red-unchanged: no file recorded")
    return problems


# --- openapi-leaf, electron-binary, macro-current
def openapi_leaf(ctx: Ctx) -> list[str]:
    raw = ctx.now(OPENAPI)
    problems: list[str] = []
    bare_lf = raw.count(b"\n") - raw.count(b"\r\n")
    if raw.count(b"\r\n") == 0 or bare_lf:
        problems.append(f"openapi-leaf: {OPENAPI} is not CRLF ({bare_lf} bare LF)")
    schemas = json.loads(raw.decode("utf-8")).get("components", {}).get("schemas", {})
    models = [k for k in schemas if k.startswith("SettingsPutIn")]
    if not models:
        problems.append("openapi-leaf: no SettingsPutIn schema")
    for k in models:
        has = "update_interval" in schemas[k].get("properties", {})
        print(f"openapi-leaf {k}: update_interval {'present' if has else 'MISSING'}")
        if not has:
            problems.append(f"openapi-leaf: {k} lacks update_interval")
    return problems


def electron_binary(ctx: Ctx) -> list[str]:
    p = ctx.root / ELECTRON_EXE
    size = p.stat().st_size if p.is_file() else 0
    print(f"electron-binary {ELECTRON_EXE}: {size} bytes")
    return [] if size > 1_000_000 else [f"electron-binary: {ELECTRON_EXE} missing or truncated"]


def macro_current(ctx: Ctx, record: pathlib.Path) -> list[str]:
    if not record.is_file():
        return [f"macro-current: {record} missing"]
    want = json.loads(record.read_text(encoding="utf-8")).get("working_sha256")
    got = sha(ctx.root / NSH)
    problems: list[str] = []
    print(f"macro-current {NSH}: now {got[:16]}, row 3 {str(want)[:16]}")
    if got != want:
        problems.append(f"macro-current: {NSH} changed since row 3; rebuild the canary (row 3)")
    if got != "absent" and MACRO.encode() not in ctx.now(NSH):
        problems.append(f"macro-current: {NSH} lacks {MACRO}")
    return problems


# --- canon, register, status
def _issues(raw: bytes, label: str) -> dict[str, dict]:
    data = yaml.safe_load(raw.decode("utf-8"))
    ids = [i.get("id") for i in data["issues"]]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{label}: doubled issue ids")
    return {i["id"]: i for i in data["issues"]}


def _meus(raw: bytes) -> dict[str, dict]:
    out: dict[str, dict] = {}

    def walk(node: object) -> None:
        if isinstance(node, dict):
            if "row_key" in node:
                out[str(node.get("id"))] = node
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(yaml.safe_load(raw.decode("utf-8")))
    return out


def canon(ctx: Ctx, edits: dict | None = None) -> list[str]:
    ced = _load("aau_canon_edit", "canon-edit.py", ctx.plan)
    edits = ced.EDITS if edits is None else edits
    if not edits:
        return ["canon: EDITS not written"]
    problems: list[str] = []
    for path, pairs in edits.items():
        before_p = ctx.r / "canon-before" / path
        if not before_p.is_file():
            problems.append(f"canon: no canon-before copy of {path}")
            continue
        before = before_p.read_bytes()
        want, probs = ced.apply(before, pairs, path)
        problems += [f"canon: {x}" for x in probs]
        if ctx.now(path) != want:
            problems.append(f"canon: {path} is not its before bytes with the edits")
        if (ctx.copies / path).is_file() and before != ctx.base(path):
            print(f"canon note: {path} changed between row 0 and row 18 (another session)")
        print(f"canon {path}: {len(pairs)} edit(s)")
    return problems


# --- scope-paths, remote-run-2
def _git(root: pathlib.Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout


def _changed(root: pathlib.Path) -> list[str]:
    raw = _git(root, "diff", "--no-renames", "--name-only", "-z", "HEAD")
    raw += _git(root, "ls-files", "--others", "--exclude-standard", "-z")
    return sorted({x.decode("utf-8") for x in raw.split(b"\0") if x})


def _secret(path: str) -> bool:
    return path.startswith(HUB) or pathlib.PurePosixPath(path).name in SECRET_NAMES


def _sha(path: pathlib.Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def scope_paths(ctx: Ctx, changed: list[str] | None = None) -> list[str]:
    scope = json.loads((ctx.plan / "baseline-scope.json").read_text(encoding="utf-8"))
    dirty_p = ctx.plan / "baseline-dirty-hashes.json"
    dirty = json.loads(dirty_p.read_text(encoding="utf-8")) if dirty_p.is_file() else {}
    changed = _changed(ctx.root) if changed is None else changed
    own = (
        PLAN_REL + "/",
        f".agent/context/handoffs/{SLUG}-",
        f"docs/execution/reflections/{SLUG}-",
    )
    problems: list[str] = []
    kept = notes = 0
    for p in changed:
        if "__pycache__" in p or _secret(p):
            continue
        if p in scope or p.startswith(own):
            kept += 1
            continue
        if RELEASE.search(p):
            problems.append(f"scope-paths: {p} is a release note outside the scope")
            continue
        if p in dirty and _sha(ctx.root / p) == dirty[p]:
            notes += 1
            continue
        if OTHER_PLAN.match(p) or OTHER_ARTIFACT.match(p):
            notes += 1
            print(f"scope-paths note: {p} is another session's")
            continue
        problems.append(f"scope-paths: {p} is outside §Files Modified")
    print(f"scope-paths: {len(changed)} changed, {kept} in scope, {notes} note(s)")
    return problems


def _hash_now(root: pathlib.Path, path: str) -> str | None:
    if not (root / path).is_file():
        return None
    return _git(root, "hash-object", f"--path={path}", "--", path).decode("utf-8").strip()


def _blob(root: pathlib.Path, commit: str, path: str) -> str | None:
    listed = _git(root, "ls-tree", commit, "--", path).decode("utf-8").strip()
    return listed.split()[2] if listed else None


def run_reason_ok(reason: str, code: str) -> bool:
    """tools/e2e_remote.py ends a passing run `e2e-remote: ok exit=0` (REASONS, D-1585)."""
    return reason == "ok" and code == "0"


def remote_run_2(ctx: Ctx) -> list[str]:
    problems: list[str] = []
    snap = json.loads((ctx.r / SNAP_16).read_text(encoding="utf-8"))
    commit = str(snap["commit"])
    lines = [m for ln in _lines_of(ctx.r / RUN_17) if (m := E2E_LINE.match(ln))]
    if not lines:
        return [f"remote-run-2: {RUN_17} has no e2e-remote line"]
    reason, code, run, receipts = lines[-1].groups()
    print(f"remote-run-2: run {run} {reason} exit={code}; snapshot {commit[:12]}")
    if not run_reason_ok(reason, code):
        problems.append(f"remote-run-2: run {run} ended {reason} exit={code}")
    summary_p = pathlib.Path(receipts) / "summary.json"
    if not summary_p.is_file():
        problems.append(f"remote-run-2: no summary.json under {receipts}")
    else:
        summary = json.loads(summary_p.read_text(encoding="utf-8"))
        if summary.get("commit") != commit:
            problems.append(f"remote-run-2: the run archived {summary.get('commit')}, not {commit}")
        if summary.get("run_id") != run:
            problems.append(f"remote-run-2: summary.json names run {summary.get('run_id')}")
    checked = _lines_of(ctx.r / RUN_CHECK_17)
    if not checked or checked[-1].strip() != "run-check: 0 problem(s)":
        problems.append(f"remote-run-2: {RUN_CHECK_17} does not end with 0 problem(s)")
    product = sorted(p for p in SCOPE if p.startswith(PRODUCT))
    differ = [p for p in product if _hash_now(ctx.root, p) != _blob(ctx.root, commit, p)]
    for p in differ:
        problems.append(f"remote-run-2: {p} changed since snapshot {commit[:12]}")
    print(f"remote-run-2: {len(product)} product path(s), {len(differ)} changed since the snapshot")
    return problems


def _lines_of(path: pathlib.Path) -> list[str]:
    if not path.is_file():
        return []
    return [ln for ln in path.read_text(encoding="utf-8", errors="replace").splitlines() if ln]


def register(ctx: Ctx) -> list[str]:
    got = _issues(ctx.now(REGISTER), REGISTER).get(ISSUE, {}).get("status")
    print(f"register {ISSUE}: {got}")
    return [] if got == "resolved" else [f"register: {ISSUE} is {got}, not resolved"]


def status(ctx: Ctx, meus: list[str], want: str) -> list[str]:
    found = _meus(ctx.now(MEU_STATUS))
    problems: list[str] = []
    for m in meus:
        got = found.get(m, {}).get("status")
        print(f"status {m}: {got}")
        if got != want:
            problems.append(f"status: {m} is {got}, not {want}")
    return problems


# --- selftest
def _put(base: pathlib.Path, files: dict[str, bytes | str]) -> None:
    for name, data in files.items():
        p = base / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)


def _ctx(tmp: pathlib.Path, tag: str) -> Ctx:
    ctx = Ctx(tmp / tag / "root", tmp / tag / "r", HERE)
    for p in (ctx.root, ctx.r, ctx.copies):
        p.mkdir(parents=True, exist_ok=True)
    return ctx


def _openapi(prop: bool, crlf: bool) -> bytes:
    props = {"log_level": {"type": "string"}}
    if prop:
        props["update_interval"] = {"type": "string"}
    doc = {"components": {"schemas": {"SettingsPutIn": {"properties": props}}}}
    text = json.dumps(doc, indent=2) + "\n"
    return (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")


REGISTER_FIX = "issues:\n- id: APP-NO-IN-APP-UPDATE\n  status: {s}\n- id: OTHER\n  status: open\n"
MEU_FIX = (
    "phases:\n  p1:\n  - id: MEU-173\n    row_key: a\n    status: {a}\n"
    "  - id: MEU-174\n    row_key: b\n    status: {b}\n"
)


def selftest() -> int:
    cases: list[tuple[str, Callable[[pathlib.Path], list[str]], bool]] = []

    def red_ok(tmp: pathlib.Path) -> list[str]:
        ctx = _ctx(tmp, "red-ok")
        _put(ctx.root, {"t/a.test.ts": "a\n"})
        return red_record(ctx, "1", ["t/a.test.ts"]) + red_unchanged(ctx)

    def red_changed(tmp: pathlib.Path) -> list[str]:
        ctx = _ctx(tmp, "red-changed")
        _put(ctx.root, {"t/a.test.ts": "a\n"})
        red_record(ctx, "1", ["t/a.test.ts"])
        _put(ctx.root, {"t/a.test.ts": "b\n"})
        return red_unchanged(ctx)

    def red_rerecord(tmp: pathlib.Path) -> list[str]:
        ctx = _ctx(tmp, "red-rerecord")
        _put(ctx.root, {"t/a.test.ts": "a\n"})
        red_record(ctx, "1", ["t/a.test.ts"])
        _put(ctx.root, {"t/a.test.ts": "b\n"})
        return red_record(ctx, "1", ["t/a.test.ts"])

    def red_none(tmp: pathlib.Path) -> list[str]:
        return red_unchanged(_ctx(tmp, "red-none"))

    def leaf(prop: bool, crlf: bool, tag: str) -> Callable[[pathlib.Path], list[str]]:
        def run(tmp: pathlib.Path) -> list[str]:
            ctx = _ctx(tmp, tag)
            _put(ctx.root, {OPENAPI: _openapi(prop, crlf)})
            return openapi_leaf(ctx)

        return run

    def exe(size: int, tag: str) -> Callable[[pathlib.Path], list[str]]:
        def run(tmp: pathlib.Path) -> list[str]:
            ctx = _ctx(tmp, tag)
            if size:
                _put(ctx.root, {ELECTRON_EXE: b"\0" * size})
            return electron_binary(ctx)

        return run

    def macro(body: str, record_body: str, tag: str) -> Callable[[pathlib.Path], list[str]]:
        def run(tmp: pathlib.Path) -> list[str]:
            ctx = _ctx(tmp, tag)
            _put(ctx.root, {NSH: body})
            rec = ctx.r / "macro.json"
            want = hashlib.sha256(record_body.encode()).hexdigest()
            _put(ctx.r, {"macro.json": json.dumps({"working_sha256": want})})
            return macro_current(ctx, rec)

        return run

    def reg(s: str, tag: str) -> Callable[[pathlib.Path], list[str]]:
        def run(tmp: pathlib.Path) -> list[str]:
            ctx = _ctx(tmp, tag)
            _put(ctx.root, {REGISTER: REGISTER_FIX.format(s=s)})
            return register(ctx)

        return run

    def stat(a: str, b: str, want: str, tag: str) -> Callable[[pathlib.Path], list[str]]:
        def run(tmp: pathlib.Path) -> list[str]:
            ctx = _ctx(tmp, tag)
            _put(ctx.root, {MEU_STATUS: MEU_FIX.format(a=a, b=b)})
            return status(ctx, list(MEUS), want)

        return run

    def canon_case(after: str, tag: str) -> Callable[[pathlib.Path], list[str]]:
        def run(tmp: pathlib.Path) -> list[str]:
            ctx = _ctx(tmp, tag)
            _put(ctx.r / "canon-before", {"docs/x.md": "a planned b\n"})
            _put(ctx.root, {"docs/x.md": after})
            return canon(ctx, {"docs/x.md": [("planned", "done")]})

        return run

    with_macro = f"{MACRO}\n!macroend\n"
    cases += [
        ("red-record then red-unchanged passes", red_ok, True),
        ("red-unchanged fails on a changed Red file", red_changed, False),
        ("red-record refuses a row recorded with other hashes", red_rerecord, False),
        ("red-unchanged fails with no record", red_none, False),
        ("openapi-leaf passes on CRLF with the leaf", leaf(True, True, "leaf-ok"), True),
        ("openapi-leaf fails without the leaf", leaf(False, True, "leaf-missing"), False),
        ("openapi-leaf fails on LF", leaf(True, False, "leaf-lf"), False),
        ("electron-binary passes on a 2 MB file", exe(2_000_000, "exe-ok"), True),
        ("electron-binary fails when absent", exe(0, "exe-absent"), False),
        ("electron-binary fails when truncated", exe(10, "exe-small"), False),
        ("macro-current passes when unchanged", macro(with_macro, with_macro, "m-ok"), True),
        ("macro-current fails when changed", macro(with_macro + "x\n", with_macro, "m-chg"), False),
        ("macro-current fails without the macro", macro("x\n", "x\n", "m-none"), False),
        ("register passes on resolved", reg("resolved", "reg-ok"), True),
        ("register fails on open", reg("open", "reg-open"), False),
        ("status passes when both match", stat("approved", "approved", "approved", "s-ok"), True),
        ("status fails when one differs", stat("approved", "planned", "approved", "s-no"), False),
        ("canon passes on the edited bytes", canon_case("a done b\n", "c-ok"), True),
        ("canon fails on other bytes", canon_case("a planned b\n", "c-no"), False),
        (
            "remote-run-2 takes ok exit=0",
            lambda _t: [] if run_reason_ok("ok", "0") else ["no"],
            True,
        ),
        (
            "remote-run-2 refuses install-failures exit=41",
            lambda _t: [] if run_reason_ok("install-failures", "41") else ["no"],
            False,
        ),
        (
            "remote-run-2 refuses green",
            lambda _t: [] if run_reason_ok("green", "0") else ["no"],
            False,
        ),
    ]
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        for name, fn, want_pass in cases:
            crashed = False
            try:
                problems = fn(tmp)
            except Exception as exc:  # noqa: BLE001 - a crash is a bad case either way
                problems, crashed = [f"crash: {type(exc).__name__}: {exc}"], True
            ok = not crashed and (not problems) == want_pass
            bad += 0 if ok else 1
            print(f"selftest {'ok ' if ok else 'BAD'} {name}: {len(problems)} problem(s)")
    print(f"row-check selftest: {len(cases) - bad}/{len(cases)} ok")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    ctx = Ctx()
    simple: dict[str, Callable[[Ctx], list[str]]] = {
        "red-unchanged": red_unchanged,
        "openapi-leaf": openapi_leaf,
        "electron-binary": electron_binary,
        "canon": canon,
        "register": register,
        "scope-paths": scope_paths,
        "remote-run-2": remote_run_2,
    }
    try:
        if cmd in simple and not rest:
            problems = simple[cmd](ctx)
        elif cmd == "red-record" and len(rest) >= 3 and rest[0] == "--row":
            problems = red_record(ctx, rest[1], rest[2:])
        elif cmd == "status" and len(rest) >= 2 and all(m.startswith("MEU-") for m in rest[:-1]):
            problems = status(ctx, rest[:-1], rest[-1])
        elif cmd == "macro-current" and len(rest) == 1:
            problems = macro_current(ctx, pathlib.Path(rest[0]))
        else:
            raise ValueError(f"unknown or malformed subcommand {cmd!r} {rest}")
    except ValueError as exc:
        print(f"usage: {exc}")
        return 2
    for p in problems:
        print("PROBLEM:", p)
    print(f"row-check {cmd}: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
