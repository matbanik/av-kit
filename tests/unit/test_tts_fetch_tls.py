"""rc.3 F1: the spaCy wheel fetch trusts certifi's roots, not only the Windows store's.

A fresh Windows install holds few roots and adds the rest lazily, which Python's default
context never triggers, so github.com and its release-asset host failed verification.
"""

from __future__ import annotations

import io
import ssl
from pathlib import Path
from typing import Any

import certifi
import pytest

from avkit_infra.tts import assets as assets_mod


class _Response(io.BytesIO):
    headers: dict[str, str] = {"Content-Length": "3"}

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def _issuers(context: ssl.SSLContext) -> set[str]:
    names: set[str] = set()
    for cert in context.get_ca_certs():
        for rdn in cert.get("subject", ()):
            for key, value in rdn:
                if key == "commonName":
                    names.add(str(value))
    return names


def test_default_fetch_verifies_against_certifi(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen: dict[str, Any] = {}

    def fake_urlopen(url: str, *args: object, **kwargs: object) -> _Response:
        seen["url"] = url
        seen["kwargs"] = kwargs
        return _Response(b"abc")

    real_factory = ssl.create_default_context
    built: list[tuple[dict[str, object], ssl.SSLContext]] = []

    def spy_factory(*args: Any, **kwargs: Any) -> ssl.SSLContext:
        made = real_factory(*args, **kwargs)
        built.append((dict(kwargs), made))
        return made

    monkeypatch.setattr(assets_mod.urllib.request, "urlopen", fake_urlopen)
    # This host's own store may hold both roots, so the roots alone can't tell certifi's
    # bundle from the system trust; the factory call can (rc.3 review R1-F1).
    monkeypatch.setattr(assets_mod.ssl, "create_default_context", spy_factory)
    progress: list[float] = []
    dest = tmp_path / "wheel.whl"
    assets_mod._default_fetch("https://example.invalid/w.whl", dest, progress.append)

    assert dest.read_bytes() == b"abc"
    assert progress[-1] == 1.0
    context = seen["kwargs"].get("context")
    assert isinstance(context, ssl.SSLContext)
    assert [(kwargs.get("cafile"), made) for kwargs, made in built] == [(certifi.where(), context)]
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
    issuers = _issuers(context)
    assert "ISRG Root X1" in issuers
    assert "USERTrust ECC Certification Authority" in issuers
