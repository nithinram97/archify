"""The camera grammar: every framing and move builds, follow tracks, shots merge with automatic coverage.

    python tests/test_camera.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import dreamreel as dr  # noqa: E402
from dreamreel import keys  # noqa: E402

ROOM = {"kind": "room", "props": [{"type": "door", "place": "back-left"},
                                  {"type": "table", "place": "center", "items": ["cookie-jar"]}]}


def scene():
    s = dr.Scene(ROOM)
    mia, tom = s.cast(mia={}, tom={})
    mia.place("table-left", facing="tom")
    tom.place("table-right", facing="mia")
    return s, mia, tom


def main():
    subjects = {0: {}, 1: {"of": "mia"}, 2: {"of": "mia", "other": "tom"}}
    # every framing, at every angle
    for name, cls in dr.registry("shot").items():
        for angle in ("eye_level", "high", "low", "birds_eye", "worms_eye"):
            s, mia, tom = scene()
            kw = dict(subjects[cls.subjects])
            if name == "insert":
                kw = {"of": "cookie-jar"}
            s.cut.shot(name, at=0.0, angle=angle, **kw)
            s.wait(2)
            s.finish()
            shot = s.cut.final[0]
            assert shot.state.pos.z >= 0.05, (name, angle, shot.state.pos)
            assert (shot.state.pos - shot.state.aim).length > 0.1, (name, angle)
    # every move changes the camera over the shot (except static)
    for move in dr.names("move"):
        s, mia, tom = scene()
        kw = {"to": "tom"} if move == "rack_focus" else {}
        s.cut.shot("medium", of="mia", at=0.0, move=move, **kw)
        if move == "follow":
            mia.walk_to("door")
        s.wait(3)
        s.finish()
        cam, rig, aim = s.cut.cam, s.cut.rig, s.cut.aim
        a = [keys.sample(o, p, 0.0) for o, p in ((rig, "location"), (aim, "location"), (cam.data, "lens"))]
        b = [keys.sample(o, p, s.length - 0.2) for o, p in ((rig, "location"), (aim, "location"), (cam.data, "lens"))]
        focus = (keys.sample(cam.data.dof, "focus_distance", 0.0), keys.sample(cam.data.dof, "focus_distance", s.length - 0.2))
        changed = a != b or focus[0] != focus[1]
        assert changed == (move != "static"), (move, a, b)
    # follow keeps the walker framed
    s, mia, tom = scene()
    s.cut.shot("medium_wide", of="mia", at=0.0, move="follow")
    mia.walk_to("door")
    s.finish()
    t = s.length - 0.5
    p, _, _ = mia.where_at(t)
    aim = dr.character.Vector(keys.sample(s.cut.aim, "location", t))
    assert (dr.character.Vector((aim.x, aim.y)) - dr.character.Vector((p.x, p.y))).length < 0.8, (aim, p)
    # a shot with a duration hands back to the automatic director
    s, mia, tom = scene()
    mia.say("One.", to=tom)
    s.cut.shot("extreme_close_up", of="tom", duration=1.0)
    tom.say("Two, three, four, five, six.", to=mia)
    mia.say("Seven.", to=tom)
    s.finish()
    labels = [lbl for _, lbl in s.cut.describe()]
    i = next(i for i, lbl in enumerate(labels) if lbl.startswith("extreme_close_up"))
    assert i + 1 < len(labels), labels
    print("framings:", ", ".join(dr.names("shot")))
    print("moves:", ", ".join(dr.names("move")))
    print("OK")


if __name__ == "__main__":
    main()
