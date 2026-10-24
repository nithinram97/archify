"""Restyling (experimental): the style comes from the scene or film.toml, only final renders are sent,
the result is kept and reused until the scene or the style changes, and without a booster the scene
stays as rendered. The booster runs a stand-in (Wan needs a graphics card).

    python tests/test_restyle.py
"""
import importlib.util
import io
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dreamreel import boost, cli, project, restyle  # noqa: E402


def main():
    tmp = tempfile.mkdtemp(prefix="dreamreel-restyle-")
    names = ("DREAMREEL_BOOST_TEST", "DREAMREEL_BOOST_URL", "DREAMREEL_BOOST_TOKEN", "DREAMREEL_BOOST_WORK",
             "DREAMREEL_RESTYLE_SKILL", "XDG_CONFIG_HOME")
    keep = {k: os.environ.get(k) for k in names}
    httpd = None
    try:
        os.environ["XDG_CONFIG_HOME"] = os.path.join(tmp, "config")
        os.environ.pop("DREAMREEL_BOOST_URL", None)
        film = os.path.join(tmp, "film")
        with redirect_stdout(io.StringIO()):
            cli.main(["new", film, "--example"])
        p = project.find(film)
        scene = p.scenes()[0]
        with open(scene) as f:
            text = f.read()
        assert restyle.wanted(p, scene) == (None, 0.0), "no style asked for: none"
        with open(scene, "w") as f:
            f.write('restyle = "a watercolour painting"\nrestyle_strength = 0.4\n' + text)
        assert restyle.wanted(p, scene) == ("a watercolour painting", 0.4)
        p.film["restyle"] = {"prompt": "an oil painting", "strength": 0.7}
        other = p.scenes()[1]
        assert restyle.wanted(p, other) == ("an oil painting", 0.7), "the film's style for every scene"

        video = os.path.join(film, "renders", "final", "x.mp4")
        os.makedirs(os.path.dirname(video))
        with open(video, "wb") as f:
            f.write(b"not really a video" * 100)
        meta = {"name": "x", "video": video}
        # previz isn't restyled; without a booster nothing changes
        assert restyle.apply(p, dict(meta), scene, "previz")["video"] == video
        with redirect_stdout(io.StringIO()) as said:
            assert restyle.apply(p, dict(meta), scene, "final")["video"] == video
        assert "booster" in said.getvalue()

        spec = importlib.util.spec_from_file_location("dreamreel_booster_server5",
                                                      os.path.join(ROOT, "dreamreel", "booster", "server.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        got = {}
        os.environ.update(DREAMREEL_BOOST_TEST="1", DREAMREEL_RESTYLE_SKILL="test.restyle",
                          DREAMREEL_BOOST_WORK=os.path.join(tmp, "work"))
        httpd = mod.serve(port=0, host="127.0.0.1", token="k", work=os.path.join(tmp, "work"),
                          ready=lambda h, t: got.update(port=h.server_address[1]))
        os.environ.update(DREAMREEL_BOOST_URL=f"http://127.0.0.1:{got['port']}", DREAMREEL_BOOST_TOKEN="k")
        boost._cache.clear()
        with redirect_stdout(io.StringIO()):
            m = restyle.apply(p, dict(meta), scene, "final")
        assert m["video"].endswith("x.restyled.mp4") and os.path.exists(m["video"]), m
        assert m["video_plain"] == video and m["restyle"]["style"] == "a watercolour painting"
        # kept: the same scene and style don't go to the booster again
        httpd.shutdown()
        httpd.server_close()
        httpd = None
        boost._cache.clear()
        with redirect_stdout(io.StringIO()):
            again = restyle.apply(p, dict(m), scene, "final")
        assert again["video"] == m["video"], "reused"
        # a new style: back to the plain render until it can be made again
        with open(scene, "w") as f:
            f.write('restyle = "a pencil sketch"\n' + text)
        with redirect_stdout(io.StringIO()):
            changed = restyle.apply(p, dict(m), scene, "final")
        assert changed["video"] == video, "the old style isn't used for a new one"
    finally:
        if httpd:
            httpd.shutdown()
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    print("restyle: ok")


if __name__ == "__main__":
    main()
