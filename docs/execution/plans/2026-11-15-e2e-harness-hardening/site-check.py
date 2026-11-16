"""Session 78 launch-site check (AC-9; task row 5 and the session gate's ``site-check`` step).

Usage, from the repository root: ``python site-check.py`` compares ``ui/tests/e2e`` with the BASE
copies row 0 kept under ``BASE_DIR``; ``python site-check.py --selftest`` runs the fixtures below.

It refuses unless all of these hold (implementation-plan.md §Launch-site migration):

1. ``electron-app.ts`` exists and holds exactly one ``_electron.launch(``, and no other file in
   ``ui/tests/e2e`` names ``_electron`` at all (D-933: one launch path);
2. every BASE site file (a BASE file holding ``_electron.launch(``) holds as many
   ``launchElectron(`` calls as BASE held ``_electron.launch(`` calls, in the same order;
3. for each site, the call's object has only the keys ``main`` and ``env``; ``main`` is absent when
   BASE launched ``DEFAULT_ARGS`` and is exactly BASE's single ``args`` element otherwise; and the
   ``env`` object, with ``...process.env`` and ``AVKIT_E2E: '1'`` removed from both sides and
   whitespace ignored, equals BASE's (every app-data folder and every extra variable kept);
4. ``...process.env`` occurs in a BASE site file exactly (BASE count - BASE site count) times, so
   only the region-picker stub spawn (``capture-picker.test.ts``) keeps its own spread;
5. each BASE site file keeps BASE's line endings: CRLF files stay CRLF, LF files stay LF, with no
   mixed endings (Python bytes, never grep);
6. ``theme-probe.ts`` still exports ``launchWithAppData`` (``settings.test.ts`` calls it).

Read-only. Prints one line per site and ends with ``site-check: ok`` or the problem count.
"""

from __future__ import annotations

import pathlib
import re
import sys

E2E = pathlib.Path("ui/tests/e2e")
BASE_DIR = pathlib.Path("C:/Temp/av-kit/e2e-harness-hardening/base")
HELPER = "electron-app.ts"
OLD_CALL = "_electron.launch("
NEW_CALL = "launchElectron("
DEFAULT_ARGS = "[resolve(here,'../../out/main/index.js')]"
DROPPED = ("...process.env", "AVKIT_E2E:'1'")


def _skip_string(text: str, i: int) -> int:
    quote = text[i]
    i += 1
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == quote:
            return i + 1
        i += 1
    raise ValueError("unterminated string")


def _matching(text: str, i: int) -> int:
    """Index just past the bracket that closes the one at ``i`` (strings skipped)."""
    pairs = {"{": "}", "[": "]", "(": ")"}
    stack = [pairs[text[i]]]
    i += 1
    while stack:
        c = text[i]
        if c in "'\"`":
            i = _skip_string(text, i)
            continue
        if c in pairs:
            stack.append(pairs[c])
        elif c == stack[-1]:
            stack.pop()
        i += 1
    return i


def _entries(body: str) -> list[tuple[str, str]]:
    """Top-level ``key: value`` entries of an object body; a shorthand entry maps to itself."""
    parts, depth, start, i = [], 0, 0, 0
    while i < len(body):
        c = body[i]
        if c in "'\"`":
            i = _skip_string(body, i)
            continue
        if c in "{[(":
            depth += 1
        elif c in "}])":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append(body[start:i])
            start = i + 1
        i += 1
    parts.append(body[start:])
    out = []
    for part in (p.strip() for p in parts):
        if not part:
            continue
        m = re.match(r"^([A-Za-z_$][\w$]*)\s*:\s*(.*)$", part, re.S)
        out.append((m.group(1), m.group(2).strip()) if m else (part, part))
    return out


def _squash(text: str) -> str:
    return re.sub(r"\s+", "", text)


def calls(text: str, marker: str) -> list[dict[str, str]]:
    """Each call's object entries, in order of appearance."""
    found = []
    for m in re.finditer(re.escape(marker), text):
        j = m.end()
        while text[j].isspace():
            j += 1
        if text[j] != "{":
            found.append({"<not-an-object>": text[j : j + 40]})
            continue
        end = _matching(text, j)
        found.append(dict(_entries(text[j + 1 : end - 1])))
    return found


