"""The second-host E2E tool (Session 96, AC-1 to AC-15, AC-19 and AC-21;
docs/execution/plans/2026-11-18-e2e-remote-host).

Every CLI case runs ``main`` with ``run_cmd``, ``archive``, ``sleep`` and ``utcnow`` replaced by
the ``Fake`` recorder: it answers ``ssh`` and ``scp`` from scripted results keyed by host script
name and passes ``git`` to the real one, so a run binds the real HEAD. ``HOST_DIR``, ``STUB_DIR``,
``KNOWN_FILE``, ``REGISTER`` and ``RECEIPTS`` point at ``tmp_path``. The host-script cases
(AC-15) run real Windows PowerShell 5.1 under an outer ``powershell.exe -c``, as the host's sshd
does, on fixture roots under ``tmp_path``. No case reaches a network host or reads user data.
Each case asserts its target file exists first, so before Green every case fails by assertion.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/e2e_remote.py"
HOST = ROOT / "tools/e2e_host"
EXAMPLE = HOST / "e2e-host.example.json"
KNOWN = HOST / "known-failures.json"
RUN_BOOK = ROOT / ".agent/docs/e2e-remote-host.md"
SCRIPTS = (
    "host-facts.ps1",
    "host-lock.ps1",
    "host-prepare.ps1",
    "host-release.ps1",
    "host-start.ps1",
    "host-status.ps1",
    "run-e2e.ps1",
)
BUSY_COPIES = ("host-facts.ps1", "host-lock.ps1", "host-start.ps1", "host-status.ps1")
STUB_NAMES = (
    "avkit-region-picker-stub.exe",
    "avkit-region-picker-stub.dll",
    "avkit-region-picker-stub.deps.json",
    "avkit-region-picker-stub.runtimeconfig.json",
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
SUBCOMMANDS = ("check", "run", "collect", "release", "summarize")
ON_WINDOWS = sys.platform == "win32"
WINDOWS_ONLY = "Windows PowerShell 5.1 runs only on Windows"
T0 = datetime(2026, 11, 18, 12, 0, 0, tzinfo=UTC)
LABEL = "test-host"
OTHER_RUN = "r20261118T110000Z-abcdef0"
OTHER_SHA = "0123456789abcdef0123456789abcdef01234567"
CFG = {
    "host": "e2e-host",
    "user": "tester",
    "label": LABEL,
    "root": "C:\\e2e-root",
    "task": "\\example\\e2e-task",
    "node_exe": "C:\\Program Files\\nodejs\\node.exe",
    "ffmpeg_bin": "C:\\e2e-root\\ffmpeg\\bin",
    "busy_users": ["ci-runner"],
    "min_free_gb": 20,
    "poll_s": 30,
    "timeout_min": 110,
}
#: Host-key bypasses and stored credentials no argv and no tool line may hold (AC-2, AC-14).
BYPASS = (
    "StrictHostKeyChecking=no",
    "StrictHostKeyChecking=off",
    "accept-new",
    "UserKnownHostsFile",
    "IdentityFile",
    "sshpass",
    "Password",
)
#: Stop and task-change words no argv the tool sends may hold (AC-5).
STOP_WORDS = (
    "Stop-Process",
    "taskkill",
    "Stop-ScheduledTask",
    "Register-ScheduledTask",
    "Set-ScheduledTask",
    "Unregister-ScheduledTask",
    "Disable-ScheduledTask",
)
#: Tokens no host script may hold (AC-14); ``kill`` is checked as a word on its own.
HOST_BANNED = (
    "Stop-Process",
    "spps",
    "taskkill",
    ".Kill(",
    "Stop-Job",
    "Restart-Computer",
    "schtasks",
    "Invoke-WebRequest",
    "Set-ItemProperty",
    "Stop-ScheduledTask",
    "Register-ScheduledTask",
    "Set-ScheduledTask",
    "Unregister-ScheduledTask",
    "Disable-ScheduledTask",
    "Install-",
    "winget",
    "choco",
    "msiexec",
    "Set-ExecutionPolicy",
)
#: Built from parts so this file holds none of the strings AC-21 scans for.
HOME_WIN = "C:" + "\\" + "Users"
HOME_POSIX = "/" + "Users" + "/"
SSH_DIRS = (".ssh" + "\\", ".ssh" + "/")
IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")


# --- loading and fixtures -------------------------------------------------------------------


def _load() -> ModuleType:
    assert TOOL.is_file(), "tools/e2e_remote.py does not exist yet"
    spec = importlib.util.spec_from_file_location("e2e_remote_under_test", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=True,
        stdin=subprocess.DEVNULL,
    ).stdout.strip()


def head() -> str:
    return _git("rev-parse", "HEAD")


def head_specs() -> list[str]:
    names = _git("ls-tree", "--name-only", "HEAD", "ui/tests/e2e/").splitlines()
    return sorted(
        n.rsplit("/", 1)[-1] for n in names if n.endswith(".test.ts") or n.endswith(".spec.ts")
    )


def node_major() -> int:
    return int((ROOT / ".node-version").read_text(encoding="utf-8").strip().split(".")[0])


def run_id_for(sha: str) -> str:
    return "r" + T0.strftime("%Y%m%dT%H%M%SZ") + "-" + sha[:7]


def facts(**over: object) -> dict:
    f: dict = {
        "reason": "ok",
        "schema": 1,
        "ps_version": "5.1",
        "elevated": True,
        "procs_total": 160,
        "owners_seen": 140,
        "busy": [],
        "own_orphans": [],
        "runner_workers": [],
        "busy_users_missing": [],
        "explorer": [{"session": 1, "user": "HOSTPC\\tester"}],
        "logonui_sessions": [],
        "user_session": {"id": 1, "state": "Active"},
        "task": {
            "exists": True,
            "state": "Ready",
            "principal": "tester",
            "logon": "Interactive",
            "runlevel": "Limited",
            "action_exe": "powershell.exe",
            "action_args": "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden "
            "-File C:\\e2e-root\\run-e2e.ps1",
            "limit_min": 120,
            "multiple": "IgnoreNew",
        },
        "lock": None,
        "launcher": {"exists": True, "sha256": "ab" * 32, "marker": False},
        "node": {"exists": True, "version": f"v{node_major()}.13.0"},
        "uv": True,
        "vcruntime": True,
        "ffmpeg": True,
        "ffprobe": True,
        "free_gb": 400.0,
        "tz_offset_min": -480,
        "utc_now": "2026-11-18T12:00:00.0000000Z",
        "ssh_shell": "powershell.exe",
    }
    f.update(over)
    return f


def task(**over: object) -> dict:
    t = dict(facts()["task"])
    t.update(over)
    return t


def lock_of(run_id: str, sha: str) -> dict:
    return {"run_id": run_id, "commit": sha, "set": "0123456789ab", "created_utc": "x"}


START = "2026-11-18T12:01:00.0000000Z"


def healthy_status(run_id: str, sha: str, done: int | None = 1) -> dict:
    s = facts()
    for k in ("launcher", "node", "uv", "vcruntime", "ffmpeg", "ffprobe", "free_gb"):
        s.pop(k)
    s["task"] = task(state="Running" if done is None else "Ready")
    s.update(
        {
            "last_result": 0,
            "done": done,
            "lock": lock_of(run_id, sha),
            "pid_file": {"pid": 4100, "start": START},
            "user_procs": [
                {"pid": 4100, "ppid": 900, "name": "node", "created": START},
                {"pid": 4200, "ppid": 4100, "name": "node", "created": "2026-11-18T12:01:05.0Z"},
                {
                    "pid": 4300,
                    "ppid": 4200,
                    "name": "electron",
                    "created": "2026-11-18T12:01:09.0Z",
                },
                {
                    "pid": 4301,
                    "ppid": 4300,
                    "name": "electron",
                    "created": "2026-11-18T12:01:10.0Z",
                },
            ],
            "own_orphans": [
                {
                    "user": "HOSTPC\\tester",
                    "name": "node",
                    "pid": 4100,
                    "ppid": 900,
                    "created": START,
                },
                {
                    "user": "HOSTPC\\tester",
                    "name": "node",
                    "pid": 4200,
                    "ppid": 4100,
                    "created": "2026-11-18T12:01:05.0Z",
                },
                {
                    "user": "HOSTPC\\tester",
                    "name": "electron",
                    "pid": 4300,
                    "ppid": 4200,
                    "created": "2026-11-18T12:01:09.0Z",
                },
            ],
        }
    )
    return s


def report(
    rows: list[tuple[str, str, str]],
    stats: dict | None = None,
    errors: list | None = None,
) -> dict:
    """A Playwright JSON report; every second spec sits in a nested describe suite."""
    suites: dict[str, dict] = {}
    for i, (f, title, status) in enumerate(rows):
        suite = suites.setdefault(
            f,
            {
                "title": f,
                "file": f,
                "line": 0,
                "column": 0,
                "specs": [],
                "suites": [{"title": "group", "file": f, "line": 1, "column": 1, "specs": []}],
            },
        )
        spec = {
            "title": title,
            "ok": status != "unexpected",
            "tags": [],
            "tests": [{"status": status, "results": []}],
            "id": f"id{i}",
            "file": f,
            "line": i + 1,
            "column": 1,
        }
        (suite["suites"][0]["specs"] if i % 2 else suite["specs"]).append(spec)
    st = {"startTime": "2026-11-18T12:02:00.000Z", "duration": 1234.5}
    for k in ("expected", "unexpected", "flaky", "skipped"):
        st[k] = sum(1 for r in rows if r[2] == k)
    st.update(stats or {})
    return {
        "config": {"version": "1.64.1"},
        "suites": list(suites.values()),
        "errors": errors or [],
        "stats": st,
    }


REGISTER_TEXT = (
    "version: 1\n"
    "issues:\n"
    "  - id: TEST-ISSUE-A\n"
    "    status: open\n"
    "  - id: TEST-ISSUE-B\n"
    "    status: resolved\n"
)


def known_file(
    path: Path,
    known: list[tuple[str, str, str]],
    skip: tuple[str, ...] | list[str] = (),
    label: str = LABEL,
) -> Path:
    data = {
        "known": [{"label": label, "file": f, "ac": ac, "issue": i} for f, ac, i in known]
        + [{"label": "other-host", "file": "nowhere.test.ts", "ac": "AC-1.1", "issue": "X"}],
        "skip": [{"label": label, "file": f, "reason": "fixture"} for f in skip]
        + [{"label": "other-host", "file": "nowhere.test.ts", "reason": "fixture"}],
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


class Result:
    def __init__(self, code: int, out: str = "", err: str = "") -> None:
        self.code, self.out, self.err = code, out, err


def jline(obj: dict, code: int = 0, out_before: str = "", err: str = "") -> Result:
    return Result(code, out_before + json.dumps(obj) + "\n", err)


def arg_after(argv: list[str], flag: str) -> str:
    return argv[argv.index(flag) + 1]


class Fake:
    """Recorder for every ``ssh``/``scp`` argv; ``git`` goes to the real ``run_cmd``."""

    def __init__(self, m: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp: Path) -> None:
        self.m = m
        self.tmp = tmp
        self.calls: list[list[str]] = []
        self.results: dict[str, list] = {}
        self.now = T0
        self.zip_comment: str | None = None
        self.real = m.run_cmd
        self.sha = head()
        self.run_id = run_id_for(self.sha)
        host_dir = tmp / "e2e_host"
        host_dir.mkdir()
        for n in SCRIPTS:
            (host_dir / n).write_bytes(b"# fixture " + n.encode() + b"\n")
        stub = tmp / "stub"
        stub.mkdir()
        for n in STUB_NAMES:
            (stub / n).write_bytes(b"stub " + n.encode())
        self.receipts = tmp / "receipts"
        all_specs = head_specs()
        self.skip = [all_specs[-1]]
        self.specs = [s for s in all_specs if s not in self.skip]
        self.known = known_file(
            tmp / "known.json", [(self.specs[0], "AC-901.1", "TEST-ISSUE-A")], self.skip
        )
        self.register = tmp / "register.yaml"
        self.register.write_text(REGISTER_TEXT, encoding="utf-8")
        monkeypatch.setattr(m, "run_cmd", self.run_cmd)
        monkeypatch.setattr(m, "archive", self.archive)
        monkeypatch.setattr(m, "sleep", self.sleep)
        monkeypatch.setattr(m, "utcnow", lambda: self.now)
        monkeypatch.setattr(m, "HOST_DIR", host_dir)
        monkeypatch.setattr(m, "STUB_DIR", stub)
        monkeypatch.setattr(m, "RECEIPTS", self.receipts)
        monkeypatch.setattr(m, "KNOWN_FILE", self.known)
        monkeypatch.setattr(m, "REGISTER", self.register)
        self.cfg = self.write_cfg()
        rows = [(f, f"AC-900.{i} case", "expected") for i, f in enumerate(self.specs)]
        rows.append((self.specs[0], "AC-901.1 known failure", "unexpected"))
        self.host_results = tmp / "host-results"
        self.set_results(report(rows), "\n".join(self.specs) + "\n", "1")

    def write_cfg(self, **over: object) -> str:
        cfg = dict(CFG)
        cfg.update(over)
        path = self.tmp / "e2e-host.json"
        path.write_text(json.dumps(cfg), encoding="utf-8")
        return str(path)

    def set_results(self, rep: dict | None, specs: str | None, done: str) -> None:
        if self.host_results.exists():
            shutil.rmtree(self.host_results)
        self.host_results.mkdir()
        if rep is not None:
            (self.host_results / "report.json").write_text(json.dumps(rep), encoding="utf-8")
        if specs is not None:
            (self.host_results / "specs.txt").write_text(specs, encoding="utf-8")
        (self.host_results / "DONE").write_text(done, encoding="ascii")
        (self.host_results / "run.log").write_text("999 passed\n", encoding="ascii")

    def sleep(self, s: float) -> None:
        self.now = self.now + timedelta(seconds=s)

    def archive(self, commit: str, out_path: object) -> None:
        out = Path(str(out_path))
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w") as z:
            z.comment = (self.zip_comment or commit).encode("ascii")
            z.writestr("ui/package.json", "{}")

    def key(self, argv: list[str]) -> str:
        if argv[0] == "scp":
            src = argv[-2]
            if src.startswith(CFG["host"] + ":"):
                return "scp-results" if "/results/" in src else "scp-logs"
            return "scp-upload" if Path(src).name == "runs" else "scp-stage"
        script = arg_after(argv, "-File").rsplit("\\", 1)[-1]
        if "-Stage" in argv:
            return script + " " + arg_after(argv, "-Stage")
        return script

    def answer(self, key: str, argv: list[str]) -> Result:
        for k in (key, key.split(" ")[0]):
            if k in self.results:
                q = self.results[k]
                r = q.pop(0) if len(q) > 1 else q[0]
                if callable(r):
                    return r(argv)
                if isinstance(r, dict):
                    return jline(r)
                return r
        return self.default(key, argv)

    def default(self, key: str, argv: list[str]) -> Result:
        if key in ("scp-stage", "scp-upload"):
            return Result(0)
        if key == "scp-results":
            shutil.copytree(self.host_results, argv[-1])
            return Result(0)
        if key == "scp-logs":
            Path(argv[-1]).mkdir(parents=True)
            (Path(argv[-1]) / "build-1-uv-sync.log").write_text("ok", encoding="ascii")
            return Result(0)
        script = key.split(" ")[0]
        if script == "host-facts.ps1":
            return jline(facts())
        if script == "host-lock.ps1":
            return jline({"reason": "ok", "lock": lock_of(arg_after(argv, "-RunId"), self.sha)})
        if script == "host-prepare.ps1":
            return jline(
                {
                    "reason": "ok",
                    "stage": arg_after(argv, "-Stage"),
                    "mtime_skew_s": 10800,
                    "commit_offset_s": 10800,
                }
            )
        if script == "host-start.ps1":
            return jline({"reason": "ok", "state": "Running"})
        if script == "host-status.ps1":
            return jline(healthy_status(arg_after(argv, "-RunId"), self.sha))
        if script == "host-release.ps1":
            return jline({"reason": "ok", "released": arg_after(argv, "-RunId")})
        raise AssertionError(f"unexpected call {argv}")

    def run_cmd(self, argv: list[str], timeout: float | None = None) -> object:
        argv = [str(a) for a in argv]
        if argv[0] == "git":
            return self.real(argv, timeout=timeout)
        self.calls.append(argv)
        r = self.answer(self.key(argv), argv)
        return self.m.Result(r.code, r.out, r.err)

    def scripts_called(self) -> list[str]:
        return [self.key(c) for c in self.calls]

    def released(self) -> list[str]:
        return [arg_after(c, "-RunId") for c in self.calls if self.key(c) == "host-release.ps1"]

    def run(self, *extra: str, sha: str | None = None) -> int:
        return self.m.main(["run", sha or self.sha, "--config", self.cfg, *extra])

    def check(self, *extra: str) -> int:
        return self.m.main(["check", "--config", self.cfg, *extra])

    @property
    def run_dir(self) -> Path:
        return self.receipts / self.run_id


@pytest.fixture
def env_clean(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AVKIT_E2E_HOST_CONFIG", raising=False)


def new_fake(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Fake:
    m = _load()
    return Fake(m, monkeypatch, tmp_path)


def assert_pinned(fake: Fake) -> None:
    opts = fake.m.SSH_OPTS
    assert opts == ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes"]
    assert fake.calls, "no ssh or scp call was recorded"
    for argv in fake.calls:
        assert argv[0] in ("ssh", "scp"), argv
        assert argv[1:5] == opts, argv
        if argv[0] == "ssh":
            assert argv[5] == CFG["host"], argv
        assert "-i" not in argv, argv
        for word in BYPASS + STOP_WORDS:
            assert not any(word.lower() in a.lower() for a in argv), (word, argv)


def summary_of(path: Path) -> dict:
    return json.loads((path / "summary.json").read_text(encoding="utf-8"))


# --- AC-1: the local config -----------------------------------------------------------------


def test_ac_1_config_missing_file(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    code = fake.m.main(["check", "--config", str(tmp_path / "absent.json")])
    assert code == 2
    assert "config-missing" in capsys.readouterr().out
    assert fake.calls == []


@pytest.mark.parametrize("key", CONFIG_KEYS)
def test_ac_1_config_each_key_required(tmp_path, monkeypatch, capsys, key, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    cfg = dict(CFG)
    cfg.pop(key)
    Path(fake.cfg).write_text(json.dumps(cfg), encoding="utf-8")
    assert fake.check() == 2
    assert f"config-invalid: {key}" in capsys.readouterr().out
    assert fake.calls == []


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("root", 'C:\\e2e"root'),
        ("user", "te$ter"),
        ("root", HOME_WIN + "\\someone\\e2e"),
        ("host", "e2e host"),
        ("timeout_min", 200),
        ("busy_users", ["ok", "bad;name"]),
        ("ffmpeg_bin", "C:\\e2e-root\\ff|bin"),
        ("task", "no-leading-backslash"),
        ("poll_s", True),
        ("min_free_gb", 2),
    ],
)
def test_ac_1_config_bad_value(tmp_path, monkeypatch, capsys, key, value, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.write_cfg(**{key: value})
    assert fake.check() == 2
    assert f"config-invalid: {key}" in capsys.readouterr().out
    assert fake.calls == []


@pytest.mark.parametrize("extra", ["skip_specs", "password_file"])
def test_ac_1_config_unknown_key(tmp_path, monkeypatch, capsys, extra, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.write_cfg(**{extra: ["x"]})
    assert fake.check() == 2
    assert f"config-invalid: {extra}" in capsys.readouterr().out
    assert fake.calls == []


def test_ac_1_config_not_an_object(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    Path(fake.cfg).write_text("[1, 2", encoding="utf-8")
    assert fake.check() == 2
    assert "config-invalid" in capsys.readouterr().out
    assert fake.calls == []


def test_ac_1_config_lookup_order(tmp_path, monkeypatch, env_clean):
    m = _load()
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", lambda: home)
    assert Path(m.config_path(None)) == home / ".config/av-kit/e2e-host.json"
    monkeypatch.setenv("AVKIT_E2E_HOST_CONFIG", str(tmp_path / "env.json"))
    assert Path(m.config_path(None)) == tmp_path / "env.json"
    assert Path(m.config_path(str(tmp_path / "arg.json"))) == tmp_path / "arg.json"


def test_ac_1_config_example_loads_clean(env_clean):
    m = _load()
    assert EXAMPLE.is_file(), "tools/e2e_host/e2e-host.example.json does not exist yet"
    cfg = m.load_config(EXAMPLE)
    assert cfg["host"] == "e2e-host"
    assert cfg["user"] == "tester"
    assert cfg["label"] == "example-host"
    assert cfg["root"] == "C:\\e2e-root"
    assert cfg["task"] == "\\example\\e2e-task"
    assert cfg["busy_users"] == ["ci-runner"]
    assert (cfg["min_free_gb"], cfg["poll_s"], cfg["timeout_min"]) == (20, 30, 110)
    assert sorted(json.loads(EXAMPLE.read_text(encoding="utf-8"))) == sorted(CONFIG_KEYS)


# --- AC-2: pinned SSH and result parsing ----------------------------------------------------


def test_ac_2_pinned_ssh_full_run(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    code = fake.run()
    out = capsys.readouterr().out
    assert code == 0, out
    assert_pinned(fake)
    last = out.strip().splitlines()[-1]
    assert last.startswith(f"e2e-remote: ok exit=0 run={fake.run_id} receipts="), last
    assert summary_of(fake.run_dir)["exit"] == 0
    called = fake.scripts_called()
    for script in (
        "host-facts.ps1",
        "host-lock.ps1",
        "host-prepare.ps1 verify",
        "host-prepare.ps1 extract",
        "host-prepare.ps1 build",
        "host-prepare.ps1 stale",
        "host-start.ps1",
        "host-status.ps1",
        "host-release.ps1",
    ):
        assert script in called, (script, called)
    assert all(
        re.fullmatch(r"[0-9A-Za-z-]+", a) for c in fake.calls if c[0] == "ssh" for a in c[13:]
    )


def test_ac_2_pinned_ssh_host_key_failure(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["scp-stage"] = [Result(255, "", "Host key verification failed.\r\n")]
    assert fake.check() == 11
    assert "host-key-failed" in capsys.readouterr().out
    assert len(fake.calls) == 1


def test_ac_2_pinned_ssh_changed_host_key(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [
        Result(255, "", "@@@ WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED! @@@\n")
    ]
    assert fake.check() == 11
    assert len(fake.calls) == 2


def test_ac_2_pinned_ssh_other_255(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [Result(255, "", "ssh: connect to host port 22: timed out\n")]
    assert fake.check() == 10
    assert "ssh-failed" in capsys.readouterr().out
    assert len(fake.calls) == 2


def test_ac_2_pinned_ssh_noise_is_ignored(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    err = (
        "** WARNING: connection is not using a post-quantum key exchange algorithm.\n"
        "** This session may be vulnerable to attacks.\n"
        "** The server may need to be upgraded.\n"
    )
    before = '#< CLIXML\n<Objs Version="1.1.' + '0.1"><Obj S="progress" RefId="0"/></Objs>\n\n'
    fake.results["host-facts.ps1"] = [jline(facts(), 0, before, err)]
    assert fake.check() == 0, capsys.readouterr().out


@pytest.mark.parametrize("code", [0, 1])
def test_ac_2_pinned_ssh_reason_decides(tmp_path, monkeypatch, capsys, code, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-lock.ps1"] = [
        jline({"reason": "host-locked", "detail": f"holder={OTHER_RUN}"}, code)
    ]
    assert fake.run() == 23
    assert OTHER_RUN in capsys.readouterr().out


def test_ac_2_pinned_ssh_ok_reason_with_exit_1(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [jline(facts(), 1)]
    assert fake.check() == 0


def test_ac_2_pinned_ssh_no_result_line(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [Result(1, "some text\nnot json\n", "")]
    assert fake.check() == 10
    assert "no-result" in capsys.readouterr().out


def test_ac_2_pinned_ssh_unknown_reason(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [jline({"reason": "made-up-reason"}, 1)]
    assert fake.check() == 10
    assert "made-up-reason" in capsys.readouterr().out


def test_ac_2_pinned_ssh_run_cmd_stdin(monkeypatch):
    m = _load()
    seen: dict = {}

    class Done:
        returncode = 0
        stdout = b"out"
        stderr = b""

    def fake_run(argv, **kw):
        seen.update(kw)
        seen["argv"] = argv
        return Done()

    monkeypatch.setattr(m.subprocess, "run", fake_run)
    r = m.run_cmd(["ssh", "x"], timeout=5)
    assert seen["stdin"] is subprocess.DEVNULL
    assert seen["argv"] == ["ssh", "x"]
    assert (r.code, r.out) == (0, "out")


def refusal_of(fake: Fake) -> dict:
    return json.loads((fake.run_dir / "refusal.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("err", "code", "reason"),
    [
        ("Host key verification failed.\r\n", 11, "host-key-failed"),
        ("Connection reset\n", 10, "ssh-failed"),
    ],
)
def test_ac_2_pinned_ssh_final_release_failure(
    tmp_path, monkeypatch, capsys, err, code, reason, env_clean
):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-release.ps1"] = [Result(255, "", err)]
    got = fake.run()
    out = capsys.readouterr().out
    assert got == code, out
    last = out.strip().splitlines()[-1]
    assert last.startswith(f"e2e-remote: {reason} exit={code} run={fake.run_id} "), last
    assert fake.released() == [fake.run_id]
    assert f"release {fake.run_id}" in out
    assert summary_of(fake.run_dir)["exit"] == 0
    assert (fake.run_dir / "summary.txt").is_file()
    rec = refusal_of(fake)
    assert (rec["reason"], rec["exit"], rec["lock_kept"]) == (reason, code, True)


# --- AC-3 and AC-4: the desktop -------------------------------------------------------------


def _no_upload(fake: Fake) -> None:
    called = fake.scripts_called()
    assert "host-lock.ps1" not in called, called
    assert "scp-upload" not in called, called


@pytest.mark.parametrize(
    "over",
    [
        {"explorer": []},
        {"explorer": [{"session": 0, "user": "HOSTPC\\tester"}]},
        {"explorer": [{"session": 1, "user": "HOSTPC\\someone"}]},
        {"user_session": {"id": 1, "state": "Disc"}},
        {"user_session": {"id": None, "state": None}},
    ],
)
def test_ac_3_no_desktop_refuses(tmp_path, monkeypatch, capsys, over, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [facts(**over)]
    assert fake.run() == 20
    assert "no-desktop-session" in capsys.readouterr().out
    _no_upload(fake)


def test_ac_3_no_desktop_done_96(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.set_results(None, None, "96")
    assert fake.run() == 20
    assert "no-desktop-session" in capsys.readouterr().out
    assert fake.released() == [fake.run_id]


def test_ac_4_locked_refuses(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [facts(logonui_sessions=[1])]
    assert fake.run() == 21
    assert "desktop-locked" in capsys.readouterr().out
    _no_upload(fake)


def test_ac_4_locked_other_session_is_not(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [facts(logonui_sessions=[2])]
    assert fake.check() == 0


def test_ac_4_locked_done_97(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.set_results(None, None, "97")
    assert fake.run() == 21
    assert "desktop-locked" in capsys.readouterr().out
    assert fake.released() == [fake.run_id]


# --- AC-5: busy, lock and task --------------------------------------------------------------


def _reasons(m: ModuleType, f: dict, **cfg_over: object) -> list[tuple[str, str]]:
    cfg = dict(CFG)
    cfg.update(cfg_over)
    return list(m.evaluate(f, cfg, node_major()))


def test_ac_5_busy_user_process(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [
        facts(busy=[{"user": "HOSTPC\\ci-runner", "name": "node", "pid": 77}])
    ]
    assert fake.run() == 22
    out = capsys.readouterr().out
    assert "host-busy" in out and "ci-runner" in out and "node" in out
    _no_upload(fake)


def test_ac_5_busy_unknown_owners(monkeypatch, tmp_path):
    fake = new_fake(monkeypatch, tmp_path)
    got = _reasons(fake.m, facts(owners_seen=0, elevated=False))
    assert [r for r, _ in got] == ["host-busy-unknown"]
    assert _reasons(fake.m, facts(owners_seen=0, elevated=False), busy_users=[]) == []


@pytest.mark.parametrize(
    "over",
    [
        {"runner_workers": [{"user": "HOSTPC\\someone", "pid": 55}]},
        {
            "own_orphans": [
                {
                    "user": "HOSTPC\\tester",
                    "name": "electron",
                    "pid": 66,
                    "ppid": 1,
                    "created": START,
                }
            ]
        },
        {
            "own_orphans": [
                {"user": "HOSTPC\\tester", "name": "node", "pid": 67, "ppid": 1, "created": START}
            ]
        },
    ],
)
def test_ac_5_busy_worker_and_orphans(tmp_path, monkeypatch, over):
    fake = new_fake(monkeypatch, tmp_path)
    got = _reasons(fake.m, facts(**over))
    assert [r for r, _ in got] == ["host-busy"]
    pid = str((over.get("runner_workers") or over.get("own_orphans"))[0]["pid"])
    assert pid in got[0][1]


def test_ac_5_busy_missing_account_is_reported(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [facts(busy_users_missing=["ci-runner"])]
    assert fake.check() == 0
    out = capsys.readouterr().out
    assert "busy_users_missing" in out and "ci-runner" in out


def test_ac_5_busy_overlap_healthy_run_is_empty(tmp_path, monkeypatch):
    fake = new_fake(monkeypatch, tmp_path)
    st = healthy_status(fake.run_id, fake.sha, None)
    assert fake.m.poll_overlap(st, dict(CFG), fake.run_id) == []


def _orphan(name: str, pid: int, ppid: int, created: str = "2026-11-18T12:02:00.0Z") -> dict:
    return {"user": "HOSTPC\\tester", "name": name, "pid": pid, "ppid": ppid, "created": created}


@pytest.mark.parametrize(
    "case",
    ["stray-electron", "other-run-node", "runner", "other-lock", "reused-pid", "logonui", "busy"],
)
def test_ac_5_busy_overlap_is_recorded(tmp_path, monkeypatch, case):
    fake = new_fake(monkeypatch, tmp_path)
    st = healthy_status(fake.run_id, fake.sha, None)
    if case == "stray-electron":
        st["own_orphans"].append(_orphan("electron", 5000, 1))
    elif case == "other-run-node":
        st["own_orphans"].append(_orphan("node", 5100, 900))
    elif case == "runner":
        st["runner_workers"] = [{"user": "HOSTPC\\tester", "pid": 5200}]
    elif case == "other-lock":
        st["lock"] = lock_of(OTHER_RUN, OTHER_SHA)
    elif case == "reused-pid":
        st["pid_file"] = {"pid": 4100, "start": "2026-11-18T09:00:00.0000000Z"}
    elif case == "logonui":
        st["logonui_sessions"] = [1]
    else:
        st["busy"] = [{"user": "HOSTPC\\ci-runner", "name": "python", "pid": 5300}]
    assert fake.m.poll_overlap(st, dict(CFG), fake.run_id) != []


def test_ac_5_busy_overlap_lands_in_summary(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    busy = healthy_status(fake.run_id, fake.sha, None)
    busy["runner_workers"] = [{"user": "HOSTPC\\tester", "pid": 5200}]
    fake.results["host-status.ps1"] = [
        busy,
        lambda argv: jline(healthy_status(fake.run_id, fake.sha)),
    ]
    assert fake.run() == 0
    s = summary_of(fake.run_dir)
    assert len(s["overlap"]) == 1
    assert (fake.run_dir / "polls.jsonl").read_text(encoding="utf-8").count("\n") == 2


def test_ac_5_busy_lock_held_by_another(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [facts(lock=lock_of(OTHER_RUN, OTHER_SHA))]
    assert fake.run() == 23
    out = capsys.readouterr().out
    assert "host-locked" in out and OTHER_RUN in out
    _no_upload(fake)


def test_ac_5_busy_task_running(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [facts(task=task(state="Running"))]
    assert fake.run() == 24
    assert "task-running" in capsys.readouterr().out
    _no_upload(fake)


def test_ac_5_busy_at_lock_has_no_release(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-lock.ps1"] = [{"reason": "host-busy", "detail": "ci-runner node 77"}]
    assert fake.run() == 22
    assert fake.released() == []
    assert "scp-upload" not in fake.scripts_called()


def test_ac_5_busy_at_start_releases(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-start.ps1"] = [{"reason": "host-busy", "detail": "Runner.Worker 55"}]
    assert fake.run() == 22
    assert fake.released() == [fake.run_id]
    assert_pinned(fake)


# --- AC-6: prerequisites --------------------------------------------------------------------

PREREQ_CASES = {
    "node": {"node": {"exists": False, "version": None}},
    "node-version": {"node": {"exists": True, "version": "v1.2.0"}},
    "uv": {"uv": False},
    "vcruntime": {"vcruntime": False},
    "ffmpeg": {"ffmpeg": False},
    "ffprobe": {"ffprobe": False},
    "task": {"task": task(exists=False, state=None, principal=None, action_exe=None)},
    "task-principal": {"task": task(principal="HOSTPC\\someone")},
    "task-logon-interactive": {"task": task(logon="S4U")},
    "task-action": {"task": task(action_args="-File C:\\elsewhere\\run-e2e.ps1")},
    "task-limit": {"task": task(limit_min=100)},
    "picker-stub-local": {},
    "disk": {"free_gb": 3.5},
}


@pytest.mark.parametrize("pid", sorted(PREREQ_CASES))
def test_ac_6_prereq_each_id(tmp_path, monkeypatch, pid):
    fake = new_fake(monkeypatch, tmp_path)
    assert list(fake.m.PREREQ_IDS) == [
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
    ]
    if pid == "picker-stub-local":
        (fake.m.STUB_DIR / STUB_NAMES[2]).unlink()
    got = _reasons(fake.m, facts(**PREREQ_CASES[pid]))
    assert [r for r, _ in got] == ["prerequisite-missing"], got
    assert got[0][1].split(",") == [pid]
    assert fake.m.REASONS["prerequisite-missing"] == 25


def test_ac_6_prereq_three_named_together(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-facts.ps1"] = [facts(uv=False, ffprobe=False, free_gb=1.0)]
    assert fake.check() == 25
    out = capsys.readouterr().out
    for pid in ("uv", "ffprobe", "disk"):
        assert re.search(r"\b" + pid + r"\b", out), pid


@pytest.mark.parametrize("principal", ["MACHINE\\tester", "tester", "TESTER"])
def test_ac_6_prereq_principal_forms(tmp_path, monkeypatch, principal):
    fake = new_fake(monkeypatch, tmp_path)
    assert _reasons(fake.m, facts(task=task(principal=principal))) == []


def test_ac_6_prereq_unlimited_task(tmp_path, monkeypatch):
    fake = new_fake(monkeypatch, tmp_path)
    assert _reasons(fake.m, facts(task=task(limit_min=0))) == []


def test_ac_6_prereq_order_and_first_exit(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    f = facts(explorer=[], uv=False, lock=lock_of(OTHER_RUN, OTHER_SHA), logonui_sessions=[1])
    got = [r for r, _ in _reasons(fake.m, f)]
    assert got == ["no-desktop-session", "desktop-locked", "host-locked", "prerequisite-missing"]
    fake.results["host-facts.ps1"] = [f]
    assert fake.check() == 20


# --- AC-7: the commit -----------------------------------------------------------------------


def test_ac_7_commit_unknown(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    assert fake.run(sha="0" * 40) == 26
    assert "commit-unknown" in capsys.readouterr().out
    assert fake.calls == []


def test_ac_7_commit_zip_comment_mismatch(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.zip_comment = OTHER_SHA
    assert fake.run() == 26
    assert "commit-mismatch" in capsys.readouterr().out
    assert fake.calls == []


@pytest.mark.parametrize("reason", ["commit-mismatch", "upload-mismatch", "request-missing"])
def test_ac_7_commit_verify_refusal_releases(tmp_path, monkeypatch, capsys, reason, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-prepare.ps1 verify"] = [{"reason": reason, "detail": "fixture"}]
    assert fake.run() == fake.m.REASONS[reason]
    assert reason in capsys.readouterr().out
    assert fake.released() == [fake.run_id]
    assert "host-start.ps1" not in fake.scripts_called()
    assert json.loads((fake.run_dir / "refusal.json").read_text(encoding="utf-8"))["reason"] == (
        reason
    )


def test_ac_7_commit_done_98(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.set_results(None, None, "98")
    assert fake.run() == 26
    assert "commit-mismatch" in capsys.readouterr().out


def test_ac_7_commit_request_binds(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    assert fake.run() == 0
    up = fake.run_dir / "upload" / "runs" / fake.run_id
    req = json.loads((up / "request.json").read_text(encoding="utf-8"))
    assert req["run_id"] == fake.run_id
    assert req["commit"] == fake.sha
    assert req["commit_epoch"] == int(_git("log", "-1", "--format=%ct", fake.sha))
    assert req["zip_sha256"] == hashlib.sha256((up / "src.zip").read_bytes()).hexdigest()
    assert req["stub"] == {
        n: hashlib.sha256((fake.m.STUB_DIR / n).read_bytes()).hexdigest() for n in STUB_NAMES
    }
    for n in STUB_NAMES:
        assert (up / "publish" / n).read_bytes() == (fake.m.STUB_DIR / n).read_bytes()
    assert req["skip"] == fake.skip
    assert (req["user"], req["node_exe"], req["ffmpeg_bin"]) == (
        CFG["user"],
        CFG["node_exe"],
        CFG["ffmpeg_bin"],
    )
    s = summary_of(fake.run_dir)
    assert (s["commit"], s["zip_sha256"], s["run_id"]) == (fake.sha, req["zip_sha256"], fake.run_id)


def test_ac_7_commit_real_archive(tmp_path):
    m = _load()
    sha = head()
    out = tmp_path / "head.zip"
    m.archive(sha, out)
    with zipfile.ZipFile(out) as z:
        assert z.comment.decode("ascii") == sha
        assert ".node-version" in z.namelist()


# --- AC-8: the build ------------------------------------------------------------------------


def test_ac_8_build_failed_step(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    log = f"runs\\{fake.run_id}\\logs\\build-2-npm-ci.log"
    fake.results["host-prepare.ps1 build"] = [
        {"reason": "build-failed", "detail": f"step=npm-ci log={log}", "step": "npm-ci"}
    ]
    assert fake.run() == 28
    out = capsys.readouterr().out
    assert "build-failed" in out and "npm-ci" in out and "build-2-npm-ci.log" in out
    assert fake.released() == [fake.run_id]
    assert "host-start.ps1" not in fake.scripts_called()


def test_ac_8_build_stale(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-prepare.ps1 stale"] = [{"reason": "build-stale", "detail": "ui\\src"}]
    assert fake.run() == 27
    assert "build-stale" in capsys.readouterr().out
    assert fake.released() == [fake.run_id]


def test_ac_8_build_done_99(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.set_results(None, None, "99")
    assert fake.run() == 27
    assert "build-stale" in capsys.readouterr().out


def test_ac_8_build_prepare_receipts(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    assert fake.run() == 0
    for stage in ("verify", "extract", "build", "stale"):
        got = json.loads((fake.run_dir / f"prepare-{stage}.json").read_text(encoding="utf-8"))
        assert got["reason"] == "ok"
    s = summary_of(fake.run_dir)
    assert (s["mtime_skew_s"], s["commit_offset_s"]) == (10800, 10800)
    build = [c for c in fake.calls if fake.key(c) == "host-prepare.ps1 build"]
    assert len(build) == 1


# --- AC-9: polling --------------------------------------------------------------------------


def test_ac_9_poll_timeout_keeps_lock(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-status.ps1"] = [
        lambda argv: jline(healthy_status(fake.run_id, fake.sha, None))
    ]
    assert fake.run() == 30
    out = capsys.readouterr().out
    assert "poll-timeout" in out
    assert f"collect {fake.run_id}" in out and f"release {fake.run_id}" in out
    assert fake.released() == []
    assert fake.now - T0 >= timedelta(minutes=CFG["timeout_min"])
    assert fake.now - T0 < timedelta(minutes=CFG["timeout_min"] + 5)


def test_ac_9_poll_launcher_ended(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)

    def ended(argv: list[str]) -> Result:
        st = healthy_status(fake.run_id, fake.sha, None)
        st["task"] = task(state="Ready")
        return jline(st)

    fake.results["host-status.ps1"] = [ended]
    assert fake.run() == 30
    assert "launcher-ended" in capsys.readouterr().out
    assert fake.released() == []
    assert fake.scripts_called().count("host-status.ps1") == 2


def test_ac_9_poll_three_failures(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-status.ps1"] = [Result(255, "", "Connection reset\n")]
    assert fake.run() == 10
    assert fake.scripts_called().count("host-status.ps1") == 3
    assert fake.released() == []


def test_ac_9_poll_failure_recovers(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-status.ps1"] = [
        Result(255, "", "Connection reset\n"),
        Result(255, "", "Connection reset\n"),
        lambda argv: jline(healthy_status(fake.run_id, fake.sha)),
    ]
    assert fake.run() == 0


def test_ac_9_poll_done_95(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.set_results(None, None, "95")
    assert fake.run() == 29
    assert "request-missing" in capsys.readouterr().out
    assert fake.released() == [fake.run_id]


def test_ac_9_poll_collect_after_timeout(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-status.ps1"] = [
        lambda argv: jline(healthy_status(fake.run_id, fake.sha, None))
    ]
    assert fake.run() == 30
    fake.results.pop("host-status.ps1")
    assert fake.m.main(["collect", fake.run_id, "--config", fake.cfg]) == 0
    assert (fake.run_dir / "host" / "report.json").is_file()
    assert summary_of(fake.run_dir)["exit"] == 0
    assert fake.released() == [fake.run_id]


def test_ac_9_poll_collect_without_done(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-status.ps1"] = [
        lambda argv: jline(healthy_status(fake.run_id, fake.sha, None))
    ]
    assert fake.run() == 30
    assert fake.m.main(["collect", fake.run_id, "--config", fake.cfg]) == 30
    assert not (fake.run_dir / "host").exists()


def test_ac_9_poll_receipt_write_failure(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    real_open = open

    def failing(path, *a, **kw):
        if Path(path).name == "polls.jsonl":
            raise OSError("fixture disk full")
        return real_open(path, *a, **kw)

    monkeypatch.setattr(fake.m, "open", failing, raising=False)
    try:
        got = fake.run()
    except OSError as exc:
        got = f"uncaught {type(exc).__name__}: {exc}"
    out = capsys.readouterr().out
    assert got == 34, out
    last = out.strip().splitlines()[-1]
    assert last.startswith(f"e2e-remote: receipt-write-failed exit=34 run={fake.run_id} "), last
    assert "polls.jsonl" in out
    assert f"collect {fake.run_id}" in out and f"release {fake.run_id}" in out
    assert fake.released() == []
    assert refusal_of(fake)["lock_kept"] is True


# --- AC-10: the report only -----------------------------------------------------------------


def _summarize(m: ModuleType, tmp: Path, rep: object, *extra: str, known: Path | None = None):
    rp = tmp / "rep" / "report.json"
    rp.parent.mkdir(exist_ok=True)
    if rep is not None:
        rp.write_text(rep if isinstance(rep, str) else json.dumps(rep), encoding="utf-8")
    (tmp / "rep" / "run.log").write_text("232 passed (19.3m)\n", encoding="ascii")
    reg = tmp / "register.yaml"
    reg.write_text(REGISTER_TEXT, encoding="utf-8")
    kn = known or known_file(
        tmp / "known.json", [("k.test.ts", f"AC-901.{i}", "TEST-ISSUE-A") for i in range(1, 5)]
    )
    out = tmp / "sum"
    code = m.main(
        [
            "summarize",
            str(rp),
            "--label",
            LABEL,
            "--known",
            str(kn),
            "--register",
            str(reg),
            "--out",
            str(out),
            *extra,
        ]
    )
    return code, out


def rows_228() -> list[tuple[str, str, str]]:
    rows = [(f"s{i % 7}.test.ts", f"AC-900.{i} case", "expected") for i in range(228)]
    rows += [("k.test.ts", f"AC-901.{i} known failure", "unexpected") for i in range(1, 5)]
    return rows


def test_ac_10_report_only_counts(tmp_path):
    m = _load()
    code, out = _summarize(m, tmp_path, report(rows_228()))
    assert code == 0
    s = summary_of(out)
    assert (s["tests"], s["expected"], s["unexpected"], s["flaky"], s["skipped"]) == (
        232,
        228,
        4,
        0,
        0,
    )
    assert s["spec_files"] == 8
    assert s["specs_checked"] is False
    assert s["playwright_version"] == "1.64.1"
    assert s["duration_ms"] == 1234
    assert (out / "summary.txt").is_file()


def test_ac_10_report_only_ignores_run_log(tmp_path):
    m = _load()
    rows = rows_228()[:200] + rows_228()[228:]
    code, out = _summarize(m, tmp_path, report(rows))
    assert code == 0
    assert summary_of(out)["tests"] == 204


def test_ac_10_report_only_inconsistent(tmp_path, capsys):
    m = _load()
    code, out = _summarize(m, tmp_path, report(rows_228(), stats={"expected": 232}))
    assert code == 31
    assert "report-inconsistent" in capsys.readouterr().out


def test_ac_10_report_only_errors(tmp_path, capsys):
    m = _load()
    code, _ = _summarize(m, tmp_path, report(rows_228(), errors=[{"message": "boom"}]))
    assert code == 31
    assert "report-errors" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("rep", "reason"),
    [
        ("{not json", "report-invalid"),
        (json.dumps({"suites": []}), "report-invalid"),
        (None, "report-missing"),
    ],
)
def test_ac_10_report_only_bad_file(tmp_path, capsys, rep, reason):
    m = _load()
    code, _ = _summarize(m, tmp_path, rep)
    assert code == 31
    assert reason in capsys.readouterr().out


def test_ac_10_report_only_specs_mismatch(tmp_path, capsys):
    m = _load()
    specs = tmp_path / "specs.txt"
    specs.write_text("".join(f"s{i}.test.ts\n" for i in range(7)), encoding="utf-8")
    code, _ = _summarize(m, tmp_path, report(rows_228()), "--specs", str(specs))
    assert code == 31
    assert "specs-mismatch" in capsys.readouterr().out


def test_ac_10_report_only_specs_match(tmp_path):
    m = _load()
    specs = tmp_path / "specs.txt"
    specs.write_bytes(
        ("".join(f"s{i}.test.ts\r\n" for i in range(7)) + "k.test.ts\r\n").encode("ascii")
    )
    code, out = _summarize(m, tmp_path, report(rows_228()), "--specs", str(specs))
    assert code == 0
    assert summary_of(out)["specs_checked"] is True


def test_ac_10_report_only_run_specs_mismatch(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.set_results(
        report([(f, "AC-900.1 case", "expected") for f in fake.specs[1:]]),
        "\n".join(fake.specs[1:]) + "\n",
        "0",
    )
    assert fake.run() == 31
    assert "specs-mismatch" in capsys.readouterr().out
    assert fake.released() == [fake.run_id]


# --- AC-11: the known list ------------------------------------------------------------------


def test_ac_11_known_four_exit_0(tmp_path):
    m = _load()
    code, out = _summarize(m, tmp_path, report(rows_228()))
    s = summary_of(out)
    assert code == 0 and s["exit"] == 0 and s["result"] == "ok"
    assert sorted(k["ac"] for k in s["known"]) == [f"AC-901.{i}" for i in range(1, 5)]
    assert all(set(k) >= {"file", "ac", "title"} for k in s["known"])
    assert s["new"] == [] and s["known_now_passing"] == []


def test_ac_11_known_one_more_unexpected(tmp_path, capsys):
    m = _load()
    rows = rows_228()
    rows[5] = (rows[5][0], rows[5][1], "unexpected")
    code, out = _summarize(m, tmp_path, report(rows))
    assert code == 40
    s = summary_of(out)
    assert [(n["file"], n["ac"]) for n in s["new"]] == [(rows[5][0], "AC-900.5")]
    assert rows[5][1] in capsys.readouterr().out


@pytest.mark.parametrize("status", ["flaky", "skipped"])
def test_ac_11_known_flaky_or_skipped_is_new(tmp_path, status):
    m = _load()
    rows = rows_228()
    rows[3] = (rows[3][0], rows[3][1], status)
    code, out = _summarize(m, tmp_path, report(rows))
    assert code == 40
    assert [n["ac"] for n in summary_of(out)["new"]] == ["AC-900.3"]


@pytest.mark.parametrize("status", ["flaky", "skipped"])
def test_ac_11_known_listed_back_flaky_is_new(tmp_path, status):
    m = _load()
    rows = rows_228()
    rows[-1] = (rows[-1][0], rows[-1][1], status)
    code, out = _summarize(m, tmp_path, report(rows))
    assert code == 40
    assert [n["ac"] for n in summary_of(out)["new"]] == ["AC-901.4"]


def test_ac_11_known_now_passing(tmp_path):
    m = _load()
    rows = rows_228()
    rows[-1] = (rows[-1][0], rows[-1][1], "expected")
    code, out = _summarize(m, tmp_path, report(rows))
    s = summary_of(out)
    assert code == 0
    assert [k["ac"] for k in s["known_now_passing"]] == ["AC-901.4"]
    assert len(s["known"]) == 3


def test_ac_11_known_issue_not_open(tmp_path, capsys):
    m = _load()
    kn = known_file(
        tmp_path / "kn.json",
        [
            ("k.test.ts", f"AC-901.{i}", "TEST-ISSUE-A" if i < 4 else "TEST-ISSUE-B")
            for i in range(1, 5)
        ],
    )
    code, out = _summarize(m, tmp_path, report(rows_228()), known=kn)
    assert code == 32
    assert "TEST-ISSUE-B" in capsys.readouterr().out
    assert summary_of(out)["exit"] == 32


def test_ac_11_known_listed_test_missing(tmp_path, capsys):
    m = _load()
    kn = known_file(
        tmp_path / "kn.json",
        [("k.test.ts", f"AC-901.{i}", "TEST-ISSUE-A") for i in range(1, 6)],
    )
    code, _ = _summarize(m, tmp_path, report(rows_228()), known=kn)
    assert code == 32
    assert "AC-901.5" in capsys.readouterr().out


def test_ac_11_known_first_token_only(tmp_path):
    m = _load()
    rows = rows_228()[:228]
    rows += [
        ("k.test.ts", "AC-82.6 TEXT_PIXEL_ORACLE: the preview text", "unexpected"),
        ("k.test.ts", "AC-102.20 AC-82.6 passes through the parameterised path", "unexpected"),
        ("k.test.ts", "W9-1 a title without an AC id", "expected"),
    ]
    kn = known_file(
        tmp_path / "kn.json",
        [("k.test.ts", "AC-82.6", "TEST-ISSUE-A"), ("k.test.ts", "AC-102.20", "TEST-ISSUE-A")],
    )
    code, out = _summarize(m, tmp_path, report(rows), known=kn)
    assert code == 0
    known = {k["ac"]: k["title"] for k in summary_of(out)["known"]}
    assert known["AC-82.6"].startswith("AC-82.6 TEXT_PIXEL")
    assert known["AC-102.20"].startswith("AC-102.20 AC-82.6")


def test_ac_11_known_entry_matching_two(tmp_path, capsys):
    m = _load()
    rows = rows_228()
    rows.append(("k.test.ts", "AC-901.1 a second test with the same id", "unexpected"))
    code, _ = _summarize(m, tmp_path, report(rows))
    assert code == 32
    assert "AC-901.1" in capsys.readouterr().out


def test_ac_11_known_dotted_id_is_exact(tmp_path):
    m = _load()
    rows = rows_228()
    rows[-1] = ("k.test.ts", "AC-901.40 not the listed id", "unexpected")
    code, out = _summarize(m, tmp_path, report(rows))
    assert code == 32


def test_ac_11_known_other_label_ignored(tmp_path):
    m = _load()
    code, out = _summarize(m, tmp_path, report(rows_228()))
    s = summary_of(out)
    assert code == 0
    assert all(k["file"] != "nowhere.test.ts" for k in s["known"])
    assert s["skip"] == []


def test_ac_11_known_skip_leaves_expected_set(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    assert fake.run() == 0
    s = summary_of(fake.run_dir)
    assert [e["file"] for e in s["skip"]] == fake.skip
    assert s["spec_files"] == len(fake.specs)
    assert s["specs_checked"] is True
    assert [k["ac"] for k in s["known"]] == ["AC-901.1"]


def test_ac_11_known_skip_entry_without_reason(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    data = json.loads(fake.known.read_text(encoding="utf-8"))
    data["skip"][0]["reason"] = ""
    fake.known.write_text(json.dumps(data), encoding="utf-8")
    assert fake.run() == 32
    assert fake.calls == []


def test_ac_11_known_skip_entry_not_a_spec(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    data = json.loads(fake.known.read_text(encoding="utf-8"))
    data["skip"][0]["file"] = "no-such-spec.test.ts"
    fake.known.write_text(json.dumps(data), encoding="utf-8")
    assert fake.run() == 32
    assert "no-such-spec.test.ts" in capsys.readouterr().out


def test_ac_11_known_tracked_list(tmp_path):
    m = _load()
    assert KNOWN.is_file(), "tools/e2e_host/known-failures.json does not exist yet"
    data = json.loads(KNOWN.read_text(encoding="utf-8"))
    assert [(e["label"], e["file"], e["ac"], e["issue"]) for e in data["known"]] == []
    assert [(e["label"], e["file"]) for e in data["skip"]] == [
        ("mini-air", "capture-filmstrip-actions.test.ts"),
        ("mini-air", "capture-import.test.ts"),
    ]
    assert all(e["reason"] for e in data["skip"])
    assert Path(m.KNOWN_FILE) == KNOWN


# --- AC-12: receipts ------------------------------------------------------------------------


def test_ac_12_receipts_run_folder_exists(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.run_dir.mkdir(parents=True)
    (fake.run_dir / "keep.txt").write_text("x", encoding="ascii")
    assert fake.run() == 33
    assert "receipt-exists" in capsys.readouterr().out
    assert fake.calls == []
    assert [p.name for p in fake.run_dir.iterdir()] == ["keep.txt"]


def test_ac_12_receipts_failed_collect(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)

    def half(argv: list[str]) -> Result:
        Path(argv[-1]).mkdir(parents=True)
        (Path(argv[-1]) / "DONE").write_text("1", encoding="ascii")
        return Result(1, "", "scp: connection lost\n")

    fake.results["scp-results"] = [half]
    assert fake.run() == 10
    assert not (fake.run_dir / "host").exists()
    assert not (fake.run_dir / "summary.json").exists()


def test_ac_12_receipts_summary_write_failure(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    real = os.replace

    def boom(src, dst):
        if Path(dst).name == "summary.json":
            raise OSError("disk full")
        return real(src, dst)

    monkeypatch.setattr(fake.m.os, "replace", boom)
    assert fake.run() == 34
    assert "receipt-write-failed" in capsys.readouterr().out
    assert not (fake.run_dir / "summary.json").exists()


def test_ac_12_receipts_check_out_exists(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    out = tmp_path / "check.json"
    out.write_text("{}", encoding="ascii")
    assert fake.check("--out", str(out)) == 33
    assert fake.calls == []
    assert out.read_text(encoding="ascii") == "{}"


def test_ac_12_receipts_check_out_written(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    out = tmp_path / "check.json"
    assert fake.check("--out", str(out)) == 0
    got = json.loads(out.read_text(encoding="utf-8"))
    assert got["reasons"] == [] and got["exit"] == 0 and got["facts"]["schema"] == 1
    assert re.fullmatch(r"[0-9a-f]{12}", got["set"])
    assert fake.scripts_called() == ["scp-stage", "host-facts.ps1"]
    assert "check: ok" in capsys.readouterr().out


def test_ac_12_receipts_host_results_exist(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-start.ps1"] = [{"reason": "receipt-exists", "detail": "host-results"}]
    assert fake.run() == 33
    assert "receipt-exists" in capsys.readouterr().out
    assert fake.released() == [fake.run_id]


def test_ac_12_receipts_summary_txt_exists(tmp_path, capsys):
    m = _load()
    keep = b"KEEP THIS RECEIPT\n"
    (tmp_path / "sum").mkdir()
    (tmp_path / "sum" / "summary.txt").write_bytes(keep)
    code, out = _summarize(m, tmp_path, report(rows_228()))
    assert code == 33
    assert "receipt-exists" in capsys.readouterr().out
    assert (out / "summary.txt").read_bytes() == keep
    assert not (out / "summary.json").exists()


def test_ac_12_receipts_collect_summary_txt_exists(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-status.ps1"] = [
        lambda argv: jline(healthy_status(fake.run_id, fake.sha, None))
    ]
    assert fake.run() == 30
    fake.results.pop("host-status.ps1")
    keep = b"KEEP THIS RECEIPT\n"
    (fake.run_dir / "summary.txt").write_bytes(keep)
    assert fake.m.main(["collect", fake.run_id, "--config", fake.cfg]) == 33
    assert "receipt-exists" in capsys.readouterr().out
    assert (fake.run_dir / "summary.txt").read_bytes() == keep
    assert not (fake.run_dir / "summary.json").exists()
    assert "scp-results" not in fake.scripts_called()


def test_ac_12_receipts_stage_is_content_addressed(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    assert fake.run() == 0
    sets = list((fake.run_dir / "stage" / "bin").iterdir())
    assert len(sets) == 1
    names = sorted(p.name for p in sets[0].iterdir())
    assert names == sorted([*SCRIPTS, "host.json"])
    h = hashlib.sha256()
    for n in names:
        h.update(n.encode() + b"\0" + (sets[0] / n).read_bytes() + b"\0")
    assert sets[0].name == h.hexdigest()[:12]
    hj = json.loads((sets[0] / "host.json").read_text(encoding="utf-8"))
    assert sorted(hj) == sorted(
        ["user", "root", "task", "node_exe", "ffmpeg_bin", "busy_users", "min_free_gb"]
    )
    for c in fake.calls:
        if c[0] == "ssh":
            assert arg_after(c, "-File").startswith(CFG["root"] + "\\bin\\" + sets[0].name + "\\")


# --- AC-13: release -------------------------------------------------------------------------


def test_ac_13_release_holder(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    assert fake.m.main(["release", OTHER_RUN, "--config", fake.cfg]) == 0
    assert f"released: {OTHER_RUN}" in capsys.readouterr().out
    assert fake.released() == [OTHER_RUN]


def test_ac_13_release_other_id(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-release.ps1"] = [
        {"reason": "lock-mismatch", "detail": f"holder={fake.run_id}"}
    ]
    assert fake.m.main(["release", OTHER_RUN, "--config", fake.cfg]) == 23
    out = capsys.readouterr().out
    assert "lock-mismatch" in out and fake.run_id in out


def test_ac_13_release_none(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-release.ps1"] = [{"reason": "ok", "released": "none"}]
    assert fake.m.main(["release", OTHER_RUN, "--config", fake.cfg]) == 0
    assert "released: none" in capsys.readouterr().out


def test_ac_13_release_bad_id(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    assert fake.m.main(["release", "r1; whoami", "--config", fake.cfg]) == 2
    assert fake.calls == []


def test_ac_13_release_after_lock(tmp_path, monkeypatch, capsys, env_clean):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["scp-upload"] = [Result(1, "", "scp: write failed\n")]
    assert fake.run() == 10
    assert fake.released() == [fake.run_id]
    assert fake.scripts_called()[-1] == "host-release.ps1"


@pytest.mark.parametrize(
    ("err", "reason", "detail"),
    [
        ("Host key verification failed.\r\n", "host-key-failed", "Host key verification failed."),
        ("Connection reset\n", "ssh-failed", "Connection reset"),
    ],
)
def test_ac_13_release_failure_after_refusal(
    tmp_path, monkeypatch, capsys, err, reason, detail, env_clean
):
    fake = new_fake(monkeypatch, tmp_path)
    fake.results["host-start.ps1"] = [{"reason": "receipt-exists", "detail": "host-results"}]
    fake.results["host-release.ps1"] = [Result(255, "", err)]
    assert fake.run() == 33
    out = capsys.readouterr().out
    last = out.strip().splitlines()[-1]
    assert last.startswith(f"e2e-remote: receipt-exists exit=33 run={fake.run_id} "), last
    assert f"also refused: {reason}: {detail}" in out
    assert fake.released() == [fake.run_id]
    rec = refusal_of(fake)
    assert (rec["reason"], rec["exit"], rec["lock_kept"]) == ("receipt-exists", 33, True)
    assert [reason, detail] in rec["also"]


# --- AC-14: host scripts, static ------------------------------------------------------------


def _script(name: str) -> bytes:
    path = HOST / name
    assert path.is_file(), f"tools/e2e_host/{name} does not exist yet"
    return path.read_bytes()


@pytest.mark.parametrize("name", SCRIPTS)
def test_ac_14_host_static_bytes(name):
    raw = _script(name)
    assert all(b < 128 for b in raw), "non-ASCII byte"
    assert b"\r" not in raw and b"`" not in raw
    text = raw.decode("ascii")
    low = text.lower()
    for token in HOST_BANNED:
        assert token.lower() not in low, token
    assert not re.search(r"\bkill\b", low)
    for line in low.splitlines():
        assert not ("remove-item" in line and "-recurse" in line), line
    assert text.startswith("$ErrorActionPreference = 'Continue'\n"), text[:80]
    assert "$ProgressPreference = 'SilentlyContinue'" in text
    jsons = [ln for ln in text.splitlines() if "ConvertTo-Json" in ln]
    assert jsons, "no ConvertTo-Json"
    for ln in jsons:
        assert "-InputObject" in ln and "-Depth 8" in ln and "-Compress" in ln, ln
    if name != "run-e2e.ps1":
        assert "host.json" in text
        assert "^r[0-9]{8}T[0-9]{6}Z-[0-9a-f]{7}$" in text or name == "host-facts.ps1"


def _block(text: str) -> str:
    start = text.index("# begin busy-check\n")
    end = text.index("# end busy-check\n")
    return text[start:end]


def test_ac_14_host_static_busy_block():
    blocks = [_block(_script(n).decode("ascii")) for n in BUSY_COPIES]
    assert len(blocks[0]) > 200
    assert all(b == blocks[0] for b in blocks)
    for n in ("host-prepare.ps1", "host-release.ps1", "run-e2e.ps1"):
        assert "# begin busy-check" not in _script(n).decode("ascii")


def test_ac_14_host_static_launcher():
    text = _script("run-e2e.ps1").decode("ascii")
    comments = [ln for ln in text.splitlines() if ln.startswith("#")]
    assert comments[0] == "# avkit-remote-launcher"
    starts = [ln for ln in text.splitlines() if "Start-Process" in ln]
    assert len(starts) == 1 and "-Wait" not in starts[0] and "-PassThru" in starts[0]
    after = text[text.index(starts[0]) :]
    assert ".Handle" in after
    assert after.index("pid.txt") < after.index("WaitForExit")
    assert "DONE.tmp" in text
    for ln in text.splitlines():
        if re.search(r"Set-Content|Out-File|Add-Content|WriteAll", ln) and "DONE" in ln:
            assert "DONE.tmp" in ln, ln
    assert re.search(r"(Move-Item|Rename-Item).*DONE", text)
    assert "ELECTRON_RUN_AS_NODE" in text and "AVKIT_E2E_DIAG_DIR" in text


def test_ac_14_host_static_task_calls():
    for n in SCRIPTS:
        text = _script(n).decode("ascii")
        if n == "host-start.ps1":
            assert text.count("Start-ScheduledTask") == 1
        else:
            assert "Start-ScheduledTask" not in text, n


def test_ac_14_host_static_tool_has_no_bypass():
    m = _load()
    text = TOOL.read_text(encoding="utf-8")
    for word in BYPASS:
        assert word not in text, word
    assert '"-i"' not in text and "'-i'" not in text
    for word in STOP_WORDS:
        assert word not in text, word
    assert m.SSH_OPTS == ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes"]


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_14_host_static_parses_in_ps51():
    for n in SCRIPTS:
        _script(n)
    paths = ",".join("'" + str(HOST / n) + "'" for n in SCRIPTS)
    cmd = (
        "foreach ($p in @(" + paths + ")) { $t = $null; $e = $null; "
        "[void][System.Management.Automation.Language.Parser]::ParseFile($p, [ref]$t, [ref]$e); "
        "'{0}={1}' -f (Split-Path $p -Leaf), $e.Count }"
    )
    r = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", cmd],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        timeout=120,
    )
    got = dict(ln.strip().split("=", 1) for ln in r.stdout.splitlines() if "=" in ln)
    assert got == {n: "0" for n in SCRIPTS}, r.stdout + r.stderr


# --- AC-15: host scripts on fixture roots ---------------------------------------------------


class HostRoot:
    def __init__(self, tmp: Path, user: str = "avkit-fixture-user", busy: list | None = None):
        for n in SCRIPTS:
            _script(n)
        self.root = tmp / "root"
        self.bin = self.root / "bin" / "fixtureset01"
        self.bin.mkdir(parents=True)
        for n in SCRIPTS:
            shutil.copyfile(HOST / n, self.bin / n)
        self.hj = {
            "user": user,
            "root": str(self.root),
            "task": "\\avkit-fixture\\no-such-task-q7",
            "node_exe": "C:\\avkit-no-node\\node.exe",
            "ffmpeg_bin": "C:\\avkit-no-ffmpeg\\bin",
            "busy_users": busy or [],
            "min_free_gb": 5,
        }
        (self.bin / "host.json").write_text(json.dumps(self.hj), encoding="utf-8")

    def ps(self, script: str, *args: str, where: Path | None = None) -> dict:
        path = (where or self.bin) / script
        inner = (
            "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "
            + str(path)
            + "".join(" " + a for a in args)
        )
        r = subprocess.run(
            ["powershell.exe", "-NoProfile", "-c", inner],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=240,
        )
        for line in reversed(r.stdout.splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    got = json.loads(line)
                except ValueError:
                    continue
                if isinstance(got, dict):
                    return got
        return {"reason": "<no json line>", "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:]}

    def lock(self, run_id: str, sha: str) -> None:
        body = {"run_id": run_id, "commit": sha, "set": "fixtureset01", "created_utc": "x"}
        (self.root / "avkit-remote.lock").write_text(json.dumps(body), encoding="ascii")

    def run_dir(self, run_id: str) -> Path:
        d = self.root / "runs" / run_id
        d.mkdir(parents=True, exist_ok=True)
        return d


RUN_A = "r20261118T120000Z-1234567"
RUN_B = "r20261118T120500Z-89abcde"
SHA_A = "1234567" + "0" * 33
SHA_B = "89abcde" + "f" * 33

FACT_TYPES: dict[str, object] = {
    "schema": int,
    "ps_version": str,
    "elevated": bool,
    "procs_total": int,
    "owners_seen": int,
    "busy": list,
    "own_orphans": list,
    "runner_workers": list,
    "busy_users_missing": list,
    "explorer": list,
    "logonui_sessions": list,
    "user_session": dict,
    "task": dict,
    "lock": (dict, type(None)),
    "launcher": dict,
    "node": dict,
    "uv": bool,
    "vcruntime": bool,
    "ffmpeg": bool,
    "ffprobe": bool,
    "free_gb": (int, float),
    "tz_offset_min": int,
    "utc_now": str,
    "ssh_shell": str,
}


def _facts_on_this_pc(tmp: Path, user: str, busy: list) -> dict:
    hr = HostRoot(tmp, user=user, busy=busy)
    f = hr.ps("host-facts.ps1")
    assert f.get("reason") == "ok", f
    return f


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_facts_schema(tmp_path):
    f = _facts_on_this_pc(tmp_path, "avkit-fixture-user", ["avkit-nobody-q"])
    for k, t in FACT_TYPES.items():
        assert k in f, k
        assert isinstance(f[k], t), (k, f[k])
    assert f["schema"] == 1
    assert f["busy_users_missing"] == ["avkit-nobody-q"]
    assert set(f["user_session"]) == {"id", "state"}
    assert set(f["task"]) == {
        "exists",
        "state",
        "principal",
        "logon",
        "runlevel",
        "action_exe",
        "action_args",
        "limit_min",
        "multiple",
    }
    assert f["task"]["exists"] is False
    assert set(f["launcher"]) == {"exists", "sha256", "marker"}
    assert set(f["node"]) == {"exists", "version"} and f["node"]["exists"] is False
    for e in f["explorer"]:
        assert isinstance(e["session"], int) and isinstance(e["user"], str)
    assert all(isinstance(s, int) for s in f["logonui_sessions"])
    assert f["lock"] is None
    assert not (tmp_path / "root" / "runs").exists()
    assert sorted(p.name for p in (tmp_path / "root").iterdir()) == ["bin"]


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_lock_and_release(tmp_path):
    hr = HostRoot(tmp_path)
    got = hr.ps("host-lock.ps1", "-RunId", RUN_A, "-Commit", SHA_A)
    assert got["reason"] == "ok", got
    lock = json.loads((hr.root / "avkit-remote.lock").read_text(encoding="utf-8-sig"))
    assert (lock["run_id"], lock["commit"]) == (RUN_A, SHA_A)
    got = hr.ps("host-lock.ps1", "-RunId", RUN_B, "-Commit", SHA_B)
    assert got["reason"] == "host-locked" and RUN_A in json.dumps(got), got
    got = hr.ps("host-release.ps1", "-RunId", RUN_B)
    assert got["reason"] == "lock-mismatch" and RUN_A in json.dumps(got), got
    assert (hr.root / "avkit-remote.lock").exists()
    got = hr.ps("host-release.ps1", "-RunId", RUN_A)
    assert got["reason"] == "ok" and got["released"] == RUN_A, got
    assert not (hr.root / "avkit-remote.lock").exists()
    got = hr.ps("host-release.ps1", "-RunId", RUN_A)
    assert got["reason"] == "ok" and got["released"] == "none", got


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_usage(tmp_path):
    hr = HostRoot(tmp_path)
    assert hr.ps("host-release.ps1", "-RunId", "r1-x")["reason"] == "usage"
    assert hr.ps("host-lock.ps1", "-RunId", RUN_A, "-Commit", "abc")["reason"] == "usage"
    assert hr.ps("host-prepare.ps1", "-RunId", RUN_A, "-Stage", "other")["reason"] == "usage"
    assert not (hr.root / "avkit-remote.lock").exists()


def _upload(hr: HostRoot, run_id: str, sha: str, comment: str, when: datetime | None = None):
    d = hr.run_dir(run_id)
    zp = d / "src.zip"
    with zipfile.ZipFile(zp, "w") as z:
        z.comment = comment.encode("ascii")
        stamp = (when or datetime.now()).timetuple()[:6]
        for name in ("ui/src/a.ts", "ui/package.json", "ui/tests/e2e/x.test.ts", ".node-version"):
            z.writestr(zipfile.ZipInfo(name, date_time=stamp), "content " + name)
    pub = d / "publish"
    pub.mkdir()
    for n in STUB_NAMES:
        (pub / n).write_bytes(b"stub " + n.encode())
    req = {
        "run_id": run_id,
        "commit": sha,
        "commit_epoch": int(time.time()) - 3600,
        "zip_sha256": hashlib.sha256(zp.read_bytes()).hexdigest(),
        "stub": {n: hashlib.sha256((pub / n).read_bytes()).hexdigest() for n in STUB_NAMES},
        "skip": [],
        "node_exe": "C:\\avkit-no-node\\node.exe",
        "ffmpeg_bin": "C:\\avkit-no-ffmpeg\\bin",
        "user": hr.hj["user"],
        "created_utc": "x",
    }
    (d / "request.json").write_text(json.dumps(req), encoding="utf-8")
    return d


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_verify(tmp_path):
    hr = HostRoot(tmp_path)
    hr.lock(RUN_A, SHA_A)
    _upload(hr, RUN_A, SHA_A, SHA_B)
    got = hr.ps("host-prepare.ps1", "-RunId", RUN_A, "-Stage", "verify")
    assert got["reason"] == "commit-mismatch", got
    _upload(hr, RUN_B, SHA_B, SHA_B)
    hr.lock(RUN_B, SHA_B)
    assert hr.ps("host-prepare.ps1", "-RunId", RUN_B, "-Stage", "verify")["reason"] == "ok"
    (hr.root / "runs" / RUN_B / "publish" / STUB_NAMES[0]).write_bytes(b"changed")
    got = hr.ps("host-prepare.ps1", "-RunId", RUN_B, "-Stage", "verify")
    assert got["reason"] == "upload-mismatch", got
    hr.lock(RUN_A, SHA_A)
    got = hr.ps("host-prepare.ps1", "-RunId", RUN_B, "-Stage", "verify")
    assert got["reason"] == "host-locked", got


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_extract_resets_times(tmp_path):
    hr = HostRoot(tmp_path)
    hr.lock(RUN_A, SHA_A)
    d = _upload(hr, RUN_A, SHA_A, SHA_A, datetime.now() + timedelta(hours=3))
    got = hr.ps("host-prepare.ps1", "-RunId", RUN_A, "-Stage", "extract")
    now = time.time()
    assert got["reason"] == "ok", got
    assert got["mtime_skew_s"] >= 10000, got
    assert got["commit_offset_s"] >= 10000 + 3600 - 120, got
    tree = d / "tree"
    for name in ("ui/src/a.ts", "ui/package.json", "ui/tests/e2e/x.test.ts", ".node-version"):
        assert (tree / name).stat().st_mtime <= now - 100, name
    for sub in ("ui", "ui/src", "ui/tests/e2e"):
        assert (tree / sub).stat().st_mtime <= now - 100, sub
    for n in STUB_NAMES:
        assert (
            tree / "native/region-picker-stub/publish" / n
        ).read_bytes() == b"stub " + n.encode()
    assert (tree / ".avkit-remote-tree").read_text(encoding="utf-8-sig").strip() == SHA_A
    got = hr.ps("host-prepare.ps1", "-RunId", RUN_A, "-Stage", "extract")
    assert got["reason"] != "ok", got


def _tree(hr: HostRoot, run_id: str, sha: str, build_sha: str | None, stale: bool) -> Path:
    tree = hr.run_dir(run_id) / "tree"
    files = {
        "ui/src/main/index.ts": 0,
        "ui/electron.vite.config.ts": 0,
        "ui/src/renderer/src/primitive-harness.tsx": 0,
        "ui/out/main/index.js": 60,
        "ui/out-e2e/renderer/primitive-harness.html": 60,
        "ui/out-e2e/main/index.js": 60,
    }
    base = time.time() - 3600
    for rel, offset in files.items():
        p = tree / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="ascii")
        os.utime(p, (base + offset, base + offset))
    if stale:
        os.utime(tree / "ui/src/main/index.ts", (base + 600, base + 600))
    (tree / ".avkit-remote-tree").write_text(sha, encoding="ascii")
    if build_sha is not None:
        (tree / ".avkit-remote-build").write_text(build_sha, encoding="ascii")
    return tree


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_stale(tmp_path):
    hr = HostRoot(tmp_path)
    hr.lock(RUN_A, SHA_A)
    _tree(hr, RUN_A, SHA_A, SHA_A, stale=False)
    got = hr.ps("host-prepare.ps1", "-RunId", RUN_A, "-Stage", "stale")
    assert got["reason"] == "ok", got
    _tree(hr, RUN_A, SHA_A, SHA_A, stale=True)
    got = hr.ps("host-prepare.ps1", "-RunId", RUN_A, "-Stage", "stale")
    assert got["reason"] == "build-stale", got
    _tree(hr, RUN_A, SHA_A, SHA_B, stale=False)
    got = hr.ps("host-prepare.ps1", "-RunId", RUN_A, "-Stage", "stale")
    assert got["reason"] == "build-stale", got


def _launch(hr: HostRoot) -> None:
    shutil.copyfile(HOST / "run-e2e.ps1", hr.root / "run-e2e.ps1")
    hr.ps("run-e2e.ps1", where=hr.root)


def _done(hr: HostRoot, run_id: str) -> str:
    return (hr.root / "results" / run_id / "DONE").read_text(encoding="utf-8-sig").strip()


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_launcher_95(tmp_path):
    hr = HostRoot(tmp_path)
    hr.lock(RUN_A, SHA_A)
    _launch(hr)
    assert _done(hr, RUN_A) == "95"
    assert not (hr.root / "results" / RUN_A / "DONE.tmp").exists()
    assert (hr.root / "results" / RUN_A / "meta.txt").is_file()
    _launch(hr)
    dups = [p.name for p in (hr.root / "results").iterdir() if p.name.startswith("dup-")]
    assert len(dups) == 1, dups
    assert (hr.root / "results" / dups[0] / "DONE").read_text(encoding="utf-8-sig").strip() == "95"


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_launcher_no_lock(tmp_path):
    hr = HostRoot(tmp_path)
    _launch(hr)
    names = [p.name for p in (hr.root / "results").iterdir()]
    assert len(names) == 1 and names[0].startswith("no-lock-"), names
    assert (hr.root / "results" / names[0] / "DONE").read_text(encoding="utf-8-sig").strip() == "95"


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_launcher_98(tmp_path):
    hr = HostRoot(tmp_path)
    hr.lock(RUN_A, SHA_A)
    _upload(hr, RUN_A, SHA_A, SHA_A)
    _tree(hr, RUN_A, SHA_B, SHA_A, stale=False)
    _launch(hr)
    assert _done(hr, RUN_A) == "98"


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_launcher_99(tmp_path):
    hr = HostRoot(tmp_path)
    hr.lock(RUN_A, SHA_A)
    _upload(hr, RUN_A, SHA_A, SHA_A)
    _tree(hr, RUN_A, SHA_A, SHA_A, stale=True)
    _launch(hr)
    assert _done(hr, RUN_A) == "99"
    assert not (hr.root / "results" / RUN_A / "pid.txt").exists()


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_start_other_lock(tmp_path):
    hr = HostRoot(tmp_path)
    hr.lock(RUN_A, SHA_A)
    got = hr.ps("host-start.ps1", "-RunId", RUN_B)
    assert got["reason"] == "host-locked", got
    assert not (hr.root / "results").exists()
    assert not (hr.root / "run-e2e.ps1").exists()


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_host_fixture_status(tmp_path):
    hr = HostRoot(tmp_path)
    hr.lock(RUN_A, SHA_A)
    res = hr.root / "results" / RUN_A
    res.mkdir(parents=True)
    (res / "DONE").write_text("1", encoding="ascii")
    (res / "pid.txt").write_text("4100\n" + START + "\n", encoding="ascii")
    got = hr.ps("host-status.ps1", "-RunId", RUN_A)
    assert got["reason"] == "ok", got
    assert got["done"] == 1 and got["lock"]["run_id"] == RUN_A, got
    assert got["pid_file"] == {"pid": 4100, "start": START}, got
    assert isinstance(got["user_procs"], list)


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_roundtrip_made_up_user(tmp_path, monkeypatch):
    m = _load()
    f = _facts_on_this_pc(tmp_path, "avkit-nobody-user", ["avkit-nobody-q"])
    cfg = dict(CFG, user="avkit-nobody-user", busy_users=["avkit-nobody-q"])
    got = list(m.evaluate(f, cfg, node_major()))
    assert got[0][0] == "no-desktop-session", got


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_roundtrip_current_account(tmp_path):
    m = _load()
    me = os.environ.get("USERNAME", "")
    assert me
    f = _facts_on_this_pc(tmp_path, me, ["avkit-nobody-q"])
    cfg = dict(CFG, user=me, busy_users=["avkit-nobody-q"])
    reasons = [r for r, _ in m.evaluate(f, cfg, node_major())]
    mine = [
        e
        for e in f["explorer"]
        if e["user"].rsplit("\\", 1)[-1].lower() == me.lower() and e["session"] != 0
    ]
    no_desktop = not mine or f["user_session"]["state"] != "Active"
    assert ("no-desktop-session" in reasons) == no_desktop, (reasons, f["explorer"])


@pytest.mark.skipif(not ON_WINDOWS, reason=WINDOWS_ONLY)
def test_ac_15_roundtrip_busy_users(tmp_path):
    m = _load()
    me = os.environ.get("USERNAME", "")
    f = _facts_on_this_pc(tmp_path, me, ["avkit-nobody-q"])
    cfg = dict(CFG, user=me, busy_users=["avkit-nobody-q"])
    got = list(m.evaluate(f, cfg, node_major()))
    assert f["busy_users_missing"] == ["avkit-nobody-q"]
    assert not [d for r, d in got if r == "host-busy" and "avkit-nobody-q" in d], got
    if not f["elevated"]:
        assert "host-busy-unknown" in [r for r, _ in got], got
    else:
        assert "host-busy-unknown" not in [r for r, _ in got] or f["owners_seen"] == 0, got


# --- AC-19: the run book --------------------------------------------------------------------


def test_ac_19_run_book_names_everything():
    m = _load()
    assert RUN_BOOK.is_file(), ".agent/docs/e2e-remote-host.md does not exist yet"
    text = RUN_BOOK.read_text(encoding="utf-8")
    for reason, code in m.REASONS.items():
        assert f"`{reason}`" in text, reason
        assert re.search(r"(?<!\d)" + str(code) + r"(?!\d)", text), (reason, code)
    for pid in m.PREREQ_IDS:
        assert f"`{pid}`" in text, pid
    for key in CONFIG_KEYS:
        assert f"`{key}`" in text, key
    for sub in SUBCOMMANDS:
        assert f"e2e_remote.py {sub}" in text, sub
    assert "known-failures.json" in text
    assert "Session 97" in text


def test_ac_19_run_book_lists_every_reason_once_in_the_table():
    m = _load()
    assert RUN_BOOK.is_file(), ".agent/docs/e2e-remote-host.md does not exist yet"
    text = RUN_BOOK.read_text(encoding="utf-8")
    rows = [ln for ln in text.splitlines() if ln.startswith("| ") and "`" in ln]
    for reason, code in m.REASONS.items():
        hits = [r for r in rows if re.match(r"\| " + str(code) + r" \|", r) and f"`{reason}`" in r]
        assert hits, (reason, code)


# --- AC-21: no host details in the new tracked files ----------------------------------------


def _new_files() -> list[Path]:
    files = [TOOL, EXAMPLE, KNOWN, RUN_BOOK, Path(__file__).resolve()]
    files += [HOST / n for n in SCRIPTS]
    return files


def test_ac_21_no_host_details_in_new_files():
    for p in _new_files():
        assert p.is_file(), f"{p.relative_to(ROOT).as_posix()} does not exist yet"
    for p in _new_files():
        text = p.read_text(encoding="utf-8")
        name = p.relative_to(ROOT).as_posix()
        assert not IPV4.search(text), (name, IPV4.search(text))
        for word in (HOME_WIN, HOME_POSIX, *SSH_DIRS):
            assert word.lower() not in text.lower(), (name, word)


def test_ac_21_no_host_details_scan_catches_a_hit(tmp_path):
    for p in _new_files():
        assert p.is_file(), f"{p.relative_to(ROOT).as_posix()} does not exist yet"
    bad = tmp_path / "bad.txt"
    bad.write_text(
        "host 10.0" + ".0.5 and " + HOME_WIN + "\\x and ~" + SSH_DIRS[1], encoding="utf-8"
    )
    text = bad.read_text(encoding="utf-8")
    assert IPV4.search(text)
    assert HOME_WIN.lower() in text.lower() and SSH_DIRS[1] in text
