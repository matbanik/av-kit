"""Session 84 stage-log survey (plan §Verification Plan 5; task rows 0 and 8; AC-14).

Usage::

    python stage-log-survey.py [--validator PATH] [--out RECEIPT] [--compare BASE_RECEIPT]
    python stage-log-survey.py --selftest

Reads every stage log in the tree the way the closeout validator reads it, and lists each
entry that the record-once field check refuses: a blank or non-text ``question``,
``chosen`` or ``reasoning``, or a ``chosen`` that starts with ``pending``
(``FIELD_CHECK`` in the plan). The logs read are:

- the fenced ``decision_log`` blocks of every ``docs/execution/plans/*/implementation-plan.md``
  (``fenced_decision_logs``);
- the ``## Decision Log`` of every ``.agent/context/handoffs/*-handoff.md`` that has one
  (``handoff_decisions``);
- ``enrichment.decision_log`` of every issue in ``.agent/context/known-issues.yaml``
  (``issue_decision_log``);
- the ``## 8. Open Decisions`` rows of every ``.agent/context/grouping/*.md`` that has one
  (``grouping_decisions``; added after plan review R1, CRO-P2).

Each YAML entry is judged by the validator's own ``decision_field_text`` when the module
has one (after row 3), and otherwise by ``_planned_field_text`` below: upstream
``a73d6df``'s function with the plan's one deviation, a quoted value read by
``_planned_quoted_text`` so a trailing ``# comment`` is dropped before the quotes are
(D-831, amended after R1, CRO-P1) and a double-quoted body's YAML escapes are decoded
before the blank and pending tests (amended after the R1 recheck, CRO-R1-1). Each grouping
row is judged by the validator's
``grouping_row_problems`` when it has one, and otherwise by
``_planned_grouping_row_problems`` (D-829, amended after R1): a ruled row (Resolution
``autonomous`` or ``human``) needs non-blank Question, Chosen and Reasoning cells and a
Chosen that does not start with ``pending``; an ``open`` row needs Question and Reasoning.
So the plan-time receipt predicts what the port refuses. A plan or handoff is ``open`` when
``docs/execution/reflections/<slug>-reflection.md`` does not exist: its closeout still has
to pass the check. A grouping is ``open`` when no plan declares it as ``grouping_source``
or one that does has no reflection. Every other read failure is reported as
``other-refusal`` with its first line, and is not counted as a field problem.

The run is read-only: it imports the validator from PATH and writes only RECEIPT (default
``C:/Temp/av-kit/cro/stage-log-survey.txt``). Without ``--compare`` it exits 0 after a survey.
With ``--compare BASE_RECEIPT`` (row 0's survey of the base validator, AC-14) it exits 1
unless the ``problem`` lines and the ``other-refusal`` lines, each read without its
``open``/``closed`` word, are the same set in both receipts: the port must refuse exactly the
entries the plan-time prediction named, no more and no fewer. ``--selftest`` exits 1 unless
every planted negative is found, the clean entries are not, and the comparison flags an added
and a missing problem line.
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys
import tempfile
from collections.abc import Callable

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[4]
DEFAULT_VALIDATOR = ROOT / "tools" / "validate_closeout_artifacts.py"
sys.path.insert(0, str(ROOT / "tools"))  # the validator imports durable_evidence from there
DEFAULT_OUT = pathlib.Path("C:/Temp/av-kit/cro/stage-log-survey.txt")
FIELDS = ("question", "chosen", "reasoning")
FIELD_REFUSAL = re.compile(r"blank or non-text|still pending|has a blank \w+ cell")
GROUPING_BLANK = re.compile(r"^[\s`*_]*(?:[-–—][\s`*_]*)?$")
QUOTED = re.compile(r"""^(?:"(?P<double>(?:[^"\\]|\\.)*)"|'(?P<single>(?:[^']|'')*)')[ \t]*(?:#.*)?$""")
# YAML 1.2.2 §5.7's double-quoted escapes, the set the validator's DQ_ESCAPES and
# DQ_HEX_ESCAPES admit (D-831, amended after the R1 recheck, CRO-R1-1).
# tools/issue_triage/model.py writes a value as a double-quoted scalar when it is "\n", ends
# "\n\n" or holds U+0085, U+2028 or U+2029, and PyYAML escapes those characters there.
DOUBLE_ESCAPE = re.compile(
    r"\\(?:x(?P<x>[0-9A-Fa-f]{2})|u(?P<u>[0-9A-Fa-f]{4})|U(?P<U>[0-9A-Fa-f]{8})|(?P<c>.))", re.DOTALL
)
DOUBLE_ESCAPES = {
    "0": "\0", "a": "\a", "b": "\b", "t": "\t", "\t": "\t", "n": "\n", "v": "\v", "f": "\f",
    "r": "\r", "e": "\x1b", " ": " ", '"': '"', "/": "/", "\\": "\\", "N": "\x85",
    "_": "\xa0", "L": "\u2028", "P": "\u2029",
}
DECLARED = re.compile(r"""^grouping_source:\s*["']?([^"'\n#]+?)["']?\s*$""", re.MULTILINE)
SLUG = re.compile(r"(\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*?)(?:-MEU-\d+[a-z]?)?-handoff\.md$")

