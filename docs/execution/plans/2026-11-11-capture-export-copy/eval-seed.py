"""Session 64 description eval media (implementation-plan.md EVAL_MEDIA; D-608 A or B).

Usage: python eval-seed.py MEDIA_DIR ANSWERS_DIR

Writes three local test inputs into MEDIA_DIR and the answer key into ANSWERS_DIR, which the
agent is never told about:

  meeting.mp4            1 h, 1280x720, 1 fps, H.264: 24 titled slides, 150 s each.
  meeting-transcript.txt timestamped transcript lines spoken over the slides.
  driveway.mp4           2 h, 640x360, 1 fps, H.264: an empty driveway, then a car drives
                         in at a hidden second T and stays parked.
  dashboard-4k.png       3840x2160 screenshot-like PNG whose full-size q90 JPEG is over 500 KB.

ANSWERS_DIR/answers.json holds the asked transcript time, its slide title, T and the PNG's
SHA-256. The script checks its own output: it decodes the meeting frame at the asked time and
the driveway frames at T-1 and T with the pinned FFmpeg and compares them with the pictures it
drew, and it encodes the PNG as a q90 JPEG to show the task is not already met. Any check that
fails exits 1. Both folders must be empty or missing. Nothing is read from or sent to a network.
"""

from __future__ import annotations

import hashlib
import io
import json
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

REPO_ROOT = Path(__file__).resolve().parents[4]
FFMPEG = REPO_ROOT / "packaging" / "ffmpeg-win64" / "ffmpeg.exe"
SEED = 64
SLIDES = 24
SLIDE_S = 150
MEETING_SIZE = (1280, 720)
DRIVEWAY_S = 7200
DRIVEWAY_SIZE = (640, 360)
SCREEN_SIZE = (3840, 2160)
JPEG_LIMIT = 500_000
# The asked line is ASK_OFFSET_S into its slide, so a cell placed before the change shows the
# slide before it: the answer needs a frame at the asked time.
ASK_SLIDE = 16
ASK_OFFSET_S = 9
WORDS_A = ("Harbor", "Copper", "Lantern", "Meadow", "Granite", "Velvet", "Orbit", "Summit",
           "Cedar", "Falcon", "Prism", "Tundra", "Willow", "Ember", "Quartz", "Juniper")
WORDS_B = ("Budget", "Roadmap", "Hiring", "Pricing", "Churn", "Launch", "Margins", "Security",
           "Backlog", "Forecast", "Support", "Vendors", "Latency", "Training", "Inventory", "Audit")


