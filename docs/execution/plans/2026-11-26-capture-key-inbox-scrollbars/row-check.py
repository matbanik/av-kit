"""Session 103 row checks (task rows 1 to 11 and the gate; implementation-plan.md §Verification
Plan 1 step 9, §2, §3 and §Session gate).

Written in the shape of Session 104's (2026-11-26-ytdlp-challenge-and-cookie-test/row-check.py),
whose helpers (``Ctx``, red-record, red-unchanged, scope-paths, the Playwright report reader,
canon, the register and status readers and the selftest frame) it keeps. Every subcommand exits
0 when it finds no problem, 1 when it does, 2 on a usage error:

* ``red-record --row N FILE ...``: the hashes of a Red row's test files (``cki-red-hashes.json``)
  and their byte copies.
* ``guards --row N``: the tree as it must be after row N. The Red files recorded so far are
  unchanged (N >= 1); the §Test pins files keep their row-0 hashes; ``capture-page.test.ts`` and
  ``settings-page.test.ts`` equal row 0 before row 6 and differ from it in exactly the four named
  lines from row 6 on (D-1422); ``help-quick-start.test.ts`` and ``help-shots.shots.ts`` equal
  row 0 before row 7 and differ only inside the named statements from row 7 on;
  ``capture-inbox.test.ts``, ``capture-settings-draft.test.ts`` (row 1) and ``test-ids.ts``
  (row 9) gain lines only, where an ``import`` statement may come back with more names; a file a
  later row writes is still its row-0 bytes (or absent); scope-paths and ``eol-check.py`` pass;
  from row 11, the three MEUs are ``ready_for_review`` or ``approved`` and the three issues
  ``resolved``.
* ``e2e-titles LIST``: a Playwright ``--list`` receipt names each of the four new titles once.
* ``snapshot-paths --out FILE``: the scope paths under ``ui/`` and ``packages/`` that differ from
  ``HEAD``.
* ``remote-red --snapshot S --run RUN --out OUT``: row 1's run (§3); writes the base count.
* ``remote-ok --snapshot S --run RUN --base BASE --out OUT``: row 10's run (§3); writes the
  receipts folder.
* ``remote-fresh``: the gate's ``e2e-remote`` step (D-1430).
* ``scope-paths``, ``canon``, ``decision-sources``: as the plan says.
* ``--selftest``: each check's passing case passes and its failing case fails.
"""

from __future__ import annotations

import difflib
import hashlib
import importlib.util
import json
import os
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
SLUG = "2026-11-26-capture-key-inbox-scrollbars"
PLAN_REL = f"docs/execution/plans/{SLUG}"
RECEIPTS = pathlib.Path("C:/Temp/av-kit") / SLUG
RED_STORE = "cki-red-hashes.json"
RED_COPIES = "cki-red-copies"


def _load(name: str, file: str, folder: pathlib.Path = HERE):
    spec = importlib.util.spec_from_file_location(name, folder / file)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


eolc = _load("cki_eol_check", "eol-check.py")
SCOPE: dict[str, str] = eolc.SCOPE
GROUPING: str = eolc.GROUPING
HANDOFFS = (eolc.HANDOFF_165, eolc.HANDOFF_166, eolc.HANDOFF_167)

UNIT = "ui/tests/unit/"
CAPTURE = "ui/src/renderer/src/features/capture/"
HELP = "ui/src/renderer/src/components/help/"
SETTINGS = "ui/src/renderer/src/features/settings/"
CAPTURE_PAGE_TEST = UNIT + "capture-page.test.ts"
SETTINGS_PAGE_TEST = UNIT + "settings-page.test.ts"
HELP_QS_E2E = "ui/tests/e2e/help-quick-start.test.ts"
HELP_SHOTS = "ui/tests/help-shots/help-shots.shots.ts"
E2E_INBOX = "ui/tests/e2e/capture-inbox.test.ts"
E2E_DRAFT = "ui/tests/e2e/capture-settings-draft.test.ts"
TEST_IDS = "ui/tests/e2e/test-ids.ts"
OPENAPI = "openapi.committed.json"
REGISTER = ".agent/context/known-issues.yaml"
MEU_STATUS = ".agent/context/meu-status.yaml"
CAPTURE_PY = "packages/core/src/avkit_core/services/capture.py"
ERRORS_PY = "packages/api/src/avkit_api/errors.py"

#: §Test pins: byte-identical through the session.
PINS = (
    *(
        UNIT + n
        for n in (
            "capture-page.behavior.test.ts",
            "capture-action-row.test.ts",
            "help-quick-start.test.tsx",
            "capture-help-content.test.ts",
            "capture-tool-style.test.ts",
            "capture-copy-image.behavior.test.ts",
            "capture-redact.behavior.test.ts",
            "failure-reason-copy.test.ts",
            "help-card.test.ts",
            "capture-zoom.test.ts",
            "capture-fit-map.test.ts",
            "e2e-pointer.test.ts",
            "gui-actions-audit.test.ts",
        )
    ),
    "tests/unit/test_capture_service.py",
    "tests/e2e/test_api_captures.py",
    "tests/e2e/test_api_capture_crop.py",
    "tests/tooling/test_help_guide_ste.py",
    OPENAPI,
)
#: §Project files, "Read, never changed": named files, and every file under the prefixes.
READ_ONLY_FIXED = (
    CAPTURE + "capture-fit-map.ts",
    CAPTURE + "capture-zoom.ts",
    CAPTURE + "useCaptureCatalog.ts",
    "packages/api/src/avkit_api/routes/captures.py",
    OPENAPI,
    "tools/e2e_remote.py",
    "tools/help_guide_ste.py",
    "ui/tests/e2e/fixtures/capture-region-original.png",
)
READ_ONLY_PREFIXES = ("ui/src/main/", "mcp-server/", "tools/e2e_host/")
SECRET_NAMES = {".mcp.json", "mcp-token.txt", ".claude.json", ".env", "settings.local.json"}
HUB = ".agent/fleet/hub"