_NON_TEXT_SCALAR = re.compile(
    r"^(?:~|null|true|false|yes|no|on|off|[-+]?\d[\d_]*(?:\.\d*)?(?:[eE][-+]?\d+)?|[-+]?\.\d+)$",
    re.IGNORECASE,
)


def load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _planned_quoted_text(raw: str) -> str | None:
    """A whole quoted scalar and an optional ``# comment``: the text inside the quotes.

    A ``#`` inside the quotes is text. A double-quoted body is decoded as YAML does, so
    ``"\\n"`` is a newline and ``"\\u0070ending"`` is ``pending``; a single-quoted body has no
    escapes, only ``''`` for ``'``. Anything else that starts with a quote (text after the
    closing quote, an unterminated quote, an escape YAML does not define) is not text: ``None``.
    """
    match = QUOTED.match(raw)
    if match is None:
        return None
    if match.group("single") is not None:
        return match.group("single").replace("''", "'")
    body, out, start = match.group("double"), [], 0
    for escape in DOUBLE_ESCAPE.finditer(body):
        out.append(body[start : escape.start()])
        digits = escape.group("x") or escape.group("u") or escape.group("U")
        if digits is not None:
            if int(digits, 16) > 0x10FFFF:
                return None
            out.append(chr(int(digits, 16)))
        elif escape.group("c") in DOUBLE_ESCAPES:
            out.append(DOUBLE_ESCAPES[escape.group("c")])
        else:
            return None
        start = escape.end()
    out.append(body[start:])
    return "".join(out)


def _planned_grouping_row_problems(cells: list[str]) -> list[str]:
    """The planned ``grouping_row_problems`` for one seven-cell §8 row."""
    resolution = cells[2].strip("`* ")
    named = (("Question", cells[1]), ("Chosen", cells[3]), ("Reasoning", cells[5]))
    problems = [
        f"blank {name} cell"
        for name, cell in named
        if not (name == "Chosen" and resolution == "open") and GROUPING_BLANK.match(cell)
    ]
    if resolution != "open" and re.match(r"pending\b", cells[3].strip("`* "), re.IGNORECASE):
        problems.append("still pending")
    return problems


def _planned_field_text(v, item: str, key: str) -> str | None:
    """upstream a73d6df ``decision_field_text``, quoted values read by ``_planned_quoted_text``."""
    lines = item.splitlines()
    first = next((line for line in lines if line.strip()), "")
    column = len(first) - len(first.lstrip(" \t"))
    for number, line in enumerate(lines):
        match = re.match(rf"^[ \t]{{{column}}}{re.escape(key)}:(?P<value>.*)$", line)
        if match is None:
            continue
        raw = match.group("value").strip()
        deeper = []
        for follow in lines[number + 1 :]:
            if not follow.strip():
                continue
            if len(follow) - len(follow.lstrip(" \t")) <= column:
                break
            deeper.append(follow.strip())
        if raw[:1] in ("|", ">"):
            return " ".join(deeper) if deeper else None
        if not raw or raw.startswith("#"):
            return None
        if raw[:1] in ("[", "{"):
            return None
        if raw[:1] in ('"', "'"):
            value = _planned_quoted_text(raw)
            return value if value is not None and value.strip() else None
        value = raw.split(" #", 1)[0].strip()
        if not value or _NON_TEXT_SCALAR.match(value):
            return None
        return value
    return None


def field_problems(item: str, text_of: Callable[[str, str], str | None]) -> list[str]:
    problems = [f"blank or non-text {f}" for f in FIELDS if text_of(item, f) is None]
    if re.match(r"pending\b", (text_of(item, "chosen") or "").strip(), re.IGNORECASE):
        problems.append("still pending")
    return problems


