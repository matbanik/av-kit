"""MEU-19 Red/Green: spawn `python -m avkit_api` (AC-19.2, AC-19.4)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

READY_RE = re.compile(r"AVKIT_READY port=(\d+) instance=(\S+)")
DESCRIPTOR_KEYS = {
    "schema_version",
    "pid",
    "instance_id",
    "executable_path",
    "host",
    "port",
    "bind",
    "api_base",
    "app_data",
    "started_at",
}


def _spawn(tmp_path: Path, token: str, mcp_token: str) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "avkit_api",
            "--token",
            token,
            "--mcp-token",
            mcp_token,
            "--port",
            "0",
            "--app-data",
            str(tmp_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(Path.cwd()),
    )


def _wait_ready(proc: subprocess.Popen[str], timeout_s: float = 20.0) -> re.Match[str]:
    assert proc.stdout is not None
    deadline = time.monotonic() + timeout_s
    collected = ""
    while time.monotonic() < deadline:
        line = proc.stdout.readline()
        if line == "" and proc.poll() is not None:
            stderr = proc.stderr.read() if proc.stderr is not None else ""
            raise AssertionError(f"CLI exited {proc.returncode} before READY: {collected}{stderr}")
        collected += line
        match = READY_RE.search(line)
        if match is not None:
            return match
    raise AssertionError(f"timeout waiting for READY_LINE: {collected}")


def _http(url: str, token: str | None = None) -> tuple[int, str]:
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return int(response.status), response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read().decode("utf-8")


def test_ac_19_2_ready_line_and_descriptor(tmp_path: Path) -> None:
    token = "gui-nonce-spawn"
    mcp_token = "mcp-token-spawn"
    proc = _spawn(tmp_path, token, mcp_token)
    try:
        match = _wait_ready(proc)
        port = int(match.group(1))
        assert port != 0
        descriptor_path = tmp_path / "backend.json"
        assert descriptor_path.is_file()
        payload = json.loads(descriptor_path.read_text(encoding="utf-8"))
        assert set(payload.keys()) == DESCRIPTOR_KEYS
        assert payload["schema_version"] == 1
        assert payload["pid"] == proc.pid
        assert payload["host"] == "127.0.0.1"
        assert payload["bind"] == "127.0.0.1"
        assert payload["port"] == port
        assert payload["api_base"] == f"http://127.0.0.1:{port}/api/v1"
        assert Path(payload["app_data"]) == tmp_path
        assert "0.0.0.0" not in json.dumps(payload)
        assert token not in descriptor_path.read_text(encoding="utf-8")
        assert (tmp_path / "backend-port.txt").read_text(encoding="utf-8").strip() == str(port)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def test_ac_19_4_dual_bearer_on_spawned_app(tmp_path: Path) -> None:
    token = "gui-nonce-auth"
    mcp_token = "mcp-token-auth"
    proc = _spawn(tmp_path, token, mcp_token)
    try:
        match = _wait_ready(proc)
        base = f"http://127.0.0.1:{match.group(1)}/api/v1"
        health_status, _ = _http(f"{base}/health")
        assert health_status == 200
        denied_status, _ = _http(f"{base}/health/console")
        assert denied_status == 401
        gui_status, _ = _http(f"{base}/health/console", token)
        assert gui_status == 200
        mcp_status, _ = _http(f"{base}/health/console", mcp_token)
        assert mcp_status == 200
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
