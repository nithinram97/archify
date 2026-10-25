"""Lip sync from the sounds of a line: a voiced line gives mouth shapes (closed for M/B/P, round for
"oo"), toy and pack faces follow them, and "loudness" turns it off. Needs Piper (pip install piper-tts)
and Rhubarb (downloaded on first use); skipped without them.

    python tests/test_lipsync.py
"""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import dreamreel as dr  # noqa: E402
from dreamreel import handling, lipsync, quaternius, voices  # noqa: E402

LINE = "Mum, look! The moon is blue."


def talk(set_spec, who, folder, lipsync="sounds"):
    """Say the line in a scene with voices on; what the mouth did while talking."""
    s = dr.Scene(set_spec)
    s.voices.dir, s.voices.engine, s.voices.lipsync = folder, "piper", lipsync
    a = s.cast(a=who)
    a.place("center", facing="camera")
    t0 = s.clock
    a.say(LINE)
    t1 = s.clock
    s.finish()
    out = {"round": 0.0, "open": 0.0, "closed": False, "pucker": 0.0, "jaw": 0.0}
    for k in range(80):
        handling.evaluate(s, t0 + 0.2 + (t1 - t0 - 0.4) * k / 79)
        out["round"] = max(out["round"], a.mouth.get("round", 0.0))
        opened = (a.mouth.scale.z - 1) / 2.2
        out["open"] = max(out["open"], opened)
        out["closed"] = out["closed"] or (k > 3 and opened < 0.03)
        keys_ = getattr(a, "face_keys", {})
        if keys_.get("pucker"):
            out["pucker"] = max(out["pucker"], keys_["pucker"][0].value)
        if keys_.get("open"):
            out["jaw"] = max(out["jaw"], keys_["open"][0].value)
    return out


def ai_face(tmp):
    import importlib.util
    from dreamreel import boost
    keep = {k: os.environ.get(k) for k in ("DREAMREEL_BOOST_TEST", "DREAMREEL_BOOST_URL", "DREAMREEL_BOOST_TOKEN",
                                           "DREAMREEL_FACE_SKILL", "DREAMREEL_BOOST_WORK")}
    spec = importlib.util.spec_from_file_location("dreamreel_booster_server4",
                                                  os.path.join(ROOT, "dreamreel", "booster", "server.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    got = {}
    os.environ.update(DREAMREEL_BOOST_TEST="1", DREAMREEL_FACE_SKILL="test.face",
                      DREAMREEL_BOOST_WORK=os.path.join(tmp, "work"))
    httpd = mod.serve(port=0, host="127.0.0.1", token="k", work=os.path.join(tmp, "work"),
                      ready=lambda h, t: got.update(port=h.server_address[1]))
    try:
        os.environ.update(DREAMREEL_BOOST_URL=f"http://127.0.0.1:{got['port']}", DREAMREEL_BOOST_TOKEN="k")
        boost._cache.clear()
        for f in os.listdir(tmp):
            if f.endswith(".face.json"):
                os.remove(os.path.join(tmp, f))
        face = talk({"kind": "room"}, {}, tmp, lipsync="ai")
        assert any(f.endswith(".face.json") for f in os.listdir(tmp)), "read once, then kept"
        assert face["round"] > 0.9 and face["open"] > 0.3, face
    finally:
        httpd.shutdown()
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        boost._cache.clear()


def main():
    if not voices._piper_available() or not lipsync.available():
        print("SKIP test_lipsync: needs Piper and Rhubarb")
        return
    tmp = tempfile.mkdtemp(prefix="dreamreel-lipsync-")
    try:
        wav = os.path.join(tmp, "line.wav")
        voices.Piper().speak(LINE, voices.DEFAULT_VOICE, wav)
        speech = voices.Speech(wav, LINE, english=True)
        cues = speech.shapes()
        assert cues and len(cues) > 8, cues
        assert os.path.exists(wav + ".cues.json"), "listened to once, then cached"
        assert any(r > 0.9 for _, (o, r, w) in cues), "'moon' and 'blue' round the lips"
        assert any(o < 0.05 and w > 0.05 for _, (o, r, w) in cues), "'Mum' presses the lips together"
        assert any(o > 0.4 for _, (o, r, w) in cues), "the mouth opens"
        assert speech.shapes() == cues
        # other languages: the language-independent recogniser
        other = voices.Speech(wav, LINE, english=False)
        os.remove(wav + ".cues.json")
        assert other.shapes(), "phonetic recognition"

        # a toy figure: the mouth narrows for "oo", opens for vowels and closes for "M"
        toy = talk({"kind": "room"}, {}, tmp)
        assert toy["round"] > 0.9 and toy["open"] > 0.4 and toy["closed"], toy
        # a person from the packs: their own mouth's shape keys follow the sounds
        if "men" in quaternius.installed():
            person = talk({"kind": "room", "scale": "people"}, dict(type="person", body="man"), tmp)
            assert person["pucker"] > 0.9 and person["jaw"] > 0.3, person
        # loudness only: no round lips
        loud = talk({"kind": "room"}, {}, tmp, lipsync="loudness")
        assert loud["round"] < 0.01 and loud["open"] > 0.3, loud
        # AI reading the face in the voice (on a booster; here a stand-in face skill)
        os.environ.pop("DREAMREEL_BOOST_URL", None)
        lipsync._warned.clear()
        fallback = talk({"kind": "room"}, {}, tmp, lipsync="ai")
        assert fallback["round"] > 0.9, ("no booster: the sounds", fallback)
        ai_face(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
