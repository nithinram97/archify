"""Fighting: strikes, reactions, falls and the choreography that puts them together.

Moves are gestures, in two families:

* a `Strike` (jab, punch, hook, uppercut, kick, spin_kick, flying_kick, sweep) lands its blow
  `impact` seconds after it starts, with a `power` from a tap (0) to a blow that sends someone
  flying (1);
* a `Reaction` (block, dodge, flinch, knocked_down) meets a blow `impact` seconds after it starts.

Start a reaction together with a strike (`with_previous = true`) and they meet. Strikes step in until
they land on their target, faces flash with effort and pain, blows sound where they land and shake the
camera. `knocked_down` throws a body through the air on a ballistic arc, lands it on its back, slides
it and (after a while) gets it up again.

The choreography (`surround`, `brawl`, `burst`) is how fight scenes are staged: attackers circle in
their stances and come in one or two at a time; the hero answers each attack with a block or a dodge
and a counter, and whoever is beaten is thrown away and gets up to come again. See `brawl`.
"""
import math
import random

from mathutils import Vector

from . import _compat
from .gestures import Gesture, _aim
from .keys import hold, key, value_at

IMPACT = 0.38          # seconds from the start of a move to the blow landing (unless the move says otherwise)
WAIT_FOR_UP = 1.2      # the most a brawl waits, after the hero's last move, for the last of them to get up
GET_UP_SPEED = 1.25    # captured get-ups are people getting up; fighters scramble up


def _deg(d):
    return math.radians(d)


def heading_to(dx, dy):
    return math.atan2(dx, -dy)


# ---------------------------------------------------------------------- shared pieces of moves
def guard(c, t, ease="smooth"):
    """Fists up in front of the chin, elbows down."""
    for s in (1, -1):
        c.arm_to(s, t, (_deg(-60), _deg(15 * s), 0), ease, bent=(_aim(s, 0.35, 0.8, 0.45), 0.52))
    c.fist(t)


def rest(c, t):
    """Arms down and the hands open again."""
    c.arms_rest(t)
    c.fist(t, 0)


def step(c, t0, t1, t2, metres, direction=None):
    """Step `metres` along the facing (or a direction) by t1, and back by t2 (None: stay)."""
    hold(c.root, "location", t0)
    p = c.position(t0)
    f = direction if direction is not None else c.forward(t0)
    z = value_at(c.root, "location", t0)[2]
    key(c.root, "location", t1, (p.x + f.x * metres, p.y + f.y * metres, z))
    if t2 is not None:
        key(c.root, "location", t2, (p.x, p.y, z))


def twist(c, t, deg, lean=0.0, ease="smooth"):
    """Turn the upper body (degrees, + to its left) and lean it (+ forward, - back)."""
    key(c.body, "rotation_euler", t, (_deg(lean), 0, _deg(deg)), ease)


def own_clip(c, name, t):
    """Play the actor's own animation of a move, if it has one; the end time, or None."""
    if name in getattr(c, "clip_names", {}):
        return c.play(name, t)
    return None


def gap_to(c, target, t):
    q, p = c._point(target, t), c.position(t)
    return math.hypot(q.x - p.x, q.y - p.y)


def face_now(c, t, target, turn=0.25):
    """Turn the whole body to face `target` by `t` (from `turn` seconds before)."""
    if target is None:
        return
    q, p = c._point(target, t), c.position(t)
    if (q.to_2d() - p).length < 1e-3:
        return
    hold(c.root, "rotation_euler", t - turn)
    h0 = value_at(c.root, "rotation_euler", t - turn)[2]
    h = heading_to(q.x - p.x, q.y - p.y)
    h = h0 + (h - h0 + math.pi) % (2 * math.pi) - math.pi          # the short way round
    key(c.root, "rotation_euler", t, (0, 0, h))


def captured(c, move, hit, lead, target=None, side=None, reach=None):
    """Play a captured `move` (see fightmoves.py) on `c` so its blow lands at `hit`, facing `target` and
    stepping in to be `reach` metres from them at the blow. The end time, or None if there's none to play."""
    if not hasattr(c, "perform_clip"):
        return None
    from . import fightmoves
    got = fightmoves.pick(move, random.Random(f"{c.key}/{move}/{round(hit, 2)}"), side)
    if got is None:
        return None
    m, mirror = got
    t0 = hit - lead
    face_now(c, t0, target)
    drift = None
    if target is not None and reach is not None:
        p = c.position(t0)
        d = c._point(target, hit).to_2d() - p
        if d.length > 1e-3:
            drift = d.normalized() * max(-0.3, min(0.9, d.length - reach))
    return fightmoves.play(c, m, hit, mirror, drift, lead)


def shake(c, t, strength):
    """The camera feels a blow."""
    cut = getattr(c.scene, "cut", None)
    if cut is not None and hasattr(cut, "impact"):
        cut.impact(t, strength)


# ---------------------------------------------------------------------- strikes
class Strike(Gesture):
    """A blow. `perform` plays an actor's own clip of the move if it has one; otherwise it turns to
    the target and calls `strike`, which keys the move with its blow landing at `t + impact`."""
    abstract = True
    keeps_time = True
    uses_target = True
    impact = IMPACT
    power = 0.5           # 0 a tap ... 1 sends them flying (the choreographer reads it)
    clip = None           # an actor's own animation to play instead (default: the move's name)
    face = "fierce"

    def perform(self, c, t, target=None):
        end = own_clip(c, self.clip or self.name, t)
        if end is not None:
            return end
        hit = t + self.impact
        end = captured(c, self.name, hit, self.impact, target, getattr(self, "side", None), self.reach_at)
        if end is None:                                   # no captured move for this body: dreamreel's own
            if target is not None:
                c.turn_to(target, at=t, wait=False)
            hold(c.body, "rotation_euler", t)
            end = self.strike(c, t, target, hit)
        else:
            c.scene.sound("whoosh" if self.power > 0.4 else "swish", at=hit - 0.12, volume=0.45)
            c.fist(t + 0.1)                           # the capture has no fingers: dreamreel closes the hands
            c.fist(end - 0.2, 0)
        c.flash(self.face, hit - 0.2, hold=0.45)
        return end

    reach_at = 0.75       # how far from the target to be when the blow lands (metres)

    def strike(self, c, t, target, hit):
        raise NotImplementedError


