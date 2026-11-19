"""Session 95 (eval-describe-raw-bytes) tests for Session 64's eval-describe.py (AC-1 to AC-7).

The script lives beside eval-run.md in docs/execution/plans/2026-11-11-capture-export-copy/ and
these tests run by path from this plan folder (D-1202). Every test asserts SCRIPT.is_file() first
and loads the module inside its body, so before the script exists each test fails by assertion
and none by collection. The file is ASCII only: every arrow, dash and mojibake string is built
from escapes. Bytecode writing is off, so no .pyc lands in Session 64's or Session 92's folder.
"""

from __future__ import annotations

import builtins
import errno
import hashlib
import importlib.util
import re
import subprocess
import sys
import time
import types
from pathlib import Path

import pytest

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parents[4]
SCRIPT = REPO / "docs/execution/plans/2026-11-11-capture-export-copy/eval-describe.py"
GUARD_FILE = REPO / "docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py"


def _load_separate_guard():
    """A second, independent load of Session 92's eval-rerun.py (for CUT and AC-5)."""
    spec = importlib.util.spec_from_file_location("s95_test_guard_copy", GUARD_FILE)
    assert spec is not None and spec.loader is not None, "Session 92's eval-rerun.py is missing"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SEPARATE = _load_separate_guard()
CUT = SEPARATE.CUT
ARROW = "\u2192"
DASH = "\u2013"
CLEAN = (
    "## Server instructions\n\nA " + ARROW + " B " + DASH + " C\n"
    "## avkit_capture description\n\nx "
    + ARROW
    + " y "
    + DASH
    + " z\n"
    + CUT
    + "\n\n- avkit_capture.crop: c\n"
)
CLEAN_BYTES = CLEAN.encode("utf-8")
# The real arrow and dash bytes decoded through cp437, as PowerShell's redirect does.
MOJ = CLEAN_BYTES.decode("cp437").encode("utf-8")
MOJ_ARROW = ARROW.encode("utf-8").decode("cp437")
MOJ_DASH = DASH.encode("utf-8").decode("cp437")


