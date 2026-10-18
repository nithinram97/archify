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

    def perform(self, c, t, target=None):
        for i in range(4):
            tc = t + 0.25 + i * 0.25
            for s in (1, -1):
                c.arm_to(s, tc, (_deg(-70), _deg(28 * s), 0), bent=(_aim(s, 0.1, 0.35, -0.2), 0.75))
                c.arm_to(s, tc + 0.12, (_deg(-70), _deg(10 * s), 0), bent=(_aim(s, 0.22, 0.32, -0.2), 0.78))
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
        for sd in (1, -1):
            c.arm_to(sd, t + 0.2, (0, _deg(-25 * sd), 0))
        c.arms_rest(t + 1.0)
        return t + 1.0


# ---------------------------------------------------------------------- fighting
# Fight choreography for anything with arms. Attacks step in and twist the body; the defending moves
# (block, dodge, flinch) are timed to the blow: start one together with an attack (with_previous)
# and it reacts as the blow lands. People and animals with their own animation of a move play it.
IMPACT = 0.38          # seconds from the start of an attack to the blow landing


def _aim(side, inward, forward, up):
    """An arm rotation that points the arm (hanging straight down at rest) towards a direction in
    the body's own axes: inward across the chest, forward, up."""
    from mathutils import Vector
    d = Vector((-side * inward, -forward, up)).normalized()
    return tuple(Vector((0, 0, -1)).rotation_difference(d).to_euler("XYZ"))


def _guard(c, t, ease="smooth"):
    """Fists up in front of the chin, elbows down."""
    for s in (1, -1):
        c.arm_to(s, t, (_deg(-60), _deg(15 * s), 0), ease, bent=(_aim(s, 0.35, 0.8, 0.45), 0.52))
    c.fist(t)


def _rest(c, t):
    """Arms down and the hands open again."""
    c.arms_rest(t)
    c.fist(t, 0)


def _step(c, t0, t1, t2, metres):
    """Step forward (or back, negative) along the facing by t1, and stay there until t2 (None: stay)."""
    hold(c.root, "location", t0)
    p, f = c.position(t0), c.forward(t0)
    z = value_at(c.root, "location", t0)[2]
    key(c.root, "location", t1, (p.x + f.x * metres, p.y + f.y * metres, z))
    if t2 is not None:
        key(c.root, "location", t2, (p.x, p.y, z))


def _closing(c, t, target, side, least):
    """How far to step in so a punch from this side lands on the target's face (at least `least`)."""
    if target is None:
        return least
    from . import handling
    q, p = c._point(target, t), c.position(t)
    gap = math.hypot(q.x - p.x, q.y - p.y)
    return min(max(least, gap - handling.arm_rest(c)[side][1] - 0.05 * c.H), 0.45 * c.H)


def _twist(c, t, deg, lean=0.0):
    """Turn the upper body (degrees, + to its left) and lean it (+ forward, - back)."""
    key(c.body, "rotation_euler", t, (_deg(lean), 0, _deg(deg)))


def _own_clip(c, name, t):
    """Play the actor's own animation of a move, if it has one; the end time, or None."""
    if name in getattr(c, "clip_names", {}):
        return c.play(name, t)
    return None


class Punch(Gesture):
    """A right cross: guard, a little wind-up, the punch thrown at face height with the body behind it."""
    needs = ("arms",)
    description = "Punch (a right cross); start a block, dodge or flinch with it for the other fighter"
    uses_target = True
    side = -1
    step = 0.18

    def perform(self, c, t, target=None):
        end = _own_clip(c, "punch", t)
        if end is not None:
            return end
        if not c.arms:
            raise ValueError(f"{c.name} has no arms to punch with")
        if target is not None:
            c.turn_to(target, at=t, wait=False)
        s, i = self.side, IMPACT
        hold(c.body, "rotation_euler", t)
        _guard(c, t + 0.12)
        _twist(c, t + 0.22, 12 * s, -4)                         # wind up: the shoulder goes back
        strike = (_aim(s, 0.3, 1.0, 0.3), 1.0)                 # straight out at the face
        c.arm_to(s, t + i, (_deg(-90), 0, 0), "ease_in", bent=strike)
        _twist(c, t + i, -18 * s, 8)                            # the body turns into the punch
        _step(c, t, t + i, t + i + 0.7, _closing(c, t, target, s, self.step))   # in, and back out
        c.arm_to(s, t + i + 0.12, (_deg(-90), 0, 0), bent=strike)
        _guard(c, t + i + 0.4)
        _twist(c, t + i + 0.4, 0)
        _rest(c, t + i + 0.9)
        return t + i + 0.9


class Jab(Punch):
    """A quick left jab."""
    description = "A quick left jab"
    side = 1
    step = 0.1


