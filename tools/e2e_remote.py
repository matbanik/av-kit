"""Run the Electron E2E suite on a second Windows host over pinned SSH (Session 96).

Usage::

    uv run python tools/e2e_remote.py check [--config F] [--out FILE]
    uv run python tools/e2e_remote.py run COMMIT [--config F] [--receipts DIR] [--payload DIR]
    uv run python tools/e2e_remote.py collect RUN_ID [--config F] [--receipts DIR]
    uv run python tools/e2e_remote.py release RUN_ID [--config F]
    uv run python tools/e2e_remote.py summarize REPORT --label L [--specs FILE] [--known FILE]
        [--register FILE] [--out DIR]

The local config is ``--config``, else ``AVKIT_E2E_HOST_CONFIG``, else
``<HOME>/.config/av-kit/e2e-host.json``; it is never tracked. ``run`` archives the commit, stages
the host scripts in ``tools/e2e_host/`` into a content-addressed ``<root>\\bin\\<set>\\``, takes
the host's lock, uploads, verifies, extracts, builds, starts the host's scheduled task, polls,
collects ``report.json`` and summarizes it against ``tools/e2e_host/known-failures.json``. Every
outcome is one reason of ``REASONS``; the last stdout line of ``run`` and ``collect`` is
``e2e-remote: <reason> exit=<n> run=<id> receipts=<dir>``. The tool never stops a process and
never changes the scheduled task; the run book is ``.agent/docs/e2e-remote-host.md``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
HOST_DIR = REPO / "tools/e2e_host"
KNOWN_FILE = HOST_DIR / "known-failures.json"
REGISTER = REPO / ".agent/context/known-issues.yaml"
STUB_DIR = REPO / "native/region-picker-stub/publish"
RECEIPTS = Path("C:/Temp/av-kit/e2e-remote")
SSH_OPTS = ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes"]
BUILD_TIMEOUT_S = 2700
STEP_TIMEOUT_S = 300

#: Every outcome and its exit code (the run book's table lists each one).
REASONS: dict[str, int] = {
    "ok": 0,
    "released": 0,
    "usage": 2,
    "payload-invalid": 2,
    "config-missing": 2,
    "config-invalid": 2,
    "ssh-failed": 10,
    "host-key-failed": 11,
    "no-desktop-session": 20,
    "desktop-locked": 21,
    "host-busy": 22,
    "host-busy-unknown": 22,
    "host-locked": 23,
    "lock-mismatch": 23,
    "task-running": 24,
    "task-not-started": 24,
    "prerequisite-missing": 25,
    "commit-unknown": 26,
    "commit-mismatch": 26,
    "upload-mismatch": 26,
    "payload-mismatch": 26,
    "build-stale": 27,
    "build-failed": 28,
    "request-missing": 29,
    "poll-timeout": 30,
    "launcher-ended": 30,
    "report-missing": 31,
    "report-invalid": 31,
    "report-inconsistent": 31,
    "report-errors": 31,
    "specs-mismatch": 31,
    "known-failures-stale": 32,
    "receipt-exists": 33,
    "receipt-write-failed": 34,
    "new-failures": 40,
    "install-failures": 41,
}

#: The ``prerequisite-missing`` ids, in the order they are reported.
PREREQ_IDS = (
    "node",
    "node-version",
    "uv",
    "vcruntime",
    "ffmpeg",
    "ffprobe",
    "task",
    "task-principal",
    "task-logon-interactive",
    "task-action",
    "task-limit",
    "picker-stub-local",
    "disk",
)

CONFIG_KEYS = (
    "host",
    "user",
    "label",
    "root",
    "task",
    "node_exe",
    "ffmpeg_bin",
    "busy_users",
    "min_free_gb",
    "poll_s",
    "timeout_min",
)
HOST_JSON_KEYS = ("user", "root", "task", "node_exe", "ffmpeg_bin", "busy_users", "min_free_gb")
INT_RANGES = {"min_free_gb": (5, 1000), "poll_s": (5, 300), "timeout_min": (10, 115)}
BAD_CHARS = frozenset("\"'$;|&`\n\r")
HOST_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]{0,62}")
USER_RE = re.compile(r"[A-Za-z0-9._-]{1,64}")
LABEL_RE = re.compile(r"[a-z0-9-]{1,32}")
ROOT_RE = re.compile(r"[A-Za-z]:\\[A-Za-z0-9._\\-]{1,120}")
SPACED_RE = re.compile(r"[A-Za-z]:\\[A-Za-z0-9._\\ -]{1,120}")
TASK_RE = re.compile(r"\\[A-Za-z0-9._\\-]+\\[A-Za-z0-9._-]+")
PROFILE_RE = re.compile(r"(^|\\)users(\\|$)", re.IGNORECASE)
RUN_ID_RE = re.compile(r"r[0-9]{8}T[0-9]{6}Z-[0-9a-f]{7}")
ARG_RE = re.compile(r"[0-9A-Za-z-]+")
AC_RE = re.compile(r"AC-[0-9]+(\.[0-9]+)*")

STUB_NAMES = (
    "avkit-region-picker-stub.exe",
    "avkit-region-picker-stub.dll",
    "avkit-region-picker-stub.deps.json",
    "avkit-region-picker-stub.runtimeconfig.json",
)
TEST_PROCS = ("node", "electron", "python", "pytest", "vitest")
ORPHAN_PROCS = ("node", "electron")
STATUSES = ("expected", "unexpected", "flaky", "skipped")
#: ``HOST_PAYLOAD`` (Session 106): a flat folder of ``payload.json`` and at most five files.
PAYLOAD_MAX_FILES = 5
PAYLOAD_MAX_BYTES = 1_200_000_000
PAYLOAD_NAME_RE = re.compile(r"[A-Za-z0-9._-]{1,100}")
STAGES = ("verify", "extract", "build", "stale")
DONE_MAP = {
    95: "request-missing",
    96: "no-desktop-session",
    97: "desktop-locked",
    98: "commit-mismatch",
    99: "build-stale",
}
NOISE = (
    "** WARNING: connection is not using a post-quantum",
    "** This session",
    "** The server may need",
)
HOST_KEY_TEXT = ("Host key verification failed", "REMOTE HOST IDENTIFICATION HAS CHANGED")


# --- seams the tests replace ----------------------------------------------------------------


class Result:
    """One finished command: exit code, stdout and stderr as text."""

    def __init__(self, code: int, out: str = "", err: str = "") -> None:
        self.code, self.out, self.err = code, out, err


def run_cmd(argv: list[str], timeout: float | None = None) -> Result:
    """Run ``argv`` with no stdin; bytes are decoded as UTF-8 with replacement."""
    try:
        done = subprocess.run(
            [str(a) for a in argv],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return Result(-1, "", f"timed out after {timeout} s")
    except OSError as exc:
        return Result(-1, "", f"could not start {argv[0]}: {exc}")
    out = done.stdout.decode("utf-8", "replace") if done.stdout else ""
    err = done.stderr.decode("utf-8", "replace") if done.stderr else ""
    return Result(done.returncode, out, err)


def archive(commit: str, out_path: Path) -> None:
    """``git archive`` the commit into a zip; git writes the commit id as the zip comment."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    r = run_cmd(
        ["git", "-C", str(REPO), "archive", "--format=zip", "-o", str(out), commit],
        timeout=STEP_TIMEOUT_S,
    )
    if r.code != 0:
        raise Refusal("commit-unknown", f"git archive failed: {_last_line(r.err)}")


def sleep(seconds: float) -> None:
    time.sleep(seconds)


def utcnow() -> datetime:
    return datetime.now(UTC)


# --- refusals and output --------------------------------------------------------------------


