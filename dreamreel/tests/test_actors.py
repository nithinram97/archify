"""People and animals from Quaternius's packs: a woman walks, waves and picks up a cup; a husky walks
and a horse gallops; a deer eats; heads turn to look. Skipped when the packs aren't downloaded
(`dreamreel assets --download --pack women` and so on).

    python tests/test_actors.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import dreamreel as dr  # noqa: E402
from dreamreel import handling, quaternius  # noqa: E402


def at(s, obj, t):
    handling.evaluate(s, t)
    return obj.matrix_world.translation.copy()


def clips_at(c, t):
    """Names of the clips (NLA strips) playing at time t."""
    f = dr.keys.CLOCK.frame(t)
    return {st.action.name.split("|")[-1].split(".")[0] for tr in c.rig.animation_data.nla_tracks
            for st in tr.strips if st.frame_start <= f <= st.frame_end}


def people():
    s = dr.Scene({"kind": "room", "props": [{"type": "table", "place": "back", "items": ["cup"]}]})
    mia, ben = s.cast(mia=dict(type="person", body="woman", outfit="casual"),
                      ben=dict(type="person", body="man", outfit="suit", height=1.85))
    assert {"walk", "run", "wave", "idle"} <= set(mia.clip_names), sorted(mia.clip_names)
    mia.place("left", facing="camera")
    ben.place("right", facing="mia")
    t_wave = s.clock + 0.6
    mia.do("wave")
    start = at(s, mia.root, s.clock)
    t_go = s.clock
    mia.walk_to("center")
    t_walk = (t_go + s.clock) / 2
    mia.pick_up("cup")
    t_held = s.clock
    t_still = s.clock
    ben.look_at("door" if "door" in s.set.marks else "back")
    t_look = s.clock + 0.5
    s.wait(1)
    s.finish()
    handling.evaluate(s, 0.0)
    for c, h in ((mia, 1.68), (ben, 1.85)):
        hp = c.head_point(0.0).z
        assert 0.8 * h < hp < 1.05 * h, (c.name, "the head is at the top", hp, h)
    assert "Wave" in clips_at(mia, t_wave), clips_at(mia, t_wave)
    assert "Walk" in clips_at(mia, t_walk), clips_at(mia, t_walk)
    assert (at(s, mia.root, s.clock) - start).length > 0.5, "she walked"
    side = next(iter(mia.holding))
    cup = s.set.things["cup"].root
    assert (at(s, cup, t_held) - at(s, mia.hands[side], t_held)).length < 0.05, "the cup is in her hand"
    assert (at(s, cup, s.clock) - at(s, mia.hands[side], s.clock)).length < 0.05, "and stays there"
    turn = dr.keys.value_at(ben.neck, "rotation_euler", t_look)[2]
    assert abs(turn) > 0.2, ("he turns his head", turn)
    head = ben.rig.pose.bones[next(h for h in ben.head_names if h in ben.rig.pose.bones)]
    handling.evaluate(s, t_still)
    q0 = (ben.rig.matrix_world @ head.matrix).to_quaternion()
    handling.evaluate(s, t_look)
    q1 = (ben.rig.matrix_world @ head.matrix).to_quaternion()
    assert q0.rotation_difference(q1).angle > 0.6 * abs(turn), ("the head bone follows", q0, q1, turn)
    print("  people: ok")


def animals():
    s = dr.Scene({"kind": "outdoor", "biome": "meadow"})
    rex, star, doe = s.cast(rex=dict(type="animal", species="husky"), star=dict(type="animal", species="horse"),
                            doe=dict(type="animal", species="deer", size=0.8))
    for c, h in ((rex, 0.75), (star, 2.1), (doe, 1.35 * 0.8)):
        assert c.height() == h, (c.name, c.height())
    rex.place((-3, 0), facing="right")
    star.place((-6, 3), facing="right")
    doe.place((3, 2), facing="left")
    t0 = s.clock
    rex.walk_to((1, 0), wait=False)
    star.run_to((6, 3), wait=False)
    doe.do("eat", wait=False)
    s.wait(1.5)
    s.finish()
    assert "Walk" in clips_at(rex, t0 + 0.8), clips_at(rex, t0 + 0.8)
    assert "Gallop" in clips_at(star, t0 + 0.8), clips_at(star, t0 + 0.8)
    assert "Eating" in clips_at(doe, t0 + 0.5), clips_at(doe, t0 + 0.5)
    assert (at(s, rex.root, s.length) - at(s, rex.root, 0)).length > 3.5, "the dog walked"
    assert (at(s, star.root, s.length) - at(s, star.root, 0)).length > 11, "the horse galloped"
    try:
        s.cast(nessie=dict(type="animal", species="plesiosaur"))
    except ValueError as e:
        assert "plesiosaur" in str(e)
    else:
        raise AssertionError("an unknown species is an error")
    print("  animals: ok")


def main():
    have = quaternius.installed()
    if not {"women", "men"} <= have:
        print("actors: skipped (no Quaternius people: `dreamreel assets --download --pack women --pack men`)")
    else:
        people()
    if "animals" not in have:
        print("actors: skipped (no Quaternius animals: `dreamreel assets --download --pack animals`)")
    else:
        animals()
    print("actors: all ok")


if __name__ == "__main__":
    main()
