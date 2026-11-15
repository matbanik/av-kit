"""The closeout reads each decision once, in its stage log (Session 84, AC-1..AC-4, AC-6..AC-10).

Every CLI test runs the real validator by subprocess with ``cwd=ROOT`` and writes its own
plan, handoff, grouping and known-issues text under ``tmp_path``. A test whose plan declares
``grouping_source`` makes ``tmp_path`` its own repository (``.agent`` and ``.git``), so the
declared file resolves there under any temp folder.
"""

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

NONE_LOG = "### Decisions Log\n\nNone.\n"
LINK_LIST_LOG = "### Decisions Log\n\n- Kept the table — [D-1](docs/x.md)\n"
EXAMPLE_LOG = (
    "### Decisions Log\n\n- _{the choice in plain words}_ — [D-1](_{path to the stage log}_)\n"
)
D1_TABLE_LOG = v._DECISIONS_LOG_ROWS.replace(v._DECISION_ROW_D3, "")

FULL_FIELDS = {
    "question": '"Which store?"',
    "chosen": '"SQLite"',
    "reasoning": '"precedent converges; two-way door"',
}
MISSING = object()


# -- builders ----------------------------------------------------------------------------


def entry(decision_id: str = "D-1", stage: str = "planning", indent: str = "  ", **fields) -> str:
    """One ``decision_log`` item; a field set to ``MISSING`` is left out, ``""`` is empty."""
    values = {**FULL_FIELDS, **fields}
    lines = [f"{indent}- id: {decision_id}", f"{indent}  stage: {stage}"]
    for key in ("question", "chosen", "reasoning"):
        value = values[key]
        if value is MISSING:
            continue
        lines.append(f"{indent}  {key}:" + (f" {value}" if value else ""))
    return "\n".join(lines) + "\n"


def plan_text(*entries: str, grouping_source: str | None = None) -> str:
    text = v._GOOD_PLAN
    if grouping_source is not None:
        text = text.replace(
            'date: "2026-09-01"\n',
            f'date: "2026-09-01"\ngrouping_source: "{grouping_source}"\n',
            1,
        )
    if entries:
        text += "\n## Decision Log\n\n```yaml\ndecision_log:\n" + "".join(entries) + "```\n"
    return text


def handoff_text(*entries: str) -> str:
    return v._GOOD_HANDOFF.replace(
        "## Decision Log\n\nNone.\n",
        "## Decision Log\n\n```yaml\ndecision_log:\n" + "".join(entries) + "```\n",
    )


def known_issues_text(*entries: str, issue_id: str = "DEMO-ISSUE") -> str:
    return (
        f"issues:\n- id: {issue_id}\n  status: active\n  enrichment:\n    decision_log:\n"
        + "".join(entries)
    )


def issue_entry(decision_id: str = "D-5", **fields) -> str:
    return entry(decision_id, "triage", indent="    ", **fields)


def grouping_text(*replacements: tuple[str, str]) -> str:
    text = v._DECISION_GROUPING
    for old, new in replacements:
        assert old in text, old
        text = text.replace(old, new, 1)
    return text


EMPTY_GROUPING = (
    v._DECISION_GROUPING.split("## 8. Open Decisions")[0]
    + "## 8. Open Decisions\n\nNone.\n\n## 9. Notes\n"
)


