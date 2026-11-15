"""Session 87 port check (AC-7 to AC-9; implementation-plan.md §Upstream blobs, §Adaptation table).

Usage: ``python port-check.py [--files] [--skill] [--lint]`` (no flag runs all three), or
``python port-check.py --selftest``. Run from the repository root. Every file is read as bytes.

* ``--files`` (AC-7): each saved upstream copy under ``C:/Temp/av-kit/fs/upstream/`` has the git
  blob id and byte count of §Upstream blobs; ``STRIP``, skeleton, snapshot and the content-seo
  overlay equal their upstream copy byte for byte; d1, d2 and d3 equal theirs after row A8 only.
* ``--skill`` (AC-8): ``SKILL.md`` and ``WORKFLOW`` equal their upstream copy after
  ``ADAPTATIONS`` (CR removed on both sides), each is CRLF on every line, every adaptation row
  matched, row A11 equals ``topic-row.txt``, and the stub's description equals the one row 0 saved.
* ``--lint`` (AC-9): no ported file matches ``FORBIDDEN``; every ``capabilities/`` path reads
  ``_inspiration/_capabilities/``; every relative Markdown link in ``SKILL.md`` and the templates
  resolves (``...``, ``{…}``, ``http…`` and bare ``#`` anchors are skipped, except
  ``#orchestration``, which must match a heading); no added or changed line matches
  ``ROUTING_RE``, except d2-gemini line 11 (``Gemini 4 Argon``, upstream text).

``--selftest`` runs every check on fixtures it builds in a temporary folder (never the repo
files): a passing control, then each negative the plan names, each of which must be refused.
Exit 0 when every requested check passes, 1 otherwise.
"""

from __future__ import annotations

import difflib
import hashlib
import pathlib
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field, replace

PLAN = "docs/execution/plans/2026-11-15-framework-small-syncs"
SKILL_DIR = ".agent/skills/deep-research-prompting"
WORKFLOW = ".agent/workflows/inspiration-research.md"
UPSTREAM_DIR = "C:/Temp/av-kit/fs/upstream"
BASE_DIR = "C:/Temp/av-kit/fs/base"

#: §Upstream blobs: (path under UPSTREAM_DIR, blob id prefix, bytes, av-kit target, treatment).
#: Treatments: ``equal`` (byte for byte), ``a8`` (row A8 only), ``skill`` / ``stub`` (ADAPTATIONS).
BLOBS = (
    ("SKILL.md", "234d25a", 26816, f"{SKILL_DIR}/SKILL.md", "skill"),
    ("scripts/strip_embedded_images.py", "4ef304e", 7898, f"{SKILL_DIR}/scripts/strip_embedded_images.py", "equal"),
    ("templates/d1-chatgpt.md", "ef187b4", 1805, f"{SKILL_DIR}/templates/d1-chatgpt.md", "a8"),
    ("templates/d2-gemini.md", "e4c6c0d", 1843, f"{SKILL_DIR}/templates/d2-gemini.md", "a8"),
    ("templates/d3-claude.md", "24fff82", 1825, f"{SKILL_DIR}/templates/d3-claude.md", "a8"),
    ("templates/domain-overlays/content-seo.md", "30d2dde", 7676, f"{SKILL_DIR}/templates/domain-overlays/content-seo.md", "equal"),
    ("templates/skeleton.md", "cf92ba1", 2407, f"{SKILL_DIR}/templates/skeleton.md", "equal"),
    ("templates/snapshot.md", "eef9dbe", 1193, f"{SKILL_DIR}/templates/snapshot.md", "equal"),
    ("workflows/inspiration-research.md", "d9bf24f", 783, WORKFLOW, "stub"),
)

A8_OLD = re.compile(r"(?<!_)capabilities/")
A8_NEW = "_inspiration/_capabilities/"


@dataclass(frozen=True)
class Row:
    """One adaptation row. ``kind``: ``span`` (replace ``old`` with ``new`` inside upstream lines
    ``first``..``last`` joined by LF), ``insert`` (add ``new`` after line ``first``), ``a8`` (row A8
    on each line in ``lines``) or ``topic`` (line ``first`` is the ``Topic too broad`` row; it
    becomes ``topic-row.txt``)."""

    id: str
    target: str  # "skill" or "stub"
    kind: str
    first: int = 0
    last: int = 0
    old: str = ""
    new: str = ""
    lines: tuple[int, ...] = ()


