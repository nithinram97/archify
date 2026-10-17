"""People: stylized humans of three ages, with a skinned body, a sculpted head and the full face.

    python tests/test_people.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import handling  # noqa: E402


def at(s, obj, t):
    handling.evaluate(s, t)
    return obj.matrix_world.translation.copy()


def extent(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    zs = []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        zs += [(ev.matrix_world @ v.co).z for v in me.vertices]
        ev.to_mesh_clear()
    return min(zs), max(zs)


def skin_near(c, point):
    dg = bpy.context.evaluated_depsgraph_get()
    m = c.meshes[0]
    tree = BVHTree.FromObject(m, dg)
    hit = tree.find_nearest(m.matrix_world.inverted() @ point)
    return (m.matrix_world @ hit[0] - point).length


def main():
    s = dr.Scene({"kind": "room", "size": "large", "props": [{"type": "table", "place": "back", "items": ["cup"]}]})
    maya, sam, ann = s.cast(
        maya=dict(type="person", hair="space_buns", eye_color="#5a3a22", outfit="skirt", freckles=True, braces=True,
                  brows="thick"),
        sam=dict(type="person", age="teen", outfit="shorts", sleeves="short", skin="#8d5a3b"),
        ann=dict(type="person", age="adult", hair="long", outfit="dress", height=1.7))
    maya.place("center", facing="camera")
    sam.place("left", facing="camera")
    ann.place("right", facing="camera")
    # sizes: each as tall as asked (head included), standing on the floor
    handling.evaluate(s, 0.0)
    for c, h in ((maya, 1.0), (sam, 1.3), (ann, 1.7)):
        head = [o for o in bpy.data.objects if o.name.startswith(f"{c.name}.head")]
        lo, _ = extent(c.meshes)
        _, top = extent(head)
        assert abs(lo) < 0.03 and abs(top - h) < 0.06 * h, (c.name, lo, top)
        assert 0.8 * h < c.head_point(0.0).z < h, (c.name, "face height", c.head_point(0.0))
    # the face: white eyes with irises, lashes, freckles, braces, teeth, sculpted nose
    names = [o.name for o in bpy.data.objects]
    for part in ("Maya.iris", "Maya.lash", "Maya.lashline", "Maya.lid", "Maya.lip", "Maya.freckle", "Maya.braces",
                 "Maya.ear", "Maya.skirt", "Maya.brow"):
        assert any(n.startswith(part) for n in names), part
    assert not any(n.startswith("Sam.freckle") for n in names)
    # clothes by region: shorts leave the shins bare, long sleeves cover the forearms
    body = sam.meshes[0]
    mats = [m.name for m in body.data.materials]
    shin = [p for p in body.data.polygons if 0.12 * 1.3 < p.center.z < 0.2 * 1.3 and abs(p.center.x) < 0.12]
    assert shin and sum(mats[p.material_index].startswith("skin") for p in shin) > 0.8 * len(shin), "bare shins"
    # acting: a wave, a walk, carrying a cup, a crazed grin
    t0 = s.clock
    maya.do("wave")
    t_wave = t0 + 0.6
    start = maya.position(s.clock)
    maya.pick_up("cup")
    t_held = s.clock + 0.1
    maya.walk_to("front")
    t_walk = s.clock - 0.2
    maya.feel("crazed")
    t_crazed = s.clock + 0.5
    s.wait(1)
    s.finish()
    hand = maya.hands[1]
    shoulder = at(s, maya.arms[1], t_wave)
    assert at(s, hand, t_wave).z > shoulder.z - 0.03, "the waving hand is up"
    assert skin_near(maya, at(s, hand, t_wave)) < 0.06, "and the skin follows it"
    cup = s.set.things["cup"].root
    held = min((at(s, cup, t_held) - at(s, maya.hands[k], t_held)).length for k in (1, -1))
    assert held < 0.1, ("cup in hand", held)
    assert (maya.position(t_walk) - start).length > 0.5
    # skin lids slide over the eyeballs: open at rest, they close in a blink and narrow when sleepy
    up = maya.lid_pivots[1][0]
    angles = []
    for k in range(int(s.length * 24)):
        handling.evaluate(s, k / 24)
        angles.append(up.rotation_euler.x)
    assert min(angles) < -0.4 and max(angles) > 0.1, ("lids open and blink", min(angles), max(angles))
    handling.evaluate(s, t_crazed)
    assert maya.teeth["upper"].scale.z > 0.1 and maya.gazes[0].scale.x < 0.8, "crazed grin, tiny pupils"
    try:
        dr.Scene({"kind": "room"}).cast(bad=dict(type="person", age="baby"))
    except ValueError as e:
        assert "age" in str(e)
    else:
        raise AssertionError("unknown age")
    print("people: all ok")


if __name__ == "__main__":
    main()
