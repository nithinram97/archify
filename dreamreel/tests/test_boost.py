"""Boosters: a booster server (here on this computer, with test skills) installs a skill on first use,
runs jobs one at a time, takes and gives back files, refuses a wrong pass key and reports failures;
dreamreel connects to it, speaks a voice line through it, and carries on without it when it's gone.

    python tests/test_boost.py
"""
import importlib.util
import io
import os
import shutil
import sys
import tempfile
import wave
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dreamreel import boost, cli, plugins, userkeys, voices  # noqa: E402

SERVER = os.path.join(ROOT, "dreamreel", "booster", "server.py")


def start_booster(work):
    spec = importlib.util.spec_from_file_location("dreamreel_booster_server", SERVER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    got = {}
    httpd = mod.serve(port=0, host="127.0.0.1", token="pass-123", work=work,
                      ready=lambda h, t: got.update(port=h.server_address[1], token=t))
    return httpd, f"http://127.0.0.1:{got['port']}", got["token"]


def main():
    tmp = tempfile.mkdtemp(prefix="dreamreel-boost-")
    os.environ["DREAMREEL_BOOST_TEST"] = "1"
    os.environ["DREAMREEL_BOOST_WORK"] = os.path.join(tmp, "work")
    os.environ["XDG_CONFIG_HOME"] = os.path.join(tmp, "config")
    for k in ("DREAMREEL_BOOST_URL", "DREAMREEL_BOOST_TOKEN", "DREAMREEL_TEST_SPEAKER"):
        os.environ.pop(k, None)
    httpd = None
    try:
        httpd, url, token = start_booster(os.path.join(tmp, "work"))
        assert token == "pass-123"

        # a wrong key is refused, plainly
        try:
            boost.Booster(url, "wrong").status(fresh=True)
            raise AssertionError("a wrong key must be refused")
        except boost.BoostError as e:
            assert "pass key" in str(e)

        b = boost.Booster(url, token)
        st = b.status(fresh=True)
        assert st["skills"]["test.echo"]["state"] == "not installed" and "voice.indic_parler" in st["skills"], st
        # a job: installs the skill first, uploads a file, downloads the result
        src = os.path.join(tmp, "in.bin")
        with open(src, "wb") as f:
            f.write(os.urandom(5000))
        seen, lines = [], []
        out = b.run("test.echo", {"word": "hello", "n": 3}, {"file": src}, out_dir=os.path.join(tmp, "out"),
                    on_progress=seen.append, log=lines.append)
        assert out["echo"] == {"word": "hello", "n": 3}, out
        with open(src, "rb") as f, open(out["copy"], "rb") as g:
            assert f.read() == g.read(), "the file came back as it went"
        assert seen[-1] == 1.0 and any("installing" in x for x in lines), (seen, lines)
        assert b.status(fresh=True)["skills"]["test.echo"]["ready"]
        assert b.upload(src) == b.upload(src), "a file is sent once"
        # failures come back as errors, and the booster carries on
        try:
            b.run("test.echo", {"fail": True})
            raise AssertionError("expected a failure")
        except boost.BoostError as e:
            assert "asked to fail" in str(e)
        try:
            b.run("no.such.skill", {})
            raise AssertionError("expected an unknown skill")
        except boost.BoostError as e:
            assert "no skill" in str(e)
        assert b.run("test.echo", {"again": 1})["echo"] == {"again": 1}

        # connecting saves the address and key on this computer
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli.main(["boost", "connect", url, token])
            cli.main(["boost"])
        assert "connected" in buf.getvalue() and "test.echo" in buf.getvalue(), buf.getvalue()
        assert userkeys.status()["DREAMREEL_BOOST_URL"]["set"] and os.environ["DREAMREEL_BOOST_URL"] == url
        assert boost.configured() is not None and boost.can("voice.tone")

        # a voice engine with no model on this computer speaks through the booster
        class Tone(voices._AIVoice):
            name = "tone"
            languages = ("ta",)
        try:
            assert Tone.available() and not voices._local_ready("tone")
            vs = voices.Voices(os.path.join(tmp, "film"))

            class Who:
                name, voice = "Paati", {"language": "ta", "engine": "tone"}
            sp = vs.speak(Who(), "வணக்கம், எப்படி இருக்கீங்க?")
            assert sp is not None and sp.duration > 0.5, vs.warned
            with wave.open(sp.path) as w:
                assert w.getsampwidth() == 2
        finally:
            del plugins._REGISTRY["voice"]["tone"]

        # the booster goes away: dreamreel notices once, quickly, and carries on
        httpd.shutdown()
        httpd.server_close()
        httpd = None
        boost._cache.clear()
        assert not boost.can("voice.tone")
        assert not voices.IndicParler.available() or voices._local_ready("indic_parler")
        with redirect_stdout(io.StringIO()):
            cli.main(["boost", "disconnect"])
        assert boost.configured() is None
    finally:
        if httpd:
            httpd.shutdown()
        for k in ("DREAMREEL_BOOST_TEST", "DREAMREEL_BOOST_WORK", "XDG_CONFIG_HOME", "DREAMREEL_BOOST_URL",
                  "DREAMREEL_BOOST_TOKEN"):
            os.environ.pop(k, None)
        shutil.rmtree(tmp, ignore_errors=True)
    print("boost: ok")


if __name__ == "__main__":
    main()
