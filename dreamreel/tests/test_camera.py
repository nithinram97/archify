"""The camera grammar: every framing and move builds, follow tracks, shots merge with automatic coverage.

    python tests/test_camera.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import dreamreel as dr  # noqa: E402
from dreamreel import keys  # noqa: E402
from mathutils import Vector  # noqa: E402

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
    # an angle asked for is kept even when furniture is in the way (look round or come closer instead)
    s, mia, tom = scene()
    s.cut.shot("medium_close", of="tom", at=0.0, angle="worms_eye")
    s.wait(1)
    s.finish()
    shot = s.cut.final[0]
    head = tom.head_point(0.5)
    assert shot.state.pos.z < head.z, ("worm's eye stays below the face", shot.state.pos, head)

    # the fourth wall: there for reverse angles, invisible and see-through from the front, no shadow
    s, mia, tom = scene()
    front = next(o for o in s.bscene.objects if o.get("dr_fourth_wall"))
    assert front.active_material.use_backface_culling and not front.visible_shadow and front.get("dr_final_only")
    head = mia.head_point(0.0)
    outside = head + Vector((0, -6.0, 0.3))      # a wide shot's camera, beyond the front wall
    assert s.cut.clear_view(head, outside), "the fourth wall doesn't block shots from the front"
    # a close-up of someone facing the back wall is from the front of their face, not their back
    s, mia, tom = scene()
    mia.place("table-left", facing="back")
    s.cut.shot("close_up", of="mia", at=0.0)
    s.wait(1)
    s.finish()
    shot = s.cut.final[0]
    face_dir = mia.forward(0.5)
    to_cam = shot.state.pos - mia.head_point(0.5)
    assert face_dir.x * to_cam.x + face_dir.y * to_cam.y > 0, ("a close-up sees the face", face_dir, to_cam)

    # the 180-degree line: an over-the-shoulder named one way round and a two-shot named the other way
    # round are on the same side; a fight two-shot shows its hero's face three-quarters on
    import math
    for hero, foe in (("mia", "tom"), ("tom", "mia")):
        s, mia, tom = scene()
        s.cut.shot("over_shoulder", of=foe, other=hero, at=0.0)
        s.cut.shot("full_two_shot", of=hero, other=foe, at=1.0)
        s.wait(2)
        s.finish()
        h, f = s.character(hero), s.character(foe)
        line = f.position(1.0) - h.position(1.0)
        n = Vector((-line.y, line.x))
        sides = [n.dot(Vector((sh.state.pos.x, sh.state.pos.y)) - h.position(1.0)) for sh in s.cut.final[-2:]]
        assert sides[0] * sides[1] > 0, ("both shots on one side of the line", hero, sides)
        to_cam = Vector((s.cut.final[-1].state.pos.x, s.cut.final[-1].state.pos.y)) - h.position(1.0)
        off = math.degrees(h.forward(1.0).angle(to_cam.normalized()))
        assert 20 < off < 80, ("the hero's open three-quarter side", hero, off)
    print("  the line and the hero's side: ok")

    # someone in the way is their body as posed, not a cylinder: standing in the line of sight blocks it
    # (the camera moves), lying on the ground under it doesn't (the camera stays)
    for lying in (False, True):
        s = dr.Scene({"kind": "outdoor", "biome": "meadow", "trees": 0})
        mia, tom = s.cast(mia={}, tom={})
        mia.place((0, 2), facing="camera")
        tom.place((0, 0), facing="mia")
        if lying:
            keys.key(tom.hips, "location", 0.0, (0, 0, 0.12))
            keys.key(tom.body, "rotation_euler", 0.0, (math.radians(-90), 0, 0))
        s.wait(2)
        head = mia.head_point(0.0)
        asked = Vector((0, -3, head.z))
        s.cut.add("medium", 0.0, [mia], asked, head)
        s.cut.manual = True
        s.finish()
        moved = (s.cut.final[0].state.pos - asked).length
        assert (moved < 0.01) == lying, ("lying under the line of sight" if lying else "standing in it", moved)
    print("  people in the way, as posed: ok")
    print("OK")


if __name__ == "__main__":
    main()
