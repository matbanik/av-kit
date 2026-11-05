"""Session 49 triage-decision extract (task row 7 and H2-2; plan §Verification Plan 4; D-272).

The closeout validator can't read known-issues.yaml as model.save writes it: its bounded grammar
refuses the indentless lists and the wrapped values. This writes the decision logs of the two
issues this session reconciles, unchanged, to EXTRACT in the validator's grammar. It exits 1
unless the extract reads back equal to a fresh load of the register and the validator's own
issue_decision_log returns the ids and stages the register holds. The register is never written.
FETCH-FFMPEG-EXIT-CODES holds no decisions, so it isn't extracted.
"""

from __future__ import annotations

import copy
import hashlib
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

import validate_closeout_artifacts as validator  # noqa: E402
import yaml  # noqa: E402
from issue_triage import model  # noqa: E402

REGISTER = ROOT / ".agent" / "context" / "known-issues.yaml"
EXTRACT = Path("C:/Temp/av-kit/rc2/issue-decisions.yaml")
ISSUES = ("UNINSTALL-LEAVES-INSTALLER-COPY", "FFMPEG-LIBDVDCSS-BUNDLED")


class IndentedDumper(yaml.SafeDumper):
    """Indents every sequence under its key, the one list shape the bounded grammar reads."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow, False)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decision_log(register: dict[str, Any], issue_id: str) -> list[dict[str, Any]] | None:
    issue = model.get_issue(register, issue_id)
    if issue is None:
        return None
    return (issue.get("enrichment") or {}).get("decision_log")


def main() -> int:
    before = sha256(REGISTER)
    register = model.load(REGISTER)
    payload: dict[str, list[dict[str, Any]]] = {"issues": []}
    for issue_id in ISSUES:
        log = decision_log(register, issue_id)
        if not log:
            print(f"FAIL: the register holds no decision_log for {issue_id}")
            return 1
        payload["issues"].append(
            {"id": issue_id, "enrichment": {"decision_log": copy.deepcopy(log)}}
        )
    EXTRACT.parent.mkdir(parents=True, exist_ok=True)
    EXTRACT.write_text(
        yaml.dump(payload, Dumper=IndentedDumper, sort_keys=False, allow_unicode=True, width=10**9),
        encoding="utf-8",
    )

    text = EXTRACT.read_text(encoding="utf-8")
    problems: list[str] = []
    fresh = model.load(REGISTER)
    read_back = yaml.safe_load(text)
    if read_back != payload:
        problems.append("the extract does not read back as it was written")
    for row in read_back["issues"]:
        if row["enrichment"]["decision_log"] != decision_log(fresh, row["id"]):
            problems.append(f"{row['id']}: the extract differs from a fresh load of the register")
    try:
        validator.check_yaml_subset(text, EXTRACT.name)
    except validator.Refuse as exc:
        problems.append(f"bounded grammar: {exc}")
    for issue_id in ISSUES:
        expected = [(entry["id"], entry.get("stage")) for entry in decision_log(fresh, issue_id)]
        try:
            actual = validator.issue_decision_log(text, EXTRACT.name, issue_id)
        except validator.Refuse as exc:
            problems.append(f"{issue_id}: issue_decision_log refused: {exc}")
            continue
        print(f"{issue_id}: {', '.join(f'{d} ({stage})' for d, stage in actual)}")
        if actual != expected:
            problems.append(
                f"{issue_id}: issue_decision_log read {actual}, register has {expected}"
            )
    if validator.PLACEHOLDER.search(text):
        problems.append("the extract matches the validator's placeholder pattern")
    if sha256(REGISTER) != before:
        problems.append("the register changed while the extract ran")

    for problem in problems:
        print(f"FAIL: {problem}")
    print(f"register sha256={before}")
    print(f"extract {EXTRACT} sha256={sha256(EXTRACT)}")
    print(f"issue-decisions: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
