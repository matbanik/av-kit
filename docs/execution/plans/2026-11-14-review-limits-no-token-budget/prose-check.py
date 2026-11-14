"""Review-limits prose check (task rows 5 to 7; implementation-plan.md §Prose inventory, AC-14, AC-15).

Usage::

    python prose-check.py --rows P1-P22 [--begin-examples] [--agents-size] [--templates]
    python prose-check.py --selftest

``INVENTORY`` is the plan's prose table as data: for each row, the file, the phrase that is
there today and the phrase that replaces it. A row passes when none of its old phrases is left
in the file (outside the new phrases, which can contain an old one, as P21 does), every new
phrase is present, and every new phrase names ``.agent/review-limits.json`` or
``review_limits``. Every file the check reads must still be CRLF throughout.

``--begin-examples`` checks the four ``begin`` examples: after the marker that opens each
example, the limits sentence follows within ``BEGIN_WINDOW`` lines, and ``--ac-file`` appears
between them, so a plan's ``review_limits`` block is read at all.

``--agents-size`` checks ``AGENTS.md`` has at most 126 lines and fewer than 20,000 bytes.

``--templates`` checks AC-15: both templates say ``template_version: "2.3"`` and hold the
commented block in their frontmatter, no template line is a live ``review_limits:`` key, the
task template's ``{configured-cap}`` note names ``review_ledger.py state``, and
``create-plan.md`` §4 has the "Review limits" paragraph without the run-parameters path.

Exit 0 when every check passes, 1 otherwise. Run from the repository root.
"""

from __future__ import annotations

import pathlib
import re
import sys
import tempfile

NAMES = (".agent/review-limits.json", "review_limits")

CP = ".agent/workflows/create-plan.md"
DPC = ".agent/workflows/delegated-plan-creation.md"
ES = ".agent/workflows/execution-session.md"
VR = ".agent/workflows/validation-review.md"
DL = ".agent/docs/development-lifecycle.md"
ILG = ".agent/docs/issue-lifecycle-guide.md"
MR = ".agent/docs/model-routing.md"
SKILL = ".agent/skills/cli-dispatch/SKILL.md"
PLAN_TEMPLATE = "docs/execution/plans/PLAN-TEMPLATE.md"
TASK_TEMPLATE = "docs/execution/plans/TASK-TEMPLATE.md"

