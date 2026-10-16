"""Editing: time effects move the animation, transitions and screen effects build, the edit list adds up.

    python tests/test_editing.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import cli  # noqa: E402
from dreamreel.editing import Clip, Editor  # noqa: E402


def walk(effect=None, **kw):
    """Mia walks across a room; `effect` (a Scene method name) runs before the walk starts."""
    s = dr.Scene({"kind": "room"})
    mia = s.cast(mia={})
    mia.place("left", facing="right")
    if effect:
        getattr(s, effect)(**kw)
    mia.walk_to("right")
    s.wait(1)
    s.finish()
    return s, mia


def x_at(mia, t):
    return mia.where_at(t)[0].x


def close(a, b, tol=0.03):
    return abs(a - b) <= tol


def main():
    plain, mia = walk()
    base = {t: x_at(mia, t) for t in (0.5, 1.0, 1.5, 2.0, 2.5)}
    base_len = plain.length

    # slow motion: half speed for the first two story-seconds, so story time 1.0 shows at 2.0
    s, mia = walk("slow_motion", seconds=2.0, speed=0.5, ramp=0.0)
    assert close(x_at(mia, 2.0), base[1.0]), (x_at(mia, 2.0), base[1.0])
    assert close(x_at(mia, 1.0), base[0.5]), (x_at(mia, 1.0), base[0.5])
    assert close(s.length, base_len + 2.0, 0.1), (s.length, base_len)
    assert s.bscene.frame_end >= int((s.length - 0.1) * s.fps), "the render range covers the slowed scene"
    assert any("SLOW" in r[2] for r in s.time_fx)

    # a ramped slow motion is smooth: the figure only ever moves forward
    s, mia = walk("slow_motion", seconds=2.0, speed=0.3, ramp=0.5)
    xs = [x_at(mia, i / 12) for i in range(int(s.length * 12))]
    assert all(b >= a - 1e-3 for a, b in zip(xs, xs[1:])), "slow motion never goes backwards"

    # freeze: everything holds for 1 s at 1.0, then carries on where it was
    s, mia = walk("freeze", seconds=1.0, after=1.0)
    assert close(x_at(mia, 1.0), base[1.0]) and close(x_at(mia, 1.9), base[1.0]), "frozen"
    assert close(x_at(mia, 2.5), base[1.5]), (x_at(mia, 2.5), base[1.5])
    assert close(s.length, base_len + 1.0, 0.1)

    # jump cut: story 1.0 to 2.0 is cut out, so 1.5 shows what 2.5 showed
    s, mia = walk("jump_cut", seconds=1.0, after=1.0)
    assert close(x_at(mia, 0.5), base[0.5])
    assert close(x_at(mia, 1.5), base[2.5]), (x_at(mia, 1.5), base[2.5])
    assert close(s.length, base_len - 1.0, 0.1)

    # screen effects are recorded for the edit, and move with time effects before them
    s = dr.Scene({"kind": "room"})
    mia = s.cast(mia={})
    mia.place("center")
    s.slow_motion(seconds=1.0, speed=0.5, ramp=0.0)
    s.wait(2)
    s.screen("flash")
    s.screen("fade_out", duration=1.0)
    s.finish()
    meta = s.metadata()
    assert [fx for _, fx, _, _ in meta["screen"]] == ["flash", "fade_out"]
    assert close(meta["screen"][0][0], 3.0, 0.05), meta["screen"]
    assert meta["screen"][0][3] == "white", "flash defaults to white"

    # scene transitions come from the scene file
    spec = {"set": {"kind": "room"}, "transition": "wipe", "transition_direction": "right",
            "beats": [{"do": "wait", "seconds": 1}]}
    s = dr.Scene.from_spec(spec)
    assert s.transition["name"] == "wipe" and s.transition["direction"] == "right"

    # every transition and screen effect builds in the sequencer
    assert set(dr.names("transition")) >= {"cut", "fade", "dissolve", "wipe", "iris", "clock", "push", "whip",
                                           "zoom", "flash"}
    assert set(dr.names("screen")) >= {"fade_out", "fade_in", "flash", "dip", "blackout"}
    for name, cls in dr.registry("transition").items():
        for direction in (None, "left", "right", "up", "down", "in"):
            bpy.ops.wm.read_factory_settings(use_empty=True)
            sc = bpy.context.scene
            sc.render.resolution_x, sc.render.resolution_y = 320, 180
            ed = Editor(sc, 24)
            a = ed.color(1, 49, "red", channel=2)
            b = ed.color(25, 73, "blue", channel=3)
            ca, cb = Clip("scene", 1, 48, [a], channel=2), Clip("scene", 25, 48, [b], channel=3)
            before = len(ed.strips)
            cls().apply(ed, ca, cb, 25, 24, color="white", direction=direction)
            if name not in ("cut", "dissolve", "push", "whip", "zoom"):
                assert len(ed.strips) > before, f"{name} adds a strip"
            sc.frame_set(37)   # mid-transition evaluates
    for name, cls in dr.registry("screen").items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        ed = Editor(bpy.context.scene, 24)
        st = cls().apply(ed, 10, 24, cls.default_color)
        assert st is not None, name

    # the edit list: trims, overlaps and L-cuts add up
    built = {"a": (5.0, 0.0, None), "b": (4.0, 2.0, {"name": "dissolve", "duration": 1.0}), "c": (3.0, 0.0, None)}
    total, lines = cli._edit_plan([{"scene": "a", "to": 3.0}, {"scene": "b"}, {"scene": "a", "from": 3.0},
                                   {"scene": "c", "transition": "fade", "audio": "l", "audio_seconds": 0.5},
                                   {"split": ["a", "c"]}], built)
    # 3 + (2 card + 4 - 1 dissolve) + 2 + (3 - 0.5) + 3
    assert close(total, 15.5, 1e-6), (total, lines)
    assert len(lines) == 5 and "dissolve" in lines[1] and "fade" in lines[3] and "a | c" in lines[4], lines
    print("editing: ok")


if __name__ == "__main__":
    main()