#: D-1422: the four expectations that take the token form at row 6, as whole lines.
NAMED: dict[str, tuple[tuple[str, str], ...]] = {
    CAPTURE_PAGE_TEST: (
        ("  'When F2 is in use',", "  'When {captureKey} is in use',"),
        ("  'Close to tray keeps F2',", "  'Close to tray keeps {captureKey}',"),
        (
            "    expect(page).toMatch(/Press F2 or Capture region/)",
            "    expect(page).toMatch(/Press \\{captureKey\\} or Capture region/)",
        ),
    ),
    SETTINGS_PAGE_TEST: (
        ("    expect(help).toContain('F2')", "    expect(help).toContain('{captureKey}')"),
    ),
}
NAMED_ROW = 6
#: Row 7's two test-side edits: the row-0 lines (1-based, inclusive) each may change, with the
#: text the first line of each span holds at row 0.
SPANS: dict[str, tuple[tuple[int, int, str], ...]] = {
    HELP_QS_E2E: ((17, 31, "import"), (135, 135, "HELP_QUICK_START_STEP")),
    HELP_SHOTS: (
        (24, 33, "import"),
        (59, 66, ""),
        (515, 515, "stepsHash: stepsHash(QUICK_START[feature]),"),
    ),
}
SPANS_ROW = 7
#: Files that gain lines only, from the row that first writes them.
ADDED_ONLY = {E2E_DRAFT: 1, E2E_INBOX: 1, TEST_IDS: 9}
#: The row that first writes each file; before it the file is its row-0 bytes or absent.
BY_ROW = {
    "tests/unit/test_capture_inbox_scope.py": 2,
    "tests/e2e/test_api_capture_inbox_scope.py": 2,
    CAPTURE_PY: 3,
    UNIT + "capture-inbox-scope.behavior.test.ts": 4,
    CAPTURE + "useCaptureSettings.ts": 5,
    CAPTURE + "CapturePage.tsx": 5,
    UNIT + "capture-key.test.ts": 6,
    UNIT + "capture-key.behavior.test.ts": 6,
    CAPTURE + "capture-key.ts": 7,
    CAPTURE + "capture-help-content.ts": 7,
    SETTINGS + "settings-help-content.ts": 7,
    HELP + "quick-start.json": 7,
    HELP + "quick-start.ts": 7,
    HELP + "HelpCard.tsx": 7,
    SETTINGS + "SettingsPage.tsx": 7,
    UNIT + "capture-scroll-bars.test.ts": 8,
    UNIT + "capture-scroll-bars.behavior.test.ts": 8,
    CAPTURE + "capture-scroll-bars.ts": 9,
    CAPTURE + "CaptureViewport.tsx": 9,
}
E2E_TITLES = (
    (
        "capture-settings-draft.test.ts",
        "AC-165.10 a saved capture key shows in the Capture texts with no restart",
    ),
    ("capture-settings-draft.test.ts", "AC-166.7 a saved inbox change lists only the new folder"),
    ("capture-inbox.test.ts", "AC-167.7 scroll bars show the view and a thumb drag moves it"),
    ("capture-inbox.test.ts", "AC-167.8 the scroll bar thumb is seen in both themes"),
)
MEUS = ("MEU-165", "MEU-166", "MEU-167")
ISSUES = (
    "CAPTURE-HOTKEY-TEXT-HARDCODED",
    "CAPTURE-INBOX-CHANGE-KEEPS-OLD-SHOTS",
    "CAPTURE-ZOOM-NO-SCROLLBARS",
)
PLAN_DECISIONS = tuple(f"D-{n}" for n in range(1420, 1433))
E2E_LINE = re.compile(r"^e2e-remote: (\S+) exit=(-?\d+) run=(\S+) receipts=(.+?)\s*$")
ANSI = re.compile(r"\x1b\[[0-9;]*m")
UNHANDLED = re.compile(r"unhandled rejection:", re.IGNORECASE)
OTHER_PLAN = re.compile(r"^docs/execution/plans/2026-11-(?:1[6-9]|2[0-6])-[^/]+/")
OTHER_ARTIFACT = re.compile(
    r"^(?:\.agent/context/handoffs/2026-11-2\d-|docs/proposals/2026-11-2\d-|"
    r"docs/execution/reflections/2026-11-2\d-|\.agent/context/grouping/2026-11-2\d-)"
)
RELEASE = re.compile(r"changelog|release[-_ ]?notes?|docs/releases/", re.IGNORECASE)
NOREPLY = (
    "-c",
    "user.name=MatBanik",
    "-c",
    "user.email=219344396+matbanik@users.noreply.github.com",
)


@dataclass
class Ctx:
    root: pathlib.Path = ROOT
    r: pathlib.Path = RECEIPTS
    plan: pathlib.Path = HERE

    @property
    def copies(self) -> pathlib.Path:
        return self.r / "baseline-copies"

    def pjson(self, name: str):
        return json.loads((self.plan / name).read_text(encoding="utf-8"))

    def base(self, name: str) -> bytes:
        return (self.copies / name).read_bytes()

    def now(self, name: str) -> bytes:
        return (self.root / name).read_bytes()

    def text(self, name: str) -> str:
        return self.now(name).decode("utf-8")

    def rtext(self, name: str) -> str:
        return (self.r / name).read_bytes().decode("utf-8", "replace").lstrip("\ufeff")


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "absent"


def rel(path: pathlib.Path, root: pathlib.Path) -> str:
    path = path if path.is_absolute() else root / path
    return path.resolve().relative_to(root.resolve()).as_posix()


def _lines(raw: bytes | str) -> list[str]:
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    return text.replace("\r\n", "\n").split("\n")


def _ops(a: list[str], b: list[str]):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()


def _read(path: pathlib.Path) -> str:
    return path.read_bytes().decode("utf-8", "replace").lstrip("\ufeff")


def _secret(path: str) -> bool:
    return path.startswith(HUB) or pathlib.PurePosixPath(path).name in SECRET_NAMES


# --- red-record, red-unchanged (Session 104's)
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


# --- guards
def pins(ctx: Ctx) -> list[str]:
    want = ctx.pjson("baseline-pins.json")["files"]
    problems = [f"pins: {p} is not pinned at row 0" for p in PINS if p not in want]
    for p, h in sorted(want.items()):
        if sha(ctx.root / p) != h:
            problems.append(f"pins: {p} changed since row 0")
    print(f"pins: {len(want)} file(s), {len(problems)} problem(s)")
    return problems


def _replace_lines(raw: bytes, pairs, path: str) -> tuple[bytes, list[str]]:
    """Row 0's bytes with each whole old line (found once) set to its new text, ending kept."""
    lines = raw.split(b"\n")
    problems: list[str] = []
    for old, new in pairs:
        hits = [i for i, x in enumerate(lines) if x.rstrip(b"\r") == old.encode("utf-8")]
        if len(hits) != 1:
            problems.append(f"named: {path} holds the line {old.strip()!r} {len(hits)} time(s)")
            continue
        cr = b"\r" if lines[hits[0]].endswith(b"\r") else b""
        lines[hits[0]] = new.encode("utf-8") + cr
    return b"\n".join(lines), problems


def named(ctx: Ctx, row: int) -> list[str]:
    problems: list[str] = []
    for path, pairs in NAMED.items():
        base, now = ctx.base(path), ctx.now(path)
        want, probs = _replace_lines(base, pairs, path)
        problems += probs
        if row < NAMED_ROW and now != base:
            problems.append(f"named: {path} changed before row {NAMED_ROW}")
        elif row >= NAMED_ROW and now != want:
            hunks = [op for op in _ops(_lines(want), _lines(now)) if op[0] != "equal"]
            problems.append(
                f"named: {path} is not row 0 with its named lines ({len(hunks)} hunk(s))"
            )
        print(
            f"named {path}: {'equal' if now == base else 'named lines' if now == want else 'other'}"
        )
    return problems


def spans(ctx: Ctx, row: int) -> list[str]:
    problems: list[str] = []
    for path, allowed in SPANS.items():
        base, now = ctx.base(path), ctx.now(path)
        a, b = _lines(base), _lines(now)
        for start, _end, anchor in allowed:
            if anchor and anchor not in a[start - 1]:
                problems.append(f"spans: {path}:{start} at row 0 does not hold {anchor!r}")
        if row < SPANS_ROW:
            if now != base:
                problems.append(f"spans: {path} changed before row {SPANS_ROW}")
            continue
        hunks = 0
        for tag, i1, i2, _j1, _j2 in _ops(a, b):
            if tag == "equal":
                continue
            hunks += 1
            if i1 == i2:
                ok = any(s - 1 <= i1 <= e for s, e, _ in allowed)
            else:
                ok = all(any(s <= i + 1 <= e for s, e, _ in allowed) for i in range(i1, i2))
            if not ok:
                problems.append(
                    f"spans: {path} changed row-0 line(s) {i1 + 1}-{i2} outside its spans"
                )
        print(f"spans {path}: {hunks} hunk(s)")
    return problems


