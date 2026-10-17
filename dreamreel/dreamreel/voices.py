"""Voices: turn dialogue into speech with a local, free text-to-speech engine.

dreamreel uses Piper (https://github.com/OHF-Voice/piper1-gpl) when it is installed:

    pip install piper-tts
    dreamreel voices                      # list the voices cast members can use
    # in cast/mia.toml:  voice = "en_US-amy-medium"

Lines are rendered once and cached in the project's audio/voices folder, keyed by voice + text,
so editing one line only re-voices that line. Without Piper the film still works: mouths move
from the words and the lines appear as subtitles.

Any other engine can be plugged in as a class, then chosen in film.toml with `voice_engine = "..."`:

    class MyTTS(dr.VoiceEngine):
        @classmethod
        def available(cls):
            return True
        def speak(self, text, voice, wav_path):     # write a 16-bit WAV file
            ...
"""
import array
import hashlib
import os
import shutil
import subprocess
import sys
import wave

from .plugins import Plugin
from . import plugins

VOICE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "dreamreel", "voices")
DEFAULT_VOICE = "en_US-lessac-medium"
SUGGESTED = (  # a few good Piper voices; hundreds more at https://rhasspy.github.io/piper-samples/
    "en_US-lessac-medium", "en_US-amy-medium", "en_US-ryan-medium", "en_US-joe-medium",
    "en_US-kristin-medium", "en_US-hfc_female-medium", "en_US-hfc_male-medium", "en_US-kathleen-low",
    "en_GB-alan-medium", "en_GB-alba-medium", "en_GB-cori-medium", "en_GB-jenny_dioco-medium",
    "en_GB-northern_english_male-medium", "en_GB-southern_english_female-low",
)


class VoiceEngine(Plugin):
    """Turns a line of text into a WAV file in a given voice."""
    kind = "voice"
    abstract = True

    @classmethod
    def available(cls):
        return True

    def speak(self, text, voice, wav_path):
        raise NotImplementedError


def _piper_available():
    try:
        import piper  # noqa: F401
        return True
    except ImportError:
        return shutil.which("piper") is not None


class Piper(VoiceEngine):
    description = "Free, offline voices (pip install piper-tts)"

    @classmethod
    def available(cls):
        return _piper_available()

    def speak(self, text, voice, wav_path):
        model = voice if voice.endswith(".onnx") else os.path.join(VOICE_DIR, voice + ".onnx")
        if not os.path.exists(model):
            os.makedirs(VOICE_DIR, exist_ok=True)
            subprocess.run([sys.executable, "-m", "piper.download_voices", "--download-dir", VOICE_DIR, voice],
                           check=True, capture_output=True)
        subprocess.run([sys.executable, "-m", "piper", "-m", model, "-f", wav_path, "--", text],
                       check=True, capture_output=True)


def _piper(text, voice, wav_path):  # kept for the CLI's voice audition
    Piper().speak(text, voice, wav_path)


def pick_engine(name="auto"):
    """The engine to use: a name from film.toml, or the first available one."""
    if name and name != "auto":
        return name if plugins.get("voice", name).available() else None
    for n, cls in plugins.registry("voice").items():
        if cls.available():
            return n
    return None


class Speech:
    """A rendered line: a wav file, its length, its loudness over time and the mouth shapes of its
    sounds (for the mouth)."""

    def __init__(self, path, text=None, english=True):
        self.path, self.text, self.english = path, text, english
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

    def shapes(self, download=True):
        """[(start, (open, round, wide))] from the sounds of the line, or None (see lipsync.py)."""
        from . import lipsync
        return lipsync.cues(self.path, self.text, self.english, download)

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
    def __init__(self, project_dir=None, engine="auto", enabled=True, lipsync="sounds"):
        self.dir = os.path.join(project_dir, "audio", "voices") if project_dir else None
        self.engine = pick_engine(engine) if enabled else None
        self.lipsync = lipsync
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
            tmp = f"{path}.{os.getpid()}.part.wav"  # write aside, then rename: never read half a file
            try:
                plugins.get("voice", self.engine)().speak(line, voice, tmp)
                os.replace(tmp, path)
            except Exception as e:  # never stop a render for a voice problem
                if not self.warned:
                    print(f"[dreamreel] voice engine {self.engine!r} failed ({e}); using silent mouths")
                    self.warned = True
                self.engine = None
                return None
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)
        english = voice.lower().startswith("en")
        return Speech(path, line, english)
