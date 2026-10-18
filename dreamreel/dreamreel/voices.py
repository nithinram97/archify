"""Voices: turn dialogue into speech, in the character's own language.

A cast file says how a character sounds. The simple way is a voice name:

    voice = "en_US-amy-medium"              # a Piper voice (free, offline, runs on any computer)

or a table, for every other way of making a voice:

    [voice]
    language = "ta"                         # en, hi, ta, te, bn, mr, kn, ml, gu, pa, or, as, ur ...
    describe = "An old woman with a warm, slow, gentle voice"     # Indic Parler-TTS makes it
    # or copy someone's voice from a 5-10 second recording of them (IndicF5):
    sample = "audio/samples/ammamma.wav"
    sample_text = "what the recording says, word for word"
    # or a voice from Fish Audio (paid, needs FISH_API_KEY):
    fish = "<a Fish Audio voice id>"
    engine = "fish"                         # force one engine (otherwise dreamreel picks)
    speed = 1.0

The language is also worked out from the line itself: a line written in Tamil script is Tamil.

Engines, best first when several could speak a line:

    engine        what                                         runs
    indic_f5      copies a recorded voice; 11 Indian languages  your computer (slow without a
                  (AI4Bharat, MIT)                              graphics card) or a booster
    indic_parler  a voice described in words; 21 languages      same
                  (AI4Bharat, Apache-2.0)
    fish          Fish Audio (Drama 3 by default): acted,       Fish Audio's servers (paid)
                  emotional speech
    piper         ready-made voices: English, Hindi, Telugu,    any computer, offline, quick
                  Malayalam, Marathi, Bengali, Urdu, Nepali

Lines are rendered once and cached in the project's audio/voices folder, keyed by everything that
shapes the sound, so editing one line only re-voices that line. Without any engine the film still
works: mouths move from the words and the lines appear as subtitles.

Any other engine can be plugged in as a class, then chosen in film.toml (`voice_engine = "..."`)
or in a cast file (`engine = "..."` under [voice]):

    class MyTTS(dr.VoiceEngine):
        @classmethod
        def available(cls):
            return True
        def speak(self, text, voice, wav_path, **opts):     # write a 16-bit WAV file
            ...                                             # opts: language, describe, sample,
                                                            # sample_text, mood, speed, fish
"""
import array
import atexit
import hashlib
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
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
    "hi_IN-priyamvada-medium", "hi_IN-pratham-medium", "hi_IN-rohan-medium",
    "te_IN-maya-medium", "te_IN-padmavathi-medium", "te_IN-venkatesh-medium",
    "ml_IN-meera-medium", "ml_IN-arjun-medium", "mr_IN-google-medium", "bn_BD-google-medium",
    "ur_PK-aegis_female-medium", "ur_PK-fasih-medium", "ne_NP-chitwan-medium",
)

