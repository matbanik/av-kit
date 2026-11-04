#!/usr/bin/env python3
"""Validate the live YAML frontmatter of an execution-review rolling file.

Only the first ``---`` / ``---`` block is the contract. Historical ``verdict:``
lines in the body are ignored so a later ``changes_required`` appendix cannot
be masked by an earlier ``approved``, and a slug mentioned only in the body
cannot bind a review written for a different ``target_plan``.

Usage:
  uv run python tools/check_exec_review.py \\
    --review-file .agent/context/handoffs/<slug>-implementation-critical-review.md \\
    --expected-mode implementation \\
    --expected-target docs/execution/plans/<slug>/implementation-plan.md \\
    --max-round 6

  uv run python tools/check_exec_review.py --self-test
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

_ALLOWED_MODES = frozenset({"implementation"})
_APPROVED = "approved"


def _ensure_utf8() -> None:
    if sys.platform == "win32":
        import io
        from typing import cast

        cast(io.TextIOWrapper, sys.stdout).reconfigure(encoding="utf-8", errors="replace")
        cast(io.TextIOWrapper, sys.stderr).reconfigure(encoding="utf-8", errors="replace")


def parse_first_frontmatter(text: str) -> dict[str, Any]:
    """Return the first YAML frontmatter mapping, or raise ValueError."""
    if not text.startswith("---"):
        raise ValueError("review file does not start with YAML frontmatter (---)")
    rest = text[3:]
    if rest.startswith("\r\n"):
        rest = rest[2:]
    elif rest.startswith("\n"):
        rest = rest[1:]
    end = rest.find("\n---")
    if end < 0:
        raise ValueError("review file is missing the closing frontmatter ---")
    block = rest[:end]
    loaded = yaml.safe_load(block)
    if not isinstance(loaded, dict):
        raise ValueError("frontmatter is not a YAML mapping")
    return loaded


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().strip("\"'")


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field} is missing or not an integer")
    if isinstance(value, int):
        return value
    text = _as_str(value)
    if not text or not text.lstrip("-").isdigit():
        raise ValueError(f"{field} is not an integer: {value!r}")
    return int(text)


def resolve_round(meta: dict[str, Any]) -> int:
    has_round = "round" in meta
    has_review_round = "review_round" in meta
    if not has_round and not has_review_round:
        raise ValueError("frontmatter missing round and review_round")
    if has_round and has_review_round:
        left = _as_int(meta["round"], "round")
        right = _as_int(meta["review_round"], "review_round")
        if left != right:
            raise ValueError(f"round ({left}) != review_round ({right})")
        return left
    if has_round:
        return _as_int(meta["round"], "round")
    return _as_int(meta["review_round"], "review_round")


def check_review(
    path: Path,
    *,
    expected_mode: str,
    expected_target: str,
    max_round: int,
) -> None:
    if not path.is_file():
        raise ValueError(f"missing review file: {path}")
    text = path.read_text(encoding="utf-8")
    meta = parse_first_frontmatter(text)
    mode = _as_str(meta.get("review_mode")).lower()
    if mode != expected_mode.lower():
        raise ValueError(
            f"review_mode={mode!r} expected {expected_mode!r} "
            "(body text is not consulted)"
        )
    if mode not in _ALLOWED_MODES:
        raise ValueError(f"review_mode {mode!r} is not an execution review")
    target = _as_str(meta.get("target_plan"))
    if target != expected_target:
        raise ValueError(
            f"target_plan={target!r} expected {expected_target!r} "
            "(a slug in the body does not bind the review)"
        )
    verdict = _as_str(meta.get("verdict")).lower()
    if verdict != _APPROVED:
        raise ValueError(f"verdict={verdict!r} expected {_APPROVED!r}")
    findings = _as_int(meta.get("findings_count"), "findings_count")
    if findings != 0:
        raise ValueError(
            f"findings_count={findings} expected 0 for an approved execution review"
        )
    review_round = resolve_round(meta)
    if review_round < 1 or review_round > max_round:
        raise ValueError(
            f"round={review_round} is outside 1..{max_round}"
        )


def _write_fixture(directory: Path, name: str, body: str) -> Path:
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path


def run_self_test() -> None:
    """Reproduce the Round 3 false-pass cases plus the happy path."""
    target = (
        "docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md"
    )
    good = """---
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md"
verdict: approved
findings_count: 0
round: 2
---

# ok
"""
    wrong_target = """---
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-19-p2-persistence-io/implementation-plan.md"
verdict: approved
findings_count: 0
round: 1
---

p2-external-adapters appears only in the body and must not bind this file.
"""
    findings_two = """---
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md"
verdict: approved
findings_count: 2
round: 1
---

# inconsistent approval
"""
    plan_mode = """---
review_mode: plan
target_plan: "docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md"
verdict: approved
findings_count: 0
review_round: 3
---

# plan review
"""
    changes = """---
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md"
verdict: changes_required
findings_count: 0
round: 1
---

verdict: approved
"""
    kwargs = {
        "expected_mode": "implementation",
        "expected_target": target,
        "max_round": 6,
    }
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        check_review(_write_fixture(directory, "good.md", good), **kwargs)
        cases = (
            ("wrong-target.md", wrong_target, "target_plan="),
            ("findings-2.md", findings_two, "findings_count=2"),
            ("plan-mode.md", plan_mode, "review_mode="),
            ("changes.md", changes, "verdict="),
        )
        for name, text, needle in cases:
            path = _write_fixture(directory, name, text)
            try:
                check_review(path, **kwargs)
            except ValueError as exc:
                message = str(exc)
                if needle not in message:
                    raise AssertionError(
                        f"{name} failed with {message!r}, expected {needle!r}"
                    ) from exc
            else:
                raise AssertionError(f"{name} false-passed")
    print("PASS: check_exec_review self-test")


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-file", type=Path)
    parser.add_argument("--expected-mode", default="implementation")
    parser.add_argument(
        "--expected-target",
        default=(
            "docs/execution/plans/2026-08-19-p2-external-adapters/"
            "implementation-plan.md"
        ),
    )
    parser.add_argument("--max-round", type=int, default=6)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            run_self_test()
            return 0
        if args.review_file is None:
            raise ValueError("--review-file is required unless --self-test")
        check_review(
            args.review_file,
            expected_mode=args.expected_mode,
            expected_target=args.expected_target,
            max_round=args.max_round,
        )
    except (OSError, ValueError, AssertionError, yaml.YAMLError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: latest execution review approved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
