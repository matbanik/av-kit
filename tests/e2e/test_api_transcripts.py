"""MEU-16 transcript queue tests (AC-16.1–16.2)."""

from __future__ import annotations

from pathlib import Path

from tests.e2e.api_fakes import AUTH, JOB_A, JOB_B, make_client

from avkit_core.domain.enums import TranscriptStatus


def _assert_envelope(body: dict[str, object]) -> None:
    error = body["error"]
    assert set(error) == {"code", "message", "details"}


def test_ac_16_1_transcript_lifecycle_and_conflicts() -> None:
    client, fake, _tts, _models = make_client()
    created = client.post(
        "/api/v1/transcripts",
        headers=AUTH,
        json={"channel_url": "https://www.youtube.com/@other"},
    )
    extra = client.post(
        "/api/v1/transcripts",
        headers=AUTH,
        json={"channel_url": "https://www.youtube.com/@other", "nope": 1},
    )
    listed = client.get("/api/v1/transcripts", headers=AUTH)
    start = client.post("/api/v1/transcripts/start", headers=AUTH)
    pause = client.post("/api/v1/transcripts/pause", headers=AUTH)
    resume = client.post("/api/v1/transcripts/resume", headers=AUTH)
    stop = client.post("/api/v1/transcripts/stop", headers=AUTH)
    reorder_extra = client.put(
        "/api/v1/transcripts/reorder",
        headers=AUTH,
        json={"job_ids": [JOB_A], "nope": 1},
    )
    created_id = created.json()["id"]
    reorder = client.put(
        "/api/v1/transcripts/reorder",
        headers=AUTH,
        json={"job_ids": [JOB_A, created_id]},
    )
    swapped = client.put(
        "/api/v1/transcripts/reorder",
        headers=AUTH,
        json={"job_ids": [created_id, JOB_A]},
    )
    requeue_pending = client.post(f"/api/v1/transcripts/{JOB_A}/requeue", headers=AUTH)
    retry_pending = client.post(f"/api/v1/transcripts/{JOB_A}/retry", headers=AUTH)
    fake.set_status(JOB_A, TranscriptStatus.Cancelled)
    requeue_ok = client.post(f"/api/v1/transcripts/{JOB_A}/requeue", headers=AUTH)
    fake.set_status(JOB_A, TranscriptStatus.Failed)
    retry_ok = client.post(f"/api/v1/transcripts/{JOB_A}/retry", headers=AUTH)
    compiled = client.post(f"/api/v1/transcripts/{JOB_A}/compile", headers=AUTH)
    deleted = client.delete(f"/api/v1/transcripts/{JOB_A}", headers=AUTH)
    missing = client.get(f"/api/v1/transcripts/{JOB_B}", headers=AUTH)

    assert created.status_code == 201
    assert extra.status_code == 422
    _assert_envelope(extra.json())
    assert listed.status_code == 200
    assert set(listed.json()) == {"items", "processor"}
    assert start.status_code == 202
    assert pause.status_code == 202
    assert resume.status_code == 202
    assert stop.status_code == 202
    assert reorder_extra.status_code == 422
    _assert_envelope(reorder_extra.json())
    assert reorder.status_code == 200
    assert swapped.status_code == 200
    assert fake.last_reorder == [created_id, JOB_A]
    assert [item["id"] for item in swapped.json()["items"]] == [created_id, JOB_A]
    assert requeue_pending.status_code == 409
    _assert_envelope(requeue_pending.json())
    assert retry_pending.status_code == 409
    _assert_envelope(retry_pending.json())
    assert requeue_ok.status_code == 200
    assert retry_ok.status_code == 200
    assert compiled.status_code == 200
    assert list(compiled.json()) == ["compiled_paths"]
    assert [Path(item) for item in compiled.json()["compiled_paths"]] == [
        Path("C:/tmp/compiled/vol-1.md")
    ]
    assert "text" not in compiled.json()
    assert deleted.status_code == 204
    assert missing.status_code == 404


def test_ac_16_2_aggregates_without_video_ids_or_text() -> None:
    client, _fake, _tts, _models = make_client()
    response = client.get(f"/api/v1/transcripts/{JOB_A}", headers=AUTH)
    assert response.status_code == 200
    body = response.json()
    assert body["transcripts_done"] == 1
    assert body["last_title"] == "Latest"
    assert body["last_item_status"] == "Pending"
    assert "video_ids" not in body
    assert "text" not in body
    assert "items" not in body
    listed = client.get("/api/v1/transcripts", headers=AUTH)
    payload = listed.json()
    assert "video_ids" not in listed.text
    assert all("text" not in item for item in payload["items"])
    assert all("video_ids" not in item for item in payload["items"])


def test_ac_115_8_job_out_carries_the_latest_item_message() -> None:
    from dataclasses import replace

    from avkit_core.domain.enums import TranscriptItemStatus

    client, fake, _tts, _models = make_client()
    job_text = "1 of 2 videos failed. Last: Couldn't get captions: the video is age-restricted."
    fake.jobs = [replace(fake.jobs[0], status=TranscriptStatus.Failed, error_message=job_text)]
    latest = fake.items[JOB_A][1]
    failed_text = "Couldn't get captions: x."
    skipped_text = "No captions for this video."
    done_path = Path("C:/tmp/transcripts/raw/latest.md")
    cases = [
        (TranscriptItemStatus.Failed, None, failed_text, failed_text),
        (TranscriptItemStatus.Skipped, None, skipped_text, skipped_text),
        (TranscriptItemStatus.Pending, None, "Retrying after a block.", None),
        (TranscriptItemStatus.Done, done_path, None, None),
    ]
    seen = []
    for status, path, message, _expected in cases:
        fake.items[JOB_A][1] = replace(latest, status=status, path=path, error_message=message)
        one = client.get(f"/api/v1/transcripts/{JOB_A}", headers=AUTH).json()
        listed = client.get("/api/v1/transcripts", headers=AUTH).json()["items"][0]
        seen.append(
            (
                one["last_item_status"],
                one.get("last_item_message", "<absent>"),
                listed.get("last_item_message", "<absent>"),
                one["error_message"],
            )
        )
    assert seen == [
        (status.value, expected, expected, job_text) for status, _path, _message, expected in cases
    ]


def test_ac_122_15_last_title_comes_only_from_a_processed_item() -> None:
    from dataclasses import replace

    client, fake, _tts, _models = make_client()
    first, latest = fake.items[JOB_A]
    assert (first.title, latest.title) == ("First", "Latest")
    fake.items[JOB_A] = [replace(first, processed_at=None), replace(latest, processed_at=None)]
    unprocessed = client.get(f"/api/v1/transcripts/{JOB_A}", headers=AUTH).json()
    listed = client.get("/api/v1/transcripts", headers=AUTH).json()["items"][0]
    assert (unprocessed["last_title"], listed["last_title"]) == (None, None)
    assert unprocessed["last_item_status"] == "Pending"

    fake.items[JOB_A] = [first, replace(latest, processed_at=None)]
    processed = client.get(f"/api/v1/transcripts/{JOB_A}", headers=AUTH).json()
    assert processed["last_title"] == "First"
