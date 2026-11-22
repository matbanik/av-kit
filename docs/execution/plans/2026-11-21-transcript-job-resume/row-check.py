"""Session 101 row checks (task rows 1 to 7 and the gate; implementation-plan.md §Verification).

Written in the shape of Session 99's (2026-11-20-help-quick-start/row-check.py). Subcommands
(each exits 0 when it finds no problem, 1 when it does, 2 on a usage error):

* ``red-record --row N FILE ...``: writes the files' SHA-256 under the row in
  ``tjr-red-hashes.json`` and copies their bytes to ``tjr-red-copies/row<N>/``. A row is a string
  (``3a``). A row already recorded with other hashes is refused (a Red file never changes after
  its row); the rows keep the order they were recorded in.
* ``red-unchanged``: every file in ``tjr-red-hashes.json`` still has the hash of the latest row
  that recorded it (row 3a records ``test_services.py`` again after row 1).
* ``pins-unchanged``: every ``baseline-pins.json`` file hash, and every ``test_ac_11_`` and
  ``test_ac_116_`` top-level function of ``test_services.py`` except AC-116.5 and AC-116.9,
  parsed now with ``ast``, equal to row 0's source.
* ``red-reason RECEIPT --id ID [--id ID ...] --needle TEXT``: in the Playwright receipt each id
  has a failing block, and every block of that id fails by an assertion first, holds no launch,
  seed or timeout line, and has ``TEXT`` in its message (the lines before the first code frame
  line; the code frame quotes the test source, so it never counts).
* ``e2e-count RECEIPT N [--plain RECEIPT ...]``: the first receipt has ``N`` lines matching
  ``^ +ok +[0-9]+ .*AC-163\\.`` and an ``N passed`` line; each ``--plain`` receipt has a pass
  count; no receipt has a ``failed``, ``flaky`` or ``unhandled rejection:`` line.
* ``index-row``: AC-163.9. The plan's ``transcript:resume_job`` row occurs exactly once, on the
  line after the ``transcript:resume`` row; ``gui-actions-index.md`` has no bare LF; without that
  row the file equals its row-0 copy.
* ``register``: ``known-issues.yaml`` now and its row-0 copy, parsed with ``yaml.safe_load`` and
  keyed by issue id: the same ids, every other issue equal, and
  ``TRANSCRIPT-PAUSED-JOB-NO-RESUME-AFTER-RESTART`` resolved and different only in ``status``,
  ``verification`` and ``resolution_path``. In the grouping file only §6 row 101 changed, from
  ``queued`` to ``executed (Session 101)``.
* ``named-edits``: ``DEFAULTS_TEST_EDITS`` by top-level ``ast`` node against
  ``baseline-pins.json``. In ``test_services.py`` the new nodes are exactly ``MEU_116_PACING``
  (just before ``_four_hundred``), the renamed AC-116.9 (at the old name's place) and the two
  ``test_ac_163_6_`` tests (just after ``test_ac_11_3_resume_only_from_paused``), the only
  removed node is the old AC-116.9 name, and the only changed nodes are ``_four_hundred`` and
  AC-116.5. In ``test_transcript_metadata.py`` only AC-122.12 changed. Each planned node's
  source equals the form below, and row 0's sources equal the old forms below.
* ``defaults-values``: ``TRANSCRIPT_DEFAULTS``. By bytes against the row-0 copies,
  ``settings.py`` and ``settings.ts`` differ only on their six transcript lines, each from the
  old line to the new one exactly, and both have no bare LF.
* ``defaults-canon``: ``DEFAULTS_CANON``. The same check for the six 06 rows and the 03 Rate
  cap row.
* ``--selftest``: every subcommand on fixtures in a temporary folder.

The Playwright block grammar is red-check.py's, loaded by path. ``top_level_sources`` is the one
function row 0 used to write ``baseline-pins.json`` (baseline.ps1 imports it).
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
RECEIPTS = pathlib.Path("C:/Temp/av-kit/2026-11-21-transcript-job-resume")
COPIES = RECEIPTS / "baseline-copies"
PINS = HERE / "baseline-pins.json"
RED_STORE = "tjr-red-hashes.json"
RED_COPIES = "tjr-red-copies"

SERVICES = "tests/unit/test_services.py"
METADATA = "tests/unit/test_transcript_metadata.py"
SETTINGS_PY = "packages/core/src/avkit_core/services/settings.py"
SETTINGS_TS = "mcp-server/src/toolsets/settings.ts"
GUI = "docs/build-plan/06-gui.md"
SERVICE_LAYER = "docs/build-plan/03-service-layer.md"
INDEX = "docs/build-plan/gui-actions-index.md"
REGISTER = ".agent/context/known-issues.yaml"
GROUPING = ".agent/context/grouping/2026-11-21-transcript-job-resume-session-grouping.md"
ISSUE = "TRANSCRIPT-PAUSED-JOB-NO-RESUME-AFTER-RESTART"
ISSUE_FIELDS = {"status", "verification", "resolution_path"}

OK_LINE = re.compile(r"^ +ok +[0-9]+ .*AC-163\.")
PASSED = re.compile(r"^\s*(\d+) passed\b")
E2E_BAD = re.compile(r"^\s*\d+ (?:failed|flaky)\b|unhandled rejection:", re.IGNORECASE)

# --- the plan's exact texts
#: TRANSCRIPT_DEFAULTS: (key, old, new).
DEFAULTS = (
    ("requests_per_hour", 300, 20),
    ("delay_between_requests", 6, 120),
    ("max_retries", 3, 1),
    ("retry_delay", 30, 7),
    ("batch_size", 50, 5),
    ("pause_between_batches", 300, 500),
)


def _py_line(key: str, value: int) -> str:
    return f'    ("transcript", "{key}"): SettingSpec("number", {value}, min_number=0),'


def _ts_line(key: str, value: int) -> str:
    return f'      {key}: {{ type: "number", default: {value} }},'


LINK = "[Transcript §3](../../_inspiration/_transcript_pseudo_logic.md)"


def _gui_row(key: str, value: int, old: int | None) -> str:
    source = LINK if old is None else f"Mat 2026-11-21 (D-1355); was {old} per {LINK}"
    return f"| `transcript.{key}` | `number` | `{value}` | {source} |"


RATE_CAP_OLD = (
    "| Rate cap | `transcript.requests_per_hour` is enforced as a rolling cap over real "
    "requests. Default behaviour doesn't change: 6 s apart with a 300 s pause after 50 is "
    "already about 300 an hour. | Local Canon: triage D-220 |"
)
RATE_CAP_NEW = (
    "| Rate cap | `transcript.requests_per_hour` is enforced as a rolling cap over real "
    "requests. The defaults do not reach it: 120 s apart with a 500 s pause after each 5 "
    "requests, before the next, is at most 18 starts in any hour, under the cap of 20, and "
    "`max_retries` 1 makes no retry (Mat 2026-11-21, D-1355). Until Session 101 the defaults "
    "were 6 s apart with a 300 s pause after 50, about 300 an hour. | Local Canon: triage "
    "D-220; D-1355 |"
)

#: path -> [(old line, new line)], each without its line ending.
VALUE_EDITS = {
    SETTINGS_PY: [(_py_line(k, o), _py_line(k, n)) for k, o, n in DEFAULTS],
    SETTINGS_TS: [(_ts_line(k, o), _ts_line(k, n)) for k, o, n in DEFAULTS],
}
CANON_EDITS = {
    GUI: [(_gui_row(k, o, None), _gui_row(k, n, o)) for k, o, n in DEFAULTS],
    SERVICE_LAYER: [(RATE_CAP_OLD, RATE_CAP_NEW)],
}

RESUME_ROW = (
    "| `transcript:resume` | Resume | yes | `POST /transcripts/resume` | specified | 04 / 06 |"
)
INDEX_ROW = (
    "| `transcript:resume_job` | Card menu Resume (first Paused job) | no | "
    "`POST /transcripts/resume` | specified | 10 / 06 |"
)

PACING = "MEU_116_PACING"
FOUR = "_four_hundred"
AC_11_3 = "test_ac_11_3_resume_only_from_paused"
AC_116_5 = "test_ac_116_5_default_cap_delays_nothing_without_retries"
AC_116_9_OLD = "test_ac_116_9_a_retry_makes_the_default_cap_wait"
AC_116_9 = "test_ac_116_9_a_retry_makes_a_300_an_hour_cap_wait"
AC_163_6 = ("test_ac_163_6_refused_while_processing", "test_ac_163_6_idle_resume_done")
AC_122_12 = "test_ac_122_12_no_extra_request_per_video"

FOUR_OLD = """def _four_hundred(tmp_path: Path, *, retries: int):
    from avkit_core.domain.enums import TranscriptStatus

    clock = FakeClock()
    service, _settings, yt, uow, _fs, captions, _sleeps = _transcript_stack(tmp_path, clock=clock)
    _set_ids(yt, [f"v{index}" for index in range(400)])
    captions.retryable_left = retries
    job = service.add_channel("https://youtube.com/@four-hundred")
    service.start_processing()
    _join(service, timeout=120)
    assert uow.transcripts.get_job(job.id).status is TranscriptStatus.Done
    return captions, clock"""
FOUR_NEW = """\
def _four_hundred(tmp_path: Path, *, retries: int, pacing: dict[str, int] | None = None):
    from avkit_core.domain.enums import TranscriptStatus

    clock = FakeClock()
    service, settings, yt, uow, _fs, captions, _sleeps = _transcript_stack(tmp_path, clock=clock)
    for key, value in (pacing or {}).items():
        settings.set("transcript", key, value)
    _set_ids(yt, [f"v{index}" for index in range(400)])
    captions.retryable_left = retries
    job = service.add_channel("https://youtube.com/@four-hundred")
    service.start_processing()
    _join(service, timeout=120)
    assert uow.transcripts.get_job(job.id).status is TranscriptStatus.Done
    return captions, clock"""
PACING_NEW = """MEU_116_PACING = {
    "requests_per_hour": 300,
    "delay_between_requests": 6,
    "max_retries": 3,
    "retry_delay": 30,
    "batch_size": 50,
    "pause_between_batches": 300,
}"""
AC_116_5_OLD = """\
def test_ac_116_5_default_cap_delays_nothing_without_retries(tmp_path: Path) -> None:
    captions, clock = _four_hundred(tmp_path, retries=0)
    assert len(captions.fetch_calls) == 400
    assert set(clock.sleeps) <= {0.0, 6.0, 300.0}, sorted(set(clock.sleeps))"""
AC_116_5_NEW = AC_116_5_OLD.replace("{0.0, 6.0, 300.0}", "{0.0, 120.0, 500.0}")
AC_116_9_OLD_SRC = """def test_ac_116_9_a_retry_makes_the_default_cap_wait(tmp_path: Path) -> None:
    _require_clock()
    captions, _clock = _four_hundred(tmp_path, retries=1)
    starts = captions.starts
    assert len(starts) == 401
    assert starts[300] == pytest.approx(3600.0)
    busiest = max(sum(1 for start in starts if end - 3600 < start <= end) for end in starts)
    assert busiest <= 300"""
AC_116_9_NEW = AC_116_9_OLD_SRC.replace(AC_116_9_OLD, AC_116_9).replace(
    "retries=1)", "retries=1, pacing=MEU_116_PACING)"
)
AC_122_12_OLD = """@pytest.mark.parametrize("count", [2, 50])
def test_ac_122_12_no_extra_request_per_video(tmp_path: Path, count: int) -> None:
    _require_listing()
    ids = [f"v{index}" for index in range(count)]
    service, _settings, yt, uow, _fs, captions, _sleeps = _listed_stack(
        tmp_path, ids, {video_id: f"Title {video_id}" for video_id in ids}, "Real Channel"
    )
    job = service.add_channel(URL)
    assert (yt.extract_calls, yt.ids_calls, yt.last_options) == (1, 1, None)
    _process(service, timeout=20.0)
    assert uow.transcripts.get_job(job.id).status is TranscriptStatus.Done
    assert len(captions.fetch_calls) == count
    assert (yt.extract_calls, yt.ids_calls, yt.last_options) == (1, 1, None)"""
AC_122_12_NEW = AC_122_12_OLD.replace("service, _settings, yt,", "service, settings, yt,").replace(
    '"Real Channel"\n    )\n',
    '"Real Channel"\n    )\n    settings.set("transcript", "requests_per_hour", 0)\n',
)
#: name -> (row-0 source, or None for a new node; planned source).
SERVICES_FORMS: dict[str, tuple[str | None, str]] = {
    PACING: (None, PACING_NEW),
    FOUR: (FOUR_OLD, FOUR_NEW),
    AC_116_5: (AC_116_5_OLD, AC_116_5_NEW),
    AC_116_9: (None, AC_116_9_NEW),
}
METADATA_FORMS: dict[str, tuple[str | None, str]] = {AC_122_12: (AC_122_12_OLD, AC_122_12_NEW)}


def _load_red_check():
    spec = importlib.util.spec_from_file_location("tjr_red_check", HERE / "red-check.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["tjr_red_check"] = module
    spec.loader.exec_module(module)
    return module


rc = _load_red_check()


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


def _pinned_test(name: str) -> bool:
    return name.startswith(("test_ac_11_", "test_ac_116_")) and not name.startswith(
        ("test_ac_116_5_", "test_ac_116_9_")
    )


def pins_unchanged(root: pathlib.Path, pins: pathlib.Path) -> list[str]:
    data = json.loads(pins.read_text(encoding="utf-8"))
    problems: list[str] = []
    for name, want in sorted(data["files"].items()):
        p = root / name
        got = sha(p) if p.is_file() else "absent"
        print(f"pins-unchanged: {name} {'ok' if got == want else 'CHANGED'}")
        if got != want:
            problems.append(f"pins-unchanged: {name} is {got[:16]}, not {want[:16]}")
    base = data["ast"][SERVICES]
    now = top_level_sources((root / SERVICES).read_bytes().decode("utf-8"))
    checked = [k for k in base if _pinned_test(k)]
    for key in checked:
        if now.get(key) != base[key]:
            state = "missing" if key not in now else "changed"
            problems.append(f"pins-unchanged: {SERVICES}::{key} {state}")
    print(f"pins-unchanged: {len(data['files'])} files, {len(checked)} AC-11/AC-116 sources")
    if not data["files"] or not checked:
        problems.append("pins-unchanged: no pin file or no AC-11/AC-116 source recorded")
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
            print(f"e2e-count {path.name}: {ok} AC-163 ok lines, passed {passes}, want {n}")
            if ok != n:
                problems.append(f"e2e-count: {path.name}: {ok} AC-163 ok lines, not {n}")
            if passes != [n]:
                problems.append(f"e2e-count: {path.name}: passed {passes}, not [{n}]")
        else:
            print(f"e2e-count {path.name}: passed {passes}")
            if len(passes) != 1 or passes[0] < 1:
                problems.append(f"e2e-count: {path.name}: no single pass count ({passes})")
    return problems


# --- line edits: defaults-values, defaults-canon, index-row
def _bare_lf(raw: bytes) -> int:
    return raw.count(b"\n") - raw.count(b"\r\n")


def line_edits(
    name: str, base: bytes, now: bytes, edits: list[tuple[str, str]], label: str
) -> list[str]:
    """``now`` equals ``base`` except that each old line (found once) is the new line."""
    problems: list[str] = []
    if _bare_lf(base) or _bare_lf(now):
        problems.append(f"{label}: {name}: bare LF (row 0 {_bare_lf(base)}, now {_bare_lf(now)})")
    old_lines = base.split(b"\r\n")
    new_lines = now.split(b"\r\n")
    if len(old_lines) != len(new_lines):
        return [
            *problems,
            f"{label}: {name}: {len(old_lines)} lines at row 0, {len(new_lines)} now",
        ]
    planned: dict[int, bytes] = {}
    for old, new in edits:
        hits = [i for i, line in enumerate(old_lines) if line == old.encode("utf-8")]
        if len(hits) != 1:
            problems.append(f"{label}: {name}: old line found {len(hits)} time(s): {old[:70]!r}")
            continue
        planned[hits[0]] = new.encode("utf-8")
    for i, (a, b) in enumerate(zip(old_lines, new_lines, strict=True)):
        want = planned.get(i, a)
        if b != want:
            kind = "planned line" if i in planned else "other line"
            problems.append(f"{label}: {name}:{i + 1}: {kind} is {b[:90]!r}")
    print(f"{label}: {name}: {len(planned)} planned line(s), {len(new_lines)} lines")
    return problems


def _pair(root: pathlib.Path, copies: pathlib.Path, name: str) -> tuple[bytes, bytes]:
    return (copies / name).read_bytes(), (root / name).read_bytes()


def defaults_values(root: pathlib.Path, copies: pathlib.Path) -> list[str]:
    problems: list[str] = []
    for name, edits in VALUE_EDITS.items():
        problems += line_edits(name, *_pair(root, copies, name), edits, "defaults-values")
    return problems


def defaults_canon(root: pathlib.Path, copies: pathlib.Path) -> list[str]:
    problems: list[str] = []
    for name, edits in CANON_EDITS.items():
        problems += line_edits(name, *_pair(root, copies, name), edits, "defaults-canon")
    return problems


def index_row(root: pathlib.Path, copies: pathlib.Path) -> list[str]:
    base, now = _pair(root, copies, INDEX)
    problems: list[str] = []
    if _bare_lf(now):
        problems.append(f"index-row: {INDEX} has {_bare_lf(now)} bare LF")
    lines = now.split(b"\r\n")
    row = INDEX_ROW.encode("utf-8")
    hits = [i for i, line in enumerate(lines) if line == row]
    print(f"index-row: the transcript:resume_job row at {[i + 1 for i in hits]}")
    if len(hits) != 1:
        return [*problems, f"index-row: the row occurs {len(hits)} time(s), not once"]
    i = hits[0]
    if i == 0 or lines[i - 1] != RESUME_ROW.encode("utf-8"):
        problems.append(f"index-row: the line before it is not the transcript:resume row: {i}")
    if b"\r\n".join(lines[:i] + lines[i + 1 :]) != base:
        problems.append("index-row: without the row the file differs from its row-0 copy")
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
        if key == ISSUE:
            continue
        if base[key] != now[key]:
            problems.append(f"register: {key} changed")
    if ISSUE not in now or ISSUE not in base:
        problems.append(f"register: {ISSUE} is missing")
    else:
        a, b = base[ISSUE], now[ISSUE]
        changed = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
        print(f"register: {ISSUE} changed fields {sorted(changed)}; status {b.get('status')}")
        if changed - ISSUE_FIELDS:
            problems.append(f"register: {ISSUE} also changed {sorted(changed - ISSUE_FIELDS)}")
        if b.get("status") != "resolved":
            problems.append(f"register: {ISSUE} status is {b.get('status')!r}, not 'resolved'")
    print(f"register: {len(now)} issues now, {len(base)} at row 0")
    g_base, g_now = _pair(root, copies, GROUPING)
    if b"\r" in g_now:
        problems.append(f"register: {GROUPING} has a CR")
    old_lines, new_lines = g_base.split(b"\n"), g_now.split(b"\n")
    rows = [i for i, line in enumerate(old_lines) if line.startswith(b"| 101 |")]
    if len(rows) != 1 or len(old_lines) != len(new_lines):
        return [*problems, f"register: grouping row 101 at {rows}; {len(new_lines)} lines now"]
    want = old_lines[rows[0]].replace(b"| queued |", b"| executed (Session 101) |")
    if want == old_lines[rows[0]]:
        problems.append("register: grouping row 101 did not read queued at row 0")
    for i, (a, b) in enumerate(zip(old_lines, new_lines, strict=True)):
        if b != (want if i == rows[0] else a):
            problems.append(f"register: {GROUPING}:{i + 1} is {b[:90]!r}")
    return problems


# --- named-edits
def _node_problems(
    label: str,
    base: dict[str, str],
    now: dict[str, str],
    forms: dict[str, tuple[str | None, str]],
    free: tuple[str, ...],
    removed: set[str],
) -> list[str]:
    problems: list[str] = []
    added_want = {k for k, (old, _) in forms.items() if old is None} | set(free)
    changed_want = {k for k, (old, _) in forms.items() if old is not None}
    added, gone = set(now) - set(base), set(base) - set(now)
    changed = {k for k in set(base) & set(now) if base[k] != now[k]}
    print(f"named-edits {label}: added {sorted(added)}, removed {sorted(gone)}")
    print(f"named-edits {label}: changed {sorted(changed)}")
    if added != added_want:
        problems.append(f"named-edits: {label}: added {sorted(added)}, not {sorted(added_want)}")
    if gone != removed:
        problems.append(f"named-edits: {label}: removed {sorted(gone)}, not {sorted(removed)}")
    if changed != changed_want:
        problems.append(
            f"named-edits: {label}: changed {sorted(changed)}, not {sorted(changed_want)}"
        )
    for key, (old, new) in forms.items():
        if old is not None and base.get(key) != old:
            problems.append(f"named-edits: {label}: row 0's {key} is not the plan's old form")
        if now.get(key) != new:
            problems.append(f"named-edits: {label}: {key} is not the plan's form")
    for key in free:
        if key in now and not now[key].startswith(f"def {key}("):
            problems.append(f"named-edits: {label}: {key} is not a plain function")
    return problems


def named_edits(root: pathlib.Path, pins: pathlib.Path) -> list[str]:
    data = json.loads(pins.read_text(encoding="utf-8"))
    problems: list[str] = []
    base = data["ast"][SERVICES]
    now = top_level_sources((root / SERVICES).read_bytes().decode("utf-8"))
    problems += _node_problems(SERVICES, base, now, SERVICES_FORMS, AC_163_6, {AC_116_9_OLD})
    # Order: the row-0 order with the new name in the old one's place, the constant just before
    # _four_hundred and the two AC-163.6 tests just after AC-11.3.
    want: list[str] = []
    for key in base:
        if key == FOUR:
            want.append(PACING)
        want.append(AC_116_9 if key == AC_116_9_OLD else key)
        if key == AC_11_3:
            want += sorted(AC_163_6, key=lambda k: list(now).index(k) if k in now else -1)
    if list(now) != want:
        problems.append(f"named-edits: {SERVICES}: the node order is not the planned order")
    base_m = data["ast"][METADATA]
    now_m = top_level_sources((root / METADATA).read_bytes().decode("utf-8"))
    problems += _node_problems(METADATA, base_m, now_m, METADATA_FORMS, (), set())
    if list(now_m) != list(base_m):
        problems.append(f"named-edits: {METADATA}: the node order changed")
    return problems


# --- selftest
PW_FILE = "tests\\e2e\\transcript-job-resume.test.ts"
ARROW = "\u0393\u00c7\u2551"
LOCATOR_EXPECT = [
    "Error: expect(locator).toBeVisible() failed",
    "",
    "Locator: getByTestId('resume-job-btn')",
    "Expected: visible",
    "Timeout: 5000ms",
    "Error: element(s) not found",
    "",
    "Call log:",
    '  - Expect "toBeVisible" with timeout 5000ms',
    "  - waiting for getByTestId('resume-job-btn')",
    "",
    "  40 |   await menu.click();",
    "> 41 |   await expect(page.getByTestId('resume-job-btn')).toBeVisible();",
    "     |                                                     ^",
]
NO_NEEDLE = [
    "Error: expect(locator).toBeVisible() failed",
    "",
    "Locator: getByTestId('job-card-menu')",
    "Expected: visible",
    "Error: element(s) not found",
    "",
    "> 41 |   await expect(page.getByTestId('resume-job-btn')).toBeVisible();",
]
LAUNCH = [
    "Error: electron.launch: Process failed to launch!",
    "",
    "> 12 |   const app = await launchElectron(); // resume-job-btn",
]
SEED = [
    "TypeError: Cannot read properties of undefined (reading 'id')",
    "",
    "Locator: getByTestId('resume-job-btn')",
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


SERVICES_HEAD = """from pathlib import Path

