"""MEU-141: the JS runtime lookup (`JS_RUNTIME_LOOKUP`) and Deno's version probe (`RUNTIME_HEALTH`).

`shutil.which` and `subprocess.run` are patched on their modules, so no test sees this machine's
Deno and nothing runs. A wrong exception is caught and asserted on, so every failure here is an
assertion (red-check).
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from structlog.testing import capture_logs

from avkit_infra.youtube.js_runtime import JsRuntime, JsRuntimeLocator, probe_deno_version

#: A marker that must never reach a log line (Session 53 RULE-1).
MARKER = "zq-marker-7741"
DENO_VERSION_TEXT = (
    "deno 2.9.8 (stable, release, x86_64-pc-windows-msvc)\nv8 14.3.127.12-rusty\ntypescript 5.9.2\n"
)


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"MZ")
    return path


def _which(monkeypatch: pytest.MonkeyPatch, found: Path | None) -> list[str]:
    """`shutil.which("deno")` gives `found`; every other name gives None. The names asked."""
    asked: list[str] = []

    def fake_which(name: str, *args: Any, **kwargs: Any) -> str | None:
        del args, kwargs
        asked.append(name)
        return str(found) if name == "deno" and found is not None else None

    monkeypatch.setattr("shutil.which", fake_which)
    return asked


def _resolve(locator: JsRuntimeLocator) -> tuple[JsRuntime | None, BaseException | None]:
    try:
        return locator.resolve(), None
    except Exception as exc:  # noqa: BLE001 - the exception is the observation
        return None, exc


def _same(found: JsRuntime | None, path: Path, source: str) -> tuple[object, ...]:
    """What the lookup found, as (name, source, same file) so a miss reads as one line."""
    if found is None:
        return (None, None, False)
    same = found.path.exists() and path.exists() and os.path.samefile(found.path, path)
    return (found.name, found.source, same)


# --- AC-141.2: JS_RUNTIME_LOOKUP order ------------------------------------------------------------

#: (id, setting file?, bundle file?, PATH file?, expected source). "dir" names a folder.
ORDER_ROWS = [
    ("all_three_setting_wins", "file", True, True, "setting"),
    ("setting_and_bundle_setting_wins", "file", True, False, "setting"),
    ("setting_and_path_setting_wins", "file", False, True, "setting"),
    ("bundle_and_path_bundle_wins", "", True, True, "bundled"),
    ("bundle_only", "", True, False, "bundled"),
    ("path_only", "", False, True, "path"),
    ("missing_setting_file_bundle_wins", "missing", True, True, "bundled"),
    ("missing_setting_file_path_wins", "missing", False, True, "path"),
    ("setting_names_a_folder_bundle_wins", "dir", True, True, "bundled"),
]


@pytest.mark.parametrize(
    ("setting", "bundle", "on_path", "expected"),
    [pytest.param(*row[1:], id=row[0]) for row in ORDER_ROWS],
)
def test_ac_141_2_lookup_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    setting: str,
    bundle: bool,
    on_path: bool,
    expected: str,
) -> None:
    chosen = _touch(tmp_path / "chosen" / "deno.exe")
    bundled = _touch(tmp_path / "resources" / "deno" / "deno.exe")
    path_bin = _touch(tmp_path / "path-bin" / "deno.exe")
    values = {
        "file": str(chosen),
        "": "",
        "missing": str(tmp_path / "gone" / "deno.exe"),
        "dir": str(tmp_path / "chosen"),
    }
    _which(monkeypatch, path_bin if on_path else None)
    locator = JsRuntimeLocator(lambda: values[setting], bundled if bundle else None)
    found, raised = _resolve(locator)
    assert raised is None, repr(raised)
    want = {"setting": chosen, "bundled": bundled, "path": path_bin}[expected]
    assert _same(found, want, expected) == ("deno", expected, True)


def test_ac_141_2_nothing_found_gives_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _which(monkeypatch, None)
    found, raised = _resolve(JsRuntimeLocator(lambda: "", tmp_path / "absent" / "deno.exe"))
    assert raised is None, repr(raised)
    assert found is None


def test_ac_141_2_no_setting_reader_still_finds_the_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundled = _touch(tmp_path / "resources" / "deno" / "deno.exe")
    _which(monkeypatch, None)
    found, raised = _resolve(JsRuntimeLocator(None, bundled))
    assert raised is None, repr(raised)
    assert _same(found, bundled, "bundled") == ("deno", "bundled", True)


def test_ac_141_2_missing_bundle_falls_to_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path_bin = _touch(tmp_path / "path-bin" / "deno.exe")
    _which(monkeypatch, path_bin)
    found, raised = _resolve(JsRuntimeLocator(lambda: "", tmp_path / "absent" / "deno.exe"))
    assert raised is None, repr(raised)
    assert _same(found, path_bin, "path") == ("deno", "path", True)


def test_ac_141_2_setting_is_read_at_every_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = _touch(tmp_path / "one" / "deno.exe")
    second = _touch(tmp_path / "two" / "deno.exe")
    _which(monkeypatch, None)
    current = {"value": str(first)}
    reads: list[int] = []

    def configured() -> object:
        reads.append(1)
        return current["value"]

    locator = JsRuntimeLocator(configured, None)
    found_one, raised_one = _resolve(locator)
    current["value"] = str(second)
    found_two, raised_two = _resolve(locator)
    assert (raised_one, raised_two) == (None, None)
    assert _same(found_one, first, "setting") == ("deno", "setting", True)
    assert _same(found_two, second, "setting") == ("deno", "setting", True)
    assert len(reads) >= 2


def test_ac_141_2_setting_expands_the_home_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "home"
    chosen = _touch(home / "deno" / "deno.exe")
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("HOME", str(home))
    _which(monkeypatch, None)
    found, raised = _resolve(JsRuntimeLocator(lambda: "~/deno/deno.exe", None))
    assert raised is None, repr(raised)
    assert _same(found, chosen, "setting") == ("deno", "setting", True)


# --- AC-141.3: unusable setting values fall through -----------------------------------------------

UNUSABLE: list[Any] = [
    pytest.param(None, id="none"),
    pytest.param(7, id="int"),
    pytest.param(True, id="bool"),
    pytest.param(f"C:/{MARKER}/deno.exe".encode(), id="bytes"),
    pytest.param("", id="empty"),
    pytest.param("   ", id="spaces"),
    pytest.param(f"C:/{MARKER}\x00/deno.exe", id="nul"),
    pytest.param(f"C:/{MARKER}\x07/deno.exe", id="control_character"),
    pytest.param(f"C:/{MARKER}\ud800/deno.exe", id="lone_surrogate"),
    pytest.param("C:/" + MARKER + "/" + "x" * 40000 + "/deno.exe", id="too_long"),
]


@pytest.mark.parametrize("value", UNUSABLE)
def test_ac_141_3_unusable_setting_falls_through(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, value: object
) -> None:
    bundled = _touch(tmp_path / "resources" / "deno" / "deno.exe")
    _which(monkeypatch, None)
    with capture_logs() as logs:
        found, raised = _resolve(JsRuntimeLocator(lambda: value, bundled))
    assert raised is None, repr(raised)
    assert _same(found, bundled, "bundled") == ("deno", "bundled", True)
    assert [entry for entry in logs if MARKER in repr(entry)] == []


def test_ac_141_3_a_raising_setting_reader_falls_through(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundled = _touch(tmp_path / "resources" / "deno" / "deno.exe")
    _which(monkeypatch, None)

    def configured() -> object:
        raise OSError(MARKER)

    with capture_logs() as logs:
        found, raised = _resolve(JsRuntimeLocator(configured, bundled))
    assert raised is None, repr(raised)
    assert _same(found, bundled, "bundled") == ("deno", "bundled", True)
    assert [entry for entry in logs if MARKER in repr(entry)] == []


# --- AC-141.7: the version probe ------------------------------------------------------------------


def _run(
    monkeypatch: pytest.MonkeyPatch, outcome: Callable[[list[str]], object]
) -> list[tuple[list[str], dict[str, Any]]]:
    """`subprocess.run` gives `outcome(cmd)` as stdout, or raises it; the calls it saw."""
    calls: list[tuple[list[str], dict[str, Any]]] = []

    def fake_run(cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        del args
        calls.append((list(cmd), dict(kwargs)))
        result = outcome(list(cmd))
        if isinstance(result, BaseException):
            raise result
        return subprocess.CompletedProcess(cmd, 0, result, "")

    monkeypatch.setattr("subprocess.run", fake_run)
    return calls


def _probe(path: Path) -> tuple[str | None, BaseException | None]:
    try:
        return probe_deno_version(path), None
    except Exception as exc:  # noqa: BLE001 - the exception is the observation
        return None, exc


def test_ac_141_7_parses_the_first_line(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    deno = _touch(tmp_path / "deno.exe")
    calls = _run(monkeypatch, lambda cmd: DENO_VERSION_TEXT)
    version, raised = _probe(deno)
    assert raised is None, repr(raised)
    assert version == "2.9.8"
    assert len(calls) == 1
    cmd, kwargs = calls[0]
    assert cmd == [str(deno), "--version"]
    timeout = kwargs.get("timeout")
    assert isinstance(timeout, int | float) and 0 < timeout <= 5, timeout


UNPARSED: list[Any] = [
    pytest.param(subprocess.TimeoutExpired(["deno"], 5), id="timeout"),
    pytest.param(OSError("no exec"), id="oserror"),
    pytest.param(UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad"), id="undecodable"),
    pytest.param("garbage line\n", id="garbage"),
    pytest.param("", id="empty"),
    pytest.param("   \n", id="whitespace"),
    pytest.param("deno 2.9\n", id="two_parts"),
    pytest.param(None, id="stdout_none"),
    pytest.param(f"node {MARKER} 2.9.8\n", id="other_name"),
]


@pytest.mark.parametrize("outcome", UNPARSED)
def test_ac_141_7_unparsed_output_gives_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, outcome: object
) -> None:
    deno = _touch(tmp_path / "deno.exe")
    _run(monkeypatch, lambda cmd: outcome)
    with capture_logs() as logs:
        version, raised = _probe(deno)
    assert raised is None, repr(raised)
    assert version is None
    assert [entry for entry in logs if MARKER in repr(entry)] == []


def test_ac_141_7_no_output_text_leaves_the_probe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    deno = _touch(tmp_path / "deno.exe")
    calls = _run(monkeypatch, lambda cmd: f"deno 2.9.8 ({MARKER})\nv8 {MARKER}\n")
    with capture_logs() as logs:
        version, raised = _probe(deno)
    assert raised is None, repr(raised)
    assert len(calls) == 1
    assert version == "2.9.8"
    assert [entry for entry in logs if MARKER in repr(entry)] == []
