"""MEU-62 TTS runtime assets (AC-62.1–62.11, 62.14, 62.16).

Call chains start at the production composition root (`avkit_api.wiring.build_services` →
`avkit_api.main.create_app`) and go through the real routes, services and adapters. Only
the engines (Kokoro `KModel` / `KPipeline`, onnxruntime `InferenceSession`), the Hugging
Face download and the spaCy wheel fetch are faked: no network, no model weights.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import threading
import time
import zipfile
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from fastapi.testclient import TestClient
from tests.integration.test_tts_models import FakeKModel, FakeSession, _patch_engines
from tests.tts_g2p_fakes import PACK_BYTES, g2p_lang_codes, write_voice_packs

TOKEN = "s27-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}
VOCAB = {"vocab": {"a": 1, "b": 2}, "n_token": 3}


# --- fixtures ---------------------------------------------------------------------------


def _fake_wheel(*, member_prefix: str = "", extra: dict[str, bytes] | None = None) -> bytes:
    """Build a minimal importable `en_core_web_sm` wheel (package + dist-info)."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr(f"{member_prefix}en_core_web_sm/__init__.py", "MARK = 'fake'\n")
        zf.writestr(
            f"{member_prefix}en_core_web_sm-3.8.0.dist-info/METADATA",
            "Metadata-Version: 2.1\nName: en_core_web_sm\nVersion: 3.8.0\n",
        )
        zf.writestr(f"{member_prefix}en_core_web_sm-3.8.0.dist-info/RECORD", "")
        for name, data in (extra or {}).items():
            zf.writestr(name, data)
    return buffer.getvalue()


class WheelServer:
    """Stands in for the GitHub release download; records every fetch."""

    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.calls: list[str] = []
        self.hold: threading.Event | None = None

    def fetch(self, url: str, dest: Path, on_progress: Callable[[float], None]) -> None:
        self.calls.append(url)
        if self.hold is not None:
            self.hold.wait(timeout=5)
        on_progress(0.5)
        dest.write_bytes(self.payload)
        on_progress(1.0)


class HubServer:
    """Stands in for `hf_hub_download`; records every requested filename."""

    def __init__(self, vocab: object = VOCAB) -> None:
        self.vocab = vocab
        self.calls: list[dict[str, Any]] = []

    def __call__(self, **kwargs: Any) -> str:
        self.calls.append(kwargs)
        local = Path(kwargs["local_dir"]) / kwargs["filename"]
        local.parent.mkdir(parents=True, exist_ok=True)
        if kwargs["filename"] == "config.json":
            local.write_text(json.dumps(self.vocab), encoding="utf-8")
        else:
            local.write_bytes(b"weights")
        return str(local)


class PackServer:
    """Stands in for the voice-pack `hf_hub_download`; writes a full-size pack per call."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def __call__(self, **kwargs: Any) -> str:
        self.calls.append(kwargs)
        local = Path(kwargs["local_dir"]) / kwargs["filename"]
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(b"\0" * PACK_BYTES)
        return str(local)


@pytest.fixture(autouse=True)
def isolated_home(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Point `~` at an empty dir (HOME on POSIX, USERPROFILE on Windows).

    `build_services` activates the configured models directory at startup, and the default is
    `~/.avkit/models`, read before a test can set its own. A real user install there (a spaCy
    model from an interactive app session) would otherwise leak onto the process-wide sys.path
    and make every later test see spaCy as ready (Session 27 WINDOWS_GATE attempt 3).
    """
    home = tmp_path_factory.mktemp("home")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))


