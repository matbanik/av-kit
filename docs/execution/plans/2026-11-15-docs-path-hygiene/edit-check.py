"""Session 83 edit check (implementation-plan.md §`edit-check.py`; AC-10 to AC-14, AC-17 to AC-19).

Usage, from the repository root:

    python edit-check.py --group docs|tests|commands     # rows 5, 6 and 8
    python edit-check.py --group register --stage 7|10   # rows 7 and 10
    python edit-check.py --anchors                       # row 0: every anchor is found (S5)
    python edit-check.py --selftest                      # the negatives of AC-10 to AC-14 and AC-19

For the docs, tests and commands groups it builds each file's expected bytes from BASE(path)
(C:/Temp/av-kit/dph/base/<path>, row 0's copy) by the exact edits of §Live fixes, §The layout
block and §The D6 row, each found by content, and compares them with the file byte for byte.
So only the named lines may change, each to §Live fixes' text, and every line keeps its ending.
Named checks add the line-ending kind, the 06-gui widths, the 07-distribution comment column, the
README JSON block and the add-only commands row. A mismatch reports a line number, never text.

The register group compares the parsed register with BASE's: the file is LF, no line holds the
home folder's path, and the parsed difference is exactly the fields of §The register that the
rows so far changed.

The home pattern comes from inventory.py (CHECK does not exist when row 0 runs this selftest).
Nothing printed holds the home folder or a line's text.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import tempfile
from collections.abc import Callable

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import inventory  # noqa: E402

BASE = pathlib.Path("C:/Temp/av-kit/dph/base")

SKILL = ".agent/skills/git-workflow/SKILL.md"
DESIGN = "_inspiration/capture-crop/design.md"
GUI = "docs/build-plan/06-gui.md"
DIST = "docs/build-plan/07-distribution.md"
README = "README.md"
CAPTURE = "ui/tests/unit/capture-interactive.test.ts"
SPAWN = "ui/tests/unit/dev-spawn.test.ts"
REGISTER = ".agent/context/known-issues.yaml"
COMMANDS = ".agent/docs/commands.md"

EOL = {
    SKILL: "CRLF",
    DESIGN: "LF",
    GUI: "CRLF",
    DIST: "CRLF",
    README: "LF",
    CAPTURE: "LF",
    SPAWN: "LF",
    REGISTER: "LF",
    COMMANDS: "CRLF",
}
GROUPS = {
    "docs": (SKILL, DESIGN, GUI, DIST, README),
    "tests": (CAPTURE, SPAWN),
    "commands": (COMMANDS,),
    "register": (REGISTER,),
}

BS = "\\"
OLD_PROGRAMS = "Programs" + BS * 2 + "av-kit" + BS * 2
NEW_PROGRAMS = "Programs" + BS * 2 + "av-kit-ui" + BS * 2
LINE40_OLD = "# e.g. %LOCALAPPDATA%/Programs/av-kit"
LINE40_NEW = "# e.g. %LOCALAPPDATA%/Programs/av-kit-ui"
OLD_LAYOUT = (
    "│   ├── extra/",
    "│   │   ├── avkit-backend/         # PyInstaller onedir (preferred over onefile)",
    "│   │   │   └── avkit-backend.exe",
    "│   │   ├── ffmpeg/",
    "│   │   │   ├── ffmpeg.exe",
    "│   │   │   └── ffprobe.exe",
    "│   │   └── mcp-server/            # compiled JS (Phase 5 dist/)",
)
NEW_LAYOUT = (
    "│   ├── avkit-backend/             # PyInstaller onedir (preferred over onefile)",
    "│   │   └── avkit-backend.exe",
    "│   ├── ffmpeg/",
    "│   │   ├── ffmpeg.exe",
    "│   │   └── ffprobe.exe",
    "│   ├── mcp-server/                # compiled JS (Phase 5 dist/)",
)
D6_ROW = (
    "| home-path | static | `uv run python tools/check_home_path.py` | Every session: tracked and untracked "
    "(not ignored) files outside .agent/fleet/hub; allow-list tools/home_path_allowlist.txt (D-817); exit 0 ok, "
    "1 an instance or a stale entry, 2 usage; maintainer host only, CI's home differs |"
)
CAPTURE_NEW = "const INBOX_PATH = 'C:/Users/avkit/Pictures/av-kit/2026-08-27_12-00-00.png'"
SPAWN_NEW = "'C:/Users/avkit/.local/share/uv/python/cpython.exe'"
GUI_TARGETS = ("~/Downloads/av-kit", "~/Documents/Transcripts")

# The register (§The register): issue -> the fields each stage may change.
SCRUB_ISSUE, SCRUB_FIELDS = "CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR", ("root_cause", "notes")
RESOLVE_KEYS = ("status", "verification", "resolution_path")
RESOLVED_AT = {"INSTALL-FOLDER-NAME-MISMATCH": 7, "TRACKED-FILES-HOLD-HOME-PATH": 10}


class Refused(Exception):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise Refused(message)


def split(raw: bytes) -> list[str]:
    """The lines of RAW, each keeping a trailing CR; the last item follows the last LF."""
    return raw.decode("utf-8").split("\n")


def body(line: str) -> str:
    return line[:-1] if line.endswith("\r") else line


def end(line: str) -> str:
    return "\r" if line.endswith("\r") else ""


def hits(lines: list[str], rx: re.Pattern[str]) -> list[int]:
    return [i for i, line in enumerate(lines) if rx.search(line)]


def one_match(line: str, rx: re.Pattern[str], number: int) -> None:
    require(len(rx.findall(line)) == 1, f"line {number} holds the path more than once")


# --- the expected edits, each found by content ----------------------------------------------


def t_skill(lines: list[str], rx: re.Pattern[str]) -> list[str]:
    at = hits(lines, rx)
    require(
        len(at) == 1 and "antigravity-ide" in lines[at[0]],
        f"SKILL: {len(at)} home line(s), the plan names 1 transcript line",
    )
    i = at[0]
    one_match(lines[i], rx, i + 1)
    lines[i] = rx.sub("~", lines[i])
    require(
        "`~" + BS + ".gemini" + BS + "antigravity-ide" + BS + "brain" + BS in lines[i],
        f"SKILL: line {i + 1} new text is not §Live fixes'",
    )
    return lines


def t_design(lines: list[str], rx: re.Pattern[str]) -> list[str]:
    at = hits(lines, rx)
    require(len(at) == 1, f"design: {len(at)} home line(s), the plan names 1")
    i = at[0]
    one_match(lines[i], rx, i + 1)
    lines[i] = rx.sub("C:/Users/YOU", lines[i])
    require(
        '"path": "C:/Users/YOU/Desktop/2026-11-07_13-16-09.png"' in lines[i],
        f"design: line {i + 1} new text is not §Live fixes'",
    )
    return lines


def t_gui(lines: list[str], rx: re.Pattern[str]) -> list[str]:
    at = hits(lines, rx)
    require(len(at) == 2, f"06-gui: {len(at)} home line(s), the plan names 2")
    for i, target in zip(at, GUI_TARGETS):
        fields = [m for m in re.finditer(r"\[([^\[\]]*)\]", lines[i]) if rx.search(m.group(1))]
        require(len(fields) == 1, f"06-gui: line {i + 1} has {len(fields)} bracketed path field(s)")
        m = fields[0]
        content = m.group(1)
        require(
            rx.sub("~", content).rstrip().replace(BS, "/") == target,
            f"06-gui: line {i + 1} is not the {target} field",
        )
        require(
            len(target) <= len(content),
            f"06-gui: line {i + 1}'s field is narrower than the new path",
        )
        lines[i] = lines[i][: m.start(1)] + target.ljust(len(content)) + lines[i][m.end(1) :]
    return lines


def t_dist(lines: list[str], rx: re.Pattern[str]) -> list[str]:
    at = [i for i, line in enumerate(lines) if body(line).endswith(LINE40_OLD)]
    require(len(at) == 1, f"07: {len(at)} line(s) end with the line-40 comment, the plan names 1")
    i = at[0]
    lines[i] = body(lines[i])[: -len(LINE40_OLD)] + LINE40_NEW + end(lines[i])
    bodies = [body(line) for line in lines]
    runs = [
        j
        for j in range(len(lines) - len(OLD_LAYOUT) + 1)
        if tuple(bodies[j : j + len(OLD_LAYOUT)]) == OLD_LAYOUT
    ]
    require(
        len(runs) == 1,
        f"07: the seven-line extra/ block is found {len(runs)} time(s), the plan names 1",
    )
    j = runs[0]
    ending = end(lines[j])
    return lines[:j] + [b + ending for b in NEW_LAYOUT] + lines[j + len(OLD_LAYOUT) :]


def t_readme(lines: list[str], rx: re.Pattern[str]) -> list[str]:
    at = [i for i, line in enumerate(lines) if OLD_PROGRAMS in line]
    require(
        len(at) == 2 and at[1] == at[0] + 1,
        f"README: {len(at)} Programs line(s), the plan names 2 adjacent",
    )
    for i in at:
        require(
            lines[i].count(OLD_PROGRAMS) == 1,
            f"README: line {i + 1} holds the segment more than once",
        )
        lines[i] = lines[i].replace(OLD_PROGRAMS, NEW_PROGRAMS)
    require("av-kit.exe" in lines[at[0]], f"README: line {at[0] + 1} does not name av-kit.exe")
    return lines


def t_capture(lines: list[str], rx: re.Pattern[str]) -> list[str]:
    at = hits(lines, rx)
    require(
        len(at) == 1 and "const INBOX_PATH = '" in lines[at[0]],
        f"capture-interactive: {len(at)} home line(s), the plan names 1",
    )
    i = at[0]
    one_match(lines[i], rx, i + 1)
    lines[i] = rx.sub("C:/Users/avkit", lines[i])
    require(
        CAPTURE_NEW in lines[i], f"capture-interactive: line {i + 1} new text is not §Live fixes'"
    )
    return lines


def t_spawn(lines: list[str], rx: re.Pattern[str]) -> list[str]:
    at = hits(lines, rx)
    require(len(at) == 5, f"dev-spawn: {len(at)} home line(s), the plan names 5")
    for i in at:
        one_match(lines[i], rx, i + 1)
        lines[i] = rx.sub("C:/Users/avkit", lines[i])
        require(SPAWN_NEW in lines[i], f"dev-spawn: line {i + 1} new text is not §Live fixes'")
    return lines


def t_commands(lines: list[str], rx: re.Pattern[str]) -> list[str]:
    at = [i for i, line in enumerate(lines) if line.startswith("| task-contract |")]
    require(len(at) == 1, f"commands: {len(at)} task-contract row(s), the plan names 1")
    i = at[0]
    return lines[: i + 1] + [D6_ROW + end(lines[i])] + lines[i + 1 :]


TRANSFORMS: dict[str, Callable[[list[str], re.Pattern[str]], list[str]]] = {
    SKILL: t_skill,
    DESIGN: t_design,
    GUI: t_gui,
    DIST: t_dist,
    README: t_readme,
    CAPTURE: t_capture,
    SPAWN: t_spawn,
    COMMANDS: t_commands,
}


def expected(path: str, base: bytes, rx: re.Pattern[str]) -> bytes:
    return "\n".join(TRANSFORMS[path](split(base), rx)).encode("utf-8")


# --- named checks ---------------------------------------------------------------------------


def eol_problems(path: str, raw: bytes, label: str) -> list[str]:
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if EOL[path] == "CRLF":
        ok = crlf == lf and raw.count(b"\r") == crlf
    else:
        ok = b"\r" not in raw
    return (
        []
        if ok
        else [f"{path}: {label} line endings are not all {EOL[path]} (CRLF={crlf} LF={lf - crlf})"]
    )


def gui_problems(base: bytes, cur: bytes, rx: re.Pattern[str]) -> list[str]:
    old, new = split(base), split(cur)
    out = []
    for i in hits(old, rx):
        if i >= len(new) or len(body(new[i])) != len(body(old[i])):
            out.append(f"06-gui: line {i + 1} width changed")
    return out


def dist_problems(cur: bytes) -> list[str]:
    """The layout lost extra/, and each moved comment keeps the column it had in the old block."""
    new = [body(line) for line in split(cur)]
    out = []
    if OLD_LAYOUT[0] in new:
        out.append("07: the layout still holds the extra/ line")
    for name, old in (("avkit-backend/", OLD_LAYOUT[1]), ("mcp-server/", OLD_LAYOUT[6])):
        lines = [b for b in new if b.startswith("│   ├── " + name) and "#" in b]
        if len(lines) != 1 or lines[0].index("#") != old.index("#"):
            out.append(f"07: the {name} comment column moved (or the line is not found once)")
    return out


def readme_problems(cur: bytes) -> list[str]:
    lines = [body(line) for line in split(cur)]
    at = [i for i, line in enumerate(lines) if NEW_PROGRAMS in line]
    if not at:
        return ["README: no Programs/av-kit-ui line"]
    starts = [i for i in range(at[0], -1, -1) if lines[i].strip() == "```json"]
    stops = [i for i in range(at[0], len(lines)) if lines[i].strip() == "```"]
    if not starts or not stops:
        return ["README: the JSON block around the Programs lines is not found"]
    try:
        json.loads("\n".join(lines[starts[0] + 1 : stops[0]]))
    except json.JSONDecodeError as exc:
        return [
            f"README: the JSON block (lines {starts[0] + 2}-{stops[0]}) does not parse: line {exc.lineno}"
        ]
    return []


def commands_problems(base: bytes, cur: bytes) -> list[str]:
    old, new = split(base), split(cur)
    if len(new) != len(old) + 1:
        return [f"commands: {len(new) - len(old)} line(s) added, the plan adds 1 (add-only)"]
    extra = [i for i in range(len(new)) if new[:i] + new[i + 1 :] == old]
    return [] if extra else ["commands: removing one line does not give the base; not add-only"]


def file_problems(path: str, base: bytes, cur: bytes, rx: re.Pattern[str]) -> list[str]:
    problems = eol_problems(path, base, "base") + eol_problems(path, cur, "current")
    try:
        want = expected(path, base, rx)
    except Refused as exc:
        return problems + [f"{path}: base anchors: {exc}"]
    if cur != want:
        a, b = split(want), split(cur)
        first = next((n for n, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        problems.append(
            f"{path}: differs from the expected edit at line {first + 1} (expected {len(a)} lines, found {len(b)})"
        )
    if path == GUI:
        problems += gui_problems(base, cur, rx)
    if path == DIST:
        problems += dist_problems(cur)
    if path == README:
        problems += readme_problems(cur)
    if path == COMMANDS:
        problems += commands_problems(base, cur)
    if path in (SKILL, DESIGN, GUI, CAPTURE, SPAWN):
        left = hits(split(cur), rx)
        if left:
            problems.append(f"{path}: lines {[n + 1 for n in left]} still hold the path")
    return problems


def changed_lines(base: bytes, cur: bytes) -> str:
    a, b = split(base), split(cur)
    if len(a) != len(b):
        return f"lines {len(a)} -> {len(b)}"
    return "changed lines " + ",".join(str(n + 1) for n, (x, y) in enumerate(zip(a, b)) if x != y)


# --- the register ---------------------------------------------------------------------------


def register_problems(base: bytes, cur: bytes, stage: int, rx: re.Pattern[str]) -> list[str]:
    sys.path.insert(0, str(ROOT / "tools"))
    from issue_triage import model

    problems = eol_problems(REGISTER, cur, "current")
    left = hits(split(cur), rx)
    if left:
        problems.append(f"register: lines {[n + 1 for n in left]} hold the path")
    with tempfile.TemporaryDirectory(dir="C:/Temp/av-kit/dph/tmp") as t:
        a_path, b_path = pathlib.Path(t, "base.yaml"), pathlib.Path(t, "cur.yaml")
        a_path.write_bytes(base)
        b_path.write_bytes(cur)
        a, b = model.load(a_path), model.load(b_path)
    ids = [i["id"] for i in a["issues"]]
    if [i["id"] for i in b["issues"]] != ids:
        return problems + ["register: the issue list changed"]
    idx = {k: ids.index(k) for k in (SCRUB_ISSUE, *RESOLVED_AT)}
    allowed = {f".issues[{idx[SCRUB_ISSUE]}].{f}" for f in SCRUB_FIELDS}
    for issue_id, at in RESOLVED_AT.items():
        if stage >= at:
            allowed |= {f".issues[{idx[issue_id]}].{k}" for k in RESOLVE_KEYS}
    diffs = sorted(set(_differences(a, b)))
    outside = [d for d in diffs if not d.startswith(tuple(allowed))]
    if outside:
        problems.append(f"register: parsed differences outside §The register: {outside}")
    old_s, new_s = a["issues"][idx[SCRUB_ISSUE]], b["issues"][idx[SCRUB_ISSUE]]
    for f in SCRUB_FIELDS:
        if not rx.search(old_s[f]):
            problems.append(f"register: base {SCRUB_ISSUE}.{f} holds no path to scrub")
        if new_s[f] != rx.sub("~", old_s[f]):
            problems.append(f"register: {SCRUB_ISSUE}.{f} is not the base with the path read as ~")
    for issue_id, at in RESOLVED_AT.items():
        issue, before = b["issues"][idx[issue_id]], a["issues"][idx[issue_id]]
        if stage >= at:
            v = issue.get("verification") or {}
            if issue.get("status") != "resolved":
                problems.append(f"register: {issue_id} is not resolved")
            if not all(
                isinstance(v.get(k), str) and v.get(k) for k in ("last_checked", "method", "result")
            ):
                problems.append(
                    f"register: {issue_id}.verification lacks last_checked, method or result"
                )
            rp = issue.get("resolution_path")
            if not (
                isinstance(rp, str) and rp.startswith("Fixed in Session 83 on ") and BS not in rp
            ):
                problems.append(
                    f"register: {issue_id}.resolution_path is not Session 83's, with forward slashes"
                )
        elif issue != before:
            problems.append(f"register: {issue_id} changed before row {at}")
    print(f"register parsed differences ({len(diffs)}):")
    for d in diffs:
        print(f"  {d}")
    return problems


def _differences(a: object, b: object, path: str = "") -> list[str]:
    """issue-resolve.py's `differences`: every path at which two parsed values differ."""
    if isinstance(a, dict) and isinstance(b, dict):
        if [k for k in b if k in a] != list(a):
            return [f"{path}: keys differ"]
        added = [f"{path}.{k}" for k in b if k not in a]
        return added + [d for k in a for d in _differences(a[k], b[k], f"{path}.{k}")]
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: lengths differ"]
        return [d for n, (x, y) in enumerate(zip(a, b)) for d in _differences(x, y, f"{path}[{n}]")]
    return [] if type(a) is type(b) and a == b else [path or "<root>"]


