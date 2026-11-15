"""The deep-research skill's image-strip script (Session 87, AC-1 to AC-6;
docs/execution/plans/2026-11-15-framework-small-syncs).

Gemini's portal export embeds each figure as a base64 ``data:image`` URI, either as a
reference definition (``[image1]: <data:image/png;base64,...>``) or inline
(``![alt](data:image/png;base64,...)``).
``STRIP`` decodes every one to ``{topic}/images/<provider>-<id>.<ext>``, points the link at the
file and rewrites the output in place. These are the 18 tests of the global
``P:/.agent/tests/test_strip_embedded_images.py``, renamed ``test_ac_<n>_<upstream name>``, plus a
CRLF case; the CLI cases run the script as a subprocess through ``uv run python``.

Each test asserts ``STRIP.is_file()`` before it loads or runs the script, so a missing script
fails by assertion, not by an import error.
"""

from __future__ import annotations

import base64
import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
STRIP = ROOT / ".agent/skills/deep-research-prompting/scripts/strip_embedded_images.py"

PNG = b"\x89PNG\r\n\x1a\n" + bytes(range(64))
JPEG = b"\xff\xd8\xff\xe0" + bytes(range(32))
SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>'


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def load(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    assert STRIP.is_file(), f"missing {STRIP.relative_to(ROOT).as_posix()}"
    spec = importlib.util.spec_from_file_location("strip_embedded_images", STRIP)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # dataclasses resolve their module through sys.modules while the class is built.
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def run(*args: str) -> subprocess.CompletedProcess[str]:
    assert STRIP.is_file(), f"missing {STRIP.relative_to(ROOT).as_posix()}"
    return subprocess.run(
        ["uv", "run", "python", str(STRIP), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


@pytest.fixture
def topic(tmp_path: Path) -> Path:
    root = tmp_path / "topic"
    root.mkdir()
    return root


def write(path: Path, text: str, newline: str = "\n") -> Path:
    path.write_text(text, encoding="utf-8", newline=newline)
    return path


# AC-1: reference definitions and inline images are decoded and repointed.


def test_ac_1_reference_definition_is_decoded_and_repointed(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    strip = load(monkeypatch)
    out = write(
        topic / "output-gemini.md",
        f"# Report\n\n![][image1]\n\nText.\n\n[image1]: <data:image/png;base64,{b64(PNG)}>\n",
    )
    written = strip.strip_file(out)
    image = topic / "images" / "gemini-image1.png"
    assert written == [image]
    assert image.read_bytes() == PNG
    text = out.read_text(encoding="utf-8")
    assert "data:image" not in text
    assert "[image1]: images/gemini-image1.png" in text
    assert "![][image1]" in text


def test_ac_1_reference_definition_without_angle_brackets(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    strip = load(monkeypatch)
    out = write(
        topic / "output-gemini.md", f"![][fig2]\n\n[fig2]: data:image/jpeg;base64,{b64(JPEG)}\n"
    )
    strip.strip_file(out)
    assert (topic / "images" / "gemini-fig2.jpeg").read_bytes() == JPEG
    text = out.read_text(encoding="utf-8")
    assert "data:image" not in text
    assert "[fig2]: images/gemini-fig2.jpeg" in text


def test_ac_1_inline_image_is_decoded_and_repointed(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    strip = load(monkeypatch)
    out = write(
        topic / "output-chatgpt.md",
        f"See ![Market share](data:image/png;base64,{b64(PNG)}) and "
        f"![](data:image/png;base64,{b64(PNG[::-1])}).\n",
    )
    written = strip.strip_file(out)
    assert [p.name for p in written] == ["chatgpt-inline1.png", "chatgpt-inline2.png"]
    assert (topic / "images" / "chatgpt-inline1.png").read_bytes() == PNG
    assert (topic / "images" / "chatgpt-inline2.png").read_bytes() == PNG[::-1]
    text = out.read_text(encoding="utf-8")
    assert "![Market share](images/chatgpt-inline1.png)" in text
    assert "![](images/chatgpt-inline2.png)" in text
    assert "data:image" not in text


def test_ac_1_svg_xml_subtype_maps_to_svg_extension(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    strip = load(monkeypatch)
    out = write(topic / "output-gemini.md", f"[image3]: <data:image/svg+xml;base64,{b64(SVG)}>\n")
    strip.strip_file(out)
    assert (topic / "images" / "gemini-image3.svg").read_bytes() == SVG
    assert "data:image" not in out.read_text(encoding="utf-8")


# AC-2: a second run changes nothing, and a file with no images keeps its bytes.


def test_ac_2_second_run_is_a_no_op(monkeypatch: pytest.MonkeyPatch, topic: Path) -> None:
    strip = load(monkeypatch)
    out = write(
        topic / "output-gemini.md", f"![][image1]\n\n[image1]: <data:image/png;base64,{b64(PNG)}>\n"
    )
    strip.strip_file(out)
    first = out.read_bytes()
    images = sorted(p.name for p in (topic / "images").iterdir())
    assert strip.strip_file(out) == []
    assert out.read_bytes() == first
    assert sorted(p.name for p in (topic / "images").iterdir()) == images


def test_ac_2_file_without_images_is_untouched(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    strip = load(monkeypatch)
    out = write(topic / "output-claude.md", "# Report\n\nNo figures here.\n")
    before = out.read_bytes()
    assert strip.strip_file(out) == []
    assert out.read_bytes() == before
    assert not (topic / "images").exists()


# AC-3: two figures never share a file (Zorivest R1-F1).


def test_ac_3_reference_and_inline_images_never_share_a_file(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    """A reference labelled inline1 and the first inline image are two figures."""
    strip = load(monkeypatch)
    out = write(
        topic / "output-gemini.md",
        f"![a][inline1] ![b](data:image/png;base64,{b64(PNG[::-1])})\n\n"
        f"[inline1]: <data:image/png;base64,{b64(PNG)}>\n",
    )
    written = strip.strip_file(out)
    assert len(set(written)) == 2
    assert written[0].read_bytes() == PNG[::-1]
    assert written[1].read_bytes() == PNG
    text = out.read_text(encoding="utf-8")
    assert f"![b](images/{written[0].name})" in text
    assert f"[inline1]: images/{written[1].name}" in text


def test_ac_3_labels_that_normalize_alike_keep_both_images(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    """'fig 1' and 'fig-1' are different labels with different figures."""
    strip = load(monkeypatch)
    out = write(
        topic / "output-gemini.md",
        f"![a][fig 1] ![b][fig-1]\n\n"
        f"[fig 1]: <data:image/png;base64,{b64(PNG)}>\n"
        f"[fig-1]: <data:image/png;base64,{b64(PNG[::-1])}>\n",
    )
    written = strip.strip_file(out)
    assert len(set(written)) == 2
    assert written[0].read_bytes() == PNG
    assert written[1].read_bytes() == PNG[::-1]
    text = out.read_text(encoding="utf-8")
    assert f"[fig 1]: images/{written[0].name}" in text
    assert f"[fig-1]: images/{written[1].name}" in text


def test_ac_3_existing_image_file_is_never_overwritten(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    """A file already in images/ belongs to another figure."""
    strip = load(monkeypatch)
    images = topic / "images"
    images.mkdir()
    kept = images / "gemini-image1.png"
    kept.write_bytes(JPEG)
    out = write(topic / "output-gemini.md", f"[image1]: <data:image/png;base64,{b64(PNG)}>\n")
    [written] = strip.strip_file(out)
    assert kept.read_bytes() == JPEG
    assert written != kept
    assert written.read_bytes() == PNG
    assert f"[image1]: images/{written.name}" in out.read_text(encoding="utf-8")


# AC-4: titles and braces survive the rewrite (Zorivest R1-F3).


def test_ac_4_titled_reference_definition_keeps_its_title(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    """A Markdown title after the URI does not hide the image."""
    strip = load(monkeypatch)
    out = write(
        topic / "output-gemini.md",
        f'![][image1]\n\n[image1]: <data:image/png;base64,{b64(PNG)}> "Figure 1"\n',
    )
    strip.strip_file(out)
    assert (topic / "images" / "gemini-image1.png").read_bytes() == PNG
    text = out.read_text(encoding="utf-8")
    assert "data:image" not in text
    assert '[image1]: images/gemini-image1.png "Figure 1"' in text


def test_ac_4_titled_inline_image_keeps_its_title(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    strip = load(monkeypatch)
    out = write(topic / "output-gemini.md", f'![x](data:image/png;base64,{b64(PNG)} "Figure 2")\n')
    strip.strip_file(out)
    assert (topic / "images" / "gemini-inline1.png").read_bytes() == PNG
    text = out.read_text(encoding="utf-8")
    assert "data:image" not in text
    assert '![x](images/gemini-inline1.png "Figure 2")' in text


def test_ac_4_braces_in_alt_text_and_label_survive(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    strip = load(monkeypatch)
    out = write(
        topic / "output-gemini.md",
        f"![{{x}}](data:image/png;base64,{b64(PNG)})\n\n"
        f"[{{y}}]: <data:image/png;base64,{b64(JPEG)}>\n",
    )
    written = strip.strip_file(out)
    text = out.read_text(encoding="utf-8")
    assert f"![{{x}}](images/{written[0].name})" in text
    assert f"[{{y}}]: images/{written[1].name}" in text
    assert written[1].read_bytes() == JPEG


# AC-5: a bad payload or an unhandled form fails and changes nothing (Zorivest R1-F3).


def test_ac_5_malformed_payload_leaves_everything_unchanged(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    strip = load(monkeypatch)
    good = f"[image1]: <data:image/png;base64,{b64(PNG)}>"
    bad = "[image2]: <data:image/png;base64,@@not-base64@@>"
    out = write(topic / "output-gemini.md", f"{good}\n{bad}\n")
    before = out.read_bytes()
    with pytest.raises(ValueError, match="image2"):
        strip.strip_file(out)
    assert out.read_bytes() == before
    assert not (topic / "images").exists()


@pytest.mark.parametrize(
    "bad",
    ["[image2]: <data:image/png;base64,>", "![y](data:image/png;base64,)"],
    ids=["reference", "inline"],
)
def test_ac_5_empty_payload_fails_and_changes_nothing(
    monkeypatch: pytest.MonkeyPatch, topic: Path, bad: str
) -> None:
    """An empty payload next to a good image fails before any write."""
    strip = load(monkeypatch)
    out = write(
        topic / "output-gemini.md", f"[image1]: <data:image/png;base64,{b64(PNG)}>\n{bad}\n"
    )
    before = out.read_bytes()
    with pytest.raises(ValueError):
        strip.strip_file(out)
    assert out.read_bytes() == before
    assert not (topic / "images").exists()
    assert strip.main([str(topic)]) == 1


def test_ac_5_unhandled_embedded_image_fails_and_changes_nothing(
    monkeypatch: pytest.MonkeyPatch, topic: Path
) -> None:
    """A data:image form the script does not convert is never reported clean."""
    strip = load(monkeypatch)
    out = write(
        topic / "output-gemini.md",
        f"[image1]: <data:image/png;base64,{b64(PNG)}>\n"
        f'<img alt="x" src="data:image/png;base64,{b64(PNG)}">\n',
    )
    before = out.read_bytes()
    with pytest.raises(ValueError, match="unhandled"):
        strip.strip_file(out)
    assert out.read_bytes() == before
    assert not (topic / "images").exists()


# AC-6: the command line, as a subprocess through uv run python (SKILL §6).


def test_ac_6_cli_strips_every_output_file_in_the_topic(topic: Path) -> None:
    write(topic / "output-gemini.md", f"[image1]: <data:image/png;base64,{b64(PNG)}>\n")
    write(topic / "output-chatgpt.md", f"![x](data:image/png;base64,{b64(PNG)})\n")
    write(topic / "synthesis.md", f"![x](data:image/png;base64,{b64(PNG)})\n")
    result = run(str(topic))
    assert result.returncode == 0, result.stderr
    assert (topic / "images" / "gemini-image1.png").read_bytes() == PNG
    assert (topic / "images" / "chatgpt-inline1.png").read_bytes() == PNG
    assert "data:image" not in (topic / "output-gemini.md").read_text(encoding="utf-8")
    assert "data:image" in (topic / "synthesis.md").read_text(encoding="utf-8")


def test_ac_6_cli_glob_selects_project_output_names(topic: Path) -> None:
    write(topic / "gemini-d2.md", f"[image1]: <data:image/png;base64,{b64(PNG)}>\n")
    write(topic / "prompt-d2-gemini.md", f"![x](data:image/png;base64,{b64(PNG)})\n")
    result = run(str(topic), "*-d[123].md")
    assert result.returncode == 0, result.stderr
    assert (topic / "images" / "gemini-d2-image1.png").read_bytes() == PNG
    assert "data:image" not in (topic / "gemini-d2.md").read_text(encoding="utf-8")
    assert "data:image" in (topic / "prompt-d2-gemini.md").read_text(encoding="utf-8")


def test_ac_6_cli_exit_codes(topic: Path, tmp_path: Path) -> None:
    assert run(str(tmp_path / "missing")).returncode == 2
    assert run().returncode == 2
    assert run(str(topic), "*.md", "extra").returncode == 2
    write(topic / "output-gemini.md", "[image1]: <data:image/png;base64,@@>\n")
    before = (topic / "output-gemini.md").read_bytes()
    assert run(str(topic)).returncode == 1
    assert (topic / "output-gemini.md").read_bytes() == before


def test_ac_6_cli_keeps_crlf_line_endings(topic: Path) -> None:
    """A Windows (CRLF) output keeps CRLF on every line after the rewrite."""
    out = write(
        topic / "output-gemini.md",
        f"# Report\n\n![][image1]\n\nText.\n\n[image1]: <data:image/png;base64,{b64(PNG)}>\n",
        newline="\r\n",
    )
    lines = out.read_bytes().count(b"\n")
    assert out.read_bytes().count(b"\r\n") == lines
    result = run(str(topic))
    assert result.returncode == 0, result.stderr
    data = out.read_bytes()
    assert b"data:image" not in data
    assert b"[image1]: images/gemini-image1.png\r\n" in data
    assert data.count(b"\n") == lines
    assert data.count(b"\r\n") == lines
    assert (topic / "images" / "gemini-image1.png").read_bytes() == PNG