def survey(v, root: pathlib.Path) -> tuple[list[str], dict[str, int]]:
    live = hasattr(v, "decision_field_text")

    def text_of(item: str, key: str) -> str | None:
        return v.decision_field_text(item, key) if live else _planned_field_text(v, item, key)

    found: list[tuple[str, str, list[str]]] = []
    current: list[str] = [""]
    original = v.decision_entries

    def wrapped(items, label):
        for item in items or []:
            problems = field_problems(item, text_of)
            if problems:
                found.append((current[0], v.item_key(item, "id") or "?", problems))
        try:
            return original(items, label)
        except v.Refuse as exc:
            if FIELD_REFUSAL.search(str(exc)):
                return [(v.item_key(i, "id"), v.item_key(i, "stage")) for i in items or []]
            raise

    v.decision_entries = wrapped
    original_grouping = v.grouping_decisions
    row_problems = getattr(v, "grouping_row_problems", _planned_grouping_row_problems)

    def grouping_wrapped(text, name):
        rows = grouping_rows(v, text)
        for cells in rows:
            if len(cells) == 7:
                problems = row_problems(cells)
                if problems:
                    found.append((current[0], cells[0].strip("`* ") or "?", problems))
        try:
            return original_grouping(text, name)
        except v.Refuse as exc:
            if FIELD_REFUSAL.search(str(exc)):
                return [(cells[0].strip("`* "), "grouping") for cells in rows]
            raise

    v.grouping_decisions = grouping_wrapped
    reflections = root / "docs" / "execution" / "reflections"
    counts = {"sources": 0, "entries": 0, "other-refusal": 0}
    lines: list[str] = []

    def is_open(slug: str | None) -> bool:
        return slug is None or not (reflections / f"{slug}-reflection.md").exists()

    def read(source: str, slug: str | None, reader: Callable[[], list]) -> None:
        current[0] = f"{'open' if is_open(slug) else 'closed'} {source}"
        counts["sources"] += 1
        try:
            counts["entries"] += len(reader())
        except v.Refuse as exc:
            counts["other-refusal"] += 1
            lines.append(f"other-refusal {current[0]}: {str(exc).splitlines()[0][:160]}")

    try:
        for plan in sorted((root / "docs" / "execution" / "plans").glob("*/implementation-plan.md")):
            rel = plan.relative_to(root).as_posix()
            text = plan.read_text(encoding="utf-8")
            read(rel, plan.parent.name, lambda t=text, n=plan.name: v.fenced_decision_logs(t, n))
        for handoff in sorted((root / ".agent" / "context" / "handoffs").glob("*-handoff.md")):
            text = handoff.read_text(encoding="utf-8")
            if not re.search(r"^## Decision Log", text, re.MULTILINE):
                continue
            match = SLUG.search(handoff.name)
            rel = handoff.relative_to(root).as_posix()
            read(rel, match.group(1) if match else None,
                 lambda t=text, n=handoff.name: v.handoff_decisions(t, n))
        register = root / ".agent" / "context" / "known-issues.yaml"
        text = register.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
        logged = [
            i.get("id")
            for i in data.get("issues") or []
            if isinstance(i.get("enrichment"), dict) and "decision_log" in i["enrichment"]
        ]
        for issue in logged:
            read(f"known-issues.yaml issue {issue}", None,
                 lambda t=text, i=issue: v.issue_decision_log(t, "known-issues.yaml", i))
        consumers: dict[str, list[str]] = {}
        for plan in sorted((root / "docs" / "execution" / "plans").glob("*/implementation-plan.md")):
            head = plan.read_text(encoding="utf-8").split("\n---", 1)[0]
            declared = DECLARED.search(head)
            if declared and declared.group(1).strip() not in ("null", "~"):
                name = pathlib.PurePosixPath(declared.group(1).strip()).name
                consumers.setdefault(name, []).append(plan.parent.name)
        for grouping in sorted((root / ".agent" / "context" / "grouping").glob("*.md")):
            text = grouping.read_text(encoding="utf-8")
            if not grouping_rows(v, text):
                continue
            slugs = consumers.get(grouping.name, [])
            slug = next((s for s in slugs if is_open(s)), slugs[0] if slugs else None)
            counts["groupings"] = counts.get("groupings", 0) + 1
            read(grouping.relative_to(root).as_posix(), slug,
                 lambda t=text, n=grouping.name: v.grouping_decisions(t, n))
    finally:
        v.decision_entries = original
        v.grouping_decisions = original_grouping

    by_kind: dict[str, int] = {}
    open_problems = 0
    for where, decision_id, problems in found:
        for problem in problems:
            by_kind[problem] = by_kind.get(problem, 0) + 1
        if where.startswith("open "):
            open_problems += 1
        lines.append(f"problem {where} {decision_id}: {', '.join(problems)}")
    counts["problem-entries"] = len(found)
    counts["open-problems"] = open_problems
    for kind, n in sorted(by_kind.items()):
        counts[f"kind {kind}"] = n
    counts["mode"] = 1 if live else 0
    return lines, counts