#: (row, file, old phrases, new phrases). The wording follows upstream 6dd76b7 where it has the line.
INVENTORY: tuple[tuple[str, str, tuple[str, ...], tuple[str, ...]], ...] = (
    (
        "P1",
        CP,
        ("Plan review round cap: 3 rounds.** If the review loop reaches 3 rounds",),
        (
            "Plan review round cap: the plan loop's round budget** (`review_limits.plan_rounds`, else "
            "`rounds.plan` in `.agent/review-limits.json`; default 3; `review_ledger.py state` prints it).",
        ),
    ),
    (
        "P2",
        CP,
        ("Plan review reached 3 rounds without approval.",),
        ("Plan review reached its round cap ({N} rounds; review_limits or .agent/review-limits.json) without approval.",),
    ),
    (
        "P3",
        CP,
        ("Round cap reached (3 rounds)",),
        ("Round cap reached (the plan loop's, from `review_limits` or `.agent/review-limits.json`; default 3)",),
    ),
    (
        "P4",
        CP,
        ("round cap (6)",),
        ("round cap (the execution loop's, from `review_limits` or `.agent/review-limits.json`; default 6)",),
    ),
    (
        "P5",
        CP,
        ("**Round cap: 6 rounds**",),
        (
            "**Round cap: the execution loop's round budget** (`review_limits.execution_rounds`, else "
            "`rounds.execution` in `.agent/review-limits.json`; default 6, plus any `continue` grant; "
            "`review_ledger.py state --loop-id exec-<slug>` prints it)",
        ),
    ),
    (
        "P6",
        DPC,
        ("round cap (3)",),
        ("the plan loop's round cap (default 3; from review_limits or .agent/review-limits.json)",),
    ),
    (
        "P7",
        DPC,
        ("`--review-mode plan` is what sets the cap of 3",),
        (
            "`begin` sets the cap referenced in 5c: the plan's `review_limits` block (read from "
            "`--ac-file`), else `rounds.plan` in `.agent/review-limits.json`, else the ledger's constant of 3.",
        ),
    ),
    (
        "P8",
        DPC,
        ("`--review-mode plan` is 3 rounds",),
        (
            "`--review-mode plan` is set at `begin` (`review_limits.plan_rounds`, else `rounds.plan` in "
            "`.agent/review-limits.json`; default 3)",
        ),
    ),
    (
        "P9",
        DPC,
        ("If 3 rounds without approval",),
        ("If the plan loop reaches its round cap (from `review_limits` or `.agent/review-limits.json`; default 3) without approval",),
    ),
    (
        "P10",
        ES,
        ("the 3-round cap",),
        ("the plan loop's round cap — `review_limits.plan_rounds`, else `.agent/review-limits.json`; default 3 —",),
    ),
    (
        "P11",
        ES,
        ("(`ROUND_BUDGETS`, execution = 6), token budget (`TOKEN_BUDGETS`)",),
        (
            "(the loop's, set at `begin` from the plan's `review_limits` block or `.agent/review-limits.json`; "
            "execution default 6), token budget (only when the loop has one; `.agent/review-limits.json` sets it off)",
        ),
    ),
    ("P12", DL, ("(≤3 rounds)",), ("(≤ plan round cap,<br/>.agent/review-limits.json)",)),
    ("P13", DL, ("(≤6 rounds)",), ("(≤ execution round cap,<br/>.agent/review-limits.json)",)),
    (
        "P14",
        DL,
        ("(max 3 rounds before T2 escalation)",),
        (
            "(up to the plan loop's round cap before T2 escalation: `review_limits.plan_rounds`, else "
            "`rounds.plan` in `.agent/review-limits.json`; default 3)",
        ),
    ),
    (
        "P15",
        DL,
        ("3 non-approved rounds → T2 escalation",),
        ("the plan round cap of non-approved rounds (`review_limits` or `.agent/review-limits.json`; default 3) → T2 escalation",),
    ),
    (
        "P16",
        DL,
        ("(max 6 rounds before T2 escalation)", "6 non-approved rounds → T2 escalation", "7th autonomous round"),
        (
            "(up to the execution loop's round cap before T2 escalation: `review_limits.execution_rounds`, else "
            "`rounds.execution` in `.agent/review-limits.json`; default 6)",
            "the execution round cap of non-approved rounds (`review_limits` or `.agent/review-limits.json`; default 6) → T2 escalation",
            "A round past the execution round cap (`.agent/review-limits.json`)",
        ),
    ),
    (
        "P17",
        DL,
        ("→ ≤3 rounds, agent loops", "→ ≤6 rounds, agent loops"),
        (
            "→ up to the plan round cap (.agent/review-limits.json), agent loops",
            "→ up to the execution round cap (.agent/review-limits.json), agent loops",
        ),
    ),
    (
        "P18",
        ILG,
        ("a 6-round cap",),
        ("the execution loop's round cap (`review_limits` or `.agent/review-limits.json`; default 6)",),
    ),
    (
        "P19",
        SKILL,
        ("capped at 3 rounds",),
        (
            "capped at the plan loop's round budget (`review_limits.plan_rounds`, else `rounds.plan` in "
            "`.agent/review-limits.json`; default 3; `review_ledger.py state` prints it)",
        ),
    ),
    (
        "P20",
        "AGENTS.md",
        ("Initial ledger caps: plan 3, execution 6;",),
        ("Initial ledger caps come from .agent/review-limits.json (plan 3, execution 6; token budgets off);",),
    ),
    (
        "P21",
        "PROJECT-PROFILE.md",
        ("plan: 3 · execution: 6",),
        ("plan: 3 · execution: 6 · token budgets: off (.agent/review-limits.json)",),
    ),
    (
        "P22",
        MR,
        ("(plan 3, execution 6)",),
        ("(caps from `.agent/review-limits.json`: plan 3, execution 6; token budgets off)",),
    ),
)