def _env_key(value: str) -> str:
    v = _squash(value)
    if v.startswith("{") and v.endswith("}"):
        v = v[1:-1]
    items = [x for x in (_squash(k + ":" + val) if k != val else _squash(k) for k, val in _entries(v)) if x not in DROPPED]
    return ",".join(items)


def endings(data: bytes) -> str:
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n")
    if lf == 0:
        return "none"
    if crlf == lf:
        return "CRLF"
    if crlf == 0:
        return "LF"
    return f"mixed ({crlf} CRLF of {lf})"


def check(base: dict[str, bytes], live: dict[str, bytes]) -> list[str]:
    problems: list[str] = []
    helper = live.get(HELPER)
    if helper is None:
        problems.append(f"{HELPER} is missing")
    elif helper.decode("utf-8").count(OLD_CALL) != 1:
        problems.append(f"{HELPER} must hold exactly one {OLD_CALL}")
    for name, data in sorted(live.items()):
        if name != HELPER and "_electron" in data.decode("utf-8"):
            problems.append(f"{name} still names _electron")
    sites = {n: d for n, d in base.items() if OLD_CALL in d.decode("utf-8")}
    total = 0
    for name, bdata in sorted(sites.items()):
        btext = bdata.decode("utf-8")
        ldata = live.get(name)
        if ldata is None:
            problems.append(f"{name} is missing")
            continue
        ltext = ldata.decode("utf-8")
        old, new = calls(btext, OLD_CALL), calls(ltext, NEW_CALL)
        total += len(old)
        if len(new) != len(old):
            problems.append(f"{name}: {len(old)} BASE launch site(s) but {len(new)} {NEW_CALL} call(s)")
        for k, (o, n) in enumerate(zip(old, new), start=1):
            label = f"{name} site {k}"
            extra = sorted(set(n) - {"main", "env"})
            if extra:
                problems.append(f"{label}: unexpected key(s) {extra}")
            args = _squash(o.get("args", ""))
            if args == DEFAULT_ARGS:
                if "main" in n:
                    problems.append(f"{label}: BASE launched the default main, so main must be absent")
            else:
                inner = args[1:-1] if args.startswith("[") and args.endswith("]") else None
                if inner is None or "," in inner or _squash(n.get("main", "")) != inner:
                    problems.append(f"{label}: main {n.get('main')!r} is not BASE's args element {o.get('args')!r}")
            if _env_key(o.get("env", "")) != _env_key(n.get("env", "{}")):
                problems.append(f"{label}: env differs from BASE once the spread and AVKIT_E2E are dropped: BASE {_env_key(o.get('env', ''))!r} live {_env_key(n.get('env', '{}'))!r}")
            print(f"{label}: main={'default' if 'main' not in n else n['main']} env=[{_env_key(n.get('env', '{}'))}]")
        want_spread = btext.count("...process.env") - len(old)
        got_spread = ltext.count("...process.env")
        if got_spread != want_spread:
            problems.append(f"{name}: ...process.env occurs {got_spread} time(s), expected {want_spread}")
        if endings(ldata) != endings(bdata):
            problems.append(f"{name}: line endings {endings(ldata)}, BASE {endings(bdata)}")
    probe = live.get("theme-probe.ts", b"").decode("utf-8")
    if not re.search(r"export (async )?function launchWithAppData\(", probe):
        problems.append("theme-probe.ts no longer exports launchWithAppData")
    print(f"BASE sites: {total} in {len(sites)} file(s)")
    return problems


def _read(folder: pathlib.Path) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in sorted(folder.iterdir()) if p.is_file() and p.suffix in (".ts", ".cjs")}


