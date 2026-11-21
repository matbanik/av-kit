"""Session 99 row checks (task rows 2 to 9 and the gate; implementation-plan.md §Verification Plan).

Subcommands (each exits 0 when it finds no problem, 1 when it does, 2 on a usage error):

* ``skill``: AC-162.15. Each vendored skill file's SHA-256 equals the creative-writing copy's,
  the vendored folder holds those files and ``UPSTREAM.md`` only, ``LICENSE`` is the MIT text,
  and ``UPSTREAM.md`` names the upstream URL, the full commit and the MIT licence.
* ``red-record --row N FILE ...``: writes the files' SHA-256 under the row in
  ``hq-red-hashes.json`` and copies their bytes to ``hq-red-copies/row<N>/``. A row already
  recorded with other hashes is refused (a Red file never changes after its row).
* ``red-unchanged``: every file in ``hq-red-hashes.json`` still has its recorded hash.
* ``pins-unchanged``: every ``baseline-pins.json`` file hash, except
  ``ui/tests/unit/failure-reason-copy.test.ts`` (D-1290 A changes it in row 4, and
  ``red-unchanged`` covers it from then).
* ``only-failing --id ID [--id ID ...] RECEIPT``: the Vitest receipt fails exactly the named
  ids, each by an assertion, and passes every other test it lists; an id matches a title that
  starts with it plus a space. The summary's failed count equals those failures, and no test is
  skipped or todo.
* ``shots``: row 8. The manifest has one entry per shot of ``quick-start.json`` and no other,
  each file exists at 153,600 bytes or fewer with the manifest's byte count and its WebP header
  giving the manifest's width (1280 or less) and height (900 or less), ``assets/help/`` holds
  nothing else, both generator logs hold one ``privacy: clean <name>-<theme>`` line per file,
  no ``privacy: blocked`` line and one ``isolation: ok`` line per launch (pages x 2 themes),
  and the second run's manifest has the first run's ``stepsHash``, ``width`` and ``height``.
* ``assets-record OUT``: writes every ``assets/help/`` file's SHA-256 to ``OUT``.
* ``neg-stage OUT``: copies ``stage.ts`` to ``OUT`` with the Settings download path (the one
  ``path: 'D:\\\\Media\\\\av-kit',`` line of the downloader settings seed) set to
  ``C:\\\\Users\\\\alex\\\\Videos``; refuses when that line is not found exactly once.
* ``assets-unchanged BEFORE --neg-receipt R --neg-exit N``: ``N`` is 1, ``R`` holds the line
  ``privacy: blocked settings-download-light``, and every ``assets/help/`` file is at its
  ``BEFORE`` hash with none added or removed.
* ``e2e-count RECEIPT N [--plain RECEIPT ...]``: the first receipt has ``N`` lines matching
  ``^ +ok +[0-9]+ .*AC-162\\.`` and an ``N passed`` line; each ``--plain`` receipt has a pass
  count; no receipt has a ``failed``, ``flaky`` or ``unhandled rejection:`` line.
* ``--selftest``: every subcommand on fixtures in a temporary folder.

The Vitest block grammar is red-check.py's, loaded by path.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import re
import struct
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RECEIPTS = pathlib.Path("C:/Temp/av-kit/help-quick-start")
SKILL_SRC = pathlib.Path("P:/creative-writing/.agent/skills/asd-ste100")
SKILL_DST = ROOT / ".agent/skills/asd-ste100"
SKILL_FILES = (
    "SKILL.md",
    "LICENSE",
    "references/writing-rules.md",
    "examples/before-after.md",
    "examples/linter-edge-cases.md",
    "scripts/ste-lint.py",
)
UPSTREAM_URL = "https://github.com/danyuchn/asd-ste100-skill"
UPSTREAM_COMMIT = "32511c6992ecb5f1971e46a2943f2e6adceedafe"
MIT_MARKS = (
    "MIT License",
    "Permission is hereby granted, free of charge",
    'THE SOFTWARE IS PROVIDED "AS IS"',
)
ASSETS = ROOT / "ui/src/renderer/src/assets/help"
QUICK_START = ROOT / "ui/src/renderer/src/components/help/quick-start.json"
STAGE = ROOT / "ui/tests/help-shots/stage.ts"
PINS = HERE / "baseline-pins.json"
PIN_SKIP = "ui/tests/unit/failure-reason-copy.test.ts"
THEMES = ("light", "dark")
MAX_BYTES = 153_600
MAX_W, MAX_H = 1280, 900
MANIFEST_KEYS = {"name", "page", "width", "height", "bytes", "stepsHash"}
# Row 5 wrote the Settings download path as ``path: media,`` (the seam takes MEDIA as an argument),
# so the plant matches that one line and writes a quoted literal in its place.
NEG_LINE = re.compile(r"^(\s*path: )media(,?)\s*$")
NEG_VALUE = "C:\\\\Users\\\\alex\\\\Videos"
NEG_BLOCKED = re.compile(r"(?<![\w-])privacy: blocked settings-download-light(?![\w-])")
OK_LINE = re.compile(r"^ +ok +[0-9]+ .*AC-162\.")
PASSED = re.compile(r"^\s*(\d+) passed\b")
E2E_BAD = re.compile(r"^\s*\d+ (?:failed|flaky)\b|unhandled rejection:", re.IGNORECASE)
# Vitest's per-test lines: the real glyphs and their cp437 mojibake (Γ£ô is ✓, ├ù is ×, Γåô is ↓).
VITEST_TEST = re.compile(r"^\s+(✓|Γ£ô|×|├ù|↓|Γåô)\s+(.+?)(?:\s+\d+ms)?\s*$")
PASS_MARKS = ("✓", "Γ£ô")
FAIL_MARKS = ("×", "├ù")


def _load_red_check():
    spec = importlib.util.spec_from_file_location("hq_red_check", HERE / "red-check.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["hq_red_check"] = module
    spec.loader.exec_module(module)
    return module


rc = _load_red_check()


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: pathlib.Path, root: pathlib.Path) -> str:
    path = path if path.is_absolute() else root / path
    return path.resolve().relative_to(root.resolve()).as_posix()


# --- skill (AC-162.15)
def skill(src: pathlib.Path, dst: pathlib.Path) -> list[str]:
    problems: list[str] = []
    for name in SKILL_FILES:
        a, b = src / name, dst / name
        if not a.is_file() or not b.is_file():
            problems.append(f"skill: {name}: source {a.is_file()}, vendored {b.is_file()}")
            continue
        got, want = sha(b), sha(a)
        print(f"skill {name} {got[:16]} {'==' if got == want else '!='} {want[:16]}")
        if got != want:
            problems.append(f"skill: {name} differs from the creative-writing copy")
    allowed = {*SKILL_FILES, "UPSTREAM.md"}
    extra = sorted(
        p.relative_to(dst).as_posix()
        for p in dst.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    )
    for name in extra:
        if name not in allowed:
            problems.append(f"skill: unexpected vendored file {name}")
    lic = dst / "LICENSE"
    if lic.is_file():
        text = lic.read_text(encoding="utf-8")
        for mark in MIT_MARKS:
            if mark not in text:
                problems.append(f"skill: LICENSE lacks {mark!r}")
    up = dst / "UPSTREAM.md"
    if not up.is_file():
        problems.append("skill: UPSTREAM.md missing")
    else:
        text = up.read_text(encoding="utf-8")
        for mark in (UPSTREAM_URL, UPSTREAM_COMMIT, "MIT"):
            if mark not in text:
                problems.append(f"skill: UPSTREAM.md lacks {mark!r}")
    return problems


# --- red-record, red-unchanged, pins-unchanged
def red_record(row: int, files: list[str], root: pathlib.Path, store: pathlib.Path) -> list[str]:
    record = store / "hq-red-hashes.json"
    data = json.loads(record.read_text(encoding="utf-8")) if record.is_file() else {}
    entry: dict[str, str] = {}
    for f in files:
        p = pathlib.Path(f)
        p = p if p.is_absolute() else root / p
        if not p.is_file():
            return [f"red-record: {f} is not a file"]
        entry[rel(p, root)] = sha(p)
    key = str(row)
    if key in data and data[key] != entry:
        return [f"red-record: row {row} is already recorded with other hashes: {data[key]}"]
    for name in entry:
        dest = store / "hq-red-copies" / f"row{row}" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((root / name).read_bytes())
    data[key] = entry
    store.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for name, h in entry.items():
        print(f"red-record row {row}: {name} {h}")
    return []


def red_unchanged(root: pathlib.Path, store: pathlib.Path) -> list[str]:
    record = store / "hq-red-hashes.json"
    if not record.is_file():
        return [f"red-unchanged: {record} missing"]
    data = json.loads(record.read_text(encoding="utf-8"))
    problems: list[str] = []
    count = 0
    for row, entry in sorted(data.items()):
        for name, want in sorted(entry.items()):
            p = root / name
            got = sha(p) if p.is_file() else "absent"
            count += 1
            print(f"red-unchanged row {row}: {name} {'ok' if got == want else 'CHANGED'}")
            if got != want:
                problems.append(f"red-unchanged: {name} (row {row}) is {got[:16]}, not {want[:16]}")
    if not count:
        problems.append("red-unchanged: no file recorded")
    return problems


def pins_unchanged(root: pathlib.Path, pins: pathlib.Path) -> list[str]:
    files = json.loads(pins.read_text(encoding="utf-8"))["files"]
    problems: list[str] = []
    checked = 0
    for name, want in sorted(files.items()):
        if name == PIN_SKIP:
            print(f"pins-unchanged: {name} skipped (red-unchanged covers it from row 4)")
            continue
        p = root / name
        got = sha(p) if p.is_file() else "absent"
        checked += 1
        print(f"pins-unchanged: {name} {'ok' if got == want else 'CHANGED'}")
        if got != want:
            problems.append(f"pins-unchanged: {name} is {got[:16]}, not {want[:16]}")
    if not checked:
        problems.append("pins-unchanged: no pin file recorded")
    return problems


# --- only-failing
def _starts(title: str, wanted: str) -> bool:
    # Row 7 (Session 99): the real titles write `AC-162.4 figures: ...`, so a colon ends an id
    # as a space does. `AC-162.1` still never matches `AC-162.10 ...`.
    return title.startswith((wanted + " ", wanted + ":"))


def only_failing(ids: list[str], receipt: pathlib.Path) -> list[str]:
    text = rc.ANSI_ESCAPE.sub("", receipt.read_text(encoding="utf-8", errors="replace"))
    lines = text.splitlines()
    problems: list[str] = []
    failed: list[str] = []
    passed: list[str] = []
    for line in lines:
        m = VITEST_TEST.match(line)
        if not m or m.group(2).startswith("tests/"):
            continue
        mark, title = m.group(1), m.group(2)
        if mark in PASS_MARKS:
            passed.append(title)
        elif mark in FAIL_MARKS:
            failed.append(title)
        else:
            problems.append(f"only-failing: skipped test {title}")
    for title in failed:
        if not any(_starts(title, i) for i in ids):
            problems.append(f"only-failing: {title} fails, but it is not a named id")
    for i in ids:
        if not any(_starts(t, i) for t in failed):
            problems.append(f"only-failing: {i} does not fail")
    blocks = rc._blocks("vitest", lines)
    block_titles = [t.split(" > ")[-1].strip() for b in blocks for t in b.titles]
    for b in blocks:
        names = [t.split(" > ")[-1].strip() for t in b.titles]
        if not b.diagnostics or any(kind != "assertion" for _, kind in b.diagnostics):
            problems.append(
                f"only-failing: {names} failed by something other than an assertion: "
                f"{[c[:80] for c, _ in b.diagnostics]}"
            )
    if sorted(block_titles) != sorted(failed):
        problems.append(
            f"only-failing: FAIL blocks {block_titles} do not match the × lines {failed}"
        )
    summary = [m.group(1) for line in lines if (m := rc.VITEST_SUMMARY.match(line))]
    counts = rc._summary_counts(text).get("vitest", (0, 0))
    if counts[0] != len(failed):
        problems.append(
            f"only-failing: the summary fails {counts[0]}, the receipt lists {len(failed)}"
        )
    for s in summary:
        if re.search(r"\b(skipped|todo)\b", s):
            problems.append(f"only-failing: the summary has a skipped or todo test: {s}")
    if not summary:
        problems.append("only-failing: no Tests summary line")
    print(f"only-failing: {len(failed)} failing {failed}; {len(passed)} listed passing; {summary}")
    return problems


# --- shots, assets-record, neg-stage, assets-unchanged
def webp_size(raw: bytes) -> tuple[int, int] | None:
    if len(raw) < 30 or raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
        return None
    kind = raw[12:16]
    if kind == b"VP8 " and raw[23:26] == b"\x9d\x01\x2a":
        w, h = struct.unpack("<HH", raw[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if kind == b"VP8L" and raw[20] == 0x2F:
        bits = int.from_bytes(raw[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if kind == b"VP8X":
        return int.from_bytes(raw[24:27], "little") + 1, int.from_bytes(raw[27:30], "little") + 1
    return None


def _manifest_entries(path: pathlib.Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data["shots"] if isinstance(data, dict) else data
    if not isinstance(entries, list):
        raise ValueError(f"{path}: the manifest is not a list of shots")
    return entries


def _expected_shots(quick_start: pathlib.Path) -> tuple[dict[str, str], int]:
    pages = json.loads(quick_start.read_text(encoding="utf-8"))["pages"]
    shots = {s["name"]: page for page, data in pages.items() for s in data["shots"]}
    return shots, len(pages)


def shots(
    assets: pathlib.Path,
    quick_start: pathlib.Path,
    logs: list[pathlib.Path],
    manifest_1: pathlib.Path,
) -> list[str]:
    problems: list[str] = []
    expected, page_count = _expected_shots(quick_start)
    entries = _manifest_entries(assets / "manifest.json")
    names = [e.get("name") for e in entries]
    if sorted(names) != sorted(expected) or len(set(names)) != len(names):
        problems.append(f"shots: manifest names {sorted(names)}, quick start {sorted(expected)}")
    files = {"manifest.json"}
    for e in entries:
        name = e.get("name")
        if set(e) != MANIFEST_KEYS:
            problems.append(f"shots: {name}: keys {sorted(e)}, not {sorted(MANIFEST_KEYS)}")
            continue
        if expected.get(name) != e["page"]:
            problems.append(f"shots: {name}: page {e['page']}, quick start {expected.get(name)}")
        w, h = e["width"], e["height"]
        if not (isinstance(w, int) and isinstance(h, int) and 0 < w <= MAX_W and 0 < h <= MAX_H):
            problems.append(f"shots: {name}: size {w}x{h} out of range")
        if not isinstance(e["stepsHash"], str) or not e["stepsHash"]:
            problems.append(f"shots: {name}: no stepsHash")
        for theme in THEMES:
            fname = f"{name}-{theme}.webp"
            files.add(fname)
            p = assets / fname
            if not p.is_file():
                problems.append(f"shots: {fname} missing")
                continue
            raw = p.read_bytes()
            dims = webp_size(raw)
            print(
                f"shot {fname}: {len(raw)} bytes, {dims}, manifest {w}x{h} {e['bytes'].get(theme)}"
            )
            if len(raw) > MAX_BYTES:
                problems.append(f"shots: {fname} is {len(raw)} bytes (> {MAX_BYTES})")
            if e["bytes"].get(theme) != len(raw):
                problems.append(
                    f"shots: {fname} is {len(raw)} bytes, manifest {e['bytes'].get(theme)}"
                )
            if dims != (w, h):
                problems.append(f"shots: {fname} header {dims}, manifest {w}x{h}")
    on_disk = {p.relative_to(assets).as_posix() for p in assets.rglob("*") if p.is_file()}
    for extra in sorted(on_disk - files):
        problems.append(f"shots: unexpected file assets/help/{extra}")
    launches = page_count * len(THEMES)
    for log in logs:
        text = log.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        for name in expected:
            for theme in THEMES:
                tag = re.compile(rf"(?<![\w-])privacy: clean {re.escape(name)}-{theme}(?![\w-])")
                n = sum(1 for line in lines if tag.search(line))
                if n != 1:
                    problems.append(f"shots: {log.name}: {n} 'privacy: clean {name}-{theme}' lines")
        blocked = [line.strip() for line in lines if "privacy: blocked" in line]
        if blocked:
            problems.append(f"shots: {log.name}: {blocked}")
        iso = sum(1 for line in lines if re.search(r"(?<![\w-])isolation: ok\b", line))
        print(f"shots {log.name}: isolation ok {iso} (launches {launches})")
        if iso != launches:
            problems.append(f"shots: {log.name}: {iso} 'isolation: ok' lines, {launches} launches")
    first = {e.get("name"): e for e in _manifest_entries(manifest_1)}
    for e in entries:
        a = first.get(e.get("name"))
        keys = ("stepsHash", "width", "height")
        if a is None or any(a.get(k) != e.get(k) for k in keys):
            problems.append(f"shots: rerun: {e.get('name')} differs from the first run's manifest")
    return problems


def assets_hashes(assets: pathlib.Path) -> dict[str, str]:
    return {
        p.relative_to(assets).as_posix(): sha(p) for p in sorted(assets.rglob("*")) if p.is_file()
    }


def assets_record(out: pathlib.Path, assets: pathlib.Path) -> list[str]:
    hashes = assets_hashes(assets) if assets.is_dir() else {}
    if not hashes:
        return [f"assets-record: {assets} holds no file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"assets-record: {len(hashes)} file(s) to {out}")
    return []


def neg_stage(out: pathlib.Path, stage: pathlib.Path) -> list[str]:
    raw = stage.read_bytes().decode("utf-8")
    lines = raw.split("\n")
    hits = [i for i, line in enumerate(lines) if NEG_LINE.match(line.rstrip("\r"))]
    if len(hits) != 1:
        return [
            f"neg-stage: the Settings download path line is found {len(hits)} time(s), not once"
        ]
    i = hits[0]
    cr = "\r" if lines[i].endswith("\r") else ""
    m = NEG_LINE.match(lines[i].rstrip("\r"))
    assert m
    lines[i] = m.group(1) + "'" + NEG_VALUE + "'" + m.group(2) + cr
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes("\n".join(lines).encode("utf-8"))
    print(f"neg-stage: line {i + 1} planted; {out}")
    return []


def assets_unchanged(
    before: pathlib.Path, assets: pathlib.Path, receipt: pathlib.Path, code: int
) -> list[str]:
    problems: list[str] = []
    if code != 1:
        problems.append(f"assets-unchanged: the negative run exited {code}, not 1")
    text = receipt.read_text(encoding="utf-8", errors="replace")
    if not any(NEG_BLOCKED.search(line) for line in text.splitlines()):
        problems.append("assets-unchanged: no 'privacy: blocked settings-download-light' line")
    want = json.loads(before.read_text(encoding="utf-8"))
    got = assets_hashes(assets)
    for name in sorted(set(want) | set(got)):
        if want.get(name) != got.get(name):
            problems.append(f"assets-unchanged: {name}: {want.get(name)} -> {got.get(name)}")
    print(f"assets-unchanged: {len(got)} file(s), negative exit {code}")
    return problems


# --- e2e-count
def e2e_count(receipt: pathlib.Path, n: int, plain: list[pathlib.Path]) -> list[str]:
    problems: list[str] = []
    for i, path in enumerate([receipt, *plain]):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        bad = [line.strip() for line in lines if E2E_BAD.search(line)]
        if bad:
            problems.append(f"e2e-count: {path.name}: {bad[:5]}")
        passes = [int(m.group(1)) for line in lines if (m := PASSED.match(line))]
        if i == 0:
            ok = sum(1 for line in lines if OK_LINE.match(line))
            print(f"e2e-count {path.name}: {ok} AC-162 ok lines, passed {passes}, want {n}")
            if ok != n:
                problems.append(f"e2e-count: {path.name}: {ok} AC-162 ok lines, not {n}")
            if passes != [n]:
                problems.append(f"e2e-count: {path.name}: passed {passes}, not [{n}]")
        else:
            print(f"e2e-count {path.name}: passed {passes}")
            if len(passes) != 1 or passes[0] < 1:
                problems.append(f"e2e-count: {path.name}: no single pass count ({passes})")
    return problems


# --- selftest
def _vitest_receipt(
    tests: list[tuple[str, str]], blocks: list[tuple[str, list[str]]], summary: str
) -> str:
    f = "tests/unit/help-quick-start.test.tsx"
    out = [f" ❯ {f} ({len(tests)} tests | {len(blocks)} failed) 120ms"]
    out += [f"     {mark} {title} 3ms" for mark, title in tests]
    out += [" Γ£ô tests/unit/help-shots-privacy.test.ts (6 tests) 9ms", ""]
    out += [f"ΓÄ»ΓÄ»ΓÄ» Failed Tests {len(blocks)} ΓÄ»ΓÄ»ΓÄ»", ""]
    for i, (title, body) in enumerate(blocks, 1):
        out += [
            f" FAIL  {f} > MEU-162 quick start > {title}",
            *body,
            "",
            f"ΓÄ»ΓÄ»ΓÄ»[{i}/{len(blocks)}]ΓÄ»",
            "",
        ]
    out += [" Test Files  1 failed | 1 passed (2)", f"      Tests  {summary}"]
    return "\n".join(out) + "\n"


ASSERT_JS = ["AssertionError: expected false to be true // Object.is equality"]
TYPE_JS = ["TypeError: Cannot read properties of undefined (reading 'width')"]


def _webp(kind: str, w: int, h: int, pad: int = 40) -> bytes:
    if kind == "VP8 ":
        data = b"\x00\x00\x00" + b"\x9d\x01\x2a" + struct.pack("<HH", w, h)
    elif kind == "VP8L":
        bits = (w - 1) | ((h - 1) << 14)
        data = b"\x2f" + bits.to_bytes(4, "little")
    else:
        data = b"\x00\x00\x00\x00" + (w - 1).to_bytes(3, "little") + (h - 1).to_bytes(3, "little")
    data += b"\x00" * pad
    chunk = kind.encode() + struct.pack("<I", len(data)) + data
    return b"RIFF" + struct.pack("<I", 4 + len(chunk)) + b"WEBP" + chunk


def selftest() -> int:
    failures: list[str] = []

    def case(name: str, problems: list[str], want_pass: bool) -> None:
        ok = not problems
        why = "" if ok else f" -- {problems[0][:110]}"
        print(
            f"{name}: {'pass' if ok else 'refused'} "
            f"(expected {'pass' if want_pass else 'refused'}){why}"
        )
        if ok != want_pass:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        t = pathlib.Path(tmp)
        # skill
        src, dst = t / "src", t / "dst"
        for name in SKILL_FILES:
            for base in (src, dst):
                (base / name).parent.mkdir(parents=True, exist_ok=True)
                body = "\n".join(MIT_MARKS) if name == "LICENSE" else f"{name} body\n"
                (base / name).write_text(body, encoding="utf-8")
        up = f"Source {UPSTREAM_URL} at {UPSTREAM_COMMIT}, MIT.\n"
        (dst / "UPSTREAM.md").write_text(up, encoding="utf-8")
        case("skill-identical", skill(src, dst), True)
        (dst / "UPSTREAM.md").write_text(up.replace(UPSTREAM_COMMIT, "32511c6"), encoding="utf-8")
        case("skill-upstream-short-commit", skill(src, dst), False)
        (dst / "UPSTREAM.md").write_text(up, encoding="utf-8")
        (dst / "examples/before-after.md").write_text("changed\n", encoding="utf-8")
        case("skill-changed-byte", skill(src, dst), False)
        (dst / "examples/before-after.md").write_text(
            "examples/before-after.md body\n", encoding="utf-8"
        )
        (dst / "notes.md").write_text("x\n", encoding="utf-8")
        case("skill-extra-file", skill(src, dst), False)
        (dst / "notes.md").unlink()
        (dst / "LICENSE").write_text("Apache License\n", encoding="utf-8")
        case("skill-not-mit", skill(src, dst), False)

        # red-record and red-unchanged
        root, store = t / "repo", t / "store"
        (root / "ui").mkdir(parents=True)
        (root / "ui/a.test.tsx").write_text("a\n", encoding="utf-8")
        (root / "ui/b.test.ts").write_text("b\n", encoding="utf-8")
        case("red-unchanged-no-record", red_unchanged(root, store), False)
        case("red-record-row4", red_record(4, ["ui/a.test.tsx", "ui/b.test.ts"], root, store), True)
        copy = store / "hq-red-copies/row4/ui/a.test.tsx"
        copied = copy.is_file() and copy.read_bytes() == (root / "ui/a.test.tsx").read_bytes()
        case("red-record-copied", [] if copied else ["copy missing"], True)
        case(
            "red-record-row4-again-same",
            red_record(4, ["ui/a.test.tsx", "ui/b.test.ts"], root, store),
            True,
        )
        case("red-unchanged-ok", red_unchanged(root, store), True)
        (root / "ui/a.test.tsx").write_text("a changed\n", encoding="utf-8")
        case("red-unchanged-changed", red_unchanged(root, store), False)
        case(
            "red-record-row4-other-hashes",
            red_record(4, ["ui/a.test.tsx", "ui/b.test.ts"], root, store),
            False,
        )
        case("red-record-missing-file", red_record(5, ["ui/none.ts"], root, store), False)

        # pins-unchanged
        (root / "ui/tests/unit").mkdir(parents=True)
        pin = root / "ui/tests/unit/help-card.test.ts"
        skip = root / PIN_SKIP
        pin.write_text("pin\n", encoding="utf-8")
        skip.write_text("skip\n", encoding="utf-8")
        pins = t / "pins.json"
        rel_pin = "ui/tests/unit/help-card.test.ts"
        pins.write_text(
            json.dumps({"files": {rel_pin: sha(pin), PIN_SKIP: sha(skip)}}), encoding="utf-8"
        )
        skip.write_text("skip changed in row 4\n", encoding="utf-8")
        case("pins-unchanged-skip-file-changed", pins_unchanged(root, pins), True)
        pin.write_text("pin changed\n", encoding="utf-8")
        case("pins-unchanged-pin-changed", pins_unchanged(root, pins), False)

        # only-failing
        green = [
            ("Γ£ô", "AC-162.1 the quick start data validates"),
            ("Γ£ô", "AC-162.4 css the theme rules exist once"),
            ("├ù", "AC-162.4 figures each shot renders two images"),
            ("├ù", "AC-162.7 the manifest matches the data"),
            ("Γ£ô", "AC-162.10 never in this file but a prefix trap"),
        ]
        blocks = [
            ("AC-162.4 figures each shot renders two images", ASSERT_JS),
            ("AC-162.7 the manifest matches the data", ASSERT_JS),
        ]
        ids = ["AC-162.4 figures", "AC-162.7"]

        def vit(name: str, tests, blocks, summary: str) -> pathlib.Path:
            p = t / f"{name}.txt"
            p.write_text(_vitest_receipt(tests, blocks, summary), encoding="utf-8")
            return p

        r = vit("of-ok", green, blocks, "2 failed | 9 passed (11)")
        case("only-failing-row7", only_failing(ids, r), True)
        case("only-failing-id-not-failing", only_failing([*ids, "AC-162.1"], r), False)
        trap = [(("├ù" if t.startswith("AC-162.10") else m), t) for m, t in green]
        trap = [(("Γ£ô" if t.startswith(("AC-162.4", "AC-162.7")) else m), t) for m, t in trap]
        r = vit(
            "of-trap",
            trap,
            [("AC-162.10 never in this file but a prefix trap", ASSERT_JS)],
            "1 failed | 10 passed (11)",
        )
        case("only-failing-prefix-is-not-a-match", only_failing(["AC-162.1"], r), False)
        case("only-failing-prefix-exact", only_failing(["AC-162.10"], r), True)
        extra = [*green, ("├ù", "AC-162.5 search hides the steps")]
        r = vit(
            "of-extra",
            extra,
            [*blocks, ("AC-162.5 search hides the steps", ASSERT_JS)],
            "3 failed | 8 passed (11)",
        )
        case("only-failing-extra-failure", only_failing(ids, r), False)
        r = vit("of-type", green, [blocks[0], (blocks[1][0], TYPE_JS)], "2 failed | 9 passed (11)")
        case("only-failing-typeerror", only_failing(ids, r), False)
        r = vit(
            "of-skip",
            [*green, ("Γåô", "AC-162.6 skipped")],
            blocks,
            "2 failed | 9 passed | 1 skipped (12)",
        )
        case("only-failing-skipped", only_failing(ids, r), False)
        real = [(m.replace("Γ£ô", "✓").replace("├ù", "×"), title) for m, title in green]
        r = vit("of-real-glyphs", real, blocks, "2 failed | 9 passed (11)")
        case("only-failing-real-glyphs", only_failing(ids, r), True)
        r = vit("of-count", green, blocks, "3 failed | 8 passed (11)")
        case("only-failing-summary-count", only_failing(ids, r), False)
        colon = [(m, t.replace("figures each", "figures: each")) for m, t in green]
        colon_blocks = [(t.replace("figures each", "figures: each"), b) for t, b in blocks]
        r = vit("of-colon", colon, colon_blocks, "2 failed | 9 passed (11)")
        case("only-failing-colon-ends-the-id", only_failing(ids, r), True)
        case(
            "only-failing-colon-prefix-is-not-a-match",
            only_failing(["AC-162.4 fig", "AC-162.7"], r),
            False,
        )

        # shots, assets-record, neg-stage, assets-unchanged
        assets = t / "assets"
        assets.mkdir()
        qs = t / "quick-start.json"
        qs.write_text(
            json.dumps(
                {
                    "pages": {
                        "downloader": {"shots": [{"name": "downloader"}]},
                        "settings": {
                            "shots": [{"name": "settings-download"}, {"name": "settings-setup"}]
                        },
                    }
                }
            ),
            encoding="utf-8",
        )
        manifest = []
        for i, (name, page, kind) in enumerate(
            (
                ("downloader", "downloader", "VP8 "),
                ("settings-download", "settings", "VP8L"),
                ("settings-setup", "settings", "VP8X"),
            )
        ):
            w, h = 1200 - i, 640 + i
            sizes = {}
            for theme in THEMES:
                raw = _webp(kind, w, h, pad=40 + len(theme))
                (assets / f"{name}-{theme}.webp").write_bytes(raw)
                sizes[theme] = len(raw)
            manifest.append(
                {
                    "name": name,
                    "page": page,
                    "width": w,
                    "height": h,
                    "bytes": sizes,
                    "stepsHash": "ab" * 32,
                }
            )
        (assets / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        m1 = t / "manifest-1.json"
        m1.write_text(json.dumps(manifest), encoding="utf-8")
        log_lines = ["isolation: ok"] * 4 + [
            f"privacy: clean {e['name']}-{theme}" for e in manifest for theme in THEMES
        ]
        log = t / "shots-1.txt"
        log.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        case("shots-ok", shots(assets, qs, [log, log], m1), True)
        bad_log = t / "shots-bad.txt"
        bad_log.write_text(
            "\n".join(log_lines[:-1] + ["privacy: blocked settings-setup-dark"]) + "\n",
            encoding="utf-8",
        )
        case("shots-blocked-line", shots(assets, qs, [log, bad_log], m1), False)
        iso_log = t / "shots-iso.txt"
        iso_log.write_text("\n".join(log_lines[1:]) + "\n", encoding="utf-8")
        case("shots-isolation-count", shots(assets, qs, [iso_log], m1), False)
        m1.write_text(
            json.dumps([{**manifest[0], "stepsHash": "cd" * 32}, *manifest[1:]]), encoding="utf-8"
        )
        case("shots-rerun-hash-differs", shots(assets, qs, [log], m1), False)
        m1.write_text(json.dumps(manifest), encoding="utf-8")
        (assets / "stray.png").write_bytes(b"x")
        case("shots-stray-file", shots(assets, qs, [log], m1), False)
        (assets / "stray.png").unlink()
        (assets / "downloader-dark.webp").write_bytes(_webp("VP8 ", 1199, 640, pad=41))
        case("shots-header-mismatch", shots(assets, qs, [log], m1), False)
        (assets / "downloader-dark.webp").write_bytes(_webp("VP8 ", 1200, 640, pad=MAX_BYTES))
        case("shots-over-size", shots(assets, qs, [log], m1), False)
        (assets / "downloader-dark.webp").write_bytes(_webp("VP8 ", 1200, 640, pad=44))
        case("shots-restored", shots(assets, qs, [log], m1), True)

        before = t / "assets-before.json"
        case("assets-record", assets_record(before, assets), True)
        case("assets-record-empty", assets_record(t / "x.json", t / "none"), False)
        neg = t / "neg.txt"
        neg.write_text("  x privacy: blocked settings-download-light\n", encoding="utf-8")
        case("assets-unchanged-ok", assets_unchanged(before, assets, neg, 1), True)
        case("assets-unchanged-exit-0", assets_unchanged(before, assets, neg, 0), False)
        neg2 = t / "neg2.txt"
        neg2.write_text("privacy: blocked settings-download-lightx\n", encoding="utf-8")
        case("assets-unchanged-no-blocked-line", assets_unchanged(before, assets, neg2, 1), False)
        (assets / "settings-setup-light.webp").write_bytes(b"new")
        case("assets-unchanged-file-written", assets_unchanged(before, assets, neg, 1), False)
        (assets / "added.webp").write_bytes(b"new")
        case("assets-unchanged-file-added", assets_unchanged(before, assets, neg, 1), False)

        stage = t / "stage.ts"
        good = "    downloader: {\n      path: media,\n      quality: '1080p',\n"
        other = "    transcript: { output_dir: media, delay_between_requests: 6 },\n"
        stage.write_text(good + other, encoding="utf-8")
        out = t / "neg" / "stage.ts"
        case("neg-stage-once", neg_stage(out, stage), True)
        planted = out.read_text(encoding="utf-8")
        ok = "path: 'C:\\\\Users\\\\alex\\\\Videos'," in planted and other in planted
        case("neg-stage-planted", [] if ok else ["not planted"], True)
        stage.write_text(good + good, encoding="utf-8")
        case("neg-stage-twice", neg_stage(out, stage), False)
        stage.write_text(other, encoding="utf-8")
        case("neg-stage-absent", neg_stage(out, stage), False)

        # e2e-count
        def pw(name: str, body: list[str]) -> pathlib.Path:
            p = t / f"{name}.txt"
            p.write_text("\n".join(body) + "\n", encoding="utf-8")
            return p

        oks = [
            f"  ok {i:>2} tests\\e2e\\help-quick-start.test.ts:1:1 ΓÇ║ AC-162.1{i} x (1.0s)"
            for i in range(1, 4)
        ]
        oks[0] = (
            "  ok  1 [electron] ΓÇ║ tests\\e2e\\help-quick-start.test.ts:1:1 "
            "ΓÇ║ AC-162.10 hint (1.0s)"
        )
        hq = pw("hq", ["Running 3 tests using 1 worker", *oks, "", "  3 passed (9.0s)"])
        plain = pw(
            "plain",
            ["  ok 1 tests\\e2e\\help-search.spec.ts:1:1 ΓÇ║ W6-1 (1.0s)", "  1 passed (2.0s)"],
        )
        case("e2e-count-ok-below-10", e2e_count(hq, 3, [plain]), True)
        case("e2e-count-wrong-n", e2e_count(hq, 4, [plain]), False)
        flaky = pw("flaky", ["  ok 1 x ΓÇ║ AC-162.10 y (1.0s)", "  1 flaky", "  1 passed (1.0s)"])
        case("e2e-count-flaky", e2e_count(hq, 3, [flaky]), False)
        rej = pw("rej", [*oks, "unhandled rejection: boom", "  3 passed (9.0s)"])
        case("e2e-count-unhandled", e2e_count(rej, 3, []), False)
        failed = pw("failed", [*oks, "  1 failed", "  3 passed (9.0s)"])
        case("e2e-count-failed", e2e_count(failed, 3, []), False)
        nopass = pw("nopass", ["  ok 1 tests\\e2e\\x.ts:1:1 ΓÇ║ W6-1 (1.0s)"])
        case("e2e-count-plain-no-pass", e2e_count(hq, 3, [nopass]), False)

    print(f"row-check selftest: {len(failures)} wrong: {failures}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == "skill" and not rest:
            problems = skill(SKILL_SRC, SKILL_DST)
        elif cmd == "red-record" and len(rest) >= 3 and rest[0] == "--row":
            problems = red_record(int(rest[1]), rest[2:], ROOT, RECEIPTS)
        elif cmd == "red-unchanged" and not rest:
            problems = red_unchanged(ROOT, RECEIPTS)
        elif cmd == "pins-unchanged" and not rest:
            problems = pins_unchanged(ROOT, PINS)
        elif cmd == "only-failing":
            ids: list[str] = []
            paths: list[str] = []
            it = iter(rest)
            for arg in it:
                if arg == "--id":
                    ids.append(next(it, ""))
                else:
                    paths.append(arg)
            if not ids or "" in ids or len(paths) != 1:
                raise ValueError("only-failing --id ID [--id ID ...] RECEIPT")
            problems = only_failing(ids, pathlib.Path(paths[0]))
        elif cmd == "shots" and not rest:
            logs = [RECEIPTS / "hq-row8-shots-1.txt", RECEIPTS / "hq-row8-shots-2.txt"]
            problems = shots(ASSETS, QUICK_START, logs, RECEIPTS / "hq-row8-manifest-1.json")
        elif cmd == "assets-record" and len(rest) == 1:
            problems = assets_record(pathlib.Path(rest[0]), ASSETS)
        elif cmd == "neg-stage" and len(rest) == 1:
            problems = neg_stage(pathlib.Path(rest[0]), STAGE)
        elif (
            cmd == "assets-unchanged"
            and len(rest) == 5
            and rest[1] == "--neg-receipt"
            and rest[3] == "--neg-exit"
        ):
            problems = assets_unchanged(
                pathlib.Path(rest[0]), ASSETS, pathlib.Path(rest[2]), int(rest[4])
            )
        elif cmd == "e2e-count" and len(rest) >= 2:
            plain: list[pathlib.Path] = []
            it = iter(rest[2:])
            for arg in it:
                if arg != "--plain":
                    raise ValueError("e2e-count RECEIPT N [--plain RECEIPT ...]")
                plain.append(pathlib.Path(next(it)))
            problems = e2e_count(pathlib.Path(rest[0]), int(rest[1]), plain)
        else:
            raise ValueError(f"unknown or malformed subcommand {cmd!r}")
    except (ValueError, StopIteration) as exc:
        print(f"usage: {exc}")
        return 2
    for p in problems:
        print("PROBLEM:", p)
    print(f"row-check {cmd}: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