IMPORT_START = re.compile(r"^import\b")
IMPORT_END = re.compile(r"""\bfrom\s+(['"])([^'"]+)\1|^import\s+(['"])([^'"]+)\3""")


def split_imports(lines: list[str]) -> tuple[dict[str, set[str]], list[str]]:
    """TypeScript ``import`` statements by module (their names), and the other lines."""
    imports: dict[str, set[str]] = {}
    rest: list[str] = []
    i = 0
    while i < len(lines):
        if not IMPORT_START.match(lines[i]):
            rest.append(lines[i])
            i += 1
            continue
        stmt = [lines[i]]
        while not IMPORT_END.search(stmt[-1]) and i + len(stmt) < len(lines):
            stmt.append(lines[i + len(stmt)])
        i += len(stmt)
        text = " ".join(stmt)
        m = IMPORT_END.search(text)
        module = (m[2] or m[4]) if m else text
        head = re.sub(r"^import\s+(type\s+)?", "", text.split(" from ")[0]).strip()
        names: set[str] = set()
        for part in re.split(r"[{},]", head):
            part = re.sub(r"^type\s+", "", part.strip())
            if part:
                names.add(part.split(" as ")[-1].strip())
        imports.setdefault(module, set()).update(names)
    return imports, rest


def _subsequence(small: list[str], big: list[str]) -> int:
    """The first index of ``small`` not found, in order, in ``big``; ``len(small)`` if all are."""
    j = 0
    for i, x in enumerate(small):
        while j < len(big) and big[j] != x:
            j += 1
        if j == len(big):
            return i
        j += 1
    return len(small)


def added_only(ctx: Ctx, row: int) -> list[str]:
    problems: list[str] = []
    for path, first in ADDED_ONLY.items():
        base, now = ctx.base(path), ctx.now(path)
        if row < first:
            if now != base:
                problems.append(f"added-only: {path} changed before row {first}")
            continue
        bi, brest = split_imports(_lines(base))
        ni, nrest = split_imports(_lines(now))
        at = _subsequence(brest, nrest)
        if at < len(brest):
            problems.append(f"added-only: {path} lost or changed the row-0 line {brest[at]!r}")
        for module, names in bi.items():
            if not names <= ni.get(module, set()):
                lost = sorted(names - ni.get(module, set()))
                problems.append(f"added-only: {path} import of {module} lost {lost}")
        print(f"added-only {path}: {len(nrest) - len(brest)} line(s) added")
    return problems


def by_row(ctx: Ctx, row: int) -> list[str]:
    problems: list[str] = []
    later = 0
    for path, first in BY_ROW.items():
        if first <= row:
            continue
        later += 1
        base = ctx.copies / path
        now = ctx.root / path
        if base.is_file():
            if not now.is_file() or now.read_bytes() != base.read_bytes():
                problems.append(f"by-row: {path} changed before its row {first}")
        elif now.exists():
            problems.append(f"by-row: {path} exists before its row {first}")
    print(f"by-row: {later} file(s) wait for a later row")
    return problems


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


def closed(ctx: Ctx) -> list[str]:
    meus, issues = _meus(ctx.now(MEU_STATUS)), _issues(ctx.now(REGISTER), REGISTER)
    problems: list[str] = []
    for m in MEUS:
        got = meus.get(m, {}).get("status")
        if got not in ("ready_for_review", "approved"):
            problems.append(f"closed: {m} is {got}")
    for i in ISSUES:
        got = issues.get(i, {}).get("status")
        if got != "resolved":
            problems.append(f"closed: {i} is {got}")
    print(f"closed: {len(problems)} problem(s)")
    return problems


def guards(
    ctx: Ctx,
    row: int,
    scope_fn: Callable[[Ctx], list[str]] | None = None,
    eol_fn: Callable[[Ctx], list[str]] | None = None,
) -> list[str]:
    problems: list[str] = []
    if row >= 1:
        problems += red_unchanged(ctx)
    problems += pins(ctx)
    problems += named(ctx, row)
    problems += spans(ctx, row)
    problems += added_only(ctx, row)
    problems += by_row(ctx, row)
    problems += (scope_fn or scope_paths)(ctx)
    problems += (eol_fn or _eol)(ctx)
    if row >= 11:
        problems += closed(ctx)
    return problems


def _eol(ctx: Ctx) -> list[str]:
    problems, notes = eolc.check(ctx.root, ctx.copies, SCOPE)
    print(f"eol-check: {len(SCOPE)} path(s), {len(notes)} note(s), {len(problems)} problem(s)")
    return [f"eol: {p}" for p in problems]


# --- scope-paths
def _git(root: pathlib.Path, *args: str, env: dict | None = None) -> bytes:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True, env=env).stdout


def _changed(root: pathlib.Path) -> list[str]:
    raw = _git(root, "diff", "--no-renames", "--name-only", "-z", "HEAD")
    raw += _git(root, "ls-files", "--others", "--exclude-standard", "-z")
    return sorted({x.decode("utf-8") for x in raw.split(b"\0") if x})


def ro_prefix_files(root: pathlib.Path) -> list[str]:
    """Every tracked or not-ignored file under the read-only prefixes, secrets dropped."""
    raw = _git(root, "ls-files", "-co", "--exclude-standard", "-z", "--", *READ_ONLY_PREFIXES)
    names = {x.decode("utf-8") for x in raw.split(b"\0") if x}
    return sorted(p for p in names if not _secret(p) and (root / p).is_file())


def _other_texts(root: pathlib.Path) -> str:
    texts = []
    for folder in sorted((root / "docs/execution/plans").glob("2026-11-2*")):
        if folder.name != SLUG and folder.is_dir():
            texts += [f.read_bytes().decode("utf-8", "replace") for f in folder.glob("*.md")]
    return "\n".join(texts)


def scope_paths(
    ctx: Ctx,
    changed: list[str] | None = None,
    tags: str | None = None,
    listed: list[str] | None = None,
) -> list[str]:
    scope = ctx.pjson("baseline-scope.json")
    dirty = ctx.pjson("baseline-dirty-hashes.json")
    changed = _changed(ctx.root) if changed is None else changed
    texts = _other_texts(ctx.root)
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
        if RELEASE.search(p):
            problems.append(f"scope-paths: {p} is a release note or changelog")
            continue
        if p in SCOPE or p.startswith(own):
            kept += 1
            continue
        if p.startswith(READ_ONLY_PREFIXES) or p in READ_ONLY_FIXED:
            continue  # the read-only checks below name it
        if p in dirty and sha(ctx.root / p) == dirty[p]:
            notes += 1
            continue
        if OTHER_PLAN.match(p) or OTHER_ARTIFACT.match(p) or p in texts:
            notes += 1
            print(f"scope-paths note: {p} is another session's")
            continue
        problems.append(f"scope-paths: {p} is outside §Files Modified")
    ro = [*READ_ONLY_FIXED, *(p for p in scope if p.startswith(READ_ONLY_PREFIXES))]
    for p in ro:
        want = scope.get(p)
        if want is None:
            problems.append(f"scope-paths: read-only {p} has no row-0 hash")
        elif sha(ctx.root / p) != want:
            problems.append(f"scope-paths: read-only {p} changed")
    listed = ro_prefix_files(ctx.root) if listed is None else listed
    for p in listed:
        if p not in scope:
            problems.append(f"scope-paths: {p} is new under a read-only folder")
    tags = _git(ctx.root, "tag").decode("utf-8") if tags is None else tags
    want_tags = (ctx.r / "baseline-tags.txt").read_bytes().decode("utf-8")
    if sorted(tags.split()) != sorted(want_tags.split()):
        problems.append("scope-paths: the tags differ from row 0's")
    print(
        f"scope-paths: {len(changed)} changed, {kept} in scope, {notes} note(s), "
        f"{len(ro)} read-only"
    )
    return problems