#: (file, marker that opens the example, the limits sentence that must follow it).
BEGIN_EXAMPLES: tuple[tuple[str, str, str], ...] = (
    (DPC, '$LOOP_ID = "planreview-', INVENTORY[6][3][0]),
    (
        ES,
        "review_ledger.py begin --loop-id exec-<plan-slug>",
        "`begin` sets the loop's limits from `.agent/review-limits.json` (the ledger's constants when it is "
        "absent), then the plan's `review_limits` block, read from `--ac-file`, and prints their source; "
        "`--round-budget` and `--token-budget N|off` may only tighten them.",
    ),
    (
        VR,
        '$LOOP_ID = "validation-',
        "Round and token limits come from `.agent/review-limits.json` (the ledger's constants when it is "
        "absent), then from a `review_limits` block in the `--ac-file` frontmatter; `begin` prints their source.",
    ),
    (
        SKILL,
        "export RECEIPTS_DIR=/absolute/path/outside/the/repo",
        "`begin` takes the loop's round and token limits from `.agent/review-limits.json` (the ledger's "
        "constants when it is absent), then from the plan's `review_limits` block in the `--ac-file`, then "
        "from `--round-budget` and `--token-budget N|off`, which may only tighten; it prints their source.",
    ),
)
BEGIN_WINDOW = 16

TEMPLATE_BLOCK = (
    "# review_limits:            # optional (v2.3): equal in plan and task; absent = .agent/review-limits.json",
    "#   schema: review-limits/1",
    "#   plan_rounds: 3          # integer >= 1, at most rounds.plan",
    "#   execution_rounds: 6     # integer >= 1, at most rounds.execution",
    "#   plan_tokens: off        # integer >= 1 or off; a number tightens off",
    "#   execution_tokens: off",
    "#   basis: tightened        # repo (every value equal) | tightened (none looser)",
)
LIVE_KEY = re.compile(r"^\s*review_limits\s*:")
REVIEW_LIMITS_PARAGRAPH = "**Review limits.**"
AGENTS_MAX_LINES = 126
AGENTS_MAX_BYTES = 20_000


def read_crlf(root: pathlib.Path, rel: str, problems: list[str]) -> str:
    raw = (root / rel).read_bytes()
    bare = raw.count(b"\n") - raw.count(b"\r\n")
    if bare:
        problems.append(f"{rel}: {bare} line(s) end in a bare LF; the file must stay CRLF")
    return raw.decode("utf-8").replace("\r\n", "\n")


def names_source(text: str) -> bool:
    return any(name in text for name in NAMES)


def row_ids(spec: str) -> list[str]:
    match = re.fullmatch(r"P(\d+)-P(\d+)", spec)
    if not match:
        raise SystemExit(f"--rows takes P<a>-P<b>, not {spec!r}")
    first, last = int(match.group(1)), int(match.group(2))
    known = {row[0] for row in INVENTORY}
    wanted = [f"P{n}" for n in range(first, last + 1)]
    missing = [w for w in wanted if w not in known]
    if missing:
        raise SystemExit(f"--rows names rows the inventory lacks: {missing}")
    return wanted


def check_rows(root: pathlib.Path, wanted: list[str]) -> list[str]:
    problems: list[str] = []
    texts: dict[str, str] = {}
    for row, rel, olds, news in INVENTORY:
        if row not in wanted:
            continue
        if rel not in texts:
            texts[rel] = read_crlf(root, rel, problems)
        text = texts[rel]
        rest = text
        for new in news:
            if not names_source(new):
                problems.append(f"{row} {rel}: the new phrase names neither {NAMES}: {new!r}")
            if new not in text:
                problems.append(f"{row} {rel}: new phrase missing: {new!r}")
            rest = rest.replace(new, "")
        for old in olds:
            if old in rest:
                line = next(n for n, ln in enumerate(text.split("\n"), 1) if old in ln)
                problems.append(f"{row} {rel}:{line}: old phrase still there: {old!r}")
        if not any(p.startswith(f"{row} ") for p in problems):
            print(f"ok   {row} {rel}")
    return problems