def load():
    """The script as a fresh module; asserts it exists first (the Red reason)."""
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("s95_eval_describe", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def names(reasons):
    return [r[0] for r in reasons]


def run(ed, argv, capsys):
    """main(argv) as (exit code, stdout, stderr); every line it prints must be ASCII."""
    capsys.readouterr()
    try:
        code = ed.main(argv)
    except SystemExit as exc:
        code = exc.code
    out, err = capsys.readouterr()
    assert out.isascii(), f"stdout is not ASCII: {out!a}"
    assert err.isascii(), f"stderr is not ASCII: {err!a}"
    return (0 if code is None else code), out, err


def write(tmp_path, name, data: bytes) -> str:
    path = tmp_path / name
    path.write_bytes(data)
    return str(path)


def fake_child(monkeypatch, ed, tmp_path, code: str):
    """command() returns a Python child; BASE moves under tmp_path. Returns a root under BASE."""
    base = (tmp_path / "base").as_posix() + "/"
    monkeypatch.setattr(ed, "BASE", base)
    monkeypatch.setattr(ed, "command", lambda root: ([sys.executable, "-c", code], str(tmp_path)))
    return base + "r1/root"


def writer(data: bytes, exit_code: int = 0, marker: Path | None = None) -> str:
    lines = ["import sys"]
    if marker is not None:
        lines.append(f"open({str(marker)!r}, 'w').close()")
    lines.append(f"sys.stdout.buffer.write({data!r})")
    lines.append("sys.stdout.buffer.flush()")
    lines.append("sys.stderr.write('child-note\\n')")
    lines.append(f"sys.exit({exit_code})")
    return "\n".join(lines)


def side(out: Path, suffix: str) -> Path:
    return out.with_name(out.name + suffix)


# AC-1 ------------------------------------------------------------------------------------


def test_ac_1_clean_passes(tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    assert ed.refusals(CLEAN_BYTES) == []
    f = write(tmp_path, "clean.txt", CLEAN_BYTES)
    code, out, _ = run(ed, ["check", f], capsys)
    assert code == 0
    assert out.startswith("ok:")


# AC-2 ------------------------------------------------------------------------------------


def test_ac_2_cp437_fixture_refused(tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    assert MOJ_ARROW in MOJ.decode("utf-8") and MOJ_DASH in MOJ.decode("utf-8")
    assert names(ed.refusals(MOJ)) == ["mojibake"]
    f = write(tmp_path, "moj.txt", MOJ)
    code, out, _ = run(ed, ["check", f], capsys)
    assert code == 1
    assert "refused:" in out and "mojibake" in out


def test_ac_2_cp437_crlf_refused(tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    moj_crlf = MOJ.replace(b"\n", b"\r\n")
    assert names(ed.refusals(moj_crlf)) == ["cr", "mojibake"]
    f = write(tmp_path, "moj-crlf.txt", moj_crlf)
    code, out, _ = run(ed, ["check", f], capsys)
    assert code == 1
    assert "cr" in out and "mojibake" in out


# AC-3 ------------------------------------------------------------------------------------


def test_ac_3_mixed_arrow_refused(tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    mixed = CLEAN.replace("A " + ARROW + " B " + DASH, "A " + ARROW + " B " + MOJ_DASH)
    assert ARROW in mixed and MOJ_DASH in mixed
    data = mixed.encode("utf-8")
    assert "mojibake" in names(ed.refusals(data))
    code, out, _ = run(ed, ["check", write(tmp_path, "mixed-arrow.txt", data)], capsys)
    assert code == 1 and "mojibake" in out


def test_ac_3_mixed_dash_refused(tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    mixed = CLEAN.replace("A " + ARROW + " B " + DASH, "A " + MOJ_ARROW + " B " + DASH)
    assert DASH in mixed and MOJ_ARROW in mixed
    data = mixed.encode("utf-8")
    assert "mojibake" in names(ed.refusals(data))
    code, out, _ = run(ed, ["check", write(tmp_path, "mixed-dash.txt", data)], capsys)
    assert code == 1 and "mojibake" in out


# AC-4 ------------------------------------------------------------------------------------

AC4_CASES = {
    "empty": (b"", "empty"),
    "utf8-bom": (b"\xef\xbb\xbf" + CLEAN_BYTES, "bom"),
    "utf16-bom": (b"\xff\xfe" + CLEAN.encode("utf-16-le"), "bom"),
    "invalid-utf8": (CLEAN_BYTES + b"\x80", "not-utf8"),
    "bare-cr": (CLEAN.replace("B ", "B\r", 1).encode("utf-8"), "cr"),
    "no-cut": (CLEAN.replace(CUT + "\n", "").encode("utf-8"), "cut"),
    "two-cuts": (CLEAN.replace(CUT, CUT + "\n" + CUT).encode("utf-8"), "cut"),
}


@pytest.mark.parametrize("case", list(AC4_CASES))
def test_ac_4_refuses(case, tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    data, reason = AC4_CASES[case]
    got = names(ed.refusals(data))
    assert reason in got, f"{case}: expected {reason!r} in {got!r}"
    code, out, _ = run(ed, ["check", write(tmp_path, f"{case}.txt", data)], capsys)
    if case == "empty":
        assert code == 1 and "refused:" in out and "empty" in out
    else:
        assert code == 1 and "refused:" in out and reason in out


# AC-5 ------------------------------------------------------------------------------------


def test_ac_5_one_guard():
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    assert ed.GUARD is not None, f"guard not loaded: {ed.GUARD_ERROR}"
    assert Path(ed.GUARD.__file__).resolve() == GUARD_FILE.resolve()
    assert Path(ed.GUARD_PATH).resolve() == GUARD_FILE.resolve()
    assert ed.GUARD.CUT == SEPARATE.CUT
    assert "MOJIBAKE" not in vars(ed) and "CUT" not in vars(ed), "a module-level copy"
    src = SCRIPT.read_text(encoding="utf-8")
    assert "re.compile" not in src
    assert "cp437" not in src.lower()
    assert re.search(r"^\s*MOJIBAKE\s*=(?!=)", src, flags=re.M) is None
    assert "MOJIBAKE =" not in src


def test_ac_5_stub_guard_used(monkeypatch):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    stub = types.SimpleNamespace(MOJIBAKE=re.compile("ZZ"), CUT=SEPARATE.CUT)
    monkeypatch.setattr(ed, "GUARD", stub)
    zz = CLEAN.replace("x ", "ZZ x ", 1).encode("utf-8")
    assert "mojibake" in names(ed.refusals(zz))
    assert "mojibake" not in names(ed.refusals(MOJ))


# AC-6 ------------------------------------------------------------------------------------


def test_ac_6_capture_writes_child_bytes(monkeypatch, tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    root = fake_child(monkeypatch, ed, tmp_path, writer(CLEAN_BYTES))
    out = tmp_path / "out.txt"
    code, stdout, _ = run(ed, ["capture", root, str(out)], capsys)
    assert code == 0
    assert out.read_bytes() == CLEAN_BYTES
    assert b"child-note" in side(out, ".stderr.txt").read_bytes()
    assert not side(out, ".refused").exists()
    assert stdout.startswith("captured:")
    assert hashlib.sha256(CLEAN_BYTES).hexdigest() in stdout


def test_ac_6_capture_never_overwrites(monkeypatch, tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    for suffix in ("", ".stderr.txt", ".refused"):
        work = tmp_path / f"case{suffix or '-out'}"
        work.mkdir()
        marker = work / "child-ran"
        root = fake_child(monkeypatch, ed, work, writer(CLEAN_BYTES, marker=marker))
        out = work / "out.txt"
        held = side(out, suffix)
        held.write_bytes(b"held")
        code, _, _ = run(ed, ["capture", root, str(out)], capsys)
        assert code == 2, f"{suffix or 'OUT'}: exit {code}"
        assert not marker.exists(), f"{suffix or 'OUT'}: the child ran"
        assert held.read_bytes() == b"held"


def test_ac_6_capture_refuses_child_exit(monkeypatch, tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    root = fake_child(monkeypatch, ed, tmp_path, writer(CLEAN_BYTES, exit_code=3))
    out = tmp_path / "out.txt"
    code, stdout, _ = run(ed, ["capture", root, str(out)], capsys)
    assert code == 1
    assert "refused:" in stdout and "harness-exit" in stdout
    assert not out.exists()


def test_ac_6_capture_refuses_mojibake_child(monkeypatch, tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    root = fake_child(monkeypatch, ed, tmp_path, writer(MOJ))
    out = tmp_path / "out.txt"
    code, stdout, _ = run(ed, ["capture", root, str(out)], capsys)
    assert code == 1
    assert "refused:" in stdout and "mojibake" in stdout
    assert side(out, ".refused").read_bytes() == MOJ
    assert not out.exists()


def test_ac_6_capture_refuses_timeout(monkeypatch, tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    root = fake_child(monkeypatch, ed, tmp_path, "import time\ntime.sleep(60)")
    monkeypatch.setattr(ed, "DESCRIBE_TIMEOUT_S", 2)
    out = tmp_path / "out.txt"
    start = time.monotonic()
    code, stdout, _ = run(ed, ["capture", root, str(out)], capsys)
    elapsed = time.monotonic() - start
    assert code == 1
    assert "refused:" in stdout and "timeout" in stdout
    assert elapsed < 30, f"the timed-out child held capture for {elapsed:.1f} s"
    assert not out.exists()


def test_ac_6_capture_refuses_root_outside_base(monkeypatch, tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    marker = tmp_path / "child-ran"
    fake_child(monkeypatch, ed, tmp_path, writer(CLEAN_BYTES, marker=marker))
    out = tmp_path / "out.txt"
    outside = (tmp_path / "elsewhere/root").as_posix()
    code, _, _ = run(ed, ["capture", outside, str(out)], capsys)
    assert code == 2
    assert not marker.exists()
    assert not out.exists()


class FailingFile:
    """A real exclusive-create handle that fails on write (after the CUT line) or on close."""

    def __init__(self, path, fail: str):
        self.handle = builtins.open(path, "xb")
        self.fail = fail

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    def write(self, data: bytes) -> int:
        if self.fail == "close":
            return self.handle.write(data)
        cut = data.find(CUT.encode("ascii"))
        keep = data[: cut + len(CUT) + 1] if cut >= 0 else data[: max(1, len(data) // 2)]
        self.handle.write(keep)
        self.handle.flush()
        raise OSError(errno.ENOSPC, "test fixture: disk full")

    def close(self) -> None:
        if self.handle.closed:
            return
        self.handle.close()
        if self.fail == "close":
            raise OSError(errno.EIO, "test fixture: close failed")


# F1 of the round-1 execution review: a write or close error after the exclusive create must
# leave no partial file behind (RAW_CAPTURE: exactly the child's bytes, or no OUT at all).
@pytest.mark.parametrize(
    ("suffix", "fail"),
    [("", "write"), ("", "close"), (".stderr.txt", "write"), (".refused", "write")],
    ids=["out-write", "out-close", "stderr-write", "refused-write"],
)
def test_ac_6_capture_write_failure_leaves_no_file(monkeypatch, tmp_path, capsys, suffix, fail):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    data = MOJ if suffix == ".refused" else CLEAN_BYTES
    root = fake_child(monkeypatch, ed, tmp_path, writer(data))
    out = tmp_path / "out.txt"
    target = side(out, suffix)
    real_open = builtins.open

    def failing_open(path, mode="r", *args, **kwargs):
        if Path(path) == target and mode == "xb":
            return FailingFile(path, fail)
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(ed, "open", failing_open, raising=False)
    code, stdout, stderr = run(ed, ["capture", root, str(out)], capsys)
    assert code == 2, f"exit {code}: {stdout!a}"
    assert stdout.startswith("error: OSError:"), stdout
    assert "Traceback" not in stdout + stderr
    assert not target.exists(), f"{target.name} survives the {fail} failure"
    assert not out.exists(), "OUT exists after a failed capture"


# AC-7 ------------------------------------------------------------------------------------


@pytest.mark.parametrize("argv", [[], ["frobnicate"], ["check", "MISSING"]], ids=str)
def test_ac_7_cli_usage(argv, tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    args = [str(tmp_path / "missing.txt") if a == "MISSING" else a for a in argv]
    code, _, _ = run(ed, args, capsys)
    assert code == 2


def test_ac_7_cli_build_first(monkeypatch, tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    monkeypatch.setattr(ed, "DIST", tmp_path / "missing/dist/index.js")
    out = tmp_path / "out.txt"
    root = ed.BASE + "s95-test-nodist/root"
    code, stdout, stderr = run(ed, ["capture", root, str(out)], capsys)
    assert code == 2
    assert "build first" in stdout + stderr
    assert not out.exists() and not side(out, ".stderr.txt").exists()


def test_ac_7_guard_missing(monkeypatch, tmp_path, capsys):
    assert SCRIPT.is_file(), f"eval-describe.py is not written yet: {SCRIPT.as_posix()}"
    ed = load()
    # 1: a guard file that is not there raises OSError.
    with pytest.raises(OSError):
        ed.load_guard(tmp_path / "none.py")
    # 2: the module-level try, in a child where every spec comes back empty.
    f = write(tmp_path, "clean.txt", CLEAN_BYTES)
    child = "\n".join(
        [
            "import importlib.util, runpy, sys",
            "sys.dont_write_bytecode = True",
            "importlib.util.spec_from_file_location = lambda *a, **k: None",
            f"sys.argv = [{str(SCRIPT)!r}, 'check', {f!r}]",
            f"runpy.run_path({str(SCRIPT)!r}, run_name='__main__')",
        ]
    )
    proc = subprocess.run(
        [sys.executable, "-I", "-c", child], capture_output=True, timeout=120, check=False
    )
    assert proc.returncode == 2, f"exit {proc.returncode}: {proc.stdout!a} {proc.stderr!a}"
    assert proc.stdout.startswith(b"error: guard not loaded:")
    assert proc.stdout.isascii() and proc.stderr.isascii()
    assert b"Traceback" not in proc.stderr
    # 3: with no guard, capture starts no child and writes no OUT.
    monkeypatch.setattr(ed, "GUARD", None)
    marker = tmp_path / "child-ran"
    root = fake_child(monkeypatch, ed, tmp_path, writer(CLEAN_BYTES, marker=marker))
    out = tmp_path / "out.txt"
    code, stdout, _ = run(ed, ["capture", root, str(out)], capsys)
    assert code == 2
    assert stdout.startswith("error: guard not loaded:")
    assert not marker.exists()
    assert not out.exists() and not side(out, ".stderr.txt").exists()
