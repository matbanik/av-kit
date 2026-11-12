"""MEU-141: the runtime reaches yt-dlp and Health live (`JS_RUNTIME_OPTS`, `RUNTIME_HEALTH`).

`build_services` builds the real stack. `shutil.which` and `subprocess.run` are patched on their
modules and `bundled_deno` on `avkit_api.wiring`, so no test sees this machine's Deno and nothing
runs. `YoutubeDL` is the scripted fake of the MEU-140 tests. Every failure is an assertion.
"""

from __future__ import annotations

import inspect
import subprocess
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from tests.integration.test_youtube_adapter import (
    SABR_PROBE_URL,
    _download_error,
    _options,
    _video_info_payload,
)
from tests.integration.test_youtube_client_fallback import RELOAD, URL, _info, _script

from avkit_api.main import create_app
from avkit_api.wiring import build_services
from avkit_infra.youtube.js_runtime import JsRuntime

pytestmark = pytest.mark.integration

TOKEN = "s66-runtime-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}
DENO_VERSION_TEXT = (
    "deno 2.9.8 (stable, release, x86_64-pc-windows-msvc)\nv8 14.3\ntypescript 5.9\n"
)


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"MZ")
    return path


def _tools(
    monkeypatch: pytest.MonkeyPatch, on_path: Path | None, version_text: str = DENO_VERSION_TEXT
) -> None:
    """`shutil.which` finds Deno only at `on_path`; `subprocess.run` answers by program name."""

    def fake_which(name: str, *args: Any, **kwargs: Any) -> str | None:
        del args, kwargs
        return str(on_path) if name == "deno" and on_path is not None else None

    def fake_run(cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        del args, kwargs
        stem = Path(str(cmd[0])).stem.lower()
        if stem == "deno":
            return subprocess.CompletedProcess(cmd, 0, version_text, "")
        if stem == "ffmpeg":
            return subprocess.CompletedProcess(cmd, 0, "ffmpeg version 7.1-test\n", "")
        return subprocess.CompletedProcess(cmd, 1, "", "")

    monkeypatch.setattr("shutil.which", fake_which)
    monkeypatch.setattr("subprocess.run", fake_run)


def _adapter_kwargs(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    """Spy on `YouTubeAdapter.__init__` kwargs, after asserting the `js_runtime` seam exists."""
    from avkit_infra.youtube.adapter import YouTubeAdapter

    assert "js_runtime" in inspect.signature(YouTubeAdapter).parameters
    captured: list[dict[str, object]] = []
    original = YouTubeAdapter.__init__

    def spy(self: YouTubeAdapter, *args: Any, **kwargs: Any) -> None:
        captured.append(dict(kwargs))
        original(self, *args, **kwargs)

    monkeypatch.setattr(YouTubeAdapter, "__init__", spy)
    return captured


@contextmanager
def _stack(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bundled: Path | None) -> Iterator[Any]:
    import avkit_api.wiring as wiring
    from avkit_core.services.health import HealthService

    assert hasattr(wiring, "bundled_deno")
    monkeypatch.setattr(HealthService, "_active", None)
    monkeypatch.setattr(wiring, "bundled_deno", lambda: bundled)
    app_data = tmp_path / "app"
    app_data.mkdir(parents=True, exist_ok=True)
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        yield services, dispose
    finally:
        dispose()


def _runtime_view(found: object) -> tuple[object, object, object]:
    """(name, source, path) of a resolved runtime, or Nones when there is none."""
    if not isinstance(found, JsRuntime):
        return (None, None, None)
    return (found.name, found.source, str(found.path))


def _health_view(status: object) -> dict[str, object]:
    fields = ("available", "name", "path", "version", "source", "solver")
    return {field: getattr(status, field, "absent") for field in fields}


# --- AC-141.4: a deno_path PUT reaches the adapter and Health live --------------------------------


def test_ac_141_4_put_reaches_adapter_and_health(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _adapter_kwargs(monkeypatch)
    bundled = _touch(tmp_path / "resources" / "deno" / "deno.exe")
    chosen = _touch(tmp_path / "chosen" / "deno.exe")
    _tools(monkeypatch, None)
    with _stack(tmp_path, monkeypatch, bundled) as (services, dispose):
        assert "deno_path" in services.settings.get_namespace("downloader")
        assert len(captured) == 1
        source = captured[0].get("js_runtime")
        assert callable(source)
        live: Callable[[], object] = source
        app = create_app(tokens=frozenset({TOKEN}), services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            before = _runtime_view(live())
            status = client.put(
                "/api/v1/settings/downloader", headers=AUTH, json={"deno_path": str(chosen)}
            )
            after = _runtime_view(live())
            health_path = getattr(services.health.dependencies().js_runtime, "path", None)
        assert before == ("deno", "bundled", str(bundled))
        assert status.status_code == 200
        assert after == ("deno", "setting", str(chosen))
        assert health_path == str(chosen)


def test_ac_141_4_cleared_setting_falls_back_neg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _adapter_kwargs(monkeypatch)
    bundled = _touch(tmp_path / "resources" / "deno" / "deno.exe")
    chosen = _touch(tmp_path / "chosen" / "deno.exe")
    _tools(monkeypatch, None)
    with _stack(tmp_path, monkeypatch, bundled) as (services, _dispose):
        assert "deno_path" in services.settings.get_namespace("downloader")
        source = captured[0].get("js_runtime") if captured else None
        assert callable(source)
        live: Callable[[], object] = source
        services.settings.set("downloader", "deno_path", str(chosen))
        assert _runtime_view(live()) == ("deno", "setting", str(chosen))
        services.settings.set("downloader", "deno_path", "")
        assert _runtime_view(live()) == ("deno", "bundled", str(bundled))
        assert getattr(services.health.dependencies().js_runtime, "source", None) == "bundled"


# --- AC-141.5: js_runtimes in every opts builder --------------------------------------------------


def _adapter(runtime: JsRuntime | None) -> Any:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    return YouTubeAdapter(js_runtime=lambda: runtime)


def _call(action: Callable[[], object]) -> BaseException | None:
    try:
        action()
    except Exception as exc:  # noqa: BLE001 - the exception is the observation
        return exc
    return None


def _builder_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runtime: JsRuntime | None
) -> dict[str, dict[str, Any]]:
    """Run each public call once on the scripted fake; each builder's yt-dlp opts by name."""
    out: dict[str, dict[str, Any]] = {}
    info, _outfile = _info(tmp_path)

    seen = _script(monkeypatch, [_download_error(RELOAD), None], info=info)
    raised = _call(lambda: _adapter(runtime).download(URL, _options(tmp_path)))
    assert raised is None, repr(raised)
    assert len(seen.runs) == 2
    out["download_attempt_1"] = seen.opts(0)
    out["download_attempt_2"] = seen.opts(1)

    seen = _script(monkeypatch, [None], info=_video_info_payload())
    raised = _call(lambda: _adapter(runtime).extract_info(URL, flat=False))
    assert raised is None, repr(raised)
    out["extract_info"] = seen.opts(0)

    seen = _script(monkeypatch, [None], info=_video_info_payload())
    raised = _call(
        lambda: _adapter(runtime).extract_info(URL, flat=False, options=_options(tmp_path))
    )
    assert raised is None, repr(raised)
    out["extract_info_with_options"] = seen.opts(0)

    seen = _script(monkeypatch, [None], info=_video_info_payload())
    raised = _call(lambda: _adapter(runtime).extract_video_ids(URL))
    assert raised is None, repr(raised)
    out["extract_video_ids"] = seen.opts(0)

    seen = _script(monkeypatch, [None], info=_video_info_payload())
    raised = _call(lambda: _adapter(runtime).check_sabr_status())
    assert raised is None, repr(raised)
    assert seen.runs[0]["url"] == SABR_PROBE_URL
    out["check_sabr_status"] = seen.opts(0)

    cookie = tmp_path / "cookies.txt"
    cookie.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    seen = _script(monkeypatch, [None], info=_video_info_payload())
    result: list[object] = []
    raised = _call(
        lambda: result.append(_adapter(runtime).test_cookies("file", None, None, cookie))
    )
    assert raised is None, repr(raised)
    assert getattr(result[0], "ok", None) is True
    out["test_cookies"] = seen.opts(0)
    return out


def test_ac_141_5_every_builder_names_the_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    deno = _touch(tmp_path / "rt" / "deno.exe")
    runs = _builder_runs(tmp_path, monkeypatch, JsRuntime("deno", deno, "setting"))
    want = {"deno": {"path": str(deno)}}
    assert {name: opts.get("js_runtimes") for name, opts in runs.items()} == {
        name: want for name in runs
    }


def test_ac_141_5_no_runtime_leaves_the_key_out_neg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs = _builder_runs(tmp_path, monkeypatch, None)
    assert [name for name, opts in runs.items() if "js_runtimes" in opts] == []


# --- AC-141.6 and AC-141.7: RUNTIME_HEALTH per source ---------------------------------------------


@pytest.mark.parametrize("source", ["setting", "bundled", "path"])
def test_ac_141_6_health_names_the_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, source: str
) -> None:
    files = {
        "setting": _touch(tmp_path / "chosen" / "deno.exe"),
        "bundled": _touch(tmp_path / "resources" / "deno" / "deno.exe"),
        "path": _touch(tmp_path / "path-bin" / "deno.exe"),
    }
    _tools(monkeypatch, files["path"] if source == "path" else None)
    bundled = files["bundled"] if source in ("setting", "bundled") else None
    with _stack(tmp_path, monkeypatch, bundled) as (services, _dispose):
        assert "deno_path" in services.settings.get_namespace("downloader")
        if source == "setting":
            services.settings.set("downloader", "deno_path", str(files["setting"]))
        status = _health_view(services.health.dependencies().js_runtime)
    assert status == {
        "available": True,
        "name": "deno",
        "path": str(files[source]),
        "version": "2.9.8",
        "source": source,
        "solver": True,
    }


def test_ac_141_6_none_found_neg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _tools(monkeypatch, None)
    with _stack(tmp_path, monkeypatch, tmp_path / "absent" / "deno.exe") as (services, _dispose):
        status = _health_view(services.health.dependencies().js_runtime)
    assert (
        status["available"],
        status["name"],
        status["path"],
        status["source"],
        status["version"],
    ) == (
        False,
        None,
        None,
        None,
        None,
    )


def test_ac_141_7_unparsed_version_keeps_available(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundled = _touch(tmp_path / "resources" / "deno" / "deno.exe")
    _tools(monkeypatch, None, version_text="not a version\n")
    with _stack(tmp_path, monkeypatch, bundled) as (services, _dispose):
        status = _health_view(services.health.dependencies().js_runtime)
    assert (status["available"], status["source"], status["path"], status["version"]) == (
        True,
        "bundled",
        str(bundled),
        None,
    )
