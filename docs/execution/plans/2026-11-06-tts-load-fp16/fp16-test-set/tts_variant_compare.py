"""Compare the four Kokoro variants through the app's KokoroAdapter: same text, voice, speed and device, each in a fresh process.

ONNX runs block torch, as the packaged backend has none. Read-only for the repo; output goes to C:/Temp/av-kit/tts-compare.
"""
import ctypes
import hashlib
import json
import statistics
import subprocess
import sys
import time
import wave
from ctypes import wintypes
from pathlib import Path

MODELS = Path.home() / ".avkit/models"
OUT = Path("C:/Temp/av-kit/tts-compare")
WEIGHTS = {
    "kokoro-pt-fp32": MODELS / "kokoro-v1_0.pth",
    "kokoro-onnx-fp32": MODELS / "onnx/model.onnx",
    "kokoro-onnx-fp16": MODELS / "kokoro-v1.0-onnx/onnx/model_fp16.onnx",
    "kokoro-onnx-int8": MODELS / "onnx/model_quantized.onnx",
}
VOICE = "af_heart"
SPEED = 1.0
RATE = 24000
TEXT = (
    "The morning train left the station a few minutes late. Most of the passengers were reading or looking out at the wet fields. "
    "A young woman near the door opened her notebook and began to write a long letter to her brother. "
    "She told him about the new house, the garden that needed work, and the neighbours who had already invited her to dinner. "
    "By the time the train reached the coast, the rain had stopped and the sea was bright under a pale sky. "
    "She folded the letter, put it in her coat, and smiled."
)


class Counters(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def peak_mb() -> float:
    kernel32 = ctypes.WinDLL("kernel32")
    psapi = ctypes.WinDLL("psapi")
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    counters = Counters()
    counters.cb = ctypes.sizeof(Counters)
    psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb)
    return counters.PeakWorkingSetSize / 1_000_000


