"""JavaScript runtime lookup for yt-dlp's challenge solver (MEU-141, `JS_RUNTIME_LOOKUP`).

The order is the live `downloader.deno_path` setting, the bundled `resources/deno/deno.exe`, then
`deno` on PATH. Every filesystem call on the setting sits inside the error mapping (Session 58
RULE-2), and no setting value or probe output reaches a log line.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from avkit_core.domain.health import JsRuntimeStatus

JsRuntimeSource = Literal["setting", "bundled", "path"]

#: One `deno --version` run is bounded to this many seconds (`RUNTIME_HEALTH`).
DENO_VERSION_TIMEOUT_S = 5
_DENO_VERSION_RE = re.compile(r"^deno (\d+\.\d+\.\d+)(?:\s|$)")
#: The import name of the yt-dlp-ejs solver package (`SOLVER_SPEC`).
SOLVER_MODULE = "yt_dlp_ejs"


@dataclass(frozen=True)
class JsRuntime:
    """A resolved runtime: its yt-dlp name, its executable and where it was found."""

    name: str
    path: Path
    source: JsRuntimeSource


def _is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except (OSError, ValueError, RuntimeError, UnicodeError):
        return False


def _setting_path(value: object) -> Path | None:
    """The setting as a usable file path, else None. Nothing here raises or logs."""
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text == "":
        return None
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in text):
        return None
    try:
        text.encode("utf-8")
        path = Path(text).expanduser()
    except (OSError, ValueError, RuntimeError, UnicodeError):
        return None
    return path if _is_file(path) else None


class JsRuntimeLocator:
    """Find Deno from the live setting, the bundled file, then PATH."""

    def __init__(self, configured: Callable[[], object] | None, bundle_path: Path | None) -> None:
        self._configured = configured
        self._bundle_path = bundle_path

    def _from_setting(self) -> Path | None:
        if self._configured is None:
            return None
        try:
            value = self._configured()
        except Exception:  # noqa: BLE001 - an unreadable setting falls through
            return None
        return _setting_path(value)

    def resolve(self) -> JsRuntime | None:
        """The first usable runtime, else None. The setting is read at every call."""
        chosen = self._from_setting()
        if chosen is not None:
            return JsRuntime("deno", chosen, "setting")
        if self._bundle_path is not None and _is_file(self._bundle_path):
            return JsRuntime("deno", self._bundle_path, "bundled")
        try:
            found = shutil.which("deno")
        except (OSError, ValueError):
            found = None
        if isinstance(found, str) and found != "":
            on_path = Path(found)
            if _is_file(on_path):
                return JsRuntime("deno", on_path, "path")
        return None


def probe_deno_version(path: Path) -> str | None:
    """`X.Y.Z` from one bounded `deno --version` run, else None. The output is never logged."""
    try:
        result = subprocess.run(
            [str(path), "--version"],
            capture_output=True,
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=DENO_VERSION_TIMEOUT_S,
        )
    except (subprocess.TimeoutExpired, OSError, UnicodeError, ValueError):
        return None
    if getattr(result, "returncode", 1) != 0:
        return None
    stdout = getattr(result, "stdout", None)
    if not isinstance(stdout, str):
        return None
    lines = stdout.splitlines()
    if not lines:
        return None
    match = _DENO_VERSION_RE.match(lines[0].strip())
    return match.group(1) if match else None


def solver_available() -> bool:
    """True when the yt-dlp-ejs solver package can be imported."""
    try:
        return importlib.util.find_spec(SOLVER_MODULE) is not None
    except (ImportError, ValueError):
        return False


def runtime_status(locator: JsRuntimeLocator) -> JsRuntimeStatus:
    """`RUNTIME_HEALTH`: the runtime yt-dlp would be given now, its version and the solver."""
    solver = solver_available()
    found = locator.resolve()
    if found is None:
        return JsRuntimeStatus(
            available=False, name=None, path=None, version=None, source=None, solver=solver
        )
    return JsRuntimeStatus(
        available=True,
        name=found.name,
        path=str(found.path),
        version=probe_deno_version(found.path),
        source=found.source,
        solver=solver,
    )