class Refusal(Exception):
    """A named outcome from ``REASONS``; ``keep_lock`` leaves the host lock in place."""

    def __init__(
        self,
        reason: str,
        detail: str = "",
        *,
        keep_lock: bool = False,
        hint: str = "",
        also: list[tuple[str, str]] | None = None,
    ) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail
        self.keep_lock = keep_lock
        self.hint = hint
        self.also = also or []

    @property
    def code(self) -> int:
        return REASONS.get(self.reason, 10)


def safe(text: object) -> str:
    """ASCII form of any text: non-ASCII characters become backslash escapes."""
    return str(text).encode("ascii", "backslashreplace").decode("ascii")


def say(text: object) -> None:
    print(safe(text), flush=True)


def print_refusal(e: Refusal) -> None:
    say(f"refused: {e.reason}: {e.detail}" if e.detail else f"refused: {e.reason}")
    for reason, detail in e.also:
        say(f"also refused: {reason}: {detail}")
    if e.hint:
        say(e.hint)


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _last_line(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_atomic(path: Path, data: bytes) -> None:
    """Write to ``<name>.tmp`` and rename it over ``path`` (``NO_PARTIAL``)."""
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_bytes(data)
        os.replace(tmp, path)
    except OSError as exc:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise Refusal("receipt-write-failed", f"{path.name}: {exc}") from exc


def unique_path(path: Path) -> Path:
    """``path`` when free, else ``<stem>-2<suffix>``, ``-3`` and on; never an existing file."""
    if not path.exists():
        return path
    n = 2
    while True:
        cand = path.with_name(f"{path.stem}-{n}{path.suffix}")
        if not cand.exists():
            return cand
        n += 1


def _json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=True) + "\n").encode("ascii")


# --- the local config -----------------------------------------------------------------------


def config_path(arg: str | None) -> Path:
    if arg:
        return Path(arg)
    env = os.environ.get("AVKIT_E2E_HOST_CONFIG")
    if env:
        return Path(env)
    return Path.home() / ".config/av-kit/e2e-host.json"


def _text_ok(value: object, rx: re.Pattern[str]) -> bool:
    return isinstance(value, str) and not (set(value) & BAD_CHARS) and bool(rx.fullmatch(value))


def _value_ok(key: str, value: object) -> bool:
    if key == "host":
        return _text_ok(value, HOST_RE)
    if key == "user":
        return _text_ok(value, USER_RE)
    if key == "label":
        return _text_ok(value, LABEL_RE)
    if key == "root":
        return _text_ok(value, ROOT_RE) and not PROFILE_RE.search(str(value))
    if key == "task":
        return _text_ok(value, TASK_RE)
    if key in ("node_exe", "ffmpeg_bin"):
        return _text_ok(value, SPACED_RE) and not PROFILE_RE.search(str(value))
    if key == "busy_users":
        return isinstance(value, list) and all(_text_ok(v, USER_RE) for v in value)
    lo, hi = INT_RANGES[key]
    return isinstance(value, int) and not isinstance(value, bool) and lo <= value <= hi


def validate_config(data: object) -> dict:
    if not isinstance(data, dict):
        raise Refusal("config-invalid", "json")
    for key in sorted(data):
        if key not in CONFIG_KEYS:
            raise Refusal("config-invalid", str(key))
    for key in CONFIG_KEYS:
        if key not in data or not _value_ok(key, data[key]):
            raise Refusal("config-invalid", key)
    return dict(data)


def load_config(path: Path | str) -> dict:
    p = Path(path)
    if not p.is_file():
        raise Refusal("config-missing", str(p))
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise Refusal("config-invalid", "json") from exc
    return validate_config(data)


# --- git ------------------------------------------------------------------------------------


def git(*args: str) -> str:
    r = run_cmd(["git", "-C", str(REPO), *args], timeout=STEP_TIMEOUT_S)
    if r.code != 0:
        raise Refusal("commit-unknown", f"git {args[0]}: {_last_line(r.err) or r.code}")
    return r.out


def resolve_commit(commit: str) -> str:
    if not re.fullmatch(r"[0-9a-fA-F]{4,40}", commit or ""):
        raise Refusal("commit-unknown", commit)
    r = run_cmd(
        ["git", "-C", str(REPO), "rev-parse", "--verify", "--quiet", commit + "^{commit}"],
        timeout=STEP_TIMEOUT_S,
    )
    sha = r.out.strip()
    if r.code != 0 or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise Refusal("commit-unknown", commit)
    return sha


def node_major_of(ref: str) -> int:
    text = git("show", f"{ref}:.node-version").strip()
    m = re.match(r"v?(\d+)", text)
    if not m:
        raise Refusal("commit-unknown", f".node-version of {ref} reads {text!r}")
    return int(m.group(1))


def commit_specs(sha: str) -> list[str]:
    names = git("ls-tree", "--name-only", sha, "ui/tests/e2e/").splitlines()
    return sorted(
        n.rsplit("/", 1)[-1] for n in names if n.endswith(".test.ts") or n.endswith(".spec.ts")
    )


# --- the known list and the register --------------------------------------------------------


def load_known(path: Path) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        raise Refusal("known-failures-stale", f"known list unreadable: {Path(path).name}") from exc
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("known"), list)
        or not isinstance(data.get("skip"), list)
        or not all(isinstance(e, dict) for e in data["known"] + data["skip"])
    ):
        raise Refusal("known-failures-stale", f"known list malformed: {Path(path).name}")
    # Session 98: an optional ``gated`` list of {label, file, reason}; a missing key is [].
    gated = data.get("gated", [])
    if not isinstance(gated, list) or not all(
        isinstance(e, dict) and all(k in e for k in ("label", "file", "reason")) for e in gated
    ):
        raise Refusal("known-failures-stale", f"known list gated malformed: {Path(path).name}")
    data["gated"] = gated
    return data


def label_skip(known: dict, label: str) -> list[dict]:
    return [
        {"file": e.get("file"), "reason": e.get("reason")}
        for e in known["skip"]
        if e.get("label") == label
    ]


def label_gated(known: dict, label: str) -> list[str]:
    """The label's gated spec files (Session 98): they run in the gated stage, not the main."""
    return [e.get("file") for e in known.get("gated", []) if e.get("label") == label]


def _label_gated_entries(known: dict, label: str) -> list[dict]:
    return [e for e in known.get("gated", []) if e.get("label") == label]


def register_status(path: Path) -> dict[str, str]:
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as exc:
        raise Refusal("known-failures-stale", f"register unreadable: {Path(path).name}") from exc
    issues = data.get("issues") if isinstance(data, dict) else None
    if not isinstance(issues, list):
        raise Refusal("known-failures-stale", f"register has no issues list: {Path(path).name}")
    return {
        str(i.get("id")): str(i.get("status"))
        for i in issues
        if isinstance(i, dict) and i.get("id") is not None
    }


# --- facts: refusal order and poll overlap --------------------------------------------------


def _bare(user: object) -> str:
    return str(user or "").rsplit("\\", 1)[-1].lower()


def _busy_items(f: dict, cfg: dict) -> list[str]:
    users = {u.lower() for u in cfg["busy_users"]}
    items = []
    for b in f.get("busy") or []:
        if _bare(b.get("user")) in users and str(b.get("name", "")).lower() in TEST_PROCS:
            items.append(f"{_bare(b.get('user'))} {b.get('name')} {b.get('pid')}")
    for w in f.get("runner_workers") or []:
        items.append(f"Runner.Worker {_bare(w.get('user'))} {w.get('pid')}")
    return items


def _orphan_text(o: dict) -> str:
    return f"orphan {_bare(o.get('user'))} {o.get('name')} {o.get('pid')}"