class ArmStrike(Strike):
    """A punch: guard, a wind-up, the fist driven along `aim` (inward, forward, up in the body's axes)
    with the body turning into it, a step in if the target is out of reach, and back to guard."""
    abstract = True
    needs = ("arms",)
    side = -1             # 1 the left hand, -1 the right
    step = 0.18
    aim = (0.3, 1.0, 0.3)
    wind = (12, -4)       # the wind-up: body turn (degrees, away from the blow) and lean
    drive = (-18, 8)      # the body turning into the blow, and leaning in
    dip = 0.0             # crouch before (an uppercut comes up from the legs)
    sound = "whoosh"

    def strike(self, c, t, target, hit):
        s = self.side
        guard(c, t + 0.12)
        twist(c, t + 0.22, self.wind[0] * s, self.wind[1])
        if self.dip:
            hold(c.hips, "location", t)
            key(c.hips, "location", hit - 0.12, (0, 0, c.hip_z - self.dip * c.H))
            key(c.hips, "location", hit + 0.05, (0, 0, c.hip_z + 0.3 * self.dip * c.H), "ease_out")
            key(c.hips, "location", hit + 0.45, (0, 0, c.hip_z))
        blow = (_aim(s, *self.aim), 1.0)
        c.arm_to(s, hit, (_deg(-90), 0, 0), "ease_in", bent=blow)
        c.scene.sound(self.sound, at=hit - 0.12, volume=0.45)
        twist(c, hit, self.drive[0] * s, self.drive[1])
        step(c, t, hit, hit + 0.7, self.reach(c, t, target))          # in, and back out
        c.arm_to(s, hit + 0.12, (_deg(-90), 0, 0), bent=blow)
        guard(c, hit + 0.4)
        twist(c, hit + 0.4, 0)
        rest(c, hit + 0.9)
        return hit + 0.9

    def reach(self, c, t, target):
        """How far to step in so the fist lands on the target's face (at least `step`)."""
        if target is None:
            return self.step
        from . import handling
        return min(max(self.step, gap_to(c, target, t) - handling.arm_rest(c)[self.side][1] - 0.05 * c.H),
                   0.45 * c.H)


class Punch(ArmStrike):
    """A right cross: guard, a little wind-up, the punch thrown at face height with the body behind it."""
    description = "Punch (a right cross); start a block, dodge or flinch with it for the other fighter"
    power = 0.6


class Jab(Punch):
    """A quick left jab."""
    description = "A quick left jab"
    side = 1
    step = 0.1
    power = 0.3
    sound = "swish"


class Hook(ArmStrike):
    """A hook: the right fist swings round from the side into the jaw."""
    description = "A hook to the jaw"
    aim = (0.95, 0.55, 0.35)
    wind = (28, -2)
    drive = (-38, 6)
    power = 0.7


class Uppercut(ArmStrike):
    """An uppercut: drop low, then drive the fist up under the chin with the legs."""
    description = "An uppercut: from a crouch, up under the chin (it lifts them off their feet)"
    aim = (0.25, 0.6, 1.0)
    wind = (10, 12)
    drive = (-14, -10)
    dip = 0.07
    power = 0.9


class LegStrike(Strike):
    """A kick: the knee comes up (`chamber`), the leg snaps out to `extend` degrees as the blow lands,
    the body leans back to balance, and the leg comes back down."""
    abstract = True
    needs = ("swing_legs",)
    side = -1
    chamber = -35
    extend = -80
    lean = -12
    closes = 0.55         # steps in until the target is this many heights away

    def strike(self, c, t, target, hit):
        if not getattr(c, "legs", None):
            raise ValueError(f"{c.name} has no legs to kick with")
        leg = c.legs[self.side]
        hold(leg, "rotation_euler", t)
        if c.arms:
            guard(c, t + 0.12)
        if target is not None:
            step(c, t, hit, hit + 0.6, min(max(0.0, gap_to(c, target, t) - self.closes * c.H), 0.4 * c.H))
        self.kick(c, leg, t, hit)
        if c.arms:
            rest(c, hit + 0.9)
        return hit + 0.9

    def kick(self, c, leg, t, hit):
        key(leg, "rotation_euler", t + 0.18, (_deg(self.chamber), 0, 0))           # the knee comes up
        c._reach(("leg", self.side), t + 0.18, 0.75)
        key(leg, "rotation_euler", hit, (_deg(self.extend), 0, 0), "ease_out")     # and the foot snaps out
        c.scene.sound("whoosh", at=hit - 0.15, volume=0.5)
        c._reach(("leg", self.side), hit, 1.0, "ease_out")
        twist(c, hit, 0, self.lean)
        key(leg, "rotation_euler", hit + 0.25, (_deg(self.chamber + 5), 0, 0))
        c._reach(("leg", self.side), hit + 0.25, 0.8)
        key(leg, "rotation_euler", hit + 0.5, (0, 0, 0))
        c._reach(("leg", self.side), hit + 0.5, 1.0)
        twist(c, hit + 0.5, 0)


class Kick(LegStrike):
    """A front kick: lean back, the right leg snaps up, back down into a stance."""
    reach_at = 1.0
    description = "Kick (a front kick)"
    power = 0.7


class SpinKick(LegStrike):
    """A spinning roundhouse: a full turn on the standing foot, the leg swinging out flat into the target."""
    reach_at = 1.0
    description = "A spinning kick: a full turn, the leg swinging round at head height"
    impact = 0.55
    power = 0.95
    closes = 0.6

    def kick(self, c, leg, t, hit):
        h = value_at(c.root, "rotation_euler", t)[2]
        hold(c.root, "rotation_euler", t)
        key(c.root, "rotation_euler", hit, (0, 0, h + 2 * math.pi), "ease_in")      # round we go
        key(c.root, "rotation_euler", hit + 0.01, (0, 0, h))                          # (the same facing)
        key(leg, "rotation_euler", t + 0.2, (_deg(-50), _deg(20 * self.side), 0))
        key(leg, "rotation_euler", hit, (_deg(-20), _deg(105 * self.side), 0), "ease_out")  # out at head height
        c._reach(("leg", self.side), hit, 1.0, "ease_out")
        key(c.body, "rotation_euler", hit, (_deg(-4), _deg(-35 * self.side), 0))     # leaning away
        c.scene.sound("whoosh", at=hit - 0.2, volume=0.6)
        key(leg, "rotation_euler", hit + 0.3, (_deg(-30), _deg(20 * self.side), 0))
        key(leg, "rotation_euler", hit + 0.55, (0, 0, 0))
        key(c.body, "rotation_euler", hit + 0.55, (0, 0, 0))


