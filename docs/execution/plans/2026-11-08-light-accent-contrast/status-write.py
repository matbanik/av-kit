"""Session 56 guarded status write (task rows 5 and H2-2; plan D-454; plan review round 1, F3).

`tools/meu_status.py update` loads `meu-status.yaml` and saves the whole file, and `render`
rewrites `docs/BUILD_PLAN.md` and `meu-registry.md` whole, each without a lock
(`tools/meu_status.py:131-145`, `tools/meu_status/model.py:204-225`,
`tools/meu_status/render.py:296-310`). The capture-crop session writes the same three files.
A write of theirs between that load and that save would be lost, and a diff taken afterwards
would not show it.

This run opens the three files through Windows handles that let other processes read them
but not write, replace or delete them, and holds the handles from its first read to its last
write. A write by another process inside that interval fails loudly in that process. A write
that landed before it is in the bytes read here, so it is kept. If another process already
has one of the files open for writing, the run refuses and writes nothing.

The bytes read are kept under `--keep` and staged beside them, where the status tool's own
code runs on the staged copies: `update_meu_status` and `save`, then `render_all` and
`check_drift`, with the tool's path constants pointed at the copies. Every line removed or
added must lie inside the row's own entry in `meu-status.yaml` or inside an AUTOGEN region of
the two renders, and no file's line endings may change; anything else is refused. Only then
do the staged bytes replace the three files through the held handles, and each is read back.

`--diff-out` receives the unified diff of the three files, and each changed line that doesn't
name the row is listed in the output as a disclosure (D-454).

`--verify ROW=STATUS` writes nothing. It checks that the row still holds STATUS and that the
renders match the YAML, which catches the other direction: a later save of theirs from a load
taken before this write, which would drop this session's status (H1-3, H2-5).

`--selftest` runs on copies of the three files: a write before the hold is kept, a write
during it fails in the writer, a stale save after it is caught by `--verify`, the unguarded
tool loses an interleaved write (the positive control for round 1's F3), a change outside the
row and the regions is refused with nothing written, and a file already held is refused.
"""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import difflib
import hashlib
import io
import os
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.meu_status import model, render  # noqa: E402

NAMES = ("yaml", "build_plan", "registry")
REGIONS = {"build_plan": ("phase-tracker", "summary"), "registry": ("registry",)}
SCRATCH = Path("C:/Temp/av-kit/s56")

Hook = Callable[[str, dict[str, Path]], None]


class HandleRefused(Exception):
    """A file is open for writing in another process."""


class ExclusiveHandle:
    """A read-write handle on PATH that lets other processes read it but not write, replace or delete it."""

    GENERIC_READ, GENERIC_WRITE = 0x80000000, 0x40000000
    FILE_SHARE_READ, OPEN_EXISTING = 0x1, 3

    def __init__(self, path: Path) -> None:
        self.path = path

    def __enter__(self) -> ExclusiveHandle:
        if os.name != "nt":
            raise SystemExit("FAIL: the exclusive handle needs Windows; nothing written")
        import msvcrt
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateFileW.restype = wintypes.HANDLE
        kernel32.CreateFileW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
            wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
        ]
        handle = kernel32.CreateFileW(
            str(self.path), self.GENERIC_READ | self.GENERIC_WRITE, self.FILE_SHARE_READ,
            None, self.OPEN_EXISTING, 0, None,
        )
        if handle == wintypes.HANDLE(-1).value:
            raise HandleRefused(f"WinError {ctypes.get_last_error()} opening {self.path.name}")
        self.file = os.fdopen(msvcrt.open_osfhandle(handle, os.O_RDWR | os.O_BINARY), "r+b")
        return self

    def __exit__(self, *exc: object) -> None:
        self.file.close()

    def read(self) -> bytes:
        self.file.seek(0)
        return self.file.read()

    def replace(self, raw: bytes) -> None:
        self.file.seek(0)
        self.file.truncate()
        self.file.write(raw)
        self.file.flush()
        os.fsync(self.file.fileno())


