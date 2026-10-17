"""Faces: white eyes with irises, lids, teeth, the extreme moods, how_much, tears and sweat.

    python tests/test_face.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import face, handling, plugins  # noqa: E402

EXTREMES = ("gleeful", "crazed", "furious", "determined", "terrified", "screaming", "shocked", "disgusted",
            "suspicious", "crying", "embarrassed", "nervous", "bored", "loving")


def kv(obj, name):
    return obj.data.shape_keys.key_blocks[name].value


def main():
    assert set(EXTREMES) <= set(plugins.names("mood"))
    s = dr.Scene({"kind": "room"})
    girl, frog = s.cast(girl=dict(eye_color="#3f7fbf", braces=True), frog=dict(type="creature", body="frog"))
    girl.place("left")
    frog.place("right")
    # white eyes with a coloured iris for people; beads for creatures
    assert len(girl.gazes) == 2 and girl.irises and girl.scleras
    iris = next(o for o in girl.irises if ".iris" in o.name)
    assert iris.active_material.diffuse_color[2] > iris.active_material.diffuse_color[0], "blue eyes"
    assert not frog.gazes
    assert bpy.data.objects.get("Girl.braces") or any(".braces" in o.name for o in bpy.data.objects)
    times = {}
    for m in ("neutral", "crazed", "furious", "sleepy", "shocked", "crying", "nervous"):
        times[m] = s.clock + 0.5
        girl.feel(m)
        frog.feel(m)
        s.wait(1.2)
    girl.feel("happy", how_much=0.5)
    t_half = s.clock + 0.5
    s.wait(1)
    girl.feel("happy", how_much=1.5)
    t_more = s.clock + 0.5
    s.wait(1)
    s.finish()

    def at(t):
        handling.evaluate(s, t)

    at(times["neutral"])
    up = girl.teeth["upper"]
    assert up.scale.z < 0.01 and girl.gazes[0].scale.x > 0.99, "neutral: no teeth, normal pupils"
    at(times["crazed"])
    assert girl.gazes[0].scale.x < 0.8 and up.scale.z > 0.1 and girl.eyes[0].scale.x > 1.2, "crazed: wide, tiny pupils, teeth"
    at(times["furious"])
    assert kv(iris, "angry") > 0.9 and girl.teeth["lower"].scale.z > 0.1, "furious: angry lids, clenched teeth"
    at(times["sleepy"])
    assert kv(iris, "upper") > 0.7, "sleepy: lids down"
    at(times["shocked"])
    assert kv(girl.mouth_mesh, "o") > 0.6 and girl.mouth.scale.z > 2, "shocked: round open mouth"
    at(times["crying"] + 0.6)
    tears = [o for o in bpy.data.objects if ".tear" in o.name and o.scale.x > 0.1]
    assert tears, "crying: tears"
    at(times["nervous"] + 0.6)
    assert any(".sweat" in o.name and o.scale.x > 0.1 for o in bpy.data.objects), "nervous: sweat"
    at(t_half)
    half = kv(girl.mouth_mesh, "smile")
    at(t_more)
    assert half < 0.7 and kv(girl.mouth_mesh, "smile") > 1.0, ("how_much", half)
    # the frog's bead eyes still take moods
    at(times["crazed"])
    assert kv(frog.irises[0], "upper") < 0.01
    vals = face.values(plugins.get("mood", "furious"), 1.5)
    assert vals["brow_tilt"] < plugins.get("mood", "furious").brow_tilt, "pushed further"
    print("face: all ok")


if __name__ == "__main__":
    main()
