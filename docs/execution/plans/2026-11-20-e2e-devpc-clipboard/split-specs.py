"""Session 100 statement-level move of the dev-PC clipboard steps (task rows 0 to 2, the gate;
D-1305, D-1306, D-1307, D-1308, D-1309, D-1327, D-1328; AC-1 to AC-4).

Builds four files from the BASE commit's blobs, never from the working tree:

  ui/tests/e2e/copy-system-clipboard.test.ts  new, LF: a header, mcp-setup-prompt's imports and
                                              helpers (lines 1-14 and 28-84, byte for byte), the
                                              GUARD lines, and three tests whose clipboard lines
                                              are copied byte for byte: C1-5's route and copy
                                              (console 79-93, two more spaces of indent inside
                                              try/finally; D-1328), AC-71.15 (b) (mcp 99,
                                              106-114) and AC-71.15 (d) (mcp 136-149)
  ui/tests/e2e/console-chrome.test.ts         CRLF kept: minus lines 90-93, C1-5 retitled, one
                                              named comment line
  ui/tests/e2e/mcp-setup-prompt.test.ts       CRLF kept: minus (b) 106-115 and (d)'s clipboard
                                              part 138-150, both tests retitled, the two import
                                              names only (b) used dropped, launchApp(token?)
                                              seeding a throwaway token (D-1307), and one new
                                              line after (e): the token file still holds the
                                              seed (D-1327)
  ui/tests/e2e/settings.test.ts               CRLF kept: W4-3 minus its copy-mcp-btn and
                                              pin-mcp-btn clicks (216-217; D-1308), one named
                                              comment line

Every edit is a named base line range whose first line is pinned (ANCHORS), so a different base
fails as a setup error. Usage:

  split-specs.py --out DIR    write the four files under DIR (nothing tracked is touched);
                              refuses, exit 1, when any of them already exists there
  split-specs.py --write      write them into ui/tests/e2e; refuses unless each kept file equals
                              its BASE blob in checkout form (LF blob -> CRLF; D-1286) and the new
                              file is absent (NO_PARTIAL: temp files first, then renamed)
  split-specs.py --check      exit 0 when the four tracked files equal the built ones and every
                              invariant holds; exit 1 with each difference named
  split-specs.py --selftest   builds in memory, checks the invariants, and proves that a changed
                              assertion, a lost moved line, a lost route line, a test without
                              its try/finally, a lost token-file check, a CRLF new file, an LF
                              kept file, a clipboard writer left in a kept file, a new file
                              without its guard, a lost title, a moved anchor and an --out
                              folder that already holds a file are each refused

Invariants: every code line the kept files lose is in the new file (with two more spaces of
indent when its range is an "indent" step), but the two W4-3 clicks the plan retires (RETIRED);
each copied range is one contiguous block in the new file; each new test closes its app in a
finally; the kept AC-71.15 Advanced test holds the TOKEN_CHECK line once; the new file holds
the three NEW_TITLES once each and the GUARD lines once,
after its imports and before its first test, and no other test.skip; each kept file holds its base
titles with the RENAMED ones swapped, each once; no kept file has a writer-scan.py hit; the new
file is LF only and the kept files CRLF only. Exit 2 is a setup failure (git, or an anchor).
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = "f1ba411"
E2E = "ui/tests/e2e"
CON = "console-chrome.test.ts"
MCP = "mcp-setup-prompt.test.ts"
SET = "settings.test.ts"
NEW = "copy-system-clipboard.test.ts"
KEPT = (CON, MCP, SET)

GATE_ENV = "AVKIT_E2E_CLIPBOARD_GATED"
GUARD_REASON = "system clipboard spec: runs only in the gated stage on the second Windows host"
#: D-1305: the same file-level skip as capture-system-clipboard.test.ts (Session 98 D-1282).
GUARD = [
    "// Session 100 (D-1305): as in capture-system-clipboard.test.ts, only the gated stage of",
    f"// tools/e2e_host/run-e2e.ps1 sets {GATE_ENV}=1. Every other run, the dev PC's",
    "// included, lists these tests as skipped.",
    "test.skip(",
    f"  process.env.{GATE_ENV} !== '1',",
    f"  '{GUARD_REASON}',",
    ")",
]
NEW_HEADER = [
    "// Session 100 (D-1305): the E2E steps that write or read the system clipboard, moved with",
    "// their assertions unchanged from console-chrome.test.ts (C1-5) and mcp-setup-prompt.test.ts",
    "// (AC-71.15 (b) and (d)). The clipboard is shared with the whole desktop, so this file never",
    "// runs on the dev PC (flake-run.py EXCLUDED); on the mini-air, tools/e2e_host/known-failures.json",  # noqa: E501
    "// names how it runs (gated by the remote-session probe, or skipped).",
    "",
]
NEW_TITLES = [
    "C1-5 console copy writes the visible logs to the clipboard",
    "AC-71.15 (b) Copy prompt fills the clipboard with the Codex setup prompt",
    "AC-71.15 (d) Copy MCP config puts a non-empty app token on the clipboard",
]
#: D-1309: old title -> new title in the kept files.
RENAMED = {
    CON: {
        "C1-5 copy writes clipboard and log-to-file PUTs settings/app": "C1-5 log-to-file PUTs settings/app",  # noqa: E501
    },
    MCP: {
        "AC-71.15 Codex prompt carries execPath and app data, Copy prompt fills the clipboard, Claude Desktop disables scope": "AC-71.15 Codex prompt carries execPath and app data, Claude Desktop disables scope",  # noqa: E501
        "AC-71.15 Advanced starts closed and holds Copy MCP config; no setup prompt contains the token it copies": "AC-71.15 Advanced starts closed and holds Copy MCP config; no setup prompt contains the app token",  # noqa: E501
    },
    SET: {},
}
#: The first line of each edited or copied base range, stripped (a different base is a setup error).
ANCHORS = {
    (CON, 77): "test('C1-5 copy writes clipboard and log-to-file PUTs settings/app'",
    (CON, 79): "const putBodies: string[] = []",
    (CON, 87): "await expect(page.getByTestId('header-console-btn')).toBeVisible()",
    (CON, 90): "const visibleLogs = await page.locator(",
    (CON, 93): "expect(clipboard).toBe(visibleLogs)",
    (
        MCP,
        1,
    ): "import { expect, test, type ElectronApplication, type Page } from '@playwright/test'",
    (MCP, 2): "import { mkdtempSync } from 'node:fs'",
    (MCP, 10): "MCP_COPY_PROMPT_BTN,",
    (MCP, 11): "MCP_PROMPT_STATUS,",
    (MCP, 14): "} from './test-ids'",
    (
        MCP,
        28,
    ): "async function launchApp(): Promise<{ app: ElectronApplication; appData: string }> {",
    (MCP, 29): "const appData = mkdtempSync(join(tmpdir(), 'avkit-e2e-mcp-prompt-'))",
    (MCP, 83): "}",
    (MCP, 91): "test('AC-71.15 Codex prompt carries execPath and app data, Copy prompt fills",
    (MCP, 93): "try {",
    (MCP, 99): "const text = await showPrompt(page, 'codex', 'Codex', 'user')",
    (MCP, 106): "// (b) Copy prompt: the main-process clipboard holds exactly the viewer text.",
    (MCP, 114): "await expect(page.getByTestId(MCP_PROMPT_STATUS)).toHaveText(",
    (MCP, 116): "// (c) Claude Desktop has no project file",
    (MCP, 121): "} finally {",
    (MCP, 126): "test('AC-71.15 Advanced starts closed and holds Copy MCP config; no setup prompt",
    (MCP, 127): "const { app } = await launchApp()",
    (MCP, 136): "await page.getByTestId(MCP_ADVANCED_SUMMARY).click()",
    (MCP, 138): "// Same clipboard-lock race as (b)",
    (MCP, 149): "expect(token.length).toBeGreaterThan(0)",
    (
        MCP,
        151,
    ): "// (e) No viewer text for any client, at any scope it offers, contains that token.",
    (MCP, 162): "} finally {",
    (SET, 215): "await page.getByTestId('mcp-advanced-summary').click()",
    (SET, 216): "await page.getByTestId('copy-mcp-btn').click()",
    (SET, 217): "await page.getByTestId('pin-mcp-btn').click()",
}
SEED = "`${token}\\n`"
#: D-1327: after (e), the app's token file still holds the seed, so (e) checked the token the app
#: uses (a new assertion line that row 2 names; no existing assertion line changes).
TOKEN_CHECK = f"    expect(readFileSync(join(appData, 'mcp-token.txt'), 'utf8')).toBe({SEED})"
#: Kept-file edits: (first, last, replacement lines) on 1-based base lines, inclusive; last =
#: first - 1 inserts before first.
EDITS: dict[str, list[tuple[int, int, list[str]]]] = {
    CON: [
        (
            77,
            77,
            [
                "// Session 100 (D-1305): C1-5's copy step runs in copy-system-clipboard.test.ts (gated stage only).",  # noqa: E501
                "test('C1-5 log-to-file PUTs settings/app', async () => {",
            ],
        ),
        (90, 93, []),
    ],
    MCP: [
        (2, 1, ["import { randomUUID } from 'node:crypto'"]),
        (2, 2, ["import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs'"]),
        (10, 11, []),
        (
            28,
            28,
            [
                "async function launchApp(token?: string): Promise<{ app: ElectronApplication; appData: string }> {"  # noqa: E501
            ],
        ),
        (
            30,
            29,
            [
                "  // Session 100 (D-1307): a test that needs the app's MCP token seeds a throwaway one in its own",  # noqa: E501
                "  // scratch app data, which readOrCreateMcpToken (src/main/index.ts) reads instead of making one.",  # noqa: E501
                f"  if (token !== undefined) writeFileSync(join(appData, 'mcp-token.txt'), {SEED}, {{ encoding: 'utf8' }})",  # noqa: E501
            ],
        ),
        (
            91,
            91,
            [
                "test('AC-71.15 Codex prompt carries execPath and app data, Claude Desktop disables scope', async () => {"  # noqa: E501
            ],
        ),
        (
            106,
            115,
            [
                "    // Session 100 (D-1305): (b) Copy prompt runs in copy-system-clipboard.test.ts (gated stage only).",  # noqa: E501
                "",
            ],
        ),
        (
            126,
            127,
            [
                "test('AC-71.15 Advanced starts closed and holds Copy MCP config; no setup prompt contains the app token', async () => {",  # noqa: E501
                "  const token = randomUUID()",
                "  const { app, appData } = await launchApp(token)",
            ],
        ),
        (
            138,
            151,
            [
                "    // Session 100 (D-1305): (d)'s Copy MCP config read runs in copy-system-clipboard.test.ts (gated stage only).",  # noqa: E501
                "",
                "    // (e) No viewer text for any client, at any scope it offers, contains the app's token (seeded at launch, D-1307).",  # noqa: E501
            ],
        ),
        (
            162,
            161,
            [
                "    // Session 100 (D-1327): the app read the seeded token and kept it, so (e) checked the token it uses.",  # noqa: E501
                TOKEN_CHECK,
            ],
        ),
    ],
    SET: [
        (
            216,
            217,
            [
                "  // Session 100 (D-1308): no Copy MCP config or Pin click here; both write the system clipboard."  # noqa: E501
            ],
        ),
    ],
}
#: Kept-file code lines that leave without moving (D-1308).
RETIRED = {
    "await page.getByTestId('copy-mcp-btn').click()",
    "await page.getByTestId('pin-mcp-btn').click()",
}
#: The new file: ("add", lines), ("copy", file, first, last) or ("indent", file, first, last), a
#: copy with two more spaces of indent (D-1328: C1-5 inside try/finally, as the mcp tests are).
NEW_PLAN: list[tuple] = [
    ("add", NEW_HEADER),
    ("copy", MCP, 1, 14),
    ("add", [""]),
    ("add", GUARD),
    ("add", [""]),
    ("copy", MCP, 28, 84),
    (
        "add",
        [
            f"test('{NEW_TITLES[0]}', async () => {{",
            "  const { app } = await launchApp()",
            "  try {",
            "    const page = await app.firstWindow()",
            "    // C1-5's /settings/app route, kept so the Console opens as it does in console-chrome.test.ts.",  # noqa: E501
        ],
    ),
    ("indent", CON, 79, 93),
    ("add", ["  } finally {", "    await app.close()", "  }", "})", ""]),
    ("add", [f"test('{NEW_TITLES[1]}', async () => {{"]),
    ("copy", MCP, 127, 127),
    ("copy", MCP, 93, 97),
    ("copy", MCP, 99, 99),
    ("add", [""]),
    ("copy", MCP, 106, 114),
    ("copy", MCP, 121, 124),
    ("add", ["", f"test('{NEW_TITLES[2]}', async () => {{"]),
    ("copy", MCP, 127, 132),
    (
        "add",
        [
            "    // (d) Copy MCP config: the clipboard holds a config with a non-empty AVKIT_API_TOKEN."  # noqa: E501
        ],
    ),
    ("copy", MCP, 136, 149),
    ("copy", MCP, 162, 165),
]
TITLE = re.compile(r"^test\('([^']*)'", re.M)


class SetupError(Exception):
    pass


def _writer_scan():
    spec = importlib.util.spec_from_file_location("writer_scan", HERE / "writer-scan.py")
    if spec is None or spec.loader is None:
        raise SetupError("writer-scan.py cannot be loaded")
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True  # no __pycache__ in the plan folder
    spec.loader.exec_module(mod)
    return mod


def base_text(name: str) -> str:
    r = subprocess.run(
        ["git", "show", f"{BASE}:{E2E}/{name}"], cwd=REPO, capture_output=True, check=False
    )
    if r.returncode != 0:
        raise SetupError(
            f"git show {BASE}:{E2E}/{name} failed: {r.stderr.decode(errors='replace')}"
        )
    return r.stdout.decode("utf-8")


def lines_of(text: str) -> list[str]:
    if "\r" in text or not text.endswith("\n"):
        raise SetupError("a base blob is not LF with a final newline")
    return text[:-1].split("\n")


def check_anchors(bases: dict[str, str]) -> None:
    for (name, n), want in ANCHORS.items():
        got = lines_of(bases[name])[n - 1].strip()
        if not got.startswith(want):
            raise SetupError(f"{name}:{n} is {got[:80]!r}, not the pinned {want[:80]!r}")


def apply_edits(lines: list[str], edits: list[tuple[int, int, list[str]]]) -> list[str]:
    out = list(lines)
    for first, last, repl in sorted(edits, key=lambda e: (e[0], e[1]), reverse=True):
        out[first - 1 : last] = repl
    return out


def build(bases: dict[str, str]) -> dict[str, bytes]:
    check_anchors(bases)
    out: dict[str, bytes] = {}
    for name in KEPT:
        kept = apply_edits(lines_of(bases[name]), EDITS[name])
        out[name] = ("\r\n".join(kept) + "\r\n").encode("utf-8")
    new: list[str] = []
    for step in NEW_PLAN:
        new += step[1] if step[0] == "add" else copied(step, bases)
    out[NEW] = ("\n".join(new) + "\n").encode("utf-8")
    return out


def copied(step: tuple, bases: dict[str, str]) -> list[str]:
    kind, name, first, last = step
    lines = lines_of(bases[name])[first - 1 : last]
    return ["  " + x if x and kind == "indent" else x for x in lines]


def indented(name: str, n: int) -> bool:
    return any(s[0] == "indent" and s[1] == name and s[2] <= n <= s[3] for s in NEW_PLAN)


def dropped_code(bases: dict[str, str]) -> list[str]:
    """Each code line the kept files lose, in the form the new file must hold it."""
    lost: list[str] = []
    for name in KEPT:
        lines = lines_of(bases[name])
        for first, last, _repl in EDITS[name]:
            for n in range(first, last + 1):
                line = lines[n - 1]
                s = line.strip()
                if s and not s.startswith("//") and not s.startswith("test("):
                    lost.append("  " + line if indented(name, n) else line)
    return lost


def holds_block(lines: list[str], block: list[str]) -> bool:
    k = len(block)
    return any(lines[i : i + k] == block for i in range(len(lines) - k + 1))


def invariants(out: dict[str, bytes], bases: dict[str, str]) -> list[str]:
    bad: list[str] = []
    scan = _writer_scan()
    new = out[NEW]
    if b"\r" in new:
        bad.append(f"{NEW} is not LF only")
    new_text = new.decode("utf-8", errors="replace").replace("\r\n", "\n")
    new_lines = new_text.split("\n")
    for line in dropped_code(bases):
        if line.strip() in RETIRED:
            continue
        if line not in new_lines:
            bad.append(f"a moved line is not in {NEW}: {line.strip()[:90]}")
    for step in NEW_PLAN:
        if step[0] != "add" and not holds_block(new_lines, copied(step, bases)):
            bad.append(f"{NEW} does not hold {step[1]} {step[2]}-{step[3]} as one block")
    closes = "\n  } finally {\n    await app.close()\n  }\n})\n"
    if new_text.count(closes) != len(NEW_TITLES) or "\n  await app.close()\n" in new_text:
        bad.append(f"{NEW} has a test that does not close its app in a finally")
    titles = TITLE.findall(new_text)
    if titles != NEW_TITLES:
        bad.append(f"{NEW} titles are {titles}, not {NEW_TITLES}")
    guard_at = [i for i in range(len(new_lines)) if new_lines[i : i + len(GUARD)] == GUARD]
    first_test = next((i for i, x in enumerate(new_lines) if x.startswith("test(")), len(new_lines))
    last_import = max(
        (i for i, x in enumerate(new_lines) if x.startswith("} from ") or x.startswith("import ")),
        default=-1,
    )
    if len(guard_at) != 1 or not last_import < guard_at[0] < first_test:
        bad.append(
            f"{NEW} does not hold the GUARD lines once between its imports and its first test"
        )
    if new_text.count("test.skip(") != 1:
        bad.append(f"{NEW} holds a test.skip other than the GUARD")
    for name in KEPT:
        data = out[name]
        if data.count(b"\n") != data.count(b"\r\n") or b"\r\r" in data:
            bad.append(f"{name} is not CRLF only")
        text = data.decode("utf-8", errors="replace").replace("\r\n", "\n")
        want = [RENAMED[name].get(t, t) for t in TITLE.findall(bases[name])]
        got = TITLE.findall(text)
        if got != want:
            bad.append(f"{name} titles differ from the base titles with RENAMED swapped")
        for kind, n, src in scan.hits_in(name, text):
            bad.append(f"{name}:{n}: writer-scan {kind}: {src[:80]}")
    mcp_text = out[MCP].decode("utf-8", errors="replace").replace("\r\n", "\n")
    if mcp_text.split("\n").count(TOKEN_CHECK) != 1:
        bad.append(f"{MCP} does not hold the TOKEN_CHECK line once (D-1327)")
    return bad


def tracked() -> dict[str, Path]:
    return {n: REPO / E2E / n for n in (NEW, *KEPT)}


def cmd_check(out: dict[str, bytes], bases: dict[str, str]) -> int:
    bad = invariants(out, bases)
    for n, p in tracked().items():
        if not p.is_file():
            bad.append(f"{E2E}/{n} is missing")
        elif p.read_bytes() != out[n]:
            bad.append(f"{E2E}/{n} differs from the built file")
    for b in bad:
        print("split-specs: " + b)
    print(f"split-specs check: {'ok' if not bad else 'FAILED'} ({len(bad)} problem(s))")
    return 0 if not bad else 1


def cmd_write(out: dict[str, bytes], bases: dict[str, str], root: Path | None = None) -> int:
    bad = invariants(out, bases)
    paths = tracked() if root is None else {n: root / n for n in (NEW, *KEPT)}
    if paths[NEW].exists():
        bad.append(f"{E2E}/{NEW} exists already")
    for n in KEPT:
        want = bases[n].encode("utf-8").replace(b"\n", b"\r\n")  # autocrlf checkout of an LF blob
        if not paths[n].is_file() or paths[n].read_bytes() != want:
            bad.append(f"{E2E}/{n} is not its {BASE} blob in checkout form (CRLF)")
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
            print(f"split-specs: wrote {paths[n]} ({len(out[n])} bytes)")
    finally:
        for tmp in temps.values():
            if tmp.exists():
                tmp.unlink()
    return 0


def cmd_out(d: Path, out: dict[str, bytes], bases: dict[str, str]) -> int:
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
    bad = invariants(out, bases)
    for b in bad:
        print("split-specs: " + b)
    return 0 if not bad else 1


def cmd_selftest(out: dict[str, bytes], bases: dict[str, str]) -> int:
    fails = []
    first = invariants(out, bases)
    if first:
        fails.append("the built files fail the invariants: " + "; ".join(first))

    def refused(label: str, name: str, old: bytes, new: bytes) -> None:
        changed = dict(out)
        changed[name] = out[name].replace(old, new, 1)
        if changed[name] == out[name] or not invariants(changed, bases):
            fails.append(f"{label} was not refused")

    refused(
        "a changed assertion",
        NEW,
        b"expect(clipboard).toBe(visibleLogs)",
        b"expect(clipboard).toBe('')",
    )
    refused("a lost moved line", NEW, b"    expect(token.length).toBeGreaterThan(0)\n", b"")
    refused(
        "a lost route line",
        NEW,
        b"      await route.fulfill({ json: { log_to_file: true } })\n",
        b"",
    )
    refused(
        "a test without its try/finally",
        NEW,
        b"  } finally {\n    await app.close()\n  }\n})\n",
        b"  }\n  await app.close()\n})\n",
    )
    refused("a lost token-file check", MCP, TOKEN_CHECK.encode() + b"\r\n", b"")
    refused("a CRLF new file", NEW, b"\n", b"\r\n")
    refused("an LF kept file", MCP, b"\r\n", b"\n")
    refused(
        "a writer left in a kept file",
        CON,
        b"  await app.close()\r\n",
        b"  await page.getByTestId('console-copy').click()\r\n  await app.close()\r\n",
    )
    refused(
        "a new file without its guard", NEW, f"process.env.{GATE_ENV} !== '1'".encode(), b"false"
    )
    refused("a lost title", SET, b"test('W4-3 ", b"test.skip('W4-3 ")
    moved = dict(bases)
    moved[MCP] = bases[MCP].replace("    // (b) Copy prompt:", "    // (b) Copy  prompt:", 1)
    try:
        build(moved)
        fails.append("a moved anchor was not refused")
    except SetupError:
        pass
    with tempfile.TemporaryDirectory(prefix="split-out-") as tmp:
        d = Path(tmp) / "out"
        a = cmd_out(d, out, bases)
        sentinel = b"sentinel\n"
        (d / NEW).write_bytes(sentinel)
        b = cmd_out(d, out, bases)
        if a != 0 or b == 0 or (d / NEW).read_bytes() != sentinel:
            fails.append("an existing --out file was not refused")
        # --write on a scratch tree in checkout form (Session 98 RULE-3), then again (refused).
        root = Path(tmp) / "tree"
        root.mkdir()
        for n in KEPT:
            (root / n).write_bytes(bases[n].encode("utf-8").replace(b"\n", b"\r\n"))
        w1 = cmd_write(out, bases, root)
        same = all((root / n).read_bytes() == out[n] for n in out)
        w2 = cmd_write(out, bases, root)
        if w1 != 0 or not same or w2 == 0:
            fails.append(
                "--write on a checkout-form scratch tree did not write once and refuse after"
            )
    for f in fails:
        print("split-specs selftest: " + f)
    print(f"split-specs selftest: {'ok' if not fails else 'FAILED'} (13 cases)")
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
        bases = {n: base_text(n) for n in KEPT}
        out = build(bases)
    except SetupError as e:
        print(f"split-specs: setup: {e}")
        return 2
    if a.out:
        return cmd_out(Path(a.out), out, bases)
    if a.write:
        return cmd_write(out, bases)
    if a.check:
        return cmd_check(out, bases)
    return cmd_selftest(out, bases)


if __name__ == "__main__":
    sys.exit(main())
