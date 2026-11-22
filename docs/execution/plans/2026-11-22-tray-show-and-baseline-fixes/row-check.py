"""Session 102 row checks (task rows 1 to 7 and the gate; implementation-plan.md §Verification).

Written in the shape of Session 101's (2026-11-21-transcript-job-resume/row-check.py), whose
red-record, red-unchanged, red-reason, e2e-count and register checks it keeps. Subcommands (each
exits 0 when it finds no problem, 1 when it does, 2 on a usage error):

* ``red-record --row N FILE ...``: writes the files' SHA-256 under the row in
  ``tsb-red-hashes.json`` and copies their bytes to ``tsb-red-copies/row<N>/``. A row already
  recorded with other hashes is refused (a Red file never changes after its row).
  ``tests/unit/test_capture_adapter.py`` is never recorded: row 2 changes the helper's body in
  it, and ``named-edits`` checks it node by node instead.
* ``red-unchanged``: every file in ``tsb-red-hashes.json`` still has the hash of the latest row
  that recorded it.
* ``pins-unchanged``: every ``baseline-pins.json`` file hash; every top-level node of
  ``test_capture_adapter.py`` except AC-130.10, and of ``validate_closeout_artifacts.py``
  except ``plan_slug``, parsed now with ``ast``, equal to row 0's source.
* ``red-reason RECEIPT --id ID [--id ID ...] --needle TEXT``: in the Playwright receipt each id
  has a failing block, and every block of that id fails by an assertion first, holds no launch,
  seed or timeout line, and has ``TEXT`` in its message (the lines before the first code frame
  line; the code frame quotes the test source, so it never counts).
* ``e2e-count RECEIPT N [--plain RECEIPT ...]``: the first receipt has ``N`` lines matching
  ``^ +ok +[0-9]+ .*AC-164\\.`` and an ``N passed`` line; each ``--plain`` receipt has a pass
  count; no receipt has a ``failed``, ``flaky`` or ``unhandled rejection:`` line.
* ``named-edits --stage red|green``: ``ICC_HEADER_MASK`` by top-level ``ast`` node of
  ``test_capture_adapter.py`` against ``baseline-pins.json``. The new nodes are exactly the
  helper (just before AC-130.10) and the two ``test_ac_164_8_`` tests (just after it); nothing is
  removed; the only changed node is AC-130.10, which differs from row 0 in its one comparison
  line only and still starts at its first decorator. The helper equals the stage's form in
  ``debt-edit.py``, the two tests equal the forms there, and the file has no bare LF.
* ``slug-edit``: ``PLAN_SLUG_PARENT_ONLY``. In ``validate_closeout_artifacts.py`` only
  ``plan_slug`` changed, from ``debt-edit.py``'s old form to its new form; the node order is
  row 0's, and the file has no bare LF.
* ``canon``: AC-164.7. 09 against its row-0 copy, by CRLF lines: the tray row is
  ``TRAY_ROW_NEW``; right after §Tray double-click's Menu row come a blank line,
  ``> **Delivered (Session 102).**`` and one or more ``> - `` lines naming every
  ``DELIVERED_TOKENS`` entry; every other line is row 0's; no bare LF.
* ``register``: ``known-issues.yaml`` now and its row-0 copy, parsed with ``yaml.safe_load`` and
  keyed by issue id: the same ids, every other issue equal, and the three issues resolved and
  different only in ``status``, ``verification`` and ``resolution_path``. In the grouping file
  only §6 row 102 changed, from ``planned`` to ``executed (Session 102)``.
* ``--selftest``: every subcommand on fixtures in a temporary folder.

The Playwright block grammar is red-check.py's and the edit forms are debt-edit.py's, both
loaded by path. ``top_level_sources`` is the one function row 0 used to write
``baseline-pins.json`` (baseline.ps1 imports it). ``canon-edit.py`` (row 7) imports the canon
texts below.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import tempfile

import yaml

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RECEIPTS = pathlib.Path("C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes")
COPIES = RECEIPTS / "baseline-copies"
PINS = HERE / "baseline-pins.json"
RED_STORE = "tsb-red-hashes.json"
RED_COPIES = "tsb-red-copies"

CANON = "docs/build-plan/09-screenshot-capture.md"
REGISTER = ".agent/context/known-issues.yaml"
GROUPING = ".agent/context/grouping/2026-11-22-tray-show-and-baseline-fixes-session-grouping.md"
ISSUES = (
    "TRAY-DOUBLE-CLICK-NO-SHOW",
    "TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE",
    "TOOLING-PLAN-SLUG-ANCESTOR-MATCH",
)
ISSUE_FIELDS = {"status", "verification", "resolution_path"}

OK_LINE = re.compile(r"^ +ok +[0-9]+ .*AC-164\.")
PASSED = re.compile(r"^\s*(\d+) passed\b")
E2E_BAD = re.compile(r"^\s*\d+ (?:failed|flaky)\b|unhandled rejection:", re.IGNORECASE)

# --- the plan's canon texts (Proposed Changes MEU-164 step 2; canon-edit.py imports them)
TRAY_ROW_OLD = (
    "| Tray icon | Electron main | Always created while the app runs. "
    "Menu: Show window, Capture region, Open inbox folder, Quit |"
)
TRAY_ROW_NEW = (
    "| Tray icon | Electron main | Always created while the app runs. "
    "Menu: Show window, Capture region, Open inbox folder, Quit. "
    "A double-click on the icon runs Show window (MEU-164) |"
)
MENU_PREFIX = "| Menu | The tray menu keeps its four items"
DELIVERED_HEAD = "> **Delivered (Session 102).**"
DELIVERED_TOKENS = (
    "TRAY_SHOW_SHARED",
    "restore",
    "TRAY_E2E_HOOK",
    "capture-tray.test.ts",
    "tray-double-click.test.ts",
    "D-1365",
    "D-1368",
)
GROUPING_OLD = "| planned |"
GROUPING_NEW = "| executed (Session 102) |"


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rc = _load("tsb_red_check", "red-check.py")
dbt = _load("tsb_debt_edit", "debt-edit.py")
ADAPTER, VALIDATOR = dbt.ADAPTER, dbt.VALIDATOR


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: pathlib.Path, root: pathlib.Path) -> str:
    path = path if path.is_absolute() else root / path
    return path.resolve().relative_to(root.resolve()).as_posix()


# --- top-level sources (row 0's baseline-pins.json and the checks below)
def _node_key(node: ast.stmt, source: str) -> str:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name
    if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) for t in node.targets):
        return ",".join(t.id for t in node.targets if isinstance(t, ast.Name))
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id
    return f"{type(node).__name__}:{source}"


def top_level_sources(text: str) -> dict[str, str]:
    """Each top-level node's source (LF), from its first decorator to its last line, by name.

    A doubled key gets ``#2``, ``#3`` in file order. The dict keeps the file's order.
    """
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")
    out: dict[str, str] = {}
    for node in ast.parse(text).body:
        decorators = getattr(node, "decorator_list", [])
        start = min([node.lineno, *(d.lineno for d in decorators)])
        end = node.end_lineno or node.lineno
        source = "\n".join(lines[start - 1 : end])
        key = base = _node_key(node, source)
        n = 2
        while key in out:
            key = f"{base}#{n}"
            n += 1
        out[key] = source
    return out


def _sources(root: pathlib.Path, name: str) -> dict[str, str]:
    return top_level_sources((root / name).read_bytes().decode("utf-8"))


def _bare_lf(raw: bytes) -> int:
    return raw.count(b"\n") - raw.count(b"\r\n")


# --- red-record, red-unchanged, pins-unchanged
def _red_data(record: pathlib.Path) -> dict:
    if not record.is_file():
        return {"order": [], "rows": {}}
    return json.loads(record.read_text(encoding="utf-8"))


def red_record(row: str, files: list[str], root: pathlib.Path, store: pathlib.Path) -> list[str]:
    record = store / RED_STORE
    data = _red_data(record)
    entry: dict[str, str] = {}
    for f in files:
        p = pathlib.Path(f)
        p = p if p.is_absolute() else root / p
        if not p.is_file():
            return [f"red-record: {f} is not a file"]
        name = rel(p, root)
        if name == ADAPTER:
            return [f"red-record: {ADAPTER} is checked by named-edits, never hash-recorded"]
        entry[name] = sha(p)
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
    record.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    for name, h in entry.items():
        print(f"red-record row {row}: {name} {h}")
    return []


def red_unchanged(root: pathlib.Path, store: pathlib.Path) -> list[str]:
    record = store / RED_STORE
    if not record.is_file():
        return [f"red-unchanged: {record} missing"]
    data = _red_data(record)
    latest: dict[str, tuple[str, str]] = {}
    for row in data["order"]:
        for name, want in data["rows"][row].items():
            latest[name] = (row, want)
    problems: list[str] = []
    for name, (row, want) in sorted(latest.items()):
        p = root / name
        got = sha(p) if p.is_file() else "absent"
        print(f"red-unchanged {name} (latest row {row}): {'ok' if got == want else 'CHANGED'}")
        if got != want:
            problems.append(f"red-unchanged: {name} (row {row}) is {got[:16]}, not {want[:16]}")
    if not latest:
        problems.append("red-unchanged: no file recorded")
    return problems


#: The one node per pinned Python file that a row may change.
EDITABLE = {ADAPTER: dbt.AC_130_10, VALIDATOR: dbt.PLAN_SLUG_FN}


def pins_unchanged(root: pathlib.Path, pins: pathlib.Path) -> list[str]:
    data = json.loads(pins.read_text(encoding="utf-8"))
    problems: list[str] = []
    for name, want in sorted(data["files"].items()):
        p = root / name
        got = sha(p) if p.is_file() else "absent"
        print(f"pins-unchanged: {name} {'ok' if got == want else 'CHANGED'}")
        if got != want:
            problems.append(f"pins-unchanged: {name} is {got[:16]}, not {want[:16]}")
    for name, editable in EDITABLE.items():
        if name not in data["ast"]:
            problems.append(f"pins-unchanged: no ast pin for {name}")
            continue
        base, now = data["ast"][name], _sources(root, name)
        checked = [k for k in base if k != editable]
        for key in checked:
            if now.get(key) != base[key]:
                state = "missing" if key not in now else "changed"
                problems.append(f"pins-unchanged: {name}::{key[:60]} {state}")
        print(f"pins-unchanged: {name}: {len(checked)} node(s) besides {editable}")
        if not checked:
            problems.append(f"pins-unchanged: {name}: no node recorded")
    if not data["files"]:
        problems.append("pins-unchanged: no pin file recorded")
    return problems


# --- red-reason
def red_reason(receipt: pathlib.Path, ids: list[str], needle: str) -> list[str]:
    text = rc.ANSI_ESCAPE.sub("", receipt.read_text(encoding="utf-8", errors="replace"))
    blocks = rc._blocks("playwright", text.splitlines())
    problems: list[str] = []
    for wanted in ids:
        matched = [b for b in blocks if any(rc._title_matches(t, wanted) for t in b.titles)]
        if not matched:
            problems.append(f"red-reason: {wanted} has no failing block")
        for b in matched:
            hard = [line.strip() for line in b.lines if rc.HARD_SETUP_FAILURE.search(line)]
            first = b.diagnostics[0] if b.diagnostics else ("", "none")
            message: list[str] = []
            for line in b.lines:
                if rc.CODE_FRAME.match(line):
                    break
                message.append(line)
            found = any(needle in line for line in message)
            print(f"red-reason {wanted}: first {first[1]} {first[0][:70]!r}; needle {found}")
            if hard:
                problems.append(f"red-reason: {wanted} fails on setup: {hard[:2]}")
            if first[1] != "assertion":
                problems.append(f"red-reason: {wanted}'s first diagnostic is {first[1]}")
            if not found:
                problems.append(f"red-reason: {wanted}'s message lacks {needle!r}")
    return problems


# --- e2e-count
def e2e_count(receipt: pathlib.Path, n: int, plain: list[pathlib.Path]) -> list[str]:
    problems: list[str] = []
    for i, path in enumerate([receipt, *plain]):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        bad = [line.strip() for line in lines if E2E_BAD.search(line)]
        if bad:
            problems.append(f"e2e-count: {path.name}: {bad[:5]}")
        passes = [int(m.group(1)) for line in lines if (m := PASSED.match(line))]
        if i == 0:
            ok = sum(1 for line in lines if OK_LINE.match(line))
            print(f"e2e-count {path.name}: {ok} AC-164 ok lines, passed {passes}, want {n}")
            if ok != n:
                problems.append(f"e2e-count: {path.name}: {ok} AC-164 ok lines, not {n}")
            if passes != [n]:
                problems.append(f"e2e-count: {path.name}: passed {passes}, not [{n}]")
        else:
            print(f"e2e-count {path.name}: passed {passes}")
            if len(passes) != 1 or passes[0] < 1:
                problems.append(f"e2e-count: {path.name}: no single pass count ({passes})")
    return problems


# --- named-edits and slug-edit
def _doubled(label: str, *maps: dict[str, str]) -> None:
    doubled = sorted({k for m in maps for k in m if "#" in k.split(":", 1)[0]})
    if doubled:
        print(f"note: {label}: doubled top-level keys {doubled}")


def _node_problems(
    label: str,
    base: dict[str, str],
    now: dict[str, str],
    forms: dict[str, tuple[str | None, str]],
) -> list[str]:
    """New nodes are the forms with no old text; changed nodes are the others; none removed."""
    problems: list[str] = []
    added_want = {k for k, (old, _) in forms.items() if old is None}
    changed_want = {k for k, (old, _) in forms.items() if old is not None}
    added, gone = set(now) - set(base), set(base) - set(now)
    changed = {k for k in set(base) & set(now) if base[k] != now[k]}
    print(f"{label}: added {sorted(added)}, removed {sorted(gone)}, changed {sorted(changed)}")
    if added != added_want:
        problems.append(f"{label}: added {sorted(added)}, not {sorted(added_want)}")
    if gone:
        problems.append(f"{label}: removed {sorted(gone)}")
    if changed != changed_want:
        problems.append(f"{label}: changed {sorted(changed)}, not {sorted(changed_want)}")
    for key, (old, new) in forms.items():
        if old is not None and base.get(key) != old:
            problems.append(f"{label}: row 0's {key} is not the plan's old form")
        if now.get(key) != new:
            problems.append(f"{label}: {key} is not the plan's form")
    return problems


def named_edits(stage: str, root: pathlib.Path, pins: pathlib.Path) -> list[str]:
    data = json.loads(pins.read_text(encoding="utf-8"))
    label = f"named-edits {stage}: {ADAPTER}"
    problems: list[str] = []
    raw = (root / ADAPTER).read_bytes()
    if _bare_lf(raw):
        problems.append(f"{label}: {_bare_lf(raw)} bare LF")
    base, now = data["ast"][ADAPTER], top_level_sources(raw.decode("utf-8"))
    _doubled(label, base, now)
    old_130 = base.get(dbt.AC_130_10, "")
    line_old, line_new = dbt.AC_130_10_LINE_OLD.rstrip("\n"), dbt.AC_130_10_LINE_NEW.rstrip("\n")
    if old_130.count(line_old) != 1:
        problems.append(f"{label}: row 0's AC-130.10 holds its comparison line not once")
    if not old_130.startswith(dbt.AC_130_10_HEAD):
        problems.append(f"{label}: row 0's AC-130.10 does not start at its first decorator")
    helper = dbt.HELPER_RED if stage == "red" else dbt.HELPER_GREEN
    forms: dict[str, tuple[str | None, str]] = {
        dbt.HELPER: (None, helper),
        dbt.AC_130_10: (old_130, old_130.replace(line_old, line_new)),
        **{name: (None, src) for name, src in dbt.TESTS.items()},
    }
    problems += _node_problems(label, base, now, forms)
    want: list[str] = []
    for key in base:
        if key == dbt.AC_130_10:
            want += [dbt.HELPER, key, *dbt.AC_164_8]
        else:
            want.append(key)
    if list(now) != want:
        problems.append(f"{label}: the node order is not the planned order")
    return problems


def slug_edit(root: pathlib.Path, pins: pathlib.Path) -> list[str]:
    data = json.loads(pins.read_text(encoding="utf-8"))
    label = f"slug-edit: {VALIDATOR}"
    problems: list[str] = []
    raw = (root / VALIDATOR).read_bytes()
    if _bare_lf(raw):
        problems.append(f"{label}: {_bare_lf(raw)} bare LF")
    base, now = data["ast"][VALIDATOR], top_level_sources(raw.decode("utf-8"))
    _doubled(label, base, now)
    forms: dict[str, tuple[str | None, str]] = {
        dbt.PLAN_SLUG_FN: (dbt.PLAN_SLUG_OLD, dbt.PLAN_SLUG_NEW)
    }
    problems += _node_problems(label, base, now, forms)
    if list(now) != list(base):
        problems.append(f"{label}: the node order changed")
    return problems


# --- canon
def _pair(root: pathlib.Path, copies: pathlib.Path, name: str) -> tuple[bytes, bytes]:
    return (copies / name).read_bytes(), (root / name).read_bytes()


def canon(root: pathlib.Path, copies: pathlib.Path) -> list[str]:
    base_raw, now_raw = _pair(root, copies, CANON)
    problems: list[str] = []
    if _bare_lf(base_raw) or _bare_lf(now_raw):
        problems.append(f"canon: bare LF (row 0 {_bare_lf(base_raw)}, now {_bare_lf(now_raw)})")
    base = base_raw.decode("utf-8").split("\r\n")
    now = now_raw.decode("utf-8").split("\r\n")
    tray = [i for i, line in enumerate(base) if line == TRAY_ROW_OLD]
    menu = [i for i, line in enumerate(base) if line.startswith(MENU_PREFIX)]
    if len(tray) != 1 or len(menu) != 1 or not tray[0] < menu[0]:
        return [*problems, f"canon: row 0 has the tray row at {tray}, the Menu row at {menu}"]
    t, m = tray[0], menu[0]
    head = now[: m + 1]
    want_head = base[: m + 1]
    want_head[t] = TRAY_ROW_NEW
    if head != want_head:
        diff = [i + 1 for i, (a, b) in enumerate(zip(head, want_head, strict=False)) if a != b]
        problems.append(f"canon: lines up to the Menu row differ from the plan at {diff[:5]}")
    rest = base[m + 1 :]
    block = now[m + 1 : len(now) - len(rest)] if len(now) > m + 1 + len(rest) else []
    if now[len(now) - len(rest) :] != rest:
        problems.append("canon: the lines after the Delivered note differ from row 0")
    bullets = block[2:]
    shape = (
        len(block) >= 3
        and block[0] == ""
        and block[1] == DELIVERED_HEAD
        and all(line.startswith("> - ") for line in bullets)
    )
    print(f"canon: tray row at {t + 1}; Delivered note after line {m + 1}: {len(block)} line(s)")
    if not shape:
        problems.append(f"canon: the Delivered note is not blank, head, bullets: {block[:3]}")
    text = "\n".join(bullets)
    missing = [tok for tok in DELIVERED_TOKENS if tok not in text]
    if missing:
        problems.append(f"canon: the Delivered note lacks {missing}")
    if now.count(DELIVERED_HEAD) != 1:
        problems.append(f"canon: {DELIVERED_HEAD} occurs {now.count(DELIVERED_HEAD)} times")
    return problems


# --- register
def _issues(raw: bytes, label: str) -> dict[str, dict]:
    data = yaml.safe_load(raw.decode("utf-8"))
    ids = [i.get("id") for i in data["issues"]]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{label}: doubled issue ids")
    return {i["id"]: i for i in data["issues"]}


def register(root: pathlib.Path, copies: pathlib.Path) -> list[str]:
    problems: list[str] = []
    base_raw, now_raw = _pair(root, copies, REGISTER)
    base, now = _issues(base_raw, "row 0"), _issues(now_raw, "now")
    if set(base) != set(now):
        problems.append(
            f"register: ids added {sorted(set(now) - set(base))}, "
            f"removed {sorted(set(base) - set(now))}"
        )
    for key in sorted(set(base) & set(now)):
        if key not in ISSUES and base[key] != now[key]:
            problems.append(f"register: {key} changed")
    for issue in ISSUES:
        if issue not in now or issue not in base:
            problems.append(f"register: {issue} is missing")
            continue
        a, b = base[issue], now[issue]
        changed = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
        print(f"register: {issue} changed fields {sorted(changed)}; status {b.get('status')}")
        if changed - ISSUE_FIELDS:
            problems.append(f"register: {issue} also changed {sorted(changed - ISSUE_FIELDS)}")
        if b.get("status") != "resolved":
            problems.append(f"register: {issue} status is {b.get('status')!r}, not 'resolved'")
    print(f"register: {len(now)} issues now, {len(base)} at row 0")
    g_base, g_now = _pair(root, copies, GROUPING)
    if b"\r" in g_now:
        problems.append(f"register: {GROUPING} has a CR")
    old_lines, new_lines = g_base.split(b"\n"), g_now.split(b"\n")
    rows = [i for i, line in enumerate(old_lines) if line.startswith(b"| 102 |")]
    if len(rows) != 1 or len(old_lines) != len(new_lines):
        return [*problems, f"register: grouping row 102 at {rows}; {len(new_lines)} lines now"]
    old_row = old_lines[rows[0]]
    want = old_row.replace(GROUPING_OLD.encode(), GROUPING_NEW.encode())
    if old_row.count(GROUPING_OLD.encode()) != 1:
        problems.append("register: grouping row 102 did not read planned once at row 0")
    for i, (a, b) in enumerate(zip(old_lines, new_lines, strict=True)):
        if b != (want if i == rows[0] else a):
            problems.append(f"register: {GROUPING}:{i + 1} is {b[:90]!r}")
    return problems


# --- selftest
PW_FILE = "tests\\e2e\\tray-double-click.test.ts"
ARROW = "\u0393\u00c7\u2551"
TRAY_HOOK = [
    "Error: expect(tray hook)",
    "",
    "Expected: true",
    "Received: false",
    "",
    "Call Log:",
    "- Timeout 10000ms exceeded while waiting on the predicate",
    "",
    "  30 |   await expect",
    "> 31 |     .poll(() => app.evaluate(() => Boolean(globalThis.__AVKIT_E2E_TRAY__)), {",
    "     |      ^",
]
NO_NEEDLE = [
    "Error: expect(received).toBe(expected) // Object.is equality",
    "",
    "Expected: true",
    "Received: false",
    "",
    "> 31 |     .poll(() => app.evaluate(() => Boolean(globalThis.__AVKIT_E2E_TRAY__)), {",
    "> 32 |       message: 'expect(tray hook)',",
]
LAUNCH = [
    "Error: electron.launch: Process failed to launch!",
    "",
    "> 12 |   const app = await launchElectron(); // tray hook",
]
SEED = [
    "TypeError: Cannot read properties of undefined (reading 'show')",
    "",
    "tray hook",
]


def _pw(blocks: list[tuple[str, list[str]]], passed: int) -> str:
    out = [f"Running {len(blocks) + passed} tests using 1 worker", ""]
    for i, (title, body) in enumerate(blocks, 1):
        out += [f"  {i}) [electron] {ARROW} {PW_FILE}:{20 + i}:1 {ARROW} {title} ", ""]
        out += [f"    {line}" for line in body] + [""]
    out += [f"  {len(blocks)} failed"]
    out += [f"    [electron] {ARROW} {PW_FILE}:21:1 {ARROW} {t}" for t, _ in blocks]
    out += [f"  {passed} passed (14.2s)"]
    return "\n".join(out) + "\n"


ADAPTER_HEAD = """from __future__ import annotations

