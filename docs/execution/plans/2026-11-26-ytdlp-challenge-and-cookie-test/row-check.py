"""Session 104 row checks (task rows 0 to 19, the H rows and the gate; implementation-plan.md
§Verification Plan, §Plan-local scripts).

Written in the shape of Session 102's (2026-11-22-tray-show-and-baseline-fixes/row-check.py),
whose ``top_level_sources``, red-record, red-unchanged and register checks it keeps. Every
subcommand exits 0 when it finds no problem, 1 when it does, 2 on a usage error:

* ``steps [--emit]``: ``row-run.ps1`` between ``# BEGIN STEPS`` and ``# END STEPS`` equals the
  block generated from task.md §Row steps (``--emit`` prints that block).
* ``red-record --row N FILE ...`` / ``red-unchanged``: as Session 102's, with no exception.
* ``pins-unchanged [--row 4|14]``: row 4, the five suites' files have their baseline-scope hashes;
  row 14, no top-level node whose name holds ``sabr`` changed in test_services.py and
  test_youtube_adapter.py; with no row (the gate), the read-only test files' pins, the row-14
  rule and the two ``pins-moved`` rules.
* ``pins-moved --row 7|11``: §Pins that move, by top-level ast node (Python) or by test block
  (TypeScript), against row 0.
* ``scope-paths``: AC-168.8; every changed path is in §Files Modified, this session's own
  files, or another session's (a note); read-only paths keep their hashes; no release note; the
  tags are row 0's.
* ``lock [--installed]``: ``YTDLP_LOCK`` and ``HOLD_OVERRIDE``; writes ``ycc-hold.txt``.
* ``proof-recorded before|after|fallback``, ``proof-pair --classify|--require-proved --out F``:
  ``PROOF_PAIR``.
* ``variant-gate --stage red|green``: ``VARIANT_FALLBACK``.
* ``type-only``, ``kept``, ``openapi``, ``test-ids``, ``licence``,
  ``snapshot-paths --stage red|green --out F``, ``e2e-red``, ``e2e-result``, ``canon``,
  ``register``, ``status --stage ready|approved``, ``no-deselect``, ``metrics``,
  ``commit-draft``, ``next-prompt``: as task.md §Row steps says.
* ``--selftest``: each subcommand's passing case passes and its failing case fails.
"""

from __future__ import annotations

import ast
import difflib
import hashlib
import importlib.metadata
import importlib.util
import json
import pathlib
import re
import shlex
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass

import yaml

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SLUG = "2026-11-26-ytdlp-challenge-and-cookie-test"
PLAN_REL = f"docs/execution/plans/{SLUG}"
RECEIPTS = pathlib.Path("C:/Temp/av-kit") / SLUG
RED_STORE = "ycc-red-hashes.json"
RED_COPIES = "ycc-red-copies"


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


eolc = _load("ycc_eol_check", "eol-check.py")
pe = _load("ycc_proof_extract", "proof-extract.py")
SCOPE: dict[str, str] = eolc.SCOPE
GROUPING: str = eolc.GROUPING

INFRA_PY = "packages/infrastructure/pyproject.toml"
ROOT_PY = "pyproject.toml"
LOCK = "uv.lock"
LOCK_TEST = "tests/unit/test_ytdlp_lock.py"
ENUMS = "packages/core/src/avkit_core/domain/enums.py"
DOMAIN = "packages/core/src/avkit_core/domain/download.py"
ADAPTER = "packages/infrastructure/src/avkit_infra/youtube/adapter.py"
SERVICE = "packages/core/src/avkit_core/services/download.py"
ROUTES = "packages/api/src/avkit_api/routes/downloads.py"
OPENAPI = "openapi.committed.json"
TEST_IDS = "ui/tests/e2e/test-ids.ts"
DLPAGE = "ui/src/renderer/src/features/downloader/DownloaderPage.tsx"
SABR_PANEL = "ui/src/renderer/src/features/downloader/sabr-panel.ts"
COOKIE_RESULT = "ui/src/renderer/src/features/downloader/cookie-test-result.ts"
SABR_TEST = "ui/tests/unit/sabr-panel.test.ts"
BEHAVIOR_TEST = "ui/tests/unit/downloader-page.behavior.test.ts"
E2E_COOKIE = "ui/tests/e2e/downloader-cookie-test.test.ts"
ADV_GAP = "ui/tests/e2e/downloader-advanced-gap.test.ts"
TEST_DOMAIN = "tests/unit/test_domain.py"
TEST_SERVICES = "tests/unit/test_services.py"
YT_TEST = "tests/integration/test_youtube_adapter.py"
TEST_API = "tests/e2e/test_api_downloads.py"
API_FAKES = "tests/e2e/api_fakes.py"
FETCH_DENO = "tests/unit/test_fetch_deno.py"
CLIENT_FALLBACK = "tests/integration/test_youtube_client_fallback.py"
EXTRACT_OPTIONS = "tests/unit/test_extract_options.py"
JS_WIRING = "tests/integration/test_js_runtime_wiring.py"
REGISTER = ".agent/context/known-issues.yaml"
MEU_STATUS = ".agent/context/meu-status.yaml"
METRICS = "docs/execution/metrics.md"

#: "Read, never changed" (implementation-plan.md §Files Modified).
READ_ONLY = (
    ADV_GAP,
    FETCH_DENO,
    CLIENT_FALLBACK,
    EXTRACT_OPTIONS,
    JS_WIRING,
    "packages/core/src/avkit_core/ports/youtube.py",
    "ui/src/renderer/src/features/downloader/cookie-bar.ts",
    "ui/src/renderer/src/features/downloader/downloader-help-content.ts",
    "docs/build-plan/gui-actions-index.md",
)
READ_TESTS = (ADV_GAP, FETCH_DENO, CLIENT_FALLBACK, EXTRACT_OPTIONS, JS_WIRING)
ROW4 = (FETCH_DENO, YT_TEST, CLIENT_FALLBACK, EXTRACT_OPTIONS, JS_WIRING)
PY_PINNED = (TEST_DOMAIN, TEST_SERVICES, YT_TEST, TEST_API, API_FAKES)
#: SABR_KEPT: the named sources, by member.
KEPT = {
    ADAPTER: (
        "SABR_PHRASES",
        "SABR_EXTRACTOR_ARGS",
        "sabr_phrase",
        "YouTubeAdapter.check_sabr_status",
    ),
    SERVICE: (
        "DownloadService.check_sabr",
        "DownloadService.force_sabr",
        "DownloadService.clear_sabr",
    ),
    ROUTES: ("check_sabr", "force_sabr", "clear_sabr"),
}
#: §Pins that move (Python): test -> (new needles, kept needles).
MOVED_PY = {
    TEST_API: {
        "test_ac_15_7_cookie_test_envelope": (
            ('"outcome": "ok"', "Sign in to confirm", '"check_failed"'),
            ('"HTTP_COOKIE" not in ok.text',),
        )
    },
    TEST_DOMAIN: {
        "test_ac_4_4_cookie_test_result_shape": (
            ('("ok", "error_message", "outcome")',),
            ('"cookies" not in',),
        )
    },
    YT_TEST: {
        "test_ac_6_13_test_cookies_never_raises_cookie_error": (
            ("CookieTestOutcome.unreadable", "CookieTestOutcome.ok", "outcome=None"),
            ('"Netscape" not in',),
        )
    },
}
CLAUSE = "Check SABR does not use cookies"
#: §Pins that move (TypeScript): file -> {test title: clauses added}.
MOVED_TS = {
    SABR_TEST: {
        "AC-138.8 each snapshot gives its contract text": 2,
        "AC-138.8 the time is zero-padded local time": 1,
    },
    BEHAVIOR_TEST: {
        "AC-138.8 the SABR panel shows an Inactive and an Active check with their time": 2
    },
}
TS_OTHER = re.compile(r"outcome|error_message|cookie", re.IGNORECASE)
GUARD = "test_ac_168_6_adapter_sets_no_player_js_variant"
TV_TEST = "test_ac_168_6_adapter_passes_player_js_variant_tv"
HOLD_LINE = "exclude-newer-package = { yt-dlp = false }"
NEW_YTDLP = "2026.11.23"
OLD_YTDLP = "2026.10.26"
EJS = "0.8.0"
TEST_IDS_BLOCK = (
    b"// MEU-169 cookie test result ID.\r\n"
    b"export const COOKIE_TEST_RESULT = 'cookie-test-result'\r\n"
)
RED_TITLES = (
    "AC-169.11 each Test Cookies outcome shows its text beside the button",
    "AC-169.11 the button is disabled while the reply is pending",
    "AC-169.11 the Advanced panel keeps its ids, tail and gap with a result shown",
    "AC-170.4 a detected SABR check says that it does not use cookies",
)
E2E_GUARD = "AC-170.4 a forced SABR status has no clause"
E2E_LINE = re.compile(r"^e2e-remote: (\S+) exit=(-?\d+) run=(\S+) receipts=(.+?)\s*$")
ANSI = re.compile(r"\x1b\[[0-9;]*m")
ISSUE_FIELDS = {"status", "verification", "resolution_path", "meu_links", "root_cause"}
SOLVER_ISSUE = "YTDLP-CHALLENGE-SOLVE-FAILS"
GROUPING_OLD = "| planning |"
GROUPING_NEW = "| executed (Session 104) |"
SUBJECT = (
    "fix(downloader): yt-dlp 2026.11.23, a Test Cookies result line and a clearer SABR status "
    "(MEU-168, MEU-169, MEU-170)"
)
MECHANISMS = (
    "YTDLP_LOCK",
    "HOLD_OVERRIDE",
    "PROOF_PAIR",
    "VARIANT_FALLBACK",
    "COOKIE_TEST_OUTCOME",
    "COOKIE_TEST_STEPS",
    "COOKIE_TEST_REASON",
    "COOKIE_TEST_WIRE",
    "COOKIE_TEST_SHOWN",
    "COOKIE_TEST_BUSY",
    "SABR_CHECK_SCOPE",
    "SABR_KEPT",
)
NEXT_PROMPT = pathlib.Path("C:/Temp/av-kit/next-session-prompt.md")
OTHER_PLAN = re.compile(r"^docs/execution/plans/2026-11-(?:1[6-9]|2[0-6])-[^/]+/")
OTHER_ARTIFACT = re.compile(
    r"^(?:\.agent/context/handoffs/2026-11-2\d-|docs/proposals/2026-11-2\d-|"
    r"docs/execution/reflections/2026-11-2\d-|\.agent/context/grouping/2026-11-2\d-)"
)
RELEASE = re.compile(r"changelog|release[-_ ]?notes?|docs/releases/", re.IGNORECASE)
HOME = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]|/Users/|/home/", re.IGNORECASE)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


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
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: pathlib.Path, root: pathlib.Path) -> str:
    path = path if path.is_absolute() else root / path
    return path.resolve().relative_to(root.resolve()).as_posix()