class FlyingKick(LegStrike):
    """A flying kick: a run-up step, a leap, the leg straight out in the air, and the landing."""
    reach_at = 1.0
    description = "A flying kick: a leap at them, foot first"
    impact = 0.6
    power = 1.0
    closes = 0.5

    def strike(self, c, t, target, hit):
        leg = c.legs[self.side]
        hold(leg, "rotation_euler", t)
        if c.arms:
            guard(c, t + 0.1)
        dist = min(max(0.4, gap_to(c, target, t) - self.closes * c.H), 2.0) if target is not None else 1.0
        f, p = c.forward(t), c.position(t)
        z0 = value_at(c.root, "location", t)[2]
        hold(c.root, "location", t)
        crouch, peak = 0.15, 0.35 * c.H
        hold(c.hips, "location", t)
        key(c.hips, "location", t + crouch, (0, 0, c.hip_z - 0.06 * c.H))                 # gather
        for k in range(1, 7):                                                                  # the leap
            u = k / 6
            tt = t + crouch + (hit + 0.15 - t - crouch) * u
            key(c.root, "location", tt, (p.x + f.x * dist * u, p.y + f.y * dist * u, z0 + 4 * peak * u * (1 - u)),
                "linear")
        key(c.hips, "location", t + crouch + 0.1, (0, 0, c.hip_z))
        key(leg, "rotation_euler", t + crouch + 0.08, (_deg(-60), 0, 0))
        c._reach(("leg", self.side), t + crouch + 0.08, 0.6)
        key(c.legs[-self.side], "rotation_euler", hit, (_deg(-50), 0, 0))                   # the other leg tucked
        c._reach(("leg", -self.side), hit, 0.55)
        key(leg, "rotation_euler", hit, (_deg(-85), 0, 0), "ease_out")
        c._reach(("leg", self.side), hit, 1.0, "ease_out")
        twist(c, hit, 0, -18)
        c.scene.sound("whoosh", at=hit - 0.2, volume=0.6)
        land = hit + 0.15
        for s in (1, -1):
            key(c.legs[s], "rotation_euler", land + 0.05, (_deg(-20), 0, 0))
            c._reach(("leg", s), land + 0.05, 0.8)
            key(c.legs[s], "rotation_euler", land + 0.4, (0, 0, 0))
            c._reach(("leg", s), land + 0.4, 1.0)
        key(c.hips, "location", land + 0.08, (0, 0, c.hip_z - 0.07 * c.H))              # absorbing the landing
        key(c.hips, "location", land + 0.4, (0, 0, c.hip_z))
        c.scene.sound("thud", at=land, volume=0.35)
        twist(c, land + 0.3, 0)
        if c.arms:
            rest(c, land + 0.8)
        return land + 0.8


class Sweep(LegStrike):
    """A leg sweep: drop low and swing the leg round at the ankles."""
    reach_at = 1.0
    description = "A leg sweep: low, at their ankles (they fall)"
    impact = 0.45
    power = 0.8
    closes = 0.5

    def kick(self, c, leg, t, hit):
        hold(c.hips, "location", t)
        key(c.hips, "location", t + 0.25, (0, 0, c.hip_z - 0.3 * c.H))                     # down low
        key(c.body, "rotation_euler", t + 0.25, (_deg(25), 0, 0))
        key(leg, "rotation_euler", t + 0.25, (_deg(-60), _deg(-30 * self.side), 0))
        key(leg, "rotation_euler", hit, (_deg(-75), _deg(60 * self.side), 0), "ease_out")
        c._reach(("leg", -self.side), t + 0.25, 0.55)
        c.scene.sound("swish", at=hit - 0.1, volume=0.5)
        key(leg, "rotation_euler", hit + 0.4, (0, 0, 0))
        key(c.hips, "location", hit + 0.5, (0, 0, c.hip_z))
        key(c.body, "rotation_euler", hit + 0.5, (0, 0, 0))
        c._reach(("leg", -self.side), hit + 0.5, 1.0)


# ---------------------------------------------------------------------- reactions
class Reaction(Gesture):
    """Meeting a blow: `react` keys the response from `hit` (`impact` after the start). The target, if
    given, is who threw it."""
    abstract = True
    keeps_time = True
    impact = IMPACT

    capture = None        # the captured move to play instead (fightmoves.py), for bodies with a skeleton

    def perform(self, c, t, target=None):
        hit = self.meets(c, t, target)
        if self.capture:
            end = captured(c, self.capture, hit, max(0.2, hit - t), target)
            if end is not None:
                self.after(c, hit, target)
                return end
        return self.react(c, hit, target)

    def after(self, c, hit, attacker):
        """What goes with a captured reaction (a sound, the camera's jolt)."""

    def meets(self, c, t, attacker):
        """When the blow lands: the attacker's strike that started at `t` (when started together with it),
        else `impact` after the start."""
        who = c.scene.character(attacker) if attacker is not None else None
        if who is not None:
            for e in reversed(c.scene.events):
                if e["kind"] == "gesture" and e["who"] is who and abs(e["t0"] - t) < 0.05:
                    g = _gesture(e.get("gesture"))
                    if issubclass(g, Strike):
                        return t + g.impact
        return t + self.impact

    def react(self, c, hit, attacker):
        raise NotImplementedError