# --- selftest fixtures (shaped on the real sites) -------------------------------------------
_HEAD = "import { _electron, expect, test } from '@playwright/test'\n"
_OLD = (
    "const app = await _electron.launch({\n"
    "    args: [resolve(here, '../../out/main/index.js')],\n"
    "    env: {\n      ...process.env,\n      AVKIT_E2E: '1',\n"
    "      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-x-')),\n      ...extraEnv,\n    },\n  })\n"
)
_NEW = (
    "const app = await launchElectron({\n"
    "    env: {\n      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-x-')),\n      ...extraEnv,\n    },\n  })\n"
)
_OLD_MAIN = "const app = await _electron.launch({\n    args: [main],\n    env: { ...process.env, AVKIT_E2E: '1', AVKIT_APP_DATA: dir },\n  })\n"
_NEW_MAIN = "const app = await launchElectron({ main, env: { AVKIT_APP_DATA: dir } })\n"
_PROBE = "export function launchWithAppData(dir: string) {\n  return 1\n}\n"
_HELPER = b"const app = await _electron.launch({ args: [] })\n"
_IMPORT = "import { launchElectron } from './electron-app'\n"


def _fixture(**over: bytes) -> tuple[dict[str, bytes], dict[str, bytes]]:
    base = {
        "a.test.ts": (_HEAD + _OLD).encode(),
        "b.test.ts": (_HEAD + _OLD_MAIN + "spawn(x, { env: { ...process.env, STUB: '1' } })\n").replace("\n", "\r\n").encode(),
        "theme-probe.ts": _PROBE.encode(),
    }
    live = {
        "a.test.ts": (_IMPORT + _NEW).encode(),
        "b.test.ts": (_IMPORT + _NEW_MAIN + "spawn(x, { env: { ...process.env, STUB: '1' } })\n").replace("\n", "\r\n").encode(),
        "theme-probe.ts": _PROBE.encode(),
        HELPER: _HELPER,
    }
    for key, value in over.items():
        name = key.replace("__", ".").replace("_", "-")
        if value == b"<delete>":
            live.pop(name, None)
        else:
            live[name] = value
    return base, live


def selftest() -> int:
    cases = [
        ("migrated", _fixture(), False),
        ("helper-missing", _fixture(electron_app__ts=b"<delete>"), True),
        ("helper-two-launches", _fixture(electron_app__ts=_HELPER + _HELPER), True),
        ("old-import-left", _fixture(a__test__ts=(_HEAD + _NEW).encode()), True),
        ("extra-env-dropped", _fixture(a__test__ts=(_IMPORT + _NEW.replace("      ...extraEnv,\n", "")).encode()), True),
        ("app-data-changed", _fixture(a__test__ts=(_IMPORT + _NEW.replace("avkit-e2e-x-", "avkit-e2e-y-")).encode()), True),
        ("spread-kept", _fixture(a__test__ts=(_IMPORT + _NEW.replace("env: {", "env: { ...process.env,")).encode()), True),
        ("main-added-to-default", _fixture(a__test__ts=(_IMPORT + _NEW.replace("env: {", "main: other, env: {", 1)).encode()), True),
        ("main-dropped", _fixture(b__test__ts=(_IMPORT + "const app = await launchElectron({ env: { AVKIT_APP_DATA: dir } })\nspawn(x, { env: { ...process.env, STUB: '1' } })\n").replace("\n", "\r\n").encode()), True),
        ("stub-spread-removed", _fixture(b__test__ts=(_IMPORT + _NEW_MAIN + "spawn(x, { env: { STUB: '1' } })\n").replace("\n", "\r\n").encode()), True),
        ("crlf-to-lf", _fixture(b__test__ts=(_IMPORT + _NEW_MAIN + "spawn(x, { env: { ...process.env, STUB: '1' } })\n").encode()), True),
        ("site-missing", _fixture(a__test__ts=_IMPORT.encode()), True),
        ("probe-export-gone", _fixture(theme_probe__ts=b"export const x = 1\n"), True),
    ]
    wrong = []
    for name, (base, live), expect_refused in cases:
        problems = check(base, live)
        ok = bool(problems) == expect_refused
        print(f"{name}: {'refused' if problems else 'ok'} (expected {'refused' if expect_refused else 'ok'}) {problems[:1]}")
        if not ok:
            wrong.append(name)
    print(f"site-check selftest: {len(cases)} fixture(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv:
        print(__doc__)
        return 2
    problems = check(_read(BASE_DIR / E2E), _read(E2E))
    for p in problems:
        print("PROBLEM:", p)
    print(f"site-check: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
