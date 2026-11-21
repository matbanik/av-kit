"""Session 100 static clipboard-writer scan (plan time, row 1's Red count, row 2's Green and the
gate's ``writer-scan`` step; implementation-plan.md §The static scan; AC-5; D-1312, D-1326).

The same patterns as the tracked Vitest scan ``ui/tests/unit/e2e-clipboard-guard.test.ts``
(``AC-5``), in Python so the plan can count the writers at ``f1ba411`` before that test exists.
It reads every ``*.ts``, ``*.cjs`` and ``*.mjs`` file under ``ui/tests/e2e`` (fixtures included)
except the gated files that ``tools/e2e_host/known-failures.json`` names and the guard's own two
files (``ALLOWED_FILES``), and prints one line per hit as ``<file>:<line>: <kind>: <source>``::

    python writer-scan.py                  # the tree as it is; exit 0 when no hit, else 1
    python writer-scan.py --expect N       # exit 0 only when there are exactly N hits (Red)
    python writer-scan.py --root DIR --gated A --gated B   # another tree (plan-time counts)
    python writer-scan.py --selftest       # the patterns on fixtures

Each pattern runs over the whole file text, so a chain split across lines still matches; the line
is the line of the match's first character. A hit is:

- a test-side clipboard call (``clipboard.read*``, ``write*``, ``clear``, ``has``,
  ``available*``), any ``navigator.clipboard``, ``execCommand('copy'|'cut')``;
- a native copy (``webContents.copy(``, ``wc.cut(`` and the like, and ``.copyImageAt(`` on any
  receiver);
- a copy or cut chord in a ``press(`` (``Control``, ``Meta`` or ``ControlOrMeta`` with ``C``,
  ``X``, ``KeyC``, ``KeyX`` or ``Insert``, and ``Shift+Delete``; any case);
- a native paste (plan review round 1 EDC-R1-1, D-1331): ``.paste(`` on any receiver, any
  ``pasteAndMatchStyle`` and ``execCommand('paste')``; and a paste chord in a ``press(``
  (``Control``, ``Meta`` or ``ControlOrMeta`` with ``V`` or ``KeyV``, ``Shift`` before or after
  the modifier allowed, so ``Control+Shift+V``; and ``Shift+Insert``; any case). A click on the
  TTS ``paste-btn`` is not a hit: the product's ``readClipboard`` returns ``'pasted'`` under
  ``AVKIT_E2E=1`` (``index.ts:405-409``), and the runtime guard's readers catch anything else.
  ``replace(`` and ``replaceMisspelling(`` insert their own text and read no clipboard;
- a click, double click, press or tap (``.first()``, ``.last()`` or ``.nth(n)`` allowed before
  it) on a copy locator: a test id or a ``locator('...')`` CSS string that holds ``copy`` (but
  ``ALLOWED_IDS``), a test-id constant whose name holds ``copy``, ``WRITER_IDS``, or a role, text,
  label or title locator whose argument holds ``copy`` as a word start (``'Copy path'``,
  ``/copy/i``); any case;
- the same action on a variable bound to such a locator (``const b = page.getByTestId('x-copy')``
  then ``b.click()``), the binding's chained continuation lines included;
- a ``_electron.launch(``, except in ``electron-app.ts`` and ``electron-env.ts``, which are
  exempt from that kind only.

Exit 2 is a setup failure (the folder or the known list missing or unreadable). It reads only
repository files (or ``--root``) and writes nothing. What it cannot see (a locator built by a
helper function, a test id assembled at run time) is the runtime guard's job (AC-8 to AC-10).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("P:/av-kit")
E2E = ROOT / "ui/tests/e2e"
KNOWN = ROOT / "tools/e2e_host/known-failures.json"
# The guard's own files: the preload and the guard's spec, which calls only tagged replacements
# (D-1313, D-1320). The launch helpers are exempt from the launch kind only (D-1326).
ALLOWED_FILES = ("clipboard-guard.cjs", "clipboard-guard.test.ts")
LAUNCH_FILES = ("electron-app.ts", "electron-env.ts")
#: D-1342 (coordinator ruling): Session 99's new E2E file. A hit there is printed as a Session 99
#: finding for the coordinator and not counted; this session's files are never set aside.
PEER_FILES = ("help-quick-start.test.ts",)
# Not clipboard writers: a settings toggle that saves copy_to_clipboard (no capture follows in its
# test), and the converter's stream-copy mode radios (ConvertPage.tsx:789-790).
ALLOWED_IDS = ("settings-leaf-copy_to_clipboard", "convert-copy-fast", "convert-copy-reencode")
# Writers whose id does not hold "copy" (SettingsPage.tsx: copyMcp(true)).
WRITER_IDS = ("pin-mcp-btn",)
Q = "['\"`]"
NQ = "[^'\"`]"
PICK = r"(?:\s*\.\s*(?:first|last)\(\s*\)|\s*\.\s*nth\(\s*\d+\s*\))*"
ACT = PICK + r"\s*\.\s*(?:click|dblclick|press|tap)\("
# Copy locators, without the action (used for the click kinds and for variable bindings).
LOC_ID = re.compile(r"getByTestId\(\s*" + Q + "(" + NQ + "*copy" + NQ + r"*)" + Q + r"\s*\)", re.I)
LOC_CONST = re.compile(r"getByTestId\(\s*([A-Za-z_$][\w$.]*)\s*\)")
LOC_WRITER = re.compile(
    r"getByTestId\(\s*" + Q + "(" + "|".join(map(re.escape, WRITER_IDS)) + ")" + Q + r"\s*\)"
)
LOC_TEXT = re.compile(r"getBy(?:Role|Text|Label|Title)\(([^)]*)\)")
LOC_CSS = re.compile(r"\.locator\(\s*" + Q + "(" + NQ + "*copy" + NQ + r"*)" + Q + r"\s*\)", re.I)
COPY_WORD = re.compile(r"\bcopy", re.I)
SIMPLE = (
    (
        "clipboard-call",
        re.compile(
            r"(?<!navigator\.)\bclipboard\s*\.\s*(?:read|write|clear|has|available)\w*\s*\("
        ),
    ),
    ("navigator-clipboard", re.compile(r"\bnavigator\s*\.\s*clipboard\b")),
    ("exec-copy", re.compile(r"execCommand\(\s*" + Q + "(?:copy|cut)" + Q, re.I)),
    ("exec-paste", re.compile(r"execCommand\(\s*" + Q + "paste" + Q, re.I)),
    (
        "native-copy",
        re.compile(r"\b(?:webContents|wc|contents)\s*\??\s*\.\s*(?:copy|cut)\s*\(", re.I),
    ),
    ("native-copy", re.compile(r"\.\s*copyImageAt\s*\(")),
    ("native-paste", re.compile(r"\.\s*paste\s*\(")),
    ("native-paste", re.compile(r"\bpasteAndMatchStyle\b")),
    (
        "paste-chord",
        re.compile(
            r"\.press\(\s*"
            + Q
            + NQ
            + r"*(?:\b(?:Shift\+)?(?:Control|Meta|ControlOrMeta)\+(?:Shift\+)?(?:v|KeyV)"
            + r"|\bShift\+Insert)"
            + Q,
            re.I,
        ),
    ),
    (
        "copy-chord",
        re.compile(
            r"\.press\(\s*"
            + Q
            + NQ
            + r"*(?:\b(?:Control|Meta|ControlOrMeta)\+(?:[cx]|Key[cx]|Insert)|\bShift\+Delete)"
            + Q,
            re.I,
        ),
    ),
    ("electron-launch", re.compile(r"_electron\s*\.\s*launch\(")),
)
BINDING = re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*")


def gated_files(known_text: str) -> list[str]:
    data = json.loads(known_text)
    return sorted({str(row["file"]) for row in data.get("gated", [])})


def copy_locators(text: str) -> list[tuple[int, int, str]]:
    """Every copy locator in ``text`` as (start, end, kind); the allowed ids are left out."""
    out: list[tuple[int, int, str]] = []
    for match in LOC_ID.finditer(text):
        if match.group(1) not in ALLOWED_IDS:
            out.append((match.start(), match.end(), "copy-id-click"))
    for match in LOC_CONST.finditer(text):
        if "copy" in match.group(1).lower():
            out.append((match.start(), match.end(), "copy-const-click"))
    for match in LOC_WRITER.finditer(text):
        out.append((match.start(), match.end(), "writer-id-click"))
    for match in LOC_TEXT.finditer(text):
        if COPY_WORD.search(match.group(1)):
            out.append((match.start(), match.end(), "copy-locator-click"))
    for match in LOC_CSS.finditer(text):
        if not any(allowed in match.group(1) for allowed in ALLOWED_IDS):
            out.append((match.start(), match.end(), "copy-css-click"))
    return out


def binding_text(text: str, start: int) -> str:
    """The bound expression: the rest of the line plus each following line starting ``.``."""
    end = text.find("\n", start)
    end = len(text) if end < 0 else end
    while end < len(text):
        nxt = text.find("\n", end + 1)
        nxt = len(text) if nxt < 0 else nxt
        if not text[end + 1 : nxt].lstrip().startswith("."):
            break
        end = nxt
    return text[start:end]


def hits_in(name: str, text: str) -> list[tuple[str, int, str]]:
    found: list[tuple[int, str]] = []
    for kind, pattern in SIMPLE:
        for match in pattern.finditer(text):
            if kind == "electron-launch" and name in LAUNCH_FILES:
                continue
            found.append((match.start(), kind))
    act = re.compile(ACT)
    for start, end, kind in copy_locators(text):
        if act.match(text, end):
            found.append((start, kind))
    for match in BINDING.finditer(text):
        expr = binding_text(text, match.end())
        if not copy_locators(expr) or re.match(r".*" + ACT, expr, re.S):
            continue
        use = re.compile(r"(?<![\w$.])" + re.escape(match.group(1)) + ACT)
        for call in use.finditer(text, match.end()):
            found.append((call.start(), "copy-var-click"))
    out: list[tuple[str, int, str]] = []
    for start, kind in sorted(found):
        number = text.count("\n", 0, start) + 1
        line = text.splitlines()[number - 1] if text else ""
        out.append((kind, number, line.strip()[:140]))
    return out


def scan(folder: pathlib.Path, gated: list[str]) -> list[str]:
    lines: list[str] = []
    for path in sorted(folder.rglob("*")):
        if path.suffix not in (".ts", ".cjs", ".mjs") or not path.is_file():
            continue
        if path.name in gated or path.name in ALLOWED_FILES:
            continue
        text = path.read_bytes().decode("utf-8")
        rel = path.relative_to(folder).as_posix()
        lines += [f"{rel}:{n}: {kind}: {src}" for kind, n, src in hits_in(path.name, text)]
    return lines


def split_peer(lines: list[str]) -> tuple[list[str], list[str]]:
    """(this session's hits, Session 99's hits), by the hit's file path."""
    peer = [ln for ln in lines if ln.split(":", 1)[0] in PEER_FILES]
    return [ln for ln in lines if ln not in peer], peer


