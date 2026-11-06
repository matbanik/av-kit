"""The closeout check reads known-issues.yaml as model.save writes it (Session 49b, AC-1..AC-7)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools" / "validate_closeout_artifacts.py"
sys.path.insert(0, str(ROOT / "tools"))

import validate_closeout_artifacts as v  # noqa: E402
from issue_triage import model  # noqa: E402

# Strings PyYAML cannot write as a plain or literal-block scalar, or that the reader splits on.
EDGE_STRINGS = {
    "trailing-space": "a \nb",
    "tab": "a\tb",
    "carriage-return": "a\r\nb",
    "U+0085": "a\x85b",
    "U+2028": "a b",
    "U+2029": "a b",
    "separator-and-newline": "a b\nc",
    "two-trailing-newlines": "trail\n\n",
    "newline-only": "\n",
}
PLAIN_EDGE_STRINGS = {
    "colon": "a: b",
    "yes": "yes",
    "hash": "# not a comment",
    "quote": 'it\'s "quoted"',
    "unicode": "héllo — ✓",
    "leading-dash": "- item",
    "empty": "",
}


def issue(issue_id: str, **fields: object) -> dict:
    return {
        "id": issue_id,
        "title": "Demo issue",
        "severity": "low",
        "component": "agent",
        "status": "open",
        "discovered": "2026-11-05",
        "root_cause": "demo",
        "blast_radius": "demo",
        **fields,
    }


def register(*issues: dict) -> dict:
    return {"version": 1, "issues": list(issues)}


def saved(data: dict, path: Path) -> str:
    model.save(data, path)
    return path.read_text(encoding="utf-8")


def grammar_refusal(text: str) -> str | None:
    """The grammar's refusal of the whole file, or None when it passes."""
    try:
        v.check_yaml_subset(text, "known-issues.yaml")
    except v.Refuse as exc:
        return str(exc)
    return None


def decision_log_or_refusal(text: str, issue_id: str) -> list[tuple[str, str | None]] | str:
    try:
        return v.issue_decision_log(text, "known-issues.yaml", issue_id)
    except v.Refuse as exc:
        return f"REFUSE: {exc}"


# -- the writer ------------------------------------------------------------------------


def test_ac_1_nested_sequences_pass_the_grammar_and_read(tmp_path):
    data = register(
        issue(
            "GRAMMAR-A",
            related=["GRAMMAR-B"],
            meu_links=["MEU-1"],
            enrichment={
                "decided_by": "agent",
                "decision_log": [
                    {
                        "id": "D-1",
                        "stage": "planning",
                        "question": "Which writer?",
                        "precedents": ["tools/a.py:1 — one", "tools/b.py:2 — two"],
                        "research": {
                            "engine": "none",
                            "sources": ["https://example.invalid/a", "https://example.invalid/b"],
                        },
                        "nested": [[["a"], "b"], [], ["c", "d"]],
                    },
                    {
                        "id": "D-2",
                        "stage": "triage",
                        "matrix": [["alpha", "beta"], ["gamma"]],
                        "rows": [{"k": "v", "l": ["m"]}],
                    },
                ],
            },
        ),
        issue(
            "GRAMMAR-B",
            enrichment={"decision_log": [{"id": "D-3", "stage": "triage", "chosen": "keep"}]},
        ),
    )
    text = saved(data, tmp_path / "known-issues.yaml")
    assert grammar_refusal(text) is None
    assert "- - " not in text
    assert decision_log_or_refusal(text, "GRAMMAR-A") == [("D-1", "planning"), ("D-2", "triage")]
    assert decision_log_or_refusal(text, "GRAMMAR-B") == [("D-3", "triage")]


def test_ac_2_long_value_is_one_line(tmp_path):
    value = ("word " * 60)[:-1] + "s"
    assert len(value) == 300
    text = saved(register(issue("GRAMMAR-A", root_cause=value)), tmp_path / "known-issues.yaml")
    assert f"    root_cause: {value}\n" in text
    assert grammar_refusal(text) is None


def test_ac_2_multiline_value_is_a_literal_block(tmp_path):
    text = saved(
        register(issue("GRAMMAR-A", notes="line one\nline two\n")), tmp_path / "known-issues.yaml"
    )
    assert "    notes: |\n      line one\n      line two\n" in text
    assert grammar_refusal(text) is None


@pytest.mark.parametrize("value", EDGE_STRINGS.values(), ids=EDGE_STRINGS.keys())
def test_ac_2_edge_string_passes_the_grammar(tmp_path, value):
    data = register(
        issue(
            "GRAMMAR-A",
            notes=value,
            enrichment={"decision_log": [{"id": "D-1", "stage": "planning", "reasoning": value}]},
        )
    )
    text = saved(data, tmp_path / "known-issues.yaml")
    assert grammar_refusal(text) is None
    assert decision_log_or_refusal(text, "GRAMMAR-A") == [("D-1", "planning")]


