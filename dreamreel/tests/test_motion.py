"""The motion library: BVH clips load, joints are found by role, clips retarget onto a toy (arms,
legs, travel, mirroring), walks use library walk clips, and the motions command lists them.

The clips here are tiny skeletons written by the test (dreamreel can't ship real motion capture).

    python tests/test_motion.py
"""
import contextlib
import io
import math
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import dreamreel as dr  # noqa: E402
from dreamreel import cli, handling, keys, motion  # noqa: E402

JOINTS = [  # name, parent, offset (y up, a person facing +z, in centimetres)
    ("Hips", None, (0, 90, 0)), ("LeftUpLeg", "Hips", (10, 0, 0)), ("LeftLeg", "LeftUpLeg", (0, -42, 0)),
    ("LeftFoot", "LeftLeg", (0, -42, 0)), ("RightUpLeg", "Hips", (-10, 0, 0)),
    ("RightLeg", "RightUpLeg", (0, -42, 0)), ("RightFoot", "RightLeg", (0, -42, 0)),
    ("Spine", "Hips", (0, 20, 0)), ("Spine1", "Spine", (0, 20, 0)), ("Neck", "Spine1", (0, 15, 0)),
    ("Head", "Neck", (0, 10, 0)), ("LeftArm", "Spine1", (18, 10, 0)), ("LeftForeArm", "LeftArm", (0, -28, 0)),
    ("LeftHand", "LeftForeArm", (0, -25, 0)), ("RightArm", "Spine1", (-18, 10, 0)),
    ("RightForeArm", "RightArm", (0, -28, 0)), ("RightHand", "RightForeArm", (0, -25, 0)),
]


def write_bvh(path, frames=61, fps=30, walk=False, raise_left=True):
    """A skeleton that raises its left arm sideways to horizontal (or walks forward, swinging legs)."""
    kids = {}
    for n, par, off in JOINTS:
        kids.setdefault(par, []).append((n, off))
    lines = ["HIERARCHY"]

    def emit(name, off, depth, root=False):
        ind = "  " * depth
        lines.append(f"{ind}{'ROOT' if root else 'JOINT'} {name}")
        lines.append(ind + "{")
        lines.append(f"{ind}  OFFSET {off[0]} {off[1] if not root else 0} {off[2]}")
        ch = "6 Xposition Yposition Zposition Zrotation Xrotation Yrotation" if root else "3 Zrotation Xrotation Yrotation"
        lines.append(f"{ind}  CHANNELS {ch}")
        for k, o in kids.get(name, []):
            emit(k, o, depth + 1)
        if not kids.get(name):
            lines.extend([f"{ind}  End Site", ind + "  {", f"{ind}    OFFSET 0 -5 0", ind + "  }"])
        lines.append(ind + "}")
    emit("Hips", (0, 0, 0), 0, root=True)
    order = []

    def walk_order(name):
        order.append(name)
        for k, _ in kids.get(name, []):
            walk_order(k)
    walk_order("Hips")
    lines += ["MOTION", f"Frames: {frames}", f"Frame Time: {1 / fps:.6f}"]
    for i in range(frames):
        u = i / (frames - 1)
        row = []
        for n in order:
            if n == "Hips":
                row += [0, 90, (u * 260 if walk else 0), 0, 0, 0]
            elif n == "LeftArm" and raise_left and not walk:
                row += [90 * min(1, u * 2), 0, 0]          # out to the side, then held
            elif n in ("LeftUpLeg", "RightUpLeg") and walk:
                s = 1 if n == "LeftUpLeg" else -1
                row += [0, s * 25 * math.sin(u * 4 * math.pi), 0]
            else:
                row += [0, 0, 0]
        lines.append(" ".join(f"{v:.4f}" for v in row))
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    tmp = tempfile.mkdtemp(prefix="dreamreel-motion-")
    try:
        lib_dir = os.path.join(tmp, "motions")
        os.makedirs(lib_dir)
        write_bvh(os.path.join(lib_dir, "arm_up.bvh"))
        write_bvh(os.path.join(lib_dir, "walk_test.bvh"), frames=121, walk=True)
        lib = motion.Library(tmp)
        assert lib.names() == ["arm_up", "walk_test"], lib.names()
        clip = lib.get("arm_up")
        assert abs(clip.length - 2.0) < 0.05 and abs(clip.hip_height - 84) < 6, (clip.length, clip.hip_height)
        assert "walk" in lib.get("walk_test").tags and lib.get("walk_test").speed() > 0.5

        # retarget onto a toy: the left arm comes up to the side, the right arm stays down
        s = dr.Scene({"kind": "room"})
        s._motions = lib
        mia = s.cast(mia={})
        mia.place("center", facing="camera")
        t0 = s.clock
        mia.perform("arm_up")
        t_end = s.clock
        s.finish()
        handling.evaluate(s, t0 + 1.8)
        sh = mia.arms[1].matrix_world.translation
        hand_l = mia.hands[1].matrix_world.translation
        hand_r = mia.hands[-1].matrix_world.translation
        assert abs(hand_l.z - sh.z) < 0.08 and hand_l.x > sh.x + 0.1, ("left arm out to the side", hand_l, sh)
        assert hand_r.z < mia.arms[-1].matrix_world.translation.z - 0.15, "right arm still down"
        assert t_end > t0 + 1.9

        # mirrored: the right arm does it instead
        s = dr.Scene({"kind": "room"})
        s._motions = lib
        mia = s.cast(mia={})
        mia.place("center", facing="camera")
        t0 = s.clock
        mia.perform("arm_up", mirror=True)
        s.finish()
        handling.evaluate(s, t0 + 1.8)
        hand_r = mia.hands[-1].matrix_world.translation
        assert abs(hand_r.z - mia.arms[-1].matrix_world.translation.z) < 0.08, "mirrored"

        # travel: the walk clip carries the character forward (the way they face), unless in place
        for in_place in (False, True):
            s = dr.Scene({"kind": "room", "size": "large"})
            s._motions = lib
            tom = s.cast(tom={})
            tom.place("left", facing="right")
            p0 = tom.position(0)
            tom.perform("walk_test", in_place=in_place)
            s.finish()
            moved = tom.position(s.length) - p0
            if in_place:
                assert moved.length < 0.05, moved
            else:
                assert moved.x > 0.5 and abs(moved.y) < 0.2, ("walked to their right-facing front", moved)

        # walk_to uses the library's walk clip: legs swing from the clip, the path is followed
        s = dr.Scene({"kind": "room", "size": "large"})
        s._motions = lib
        tom = s.cast(tom={})
        tom.place("left", facing="right")
        tom.walk_to("right")
        s.finish()
        swings = {round(keys.sample(tom.legs[1], "rotation_euler", 0.5 + i * 0.1)[0], 3) for i in range(15)}
        assert len(swings) > 5, "the legs move with the clip"

        # the motions command
        cli.main(["new", os.path.join(tmp, "film")])
        old = os.getcwd()
        os.chdir(os.path.join(tmp, "film"))
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                cli.main(["motions", "--add", os.path.join(lib_dir, "walk_test.bvh"), "--name", "stroll", "--tags", "walk"])
                cli.main(["motions"])
            text = buf.getvalue()
            assert "stroll" in text and "walk" in text, text
        finally:
            os.chdir(old)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("motion: ok")


if __name__ == "__main__":
    main()
