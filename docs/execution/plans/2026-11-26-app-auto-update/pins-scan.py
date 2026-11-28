"""Session 106 §Test pins scan (task row 0 and the --check rows; implementation-plan.md
``PIN_GROWTH``).

With no argument it records, into ``baseline-pins.json`` beside this file, which §Test pins files
(``eol-check.PINS``) enumerate a list this plan grows: the renderer-to-main channels of
``ui/src/main/ipc.ts``, the preload keys of ``ui/src/main/preload.ts``, the settings section keys
of ``settings-sections.ts`` or the ``app`` leaves of the core registry. A file enumerates a list
when it names at least two of that list's entries. Two files are set by hand: the E2E harness
census (its launcher allow list may gain the install helper, one entry) and
``login-item-nsh.test.ts`` (row 13's five lines, D-1553).

``--check`` passes when each §Test pins file is its baseline copy, or, for a file that
enumerates, differs from it only by:

* added lines that hold a name of this plan (``PLAN_NAMES``) or hold only brackets and
  punctuation;
* a replaced line whose only change is a number (a count such as ``toHaveLength(22)`` to 25);
* a replaced line that holds a name of this plan and keeps every word of the old line in order
  (an inline list that gains an entry);
* in ``login-item-nsh.test.ts`` only, a replacement of baseline lines 105, 112, 119, 122 and 125.

Any other change is S5. ``--selftest`` runs the fixtures.
"""

from __future__ import annotations

import difflib
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COPIES = pathlib.Path("C:/Temp/av-kit/2026-11-26-app-auto-update/baseline-copies")
OUT = HERE / "baseline-pins.json"


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PINS: dict[str, str] = _load("aau_eol_check_pins", "eol-check.py").PINS
CENSUS = "ui/tests/e2e/electron-harness.test.ts"
LOGIN_NSH = "ui/tests/unit/login-item-nsh.test.ts"
LOGIN_NSH_LINES = frozenset({105, 112, 119, 122, 125})
#: clipboard-image-main.test.ts imports the channel list and pins its length, so the two-name
#: scan misses it; its count line is a count growth (D-1569).
CLIPBOARD_MAIN = "ui/tests/unit/clipboard-image-main.test.ts"
#: test-ids.ts lists the E2E ids, which carry the section keys only inside longer ids, so the
#: two-name scan misses it; row 15 adds the Updates ids (D-1572).
TEST_IDS = "ui/tests/e2e/test-ids.ts"
BY_HAND = {
    CENSUS: ["launcher-allow-list"],
    LOGIN_NSH: ["installer-macro-lines"],
    CLIPBOARD_MAIN: ["channel-count"],
    TEST_IDS: ["test-id-list"],
}

#: The names this plan adds (UPDATE_IPC, UPDATES_CARD, UPDATE_INTERVAL_LEAF, the install helper).
PLAN_NAMES = (
    "update-get-state",
    "update-check",
    "update-install",
    "update-state-changed",
    "updateGetState",
    "updateCheck",
    "updateInstall",
    "onUpdateState",
    "updates-settings",
    "'updates'",
    '"updates"',
    "Updates",
    "UpdatesCard",
    "update_interval",
    "UPDATE_INTERVAL",
    "settings-update-",
    "install-helper",
    "e2e-install",
    "weekly",
    "monthly",
)
PUNCT = re.compile(r"^[\s\[\]{}(),;:]*$")
WORD = re.compile(r"[A-Za-z0-9_$.-]+")
QUOTED = re.compile(r"""['"`]([A-Za-z0-9_.-]+)['"`]""")


def _block(text: str, start: str) -> list[str]:
    i = text.index(start)
    j = text.index("]", i)
    return QUOTED.findall(text[i:j])


