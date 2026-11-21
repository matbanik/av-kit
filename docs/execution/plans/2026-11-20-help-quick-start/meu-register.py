"""Session 99 MEU registration (task row 1; MEU-162): the MEU-162 entry in the MEU SSOT, its
Phase 6 residual section and its matrix row 6.23. Adapted from Session 97's
`docs/execution/plans/2026-11-19-e2e-host-parity/meu-register.py`, for phase 6.

    uv run --no-sync python <plan>/meu-register.py                 (the real run)
    uv run --no-sync python <plan>/meu-register.py --dry-run
    uv run --no-sync python <plan>/meu-register.py --selftest [--live <tree>]

There is no add-MEU command in `tools/meu_status.py`, so this script makes the three edits and
`tools/meu_status.py render` then regenerates `meu-registry.md` and `docs/BUILD_PLAN.md`
(never hand-edited).

1. `.agent/context/meu-status.yaml` (LF): loaded with `tools.meu_status.model.load`, the new
   entry appended to `meus` and the P2 band's range raised to the new id with this session's
   note, then written by `tools.meu_status.model.save` to a staged file. `save` must write the
   repository file byte for byte when nothing changed (checked first), so the staged file
   differs from the file now only by the new entry and the P2 range. That is checked on the
   parsed data. Then the staged bytes replace the file.
2. `docs/build-plan/06-gui.md` (CRLF): the anchor `help-quick-start-residual` and the plan's
   §The 06 residual section, read from `implementation-plan.md`, before
   `## Validation Commands`. Phase 6 has no MEUs table, so no table row is added.
3. `docs/build-plan/build-priority-matrix.md` (CRLF): the 6.23 row after the `6.22 | MEU-158`
   row, in the same columns.

Before any write: the id, the matrix item, the slug and the anchor are free in all three
files; each insertion point occurs exactly once; and each file's SHA-256 is the one row 0
recorded in `baseline-scope.json` (`--baseline-scope`, default this plan's), so the edit
applies to the bytes the plan read. Every file is read and written as bytes and keeps its line
endings, and each file's endings are checked again after the write. `--dry-run` writes the
three results under `C:/Temp/av-kit/help-quick-start/meu-register/` and changes no repository
file.

`--selftest` never reads the live register for its positive case. It builds the three edits on
an unregistered fixture: the three files at HEAD read from git (or, once the registration is
committed, at the parent of the commit that added it), with the endings the worktree keeps. The
live tree (`--live`, default the repository) is only checked for its own state: unregistered
files build, and registered files refuse a second registration.

Exit 0 on success, 1 on a refused precondition or check, 2 on an argument problem.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = Path("P:/av-kit")
SCRATCH = Path("C:/Temp/av-kit/help-quick-start/meu-register")
PLAN_FILE = HERE / "implementation-plan.md"
SCOPE_FILE = HERE / "baseline-scope.json"
YAML = ".agent/context/meu-status.yaml"
PHASE = "docs/build-plan/06-gui.md"
MATRIX = "docs/build-plan/build-priority-matrix.md"
MEU = "MEU-162"
MATRIX_ITEM = "6.23"
SLUG = "gui-help-quick-start"
ANCHOR = "help-quick-start-residual"
TITLE = "Help quick start (residual)"
DEPENDS = ["MEU-23", "MEU-158"]
TODAY = "2026-11-20"
VALIDATION = "## Validation Commands"
SECTION_HEADING = "### The 06 residual section (written in row 1)"
MATRIX_ROW_AFTER = "| 6.22 | MEU-158 |"
DESCRIPTION = (
    "Each page's help card gets a short quick start: one intro sentence, 4 or 5 numbered steps"
    " in ASD-STE100 Strict style and a marked screenshot (two on Settings) in light and dark,"
    " taken by script from demo data; the card stays closed on a first visit and its header"
    " names the quick start; a unit test fails on step drift and an Electron test proves every"
    " step target and image on the real app."
)


def note() -> str:
    return (
        f"Registered {TODAY} from Mat's request for a better help guide (D-1289 to D-1294),"
        " Session 99."
    )


def entry(meu: str, matrix: str) -> dict[str, Any]:
    return {
        "row_key": meu,
        "id": meu,
        "slug": SLUG,
        "phase": "6",
        "band": "P2",
        "matrix_item": matrix,
        "build_ref": {
            "path": "build-plan/06-gui.md",
            "anchor": ANCHOR,
            "text": f"Phase 6 §{TITLE}",
        },
        "description": DESCRIPTION,
        "status": "pending",
        "status_labels": {"registry": "⬜ pending", "build_plan": "⬜"},
        "surface_overrides": None,
        "dependencies_raw": ", ".join(DEPENDS),
        "dependency_parse_status": "parsed",
        "depends_on": list(DEPENDS),
        "execution_plan": None,
        "updated": TODAY,
        "closed_reason": None,
        "note": note(),
    }


def raise_range(text: str, number: int) -> str:
    match = re.match(r"MEU-14–(\d+) \(", text)
    if match is None or not text.endswith(")"):
        raise ValueError("the P2 range is not 'MEU-14–N (...)'")
    if number <= int(match.group(1)):
        raise ValueError(f"the P2 range already reaches MEU-{match.group(1)}")
    raised = f"MEU-14–{number} (" + text[match.end() :]
    return raised[:-1] + f"; {TODAY} Session 99 residual MEU-{number})"


def plan_section(plan_text: str) -> list[str]:
    """The fenced markdown block under the plan's §The 06 residual section."""
    lines = plan_text.replace("\r\n", "\n").split("\n")
    at = once(lines, lambda line: line == SECTION_HEADING, "plan §The 06 residual section")
    start = next(i for i in range(at + 1, len(lines)) if lines[i].startswith("```"))
    if lines[start] != "```markdown":
        raise ValueError("the plan's residual section is not a ```markdown block")
    end = next(i for i in range(start + 1, len(lines)) if lines[i] == "```")
    body = lines[start + 1 : end]
    if not body or body[0] != f"### {TITLE}":
        raise ValueError(f"the plan's residual section does not start '### {TITLE}'")
    return body