# --- modes ----------------------------------------------------------------------------------


def run_group(group: str, stage: int | None) -> int:
    rx = inventory.home_regex(str(pathlib.Path.home()))
    problems: list[str] = []
    for path in GROUPS[group]:
        base = (BASE / path).read_bytes()
        cur = (ROOT / path).read_bytes()
        if group == "register":
            assert stage is not None
            found = register_problems(base, cur, stage, rx)
        else:
            found = file_problems(path, base, cur, rx)
        problems += found
        note = changed_lines(base, cur) if group != "register" else f"stage {stage}"
        print(f"{path}: {'ok' if not found else f'{len(found)} problem(s)'} ({EOL[path]}; {note})")
    for p in problems:
        print("PROBLEM:", p)
    label = group + (f" --stage {stage}" if stage else "")
    if problems:
        print(f"edit-check {label}: {len(problems)} problem(s)")
        return 1
    print(f"edit-check {label}: ok files={len(GROUPS[group])}")
    return 0


def anchors() -> int:
    """Row 0: every edit applies to the current file (which is BASE), so every anchor is found."""
    rx = inventory.home_regex(str(pathlib.Path.home()))
    problems = []
    for path, transform in TRANSFORMS.items():
        raw = (ROOT / path).read_bytes()
        problems += eol_problems(path, raw, "current")
        try:
            transform(split(raw), rx)
            print(f"anchor {path}: found ({EOL[path]})")
        except Refused as exc:
            problems.append(f"S5: {path}: {exc}")
    sys.path.insert(0, str(ROOT / "tools"))
    from issue_triage import model

    data = model.load(ROOT / REGISTER)
    issues = {i["id"]: i for i in data["issues"]}
    problems += eol_problems(REGISTER, (ROOT / REGISTER).read_bytes(), "current")
    for issue_id in (SCRUB_ISSUE, *RESOLVED_AT):
        if issue_id not in issues:
            problems.append(f"S5: the register has no issue {issue_id}")
    if SCRUB_ISSUE in issues:
        for f in SCRUB_FIELDS:
            if not rx.search(str(issues[SCRUB_ISSUE].get(f, ""))):
                problems.append(f"S5: {SCRUB_ISSUE}.{f} holds no path")
            else:
                print(f"anchor register {SCRUB_ISSUE}.{f}: found")
    for issue_id in RESOLVED_AT:
        if issue_id in issues:
            print(f"anchor register {issue_id}: status={issues[issue_id].get('status')}")
            if issues[issue_id].get("status") != "open":
                problems.append(f"S5: {issue_id} is not open")
    for p in problems:
        print("PROBLEM:", p)
    print(f"edit-check anchors: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


# --- selftest -------------------------------------------------------------------------------

H = "C:" + BS + "Users" + BS + "fixture"
FIXTURES = {
    SKILL: "intro\r\n- transcript: `"
    + H
    + BS
    + ".gemini"
    + BS
    + "antigravity-ide"
    + BS
    + "brain"
    + BS
    + "x.md`\r\nafter\r\n",
    DESIGN: 'a\n  "path": "C:/Users/fixture/Desktop/2026-11-07_13-16-09.png",\nb\n',
    GUI: (
        "│  Folder: [" + H + BS + "Downloads" + BS + "av-kit         ] [Browse...]  ││\r\n"
        "│  other\r\n"
        "│  Out:    [" + H + BS + "Documents" + BS + "Transcripts    ] [Browse...]  ││\r\n"
    ),
    DIST: "{install}/                         "
    + LINE40_OLD
    + "\r\n├── resources/\r\n"
    + "".join(x + "\r\n" for x in OLD_LAYOUT)
    + "│   └── app.asar\r\n",
    README: '```json\n{\n  "a": {\n    "command": "C:'
    + BS * 2
    + "Users"
    + BS * 2
    + "YOU"
    + BS * 2
    + "AppData"
    + BS * 2
    + OLD_PROGRAMS
    + 'av-kit.exe",\n'
    '    "args": ["C:' + BS * 2 + OLD_PROGRAMS + 'resources"]\n  }\n}\n```\n',
    CAPTURE: "import x\nconst INBOX_PATH = 'C:/Users/fixture/Pictures/av-kit/2026-08-27_12-00-00.png'\nend\n",
    SPAWN: "".join(
        f"    k{n}: 'C:/Users/fixture/.local/share/uv/python/cpython.exe',\n" for n in range(5)
    ),
    COMMANDS: "| a | b |\r\n| task-contract | static | x |\r\n| z | y |\r\n",
}


def _swap_line(raw: bytes, number: int, new: str) -> bytes:
    lines = split(raw)
    lines[number - 1] = new + end(lines[number - 1])
    return "\n".join(lines).encode("utf-8")


def selftest() -> int:
    rx = inventory.home_regex(H)
    failures: list[str] = []

    def case(name: str, path: str, cur: bytes, refused: bool, keyword: str = "") -> None:
        base = FIXTURES[path].encode("utf-8")
        problems = file_problems(path, base, cur, rx)
        ok = bool(problems) == refused and (not keyword or any(keyword in p for p in problems))
        print(
            f"{name}: {'refused' if problems else 'accepted'} (expected {'refused' if refused else 'accepted'}) {problems[:2]}"
        )
        if not ok:
            failures.append(name)

    good = {p: expected(p, FIXTURES[p].encode("utf-8"), rx) for p in TRANSFORMS}
    for path in TRANSFORMS:
        case(f"positive {path}", path, good[path], False)
    for path in (SKILL, DESIGN, GUI, DIST, README):
        g = good[path]
        lines = split(g)
        unchanged = next(
            i
            for i, line in enumerate(lines)
            if line == split(FIXTURES[path].encode("utf-8"))[i] and body(line)
        )
        case(
            f"{path}: a second changed line",
            path,
            _swap_line(g, unchanged + 1, body(lines[unchanged]) + " x"),
            True,
            "differs",
        )
        if EOL[path] == "CRLF":
            case(f"{path}: an LF line", path, g.replace(b"\r\n", b"\n", 1), True, "line endings")
        else:
            case(f"{path}: a CRLF line", path, g.replace(b"\n", b"\r\n", 1), True, "line endings")
    case(
        "SKILL: a wrong new text",
        SKILL,
        good[SKILL].replace(b"`~", b"`%USERPROFILE%"),
        True,
        "differs",
    )
    case("design: a wrong new text", DESIGN, good[DESIGN].replace(b"YOU", b"you"), True, "differs")
    case(
        "06-gui: a line one character shorter",
        GUI,
        good[GUI].replace(b" ] [Browse", b"] [Browse", 1),
        True,
        "width",
    )
    keep_extra = FIXTURES[DIST].replace(LINE40_OLD, LINE40_NEW).encode("utf-8")
    case("07: a layout that keeps extra/", DIST, keep_extra, True, "extra/")
    moved = good[DIST].replace(b"avkit-backend/             #", b"avkit-backend/              #")
    case("07: a comment column moved", DIST, moved, True, "column")
    case(
        "README: JSON that no longer parses",
        README,
        good[README].replace(b'av-kit.exe",', b'av-kit.exe"'),
        True,
        "does not parse",
    )
    cmd_lines = split(good[COMMANDS])
    removed = "\n".join(cmd_lines[:0] + cmd_lines[1:]).encode("utf-8")
    case("commands: a removed line", COMMANDS, removed, True, "add-only")
    case(
        "commands: an LF line",
        COMMANDS,
        good[COMMANDS].replace(b"|\r\n| z", b"|\n| z"),
        True,
        "line endings",
    )
    case(
        "capture: a wrong new text",
        CAPTURE,
        good[CAPTURE].replace(b"avkit", b"fixture2"),
        True,
        "differs",
    )
    case(
        "dev-spawn: one line left",
        SPAWN,
        FIXTURES[SPAWN].encode("utf-8").replace(b"fixture", b"avkit", 4),
        True,
        "still hold",
    )
    for f in failures:
        print("SELFTEST FAIL:", f)
    print(f"edit-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv == ["--anchors"]:
        return anchors()
    if len(argv) == 2 and argv[0] == "--group" and argv[1] in ("docs", "tests", "commands"):
        return run_group(argv[1], None)
    if len(argv) == 4 and argv[:3] == ["--group", "register", "--stage"] and argv[3] in ("7", "10"):
        return run_group("register", int(argv[3]))
    print(
        "usage: edit-check.py --group docs|tests|commands | --group register --stage 7|10 | --anchors | --selftest"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
