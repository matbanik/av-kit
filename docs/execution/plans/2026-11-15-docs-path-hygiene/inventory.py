"""Session 83 inventory of the home folder's full path (implementation-plan.md §inventory.py).

Usage, from the repository root:

    python inventory.py                       # write C:/Temp/av-kit/dph/inventory.json
    python inventory.py --baseline            # row 0: write inventory-0.json (S2, S7)
    python inventory.py --write-allowlist     # row 3: write tools/home_path_allowlist.txt
    python inventory.py --check-allowlist --cross-check   # AC-8 (and AC-21 once allowlist.sha256 exists)
    python inventory.py --expect-live RECEIPT              # AC-9, the repo Red receipt
    python inventory.py --expect-evidence RECEIPT          # AC-20, the empty-allow-list receipt
    python inventory.py --selftest                         # AC-8's negatives on fixtures

It has its own pattern builder and decoder, written apart from tools/check_home_path.py's with
the same rules (§The check, steps 2a and 3), so the cross-check compares two implementations.
It lists the files ``git ls-files -z --cached --others --exclude-standard`` names, drops
``.agent/fleet/hub/`` and the secret files (execution decision D-1081) before reading anything,
and skips a missing or non-regular path. Each instance is a ``(path, line)`` pair; each file has
a kind (``own`` first, then ``handoff``, ``digest``, ``plan-folder``, ``reflection``, else
``live``) and its DIGEST (SHA-256 of the bytes with each CRLF read as LF).

Nothing it writes or prints holds the home folder or a line's text: only paths, line numbers,
kinds, counts and digests. An ``own`` instance fails every mode (S7).
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import stat
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[4]
PLAN = "docs/execution/plans/2026-11-15-docs-path-hygiene"
SCRATCH = pathlib.Path("C:/Temp/av-kit/dph")
ALLOW = "tools/home_path_allowlist.txt"
CHECK = "tools/check_home_path.py"
HUB = ".agent/fleet/hub/"

OWN = re.compile(
    r"^(?:" + re.escape(PLAN) + r"/"
    r"|\.agent/context/handoffs/2026-11-15-docs-path-hygiene-"
    r"|docs/execution/reflections/2026-11-15-docs-path-hygiene-)"
)
EVIDENCE_KINDS = (
    ("handoff", re.compile(r"^\.agent/context/handoffs/[^/]+\.md$")),
    ("digest", re.compile(r"^\.agent/context/sessions/[^/]+/digest\.md$")),
    ("plan-folder", re.compile(r"^docs/execution/plans/\d{4}-\d{2}-\d{2}-[^/]*/.+")),
    ("reflection", re.compile(r"^docs/execution/reflections/.+")),
)

#: The six live files of §Live fixes, each with the instance count and the anchor every
#: instance line must hold (bound by content; the line numbers may have moved).
LIVE_FIXES = {
    ".agent/skills/git-workflow/SKILL.md": (1, ("antigravity-ide",)),
    "_inspiration/capture-crop/design.md": (1, ('Desktop/2026-11-07_13-16-09.png"',)),
    "docs/build-plan/06-gui.md": (2, ("Downloads", "Documents")),
    "ui/tests/unit/capture-interactive.test.ts": (1, ("const INBOX_PATH = '",)),
    "ui/tests/unit/dev-spawn.test.ts": (5, ("const pythonImage = '", "liveImage: '", "oursExe: '")),
    ".agent/context/known-issues.yaml": (2, ("    root_cause: ", "    notes: ")),
}
DOC_SUFFIXES = (".md", ".markdown", ".rst", ".adoc")

HEADER = (
    "# Evidence files that hold the home folder's full path, kept byte for byte (D-817).\n"
    '# Each entry is "<sha256>  <path>": the SHA-256, lowercase hex, of the file\'s bytes with\n'
    "# each CRLF read as LF (D-997). tools/check_home_path.py exempts a listed file only while\n"
    "# its digest matches, so any change to a listed file fails the check.\n"
    "# A new entry, or a new digest for an entry, loosens the check and needs an HDP decision.\n"
    "# A file that no longer holds the path is a stale entry; remove it with\n"
    "# `uv run python tools/check_home_path.py --prune`.\n"
)


class Refused(Exception):
    pass


# --- the pattern (independent of CHECK's builder) -------------------------------------------

_STOP = "\\\\/<>:\"|?*'`\\s\\x00-\\x1f"
#: Zero or more of .,;!)]} and then a stop character or the end of the line.
_END = "(?=[.,;!)\\]}]*(?:[" + _STOP + "]|$))"


def home_regex(home: str) -> re.Pattern[str]:
    drive = re.match(r"([A-Za-z]):", home)
    if drive:
        segs = [s for s in re.split(r"[\\/]+", home[2:]) if s]
        if len(segs) < 2:
            raise Refused("the home has fewer than two segments")
        tail = "".join("[/\\\\]+" + re.escape(s) for s in segs)
        letter = re.escape(drive.group(1))
        return re.compile(
            "(?:(?<![A-Za-z])" + letter + ":" + tail + "|[/\\\\]" + letter + tail + ")" + _END, re.I
        )
    segs = [s for s in home.split("/") if s]
    if len(segs) < 2:
        raise Refused("the home has fewer than two segments")
    return re.compile("(?<![A-Za-z0-9_])" + "/+".join(re.escape(s) for s in segs) + _END)


# --- decoding (step 2a) ----------------------------------------------------------------------

_MARKS = (
    ("utf-32-le", b"\xff\xfe\x00\x00"),
    ("utf-32-be", b"\x00\x00\xfe\xff"),
    ("utf-16-le", b"\xff\xfe"),
    ("utf-16-be", b"\xfe\xff"),
    ("utf-8", b"\xef\xbb\xbf"),
)


def texts(raw: bytes) -> tuple[list[str], bool]:
    """The decoded views of RAW, and whether it is a no-mark file with a NUL byte."""
    for codec, mark in _MARKS:
        if raw[: len(mark)] == mark:
            errors = "surrogateescape" if codec == "utf-8" else "replace"
            return [raw[len(mark) :].decode(codec, errors)], False
    if raw.find(b"\0") >= 0:
        views = [raw.decode("utf-8", "surrogateescape")]
        views += [
            raw.decode(c, "replace") for c in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be")
        ]
        return views, True
    return [raw.decode("utf-8", "surrogateescape")], False


def instance_lines(raw: bytes, rx: re.Pattern[str]) -> tuple[list[int], bool]:
    views, nul = texts(raw)
    found: set[int] = set()
    for view in views:
        for number, line in enumerate(view.split("\n"), 1):
            if rx.search(line):
                found.add(number)
    return sorted(found), nul


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()


# --- the file walk ---------------------------------------------------------------------------


def secret(path: str) -> bool:
    """The secret files the session never opens (execution decision D-1081)."""
    name = path.rsplit("/", 1)[-1].lower()
    return (
        name in (".mcp.json", "mcp-token.txt", ".claude.json")
        or name == ".env"
        or name.startswith(".env.")
        or path.lower().endswith(".claude/settings.local.json")
    )


def listed(root: pathlib.Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
        check=True,
    ).stdout
    names = {n.decode("utf-8", "surrogateescape") for n in out.split(b"\0") if n}
    return sorted(n for n in names if not n.startswith(HUB) and not secret(n))


def kind_of(path: str) -> str:
    if OWN.match(path):
        return "own"
    for kind, rx in EVIDENCE_KINDS:
        if rx.match(path):
            return kind
    return "live"


def scan(root: pathlib.Path, home: str) -> dict[str, dict]:
    """Every file holding an instance: path -> kind, digest, lines, nul."""
    rx = home_regex(home)
    files: dict[str, dict] = {}
    for path in listed(root):
        full = root / path
        try:
            mode = os.lstat(full).st_mode
        except FileNotFoundError:
            continue
        if not stat.S_ISREG(mode):
            continue
        raw = full.read_bytes()
        lines, nul = instance_lines(raw, rx)
        if lines:
            files[path] = {"kind": kind_of(path), "digest": digest(raw), "lines": lines, "nul": nul}
    return files


def pairs(files: dict[str, dict], kinds: tuple[str, ...] | None = None) -> set[tuple[str, int]]:
    return {
        (p, n) for p, f in files.items() if kinds is None or f["kind"] in kinds for n in f["lines"]
    }


def evidence(files: dict[str, dict]) -> dict[str, str]:
    """EVIDENCE_SET: path -> digest, for every evidence-kind file holding an instance (never own)."""
    return {p: f["digest"] for p, f in sorted(files.items()) if f["kind"] not in ("own", "live")}


def own_problems(files: dict[str, dict]) -> list[str]:
    return [
        f"S7: this session's own file holds the path: {p}:{n}"
        for p, n in sorted(pairs(files, ("own",)))
    ]


def counts(files: dict[str, dict]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for f in files.values():
        c = out.setdefault(f["kind"], [0, 0])
        c[0] += 1
        c[1] += len(f["lines"])
    return out


def report(files: dict[str, dict]) -> None:
    for kind, (n_files, n_lines) in sorted(counts(files).items()):
        print(f"kind {kind}: files={n_files} lines={n_lines}")
    print(
        f"total: files={len(files)} lines={len(pairs(files))} nul_files={sum(f['nul'] for f in files.values())}"
    )
    for p, n in sorted(pairs(files, ("live",))):
        print(f"live {p}:{n}")


def live_problems(root: pathlib.Path, files: dict[str, dict]) -> list[str]:
    """S2: a live test, source, config or script beyond the six, or a pair the table does not name."""
    problems = []
    for path, f in sorted(files.items()):
        if f["kind"] != "live":
            continue
        if path in LIVE_FIXES:
            want, anchors = LIVE_FIXES[path]
            if len(f["lines"]) != want:
                problems.append(
                    f"S2: {path} holds {len(f['lines'])} instance line(s), the plan names {want}"
                )
            text = (root / path).read_bytes().decode("utf-8", "surrogateescape").split("\n")
            for n in f["lines"]:
                if not any(a in text[n - 1] for a in anchors):
                    problems.append(f"S2: {path}:{n} is not a line §Live fixes names")
        elif path.lower().endswith(DOC_SUFFIXES):
            print(f"D-993 live doc beyond §Live fixes (fixed in row 5): {path} lines={f['lines']}")
        else:
            problems.append(
                f"S2: live test, source, config or script beyond §Live fixes: {path} lines={f['lines']}"
            )
    return problems


# --- the allow-list and the receipts ---------------------------------------------------------


def allowlist_text(entries: dict[str, str]) -> str:
    return HEADER + "".join(f"{d}  {p}\n" for p, d in sorted(entries.items()))


def parse_allowlist(text: str) -> tuple[list[tuple[str, str]], list[str]]:
    entries, problems = [], []
    for number, line in enumerate(text.split("\n"), 1):
        if not line.strip() or line.startswith("#"):
            continue
        m = re.fullmatch(r"([0-9a-f]{64})  (\S(?:.*\S)?)", line)
        if not m:
            problems.append(f"allow-list line {number} is malformed")
            continue
        entries.append((m.group(2), m.group(1)))
    names = [p for p, _ in entries]
    if names != sorted(names) or len(set(names)) != len(names):
        problems.append("allow-list entries are not sorted and unique")
    return entries, problems


def allowlist_problems(text: str, now: dict[str, dict], row0: dict[str, dict]) -> list[str]:
    """AC-8: ALLOW lists exactly EVIDENCE_SET, each with row 0's digest, which is still current."""
    problems = []
    if "D-817" not in text or "D-997" not in text or not text.startswith("#"):
        problems.append("the allow-list header does not cite D-817 and D-997")
    if "\r" in text:
        problems.append("the allow-list is not LF")
    entries, parse = parse_allowlist(text)
    problems += parse
    listed_ = dict(entries)
    want = evidence(now)
    for p in sorted(set(want) - set(listed_)):
        problems.append(f"missing entry: {p}")
    for p in sorted(set(listed_) - set(want)):
        problems.append(f"extra entry: {p}")
    for p in sorted(set(listed_) & set(want)):
        first = row0.get(p, {}).get("digest")
        if listed_[p] != first:
            problems.append(f"digest differs from row 0's: {p}")
        if want[p] != listed_[p]:
            problems.append(f"the file changed since its entry: {p}")
    for p in sorted(listed_):
        if kind_of(p) == "own":
            problems.append(f"S7: an own file is listed: {p}")
    return problems


