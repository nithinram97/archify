"""Voices in every language: the language is read from the script, each voice finds an engine that
can speak it (with a ready-made voice of the language meanwhile), AI models run in a worker process,
Fish Audio is called properly (against a stand-in server), keys stay out of film folders, and
subtitles in Indian scripts are shaped.

    python tests/test_voices.py
"""
import http.server
import json
import os
import shutil
import stat
import sys
import tempfile
import threading
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import dreamreel as dr  # noqa: E402
from dreamreel import fonts, lipsync, plugins, userkeys, voices  # noqa: E402
from dreamreel.voices import VoiceSpec  # noqa: E402


class Who:
    def __init__(self, name, voice=None):
        self.name, self.voice = name, voice


def wav_bytes(seconds=0.5, rate=22050, width=2):
    import io
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(width)
        w.setframerate(rate)
        w.writeframes(b"\x10\x20\x30"[:width] * int(rate * seconds))
    return buf.getvalue()


def languages():
    assert voices.detect_language("नमस्ते दादी!") == "hi"
    assert voices.detect_language("வணக்கம் பாட்டி") == "ta"
    assert voices.detect_language("ನಮಸ್ಕಾರ") == "kn"
    assert voices.detect_language("السلام علیکم") == "ur"
    assert voices.detect_language("Hello there") is None
    assert voices.detect_language("Mia: नमस्ते! Hello!") == "hi", "the Indian script wins over a name"
    assert VoiceSpec("hi_IN-rohan-medium").language == "hi"
    assert VoiceSpec({"language": "mr"}).language_for("नमस्कार! हा माझा आवाज आहे.") == "mr", "Marathi shares Devanagari"
    assert VoiceSpec({"language": "hi"}).language_for("வணக்கம்") == "ta", "a Tamil line is Tamil"
    assert VoiceSpec(None).language_for("Hello") == "en"
    assert VoiceSpec("en_US-amy-medium").key() != VoiceSpec({"name": "en_US-amy-medium", "speed": 1.2}).key()


def choosing():
    reg = plugins.registry("voice")
    saved = {n: reg[n].available for n in ("indic_parler", "indic_f5", "fish", "piper")}
    try:
        for n in saved:
            reg[n].available = classmethod(lambda cls: True)
        assert voices.engine_for(VoiceSpec("en_US-amy-medium"), "en") == "piper"
        assert voices.engine_for(VoiceSpec({"language": "ta", "describe": "a warm voice"}), "ta") == "indic_parler"
        assert voices.engine_for(VoiceSpec({"sample": "a.wav", "sample_text": "x"}), "ta") == "indic_f5"
        assert voices.engine_for(VoiceSpec({"fish": "abc"}), "en") == "fish"
        assert voices.engine_for(VoiceSpec({"language": "ta"}), "ta") == "indic_parler", "no Piper Tamil voice"
        assert voices.engine_for(VoiceSpec({"engine": "fish"}), "hi") == "fish", "the voice's own engine wins"
        assert voices.engine_for(VoiceSpec({"language": "hi"}), "hi", default="indic_parler") == "indic_parler"
        reg["indic_parler"].available = classmethod(lambda cls: False)
        reg["indic_f5"].available = classmethod(lambda cls: False)
        reg["fish"].available = classmethod(lambda cls: False)
        assert voices.engine_for(VoiceSpec({"language": "ta"}), "ta") is None
    finally:
        for n, fn in saved.items():
            reg[n].available = fn


def worker(tmp):
    """AI voice models run in a separate Python that stays loaded: here a stand-in model."""
    os.environ["DREAMREEL_TEST_SPEAKER"] = "1"

    class Hum(voices.VoiceEngine):
        name = "test_hum"
        languages = ("ta",)

        def speak(self, text, voice, wav_path, **opts):
            assert opts["language"] == "ta" and opts["describe"] == "a calm man", opts
            voices._Worker.get("tone").run({"text": text, "out": wav_path, **opts})
    try:
        vs = voices.Voices(tmp)
        who = Who("Arun", {"language": "ta", "describe": "a calm man", "engine": "test_hum"})
        sp = vs.speak(who, "வணக்கம் பாட்டி, எப்படி இருக்கீங்க?")
        assert sp is not None and sp.duration > 0.5 and not sp.english, sp
        again = vs.speak(who, "வணக்கம் பாட்டி, எப்படி இருக்கீங்க?")
        assert again.path == sp.path, "cached"
        assert len(voices._Worker._all) == 1
        first = voices._Worker._all["tone"].proc.pid
        vs.speak(who, "இன்னொரு வரி")
        assert voices._Worker._all["tone"].proc.pid == first, "the model stays loaded between lines"
        bad = voices._Worker.get("tone")
        try:
            bad.run({"text": "x"})            # no "out": the worker reports the error, and lives on
            raise AssertionError("expected an error")
        except RuntimeError as e:
            assert "out" in str(e)
        assert bad.proc.poll() is None
    finally:
        voices._Worker.close_all()
        del plugins._REGISTRY["voice"]["test_hum"]
        os.environ.pop("DREAMREEL_TEST_SPEAKER", None)


