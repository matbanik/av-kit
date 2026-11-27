"""Session 103 canon edits (task row 11; implementation-plan.md §Spec, D-1432). A copy of
Session 104's, with this plan's SLUG, EDITS and grouping row.

``EDITS`` maps a repository path to its (old text, new text) pairs. Each old text must occur
exactly once; ``\\n`` in a text becomes the file's own line ending. The script copies each file's
bytes before the edit to ``R/canon-before/<path>`` (and refuses a rerun whose before-copy differs
from the file it would edit, unless the file already holds the edits), then writes the files.
``--grouping`` instead sets the status cell of the grouping file's ``| 103 |`` row to
``| executed (Session 103) |`` (LF file). The cell it replaces is ``planning``, ``planned``
or ``plan approved (round 2)``, the text the orchestrator wrote for D-1413 (D-1433).

``row-check.py canon`` checks the result against the before-copies.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SLUG = "2026-11-26-capture-key-inbox-scrollbars"
RECEIPTS = pathlib.Path("C:/Temp/av-kit") / SLUG
GROUPING = ".agent/context/grouping/2026-11-26-ui-findings-and-auto-update-session-grouping.md"

#: Written at row 11 from implementation-plan.md §Spec (D-1432).
EDITS: dict[str, list[tuple[str, str]]] = {
    "docs/build-plan/09-screenshot-capture.md": [
        (
            "Empty inbox: viewport shows a short empty state (“Press F2 or Capture region”).",
            "Empty inbox: viewport shows a short empty "
            "state (“Press F2 or Capture region”), which "
            "names the key set in `capture.hotkey`, `F2` by "
            "default ([§Capture key in "
            "texts](#capture-key-in-texts)).",
        ),
        (
            "Lock: **scan deletes rows whose original file "
            "is missing** (inbox is source of files).",
            "Lock: **scan deletes rows whose original file "
            "is missing** (inbox is source of files). The "
            "scan, its prune, the list and every by-id "
            "lookup cover only the shots directly inside "
            "the current `inbox_dir`; rows of other folders "
            "stay in the catalog untouched and are listed "
            "again when their folder is the inbox again "
            "([§Catalog follows the inbox "
            "folder](#catalog-follows-the-inbox-folder)).",
        ),
        (
            "Upsert shots; delete rows whose file vanished |",
            "Upsert shots; delete rows of the current inbox "
            "whose file vanished. Rows of other folders are "
            "neither touched nor returned |",
        ),
        (
            "| `list_shots` | `scan_inbox` then return shots newest first |",
            "| `list_shots` | `scan_inbox` then return the current inbox's shots newest first |",
        ),
        (
            "| `get_shot` | 404 if missing |",
            "| `get_shot` | 404 if missing or outside the "
            "current inbox; every method that takes a shot "
            "id answers the same 404 |",
        ),
        (
            "| Pan gestures | Space+drag and middle-button "
            "drag move a clamped offset inside a fixed, "
            "`overflow-hidden` frame with no scrollbars. An "
            "axis whose image fits is centred; an "
            "overflowing axis never shows blank margin. A "
            "pan creates no mark, gesture, history entry or "
            "sample (Sample removed by MEU-81) | Session 29 "
            "plan D-15 |",
            "| Pan gestures | Space+drag and middle-button "
            "drag move a clamped offset inside a fixed, "
            "`overflow-hidden` frame. On each axis where "
            "the image is larger than the frame, a scroll "
            "bar drawn over the frame shows where the view "
            "is, and dragging its thumb moves the same "
            "clamped offset ([§Viewport scroll "
            "bars](#viewport-scroll-bars)). An axis whose "
            "image fits is centred; an overflowing axis "
            "never shows blank margin. A pan or a thumb "
            "drag creates no mark, gesture, history entry "
            "or sample (Sample removed by MEU-81) | Session "
            "29 plan D-15; its no-scrollbars half replaced "
            "by triage D-1402 (Mat, 2026-11-26) and Session "
            "103 plan D-1426 |",
        ),
        (
            '\n\n<a id="catalog-follows-the-inbox-folder"></a>',
            "\n"
            "\n"
            "> **Delivered (Session 103).**\n"
            "> - `CAPTURE_KEY_TOKEN`: each text that names "
            "the capture key holds `{captureKey}`, and one "
            "formatter, `captureKeyText(template, key)` in "
            "`ui/src/renderer/src/features/capture/capture-key.ts`, "
            "replaces it; a blank key gives `F2`.\n"
            "> - `CAPTURE_KEY_SAVED`: the texts, the key "
            "cap and the in-use banner show the saved "
            "`capture.hotkey` (`saved.hotkey` from "
            "`useCaptureSettings`); a draft changes none of "
            "them (D-1420).\n"
            "> - `CAPTURE_KEY_FOLLOW` and "
            "`CAPTURE_KEY_UNCONFIRMED`: the page reads "
            "main's hotkey status on mount and after the "
            "saved key changes, and again every 500 ms, at "
            "most 10 times, while the status names another "
            "key. If no read confirms the saved key, the "
            "banner place says that the key is saved but "
            "av-kit cannot confirm that it works.\n"
            "> - `CAPTURE_KEY_DEFAULT_READING`: "
            "`CAPTURE_HELP_SECTIONS`, "
            "`SETTINGS_HELP_SECTIONS` and `QUICK_START` "
            "read as before with `F2`; "
            "`captureHelpSections(key)`, "
            "`settingsHelpSections(key)` and "
            "`quickStartPage(feature, key)` give the texts "
            "for another key. The help images are not "
            "retaken (D-1421).\n"
            "> - Tests: `ui/tests/unit/capture-key.test.ts` "
            "and "
            "`ui/tests/unit/capture-key.behavior.test.ts` "
            "(AC-165.1 to AC-165.9), and the Electron test "
            "in "
            "`ui/tests/e2e/capture-settings-draft.test.ts` "
            "(AC-165.10). D-1422 names the four test "
            "expectations that changed. D-1420 to D-1422 "
            "and D-1435 to D-1437 are in the plan "
            "`docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/`.\n"
            "\n"
            '<a id="catalog-follows-the-inbox-folder"></a>',
        ),
        (
            '\n\n<a id="viewport-scroll-bars"></a>',
            "\n"
            "\n"
            "> **Delivered (Session 103).**\n"
            "> - `INBOX_SCOPE` and `INBOX_SCOPE_SCAN`: in "
            "`packages/core/src/avkit_core/services/capture.py` "
            "a shot is in scope when the parent of its "
            "`original_path` is the resolved inbox folder. "
            "`scan_inbox` and `list_shots` return only "
            "those shots, and they do not probe, prune, "
            "recover or write any other row (D-1423).\n"
            "> - `INBOX_SCOPE_BY_ID`: every public "
            "`CaptureService` method that takes a shot id "
            "answers a shot out of scope with the same "
            "not-found error as an unknown id, through one "
            "lookup, and writes nothing (D-1424).\n"
            "> - `INBOX_SAVE_REFRESH`, "
            "`INBOX_SELECTION_LEFT` and "
            "`INBOX_RESULT_BOUND`: a settings save that "
            "changes `inbox_dir` refreshes the Capture list "
            "at once; a selection that left the list is "
            "cleared; a crop result or a flatten's PNG copy "
            "is selected only when the inbox did not change "
            "while it ran (D-1425).\n"
            "> - Tests: "
            "`tests/unit/test_capture_inbox_scope.py`, "
            "`tests/e2e/test_api_capture_inbox_scope.py` "
            "and "
            "`ui/tests/unit/capture-inbox-scope.behavior.test.ts` "
            "(AC-166.1 to AC-166.8), with the Electron test "
            "in "
            "`ui/tests/e2e/capture-settings-draft.test.ts` "
            "(AC-166.7). D-1423 to D-1425, D-1435 and "
            "D-1436 are in the plan "
            "`docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/`.\n"
            "\n"
            '<a id="viewport-scroll-bars"></a>',
        ),
        (
            "\n\n## Named deferrals (not this phase)",
            "\n"
            "\n"
            "> **Delivered (Session 103).**\n"
            "> - `SCROLL_BAR_GEOMETRY`: `scrollBars(frame, "
            "image, state)` and `thumbDragToPan(drag, bar)` "
            "in "
            "`ui/src/renderer/src/features/capture/capture-scroll-bars.ts` "
            "give each axis's bar from the view transform: "
            "it shows when the zoomed image is longer than "
            "the frame, it is 10 px thick, its thumb is at "
            "least 24 px and never longer than the track, "
            "and its value goes from 0 to 100.\n"
            "> - `SCROLL_BAR_OVERLAY` and "
            "`SCROLL_BAR_DRAG`: `ViewportScrollBar` in "
            "`CaptureViewport.tsx` draws the bars over the "
            "`overflow-hidden` frame. Only a thumb takes "
            "the pointer, and its drag pans through the "
            "existing clamp with no mark, history entry or "
            "sample. `capture-fit-map.ts` does not change "
            "(D-1426).\n"
            "> - `SCROLL_BAR_LOOK`: theme tokens only (a "
            "`fg-muted` thumb with a `bg` edge on a "
            "transparent track), no transition, and the "
            "`scrollbar` role with its values; a bar is not "
            "a tab stop (D-1427).\n"
            "> - Tests: "
            "`ui/tests/unit/capture-scroll-bars.test.ts` "
            "and "
            "`ui/tests/unit/capture-scroll-bars.behavior.test.ts` "
            "(AC-167.1 to AC-167.6), and the Electron tests "
            "in `ui/tests/e2e/capture-inbox.test.ts` "
            "(AC-167.7 in the light theme, AC-167.8 in the "
            "dark theme). D-1426, D-1427 and D-1431 are in "
            "the plan "
            "`docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/`.\n"
            "\n"
            "## Named deferrals (not this phase)",
        ),
    ],
    ".agent/context/grouping/2026-11-26-ui-findings-and-auto-update-session-grouping.md": [
        (
            "| "
            "103 "
            "| "
            "`capture-key-inbox-scrollbars` "
            "| "
            "MEU-165, "
            "MEU-166, "
            "MEU-167 "
            "| P2 "
            "| "
            "plan "
            "approved "
            "(round "
            "2) |",
            "| "
            "103 "
            "| "
            "`capture-key-inbox-scrollbars` "
            "| "
            "MEU-165, "
            "MEU-166, "
            "MEU-167 "
            "| P2 "
            "| "
            "executed "
            "(Session "
            "103) "
            "|",
        )
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
    rows = [i for i, line in enumerate(lines) if line.startswith(b"| 103 |")]
    if len(rows) != 1:
        print(f"refused: {len(rows)} row(s) start '| 103 |'")
        return 1
    row = lines[rows[0]]
    if b"| executed (Session 103) |" in row:
        print("grouping: row 103 already reads executed (Session 103)")
        return 0
    # D-1433: the orchestrator set the cell to `plan approved (round 2)` for D-1413.
    for old in (b"| planning |", b"| planned |", b"| plan approved (round 2) |"):
        if row.count(old) == 1:
            lines[rows[0]] = row.replace(old, b"| executed (Session 103) |")
            p.write_bytes(b"\n".join(lines))
            print("grouping: row 103 now reads executed (Session 103)")
            return 0
    print(f"refused: row 103 has no single planning cell: {row[:120]!r}")
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
