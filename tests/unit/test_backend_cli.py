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
