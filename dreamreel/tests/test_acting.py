"""Acting: moods and manners shape gestures and walks (effort), gestures anticipate and follow
through, dangly parts lag and settle, jumps squash and stretch, the director cuts on action.

    python tests/test_acting.py
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import dreamreel as dr  # noqa: E402
from dreamreel import keys  # noqa: E402


def wave(how=None, mood=None):
    s = dr.Scene({"kind": "room"})
    mia = s.cast(mia=dict(hair="ponytail"))
    mia.place("center")
    if mood:
        mia.feel(mood, at=0)
    t0 = s.clock
    mia.do("wave", how=how)
    t1 = s.clock
    ys = [keys.sample(mia.arms[1], "rotation_euler", t0 + i * 0.02)[1] for i in range(int((t1 - t0) / 0.02) + 1)]
    return t1 - t0, ys


def main():
    assert {"angrily", "sadly", "nervously", "proudly", "sneakily"} <= set(dr.names("manner"))
    plain, ys = wave()
    angry, ya = wave("angrily")
    sad, yd = wave("sadly")
    assert angry < plain < sad, (angry, plain, sad)
    assert min(ya) <= min(ys) + 0.01 < min(yd), "angry waves are no smaller (overhead poses don't grow), sad ones smaller"
    assert max(ys) > 0.02, "anticipation: the arm first moves the other way"
    moody, _ = wave(mood="sad")
    assert abs(moody - sad) < 0.15, "the mood shapes a gesture like the manner does"

    # walks: angry is quicker than sad
    lengths = {}
    for how in ("angrily", None, "sadly"):
        s = dr.Scene({"kind": "room"})
        tom = s.cast(tom={})
        tom.place("left")
        a = s.clock
        tom.walk_to("right", how=how)
        lengths[how] = s.clock - a
    assert lengths["angrily"] < lengths[None] < lengths["sadly"], lengths

    # follow-through: a ponytail swings when its owner stops, then settles
    s = dr.Scene({"kind": "room"})
    mia = s.cast(mia=dict(hair="ponytail"))
    dog = s.cast(dog=dict(type="creature", body="quadruped", ears="floppy"))
    mia.place("left", facing="right")
    dog.place("front-left", facing="right")
    mia.walk_to("right")
    stop = s.clock
    mia.do("jump")
    s.wait(2)
    s.finish()
    piv = mia.danglers[0][0]
    swing = [abs(keys.sample(piv, "rotation_euler", stop + i * 0.05)[0]) for i in range(10)]
    assert max(swing) > math.radians(5), "it swings"
    assert abs(keys.sample(piv, "rotation_euler", s.length - 0.2)[0]) < math.radians(1), "and settles"
    assert len(dog.danglers) == 2, "floppy ears dangle"
    # squash and stretch on the jump
    zs = [keys.sample(mia.body, "scale", stop + i * 0.05)[2] for i in range(40)]
    assert min(zs) < 0.95 and max(zs) > 1.05, (min(zs), max(zs))

    # the automatic director cuts a moment into a movement, not before it
    s = dr.Scene({"kind": "room"})
    a, b = s.cast(a={}, b={})
    a.place("left")
    b.place("right")
    a.say("Look!")
    t = s.clock
    a.walk_to("door" if "door" in s.set.marks else "back")
    s.wait(1)
    s.finish()
    cuts = [sh.at for sh in s.cut.final if sh.at > t - 0.05]
    assert cuts and all(c >= t + 0.1 for c in cuts), (t, cuts)

    # exaggeration comes from the style unless film.toml says otherwise
    assert dr.Scene({"kind": "room"}, style="toon").exaggeration > dr.Scene({"kind": "room"}, style="realistic").exaggeration
    print("acting: ok")


if __name__ == "__main__":
    main()
