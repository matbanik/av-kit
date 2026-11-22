"""Row 7: the canon edits of MEU-163, by bytes.

* ``gui-actions-index.md`` (CRLF): the ``transcript:resume_job`` row after ``transcript:resume``.
* ``10-queue-card-ui.md`` (CRLF): the Delivered note at the end of §Per-job resume (residual).
* ``06-gui.md`` and ``03-service-layer.md`` (CRLF): ``DEFAULTS_CANON``.
* The session grouping (LF): §6 row 101 from ``queued`` to ``executed (Session 101)``.

The exact texts come from ``row-check.py``, which checks them. Every target must be found
exactly once and every file must keep its line endings, or nothing is written.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
_spec = importlib.util.spec_from_file_location("tjr_row_check", HERE / "row-check.py")
assert _spec is not None and _spec.loader is not None
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)

TEN = "docs/build-plan/10-queue-card-ui.md"
TEN_LAST = (
    "| Tests | Unit: the availability rule and the menu order; pytest: resume refused while a "
    "job runs; Electron E2E: the card Resume on a seeded Paused job after a fresh launch reaches "
    'Done on the real backend | Mat, 2026-11-16 ("This should be done with framework and '
    'scripts!") |'
)
DELIVERED = [
    "",
    "> **Delivered (Session 101).**",
    "> - The first Paused job's card offers `Resume` first in its kebab while the processor is "
    "not `Processing` (`CARD_RESUME_RULE`, "
    "`ui/src/renderer/src/features/transcript/transcript-controls.ts:85`; "
    "`TRANSCRIPT_MENU_ORDER` and the test id `resume-job-btn`, "
    "`features/transcript/transcript-card.ts:25`, `:40`, `:99`; the label and the menu case, "
    "`features/transcript/TranscriptPage.tsx:96`, `:325`). Any other card, and every card while "
    "a job runs, omits it. The toolbar keeps its three actions, and a Paused card has no Resume "
    "link (D-1352). AC-163.1 to AC-163.3.",
    "> - The item reads the queue fresh, never from the cache, and sends the existing bodyless "
    "`POST /transcripts/resume` only when the clicked job is still the first Paused job; it "
    "refreshes the page even when the request is refused (`resumeTranscriptJob`, "
    "`features/transcript/transcript-commands.ts:161`). AC-163.4.",
    "> - `resume_processing` is refused with 409 while a job runs, before it reads or writes "
    "anything (`RESUME_GUARD`, `packages/core/src/avkit_core/services/transcript.py:243`; "
    "D-1353). No API route, request body, OpenAPI document or MCP tool changed. AC-163.6.",
    "> - Tests: `ui/tests/unit/transcript-job-resume.test.tsx`; pytest "
    "`test_ac_163_6_refused_while_processing` and `test_ac_163_6_idle_resume_done` "
    "(`tests/unit/test_services.py:1285`, `:1308`); Electron E2E "
    "(`ui/tests/e2e/transcript-job-resume.test.ts`) with a seam, and on the real backend, where "
    "a Paused job seeded by `tests/transcript_paused_fixture.py` resumes after a fresh launch "
    "and reaches Done with its ZIP and compiled file (D-1354). AC-163.5, AC-163.7, AC-163.8.",
    "> - The transcript defaults are Mat's values (D-1355): `requests_per_hour` 20, "
    "`delay_between_requests` 120, `max_retries` 1, `retry_delay` 7, `batch_size` 5 and "
    "`pause_between_batches` 500, with `playlist_end` 0 and `max_words_per_document` 490000 "
    "unchanged (`packages/core/src/avkit_core/services/settings.py:69-74`, "
    "`mcp-server/src/toolsets/settings.ts:34-39`; 06 §Settings Key Convention, 03 Rate cap). "
    "A stored value still wins. Three tests that read the old defaults now set MEU-116's "
    "pacing or turn the cap off (`MEU_116_PACING`, D-1356). Tests: "
    "`tests/unit/test_transcript_defaults.py`, `mcp-server/tests/transcript-defaults.test.ts`. "
    "AC-163.10.",
    "> - The `transcript:resume_job` row in `gui-actions-index.md`. AC-163.9. The plan review "
    "restarted in a disclosed loop after the defaults joined the scope (D-1357). AC-163.1 to "
    "AC-163.10. Plan `docs/execution/plans/2026-11-21-transcript-job-resume/`.",
]


def crlf_lines(raw: bytes, name: str) -> list[bytes]:
    if raw.count(b"\n") != raw.count(b"\r\n"):
        sys.exit(f"canon-edit: {name} holds a bare LF")
    return raw.split(b"\r\n")


def one(lines: list[bytes], text: str, name: str) -> int:
    want = text.encode("utf-8")
    hits = [i for i, line in enumerate(lines) if line == want]
    if len(hits) != 1:
        sys.exit(f"canon-edit: {name}: found {len(hits)} time(s): {text[:70]!r}")
    return hits[0]


def main() -> None:
    out: dict[str, bytes] = {}

    lines = crlf_lines((ROOT / rc.INDEX).read_bytes(), rc.INDEX)
    at = one(lines, rc.RESUME_ROW, rc.INDEX)
    lines.insert(at + 1, rc.INDEX_ROW.encode("utf-8"))
    out[rc.INDEX] = b"\r\n".join(lines)

    lines = crlf_lines((ROOT / TEN).read_bytes(), TEN)
    at = one(lines, TEN_LAST, TEN)
    if any(line.strip() for line in lines[at + 1 :]):
        sys.exit(f"canon-edit: {TEN}: §Per-job resume (residual) is no longer the last section")
    lines[at + 1 : at + 1] = [line.encode("utf-8") for line in DELIVERED]
    out[TEN] = b"\r\n".join(lines)

    for name, edits in rc.CANON_EDITS.items():
        lines = crlf_lines((ROOT / name).read_bytes(), name)
        for old, new in edits:
            lines[one(lines, old, name)] = new.encode("utf-8")
        out[name] = b"\r\n".join(lines)

    raw = (ROOT / rc.GROUPING).read_bytes()
    if b"\r" in raw:
        sys.exit(f"canon-edit: {rc.GROUPING} holds a CR")
    lines = raw.split(b"\n")
    rows = [i for i, line in enumerate(lines) if line.startswith(b"| 101 |")]
    if len(rows) != 1 or lines[rows[0]].count(b"| queued |") != 1:
        sys.exit(f"canon-edit: {rc.GROUPING}: row 101 does not read queued once")
    lines[rows[0]] = lines[rows[0]].replace(b"| queued |", b"| executed (Session 101) |")
    out[rc.GROUPING] = b"\n".join(lines)

    for name, data in out.items():
        (ROOT / name).write_bytes(data)
        print(f"canon-edit: {name}: written")


if __name__ == "__main__":
    main()