@pytest.fixture
def isolated_path(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Restore sys.path / sys.modules after tests that activate a spaCy install dir."""
    monkeypatch.setattr(sys, "path", list(sys.path))
    before = set(sys.modules)
    yield
    for name in set(sys.modules) - before:
        if name.startswith("en_core_web_sm"):
            del sys.modules[name]


class Stack:
    def __init__(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, wheel: bytes | None = None
    ) -> None:
        from avkit_api.main import create_app
        from avkit_api.wiring import build_services

        _patch_engines(monkeypatch)
        self.hub = HubServer()
        monkeypatch.setattr("avkit_infra.model_manager.manager.hf_hub_download", self.hub)
        payload = wheel if wheel is not None else _fake_wheel()
        self.wheel = WheelServer(payload)
        try:
            from avkit_infra.model_manager import vocab as vocab_mod
            from avkit_infra.tts import assets as assets_mod
        except ImportError:
            # Red stage: the MEU-62 modules do not exist yet, so the stack runs against the
            # current code and each test fails on its own assertion instead of on setup.
            assets_mod = None
            vocab_mod = None
        if vocab_mod is not None:
            monkeypatch.setattr(vocab_mod, "hf_hub_download", self.hub)
        self.packs = PackServer()
        try:
            from avkit_infra.model_manager import voice_packs as packs_mod
        except ImportError:
            packs_mod = None  # Red stage for MEU-73: the voice-pack module does not exist yet.
        if packs_mod is not None:
            monkeypatch.setattr(packs_mod, "hf_hub_download", self.packs)
        if assets_mod is not None:
            pin = assets_mod.WheelPin(
                name="en_core_web_sm",
                version="3.8.0",
                url="https://example.invalid/en_core_web_sm-3.8.0-py3-none-any.whl",
                sha256=hashlib.sha256(payload).hexdigest(),
            )
            monkeypatch.setattr(assets_mod, "SPACY_MODEL_PIN", {"3.8": pin})
            monkeypatch.setattr(assets_mod, "_default_fetch", self.wheel.fetch)
        self.models_dir = tmp_path / "models"
        self.out_dir = tmp_path / "out"
        self.db_path = tmp_path / "avkit.db"
        self.services, self.dispose = build_services(app_data=tmp_path, database_path=self.db_path)
        settings: Any = self.services.settings
        settings.set("tts", "models_directory", str(self.models_dir))
        settings.set("tts", "output_path", str(self.out_dir))
        app = create_app(
            tokens=frozenset({TOKEN}), services=self.services, engine_dispose=self.dispose
        )
        self.client = TestClient(app)

    def wait_idle(self, timeout: float = 5.0) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while True:
            body = self.client.get("/api/v1/models/download-runtime", headers=AUTH).json()
            if body["state"] != "Downloading" or time.monotonic() > deadline:
                return body
            time.sleep(0.02)

    def put_weights(self, variant_id: str) -> Path:
        try:
            from avkit_infra.tts.voices import variant_local_path
        except ImportError:  # Red stage for MEU-73
            from avkit_infra.model_manager.catalog import HF_FILE_MAP

            path = self.models_dir / HF_FILE_MAP[variant_id][1]
        else:
            path = variant_local_path(variant_id, self.models_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"weights")
        # Setup: record the weights the way a finished download does (load reads the row).
        with self.services.models._uow_factory() as uow:  # type: ignore[attr-defined]
            uow.models.mark_downloaded(variant_id, path)
            uow.commit()
        return path

    def put_vocab(self, payload: object = VOCAB) -> Path:
        path = self.models_dir / "config.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def deps(self) -> dict[str, Any]:
        response = self.client.get("/api/v1/health/dependencies", headers=AUTH)
        assert response.status_code == 200
        return response.json()


@pytest.fixture
def stack(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, isolated_path: None) -> Iterator[Stack]:
    built = Stack(tmp_path, monkeypatch)
    try:
        yield built
    finally:
        built.client.close()
        built.dispose()


def _generate(stack: Stack, voice: str = "am_eric", steps: list[str] | None = None) -> Any:
    # FIXTURE_REPAIRS (f) (Session 33, MEU-77): let the background worker finish.
    response = _post_generate(stack, voice, steps)
    stack.services.tts.wait_idle(5.0)  # type: ignore[attr-defined]
    return response


def _post_generate(stack: Stack, voice: str = "am_eric", steps: list[str] | None = None) -> Any:
    """POST /tts/generate without waiting; for tests that hold the worker."""
    return stack.client.post(
        "/api/v1/tts/generate",
        headers=AUTH,
        json={
            "text": "Hello there.",
            "voice": voice,
            "speed": 1.0,
            "format": "WAV",
            "enabled_steps": ["whitespace"] if steps is None else steps,
            "source_kind": "inline",
        },
    )


def _tts_rows(stack: Stack) -> list[tuple[str, str | None]]:
    """(status, error_message) of every persisted TTS job, oldest first."""
    import sqlite3

    with sqlite3.connect(stack.db_path) as conn:
        return list(conn.execute("SELECT status, error_message FROM tts_jobs ORDER BY created_at"))


def _install_spacy(stack: Stack) -> None:
    response = stack.client.post(
        "/api/v1/models/download", headers=AUTH, json={"asset": "tts_spacy_model"}
    )
    assert response.status_code == 202, response.text
    assert stack.wait_idle()["state"] == "Idle"


# --- AC-62.1 ------------------------------------------------------------------------------


def test_ac_62_1_required_assets_rule_and_closed_enums() -> None:
    from avkit_core.domain.enums import ModelFormat
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.tts import (
        KOKORO_LANG_CODES,
        SPACY_LANG_CODES,
        SPACY_STEPS,
        AssetState,
        TtsAsset,
        required_tts_assets,
    )
    from avkit_infra.tts.voices import LANG_BY_PREFIX

    assert [a.value for a in TtsAsset] == ["tts_onnx_vocab", "tts_spacy_model", "tts_voice_packs"]
    assert {s.value for s in AssetState} == {"ready", "missing", "downloading"}
    assert SPACY_LANG_CODES == frozenset({"a", "b"})
    assert SPACY_STEPS == frozenset({"chunk"})
    assert KOKORO_LANG_CODES == frozenset(LANG_BY_PREFIX)
    both = (TtsAsset.ONNX_VOCAB, TtsAsset.SPACY_MODEL, TtsAsset.VOICE_PACKS)
    for fmt in ModelFormat:
        assert required_tts_assets(fmt, "am_eric", []) == both
        assert required_tts_assets(fmt, "bf_emma", ["whitespace"]) == both
        for voice in ("jf_alpha", "zf_xiaobei", "ef_dora"):
            no_spacy = (TtsAsset.ONNX_VOCAB, TtsAsset.VOICE_PACKS)
            assert required_tts_assets(fmt, voice, ["whitespace"]) == no_spacy
            assert required_tts_assets(fmt, voice, ["whitespace", "chunk"]) == both
    with pytest.raises(ValidationError):
        required_tts_assets(ModelFormat.ONNX, "xf_nobody", [])


# --- AC-62.2 / 62.3 -----------------------------------------------------------------------


def test_ac_62_2_variant_download_fetches_vocab_even_when_weights_exist(stack: Stack) -> None:
    stack.put_weights("kokoro-onnx-int8")
    response = stack.client.post(
        "/api/v1/models/download", headers=AUTH, json={"variant_id": "kokoro-onnx-int8"}
    )
    assert response.status_code == 202, response.text
    assert stack.wait_idle()["state"] == "Idle"
    assert [call["filename"] for call in stack.hub.calls] == ["config.json"]
    assert stack.hub.calls[0]["repo_id"] == "hexgrad/Kokoro-82M"
    assert (
        json.loads((stack.models_dir / "config.json").read_text(encoding="utf-8"))["vocab"]
        == VOCAB["vocab"]
    )


def test_ac_62_2_invalid_vocab_fails_and_is_removed(stack: Stack) -> None:
    stack.hub.vocab = {"not_vocab": 1}
    stack.put_weights("kokoro-onnx-int8")
    stack.client.post(
        "/api/v1/models/download", headers=AUTH, json={"variant_id": "kokoro-onnx-int8"}
    )
    runtime = stack.wait_idle()
    assert runtime["state"] == "Failed"
    assert runtime["error_message"]
    assert not (stack.models_dir / "config.json").exists()


def test_ac_62_3_variant_needs_weights_and_vocab_to_be_downloaded(stack: Stack) -> None:
    stack.put_weights("kokoro-onnx-int8")

    def downloaded() -> bool:
        items = stack.client.get("/api/v1/models/available", headers=AUTH).json()["items"]
        return next(item for item in items if item["id"] == "kokoro-onnx-int8")["is_downloaded"]

    assert downloaded() is False
    stack.put_vocab()
    assert downloaded() is True


# --- AC-62.4 / 62.5 -----------------------------------------------------------------------


def test_ac_62_4_load_refuses_without_vocab(stack: Stack) -> None:
    stack.put_weights("kokoro-onnx-int8")
    response = stack.client.post(
        "/api/v1/models/load",
        headers=AUTH,
        json={"variant_id": "kokoro-onnx-int8", "device": "cpu"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ConflictError"
    assert "tts_onnx_vocab" in response.json()["error"]["message"]
    assert FakeSession.calls == []
    assert stack.client.get("/api/v1/models/status", headers=AUTH).json()["is_loaded"] is False


def test_ac_62_5_pytorch_load_passes_local_config_and_onnx_reads_resolver(
    stack: Stack, tmp_path: Path
) -> None:
    from avkit_core.domain.tts import VoiceConfig

    stack.put_weights("kokoro-pt-fp32")
    vocab = stack.put_vocab()
    _install_spacy(stack)
    response = stack.client.post(
        "/api/v1/models/load", headers=AUTH, json={"variant_id": "kokoro-pt-fp32", "device": "cpu"}
    )
    assert response.status_code == 200, response.text
    kwargs = FakeKModel.calls[-1]["kwargs"]
    assert kwargs["config"] == str(vocab)
    assert kwargs["repo_id"] == "hexgrad/Kokoro-82M"
    assert all(call["filename"] != "config.json" for call in stack.hub.calls)

    # The resolver is evaluated per call: a new models_directory is honoured by the next chunk.
    adapter: Any = stack.services.tts._tts  # type: ignore[attr-defined]
    stack.put_weights("kokoro-onnx-int8")
    stack.client.post(
        "/api/v1/models/load",
        headers=AUTH,
        json={"variant_id": "kokoro-onnx-int8", "device": "cpu"},
    )
    moved = tmp_path / "moved"
    moved.mkdir()
    (moved / "config.json").write_text(json.dumps({"vocab": {"a": 7, "b": 8}}), encoding="utf-8")
    write_voice_packs(moved, ["af_heart"])
    stack.services.settings.set("tts", "models_directory", str(moved))  # type: ignore[attr-defined]
    voice = VoiceConfig(
        voice_id="af_heart",
        lang_code="a",
        language="American English",
        gender="Female",
        style_description="heart",
    )
    adapter.generate("hi", voice, 1.0, lambda _f: None)
    assert FakeSession.runs[-1]["input_ids"].tolist() == [[0, 7, 8, 0]]


# --- AC-62.6 ------------------------------------------------------------------------------


def test_ac_62_6_spacy_download_installs_pinned_wheel(stack: Stack) -> None:
    import spacy.util

    assert stack.deps().get("tts_spacy_model", {}).get("state") == "missing"
    stack.wheel.hold = threading.Event()
    response = stack.client.post(
        "/api/v1/models/download", headers=AUTH, json={"asset": "tts_spacy_model"}
    )
    assert response.status_code == 202
    running = stack.client.get("/api/v1/models/download-runtime", headers=AUTH).json()
    assert running["asset"] == "tts_spacy_model"
    assert running["variant_id"] is None
    assert running["state"] == "Downloading"
    assert stack.deps().get("tts_spacy_model", {}).get("state") == "downloading"
    stack.wheel.hold.set()
    assert stack.wait_idle()["state"] == "Idle"
    assert stack.wheel.calls == ["https://example.invalid/en_core_web_sm-3.8.0-py3-none-any.whl"]
    install = stack.models_dir / "spacy" / "en_core_web_sm-3.8.0"
    assert (install / "en_core_web_sm" / "__init__.py").is_file()
    assert spacy.util.is_package("en_core_web_sm")
    row = stack.deps().get("tts_spacy_model")
    assert row == {"available": True, "version": "3.8.0", "state": "ready"}


def test_ac_62_6_sha_mismatch_unpinned_and_zip_slip_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, isolated_path: None
) -> None:
    from avkit_infra.tts import assets as assets_mod

    # (a) sha256 mismatch
    s = Stack(tmp_path / "a", monkeypatch)
    try:
        pin = assets_mod.SPACY_MODEL_PIN["3.8"]
        monkeypatch.setattr(
            assets_mod,
            "SPACY_MODEL_PIN",
            {
                "3.8": assets_mod.WheelPin(
                    name=pin.name, version=pin.version, url=pin.url, sha256="0" * 64
                )
            },
        )
        s.client.post("/api/v1/models/download", headers=AUTH, json={"asset": "tts_spacy_model"})
        runtime = s.wait_idle()
        assert runtime["state"] == "Failed"
        assert "sha256" in runtime["error_message"]
        assert not (s.models_dir / "spacy" / "en_core_web_sm-3.8.0").exists()
        # (b) unpinned spaCy minor: nothing is fetched
        s.wheel.calls.clear()
        monkeypatch.setattr(assets_mod, "_installed_spacy_minor", lambda: "3.9")
        s.client.post("/api/v1/models/download", headers=AUTH, json={"asset": "tts_spacy_model"})
        runtime = s.wait_idle()
        assert runtime["state"] == "Failed"
        assert runtime["error_message"] == "no pinned en_core_web_sm for spaCy 3.9"
        assert s.wheel.calls == []
    finally:
        s.client.close()
        s.dispose()

    # (c) zip-slip member
    evil = _fake_wheel(extra={"../evil.py": b"x = 1\n"})
    s = Stack(tmp_path / "c", monkeypatch, wheel=evil)
    try:
        s.client.post("/api/v1/models/download", headers=AUTH, json={"asset": "tts_spacy_model"})
        runtime = s.wait_idle()
        assert runtime["state"] == "Failed"
        assert not (tmp_path / "c" / "models" / "evil.py").exists()
        assert not (tmp_path / "c" / "models" / "spacy" / "evil.py").exists()
        spacy_dir = s.models_dir / "spacy"
        leftovers = [p.name for p in spacy_dir.iterdir()] if spacy_dir.exists() else []
        assert leftovers == []
    finally:
        s.client.close()
        s.dispose()


def test_ac_62_6_existing_install_ready_is_409_and_stale_is_replaced(stack: Stack) -> None:
    _install_spacy(stack)
    stack.wheel.calls.clear()
    again = stack.client.post(
        "/api/v1/models/download", headers=AUTH, json={"asset": "tts_spacy_model"}
    )
    assert again.status_code == 409
    assert stack.wheel.calls == []

    # Corrupt install (dist-info kept, package dir gone) reads missing; a re-download fixes it.
    install = stack.models_dir / "spacy" / "en_core_web_sm-3.8.0"
    for child in (install / "en_core_web_sm").iterdir():
        child.unlink()
    (install / "en_core_web_sm").rmdir()
    for name in list(sys.modules):
        if name.startswith("en_core_web_sm"):
            del sys.modules[name]
    assert stack.deps().get("tts_spacy_model", {}).get("state") == "missing"
    _install_spacy(stack)
    assert stack.deps().get("tts_spacy_model", {}).get("state") == "ready"
    assert (install / "en_core_web_sm" / "__init__.py").is_file()


# --- AC-62.7 ------------------------------------------------------------------------------


def test_ac_62_7_load_starts_spacy_download_unless_busy(stack: Stack) -> None:
    stack.put_weights("kokoro-onnx-int8")
    stack.put_vocab()
    stack.wheel.hold = threading.Event()
    loaded = stack.client.post(
        "/api/v1/models/load",
        headers=AUTH,
        json={"variant_id": "kokoro-onnx-int8", "device": "cpu"},
    )
    assert loaded.status_code == 200
    runtime = stack.client.get("/api/v1/models/download-runtime", headers=AUTH).json()
    assert runtime["state"] == "Downloading"
    assert runtime["asset"] == "tts_spacy_model"
    stack.wheel.hold.set()
    assert stack.wait_idle()["state"] == "Idle"
    assert stack.deps().get("tts_spacy_model", {}).get("state") == "ready"


def test_ac_62_7_load_defers_spacy_while_variant_download_runs(stack: Stack) -> None:
    stack.put_weights("kokoro-onnx-int8")
    stack.put_vocab()
    gate = threading.Event()
    original = stack.hub

    def slow(**kwargs: Any) -> str:
        gate.wait(timeout=5)
        return original(**kwargs)

    import avkit_infra.model_manager.manager as manager

    manager.hf_hub_download = slow  # type: ignore[assignment]
    try:
        started = stack.client.post(
            "/api/v1/models/download", headers=AUTH, json={"variant_id": "kokoro-pt-fp32"}
        )
        assert started.status_code == 202
        stack.client.post(
            "/api/v1/models/load",
            headers=AUTH,
            json={"variant_id": "kokoro-onnx-int8", "device": "cpu"},
        )
        runtime = stack.client.get("/api/v1/models/download-runtime", headers=AUTH).json()
        assert runtime["variant_id"] == "kokoro-pt-fp32"
        assert runtime["asset"] is None
        assert stack.wheel.calls == []
    finally:
        gate.set()
        stack.wait_idle()
        manager.hf_hub_download = original  # type: ignore[assignment]


# --- AC-62.8 ------------------------------------------------------------------------------


def test_ac_62_8_dependency_rows_are_independent(stack: Stack) -> None:
    fresh = stack.deps()
    assert fresh.get("tts_onnx_vocab") == {"available": False, "version": None, "state": "missing"}
    assert fresh.get("tts_spacy_model") == {"available": False, "version": None, "state": "missing"}
    assert set(fresh) >= {"yt_dlp", "ffmpeg"}
    stack.wheel.hold = threading.Event()
    stack.client.post("/api/v1/models/download", headers=AUTH, json={"asset": "tts_spacy_model"})
    busy = stack.deps()
    assert busy.get("tts_spacy_model", {}).get("state") == "downloading"
    assert busy.get("tts_onnx_vocab", {}).get("state") == "missing"
    stack.wheel.hold.set()
    stack.wait_idle()
    stack.put_vocab()
    assert stack.deps().get("tts_onnx_vocab") == {
        "available": True,
        "version": None,
        "state": "ready",
    }


# --- AC-62.9 ------------------------------------------------------------------------------


def _load_ready_variant(stack: Stack, *, spacy: bool) -> None:
    stack.put_weights("kokoro-onnx-int8")
    stack.put_vocab()
    write_voice_packs(stack.models_dir)
    if spacy:
        _install_spacy(stack)
    else:
        stack.wheel.hold = threading.Event()  # keep the auto-trigger from completing
    loaded = stack.client.post(
        "/api/v1/models/load",
        headers=AUTH,
        json={"variant_id": "kokoro-onnx-int8", "device": "cpu"},
    )
    assert loaded.status_code == 200, loaded.text


def test_ac_62_9_generate_fails_fast_on_missing_spacy(
    stack: Stack, monkeypatch: pytest.MonkeyPatch
) -> None:
    import spacy.cli

    from avkit_core.domain.tts import EspeakStatus
    from avkit_infra.tts.espeak import EspeakCliAdapter

    cli_calls: list[object] = []
    monkeypatch.setattr(spacy.cli, "download", lambda *a, **k: cli_calls.append(a))
    # TA-9 (MEU-74): report eSpeak NG present, so `ef_dora` passes `VOICE_AVAILABLE_409`.
    present = EspeakStatus(available=True, version="1.52.0", path=Path("espeak-ng.exe"))
    monkeypatch.setattr(EspeakCliAdapter, "status", lambda self: present)
    _load_ready_variant(stack, spacy=False)
    # TA-3b (MEU-72): count requests on the G2P_SEAM fake, not KPipeline constructions.
    g2p_before = len(g2p_lang_codes())
    try:
        response = _generate(stack, "am_eric", ["whitespace"])
        assert response.status_code == 409
        assert response.json()["error"]["message"] == "tts asset missing: tts_spacy_model"
        default_gui = _generate(stack, "ef_dora", ["whitespace", "chunk"])
        assert default_gui.status_code == 409
        assert "tts_spacy_model" in default_gui.json()["error"]["message"]
        assert _tts_rows(stack) == []
        assert not stack.out_dir.exists() or list(stack.out_dir.iterdir()) == []
        assert len(g2p_lang_codes()) == g2p_before
        assert cli_calls == []
        # No spaCy needed: a Spanish voice without the chunk step passes the asset check.
        passed = _generate(stack, "ef_dora", ["whitespace"])
        assert passed.status_code == 201, passed.text
    finally:
        assert stack.wheel.hold is not None
        stack.wheel.hold.set()
        stack.wait_idle()


# --- AC-62.10 / 62.11 ---------------------------------------------------------------------


def test_ac_62_10_generate_events_and_console_fields(stack: Stack) -> None:
    from structlog.testing import capture_logs

    _load_ready_variant(stack, spacy=True)
    with capture_logs() as logs:
        ok = _generate(stack)
    assert ok.status_code == 201, ok.text
    events = [entry["event"] for entry in logs]
    started = next(e for e in logs if e["event"] == "tts.generate")
    assert {"job_id", "voice", "variant"} <= set(started)
    assert started["variant"] == "kokoro-onnx-int8"
    done = next(e for e in logs if e["event"] == "tts.generate_done")
    assert {"job_id", "output"} <= set(done)
    assert "tts.generate_failed" not in events

    session: Any = stack.services.tts._tts._session  # type: ignore[attr-defined]
    session.run = _session_boom
    # Session 33 (MEU-77) made generate asynchronous: the POST is accepted and the
    # session failure lands on the persisted job instead of the response.
    failed = _generate(stack)
    assert failed.status_code == 201, failed.text
    job_id = failed.json()["id"]
    assert _tts_rows(stack)[-1] == ("Failed", "RuntimeError: session boom")
    health: Any = stack.services.health
    messages = [event.message for event in health.console_snapshot(0)]
    line = next(m for m in messages if m.startswith("tts.generate_failed"))
    assert f"job_id={job_id}" in line
    assert "error=RuntimeError: session boom" in line
    import structlog

    structlog.get_logger(module="tts").warning(
        "tts.generate_failed", job_id="j1", error="Bearer abc123"
    )
    redacted = health.console_snapshot(0)[-1].message
    assert "abc123" not in redacted and "[REDACTED]" in redacted


def _session_boom(*_args: object, **_kwargs: object) -> list[np.ndarray]:
    raise RuntimeError("session boom")


def test_ac_62_11_every_failed_job_has_error_message(
    stack: Stack, monkeypatch: pytest.MonkeyPatch
) -> None:
    _load_ready_variant(stack, spacy=True)
    adapter: Any = stack.services.tts._tts  # type: ignore[attr-defined]

    def boom(*_a: object, **_k: object) -> np.ndarray:
        raise RuntimeError("hf 503")

    monkeypatch.setattr(adapter, "generate", boom)
    client = TestClient(stack.client.app, raise_server_exceptions=False)
    response = _generate_with(client)
    # TA-9 (Session 33, MEU-77): the job is accepted; the worker records the failure.
    assert response.status_code == 201
    assert _tts_rows(stack) == [("Failed", "RuntimeError: hf 503")]
    monkeypatch.setattr(
        adapter, "generate", lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError())
    )
    second = _generate_with(client)
    # TA-9 (Session 33, MEU-77): accepted, not a 409 overlap: _current_id was reset.
    assert second.status_code == 201
    assert _tts_rows(stack)[-1] == ("Failed", "RuntimeError")


def _generate_with(client: TestClient) -> Any:
    response = client.post(
        "/api/v1/tts/generate",
        headers=AUTH,
        json={
            "text": "Hello.",
            "voice": "am_eric",
            "speed": 1.0,
            "format": "WAV",
            "enabled_steps": ["whitespace"],
            "source_kind": "inline",
        },
    )
    # FIXTURE_REPAIRS (f) (Session 33, MEU-77): let the background worker finish.
    client.app.state.services.tts.wait_idle(5.0)  # type: ignore[attr-defined]
    return response


# --- AC-62.14 / 62.16 ---------------------------------------------------------------------


def test_ac_62_14_startup_activation_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, isolated_path: None
) -> None:
    import spacy.util

    from avkit_infra.tts.assets import activate_spacy_dir

    models = tmp_path / "models"
    before = list(sys.path)
    activate_spacy_dir(models)
    assert sys.path == before
    install = models / "spacy" / "en_core_web_sm-3.8.0"
    with zipfile.ZipFile(io.BytesIO(_fake_wheel())) as zf:
        zf.extractall(install)
    activate_spacy_dir(models)
    activate_spacy_dir(models)
    assert sys.path.count(str(install)) == 1
    assert spacy.util.is_package("en_core_web_sm")

    # build_services activates an existing install from the configured models directory.
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != str(install)])
    from avkit_api.wiring import build_services

    services, dispose = build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")
    try:
        services.settings.set("tts", "models_directory", str(models))  # type: ignore[attr-defined]
    finally:
        dispose()
    services, dispose = build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")
    try:
        assert sys.path.count(str(install)) == 1
    finally:
        dispose()


def test_ac_73_12_activation_appends_the_install_dir(tmp_path: Path, isolated_path: None) -> None:
    from avkit_infra.tts.assets import activate_spacy_dir

    models = tmp_path / "models"
    install = models / "spacy" / "en_core_web_sm-3.8.0"
    with zipfile.ZipFile(io.BytesIO(_fake_wheel())) as zf:
        zf.extractall(install)
    before = [entry for entry in sys.path if entry != str(install)]
    sys.path[:] = before
    activate_spacy_dir(models)
    assert sys.path[-1] == str(install), "the install dir must not shadow site-packages"
    assert sys.path[:-1] == before
    activate_spacy_dir(models)
    assert sys.path == [*before, str(install)]


def test_ac_62_16_onnx_generate_with_vocab_yields_samples(stack: Stack) -> None:
    _load_ready_variant(stack, spacy=True)
    response = _generate(stack)
    assert response.status_code == 201, response.text
    # TA-10 (Session 33, MEU-77): the finished job is read back with GET.
    body = stack.client.get(f"/api/v1/tts/{response.json()['id']}", headers=AUTH).json()
    assert body["status"] == "Done"
    assert body["error_message"] is None
    assert body["output_path"]
    assert FakeSession.runs, "ONNX session never ran"


def test_ac_62_16_model_overshoot_is_clipped_not_failed(
    stack: Stack, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Found by the real-network tts-live-pre run: Kokoro output peaks slightly past ±1.0,
    # which the WAV writer's AC-8.4 contract rejects. Clip, like the reference 16-bit PCM write.
    import wave

    monkeypatch.setattr(FakeSession, "audio", np.array([[1.3, -1.2, 0.5]], dtype=np.float32))
    _load_ready_variant(stack, spacy=True)
    response = _generate(stack)
    assert response.status_code == 201, response.text
    # TA-10 (Session 33, MEU-77): the finished job is read back with GET.
    body = stack.client.get(f"/api/v1/tts/{response.json()['id']}", headers=AUTH).json()
    assert body["status"] == "Done", body
    assert body["error_message"] is None
    with wave.open(str(body["output_path"]), "rb") as handle:
        decoded = np.frombuffer(handle.readframes(handle.getnframes()), dtype="<i2")
    assert decoded.tolist() == [32767, -32768, 16384]


# --- AC-62.12 -----------------------------------------------------------------------------


def test_ac_62_12_download_body_is_exactly_one_target(stack: Stack) -> None:
    bad_bodies: list[dict[str, object]] = [
        {},
        {"variant_id": "kokoro-onnx-int8", "asset": "tts_spacy_model"},
        {"asset": "tts_bogus"},
        {"asset": "tts_spacy_model", "x": 1},
        {"variant_id": ""},
    ]
    for body in bad_bodies:
        response = stack.client.post("/api/v1/models/download", headers=AUTH, json=body)
        assert response.status_code == 422, body
        assert response.json()["error"]["code"]
    runtime = stack.client.get("/api/v1/models/download-runtime", headers=AUTH).json()
    assert runtime == {
        "variant_id": None,
        "asset": None,
        "state": "Idle",
        "fraction": 0.0,
        "error_message": None,
    }
    assert stack.hub.calls == []
    assert stack.wheel.calls == []

    stack.wheel.hold = threading.Event()
    first = stack.client.post(
        "/api/v1/models/download", headers=AUTH, json={"asset": "tts_spacy_model"}
    )
    assert first.status_code == 202
    assert first.json() == {"variant": None, "asset": "tts_spacy_model"}
    second = stack.client.post(
        "/api/v1/models/download", headers=AUTH, json={"variant_id": "kokoro-onnx-int8"}
    )
    assert second.status_code == 409
    stack.wheel.hold.set()
    stack.wait_idle()
    legacy = stack.client.post(
        "/api/v1/models/download", headers=AUTH, json={"variant_id": "kokoro-onnx-int8"}
    )
    assert legacy.status_code == 202
    assert legacy.json()["variant"]["id"] == "kokoro-onnx-int8"
    assert legacy.json()["asset"] is None
    stack.wait_idle()


# --- AC-77.8 / 77.10 (Session 33, MEU-77) -------------------------------------------------


def _tts_job(status: str, minute: int, **fields: Any) -> Any:
    from datetime import UTC, datetime
    from uuid import uuid4

    from avkit_core.domain.enums import MediaFormat, TTSSourceKind, TTSStatus
    from avkit_core.domain.tts import TTSJob

    stamp = datetime(2026, 10, 15, 12, minute, tzinfo=UTC)
    values: dict[str, Any] = {
        "id": str(uuid4()),
        "source_kind": TTSSourceKind.Inline,
        "source_path": None,
        "text_hash": "h" * 64,
        "text_preview": "Hello there.",
        "voice": "am_eric",
        "speed": 1.0,
        "format": MediaFormat.WAV,
        "status": TTSStatus(status),
        "output_path": None,
        "segments_total": 1000,
        "segments_done": 0,
        "error_message": None,
        "created_at": stamp,
        "updated_at": stamp,
    }
    values.update(fields)
    return TTSJob(**values)


def _add_rows(stack: Stack, *jobs: Any) -> None:
    # Setup: persist rows directly, as a backend that stopped mid-run leaves them.
    with stack.services.tts._uow_factory() as uow:  # type: ignore[attr-defined]
        for job in jobs:
            uow.tts_jobs.add(job)
        uow.commit()


def _lifespan_app(stack: Stack) -> Any:
    from avkit_api.main import create_app

    # engine_dispose=None: the `stack` fixture disposes the engine after the test.
    return create_app(tokens=frozenset({TOKEN}), services=stack.services, engine_dispose=None)


def _poll_tts(client: TestClient, job_id: str, wanted: str, timeout: float = 5.0) -> str:
    deadline = time.monotonic() + timeout
    while True:
        status = client.get(f"/api/v1/tts/{job_id}", headers=AUTH).json()["status"]
        if status == wanted or time.monotonic() > deadline:
            return str(status)
        time.sleep(0.02)


def test_ac_77_8_startup_fails_generating_rows(stack: Stack) -> None:
    _add_rows(stack, _tts_job("Generating", 1))
    with TestClient(_lifespan_app(stack)):
        rows = _tts_rows(stack)
    assert rows == [("Failed", "interrupted by restart")]


def test_ac_77_8_startup_keeps_terminal_rows_neg(stack: Stack, tmp_path: Path) -> None:
    _add_rows(
        stack,
        _tts_job("Done", 1, output_path=tmp_path / "out" / "done.wav", segments_done=1000),
        _tts_job("Cancelled", 2),
    )
    before = sorted(_tts_rows(stack), key=str)
    with TestClient(_lifespan_app(stack)):
        rows = sorted(_tts_rows(stack), key=str)
    assert rows == before


class _GatedGenerate:
    """Replaces the adapter's `generate`: reports progress, then blocks until released."""

    def __init__(self) -> None:
        self.entered = threading.Event()
        self.release = threading.Event()
        self.released: list[bool] = []

    def __call__(
        self, text: str, voice: object, speed: float, on_progress: Callable[[float], None]
    ) -> np.ndarray:
        del text, voice, speed
        on_progress(0.1)
        self.entered.set()
        self.released.append(self.release.wait(5.0))
        on_progress(0.5)
        return np.zeros(8, dtype=np.float32)


def test_ac_77_10_generate_returns_generating_then_cancel_reaches_cancelled(
    stack: Stack, monkeypatch: pytest.MonkeyPatch
) -> None:
    tts: Any = stack.services.tts
    assert hasattr(tts, "wait_idle"), "TTSService.wait_idle is missing"
    _load_ready_variant(stack, spacy=True)
    gated = _GatedGenerate()
    monkeypatch.setattr(tts._tts, "generate", gated)
    created = _post_generate(stack)
    assert created.status_code == 201, created.text
    assert created.json()["status"] == "Generating"
    job_id = created.json()["id"]
    assert gated.entered.wait(5.0)
    polled = stack.client.get(f"/api/v1/tts/{job_id}", headers=AUTH)
    assert polled.status_code == 200
    assert polled.json()["status"] == "Generating"
    cancelled = stack.client.delete(f"/api/v1/tts/{job_id}", headers=AUTH)
    assert cancelled.status_code == 204
    gated.release.set()
    assert _poll_tts(stack.client, job_id, "Cancelled") == "Cancelled"
    assert tts.wait_idle(5.0) is True
    assert gated.released == [True]


def test_ac_77_10_second_post_during_run_conflicts_neg(
    stack: Stack, monkeypatch: pytest.MonkeyPatch
) -> None:
    tts: Any = stack.services.tts
    assert hasattr(tts, "wait_idle"), "TTSService.wait_idle is missing"
    _load_ready_variant(stack, spacy=True)
    gated = _GatedGenerate()
    monkeypatch.setattr(tts._tts, "generate", gated)
    first = _post_generate(stack)
    assert first.status_code == 201, first.text
    assert gated.entered.wait(5.0)
    second = _post_generate(stack)
    assert second.status_code == 409
    error = second.json()["error"]
    assert set(error) == {"code", "message", "details"}
    assert error["message"] == "a TTS generation is already in progress"
    gated.release.set()
    assert tts.wait_idle(5.0) is True


# --- AC-98.6 sideload contract: list then load (Session 42, MEU-98) ----------------------------


def test_ac_98_6_sideload_contract_list_then_load(stack: Stack) -> None:
    from structlog.testing import capture_logs

    stack.put_vocab()
    stack.wheel.hold = threading.Event()  # the spaCy auto-download stays pending
    dropped = stack.models_dir / "kokoro-v1.0-onnx" / "onnx" / "model.onnx"
    dropped.parent.mkdir(parents=True, exist_ok=True)
    dropped.write_bytes(b"sideloaded weights")
    body = {"variant_id": "kokoro-onnx-fp32", "device": "cpu"}
    try:
        downloaded = stack.client.get("/api/v1/models/downloaded", headers=AUTH)
        assert downloaded.status_code == 200, downloaded.text
        assert "kokoro-onnx-fp32" in [item["id"] for item in downloaded.json()["items"]]
        loaded = stack.client.post("/api/v1/models/load", headers=AUTH, json=body)
        assert loaded.status_code == 200, loaded.text
        assert [call["path"] for call in FakeSession.calls] == [str(dropped)]
        with stack.services.models._uow_factory() as uow:  # type: ignore[attr-defined]
            row = uow.models.get("kokoro-onnx-fp32")
        assert row is not None
        assert (row.is_downloaded, row.path) == (True, dropped)
        assert row.size_bytes == dropped.stat().st_size

        # A recorded file deleted later: the existing 422 and one `tts.load_failed`.
        dropped.unlink()
        with capture_logs() as logs:
            again = stack.client.post("/api/v1/models/load", headers=AUTH, json=body)
        assert again.status_code == 422, again.text
        assert again.json()["error"]["message"] == "model weight file is missing"
        failed = [entry for entry in logs if entry["event"] == "tts.load_failed"]
        assert [(entry["variant_id"], entry["error"]) for entry in failed] == [
            ("kokoro-onnx-fp32", "FileNotFoundError")
        ], logs
    finally:
        stack.wheel.hold.set()
        stack.wait_idle()


# --- AC-98.8 / 98.9 SPACY_PATH_SWAP (Session 42, MEU-98) ---------------------------------------


def _spacy_install(models_dir: Path) -> Path:
    install = models_dir / "spacy" / "en_core_web_sm-3.8.0"
    with zipfile.ZipFile(io.BytesIO(_fake_wheel())) as zf:
        zf.extractall(install)
    return install


def _reset_tracked_spacy_entries(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_infra.tts import assets

    monkeypatch.setattr(assets, "_ACTIVE_SPACY_ENTRIES", set())


def test_ac_98_8_activate_swaps_tracked_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, isolated_path: None
) -> None:
    from avkit_infra.tts.assets import activate_spacy_dir, spacy_ready

    _reset_tracked_spacy_entries(monkeypatch)
    first, second, empty = tmp_path / "a", tmp_path / "b", tmp_path / "c"
    install_a, install_b = _spacy_install(first), _spacy_install(second)
    activate_spacy_dir(first)
    assert sys.path[-1] == str(install_a)
    activate_spacy_dir(second)
    assert str(install_a) not in sys.path
    assert sys.path[-1] == str(install_b)
    assert sys.path.count(str(install_b)) == 1
    settled = list(sys.path)
    activate_spacy_dir(second)
    assert sys.path == settled
    activate_spacy_dir(empty)
    assert str(install_a) not in sys.path
    assert str(install_b) not in sys.path
    assert spacy_ready(empty) is False


def test_ac_98_8_untracked_entry_survives(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, isolated_path: None
) -> None:
    from avkit_infra.tts.assets import activate_spacy_dir

    _reset_tracked_spacy_entries(monkeypatch)
    first, second, empty = tmp_path / "a", tmp_path / "b", tmp_path / "c"
    install_a = _spacy_install(first)
    _spacy_install(second)
    foreign = str(tmp_path / "someone-elses-dir")
    # One entry equals no install dir; the other is A's dir, appended before av-kit saw it.
    sys.path.extend([foreign, str(install_a)])
    for models_dir in (first, second, empty, first):
        activate_spacy_dir(models_dir)
        assert sys.path.count(foreign) == 1, models_dir
        assert sys.path.count(str(install_a)) == 1, models_dir


def test_ac_98_9_models_directory_change_reports_spacy_missing(
    stack: Stack, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _reset_tracked_spacy_entries(monkeypatch)
    _install_spacy(stack)
    install_a = stack.models_dir / "spacy" / "en_core_web_sm-3.8.0"
    assert stack.deps()["tts_spacy_model"]["state"] == "ready"
    settings: Any = stack.services.settings
    empty = tmp_path / "other-models"
    empty.mkdir()
    settings.set("tts", "models_directory", str(empty))
    assert stack.deps()["tts_spacy_model"]["state"] == "missing"
    assert str(install_a) not in sys.path
    settings.set("tts", "models_directory", str(stack.models_dir))
    assert stack.deps()["tts_spacy_model"]["state"] == "ready"
    assert sys.path.count(str(install_a)) == 1
