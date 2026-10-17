"""Acting from a sentence (do = "act"): with a booster, the motion is made once, kept in motions/ai/,
and played by a toy and by a person from the packs on their own rig; without one, the closest gesture.
The booster here runs a stand-in skill that hands back a test clip (HY-Motion needs a graphics card).

    python tests/test_aimotion.py
"""
import importlib.util
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dreamreel import aimotion, boost, cli, film, handling, project, quaternius  # noqa: E402
from test_motion import write_bvh  # noqa: E402

SCENE = '''set = "kitchen"
cast = ["{who}"]

[[beats]]
who = "{who}"
do = "act"
what = "raises her left arm to the side and holds it"
seconds = 2
'''


def booster(work):
    spec = importlib.util.spec_from_file_location("dreamreel_booster_server2",
                                                  os.path.join(ROOT, "dreamreel", "booster", "server.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    got = {}
    httpd = mod.serve(port=0, host="127.0.0.1", token="k", work=work,
                      ready=lambda h, t: got.update(port=h.server_address[1]))
    return httpd, f"http://127.0.0.1:{got['port']}"


def build(p, file):
    return film.build(p, os.path.join(p.root, "scenes", file))


def arm_up(s, who):
    """Is the left hand at shoulder height at the end of the motion?"""
    ev = next(e for e in s.events if e["kind"] == "perform")
    handling.evaluate(s, ev["t0"] + 1.7)          # the arm is up from halfway through the clip
    c = s.character(who)
    if getattr(c, "rig", None) is not None:
        pb = c.rig.pose.bones
        return (c.rig.matrix_world @ pb["LowerArm.L"].tail).z > (c.rig.matrix_world @ pb["UpperArm.L"].head).z - 0.08
    hand = c.hands[1].matrix_world.translation
    return hand.z > c.arms[1].matrix_world.translation.z - 0.1 * c.H


def main():
    tmp = tempfile.mkdtemp(prefix="dreamreel-act-")
    keep = {k: os.environ.get(k) for k in ("DREAMREEL_BOOST_TEST", "DREAMREEL_BOOST_URL", "DREAMREEL_BOOST_TOKEN",
                                           "DREAMREEL_MOTION_SKILL", "DREAMREEL_TEST_MOTION", "XDG_CONFIG_HOME")}
    httpd = None
    try:
        os.environ["XDG_CONFIG_HOME"] = os.path.join(tmp, "config")
        os.environ.pop("DREAMREEL_BOOST_URL", None)
        filmdir = os.path.join(tmp, "cookie")
        cli.main(["new", filmdir, "--example"])
        p = project.find(filmdir)
        people = "women" in quaternius.installed()
        # a toy for sure (the example's cast are people when the packs are there)
        with open(os.path.join(filmdir, "cast", "toyo.toml"), "w") as f:
            f.write('name = "Toyo"\nhair = "bob"\n')
        with open(os.path.join(filmdir, "scenes", "050_toy.toml"), "w") as f:
            f.write(SCENE.format(who="toyo"))
        if people:
            with open(os.path.join(filmdir, "scenes", "060_person.toml"), "w") as f:
                f.write(SCENE.format(who="mia"))

        # no booster: the closest gesture (none fits "raises her arm"), and nothing kept
        aimotion._warned.clear()
        s = build(p, "050_toy.toml")
        assert not any(e["kind"] == "perform" for e in s.events)
        assert not os.path.isdir(os.path.join(filmdir, "motions", "ai"))
        assert aimotion.fallback_gesture("she waves goodbye", lambda g: True) == "wave"
        assert aimotion.fallback_gesture("she stands still", lambda g: True) is None

        # with a booster: the motion is made, kept, and played
        clip = os.path.join(tmp, "arm_up.bvh")
        write_bvh(clip)
        os.environ.update(DREAMREEL_BOOST_TEST="1", DREAMREEL_MOTION_SKILL="test.motion", DREAMREEL_TEST_MOTION=clip,
                          DREAMREEL_BOOST_WORK=os.path.join(tmp, "work"))
        httpd, url = booster(os.path.join(tmp, "work"))
        os.environ.update(DREAMREEL_BOOST_URL=url, DREAMREEL_BOOST_TOKEN="k")
        boost._cache.clear()
        s = build(p, "050_toy.toml")
        kept = os.listdir(os.path.join(filmdir, "motions", "ai"))
        assert len(kept) == 1 and kept[0].startswith("raises-her-left-arm") and kept[0].endswith(".bvh"), kept
        assert arm_up(s, "toyo"), "the toy raises its arm"
        if people:
            s = build(p, "060_person.toml")
            assert arm_up(s, "mia"), "the person raises her arm, on her own rig"

        # made once: with the booster gone, the kept motion still plays
        httpd.shutdown()
        httpd.server_close()
        httpd = None
        boost._cache.clear()
        s = build(p, "050_toy.toml")
        assert any(e["kind"] == "perform" for e in s.events)
        assert len(os.listdir(os.path.join(filmdir, "motions", "ai"))) == 1
    finally:
        if httpd:
            httpd.shutdown()
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        os.environ.pop("DREAMREEL_BOOST_WORK", None)
        shutil.rmtree(tmp, ignore_errors=True)
    print("act: ok")


if __name__ == "__main__":
    main()