class Block(Reaction):
    """Forearms up in front of the face, taking the blow, a half step back."""
    needs = ("arms",)
    description = "Block a blow (start it together with the punch)"
    capture = "block"

    def after(self, c, hit, attacker):
        c.scene.sound("block", at=hit, volume=0.55)
        shake(c, hit, 0.25)
        c.flash("fierce", hit - 0.05, hold=0.3, how_much=0.7)

    def react(self, c, hit, attacker):
        hold(c.body, "rotation_euler", hit - self.impact)
        cover = {s: (_aim(s, 0.3, 0.6, 0.75), 0.5) for s in (1, -1)}   # forearms up in front of the face
        for s in (1, -1):
            c.arm_to(s, hit - 0.12, (_deg(-120), _deg(20 * s), 0), "ease_out", bent=cover[s])
        c.fist(hit - 0.12)
        twist(c, hit + 0.05, 0, -8)                                      # the blow pushes them back a little
        c.scene.sound("block", at=hit, volume=0.55)                      # the blow lands on the forearms
        shake(c, hit, 0.25)
        c.flash("fierce", hit - 0.05, hold=0.3, how_much=0.7)
        step(c, hit, hit + 0.15, None, -0.08)
        for s in (1, -1):
            c.arm_to(s, hit + 0.45, (_deg(-120), _deg(20 * s), 0), bent=cover[s])
        twist(c, hit + 0.45, 0)
        rest(c, hit + 0.85)
        return hit + 0.85


class Dodge(Reaction):
    """Duck and slip to the side as the blow comes."""
    description = "Dodge a blow (start it together with the punch or kick)"
    capture = "dodge"

    def after(self, c, hit, attacker):
        c.scene.sound("cloth", at=hit - 0.2, volume=0.35)

    def react(self, c, hit, attacker):
        hold(c.body, "rotation_euler", hit - self.impact)
        hold(c.hips, "location", hit - 0.22)
        if c.arms:
            guard(c, hit - 0.15)
        key(c.body, "rotation_euler", hit, (_deg(14), _deg(-24), 0), "ease_out")   # duck and slip
        c.scene.sound("cloth", at=hit - 0.2, volume=0.35)
        key(c.hips, "location", hit, (0, 0, c.hip_z - 0.06 * c.H), "ease_out")
        key(c.body, "rotation_euler", hit + 0.4, (0, 0, 0))
        key(c.hips, "location", hit + 0.4, (0, 0, c.hip_z))
        if c.arms:
            rest(c, hit + 0.8)
        return hit + 0.8


class Flinch(Reaction):
    """Hit: the head snaps back, the body reels and staggers back a step."""
    description = "Take a hit (start it together with the punch or kick)"

    def perform(self, c, t, target=None):
        hit = self.meets(c, t, target)
        c.scene.sound("punch_heavy", at=hit, volume=0.65)               # the blow lands (whoever threw it)
        end = own_clip(c, "flinch", hit - 0.1)
        if end is not None:
            return end
        return self.react(c, hit, target)

    def react(self, c, hit, attacker):
        hold(c.body, "rotation_euler", hit - 0.02)
        hold(c.neck, "rotation_euler", hit - 0.02)
        shake(c, hit, 0.45)
        c.flash("pain", hit, hold=0.6)
        cur = value_at(c.neck, "rotation_euler", hit)
        key(c.neck, "rotation_euler", hit + 0.08, (cur[0] - _deg(22), cur[1] + _deg(10), cur[2]), "ease_out")
        key(c.body, "rotation_euler", hit + 0.12, (_deg(-16), _deg(8), _deg(10)), "ease_out")   # thrown back
        step(c, hit, hit + 0.3, None, -0.25, direction=self.away(c, hit, attacker))
        if c.arms:
            for s in (1, -1):
                c.arm_to(s, hit + 0.15, (_deg(-30), _deg(-40 * s), 0), "ease_out", bent=(_aim(s, -0.6, 0.4, -0.5), 0.85))
            c.fist(hit + 0.15, 0)
        key(c.neck, "rotation_euler", hit + 0.7, tuple(cur))
        key(c.body, "rotation_euler", hit + 0.7, (0, 0, 0))
        if c.arms:
            c.arms_rest(hit + 0.9)
        return hit + 0.9

    @staticmethod
    def away(c, t, attacker):
        """The direction a blow drives them: straight away from whoever threw it (else backwards)."""
        if attacker is not None:
            d = c.position(t) - c._point(attacker, t).to_2d()
            if d.length > 1e-3:
                return d.normalized()
        return -c.forward(t)


class KnockedDown(Reaction):
    """Knocked off their feet: thrown back through the air, landing on their back, sliding, lying there
    a moment and getting up again."""
    description = "Knocked flying by a blow (start it with the punch or kick); gets up after a while"
    needs = ("swing_legs",)       # bodies whose feet are planted by a footstep planner stay on their feet
    distance = 1.4
    height = 0.3
    lie = 1.0

    def perform(self, c, t, target=None):
        hit = self.meets(c, t, target)
        c.scene.sound("punch_heavy", at=hit, volume=0.8)
        return self.react(c, hit, target)

    def react(self, c, hit, attacker):
        return knock_down(c, hit, attacker, self.distance, self.height, self.lie)


