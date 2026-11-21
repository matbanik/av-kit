"""AC-162.2 (MEU-162, STE_GATE, D-1293): the help card content passes the vendored
ASD-STE100 linter through `tools/help_guide_ste.py`.

- `AC-162.2 repo`: the tool finds 0 problems in the repository.
- `AC-162.2 selftest`: the tool's own fixtures pass.
- `AC-162.2 negatives`: each of the five negative fixtures of AC-162.2 gives a problem.
- `AC-162.2 parser`: the tool's topic parser gives row 0's topic ids in order, and row 0's
  pinned titles and bodies (`baseline-pins.json`). The pinned `four-tools` body is compared
  after the one `CONSOLE_AND_SAVE` sentence change, on both sides; unpinned titles are not
  compared, because `PLAIN_TOPICS` rewrites them.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "help_guide_ste.py"
PINS = ROOT / "docs" / "execution" / "plans" / "2026-11-20-help-quick-start" / "baseline-pins.json"
SAVE_OLD = "Save POSTs the full annotation list."
SAVE_NEW = "Save stores all the marks on the shot."


def _tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location("help_guide_ste_under_test", TOOL)
    assert spec is not None and spec.loader is not None, f"cannot load {TOOL}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _repo(tool: ModuleType) -> list[str]:
    return list(tool.run())


def _selftest(tool: ModuleType) -> list[str]:
    return [f"selftest failure: {name}" for name in tool.selftest()]


def _negatives(tool: ModuleType) -> list[str]:
    results = tool.negatives(tool.load_linter())
    want = {
        "passive step",
        "phrasal verb step",
        "21-word sentence",
        "unpinned topic",
        "unknown level",
    }
    problems = [] if set(results) == want else [f"negative fixtures {sorted(results)}"]
    return problems + [f"no problem for {name}" for name, found in results.items() if not found]


def _parser(tool: ModuleType) -> list[str]:
    pins = json.loads(PINS.read_bytes().decode("utf-8"))
    problems: list[str] = []
    if set(pins["modules"]) != set(tool.MODULES):
        problems.append(f"modules {sorted(tool.MODULES)} differ from row 0's")
    for feature, row0 in pins["modules"].items():
        if tool.MODULES.get(feature) != row0["path"]:
            problems.append(f"{feature}: path {tool.MODULES.get(feature)} is not {row0['path']}")
            continue
        topics = tool.parse_topics((ROOT / row0["path"]).read_bytes().decode("utf-8"))
        if [t["id"] for t in topics] != [t["id"] for t in row0["topics"]]:
            problems.append(f"{feature}: topic ids or order differ from row 0")
        by_id = {t["id"]: t for t in topics}
        for tid, pinned in row0["pinned"].items():
            got = by_id.get(tid)
            if got is None:
                problems.append(f"{feature}:{tid}: pinned topic missing")
                continue
            if got["title"] != pinned["title"]:
                problems.append(f"{feature}:{tid}: title differs from row 0")
            got_body = got["body"].replace(SAVE_OLD, SAVE_NEW)
            if got_body != pinned["body"].replace(SAVE_OLD, SAVE_NEW):
                problems.append(f"{feature}:{tid}: body differs from row 0")
    pinned_keys = {f"{f}:{tid}" for f, m in pins["modules"].items() for tid in m["pinned"]}
    if pinned_keys != set(tool.PINNED_TOPICS):
        problems.append(f"PINNED_TOPICS is not row 0's {sorted(pinned_keys)}")
    return problems


CASES = {
    "AC-162.2 repo": _repo,
    "AC-162.2 selftest": _selftest,
    "AC-162.2 negatives": _negatives,
    "AC-162.2 parser": _parser,
}


@pytest.mark.parametrize("case", list(CASES), ids=list(CASES))
def test_help_guide_ste(case: str) -> None:
    problems = CASES[case](_tool())
    assert problems == [], f"{case}:\n" + "\n".join(problems)
