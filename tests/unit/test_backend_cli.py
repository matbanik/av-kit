"""MEU-19 Red/Green: runtime CLI parser, descriptor secrets, atomic replace (AC-19.1, AC-19.3)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


def test_ac_19_1_parse_spawn_flags(tmp_path: Path) -> None:
    from avkit_api.cli import parse_args

    parsed = parse_args(
        [
            "--token",
            "gui-nonce",
            "--mcp-token",
            "mcp-token",
            "--port",
            "0",
            "--app-data",
            str(tmp_path),
        ]
    )
    assert parsed.token == "gui-nonce"
    assert parsed.mcp_token == "mcp-token"
    assert parsed.port == 0
    assert Path(parsed.app_data) == tmp_path


def test_ac_19_1_missing_token_exits_nonzero(tmp_path: Path) -> None:
    from avkit_api.cli import parse_args

    with pytest.raises(SystemExit) as exc:
        parse_args(
            [
                "--mcp-token",
                "mcp-token",
                "--port",
                "0",
                "--app-data",
                str(tmp_path),
            ]
        )
    assert exc.value.code not in (0, None)


def test_ac_19_1_blank_mcp_token_exits_nonzero(tmp_path: Path) -> None:
    from avkit_api.cli import parse_args

    with pytest.raises(SystemExit) as exc:
        parse_args(
            [
                "--token",
                "gui-nonce",
                "--mcp-token",
                "   ",
                "--port",
                "0",
                "--app-data",
                str(tmp_path),
            ]
        )
    assert exc.value.code not in (0, None)


def test_ac_19_1_unknown_flag_exits_nonzero(tmp_path: Path) -> None:
    from avkit_api.cli import parse_args

    with pytest.raises(SystemExit) as exc:
        parse_args(
            [
                "--token",
                "gui-nonce",
                "--mcp-token",
                "mcp-token",
                "--port",
                "0",
                "--app-data",
                str(tmp_path),
                "--bind",
                "0.0.0.0",
            ]
        )
    assert exc.value.code not in (0, None)


def test_ac_19_3_descriptor_omits_secrets(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from avkit_api.cli import write_descriptor

    nonce = "gui-secret-nonce-9f3a"
    mcp = "mcp-secret-token-c21b"
    payload = write_descriptor(
        app_data=tmp_path,
        pid=os.getpid(),
        instance_id="inst-1",
        executable_path=str(tmp_path / "python.exe"),
        host="127.0.0.1",
        port=51234,
        token=nonce,
        mcp_token=mcp,
    )
    raw = (tmp_path / "backend.json").read_text(encoding="utf-8")
    captured = capsys.readouterr()
    assert nonce not in raw
    assert mcp not in raw
    assert "Authorization" not in raw
    assert "mcp-token" not in raw
    assert payload["schema_version"] == 1
    assert nonce not in captured.out
    assert nonce not in captured.err
    assert mcp not in captured.out
    assert mcp not in captured.err


def test_ac_19_2_write_descriptor_uses_os_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_api.cli import write_descriptor

    calls: list[tuple[str, str]] = []
    real_replace = os.replace

    def _spy(src: str, dst: str) -> None:
        calls.append((src, dst))
        real_replace(src, dst)

    monkeypatch.setattr(os, "replace", _spy)
    write_descriptor(
        app_data=tmp_path,
        pid=os.getpid(),
        instance_id="inst-2",
        executable_path=str(tmp_path / "python.exe"),
        host="127.0.0.1",
        port=51235,
        token="nonce",
        mcp_token="mcp",
    )
    assert calls
    assert Path(calls[0][1]) == tmp_path / "backend.json"
    sibling = (tmp_path / "backend-port.txt").read_text(encoding="utf-8").strip()
    assert sibling == "51235"


def _run_main_recording(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Run the real main() with services, app and server stubbed; record listen state per step."""
    import socket

    import uvicorn

    from avkit_api import cli

    record: dict[str, object] = {"sockets": [], "port": None, "descriptor": [], "print": []}
    sockets: list[socket.socket] = record["sockets"]  # type: ignore[assignment]
    real_bind = uvicorn.Config.bind_socket
    real_write = cli.write_descriptor

    def _accepting() -> int:
        return int(sockets[0].getsockopt(socket.SOL_SOCKET, socket.SO_ACCEPTCONN))

    def _bind(self: uvicorn.Config) -> socket.socket:
        sock = real_bind(self)
        sockets.append(sock)
        record["port"] = int(sock.getsockname()[1])
        return sock

    def _write(**kwargs: object) -> dict[str, object]:
        record["descriptor"].append((_accepting(), kwargs["port"]))  # type: ignore[attr-defined]
        return real_write(**kwargs)  # type: ignore[arg-type]

    def _print(*args: object, **kwargs: object) -> None:
        record["print"].append((_accepting(), args, kwargs))  # type: ignore[attr-defined]

    def _serve(self: uvicorn.Server, sockets: list[socket.socket] | None = None) -> None:
        for sock in sockets or []:
            sock.close()

    monkeypatch.setattr(cli, "build_services", lambda *, app_data: (object(), lambda: None))
    monkeypatch.setattr(cli, "create_app", lambda **kwargs: object())
    monkeypatch.setattr(uvicorn.Config, "bind_socket", _bind)
    monkeypatch.setattr(cli, "write_descriptor", _write)
    monkeypatch.setattr(cli, "print", _print, raising=False)
    monkeypatch.setattr(uvicorn.Server, "run", _serve)
    app_data = tmp_path / "app-data"
    try:
        record["exit"] = cli.main(
            [
                "--token",
                "gui-nonce",
                "--mcp-token",
                "mcp-token",
                "--port",
                "0",
                "--app-data",
                str(app_data),
            ]
        )
    finally:
        for sock in sockets:
            sock.close()
    record["app_data"] = app_data
    return record


def test_ac_153_1_socket_listens_before_descriptor_and_ready_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MEU-153 LISTEN_FIRST: the socket listens before the descriptor and the ready line."""
    import socket

    assert hasattr(socket, "SO_ACCEPTCONN")
    record = _run_main_recording(tmp_path, monkeypatch)
    assert record["exit"] == 0
    descriptor = record["descriptor"]
    printed = record["print"]
    assert isinstance(descriptor, list) and len(descriptor) == 1
    assert isinstance(printed, list) and len(printed) == 1
    assert (descriptor[0][0], printed[0][0]) == (1, 1)


def test_ac_153_2_ready_line_text_kept(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MEU-153 READY_TEXT_KEPT (a pin): one ready line, the bound port, flushed."""
    import json
    import re

    record = _run_main_recording(tmp_path, monkeypatch)
    printed = record["print"]
    assert isinstance(printed, list) and len(printed) == 1
    _, args, kwargs = printed[0]
    assert len(args) == 1
    match = re.match(r"^AVKIT_READY port=(\d+) instance=[0-9a-f-]{36}$", args[0])
    assert match is not None
    port = int(match.group(1))
    assert port == record["port"]
    app_data = record["app_data"]
    assert isinstance(app_data, Path)
    payload = json.loads((app_data / "backend.json").read_text(encoding="utf-8"))
    assert payload["port"] == port
    assert kwargs.get("flush") is True