def _bare_lf(raw: bytes) -> int:
    return raw.count(b"\n") - raw.count(b"\r\n")


def _lines(raw: bytes | str) -> list[str]:
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    return text.replace("\r\n", "\n").split("\n")


def _ops(a: list[str], b: list[str]):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()


def _diff(a: list[str], b: list[str]) -> tuple[list[str], list[str]]:
    removed: list[str] = []
    added: list[str] = []
    for tag, i1, i2, j1, j2 in _ops(a, b):
        if tag != "equal":
            removed += a[i1:i2]
            added += b[j1:j2]
    return removed, added


def _exit(path: pathlib.Path) -> int | None:
    if not path.is_file():
        return None
    try:
        return int(path.read_bytes().decode("ascii", "replace").strip().lstrip("\ufeff"))
    except ValueError:
        return None


# --- top-level sources (row 0's baseline-pins.json and the checks below)
def _node_key(node: ast.stmt, source: str) -> str:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name
    if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) for t in node.targets):
        return ",".join(t.id for t in node.targets if isinstance(t, ast.Name))
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id
    return f"{type(node).__name__}:{source}"


def _span(node: ast.stmt, lines: list[str]) -> str:
    decorators = getattr(node, "decorator_list", [])
    start = min([node.lineno, *(d.lineno for d in decorators)])
    end = node.end_lineno or node.lineno
    return "\n".join(lines[start - 1 : end])


def _keyed(body: list[ast.stmt], lines: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for node in body:
        source = _span(node, lines)
        key = base = _node_key(node, source)
        n = 2
        while key in out:
            key = f"{base}#{n}"
            n += 1
        out[key] = source
    return out


def top_level_sources(text: str) -> dict[str, str]:
    """Each top-level node's source (LF), from its first decorator to its last line, by name."""
    text = text.replace("\r\n", "\n")
    return _keyed(ast.parse(text).body, text.split("\n"))


def member_sources(text: str, names) -> dict[str, str]:
    """The source of each named top-level node or ``Class.method``; ``<missing>`` if absent."""
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")
    tree = ast.parse(text)
    out: dict[str, str] = {}
    for name in names:
        owner, _, member = name.rpartition(".")
        body = tree.body
        if owner:
            cls = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == owner]
            body = cls[0].body if cls else []
        found = [n for n in body if _node_key(n, "").split(",")[0] == (member or name)]
        out[name] = _span(found[0], lines) if len(found) == 1 else "<missing>"
    return out


def _is_import(key: str) -> bool:
    return key.startswith(("Import:", "ImportFrom:"))


def _import_names(sources: dict[str, str]) -> set[str]:
    names: set[str] = set()
    for key, source in sources.items():
        if _is_import(key):
            for node in ast.parse(source).body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names |= {a.asname or a.name for a in node.names}
    return names


def _import_ok(base: dict[str, str], now: dict[str, str], key: str) -> bool:
    return _import_names({key: base[key]}) <= _import_names(now)


# --- steps
ROW_STEP = re.compile(
    r"^\| (?P<id>[0-9H][0-9A-Za-z-]*\.\d+) \| (?P<flags>.*?) \| `(?P<cmd>[^`]+)` \| "
    r"`(?P<receipt>[^`]+)` \| .* \|$"
)
FLAG_WORDS = {
    "recorded": "recorded",
    "fallback only": "fallback",
    "proved only": "proved",
    "in `ui`": "ui",
}
PY = ["uv", "run", "--no-sync", "python"]


def _expand(token: str) -> str:
    if token == "PLAN":
        return PLAN_REL
    if token.startswith("PLAN/"):
        return PLAN_REL + token[4:]
    if token.startswith("R/"):
        return RECEIPTS.as_posix() + token[1:]
    return token


def parse_steps(task_text: str) -> list[dict[str, object]]:
    lines = _lines(task_text)
    start = lines.index("## Row steps")
    out: list[dict[str, object]] = []
    for line in lines[start + 1 :]:
        if line.startswith("#"):
            break
        m = ROW_STEP.match(line)
        if not m:
            if re.match(r"^\| [0-9H]", line):
                raise ValueError(f"steps: an unparsed step row: {line[:70]}")
            continue
        flags = []
        for word in filter(None, m["flags"].strip().split("; ")):
            if word not in FLAG_WORDS:
                raise ValueError(f"steps: unknown flag {word!r} in {m['id']}")
            flags.append(FLAG_WORDS[word])
        tokens = shlex.split(m["cmd"], posix=True)
        if tokens[0] == "PY":
            tokens = [*PY, *tokens[1:]]
        out.append(
            {
                "id": m["id"],
                "flags": ",".join(flags),
                "receipt": m["receipt"],
                "argv": [_expand(t) for t in tokens],
            }
        )
    return out