def font(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    for name in ("segoeuib.ttf", "arialbd.ttf", "segoeui.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def run_ffmpeg(args: list[str], cwd: Path) -> None:
    done = subprocess.run(
        [str(FFMPEG), "-hide_banner", "-nostdin", "-y", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=1800,
        check=False,
    )
    if done.returncode != 0:
        raise SystemExit(f"ffmpeg exited {done.returncode}: {done.stderr[-600:]}")


def frame_at(video: Path, second: int) -> Image.Image:
    done = subprocess.run(
        [str(FFMPEG), "-hide_banner", "-nostdin", "-ss", str(second), "-i", str(video),
         "-frames:v", "1", "-f", "image2pipe", "-c:v", "png", "-"],
        capture_output=True,
        timeout=300,
        check=False,
    )
    if done.returncode != 0 or not done.stdout:
        raise SystemExit(f"frame decode at {second}s failed")
    return Image.open(io.BytesIO(done.stdout)).convert("RGB")


def close(a: Image.Image, b: Image.Image) -> float:
    """Mean absolute difference of two same-size RGB pictures, 0 to 255."""
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3


def encode(work: Path, segments: list[tuple[str, int]], out: Path) -> None:
    """Each (picture, seconds) held at 1 fps, joined by the concat filter: exact durations."""
    args: list[str] = []
    for name, seconds in segments:
        args += ["-loop", "1", "-framerate", "1", "-t", str(seconds), "-i", name]
    joined = "".join(f"[{i}:v]" for i in range(len(segments)))
    args += ["-filter_complex", f"{joined}concat=n={len(segments)}:v=1:a=0[v]", "-map", "[v]",
             "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-g", "250",
             "-pix_fmt", "yuv420p", str(out)]
    run_ffmpeg(args, work)


def slide(title: str, index: int, rng: random.Random) -> Image.Image:
    img = Image.new("RGB", MEETING_SIZE, (250, 250, 252))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, MEETING_SIZE[0], 120), fill=(28, 52, 96))
    d.text((60, 30), title, fill=(255, 255, 255), font=font(56))
    body = font(30)
    for row in range(5):
        words = " ".join(rng.choice(WORDS_B).lower() for _ in range(rng.randint(4, 7)))
        d.text((90, 190 + row * 80), f"• {words}", fill=(40, 40, 40), font=body)
    d.text((1140, 660), f"{index + 1}/{SLIDES}", fill=(120, 120, 120), font=font(24))
    return img


def driveway(car_x: int | None) -> Image.Image:
    w, h = DRIVEWAY_SIZE
    img = Image.new("RGB", DRIVEWAY_SIZE, (92, 150, 70))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w, 120), fill=(170, 200, 230))
    d.rectangle((380, 40, 620, 200), fill=(190, 170, 150))
    d.polygon([(370, 40), (500, -10), (630, 40)], fill=(120, 60, 50))
    d.rectangle((420, 120, 500, 200), fill=(90, 90, 100))
    d.polygon([(0, 360), (0, 250), (420, 200), (500, 200), (640, 360)], fill=(120, 120, 120))
    if car_x is not None:
        d.rectangle((car_x, 236, car_x + 150, 296), fill=(200, 30, 30))
        d.rectangle((car_x + 30, 206, car_x + 115, 240), fill=(170, 25, 25))
        for wx in (car_x + 25, car_x + 105):
            d.ellipse((wx, 284, wx + 30, 314), fill=(20, 20, 20))
    return img


def screenshot(rng: random.Random) -> Image.Image:
    img = Image.new("RGB", SCREEN_SIZE, (245, 245, 245))
    d = ImageDraw.Draw(img)
    text = font(22)
    for row in range(0, SCREEN_SIZE[1], 34):
        line = " ".join(f"{rng.choice(WORDS_A).lower()}{rng.randint(0, 9999)}" for _ in range(12))
        d.text((40, row + 6), line, fill=(30, 30, 30), font=text)
    for _ in range(60):
        x, y = rng.randint(1900, 3600), rng.randint(0, 1900)
        colour = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
        d.rectangle((x, y, x + rng.randint(60, 300), y + rng.randint(30, 200)), fill=colour)
    img.paste(Image.effect_noise((1600, 900), 40).convert("RGB"), (2100, 1200))
    return img