def test_ac_2_shared_list_is_written_twice(tmp_path):
    shared = ["GRAMMAR-B", "GRAMMAR-C"]
    text = saved(
        register(issue("GRAMMAR-A", related=shared, blocks=shared)), tmp_path / "known-issues.yaml"
    )
    assert "&id" not in text and "*id" not in text
    assert text.count("- GRAMMAR-C\n") == 2
    assert grammar_refusal(text) is None


@pytest.mark.parametrize("key", ["", "a\nb"], ids=["empty-key", "multiline-key"])
def test_ac_2_refused_key_leaves_the_file(tmp_path, key):
    path = tmp_path / "known-issues.yaml"
    path.write_bytes(b"before\n")
    data = register(
        issue(
            "GRAMMAR-A", enrichment={"decision_log": [{"id": "D-1", "stage": "planning", key: "v"}]}
        )
    )
    with pytest.raises(model.IssueTriageError):
        model.save(data, path)
    assert path.read_bytes() == b"before\n"


@pytest.mark.parametrize(
    "value",
    [*EDGE_STRINGS.values(), *PLAIN_EDGE_STRINGS.values()],
    ids=[*EDGE_STRINGS.keys(), *PLAIN_EDGE_STRINGS.keys()],
)
def test_ac_3_saved_value_loads_back_equal(tmp_path, value):
    data = register(
        issue(
            "GRAMMAR-A",
            notes=value,
            related=[value],
            enrichment={"decision_log": [{"id": "D-1", "stage": "planning", "reasoning": value}]},
        )
    )
    path = tmp_path / "known-issues.yaml"
    model.save(data, path)
    assert model.load(path) == data


# -- the repeatable --decision-issue -----------------------------------------------------

DECISION_ROW_D9 = (
    "| D-9 | triage | Other issue? | autonomous | Keep | Local Canon | two-way door | — |\n"
)


def run_check(tmp_path: Path, rows: str, *issues: str) -> subprocess.CompletedProcess[str]:
    """The reflection check over the selftest's plan and known-issues file, naming each issue."""
    reflection = tmp_path / "reflection.md"
    reflection.write_text(
        v._GOOD_REFLECTION.replace("### Decisions Log\n\nNone.\n", rows), encoding="utf-8"
    )
    template = tmp_path / "REFLECTION-TEMPLATE.md"
    template.write_text(v._GOOD_REFLECTION_TEMPLATE, encoding="utf-8")
    plan = tmp_path / "decided-plan.md"
    plan.write_text(v._GOOD_PLAN + v._DECISION_PLAN_TAIL, encoding="utf-8")
    known_issues = tmp_path / "known-issues.yaml"
    known_issues.write_text(v._DECISION_KNOWN_ISSUES, encoding="utf-8")
    flags = [arg for issue_id in issues for arg in ("--decision-issue", issue_id)]
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--reflection",
            str(reflection),
            "--reflection-template",
            str(template),
            "--decision-source",
            str(plan),
            "--decision-source",
            str(known_issues),
            *flags,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=ROOT,
        check=False,
    )


def test_ac_4_every_named_issue_is_read(tmp_path):
    result = run_check(tmp_path, v._DECISIONS_LOG_ROWS, "OTHER-ISSUE", "CORE-DEMO")
    assert (result.returncode, "missing decision D-9" in result.stdout) == (1, True), (
        result.stdout + result.stderr
    )


def test_ac_5_repeated_issue_is_usage(tmp_path):
    result = run_check(tmp_path, v._DECISIONS_LOG_ROWS, "CORE-DEMO", "CORE-DEMO")
    assert (result.returncode, result.stdout.startswith("USAGE:")) == (2, True), (
        result.stdout + result.stderr
    )


def test_ac_6_absent_issue_is_refused_beside_a_present_one(tmp_path):
    result = run_check(tmp_path, v._DECISIONS_LOG_ROWS, "ABSENT-ISSUE", "CORE-DEMO")
    assert (result.returncode, "has no issue ABSENT-ISSUE" in result.stdout) == (1, True), (
        result.stdout + result.stderr
    )


def test_ac_7_every_decision_present_passes(tmp_path):
    several = run_check(
        tmp_path, v._DECISIONS_LOG_ROWS + DECISION_ROW_D9, "OTHER-ISSUE", "CORE-DEMO"
    )
    assert several.returncode == 0, several.stdout + several.stderr
    single = run_check(tmp_path, v._DECISIONS_LOG_ROWS, "CORE-DEMO")
    assert single.returncode == 0, single.stdout + single.stderr
    assert "2 recorded decision(s) reconciled" in single.stdout