def phase_section(meu: str, plan_text: str) -> list[str]:
    body = plan_section(plan_text)
    if meu != MEU:
        body = [line.replace(f"**{MEU}.**", f"**{meu}.**") for line in body]
    return [f'<a id="{ANCHOR}"></a>', "", *body, ""]


def matrix_row(meu: str, matrix: str) -> str:
    deps = ", ".join(DEPENDS)
    return f"| {matrix} | {meu} | `{SLUG}` | [06 §{TITLE}](06-gui.md#{ANCHOR}) | {deps} |"


def split(raw: bytes, ending: bytes) -> list[str]:
    text = raw.decode("utf-8")
    if ending == b"\r\n" and raw.count(b"\n") != raw.count(b"\r\n"):
        raise ValueError("a CRLF file has a bare LF")
    return text.split(ending.decode())


def once(lines: list[str], pred: Any, what: str) -> int:
    hits = [i for i, line in enumerate(lines) if pred(line)]
    if len(hits) != 1:
        raise ValueError(f"{what}: {len(hits)} matches, not 1")
    return hits[0]


def edit_phase(raw: bytes, meu: str, plan_text: str) -> bytes:
    lines = split(raw, b"\r\n")
    text = "\n".join(lines)
    for needle in (meu, f'id="{ANCHOR}"', f"### {TITLE}"):
        if needle in text:
            raise ValueError(f"{PHASE}: {needle!r} is already there")
    at = once(lines, lambda line: line == VALIDATION, f"{PHASE} validation heading")
    lines[at:at] = phase_section(meu, plan_text)
    return "\r\n".join(lines).encode("utf-8")


def edit_matrix(raw: bytes, meu: str, matrix: str) -> bytes:
    lines = split(raw, b"\r\n")
    text = "\n".join(lines)
    for needle in (f"| {meu} |", f"| {matrix} |", f"`{SLUG}`"):
        if needle in text:
            raise ValueError(f"{MATRIX}: {needle!r} is already there")
    row = once(lines, lambda line: line.startswith(MATRIX_ROW_AFTER), f"{MATRIX} 6.22 row")
    lines.insert(row + 1, matrix_row(meu, matrix))
    return "\r\n".join(lines).encode("utf-8")


