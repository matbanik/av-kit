"""Session 90 pytest plugin: slow the fake workers so a 5-second wait runs out (AC-1, AC-2).

Loaded only by name, with this folder on PYTHONPATH:

    uv run --no-sync python -m pytest -p slow_worker <tests>

with PYTHONPATH=<plan folder>, AVKIT_SLOW_WORKER_S=6 and AVKIT_SLOW_WORKER_LOG=<file> set.

With AVKIT_SLOW_WORKER_S unset or empty it does nothing, so a run without it is the plain suite.
With it set, an autouse fixture, which runs before the test module's own fixtures:

- patches `WheelServer.fetch` in a test module that defines `WheelServer`
  (`tests/integration/test_tts_assets.py:51-65`): the fake spaCy wheel download;
- patches `FakeCaptions.get_transcript` (`tests/unit/test_services.py:1151`) in the
  `test_youtube_adapter` module only: the fake caption fetch that
  `test_ac_122_8_surrogate_title_survives_real_storage` imports at `:885`.

Each patch sleeps S seconds, then calls the original unchanged, and appends
`delayed <nodeid> <target>` to AVKIT_SLOW_WORKER_LOG. `armed <nodeid>` is logged when a test
starts with the plugin active. The log holds node ids and target names only. monkeypatch undoes
every patch when the test ends.

With S = 6, the worker outlives a 5-second wait and the test fails by its own assertion
(`test_tts_assets.py:260`, `test_youtube_adapter.py:940`), which is the Red. After the waits
read WORKER_WAIT_S = 60.0, the same run passes, which is the Green.
"""

from __future__ import annotations

import importlib
import os
import time
from collections.abc import Callable, Iterator
from typing import Any

import pytest

ENV_SECONDS = "AVKIT_SLOW_WORKER_S"
ENV_LOG = "AVKIT_SLOW_WORKER_LOG"
YOUTUBE_MODULE = "test_youtube_adapter"
CAPTIONS_MODULE = "tests.unit.test_services"


def delay_seconds() -> float | None:
    """The delay from AVKIT_SLOW_WORKER_S, or None when the plugin is off."""
    raw = os.environ.get(ENV_SECONDS, "").strip()
    if not raw:
        return None
    return float(raw)


def log(line: str) -> None:
    path = os.environ.get(ENV_LOG, "").strip()
    if not path:
        return
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(line + "\n")


def slowed(
    original: Callable[..., Any], seconds: float, nodeid: str, target: str
) -> Callable[..., Any]:
    """ORIGINAL, called after SECONDS; a plain function, so it binds as a method on the class."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        log(f"delayed {nodeid} {target}")
        time.sleep(seconds)
        return original(*args, **kwargs)

    return wrapper


@pytest.fixture(autouse=True)
def avkit_slow_worker(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> Iterator[None]:
    seconds = delay_seconds()
    if seconds is None:
        yield
        return
    module = request.module
    nodeid = request.node.nodeid
    server = getattr(module, "WheelServer", None)
    if server is not None and hasattr(server, "fetch"):
        monkeypatch.setattr(
            server, "fetch", slowed(server.fetch, seconds, nodeid, "WheelServer.fetch")
        )
    if module.__name__.rsplit(".", 1)[-1] == YOUTUBE_MODULE:
        captions = importlib.import_module(CAPTIONS_MODULE).FakeCaptions
        monkeypatch.setattr(
            captions,
            "get_transcript",
            slowed(captions.get_transcript, seconds, nodeid, "FakeCaptions.get_transcript"),
        )
    log(f"armed {nodeid}")
    yield