# language code: (name, its own name, a line to try a voice with)
LANGUAGES = {
    "en": ("English", "English", "Hi! This is my voice. Nice to meet you!"),
    "hi": ("Hindi", "हिन्दी", "नमस्ते! यह मेरी आवाज़ है। आपसे मिलकर ख़ुशी हुई!"),
    "ta": ("Tamil", "தமிழ்", "வணக்கம்! இது என் குரல். உங்களைச் சந்தித்ததில் மகிழ்ச்சி!"),
    "te": ("Telugu", "తెలుగు", "నమస్కారం! ఇది నా గొంతు. మిమ్మల్ని కలవడం సంతోషంగా ఉంది!"),
    "bn": ("Bengali", "বাংলা", "নমস্কার! এটা আমার গলা। আপনার সঙ্গে দেখা হয়ে ভালো লাগল!"),
    "mr": ("Marathi", "मराठी", "नमस्कार! हा माझा आवाज आहे. तुम्हाला भेटून आनंद झाला!"),
    "kn": ("Kannada", "ಕನ್ನಡ", "ನಮಸ್ಕಾರ! ಇದು ನನ್ನ ಧ್ವನಿ. ನಿಮ್ಮನ್ನು ಭೇಟಿಯಾಗಿ ಸಂತೋಷವಾಯಿತು!"),
    "ml": ("Malayalam", "മലയാളം", "നമസ്കാരം! ഇത് എന്റെ ശബ്ദമാണ്. നിങ്ങളെ കണ്ടതിൽ സന്തോഷം!"),
    "gu": ("Gujarati", "ગુજરાતી", "નમસ્તે! આ મારો અવાજ છે. તમને મળીને આનંદ થયો!"),
    "pa": ("Punjabi", "ਪੰਜਾਬੀ", "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਇਹ ਮੇਰੀ ਆਵਾਜ਼ ਹੈ। ਤੁਹਾਨੂੰ ਮਿਲ ਕੇ ਖ਼ੁਸ਼ੀ ਹੋਈ!"),
    "or": ("Odia", "ଓଡ଼ିଆ", "ନମସ୍କାର! ଏହା ମୋର ସ୍ୱର। ଆପଣଙ୍କୁ ଭେଟି ଖୁସି ଲାଗିଲା!"),
    "as": ("Assamese", "অসমীয়া", "নমস্কাৰ! এইটো মোৰ মাত। আপোনাক লগ পাই ভাল লাগিল!"),
    "ur": ("Urdu", "اردو", "السلام علیکم! یہ میری آواز ہے۔ آپ سے مل کر خوشی ہوئی!"),
    "ne": ("Nepali", "नेपाली", "नमस्ते! यो मेरो आवाज हो। तपाईंलाई भेटेर खुसी लाग्यो!"),
}
# the Piper voice a language starts with, when the cast file doesn't name one
PIPER_DEFAULT = {"en": DEFAULT_VOICE, "hi": "hi_IN-priyamvada-medium", "te": "te_IN-maya-medium",
                 "ml": "ml_IN-meera-medium", "mr": "mr_IN-google-medium", "bn": "bn_BD-google-medium",
                 "ur": "ur_PK-aegis_female-medium", "ne": "ne_NP-chitwan-medium"}
# Unicode blocks of the scripts of India: a line written in one says its language
SCRIPTS = ((0x0900, 0x097F, "hi"), (0x0980, 0x09FF, "bn"), (0x0A00, 0x0A7F, "pa"), (0x0A80, 0x0AFF, "gu"),
           (0x0B00, 0x0B7F, "or"), (0x0B80, 0x0BFF, "ta"), (0x0C00, 0x0C7F, "te"), (0x0C80, 0x0CFF, "kn"),
           (0x0D00, 0x0D7F, "ml"), (0x0600, 0x06FF, "ur"))
# languages that share a script: a voice set to one of these keeps it
SAME_SCRIPT = {"hi": {"hi", "mr", "ne"}, "bn": {"bn", "as"}}


def detect_language(text):
    """The language a line is written in, from its script (None for Latin: could be anything)."""
    counts = {}
    for ch in text:
        c = ord(ch)
        for lo, hi, lang in SCRIPTS:
            if lo <= c <= hi:
                counts[lang] = counts.get(lang, 0) + 1
    return max(counts, key=counts.get) if counts else None


class VoiceSpec:
    """How a character sounds: a cast file's `voice` (a name, or a table)."""
    FIELDS = ("name", "engine", "language", "describe", "sample", "sample_text", "fish", "speed")

    def __init__(self, value=None):
        if isinstance(value, dict):
            d = dict(value)
        elif value:
            d = {"name": str(value)}
        else:
            d = {}
        for f in self.FIELDS:
            setattr(self, f, d.get(f) or None)
        if self.name and not self.language:
            pre = self.name.split("_")[0].split("-")[0].lower()
            if pre in LANGUAGES:
                self.language = pre

    def language_for(self, line):
        """The line's language: what it's written in, unless the voice is set to a language that
        shares that script (Marathi and Hindi are both Devanagari)."""
        seen = detect_language(line)
        mine = (self.language or "").lower() or None
        if seen is None:
            return mine or "en"
        if mine and mine in SAME_SCRIPT.get(seen, {seen}):
            return mine
        return seen

    def key(self):
        return json.dumps({f: getattr(self, f) for f in self.FIELDS}, sort_keys=True, ensure_ascii=False)