class FishServer(http.server.BaseHTTPRequestHandler):
    seen = []

    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FishServer.seen.append(({k.lower(): v for k, v in self.headers.items()}, body))
        if self.headers.get("Authorization") != "Bearer fish-key":
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"status":401,"message":"bad key"}')
            return
        data = wav_bytes(0.8, 44100, width=3)       # 24-bit: dreamreel converts it to 16-bit
        self.send_response(200)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def fish(tmp):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FishServer)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    os.environ["DREAMREEL_FISH_URL"] = f"http://127.0.0.1:{srv.server_address[1]}"
    os.environ["FISH_API_KEY"] = "fish-key"
    try:
        assert voices.Fish.available()
        vs = voices.Voices(tmp)
        sp = vs.speak(Who("Gran", {"fish": "voice-123"}), "I'm fine. Really.", mood="sad")
        assert sp is not None and abs(sp.duration - 0.8) < 0.05, sp and sp.duration
        headers, body = FishServer.seen[-1]
        assert headers["model"] == "drama-3" and body["reference_id"] == "voice-123", (headers, body)
        assert body["text"].startswith("[sad, quiet] ") and body["format"] == "wav", body
        same = vs.speak(Who("Gran", {"fish": "voice-123"}), "I'm fine. Really.", mood="happy")
        assert same.path != sp.path, "the mood changes an acted line"
        os.environ["FISH_API_KEY"] = "wrong"
        vs2 = voices.Voices(tmp)
        assert vs2.speak(Who("Gran", {"fish": "voice-123"}), "Another line.") is None, "a refused key: silent mouths"
        assert any("refused" in w for w in vs2.warned), vs2.warned
    finally:
        srv.shutdown()
        os.environ.pop("DREAMREEL_FISH_URL", None)
        os.environ.pop("FISH_API_KEY", None)


def piper(tmp):
    if not voices._piper_available():
        print("  (Piper not installed: skipping real voices)")
        return
    vs = voices.Voices(tmp)
    sp = vs.speak(Who("Dadi", "hi_IN-priyamvada-medium"), "नमस्ते! देखो, चाँद नीला है।")
    assert sp is not None and sp.duration > 1 and not sp.english
    # a described Hindi voice with no AI voice model here: a ready-made Hindi voice speaks meanwhile
    reg = plugins.registry("voice")
    saved = reg["indic_parler"].available
    reg["indic_parler"].available = classmethod(lambda cls: False)
    try:
        vs2 = voices.Voices(tmp)
        sp2 = vs2.speak(Who("Nani", {"language": "hi", "describe": "an old woman"}), "बेटा, खाना खा लो।")
        assert sp2 is not None and any("ready-made Hindi" in w for w in vs2.warned), vs2.warned
        # Tamil has no ready-made voice: subtitles only, with a clear message
        assert vs2.speak(Who("Paati", {"language": "ta"}), "வணக்கம்") is None
        assert any("Tamil" in w for w in vs2.warned)
    finally:
        reg["indic_parler"].available = saved
    if lipsync.available():
        cues = sp.shapes()
        assert cues and any(o < 0.05 and w > 0 for _, (o, r, w) in cues), "'namaste' closes the lips on the m"


def keys(tmp):
    os.environ["XDG_CONFIG_HOME"] = os.path.join(tmp, "config")
    os.environ.pop("FISH_API_KEY", None)
    try:
        assert not userkeys.status()["FISH_API_KEY"]["set"]
        userkeys.set_key("FISH_API_KEY", " abc ")
        assert os.environ["FISH_API_KEY"] == "abc"
        st = userkeys.status()["FISH_API_KEY"]
        assert st["set"] and st["from"] == "saved" and "abc" not in json.dumps(userkeys.status())
        mode = stat.S_IMODE(os.stat(userkeys.path()).st_mode)
        assert mode == 0o600, oct(mode)
        userkeys.set_key("FISH_API_KEY", "")
        assert "FISH_API_KEY" not in os.environ and not userkeys.status()["FISH_API_KEY"]["set"]
        try:
            userkeys.set_key("PATH", "x")
            raise AssertionError("only known keys")
        except ValueError:
            pass
    finally:
        os.environ.pop("XDG_CONFIG_HOME", None)


def subtitles():
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("  (Pillow not installed: skipping shaped subtitles)")
        return
    from PIL import Image
    assert fonts.needs_shaping("नमस्ते") and fonts.needs_shaping("ਸਤ ਸ੍ਰੀ") and not fonts.needs_shaping("Hello!")
    assert [f for f, _ in fonts._runs("Mia: नमस्ते! 2")] == ["NotoSans", "NotoSansDevanagari", "NotoSans"]
    try:
        path = fonts.text_image("வணக்கம் பாட்டி! நிலா நீலம்.", 640, 360)
    except OSError as e:
        print(f"  (couldn't download a font: {e}; skipping)")
        return
    im = Image.open(path)
    assert im.size == (640, 360) and im.mode == "RGBA"
    box = im.getbbox()
    assert box and box[1] > 250 and box[3] <= 360 - 20, ("a subtitle near the bottom", box)
    assert fonts.text_image("வணக்கம் பாட்டி! நிலா நீலம்.", 640, 360) == path, "cached"


def main():
    tmp = tempfile.mkdtemp(prefix="dreamreel-voices-")
    try:
        languages()
        choosing()
        worker(os.path.join(tmp, "w"))
        fish(os.path.join(tmp, "f"))
        piper(os.path.join(tmp, "p"))
        keys(tmp)
        subtitles()
        assert dr.VoiceEngine is voices.VoiceEngine
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("voices: ok")


if __name__ == "__main__":
    main()
