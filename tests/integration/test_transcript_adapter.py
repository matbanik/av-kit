"""MEU-7 transcript adapter integration tests. Mocked youtube-transcript-api only."""

from __future__ import annotations

import ast
import inspect
import re
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest

from avkit_core.domain.errors import (
    DomainError,
    NoTranscriptFoundError,
    TranscriptRetryableError,
    TranscriptsDisabledError,
)
from avkit_core.domain.transcript import TranscriptResult
from avkit_core.ports.transcript import TranscriptPort

REPO_ROOT = Path(__file__).resolve().parents[2]
INFRA_PYPROJECT = REPO_ROOT / "packages" / "infrastructure" / "pyproject.toml"
ADAPTER_PATH = (
    REPO_ROOT
    / "packages"
    / "infrastructure"
    / "src"
    / "avkit_infra"
    / "transcript"
    / "adapter.py"
)
TRANSCRIPT_PORT_METHODS = ("get_transcript",)


def _dependency_name(spec: str) -> str:
    name = spec.strip()
    for separator in ("==", ">=", "<=", "~=", "!=", ">", "<"):
        if separator in name:
            name = name.split(separator, 1)[0]
    return name.strip()


def _floor_major(spec: str) -> int:
    match = re.search(r">=\s*(\d+)", spec)
    if match is None:
        raise AssertionError(f"spec {spec!r} has no >= major floor")
    return int(match.group(1))


def _fetched(texts: list[str], language_code: str, title: str | None = None) -> SimpleNamespace:
    snippets = [SimpleNamespace(text=item) for item in texts]
    return SimpleNamespace(snippets=snippets, language_code=language_code, title=title)


class _FakeApi:
    def __init__(
        self,
        *,
        fetch_map: dict[str, object] | None = None,
        list_items: list[object] | None = None,
        fetch_error: BaseException | None = None,
        list_error: BaseException | None = None,
    ) -> None:
        self.fetch_map = fetch_map or {}
        self.list_items = list_items or []
        self.fetch_error = fetch_error
        self.list_error = list_error
        self.fetch_calls: list[list[str] | None] = []
        self.list_calls = 0

    def fetch(self, video_id: str, languages: list[str] | None = None) -> object:
        self.fetch_calls.append(languages)
        if self.fetch_error is not None:
            raise self.fetch_error
        key = languages[0] if languages else ""
        mapped = self.fetch_map.get(key)
        if isinstance(mapped, BaseException):
            raise mapped
        if mapped is not None:
            return mapped
        from youtube_transcript_api._errors import NoTranscriptFound

        raise NoTranscriptFound(video_id, languages or [], [])

    def list(self, video_id: str) -> list[object]:
        self.list_calls += 1
        if self.list_error is not None:
            raise self.list_error
        return self.list_items


@pytest.mark.integration
def test_ac_7_1_transcript_module_and_version_floor() -> None:
    from avkit_infra.transcript.adapter import TranscriptAdapter

    assert TranscriptAdapter is not None
    data = tomllib.loads(INFRA_PYPROJECT.read_text(encoding="utf-8"))
    specs = [
        str(item)
        for item in data["project"]["dependencies"]
        if _dependency_name(str(item)) == "youtube-transcript-api"
    ]
    assert specs, "youtube-transcript-api dependency missing"
    assert any(_floor_major(spec) >= 1 for spec in specs)
    naive_old = "youtube-transcript-api>=0.9"
    assert "1" not in naive_old
    assert _floor_major(naive_old) < 1


@pytest.mark.integration
def test_ac_7_2_transcript_port_signature_matches() -> None:
    from avkit_infra.transcript.adapter import TranscriptAdapter

    for name in TRANSCRIPT_PORT_METHODS:
        proto = inspect.signature(getattr(TranscriptPort, name))
        impl = inspect.signature(getattr(TranscriptAdapter, name))
        proto_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in proto.parameters.items()
        ]
        impl_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in impl.parameters.items()
        ]
        assert impl_params == proto_params, name
        assert impl.return_annotation == proto.return_annotation


@pytest.mark.integration
def test_ac_7_3_language_order_then_en_then_list(monkeypatch: pytest.MonkeyPatch) -> None:
    from youtube_transcript_api._errors import NoTranscriptFound

    from avkit_infra.transcript.adapter import TranscriptAdapter

    first = _FakeApi(
        fetch_map={
            "de": NoTranscriptFound("vid", ["de"], []),
            "fr": _fetched(["bonjour"], "fr", title="Bonjour"),
        }
    )
    monkeypatch.setattr("avkit_infra.transcript.adapter.YouTubeTranscriptApi", lambda: first)
    result = TranscriptAdapter().get_transcript("vid12345678", ["de", "fr"])
    assert result is not None
    assert result.language == "fr"
    assert first.fetch_calls == [["de"], ["fr"]]
    assert first.list_calls == 0

    listed = SimpleNamespace(
        language_code="es",
        fetch=lambda: _fetched(["hola"], "es"),
    )
    second = _FakeApi(
        fetch_map={
            "de": NoTranscriptFound("vid", ["de"], []),
            "en": NoTranscriptFound("vid", ["en"], []),
        },
        list_items=[listed],
    )
    monkeypatch.setattr("avkit_infra.transcript.adapter.YouTubeTranscriptApi", lambda: second)
    fallback = TranscriptAdapter().get_transcript("vid12345678", ["de"])
    assert fallback is not None
    assert fallback.language == "es"
    assert ["en"] in second.fetch_calls
    assert second.list_calls == 1