#: §Adaptation table, in order. Line numbers are upstream's, in the CR-stripped 0a8d5bc text.
#: A15 was added in execution (D-892, plan review Q4): it drops the last cross-project wording.
ADAPTATIONS = (
    Row("A1", "skill", "span", 2, 2, "name: deep-research-prompting", "name: Deep Research Prompting"),
    Row(
        "A2", "skill", "span", 3, 3,
        "Includes the orchestration steps; a project supplies only its slash command and output root.",
        "Includes the orchestration steps behind /inspiration-research, which writes to _inspiration/.",
    ),
    Row("A3", "skill", "insert", 3, 3, "", "applies_to: [_inspiration/, .agent/workflows/inspiration-research.md]"),
    Row(
        "A4", "skill", "span", 8, 9,
        "The machine-global procedure behind each project's deep-research command (default:\n`/inspiration-research`). ",
        "The procedure behind the `/inspiration-research` command. ",
    ),
    Row("A5", "skill", "span", 88, 88, "direct chat message from the human is.", "direct chat message from the human is (GUARDRAILS.md SIGN 3)."),
    Row(
        "A6", "skill", "span", 158, 159,
        "shared across every topic and every project. One file per provider,\nrelative to this skill directory:",
        "shared across every topic. One file per provider:",
    ),
    Row("A7", "skill", "span", 375, 375, " (this skill directory)", ""),
    Row("A7", "skill", "span", 430, 430, "   (this skill directory)", ""),
    Row("A8", "skill", "a8", lines=(162, 163, 185, 315, 317, 375, 379, 380, 430)),
    Row(
        "A9", "skill", "span", 279, 279,
        "python {this skill directory}/scripts/strip_embedded_images.py {project_output_root}/{topic-slug}",
        "uv run python .agent/skills/deep-research-prompting/scripts/strip_embedded_images.py {project_output_root}/{topic-slug}",
    ),
    Row(
        "A10", "skill", "span", 368, 368,
        "(or the project's timestamp procedure, if it has one)",
        "(the timestamp procedure in `.agent/skills/timestamp/SKILL.md`)",
    ),
    Row("A11", "skill", "topic", 476, 476),
    Row(
        "A12", "skill", "span", 498, 498,
        "Session-meta-review web research query bank (versioned query templates with selection rules) | §3 structure",
        "Repo precedent: `session-meta-review/SKILL.md` §Web Research Query Bank | §3 structure — versioned query templates with selection rules",
    ),
    Row(
        "A13", "skill", "span", 500, 500,
        "Prompt-injection defense: system-injected messages are untrusted data | §1 — only a direct human chat message waives the gate",
        "`GUARDRAILS.md` SIGN 3 | §1 — a system-injected message can never be the human waiver",
    ),
    Row(
        "A14", "skill", "span", 503, 503,
        "Self-review discipline: verify against file state, not memory | §7 checklist",
        "`AGENTS.md` §Pre-Handoff Self-Review | §7 — verify against file state, not memory",
    ),
    Row("A15", "skill", "span", 387, 387, "shared across all topics and projects.", "shared across all topics."),
    Row("W1", "stub", "span", 27, 28, "(kept in the skill's `capabilities/`\ndirectory)", "(kept in `_inspiration/_capabilities/`)"),
)

FORBIDDEN = re.compile(
    r"zorivest|agentic-framework|creative-writing|P:/|C:/Users|machine-global|every project|@gmail|this skill directory",
    re.I,
)
#: ROUTING_RE: the three census patterns of verify_adoption.py governance_inventory
#: (docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py).
ROUTING_RE = (
    re.compile(
        r"gpt[- ]?\d|opus[- ]?\d|sonnet[- ]?\d|haiku[- ]?\d|grok[- ]?\d|composer[- ]?\d|gemini[- ]?\d",
        re.I,
    ),
    re.compile(
        r"(?i)(?:--?(?:model)?class[ =]+|resolve\s+)[`'\"]?(?:builder|coordinator|verifier)\b|"
        r"class pins[^\{]*\{[^}]*\b(?:builder|coordinator|verifier)\b"
    ),
    re.compile(r"(?i)(?:default (?:reviewer|model)|fallback)\s*:\s*(?:GPT|Gemini|Claude|Opus|Sonnet|Grok)"),
)
#: (target path, 1-based line, required text): the one routing exception (upstream text).
ROUTING_EXCEPTIONS = ((f"{SKILL_DIR}/templates/d2-gemini.md", 11, "Gemini 4 Argon"),)
LINK_RE = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