import pytest"""
ADAPTER_CROP = """@pytest.mark.parametrize("ac_id", ["AC-130.10"], ids=["AC-130.10"])
@pytest.mark.unit
def test_ac_130_10_crop_keeps_icc_and_drops_the_rest(ac_id: str) -> None:
    assert ac_id"""
ADAPTER_130 = """@pytest.mark.parametrize("ac_id", ["AC-130.10"], ids=["AC-130.10"])
@pytest.mark.unit
def test_ac_130_10_cmyk_icc_to_srgb(ac_id: str, tmp_path) -> None:
    srgb = cropped = managed = tmp_path
    if ac_id:
        assert cropped.info.get("icc_profile") == srgb.tobytes()
        assert cropped.tobytes() == managed.tobytes()"""
ADAPTER_PLAIN = """@pytest.mark.parametrize("ac_id", ["AC-130.10"], ids=["AC-130.10"])
@pytest.mark.unit
def test_ac_130_10_cmyk_plain_fallback(ac_id: str) -> None:
    assert ac_id"""
VALIDATOR_HEAD = """import re
from pathlib import Path

PLAN_SLUG = re.compile(r"(\\d{4}-\\d{2}-\\d{2}-[a-z0-9][a-z0-9-]*)")


class Usage(Exception):
    pass"""
VALIDATOR_TAIL = """def main() -> int:
    return 0"""


def _crlf_text(parts: list[str]) -> bytes:
    return ("\n\n\n".join(parts) + "\n").replace("\n", "\r\n").encode("utf-8")


def selftest() -> int:
    failures: list[str] = []

    def case(name: str, problems: list[str], want_pass: bool) -> None:
        ok = not problems
        why = "" if ok else f" -- {problems[0][:110]}"
        print(
            f"{name}: {'pass' if ok else 'refused'} "
            f"(expected {'pass' if want_pass else 'refused'}){why}"
        )
        if ok != want_pass:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        t = pathlib.Path(tmp)
        root, store, copies = t / "repo", t / "store", t / "copies"

        def put(base: pathlib.Path, name: str, data: str | bytes) -> None:
            p = base / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)

        # top_level_sources
        src = "import os\n\n\n@dec\ndef f():\n    return 1\n\n\nX = 1\nX = 2\nos.getcwd()\n"
        nodes = top_level_sources(src.replace("\n", "\r\n"))
        want_keys = ["Import:import os", "f", "X", "X#2", "Expr:os.getcwd()"]
        ok = list(nodes) == want_keys and nodes["f"] == "@dec\ndef f():\n    return 1"
        case("top-level-sources", [] if ok else [f"got {list(nodes)}"], True)

        # red-record and red-unchanged
        slug_test = "tests/tooling/test_closeout_plan_slug.py"
        put(root, slug_test, "a\n")
        put(root, "ui/tests/unit/capture-tray.test.ts", "b\n")
        put(root, ADAPTER, "c\r\n")
        case("red-unchanged-no-record", red_unchanged(root, store), False)
        case("red-record-row1", red_record("1", [slug_test], root, store), True)
        case(
            "red-record-row3",
            red_record("3", ["ui/tests/unit/capture-tray.test.ts"], root, store),
            True,
        )
        case("red-record-adapter-refused", red_record("9", [ADAPTER], root, store), False)
        copy = store / RED_COPIES / "row1" / slug_test
        copied = copy.is_file() and copy.read_bytes() == b"a\n"
        case("red-record-copied", [] if copied else ["copy missing"], True)
        case("red-record-row1-again-same", red_record("1", [slug_test], root, store), True)
        case("red-unchanged-ok", red_unchanged(root, store), True)
        put(root, slug_test, "a edited\n")
        case("red-unchanged-changed", red_unchanged(root, store), False)
        case("red-record-row1-other-hashes", red_record("1", [slug_test], root, store), False)
        order = json.loads((store / RED_STORE).read_text(encoding="utf-8"))["order"]
        case("red-record-order", [] if order == ["1", "3"] else [str(order)], True)
        case("red-record-missing-file", red_record("5", ["ui/none.ts"], root, store), False)

        # debt-edit forms applied through debt-edit.apply, then pins, named-edits, slug-edit
        adapter0 = _crlf_text([ADAPTER_HEAD, ADAPTER_CROP, ADAPTER_130, ADAPTER_PLAIN])
        validator0 = _crlf_text([VALIDATOR_HEAD, dbt.PLAN_SLUG_OLD, VALIDATOR_TAIL])
        adapter_red, p_red = dbt.apply(adapter0, dbt.red_edits(), ADAPTER)
        green = dbt.green_edits()
        adapter_green, p_green = dbt.apply(adapter_red, green[ADAPTER], ADAPTER)
        validator_green, p_slug = dbt.apply(validator0, green[VALIDATOR], VALIDATOR)
        case("debt-edit-applies", p_red + p_green + p_slug, True)
        case("debt-edit-red-twice", dbt.apply(adapter_red, dbt.red_edits(), "x")[1], False)
        doubled = adapter0.replace(
            dbt.crlf(dbt.AC_130_10_LINE_OLD), dbt.crlf(dbt.AC_130_10_LINE_OLD) * 2
        )
        case("debt-edit-doubled-anchor", dbt.apply(doubled, dbt.red_edits(), "x")[1], False)
        lf = adapter0.replace(b"\r\n", b"\n")
        case("debt-edit-lf-file", dbt.apply(lf, dbt.red_edits(), "x")[1], False)

        put(root, ADAPTER, adapter0)
        put(root, VALIDATOR, validator0)
        put(root, "ui/tests/unit/app-icon.test.ts", "pin\n")
        pins = t / "pins.json"
        pins_data = {
            "files": {
                "ui/tests/unit/app-icon.test.ts": sha(root / "ui/tests/unit/app-icon.test.ts")
            },
            "ast": {ADAPTER: _sources(root, ADAPTER), VALIDATOR: _sources(root, VALIDATOR)},
        }
        pins.write_text(json.dumps(pins_data, indent=2), encoding="utf-8")
        case("pins-unchanged-row0", pins_unchanged(root, pins), True)
        case("named-edits-row0-refused", named_edits("red", root, pins), False)
        case("slug-edit-row0-refused", slug_edit(root, pins), False)
        put(root, ADAPTER, adapter_red)
        case("named-edits-red-ok", named_edits("red", root, pins), True)
        case("named-edits-red-as-green", named_edits("green", root, pins), False)
        case("pins-unchanged-after-red", pins_unchanged(root, pins), True)
        put(root, ADAPTER, adapter_green)
        put(root, VALIDATOR, validator_green)
        case("named-edits-green-ok", named_edits("green", root, pins), True)
        case("named-edits-green-as-red", named_edits("red", root, pins), False)
        case("slug-edit-ok", slug_edit(root, pins), True)
        case("pins-unchanged-after-green", pins_unchanged(root, pins), True)

        # the helper took AC-130.10's decorators (plan review round 1 F1)
        head = dbt.crlf(dbt.HELPER_RED + "\n\n\n" + dbt.AC_130_10_HEAD)
        lines = dbt.AC_130_10_HEAD.split("\n")
        stolen = dbt.crlf(lines[0] + "\n" + lines[1] + "\n" + dbt.HELPER_RED + "\n\n\n" + lines[2])
        put(root, ADAPTER, adapter_red.replace(head, stolen))
        case("named-edits-decorators-lost", named_edits("red", root, pins), False)
        other = adapter_red.replace(b"    assert ac_id\r\n", b"    assert ac_id or True\r\n", 1)
        put(root, ADAPTER, other)
        case("named-edits-other-130-10-test-changed", named_edits("red", root, pins), False)
        case("pins-unchanged-other-test-changed", pins_unchanged(root, pins), False)
        extra = adapter_red.replace(
            dbt.crlf(dbt.AC_130_10_LAST), dbt.crlf("        assert srgb\n" + dbt.AC_130_10_LAST)
        )
        put(root, ADAPTER, extra)
        case("named-edits-130-10-other-line", named_edits("red", root, pins), False)
        tests = dbt.crlf("\n\n" + "\n\n\n".join(dbt.TESTS.values()) + "\n")
        moved = adapter_red.replace(tests, b"\r\n") + dbt.crlf(
            "\n\n" + "\n\n\n".join(dbt.TESTS.values()) + "\n"
        )
        put(root, ADAPTER, moved)
        case("named-edits-tests-out-of-place", named_edits("red", root, pins), False)
        put(root, ADAPTER, adapter_red.replace(b"0xFF", b"0xFE", 1))
        case("named-edits-test-not-the-form", named_edits("red", root, pins), False)
        put(root, ADAPTER, adapter_red.replace(b"\r\n", b"\n", 1))
        case("named-edits-bare-lf", named_edits("red", root, pins), False)
        put(root, ADAPTER, adapter_red)
        put(root, VALIDATOR, validator_green.replace(b"return 0", b"return 1"))
        case("slug-edit-other-node-changed", slug_edit(root, pins), False)
        case("pins-unchanged-validator-changed", pins_unchanged(root, pins), False)
        put(root, VALIDATOR, validator_green.replace(b"parts[-2]", b"parts[-3]"))
        case("slug-edit-not-the-form", slug_edit(root, pins), False)
        put(root, VALIDATOR, validator_green.replace(b"\r\n", b"\n", 1))
        case("slug-edit-bare-lf", slug_edit(root, pins), False)
        put(root, VALIDATOR, validator_green)
        put(root, "ui/tests/unit/app-icon.test.ts", "pin changed\n")
        case("pins-unchanged-file-changed", pins_unchanged(root, pins), False)

        # red-reason
        def receipt(name: str, body: str) -> pathlib.Path:
            p = t / f"{name}.txt"
            p.write_text(body, encoding="utf-8")
            return p

        ids = ["AC-164.4 hidden", "AC-164.5 minimized"]
        good = [("AC-164.4 hidden: a double-click shows the window", TRAY_HOOK)]
        good.append(("AC-164.5 minimized: a double-click restores it", TRAY_HOOK))
        n = "tray hook"
        case("red-reason-ok", red_reason(receipt("rr-ok", _pw(good, 0)), ids, n), True)
        ansi = _pw(good, 0).replace("Error: expect", "\x1b[31mError: expect")
        case("red-reason-ansi", red_reason(receipt("rr-ansi", ansi), ids, n), True)
        one = _pw(good[:1], 1)
        case("red-reason-id-missing", red_reason(receipt("rr-missing", one), ids, n), False)
        bad = [good[0], (good[1][0], LAUNCH)]
        case("red-reason-launch", red_reason(receipt("rr-launch", _pw(bad, 0)), ids, n), False)
        bad = [good[0], (good[1][0], SEED)]
        case("red-reason-seed", red_reason(receipt("rr-seed", _pw(bad, 0)), ids, n), False)
        bad = [good[0], (good[1][0], NO_NEEDLE)]
        case(
            "red-reason-needle-in-frame",
            red_reason(receipt("rr-frame", _pw(bad, 0)), ids, n),
            False,
        )
        bare = [("AC-164.4 hidden: x", ["Error: tray hook", *TRAY_HOOK[1:]]), good[1]]
        case("red-reason-bare-message", red_reason(receipt("rr-bare", _pw(bare, 0)), ids, n), False)
        timeout = [*TRAY_HOOK[:2], "Test timeout of 30000ms exceeded.", *TRAY_HOOK[2:]]
        bad = [good[0], (good[1][0], timeout)]
        case("red-reason-test-timeout", red_reason(receipt("rr-to", _pw(bad, 0)), ids, n), False)
        prefix = [("AC-164.40 hidden x", TRAY_HOOK), good[1]]
        case(
            "red-reason-prefix-is-not-a-match",
            red_reason(receipt("rr-prefix", _pw(prefix, 0)), ["AC-164.4"], n),
            False,
        )

        # e2e-count
        def pw(name: str, body: list[str]) -> pathlib.Path:
            return receipt(name, "\n".join(body) + "\n")

        oks = [
            f"  ok {i:>2} [electron] {ARROW} {PW_FILE}:1:1 {ARROW} AC-164.{4 + i % 2} x (1.0s)"
            for i in range(1, 7)
        ]
        tsb = pw("tsb", ["Running 6 tests using 1 worker", *oks, "", "  6 passed (19.0s)"])
        plain = pw(
            "plain",
            [
                f"  ok 1 [electron] {ARROW} tests\\e2e\\startup-reveal.test.ts:1:1 {ARROW} AC-1",
                "  3 passed (20.0s)",
            ],
        )
        case("e2e-count-ok-below-10", e2e_count(tsb, 6, [plain]), True)
        case("e2e-count-wrong-n", e2e_count(tsb, 3, [plain]), False)
        flaky = pw("flaky", ["  ok 1 x ΓÇ║ AC-164.4 y (1.0s)", "  1 flaky", "  1 passed (1.0s)"])
        case("e2e-count-flaky", e2e_count(tsb, 6, [flaky]), False)
        rej = pw("rej", [*oks, "unhandled rejection: boom", "  6 passed (9.0s)"])
        case("e2e-count-unhandled", e2e_count(rej, 6, []), False)
        failed = pw("failed", [*oks, "  1 failed", "  6 passed (9.0s)"])
        case("e2e-count-failed", e2e_count(failed, 6, []), False)
        nopass = pw("nopass", ["  ok 1 tests\\e2e\\x.ts:1:1 ΓÇ║ AC-1 (1.0s)"])
        case("e2e-count-plain-no-pass", e2e_count(tsb, 6, [nopass]), False)

        # canon
        def crlf(lines: list[str]) -> bytes:
            return ("\r\n".join(lines) + "\r\n").encode("utf-8")

        menu = MENU_PREFIX + ", in order. | Local Canon |"
        note = [
            "",
            DELIVERED_HEAD,
            "> - TRAY_SHOW_SHARED: one show function; it calls restore() first when minimized.",
            "> - TRAY_E2E_HOOK; capture-tray.test.ts and tray-double-click.test.ts prove it.",
            "> - D-1365 to D-1368.",
        ]
        canon0 = ["| Surface | Owner | Rule |", TRAY_ROW_OLD, "", "### Tray double-click", menu]
        canon0 += ["", "## Named deferrals (not this phase)", ""]
        done = list(canon0)
        done[1] = TRAY_ROW_NEW
        done[5:5] = note
        put(copies, CANON, crlf(canon0))
        put(root, CANON, crlf(done))
        case("canon-ok", canon(root, copies), True)
        put(root, CANON, crlf([*canon0[:5], *note, *canon0[5:]]))
        case("canon-tray-row-not-edited", canon(root, copies), False)
        put(root, CANON, crlf([line.replace("D-1368", "D-1367") for line in done]))
        case("canon-token-missing", canon(root, copies), False)
        put(root, CANON, crlf([*done[:5], *note[:2], "plain line", *done[7:]]))
        case("canon-bullet-shape", canon(root, copies), False)
        put(root, CANON, crlf([*done, "extra"]))
        case("canon-extra-line-after", canon(root, copies), False)
        put(root, CANON, crlf([done[0] + " ", *done[1:]]))
        case("canon-other-line-changed", canon(root, copies), False)
        put(root, CANON, crlf(done).replace(b"\r\n", b"\n", 1))
        case("canon-bare-lf", canon(root, copies), False)
        put(root, CANON, crlf([*done[:5], *note, *done[5:]]))
        case("canon-note-twice", canon(root, copies), False)
        put(root, CANON, crlf([*canon0[:1], TRAY_ROW_NEW, *note, *canon0[2:]]))
        case("canon-note-in-wrong-place", canon(root, copies), False)

        # register
        def reg(issues: list[dict], other: str = "open") -> bytes:
            data = {
                "version": 1,
                "issues": [
                    {"id": "CAPTURE-JOURNAL-VOLATILE", "status": other, "severity": "low"},
                    *issues,
                ],
            }
            return yaml.safe_dump(data, sort_keys=False).replace("\n", "\r\n").encode("utf-8")

        def issue(key: str, resolved: bool, **extra: object) -> dict:
            base = {
                "id": key,
                "status": "open",
                "severity": "medium",
                "meu_links": ["MEU-164"],
                "verification": {"last_checked": "2026-11-22", "method": "m", "result": "r"},
            }
            if resolved:
                base.update(
                    status="resolved",
                    verification={"last_checked": "2026-11-22", "method": "tsb", "result": "ok"},
                    resolution_path="Fixed in Session 102 on 2026-11-22",
                )
            base.update(extra)
            return base

        opened = [issue(k, False) for k in ISSUES]
        closed = [issue(k, True) for k in ISSUES]
        grouping = (
            "| Session | Slug |\n"
            "| 102 | `tray-show-and-baseline-fixes` | MEU-164 | P3 | planned | `docs/x/` |\n"
        )
        executed = grouping.replace(GROUPING_OLD, GROUPING_NEW)
        put(copies, REGISTER, reg(opened))
        put(copies, GROUPING, grouping)
        put(root, REGISTER, reg(closed))
        put(root, GROUPING, executed)
        case("register-ok", register(root, copies), True)
        put(root, REGISTER, reg(closed, other="resolved"))
        case("register-other-issue-changed", register(root, copies), False)
        put(root, REGISTER, reg([*closed[:2], issue(ISSUES[2], True, severity="low")]))
        case("register-issue-other-field", register(root, copies), False)
        put(root, REGISTER, reg([*closed[:2], issue(ISSUES[2], True, meu_links=["MEU-1"])]))
        case("register-meu-links-changed", register(root, copies), False)
        put(root, REGISTER, reg([closed[0], opened[1], closed[2]]))
        case("register-one-not-resolved", register(root, copies), False)
        put(root, REGISTER, reg(closed[:2]))
        case("register-issue-removed", register(root, copies), False)
        put(root, REGISTER, reg(closed))
        put(root, GROUPING, grouping)
        case("register-grouping-still-planned", register(root, copies), False)
        put(root, GROUPING, grouping.replace(GROUPING_OLD, "| executed |"))
        case("register-grouping-other-text", register(root, copies), False)
        put(root, GROUPING, executed + "x\n")
        case("register-grouping-extra-line", register(root, copies), False)
        put(root, GROUPING, executed.replace("\n", "\r\n"))
        case("register-grouping-crlf", register(root, copies), False)

    print(f"row-check selftest: {len(failures)} wrong: {failures}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == "red-record" and len(rest) >= 3 and rest[0] == "--row":
            problems = red_record(rest[1], rest[2:], ROOT, RECEIPTS)
        elif cmd == "red-unchanged" and not rest:
            problems = red_unchanged(ROOT, RECEIPTS)
        elif cmd == "pins-unchanged" and not rest:
            problems = pins_unchanged(ROOT, PINS)
        elif cmd == "red-reason":
            ids: list[str] = []
            needle = ""
            paths: list[str] = []
            it = iter(rest)
            for arg in it:
                if arg == "--id":
                    ids.append(next(it, ""))
                elif arg == "--needle":
                    needle = next(it, "")
                else:
                    paths.append(arg)
            if not ids or "" in ids or not needle or len(paths) != 1:
                raise ValueError("red-reason RECEIPT --id ID [--id ID ...] --needle TEXT")
            problems = red_reason(pathlib.Path(paths[0]), ids, needle)
        elif cmd == "e2e-count" and len(rest) >= 2:
            plain: list[pathlib.Path] = []
            it = iter(rest[2:])
            for arg in it:
                if arg != "--plain":
                    raise ValueError("e2e-count RECEIPT N [--plain RECEIPT ...]")
                plain.append(pathlib.Path(next(it)))
            problems = e2e_count(pathlib.Path(rest[0]), int(rest[1]), plain)
        elif cmd == "named-edits" and len(rest) == 2 and rest[0] == "--stage":
            if rest[1] not in ("red", "green"):
                raise ValueError("named-edits --stage red|green")
            problems = named_edits(rest[1], ROOT, PINS)
        elif cmd == "slug-edit" and not rest:
            problems = slug_edit(ROOT, PINS)
        elif cmd == "canon" and not rest:
            problems = canon(ROOT, COPIES)
        elif cmd == "register" and not rest:
            problems = register(ROOT, COPIES)
        else:
            raise ValueError(f"unknown or malformed subcommand {cmd!r}")
    except (ValueError, StopIteration) as exc:
        print(f"usage: {exc}")
        return 2
    for p in problems:
        print("PROBLEM:", p)
    print(f"row-check {cmd}: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