def real_files() -> dict[str, Path]:
    return {"yaml": model.DEFAULT_SSOT_PATH, "build_plan": render.BUILD_PLAN_PATH, "registry": render.REGISTRY_PATH}


@contextlib.contextmanager
def pointed_at(files: dict[str, Path]):
    """Point the status tool's path constants at FILES for the duration."""
    saved = real_files()
    model.DEFAULT_SSOT_PATH, render.BUILD_PLAN_PATH, render.REGISTRY_PATH = (files[n] for n in NAMES)
    try:
        yield
    finally:
        model.DEFAULT_SSOT_PATH, render.BUILD_PLAN_PATH, render.REGISTRY_PATH = (saved[n] for n in NAMES)


def quiet(fn: Callable[[], int]) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = fn()
    return code, out.getvalue()


def spans(name: str, lines: list[str], row: str) -> list[tuple[int, int]]:
    """Line ranges [start, end) the write may change: the row's YAML entry, or the AUTOGEN regions."""
    if name == "yaml":
        head = f"- row_key: {row}"
        if head not in lines:
            raise ValueError(f"no entry for {row}")
        start = lines.index(head)
        end = next((i for i in range(start + 1, len(lines)) if lines[i][:1] not in (" ", "")), len(lines))
        return [(start + 1, end)]
    found = []
    for region in REGIONS[name]:
        begin, end = render._begin(region), render._end(region)
        if lines.count(begin) != 1 or lines.count(end) != 1:
            raise ValueError(f"{name}: markers for {region} missing or repeated")
        found.append((lines.index(begin) + 1, lines.index(end)))
    return found


def outside(name: str, before: bytes, after: bytes, row: str) -> list[str]:
    """Each changed line that lies outside the spans the write may change."""
    a, b = before.decode("utf-8").split("\n"), after.decode("utf-8").split("\n")
    try:
        sa, sb = spans(name, a, row), spans(name, b, row)
    except ValueError as exc:
        return [str(exc)]
    inside = lambda i, ss: any(s <= i < e for s, e in ss)  # noqa: E731
    bad = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        bad += [f"{name} -{i + 1}" for i in range(i1, i2) if not inside(i, sa)]
        bad += [f"{name} +{j + 1}" for j in range(j1, j2) if not inside(j, sb)]
    crlf = (before.count(b"\r\n"), after.count(b"\r\n"))
    if crlf[0] != crlf[1]:
        bad.append(f"{name}: CRLF count {crlf[0]} became {crlf[1]}")
    return bad


