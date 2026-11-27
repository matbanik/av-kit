"""Session 104 canon edits (task row 18; implementation-plan.md §Spec, D-1481).

``EDITS`` maps a repository path to its (old text, new text) pairs. Each old text must occur
exactly once; ``\\n`` in a text becomes the file's own line ending. The script copies each file's
bytes before the edit to ``R/canon-before/<path>`` (and refuses a rerun whose before-copy differs
from the file it would edit, unless the file already holds the edits), then writes the files.
``--grouping`` instead sets the status cell of the grouping file's ``| 104 |`` row to
``| executed (Session 104) |`` (LF file).

``row-check.py canon`` checks the result against the before-copies.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SLUG = "2026-11-26-ytdlp-challenge-and-cookie-test"
RECEIPTS = pathlib.Path("C:/Temp/av-kit") / SLUG
GROUPING = ".agent/context/grouping/2026-11-26-ui-findings-and-auto-update-session-grouping.md"

#: Written at row 18 from implementation-plan.md §Spec (D-1481).
EDITS: dict[str, list[tuple[str, str]]] = {
    "docs/build-plan/01-domain-layer.md": [
        (
            "`CookieTestResult` is `{ ok: bool, error_message: str | None }` — never cookie bytes.",
            "`CookieTestResult` is `{ ok: bool, error_message: str | None, outcome: "
            "CookieTestOutcome | None }` — never cookie bytes. `CookieTestOutcome` is `ok`, "
            "`unreadable` or `check_failed` (MEU-169, D-1463). `outcome` is None for cookie Mode "
            "None; `ok` is true when `outcome` is `ok` or None, and a passed test carries no "
            "`error_message`.",
        ),
    ],
    "docs/build-plan/02-infrastructure.md": [
        (
            "Implements Phase 1 `YouTubePort.test_cookies` → `CookieTestResult` (`ok`, "
            "`error_message`) **only**.",
            "Implements Phase 1 `YouTubePort.test_cookies` → `CookieTestResult` (`ok`, "
            "`error_message`, `outcome`) **only**; `outcome` follows [§Cookie test outcome "
            "(residual)](#cookie-test-outcome-residual).",
        ),
        (
            "{ ok: false, error_message }",
            "{ ok: false, outcome: unreadable, error_message }",
        ),
        (
            "| Tests | The adapter, client fallback and extract option suites pass on the new "
            "version. The real extraction is a recorded script, not a CI test. | Local Canon: "
            "[§SABR check result (residual)](#sabr-check-result-residual) Tests row (no live "
            "YouTube) |\n",
            "| Tests | The adapter, client fallback and extract option suites pass on the new "
            "version. The real extraction is a recorded script, not a CI test. | Local Canon: "
            "[§SABR check result (residual)](#sabr-check-result-residual) Tests row (no live "
            "YouTube) |\n\n> **Delivered (Session 104).**\n> - The lock moved yt-dlp from "
            "2026.10.26 to 2026.11.23 (D-1460; `tests/unit/test_ytdlp_lock.py`). The version was "
            "needed; the `player_js_variant` fallback was not (D-1461): yt-dlp 2026.11.23's own "
            "default variant is `tv`, and av-kit sets none.\n> - Proof (D-1462): the recorded "
            "before-run on 2026.10.26 ended `challenge-errors` with 0 formats; the after-run on "
            "2026.11.23, same video, ended `clean` with 11 formats.\n> - `exclude-newer-package = "
            "{ yt-dlp = false }` in the root `[tool.uv]` (D-1468) lets the release past the 7-day "
            "hold. Remove it and run `uv lock` again after 2026-11-30.\n> - The licence list "
            "names yt-dlp 2026.11.23; the runtime smoke solves with the bundled Deno 2.9.8.\n",
        ),
        (
            "Renderer: each outcome and the busy state. Electron E2E through the API seam. No "
            'live YouTube. | Local Canon; Mat, 2026-11-16 ("This should be done with framework '
            'and scripts!") |\n',
            "Renderer: each outcome and the busy state. Electron E2E through the API seam. No "
            'live YouTube. | Local Canon; Mat, 2026-11-16 ("This should be done with framework '
            'and scripts!") |\n\n> **Delivered (Session 104).**\n> - `CookieTestOutcome` (`ok`, '
            "`unreadable`, `check_failed`; D-1463) on `CookieTestResult.outcome`, None for Mode "
            "None. The adapter sets it, the service keeps the first line of `error_message` and "
            "scrubs it, and `POST /downloads/cookies/test` returns `200 { ok, outcome, "
            "error_message }`. The MCP tool description names the three outcomes.\n> - Test "
            "Cookies shows its result in `cookie-test-result`, one of four texts; the button is "
            "busy while the test runs, and a change to the cookie settings clears the line "
            "(D-1464).\n> - Tests: adapter, service, route, MCP, renderer and Electron E2E "
            "(`ui/tests/e2e/downloader-cookie-test.test.ts`). No live YouTube.\n",
        ),
        (
            "| Tests | Unit tests for the option the plan chooses and for the status text. No "
            "live YouTube. | Local Canon |\n",
            "| Tests | Unit tests for the option the plan chooses and for the status text. No "
            "live YouTube. | Local Canon |\n\n> **Delivered (Session 104).**\n> - Option B "
            "(D-1465): Check SABR still probes without cookies, and a detected status ends ` · "
            "Check SABR does not use cookies` (D-1466; `SABR_CHECK_SCOPE`). A forced status has "
            "no clause.\n> - The phrase set, Force SABR, Clear SABR, their log lines and "
            "`SABRStatusOut` are unchanged.\n",
        ),
    ],
    "docs/build-plan/04-rest-api.md": [
        (
            "| 200 `{ ok: true }` | Body: mode, browser?, profile?, cookie_file? — no cookie "
            "bytes back |",
            "| 200 `{ ok, outcome, error_message }` | Body: mode, browser?, profile?, "
            "cookie_file? — no cookie bytes back; `outcome` is `ok`, `unreadable`, "
            "`check_failed`, or null for mode none (MEU-169) |",
        ),
    ],
    "docs/build-plan/06-gui.md": [
        (
            "- **Manual check**: `Check SABR` button runs test extraction\n",
            "- **Manual check**: `Check SABR` button runs test extraction with the `android`, "
            "`tv` and `ios` clients and no cookies; a detected status ends ` · Check SABR does "
            "not use cookies` (MEU-170, D-1465, D-1466)\n",
        ),
        (
            'Paths only; never cookie bytes. Warning: "Close browser first!" '
            "([§5](../../_inspiration/_downloader_pseudo_logic.md)) |",
            'Paths only; never cookie bytes. Warning: "Close browser first!" '
            "([§5](../../_inspiration/_downloader_pseudo_logic.md)). The result shows in "
            '`cookie-test-result`: "Cookies read. YouTube answered.", "Could not read the '
            'cookies: <reason>", "Cookies read, but YouTube\'s check failed: <reason>", or '
            '"Cookie mode is None. Nothing to test." The button is busy while the test runs; a '
            "cookie setting change clears the line (MEU-169, D-1464) |",
        ),
    ],
}


def apply(raw: bytes, edits: list[tuple[str, str]], path: str) -> tuple[bytes, list[str]]:
    nl = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8")
    problems: list[str] = []
    for old, new in edits:
        o, n = old.replace("\n", nl), new.replace("\n", nl)
        count = text.count(o)
        if count != 1:
            problems.append(f"{path}: the old text occurs {count} time(s): {old[:60]!r}")
            continue
        text = text.replace(o, n)
    return text.encode("utf-8"), problems


def grouping(root: pathlib.Path = ROOT) -> int:
    p = root / GROUPING
    raw = p.read_bytes()
    lines = raw.split(b"\n")
    rows = [i for i, line in enumerate(lines) if line.startswith(b"| 104 |")]
    if len(rows) != 1:
        print(f"refused: {len(rows)} row(s) start '| 104 |'")
        return 1
    row = lines[rows[0]]
    if b"| executed (Session 104) |" in row:
        print("grouping: row 104 already reads executed (Session 104)")
        return 0
    for old in (b"| planning |", b"| planned |"):
        if row.count(old) == 1:
            lines[rows[0]] = row.replace(old, b"| executed (Session 104) |")
            p.write_bytes(b"\n".join(lines))
            print("grouping: row 104 now reads executed (Session 104)")
            return 0
    print(f"refused: row 104 has no single planning cell: {row[:120]!r}")
    return 1


def main(argv: list[str]) -> int:
    if argv == ["--grouping"]:
        return grouping()
    if argv:
        print("usage: canon-edit.py [--grouping]")
        return 2
    if not EDITS:
        print("refused: EDITS not written")
        return 1
    plans: dict[str, bytes] = {}
    problems: list[str] = []
    for path, pairs in EDITS.items():
        target = ROOT / path
        raw = target.read_bytes()
        before = RECEIPTS / "canon-before" / path
        if before.is_file() and before.read_bytes() != raw:
            done, probs = apply(before.read_bytes(), pairs, path)
            if not probs and done == raw:
                print(f"canon-edit {path}: already applied")
                continue
            problems.append(f"{path}: the before-copy differs and the edits are not applied")
            continue
        out, probs = apply(raw, pairs, path)
        problems += probs
        plans[path] = out
    if problems:
        for p in problems:
            print("refused:", p)
        return 1
    for path, out in plans.items():
        before = RECEIPTS / "canon-before" / path
        before.parent.mkdir(parents=True, exist_ok=True)
        if not before.is_file():
            before.write_bytes((ROOT / path).read_bytes())
        (ROOT / path).write_bytes(out)
        print(f"canon-edit {path}: {len(EDITS[path])} edit(s) written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