def write(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def make_repo(folder: Path) -> Path:
    (folder / ".agent").mkdir(parents=True, exist_ok=True)
    (folder / ".git").mkdir(parents=True, exist_ok=True)
    return folder


def closeout(
    tmp_path: Path,
    *sources: str,
    log: str = NONE_LOG,
    issues: tuple[str, ...] = (),
    reflection: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """The reflection check, with ``log`` as its Decisions Log, over ``sources``."""
    text = reflection if reflection is not None else v._GOOD_REFLECTION.replace(NONE_LOG, log)
    reflection_path = write(tmp_path / "reflection.md", text)
    template = write(tmp_path / "REFLECTION-TEMPLATE.md", v._GOOD_REFLECTION_TEMPLATE)
    args = ["--reflection", reflection_path, "--reflection-template", template]
    for source in sources:
        args += ["--decision-source", source]
    for issue_id in issues:
        args += ["--decision-issue", issue_id]
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=ROOT,
        check=False,
    )


def outcome(result: subprocess.CompletedProcess[str], phrase: str) -> tuple[int, bool]:
    return result.returncode, phrase in result.stdout


def report(result: subprocess.CompletedProcess[str]) -> str:
    return result.stdout + result.stderr


# -- AC-1: a decision stated in full is read -----------------------------------------------


def test_ac_1_block_scalar_reasoning_is_read(tmp_path):
    plan = write(
        tmp_path / "plan.md",
        plan_text(entry(reasoning="|\n      precedent converges;\n      two-way door")),
    )
    result = closeout(tmp_path, plan, log=D1_TABLE_LOG)
    assert result.returncode == 0, report(result)


# -- AC-2: a choice that is still pending ----------------------------------------------------

PENDING_PLAN_CHOICES = {
    "pending": "pending",
    "pending-mat": "Pending Mat",
    # quoted: the grammar refuses a plain scalar that holds ": " before any field is read
    "pending-colon": '"pending: yes"',
    "quoted-then-comment": '"pending Mat" # awaiting reply',
    "escaped": r'"pending Mat"',
}


@pytest.mark.parametrize("chosen", PENDING_PLAN_CHOICES.values(), ids=PENDING_PLAN_CHOICES.keys())
def test_ac_2_pending_plan_choice_is_refused(tmp_path, chosen):
    plan = write(tmp_path / "plan.md", plan_text(entry(chosen=chosen)))
    result = closeout(tmp_path, plan)
    assert outcome(result, "decision_log entry D-1 is still pending") == (1, True), report(result)


def test_ac_2_pending_handoff_choice_is_refused(tmp_path):
    handoff = write(
        tmp_path / "demo-handoff.md", handoff_text(entry("D-2", "execution", chosen="Pending Mat"))
    )
    result = closeout(tmp_path, handoff)
    assert outcome(result, "decision_log entry D-2 is still pending") == (1, True), report(result)


def test_ac_2_pending_issue_choice_is_refused(tmp_path):
    issues = write(tmp_path / "known-issues.yaml", known_issues_text(issue_entry(chosen="pending")))
    result = closeout(tmp_path, issues, issues=("DEMO-ISSUE",))
    assert outcome(result, "decision_log entry D-5 is still pending") == (1, True), report(result)


def test_ac_2_pending_grouping_choice_is_refused(tmp_path):
    grouping = write(
        tmp_path / "demo.md",
        grouping_text(("| autonomous | One |", "| autonomous | pending Mat |")),
    )
    result = closeout(tmp_path, grouping)
    assert outcome(result, "row D-7 is still pending") == (1, True), report(result)


TEXT_THAT_MENTIONS_PENDING = {
    "pending-queue": '"Keep the pending queue"',
    "pendingly": '"Pendingly"',
    "hash-inside-quotes": '"Keep # 3"',
}


@pytest.mark.parametrize(
    "chosen", TEXT_THAT_MENTIONS_PENDING.values(), ids=TEXT_THAT_MENTIONS_PENDING.keys()
)
def test_ac_2_choice_that_is_not_pending_passes(tmp_path, chosen):
    plan = write(tmp_path / "plan.md", plan_text(entry(chosen=chosen)))
    result = closeout(tmp_path, plan)
    assert result.returncode == 0, report(result)


def test_ac_2_open_grouping_row_passes(tmp_path):
    assert v._GROUPING_ROW_D8 in v._DECISION_GROUPING
    grouping = write(tmp_path / "demo.md", grouping_text())
    result = closeout(tmp_path, grouping)
    assert result.returncode == 0, report(result)


# -- AC-3: a blank or non-text choice or question ---------------------------------------------

NON_TEXT_VALUES = {
    "number": "3",
    "boolean": "true",
    "null": "null",
    "no": "no",
    "empty-quotes": '""',
    "flow-sequence": "[a, b]",
    "missing": MISSING,
}
NON_TEXT_CASES = [
    pytest.param(field, value, id=f"{field}-{name}")
    for field in ("chosen", "question")
    for name, value in NON_TEXT_VALUES.items()
] + [
    pytest.param("chosen", '"" # not recorded', id="chosen-commented-empty"),
    pytest.param("question", '"" # not asked', id="question-commented-empty"),
    pytest.param("question", r'"\t"', id="question-escaped-tab"),
    pytest.param("chosen", r'"\x20\L"', id="chosen-escaped-blank"),
]


@pytest.mark.parametrize(("field", "value"), NON_TEXT_CASES)
def test_ac_3_blank_or_non_text_field_is_refused(tmp_path, field, value):
    plan = write(tmp_path / "plan.md", plan_text(entry(**{field: value})))
    result = closeout(tmp_path, plan)
    assert outcome(result, f"has a blank or non-text {field}") == (1, True), report(result)


@pytest.mark.parametrize(
    ("replacement", "column"),
    [
        pytest.param(("| autonomous | One |", "| autonomous |  |"), "Chosen", id="chosen-empty"),
        pytest.param(("| autonomous | One |", "| autonomous | — |"), "Chosen", id="chosen-dash"),
        pytest.param(("| D-7 | One session or two? |", "| D-7 |  |"), "Question", id="question"),
    ],
)
def test_ac_3_blank_grouping_cell_is_refused(tmp_path, replacement, column):
    grouping = write(tmp_path / "demo.md", grouping_text(replacement))
    result = closeout(tmp_path, grouping)
    assert outcome(result, f"row D-7 has a blank {column} cell") == (1, True), report(result)


@pytest.mark.parametrize(
    "fields",
    [
        pytest.param({"chosen": '"3 rounds"'}, id="number-then-words"),
        pytest.param({"chosen": r'"say \"x\" \x7Bid\x7D"'}, id="escaped-text"),
    ],
)
def test_ac_3_text_field_passes(tmp_path, fields):
    plan = write(tmp_path / "plan.md", plan_text(entry(**fields)))
    result = closeout(tmp_path, plan)
    assert result.returncode == 0, report(result)


def test_ac_3_grouping_cell_has_no_type_rule(tmp_path):
    grouping = write(
        tmp_path / "demo.md", grouping_text(("| autonomous | One |", "| autonomous | 49 |"))
    )
    result = closeout(tmp_path, grouping)
    assert result.returncode == 0, report(result)


# -- AC-4: a blank reasoning -------------------------------------------------------------------

BLANK_REASONING = {
    "empty-quotes": '""',
    "empty-value": "",
    "blank-block": "|\n",
    "commented-empty": '"" # later',
}


@pytest.mark.parametrize("reasoning", BLANK_REASONING.values(), ids=BLANK_REASONING.keys())
def test_ac_4_blank_reasoning_is_refused(tmp_path, reasoning):
    plan = write(tmp_path / "plan.md", plan_text(entry(reasoning=reasoning)))
    result = closeout(tmp_path, plan)
    assert outcome(result, "has a blank or non-text reasoning") == (1, True), report(result)


def test_ac_4_saved_newline_reasoning_is_refused(tmp_path):
    data = {
        "version": 1,
        "issues": [
            {
                "id": "DEMO-ISSUE",
                "title": "Demo issue",
                "severity": "low",
                "component": "agent",
                "status": "open",
                "discovered": "2026-11-05",
                "root_cause": "demo",
                "blast_radius": "demo",
                "enrichment": {
                    "decision_log": [
                        {
                            "id": "D-5",
                            "stage": "triage",
                            "question": "Scope the fix?",
                            "chosen": "New MEU",
                            "reasoning": "\n",
                        }
                    ]
                },
            }
        ],
    }
    path = tmp_path / "known-issues.yaml"
    model.save(data, path)
    assert 'reasoning: "\\n"' in path.read_text(encoding="utf-8")
    result = closeout(tmp_path, str(path), issues=("DEMO-ISSUE",))
    assert outcome(result, "D-5 has a blank or non-text reasoning") == (1, True), report(result)


@pytest.mark.parametrize(
    "replacement",
    [
        pytest.param(("| p15 precedent; two-way door |", "|  |"), id="ruled-row"),
        pytest.param(("| needs the S1 outcome |", "|  |"), id="open-row"),
    ],
)
def test_ac_4_blank_grouping_reasoning_is_refused(tmp_path, replacement):
    grouping = write(tmp_path / "demo.md", grouping_text(replacement))
    result = closeout(tmp_path, grouping)
    assert outcome(result, "has a blank Reasoning cell") == (1, True), report(result)


@pytest.mark.parametrize(
    "reasoning",
    [
        pytest.param('"precedent"', id="one-word"),
        pytest.param(r"'a \n stays as written'", id="single-quoted-backslash"),
    ],
)
def test_ac_4_stated_reasoning_passes(tmp_path, reasoning):
    plan = write(tmp_path / "plan.md", plan_text(entry(reasoning=reasoning)))
    result = closeout(tmp_path, plan)
    assert result.returncode == 0, report(result)


# -- AC-6: the reflection's Decisions Log holds no template example -----------------------------


@pytest.mark.parametrize(
    ("log", "want"),
    [
        pytest.param(EXAMPLE_LOG, 1, id="template-example"),
        pytest.param(LINK_LIST_LOG, 0, id="link-list"),
        pytest.param(NONE_LOG, 0, id="none"),
    ],
)
def test_ac_6_decisions_log_example_is_refused(tmp_path, log, want):
    result = closeout(tmp_path, log=log)
    phrase = "still holds the template example"
    assert outcome(result, phrase) == (want, want == 1), report(result)


# -- AC-7: the reflection no longer restates the stage logs --------------------------------------


def four_sources(tmp_path: Path, plan_chosen: str = '"SQLite"') -> list[str]:
    make_repo(tmp_path)
    return [
        write(
            tmp_path / "plan.md",
            plan_text(entry(chosen=plan_chosen), grouping_source="demo.md"),
        ),
        write(
            tmp_path / "demo-handoff.md",
            handoff_text(entry("D-2", "execution", question='"Retry budget?"', chosen='"3 tries"')),
        ),
        write(tmp_path / "demo.md", grouping_text()),
        write(
            tmp_path / "known-issues.yaml",
            known_issues_text(issue_entry("D-3", question='"Scope the fix?"', chosen='"New MEU"')),
        ),
    ]


@pytest.mark.parametrize("log", [NONE_LOG, LINK_LIST_LOG], ids=["none", "link-list"])
def test_ac_7_reflection_need_not_list_stage_log_decisions(tmp_path, log):
    result = closeout(tmp_path, *four_sources(tmp_path), log=log, issues=("DEMO-ISSUE",))
    assert outcome(result, "stage-log decision(s) read") == (0, True), report(result)


def test_ac_7_pending_plan_choice_still_refused(tmp_path):
    sources = four_sources(tmp_path, plan_chosen='"pending Mat"')
    result = closeout(tmp_path, *sources, log=LINK_LIST_LOG, issues=("DEMO-ISSUE",))
    assert outcome(result, "is still pending") == (1, True), report(result)


# -- AC-8: the kept checks still refuse ----------------------------------------------------------


def test_ac_8_one_decision_has_one_stage(tmp_path):
    plan = write(tmp_path / "plan.md", plan_text(entry()))
    handoff = write(tmp_path / "demo-handoff.md", handoff_text(entry("D-1", "execution")))
    result = closeout(tmp_path, plan, handoff)
    assert outcome(result, "one decision has one stage") == (1, True), report(result)


@pytest.mark.parametrize("kind", ["plan", "handoff", "grouping", "issue"])
def test_ac_8_repeated_id_in_one_source_is_refused(tmp_path, kind):
    issues: tuple[str, ...] = ()
    if kind == "plan":
        source, decision_id = write(tmp_path / "plan.md", plan_text(entry(), entry())), "D-1"
    elif kind == "handoff":
        two = entry("D-2", "execution") + entry("D-2", "execution", question='"Timeout?"')
        source, decision_id = write(tmp_path / "demo-handoff.md", handoff_text(two)), "D-2"
    elif kind == "grouping":
        source = write(
            tmp_path / "demo.md",
            grouping_text((v._GROUPING_ROW_D8, v._GROUPING_ROW_D8.replace("D-8", "D-7"))),
        )
        decision_id = "D-7"
    else:
        source = write(
            tmp_path / "known-issues.yaml", known_issues_text(issue_entry(), issue_entry())
        )
        decision_id, issues = "D-5", ("DEMO-ISSUE",)
    result = closeout(tmp_path, source, issues=issues)
    phrase = f"repeats decision ID {decision_id}"
    assert outcome(result, phrase) == (1, True), report(result)


def test_ac_8_declared_grouping_must_be_a_source(tmp_path):
    make_repo(tmp_path)
    write(tmp_path / "demo.md", grouping_text())
    plan = write(tmp_path / "plan.md", plan_text(entry(), grouping_source="demo.md"))
    result = closeout(tmp_path, plan)
    assert outcome(result, "declares grouping_source") == (1, True), report(result)


@pytest.mark.parametrize(
    ("old", "new", "phrase"),
    [
        pytest.param(
            "   The AC table reconciliation.\n",
            "   _Answer here_\n",
            "unfilled template marker",
            id="unfilled-marker",
        ),
        pytest.param(
            "### Friction Log\n", "### Friction notes\n", "is missing 1 section", id="section"
        ),
    ],
)
def test_ac_8_reflection_shape_is_still_checked(tmp_path, old, new, phrase):
    assert old in v._GOOD_REFLECTION
    plan = write(tmp_path / "plan.md", plan_text(entry()))
    result = closeout(tmp_path, plan, reflection=v._GOOD_REFLECTION.replace(old, new, 1))
    assert outcome(result, phrase) == (1, True), report(result)


# -- AC-9: the project root stops at the repository ----------------------------------------------


def _outer_dot_git_dir(base: Path) -> tuple[Path, Path]:
    (base / ".agent").mkdir()
    (base / "repo" / ".git").mkdir(parents=True)
    return base / "repo" / "plan.md", base / "repo"


def _outer_dot_git_file(base: Path) -> tuple[Path, Path]:
    (base / ".agent").mkdir()
    (base / "repo").mkdir()
    (base / "repo" / ".git").write_text("gitdir: ../elsewhere\n", encoding="utf-8")
    return base / "repo" / "plan.md", base / "repo"


def _root_two_levels_up(base: Path) -> tuple[Path, Path]:
    make_repo(base)
    (base / "a" / "b").mkdir(parents=True)
    return base / "a" / "b" / "plan.md", base


def _root_beside_plan(base: Path) -> tuple[Path, Path]:
    make_repo(base / "here")
    return base / "here" / "plan.md", base / "here"


@pytest.mark.parametrize(
    "layout",
    [_outer_dot_git_dir, _outer_dot_git_file, _root_two_levels_up, _root_beside_plan],
    ids=["outer-agent-git-dir", "outer-agent-git-file", "root-two-levels-up", "root-beside-plan"],
)
def test_ac_9_project_root_stops_at_the_repository(tmp_path, layout):
    plan, want = layout(tmp_path)
    plan.write_text(v._GOOD_PLAN, encoding="utf-8")
    assert v.project_root(str(plan)) == want.resolve()


# -- AC-10: an outer .agent folder's grouping cannot stand in --------------------------------------


def nested_repo(tmp_path: Path) -> tuple[str, str, str]:
    nest = tmp_path / "nest"
    (nest / ".agent").mkdir(parents=True)
    decoy = write(nest / "demo.md", EMPTY_GROUPING)
    (nest / "repo" / ".git").mkdir(parents=True)
    plan = write(nest / "repo" / "plan.md", plan_text(grouping_source="demo.md"))
    actual = write(nest / "repo" / "demo.md", grouping_text())
    return plan, decoy, actual


def test_ac_10_outer_decoy_grouping_is_refused(tmp_path):
    plan, decoy, _actual = nested_repo(tmp_path)
    result = closeout(tmp_path, plan, decoy)
    assert outcome(result, "declares grouping_source") == (1, True), report(result)


def test_ac_10_repository_grouping_is_read(tmp_path):
    plan, _decoy, actual = nested_repo(tmp_path)
    result = closeout(tmp_path, plan, actual)
    assert result.returncode == 0, report(result)
