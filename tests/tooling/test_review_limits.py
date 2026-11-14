"""Review loops stop on rounds, not tokens (plan 2026-11-14-review-limits-no-token-budget).

AC-1 reads the repository's ``.agent/review-limits.json``. Every other test copies
``tools/review_ledger.py`` into a temporary root beside the verdict schema and the mechanism
vocabulary, so the copy's ``REPO_ROOT`` is that root and each test writes its own limits
file. CLI tests run the copy by subprocess with ``RECEIPTS_DIR`` inside ``tmp_path``; unit
tests import the copy. Every test asserts before it reads a field or calls a function the
change adds, so a run against the old ledger fails by assertion, not by a missing name.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "tools" / "review_ledger.py"
LIMITS = ROOT / ".agent" / "review-limits.json"
MODES = ("plan", "execution", "discovery", "handoff", "multi-handoff")
ROUNDS = {"plan": 3, "execution": 6, "discovery": 2, "handoff": 3, "multi-handoff": 3}
TOKENS = {
    "plan": 10_500_000,
    "execution": 21_000_000,
    "discovery": 7_000_000,
    "handoff": 10_500_000,
    "multi-handoff": 10_500_000,
}
EXPECTED = {
    "schema": "review-limits/1",
    "token_budgets": "off",
    "rounds": ROUNDS,
    "tokens": TOKENS,
}
GOAL = "Bounded independent review of the fixture plan for review limits"
CONTINUE_WHO = (
    "--said",
    "Mat continues this fixture loop on purpose",
    "--by",
    "Mat",
    "--at",
    "2026-11-14T10:00:00",
)


# --- fixtures and helpers ---------------------------------------------------------


@pytest.fixture
def root(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    for rel in (
        "tools/review_ledger.py",
        ".agent/schemas/review-verdict.schema.v2.json",
        ".agent/context/review-vocabulary.yaml",
    ):
        dest = repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dest)
    return repo


def write_limits(root: Path, switch: str = "off", text: str | None = None, **rounds: int) -> Path:
    path = root / ".agent" / "review-limits.json"
    if text is None:
        text = json.dumps(
            {
                "schema": "review-limits/1",
                "token_budgets": switch,
                "rounds": {**ROUNDS, **rounds},
                "tokens": dict(TOKENS),
            }
        )
    path.write_text(text, encoding="utf-8")
    return path


def receipts(root: Path) -> Path:
    return root.parent / "receipts"


def run_ledger(root: Path, *args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "RECEIPTS_DIR": str(receipts(root)), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, str(root / "tools" / "review_ledger.py"), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=root,
        env=env,
        check=False,
    )


def plan_file(
    root: Path, block: str | None = None, name: str = "fixture", task_block: str | None = None
) -> Path:
    folder = root / "docs" / "plans" / name
    folder.mkdir(parents=True, exist_ok=True)
    front = "---\nproject: fixture\n" + (block or "") + "---\n"
    path = folder / "implementation-plan.md"
    path.write_text(front + "\n| AC-1 | fixture |\n", encoding="utf-8")
    if task_block is not None:
        (folder / "task.md").write_text(
            "---\nproject: fixture\n" + task_block + "---\n", encoding="utf-8"
        )
    return path


def block(
    plan_rounds="3",
    execution_rounds="6",
    plan_tokens="off",
    execution_tokens="off",
    basis="repo",
    extra="",
) -> str:
    return (
        "review_limits:\n"
        "  schema: review-limits/1\n"
        f"  plan_rounds: {plan_rounds}\n"
        f"  execution_rounds: {execution_rounds}\n"
        f"  plan_tokens: {plan_tokens}\n"
        f"  execution_tokens: {execution_tokens}\n"
        f"  basis: {basis}\n" + extra
    )


def begin(
    root: Path, loop: str, mode: str = "plan", ac_file: Path | None = None, *extra: str
) -> subprocess.CompletedProcess:
    plan = ac_file if ac_file is not None else plan_file(root, name=f"plan-{loop}")
    return run_ledger(
        root,
        "begin",
        "--loop-id",
        loop,
        "--review-mode",
        mode,
        "--producer",
        "claude-opus",
        "--goal-anchor",
        GOAL,
        "--ac-file",
        str(plan),
        *extra,
    )


def ledger_file(root: Path, loop: str) -> Path:
    return receipts(root) / "review-ledger" / f"{loop}.json"


def read_ledger(root: Path, loop: str) -> dict:
    path = ledger_file(root, loop)
    assert path.is_file(), f"no ledger written at {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def edit_ledger(root: Path, loop: str, **changes) -> None:
    path = ledger_file(root, loop)
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw.update(changes)
    path.write_text(json.dumps(raw), encoding="utf-8")


def output(result: subprocess.CompletedProcess) -> str:
    # Each line is marked as the child's, so a traceback the old ledger prints is read as the
    # assertion's message, never as this test's own error (red-check.py).
    return "\n".join(f"child| {line}" for line in (result.stdout + result.stderr).splitlines())


def load_copy(root: Path):
    name = f"review_ledger_copy_{abs(hash(str(root)))}"
    spec = importlib.util.spec_from_file_location(name, root / "tools" / "review_ledger.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def usage_round(n: int, usage: int) -> dict:
    return {
        "round": n,
        "agent": "reviewer-a",
        "verdict": "changes_required",
        "date": "2026-11-14",
        "blocking": 0,
        "findings": [],
        "usage": usage,
        "unmeasured": False,
        "intent_achieved": "partial",
    }


def unit_ledger(token_budget, rounds: list[dict], round_budget: int = 3) -> dict:
    return {
        "loop_id": "unit",
        "review_mode": "plan",
        "round_budget": round_budget,
        "token_budget": token_budget,
        "rounds": rounds,
        "grants": [],
        "mechanism_reliefs": [],
        "goal_anchor": GOAL,
    }


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- AC-1: the repository's limits file --------------------------------------------


def test_ac_1_repo_limits_file_holds_the_approved_values(root):
    assert LIMITS.is_file(), f"{LIMITS} does not exist"
    assert b"\r" not in LIMITS.read_bytes(), "the limits file must be LF"
    data = json.loads(LIMITS.read_text(encoding="utf-8"))
    assert data == EXPECTED
    module = load_copy(root)
    assert data["tokens"] == module.TOKEN_BUDGETS
    assert hasattr(module, "read_repo_limits"), "the ledger has no read_repo_limits"
    found = module.read_repo_limits(ROOT)
    assert found is not None and found[0] == EXPECTED


def test_ac_1_a_changed_copy_fails_the_equality_check():
    on = {**EXPECTED, "token_budgets": "on"}
    four = {**EXPECTED, "rounds": {**ROUNDS, "plan": 4}}
    assert on != EXPECTED
    assert four != EXPECTED


# --- AC-2: begin takes each mode's limits from the file ----------------------------


@pytest.mark.parametrize("mode", MODES)
def test_ac_2_begin_reads_the_repo_file(root, mode):
    limits = write_limits(root, "off")
    result = begin(root, f"loop-{mode}", mode)
    assert result.returncode == 0, output(result)
    first = result.stdout.splitlines()[0]
    assert f"mode={mode}" in first
    assert f"budget={ROUNDS[mode]} " in first
    assert "tokens=off" in first, first
    assert "source=" in first, first
    data = read_ledger(root, f"loop-{mode}")
    assert data["round_budget"] == ROUNDS[mode]
    assert data["token_budget"] == "off"
    assert "limits_source" in data, sorted(data)
    assert data["limits_source"]["repo"] == sha(limits)


@pytest.mark.parametrize("mode", MODES)
def test_ac_2_no_repo_file_uses_the_constants(root, mode):
    result = begin(root, f"loop-{mode}", mode)
    assert result.returncode == 0, output(result)
    assert "source=constants" in result.stdout.splitlines()[0], result.stdout
    data = read_ledger(root, f"loop-{mode}")
    assert data["token_budget"] == TOKENS[mode]


# --- AC-3: a malformed file fails closed -------------------------------------------


def _good() -> dict:
    return {
        "schema": "review-limits/1",
        "token_budgets": "off",
        "rounds": dict(ROUNDS),
        "tokens": dict(TOKENS),
    }


def _malformed() -> dict[str, str]:
    wrong_schema = {**_good(), "schema": "review-limits/2"}
    missing_mode = _good()
    del missing_mode["rounds"]["discovery"]
    extra_key = {**_good(), "extra": 1}
    round_zero = _good()
    round_zero["rounds"]["plan"] = 0
    round_true = _good()
    round_true["rounds"]["plan"] = True
    maybe = {**_good(), "token_budgets": "maybe"}
    token_zero = _good()
    token_zero["tokens"]["plan"] = 0
    good = json.dumps(_good())
    duplicate = good[:-1] + ', "schema": "review-limits/1"}'
    return {
        "wrong-schema": json.dumps(wrong_schema),
        "missing-mode": json.dumps(missing_mode),
        "extra-key": json.dumps(extra_key),
        "round-zero": json.dumps(round_zero),
        "round-true": json.dumps(round_true),
        "token-budgets-maybe": json.dumps(maybe),
        "token-zero": json.dumps(token_zero),
        "duplicate-key": duplicate,
    }


@pytest.mark.parametrize("case", sorted(_malformed()))
def test_ac_3_malformed_repo_file_fails_closed(root, case):
    write_limits(root, text=_malformed()[case])
    result = begin(root, "loop-bad")
    assert result.returncode == 3, output(result)
    assert result.stdout.startswith("FAIL-CLOSED:"), output(result)
    assert not ledger_file(root, "loop-bad").exists()


# --- AC-4: no token stop under off ----------------------------------------------


@pytest.mark.parametrize("usage", [0, 1, 10**6, 10**12])
def test_ac_4_off_ledger_has_no_tokens_stop(root, usage):
    module = load_copy(root)
    assert hasattr(module, "resolve_limits"), "the ledger has no review-limits path"
    ledger = unit_ledger("off", [usage_round(1, usage)])
    kinds = [kind for kind, _ in module.stops(ledger)]
    assert "tokens" not in kinds, kinds
    readout = module.stop_readout(ledger)
    assert "off (" in readout and "not budgeted" in readout, readout


def test_ac_4_a_numeric_budget_still_stops(root):
    module = load_copy(root)
    ledger = unit_ledger(1, [usage_round(1, 5)])
    kinds = [kind for kind, _ in module.stops(ledger)]
    assert "tokens" in kinds, kinds


# --- AC-5: state on an off loop ------------------------------------------------------


def test_ac_5_state_says_not_budgeted_and_names_the_repo_file(root):
    limits = write_limits(root, "off")
    assert begin(root, "loop-state").returncode == 0
    result = run_ledger(root, "state", "--loop-id", "loop-state")
    assert result.returncode == 0, output(result)
    assert "off (0 spent, not budgeted)" in result.stdout, result.stdout
    lines = [
        line.strip() for line in result.stdout.splitlines() if line.strip().startswith("limits:")
    ]
    assert lines, result.stdout
    assert f"repo:{sha(limits)[:12]}" in lines[0], lines[0]


def test_ac_5_a_legacy_ledger_says_so(root):
    assert begin(root, "loop-legacy").returncode == 0
    raw = json.loads(ledger_file(root, "loop-legacy").read_text(encoding="utf-8"))
    raw.pop("limits_source", None)
    ledger_file(root, "loop-legacy").write_text(json.dumps(raw), encoding="utf-8")
    result = run_ledger(root, "state", "--loop-id", "loop-legacy")
    assert result.returncode == 0, output(result)
    assert "(pre-review-limits ledger)" in result.stdout, result.stdout


# --- AC-6: continue --tokens on an off loop --------------------------------------


def test_ac_6_continue_tokens_on_an_off_loop_is_refused(root):
    write_limits(root, "off")
    assert begin(root, "loop-cont").returncode == 0
    before = ledger_file(root, "loop-cont").read_bytes()
    result = run_ledger(root, "continue", "--loop-id", "loop-cont", "--tokens", "1", *CONTINUE_WHO)
    assert result.returncode == 1, output(result)
    assert "nothing to lift" in result.stdout, result.stdout
    assert ledger_file(root, "loop-cont").read_bytes() == before


def test_ac_6_continue_rounds_on_an_off_loop_raises_the_cap(root):
    write_limits(root, "off")
    assert begin(root, "loop-cont").returncode == 0
    assert read_ledger(root, "loop-cont")["token_budget"] == "off"
    result = run_ledger(root, "continue", "--loop-id", "loop-cont", "--rounds", "1", *CONTINUE_WHO)
    assert result.returncode == 0, output(result)
    state = run_ledger(root, "state", "--loop-id", "loop-cont")
    assert state.returncode == 0, output(state)
    assert "rounds     0/4" in state.stdout, state.stdout


# --- AC-7: an off loop still stops at its round cap --------------------------------


def test_ac_7_off_loop_stops_at_the_round_cap(root):
    module = load_copy(root)
    assert hasattr(module, "resolve_limits"), "the ledger cannot hold an off loop"
    full = unit_ledger("off", [usage_round(n, 10) for n in (1, 2, 3)])
    assert "budget" in [kind for kind, _ in module.stops(full)]
    short = unit_ledger("off", [usage_round(n, 10) for n in (1, 2)])
    assert "budget" not in [kind for kind, _ in module.stops(short)]


# --- AC-8: a ledger with a bad budget or source fails closed -------------------------


@pytest.mark.parametrize(
    "value", [0, None, -1, True, "none", 1.5], ids=["0", "null", "-1", "true", "none", "1.5"]
)
def test_ac_8_bad_token_budget_fails_closed(root, value):
    assert begin(root, "loop-bad").returncode == 0
    edit_ledger(root, "loop-bad", token_budget=value)
    result = run_ledger(root, "state", "--loop-id", "loop-bad")
    assert result.returncode == 3, output(result)


def test_ac_8_unknown_limits_source_key_fails_closed(root):
    assert begin(root, "loop-bad").returncode == 0
    edit_ledger(
        root, "loop-bad", limits_source={"repo": "constants", "plan": None, "flags": [], "extra": 1}
    )
    result = run_ledger(root, "state", "--loop-id", "loop-bad")
    assert result.returncode == 3, output(result)


def test_ac_8_integer_budget_without_source_loads(root):
    assert begin(root, "loop-old").returncode == 0
    raw = json.loads(ledger_file(root, "loop-old").read_text(encoding="utf-8"))
    raw.pop("limits_source", None)
    raw["token_budget"] = 10_500_000
    ledger_file(root, "loop-old").write_text(json.dumps(raw), encoding="utf-8")
    result = run_ledger(root, "state", "--loop-id", "loop-old")
    assert result.returncode == 0, output(result)


# --- AC-9: the plan block -------------------------------------------------------


@pytest.mark.parametrize(("mode", "budget"), [("plan", 2), ("execution", 5)])
def test_ac_9_tightened_block_applies_to_plan_and_execution(root, mode, budget):
    write_limits(root, "off")
    plan = plan_file(root, block(plan_rounds="2", execution_rounds="5", basis="tightened"))
    result = begin(root, f"loop-{mode}", mode, plan)
    assert result.returncode == 0, output(result)
    first = result.stdout.splitlines()[0]
    assert f"budget={budget} " in first, first
    assert "plan=" in first, first
    data = read_ledger(root, f"loop-{mode}")
    assert "limits_source" in data, sorted(data)
    assert data["limits_source"]["plan"] == str(plan)


def test_ac_9_repo_basis_with_equal_values_is_accepted(root):
    write_limits(root, "off")
    plan = plan_file(root, block(basis="repo"))
    result = begin(root, "loop-repo", "plan", plan)
    assert result.returncode == 0, output(result)
    first = result.stdout.splitlines()[0]
    assert "budget=3 " in first and "plan=" in first, first


def test_ac_9_discovery_ignores_the_block(root):
    write_limits(root, "off")
    plan = plan_file(root, block(plan_rounds="1", execution_rounds="1", basis="tightened"))
    result = begin(root, "loop-disc", "discovery", plan)
    assert result.returncode == 0, output(result)
    data = read_ledger(root, "loop-disc")
    assert "limits_source" in data, sorted(data)
    assert data["limits_source"]["plan"] is None
    assert data["round_budget"] == ROUNDS["discovery"]
    assert "plan=" not in result.stdout.splitlines()[0]


@pytest.mark.parametrize(
    "case",
    ["basis-contradicted", "unknown-key", "plan-rounds-zero", "plan-tokens-maybe"],
)
def test_ac_9_malformed_block_fails_closed(root, case):
    write_limits(root, "off")
    text = {
        "basis-contradicted": block(plan_rounds="2", basis="repo"),
        "unknown-key": block(extra="  extra_rounds: 2\n"),
        "plan-rounds-zero": block(plan_rounds="0", basis="tightened"),
        "plan-tokens-maybe": block(plan_tokens="maybe", basis="tightened"),
    }[case]
    result = begin(root, "loop-block", "plan", plan_file(root, text))
    assert result.returncode == 3, output(result)
    assert not ledger_file(root, "loop-block").exists()


def test_ac_9_block_that_differs_from_task_is_refused(root):
    write_limits(root, "off")
    plan = plan_file(
        root,
        block(plan_rounds="2", basis="tightened"),
        task_block=block(plan_rounds="1", basis="tightened"),
    )
    result = begin(root, "loop-differs", "plan", plan)
    assert result.returncode == 1, output(result)
    assert "differs between" in result.stdout, result.stdout
    assert not ledger_file(root, "loop-differs").exists()


# --- AC-10: a loosened block without run_parameters.py ----------------------------


def test_ac_10_loosened_block_is_refused_and_names_continue(root):
    write_limits(root, "off")
    assert not (root / "tools" / "run_parameters.py").exists()
    plan = plan_file(root, block(plan_rounds="4", basis="loosened"))
    result = begin(root, "loop-loose", "plan", plan)
    text = output(result)
    assert result.returncode == 1, text
    assert "needs tools/run_parameters.py, which this repo does not have" in text, text
    assert "review_ledger.py continue" in text, text
    assert "can't open file" not in text, text
    assert not ledger_file(root, "loop-loose").exists()


# --- AC-11: flags only tighten ------------------------------------------------------


def test_ac_11_round_flag_tightens(root):
    write_limits(root, "off")
    result = begin(root, "loop-flag", "plan", None, "--round-budget", "2")
    assert result.returncode == 0, output(result)
    first = result.stdout.splitlines()[0]
    assert "budget=2 " in first and "flags=round_budget" in first, first


def test_ac_11_token_flag_tightens_off(root):
    write_limits(root, "off")
    result = begin(root, "loop-flag", "plan", None, "--token-budget", "5000000")
    assert result.returncode == 0, output(result)
    data = read_ledger(root, "loop-flag")
    assert data["token_budget"] == 5_000_000
    assert "limits_source" in data, sorted(data)
    assert data["limits_source"]["flags"] == ["token_budget"]


def test_ac_11_round_flag_loosening_is_refused(root):
    write_limits(root, "off")
    result = begin(root, "loop-flag", "plan", None, "--round-budget", "4")
    assert result.returncode == 1, output(result)
    assert "only tighten" in result.stdout, result.stdout
    assert not ledger_file(root, "loop-flag").exists()


def test_ac_11_token_off_flag_under_an_on_file_is_refused(root):
    write_limits(root, "on")
    result = begin(root, "loop-flag", "plan", None, "--token-budget", "off")
    assert result.returncode == 1, output(result)
    assert "only tighten" in result.stdout, result.stdout
    assert not ledger_file(root, "loop-flag").exists()


@pytest.mark.parametrize(
    "flags",
    [("--round-budget", "0"), ("--token-budget", "0"), ("--token-budget", "abc")],
    ids=["round-0", "token-0", "token-abc"],
)
def test_ac_11_bad_flag_values_are_usage_errors(root, flags):
    write_limits(root, "off")
    result = begin(root, "loop-flag", "plan", None, *flags)
    assert result.returncode == 2, output(result)
    assert not ledger_file(root, "loop-flag").exists()