def check_begin(root: pathlib.Path) -> list[str]:
    problems: list[str] = []
    for rel, marker, sentence in BEGIN_EXAMPLES:
        lines = read_crlf(root, rel, problems).split("\n")
        if not names_source(sentence):
            problems.append(f"begin {rel}: the sentence names neither {NAMES}")
        starts = [n for n, ln in enumerate(lines) if marker in ln]
        if len(starts) != 1:
            problems.append(f"begin {rel}: marker {marker!r} found {len(starts)} times, expected once")
            continue
        start = starts[0]
        window = lines[start : start + BEGIN_WINDOW + 1]
        hits = [n for n, ln in enumerate(window) if sentence in ln]
        if not hits:
            problems.append(f"begin {rel}:{start + 1}: the limits sentence is not within {BEGIN_WINDOW} lines of the example")
            continue
        if not any("--ac-file" in ln for ln in window[: hits[0]]):
            problems.append(f"begin {rel}:{start + 1}: the example does not pass --ac-file")
            continue
        print(f"ok   begin {rel}:{start + 1}")
    return problems


def check_agents(root: pathlib.Path) -> list[str]:
    raw = (root / "AGENTS.md").read_bytes()
    lines = raw.count(b"\n") + (0 if raw.endswith(b"\n") or not raw else 1)
    problems = []
    if lines > AGENTS_MAX_LINES:
        problems.append(f"AGENTS.md has {lines} lines; at most {AGENTS_MAX_LINES}")
    if len(raw) >= AGENTS_MAX_BYTES:
        problems.append(f"AGENTS.md has {len(raw)} bytes; fewer than {AGENTS_MAX_BYTES} required")
    if not problems:
        print(f"ok   AGENTS.md {lines} lines, {len(raw)} bytes")
    return problems


def frontmatter(text: str) -> list[str]:
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        return []
    try:
        end = lines.index("---", 1)
    except ValueError:
        return []
    return lines[1:end]


def check_templates(root: pathlib.Path) -> list[str]:
    problems: list[str] = []
    for rel in (PLAN_TEMPLATE, TASK_TEMPLATE):
        text = read_crlf(root, rel, problems)
        head = frontmatter(text)
        if 'template_version: "2.3"' not in head:
            problems.append(f'{rel}: frontmatter lacks template_version: "2.3"')
        joined = "\n".join(head)
        if "\n".join(TEMPLATE_BLOCK) not in joined:
            problems.append(f"{rel}: frontmatter lacks the commented review_limits block")
        live = [n for n, ln in enumerate(text.split("\n"), 1) if LIVE_KEY.match(ln)]
        if live:
            problems.append(f"{rel}: live review_limits key at line(s) {live}; the block must stay commented")
    task = read_crlf(root, TASK_TEMPLATE, problems)
    if not any("{configured-cap}" in ln and "review_ledger.py state" in ln for ln in task.split("\n")):
        problems.append(f"{TASK_TEMPLATE}: no {{configured-cap}} note naming review_ledger.py state")
    plan = read_crlf(root, CP, problems)
    section = re.search(r"^### 4\. Generate Plan\n(.*?)^### 4A\.", plan, re.S | re.M)
    if not section:
        problems.append(f"{CP}: §4 not found")
    else:
        body = section.group(1)
        para = next((p for p in body.split("\n\n") if REVIEW_LIMITS_PARAGRAPH in p), None)
        if para is None:
            problems.append(f"{CP} §4: no {REVIEW_LIMITS_PARAGRAPH} paragraph")
        else:
            if ".agent/review-limits.json" not in para or "continue" not in para:
                problems.append(f"{CP} §4: the paragraph must name .agent/review-limits.json and continue")
            if "run-parameters" in para or "run_parameters" in para:
                problems.append(f"{CP} §4: the paragraph names the run-parameters path (D-733)")
    if not problems:
        print("ok   templates v2.3, commented block, cap note, create-plan §4 paragraph")
    return problems


