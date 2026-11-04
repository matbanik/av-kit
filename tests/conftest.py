"""Shared pytest configuration for av-kit."""

from __future__ import annotations

import sys
from collections.abc import Iterator

import pytest


def pytest_configure(config: object) -> None:
    """Register Phase 1 markers used by tests/unit/test_domain.py."""
    marker_plugin = getattr(config, "addinivalue_line", None)
    if marker_plugin is None:
        return
    marker_plugin("markers", "unit: isolated unit tests")
    marker_plugin("markers", "integration: adapter/integration tests")
    marker_plugin("markers", "e2e: end-to-end tests")


@pytest.fixture(autouse=True)
def _restore_import_path() -> Iterator[None]:
    """Undo `sys.path` entries and spaCy-model imports a test added (Session 27 MEU-62).

    `build_services` activates the configured models directory's spaCy install by extending the
    process-wide `sys.path`; outside a test that sets its own directory, that is the real
    `~/.avkit/models`. Without this, any test that builds services (e.g. the captures wiring test)
    leaks a user's real install into every later test in the process (WINDOWS_GATE attempt 4).
    """
    path_before = list(sys.path)
    modules_before = set(sys.modules)
    yield
    sys.path[:] = path_before
    for name in set(sys.modules) - modules_before:
        if name == "en_core_web_sm" or name.startswith("en_core_web_sm."):
            del sys.modules[name]