def evaluate(f: dict, cfg: dict, node_major: int) -> list[tuple[str, str]]:
    """Every reason the facts give, in the refusal order; the first decides the exit."""
    out: list[tuple[str, str]] = []
    user = cfg["user"].lower()
    sess = f.get("user_session") or {}
    mine = [
        e
        for e in f.get("explorer") or []
        if _bare(e.get("user")) == user and e.get("session") not in (0, None)
    ]
    if not mine or sess.get("state") != "Active":
        out.append(
            (
                "no-desktop-session",
                f"explorer of user outside session 0: {len(mine)}; "
                f"session {sess.get('id')} state {sess.get('state')}",
            )
        )
    if sess.get("id") is not None and sess.get("id") in (f.get("logonui_sessions") or []):
        out.append(("desktop-locked", f"LogonUI in session {sess.get('id')}"))
    busy = _busy_items(f, cfg)
    busy += [
        _orphan_text(o)
        for o in f.get("own_orphans") or []
        if str(o.get("name", "")).lower() in ORPHAN_PROCS
    ]
    if busy:
        out.append(("host-busy", "; ".join(busy)))
    if cfg["busy_users"] and (not f.get("elevated") or not f.get("owners_seen")):
        out.append(("host-busy-unknown", "process owners are hidden from this SSH session"))
    lock = f.get("lock")
    if lock:
        out.append(("host-locked", f"holder={lock.get('run_id')}"))
    t = f.get("task") or {}
    if t.get("state") == "Running":
        out.append(("task-running", "the task is Running"))
    missing = _missing_prereqs(f, cfg, node_major)
    if missing:
        out.append(("prerequisite-missing", ",".join(missing)))
    return out


def _missing_prereqs(f: dict, cfg: dict, node_major: int) -> list[str]:
    miss: set[str] = set()
    node = f.get("node") or {}
    if not node.get("exists"):
        miss.add("node")
    else:
        m = re.match(r"v?(\d+)", str(node.get("version") or ""))
        if not m or int(m.group(1)) != node_major:
            miss.add("node-version")
    for key in ("uv", "vcruntime", "ffmpeg", "ffprobe"):
        if not f.get(key):
            miss.add(key)
    t = f.get("task") or {}
    if not t.get("exists"):
        miss.add("task")
    else:
        if _bare(t.get("principal")) != cfg["user"].lower():
            miss.add("task-principal")
        if t.get("logon") != "Interactive":
            miss.add("task-logon-interactive")
        exe = str(t.get("action_exe") or "").rsplit("\\", 1)[-1].lower()
        pattern = r'-File\s+"?' + re.escape(cfg["root"]) + r'\\run-e2e\.ps1"?(\s|$)'
        if exe != "powershell.exe" or not re.search(
            pattern, str(t.get("action_args") or ""), re.IGNORECASE
        ):
            miss.add("task-action")
        limit = t.get("limit_min")
        if not isinstance(limit, int) or (limit != 0 and limit < cfg["timeout_min"] + 5):
            miss.add("task-limit")
    if not all((Path(STUB_DIR) / n).is_file() for n in STUB_NAMES):
        miss.add("picker-stub-local")
    free = f.get("free_gb")
    if not isinstance(free, (int, float)) or free < cfg["min_free_gb"]:
        miss.add("disk")
    return [p for p in PREREQ_IDS if p in miss]


def run_tree(status: dict, run_id: str) -> set:
    """The verified run tree: ``pid.txt``'s process and its descendants, else nothing."""
    lock = status.get("lock") or {}
    pf = status.get("pid_file") or {}
    procs = {p.get("pid"): p for p in status.get("user_procs") or []}
    root = procs.get(pf.get("pid"))
    if lock.get("run_id") != run_id or root is None or root.get("created") != pf.get("start"):
        return set()
    tree = {root.get("pid")}
    grew = True
    while grew:
        grew = False
        for p in procs.values():
            parent = procs.get(p.get("ppid"))
            if (
                p.get("pid") not in tree
                and p.get("ppid") in tree
                and parent is not None
                and str(p.get("created")) >= str(parent.get("created"))
            ):
                tree.add(p.get("pid"))
                grew = True
    return tree


def poll_overlap(status: dict, cfg: dict, run_id: str) -> list[str]:
    """What one poll saw that another workload or a stray process could have caused."""
    problems: list[str] = []
    sess = status.get("user_session") or {}
    if sess.get("id") is not None and sess.get("id") in (status.get("logonui_sessions") or []):
        problems.append(f"LogonUI in session {sess.get('id')}")
    if sess.get("state") != "Active":
        problems.append(f"session state {sess.get('state')}")
    lock = status.get("lock") or {}
    if lock.get("run_id") != run_id:
        problems.append(f"lock holder={lock.get('run_id')}")
    problems += _busy_items(status, cfg)
    tree = run_tree(status, run_id)
    for o in status.get("own_orphans") or []:
        if str(o.get("name", "")).lower() in ORPHAN_PROCS and o.get("pid") not in tree:
            problems.append(_orphan_text(o))
    return problems


def fact_lines(f: dict) -> list[str]:
    t = f.get("task") or {}
    lock = f.get("lock") or {}
    sess = f.get("user_session") or {}
    node = f.get("node") or {}
    launcher = f.get("launcher") or {}
    lines = [
        f"facts: ps={f.get('ps_version')} elevated={f.get('elevated')} "
        f"procs={f.get('procs_total')} owners_seen={f.get('owners_seen')}",
        f"desktop: explorer={len(f.get('explorer') or [])} session={sess.get('id')} "
        f"state={sess.get('state')} logonui={f.get('logonui_sessions')}",
        f"busy: busy={len(f.get('busy') or [])} "
        f"runner_workers={len(f.get('runner_workers') or [])} "
        f"own_orphans={len(f.get('own_orphans') or [])} "
        f"busy_users_missing={','.join(f.get('busy_users_missing') or [])}",
        f"task: exists={t.get('exists')} state={t.get('state')} logon={t.get('logon')} "
        f"runlevel={t.get('runlevel')} limit_min={t.get('limit_min')} multiple={t.get('multiple')}",
        f"lock: holder={lock.get('run_id')} launcher_marker={launcher.get('marker')}",
        f"prereq: node={node.get('version')} uv={f.get('uv')} vcruntime={f.get('vcruntime')} "
        f"ffmpeg={f.get('ffmpeg')} ffprobe={f.get('ffprobe')} free_gb={f.get('free_gb')}",
        f"clock: utc_now={f.get('utc_now')} tz_offset_min={f.get('tz_offset_min')} "
        f"ssh_shell_set={bool(f.get('ssh_shell'))}",
    ]
    probe = f.get("session_probe")
    if isinstance(probe, dict):
        # A fact, not a refusal: printed whatever the state (Session 98).
        lines.append(
            f"session-probe: state={probe.get('state')} reason={probe.get('reason')} "
            f"rustdesk={probe.get('rustdesk_version') or '-'}"
        )
    if "smart_app_control" in f:
        # A fact for the install stage (Session 106): 0 off, 1 on, 2 evaluation.
        lines.append(f"smart-app-control: state={f.get('smart_app_control') or '-'}")
    return lines


# --- transport ------------------------------------------------------------------------------


def _clean_err(err: str) -> str:
    return "\n".join(
        ln for ln in err.splitlines() if ln.strip() and not ln.strip().startswith(NOISE)
    )


def _transport_refusal(r: Result) -> Refusal | None:
    err = _clean_err(r.err)
    if r.code == 255:
        if any(t in err for t in HOST_KEY_TEXT):
            return Refusal("host-key-failed", _last_line(err))
        return Refusal("ssh-failed", _last_line(err) or "exit 255")
    return None


def _last_json(out: str) -> dict | None:
    for line in reversed(out.splitlines()):
        s = line.strip()
        if not s.startswith("{"):
            continue
        try:
            obj = json.loads(s)
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def remote_root(cfg: dict) -> str:
    return cfg["host"] + ":" + cfg["root"].replace("\\", "/")


