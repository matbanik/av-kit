"""Session 53 row 0a: which URL shapes give titles and a channel name (D-353, D-354, D-358).

--recorded makes no network request. It checks yt-dlp's installed version and the
_tab.py strings the plan cites, and writes the plan's shape table with
`live: not measured`.

--live, only under Mat's yes to D-353, runs yt-dlp flat once on each of four URLs with
the adapter's own options plus extract_flat and playlistend 3, no cookies and
download=False. It records which fields are present, never their values. A 429 or a
bot check records that URL as `not run`, with no retry.

Exit 0 when every measured shape matches the plan, 1 on a contradiction (S8), 2 on a
usage error.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import yt_dlp
from yt_dlp.version import __version__ as YT_DLP_VERSION

from avkit_infra.youtube.adapter import YouTubeAdapter, _YtDlpLogger

EXPECTED_VERSION = "2026.10.26"
TAB_SOURCE = Path(yt_dlp.__file__).parent / "extractor" / "youtube" / "_tab.py"
CITED = (
    ("flat entry title", "'title': title,"),
    ("flat entry channel", "'channel': channel,"),
    ("Videos tab title expectation", "'Creative Commons - Videos'"),
    ("tab names may be translated", "NB: Name may be translated"),
    ("extra tabs extracted in full", "entries.extend(map(self._real_extract, extra_tabs))"),
    ("a sole tab returned directly", "if len(entries) == 1:\n            return entries[0]"),
    ("nested tabs announced", "'Downloading as multiple playlists, separated by tabs. '"),
)
CHANNEL = "https://www.youtube.com/channel/UCTwECeGqMZee77BjdoYtI2Q"
SHAPES = (
    ("channel-videos-tab", f"{CHANNEL}/videos"),
    ("bare-channel", CHANNEL),
    ("playlist", "https://www.youtube.com/playlist?list=PLav47HAVZMjnA3P7yQvneyQPiVxZ6erFS"),
    ("single-video", "https://www.youtube.com/watch?v=jNQXAC9IVRw"),
)
RECORDED_TABLE = """\
| URL shape | Top-level title | Top-level channel | Entries |
|---|---|---|---|
| Channel Videos tab | "<channel> - Videos" | the channel | flat url entries: id, title, channel |
| Playlist | the playlist's title | the owner | the same |
| Single video | the video's title | the uploader | none |
| Bare channel, 2+ tabs give a result | the channel's | the channel | nested tabs (FLAT_TABS) |
| Bare channel, one tab gives a result | as that tab | as that tab | as that tab |"""
BLOCK_NEEDLES = ("429", "too many requests", "sign in to confirm", "not a bot")


def _present(value: object) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _types(entries: list[object]) -> str:
    counts = Counter(
        str(e.get("_type")) if isinstance(e, dict) else type(e).__name__ for e in entries
    )
    return "{" + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) + "}"


def _count(entries: list[object], key: str) -> int:
    return sum(1 for e in entries if isinstance(e, dict) and _present(e.get(key)))


def check_source(out: list[str]) -> list[str]:
    problems: list[str] = []
    out.append(f"yt-dlp version: {YT_DLP_VERSION} (expected {EXPECTED_VERSION})")
    if YT_DLP_VERSION != EXPECTED_VERSION:
        problems.append(f"yt-dlp is {YT_DLP_VERSION}, not {EXPECTED_VERSION}")
    text = TAB_SOURCE.read_text(encoding="utf-8")
    for label, needle in CITED:
        found = needle in text
        out.append(f"source: {label}: {'found' if found else 'MISSING'}")
        if not found:
            problems.append(f"_tab.py no longer holds the cited string for {label}")
    return problems


def describe_entries(entries: list[object], out: list[str], indent: str) -> None:
    out.append(
        f"{indent}entries: {len(entries)}; _type {_types(entries)}; id {_count(entries, 'id')}/"
        f"{len(entries)}; title {_count(entries, 'title')}/{len(entries)}; channel "
        f"{_count(entries, 'channel')}/{len(entries)}"
    )


def measure(label: str, url: str, out: list[str]) -> list[str]:
    problems: list[str] = []
    adapter = YouTubeAdapter()
    opts = adapter._base_opts(_YtDlpLogger(False))  # noqa: SLF001 - the adapter's own options
    opts["extract_flat"] = True
    opts["playlistend"] = 3
    out.append(f"== {label}: {url}")
    try:
        info, _logger = adapter._run_extract(url, opts, download=False)  # noqa: SLF001
    except Exception as exc:  # noqa: BLE001 - a block is recorded, never retried
        text = str(exc).casefold()
        reason = (
            "blocked (429 or bot check)"
            if any(n in text for n in BLOCK_NEEDLES)
            else type(exc).__name__
        )
        out.append(f"  not run: {reason}; treated as do-nothing for this shape")
        return problems
    fields = "; ".join(
        f"{key} {'present' if _present(info.get(key)) else 'absent'}"
        for key in ("channel", "uploader", "title")
    )
    out.append(f"  top: _type={info.get('_type')!s}; {fields}")
    entries = info.get("entries")
    if not isinstance(entries, list):
        out.append("  entries: none")
        entries = []
    else:
        describe_entries(entries, out, "  ")
    nested = [e for e in entries if isinstance(e, dict) and e.get("_type") == "playlist"]
    if label in ("channel-videos-tab", "playlist"):
        if not entries or _count(entries, "title") != len(entries):
            problems.append(f"{label}: an entry lacks a title")
        if not _present(info.get("channel")):
            problems.append(f"{label}: no top-level channel")
        if nested:
            problems.append(f"{label}: holds nested playlists")
    elif label == "single-video":
        if not _present(info.get("title")):
            problems.append("single-video: no title")
    elif label == "bare-channel":
        if not nested:
            out.append("  nested: not seen live (one tab returned directly)")
        for index, tab in enumerate(nested):
            inner = tab.get("entries")
            if not isinstance(inner, list):
                out.append(f"  tab {index}: no entries list")
                problems.append(f"bare-channel: tab {index} has no entries list")
                continue
            describe_entries(inner, out, f"  tab {index}: ")
            if _count(inner, "id") != len(inner) or _count(inner, "title") != len(inner):
                problems.append(f"bare-channel: tab {index} has an entry without id or title")
            if any(isinstance(e, dict) and e.get("_type") == "playlist" for e in inner):
                out.append(f"  tab {index}: holds a nested playlist (FLAT_TABS gives it nothing)")
        if nested and not _present(info.get("channel")):
            problems.append("bare-channel: no top-level channel")
    return problems


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--recorded", action="store_true")
    mode.add_argument("--live", action="store_true")
    args = parser.parse_args(argv)
    out: list[str] = ["s53 row 0a: URL shapes (fields present, never values)"]
    problems = check_source(out)
    out.append("recorded shapes, from yt-dlp's installed source:")
    out.append(RECORDED_TABLE)
    if args.live:
        out.append("live: measured (D-353 yes, 2026-11-07); playlistend 3; no cookies; no retry")
        for label, url in SHAPES:
            problems.extend(measure(label, url, out))
    else:
        out.append("live: not measured")
    for problem in problems:
        out.append(f"PROBLEM: {problem}")
    out.append(f"measure-shapes: {len(problems)} problem(s)")
    print("\n".join(out))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