# --- e2e-titles, snapshot-paths, remote-red, remote-ok, remote-fresh
def e2e_titles(ctx: Ctx, listing: pathlib.Path) -> list[str]:
    lines = [ANSI.sub("", x).rstrip() for x in _lines(_read(listing))]
    problems: list[str] = []
    for file, title in E2E_TITLES:
        hits = [x for x in lines if x.endswith(title) and file in x]
        if len(hits) != 1:
            problems.append(f"e2e-titles: {title!r} is listed {len(hits)} time(s) in {file}")
        print(f"e2e-titles: {len(hits)} x {title}")
    return problems


def _git_dirty(root: pathlib.Path) -> Callable[[str], bool]:
    return lambda p: bool(_git(root, "status", "--porcelain", "--", p).strip())


def snapshot_paths(
    ctx: Ctx, out: pathlib.Path, dirty: Callable[[str], bool] | None = None
) -> list[str]:
    is_dirty = dirty or _git_dirty(ctx.root)
    paths = [p for p in SCOPE if p.startswith(("ui/", "packages/")) and is_dirty(p)]
    problems = [] if paths else ["snapshot-paths: no path differs from HEAD"]
    out.write_bytes(("".join(p + "\n" for p in paths)).encode("utf-8"))
    for p in paths:
        print(f"snapshot-paths: {p}")
    return problems


def _e2e_line(path: pathlib.Path) -> re.Match[str] | None:
    if not path.is_file():
        return None
    lines = [x for x in _lines(_read(path)) if x.startswith("e2e-remote:")]
    return E2E_LINE.match(lines[-1]) if lines else None


def _specs(node: dict, file: str = "") -> list[dict]:
    out: list[dict] = []
    for suite in node.get("suites", []) or []:
        out += _specs(suite, suite.get("file", file))
    for spec in node.get("specs", []) or []:
        for t in spec.get("tests", []) or []:
            msgs = []
            for res in t.get("results", []) or []:
                errs = [res.get("error") or {}, *(res.get("errors") or [])]
                msgs += [ANSI.sub("", e.get("message", "")) for e in errs if e.get("message")]
            out.append(
                {
                    "file": str(spec.get("file", file)).replace("\\", "/"),
                    "title": spec.get("title", ""),
                    "status": t.get("status"),
                    "messages": msgs,
                }
            )
    return out


def _run(run: pathlib.Path) -> tuple[re.Match[str] | None, dict, list[dict], pathlib.Path]:
    m = _e2e_line(run)
    if not m:
        return None, {}, [], pathlib.Path()
    folder = pathlib.Path(m[4])
    summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    report = json.loads((folder / "host" / "report.json").read_text(encoding="utf-8"))
    return m, summary, _specs(report), folder


def _hits(specs: list[dict], file: str, title: str) -> list[dict]:
    return [s for s in specs if s["title"] == title and s["file"].endswith(file)]


def _write_once(out: pathlib.Path, text: str, label: str) -> list[str]:
    if out.is_file():
        if out.read_bytes().decode("utf-8") != text:
            return [f"{label}: {out.name} already holds other data"]
        print(f"{label}: {out.name} already holds the same data")
        return []
    out.write_bytes((text).encode("utf-8"))
    return []


def remote_red(ctx: Ctx, snapshot: pathlib.Path, run: pathlib.Path, out: pathlib.Path) -> list[str]:
    m, summary, specs, _ = _run(run)
    if not m:
        return ["remote-red: no e2e-remote line"]
    snap = json.loads(snapshot.read_text(encoding="utf-8"))
    problems: list[str] = []
    if m[1] != "new-failures" or m[2] != "40":
        problems.append(f"remote-red: {m[1]} exit={m[2]}, want new-failures exit=40")
    if summary.get("result") != "new-failures" or summary.get("exit") != 40:
        problems.append(f"remote-red: summary {summary.get('result')} {summary.get('exit')}")
    if summary.get("commit") != snap.get("commit"):
        problems.append("remote-red: the run's commit is not the snapshot's")
    for key in ("skipped", "flaky"):
        if summary.get(key) != 0:
            problems.append(f"remote-red: {key} is {summary.get(key)}")
    if summary.get("overlap"):
        problems.append(f"remote-red: overlap is {summary.get('overlap')}")
    new = sorted(
        (pathlib.PurePath(str(n.get("file", ""))).name, str(n.get("title", "")))
        for n in summary.get("new", [])
    )
    if new != sorted(E2E_TITLES):
        problems.append(f"remote-red: new is {new}")
    for file, title in E2E_TITLES:
        hits = _hits(specs, file, title)
        msgs = [x for s in hits for x in s["messages"]]
        bad = [
            x for x in msgs if "expect(" not in x or "Test timeout of" in x or "launch" in x.lower()
        ]
        if not hits or any(s["status"] != "unexpected" for s in hits) or not msgs or bad:
            problems.append(f"remote-red: {title} did not fail by an expect assertion")
    tests = summary.get("tests")
    if not isinstance(tests, int) or tests < 4:
        problems.append(f"remote-red: tests is {tests}")
    if not problems:
        data = json.dumps({"base": tests - 4, "run": m[3]}, indent=2) + "\n"
        problems += _write_once(out, data, "remote-red")
    print(f"remote-red: run {m[3]}; tests {tests}; new {len(new)}; {len(problems)} problem(s)")
    return problems


def _run_logs(folder: pathlib.Path) -> list[str]:
    hits: list[str] = []
    for name in ("run.log", "run.err"):
        p = folder / "host" / name
        if p.is_file():
            hits += [f"{name}: {x[:100]}" for x in _lines(_read(p)) if UNHANDLED.search(x)]
    return hits


