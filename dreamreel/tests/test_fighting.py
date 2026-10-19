"""Fighting (fighting.py): strikes and reactions meet; knockdowns fly, land, lie and get up; moods
shape moves without moving the blow; the camera feels the hits; clones; and the choreography (surround,
brawl, burst, bullet time).

    python tests/test_fighting.py
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402,F401

import dreamreel as dr  # noqa: E402
from dreamreel import fighting  # noqa: E402
from dreamreel.keys import value_at  # noqa: E402


def two(spec_a=None, spec_b=None):
    s = dr.Scene({"kind": "outdoor", "biome": "meadow", "trees": 0})
    a, b = s.cast(a=spec_a or {}), s.cast(b=spec_b or {})
    a.place((-0.5, 0), facing="right")
    b.place((0.5, 0), facing="left")
    return s, a, b


def moves():
    g = dr.get
    assert issubclass(g("gesture", "jab"), g("gesture", "punch")) and issubclass(g("gesture", "punch"), fighting.Strike)
    assert issubclass(g("gesture", "spin_kick"), fighting.LegStrike) and issubclass(g("gesture", "block"), fighting.Reaction)
    for name in ("hook", "uppercut", "kick", "spin_kick", "flying_kick", "sweep"):
        s, a, b = two()
        t = s.clock
        a.do(name, target="b")
        b.do("flinch", target="a", at=t)           # started together: it meets the blow whenever it lands
        s.finish()
        hit = t + g("gesture", name).impact
        smack = [ts for ts, _, _, n in s.sound_fx if n == "punch_heavy"]
        assert smack and abs(smack[0] - hit) < 0.02, (name, smack, hit)
    print("  moves: ok (every strike meets its reaction)")


def mood_keeps_time():
    s, a, b = two()
    a.feel("sad")                                    # a sad body is slow, but a blow lands when it lands
    t = s.clock
    a.do("punch", target="b")
    b.do("block", target="a", at=t)
    s.finish()
    block = [ts for ts, _, _, n in s.sound_fx if n == "block"][0]
    assert abs(block - (t + fighting.IMPACT)) < 0.02, block
    print("  moods: ok (they shape a move, not its timing)")


def knockdown():
    s, a, b = two()
    t = s.clock
    a.do("uppercut", target="b")
    b.do("knocked_down", target="a", at=t)
    s.finish()
    hit = t + dr.get("gesture", "uppercut").impact
    start = b.position(hit)
    _, down = b._down                                # (when the blow landed, when they start getting up)
    tilt = math.degrees(value_at(b.root, "rotation_euler", down - 0.1)[0])
    assert tilt < -80, ("lying on the back", tilt)
    flown = (b.position(down) - start)
    assert flown.length > 1.2 and flown.x > 0, ("thrown away from the blow", flown)
    peak = max(value_at(b.root, "location", hit + k * 0.05)[2] for k in range(12))
    assert peak > 0.2, ("through the air", peak)
    end = s.length
    assert abs(value_at(b.root, "rotation_euler", end)[0]) < 0.05 and abs(value_at(b.root, "location", end)[2]) < 0.02, \
        "back on their feet"
    assert s.cut.impulses and any(o.name == "camera.shaker" for o in bpy.data.objects), "the camera feels it"
    assert any(n == "thud" for *_, n in s.sound_fx)
    print(f"  knockdown: ok (thrown {flown.length:.1f} m, {peak:.2f} m high, lying, up again)")


def clones():
    s = dr.Scene({"kind": "room"})
    cs = s._add_copies("agent", {"hair": "short"}, 3)
    assert [c.key for c in cs] == ["agent_1", "agent_2", "agent_3"] and len({c.name for c in cs}) == 3
    assert [c.key for c in s.matching("agent_*")] == ["agent_1", "agent_2", "agent_3"]
    assert all(c.spec.get("seed") == "agent" for c in cs), "copies share a seed (the same face)"
    print("  clones: ok")


def choreography():
    s = dr.Scene({"kind": "outdoor", "biome": "meadow", "trees": 0})
    hero = s.cast(hero={})
    crowd = s._add_copies("goon", {"hair": "short", "top": "#333333"}, 5)
    hero.place((0, 0), facing="camera")
    t0 = s.clock
    ready = fighting.surround(s, "hero", [c.key for c in crowd], t0, radius=1.8, seed=1, enter_from=6)
    for c in crowd:
        assert abs((c.position(ready) - hero.position(ready)).length - 1.8) < 0.5, "a ring round the hero"
        assert (c.position(0) - hero.position(0)).length > 4, "they came from out there"
    end = fighting.brawl(s, "hero", [c.key for c in crowd], ready, exchanges=5, seed=3)
    assert end - ready < 5 * 4.0, ("the brawl keeps moving", end - ready)
    hits = [ts for ts, _, _, n in s.sound_fx if n == "punch_heavy" and ready < ts < end]
    assert len(hits) >= 5, hits
    strikes = sorted((e["t0"], e["who"].key) for e in s.events if e["kind"] == "gesture" and e["who"] is not hero
                     and issubclass(dr.get("gesture", e["gesture"]), fighting.Strike))
    assert strikes, "the attackers attack"
    for (ta, wa), (tb, wb) in zip(strikes, strikes[1:]):
        assert tb - ta > 0.3, ("one at a time", ta, wa, tb, wb)
    s.clock = end
    b = fighting.burst(s, "hero", [c.key for c in crowd], end)
    s.finish()
    after = s.length
    for c in crowd:
        assert (c.position(after) - hero.position(after)).length > 1.8, ("thrown clear", c.key)
    assert s.cut.shots, "the camera covers it"
    print(f"  choreography: ok (surround, {len(strikes)} attacks and {len(hits)} hits in {end - ready:.1f} s, burst)")


def bullet_time():
    s, a, b = two()
    dr.get("action", "bullet_time")().run(s, None, of="a", seconds=0.8, speed=0.25, amount=120)
    t = s.clock
    a.do("flying_kick", target="b")
    b.do("knocked_down", target="a", at=t)
    s.finish()
    assert s.warps_applied and any("orbit" in label for _, label in s.cut.describe())
    print("  bullet time: ok")


def main():
    moves()
    mood_keeps_time()
    knockdown()
    clones()
    choreography()
    bullet_time()
    print("fighting: all ok")


if __name__ == "__main__":
    main()