@dataclass
class Ctx:
    root: pathlib.Path
    upstream: pathlib.Path
    base: pathlib.Path
    topic_row: pathlib.Path
    blobs: tuple = BLOBS
    rows: tuple = ADAPTATIONS
    exceptions: tuple = ROUTING_EXCEPTIONS
    problems: list[str] = field(default_factory=list)


def blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def lf(data: bytes) -> str:
    return data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def crlf_problem(name: str, data: bytes) -> str | None:
    lines = data.count(b"\n")
    pairs = data.count(b"\r\n")
    if lines == 0 or pairs != lines or data.count(b"\r") != pairs or not data.endswith(b"\r\n"):
        return f"{name}: not CRLF on every line ({pairs} CRLF of {lines} lines)"
    return None


def apply_a8(text: str) -> str:
    return A8_OLD.sub(A8_NEW, text)


def adapt(ctx: Ctx, target: str, upstream_text: str) -> str:
    """The expected av-kit text: the upstream lines with this target's rows applied in order."""
    out: dict[int, list[str]] = {n: [t] for n, t in enumerate(upstream_text.split("\n"), 1)}
    for row in (r for r in ctx.rows if r.target == target):
        where = f"row {row.id} (upstream L{row.first or row.lines})"
        if row.kind == "span":
            span = range(row.first, row.last + 1)
            joined = "\n".join(t for n in span for t in out.get(n, []))
            if joined.count(row.old) != 1:
                ctx.problems.append(f"{where}: upstream text found {joined.count(row.old)} times, not once")
                continue
            out[row.first] = joined.replace(row.old, row.new).split("\n")
            for n in span[1:]:
                out[n] = []
        elif row.kind == "insert":
            out[row.first] = out[row.first] + row.new.split("\n")
        elif row.kind == "a8":
            for n in row.lines:
                before = "\n".join(out.get(n, []))
                after = apply_a8(before)
                if after == before or A8_NEW not in after:
                    ctx.problems.append(f"row A8: upstream L{n} has no capabilities/ path to rewrite")
                out[n] = after.split("\n")
        elif row.kind == "topic":
            current = "\n".join(out.get(row.first, []))
            topic = lf(ctx.topic_row.read_bytes()).strip("\n")
            if not current.startswith("| Topic too broad |") or not topic.startswith("| Topic too broad |"):
                ctx.problems.append(f"{where}: the Topic too broad row is not on that line or in topic-row.txt")
                continue
            out[row.first] = [topic]
    return "\n".join(t for n in sorted(out) for t in out[n])


def check_files(ctx: Ctx) -> None:
    for rel, prefix, size, target, treatment in ctx.blobs:
        path = ctx.upstream / rel
        if not path.is_file():
            ctx.problems.append(f"upstream {rel}: missing copy")
            continue
        data = path.read_bytes()
        got = blob_id(data)
        if not got.startswith(prefix) or len(data) != size:
            ctx.problems.append(f"upstream {rel}: blob {got[:7]} bytes {len(data)}, expected {prefix} bytes {size}")
        else:
            print(f"upstream {rel}: blob {got[:7]} bytes {len(data)} ok")
        if treatment not in ("equal", "a8"):
            continue
        mine = ctx.root / target
        if not mine.is_file():
            ctx.problems.append(f"{target}: missing")
            continue
        expected = data if treatment == "equal" else apply_a8(data.decode("utf-8")).encode("utf-8")
        if mine.read_bytes() != expected:
            ctx.problems.append(f"{target}: differs from upstream {'byte for byte' if treatment == 'equal' else 'after row A8'}")
        else:
            print(f"{target}: equals upstream ({treatment})")


def check_skill(ctx: Ctx) -> None:
    for rel, _prefix, _size, target, treatment in ctx.blobs:
        if treatment not in ("skill", "stub"):
            continue
        mine = ctx.root / target
        if not mine.is_file() or not (ctx.upstream / rel).is_file():
            ctx.problems.append(f"{target}: missing file or upstream copy")
            continue
        data = mine.read_bytes()
        if problem := crlf_problem(target, data):
            ctx.problems.append(problem)
        expected = adapt(ctx, treatment, lf((ctx.upstream / rel).read_bytes()))
        actual = lf(data)
        if actual != expected:
            diff = list(difflib.unified_diff(expected.split("\n"), actual.split("\n"), "expected", target, n=0, lineterm=""))
            ctx.problems.append(f"{target}: differs from upstream plus ADAPTATIONS ({len(diff)} diff lines)")
            for line in diff[:12]:
                print("  ", line[:160])
        else:
            print(f"{target}: equals upstream plus its rows; CRLF on every line")
        if treatment == "skill":
            topic = lf(ctx.topic_row.read_bytes()).strip("\n")
            if topic not in actual.split("\n"):
                ctx.problems.append(f"{target}: row A11 does not equal topic-row.txt")
        if treatment == "stub":
            base = ctx.base / target
            if base.is_file():
                desc = [ln for ln in lf(base.read_bytes()).split("\n") if ln.startswith("description:")][:1]
                mine_desc = [ln for ln in actual.split("\n") if ln.startswith("description:")][:1]
                if not desc or desc != mine_desc:
                    ctx.problems.append(f"{target}: the description differs from the row-0 copy")
                else:
                    print(f"{target}: description equals the row-0 copy")
            else:
                ctx.problems.append(f"{target}: no row-0 copy to compare the description with")