CASES = [
    (
        "a.test.ts",
        "await app.evaluate(({ clipboard }) => clipboard.writeText('s'))",
        ["clipboard-call"],
    ),
    (
        "a.test.ts",
        "const t = await app.evaluate(({ clipboard }) => clipboard.readText())",
        ["clipboard-call"],
    ),
    ("a.test.ts", "await page.getByTestId('console-copy').click()", ["copy-id-click"]),
    ("a.test.ts", "await page.getByTestId(MCP_COPY_PROMPT_BTN).click()", ["copy-const-click"]),
    ("a.test.ts", "await page.getByTestId(ids.copyButton).dblclick()", ["copy-const-click"]),
    ("a.test.ts", "await page.getByTestId('pin-mcp-btn').click()", ["writer-id-click"]),
    ("a.test.ts", "await page.getByTestId('settings-leaf-copy_to_clipboard').click()", []),
    ("a.test.ts", "await expect(page.getByTestId('copy-mcp-btn')).toBeVisible()", []),
    ("a.test.ts", "await page.keyboard.press('Control+C')", ["copy-chord"]),
    ("a.test.ts", "await page.keyboard.press('ControlOrMeta+x')", ["copy-chord"]),
    ("a.test.ts", "await page.keyboard.press('Control+KeyC')", ["copy-chord"]),
    ("a.test.ts", "await page.keyboard.press('Control+Insert')", ["copy-chord"]),
    ("a.test.ts", "await field.press('Shift+Delete')", ["copy-chord"]),
    # Paste (plan review round 1 EDC-R1-1, D-1331): hits, and their near misses.
    ("a.test.ts", "await page.keyboard.press('Control+V')", ["paste-chord"]),
    ("a.test.ts", "await page.keyboard.press('Shift+Insert')", ["paste-chord"]),
    ("a.test.ts", "await page.keyboard.press('Control+Shift+V')", ["paste-chord"]),
    ("a.test.ts", "await page.keyboard.press('Shift+Control+v')", ["paste-chord"]),
    ("a.test.ts", "await field.press('ControlOrMeta+KeyV')", ["paste-chord"]),
    ("a.test.ts", "await page.keyboard.press('Meta+v')", ["paste-chord"]),
    ("a.test.ts", "await page.keyboard.press('v')", []),
    ("a.test.ts", "await page.keyboard.press('Shift+V')", []),
    ("a.test.ts", "await page.keyboard.press('Insert')", []),
    ("a.test.ts", "await page.keyboard.press('Control+Verbose')", []),
    ("a.test.ts", "await app.evaluate(() => wc.paste())", ["native-paste"]),
    (
        "a.test.ts",
        "BrowserWindow.getAllWindows()[0]\n  .webContents\n  .paste()",
        ["native-paste"],
    ),
    ("a.test.ts", "contents.pasteAndMatchStyle()", ["native-paste"]),
    ("a.test.ts", "const m = 'pasteAndMatchStyle'", ["native-paste"]),
    ("a.test.ts", "document.execCommand('paste')", ["exec-paste"]),
    ("a.test.ts", "wc.copyImageAt(10, 20)", ["native-copy"]),
    ("a.test.ts", "await page.getByTestId('paste-btn').click()", []),
    ("a.test.ts", "wc.replace('x'); wc.replaceMisspelling('y')", []),
    ("a.test.ts", "// AC-132.23 (a paste) in the real app; const pasted = 1", []),
    ("a.test.ts", "await page.keyboard.press('Delete')", []),
    (
        "a.test.ts",
        "await page.evaluate(() => navigator.clipboard.writeText('x'))",
        ["navigator-clipboard"],
    ),
    ("a.test.ts", "document.execCommand('copy')", ["exec-copy"]),
    ("a.test.ts", "await app.evaluate(({ BrowserWindow }) => wc.copy())", ["native-copy"]),
    (
        "a.test.ts",
        "BrowserWindow.getAllWindows()[0].webContents.cut()",
        ["native-copy"],
    ),
    (
        "a.test.ts",
        "await page.getByRole('menuitem', { name: 'Copy path' }).click()",
        ["copy-locator-click"],
    ),
    (
        "a.test.ts",
        "await page.getByRole('button', { name: /copy/i }).first().click()",
        ["copy-locator-click"],
    ),
    ("a.test.ts", "await page.getByText('copy link').nth(1).tap()", ["copy-locator-click"]),
    ("a.test.ts", "await page.getByRole('button', { name: 'Photocopy' }).click()", []),
    (
        "a.test.ts",
        "await page\n    .getByTestId('console-copy')\n    .click()",
        ["copy-id-click"],
    ),
    ("a.test.ts", "await page.locator('[data-testid=console-copy]').click()", ["copy-css-click"]),
    (
        "a.test.ts",
        'await page.locator("[data-menu-action=copy-location]").last().click()',
        ["copy-css-click"],
    ),
    ("a.test.ts", "await page.locator('[data-testid=convert-copy-fast]').click()", []),
    (
        "a.test.ts",
        "const btn = page.getByTestId('console-copy')\nawait expect(btn).toBeVisible()\n"
        "await btn.click()",
        ["copy-var-click"],
    ),
    (
        "a.test.ts",
        "const item = page\n  .getByRole('menuitem', { name: /copy/i })\n  .first()\n"
        "await item.click()",
        ["copy-var-click"],
    ),
    (
        "a.test.ts",
        "const btn = page.getByTestId('console-copy')\nawait expect(btn).toBeVisible()",
        [],
    ),
    ("a.test.ts", "const app = await _electron.launch({ args })", ["electron-launch"]),
    ("electron-app.ts", "app = await _electron.launch({", []),
    ("electron-env.ts", "app = await _electron.launch({", []),
    (
        "electron-app.ts",
        "await app.evaluate(({ clipboard }) => clipboard.clear())",
        ["clipboard-call"],
    ),
    ("a.test.ts", "// copy_to_clipboard: false", []),
    ("a.test.ts", "await panel.getByTestId('convert-copy-reencode').click()", []),
]


