"""Voices: turn dialogue into speech with a local, free text-to-speech engine.

dreamreel uses Piper (https://github.com/OHF-Voice/piper1-gpl) when it is installed:

    pip install piper-tts
    dreamreel voices                      # list the voices cast members can use
    # in cast/mia.toml:  voice = "en_US-amy-medium"

Lines are rendered once and cached in the project's audio/voices folder, keyed by voice + text,
so editing one line only re-voices that line. Without Piper the film still works: mouths move
from the words and the lines appear as subtitles.

Any other engine can be plugged in: write a function (text, voice, wav_path) -> None and pass it
to `register_engine`.
"""
import array
import hashlib
import os
import shutil
import subprocess
import sys
import wave

ENGINES = {}
VOICE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "dreamreel", "voices")
DEFAULT_VOICE = "en_US-lessac-medium"


def register_engine(name, fn):
    ENGINES[name] = fn


def _piper_available():
    try:
        import piper  # noqa: F401
        return True
    except ImportError:
        return shutil.which("piper") is not None


def _piper(text, voice, wav_path):
    model = voice if voice.endswith(".onnx") else os.path.join(VOICE_DIR, voice + ".onnx")
    if not os.path.exists(model):
        os.makedirs(VOICE_DIR, exist_ok=True)
        subprocess.run([sys.executable, "-m", "piper.download_voices", "--download-dir", VOICE_DIR, voice],
                       check=True, capture_output=True)
    subprocess.run([sys.executable, "-m", "piper", "-m", model, "-f", wav_path, "--", text],
                   check=True, capture_output=True)


register_engine("piper", _piper)


class Speech:
    """A rendered line: a wav file, its length, and its loudness over time (for the mouth)."""

    def __init__(self, path):
        self.path = path
        with wave.open(path, "rb") as w:
            self.rate = w.getframerate()
            ch = w.getnchannels()
            width = w.getsampwidth()
            raw = w.readframes(w.getnframes())
        if width != 2:
            raise ValueError(f"{path}: expected 16-bit audio")
        samples = array.array("h", raw)
        if ch > 1:
            samples = samples[::ch]
        self.samples = samples
        self.duration = len(samples) / self.rate

    def envelope(self, step):
        """Loudness (0-1) every `step` seconds."""
        n = max(1, int(self.rate * step))
        peak = max(1, max((abs(s) for s in self.samples), default=1))
        out = []
        for i in range(0, len(self.samples), n):
            chunk = self.samples[i:i + n]
            rms = (sum(s * s for s in chunk) / max(1, len(chunk))) ** 0.5
            out.append(min(1.0, rms / peak * 2.2))
        return out


class Voices:
    def __init__(self, project_dir=None, engine="auto", enabled=True):
        self.dir = os.path.join(project_dir, "audio", "voices") if project_dir else None
        if engine == "auto":
            engine = "piper" if _piper_available() else None
        self.engine = engine if enabled else None
        self.warned = False

    def speak(self, character, line):
        """Return a Speech for the line, or None to fall back to text-driven mouths."""
        if self.engine is None or self.dir is None:
            return None
        voice = character.voice or DEFAULT_VOICE
        h = hashlib.sha1(f"{self.engine}|{voice}|{line}".encode()).hexdigest()[:16]
        os.makedirs(self.dir, exist_ok=True)
        path = os.path.join(self.dir, f"{character.name.lower()}-{h}.wav")
        if not os.path.exists(path):
            try:
                ENGINES[self.engine](line, voice, path)
            except Exception as e:  # never stop a render for a voice problem
                if not self.warned:
                    print(f"[dreamreel] voice engine {self.engine!r} failed ({e}); using silent mouths")
                    self.warned = True
                self.engine = None
                return None
        return Speech(path)