def edit_yaml(raw: bytes, meu: str, matrix: str, staged: Path, model: Any) -> bytes:
    if b"\r" in raw:
        raise ValueError(f"{YAML}: a CR in an LF file")
    source = staged.with_name("meu-status.now.yaml")
    source.write_bytes(raw)
    data = model.load(source)
    roundtrip = staged.with_name("meu-status.roundtrip.yaml")
    model.save(copy.deepcopy(data), roundtrip)
    if roundtrip.read_bytes() != raw:
        raise ValueError(f"{YAML}: model.save does not write the file byte for byte")
    meus = data["meus"]
    if any(m["row_key"] == meu or m["id"] == meu for m in meus):
        raise ValueError(f"{YAML}: {meu} is already registered")
    if any(m.get("matrix_item") == matrix for m in meus):
        raise ValueError(f"{YAML}: matrix item {matrix} is taken")
    if any(m.get("slug") == SLUG for m in meus):
        raise ValueError(f"{YAML}: slug {SLUG} is taken")
    number = int(meu.split("-", 1)[1])
    new = copy.deepcopy(data)
    new["meus"].append(entry(meu, matrix))
    band = once(new["summary_bands"], lambda b: b.get("key") == "P2", "P2 band")
    old_range = new["summary_bands"][band]["range"]
    new["summary_bands"][band]["range"] = raise_range(old_range, number)
    model.save(new, staged)
    reread = model.load(staged)
    back = copy.deepcopy(reread)
    back["meus"] = [m for m in back["meus"] if m["row_key"] != meu]
    back["summary_bands"][band]["range"] = old_range
    if back != data:
        raise ValueError(f"{YAML}: the staged file differs by more than the entry and the range")
    if [m for m in reread["meus"] if m["row_key"] == meu] != [entry(meu, matrix)]:
        raise ValueError(f"{YAML}: the staged entry does not read back as written")
    return staged.read_bytes()


def endings_ok(rel: str, raw: bytes) -> bool:
    if rel == YAML:
        return b"\r" not in raw
    return raw.count(b"\n") == raw.count(b"\r\n") and raw.count(b"\r") == raw.count(b"\r\n")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_model() -> Any:
    sys.path.insert(0, str(REPO))
    from tools.meu_status import model

    return model


def build(repo: Path, meu: str, matrix: str, work: Path, model: Any) -> dict[str, bytes]:
    work.mkdir(parents=True, exist_ok=True)
    plan_text = PLAN_FILE.read_bytes().decode("utf-8")
    return {
        YAML: edit_yaml((repo / YAML).read_bytes(), meu, matrix, work / "meu-status.yaml", model),
        PHASE: edit_phase((repo / PHASE).read_bytes(), meu, plan_text),
        MATRIX: edit_matrix((repo / MATRIX).read_bytes(), meu, matrix),
    }


def git(*args: str) -> bytes:
    done = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, check=False)
    if done.returncode != 0:
        raise ValueError(f"git {' '.join(args)}: {done.stderr.decode('utf-8', 'replace').strip()}")
    return done.stdout


def registered(raw: bytes) -> bool:
    return SLUG.encode() in raw or f'id="{ANCHOR}"'.encode() in raw


def fixture_rev() -> str:
    """A commit whose three files are not yet registered: HEAD until the registration is
    committed, then the parent of the oldest commit that added the slug to the YAML."""
    head = git("rev-parse", "HEAD").decode().strip()
    if not any(registered(git("show", f"{head}:{rel}")) for rel in (YAML, PHASE, MATRIX)):
        return head
    log = git("log", "--format=%H", "-S", SLUG, "--", YAML).decode().split()
    if not log:
        raise ValueError("HEAD is registered but no commit added the slug to the YAML")
    return git("rev-parse", f"{log[-1]}^").decode().strip()


def write_fixture(rev: str, root: Path) -> Path:
    """The three files at REV, with the endings the worktree keeps (git stores them as LF)."""
    for rel, ending in ((YAML, b"\n"), (PHASE, b"\r\n"), (MATRIX, b"\r\n")):
        raw = git("show", f"{rev}:{rel}")
        if b"\r" in raw:
            raise ValueError(f"{rel} at {rev[:12]}: a CR in the stored blob")
        if registered(raw):
            raise ValueError(f"{rel} at {rev[:12]} is already registered")
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw.replace(b"\n", ending))
    return root


