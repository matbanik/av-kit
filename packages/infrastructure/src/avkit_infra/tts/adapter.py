"""TTSPort adapter: Kokoro PyTorch and onnxruntime ONNX behind one G2P front end (MEU-72).

Both formats phonemize through `KokoroG2p` (`G2P_ROUTE`) and cut with `split_phonemes`
(`CHUNK_RULE`). The PyTorch variant calls kokoro's `KModel` directly (`TORCH_PATH`); kokoro's
`KPipeline` is never imported.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol

import numpy as np
import structlog
from onnxruntime import (
    InferenceSession,
    # Re-exported from onnxruntime's compiled module; its type stubs omit it.
    get_available_providers,  # type: ignore[attr-defined]
)

try:
    import torch
except ModuleNotFoundError:
    # Packaged onedir excludes torch and kokoro (AC-24.9, AC-72.6). The ONNX path still runs.
    torch = None

from avkit_core.domain.enums import DeviceType, ModelFormat
from avkit_core.domain.errors import ModelLoadError, ValidationError
from avkit_core.domain.tts import ModelStatus, ModelVariant, VoiceConfig
from avkit_infra.tts.assets import ONNX_VOCAB_FILE, ONNX_VOCAB_REPO
from avkit_infra.tts.espeak import EspeakCliAdapter
from avkit_infra.tts.g2p import KokoroG2p, split_phonemes
from avkit_infra.tts.voices import (
    PACK_ROWS,
    STYLE_DIM,
    VOICE_PACK_BYTES,
    list_voice_configs,
    voice_pack_path,
)

log = structlog.get_logger(module="tts")

__all__ = [
    "DeviceProbe",
    "KokoroAdapter",
    "ONNX_VOCAB_FILE",
    "ONNX_VOCAB_REPO",
    "runtime_devices",
]

MAX_ONNX_INPUT_IDS = 510
# Each G2P call gets one sentence or line, so misaki and eSpeak NG see short inputs.
_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+|\n+")


class PhonemeSource(Protocol):
    def phonemize(self, text: str, lang_code: str) -> str: ...


DeviceProbe = Callable[[ModelFormat], tuple[DeviceType, ...]]

# `DEVICE_ORDER`: probe results are listed in this order.
_DEVICE_ORDER = (DeviceType.Auto, DeviceType.CUDA, DeviceType.CPU, DeviceType.MPS)
# Runtime device names; they are also the wire names logged as `requested`/`actual`.
_DEVICE_NAMES = {DeviceType.CUDA: "cuda", DeviceType.CPU: "cpu", DeviceType.MPS: "mps"}


def runtime_devices(fmt: ModelFormat) -> tuple[DeviceType, ...]:
    """`DEVICE_PROBE`: the devices this process can load `fmt` on, read at call time.

    `Auto` and `CPU` are always listed. PyTorch adds `CUDA` and `MPS` as torch reports them
    (none when torch is not installed); ONNX adds `CUDA` when onnxruntime has the CUDA
    provider and never lists `MPS`. A runtime query that raises lists no such device and logs
    `tts.device_probe_failed`, so the catalog and a CPU load still work.
    """
    found = {DeviceType.Auto, DeviceType.CPU}
    if fmt is ModelFormat.ONNX:
        providers = get_available_providers
        if _query(fmt, DeviceType.CUDA, lambda: "CUDAExecutionProvider" in providers()):
            found.add(DeviceType.CUDA)
    elif torch is not None:
        cuda = torch.cuda
        if _query(fmt, DeviceType.CUDA, lambda: bool(cuda.is_available())):
            found.add(DeviceType.CUDA)
        mps = getattr(getattr(torch, "backends", None), "mps", None)
        if (
            mps is not None
            and callable(getattr(mps, "is_available", None))
            and _query(fmt, DeviceType.MPS, lambda: bool(mps.is_available()))
        ):
            found.add(DeviceType.MPS)
    return tuple(device for device in _DEVICE_ORDER if device in found)


def _query(fmt: ModelFormat, device: DeviceType, ask: Callable[[], bool]) -> bool:
    """One runtime availability query; a raising query reports the device as absent."""
    try:
        return ask()
    except Exception as exc:
        log.warning(
            "tts.device_probe_failed",
            format=fmt.value,
            device=_DEVICE_NAMES[device],
            error=type(exc).__name__,
        )
        return False


def _log_fallback(variant: ModelVariant, requested: str, reason: str) -> None:
    log.warning(
        "tts.device_fallback",
        variant_id=variant.id,
        requested=requested,
        actual="cpu",
        reason=reason,
    )


def _log_load_failed(variant: ModelVariant, device: str, exc: BaseException) -> None:
    """`LOG_CAUSE`: a `ModelLoadError` with a cause logs the cause's type, else `exc`'s own.

    `detail` is the first line of that same exception's text; an empty text adds none.
    """
    cause = exc.__cause__ if isinstance(exc, ModelLoadError) else None
    source = cause if cause is not None else exc
    error = type(source).__name__
    lines = str(source).strip().splitlines()
    fields = {"detail": lines[0].strip()} if lines else {}
    log.error("tts.load_failed", variant_id=variant.id, device=device, error=error, **fields)


def _onnx_providers(device_name: str) -> list[str]:
    if device_name == "cuda":
        return ["CUDAExecutionProvider", "CPUExecutionProvider"]
    return ["CPUExecutionProvider"]


def _require_weight_path(variant: ModelVariant) -> Path:
    path = variant.path
    try:
        present = path is not None and path.is_file()
    except OSError as exc:  # `is_file` re-raises e.g. a PermissionError from `stat`
        raise ModelLoadError("model weight file is unreadable") from exc
    if path is None or not present:
        missing = path if path is not None else Path(variant.id)
        raise ModelLoadError("model weight file is missing") from FileNotFoundError(str(missing))
    return path


def _as_float32_pcm(raw: object) -> np.ndarray:
    """Flatten model output to float32 PCM in [-1.0, 1.0].

    Kokoro's output can peak slightly past ±1.0; it is clipped (as a 16-bit PCM write
    in the Kokoro reference example does), so the WAV writer's range contract holds.
    """
    detach = getattr(raw, "detach", None)
    if callable(detach):  # a torch tensor, possibly on CUDA
        tensor: Any = detach()
        raw = tensor.cpu().numpy()
    audio = np.asarray(raw, dtype=np.float32).reshape(-1)
    if audio.size and not bool(np.all(np.isfinite(audio))):
        raise ValidationError("generated audio must be finite")
    return np.clip(audio, -1.0, 1.0)


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_BREAK.split(text) if part.strip()]


def _phoneme_symbols(phonemes: object) -> list[str]:
    if isinstance(phonemes, str):
        return list(phonemes)
    if isinstance(phonemes, list | tuple):
        return [str(item) for item in phonemes]
    return []


class KokoroAdapter:
    """Kokoro TTS adapter. generate returns PCM only; no WAV writes."""

    def __init__(
        self,
        *,
        onnx_vocab_path: Path | None = None,
        vocab_path: Callable[[], Path] | None = None,
        g2p: PhonemeSource | None = None,
        device_probe: DeviceProbe | None = None,
    ) -> None:
        """Create the adapter.

        Args:
            onnx_vocab_path: A fixed vocab/config path (tests and overrides).
            vocab_path: A resolver evaluated per call (production: `VOCAB_LOCATION` under
                the current `tts.models_directory`). Ignored when `onnx_vocab_path` is set.
            g2p: The phoneme source (default: `KokoroG2p` over the eSpeak NG CLI, built on
                first use).
            device_probe: Which devices exist per format (default: `runtime_devices`).
        """
        self._onnx_vocab_path = onnx_vocab_path
        self._device_probe: DeviceProbe = device_probe or runtime_devices
        self._vocab_resolver = vocab_path
        self._g2p = g2p
        self._variant: ModelVariant | None = None
        self._device_name = "cpu"
        self._kmodel: Any = None
        self._session: InferenceSession | None = None

    def unload_model(self) -> None:
        self._variant = None
        self._kmodel = None
        self._session = None
        self._device_name = "cpu"

    def get_model_status(self) -> ModelStatus:
        variant = self._variant
        if variant is None:
            return ModelStatus(
                variant_id=None,
                name="unloaded",
                device=self._device_name,
                memory_bytes=0,
                is_loaded=False,
            )
        path = variant.path
        memory = path.stat().st_size if path is not None and path.is_file() else 0
        return ModelStatus(
            variant_id=variant.id,
            name=variant.name,
            device=self._device_name,
            memory_bytes=memory,
            is_loaded=True,
        )

    def list_voices(self) -> list[VoiceConfig]:
        return list_voice_configs()

    def available_devices(self, fmt: ModelFormat) -> tuple[DeviceType, ...]:
        return self._device_probe(fmt)

    def load_model(self, variant: ModelVariant, device: DeviceType) -> None:
        """Load `variant`, falling back to CPU (`DEVICE_RESOLVE`, `LOAD_FALLBACK`).

        The model or session is built in locals; the adapter's fields change only once
        every stage has succeeded, so a failed load leaves nothing loaded on `cpu`. Every
        failure logs one `tts.load_failed` before it leaves (`LOAD_FAILURE_PATHS`).

        Raises:
            ModelLoadError: The weight file is missing or unreadable, the runtime is not
                bundled or failed to initialize, the device probe raised, or the load failed
                on every device it tried (the cause is the last failure).
            ValidationError: The variant's format is neither PyTorch nor ONNX.
        """
        self.unload_model()
        try:
            path = _require_weight_path(variant)
        except ModelLoadError as exc:
            _log_load_failed(variant, "cpu", exc)
            raise
        try:
            target = self._resolve(variant, device)
        except Exception as exc:
            # `runtime_devices` never raises; an injected probe still must not escape bare.
            _log_load_failed(variant, "cpu", exc)
            raise ModelLoadError("TTS device probe failed") from exc
        kmodel: Any = None
        session: InferenceSession | None = None
        if variant.format is ModelFormat.PyTorch:
            kmodel, actual = self._load_pytorch(variant, path, target)
        elif variant.format is ModelFormat.ONNX:
            session, actual = self._load_onnx(variant, path, target)
        else:
            unsupported = ValidationError(f"unsupported model format: {variant.format}")
            _log_load_failed(variant, target, unsupported)
            raise unsupported
        self._kmodel = kmodel
        self._session = session
        self._device_name = actual
        self._variant = variant
        log.info("tts.load_model", variant_id=variant.id, device=actual)

    def _resolve(self, variant: ModelVariant, device: DeviceType) -> str:
        """`DEVICE_RESOLVE`: the device name to try first."""
        probe = self._device_probe(variant.format)
        if device is DeviceType.Auto:
            for candidate in (DeviceType.CUDA, DeviceType.MPS):
                if candidate in probe:
                    return _DEVICE_NAMES[candidate]
            return "cpu"
        if device is DeviceType.CPU or device in probe:
            return _DEVICE_NAMES[device]
        _log_fallback(variant, _DEVICE_NAMES[device], "unavailable")
        return "cpu"

    def _load_pytorch(self, variant: ModelVariant, path: Path, target: str) -> tuple[Any, str]:
        if torch is None:
            absent = ModelLoadError("PyTorch runtime is not bundled")
            _log_load_failed(variant, target, absent)
            raise absent
        try:
            # `TORCH_PATH`: only `KModel`, imported here, never `KPipeline`.
            from kokoro import KModel
        except ImportError as exc:
            _log_load_failed(variant, target, exc)
            raise ModelLoadError("PyTorch runtime is not bundled") from exc
        except Exception as exc:
            # The engine is present but failed to initialize (a native DLL, say): a failed load.
            _log_load_failed(variant, target, exc)
            raise ModelLoadError("PyTorch model failed to load") from exc
        tried = target
        try:
            config = self._vocab_file()
            # A local config keeps kokoro from fetching config.json from Hugging Face at load.
            # The constructor takes no device, so a failure here is not retried.
            loaded = KModel(
                repo_id=ONNX_VOCAB_REPO,
                config=str(config) if config is not None and config.is_file() else None,
                model=str(path),
            )
            try:
                moved = loaded.to(target)
            except Exception:
                if target == "cpu":
                    raise
                _log_fallback(variant, target, "load_failed")
                tried = "cpu"
                moved = loaded.to("cpu")
            model = moved.eval() if hasattr(moved, "eval") else moved
        except Exception as exc:
            _log_load_failed(variant, tried, exc)
            raise ModelLoadError("PyTorch model failed to load") from exc
        return model, tried

    def _load_onnx(
        self, variant: ModelVariant, path: Path, target: str
    ) -> tuple[InferenceSession, str]:
        if target == "cuda":
            try:
                session = InferenceSession(str(path), providers=_onnx_providers("cuda"))
                active = session.get_providers()
            except Exception:
                # A session whose providers cannot be read cannot confirm its device.
                _log_fallback(variant, "cuda", "load_failed")
            else:
                if "CUDAExecutionProvider" in active:
                    return session, "cuda"
                _log_fallback(variant, "cuda", "provider_fallback")
                return session, "cpu"
        try:
            # The CPU session is trusted as built; `get_providers` is never read here.
            session = InferenceSession(str(path), providers=_onnx_providers("cpu"))
        except Exception as exc:
            _log_load_failed(variant, "cpu", exc)
            raise ModelLoadError("ONNX session failed") from exc
        return session, "cpu"

    def _vocab_file(self) -> Path | None:
        if self._onnx_vocab_path is not None:
            return self._onnx_vocab_path
        if self._vocab_resolver is not None:
            return self._vocab_resolver()
        return None

    def _g2p_engine(self) -> PhonemeSource:
        if self._g2p is None:
            self._g2p = KokoroG2p(EspeakCliAdapter())
        return self._g2p

    def _phoneme_chunks(self, text: str, lang_code: str) -> list[str]:
        """`G2P_ROUTE` per sentence, joined, then cut by `CHUNK_RULE`."""
        engine = self._g2p_engine()
        phonemes = [engine.phonemize(sentence, lang_code) for sentence in _sentences(text)]
        return split_phonemes(" ".join(ps for ps in phonemes if ps))

    def _torch_chunk(self, phonemes: str, pack: np.ndarray, speed: float) -> np.ndarray:
        """`TORCH_PATH`: the style row is indexed by phoneme-string length, as in kokoro."""
        assert torch is not None
        row = pack[min(len(phonemes), PACK_ROWS) - 1].copy()
        ref_s = torch.from_numpy(row).unsqueeze(0).to(self._device_name)
        return _as_float32_pcm(self._kmodel(phonemes, ref_s, speed))

    def _load_onnx_vocab(self) -> dict[str, int]:
        path = self._vocab_file()
        if path is None or not path.is_file():
            missing = path if path is not None else Path(ONNX_VOCAB_FILE)
            raise ModelLoadError("ONNX vocab file is missing") from FileNotFoundError(str(missing))
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise ModelLoadError("ONNX vocab file is unreadable") from exc
        vocab = payload.get("vocab") if isinstance(payload, dict) else None
        if not isinstance(vocab, dict):
            raise ValidationError("ONNX vocab file missing vocab mapping")
        mapped: dict[str, int] = {}
        for key, value in vocab.items():
            if isinstance(key, str) and isinstance(value, int) and not isinstance(value, bool):
                mapped[key] = value
        return mapped

    def _voice_pack(self, voice_id: str) -> np.ndarray:
        """Read `VOICE_PACK` for `voice_id` from the models dir that holds the vocab.

        Raises:
            ModelLoadError: the pack is missing (cause `FileNotFoundError`), unreadable or
                not exactly `VOICE_PACK_BYTES`.
        """
        vocab = self._vocab_file()
        if vocab is None:
            raise ModelLoadError(f"voice pack {voice_id} is missing") from FileNotFoundError(
                f"{voice_id}.bin"
            )
        path = voice_pack_path(vocab.parent, voice_id)
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise ModelLoadError(f"voice pack {voice_id} is missing") from exc
        if len(raw) != VOICE_PACK_BYTES:
            raise ModelLoadError(
                f"voice pack {voice_id} is {len(raw)} bytes, expected {VOICE_PACK_BYTES}"
            )
        return np.frombuffer(raw, dtype="<f4").reshape(PACK_ROWS, STYLE_DIM)

    def _onnx_chunk(
        self,
        phonemes: object,
        voice: VoiceConfig,
        speed: float,
        session: InferenceSession,
    ) -> np.ndarray:
        vocab = self._load_onnx_vocab()
        symbols = _phoneme_symbols(phonemes)
        input_ids = [vocab[symbol] for symbol in symbols if symbol in vocab]
        if len(input_ids) > MAX_ONNX_INPUT_IDS:
            raise ValidationError("ONNX input_ids exceed 510")
        tokens = np.array([[0, *input_ids, 0]], dtype=np.int64)
        # ONNX_FEEDS: the style row is indexed by the token count, after unknowns are dropped.
        pack = self._voice_pack(voice.voice_id)
        style = pack[max(min(len(input_ids), PACK_ROWS) - 1, 0)].reshape(1, STYLE_DIM)
        speed_arr = np.array([speed], dtype=np.float32)
        outputs = session.run(
            None,
            {"input_ids": tokens, "style": style, "speed": speed_arr},
        )
        return _as_float32_pcm(outputs[0] if outputs else [])

    def generate(
        self,
        text: str,
        voice: VoiceConfig,
        speed: float,
        on_progress: Callable[[float], None],
    ) -> np.ndarray:
        if not isinstance(text, str):
            raise ValidationError("text must be a str")
        if not math.isfinite(float(speed)):
            raise ValidationError("speed must be finite")
        variant = self._variant
        if variant is None:
            raise ModelLoadError("no model is loaded") from FileNotFoundError("no model is loaded")
        lang_code = voice.voice_id[0]
        session = self._session
        if variant.format is ModelFormat.PyTorch:
            if torch is None or self._kmodel is None:
                raise ModelLoadError("PyTorch model is not loaded") from FileNotFoundError(
                    "PyTorch model is not loaded"
                )
        elif variant.format is ModelFormat.ONNX:
            if session is None:
                raise ModelLoadError("ONNX session is not loaded") from FileNotFoundError(
                    "ONNX session is not loaded"
                )
        else:
            raise ValidationError(f"unsupported model format: {variant.format}")
        chunks = self._phoneme_chunks(text, lang_code)
        total = len(chunks)
        if total == 0:
            on_progress(1.0)
            return np.array([], dtype=np.float32)
        pieces: list[np.ndarray] = []
        if session is not None:
            for index, chunk in enumerate(chunks, start=1):
                pieces.append(self._onnx_chunk(chunk, voice, speed, session))
                on_progress(index / total)
        else:
            pack = self._voice_pack(voice.voice_id)
            for index, chunk in enumerate(chunks, start=1):
                pieces.append(self._torch_chunk(chunk, pack, speed))
                on_progress(index / total)
        return np.concatenate(pieces)