def grouping_rows(v, text: str) -> list[list[str]]:
    """The cells of each §8 row, located the way ``grouping_decisions`` locates them."""
    match = re.search(
        r"^## 8\.[^\n]*\n(?P<body>.*?)(?=^## |\Z)", v.markdown_structure(text), re.MULTILINE | re.DOTALL
    )
    if match is None:
        return []
    body = v.HTML_COMMENT.sub("", text[match.start("body") : match.end("body")])
    if body.strip() == "None.":
        return []
    try:
        return v.table_with_header(text[match.start() : match.end()], "## 8.")[1]
    except v.Refuse:
        return []


def findings(text: str) -> set[str]:
    """The receipt's problem and other-refusal lines, without the open/closed word."""
    out = set()
    for line in text.splitlines():
        match = re.match(r"^(problem|other-refusal) (?:open|closed) (.*)$", line)
        if match:
            out.add(f"{match.group(1)} {match.group(2)}")
    return out


def compare(base_text: str, text: str) -> list[str]:
    base, now = findings(base_text), findings(text)
    return [f"added: {line}" for line in sorted(now - base)] + [
        f"missing: {line}" for line in sorted(base - now)
    ]


def report(lines: list[str], counts: dict[str, int]) -> str:
    mode = (
        "live (validator's decision_field_text)"
        if counts["mode"]
        else "simulated (upstream a73d6df copy with the plan's quoted-comment deviation)"
    )
    out = [f"stage-log-survey mode: {mode}"]
    out += lines
    out += [f"{k}: {n}" for k, n in counts.items() if k != "mode"]
    return "\n".join(out) + "\n"


PLANTED = r"""---
project: "2026-01-01-planted"
---

```yaml
decision_log:
  - id: D-1
    stage: planning
    question: "Which store?"
    chosen: "SQLite"
    reasoning: "precedent converges"
  - id: D-2
    stage: planning
    question: "Which cap?"
    chosen: "pending the human ruling"
    reasoning: "brief written"
  - id: D-3
    stage: planning
    question: "How many?"
    chosen: 3
    reasoning: "measured"
  - id: D-4
    stage: planning
    question: "Who?"
    chosen: "Mat"
  - id: D-5
    stage: planning
    question: "Block?"
    chosen: "yes, as text"
    reasoning: |
      a block scalar with a body
  - id: D-6
    stage: planning
    question: "Commented pending?"
    chosen: "pending Mat" # awaiting reply
    reasoning: "brief written"
  - id: D-7
    stage: planning
    question: "" # not asked yet
    chosen: "Keep # 3 as text"
    reasoning: "measured"
  - id: D-8
    stage: planning
    question: "Escaped pending?"
    chosen: "\u0070ending Mat"
    reasoning: "brief written"
  - id: D-9
    stage: planning
    question: "\t"
    chosen: "\x20\L"
    reasoning: "measured"
  - id: D-10
    stage: planning
    question: "Escaped text?"
    chosen: "Keep \"A\" and \x7Bid\x7D\n"
    reasoning: 'a \n stays as written'
```
"""

WRITER_REGISTER = {
    "version": 1,
    "issues": [
        {
            "id": "PLANTED-ISSUE",
            "title": "Demo issue",
            "severity": "low",
            "component": "agent",
            "status": "open",
            "discovered": "2026-11-05",
            "root_cause": "demo",
            "blast_radius": "demo",
            "enrichment": {
                "decision_log": [
                    {"id": "D-30", "stage": "planning", "question": "Q?", "chosen": "A", "reasoning": "\n"}
                ]
            },
        }
    ],
}

