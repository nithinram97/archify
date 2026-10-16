"""Every body plan builds, walks, turns and does what its body allows (no rendering).

    python tests/test_creatures.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import dreamreel as dr  # noqa: E402
from dreamreel.keys import value_at  # noqa: E402

PLANS = {
    "biped": dict(ears="pointy"),
    "quadruped": dict(wings=True, horns="ram", pattern="spots"),
    "bird": {},
    "fish": dict(pattern="stripes"),
    "serpent": {},
    "bug": {},
    "spider": {},
    "blob": {"float": True},
    "frog": dict(iris="#8a5fd1", size=0.6),
}


def main():
    assert set(PLANS) <= set(dr.names("body")), dr.names("body")
    for plan, extra in PLANS.items():
        s = dr.Scene({"kind": "outdoor", "trees": 0, "hills": 0})
        c = s.cast(it=dict(type="creature", body=plan, **extra))
        c.place((-1.5, 0), facing="right")
        c.walk_to((1.5, 0.5))
        c.turn_to("camera")
        c.say("Hello!", mood="happy")
        for g, cls in dr.registry("gesture").items():
            if not set(cls.needs) - c.capabilities:
                c.do(g)
        if "fly" in c.capabilities:
            c.fly_to((0, 1), height=1.0)
        if "arms" not in c.capabilities:
            try:
                c.do("wave")
                raise AssertionError(f"{plan}: waved without arms")
            except ValueError as e:
                assert "can't" in str(e), e
        s.finish()
        end = value_at(c.root, "location", s.length)
        assert abs(end[0] - (0 if "fly" in c.capabilities else 1.5)) < 0.8, (plan, end)
        if c.feet:   # feet end up under the body
            for leg, target in c.feet.items():
                foot = value_at(target, "location", s.length)
                home = c.home_at(leg, dr.character.Vector((end[0], end[1])), c.heading(s.length))
                assert (dr.character.Vector(foot) - home).length < 0.5 * c.size, (plan, leg, foot, home)
        print(f"{plan:10} ok  {len(c.skel.joints):2} joints, {len(c.feet)} feet, can: {', '.join(sorted(c.capabilities))}")
    # the frog: hops (body and feet leave the ground), croaks, flicks its tongue, has hands
    s = dr.Scene({"kind": "room"})
    f = s.cast(frog=dict(type="creature", body="frog", size=0.55))
    f.place("left", facing="right")
    f.walk_to("right")
    f.do("croak")
    f.do("tongue")
    f.do("cheer")
    s.finish()
    hips = [value_at(f.hips, "location", i * 0.05)[2] for i in range(60)]
    feet = [value_at(f.feet["leg.L"], "location", i * 0.05)[2] for i in range(60)]
    assert max(hips) > 0.2 and max(feet) > 0.1, (max(hips), max(feet))
    assert {"croak", "tongue", "arms", "hop"} <= f.capabilities
    assert f.sac.scale[0] < 0.5 and f.tongue.scale[1] < 0.05, "sac and tongue are hidden at rest"
    print("OK")


if __name__ == "__main__":
    main()