def knock_down(c, hit, attacker=None, distance=1.4, height=0.3, lie=1.0, get_up=True):
    """Knock `c` down at `hit`, away from `attacker`: a body with a skeleton falls as a ragdoll (real
    physics) and gets up with a captured get-up; others are thrown on a ballistic arc `distance` metres
    long and `height` high onto their backs. They lie for `lie` seconds and (with get_up) stand up again.
    Returns when they're back on their feet (or have come to rest)."""
    from . import ragdoll
    if ragdoll.can_fall(c):
        return fall_together([(c, attacker, distance, height)], hit, lie, get_up)[c]
    d = Flinch.away(c, hit, attacker)
    p = c.position(hit)
    while distance > 0.6 and not standable(c.scene, p + d * (distance + 0.3)):
        distance *= 0.8                            # not through a wall (landing short of it instead)
    h = heading_to(-d.x, -d.y)                     # facing the blow, falling on its back
    lift = 0.09 * c.H                              # lying, its back is on the ground, not its middle
    T = 0.45 + 0.12 * distance + 0.4 * height
    hold(c.root, "location", hit - 0.02)
    hold(c.root, "rotation_euler", hit - 0.02)
    hold(c.neck, "rotation_euler", hit - 0.02)
    shake(c, hit, 0.7)
    c.flash("pain", hit, hold=T + lie + 0.4)
    n = max(4, int(T * 12))
    for k in range(1, n + 1):
        u = k / n
        tilt = -90 * min(1.0, (u * 1.2) ** 1.6)
        pos = p + d * distance * u
        z = 4 * height * u * (1 - u) + lift * min(1.0, u * 1.3)
        tt = hit + T * u
        key(c.root, "location", tt, (pos.x, pos.y, z), "linear")
        key(c.root, "rotation_euler", tt, (_deg(tilt), 0, h), "linear")
    key(c.neck, "rotation_euler", hit + 0.1, (_deg(-28), 0, 0), "ease_out")      # the head snaps back
    if c.arms:
        for s in (1, -1):
            c.arm_to(s, hit + 0.15, (_deg(-150), _deg(25 * s), 0), "ease_out")  # arms flung forward
        c.fist(hit + 0.1, 0)
    if getattr(c, "legs", None):
        for s in (1, -1):
            hold(c.legs[s], "rotation_euler", hit)
            key(c.legs[s], "rotation_euler", hit + 0.3 * T, (_deg(-45 if s == 1 else -30), 0, 0))
    land = hit + T
    end = p + d * distance
    slide = end + d * min(0.6, 0.25 * distance)
    key(c.root, "location", land + 0.1, (end.x + d.x * 0.08, end.y + d.y * 0.08, lift + 0.05))   # a bounce
    key(c.root, "location", land + 0.45, (slide.x, slide.y, lift), "ease_out")                  # a slide
    key(c.root, "rotation_euler", land + 0.45, (_deg(-90), 0, h))
    key(c.neck, "rotation_euler", land + 0.2, (_deg(10), 0, 0))
    c.scene.sound("thud", at=land, volume=0.8)
    shake(c, land, 0.35)
    if c.arms:
        for s in (1, -1):
            c.arm_to(s, land + 0.15, (_deg(-20), _deg(-70 * s), 0))            # sprawled
    if getattr(c, "legs", None):
        for s in (1, -1):
            key(c.legs[s], "rotation_euler", land + 0.15, (_deg(-8 * s), 0, 0))
    down = land + 0.45 + lie
    c._down = (hit, down)
    if not get_up:
        return land + 0.45
    return get_up_from_floor(c, down)


def _push(c, attacker, t, distance, height):
    """The velocity a blow gives a body: away from the attacker, and up, enough to carry it `distance`."""
    d = Flinch.away(c, t, attacker)
    speed = 0.8 + 1.0 * distance                     # a hard punch: 2-3 m/s; the burst: 3-4
    return Vector((d.x * speed, d.y * speed, 0.6 + 2.0 * height))


def fall_together(falls, hit, lie=1.0, get_up=True):
    """Ragdoll falls for several bodies knocked down at once ([(character, attacker, distance, height)]),
    simulated together so they hit each other; each gets up with a captured get-up. {character: end}."""
    from . import fightmoves, ragdoll
    scene = falls[0][0].scene
    chosen = {}

    def settle(c, axis, on_back, pelvis):
        got = fightmoves.pick("get_up" if on_back else "get_up_face_down", random.Random(f"{c.key}/up/{hit}"))
        if got is None and not on_back:
            got = fightmoves.pick("get_up", random.Random(f"{c.key}/up/{hit}"))
        if got is None:
            return pelvis, math.atan2(axis.x, -axis.y)
        m, _ = got
        cl = fightmoves.clip(m["trial"])
        first = cl.at(m["start"])
        clip_axis = (first["chest"] - first["hips"]).to_2d()
        hs0 = cl.heading(first)
        # turn the get-up so it starts lying the way the body came to rest
        H0 = math.atan2(axis.y, axis.x) - math.atan2(clip_axis.y, clip_axis.x) + hs0
        chosen[c] = m
        return pelvis, H0
    for c, attacker, distance, height in falls:
        shake(c, hit, 0.7)
        c.flash("pain", hit, hold=1.5 + lie)
    res = ragdoll.knock_down(scene, [(c, _push(c, a, hit, d, h)) for c, a, d, h in falls], hit, settle=settle)
    out = {}
    for c, info in res.items():
        rest = info["rest"]
        c.scene.sound("thud", at=min(rest, hit + 0.6), volume=0.8)
        c._down = (hit, rest + lie)
        if not get_up or c not in chosen:
            out[c] = rest
            scene._end(c, rest, False)
            continue
        m = chosen[c]
        out[c] = c.perform_clip(fightmoves.clip(m["trial"]), rest + lie, speed=GET_UP_SPEED, start=m["start"],
                                end=m["end"], blend=0.45)
        c.scene.sound("cloth", at=rest + lie + 0.2, volume=0.4)
        scene._end(c, out[c], False)
    return out


def get_up_from_floor(c, t, seconds=1.1):
    """Get up from lying on the back: sit up, draw the feet in, push up to standing."""
    loc = value_at(c.root, "location", t)
    h = value_at(c.root, "rotation_euler", t)[2]
    f = Vector((math.sin(h), -math.cos(h)))
    hz = c.hip_z
    feet = Vector((loc[0], loc[1]))
    hips = feet - f * hz                         # lying, the hips are a hip-height behind the feet
    hold(c.root, "location", t)
    hold(c.root, "rotation_euler", t)
    legs = getattr(c, "legs", None) or {}
    for s in legs:
        hold(legs[s], "rotation_euler", t)

    def pose(tt, tilt, leg, knees, hips_up, at_feet, ease="smooth"):
        """Root keyed so the hips sit at a point between where they lie and the feet, `hips_up` high."""
        a = _deg(tilt)
        where = hips + (feet - hips) * at_feet
        back, up = -math.sin(a) * hz, math.cos(a) * hz      # the hips seen from the root: behind it and above it
        key(c.root, "location", tt, (where.x + f.x * back, where.y + f.y * back, hips_up - up), ease)
        key(c.root, "rotation_euler", tt, (a, 0, h), ease)
        for s in legs:
            key(legs[s], "rotation_euler", tt, (_deg(leg), 0, 0), ease)
            c._reach(("leg", s), tt, knees, ease)

    pose(t + 0.35 * seconds, -35, -55, 1.0, 0.05 * c.H, 0.0)           # sit up, legs out in front
    pose(t + 0.7 * seconds, 15, -100, 0.45, 0.28 * c.H, 0.75)          # a crouch over the feet
    pose(t + seconds, 0, 0, 1.0, hz, 1.0, "ease_out")                    # and up
    if c.arms:
        for s in (1, -1):
            c.arm_to(s, t + 0.35 * seconds, (_deg(30), _deg(-20 * s), 0))   # pushing off the ground
        guard(c, t + seconds)
    c.scene.sound("cloth", at=t + 0.2, volume=0.4)
    return t + seconds


