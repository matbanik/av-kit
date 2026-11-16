"""Orientation fixtures for MEU-146 (Session 75, D-904, WEBP_PIN): one Pillow builder.

`build(out_dir)` writes eight 40x30 images, blue with a red top-left block, each carrying
EXIF orientation 6 in a different place, and returns what each one holds, so a fixture that
lost its tag fails the test that uses it instead of passing it:

- `o6.jpg`, `o6.png`, `o6.mpo.jpg`, `o6.webp`: written by Pillow with `exif=`. The PNG's
  `eXIf` chunk sits before `IDAT`; the WebP is `VP8X` with flag `0x08` and an `EXIF` chunk.
- `o6-after-idat.png`: the `eXIf` chunk spliced in after `IDAT`.
- `o6-prefixed.png`: an `eXIf` chunk whose data starts with `Exif\\0\\0`.
- `o6-raw-profile.png`: no `eXIf`; the tag is in a `Raw profile type exif` text chunk.
- `o6-xmp.jpg`: no EXIF block; the tag is XMP `tiff:Orientation`.

Pillow's `getexif()` reads 6 from every one of them. Chromium turns only the first three
(`s75-plan-probe-electron.txt`, `s75-plan-probe-extra-electron.txt`). Test input, not
product code. `python -m tests.orientation_fixtures <out_dir>` prints the report as JSON.
"""

from __future__ import annotations

import io
import json
import struct
import sys
import zlib
from pathlib import Path

from PIL import Image

SIZE = (40, 30)
BLUE = (20, 20, 200)
RED = (230, 20, 20)
RED_BLOCK = (0, 0, 10, 10)
ORIENTATION = 6
EXIF_ORIENTATION_TAG = 0x0112
EXIF_PREFIX = b"Exif\x00\x00"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
FIXTURE_NAMES = (
    "o6.jpg",
    "o6.png",
    "o6.mpo.jpg",
    "o6.webp",
    "o6-after-idat.png",
    "o6-prefixed.png",
    "o6-raw-profile.png",
    "o6-xmp.jpg",
)
XMP_ORIENTATION = (
    '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
    '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
    '<rdf:Description xmlns:tiff="http://ns.adobe.com/tiff/1.0/" tiff:Orientation="6"/>'
    "</rdf:RDF></x:xmpmeta>"
).encode("ascii")


def base_image() -> Image.Image:
    """The stored frame: 40x30 blue with a red 10x10 block at the top left."""
    image = Image.new("RGB", SIZE, BLUE)
    image.paste(RED, RED_BLOCK)
    return image


def exif_bytes(orientation: int = ORIENTATION) -> bytes:
    """An EXIF block holding only the orientation, as Pillow writes it (with `Exif\\0\\0`)."""
    exif = Image.Exif()
    exif[EXIF_ORIENTATION_TAG] = orientation
    return exif.tobytes()


def tiff_body(orientation: int = ORIENTATION) -> bytes:
    """The same block with no `Exif\\0\\0` prefix: what an `eXIf` chunk holds."""
    raw = exif_bytes(orientation)
    return raw[len(EXIF_PREFIX) :] if raw.startswith(EXIF_PREFIX) else raw


def png_chunk(kind: bytes, data: bytes) -> bytes:
    """One PNG chunk: length, type, data and the CRC32 of type plus data."""
    crc = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def png_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    """The (type, data) pairs of a PNG, in file order."""
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG")
    pos = len(PNG_SIGNATURE)
    chunks: list[tuple[bytes, bytes]] = []
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        kind = data[pos + 4 : pos + 8]
        chunks.append((kind, data[pos + 8 : pos + 8 + length]))
        pos += 12 + length
    return chunks


def build_png(chunks: list[tuple[bytes, bytes]]) -> bytes:
    return PNG_SIGNATURE + b"".join(png_chunk(kind, data) for kind, data in chunks)


