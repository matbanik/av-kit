"""Session 84 old-reflections check (plan §Verification Plan 5; task rows 0 and 8; AC-13).

Usage::

    python reflections-check.py --before BASE_VALIDATOR [--after VALIDATOR] [--out RECEIPT]
    python reflections-check.py --selftest

Runs ``check_reflection`` from two copies of the closeout validator over every
``docs/execution/reflections/*.md`` except ``TEMPLATE.md``, each with
``docs/execution/reflections/TEMPLATE.md`` and ``.agent/schemas/reflection.v1.yaml`` and no
decision source (``REFLECTION_SET`` in the plan). ``BASE_VALIDATOR`` is row 0's copy of the
validator as it stood before the port; ``--after`` defaults to the working file.

It refuses (exit 1) when any reflection that the base copy accepts is refused by the after
copy, or when the after copy refuses any reflection for holding the template example. A
reflection refused by both is listed as ``both-refuse`` and does not fail the run: the port
cannot have caused it.

When the after copy has no template-example check yet (plan time, before row 4), the run
adds upstream ``a73d6df``'s check in-script (``simulated_example_check``), so the plan-time
receipt predicts the port. Read-only: it imports both copies and writes only RECEIPT
(default ``C:/Temp/av-kit/cro/reflections-check.txt``). ``--selftest`` exits 1 unless the
classifier flags an OK-to-REFUSE pair and a template-example refusal, passes the other
pairs, and the simulated check refuses a planted example line and accepts a link list.
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))  # the validator imports durable_evidence from there
DEFAULT_AFTER = ROOT / "tools" / "validate_closeout_artifacts.py"
DEFAULT_OUT = pathlib.Path("C:/Temp/av-kit/cro/reflections-check.txt")
REFLECTIONS = ROOT / "docs" / "execution" / "reflections"
TEMPLATE = REFLECTIONS / "TEMPLATE.md"
SCHEMA = ROOT / ".agent" / "schemas" / "reflection.v1.yaml"
EXAMPLE_REFUSAL = "template example"
LOG = re.compile(r"^### Decisions Log\n(?P<body>.*?)(?=^##+ |\Z)", re.MULTILINE | re.DOTALL)


def load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def simulated_example_check(text: str) -> str | None:
    """upstream a73d6df: a ``_{`` in the Decisions Log body is the template example."""
    log = LOG.search(text)
    if log is not None and "_{" in log.group("body"):
        return "Decisions Log still holds the template example (simulated)"
    return None


def outcome(v, text: str, path: str, simulate: bool) -> str:
    try:
        v.check_reflection(text, path, str(TEMPLATE), str(SCHEMA))
    except v.Refuse as exc:
        return "REFUSE " + str(exc).splitlines()[0][:200]
    if simulate:
        refusal = simulated_example_check(text)
        if refusal:
            return "REFUSE " + refusal
    return "OK"


def classify(before: str, after: str) -> str:
    if EXAMPLE_REFUSAL in after:
        return "example-refused"
    if before == "OK" and after != "OK":
        return "newly-refused"
    if before != "OK" and after != "OK":
        return "both-refuse"
    return "ok"


def run(before_path: pathlib.Path, after_path: pathlib.Path) -> tuple[list[str], int]:
    before = load(before_path, "cro_reflections_before")
    after = load(after_path, "cro_reflections_after")
    simulate = "template example" not in inspect.getsource(after.check_reflection)
    lines = [f"reflections-check mode: {'simulated example check' if simulate else 'live'}"]
    counts: dict[str, int] = {}
    for path in sorted(REFLECTIONS.glob("*.md")):
        if path.name == "TEMPLATE.md":
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        b, a = outcome(before, text, rel, False), outcome(after, text, rel, simulate)
        kind = classify(b, a)
        counts[kind] = counts.get(kind, 0) + 1
        if kind != "ok":
            lines.append(f"{kind} {rel}: before={b[:120]} | after={a[:120]}")
    bad = counts.get("newly-refused", 0) + counts.get("example-refused", 0)
    lines.append(
        "reflections: "
        + str(sum(counts.values()))
        + "; "
        + ", ".join(f"{k} {n}" for k, n in sorted(counts.items()))
    )
    lines.append(f"reflections-check: {bad} regression(s)")
    return lines, bad


def selftest() -> int:
    failures = []
    cases = [
        (("OK", "REFUSE x"), "newly-refused"),
        (("OK", "REFUSE reflection r Decisions Log still holds the template example"), "example-refused"),
        (("REFUSE a", "REFUSE a"), "both-refuse"),
        (("OK", "OK"), "ok"),
        (("REFUSE a", "OK"), "ok"),
    ]
    for (b, a), want in cases:
        if classify(b, a) != want:
            failures.append(f"classify({b!r}, {a!r}) != {want}")
    head = "# r\n\n### Decisions Log\n\n"
    tail = "\n## Pattern Extraction\n\n_{not in the log}_\n"
    example = head + "- _{the choice in plain words}_ — [D-1](_{path to the stage log}_)\n" + tail
    links = head + "- Kept the cap at 6 — [D-1](plan.md)\n" + tail
    none = head + "None.\n" + tail
    if simulated_example_check(example) is None:
        failures.append("the planted example line was not refused")
    for name, text in (("link list", links), ("None.", none)):
        if simulated_example_check(text) is not None:
            failures.append(f"the {name} Decisions Log was refused")
    for f in failures:
        print(f"FAIL {f}")
    print(f"reflections-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--before", type=pathlib.Path)
    parser.add_argument("--after", type=pathlib.Path, default=DEFAULT_AFTER)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.before is None:
        parser.error("--before is required")
    lines, bad = run(args.before, args.after)
    text = "\n".join(lines) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