class GetUp(Gesture):
    """Get up off the floor (after being knocked down)."""
    description = "Get up off the floor"
    needs = ("swing_legs",)

    def perform(self, c, t, target=None):
        if value_at(c.root, "rotation_euler", t)[0] > _deg(-45):
            return t                                     # already up
        return get_up_from_floor(c, t)


# ---------------------------------------------------------------------- stance
def stance(c, t0, t1, bounce=0.02, lean=6, period=0.55):
    """A fighter's stance from t0 to t1: guard up, knees soft, bouncing on the balls of the feet (captured
    boxers' footwork for bodies with a skeleton)."""
    if hasattr(c, "perform_clip") and t1 - t0 > 0.8:
        from . import fightmoves
        rng = random.Random(f"{c.key}/stance/{round(t0, 2)}")
        t, done = t0, False
        while t < t1 - 0.4:
            got = fightmoves.pick("stance", rng)
            if got is None:
                break
            m, _ = got
            seg = min(m["end"] - m["start"], t1 - t)
            fightmoves.play(c, dict(m, end=m["start"] + seg, at=m["start"]), t, in_place=True)
            t += seg
            done = True
        if done:
            c.fist(t0 + 0.2)
        if done:
            return t1
    if c.arms:
        guard(c, t0 + 0.2)
    hold(c.hips, "location", t0)
    hold(c.body, "rotation_euler", t0)
    key(c.body, "rotation_euler", t0 + 0.3, (_deg(lean), 0, 0))
    low = c.hip_z - 0.035 * c.H
    k, tt = 0, t0 + 0.3
    while tt < t1 - 0.05:
        key(c.hips, "location", tt, (0, 0, low - (bounce * c.H if k % 2 else 0)))
        k += 1
        tt += period / 2
    key(c.hips, "location", t1, (0, 0, c.hip_z))          # ready to move again
    key(c.body, "rotation_euler", t1, (0, 0, 0))
    return t1


class Stance(Gesture):
    """Take a fighting stance and bounce in it for two seconds."""
    description = "A fighting stance: guard up, bouncing on the toes (2 s)"

    def perform(self, c, t, target=None):
        if target is not None:
            c.turn_to(target, at=t, wait=False)
        return stance(c, t, t + 2.0)


# ---------------------------------------------------------------------- choreography
# How fight scenes are staged (the stunt-team way): attackers keep their distance in a ring, in their
# stances, and come in one or two at a time, so every blow can be seen and answered. Each exchange is
# action and reaction: an attack, a block or a dodge, a counter that lands, a fighter thrown out of the
# fight who gets up and comes back. The camera cuts on the blows.
ATTACKS = ("jab", "punch", "hook", "kick", "punch", "hook")
COUNTERS = ("punch", "hook", "uppercut", "kick", "spin_kick", "uppercut", "kick")


def _gesture(name):
    from . import plugins
    return plugins.get("gesture", name)


def standable(scene, p):
    """Whether someone can stand at p: on the ground, not inside a building, a lamp post or a tree."""
    import bpy
    st = scene.set
    ground = st.ground_height(p.x, p.y) if st is not None and hasattr(st, "ground_height") else 0.0
    roots = {c.root for c in scene.actors.values()}
    dg = bpy.context.evaluated_depsgraph_get()
    origin, down = Vector((p.x, p.y, ground + 40.0)), Vector((0, 0, -1))
    for _ in range(8):
        hit, loc, _n, _i, obj, _m = scene.bscene.ray_cast(dg, origin, down, distance=60.0)
        if not hit:
            return True
        top = obj
        while top.parent is not None:
            top = top.parent
        if top in roots or obj.name.startswith("camera"):
            origin = loc + down * 0.01
            continue
        return loc.z < ground + 0.25
    return True


def _ring(centre, n, radius, start, rng, scene=None):
    """n points round a centre, evenly spread from angle `start`, a little uneven; with a scene, each
    one somewhere a person can stand (pulled in, or moved round, out of buildings and the like)."""
    out = []
    for i in range(n):
        a = start + 2 * math.pi * i / n + rng.uniform(-0.25, 0.25) * math.pi / n
        r = radius * rng.uniform(0.92, 1.1)
        p = Vector((centre.x + r * math.sin(a), centre.y - r * math.cos(a)))
        if scene is not None and not standable(scene, p):
            tries = [(a + da, r * k) for k in (1.0, 0.8, 0.6, 0.45) for da in (0.0, 0.35, -0.35, 0.7, -0.7)]
            for aa, rr in tries:
                q = Vector((centre.x + rr * math.sin(aa), centre.y - rr * math.cos(aa)))
                if standable(scene, q):
                    p = q
                    break
        out.append(p)
    return out


def surround(scene, hero, attackers, t=None, radius=1.8, seed=0, enter_from=None):
    """The attackers walk to a ring round the hero and face him; returns when they're all in place.
    With `enter_from` (metres) they start from a wide ring that far out, watching."""
    hero, attackers = scene.character(hero), [scene.character(a) for a in attackers]
    t = scene.clock if t is None else t
    rng = random.Random(seed)
    c = hero.position(t)
    if enter_from:
        for a, p in zip(attackers, _ring(c, len(attackers), float(enter_from), hero.heading(t) + 0.4, rng, scene)):
            if not _compat.fcurves(a.root):              # not placed yet: they've been standing out there
                a.place((p.x, p.y), facing=hero.key, at=0.0)
    spots = _ring(c, len(attackers), radius, hero.heading(t), rng, scene)
    # nearest spot for each, so nobody walks through the middle
    free, done = list(spots), t
    for a in sorted(attackers, key=lambda a: (a.position(t) - c).length):
        p = min(free, key=lambda q: (q - a.position(t)).length)
        free.remove(p)
        a.walk_to((p.x, p.y), at=t + rng.uniform(0, 0.4), wait=False, facing=hero.key)
        done = max(done, a.busy)
    return done


