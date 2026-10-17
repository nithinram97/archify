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
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
