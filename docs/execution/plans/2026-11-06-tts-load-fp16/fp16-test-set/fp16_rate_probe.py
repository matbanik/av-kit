"""How often does each variant fail, through the app's adapter, on ordinary text? Uses the pinned ONNX files a fresh download gets. Models folder untouched."""
import json
import statistics
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np
from huggingface_hub import hf_hub_download

from avkit_core.domain.enums import DeviceType
from avkit_core.domain.errors import ValidationError
from avkit_core.domain.tts import ModelVariant
from avkit_infra.tts.adapter import KokoroAdapter, _sentences
from avkit_infra.tts.assets import activate_spacy_dir
from avkit_infra.tts.espeak import EspeakCliAdapter
from avkit_infra.tts.g2p import KokoroG2p
from avkit_infra.tts.voices import CATALOG_METADATA, ONNX_REPO, ONNX_REVISION, voice_config_for

MODELS = Path.home() / ".avkit/models"
OUT = Path("C:/Temp/av-kit/tts-compare")
PINNED = OUT / "pinned"
RATE = 24000
SENTENCES = [
    "The kettle clicked off just as the phone began to ring.",
    "Nobody at the table wanted to be the first to speak.",
    "He checked the map twice before turning onto the gravel road.",
    "Rain tapped against the window for most of the afternoon.",
    "We should leave early if we want to avoid the traffic near the bridge.",
    "Her first job was sorting letters at the small post office on the corner.",
    "The museum closes at five, but the gift shop stays open a little longer.",
    "After the storm, the whole street smelled of wet leaves and cut grass.",
    "I could not remember where I had put the keys, so I looked in every coat pocket.",
    "The children built a tower out of old boxes and painted it bright green.",
    "When the lights came back on, everyone in the room started talking at the same time.",
    "A narrow path runs along the river and comes out behind the old mill.",
    "The doctor said the results looked good and asked him to come back in six months.",
    "She kept the photograph in a drawer and only took it out when she was alone.",
    "The bakery on the square sells out of bread by nine o'clock on most Saturdays.",
    "They spent the whole summer repairing the roof, the fence and the broken garden gate.",
    "If the train is delayed again, I will take the bus and meet you at the station.",
    "The old dog slept by the door and lifted his head whenever someone walked past the house.",
    "Most of the books in the shop had been bought from families who were moving away.",
    "He poured two cups of coffee, sat down at the kitchen table, and opened the letter from the bank.",
    "The teacher wrote the date on the board and waited for the class to settle down before she began.",
    "By the end of the week we had learned the names of all the streets between the harbour and the market.",
    "The mountain looks close from the village, but it takes most of a day to walk to the foot of it.",
    "My grandmother always said that a good soup needs time, patience, and more salt than you would expect.",
    "The committee met on Tuesday to discuss the budget, the new car park, and the repairs to the town hall.",
    "Every spring the river rises over the lower fields, and the farmers move their animals up to higher ground.",
    "Although the film received poor reviews when it came out, it has since found a large and loyal audience.",
    "The engineer explained that the bridge had been designed to move slightly in strong winds, which surprised most of the visitors.",
    "On clear nights you can see the lights of the fishing boats far out on the water, moving slowly along the horizon.",
    "She had meant to call him back that evening, but the day had been long and she fell asleep on the sofa with the television on.",
    "What time does the last ferry leave?",
    "Please put the boxes in the hall.",
    "That was the best meal we had all year!",
    "Do you know whether the library is open on Sundays?",
    "The results were published in March, and the authors have since corrected two small errors in the second table.",
    "Sound travels faster through water than through air, which is why whales can hear each other across great distances.",
    "Bees return to the hive and perform a short dance that tells the others where the flowers can be found.",
    "The company moved its offices to the edge of town last year, and many of the staff now drive to work instead of walking.",
    "He played the same three songs on the piano every evening, and after a while the neighbours began to hum along through the wall.",
    "Before you start the machine, check that the door is closed and that the water tank has been filled to the marked line.",
]
FILES = {
    "kokoro-pt-fp32": MODELS / "kokoro-v1_0.pth",
    "kokoro-onnx-fp32": PINNED / "onnx/model.onnx",
    "kokoro-onnx-fp16": MODELS / "kokoro-v1.0-onnx/onnx/model_fp16.onnx",
    "kokoro-onnx-int8": PINNED / "onnx/model_quantized.onnx",
}
LISTEN = ["The kettle clicked off just as the phone began to ring.", "Rain tapped against the window for most of the afternoon.", "The old dog slept by the door and lifted his head whenever someone walked past the house."]


class Cached:
    def __init__(self, cache: dict[str, str]) -> None:
        self.cache = cache

    def phonemize(self, text: str, lang_code: str) -> str:
        return self.cache[text]


def adapter_for(variant_id: str, cache: dict[str, str]) -> KokoroAdapter:
    meta = CATALOG_METADATA[variant_id]
    path = FILES[variant_id]
    variant = ModelVariant(id=variant_id, name=str(meta["name"]), format=meta["format"], precision=meta["precision"], size_bytes=path.stat().st_size, path=path, is_downloaded=True)
    adapter = KokoroAdapter(onnx_vocab_path=MODELS / "config.json", g2p=Cached(cache))
    adapter.load_model(variant, DeviceType.CPU)
    return adapter


