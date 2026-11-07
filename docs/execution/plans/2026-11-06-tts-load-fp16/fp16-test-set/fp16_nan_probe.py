"""Why did ONNX FP16 return non-finite audio? Run each chunk on both local FP16 files and on the other ONNX files. Read-only."""
import hashlib
import json
import sys
from pathlib import Path

sys.modules["torch"] = None
import numpy as np
import onnxruntime as ort

from avkit_infra.tts.g2p import split_phonemes
from avkit_infra.tts.voices import voice_pack_path

MODELS = Path.home() / ".avkit/models"
OUT = Path("C:/Temp/av-kit/tts-compare")
cache = json.loads((OUT / "phonemes.json").read_text(encoding="utf-8"))
vocab = json.loads((MODELS / "config.json").read_text(encoding="utf-8"))["vocab"]
pack = np.fromfile(voice_pack_path(MODELS, "af_heart"), dtype="<f4").reshape(510, 256)
FILES = {
    "fp16 app path": MODELS / "kokoro-v1.0-onnx/onnx/model_fp16.onnx",
    "fp16 old path": MODELS / "onnx/model_fp16.onnx",
    "fp32 old path": MODELS / "onnx/model.onnx",
    "int8 old path": MODELS / "onnx/model_quantized.onnx",
}
whole = " ".join(ps for ps in cache.values() if ps)
chunks = split_phonemes(whole)
sentences = [ps for ps in cache.values() if ps]
print("onnxruntime", ort.__version__, "| chunks", [len(c) for c in chunks], "| sentence lengths", [len(s) for s in sentences])
for label, path in FILES.items():
    if not path.is_file():
        print(label, "missing")
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    print(f"\n--- {label} | {path.stat().st_size:,} B | sha256 {digest} | style input type", [i.type for i in session.get_inputs() if i.name == "style"])
    for name, group in (("chunks", chunks), ("sentences", sentences)):
        for index, text in enumerate(group):
            ids = [vocab[s] for s in text if s in vocab]
            style = pack[max(min(len(ids), 510) - 1, 0)].reshape(1, 256)
            results = []
            for _ in range(3):
                audio = session.run(None, {"input_ids": np.array([[0, *ids, 0]], dtype=np.int64), "style": style, "speed": np.array([1.0], dtype=np.float32)})[0].reshape(-1)
                bad = int(np.sum(~np.isfinite(audio)))
                results.append((audio.size, bad, hashlib.sha256(audio.tobytes()).hexdigest()[:8]))
            first_bad = np.flatnonzero(~np.isfinite(audio))
            where = f"first bad sample {int(first_bad[0])}" if first_bad.size else ""
            print(f"{name}[{index}] tokens {len(ids):3} | samples {results[0][0]:7} | bad per run {[r[1] for r in results]} | repeatable {len({r[2] for r in results}) == 1} {where}")