def remote_ok(
    ctx: Ctx, snapshot: pathlib.Path, run: pathlib.Path, base: pathlib.Path, out: pathlib.Path
) -> list[str]:
    m, summary, specs, folder = _run(run)
    if not m:
        return ["remote-ok: no e2e-remote line"]
    snap = json.loads(snapshot.read_text(encoding="utf-8"))
    want = json.loads(base.read_text(encoding="utf-8"))["base"] + 4
    problems: list[str] = []
    if m[1] != "ok" or m[2] != "0":
        problems.append(f"remote-ok: {m[1]} exit={m[2]}, want ok exit=0")
    if summary.get("result") != "ok" or summary.get("exit") != 0:
        problems.append(f"remote-ok: summary {summary.get('result')} {summary.get('exit')}")
    for key in ("unexpected", "flaky", "skipped"):
        if summary.get(key) != 0:
            problems.append(f"remote-ok: {key} is {summary.get(key)}")
    for key in ("new", "overlap"):
        if summary.get(key):
            problems.append(f"remote-ok: {key} is {summary.get(key)}")
    if summary.get("tests") != want:
        problems.append(f"remote-ok: tests is {summary.get('tests')}, want {want}")
    if summary.get("commit") != snap.get("commit"):
        problems.append("remote-ok: the run's commit is not the snapshot's")
    for file, title in E2E_TITLES:
        hits = _hits(specs, file, title)
        if not hits or any(s["status"] != "expected" for s in hits):
            problems.append(f"remote-ok: {title} did not pass")
    problems += [f"remote-ok: {x}" for x in _run_logs(folder)]
    if not problems:
        out.write_bytes((folder.as_posix() + "\n").encode("utf-8"))
    print(f"remote-ok: run {m[3]}; tests {summary.get('tests')}; {len(problems)} problem(s)")
    return problems


def _work_tree(root: pathlib.Path) -> str:
    """The tree of HEAD plus the working tree under ui/ and packages/ (untracked included)."""
    with tempfile.TemporaryDirectory() as td:
        env = {**os.environ, "GIT_INDEX_FILE": str(pathlib.Path(td) / "index")}
        _git(root, "read-tree", "HEAD", env=env)
        _git(root, "add", "-A", "--", "ui", "packages", env=env)
        return _git(root, "write-tree", env=env).decode("ascii").strip()


def _subtree(root: pathlib.Path, rev: str, sub: str) -> str:
    return _git(root, "rev-parse", f"{rev}:{sub}").decode("ascii").strip()


def _next_name(r: pathlib.Path, stem: str, ext: str) -> pathlib.Path:
    p, n = r / f"{stem}{ext}", 2
    while p.exists():
        p, n = r / f"{stem}-r{n}{ext}", n + 1
    return p


def _fresh_run(ctx: Ctx, changed: list[str]) -> list[str]:
    """A fresh snapshot of this session's paths, its check, its run and row 10's check."""
    snap = _next_name(ctx.r, "cki-D6-snapshot", ".json")
    tag = snap.stem.replace("cki-D6-snapshot", "")
    paths_file = ctx.r / f"cki-D6-snapshot{tag}-paths.txt"
    problems = snapshot_paths(ctx, paths_file)
    if problems:
        return problems
    paths = [x for x in _lines(paths_file.read_text(encoding="utf-8")) if x]
    py = [sys.executable]
    steps = [
        ("snapshot", [*py, str(HERE / "snapshot-commit.py"), "--out", str(snap), *paths]),
        ("verify", [*py, str(HERE / "snapshot-commit.py"), "--verify", str(snap)]),
        (
            "check",
            [*py, "tools/e2e_remote.py", "check", "--out", str(ctx.r / f"cki-D6-check{tag}.json")],
        ),
    ]
    for label, argv in steps:
        res = subprocess.run(argv, cwd=ctx.root, capture_output=True)
        receipt = ctx.r / f"cki-D6-{label}{tag}.txt"
        receipt.write_bytes(res.stdout + res.stderr)
        print(f"remote-fresh {label}: exit {res.returncode} ({receipt.name})")
        if res.returncode != 0:
            return [f"remote-fresh: {label} exit {res.returncode}; see {receipt.name}"]
    commit = json.loads(snap.read_text(encoding="utf-8"))["commit"]
    run = ctx.r / f"cki-D6-run{tag}.txt"
    res = subprocess.run(
        [*py, "tools/e2e_remote.py", "run", commit], cwd=ctx.root, capture_output=True
    )
    run.write_bytes(res.stdout + res.stderr)
    m = _e2e_line(run)
    print(m[0] if m else f"remote-fresh: run exit {res.returncode}, no e2e-remote line")
    out = ctx.r / f"cki-D6-run{tag}-dir.txt"
    return remote_ok(ctx, snap, run, ctx.r / "cki-e2e-base.json", out)


def remote_fresh(
    ctx: Ctx,
    ok_fn: Callable[..., list[str]] | None = None,
    fresh_fn: Callable[[Ctx, list[str]], list[str]] | None = None,
) -> list[str]:
    snap10 = ctx.r / "cki-snapshot-10.json"
    commit = json.loads(snap10.read_text(encoding="utf-8"))["commit"]
    tree = _work_tree(ctx.root)
    same = all(
        _subtree(ctx.root, tree, s) == _subtree(ctx.root, commit, s) for s in ("ui", "packages")
    )
    if same:
        print(f"remote-fresh: ui/ and packages/ equal row 10's snapshot {commit[:12]}; reuse")
        run = ctx.r / "cki-run-10.txt"
        problems = (ok_fn or remote_ok)(
            ctx, snap10, run, ctx.r / "cki-e2e-base.json", ctx.r / "cki-D6-run-dir.txt"
        )
        m = _e2e_line(run)
        print(m[0] if m else "remote-fresh: row 10's run has no e2e-remote line")
        return problems
    diff = _git(ctx.root, "diff-tree", "-r", "--name-only", commit, tree, "--", "ui", "packages")
    changed = [x for x in diff.decode("utf-8").split("\n") if x]
    for p in changed:
        print(f"remote-fresh: changed since row 10: {p}")
    return (fresh_fn or _fresh_run)(ctx, changed)


# --- canon, decision-sources
def canon(ctx: Ctx, edits: dict | None = None) -> list[str]:
    ced = _load("cki_canon_edit", "canon-edit.py")
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
            print(f"canon note: {path} changed between row 0 and row 11 (another session)")
        print(f"canon {path}: {len(pairs)} edit(s)")
    return problems


def decision_sources(ctx: Ctx, fn: Callable[..., dict] | None = None) -> list[str]:
    paths = [ctx.plan / "implementation-plan.md", *(ctx.root / h for h in HANDOFFS)]
    paths += [ctx.root / GROUPING, ctx.root / REGISTER]
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        return [f"decision-sources: missing {missing}"]
    if fn is None:
        vca = _load("cki_vca", "validate_closeout_artifacts.py", ctx.root / "tools")
        fn = vca.decision_sources
    try:
        found = fn([str(p) for p in paths], list(ISSUES))
    except Exception as exc:  # noqa: BLE001 - a refusal is the finding
        return [f"decision-sources: {type(exc).__name__}: {exc}"]
    problems = [f"decision-sources: {d} is not found" for d in PLAN_DECISIONS if d not in found]
    stages: dict[str, int] = {}
    for stage, _ in found.values():
        stages[stage] = stages.get(stage, 0) + 1
    print(f"decision-sources: {len(found)} id(s) {dict(sorted(stages.items()))}")
    return problems


# --- selftest
def _put(base: pathlib.Path, files: dict[str, bytes | str]) -> None:
    for name, data in files.items():
        p = base / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)


def _ctx(tmp: pathlib.Path, tag: str) -> Ctx:
    ctx = Ctx(tmp / tag / "root", tmp / tag / "r", tmp / tag / "plan")
    for p in (ctx.root, ctx.r, ctx.plan, ctx.copies):
        p.mkdir(parents=True, exist_ok=True)
    return ctx


def _both(ctx: Ctx, files: dict[str, bytes | str]) -> None:
    _put(ctx.root, files)
    _put(ctx.copies, files)


