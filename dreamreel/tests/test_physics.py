"""Physics: knocking over, dropping, throwing (caught and not), kicking a ball on the floor.

    python tests/test_physics.py
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import handling  # noqa: E402

ROOM = {"kind": "room", "size": "large", "props": [{"type": "table", "place": "center", "items": ["vase", "cup"]},
                                                   {"type": "ball", "place": "front-left"}]}


def at(s, obj, t):
    handling.evaluate(s, t)
    return obj.matrix_world.translation.copy()


def tilt(s, obj, t):
    """How far from upright, in degrees."""
    handling.evaluate(s, t)
    up = obj.matrix_world.to_3x3() @ Vector((0, 0, 1))
    return math.degrees(up.angle(Vector((0, 0, 1))))


def ends(s, kind):
    return [e for e in s.events if e["kind"] == "handle" and kind in e["action"].lower()][-1]


def main():
    s = dr.Scene(ROOM)
    mia, tom = s.cast(mia={}, tom={})
    mia.place("left", facing="right")
    tom.place("right", facing="left")
    vase, cup, ball = (s.set.things[n].root for n in ("vase", "cup", "ball"))
    assert at(s, ball, 0).z < 0.01, "a ball in props stands on the floor"
    mia.knock_over("vase")
    k = ends(s, "knocks over")
    mia.pick_up("cup")
    mia.drop()
    d = ends(s, "drops")
    mia.throw("ball", to="tom")
    c = ends(s, "throws ball to tom")
    tom.throw(to="front")
    w = ends(s, "throws ball")
    tom.kick("ball", to="left")
    kk = ends(s, "kicks")
    s.wait(2)
    s.finish()
    h = s.set.surfaces["table"][2]

    # knocked over: tipped right over, lying on the table or the floor, and still
    assert tilt(s, vase, k["t0"]) < 5, "upright before"
    assert tilt(s, vase, k["t1"]) > 60, ("knocked over", tilt(s, vase, k["t1"]))
    rest = at(s, vase, k["t1"])
    assert rest.z < h + 0.15, rest
    assert (at(s, vase, k["t1"] + 1) - rest).length < 0.01, "and it stays down"

    # dropped: falls from the hand to the floor and comes to rest there
    z0 = at(s, cup, d["t0"]).z
    assert at(s, cup, d["t0"] + 0.15).z < z0 - 0.05, "falling"
    assert at(s, cup, d["t1"]).z < 0.1, ("on the floor", at(s, cup, d["t1"]))
    assert (at(s, cup, s.length - 0.1) - at(s, cup, d["t1"])).length < 0.01, "still"

    # thrown and caught: an arc that ends in Tom's hand
    t_arr = c["t1"]
    assert (at(s, ball, t_arr) - at(s, tom.hands[-1], t_arr)).length < 0.12 or \
        (at(s, ball, t_arr) - at(s, tom.hands[1], t_arr)).length < 0.12, "Tom catches it"
    a, b = at(s, ball, c["t0"]), at(s, ball, t_arr)
    mids = [at(s, ball, c["t0"] + (t_arr - c["t0"]) * k_ / 20).z for k_ in range(1, 20)]
    assert max(mids) > max(a.z, b.z) + 0.05, ("it flies in an arc", mids)

    # thrown to a place: lands on the floor somewhere in front and settles
    land = at(s, ball, w["t1"] + 1.5)
    assert land.z < 0.2 and land.y < at(s, tom.root, w["t0"]).y, ("landed in front", land)

    # kicked: off towards the left of the room, stopping inside it
    p0 = at(s, ball, kk["t0"])
    p1 = at(s, ball, kk["t1"])
    goal = s.set.zone("left")
    assert (p1 - p0).length > 1.0 and (p1.to_2d() - goal).length < (p0.to_2d() - goal).length, ("kicked left", p0, p1)
    assert p1.z < 0.2 and abs(p1.x) < s.set.width / 2 and p1.y < s.set.depth / 2, ("in the room", p1)

    # the simulation leaves nothing behind
    assert s.bscene.rigidbody_world is None
    assert not [o for o in bpy.data.objects if o.name.startswith("phys.")]
    print("physics: all ok")


if __name__ == "__main__":
    main()