def webp_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    """The (fourcc, data) pairs inside a WebP's RIFF container, in file order."""
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("not a WebP")
    pos = 12
    chunks: list[tuple[bytes, bytes]] = []
    while pos + 8 <= len(data):
        fourcc = data[pos : pos + 4]
        (length,) = struct.unpack("<I", data[pos + 4 : pos + 8])
        chunks.append((fourcc, data[pos + 8 : pos + 8 + length]))
        pos += 8 + length + (length & 1)
    return chunks


def _encode(image: Image.Image, fmt: str, **params: object) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format=fmt, **params)
    return buffer.getvalue()


def fixture_bytes() -> dict[str, bytes]:
    """The eight fixtures' bytes by file name."""
    raw = exif_bytes()
    body = tiff_body()
    plain = png_chunks(_encode(base_image(), "PNG"))
    idat = next(index for index, (kind, _) in enumerate(plain) if kind == b"IDAT")
    hexed = (EXIF_PREFIX + body).hex()
    raw_profile = b"Raw profile type exif\x00" + (
        f"\nexif\n{len(hexed) // 2:8d}\n{hexed}\n".encode("ascii")
    )
    return {
        "o6.jpg": _encode(base_image(), "JPEG", quality=95, exif=raw),
        "o6.png": _encode(base_image(), "PNG", exif=raw),
        "o6.mpo.jpg": _encode(
            base_image(), "MPO", exif=raw, save_all=True, append_images=[base_image()]
        ),
        "o6.webp": _encode(base_image(), "WEBP", exif=raw),
        "o6-after-idat.png": build_png([*plain[:-1], (b"eXIf", body), plain[-1]]),
        "o6-prefixed.png": build_png([*plain[:idat], (b"eXIf", raw), *plain[idat:]]),
        "o6-raw-profile.png": build_png([*plain[:idat], (b"tEXt", raw_profile), *plain[idat:]]),
        "o6-xmp.jpg": _encode(base_image(), "JPEG", quality=95, xmp=XMP_ORIENTATION),
    }


def _block_tag(info: dict[object, object]) -> int | None:
    """Pillow's own parse of the EXIF block the open file carries (None with no block)."""
    data = info.get("exif")
    if not isinstance(data, bytes) or not data:
        return None
    exif = Image.Exif()
    exif.load(data)
    value = exif.get(EXIF_ORIENTATION_TAG)
    return value if isinstance(value, int) else None


def describe(path: Path) -> dict[str, object]:
    """What one fixture holds: format, size, EXIF-block tag at open, `getexif()` tag."""
    data = path.read_bytes()
    with Image.open(path) as image:
        fmt = image.format
        block = _block_tag(image.info)
        image.load()
        size = list(image.size)
        value = image.getexif().get(EXIF_ORIENTATION_TAG)
    report: dict[str, object] = {
        "format": fmt,
        "size": size,
        "exif_block_tag": block,
        "getexif_tag": value if isinstance(value, int) else None,
    }
    if fmt == "PNG":
        kinds = [kind for kind, _ in png_chunks(data)]
        report["chunks"] = [kind.decode("ascii") for kind in kinds]
    if fmt == "WEBP":
        chunks = webp_chunks(data)
        vp8x = next((body for fourcc, body in chunks if fourcc == b"VP8X"), b"")
        report["vp8x_flags"] = vp8x[0] if vp8x else None
        report["exif_chunk"] = any(fourcc == b"EXIF" for fourcc, _ in chunks)
    return report


def build(out_dir: Path) -> dict[str, dict[str, object]]:
    """Write the eight fixtures into `out_dir` and return each one's report by name."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, dict[str, object]] = {}
    for name, data in fixture_bytes().items():
        path = out_dir / name
        path.write_bytes(data)
        report[name] = describe(path)
    return report


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m tests.orientation_fixtures <out_dir>", file=sys.stderr)
        return 2
    print(json.dumps(build(Path(argv[0])), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
