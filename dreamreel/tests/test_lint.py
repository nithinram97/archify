"""The director's checks (lint.py): a long static shot, line after line with nobody doing anything, a
listener made of wood; a well-directed version of the same scene passes; films can switch checks off,
tune them and add their own.

    python tests/test_lint.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402,F401

import dreamreel as dr  # noqa: E402

LINES = ("We need to talk.", "About what happened yesterday.", "I saw everything.", "And I'm not angry.")


def scene(directed, film=None):
    s = dr.Scene({"kind": "room"})
    if film:
        s.film = film
    mia, tom = s.cast(mia={}, tom={})
    mia.place("left", facing="right")
    tom.place("right", facing="left")
    s.cut.shot("two_shot", of="mia", other="tom", at=0)
    for i, line in enumerate(LINES):
        if directed:
            if i == 2:
                s.cut.shot("close_up", of="tom", at=s.clock)
            mia.do(("shrug", "point", "shake_head", "nod")[i], wait=False)
            tom.feel(("suspicious", "sad", "surprised", "happy")[i], at=s.clock + 0.5)
        mia.say(line, to="tom")
    s.end_time = s.clock + 1
    s.finish()
    return s


def kinds(warnings):
    return {w.split(":")[0] for w in warnings if ":" in w}


def main():
    bad = scene(False).check()
    assert {"static camera", "radio play", "dead reaction"} <= kinds(bad), bad
    assert any("Tom" in w for w in bad if w.startswith("dead reaction")), "the listener, not the speaker"
    good = scene(True).check()
    assert not ({"static camera", "radio play", "dead reaction"} & kinds(good)), good
    print(f"  checks: ok ({len(bad)} warnings for the flat scene, none once it's directed)")

    quiet = scene(False, film={"check": {"ignore": ["radio_play"], "static_camera_seconds": 30}}).check()
    assert not ({"radio play", "static camera"} & kinds(quiet)) and "dead reaction" in kinds(quiet), quiet

    class NoTom(dr.Lint):                         # a film's own check
        def check(self, scene):
            return ["no tom: Tom is in this"] if scene.character("tom") else []
    assert "no tom" in kinds(scene(True).check())
    print("  settings and new checks: ok")
    print("lint: all ok")


if __name__ == "__main__":
    main()
