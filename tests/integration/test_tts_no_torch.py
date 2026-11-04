"""MEU-72 AC-72.1 `IMPORT_HYGIENE`: the ONNX path runs with torch and kokoro unimportable.

A fresh interpreter blocks `torch`, `kokoro`, `phonemizer` and `espeakng_loader` through
`sys.modules[name] = None`, so any import attempt fails loudly. It imports the real
`misaki.en`, then generates one English and one Spanish ONNX clip through `KokoroG2p` with a
fake `misaki_factory`, a fake session and a fake espeak runner.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOCKED = ("torch", "kokoro", "phonemizer", "espeakng_loader")

SCRIPT = r"""
import json
import subprocess
import sys
from pathlib import Path

BLOCKED = ("torch", "kokoro", "phonemizer", "espeakng_loader")
for name in BLOCKED:
    sys.modules[name] = None

import misaki.en  # noqa: E402,F401 - the real module, not a fake
import numpy as np  # noqa: E402
import spacy.util  # noqa: E402

spacy.util.is_package = lambda name: True

import avkit_infra.tts.adapter as adapter_mod  # noqa: E402
from avkit_core.domain.enums import DeviceType, ModelFormat, ModelPrecision  # noqa: E402
from avkit_core.domain.tts import ModelVariant  # noqa: E402
from avkit_infra.tts.espeak import EspeakCliAdapter  # noqa: E402
from avkit_infra.tts.g2p import KokoroG2p  # noqa: E402
from avkit_infra.tts.voices import list_voice_configs  # noqa: E402

root = Path(sys.argv[1])
models = root / "models"
voices_dir = models / "kokoro-v1.0-onnx" / "voices"
voices_dir.mkdir(parents=True)
for voice_id in ("af_heart", "ef_dora"):
    (voices_dir / f"{voice_id}.bin").write_bytes(np.zeros((510, 256), dtype="<f4").tobytes())
vocab = models / "config.json"
vocab.write_text(json.dumps({"vocab": {"a": 1, "b": 2}}), encoding="utf-8")
weights = models / "kokoro-v1.0-onnx" / "onnx" / "model_quantized.onnx"
weights.parent.mkdir(parents=True)
weights.write_bytes(b"weights")
exe = root / "espeak-ng.exe"
exe.write_bytes(b"exe")


class FakeSession:
    def __init__(self, path, providers=None, **kwargs):
        self.path = path

    def run(self, outputs, feed):
        return [np.array([[1.5, -0.25, 0.25]], dtype=np.float32)]


def fake_run(argv, **kwargs):
    stdout = "eSpeak NG text-to-speech: 1.52.0\n" if "--version" in argv else "ab\n"
    return subprocess.CompletedProcess(argv, 0, stdout=stdout, stderr="")


adapter_mod.InferenceSession = FakeSession
espeak = EspeakCliAdapter(which=lambda name: str(exe), environ={}, run=fake_run)
g2p = KokoroG2p(espeak, misaki_factory=lambda **kwargs: (lambda text: ("ab", [])))
adapter = adapter_mod.KokoroAdapter(onnx_vocab_path=vocab, g2p=g2p)
variant = ModelVariant(
    id="kokoro-onnx-int8",
    name="Kokoro ONNX int8",
    format=ModelFormat.ONNX,
    precision=ModelPrecision.INT8,
    size_bytes=weights.stat().st_size,
    path=weights,
    is_downloaded=True,
)
adapter.load_model(variant, DeviceType.CPU)
by_id = {voice.voice_id: voice for voice in list_voice_configs()}
results = {}
for voice_id, text in (("af_heart", "Hello there."), ("ef_dora", "Hola.")):
    progress = []
    pcm = adapter.generate(text, by_id[voice_id], 1.0, progress.append)
    results[voice_id] = {
        "dtype": str(pcm.dtype),
        "size": int(pcm.size),
        "finite": bool(np.all(np.isfinite(pcm))),
        "in_range": bool(np.all((pcm >= -1.0) & (pcm <= 1.0))),
        "last_progress": progress[-1] if progress else None,
    }
loaded = sorted(
    name
    for name, module in sys.modules.items()
    if module is not None
    and any(
        name == root_name or name.startswith(root_name + ".")
        for root_name in (*BLOCKED, "misaki.espeak")
    )
)
print(json.dumps({"results": results, "loaded": loaded}))
"""


@pytest.mark.integration
def test_ac_72_1_onnx_generate_without_torch_or_kokoro(tmp_path: Path) -> None:
    done = subprocess.run(
        [sys.executable, "-c", SCRIPT, str(tmp_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        check=False,
    )
    assert done.returncode == 0, done.stderr[-4000:]
    report = json.loads(done.stdout.strip().splitlines()[-1])
    assert sorted(report["results"]) == ["af_heart", "ef_dora"]
    for voice_id, result in report["results"].items():
        assert result["dtype"] == "float32", voice_id
        assert result["size"] > 0, voice_id
        assert result["finite"] is True, voice_id
        assert result["in_range"] is True, voice_id
        assert result["last_progress"] == 1.0, voice_id
    assert report["loaded"] == []


PROBE_SCRIPT = r"""
import json
import sys

for name in ("torch", "kokoro", "phonemizer", "espeakng_loader"):
    sys.modules[name] = None

from avkit_core.domain.enums import ModelFormat  # noqa: E402
from avkit_infra.tts.adapter import runtime_devices  # noqa: E402

print(json.dumps([device.value for device in runtime_devices(ModelFormat.PyTorch)]))
"""


@pytest.mark.integration
def test_ac_75_1_pytorch_probe_without_torch_is_auto_and_cpu() -> None:
    done = subprocess.run(
        [sys.executable, "-c", PROBE_SCRIPT],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        check=False,
    )
    assert done.returncode == 0, done.stderr[-4000:]
    assert json.loads(done.stdout.strip().splitlines()[-1]) == ["Auto", "CPU"]