import pytest


def _transcript_stack(tmp_path: Path, clock=None):
    return tmp_path, clock"""
SERVICES_11 = """def test_ac_11_3_resume_only_from_paused(tmp_path: Path) -> None:
    service, _settings, _yt, _uow, _fs, _captions, _sleeps = _transcript_stack(tmp_path)
    service.add_channel("https://youtube.com/@example")
    with pytest.raises(ConflictError):
        service.resume_processing()


def test_ac_11_4_stop_leaves_pending_and_keeps_done(tmp_path: Path) -> None:
    assert tmp_path"""
SERVICES_163 = """def test_ac_163_6_refused_while_processing(tmp_path: Path) -> None:
    assert tmp_path


def test_ac_163_6_idle_resume_done(tmp_path: Path) -> None:
    assert tmp_path"""
SERVICES_TAIL = """def _race_stack(tmp_path: Path):
    return tmp_path"""
METADATA_HEAD = """URL = "https://youtube.com/@real"


def test_ac_122_11_listing(tmp_path: Path) -> None:
    assert tmp_path"""


def _services(
    *, eleven: str = SERVICES_11, new: bool, extra: str = "", order_163: bool = True
) -> str:
    if new:
        parts = [SERVICES_HEAD]
        parts.append(
            eleven.replace(
                "\n\n\ndef test_ac_11_4", "\n\n\n" + SERVICES_163 + "\n\n\ndef test_ac_11_4"
            )
            if order_163
            else eleven
        )
        parts += [PACING_NEW, FOUR_NEW, AC_116_5_NEW, AC_116_9_NEW, SERVICES_TAIL]
        if not order_163:
            parts.append(SERVICES_163)
    else:
        parts = [SERVICES_HEAD, eleven, FOUR_OLD, AC_116_5_OLD, AC_116_9_OLD_SRC, SERVICES_TAIL]
    text = "\n\n\n".join(parts) + extra + "\n"
    return text.replace("\n", "\r\n")


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

        # red-record and red-unchanged (the latest row wins)
        put(root, "tests/unit/test_services.py", "a\n")
        put(root, "ui/b.test.tsx", "b\n")
        case("red-unchanged-no-record", red_unchanged(root, store), False)
        case("red-record-row1", red_record("1", ["tests/unit/test_services.py"], root, store), True)
        case("red-record-row2", red_record("2", ["ui/b.test.tsx"], root, store), True)
        copy = store / RED_COPIES / "row1/tests/unit/test_services.py"
        copied = copy.is_file() and copy.read_bytes() == b"a\n"
        case("red-record-copied", [] if copied else ["copy missing"], True)
        case(
            "red-record-row1-again-same",
            red_record("1", ["tests/unit/test_services.py"], root, store),
            True,
        )
        case("red-unchanged-ok", red_unchanged(root, store), True)
        put(root, "tests/unit/test_services.py", "a edited in row 3a\n")
        case("red-unchanged-changed-before-3a", red_unchanged(root, store), False)
        case(
            "red-record-row1-other-hashes",
            red_record("1", ["tests/unit/test_services.py"], root, store),
            False,
        )
        case(
            "red-record-row3a",
            red_record("3a", ["tests/unit/test_services.py"], root, store),
            True,
        )
        case("red-unchanged-latest-row-wins", red_unchanged(root, store), True)
        order = json.loads((store / RED_STORE).read_text(encoding="utf-8"))["order"]
        case("red-record-order", [] if order == ["1", "2", "3a"] else [str(order)], True)
        put(root, "ui/b.test.tsx", "b changed\n")
        case("red-unchanged-other-file-changed", red_unchanged(root, store), False)
        case("red-record-missing-file", red_record("5", ["ui/none.ts"], root, store), False)

        # pins-unchanged and named-edits
        put(root, SERVICES, _services(new=False))
        put(root, METADATA, (METADATA_HEAD + "\n\n\n" + AC_122_12_OLD + "\n"))
        put(root, "ui/tests/unit/transcript-page.test.ts", "pin\n")
        pins = t / "pins.json"
        pins_data = {
            "files": {
                "ui/tests/unit/transcript-page.test.ts": sha(
                    root / "ui/tests/unit/transcript-page.test.ts"
                )
            },
            "ast": {
                SERVICES: top_level_sources((root / SERVICES).read_bytes().decode("utf-8")),
                METADATA: top_level_sources((root / METADATA).read_bytes().decode("utf-8")),
            },
        }
        pins.write_text(json.dumps(pins_data, indent=2), encoding="utf-8")
        case("pins-unchanged-row0", pins_unchanged(root, pins), True)
        case("named-edits-row0-refused", named_edits(root, pins), False)
        put(root, SERVICES, _services(new=True))
        put(root, METADATA, (METADATA_HEAD + "\n\n\n" + AC_122_12_NEW + "\n"))
        case("pins-unchanged-after-edits", pins_unchanged(root, pins), True)
        case("named-edits-ok", named_edits(root, pins), True)
        eleven = SERVICES_11.replace("assert tmp_path", "assert tmp_path is not None")
        put(root, SERVICES, _services(new=True, eleven=eleven))
        case("pins-unchanged-ac11-changed", pins_unchanged(root, pins), False)
        case("named-edits-other-node-changed", named_edits(root, pins), False)
        put(root, SERVICES, _services(new=True, order_163=False))
        case("named-edits-163-out-of-place", named_edits(root, pins), False)
        put(root, SERVICES, _services(new=True, extra="\n\n\n" + AC_116_9_OLD_SRC))
        case("named-edits-old-name-kept", named_edits(root, pins), False)
        put(root, SERVICES, _services(new=True).replace("{0.0, 120.0, 500.0}", "{0.0, 6.0, 300.0}"))
        case("named-edits-116-5-not-edited", named_edits(root, pins), False)
        put(root, SERVICES, _services(new=True).replace('"retry_delay": 30', '"retry_delay": 7'))
        case("named-edits-pacing-wrong", named_edits(root, pins), False)
        put(root, SERVICES, _services(new=True))
        put(root, METADATA, (METADATA_HEAD + "\n\n\n" + AC_122_12_OLD + "\n"))
        case("named-edits-122-12-not-edited", named_edits(root, pins), False)
        other = METADATA_HEAD.replace("assert tmp_path", "assert tmp_path.exists()")
        put(root, METADATA, (other + "\n\n\n" + AC_122_12_NEW + "\n"))
        case("named-edits-metadata-other-changed", named_edits(root, pins), False)
        put(root, "ui/tests/unit/transcript-page.test.ts", "pin changed\n")
        case("pins-unchanged-file-changed", pins_unchanged(root, pins), False)

        # red-reason
        def receipt(name: str, body: str) -> pathlib.Path:
            p = t / f"{name}.txt"
            p.write_text(body, encoding="utf-8")
            return p

        ids = ["AC-163.7 seam", "AC-163.8 real backend"]
        good = [("AC-163.7 seam: the menu resumes", LOCATOR_EXPECT)]
        good.append(("AC-163.8 real backend: the job resumes", LOCATOR_EXPECT))
        n = "resume-job-btn"
        case("red-reason-ok", red_reason(receipt("rr-ok", _pw(good, 4)), ids, n), True)
        ansi = _pw(good, 4).replace("Error: expect", "\x1b[31mError: expect")
        case("red-reason-ansi", red_reason(receipt("rr-ansi", ansi), ids, n), True)
        one = _pw(good[:1], 5)
        case("red-reason-id-missing", red_reason(receipt("rr-missing", one), ids, n), False)
        bad = [good[0], (good[1][0], LAUNCH)]
        case("red-reason-launch", red_reason(receipt("rr-launch", _pw(bad, 4)), ids, n), False)
        bad = [good[0], (good[1][0], SEED)]
        case("red-reason-seed", red_reason(receipt("rr-seed", _pw(bad, 4)), ids, n), False)
        bad = [good[0], (good[1][0], NO_NEEDLE)]
        case(
            "red-reason-needle-in-frame",
            red_reason(receipt("rr-frame", _pw(bad, 4)), ids, n),
            False,
        )
        timeout = [*LOCATOR_EXPECT[:2], "Test timeout of 30000ms exceeded.", *LOCATOR_EXPECT[2:]]
        bad = [good[0], (good[1][0], timeout)]
        case("red-reason-test-timeout", red_reason(receipt("rr-to", _pw(bad, 4)), ids, n), False)
        prefix = [("AC-163.70 seam x", LOCATOR_EXPECT), good[1]]
        case(
            "red-reason-prefix-is-not-a-match",
            red_reason(receipt("rr-prefix", _pw(prefix, 4)), ["AC-163.7"], n),
            False,
        )

        # e2e-count
        def pw(name: str, body: list[str]) -> pathlib.Path:
            return receipt(name, "\n".join(body) + "\n")

        oks = [
            f"  ok {i:>2} [electron] {ARROW} {PW_FILE}:1:1 {ARROW} AC-163.{6 + i} x (1.0s)"
            for i in range(1, 3)
        ]
        tjr = pw("tjr", ["Running 2 tests using 1 worker", *oks, "", "  2 passed (9.0s)"])
        plain = pw(
            "plain",
            [
                f"  ok 1 [electron] {ARROW} tests\\e2e\\transcript-queue.test.ts:1:1 "
                f"{ARROW} AC-55.7",
                "  12 passed (20.0s)",
            ],
        )
        case("e2e-count-ok-below-10", e2e_count(tjr, 2, [plain]), True)
        case("e2e-count-wrong-n", e2e_count(tjr, 3, [plain]), False)
        flaky = pw("flaky", ["  ok 1 x ΓÇ║ AC-163.7 y (1.0s)", "  1 flaky", "  1 passed (1.0s)"])
        case("e2e-count-flaky", e2e_count(tjr, 2, [flaky]), False)
        rej = pw("rej", [*oks, "unhandled rejection: boom", "  2 passed (9.0s)"])
        case("e2e-count-unhandled", e2e_count(rej, 2, []), False)
        failed = pw("failed", [*oks, "  1 failed", "  2 passed (9.0s)"])
        case("e2e-count-failed", e2e_count(failed, 2, []), False)
        nopass = pw("nopass", ["  ok 1 tests\\e2e\\x.ts:1:1 ΓÇ║ AC-55.7 (1.0s)"])
        case("e2e-count-plain-no-pass", e2e_count(tjr, 2, [nopass]), False)

        # defaults-values and defaults-canon
        def crlf(lines: list[str]) -> bytes:
            return ("\r\n".join(lines) + "\r\n").encode("utf-8")

        py_old = ["SPECS = {", *(o for o, _ in VALUE_EDITS[SETTINGS_PY]), "}"]
        py_new = ["SPECS = {", *(n for _, n in VALUE_EDITS[SETTINGS_PY]), "}"]
        ts_old = ["transcript: {", *(o for o, _ in VALUE_EDITS[SETTINGS_TS]), "},"]
        ts_new = ["transcript: {", *(n for _, n in VALUE_EDITS[SETTINGS_TS]), "},"]
        put(copies, SETTINGS_PY, crlf(py_old))
        put(copies, SETTINGS_TS, crlf(ts_old))
        put(root, SETTINGS_PY, crlf(py_new))
        put(root, SETTINGS_TS, crlf(ts_new))
        case("defaults-values-ok", defaults_values(root, copies), True)
        put(root, SETTINGS_TS, crlf(ts_old))
        case("defaults-values-ts-not-edited", defaults_values(root, copies), False)
        put(root, SETTINGS_TS, crlf(ts_new).replace(b"\r\n", b"\n"))
        case("defaults-values-lf", defaults_values(root, copies), False)
        put(root, SETTINGS_TS, crlf([*ts_new[:-1], "    playlist_end: 1,", "},"]))
        case("defaults-values-extra-line", defaults_values(root, copies), False)
        put(root, SETTINGS_TS, crlf([ts_new[0].replace("{", "{ "), *ts_new[1:]]))
        case("defaults-values-other-line-changed", defaults_values(root, copies), False)
        wrong = [line.replace("default: 7 ", "default: 8 ") for line in ts_new]
        put(root, SETTINGS_TS, crlf(wrong))
        case("defaults-values-wrong-number", defaults_values(root, copies), False)
        put(root, SETTINGS_TS, crlf(ts_new))
        put(copies, SETTINGS_PY, crlf([*py_old, py_old[1]]))
        put(root, SETTINGS_PY, crlf([*py_new, py_old[1]]))
        case("defaults-values-old-line-doubled", defaults_values(root, copies), False)

        tail = _gui_row("playlist_end", 0, None)
        gui_old = ["| Key | Type | Default | Source |", *(o for o, _ in CANON_EDITS[GUI]), tail]
        gui_new = ["| Key | Type | Default | Source |", *(n for _, n in CANON_EDITS[GUI]), tail]
        put(copies, GUI, crlf(gui_old))
        put(copies, SERVICE_LAYER, crlf(["| Rule | Text | Source |", RATE_CAP_OLD, "| x |"]))
        put(root, GUI, crlf(gui_new))
        put(root, SERVICE_LAYER, crlf(["| Rule | Text | Source |", RATE_CAP_NEW, "| x |"]))
        case("defaults-canon-ok", defaults_canon(root, copies), True)
        row = "| `transcript.requests_per_hour` | `number` | `20` | "
        row += "Mat 2026-11-21 (D-1355); was 300 per"
        ok = gui_new[1] == row + " " + LINK + " |"
        case("defaults-canon-row-form", [] if ok else [gui_new[1]], True)
        put(root, GUI, crlf([*gui_new[:-1], _gui_row("playlist_end", 0, 0)]))
        case("defaults-canon-playlist-end-changed", defaults_canon(root, copies), False)
        put(root, GUI, crlf(gui_new))
        put(root, SERVICE_LAYER, crlf(["| Rule | Text | Source |", RATE_CAP_OLD, "| x |"]))
        case("defaults-canon-rate-cap-not-edited", defaults_canon(root, copies), False)

        # index-row
        idx_old = ["| Id | Action |", RESUME_ROW, "| `transcript:stop` | Stop |"]
        put(copies, INDEX, crlf(idx_old))
        put(root, INDEX, crlf([*idx_old[:2], INDEX_ROW, idx_old[2]]))
        case("index-row-ok", index_row(root, copies), True)
        put(root, INDEX, crlf([idx_old[0], INDEX_ROW, *idx_old[1:]]))
        case("index-row-before-resume", index_row(root, copies), False)
        put(root, INDEX, crlf([*idx_old[:2], INDEX_ROW, INDEX_ROW, idx_old[2]]))
        case("index-row-twice", index_row(root, copies), False)
        put(root, INDEX, crlf([*idx_old[:2], INDEX_ROW, idx_old[2]]).replace(b"\r\n", b"\n", 1))
        case("index-row-bare-lf", index_row(root, copies), False)
        put(root, INDEX, crlf([*idx_old[:2], INDEX_ROW, idx_old[2] + " "]))
        case("index-row-other-line-changed", index_row(root, copies), False)
        put(root, INDEX, crlf(idx_old))
        case("index-row-absent", index_row(root, copies), False)

        # register
        def reg(issue: dict, other: str = "open") -> bytes:
            data = {
                "version": 1,
                "issues": [
                    {"id": "CAPTURE-JOURNAL-VOLATILE", "status": other, "severity": "low"},
                    issue,
                ],
            }
            return yaml.safe_dump(data, sort_keys=False).replace("\n", "\r\n").encode("utf-8")

        open_issue = {
            "id": ISSUE,
            "status": "open",
            "severity": "medium",
            "meu_links": ["MEU-163"],
            "verification": {"last_checked": "2026-11-21", "method": "m", "result": "r"},
        }
        done = {
            **open_issue,
            "status": "resolved",
            "verification": {"last_checked": "2026-11-21", "method": "tjr", "result": "ok"},
            "resolution_path": "Fixed in Session 101 on 2026-11-21",
        }
        grouping = (
            "| Session | Slug |\n| 101 | `transcript-job-resume` | MEU-163 | P3 | queued | x |\n"
        )
        put(copies, REGISTER, reg(open_issue))
        put(copies, GROUPING, grouping)
        put(root, REGISTER, reg(done))
        put(root, GROUPING, grouping.replace("| queued |", "| executed (Session 101) |"))
        case("register-ok", register(root, copies), True)
        put(root, REGISTER, reg(done, other="resolved"))
        case("register-other-issue-changed", register(root, copies), False)
        put(root, REGISTER, reg({**done, "severity": "low"}))
        case("register-issue-other-field", register(root, copies), False)
        put(root, REGISTER, reg({**done, "meu_links": ["MEU-163", "MEU-1"]}))
        case("register-meu-links-changed", register(root, copies), False)
        put(root, REGISTER, reg({**done, "status": "open"}))
        case("register-not-resolved", register(root, copies), False)
        put(root, REGISTER, reg(done))
        put(root, GROUPING, grouping)
        case("register-grouping-still-queued", register(root, copies), False)
        put(root, GROUPING, grouping.replace("| queued |", "| executed |"))
        case("register-grouping-other-text", register(root, copies), False)
        put(root, GROUPING, grouping.replace("| queued |", "| executed (Session 101) |") + "x\n")
        case("register-grouping-extra-line", register(root, copies), False)

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
        elif cmd == "index-row" and not rest:
            problems = index_row(ROOT, COPIES)
        elif cmd == "register" and not rest:
            problems = register(ROOT, COPIES)
        elif cmd == "named-edits" and not rest:
            problems = named_edits(ROOT, PINS)
        elif cmd == "defaults-values" and not rest:
            problems = defaults_values(ROOT, COPIES)
        elif cmd == "defaults-canon" and not rest:
            problems = defaults_canon(ROOT, COPIES)
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
