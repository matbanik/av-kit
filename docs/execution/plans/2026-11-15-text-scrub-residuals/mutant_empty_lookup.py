"""Session 77 empty-lookup mutant (plan §Acceptance Criteria, D-927, review R1-F1).

A pytest plugin: load it with ``-p mutant_empty_lookup`` and ``PYTHONPATH`` at this plan folder.
It replaces ``avkit_core.services.health.short_path_name`` with a function that always returns
``""``. Every AC-148.8 test must then fail by assertion, so an always-empty helper cannot pass.
"""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    from avkit_core.services import health

    health.short_path_name = lambda _path: ""  # type: ignore[assignment]