def lists(root: pathlib.Path) -> dict[str, list[str]]:
    ipc = (root / "ui/src/main/ipc.ts").read_text(encoding="utf-8")
    pre = (root / "ui/src/main/preload.ts").read_text(encoding="utf-8")
    sec = (root / "ui/src/renderer/src/features/settings/settings-sections.ts").read_text(
        encoding="utf-8"
    )
    reg = (root / "packages/core/src/avkit_core/services/settings.py").read_text(encoding="utf-8")
    return {
        "channels": _block(ipc, "export const RENDERER_TO_MAIN_CHANNELS = ["),
        "preload-keys": _block(pre, "const API_KEYS = ["),
        "sections": sorted(set(re.findall(r"\bkey: '([a-z-]+)'", sec))),
        "app-leaves": sorted(set(re.findall(r'\("app", "([a-z_]+)"\)', reg))),
    }


def record(root: pathlib.Path = ROOT, out: pathlib.Path = OUT) -> dict:
    known = lists(root)
    files: dict[str, dict] = {}
    for path in sorted(PINS):
        p = root / path
        text = p.read_bytes().decode("utf-8", "replace") if p.is_file() else ""
        kinds = []
        for kind, names in known.items():
            hits = [n for n in names if re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", text)]
            if len(hits) >= 2:
                kinds.append(kind)
        kinds += BY_HAND.get(path, [])
        digest = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "absent"
        files[path] = {"enumerates": bool(kinds), "kinds": kinds, "sha256": digest}
    data = {"lists": {k: len(v) for k, v in known.items()}, "files": files}
    out.write_bytes((json.dumps(data, indent=2) + "\n").encode("utf-8"))
    for path, info in files.items():
        what = "enumerates " + ",".join(info["kinds"]) if info["enumerates"] else "no list"
        print(f"pins-scan {path}: {what}")
    enumerating = sum(f["enumerates"] for f in files.values())
    print(f"pins-scan: recorded {enumerating}/{len(files)} enumerating")
    return data


def _lines(raw: bytes) -> list[str]:
    return raw.decode("utf-8").replace("\r\n", "\n").split("\n")


def _named(line: str) -> bool:
    return any(n in line for n in PLAN_NAMES)


def _grows(old: str, new: str) -> bool:
    if re.sub(r"\d+", "#", old) == re.sub(r"\d+", "#", new):
        return True
    if not _named(new):
        return False
    it = iter(WORD.findall(new))
    return all(w in it for w in WORD.findall(old))


def diff_problems(path: str, base: bytes, now: bytes, enumerates: bool) -> list[str]:
    if base == now:
        return []
    if not enumerates:
        return [f"{path}: changed but does not enumerate a list (must stay byte-identical)"]
    a, b = _lines(base), _lines(now)
    problems: list[str] = []
    ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            continue
        if tag == "insert":
            for k in range(j1, j2):
                if not (_named(b[k]) or PUNCT.match(b[k])):
                    problems.append(
                        f"{path}:{k + 1} added line holds no name of this plan: {b[k].strip()[:90]}"
                    )
            continue
        if tag == "delete":
            problems.append(f"{path}:{i1 + 1}-{i2} lines removed")
            continue
        # replace
        if (
            path == LOGIN_NSH
            and set(range(i1 + 1, i2 + 1)) <= LOGIN_NSH_LINES
            and i2 - i1 == j2 - j1
        ):
            for k in range(i1, i2):
                print(f"pins-scan note {path}:{k + 1} row 13 line replaced")
            continue
        if i2 - i1 == j2 - j1 and all(_grows(a[i1 + k], b[j1 + k]) for k in range(i2 - i1)):
            for k in range(i2 - i1):
                print(f"pins-scan note {path}:{i1 + k + 1} grows: {b[j1 + k].strip()[:90]}")
            continue
        problems.append(f"{path}:{i1 + 1}-{i2} changed beyond PIN_GROWTH")
    return problems


def check(
    root: pathlib.Path = ROOT, copies: pathlib.Path = COPIES, rec: pathlib.Path = OUT
) -> list[str]:
    files = json.loads(rec.read_text(encoding="utf-8"))["files"]
    problems: list[str] = []
    for path, info in sorted(files.items()):
        base_p, now_p = copies / path, root / path
        if not base_p.is_file() or not now_p.is_file():
            if base_p.is_file() != now_p.is_file():
                problems.append(f"{path}: present in only one of baseline and tree")
            continue
        got = diff_problems(path, base_p.read_bytes(), now_p.read_bytes(), info["enumerates"])
        state = (
            "unchanged"
            if base_p.read_bytes() == now_p.read_bytes()
            else ("ok" if not got else "S5")
        )
        print(f"pins-scan --check {path}: {state}")
        problems += got
    return problems


def selftest() -> int:
    base = "a\r\n  expect(x).toHaveLength(22)\r\n  ['login-item-get', 'login-item-set'],\r\n]\r\n"
    cases = [
        ("unchanged passes", base, base, True, True),
        (
            "added named line passes",
            base,
            base.replace("]\r\n", "  'update-check',\r\n]\r\n"),
            True,
            True,
        ),
        ("count change passes", base, base.replace("22", "25"), True, True),
        (
            "inline list growth passes",
            base,
            base.replace("'login-item-set'],", "'login-item-set', 'update-check'],"),
            True,
            True,
        ),
        (
            "added foreign line fails",
            base,
            base.replace("]\r\n", "  'other-thing',\r\n]\r\n"),
            True,
            False,
        ),
        ("changed assertion fails", base, base.replace("toHaveLength", "toBe"), True, False),
        ("removed line fails", base, base.replace("a\r\n", ""), True, False),
        ("non-enumerating change fails", base, base.replace("22", "25"), False, False),
    ]
    bad = 0
    for name, a, b, enum, want in cases:
        got = diff_problems("f.ts", a.encode(), b.encode(), enum)
        ok = (not got) == want
        bad += 0 if ok else 1
        print(f"selftest {'ok ' if ok else 'BAD'} {name}: {got}")
    nsh = "".join(f"line {n}\n" for n in range(1, 131))
    for name, lines, want in (
        ("login-item-nsh named lines pass", (105, 112), True),
        ("login-item-nsh other line fails", (106,), False),
    ):
        now = nsh
        for n in lines:
            now = now.replace(f"line {n}\n", f"line {n} RMDir /r\n")
        got = diff_problems(LOGIN_NSH, nsh.encode(), now.encode(), True)
        ok = (not got) == want
        bad += 0 if ok else 1
        print(f"selftest {'ok ' if ok else 'BAD'} {name}: {got}")
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        files = {
            "ui/src/main/ipc.ts": (
                "export const RENDERER_TO_MAIN_CHANNELS = [\n"
                "  'get-token',\n  'login-item-get',\n] as const\n"
            ),
            "ui/src/main/preload.ts": "const API_KEYS = [\n  'getToken',\n  'getBackendUrl',\n]\n",
            "ui/src/renderer/src/features/settings/settings-sections.ts": (
                "{ key: 'startup' }, { key: 'console' }\n"
            ),
            "packages/core/src/avkit_core/services/settings.py": (
                '("app", "log_level") ("app", "log_to_file")\n'
            ),
        }
        for k, v in files.items():
            (root / k).parent.mkdir(parents=True, exist_ok=True)
            (root / k).write_text(v, encoding="utf-8")
        known = lists(root)
        ok = known["channels"] == ["get-token", "login-item-get"] and known["app-leaves"] == [
            "log_level",
            "log_to_file",
        ]
        bad += 0 if ok else 1
        print(f"selftest {'ok ' if ok else 'BAD'} lists read the four sources: {known}")
    total = len(cases) + 3
    print(f"pins-scan selftest: {total - bad}/{total} ok")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv == ["--check"]:
        problems = check()
        for p in problems:
            print("PROBLEM:", p)
        print(f"pins-scan --check: {len(problems)} problem(s)")
        return 1 if problems else 0
    if not argv:
        record()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
