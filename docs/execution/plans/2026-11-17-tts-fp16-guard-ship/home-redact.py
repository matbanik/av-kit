"""Session 74 home-prefix redaction (task rows 2, 3, 7, 8 and H1-6, and the gate's
``home-redact-selftest`` step; implementation-plan.md §Verification Plan 3, S16; Session 73
RULE-1).

Every form of the home folder's prefix is replaced with ``<HOME>``: the drive form with
backslashes, with forward slashes and JSON-escaped (doubled backslashes), and the Git Bash forms
(``/c/...``, ``/mnt/c/...``), each matched case-insensitively and only where the last segment
ends (the next character is not a letter, digit, ``_`` or ``-``). The home comes from
``Path.home()``; this file holds none.

Usage, from the repository root::

    python home-redact.py RAW OUT          # write OUT redacted, delete RAW; 1 if a form is left
    python home-redact.py --in-place JSON  # rewrite a JSON file; it must still parse
    python home-redact.py --scan-cited HANDOFF --scan-dir DIR
        # every ff-* receipt name HANDOFF cites must exist under DIR and hold no form; the
        # handoff itself, and any other cited .txt/.json name found under DIR, are scanned too
    python home-redact.py --selftest

Nothing this script prints holds the home folder.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path, PureWindowsPath

MARK = b"<HOME>"
CITED_FF = re.compile(r"\bff-[A-Za-z0-9_.-]*?\.(?:txt|json|exit|log)\b")
CITED_OTHER = re.compile(r"(?<![A-Za-z0-9_.-])[A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:txt|json)\b")


def forms(home: str) -> list[str]:
    """The textual forms of HOME, longest first."""
    win = PureWindowsPath(home)
    drive = win.drive.rstrip(":")
    parts = [p for p in win.parts[1:]]
    if not drive or len(parts) < 2:
        raise SystemExit("home-redact: the home folder must be a drive path two segments deep")
    out = [
        f"{drive}:\\\\" + "\\\\".join(parts),
        f"{drive}:\\" + "\\".join(parts),
        f"{drive}:/" + "/".join(parts),
        f"/mnt/{drive.lower()}/" + "/".join(parts),
        f"/{drive.lower()}/" + "/".join(parts),
    ]
    return sorted(set(out), key=len, reverse=True)


def pattern(home: str) -> re.Pattern[bytes]:
    alts = b"|".join(re.escape(f.encode("utf-8")) for f in forms(home))
    return re.compile(b"(?:" + alts + b")(?![A-Za-z0-9_-])", re.IGNORECASE)


def redact(raw: bytes, home: str) -> tuple[bytes, int]:
    return pattern(home).subn(MARK, raw)


def hits(raw: bytes, home: str) -> int:
    return len(pattern(home).findall(raw))


def redact_file(raw_path: Path, out_path: Path, home: str) -> int:
    if not raw_path.is_file():
        print(f"home-redact: FAIL: no raw file {raw_path.name}")
        return 1
    raw = raw_path.read_bytes()
    out, n = redact(raw, home)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(out)
    left = hits(out_path.read_bytes(), home)
    raw_path.unlink()
    print(f"home-redact: {out_path.name}: {n} replaced, {left} left, raw deleted")
    return 1 if left or raw_path.exists() else 0


def redact_json(path: Path, home: str) -> int:
    if not path.is_file():
        print(f"home-redact: FAIL: no file {path.name}")
        return 1
    raw = path.read_bytes()
    out, n = redact(raw, home)
    try:
        json.loads(out.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(
            f"home-redact: FAIL: {path.name} would not parse after redaction ({type(exc).__name__})"
        )
        return 1
    if out != raw:
        path.write_bytes(out)
    left = hits(path.read_bytes(), home)
    print(f"home-redact: {path.name}: {n} replaced in place, {left} left, parses")
    return 1 if left else 0


def scan_cited(handoff: Path, scan_dir: Path, home: str) -> int:
    if not handoff.is_file():
        print(f"home-redact: FAIL: no handoff {handoff.name}")
        return 1
    text_raw = handoff.read_bytes()
    text = text_raw.decode("utf-8", errors="replace")
    cited_ff = sorted(set(CITED_FF.findall(text)))
    others = sorted(
        n for n in set(CITED_OTHER.findall(text)) - set(cited_ff) if (scan_dir / n).is_file()
    )
    problems: list[str] = []
    if hits(text_raw, home):
        problems.append(f"{handoff.name}: holds the home prefix")
    for name in cited_ff:
        path = scan_dir / name
        if not path.is_file():
            problems.append(f"{name}: cited but missing under the scan folder")
            continue
        if hits(path.read_bytes(), home):
            problems.append(f"{name}: holds the home prefix")
    for name in others:
        if hits((scan_dir / name).read_bytes(), home):
            problems.append(f"{name}: holds the home prefix")
    for problem in problems:
        print(f"home-redact: FAIL: {problem}")
    print(
        f"home-redact scan: {len(cited_ff)} cited ff receipt(s), {len(others)} other cited "
        f"file(s), the handoff, {len(problems)} problem(s)"
    )
    return 1 if problems else 0


def selftest() -> int:
    home = "C:\\Users\\Someone"
    wrong: list[str] = []
    cases = 0

    def expect(name: str, ok: bool) -> None:
        nonlocal cases
        cases += 1
        print(f"{name}: {'ok' if ok else 'WRONG'}")
        if not ok:
            wrong.append(name)

    for label, text in (
        ("backslash", b"at C:\\Users\\Someone\\x.txt"),
        ("forward", b"at C:/Users/Someone/x.txt"),
        ("json-escaped", b'{"p": "C:\\\\Users\\\\Someone\\\\x"}'),
        ("lower-case", b"at c:\\users\\someone\\x"),
        ("git-bash", b"at /c/Users/Someone/x"),
        ("wsl", b"at /mnt/c/Users/Someone/x"),
        ("end-of-text", b"home is C:\\Users\\Someone"),
        ("quoted", b"'C:/Users/Someone'"),
    ):
        out, n = redact(text, home)
        expect(f"redact-{label}", n == 1 and hits(out, home) == 0 and MARK in out)
    out, n = redact(b"C:\\Users\\Someone2\\x and C:\\Users\\Someone-old", home)
    expect("no-redact-longer-name", n == 0)
    out, n = redact(b"C:\\Users\\Other\\x", home)
    expect("no-redact-other-user", n == 0)

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        raw = base / "raw.txt"
        raw.write_bytes(b"line C:\\Users\\Someone\\a\r\nline two\r\n")
        out_path = base / "out.txt"
        code = redact_file(raw, out_path, home)
        expect(
            "file-redacted-raw-deleted",
            code == 0
            and not raw.exists()
            and out_path.read_bytes() == b"line <HOME>\\a\r\nline two\r\n",
        )
        expect("file-missing-raw", redact_file(base / "nope.txt", out_path, home) == 1)

        js = base / "smoke.json"
        js.write_bytes(json.dumps({"d": "C:\\Users\\Someone\\run"}).encode())
        code = redact_json(js, home)
        expect(
            "json-in-place",
            code == 0 and json.loads(js.read_text(encoding="utf-8"))["d"] == "<HOME>\\run",
        )
        bad = base / "bad.json"
        bad.write_bytes(b"{not json C:/Users/Someone}")
        expect("json-not-parsing", redact_json(bad, home) == 1)

        scan = base / "scan"
        scan.mkdir()
        (scan / "ff-a.txt").write_bytes(b"clean\n")
        (scan / "ff-b.json").write_bytes(b'{"x": "<HOME>"}\n')
        (scan / "other.txt").write_bytes(b"clean\n")
        handoff = base / "handoff.md"
        handoff.write_bytes(b"See `ff-a.txt`, `ff-b.json`, other.txt and loop ff-execution-x.\n")
        expect("scan-clean", scan_cited(handoff, scan, home) == 0)
        (scan / "ff-a.txt").write_bytes(b"at C:\\Users\\Someone\\q\n")
        expect("scan-hit", scan_cited(handoff, scan, home) == 1)
        (scan / "ff-a.txt").write_bytes(b"clean\n")
        (scan / "other.txt").write_bytes(b"at C:/Users/Someone/q\n")
        expect("scan-other-hit", scan_cited(handoff, scan, home) == 1)
        (scan / "other.txt").write_bytes(b"clean\n")
        handoff.write_bytes(b"See `ff-a.txt` and `ff-missing.txt`.\n")
        expect("scan-missing", scan_cited(handoff, scan, home) == 1)
        handoff.write_bytes(b"See `ff-a.txt` at C:\\Users\\Someone.\n")
        expect("scan-handoff-hit", scan_cited(handoff, scan, home) == 1)
    print(f"home-redact selftest: {cases} case(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def main(argv: list[str]) -> int:
    home = str(Path.home())
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) == 2 and argv[0] == "--in-place":
        return redact_json(Path(argv[1]), home)
    if len(argv) == 4 and argv[0] == "--scan-cited" and argv[2] == "--scan-dir":
        return scan_cited(Path(argv[1]), Path(argv[3]), home)
    if len(argv) == 2 and not argv[0].startswith("-"):
        return redact_file(Path(argv[0]), Path(argv[1]), home)
    print("usage: home-redact.py RAW OUT | --in-place JSON | --scan-cited HANDOFF --scan-dir DIR")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