def selftest() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)

        def put(rel: str, text: str, crlf: bool = True) -> None:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))

        new19 = INVENTORY[18][3][0]
        put(SKILL, f"- **Round-cap behavior**: The loop is {new19}.\n")
        if check_rows(root, ["P19"]):
            failures.append("control: the rewritten P19 line was refused")
        put(SKILL, "- **Round-cap behavior**: The plan review correction loop is capped at 3 rounds.\n")
        if not any("old phrase still there" in p for p in check_rows(root, ["P19"])):
            failures.append("a line 'capped at 3 rounds' was accepted")
        put(SKILL, f"- **Round-cap behavior**: The loop is {new19}.\n", crlf=False)
        if not any("bare LF" in p for p in check_rows(root, ["P19"])):
            failures.append("an LF copy of a CRLF file was accepted")
        put("PROJECT-PROFILE.md", f"| Round caps (B5) | {INVENTORY[20][3][0]} |\n")
        if check_rows(root, ["P21"]):
            failures.append("control: P21's new phrase, which contains the old one, was refused")

        put("AGENTS.md", "x\n" * AGENTS_MAX_LINES)
        if check_agents(root):
            failures.append(f"control: an AGENTS.md of {AGENTS_MAX_LINES} lines was refused")
        put("AGENTS.md", "x\n" * (AGENTS_MAX_LINES + 1))
        if not check_agents(root):
            failures.append(f"an AGENTS.md of {AGENTS_MAX_LINES + 1} lines was accepted")

        rel, marker, sentence = BEGIN_EXAMPLES[2]
        put(rel, f"   {marker}x\"\n   begin `\n     --ac-file p.md\n   ```\n   {sentence}\n")
        if check_begin_one(root, 2):
            failures.append("control: a begin example with --ac-file and the sentence was refused")
        put(rel, f"   {marker}x\"\n   begin `\n   ```\n   {sentence}\n")
        if not check_begin_one(root, 2):
            failures.append("a begin example without --ac-file was accepted")

        good_head = ["---", 'template_version: "2.3"', *TEMPLATE_BLOCK, "---", ""]
        put(PLAN_TEMPLATE, "\n".join(good_head))
        put(TASK_TEMPLATE, "\n".join(good_head) + "\n> `{configured-cap}`: copy it from `review_ledger.py state --loop-id <loop>`.\n")
        put(CP, "### 4. Generate Plan\n\n**Review limits.** From `.agent/review-limits.json`; more rounds come from `continue`.\n\n### 4A. x\n")
        if check_templates(root):
            failures.append("control: good templates were refused")
        live = ["---", 'template_version: "2.3"', *TEMPLATE_BLOCK, "review_limits:", "---", ""]
        put(PLAN_TEMPLATE, "\n".join(live))
        if not any("live review_limits key" in p for p in check_templates(root)):
            failures.append("a template with an uncommented review_limits: line was accepted")
    for failure in failures:
        print("SELFTEST FAIL:", failure)
    print(f"prose-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def check_begin_one(root: pathlib.Path, index: int) -> list[str]:
    global BEGIN_EXAMPLES
    saved = BEGIN_EXAMPLES
    BEGIN_EXAMPLES = (saved[index],)
    try:
        return check_begin(root)
    finally:
        BEGIN_EXAMPLES = saved


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    root = pathlib.Path.cwd()
    problems: list[str] = []
    if "--rows" in argv:
        problems += check_rows(root, row_ids(argv[argv.index("--rows") + 1]))
    if "--begin-examples" in argv:
        problems += check_begin(root)
    if "--agents-size" in argv:
        problems += check_agents(root)
    if "--templates" in argv:
        problems += check_templates(root)
    for problem in problems:
        print("FAIL", problem)
    print(f"prose-check: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