def empty_dir(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise SystemExit(f"{path} already holds files; use a new folder")
    path.mkdir(parents=True, exist_ok=True)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: eval-seed.py MEDIA_DIR ANSWERS_DIR", file=sys.stderr)
        return 2
    media, answers = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    if media == answers or answers.is_relative_to(media):
        raise SystemExit("ANSWERS_DIR must sit outside MEDIA_DIR")
    if not FFMPEG.is_file():
        raise SystemExit(f"pinned FFmpeg missing: {FFMPEG}")
    empty_dir(media)
    empty_dir(answers)
    work = answers / "work"
    work.mkdir()
    rng = random.Random(SEED)
    failures: list[str] = []

    # Task 1: the meeting.
    titles: list[str] = []
    while len(titles) < SLIDES:
        title = f"{rng.choice(WORDS_A)} {rng.choice(WORDS_B)} {rng.randint(10, 99)}"
        if title not in titles:
            titles.append(title)
    pictures = []
    for index, title in enumerate(titles):
        picture = slide(title, index, rng)
        picture.save(work / f"slide_{index:02d}.png")
        pictures.append(picture)
    encode(work, [(f"slide_{i:02d}.png", SLIDE_S) for i in range(SLIDES)], media / "meeting.mp4")
    ask_s = ASK_SLIDE * SLIDE_S + ASK_OFFSET_S
    lines = []
    said = iter((
        "let's start with where we are against plan.",
        "this one surprised me, honestly.",
        "I'd park that until the vendor call.",
        "so the number on this slide is the one we keep coming back to.",
        "we'll pick that up next week.",
    ))
    for index in (2, 7, 11, ASK_SLIDE, 20):
        second = index * SLIDE_S + (ASK_OFFSET_S if index == ASK_SLIDE else rng.randint(20, 120))
        stamp = f"{second // 3600:02d}:{second % 3600 // 60:02d}:{second % 60:02d}"
        speaker = rng.choice(("Priya", "Tomas", "Ana", "Wei"))
        lines.append(f"[{stamp}] {speaker}: {next(said)}")
    (media / "meeting-transcript.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    asked = frame_at(media / "meeting.mp4", ask_s)
    want, before = pictures[ASK_SLIDE], pictures[ASK_SLIDE - 1]
    if not close(asked, want) < close(asked, before):
        failures.append(f"meeting frame at {ask_s}s is not slide {ASK_SLIDE + 1}")

    # Task 2: the driveway.
    arrive = rng.randrange(1800, 6600)
    while arrive % 10 == 0:
        arrive += 1
    driveway(None).save(work / "empty.png")
    for step, x in enumerate((-110, 0, 80)):
        driveway(x).save(work / f"in_{step}.png")
    driveway(150).save(work / "parked.png")
    encode(work, [
        ("empty.png", arrive), ("in_0.png", 1), ("in_1.png", 1), ("in_2.png", 1),
        ("parked.png", DRIVEWAY_S - arrive - 3),
    ], media / "driveway.mp4")
    empty = Image.open(work / "empty.png").convert("RGB")
    first = Image.open(work / "in_0.png").convert("RGB")
    if close(frame_at(media / "driveway.mp4", arrive - 1), empty) > 3:
        failures.append(f"driveway frame at {arrive - 1}s is not empty")
    if close(frame_at(media / "driveway.mp4", arrive), empty) <= close(frame_at(media / "driveway.mp4", arrive), first):
        failures.append(f"driveway frame at {arrive}s shows no car")

    # Task 3: the 4K screenshot.
    shot = screenshot(rng)
    shot.save(media / "dashboard-4k.png", format="PNG")
    buffer = io.BytesIO()
    shot.save(buffer, format="JPEG", quality=90)
    full_q90 = len(buffer.getvalue())
    if full_q90 <= JPEG_LIMIT:
        failures.append(f"a full-size q90 JPEG is {full_q90} B, already under the limit")
    sizes = {}
    for edge, quality in ((1920, 90), (1920, 75), (1600, 90), (1280, 90)):
        target = (edge, (2 * edge * SCREEN_SIZE[1] + SCREEN_SIZE[0]) // (2 * SCREEN_SIZE[0]))
        buffer = io.BytesIO()
        shot.resize(target, Image.Resampling.LANCZOS).save(buffer, format="JPEG", quality=quality)
        sizes[f"{edge}q{quality}"] = len(buffer.getvalue())

    key = {
        "meeting": {"ask_s": ask_s, "title": titles[ASK_SLIDE], "previous_title": titles[ASK_SLIDE - 1]},
        "driveway": {"arrive_s": arrive},
        "screenshot": {
            "sha256": hashlib.sha256((media / "dashboard-4k.png").read_bytes()).hexdigest(),
            "full_q90_bytes": full_q90,
            "shrunk_jpeg_bytes": sizes,
        },
        "media_sha256": {
            name: hashlib.sha256((media / name).read_bytes()).hexdigest()
            for name in ("meeting.mp4", "driveway.mp4", "meeting-transcript.txt")
        },
    }
    (answers / "answers.json").write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8", newline="\n")
    for name in sorted(p.name for p in media.iterdir()):
        print(f"media {name} {(media / name).stat().st_size} B")
    print(f"meeting ask {ask_s}s; driveway arrival {arrive}s; 4K q90 JPEG {full_q90} B; shrunk {sizes}")
    for failure in failures:
        print(f"FAIL {failure}")
    print("eval-seed: ok" if not failures else f"eval-seed: {len(failures)} check(s) failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