def _dump(path: pathlib.Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data)).encode("utf-8"))


def _guard_tree(ctx: Ctx) -> None:
    """Row-0 copies and a tree equal to them, for every file the guards read."""
    named_files = {
        CAPTURE_PAGE_TEST: "a\r\n  'When F2 is in use',\r\n  'Close to tray keeps F2',\r\n"
        "    expect(page).toMatch(/Press F2 or Capture region/)\r\nz\r\n",
        SETTINGS_PAGE_TEST: "a\r\n    expect(help).toContain('F2')\r\nz\r\n",
    }
    qs = [f"l{i}" for i in range(1, 140)]
    qs[16] = "import { a } from './a'"
    qs[134] = "    await expect(card.getByTestId(HELP_QUICK_START_STEP)).toHaveText(x)"
    shots = [f"s{i}" for i in range(1, 520)]
    shots[23] = "import { b } from './b'"
    shots[514] = "        stepsHash: stepsHash(QUICK_START[feature]),"
    e2e = (
        "import { test } from '@playwright/test'\nimport { a } from './a'\n\ntest('x', () => {})\n"
    )
    _both(
        ctx,
        {
            **named_files,
            HELP_QS_E2E: "\n".join(qs) + "\n",
            HELP_SHOTS: "\n".join(shots) + "\n",
            E2E_DRAFT: e2e,
            E2E_INBOX: e2e,
            TEST_IDS: "export const A = 'a'\r\n",
            CAPTURE_PY: "x\r\n",
            **{p: "p\n" for p in PINS},
        },
    )
    _dump(ctx.plan / "baseline-pins.json", {"files": {p: sha(ctx.root / p) for p in PINS}})


def _report(
    tmp: pathlib.Path, line: str, summary: dict, status: str, msg: str, log: str = ""
) -> pathlib.Path:
    folder = tmp / "rc"
    specs = {}
    for file, title in E2E_TITLES:
        result = {"error": {"message": msg}} if msg else {}
        spec = {"title": title, "file": file, "tests": [{"status": status, "results": [result]}]}
        specs.setdefault(file, []).append(spec)
    report = {"suites": [{"file": f, "specs": s} for f, s in specs.items()]}
    _dump(folder / "summary.json", summary)
    _dump(folder / "host" / "report.json", report)
    _put(folder / "host", {"run.log": log, "run.err": ""})
    run = tmp / "run.txt"
    run.write_text(f"noise\ne2e-remote: {line} run=R1 receipts={folder.as_posix()}\n", "utf-8")
    return run