class VoiceEngine(Plugin):
    """Turns a line of text into a WAV file in a given voice."""
    kind = "voice"
    abstract = True
    languages = None          # language codes it can speak (None: any)
    uses_mood = False         # the mood changes the sound (part of the cache key)
    setup = ""                # how to make it available, in a sentence

    @classmethod
    def available(cls):
        return True

    @classmethod
    def can(cls, spec, language):
        """Whether it can speak this voice in this language."""
        return cls.languages is None or language in cls.languages

    def speak(self, text, voice, wav_path, **opts):
        raise NotImplementedError

    @classmethod
    def describe_extra(cls):
        return {"available": bool(cls.available()), "languages": list(cls.languages or []),
                "setup": cls.setup}


# ---------------------------------------------------------------------- Piper
def _piper_available():
    try:
        import piper  # noqa: F401
        return True
    except ImportError:
        return shutil.which("piper") is not None


def piper_voice_file(voice):
    """The voice model, downloaded once (to a side folder first, so a broken download never stays)."""
    if voice.endswith(".onnx"):
        return voice
    model = os.path.join(VOICE_DIR, voice + ".onnx")
    if not (os.path.exists(model) and os.path.exists(model + ".json")):
        os.makedirs(VOICE_DIR, exist_ok=True)
        part = tempfile.mkdtemp(prefix=".download-", dir=VOICE_DIR)
        try:
            subprocess.run([sys.executable, "-m", "piper.download_voices", "--download-dir", part, voice],
                           check=True, capture_output=True)
            for fn in os.listdir(part):
                os.replace(os.path.join(part, fn), os.path.join(VOICE_DIR, fn))
        finally:
            shutil.rmtree(part, ignore_errors=True)
        if not (os.path.exists(model) and os.path.exists(model + ".json")):
            raise RuntimeError(f"Piper couldn't download the voice {voice!r} (check its name and the internet)")
    return model


class Piper(VoiceEngine):
    label = "Piper (ready-made)"
    description = "Free, offline voices: English, Hindi, Telugu, Malayalam, Marathi, Bengali, Urdu, Nepali"
    languages = tuple(PIPER_DEFAULT)
    setup = 'pip install piper-tts (or pip install "dreamreel[voices]")'

    @classmethod
    def available(cls):
        return _piper_available()

    @classmethod
    def can(cls, spec, language):
        if spec.name:
            return VoiceSpec(spec.name).language in (None, language) or language in SAME_SCRIPT.get(
                VoiceSpec(spec.name).language, ())
        return language in PIPER_DEFAULT and not spec.describe and not spec.sample and not spec.fish

    def speak(self, text, voice, wav_path, language="en", speed=None, **opts):
        voice = voice or PIPER_DEFAULT.get(language, DEFAULT_VOICE)
        model = piper_voice_file(voice)
        cmd = [sys.executable, "-m", "piper", "-m", model, "-f", wav_path]
        if speed:
            cmd += ["--length-scale", str(round(1.0 / float(speed), 3))]
        for attempt in (1, 2):
            try:
                subprocess.run(cmd + ["--", text], check=True, capture_output=True)
                return
            except subprocess.CalledProcessError as e:
                err = e.stderr or b""
                if attempt == 2 or not (b"Protobuf" in err or b"Unable to find voice" in err):
                    raise
                for fn in (model, model + ".json"):     # a damaged or missing download: fetch it again
                    if os.path.exists(fn):
                        os.remove(fn)
                piper_voice_file(voice)


def _piper(text, voice, wav_path):  # kept for the CLI's voice audition
    Piper().speak(text, voice, wav_path)


