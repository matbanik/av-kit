"""Paused transcript job fixture for MEU-163 (Session 101, PAUSED_FIXTURE, AC-163.8).

`seed(app_data)` builds the real services on a fresh `app_data` and stores one channel job
that a blocked caption request left `Paused`, with its one video already `Done` and its raw
file on disk. Resuming it needs no network: the worker finds no pending item, compiles the
raw file and zips it, and the job ends `Done`.

The folder must be empty or absent, and inside the system temp folder or `C:/Temp`, so the
fixture never writes into a real profile. Test input, not product code.
`python -m tests.transcript_paused_fixture <app_data>` prints `fixture: paused job <id>`.
"""

from __future__ import annotations

import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from avkit_api.wiring import build_services
from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus
from avkit_core.domain.transcript import TranscriptItem, TranscriptJob

CHANNEL_NAME = "Resume Fixture"
CHANNEL_URL = "https://www.youtube.com/@resume-fixture"
SLUG = "resume-fixture"
VIDEO_ID = "vid00000001"
VIDEO_TITLE = "Resume fixture video"
BODY = "A paused job resumes offline."
PAUSED_MESSAGE = "Paused: YouTube blocked caption requests."
ALLOWED_ROOTS = (Path(tempfile.gettempdir()), Path("C:/Temp"))


def _inside_allowed_root(path: Path) -> bool:
    resolved = path.resolve()
    for root in ALLOWED_ROOTS:
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        return True
    return False


def _raw_markdown() -> str:
    """The raw file in the worker's own shape (front matter, then the text)."""
    return (
        "---\n"
        f"video_id: {VIDEO_ID}\n"
        f'title: "{VIDEO_TITLE}"\n'
        f'channel: "{CHANNEL_NAME}"\n'
        f"url: https://www.youtube.com/watch?v={VIDEO_ID}\n"
        "---\n\n"
        f"{BODY}\n"
    )


def seed(app_data: Path) -> str:
    """Store the Paused job in `app_data` and return its id."""
    if not _inside_allowed_root(app_data):
        raise SystemExit(f"refused: {app_data} is outside the temp folder and C:/Temp")
    if app_data.exists() and any(app_data.iterdir()):
        raise SystemExit(f"refused: {app_data} exists and is not empty")
    app_data.mkdir(parents=True, exist_ok=True)
    output_dir = app_data / "out" / SLUG
    raw_path = output_dir / "raw" / f"{VIDEO_ID}.md"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    (output_dir / "compiled").mkdir(parents=True, exist_ok=True)
    raw_path.write_text(_raw_markdown(), encoding="utf-8", newline="\n")
    now = datetime.now(UTC)
    job = TranscriptJob(
        id=str(uuid4()),
        channel_url=CHANNEL_URL,
        channel_name=CHANNEL_NAME,
        status=TranscriptStatus.Paused,
        output_dir=output_dir,
        video_count=1,
        word_count=len(BODY.split()),
        zip_path=None,
        queue_position=0,
        error_message=PAUSED_MESSAGE,
        created_at=now,
        updated_at=now,
    )
    item = TranscriptItem(
        id=str(uuid4()),
        job_id=job.id,
        video_id=VIDEO_ID,
        title=VIDEO_TITLE,
        language="en",
        word_count=len(BODY.split()),
        path=raw_path,
        status=TranscriptItemStatus.Done,
        error_message=None,
        retry_count=0,
        processed_at=now,
    )
    services, dispose = build_services(app_data=app_data)
    try:
        with services.transcript._uow_factory() as uow:
            uow.transcripts.add_job(job)
            uow.transcripts.replace_items(job.id, [item])
            uow.commit()
    finally:
        dispose()
    return job.id


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m tests.transcript_paused_fixture <app_data>", file=sys.stderr)
        return 2
    job_id = seed(Path(argv[0]))
    print(f"fixture: paused job {job_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
