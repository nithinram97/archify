"""Gestures: short pieces of body language a character can do. Each one is a class.

    class Dance(dr.Gesture):
        description = "A happy little dance"
        def perform(self, c, t, target=None):
            for i in range(4):                       # sway left and right
                c.lean_at(t + i * 0.4, 12 if i % 2 else -12)
            c.arms_up_at(t + 0.2)
            c.arms_rest(t + 1.8)
            return t + 1.8                           # when the gesture ends

`perform` gets the character and the start time (seconds) and returns the end time. Character has
helpers for poses (`arm_to`, `arms_rest`, `nod_at`, `tilt_head_at`, `hop_at`, `lean_at`, ...), and the
low-level `dr.keys.key(obj, prop, at, value)` is always available for anything else.
"""
from .keys import hold, key, value_at
from .plugins import Param, Plugin
import math


def _deg(d):
    return math.radians(d)


class Gesture(Plugin):
    kind = "gesture"
    abstract = True
    params = [Param("target", "target", label="At / towards")]
    uses_target = False   # True if the gesture points at or turns to its target
    needs = ()            # body capabilities it needs: "arms", "tail", "wings", "rear", ...
    keeps_time = False    # True: the mood shapes it but never changes its timing (moves that must meet others)
    symmetric = False     # True: both sides must move exactly together (hands that meet in a clap)

    @classmethod
    def describe_extra(cls):
        return {"uses_target": cls.uses_target, "needs": list(cls.needs)}

    def perform(self, c, t, target=None):
        """Animate character `c` from time `t`; return the end time."""
        raise NotImplementedError


class Wave(Gesture):
    needs = ("arms",)
    description = "Wave hello or goodbye"

    def perform(self, c, t, target=None):
        up = _deg(-150)
        c.arm_to(1, t + 0.3, (0, up, 0), bent=(_aim(1, -0.25, 0.05, 0.35), 0.75))
        for i in range(4):                    # real proportions: the forearm waves from a bent elbow
            c.arm_to(1, t + 0.45 + i * 0.22, (0, up + _deg(22 if i % 2 else -22), 0),
                     bent=(_aim(1, -0.32 if i % 2 else -0.12, 0.05, 0.35), 0.75))
        c.arm_to(1, t + 1.5, (0, 0, 0))
        return t + 1.5


class Nod(Gesture):
    description = "Nod yes"

    def perform(self, c, t, target=None):
        c.nod_at(t, 12)
        c.nod_at(t + 0.35, 10)
        return t + 0.8


class ShakeHead(Gesture):
    description = "Shake the head no"

    def perform(self, c, t, target=None):
        hold(c.neck, "rotation_euler", t)
        cur = value_at(c.neck, "rotation_euler", t)
        for i, d in enumerate((-20, 20, -16, 12, 0)):
            key(c.neck, "rotation_euler", t + 0.18 * (i + 1), (cur[0], cur[1], cur[2] + _deg(d)))
        return t + 1.0


class Shrug(Gesture):
    needs = ("arms",)
    description = "Shrug: who knows?"

    def perform(self, c, t, target=None):
        for s in (1, -1):
            c.arm_to(s, t + 0.25, (_deg(-35), _deg(-55 * s), 0), reach=0.72)
            c.arm_to(s, t + 0.9, (_deg(-35), _deg(-55 * s), 0), reach=0.72)
        c.tilt_head_at(t, 12)
        c.hop_at(t, 0.02, 0.3, 0.9)
        c.arms_rest(t + 1.2)
        return t + 1.2


class Point(Gesture):
    needs = ("arms",)
    description = "Point at someone or something"
    uses_target = True

    def perform(self, c, t, target=None):
        if target is not None:
            c.turn_to(target, at=t, wait=False)
        c.arm_to(1, t + 0.35, (_deg(-90), _deg(-8), 0))
        c.arm_to(1, t + 1.4, (_deg(-90), _deg(-8), 0))
        c.arm_to(1, t + 1.8, (0, 0, 0))
        return t + 1.8


class Jump(Gesture):
    description = "Jump on the spot"

    def perform(self, c, t, target=None):
        c.jump_at(t)
        c.scene.sound("thud", at=t + 0.65, volume=0.5)            # landing
        return t + 0.9