def guarded_write(
    files: dict[str, Path], row: str, status: str, plan: str | None, note: str | None,
    keep: Path, diff_out: Path, hook: Hook | None = None,
) -> int:
    problems: list[str] = []
    with contextlib.ExitStack() as stack:
        try:
            handles = {n: stack.enter_context(ExclusiveHandle(files[n])) for n in NAMES}
        except HandleRefused as exc:
            print(f"FAIL: another process has a status file open for writing ({exc})")
            print("status-write: nothing written")
            return 1
        before = {n: handles[n].read() for n in NAMES}
        if keep.exists():
            shutil.rmtree(keep)
        (keep / "stage").mkdir(parents=True)
        for n in NAMES:
            (keep / files[n].name).write_bytes(before[n])
            (keep / "stage" / files[n].name).write_bytes(before[n])
        staged = {n: keep / "stage" / files[n].name for n in NAMES}
        if hook:
            hook("held", files)
        with pointed_at(staged):
            try:
                data = model.load()
                model.update_meu_status(data, row, status, plan=plan, note=note)
                model.save(data)
            except model.MeuStatusError as exc:
                problems.append(f"update refused: {exc}")
            else:
                code, out = quiet(render.render_all)
                if code:
                    problems.append(f"render exit {code}: {out.strip()[-300:]}")
                code, out = quiet(render.check_drift)
                if code:
                    problems.append(f"render --check exit {code} on the staged copies")
                meu = model.get_meu(model.load(), row)
                if meu is None or meu["status"] != status:
                    problems.append(f"the staged YAML doesn't hold {row} at {status}")
        if hook:
            hook("staged", staged)
        after = {n: staged[n].read_bytes() for n in NAMES}
        for n in NAMES:
            problems += [f"changed outside the row and the regions: {b}" for b in outside(n, before[n], after[n], row)]
        if problems:
            for problem in problems:
                print(f"FAIL: {problem}")
            print(f"status-write: {len(problems)} problem(s); nothing written")
            return 1
        for n in NAMES:
            handles[n].replace(after[n])
            if handles[n].read() != after[n]:
                problems.append(f"{files[n].name} doesn't hold the staged bytes after the write")

    disclosed, diff = [], []
    for n in NAMES:
        a, b = before[n].decode("utf-8").split("\n"), after[n].decode("utf-8").split("\n")
        for ln in difflib.unified_diff(a, b, f"{files[n].name} before", f"{files[n].name} after", n=0, lineterm=""):
            diff.append(ln)
            # The YAML's changed lines are all inside the row's entry (checked above); a render
            # line that doesn't name the row is a count or a tracker cell, and is disclosed.
            if n != "yaml" and ln[:1] in "+-" and not ln.startswith(("+++", "---")) and row not in ln:
                disclosed.append(f"{files[n].name} {ln[:1]} {ln[1:120]}")
        sha = (hashlib.sha256(before[n]).hexdigest()[:16], hashlib.sha256(after[n]).hexdigest()[:16])
        ends = (after[n].count(b"\n"), after[n].count(b"\r\n"))
        print(f"{files[n].name}: sha256 {sha[0]}… -> {sha[1]}…, LF {ends[0]}, CRLF {ends[1]}")
    diff_out.parent.mkdir(parents=True, exist_ok=True)
    diff_out.write_text("\n".join(diff) + "\n", encoding="utf-8", newline="\n")
    print(f"{files['yaml'].name}: every changed line is inside {row}'s entry")
    print(f"render lines changed that don't name {row} (disclosed, D-454): {len(disclosed)}")
    for ln in disclosed:
        print(f"  {ln}")
    for problem in problems:
        print(f"FAIL: {problem}")
    print(f"status-write: {len(problems)} problem(s); {row} -> {status}; diff {diff_out}")
    return 1 if problems else 0


def verify(files: dict[str, Path], row: str, status: str) -> int:
    with pointed_at(files):
        meu = model.get_meu(model.load(), row)
        drift, _ = quiet(render.check_drift)
    held = meu is not None and meu["status"] == status
    print(f"{row} status {meu['status'] if meu else None}; expected {status}; renders in step: {drift == 0}")
    print(f"status-write --verify: {'ok' if held and drift == 0 else 'FAIL'}")
    return 0 if held and drift == 0 else 1


