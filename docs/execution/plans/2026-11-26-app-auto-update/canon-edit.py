"""Session 106 canon edits (task row 18; implementation-plan.md §BUILD_PLAN.md Audit). A copy
of Session 103's, itself from Session 104's and Session 102's
(2026-11-22-tray-show-and-baseline-fixes/canon-edit.py), with this plan's SLUG, EDITS and
grouping row.

``EDITS`` maps a repository path to its (old text, new text) pairs. Each old text must occur
exactly once; ``\\n`` in a text becomes the file's own line ending. The script copies each file's
bytes before the edit to ``R/canon-before/<path>`` (and refuses a rerun whose before-copy differs
from the file it would edit, unless the file already holds the edits), then writes the files.
``--grouping`` instead sets the status cell of the grouping file's ``| 106 |`` row to
``| executed (Session 106) |`` (LF file). The cell it replaces is ``planning``, ``planned``
or ``plan approved (round 3)``, the text the orchestrator wrote for D-1413.

``row-check.py canon`` checks the result against the before-copies.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SLUG = "2026-11-26-app-auto-update"
RECEIPTS = pathlib.Path("C:/Temp/av-kit") / SLUG
GROUPING = ".agent/context/grouping/2026-11-26-ui-findings-and-auto-update-session-grouping.md"

#: Written at row 18 from implementation-plan.md §BUILD_PLAN.md Audit and task row 18.
EDITS: dict[str, list[tuple[str, str]]] = {
    "docs/build-plan/07-distribution.md": [
        (
            "After install, everything except YouTube / Hugging Face calls and the one-time "
            "pinned spaCy model wheel (`github.com/explosion/spacy-models` releases; [03 §TTS "
            "runtime assets](03-service-layer.md#tts-runtime-assets-residual)) works offline.",
            "After install, everything except YouTube / Hugging Face calls, the one-time pinned "
            "spaCy model wheel (`github.com/explosion/spacy-models` releases; [03 §TTS runtime "
            "assets](03-service-layer.md#tts-runtime-assets-residual)) and the update check works "
            "offline. The update check asks `github.com` for the newest release of the public "
            "repository on the schedule chosen in Settings (once a week by default, once a month, "
            "or never), at each start while a found update waits, and when the user clicks Check "
            "now. The request carries no identifier, only what any HTTPS request shows (the "
            "address and a user agent), and Never stops the scheduled request ([§In-app update "
            "(residual)](#in-app-update-residual); D-1544, the plan's recommendation while Mat's "
            "ruling is open).",
        ),
        (
            "| Auto-update | `electron-updater` **optional**; do not block ship on it |",
            "| Auto-update | Delivered in Session 106. `electron-updater` 6.8.11 checks the "
            "public repository's GitHub releases (`publish` provider `github`; every build still "
            "runs `--publish never`) on the Settings interval, downloads a newer installer in the "
            "background, checks its SHA-512 and installs it on **Restart and update**. See "
            "[§Update feed (residual)](#update-feed-residual) and [§In-app update "
            "(residual)](#in-app-update-residual) |",
        ),
        (
            "Research-backed: electron-builder's auto-update documentation "
            "(www.electron.build/v26/docs/features/auto-update/, read 2026-11-26)",
            "Research-backed: electron-builder's auto-update documentation "
            "(https://www.electron.build/v26/docs/features/auto-update/, read 2026-11-26)",
        ),
        (
            "| Research-backed: www.electron.build/v26/docs/features/auto-update/; Local Canon:",
            "| Research-backed: https://www.electron.build/v26/docs/features/auto-update/; Local "
            "Canon:",
        ),
        (
            "| Tests | A unit test on the builder configuration and the checklist; the feed check "
            "script run against a real build. | Local Canon |\n",
            "| Tests | A unit test on the builder configuration and the checklist; the feed check "
            "script run against a real build. | Local Canon |\n\n> **Delivered (Session "
            "106).**\n> - `FEED_BLOCK` and `DIST_NEVER_PUBLISHES`: `ui/electron-builder.yml` "
            "names the GitHub provider for `matbanik/av-kit` with no other key, and every build "
            "script still passes `--publish never`.\n> - `FEED_CHECK`: "
            "`tools/check_update_feed.py` compares `latest.yml` and the `.blockmap` with the "
            "built installer (file name, size, SHA-512) and with `resources/app-update.yml`. On a "
            "product build of this plan's snapshot it returned `feed-ok` for "
            "`av-kit-Setup-0.1.0-rc.5.exe` (371,756,740 B, blockmap 388,536 B), `feed-missing` "
            "without `latest.yml` and `sha512-mismatch` for one changed byte.\n> - "
            "`FEED_CHECKLIST`: `docs/releases/publish-checklist-update-feed.md` adds the two feed "
            "files to each release's upload. No tool uploads. The first release that carries them "
            "is Mat's step; users of rc.5 and earlier install that release by hand once.\n> - "
            "AC-173.1 to AC-173.5; plan decisions D-1540 to D-1554, and the execution decisions "
            "in the MEU-173 handoff.\n> - Plan "
            "`docs/execution/plans/2026-11-26-app-auto-update/`.\n",
        ),
        (
            "| Tests | Unit: the schedule with a fake clock and the updater mocked. Electron E2E "
            "against a local feed. A real update from one built version to the next, run by "
            'script on the remote E2E host. | Local Canon; Mat, 2026-11-16 ("This should be done '
            'with framework and scripts!") |\n',
            "| Tests | Unit: the schedule with a fake clock and the updater mocked. Electron E2E "
            "against a local feed. A real update from one built version to the next, run by "
            'script on the remote E2E host. | Local Canon; Mat, 2026-11-16 ("This should be done '
            'with framework and scripts!") |\n\n> **Delivered (Session 106).**\n> - '
            "`UPDATE_INTERVAL_LEAF`: `app.update_interval` (`weekly`, the default; `monthly`; "
            "`never`) in the core registry, the API model and the OpenAPI document, the UI "
            "schema, the Settings page and the MCP settings tool, and in [06 "
            "§Settings](06-gui.md#settings-page-settings).\n> - `UPDATE_SCHEDULE`, "
            "`UPDATER_CONFIG`, `UPDATE_TICK`, `UPDATE_STATE`, `UPDATE_QUIET_FAILURE` and "
            "`UPDATE_NOTICE_ONCE`: the packaged app checks on the interval (a found update is "
            "checked again at each start), downloads in the background, fails quietly with no "
            "network, and shows one notice per downloaded version. A development run never "
            "checks.\n> - `UPDATE_IPC` and `UPDATES_CARD`: Settings → Updates holds the interval, "
            "Check now, the status and **Restart and update**, and says that updates are checked "
            "by the release's SHA-512 and are not signed (D-1543, the plan's recommendation while "
            "Mat's ruling is open).\n> - `UPDATE_INSTALL_ORDER`, `APP_RUNNING_CHECK` and "
            "`UNINSTALL_CACHE_RECURSIVE`: the backend stops before the installer starts, the "
            "installer stops every process under the install folder (the MCP server too) and "
            "keeps user data, and an uninstall removes the updater's cache.\n> - `HOST_PAYLOAD`, "
            "`INSTALL_STAGE_RULES` and `ROUND_TRIP`: the installer pair and its feed passed on "
            "the dev PC (row 16: `pair-ok`). On the remote E2E host, run "
            "r20261128T024018Z-d7983df passed the main suite (266 of 266) and the install stage "
            "(2 of 2): an installed `0.0.901` found, downloaded and installed `0.0.902` from the "
            "local feed and kept its setting, marker file and sign-in value (AC-174.19), and the "
            "uninstall then removed the updater's cache and both sign-in values (AC-174.20). "
            "Three earlier runs failed at AC-174.19 because Windows reads Start at sign-in under "
            "the app's AppUserModelId, which was still Electron's default at startup; `boot()` "
            "now sets it to the appId before it reads the login item (D-1583).\n> - AC-174.1 to "
            "AC-174.21; plan decisions D-1540 to D-1554, and the execution decisions in the "
            "MEU-174 handoff. Users get the updater with the first release that carries the feed "
            "files, which is Mat's step.\n> - Plan "
            "`docs/execution/plans/2026-11-26-app-auto-update/`.\n",
        ),
    ],
    "docs/build-plan/06-gui.md": [
        (
            (
                "| `app.console_visible` | `boolean` | `true` | "
                "[Downloader "
                "§8](../../_inspiration/_downloader_pseudo_logic.md) |\n"
            ),
            (
                "| `app.console_visible` | `boolean` | `true` | "
                "[Downloader "
                "§8](../../_inspiration/_downloader_pseudo_logic.md) |\n| "
                "`app.update_interval` | `string` | `weekly` (`weekly`, "
                "`monthly` or `never`) | [07 §In-app update "
                "(residual)](07-distribution.md#in-app-update-residual) |\n"
            ),
        ),
        (
            (
                "│  │  (hidden in unpackaged / Linux; not a Windows "
                "service)                           ││\n│  "
                "└───────────────────────────────────────────────────────────"
                "───────────────────────┘│\n"
                "│                                                           "
                "                           │\n"
            ),
            (
                "│  │  (hidden in unpackaged / Linux; not a Windows "
                "service)                           ││\n│  "
                "└───────────────────────────────────────────────────────────"
                "───────────────────────┘│\n"
                "│                                                           "
                "                           │\n│  ┌─ UPDATES "
                "────────────────────────────────────────────────────────────────────────┐│\n"
                "│  │  Check for updates   [Once a week ▼]   once a month; "
                "never                       ││\n│  │  Status              "
                "Up to date · last checked     [Check "
                "now]                   ││\n│  │  Ready               "
                "Version x.y.z is ready        [Restart and "
                "update]          ││\n│  │  (installed app only; checked "
                "by the release's SHA-512, not signed)              ││\n│  "
                "└───────────────────────────────────────────────────────────"
                "───────────────────────┘│\n"
                "│                                                           "
                "                           │\n"
            ),
        ),
    ],
    "README.md": [
        (
            (
                "FFmpeg comes inside the installer. Text to speech needs a "
                "one-time voice model download,\nwhich you pick and start "
                "from inside the app; after that it works offline.\n"
            ),
            (
                "FFmpeg comes inside the installer. Text to speech needs a "
                "one-time voice model download,\nwhich you pick and start "
                "from inside the app; after that it works offline, apart "
                "from the\nupdate check below.\n\n**Updates.** In-app "
                "updates are built but not yet in a release. Once they "
                "ship, av-kit\nasks GitHub once a week (or once a month, "
                "or never: **Settings → Updates**) for the newest\nrelease "
                "of this repository. The request carries no identifier, "
                "only\nwhat any web request shows (your address and a user "
                "agent). A newer version downloads in\nthe background, and "
                "Settings offers **Restart and update** when it is ready. "
                "The installer\nis not code-signed, so an update is "
                "trusted because its SHA-512 matches the one in the\n"
                "release's `latest.yml`, fetched over HTTPS: whoever "
                "controls this repository's releases\ncontrols what "
                "installs. Updates start with the first release that "
                "carries these files;\nrc.5 and earlier need one more "
                "install by hand.\n"
            ),
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
    rows = [i for i, line in enumerate(lines) if line.startswith(b"| 106 |")]
    if len(rows) != 1:
        print(f"refused: {len(rows)} row(s) start '| 106 |'")
        return 1
    row = lines[rows[0]]
    if b"| executed (Session 106) |" in row:
        print("grouping: row 106 already reads executed (Session 106)")
        return 0
    # The orchestrator set the cell to `plan approved (round 3)` for D-1413.
    for old in (b"| planning |", b"| planned |", b"| plan approved (round 3) |"):
        if row.count(old) == 1:
            lines[rows[0]] = row.replace(old, b"| executed (Session 106) |")
            p.write_bytes(b"\n".join(lines))
            print("grouping: row 106 now reads executed (Session 106)")
            return 0
    print(f"refused: row 106 has no single planning cell: {row[:120]!r}")
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