def child(variant_id: str, round_number: int) -> None:
    started = time.perf_counter()
    if "onnx" in variant_id:
        sys.modules["torch"] = None
    import numpy as np

    from avkit_core.domain.enums import DeviceType
    from avkit_core.domain.tts import ModelVariant
    from avkit_infra.tts.adapter import KokoroAdapter
    from avkit_infra.tts.voices import CATALOG_METADATA, voice_config_for

    imported = time.perf_counter() - started
    cache = json.loads((OUT / "phonemes.json").read_text(encoding="utf-8"))

    class CachedPhonemes:
        def phonemize(self, text: str, lang_code: str) -> str:
            return cache[text]

    meta = CATALOG_METADATA[variant_id]
    path = WEIGHTS[variant_id]
    variant = ModelVariant(id=variant_id, name=str(meta["name"]), format=meta["format"], precision=meta["precision"], size_bytes=path.stat().st_size, path=path, is_downloaded=True)
    adapter = KokoroAdapter(onnx_vocab_path=MODELS / "config.json", g2p=CachedPhonemes())
    started = time.perf_counter()
    adapter.load_model(variant, DeviceType.CPU)
    loaded = time.perf_counter() - started
    after_load = peak_mb()
    voice = voice_config_for(VOICE)
    timings, hashes, audio, first = [], [], None, None
    for _ in range(4):
        started = time.perf_counter()
        audio = adapter.generate(TEXT, voice, SPEED, lambda _fraction: None)
        timings.append(time.perf_counter() - started)
        hashes.append(hashlib.sha256(audio.tobytes()).hexdigest()[:12])
        first = audio if first is None else first
    noise = float(np.mean((first - audio) ** 2)) if first.size == audio.size else None
    run_to_run = None if not noise else float(10 * np.log10(float(np.mean(first**2)) / noise))
    stem = OUT / variant_id
    if round_number == 0:
        np.save(stem.with_suffix(".npy"), audio)
        with wave.open(str(stem.with_suffix(".wav")), "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(RATE)
            out.writeframes((audio * 32767).astype("<i2").tobytes())
    result = {
        "variant": variant_id,
        "round": round_number,
        "file_mb": path.stat().st_size / 1_000_000,
        "import_s": imported,
        "load_s": loaded,
        "peak_after_load_mb": after_load,
        "peak_mb": peak_mb(),
        "first_generate_s": timings[0],
        "generate_s": statistics.median(timings[1:]),
        "audio_s": audio.size / RATE,
        "samples": int(audio.size),
        "repeatable": len(set(hashes)) == 1,
        "run_to_run_snr_db": run_to_run,
        "device": adapter.get_model_status().device,
        "torch_loaded": sys.modules.get("torch") is not None,
    }
    (OUT / f"{variant_id}.{round_number}.json").write_text(json.dumps(result), encoding="utf-8")


def phonemes() -> None:
    """The app's G2P, once, so every variant gets the same phonemes without spaCy in its process."""
    started = time.perf_counter()
    from avkit_infra.tts.adapter import _sentences
    from avkit_infra.tts.assets import activate_spacy_dir
    from avkit_infra.tts.espeak import EspeakCliAdapter
    from avkit_infra.tts.g2p import KokoroG2p

    activate_spacy_dir(MODELS)
    engine = KokoroG2p(EspeakCliAdapter())
    cache = {sentence: engine.phonemize(sentence, VOICE[0]) for sentence in _sentences(TEXT)}
    (OUT / "phonemes.json").write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    print("phonemes", sum(len(v) for v in cache.values()), "chars in", len(cache), "sentences,", round(time.perf_counter() - started, 1), "s including imports")


def log_mel(audio, numpy):
    window, hop = 1024, 480
    frames = numpy.lib.stride_tricks.sliding_window_view(audio, window)[::hop] * numpy.hanning(window)
    power = numpy.abs(numpy.fft.rfft(frames, axis=1)) ** 2
    edges = numpy.geomspace(3, power.shape[1] - 1, 81).astype(int)
    bands = numpy.stack([power[:, a : max(a + 1, b)].sum(axis=1) for a, b in zip(edges[:-1], edges[1:])], axis=1)
    return 10 * numpy.log10(bands + 1e-10)


def aligned_distance(a, b, numpy, band: int = 200) -> float:
    """Mean dB distance per band along the best time alignment, so a pace difference alone does not count."""
    n, m = len(a), len(b)
    cost = numpy.full((n + 1, m + 1), numpy.inf)
    steps = numpy.zeros((n + 1, m + 1), dtype=numpy.int32)
    cost[0, 0] = 0
    for i in range(1, n + 1):
        low, high = max(1, i - band), min(m, i + band)
        row = numpy.abs(a[i - 1] - b[low - 1 : high]).mean(axis=1)
        for j, value in zip(range(low, high + 1), row):
            options = (cost[i - 1, j - 1], cost[i - 1, j], cost[i, j - 1])
            best = int(numpy.argmin(options))
            cost[i, j] = options[best] + value
            steps[i, j] = (steps[i - 1, j - 1], steps[i - 1, j], steps[i, j - 1])[best] + 1
    return float(cost[n, m] / steps[n, m])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("text words", len(TEXT.split()), "| voice", VOICE, "| speed", SPEED, "| device cpu")
    prepared = subprocess.run([sys.executable, __file__, "phonemes"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(prepared.stdout.strip()[-200:] if not prepared.returncode else "PHONEMES FAILED " + prepared.stderr[-1200:], flush=True)
    for round_number in range(3):
        for variant_id in WEIGHTS:
            done = subprocess.run([sys.executable, __file__, "child", variant_id, str(round_number)], capture_output=True, text=True, encoding="utf-8", errors="replace")
            if done.returncode:
                print("FAILED", variant_id, done.returncode, done.stderr[-1200:])
            print("ran", variant_id, "round", round_number, flush=True)

    rows = {v: [json.loads(p.read_text(encoding="utf-8")) for p in sorted(OUT.glob(f"{v}.*.json"))] for v in WEIGHTS}
    print(f"\n{'variant':18} {'file MB':>8} {'import s':>9} {'load s':>7} {'peak MB':>8} {'first s':>8} {'gen s':>6} {'audio s':>8} {'x real':>7} {'same':>5} {'torch':>6} device")
    for variant_id, runs in rows.items():
        if not runs:
            continue
        pick = lambda key, fn=statistics.median: fn(r[key] for r in runs)  # noqa: E731
        generate = pick("generate_s")
        audio = runs[0]["audio_s"]
        print(f"{variant_id:18} {runs[0]['file_mb']:8.0f} {pick('import_s'):9.1f} {pick('load_s'):7.2f} {pick('peak_mb', max):8.0f} {pick('first_generate_s'):8.2f} {generate:6.2f} {audio:8.2f} {audio / generate:7.1f} {str(all(r['repeatable'] for r in runs)):>5} {str(runs[0]['torch_loaded']):>6} {runs[0]['device']}")
    print("per-round gen s", {v: [round(r["generate_s"], 2) for r in runs] for v, runs in rows.items()})
    print("samples equal across rounds", {v: len({r["samples"] for r in runs}) == 1 for v, runs in rows.items()})
    print("run-to-run SNR dB within a process, None means sample-identical", {v: [None if r["run_to_run_snr_db"] is None else round(r["run_to_run_snr_db"], 1) for r in runs] for v, runs in rows.items()})

    import numpy

    audio = {v: numpy.load(OUT / f"{v}.npy") for v in WEIGHTS if (OUT / f"{v}.npy").exists()}
    mel = {v: log_mel(a, numpy) for v, a in audio.items()}
    print("\npair | duration ratio | sample SNR dB if same length | aligned spectrum distance dB")
    pairs = [("kokoro-pt-fp32", "kokoro-onnx-fp32"), ("kokoro-pt-fp32", "kokoro-onnx-fp16"), ("kokoro-pt-fp32", "kokoro-onnx-int8"), ("kokoro-onnx-fp32", "kokoro-onnx-fp16"), ("kokoro-onnx-fp32", "kokoro-onnx-int8")]
    for a, b in pairs:
        if a not in audio or b not in audio:
            continue
        ratio = audio[b].size / audio[a].size
        snr = "n/a"
        if audio[a].size == audio[b].size:
            noise = float(numpy.mean((audio[a] - audio[b]) ** 2))
            snr = "identical" if noise == 0 else f"{10 * numpy.log10(float(numpy.mean(audio[a] ** 2)) / noise):.1f}"
        print(f"{a} vs {b} | {ratio:.3f} | {snr} | {aligned_distance(mel[a], mel[b], numpy):.2f}")
    print("\nnative outputs: ", sorted(p.name for p in OUT.glob("*.wav")))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "child":
        child(sys.argv[2], int(sys.argv[3]))
    elif len(sys.argv) > 1 and sys.argv[1] == "phonemes":
        phonemes()
    else:
        main()