def heading_slugs(text: str) -> set[str]:
    slugs = set()
    for heading in re.findall(r"^#+\s+(.+?)\s*$", text, re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        slugs.add(slug)
    return slugs


def check_lint(ctx: Ctx) -> None:
    targets = [b[3] for b in ctx.blobs]
    link_targets = [b[3] for b in ctx.blobs if b[4] != "stub" and b[3].endswith(".md")]
    for target in targets:
        path = ctx.root / target
        if not path.is_file():
            ctx.problems.append(f"{target}: missing")
            continue
        text = lf(path.read_bytes())
        lines = text.split("\n")
        for n, line in enumerate(lines, 1):
            if m := FORBIDDEN.search(line):
                ctx.problems.append(f"{target}:{n}: FORBIDDEN match {m.group(0)!r}")
            if A8_OLD.search(line):
                ctx.problems.append(f"{target}:{n}: a capabilities/ path not under _inspiration/_capabilities/")
        if target in link_targets:
            slugs = heading_slugs(text)
            for n, line in enumerate(lines, 1):
                for link in LINK_RE.findall(line):
                    if link == "..." or "{" in link or link.startswith(("http://", "https://")):
                        continue
                    if link.startswith("#"):
                        if link == "#orchestration" and "orchestration" not in slugs:
                            ctx.problems.append(f"{target}:{n}: #orchestration matches no heading")
                        continue
                    rel = link.split("#", 1)[0]
                    if not (path.parent / rel).exists():
                        ctx.problems.append(f"{target}:{n}: broken link {link}")
        base = ctx.base / target
        old = lf(base.read_bytes()).split("\n") if base.is_file() else []
        changed: list[int] = []
        for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(None, old, lines, autojunk=False).get_opcodes():
            if tag in ("replace", "insert"):
                changed.extend(range(j1 + 1, j2 + 1))
        for n in changed:
            line = lines[n - 1]
            if any(rx.search(line) for rx in ROUTING_RE):
                if any(t == target and ln == n and need in line for t, ln, need in ctx.exceptions):
                    print(f"{target}:{n}: routing exception (upstream text)")
                    continue
                ctx.problems.append(f"{target}:{n}: added or changed line matches ROUTING_RE")
    print(f"lint: {len(targets)} ported files scanned")


def run(ctx: Ctx, modes: list[str]) -> list[str]:
    for mode in modes:
        {"files": check_files, "skill": check_skill, "lint": check_lint}[mode](ctx)
    return ctx.problems


# ---------------------------------------------------------------- selftest fixtures
FIX_SKILL = "---\nname: fixture-skill\n---\nSnapshots live in capabilities/x.md here.\n| Topic too broad | upstream text |\nSee [the template](templates/t.md).\n"
FIX_STUB = "---\ndescription: \"fixture stub\"\n---\nkept in the skill's `capabilities/`\ndirectory) and more.\n"
FIX_T = "Source: `capabilities/chatgpt.md`.\nPlain line.\n"
FIX_S = "Skeleton line.\n"
FIX_TOPIC = "| Topic too broad | av-kit text |"
SK = "s/SKILL.md"
WF = "w/stub.md"
FIX_ROWS = (
    Row("F1", "skill", "span", 2, 2, "name: fixture-skill", "name: Fixture Skill"),
    Row("F8", "skill", "a8", lines=(4,)),
    Row("F11", "skill", "topic", 5, 5),
    Row("FW", "stub", "span", 4, 5, "(the skill's `capabilities/`\ndirectory)", "(`_inspiration/_capabilities/`)"),
)


def build_fixture(tmp: pathlib.Path) -> Ctx:
    up, root, base = tmp / "up", tmp / "root", tmp / "base"
    files = {"SKILL.md": FIX_SKILL, "stub.md": FIX_STUB.replace("kept in the skill's", "kept in (the skill's"), "t.md": FIX_T, "s.md": FIX_S}
    for name, text in files.items():
        (up / name).parent.mkdir(parents=True, exist_ok=True)
        (up / name).write_bytes(text.encode())
    blobs = tuple(
        (name, blob_id(files[name].encode())[:7], len(files[name].encode()), target, kind)
        for name, target, kind in (("SKILL.md", SK, "skill"), ("stub.md", WF, "stub"), ("t.md", "s/templates/t.md", "a8"), ("s.md", "s/templates/s.md", "equal"))
    )
    (tmp / "topic.txt").write_bytes((FIX_TOPIC + "\n").encode())
    ctx = Ctx(root=root, upstream=up, base=base, topic_row=tmp / "topic.txt", blobs=blobs, rows=FIX_ROWS, exceptions=())
    skill = adapt(ctx, "skill", FIX_SKILL)
    stub = adapt(ctx, "stub", files["stub.md"])
    assert not ctx.problems, ctx.problems
    out = {SK: skill.replace("\n", "\r\n"), WF: stub.replace("\n", "\r\n"), "s/templates/t.md": apply_a8(FIX_T), "s/templates/s.md": FIX_S}
    for rel, text in out.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(text.encode())
    (base / WF).parent.mkdir(parents=True, exist_ok=True)
    (base / WF).write_bytes(files["stub.md"].replace("\n", "\r\n").encode())
    return ctx


def selftest() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as raw:
        tmp = pathlib.Path(raw)
        master = build_fixture(tmp / "master")

        def case(name: str, modes: list[str], mutate, expect_refused: bool = True) -> None:
            work = tmp / name
            shutil.copytree(tmp / "master", work)
            ctx = replace(master, root=work / "root", upstream=work / "up", base=work / "base", topic_row=work / "topic.txt", problems=[])
            ctx = mutate(ctx) or ctx
            problems = run(ctx, modes)
            refused = bool(problems)
            print(f"selftest {name}: refused={refused} problems={problems[:2]}")
            if refused != expect_refused:
                failures.append(f"{name}: refused={refused}, expected {expect_refused}")

        def edit(rel: str, old: bytes, new: bytes):
            def mutate(ctx: Ctx):
                path = ctx.root / rel
                data = path.read_bytes()
                assert old in data, (rel, old)
                path.write_bytes(data.replace(old, new, 1))
            return mutate

        case("control", ["files", "skill", "lint"], lambda ctx: None, expect_refused=False)
        case("template-extra-word", ["files"], edit("s/templates/t.md", b"Plain line.", b"Plain extra line."))
        case("wrong-blob-id", ["files"], lambda ctx: replace(ctx, blobs=tuple((b[0], "0000000", *b[2:]) if b[0] == "s.md" else b for b in ctx.blobs)))
        case("adaptation-left-out", ["skill"], edit(SK, b"name: Fixture Skill", b"name: fixture-skill"))
        case("lf-line", ["skill"], edit(SK, b"---\r\n", b"---\n"))
        case("row-matches-nothing", ["skill"], lambda ctx: replace(ctx, rows=ctx.rows + (Row("FX", "skill", "span", 6, 6, "no such upstream text", "x"),)))
        case("forbidden-path", ["lint"], edit("s/templates/s.md", b"Skeleton line.", b"Skeleton line from P:/agentic-framework."))
        case("bare-capabilities", ["lint"], edit("s/templates/s.md", b"Skeleton line.", b"Read capabilities/chatgpt.md first."))
        case("broken-link", ["lint"], edit(SK, b"templates/t.md", b"templates/missing.md"))
        case("routing-pin", ["lint"], edit("s/templates/s.md", b"Skeleton line.", b"Use gpt-5 for this."))
    for f in failures:
        print("SELFTEST FAIL:", f)
    print(f"port-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    modes = [m for m in ("files", "skill", "lint") if f"--{m}" in argv] or ["files", "skill", "lint"]
    unknown = [a for a in argv if a not in ("--files", "--skill", "--lint")]
    if unknown:
        print("usage: port-check.py [--files] [--skill] [--lint] | --selftest")
        return 2
    root = pathlib.Path.cwd()
    ctx = Ctx(root=root, upstream=pathlib.Path(UPSTREAM_DIR), base=pathlib.Path(BASE_DIR), topic_row=root / PLAN / "topic-row.txt")
    problems = run(ctx, modes)
    for p in problems:
        print("PROBLEM:", p)
    print(f"port-check {' '.join('--' + m for m in modes)}: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
