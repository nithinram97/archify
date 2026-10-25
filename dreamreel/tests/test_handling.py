"""Handling things: pick up, carry, give, put down, drop, hold new items, grab a small character.

    python tests/test_handling.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import dreamreel as dr  # noqa: E402
from dreamreel import handling  # noqa: E402

KITCHEN = {"kind": "room", "props": [{"type": "table", "place": "center", "items": ["cup", "book"]},
                                     {"type": "counter", "place": "back-right"}]}


def at(s, obj, t):
    handling.evaluate(s, t)
    return obj.matrix_world.translation.copy()


def main():
    s = dr.Scene(KITCHEN)
    mia, tom = s.cast(mia={}, tom={})
    mia.place("left", facing="right")
    tom.place("right", facing="left")
    assert {"cup", "book"} <= set(s.set.things)
    mia.pick_up("cup")
    t_carry = s.clock + 0.2
    mia.walk_to("front")
    t_walk = s.clock - 0.5
    mia.give("tom")
    t_given = s.clock
    tom.put_down(on="counter")
    t_down = s.clock
    tom.hold("scalpel")
    tom.drop()
    s.wait(1)
    s.finish()
    cup = s.set.things["cup"].root
    for t in (t_carry, t_walk):
        assert (at(s, cup, t) - at(s, mia.hands[-1], t)).length < 0.1, f"the cup is in Mia's hand at {t}"
    assert (at(s, cup, t_given) - at(s, tom.hands[-1], t_given)).length < 0.1, "Tom has it"
    end = at(s, cup, s.length - 0.1)
    cx, cy, h = s.set.surfaces["counter"]
    assert abs(end.z - h) < 0.02 and abs(end.x - cx) < 1.2 and abs(end.y - cy) < 0.35, ("on the counter", end)
    assert (at(s, cup, s.length - 0.1) - at(s, cup, t_down + 0.5)).length < 1e-3, "and it stays there"
    scalpel = s.set.things["scalpel"].root
    assert at(s, scalpel, s.length - 0.05).z < 0.05, "a dropped scalpel lands on the floor"
    assert not mia.holding and not tom.holding

    # hands full, no hands
    s = dr.Scene(KITCHEN)
    mia = s.cast(mia={})
    mia.place("table")
    mia.hold("cup")
    mia.hold("book")
    try:
        mia.hold("scalpel")
        raise AssertionError("three things in two hands")
    except ValueError as e:
        assert "full" in str(e)
    snake = s.cast(snake=dict(type="creature", body="serpent"))
    try:
        snake.hold("scalpel")
        raise AssertionError("a snake held something")
    except ValueError as e:
        assert "hands" in str(e)

    # grab a frog off its tray and put it back
    s = dr.Scene({"kind": "room", "furnish": "lab"})
    girl = s.cast(girl={})
    frog = s.cast(frog=dict(type="creature", body="frog", size=0.35))
    frog.place("tray", on="tray")
    girl.place("left", facing="right")
    start = at(s, frog.root, 0.0)
    girl.grab("frog")
    t_held = s.clock + 0.3
    girl.turn_to("camera")
    girl.put_down(on="tray")
    s.wait(1)
    s.finish()
    held = at(s, frog.root, t_held)
    assert (held - at(s, girl.hands[-1], t_held)).length < 0.25, "the frog is in her hand"
    foot = at(s, frog.feet["leg.L"], t_held)
    assert (foot - held).length < 0.3, "its feet came along"
    back = at(s, frog.root, s.length - 0.1)
    assert abs(back.z - s.set.surfaces["tray"][2]) < 0.02 and (back.to_2d() - start.to_2d()).length < 0.4, (back, start)
    print("handling: ok")


if __name__ == "__main__":
    main()