def host_call(
    cfg: dict,
    set_id: str,
    script: str,
    *args: str,
    timeout: float = STEP_TIMEOUT_S,
    save: Path | None = None,
) -> dict:
    """Run one host script; its outcome is the ``reason`` of its last JSON stdout line."""
    for a in (set_id, *args):
        if not ARG_RE.fullmatch(a):
            raise Refusal("usage", f"host argument {a!r}")
    path = cfg["root"] + "\\bin\\" + set_id + "\\" + script
    argv = [
        "ssh",
        *SSH_OPTS,
        cfg["host"],
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        path,
        *args,
    ]
    r = run_cmd(argv, timeout=timeout)
    bad = _transport_refusal(r)
    if bad is not None:
        raise bad
    obj = _last_json(r.out)
    if obj is None:
        raise Refusal("ssh-failed", "no-result")
    if save is not None:
        write_atomic(save, _json_bytes(obj))
    reason = obj.get("reason")
    if reason == "ok":
        return obj
    if not isinstance(reason, str) or reason not in REASONS or REASONS[reason] == 0:
        raise Refusal("ssh-failed", f"{script} reason {reason}")
    raise Refusal(reason, str(obj.get("detail", "")))


def scp(src: str, dst: str, timeout: float = STEP_TIMEOUT_S) -> None:
    r = run_cmd(["scp", *SSH_OPTS, "-r", src, dst], timeout=timeout)
    bad = _transport_refusal(r)
    if bad is not None:
        raise bad
    if r.code != 0:
        raise Refusal("ssh-failed", f"scp exit {r.code}: {_last_line(_clean_err(r.err))}")


def stage(cfg: dict, base: Path) -> str:
    """Write the host set under ``base/stage/bin/<set>/`` and copy ``bin`` to the host."""
    files = {
        p.name: p.read_bytes()
        for p in sorted(Path(HOST_DIR).iterdir())
        if p.is_file() and p.suffix == ".ps1"
    }
    files["host.json"] = _json_bytes({k: cfg[k] for k in HOST_JSON_KEYS})
    h = hashlib.sha256()
    for name in sorted(files):
        h.update(name.encode() + b"\0" + files[name] + b"\0")
    set_id = h.hexdigest()[:12]
    target = base / "stage" / "bin" / set_id
    target.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (target / name).write_bytes(data)
    scp(str(base / "stage" / "bin"), remote_root(cfg) + "/")
    return set_id


# --- summarize ------------------------------------------------------------------------------


def _walk(suites: list, inherited: str | None, rows: list[dict]) -> None:
    for s in suites:
        if not isinstance(s, dict):
            continue
        sfile = s.get("file") or inherited
        for spec in s.get("specs") or []:
            title = str(spec.get("title", ""))
            first = title.split(maxsplit=1)[0] if title.split() else ""
            ac = first if AC_RE.fullmatch(first) else None
            for t in spec.get("tests") or []:
                rows.append(
                    {
                        "file": str(spec.get("file") or sfile),
                        "ac": ac,
                        "title": title,
                        "status": t.get("status"),
                    }
                )
        _walk(s.get("suites") or [], sfile, rows)


def _report_rows(report_path: Path) -> tuple[dict, list[dict], dict[str, int]]:
    """A Playwright JSON report's data, test rows and counts; refusals 31 raise."""
    if not report_path.is_file():
        raise Refusal("report-missing", str(report_path))
    try:
        data = json.loads(report_path.read_text(encoding="utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise Refusal("report-invalid", "not JSON") from exc
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("suites"), list)
        or not isinstance(data.get("stats"), dict)
    ):
        raise Refusal("report-invalid", "no suites and stats")
    if data.get("errors"):
        first = data["errors"][0]
        msg = first.get("message", "") if isinstance(first, dict) else first
        raise Refusal("report-errors", f"{len(data['errors'])} error(s): {_last_line(str(msg))}")
    rows: list[dict] = []
    _walk(data["suites"], None, rows)
    counts = {k: sum(1 for r in rows if r["status"] == k) for k in STATUSES}
    stats = data["stats"]
    off = [
        f"{k} walked {counts[k]} stats {stats.get(k)}"
        for k in STATUSES
        if stats.get(k) != counts[k]
    ]
    if sum(counts.values()) != len(rows):
        off.append(f"{len(rows) - sum(counts.values())} test(s) with another status")
    if off:
        raise Refusal("report-inconsistent", "; ".join(off))
    return data, rows, counts


