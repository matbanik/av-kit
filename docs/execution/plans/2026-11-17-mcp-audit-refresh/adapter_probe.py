"""One fetch through the product's TranscriptAdapter (recheck of YOUTUBE-CAPTIONS-IP-BLOCK)."""

import datetime

from avkit_infra.transcript.adapter import TranscriptAdapter

print("when", datetime.datetime.now().isoformat(timespec="seconds"))
a = TranscriptAdapter()
for vid in ("VSU9VjZFoLI",):
    try:
        r = a.get_transcript(vid, ["en"])
        text = getattr(r, "text", None)
        print(
            vid,
            type(r).__name__,
            "language",
            getattr(r, "language", None),
            "chars",
            len(text) if text else None,
        )
    except Exception as e:
        print(vid, "FAIL", type(e).__name__, str(e).splitlines()[0][:200] if str(e) else "")
