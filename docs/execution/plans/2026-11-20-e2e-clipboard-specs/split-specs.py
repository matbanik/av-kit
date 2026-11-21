"""Session 98 split of the two clipboard spec files (task rows 0 to 2, the gate; D-1268).

Builds three files from the BASE commit's blobs, never from the working tree:

  ui/tests/e2e/capture-system-clipboard.test.ts  new, LF: the two clipboard tests and the blocks
                                                  they need, each copied byte for byte (a CRLF
                                                  source block is copied with LF endings), after
                                                  the named GUARD lines (D-1282): a file-level
                                                  test.skip unless AVKIT_E2E_CLIPBOARD_GATED=1
  ui/tests/e2e/capture-filmstrip-actions.test.ts CRLF kept: the base file minus AC-88.12 (a)(b)(f)
                                                  and its five clipboard-only blocks, plus one
                                                  named comment line
  ui/tests/e2e/capture-import.test.ts            LF kept: the base file minus AC-132.23 and its
                                                  seven paste-only blocks, the import names they
                                                  alone used, plus one named comment line

A block is one top-level declaration or test() call, with the comment lines right above it, up to
the line before the next block. Usage:

  split-specs.py --out DIR      write the three files under DIR (nothing tracked is touched);
                                refuses, exit 1, when any of the three already exists there
  split-specs.py --write        write them into ui/tests/e2e; refuses unless both old files still
                                equal their BASE blobs and the new file is absent (NO_PARTIAL:
                                all three are written to temp files first, then renamed)
  split-specs.py --check        exit 0 when the three tracked files equal the built ones and every
                                invariant holds; exit 1 with each difference named
  split-specs.py --selftest     builds in memory, checks the invariants, and proves that a changed
                                assertion, a dropped block, a CRLF new file, a clipboard call left
                                in an old file, a new file without its guard and an --out folder
                                that already holds a file are each refused

Invariants (--check and --selftest): every moved block equals its BASE block after CRLF -> LF; the
old files equal BASE minus the named removals plus the named added lines; the new file holds the
two MOVED titles and the old files the five KEPT titles, each once; no file but the new one calls
the system clipboard (CLIPBOARD_CALL); the new file holds the GUARD lines once, after its imports
and before its first block, and no other test.skip; the new file is LF only, the filmstrip file
CRLF only, the import file LF only. Exit 2 is a setup failure (git or a missing block).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BASE = "b59207b"
E2E = "ui/tests/e2e"
FILM = "capture-filmstrip-actions.test.ts"
IMP = "capture-import.test.ts"
NEW = "capture-system-clipboard.test.ts"

FILM_MOVED = [
    "CaptureItem",
    "ImageFixture",
    "SeamState",
    "SHOT_W",
    "SHOT_H",
    "sampleShot",
    "launchApp",
    "buildFixtures",
    "installSeam",
    "ClipboardProbe",
    "readClipboardImage",
    "readSettledClipboardImage",
    "passesShotPixels",
    "primeTransparentClipboard",
    "SHOT_A",
    "SHOT_B",
    "SHOT_C",
    "openCapture",
    "test:AC-88.12 (a)(b)(f)",
]
FILM_REMOVED = [
    "ClipboardProbe",
    "readClipboardImage",
    "readSettledClipboardImage",
    "passesShotPixels",
    "primeTransparentClipboard",
    "test:AC-88.12 (a)(b)(f)",
]
IMP_MOVED = [
    "NOT_AN_IMAGE",
    "PASTED_NAME",
    "CaptureRow",
    "Backend",
    "startBackend",
    "Harness",
    "launch",
    "pngs",
    "slashes",
    "registerBodies",
    "registerBody",
    "toastMessage",
    "SavedClipboard",
    "readClipboard",
    "restoreClipboard",
    "describeFormats",
    "test:AC-132.23",
]
IMP_REMOVED = [
    "PASTED_NAME",
    "pngs",
    "registerBody",
    "SavedClipboard",
    "readClipboard",
    "restoreClipboard",
    "describeFormats",
    "test:AC-132.23",
]
MOVED_TITLES = ["AC-88.12 (a)(b)(f)", "AC-132.23"]
KEPT_TITLES = {
    FILM: ["AC-88.12 (c)", "AC-88.12 (d)(e)", "AC-89.9", "AC-89.15"],
    IMP: ["AC-132.22"],
}
FILM_NOTE_AFTER = (
    "// Copy image oracle (SHOT_PIXELS) reads real decoded pixels back from the main-process"
    " clipboard."
)
FILM_NOTE = (
    "// Session 98 (D-1268): AC-88.12 (a)(b)(f) and its clipboard oracle moved to"
    " capture-system-clipboard.test.ts."
)
IMP_NOTE_AFTER = (
    " * and fails on any difference (S13). The formats before and after are printed for the"
    " receipt."
)
IMP_NOTE = (
    " * Session 98 (D-1268): AC-132.23 and its clipboard helpers moved to"
    " capture-system-clipboard.test.ts."
)
NEW_HEADER = [
    "// Session 98 (D-1268, D-1269): the two E2E tests that write the system clipboard,",
    "// moved unchanged from capture-filmstrip-actions.test.ts (AC-88.12 (a)(b)(f)) and",
    "// capture-import.test.ts (AC-132.23) with the blocks they need. The clipboard is",
    "// shared with the whole desktop, so this file never runs on the dev PC (flake-run.py",
    "// EXCLUDED); on the mini-air, tools/e2e_host/known-failures.json names how it runs",
    "// (gated by the remote-session probe, or skipped).",
    "",
]
GATE_ENV = "AVKIT_E2E_CLIPBOARD_GATED"
GUARD_REASON = "system clipboard spec: runs only in the gated stage on the second Windows host"
#: D-1282: the file skips itself in every run but the mini-air's gated stage, which alone sets
#: GATE_ENV. These lines are the only addition to the new file beyond the header and the move.
GUARD = [
    "// Session 98 (D-1282): only the gated stage of tools/e2e_host/run-e2e.ps1 sets",
    f"// {GATE_ENV}=1. Every other run, the dev PC's included, lists both tests as skipped.",
    "test.skip(",
    f"  process.env.{GATE_ENV} !== '1',",
    f"  '{GUARD_REASON}',",
    ")",
]
CLIPBOARD_CALL = re.compile(r"\bclipboard\.(read|write|clear|available)[A-Za-z]*\(")
TITLE = re.compile(r"^test\('([^']*)'", re.M)
DECL = re.compile(
    r"^(?:export\s+)?(?:async\s+)?(?:function|const|type|let)\s+([A-Za-z_][A-Za-z0-9_]*)"
)


class SetupError(Exception):
    pass


def base_text(name: str) -> str:
    r = subprocess.run(
        ["git", "show", f"{BASE}:{E2E}/{name}"],
        cwd=REPO,
        capture_output=True,
        check=False,
    )
    if r.returncode != 0:
        raise SetupError(
            f"git show {BASE}:{E2E}/{name} failed: {r.stderr.decode(errors='replace')}"
        )
    return r.stdout.decode("utf-8")


def split_lines(text: str) -> list[str]:
    """Lines without their endings (the caller knows the file's one ending)."""
    return text.replace("\r\n", "\n").split("\n")


def block_name(line: str) -> str | None:
    if line.startswith("test('"):
        title = line[len("test('") :].split("'", 1)[0]
        for t in MOVED_TITLES + KEPT_TITLES[FILM] + KEPT_TITLES[IMP]:
            if title.startswith(t + " "):
                return "test:" + t
        return "test:" + title
    m = DECL.match(line)
    return m.group(1) if m else None


def blocks(lines: list[str]) -> tuple[int, list[tuple[str, int, int]]]:
    """(the first block's start, [(name, start, end_exclusive)]) over 0-based line indexes."""
    starts: list[tuple[int, str]] = []
    for i, ln in enumerate(lines):
        if not ln or ln[0].isspace() or ln.startswith(("import", "}", ")", "]", "/", "*")):
            continue
        name = block_name(ln)
        if name is None:
            raise SetupError(f"top-level line {i + 1} is no known block: {ln[:60]!r}")
        s = i
        while s > 0 and lines[s - 1].startswith(("//", "/**", " *", " */")):
            s -= 1
        starts.append((s, name))
    out = []
    for k, (s, name) in enumerate(starts):
        e = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        out.append((name, s, e))
    return (starts[0][0] if starts else len(lines)), out


def pick(lines: list[str], names: list[str]) -> list[str]:
    _, bl = blocks(lines)
    by = {n: (s, e) for n, s, e in bl}
    missing = [n for n in names if n not in by]
    if missing:
        raise SetupError(f"blocks not found: {missing}")
    out: list[str] = []
    for n, s, e in bl:
        if n in names:
            out.extend(lines[s:e])
    return out


def drop(lines: list[str], names: list[str]) -> list[str]:
    _, bl = blocks(lines)
    gone = {n for n, _, _ in bl if n in names}
    if gone != set(names):
        raise SetupError(f"blocks not found: {sorted(set(names) - gone)}")
    keep: list[str] = []
    first, _ = blocks(lines)
    keep.extend(lines[:first])
    for n, s, e in bl:
        if n not in names:
            keep.extend(lines[s:e])
    return keep


def import_lines(lines: list[str]) -> list[tuple[int, str]]:
    return [(i, ln) for i, ln in enumerate(lines) if ln.startswith("import ")]


IMPORT_RE = re.compile(r"^import \{ (.*) \} from '([^']+)'$")


def used(name: str, body: str) -> bool:
    return re.search(r"\b" + re.escape(name) + r"\b", body) is not None


def prune_imports(head: list[str], body: str) -> list[str]:
    """The import lines of head with each named import kept only when body uses it."""
    out = []
    for ln in head:
        m = IMPORT_RE.match(ln)
        if not m:
            out.append(ln)
            continue
        names = [n.strip() for n in m.group(1).split(",")]
        kept = [n for n in names if used(n.split()[-1], body)]
        if kept:
            out.append("import { " + ", ".join(kept) + " } from '" + m.group(2) + "'")
    return out


def merged_imports(film: list[str], imp: list[str], body: str) -> list[str]:
    """One import line per module, film's order first, names in first-seen order, pruned."""
    order: list[str] = []
    names: dict[str, list[str]] = {}
    for src in (film, imp):
        for _, ln in import_lines(src):
            m = IMPORT_RE.match(ln)
            if not m:
                raise SetupError(f"unexpected import line: {ln!r}")
            mod = m.group(2)
            if mod not in names:
                order.append(mod)
                names[mod] = []
            for n in (x.strip() for x in m.group(1).split(",")):
                if n not in names[mod]:
                    names[mod].append(n)
    out = []
    local = [m for m in order if m.startswith("./")]
    for mod in [m for m in order if not m.startswith("./")]:
        kept = [n for n in names[mod] if used(n.split()[-1], body)]
        if kept:
            out.append("import { " + ", ".join(kept) + " } from '" + mod + "'")
    out.append("")
    for mod in local:
        kept = [n for n in names[mod] if used(n.split()[-1], body)]
        if kept:
            out.append("import { " + ", ".join(kept) + " } from '" + mod + "'")
    return out


def header_end(lines: list[str]) -> int:
    """The index of the first line after the import block (imports and blank lines)."""
    i = 0
    while i < len(lines) and (lines[i].startswith("import ") or lines[i] == ""):
        i += 1
    return i


def insert_after(lines: list[str], anchor: str, new: str) -> list[str]:
    hits = [i for i, ln in enumerate(lines) if ln == anchor]
    if len(hits) != 1:
        raise SetupError(f"anchor found {len(hits)} times: {anchor[:50]!r}")
    return lines[: hits[0] + 1] + [new] + lines[hits[0] + 1 :]


def build(film_text: str, imp_text: str) -> dict[str, bytes]:
    film = split_lines(film_text)
    imp = split_lines(imp_text)
    # The new file: header comment, merged imports, then each source's moved blocks in order.
    film_body = pick(film, FILM_MOVED)
    imp_body = pick(imp, IMP_MOVED)
    body = "\n".join(film_body + imp_body)
    new_lines = (
        NEW_HEADER + merged_imports(film, imp, body) + [""] + GUARD + [""] + film_body + imp_body
    )
    while new_lines and new_lines[-1] == "":
        new_lines.pop()
    new_text = "\n".join(new_lines) + "\n"
    # The old files: base minus the removed blocks, the unused imports pruned, one note line.
    film_rest = drop(film, FILM_REMOVED)
    he = header_end(film_rest)
    film_rest = prune_imports(film_rest[:he], "\n".join(film_rest[he:])) + film_rest[he:]
    film_rest = insert_after(film_rest, FILM_NOTE_AFTER, FILM_NOTE)
    imp_rest = drop(imp, IMP_REMOVED)
    he = header_end(imp_rest)
    imp_rest = prune_imports(imp_rest[:he], "\n".join(imp_rest[he:])) + imp_rest[he:]
    imp_rest = insert_after(imp_rest, IMP_NOTE_AFTER, IMP_NOTE)
    return {
        NEW: new_text.encode("utf-8"),
        FILM: "\r\n".join(film_rest).encode("utf-8"),
        IMP: "\n".join(imp_rest).encode("utf-8"),
    }


def invariants(out: dict[str, bytes], film_text: str, imp_text: str) -> list[str]:
    bad: list[str] = []
    new = out[NEW].decode("utf-8")
    if "\r" in new:
        bad.append(f"{NEW} holds a CR (it is LF only)")
    film_out = out[FILM].decode("utf-8")
    if film_out.replace("\r\n", "").count("\n"):
        bad.append(f"{FILM} holds a bare LF (it stays CRLF)")
    if "\r" in out[IMP].decode("utf-8"):
        bad.append(f"{IMP} holds a CR (it stays LF)")
    new_lines = split_lines(new)
    for src_text, names in ((film_text, FILM_MOVED), (imp_text, IMP_MOVED)):
        src = split_lines(src_text)
        _, bl = blocks(src)
        for n, s, e in bl:
            if n not in names:
                continue
            chunk = [ln for ln in src[s:e]]
            while chunk and chunk[-1] == "":
                chunk.pop()
            hits = [i for i in range(len(new_lines)) if new_lines[i : i + len(chunk)] == chunk]
            if len(hits) != 1:
                bad.append(f"moved block {n} found {len(hits)} times in {NEW}")
    titles = TITLE.findall(new)
    for t in MOVED_TITLES:
        if sum(1 for x in titles if x.startswith(t + " ")) != 1:
            bad.append(f"{NEW} does not hold {t} once")
    if len(titles) != len(MOVED_TITLES):
        bad.append(f"{NEW} holds {len(titles)} tests, not {len(MOVED_TITLES)}")
    for name, kept in KEPT_TITLES.items():
        text = out[name].decode("utf-8")
        got = TITLE.findall(text)
        if [next((k for k in kept if g.startswith(k + " ")), g) for g in got] != kept:
            bad.append(f"{name} titles {got} are not {kept}")
        if CLIPBOARD_CALL.search(text):
            bad.append(f"{name} still calls the system clipboard")
    if not CLIPBOARD_CALL.search(new):
        bad.append(f"{NEW} calls no clipboard function")
    guard_at = [i for i in range(len(new_lines)) if new_lines[i : i + len(GUARD)] == GUARD]
    first_test = next((i for i, ln in enumerate(new_lines) if ln.startswith("test('")), -1)
    last_import = max((i for i, ln in enumerate(new_lines) if ln.startswith("import ")), default=-1)
    if len(guard_at) != 1 or not last_import < guard_at[0] < first_test:
        bad.append(f"{NEW} does not hold the GUARD lines once, after its imports and before a test")
    if new.count("test.skip(") != 1:
        bad.append(f"{NEW} holds {new.count('test.skip(')} test.skip calls, not the guard's one")
    for name in (FILM, IMP):
        if "test.skip(" in out[name].decode("utf-8"):
            bad.append(f"{name} holds a test.skip")
    # The old files: every base line that is not in a removed block or a pruned import survives
    # in order, and the only added line is the note.
    for name, src_text, removed, note in (
        (FILM, film_text, FILM_REMOVED, FILM_NOTE),
        (IMP, imp_text, IMP_REMOVED, IMP_NOTE),
    ):
        src = split_lines(src_text)
        _, bl = blocks(src)
        gone = {i for n, s, e in bl if n in removed for i in range(s, e)}
        expect = [ln for i, ln in enumerate(src) if i not in gone and not ln.startswith("import ")]
        got = [ln for ln in split_lines(out[name].decode("utf-8")) if not ln.startswith("import ")]
        if got.count(note) != 1:
            bad.append(f"{name}: the note line is not there once")
        got = [ln for ln in got if ln != note]
        if got != expect:
            bad.append(f"{name}: the kept lines differ from BASE minus the removed blocks")
    return bad


def tracked() -> dict[str, Path]:
    return {n: REPO / E2E / n for n in (NEW, FILM, IMP)}


def cmd_check(out: dict[str, bytes], film_text: str, imp_text: str) -> int:
    bad = invariants(out, film_text, imp_text)
    for n, p in tracked().items():
        if not p.is_file():
            bad.append(f"{E2E}/{n} is missing")
        elif p.read_bytes() != out[n]:
            bad.append(f"{E2E}/{n} differs from the built file")
    for b in bad:
        print("split-specs: " + b)
    print(f"split-specs check: {'ok' if not bad else 'FAILED'} ({len(bad)} problem(s))")
    return 0 if not bad else 1


def cmd_write(out: dict[str, bytes], film_text: str, imp_text: str) -> int:
    bad = invariants(out, film_text, imp_text)
    paths = tracked()
    if paths[NEW].exists():
        bad.append(f"{E2E}/{NEW} exists already")
    for n, src in ((FILM, film_text), (IMP, imp_text)):
        want = src.encode("utf-8")
        if n == FILM:
            want = want.replace(b"\n", b"\r\n")  # autocrlf checkout of an LF blob
        if paths[n].read_bytes() != want:
            bad.append(f"{E2E}/{n} is not its {BASE} blob")
    if bad:
        for b in bad:
            print("split-specs: refused: " + b)
        return 1
    temps: dict[str, Path] = {}
    try:
        for n, data in out.items():
            fd, tmp = tempfile.mkstemp(prefix=".split-", dir=paths[n].parent)
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
            temps[n] = Path(tmp)
        for n, tmp in temps.items():
            os.replace(tmp, paths[n])
            print(f"split-specs: wrote {E2E}/{n} ({len(out[n])} bytes)")
    finally:
        for tmp in temps.values():
            if tmp.exists():
                tmp.unlink()
    return 0


def cmd_out(d: Path, out: dict[str, bytes], film_text: str, imp_text: str) -> int:
    present = [d / n for n in out if (d / n).exists()]
    if present:
        for p in present:
            print(f"split-specs: refused: {p} exists; --out writes a fresh folder")
        return 1
    d.mkdir(parents=True, exist_ok=True)
    for n, data in out.items():
        with open(d / n, "xb") as fh:
            fh.write(data)
        print(f"split-specs: {d / n} ({len(data)} bytes)")
    bad = invariants(out, film_text, imp_text)
    for b in bad:
        print("split-specs: " + b)
    return 0 if not bad else 1


def cmd_selftest(out: dict[str, bytes], film_text: str, imp_text: str) -> int:
    fails = []
    if invariants(out, film_text, imp_text):
        fails.append(
            "the built files fail the invariants: "
            + "; ".join(invariants(out, film_text, imp_text))
        )
    changed = dict(out)
    changed[NEW] = out[NEW].replace(b"toBe('C:/e2e/b.webp')", b"toBe('C:/e2e/x.webp')", 1)
    if changed[NEW] == out[NEW] or not invariants(changed, film_text, imp_text):
        fails.append("a changed assertion was not refused")
    dropped = dict(out)
    dropped[NEW] = out[NEW].replace(b"function passesShotPixels", b"function passesShotPixelz", 1)
    if not invariants(dropped, film_text, imp_text):
        fails.append("a changed block was not refused")
    crlf = dict(out)
    crlf[NEW] = out[NEW].replace(b"\n", b"\r\n")
    if not invariants(crlf, film_text, imp_text):
        fails.append("a CRLF new file was not refused")
    leak = dict(out)
    leak[IMP] = out[IMP] + b"// clipboard.readText()\n"
    if not invariants(leak, film_text, imp_text):
        fails.append("a clipboard call left in an old file was not refused")
    unguarded = dict(out)
    unguarded[NEW] = out[NEW].replace(f"process.env.{GATE_ENV} !== '1'".encode(), b"false", 1)
    if unguarded[NEW] == out[NEW] or not invariants(unguarded, film_text, imp_text):
        fails.append("a new file without its guard was not refused")
    with tempfile.TemporaryDirectory(prefix="split-out-") as tmp:
        d = Path(tmp) / "out"
        first = cmd_out(d, out, film_text, imp_text)
        sentinel = b"sentinel\n"
        (d / NEW).write_bytes(sentinel)
        again = cmd_out(d, out, film_text, imp_text)
        if first != 0 or again == 0 or (d / NEW).read_bytes() != sentinel:
            fails.append("an existing --out file was not refused")
    for f in fails:
        print("split-specs selftest: " + f)
    print(f"split-specs selftest: {'ok' if not fails else 'FAILED'} (7 cases)")
    return 0 if not fails else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--out")
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    try:
        film_text, imp_text = base_text(FILM), base_text(IMP)
        out = build(film_text, imp_text)
    except SetupError as e:
        print(f"split-specs: setup: {e}")
        return 2
    if a.out:
        return cmd_out(Path(a.out), out, film_text, imp_text)
    if a.write:
        return cmd_write(out, film_text, imp_text)
    if a.check:
        return cmd_check(out, film_text, imp_text)
    return cmd_selftest(out, film_text, imp_text)


if __name__ == "__main__":
    sys.exit(main())