def read_payload(folder: Path) -> list[tuple[Path, dict]]:
    """``HOST_PAYLOAD``: the payload files and their request entries; a bad folder raises 2."""
    if not folder.is_dir():
        raise Refusal("payload-invalid", f"{folder} is not a folder")
    found: list[tuple[Path, dict]] = []
    total = 0
    for p in sorted(folder.iterdir(), key=lambda q: q.name):
        if not p.is_file() or p.is_symlink():
            raise Refusal("payload-invalid", f"{p.name} is not a plain file (the folder is flat)")
        if not PAYLOAD_NAME_RE.fullmatch(p.name):
            raise Refusal("payload-invalid", f"{p.name!r} is not a plain file name")
        size = p.stat().st_size
        total += size
        found.append((p, {"name": p.name, "size": size, "sha256": sha256_file(p)}))
    names = [e["name"] for _, e in found]
    if "payload.json" not in names:
        raise Refusal("payload-invalid", "no payload.json")
    if len(names) - 1 > PAYLOAD_MAX_FILES:
        raise Refusal(
            "payload-invalid",
            f"{len(names) - 1} files besides payload.json, at most {PAYLOAD_MAX_FILES}",
        )
    if total > PAYLOAD_MAX_BYTES:
        raise Refusal("payload-invalid", f"{total} bytes, at most {PAYLOAD_MAX_BYTES}")
    try:
        json.loads((folder / "payload.json").read_text(encoding="utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise Refusal("payload-invalid", "payload.json is not JSON") from exc
    return found


def install_block(folder: Path, has_payload: bool) -> dict:
    """The summary's ``install`` block: ``not-run``, ``missing``, ``invalid`` or ``ran``."""
    if not has_payload:
        return {"state": "not-run"}
    if not (folder / "report.json").is_file():
        return {"state": "missing"}
    try:
        _, rows, counts = _report_rows(folder / "report.json")
    except Refusal as exc:
        return {"state": "invalid", "detail": f"{exc.reason}: {exc.detail}"}
    return {
        "state": "ran",
        "tests": len(rows),
        **counts,
        "failed": [
            {"file": r["file"], "title": r["title"], "status": r["status"]}
            for r in rows
            if r["status"] != "expected"
        ],
    }


def install_passed(block: dict) -> bool:
    return (
        block.get("state") == "ran" and block["tests"] > 0 and block["expected"] == block["tests"]
    )


def build_summary(
    report_path: Path,
    specs_path: Path | None,
    expected: list[str] | None,
    label: str,
    known_path: Path,
    register_path: Path,
) -> dict:
    """The summary of one Playwright JSON report; refusals 31 raise, 32 and 40 return."""
    data, rows, counts = _report_rows(report_path)
    stats = data["stats"]
    files = sorted({r["file"] for r in rows})
    specs_checked = False
    if specs_path is not None:
        if not specs_path.is_file():
            raise Refusal("specs-mismatch", "specs.txt missing")
        listed = sorted(
            {
                ln.strip()
                for ln in specs_path.read_text(encoding="utf-8-sig").splitlines()
                if ln.strip()
            }
        )
        sets = {"specs.txt": listed}
        if expected is not None:
            sets["the commit's expected set"] = sorted(set(expected))
        diffs = []
        for name, other in sets.items():
            if other != files:
                only_r = sorted(set(files) - set(other))
                only_o = sorted(set(other) - set(files))
                diffs.append(f"report vs {name}: only in report {only_r}, only in {name} {only_o}")
        if diffs:
            raise Refusal("specs-mismatch", "; ".join(diffs))
        specs_checked = True
    known_data = load_known(known_path)
    entries = [e for e in known_data["known"] if e.get("label") == label]
    skip = label_skip(known_data, label)
    status_of = register_status(register_path) if entries else {}
    stale: list[str] = []
    matched: dict[int, dict] = {}
    for e in entries:
        hits = [
            i for i, r in enumerate(rows) if r["file"] == e.get("file") and r["ac"] == e.get("ac")
        ]
        if len(hits) != 1:
            stale.append(f"{e.get('ac')} in {e.get('file')} matches {len(hits)} test(s)")
        else:
            matched[hits[0]] = e
        if status_of.get(str(e.get("issue"))) != "open":
            stale.append(f"{e.get('issue')} (for {e.get('ac')}) is not open in the register")
    known: list[dict] = []
    passing: list[dict] = []
    new: list[dict] = []
    for i, r in enumerate(rows):
        item = {"file": r["file"], "ac": r["ac"], "title": r["title"]}
        if i in matched and r["status"] == "unexpected":
            known.append(item)
        elif i in matched and r["status"] == "expected":
            passing.append(item)
        elif r["status"] != "expected":
            new.append(dict(item, status=r["status"]))
    if stale:
        result = "known-failures-stale"
    elif new:
        result = "new-failures"
    else:
        result = "ok"
    duration = stats.get("duration", 0)
    return {
        "tests": len(rows),
        "expected": counts["expected"],
        "unexpected": counts["unexpected"],
        "flaky": counts["flaky"],
        "skipped": counts["skipped"],
        "spec_files": len(files),
        "specs_checked": specs_checked,
        "known": known,
        "known_now_passing": passing,
        "new": new,
        "skip": skip,
        "playwright_version": (data.get("config") or {}).get("version"),
        "duration_ms": int(duration) if isinstance(duration, (int, float)) else 0,
        "result": result,
        "exit": REASONS[result],
        "stale": stale,
    }


# --- the gated stage (Session 98) -----------------------------------------------------------

#: The session probe's states, in the order the run book names them.
PROBE_STATES = ("none", "connected", "undecided")
#: The gated stage's outcomes; only ``run`` can add to the exit code (L2, D-1283).
GATED_OUTCOMES = (
    "run",
    "skipped-connected",
    "skipped-undecided",
    "voided-connected-during",
    "voided-undecided-during",
)
_UTC_RE = re.compile(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d+))?(Z|[+-]\d\d:\d\d)?")


def _probe_reading(probe: object) -> dict | None:
    """The ``{state, reason}`` of one probe, or ``None`` when there is none."""
    if not isinstance(probe, dict):
        return None
    return {"state": probe.get("state"), "reason": probe.get("reason")}


def _parse_utc(text: object) -> datetime | None:
    """A round-trip (``'o'``) time with up to 7 fractional digits; ``None`` when unparseable."""
    m = _UTC_RE.fullmatch(str(text or ""))
    if not m:
        return None
    frac = (m.group(2) or "")[:6].ljust(6, "0")
    tz = m.group(3) or "Z"
    try:
        return datetime.fromisoformat(
            f"{m.group(1)}.{frac}{'+00:00' if tz == 'Z' else tz}"
        ).astimezone(UTC)
    except ValueError:
        return None


def _state_of(reading: object) -> str | None:
    return reading.get("state") if isinstance(reading, dict) else None


def gated_outcome(before: dict, after: dict | None, polls: list[dict]) -> tuple[str, str]:
    """The gated stage's outcome and reason from its probes (D-1269, D-1283, D-1284).

    A before probe that is not ``none`` skips the stage. Otherwise any reading that is not
    ``none`` from the after probe, or from a poll taken while ``stage`` was ``gated``, voids it;
    ``connected`` wins over ``undecided``. A poll taken during the main stage never voids. An
    after probe that is missing (``None``) reads ``undecided`` with the reason
    ``after-probe-missing``, and one with no probe state (``{}``, unreadable or an unknown
    state) reads ``undecided`` with ``after-probe-invalid``, so the stage is voided, never
    ``run`` (fail closed); an earlier gated poll's reading keeps its own reason.
    """
    state = _state_of(before)
    if state != "none":
        kind = "connected" if state == "connected" else "undecided"
        return f"skipped-{kind}", str(before.get("reason") if isinstance(before, dict) else "")
    readings = [
        p.get("session_probe") for p in polls if isinstance(p, dict) and p.get("stage") == "gated"
    ]
    if after is None:
        readings.append({"state": "undecided", "reason": "after-probe-missing"})
    elif _state_of(after) not in PROBE_STATES:
        readings.append({"state": "undecided", "reason": "after-probe-invalid"})
    else:
        readings.append(after)
    seen = [r for r in readings if _state_of(r) not in (None, "none")]
    for want in ("connected", None):
        for r in seen:
            if want is None or _state_of(r) == want:
                kind = "connected" if _state_of(r) == "connected" else "undecided"
                return f"voided-{kind}-during", str(r.get("reason"))
    return "run", str(before.get("reason"))


def _probe_detail(probe: dict | None) -> list[str]:
    """Each proc of a probe as ``<name> <switches> session=N started=<UTC> age_s=<seconds>``."""
    if not isinstance(probe, dict):
        return []
    at = _parse_utc(probe.get("utc"))
    out = []
    for p in probe.get("procs") or []:
        if not isinstance(p, dict):
            continue
        sw = p.get("switches")
        shown = "(unreadable)" if sw is None else (str(sw).strip() or "-")
        started = _parse_utc(p.get("started"))
        age = "-" if at is None or started is None else str(int((at - started).total_seconds()))
        out.append(
            f"{p.get('name')} {shown} session={p.get('session')} "
            f"started={p.get('started')} age_s={age}"
        )
    return out


def _polls_of(folder: Path) -> list[dict]:
    path = folder / "polls.jsonl"
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict):
            out.append(rec)
    return out


def gated_summary(host: Path, files: list[str], polls: list[dict]) -> dict:
    """The ``gated`` object of a run's summary; a missing before probe or report is 31.

    The gated report is never matched against the known list (D-1272). A missing or unreadable
    after probe is no refusal: ``gated_outcome`` voids the stage (D-1284), and the main stage's
    summary is unchanged.
    """
    pb_path = host / "probe-before.json"
    if not pb_path.is_file():
        raise Refusal("report-missing", str(pb_path))
    before = _read_json(pb_path)
    if _state_of(before) not in PROBE_STATES:
        raise Refusal("report-invalid", "probe-before.json has no probe state")
    pa_path = host / "probe-after.json"
    after = _read_json(pa_path) if pa_path.is_file() else None
    outcome, reason = gated_outcome(before, after, polls)
    counts = None
    failing: list[dict] = []
    if _state_of(before) == "none":
        _, rows, c = _report_rows(host / "gated" / "report.json")
        counts = {"tests": len(rows), **c}
        failing = [
            {"file": r["file"], "ac": r["ac"], "title": r["title"], "status": r["status"]}
            for r in rows
            if r["status"] != "expected"
        ]
    return {
        "outcome": outcome,
        "reason": reason,
        "files": list(files),
        "probe_before": before,
        "probe_after": after,
        "counts": counts,
        "new": failing if outcome == "run" else [],
        "detail": _probe_detail(before) + _probe_detail(after),
        "voided_failures": failing if outcome.startswith("voided-") else [],
    }