@pytest.mark.integration
def test_ac_7_4_disabled_missing_unavailable_return_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from youtube_transcript_api._errors import (
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    )

    from avkit_infra.transcript.adapter import TranscriptAdapter

    before = list(tmp_path.rglob("*"))
    for exc in (
        TranscriptsDisabled("vid"),
        NoTranscriptFound("vid", ["en"], []),
        VideoUnavailable("vid"),
    ):
        api = _FakeApi(fetch_error=exc)
        monkeypatch.setattr("avkit_infra.transcript.adapter.YouTubeTranscriptApi", lambda: api)
        assert TranscriptAdapter().get_transcript("vid12345678", ["en"]) is None
    after = list(tmp_path.rglob("*"))
    assert after == before
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    with pytest.raises(TranscriptsDisabledError):
        raise TranscriptsDisabledError("disabled")
    with pytest.raises(NoTranscriptFoundError):
        raise NoTranscriptFoundError("missing")
    assert "TranscriptsDisabledError" not in source
    assert "NoTranscriptFoundError" not in source


@pytest.mark.integration
def test_ac_7_5_retryable_request_and_ip_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    from youtube_transcript_api._errors import IpBlocked, RequestBlocked

    from avkit_infra.transcript.adapter import TranscriptAdapter

    blocked = RequestBlocked("vid")
    api = _FakeApi(fetch_error=blocked)
    monkeypatch.setattr("avkit_infra.transcript.adapter.YouTubeTranscriptApi", lambda: api)
    with pytest.raises(TranscriptRetryableError) as err:
        TranscriptAdapter().get_transcript("vid12345678", ["en"])
    assert err.value.__cause__ is blocked

    ip_blocked = IpBlocked("vid")
    api = _FakeApi(fetch_error=ip_blocked)
    monkeypatch.setattr("avkit_infra.transcript.adapter.YouTubeTranscriptApi", lambda: api)
    with pytest.raises(TranscriptRetryableError) as ip_err:
        TranscriptAdapter().get_transcript("vid12345678", ["en"])
    assert ip_err.value.__cause__ is ip_blocked
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "TooManyRequests" not in source


@pytest.mark.integration
def test_ac_7_6_join_newlines_language_and_title_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from avkit_infra.transcript.adapter import TranscriptAdapter

    api = _FakeApi(
        fetch_map={"en": _fetched(["hello", "world"], "en", title=None)},
    )
    monkeypatch.setattr("avkit_infra.transcript.adapter.YouTubeTranscriptApi", lambda: api)
    result = TranscriptAdapter().get_transcript("vid12345678", ["en"])
    assert result == TranscriptResult(
        video_id="vid12345678",
        title="vid12345678",
        text="hello\nworld",
        language="en",
    )
    titled = _FakeApi(fetch_map={"en": _fetched(["only"], "en", title="Named")})
    monkeypatch.setattr("avkit_infra.transcript.adapter.YouTubeTranscriptApi", lambda: titled)
    named = TranscriptAdapter().get_transcript("vid12345678", ["en"])
    assert named is not None
    assert named.title == "Named"


@pytest.mark.integration
def test_ac_7_7_no_sleep_and_unrecognized_domain_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from avkit_infra.transcript.adapter import TranscriptAdapter

    def _boom(*args: object, **kwargs: object) -> None:
        raise AssertionError("adapter must not sleep")

    monkeypatch.setattr("time.sleep", _boom)
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "sleep" not in source
    unexpected = RuntimeError("nope")
    api = _FakeApi(fetch_error=unexpected)
    monkeypatch.setattr("avkit_infra.transcript.adapter.YouTubeTranscriptApi", lambda: api)
    with pytest.raises(DomainError) as err:
        TranscriptAdapter().get_transcript("vid12345678", ["en"])
    assert type(err.value) is DomainError
    assert err.value.__cause__ is unexpected


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".", 1)[0])
    return names


def _import_hits_outside(root: Path, module: str, allow: str | None) -> list[str]:
    hits: list[str] = []
    for path in root.rglob("*.py"):
        if module not in _top_level_imports(path):
            continue
        rel = path.relative_to(root)
        if allow is not None and allow in rel.parts:
            continue
        hits.append(str(rel).replace("\\", "/"))
    return hits


@pytest.mark.integration
def test_ac_7_8_no_uow_and_library_confined_to_transcript() -> None:
    from avkit_infra.transcript.adapter import TranscriptAdapter

    assert TranscriptAdapter is not None
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "SqlAlchemyUnitOfWork" not in source
    assert "avkit_infra.database" not in source
    infra_src = REPO_ROOT / "packages" / "infrastructure" / "src"
    core_src = REPO_ROOT / "packages" / "core" / "src"
    assert _import_hits_outside(infra_src, "youtube_transcript_api", "transcript") == []
    assert _import_hits_outside(core_src, "youtube_transcript_api", None) == []