FOUND = re.compile(r"check_home_path: found (.+):(\d+)\s*$")


def found_pairs(text: str) -> set[tuple[str, int]]:
    out = set()
    for line in text.splitlines():
        m = FOUND.search(line)
        if m:
            out.add((m.group(1), int(m.group(2))))
    return out


def cross_problems(check_output: str, now: dict[str, dict]) -> list[str]:
    """CHECK with an empty allow-list reports exactly the pairs this inventory finds."""
    got, want = found_pairs(check_output), pairs(now)
    problems = [
        f"CHECK found a pair the inventory does not: {p}:{n}" for p, n in sorted(got - want)
    ]
    problems += [f"CHECK missed a pair the inventory finds: {p}:{n}" for p, n in sorted(want - got)]
    return problems


def _load(path: pathlib.Path) -> dict[str, dict]:
    return json.loads(path.read_text(encoding="utf-8"))["files"]


def _write_inventory(path: pathlib.Path, files: dict[str, dict], root: pathlib.Path) -> None:
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    record = {
        "head": head,
        "counts": {k: {"files": v[0], "lines": v[1]} for k, v in sorted(counts(files).items())},
        "files": files,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(record, indent=1, sort_keys=True) + "\n").encode("utf-8"))
    print("wrote", path.as_posix())