def summary_lines(s: dict) -> list[str]:
    lines = [
        f"summary: tests={s['tests']} expected={s['expected']} unexpected={s['unexpected']} "
        f"flaky={s['flaky']} skipped={s['skipped']} spec_files={s['spec_files']} "
        f"specs_checked={s['specs_checked']} playwright={s['playwright_version']} "
        f"duration_ms={s['duration_ms']}",
    ]
    lines += [f"known: {k['file']} {k['title']}" for k in s["known"]]
    lines += [f"known now passing: {k['file']} {k['title']}" for k in s["known_now_passing"]]
    lines += [f"new: {n['file']} [{n.get('status')}] {n['title']}" for n in s["new"]]
    lines += [f"stale: {x}" for x in s.get("stale", [])]
    lines += [f"skip: {e['file']} ({e['reason']})" for e in s["skip"]]
    g = s.get("gated")
    if g:
        c = g["counts"]
        shown = "-" if c is None else " ".join(f"{k}={c[k]}" for k in ("tests", *STATUSES))
        lines.append(
            f"gated: outcome={g['outcome']} reason={g['reason']} files={','.join(g['files'])} "
            f"counts={shown}"
        )
        for name in ("probe_before", "probe_after"):
            r = _probe_reading(g[name])
            if r is not None:
                lines.append(f"gated {name}: state={r['state']} reason={r['reason']}")
        lines += [f"gated new: {n['file']} [{n.get('status')}] {n['title']}" for n in g["new"]]
        lines += [
            f"gated voided: {n['file']} [{n.get('status')}] {n['title']}"
            for n in g["voided_failures"]
        ]
        lines += [f"gated detail: {d}" for d in g["detail"]]
    ib = s.get("install")
    if ib:
        if ib["state"] == "ran":
            lines.append(
                f"install: state=ran tests={ib['tests']} "
                + " ".join(f"{k}={ib[k]}" for k in STATUSES)
            )
            lines += [
                f"install failed: {n['file']} [{n['status']}] {n['title']}" for n in ib["failed"]
            ]
        else:
            lines.append(f"install: state={ib['state']} {ib.get('detail', '')}".rstrip())
    lines.append(f"result: {s['result']} exit={s['exit']}")
    return lines


#: The two summary receipts; an existing one of either is ``receipt-exists`` (``NO_PARTIAL``).
SUMMARY_NAMES = ("summary.json", "summary.txt")


def write_summary(folder: Path, s: dict) -> None:
    write_atomic(folder / "summary.json", _json_bytes(s))
    text = "\n".join(safe(ln) for ln in summary_lines(s)) + "\n"
    write_atomic(folder / "summary.txt", text.encode("ascii"))


def _summary_refusal(s: dict) -> Refusal | None:
    if s["result"] == "known-failures-stale":
        return Refusal("known-failures-stale", "; ".join(s["stale"]))
    if s["result"] == "new-failures":
        # A gated-stage failure counts as a main-stage one does (Session 98).
        new = s["new"] + ((s.get("gated") or {}).get("new") or [])
        names = "; ".join(f"{n['file']}: {n['title']}" for n in new)
        return Refusal("new-failures", f"{len(new)} new: {names}")
    if s["result"] == "install-failures":
        ib = s.get("install") or {}
        if ib.get("state") != "ran":
            return Refusal("install-failures", f"install stage {ib.get('state')}")
        if not ib["tests"]:
            return Refusal("install-failures", "the install stage ran no test")
        names = "; ".join(f"[{n['status']}] {n['title']}" for n in ib["failed"])
        return Refusal("install-failures", f"{len(ib['failed'])} not passed: {names}")
    return None


# --- run state ------------------------------------------------------------------------------


class RunState:
    def __init__(self) -> None:
        self.run_id: str | None = None
        self.dir: Path | None = None
        self.locked = False
        self.cfg: dict | None = None
        self.set_id: str | None = None

    def progress(self, text: str) -> None:
        if self.dir is None:
            return
        line = f"{iso(utcnow())} {safe(text)}\n"
        try:
            with open(self.dir / "progress.log", "a", encoding="ascii") as fh:
                fh.write(line)
        except OSError:
            pass


def release_lock(st: RunState) -> Refusal | None:
    """Release the run's host lock once; a failed release comes back as a ``Refusal``.

    The lock is then kept (``st.locked`` stays true) and the caller makes the failure part of
    the outcome (``NAMED_REFUSAL``), so a run never ends 0 with the lock held; a host-key failure
    is never retried.
    """
    if not st.locked or st.cfg is None or st.set_id is None or st.run_id is None:
        return None
    try:
        got = host_call(st.cfg, st.set_id, "host-release.ps1", "-RunId", st.run_id)
    except Refusal as e:
        st.progress(f"release failed: {e.reason}: {e.detail}")
        say(f"release failed: {e.reason}: {e.detail}")
        e.keep_lock = True
        e.hint = _release_hint(st.run_id)
        return e
    st.progress(f"released: {got.get('released')}")
    say(f"released: {got.get('released')}")
    st.locked = False
    return None


def _hint(run_id: str) -> str:
    return (
        f"the lock is kept; wait, then run: e2e_remote.py collect {run_id} "
        f"(or, to give the host back: e2e_remote.py release {run_id})"
    )


def _release_hint(run_id: str) -> str:
    return (
        f"the lock is kept; once the host answers (and, after host-key-failed, its key is "
        f"checked), give it back: e2e_remote.py release {run_id}"
    )


def _poll(cfg: dict, st: RunState) -> dict:
    assert st.run_id and st.dir and st.set_id
    start = utcnow()
    limit = timedelta(minutes=cfg["timeout_min"])
    fails = idle = n = 0
    while True:
        n += 1
        try:
            status = host_call(cfg, st.set_id, "host-status.ps1", "-RunId", st.run_id)
        except Refusal as e:
            if e.reason == "host-key-failed":
                e.keep_lock = True
                raise
            fails += 1
            st.progress(f"poll {n} failed ({fails} in a row): {e.reason}: {e.detail}")
            if fails >= 3:
                raise Refusal(
                    "ssh-failed",
                    f"3 polls in a row failed; last: {e.reason}: {e.detail}",
                    keep_lock=True,
                    hint=_hint(st.run_id),
                ) from e
        else:
            fails = 0
            problems = poll_overlap(status, cfg, st.run_id)
            t = status.get("task") or {}
            rec = {
                "poll": n,
                "utc": iso(utcnow()),
                "done": status.get("done"),
                "task_state": t.get("state"),
                "lock": (status.get("lock") or {}).get("run_id"),
                "user_session": status.get("user_session"),
                "logonui_sessions": status.get("logonui_sessions"),
                "busy": status.get("busy"),
                "runner_workers": status.get("runner_workers"),
                "own_orphans": status.get("own_orphans"),
                "problems": problems,
                "session_probe": _probe_reading(status.get("session_probe")),
                "stage": status.get("stage"),
            }
            try:
                with open(st.dir / "polls.jsonl", "a", encoding="ascii") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
            except OSError as exc:
                # The task may still be running: keep the lock and name collect and release.
                raise Refusal(
                    "receipt-write-failed",
                    f"polls.jsonl: {exc}",
                    keep_lock=True,
                    hint=_hint(st.run_id),
                ) from exc
            st.progress(f"poll {n}: done={status.get('done')} task={t.get('state')}")
            if status.get("done") is not None:
                return status
            idle = idle + 1 if t.get("state") != "Running" else 0
            if idle >= 2:
                raise Refusal(
                    "launcher-ended",
                    f"two polls in a row with the task {t.get('state')} and no DONE",
                    keep_lock=True,
                    hint=_hint(st.run_id),
                )
        if utcnow() - start >= limit:
            raise Refusal(
                "poll-timeout",
                f"no DONE {cfg['timeout_min']} min after the start",
                keep_lock=True,
                hint=_hint(st.run_id),
            )
        sleep(cfg["poll_s"])


