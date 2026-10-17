"""Humans from MakeHuman's assets: shape by age and sex, fitted clothes and hair, MakeHuman's rig,
expressions driven by moods. Skipped when the assets aren't set up (dreamreel makehuman --download).

    python tests/test_makehuman.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import handling, makehuman  # noqa: E402


def at(s, obj, t):
    handling.evaluate(s, t)
    return obj.matrix_world.translation.copy()


def top(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    zs = []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        zs += [(ev.matrix_world @ v.co).z for v in me.vertices]
        ev.to_mesh_clear()
    return min(zs), max(zs)


def main():
    if not makehuman.available():
        print("makehuman: skipped (no assets; run `dreamreel makehuman --download` and --use a MakeHuman checkout)")
        return
    clothes_ok = makehuman.find_asset("clothes", "female_casualsuit01") is not None
    s = dr.Scene({"kind": "room", "size": "large"})
    ann, kid, sam = s.cast(
        ann=dict(type="human", gender=0.0, age=30, eye_color="blue",
                 **(dict(hair="bob01", clothes=["female_casualsuit01", "shoes02"]) if clothes_ok else {})),
        kid=dict(type="human", gender=1.0, age=8),
        sam=dict(type="human", gender=1.0, age=40, height=1.85, shape={"nose-scale-horiz": 0.5}))
    ann.place("left", facing="camera")
    kid.place("center", facing="camera")
    sam.place("right", facing="camera")
    handling.evaluate(s, 0.0)
    # sizes: an adult woman, a shorter child, a man exactly as tall as asked
    lo, hi = top(ann.meshes)
    assert abs(lo) < 0.03 and 1.5 < hi < 1.85, ("ann", lo, hi)
    assert top([kid.meshes[0]])[1] < hi - 0.2, "the child is shorter"
    assert abs(top([sam.meshes[0]])[1] - 1.85) < 0.02, "height in metres"
    assert sam.rig.data.bones.get("finger2-1.L") is not None, "MakeHuman's rig, fingers and all"
    assert {"eye-left-closure", "mouth-corner-puller", "mouth-open"} <= set(ann.units)
    if clothes_ok:
        names = [o.name for o in ann.meshes]
        assert any(".clothes" in n for n in names) and any(".hair" in n for n in names), names
        full = sum(1 for _ in kid.meshes[0].data.vertices)
        assert len(ann.meshes[0].data.vertices) < full, "the body under the clothes is hidden"
    # acting: moods drive the expression units; waves and walks
    ann.feel("happy")
    t_happy = s.clock + 0.5
    s.wait(0.8)
    ann.feel("sad")
    t_sad = s.clock + 0.5
    s.wait(0.8)
    t0 = s.clock
    ann.do("wave")
    t_wave = t0 + 0.6
    t_start = s.clock
    ann.walk_to("front")
    t_walk = s.clock - 0.2
    s.wait(0.5)
    s.finish()
    smile = ann.units["mouth-corner-puller"][0]
    handling.evaluate(s, t_happy)
    happy = smile.value
    handling.evaluate(s, t_sad)
    assert happy > 0.5 and smile.value < 0.2, ("smiles when happy", happy, smile.value)
    assert ann.units["mouth-depression"][0].value > 0.5, "frowns when sad"
    assert at(s, ann.hands[1], t_wave).z > at(s, ann.arms[1], t_wave).z - 0.05, "the waving hand is up"
    assert (at(s, ann.root, t_walk) - at(s, ann.root, t_start)).length > 0.5, "she walks"
    print("makehuman: all ok")


if __name__ == "__main__":
    main()