def selftest() -> int:
    base = SCRATCH / "status-write-selftest"
    failures: list[str] = []
    row, other = "MEU-126", "MEU-127"

    def fresh() -> dict[str, Path]:
        if base.exists():
            shutil.rmtree(base)
        (base / "files").mkdir(parents=True)
        files = {n: base / "files" / p.name for n, p in real_files().items()}
        for n, p in real_files().items():
            files[n].write_bytes(p.read_bytes())
        return files

    def set_note(data: dict, key: str, text: str) -> None:
        meu = model.get_meu(data, key)
        assert meu is not None, key
        meu["note"] = text

    def peer_note(files: dict[str, Path], text: str) -> None:
        with pointed_at(files):
            data = model.load()
            set_note(data, other, text)
            model.save(data)

    def note_of(files: dict[str, Path], key: str) -> tuple[str, str]:
        with pointed_at(files):
            meu = model.get_meu(model.load(), key)
        return (meu["status"], meu["note"]) if meu else ("", "")

    def case(name: str, ok: bool, detail: str) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {detail}")
        if not ok:
            failures.append(name)

    def run(files: dict[str, Path], hook: Hook | None = None) -> tuple[int, str]:
        return quiet(lambda: guarded_write(
            files, row, "ready_for_review", "docs/execution/plans/x/", None, base / "keep", base / "diff.txt", hook,
        ))

    files = fresh()
    code, out = run(files)
    case("today's files change only in the row and the regions", code == 0, out.strip().splitlines()[-1])

    files = fresh()
    peer_note(files, "PEER-MARK-1")
    code, out = run(files)
    case("a write before the hold is kept", code == 0 and note_of(files, other)[1] == "PEER-MARK-1"
         and note_of(files, row)[0] == "ready_for_review", f"exit {code}, {other} {note_of(files, other)}")
    code, _ = quiet(lambda: verify(files, row, "ready_for_review"))
    case("the run's own render is in step", code == 0, f"verify exit {code}")

    files = fresh()
    blocked: list[str] = []

    def writer_during_hold(stage: str, paths: dict[str, Path]) -> None:
        if stage != "held":
            return
        for n in NAMES:
            try:
                with open(paths[n], "r+b"):
                    blocked.append(f"{n} opened")
            except PermissionError:
                blocked.append(f"{n} refused")

    code, out = run(files, writer_during_hold)
    case("a write during the hold fails in the writer", code == 0 and blocked == [f"{n} refused" for n in NAMES], f"{blocked}")
    peer_note(files, "PEER-MARK-2")
    case("the writer's retry after the hold keeps both", note_of(files, row)[0] == "ready_for_review"
         and note_of(files, other)[1] == "PEER-MARK-2", f"{note_of(files, row)[0]}, {note_of(files, other)[1]}")

    files = fresh()
    with pointed_at(files):
        stale = model.load()
    run(files)
    with pointed_at(files):
        set_note(stale, other, "PEER-MARK-3")
        model.save(stale)
    code, _ = quiet(lambda: verify(files, row, "ready_for_review"))
    case("a stale save after the write is caught by --verify", code == 1, f"verify exit {code}, {row} {note_of(files, row)[0]}")

    files = fresh()
    with pointed_at(files):
        mine = model.load()
    peer_note(files, "PEER-MARK-4")
    with pointed_at(files):
        model.update_meu_status(mine, row, "ready_for_review")
        model.save(mine)
    lost = note_of(files, other)[1] != "PEER-MARK-4"
    case("control: the unguarded tool loses an interleaved write", lost, f"{other} note after {note_of(files, other)[1]!r:.40}")

    files = fresh()
    raw = {n: p.read_bytes() for n, p in files.items()}

    def stray_edit(stage: str, paths: dict[str, Path]) -> None:
        if stage == "staged":
            text = paths["yaml"].read_bytes().replace(b"slug: svc-tts-fp16-phase-guard", b"slug: svc-tts-fp16-phase-guard-x", 1)
            paths["yaml"].write_bytes(text)

    code, out = run(files, stray_edit)
    same = all(files[n].read_bytes() == raw[n] for n in NAMES)
    case("a change outside the row and the regions is refused", code == 1 and same and "changed outside" in out,
         f"exit {code}, files unchanged {same}")

    files = fresh()
    with ExclusiveHandle(files["registry"]):
        code, out = run(files)
    same = all(files[n].read_bytes() == raw[n] for n in NAMES)
    case("a file already held for writing is refused", code == 1 and same and "nothing written" in out,
         f"exit {code}, files unchanged {same}")

    print(f"status-write selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--verify", metavar="ROW=STATUS")
    parser.add_argument("--row")
    parser.add_argument("--status")
    parser.add_argument("--plan")
    parser.add_argument("--note")
    parser.add_argument("--keep", type=Path, help="where the bytes read and the staged copies go")
    parser.add_argument("--diff-out", type=Path)
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.verify:
        row, _, status = args.verify.partition("=")
        return verify(real_files(), row, status)
    if not (args.row and args.status and args.keep and args.diff_out):
        parser.error("a write needs --row, --status, --keep and --diff-out")
    return guarded_write(real_files(), args.row, args.status, args.plan, args.note, args.keep, args.diff_out)


if __name__ == "__main__":
    sys.exit(main())