def _overlap_from_polls(folder: Path) -> list[dict]:
    return [
        {"poll": rec.get("poll"), "utc": rec.get("utc"), "problems": rec["problems"]}
        for rec in _polls_of(folder)
        if rec.get("problems")
    ]


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def tool_hashes() -> dict[str, str]:
    out = {"tools/e2e_remote.py": sha256_file(Path(__file__))}
    for p in sorted(Path(HOST_DIR).iterdir()):
        if p.is_file() and p.suffix in (".ps1", ".json"):
            out[f"tools/e2e_host/{p.name}"] = sha256_file(p)
    return out


def _collect_and_summarize(cfg: dict, st: RunState, status: dict) -> int:
    """Steps 11 to 13: copy the results, map ``DONE``, summarize, release."""
    assert st.run_id and st.dir and st.set_id
    rd, run_id = st.dir, st.run_id
    existing = [p for p in (rd / "host", *(rd / n for n in SUMMARY_NAMES)) if p.exists()]
    if existing:
        raise Refusal("receipt-exists", str(existing[0]))
    req = _read_json(rd / "upload" / "runs" / run_id / "request.json")
    if not req.get("commit"):
        raise Refusal("request-missing", "upload/runs request.json")
    inc = unique_path(rd / "host.incoming")
    linc = unique_path(rd / "host-logs.incoming")
    remote = remote_root(cfg)
    scp(f"{remote}/results/{run_id}", str(inc), timeout=BUILD_TIMEOUT_S)
    scp(f"{remote}/runs/{run_id}/logs", str(linc), timeout=BUILD_TIMEOUT_S)
    inc.rename(rd / "host")
    linc.rename(rd / "host-logs")
    st.progress("collected host and host-logs")
    done = status.get("done")
    try:
        done = int((rd / "host" / "DONE").read_text(encoding="utf-8-sig").strip())
    except (OSError, ValueError):
        pass
    st.progress(f"DONE {done}")
    if done in DONE_MAP:
        raise Refusal(DONE_MAP[done], f"the launcher wrote DONE {done}")
    known_data = load_known(KNOWN_FILE)
    skip_files = {e["file"] for e in label_skip(known_data, cfg["label"])}
    gated_files = label_gated(known_data, cfg["label"])
    expected = [
        s for s in commit_specs(req["commit"]) if s not in skip_files and s not in gated_files
    ]
    s = build_summary(
        rd / "host" / "report.json",
        rd / "host" / "specs.txt",
        expected,
        cfg["label"],
        KNOWN_FILE,
        REGISTER,
    )
    gated = gated_summary(rd / "host", gated_files, _polls_of(rd)) if gated_files else None
    extract = _read_json(rd / "prepare-extract.json")
    facts = _read_json(rd / "facts.json")
    s.update(
        {
            "run_id": run_id,
            "commit": req.get("commit"),
            "label": cfg["label"],
            "done": done,
            "mtime_skew_s": extract.get("mtime_skew_s"),
            "commit_offset_s": extract.get("commit_offset_s"),
            "zip_sha256": req.get("zip_sha256"),
            "stub": req.get("stub"),
            "overlap": _overlap_from_polls(rd),
            "busy_users_missing": facts.get("busy_users_missing", []),
            "tool_sha256": tool_hashes(),
        }
    )
    if gated is not None:
        s["gated"] = gated
        if gated["new"] and s["result"] == "ok":
            s["result"] = "new-failures"
            s["exit"] = REASONS["new-failures"]
    # HOST_PAYLOAD (Session 106): the install stage's block; a main-stage reason comes first.
    s["install"] = install_block(rd / "host" / "install", "payload" in req)
    if "payload" in req and s["result"] == "ok" and not install_passed(s["install"]):
        s["result"] = "install-failures"
        s["exit"] = REASONS["install-failures"]
    for line in summary_lines(s):
        say(line)
    if s["overlap"]:
        say(f"overlap: {len(s['overlap'])} poll(s) saw another workload; see polls.jsonl")
    write_summary(rd, s)
    st.progress(f"summary: {s['result']} exit={s['exit']}")
    bad = _summary_refusal(s)
    if bad is not None:
        raise bad
    failed = release_lock(st)
    if failed is not None:
        # The summary stays as written; the failed release is the run's outcome (10 or 11).
        raise failed
    return 0


def _run(args: argparse.Namespace, st: RunState) -> int:
    cfg = load_config(config_path(args.config))
    st.cfg = cfg
    receipts = Path(args.receipts) if args.receipts else Path(RECEIPTS)
    # HOST_PAYLOAD: a bad folder is refused before any receipt, lock or upload.
    payload = read_payload(Path(args.payload)) if getattr(args, "payload", None) else None
    sha = resolve_commit(args.commit)
    epoch = int(git("log", "-1", "--format=%ct", sha).strip())
    major = node_major_of(sha)
    run_id = "r" + utcnow().strftime("%Y%m%dT%H%M%SZ") + "-" + sha[:7]
    st.run_id = run_id
    known_data = load_known(KNOWN_FILE)
    all_specs = commit_specs(sha)
    skip = label_skip(known_data, cfg["label"])
    for e in skip:
        if not e.get("reason") or e.get("file") not in all_specs:
            raise Refusal(
                "known-failures-stale",
                f"skip entry {e.get('file')} has no reason or names no spec file of {sha[:7]}",
            )
    # Only this label's gated entries are checked against the commit (Session 98).
    gated = _label_gated_entries(known_data, cfg["label"])
    skip_names = {e.get("file") for e in skip}
    for e in gated:
        if not e.get("reason") or e.get("file") not in all_specs:
            raise Refusal(
                "known-failures-stale",
                f"gated entry {e.get('file')} has no reason or names no spec file of {sha[:7]}",
            )
        if e.get("file") in skip_names:
            raise Refusal(
                "known-failures-stale",
                f"{e.get('file')} is both skipped and gated for {cfg['label']}",
            )
    if not all((Path(STUB_DIR) / n).is_file() for n in STUB_NAMES):
        raise Refusal("prerequisite-missing", "picker-stub-local")
    receipts.mkdir(parents=True, exist_ok=True)
    rd = receipts / run_id
    try:
        rd.mkdir()
    except FileExistsError as exc:
        raise Refusal("receipt-exists", str(rd)) from exc
    st.dir = rd
    st.progress(f"run {run_id} commit {sha} epoch {epoch} node {major}")
    up = rd / "upload" / "runs" / run_id
    up.mkdir(parents=True)
    zp = up / "src.zip"
    archive(sha, zp)
    with zipfile.ZipFile(zp) as z:
        comment = z.comment.decode("ascii", "replace")
    if comment != sha:
        raise Refusal("commit-mismatch", f"zip comment {comment[:40]!r} is not {sha}")
    zip_sha = sha256_file(zp)
    pub = up / "publish"
    pub.mkdir()
    stub = {}
    for n in STUB_NAMES:
        shutil.copyfile(Path(STUB_DIR) / n, pub / n)
        stub[n] = sha256_file(pub / n)
    request = {
        "run_id": run_id,
        "commit": sha,
        "commit_epoch": epoch,
        "zip_sha256": zip_sha,
        "stub": stub,
        "skip": [e["file"] for e in skip],
        "gated": [e["file"] for e in gated],
        "node_exe": cfg["node_exe"],
        "ffmpeg_bin": cfg["ffmpeg_bin"],
        "user": cfg["user"],
        "created_utc": iso(utcnow()),
    }
    if payload is not None:
        (up / "payload").mkdir()
        for src, entry in payload:
            shutil.copyfile(src, up / "payload" / entry["name"])
            if sha256_file(up / "payload" / entry["name"]) != entry["sha256"]:
                raise Refusal("payload-invalid", f"{entry['name']} changed while copying")
        request["payload"] = [e for _, e in payload]
    write_atomic(up / "request.json", _json_bytes(request))
    st.progress(f"archive {zip_sha}")
    st.set_id = stage(cfg, rd)
    st.progress(f"staged set {st.set_id}")
    facts = host_call(cfg, st.set_id, "host-facts.ps1", save=rd / "facts.json")
    for line in fact_lines(facts):
        say(line)
    reasons = evaluate(facts, cfg, major)
    if reasons:
        raise Refusal(reasons[0][0], reasons[0][1], also=reasons[1:])
    host_call(cfg, st.set_id, "host-lock.ps1", "-RunId", run_id, "-Commit", sha)
    st.locked = True
    st.progress("locked")
    scp(str(rd / "upload" / "runs"), remote_root(cfg) + "/", timeout=BUILD_TIMEOUT_S)
    st.progress("uploaded")
    for name in STAGES:
        got = host_call(
            cfg,
            st.set_id,
            "host-prepare.ps1",
            "-RunId",
            run_id,
            "-Stage",
            name,
            timeout=BUILD_TIMEOUT_S if name == "build" else STEP_TIMEOUT_S,
            save=rd / f"prepare-{name}.json",
        )
        st.progress(f"prepare {name}: {got.get('reason')}")
    host_call(cfg, st.set_id, "host-start.ps1", "-RunId", run_id)
    st.progress("started")
    status = _poll(cfg, st)
    return _collect_and_summarize(cfg, st, status)