class Cheer(Gesture):
    needs = ("arms",)
    description = "Jump with both arms up"

    def perform(self, c, t, target=None):
        c.jump_at(t)
        c.arms_up_at(t + 0.3, hold_until=t + 1.0)
        c.arms_rest(t + 1.3)
        return t + 1.3


class Facepalm(Gesture):
    needs = ("arms",)
    description = "Hand to the face"

    def perform(self, c, t, target=None):
        palm = (_aim(1, 0.2, 0.15, 0.24), 0.52)         # real proportions: the hand over the brow
        c.arm_to(1, t + 0.35, (_deg(-150), _deg(30), 0), bent=palm)
        c.arm_to(1, t + 1.3, (_deg(-150), _deg(30), 0), bent=palm)
        c.nod_at(t + 0.2, 14)
        c.arm_to(1, t + 1.7, (0, 0, 0))
        return t + 1.7


class Clap(Gesture):
    needs = ("arms",)
    description = "Clap hands"
    symmetric = True          # the hands have to meet

    def perform(self, c, t, target=None):
        for i in range(4):
            tc = t + 0.25 + i * 0.25
            for s in (1, -1):
                c.arm_to(s, tc, (_deg(-70), _deg(28 * s), 0), bent=(_aim(s, 0.1, 0.35, -0.2), 0.75))
                c.arm_to(s, tc + 0.12, (_deg(-70), _deg(10 * s), 0), bent=(_aim(s, 0.22, 0.32, -0.2), 0.78))
            c.scene.sound("clap", at=tc + 0.12, volume=0.7)
        c.arms_rest(t + 1.5)
        return t + 1.5


class Think(Gesture):
    needs = ("arms",)
    description = "Hand on chin, thinking"

    def perform(self, c, t, target=None):
        chin = (_aim(1, 0.16, 0.12, 0.05), 0.42)        # real proportions: the hand under the chin
        c.arm_to(1, t + 0.4, (_deg(-125), _deg(28), 0), bent=chin)
        c.arm_to(1, t + 1.8, (_deg(-125), _deg(28), 0), bent=chin)
        c.tilt_head_at(t + 0.2, 12)
        c.arm_to(1, t + 2.2, (0, 0, 0))
        return t + 2.2


class Bow(Gesture):
    description = "Bow from the waist"

    def perform(self, c, t, target=None):
        hold(c.body, "rotation_euler", t)
        key(c.body, "rotation_euler", t + 0.4, (_deg(-35), 0, 0))
        key(c.body, "rotation_euler", t + 0.9, (_deg(-35), 0, 0))
        key(c.body, "rotation_euler", t + 1.3, (0, 0, 0))
        return t + 1.3


class Stomp(Gesture):
    needs = ("swing_legs",)
    description = "Stomp in a temper"

    def perform(self, c, t, target=None):
        for i, s in enumerate((1, -1, 1)):
            tl = t + i * 0.3
            hold(c.legs[s], "rotation_euler", tl)
            key(c.legs[s], "rotation_euler", tl + 0.12, (_deg(-30), 0, 0))
            key(c.legs[s], "rotation_euler", tl + 0.24, (0, 0, 0), "ease_in")
            c.scene.sound("thud", at=tl + 0.24, volume=0.6)
        for sd in (1, -1):
            c.arm_to(sd, t + 0.2, (0, _deg(-25 * sd), 0))
        c.arms_rest(t + 1.0)
        return t + 1.0


def _aim(side, inward, forward, up):
    """An arm rotation that points the arm (hanging straight down at rest) towards a direction in
    the body's own axes: inward across the chest, forward, up."""
    from mathutils import Vector
    d = Vector((-side * inward, -forward, up)).normalized()
    return tuple(Vector((0, 0, -1)).rotation_difference(d).to_euler("XYZ"))