# ---------------------------------------------------------------------- AI voices on this computer
class _Worker:
    """A model kept loaded in a separate Python (speakers.py) while a film is made: loading takes
    a minute, each line then takes seconds. One per engine; closed when dreamreel exits."""
    _all = {}
    _lock = threading.Lock()

    @classmethod
    def get(cls, engine):
        with cls._lock:
            w = cls._all.get(engine)
            if w is None or w.proc.poll() is not None:
                w = cls._all[engine] = cls(engine)
            return w

    def __init__(self, engine):
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "speakers.py")  # needs no Blender
        self.proc = subprocess.Popen([sys.executable, script, engine], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, encoding="utf-8")
        self.log = []                        # the model's own messages (it loads noisily): the last few
        threading.Thread(target=self._drain, daemon=True).start()

    def _drain(self):
        for line in self.proc.stderr:
            self.log = (self.log + [line])[-20:]

    def run(self, job):
        self.proc.stdin.write(json.dumps(job, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()
        reply = self.proc.stdout.readline()
        if not reply:
            self.proc.wait(timeout=10)
            err = "".join(self.log)[-600:]
            raise RuntimeError(f"the voice model stopped: {err.strip() or 'no reason given'}")
        out = json.loads(reply)
        if out.get("error"):
            raise RuntimeError(out["error"])
        return out

    @classmethod
    def close_all(cls):
        for w in cls._all.values():
            try:
                w.proc.stdin.close()
                w.proc.wait(timeout=5)
            except Exception:
                w.proc.kill()
        cls._all.clear()


atexit.register(_Worker.close_all)


def _local_ready(engine):
    from . import speakers
    return speakers.ready(engine)


class _AIVoice(VoiceEngine):
    """A voice model run on this computer when it's set up here, else on a connected booster."""
    abstract = True

    @classmethod
    def available(cls):
        from . import boost
        return _local_ready(cls.name) or boost.can("voice." + cls.name)

    def speak(self, text, voice, wav_path, **opts):
        if _local_ready(self.name):
            _Worker.get(self.name).run({"text": text, "out": wav_path, **opts})
            return
        from . import boost
        b = boost.configured()
        files = {"sample": opts.pop("sample")} if opts.get("sample") else {}
        out = b.run("voice." + self.name, {"text": text, **opts}, files, os.path.dirname(wav_path) or ".",
                    timeout=900)
        os.replace(out["speech"], wav_path)


class IndicParler(_AIVoice):
    name = "indic_parler"
    label = "Indic Parler-TTS"
    description = "A voice described in words, in 21 Indian languages and English (AI4Bharat, Apache-2.0)"
    languages = ("en", "hi", "ta", "te", "bn", "mr", "kn", "ml", "gu", "pa", "or", "as", "ur", "ne")
    uses_mood = True
    setup = ("on a booster (dreamreel boost), or on this computer: pip install torch "
             "git+https://github.com/huggingface/parler-tts.git, accept the model's terms at "
             "huggingface.co/ai4bharat/indic-parler-tts and set HF_TOKEN")

    @classmethod
    def can(cls, spec, language):
        # a described voice; or any voice of a language with no ready-made one
        return (language in cls.languages and not spec.sample and not spec.fish
                and bool(spec.describe or (not spec.name and language not in PIPER_DEFAULT)))


class IndicF5(_AIVoice):
    name = "indic_f5"
    label = "IndicF5 (copies a voice)"
    description = "Copies a voice from a short recording, in 11 Indian languages (AI4Bharat, MIT)"
    languages = ("hi", "ta", "te", "bn", "mr", "kn", "ml", "gu", "pa", "or", "as")
    setup = ("on a booster (dreamreel boost), or on this computer: pip install torch transformers f5-tts, "
             "accept the model's terms at huggingface.co/ai4bharat/IndicF5 and set HF_TOKEN")

    @classmethod
    def can(cls, spec, language):
        return language in cls.languages and bool(spec.sample and spec.sample_text)


# ---------------------------------------------------------------------- Fish Audio
FISH_URL = "https://api.fish.audio"
# moods as Drama 3 stage directions (it reads plain words in [brackets] before a line)
FISH_DIRECTIONS = {"happy": "cheerful", "gleeful": "bursting with joy", "sad": "sad, quiet", "crying": "crying",
                   "angry": "angry", "furious": "furious, shouting", "scared": "frightened", "terrified": "terrified",
                   "surprised": "surprised", "shocked": "shocked", "nervous": "nervous, hesitant",
                   "sleepy": "sleepy, drowsy", "bored": "bored", "loving": "tender, loving",
                   "proud": "proud", "confused": "confused", "excited": "excited", "suspicious": "suspicious",
                   "disgusted": "disgusted", "determined": "determined", "embarrassed": "embarrassed"}


class Fish(VoiceEngine):
    label = "Fish Audio"
    description = "Fish Audio: acted, emotional voices (Drama 3); paid, needs FISH_API_KEY"
    uses_mood = True
    setup = "set FISH_API_KEY (fish.audio, then API keys); voices are ids from fish.audio's voice library"

    @classmethod
    def available(cls):
        return bool(os.environ.get("FISH_API_KEY"))

    @classmethod
    def can(cls, spec, language):
        return bool(spec.fish) or spec.engine == "fish"

    def speak(self, text, voice, wav_path, fish=None, mood=None, speed=None, language=None, **opts):
        from . import project
        p = project.current()
        model = ((p.film.get("fish_model") if p else None) or os.environ.get("DREAMREEL_FISH_MODEL") or "drama-3")
        direction = FISH_DIRECTIONS.get(mood or "")
        body = {"text": f"[{direction}] {text}" if direction and model == "drama-3" else text,
                "format": "wav", "sample_rate": 44100, "normalize": True}
        if fish:
            body["reference_id"] = fish
        if speed:
            body["prosody"] = {"speed": max(0.5, min(2.0, float(speed)))}
        if language:
            body["language"] = language
        url = os.environ.get("DREAMREEL_FISH_URL", FISH_URL).rstrip("/") + "/v1/tts"
        req = urllib.request.Request(url, data=json.dumps(body, ensure_ascii=False).encode(), headers={
            "Authorization": f"Bearer {os.environ.get('FISH_API_KEY', '')}", "Content-Type": "application/json",
            "model": model, "User-Agent": "dreamreel"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = r.read()
        except urllib.error.HTTPError as e:
            why = {401: "the API key was refused", 402: "the account is out of credit",
                   503: "Fish Audio is busy; try again soon"}.get(e.code, e.read().decode(errors="replace")[:200])
            raise RuntimeError(f"Fish Audio: {e.code} {why}")
        _write_wav16(data, wav_path)


def _write_wav16(data, wav_path):
    """Save a WAV from a service as 16-bit (what the editor and lip sync read)."""
    tmp = wav_path + ".in.wav"
    with open(tmp, "wb") as f:
        f.write(data)
    try:
        with wave.open(tmp, "rb") as w:
            if w.getsampwidth() == 2:
                os.replace(tmp, wav_path)
                return
            rate, ch, width, raw = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.readframes(w.getnframes())
        samples = array.array("h")
        for i in range(0, len(raw), width):
            v = int.from_bytes(raw[i:i + width], "little", signed=width > 1)
            samples.append(max(-32768, min(32767, (v - 128) * 256 if width == 1 else v >> (8 * (width - 2)))))
        with wave.open(wav_path, "wb") as w:
            w.setnchannels(ch)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(samples.tobytes())
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# ---------------------------------------------------------------------- picking an engine
ORDER = ("indic_f5", "indic_parler", "fish", "piper")


def pick_engine(name="auto"):
    """The film's default engine: a name from film.toml, or the first available one."""
    if name and name != "auto":
        return name if plugins.get("voice", name).available() else None
    for n, cls in plugins.registry("voice").items():
        if cls.available():
            return n
    return None


def engine_for(spec, language, default="auto", loose=True):
    """The engine to speak this voice in this language, or None. A voice's own `engine` wins, then
    the film's `voice_engine`; otherwise the first one that can (copied voice, described voice, Fish,
    Piper), then any added engine."""
    for name in (spec.engine, default if default not in (None, "auto") else None):
        if name:
            try:
                cls = plugins.get("voice", name)
            except ValueError:
                continue
            if cls.available():
                return name
    reg = plugins.registry("voice")
    names = [n for n in ORDER if n in reg] + [n for n in reg if n not in ORDER]
    for n in names:
        cls = reg[n]
        if cls.available() and cls.can(spec, language):
            return n
    if not loose:
        return None
    # nothing made for this voice: any engine that speaks the language in a voice of its own
    for n in ("indic_parler", "piper"):
        cls = reg.get(n)
        if cls and cls.available() and language in (cls.languages or ()) and (n != "piper" or language in PIPER_DEFAULT):
            return n
    return None


def status():
    """Every engine: available now, and what it speaks (for the studio and `dreamreel voices`)."""
    return {n: cls.describe() for n, cls in plugins.registry("voice").items()}


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

    def letters(self, download=True):
        """[(start, Rhubarb mouth shape letter)] from the sounds of the line, or None."""
        from . import lipsync
        return lipsync.letters(self.path, self.text, self.english, download)

    def face_frames(self, download=True):
        """[(time, {ARKit shape: weight})] from an AI reading the whole face in the voice, or None."""
        from . import lipsync
        return lipsync.face_frames(self.path, download)

    def face(self, download=True):
        """[(start, (open, round, wide))] from an AI reading the face in the voice, or None."""
        from . import lipsync
        return lipsync.face_cues(self.path, download)

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


def _accepts_opts(fn):
    try:
        return any(p.kind == p.VAR_KEYWORD for p in inspect.signature(fn).parameters.values())
    except (TypeError, ValueError):
        return False


class Voices:
    def __init__(self, project_dir=None, engine="auto", enabled=True, lipsync="sounds"):
        self.root = project_dir
        self.dir = os.path.join(project_dir, "audio", "voices") if project_dir else None
        self.default = engine or "auto"
        self.enabled = enabled
        self.engine = pick_engine(engine) if enabled else None   # the film's engine, if any can run
        self.lipsync = lipsync
        self.failed = set()
        self.warned = set()

    def _warn(self, msg):
        if msg not in self.warned:
            self.warned.add(msg)
            print(f"[dreamreel] {msg}")

    def speak(self, character, line, mood=None):
        """Return a Speech for the line, or None to fall back to text-driven mouths."""
        if not self.enabled or self.dir is None:
            return None
        spec = VoiceSpec(character.voice)
        language = spec.language_for(line)
        if self.engine is None and self.default not in (None, "auto"):
            return None                      # the film asked for an engine that can't run here
        name = (self.engine if self.default not in (None, "auto") and not spec.engine
                else engine_for(spec, language, self.default, loose=False))
        lang_name = LANGUAGES.get(language, (language,))[0]
        if name is None:
            # the voice asked for can't be made here yet: another voice of the language meanwhile
            name = engine_for(VoiceSpec({"language": language}), language, self.default)
            if name is not None:
                self._warn(f"{character.name}'s voice needs a voice engine that isn't set up (see `dreamreel "
                           f"voices`); using a {'ready-made ' if name == 'piper' else ''}{lang_name} voice for now")
                spec = VoiceSpec({"language": language, "speed": spec.speed})
        if name is None or name in self.failed:
            if name is None:
                self._warn(f"no voice engine here speaks {lang_name} for {character.name}; see `dreamreel voices`")
            return None
        cls = plugins.get("voice", name)
        sample = spec.sample
        if sample and self.root and not os.path.isabs(sample):
            sample = os.path.join(self.root, sample)
        opts = {"language": language, "describe": spec.describe, "sample": sample, "sample_text": spec.sample_text,
                "fish": spec.fish, "speed": spec.speed, "mood": mood if cls.uses_mood else None}
        voice = spec.name or (DEFAULT_VOICE if name == "piper" and language == "en" else None)
        if name == "piper" and voice and not cls.can(VoiceSpec(voice), language):
            voice = None                     # an English voice can't read Tamil: the language's own
        h = hashlib.sha1(f"{name}|{voice}|{spec.key()}|{opts['mood']}|{language}|{line}".encode()).hexdigest()[:16]
        os.makedirs(self.dir, exist_ok=True)
        path = os.path.join(self.dir, f"{character.name.lower()}-{h}.wav")
        if not os.path.exists(path):
            tmp = f"{path}.{os.getpid()}.part.wav"  # write aside, then rename: never read half a file
            try:
                eng = cls()
                if _accepts_opts(eng.speak):
                    eng.speak(line, voice, tmp, **{k: v for k, v in opts.items() if v is not None})
                else:
                    eng.speak(line, voice or DEFAULT_VOICE, tmp)
                os.replace(tmp, path)
            except Exception as e:  # never stop a render for a voice problem
                self._warn(f"voice engine {name!r} failed ({e}); using silent mouths")
                self.failed.add(name)
                return None
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)
        return Speech(path, line, language == "en")