def _collect(args: argparse.Namespace, st: RunState) -> int:
    if not RUN_ID_RE.fullmatch(args.run_id or ""):
        raise Refusal("usage", "RUN_ID must look like r<yyyyMMddTHHmmssZ>-<sha7>")
    cfg = load_config(config_path(args.config))
    st.cfg = cfg
    st.run_id = args.run_id
    receipts = Path(args.receipts) if args.receipts else Path(RECEIPTS)
    rd = receipts / args.run_id
    if not rd.is_dir():
        raise Refusal("request-missing", f"no run folder {rd}")
    st.dir = rd
    st.progress("collect")
    st.set_id = stage(cfg, rd)
    status = host_call(cfg, st.set_id, "host-status.ps1", "-RunId", args.run_id)
    if status.get("done") is None:
        raise Refusal(
            "poll-timeout",
            "the host has no DONE for this run yet",
            keep_lock=True,
            hint=_hint(args.run_id),
        )
    st.locked = True
    return _collect_and_summarize(cfg, st, status)


def _with_run(fn, args: argparse.Namespace) -> int:
    st = RunState()
    reason, code = "ok", 0
    try:
        code = fn(args, st)
    except Refusal as e:
        if not e.keep_lock and e.reason != "host-key-failed":
            # The refusal stays the outcome; a failed release is added under ``also``.
            failed = release_lock(st)
            if failed is not None:
                e.also.append((failed.reason, failed.detail))
                e.hint = e.hint or failed.hint
        reason, code = e.reason, e.code
        print_refusal(e)
        if st.dir is not None:
            st.progress(f"refused: {e.reason}: {e.detail}")
            body = {
                "reason": e.reason,
                "detail": e.detail,
                "exit": e.code,
                "run_id": st.run_id,
                "also": [list(x) for x in e.also],
                "lock_kept": bool(st.locked),
                "utc": iso(utcnow()),
            }
            try:
                write_atomic(unique_path(st.dir / "refusal.json"), _json_bytes(body))
            except Refusal as w:
                say(f"refusal.json not written: {w.detail}")
    say(
        f"e2e-remote: {reason} exit={code} run={st.run_id or 'none'} "
        f"receipts={st.dir if st.dir is not None else 'none'}"
    )
    return code


# --- the other subcommands ------------------------------------------------------------------


def _check(args: argparse.Namespace) -> int:
    cfg = load_config(config_path(args.config))
    out = Path(args.out) if args.out else None
    if out is not None and out.exists():
        raise Refusal("receipt-exists", str(out))
    major = node_major_of("HEAD")
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        scratch = Path(tempfile.mkdtemp(prefix=out.name + ".stage-", dir=out.parent))
        set_id = stage(cfg, scratch)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            set_id = stage(cfg, Path(tmp))
    facts = host_call(cfg, set_id, "host-facts.ps1")
    for line in fact_lines(facts):
        say(line)
    reasons = evaluate(facts, cfg, major)
    code = REASONS[reasons[0][0]] if reasons else 0
    if out is not None:
        body = {
            "facts": facts,
            "reasons": [{"reason": r, "detail": d} for r, d in reasons],
            "exit": code,
            "set": set_id,
        }
        try:
            with open(out, "xb") as fh:
                fh.write(_json_bytes(body))
        except FileExistsError as exc:
            raise Refusal("receipt-exists", str(out)) from exc
        except OSError as exc:
            raise Refusal("receipt-write-failed", f"{out.name}: {exc}") from exc
    for r, d in reasons:
        say(f"refused: {r}: {d}")
    if not reasons:
        say("check: ok")
    return code


def _release(args: argparse.Namespace) -> int:
    if not RUN_ID_RE.fullmatch(args.run_id or ""):
        raise Refusal("usage", "RUN_ID must look like r<yyyyMMddTHHmmssZ>-<sha7>")
    cfg = load_config(config_path(args.config))
    with tempfile.TemporaryDirectory() as tmp:
        set_id = stage(cfg, Path(tmp))
    got = host_call(cfg, set_id, "host-release.ps1", "-RunId", args.run_id)
    say(f"released: {got.get('released')}")
    return 0


def _summarize(args: argparse.Namespace) -> int:
    out = Path(args.out) if args.out else None
    if out is not None:
        for name in SUMMARY_NAMES:
            if (out / name).exists():
                raise Refusal("receipt-exists", str(out / name))
        out.mkdir(parents=True, exist_ok=True)
    s = build_summary(
        Path(args.report),
        Path(args.specs) if args.specs else None,
        None,
        args.label,
        Path(args.known) if args.known else Path(KNOWN_FILE),
        Path(args.register) if args.register else Path(REGISTER),
    )
    for line in summary_lines(s):
        say(line)
    if out is not None:
        write_summary(out, s)
    bad = _summary_refusal(s)
    if bad is not None:
        raise bad
    return 0


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise Refusal("usage", message)


def _parser() -> argparse.ArgumentParser:
    p = _Parser(prog="e2e_remote.py", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True, parser_class=_Parser)
    c = sub.add_parser("check", help="stage the host scripts and read the host's facts")
    c.add_argument("--config")
    c.add_argument("--out")
    r = sub.add_parser("run", help="run the suite on the host for one commit")
    r.add_argument("commit")
    r.add_argument("--config")
    r.add_argument("--receipts")
    r.add_argument("--payload", help="a flat folder of payload.json and installers (Session 106)")
    k = sub.add_parser("collect", help="collect and summarize a run that timed out")
    k.add_argument("run_id")
    k.add_argument("--config")
    k.add_argument("--receipts")
    x = sub.add_parser("release", help="release the host lock a run holds")
    x.add_argument("run_id")
    x.add_argument("--config")
    s = sub.add_parser("summarize", help="summarize a Playwright JSON report offline")
    s.add_argument("report")
    s.add_argument("--label", required=True)
    s.add_argument("--specs")
    s.add_argument("--known")
    s.add_argument("--register")
    s.add_argument("--out")
    return p


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
    except Refusal as e:
        print_refusal(e)
        return e.code
    except SystemExit as e:
        return int(e.code or 0)
    if args.cmd == "run":
        return _with_run(_run, args)
    if args.cmd == "collect":
        return _with_run(_collect, args)
    handler = {"check": _check, "release": _release, "summarize": _summarize}[args.cmd]
    try:
        return handler(args)
    except Refusal as e:
        print_refusal(e)
        return e.code


if __name__ == "__main__":
    sys.exit(main())
