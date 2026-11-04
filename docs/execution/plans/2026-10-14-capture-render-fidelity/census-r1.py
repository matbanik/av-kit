"""Session 36 round-1 correction census (plan-corrections Step 5c; plan-critical-review PR-6).

Sweeps every old and new value the round-1 corrections touched across the plan and
``task.md``, one raw receipt per variant (``rtk proxy rg -F -n``, untruncated, exit 0 = hits,
1 = none, >1 = error), and assigns each hit a disposition, ``updated`` or
``confirmed-consistent``, from ``RULES``. A rule matches by variant and a content anchor
taken from the hit line, never by line number, so it survives edits elsewhere; the table
it renders carries the live ``file:line``.

Usage, from the worktree root:

* ``python census-r1.py --write`` -- run the sweep, then rewrite the disposition table
  between the ``census-table`` markers in ``implementation-plan.md``, repeating until the
  line numbers are stable;
* ``python census-r1.py --check`` -- run the sweep and exit 1 unless every hit has exactly
  one rule, every rule matched a hit, and the plan's table equals the rendered one.

Receipts: ``C:/Temp/av-kit/census-s36r2-<id>.txt`` (the round-1 ``census-s36r1-*`` receipts
are left as they were). The table text holds no search term, so it never hits itself.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

PLAN_DIR = "docs/execution/plans/2026-10-14-capture-render-fidelity"
PLAN = f"{PLAN_DIR}/implementation-plan.md"
TASK = f"{PLAN_DIR}/task.md"
RECEIPT = "C:/Temp/av-kit/census-s36r2-{}.txt"
START = "<!-- census-table:start -->"
END = "<!-- census-table:end -->"

#: id -> (term, value changed). ``old-*`` must be gone or explained; ``new-*`` are the edits.
VARIANTS = {
    "old-grown": ("grown by 1", "tip oracle halo"),
    "old-pad2": ("stroke/2 + 2", "tile padding"),
    "old-tipcol": ("tip column", "clipped-tip probe"),
    "old-factor5": ("factor 5", "ARROW_HEAD restatement"),
    "old-angle": ("0.45", "ARROW_HEAD restatement"),
    "old-codepath": ("code-path", "identity scope"),
    "old-exactwhite": ("exact white", "tip oracle halo"),
    "old-halfpx": ("x + 0.5", "coordinate convention"),
    "old-11ids": ("11 ids", "gate order"),
    "old-rendercheck": ("(render and check)", "admin inventory"),
    "new-pad4": ("stroke/2 + 4", "tile padding"),
    "new-halo": ("AA_HALO_PX", "tip oracle halo"),
    "new-centre": ("PIXEL_CENTRE", "coordinate convention"),
    "new-identity": ("INPUT_IDENTITY", "identity scope"),
    "new-redproof": ("RED_PROOF", "Red proof"),
    "new-exit": (".txt.exit", "Red proof"),
    "new-notrun": ("not_run", "gate order"),
    "new-issuerender": ("issue_triage.py render", "admin inventory"),
}

U, C = "updated", "confirmed-consistent"
#: (variant, file, content anchor in the hit line, disposition, reason)
RULES = (
    ("old-tipcol", PLAN, "| AC-83.7 |", C, "AC-83.7 says the apex column is *not* asserted and why (F1)"),
    ("old-angle", PLAN, "| `ARROW_HEAD` |", C, "the one canonical `ARROW_HEAD` definition (F6 keeps it)"),
    ("old-angle", PLAN, "| `SHAFT_INSIDE_HEAD` |", C, "the derivation needs the numeric angle; it cites `ARROW_HEAD` values, not a second definition"),
    ("old-exactwhite", PLAN, "The round-1 counts", C, "R-3 describes the round-1 reviewer's method"),
    ("old-halfpx", PLAN, "| `PIXEL_CENTRE` |", C, "the convention names the rejected offset"),
    ("old-halfpx", PLAN, "The round-1 counts", C, "R-3 describes the round-1 reviewer's method"),
    ("new-pad4", PLAN, "| `BAKE_AA` |", U, "F1: tile padding widened"),
    ("new-pad4", PLAN, "| F1 (High)", C, "correction log row"),
    ("new-halo", PLAN, "| `AA_LIMITS` |", U, "F1: new halo constant"),
    ("new-halo", PLAN, "| `ARROW_TIP_ORACLE` |", U, "F1: oracle uses the halo"),
    ("new-halo", PLAN, "The round-1 counts", U, "F1: R-3 cites the halo sensitivity"),
    ("new-centre", PLAN, "| `BAKE_AA` |", U, "F1: bake states the convention"),
    ("new-centre", PLAN, "| `PIXEL_CENTRE` |", U, "F1: new convention row"),
    ("new-centre", PLAN, "| `ARROW_TIP_ORACLE` |", U, "F1: oracle measures at pixel centre"),
    ("new-centre", PLAN, "| `EDGE_ORACLE` |", U, "F1: oracle measures at pixel centre"),
    ("new-centre", PLAN, "| F1 (High)", C, "correction log row"),
    ("new-identity", TASK, "| H1-6b |", U, "F2: H1-6b re-derives the identity live"),
    ("new-identity", PLAN, "1. `identity-before`", U, "F2/F4: gate step list"),
    ("new-identity", PLAN, "- **Input identity", U, "F2: identity contract rewritten"),
    ("new-identity", PLAN, "| F2 (High)", C, "correction log row"),
    ("new-redproof", PLAN, "`RED_PROOF`: [red-check.py]", U, "F3: Red proof paragraph"),
    ("new-redproof", PLAN, "| S3 |", U, "F3: stop condition cites the Red proof"),
    ("new-redproof", PLAN, "| F3 (Medium)", C, "correction log row"),
    ("new-exit", TASK, "| 2 |", U, "F3: Red row 2 keeps child exits"),
    ("new-exit", TASK, "| 4 |", U, "F3: Red row 4 keeps child exits"),
    ("new-exit", TASK, "| 6 |", U, "F3: Red row 6 keeps child exits"),
    ("new-notrun", TASK, "| 8 |", U, "F4: gate row reports later steps"),
    ("new-notrun", TASK, "| H1-2 |", U, "F4: gate rerun reports later steps"),
    ("new-notrun", PLAN, "The plan-local [session-gate.ps1]", U, "F4: gate section"),
    ("new-notrun", PLAN, "| F4 (Medium)", C, "correction log row"),
    ("new-issuerender", TASK, "| H2-2 |", U, "F5: H2-2 checks the rendered issues file"),
    ("new-issuerender", PLAN, "| `.agent/context/known-issues.md` |", U, "F5: new Files Modified row"),
    ("new-issuerender", PLAN, "| F5 (Low)", C, "correction log row"),
)

HIT = re.compile(r"^(?P<path>[^\s:][^:]*\.md):(?P<line>\d+):(?P<text>.*)$")


def sweep() -> list[tuple[str, str, int, str]]:
    hits = []
    for vid, (term, _) in VARIANTS.items():
        proc = subprocess.run(
            ["rtk", "proxy", "rg", "-F", "-n", term, PLAN, TASK], capture_output=True, text=True, encoding="utf-8"
        )
        pathlib.Path(RECEIPT.format(vid)).write_text(proc.stdout + proc.stderr, encoding="utf-8")
        if proc.returncode > 1:
            raise SystemExit(f"rg error on {vid}: exit {proc.returncode}")
        for raw in proc.stdout.splitlines():
            m = HIT.match(raw)
            if m:
                hits.append((vid, m["path"], int(m["line"]), m["text"]))
    # rg searches the two files in parallel, so its output order varies between runs.
    order = list(VARIANTS)
    return sorted(hits, key=lambda h: (order.index(h[0]), h[1], h[2]))


def dispositions(hits):
    rows, problems, used = [], [], set()
    for vid, path, line, text in hits:
        match = [i for i, r in enumerate(RULES) if r[0] == vid and r[1] == path and r[2] in text]
        if len(match) != 1:
            problems.append(f"{vid} {path}:{line}: {len(match)} rule(s) match")
            continue
        used.add(match[0])
        _, _, _, disp, reason = RULES[match[0]]
        rows.append((vid, path, line, disp, reason))
    problems += [f"rule never matched: {RULES[i][:3]}" for i in range(len(RULES)) if i not in used]
    return rows, problems


def render(rows) -> str:
    updated = sum(r[3] == U for r in rows)
    zero = [v for v in VARIANTS if not any(r[0] == v for r in rows)]
    changed = len({value for _, value in VARIANTS.values()})
    out = [
        START,
        f"Blast-radius census: {changed} values changed, {len(VARIANTS)} variants swept, {len(rows)} sites found, "
        f"{updated} updated, {len(rows) - updated} confirmed consistent. Variants with no hit: "
        + ", ".join(f"`{v}`" for v in zero)
        + ".",
        "",
        "| Variant | Value | Hit | Disposition | Reason |",
        "|---|---|---|---|---|",
    ]
    for vid, path, line, disp, reason in rows:
        short = pathlib.PurePosixPath(path).name
        out.append(f"| `{vid}` | {VARIANTS[vid][1]} | `{short}:{line}` | {disp} | {reason} |")
    out.append(END)
    return "\n".join(out)


def current_table(text: str) -> str:
    a, b = text.index(START), text.index(END) + len(END)
    return text[a:b]


def main(argv: list[str]) -> int:
    plan = pathlib.Path(PLAN)
    if argv == ["--write"]:
        for _ in range(4):
            rows, problems = dispositions(sweep())
            if problems:
                print("\n".join(problems))
                return 1
            text = plan.read_text(encoding="utf-8")
            table = render(rows)
            if current_table(text) == table:
                print(f"census-r1: table stable, {len(rows)} hit(s)")
                return 0
            plan.write_text(text.replace(current_table(text), table), encoding="utf-8")
        print("census-r1: table did not stabilise")
        return 1
    if argv == ["--check"]:
        rows, problems = dispositions(sweep())
        if current_table(plan.read_text(encoding="utf-8")) != render(rows):
            problems.append("the plan's census table differs from the receipts")
        for p in problems:
            print("CENSUS:", p)
        print(f"census-r1 check: {len(rows)} hit(s), {len(problems)} problem(s)")
        return 1 if problems else 0
    print("usage: census-r1.py --write | --check")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
