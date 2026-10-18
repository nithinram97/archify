"""Realistic people (humans.py): built from MakeHuman's assets with hair, brows, lashes, eyes, teeth
and clothes; 52 ARKit face shapes and 15 visemes that the brows and lashes follow; moods, blinks and
speech moving the face; elbows and knees bending for gestures and sitting. Without the assets (`dreamreel
assets --pack humans`) a toy figure stands in, which is checked instead.

    python tests/test_humans.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402
import numpy as np  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import handling, humans  # noqa: E402


def at(s, obj, t):
    handling.evaluate(s, t)
    return obj.matrix_world.translation.copy()


def key_value(s, mesh, name, t):
    handling.evaluate(s, t)
    return mesh.data.shape_keys.key_blocks[name].value


def stand_in():
    s = dr.Scene({"kind": "room"})
    saved = humans.installed
    humans.installed = lambda: False
    try:
        c = s.cast(asha=dict(type="human", gender="female", age=30))
        assert type(c).__name__ == "ToyFigure", type(c)
    finally:
        humans.installed = saved
    print("  stand-in: ok (a toy plays the part without the assets)")


def recipes():
    a = humans.body_shape(humans.Recipe(dict(gender="female", age=25, heritage="east_asian"), "a"))
    b = humans.body_shape(humans.Recipe(dict(gender="male", age=70, heritage="african", build="heavy"), "b"))
    c = humans.body_shape(humans.Recipe(dict(gender="female", age=25, heritage="east_asian"), "c"))
    assert np.abs(a - b).max() > 0.5, "gender, age, build and heritage shape the body"
    assert 0 < np.abs(a - c).max() < 0.5, "two people of the same description still have different faces"
    hair = humans.Proxy(humans._find("hair", "bob01"))
    pts = hair.fit(a)
    assert len(pts) and pts[:, 1].mean() > a[:, 1].mean(), "the hair sits on the head"
    print("  recipes: ok")


def person():
    s = dr.Scene({"kind": "room", "props": [{"type": "table", "place": "back", "chairs": 2}]})
    asha = s.cast(asha=dict(type="human", gender="female", age=30, heritage="south_asian", hair="long01"))
    parts = {m.name.split(".")[-1] for m in asha.meshes}
    assert {"body", "eyes", "eyebrows", "eyelashes", "teeth", "hair"} <= parts, parts
    body = next(m for m in asha.meshes if m.name.endswith(".body"))
    brows = next(m for m in asha.meshes if m.name.endswith(".eyebrows"))
    names = set(body.data.shape_keys.key_blocks.keys())
    assert len(names & set(humans.ARKIT)) >= 50 and len([n for n in names if n.startswith("viseme_")]) >= 14, names
    assert "browInnerUp" in brows.data.shape_keys.key_blocks, "the brows move with the face"
    assert 1.55 < asha.H < 1.72, asha.H
    assert abs(asha.height() - asha.H) < 0.06, ("framed by her full height", asha.height(), asha.H)
    asha.place("center", facing="camera")
    t0 = s.clock
    asha.feel("happy")
    t_happy = s.clock + 0.5
    s.wait(0.8)
    asha.feel("surprised")
    t_surprised = s.clock + 0.5
    s.wait(0.8)
    asha.feel("sad")
    t_sad = s.clock + 0.5
    s.wait(0.8)
    t_palm = s.clock
    asha.do("facepalm")
    asha.sit("chair")
    t_sit = s.clock + 0.5
    s.wait(1.0)

    class Speech:                         # the sounds of a line, as Rhubarb hears them
        duration = 1.0

        def letters(self):
            return [(0.0, "X"), (0.1, "A"), (0.25, "D"), (0.45, "F"), (0.65, "G"), (0.9, "X")]
    s.voices.lipsync = "sounds"
    t_say = s.clock
    asha._lipsync_audio(t_say, Speech())
    s.wait(1.5)
    s.finish()
    smile = key_value(s, body, "mouthSmileLeft", t_happy)
    assert smile > 0.6 and key_value(s, body, "mouthSmileLeft", t_sad) < 0.2, ("smiles when happy", smile)
    assert key_value(s, body, "jawOpen", t_surprised) > 0.2 and key_value(s, body, "eyeWideLeft", t_surprised) > 0.3
    assert key_value(s, body, "browInnerUp", t_sad) > 0.5 and key_value(s, body, "mouthFrownLeft", t_sad) > 0.5
    assert key_value(s, brows, "browInnerUp", t_sad) > 0.5, "the brows follow"
    blinks = [key_value(s, body, "eyeBlinkLeft", t0 + k / 24) for k in range(int((s.clock - t0) * 24))]
    assert max(blinks) > 0.8, ("she blinks", max(blinks))
    def peak(name, a, b):
        return max(key_value(s, body, name, t_say + a + (b - a) * k / 8) for k in range(9))
    assert peak("viseme_aa", 0.25, 0.45) > 0.8 and peak("viseme_U", 0.45, 0.65) > 0.8 and \
        peak("viseme_aa", 0.65, 0.9) < 0.3, "her mouth makes the sounds of speech"
    near = min((at(s, asha.hands[1], t_palm + k * 0.1) - asha.head_point(t_palm + k * 0.1)).length for k in range(16))
    assert near < 0.15, ("the facepalm reaches the face", near)
    knee = asha.rig.pose.bones[asha.roles["l_knee"]]
    ankle = asha.rig.pose.bones[asha.roles["l_ankle"]]
    handling.evaluate(s, t_sit)
    kz, az = (asha.rig.matrix_world @ knee.head).z, (asha.rig.matrix_world @ ankle.head).z
    assert kz - az > 0.25 and az < 0.2, ("sitting: knees bent, feet on the floor", kz, az)
    print(f"  person: ok (parts {sorted(parts)}, {len(names)} face shapes)")


def fight():
    s = dr.Scene({"kind": "street"})
    ravi = s.cast(ravi=dict(type="human", gender="male", age=34))
    arjun = s.cast(arjun=dict(type="human", gender="male", age=26))
    ravi.place((-0.5, 0), facing="camera")
    arjun.place((0.5, 0), facing="camera")
    ravi.turn_to(arjun)
    arjun.turn_to(ravi)
    t_jab = s.clock
    ravi.do("jab", target="arjun")
    t_kick = s.clock
    arjun.do("kick", target=ravi)
    s.finish()

    def closest(hand, t0):
        return min((at(s, hand, t0 + k * 0.05) - arjun.head_point(t0 + k * 0.05)).length for k in range(40))
    near = min(closest(h, t_jab) for h in ravi.hands.values())
    assert near < 0.3, ("the jab reaches his face", near)
    finger = ravi.rig.pose.bones["mixamorig:LeftHandIndex2"]
    handling.evaluate(s, t_jab + 0.3)
    assert finger.rotation_quaternion.angle > 1.0, "he punches with a fist"
    handling.evaluate(s, t_kick - 0.05)
    assert finger.rotation_quaternion.angle < 0.1, "and opens his hands after"
    foot = arjun.rig.pose.bones[arjun.roles["r_ankle"]]
    highest = 0.0
    for k in range(20):
        handling.evaluate(s, t_kick + k * 0.05)
        highest = max(highest, (arjun.rig.matrix_world @ foot.head).z)
    assert highest > 0.5, ("the kick comes up", highest)
    print(f"  fight: ok (jab {near:.2f} m from the face, kick {highest:.2f} m high)")


def main():
    stand_in()
    if not humans.installed():
        print("humans: skipped the people (MakeHuman's assets aren't downloaded: `dreamreel assets --pack humans`)")
        return
    recipes()
    person()
    fight()
    print("humans: all ok")


if __name__ == "__main__":
    main()
