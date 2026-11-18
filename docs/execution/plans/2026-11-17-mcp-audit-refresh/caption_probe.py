"""One read-only caption fetch from this network (triage recheck of YOUTUBE-CAPTIONS-IP-BLOCK)."""

import datetime
import importlib.metadata

from youtube_transcript_api import YouTubeTranscriptApi

print("when", datetime.datetime.now().isoformat(timespec="seconds"))
print("youtube-transcript-api", importlib.metadata.version("youtube-transcript-api"))
api = YouTubeTranscriptApi()
for vid in ("jNQXAC9IVRw",):
    try:
        t = api.fetch(vid, languages=["en"])
        snippets = list(t)
        print(
            vid,
            "OK",
            len(snippets),
            "snippets; first:",
            repr(snippets[0].text[:60]) if snippets else None,
        )
    except Exception as e:  # report the class and the first line only
        print(vid, "FAIL", type(e).__name__, str(e).splitlines()[0][:200] if str(e) else "")
