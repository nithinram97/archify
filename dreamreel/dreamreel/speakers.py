"""AI voice models, run in their own Python process (voices._Worker starts one per engine), or on a
booster (boost.py). A model is loaded once and then speaks line after line:

    python dreamreel/speakers.py indic_parler     # reads one JSON job per line on stdin:
    {"text": "...", "out": "line.wav", "language": "ta", "describe": "...", "mood": "sad"}
                                                  # answers {"ok": true} or {"error": "..."}

Models download from Hugging Face on first use. AI4Bharat's models ask you to accept their terms on
the model's page first, then to set HF_TOKEN (a free read token from huggingface.co, Settings,
Access tokens).
"""
import importlib.util
import json
import math
import os
import sys
import wave

MODELS = {"indic_parler": os.environ.get("DREAMREEL_PARLER_MODEL") or "ai4bharat/indic-parler-tts",
          "indic_f5": os.environ.get("DREAMREEL_F5_MODEL") or "ai4bharat/IndicF5"}
NEEDS = {"indic_parler": ("torch", "parler_tts", "transformers"), "indic_f5": ("torch", "transformers", "f5_tts")}
_loaded = {}

# a few of the speakers Indic Parler-TTS was trained on, per language: naming one keeps a character's
# voice the same from line to line (a description alone can drift)
PARLER_SPEAKERS = {
    "en": ("Thoma", "Mary"), "hi": ("Rohit", "Divya"), "ta": ("Jaya", "Kavitha"), "te": ("Prakash", "Lalitha"),
    "bn": ("Arjun", "Aditi"), "mr": ("Sanjay", "Sunita"), "kn": ("Suresh", "Anu"), "ml": ("Harish", "Anjali"),
    "gu": ("Yash", "Neha"), "pa": ("Divjot", "Gurpreet"), "or": ("Manas", "Debjani"), "as": ("Amit", "Sita"),
    "ur": ("Amit", "Sita"), "ne": ("Amrita",),
}
MOOD_WORDS = {"happy": "cheerful", "gleeful": "very happy, excited", "sad": "sad, slow", "crying": "tearful, sobbing",
              "angry": "angry", "furious": "furious, loud", "scared": "frightened, shaky", "terrified": "terrified",
              "surprised": "surprised", "shocked": "shocked", "nervous": "nervous, hesitant", "sleepy": "sleepy, slow",
              "bored": "flat, bored", "loving": "warm, tender", "proud": "proud, confident", "excited": "excited, fast"}


def ready(engine):
    """Whether this computer can run the engine's model: its Python packages are installed, and the
    model is downloaded or a Hugging Face token is set to download it."""
    if engine not in MODELS:
        return engine == "tone" and bool(os.environ.get("DREAMREEL_TEST_SPEAKER"))
    if any(importlib.util.find_spec(m) is None for m in NEEDS[engine]):
        return False
    hub = os.environ.get("HF_HUB_CACHE") or os.path.join(
        os.environ.get("HF_HOME", os.path.join(os.path.expanduser("~"), ".cache", "huggingface")), "hub")
    cached = os.path.isdir(os.path.join(hub, "models--" + MODELS[engine].replace("/", "--")))
    return cached or bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN"))


def describe(job):
    """Indic Parler-TTS's caption for a line: the cast file's description, else a clear voice, plus
    the mood and pace."""
    lang = job.get("language") or "en"
    text = (job.get("describe") or "").strip()
    if not text:
        name = PARLER_SPEAKERS.get(lang, ("Divya",))[-1]
        text = f"{name} speaks with a clear, natural voice at a moderate pace."
    mood = MOOD_WORDS.get(job.get("mood") or "")
    if mood:
        text += f" The voice sounds {mood}."
    speed = float(job.get("speed") or 1.0)
    if abs(speed - 1.0) > 0.1:
        text += " The speech is fast." if speed > 1 else " The speech is slow."
    return text + " The recording is very high quality with no background noise."


def write_wav(path, samples, rate):
    """Float samples (-1..1) as a 16-bit mono WAV."""
    import array
    pcm = array.array("h", (max(-32767, min(32767, int(float(s) * 32767))) for s in samples))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(rate))
        w.writeframes(pcm.tobytes())


def _device():
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def speak_parler(job):
    if "parler" not in _loaded:
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer
        dev = _device()
        model = ParlerTTSForConditionalGeneration.from_pretrained(MODELS["indic_parler"]).to(dev)
        _loaded["parler"] = (model, AutoTokenizer.from_pretrained(MODELS["indic_parler"]),
                             AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path), dev)
    model, tok, desc_tok, dev = _loaded["parler"]
    d = desc_tok(describe(job), return_tensors="pt").to(dev)
    p = tok(job["text"], return_tensors="pt").to(dev)
    audio = model.generate(input_ids=d.input_ids, attention_mask=d.attention_mask,
                           prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask)
    write_wav(job["out"], audio.cpu().numpy().squeeze(), model.config.sampling_rate)


def speak_f5(job):
    if not job.get("sample") or not job.get("sample_text"):
        raise ValueError("IndicF5 copies a voice: give the voice a sample recording and what it says (sample_text)")
    if "f5" not in _loaded:
        from transformers import AutoModel
        _loaded["f5"] = AutoModel.from_pretrained(MODELS["indic_f5"], trust_remote_code=True)
    import numpy as np
    audio = _loaded["f5"](job["text"], ref_audio_path=job["sample"], ref_text=job["sample_text"])
    audio = np.asarray(audio)
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0
    write_wav(job["out"], audio.squeeze(), 24000)


def speak_tone(job):
    """A stand-in model for tests: a hum as long as the words."""
    rate, n = 16000, max(1, len(job["text"].split()))
    write_wav(job["out"], (0.3 * math.sin(2 * math.pi * 220 * i / rate) * (0.5 + 0.5 * math.sin(i / 900))
                           for i in range(int(rate * 0.3 * n))), rate)


SPEAK = {"indic_parler": speak_parler, "indic_f5": speak_f5, "tone": speak_tone}


def serve(engine, stdin=sys.stdin, stdout=sys.stdout):
    real_out = stdout
    for line in stdin:
        if not line.strip():
            continue
        try:
            job = json.loads(line)
            sys.stdout = sys.stderr          # models print while loading: keep the answers channel clean
            SPEAK[engine](job)
            reply = {"ok": True}
        except Exception as e:
            reply = {"error": f"{type(e).__name__}: {e}"}
        finally:
            sys.stdout = real_out
        real_out.write(json.dumps(reply) + "\n")
        real_out.flush()


if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    serve(sys.argv[1])