class Brawl:
    """One hero against a crowd, choreographed. Use `run` (or the beats: surround, brawl, burst)."""

    def __init__(self, scene, hero, attackers, seed=0, pressure=0.35, coverage=True):
        self.s = scene
        self.hero = scene.character(hero)
        self.attackers = [scene.character(a) for a in attackers]
        if self.hero is None or None in self.attackers or not self.attackers:
            raise ValueError("a brawl needs a hero and attackers who are in the scene")
        self.rng = random.Random(seed)
        self.pressure = pressure          # how much the next attack overlaps the last exchange
        self.coverage = coverage
        self.free = {a.key: 0.0 for a in self.attackers}
        self.up = {a.key: 0.0 for a in self.attackers}           # when each was last back on their feet
        self.idle = {a.key: None for a in self.attackers}     # since when each has been waiting
        self.shots = 0

    # -- the pieces
    def wait_in_stance(self, a, until):
        """An attacker circling in their stance while they wait their turn."""
        since = self.idle.get(a.key)
        if since is not None and until - since > 0.7:
            a.turn_to(self.hero.key, at=since, wait=False)
            stance(a, since + 0.1, until)
        self.idle[a.key] = None

    def approach(self, a, t, gap=1.05):
        """Come in from the ring to striking distance."""
        c, p = self.hero.position(t), a.position(t)
        d = p - c
        if d.length < 1e-3:
            d = Vector((1, 0))
        q = c + d.normalized() * gap
        if (q - p).length > 0.15:
            a.walk_to((q.x, q.y), at=t, wait=False, speed="fast", facing=self.hero.key)
            return a.busy
        a.turn_to(self.hero.key, at=t, wait=False)
        return a.busy

    def strike(self, who, move, target, at, reaction=None, power=None):
        """`who` throws `move` at `target` from `at`, and `target` meets it with `reaction`."""
        m = _gesture(move)
        who.do(move, target=target.key, at=at, wait=False)
        hit = at + m.impact
        if reaction is not None:
            r = _gesture(reaction)
            if reaction == "knocked_down":
                p = m.power if power is None else power
                end = knock_down(target, hit, who, distance=1.0 + 1.8 * p, height=0.15 + 0.35 * p,
                                 lie=self.rng.uniform(0.3, 0.9))
                target.scene.sound("punch_heavy", at=hit, volume=0.8)
                target.scene._end(target, end, False)
            else:
                target.do(reaction, target=who.key, at=hit - r.impact, wait=False)
        return hit, who.busy

    def cover(self, t, kind, *who, **kw):
        """A shot of the exchange (cut on the action), unless the last cut was a moment ago."""
        if not self.coverage or abs(t - getattr(self, "last_cut", -9.0)) < 0.6:
            return
        self.last_cut = t
        from . import plugins
        subjects = plugins.get("shot", kind).subjects
        kw.setdefault("lens", 20)          # a wide lens close in: inside the ring of fighters, the action big
        try:
            self.s.cut.shot(kind, of=who[0].key if subjects >= 1 else None,
                            other=who[1].key if subjects >= 2 and len(who) > 1 else None, at=max(0.0, t), **kw)
            self.shots += 1
        except ValueError:
            pass

    # -- an exchange
    def exchange(self, t, n):
        rng, hero = self.rng, self.hero
        ready = [a for a in self.attackers if self.free[a.key] <= t + 0.3]
        if not ready:
            t = min(self.free.values())
            ready = [a for a in self.attackers if self.free[a.key] <= t + 0.3]
        a = rng.choice(ready)
        self.wait_in_stance(a, t)
        go = self.approach(a, t)
        hero.turn_to(a.key, at=max(t, go - 0.3), wait=False)
        attack = rng.choice(ATTACKS)
        defence = "dodge" if attack in ("kick", "hook") or rng.random() < 0.35 else "block"
        # fights are covered side-on, both fighters in the frame (never over a shoulder, which hides the blow)
        self.cover(go - 0.2, "full_two_shot", hero, a, handheld=n % 2 == 0)
        hit, a_end = self.strike(a, attack, hero, go, defence)
        hero_end = hero.busy
        counter = rng.choice(COUNTERS)
        c_at = max(hit + 0.25, hero_end - 0.35)
        down = _gesture(counter).power >= 0.65 or rng.random() < 0.3
        big = counter in ("uppercut", "spin_kick", "flying_kick")
        self.cover(c_at + _gesture(counter).impact - 0.35, "full", hero, side="profile",
                   angle="low" if big else None, handheld=not big)
        chit, c_end = self.strike(hero, counter, a, c_at, "knocked_down" if down else "flinch")
        self.back_to_ring(a)
        # the next one is already on his way in as this blow lands: the hero is never left standing about
        return max(chit - 0.7, c_end - 1.2 - self.pressure)

    def back_to_ring(self, a):
        """Back out to the ring (after getting up), to come again later."""
        self.up[a.key] = a.busy
        ring = self.ring_spot(a, a.busy)
        a.walk_to((ring.x, ring.y), at=a.busy + 0.1, wait=False, facing=self.hero.key)
        self.free[a.key] = a.busy + self.rng.uniform(0.2, 0.9)
        self.idle[a.key] = a.busy

    def ring_spot(self, a, t, radius=1.9):
        c, p = self.hero.position(t), a.position(t)
        d = p - c
        d = d.normalized() if d.length > 1e-3 else Vector((1, 0))
        for turn in (0.0, 0.4, -0.4, 0.8, -0.8, 1.3, -1.3):
            q = c + Vector((d.x * math.cos(turn) - d.y * math.sin(turn), d.x * math.sin(turn) + d.y * math.cos(turn))) * radius
            if standable(self.s, q):
                return q
        return c + d * radius

    def double(self, t, n):
        """Two at once: one from the front, one from behind; the hero answers both."""
        rng, hero = self.rng, self.hero
        ready = sorted([a for a in self.attackers if self.free[a.key] <= t + 0.3],
                       key=lambda a: (a.position(t) - hero.position(t)).dot(hero.forward(t)))
        if len(ready) < 2:
            return self.exchange(t, n)
        back, front = ready[0], ready[-1]
        for a in (front, back):
            self.wait_in_stance(a, t)
        g1 = self.approach(front, t)
        self.approach(back, t + 0.2)
        self.cover(t, "group", hero)
        hero.turn_to(front.key, at=max(t, g1 - 0.3), wait=False)
        first, answer = rng.choice((("punch", "dodge"), ("hook", "dodge"), ("jab", "block"), ("kick", "dodge")))
        self.strike(front, first, hero, g1, answer)
        # slip that, and take the one behind on the way round...
        hero_at = hero.busy - 0.25
        hero.turn_to(back.key, at=hero_at, wait=False)
        self.cover(hero_at + 0.2, "full", hero, side="profile", angle="low", handheld=True)
        k_hit, _ = self.strike(hero, rng.choice(("spin_kick", "kick", "hook")), back, hero.busy - 0.05, "knocked_down")
        # ... then the one in front
        hero.turn_to(front.key, at=hero.busy - 0.1, wait=False)
        self.cover(hero.busy - 0.1, "full_two_shot", hero, front)
        p_hit, end = self.strike(hero, rng.choice(("uppercut", "punch", "hook")), front, hero.busy, "knocked_down")
        for a in (front, back):
            self.back_to_ring(a)
        return max(p_hit - 0.7, end - 1.2 - self.pressure)

    def run(self, t, exchanges=8, doubles=0.3):
        """`exchanges` rounds from `t`; returns when the hero is free again."""
        for a in self.attackers:
            self.free[a.key] = max(t, a.busy)
            self.idle[a.key] = max(t, a.busy)
        last_double = -2
        for n in range(exchanges):
            if n > 0 and n - last_double > 1 and self.rng.random() < doubles:      # never two in a row
                t, last_double = self.double(t, n), n
            else:
                t = self.exchange(t, n)
        # over when the hero is done and everyone is nearly back on their feet (no long wait for the last
        # one: they get up while whatever comes next begins)
        end = max(t, self.hero.busy, min(max(self.up.values(), default=0.0), self.hero.busy + WAIT_FOR_UP))
        self.settle(end)
        return end

    def settle(self, end):
        """Whoever is still waiting keeps their stance until the end of the brawl, the hero too."""
        for a in self.attackers:
            if self.idle.get(a.key) is not None and self.idle[a.key] < end:
                self.wait_in_stance(a, end)
        if end - self.hero.busy > 0.7:
            stance(self.hero, self.hero.busy, end)