def selftest() -> int:
    results: list[tuple[str, bool]] = []

    def case(name: str, fn: Callable[[], list[str]], want_pass: bool) -> None:
        try:
            problems = fn()
        except Exception as exc:  # noqa: BLE001 - a crash is a failing case
            problems = [f"crash: {type(exc).__name__}: {exc}"]
        ok = (not problems) == want_pass
        results.append((name, ok))
        print(f"selftest {'ok ' if ok else 'BAD'} {name}: {problems[:2]}")

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)

        # red-record, red-unchanged
        c = _ctx(tmp, "red")
        _put(c.root, {"t/a.test.ts": "a\n"})
        case("red-record pass", lambda: red_record(c, "1", ["t/a.test.ts"]), True)
        case("red-record same again", lambda: red_record(c, "1", ["t/a.test.ts"]), True)
        case("red-unchanged pass", lambda: red_unchanged(c), True)
        _put(c.root, {"t/a.test.ts": "b\n"})
        case("red-record other hashes", lambda: red_record(c, "1", ["t/a.test.ts"]), False)
        case("red-unchanged fail", lambda: red_unchanged(c), False)

        # pins
        c = _ctx(tmp, "pins")
        _guard_tree(c)
        case("pins pass", lambda: pins(c), True)
        _put(c.root, {PINS[0]: "q\n"})
        case("pins fail", lambda: pins(c), False)

        # named
        c = _ctx(tmp, "named")
        _guard_tree(c)
        case("named row 5 equal", lambda: named(c, 5), True)
        for path, pairs in NAMED.items():
            _put(c.root, {path: _replace_lines(c.base(path), pairs, path)[0]})
        case("named row 6 named lines", lambda: named(c, 6), True)
        case("named row 5 changed", lambda: named(c, 5), False)
        _put(c.root, {SETTINGS_PAGE_TEST: c.now(SETTINGS_PAGE_TEST) + b"extra\r\n"})
        case("named row 6 another line", lambda: named(c, 6), False)
        c2 = _ctx(tmp, "named-lf")
        _guard_tree(c2)
        raw = c2.base(CAPTURE_PAGE_TEST).replace(b"F2 is in use',\r", b"F2 is in use',")
        _put(c2.copies, {CAPTURE_PAGE_TEST: raw})
        mixed = raw.replace(b"When F2 is", b"When {captureKey} is")
        mixed = mixed.replace(b"keeps F2',\r", b"keeps {captureKey}',\r")
        mixed = mixed.replace(b"/Press F2 or", b"/Press \\{captureKey\\} or")
        _put(c2.root, {CAPTURE_PAGE_TEST: mixed})
        for path, pairs in NAMED.items():
            if path != CAPTURE_PAGE_TEST:
                _put(c2.root, {path: _replace_lines(c2.base(path), pairs, path)[0]})
        case("named keeps each line's ending", lambda: named(c2, 6), True)
        _put(c2.root, {CAPTURE_PAGE_TEST: mixed.replace(b"is in use',", b"is in use',\r")})
        case("named line ending changed", lambda: named(c2, 6), False)
        c3 = _ctx(tmp, "named-twice")
        _guard_tree(c3)
        _put(c3.copies, {SETTINGS_PAGE_TEST: "    expect(help).toContain('F2')\r\n" * 2})
        case("named doubled line", lambda: named(c3, 6), False)

        # spans
        c = _ctx(tmp, "spans")
        _guard_tree(c)
        case("spans row 6 equal", lambda: spans(c, 6), True)
        qs = _lines(c.base(HELP_QS_E2E))
        qs[134] = "    await expect(x).toHaveText(steps)"
        qs.insert(31, "import { captureKeyText } from '../../src/capture-key'")
        _put(c.root, {HELP_QS_E2E: "\n".join(qs)})
        case("spans row 7 inside", lambda: spans(c, 7), True)
        case("spans row 6 changed", lambda: spans(c, 6), False)
        qs[60] = "changed"
        _put(c.root, {HELP_QS_E2E: "\n".join(qs)})
        case("spans row 7 outside", lambda: spans(c, 7), False)
        qs[60] = "l61"
        qs.insert(100, "inserted")
        _put(c.root, {HELP_QS_E2E: "\n".join(qs)})
        case("spans row 7 insert outside", lambda: spans(c, 7), False)
        c2 = _ctx(tmp, "spans-anchor")
        _guard_tree(c2)
        _put(c2.copies, {HELP_SHOTS: c2.base(HELP_SHOTS).replace(b"stepsHash: ", b"other: ")})
        case("spans anchor moved", lambda: spans(c2, 6), False)

        # added-only
        c = _ctx(tmp, "added")
        _guard_tree(c)
        case("added-only row 0 equal", lambda: added_only(c, 0), True)
        grown = (
            "import { test } from '@playwright/test'\nimport {\n  a,\n  b,\n} from './a'\n"
            "import { c } from './c'\n\ntest('x', () => {})\n\ntest('AC-167.7 y', () => {})\n"
        )
        _put(c.root, {E2E_INBOX: grown, E2E_DRAFT: grown})
        case("added-only row 1 added and reflowed", lambda: added_only(c, 1), True)
        case("added-only row 0 changed", lambda: added_only(c, 0), False)
        _put(c.root, {E2E_INBOX: grown.replace("test('x', () => {})", "test('x', () => 1)")})
        case("added-only changed line", lambda: added_only(c, 1), False)
        _put(c.root, {E2E_INBOX: grown.replace("  a,\n", "")})
        case("added-only lost import name", lambda: added_only(c, 1), False)
        _put(c.root, {E2E_INBOX: grown})
        _put(c.root, {TEST_IDS: "export const A = 'a'\r\nexport const B = 'b'\r\n"})
        case("added-only test-ids before row 9", lambda: added_only(c, 8), False)
        case("added-only test-ids row 9", lambda: added_only(c, 9), True)

        # by-row
        c = _ctx(tmp, "byrow")
        _guard_tree(c)
        case("by-row row 2", lambda: by_row(c, 2), True)
        _put(c.root, {CAPTURE_PY: "y\r\n"})
        case("by-row capture.py before row 3", lambda: by_row(c, 2), False)
        case("by-row capture.py at row 3", lambda: by_row(c, 3), True)
        _put(c.root, {UNIT + "capture-key.test.ts": "k\n"})
        case("by-row new file before its row", lambda: by_row(c, 5), False)
        case("by-row new file at its row", lambda: by_row(c, 6), True)

        # closed
        c = _ctx(tmp, "closed")
        meus = {"meus": [{"row_key": m, "id": m, "status": "ready_for_review"} for m in MEUS]}
        issues = {"issues": [{"id": i, "status": "resolved"} for i in ISSUES]}
        _put(c.root, {MEU_STATUS: yaml.safe_dump(meus), REGISTER: yaml.safe_dump(issues)})
        case("closed pass", lambda: closed(c), True)
        issues["issues"][1]["status"] = "open"
        _put(c.root, {REGISTER: yaml.safe_dump(issues)})
        case("closed fail", lambda: closed(c), False)

        # guards (scope and eol injected)
        c = _ctx(tmp, "guards")
        _guard_tree(c)
        _put(c.root, {"t/r.ts": "r\n"})
        red_record(c, "1", ["t/r.ts"])
        case("guards row 1", lambda: guards(c, 1, lambda _: [], lambda _: []), True)
        case("guards scope fails", lambda: guards(c, 1, lambda _: ["x"], lambda _: []), False)
        case("guards eol fails", lambda: guards(c, 1, lambda _: [], lambda _: ["x"]), False)
        _put(c.root, {"t/r.ts": "changed\n"})
        case("guards red file changed", lambda: guards(c, 1, lambda _: [], lambda _: []), False)

        # scope-paths
        c = _ctx(tmp, "scope")
        _put(
            c.root, {READ_ONLY_PREFIXES[0] + "ipc.ts": "i\n", **{p: "r\n" for p in READ_ONLY_FIXED}}
        )
        ro = {p: sha(c.root / p) for p in (*READ_ONLY_FIXED, READ_ONLY_PREFIXES[0] + "ipc.ts")}
        _dump(c.plan / "baseline-scope.json", ro)
        _dump(c.plan / "baseline-dirty-hashes.json", {})
        _put(c.r, {"baseline-tags.txt": "v1\n"})
        ok_changed = [
            CAPTURE_PY,
            f"{PLAN_REL}/x.py",
            "docs/execution/plans/2026-11-26-app-auto-update/a",
        ]
        listed = [READ_ONLY_PREFIXES[0] + "ipc.ts"]
        case("scope-paths pass", lambda: scope_paths(c, ok_changed, "v1", listed), True)
        case("scope-paths outside", lambda: scope_paths(c, ["README.md"], "v1", listed), False)
        case(
            "scope-paths release",
            lambda: scope_paths(c, ["docs/releases/x.md"], "v1", listed),
            False,
        )
        case("scope-paths tags", lambda: scope_paths(c, [], "v1 v2", listed), False)
        new_ro = [*listed, "mcp-server/src/new.ts"]
        case("scope-paths new read-only file", lambda: scope_paths(c, [], "v1", new_ro), False)
        _put(c.root, {READ_ONLY_PREFIXES[0] + "ipc.ts": "changed\n"})
        case("scope-paths read-only changed", lambda: scope_paths(c, [], "v1", listed), False)
        case(
            "secret names",
            lambda: [] if _secret(".agent/fleet/hub/a") and _secret("x/.env") else ["x"],
            True,
        )

        # e2e-titles
        c = _ctx(tmp, "titles")
        listing = "".join(f"  \x1b[2m›\x1b[22m {f}:9:3 › {t}\n" for f, t in E2E_TITLES)
        _put(c.r, {"list.txt": "Listing tests:\n" + listing + "Total: 4 tests\n"})
        case("e2e-titles pass", lambda: e2e_titles(c, c.r / "list.txt"), True)
        _put(c.r, {"list2.txt": listing + listing})
        case("e2e-titles twice", lambda: e2e_titles(c, c.r / "list2.txt"), False)
        _put(c.r, {"list3.txt": listing.replace("AC-166.7 a saved", "AC-166.7 a")})
        case("e2e-titles missing", lambda: e2e_titles(c, c.r / "list3.txt"), False)

        # snapshot-paths
        c = _ctx(tmp, "snap")
        hit = {CAPTURE_PY, E2E_INBOX}
        case(
            "snapshot-paths pass", lambda: snapshot_paths(c, c.r / "p.txt", hit.__contains__), True
        )
        case(
            "snapshot-paths wrote only ui/ and packages/",
            lambda: [] if c.rtext("p.txt").split() == [p for p in SCOPE if p in hit] else ["x"],
            True,
        )
        case(
            "snapshot-paths none", lambda: snapshot_paths(c, c.r / "q.txt", lambda _: False), False
        )

        # remote-red
        c = _ctx(tmp, "red-run")
        _dump(c.r / "snap.json", {"commit": "abc"})
        new = [
            {"file": f, "ac": t.split()[0], "title": t, "status": "unexpected"}
            for f, t in E2E_TITLES
        ]
        red_sum = {
            "tests": 300, "unexpected": 4, "flaky": 0, "skipped": 0, "new": new, "overlap": [],
            "result": "new-failures", "exit": 40, "commit": "abc",
        }  # fmt: skip
        msg = "Error: expect(locator).toBeVisible() failed"
        run = _report(c.r, "new-failures exit=40", red_sum, "unexpected", msg)
        out = c.r / "base.json"
        case("remote-red pass", lambda: remote_red(c, c.r / "snap.json", run, out), True)
        case(
            "remote-red wrote the base",
            lambda: (
                [] if json.loads(out.read_text("utf-8")) == {"base": 296, "run": "R1"} else ["x"]
            ),
            True,
        )
        case(
            "remote-red again, same base", lambda: remote_red(c, c.r / "snap.json", run, out), True
        )
        _dump(out, {"base": 1, "run": "R0"})
        case(
            "remote-red other base on file",
            lambda: remote_red(c, c.r / "snap.json", run, out),
            False,
        )
        out.unlink()
        run = _report(c.r, "new-failures exit=40", red_sum, "unexpected", "Test timeout of 30000ms")
        case("remote-red timeout", lambda: remote_red(c, c.r / "snap.json", run, out), False)
        run = _report(c.r, "new-failures exit=40", {**red_sum, "new": new[:3]}, "unexpected", msg)
        case("remote-red three new", lambda: remote_red(c, c.r / "snap.json", run, out), False)
        run = _report(c.r, "new-failures exit=40", {**red_sum, "flaky": 1}, "unexpected", msg)
        case("remote-red flaky", lambda: remote_red(c, c.r / "snap.json", run, out), False)
        run = _report(c.r, "new-failures exit=40", {**red_sum, "commit": "def"}, "unexpected", msg)
        case("remote-red other commit", lambda: remote_red(c, c.r / "snap.json", run, out), False)
        run = _report(c.r, "ok exit=0", red_sum, "unexpected", msg)
        case("remote-red ok line", lambda: remote_red(c, c.r / "snap.json", run, out), False)

        # remote-ok
        c = _ctx(tmp, "ok-run")
        _dump(c.r / "snap.json", {"commit": "abc"})
        _dump(c.r / "base.json", {"base": 296, "run": "R0"})
        ok_sum = {
            "tests": 300, "unexpected": 0, "flaky": 0, "skipped": 0, "new": [], "overlap": [],
            "result": "ok", "exit": 0, "commit": "abc",
        }  # fmt: skip
        out = c.r / "dir.txt"

        def ok_case(line: str, summary: dict, status: str = "expected", log: str = ""):
            run = _report(c.r, line, summary, status, "", log)
            return lambda: remote_ok(c, c.r / "snap.json", run, c.r / "base.json", out)

        case("remote-ok pass", ok_case("ok exit=0", ok_sum), True)
        case("remote-ok tests count", ok_case("ok exit=0", {**ok_sum, "tests": 299}), False)
        case("remote-ok a test failed", ok_case("ok exit=0", ok_sum, "unexpected"), False)
        case("remote-ok skipped", ok_case("ok exit=0", {**ok_sum, "skipped": 1}), False)
        case("remote-ok exit 40", ok_case("new-failures exit=40", ok_sum), False)
        log = "x\nUnhandled Rejection: boom\n"
        case("remote-ok unhandled rejection", ok_case("ok exit=0", ok_sum, log=log), False)

        # remote-fresh
        c = _ctx(tmp, "fresh")
        for sub in ("ui", "packages"):
            _put(c.root, {f"{sub}/a.txt": "a\n"})
        git = ["git", "-c", "core.autocrlf=false", *NOREPLY]
        subprocess.run(["git", "init", "-q", str(c.root)], check=True)
        subprocess.run([*git, "add", "-A"], cwd=c.root, check=True)
        subprocess.run([*git, "commit", "-q", "-m", "x"], cwd=c.root, check=True)
        head = _git(c.root, "rev-parse", "HEAD").decode("ascii").strip()
        _dump(c.r / "cki-snapshot-10.json", {"commit": head})
        calls: list[str] = []

        def ok_fn(*_a) -> list[str]:
            calls.append("ok")
            return []

        def fresh_fn(_c: Ctx, changed: list[str]) -> list[str]:
            calls.append("fresh:" + ",".join(changed))
            return [] if changed == ["ui/a.txt"] else ["wrong"]

        case("remote-fresh reuse", lambda: remote_fresh(c, ok_fn, fresh_fn), True)
        case("remote-fresh reused, no fresh run", lambda: [] if calls == ["ok"] else calls, True)
        _put(c.root, {"ui/a.txt": "b\n"})
        case("remote-fresh changed runs fresh", lambda: remote_fresh(c, ok_fn, fresh_fn), True)
        _put(c.root, {"packages/new.txt": "n\n"})
        case("remote-fresh fresh fails", lambda: remote_fresh(c, ok_fn, fresh_fn), False)

        # canon
        c = _ctx(tmp, "canon")
        _put(c.r / "canon-before", {"d.md": "a\r\nold\r\n"})
        _put(c.root, {"d.md": "a\r\nnew\r\nmore\r\n"})
        edits = {"d.md": [("old\n", "new\nmore\n")]}
        case("canon pass", lambda: canon(c, edits), True)
        _put(c.root, {"d.md": "a\r\nnew\r\n"})
        case("canon fail", lambda: canon(c, edits), False)

        # decision-sources
        c = _ctx(tmp, "ds")
        _put(c.plan, {"implementation-plan.md": "x\n"})
        _put(c.root, {h: "x\n" for h in (*HANDOFFS, GROUPING, REGISTER)})
        found = {d: ("planning", "plan") for d in PLAN_DECISIONS}
        case("decision-sources pass", lambda: decision_sources(c, lambda *_: found), True)
        short = dict(list(found.items())[1:])
        case("decision-sources missing id", lambda: decision_sources(c, lambda *_: short), False)

        def refuse(*_a):
            raise RuntimeError("refused")

        case("decision-sources refused", lambda: decision_sources(c, refuse), False)
        (c.root / HANDOFFS[2]).unlink()
        case("decision-sources no handoff", lambda: decision_sources(c, lambda *_: found), False)

        # imports
        imps, rest = split_imports(["import type { A } from 'a'", "import * as n from 'b'", "x"])
        case(
            "split-imports",
            lambda: (
                []
                if imps == {"a": {"A"}, "b": {"* as n".split(" as ")[-1]}} and rest == ["x"]
                else [str(imps)]
            ),
            True,
        )

    bad = [n for n, ok in results if not ok]
    print(f"row-check selftest: {len(results)} case(s), {len(bad)} wrong {bad}")
    return 1 if bad else 0