def _run_check_empty(root: pathlib.Path) -> tuple[int, str]:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    empty = SCRATCH / "cross-check-empty-allowlist.txt"
    empty.write_bytes(b"")
    result = subprocess.run(
        [sys.executable, str(root / CHECK), "--repo", str(root), "--allowlist", str(empty)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout + result.stderr


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    root = ROOT
    home = str(pathlib.Path.home())
    files = scan(root, home)
    report(files)
    problems = own_problems(files)
    inv0_path = SCRATCH / "inventory-0.json"
    if not argv:
        _write_inventory(SCRATCH / "inventory.json", files, root)
    elif argv == ["--baseline"]:
        problems += live_problems(root, files)
        evid = evidence(files)
        print(f"EVIDENCE_SET at row 0: {len(evid)} file(s) (the plan counted 60)")
        print(f"live pairs at row 0: {len(pairs(files, ('live',)))} (the plan counted 12)")
        _write_inventory(inv0_path, files, root)
        _write_inventory(SCRATCH / "inventory.json", files, root)
    elif argv == ["--write-allowlist"]:
        row0 = _load(inv0_path)
        entries = {}
        for p, d in evidence(files).items():
            if p not in row0:
                problems.append(f"S4: {p} holds the path but was not in inventory-0.json")
            elif row0[p]["digest"] != d:
                problems.append(f"S4: {p} changed since row 0")
            else:
                entries[p] = row0[p]["digest"]
        target = root / ALLOW
        text = allowlist_text(entries)
        if target.exists() and target.read_bytes() != text.encode("utf-8"):
            problems.append(f"{ALLOW} exists with other content")
        if not problems:
            target.write_bytes(text.encode("utf-8"))
            print(f"wrote {ALLOW}: {len(entries)} entries")
            for kind, (n, _) in sorted(counts({p: files[p] for p in entries}).items()):
                print(f"  entries of kind {kind}: {n}")
    elif argv == ["--check-allowlist", "--cross-check"]:
        row0 = _load(inv0_path)
        raw = (root / ALLOW).read_bytes()
        problems += allowlist_problems(raw.decode("utf-8"), files, row0)
        print(
            f"allow-list entries: {len(parse_allowlist(raw.decode('utf-8'))[0])}; EVIDENCE_SET now: {len(evidence(files))}"
        )
        code, out = _run_check_empty(root)
        print(
            f"CHECK with an empty allow-list: exit={code} found={len(found_pairs(out))}; inventory pairs={len(pairs(files))}"
        )
        if code != (1 if files else 0):
            problems.append(f"CHECK with an empty allow-list exited {code}")
        problems += cross_problems(out, files)
        pinned = root / PLAN / "allowlist.sha256"
        if pinned.exists():
            want = pinned.read_text(encoding="utf-8").strip()
            got = hashlib.sha256(raw).hexdigest()
            print(f"allowlist.sha256 {'matches' if got == want else 'DIFFERS'}")
            if got != want:
                problems.append("AC-21: the allow-list's SHA-256 differs from allowlist.sha256")
    elif len(argv) == 2 and argv[0] == "--expect-live":
        text = pathlib.Path(argv[1]).read_text(encoding="utf-8", errors="replace")
        live0 = pairs(_load(inv0_path), ("live",))
        got = found_pairs(text)
        problems += [f"AC-9: an extra found pair: {p}:{n}" for p, n in sorted(got - live0)]
        problems += [f"AC-9: a missing found pair: {p}:{n}" for p, n in sorted(live0 - got)]
        if re.search(r"check_home_path: (stale|changed) ", text):
            problems.append("AC-9: the repo Red holds a stale or changed line")
        if not re.search(r"check_home_path: refused found=\d+ changed=0 stale=0", text):
            problems.append("AC-9: no 'refused found=<n> changed=0 stale=0' line")
        print(f"repo Red found={len(got)} LIVE_SET={len(live0)}")
    elif len(argv) == 2 and argv[0] == "--expect-evidence":
        text = pathlib.Path(argv[1]).read_text(encoding="utf-8", errors="replace")
        got = found_pairs(text)
        evid = set(evidence(files))
        allow_paths = {p for p, _ in parse_allowlist((root / ALLOW).read_text(encoding="utf-8"))[0]}
        got_files = {p for p, _ in got}
        if got_files != evid or evid != allow_paths:
            problems.append(
                f"AC-20: found files {len(got_files)}, EVIDENCE_SET {len(evid)}, allow-list {len(allow_paths)}: "
                f"extra {sorted(got_files - evid)} missing {sorted(evid - got_files)}"
            )
        if got != pairs(files, ("handoff", "digest", "plan-folder", "reflection")):
            problems.append(
                "AC-20: the empty-list found pairs differ from the inventory's evidence pairs"
            )
        if pairs(files, ("live",)):
            problems.append(f"AC-20: live pairs remain: {sorted(pairs(files, ('live',)))}")
        print(
            f"empty-list run found files={len(got_files)} pairs={len(got)} EVIDENCE_SET={len(evid)}"
        )
    else:
        print(
            "usage: inventory.py [--baseline | --write-allowlist | --check-allowlist --cross-check | --expect-live R | --expect-evidence R | --selftest]"
        )
        return 2
    for p in problems:
        print("PROBLEM:", p)
    print(f"inventory: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


# --- selftest (AC-8's negatives) -------------------------------------------------------------


def _git_env(tmp: pathlib.Path) -> dict[str, str]:
    env = dict(os.environ)
    cfg = tmp / "global.gitconfig"
    cfg.touch()
    env.update(
        GIT_CONFIG_GLOBAL=str(cfg), GIT_CONFIG_NOSYSTEM="1", GIT_CEILING_DIRECTORIES=str(tmp)
    )
    return env


def selftest() -> int:
    home = "C:\\Users\\fixture"
    failures: list[str] = []

    def expect(name: str, problems: list[str], refused: bool) -> None:
        ok = bool(problems) == refused
        print(
            f"{name}: {'refused' if problems else 'accepted'} (expected {'refused' if refused else 'accepted'}) {problems[:2]}"
        )
        if not ok:
            failures.append(name)

    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t)
        root = tmp / "repo"
        root.mkdir()
        env = _git_env(tmp)
        subprocess.run(["git", "-C", str(root), "init", "-q"], env=env, check=True)
        content = {
            ".agent/context/handoffs/2026-01-01-a-handoff.md": b"one\r\npath C:\\Users\\fixture\\x\r\n",
            "docs/execution/plans/2026-01-02-b/notes.md": b"C:/Users/fixture/y\nC:/Users/fixtures/z\n",
            ".agent/context/sessions/s1/digest.md": b"x\n/c/Users/fixture/q\n",
            "docs/live.md": b"no\nyes C:\\Users\\fixture.\n",
            "docs/clean.md": b"C:\\Users\\fixture.other\\a\n",
            ".agent/fleet/hub/x.md": b"C:\\Users\\fixture\\hub\n",
            "u16.txt": "a\nb\nC:/Users/fixture/a\n".encode("utf-16-le"),
        }
        for rel, raw in content.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes(raw)
        old = os.environ.copy()
        os.environ.update(env)
        try:
            files = scan(root, home)
        finally:
            os.environ.clear()
            os.environ.update(old)
        kinds = {p: (f["kind"], f["lines"]) for p, f in files.items()}
        want = {
            ".agent/context/handoffs/2026-01-01-a-handoff.md": ("handoff", [2]),
            "docs/execution/plans/2026-01-02-b/notes.md": ("plan-folder", [1]),
            ".agent/context/sessions/s1/digest.md": ("digest", [2]),
            "docs/live.md": ("live", [2]),
            "u16.txt": ("live", [3]),
        }
        print("scan:", kinds)
        if kinds != want:
            failures.append(f"scan: {kinds} != {want}")
        good = allowlist_text(evidence(files))
        expect("allowlist-correct", allowlist_problems(good, files, files), False)
        entries = dict(sorted(evidence(files).items()))
        first = next(iter(entries))
        missing = {k: v for k, v in entries.items() if k != first}
        expect(
            "allowlist-missing-entry",
            allowlist_problems(allowlist_text(missing), files, files),
            True,
        )
        extra = {**entries, "docs/execution/plans/2026-01-03-c/x.md": "0" * 64}
        expect(
            "allowlist-extra-entry", allowlist_problems(allowlist_text(extra), files, files), True
        )
        row0 = json.loads(json.dumps(files))
        row0[first]["digest"] = "1" * 64
        expect("allowlist-digest-differs-from-row-0", allowlist_problems(good, files, row0), True)
        expect(
            "allowlist-no-header",
            allowlist_problems(good.replace("D-817", "D-000"), files, files),
            True,
        )
        full = "".join(f"check_home_path: found {p}:{n}\n" for p, n in sorted(pairs(files)))
        expect("cross-check-exact", cross_problems(full, files), False)
        dropped = "".join(full.splitlines(keepends=True)[1:])
        expect("cross-check-check-output-drops-a-line", cross_problems(dropped, files), True)
        # An own fixture: reported as own, fails, and is never written to the allow-list.
        for rel in (
            f"{PLAN}/notes.md",
            ".agent/context/handoffs/2026-11-15-docs-path-hygiene-plan-critical-review.md",
        ):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes(b"C:\\Users\\fixture\\own\n")
            os.environ.update(env)
            try:
                with_own = scan(root, home)
            finally:
                os.environ.clear()
                os.environ.update(old)
            kind = with_own.get(rel, {}).get("kind")
            print(f"own fixture {rel}: kind={kind}")
            if kind != "own":
                failures.append(f"own fixture {rel} is {kind}")
            expect(f"own-fails:{rel}", own_problems(with_own), True)
            if rel in evidence(with_own):
                failures.append(f"own fixture {rel} would be written to the allow-list")
            (root / rel).unlink()
        try:
            home_regex("C:\\Users")
            failures.append("a one-segment home was accepted")
        except Refused:
            print("short-home: refused (expected refused)")
    for f in failures:
        print("SELFTEST FAIL:", f)
    print(f"inventory selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