# ---------------------------------------------------------------------- for any body
class Roar(Gesture):
    description = "Head up, mouth wide open"

    def perform(self, c, t, target=None):
        hold(c.neck, "rotation_euler", t)
        cur = value_at(c.neck, "rotation_euler", t)
        key(c.neck, "rotation_euler", t + 0.3, (cur[0] - _deg(25), cur[1], cur[2]))
        hold(c.mouth, "scale", t)
        key(c.mouth, "scale", t + 0.3, (1.3, 1, 4.0))
        key(c.mouth, "scale", t + 1.2, (1.3, 1, 4.0))
        key(c.mouth, "scale", t + 1.5, (1, 1, 1))
        key(c.neck, "rotation_euler", t + 1.5, tuple(cur))
        c.hop_at(t, 0.03, 0.3, 1.4)
        return t + 1.5


class Sniff(Gesture):
    description = "Head down, sniffing"

    def perform(self, c, t, target=None):
        hold(c.neck, "rotation_euler", t)
        cur = value_at(c.neck, "rotation_euler", t)
        for i in range(4):
            key(c.neck, "rotation_euler", t + 0.25 + i * 0.18, (cur[0] + _deg(30 + (6 if i % 2 else 0)), cur[1], cur[2]))
        key(c.neck, "rotation_euler", t + 1.2, tuple(cur))
        return t + 1.2


class Spin(Gesture):
    description = "Spin round once"

    def perform(self, c, t, target=None):
        hold(c.root, "rotation_euler", t)
        h = value_at(c.root, "rotation_euler", t)[2]
        key(c.root, "rotation_euler", t + 0.8, (0, 0, h + 2 * math.pi), "ease_in_out")
        if hasattr(c, "plant_feet"):
            c.plant_feet(t + 0.8)
        return t + 0.8


class TailWag(Gesture):
    description = "Wag the tail"
    needs = ("tail",)

    def perform(self, c, t, target=None):
        c.wave(c.skel.tail, t, t + 1.4, period=0.3, amp_deg=30, axis="Z", phase_step=0.4)
        return t + 1.4


class Flap(Gesture):
    description = "Flap the wings"
    needs = ("wings",)

    def perform(self, c, t, target=None):
        c.flap(t, t + 1.4, beat=0.3)
        c.hop_at(t, 0.04, 0.4, 1.4)
        return t + 1.5


class RearUp(Gesture):
    description = "Rear up on the hind legs"
    needs = ("rear",)

    def perform(self, c, t, target=None):
        hold(c.body, "rotation_euler", t)
        key(c.body, "rotation_euler", t + 0.5, (_deg(28), 0, 0), "ease_out")
        key(c.body, "rotation_euler", t + 1.4, (_deg(28), 0, 0))
        key(c.body, "rotation_euler", t + 1.9, (0, 0, 0), "ease_in")
        for leg, target_ in c.feet.items():
            if leg.endswith("F"):
                hold(target_, "location", t)
                p = value_at(target_, "location", t)
                key(target_, "location", t + 0.5, (p[0], p[1], p[2] + c.leg_len * 0.7))
                key(target_, "location", t + 1.4, (p[0], p[1], p[2] + c.leg_len * 0.7))
                key(target_, "location", t + 1.9, tuple(p), "ease_in")
        return t + 1.9


class Croak(Gesture):
    description = "Puff up the throat and croak"
    needs = ("croak",)

    def perform(self, c, t, target=None):
        sac = getattr(c, "sac", None)
        if sac is None:
            return t + 0.2
        hold(sac, "scale", t)
        for i in range(3):
            key(sac, "scale", t + 0.15 + i * 0.4, (1.3, 1.3, 1.3), "ease_out")
            key(sac, "scale", t + 0.35 + i * 0.4, (0.3, 0.3, 0.3))
        c.nod_at(t + 0.1, -6)
        return t + 1.4


class Tongue(Gesture):
    description = "Flick the tongue out (and back)"
    needs = ("tongue",)
    uses_target = True

    def perform(self, c, t, target=None):
        tongue = getattr(c, "tongue", None)
        if tongue is None:
            return t + 0.2
        if target is not None:
            c.look_at(target, at=t) if hasattr(c, "look_at") else None
        hold(tongue, "scale", t)
        key(tongue, "scale", t + 0.12, (1, 1, 1), "ease_out")
        key(tongue, "scale", t + 0.35, (1, 1, 1))
        key(tongue, "scale", t + 0.5, (1, 0.01, 1))
        return t + 0.6