def _opt(rest: list[str], flag: str) -> str:
    if flag not in rest or rest.index(flag) + 1 >= len(rest):
        raise ValueError(f"{flag} VALUE is required")
    return rest[rest.index(flag) + 1]


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    ctx = Ctx()
    simple: dict[str, Callable[[Ctx], list[str]]] = {
        "scope-paths": scope_paths,
        "remote-fresh": remote_fresh,
        "canon": canon,
        "decision-sources": decision_sources,
    }
    path = lambda flag: pathlib.Path(_opt(rest, flag))  # noqa: E731
    try:
        if cmd in simple and not rest:
            problems = simple[cmd](ctx)
        elif cmd == "red-record" and len(rest) >= 3 and rest[0] == "--row":
            problems = red_record(ctx, rest[1], rest[2:])
        elif cmd == "guards" and len(rest) == 2 and rest[0] == "--row" and rest[1].isdigit():
            problems = guards(ctx, int(rest[1]))
        elif cmd == "e2e-titles" and len(rest) == 1:
            problems = e2e_titles(ctx, pathlib.Path(rest[0]))
        elif cmd == "snapshot-paths" and len(rest) == 2:
            problems = snapshot_paths(ctx, path("--out"))
        elif cmd == "remote-red" and len(rest) == 6:
            problems = remote_red(ctx, path("--snapshot"), path("--run"), path("--out"))
        elif cmd == "remote-ok" and len(rest) == 8:
            problems = remote_ok(
                ctx, path("--snapshot"), path("--run"), path("--base"), path("--out")
            )
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
