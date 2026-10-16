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

    @classmethod
    def describe_extra(cls):
        return {"uses_target": cls.uses_target}

    def perform(self, c, t, target=None):
        """Animate character `c` from time `t`; return the end time."""
        raise NotImplementedError


class Wave(Gesture):
    description = "Wave hello or goodbye"

    def perform(self, c, t, target=None):
        up = _deg(-150)
        c.arm_to(1, t + 0.3, (0, up, 0))
        for i in range(4):
            c.arm_to(1, t + 0.45 + i * 0.22, (0, up + _deg(22 if i % 2 else -22), 0))
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
    description = "Shrug: who knows?"

    def perform(self, c, t, target=None):
        for s in (1, -1):
            c.arm_to(s, t + 0.25, (_deg(-35), _deg(-55 * s), 0))
            c.arm_to(s, t + 0.9, (_deg(-35), _deg(-55 * s), 0))
        c.tilt_head_at(t, 12)
        c.hop_at(t, 0.02, 0.3, 0.9)
        c.arms_rest(t + 1.2)
        return t + 1.2


class Point(Gesture):
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
        return t + 0.9


class Cheer(Gesture):
    description = "Jump with both arms up"

    def perform(self, c, t, target=None):
        c.jump_at(t)
        c.arms_up_at(t + 0.3, hold_until=t + 1.0)
        c.arms_rest(t + 1.3)
        return t + 1.3


class Facepalm(Gesture):
    description = "Hand to the face"

    def perform(self, c, t, target=None):
        c.arm_to(1, t + 0.35, (_deg(-150), _deg(30), 0))
        c.arm_to(1, t + 1.3, (_deg(-150), _deg(30), 0))
        c.nod_at(t + 0.2, 14)
        c.arm_to(1, t + 1.7, (0, 0, 0))
        return t + 1.7


class Clap(Gesture):
    description = "Clap hands"

    def perform(self, c, t, target=None):
        for i in range(4):
            tc = t + 0.25 + i * 0.25
            for s in (1, -1):
                c.arm_to(s, tc, (_deg(-70), _deg(28 * s), 0))
                c.arm_to(s, tc + 0.12, (_deg(-70), _deg(10 * s), 0))
        c.arms_rest(t + 1.5)
        return t + 1.5


class Think(Gesture):
    description = "Hand on chin, thinking"

    def perform(self, c, t, target=None):
        c.arm_to(1, t + 0.4, (_deg(-125), _deg(28), 0))
        c.arm_to(1, t + 1.8, (_deg(-125), _deg(28), 0))
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
    description = "Stomp in a temper"

    def perform(self, c, t, target=None):
        for i, s in enumerate((1, -1, 1)):
            tl = t + i * 0.3
            hold(c.legs[s], "rotation_euler", tl)
            key(c.legs[s], "rotation_euler", tl + 0.12, (_deg(-30), 0, 0))
            key(c.legs[s], "rotation_euler", tl + 0.24, (0, 0, 0), "ease_in")
        for sd in (1, -1):
            c.arm_to(sd, t + 0.2, (0, _deg(-25 * sd), 0))
        c.arms_rest(t + 1.0)
        return t + 1.0