def _ps(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def emit_steps(steps: list[dict[str, object]]) -> str:
    out = []
    for s in steps:
        argv = ", ".join(_ps(str(a)) for a in s["argv"])  # type: ignore[union-attr]
        out.append(
            f"$S.Add(@{{ Id = {_ps(str(s['id']))}; Flags = {_ps(str(s['flags']))}; "
            f"Receipt = {_ps(str(s['receipt']))}; Argv = @({argv}) }})"
        )
    return "\n".join(out) + "\n"


def steps_check(ctx: Ctx) -> list[str]:
    want = emit_steps(parse_steps((ctx.plan / "task.md").read_bytes().decode("utf-8")))
    script = (ctx.plan / "row-run.ps1").read_bytes().decode("utf-8").replace("\r\n", "\n")
    begin, end = "# BEGIN STEPS\n", "# END STEPS"
    if script.count(begin) != 1 or script.count(end) != 1:
        return ["steps: row-run.ps1 lacks one BEGIN STEPS and one END STEPS marker"]
    got = script.split(begin, 1)[1].split(end, 1)[0]
    print(f"steps: {want.count(chr(10))} step(s) from task.md; {got.count(chr(10))} in row-run.ps1")
    if got != want:
        a, b = got.split("\n"), want.split("\n")
        first = next((i for i, (x, y) in enumerate(zip(a, b, strict=False)) if x != y), None)
        return [f"steps: row-run.ps1 differs from task.md §Row steps at block line {first}"]
    return []


# --- red-record, red-unchanged
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
    record.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
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
        p = ctx.root / name
        got = sha(p) if p.is_file() else "absent"
        print(f"red-unchanged {name} (latest row {row}): {'ok' if got == want else 'CHANGED'}")
        if got != want:
            problems.append(f"red-unchanged: {name} (row {row}) is {got[:16]}, not {want[:16]}")
    if not latest:
        problems.append("red-unchanged: no file recorded")
    return problems


# --- pins-unchanged, pins-moved
def _sabr_nodes(sources: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in sources.items() if ":" not in k and "sabr" in k.lower()}


def _sabr_unchanged(ctx: Ctx) -> list[str]:
    pins = ctx.pjson("baseline-pins.json")
    problems: list[str] = []
    for p in (TEST_SERVICES, YT_TEST):
        base = _sabr_nodes(pins["ast"][p])
        now = _sabr_nodes(top_level_sources(ctx.text(p)))
        print(f"pins sabr {p}: {len(base)} node(s) at row 0, {len(now)} now")
        for k in sorted(set(base) | set(now)):
            if base.get(k) != now.get(k):
                problems.append(
                    f"pins: {p}:{k} {'changed' if k in base and k in now else 'added or removed'}"
                )
    return problems


def pins_unchanged(ctx: Ctx, row: str | None) -> list[str]:
    problems: list[str] = []
    if row == "4":
        scope = ctx.pjson("baseline-scope.json")
        for p in ROW4:
            ok = sha(ctx.root / p) == scope[p]
            print(f"pins row 4 {p}: {'ok' if ok else 'CHANGED'}")
            if not ok:
                problems.append(f"pins: {p} differs from its baseline hash")
        return problems
    if row == "14":
        return _sabr_unchanged(ctx)
    pins = ctx.pjson("baseline-pins.json")
    for p, want in pins["files"].items():
        ok = (ctx.root / p).is_file() and sha(ctx.root / p) == want
        print(f"pins file {p}: {'ok' if ok else 'CHANGED'}")
        if not ok:
            problems.append(f"pins: {p} differs from its pin")
    return [*problems, *_sabr_unchanged(ctx), *pins_moved(ctx, "7"), *pins_moved(ctx, "11")]


def _class_fake_ok(base_src: str, now_src: str) -> bool:
    """A class whose only changed members are ``test_cookies`` (with outcome) and ``__init__``."""
    b_tree, n_tree = ast.parse(base_src).body, ast.parse(now_src).body
    if len(b_tree) != 1 or len(n_tree) != 1:
        return False
    b, n = b_tree[0], n_tree[0]
    if not (isinstance(b, ast.ClassDef) and isinstance(n, ast.ClassDef)):
        return False
    if b.name != n.name or ast.dump(ast.Tuple(b.bases)) != ast.dump(ast.Tuple(n.bases)):
        return False
    bm = _keyed(b.body, base_src.split("\n"))
    nm = _keyed(n.body, now_src.split("\n"))
    if list(bm) != list(nm):
        return False
    changed = [k for k in bm if bm[k] != nm[k]]
    if not changed or set(changed) - {"test_cookies", "__init__"}:
        return False
    if "test_cookies" in changed and "outcome" not in nm["test_cookies"]:
        return False
    if "__init__" in changed:
        _, added = _diff(bm["__init__"].split("\n"), nm["__init__"].split("\n"))
        if any("cookie" not in line.lower() for line in added):
            return False
    return True


def _pins_moved_py(ctx: Ctx) -> list[str]:
    pins = ctx.pjson("baseline-pins.json")
    problems: list[str] = []
    for p in PY_PINNED:
        base = pins["ast"][p]
        now = top_level_sources(ctx.text(p))
        moved = MOVED_PY.get(p, {})
        for k in base.keys() - now.keys():
            if not (_is_import(k) and _import_ok(base, now, k)):
                problems.append(f"pins-moved: {p}: {k[:60]} was removed")
        added = [k for k in now.keys() - base.keys() if not _is_import(k)]
        for k in added:
            if not k.startswith(("test_ac_169_", "_")):
                problems.append(f"pins-moved: {p}: {k[:60]} is new and not an AC-169 test")
        changed = [k for k in base.keys() & now.keys() if base[k] != now[k]]
        for k in changed:
            if k in moved:
                new, kept = moved[k]
                lost = [n for n in new if n not in now[k]]
                gone = [n for n in kept if n not in now[k] or n not in base[k]]
                if lost or gone:
                    problems.append(f"pins-moved: {p}:{k} lacks {lost} new, {gone} kept")
            elif not _class_fake_ok(base[k], now[k]):
                problems.append(f"pins-moved: {p}:{k[:60]} changed and is not a named pin or fake")
        for k in moved:
            if k not in changed:
                problems.append(f"pins-moved: {p}:{k} did not move")
        print(f"pins-moved {p}: changed {sorted(changed)}; new {sorted(added)}")
    return problems


TS_BLOCK = re.compile(r"^\s*(it|test|describe)(?:\.\w+)*\(\s*(['\"`])(.*?)\2")
CLOSER = re.compile(r"^\s*[})\]]+[;,)]*\s*$")


def ts_blocks(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    key, buf = "head", []

    def store(k: str, lines: list[str]) -> None:
        while lines and (not lines[-1].strip() or CLOSER.match(lines[-1])):
            lines.pop()
        name, n = k, 2
        while name in out:
            name = f"{k}#{n}"
            n += 1
        out[name] = lines

    for line in _lines(text):
        m = TS_BLOCK.match(line)
        if m:
            store(key, buf)
            key = f"describe:{m[3]}" if m[1] == "describe" else m[3]
            buf = [line]
        else:
            buf.append(line)
    store(key, buf)
    return out


def _pins_moved_ts(ctx: Ctx) -> list[str]:
    problems: list[str] = []
    for p, moved in MOVED_TS.items():
        base, now = ts_blocks(ctx.base(p).decode("utf-8")), ts_blocks(ctx.text(p))
        for k in base.keys() - now.keys():
            problems.append(f"pins-moved: {p}: {k[:70]} was removed")
        for k in now.keys() - base.keys():
            title = k.removeprefix("describe:")
            ok = (
                re.search(r"MEU-1(69|70)|AC-1(69|70)", title)
                if k.startswith("describe:")
                else title.startswith(("AC-169.", "AC-170."))
            )
            if not ok:
                problems.append(f"pins-moved: {p}: new block {k[:70]} is not AC-169 or AC-170")
        for k in moved:
            if k not in base or k not in now:
                problems.append(f"pins-moved: {p}: {k} is missing")
        changed = [k for k in base.keys() & now.keys() if base[k] != now[k]]
        for k in changed:
            a, b = base[k], now[k]
            ops = [op for op in _ops(a, b) if op[0] != "equal"]
            if k in moved:
                gained = "\n".join(b).count(CLAUSE) - "\n".join(a).count(CLAUSE)
                bad = [op for op in ops if op[0] == "delete"] + [
                    op for op in ops if any(CLAUSE not in x for x in b[op[3] : op[4]])
                ]
                if gained != moved[k] or bad:
                    problems.append(
                        f"pins-moved: {p}:{k} gained {gained} clause(s), want {moved[k]}"
                    )
            else:
                touched = [
                    x
                    for op in ops
                    for x in (a[op[1] : op[2]] if op[0] == "delete" else b[op[3] : op[4]])
                ]
                if any(not TS_OTHER.search(x) for x in touched):
                    problems.append(f"pins-moved: {p}:{k[:70]} changed beyond the cookie result")
        for k in moved:
            if k not in changed:
                problems.append(f"pins-moved: {p}:{k} did not move")
        print(f"pins-moved {p}: changed {sorted(changed)}")
    return problems


def pins_moved(ctx: Ctx, row: str) -> list[str]:
    if row == "7":
        return _pins_moved_py(ctx)
    if row == "11":
        return _pins_moved_ts(ctx)
    raise ValueError("pins-moved --row 7|11")


# --- scope-paths
def _git(root: pathlib.Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout


def _changed(root: pathlib.Path) -> list[str]:
    raw = _git(root, "diff", "--no-renames", "--name-only", "-z", "HEAD")
    raw += _git(root, "ls-files", "--others", "--exclude-standard", "-z")
    return sorted({x.decode("utf-8") for x in raw.split(b"\0") if x})


def _other_texts(root: pathlib.Path) -> str:
    texts = []
    for folder in sorted((root / "docs/execution/plans").glob("2026-11-2*")):
        if folder.name != SLUG and folder.is_dir():
            texts += [f.read_bytes().decode("utf-8", "replace") for f in folder.glob("*.md")]
    return "\n".join(texts)


def scope_paths(ctx: Ctx, changed: list[str] | None = None, tags: str | None = None) -> list[str]:
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

    def other(p: str) -> bool:
        return bool(OTHER_PLAN.match(p) or OTHER_ARTIFACT.match(p) or p in texts)

    for p in changed:
        if "__pycache__" in p or p.startswith(".agent/fleet/hub"):
            continue
        if RELEASE.search(p):
            problems.append(f"scope-paths: {p} is a release note or changelog")
            continue
        if p in SCOPE or p.startswith(own):
            kept += 1
            continue
        if p in dirty and (ctx.root / p).is_file() and sha(ctx.root / p) == dirty[p]:
            notes += 1
            continue
        if other(p):
            notes += 1
            print(f"scope-paths note: {p} is another session's")
            continue
        problems.append(f"scope-paths: {p} is outside §Files Modified")
    for p in READ_ONLY:
        if sha(ctx.root / p) != scope[p]:
            problems.append(f"scope-paths: read-only {p} changed")
    tags = _git(ctx.root, "tag").decode("utf-8") if tags is None else tags
    want = (ctx.r / "baseline-tags.txt").read_bytes().decode("utf-8")
    if sorted(tags.split()) != sorted(want.split()):
        problems.append("scope-paths: the tags differ from row 0's")
    print(f"scope-paths: {len(changed)} changed, {kept} in scope, {notes} note(s)")
    return problems


# --- lock
def _lock_blocks(text: str) -> tuple[str, dict[str, str]]:
    parts = text.split("\n[[package]]\n")
    blocks: dict[str, str] = {}
    for b in parts[1:]:
        m = re.match(r'name = "([^"]+)"', b)
        name = key = m.group(1) if m else "?"
        n = 2
        while key in blocks:
            key = f"{name}#{n}"
            n += 1
        blocks[key] = b
    return parts[0], blocks


def _hold_line(line: str) -> bool:
    return (
        not line.strip()
        or "exclude-newer-package" in line
        or bool(re.match(r'^\s*"?yt-dlp"?\s*=\s*false', line))
    )


def _version(block: str) -> str:
    m = re.search(r'^version = "([^"]+)"', block, re.MULTILINE)
    return m.group(1) if m else "?"


def lock(
    ctx: Ctx, installed: bool = False, getter: Callable[[str], str] | None = None
) -> list[str]:
    problems: list[str] = []
    if installed:
        get = getter or importlib.metadata.version
        got = {"yt-dlp": get("yt-dlp"), "yt-dlp-ejs": get("yt-dlp-ejs")}
        print(f"lock --installed: {got}")
        if got != {"yt-dlp": NEW_YTDLP, "yt-dlp-ejs": EJS}:
            problems.append(f"lock: installed {got}")
        return problems
    root_base, root_now = ctx.base(ROOT_PY).decode(), ctx.text(ROOT_PY)
    hold = HOLD_LINE in root_now
    if hold:
        removed, added = _diff(_lines(root_base), _lines(root_now))
        now_lines = _lines(root_now)
        at = now_lines.index(HOLD_LINE)
        heads = [x for x in now_lines[:at] if x.startswith("[")]
        if removed or added != [HOLD_LINE] or not heads or heads[-1] != "[tool.uv]":
            problems.append("lock: pyproject.toml differs by more than the hold line in [tool.uv]")
    elif root_now != root_base:
        problems.append("lock: pyproject.toml changed without the hold line")
    i_base, i_now = ctx.base(INFRA_PY), ctx.now(INFRA_PY)
    if i_base.count(b'"yt-dlp",') != 1 or i_now != i_base.replace(
        b'"yt-dlp",', f'"yt-dlp>={NEW_YTDLP}",'.encode()
    ):
        problems.append("lock: the infra pyproject is not row 0's with yt-dlp>=2026.11.23")
    raw = ctx.now(LOCK)
    if b"\r" in raw:
        problems.append("lock: uv.lock has a CR")
    hb, bb = _lock_blocks(ctx.base(LOCK).decode())
    hn, bn = _lock_blocks(raw.decode())
    removed, added = _diff(hb.split("\n"), hn.split("\n"))
    if (removed or added) and not (hold and all(_hold_line(x) for x in removed + added)):
        problems.append(f"lock: the header changed: {(removed + added)[:3]}")
    if set(bb) != set(bn):
        problems.append(
            f"lock: packages added {sorted(set(bn) - set(bb))}, removed {sorted(set(bb) - set(bn))}"
        )
    for name in sorted(set(bb) & set(bn)):
        if bb[name] == bn[name] or name == "yt-dlp":
            continue
        if name == "avkit-infra":
            removed, added = _diff(bb[name].split("\n"), bn[name].split("\n"))
            if all('"yt-dlp"' in x and "yt-dlp-ejs" not in x for x in removed + added):
                continue
        problems.append(f"lock: the {name} entry changed")
    versions = {k: _version(bn.get(k, "")) for k in ("yt-dlp", "yt-dlp-ejs")}
    if versions != {"yt-dlp": NEW_YTDLP, "yt-dlp-ejs": EJS}:
        problems.append(f"lock: versions {versions}")
    word = "yes" if hold else "no"
    (ctx.r / "ycc-hold.txt").write_text(f"hold-override: {word}\n", encoding="utf-8")
    print(f"lock: versions {versions}; hold-override: {word}")
    return problems


# --- proof-recorded, proof-pair, variant-gate
EXPECT = {"before": "challenge-errors", "after": "clean", "fallback": "clean"}


def proof_recorded(ctx: Ctx, which: str) -> list[str]:
    if which not in EXPECT:
        raise ValueError("proof-recorded before|after|fallback")
    receipt = ctx.r / f"ycc-proof-{which}.txt"
    js = ctx.r / f"ycc-proof-{which}.json"
    if not receipt.is_file() or not js.is_file():
        return [f"proof-recorded: {receipt.name} or {js.name} is missing"]
    data = json.loads(js.read_text(encoding="utf-8"))
    # rtk prints its own banner into a receipt; it is the harness, not a proof line (D-1489).
    lines = [x for x in _lines(ctx.rtext(receipt.name)) if x.strip() and not x.startswith("[rtk] ")]
    want = [f"{k}={data[k]}" for k in pe.FIELDS]
    if data["verdict"] == "blocked":
        want.append("INCOMPLETE VERIFICATION")
    problems: list[str] = []
    if lines != want:
        extra = [x[:60] for x in lines if x not in want]
        problems.append(f"proof-recorded: the receipt is not the field lines (extra {extra[:3]})")
    code = _exit(receipt.with_name(receipt.name + ".exit"))
    want_code = (
        4 if data["verdict"] == "blocked" else (0 if data["verdict"] == EXPECT[which] else 1)
    )
    if code != want_code:
        problems.append(f"proof-recorded: exit {code}, want {want_code} for {data['verdict']}")
    version = OLD_YTDLP if which == "before" else NEW_YTDLP
    if data["yt-dlp"] != version:
        problems.append(f"proof-recorded: yt-dlp={data['yt-dlp']}, want {version}")
    if which == "fallback" and data["variant"] != "tv":
        problems.append(f"proof-recorded: variant={data['variant']}, want tv")
    print(f"proof-recorded {which}: verdict={data['verdict']} exit={code}")
    return problems


def _verdict(ctx: Ctx, which: str) -> dict:
    return json.loads((ctx.r / f"ycc-proof-{which}.json").read_text(encoding="utf-8"))


def proof_pair(ctx: Ctx, mode: str, out: pathlib.Path) -> list[str]:
    before = _verdict(ctx, "before")
    if mode == "--classify":
        after = _verdict(ctx, "after")
        b, a = before["verdict"], after["verdict"]
        if b == "challenge-errors" and a == "clean":
            word = "proved"
        elif b == "challenge-errors" and a == "challenge-errors" and after["variant"] != "tv":
            word = "fallback-applies"
        else:
            word = "incomplete"
        out.write_text(word + "\n", encoding="utf-8")
        print(f"proof-pair: before {b}, after {a} (variant {after['variant']}): {word}")
        return []
    if mode != "--require-proved":
        raise ValueError("proof-pair --classify|--require-proved --out FILE")
    last = "fallback" if (ctx.r / "ycc-proof-fallback.json").is_file() else "after"
    v = _verdict(ctx, last)["verdict"]
    word = "proved" if before["verdict"] == "challenge-errors" and v == "clean" else "not-proved"
    out.write_text(word + "\n", encoding="utf-8")
    print(f"proof-pair: before {before['verdict']}, last run ({last}) {v}: {word}")
    return [] if word == "proved" else [f"proof-pair: {word}"]


def _word(ctx: Ctx, name: str) -> str:
    p = ctx.r / name
    return p.read_text(encoding="utf-8").strip() if p.is_file() else ""


def variant_gate(ctx: Ctx, stage: str) -> list[str]:
    fallback = _word(ctx, "ycc-proof-pair.txt") == "fallback-applies"
    red = _red_data(ctx.r / RED_STORE)["rows"]
    adapter = ctx.now(ADAPTER)
    if not fallback:
        if stage == "red":
            ok = sha(ctx.root / LOCK_TEST) == red.get("2", {}).get(LOCK_TEST)
        else:
            ok = b"player_js_variant" not in adapter and GUARD in top_level_sources(
                ctx.text(LOCK_TEST)
            )
        print(f"variant-gate {stage}: not-needed ({'ok' if ok else 'FAILED'})")
        return [] if ok else [f"variant-gate {stage}: not-needed, but the check failed"]
    problems: list[str] = []
    if stage == "red":
        base = top_level_sources((ctx.r / RED_COPIES / "row2" / LOCK_TEST).read_bytes().decode())
        now = top_level_sources(ctx.text(LOCK_TEST))
        want_keys = [TV_TEST if k == GUARD else k for k in base]
        if list(now) != want_keys or any(now[k] != base[k] for k in base if k != GUARD):
            problems.append("variant-gate red: more than the guard changed in the test file")
        if "5a" not in red:
            problems.append("variant-gate red: row 5a is not recorded")
        if adapter != ctx.base(ADAPTER):
            problems.append("variant-gate red: the adapter changed")
    else:
        kept = ctx.pjson("baseline-pins.json")["kept"][ADAPTER]
        names = ("SABR_EXTRACTOR_ARGS", "YouTubeAdapter.check_sabr_status")
        now = member_sources(adapter.decode("utf-8"), names)
        if b"player_js_variant" not in adapter:
            problems.append("variant-gate green: the adapter sets no player_js_variant")
        if any(now[n] != kept[n] for n in names):
            problems.append("variant-gate green: the SABR probe's arguments changed")
    print(f"variant-gate {stage}: fallback; {len(problems)} problem(s)")
    return problems


# --- type-only, kept, openapi, test-ids, licence
def type_only(ctx: Ctx) -> list[str]:
    fallback = _word(ctx, "ycc-proof-pair.txt") == "fallback-applies"
    problems: list[str] = []
    product = [
        p
        for p in SCOPE
        if p.startswith(("packages/", "ui/src/", "mcp-server/src/")) or p == OPENAPI
    ]
    for p in product:
        if p in (ENUMS, DOMAIN, INFRA_PY) or (p == ADAPTER and fallback):
            continue
        if not (ctx.copies / p).is_file():
            if (ctx.root / p).exists():
                problems.append(f"type-only: new {p} exists")
        elif ctx.now(p) != ctx.base(p):
            problems.append(f"type-only: {p} changed")
    b, n = top_level_sources(ctx.base(ENUMS).decode()), top_level_sources(ctx.text(ENUMS))
    if list(n.keys() - b.keys()) != ["CookieTestOutcome"] or b.keys() - n.keys():
        problems.append(f"type-only: enums nodes added {sorted(n.keys() - b.keys())}")
    elif any(b[k] != n[k] for k in b):
        problems.append("type-only: an existing enum changed")
    else:
        cls = ast.parse(n["CookieTestOutcome"]).body[0]
        members = [
            t.id
            for s in getattr(cls, "body", [])
            if isinstance(s, ast.Assign)
            for t in s.targets
            if isinstance(t, ast.Name)
        ]
        if members != ["ok", "unreadable", "check_failed"]:
            problems.append(f"type-only: CookieTestOutcome members {members}")
    b, n = top_level_sources(ctx.base(DOMAIN).decode()), top_level_sources(ctx.text(DOMAIN))
    for k in b.keys() - n.keys():
        if not (_is_import(k) and _import_ok(b, n, k)):
            problems.append(f"type-only: {DOMAIN}: {k[:60]} removed")
    for k in n.keys() - b.keys():
        if not _is_import(k):
            problems.append(f"type-only: {DOMAIN}: {k[:60]} added")
    for k in b.keys() & n.keys():
        if b[k] != n[k] and k != "CookieTestResult":
            problems.append(f"type-only: {DOMAIN}: {k[:60]} changed")
    a, z = b["CookieTestResult"].split("\n"), n["CookieTestResult"].split("\n")
    ops = [op for op in _ops(a, z) if op[0] != "equal"]
    inserted = [x for op in ops for x in z[op[3] : op[4]]]
    if any(op[0] != "insert" for op in ops) or not inserted:
        problems.append("type-only: CookieTestResult is not row 0's with inserted lines")
    if any("outcome" not in x or re.search(r"require|raise|__post_init__", x) for x in inserted):
        problems.append(f"type-only: CookieTestResult inserted {inserted}")
    print(f"type-only: CookieTestResult inserted {inserted}; fallback {fallback}")
    return problems


def _sabr_openapi(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    schemas = data.get("components", {}).get("schemas", {})
    return {
        "schemas": {k: v for k, v in schemas.items() if "sabr" in k.lower()},
        "paths": {k: v for k, v in data.get("paths", {}).items() if "sabr" in k.lower()},
    }


def kept(ctx: Ctx) -> list[str]:
    pins = ctx.pjson("baseline-pins.json")["kept"]
    problems: list[str] = []
    for path, names in KEPT.items():
        now = member_sources(ctx.text(path), names)
        for name in names:
            same = now[name] == pins[path][name] and now[name] != "<missing>"
            print(f"kept {path}:{name}: {'ok' if same else 'CHANGED'}")
            if not same:
                problems.append(f"kept: {path}:{name} changed")
    base, now = _sabr_openapi(ctx.base(OPENAPI)), _sabr_openapi(ctx.now(OPENAPI))
    if base != now or not base["schemas"] or not base["paths"]:
        problems.append("kept: the SABR schemas or paths of openapi.committed.json changed")
    print(f"kept: openapi {sorted(base['schemas'])}, {len(base['paths'])} SABR path(s)")
    return problems


def openapi(ctx: Ctx) -> list[str]:
    problems: list[str] = []
    if _exit(ctx.r / "ycc-row9-drift.txt.exit") in (0, None):
        problems.append("openapi: the drift check before the write did not fail")
    raw = ctx.now(OPENAPI)
    if _bare_lf(raw):
        problems.append(f"openapi: {_bare_lf(raw)} bare LF")
    base, now = json.loads(ctx.base(OPENAPI)), json.loads(raw)
    props = set(now["components"]["schemas"]["CookieTestOut"].get("properties", {}))
    if props != {"ok", "outcome", "error_message"}:
        problems.append(f"openapi: CookieTestOut properties {sorted(props)}")
    bs, ns = base["components"]["schemas"], now["components"]["schemas"]
    diff = {k for k in set(bs) | set(ns) if bs.get(k) != ns.get(k)}
    if diff - {"CookieTestOut", "CookieTestOutcome"}:
        problems.append(f"openapi: other schemas changed {sorted(diff)}")
    rest = [k for k in set(base) | set(now) if k != "components" and base.get(k) != now.get(k)]
    other = {k: v for k, v in base["components"].items() if k != "schemas"}
    if rest or other != {k: v for k, v in now["components"].items() if k != "schemas"}:
        problems.append(f"openapi: other parts changed {rest}")
    print(f"openapi: schemas changed {sorted(diff)}")
    return problems


def test_ids(ctx: Ctx) -> list[str]:
    ok = ctx.now(TEST_IDS) == ctx.base(TEST_IDS) + TEST_IDS_BLOCK
    print(f"test-ids: {'row 0 plus the block' if ok else 'DIFFERENT'}")
    return [] if ok else ["test-ids: test-ids.ts is not its row-0 bytes plus the two-line block"]


def licence(ctx: Ctx) -> list[str]:
    text = ctx.rtext("ycc-licences.txt")
    problems = []
    for pattern in (r"^\W*yt[-_]dlp 2026\.11\.23\W*$", r"^\W*yt[-_]dlp[-_]ejs 0\.8\.0\W*$"):
        if not re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            problems.append(f"licence: no title {pattern}")
    print(f"licence: {len(problems)} title(s) missing")
    return problems


# --- snapshot-paths, e2e-red, e2e-result
def _git_dirty(root: pathlib.Path) -> Callable[[str], bool]:
    return lambda p: bool(_git(root, "status", "--porcelain", "--", p).strip())


def snapshot_paths(
    ctx: Ctx, stage: str, out: pathlib.Path, dirty: Callable[[str], bool] | None = None
) -> list[str]:
    is_dirty = dirty or _git_dirty(ctx.root)
    code = ("packages/", "ui/", "mcp-server/", "tests/")
    paths = [
        p for p in SCOPE if (p.startswith(code) or p in (OPENAPI, LOCK, ROOT_PY)) and is_dirty(p)
    ]
    problems: list[str] = []
    if stage == "red":
        problems += [
            f"snapshot-paths: renderer {p} changed before Red"
            for p in paths
            if p in (COOKIE_RESULT, DLPAGE, SABR_PANEL)
        ]
    if not paths:
        problems.append("snapshot-paths: no path differs from HEAD")
    out.write_text("".join(p + "\n" for p in paths), encoding="utf-8")
    for p in paths:
        print(f"snapshot-paths {stage}: {p}")
    return problems


def _e2e_line(ctx: Ctx, name: str) -> re.Match[str] | None:
    lines = [x for x in _lines(ctx.rtext(name)) if x.startswith("e2e-remote:")]
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


def _run(ctx: Ctx, name: str) -> tuple[re.Match[str] | None, dict, list[dict]]:
    m = _e2e_line(ctx, name)
    if not m:
        return None, {}, []
    folder = pathlib.Path(m[4])
    summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    report = json.loads((folder / "host" / "report.json").read_text(encoding="utf-8"))
    return m, summary, _specs(report)


def e2e_red(ctx: Ctx) -> list[str]:
    m, summary, specs = _run(ctx, "ycc-row11b-e2e.txt")
    if not m:
        return ["e2e-red: no e2e-remote line"]
    problems: list[str] = []
    if m[1] != "new-failures" or m[2] != "40":
        problems.append(f"e2e-red: {m[1]} exit={m[2]}, want new-failures exit=40")
    new = summary.get("new", [])
    if any(
        not str(n.get("file", "")).replace("\\", "/").endswith("downloader-cookie-test.test.ts")
        for n in new
    ):
        problems.append("e2e-red: the new list holds another file")
    titles = [str(n.get("title", "")) for n in new]
    for t in RED_TITLES:
        if not any(x.endswith(t) for x in titles):
            problems.append(f"e2e-red: {t} is not in the new list")
        hits = [s for s in specs if s["title"] == t]
        msgs = [x for s in hits for x in s["messages"]]
        if (
            not hits
            or not msgs
            or any(
                "expect(" not in x or "Test timeout of" in x or "launch" in x.lower() for x in msgs
            )
        ):
            problems.append(f"e2e-red: {t} did not fail by an expect assertion")
    guard = [s for s in specs if s["title"] == E2E_GUARD]
    if not guard or any(s["status"] != "expected" for s in guard):
        problems.append("e2e-red: the guard did not pass")
    print(f"e2e-red: run {m[3]}; new {len(new)}; {len(problems)} problem(s)")
    return problems


def e2e_result(ctx: Ctx) -> list[str]:
    m, summary, specs = _run(ctx, "ycc-row16-e2e.txt")
    if not m:
        return ["e2e-result: no e2e-remote line"]
    problems: list[str] = []
    snap = json.loads((ctx.r / "ycc-snapshot.json").read_text(encoding="utf-8"))
    if m[2] != "0" or summary.get("exit") != 0 or summary.get("unexpected") != 0:
        problems.append(f"e2e-result: exit {m[2]}, unexpected {summary.get('unexpected')}")
    if summary.get("commit") != snap.get("commit"):
        problems.append("e2e-result: the run's commit is not the snapshot's")
    for t in (*RED_TITLES, E2E_GUARD):
        hits = [s for s in specs if s["title"] == t]
        if not hits or any(s["status"] != "expected" for s in hits):
            problems.append(f"e2e-result: {t} did not pass")
    gap = [
        s
        for s in specs
        if s["file"].endswith("downloader-advanced-gap.test.ts") and "AC-159" in s["title"]
    ]
    if not gap or any(s["status"] != "expected" for s in gap):
        problems.append("e2e-result: the AC-159 titles did not all pass")
    if sha(ctx.root / ADV_GAP) != ctx.pjson("baseline-scope.json")[ADV_GAP]:
        problems.append("e2e-result: downloader-advanced-gap.test.ts changed")
    print(f"e2e-result: run {m[3]}; {summary.get('tests')} tests; AC-159 {len(gap)}")
    return problems


# --- canon, register, status
def canon(ctx: Ctx, edits: dict | None = None) -> list[str]:
    ced = _load("ycc_canon_edit", "canon-edit.py")
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


def status(ctx: Ctx, stage: str) -> list[str]:
    want = {"ready": "ready_for_review", "approved": "approved"}[stage]
    proved = _word(ctx, "ycc-proof-verdict.txt") == "proved"
    base, now = _meus(ctx.base(MEU_STATUS)), _meus(ctx.now(MEU_STATUS))
    problems: list[str] = []
    for meu in ("MEU-169", "MEU-170", *(("MEU-168",) if proved else ())):
        if now[meu].get("status") != want:
            problems.append(f"status: {meu} is {now[meu].get('status')}, want {want}")
    if not proved and now["MEU-168"].get("status") != base["MEU-168"].get("status"):
        problems.append("status: MEU-168 changed though the proof is not proved")
    print(
        f"status {stage}: "
        + ", ".join(f"{m} {now[m].get('status')}" for m in ("MEU-168", "MEU-169", "MEU-170"))
    )
    return problems


def register(ctx: Ctx) -> list[str]:
    problems: list[str] = []
    issues = list(json.loads((ctx.r / "ycc-issue-resolve-set.json").read_text(encoding="utf-8")))
    proved = _word(ctx, "ycc-proof-verdict.txt") == "proved"
    if (SOLVER_ISSUE in issues) != proved:
        problems.append(
            f"register: {SOLVER_ISSUE} in the set is {SOLVER_ISSUE in issues}, proved {proved}"
        )
    base, now = _issues(ctx.base(REGISTER), "row 0"), _issues(ctx.now(REGISTER), "now")
    if set(base) != set(now):
        problems.append(
            f"register: ids added {sorted(set(now) - set(base))}, "
            f"removed {sorted(set(base) - set(now))}"
        )
    for key in sorted(set(base) & set(now)):
        if key not in issues and base[key] != now[key]:
            problems.append(f"register: {key} changed")
    for issue in issues:
        if issue not in now or issue not in base:
            problems.append(f"register: {issue} is missing")
            continue
        a, b = base[issue], now[issue]
        changed = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
        print(f"register: {issue} changed fields {sorted(changed)}; status {b.get('status')}")
        if changed - ISSUE_FIELDS:
            problems.append(f"register: {issue} also changed {sorted(changed - ISSUE_FIELDS)}")
        if b.get("status") != "resolved":
            problems.append(f"register: {issue} status is {b.get('status')!r}")
    g_base, g_now = ctx.base(GROUPING), ctx.now(GROUPING)
    if b"\r" in g_now:
        problems.append("register: the grouping file has a CR")
    old_lines, new_lines = g_base.split(b"\n"), g_now.split(b"\n")
    rows = [i for i, line in enumerate(old_lines) if line.startswith(b"| 104 |")]
    if len(rows) != 1 or len(old_lines) != len(new_lines):
        return [*problems, f"register: grouping row 104 at {rows}; {len(new_lines)} lines now"]
    old_row = old_lines[rows[0]]
    if old_row.count(GROUPING_OLD.encode()) != 1:
        problems.append("register: grouping row 104 did not read planning once at row 0")
    want = old_row.replace(GROUPING_OLD.encode(), GROUPING_NEW.encode())
    for i, (a, b) in enumerate(zip(old_lines, new_lines, strict=True)):
        if b != (want if i == rows[0] else a):
            problems.append(f"register: grouping line {i + 1} is {b[:90]!r}")
    return [*problems, *status(ctx, "ready")]


# --- no-deselect, metrics, commit-draft, next-prompt
def no_deselect(ctx: Ctx) -> list[str]:
    problems: list[str] = []
    gate = (ctx.plan / "session-gate.ps1").read_bytes().decode("utf-8")
    if "--deselect" in gate:
        problems.append("no-deselect: the gate has --deselect")
    if gate.count("Id = 'py-tests'") != 1:
        problems.append("no-deselect: the gate does not have one py-tests step")
    text = ctx.rtext("ycc-D6-py-tests.txt")
    tail = [x for x in _lines(text) if x.strip()][-3:]
    if not re.search(r"\d+ passed", "\n".join(tail)) or re.search(
        r"\d+ (failed|errors?)\b", "\n".join(tail)
    ):
        problems.append(f"no-deselect: the py-tests summary is {tail[-1:]}")
    if _exit(ctx.r / "ycc-D6-py-tests.txt.exit") != 0:
        problems.append("no-deselect: py-tests did not exit 0")
    print(f"no-deselect: {tail[-1:]}")
    return problems


def metrics(ctx: Ctx) -> list[str]:
    raw = ctx.now(METRICS)
    rows = [x for x in _lines(raw) if SLUG in x]
    problems = []
    if len(rows) != 1:
        problems.append(f"metrics: {len(rows)} line(s) name the slug")
    if _bare_lf(raw):
        problems.append(f"metrics: {_bare_lf(raw)} bare LF")
    print(f"metrics: {len(rows)} row(s)")
    return problems


def commit_draft(ctx: Ctx) -> list[str]:
    raw = (ctx.r / "ycc-commit-draft.txt").read_bytes()
    text = raw.decode("utf-8")
    lines = text.split("\n")
    problems = []
    if lines[0] != SUBJECT or len(lines) < 3 or lines[1] != "":
        problems.append("commit-draft: the subject or the empty second line is wrong")
    if b"\r" in raw:
        problems.append("commit-draft: a CR")
    if re.search(r"co-authored-by|generated with", text, re.IGNORECASE):
        problems.append("commit-draft: an attribution trailer")
    if HOME.search(text):
        problems.append("commit-draft: a home path")
    if EMAIL.search(text):
        problems.append("commit-draft: an email address")
    print(f"commit-draft: {len(lines)} line(s)")
    return problems


def next_prompt(ctx: Ctx, prompt: pathlib.Path = NEXT_PROMPT) -> list[str]:
    problems = []
    queue = ctx.r / "ycc-close-queue.txt"
    if not queue.is_file() or "meu_status.py next" not in ctx.rtext(queue.name):
        problems.append(
            "next-prompt: the queue receipt is missing or does not name meu_status.py next"
        )
    text = prompt.read_bytes().decode("utf-8") if prompt.is_file() else ""
    if not text.startswith("Session 104 done:"):
        problems.append("next-prompt: the prompt does not start 'Session 104 done:'")
    missing = [m for m in MECHANISMS if m not in text]
    if missing:
        problems.append(f"next-prompt: lacks {missing}")
    print(f"next-prompt: {len(text)} chars")
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
    path.write_text(json.dumps(data), encoding="utf-8")


def selftest() -> int:  # noqa: C901 - one case pair per subcommand
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

        # steps
        c = _ctx(tmp, "steps")
        task = (
            "x\n## Row steps\n\n| Step | Flags | Command | Receipt | Passes when |\n"
            "|---|---|---|---|---|\n"
            '| 1.1 | recorded; in `ui` | `PY PLAN/a.py --out R/b.json -t "A B"` '
            "| `ycc-a.txt` | x |\n"
            "\n### Next\n"
        )
        _put(c.plan, {"task.md": task})
        block = emit_steps(parse_steps(task))
        _put(c.plan, {"row-run.ps1": f"a\n# BEGIN STEPS\n{block}# END STEPS\nb\n"})
        case(
            "steps pass",
            lambda: steps_check(c) if "'A B'" in block and "'recorded,ui'" in block else ["emit"],
            True,
        )
        c2 = _ctx(tmp, "steps2")
        _put(c2.plan, {"task.md": task, "row-run.ps1": f"# BEGIN STEPS\n{block}x\n# END STEPS\n"})
        case("steps fail", lambda: steps_check(c2), False)

        # red-record, red-unchanged
        c = _ctx(tmp, "red")
        _put(c.root, {"t.py": "a\n"})
        case("red-record pass", lambda: red_record(c, "2", ["t.py"]), True)
        case("red-unchanged pass", lambda: red_unchanged(c), True)
        _put(c.root, {"t.py": "b\n"})
        case("red-unchanged fail", lambda: red_unchanged(c), False)
        case("red-record fail", lambda: red_record(c, "2", ["t.py"]), False)

        # pins-unchanged --row 4 and 14
        c = _ctx(tmp, "pins")
        files = {p: "x = 1\r\n" for p in ROW4}
        files[TEST_SERVICES] = "def test_sabr_a():\r\n    assert 1\r\n"
        files[YT_TEST] = "def test_sabr_b():\r\n    assert 1\r\n"
        _both(c, files)
        _dump(c.plan / "baseline-scope.json", {p: sha(c.root / p) for p in files})
        _dump(
            c.plan / "baseline-pins.json",
            {
                "files": {},
                "ast": {p: top_level_sources(files[p]) for p in (TEST_SERVICES, YT_TEST)},
                "kept": {},
            },
        )
        case("pins-unchanged 4 pass", lambda: pins_unchanged(c, "4"), True)
        case("pins-unchanged 14 pass", lambda: pins_unchanged(c, "14"), True)
        _put(c.root, {FETCH_DENO: "x = 2\r\n", YT_TEST: "def test_sabr_b():\r\n    assert 2\r\n"})
        case("pins-unchanged 4 fail", lambda: pins_unchanged(c, "4"), False)
        case("pins-unchanged 14 fail", lambda: pins_unchanged(c, "14"), False)

        # pins-moved --row 7
        def py_fixture(tag: str, good: bool) -> Ctx:
            c = _ctx(tmp, tag)
            base = {p: "import os\n\n\ndef keep():\n    return 1\n" for p in PY_PINNED}
            base[TEST_API] = (
                "from x import A\n\n\nclass Fake:\n    def __init__(self):\n        self.a = 1\n\n"
                "    def test_cookies(self):\n        return A(ok=True)\n\n\n"
                "def test_ac_15_7_cookie_test_envelope():\n"
                '    assert "HTTP_COOKIE" not in ok.text\n'
            )
            base[TEST_DOMAIN] = (
                'def test_ac_4_4_cookie_test_result_shape():\n    assert "cookies" not in f\n'
                '    assert ("ok", "error_message")\n'
            )
            base[YT_TEST] = (
                "def test_ac_6_13_test_cookies_never_raises_cookie_error():\n"
                '    assert "Netscape" not in m\n'
            )
            now = dict(base)
            now[TEST_API] = (
                "from x import A, B\n\n\nclass Fake:\n    def __init__(self):\n        self.a = 1\n"
                "        self.cookie_result = None\n\n"
                "    def test_cookies(self):\n        return A(ok=True, outcome=B.ok)\n\n\n"
                "def test_ac_15_7_cookie_test_envelope():\n"
                '    assert "HTTP_COOKIE" not in ok.text\n'
                '    assert x == {"outcome": "ok"}\n'
                '    assert "check_failed" and "Sign in to confirm"\n'
                '    assert y == "check_failed"\n'
            )
            now[TEST_DOMAIN] = (
                'def test_ac_4_4_cookie_test_result_shape():\n    assert "cookies" not in f\n'
                '    assert ("ok", "error_message", "outcome")\n'
            )
            now[YT_TEST] = (
                "def test_ac_6_13_test_cookies_never_raises_cookie_error():\n"
                '    assert "Netscape" not in m\n    assert CookieTestOutcome.unreadable\n'
                "    assert CookieTestOutcome.ok and f(outcome=None)\n\n\n"
                "def test_ac_169_4_x():\n    pass\n"
            )
            if not good:
                now[TEST_SERVICES] = "import os\n\n\ndef keep():\n    return 2\n"
            _put(c.root, now)
            _dump(
                c.plan / "baseline-pins.json",
                {"ast": {p: top_level_sources(base[p]) for p in PY_PINNED}},
            )
            return c

        c7, c7b = py_fixture("moved7", True), py_fixture("moved7b", False)
        case("pins-moved 7 pass", lambda: pins_moved(c7, "7"), True)
        case("pins-moved 7 fail", lambda: pins_moved(c7b, "7"), False)

        # pins-moved --row 11
        def ts_fixture(tag: str, good: bool) -> Ctx:
            c = _ctx(tmp, tag)
            sabr_base = (
                "import x\n\ndescribe('panel', () => {\n"
                "  it('AC-138.8 each snapshot gives its contract text', () => {\n"
                "    expect(a).toBe('A')\n"
                "    expect(b).toBe('B')\n  })\n\n"
                "  it('AC-138.8 the time is zero-padded local time', () => {\n"
                "    expect(c).toBe('C')\n  })\n})\n"
            )
            beh_base = (
                "const mock = { ok: true }\n\n"
                "it('AC-138.8 the SABR panel shows an Inactive and an Active check "
                "with their time', () => {\n"
                "  expect(a).toBe('A')\n  expect(b).toBe('B')\n})\n"
            )
            sabr_now = (
                sabr_base.replace("toBe('A')", f"toBe('A · {CLAUSE}')")
                .replace("toBe('B')", f"toBe('B · {CLAUSE}')")
                .replace("toBe('C')", f"toBe('C · {CLAUSE}')")
            )
            beh_now = (
                beh_base.replace("toBe('A')", f"toBe('A · {CLAUSE}')")
                .replace("toBe('B')", f"toBe('B · {CLAUSE}')")
                .replace("{ ok: true }", "{ ok: true, outcome: 'ok', error_message: null }")
            )
            beh_now += (
                "\nit('AC-169.9 each outcome shows its text with role status', () => {\n  x()\n})\n"
            )
            if not good:
                beh_now = beh_now.replace("const mock =", "const other = 1\nconst mock =")
            _put(c.copies, {SABR_TEST: sabr_base, BEHAVIOR_TEST: beh_base})
            _put(c.root, {SABR_TEST: sabr_now, BEHAVIOR_TEST: beh_now})
            return c

        c11, c11b = ts_fixture("moved11", True), ts_fixture("moved11b", False)
        case("pins-moved 11 pass", lambda: pins_moved(c11, "11"), True)
        case("pins-moved 11 fail", lambda: pins_moved(c11b, "11"), False)

        # scope-paths
        c = _ctx(tmp, "scope")
        _both(c, {p: "r\n" for p in READ_ONLY})
        _dump(c.plan / "baseline-scope.json", {p: sha(c.root / p) for p in READ_ONLY})
        _dump(c.plan / "baseline-dirty-hashes.json", {})
        _put(c.r, {"baseline-tags.txt": "v1\nv2\n"})
        ok_changed = [
            ENUMS,
            f"{PLAN_REL}/x.py",
            "docs/execution/plans/2026-11-26-app-auto-update/task.md",
        ]
        case("scope-paths pass", lambda: scope_paths(c, ok_changed, "v2\nv1\n"), True)
        case(
            "scope-paths fail",
            lambda: scope_paths(c, [*ok_changed, "ui/package.json"], "v1\nv2\nv3\n"),
            False,
        )

        # lock
        def lock_fixture(tag: str, good: bool) -> Ctx:
            c = _ctx(tmp, tag)
            root_py = '[project]\nname = "x"\n\n[tool.uv]\npackage = false\n\n[tool.ruff]\n'
            infra = b'dependencies = [\r\n    "yt-dlp",\r\n    "yt-dlp-ejs==0.8.0",\r\n]\r\n'
            lock_base = (
                'version = 1\n\n[options]\nexclude-newer = "x"\n\n'
                '[[package]]\nname = "avkit-infra"\ndependencies = [\n'
                '    { name = "yt-dlp" },\n]\n\n'
                '[[package]]\nname = "yt-dlp"\nversion = "2026.10.26"\n\n'
                '[[package]]\nname = "yt-dlp-ejs"\nversion = "0.8.0"\n'
            )
            lock_now = lock_base.replace(
                '{ name = "yt-dlp" }', '{ name = "yt-dlp", specifier = ">=2026.11.23" }'
            )
            lock_now = lock_now.replace("2026.10.26", "2026.11.23").replace(
                'exclude-newer = "x"\n',
                'exclude-newer = "x"\nexclude-newer-package = { yt-dlp = false }\n',
            )
            _put(c.copies, {ROOT_PY: root_py, INFRA_PY: infra, LOCK: lock_base})
            now_py = root_py.replace("package = false\n", f"package = false\n{HOLD_LINE}\n")
            _put(
                c.root,
                {ROOT_PY: now_py, INFRA_PY: infra.replace(b'"yt-dlp",', b'"yt-dlp>=2026.11.23",')},
            )
            _put(c.root, {LOCK: lock_now if good else lock_now.replace('"0.8.0"', '"0.9.0"')})
            return c

        cl, clb = lock_fixture("lock", True), lock_fixture("lockb", False)
        case("lock pass", lambda: lock(cl), True)
        case("lock fail", lambda: lock(clb), False)
        case(
            "lock --installed pass",
            lambda: lock(cl, True, {"yt-dlp": NEW_YTDLP, "yt-dlp-ejs": EJS}.__getitem__),
            True,
        )
        case(
            "lock --installed fail",
            lambda: lock(cl, True, {"yt-dlp": OLD_YTDLP, "yt-dlp-ejs": EJS}.__getitem__),
            False,
        )

        # proof-recorded, proof-pair
        def proof(
            c: Ctx, which: str, verdict: str, code: int, version: str, variant: str = "default"
        ) -> None:
            data = {k: "x" for k in pe.FIELDS}
            data.update({"yt-dlp": version, "verdict": verdict, "variant": variant, "formats": 3})
            _dump(c.r / f"ycc-proof-{which}.json", data)
            lines = [f"{k}={data[k]}" for k in pe.FIELDS] + (
                ["INCOMPLETE VERIFICATION"] if verdict == "blocked" else []
            )
            _put(
                c.r,
                {
                    f"ycc-proof-{which}.txt": "\n".join(lines) + "\n",
                    f"ycc-proof-{which}.txt.exit": f"{code}\n",
                },
            )

        c = _ctx(tmp, "proof")
        proof(c, "before", "challenge-errors", 0, OLD_YTDLP)
        proof(c, "after", "clean", 0, NEW_YTDLP)
        case("proof-recorded pass", lambda: proof_recorded(c, "before"), True)
        case(
            "proof-pair classify",
            lambda: (
                []
                if not proof_pair(c, "--classify", c.r / "p.txt") and _word(c, "p.txt") == "proved"
                else ["word"]
            ),
            True,
        )
        case(
            "proof-pair proved pass", lambda: proof_pair(c, "--require-proved", c.r / "v.txt"), True
        )
        cb = _ctx(tmp, "proofb")
        proof(cb, "before", "blocked", 0, OLD_YTDLP)
        proof(cb, "after", "challenge-errors", 1, NEW_YTDLP)
        case("proof-recorded fail", lambda: proof_recorded(cb, "before"), False)
        case(
            "proof-pair proved fail",
            lambda: proof_pair(cb, "--require-proved", cb.r / "v.txt"),
            False,
        )
        proof(cb, "before", "challenge-errors", 0, OLD_YTDLP)
        case(
            "proof-pair fallback",
            lambda: (
                []
                if not proof_pair(cb, "--classify", cb.r / "p.txt")
                and _word(cb, "p.txt") == "fallback-applies"
                else ["word"]
            ),
            True,
        )

        # variant-gate (not-needed)
        c = _ctx(tmp, "variant")
        _both(c, {LOCK_TEST: f"def {GUARD}():\n    pass\n", ADAPTER: "x = 1\n"})
        _put(c.r, {"ycc-proof-pair.txt": "proved\n"})
        red_record(c, "2", [LOCK_TEST])
        case("variant-gate red pass", lambda: variant_gate(c, "red"), True)
        case("variant-gate green pass", lambda: variant_gate(c, "green"), True)
        _put(c.root, {LOCK_TEST: "def other():\n    pass\n", ADAPTER: "player_js_variant = 1\n"})
        case("variant-gate red fail", lambda: variant_gate(c, "red"), False)
        case("variant-gate green fail", lambda: variant_gate(c, "green"), False)

        # type-only
        def type_fixture(tag: str, good: bool) -> Ctx:
            c = _ctx(tmp, tag)
            enums = "from enum import StrEnum\n\n\nclass A(StrEnum):\n    x = 'x'\n"
            dom = (
                "from x import A\n\n\nclass CookieTestResult:\n    ok: bool\n"
                "    error_message: str | None\n\n"
                "    def __post_init__(self):\n        require(self.ok)\n"
            )
            _both(c, {ENUMS: enums, DOMAIN: dom, SERVICE: "s = 1\n"})
            enums_now = enums + (
                "\n\nclass CookieTestOutcome(StrEnum):\n    ok = 'ok'\n"
                "    unreadable = 'unreadable'\n    check_failed = 'check_failed'\n"
            )
            dom_now = dom.replace("from x import A", "from x import A, CookieTestOutcome").replace(
                "str | None\n", "str | None\n    outcome: CookieTestOutcome | None = None\n"
            )
            _put(c.root, {ENUMS: enums_now, DOMAIN: dom_now})
            if not good:
                _put(c.root, {SERVICE: "s = 2\n"})
            return c

        case("type-only pass", lambda: type_only(type_fixture("type", True)), True)
        case("type-only fail", lambda: type_only(type_fixture("typeb", False)), False)

        # kept, openapi
        def api_fixture(tag: str, good: bool) -> Ctx:
            c = _ctx(tmp, tag)
            srcs = {
                ADAPTER: (
                    "SABR_PHRASES = 1\nSABR_EXTRACTOR_ARGS = 2\n\n\ndef sabr_phrase():\n"
                    "    pass\n\n\nclass YouTubeAdapter:\n    def check_sabr_status(self):\n"
                    "        pass\n"
                ),
                SERVICE: (
                    "class DownloadService:\n    def check_sabr(self):\n        pass\n\n"
                    "    def force_sabr(self):\n        pass\n\n    def clear_sabr(self):\n"
                    "        pass\n"
                ),
                ROUTES: (
                    "def check_sabr():\n    pass\n\n\ndef force_sabr():\n    pass\n\n\n"
                    "def clear_sabr():\n    pass\n"
                ),
            }
            spec = {
                "openapi": "3",
                "paths": {"/sabr": {"get": 1}},
                "components": {
                    "schemas": {
                        "SABRStatusOut": {"a": 1},
                        "CookieTestOut": {"properties": {"ok": 1}},
                    }
                },
            }
            raw = json.dumps(spec, indent=2).replace("\n", "\r\n").encode()
            _both(c, {**srcs, OPENAPI: raw})
            _dump(
                c.plan / "baseline-pins.json",
                {"kept": {p: member_sources(srcs[p], KEPT[p]) for p in KEPT}},
            )
            spec["components"]["schemas"]["CookieTestOut"] = {
                "properties": {"ok": 1, "outcome": 2, "error_message": 3}
            }
            spec["components"]["schemas"]["CookieTestOutcome"] = {"enum": ["ok"]}
            if not good:
                spec["paths"]["/sabr"] = {"get": 2}
            _put(c.root, {OPENAPI: json.dumps(spec, indent=2).replace("\n", "\r\n").encode()})
            if not good:
                _put(
                    c.root,
                    {
                        ROUTES: srcs[ROUTES].replace(
                            "def clear_sabr():\n    pass", "def clear_sabr():\n    return 1"
                        )
                    },
                )
            _put(c.r, {"ycc-row9-drift.txt.exit": "1\n"})
            return c

        ca, cab = api_fixture("api", True), api_fixture("apib", False)
        case("kept pass", lambda: kept(ca), True)
        case("kept fail", lambda: kept(cab), False)
        case("openapi pass", lambda: openapi(ca), True)
        case("openapi fail", lambda: openapi(cab), False)

        # test-ids, licence
        c = _ctx(tmp, "ids")
        _put(c.copies, {TEST_IDS: b"export const A = 'a'\r\n"})
        _put(c.root, {TEST_IDS: b"export const A = 'a'\r\n" + TEST_IDS_BLOCK})
        _put(c.r, {"ycc-licences.txt": "yt-dlp 2026.11.23\n-----\nyt-dlp-ejs 0.8.0\n"})
        case("test-ids pass", lambda: test_ids(c), True)
        case("licence pass", lambda: licence(c), True)
        _put(c.root, {TEST_IDS: b"export const A = 'a'\n" + TEST_IDS_BLOCK})
        _put(c.r, {"ycc-licences.txt": "yt-dlp 2026.10.26\nyt-dlp-ejs 0.8.0\n"})
        case("test-ids fail", lambda: test_ids(c), False)
        case("licence fail", lambda: licence(c), False)

        # snapshot-paths
        c = _ctx(tmp, "snap")
        case(
            "snapshot-paths pass",
            lambda: snapshot_paths(c, "red", c.r / "s.txt", {ENUMS, LOCK}.__contains__),
            True,
        )
        case(
            "snapshot-paths fail",
            lambda: snapshot_paths(c, "red", c.r / "s.txt", {ENUMS, DLPAGE}.__contains__),
            False,
        )

        # e2e-red, e2e-result
        def e2e_fixture(tag: str, red: bool, good: bool) -> Ctx:
            c = _ctx(tmp, tag)
            folder = c.r / "run"
            fail = {
                "status": "unexpected",
                "results": [
                    {
                        "status": "failed",
                        "error": {"message": "Error: \x1b[2mexpect(\x1b[22mlocator).toHaveText"},
                    }
                ],
            }
            passed = {"status": "expected", "results": [{"status": "passed"}]}
            msg = fail if red else passed
            if not good:
                msg = {
                    "status": "unexpected",
                    "results": [
                        {
                            "status": "failed",
                            "error": {"message": "Test timeout of 30000ms exceeded"},
                        }
                    ],
                }
            specs = [
                {"title": t, "file": "downloader-cookie-test.test.ts", "tests": [msg]}
                for t in RED_TITLES
            ]
            specs.append(
                {"title": E2E_GUARD, "file": "downloader-cookie-test.test.ts", "tests": [passed]}
            )
            specs.append(
                {
                    "title": "AC-159.1 gap",
                    "file": "downloader-advanced-gap.test.ts",
                    "tests": [passed],
                }
            )
            _dump(
                folder / "host" / "report.json",
                {"suites": [{"file": "x", "suites": [{"specs": specs}]}]},
            )
            new = (
                [
                    {"file": "tests/e2e/downloader-cookie-test.test.ts", "title": t}
                    for t in RED_TITLES
                ]
                if red
                else []
            )
            _dump(
                folder / "summary.json",
                {
                    "new": new,
                    "exit": 40 if red else 0,
                    "unexpected": 4 if red else 0,
                    "commit": "abc",
                    "tests": 6,
                },
            )
            _dump(c.r / "ycc-snapshot.json", {"commit": "abc"})
            reason, code = ("new-failures", 40) if red else ("passed", 0)
            line = f"e2e-remote: {reason} exit={code} run=r1 receipts={folder.as_posix()}\n"
            _put(c.r, {"ycc-row11b-e2e.txt": "x\n" + line, "ycc-row16-e2e.txt": "x\n" + line})
            _both(c, {ADV_GAP: "t\n"})
            _dump(c.plan / "baseline-scope.json", {ADV_GAP: sha(c.root / ADV_GAP)})
            return c

        case("e2e-red pass", lambda: e2e_red(e2e_fixture("e2er", True, True)), True)
        case("e2e-red fail", lambda: e2e_red(e2e_fixture("e2erb", True, False)), False)
        case("e2e-result pass", lambda: e2e_result(e2e_fixture("e2eg", False, True)), True)
        case("e2e-result fail", lambda: e2e_result(e2e_fixture("e2egb", False, False)), False)

        # canon
        c = _ctx(tmp, "canon")
        edits = {"docs/a.md": [("old line\n", "new line\n")]}
        _both(c, {"docs/a.md": b"x\r\nold line\r\ny\r\n"})
        _put(c.r, {"canon-before/docs/a.md": b"x\r\nold line\r\ny\r\n"})
        case("canon fail", lambda: canon(c, edits), False)
        _put(c.root, {"docs/a.md": b"x\r\nnew line\r\ny\r\n"})
        case("canon pass", lambda: canon(c, edits), True)

        # register, status
        def reg_fixture(tag: str, good: bool) -> Ctx:
            c = _ctx(tmp, tag)
            issues = {
                "issues": [
                    {"id": i, "status": "open", "title": "t"}
                    for i in (
                        "A",
                        "DOWNLOADER-COOKIE-TEST-SILENT",
                        "SABR-CHECK-IGNORES-COOKIES",
                        SOLVER_ISSUE,
                    )
                ]
            }
            meus = [
                {"row_key": m, "id": m, "status": "planned"}
                for m in ("MEU-168", "MEU-169", "MEU-170")
            ]
            grouping = (
                "# g\n| 104 | `x` | MEU-168 | P1 | planning | `p/` |\n| 105 | y | planning |\n"
            )
            _both(
                c,
                {
                    REGISTER: yaml.safe_dump(issues),
                    MEU_STATUS: yaml.safe_dump(meus),
                    GROUPING: grouping,
                },
            )
            for i in issues["issues"][1:3]:
                i["status"] = "resolved"
                i["verification"] = {"result": "ok"}
            if not good:
                issues["issues"][0]["title"] = "changed"
            for m in meus[1:]:
                m["status"] = "ready_for_review"
            _put(c.root, {REGISTER: yaml.safe_dump(issues), MEU_STATUS: yaml.safe_dump(meus)})
            _put(
                c.root, {GROUPING: grouping.replace("P1 | planning", "P1 | executed (Session 104)")}
            )
            _dump(
                c.r / "ycc-issue-resolve-set.json",
                {"DOWNLOADER-COOKIE-TEST-SILENT": {}, "SABR-CHECK-IGNORES-COOKIES": {}},
            )
            _put(c.r, {"ycc-proof-verdict.txt": "not-proved\n"})
            return c

        cr, crb = reg_fixture("reg", True), reg_fixture("regb", False)
        case("register pass", lambda: register(cr), True)
        case("register fail", lambda: register(crb), False)
        case("status pass", lambda: status(cr, "ready"), True)
        case("status fail", lambda: status(cr, "approved"), False)

        # no-deselect, metrics, commit-draft, next-prompt
        c = _ctx(tmp, "close")
        _put(c.plan, {"session-gate.ps1": "@{ Id = 'py-tests'; Argv = @('pytest') }\n"})
        _put(
            c.r,
            {"ycc-D6-py-tests.txt": "....\n2105 passed in 9s\n", "ycc-D6-py-tests.txt.exit": "0\n"},
        )
        _put(c.root, {METRICS: f"| a |\r\n| {SLUG} |\r\n"})
        _put(c.r, {"ycc-commit-draft.txt": f"{SUBJECT}\n\nBody line.\n"})
        _put(c.r, {"ycc-close-queue.txt": "uv run python tools/meu_status.py next\n"})
        _put(c.r, {"prompt.md": "Session 104 done: " + " ".join(MECHANISMS) + "\n"})
        case("no-deselect pass", lambda: no_deselect(c), True)
        case("metrics pass", lambda: metrics(c), True)
        case("commit-draft pass", lambda: commit_draft(c), True)
        case("next-prompt pass", lambda: next_prompt(c, c.r / "prompt.md"), True)
        _put(c.r, {"ycc-D6-py-tests.txt": "1 failed, 2104 passed in 9s\n"})
        _put(c.root, {METRICS: f"| a |\n| {SLUG} |\r\n"})
        _put(c.r, {"ycc-commit-draft.txt": f"{SUBJECT}\n\nCo-Authored-By: x <a@b.io>\n"})
        _put(c.r, {"prompt.md": "Session 104 done: YTDLP_LOCK\n"})
        case("no-deselect fail", lambda: no_deselect(c), False)
        case("metrics fail", lambda: metrics(c), False)
        case("commit-draft fail", lambda: commit_draft(c), False)
        case("next-prompt fail", lambda: next_prompt(c, c.r / "prompt.md"), False)

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
    simple = {
        "red-unchanged": red_unchanged,
        "scope-paths": scope_paths,
        "type-only": type_only,
        "kept": kept,
        "openapi": openapi,
        "test-ids": test_ids,
        "licence": licence,
        "e2e-red": e2e_red,
        "e2e-result": e2e_result,
        "canon": canon,
        "register": register,
        "no-deselect": no_deselect,
        "metrics": metrics,
        "commit-draft": commit_draft,
        "next-prompt": next_prompt,
    }
    try:
        if cmd == "steps" and rest == ["--emit"]:
            sys.stdout.write(
                emit_steps(parse_steps((HERE / "task.md").read_bytes().decode("utf-8")))
            )
            return 0
        if cmd == "steps" and not rest:
            problems = steps_check(ctx)
        elif cmd in simple and not rest:
            problems = simple[cmd](ctx)
        elif cmd == "red-record" and len(rest) >= 3 and rest[0] == "--row":
            problems = red_record(ctx, rest[1], rest[2:])
        elif cmd == "pins-unchanged" and rest in ([], ["--row", "4"], ["--row", "14"]):
            problems = pins_unchanged(ctx, rest[1] if rest else None)
        elif cmd == "pins-moved" and len(rest) == 2 and rest[0] == "--row":
            problems = pins_moved(ctx, rest[1])
        elif cmd == "lock" and rest in ([], ["--installed"]):
            problems = lock(ctx, bool(rest))
        elif cmd == "proof-recorded" and len(rest) == 1:
            problems = proof_recorded(ctx, rest[0])
        elif cmd == "proof-pair" and len(rest) == 3 and rest[1] == "--out":
            problems = proof_pair(ctx, rest[0], pathlib.Path(rest[2]))
        elif cmd == "variant-gate" and rest in (["--stage", "red"], ["--stage", "green"]):
            problems = variant_gate(ctx, rest[1])
        elif cmd == "snapshot-paths" and len(rest) == 4 and rest[1] in ("red", "green"):
            problems = snapshot_paths(ctx, _opt(rest, "--stage"), pathlib.Path(_opt(rest, "--out")))
        elif cmd == "status" and rest in (["--stage", "ready"], ["--stage", "approved"]):
            problems = status(ctx, rest[1])
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
