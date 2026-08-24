import soundfile as sf
import numpy as np
import sys
from faster_whisper import WhisperModel

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="backslashreplace")

samples = [
    "vi_000.wav",
    "vi_001.wav",
    "en_000.wav",
    "en_001.wav",
]

model = WhisperModel("d:/TailieuNPKH/classbridge/backend/ai-service/whisper-large-v3-turbo-ct2", device="cuda", compute_type="float16")

for name in samples:
    path = f"d:/TailieuNPKH/classbridge/data/audio/local/{name}"
    data, samplerate = sf.read(path)
    segments, info = model.transcribe(data.astype(np.float32), language=None, beam_size=1, condition_on_previous_text=False)
    print(f"\n--- {name} (sr={samplerate}, size={data.size}, peak={np.max(np.abs(data)):.3f}, detected_lang={info.language}, prob={info.language_probability:.2f}) ---")
    for s in segments:
        print(f"  segment: text='{s.text}', logprob={s.avg_logprob:.2f}, no_speech={s.no_speech_prob:.2f}, comp_ratio={s.compression_ratio:.2f}")