def selftest(live: Path) -> int:
    """The positive case runs on an unregistered fixture from git; LIVE is only checked for
    the state it is in: unregistered files build, registered files refuse a second run."""
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            failures.append(name)

    model = load_model()
    plan_text = PLAN_FILE.read_bytes().decode("utf-8")
    long_range = "MEU-14–161 (Phases 4–11; 2026-11-19 Session 97 residual MEU-161)"
    raised = raise_range(long_range, 162)
    check("the range top is raised", raised.startswith("MEU-14–162 ("))
    check("the note is added before the last bracket", raised.endswith("residual MEU-162)"))
    try:
        raise_range(long_range, 161)
        check("a range already at the id is refused", False)
    except ValueError:
        check("a range already at the id is refused", True)
    section = plan_section(plan_text)
    check("the plan section has the heading, the MEU line and a table", len(section) >= 10)
    check("the plan section names MEU-162", any("**MEU-162.**" in s for s in section))
    check("no backslash in the section", not any("\\" in s for s in section))
    check(
        "the matrix row has the 6.22 row's five columns",
        matrix_row(MEU, MATRIX_ITEM).count(" | ") == 4,
    )
    check("CRLF endings pass", endings_ok(PHASE, b"a\r\nb\r\n"))
    check("a bare LF in a CRLF file fails", not endings_ok(PHASE, b"a\r\nb\n"))
    check("a bare CR in a CRLF file fails", not endings_ok(MATRIX, b"a\rb\r\n"))
    check("a CR in the YAML fails", not endings_ok(YAML, b"a: 1\r\n"))
    with tempfile.TemporaryDirectory() as scratch:
        work = Path(scratch)
        try:
            rev = fixture_rev()
            fixture = write_fixture(rev, work / "fixture")
            print(f"fixture: the three files at {rev[:12]}, unregistered")
        except ValueError as exc:
            print(f"fixture refused: {exc}")
            fixture = None
        check("an unregistered fixture is read from git", fixture is not None)
        try:
            out = build(fixture, MEU, MATRIX_ITEM, work, model) if fixture else {}
        except ValueError as exc:
            print(f"build refused: {exc}")
            out = {}
        check("the three edits build on the fixture", set(out) == {YAML, PHASE, MATRIX})
        live_raw = {rel: (live / rel).read_bytes() for rel in (YAML, PHASE, MATRIX)}
        state = [rel for rel, raw in live_raw.items() if registered(raw)]
        try:
            build(live, MEU, MATRIX_ITEM, work / "live", model)
            refused = ""
        except ValueError as exc:
            refused = str(exc)
        if state:
            print(f"live: registered in {len(state)} of 3 files")
            check(
                "live: a second registration is refused",
                "already" in refused or "taken" in refused,
            )
        else:
            print("live: unregistered")
            check("live: the three edits build", refused == "")
        if out and fixture is not None:
            phase_now = (fixture / PHASE).read_bytes()
            matrix_now = (fixture / MATRIX).read_bytes()
            crlf = b"\r\n"
            for rel in (YAML, PHASE, MATRIX):
                check(f"{Path(rel).name} keeps its endings", endings_ok(rel, out[rel]))
            added = out[PHASE].count(crlf) - phase_now.count(crlf)
            check("06 gains the section", added == len(phase_section(MEU, plan_text)))
            check("matrix gains one row", out[MATRIX].count(crlf) - matrix_now.count(crlf) == 1)
            text = out[PHASE].decode("utf-8")
            at_anchor, at_validation = text.index(f'id="{ANCHOR}"'), text.index(VALIDATION)
            check("the section sits before the validation heading", at_anchor < at_validation)
            p_lines = text.split("\r\n")
            at = p_lines.index(VALIDATION)
            check("a blank line precedes the validation heading", p_lines[at - 1] == "")
            check(
                "the anchor follows a blank line",
                p_lines[p_lines.index(f'<a id="{ANCHOR}"></a>') - 1] == "",
            )
            m_lines = out[MATRIX].decode("utf-8").split("\r\n")
            at = next(i for i, line in enumerate(m_lines) if line.startswith(MATRIX_ROW_AFTER))
            check(
                "the matrix row follows 6.22",
                m_lines[at + 1] == matrix_row(MEU, MATRIX_ITEM),
            )
            now_yaml = (fixture / YAML).read_bytes()
            refusals = (
                ("06 refuses a second run", lambda: edit_phase(out[PHASE], MEU, plan_text)),
                ("matrix refuses a second run", lambda: edit_matrix(out[MATRIX], MEU, "6.23")),
                (
                    "YAML refuses a second run",
                    lambda: edit_yaml(out[YAML], MEU, "6.23", work / "s2.yaml", model),
                ),
                (
                    "YAML refuses a taken matrix item",
                    lambda: edit_yaml(now_yaml, MEU, "6.22", work / "s3.yaml", model),
                ),
                (
                    "YAML refuses a CR",
                    lambda: edit_yaml(b"a: 1\r\n", MEU, "6.23", work / "s4.yaml", model),
                ),
                (
                    "matrix refuses a bare LF",
                    lambda: edit_matrix(matrix_now.replace(crlf, b"\n", 1), "MEU-999", "6.99"),
                ),
            )
            for name, func in refusals:
                try:
                    func()
                    check(name, False)
                except ValueError:
                    check(name, True)
            moved = build(fixture, "MEU-163", "6.24", work / "moved", model)
            check("a moved id gives the moved 06 line", b"**MEU-163.**" in moved[PHASE])
            check("a moved id gives the moved range", "MEU-14–163 (".encode() in moved[YAML])
    print(f"meu-register selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--meu", default=MEU)
    parser.add_argument("--matrix", default=MATRIX_ITEM)
    parser.add_argument("--baseline-scope", type=Path, default=SCOPE_FILE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument(
        "--live", type=Path, default=REPO, help="--selftest only: the tree whose state is checked"
    )
    args = parser.parse_args()
    if args.selftest:
        return selftest(args.live)
    if args.live != REPO:
        print("--live is for --selftest only")
        return 2
    if not re.fullmatch(r"MEU-\d+", args.meu) or not re.fullmatch(r"6\.\d+", args.matrix):
        print("--meu is MEU-N and --matrix is 6.N")
        return 2
    model = load_model()
    if not args.baseline_scope.is_file():
        print(f"REFUSED: no row 0 scope file at {args.baseline_scope.name}")
        return 1
    scope = json.loads(args.baseline_scope.read_bytes().decode("utf-8"))
    for rel in (YAML, PHASE, MATRIX):
        now = sha((REPO / rel).read_bytes())
        if scope.get(rel) != now:
            print(f"REFUSED: {rel} sha256 {now[:16]} is not row 0's {str(scope.get(rel))[:16]}")
            return 1
    print("row 0 hashes: the three files match baseline-scope.json")
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        out = build(REPO, args.meu, args.matrix, SCRATCH / "work", model)
    except ValueError as exc:
        print(f"REFUSED: {exc}")
        return 1
    for rel, raw in out.items():
        before = (REPO / rel).read_bytes()
        print(f"{rel}: {len(before)} -> {len(raw)} bytes, sha256 {sha(raw)[:16]}")
        if not endings_ok(rel, raw):
            print(f"REFUSED: {rel} would change its line endings")
            return 1
        if args.dry_run:
            target = SCRATCH / Path(rel).name
            target.write_bytes(raw)
            print(f"  dry run: written to {target.name} in the scratch folder")
    if args.dry_run:
        print(f"dry run: {args.meu} at {args.matrix} would register; no repository file changed")
        return 0
    for rel, raw in out.items():
        (REPO / rel).write_bytes(raw)
    bad = [rel for rel in out if not endings_ok(rel, (REPO / rel).read_bytes())]
    if bad:
        print(f"FAILED: line endings changed after the write in {', '.join(bad)}")
        return 1
    print("line endings after the write: 06 CRLF, matrix CRLF, YAML LF")
    print(f"registered {args.meu} at {args.matrix}; now run tools/meu_status.py render")
    return 0


if __name__ == "__main__":
    sys.exit(main())