PLANTED_GROUPING = """# Planted grouping

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|---|---|---|---|---|---|---|
| D-20 | Which order? | autonomous | 49 | Local Canon | measured | — |
| D-21 | Which cap? | human | pending Mat | Human-approved | brief written | — |
| D-22 | Which store? | autonomous | — | Local Canon | precedent | — |
| D-23 | Licence? | open | — | — | owned by a later session | — |
"""


def selftest(validator: pathlib.Path) -> int:
    v = load(validator, "cro_survey_validator_selftest")
    with tempfile.TemporaryDirectory(dir="C:/Temp/av-kit") as tmp:
        root = pathlib.Path(tmp)
        plan = root / "docs" / "execution" / "plans" / "2026-01-01-planted" / "implementation-plan.md"
        plan.parent.mkdir(parents=True)
        plan.write_text(PLANTED, encoding="utf-8")
        (root / "docs" / "execution" / "reflections").mkdir(parents=True)
        (root / ".agent" / "context" / "handoffs").mkdir(parents=True)
        # The register's own writer, for a reasoning that is only a newline (CRO-R1-1).
        from issue_triage import model

        model.save(WRITER_REGISTER, root / ".agent" / "context" / "known-issues.yaml")
        written = (root / ".agent" / "context" / "known-issues.yaml").read_text(encoding="utf-8")
        (root / ".agent" / "context" / "grouping").mkdir(parents=True)
        (root / ".agent" / "context" / "grouping" / "planted-session-grouping.md").write_text(
            PLANTED_GROUPING, encoding="utf-8"
        )
        lines, counts = survey(v, root)
    got = {line.split(": ", 1)[0].rsplit(" ", 1)[-1]: line for line in lines if line.startswith("problem ")}
    want = {
        "D-2": "still pending",
        "D-3": "blank or non-text chosen",
        "D-4": "blank or non-text reasoning",
        "D-6": "still pending",
        "D-7": "blank or non-text question",
        "D-21": "still pending",
        "D-22": "blank Chosen cell",
        "D-8": "still pending",
        "D-9": "blank or non-text question",
        "D-30": "blank or non-text reasoning",
    }
    failures = [f"{d} not refused for {w!r}" for d, w in want.items() if w not in got.get(d, "")]
    clean = ("D-1", "D-5", "D-10", "D-20", "D-23")
    failures += [f"{d} refused but states every field" for d in clean if d in got]
    if "chosen" in got.get("D-7", "").split(": ", 1)[-1]:
        failures.append("D-7's quoted chosen with a # inside was not read as text")
    if "blank or non-text chosen" not in got.get("D-9", ""):
        failures.append("D-9's escaped blank chosen was not refused")
    if 'reasoning: "\\n"' not in written:
        failures.append("model.save no longer writes a newline-only reasoning as \"\\n\"")
    if set(DOUBLE_ESCAPES) != set(v.DQ_ESCAPES):
        failures.append("DOUBLE_ESCAPES no longer decodes exactly the validator's DQ_ESCAPES")
    if _planned_quoted_text(r'"\q"') is not None:
        failures.append("an escape YAML does not define was read as text")
    if counts.get("open-problems") != 10:
        failures.append(f"open-problems {counts.get('open-problems')} != 10")
    if counts.get("groupings") != 1:
        failures.append(f"groupings {counts.get('groupings')} != 1")
    receipt = report(lines, counts)
    if compare(receipt, receipt):
        failures.append("a receipt compared with itself differs")
    fewer = "\n".join(line for line in receipt.splitlines() if " D-2:" not in line)
    if not any(d.startswith("added: ") for d in compare(fewer, receipt)):
        failures.append("an added problem line was not flagged")
    if not any(d.startswith("missing: ") for d in compare(receipt, fewer)):
        failures.append("a missing problem line was not flagged")
    for f in failures:
        print(f"FAIL {f}")
    print(f"stage-log-survey selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--validator", type=pathlib.Path, default=DEFAULT_VALIDATOR)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument("--compare", type=pathlib.Path)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest(args.validator)
    v = load(args.validator, "cro_survey_validator")
    text = report(*survey(v, ROOT))
    if args.compare is not None:
        differences = compare(args.compare.read_text(encoding="utf-8"), text)
        text += "".join(f"compare {d}\n" for d in differences)
        text += f"compare with {args.compare.as_posix()}: {len(differences)} difference(s)\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if args.compare is not None and differences else 0


if __name__ == "__main__":
    sys.exit(main())