def brawl(scene, hero, attackers, t=None, exchanges=8, seed=0, pressure=0.35, doubles=0.3, coverage=True):
    """Choreograph a fight of one hero against several attackers (see Brawl). Returns the end time."""
    t = scene.clock if t is None else t
    return Brawl(scene, hero, attackers, seed, pressure, coverage).run(t, exchanges, doubles)


def burst(scene, hero, attackers, t=None, hold_s=0.9, seed=0, coverage=True):
    """The pile-on: they all rush the hero and bury him; he bursts out, throwing them in every direction."""
    hero, attackers = scene.character(hero), [scene.character(a) for a in attackers]
    t = scene.clock if t is None else t
    rng = random.Random(seed)
    c = hero.position(t)
    arrive = t
    for i, a in enumerate(attackers):
        d = a.position(t) - c
        d = d.normalized() if d.length > 1e-3 else Vector((math.cos(i), math.sin(i)))
        q = c + d * rng.uniform(0.42, 0.6)
        a.walk_to((q.x, q.y), at=t + rng.uniform(0, 0.35), wait=False, speed="run", facing=hero.key)
        arrive = max(arrive, a.busy)
    for a in attackers:                       # grabbing hold
        if a.arms:
            for s in (1, -1):
                a.arm_to(s, a.busy, (_deg(-80), _deg(-10 * s), 0), "ease_out", bent=(_aim(s, 0.4, 0.8, 0.0), 0.7))
            a.flash("fierce", a.busy, hold=hold_s + 0.5)
    # the hero goes down under them, gathering...
    hold(hero.hips, "location", t)
    hold(hero.body, "rotation_euler", t)
    key(hero.hips, "location", arrive, (0, 0, hero.hip_z - 0.18 * hero.H), "ease_in")
    key(hero.body, "rotation_euler", arrive, (_deg(30), 0, 0))
    if hero.arms:
        for s in (1, -1):
            hero.arm_to(s, arrive, (_deg(-100), _deg(30 * s), 0), bent=(_aim(s, 0.8, 0.4, 0.4), 0.45))
    hero.flash("fierce", arrive + hold_s - 0.4, hold=0.9, how_much=1.2)
    if coverage:
        try:
            scene.cut.shot("group", at=t, angle="high")
            scene.cut.shot("full", of=hero.key, at=arrive + hold_s - 0.3, angle="low", move="pull_out")
        except ValueError:
            pass
    # ... and bursts out
    go = arrive + hold_s
    key(hero.hips, "location", go + 0.15, (0, 0, hero.hip_z + 0.05 * hero.H), "ease_out")
    key(hero.body, "rotation_euler", go + 0.15, (_deg(-12), 0, 0), "ease_out")
    key(hero.hips, "location", go + 0.6, (0, 0, hero.hip_z))
    key(hero.body, "rotation_euler", go + 0.6, (0, 0, 0))
    if hero.arms:
        for s in (1, -1):
            hero.arm_to(s, go + 0.15, (0, _deg(-110 * s), 0), "ease_out")     # arms flung wide
        guard(hero, go + 0.9)
    scene.sound("boom", at=go, volume=0.7)
    scene.sound("whoosh", at=go - 0.05, volume=0.8)
    shake(hero, go, 1.2)
    end = go
    from . import ragdoll
    flying = [(a, hero, rng.uniform(2.4, 3.6), rng.uniform(0.4, 0.8)) for a in attackers]
    bodies = [f for f in flying if ragdoll.can_fall(f[0])]
    if bodies:                    # thrown together, they hit each other on the way
        for a, t_up in fall_together(bodies, go, lie=rng.uniform(1.0, 2.0)).items():
            end = max(end, t_up)
    for a, h, dist, height in flying:
        if not ragdoll.can_fall(a):
            end = max(end, knock_down(a, go + rng.uniform(0, 0.08), h, distance=dist, height=height,
                                      lie=rng.uniform(1.0, 2.2)))
            scene._end(a, end, False)
    scene._end(hero, go + 0.9, False)
    return go + 0.9
