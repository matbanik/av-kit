"""Session 97 MEU registration (task row 2; AC-161.13; D-1250): MEU-161 in the MEU SSOT, its
Phase 9 section and its matrix row. Adapted from Session 93's
`docs/execution/plans/2026-11-17-video-tail-frame/meu-register.py` (Session 96 RULE-3).

    uv run --no-sync python <plan>/meu-register.py --dry-run
    uv run --no-sync python <plan>/meu-register.py --baseline-scope <plan>/baseline-scope.json
    uv run --no-sync python <plan>/meu-register.py --selftest [--live <tree>]

There is no add-MEU command in `tools/meu_status.py`, so this script makes the three edits and
`tools/meu_status.py render` then regenerates `meu-registry.md` and `docs/BUILD_PLAN.md`
(never hand-edited). The id and the matrix item are arguments (`--meu`, default MEU-161;
`--matrix`, default 9.46), because a session that lands first can take them; row 0 records the
free pair and the handoff maps any move.

1. `.agent/context/meu-status.yaml` (LF): loaded with `tools.meu_status.model.load`, the new
   entry appended to `meus` and the P2 band's range raised to the new id with this session's
   note, then written by `tools.meu_status.model.save` to a staged file. `save` writes the
   repository file byte for byte when nothing changed (checked first, so a format drift
   stops the row), so the staged file differs from the file now only by the new entry and the
   P2 range. That is checked on the parsed data: the staged data without the new entry and
   with the old range equals the data now. Then the staged bytes replace the file.
2. `docs/build-plan/09-screenshot-capture.md` (CRLF): the `## Residuals registered 2026-11-19`
   section before `## Named deferrals (not this phase)`, and the MEUs-table row after the
   MEU-160 row.
3. `docs/build-plan/build-priority-matrix.md` (CRLF): the row after the `9.45 | MEU-160` row.

Before any write: the id, the matrix item, the slug and the anchor are free in all three
files; each insertion point occurs exactly once; and, with `--baseline-scope`, each file's
SHA-256 is the one row 0 recorded, so the edit applies to the bytes the plan read. Every file
is read and written as bytes and keeps its line endings. `--dry-run` writes the three results
under `C:/Temp/av-kit/e2e-host-parity/meu-register/` and changes no repository file.

`--selftest` never reads the live register for its positive case (plan R1-F1). It builds the
three edits on an unregistered fixture: the three files at HEAD read from git (or, once the
registration is committed, at the parent of the commit that added it), with the endings the
worktree keeps. The live tree (`--live`, default the repository) is only checked for its own
state: unregistered files build, and registered files (pending, ready_for_review or approved)
refuse a second registration. So it passes before row 2, after it and after row 8 and H2-2.

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

REPO = Path("P:/av-kit")
SCRATCH = Path("C:/Temp/av-kit/e2e-host-parity/meu-register")
YAML = ".agent/context/meu-status.yaml"
PHASE = "docs/build-plan/09-screenshot-capture.md"
MATRIX = "docs/build-plan/build-priority-matrix.md"
SLUG = "capture-text-plate-metrics"
ANCHOR = "text-plate-metrics"
DEPENDS = ["MEU-82", "MEU-102"]
TODAY = "2026-11-19"
DEFERRALS = "## Named deferrals (not this phase)"
PHASE_ROW_AFTER = "| MEU-160 | `capture-video-tail-packet-read` |"
MATRIX_ROW_AFTER = "| 9.45 | MEU-160 |"
DESCRIPTION = (
    "The preview's text plate takes the bake's box: glyph extents in font units scaled and"
    " rounded per extent as FreeType does, and the painted size r - l + 1; against Pillow the"
    " preview plate is exact on all four sides in at least 1,702 of 2,448 breadth cases, more"
    " than 1 px off on a side in at most 5 and never more than 2 px off, and exact in 36 of"
    " the 40 multi-line matrix cases with the other four 1 px off; proved by a"
    " Pillow-generated plate fixture, unit tests and the fidelity E2E at a device scale of 1."
)


def note() -> str:
    return (
        f"Registered {TODAY} from CAPTURE-TEXT-PIXEL-2PX-MINIAIR (triage D-1213; plan"
        f" D-1250), Session 97."
    )


def entry(meu: str, matrix: str) -> dict[str, Any]:
    return {
        "row_key": meu,
        "id": meu,
        "slug": SLUG,
        "phase": "9",
        "band": "P2",
        "matrix_item": matrix,
        "build_ref": {
            "path": "build-plan/09-screenshot-capture.md",
            "anchor": ANCHOR,
            "text": "Phase 9 §Text plate metrics",
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
    return raised[:-1] + f"; {TODAY} Session 97 residual MEU-{number})"


def phase_section(meu: str) -> list[str]:
    return [
        f"## Residuals registered {TODAY}",
        "",
        "One residual MEU from Session 97's plan"
        " (`docs/execution/plans/2026-11-19-e2e-host-parity/`; grouping"
        " `.agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md`). It"
        " changes the preview plate of [§Text preview baseline](#text-preview-baseline) and"
        " [§Multi-line text](#multi-line-text)"
        " (`ui/src/renderer/src/features/capture/capture-text-metrics.ts`).",
        "",
        f'<a id="{ANCHOR}"></a>',
        "",
        "### Text plate metrics",
        "",
        f"> **{meu}.** From `CAPTURE-TEXT-PIXEL-2PX-MINIAIR` (triage D-1213; plan D-1242)."
        " The preview's plate (`textBackgroundBox`) scaled a 16 px glyph table linearly and"
        " rounded the union once, and its width was r − l, while the bake paints Pillow's"
        " inclusive rectangle, r − l + 1 pixels wide. At a device scale of 1 the two right"
        " edges sit 2 px apart, so the fidelity E2E (AC-82.6, AC-102.19, AC-102.20) failed on"
        " the second Windows host; the dev PC's device scale of 2 at a half-pixel origin hid the"
        " gap. The preview follows the bake, as MEU-82 asks: one anchor from the same Segoe"
        " metrics the bake uses.",
        "",
        "| Rule | Contract | Source |",
        "|------|----------|--------|",
        "| Units | Glyph extents and advances for printable ASCII are kept in font units (2048"
        " per em), generated from the system Segoe UI with Pillow; any other character takes"
        " the old fallback's units. | Local Canon: D-1243 |",
        "| Rounding | Each extent is the pen or baseline position plus the FreeType rounding of"
        " its scaled units (FT_MulFix by size × 2048, then FT_PIX_ROUND); the advance is"
        " rounded the same way; the baseline is the line top plus the Segoe ascent, and lines"
        " stay ascent + 4 px apart. | Research-backed: FreeType FT_MulFix and FT_PIX_ROUND;"
        " D-1243 |",
        "| Painted size | The box is x = l, y = t, width r − l + 1 and height"
        " b − t + 1, the pixels Pillow's inclusive rectangle paints. | Local Canon:"
        " D-1242; `adapter.py` `_apply_text` |",
        "| Residual | Against Pillow over 2,448 breadth cases (18 texts × 136 sizes) at"
        " least 1,702 are exact on all four sides, at most 5 differ by more than 1 px on a"
        " side and none by more than 2; of the 40 multi-line matrix cases 36 are exact and"
        " the other four differ by 1 px on one side. The residual is a P3 issue."
        " | Local Canon: D-1244 |",
        "| Tests | A Pillow-generated plate fixture read by pytest and Vitest, and the"
        " fidelity E2E at a device scale of 1. | Local Canon: D-1245, D-1251 |",
        "",
    ]


def phase_row(meu: str) -> str:
    deps = ", ".join(DEPENDS)
    return f"| {meu} | `{SLUG}` | [Text plate metrics](#{ANCHOR}) | {deps} |"


def matrix_row(meu: str, matrix: str) -> str:
    deps = ", ".join(DEPENDS)
    return (
        f"| {matrix} | {meu} | `{SLUG}` | [09 §Text plate metrics]"
        f"(09-screenshot-capture.md#{ANCHOR}) | {deps} |"
    )


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


def edit_phase(raw: bytes, meu: str) -> bytes:
    lines = split(raw, b"\r\n")
    text = "\n".join(lines)
    for needle in (f"| {meu} |", f'id="{ANCHOR}"', f"`{SLUG}`", f"## Residuals registered {TODAY}"):
        if needle in text:
            raise ValueError(f"{PHASE}: {needle!r} is already there")
    at = once(lines, lambda line: line == DEFERRALS, f"{PHASE} deferrals heading")
    lines[at:at] = phase_section(meu)
    row = once(lines, lambda line: line.startswith(PHASE_ROW_AFTER), f"{PHASE} MEU-160 row")
    lines.insert(row + 1, phase_row(meu))
    return "\r\n".join(lines).encode("utf-8")


def edit_matrix(raw: bytes, meu: str, matrix: str) -> bytes:
    lines = split(raw, b"\r\n")
    text = "\n".join(lines)
    for needle in (f"| {meu} |", f"| {matrix} |", f"`{SLUG}`"):
        if needle in text:
            raise ValueError(f"{MATRIX}: {needle!r} is already there")
    row = once(lines, lambda line: line.startswith(MATRIX_ROW_AFTER), f"{MATRIX} 9.45 row")
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


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_model() -> Any:
    sys.path.insert(0, str(REPO))
    from tools.meu_status import model

    return model


def build(repo: Path, meu: str, matrix: str, work: Path, model: Any) -> dict[str, bytes]:
    work.mkdir(parents=True, exist_ok=True)
    return {
        YAML: edit_yaml((repo / YAML).read_bytes(), meu, matrix, work / "meu-status.yaml", model),
        PHASE: edit_phase((repo / PHASE).read_bytes(), meu),
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
    """Isolated from the live register: the positive case runs on an unregistered fixture
    from git, so it passes before registration, after it and after the status advances
    (plan R1-F1). LIVE (the repository, or a scratch copy) is only checked for the state it
    is in: unregistered files build, registered files refuse a second run."""
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            failures.append(name)

    model = load_model()
    long_range = "MEU-14–160 (Phases 4–11; 2026-11-17 Session 93 residual MEU-160)"
    raised = raise_range(long_range, 161)
    check("the range top is raised", raised.startswith("MEU-14–161 ("))
    check("the note is added before the last bracket", raised.endswith("residual MEU-161)"))
    try:
        raise_range(long_range, 160)
        check("a range already at the id is refused", False)
    except ValueError:
        check("a range already at the id is refused", True)
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
            out = build(fixture, "MEU-161", "9.46", work, model) if fixture else {}
        except ValueError as exc:
            print(f"build refused: {exc}")
            out = {}
        check("the three edits build on the fixture", set(out) == {YAML, PHASE, MATRIX})
        live_raw = {rel: (live / rel).read_bytes() for rel in (YAML, PHASE, MATRIX)}
        state = [rel for rel, raw in live_raw.items() if registered(raw)]
        try:
            build(live, "MEU-161", "9.46", work / "live", model)
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
            check("09 stays CRLF", out[PHASE].count(b"\n") == out[PHASE].count(crlf))
            check("matrix stays CRLF", out[MATRIX].count(b"\n") == out[MATRIX].count(crlf))
            check("YAML stays LF", b"\r" not in out[YAML])
            added = out[PHASE].count(crlf) - phase_now.count(crlf)
            check("09 gains the section and one row", added == len(phase_section("MEU-161")) + 1)
            check("matrix gains one row", out[MATRIX].count(crlf) - matrix_now.count(crlf) == 1)
            text = out[PHASE].decode("utf-8")
            at_anchor, at_deferrals = text.index(f'id="{ANCHOR}"'), text.index(DEFERRALS)
            check("the section sits before the deferrals", at_anchor < at_deferrals)
            p_lines = text.split("\r\n")
            at = next(i for i, line in enumerate(p_lines) if line.startswith(PHASE_ROW_AFTER))
            check("the 09 row follows the MEU-160 row", p_lines[at + 1] == phase_row("MEU-161"))
            m_lines = out[MATRIX].decode("utf-8").split("\r\n")
            at = next(i for i, line in enumerate(m_lines) if line.startswith(MATRIX_ROW_AFTER))
            check("the matrix row follows 9.45", m_lines[at + 1] == matrix_row("MEU-161", "9.46"))
            new_text = "\n".join(phase_section("MEU-161"))
            check("no backslash in the new text", "\\" not in new_text)
            now_yaml = (fixture / YAML).read_bytes()
            refusals = (
                ("09 refuses a second run", lambda: edit_phase(out[PHASE], "MEU-161")),
                (
                    "matrix refuses a second run",
                    lambda: edit_matrix(out[MATRIX], "MEU-161", "9.46"),
                ),
                (
                    "YAML refuses a second run",
                    lambda: edit_yaml(out[YAML], "MEU-161", "9.46", work / "s2.yaml", model),
                ),
                (
                    "YAML refuses a taken matrix item",
                    lambda: edit_yaml(now_yaml, "MEU-161", "9.45", work / "s3.yaml", model),
                ),
                (
                    "YAML refuses a CR",
                    lambda: edit_yaml(b"a: 1\r\n", "MEU-161", "9.46", work / "s4.yaml", model),
                ),
            )
            for name, func in refusals:
                try:
                    func()
                    check(name, False)
                except ValueError:
                    check(name, True)
            moved = build(fixture, "MEU-162", "9.47", work / "moved", model)
            check("a moved id gives the moved 09 row", b"| MEU-162 |" in moved[PHASE])
            check("a moved id gives the moved range", "MEU-14–162 (".encode() in moved[YAML])
    print(f"meu-register selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--meu", default="MEU-161")
    parser.add_argument("--matrix", default="9.46")
    parser.add_argument("--baseline-scope", type=Path)
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
    if not re.fullmatch(r"MEU-\d+", args.meu) or not re.fullmatch(r"9\.\d+", args.matrix):
        print("--meu is MEU-N and --matrix is 9.N")
        return 2
    if not args.dry_run and args.baseline_scope is None:
        print("a real run needs --baseline-scope")
        return 2
    model = load_model()
    if args.baseline_scope is not None:
        scope = json.loads(args.baseline_scope.read_bytes().decode("utf-8"))
        for rel in (YAML, PHASE, MATRIX):
            now = sha((REPO / rel).read_bytes())
            if scope.get(rel) != now:
                print(f"REFUSED: {rel} sha256 {now[:16]} is not row 0's {str(scope.get(rel))[:16]}")
                return 1
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        out = build(REPO, args.meu, args.matrix, SCRATCH / "work", model)
    except ValueError as exc:
        print(f"REFUSED: {exc}")
        return 1
    for rel, raw in out.items():
        before = (REPO / rel).read_bytes()
        print(f"{rel}: {len(before)} -> {len(raw)} bytes, sha256 {sha(raw)[:16]}")
        if args.dry_run:
            target = SCRATCH / Path(rel).name
            target.write_bytes(raw)
            print(f"  dry run: written to {target.name} in the scratch folder")
    if args.dry_run:
        print(f"dry run: {args.meu} at {args.matrix} would register; no repository file changed")
        return 0
    for rel, raw in out.items():
        (REPO / rel).write_bytes(raw)
    print(f"registered {args.meu} at {args.matrix}; now run tools/meu_status.py render")
    return 0


if __name__ == "__main__":
    sys.exit(main())