def selftest() -> int:
    bad = []
    for name, text, want in CASES:
        got = [kind for kind, _n, _s in hits_in(name, text)]
        if got != want:
            bad.append((text, want, got))
    lines = hits_in("a.test.ts", "x\ny\nawait page\n  .getByTestId('console-copy')\n  .click()")
    if [n for _k, n, _s in lines] != [4]:
        bad.append(("line of a split chain", [4], [n for _k, n, _s in lines]))
    known = '{"known": [], "skip": [], "gated": [{"label": "mini-air", "file": "b.test.ts", "reason": "r"}, {"label": "mini-air", "file": "a.test.ts", "reason": "r"}]}'  # noqa: E501
    if gated_files(known) != ["a.test.ts", "b.test.ts"]:
        bad.append(("gated_files", ["a.test.ts", "b.test.ts"], gated_files(known)))
    for row in bad:
        print("selftest FAIL:", row)
    own, peer = split_peer(
        [
            "a.test.ts:1: copy-chord: x",
            "help-quick-start.test.ts:2: copy-id-click: y",
            "sub/help-quick-start.test.ts:3: copy-id-click: z",
        ]
    )
    if len(own) != 2 or len(peer) != 1:
        bad.append(("split_peer (D-1342)", (2, 1), (len(own), len(peer))))
    total = len(CASES) + 3
    print(f"writer-scan selftest: {total - len(bad)} of {total} cases pass")
    return 1 if bad else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--expect", type=int, default=None)
    parser.add_argument("--root", type=pathlib.Path, default=None)
    parser.add_argument("--gated", action="append", default=None)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    folder = args.root or E2E
    try:
        gated = (
            args.gated
            if args.gated is not None
            else gated_files(KNOWN.read_bytes().decode("utf-8"))
        )
        if not folder.is_dir():
            raise OSError(f"{folder} is not a folder")
    except (OSError, ValueError, KeyError) as error:
        print(f"writer-scan: setup failure: {error}")
        return 2
    lines, peer = split_peer(scan(folder, sorted(gated)))
    print("gated files:", sorted(gated))
    for line in peer:
        print("Session 99 finding (D-1342, not counted):", line)
    print(f"writer-scan: {len(peer)} hit(s) in Session 99's file")
    for line in lines:
        print(line)
    print(f"writer-scan: {len(lines)} hit(s) outside the gated files")
    if args.expect is not None:
        return 0 if len(lines) == args.expect else 1
    return 0 if not lines else 1


if __name__ == "__main__":
    sys.exit(main())