class Kick(Gesture):
    """A front kick: lean back, the right leg snaps up, back down into a stance."""
    needs = ("swing_legs",)
    description = "Kick (a front kick)"
    uses_target = True

    def perform(self, c, t, target=None):
        end = _own_clip(c, "kick", t)
        if end is not None:
            return end
        if not getattr(c, "legs", None):
            raise ValueError(f"{c.name} has no legs to kick with")
        if target is not None:
            c.turn_to(target, at=t, wait=False)
        leg = c.legs[-1]
        hold(leg, "rotation_euler", t)
        hold(c.body, "rotation_euler", t)
        if c.arms:
            _guard(c, t + 0.12)
        if target is not None:                                          # close in so the foot lands
            q, p = c._point(target, t), c.position(t)
            gap = math.hypot(q.x - p.x, q.y - p.y)
            _step(c, t, t + IMPACT, t + IMPACT + 0.6, min(max(0.0, gap - 0.55 * c.H), 0.4 * c.H))
        key(leg, "rotation_euler", t + 0.18, (_deg(-35), 0, 0))           # the knee comes up
        c._reach(("leg", -1), t + 0.18, 0.75)
        key(leg, "rotation_euler", t + IMPACT, (_deg(-80), 0, 0), "ease_out")   # and the foot snaps out
        c._reach(("leg", -1), t + IMPACT, 1.0, "ease_out")
        _twist(c, t + IMPACT, 0, -12)                                       # leaning back
        key(leg, "rotation_euler", t + IMPACT + 0.25, (_deg(-30), 0, 0))
        c._reach(("leg", -1), t + IMPACT + 0.25, 0.8)
        key(leg, "rotation_euler", t + IMPACT + 0.5, (0, 0, 0))
        c._reach(("leg", -1), t + IMPACT + 0.5, 1.0)
        _twist(c, t + IMPACT + 0.5, 0)
        if c.arms:
            _rest(c, t + IMPACT + 0.9)
        return t + IMPACT + 0.9


class Block(Gesture):
    """Forearms up in front of the face, taking the blow, a half step back."""
    needs = ("arms",)
    description = "Block a blow (start it together with the punch)"

    def perform(self, c, t, target=None):
        hold(c.body, "rotation_euler", t)
        cover = {s: (_aim(s, 0.3, 0.6, 0.75), 0.5) for s in (1, -1)}   # forearms up in front of the face
        for s in (1, -1):
            c.arm_to(s, t + IMPACT - 0.12, (_deg(-120), _deg(20 * s), 0), "ease_out", bent=cover[s])
        c.fist(t + IMPACT - 0.12)
        _twist(c, t + IMPACT + 0.05, 0, -8)                      # the blow pushes them back a little
        _step(c, t + IMPACT, t + IMPACT + 0.15, None, -0.08)
        for s in (1, -1):
            c.arm_to(s, t + IMPACT + 0.45, (_deg(-120), _deg(20 * s), 0), bent=cover[s])
        _twist(c, t + IMPACT + 0.45, 0)
        _rest(c, t + IMPACT + 0.85)
        return t + IMPACT + 0.85


class Dodge(Gesture):
    """Duck and slip to the side as the blow comes."""
    description = "Dodge a blow (start it together with the punch or kick)"

    def perform(self, c, t, target=None):
        hold(c.body, "rotation_euler", t)
        hold(c.hips, "location", t + IMPACT - 0.22)
        if c.arms:
            _guard(c, t + IMPACT - 0.15)
        key(c.body, "rotation_euler", t + IMPACT, (_deg(14), _deg(-24), 0), "ease_out")   # duck and slip
        z = c.hip_z
        key(c.hips, "location", t + IMPACT, (0, 0, z - 0.06 * c.H), "ease_out")
        key(c.body, "rotation_euler", t + IMPACT + 0.4, (0, 0, 0))
        key(c.hips, "location", t + IMPACT + 0.4, (0, 0, z))
        if c.arms:
            _rest(c, t + IMPACT + 0.8)
        return t + IMPACT + 0.8


class Flinch(Gesture):
    """Hit: the head snaps back, the body reels and staggers back a step."""
    description = "Take a hit (start it together with the punch or kick)"

    def perform(self, c, t, target=None):
        end = _own_clip(c, "flinch", t + IMPACT - 0.1)
        if end is not None:
            return end
        hit = t + IMPACT
        hold(c.body, "rotation_euler", hit - 0.02)
        hold(c.neck, "rotation_euler", hit - 0.02)
        cur = value_at(c.neck, "rotation_euler", hit)
        key(c.neck, "rotation_euler", hit + 0.08, (cur[0] - _deg(22), cur[1] + _deg(10), cur[2]), "ease_out")
        key(c.body, "rotation_euler", hit + 0.12, (_deg(-16), _deg(8), _deg(10)), "ease_out")   # thrown back
        _step(c, hit, hit + 0.3, None, -0.25)
        if c.arms:
            for s in (1, -1):
                c.arm_to(s, hit + 0.15, (_deg(-30), _deg(-40 * s), 0), "ease_out", bent=(_aim(s, -0.6, 0.4, -0.5), 0.85))
            c.fist(hit + 0.15, 0, sides=(s,))
        key(c.neck, "rotation_euler", hit + 0.7, tuple(cur))
        key(c.body, "rotation_euler", hit + 0.7, (0, 0, 0))
        if c.arms:
            c.arms_rest(hit + 0.9)
        return hit + 0.9


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