def main() -> None:
    print("pinned", ONNX_REPO, ONNX_REVISION)
    for name in ("onnx/model.onnx", "onnx/model_quantized.onnx"):
        started = time.perf_counter()
        got = Path(hf_hub_download(repo_id=ONNX_REPO, filename=name, revision=ONNX_REVISION, local_dir=str(PINNED)))
        print(" ", name, f"{got.stat().st_size:,} B", round(time.perf_counter() - started, 1), "s", flush=True)

    activate_spacy_dir(MODELS)
    g2p = KokoroG2p(EspeakCliAdapter())
    cache: dict[str, str] = {s: g2p.phonemize(s, "a") for s in SENTENCES}
    british: dict[str, str] = {s: g2p.phonemize(s, "b") for s in SENTENCES[:20]}
    paragraphs = [" ".join(SENTENCES[i : i + 5]) for i in range(0, 40, 5)]
    for paragraph in paragraphs:
        for sentence in _sentences(paragraph):
            cache.setdefault(sentence, g2p.phonemize(sentence, "a"))
    print("sentences", len(SENTENCES), "tokens", min(len(v) for v in cache.values()), "to", max(len(v) for v in cache.values()), "| paragraphs", len(paragraphs), flush=True)

    print("\nvariant | voice | sentences failing | speech s | failing token counts")
    totals = {}
    for variant_id in FILES:
        adapter = adapter_for(variant_id, {**cache})
        for voice_id in ("af_heart", "am_michael", "af_bella"):
            voice = voice_config_for(voice_id)
            failed, samples = [], 0
            for sentence in SENTENCES:
                try:
                    samples += adapter.generate(sentence, voice, 1.0, lambda _f: None).size
                except ValidationError:
                    failed.append(len(cache[sentence]))
            totals[(variant_id, voice_id)] = samples
            print(f"{variant_id} | {voice_id} | {len(failed)}/{len(SENTENCES)} | {samples / RATE:.1f} | {failed}", flush=True)
        voice = voice_config_for("af_heart")
        failed = 0
        for paragraph in paragraphs:
            try:
                adapter.generate(paragraph, voice, 1.0, lambda _f: None)
            except ValidationError:
                failed += 1
        print(f"{variant_id} | af_heart paragraphs | {failed}/{len(paragraphs)} failing", flush=True)
        british_adapter = adapter_for(variant_id, {**british})
        voice = voice_config_for("bf_emma")
        failed = sum(1 for s in british if _fails(british_adapter, s, voice))
        print(f"{variant_id} | bf_emma | {failed}/{len(british)} failing", flush=True)

    print("\ntiming in a fresh process per variant, on sentences every variant finished")
    for variant_id in FILES:
        runs = []
        for _ in range(3):
            done = subprocess.run([sys.executable, __file__, "time", variant_id, json.dumps(cache, ensure_ascii=False)], capture_output=True, text=True, encoding="utf-8", errors="replace")
            if done.returncode:
                print("TIME FAILED", variant_id, done.stderr[-600:])
                continue
            runs.append(json.loads(done.stdout.strip().splitlines()[-1]))
        if runs:
            med = lambda k: statistics.median(r[k] for r in runs)  # noqa: E731
            print(f"{variant_id:18} file {FILES[variant_id].stat().st_size / 1e6:4.0f} MB | import {med('import_s'):.1f} s | load {med('load_s'):.2f} s | gen {med('gen_s'):.2f} s | speech {med('audio_s'):.2f} s | {med('audio_s') / med('gen_s'):.1f}x real | peak {max(r['peak_mb'] for r in runs):.0f} MB | all runs gen {[round(r['gen_s'], 2) for r in runs]}", flush=True)


def _fails(adapter: KokoroAdapter, sentence: str, voice) -> bool:
    try:
        adapter.generate(sentence, voice, 1.0, lambda _f: None)
    except ValidationError:
        return True
    return False


def timed(variant_id: str, cache_text: str) -> None:
    sys.path.insert(0, str(Path(__file__).parent))
    from tts_variant_compare import peak_mb

    cache = json.loads(cache_text)
    started = time.perf_counter()
    adapter = adapter_for(variant_id, cache)
    load = time.perf_counter() - started
    voice = voice_config_for("af_heart")
    gaps = np.zeros(int(RATE * 0.3), dtype=np.float32)
    pieces, times = [], []
    for attempt in range(3):
        started = time.perf_counter()
        made = [adapter.generate(sentence, voice, 1.0, lambda _f: None) for sentence in LISTEN]
        times.append(time.perf_counter() - started)
        if attempt == 0:
            pieces = made
    joined = np.concatenate([part for piece in pieces for part in (piece, gaps)])
    with wave.open(str(OUT / f"listen-{variant_id}.wav"), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes((joined * 32767).astype("<i2").tobytes())
    print(json.dumps({"import_s": 0.0, "load_s": load, "gen_s": statistics.median(times[1:]), "audio_s": sum(p.size for p in pieces) / RATE, "peak_mb": peak_mb()}))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "time":
        timed(sys.argv[2], sys.argv[3])
    else:
        main()
